---
name: gamedev-infrastructure-engineer
description: >-
  Run the infrastructure under a live game: Kubernetes and Agones fleets with fleet
  autoscaling, GameLift Servers containers, regions and latency, dedicated vs relay
  hosting, event-spike scaling, CDN for asset bundles, Postgres, Spanner, Cassandra
  and Redis at scale, game-specific SLIs, cost per DAU, Terraform, backups, DR and
  multi-region. Use when writing Fleet or FleetAutoscaler YAML or Terraform for GKE,
  picking regions or a hosting vendor, preparing for a launch or event spike, the
  cloud bill grows faster than DAU, or someone asks what the RPO for the ledger is.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: backend
---

# Game Infrastructure Engineer

Game infrastructure fails on the calendar, not on the graph. Load does not grow smoothly; it arrives at 10:00 UTC when the event starts, at the moment a featuring goes live, and at the minute a streamer hits Play. Everything here is designed around three numbers you can defend in a review: **peak CCU at the worst minute, the RPO of the ledger, and cost per DAU**. Game servers are cattle and must be killable at any moment between matches; the economy database is the one pet, and it gets synchronous replication, point-in-time recovery and a restore drill you have actually run. Keep the hosting layer swappable — 2026 removed two hosting providers from under their customers.

## Role Profile

The SRE/DevOps/infra engineer for a live title or central platform. Dream Games' Senior DevOps posting asks for "GCP (preferred) or AWS", Docker/Kubernetes, Terraform/Ansible, Jenkins, MySQL/DynamoDB/Redis/Kafka, with New Relic, ELK, Prometheus and Grafana as a plus; Agones is typically "nice to have", with Supersolid running game, lobby and messaging servers on GKE + Agones in production. King runs on GKE with Terraform and Helm; Supercell on AWS with Terraform.

- **Responsibilities:** clusters, fleets, regions, databases, CDN, CI/CD infrastructure, observability, cost, security hardening, RCA and automation that prevents recurrence.
- **KPIs (inferred):** availability/SLO attainment, MTTR, cloud cost per DAU, deployment frequency and pipeline time.
- **Collaborators:** backend, build/release, security, game teams, finance (for cost).
- Sources: https://www.dreamgames.com/jobs/senior-devops-engineer, https://cloud.google.com/customers/supersolid, https://builtin.com/job/uncapped-games-senior-devops-engineer-sre-focus/3271887

## When to Use / Not

Use for: cluster and fleet design, hosting vendor choice, region plan, autoscaling, CDN, database operations, observability stack, cost model, Terraform, backup/DR.

Not for:
- Service boundaries and consistency models → `gamedev-platform-server-architect`.
- Application code (ledger, receipts, leaderboards) → `gamedev-backend-engineer`.
- Tick rate, netcode topology tradeoffs → `gamedev-netcode-engineer`.
- Incident command, launch-day runbooks, maintenance comms → `gamedev-live-serving`.
- Build pipelines, signing, store submission → `gamedev-delivery-release`.

## Inputs to Gather

- Capacity model from the architect: daily peak CCU, event-start peak, API RPS. Default: event peak = 6× daily average CCU.
- Player geography by country (from analytics or soft-launch data). Default: plan from install distribution of the soft-launch markets, re-plan at global launch.
- Session model: async only, or dedicated servers (players per server, match length, tick rate, vCPU per server).
- Cloud and contracts: GCP or AWS commit, China needs. Default: GCP (GKE, Cloud SQL/AlloyDB or Spanner, Memorystore, BigQuery), AWS equivalent noted.
- Data tiers and their RPO/RTO (ledger, profile, leaderboards, chat, analytics).
- Budget target for cost per DAU.

## Method

1. **Write the capacity sheet** (Deliverable 1) and size every tier for the event-start minute. Node provisioning takes minutes; a buffer you did not pre-provision does not exist at 10:00:30.
2. **Choose hosting per workload**: stateless APIs on Kubernetes Deployments + HPA; session game servers on Agones (portable) or GameLift Servers / managed edge (less ops); co-op/P2P on a relay (Photon, UGS Relay) where authority is not required. Keep game server images Agones-SDK compatible regardless — that is your exit.
3. **Pick regions** from player distribution and RTT budgets (Technical Reference). Use client-side ping beacons per region at matchmaking time, not GeoIP alone.
4. **Define fleets and autoscalers** — read `references/agones-and-hosting.md` when writing Fleet, FleetAutoscaler, or allocation manifests. Buffer sized to cover allocation rate × node provisioning time.
5. **Pick data stores per tier** (Technical Reference table). The ledger goes on a relational store with synchronous HA and PITR; Redis is a cache and ranking engine, never the system of record.
6. **Put assets behind a CDN** with content-hashed immutable paths and a short-TTL manifest; prewarm before events.
7. **Instrument game SLIs** (Deliverable 3) and alert on SLO burn rate, not on CPU.
8. **Codify everything in Terraform** — read `references/terraform-gcp.md` for the GKE, node pool, firewall and state-backend skeleton. Remote state with locking; one state per environment per region.
9. **Plan DR** (Deliverable 4): RPO/RTO per tier, restore drills on a calendar, region evacuation runbook.
10. **Build the cost model** (Technical Reference) and review it monthly against DAU; investigate any month where cost grows faster than DAU.

