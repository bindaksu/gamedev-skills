# Genre Variants: Turn-Based, Auto-Battler, Auto-Battle RPG, Ability Budgets

Read when designing turn order or speed systems, auto-battler boards and synergies, power-score-driven auto-battle RPG combat, or when comparing abilities of different types (damage vs control vs sustain) on one budget. Numbers marked heuristic are starting points to validate, not standards.

## 1. Ability budget on one axis

Damage dealt, damage prevented, and healing are different currencies. Convert them through the squad-strength identity: under the Lanchester square law a team's fighting strength is proportional to `DPS × EHP` (times N²), so a **1% increase in own DPS is worth the same as a 1% reduction in enemy DPS or a 1% increase in own EHP**. Express every ability as a percentage strength change.

```
Damage ability:   Δ% = (dmg × expected_targets / cooldown) / own_team_DPS
Control ability:  Δ% = (target_DPS × duration × hit_chance / cooldown) / enemy_team_DPS   (+ interrupt value if it cancels casts)
Shield / heal:    Δ% = (amount × efficiency / cooldown) / enemy_team_DPS               (efficiency 0.6–0.8 heuristic: overheal, expiry)
Buff / debuff:    Δ% = buff_% × uptime × share_of_team_affected
```

**Worked example.** Team DPS 2,000; enemy team DPS 1,500.

| Ability | Inputs | Per-cycle value | Δ% strength |
| --- | --- | --- | --- |
| Meteor (nuke) | 4.0 × ATK 500 = 2,000 dmg, 2.5 targets, cd 12 s | 5,000 / 12 = 417 DPS | **+20.8%** |
| Shield Bash (stun) | Enemy carry 600 DPS, 2 s, hit 0.9, cd 10 s | 108 DPS denied | **+7.2%** |
| Bulwark (shield) | 1,800 shield, eff 0.7, cd 15 s | 84 HPS | **+5.6%** |

With a budget of roughly +8–12% per active ability slot (heuristic), Meteor is ~2× over budget. The fix is the term that is out of line: expected targets 2.5 is high because enemies spawn clustered — reduce the radius or the coefficient, not the cooldown (the cooldown sets rhythm, which is a feel decision).

Caveats: control abilities gain extra value against burst (interrupting a 3,000-damage cast is worth more than its DPS share) and lose value against immune bosses; record those as separate rows rather than fudging the coefficient.

## 2. Turn-based and speed systems

### Fixed-round initiative
Everyone acts once per round in initiative order. Speed only decides order, so its value is the **first-strike value**: in a fight lasting R rounds where the faster side can kill before the slower acts in the last round, going first is worth roughly one extra action — about `1/R` of total output. Short fights (R ≤ 3) make initiative decisive; long fights make it a tiebreaker.

### Speed / action-value (ATB-style)
A common form: each unit has action value `AV = K / SPD` (K = 10,000). The unit with the lowest remaining AV acts, then its AV resets to `K / SPD`. Turns inside a window W: `floor(W / AV)` (first action at AV). Speed needed for n turns: `SPD ≥ K × n / W`.

**Worked example — breakpoints.** First-cycle window W = 450 AV.

| Turns in W | Required SPD | Note |
| --- | --- | --- |
| 4 | ≥ 88.9 | base heroes at 90–100 get 4 |
| 5 | ≥ 111.2 | 112 SPD gets a fifth turn |
| 6 | ≥ 133.4 | 134 SPD gets a sixth turn |

A hero at 112 and a hero at 133 take the same number of turns in the window. 21 points of speed are worth **zero** there, and the next point is worth a whole turn — 20% more of everything that hero does (damage, buffs, CC). Consequences:
- Price speed substats by breakpoint: show players the next breakpoint, or quantize speed sources so that each source moves one breakpoint.
- Turn manipulation ("advance forward 30%", "delay 20%") is speed in disguise; budget it as `AV shifted / AV per turn` turns.
- PvP speed races resolve on ties; define tie-breaking explicitly (higher base speed, then position) and make it visible.

