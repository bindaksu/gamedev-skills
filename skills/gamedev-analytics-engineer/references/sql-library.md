# SQL Library (BigQuery dialect)

Read when building staging dedupe, sessionization, funnels, experiment analysis (SRM, CUPED) or attribution joins. Table names follow the warehouse layout in SKILL.md. Adapt function names for Snowflake/Databricks.

## 1. Staging dedupe with late-arrival window

```sql
-- stg_events: keep the first copy of each event_id; reprocess a 3-day window daily
SELECT * EXCEPT (rn)
FROM (
  SELECT
    e.*,
    ROW_NUMBER() OVER (PARTITION BY event_id ORDER BY server_ts) AS rn
  FROM raw.events e
  WHERE DATE(server_ts) BETWEEN DATE_SUB(@run_date, INTERVAL 3 DAY) AND @run_date
)
WHERE rn = 1
  AND NOT is_test_device;
```

In dbt, make this an incremental model with `unique_key = 'event_id'` and `partition_by` on `DATE(server_ts)`, and re-run the trailing 3 partitions each day.

## 2. Sessionization (30-minute inactivity gap)

```sql
WITH ordered AS (
  SELECT
    user_id,
    server_ts,
    LAG(server_ts) OVER (PARTITION BY user_id ORDER BY server_ts, seq) AS prev_ts
  FROM analytics.stg_events
  WHERE event_name NOT IN ('push_received', 'background_ping')   -- foreground only
),
flagged AS (
  SELECT
    *,
    IF(prev_ts IS NULL OR TIMESTAMP_DIFF(server_ts, prev_ts, MINUTE) > 30, 1, 0) AS new_session
  FROM ordered
),
numbered AS (
  SELECT *, SUM(new_session) OVER (PARTITION BY user_id ORDER BY server_ts) AS session_n
  FROM flagged
)
SELECT
  user_id,
  session_n,
  MIN(server_ts) AS session_start,
  MAX(server_ts) AS session_end,
  TIMESTAMP_DIFF(MAX(server_ts), MIN(server_ts), SECOND) AS length_s,
  COUNT(*) AS events
FROM numbered
GROUP BY 1, 2;
```

Prefer client-emitted `session_start`/`session_end` with a `session_id` when the SDK provides them; use this as a fallback and a cross-check.

## 3. agg_user_day

```sql
SELECT
  s.user_id,
  DATE(s.session_start) AS activity_date,
  COUNT(*) AS sessions,
  SUM(s.length_s) AS seconds_played,
  COALESCE(p.iap_net_usd, 0) AS iap_net_usd,
  COALESCE(a.ad_rev_usd, 0) AS ad_rev_usd
FROM analytics.fct_sessions s
LEFT JOIN (
  SELECT user_id, DATE(validated_at) AS d, SUM(amount_net_usd) AS iap_net_usd
  FROM analytics.fct_purchases GROUP BY 1, 2
) p ON p.user_id = s.user_id AND p.d = DATE(s.session_start)
LEFT JOIN (
  SELECT user_id, DATE(impression_ts) AS d, SUM(revenue_usd) AS ad_rev_usd
  FROM analytics.fct_ad_impressions GROUP BY 1, 2
) a ON a.user_id = s.user_id AND a.d = DATE(s.session_start)
GROUP BY 1, 2, 5, 6;
```

Revenue on a day with no session (e.g. a refund) should be added via a FULL OUTER JOIN variant if finance needs exact daily totals; for ARPDAU, active-day revenue is the standard.

## 4. Funnel (ordered steps, per install cohort)

```sql
WITH steps AS (
  SELECT
    user_id,
    MIN(IF(event_name = 'first_open', server_ts, NULL))             AS t0,
    MIN(IF(event_name = 'tutorial_step_completed' AND step = 1, server_ts, NULL)) AS t1,
    MIN(IF(event_name = 'tutorial_completed', server_ts, NULL))     AS t2,
    MIN(IF(event_name = 'level_completed' AND level_id = 10 AND result = 'win', server_ts, NULL)) AS t3
  FROM analytics.stg_events
  GROUP BY 1
)
SELECT
  COUNTIF(t0 IS NOT NULL)                       AS opened,
  COUNTIF(t1 > t0)                              AS step1,
  COUNTIF(t2 > t1 AND t1 > t0)                  AS tutorial_done,
  COUNTIF(t3 > t2 AND t2 > t1 AND t1 > t0)      AS reached_l10
FROM steps
WHERE DATE(t0) BETWEEN @start AND @end;
```

Denominator is always `opened` (first launch), never a later step.

## 5. Experiment exposure and SRM

```sql
-- Exposure: first time each user saw the experiment
CREATE OR REPLACE TABLE analytics.mart_exp_exposure AS
SELECT user_id, exp_id, ANY_VALUE(variant) AS variant, MIN(server_ts) AS exposed_at
FROM analytics.stg_events, UNNEST(experiment_assignments) ea
WHERE event_name = 'experiment_exposed'
GROUP BY user_id, exp_id;

-- SRM chi-square for a 50/50 test (compare statistic with 10.83 for p < 0.001, df = 1)
WITH c AS (
  SELECT variant, COUNT(*) AS n FROM analytics.mart_exp_exposure
  WHERE exp_id = @exp GROUP BY 1
), t AS (SELECT SUM(n) AS total FROM c)
SELECT
  SUM(POW(n - total * 0.5, 2) / (total * 0.5)) AS chi_sq
FROM c, t;
```

