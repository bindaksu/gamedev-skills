# Loop, Interpolation and Determinism (C++ / C#)

## 1. Fixed timestep with interpolation (Fiedler "Fix Your Timestep!" pattern)

```cpp
// main_loop.cpp
struct SimState { /* plain data only: positions, velocities, rng, tick */ };

class Game {
public:
    void run() {
        constexpr double kDt          = 1.0 / 60.0;   // fixed sim step
        constexpr double kMaxFrame    = 0.25;         // clamp: avoids spiral of death
        constexpr int    kMaxSubsteps = 8;

        double previous    = now_seconds();
        double accumulator = 0.0;

        while (running_) {
            if (reset_clock_) { previous = now_seconds(); accumulator = 0.0; reset_clock_ = false; }
            double current = now_seconds();
            double frame   = std::min(current - previous, kMaxFrame);
            previous = current;
            accumulator += frame;

            poll_input();                              // OS events → input buffer

            int steps = 0;
            while (accumulator >= kDt && steps < kMaxSubsteps) {
                prev_ = curr_;                         // copy or double-buffer swap
                Commands cmds = sample_commands(curr_.tick);
                simulate(curr_, cmds, kDt);            // deterministic, fixed dt only
                accumulator -= kDt;
                ++steps;
            }
            if (steps == kMaxSubsteps) accumulator = 0.0;   // drop debt rather than freeze

            const double alpha = accumulator / kDt;    // 0..1
            render(interpolate(prev_, curr_, alpha));  // presentation only
        }
    }

    void on_resume_from_background() { reset_clock_ = true; }   // next frame: previous = now, accumulator = 0

private:
    SimState prev_{}, curr_{};
    bool running_ = true, reset_clock_ = false;
};
```

Notes:
- `simulate` reads only `cmds`, `curr_` and `kDt`. No clocks, no globals, no engine singletons.
- Double-buffer `prev_`/`curr_` by swapping indices when state is large instead of copying.
- Interpolate positions linearly, rotations with `slerp` (or nlerp for small deltas), and never interpolate discrete state (alive/dead, animation state IDs) — snap those at the tick.
- On mobile, display link callbacks (CADisplayLink, Choreographer/Swappy) give you the frame boundary; the accumulator still owns sim time.

## 2. Same pattern in C# (engine-agnostic core)

```csharp
public sealed class FixedStepRunner
{
    private const double Dt = 1.0 / 30.0;
    private const double MaxFrame = 0.25;
    private const int MaxSubsteps = 6;

    private double accumulator;
    private readonly ISimulation sim;
    private readonly IPresenter presenter;

    public FixedStepRunner(ISimulation sim, IPresenter presenter) { this.sim = sim; this.presenter = presenter; }

    public void Frame(double frameSeconds)
    {
        accumulator += Math.Min(frameSeconds, MaxFrame);
        int steps = 0;
        while (accumulator >= Dt && steps++ < MaxSubsteps)
        {
            sim.Step(Dt);                 // snapshots prev before mutating
            accumulator -= Dt;
        }
        if (steps > MaxSubsteps) accumulator = 0;
        presenter.Present(sim.Previous, sim.Current, (float)(accumulator / Dt));
    }

    public void ResetClock() => accumulator = 0;
}
```

## 3. Q16.16 fixed-point

```cpp
#include <cstdint>

struct Fix {
    int32_t raw;
    static constexpr int kShift = 16;
    static constexpr Fix from_int(int v)           { return {v << kShift}; }
    static constexpr Fix from_ratio(int n, int d)  { return {static_cast<int32_t>((int64_t(n) << kShift) / d)}; }

    friend constexpr Fix operator+(Fix a, Fix b) { return {a.raw + b.raw}; }
    friend constexpr Fix operator-(Fix a, Fix b) { return {a.raw - b.raw}; }
    friend constexpr Fix operator*(Fix a, Fix b) { return {static_cast<int32_t>((int64_t(a.raw) * b.raw) >> kShift)}; }
    friend constexpr Fix operator/(Fix a, Fix b) { return {static_cast<int32_t>((int64_t(a.raw) << kShift) / b.raw)}; }
    friend constexpr bool operator<(Fix a, Fix b) { return a.raw < b.raw; }

    float to_float() const { return raw / 65536.0f; }      // presentation only, never back into sim
};
```

