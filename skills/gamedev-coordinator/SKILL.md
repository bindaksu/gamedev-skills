---
name: gamedev-coordinator
description: >-
  Entry point for the game studio skill pack. Decomposes a game request into
  discipline-sized work packages, routes each to the right specialist skill,
  writes handoff contracts and a RACI, sequences or parallelizes the
  specialists, merges their outputs and settles conflicts between disciplines.
  Use when a request spans more than one discipline ("add a guild war mode",
  "plan our soft launch", "build an event system"), when you are unsure which
  game skill applies, when two specialists disagree (monetization vs
  retention, art vs performance), or when a feature needs an owner map before
  work starts.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: meta
---

# Game Dev Coordinator

A game feature is never one discipline. "Add a guild war mode" is a PvP ruleset, a backend data model, a schedule of server-side state transitions, two new screens, a HUD state, an event calendar slot, a reward table that touches the economy, a dashboard and a test plan, and it ships through a store review you do not control. Studios that ship fast do not have better specialists; they have a GM or producer who cuts the request into packages with one owner each, writes down what "done" means for each package before anyone starts, and decides disagreements by a pre-agreed metric instead of by seniority. This skill is that function. It does not do the specialist work. It decides who does it, in what order, against what contract, and it merges the results into one plan a team can execute.

## Role Profile

There is no "coordinator" job title at top-grossing studios. The function is split between the **game lead / GM / franchise owner** and the **producer**. Top grossers run a GM or franchise owner per game, not a director hierarchy: King's franchise GM, Scopely's GM and product VP on Monopoly GO, Supercell's game lead with servant-leadership leads ([inference] from https://mobilegamer.biz/candy-crush-boss-todd-green-on-live-ops-excellence-new-games-and-that-microsoft-takeover/ and https://mobilegamer.biz/scopelys-monopoly-go-three-years-of-iterating-to-greatness-and-one-big-pivot/). The producer is "the hub between design, art, dev, QA, marketing, UA and CS" (https://hitmarker.net/jobs/kabam-game-producer-advanced-level-726287 [proxy]). Supercell added its first full-time producer to Brawl Stars only when the team passed ~40 people, because single-owner coordination had broken down (https://mobilegamer.biz/why-supercell-doubled-the-brawl-stars-team-and-continues-to-evolve-its-culture/).

- **Responsibilities:** decompose requests, assign one accountable owner per package, define acceptance criteria, sequence dependencies, arbitrate cross-discipline conflicts, merge outputs into one plan.
- **Hard skills:** enough literacy in every discipline to know which questions each specialist must answer; dependency mapping; F2P KPI fluency (D1/D7/D30, ARPDAU, payer conversion, crash-free sessions).
- **Tools:** Jira/Confluence, dependency maps, RACI sheets, KPI dashboards.
- **Judged on:** features shipped on the first integration pass, number of late-discovered cross-discipline blockers, decision latency on conflicts.
- **Collaborators:** every specialist skill; gamedev-producer for schedule, gamedev-reviewer for the gate.

## When to Use / Not

Use when a request touches two or more disciplines, when the right skill is unclear, when outputs from several specialists must be merged, or when disciplines disagree.

Do not use when the request is plainly single-discipline: go straight to the specialist (routing table below). Schedules, milestones, staffing and risk registers belong to gamedev-producer. Quality gates on finished work belong to gamedev-reviewer and gamedev-qa-verifier.

## Inputs to Gather

- **The request in one sentence plus the player-facing outcome.** If missing, write one and confirm it.
- **Lifecycle stage** (concept, prototype, vertical slice, alpha, soft launch, global, live). Default: live, because most requests are.
- **Platforms and engine.** Default: iOS + Android, Unity 6.3 LTS client, Java or Node backend (the most common top-grosser stack per research).
- **Business metric the feature exists to move** (retention, engagement, monetization, cost). Default: D7 retention, and say so.
- **Hard constraints:** launch date, store/legal region, team size, existing systems that must be reused.
- **Installed skills.** The six companion skills (core-loop-designer, game-economy-balancer, game-playtest-analyst, game-prototype-planner, game-asset-art-director, mobile-game-ux-designer) are optional; route to them only if installed, otherwise route to the closest pack skill.

