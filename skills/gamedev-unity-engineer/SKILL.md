---
name: gamedev-unity-engineer
description: >-
  Build and ship Unity 6 mobile game clients that hold frame-time, memory and
  crash-free targets on real devices: project and assembly architecture,
  Addressables with remote catalogs, URP mobile settings, IL2CPP and stripping,
  GC discipline, Burst/Jobs and ECS where justified, iOS/Android native plugins,
  profiling and build automation. Use when a user asks to structure or refactor
  a Unity project, set up Addressables or content updates, chases GC spikes or
  IL2CPP stripping crashes, writes a Swift or Kotlin bridge, picks a Unity 6.x
  version or render pipeline, or scripts headless builds.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: client-eng
---

# Unity Engineer

A Unity project fails slowly. No single commit breaks it; the frame budget and the heap erode one convenient `GetComponent`, one LINQ query, one singleton, one 40 MB bundle at a time, until a mid-tier Android phone stutters on the third level and the crash rate sits at 1.5% with nobody owning why. The job is to make the cheap path the correct path: assemblies that enforce dependency direction, config that is data, a heap that does not grow during gameplay, content that ships without a binary, and builds that a machine produces identically every time. Measure on the lowest device you support, in a release-configured build, or you are measuring the editor.

## Role Profile

At Dream Games, Rovio, Moon Active or Scopely (Monopoly GO), the Unity client engineer owns gameplay features end to end in C#, plus the architecture other engineers build inside. Postings ask for "flexible code that can be easily updated as the product evolves" (Dream Games), Unity Editor tooling and live-game stability (Rovio, Angry Birds 2), and "mobile optimization, performance profiling, and memory management" (Moon Active). Dream Games hires on OOP and CS fundamentals and teaches Unity on the job; Playrix retrains Unity developers onto its in-house C++ engine.

- **Hard skills:** C#, Unity runtime and editor APIs, design patterns, profiling (Unity Profiler, Memory Profiler, Xcode Instruments, Android Studio/Perfetto), Addressables/asset bundles, platform SDKs (GameKit, StoreKit, Play Billing), native bridges, editor tooling.
- **Seniority signals:** owns architecture, builds editor tools designers live in, keeps the live game stable through content updates.
- **Judged on (inferred from postings):** crash-free sessions, feature delivery cadence, frame rate and load time on target devices.
- **Collaborators:** game designers, artists and UI, backend, QA, product.
- Sources: https://jobs.lever.co/rovio-2/bb258566-0434-4025-ae4a-1d4b7a57896e , https://www.dreamgames.com/jobs/senior-software-engineer , https://hitmarker.net/jobs/moon-active-game-engineer-4523479

Unity dominates top-grossing mobile (Royal Match, Monopoly GO, Coin Master, Genshin Impact on a heavily customized pipeline); share estimates run around 70% of top grossers and are directional only.

## When to Use / Not

Use for Unity client code, project structure, Addressables, URP settings, IL2CPP builds, GC and CPU optimization inside Unity, Burst/Jobs/ECS adoption, native plugin bridges, and build scripts.

Not for:
- Engine-agnostic loop, timestep, determinism or save-format design: `gamedev-engine-architect`.
- Device tiers, budgets, thermal policy and cross-engine profiling strategy: `gamedev-optimization-compatibility`.
- Shaders, VFX, texture compression and draw-call budgets owned by art: `gamedev-technical-artist`.
- HUD and UGUI/UI Toolkit canvas performance: `gamedev-hud-engineer`.
- Multiplayer model and Netcode/Photon choice: `gamedev-netcode-engineer`.
- Signing, store submission, staged rollout: `gamedev-delivery-release`.

## Inputs to Gather

- **Unity version and upgrade window.** Default: 6.3 LTS for a live game; do not chase a Supported (non-LTS) release mid-production.
- **Render pipeline.** Default: URP. If the project is on Built-in, plan the migration now.
- **Target device floor** per platform (SoC, RAM, OS). Default: a 3–4 GB RAM Android device with a mid-range Adreno/Mali GPU and the oldest iPhone you support.
- **Frame target** (30, 60, 120) and memory budget per tier, from `gamedev-optimization-compatibility`. Default: 33.3 ms at 30 fps on the floor device, 16.6 ms at 60 fps on mid tier.
- **Content model:** what ships in the binary vs downloaded, update cadence, CDN. Default: binary holds first session; everything else remote via Addressables.
- **Existing architecture:** asmdef map, how services are found (singletons, DI container), where config lives.
- **Third-party SDKs** (ads, analytics, attribution, billing) — they own much of your startup time, method count and native crash surface.
- **CI:** who builds, on what machines, with what license. Default: headless batchmode builds per commit on main.

