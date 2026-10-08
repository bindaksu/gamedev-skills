# Purchases, Notifications, Refunds, Reconciliation

Read when implementing `/purchase/verify`, store webhooks, refund clawback, or the daily reconciler. API names below are stable public APIs; field-level details change — verify against the current Apple and Google reference before shipping (as of 2026-10; verify).

## Apple (StoreKit 2 + App Store Server API)

Facts from research:
- The original StoreKit API was deprecated at WWDC24; new features ship only in StoreKit 2 (iOS 15+). Server-side, use the **App Store Server API** with the **App Store Server Library** to verify JWS; receipt validation (`verifyReceipt`) is legacy. https://developer.apple.com/documentation/appstoreserverapi/app-store-server-api-changelog
- `AppTransaction.appTransactionId` is per Apple Account per app (WWDC25). https://developer.apple.com/videos/play/wwdc2025/249

Flow:
1. Client purchases with `appAccountToken` = a UUID the server issued and mapped to `player_id`.
2. On `.verified` result, client sends `transaction.jwsRepresentation` to the server. Client calls `finish()` only after the server returns 200.
3. Server verifies the JWS chain and claims, then grants with idempotency key `apple:<transactionId>`.
4. On launch, the client iterates `Transaction.unfinished` and re-sends each one — this is the recovery path for crashes and lost responses.

```kotlin
// JVM: App Store Server Library (com.apple.itunes.storekit). Verify constructor args against current release.
val verifier = SignedDataVerifier(
    appleRootCAs,            // Set<InputStream>: Apple Root CA - G3 etc.
    bundleId, appAppleId,    // appAppleId required for Production
    Environment.PRODUCTION,
    /* enableOnlineChecks = */ true,
)

fun verifyApple(playerId: UUID, jws: String): Grant {
    val tx = verifier.verifyAndDecodeTransaction(jws)        // throws VerificationException
    require(tx.bundleId == bundleId)
    require(tx.revocationDate == null) { "revoked" }
    require(tx.appAccountToken == tokenFor(playerId)) { "account binding mismatch" }
    val sku = catalog.byAppleProductId(tx.productId) ?: error("unknown product")
    return Grant(idemKey = "apple:${tx.transactionId}", sku = sku, storeTxnId = tx.transactionId,
                 sandbox = tx.environment != Environment.PRODUCTION)
}
```

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
3. Server calls the Play Developer API (`purchases.products.get`; check whether one-time products with purchase options require the newer product purchase resource — verify), checks `purchaseState == 0` (purchased; 2 = pending — do not grant), `obfuscatedExternalAccountId`, `orderId`.
4. Grant with idempotency key `google:<purchaseToken>` (the token, not orderId, is the unique handle).
5. Server consumes (consumables) or acknowledges (non-consumables) **after** the grant commits. Unacknowledged purchases are refunded automatically after 3 days.

```kotlin
// google-api-services-androidpublisher
fun verifyGoogle(playerId: UUID, productId: String, token: String): Grant {
    val p = publisher.purchases().products().get(packageName, productId, token).execute()
    require(p.purchaseState == 0) { "not purchased (pending or cancelled)" }
    require(p.obfuscatedExternalAccountId == obfuscate(playerId)) { "account binding mismatch" }
    val isTest = p.purchaseType == 0   // license tester
    val sku = catalog.byGoogleProductId(productId) ?: error("unknown product")
    return Grant(idemKey = "google:$token", sku = sku, storeTxnId = p.orderId, sandbox = isTest)
}

fun finalizeGoogle(productId: String, token: String, consumable: Boolean) {
    val req = publisher.purchases().products()
    if (consumable) req.consume(packageName, productId, token).execute()
    else req.acknowledge(packageName, productId, token, ProductPurchasesAcknowledgeRequest()).execute()
}
```

Notifications: Real-time developer notifications arrive on Cloud Pub/Sub; they carry identifiers only — always re-fetch state from the API. Voided purchases (refunds, chargebacks, revocations) are available from the **Voided Purchases API** (`purchases.voidedpurchases.list`, with `voidedReason` and `voidedSource`) and as RTDN voided-purchase notifications (verify current payload). Poll the Voided Purchases API daily regardless — it is the reconciliation source.

## Refund and voided-purchase policy

```
ON REFUND(store_txn_id):
  txn = ledger.find(idem_key = "<store>:<store_txn_id>")
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
