---
name: gamedev-platform-server-architect
description: >-
  Design the backend platform for a live game: service decomposition, build vs buy
  across Nakama, PlayFab, AccelByte, Pragma, UGS, Photon, GameLift Servers and
  Agones, consistency per domain, player sharding, scale targets and data residency.
  Use when someone asks "what backend should we use", sketches a service map or
  architecture diagram, picks between a BaaS and custom servers, sizes CCU and RPS
  from a DAU forecast, plans cross-platform account linking or client version
  windows, or needs GDPR, account deletion or China launch constraints designed in.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: backend
---

# Game Platform & Server Architect

A game backend is a ledger with a social graph bolted on. Everything that can be bought, earned, traded or ranked must be decided by the server, written once, and survive a client that is three versions old, offline for a week, and possibly lying. The architect's job is not to draw boxes; it is to decide, per domain, **who is authoritative, how consistent it must be, which key it shards on, and what happens when it is down** — and to buy everything that is not a differentiator, behind an interface that lets you leave. In 2026 that last clause is not theoretical: Multiplay and Hathora both disappeared as hosting options within six weeks of each other.

## Role Profile

At a top-grossing studio this is the platform/central-tech lead: King's "Shared Tech" ("the engine that powers all our live games"), Supercell Central Tech and Supercell ID, Scopely's Playgami. They own service boundaries and the platform contract that many game teams consume.

- **Responsibilities:** service decomposition and API contracts; build vs buy decisions; data model and consistency rules per domain; capacity model from DAU forecast; client-compatibility policy; data-residency and privacy architecture; design reviews for every new service.
- **Hard skills:** distributed systems on the JVM (Java dominates at Supercell, King, Dream Games; Go/Node accepted for Supercell ID; Erlang/Scala at Wargaming), sharded MySQL/Postgres, Redis, Kafka, Kubernetes, GCP (BigQuery, Vertex) or AWS; multi-tenant service design; API/SDK ownership.
- **KPIs (inferred from postings):** platform SLOs, game-team adoption, game-team time-to-ship, cost per DAU, incidents caused by platform changes.
- **Collaborators:** every game team, SRE/infra, data/ML, security, LiveOps.
- Sources: https://hitmarker.net/jobs/king-senior-backend-engineer-1745379, https://supercell.com/en/careers/server-engineer-supercellid/1729743, https://thenewstack.io/inside-supercells-minimalist-massive-social-network/

## When to Use / Not

Use for: greenfield backend design, BaaS selection or migration, service boundaries, scale planning, cross-platform identity, residency/compliance architecture, client-compat policy.

Not for:
- Writing the ledger, receipt validation, leaderboards or mailbox code → `gamedev-backend-engineer`.
- Clusters, Agones fleets, Terraform, regions, DB operations → `gamedev-infrastructure-engineer`.
- Tick rate, prediction, rollback, state sync → `gamedev-netcode-engineer`.
- Threat modeling and attestation → `gamedev-anti-cheat-security`.
- Event taxonomy and warehouse modeling → `gamedev-analytics-engineer`.
- SLOs, incident runbooks, launch-day ops → `gamedev-live-serving`.

## Inputs to Gather

- **Genre and multiplayer shape:** async (match-3, 4X, idle), session-based real-time (MOBA, shooter, battle royale), persistent shared world. Default: async mobile F2P with a social layer.
- **DAU forecast** at soft launch, global launch, and 12 months; sessions/day; median session length. Default: 3 sessions × 8 min.
- **Platforms:** iOS, Android, PC (Steam), console; cross-progression required? Default: iOS + Android, cross-progression yes.
- **Team:** backend headcount and language. Under 3 backend engineers, bias hard toward buy.
- **Markets:** EU (GDPR), US (COPPA if under-13 audience), mainland China, Korea, Japan. Default: global ex-China.
- **Monetization surfaces:** store IAP, webshop/DTC, ads, subscriptions. Webshops are now material (FunPlus >25% of mobile revenue; Monopoly GO webshop is invisible to chart trackers) — design entitlement as store-agnostic from day one.
- **Existing commitments:** engine (Unity, Unreal, in-house C++), cloud contract (GCP vs AWS), existing BaaS.
- **LiveOps cadence:** weekly events? hourly offers? This sets config and segmentation requirements.

## Method

