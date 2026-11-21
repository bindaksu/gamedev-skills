---
name: gamedev-react-native-engineer
description: >-
  Build and ship games on React Native and Expo with Skia, Reanimated worklets and Hermes: deciding
  when React Native fits a game, a deterministic TypeScript or native (Rust via JSI, wasm in Node)
  simulation core, frame loops on the UI runtime, Metro inline requires in hot loops, worklet
  serializer leaks, per-runtime heaps, the Skia GPU resource cache versus prebaked tiles, Expo
  modules and config plugins, expo-iap and expo-audio, release environment switches, OTA updates
  versus store review, and Vitest or Jest sim suites with Maestro or XCUITest. Use when a user asks
  whether React Native or Expo suits a game, structures an Expo game or sim core, chases jank, memory
  growth, crashes or slow sim throughput on device, writes a config plugin or native module, wires
  purchases or audio, sets an OTA policy, or ships an Expo game to the App Store, Apple Arcade or
  Google Play.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.1.0"
  category: client-eng
---

# React Native Game Engineer

A React Native game is an app with a game inside it, and the app's plumbing is shared with the game. The JS thread runs React, gesture callbacks, timers, network code and, unless you move it, the simulation. Hermes interprets your hot loop. Skia draws on the UI thread from values that cross a runtime boundary. Every crossing, every allocation in a frame callback and every texture over the GPU cache shows up as jank, memory growth or a kill with no crash report. The build is part of the game too: Expo config plugins, precompiled native modules, `.env` files and Xcode upgrades break React Native games at release time more often than gameplay code does. The job is to keep the simulation pure and deterministic, drive frames on the UI runtime with no per-frame crossings, budget GPU and heap memory per runtime, and make the release lane prove what is inside the signed archive.

## Role Profile

No posting research backs this seat; the profile is [inference] from shipped React Native/Expo games in UI-heavy 2D genres. The seat is usually a TypeScript product engineer who learned frame budgets, or a game engineer who learned the React Native build. Both halves are required.

| Dimension | What it looks like |
| --- | --- |
| Responsibilities | Fit decision; package layout and sim core boundary; thread and runtime plan; Skia render path; native modules and config plugins; build flavors and release lane checks; purchases, audio, haptics; OTA policy; test lanes |
| Hard skills | TypeScript, React and hooks, Reanimated and worklets, Skia, Hermes behaviour, Metro, Expo modules (Swift/Kotlin), Xcode and Gradle basics, optionally Rust or C++ over JSI |
| Tools | Expo CLI and prebuild, React Native DevTools, Instruments, Android Studio profilers, Vitest or Jest, Maestro, XCUITest |
| KPIs [inference] | Presented-frame p95 on floor devices; memory growth per soak; crash-free sessions; sim days per second at top speed; release-lane defects caught before upload |
| Collaborators | Game and sim designers, engine-architect, iOS and Android platform seats, backend, QA, release engineering |

## When to Use / Not

Use for games and game-like apps built on React Native or Expo: fit decisions, project and sim-core structure, Skia and Reanimated render paths, performance and memory on device, Expo modules and config plugins, build flavors, purchases and audio through Expo libraries, OTA policy, and test lanes.

Not for:
- Engine choice across Unity, Godot, native and React Native, determinism and save design: `gamedev-engine-architect` (this seat implements them on Hermes).
- Swift-side platform services, App Review rules, Apple Arcade requirements: `gamedev-ios-engineer`; Android platform work and Play policy: `gamedev-android-engineer`.
- Receipt verification, refunds and entitlement ledgers: `gamedev-backend-engineer`.
- Device tiers and budgets: `gamedev-optimization-compatibility`; lanes, signing and submission: `gamedev-delivery-release`.
- Games on Unity or Godot: `gamedev-unity-engineer`, `gamedev-godot-engineer`.

## Inputs to Gather

