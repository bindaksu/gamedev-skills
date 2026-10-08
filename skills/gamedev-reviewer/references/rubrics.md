# Full Review Rubrics

Read when reviewing an artifact type in depth. Each item is phrased as a check; a failed check becomes one finding. Suggested default severity is in brackets; adjust with the escalation rules in SKILL.md.

## 1. Design document / feature spec

- [ ] Outcome metric, baseline, target and guardrail stated [major if missing]
- [ ] Ties to core loop or meta; states which loop phase it feeds [minor]
- [ ] Player journey complete: discover, enter, play, resolve, reward, return [major per missing step on main path]
- [ ] States: first-time, empty, loading, error, offline, expired/ended, ineligible, old client [major per missing main-path state]
- [ ] Rules expressed as tables or pseudo-code with all numbers [minor]
- [ ] Edge cases: ties, disconnects, leaving mid-activity, time zones, daylight saving, server maintenance overlap [major for ties/disconnects in competitive modes]
- [ ] Economy: every new faucet has a matched sink or a stated reason [major]
- [ ] Monetization touchpoints listed with ethics check [major if paid randomness without disclosure]
- [ ] Live-ops: config-driven parameters, schedulable, kill switch, reusable template [major if not kill-switchable and touches currency]
- [ ] Telemetry events listed with parameters [minor; major if outcome metric not measurable]
- [ ] Localization (string count, text expansion) and accessibility notes [minor]
- [ ] Dependencies and owners listed [minor]
- [ ] Cut line: what is out of scope [nit to minor]

## 2. Economy / monetization change

- [ ] Net flow delta per currency at p10, p50, p90, p99 [major if only mean]
- [ ] Conversion graph rechecked: no new cycle with product at least 1 [blocker]
- [ ] Two-way converters keep a spread (round-trip under 0.90) [major]
- [ ] Price ladder per-unit value monotonic across rungs [major]
- [ ] Bundle value claims ("300% value") computed from a stated base [major; consumer-protection risk]
- [ ] Randomized paid items: odds per item type shown before purchase (App Store 3.1.1); disclose for earned-currency boxes too [blocker if missing]
- [ ] Pity / bad-luck protection defined and displayed [major]
- [ ] Regional rules checked for loot boxes and minors (route to gamedev-monetization-designer) [blocker if a target market bans the mechanic]
- [ ] Refund/chargeback path revokes or flags granted items per policy [major]
- [ ] Grant is server-side and idempotent [blocker]
- [ ] Offer targeting excludes vulnerable segments where policy requires (minors, spend limits) [major]
- [ ] A/B test: hypothesis, primary metric, guardrails, sample size, duration to D30 when retention is a guardrail [major if no guardrail]

## 3. UX flow

- [ ] Main-path taps-to-goal counted; no step without purpose [minor]
- [ ] Touch targets and thumb reach; safe areas and notches [major for primary actions out of reach]
- [ ] Interruption: incoming call, app background, network loss, low battery; resume restores state [major]
- [ ] Paid action has explicit price, confirmation and no pre-checked upsell [blocker if price unclear]
- [ ] No fake timers or fake scarcity; countdowns are real [major]
- [ ] Error messages say what to do next [minor]
- [ ] Colorblind-safe state encoding; contrast; minimum font size [major on gameplay-critical info]
- [ ] Text expansion and RTL layout tolerance [minor]
- [ ] Back navigation and exit from every screen [major if trapped]

## 4. Client code

### Unity C#
- [ ] No allocations in `Update`/`LateUpdate`/`FixedUpdate` (string concat, LINQ, boxing, closures, `new` arrays) [major on per-frame paths]
- [ ] No `GameObject.Find*`, `FindObjectOfType`, `GetComponent` per frame; cache references [major]
- [ ] Object pooling for spawned entities, projectiles, damage numbers [minor to major]
- [ ] Addressables: every `LoadAssetAsync` handle released; catalog update not blocking boot [major]
- [ ] Async: no `async void` except event handlers; cancellation on scene unload [major]
- [ ] Coroutines stopped on disable/destroy [minor]
- [ ] IL2CPP stripping: reflection targets preserved (link.xml) [major if crash on device only]
- [ ] Remote config read with default fallback; never block boot on fetch [major]

Bad vs fixed:

```csharp
// Bad: allocates every frame, searches the scene every frame
void Update() {
    var hud = GameObject.Find("Score").GetComponent<TMP_Text>();
    hud.text = "Score: " + score;
}

// Fixed: cached reference, update on change only
[SerializeField] TMP_Text scoreText;
int shownScore = -1;
void Update() {
    if (score == shownScore) return;
    shownScore = score;
    scoreText.SetText("Score: {0}", score);
}
```

