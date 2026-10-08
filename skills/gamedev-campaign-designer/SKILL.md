---
name: gamedev-campaign-designer
description: >-
  Structure single-player campaigns: chapters, missions and quests, mechanic introduction order,
  interest and difficulty curves across the whole run, boss gates, and power-gated stage campaigns
  in free-to-play, plus the arc of LiveOps event and season campaigns. Use when asked to plan a
  campaign or chapter structure, order missions, place bosses, fix a mid-campaign drop-off or a
  surprise wall, write a mission spec or livesheet, or shape the beats of a season or event arc.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: design
---

# Campaign Designer

A campaign is a novelty budget and a difficulty budget spent over time. Players abandon campaigns at two kinds of points: where nothing new has happened for too long, and where a wall arrives that nothing earlier prepared them for. So the campaign designer plans two curves together, interest and difficulty, schedules every mechanic's teach, test and twist, and places boss gates as exams on what the chapter taught. Individual missions can be great and the campaign still fail; the order is the design.

**Interpretation note.** In this pack, "campaign design" means the story/mission campaign: chapters, missions, quests and their pacing. LiveOps and marketing event campaigns (season arcs, limited-time event series) are covered in a section below, but the event calendar, event economy and season pass are owned by `gamedev-liveops-designer`.

## Role Profile

The job appears as campaign, mission or quest designer:

