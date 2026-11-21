---
name: gamedev-godot-engineer
description: >-
  Build and ship Godot 4 games on iOS, Android, Mac and Steam: project layout, GDScript versus C#
  versus GDExtension, export presets and the traps that appear only in exported builds (imported-only
  resources, FileAccess ignoring import remaps, native plugins missing from clean checkouts), iOS
  plugins and macOS godot-cpp GDExtensions, GodotSteam, Mac App Store packaging, gamepad UI input,
  glyph priming, translation overrides, accessibility APIs, GUT tests, and release gates such as an
  audio peak probe and store-symbol checks. Use when a user structures or audits a Godot project,
  sees an asset, sound or plugin work in the editor but not in the export, wires a native plugin or
  Steamworks, prepares a Godot build for the App Store, Mac App Store or Steam, or sets up headless
  Godot tests and gates in CI.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.1.0"
  category: client-eng
---

# Godot Engineer

Godot is fast to build in and easy to ship wrong. The editor resolves every path, imports every file, loads every plugin and plays every sound; the exported build does none of that for you. Exports carry only imported resources, `FileAccess` does not follow import remaps, a native plugin missing from a clean checkout is skipped without an error, and a headless CI run reports zero draw calls and never reaches a speaker. In shipped Godot projects the costliest defects were of exactly this kind: builds that exported with no sound, store builds without their store plugin, Mac packages rejected on plist keys and file modes. The job is to make the export the thing you test: pin the engine, run every gate against exported builds, prove native code and sound by inspecting and measuring the artifact, and keep the simulation in plain classes that tests can drive without a scene.

## Role Profile

No posting research backs this seat; the profile is [inference] from Godot projects shipping to mobile, Mac and Steam. In small studios the Godot engineer is the whole client team: gameplay code, the engine-facing architecture, export presets, native glue, and the build lane. Larger teams split gameplay from a tools-and-platform engineer who owns exports, GDExtensions and CI.

| Dimension | What it looks like |
| --- | --- |
| Responsibilities | Project layout and autoloads; language choice per layer; export presets per store and edition; iOS plugins and GDExtensions; GodotSteam; input maps; fonts, translations and accessibility wiring; headless tests; release gates on exported artifacts |
| Hard skills | Typed GDScript, scene and resource model, signals, `WorkerThreadPool`; C++ with godot-cpp or C#; Xcode projects, codesign and plists; SCons; shell for gates |
| Tools | Godot editor and export templates, GUT, Godot profiler and monitors, Xcode and Instruments, Android Studio, Steamworks partner site |
| KPIs [inference] | Exported-build defects per release; gate pass rate on first run; crash-free sessions; frame time on floor devices; cold start |
| Collaborators | Design, art and audio (import settings), desktop and iOS platform seats, QA, release engineering |

## When to Use / Not

Use for Godot 4 client code and project structure, export presets, native plugins and GDExtensions, GodotSteam, Godot-side input, text, translation and accessibility wiring, GUT tests, and gates that run on Godot exports.

Not for:
- Engine-agnostic loop, determinism, save formats and engine choice: `gamedev-engine-architect`.
- Steamworks policy, Deck and Steam Machine verification, notarization and desktop input design: `gamedev-desktop-engineer`.
- App Review rules, StoreKit, Game Center and Apple Arcade requirements: `gamedev-ios-engineer`; Play policy and Android platform layers: `gamedev-android-engineer`.
- Shaders, VFX, texture compression and import budgets owned by art: `gamedev-technical-artist`.
- CI infrastructure, signing secrets and store submission: `gamedev-delivery-release`; test strategy and device matrix: `gamedev-qa-verifier`.
- Games on Unity or React Native: `gamedev-unity-engineer`, `gamedev-react-native-engineer`.

## Inputs to Gather

