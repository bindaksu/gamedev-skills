# Meta Progression Math — deep reference

Read when you need the exact completion math for random collections, a duplicate-conversion simulation, shard-ladder tables by rarity, gear rarity scaffolds, the power-vs-win-rate fit, or a renovation area generator. Every parameter table here is a **heuristic starting scaffold**, not a measured figure from any named game. Replace with build telemetry before committing.

## 1. Collections: coupon-collector math

### Equal odds

Expected draws to complete a set of n equally likely items:

```
E[T] = n · H_n,   H_n = 1 + 1/2 + ... + 1/n ≈ ln n + 0.5772
Var[T] ≈ (π² / 6) · n²   (for large n)
```

| n | E[T] | Rough p90 (simulate to confirm) |
| --- | --- | --- |
| 6 | 14.7 | ~23 |
| 9 | 25.5 | ~38 |
| 12 | 37.2 | ~55 |
| 20 | 72.0 | ~104 |

The last item alone costs `n` draws on average — the final 1/n of the set is as expensive as the first half.

### Unequal odds (rarity tiers)

```
E[T] = ∫₀^∞ ( 1 − Π_i (1 − e^(−p_i · t)) ) dt
```

Lower bound: `E[T] ≥ 1 / min(p_i)`. If the rarest item has p = 1/55, no amount of tuning the common items brings mean completion under 55 draws.

```python
import math

def expected_completion(weights, dt=0.01, t_max=10_000):
    total = sum(weights)
    probs = [w / total for w in weights]
    t, acc = 0.0, 0.0
    while t < t_max:
        prod = 1.0
        for p in probs:
            prod *= 1.0 - math.exp(-p * t)
        acc += (1.0 - prod) * dt
        if prod > 0.999999:
            break
        t += dt
    return acc

print(expected_completion([5, 5, 5, 3, 3, 3, 1.5, 1.5, 0.5]))  # ~64 draws
```

### Duplicate conversion and last-item purchase

Analytic forms get ugly; simulate. Rule modeled: each duplicate yields 1 unit of dupe currency; once only one item is missing, D units buy it.

```python
import random

def simulate(weights, dupes_for_last, trials=20_000):
    n = len(weights)
    results = []
    for _ in range(trials):
        have, dust, draws = set(), 0, 0
        while len(have) < n:
            draws += 1
            card = random.choices(range(n), weights=weights)[0]
            if card in have:
                dust += 1
            else:
                have.add(card)
            if len(have) == n - 1 and dust >= dupes_for_last:
                break
        results.append(draws)
    results.sort()
    return sum(results) / trials, results[int(0.9 * trials)]
```

Reference run, weights `[5,5,5,3,3,3,1.5,1.5,0.5]`:

| Rule | Mean draws | p90 draws |
| --- | --- | --- |
| No conversion | 63 | 123 |
| 60 dupes buy last item | 48 | 68 |
| 30 dupes buy last item | 36 | 42 |
| 20 dupes buy last item | 31 | 42 |

Pattern: conversion cuts p90 far more than the mean. Tune D so p90 completion fits inside the album window, then stop — below that, the rare tier loses meaning.

### Album-level targets (heuristic)

| Metric | Target |
| --- | --- |
| Album length | 4–8 weeks |
| Sets per album | 8–20 |
| p50 engaged player | completes 50–70% of sets |
| Top 10–20% engaged | completes the album |
| Sets completed by nobody in soft launch | 0 — every set must be completable at p90 within the window |
| Untradeable tier | the rarest 1–2 items per set if trading exists, so trading accelerates but does not short-circuit completion |

## 2. Hero roster and shard ladders

### Days to max

```
shards_per_day_for_hero = S_random / H + S_targeted + S_wildcard
days_to_max             = cumulative_ladder / shards_per_day_for_hero
```

### Scaffold by rarity (heuristic)

| Rarity | Pool H | Ladder (unlock, 2-star..5-star) | Cumulative | Random/day (rarity) | Targeted + wildcard/day | Days to max | Random-only days |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Rare | 16 | 10, 10/20/30/40 | 110 | 16 | 2 | 37 | 110 |
| Epic | 24 | 10, 20/30/50/80 | 190 | 12 | 6 | 29 | 380 |
| Legendary | 10 | 20, 30/50/80/120 | 300 | 2 | 2 | 136 | 1,500 |

Reading the table: random-only accrual is always the failure; the targeted column is the design lever. A legendary taking ~4–5 months for p50 F2P is a deliberate long goal, but only if the player chooses which legendary.

