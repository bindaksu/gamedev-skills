---
name: gamedev-ios-engineer
description: >-
  Build and ship native Swift games on iOS, iPadOS and macOS: SpriteKit versus RealityKit choices,
  a fixed-timestep loop on CADisplayLink or MTKView, ProMotion, Game Center and the Apple Games app,
  StoreKit 2 with server-side verification, controllers, thermal and audio handling, Background
  Assets, and App Review rules. Use when someone asks to build or audit a Swift or SpriteKit game,
  migrate off SceneKit or the original StoreKit API, fix 120 Hz stutter or frame pacing, wire Game
  Center or in-app purchases, add controller support, or prepare a game build for App Review.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: client-eng
---

# iOS Game Engineer

On Apple platforms the game is a guest of the OS. The OS picks your refresh rate, throttles your clocks, owns your audio session, interrupts you for a phone call, and decides whether your purchase happened. A native iOS game engineer's job is less about drawing sprites than about negotiating with those systems correctly: a loop that survives variable refresh and thermal throttling, a store that treats the device as untrusted, and a build that passes review on the first submission. Pick frameworks by their roadmap, not their tutorial count. SceneKit is in maintenance, SpriteKit is stagnant, and anything you build on them inherits that risk.

## Role Profile

**Be honest about the market.** Job-post research across top-grossing studios (Supercell, King, Playrix, Dream Games, Scopely, Tencent and others) found no posting for a Swift/SpriteKit gameplay engineer. These studios ship on Unity or in-house C++ engines (King and Playrix run proprietary C++ engines; Playrix lists C++17 with OpenGL ES/Metal). Native iOS work shows up in three places:

- **Rendering:** C++ plus Metal. Scopely asks for "rendering features ... for Vulkan (Android) and Metal (iOS)"; Sony and EA mobile want 5+ years of C++ plus Metal/Vulkan. Hand that work to `gamedev-metal-graphics-engineer`.
- **Platform SDK and bridge layers:** Swift/Obj-C wrappers for GameKit, StoreKit, push, ATT and account SDKs that a Unity or C++ game calls (Supercell ID client SDK; Rovio asks for "Apple GameKit and other Apple APIs").
- **Apple's own Games team and indie/premium studios** that ship pure Swift: "excellent Swift skills", concurrency, memory management, 5+ years.

| Dimension | What it looks like |
| --- | --- |
| Responsibilities | Platform integration layer (StoreKit, GameKit, controllers, audio session, Background Assets); app lifecycle and interruption handling; frame pacing and thermal policy; App Review compliance; for Swift-native titles, the whole client |
| Hard skills | Swift concurrency (actors, `Task`, `AsyncSequence`), Obj-C/C++ interop, memory and ARC cycles, Instruments, Metal basics, App Store Connect |
| Tools | Xcode, Instruments (Game Performance, Metal System Trace, Time Profiler, Allocations), Metal debugger and Performance HUD, StoreKit Testing in Xcode, TestFlight |
| KPIs (inferred) | GPU/CPU frame time and thermal behavior per device tier; crash-free sessions; purchase success and unverified-transaction rate; review rejections per release |
| Collaborators | Engine/rendering, backend (receipt and entitlement service), monetization, QA device lab, release engineering |

Sources: https://www.workingnomads.com/jobs/senior-engineer-graphics-unannounced-project-scopely , https://jobs.anitab.org/companies/apple/jobs/81543173-senior-ios-engineer-apple-games , https://jobs.anitab.org/companies/sony-interactive-entertainment-2/jobs/73763716-senior-graphics-programmer-mobile-ios-android

## When to Use / Not

Use for Swift game clients, Apple platform SDK integration (including bridges called from Unity or C++), frame-rate and thermal policy on Apple devices, and App Store submission readiness.

Not for: Metal renderer internals, MSL, MetalFX (`gamedev-metal-graphics-engineer`); Unity-side C# and IL2CPP plugin build (`gamedev-unity-engineer`); entitlement ledger and server receipt service (`gamedev-backend-engineer`); offer and pricing design (`gamedev-monetization-designer`); cross-device perf matrix (`gamedev-optimization-compatibility`); Mac Steam builds and notarization (`gamedev-desktop-engineer`); touch layout and thumb zones (if installed, `mobile-game-ux-designer`).

## Inputs to Gather