## Method

1. **Restate the request as an outcome and a falsifiable metric.** "Guild wars raise D30 retention of guild members by 3 points without lowering non-guild D30." Without the metric, step 7 has nothing to arbitrate with.
2. **Classify the request** with the routing table. One primary skill owns the overall design; everything else is supporting.
3. **Decompose by player journey, then by layer.** Walk the feature as a player experiences it (discover, enter, play, resolve, reward, return). At each step, list the layers it touches: design rules, content, client UI/HUD, client logic, server, data, live ops, monetization, analytics, QA, release. Each non-empty cell is a candidate package. Walking the journey finds the packages people forget (notifications, matchmaking for absent players, reward mail, the "event ended" state).
4. **Merge and cut packages.** Merge cells with the same owner and the same acceptance test. Cut anything that does not serve the metric from step 1, and record cuts on the cut line (gamedev-producer owns MoSCoW).
5. **Write a handoff contract per package** (template below). Inputs must name the upstream package that produces them. A package with an input nobody produces is a hidden dependency; resolve it now.
6. **Build the dependency graph and choose execution mode.** Packages with no shared inputs run in parallel; anything consuming another package's output runs after it. Design and data contracts (rules spec, API schema, event taxonomy) run first because almost everything else consumes them.
7. **Pre-decide conflicts.** For every pair of packages that could disagree (monetization vs retention, art vs performance, design vs netcode), write which metric wins and the guardrail, using the conflict rules below, before work starts.
8. **Run the specialists** with the execution protocol below, each given only its contract and the upstream outputs it names.
9. **Merge.** Check every output against its acceptance criteria, reconcile interfaces (field names, IDs, event names, timings), and list open conflicts. Do not paper over a mismatch; send it back to the owner named in the contract.
10. **Gate.** Send the merged plan to gamedev-reviewer; send builds to gamedev-qa-verifier; hand shipping to gamedev-delivery-release and runtime to gamedev-live-serving.

## Routing Table

Primary owns the design and the merged output for that request type. Reviewer is the default gate. Full one-line scopes are in references/roster.md (read when you are unsure where a boundary falls).