- **Engine build:** exact version string and export templates. Default: the newest 4.7.x stable (4.7.2 as of 2026-11; verify at https://github.com/godotengine/godot/releases).
- **Targets and editions:** iOS, Android, Mac (Steam, Mac App Store), Windows/Linux (Steam), plus editions such as no-purchase, Arcade or demo. Default: one export preset per store per edition.
- **Languages:** GDScript only, C#, or GDExtension (C++/Rust). Default: typed GDScript, GDExtension only for named hot paths or SDKs.
- **Native dependencies:** store, Steam, analytics, Game Center, haptics; where each binary comes from and whether it is in git.
- **Device floor and frame target** from `gamedev-optimization-compatibility`. Default: 60 fps on the floor phone, physics at 60 Hz with interpolation on.
- **Input:** touch, mouse and keyboard, gamepad. Default: all actions reachable by gamepad on desktop builds.
- **Languages and fonts:** locales, CJK or RTL, dynamic font sizes.
- **CI:** where exports run (macOS runner for Apple targets), which gates exist, who can upload.

## Method

1. **Pin the toolchain.** Commit the exact engine build string, export template version, add-on versions and a hash for every native binary. Re-run a headless API probe after every engine bump and at each milestone, so a renamed method fails a script, not a player session (`references/export-native-release.md` §2).
2. **Keep the simulation out of the scene tree.** Put rules and state in typed `RefCounted` classes or static functions, advanced by fixed ticks; scenes and nodes present that state. Turn on physics interpolation for moving bodies. This is what makes headless tests, saves and replays cheap. Tick and determinism design comes from `gamedev-engine-architect`.
3. **Choose the language per layer.** Typed GDScript with untyped-declaration warnings raised to errors for game code; GDExtension (godot-cpp) for measured hot loops and SDK wrappers; C# only when the team is C#-first and every target platform supports it in your engine version (check the current platform table).
4. **Wire signals to methods, never lambdas.** Pass context with `bind()`. A lambda connection cannot be found again to disconnect, so hidden or pooled screens keep receiving it (`references/gdscript-patterns.md` §1).
5. **Treat the export as the product.** Load assets only through `load()` or `ResourceLoader`; reserve `FileAccess` for your own data files listed in the export filter; list folders with `ResourceLoader.list_directory()`. Export a pack in CI and run a selftest inside it that loads every required asset.
6. **One preset per store and edition.** Each preset names its feature tags, export filters, native libraries, entitlements and a forbidden-code list. Never toggle stores with runtime flags inside one preset.
7. **Separate iOS plugins from macOS GDExtensions.** iOS: one plugin per framework. macOS: godot-cpp libraries with feature-tagged keys for debug and release, built with the template's target and precision and matching defines. Never link one library through both paths.
8. **Fail on missing native binaries before export, and on wrong code after archive.** Check a hash manifest of untracked artifacts before exporting; after archiving, check linked frameworks, marker classes and plist keys per edition. A no-purchase or Arcade edition must contain zero store code.
9. **Prove sound by measurement.** Run a master-bus peak probe inside every exported pack and fail at -60 dB or quieter; headless runs still mix (checked on 4.7.2), so CI catches engine-side silence, and one run per platform on hardware catches output problems. Load counters and "is playing" flags do not detect a silent build.
10. **Map input to actions and add gamepad events yourself.** The 4.7.2 default `ui_accept` has no gamepad button (checked headless); add confirm and cancel buttons explicitly and switch glyphs to the last device used.
11. **Prime text and layer translations correctly.** Draw each font size's glyphs once at the viewport's real oversampling behind the loading screen, and re-prime when it changes. Add override translations before the OptimizedTranslation they override: for one locale the first-added translation wins.
12. **Wire accessibility.** Give focusable Controls `accessibility_name` and `accessibility_description` from the string table; poll the OS reduce-motion, contrast and transparency preferences about once a second (tri-state, no change signal); the in-game setting overrides the OS; tests that pin a value stop the poll.
13. **Measure performance windowed, on devices.** Headless runs report zero draw calls; use them only for load time and sim throughput. Run every wall-clock test in a fresh process with one worker and record host load.
14. **Save safely.** Version the envelope (engine-architect seat); write on a worker with one write in flight and the newest state winning; compare canonical bytes before writing or pushing to the cloud, because JSON parsing turns every number into a float.
15. **Package per store.** Steam: GodotSteam only in Steam presets, Steam library signed inside the app, no sandbox. Mac App Store: sandbox, embedded profile, top-level minimum OS key, world-readable files, macOS added to the app record before the first upload. iOS: record Xcode and SDK per archive and launch the exact signed build on the newest OS when they change. Android: Gradle build export to an AAB, plugins as AARs, every native library 16 KB aligned.
16. **Gate on the full suite before every submission.** Targeted test lists drift; run the full GUT suite plus export, audio and archive gates, parse every failure line, and list known failures one per line with a reason.

## Deliverables

### 1. Toolchain pin sheet

```text
ENGINE:          4.7.[x].stable.official.[hash]   templates: same   pinned on: [date]
ADD-ONS:         GUT [ver] | GodotSteam [ver] / Steamworks SDK [ver] | godot-cpp [ver] | [other]
NATIVE BINARIES: [path] sha256 [..] built from [repo@commit] by [command]      (one line each)
FLOORS:          iOS [ver]  macOS [ver] universal  Android minSdk [..]
XCODE / SDK:     [Xcode build] [SDK name]  per archive, compared with last shipped
API PROBE:       tools/api_probe.gd  last run [date] on [engine string]: PASS
```

### 2. Export matrix

```text
Preset        │ Feature tags        │ Native libs            │ Entitlements / plist          │ Must contain        │ Must not contain
iOS-Store     │ ios, store          │ StoreBridge            │ Game Center                   │ StoreKit, bridge    │ libsteam_api
iOS-Arcade    │ ios, arcade         │ (none store-related)   │ Game Center, iCloud           │ GameKit             │ StoreKit, ad SDKs
Mac-Steam     │ macos, steam        │ GodotSteam             │ hardened runtime, no sandbox  │ libsteam_api        │ StoreKit
Mac-AppStore  │ macos, mas          │ StoreBridge (desktop)  │ App Sandbox, profile embedded │ LSMinimumSystemVersion │ libsteam_api
Android-Play  │ android, store      │ billing plugin (AAR)   │ minimal permissions           │ billing classes     │ libsteam_api; .so not 16 KB aligned
Win-Steam     │ windows, steam      │ GodotSteam             │ n/a                           │ steam_api64         │
Filters (all): *.json, *.txt data    Selftest: tests/export_selftest.gd    Audio probe: [cue]
```

### 3. Native extension contract

```text
FEATURE:       [store | haptics | Game Center | analytics]
PLATFORMS:     iOS plugin [name] (one framework) | macOS GDExtension [name] (universal) | other: stub
GDSCRIPT API:  [autoload or singleton name, methods, signals]
BUILD:         target [template_debug/template_release]  precision [single]  defines [..]  floor [..]
ABSENT:        behaviour when the binary is missing: [stub that logs once | hard fail in release]
ARCHIVE CHECK: marker class [..] or framework [..] required in [presets], forbidden in [presets]
```

### 4. Release gate record

```text
BUILD:          [preset] [version/build] from [full commit hash]  tree clean: [yes/no]
GUT FULL SUITE: [passed]/[total]  failures parsed: [n]  known failures: [list with reasons]
EXPORT SELFTEST:[pass/fail]   NATIVE MANIFEST: [pass/fail]   ARCHIVE CHECK: [edition] [pass/fail]
AUDIO PROBE:    peak [..] dB (threshold -60 dB)  on [device/window]
LAUNCH CHECK:   signed build launched on [device, OS]  content screen seen: [yes/no]
VERDICT:        PASS only if every line above passed
```

Read `references/gdscript-patterns.md` when writing signal wiring, gamepad menu input, glyph priming, translation overrides, accessibility polling, the audio probe, save writing or GUT and wall-clock tests. Read `references/export-native-release.md` when configuring presets and filters, adding an iOS plugin or GDExtension, wiring GodotSteam, writing the native-artifact and archive checks, or packaging for the Mac App Store, Android or iOS.

## Technical Reference

### Godot version facts (as of 2026-11; verify at https://github.com/godotengine/godot/releases)

| Release | Date (GitHub release) | Notes |
|---|---|---|
| 4.5 | 2025-09-15 | Shader baker, stencil buffer, partial AccessKit screen-reader support |
| 4.6 | 2026-01-26 | Jolt default for new 3D projects, LibGodot embedding, C++ tracing profiler |
| 4.7 / 4.7.1 / 4.7.2 | 2026-06-18 / 2026-07-14 / 2026-08-18 | 4.7.2 is the newest stable on the release page as of 2026-11-21 (verify) |

Pin exact versions of the engine build, GUT (https://github.com/bitwes/Gut), GodotSteam with its Steamworks SDK (https://godotsteam.com) and godot-cpp together, and bump them as one set; check each upstream release page before pinning (as of 2026-11; verify).

### Language choice

| Option | Use for | Watch out |
|---|---|---|
| Typed GDScript | Gameplay, UI, tools, most sims | Raise untyped-declaration warnings to errors; profile hot loops before porting |
| GDExtension (godot-cpp) | Measured hot loops, SDK wrappers on desktop | Build per target and precision; feature-tagged library keys; signing on macOS |
| iOS plugin | Apple SDKs on iOS (StoreKit, GameKit, haptics) | One framework per plugin; format differs across 4.x |
| C# | C#-first teams | Check platform support for every target in your version before committing |
| Rust (godot-rust) | Teams with a Rust core | Third-party binding; check its Godot version support [inference] |

### Behaviour checked on 4.7.2 (headless)

| Fact | Consequence |
|---|---|
| Default `ui_accept` = Enter, keypad Enter, Space | Add gamepad confirm and cancel buttons |
| `JSON.parse_string("{\"a\":1}")` re-serializes as `{"a":1.0}` | Canonicalize numbers before comparing or hashing saves |
| `OptimizedTranslation.add_message()` is a no-op; first translation per locale wins | Add overrides before the base |
| `DisplayServer.accessibility_should_*()` return -1 headless; no change signal | Poll; treat -1 as off |
| `physics/common/physics_interpolation` defaults to off; physics ticks 60 | Turn interpolation on for moving bodies |
| `Viewport.oversampling` read-only, `oversampling_override` settable | Prime glyphs after oversampling is final |
| Lambdas never compare equal | Connect signals to methods |

## Diagnostics

| Symptom | Likely cause | Fix |
|---|---|---|
| Asset or data file works in the editor, missing in the export | `FileAccess` or `Image.load()` on an imported file; data file not in the export filter | `load()`/`ResourceLoader`; add the filter; run the export selftest |
| Folder listing empty or full of `.import`/`.remap` names in the export | `DirAccess` on imported assets | `ResourceLoader.list_directory()` |
| Data CSV gone from the export | CSV imported as a translation by default | Set that file's Import As to "Keep File (exported as is)" |
| Export plays no sound though players report playing | Streams or bus layout not exported, stream loaded via `FileAccess`, muted bus | Master-bus peak probe in every exported pack plus once per platform on hardware; fail at -60 dB or quieter |
| Store or Steam features silently absent in a CI build | Untracked native binary missing from the clean checkout; the engine skips the plugin | Hash manifest checked before export; archive check after |
| No-purchase or Arcade build contains store code | Plugin included in every preset | Per-preset plugins; forbidden-code list in the archive check |
| GDExtension loads in debug, fails in release exports | No `macos.release` key, or library built for another target or precision | Feature-tagged keys for both; match target and precision |
| Duplicate-symbol link errors in the iOS project | Two frameworks in one plugin, or one library via plugin and GDExtension | One plugin per framework; one link path per library |
| Gamepad moves menu focus but confirm does nothing | Default `ui_accept` has no gamepad button | Add gamepad events to `ui_accept`/`ui_cancel` |
| Hitch the first time a screen or language shows text | Glyphs rasterized on first draw, or primed at the wrong oversampling | Glyph primer after stretch settles; re-prime when oversampling changes |
| Hotfix string never appears | Override added after the OptimizedTranslation | Add overrides first |
| Handler fires while its screen is hidden or pooled; disconnect fails | Lambda connection, which cannot be found again to disconnect | Method plus `bind()`; disconnect on close |
| Draw-call budget test always passes in CI | Headless renderer reports 0 draw calls | Run render budgets windowed on hardware |
| Wall-clock tests fail at random | Warm caches from earlier tests; loaded host | One process per test, one worker, host load recorded |
| Reduced-motion test passes alone, fails in the suite | The OS preference poll overwrote the pinned value | Pin through a method that stops the poll |
| Hitch once per second while cloud saves are on | Echo loop: JSON floats make every merge look like a change | Canonical bytes; push only changes; apply off the main thread |
| Mac App Store upload rejected | Only per-architecture minimum-OS keys, root-only file modes, or macOS missing from the app record | Top-level `LSMinimumSystemVersion`; `chmod -R a+rX`; add the platform first |
| Mac app killed at launch after signing | Game Center or iCloud entitlement without an embedded provisioning profile | Embed the profile; launch the signed build before upload |
| Signed bundle contains `._` files or root-only files | Built or staged on an exFAT external drive | Stage on internal APFS; check for zero `._` files |
| iOS build crashes at launch only on the newest iOS | New SDK requires a life-cycle change the project lacks | Compare Xcode/SDK with last shipped; launch the signed build on the newest OS |

## Anti-Patterns

**Editor-Only Verification** — testing in the editor and shipping the export. Imports, remaps, filters and plugins differ; gate on exported builds.

**FileAccess on res://** — opening imported assets as files. It works on every developer machine and fails for every player.

**The Untracked Plugin** — native binaries built on one machine, absent from git and from any manifest. The first clean CI build ships without them and nothing errors.

**Lambda Wiring** — connecting signals to inline lambdas. Unremovable connections and handlers that outlive their screens.

**Headless Performance Gates** — draw-call or GPU budgets checked in a headless run. Draw calls read zero and the gate passes forever.

**One Preset, Every Store** — a single export toggled by runtime flags. Steam code reaches the Mac App Store build and store code reaches the no-purchase edition.

**PASS Over Failures** — a gate summary that says PASS while steps failed. The verdict is the AND of every step, computed from parsed results.

**Floating Engine** — CI downloading "latest 4.x". Pin the build string and probe the API at every bump.

## Quality Checklist

- [ ] Engine build string, export templates, add-ons and native binary hashes pinned in a committed toolchain file
- [ ] API probe passes on the pinned build; rerun at the last engine bump
- [ ] Simulation state lives outside the scene tree and runs in headless tests
- [ ] Untyped-declaration warnings are errors in game code
- [ ] Every signal connects to a method; no lambda connections
- [ ] No `FileAccess` or `Image.load()` on imported assets; data files listed in export filters
- [ ] Export selftest loads every required asset inside each preset's exported pack
- [ ] One preset per store and edition, each with feature tags and a must/must-not code list
- [ ] Native artifact manifest checked before export; archive check run after every archive
- [ ] No-purchase and Arcade editions contain zero store code
- [ ] Master-bus peak probe above -60 dB in every exported pack and once per platform on hardware
- [ ] `ui_accept` and `ui_cancel` carry gamepad buttons; glyphs follow the last device
- [ ] Glyphs primed at the final viewport oversampling for every font size and language
- [ ] Translation overrides added before the OptimizedTranslation base
- [ ] Focusable Controls have accessibility names; OS preferences polled; in-game setting wins
- [ ] Render budgets measured windowed on devices; wall-clock tests one per process with host load recorded
- [ ] Saves compared and pushed as canonical bytes; one write in flight
- [ ] Mac App Store: sandbox, embedded profile, top-level minimum OS, world-readable, APFS staging
- [ ] Signed build launched on the newest OS whenever Xcode or the SDK changed
- [ ] Full GUT suite plus every gate passed on the exact commit before submission

## Related Skills

Loop, determinism, save envelopes and engine choice come from `gamedev-engine-architect`. Steam, Deck, notarization and desktop input: `gamedev-desktop-engineer`. Apple platform services, App Review and Arcade requirements: `gamedev-ios-engineer`; Android platform work: `gamedev-android-engineer`. Import settings, shaders and texture budgets: `gamedev-technical-artist`. Frame and memory budgets: `gamedev-optimization-compatibility`. HUD and menu structure: `gamedev-hud-engineer` and `gamedev-ui-designer`. Screen-reader and preference audits: `gamedev-accessibility-specialist`; string pipeline and fonts per language: `gamedev-localization-specialist`; mixes and audio budgets: `gamedev-audio-designer`. Lanes, signing and submission: `gamedev-delivery-release`; test plans and device matrix: `gamedev-qa-verifier`. Purchase verification on the server: `gamedev-backend-engineer`. Generated art and audio entering the import pipeline: `gamedev-ai-asset-pipeline`; agents running these gates: `gamedev-agentic-production`. A game better suited to a React stack: `gamedev-react-native-engineer`.
