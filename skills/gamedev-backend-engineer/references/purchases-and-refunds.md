# Purchases, Notifications, Refunds, Reconciliation

Read when implementing `/purchase/verify`, store webhooks, refund clawback, or the daily reconciler. API names below are stable public APIs; field-level details change — verify against the current Apple and Google reference before shipping (as of 2026-10; verify).

## Apple (StoreKit 2 + App Store Server API)

Facts from research:
- The original StoreKit API was deprecated at WWDC24; new features ship only in StoreKit 2 (iOS 15+). Server-side, use the **App Store Server API** with the **App Store Server Library** to verify JWS; receipt validation (`verifyReceipt`) is legacy. https://developer.apple.com/documentation/appstoreserverapi/app-store-server-api-changelog
- `AppTransaction.appTransactionId` is per Apple Account per app (WWDC25). https://developer.apple.com/videos/play/wwdc2025/249

Flow:
1. Client purchases with `appAccountToken` = a UUID the server issued and mapped to `player_id`.
2. On `.verified` result, client sends `transaction.jwsRepresentation` to the server. Client calls `finish()` only after the server returns 200.
3. Server verifies the JWS chain and claims, resolves the owning account from `appAccountToken` (next section), then grants with idempotency key `apple:<transactionId>`.
4. On launch, the client iterates `Transaction.unfinished` and re-sends each one — this is the recovery path for crashes and lost responses. StoreKit also hands an unfinished consumable back on every later purchase of the same product, so the server must answer every verified transaction with a response the client can `finish()` on.

Account binding rules (a mismatch is normal: shared devices, account switches, reinstalls):

| Case | Server action | Response |
| --- | --- | --- |
| Token names the caller | Grant to caller | 200 with balances |
| Token names another live account | Grant to that account | Neutral 200, no balances of that account |
| Token names a deleted account, non-consumable | Rebind to the caller (move its `purchase_order` row in the grant transaction) so Restore works | 200 with entitlement |
| Token names a deleted account, consumable | Void: record, grant nothing | Neutral 200 |
| `transactionId` already held by a live account other than the resolved owner | Refuse; flag for review | 409 (the only refusal) |
| No token (offer code, promoted purchase, old client) | Grant to caller | 200 with balances |

```kotlin
// JVM: App Store Server Library (com.apple.itunes.storekit). Verify constructor args against current release.
val verifier = SignedDataVerifier(
    appleRootCAs,            // Set<InputStream>: Apple Root CA - G3 etc.
    bundleId, appAppleId,    // appAppleId required for Production
    Environment.PRODUCTION,
    /* enableOnlineChecks = */ true,
)

fun verifyApple(callerId: UUID, jws: String): Outcome {
    val tx = verifier.verifyAndDecodeTransaction(jws)        // throws VerificationException
    require(tx.bundleId == bundleId)
    require(tx.revocationDate == null) { "revoked" }
    val sku = catalog.byAppleProductId(tx.productId) ?: error("unknown product")
    val named = tx.appAccountToken?.let { accounts.byToken(it) }      // never assert it equals the caller
    val owner = when {
        named == null -> callerId                                     // no token: credit the caller
        named.deleted && sku.consumable -> return Outcome.Void(tx.transactionId)
        named.deleted -> callerId                                     // rebind non-consumable for Restore
        else -> named.id                                              // may differ from the caller
    }
    val holder = orders.holder("apple", tx.transactionId)            // purchase_order UNIQUE (store, store_txn_id)
    if (holder != null && holder != owner && !accounts.isDeleted(holder)) return Outcome.Refuse(tx.transactionId)
    val grant = Grant(playerId = owner, idemKey = "apple:${tx.transactionId}", sku = sku,
                      storeTxnId = tx.transactionId, sandbox = tx.environment != Environment.PRODUCTION)
    return Outcome.Credit(grant, neutral = owner != callerId)        // neutral: no owner balances in the reply
}
```