Also check that each variant has the same user ID appearing in only one arm: `COUNT(DISTINCT variant) > 1` per user means assignment drifted.

## 6. CUPED-adjusted metric

```sql
-- Y = revenue in 14 days after exposure; X = revenue in 14 days before exposure (pre-period)
WITH base AS (
  SELECT
    x.user_id, x.variant,
    LEAST(COALESCE(post.rev, 0), @winsor_cap) AS y,
    LEAST(COALESCE(pre.rev, 0),  @winsor_cap) AS x_cov
  FROM analytics.mart_exp_exposure x
  LEFT JOIN (
    SELECT e.user_id, SUM(a.iap_net_usd + a.ad_rev_usd) AS rev
    FROM analytics.mart_exp_exposure e
    JOIN analytics.agg_user_day a
      ON a.user_id = e.user_id
     AND a.activity_date BETWEEN DATE(e.exposed_at) AND DATE_ADD(DATE(e.exposed_at), INTERVAL 13 DAY)
    WHERE e.exp_id = @exp GROUP BY 1
  ) post USING (user_id)
  LEFT JOIN (
    SELECT e.user_id, SUM(a.iap_net_usd + a.ad_rev_usd) AS rev
    FROM analytics.mart_exp_exposure e
    JOIN analytics.agg_user_day a
      ON a.user_id = e.user_id
     AND a.activity_date BETWEEN DATE_SUB(DATE(e.exposed_at), INTERVAL 14 DAY) AND DATE_SUB(DATE(e.exposed_at), INTERVAL 1 DAY)
    WHERE e.exp_id = @exp GROUP BY 1
  ) pre USING (user_id)
  WHERE x.exp_id = @exp
),
theta AS (
  SELECT COVAR_SAMP(y, x_cov) / VAR_SAMP(x_cov) AS th, AVG(x_cov) AS mx FROM base
)
SELECT
  variant,
  COUNT(*)                                  AS n,
  AVG(y)                                    AS mean_y,
  AVG(y - th * (x_cov - mx))                AS mean_y_cuped,
  VAR_SAMP(y - th * (x_cov - mx))           AS var_y_cuped
FROM base, theta
GROUP BY variant;
```

Compute θ on pooled data (both arms) so the adjustment does not depend on treatment. For new-install experiments there is no pre-period; use pre-exposure first-session behaviour as X, or skip CUPED.

## 7. Attribution joins

```sql
-- MMP user-level installs (consented iOS + Android) to users
SELECT u.user_id, m.media_source, m.campaign, m.install_time
FROM analytics.dim_users u
JOIN mmp.installs m ON m.customer_user_id = u.user_id;

-- SKAN / AdAttributionKit: aggregate only — campaign × postback date
SELECT
  postback_date,
  ad_network,
  source_identifier,                  -- campaign mapping via network
  COUNT(*)                                            AS installs,
  COUNTIF(fine_value >= 41 OR coarse_value = 'high')  AS predicted_payers
FROM attribution.skan_aak_postbacks
GROUP BY 1, 2, 3;

-- Blended campaign performance: cost × (MMP + SKAN) at campaign × date, never per user
SELECT c.date, c.campaign, c.spend_usd, s.installs AS skan_installs, m.installs AS mmp_installs
FROM cost.network_daily c
LEFT JOIN skan_by_campaign s ON s.campaign = c.campaign AND s.postback_date = c.date
LEFT JOIN mmp_by_campaign  m ON m.campaign = c.campaign AND m.install_date  = c.date;
```

SKAN/AAK postbacks arrive with delays (randomized timers), so postback date ≠ install date; report them in their own date frame or model the lag.

## 8. Deletion

```sql
-- Run per deletion request batch; tables clustered by user_id keep this cheap
DELETE FROM analytics.stg_events      WHERE user_id IN (SELECT user_id FROM privacy.deletion_queue WHERE status = 'pending');
DELETE FROM analytics.agg_user_day    WHERE user_id IN (SELECT user_id FROM privacy.deletion_queue WHERE status = 'pending');
-- repeat for every table holding user_id; then call vendor deletion APIs (MMP, product analytics) and mark status = 'done'
```

Keep the deletion workflow in the orchestrator with an audit log of tables touched and vendor responses.

## 9. dbt tests to attach (schema.yml sketch)

```yaml
models:
  - name: fct_purchases
    columns:
      - name: transaction_id
        tests: [unique, not_null]
      - name: amount_net_usd
        tests: [not_null]
    tests:
      - dbt_utils.recency:
          datepart: hour
          field: validated_at
          interval: 6
  - name: mart_kpi_daily
    tests:
      - dbt_utils.unique_combination_of_columns:
          combination_of_columns: [activity_date, platform, country]
```

Verify the current `dbt_utils` test names and argument syntax for your dbt version.
