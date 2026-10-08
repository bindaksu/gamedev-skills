---
name: gamedev-meta-progression-designer
description: >-
  Design the persistent layers that turn core-loop wins into owned, visible progress: collections
  and albums, hero rosters and shard ladders, gear, renovation and decor meta, account level, unlock
  pacing, and power curves. Use when planning what players spend stars, shards, or cards on, pacing a
  feature unlock schedule, sizing a roster or collection album, diagnosing power creep or a last-card
  completion wall, choosing how tightly meta couples to core difficulty, or when a game feels like
  levels with nothing to come back for.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: design
---

# Meta Progression Designer

The core loop is why a session is fun; the meta is why there is a next session. Meta converts disposable outcomes (a level won, a battle cleared) into something the player owns, sees, and is one step away from improving. Every meta layer answers three questions: what does the core loop pay into it, what does it pay back, and how long until the next visible step. A meta that consumes nothing from the core is a separate game. A meta that pays back raw power without a content gate is a power-creep machine. A meta whose next step is more than a session away is a to-do list players stop reading. Design the coupling deliberately, pace the steps from measured consumption rates, and never ship a layer you cannot keep feeding with content.

## Role Profile

No top-grossing studio posts a "meta designer" title. The work sits with the **systems designer** (progression, combat scaling, economy, rewards, "power curves, stat growth, gear or ability scaling"; builds "models, simulations, and tuning tools that define loot tables, costs, XP curves"; implements directly in-engine — Scopely Principal Systems Designer, https://hitmarker.net/jobs/scopely-principal-systems-designer-4669537), with seasonal collection layers co-owned by LiveOps. At Dream Games and Peak the same work is folded into a generalist "Product Specialist / PM, Games" role that combines design, data and A/B tests.

- **Responsibilities:** meta architecture (which layers, how coupled), power budget across axes, roster/gear/collection ladders, renovation area and task pacing, account-level spine, feature unlock schedule, content-runway forecasting, meta telemetry.
- **Hard skills:** spreadsheet and Python simulation (coupon collector, shard accrual, power vs difficulty), progression-curve math, cohort pacing analysis, A/B design on unlock order.
- **Why it matters commercially:** meta systems are the reusable asset of a formula. Century Games built Kingshot by reusing Whiteout Survival's core 4X systems, hero kits and live-ops events under a simpler skin (https://naavik.co/digest/century-games-4x-portfolio-strategy/). Renovation meta is art-bound: the Gardenscapes production team was 100+ people across disciplines around 2019 (https://www.articy.com/en/showcase/gardenscapes/), so runway is a production-capacity question, not a design whim.
- **Fewer layers, fully fed:** Dream Games' CEO describes a Pixar-style approach of few titles and extreme polish (https://www.pocketgamer.biz/dream-games-ceo-soner-aydemir-on-the-companys-expansion-into-new-markets). Applied to meta, that argues for a small number of layers, each with a content pipeline that can keep it alive, over many thin ones.
- **KPIs (inferred, not quoted):** time-to-level and time-to-area vs target at p50/p90; D30+ retention; sink utilization; feature adoption within N sessions of unlock; collection completion distribution; power-to-content ratio per chapter.
- **Collaborators:** core/level designers, economy, LiveOps, narrative, UI, analytics, art production (decor and hero throughput per month).

## When to Use / Not

Use for: choosing meta layers and their coupling to the core; roster, shard, gear and collection ladders; renovation/decor task and area pacing; account level and feature unlock schedules; power score definition and power-vs-content gap; content-runway forecasting.

Not for:
- Faucet/sink ledgers, cost-curve `r` derivation, currency exchange and price ladders: if installed, `game-economy-balancer`.
- The core loop itself: if installed, `core-loop-designer`.
- Per-level difficulty and stars-per-level tuning on the board: `gamedev-level-layout-designer`.
- Combat stat budgets, TTK, ability kits: `gamedev-combat-designer`.
- Gacha rates, pity disclosure, shard/offer packaging: `gamedev-monetization-designer`.
- Event-limited collections and battle pass calendars: `gamedev-liveops-designer`.
- Idle production chains and offline progress: `gamedev-simulation-designer`.

## Inputs to Gather

- **Core loop unit and its output** (level win, battle, run) and measured attempts per session, sessions per day, win rate by stage. Default if missing: 6 attempts/session, 2.5 sessions/day, 55% win rate mid-game (heuristic; replace with build data before shipping numbers).
- **Genre archetype:** casual puzzle + decor, mid-core hero RPG, 4X, roguelite + idle meta, PvP collection. It decides the coupling default.
- **Content production rate:** levels, decor areas, heroes, gear sets per month that art and level teams can actually ship. Without it, runway math is fiction.
- **Spend profile and audience:** F2P share, payer conversion, whether meta items are sold. Default: assume meta items are purchasable and design free-path timelines explicitly.
- **Existing telemetry:** time-to-level percentiles, feature adoption, collection completion, power distribution by cohort day.
- **Session target and lifetime target:** e.g. 10-minute sessions, 180-day planned live arc.
- **Constraints:** narrative arc (story-in-meta), store rules on randomized items, team size.

## Method

1. **Pick the meta family per layer and the coupling level.** Expression meta (decor, cosmetics, albums) does not change core outcomes; power meta (heroes, gear, account level) does. Then set coupling: *decoupled* (meta never changes difficulty — renovation puzzle games), *soft-coupled* (meta grants boosters or consumables), *hard-coupled* (power gates content — RPG, 4X). Decide this first because it decides whether difficulty lives in the level designer's hands or in your power curve.
2. **Define one spine.** Exactly one monotonic progress number the player always sees: area/chapter for decor games, account level for RPG/4X, trophy road for PvP. Every unlock hangs off the spine, never off calendar time, so fast and slow players see the same order.
3. **Write the meta map.** For each layer: input currency from the core, output, cap, next-step distance, and which team produces its content. A layer with no core input is orphaned; a layer with no production owner will starve.
4. **Budget power across axes (hard-coupled only).** Split total power across 3–5 axes, each gated by a different resource, no axis above 45% of the total. Single-axis power turns every reward except one into noise.
5. **Model consumption vs production (the runway).** Consumption = units of meta content a p50 and a p90 player consume per week; production = what the team ships per week. Compute the frontier date at p90. That date is when LiveOps must carry the game.
6. **Pace the step distance.** Set target time between visible meta steps by lifecycle phase (table below), then derive task costs, shard counts or XP from measured core output. Never pick costs first.
7. **Lay out the unlock schedule.** One new system at a time, introduced at a point where the player already has the input for it. Gate by spine position, not by day.
8. **Model random layers explicitly.** Collections and shard drops are coupon-collector problems; compute mean and p90 completion, then add duplicate conversion and last-item protection until p90 is under the target.
9. **Check the power-vs-content gap** chapter by chapter at p10/p50/p90 power. Fit win probability against power ratio from playtests.
10. **Hand cost curves to economy.** Give `game-economy-balancer` (if installed) the step targets and resource per axis; take back the cost curve and confirm time-to-step at measured earn rates.
11. **Instrument and gate the build.** Ship the telemetry panel before the layer; a meta you cannot measure cannot be paced.

## Deliverables

### 1. Meta Architecture Map

```
LAYER        | FAMILY      | COUPLING   | CORE INPUT        | OUTPUT                 | CAP / END        | NEXT STEP (p50) | CONTENT OWNER / RATE
Renovation   | Expression  | Decoupled  | 1 star per win    | task -> story beat     | area 1..N        | <= 1 session    | Art: X areas/month
Collection   | Expression  | Soft       | packs from events | set reward (boosters)  | album per season | 1-3 sessions    | LiveOps: 1 album / 4-8 wk
Hero roster  | Power       | Hard       | shards, XP        | team power             | 5 stars, lvl cap | 1 day           | Design+Art: N heroes/month
Gear         | Power       | Hard       | drops, ore        | stat %, set bonus      | rarity x level   | 1-2 sessions    | Design: 1 set / season
Account lvl  | Spine       | Gate       | XP from all modes | unlocks, hero lvl cap  | level cap        | 1 session early | Design
```

### 2. Unlock Schedule

```
Spine pos | Session # (p50) | System unlocked   | Input already held?   | Tutorial beats | First reward | Adoption target (within 3 sessions)
Lvl 3     | 1               | Renovation task 1 | Yes: 1 star from L1-3 | 1              | story beat   | 95%
Lvl 8     | 2-3             | Boosters          | Granted 3             | 1              | -            | 80%
Lvl 20    | 5-6             | Daily quests      | -                     | 1              | 1 pack       | 70%
...
RULES: max 1 new system per session for sessions 1-10; never 2 systems on one screen visit; every system gated on spine position
```

### 3. Renovation Area Sheet

```
AREA: [name]   STORY ARC: [beat list from narrative]   CHOICE TASKS: [count with 3 variants]
Task # | Description        | Star cost | Cumulative | Story beat? | Decor choice? | Levels needed (= cum / stars per win)
1      |                    |           |            |             |               |
...
TOTAL STARS: S   ATTEMPTS = S / (stars per win x win rate)   DAYS (p50) = attempts / (attempts per session x sessions/day)
```

### 4. Roster and Shard Ladder

```
RARITY | HEROES IN POOL H | UNLOCK SHARDS | STAR STEP SHARDS (2..5) | CUMULATIVE | RANDOM SHARDS/DAY | TARGETED SHARDS/DAY | DAYS TO MAX (p50 F2P)
Rare   |                  |               |                         |            |                   |                     |
Epic   |                  |               |                         |            |                   |                     |
Legend |                  |               |                         |            |                   |                     |
Days to max = cumulative / (random/H + targeted + wildcard)
Useful roster target: [team size] x [2-3] heroes at mid tier by day [N]
```

### 5. Collection Album Spec

```
ALBUM: [name]  LENGTH: [weeks]  SETS: [k]  ITEMS PER SET: [n]  RARITY TIERS & WEIGHTS: [...]
SOURCES: [core rewards, events, purchase]   DUPLICATE RULE: [dupe -> currency at rate]
LAST-ITEM PROTECTION: [cost to buy any missing item with dupe currency]
SOCIAL: [trade / gift rules, untradeable tier]
TARGETS: p50 completes [x] sets; p90 completes album; mean draws to complete a set = [computed]
SET REWARD: [what]   ALBUM REWARD: [what]   CARRY-OVER: [what survives the reset]
```

### 6. Power Budget

```
AXIS          | SHARE OF TOTAL POWER | GATING RESOURCE      | GROWTH SHAPE        | SOFT CAP / LINK
Hero level    | 35%                  | XP + soft currency   | exponential cost    | <= account level
Stars         | 25%                  | shards               | stepped             | rarity cap
Gear          | 25%                  | drops + ore          | rarity x upgrade    | gear level <= hero level
Talents/guild | 15%                  | time / social        | saturating          | per-tier unlock
```

### 7. Meta Telemetry Panel

```
METRIC                                   | CUT BY                       | ALERT WHEN
Time to next spine step (p50, p90)       | cohort day, spend tier       | > 1.5x target for 3 days
Unlock adoption within 3 sessions        | system, unlock position      | < 50%
Collection completion distribution       | set, album week              | any set < 10% completion at p90 by album end
Days-to-max per hero (owned, pursuing)   | rarity, spend tier           | median > 2x ladder target
Power-to-content ratio rho at frontier   | chapter, p10/p50/p90         | p10 < 0.85 for 3+ days of play
Hero usage share                         | role, release month          | top 5 heroes > 70% of team slots
Frontier share (players with no content) | spend tier                   | > 10% of DAU
Hoard index (held vs next-step cost)     | resource                     | > 5x next-step cost at p50
```

Read `references/meta-math.md` when you need the coupon-collector integral, a duplicate-conversion simulation, shard-ladder tables by rarity, gear rarity multipliers, or the power-vs-win-rate fit procedure.

## Quantitative Reference

All numbers in this section are **heuristics** from genre practice, to be replaced by measured values. None are internal figures of any named game.

### Coupling defaults by archetype

| Archetype | Dominant meta | Coupling | Who owns difficulty | Meta share of session time |
| --- | --- | --- | --- | --- |
| Match-3 / puzzle + decor | Renovation, collections | Decoupled (boosters soft) | Level designer | 10–20% |
| Casual board / social | Albums, building upgrades | Soft | Economy + LiveOps | 15–30% |
| Mid-core hero RPG | Roster, gear, account level | Hard | Meta + combat | 30–50% |
| 4X / SLG | Buildings, heroes, research | Hard | Meta + PvP | 40–60% |
| Roguelite + idle meta | Permanent upgrades, talents | Hard but capped | Meta + run design | 15–30% |

Decoupled meta lets level designers tune difficulty on the board without fighting a power curve; hard coupling gives spenders a lever on outcomes and therefore needs the soft caps below. Switching coupling after launch invalidates player investment — choose before soft launch.

### Step distance by lifecycle phase

| Phase | Target time between visible meta steps | Major milestone (area, star tier, chapter) |
| --- | --- | --- |
| Session 1 | 2–4 minutes | 1 by end of session 1 |
| Days 1–3 | 1 step per session | every 1–2 days |
| Days 4–14 | 1 step per 1–2 sessions | every 2–4 days |
| Days 15–60 | 1 step per 2–3 sessions | every 4–8 days |
| Day 60+ | 1 step per day | every 7–14 days, plus event layers |

If a player cannot see the next step reachable within the current or next session, the step is too far — split it.

### Renovation / decor meta

- **Star-per-win model:** a common genre pattern is one star per level won, spent on tasks costing a small number of stars each. Task cost rises slowly across the game (e.g. 1–2 early, 3–5 later); steeper task costs are how the meta absorbs a rising level supply.
- **Attempts per area** `A = S / (stars_per_win × win_rate)` where S is total star cost of the area.
- **Story beat density:** a narrative or visible decor change every 1–3 tasks; a task that only fills a progress bar is a tax.
- **Choice tasks:** 2–3 decor variants on roughly 1 task in 4–6 keeps ownership without multiplying art cost uncontrollably (each variant is extra art).
- **Runway check:** weekly level consumption at p90 vs weekly level production. As a public datapoint, Candy Crush adds new levels weekly in batches of 30–60 (https://www.pocketgamer.com/candy-crush-saga/how-many-levels-are-there, secondary source). Frontier players beyond production need events, not more stars.

### Hero rosters

- **Useful roster** = team size × 2–3 (counters, element or role coverage). Pool size beyond what dilutes random shards is cost, not content.
- **Random shard dilution:** a hero gets `S_random / H` shards per day from a uniform pool of H heroes. With H = 24 and 12 random shards/day, each hero gets 0.5/day — a 190-shard ladder takes 380 days. Random-only shard economies always need a targeted source (featured hero, wildcard shards, shop rotation).
- **Star ladder shape:** roughly doubling step cost (e.g. unlock 10, then 20/30/50/80) gives early stars in days and late stars in weeks.
- **Targets (heuristic):** first chosen hero at max stars for p50 F2P in 21–45 days; a full useful team at max in 120–200 days; new hero releases no more than 5–10% stronger than the best existing hero of the same role (above that, creep).
- **Duplicates must never be dead:** a duplicate of a maxed hero converts to a universal currency, never to nothing.

### Gear

- **Slots:** 4–6. Fewer than 4 removes build choice; more than 6 makes each drop feel small.
- **Rarity tiers:** 4–6, with base stat multipliers of roughly 1.0 / 1.3 / 1.7 / 2.2 / 2.8 per tier, each tier also raising the upgrade cap.
- **Set bonuses:** 2-piece and 4-piece bonuses worth 8–15% of the set's total stat budget. Above ~20% the set becomes mandatory and slots stop being choices.
- **Enhancement:** deterministic level-ups for the main path; random reforge only as an optional sink, never as the main gate.
- **Gear level cap tied to hero or account level** so gear cannot outrun content.

### Collections and albums

- **Coupon collector (equal odds):** expected draws to complete a set of n items = `n · H_n ≈ n(ln n + 0.577)`. n = 9: 25.5 draws; n = 12: 37.2; n = 20: 72.0.
- **Unequal odds:** `E[T] = ∫₀^∞ (1 − Π_i (1 − e^(−p_i t))) dt`. The rarest item dominates: with one item at 1/110 of draws, completion is pinned near 1/p ≈ 110 draws regardless of the rest.
- **Duplicate conversion plus last-item purchase** cuts the tail more than it cuts the mean. Simulated 9-item set with one rare card (mean 63 draws, p90 123): letting 30 duplicates buy the last missing card drops it to mean 36, p90 42.
- **Album length:** 4–8 weeks; target p50 completing 50–70% of sets, the most engaged 10–20% completing the album. A set nobody completes is a lie; an album everyone completes is not a goal.

### Account level and power curves

- **Account level cadence:** a level-up every session on day 1, about one per day by day 7, about one per week by day 60.
- **Hero level ≤ account level** (or gear level ≤ hero level) is the standard soft cap: it caps spend-driven power at the content the player has reached.
- **Power-to-content ratio** `ρ = P_player / R_content` (recommended power). Fit win probability with `p_win = 1 / (1 + ρ^(−k))`; k is fitted from telemetry, often in the 6–10 range. At k = 8: ρ = 0.9 → 30%, 1.0 → 50%, 1.1 → 68%, 1.2 → 81%.
- **Gap targets:** p50 player sits at ρ = 1.00–1.10 at the chapter frontier; p10 never below 0.85 for more than 2–3 days of play; p90 at 1.3+ is fine for story content but must be met by harder modes.
- **Power growth vs content growth:** if content recommended power grows by factor q per chapter and player power by g per chapter-equivalent of play, the gap drifts by `(g/q)^chapters`. Keep g/q within 0.97–1.03 per chapter.

### Unlock pacing

- At most **3 systems in the first session**, at most **1 new system per session** through session 10, then roughly 1 every 2–4 days through day 14, then unlocks follow content.
- **Adoption target:** 70%+ of players who see an unlock use it within 3 sessions. Below 50%, the system arrived before the player had a reason or an input for it.

## Diagnostics

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| D1 fine, D7 drops sharply at one spine position | Step distance jumps there (task cost or XP step) | Split the step; add an intermediate visible reward within 1 session |
| Players finish levels but skip renovation tasks | Tasks are progress-bar taxes without story or visual payoff | Story beat or visible change every 1–3 tasks; add choice tasks |
| Collection set completion under 20% at album end | Rare item weight too low; no duplicate conversion | Add dupe currency and last-item purchase; recompute p90 |
| Collection completed by most players in week 1 | Pack supply too high or set size too small | Larger sets or more rarity tiers; move supply into events |
| Most-used heroes are the newest release | Release power above 5–10% of same-role best | Cap new-hero budget; add upgrades for older heroes before new releases |
| Large roster but players use the same 5 heroes | No counters or role requirements; dilution of shards | Content that rewards role coverage; reduce random pool or add targeted shards |
| Win rate at chapter frontier under 35% for p50 | Content power growth q above player power growth g | Lower q or raise a cheap power axis; don't nerf live rewards |
| Spenders clear all content in days and stop | No soft cap linking power to spine | Hero lvl ≤ account lvl; gear lvl ≤ hero lvl |
| New feature adoption under 50% within 3 sessions | Unlocked before input exists or two unlocks collided | Move unlock later; ensure input held; one system per session |
| p90 players hit end of content weeks before update | Consumption exceeds production at the frontier | Raise late task costs, add repeatable layer or event-carried content |
| Players hoard shards or gear ore | Next step cost visible as a big jump, or fear of wrong choice | Show the full ladder; allow refunds/respec on early tiers |
| Players feel gear drops are meaningless | Too many slots or flat rarity multipliers | 4–6 slots; widen rarity multipliers; visible stat delta on drop |

## Anti-Patterns

**The Orphan Meta** — a layer that consumes nothing the core loop produces. Players ignore it or treat it as a separate chore, and the core loop gets no extra reason to be played.

**The Last-Sticker Wall** — a set whose rarest item sets completion time. The mean looks fine; the p90 posts the complaint. Duplicates with no path to the missing item turn a goal into a lottery.

**The Single-Axis Ladder** — all power on hero level. Every other reward is irrelevant, and the one resource that matters becomes the only one players notice.

**The Feature Avalanche** — five systems unlocked in the first two sessions. Adoption collapses for all of them; players learn to dismiss unlock popups.

**The Power Creep Ratchet** — each new hero or gear set beats the last by 15%+. Content must rise to match, old investment is devalued, and F2P players fall below the ρ = 0.85 floor.

**The Infinite Roster** — pool size grows faster than useful roster need. Random shards dilute across heroes nobody uses, and time-to-max for the hero the player wants goes to a year.

**The Calendar Gate** — unlocks tied to days since install instead of spine position. Fast players wait with nothing to do; slow players get systems they cannot feed.

**The Hollow Renovation** — decor tasks with no story beat, no visible change, no choice. The meta becomes a progress-bar tax on level wins.

**The Retroactive Reset** — changing costs or stats of items players already invested in. It teaches players that investment is unsafe; they stop investing.

## Worked Example — "Harbor Lane", match-3 with renovation meta

Measured in soft-launch build: p50 player 6 attempts/session, 2.5 sessions/day = 15 attempts/day; win rate around levels 120–160 is 55%; 1 star per win. Level production: 40 levels/week.

**Area 5 sheet.** 12 tasks, costs 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 5, 5 = **35 stars**. Attempts `A = 35 / (1 × 0.55) = 63.6`. Days at p50 = 63.6 / 15 = **4.2 days** — inside the 4–8 day band for days 15–60, so the area length holds. Story beat placed on tasks 2, 4, 6, 8, 10, 12 (every 2 tasks); choice tasks on 3, 7, 11 (3 of 12, one in four). Average task = 35/12 = 2.9 stars = 5.3 attempts — under one session at 6 attempts/session, so a visible step lands every session.

**Runway.** p50 consumes 35 levels per 4.2 days = **58 levels/week**; p90 plays about 3× median = 175 levels/week. Production is 40/week. Both outrun production, so time-to-frontier = `gap / (consumption − 40)`. With 600 levels at launch, week 3 has 600 + 3 × 40 = 720 levels. The p50 player is near level 174 (3 × 58): gap 546 closing at 18/week = **~30 weeks**. The p90 player is near level 525 (3 × 175): gap 195 closing at 135/week = **~1.4 weeks**. Decision: raise task costs from area 8 (6–8 stars) to slow consumption to ~45 levels/week at p50, and put the p90 frontier on event layers owned by LiveOps rather than adding levels the team cannot produce.

**Collection layer (soft-coupled).** A 9-card set with one rare card at weight 0.5 of 27.5 total: mean 63 packs, p90 123 — at 2 packs/day that is 62 days at p90, longer than the 6-week album. Adding "30 duplicates buy any missing card" drops it to mean 36, p90 42 packs = **21 days at p90**. Set reward: 3 boosters (soft coupling), never stars, so the collection cannot speed up the renovation runway.

**Unlock schedule check.** Renovation at level 3 (session 1), boosters at 8 (session 2), daily quests at 20 (session 5), collection at 40 (session 9), team events at 80 (day 5). One system per session; each arrives after its input exists. Boosters' 3-session adoption measured at 84%; collection at 46% — below 50%, so the first pack is granted on unlock and the first set is reduced to 6 cards.

## Quality Checklist

- [ ] Every layer has family, coupling, core input, output, cap, next-step distance, and a named content owner with a monthly rate
- [ ] One spine; every unlock gated on spine position, none on calendar days
- [ ] Step distances meet the lifecycle-phase table at p50 and are checked at p90
- [ ] Power split across 3–5 axes, no axis above 45%, each gated by a different resource
- [ ] Soft caps link power to the spine (hero level ≤ account level or equivalent)
- [ ] Power-to-content ratio ρ computed per chapter at p10/p50/p90; p50 within 1.00–1.10 at frontier
- [ ] New hero/gear releases ≤ 5–10% over best existing same-role option
- [ ] Every random layer has computed mean and p90 completion plus duplicate conversion and last-item protection
- [ ] Shard economy has a targeted source; days-to-max computed with pool dilution
- [ ] Unlock schedule: ≤ 3 systems in session 1, ≤ 1 new system per session through session 10
- [ ] Runway model: p50 and p90 consumption vs production, frontier date known and LiveOps informed
- [ ] Cost curves handed to economy and time-to-step re-verified at measured earn rates
- [ ] Telemetry live: time-to-step percentiles, adoption per unlock, completion distribution, ρ distribution, frontier share

## Related Skills

- If installed, `game-economy-balancer` — owns cost curves, currency flows and price ladders behind every step this skill paces.
- If installed, `core-loop-designer` — the loop whose output the meta consumes; fix there if the core produces nothing worth spending.
- `gamedev-level-layout-designer` — level difficulty and win rate that set stars per attempt; coordinate when attempts per area drift.
- `gamedev-combat-designer` — stat budgets and archetypes that power axes feed; agree on power score weights.
- `gamedev-narrative-designer` — story beats on renovation tasks and area arcs (story-in-meta).
- `gamedev-liveops-designer` — seasonal albums, event collections and carrying frontier players past the runway.
- `gamedev-monetization-designer` — gacha rates, pity, shard and decor offers built on these ladders.
- `gamedev-simulation-designer` — idle or production meta layers and offline accrual.
- `gamedev-growth-designer` — retention levers that hook into meta milestones and social collection trading.
- `gamedev-ui-designer` — making the spine, next step and full ladder legible on screen.
- `gamedev-analytics-engineer` — instrumenting the meta telemetry panel.