- **Engine and language:** pure Swift, SpriteKit, RealityKit, custom Metal, or a bridge from Unity/C++? Default: a bridge layer, because that is what most studios need.
- **Deployment target:** default iOS 17+ (covers StoreKit 2, `GCVirtualController`, modern `CADisplayLink` ranges). Metal 4 features need A14/M1 or later.
- **Target frame rate per device tier:** default 60 fps everywhere, 120 fps only for fast-action genres on ProMotion devices with thermal headroom.
- **Monetization model:** consumables, non-consumables, subscriptions, randomized items. Randomized items trigger guideline 3.1.1 odds disclosure.
- **Backend:** does an entitlement service exist? If not, the first deliverable is its contract, because StoreKit without server grants is a fraud surface.
- **Account model:** Game Center only, Sign in with Apple, or a studio account (cross-progression)? Default: studio account keyed to Game Center `teamPlayerID` plus an explicit link flow.
- **Content size:** install size and post-install content. Above ~200 MB of content, plan Background Assets from day one.

## Method

1. **Choose the framework by roadmap.** New 3D: RealityKit or a custom Metal renderer, never SceneKit (soft-deprecated, critical fixes only). New 2D with a multi-year life: a cross-platform engine or custom Metal; SpriteKit only for small or Apple-only titles, and budget time for its iOS 26 frame-rate regressions. Record the decision in a Platform Decision Record.
2. **Own the clock.** Drive the simulation at a fixed step (1/60 s or 1/120 s) from whatever callback renders (`SKScene.update`, `MTKViewDelegate.draw`, `CADisplayLink`). Render with interpolation. A variable-dt simulation breaks replays, physics stability, and any server-side validation.
3. **Request refresh rates, do not assume them.** Set `CADisableMinimumFrameDurationOnPhone` for iPhone ProMotion, use `preferredFrameRateRange`, and compute frame duration from `targetTimestamp - timestamp`. The OS may still drop to 60 Hz, so the loop must be rate-agnostic.
4. **Install the thermal ladder before content lock.** Observe `ProcessInfo.thermalState` and map each state to concrete knobs (frame cap, resolution scale, particle density, background work). Test with Xcode's thermal condition simulation. Retrofitting this after launch means reviews already say "phone gets hot".
5. **Configure the audio session at launch.** `.ambient` with `.mixWithOthers` for most casual games (respects the silent switch, mixes with user music); `.playback` only when audio is the game. Handle interruptions and route changes.
6. **Build the store as an event consumer.** Start a `Transaction.updates` listener at launch, process `Transaction.unfinished`, send the JWS to your server, and call `finish()` only after the server confirms the grant. Purchases arrive from Ask to Buy, family sharing, refunds, and other devices, not just your buy button.
7. **Authenticate Game Center early and non-blockingly.** Set the `authenticateHandler` at launch, present its view controller at a natural pause, and let the game run as guest if it fails. Wire Achievements and Leaderboards first; Challenges reuse leaderboards, so a single-player game gets a social loop almost free.
8. **Treat controllers as first-class.** Poll `GCController.current` in the sim tick, support connect/disconnect mid-session, show a `GCVirtualController` only when no physical controller is present, and set the Game Mode plist keys.
9. **Move content off the binary.** Use Apple-hosted Background Assets (up to 200 GB, updatable without a binary) instead of deprecated On-Demand Resources. Essential packs gate first launch; prefetch and on-demand packs never block the core loop.
10. **Run the App Review pre-flight** (see `references/release-compliance.md`) before every submission, not only the first.

## Deliverables

### 1. Platform Decision Record

```
GAME:                 [title]          DATE: [yyyy-mm-dd]
RENDER PATH:          SpriteKit / RealityKit / custom Metal / engine (Unity, Godot) + Swift bridge
WHY NOT THE OTHERS:   [one line each; cite SceneKit soft-deprecation, SpriteKit stagnation]
MIN OS / DEVICES:     iOS [x]+, oldest device [model], Metal 4 required? Y/N (A14/M1+)
FRAME TARGETS:        tier A [120/60] fps, tier B [60], tier C [30-60]; per-frame budget ms
THERMAL POLICY:       nominal / fair / serious / critical -> knob settings (table)
AUDIO SESSION:        category, mode, options; interruption behavior
STORE:                product types; server entitlement service URL; appAccountToken source
IDENTITY:             Game Center teamPlayerID / Sign in with Apple / studio account; link flow
CONTENT DELIVERY:     binary size target; Background Assets packs (essential/prefetch/on-demand)
CONTROLLERS:          physical, virtual overlay, Game Mode keys set Y/N
RISKS:                [framework roadmap, OS regressions, review guidelines]
```

