---
name: gamedev-combat-designer
description: >-
  Design and balance combat as math plus timing: damage formulas, TTK, DPS and EHP models, frame data, hit and hurt boxes, ability specs, enemy archetypes and encounter budgets for real-time action, turn-based, and auto-battler games, mobile first. Use when tuning time-to-kill or choosing a damage formula, when one hero or unit dominates usage or win rate, when combat feels sluggish or hits feel unfair, when writing an ability spec or enemy roster, when building the combat balancing spreadsheet, or when adapting action combat to one-thumb touch controls.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: design
---

# Combat Designer

Combat is two systems pretending to be one: a **spreadsheet** that decides how long things live, and a **clock** that decides whether the player could have done anything about it. Most broken combat is broken in exactly one of the two. A boss that takes 90 seconds of mashing is a spreadsheet bug; an attack the player cannot react to is a clock bug; a hero in 70% of teams is usually a spreadsheet bug that hides in a term nobody modeled — uptime, accuracy, crit, or speed. Write the formula, measure the terms, and design the timing in milliseconds before anyone argues about how it feels.

## Role Profile

At a top-grossing studio the combat designer owns player combat mechanics, enemy behavior, and the encounter math, prototyping and polishing with animators, gameplay engineers, level designers, VFX and audio. Postings ask for 5+ years as a combat or game designer, at least one shipped title, scripting in C#, Lua or visual scripting, and playtest-driven iteration (https://builtin.com/job/senior-combat-designer-ca/1624266 ; https://www.builtinnyc.com/job/ieg-senior-principal-gameplay-combat-designer/8659124). In mobile live-service RPGs, "combat scaling" frequently sits inside the systems role next to progression and loot models (https://hitmarker.net/jobs/scopely-principal-systems-designer-4669537); sports-sim variants own match systems and positioning AI instead of hitboxes.

- **Hard skills:** damage/TTK modeling in spreadsheets, frame data and animation-timing specs, enemy AI behavior design, scripting, encounter budgeting, telemetry reading.
- **Tools:** Unity, Unreal or a proprietary engine; Lua/C#; animation state tools; spreadsheets; telemetry/SQL for win and usage data.
- **KPIs (inferred from responsibilities, not quoted):** TTK and encounter balance against targets; unit/hero usage and win-rate spread; playtest feel scores; stage fail-rate against the designed difficulty curve.
- **Collaborators:** animation (frame data lives in their clips), gameplay engineering, level design, VFX/audio (telegraphs), systems/economy (power curve), data.

## When to Use / Not

Use for: damage formulas, TTK/DPS/EHP models, frame data and cancel rules, hit/hurt box policy, ability specs, enemy archetype rosters, encounter threat budgets, turn order and speed systems, auto-battler synergy math, combat controls on touch, combat-unit balance passes.

Not for:
- Hit-stop feel, screen shake, particles, haptic timing beyond the frame budget → `gamedev-game-feel-designer`.
- Matchmaking, ranked ladders, PvP fairness and P2W boundaries → `gamedev-pvp-designer`.
- How power grows across an account (gear, rosters, star-ups) → `gamedev-meta-progression-designer`; currency costs of that power → if installed, `game-economy-balancer`.
- Rollback, prediction, lag compensation implementation → `gamedev-netcode-engineer`.
- Arena geometry, cover and chokepoints → `gamedev-level-layout-designer`; difficulty across a chapter or campaign → `gamedev-campaign-designer`.

## Inputs to Gather