### Roster size rules

- **Useful roster** = team size × 2–3.
- **Pool growth** ≤ 1–2 heroes per month per rarity once live; each addition dilutes random shards by `H/(H+1)`.
- **Release power ceiling:** new hero ≤ 5–10% above the best same-role hero; prefer new mechanics (counters, synergies) over raw stats.
- **Retirement path:** heroes that fall out of use need an upgrade pass or a role in a mode (e.g. a counter in one event) before new heroes ship.

## 3. Gear scaffold

| Rarity | Base stat multiplier | Upgrade cap | Drop weight (main source) | Typical acquisition |
| --- | --- | --- | --- | --- |
| Common | 1.0 | 10 | 55% | every run |
| Uncommon | 1.3 | 20 | 28% | most runs |
| Rare | 1.7 | 30 | 12% | daily |
| Epic | 2.2 | 40 | 4% | weekly |
| Legendary | 2.8 | 50 | 1% | event / long-goal |

Rules:
- Set bonus (2-piece + 4-piece) = 8–15% of set stat budget.
- Gear level ≤ hero level (or account level).
- Salvage returns 50–80% of upgrade investment when the player replaces an item; below 50% players refuse to swap gear, which kills the drop loop.
- Reforge/reroll is an optional sink with deterministic fallback (pity) after N rolls.

## 4. Power score and the power-vs-win-rate fit

### Power score

```
P = Σ_axis w_axis · stat_axis      (weights agreed with combat design)
```

The weights are correct only if P predicts outcomes. Validate with the fit below; if two players with equal P have materially different win rates against the same content, the weights are wrong.

### Fit procedure

1. Log every attempt: player P, content recommended power R, outcome (win/loss), cohort day, spend tier.
2. Compute `ρ = P / R` and bin into 0.05-wide buckets.
3. Fit `logit(p_win) = k · ln(ρ) + b`.
4. If `b ≈ 0`, R is calibrated (ρ = 1 → 50%). If `b ≠ 0`, the recommended-power label is off: scale R by `e^(b/k)`.
5. `k` measures how decisive power is. High k (> 12): power decides everything, skill is irrelevant. Low k (< 4): power barely matters and power meta feels fake.

| ρ | p_win at k = 6 | k = 8 | k = 10 |
| --- | --- | --- | --- |
| 0.85 | 27% | 21% | 16% |
| 0.90 | 35% | 30% | 26% |
| 1.00 | 50% | 50% | 50% |
| 1.10 | 64% | 68% | 72% |
| 1.20 | 75% | 81% | 86% |

### Drift check

```
gap(c) = gap(0) · (g / q)^c
```

q = content recommended-power growth per chapter, g = p50 player power growth per chapter-equivalent of play time. With g/q = 0.97 over 20 chapters, the gap shrinks to 0.54 of where it started — p50 hits a wall. Keep g/q in 0.97–1.03 and re-fit every chapter from telemetry.

## 5. Account level target table

Pick the target level-by-day first; derive the XP curve from measured XP/day (hand the curve to economy).

| Cohort day | Target account level (example) | Level-ups that day |
| --- | --- | --- |
| 0 | 5 | 4–5 |
| 1 | 8 | 2–3 |
| 3 | 12 | 1–2 |
| 7 | 17 | ~1 |
| 14 | 22 | <1 |
| 30 | 28 | ~0.4 |
| 60 | 34 | ~0.2 |

```
XP_to_next(L) = XP_per_day(d at level L) / level_ups_per_day(d)
```

## 6. Renovation area generator

```python
def area_sheet(task_costs, stars_per_win, win_rate, attempts_per_session, sessions_per_day):
    total = sum(task_costs)
    attempts = total / (stars_per_win * win_rate)
    days = attempts / (attempts_per_session * sessions_per_day)
    avg_task_attempts = attempts / len(task_costs)
    return {
        "total_stars": total,
        "attempts": round(attempts, 1),
        "days_p50": round(days, 1),
        "attempts_per_task": round(avg_task_attempts, 1),
        "step_inside_one_session": avg_task_attempts <= attempts_per_session,
    }

print(area_sheet([1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 5, 5], 1, 0.55, 6, 2.5))
# total 35, attempts 63.6, days 4.2, 5.3 attempts per task -> True
```

Run the same sheet with p90 win rate and p90 sessions/day to get the frontier speed for the runway model.