## Deliverables

### 1. Capacity sheet

```
TIER             | UNIT          | PER-UNIT CAPACITY   | DAILY PEAK | EVENT PEAK | HEADROOM | UNITS @ EVENT | SCALE MECHANISM     | LEAD TIME
edge/API         | pod (2 vCPU)  | [RPS measured]      |            |            | 30%      |               | HPA + pre-scale     | 1–2 min
game servers     | GameServer    | [players/server]    |            |            | buffer   |               | FleetAutoscaler     | node: 2–5 min
ledger DB        | primary       | [write TPS measured]|            |            | 50%      |               | vertical / shard    | hours–days
Redis            | shard         | [ops/s measured]    |            |            | 50%      |               | add shards (planned)| hours
CDN              | n/a           | provider            |            |            | prewarm  |               | provider            | prewarm 1 h
```

### 2. Region plan

```
REGION         | PLAYER SHARE | MEDIAN RTT TO PLAYERS | ROLE                         | DATA HOMED HERE
europe-west1   |              |                       | primary core + game servers  | EU players
us-central1    |              |                       | game servers + read replicas | —
asia-northeast1|              |                       | game servers                 | —
```

### 3. SLI/SLO sheet

```
SLI                                   | MEASURE                                   | SLO (example)        | ALERT
login/bootstrap success               | 2xx / all, server-side                    | 99.9% / 30 d         | 14.4× burn over 1 h
bootstrap latency                     | p95 server time                           | < 400 ms             | p95 > 600 ms 10 min
purchase verify success               | verified / attempted (excl. store errors) | 99.95%               | any 5-min drop > 1%
time to match                         | p50 / p95 per queue                       | p95 < 60 s           | p95 > 90 s 10 min
game server allocation                | success rate, latency                     | 99.9%, p99 < 1 s     | failures > 0.5%
server tick time                      | p99 frame time vs tick budget             | p99 < 80% of budget  | > 90% 5 min
ledger txn errors                     | 5xx + deadlocks / txns                    | < 0.05%              | > 0.2% 5 min
CCU                                   | sessions with heartbeat < 60 s            | dashboard only       | drop > 20% in 5 min
```

### 4. DR plan

```
TIER        | RPO      | RTO     | MECHANISM                                    | DRILL CADENCE
ledger      | ~0 / < 1 min | 30 min | sync HA in-region + PITR + async cross-region replica | restore quarterly
profile/inv | < 1 min  | 30 min  | same DB class as ledger                      | quarterly
leaderboards| 15 min   | 15 min  | rebuild from SQL snapshot + submissions log  | per season
chat        | 1 h      | 2 h     | vendor or periodic export                    | yearly
analytics   | 24 h     | 24 h    | replay from Pub/Sub retention / raw bucket   | yearly
config      | 0        | 5 min   | Git + immutable CDN bundles                  | each release
```

## Technical Reference

### Latency budgets (heuristics)

| Game type | Target RTT | Notes |
| --- | --- | --- |
| Competitive shooter / fighting | < 50 ms ideal, < 80 ms acceptable | Valorant targets a peeker's-advantage window under ~60–80 ms with 128-tick servers (7.8125 ms frame budget) — https://technology.riotgames.com/node/112 |
| Action / MOBA / real-time PvP | < 100 ms | More regions beat bigger regions |
| Turn-based / async PvP / co-op | < 200 ms | Few regions; relay acceptable |
| Async mobile (match-3, 4X, idle) | Not latency-bound | 1–2 core regions; CDN does the rest |

### Dedicated vs relay

| | Dedicated (Agones, GameLift Servers, edge) | Relay (Photon cloud, UGS Relay) |
| --- | --- | --- |
| Authority | Server-authoritative; anti-cheat friendly | Host or shared authority |
| Cost | vCPU per match | Bandwidth per CCU, low |
| Use | Ranked PvP, economy-affecting outcomes | Co-op, casual, friends lobbies |

