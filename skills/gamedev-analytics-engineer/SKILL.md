---
name: gamedev-analytics-engineer
description: >-
  Build the data layer a game studio decides with: event taxonomy and naming,
  schema versioning, precise SQL definitions of DAU, retention, ARPDAU,
  conversion and LTV, the pipeline from client SDK to collector to warehouse
  (BigQuery, dbt, Airflow), A/B testing infrastructure and statistics (assignment,
  sample size, CUPED, sequential pitfalls, guardrails), dashboards, attribution
  joins with SKAN and AdAttributionKit, and consent-aware privacy. Use when
  writing a tracking plan, when two dashboards disagree on DAU or retention,
  when setting up experiments, when building dbt models or KPI SQL, or when
  wiring MMP and SKAN data into the warehouse.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: growth-business
---

# Analytics Engineer

Every number a studio argues about is a definition someone wrote down, or failed to. "Retention" without a denominator, a timezone and a day-boundary rule is not a metric; it is a meeting. The analytics engineer's job is to make the definition, the event that feeds it and the test that reads it unambiguous, versioned and cheap to trust. Design events from the questions the studio must answer, not from the screens the client happens to have. Treat revenue from the client as a hint and revenue from the server-validated receipt as the truth. Assign experiments on the server, size them before launch, check the split before the result, and read them once. A pipeline that is late, silently wrong or impossible to delete from is worse than no pipeline, because people will still decide with it.

## Role Profile

At a top-grossing studio this is the data or analytics engineer on a central data platform, serving game teams, analysts and data scientists.

