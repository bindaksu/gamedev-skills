---
name: gamedev-level-layout-designer
description: >-
  Design and tune level, map, and board layouts: match-3 and puzzle boards with goals, blockers,
  move budgets and a difficulty sawtooth tuned to win-rate targets, plus spatial layouts for
  action and strategy maps (flow, sightlines, chokepoints). Use when asked to design or rebalance
  a match-3 or puzzle level, set move counts, read a level funnel or churn-per-level report,
  plan a level chain or hard-level cadence, greybox an arena, lane or 4X map, or decide
  procedural versus hand-authored levels.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: design
---

# Level Layout Designer

A level is a difficulty contract written in space. On a match-3 board the contract is a number, the per-attempt win rate, and every tile, blocker and move exists to land that number inside its band. On an action or strategy map it is a promise about where fights happen and how long it takes to get there. Both fail the same way: the designer judges the level by playing it themselves, an expert who already knows the solution. Levels are tuned against bots and cohorts, then validated against the funnel. Your own clear rate is the least informative number in the building.

**Interpretation note.** In this pack, "layout design" means level, map and board layout. Screen and HUD layout (grids, safe areas, component placement) belongs to `gamedev-ui-designer` and `gamedev-hud-engineer`.

## Role Profile

At top-grossing puzzle studios, level design is a production line run on data:

- **King** level designers "create, assess, rebalance and tune new and existing levels", stay consistent across a multi-title catalog, form hypotheses and A/B test them with the Data team. Seniors manage outsourced level teams (https://hitmarker.net/jobs/king-senior-level-designer-901935). Candy Crush ships new levels weekly, typically in batches of 30–60, and has grown past 21,000 levels; AI does a "first pass" on new levels and on reworking old ones (https://www.nbcnewyork.com/news/national-international/candy-crush-ai-puzzles/6259551/). King cut level-design roles in 2025 per anonymous sourcing — the surviving role is tuner and reviewer of generated levels, not hand-placer of tiles.
- **Playrix** level designers "create new match-3 levels", own the "final quality of match-3 levels", help develop "product metrics to assess the quality of levels", and A/B test level-chain structures in an in-house editor. Juniors were once required to have completed 500 levels of major match-3 games (https://hitmarker.net/jobs/playrix-senior-level-designer-match-3-1548141).
- **Dream Games and Peak** publish no "level designer" title. Level work sits inside a design-plus-data "Product Specialist" role, and Peak runs level-design workshops for new grads (https://www.patika.dev/en/bootcamp/peak-level-design-workshop-etkinligi).

**Hard skills:** board-mechanic literacy (every blocker's interaction matrix), bot and simulation reading, spreadsheet funnels, A/B design, greyboxing in the engine or editor. **Tools:** proprietary level editors, the engine, solver/bot farms, Amplitude-class product analytics, spreadsheets. **KPIs** (inferred from postings): per-level win rate and attempts against the target curve, churn per level, booster and continue conversion on hard levels, A/B results on level chains. **Collaborators:** producer, game designer, data team, economy, other level designers, outsourcing vendors.

## When to Use / Not

**Use** for board and level authoring, move/time budgets, difficulty curves across a level chain, level funnel diagnosis, spatial map layout, procedural-versus-authored decisions.

**Not:** chapter and mission structure across a campaign (`gamedev-campaign-designer`); the core match or combat mechanic itself (if installed, `core-loop-designer`; `gamedev-combat-designer`); prices of boosters and continues (`gamedev-monetization-designer`, if installed `game-economy-balancer`); juice on matches and cascades (`gamedev-game-feel-designer`); competitive map fairness and matchmaking (`gamedev-pvp-designer`).

## Inputs to Gather

- **Genre and goal grammar** — goal types and blockers already in the game, with their interaction rules. Default: none assumed; request the element list.
- **Level band** — which levels (e.g. 141–160), which cohort reaches them, at what install day.
- **Target curve** — per-attempt win-rate bands per level band. Default to the bands in Quantitative Reference, labeled heuristic.
- **Live telemetry** — per level: attempts, wins, unique players, churn, boosters, continues. Absent for new content: use bot data plus the human calibration from the last 200 shipped levels.
- **Bot** — does a solver exist, what policy (random, greedy, lookahead), how many runs per level it can afford.
- **Economy constraints** — lives, refill time, continue price, booster stock. Hard levels are a monetization surface; know what is sold.
- **For spatial maps** — player metrics (move speed, jump height, weapon ranges, unit sizes), mode, player count, target match length.

## Method

### A. Match-3 and puzzle boards

1. **Place the level in its band before opening the editor.** Read the band's target win rate and where this level sits in the sawtooth (relief, normal, hard, super hard). The editor is for hitting a number, not for discovering one.
2. **Pick one goal and at most one featured blocker.** A level teaches or tests one idea. Two new ideas in one level makes failures unattributable for the player and for you.
3. **Introduce elements with teach, test, twist.** Teach on an isolated board where failure is nearly impossible (win rate 95%+); test 2–4 levels later in a normal level; twist (combined with an older element) 8–15 levels later. Heuristic cadence: a new element every 10–20 levels early, every 30–60 later.
4. **Author the board shape and layers.** Shape controls cascades; layers (1–3 hit blockers) control goal effort. Leave a reachable cascade zone: boards with no open area of at least 4×4 tiles starve combos and feel unfair.
5. **Set colors before moves.** Color count is the strongest difficulty lever on a swap board; 4 colors cascades constantly, 6 rarely does. Change colors by one step only when moves cannot reach the band.
6. **Derive the move budget from simulation.** Run the bot 1,000+ seeds. Take the distribution of moves-to-win, then pick the move count whose bot win rate maps (through your calibration) to the human target. Never ship a move count you chose by playing.
7. **Calibrate bot to human.** Fit `human_win_rate ≈ f(bot_win_rate, bot_moves_left_p50)` on the last 100–200 live levels (logistic regression is enough). Recalibrate every major mechanic release; the bot does not feel frustration or use boosters.
8. **Check the shape of failure.** On hard levels, read the "goals remaining at fail" distribution. Healthy: most fails end within 1–3 goals of winning, because a close loss invites a retry. Do not fake closeness by rigging spawns; seeded fairness is a trust asset.
9. **Place in the chain and A/B test the chain.** Order matters as much as the level: two hard levels back to back triple the churn of one. Test chain variants (swap positions, relief after a super hard), not single levels in isolation.
10. **Ship, then read the funnel at 48 h and 7 days.** Retune any level outside its band by more than 10 points or with churn over 2× the band median. Retune moves first, colors second, layout last — layout changes break the player's mental model on retries.

Read `references/match3-board-tuning.md` when you need the goal and blocker taxonomy, the ranked difficulty-lever table, board geometry rules, or the bot/calibration pipeline in detail.

### B. Spatial layout (action, shooter, strategy, 4X)

1. **Build a metrics gym first.** Measure movement speed, jump/climb heights, weapon and ability ranges, unit footprints. Every later dimension derives from these.
2. **Draw the critical path and the loop.** Beat chart the route: entry, first sight of goal, first engagement, rest, climax, exit. Prefer loops over dead ends; a dead end is a wasted 30 seconds every time someone checks it.
3. **Design sightlines and cover by engagement range.** Long sightlines favor the defender and the long-range kit; break any line longer than the effective range of the median weapon.
4. **Place chokepoints with alternatives.** Every chokepoint needs a flank route 10–30% longer in travel time; without one, the choke becomes a stalemate.
5. **Landmark for navigation.** One unique landmark visible from each decision point; players should orient without the minimap.
6. **Greybox, playtest, then dress.** No art until the greybox passes timing targets. Art hides the layout's problems without fixing them.

Read `references/spatial-layout.md` when building shooter, MOBA/lane, RTS/4X, or mobile top-down maps — it holds dimension tables, timing targets and fairness checks.

## Deliverables

### 1. Level Spec Sheet (one row per level)

```
Level │ Band │ Saw role │ Goal(s) │ Featured element │ New? (teach/test/twist) │ Board WxH │ Colors │ Moves │
Bot win% (n=) │ Bot moves-left p50 │ Pred. human win% │ Target win% │ Pred. attempts (=1/win%) │
Booster-required? (must be N) │ Fail-closeness target │ Notes │ Status (draft/sim/A-B/live) │ Live win% │ Live churn%
```

### 2. Level Chain Plan (per 20-level band)

```
Band: 141–160   Install day reached (p50): D18   Target band win%: 35–55%   Hard at: 145, 150, 158   Super hard: 160
Lvl │ 141 142 143 144 145 146 147 148 149 150 ... 160
Role│  R   N   N   N   H   R   N   N   N   H  ...  SH
Elem│  .  test .  twist .  .  NEW-teach . test  .  ...
R relief, N normal, H hard, SH super hard
```

### 3. Level Funnel Report

```
Level │ Players reached │ Attempts │ Wins │ Win%/attempt │ Attempts-to-pass p50/p90 │ Churn-at-level% │
Boosters/attempt │ Continues/attempt │ Lives-out rate │ Δ vs target │ Verdict │ Action (moves/colors/layout) │ Owner │ Re-read date
```

### 4. Spatial Layout Brief

```
MAP: [name]   MODE: [mode]   PLAYERS: [n]   TARGET MATCH LENGTH: [min]
Metrics gym values: speed [m/s], jump [m], ranges short/mid/long [m]
Critical path beats: [entry → first sight → first contact → rest → climax → exit], with travel seconds
Spawn-to-first-contact: [s]   Lanes/routes: [n]   Chokepoints (with flank and Δtravel%): [list]
Longest uninterrupted sightline: [m] vs median effective weapon range [m]
Landmarks (one per decision point): [list]   Fairness check (symmetry or asymmetry rationale): [...]
```

## Quantitative Reference

### Win-rate targets per level band (heuristic, per attempt)

| Band | Typical per-attempt win rate | Attempts to pass (≈1/win%) | Purpose |
| --- | --- | --- | --- |
| Tutorial, levels 1–20 | 90–100% | 1.0–1.1 | Teach; a loss here is a design bug |
| Early, 21–60 | 70–90% | 1.1–1.4 | Habit; first booster use, first hard level near 20–30 |
| Early-mid, 61–200 | 50–70% normal | 1.4–2.0 | Monetization appears; sawtooth begins in earnest |
| Mid, 200–1,000 | 35–60% normal | 1.7–3.0 | The long game; most revenue lives here |
| Hard levels (any band past 30) | 20–35% | 3–5 | Spike; drives boosters and continues |
| Super hard | 8–20% | 5–12 | Rare, labeled, followed by relief |
| Relief | band + 15–25 points | — | Restores confidence after a spike |

These are starting bands; every game recalibrates them against its own churn curve. Per-attempt win rate is not completion rate: a level at 25% is eventually cleared by most players who keep playing.

### Sawtooth cadence (heuristic)

- **Cycle of 5–10 levels:** relief, 3–6 rising normals, one hard. Every 2–4 cycles, a super hard in place of the hard.
- **Label hard and super-hard levels visibly** before the attempt (Candy Crush and Royal Match both do). An announced spike reads as a challenge; an unannounced one reads as a paywall.
- **Never stack spikes.** Two consecutive levels under 30% roughly doubles to triples churn compared with one (heuristic; verify in your funnel).
- **End-of-batch levels** in a weekly drop are seen by your most engaged players first; do not put the batch's hardest level last.

### Move budget

```
moves = bot_moves_to_win at the percentile that hits the target bot win rate
Healthy normal level: human win% 40–60%, bot win% typically higher (bot plays without fatigue)
Moves-left at win (p50): 3–8 normal, 0–3 hard — big leftover = no tension; 0 at p50 = coin flip
Each move removed on a mid-band level shifts win% by roughly 2–6 points (heuristic; measure per level)
Time-limited variants: seconds = p50 bot time × 1.3–1.6 for humans; recheck on low-end devices (animation time eats budget)
```

### Level funnel metrics

| Metric | Formula | Alarm (heuristic) |
| --- | --- | --- |
| Win rate per attempt | wins ÷ attempts | Outside target band by > 10 points |
| Attempts to pass, p90 | 90th percentile attempts among clearers | > 3× band median — a hidden wall |
| Churn at level | players whose last level is L after 7 days ÷ players who reached L | > 2× rolling median of the band |
| Lives-out rate | sessions ending with 0 lives on L ÷ sessions on L | Rising for 3 consecutive levels |
| Booster per attempt | pre-game boosters used ÷ attempts | Booster-required levels (bot cannot win without) must be zero |
| Continue conversion | continues bought ÷ fails | Spikes on a normal level = level is mis-tuned, not a win |
| Fail closeness | share of fails with 1–3 goals left | Under 30% on a hard level = feels hopeless |

### Procedural versus authored

| Approach | Use when | Watch |
| --- | --- | --- |
| Fully authored | Fewer than ~500 levels, signature puzzles, teach levels | Cost per level; designer taste drift |
| Generated + human tune | Weekly drops at scale (King's AI first pass model) | Same-y boards; tune pass is mandatory, not optional |
| Procedural at runtime | Endless modes, roguelites | Must validate solvability per seed; no single-level funnel |
| Re-tune of legacy levels | Mechanic change shifts old levels | Re-sim the whole back catalog; old win rates are stale |

## Diagnostics

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Churn spike at one level, win% in band | Level feels unfair: spawn-dependent, goal hidden, blocker unreadable | Watch 5 replays; fix readability before difficulty |
| Win% far below bot prediction | Calibration stale, or a mechanic humans misread | Recalibrate; check first-attempt vs later-attempt split |
| Players clear in 1 attempt with 10+ moves left | Moves set by designer play or colors too low | Cut moves to bot target; consider +1 color |
| High continue buys on a "normal" level | Accidental hard level | Add 2–3 moves; move it to the next hard slot if wanted |
| p90 attempts 20+ while p50 is 3 | Heavy RNG dependence on one spawn pattern | Add a guaranteed spawn or open the cascade zone |
| Churn after every new element | Teach level missing or combined with another idea | Isolate the teach level at 95%+ |
| Weekly drop's levels all play the same | Generator without designer twist pass | Require one signature mechanic interaction per 5 levels |
| Spatial map: one route always used | Alternative route too long or too exposed | Shorten flank to within 10–30% travel time; add cover |
| Spatial map: spawn kills | Sightline from objective to spawn | Break the line; add spawn exit options |

## Anti-Patterns

**The Designer's Win Rate** — moves set by the level designer's own play. An expert who built the board clears it at 90%; the cohort clears it at 25%.

**The Hidden Wall** — an unlabeled super-hard level. Players read the spike as a paywall and churn at exactly the moment they would have been most willing to buy.

**The Double Spike** — two hard levels in a row. Each alone is in band; together they produce a churn cliff.

**The Booster-Required Level** — a level the bot cannot clear without a pre-game booster. That is a paywall disguised as a puzzle and erodes trust in every later level.

**The Rigged Near-Miss** — manipulating spawns so fails look close. It inflates continue buys for a quarter and becomes a store review the next.

**The Kitchen-Sink Teach** — introducing a new blocker on a board that also features two older ones. The player cannot tell which rule they broke.

**The Layout Retune** — rearranging a live level's board to fix difficulty. Players retrying it lose their learned plan; change moves first.

**The Art-First Greybox** — dressing a map before its timings are proven. Art makes bad flow look finished and expensive to change.

## Worked Example — Level 147, mid band

Band 141–160 target normal win 45–60%. Level 147 is a normal in the second cycle. Goal: clear 40 grass tiles; featured element: two-layer crates (test, taught at 142). Board 9×9, 5 colors, 25 moves (designer pick).

Bot (greedy + 1-ply lookahead), 2,000 seeds: bot win 71%, moves-left p50 = 6. Calibration from the last 150 live levels predicts human win ≈ 52%. In band — but live data at 48 h shows 31% win and churn at level 1.9× band median.

Replays show the crates sit on the only 4×4 open area; humans spend 6–8 moves clearing crates before any cascade. The bot handled it because it scores crate damage. Fix without breaking the board: move one crate column to the edge (layout change is acceptable here because the level is only 48 h old and most players have not retried yet), keep 25 moves. Re-sim: bot 74%, predicted human 55%. Live at 7 days: 51% win, churn 1.1× median. Calibration note logged: the bot overrates crate-first openings — adjust feature weight.

## Quality Checklist

- [ ] Every level has a band, a saw role and a target win rate before authoring
- [ ] Move count comes from bot simulation (n ≥ 1,000 seeds) through a recorded human calibration
- [ ] Bot can win every level without boosters
- [ ] Each level features at most one new idea; teach levels hit 95%+
- [ ] No two consecutive levels below 30% predicted win
- [ ] Hard and super-hard levels are labeled in UI and followed by relief
- [ ] Fail closeness measured on hard levels; no spawn manipulation to fake it
- [ ] Funnel report read at 48 h and 7 days with named owner and action
- [ ] Retune order respected: moves, then colors, then layout
- [ ] Spatial maps: metrics gym documented; every choke has a flank within 10–30% travel time
- [ ] Spatial maps: no sightline exceeds the median effective weapon range without a break
- [ ] Greybox passed timing targets before art

## Related Skills

- `gamedev-campaign-designer` — places level bands inside chapters and decides where boss gates sit; hand it the band win-rate curve.
- `gamedev-meta-progression-designer` — the meta (renovation, collection) is what players earn by clearing levels; align star/coin rewards with the sawtooth.
- `gamedev-monetization-designer` and, if installed, `game-economy-balancer` — lives, continues and booster pricing on hard levels.
- `gamedev-liveops-designer` — event levels and limited-time board modes reuse this method with event-specific win targets.
- `gamedev-analytics-engineer` — level start/end/fail events with goals-remaining and booster fields; without them the funnel cannot be read.
- `gamedev-game-feel-designer` — cascade and match feedback; a correct level that feels flat still churns.
- `gamedev-pvp-designer` — competitive map fairness, symmetry, spawn rules.
- If installed, `game-playtest-analyst` — replay coding and funnel reading; `core-loop-designer` when the problem is the match mechanic, not the board.
