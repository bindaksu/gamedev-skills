---
name: gamedev-optimization-compatibility
description: >-
  Set and enforce performance and compatibility budgets for mobile and desktop
  games: frame time, memory, thermals, battery, download size and cold start
  per device tier, device matrix construction, cross-engine profiling, adaptive
  quality via ADPF and iOS thermal state, OOM/ANR/crash vitals, OS support
  floors, 16 KB pages and GPU driver blocklists. Use when a game stutters or
  heats up after ten minutes, OOM kills or ANRs climb, someone asks which
  devices to support or test on, a perf regression needs a CI gate, the app is
  too big to download, or Play/App Store technical deadlines approach.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: client-eng
---

# Optimization & Compatibility Engineer

Performance is a budget, not a feeling, and a budget only exists if it is written per device tier, measured from release builds in the field, and enforced by a gate that fails the build. A game that hits 60 fps for the first five minutes on a cold flagship and 38 fps at minute fifteen on the phone your median player owns has not been optimized; it has been demoed. The compatibility half of the job is the same discipline turned outward: know which devices, GPUs, drivers and OS versions your players actually run, test the ones that cover the installs and the revenue, and keep a remote-controllable escape hatch for the ones that break. Sustained, p90, on the floor device, in release — anything else is a number that lies.

## Role Profile

At Supercell the rendering owner on Clash Royale is accountable for "CPU/GPU budgets, memory, bandwidth, battery, and device fragmentation"; Central Tech asks for "predictable performance across a variety of devices", and engine automation roles "scale performance and stability observability". Goodgame frames it as owning "performance as a discipline: build time, memory, runtime" with device targets and budgets.

- **Hard skills:** Unity Profiler and Memory Profiler, Xcode Instruments, Android Studio profilers, AGI, Perfetto, RenderDoc, Unreal Insights; C++ and C#; device-tier budgets; perf CI and telemetry.
- **Seniority signals:** sets device tiers and budgets for the studio, owns perf regression gates in CI, decides OS and device support floors.
- **Judged on (inferred):** p50/p90 frame time per device tier, memory and OOM crash rate, load time and build size.
- **Collaborators:** rendering, tech art, QA compatibility lab, build engineering.
- Sources: https://hitmarker.net/jobs/supercell-senior-engine-programmer-rendering-clash-royale-4410230 , https://jobs.accel.com/companies/space-ape-games-2/jobs/59408422-senior-automation-engineer-game-engine , https://goodgamestudios.teamtailor.com/jobs/7762516-senior-unity-engineer

## When to Use / Not

Use for budgets, device tiers and matrices, profiling workflow, thermal and adaptive quality, memory kill behaviour, vitals, OS/API floors, 16 KB pages, GPU driver workarounds, app size, and startup time — across Unity, Unreal, Godot or native.

Not for:
- Unity-specific code fixes once the bottleneck is known: `gamedev-unity-engineer`.
- Shader cost, texture formats, LOD and draw-call art budgets: `gamedev-technical-artist`.
- Metal renderer internals and MSL: `gamedev-metal-graphics-engineer`; Vulkan/NDK internals: `gamedev-android-engineer`.
- HUD canvas rebuilds and UI overdraw: `gamedev-hud-engineer`.
- Network latency and bandwidth: `gamedev-netcode-engineer`.
- Device-lab execution and certification passes: `gamedev-qa-verifier`.

## Inputs to Gather

- **Install base by device model, SoC, GPU, RAM and OS version** from Play Console / App Store Connect / your analytics. Default when missing (pre-launch): genre competitor reports plus the last title's data; re-tier at soft launch.
- **Revenue share by device tier.** Payers skew to newer devices; a tier with 20% of installs may carry 40% of revenue.
- **Target frame rate per tier** and whether it must be sustained for the session length. Default: 30 fps floor tier, 60 fps mid/high, 120 fps optional on ProMotion/high-refresh flagships.
- **Session length.** Thermals only bite after 8–15 minutes (heuristic); a 3-minute puzzle game and a 25-minute battle royale need different thermal policy.
- **Engine and version**, render pipeline, graphics APIs shipped (Metal; Vulkan and/or GLES).
- **Current vitals:** crash rate, ANR rate, OOM/jetsam terminations, cold start time, per-device worst offenders.
- **Store deadlines in flight:** target API, 16 KB pages, billing library versions.
- **Download/install size** today and the content delivery model.

## Method

