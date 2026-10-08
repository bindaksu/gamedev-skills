---
name: gamedev-simulation-designer
description: >-
  Design simulation mechanics that stay correct at every timescale: tick models,
  offline progress, production chains, agent and colony sims, determinism, and
  idle/incremental math including big numbers past 1e308. Use when designing an
  idle or incremental game's cost, bulk-buy, or prestige formulas, writing
  offline-earnings or catch-up math, balancing a production chain or hunting its
  bottleneck, building a city, colony, or agent sim that oscillates or deadlocks,
  needing deterministic replays or lockstep-safe sim rules, or when numbers show
  Infinity or offline gains disagree with online play.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: design
---

# Gamedev Simulation Designer

A simulation is a function from (state, elapsed time, inputs) to a new state, and the design is only correct if that function returns the same answer whether time arrives as sixty 16 ms frames, one 8-hour offline gap, or a replay on another device. Most sim bugs that players experience as "balance" problems are really timescale bugs: production that depends on frame rate, offline gains computed by a second formula, timers that drift in float32, a buy-max loop that freezes at level 4,000, or a double that becomes Infinity in week three. Decide the time model first, write every rate as a closed form you can integrate, and only then tune numbers.

## Role Profile

At top-grossing studios this work sits under the systems designer title rather than a "simulation designer" title. Scopely's Principal Systems Designer posting asks the role to "design and build core systems, including progression, combat scaling, economy, and rewards", to "build and maintain models, simulations, and tuning tools that define loot tables, costs, XP curves", and to "implement, tune, and iterate on systems directly in Unity" (https://hitmarker.net/jobs/scopely-principal-systems-designer-4669537). Zynga's senior designer posting bundles "systems, content, narrative, math, balancing, pacing" (https://www.builtinaustin.com/job/senior-game-designer/11321933). Habby gives its dev partners latitude to focus on the core loop (https://www.gamigion.com/?p=20716) and iterates one roguelite-plus-idle-meta formula across titles, which makes idle math a reusable studio asset, not a one-off.

- **Responsibilities:** time model and tick rate; offline/catch-up rules; production chain ratios; agent needs and decision rules; number representation; prestige/reset loop; tuning tools and sim harnesses.
- **Hard skills:** closed-form integration, geometric series, logarithms, queueing (Little's Law), spreadsheet plus Python simulation, enough engine scripting to implement and profile the rules.
- **KPIs (inferred from postings, not quoted):** time-to-milestone vs target pacing, D30+ retention, offline-return rate, sim CPU ms per frame, desync rate where determinism applies.
- **Collaborators:** engine architect (loop, save), backend (authoritative time), economy designer (curves and sinks), meta-progression, HUD (number display), QA (golden tests).

## When to Use / Not

Use for: idle/incremental math, offline progress, production chains, city/colony/farm builders, agent needs and utility AI rules, tick models, determinism contracts, big-number representation and notation.

Not for: currency faucet/sink ledgers, price ladders, and cost-curve span selection (if installed, `game-economy-balancer`); the outer meta layer of collections and account level (`gamedev-meta-progression-designer`); network sync, rollback, and lockstep transport (`gamedev-netcode-engineer`); engine loop and save-system architecture (`gamedev-engine-architect`); combat damage math (`gamedev-combat-designer`).

## Inputs to Gather

- **Genre and timescale** — active session length, expected offline gap distribution (p50/p90). Default: 6-minute sessions, 3 sessions/day, p90 gap 14 h.
- **Authority model** — client-only, server-validated, or server-authoritative. Default: server-authoritative time, client-predicted state.
- **Determinism need** — none, same-device replay, cross-platform replay, or lockstep. Default: same-device replay (cheap insurance for bug repro).
- **Number range** — largest value reachable at the end of the content plan. If it can exceed 9e15, integers are inexact in doubles; past 1.8e308 doubles overflow.
- **Entity counts** — agents, buildings, conveyor items at p90 late game. Default sim budget on mid-tier mobile: 2 ms per frame (heuristic; confirm with `gamedev-optimization-compatibility`).
- **Existing curves** — cost base and growth r, production per unit, multipliers, prestige formula. If missing, take r from the economy owner rather than inventing it.
- **Platform targets** — device tiers, background execution limits (assume the OS kills the app; never plan on background ticking).

## Method

1. **Classify each system by time model.** Fixed-step for anything with spatial interaction or feedback between agents; event-driven for timers and queues (crops, construction, research); analytic for anything that must cross offline gaps. One game usually uses all three; write the classification down per system.
2. **Store time as integer ticks or absolute timestamps.** `tick` as int64 and `time = tick * dt` never drifts. Timers store an absolute end time, never a decrementing countdown, so a paused or killed app cannot lose or gain time.
3. **Write every rate as a function, then integrate it.** For each resource write `dx/dt = f(state)`. If f is constant, polynomial in t, or exponential, use the closed form (Quantitative Reference). If it is not integrable, chunk the gap into N analytic sub-steps where state is re-evaluated (N = 32-128 is usually enough).
4. **Run online and offline through the same function.** Online play calls `advance(state, dt)` with a small dt; return-from-offline calls it with a large one. A separate offline formula is guaranteed to diverge as soon as someone adds a multiplier.
5. **Make the server the only clock.** `elapsed = max(0, serverNow - lastServerSave)`, clamp to the cap, apply efficiency. Hand clock-tamper detection to `gamedev-anti-cheat-security` and authoritative storage to `gamedev-backend-engineer`.
6. **Balance chains by ratio before by number.** Compute machines per stage from throughput; find the bottleneck as the stage with the lowest capacity per required unit; size buffers with Little's Law. Only then set costs.
7. **Choose number representation for the end of content, not launch.** If the plan reaches 1e100, adopt mantissa-exponent or log-space now; retrofitting a currency type touches every formula, save, and UI string.
8. **Replace every per-unit loop with a closed form.** Bulk buy, max affordable, and offline accrual must be O(1) in the count.
9. **Design agent decisions for the crowd, not the individual.** Score actions with utility curves, add reservations and jitter so 300 agents do not pick the same tile, and give each agent tier a decision frequency (LOD).
10. **Damp every feedback loop.** Any loop where output feeds back into its own rate with a delay will oscillate; add hysteresis bands, smoothing, or rate limits before playtest finds it.
11. **Write the determinism contract if replay or lockstep is required.** Seeded per-system PRNG, ordered iteration, fixed-point or audited float math, state hash every N ticks.
12. **Build a headless harness.** Run the sim for 30, 90, and 365 simulated days at accelerated speed under scripted player policies (idle-only, optimal, casual). Pacing claims without a harness run are guesses.

## Deliverables

### 1. Sim Spec (one per system)

```
SYSTEM:            [name]
TIME MODEL:        Fixed-step @ __ Hz / Event-driven / Analytic / Chunked-analytic (N=__)
STATE:             [fields, types, units, max value at end of content]
RATE FUNCTIONS:    dx/dt = ...   (one line per resource)
CLOSED FORM:       x(t) = ...    or "chunked, N=__, error bound __%"
OFFLINE:           cap __ h, efficiency __, extensions [upgrade / pass / ad]
AUTHORITY:         client / server-validated / server-authoritative
DETERMINISM:       none / same-device / cross-platform / lockstep
CPU BUDGET:        __ ms per frame at p90 entity count (__ entities)
GOLDEN TESTS:      online 8h == offline 8h within __%; replay hash at tick __
```

### 2. Production Chain Sheet

```
Stage │ Recipe (in → out)      │ Cycle s │ Out/s per machine │ Demand/s │ Machines = Demand ÷ Out/s │ Owned │ Capacity/s │ Util%
──────┼────────────────────────┼─────────┼───────────────────┼──────────┼───────────────────────────┼───────┼────────────┼──────
BOTTLENECK = argmin(Capacity_i ÷ Required_i per final unit)      Buffer_i ≥ Flow_i × Max interruption_i (s)
```

### 3. Offline Progress Spec

```
Elapsed source:     server timestamp only (client clock ignored)
Cap:                base __ h; +__ h per upgrade; hard max __ h
Efficiency:         __% of online passive rate (active-only bonuses excluded: [list])
Integration:        closed form [formula] / chunked N=__
Return UX:          summary screen fields [resource, amount, time credited, time lost to cap]
Edge cases:         negative elapsed → 0; elapsed > 30 d → cap + lapsed-player flow; mid-gap event end → split at boundary
```

### 4. Determinism Contract

```
Numeric:      fixed-point Q__.__ / float with strict mode, no FMA contraction, no fast-math
Transcendentals: lookup table or own implementation (never platform libm across platforms)
RNG:          per-system stream, algorithm __, seed derivation __; no global RNG calls in sim
Iteration:    entities sorted by stable ID; no unordered map/set iteration in sim code
Inputs:       [list], stamped with tick number
Verification: 64-bit state hash every __ ticks; desync triggers dump of last __ ticks
```

### 5. Agent Need Table

```
Need     │ Decay/min │ Critical < │ Satisfier (action → restore) │ Score curve (shape, k) │ Hysteresis (start/stop) │ Failure cooldown s
```

Read `references/idle-math-and-big-numbers.md` when implementing the number type, notation, prestige curves, or log-space formulas. Read `references/chains-agents-colonies.md` when building production networks, agent utility scoring, LOD tiers, or city/colony services.

## Quantitative Reference

### Tick models

| Sim type | Model | Rate (heuristic) | Why |
| --- | --- | --- | --- |
| Idle accrual | Analytic | evaluated on demand + 1-10 Hz display | Must cross offline gaps exactly |
| Timers (crops, builds) | Event-driven, absolute end time | on query | Zero cost while waiting |
| City/colony economy | Fixed-step | 1-10 Hz | Slow dynamics; save CPU |
| Agent decisions | Fixed-step, time-sliced | 2-5 Hz near, 0.2-1 Hz far | Decisions are slow; movement is not |
| Agent movement / physics | Fixed-step + render interpolation | 30-60 Hz | Stability and visual smoothness |
| Lockstep strategy | Fixed-step | 10-20 Hz turn rate | Input latency budget |

Fixed-step loop, clamped against the spiral of death:

```csharp
const double Dt = 1.0 / 20.0;               // 20 Hz sim
const int MaxStepsPerFrame = 5;
long tick; double acc;

void Frame(double frameSeconds) {
    acc += Math.Min(frameSeconds, 0.25);     // never try to catch up more than 250 ms live
    int steps = 0;
    while (acc >= Dt && steps < MaxStepsPerFrame) { Step(tick++, Dt); acc -= Dt; steps++; }
    if (acc >= Dt) acc = 0;                   // still behind: drop it; long gaps go to the analytic path
    Render(acc / Dt);                         // interpolation alpha in [0,1)
}
```

### Numeric limits that bite

| Type | Max | Exact integers to | Note |
| --- | --- | --- | --- |
| int32 | 2,147,483,647 | all | ms counter overflows after 24.86 days |
| int64 | 9.22e18 | all | safe for ticks and ms timestamps |
| float32 | 3.4e38 | 2^24 = 16,777,216 | at t = 86,400 s the step is 0.0078 s; a 16 ms dt is now half-rounded |
| double | 1.797e308 | 2^53 ≈ 9.007e15 | about 15-17 significant digits |
| Q16.16 fixed | ±32,768 | — | resolution 1/65,536 ≈ 1.5e-5 |
| Q32.32 fixed | ±2.1e9 | — | resolution ≈ 2.3e-10; needs 128-bit multiply intermediate |

### Closed forms for idle math

Cost of the next unit with k owned: `c(k) = b·r^k`.
Bulk cost of n more: `C(k, n) = b·r^k·(r^n − 1)/(r − 1)`.
Max affordable with money M: `n = floor( log_r( M·(r − 1)/(b·r^k) + 1 ) )`, then decrement once if `C(k, n) > M` (float edge).
Constant rate R over offline time t, cap T, efficiency e: `gain = e·R·min(t, T)`.
Compounding (output reinvested automatically at rate λ): `x(t) = x₀·e^(λt)`.
Producer chain, tier k makes tier k−1 at p_k per unit per second, top tier fixed:

```
x₀(t) = Σ_{k=0..m} N_k · (p₁·p₂·…·p_k) · t^k / k!
```

That polynomial is why stepping a tiered idle game in one big Euler step under-credits by orders of magnitude, and why you need either the closed form or chunking.

```csharp
static double BulkCost(double b, double r, int owned, int n) =>
    b * Math.Pow(r, owned) * (Math.Pow(r, n) - 1.0) / (r - 1.0);

static int MaxAffordable(double b, double r, int owned, double money) {
    double first = b * Math.Pow(r, owned);
    if (money < first) return 0;
    int n = (int)Math.Floor(Math.Log(money * (r - 1.0) / first + 1.0) / Math.Log(r));
    if (BulkCost(b, r, owned, n) > money) n--;   // guard the rounding edge
    return n;
}
```

```ts
// Same function serves online ticks and offline gaps. tiers[k] = count of tier k;
// p[k] = tier-(k-1) units produced per tier-k unit per second (p[0] unused).
export function advanceChain(tiers: number[], p: number[], t: number): number {
  let total = 0, coeff = 1;                      // coeff_k = p1..pk * t^k / k!
  for (let k = 0; k < tiers.length; k++) {
    if (k > 0) coeff *= (p[k] * t) / k;
    total += tiers[k] * coeff;
  }
  return total;                                  // amount of tier 0 after t seconds
}

export function offlineSeconds(lastSaveServerMs: number, serverNowMs: number, capSec: number): number {
  return Math.min(Math.max(0, (serverNowMs - lastSaveServerMs) / 1000), capSec);
}
```

### Offline and prestige heuristics

| Parameter | Typical range (heuristic) | Notes |
| --- | --- | --- |
| Base offline cap | 2-12 h | Below the p50 overnight gap (≈8 h) the cap is felt daily; that is the point of cap upgrades |
| Offline efficiency | 25-100% of passive rate | Below 25% offline feels like punishment; 100% only if active play has its own bonus |
| Active vs idle rate | active 1.5-3× idle | If idle ≥ active, the session has no reason to exist |
| First prestige | 1-3 h of play | Later prestiges should arrive at roughly equal or shorter real-time intervals |
| First prestige payoff | ≥ 2× production multiplier | Below about 1.5× players will not reset |

Prestige gain families: `P = k·(L/L₀)^(1/2)` needs 4× lifetime earnings to double P; `(L/L₀)^(1/3)` needs 8×; `k·log10(L/L₀)` needs L squared. Steeper roots slow the meta loop; pick the family by how many resets the content plan needs.

### Production chains

Machines per stage: `n_i = Demand_i × CycleTime_i ÷ (OutputQty_i × Speed_i)`. Chain throughput = `min_i(Capacity_i ÷ Required_i)` per final unit. Little's Law for work-in-progress: `L = λ·W` (items in buffer = arrival rate × average wait). Buffer to ride out an upstream stop of D seconds: `Buffer ≥ Flow × D`.

### Event-driven settlement (timed chains, crops, builds)

Process completions in timestamp order up to server time; each completion may start the next step. Exact, and O(events · log queue) instead of O(seconds).

```csharp
// queue ordered by (EndMs, EntityId) so ties resolve identically on every run
while (queue.Count > 0 && queue.Peek().EndMs <= serverNowMs) {
    var job = queue.Dequeue();
    Complete(job);                                    // grant output, free the slot
    if (TryStartNext(job.Slot, job.EndMs, out var next)) // next job starts at the old end time, not "now"
        queue.Enqueue(next);
}
```

Split any analytic gap at the boundaries where a rate changes (event start/end, cap reached, auto-buy threshold) and integrate each segment separately.

## Worked Example — "Ore Baron", idle mining with a crafting chain

**Bulk buy.** Drills: b = 10, r = 1.15, k = 50 owned. Next drill: 10 × 1.15^50 = **10,837**. Buying 10: 10,837 × (1.15^10 − 1)/0.15 = 10,837 × 20.30 = **220,023**. Max affordable with 1,000,000: `floor(log_1.15(1e6 × 0.15 / 10,837 + 1)) = floor(ln 14.84 / ln 1.15) = floor(19.30) = 19`. Check: 19 cost 955,914 ≤ 1e6; 20 cost 1,110,138 > 1e6. The shipped client looped one purchase at a time; at k = 3,000 buy-max took 400 ms on a low-tier device. Closed form: O(1).

**Chain ratio.** Ore drill 1 ore/s. Smelter 3 ore → 1 ingot per 2 s (eats 1.5 ore/s, makes 0.5 ingot/s). Forge 2 ingots → 1 tool per 5 s (eats 0.4 ingot/s, makes 0.2 tool/s). Target 1 tool/s: forges 1/0.2 = 5; ingots 5 × 0.4 = 2/s → smelters 2/0.5 = 4; ore 4 × 1.5 = 6/s → drills 6. **Ratio 6 : 4 : 5.** A player with 6 drills, 3 smelters, 5 forges is smelter-bound: 1.5 ingot/s → 0.75 tool/s, forges at 75% utilization, and 1.5 ore/s piles up until storage caps. The UI must name the smelter, not "low output". Smelter upgrade animation pauses the stage for 30 s → ingot buffer ≥ 2/s × 30 s = **60 ingots** or the forges starve.

**Offline.** Passive rate 200 coins/s, cap 8 h, efficiency 50%, player gone 11 h: 200 × 0.5 × 28,800 = **2,880,000** coins; summary shows "3 h lost to cap", which sells the cap upgrade honestly.

**Tier chain.** Late game: 10 foremen, each makes 2 miners/s; each miner makes 1 ore/s; zero miners owned at departure. One Euler step over 1 h credits 0 ore. Closed form: 10 × 1 × 2 × 3,600² / 2 = **129,600,000** ore. A fixed 1 h step would have shipped a 100% offline under-credit.

**Float timer.** Crop timers decremented `remaining -= dt` in float32 with session clocks past 86,400 s; step size 0.0078 s against a 0.016 s dt, so crops finished visibly late. Fix: absolute server end timestamps.

**Prestige.** `P = floor(10·sqrt(L/1e12))`, +2% production per point. At L = 4.9e13: P = 70 → ×2.4 multiplier, above the 2× first-reset target. By the sixth reset lifetime earnings pass 1e300; the team moved currency to mantissa-exponent before launch rather than after the first Infinity report.

## Diagnostics

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Offline gain ≠ leaving the app open for the same time | Separate offline formula missing a multiplier, or one Euler step over a polynomial chain | Route both through one `advance()`; golden test online 8 h vs offline 8 h within 1% |
| Huge gains after changing device clock | Client time trusted | Server timestamps only; clamp negative elapsed to 0 |
| Currency shows Infinity or NaN | Double overflow past 1.8e308, or 0 × Infinity | Mantissa-exponent or log-space type; NaN assertion in the harness |
| Buy-max or offline return freezes the UI | Per-unit loop | Closed-form bulk cost and max affordable |
| Timers finish late in long sessions | float32 time accumulation | int64 ticks or absolute end timestamps |
| Sim runs faster on 120 Hz devices | Render dt drives the sim | Fixed step with accumulator |
| Hitch or freeze when returning from background | Unbounded catch-up steps | Cap steps per frame; long gaps go analytic |
| Replay desync after minutes | Unordered iteration, global RNG, or platform libm | Determinism contract; state hash every N ticks; bisect to first differing tick |
| Chain output below sheet value | Buffer starvation, transport cap, or batch quantization | Little's Law on buffers; model transport as a stage |
| Colony booms then crashes in cycles | Delayed feedback with no damping | Hysteresis bands, EMA smoothing, rate limits |
| 300 agents converge on one tile | Identical utility scores, no reservation | Reservations, per-agent jitter of 2-5%, distance falloff |
| Agent loops trying an unreachable job | No failure memory | Failure cooldown per target (30-120 s, heuristic) |
| Players never prestige | First reset payoff under ~1.5× | Lower L₀ or raise per-point bonus until first reset ≈ 2× |
| Prestige spam every few minutes | Gain exponent too generous early | Steeper root or higher threshold L₀ |
| Sim CPU spikes at late-game counts | Every agent decides every tick | Time-slice decisions; LOD tiers; aggregate far agents |

## Anti-Patterns

**The Frame-Rate Economy** — production computed from render dt. Faster devices earn more, and a hitch can skip or double-count a tick.

**The Trusted Wristwatch** — offline elapsed time from the device clock. Every clock-change video on the store page is this.

**The Two-Formula Offline** — offline income from a hand-written shortcut that drifts the first time someone adds a multiplier to the online path.

**The Infinity Wall** — doubles chosen at launch for a content plan that reaches 1e400. The fix touches saves, UI, analytics, and every formula.

**The Buy-Max Loop** — buying one unit at a time in a loop; fine at 50 units, a frozen frame at 5,000.

**The Countdown Timer** — storing remaining seconds and decrementing them; pauses, kills, and float rounding all leak time.

**The Dictionary Shuffle** — iterating an unordered collection inside a deterministic sim; replays diverge only on some platforms and only sometimes.

**The Omniscient Crowd** — every agent runs full perception and decision logic every tick; CPU scales with population while players can see 20 of them.

**The Undamped Feedback Loop** — population, prices, or traffic reacting to their own delayed output with no hysteresis; the colony oscillates until it dies.

## Quality Checklist

- [ ] Every system has a declared time model (fixed-step / event / analytic / chunked) and tick rate
- [ ] Sim time is int64 ticks or absolute timestamps; no float32 accumulation anywhere
- [ ] Online and offline progress call the same `advance()` function
- [ ] Golden test: online 8 h vs offline 8 h agree within 1% under each player policy
- [ ] Offline elapsed comes from the server; negative elapsed clamps to 0; cap and efficiency documented
- [ ] Bulk buy, max affordable, and offline accrual are O(1) closed forms with a rounding guard
- [ ] Number type covers end-of-content values with margin; overflow and NaN asserted in the harness
- [ ] Production chain sheet filled; bottleneck named; buffers sized from Little's Law
- [ ] Every feedback loop has damping (hysteresis, smoothing, or rate limit)
- [ ] Agent decisions time-sliced with LOD tiers; reservations prevent target pile-ups
- [ ] Determinism contract written where replay or lockstep is required; state hash per N ticks
- [ ] Headless harness run for 30/90/365 simulated days; pacing table attached
- [ ] Sim CPU measured at p90 entity count on the lowest supported tier, within budget
- [ ] All heuristic numbers labeled as heuristics and replaced by measured values after soft launch

## Related Skills

**gamedev-engine-architect** owns the game loop, fixed-timestep plumbing, ECS layout, and save-format versioning that this skill's time model plugs into. **gamedev-netcode-engineer** takes the determinism contract and turns it into lockstep or rollback transport; this skill decides what must be deterministic, that skill decides how it syncs. **gamedev-backend-engineer** implements server-authoritative timestamps, offline settlement, and idempotent resource grants; **gamedev-anti-cheat-security** handles clock tampering, speed hacks, and memory-edited currency. **gamedev-meta-progression-designer** owns the layers above the sim (collections, account level, unlock pacing) and consumes the prestige and pacing tables produced here. If installed, `game-economy-balancer` owns cost-curve span selection, sink coverage, and currency time value; hand it the measured earn rates from the harness rather than estimates. **gamedev-optimization-compatibility** sets the per-tier CPU and memory budgets that bound agent counts and tick rates. **gamedev-hud-engineer** implements big-number formatting and the "while you were away" summary; give it the notation table from the reference file. If installed, `core-loop-designer` defines what the sim loop is for; if the idle loop has no meaningful active decision, fix it there before tuning rates here.