- **Genre and render load:** units or sprites on screen, map size and zoom range, 2D or 3D, real-time or turn-based. Default: 2D, UI-heavy, under ~1,000 animated sprites per frame.
- **Stack versions:** Expo SDK, React Native, Skia, Reanimated and worklets, Hermes, Architecture (Fabric is the default). Default: current Expo SDK (58 as of 2026-11; verify).
- **Sim profile:** ticks per second, top game speed, campaign horizon, determinism needs (replays, server validation, cross-engine goldens).
- **Targets and flavors:** App Store, Apple Arcade, Google Play, iPad app on Mac, evaluation builds. Default: one flavor per store and edition.
- **Device floor:** oldest iPhone and Android device, RAM, refresh rate.
- **Native needs:** purchases, Game Center, iCloud or CloudKit saves, haptics, audio, analytics.
- **Release lane:** EAS or a local signed lane; who uploads; which gates exist.
- **OTA appetite:** what the team wants to change without a store build.

## Method

1. **Decide fit before building.** Score the game against the fit table below. Card, word, puzzle, management, strategy-map, cozy-builder and companion games fit; physics action, 3D, rhythm and fighting games do not. Record the decision and its reverse-if condition; escalate a poor fit to `gamedev-engine-architect`.
2. **Pin the stack and treat upgrades as projects.** Move one Expo SDK at a time on a branch; record Xcode and SDK per archive; when either changes, launch the exact signed build on a device running the newest OS before upload. Builds linked against the iOS 27 SDK must adopt the UIScene life cycle (as of 2026-11; verify).
3. **Split the pure core from the app.** The sim lives in a package with no React Native imports, no wall-clock and no `Math.random()`; it runs unchanged in Node and Hermes. Commands in, plain-data state out.
4. **Choose where the sim runs.** Time-sliced on the JS thread (yield every 10-15 ms), on a worklet runtime, or in a native core over JSI. Pick by measured tick cost at top speed on the floor device.
5. **Exempt hot sim modules from inline requires.** React Native's default Metro config inlines requires, turning every imported-binding read into a call. Blocklisting hot modules restored 15-26% sim throughput in one sim; keep the barrel inline for cold start.
6. **Keep the frame path on the UI runtime.** Shared values and Skia drawing; worklets defined once; no inline worklets in frame callbacks; nothing serialized per frame; HUD text pushed to React at 10 Hz or less.
7. **Decouple drawing at fast-forward.** Non-visual readers consume every tick; the map draws the newest state at most every Nth tick, with a hold of 500 ms or less, only while the clock is behind its target rate.
8. **Budget GPU memory explicitly.** Choose vectors, pictures, atlases or prebaked tiles per layer; keep the resident texture set per zoom band under the Skia resource cache; decode images asynchronously; never `dispose()` from JS what the UI thread may draw; hunt native crashes with AddressSanitizer in Release-configured builds.
9. **Measure every heap.** RN runtime, UI runtime, worker runtimes and native footprint separately. Soak at top speed across the campaign horizon, report growth per simulated day, and compare with a fresh process loading the late save.
10. **Go native by phase, not by kernel.** When the core moves to Rust or C++, port whole phases over shared memory and promote each on byte parity; leaf kernels called per entity lose their gain to marshalling.
11. **Make determinism hold on every engine.** Total-order sorts with a stable-ID tie-break, sim math through project helpers, and one parity corpus checked in Node, Hermes on device and the native port.
12. **Own the native surface through Expo modules and config plugins.** Each flavor declares the entitlements, plist keys and modules it must and must not have; strip what modules add on their own; mark native patches and require the marker in the archive.
13. **Lock the release environment.** Disable `.env` loading in the lane, set every `EXPO_PUBLIC_*` switch explicitly, and grep the built bundle for forbidden strings.
14. **Wire purchases, audio and haptics defensively.** Purchase listener at launch, finish only after the server grants; test as guest and as a refunded player; Arcade and no-purchase flavors link no purchase module. Pool audio players created at load; set the audio mode once; fire haptics without awaiting.
15. **Write the OTA policy.** Fingerprint runtime versions, one channel per flavor, a table of what may ship OTA, rules revisions stamped into saves and replays, and emergency-launch telemetry.
16. **Test in layers and gate on the full suite.** Vitest or Jest sim suites with the parity corpus, component tests, Maestro flows, XCUITest for multi-touch; the full suite before every submission, with lost tests counted as failures.

