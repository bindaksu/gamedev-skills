# Service Catalog — API Surfaces, Entities, Failure Contracts

Read when turning the service map into contracts for implementers. Each block is the minimum a service must expose; names are suggestions. All write endpoints take an `Idempotency-Key` and return the same response on replay.

## identity
- **Entities:** `account(player_id, created_at, status, age_band, region_home)`, `credential(provider, subject, player_id, linked_at)` unique on `(provider, subject)`, `session(refresh_id, player_id, device_id, expires_at, revoked)`.
- **API:** `POST /auth/{provider}` -> tokens; `POST /link/{provider}`; `POST /unlink/{provider}` (refuse if last credential); `POST /account/delete` (starts 30-day soft delete); `GET /account/export`.
- **Contract:** access token 15 min, refresh rotating; revocation list checked on refresh. Bootstrap must work for anonymous device accounts so FTUE never blocks on a login wall.
- **Down:** existing sessions continue until access-token expiry; new logins fail with retry-after.

## profile
- **Entities:** `profile(player_id, display_name, avatar_id, level, xp, flags jsonb, version)`.
- **API:** `GET /profile/me` (part of bootstrap), `PATCH /profile/me` with `If-Match: version`.
- **Contract:** display names go through moderation; flags are server-written only.

## inventory
- **Entities:** stackables `inventory_stack(player_id, item_id, qty)`; instances `item_instance(instance_id, player_id, item_id, attrs jsonb, created_by_txn)`.
- **API:** read-only to clients; mutated only through ledger transactions (grant, consume, craft).
- **Contract:** every instance carries the transaction that created it — required for rollback after fraud.

## economy-ledger
- **Entities:** `wallet(player_id, currency, balance, version)`, `journal_entry(txn_id, player_id, currency, delta, reason, ref)`, `txn(txn_id, player_id, idem_key, kind, status, created_at)`.
- **API:** internal `POST /txn` with a list of legs (debits/credits across currencies and items); clients call intent endpoints (`/shop/buy`, `/level/complete`) that build legs server-side.
- **Contract:** atomic, idempotent, sum of legs per currency balanced against a system account; balance never negative unless the currency allows debt.
- **Down:** close store and spends; queue earned rewards as pending grants keyed by intent.

## store / receipts / entitlements
- **Entities:** `catalog_item(sku, platform_product_ids, grants, price_tier, segment_rules)`, `order(order_id, player_id, store, store_txn_id, status)`, `entitlement(player_id, sku, source_order, state)`.
- **API:** `GET /store` (segmented catalog), `POST /purchase/verify` (Apple JWS or Play token), store notification webhooks (App Store Server Notifications V2, Play RTDN).
- **Contract:** store-agnostic entitlement: IAP, webshop and promo all produce the same entitlement record; `store_txn_id` unique to block replay.

## social (friends, blocks, presence)
- **Entities:** `edge(player_a, player_b, state)` stored both directions; `block(player_id, blocked_id)`; presence in Redis with TTL.
- **Contract:** block is enforced server-side in chat, invites, gifting and matchmaking — not just hidden in UI.

## guilds
- **Entities:** `guild(guild_id, name, tag, settings, member_count, version)`, `membership(guild_id, player_id, role, joined_at)`, `guild_ledger` (same shape as economy ledger).
- **Contract:** join/leave/kick are idempotent; member cap enforced with optimistic concurrency on `guild.version`; leave cooldown to stop perk-hopping.

## chat
- **Shape:** channels (global, guild, DM, match), message ordering per channel, moderation pipeline (filter -> report -> action), retention policy.
- **Default:** buy or use Nakama chat; build only moderation hooks and retention.
- **Down:** game remains fully playable.

## matchmaking
- **Entities:** `ticket(ticket_id, player_ids, region_pings, mmr, mode, created_at)`; match proposals; allocation result (server address + token).
- **Contract:** tickets expire; allocation request is idempotent per match_id; backend never returns a server address without a join token.

## leaderboards
- **Shape:** live board in Redis sorted sets, seasonal partitions, bracketed boards (e.g., 50-player cohorts), snapshot to SQL at season close; payouts computed from the snapshot through the ledger.

## mail / inbox
- **Entities:** `mail(mail_id, player_id or segment_id, attachments, expires_at)`, `mail_claim(mail_id, player_id, txn_id)` unique.
- **Contract:** broadcast mail is one row per campaign plus a per-player claim row — never fan out a million rows at send time.

## liveops-config
- **Shape:** config authored in Git or a CMS, validated against a schema, released as an immutable versioned bundle, served from CDN; per-player overrides resolved server-side from segments and experiment assignments.
- **Contract:** client boots with a bundled default; never blocks boot on config; every risky feature has a kill switch.

## analytics-ingest
- **Shape:** client batches events (event_id, player_id, session_id, ts_client, schema_version) -> HTTPS collector -> Pub/Sub or Kafka -> BigQuery. Server-side events (purchases, grants) are emitted from the ledger, not the client — they are the source of truth for revenue.

## Failure contract summary

| Service down | Player-visible behavior | Recovery |
| --- | --- | --- |
| identity | New logins fail; existing play continues | Retry with backoff + jitter |
| ledger / store | Store closed banner; play continues; rewards queued | Drain pending grants idempotently |
| inventory | Loadout read from cached copy; no crafting | Same |
| social / chat | Panels hidden | None needed |
| leaderboards | Stale board with timestamp | Rebuild from SQL snapshot |
| matchmaking | Queue shows paused | Tickets re-submitted |
| config | Last cached or bundled config | Pointer flip back |
