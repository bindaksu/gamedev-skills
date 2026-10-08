---
name: gamedev-engine-architect
description: >-
  Design the engine-level skeleton a game runs on: main loop, fixed timestep
  with interpolation, ECS versus component-OOP, determinism with fixed-point
  math and seeded RNG, data-driven config, scripting layers such as Lua, and
  versioned save systems with migrations, plus engine choice across Unity,
  Unreal, Godot, Defold, Cocos, native and custom C++. Use when a user asks how
  to structure a game loop, sees physics or gameplay behave differently at
  different frame rates, needs replays or lockstep-safe simulation, is choosing
  an engine, adding Lua or hot-reloadable config, or designing saves that must
  survive app updates.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: client-eng
---

# Engine Architect

Every game is a loop that turns input and time into state, and state into pixels. The architecture question is never "which pattern is cleanest" — it is which parts of that loop must be reproducible, which must be fast, which must change without a recompile, and which must survive five years of app updates on a player's device. Get the time model wrong and the game plays differently at 30 and 120 fps. Get determinism wrong and replays, lockstep and server validation are impossible to add later. Get the save format wrong and an update destroys someone's 400-hour account. Decide those three things on day one; everything else is refactorable.

## Role Profile

At top-grossing studios with their own technology, this is the engine or core-tech lead. Supercell runs all its games on the in-house **Titan** engine, maintained by a roughly 70-person organisation covering engine, tools and live-ops infrastructure for about 300M MAU (https://supercell.com/en/news/game-engine-called-titan). King's Candy Crush runs on a proprietary C++ cross-platform engine with Lua scripting, where "every line of code" is owned in-house and used by hundreds of developers (https://hitmarker.net/jobs/king-senior-c-developer-game-engine-799805); King also originated Defold. Playrix uses a proprietary C++17 engine with OpenGL ES/Metal and Lua/Python, and retrains Unity hires onto it (https://hitmarker.net/jobs/playrix-lead-c-software-engineer-gameplay-1518264). At Unity studios (Dream Games, Scopely) the same role is the client architect who owns the loop, data and save layers on top of the engine.

- **Hard skills:** C++ and/or C#, memory and threading models, ECS and data-oriented design, numerical determinism, serialization and schema evolution, scripting VM embedding, build and tools pipelines.
- **Judged on (inferred):** frame-time stability, iteration time (edit-to-see), crash and data-loss rate, how fast feature teams ship on the architecture.
- **Collaborators:** gameplay engineers, tools engineers, designers who author data, backend (save and validation), QA.

## When to Use / Not

Use for loop and time model, simulation architecture, ECS adoption, determinism, data/config pipelines, scripting layer design, save formats and migrations, and engine selection.

Not for:
- Unity-specific implementation (asmdefs, Addressables, IL2CPP): `gamedev-unity-engineer`.
- Network sync model, rollback and prediction: `gamedev-netcode-engineer` (this skill provides the deterministic simulation it needs).
- Tick models for idle/offline progress as a design problem: `gamedev-simulation-designer`.
- Device budgets and profiling campaigns: `gamedev-optimization-compatibility`.
- Native platform layers: `gamedev-ios-engineer`, `gamedev-android-engineer`, `gamedev-desktop-engineer`; rendering backends: `gamedev-metal-graphics-engineer`.
- Server-side save storage and cloud sync services: `gamedev-backend-engineer`.

## Inputs to Gather

- **Genre and simulation needs:** physics-driven, turn-based, real-time PvP, idle with offline progress. Default: real-time, single-player first, PvP possible later.
- **Determinism requirement:** none / replays / lockstep or rollback / server re-simulation for anti-cheat. Default: assume replays will be asked for; keep the sim deterministic within one build and platform.
- **Target platforms and frame rates**, including 120 Hz displays. Default: 60 fps target, sim at fixed 30 or 60 Hz.
- **Team shape:** engineers vs designers, scripting appetite, C++ capacity. Default: small team, designers need data and light scripting, not a VM.
- **Content scale and live-ops cadence:** how often data changes without a binary. Default: weekly config, monthly content.
- **Save scope:** local only, cloud, cross-platform, server-authoritative economy. Default: server owns currency and purchases; device owns settings and cache.
- **Existing engine and constraints** (licence, console plans, existing code).

## Method

1. **Write the time model first.** Choose the simulation rate (fixed Hz), render rate (display-driven, variable), and how the two meet (interpolation). Write it in a one-page doc before any gameplay code, because every system will encode an assumption about `dt`.
2. **Use the fixed-timestep accumulator with interpolation** (Fiedler, "Fix Your Timestep!"): simulate in fixed `dt` steps, render the blend of the last two states with `alpha = accumulator / dt`. Clamp the frame delta (e.g. 250 ms) and cap substeps per frame to avoid the spiral of death after a hitch or app resume.
3. **Separate simulation state from presentation state.** Sim state is plain data advanced only by fixed ticks; presentation (transforms, particles, UI tweens) reads it and may run at render rate. This split is what makes replays, rollback, server validation and save/load possible later.
4. **Decide determinism scope explicitly** — none, same-build-same-platform, or cross-platform. Cross-platform determinism with floats is a research project; with fixed-point it is an engineering task. Pick before writing physics.
5. **Make randomness explicit.** One seeded RNG stream per system (combat, loot, AI, cosmetic), stored in sim state, never `Random.value` or time-seeded calls inside the sim. Cosmetic randomness uses a separate stream so adding a particle effect cannot change a loot roll.
6. **Choose the object model per subsystem, not per project.** ECS where thousands of homogeneous entities are iterated every tick; component-OOP for heterogeneous, event-driven gameplay and UI (decision table below).
7. **Put every tunable in data with a schema.** Designers edit spreadsheets or editor tools; an exporter validates against a schema and emits versioned, typed config. Stable IDs are never reused. Validation errors fail the build, not the session.
8. **Add a scripting layer only for a named need** — designer-authored logic, modding, or code hot-update where allowed. Bound its frame budget, sandbox its API, and keep the hot loop in native code.
9. **Version the save format from v1.** Envelope with magic, version, checksum; a chain of pure migration functions `vN → vN+1`; atomic writes; golden files from every shipped version tested in CI.
10. **Choose or confirm the engine against the matrix** using constraints (team skills, platforms, licence, build size, determinism, console plans), not preference. Record the decision and the conditions that would reverse it.
11. **Instrument the loop**: per-phase timings, sim ticks per frame, accumulator debt, and a per-tick state checksum in debug builds so desyncs and non-determinism are caught at the tick they start.

## Deliverables

### 1. Loop and time-model spec

```
SIM RATE:          [30 | 60] Hz fixed   dt = [..] ms
RENDER:            display-driven (60/90/120 Hz), interpolated, alpha = acc/dt
MAX FRAME DELTA:   250 ms (clamp)       MAX SUBSTEPS: [4–8]
PHASE ORDER:       poll input → sample commands → N × sim.Tick(dt) → animation → late update
                   → interpolate → render prep → submit
INPUT LATENCY:     [frames from touch to first sim tick that consumes it]
BACKGROUND/RESUME: pause sim on background; on resume reset accumulator (no catch-up burst)
THREADS:           main/sim | render | jobs pool [n]   render pipelined by [0|1] frame
DETERMINISM:       none | same-build-platform | cross-platform   math: float | fixed Q[..]
RNG STREAMS:       combat, loot, ai, cosmetic — seeds stored in sim state
```

### 2. Architecture decision record

```
DECISION:   [e.g. ECS for combat sim; MonoBehaviour/node OOP for meta and UI]
CONTEXT:    [entity counts, team skills, determinism need, platforms]
OPTIONS:    [A, B, C with cost]
CHOSEN:     [..] because [..]
REVERSE IF: [measurable condition, e.g. > 2 ms sim cost at 2,000 units on floor device]
OWNER / DATE
```

### 3. Save format spec

```
FILE:        save_slot_[n].bin  (+ save_slot_[n].bak)
ENVELOPE:    magic "GSAV" | format_version u16 | schema_hash u32 | payload_len u32 | crc32 | payload
PAYLOAD:     [protobuf | FlatBuffers | MessagePack | JSON]  compression: [none | zstd | lz4]
MIGRATIONS:  v1→v2 [desc]  v2→v3 [desc]  ...  (pure functions, never deleted)
WRITE:       temp file → flush/fsync → atomic rename → rotate .bak
OWNERSHIP:   device: settings, tutorial flags, cache   server: currency, inventory, purchases
CLOUD MERGE: [rule per field: server-wins | max | union | last-writer-wins with vector clock]
TESTS:       golden saves from every shipped version load and round-trip in CI
```

### 4. Engine choice matrix (fill, then weight)

```
Criterion (weight)        │ Unity │ Unreal │ Godot │ Defold │ Cocos │ Native │ Custom C++
Team skill fit (x3)       │       │        │       │        │       │        │
Target platforms (x3)     │       │        │       │        │       │        │
Build size / cold start   │       │        │       │        │       │        │
2D vs 3D fit              │       │        │       │        │       │        │
Determinism control       │       │        │       │        │       │        │
Licence / cost at scale   │       │        │       │        │       │        │
Hiring market             │       │        │       │        │       │        │
Live-ops content pipeline │       │        │       │        │       │        │
Console path              │       │        │       │        │       │        │
```

Read `references/loop-and-determinism.md` when implementing the loop, interpolation, fixed-point math, RNG or desync checksums. Read `references/data-saves-scripting.md` when designing config schemas, save envelopes and migrations, or embedding Lua. Read `references/engine-matrix.md` when choosing an engine or weighing a custom engine.

## Technical Reference

### Time model options

| Model | How | Use when | Breaks when |
|---|---|---|---|
| Variable `dt` | `update(frameDelta)` | Menus, UI tweens, cosmetic effects | Physics, collisions, anything reproducible |
| Fixed `dt`, no interpolation | N fixed ticks per frame, render latest state | Sim rate equals display rate, locked | Display at 120 Hz with 60 Hz sim — visible judder |
| Fixed `dt` + interpolation | Accumulator, render `lerp(prev, curr, alpha)` | Default for real-time games | Adds up to one sim tick of visual latency |
| Fixed `dt` + extrapolation | Render `curr + vel × alpha·dt` | Latency-critical, smooth motion | Overshoot on direction changes, collisions |
| Turn / event-driven | Advance only on commands | Puzzle, card, turn-based | Never for real-time |

Sim rate heuristics: 30 Hz for casual/idle/puzzle-with-physics, 60 Hz for action and platforming, 60–120 Hz only for fighting or rhythm where input resolution matters. Unity's `FixedUpdate` and Godot's physics ticks (60 per second by default) are this accumulator; enable their interpolation options rather than moving bodies in render-rate callbacks.

### ECS vs component-OOP

| Factor | Favors ECS | Favors component-OOP |
|---|---|---|
| Entity count iterated per tick | 1,000s+ homogeneous | 10s–100s, heterogeneous |
| Behaviour shape | Same transform over many entities | Unique scripted behaviour per object |
| Determinism / rollback | Snapshotting contiguous component arrays is cheap | Object graphs are hard to snapshot |
| Team | Comfortable with data-oriented design | Designers script per-object behaviour |
| Tooling | Engine has mature ECS editor support | Engine's editor is built around objects |

Overwatch used an ECS with fixed command frames to make prediction and rollback tractable (GDC 2017: https://gdcvault.com/play/1024001/-Overwatch-Gameplay-Architecture-and). Hybrid is normal: ECS for the combat or crowd simulation, objects for meta, UI and one-off gameplay.

### Determinism hazards

| Hazard | Mitigation |
|---|---|
| Float results differ across compilers, CPU architectures, FMA contraction, fast-math flags | Fixed-point for sim state; or same binary, `-ffp-contract=off`, no fast-math, and test on every target CPU |
| Transcendentals (`sin`, `sqrt`, `atan2`) differ between libm versions | Lookup tables or own fixed-point implementations |
| Hash map / dictionary iteration order | Iterate sorted keys or stable insertion-ordered containers |
| Multithreaded sim with racing writes or nondeterministic reduction order | Deterministic job partitioning; reduce in fixed order |
| Shared RNG consumed by cosmetic code | Separate streams per system; cosmetic stream outside sim |
| Wall-clock or frame-time reads inside sim | Sim reads only tick number and fixed `dt` |
| Third-party physics engines | Check the engine's stated determinism scope; most guarantee only same-binary same-platform at best |
| Uninitialised memory, pointer-address ordering | Zero-init; never sort or hash by address |

Riot made the League of Legends server deterministic for Chronobreak and disaster recovery; a unified clock was the largest piece of work, and divergence was found by comparing state logs (https://technology.riotgames.com/node/67). Photon Quantum ships a deterministic ECS with fixed-point math for exactly this reason.

**Fixed-point formats:** Q16.16 in 32-bit (range ±32,768, resolution 1/65,536 ≈ 0.000015) suits 2D and small worlds; Q32.32 in 64-bit (needs 128-bit intermediate for multiply) suits large worlds. Multiply: `(a * b) >> 16` with a 64-bit intermediate; divide: `(a << 16) / b`.

### Scripting layers

| Option | Strength | Watch out |
|---|---|---|
| Lua 5.4 (sol2 or hand bindings) | Small, embeddable, designer-friendly; used by King and Playrix | GC pauses — use incremental/generational mode and a per-frame step budget |
| LuaJIT | Very fast where JIT is allowed | JIT is unavailable on iOS (no writable+executable memory for apps); interpreter only there |
| JavaScript (QuickJS-class engines) | Familiar to web-trained designers | Binding cost, larger runtime |
| C# via engine (Unity) / GDScript (Godot) | No extra VM | Not a sandbox; not hot-updatable on iOS without an interpreter |
| Visual scripting / node graphs | Non-programmers | Diffing, merging and performance at scale |

Downloaded executable code must stay within Apple guideline 2.5.2 and 4.7 and Play policy; it may not change the app's primary purpose.

### Engine landscape (as of 2026-10; verify)

- **Unity 6.3 LTS** is the live-game default; Built-in RP deprecated in 6.5; 6.7 LTS expected Q4 2026; Unity 7 (CoreCLR) announced for Q1 2027, provisional. Seat-based pricing, Pro required above $200k revenue.
- **Unreal 5.8** (June 2026): Lumen Lite, production-ready MegaLights and Iris networking; probably the last 5.x. Royalty 5% above $1M lifetime gross per product (verify current terms).
- **Godot 4.6** (early 2026; release date reported as both Jan 27 and Feb 27): Jolt is the default 3D physics, unique node IDs, LibGodot for embedding, C++ tracing profiler. 4.5 added a shader baker to cut startup compiles. MIT licence; console ports via third parties.
- **Defold 1.12.x**: King-originated, free source-available licence, 2D-focused, very small builds, Lua.
- **Cocos Creator 3.8.x**: TypeScript, strong for WeChat/Douyin mini-games, HarmonyOS and web. Acquisition reports are unconfirmed.
- **Native Apple**: SpriteKit is not deprecated but stagnant; SceneKit is soft-deprecated in favour of RealityKit. Prefer a cross-platform engine or custom Metal for long-lived titles.

## Diagnostics

| Symptom | Likely cause | Fix |
|---|---|---|
| Jumps are higher at 120 fps than at 30 fps | Physics or movement integrated with variable `dt` | Move to fixed-step sim; integrate only in ticks |
| Motion judders on 120 Hz displays though fps is high | Fixed sim rendered without interpolation | Render `lerp(prev, curr, alpha)` |
| Game freezes for seconds after a long hitch or app resume | Spiral of death: accumulator catch-up | Clamp frame delta, cap substeps, reset accumulator on resume |
| Replays diverge after a few minutes | Unseeded or shared RNG, float drift, dictionary iteration order | Per-system seeded streams; per-tick checksum to find the first divergent tick |
| Lockstep desync only between iOS and Android | Float differences across compilers/CPUs | Fixed-point sim math; deterministic trig |
| Designer change requires an engineer and a rebuild | Tunables in code | Schema'd data with hot reload in editor and dev builds |
| Lua frame spikes every few seconds | Lua GC running full cycles | Incremental/generational GC with per-frame step budget; reduce temp tables |
| Player loses progress after update | Missing or lossy migration; overwritten save on crash mid-write | Migration chain + golden-file tests; atomic write with backup |
| Save loads but values are wrong | Field renumbered or reused ID | Never reuse field numbers/IDs; reserve removed ones |
| Cloud save overwrites newer device progress | Last-writer-wins on whole blob | Per-field merge rules; server owns economy |

## Anti-Patterns

**Variable-dt Physics** — integrating gameplay with frame delta. The game is a different game on every device.

**The God Loop** — one `Update()` that polls input, simulates, animates and renders in interleaved order. No phase can be timed, threaded or replayed.

**Ambient Randomness** — `Random.Range` scattered through the sim. Determinism dies the first time an artist adds a random sparkle.

**Determinism Later** — planning to "add lockstep/replays after launch". Retrofitting determinism costs more than building it in from day one.

**ECS Religion** — moving menus, dialogue and quest logic into an ECS because the crowd sim needed one.

**The Unversioned Save** — serializing the live object graph directly. The first refactor becomes a data-loss incident.

**Scripting as an Escape Hatch** — adding a VM so "designers can do anything", then running hot loops in it and debugging without tools.

**Custom Engine by Pride** — building an engine without the scale that justifies it. Supercell amortises Titan across every title and ~300M MAU with a ~70-person org; a single-title studio pays the same platform-port and tools tax alone.

## Quality Checklist

- [ ] Time-model spec written: sim Hz, interpolation, delta clamp, substep cap, resume behaviour
- [ ] Sim state separated from presentation; presentation never writes sim state
- [ ] No wall-clock or frame-delta reads inside the sim
- [ ] Determinism scope declared; math type chosen to match
- [ ] One seeded RNG stream per system; seeds in sim state; cosmetic stream separate
- [ ] Per-tick state checksum available in debug builds
- [ ] Object model chosen per subsystem with an ADR and a reverse-if condition
- [ ] All tunables in schema'd data; IDs stable and never reused; validation fails the build
- [ ] Scripting layer (if any) has a per-frame budget, sandboxed API and profiler markers
- [ ] Save envelope has magic, version, checksum; migrations are pure functions kept forever
- [ ] Saves written atomically with a backup; golden files from every shipped version tested in CI
- [ ] Field ownership between device and server documented with merge rules
- [ ] Engine decision recorded against the weighted matrix, with licence terms re-checked
- [ ] Loop phases instrumented: per-phase ms, ticks per frame, accumulator debt

## Related Skills

`gamedev-netcode-engineer` builds lockstep, rollback and prediction on top of the deterministic sim and tick model defined here. `gamedev-simulation-designer` owns offline progress and tick-model design questions; this skill makes them computable and reproducible. `gamedev-unity-engineer` implements the architecture inside Unity; `gamedev-ios-engineer`, `gamedev-android-engineer`, `gamedev-desktop-engineer` and `gamedev-metal-graphics-engineer` own platform layers and rendering backends. `gamedev-optimization-compatibility` sets the frame and memory budgets the loop must meet. `gamedev-backend-engineer` and `gamedev-platform-server-architect` own server-side save storage, validation and cloud merge services; `gamedev-anti-cheat-security` uses deterministic re-simulation for verification. `gamedev-qa-verifier` runs golden-save and replay regression suites. If installed, `game-prototype-planner` decides how much of this architecture a prototype should carry.