## Deliverables

### 1. Fit decision record

```text
GAME:          [genre, sprites/frame peak, map size, zoom range, top game speed]
FIT SCORE:     render load [ok/risk]  input latency [ok/risk]  sim cost [ok/risk]  team [TS/React yes/no]
DECISION:      React Native + Expo + Skia, sim core in [TS | Rust via JSI]   or   hand to engine-architect
REVERSE IF:    [e.g. p95 presented frame > 33.4 ms on floor device at peak scene after optimization pass]
OWNER / DATE
```

### 2. Thread and runtime map

```text
JS (Hermes):       React, navigation, store, network, [sim if sliced: budget 10-15 ms per slice]
UI runtime:        Skia drawing, gestures, camera, frame callbacks          heap sampled: [how]
Worker runtime(s): [sim | pathing | save encode]                           heap sampled: [how]
Native:            [Rust/C++ core via JSI], Skia GPU cache [MB], audio, decoded images
Crossings/frame:   [0 target]   JS<-UI updates: [Hz, payload]   UI<-sim: [per sim tick]
```

### 3. Build flavor sheet

```text
Flavor      │ Channel   │ EXPO_PUBLIC_* set           │ Modules in            │ Entitlements must / must not   │ Archive checks
store       │ prod      │ API_URL, EDITION=store, ... │ expo-iap, analytics   │ GC / aps-environment if unused │ scene manifest, patch markers, bundle strings
arcade      │ arcade    │ EDITION=arcade, ...         │ no purchase, no ads   │ GC, iCloud / no IAP            │ zero purchase module, zero ad SDKs
evaluation  │ none      │ EDITION=eval                │ no purchase           │                                │ refused by attach-to-version script
```

### 4. Perf evidence record

```text
DEVICE: [model, OS, refresh]  BUILD: [Release, commit]  POWER: [battery %, LPM off, thermal]  HOST: [n/a | sim]
KEEP/REVERT RULE (written before measuring): [metric, threshold, runs]
BASELINE: last shipped build, same phone, same day: [p50/p95 presented frame, sim days/s, footprint]
CANDIDATE: [same metrics]   PAIRED CONFIRMATION RUNS: [n, result]
HEAPS: RN [..] MB  UI [..] MB  worker [..] MB  native footprint [..] MB  growth/sim-day [..]
VERDICT: keep | revert
```

Read `references/core-and-rendering.md` when laying out packages, configuring Metro, choosing where the sim runs, writing worklets or frame callbacks, sizing Skia layers and the GPU cache, profiling heaps, porting to a native core, or building cross-engine parity tests. Read `references/expo-build-release.md` when writing config plugins, the release lane and its archive checks, purchase, audio or haptics code, the OTA policy, or Maestro and XCUITest suites.

## Technical Reference

### Stack facts (as of 2026-11; verify at https://docs.expo.dev/versions/latest/ and https://www.npmjs.com)

| Package | npm latest on 2026-11-21 |
|---|---|
| expo (SDK) | 58.0.26 |
| react-native | 0.88.1 |
| @shopify/react-native-skia | 2.14.0 |
| react-native-reanimated / react-native-worklets | 4.8.0 / 0.14.0 |
| expo-iap | 6.5.1 |
| expo-audio | 58.0.12 |

Older SDK 57 builds still ship. Pin exact versions of expo, react-native, Skia, Reanimated with worklets, expo-iap and expo-audio together, and upgrade them as one set. Skia's GPU resource cache cap is set by the host, and some apps patch it. expo-iap's API changes across majors, so re-test purchases on every bump. Use expo-audio, not the older expo-av.

Hermes runs Release bytecode; Fabric is the default renderer. Arcade does not mandate an engine [inference]: a React Native build with a native core loaded through JSI is constrained by what it links (no purchase or ad modules in the Arcade flavor), not by the framework.