Rules:
- Convert to float only at the presentation boundary.
- Authoring data (designer values) is converted to fixed at export time, so all clients load identical raw integers.
- Overflow: Q16.16 tops out at ±32,767. Distances squared overflow quickly — compare squared lengths in 64-bit or use Q32.32 with `__int128` (or a portable 128-bit multiply) intermediates.
- Trig: table-driven `sin`/`cos` over a fixed angle unit (e.g. 4,096 steps per turn); `sqrt` via integer Newton iteration.

## 4. Seeded RNG streams (PCG32)

```cpp
struct Pcg32 {
    uint64_t state, inc;
    explicit Pcg32(uint64_t seed, uint64_t stream = 1) : state(0), inc((stream << 1u) | 1u) {
        next(); state += seed; next();
    }
    uint32_t next() {
        uint64_t old = state;
        state = old * 6364136223846793005ULL + inc;
        uint32_t xorshifted = static_cast<uint32_t>(((old >> 18u) ^ old) >> 27u);
        uint32_t rot = static_cast<uint32_t>(old >> 59u);
        return (xorshifted >> rot) | (xorshifted << ((-rot) & 31));
    }
    // Unbiased range [0, bound)
    uint32_t below(uint32_t bound) {
        uint32_t threshold = (0u - bound) % bound;
        for (;;) { uint32_t r = next(); if (r >= threshold) return r % bound; }
    }
};

struct RngStreams {           // lives inside SimState, serialized with it
    Pcg32 combat, loot, ai;   // cosmetic RNG lives outside SimState
};
```

Derive each stream from one match seed plus a stream ID so a replay needs only the seed and the command log.

## 5. Per-tick checksum for desync and replay divergence

```cpp
uint32_t fnv1a(const void* data, size_t len, uint32_t h = 2166136261u) {
    auto p = static_cast<const uint8_t*>(data);
    for (size_t i = 0; i < len; ++i) { h ^= p[i]; h *= 16777619u; }
    return h;
}

uint32_t checksum(const SimState& s) {
    uint32_t h = fnv1a(&s.tick, sizeof s.tick);
    for (const auto& e : s.entities)                   // stable order: sorted by entity id
        h = fnv1a(&e.pos, sizeof e.pos, h), h = fnv1a(&e.hp, sizeof e.hp, h);
    h = fnv1a(&s.rng, sizeof s.rng, h);
    return h;
}
```

Hash fields explicitly rather than whole structs (padding bytes are uninitialised). Log `(tick, checksum)` in debug builds; on mismatch, dump both full states at the first divergent tick and diff them. This is the same divergence-detection approach Riot describes for League of Legends.

## 6. Command log for replays

```
REPLAY FILE
header:  magic "GRPL" | format_version | build_id | sim_hz | match_seed | initial_state_hash
body:    repeated { tick u32 | player u8 | command bytes }   (only ticks with input)
footer:  final_tick | final_checksum
```

A replay is valid only for the same `build_id` unless the sim is cross-platform deterministic and versioned. Keep old sim versions runnable (or store snapshots) if replays must outlive updates.

## 7. Threading the loop

| Thread | Owns | Sync point |
|---|---|---|
| Main / sim | Input, fixed ticks, gameplay | Publishes immutable render snapshot at end of frame |
| Render | Builds and submits GPU commands from snapshot N while sim runs N+1 | Snapshot handoff (one frame of pipelining = one frame of latency) |
| Job workers | Parallel sim systems, culling, animation | Fork-join inside a tick; deterministic partitioning if determinism is required |
| IO / streaming | Asset loads, save writes | Completion queue drained on main thread |

Rule: the sim never waits on IO, and the render thread never reads live sim state.