- **Combat genre:** real-time action, turn-based (fixed rounds or speed/ATB), auto-battler, or hybrid auto-plus-skill-tap. Default: hybrid real-time with auto-attack and 2–4 manual skills, the dominant mobile RPG shape.
- **Simulation tick and render rate.** Default: fixed 60 Hz combat simulation, 30 or 60 fps render. If combat is coupled to render frame rate, fix that first.
- **Target session and fight length.** Default: 60–180 s per stage, 3–6 rounds per turn-based wave (heuristic).
- **Power curve:** stats per level/star/gear tier at p10/p50/p90 of the player base. Ask the meta-progression owner; if missing, assume stat growth of 5–8% per level (heuristic) and flag it.
- **Measured terms:** accuracy, uptime (fraction of fight time the player is actually dealing damage), dodge/block success, ability usage rate. If no build exists, assume accuracy 0.85 and uptime 0.70 for melee real-time and say so.
- **Input:** touch only, controller, or both; one-thumb or two-thumb.
- **PvP present?** If yes, symmetric fairness rules apply on top of PvE tuning.
- **Telemetry available:** per-unit pick rate, win rate, damage share, stage attempts, death causes.

## Method

1. **Choose the damage formula family before any number.** Subtractive formulas collapse under power creep; pick divisive or ratio for any game with long progression (table below).
2. **Set TTK and TTD targets per enemy role**, as a band at p50 power, and the TTD/TTK ratio per encounter. These are the design; every stat is derived from them.
3. **Write the effective DPS equation with every term**: base, attack rate, crit expectation, accuracy, uptime, armor, penetration, targets hit. A sheet that omits uptime overstates DPS by 30–50% (heuristic) and ships sponge enemies.
4. **Derive HP and armor from the target TTK**, not the other way round. `EHP_target = TTK_target × DPS_eff(p50)`. Then split EHP into HP and armor by role: armored roles reward penetration builds, high-HP roles reward sustained DPS.
5. **Check discrete hits-to-kill.** Continuous TTK lies when hits are few. `HTK = ceil(EHP / dmg_per_hit)`. A one-point damage change that crosses an HTK boundary moves TTK by a whole attack interval.
6. **Spec timing in milliseconds, store it in sim ticks.** Every enemy attack gets windup, active, recovery, and a telegraph; every player attack gets startup, active, recovery, cancel window, and buffer. Check the reaction budget (Quantitative Reference).
7. **Set hit/hurt box policy:** player hurtbox smaller than the art, player hitboxes generous, enemy hitboxes no larger than the art. Fairness is perceived, not computed.
8. **Budget every ability** as a percentage change in squad strength (DPS × EHP) so a stun, a shield, and a nuke can be compared on one axis. Read `references/genre-variants.md` when converting control and sustain into that budget.
9. **Build the enemy roster from an archetype matrix** and every encounter from a threat budget.
10. **Validate at p10, p50, p90 power.** The p90 player must not one-shot bosses; the p10 player must clear the gate within the designed attempt count.
11. **Run a dominance sweep** on units and abilities from telemetry; fix outliers by the term that is out of line, not by a blanket damage nerf.
12. **Write the Balance Change Note** with the predicted TTK/win-rate shift and the metric that falsifies it.

## Deliverables

### 1. Combat Balancing Sheet

```
SHEET A — UNITS (one row per hero/unit/enemy)
ID │ Role │ HP │ Armor A │ k(level) │ DR =A/(A+k) │ EHP =HP·(1+A/k) │ Base dmg │ Atk/s │ Crit c │ Crit m │
   │ Exp/hit =dmg·(1+c(m−1)) │ Accuracy │ Uptime │ Targets │ DPS_eff │ Range │ Move speed │ Tags

SHEET B — MATCHUPS (attacker × defender matrix at p10/p50/p90 power)
Attacker │ Defender │ Dmg/hit after DR │ HTK =ceil(EHP/hit) │ TTK_cont =EHP/DPS_eff │ TTK_disc │ Target band │ Verdict

SHEET C — ENCOUNTERS
Encounter │ Enemies (count×archetype) │ Threat pts │ Budget │ Incoming DPS_eff │ Player EHP │ TTD │ TTK_total │ TTD/TTK │ Target │ Verdict

SHEET D — ABILITIES
Ability │ Owner │ Cooldown │ Cost │ Dmg │ Targets exp. │ CC s │ Shield │ Value/cycle │ DPS-equiv │ Budget │ Δ%

SHEET E — TELEMETRY (filled weekly)
Unit │ Pick % │ Win % │ Win % excluded │ Δ │ Damage share │ Avg power │ Verdict (OP / healthy / niche / dead)
```