### Fit table

| Factor | Fits React Native | Does not fit |
|---|---|---|
| Render load | UI-heavy 2D; up to ~1,000 atlas sprites; static maps as pictures or tiles | 3D, thousands of independently animated sprites, heavy particles |
| Input | Taps, drags, pinches; turn-based or forgiving timing | Frame-exact input: rhythm, fighting, precision action |
| Sim | Deterministic TS core, or native core over JSI for heavy sims | Physics-driven gameplay needing an engine solver |
| Team | TypeScript and React skills; shared code with web or server | Team fluent in an engine and its tools |
| Content tools | Data-driven content; designers edit JSON or sheets | Level editors, animation timelines, particle editors needed in-house |
| Platforms | iOS, iPadOS, iPad app on Mac, Android | Consoles; Steam needs a separate desktop shell [inference] |

### Budgets and numbers

| Item | Value | Note |
|---|---|---|
| JS slice | 10-15 ms then yield | Long passes otherwise stall timers and touches |
| JS updates from UI runtime | 10 Hz or less for HUD text | Per-frame crossings show up as jank |
| Skia GPU resource cache | 256 MB default (Ganesh) | No JS setter in react-native-skia 2.14; native patch only |
| Fast-forward draw hold | 500 ms or less | Draw newest state only while behind target rate |
| Memory growth slope | e.g. under 25 MB between soak minutes 10 and 30 | Peak-only budgets pass a leak |
| 60 Hz frame p95 | reads only 16.7 or 33.4 ms | Judge presented frames |

## Diagnostics

| Symptom | Likely cause | Fix |
|---|---|---|
| Sim throughput 15-25% lower on device than expected | Inline requires in hot sim modules | Blocklist the hot modules in Metro; measure Release on device |
| Jank whenever the HUD updates | Sim or UI runtime pushing state to React every frame | HUD at 10 Hz or less, small slices of state |
| Memory climbs while a gesture or animation runs | Inline worklets or fresh objects serialized each frame; retained senders keep native copies | Define worklets once; send ids and typed arrays; no inline worklets in frame callbacks |
| JS heap flat, app still killed after minutes | Growth in the UI or worker runtime heap, or native textures | Sample every runtime and the native footprint |
| Killed at top game speed with no crash report | Leak that scales with simulated time | Soak at top speed over the horizon; fresh-process comparison of the late save |
| Pan p99 got worse after switching to prebaked tiles | Tile working set above the GPU resource cache; re-upload on every pan | Resident set per zoom band under the cache; compressed formats; vectors for the largest layers |
| Random native crash in Skia, mostly in Release | JS disposed an object the UI thread still draws; image decoded on the UI thread | Never dispose from JS; async decode; AddressSanitizer Release build |
| Patched native behaviour missing in the store build | Module linked precompiled, so the source patch never compiled | Marker string in the patch, required in the archive |
| Release build talks to staging or shows a dev menu | `EXPO_PUBLIC_*` switch unset in the lane, filled from a `.env` file | `EXPO_NO_DOTENV=1`; set every switch; grep the bundle |
| Crash at launch only on the newest iOS after an Xcode bump | New SDK requires the UIScene life cycle (iOS 27 SDK, as of 2026-11) | Scene manifest check; launch signed build on newest OS |
| Entitlement present that the app never uses | A module's config plugin added it | Strip it with a plugin; check `codesign -d --entitlements` |
| Buy button does nothing for some players | Guest or signed-out state disables purchase silently | Explain on tap; test as guest and refunded player |
| Goldens pass in Node, fail on device | Sort ties or engine-approximated math differ between engines | Total-order sorts; math helpers; corpus on every engine |
| Native kernel 10x faster, whole sim slower | Per-call marshalling across the JS boundary | Port whole phases over shared memory |
| Crash after the wasm core grows its memory | Typed-array views over the detached buffer | Re-create views after calls that can grow memory |
| Seconds-long JS stalls during cloud sync | Sync pass never yields | Yield every 10-15 ms; pause while a world loads |
| UI test says an element is visible, tap misses | Maestro counts below-the-fold elements as visible | Scroll until visible before asserting |
| OTA update crashes old binaries | JS shipped to a runtime without the native code it needs | Fingerprint runtime policy; channel per flavor |