- **Responsibilities.** King's Core Data Models team builds, maintains and optimizes "pipelines and models using SQL, Python and Airflow", plus Looker models and modeling standards; its Data Foundations platform runs at more than 65 PB and 130B+ events per day (https://hitmarker.net/jobs/king-data-engineer---core-data-models-reporting-1558921 ; https://hitmarker.net/jobs/king-data-platform-engineer-1700110).
- **Hard skills.** "Excellent SQL and query optimisation", solid Python, GCP/BigQuery or equivalent, data modeling, turning business needs into data products; Spark/Flink at senior level.
- **Tools.** BigQuery, Airflow, dbt, Looker/Tableau, Terraform, Kafka/Pub/Sub, Spark/Flink. Product-analytics stacks such as ThinkingData are used directly by game teams — Century Games reports over 60% of staff on it (https://naavik.co/digest/century-games-4x-portfolio-strategy/).
- **KPIs.** Freshness SLA of daily KPIs, pipeline reliability and cost, adoption of models and dashboards, experiment-platform correctness.
- **Context.** A/B testing is the most common cross-discipline skill in top-studio postings (level design, economy, PM, LiveOps); every one of those roles consumes this skill's output. Collaborators: analysts, data scientists, PMs, client and backend engineers, UA/marketing science, legal/privacy.

## When to Use / Not

Use for: tracking plans and event schemas, KPI SQL and dbt models, pipeline architecture, experiment assignment and statistics, dashboards, attribution data ingestion and joins, consent and deletion pipelines, data-quality monitoring.

Not for: interpreting a retention curve or playtest data (if installed, `game-playtest-analyst`); deciding retention levers (`gamedev-growth-designer`); LTV/ROAS business models and UA allocation (`gamedev-financial-growth-strategist`); backend services and receipt validation code (`gamedev-backend-engineer`); cluster and warehouse infrastructure operations (`gamedev-infrastructure-engineer`).

## Inputs to Gather

- **Decisions and KPIs** the studio needs (retention by cohort, monetization, event performance, experiments). Missing: start from the standard KPI set below.
- **Client stack:** engine, existing SDKs (GA4/Firebase, Amplitude, ThinkingData, MMP), offline behavior.
- **Volume:** DAU and expected events per DAU per day. Missing: assume 100–300 events/DAU/day for casual, more for mid-core.
- **Warehouse and orchestration** in place, or greenfield. Missing: default to BigQuery + dbt + Airflow, the most common stack in the research.
- **Identity:** account ID vs device ID, cross-device linking, guest accounts.
- **Markets and consent:** GDPR/UK GDPR, CCPA/CPRA, COPPA (under-13), ATT status; the consent UI that exists.
- **Experiment platform:** in-house, Firebase A/B, PlayFab, Unity, LaunchDarkly, Statsig, Satori — and where assignment happens.
- **Business clock:** reporting timezone (UTC unless the business says otherwise) and day boundary.

## Method

1. **Write the question list first.** Each question names the KPI, the cut (platform, geo, cohort, segment) and the decision it feeds. Events exist to answer these; anything else is optional.
2. **Define the taxonomy.** `object_action` in snake_case with past-tense verbs (`level_completed`, `purchase_validated`), a shared envelope on every event, and typed properties. Fewer, well-parameterized events beat many bespoke ones.
3. **Version the schema.** Register each event in a schema registry (JSON Schema or protobuf) with `event_version`. Changes are additive; renames and type changes create a new version; deprecated events have a removal date. The collector rejects or quarantines events that fail validation instead of letting them land silently.
4. **Make the client SDK boring.** Batch, persist offline, retry with backoff, attach `event_id` (UUID) for dedupe, `client_ts` plus a monotonic `seq` per session, and let the server stamp `server_ts`. Never sample economy or revenue events.
5. **Make revenue server-sourced.** Purchases come from server-validated transactions (App Store Server API / Play Developer API), refunds from store notifications, ad revenue from mediation impression-level revenue. Client purchase events are for funnels only.
6. **Build the pipeline in layers.** Collector → stream → raw (append-only, partitioned by ingestion date) → staging (dedupe, typing, late data) → core facts and dimensions → KPI marts → BI. Orchestrate with Airflow; transform with dbt; test every model.
7. **Write KPI definitions as SQL with stated denominators,** in one place (dbt models or a semantic layer), and make every dashboard read from them. Two dashboards computing DAU separately will disagree within a month.
8. **Build experiments on deterministic server-side assignment** with exposure logging, layered mutual exclusion, persistent holdouts, an SRM check, pre-registered primary and guardrail metrics, and a fixed sample size or a valid sequential method.
9. **Ingest attribution at the right grain.** MMP user-level data for consented and Android users joins on your user ID; SKAN/AAK postbacks are aggregated and join at campaign × date only; network cost joins at campaign × date × geo.
10. **Wire consent and deletion end to end.** Consent state travels in the envelope, gates SDK initialization and ad personalization, and a deletion request propagates to every table and vendor within the legal window.
11. **Monitor data quality** — volume anomalies, schema failures, null rates, duplicate rates, freshness — and page someone when the daily KPI table is late.

## Deliverables

### 1. Event Spec (tracking plan entry)

```yaml
event: level_completed
version: 3
owner: puzzle-team
question: "Where do players fail and quit in levels 1-200?"   # the decision it feeds
trigger: "Client, when the end-of-level result screen is shown (win or lose)"
properties:
  level_id:        {type: integer, required: true}
  result:          {type: string, enum: [win, lose, quit], required: true}
  moves_left:      {type: integer, required: false}
  boosters_used:   {type: array, items: string}
  attempt_number:  {type: integer, required: true}
  duration_ms:     {type: integer, required: true}
pii: none
sampling: none
added: 2026-10-01
deprecates: level_end (v2), remove after 2026-12-31
```

### 2. Event Envelope (every event)

```
event_id (UUID) │ event_name │ event_version │ user_id (account) │ install_id │ session_id │ seq
client_ts (UTC) │ server_ts (UTC) │ app_version │ build │ platform │ os_version │ device_model
country (from IP at collector, then IP dropped) │ consent_analytics │ consent_ads │ att_status
experiment_assignments (array of {exp_id, variant}) │ payer_tier │ level │ is_test_device
```

### 3. Warehouse Layout (dbt)

```
raw.events_*               append-only, partitioned by ingestion date, never edited
stg_events                 deduped on event_id, typed, late-arrival window 3 days
fct_sessions               one row per session (start, end, length, events)
fct_purchases              server-validated transactions, refunds as negative rows
fct_ad_impressions         impression-level ad revenue from mediation
dim_users                  install date, first-seen attributes, latest consent, payer flags
agg_user_day               one row per user per active day (the base of DAU, retention, ARPDAU)
mart_kpi_daily             DAU, new users, revenue, ARPDAU, payer % by date × platform × country
mart_cohort_retention      cohort_date × day_n × cut
mart_experiment_*          per-experiment exposure, metrics, CUPED covariates
```

### 4. KPI Dictionary Entry

```
KPI:          D7 retention (classic)
DEFINITION:   users with ≥1 session on install_date + 7 ÷ users installed on install_date
DENOMINATOR:  new installs (first_open with is_first_launch = true), excluding test devices
DAY BOUNDARY: UTC calendar day   TIMEZONE: UTC
MATURITY:     reportable only when install_date + 7 is complete (+ late-arrival window)
SOURCE:       mart_cohort_retention   OWNER: data platform   SQL: link
NOT THE SAME AS: rolling D7 (active on day 7 or later), which reads higher
```

### 5. Experiment Design Doc

```
EXPERIMENT ID / NAME:  ____         LAYER: ____ (mutually exclusive with ____)
HYPOTHESIS:            ____
UNIT:                  user_id (or guild_id / server_id if players interact)
POPULATION:            new installs from ____ / all DAU with ____
SPLIT:                 50/50 (holdout layer __% excluded)
PRIMARY METRIC:        ____  (one)        MDE: ____   BASELINE: ____  σ: ____
n PER ARM:             ____   DAYS TO FILL: ____   + MATURITY: ____
GUARDRAILS:            crash rate, D1/D7, refund rate, payment errors, session length, ad revenue
ANALYSIS:              fixed horizon / sequential (method: ____)   CUPED covariate: ____
SRM CHECK:             chi-square, alarm at p < 0.001
DECISION RULE:         ship if ____; stop if guardrail ____ degrades by ____
```

## Technical Reference

### Core KPI SQL (BigQuery)

`agg_user_day` has one row per `user_id` per `activity_date` (UTC). `dim_users` holds `install_date`.

```sql
-- DAU, new users, ARPDAU (net revenue from server-validated purchases + ad impressions)
SELECT
  d.activity_date,
  COUNT(DISTINCT d.user_id)                                         AS dau,
  COUNT(DISTINCT IF(u.install_date = d.activity_date, d.user_id, NULL)) AS new_users,
  SUM(d.iap_net_usd + d.ad_rev_usd)                                 AS net_revenue,
  SAFE_DIVIDE(SUM(d.iap_net_usd + d.ad_rev_usd), COUNT(DISTINCT d.user_id)) AS arpdau,
  SAFE_DIVIDE(COUNT(DISTINCT IF(d.iap_net_usd > 0, d.user_id, NULL)),
              COUNT(DISTINCT d.user_id))                            AS daily_payer_pct
FROM analytics.agg_user_day d
JOIN analytics.dim_users u USING (user_id)
WHERE NOT u.is_test_device
GROUP BY 1;
```

```sql
-- Classic Dn retention by install cohort (only mature cells)
WITH cohort AS (
  SELECT user_id, install_date FROM analytics.dim_users WHERE NOT is_test_device
)
SELECT
  c.install_date,
  n AS day_n,
  COUNT(DISTINCT c.user_id) AS cohort_size,
  SAFE_DIVIDE(COUNT(DISTINCT a.user_id), COUNT(DISTINCT c.user_id)) AS retention
FROM cohort c
CROSS JOIN UNNEST([1, 3, 7, 14, 30, 60, 90]) AS n
LEFT JOIN analytics.agg_user_day a
  ON a.user_id = c.user_id
 AND a.activity_date = DATE_ADD(c.install_date, INTERVAL n DAY)
WHERE DATE_ADD(c.install_date, INTERVAL n DAY) < CURRENT_DATE() - 3   -- late-arrival window
GROUP BY 1, 2;
```

```sql
-- Cumulative net LTV per install by cohort age (includes non-payers in denominator)
SELECT
  u.install_date,
  DATE_DIFF(a.activity_date, u.install_date, DAY) AS cohort_day,
  SUM(a.iap_net_usd + a.ad_rev_usd) AS revenue
FROM analytics.dim_users u
JOIN analytics.agg_user_day a USING (user_id)
GROUP BY 1, 2;
-- then: SUM(revenue) OVER (PARTITION BY install_date ORDER BY cohort_day) / cohort_size
```

```sql
-- Payer conversion by Dn: share of an install cohort with ≥1 validated purchase by day n
SELECT
  u.install_date,
  SAFE_DIVIDE(COUNT(DISTINCT IF(p.validated_at < TIMESTAMP(DATE_ADD(u.install_date, INTERVAL 8 DAY)),
                                p.user_id, NULL)),
              COUNT(DISTINCT u.user_id)) AS payer_conversion_d7
FROM analytics.dim_users u
LEFT JOIN analytics.fct_purchases p
  ON p.user_id = u.user_id AND p.amount_net_usd > 0
GROUP BY 1;
```

More SQL — sessionization, funnels, SRM, CUPED, attribution joins, dedupe — is in `references/sql-library.md`; read it when building those models.

### Definitions that cause most disputes

| Term | Pick one, document it |
| --- | --- |
| Day boundary | UTC calendar day (default) vs local day vs rolling 24 h from install |
| Retention | Classic (active on exactly day n) vs rolling (active on day n or later) — rolling reads higher |
| Denominator | First-open installs vs MMP installs vs account creations |
| Active | Any event vs a session ≥ N seconds vs a core action — background pings must not count |
| Revenue | Gross vs net of store fee; refunds netted on refund date vs purchase date |
| LTV | Per install (all users) vs per payer — always state which |
| ARPDAU | Net revenue ÷ DAU on the same day and basis |

### Experiment statistics

- **Assignment:** `bucket = FARM_FINGERPRINT(CONCAT(exp_salt, user_id))` mod 10,000 → variant ranges. Deterministic, server-side, salt per experiment so layers are independent. Log exposure when the player first sees the difference, and analyze exposed users only (intent-to-treat within the exposed set).
- **Sample size (continuous metric, two arms, α = 0.05 two-sided, power 0.8):** `n per arm = 2 (1.96 + 0.84)² σ² / Δ² ≈ 15.7 σ² / Δ²`. For proportions use `σ² = p(1 − p)` (Lehr's rule in `game-playtest-analyst`). Revenue is heavy-tailed: 14-day revenue per user with mean $0.50 and σ $8 needs ~1.6M users per arm to detect +5%. Winsorize at p99.9 (σ falls to perhaps $3 → ~226k per arm) and apply CUPED before deciding a test is unaffordable.
- **CUPED:** `Y_adj = Y − θ (X − mean(X))`, `θ = cov(X, Y) / var(X)` on pooled data, X a pre-exposure covariate (pre-period revenue or sessions for existing players; first-session behaviour before exposure for new installs). Variance falls by a factor `(1 − ρ²)`; ρ = 0.6 cuts the required n by 36%.
- **SRM:** chi-square of observed vs expected arm counts; p < 0.001 means assignment or logging is broken — do not read the result.
- **Sequential pitfalls:** repeated peeking at a fixed-horizon test inflates false positives far above 5% (alpha-spending details in `game-playtest-analyst`). If stakeholders must watch, use an always-valid method (mSPRT or group-sequential with pre-set looks) and still pre-commit a maximum duration. Cohort metrics (D7, D30) are not readable until the last cohort matures.
- **Interference:** players who trade, battle or share a guild contaminate user-level splits. Randomize by guild, server or region when the treatment touches shared systems (economy, matchmaking, events).
- **Novelty and primacy:** hold tests through at least two weekly cycles; check lift by days-since-exposure.
- **Guardrails** (one-sided, pre-registered): crash-free sessions, D1/D7 retention, refund rate, payment error rate, session length, ad revenue, server latency.
- **Tools** (as of 2026-10; verify): Firebase Remote Config with real-time updates and A/B Testing; LaunchDarkly; Unity Remote Config; PlayFab Experiments; Satori. Statsig was acquired by OpenAI in Sept 2025 and operates independently — weigh vendor continuity (https://pulse2.com/openai-acquires-statsig-for-a-reported-1-1-billion/).

### Attribution data (as of 2026-10; verify)

- **ATT** opt-in averaged 38% in Q1 2026, about 39% in gaming (https://www.adjust.com/blog/att-opt-in-rates-2025). For the rest of iOS, user-level attribution does not exist; do not impute it.
- **AdAttributionKit** succeeds SKAdNetwork 4 (no SKAN 5); iOS 18.4 added configurable windows and overlapping re-engagement conversions; from iOS 26.2 Apple Ads postbacks use AAK — ingest both SKAN and AAK postback copies (https://www.adjust.com/blog/wwdc-adattributionkit-2025/ ; https://support.appsflyer.com/hc/en-us/articles/34395758837137-Bulletin-Apple-Ads-now-supports-SKAN-attribution).
- **Android:** Privacy Sandbox APIs were retired in Oct 2025; GAID remains (https://engadget.com/cybersecurity/google-has-killed-privacy-sandbox-130029899.html).
- **Grain:** MMP user-level (consented iOS, Android) → join on `customer_user_id`; SKAN/AAK postbacks → `fct_skan_postbacks` keyed by source identifier/campaign × postback date with conversion values; network cost → campaign × date × geo. Blend at campaign × date, never fabricate user-level iOS rows.

### Privacy and consent

- Consent state (analytics, ads personalization) and ATT status are envelope fields and gate which SDKs initialize. Store consent changes as events with timestamps.
- Pseudonymize: account `user_id` in analytics, no names, emails or raw IP in event tables; derive country at the collector, then drop IP.
- **Deletion:** a request keyed by `user_id` deletes or anonymizes rows across raw, staging, marts and vendor exports. GDPR requires responding within one month (as of 2026-10; verify). Partition and cluster raw tables so deletion is affordable.
- **Retention policy:** raw events kept for a fixed period (e.g. 13–25 months), aggregates longer.
- **Children:** under-13 accounts in COPPA scope need parental consent before personal data and no behavioural ads; flag them in `dim_users` and filter at the source.

## Diagnostics

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Two dashboards disagree on DAU | Separate definitions (active = any event vs session) | One mart, one definition; deprecate the other |
| D1 retention jumps after an update | Background or push-wake events now count as activity | Define active as a foreground session; filter by event type |
| Revenue in BI ≠ finance | Client purchase events, gross vs net, refunds missing | Server-validated `fct_purchases`, refunds as negative rows |
| Duplicate events after reconnect | Retries without dedupe | `event_id` UUID; dedupe in staging |
| Events "from the future" or out of order | Device clock skew | Use `server_ts` for partitioning; `seq` for ordering |
| Experiment arms 52/48 on a 50/50 split | SRM: assignment or exposure logging bug | Stop reading; fix logging; rerun |
| Every test "wins" early | Peeking at a fixed-horizon test | Pre-registered horizon or valid sequential method |
| Revenue test never significant | Heavy tail | Winsorize, CUPED, longer horizon, or test conversion instead |
| iOS installs by campaign do not sum to MMP total | SKAN/AAK aggregates vs MMP deterministic | Report separately; blend at campaign × date with modeled share |
| Daily KPI table late | Upstream partition late, no SLA alerting | Freshness tests, alert to owner, backfill job |
| Deletion request takes weeks | No user-keyed partitioning; vendor exports untracked | Clustered by user_id; vendor deletion APIs in the workflow |

## Anti-Patterns

**The Screen-Driven Taxonomy** — one event per button because the client has buttons. Thousands of events, none answering a question.

**The Rename in Place** — changing an event's meaning without a version bump. Every historical chart silently breaks.

**The Client Revenue Truth** — revenue from client purchase events. Fraud, retries and refunds all land in the KPI.

**The Shadow Metric** — a dashboard computing its own DAU or retention. Two numbers, one meeting, no decision.

**The Peeking Ship** — stopping a test the first day p < 0.05. The false-positive rate is no longer 5%.

**The User-Level SKAN Join** — fabricating user rows from aggregate postbacks. Attribution becomes fiction with decimals.

**The Sampled Purchase** — sampling all events uniformly to save cost, including economy and revenue. Whale behaviour disappears from the data.

**The Undeletable Lake** — raw data with no user-keyed path to deletion. A legal liability, not an asset.

## Quality Checklist

- [ ] Every event traces to a question and a decision; owner recorded
- [ ] Taxonomy is `object_action` snake_case; shared envelope on every event
- [ ] Schema registry with versions; collector validates and quarantines failures
- [ ] `event_id` dedupe, `server_ts` partitioning, `seq` ordering, offline batching
- [ ] Revenue from server-validated transactions, refunds as negative rows, ad revenue impression-level
- [ ] KPI dictionary states denominator, day boundary, timezone and maturity for each KPI
- [ ] All dashboards read KPI marts; no dashboard computes its own DAU/retention
- [ ] dbt tests: uniqueness, not-null, accepted values, freshness, volume anomaly
- [ ] Experiments: deterministic server-side assignment, exposure logging, SRM check, one primary metric, guardrails, pre-set horizon or sequential method
- [ ] Revenue tests sized with winsorization and CUPED considered
- [ ] Shared-system tests randomized by cluster (guild, server, region)
- [ ] Attribution ingested at correct grain; no user-level iOS rows invented
- [ ] Consent and ATT state in envelope; SDK init gated; deletion propagates to all tables and vendors
- [ ] Freshness SLA for daily KPI table with alerting

## Related Skills

Interpretation of funnels, retention curves and playtest data belongs to `game-playtest-analyst` (if installed); this skill guarantees the numbers it reads are right. Experiment hypotheses come from `gamedev-growth-designer`, `gamedev-monetization-designer` and `gamedev-liveops-designer`; LTV, ROAS and MMM use the marts built here via `gamedev-financial-growth-strategist`. Receipt validation and the services that emit server events are `gamedev-backend-engineer`; collectors, streams and warehouse capacity at scale are `gamedev-infrastructure-engineer`, with platform-level service boundaries in `gamedev-platform-server-architect`. Client SDK integration details are `gamedev-unity-engineer`, `gamedev-ios-engineer` and `gamedev-android-engineer`. Remote-config rollout and kill switches for experiment flags coordinate with `gamedev-live-serving`. Fraudulent purchase and bot traffic filtering is `gamedev-anti-cheat-security`.