| Request type | Primary | Supporting | Reviewer |
|---|---|---|---|
| New game concept / pillars | game-prototype-planner (if installed) else gamedev-producer | core-loop-designer, gamedev-narrative-designer, gamedev-financial-growth-strategist | gamedev-reviewer |
| Core loop feels repetitive | core-loop-designer (if installed) else gamedev-meta-progression-designer | gamedev-game-feel-designer, gamedev-growth-designer, game-playtest-analyst | gamedev-reviewer |
| Story, world, characters | gamedev-narrative-designer | gamedev-script-writer, gamedev-campaign-designer, gamedev-localization-specialist | gamedev-reviewer |
| Dialogue, barks, UI copy voice | gamedev-script-writer | gamedev-narrative-designer, gamedev-localization-specialist | gamedev-reviewer |
| Single-player campaign / missions | gamedev-campaign-designer | gamedev-level-layout-designer, gamedev-narrative-designer, gamedev-combat-designer | gamedev-reviewer |
| Season arc / marketing event campaign | gamedev-liveops-designer | gamedev-campaign-designer (season-arc section), gamedev-narrative-designer, gamedev-monetization-designer | gamedev-reviewer |
| Level, map or match-3 board "layout" | gamedev-level-layout-designer | gamedev-analytics-engineer, game-playtest-analyst | gamedev-reviewer |
| Screen layout, shop screen, UI kit | gamedev-ui-designer | gamedev-ux-designer, gamedev-hud-engineer, mobile-game-ux-designer | gamedev-reviewer |
| FTUE / onboarding / flow friction | gamedev-ux-designer | mobile-game-ux-designer, gamedev-growth-designer, gamedev-analytics-engineer | gamedev-reviewer |
| HUD build or HUD perf | gamedev-hud-engineer | gamedev-ui-designer, gamedev-optimization-compatibility | gamedev-reviewer |
| Combat, abilities, TTK | gamedev-combat-designer | gamedev-game-feel-designer, gamedev-netcode-engineer | gamedev-reviewer |
| PvP mode, matchmaking, ranked, guild wars | gamedev-pvp-designer | gamedev-backend-engineer, gamedev-netcode-engineer, gamedev-anti-cheat-security | gamedev-reviewer |
| Idle / builder / production chains | gamedev-simulation-designer | game-economy-balancer, gamedev-engine-architect | gamedev-reviewer |
| Collections, gear, power curve | gamedev-meta-progression-designer | game-economy-balancer, gamedev-monetization-designer | gamedev-reviewer |
| Events, battle pass, calendar | gamedev-liveops-designer | gamedev-monetization-designer, game-economy-balancer, gamedev-backend-engineer | gamedev-reviewer |
| Juice, feedback, haptics | gamedev-game-feel-designer | gamedev-audio-designer, gamedev-technical-artist | gamedev-reviewer |
| Retention drop, D1/D7/D30 | gamedev-growth-designer | gamedev-analytics-engineer, game-playtest-analyst, gamedev-ux-designer | gamedev-reviewer |
| Offers, shop, gacha, ads | gamedev-monetization-designer | game-economy-balancer, gamedev-ui-designer, gamedev-financial-growth-strategist | gamedev-reviewer |
| LTV, ROAS, UA, soft-launch KPIs, P&L | gamedev-financial-growth-strategist | gamedev-analytics-engineer, gamedev-producer | gamedev-reviewer |
| Event taxonomy, dashboards, A/B | gamedev-analytics-engineer | gamedev-backend-engineer, game-playtest-analyst | gamedev-reviewer |
| Accessibility | gamedev-accessibility-specialist | gamedev-ui-designer, gamedev-hud-engineer | gamedev-reviewer |
| Localization / culturalization | gamedev-localization-specialist | gamedev-script-writer, gamedev-ui-designer | gamedev-reviewer |
| Shaders, VFX, asset pipeline | gamedev-technical-artist | game-asset-art-director, gamedev-optimization-compatibility | gamedev-reviewer |
| Audio | gamedev-audio-designer | gamedev-game-feel-designer, gamedev-optimization-compatibility | gamedev-reviewer |
| Unity client architecture | gamedev-unity-engineer | gamedev-engine-architect, gamedev-optimization-compatibility | gamedev-reviewer |
| Native iOS / StoreKit / Game Center | gamedev-ios-engineer | gamedev-metal-graphics-engineer | gamedev-reviewer |
| Metal rendering / Apple GPU | gamedev-metal-graphics-engineer | gamedev-ios-engineer, gamedev-technical-artist | gamedev-reviewer |
| Native Android / Play Billing / PAD | gamedev-android-engineer | gamedev-optimization-compatibility | gamedev-reviewer |
| PC / Mac / Steam / Deck | gamedev-desktop-engineer | gamedev-optimization-compatibility, gamedev-accessibility-specialist | gamedev-reviewer |
| Engine architecture, save system | gamedev-engine-architect | gamedev-unity-engineer | gamedev-reviewer |
| Real-time multiplayer sync | gamedev-netcode-engineer | gamedev-infrastructure-engineer, gamedev-anti-cheat-security | gamedev-reviewer |
| FPS, memory, thermal, crashes, app size | gamedev-optimization-compatibility | gamedev-technical-artist, gamedev-qa-verifier | gamedev-reviewer |
| Backend service map, build vs buy | gamedev-platform-server-architect | gamedev-backend-engineer, gamedev-infrastructure-engineer | gamedev-reviewer |
| Economy transactions, receipts, inventory | gamedev-backend-engineer | gamedev-anti-cheat-security, gamedev-platform-server-architect | gamedev-reviewer |
| Fleets, regions, CDN, cost | gamedev-infrastructure-engineer | gamedev-live-serving | gamedev-reviewer |
| Cheating, fraud, account security | gamedev-anti-cheat-security | gamedev-backend-engineer, gamedev-analytics-engineer | gamedev-reviewer |
| Milestones, scope, staffing, risk | gamedev-producer | gamedev-financial-growth-strategist | gamedev-reviewer |
| Test plan, device matrix, cert | gamedev-qa-verifier | gamedev-optimization-compatibility | gamedev-reviewer |
| CI/CD, signing, store submission, rollout | gamedev-delivery-release | gamedev-qa-verifier | gamedev-reviewer |
| Incidents, SLOs, event-day scaling, hot content | gamedev-live-serving | gamedev-infrastructure-engineer, gamedev-backend-engineer | gamedev-reviewer |
| Assess or score the whole game, next edition | gamedev-assessment-manager | all lens skills it names | gamedev-reviewer |
| Write a prompt or brief for an agent | gamedev-brief-coordinator | gamedev-coordinator (packages first if 3+ disciplines) | gamedev-reviewer |