## Anti-Patterns

**React as the Game Loop** — driving each frame through state updates and re-renders. React schedules commits, not frames; keep frames on the UI runtime.

**Inline Everything** — default inline requires on the hot sim modules. Every helper call in the tick loop pays for a require.

**The Per-Frame Worklet** — creating worklets or serializing fresh objects inside frame callbacks. Memory grows and frames stutter.

**Tile Everything** — prebaking every layer to raster to save rasterization, then thrashing the GPU cache.

**Leaf-Kernel Port** — moving the hottest inner function to native while JS still calls it per entity.

**Dotenv Release** — release lanes that rely on whatever `.env*` files exist on the build machine.

**Patched in Source Only** — trusting a patch file without checking the archive it was supposed to change.

**OTA as Feature Pipeline** — shipping features or rule changes over the air that change review-relevant behaviour or break saves and replays.

## Quality Checklist

- [ ] Fit decision recorded with a reverse-if condition
- [ ] Expo SDK, React Native and native libraries pinned; upgrades on a branch, one SDK at a time
- [ ] Sim core has no React Native imports, wall-clock reads or `Math.random()`
- [ ] Hot sim modules exempt from inline requires; throughput measured on a Release device build
- [ ] Frame callbacks allocate nothing, create no worklets and cross to JS at most at HUD rate
- [ ] Fast-forward draws are decoupled from ticks
- [ ] Skia resident texture set per zoom band fits the GPU cache; images decoded asynchronously; no JS dispose of drawn objects
- [ ] Every runtime heap and the native footprint sampled; soak at top speed with growth per simulated day
- [ ] Parity corpus passes in Node, Hermes on device and the native port; sorts have total orders
- [ ] Each flavor's modules and entitlements declared; extras stripped; signed archive checked
- [ ] Native patch markers present in the archive
- [ ] Release lane disables `.env` loading, sets every `EXPO_PUBLIC_*` switch, greps the bundle
- [ ] Toolchain change check run; signed build launched on the newest OS when Xcode or SDK changed
- [ ] Purchase listener at launch; finish after server grant; guest and refunded-player tests pass
- [ ] Arcade and no-purchase flavors link no purchase or ad modules
- [ ] Audio players pooled and created at load; haptics never awaited on gesture or frame paths
- [ ] OTA policy written: fingerprint runtime, channel per flavor, emergency-launch telemetry
- [ ] Full suite, Maestro flows and XCUITest gesture tests pass before submission

## Related Skills

Engine choice, determinism, tick model and save design: `gamedev-engine-architect`. Apple services, App Review and Arcade requirements: `gamedev-ios-engineer`; Android platform layers: `gamedev-android-engineer`; iPad-on-Mac and desktop distribution questions: `gamedev-desktop-engineer`. Purchase verification and entitlements: `gamedev-backend-engineer`; offer design: `gamedev-monetization-designer`. Frame and memory budgets and device tiers: `gamedev-optimization-compatibility`; Skia layer art and texture formats: `gamedev-technical-artist`; GPU-level renderer questions on Apple hardware: `gamedev-metal-graphics-engineer`. HUD structure: `gamedev-hud-engineer`; screen layout for resizable iPad and Mac windows: `gamedev-ui-designer`. Lanes, signing and submission: `gamedev-delivery-release`; test strategy: `gamedev-qa-verifier`; telemetry events: `gamedev-analytics-engineer`. Generated art and audio entering the bundle: `gamedev-ai-asset-pipeline`; coding agents sharing devices and lanes: `gamedev-agentic-production`. A game that needs an engine instead: `gamedev-godot-engineer` or `gamedev-unity-engineer`.