## Method

1. **Pin the version.** Choose an LTS and record the upgrade date in the roadmap. Upgrades are a project, not a chore: budget 1–2 sprints and a full regression pass.
2. **Draw the assembly graph before writing features.** Split into Core (pure C#, `noEngineReferences: true`), Runtime gameplay, UI, Platform (native bridges), Editor, and Tests. Dependencies point inward only. Why: asmdefs make illegal dependencies a compile error and cut iteration time because a UI change recompiles only UI.
3. **Pick one composition model.** A single composition root that constructs services and passes them by constructor (or a lightweight container such as VContainer). Ban new static singletons; wrap unavoidable ones (SDKs) behind interfaces. Static state also breaks fast Enter Play Mode, which skips domain reload; any remaining static must be reset in a `SubsystemRegistration` hook.
4. **Move tuning into data.** ScriptableObjects for authored, read-only config; remote config (JSON, versioned, with a bundled fallback) for anything live-tuned. Never write runtime state into a ScriptableObject — in the editor the change persists to disk, in a build it silently resets.
5. **Design Addressables groups by update cadence and load-together sets**, not by folder. Static first-session content stays local; seasonal and event content goes remote. Run the duplicate-dependency analysis before every content release.
6. **Enable the remote catalog in the very first shipped binary.** Without it, no later content update can be detected — the binary must be resubmitted.
7. **Set URP per tier** with one URP Asset per quality level, not one asset with runtime toggles. Low tier: render scale 0.7–0.8, no HDR, no depth/opaque texture copies, shadows off or one cascade.
8. **Make IL2CPP stripping explicit.** Start at Medium stripping, keep a `link.xml` per assembly that uses reflection, and run the full game in a stripped release build in CI. Stripping crashes surface only in device builds, usually in serializers and DI containers.
9. **Hold allocation at zero in steady-state gameplay.** Profile the hot loop with GC Alloc sorted descending; pool every spawned object; replace allocating APIs with NonAlloc variants. Incremental GC hides spikes; it does not remove the cost.
10. **Use Burst/Jobs for hot, data-parallel math** (crowds, projectiles, pathfinding grids, procedural meshes). Move to ECS only when entity counts and homogeneity justify the second programming model (see reference table).
11. **Bridge native code through one Platform assembly** with a C# interface, an editor stub and per-platform implementations. Every callback from native lands on the main thread before touching Unity APIs.
12. **Automate the build from day one**: a static C# build method callable by `-executeMethod`, Addressables content built before the player, symbols uploaded to the crash reporter, and the build number stamped from CI.
13. **Close the loop with field telemetry**: frame time percentiles, memory, and load time per device model from release builds, because a development build with the profiler attached distorts all three.

## Deliverables

### 1. Project architecture sheet

```
UNITY VERSION:      6.3 LTS (6000.3.x)   upgrade window: [date]   next target: 6.7 LTS
RENDER PIPELINE:    URP   assets: URP_Low / URP_Mid / URP_High
SCRIPTING BACKEND:  IL2CPP   stripping: Medium   API: .NET Standard 2.1
ASSEMBLIES:
  Game.Core        (noEngineReferences) → nothing
  Game.Runtime     → Game.Core
  Game.UI          → Game.Runtime, Game.Core
  Game.Platform    → Game.Core          (native bridges; #if per platform)
  Game.Content     → Game.Core          (Addressables wrappers)
  Game.Editor      → all (Editor only)
  Game.Tests.Edit / Game.Tests.Play
COMPOSITION:        [single root scene / container name]   singletons allowed: [list, each wrapped]
CONFIG:             ScriptableObjects (authored) + remote JSON v[n] (live) + bundled fallback
CONTENT:            local groups [..]  remote groups [..]  CDN [..]  catalog: remote, enabled
BUDGETS (floor):    frame [..] ms   managed heap [..] MB   GC alloc/frame 0 B   cold start [..] s
```

### 2. Addressables group plan

```
Group           │ Local/Remote │ Bundle mode       │ Update restriction │ Typical size │ Loaded when
Boot            │ Local        │ Pack together     │ Prevent updates    │ < 20 MB      │ app start
Core_Gameplay   │ Local        │ Pack separately   │ Prevent updates    │ 2–8 MB each  │ first session
Meta_UI         │ Remote       │ Pack by label     │ Can change         │ 1–5 MB each  │ on screen open
Event_[season]  │ Remote       │ Pack together     │ Can change         │ 5–30 MB      │ event start (prefetch)
Locale_[lang]   │ Remote       │ Pack separately   │ Can change         │ < 5 MB       │ language select
```

### 3. Performance pass report

```
DEVICE: [model, SoC, RAM, OS]   BUILD: [release, IL2CPP, version]   SCENE/STATE: [..]
            target   p50    p90    p99    worst marker (ms)
CPU main    [..]     [..]   [..]   [..]   [ProfilerMarker name]
CPU render  [..]
GPU         [..]
GC alloc/frame: [..] B  GC collections/min: [..]   managed heap: [..] MB   total RSS: [..] MB
FINDING → CHANGE → MEASURED DELTA → REGRESSION GUARD (test or CI budget)
```

### 4. Native plugin contract

```
FEATURE:        [e.g. haptics, ATT prompt, store review, keychain token]
C# INTERFACE:   IHaptics { void Play(HapticKind kind); }
IMPLEMENTATIONS: EditorStub | iOS (Swift via @_cdecl) | Android (Kotlin via AndroidJavaObject)
THREADING:      native → main thread via [dispatcher]
FAILURE MODE:   [no-op / fallback / error code]
SIZE IMPACT:    [.a/.aar/.so size, method count]   16 KB aligned: [yes/no]
```

Read `references/code-patterns.md` when writing the composition root, config, pooling, Burst job or telemetry code. Read `references/native-plugins.md` when writing an iOS or Android bridge. Read `references/addressables-and-builds.md` when wiring content updates, the CLI build or CI.

## Technical Reference

### Unity 6 version facts (as of 2026-10; verify)

| Release | Status / note |
|---|---|
| 6.0 LTS (Oct 2024) | Support ends around Oct 2026; move off it |
| 6.3 LTS (Dec 2025) | 2 years support (3 Enterprise), to about Dec 2027; recommended for live games |
| 6.4 (Mar 2026) | ECS core packages (Entities, Collections, Mathematics, Entities Graphics) ship with the Editor, versions locked to it |
| 6.5 (mid 2026) | Built-in Render Pipeline deprecated (still present through at least 6.7 LTS, no removal date); HDRP in maintenance; investment goes to URP |
| 6.6 (Sep 2026) | Fast Enter Play Mode default; experimental CoreCLR desktop player |
| 6.7 LTS | Expected Q4 2026 |
| Unity 7 | Announced as a continuation of Unity 6 on CoreCLR; beta Dec 2026, release Q1 2027 per press — provisional |

- Netcode for GameObjects 1.x is unsupported from the 6000.3 editor; use NGO 2.x (adds Distributed Authority).
- Runtime Fee was cancelled (Sept 2024). Personal tier cap is $200k; Pro is $2,200/seat/year above that; Enterprise above $25M (as of 2026-10; verify).
- Android: the App Category player setting (set to Game) exempts games from Android 16 large-screen orientation/resizability overrides; the old `androidIsGame` flag is gone.
- Apple ships StoreKit and Background Assets plug-ins for Unity (WWDC26) (as of 2026-10; verify).
- Code hot-update via HybridCLR is common in Asian markets; downloaded code must stay within Apple 2.5.2/4.7 and Play policy and must not change the app's primary purpose.

### ECS / Burst decision

| Situation | Choice |
|---|---|
| < 1,000 active objects, heterogeneous behaviour | MonoBehaviours + pooling |
| Hot math loop over arrays (steering, damage ticks, grid flow fields) | Burst job on NativeArrays, results copied back |
| 5,000+ homogeneous entities, simulation-heavy (RTS units, bullets, crowds) | Entities (ECS) for that subsystem only |
| Team has no ECS experience and ships in < 6 months | Burst jobs, not ECS (heuristic) |

Burst-compiled jobs routinely run 5–20× faster than equivalent managed loops on math-heavy code (heuristic; measure your case). Schedule early in the frame, complete as late as possible, never `Complete()` immediately after `Schedule()` — that is a slower synchronous call.

### URP mobile settings

| Setting | Low tier | Mid tier | High tier | Why |
|---|---|---|---|---|
| Rendering path | Forward | Forward / Forward+ | Forward+ | Forward+ lifts per-object light limit; costs a light-culling pass |
| Render scale | 0.7–0.8 | 0.85–0.9 | 1.0 | Fill-rate is the usual mobile GPU bound |
| HDR | Off | On (R11G11B10) | On | 64-bit targets double bandwidth |
| MSAA | Off or 2x | 2x | 4x | Cheap on tile-based GPUs, but resolves cost bandwidth |
| Depth / Opaque texture | Off | Only if a shader needs it | As needed | Each forces a copy pass |
| Main light shadows | Off / 1 cascade, 512 | 1–2 cascades, 1024 | 2–4 cascades, 2048 | Shadow maps are the top GPU cost in many mobile scenes |
| Additional lights | Off or per-vertex | 2–4 per object | 4–8 | |
| SRP Batcher | On | On | On | Cuts CPU per-draw setup |
| Post-processing | Color grading only | + light bloom | Full | Bloom at full res is expensive on mobile |

Unity 6 URP renders through Render Graph; custom renderer features must implement the Render Graph path (check whether compatibility mode still exists on your version).

### IL2CPP and stripping

- Managed Stripping Level: Minimal / Low / Medium / High. Medium is the sane default; High needs annotation discipline.
- Keep reflection targets with `link.xml` (`<assembly fullname="Game.Runtime" preserve="all"/>` for serialized DTO assemblies) or `[Preserve]`.
- Generic virtual methods and generic instances created only via reflection need AOT hints — call the generic once in a never-executed method, or use the serializer's AOT generator.
- IL2CPP Code Generation "Faster (smaller) builds" trades a little runtime speed for build time and binary size; use it for dev builds.
- C++ Compiler Configuration: Release for QA, Master for store builds (longer link, faster code).
- Upload IL2CPP symbols: enable Create symbols.zip (Android) and upload to the crash reporter, or native stack traces are unreadable. Crashlytics needs `firebase crashlytics:symbols:upload`; Apple dSYM upload is automatic.

### Allocation sources (zero-alloc gameplay)

| Allocates | Replace with |
|---|---|
| LINQ in Update | Plain loops over cached `List<T>` |
| Closures capturing locals in lambdas | Static lambdas, cached delegates |
| `string` concat / interpolation for UI each frame | Update text only on change; `StringBuilder` or `SetText(format, value)` (TextMeshPro) |
| `Physics.RaycastAll`, `OverlapSphere` | `RaycastNonAlloc`, `OverlapSphereNonAlloc` with pooled buffers |
| `new WaitForSeconds()` per yield | Cached instances |
| `gameObject.tag == "X"` | `CompareTag("X")` |
| Boxing value types into `object`/interfaces, `enum` as dictionary key in older runtimes | Generic constraints, custom `IEqualityComparer` |
| `Instantiate`/`Destroy` per spawn | `UnityEngine.Pool.ObjectPool<T>` |
| `GetComponentsInChildren()` without a list arg | Overload that fills a cached list |

Budget: 0 B per frame steady state; a scene transition can allocate, then force `GC.Collect()` and unload unused assets behind a loading screen.

## Diagnostics

| Symptom | Likely cause | Fix |
|---|---|---|
| Periodic 20–60 ms spikes every few seconds | GC collections from per-frame allocations | Profile GC Alloc column, remove sources; keep incremental GC on |
| Works in editor, `MissingMethodException` / null in device build | IL2CPP stripping removed reflection targets | `link.xml` or `[Preserve]`; add a stripped-build smoke test in CI |
| `ExecutionEngineException` / AOT error on device | Generic instantiated only via reflection | AOT hint method or serializer AOT generation |
| Content update shipped but players never get it | Remote catalog disabled in original binary, or catalog URL wrong | Enable remote catalog; for already-shipped binaries a store update is required |
| Players download the whole event twice | Bundle hashes changed due to duplicated dependencies or rebuild instead of update-previous-build | Run Analyze duplicates; use "Update a previous build" with the saved content state |
| Memory climbs every level, never drops | Addressables handles never released; static event subscriptions keep scenes alive | Pair every Load with Release; unsubscribe in OnDisable; Memory Profiler snapshot diff |
| Long hitch first time an effect plays | Shader variant compiled at first use | Shader variant collection + warmup behind loading screen; strip unused variants |
| Hitch on screen open | Synchronous `Resources.Load` or instantiating a large prefab | Async Addressables load ahead of need; split prefab |
| Android crash only on some devices in native lib | 16 KB page-size incompatible `.so`, or ABI missing | Rebuild with NDK r28+/AGP 8.5.1+; check alignment |
| Enter Play Mode shows stale data from last run | Static fields not reset with domain reload off | Reset in `[RuntimeInitializeOnLoadMethod(SubsystemRegistration)]` |
| Cold start > 5 s on mid tier | SDK init on main thread, large first scene, big Resources folder | Lazy SDK init, tiny boot scene, empty `Resources/` |
| Native callback crashes randomly | Unity API called from a native thread | Marshal to main thread via a dispatcher queue drained in Update |

## Anti-Patterns

**The Singleton Swamp** — every manager a static `Instance`. Order-of-init bugs, untestable code, and stale state with fast Enter Play Mode.

**The Mutable ScriptableObject** — runtime state written into config assets. Edits persist in the editor, reset in builds, and differ between the two.

**The Resources Folder Monolith** — everything under `Resources/`. All of it is indexed at startup, none of it can be updated remotely, and nothing can be unloaded granularly.

**Addressables Without Release** — loading by handle and never releasing. Bundles stay resident; memory climbs until the OS kills the app.

**The Schedule-Complete Job** — `Schedule()` followed by `Complete()` on the next line. All the overhead of jobs, none of the parallelism.

**ECS Everywhere** — porting menus and quests to Entities because the combat sim needed it. Two programming models for no gain.

**Profiling the Editor** — tuning against Play Mode numbers. Editor overhead, Mono and no thermal throttling make them fiction for a phone.

**Hand-Built Store Binaries** — releases built from someone's laptop. Unreproducible, missing symbols, and the one person is on holiday during the hotfix.

**One URP Asset, Runtime Toggles** — quality changed by flipping fields at runtime instead of swapping per-tier assets. Hidden copies and variants survive the toggle.

## Quality Checklist

- [ ] Unity version is an LTS with a recorded upgrade window
- [ ] URP in use; no new Built-in Render Pipeline content
- [ ] Assembly graph documented; Core has `noEngineReferences`; no circular references
- [ ] No new static singletons; remaining statics reset in a `SubsystemRegistration` hook
- [ ] ScriptableObjects hold only authored, read-only data
- [ ] Remote catalog enabled in the shipped binary; content state file archived per release
- [ ] Every Addressables load has a matching release; Memory Profiler diff across a level loop shows no growth
- [ ] Duplicate-dependency analysis clean before each content release
- [ ] One URP Asset per quality tier; depth/opaque texture off unless required
- [ ] Release IL2CPP build with intended stripping level runs the smoke test in CI
- [ ] IL2CPP symbols uploaded for every store build
- [ ] GC alloc per frame is 0 B in steady-state gameplay on the floor device
- [ ] Burst jobs scheduled early and completed late; no immediate `Complete()`
- [ ] Native plugins behind a C# interface with an editor stub; callbacks marshalled to main thread
- [ ] All native `.so` files 16 KB aligned
- [ ] Builds are produced by CI from a static build method with a stamped build number
- [ ] Frame time, memory and load-time percentiles reported per device model from release builds

## Related Skills

Hand loop, timestep, determinism and save-format questions to `gamedev-engine-architect`. Device tiers, budgets, thermal and memory-kill policy come from `gamedev-optimization-compatibility`; this skill implements them in Unity. `gamedev-technical-artist` owns shaders, VFX, texture compression and the art side of draw calls. `gamedev-hud-engineer` owns UGUI/UI Toolkit canvas structure and HUD performance. `gamedev-netcode-engineer` picks NGO, Fusion, Quantum or Mirror and the sync model. Native-side work beyond a bridge goes to `gamedev-ios-engineer` or `gamedev-android-engineer`. CI signing, store submission and staged rollout belong to `gamedev-delivery-release`; CDN hosting of Addressables content to `gamedev-live-serving` and `gamedev-infrastructure-engineer`. Integrity checks (App Attest, Play Integrity) go to `gamedev-anti-cheat-security`. Test automation on devices goes to `gamedev-qa-verifier`. If installed, `game-prototype-planner` decides whether prototype code is harvested into this architecture or thrown away.
