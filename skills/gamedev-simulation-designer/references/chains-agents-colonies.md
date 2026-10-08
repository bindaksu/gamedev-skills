# Production Chains, Agents, Colonies, Determinism

Read when building a multi-stage production network, writing agent decision rules, scaling agent counts, tuning city/colony growth and services, or implementing a determinism contract.

## 1. Production networks

**Method.**
1. Draw the recipe graph: nodes are machines, edges are item flows with quantities per cycle.
2. Fix one target (final units per second) and walk backward: `Demand_upstream = Σ downstream consumption`.
3. Machines per stage: `n_i = Demand_i × Cycle_i ÷ (OutQty_i × Speed_i)`. Round up and record the fractional remainder; the remainder is idle capacity, and players notice.
4. Treat transport (belts, carts, couriers, warehouse transfer) as a stage with its own capacity.
5. Bottleneck = `argmin_i(Capacity_i ÷ Required_i)` per final unit. Surface it in UI by name.
6. Run the cycle-product test on any loop where outputs feed back into inputs (if installed, `game-economy-balancer` owns the full test); a cycle with product ≥ 1 is an infinite resource.

**Ratio design heuristics.**
- Small integer ratios (1:1, 2:1, 3:2, 6:4:5) are puzzles players enjoy solving; ratios like 7:13 read as noise. Pick cycle times so whole-machine ratios exist.
- Make at least one intermediate shared by two downstream products; contention for a shared input is where the interesting allocation decisions come from.
- Upgrades that change speed should scale all stages of a tier together, or every upgrade invalidates the player's layout. Changing one stage's speed is a deliberate re-balancing event.

**Buffers.**
- Little's Law: `L = λ·W`. A buffer averaging 40 items at 2 items/s means items wait 20 s on average.
- Ride-through sizing: `Buffer ≥ Flow × longest planned interruption` (upgrade, reload, courier trip).
- Batch quantization: a stage consuming batches of B needs `Buffer ≥ B + Flow × cycle-time jitter`, or it stalls on the last partial batch.
- Storage caps are sinks for overproduction; show "full" states loudly, because a silent cap looks like a bug.

**Time-gated chains (farm/restaurant games).** With absolute end timestamps, a chain of timed steps is event-driven: each completion schedules the next. For offline settlement, process events in timestamp order up to `serverNow`, re-evaluating which steps can start. This is exact and costs O(events × log queue).

## 2. Agent decision rules (utility)

**Considerations** map an input in [0,1] to a score in [0,1]:

```
Linear:     s = clamp(m·(x − c) + b)
Power:      s = clamp(x^k)                           k > 1 urgent only when high; k < 1 urgent early
Logistic:   s = 1 / (1 + e^(−k·(x − x₀)))            sharp threshold around x₀
Inverse:    s = clamp(1 − x)
```

**Combine** considerations per action. A raw product shrinks as consideration count grows (four 0.8s give 0.41), biasing toward simple actions; use the geometric mean `(Π s_i)^(1/n)` or a documented compensation factor. Multiply by an action weight (0.5-2.0) for designer intent.

**Crowd rules.**
- **Reservation:** an agent claims a target (food tile, job slot) when it picks it; other agents score claimed targets at 0. Without this, 300 agents path to one apple.
- **Jitter:** add per-agent noise of 2-5% (heuristic) to scores so ties break differently.
- **Commitment:** once an action starts, add an inertia bonus (10-25%, heuristic) until it completes, or agents dither between two near-equal options.
- **Failure memory:** a target that failed (unreachable, taken) gets a cooldown of 30-120 s (heuristic) for that agent.
- **Hysteresis on needs:** start eating below 30, stop above 80; one threshold makes agents flicker.

**Need decay tuning.** Set decay from the intended rhythm: if hunger should trigger once per 8 game hours with critical at 20 of 100, decay = 80 / 480 min = 0.167 per game minute. Then check worst-case travel time to the satisfier is under 25% of the time from "start seeking" to "critical", or agents die in transit.

## 3. Agent LOD and budgets