Every DPS cell references accuracy and uptime columns, and DPS_eff is pre-armor (armor lives in EHP). A literal `1.0` in either is a modeling error unless the attack truly cannot miss and the unit never stops attacking.

### 2. Ability Spec

```
ABILITY:        [name]                 OWNER: [hero/enemy]     ROLE: [nuke / DoT / CC / sustain / mobility / utility]
FANTASY:        [one sentence the player should feel]
INPUT:          [tap / hold / drag-aim / auto-cast at full energy]   TARGETING: [auto nearest / lowest HP / aimed cone 40° / AoE r=2.5 m]
COST:           [cooldown s | energy | mana]    CHARGES: [n]
NUMBERS:        dmg = [coef] × ATK  | crit allowed: [Y/N] | pen: [flat/% ] | targets expected: [n]
CC / BUFF:      [type, duration s, diminishing returns rule]
TIMING (ms):    startup [ ] | active [ ] | recovery [ ] | cancel-into [list] from [ms] | buffer [ms]
TELEGRAPH:      [what the opponent sees, earliest ms before impact]
COUNTERPLAY:    [dodge / block / interrupt / out-range / cleanse] — at least one
BUDGET:         DPS-equivalent = [value] vs role budget [value] → [±%]
INTERACTIONS:   [what it must not combo with; known degenerate loops]
TELEMETRY:      [cast, hit, kill, wasted-cast events]
```

### 3. Enemy Archetype Matrix

Ratios are relative to fodder at the same level. **Heuristic starting points**, tuned per game.

| Archetype | HP × | Dmg/hit × | Speed | Threat it creates | Counterplay taught | Telegraph | Per encounter |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Fodder | 1 | 1 | normal | attrition, surround | AoE, positioning | minimal | 4–12 |
| Rusher / flanker | 0.8–1.2 | 1.5–2 | fast | closes distance, breaks kiting | dodge timing, target priority | 300–500 ms | 1–4 |
| Brute / tank | 4–8 | 2–3 | slow | blocks lanes, heavy hits | spacing, punish recovery | 600–900 ms | 1–2 |
| Ranged / artillery | 0.6–1 | 1–1.5 | slow | zones the arena | close in, cover | 500–800 ms + ground marker | 1–3 |
| Support / healer | 1–1.5 | 0.3–0.5 | normal | extends fight, buffs others | focus fire, interrupt | cast bar | 0–1 |
| Summoner | 1.5–2 | 0.5 | slow | spawns adds over time | rush the source | cast bar | 0–1 |
| Shielded / armored | 2–4 (high A) | 1–1.5 | normal | punishes low-pen builds | penetration, break mechanic | shield VFX | 0–2 |
| Elite | 8–15 | 2–4 | varies | 2 of the above combined | learned counterplay, combined | per move | 0–1 |
| Boss | 40–120 per phase | 3–6 | varies | phase checks (DPS, mechanic, endurance) | everything taught so far | per move, readable | 1 |

Rule: introduce each archetype alone, then pair it with one known archetype, then remix. A new archetype first seen inside a mixed pack teaches nothing.

### 4. Encounter Budget

```
Threat pts per archetype = (HP× · Dmg×)^0.5 × modifier (rusher 1.2, support 1.5, summoner 1.5)   [heuristic]
Encounter budget(level) = base_budget × (player_power(level) / player_power(1))
Encounter check:  TTD / TTK_total in target band (below); no single enemy > 50% of budget except elite/boss beats
```

### 5. Balance Change Note

`Unit/ability │ Observed (pick %, win %, TTK) │ Term out of line │ Change │ Predicted effect │ Falsifying metric │ Re-measure date`. One line per change. A change without a falsifying metric is a guess.

## Quantitative Reference

### Damage formula families