### 2. Fixed-timestep SpriteKit scene

```swift
import SpriteKit

final class GameScene: SKScene {
    private let step: TimeInterval = 1.0 / 60.0
    private var accumulator: TimeInterval = 0
    private var lastTime: TimeInterval?
    private var sim = Simulation()            // pure Swift state; no SKNode references
    private var previous = Simulation.State()

    override func update(_ currentTime: TimeInterval) {
        guard let last = lastTime else { lastTime = currentTime; return }
        let frame = min(currentTime - last, 0.25) // clamp after a stall: no spiral of death
        lastTime = currentTime
        accumulator += frame
        while accumulator >= step {
            previous = sim.state
            sim.advance(dt: step, input: InputSampler.sample()) // polls GCController.current
            accumulator -= step
        }
        render(Simulation.State.lerp(previous, sim.state, accumulator / step))
    }

    func resetClock() { lastTime = nil; accumulator = 0 } // call on didBecomeActive / unpause
}
```

Keep `SKPhysicsWorld` out of anything that must be deterministic or server-validated: it steps on the frame delta, not your fixed step.

### 3. Thermal Policy Table

```
State     │ Frame cap │ Render scale │ Particles │ Background work      │ Network
nominal   │ target    │ 1.0          │ 100%      │ allowed              │ normal
fair      │ target    │ 1.0          │ 75%       │ defer (downloads, GC)│ normal
serious   │ 60 (or 30)│ 0.8          │ 50%       │ stop                 │ essential only
critical  │ 30        │ 0.7          │ 25%       │ stop                 │ essential only
```

Apple's guidance behind it: at fair, defer work; at serious, cut animations and networking; at critical, stop heating. The specific numbers are a starting heuristic; tune them per device tier.

### 4. Store Integration Spec

```
Product ID │ Type (consumable/non-consumable/auto-renew) │ Server grant │ Randomized? │ Odds shown where
Launch:    Transaction.updates listener started in app init: Y/N
           Transaction.unfinished drained at launch: Y/N
Purchase:  appAccountToken = studio account UUID: Y/N
Grant:     client sends jwsRepresentation -> server verifies with App Store Server Library -> grant -> client finish()
Refunds:   App Store Server Notifications V2 endpoint handles REFUND / revocation: Y/N
Restore:   AppStore.sync() behind an explicit Restore button only: Y/N
```

Read `references/swift-snippets.md` when writing the StoreKit 2 store, Game Center auth, controller input, thermal observer, audio session, display link driver, or Background Assets code. Read `references/release-compliance.md` when preparing a submission: Info.plist keys, the guidelines that most often reject games, and the interruption test list.

## Technical Reference

### Framework status (as of 2026-10; verify)

| Framework | Status | Implication |
| --- | --- | --- |
| SceneKit | Soft-deprecated at WWDC25; maintenance mode, critical fixes only, no hard-deprecation date | No new projects or major updates on it; migrate with Apple's "Bringing your SceneKit projects to RealityKit" guide |
| RealityKit | Apple's recommended high-level 3D engine; iOS, iPadOS, macOS, tvOS, visionOS; WWDC25 added instancing (`MeshInstancesComponent`) | Thin for genre needs (animation graph, physics tooling, editor) compared with Unity/Unreal |
| SpriteKit | "Not deprecated at this time" (Apple DTS), no successor, no roadmap; developers report frame-rate regressions across iOS 26.0 to 26.4 | Acceptable for small Apple-only 2D; test every OS point release on device |
| Original StoreKit | Deprecated at WWDC24, renamed "original API for in-app purchase"; new features ship only in StoreKit 2 (iOS 15+) | Migrate; receipt validation is legacy |
| On-Demand Resources | Deprecated, replaced by Apple-hosted Background Assets | Do not start new ODR work |

Sources: https://developer.apple.com/videos/play/wwdc2025/288 , https://developer.apple.com/forums/thread/826562 , https://developer.apple.com/forums/thread/816719

### Frame rate and loop

