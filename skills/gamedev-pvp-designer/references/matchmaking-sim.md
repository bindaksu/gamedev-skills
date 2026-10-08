# Matchmaking Simulation Reference

Read when sizing queues, choosing a widening schedule, or proving a ranked design converges before launch. The closed-form fill estimate in SKILL.md is first-order; this harness replaces it with real arrival curves.

## 1. Population math

```
arrivals/s per queue  = DAU x pvp_share x matches_per_player_day / (active_hours x 3600) x peak_factor
f(window, R)          = Phi((R + w - mean)/sd) - Phi((R - w - mean)/sd)
expected wait         = (N - 1) / (arrivals/s x f)
players waiting       = arrivals/s x mean wait          (Little's law)
```

Peak factor (heuristic): mobile evening peak is often 1.5-2.5x the daily mean; trough 0.2-0.4x. Use the trough for the top-bracket test.

Split cost: every independent split (mode, region, party bucket, platform) divides arrivals. Two equal duo/solo queues double the top-bracket wait; four modes quadruple it. Before adding a queue, recompute the top 0.5% wait at trough with the new split.

## 2. Discrete-event queue harness (Python)

```python
import random, statistics as st

def simulate(arrivals_per_s, n_per_match, mmr_mean=1500, mmr_sd=300,
             w0=50, widen=25, step_s=5, cap=250, hours=4, seed=7):
    rng = random.Random(seed)
    t, end = 0.0, hours * 3600
    pool = []                      # (join_time, mmr)
    waits, gaps = [], []
    def window(waited):
        return min(cap, w0 + widen * int(waited // step_s))
    while t < end:
        t += rng.expovariate(arrivals_per_s)
        pool.append((t, rng.gauss(mmr_mean, mmr_sd)))
        # oldest players first: they have the widest windows
        pool.sort()
        for anchor in list(pool):
            w = window(t - anchor[0])
            near = [p for p in pool if abs(p[1] - anchor[1]) <= w]
            if len(near) >= n_per_match:
                near.sort(key=lambda p: abs(p[1] - anchor[1]))
                match = near[:n_per_match]
                for p in match:
                    pool.remove(p)
                    waits.append(t - p[0])
                ratings = sorted(p[1] for p in match)
                gaps.append(ratings[-1] - ratings[0])
                break
    q = lambda xs, p: st.quantiles(xs, n=100)[p - 1]
    return {"wait_p50": q(waits, 50), "wait_p90": q(waits, 90),
            "spread_p50": q(gaps, 50), "spread_p90": q(gaps, 90)}
```

Notes:
- Re-scan on a timer as well as on arrival in production; the harness only re-scans on arrival, which overstates waits at very low traffic.
- Segment the outputs by anchor rating decile; the global p90 hides the top bracket.
- Feed the real hourly arrival curve instead of a constant rate to test the trough.
- Add team partitioning (minimize mean gap) after selection and record P(favored) per match.

## 3. Rating convergence harness

Generate 10,000 synthetic players with true skill ~ Normal(1500, 300). Outcome model: `P(A wins) = 1/(1 + 10^((true_B - true_A)/400))`, optionally flattened by a noise factor that matches the measured win rate at a 200-point gap. Start everyone at the default rating, run the matchmaker and rating updates for 200 games each, and record:

- Games until `|rating - true| < 100` for 90% of players (target: placement + ~20, heuristic).
- Visible-rank error vs true skill at games 10, 25, 50.
- Point inflation: mean visible points over time.
- Smurf scenario: insert 2% of players with true skill +600 above their seed; count games until they leave the bottom two tiers, and the number of matches they spoil on the way.

## 4. Widening schedule, worked

Using the Normal(1500, 300) population and 3v3 (5 others):

| Anchor | Window | f | Wait at 10/s | Wait at 1/s |
| --- | --- | --- | --- | --- |
| Median | +-100 | 0.261 | 1.9 s | 19 s |
| Top 0.5% (2273) | +-100 | 0.0106 | 47 s | 472 s |
| Top 0.5% | +-300 | 0.0573 | 8.7 s | 87 s |

Reading: the median never needs to widen; the top bracket needs the cap at trough. A schedule that widens identically for everyone degrades median quality for no gain. Prefer a rating-aware schedule (heuristic): widen faster where f is small, e.g. `widen_per_step = base x clamp(0.26 / f(anchor, w0), 1, 4)`.

## 5. Live dashboard fields

```
queue | region | hour | anchor_decile | matches | wait_p50 | wait_p90 | P(favored)_p50 | P(favored)_p90
stomp_rate (score margin above mode threshold) | leaver_rate | bot_share (casual only) | cross_region_share
```
