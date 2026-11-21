# Match-3 Board Tuning Reference

Read when authoring or retuning swap-match, tap-blast (collapse) or merge-board levels, or when building the bot and calibration pipeline. Numbers are heuristics unless stated; recalibrate on your own live data.

## Goal taxonomy

| Goal type | Player verb | Difficulty driver | Common failure |
| --- | --- | --- | --- |
| Collect N of a color/item | Match target pieces | Color count, target count | Too easy at 4 colors; trivial with cascades |
| Clear tiles (jelly, grass, carpet) | Match on top of tiles | Hard-to-reach corners, layers | Last tile in a corner: the "one jelly left" fail |
| Drop items (ingredients) | Clear columns beneath | Column count, blockers in drop path | Players misread which column exits |
| Break blockers | Hit blockers adjacent or with specials | Layers, spreading blockers | Spreading speed outpaces player in late moves |
| Score target | Any | Move count | Feels aimless; use sparingly in modern design |
| Mixed (2 goals) | Both | The weaker goal decides fails | Only after both goals are taught separately |

## Blocker taxonomy

| Class | Examples (generic) | Lever it pulls | Tuning knob |
| --- | --- | --- | --- |
| Layered static | Crates, ice, stone (1–3 layers) | Effort per goal | Layer count, placement |
| Locks/cages | Chained piece, cage | Removes pieces from matching | Count; adjacency to open area |
| Spreading | Chocolate/slime-like | Time pressure inside a move budget | Spread rate per move without a hit |
| Generators | Spawners of blockers or goal items | Pacing of goal availability | Spawn rate, cap |
| Movers | Conveyors, portals | Spatial reasoning | Keep to 1 per board in mid band |
| Collectors/exits | Drop exits, bins | Spatial goals | Exit count |
| Timers/bombs | Countdown pieces | Forced priority | Countdown length (moves) |

**Interaction matrix.** Maintain a table of every element vs every special piece (line, bomb, color bomb, propeller-type): does it damage, how many layers, does it pass through. Undefined cells become live bugs.

## Difficulty levers, ranked by strength (heuristic)

| Rank | Lever | Typical effect on win rate | Player visibility |
| --- | --- | --- | --- |
| 1 | Color count (±1) | 15–40 points | Invisible; safest for retunes |
| 2 | Move budget (±1) | 2–6 points per move mid band | Visible but rarely noticed |
| 3 | Goal count (±10%) | 3–8 points | Visible |
| 4 | Blocker layers (±1 on key blockers) | 5–15 points | Visible |
| 5 | Board shape / open area | Wide range, unpredictable | Very visible; breaks learned plans |
| 6 | Spawn rules (pre-placed specials, seeded drops) | Wide range | Invisible but trust-sensitive |

Rule: retune with the highest-ranked lever that moves the number enough, and only one lever per iteration so the effect is attributable.

## Board geometry rules of thumb

- Portrait phone boards commonly run 7–9 columns by 8–10 rows; tiles under ~40 pt are mis-tapped. Coordinate with `gamedev-ui-designer` and, if installed, `mobile-game-ux-designer`.
- Keep at least one open 4×4 region for cascades on normal levels; remove it deliberately only on hard levels.
- Holes and narrow necks reduce cascade length; use them to cool a board that cascades too freely at 4–5 colors.
- Goals in corners are 2–3× costlier to finish than the same goal in the center (heuristic); the last remaining goal is usually the one in a corner.

## Bot and simulation pipeline

1. **Policies.** Run at least two: a greedy bot (best immediate score for goal progress) and a lookahead bot (1–2 ply, or Monte Carlo rollouts). The gap between them estimates how much planning the level rewards.
2. **Sample size.** 1,000 seeds gives a win-rate standard error of about ±1.5 points at 50%; 2,000+ for hard levels where small shifts matter. (SE = sqrt(p(1−p)/n).)
3. **Outputs per level.** Win rate, moves-left distribution at win, goals-remaining distribution at fail, average cascade length, special pieces created per move.
4. **Calibration.** Regress live human per-attempt win rate on bot features over the last 100–200 shipped levels. Report residuals by featured element; an element with consistently negative residuals is one humans misread and needs better teaching or feedback, not more moves.
5. **Booster check.** Each level must be beatable by the bot with zero boosters at a non-trivial rate (at least ~5% for super hard).
6. **Regression.** Any change to spawn logic or a special piece re-sims the full live back catalog and flags levels that moved more than 5 points.

## First-attempt vs repeat-attempt

Split win rate by attempt number. A healthy level shows win rate rising with attempts (learning). Flat or falling win rate by attempt means the outcome is mostly spawn luck; players perceive that as unfair and churn even when the average is in band.

## Live practices observed at top studios (from public sources)

- King: weekly batches of new levels, a large back catalog continuously reworked, AI-assisted first pass on generation and rework, A/B tests with data partners, outsourced level teams managed by seniors.
- Playrix: level designers own final level quality, help define product metrics for level quality, and A/B test level-chain structures; deep genre play literacy is expected.
- Dream Games and Peak: level work sits in a design-plus-data product role rather than a dedicated level-designer title; the founders came from Peak's Toon Blast and Toy Blast teams, and the company cites extreme polish over title count.