| Item | Value |
| --- | --- |
| Budget at 60 / 120 Hz | 16.67 ms / 8.33 ms per frame |
| Sustained-load heuristic | Keep steady-state CPU and GPU under ~70% of the frame budget to leave thermal headroom |
| iPhone ProMotion | Info.plist `CADisableMinimumFrameDurationOnPhone = YES`; iPad Pro does not need it |
| Rate request | `CADisplayLink.preferredFrameRateRange = CAFrameRateRange(minimum:maximum:preferred:)`, not `preferredFramesPerSecond` |
| Known quirks | OS can drop to 60 Hz briefly (first touch frame reported); some developers report a 90 Hz cap |
| macOS | `NSView.displayLink(target:selector:)` (macOS 14+) |

### Thermal, Game Mode, MetricKit

- `ProcessInfo.thermalState`: nominal, fair, serious, critical; observe `thermalStateDidChangeNotification`.
- Game Mode is automatic on iOS/iPadOS 18+ and macOS 14+: CPU/GPU priority, doubled Bluetooth controller polling, lower AirPods latency. Plist: `GCSupportsGameMode` (iOS 18+), `LSSupportsGameMode` (26+), `LSApplicationCategoryType` set to a games category. Keys make a game eligible; the OS decides at runtime. Non-games setting them risk rejection.
- MetricKit field reports carry Metal frame rate by game state (macOS and iOS 27), plus memory-limit terminations (as of 2026-10; verify that iOS 27 has shipped and the payload is live).

### Game Center and the Apple Games app

- The Apple Games app is preinstalled on iOS/iPadOS/macOS 26 and surfaces Game Center features and In-App Events. More Game Center integration means more OS surfaces showing your game.
- Four pillars (WWDC25 session 214): **Achievements, Leaderboards, Challenges** (async friend competitions built on existing leaderboards), **Activities** (deep links into specific content).
- Use `teamPlayerID` for backend identity across a developer team's games. Test the access-point overlay on current OS releases (an iPadOS 26 beta bug hid configured items).
- Source: https://developer.apple.com/videos/play/wwdc2025/214

### StoreKit 2 and content delivery

- Core types: `Product`, `Transaction`, `AppTransaction` (`appTransactionId` is per Apple Account per app), `RenewalInfo`, `VerificationResult`.
- Server: App Store Server API plus the App Store Server Library to verify JWS. Source: https://developer.apple.com/documentation/appstoreserverapi/app-store-server-api-changelog
- Background Assets: up to **200 GB** of Apple-hosted compressed packs per app, policies essential / prefetch / on-demand, updatable without a new binary, all platforms except watchOS. WWDC26 adds localized asset packs (iOS 27) and StoreKit plus Background Assets Unity plug-ins (as of 2026-10; verify). Source: https://developer.apple.com/documentation/backgroundassets/creating-managed-asset-packs

### Game Controller

- `GCVirtualController` (iOS 15+) renders touch controls that appear as a `GCController`.
- `GCDualSenseGamepad` (iOS 14.5+) exposes adaptive triggers; DualSense touchpad and triggers are not exposed through `GCControllerLiveInput`, so use `GCPhysicalInputProfile`.
- Research found no iOS 26/27 Game Controller API changes; check the framework release notes before claiming any.

### App Review rules that bite games

- **3.1.1:** loot boxes and other randomized virtual items must disclose the odds of each item type before purchase. Whether this covers boxes bought with earned currency is ambiguous; disclose anyway.
- **4.7** (revised Nov 13, 2025): HTML5/JS mini games, streaming games and plug-ins; you are responsible for that content (4.7.2 no exposing native APIs without permission; 4.7.5 age restriction above your rating).
- **2.5.2 / 4.7:** downloaded code may not change the app's primary purpose; this bounds Lua/JS hot updates.
- Authoritative text: https://developer.apple.com/app-store/review/guidelines/

