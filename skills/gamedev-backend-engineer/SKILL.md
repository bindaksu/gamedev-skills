---
name: gamedev-backend-engineer
description: >-
  Implement game backend services that hold real value: a double-entry economy ledger
  with idempotency keys and optimistic concurrency, App Store and Google Play purchase
  validation with refund and voided-purchase clawback, inventory, Redis leaderboards
  with ties and seasons, guilds, mailbox, remote config and segments, API versioning
  with forced update, rate limits and save conflicts. Use when writing purchase or
  grant endpoints, chasing duplicated currency or lost purchases, building a
  leaderboard or inbox, or supporting old clients after a protocol change.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: backend
---

# Game Backend Engineer

Every bug that costs a live game real money is one of four: a grant that happened twice, a purchase that was paid for and never granted, a refund that never came back out, or a value the client was allowed to decide. All four are solved by the same discipline: **every mutation is a server-built, idempotent, journaled transaction keyed to a client intent**, and the store is a notifier you reconcile against, not a source you trust once. Write the ledger first and route everything — level rewards, IAP, mail attachments, guild payouts, compensation — through it. A backend that has a separate "just add gems" path for support tooling has two economies, and the second one is where the duplication lives.

## Role Profile

The server engineer embedded in a game team or a central platform team: Supercell asks for "server-side Java, concurrency and distributed systems" and "troubleshooting high-volume sharded databases"; King's principal Java role ships and supports its own code in production; Supercell's Brawl Stars server engineers also "contribute to game design".

- **Responsibilities:** economy, store, inventory, social and LiveOps services; on-call rotation as first-line production support; schema migrations on sharded databases; integrating store APIs.
- **Hard skills:** Java/JVM concurrency (dominant), Go/Node (accepted at Supercell ID), Erlang/Scala (Wargaming); sharded MySQL/Postgres; Redis; Kafka; Kubernetes; Prometheus/Grafana.
- **KPIs (inferred):** availability and incident count, p99 latency, cost per DAU; for economy services, zero unreconciled purchases.
- **Collaborators:** designers (economy, LiveOps), client engineers, SRE, data, security.
- Sources: https://hitmarker.net/jobs/king-principal-java-backend-engineer-new-midcore-project-881778, https://jobs.accel.com/companies/space-ape-games-2/jobs/66661349-senior-server-engineer-central-tech

Snippets below use Go and SQL (Postgres syntax; MySQL notes inline); Kotlin is used where the official store library is JVM. JVM shops port the Go structure directly.

## When to Use / Not

Use for: implementing any write path that touches currency, items, purchases, rankings, guild state, mail, config delivery, or client versioning.

Not for:
- Choosing services, vendors, shard keys and scale targets → `gamedev-platform-server-architect`.
- Databases, clusters, regions, backups → `gamedev-infrastructure-engineer`.
- Attestation, bot detection, ban pipeline → `gamedev-anti-cheat-security` (this skill exposes the hooks).
- Prices, pack contents, offer rules → `gamedev-monetization-designer`; faucet/sink math → if installed, `game-economy-balancer`.
- Client-side StoreKit / Play Billing integration → `gamedev-ios-engineer`, `gamedev-android-engineer`.

## Inputs to Gather

- Currencies and item types (stackable vs instanced), which are sold for cash, which may go negative. Default: none may go negative except via refund debt.
- Stores in scope: App Store, Google Play, webshop, Steam. Default: App Store + Play.
- Database and shard layout (from the architect). Default: Postgres, sharded by `player_id`.
- Client protocol version scheme and current minimum supported version.
- Refund policy decided with monetization and support: claw back, debt, or flag only. Default: claw back unspent, debt for spent, flag repeat refunders.
- Leaderboard specs: scope (global, regional, bracketed), season length, tie rule, reward tiers.
- Expected peak write RPS per endpoint (from architect capacity model).

## Method