| Family | Formula | Behavior | Use when |
| --- | --- | --- | --- |
| Subtractive | `dmg = ATK − DEF` (floor 1) | Cliff: below DEF the attack is useless; small DEF gains erase weak attackers | Short games, board-game clarity, < 20 power levels |
| Divisive (armor) | `dmg = ATK × k/(k + A)` | Smooth; never zero; each armor point adds the same EHP | Default for long progression and RPGs |
| Ratio | `dmg = ATK² / (ATK + DEF)` | Equal ATK and DEF halves damage; self-scaling with level | Stat-on-stat RPGs where both sides grow together |
| Percent-max-HP | `dmg = p × HP_max` | Scales with target, ignores progression | Boss mechanics, anti-tank tools; cap it |

**Armor:** `DR = A/(A + k)`, so `EHP = HP/(1 − DR) = HP × (1 + A/k)`. EHP is **linear** in armor: every point adds HP/k EHP. The displayed DR% shows diminishing returns; the survival value does not. Scale `k` with level (for example `k = 5 × level + 250`, heuristic) or late-game armor makes everything immortal.

**Penetration:** apply flat pen, then percent pen, to A before the formula: `A_eff = max(0, (A − flat) × (1 − pct))`. Flat pen is strongest against low-armor targets, percent against high — give each to different roles.

**Crit:** `E[dmg] = dmg × (1 + c × (m − 1))`. At c = 0.25, m = 2.0 the multiplier is 1.25. Cap c at 0.75–1.0 and price crit damage so that `(1 + c(m−1))` per stat point stays within 10% of the flat-ATK value per point; otherwise crit stacking becomes the only build.

**Effective DPS (pre-armor):** `DPS_eff = E[dmg] × atk_rate × accuracy × uptime × targets_hit`.

**Time to kill:** `TTK = EHP / DPS_eff = HP / (DPS_eff × (1 − DR))` (continuous). Apply armor once: either against EHP or against damage, never both. Discrete: `HTK = ceil(HP / dmg_after_DR)`, `TTK = (HTK − 1)/landed_hits_per_s + first_hit_delay`. Report both when HTK ≤ 10.

**With healing:** `TTK = EHP / (DPS_eff − HPS_eff)`. If `HPS_eff ≥ 0.6 × DPS_eff` sustained, fights stall; add anti-heal, an enrage timer, or diminishing heal on repeated targets.

### TTK and TTD bands (heuristics; tune per game, validate in playtests)

| Target | Real-time mobile action | Turn-based (actions) | Auto-battler round |
| --- | --- | --- | --- |
| Fodder | 0.5–1.5 s (1–3 hits) | 1 action | — |
| Standard enemy | 2–4 s | 2–3 actions | — |
| Elite | 6–12 s | 4–6 actions | — |
| Boss phase | 20–60 s | 8–15 actions | — |
| Whole fight | 60–180 s stage | 3–6 rounds per wave | 20–40 s combat |
| Player TTD / encounter TTK | 2–4 early chapters, 1.2–2 for skill checks and bosses | same ratio in rounds | — |

TTD/TTK below 1.0 is a DPS check the p50 player fails; above 6 the encounter has no threat and players stop dodging.

### Frame data and reaction budget

1 frame = 16.7 ms at 60 Hz, 33.3 ms at 30 Hz. Design in ms; store in fixed sim ticks so a device dropping to 30 fps does not change hit windows.

| Element | Typical value (heuristic) | Why |
| --- | --- | --- |
| Visual reaction time, alert player | 200–250 ms | Below this an attack is unreactable; it can only be anticipated |
| Touch input latency added on mobile | 50–100 ms on top of display latency | Measure per device tier; budget the worst supported tier |
| Enemy telegraph, standard attack | ≥ 400 ms (mobile ≥ 500 ms) | Reaction + input + dodge startup must fit inside it |
| Enemy telegraph, boss heavy | 700–1,200 ms | Heavy hits must be readable, not memorized |
| Player light attack startup | 80–150 ms | Feels responsive; under 80 ms reads as instant |
| Player heavy attack startup | 250–450 ms | The cost that justifies its damage |
| Input buffer | 100–150 ms (6–9 frames at 60 Hz); 150–200 ms on touch | Swallowed inputs read as "unresponsive" |
| Dodge invulnerability | 150–300 ms | Shorter needs frame-perfect play; longer trivializes telegraphs |
| Hit-stop | light 40–70 ms, heavy 100–200 ms | Owned by `gamedev-game-feel-designer`; reserve it in the timeline |