- A mobile AAA studio's mission designer owns and iterates missions "based on feedback and data", balances "data driven mission values" and maintains the "livesheet data" — all mission tunables live in data, not in scenes (https://berlingamescene.com/?p=12611).
- HoYoverse runs senior quest designer roles for its open-world RPGs (https://resumegeni.com/jobs/senior-quest-designer-varsapura-hoyoverse-b8462a7a66).
- Campaign leads carry 5+ years of mission design and storytelling and run missions from pitch through concept, implementation, bug fixing, balance and polish (https://startup.jobs/campaign-design-lead-absurd-ventures-8129644). Live-service variants design quests alongside monetization features and need expert F2P knowledge.

**Hard skills:** pacing and interest curves, mechanic sequencing, encounter and boss design, scripting (Lua, C#, visual scripting), spreadsheets for mission values, funnel reading. **Tools:** the engine and its scripting layer, livesheets, mission editors, analytics. **KPIs** (inferred): mission completion and drop-off rates, retries per mission, session length and return rate driven by mission chains, reward-economy balance per mission. **Collaborators:** narrative, level design, combat design, economy, QA.

## When to Use / Not

**Use** for campaign shape, chapter and mission ordering, mechanic introduction schedules, difficulty and interest curves across a campaign, boss gate design, power-gated stage campaigns, mission spec sheets, mission funnel diagnosis, and the arc of an event or season campaign.

**Not:** the layout of a single level or board (`gamedev-level-layout-designer`); combat numbers and boss move sets (`gamedev-combat-designer`); story premise, characters and themes (`gamedev-narrative-designer`); event calendars, battle passes and event economies (`gamedev-liveops-designer`); currency yields per mission (if installed, `game-economy-balancer`).

## Inputs to Gather

- **Campaign type** — premium linear, F2P stage campaign (power-gated), open-world quest graph, or live quest chains. Default: F2P mobile stage campaign.
- **Session shape** — median session length and target mission length. Default: 6-minute sessions, 2–3 minute missions.
- **Mechanics list** — every mechanic, enemy type and objective type the campaign must teach, with dependencies.
- **Progression model** — skill-gated, power-gated, or hybrid; how player power grows (levels, gear, heroes).
- **Narrative arc** — chapters and climaxes the campaign must carry.
- **Telemetry** — per-mission starts, completions, retries, quits, time; and D1/D7 by furthest mission. Absent: plan from targets below and instrument first.

## Method

1. **Fix the shape from session length.** Total missions = target campaign hours × 60 ÷ mission minutes. Group into chapters sized so a chapter ends every 3–7 days of normal play (F2P) or every 1–3 hours (premium). A chapter end is a reward, a story beat and a save point in the player's mind.
2. **Write the mechanic introduction matrix.** Each mechanic gets a teach mission (safe, isolated), a test mission (2–4 missions later), and a twist (combined with an older mechanic, 6–15 missions later). Never teach two mechanics in one mission.
3. **Draw the interest curve.** Score each mission's intended tension 1–5. Peaks rise chapter over chapter; every peak is followed by a valley; the curve never stays flat for more than 3 missions. Novelty (new mechanic, new space, new enemy, story reveal) is what lifts a mission; difficulty alone is not interest.
4. **Set difficulty targets per mission type** (table below) and sawtooth within chapters: ramp, spike at the boss, drop at the next chapter's opening.
5. **Design each boss gate as an exam.** The boss tests at least two mechanics taught in its chapter, telegraphs its attacks, checkpoints between phases, and its fail screen names what killed the player. If the boss tests something untaught, players blame the game, correctly.
6. **For power-gated campaigns, plan the walls.** Compare each stage's recommended power with the projected p50 player power on that day. Walls are allowed only where at least two alternative progress sources exist (side modes, idle rewards, events) and only for a planned duration.
7. **Enforce variety.** No more than 2 consecutive missions with the same objective type, and no more than 3 in the same space or biome. Rotate pace: intense, exploratory, puzzle, set-piece.
8. **Attach rewards to beats.** First-clear rewards front-load; star/rating rewards (3-star) drive replays; chapter-end rewards are the largest non-boss reward. Hand yields to the economy owner.
9. **Put every tunable in the livesheet.** Enemy counts, timers, reward amounts, recommended power, star thresholds: data, versioned, editable without a client release.
10. **Read the mission funnel and iterate.** Flag missions whose quit rate exceeds 2× the chapter median or whose retries exceed target. Fix teaching before tuning numbers; most walls are untaught mechanics.

Read `references/campaign-structures.md` when working on power-gated stage campaigns, open-world quest graphs, or mission objective archetypes.

## Deliverables

### 1. Campaign Beat Chart (one row per mission)

```
Ch │ Mission │ Type (story/combat/puzzle/escort/defense/boss/rest) │ Objective │ Space/biome │ Mechanic: teach/test/twist │
Tension 1–5 │ Story beat │ Target first-attempt win% │ Target minutes │ Recommended power (if gated) │ First-clear reward │
Star thresholds │ Checkpoints │ Notes
```

### 2. Mechanic Introduction Matrix

```
Mechanic     │ Depends on │ Teach (mission) │ Test │ Twist (with what) │ Boss that examines it │ Status
Dash         │ —          │ 1-3             │ 1-6  │ 2-4 (+ shield foes)│ Boss 2               │ live
Shield foes  │ Dash       │ 2-1             │ 2-3  │ 3-2 (+ turrets)    │ Boss 2, Boss 3       │ draft
```

### 3. Boss Gate Spec

```
BOSS:            [name]   CHAPTER: [n]   POSITION: final mission of chapter
EXAMINES:        [mechanics taught in chapter — at least two]
PHASES:          [n; what changes each phase; checkpoint between phases? Y]
TELEGRAPHS:      [attack → wind-up ms → readable cue (visual + audio)]
TARGETS:         first-attempt win [x]%, cumulative win by attempt 3 [y]%, by attempt 5 [z]%
FAIL SCREEN:     [cause shown + one-tap suggestion: upgrade X / try Y]
POWER CHECK:     recommended power [n] vs projected p50 player power on day [d]: [n] (gated games)
REWARD:          [chapter-end reward]  NEXT:  [rest mission]
```

### 4. Mission Funnel Report

```
Mission │ Starts │ Completions │ Completion% │ First-attempt win% │ Retries p50/p90 │ Quit-at-mission% │
Median minutes │ Δ vs targets │ Diagnosis (teach/tune/power/bug) │ Action │ Owner
```

### 5. Event Campaign Beat Chart (handoff to `gamedev-liveops-designer`)

```
Week/Day │ Beat (announce/launch/escalation/second wind/finale/wind-down) │ Story beat │ Quest chain │
New mode or mechanic │ Reward milestone │ Marketing moment │ Owner
```

## Quantitative Reference

All targets are heuristics; calibrate against your own funnel.

### Mission length and chapter size

| Context | Mission length | Missions per chapter | Chapter cadence |
| --- | --- | --- | --- |
| F2P stage campaign (idle/RPG/puzzle-RPG) | 1–3 min | 10–20 | Every 3–7 days of play |
| Mobile mid-core mission | 3–6 min | 6–12 | Every 2–5 days |
| Premium console/PC mission | 15–45 min | 3–6 | Every 1–3 h |
| Open-world main quest step | 10–30 min | n/a (acts) | Act every 5–15 h |

Checkpoints: lost progress on failure should rarely exceed 3–5 minutes in premium, 1–2 minutes on mobile.

### Difficulty targets by mission type (first attempt)

| Type | First-attempt win | Cumulative win |
| --- | --- | --- |
| Teach mission | 90–100% | — |
| Normal | 70–90% | ≥ 95% by attempt 3 |
| Chapter boss | 30–60% | ≥ 85–90% by attempt 3–5 |
| Final boss | 20–40% | ≥ 80% by attempt 5–8 |
| Rest / story | 95–100% | — |

### Mechanic cadence

- Early game: a new mechanic, enemy or objective type every 3–5 missions.
- Mid-game: every 6–10 missions; twists (combinations) carry novelty in between.
- Late game: novelty comes mainly from combinations and set pieces; a campaign with no new element in its last third feels padded.

### Interest curve rules

- Never more than 3 consecutive missions at the same tension score.
- Peak tension rises chapter over chapter; the final chapter peak is the highest.
- Every boss (tension 5) is followed by a rest mission (tension 1–2).
- The first 10 minutes contain a peak (hook), then drop to teach.

### Power gates (F2P)

```
gap(d) = recommended_power(stage) ÷ projected_p50_power(day d)
gap ≤ 1.0         → skill content, no wall
1.0 < gap ≤ 1.2   → soft wall: clearable with good play or a small upgrade
gap > 1.2         → hard wall: needs progression; allowed only with 2+ alternate progress sources
```

Early walls (first week) should last 1 day or less; mid-game walls 1–3 days; later walls longer only if side content fills the time. Every wall is a monetization surface and a churn point; place them with `gamedev-monetization-designer`.

### Completion

Premium single-player campaigns commonly see well under half of starters reach the end; F2P stage campaigns lose most players before the final chapter by design. Read per-chapter drop-off, not overall completion, and compare chapter drops with the chapter median.

## LiveOps Event and Season Campaigns

When "campaign" means a live event series or a season arc, this skill shapes the arc; ownership of the calendar, event economy, season pass and offers belongs to `gamedev-liveops-designer`. Supercell's Hay Day live-ops designers are expected to plan the live-ops economy so players "always have intuitive incentives to engage with the calendar" and to align event narratives, timing and messaging with marketing (https://hitmarker.net/jobs/supercell-live-ops-designer-hay-day-3571823).

What this skill contributes:

1. **Arc shape.** Season 4–8 weeks (heuristic): announce (3–7 days before), launch week with the new mechanic and story question, escalation, a "second wind" beat at roughly 40–60% through (new mode, boss, or story reveal) to counter mid-season decay, finale, then a wind-down with a tease of the next season.
2. **Quest chains inside the event.** Daily and weekly chains follow the same teach/test/twist rules; the event's new mechanic is taught on day 1, tested by day 3, combined by the second week.
3. **Event boss as exam.** An event finale boss examines the event mechanic, with the same telegraph and checkpoint rules as campaign bosses.
4. **Beat chart handoff.** Deliver the Event Campaign Beat Chart; the live-ops owner places it on the calendar and sets rewards and economy.

Heuristic: engaged players (5+ days per week) should reach the free reward track's end with roughly 15–30% of the season remaining; casual players should still reach the mid-season milestone.

## Diagnostics

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Quit spike at one mission | Untaught mechanic or surprise spike | Add or isolate the teach mission; move the spike to the boss slot |
| Slow bleed through the middle chapters | Flat interest curve, no novelty | Add twists or a set piece every 3 missions; cut repeated types |
| Boss win rate fine, but quits after boss | No rest beat or weak chapter reward | Rest mission and the chapter's best reward right after |
| Retries high everywhere in a chapter | Power gap too large or checkpointing too sparse | Recompute gap at p50 day; add checkpoints |
| Players stall at a stage for a week | Hard wall without alternate progress | Add side modes or idle sources; lower gap to ≤ 1.2 |
| Mission times far above target | Objective unclear, wayfinding poor | Clarify objective text and markers; check layout |
| Event engagement collapses mid-season | No second-wind beat | Add a mid-season reveal, mode or boss |
| Mission tuning needs client patches | Values hard-coded in scenes | Move tunables into the livesheet |

## Anti-Patterns

**The Flat Middle** — chapters 3 to 6 reuse the same mission types at slowly rising numbers. Interest flatlines and players drift away without a single spike to blame.

**The Surprise Wall** — a spike in a normal mission slot. Players read it as a bug or a paywall.

**The Untaught Exam** — a boss that tests a mechanic introduced in the boss fight itself. Players die, learn the rule, and resent the lesson.

**Same-Mission Syndrome** — four escort missions in a row because they were cheap to build. Variety rules exist because production pressure always pushes toward repetition.

**The Power Wall With No Side Door** — a hard power gate and no alternative progression. The only verb left is waiting or paying, and most players choose leaving.

**The Endless Tutorial** — teaching new rules every mission through mission 20. Players never get to master anything; teaching must give way to testing.

**The Checkpoint Tax** — 15 minutes lost on a late failure. Players stop experimenting and start quitting.

**The Orphaned Season** — an event arc whose finale depends on content that slips. Every season resolves its own question.

## Worked Example — mobile mid-core, chapter 2 (10 missions, ~4 min each)

| M | Type | Mechanic | Tension | Target win | Notes |
| --- | --- | --- | --- | --- | --- |
| 2-1 | Story/combat | Teach shield foes | 2 | 95% | Isolated shield foes; dash available |
| 2-2 | Combat | — | 3 | 85% | Mixed foes from ch. 1 |
| 2-3 | Combat | Test shield foes | 3 | 80% | Shields + ranged |
| 2-4 | Defense | Twist dash + shields | 4 | 75% | First defense mission of chapter |
| 2-5 | Rest/explore | — | 1 | 100% | Story reveal; collectible room |
| 2-6 | Escort | Teach turrets | 3 | 90% | Turrets isolated, no shields |
| 2-7 | Combat | Test turrets | 4 | 75% | |
| 2-8 | Puzzle/combat | Twist turrets + shields | 4 | 70% | |
| 2-9 | Set piece | — | 4 | 80% | Chase; story peak before boss |
| 2-10 | Boss | Examines shields, turrets, dash | 5 | 45% first, 90% by attempt 4 | Phase checkpoint; fail screen hints |

Live data showed 2-4 quit rate at 2.6× the chapter median. Diagnosis: the defense objective was new and combined with a twist in the same mission (two new ideas). Fix: 2-4 became a combat mission (twist only), and the defense objective moved to 2-7, where turrets were already taught; quit rate at 2-4 fell to 1.2× median in the next cohort.

## Quality Checklist

- [ ] Campaign shape derived from session length; chapter cadence within target band
- [ ] Every mechanic has teach, test and twist missions; none taught alongside another
- [ ] Interest curve scored; no flat run longer than 3 missions; every boss followed by rest
- [ ] Difficulty targets set per mission type; sawtooth inside each chapter
- [ ] Every boss examines at least two taught mechanics, telegraphs attacks, checkpoints between phases
- [ ] Power gaps computed against projected p50 power; hard walls have 2+ alternate progress sources
- [ ] Variety rules hold: no more than 2 same-objective missions in a row
- [ ] All tunables in the livesheet, versioned
- [ ] Mission funnel instrumented; quit-at-mission compared with chapter median
- [ ] Event/season arcs have a second-wind beat, resolve on their own, and are handed to the live-ops owner

## Related Skills

- `gamedev-level-layout-designer` — builds each mission's space or board to the targets in the beat chart.
- `gamedev-narrative-designer` — supplies the arc and climaxes the interest curve should land on.
- `gamedev-combat-designer` — boss move sets, enemy archetypes, TTK.
- `gamedev-liveops-designer` — owns event calendars, season passes and event economies; receives the Event Campaign Beat Chart.
- `gamedev-meta-progression-designer` — power curves feeding the gate math; chapter rewards.
- `gamedev-monetization-designer` — offers at walls and chapter ends; ethics of gates.
- `gamedev-script-writer` — briefings, objective text and mission dialogue.
- `gamedev-analytics-engineer` — mission start/complete/fail/quit events with attempt counters.
- If installed, `game-economy-balancer` for mission reward yields; `core-loop-designer` when the mission loop itself is the problem; `game-playtest-analyst` for funnel and cohort reading.