1. **Build the ledger** (Deliverable 1). Double-entry: every transaction's legs sum to zero per currency against system accounts (`system:iap`, `system:rewards`, `system:sink`). This makes "where did 4M gems come from" a query, not an investigation.
2. **Make every write idempotent.** The client generates an idempotency key per *intent* (UUIDv7 when the player taps Buy, persisted until acknowledged). Store the key with the transaction in the same DB transaction, plus a hash of the request. Replay with same hash returns the stored response; replay with a different hash is a 422.
3. **Use conditional updates for balances, versions for documents.** Wallet updates use `balance = balance + delta WHERE balance + delta >= 0` (row lock, no lost update). Mutable documents (save blobs, guild settings) use `version` compare-and-set and return 409 on mismatch.
4. **Build purchase verification** (Deliverable 2, `references/purchases-and-refunds.md`). Verify the store's signed data server-side, bind to `player_id`, grant through the ledger with `store_txn_id` as the idempotency key, then acknowledge/consume. Grant before acknowledging, never after a crash between them. Store requirements move: Play Billing Library 8+ is required for new apps and updates since 2026-08-31, and Apple's server-side path is the App Store Server API with JWS — legacy receipt validation is deprecated (as of 2026-10; verify).
5. **Subscribe to store notifications** (App Store Server Notifications V2, Play RTDN) and reconcile daily against store APIs. Notifications get lost; the reconciler is the safety net.
6. **Implement refund clawback** as a normal ledger transaction with a negative leg — never a direct UPDATE.
7. **Implement leaderboards, guilds, mail** — read `references/leaderboards-guilds-mail.md` when building any of them (tie encoding, seasons, brackets, guild joins, campaign mail). Rewards from rankings are paid from a frozen snapshot through the ledger with key `season:{id}:board:{id}:player:{id}`.
8. **Add version gating and rate limits** at the edge (Technical Reference). Every response carries the server's view of `min_supported` so the client can force-update without a separate call.
9. **Emit ledger events** to analytics from the transaction outbox, not from the client. Server-side revenue is the source of truth.
10. **Write the reconciliation and audit queries** before launch: per-currency system balance, unacknowledged purchases older than 1 hour, negative balances, grants without txn.

## Deliverables

### 1. Ledger schema (Postgres)

```sql
CREATE TABLE ledger_txn (
  txn_id        uuid PRIMARY KEY,
  player_id     uuid        NOT NULL,
  idem_key      text        NOT NULL,
  kind          text        NOT NULL,          -- 'iap','level_reward','shop_buy','refund','mail_claim','admin'
  request_hash  bytea       NOT NULL,
  response      jsonb,
  actor         text        NOT NULL,          -- 'player', 'store:apple', 'support:<agent_id>'
  created_at    timestamptz NOT NULL DEFAULT now(),
  UNIQUE (player_id, idem_key)
);

CREATE TABLE ledger_entry (
  entry_id   bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  txn_id     uuid   NOT NULL REFERENCES ledger_txn(txn_id),
  account    text   NOT NULL,                  -- 'player:<uuid>' or 'system:iap'
  asset      text   NOT NULL,                  -- 'gems','coins','item:sword_01'
  amount     bigint NOT NULL CHECK (amount <> 0)
);
CREATE INDEX ON ledger_entry (txn_id);

CREATE TABLE wallet (
  player_id  uuid   NOT NULL,
  asset      text   NOT NULL,
  balance    bigint NOT NULL,
  allow_debt boolean NOT NULL DEFAULT false,
  PRIMARY KEY (player_id, asset),
  CHECK (allow_debt OR balance >= 0)
);

-- Enforce double-entry at commit time
CREATE FUNCTION ledger_balanced() RETURNS trigger AS $$
BEGIN
  IF EXISTS (SELECT 1 FROM ledger_entry WHERE txn_id = NEW.txn_id
             GROUP BY asset HAVING sum(amount) <> 0) THEN
    RAISE EXCEPTION 'unbalanced txn %', NEW.txn_id;
  END IF;
  RETURN NULL;
END $$ LANGUAGE plpgsql;
CREATE CONSTRAINT TRIGGER ledger_balanced_chk AFTER INSERT ON ledger_entry
  DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION ledger_balanced();
```