**Reaction check:** `telegraph_ms ≥ reaction_ms + input_latency_ms + dodge_startup_ms + 100 ms margin`. With 250 + 80 + 66 + 100 = 496 ms, a 400 ms telegraph is not reactable on touch.

**Frame advantage:** `adv_on_hit = hitstun − (remaining_active + recovery)`. If `adv_on_block < −(fastest opponent startup)`, the move is punishable. Every heavy commit should be punishable; every light poke should not.

Read `references/frame-data-and-hitboxes.md` when writing frame tables, cancel rules, hitbox policy, or touch-control combat (virtual stick, auto-aim, one-thumb).

### Touch-control combat (summary, heuristics)

| Element | Starting spec | Failure it prevents |
| --- | --- | --- |
| Floating virtual stick | left 40% of screen, dead zone 10–15% of radius | Thumb drifting off a fixed stick |
| Auto-target priority | facing cone nearest → lowest HP% → last attacked; boss tap-selectable | Swinging at fodder while the healer lives |
| Soft lock / magnetism | cone 30–45°, 1.2× reach, slide ≤ 0.5 m on startup | Whiffs from imprecise touch aim |
| Skill buttons | 3–4 on a right-thumb arc, primary ≥ 64 pt | Mis-taps mid-fight |
| One-thumb move-or-attack | attack when stationary, move by drag | Two-thumb requirement in portrait |

In move-or-attack designs, enemy pressure sets player uptime: if less than ~40% of room time is safe to stand still, DPS uptime collapses and TTK balloons. Tune projectile density before damage numbers.

### Turn-based, speed, and auto-battler math (summary)

- **Speed systems:** a common form is action value `AV = K/SPD` (K = 10,000). Turns inside a window W: `floor(W/AV)`. Speed for n turns: `SPD ≥ K·n/W`. Speed is stepwise: between breakpoints it is worth zero, at a breakpoint it adds a whole turn of every effect the unit has. Price speed against breakpoints, not linearly.
- **Action economy:** a stun of duration d removes `d/AV` actions; value it at `target DPS × d × hit chance`. Hard CC chains must have diminishing returns (for example 100%, 50%, immune for 2 turns — heuristic).
- **Squad combat:** Lanchester square law for ranged/all-can-target fights: team strength `∝ N² × DPS × HP`. Melee-only frontage approaches the linear law (`∝ N`). Doubling unit count beats doubling per-unit stats.
- **Auto-battler star-ups** at ×1.8 HP and damage give ×3.24 strength per slot (1.8²); a 3-copy merge is worth it only if the per-slot gain beats the slot it frees.

Read `references/genre-variants.md` when designing turn order, auto-battler synergies, idle/auto-battle RPG combat, or real-time mobile controls; it holds two more worked examples.

### Unit balance KPIs (heuristics)

| Metric | Healthy | Investigate | Act |
| --- | --- | --- | --- |
| Unit win rate at matched power/MMR | 47–53% | 45–47 or 53–55% | < 45% or > 55% |
| Pick rate | 0.5–2× median of role | 2–3× | > 3× median, or present in > 60% of top teams |
| Std-dev of unit win rates | ≤ 2.5 pp | 2.5–4 pp | > 4 pp |
| Win % included minus excluded | ≤ 3 pp | 3–6 pp | > 6 pp |
| Damage share of one unit in its team | ≤ 35% | 35–50% | > 50% |

