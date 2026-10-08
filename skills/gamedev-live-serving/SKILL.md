---
name: gamedev-live-serving
description: >-
  Live-service runtime operations for games: SLIs and SLOs (login success,
  matchmaking time, purchase success, crash-free sessions), incident response
  and severity, launch-day and event-day capacity planning and load tests,
  content hot update via CDN with versioned asset bundles, remote config
  rollouts with kill switches, maintenance windows, player comms and status
  pages, post-incident reviews, and economy incidents such as dupes and
  exploits with rollback or compensation. Use when the game is down or
  degraded, planning a launch or big event, shipping content without a
  client build, rolling out a risky config, or handling a currency exploit.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: meta
---

# Game Live Serving

A live game is a service that happens to have a client. Players experience it as a handful of moments that must work every time (log in, find a match, buy something, get the reward, download today's event), and they experience failure in synchronized waves, because events start for everyone at the same second and a currency exploit spreads through a Discord in an hour. Live serving is the discipline of keeping those moments inside measured objectives, absorbing synchronized load you scheduled yourself, changing the game safely without a store release, and recovering trust when something breaks. The two tools that matter most are the ones decided before the incident: a kill switch for every risky feature, and a written policy for what you do when the economy is corrupted.

**Interpretation note.** "Serving" here means live-service runtime operations plus content serving (CDN, asset bundles, remote config). The build-and-release pipeline, store submission and rollout percentages belong to gamedev-delivery-release.

## Role Profile

The function is spread across SRE/DevOps, platform engineers, backend on-call and LiveOps engineers. Dream Games' senior DevOps role covers infra, "RCA plus automation to prevent recurrence", Kubernetes, Terraform, MySQL, Redis and Kafka, with New Relic, ELK, Prometheus and Grafana (https://www.dreamgames.com/jobs/senior-devops-engineer [proxy]). Supercell's central server engineers provide "first-line support for production" on rotating on-call (https://jobs.accel.com/companies/space-ape-games-2/jobs/66661349-senior-server-engineer-central-tech [proxy]). LiveOps configuration engineers "configure and schedule in-game events, offers, and promotions" and validate configs with QA before and after launch (https://builtin.com/job/senior-configuration-engineer-valid-us-visa-mandate/6738922 [proxy]).

- **KPIs [inferred]:** availability/SLO and MTTR; incident count; cloud cost per DAU; config error rate; on-time event launches.
- **Tools:** Kubernetes, Terraform, Prometheus/Grafana, ELK/New Relic, Redis, Kafka, CDN, remote config and feature-flag services, crash reporting.
- **Collaborators:** backend, infrastructure, LiveOps designers, community/support, QA, release.

## When to Use / Not

Use for SLOs, alerting, incident response, capacity and load plans, event-day operations, CDN content updates, config rollouts, kill switches, maintenance and player comms, post-incident reviews and economy incidents.

Not for: designing services and data models (gamedev-platform-server-architect); writing the grant, receipt or inventory code (gamedev-backend-engineer); clusters, fleets, regions and IaC (gamedev-infrastructure-engineer); event design (gamedev-liveops-designer); binary rollout and hotfix builds (gamedev-delivery-release); cheat detection and bans (gamedev-anti-cheat-security).

## Inputs to Gather

- **Architecture map:** services, regions, data stores, third parties (auth, payments, ads, CDN, config). Default: assume every third party can fail.
- **Traffic profile:** DAU, peak concurrent users (PCU), peak-hour share, requests per player per minute, event start times.
- **Current SLIs** and dashboards; on-call rotation.
- **Live-ops calendar** for the next 6 weeks (events, maintenance, launches, marketing beats).
- **Content delivery path:** Addressables, Apple-hosted Background Assets, Play Asset Delivery, or custom CDN.
- **Economy ledger access:** can you query every grant by source and time?
- **Compensation policy** if one exists. Default: none exists; write one before you need it.

## Method

1. **Define the critical player journeys** and one SLI per journey, measured as close to the player as possible (client-reported success beats server 200s).
2. **Set SLOs and error budgets** per journey; alert on burn rate, not raw thresholds.
3. **Write the incident process** (severity, roles, comms cadence) and drill it before launch.
4. **Plan capacity from the calendar.** For every launch and event start, estimate peak load, load test to a multiple, pre-scale, and plan graceful degradation.
5. **Make content immutable and versioned** on the CDN; ship content by publishing a new catalog, never by overwriting files.
6. **Roll out config like code:** schema-validated, versioned, staged, with automatic guardrail checks and one-click revert.
7. **Put a kill switch on every risky feature** (new event type, new offer, new matchmaking rule, anything touching currency) and test that it works on the oldest supported client.
8. **Prepare player comms templates** and a status page before you need them.
9. **Run post-incident reviews** for every SEV1 and SEV2 within 5 working days; track actions to done.
10. **Write the economy incident policy** (detection, containment, rollback vs compensation) and agree it with design, finance and community leads.

## Deliverables

SLO sheet, capacity plan per launch/event, incident runbook and comms templates (references/runbooks.md), content and config rollout plan (references/content-and-config.md), economy incident policy, post-incident reviews.

```
CAPACITY PLAN: Season 12 reset     DATE: 2026-10-24 10:00 UTC     OWNER: ______
FORECAST: DAU 1.2M, peak-hour share 12%, avg session 18 min, 40 req/player/min
PEAK: PCU ≈ 1.2M × 0.12 × 0.30 = 43k; steady RPS ≈ 43k × 40 / 60 = 29k
BURST: 60% of online players claim in first minute ≈ 26k claims/min ≈ 430/s on claim endpoint
LOAD TEST TARGET: 2.5× = 72k RPS steady, 1.1k/s claims; date of test, result
MITIGATIONS: reward jitter 10 min; pre-scale 45 min before; leaderboards degrade first
KILL SWITCHES: season.rewards.enabled, leaderboard.enabled
ON-CALL: names; IC; comms lead; status page ready
```

## SLIs and SLOs

Targets are [heuristic] starting points; set yours from measured baselines and genre.

| Journey | SLI (good events / valid events) | Starting SLO | Notes |
|---|---|---|---|
| Login | Sessions reaching main menu / session start attempts | 99.9% over 28 days | Measure client-side; include auth provider failures |
| Matchmaking | Matches found within target time / queue entries | 95% within 30 s (casual), 60–120 s (ranked high MMR) | Track p50/p95 time-to-match per bracket |
| Purchase | Store-confirmed purchases granted within 60 s / store-confirmed purchases | 99.5% | Store-side failures excluded; grant failures included |
| Reward claim | Successful claims / claim attempts | 99.9% | Event-end spikes are the test |
| Content download | Bundles downloaded and verified / requested | 99.5%, p95 under budget | Per region and per network type |
| API latency | Requests under threshold / requests | 99% under 300 ms (p99 tracked) | Per endpoint class |
| Crash-free sessions | Sessions without crash / sessions | 99.5%+ on the current version [heuristic] | From the crash reporter; compare versions |
| Config fetch | Clients on intended config version within 10 min / active clients | 99% | Validates kill-switch propagation |

**Error budget:** 99.9% over 28 days is about 40 minutes of failed logins. Alert when the budget burns fast (for example, 2% of the 28-day budget in 1 hour) and slow (10% in 3 days) [heuristic, multiwindow burn-rate pattern].

## Incident Response

| Severity | Definition | Response |
|---|---|---|
| SEV1 | Game unplayable for many players, purchases failing, data loss, or active economy exploit | Page on-call now; incident commander; comms within 15 min; status page; updates every 30 min |
| SEV2 | Major feature or region broken; significant degradation | Page on-call; comms within 30 min; updates hourly |
| SEV3 | Minor feature degraded, workaround exists | Working hours; ticket; note in community channels if visible |
| SEV4 | Cosmetic or internal-only | Backlog |

Roles: **incident commander** (decides, does not debug), **ops lead** (debugs and mitigates), **comms lead** (player and internal updates), **scribe** (timeline). Mitigate first, root-cause later: roll back the server deploy, revert config, flip the kill switch, shed load, enable maintenance mode. Full runbook, comms templates and PIR template: references/runbooks.md (read during an incident, before a maintenance window, and when writing a post-incident review).

## Capacity Planning: Launch Day and Event Day

```
Peak concurrent users (PCU)  ≈ DAU × peak_hour_share × (avg_session_min / 60)
Peak requests/s              ≈ PCU × requests_per_player_per_min / 60
Event-start burst            ≈ eligible_players_online × logins_or_claims_in_first_minute / 60
Load test target             = max(steady peak, burst) × safety multiple
```

| Situation | Safety multiple [heuristic] | Why |
|---|---|---|
| Global launch | 3–5× forecast peak | Forecasts miss featuring and virality; launch traffic is front-loaded |
| Major event start / season reset | 2–3× last comparable event | Synchronized login and claim spikes |
| Routine weekly event | 1.5–2× | Known pattern |

Mitigations for synchronized spikes: jitter event start or reward delivery per player (spread over 5–15 minutes); login queue with honest ETA; pre-scale fleets and database read replicas 30–60 minutes before; rate limit per player; cache static event definitions on the CDN; degrade gracefully (disable leaderboards, friend lists and cosmetics before core play). Load test with realistic player scripts (login, sync, play, claim), not single-endpoint floods, and include third parties (auth, payments) in a sandbox or mock with their limits.

## Content Hot Update via CDN

- **Immutable, content-addressed bundles.** File name or path includes a content hash; `Cache-Control: public, max-age=31536000, immutable`. Never overwrite a URL.
- **Small mutable pointer.** A versioned catalog or manifest (short TTL, for example 60 s, or signed and versioned in the URL) tells clients which bundles to load. Publishing content = publishing a new catalog.
- **Compatibility key.** Each catalog declares the minimum client build it supports; old clients keep the last compatible catalog.
- **Rollback** = republish the previous catalog version; bundles are still cached.
- **Unity Addressables 2.x:** the remote catalog must be enabled in the shipped player or content updates cannot be detected; "Update a previous build" produces delta bundles; `UpdateCatalogs` blocks other Addressables requests while it runs, so call it before gameplay loads (as of 2026-10; verify).
- **Apple-hosted Background Assets:** up to 200 GB of asset packs hosted by Apple, updatable without a new binary; replaces On-Demand Resources. **Play Asset Delivery:** fast-follow and on-demand packs; query their location every time because the OS may move or delete them (as of 2026-10; verify).
- **Executable code hot-update** (Lua, JS, HybridCLR) must stay within Apple guidelines 2.5.2 and 4.7.

Details, headers and catalog schema: references/content-and-config.md (read when designing the content pipeline or a config rollout).

## Remote Config and Kill Switches

- Ship config as **signed, versioned JSON with a bundled fallback**. Never block boot on config fetch.
- **Validate** against a schema before publish; reject unknown keys for the target client version.
- **Stage** risky changes: internal, 1%, 10%, 50%, 100%, with guardrail metrics checked between steps (crash-free, login, purchase success, the feature's own metric).
- **Kill switch** = a boolean (or percentage) the client checks before entering a feature, with a defined degraded state. Test it on the oldest supported client.
- Vendors: Firebase Remote Config (real-time updates via `addOnConfigUpdateListener`), LaunchDarkly, Unity Remote Config, PlayFab Title Data, Satori. Statsig was acquired by OpenAI (announced Sept 2, 2025) and operates independently; weigh vendor-continuity risk (as of 2026-10; verify). Keep a provider-agnostic config layer; hosting and service vendors do shut down (Hathora game hosting shut down May 5, 2026).

```csharp
// Client kill-switch check with safe default (Unity C#)
public static class Features
{
    public static bool GuildWarEnabled =>
        RemoteConfig.GetBool("feature.guild_war.enabled", defaultValue: false);
}

void OnGuildWarButton()
{
    if (!Features.GuildWarEnabled) { ShowUnavailable("Guild Wars return soon."); return; }
    OpenGuildWar();
}
```

## Maintenance Windows and Player Comms

- Schedule at the lowest-traffic hour across your top revenue regions; announce 24–72 h ahead in-game and on social; never during an event's final hours.
- In-game: maintenance banner before, blocking screen with ETA during, and a server-driven message so old clients can show it.
- Compensation for planned maintenance over the announced time, and for SEV1/SEV2 outages, follows a published scale (references/runbooks.md).
- Status page with components that match player journeys (login, store, matchmaking, events), not internal service names.

## Economy Incidents: Dupes and Exploits

1. **Detect:** alerts on currency grant velocity per source, balance percentile jumps (p99/p50 ratio), purchases-to-grants mismatch, and the same idempotency key granted twice.
2. **Contain within minutes:** kill switch on the feature or endpoint, disable the offending reward source, rate limit; do not announce exploit details.
3. **Assess from the ledger:** who received what, from which source, between which timestamps; separate exploiters (repeat, scripted) from incidental beneficiaries (single, accidental).

```sql
-- Players with more than one grant for the same reward key (duplicate grants)
SELECT player_id, reward_key, COUNT(*) AS grants, SUM(amount) AS total
FROM currency_ledger
WHERE source = 'guild_war_reward'
  AND created_at BETWEEN :incident_start AND :incident_end
GROUP BY player_id, reward_key
HAVING COUNT(*) > 1
ORDER BY total DESC;
```

4. **Decide remedy** with the matrix below, agreed with design, finance, community and legal.
5. **Execute** with ledger entries (never silent balance edits), in-game notice, and support macros.
6. **Fix and verify** the root cause before re-enabling; gamedev-qa-verifier confirms with evidence.

| Situation | Remedy [policy guidance] |
|---|---|
| Incidental beneficiaries, small amounts | Let them keep it; fix forward. Clawback costs more trust than the currency is worth |
| Incidental, large amounts that distort the economy | Remove the excess with a clear notice; never push balances negative without explanation |
| Deliberate exploiters | Remove gains, plus sanctions per policy (route to gamedev-anti-cheat-security) |
| Players lost currency/items due to the bug | Restore from ledger plus a modest apology grant |
| Server-wide rollback | Last resort only: when corruption is widespread and recent (hours); it erases legitimate purchases and progress, which must then be restored |

Economy-level impact (inflation, sink capacity after the incident): if installed, game-economy-balancer.

## Quantitative Reference

| Item | Value |
|---|---|
| 99.9% over 28 days | ~40 min of allowed failure |
| 99.5% over 28 days | ~3.4 h |
| Post-incident review | within 5 working days for SEV1/SEV2 [heuristic] |
| Launch load test | 3–5× forecast peak [heuristic] |
| Event start jitter | 5–15 min spread [heuristic] |
| Catalog TTL | about 60 s or versioned URL; bundles immutable for 1 year |
| Apple-hosted Background Assets | up to 200 GB per app (as of 2026-10; verify) |
| Play Asset Delivery | asset pack 1.5 GB each; on-demand + fast-follow total 4 GB (30 GB for Level Up / XR) (as of 2026-10; verify) |
| Android vitals bad behavior | 1.09% crash, 0.47% ANR (2022 thresholds, possibly outdated) |

## Diagnostics

| Symptom | Likely cause | Fix |
|---|---|---|
| Login failures at every event start | Synchronized spike; cold caches | Jitter starts, pre-scale, login queue |
| Mixed old/new assets in client | URLs overwritten in place | Content-hashed immutable bundles; versioned catalog |
| Kill switch did not stop the feature | Old clients ignore the key or cache config | Test switch on N-2; shorten config TTL; server-side guard too |
| Purchases charged but not granted | Grant service degraded; no retry from client transaction queue | Alert on purchase SLI; idempotent retry; reconcile from store notifications |
| Alert fatigue | Threshold alerts on noisy metrics | Burn-rate alerts on SLOs only |
| Same incident recurs | PIR actions not tracked | Owner and due date per action; review weekly |
| Currency p99 jumps overnight | Exploit or duplicated grant | Economy incident procedure; ledger query |
| Event content missing for some regions | CDN propagation or regional purge failure | Verify per-region; publish catalog only after bundles are confirmed live |

## Anti-Patterns

**Server-200 SLIs** — measuring success at the load balancer while clients fail on auth or timeouts.

**Midnight UTC Thundering Herd** — every event starts at the same second for every player.

**Overwrite and Purge** — replacing CDN files in place and hoping the purge reaches every edge.

**Config Without Schema** — a typo in a JSON key disables the store for everyone.

**Silent Clawback** — removing currency without explanation; support queues and reviews explode.

**The Heroic Rollback** — rolling back the whole server for a small exploit, erasing legitimate purchases.

**Blame PIR** — reviews that name people instead of fixing process; next time, nobody reports early.

## Quality Checklist

- [ ] One SLI per critical journey, measured near the player; SLOs and error budgets set
- [ ] Burn-rate alerts; on-call rotation and escalation documented
- [ ] Incident severity, roles and comms cadence written and drilled
- [ ] Capacity plan for every launch and major event, load tested to the stated multiple
- [ ] Event starts and reward deliveries jittered; login queue ready
- [ ] CDN bundles immutable and content-addressed; catalogs versioned; rollback tested
- [ ] Config schema-validated, versioned, staged with guardrails, one-click revert
- [ ] Kill switches on all risky features, tested on the oldest supported client
- [ ] Maintenance and outage comms templates and status page ready
- [ ] Economy incident policy agreed; ledger queryable by source and time
- [ ] PIRs within 5 working days with owned, dated actions

## Related Skills

gamedev-delivery-release ships binaries, sets rollout percentages and runs hotfix builds. gamedev-infrastructure-engineer owns fleets, regions, autoscaling and CDN configuration; gamedev-platform-server-architect owns service design; gamedev-backend-engineer implements idempotent grants and config endpoints. gamedev-liveops-designer owns what events run and when; gamedev-anti-cheat-security handles exploiters and bans; gamedev-analytics-engineer builds the anomaly dashboards; gamedev-qa-verifier verifies fixes; game-economy-balancer (if installed) assesses economy-wide impact after an incident.