### Swift (StoreKit 2, lifecycle)
- [ ] Transaction listener started at launch (`Transaction.updates`) [blocker if missing: interrupted purchases lost]
- [ ] Verify `VerificationResult`; grant via server; `finish()` only after the grant is durable [blocker]
- [ ] Thermal state observed (`ProcessInfo.thermalState`) and quality scaled [minor]
- [ ] Main actor not blocked by I/O [major]

```swift
// Listen for transactions that complete outside the purchase flow (Ask to Buy, interrupted, renewals)
func listenForTransactions() -> Task<Void, Never> {
    Task.detached {
        for await result in Transaction.updates {
            guard case .verified(let transaction) = result else { continue }
            if await Server.grant(transactionID: transaction.id) {   // idempotent on the server
                await transaction.finish()
            }
        }
    }
}
```

### Kotlin (Play Billing)
- [ ] Billing library at a currently accepted major version (PBL 8+ required for new apps and updates since Aug 31, 2026; as of 2026-10; verify) [blocker at submission]
- [ ] Purchases verified server-side, then acknowledged (non-consumables) or consumed (consumables); unacknowledged purchases are refunded after 3 days [blocker]
- [ ] Pending purchases handled; grant only on `PURCHASED` state [major]
- [ ] `queryPurchasesAsync` on resume to recover missed purchases [major]

```kotlin
private suspend fun handle(purchase: Purchase) {
    if (purchase.purchaseState != Purchase.PurchaseState.PURCHASED) return
    if (!backend.verifyAndGrant(purchase.purchaseToken)) return   // idempotent on token
    if (!purchase.isAcknowledged) {
        val params = AcknowledgePurchaseParams.newBuilder()
            .setPurchaseToken(purchase.purchaseToken).build()
        billingClient.acknowledgePurchase(params)
    }
}
```

## 5. Server code

- [ ] Server authority for currency, inventory, rank, rewards, timers [blocker if client-authoritative]
- [ ] Idempotency key on every grant, purchase, reward claim [blocker]
- [ ] Atomic transactions across balance and ledger writes [blocker]
- [ ] Receipt/JWS validation via App Store Server API and Google Play Developer API; replay protection [blocker]
- [ ] Input validation and rate limiting on all player endpoints [major]
- [ ] API versioning: clients N-2 get defined responses; additive schema changes only [major]
- [ ] Config schema validation before publish; staged config rollout [major]
- [ ] Leaderboards: bounded sorted-set sizes, sharded by season/bracket [minor to major]
- [ ] No N+1 queries on guild/friend lists; pagination [major]
- [ ] Metrics, structured logs, trace IDs; alert on error rate and latency [major]
- [ ] Time handled in UTC on the server; event windows in server time [major]

```java
// Idempotent reward grant: same (warId, playerId, tier) always yields one grant
@Transactional
public GrantResult grant(String warId, String playerId, int tier) {
    String key = warId + ":" + playerId + ":" + tier;
    if (grants.existsByIdempotencyKey(key)) return GrantResult.alreadyGranted();
    grants.insert(new Grant(key, playerId, rewardsFor(tier)));   // unique index on key
    wallet.credit(playerId, rewardsFor(tier));
    return GrantResult.granted();
}
```

## 6. Netcode

- [ ] Authority model documented (server-authoritative, host, lockstep, rollback) [major]
- [ ] Client never decides hits, damage, score, cooldowns [blocker in competitive modes]
- [ ] Tick rate, snapshot rate, bandwidth per player budgeted [major]
- [ ] Tested at 150–300 ms RTT, jitter, 1–5% loss, Wi-Fi to cellular handover [major]
- [ ] Reconnect and resume mid-match; AFK and disconnect rules [major]
- [ ] Lockstep/rollback: determinism (fixed-point or strict float), desync detection by state hash [blocker if missing]
- [ ] Lag compensation window bounded [minor]

## 7. Shaders and performance

- [ ] `half` precision for colors/UVs on mobile; `float` for positions and depth [minor]
- [ ] No dynamic loops or heavy branching per pixel; texture samples counted [major on full-screen passes]
- [ ] Keyword/variant count bounded; unused variants stripped [major on build size/load time]
- [ ] Overdraw of transparent UI and particles measured [major on min tier]
- [ ] Texture compression ASTC (and ETC2 fallback where needed) [major]
- [ ] Measured on min-tier device: frame time p50/p90, memory, thermal after 20+ minutes [major if editor-only]
- [ ] Draw calls/batches within budget [minor to major]
