# Scoring Rubric by Dimension

Read before scoring. The anchors (3 structural gap · 5 built, no gate · 8 passing gate on main path · 10 committed re-runnable artifact + measured instrumented run) apply everywhere; this file says what counts as the gate and the measurement for each dimension. Score from evidence on the pinned subject only.

| Dimension | What "built" means (5) | Gate that earns 8 | Measurement that earns 9–10 | Common caps |
|---|---|---|---|---|
| Core loop | Main verb loop playable start to finish | Automated full match/level/session on the main path passes (bot or harness) | Recorded device session plus telemetry of loop length and repeat count | Loop dead-ends or needs debug tools: ≤ 4 |
| Economy | Faucets and sinks implemented | Ledger/balance test or simulation over a player lifetime passes (no inflation, no printer cycles) | Measured earn rates E from builds feeding the ledger; refund/rollback paths tested | Open exploit or refund lockout: ≤ 6 |
| Retention | Daily/return systems exist (streaks, events, unlock pacing) | Return-path tests pass (resume, daily reset, notification scheduling) and events are instrumented | Cohort query runs against real telemetry; D1/D7 computable | No telemetry at all: ≤ 5 (score what is built; do not dock for missing players) |
| Campaign / content | Content reachable through the normal UI | Full chapter/route playthrough gate passes using the player's own controls | All chapters played through, content counts match the catalog | Harness uses actions the player cannot take: recalibrate down |
| Mobile UX | Flows complete on phone | UI tests on smallest and largest supported sizes; touch targets ≥ 44 pt / 48 dp checked | Screenshot matrix across devices, locales (long languages), safe areas, committed | Text clipping in a shipped locale: ≤ 6 |
| Art & feel | Final or approved art on main screens; feedback on core verbs | Asset provenance/approval check passes; audio and haptics fire on core events | Device recording of core loop; visual diff baselines committed | Unapproved or placeholder art in the app target: ≤ 6 |
| Monetization | Store, products and purchase code exist | Sandbox purchase, restore and refund flows pass; odds disclosure if random rewards | Purchase telemetry and server verification exercised end to end | Purchase blocked behind an unreviewed gate or policy risk: ≤ 6 |
| Evidence | Tests and gates exist | Acceptance ledger agrees with gate files for this subject | Every gate re-runnable by one command; results committed with SHA | Ledger rows that contradict gate files: ≤ 6 |
| Shippability | Build archives and installs | Store checklist passes (metadata, privacy, age rating, screenshots, review notes) | Build accepted by review or TestFlight/internal track with release gates green | Any open store blocker: ≤ 6 |
| Performance | Runs at target frame rate in casual play | Perf gate on simulator or CI scene passes budgets | Device run: frame p95, worst frame, thermal over time, memory peak within budget | Simulator-only numbers: ≤ 7 |

Optional dimensions when the game has them: PvP fairness (gamedev-pvp-designer), Live ops (gamedev-liveops-designer), Backend reliability (gamedev-live-serving), Accessibility (gamedev-accessibility-specialist). Add them to every later edition once added.

## Ceiling

The ceiling is the score this dimension would get if the work already planned or in flight lands with its evidence. It is not 10 by default. A dimension is "at ceiling" when nothing planned would raise it; say what would.

## Recalibration

When a previous edition over-scored (e.g. a campaign gate passed only because a test harness used an action the player does not have), lower the score now, label it "recalibrated", and explain in one line. Report the mean both with and without the recalibration if it moved the mean by more than 0.2.

## Human factors

Default: not scored. Owner dogfooding on a real device counts as machine evidence when logged with build and date. If the owner opts in to human-playtest scoring, add it as its own dimension rather than capping others.