1. **Build the tier model from data.** Cluster devices by SoC generation, GPU family, RAM and OS into 3–4 tiers. Assign every device a tier server-side with a lookup table plus a benchmark fallback for unknown models, so you can re-tier without a binary.
2. **Write budgets per tier before optimizing anything.** Frame ms split CPU main/render/GPU, memory ceiling, thermal target, battery drain, cold start, download size. A budget is what a reviewer rejects a change against.
3. **Construct the test matrix by coverage.** Rank models by active-install share within each tier; pick devices until each tier reaches ~70–80% coverage of its installs (heuristic), then add one device per GPU family/driver line not yet covered and one worst-case (lowest RAM, oldest OS) per platform.
4. **Profile in release configuration on the floor device.** Development builds, attached profilers and the editor all distort. Use platform tools for ground truth (Instruments, AGI/Perfetto), engine tools for attribution (Unity Profiler, Unreal Insights).
5. **Classify each frame as CPU-bound, GPU-bound or pacing-bound before touching code.** A GPU-bound frame does not improve when you optimize scripts; inconsistent present intervals at average 60 fps are a pacing bug, not a speed bug.
6. **Measure sustained, not peak.** Run a 20–30 minute soak in a representative scene at room temperature, record frame time and thermal state per minute. The minute-20 number is the real budget number.
7. **Ship an adaptive quality ladder** driven by thermal headroom (Android ADPF, iOS `thermalState`) and measured frame time. Step down early (resolution scale, frame cap, effects), step up slowly with hysteresis.
8. **Instrument memory pressure.** Track footprint against the device's available memory, react to warnings by dropping caches, and count OS kills (MetricKit memory-limit exits, Android exit reasons) as crashes in dashboards — players experience them as crashes.
9. **Hunt ANRs on the main thread.** Any blocking I/O, SDK init, or synchronous IPC on the UI thread is a candidate; Android raises an ANR after 5 s of unprocessed input.
10. **Treat GPU drivers as a compatibility surface.** Keep a remote-configurable blocklist keyed by GPU renderer string, driver version and model that can force a graphics API (Vulkan → GLES), disable a feature, or drop a tier.
11. **Set OS and API floors by share and cost.** Drop an OS version when its install share falls below your threshold (heuristic: 1–3% of installs and lower payer share) or when it blocks a required SDK or store rule.
12. **Budget size like frame time.** Track install, download and on-device size per build; move non-first-session content to Play Asset Delivery, Apple Background Assets or engine remote content.
13. **Gate regressions in CI.** Automated perf runs on fixed devices per merge to main; fail the build when p90 frame time or peak memory exceeds budget by more than a set tolerance.
14. **Close the loop with field telemetry** (Android Performance Tuner, MetricKit, engine samplers): p50/p90/p99 frame time, memory and load time by device model and tier, reviewed weekly.

## Deliverables

### 1. Tier budget sheet

```
TIER  │ Example devices (verify) │ Target fps │ CPU main │ GPU   │ Mem ceiling │ Thermal target │ Battery │ Cold start
Low   │ 3–4 GB Android, older SoC│ 30         │ ≤ 25 ms  │ ≤ 25  │ [..] MB     │ no throttle    │ ≤ [..]  │ ≤ 5 s
Mid   │ 6 GB Android, recent iPh │ 60         │ ≤ 12 ms  │ ≤ 12  │ [..] MB     │ ≤ "fair" @20m  │ ≤ [..]  │ ≤ 3.5 s
High  │ flagships                │ 60 / 120   │ ≤ 12 / 6 │ ≤ 12/6│ [..] MB     │ ≤ "fair" @30m  │ ≤ [..]  │ ≤ 3 s
DOWNLOAD SIZE: store binary ≤ [..] MB   first-session content ≤ [..] MB   total on-device ≤ [..] GB
MEASURED AT: release build [..], minute 20 of soak, room temp, brightness 50%, Wi-Fi
```

Frame budgets leave ~20–25% headroom below the vsync interval (heuristic) — 16.67 ms at 60 fps means planning for ~12–13 ms, because thermals and OS work eat the rest.

### 2. Device matrix

```
Platform │ Model │ SoC │ GPU family/driver │ RAM │ OS │ Tier │ Install share │ Revenue share │ Role (floor/median/GPU-line/worst)
COVERAGE: Low [..]%  Mid [..]%  High [..]%  of tier installs   GPU families covered: Adreno / Mali / PowerVR / Apple / Xclipse
```

### 3. Performance investigation report

```
DEVICE / TIER / OS / BUILD (release, version)     SCENE + STATE      MINUTE OF SOAK
BOUND: CPU main | CPU render | GPU | pacing | memory | thermal
EVIDENCE: [trace file, tool, marker]   p50/p90/p99 frame ms: [..]   thermal state/headroom: [..]
ROOT CAUSE → CHANGE → MEASURED DELTA (same device, same minute) → GUARD (CI budget, test)
```

