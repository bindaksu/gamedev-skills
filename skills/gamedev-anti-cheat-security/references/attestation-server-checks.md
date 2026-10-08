# Attestation — Server-Side Verification

Read when integrating Play Integrity or App Attest/DeviceCheck verification into the backend. Field names and endpoints are from public documentation; confirm against current docs before shipping (as of 2026-10; verify). Sources: https://developer.android.com/google/play/integrity/improvements, https://developer.apple.com/documentation/devicecheck/assessing-fraud-risk

## Request binding (both platforms)

Bind each attestation to the specific action so a token cannot be replayed for a different request:

```
request_hash = SHA-256( player_id | action | canonical(request_body) | server_nonce )
```

- `server_nonce` is issued by the server, single-use, short TTL (e.g., 5 min), stored until consumed.
- The client passes `request_hash` into Play Integrity standard requests (`requestHash`) or into App Attest assertions (as the client data).
- The server recomputes the hash from the received request and compares.

## Google Play Integrity (standard requests)

Flow: client prepares an integrity token provider once (warm-up), then requests a token per sensitive action with `requestHash`; server decodes via Google.

```
POST https://playintegrity.googleapis.com/v1/{packageName}:decodeIntegrityToken
{ "integrity_token": "<token>" }
-> tokenPayloadExternal
```

```kotlin
data class IntegrityDecision(val allowEconomy: Boolean, val allowRanked: Boolean, val riskDelta: Int, val reasons: List<String>)

fun evaluate(p: TokenPayloadExternal, expectedHash: String, now: Instant): IntegrityDecision {
    val reasons = mutableListOf<String>()
    val rd = p.requestDetails
    if (rd.requestPackageName != PACKAGE) reasons += "package_mismatch"
    if (rd.requestHash != expectedHash) reasons += "hash_mismatch"
    if (Duration.between(Instant.ofEpochMilli(rd.timestampMillis), now) > Duration.ofMinutes(5)) reasons += "stale"

    val app = p.appIntegrity.appRecognitionVerdict             // PLAY_RECOGNIZED | UNRECOGNIZED_VERSION | UNEVALUATED
    val device = p.deviceIntegrity.deviceRecognitionVerdict.orEmpty()  // MEETS_DEVICE_INTEGRITY, MEETS_BASIC_INTEGRITY, MEETS_STRONG_INTEGRITY, ...
    val licensed = p.accountDetails?.appLicensingVerdict        // LICENSED | UNLICENSED | UNEVALUATED

    if (app != "PLAY_RECOGNIZED") reasons += "app_$app"
    if ("MEETS_DEVICE_INTEGRITY" !in device) reasons += "device_weak"
    if ("MEETS_BASIC_INTEGRITY" !in device) reasons += "device_none"

    val hardFail = reasons.any { it in setOf("package_mismatch", "hash_mismatch", "stale") } || app == "UNRECOGNIZED_VERSION"
    return IntegrityDecision(
        allowEconomy = !hardFail && "device_none" !in reasons,
        allowRanked  = !hardFail && "device_weak" !in reasons,
        riskDelta    = reasons.size * 10 + if (licensed == "UNLICENSED") 10 else 0,
        reasons      = reasons,
    )
}
```

Notes:
- Since May 2025, on Android 13+ `MEETS_DEVICE_INTEGRITY` requires hardware-backed signals; expect the share of devices without it to change by OS version — chart verdict distribution by device model and OS before setting policy.
- `MEETS_STRONG_INTEGRITY` adds a patch-recency requirement; do not require it for ordinary play.
- Optional environment signals (app access risk, Play Protect) exist; treat them as additional risk weights.
- Respect API quotas: request tokens for sensitive actions only (purchase verify, ranked queue, reward claim, account link), not every call.
- Legitimate PC/emulator environments (e.g., Google Play Games on PC) may produce different verdicts — test them and decide policy explicitly.

## Apple App Attest

Client: `DCAppAttestService.shared.isSupported` → `generateKey()` → server issues challenge → `attestKey(keyId, clientDataHash: SHA256(challenge))` → send attestation + keyId. Afterwards, per request: `generateAssertion(keyId, clientDataHash: SHA256(request_hash))`.

### Attestation validation (once per key)

1. Decode the CBOR attestation object (`fmt` = `apple-appattest`, `attStmt.x5c`, `attStmt.receipt`, `authData`).
2. Verify the `x5c` certificate chain to Apple's App Attestation Root CA.
3. Compute `clientDataHash = SHA256(challenge)`; `nonce = SHA256(authData || clientDataHash)`; it must equal the value in the credential certificate's extension (OID 1.2.840.113635.100.8.2).
4. `SHA256(credential public key)` must equal `keyId`.
5. `authData.rpIdHash` must equal `SHA256("<TeamID>.<BundleID>")`.
6. `authData.signCount` must be 0.
7. `aaguid` must be the production App Attest value (`appattest` padded) in production, `appattestdevelop` only in development builds.
8. `credentialId` in `authData` must equal `keyId`.
9. Store `(keyId, publicKey, receipt, counter=0, player_id, created_at)`.

### Assertion validation (per sensitive request)

1. `clientDataHash = SHA256(request_hash)`; `nonce = SHA256(authenticatorData || clientDataHash)`.
2. Verify the assertion signature over `nonce` with the stored public key.
3. `rpIdHash` matches the app ID hash.
4. `counter` > stored counter; then store the new counter (reject equal or lower — replay or cloned key).

### Fraud risk metric

Periodically send the stored attestation receipt to Apple's endpoint to refresh it and obtain the approximate count of attested keys on the device over 30 days. Many keys on one device suggests reinstall farming or account multiplication. Add to the risk score; never ban on it alone. (WWDC26 session 201: https://developer.apple.com/videos/play/wwdc2026/201)

### Unsupported cases

Not all devices/environments support App Attest (`isSupported == false`, simulators, some app extensions). Do not penalize; fall back to server-side validation and behavior signals. Roll out with a percentage gate — Apple recommends gradual adoption because attestation calls hit Apple's service.

## DeviceCheck (two bits)

- Two per-device bits plus a last-updated month, persisted by Apple across reinstalls, queried/updated from your server with a device token.
- Typical uses: bit 0 = "new-player promo already claimed on this device", bit 1 = "device associated with a confirmed fraud ban".
- Do not encode more meaning than two bits can carry; document the meaning and the reset policy (bits persist; set a review process before setting the fraud bit).

## Risk score aggregation

```
risk = w1*integrity_reasons + w2*app_attest_failures + w3*fraud_metric_bucket
     + w4*telemetry_anomalies + w5*graph_cluster_size + w6*refund_count_90d
thresholds: risk >= T1 -> flag; >= T2 -> shadow restriction; enforcement above that needs a confirmed detection + evidence
```

Calibrate weights on labeled cases (confirmed cheaters vs appealed-and-overturned), and re-check precision after each OS release, because verdict distributions shift.