Win rate alone lies: a niche unit picked by experts shows 58% on 2% pick. Control for player power and skill (compare at matched MMR or power bracket) before nerfing. In gacha rosters, raw pick rate tracks ownership — normalize by owners.

## Worked Example — "Ashen Vale", hybrid real-time mobile RPG

Chapter 5 elite "Shieldwarden". Target TTK 8–12 s for a p50 hero; target TTD/TTK 2–4.

**Shipped values.** HP 1,200, armor 300, `k = 500`. `DR = 300/800 = 0.375`, `EHP = 1,200 × 1.6 = 1,920`. Hero: 80 dmg, 1.25 atk/s, crit 20% × 2.0 → `E[dmg] = 80 × 1.2 = 96`, raw DPS 120. The design sheet assumed accuracy and uptime of 1.0 → `TTK = 1,920 / 120 = 16 s`, already over band. Measured in build: accuracy 0.85, uptime 0.70 (the 1.4 s shield-raise cycle blocks melee). `DPS_eff = 120 × 0.85 × 0.70 = 71.4` → **TTK = 1,920/71.4 = 26.9 s**, 2.7× the band midpoint. Playtests showed players walking away from it.

**Fix by term, not by blanket nerf.** Shorten shield-raise so uptime rises to 0.80 → DPS_eff 81.6. Derive EHP from the target: `10 s × 81.6 = 816`. Keep the armored identity with lower values: HP 600, armor 180 → `EHP = 600 × 1.36 = 816`. Discrete check: `DR = 180/680 = 0.265`, dmg/hit 70.6, `HTK = ceil(600/70.6) = 9`, landed hits/s = `1.25 × 0.85 × 0.80 = 0.85` → **TTK ≈ 10.6 s**, in band.

**Threat side.** Player HP 1,500, armor 250 → EHP 2,250. Elite hit 140 every 2.5 s, p50 dodge success 50% → 28 DPS → **TTD 80 s, TTD/TTK = 7.5**: a sponge, not a threat. Raise the hit to 280 with a 600 ms telegraph (passes the 496 ms reaction check) → 56 DPS → TTD 40 s, **ratio 3.8**. Players who dodge are rewarded; players who don't now notice.

## Diagnostics

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Late-game hits deal 1 damage, or one-shot | Subtractive formula under power creep | Move to divisive/ratio; rescale k with level |
| Measured TTK 1.5–3× the sheet | Uptime/accuracy assumed 1.0; HTK boundary crossed | Measure both; derive EHP from target TTK |
| One unit in > 60% of top teams | One term (speed, crit, AoE targets, CC uptime) underpriced | Find the term in Sheet D; nerf that term, not base damage |
| Fights stall, never end | HPS ≥ 0.6 × DPS sustained, or shields regenerate | Anti-heal, enrage timer, diminishing heals |
| "Unfair" deaths reported, no damage spike in logs | Telegraph under reaction budget, or hitbox larger than art | Run the reaction check; shrink enemy hitboxes to art |
| "Unresponsive" / swallowed inputs | No input buffer, long recovery, no cancel window | 100–200 ms buffer; cancel into dodge from active frames |
| Hit windows change on low-end devices | Combat logic tied to render frame rate | Fixed-tick sim; frame data in ticks |
| Players never dodge or block | TTD/TTK > 6, or dodge has no reward | Raise enemy threat; add punish windows after dodges |
| Bosses melted by p90, walled at p10 | Boss tuned at mean power; power spread too wide | Validate at p10/p90; add DPS floors and phase gates, % HP mechanics |
| Speed meta dominates PvP | Speed priced linearly, breakpoints ignored | Price by breakpoints; add speed-independent turn effects |
| Auto-battle clears what manual play cannot | Enemy AI targeting exploitable or manual skills under-budgeted | Fix target priority; raise manual ability budget 10–20% (heuristic) |
| Mobile players miss melee hits constantly | No aim assist, cone too narrow for touch | Soft-lock cone 30–45°, magnetism on attack startup |