**Interpretation notes encoded above.** "Layout design" means level/map/board layout (gamedev-level-layout-designer); screen layout is gamedev-ui-designer. "Campaign design" means the story/mission campaign (gamedev-campaign-designer); LiveOps event campaigns are owned by gamedev-liveops-designer. "Serving" means live-service runtime and content serving (gamedev-live-serving); the build-and-release pipeline is gamedev-delivery-release.

## Worked Decomposition: "Add a guild war mode"

Outcome: guild members' D30 retention +3 points; guardrail: non-guild D30 flat, payer conversion not down. Async or real-time? Decide first: most top-grossing guild wars (4X, RPG, puzzle) are **async** (attack windows, server-resolved battles), which removes netcode entirely. Assume async unless the request says players fight live.

| # | Package | Owner | Consumes | Produces |
|---|---|---|---|---|
| P1 | War rules: format, matchmaking of guilds, season ladder, fairness, P2W boundary | gamedev-pvp-designer | outcome metric | rules spec |
| P2 | Guild-as-retention loop: roles, contribution, notifications, re-engagement | gamedev-growth-designer | P1 | loop + notification spec |
| P3 | Reward table and economy impact | gamedev-liveops-designer + game-economy-balancer (if installed) | P1 | reward table, net-flow delta |
| P4 | War pass / offers (if any) | gamedev-monetization-designer | P1, P3 | offer spec with guardrails |
| P5 | Service design: war state machine, guild matchmaking, scoring, scheduling | gamedev-platform-server-architect then gamedev-backend-engineer | P1 | API schema, data model, idempotent scoring |
| P6 | Real-time combat sync (only if live battles) | gamedev-netcode-engineer | P1, P5 | sync model |
| P7 | Exploit surface: score manipulation, alt guilds, bots | gamedev-anti-cheat-security | P1, P5 | threat list, server checks |
| P8 | Screens and flow: war map, roster, results | gamedev-ux-designer then gamedev-ui-designer | P1, P2 | flows, screens |
| P9 | War HUD states, timers | gamedev-hud-engineer | P8 | HUD spec + implementation |
| P10 | Calendar slot, cadence, event-day comms | gamedev-liveops-designer | P1, P3 | calendar entries |
| P11 | Telemetry and success dashboard | gamedev-analytics-engineer | outcome, P1, P5 | event taxonomy, dashboard |
| P12 | Test plan, load, exploit tests | gamedev-qa-verifier | P1, P5, P7, P8 | test plan, exit criteria |
| P13 | Server capacity for war-end spikes, kill switch | gamedev-live-serving | P5, P10 | capacity plan, runbook |
| P14 | Client release plan, min version, remote-config gating | gamedev-delivery-release | P5, P9 | release plan |

Order: P1 alone; then P2, P3, P5, P8 in parallel; then P4, P6, P7, P9, P10, P11; then P12, P13, P14; then gamedev-reviewer on the merged plan.

## Deliverables

### 1. Handoff contract (one per package)