### Hosting facts (as of 2026-10; verify)

- **Agones v1.61.0** (Sept 24; year inferred 2026): Helm v4 (breaking), restricted-PSS sidecar, GameServers marked Unhealthy when the game container exits. v1.60 supports Kubernetes 1.34–1.36. PortRanges and PortPolicyNone are Stable. Python SDK since v1.58. https://github.com/googleforgames/agones/releases
- **Open Match 2** is in public preview (single `om-core`, gRPC + REST); Open Match 1.x latest confirmed v1.8.x. https://github.com/googleforgames/open-match2
- **Amazon GameLift Servers** managed containers GA 2024-11-13 (on ECS); Anywhere fleets; FleetIQ for Spot. https://aws.amazon.com/about-aws/whats-new/2024/11/amazon-gamelift-containers-dev-iteration-management
- **Unity Multiplay** direct support ended 2026-03-31 (Rocket Science Group licensed it); **Hathora** hosting shut down 2026-05-05. https://docs.unity.com/en-us/multiplay-hosting, https://docs.edgegap.com/docs/tools-and-integrations/switch-from-hathora
- **Edgegap** edge orchestration; per-vCPU pricing conflicts between sources — check https://edgegap.com/pricing.

### Event-spike playbook

- Pre-scale 30–60 min before a scheduled event: raise HPA `minReplicas` and FleetAutoscaler `minReplicas` via a scheduled job or config, warm DB connection pools, prewarm CDN for new bundles.
- Stagger the start: per-player jitter of 5–15 minutes on event unlock spreads the login wave.
- Keep images small and pre-pulled (DaemonSet pre-puller or image streaming) so new nodes become Ready faster.
- Cluster Autoscaler adds nodes in minutes; Agones buffer must cover `allocations_per_min × node_ready_minutes`.
- Disable non-critical batch jobs (analytics backfills, reindexing) during event windows.

### Data stores at scale

| Need | Choice | Why / watch-outs |
| --- | --- | --- |
| Ledger, inventory, profile (per-player ACID) | Postgres / MySQL (Cloud SQL, AlloyDB, Aurora), sharded by `player_id`; Vitess for MySQL at large scale | Mature tooling; plan logical shards early |
| Global strong consistency, multi-region writes | Cloud Spanner | No manual sharding; higher cost floor; design keys to avoid hotspots (no monotonic leading key) |
| Massive write-heavy, time-ordered (chat history, match logs, telemetry) | Cassandra / ScyllaDB / Bigtable | Query-first data modeling; no ad-hoc joins |
| Key-value at scale (AWS) | DynamoDB | Used by Supercell and Scopely (job-posting sources); design partition keys for even load |
| Leaderboards, sessions, rate limits, presence | Redis (Memorystore/ElastiCache) or Valkey | Not system of record; snapshot what matters to SQL. Licensing changed in 2024–2025 — verify the current Redis/Valkey license for your use |
| Events / outbox | Kafka or Pub/Sub | At-least-once; consumers idempotent |
| Analytics warehouse | BigQuery | King's data platform runs on GCP; partition by event date, cluster by player_id |

### CDN for asset bundles