MySQL has no deferred constraint triggers: enforce balance in the application layer and run the audit query hourly.

### 2. Transaction core (Go, pgx v5)

```go
type Leg struct{ Account, Asset string; Amount int64 }
type TxnRequest struct {
    PlayerID uuid.UUID; IdemKey, Kind, Actor string; Legs []Leg; Hash []byte
}

var ErrIdemMismatch = errors.New("idempotency key reused with different request")
var ErrInsufficient = errors.New("insufficient balance")

func (l *Ledger) Apply(ctx context.Context, r TxnRequest) (json.RawMessage, error) {
    var out json.RawMessage
    err := pgx.BeginTxFunc(ctx, l.db, pgx.TxOptions{}, func(tx pgx.Tx) error {
        txnID := uuid.Must(uuid.NewV7())
        tag, err := tx.Exec(ctx, `INSERT INTO ledger_txn (txn_id, player_id, idem_key, kind, request_hash, actor)
            VALUES ($1,$2,$3,$4,$5,$6) ON CONFLICT (player_id, idem_key) DO NOTHING`,
            txnID, r.PlayerID, r.IdemKey, r.Kind, r.Hash, r.Actor)
        if err != nil { return err }
        if tag.RowsAffected() == 0 { // replay
            var h []byte
            if err := tx.QueryRow(ctx, `SELECT request_hash, response FROM ledger_txn
                WHERE player_id=$1 AND idem_key=$2`, r.PlayerID, r.IdemKey).Scan(&h, &out); err != nil { return err }
            if !bytes.Equal(h, r.Hash) { return ErrIdemMismatch }
            return nil
        }
        legs := slices.Clone(r.Legs) // sorted copy: fixed lock order prevents deadlocks
        slices.SortFunc(legs, func(a, b Leg) int {
            return cmp.Or(cmp.Compare(a.Account, b.Account), cmp.Compare(a.Asset, b.Asset))
        })
        for _, leg := range legs { // single-player txn; cross-player moves go through escrow
            if _, err := tx.Exec(ctx, `INSERT INTO ledger_entry (txn_id, account, asset, amount)
                VALUES ($1,$2,$3,$4)`, txnID, leg.Account, leg.Asset, leg.Amount); err != nil { return err }
            if !strings.HasPrefix(leg.Account, "player:") { continue }
            tag, err := tx.Exec(ctx, `INSERT INTO wallet (player_id, asset, balance) VALUES ($1,$2,$3)
                ON CONFLICT (player_id, asset) DO UPDATE SET balance = wallet.balance + EXCLUDED.balance
                WHERE wallet.allow_debt OR wallet.balance + EXCLUDED.balance >= 0`,
                r.PlayerID, leg.Asset, leg.Amount)
            if err != nil { return err }
            if tag.RowsAffected() == 0 { return ErrInsufficient }
        }
        out = buildResponse(ctx, tx, r.PlayerID, txnID) // balances after txn
        _, err = tx.Exec(ctx, `UPDATE ledger_txn SET response=$1 WHERE txn_id=$2`, out, txnID)
        return err
    })
    return out, err
}
```

A first-time debit on a missing wallet row inserts a negative balance and fails the CHECK — that is the intended `ErrInsufficient` path; map the constraint error to it. Legs are sorted by `(account, asset)` so two concurrent transactions on the same wallets cannot deadlock.

### 3. Purchase verification flow

```
client -> POST /purchase/verify {store, signed_payload|purchase_token, product_id, idem_key}
server:  1 verify signature/chain (Apple JWS) or call Play Developer API (Google)
         2 check bundle/package, product_id, environment, not revoked, purchase state = purchased
         3 check binding: appAccountToken / obfuscatedExternalAccountId == player
         4 ledger.Apply(idem_key = "<store>:<store_txn_id>", legs from catalog)
         5 Google: acknowledge or consume  |  Apple: client calls transaction.finish() after 200
         6 return balances + entitlement
```