Set the production and sandbox Server Notifications V2 URLs in App Store Connect before the first sale: Apple sends nothing for events that happened before a URL existed, and each environment takes one URL per app, so fan out internally. TestFlight and App Review purchases arrive as SANDBOX, and sandbox refunds often never arrive; a missing sandbox refund is not a bug (as of 2026-11; verify).

Notifications (App Store Server Notifications V2): the POST body is `{ "signedPayload": "..." }`. Verify with `verifier.verifyAndDecodeNotification(signedPayload)`, then decode `data.signedTransactionInfo`. Handle at minimum:

| notificationType | Action |
| --- | --- |
| `REFUND` | Clawback txn for `transactionId` (see policy below); flag account |
| `REFUND_REVERSED` | Re-grant (idempotency key `apple:refund_reversed:<transactionId>`) |
| `REFUND_DECLINED` | Log only |
| `CONSUMPTION_REQUEST` | Customer requested a refund on a consumable; respond via the Send Consumption Information endpoint with delivery and usage facts (deadline is short, about 12 h — verify) |
| `REVOKE` | Family Sharing entitlement removed; revoke non-consumable/subscription access |
| `DID_RENEW`, `EXPIRED`, `DID_FAIL_TO_RENEW`, `GRACE_PERIOD_EXPIRED` | Subscription state (battle pass subs, VIP) |

Use `notificationUUID` as the dedup key. Return 200 only after the effect committed; Apple retries otherwise. Backstop with the Get Transaction History endpoint per player when support investigates.

## Google Play (Play Billing Library + Play Developer API)

Facts from research:
- **PBL 8+ required for new apps and updates since 2026-08-31** (extension to 2026-11-01). PBL 8 renames in-app items to **one-time products** with multiple purchase options and offers; removed `querySkuDetailsAsync` and querying consumed purchases. https://developer.android.com/google/play/billing/deprecation-faq, https://developer.android.com/google/play/billing/migrate-gpblv8
- PBL 9.1.0 adds Billing Choice APIs. https://developer.android.com/google/play/billing/release-notes

Flow:
1. Client sets `setObfuscatedAccountId(hash(player_id))` in `BillingFlowParams`.
2. Client sends `purchaseToken` + `productId` to the server.
3. Server calls the Play Developer API (`purchases.products.get`; check whether one-time products with purchase options require the newer product purchase resource — verify), checks `purchaseState == 0` (purchased; 2 = pending — do not grant), and resolves the owning account from `obfuscatedExternalAccountId` with the Apple binding table above [inference]; `orderId` is the stored `store_txn_id` that the cross-account guard checks.
4. Grant with idempotency key `google:<purchaseToken>` (the token, not orderId, is the unique handle).
5. Server consumes (consumables) or acknowledges (non-consumables) **after** the grant commits. Unacknowledged purchases are refunded automatically after 3 days.

```kotlin
// google-api-services-androidpublisher
fun verifyGoogle(callerId: UUID, productId: String, token: String): Outcome {
    val p = publisher.purchases().products().get(packageName, productId, token).execute()
    require(p.purchaseState == 0) { "not purchased (pending or cancelled)" }
    val sku = catalog.byGoogleProductId(productId) ?: error("unknown product")
    // Apple binding table applied to Google [inference]: never assert the id equals the caller.
    // The obfuscated-id map keeps deleted accounts (flagged), so a deleted owner is found, not lost.
    val named = p.obfuscatedExternalAccountId?.let { accounts.byObfuscatedId(it) }
    val owner = when {
        named == null -> callerId                                     // no id or unknown id: credit the caller
        named.deleted && sku.consumable -> return Outcome.Void(p.orderId)
        named.deleted -> callerId                                     // rebind non-consumable for Restore
        else -> named.id                                              // may differ from the caller
    }
    val holder = orders.holder("google", p.orderId)                  // same key the grant stores as storeTxnId
    if (holder != null && holder != owner && !accounts.isDeleted(holder)) return Outcome.Refuse(p.orderId)
    val isTest = p.purchaseType == 0   // license tester
    val grant = Grant(playerId = owner, idemKey = "google:$token", sku = sku, storeTxnId = p.orderId, sandbox = isTest)
    return Outcome.Credit(grant, neutral = owner != callerId)        // neutral: no owner balances in the reply
}

// Credit: finalize after the grant commits. Void: finalize after the void is recorded, as Apple's client
// finishes on the neutral 200, so the product is not blocked. Refuse: do not finalize; the holder's grant stands.
fun finalizeGoogle(productId: String, token: String, consumable: Boolean) {
    val req = publisher.purchases().products()
    if (consumable) req.consume(packageName, productId, token).execute()
    else req.acknowledge(packageName, productId, token, ProductPurchasesAcknowledgeRequest()).execute()
}
```