## Diagnostics

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Game runs at 60 on a ProMotion iPhone | Missing `CADisableMinimumFrameDurationOnPhone`, or `preferredFramesPerSecond` used | Add the plist key; set `preferredFrameRateRange`; confirm with Metal Performance HUD |
| Physics speeds up at 120 Hz | Simulation integrates on frame delta | Fixed-step accumulator; interpolate rendering |
| Huge jump after returning from background | Accumulator fed the whole pause duration | Clamp frame delta to 0.25 s and reset the clock on `didBecomeActive` |
| SpriteKit stutter appeared after an OS update | Reported SpriteKit regressions across iOS 26.0 to 26.4 | Reproduce on device per OS point release; file feedback; cap at 60 if it stabilizes; plan the engine exit |
| Frame rate decays after 10 to 15 minutes | Thermal throttling with no policy | Thermal ladder; cap at 60; lower render scale at serious |
| Purchases granted twice or never | `finish()` before server grant, or no `Transaction.updates` listener | Listener at launch; finish only after server confirms; idempotent grant by transaction ID |
| Refunded players keep items | No server notification handling | App Store Server Notifications V2; revoke on refund |
| User music stops when the game launches | Audio session `.playback` or `.soloAmbient` | `.ambient` plus `.mixWithOthers`; respect `secondaryAudioShouldBeSilencedHint` |
| Controller works in menus, dead in gameplay | Input read through UIKit events, not polled in the tick | Poll `GCController.current` in the sim step; handle reconnect |
| Review rejection citing 3.1.1 | Odds hidden or shown after purchase | Odds per item type on the purchase screen, before the buy button |
| Game Center sheet interrupts the tutorial | Auth view controller presented immediately | Queue it until a natural pause; play as guest meanwhile |

## Anti-Patterns

**Tutorial-Driven Framework Choice** — starting a new 3D game on SceneKit because the sample was there. You inherit a maintenance-mode framework on day one.

**The Variable-dt Simulation** — gameplay integrates the display link delta. It works at 60 Hz and breaks at 120 Hz, in replays, and under server validation.

**Finish-Then-Grant** — calling `transaction.finish()` before the server records the grant. A crash between the two loses a paid item with no recovery path.

**Client-Trusted Entitlements** — the device decides what the player owns. Jailbroken devices and replayed JWS turn the store into a faucet.

**The Thermal Afterthought** — no thermal policy until reviews mention heat. By then content is locked at a cost the device cannot sustain.

**Blocking Boot on Game Center** — the game waits for authentication. Offline players and players who decline see a frozen title screen.

**Hostile Audio Session** — `.playback` in a casual puzzle game. It kills the player's podcast and ignores the silent switch.

**ODR In 2026** — new On-Demand Resources work after its replacement shipped with 200 GB of Apple hosting.

## Quality Checklist

- [ ] Platform Decision Record exists; no new SceneKit dependency; SpriteKit risk acknowledged if used
- [ ] Simulation runs at a fixed step; rendering interpolates; frame delta clamped; clock reset on resume
- [ ] `CADisableMinimumFrameDurationOnPhone` set if targeting 120 Hz; `preferredFrameRateRange` used
- [ ] Thermal policy table implemented and tested with simulated thermal states on device
- [ ] Audio session category matches the game; interruptions and route changes handled
- [ ] `Transaction.updates` listener and `Transaction.unfinished` drain start at launch
- [ ] `finish()` called only after server grant; grant is idempotent per transaction ID
- [ ] Server verifies JWS with the App Store Server Library; refunds handled via Server Notifications V2
- [ ] Randomized items show per-type odds before purchase (3.1.1)
- [ ] Game Center auth is non-blocking; Achievements and Leaderboards wired; Challenges considered
- [ ] Controllers: connect/disconnect mid-session, virtual overlay only without hardware, Game Mode keys set
- [ ] Post-install content uses Background Assets, not On-Demand Resources
- [ ] Every date-sensitive claim in design docs is tagged with its as-of date

## Related Skills

Hand renderer work, MSL, MetalFX and GPU captures to `gamedev-metal-graphics-engineer`. The server half of every purchase, the entitlement ledger and refund handling, belongs to `gamedev-backend-engineer`; App Attest and receipt-fraud scoring to `gamedev-anti-cheat-security`. Offer design and odds presentation come from `gamedev-monetization-designer`. If the game is Unity, the bridge layer lives here and the C# side in `gamedev-unity-engineer`. Device tiers, memory budgets and cross-device profiling go to `gamedev-optimization-compatibility`; signing, TestFlight and phased release to `gamedev-delivery-release`; Mac Steam builds to `gamedev-desktop-engineer`. Loop and fixed-timestep architecture beyond Apple specifics: `gamedev-engine-architect`. Feel and haptic timing: `gamedev-game-feel-designer`. Touch layout and safe areas: if installed, `mobile-game-ux-designer`.