```
PACKAGE:      P5 Guild war service design
OWNER (A):    gamedev-platform-server-architect      DOER (R): gamedev-backend-engineer
GOAL:         One sentence, tied to the outcome metric.
INPUTS:       P1 rules spec v1 (from gamedev-pvp-designer); existing guild service schema
OUT OF SCOPE: Client UI; reward values; real-time sync
OUTPUTS:      API schema (fields, types, error codes); state machine; data model; idempotency keys
ACCEPTANCE:   - Every rule in P1 maps to a state or validation
              - Scoring is idempotent under retry (same request id, same result)
              - Old clients (N-2) receive a defined response, never a crash
              - Load target stated (requests/s at war-end peak)
INTERFACES:   Names/IDs shared with P8, P11 (listed)
DEADLINE:     Milestone / date
ESCALATION:   Conflicts go to coordinator with both options and the metric each moves
```

### 2. RACI matrix

R = does the work, A = single accountable owner (exactly one per row), C = consulted before, I = informed after.

```
Package            | pvp | growth | liveops | monet | server-arch | backend | ux/ui | hud | analytics | qa | release | serving | producer
P1 rules           |  A/R|   C    |    C    |   C   |     C       |         |   C   |     |     C     |  I |         |         |    I
P5 service         |  C  |        |    I    |       |     A       |    R    |   I   |     |     C     |  C |    I    |    C    |    I
P12 test plan      |  C  |        |         |       |             |    C    |   C   |  C  |           | A/R|    C    |    C    |    I
```

Rules: one A per row; an A without an R means the A does the work; a row with more than three C entries is a meeting, not a package; split it.

### 3. Merged plan

```
OUTCOME + METRIC + GUARDRAILS
PACKAGES (table above) with status: not started / in progress / accepted / rejected
INTERFACE REGISTER: shared names (event names, IDs, endpoints, config keys), owner of each
OPEN CONFLICTS: conflict, options, metric each moves, decider, due date
CUT LINE: items cut, reason, revisit date
NEXT GATE: gamedev-reviewer date; gamedev-qa-verifier entry date
```

## Execution Protocol (sequential vs parallel)

Works the same whether specialists run as sub-agents, separate sessions or one agent switching skills.

- **Isolate.** Run each package in a fresh context that loads one specialist skill and receives only its handoff contract plus the upstream outputs it names. Shared context leaks assumptions across disciplines and hides missing inputs.
- **Parallel** when packages share no inputs or outputs. Cap concurrency at what you can review; 3–5 parallel packages is a practical ceiling for one merge pass [heuristic].
- **Sequential** when one package consumes another's output, or when an upstream decision could invalidate downstream work (rules before service design, service design before test plan).
- **Contract-first parallelism.** If two packages depend on each other (UI and backend), first run a short sequential step that fixes the interface (API schema, event names), then run both in parallel against it.
- **Return format.** Require each specialist to return: outputs, acceptance self-check (pass/fail per criterion), assumptions made, open questions, and any change to a shared interface.
- **Merge, do not average.** On mismatch, return the package to its owner with the specific failing criterion.

## Conflict Resolution Rules

Decide by the metric agreed in Method step 1, with guardrails. Seniority and loudness are not inputs.

1. **Player trust and legal compliance beat everything.** Odds disclosure, refund handling, minors' protections, store policy: not negotiable for revenue.
2. **Retention beats short-term monetization** unless the experiment shows net cohort LTV gain at D30+ with retention inside its guardrail. A monetization change that lifts D7 ARPDAU and drops D30 retention loses; the test must run long enough to see D30. Route the evidence to gamedev-financial-growth-strategist.
3. **Stability beats features.** A feature that drops crash-free sessions below target or breaks the frame budget on the minimum device tier does not ship until fixed (gamedev-optimization-compatibility sets the tier).
4. **Server authority beats client convenience** for anything that touches currency, rank or rewards (gamedev-anti-cheat-security).
5. **Readability beats spectacle**: art and VFX must hold the performance and readability budget (gamedev-technical-artist owns the budget).
6. **Data beats opinion, but only data that answers the question.** If no data exists, run the cheapest test (game-playtest-analyst, if installed, or gamedev-analytics-engineer A/B) rather than debating.
7. **Unresolved after one round:** the A in the RACI decides, writes the decision and the falsifying metric, and sets a revisit date.