Why the owner lookup on Google too [inference; the evidence is StoreKit-only]: refusing a verified purchase leaves it unconsumed, which blocks re-purchase of that product, and unacknowledged, which auto-refunds it after 3 days. Keep a stored obfuscated-id-to-player map that keeps deleted accounts (flagged), and apply every row of the Apple table: credit the live account the id names, rebind a deleted account's non-consumable to the caller and void its consumable, and refuse only when a third live account already holds the `orderId`.

Notifications: Real-time developer notifications arrive on Cloud Pub/Sub; they carry identifiers only — always re-fetch state from the API. Voided purchases (refunds, chargebacks, revocations) are available from the **Voided Purchases API** (`purchases.voidedpurchases.list`, with `voidedReason` and `voidedSource`) and as RTDN voided-purchase notifications (verify current payload). Poll the Voided Purchases API daily regardless — it is the reconciliation source.

## Refund and voided-purchase policy

```
ON REFUND(store_txn_id):
  txn = purchase_order(store, store_txn_id).txn_id     # current holder; after a rebind, not the first grantee
  if none: record orphan refund; alert (may be a grant we never made)
  granted = legs of txn for player
  for each granted asset:
     unspent = min(granted.amount, wallet.balance)
     legs += player:-unspent, system:refunds:+unspent
     if policy == DEBT and granted.amount > unspent:
        legs += player:-(granted.amount - unspent) on a debt-enabled wallet
  instanced items: revoke if still owned and created_by_txn == txn
  ledger.Apply(idem_key = "refund:<store>:<store_txn_id>", legs)
  risk.flag(player, "refund", amount_usd)     # anti-cheat thresholds decide enforcement
```

Debt policy: a debt-enabled wallet blocks spending of that currency until repaid by future earnings; show it honestly in UI. Coordinate wording with support and monetization; some regions restrict how refunded players may be treated — keep enforcement proportional (verify locally).

## Reconciler (daily, per store)

```sql
-- Purchases granted but never finalized (Google) — alert if > 1 hour old
SELECT o.order_id, o.player_id, o.created_at FROM purchase_order o
WHERE o.store = 'google' AND o.status = 'granted' AND o.finalized_at IS NULL
  AND o.created_at < now() - interval '1 hour';

-- Store transactions without a ledger grant (from store API export joined to orders)
SELECT s.store_txn_id FROM store_export s
LEFT JOIN purchase_order o ON o.store_txn_id = s.store_txn_id
WHERE o.order_id IS NULL;

-- System account sanity: IAP-granted gems should equal sum of catalog grants for verified orders
SELECT asset, -sum(amount) AS issued FROM ledger_entry WHERE account = 'system:iap' GROUP BY asset;
```

Purchase order table:

```sql
CREATE TABLE purchase_order (
  order_id      uuid PRIMARY KEY,
  player_id     uuid NOT NULL,
  store         text NOT NULL,                     -- 'apple','google','web','steam'
  store_txn_id  text NOT NULL,
  product_id    text NOT NULL,
  sandbox       boolean NOT NULL,
  status        text NOT NULL,                     -- 'verified','granted','finalized','refunded'
  txn_id        uuid REFERENCES ledger_txn(txn_id),
  created_at    timestamptz NOT NULL DEFAULT now(),
  finalized_at  timestamptz,
  UNIQUE (store, store_txn_id)
);
```

Sandbox purchases grant only on non-production environments or to allowlisted QA accounts; a sandbox JWS on production is a fraud signal.