- Paths are content-hashed and immutable: `Cache-Control: public, max-age=31536000, immutable`. Manifests/catalogs are versioned files referenced from config, or short TTL (≤ 60 s).
- Origin shield on; origin is object storage (GCS/S3) in one region.
- Platform-hosted alternatives remove CDN cost for some content: Apple-hosted Background Assets (up to 200 GB, updatable without a binary), Play Asset Delivery, Unity Addressables + CCD (https://developer.apple.com/documentation/backgroundassets/creating-managed-asset-packs).
- Prewarm new event bundles in top regions 1 h ahead; monitor cache hit ratio (target > 95% for bundles).
- China needs a local CDN and ICP-filed domain (as of 2026-10; verify).

### Cost per DAU

```
cost_per_DAU_month = monthly_infra_cost / avg_DAU
  infra = compute(API) + game_servers + databases + cache + CDN egress + observability + warehouse
game_server_cost_month = peak_concurrent_matches_avg × vCPU_per_server × $_per_vCPU_hr × 730 × utilization_inverse
```

Worked (replace prices with your contract rates): 40k average concurrent players in matches, 10 players per server, 1 vCPU each → 4,000 vCPU; at an example $0.04/vCPU-hr and 70% fleet utilization: 4,000 × 0.04 × 730 / 0.7 = **$167k/month**. At 1.5M DAU that is ~$0.11 per DAU-month for game servers alone. Levers in order of yield: pack more matches per vCPU (server frame time), raise fleet utilization (Packed scheduling, smaller buffer outside peaks), Spot/preemptible for buffer capacity only, regional right-sizing, observability log volume (often the surprise line item).

Async mobile games have no game-server line; their cost is dominated by databases, CDN egress and observability. Track the ratio, not the absolute: cost growth must stay ≤ DAU growth.

Read `references/observability-and-dr.md` for the metrics/logs/traces stack, Agones metrics, restore drills and multi-region topology.

## Diagnostics

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Allocation failures at event start | Fleet buffer smaller than allocation burst × node lead time | Pre-scale minReplicas; raise buffer; pre-pull images |
| Matches dropped during deploy | Rolling update deleting Allocated servers, or node drain without graceful shutdown | Agones only replaces Ready servers; set PDBs and `terminationGracePeriodSeconds` > max match length on game server nodes; avoid node auto-upgrade during peaks |
| Spot preemptions kill matches | Allocated servers on Spot nodes | Spot only for buffer; taint so allocated servers stay on on-demand, or use GameLift FleetIQ |
| Rubber-banding in one region | Server tick overrun (CPU throttling from limits) | Guaranteed QoS (requests = limits), CPU pinning on dedicated nodes, track tick p99 |
| DB CPU at 100% at event start | Thundering herd on bootstrap | Stagger, cache config at CDN, bootstrap batching, connection pooling (PgBouncer) |
| Bill up 40%, DAU flat | Log volume, idle buffer, cross-region egress | Sample logs, cap cardinality, scale buffer by schedule, keep traffic regional |
| Restore took 9 hours in an incident | Never drilled; PITR not enabled on all shards | Quarterly restore drill per shard class; automate |
| Terraform drift / two engineers clobber state | Local state, no locking | Remote backend (GCS/S3) with locking; plan in CI, apply from CI |

## Anti-Patterns

**The Average-Day Cluster** — capacity sized to the daily mean. Events are synchronized logins.

**The Vendor-Native Game Server** — server binary bound to one host's SDK with no Agones path. Multiplay and Hathora customers in 2026 learned the cost.

**The Redis Ledger** — balances in Redis "because it is fast". Cache eviction or failover becomes a currency reset.

**The Untested Backup** — backups that have never been restored are a hypothesis.

**The CPU Alert** — paging on node CPU instead of player-facing SLIs. Players feel login failures, not CPU.

**The Click-Ops Region** — the second region built by hand. It will differ from the first in exactly the setting that matters during failover.

**The Global Active-Active Ledger** — multi-master writes for player economy without a database designed for it. Home each player to a region; replicate asynchronously; fail over deliberately.

## Quality Checklist

- [ ] Capacity sheet sized for event-start peak with measured per-unit capacity
- [ ] Game server images run under Agones SDK even if hosted elsewhere
- [ ] Fleet buffer ≥ allocation rate × node lead time; pre-scale job for scheduled events
- [ ] Allocated game servers never on preemptible nodes; graceful shutdown ≥ max match length
- [ ] Regions chosen from player distribution and RTT budget; ping beacons in matchmaking
- [ ] Ledger on relational HA with PITR; RPO/RTO written per tier
- [ ] Restore drill executed in the last quarter, with measured RTO
- [ ] CDN: immutable hashed bundle paths, short-TTL manifests, prewarm step in event runbook
- [ ] SLIs are player-facing (login, purchase, match, allocation, tick) with burn-rate alerts
- [ ] Terraform remote state with locking; CI plans and applies; no manual resources
- [ ] Cost per DAU tracked monthly with a breakdown; growth ≤ DAU growth
- [ ] Hosting vendor facts in docs dated and re-verified (2026 changes)

## Related Skills

- `gamedev-platform-server-architect` — provides the capacity model, consistency and residency rules this skill implements.
- `gamedev-backend-engineer` — consumes databases, Redis and queues; agree connection limits and migration process.
- `gamedev-netcode-engineer` — tick rate, players per server and bandwidth per player drive game-server sizing.
- `gamedev-live-serving` — SLO ownership, incident response, event-day war room on top of this stack.
- `gamedev-delivery-release` — CI/CD for server builds and fleet rollouts.
- `gamedev-anti-cheat-security` — network hardening, DDoS posture, secrets management review.
- `gamedev-analytics-engineer` — BigQuery/warehouse cost and retention policies.
- `gamedev-financial-growth-strategist` — cost per DAU as an input to unit economics.