## 8. Fast-forward: decouple drawing from ticks

At 2× and faster, drawing every tick caps the sim at render cost. Readers that are not visual must still see every tick; the map only needs the newest state.

```csharp
public sealed class FastForwardRunner
{
    private const double Dt = 1.0 / 30.0;
    private const double MaxHoldSeconds = 0.5;        // never show a map older than this
    private const double SimBudgetMs = 12.0;          // leave the rest of the frame for drawing

    private readonly ISimulation sim;
    private readonly IReadOnlyList<ITickReader> readers;  // events, notifications, autosave, achievements, HUD values
    private readonly IMapPresenter map;
    private double debtTicks, sinceDraw;
    private int ticksSinceDraw;

    public FastForwardRunner(ISimulation sim, IReadOnlyList<ITickReader> readers, IMapPresenter map)
    { this.sim = sim; this.readers = readers; this.map = map; }

    public double Speed { get; set; } = 1.0;          // ticks per base tick: 1x, 2x, 5x ...

    public void Frame(double frameSeconds, int drawEveryNthTick)
    {
        debtTicks = Math.Min(debtTicks + Math.Min(frameSeconds, 0.25) / Dt * Speed, Speed * 10);
        long start = Stopwatch.GetTimestamp();
        while (debtTicks >= 1.0 && ElapsedMs(start) < SimBudgetMs)
        {
            sim.Step(Dt);
            foreach (var reader in readers) reader.OnTick(sim.Current);   // every tick, never skipped
            debtTicks -= 1.0;
            ticksSinceDraw++;
        }
        sinceDraw += frameSeconds;
        bool behind = debtTicks >= 1.0;
        bool draw = !behind || Speed <= 1.0 || ticksSinceDraw >= drawEveryNthTick || sinceDraw >= MaxHoldSeconds;
        if (draw) Present();
    }

    public void OnPauseOrNormalSpeed() => Present();   // show the waiting state at once

    private void Present() { map.Present(sim.Current); sinceDraw = 0; ticksSinceDraw = 0; }

    private static double ElapsedMs(long start) => (Stopwatch.GetTimestamp() - start) * 1000.0 / Stopwatch.Frequency;
}
```

Skipping applies only while the clock is behind its target rate; at speeds the device sustains, every frame still draws. Measure game days per second with drawing on and off on the floor device to size N.

## 9. Total orders and the cross-engine parity corpus

```csharp
// List<T>.Sort is unstable; JS sorts with an inconsistent comparator are implementation-defined.
// Any sort that feeds goldens, replays or saves ends in a stable-ID tie-break.
static int ByScoreThenId(Unit a, Unit b)
{
    int c = b.Score.CompareTo(a.Score);
    return c != 0 ? c : a.Id.CompareTo(b.Id);   // never 0 for two distinct units
}
```

```text
PARITY CORPUS (one file per rules revision)
case:     seed u64 | commands [...] | ticks n | expected sha256(snapshot bytes)
engines:  dev host [runtime + version] | device engine [Hermes, IL2CPP, GDScript VM ...] | native port [crate@commit] | server
rule:     generated once; every engine reproduces every digest; a mismatch blocks the merge
math:     sim code calls project helpers for anything beyond + - * / and sqrt (pow, exp, hypot, trig)
```

## 10. Porting a scripted core to native

- Keep the plain-data boundary the scripted core already has: commands in, snapshot bytes out.
- Rank phases by measured cost in a device build and port whole phases in that order. Per-entity calls from the interpreter into a native kernel pay marshalling every time; in one sim a kernel more than ten times faster made the simulated day slower.
- Share memory instead of copying: let native code borrow the scripted side's buffer, or let native own columnar state that the presentation reads through views.
- WebAssembly `memory.grow` detaches every typed-array view over the old buffer. Re-create views after any call that can allocate, and never cache them across such calls.
- Promote a phase only when goldens, snapshot bytes and a device-runtime checksum match; then delete the scripted path so the two cannot drift. Freeze gameplay edits to a phase while it is in flight.