Read `references/purchases-and-refunds.md` for Apple and Google code, notification handling and the reconciler.

### 4. Endpoint spec template

```
ENDPOINT:    POST /v1/shop/buy
AUTH:        player access token
IDEMPOTENT:  yes, key = client intent UUIDv7, 24h+ retention (ledger keeps forever)
RATE LIMIT:  5/s burst 10 per player
INPUT:       {offer_id, expected_price: {asset, amount}, config_version}
SERVER:      resolve offer from config_version + segment; reject if price differs (409 PRICE_CHANGED)
LEGS:        player:-price, system:sink:+price, player:+items, system:rewards:-items
ERRORS:      402 INSUFFICIENT, 409 PRICE_CHANGED/VERSION, 422 IDEM_MISMATCH, 426 UPGRADE_REQUIRED, 429
EVENTS:      economy.txn (outbox)
```

## Technical Reference

### Optimistic concurrency for documents

```sql
UPDATE save_slot SET blob = $1, version = version + 1, updated_at = now()
WHERE player_id = $2 AND slot = $3 AND version = $4;   -- 0 rows -> 409 with current version + blob
```

### Save-game conflict resolution

Prefer server-authoritative state; a cloud-save blob is only for state that has no economic value. When a blob conflicts (two devices offline):
- Monotonic counters (levels cleared, stars, XP): take max per field.
- Sets (unlocked cosmetics, seen tutorials): union.
- Currency and items: never in the blob; the ledger wins.
- Settings: latest server-received write wins (device clocks are untrusted).
- If a merge loses player-visible progress, show both summaries and let the player choose; archive the loser for 30 days.

### API versioning and forced update

```go
func VersionGate(minSupported, recommended semver.Version) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            v, err := semver.Parse(r.Header.Get("X-Client-Version"))
            if err != nil || v.LT(minSupported) {
                w.Header().Set("X-Min-Version", minSupported.String())
                http.Error(w, `{"code":"UPGRADE_REQUIRED"}`, http.StatusUpgradeRequired) // 426
                return
            }
            if v.LT(recommended) { w.Header().Set("X-Update-Available", recommended.String()) }
            next.ServeHTTP(w, r)
        })
    }
}
```

`minSupported` lives in remote config so it can move without a deploy. The force-update screen must render with no login and no config fetch. Keep handlers for every protocol version in the window; translate old request shapes at the edge into the current internal model.

### Rate limiting

Token bucket per `(player_id, endpoint_class)` in Redis via a Lua script (atomic read-modify-write), plus a per-IP limit on unauthenticated endpoints and a global circuit breaker per downstream. Return 429 with `Retry-After`. Heuristic budgets: reads 20/s, writes 5/s, purchase verify 2/s, chat 1/s with burst 5. Clients retry with exponential backoff + full jitter (base 250 ms, cap 30 s).

### Remote config and segmentation

- Config is an immutable, versioned, schema-validated bundle; the client sends `config_version` with every economy request so the server prices against what the player saw.
- Segment rules are evaluated server-side from server-known attributes (country, install cohort, spend tier, platform, client version). Never trust client-reported spend or country.
- Experiment bucketing: `bucket = fnv32a(experiment_salt + player_id) % 10000`; assignment logged once as an exposure event when the variant is first used, not when assigned.
- Kill switches are config keys checked at the server, not only the client.

