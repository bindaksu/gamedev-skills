# Leaderboards, Guilds, Mailbox, Inventory

Read when implementing ranking, guild membership/treasury, inbox/compensation mail, or the item model.

## Leaderboards on Redis sorted sets

**Keys:** `lb:{board}:{season}` for global; `lb:{board}:{season}:b{bracket}` for bracketed cohorts (e.g., 50-player event races). Cluster mode: put a hash tag on keys you touch together, e.g. `lb:{weekly:42}:...`.

**Ties.** Redis orders equal scores lexicographically by member, which looks random to players. Encode the tie-break into the score. Scores are IEEE-754 doubles: integers are exact up to 2^53.

```
score = points * 2^22 + (2^22 - 1 - t)      # t = seconds since season start, t < 2^22 (~48.5 days)
points must stay below 2^31 so the product stays under 2^53
earlier achievement of the same points ranks higher
```

Longer seasons: use coarser `t` (minutes: 2^22 min ~ 8 years) or keep a secondary sorted set for ties.

```go
const shift = 1 << 22

func encode(points int64, t time.Duration) float64 {
    sec := int64(t / time.Second)
    return float64(points*shift + (shift - 1 - sec))
}
func decode(score float64) int64 { return int64(score) / shift }

// Keep best score only; GT requires Redis 6.2+
func Submit(ctx context.Context, rdb *redis.Client, key, member string, points int64, seasonStart time.Time) error {
    return rdb.ZAddGT(ctx, key, redis.Z{Score: encode(points, time.Since(seasonStart)), Member: member}).Err()
}
```

For cumulative boards (points add up), use `ZINCRBY` on raw points in one key and do tie-breaks at snapshot time from a last-update hash — encoded time cannot be incremented.

**Queries:** rank `ZREVRANK key member`; page `ZRANGE key start stop REV WITHSCORES`; around-me `ZREVRANK` then `ZRANGE key rank-5 rank+5 REV`. Friends board: `ZMSCORE key f1 f2 ...` for up to a few hundred friends, sort in the service.

**Seasons:** write to the new season key at season start; never `DEL` the old key until the snapshot is verified. Expire old keys with `EXPIRE` after snapshot.

**Snapshot and payout:**
1. At season end + grace (e.g., 5 min for in-flight submissions), stop accepting writes (`season.state = closing`).
2. `ZRANGE ... REV WITHSCORES` in pages → `leaderboard_snapshot(season_id, board, rank, player_id, points)`.
3. Compute reward tiers from the snapshot; enqueue payouts as mail or direct ledger txns with key `season:{id}:{board}:{player}`.
4. Anti-cheat review window for top ranks before payout (top 100 held 24 h is a common heuristic).

**Bracketing:** assign players to brackets of N by similar skill or activity at first submission (`SET NX` on `lbmap:{season}:{player}`), fill brackets sequentially per tier. Bracket boards keep competition reachable for everyone, which is why event races use them.

**Memory heuristic:** a sorted set entry costs on the order of 100 bytes with short members; 10M members is roughly 1 GB — measure with `MEMORY USAGE`.

## Guilds

```sql
CREATE TABLE guild (
  guild_id     uuid PRIMARY KEY,
  name         text NOT NULL,
  tag          text NOT NULL,
  member_cap   int  NOT NULL DEFAULT 50,
  member_count int  NOT NULL DEFAULT 0 CHECK (member_count <= member_cap),
  join_policy  text NOT NULL DEFAULT 'open',   -- open | request | closed
  version      bigint NOT NULL DEFAULT 0
);
CREATE TABLE guild_member (
  guild_id   uuid NOT NULL REFERENCES guild,
  player_id  uuid NOT NULL,
  role       text NOT NULL,                   -- leader | officer | member
  joined_at  timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (guild_id, player_id)
);
CREATE UNIQUE INDEX one_guild_per_player ON guild_member (player_id);
```

Join is one transaction: `UPDATE guild SET member_count = member_count + 1 WHERE guild_id=$1 AND member_count < member_cap` (0 rows → full) then `INSERT guild_member` (unique violation → already in a guild). Leave decrements in the same way. Leader leaves → promote oldest officer, else oldest member, in the same transaction. Enforce a rejoin cooldown (e.g., 24 h) to stop reward-hopping between guilds.

Guild treasury and contributions use the ledger with `account = 'guild:<id>'`; contribution idempotency key `guild:{id}:contrib:{player}:{intent}`. Guild-wide rewards (chest unlocked) are paid via mail to members present at the snapshot time.

## Mailbox / inbox

```sql
CREATE TABLE mail_campaign (           -- one row for a broadcast or segment send
  mail_id      uuid PRIMARY KEY,
  segment      text,                    -- null for direct mail
  title_key    text NOT NULL,           -- localization key, not text
  attachments  jsonb NOT NULL,          -- [{asset, amount}]
  starts_at    timestamptz NOT NULL,
  expires_at   timestamptz NOT NULL,
  min_client   text                     -- hide from clients that cannot render it
);
CREATE TABLE mail_direct (mail_id uuid, player_id uuid, PRIMARY KEY (player_id, mail_id));
CREATE TABLE mail_claim (
  mail_id   uuid NOT NULL,
  player_id uuid NOT NULL,
  txn_id    uuid NOT NULL,
  claimed_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (player_id, mail_id)
);
```

Inbox read = active campaigns whose segment matches the player (evaluated at read time) + direct mail − claimed. Claim = ledger txn with idem key `mail:{mail_id}` and `INSERT mail_claim` in the same DB transaction. Compensation for an outage is a campaign with `segment = 'active_during:<window>'`, not a script that writes balances.

## Inventory model

- **Stackables** (consumables, materials) live in `wallet` as assets — same ledger.
- **Instances** (gear with rolled stats, unique cosmetics) live in `item_instance(instance_id, player_id, item_def, attrs jsonb, created_by_txn, state)`; ledger legs reference `item:<instance_id>` with amount ±1.
- Item definitions are config; instances store only the def id + rolled attributes, so rebalancing a def does not require a migration.
- Trades/gifts between players: move to `escrow:<trade_id>` account in the sender's shard, settle into the receiver's shard with an idempotent consumer, refund from escrow on timeout.