1. **Classify each domain by authority and consistency** using the matrix in Technical Reference. Do this before any vendor talk; vendors differ mostly in which of these they get right.
2. **Draw the service map** (Deliverable 1). One owner per write path. If two services can mutate a wallet, you have a duplication bug waiting for a retry storm.
3. **Pick the shard key.** For async games, shard almost everything by `player_id`; that is what makes a single-player transaction a local ACID transaction. Isolate the few genuinely cross-player domains (guilds, trades, gifting, global leaderboards) and give them explicit cross-shard protocols (outbox + idempotent consumers), not distributed transactions.
4. **Size the load** with the capacity model (Technical Reference). Size to peak event hour, not average — a limited-time event start is a synchronized login of your whole active base.
5. **Run build vs buy per service**, not per platform (Deliverable 2). Buy commodity (auth, push, CDN, crash, BaaS primitives if small team); build the economy ledger and anything the LiveOps team iterates weekly. Score exit cost explicitly.
6. **Design identity first.** Every other service keys on `player_id`. Specify account linking, merge rules, recovery and deletion before anything else (Deliverable 3), because changing identity semantics after launch requires migrating every table.
7. **Define the client compatibility window** (Deliverable 4) and the protocol versioning rule. A mobile game always has a long tail of old clients; the backend must serve N-2 versions minimum.
8. **Design residency and privacy** (Technical Reference): where each table lives, what is PII, erasure and export paths, China split if needed.
9. **Write the failure-mode table**: for each service, what the game does when it is down. Chat down = game playable. Ledger down = store closed, play continues with server-queued rewards. Identity down = only cached sessions continue.
10. **Write the ADR** (Deliverable 5) and get sign-off from infra, security and one game team lead before anyone writes code.

## Deliverables

### 1. Service map

```
SERVICE         | OWNS (write path)              | AUTH | CONSISTENCY | SHARD KEY      | STORE            | DOWN => GAME DOES
identity        | accounts, links, sessions      | srv  | strong      | account_id     | SQL              | cached tokens only
profile         | name, avatar, settings, prog.  | srv  | strong/row  | player_id      | SQL              | read-only profile
inventory       | items, instances, loadouts     | srv  | strong      | player_id      | SQL              | queue grants
economy-ledger  | wallets, journal, idempotency  | srv  | strong+audit| player_id      | SQL              | close store/spend
store/receipts  | catalog, orders, entitlements  | srv  | strong      | player_id      | SQL              | close store
social          | friends, blocks, presence      | srv  | eventual    | player_id      | SQL + Redis      | hide social UI
guilds          | guild, members, roles, perks   | srv  | strong/guild| guild_id       | SQL              | read-only guild
chat            | channels, messages, moderation | srv  | eventual    | channel_id     | vendor or KV     | hide chat
matchmaking     | tickets, matches               | srv  | ephemeral   | region/queue   | Redis / OM       | queue paused
leaderboards    | scores, seasons, brackets      | srv  | eventual    | board_id       | Redis + SQL snap | stale board
mail/inbox      | messages, attachments, claims  | srv  | strong claim| player_id      | SQL              | hide inbox
liveops-config  | config, events, segments, A/B  | srv  | versioned   | n/a (global)   | Git + CDN + KV   | bundled default
analytics-ingest| raw events                     | cli+srv | at-least-once | event time  | Pub/Sub -> BQ    | buffer on device
```

### 2. Build vs buy scorecard (per service)

```
SERVICE: [name]
OPTION        | FIT (0-3) | TIME-TO-LIVE | 3-YR TCO | LOCK-IN / EXIT COST | VENDOR RISK | DATA RESIDENCY | VERDICT
custom        |
[vendor A]    |
[vendor B]    |
EXIT PLAN: [the interface you code against; the export format; the date you test the export]
```

Read `references/build-vs-buy-2026.md` when filling this — it has the vendor matrix and the 2026 landscape changes.

### 3. Identity and linking spec

```
PRIMARY KEY:       player_id (UUIDv7, server-minted, never derived from a platform ID)
CREDENTIALS:       device (anonymous) | Game Center | Play Games v2 | Apple | Google | Steam | email
LINK RULE:         one credential -> at most one player_id; one player_id -> many credentials
CONFLICT ON LINK:  credential already bound to another player_id -> show both progress summaries, player picks,
                   loser is archived 30 days (not deleted), purchases on loser are re-granted to winner
RECOVERY:          [support flow, proof required, cooldown]
DELETION:          in-app path (App Store requirement); soft-delete 30 d -> hard-delete + ledger anonymization
SESSION:           short-lived access token (15 min) + refresh token bound to device; revocable server-side
```

### 4. Client compatibility policy