## Anti-Patterns

**The Subtractive Cliff** — `ATK − DEF` in a game with 100 power levels. Mid-game armor upgrades zero out entire enemy classes, and the formula has to be rewritten live.

**The Perfect-Uptime Spreadsheet** — DPS computed without accuracy and uptime. Every enemy ships 30–50% spongier than designed, and the fix applied is a damage buff that breaks PvP.

**The Damage Sponge** — difficulty raised by HP alone. TTK grows, threat does not, and TTD/TTK drifts past 6: long, safe, boring.

**The Unreactable Telegraph** — a 300 ms windup on a touch device. It cannot be reacted to, only memorized, and it reads as cheap death.

**The Frame-Coupled Combat** — hit windows in render frames. Thermal throttling to 30 fps doubles timings and changes balance per device.

**Speed Is Free** — speed priced like any other stat. It multiplies every effect a unit has and hides behind breakpoints until the PvP meta is all speed.

**The Blanket Nerf** — base damage cut on a unit whose real problem was AoE target count or CC uptime. The unit dies in its intended role and stays dominant in the broken one.

**The Healer Stalemate** — sustain that matches damage. Fights end on timeouts, and the team composition meta becomes "two healers".

**The Mixed-Pack Introduction** — a new archetype first met alongside three others. The player dies without learning which enemy did what.

## Quality Checklist

- [ ] Damage formula family chosen and justified against progression length; k scales with level
- [ ] TTK and TTD bands set per archetype and per encounter at p50, with TTD/TTK targets
- [ ] Every DPS cell includes crit expectation, accuracy, uptime, and targets hit; armor applied exactly once
- [ ] Accuracy and uptime are measured from a build (build number recorded), not assumed
- [ ] HTK checked wherever HTK ≤ 10; no unintended HTK boundary within ±5% tuning range
- [ ] Every enemy attack passes the reaction check on the slowest supported touch device
- [ ] Combat runs on a fixed tick; frame data stored in ticks and documented in ms
- [ ] Input buffer and at least one cancel-into-dodge window exist for the player
- [ ] Hitbox policy written: player hurtbox smaller than art, enemy hitbox no larger than art
- [ ] Every ability has a spec with timing, counterplay, and a DPS-equivalent budget within ±10%
- [ ] Each archetype introduced alone before appearing in mixed packs
- [ ] Encounters validated at p10, p50, p90 power
- [ ] Sustained HPS < 0.6 × DPS in every fight, or an enrage/anti-heal exists
- [ ] Speed priced against breakpoints; CC has diminishing returns
- [ ] Unit win rates 45–55% at matched power; no unit in > 60% of top teams
- [ ] Every balance change has a predicted effect, a falsifying metric, and a re-measure date

## Related Skills

- `gamedev-game-feel-designer` — hit-stop, shake, particles and haptics inside the windows this skill reserves; hand off once frame data is locked.
- `gamedev-pvp-designer` — when units are balanced for PvP ladders, matchmaking, or P2W limits; this skill supplies the unit KPIs.
- `gamedev-netcode-engineer` — rollback, prediction and lag compensation for real-time PvP; give them frame data and hitbox specs.
- `gamedev-meta-progression-designer` — the power curve that this skill converts into TTK; agree p10/p50/p90 power per chapter. If installed, `game-economy-balancer` prices that power.
- `gamedev-campaign-designer` — difficulty curve and boss gates across chapters; this skill tunes each encounter to that curve.
- `gamedev-level-layout-designer` — arena space, cover, sightlines that change ranged and melee value.
- `gamedev-hud-engineer` — damage numbers, telegraph markers, cast bars, health bars.
- `gamedev-anti-cheat-security` — server-side damage validation when combat results grant rewards or rank.
- If installed, `core-loop-designer` (where combat sits in the loop), `game-playtest-analyst` (feel scores, death-cause coding), `mobile-game-ux-designer` (thumb reach for skill buttons), `game-prototype-planner` (greybox combat spikes before content).