### 4. Adaptive quality ladder

```
Level │ Trigger (down)                          │ Trigger (up, after hold)        │ Changes
 0    │ —                                       │ headroom < 0.5 for 60 s          │ full quality
 1    │ headroom ≥ 0.75 or iOS .fair + p90>bud  │ headroom < 0.5 for 60 s          │ render scale −15%, shadows down
 2    │ headroom ≥ 0.85 or iOS .serious         │ headroom < 0.6 for 90 s          │ cap 30 fps, particles −50%, post off
 3    │ headroom ≥ 0.95 or iOS .critical        │ manual / next session            │ minimum tier, pause non-essential work
```

Thresholds are starting heuristics; calibrate per device family from soak data.

### 5. Support policy

```
iOS min: [..] (share [..]%)   Android minSdk: [..] (share [..]%)   targetSdk: 36
Graphics: Metal | Vulkan (default) + GLES fallback via blocklist
Review cadence: quarterly + on each store-policy change   Owner: [..]
```

Read `references/adaptive-quality-code.md` when implementing thermal, frame-time or memory-pressure handling (Kotlin, Swift, C#). Read `references/profiling-and-gates.md` when capturing traces, measuring startup/battery from the command line, or wiring a CI perf gate. Read `references/compatibility-matrix.md` when building tiers, a device matrix, a GPU blocklist, or a size-reduction plan.

## Technical Reference

### Frame and thermal numbers

| Refresh | Frame interval | Planning budget (heuristic) |
|---|---|---|
| 30 Hz | 33.3 ms | 26–28 ms |
| 60 Hz | 16.67 ms | 12–13 ms |
| 90 Hz | 11.1 ms | 8–9 ms |
| 120 Hz | 8.33 ms | 6–6.5 ms |

- **iOS `ProcessInfo.thermalState`:** nominal, fair, serious, critical; observe `thermalStateDidChangeNotification`. Apple guidance: at fair defer work, at serious cut animations and networking, at critical stop heating.
- **ProMotion iPhone:** set `CADisableMinimumFrameDurationOnPhone = YES` in Info.plist and use `CADisplayLink.preferredFrameRateRange`, not `preferredFramesPerSecond`. The OS can still drop to 60 Hz briefly; some devs report a 90 Hz cap.
- **Android ADPF Thermal API** (API 30+): `PowerManager.getThermalHeadroom(forecastSeconds)` returns 1.0 at severe throttling; scale before reaching it.
- **ADPF Performance Hint API** (API 31+): create a session for game and render threads; call `updateTargetWorkDuration()` and `reportActualWorkDuration()` every frame so the scheduler sizes CPU clocks. Map headroom to your own knobs, not engine Low/Medium/High presets.
- **Engine support:** Unity Adaptive Performance Android provider (hint calls automatic); Unreal ADPF plugin (API 31+); Cocos Creator Thermal API from 3.8.2, Hint API from 3.8.3; Defold ADPF extension.
- **Frame pacing:** Swappy (AGDK Frame Pacing) for GL and Vulkan; 30 fps on a 60/90/120 Hz panel without pacing alternates 16/50 ms frames and reads as stutter.
- **Game Mode:** automatic on iOS/iPadOS 18+; eligibility keys `GCSupportsGameMode` and `LSSupportsGameMode` (26+) (as of 2026-10; verify).

### Memory kill behaviour (heuristics — verify per device)

| Platform | Mechanism | Signals you get | Working heuristic |
|---|---|---|---|
| iOS | Jetsam kills on footprint limit; no exception, no crash log in your reporter | `didReceiveMemoryWarningNotification`, `os_proc_available_memory()`, MetricKit exit metrics (memory-limit terminations) | Keep peak footprint well under the per-device limit; measure the limit on each RAM class rather than assuming a fraction. `com.apple.developer.kernel.increased-memory-limit` entitlement can raise it on supported devices |
| Android | lmkd kills by priority; foreground app dies last but does die on 3–4 GB devices | `onTrimMemory`, `ActivityManager.getMemoryInfo()` (`availMem`, `lowMemory`), `ApplicationExitInfo` (API 30+), Memory Advice API (Beta) | Keep total PSS on 3–4 GB devices under ~1–1.3 GB including GPU memory (heuristic); `isLowRamDevice()` forces the lowest tier |

OS kills look like silent restarts to players and like nothing in a crash reporter. Count them.

### Android vitals and store deadlines (as of 2026-10; verify)

- **Bad-behaviour thresholds:** user-perceived crash rate 1.09%, user-perceived ANR rate 0.47%, and 8% on any single device model — above these Play reduces visibility and can show store-listing warnings. These come from a 2022 Google blog; verify current values in Play Console.
- **Startup:** Android vitals flags excessive cold start at 5 s or longer (verify current thresholds in Play Console).
- **Target API:** new apps and updates must target Android 16 (API 36) from Aug 31, 2026; extension to Nov 1, 2026 on request.
- **16 KB pages:** apps targeting Android 15+ must support 16 KB pages on 64-bit devices; from Feb 1, 2027 non-compliant updates cannot be released. NDK r28+ and AGP 8.5.1+ align by default; older NDKs need `-Wl,-z,max-page-size=16384`. Every prebuilt `.so` (ads, physics, audio middleware) must be rebuilt.
- **Large screens:** Android 16 ignores orientation/resizability limits on sw600dp+ unless the manifest declares `android:appCategory="game"`.

### Graphics API landscape

- About 85% of active Android devices support Vulkan; all 64-bit Android 10+ devices support Vulkan 1.1. OpenGL ES gets no new features. Unity and Unreal default to Vulkan where compatible.
- ANGLE (GLES on Vulkan) ships as an optional layer on Android 15+; long-term GLES runs through ANGLE.
- Metal 4 requires A14 / M1 or later; keep a Metal 3 path for older supported iPhones.

### Size limits (as of 2026-10; verify)

| Store mechanism | Limit |
|---|---|
| Play base module | 200 MB |
| Play asset pack | 1.5 GB each, max 100 packs |
| Play install-time total | 4 GB |
| Play on-demand + fast-follow | 4 GB (30 GB for Level Up program / XR) |
| Apple-hosted Background Assets | up to 200 GB compressed per app; replaces On-Demand Resources |

PAD Texture Compression Format Targeting serves ASTC/ETC2 per device from one AAB. Fast-follow and on-demand packs can be evicted — query their location every time.

### Profiling toolset

| Question | iOS / macOS | Android | Engine |
|---|---|---|---|
| Stutter over a session | Instruments Game Performance / Game Performance Overview; `metalperftrace` look-back | Perfetto system trace | Unity Profiler, Unreal Insights |
| CPU vs GPU overlap | Metal System Trace | AGI system profiler (Perfetto-based, GPU counters) | Profiler GPU module |
| Per-draw GPU cost | Xcode Metal debugger | AGI frame profiler (Vulkan, GLES) | Frame Debugger, RenderDoc |
| Memory | Instruments Allocations / VM Tracker | `dumpsys meminfo`, Android Studio Memory | Unity Memory Profiler, Unreal Memory Insights |
| Field data | MetricKit (Metal frame rate by state on iOS 27, assumed; memory-limit exits), Metal Performance HUD in test | Android Performance Tuner, Android vitals | Engine telemetry sampler |

### Cold start budget breakdown (heuristic, mid tier, 3.5 s total)

| Phase | Budget | Usual offenders |
|---|---|---|
| Process start → engine init | ≤ 0.8 s | Large native libs, static initializers, IL2CPP metadata load |
| Engine init → boot scene | ≤ 0.7 s | Big first scene, `Resources/` indexing, shader compile |
| SDK init (ads, analytics, attribution, billing) | ≤ 0.5 s on main thread | Synchronous init; defer everything not needed before first input |
| Config/content check | ≤ 0.5 s, non-blocking | Network calls blocking boot; use cached config and continue |
| First interactive frame | ≤ 1.0 s | Loading the full meta screen instead of a light shell |

Measure with `am start -W` (Android) and launch-time metrics in Xcode Organizer / MetricKit (iOS); report median and p90 over 10 cold launches per device.

WWDC26 additions: `SRStateReporter` (StateReporting) tags traces with game state such as level or menu; look-back collection captures the last hours without a pre-armed trace (as of 2026-10; verify).

## Diagnostics

| Symptom | Likely cause | Fix |
|---|---|---|
| 60 fps at start, 40 fps after 15 min | Thermal throttling; budget set on cold device | Soak-test budgets; adaptive ladder on ADPF headroom / thermalState; cap fps on low tier |
| Average fps fine, players report stutter | Frame pacing: uneven present intervals | Swappy / platform frame pacing; cap to a divisor of refresh |
| GPU time high, CPU idle | Fill-rate/overdraw, full-res post, shadows | Render scale, cut post at low tier, hand art budgets to tech art |
| CPU main high, GPU idle | Script/UI/physics on main thread | Engine profiler attribution; move to jobs/threads; HUD rebuilds to hud engineer |
| Silent restarts, nothing in crash reporter | Jetsam / LMK kill | MetricKit exit reasons, `ApplicationExitInfo`; lower peak footprint; react to warnings |
| ANR rate above threshold | Main-thread I/O, SDK init, sync IPC, long GC | Perfetto main-thread slices; defer SDK init; async I/O |
| Crashes clustered on one GPU family | Driver bug in shader compiler or extension | Blocklist entry: force GLES/disable feature for renderer+driver; report to vendor |
| Crash on some Android 15+ devices at native load | `.so` not 16 KB aligned | Rebuild with NDK r28+/AGP 8.5.1+; verify alignment |
| 120 Hz never engages on iPhone | Missing Info.plist key or `preferredFramesPerSecond` used | `CADisableMinimumFrameDurationOnPhone`, `preferredFrameRateRange` |
| Install conversion drops after update | Download size jumped | Move content to PAD/Background Assets/remote; size gate in CI |
| Cold start > 5 s mid tier | Main-thread SDK init, large boot scene, shader compile | Lazy init, tiny boot scene, shader warmup cache |
| Battery complaints | Uncapped fps in menus, busy-wait loops, radios polling | 30 fps (or on-demand rendering) in menus; batch network |

## Anti-Patterns

**The Flagship Benchmark** — budgets measured on the team's phones. The median player owns a device two tiers lower.

**Peak-FPS Optimism** — measuring the first minute. Thermals arrive at minute ten; the sustained number is the only number.

**Average-Only Reporting** — reporting mean fps. Players feel p99 frame time and pacing, which averages hide.

**Preset Thermal Response** — dropping from High to Low preset on throttle. Step one knob at a time with hysteresis, or quality oscillates every few seconds.

**Invisible OOM** — counting only crashes the reporter sees. Jetsam and LMK kills are the largest crash category many games never chart.

**Hardcoded Device Lists** — tiers and blocklists compiled into the binary. A new driver bug then needs a store release instead of a config push.

**Debug-Build Profiling** — tuning a development build with profiler attached. Different code generation, different memory, wrong conclusions.

**Size Creep** — no size budget in CI. Each feature adds 5 MB until the store binary crosses a cellular-download prompt or the 200 MB base module.

**Deadline Surprise** — target API, 16 KB pages, billing library versions discovered at submission. Track store deadlines a quarter ahead.

## Quality Checklist

- [ ] Tier model derived from install data; tier assignment server-side with benchmark fallback
- [ ] Budget sheet exists per tier: CPU, GPU, memory, thermal, battery, cold start, size
- [ ] Device matrix covers ≥ 70–80% of installs per tier plus each GPU family and a worst-case device
- [ ] All performance numbers from release builds on device, with minute-of-soak recorded
- [ ] 20–30 minute soak test run per tier before each release
- [ ] Adaptive quality ladder uses ADPF headroom / `thermalState` with hysteresis
- [ ] ProMotion configured (Info.plist key + `preferredFrameRateRange`) if 120 Hz is a target
- [ ] Frame pacing library or engine pacing enabled on Android
- [ ] OS memory kills counted in dashboards alongside crashes
- [ ] Crash and ANR rates below Play thresholds overall and per device model
- [ ] Target API 36, 16 KB alignment verified on every `.so`
- [ ] GPU blocklist is remote-configurable and keyed by renderer + driver + model
- [ ] Download/install size tracked per build with a CI threshold
- [ ] CI perf gate on fixed devices fails on p90 frame time or peak memory regression
- [ ] Field telemetry shows p50/p90/p99 per device model, reviewed weekly
- [ ] OS support floors documented with share data and review cadence

## Related Skills

Unity-side fixes (allocations, Addressables, URP assets, IL2CPP) go to `gamedev-unity-engineer`; loop structure and frame scheduling decisions to `gamedev-engine-architect`. `gamedev-technical-artist` owns shader, texture, LOD and draw-call budgets once this skill has set the tier totals. Native platform depth goes to `gamedev-ios-engineer`, `gamedev-metal-graphics-engineer` and `gamedev-android-engineer`. `gamedev-hud-engineer` owns UI rebuild and overdraw costs inside the frame budget; `gamedev-audio-designer` owns audio memory and CPU. `gamedev-qa-verifier` runs the device matrix and soak suites; `gamedev-delivery-release` wires size and perf gates into release pipelines and tracks store deadlines; `gamedev-analytics-engineer` builds the per-device telemetry dashboards. If installed, `mobile-game-ux-designer` covers perceived performance (loading feedback, input response) and `game-asset-art-director` turns texture-memory and overdraw limits into art direction.