```
WINDOW:        server supports client protocol versions [min_supported .. current]; target N-2 builds, >= 90 days
SOFT UPDATE:   when client_version < recommended -> prompt, dismissible
FORCE UPDATE:  when client_version < min_supported -> blocking screen with store link; must work without login
BUMP RULE:     min_supported may advance only when < 2% of DAU (heuristic) is on versions below it, or for security
CONTRACT:      additive-only schema changes inside the window; removed fields keep defaults until window passes
CONFIG:        every config payload carries schema_version; server filters by client capability, not client version string
```

### 5. Architecture Decision Record

```
ADR-[n]: [decision]
CONTEXT:      [DAU, genre, team, markets]
DECISION:     [what]
ALTERNATIVES: [options + why rejected]
CONSEQUENCES: [cost, lock-in, what becomes hard]
EXIT:         [how we leave; tested on date]
REVIEW DATE:  [when to revisit]
```

## Technical Reference

### Consistency per domain

| Domain | Model | Why |
| --- | --- | --- |
| Wallets, ledger, IAP entitlements | Strong, serializable per player; append-only journal | Money. Double-grants and lost purchases are the two incidents that cost real revenue and store standing |
| Inventory, progression | Strong per player | Duplicated items become a black-market currency |
| Guild treasury, guild perks | Strong per guild, idempotent per contribution | Many writers, one balance |
| Trades, gifts between players | Two-phase via outbox + escrow, not distributed transactions | Cross-shard; must survive partial failure |
| Leaderboards | Eventual (seconds); rewards computed from a frozen snapshot | Rank display tolerates lag; payouts do not |
| Friends, presence | Eventual | Nobody notices 5 s presence lag |
| Chat | Eventual, at-least-once with client dedup | Ordering per channel is enough |
| LiveOps config | Versioned, immutable releases, atomic pointer flip | Partial config is worse than old config |
| Analytics | At-least-once, dedup in warehouse by event_id | Never in the gameplay request path |

### Capacity model (heuristics — calibrate with telemetry)

```
avg_CCU   = DAU × sessions_per_day × session_min / 1440
peak_CCU  = avg_CCU × peak_factor            # 2–3× daily peak; 4–8× at a global event start
API_RPS   = peak_CCU × calls_per_session_min / 60
write_RPS = API_RPS × write_share            # async mobile: 20–40% writes (heuristic)
```

Worked: 2M DAU × 3 × 8 min / 1440 = **33k avg CCU**; × 3 = **100k peak CCU**. At 6 calls per session-minute (heuristic for async mobile with batching) → **10k API RPS**, ~3k write RPS. Event start at 6× average → **200k CCU, 20k RPS** for 10–20 minutes. Design the login path and config fetch for the event-start number; design steady-state services for the daily peak.

| Shape | calls/session-min (heuristic) | Dominant load |
| --- | --- | --- |
| Async puzzle / match-3 | 2–6 | Level start/end, store, config |
| 4X / SLG | 10–30 | Timers, march updates, alliance chat |
| Session PvP (dedicated servers) | 1–3 to backend; game traffic on game servers | Matchmaking, results write |

**Sharding by player.** Logical shards (e.g., 4,096) mapped to physical DBs via a directory table; `shard = hash(player_id) mod 4096`. Never shard on a value that changes (region, guild). Plan re-sharding as moving logical shards, not rehashing. A shard should hold a few hundred thousand to a few million players (heuristic) so a single DB failover affects a bounded slice.

### Data residency, privacy, China