## Quantitative Reference

All heuristics unless sourced.

| Parameter | Value | Why |
|---|---|---|
| Package size | 1 owner, 2–10 working days | Larger hides sub-dependencies; smaller drowns the merge in contracts |
| Packages per mid-size feature | 8–15 | Fewer usually means a forgotten layer (QA, release, telemetry) |
| Parallel packages per merge pass | 3–5 | Review capacity, not compute, is the bottleneck |
| C entries per RACI row | at most 3 | More turns a package into a meeting |
| Conflict decision latency | under 2 working days | Blocked packages cost more than a reversible wrong call |
| Team that needs a dedicated producer | ~40 people | Brawl Stars added its first full-time producer at 45+ (2024) |
| Discovery cell | 5–10 people | Supercell cells and Spark teams (~6, 2025) |
| Live team | 20–35 (Supercell, 2022), 100–150+ for mass-market casual hits | See references/team-profiles.md |

## Diagnostics

| Symptom | Likely cause | Fix |
|---|---|---|
| Integration fails on names/IDs | No interface register | Fix interfaces in a contract-first step before parallel work |
| Late discovery of a missing screen or state | Decomposed by discipline, not by player journey | Re-walk the journey: discover, enter, play, resolve, reward, return |
| Specialists produce overlapping work | Two A's on one package | One A per RACI row; merge or split |
| Merge reveals contradictory assumptions | Specialists shared context, not contracts | Isolate contexts; require an assumptions list in returns |
| Endless monetization vs retention debate | No pre-agreed metric | Apply conflict rule 2; run a test long enough to read D30 |
| Feature ships, metric does not move | Outcome metric never set or not instrumented | Package for gamedev-analytics-engineer before build |
| Netcode work on an async feature | Mode not decided upfront | Decide async vs real-time in step 3 |

## Anti-Patterns

**The Discipline Fan-Out** — sending the whole request to every specialist. You get 14 full designs of the same feature that do not fit together.

**The Two-Owner Package** — two accountable owners. Each assumes the other decided; nobody did.

**The Unwritten Done** — packages without acceptance criteria. Merge becomes renegotiation.

**Parallel Before Contract** — UI and backend built simultaneously without a fixed schema. Integration week becomes rework week.

**The HiPPO Tiebreak** — conflicts settled by the most senior voice instead of the agreed metric.

**The Skipped Ship Path** — decomposition ends at "build it" with no QA, release or live-serving package. Mobile releases cannot be rolled back; that work must be planned.

**The Coordinator Who Designs** — the coordinator writes the specialist content itself. Route it.

## Quality Checklist

- [ ] Outcome stated with a falsifiable metric and at least one guardrail
- [ ] Primary skill chosen from the routing table; interpretation notes applied
- [ ] Decomposition walked the full player journey, including end and return states
- [ ] Every package has exactly one A and a handoff contract with acceptance criteria
- [ ] Every input names the package that produces it; no orphan inputs
- [ ] Execution order derived from dependencies; contract-first step for mutual dependencies
- [ ] Conflicts pre-decided with the rules above before work starts
- [ ] QA, release and live-serving packages included for anything that ships
- [ ] Merged plan has an interface register, open conflicts and a cut line
- [ ] Companion skills referenced only "if installed", with a pack fallback

## Related Skills

Full roster with scopes: references/roster.md (read when routing an unfamiliar request). How top studios structure the teams these skills mirror: references/team-profiles.md (read when sizing a team or explaining why a role exists). Hand schedules, staffing and risk to gamedev-producer; the merged plan's quality gate to gamedev-reviewer; test strategy and release exit criteria to gamedev-qa-verifier; the pipeline and rollout to gamedev-delivery-release; runtime operations to gamedev-live-serving. Whole-game scoring goes to gamedev-assessment-manager; turning any package or assessment move into a paste-ready agent prompt goes to gamedev-brief-coordinator.