## Diagnostics

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Players report double gems after lag | Idempotency key generated per HTTP attempt, not per intent | Persist the key client-side at tap time; reuse across retries and app restarts |
| Paid but not granted (support tickets) | Crash between store acknowledge and grant; or client never retried | Grant before acknowledge; reconciler scans unfinished purchases; client re-sends unfinished transactions at launch |
| Play auto-refunds purchases | Not acknowledged within 3 days | Acknowledge/consume after grant; alert on unacknowledged > 1 h |
| Refunded players keep the items | No notification handler or reconciler | Handle Apple REFUND / Play voided purchases; clawback txn; daily voided-purchases sweep |
| Deadlocks on gift/trade | Legs applied in arbitrary order | Sort legs by `(account, asset)`; keep txns short |
| Leaderboard ties shuffle between refreshes | Equal scores ordered lexicographically by member | Composite score with time tiebreak (`references/leaderboards-guilds-mail.md`) |
| p99 latency spikes at event start | Hot rows (global counter, guild row) | Shard counters, batch increments, move contention off the request path |
| Old clients crash after deploy | Removed field or changed enum | Additive changes only inside the compat window; edge translation |
| Support tool grants not in reports | Admin path bypasses ledger | Admin grants are ledger txns with `actor = support:<id>` and a reason |

## Anti-Patterns

**The Trusting Client** — client sends `{"gems": 500}` and the server stores it. The client sends intents; the server computes outcomes.

**The Per-Attempt Idempotency Key** — a fresh key each retry is no key at all.

**The Balance-Only Wallet** — no journal. You cannot audit, reverse fraud, or answer "where did this come from".

**The Acknowledge-First Purchase** — acknowledging or finishing before the grant commits; a crash in between loses a paid purchase.

**The Receipt Cache** — validating once and never listening for refunds. Refund abuse becomes a free-currency faucet.

**The Fan-Out Mailbox** — inserting a million rows to send a compensation mail. Use campaign rows and lazy per-player claims.

**The Live Leaderboard Payout** — paying rewards from the live sorted set while late scores still arrive. Freeze, snapshot, then pay.

**The Second Economy** — support, QA and LiveOps tools writing balances directly.

## Quality Checklist

- [ ] All currency/item mutations go through one ledger API; legs balance per asset
- [ ] Idempotency key = client intent, unique per player, stored in the same DB transaction
- [ ] Replay with different payload returns 422; replay with same payload returns the original response
- [ ] Legs applied in sorted order; no debit can drive a non-debt wallet negative
- [ ] Purchases: signature/API verified, binding to player checked, `store_txn_id` unique, grant before ack
- [ ] App Store Server Notifications V2 and Play RTDN handled; daily reconciler runs and alerts
- [ ] Refund clawback implemented as a ledger txn; repeat refunders flagged to security
- [ ] Leaderboard ties deterministic; season payouts from frozen snapshot via ledger
- [ ] Mail claims idempotent per (mail_id, player_id); broadcasts not fanned out
- [ ] Version gate returns 426 with min version; force-update screen works offline
- [ ] Rate limits per player and per IP; 429 with Retry-After; client backoff with jitter
- [ ] Economy requests carry `config_version`; server re-prices from it
- [ ] Ledger events emitted via outbox to analytics
- [ ] Audit queries scheduled: unbalanced txns, negative balances, unacknowledged purchases

## Related Skills

- `gamedev-platform-server-architect` — service boundaries, shard keys, consistency per domain; escalate when a feature needs cross-shard writes.
- `gamedev-infrastructure-engineer` — database sizing, Redis topology, backups, regions.
- `gamedev-anti-cheat-security` — consumes refund flags, integrity verdicts and ledger anomalies; owns enforcement.
- `gamedev-monetization-designer` — offer and pack definitions, refund policy.
- `gamedev-liveops-designer` — event and config needs; `gamedev-pvp-designer` — ranking and season rules.
- `gamedev-analytics-engineer` — consumes ledger outbox events; `gamedev-delivery-release` — force-update and rollout.
- `gamedev-ios-engineer` / `gamedev-android-engineer` — client purchase flow, `finish()` and acknowledgement timing.
- `gamedev-qa-verifier` — sandbox purchase, refund and replay test plans; `gamedev-reviewer` — server code review.
- If installed, `game-economy-balancer` — the flows whose integrity the ledger guarantees.