| Tier | Who | Decision rate | Movement | Notes |
| --- | --- | --- | --- | --- |
| 0 | On-screen, near camera | 2-5 Hz | 30-60 Hz, full avoidance | Full animation, perception |
| 1 | Off-screen, loaded region | 0.5-1 Hz | 5-10 Hz along path nodes | No avoidance; collision resolved on promotion |
| 2 | Unloaded / far | 0.05-0.2 Hz | Schedule-based (teleport along timetable) | Aggregate stats per district |

All rates heuristic; confirm budgets with `gamedev-optimization-compatibility`.

**Time-slicing:** with N agents and k slices, update `ceil(N/k)` agents per tick, choosing by `(agentId + tick) % k == 0` so the order is stable (matters for determinism). Many agents sharing a goal should share a flow field rather than each running A*.

**Promotion:** when an agent moves from tier 2 to tier 0, place it where its schedule says it is now, then interpolate. Players forgive a teleport off-screen, never on-screen.

## 4. City and colony dynamics

**Logistic growth** for population or demand with capacity K and rate g:

```
dx/dt = g·x·(1 − x/K)
x(t)  = K / (1 + ((K − x₀)/x₀)·e^(−g·t))
```

The closed form makes offline settlement exact for single-resource growth. Capacity K should come from player-built supply (housing, food), so the growth curve is a readout of their decisions.

**Service coverage:** a service of radius R tiles covers about `π·R²` tiles on a square grid (Euclidean) or `2R² + 2R + 1` (Manhattan). Report coverage % per district; a single uncovered district hidden in an average is the usual complaint.

**Damping toolkit.**
- EMA smoothing, frame-rate independent: `s += α·(x − s)`, `α = 1 − e^(−dt/τ)`; τ = 10-60 s of game time for demand signals (heuristic).
- Rate limits: population may change at most p% per game day.
- Hysteresis on any threshold that flips a building or agent state.
- Reserves: keep a target of D days of consumption in storage (D = 2-5, heuristic) before allowing expansion; this breaks the shortage → starvation → labor loss → deeper shortage spiral.

**Feedback audit.** For every loop, write: signal, delay, gain. Delay × gain is the oscillation risk; if output responds within less than half the delay, it will overshoot. Lower gain or shorten delay before shipping.

## 5. Determinism details

**Float rules if you keep floats.** IEEE 754 basic operations (+, −, ×, ÷, sqrt) are correctly rounded and reproducible for the same precision and rounding mode. Divergence comes from: compiler contraction into fused multiply-add, extended-precision intermediates, fast-math reassociation, SIMD reorderings of reductions, and transcendental functions (sin, exp, pow) differing between platform math libraries. Cross-platform lockstep therefore usually uses fixed-point or integer math for gameplay state and floats only for presentation.

**Fixed-point Q16.16 multiply:** `(int)(((long)a * b) >> 16)`; divide: `(int)(((long)a << 16) / b)`. Q32.32 needs a 128-bit intermediate.

**Seeded PRNG per system** (SplitMix64; good enough for gameplay, not for security):

```csharp
public struct SplitMix64
{
    private ulong _s;
    public SplitMix64(ulong seed) { _s = seed; }
    public ulong Next()
    {
        ulong z = (_s += 0x9E3779B97F4A7C15UL);
        z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9UL;
        z = (z ^ (z >> 27)) * 0x94D049BB133111EBUL;
        return z ^ (z >> 31);
    }
    public int Range(int maxExclusive) => (int)(Next() % (ulong)maxExclusive); // slight modulo bias; fine for gameplay
}
```

Derive each stream's seed from `(worldSeed, systemId)` so adding a random call in combat does not shift every loot roll in the economy.

**State hash** (FNV-1a 64) over the canonical, ID-sorted state every N ticks (N = 30-300, heuristic):

```csharp
static ulong Fnv1a(ReadOnlySpan<byte> data, ulong h = 0xCBF29CE484222325UL)
{
    foreach (byte b in data) { h ^= b; h *= 0x100000001B3UL; }
    return h;
}
```

On mismatch, both sides dump state at the last matching hash and replay to bisect the first differing tick and field. Transport, rollback, and input delay belong to `gamedev-netcode-engineer`.

**Replay for bug repro.** Even single-player games benefit: store `seed + build id + input log stamped by tick`. A reproducible repro turns a week of "cannot reproduce" into an afternoon.