- **GDPR:** export (Art. 20) and erasure (Art. 17) within one month (Art. 12(3)). Keep PII (email, IP, device IDs, chat text) in separate tables from gameplay so erasure is a delete plus ledger anonymization, not a schema-wide hunt. Financial records may need legal retention — anonymize, do not drop.
- **Account deletion:** apps with account creation must offer in-app deletion on the App Store. Wire it to the same erasure pipeline.
- **Minors:** age gate drives chat, ads personalization, and purchase limits; store the age band, not the birthdate, where possible.
- **Residency:** EU data in EU regions is a contract requirement for some publishers and partners, not strictly GDPR; decide per partner. Keep the analytics pipeline region-aware (pseudonymize before cross-border transfer).
- **China (as of 2026-10; verify):** treat mainland China as a separate deployment with a local operator/publisher, local cloud (Tencent Cloud, Alibaba Cloud), separate account system, real-name and minor play-time rules, and a game license. Global UGS ended for mainland China, Hong Kong and Macau orgs on 2026-06-30; the replacement is UOS (https://support.unity.com/hc/en-us/articles/48560161446804). Do not share a database across the boundary.

### Platform identity facts

- iOS: Game Center exposes `teamPlayerID` / `gamePlayerID` (scoped, not global). If you offer third-party social login, App Review guideline 4.8 requires an equivalent privacy-focused login option such as Sign in with Apple (verify current wording). StoreKit 2 `appAccountToken` lets you bind a purchase to `player_id` — set it on every purchase.
- Android: Play Games Services v2 sign-in is automatic; use it for recovery, not as the primary key. Set `obfuscatedAccountId` on Play Billing purchases to bind to `player_id`.
- Steam: authenticate with session tickets validated server-side.

Read `references/service-catalog.md` for per-service API surfaces, data entities and the failure contracts.

## Diagnostics

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Duplicate currency after network retries | Write path not idempotent; client retries create new transactions | Idempotency key per client intent, stored with the ledger entry in the same transaction |
| Login storm takes down DB at event start | Config + profile + inventory fetched in separate uncached calls at the same second | Single bootstrap call, CDN-served config, jittered event start (spread over 5–15 min), pre-scale |
| Players lose progress after linking a second device | Merge rule picks newest login instead of asking | Explicit conflict UI; archive loser 30 days; re-grant purchases |
| One shard hot | Shard key correlated with activity (guild, region, signup date) | Hash `player_id`; move logical shards |
| Cross-shard trade leaves items in limbo | Distributed transaction without recovery | Escrow + outbox + idempotent settle; reconciler job |
| Vendor sunset forces rewrite | Game code calls vendor SDK directly | Own a thin platform interface; vendor adapter behind it |
| Old clients crash on new config | Config not filtered by client capability | `schema_version` on payload; server-side filtering; additive changes only |
| Erasure request takes a week of engineering | PII spread across gameplay tables | PII vault table keyed by `player_id`; erasure job; quarterly drill |

## Anti-Patterns

**The Client-Side Wallet** — balance computed on device and "synced". Every memory editor becomes a mint.

**The Platform-ID Primary Key** — keying players on Game Center or Google IDs. Cross-platform, account recovery and deletion all break.

**The Vendor-Shaped Game** — gameplay code calling BaaS SDKs directly. Hathora (shut down 2026-05-05) and Multiplay (Unity support ended 2026-03-31) customers who did this rewrote under deadline.

**The Distributed Transaction** — 2PC across player shards for gifting. Use escrow and idempotent settlement.

**The Average-Load Plan** — capacity sized to daily average. Events synchronize your entire base into one minute.

**The Microservice Confetti** — 25 services for 4 backend engineers. Start with a modular monolith with the service map as module boundaries; split when a module needs independent scaling or ownership.

**The Forever Client** — no minimum supported version. Six months later the protocol cannot evolve and you carry dead code paths in the ledger.

**The Build-Everything Ego** — custom chat, push, auth and CDN in year one. Build the ledger and LiveOps config; buy the rest.

## Quality Checklist

- [ ] Every domain has one write owner, a named consistency model and a shard key
- [ ] Every money/item mutation path is idempotent and journaled
- [ ] Cross-player operations use escrow/outbox, never cross-shard 2PC
- [ ] Capacity sized for event-start peak with the formula and numbers written down
- [ ] Build vs buy scored per service, with exit plan and a dated export test
- [ ] Vendor facts in the ADR tagged with date and re-verified (2026 landscape changed)
- [ ] Identity spec covers linking conflict, recovery, in-app deletion
- [ ] Purchases bound to `player_id` via `appAccountToken` / `obfuscatedAccountId`
- [ ] Client compat window, soft/force update rules and bump threshold defined
- [ ] Failure-mode table: game behavior when each service is down
- [ ] PII isolated; erasure and export paths documented with a response SLA
- [ ] China (if in scope) is a separate deployment with its own data
- [ ] Analytics ingest out of the gameplay request path

## Related Skills

- `gamedev-backend-engineer` — implements the ledger, receipts, inventory, leaderboards, mail and config services this map defines.
- `gamedev-infrastructure-engineer` — turns capacity numbers and residency rules into clusters, regions, databases and Terraform.
- `gamedev-netcode-engineer` — owns real-time protocol and tick model; hand off once session hosting is decided.
- `gamedev-anti-cheat-security` — threat model for every write path; review before APIs freeze.
- `gamedev-analytics-engineer` — event schema and warehouse; consumes analytics-ingest.
- `gamedev-live-serving` — SLOs, kill switches and event-day runbooks on top of this design.
- `gamedev-delivery-release` — force-update and phased rollout mechanics that the compat window depends on.
- `gamedev-liveops-designer` and `gamedev-monetization-designer` — the consumers of config, segmentation and store; interview them before designing those services.
- If installed, `game-economy-balancer` — the economy math whose flows the ledger records.