### Action economy and CC
- A hard stun of one turn on a unit that acts every AV removes exactly one action; on a fast unit it is worth more per cast than on a slow one.
- Chain-CC must have diminishing returns (for example: full, then 50% duration, then immune for 2 turns — heuristic) or teams lock enemies out of the fight.
- Effect resistance vs effect hit: `p(land) = clamp(base × (1 + hit − res), floor, cap)`, with a floor around 0.15 and cap around 0.85 (heuristic) so neither side reaches certainty.

### Fight length
Target 3–6 rounds per wave and 2–3 waves per stage for mobile turn-based RPGs (heuristic). Under 2 rounds, team composition stops mattering — whoever acts first wins. Over 8 rounds, auto-battle becomes mandatory and players stop watching.

## 3. Auto-battlers (board and synergy)

### Squad strength
Lanchester square law, all-can-target (ranged-heavy boards): side A beats side B if `α·A₀² > β·B₀²`, with `α = DPS_A / HP_B` and `β = DPS_B / HP_A` per unit. Survivors: `A_end = sqrt(A₀² − (β/α)·B₀²)`. Melee boards with limited frontage behave closer to the linear law (`α·A₀ vs β·B₀`).

**Worked example.** A: 6 units, 50 DPS, 800 HP. B: 5 units, 60 DPS, 900 HP.
`α = 50/900 = 0.0556`, `β = 60/800 = 0.075`. `α·36 = 2.00` vs `β·25 = 1.875` → **A wins** with `sqrt(36 − 1.35 × 25) = sqrt(2.25) = 1.5` units left, despite every B unit being stronger (product 54,000 vs 40,000). Count beats quality under the square law — which is why board slots (level-gated unit count) are the strongest progression lever in an auto-battler, and why it must be priced the highest.

### Star-ups and merges
If a 2-star has ×1.8 HP and ×1.8 DPS (heuristic, common in the genre), its strength per slot is 1.8² = **3.24×**. A 3-star at ×3.24 stats is 10.5× per slot. Star-up must beat the slot opportunity cost: merging three 1-stars (strength 9 if all fielded under N²) into one 2-star (3.24) is only right when slots are full — which is exactly the decision the genre wants. If star multipliers rise above ~2.0, the decision disappears (always merge).

### Synergy (trait) tiers
- Tiers at 2/4/6 (or 3/6/9) units of a trait. Value per tier should rise **super-linearly** to reward commitment but stay below the value of the slots spent: a 6-trait bonus should be worth about 1.5–2.5 extra units of strength at that stage (heuristic).
- Every trait needs a counter-trait or a positional answer; log trait win rate when present at top tier, and flag any trait above 55% top-4 rate at matched MMR.
- Shop odds per tier and pool size per unit define how contested a composition is; contested comps should be stronger on paper to compensate.

### Round length
Combat 20–40 s, planning 25–35 s (heuristic). Mobile auto-battlers trend shorter; very short combats increase variance and make positioning less legible.

## 4. Power-score auto-battle RPG combat (idle / AFK-style)

When combat is fully automated, the player experiences combat as **a power check**. The design surface is the win-probability curve against the power ratio.

```
p(win) = 1 / (1 + (CP_enemy / CP_player)^s)          [heuristic logistic form]
```

| CP ratio player/enemy | p(win), s = 8 |
| --- | --- |
| 0.9 | 0.30 |
| 1.0 | 0.50 |
| 1.1 | 0.68 |
| 1.2 | 0.81 |

- Fit `s` from telemetry (logistic regression of win on log CP ratio). Large s (≥ 12) means composition and skill do not matter — combat is decorative. Small s (≤ 4) means power purchases feel unreliable.
- The combat power (CP) number is a weighted stat sum; weights must be refit when new stats or mechanics ship, or CP stops predicting outcomes and players lose trust in it.
- Stage gates should sit where p50 players are at a CP ratio of 0.9–1.0 on first attempt (heuristic): a near-miss that the next upgrade resolves. That gate pacing is shared with `gamedev-meta-progression-designer`.
- Composition matters only if counters move the effective ratio by more than ~10% (heuristic); otherwise CP alone decides and team-building is fake depth.

## 5. Real-time mobile action — summary

Covered in `frame-data-and-hitboxes.md`: virtual stick, soft lock, target priority, one-thumb move-or-attack, reaction budget on touch. The key genre number is uptime: in move-or-attack designs, enemy pressure sets uptime, so tune projectile density and safe-stand time before touching damage numbers.
