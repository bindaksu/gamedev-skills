# Detection Rules, Bot/Farm Signals, Enforcement Schema, Appeals

Read when writing detection rules, building the ban pipeline, or designing the appeal flow.

## Detection layers (build in this order)

1. **Hard rules** — impossible by construction. Zero false positives if correct. Enforce automatically (still with evidence).
2. **Plausibility bounds** — physically possible but outside human limits for the cohort. Shadow-restrict, then review.
3. **Statistical outliers** — z-scores or percentile ranks within a cohort (same level, same MMR band, same device tier). Flag for review.
4. **Graph clustering** — accounts linked by device, IP/subnet, payment instrument, gifting/trade flows. Finds farms and mule networks.
5. **Models** — gradient-boosted trees or sequence models on telemetry features, trained on labels from layers 1–4 and appeal outcomes.

## Rule catalog (examples)

```
ID     | LAYER | RULE                                                                   | ACTION
R-001  | hard  | level result with score > max achievable for that level config         | rollback + flag
R-002  | hard  | reward claim for an event the player was not eligible for              | reject + flag
R-003  | hard  | ledger asset appears without a txn (audit query)                       | incident
R-010  | bound | level completion time < p0.1 of human completions for that level       | shadow + review
R-011  | bound | actions/sec sustained above human ceiling for > N seconds              | shadow + review
R-012  | bound | 20+ hours of activity in a 24h window for 3+ consecutive days          | flag (farm/bot)
R-020  | stat  | win rate z > 4 within MMR band over 50+ matches                        | review queue
R-021  | stat  | headshot/accuracy ratio beyond cohort p99.9 with low variance          | review queue
R-030  | graph | > K accounts per device/attested key in 30 days                        | cap rewards, cluster review
R-031  | graph | gift/trade flows converging on one account from many fresh accounts    | freeze receiver, review
R-040  | fraud | 3+ refunds in 90 days or refund after consuming > 80% of grant          | debt wallet + flag
R-041  | fraud | sandbox transaction presented to production                           | reject + flag
```

Version every rule; record precision (confirmed / enforced) from appeals and reviews. Retire rules whose precision drops.

## Bot and farm features (telemetry)

- Input timing entropy (inter-tap intervals too regular), identical action sequences across accounts.
- Session shape: fixed-length sessions at fixed times, no idle, no menu exploration, never views store or settings.
- Diurnal pattern: 24/7 activity per account or per device.
- Progress shape: perfectly linear resource accumulation; no failures.
- Environment: emulator/virtualized device verdicts, many accounts per attested key or DeviceCheck bit, data-center IP ranges.
- Economy flow: resources flowing out (gifts, trades, guild donations) far exceeding consumption.

Keep features aggregate where possible (per session), retain raw input traces only for flagged accounts and only for the appeal window.

## Enforcement schema

```sql
CREATE TABLE detection_event (
  event_id     uuid PRIMARY KEY,
  player_id    uuid NOT NULL,
  rule_id      text NOT NULL,
  rule_version int  NOT NULL,
  score        numeric,
  evidence_uri text NOT NULL,          -- immutable object storage path (logs, replay, ledger txn ids)
  created_at   timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE enforcement (
  enforcement_id uuid PRIMARY KEY,
  player_id      uuid NOT NULL,
  level          smallint NOT NULL,     -- 0 flag .. 4 permanent
  reason_code    text NOT NULL,         -- shown to player in generic form
  detection_ids  uuid[] NOT NULL,
  wave_id        text,                  -- null for immediate actions
  starts_at      timestamptz NOT NULL,
  ends_at        timestamptz,           -- null = permanent
  rollback_txn   uuid,                  -- ledger txn that reversed gains
  decided_by     text NOT NULL,         -- 'rule:R-001@3' or 'reviewer:<id>'
  state          text NOT NULL          -- pending_wave | active | expired | overturned
);

CREATE TABLE appeal (
  appeal_id      uuid PRIMARY KEY,
  enforcement_id uuid NOT NULL REFERENCES enforcement,
  submitted_at   timestamptz NOT NULL DEFAULT now(),
  player_text    text,
  reviewer       text,
  outcome        text,                  -- upheld | overturned | reduced
  decided_at     timestamptz
);
```

## Ban waves

- Cadence: weekly or bi-weekly, randomized day/time so cheat developers cannot correlate a client change with a ban.
- Between detection and wave: shadow restriction (level 1) so the cheater stops harming others immediately but receives no signal.
- Pre-wave QA: human review of a random sample per rule (e.g., 50 accounts or 5%, whichever is larger); abort the rule's portion of the wave if sample precision is below target (e.g., 98% for permanent bans).
- Execute: set enforcements active, run ledger rollbacks, recompute affected leaderboards and re-issue rewards to displaced legitimate players via campaign mail.
- After: track appeals and overturns at D+14; feed back into rule precision.

Immediate (non-wave) action is reserved for active harm: economy exploits in progress, fraud, account takeover.

## Shadow restrictions (design notes)

- Separate matchmaking pool for restricted accounts (they play each other); exclude from prize leaderboards (show their own score to them only); disable trade/gift outbound.
- Never degrade gameplay in ways that could hit a misclassified legitimate player hard (no fake disconnects, no reward sabotage beyond exclusion).
- Shadow state has a review deadline; it must resolve to cleared or enforced, not persist forever.

## Appeals

```
PLAYER SEES:     generic reason ("unauthorized modification", "abnormal activity", "payment abuse"), dates, appeal link
DO NOT REVEAL:   rule ids, thresholds, the signal that fired
SLA:             first response <= 7 days; decision <= 14 days
REVIEWER GETS:   evidence bundle, account history, prior enforcements, rule precision stats
OUTCOMES:        upheld | reduced | overturned (overturn restores items via ledger re-grant and clears device bits if set)
METRICS:         appeal rate, overturn rate per rule, time to decision
```

Overturn rate above ~10% on a rule means the rule, not the players, is the problem.

## Account security controls

- Login: per-account and per-IP rate limits; breached-password screening for email/password accounts; prefer platform sign-in (Apple, Google, Game Center, Play Games) over passwords.
- New-device or new-country login on a high-value account: step-up (email/OTP) before purchases, trades or linking changes.
- Session revocation on password change, recovery, or support action; show active sessions to the player.
- Recovery via support: scripted verification (purchase receipts, account creation date, linked platform), never "username + email address" alone; log every support-initiated change as a ledger/audit event with the agent id.
- Account trading and boosting: detect via sudden device/region switches combined with credential changes; enforce per ToS.
