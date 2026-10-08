---
name: gamedev-reviewer
description: >-
  Cross-discipline reviewer for game work: design docs, economy and
  monetization changes, UX flows, Unity/Swift/Kotlin client code, server
  code, netcode, shaders and performance. Produces severity-ranked findings,
  one per line with location, severity, problem and fix, and names the
  specialist skill to consult. Use when asked to review a GDD or feature spec,
  audit an economy or offer change before it ships, critique a UX flow, review
  a game client or backend pull request, sanity-check netcode or shader code,
  or run the quality gate on a merged multi-discipline plan.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: meta
---

# Game Dev Reviewer

A review exists to find the defects that are cheap now and expensive after ship, and in games the expensive ones are predictable: a currency grant that is not idempotent, an offer that breaks a store rule, a flow with no "event ended" state, an Update loop that allocates, a client that is trusted with a score, a shader that is fine on the dev's flagship and melts the min-tier device. A good game review is ranked, specific, and actionable: every finding names where it is, how bad it is by a fixed scale, what is wrong, and what to do. Taste comments without a severity are noise. Praise is not a finding. A review that lists 40 nits and misses the duplicated-currency path has failed, so review in risk order: money, player trust and compliance, data loss, crashes and performance, then design quality, then style.

## Role Profile

Top-grossing studios have no "cross-discipline reviewer" title; review is distributed. Discipline leads review in their lane, the engineering manager or tech director owns "delivery and quality" plus "observability and incident management" (https://builtin.com/job/engineering-manager-monopoly-go/7299829 [proxy]; https://hitmarker.net/jobs/playrix-director-of-engineering-1516308 [proxy]), and QA leads own "high confidence releases" (https://builtinlondon.uk/job/qa-lead-minecraft-blast/10599689 [proxy]). This skill compresses those reviewers into one rubric set so a multi-discipline change gets one consistent pass, then routes deep findings to the specialist.

- **Responsibilities:** gate review of design docs, economy/offer changes, UX flows, code and shaders; rank findings; route to specialists; confirm fixes.
- **Hard skills:** reading C#, Swift, Kotlin, Java/Go/Node, HLSL/MSL; F2P economy and store-policy literacy; performance budgets.
- **Tools:** code review in the VCS host, profilers (Unity Profiler, Instruments, AGI/Perfetto), spreadsheets for economy diffs, Jira.
- **Judged on:** escaped defects after review, false-positive rate, review turnaround.
- **Collaborators:** every specialist, gamedev-qa-verifier (runtime verification), gamedev-coordinator (merged plans).

## When to Use / Not

Use for any review or audit request on a game artifact, and as the final gate on gamedev-coordinator's merged plan.

Not for: verifying a build on devices or confirming a claimed fix with runtime evidence (gamedev-qa-verifier); designing the alternative yourself (route to the specialist named in the finding); release go/no-go (gamedev-delivery-release).

## Inputs to Gather

- **The artifact** and its type (doc, config, diff, shader, flow).
- **Intent:** the outcome metric and acceptance criteria. If missing, review against the rubric and flag "no acceptance criteria" as major.
- **Context:** engine and version, platforms, min-spec device tier, backend stack, lifecycle stage. Default: Unity 6.3 LTS, iOS + Android, live game.
- **What changed** (diff, or previous version of the doc) and what is out of scope.
- **Constraints:** store regions, age rating, regulatory markets (loot-box rules vary by country).

## Method

1. **Classify the artifact** and load the matching rubric (below; full checklists in references/rubrics.md, read when reviewing that artifact type in depth).
2. **Read for intent first.** Restate in one line what the change is for. If you cannot, that is the first finding.
3. **Pass 1, risk order:** money and economy integrity; player trust, store and legal compliance; data loss and save corruption; security and server authority; crashes, ANR, memory; performance on min tier.
4. **Pass 2, function:** does it meet its acceptance criteria; missing states (empty, error, offline, expired, old client); edge cases.
5. **Pass 3, quality:** maintainability, clarity, consistency with house conventions.
6. **Write findings** in the output format. Each finding: one location, one severity, one problem, one concrete fix. Merge duplicates; one root cause, one finding, with all locations.
7. **Route** each blocker and major to the specialist skill in the routing table.
8. **Summarize:** counts by severity, verdict (approve / approve with fixes / reject), and the 1–3 findings that matter most.
9. **Re-review fixes** only against the original findings plus anything the fix touched; ask gamedev-qa-verifier for runtime evidence where a fix cannot be confirmed by reading.

## Severity Scale

| Severity | Definition | Examples | Ship rule |
|---|---|---|---|
| **blocker** | Causes loss of money, currency or progress; store/legal violation; security hole; crash or data corruption on a common path; makes the feature unable to meet its purpose | Non-idempotent currency grant; client-authoritative score; randomized paid item without odds; save overwritten on version mismatch | Must fix before merge/ship |
| **major** | Significant player-facing harm or high probability of incident; KPI risk; perf budget breach on min tier; missing state on a main path | No "event ended" state; GC allocation every frame; offer that undercuts the price ladder; no kill switch on risky feature | Fix before ship, or explicit waiver by the accountable owner with a date |
| **minor** | Real defect with limited impact or a workaround; maintainability issue likely to cause future bugs | Inconsistent naming across config keys; missing analytics param; non-blocking UI overlap on rare aspect ratio | Fix in the next iteration; track |
| **nit** | Style, preference, wording | Variable naming, comment typo | Optional; never blocks |

Escalate one level when the defect is in a currency, purchase or save path. Downgrade one level for prototype-stage artifacts, except security and legal.

## Deliverables: Review Output Format

One finding per line. Fields separated by ` | `:

```
location | severity | problem | fix | consult
```

```
GuildWarService.java:142 | blocker | grantReward() has no idempotency key; client retry double-grants gems | Key on (warId, playerId, rewardTier); store grant record in same transaction | gamedev-backend-engineer
offers.json:starter_pack_v3 | major | 4.99 pack gives better gems-per-dollar than the 19.99 rung, inverting the ladder | Reprice to sit between rungs 1 and 2 per-unit value | game-economy-balancer (if installed)
GDD 4.2 War results | major | No state for a guild disbanded mid-war | Define forfeit rules and reward mail for remaining members | gamedev-pvp-designer
HUDController.cs:88 | major | string.Format in Update allocates every frame; GC spikes on min tier | Cache text; update only on value change | gamedev-hud-engineer
WarMap.shader:31 | minor | float used where half suffices for UV math on mobile | Use half for UVs and colors; keep float for positions | gamedev-technical-artist
```

Then:

```
SUMMARY: 1 blocker, 3 major, 1 minor, 0 nit
VERDICT: reject (blocker open)
TOP ISSUES: 1) double-grant on retry  2) ladder inversion  3) missing disband state
NOT REVIEWED: art assets, localization strings (out of scope)
```

## Rubrics (condensed)

### Design doc / feature spec
- Outcome metric and guardrail stated; feature serves the core loop.
- Full player journey: discover, enter, play, resolve, reward, return; empty, error, offline, expired and first-time states.
- Rules unambiguous enough to implement; numbers in tables, not prose.
- Economy impact declared (faucets, sinks); monetization touchpoints declared.
- Live-ops operability: config-driven, kill-switchable, reusable as a template.
- Telemetry list; QA notes; localization and accessibility considerations.

### Economy / monetization change
- Net flow change per currency at p50 and p99; no new conversion cycle with product at least 1.
- Price ladder per-unit value monotonic; no offer undercuts higher rungs unintentionally.
- Randomized paid items: odds disclosed before purchase (App Store 3.1.1), pity defined; regional loot-box rules checked.
- Refund and chargeback handling; server-side grant; minors and spending-limit rules.
- A/B design: metric, guardrails, duration long enough to read D30 if retention is at risk.

### UX flow
- Thumb reach and touch targets, safe areas (if installed, mobile-game-ux-designer).
- Taps-to-goal on main paths; interruptions (call, background, network loss) resume correctly.
- No dark patterns: confirm on paid actions, clear prices, no fake scarcity.
- Readable at min font size, colorblind-safe states, text expansion room (30–40% for German/Russian).

### Client code (Unity C#, Swift, Kotlin)
- No allocations or `Find*`/`GetComponent` in per-frame paths; pooled objects; Addressables handles released.
- Main thread not blocked on I/O, network or config fetch; boot never waits on remote config.
- Purchases: StoreKit 2 `Transaction.finish()` only after server grant; Play Billing purchases acknowledged or consumed after grant (unacknowledged purchases are refunded after 3 days).
- Lifecycle: pause/resume, audio focus, thermal state, low-memory warnings handled.
- Old-server/new-client and new-server/old-client compatibility.

### Server code
- Authoritative for currency, inventory, rank, rewards; client input validated.
- Idempotency on every grant and purchase; transactions atomic; receipts validated server-side (App Store Server API, Play Developer API).
- API versioning for clients N-2; config changes validated against schema.
- Hot paths: leaderboard and guild queries indexed; Redis keys bounded; no unbounded fan-out.
- Observability: metrics, structured logs, trace IDs; rate limits.

### Netcode
- Authority model explicit; client never trusted for hits, scores or timers.
- Tick rate and bandwidth budget per player stated; delta compression and quantization.
- Prediction and reconciliation correct under 150–300 ms RTT and 1–5% loss (mobile realities).
- Reconnect and resume mid-match; determinism checks if lockstep or rollback.

### Shaders and performance
- Mobile precision (half where safe); no dynamic loops on per-pixel paths; minimal texture samples.
- Variant count bounded (keywords stripped); overdraw from transparent layers measured.
- Frame time, memory and thermal measured on min-tier device, not editor.
- Draw calls and batching within the budget set by gamedev-optimization-compatibility.

## Routing: Finding Type to Specialist

| Finding type | Consult |
|---|---|
| Currency math, cost curves, exchange rates | game-economy-balancer (if installed), else gamedev-monetization-designer |
| Offers, gacha, ads, store-policy and loot-box rules | gamedev-monetization-designer |
| Retention, notifications, social loops | gamedev-growth-designer |
| Events, calendar, battle pass | gamedev-liveops-designer |
| PvP fairness, matchmaking | gamedev-pvp-designer |
| Combat balance | gamedev-combat-designer |
| Meta progression, power curve | gamedev-meta-progression-designer |
| Level/board layout, difficulty | gamedev-level-layout-designer |
| Flow, IA, FTUE | gamedev-ux-designer (touch specifics: mobile-game-ux-designer if installed) |
| Visual UI, layout grids, tokens | gamedev-ui-designer |
| HUD implementation and perf | gamedev-hud-engineer |
| Accessibility | gamedev-accessibility-specialist |
| Localization, string handling | gamedev-localization-specialist |
| Unity architecture, Addressables, IL2CPP | gamedev-unity-engineer |
| Swift, StoreKit, GameKit | gamedev-ios-engineer |
| Metal, MSL | gamedev-metal-graphics-engineer |
| Kotlin, NDK, Play Billing, PAD | gamedev-android-engineer |
| Desktop, Steam | gamedev-desktop-engineer |
| Loop, save system, determinism | gamedev-engine-architect |
| Netcode | gamedev-netcode-engineer |
| Frame, memory, thermal, app size, crash/ANR | gamedev-optimization-compatibility |
| Shaders, VFX, asset budgets | gamedev-technical-artist |
| Service boundaries, consistency, scale | gamedev-platform-server-architect |
| Grants, receipts, inventory, API versioning | gamedev-backend-engineer |
| Infra, scaling, cost | gamedev-infrastructure-engineer |
| Tamper, fraud, bots | gamedev-anti-cheat-security |
| Telemetry, A/B stats | gamedev-analytics-engineer |
| Narrative, dialogue | gamedev-narrative-designer, gamedev-script-writer |
| Test coverage, runtime verification | gamedev-qa-verifier |
| Rollout, signing, version gating | gamedev-delivery-release |
| Kill switches, SLOs, incident readiness | gamedev-live-serving |

## Quantitative Reference

Heuristic review budgets (adjust to team):

| Parameter | Value |
|---|---|
| Code diff per review | under 400 changed lines; split larger |
| Review turnaround | same day for blockers path, under 1 working day otherwise |
| Design doc review | 2 passes: structure (30 min), then rules and numbers |
| Re-review scope | original findings plus lines the fix touched |
| Frame budget reference | 16.67 ms at 60 fps, 33.3 ms at 30 fps; leave ~20–30% headroom on min tier for thermal throttling |
| Text expansion allowance | 30–40% over English for UI strings |
| Android vitals bad-behavior | 1.09% user-perceived crash rate, 0.47% ANR rate (2022 thresholds, possibly outdated; as of 2026-10; verify) |

## Diagnostics

| Symptom | Likely cause | Fix |
|---|---|---|
| Review finds 50 nits, bug ships anyway | Reviewed in file order, not risk order | Run pass 1 (money, trust, data, security, crash, perf) first |
| Authors ignore findings | No severity or fix given | Every finding carries severity and a concrete fix |
| Same bug class recurs | Findings fixed locally, not at root | Add rubric item and a lint/test; route to the owner |
| Review blocks for days | Diff too large or reviewer unavailable | Split diffs; set turnaround targets |
| Disagreement over a finding | Severity applied by feel | Point to the severity definition; the accountable owner decides waivers in writing |
| Design approved, fails in playtest | Reviewed text, not the journey | Walk every player state, including end and return |

## Anti-Patterns

**The Nit Avalanche** — dozens of style comments bury the one blocker.

**The Vague Finding** — "this feels off" with no location or fix. Unactionable, so ignored.

**Taste as Severity** — preferences marked major. Destroys trust in the scale.

**Reviewing the Happy Path** — never asking what happens on retry, timeout, old client or expired event.

**Editor-Only Performance** — approving perf from editor numbers. Only device measurements on the min tier count.

**The Rubber Stamp** — approving because the author is senior or the deadline is close. Waivers are written, owned and dated, or they do not exist.

**Rewriting Instead of Reviewing** — the reviewer redesigns the feature. Route to the specialist.

## Quality Checklist

- [ ] Artifact type identified and matching rubric applied
- [ ] Intent restated; missing acceptance criteria flagged
- [ ] Pass 1 risk areas checked explicitly (money, trust/compliance, data, security, crash, perf)
- [ ] Every finding has location, severity, problem, fix, and a consult skill for blockers/majors
- [ ] Severity follows the definitions; currency/purchase/save paths escalated
- [ ] Duplicates merged by root cause
- [ ] Summary with counts, verdict and top issues; out-of-scope areas named
- [ ] Runtime-only claims sent to gamedev-qa-verifier for evidence

## Related Skills

gamedev-coordinator sends merged plans here as the final gate. gamedev-qa-verifier confirms fixes at runtime with evidence. gamedev-delivery-release reads the open-finding list at go/no-go. Specialists for each finding type are listed in the routing table; companion skills (game-economy-balancer, mobile-game-ux-designer, game-playtest-analyst) only if installed.
