# Observability, Backups, DR, and Multi-Region

Read when setting up the metrics/logs/traces stack, writing alerts, planning restore drills, or designing a second region.

## Stack

| Signal | Default | Notes |
| --- | --- | --- |
| Metrics | Prometheus (or Google Managed Prometheus) + Grafana | Postings at Dream Games and others list Prometheus/Grafana, ELK, New Relic |
| Logs | Structured JSON -> Cloud Logging / ELK / Loki | Sample INFO at volume; never log tokens, receipts, emails |
| Traces | OpenTelemetry SDK -> Cloud Trace / Tempo / Jaeger | Trace bootstrap, purchase verify, matchmaking -> allocation end to end |
| Client signals | Crash reporting (Crashlytics, Sentry), client-side latency events into analytics | Server SLIs miss DNS/TLS/mobile network failures |

Cardinality rules: no `player_id`, `match_id` or raw URL as a metric label. Put those in logs/traces and link by trace ID.

## Game-specific metrics to export

```
# Backend
game_bootstrap_requests_total{result}
game_bootstrap_duration_seconds_bucket
purchase_verify_total{store, result}          # result: granted | replay | invalid | store_error
ledger_txn_total{kind, result}
ledger_txn_duration_seconds_bucket{kind}
matchmaking_time_to_match_seconds_bucket{queue, region}
ccu{platform, region}                         # from heartbeats, gauge

# Game server (from the server process)
server_tick_duration_seconds_bucket{mode}     # compare to tick budget, e.g. 128 Hz = 7.8125 ms
server_players{mode}
server_match_end_total{reason}                # normal | crash | timeout | all_left

# Agones (exported by the controller; verify names for your version)
agones_gameservers_count{fleet_name, type}    # type = Ready | Allocated | ...
agones_fleets_replicas_count{name, type}
agones_gameserver_allocations_duration_seconds_bucket{status}
```

## Alerting

- Page on SLO burn rate: fast burn (2% of 30-day budget in 1 h, i.e., 14.4× rate) and slow burn (5% in 6 h, 6×). Ticket on slower burns.
- Page on purchase verify failure spikes immediately — it is revenue and store standing.
- Page on Ready game servers < 25% of buffer target in any region during peak hours.
- Do not page on CPU, memory or pod restarts alone; route those to dashboards and tickets.

## Backups and restore drills

| Store | Backup | Restore drill |
| --- | --- | --- |
| Relational (ledger, profile, inventory) | Automated daily + PITR (WAL/binlog) 7+ days; monthly snapshot copied to another region and project | Quarterly: restore one shard to a scratch instance at a chosen timestamp, run ledger audit queries, record RTO |
| Spanner | Scheduled backups + PITR window | Quarterly |
| Redis leaderboards | Not backed up as primary; season snapshots in SQL; submissions log in Kafka/Pub/Sub retention | Each season: rebuild a board from snapshot + log in staging |
| Object storage (bundles, config) | Versioning on; retention lock on release buckets | Per release: CDN origin failover test |
| Terraform state | Bucket versioning | Yearly |

A backup is complete only when the restore of it has been timed. Put the measured RTO in the DR plan.

## Multi-region topology

- **Async mobile:** one primary core region (APIs + DBs) + CDN globally; optional read replicas near large markets; warm standby region with replicated DBs and Terraform-ready but scaled-down compute. Failover is a deliberate, practiced runbook (promote replicas, flip DNS/global load balancer, raise compute), not automatic.
- **Session PvP:** core region(s) for backend + game-server clusters in N regions close to players. Game-server regions are stateless; losing one means matchmaking stops offering it.
- **Player homing:** each player's stateful data lives in one home region (chosen at account creation from geography/residency). Cross-region writes go through the home region. Moving a player's home is a migration job, not a request-time routing trick.
- **Global strong consistency** only where the domain needs it (global inventory trades, global leaderboards with payouts) — consider Spanner for those tables rather than making every table multi-region.

## Region evacuation runbook (outline)

1. Declare incident; freeze deploys and LiveOps config changes.
2. Stop matchmaking into the affected region (config flag); let running matches finish if the region is degraded rather than down.
3. For core-region loss: promote cross-region replicas; verify ledger replication lag at promotion time and record the RPO actually achieved.
4. Flip global load balancer / DNS to the standby; scale standby compute to the capacity sheet's daily peak.
5. Open the store only after ledger audit queries pass on the promoted primary.
6. Post-incident: compensation mail via campaign (not direct writes), RCA with prevention automation.
