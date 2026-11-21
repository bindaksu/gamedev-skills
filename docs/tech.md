# Mobile/Desktop Game Engineering: Technical Reference (as of 2026-10-08)

Research date: 2026-10-08. Sources were collected by web search plus direct fetches of official pages.

Confidence tags:
- `[official]` means the vendor's own docs, blog or session page. Where a "last updated" date was visible, it is given.
- `[secondary]` means press or a third-party blog.
- `[vendor]` means a competitor or partner with a commercial stake.
- `[forum]` means a developer forum, including Apple DTS replies.
- `[job-posting]` means the stack is inferred from a recruiting listing.
- `[official-author]` means the author's own canonical article (Fiedler, Gambetta).
- `[bg]` means model background knowledge that was not re-verified this session. Verify before relying on it.

---

## 1. Apple platforms

### Release context
- iOS/iPadOS/macOS **26** shipped in fall 2025 (WWDC25). **iOS 27** was announced at WWDC26 in June 2026; WWDC26 sessions reference "iOS 27". `[official]` https://developer.apple.com/videos/play/wwdc2026/388/
  - Shipping status of iOS 27 as of Oct 2026 is assumed (fall cadence) but was **not confirmed** this session.

### SceneKit: soft-deprecated (WWDC25)
- WWDC25 session 288, "Bring your SceneKit project to RealityKit", says SceneKit is **soft-deprecated** and in maintenance mode. `[official]` https://developer.apple.com/videos/play/wwdc2025/288
  - Existing apps keep working.
  - Apple advises against SceneKit for new apps or major updates.
  - Only critical bug fixes are planned, with no new features.
  - Apple has "no plan to hard deprecate" and promises "ample notice" if that changes.
- Migration guide: "Bringing your SceneKit projects to RealityKit". `[official]` https://developer.apple.com/documentation/realitykit/bringing-your-scenekit-projects-to-realitykit
- One third-party claim says SwiftUI `SceneView` is formally deprecated in iOS 26. **Unverified.** `[secondary]` https://dev.to/arshtechpro/wwdc-2025-scenekit-deprecation-and-realitykit-migration-a-comprehensive-guide-for-ios-developers-o26

### SpriteKit: not deprecated, but stagnant
- An Apple DTS forum reply says SpriteKit is "not deprecated at this time". It found no framework-level deprecation marker in the iOS 26 SDK. Apple makes no roadmap commitment. `[forum]` https://developer.apple.com/forums/thread/826562
- Developers report SpriteKit frame-rate regressions across iOS 26.0 to 26.4. `[forum]` https://developer.apple.com/forums/thread/816719
- Commentary notes there is no successor to SpriteKit, unlike SceneKit. `[secondary]` https://fatbobman.com/en/weekly/issue-090/
- Practical take: for new 2D titles that need longevity, prefer a cross-platform engine or a custom Metal renderer.

### RealityKit for games
- WWDC25 session 287, "What's new in RealityKit", covers iOS, iPadOS, macOS, tvOS and visionOS. `[official]` https://developer.apple.com/videos/play/wwdc2025/287
  - RealityKit is now supported on tvOS (all Apple TV 4K generations).
  - New features: ManipulationComponent, EnvironmentBlendingComponent, and MeshInstancesComponent (instancing).
- It is Apple's recommended high-level 3D engine. It is still thin for genre game needs such as an animation graph, mature physics tooling, or an editor on par with Unity/Unreal. `[bg]`
- visionOS 26 adds PS VR2 Sense controller and Logitech Muse "spatial accessory" support. `[secondary]` https://www.uploadvr.com/visionos-26-out-now-apple-vision-pro/

### Metal 4 (WWDC25) and Metal 4.1 / WWDC26
- Metal 4 hardware floor: **A14 Bionic or later** (iPhone 12+) and **Apple silicon M1 or later**. Apple Vision Pro is also supported. `[official]` https://developer.apple.com/metal/
- Core API changes (Metal 4 core API):
  - `MTL4CommandAllocator` is an explicit memory backing for command encoding. It serves one command buffer at a time, so use one allocator per encoding thread. It can be reused after `endCommandBuffer`.
  - `MTL4CommandBuffer` uses `beginCommandBuffer(allocator:)`.
  - `MTL4ArgumentTable` replaces per-encoder resource binding.
  - Source: `[official]` https://developer.apple.com/documentation/metal/understanding-the-metal-4-core-api
- Machine learning: tensors and inference can be encoded at the command level or inside shaders. See "Combine Metal 4 machine learning and graphics" (WWDC25 session 262). `[official]` https://developer.apple.com/metal/
- MetalFX (WWDC25) adds **Frame Interpolation** and **Denoising** (ray reconstruction), on top of the temporal/spatial **Upscaling** from Metal 3. Session: "Go further with Metal 4 games" (WWDC25 session 211). `[official]` https://developer.apple.com/videos/play/wwdc2025/211
  - **Conflict:** sources disagree on the interpolation ratio. PCGH says one generated frame per rendered pair. Tom's Guide implies more. Treat session 211 as the authority. `[secondary]` https://www.pcgameshardware.de/Grafikkarten-Grafikkarte-97980/News/Metal-4-mit-MetalFX-Frame-Interpolation-und-Denoising-1474693/
- WWDC26 (Metal guide): `[official]` https://developer.apple.com/wwdc26/guides/metal/
  - MetalFX has a **redesigned temporal upscaler** that uses the Neural Engine plus the Neural Accelerators on **M5 Pro and M5 Max**.
  - Upscaler API additions: subrect processing for dynamic resolution, caller-supplied motion vectors, and distortion fields for post effects.
  - Metal 4 gains quantized tensor formats.
  - Tech talks: "Boost your graphics performance with the M5 and A19 GPUs".
- WWDC26 games guide: `[official]` https://developer.apple.com/wwdc26/guides/games/
  - The Xcode Metal debugger is faster.
  - New **Metal command-line debugging tools** target scripting and agentic workflows.
  - **MetricKit reports now include Metal frame rate.**

### Profiling, performance and thermals
- Instruments templates: `[official]` https://developer.apple.com/documentation/xcode/analyzing-the-performance-of-your-metal-app
  - **Game Performance** template: Metal System Trace plus thread state, system calls, virtual memory and Points of Interest. Use it for stutter hunting.
  - **Metal System Trace**: CPU/GPU parallelism and Metal memory.
- WWDC26 session 388, "Find and fix performance issues in your Metal games": `[official]` https://developer.apple.com/videos/play/wwdc2026/388/
  - **Game Performance Overview** template for long captures.
  - **Look-back collection**:
    - macOS: `metalperftrace collect /tmp --last 5h`, and `metalperftrace overview --json`.
    - iOS: Developer settings, then Performance Trace, then Lookback, plus a Control Center button.
  - **StateReporting** API (`SRStateReporter reporterForDomain:`) tags traces with game-state domains such as level or menu, along with stable and volatile metadata.
  - MetricKit field reports (macOS and **iOS 27**) carry Metal frame rate broken down by state, plus memory-limit terminations.
- **Metal Performance HUD** is an in-game overlay showing FPS, frame interval and memory, with configurable StateReporting display. `[official]` https://developer.apple.com/metal/
- Thermal state:
  - `ProcessInfo.thermalState` has four levels: nominal, fair, serious and critical. Observe `ProcessInfo.thermalStateDidChangeNotification`.
  - Apple guidance: at fair, defer work; at serious, cut animations and networking; at critical, stop heating.
  - Source: `[official]` https://developer.apple.com/documentation/foundation/processinfo/thermalstate-swift.enum
  - Xcode can simulate thermal states on device (Devices window, Condition). `[bg]`
- ProMotion (120 Hz) on iPhone:
  - Requires the Info.plist key `CADisableMinimumFrameDurationOnPhone = YES`. iPad Pro does not need it.
  - Use `CADisplayLink.preferredFrameRateRange` (`CAFrameRateRange` min/max/preferred), not `preferredFramesPerSecond`.
  - The OS can still drop to 60 Hz briefly, for example on the first touch frame per a Unity issue tracker report. Some developers report a 90 Hz cap.
  - Sources: `[forum]` https://developer.apple.com/forums/thread/761616 and `[secondary]` https://discussions.unity.com/t/iphone-13-pro-high-refresh-rate-patch/857270

### Game Mode
- Game Mode is automatic on **iOS/iPadOS 18+** and macOS 14+. `[secondary]` https://9to5mac.com/use-game-mode-iphone-ios-18/
  - It prioritizes the game on CPU and GPU.
  - It **doubles Bluetooth polling rate** for controllers.
  - It lowers AirPods audio latency.
- Info.plist keys: `[forum]` https://developer.apple.com/forums/thread/782343
  - `GCSupportsGameMode` (iOS 18+, macOS 14+). Newer `LSSupportsGameMode` (iOS/iPadOS/macOS **26+**). Both can be set.
  - Also set `LSApplicationCategoryType` to a games category.
  - The OS decides at runtime, so the keys make a game eligible but do not guarantee Game Mode.
  - Non-games that set the keys risk App Review rejection.

### Game Porting Toolkit (lineage)
- GPTK 1 (WWDC23) → GPTK 2 (WWDC24) `[bg]` → **GPTK 3 (WWDC25)** → **GPTK 4 (WWDC26)**.
- GPTK 3 added sparse buffers, sparse textures and performance insights for Windows games. The evaluation environment runs unmodified Windows .exe files on Apple silicon (D3DMetal). `[official]` https://developer.apple.com/games/game-porting-toolkit
- GPTK 4: `[official]` https://developer.apple.com/wwdc26/guides/games/ and https://developer.apple.com/videos/play/wwdc2026/357/
  - The evaluation environment supports **Metal 4**.
  - Open-source **agent skills plus sample code**: https://github.com/apple/game-porting-toolkit
  - Command-line Metal capture/debug/profile.
  - Session: "Speedrun your game port with agentic coding" (WWDC26 session 357).
  - DX12 games translate to Metal 4. **DX11 falls back to Metal 3.** One test reported about 10% more frames for Cyberpunk on an M3 Max via DX12→Metal 4. `[secondary]` https://appleinsider.com/articles/26/06/17/apples-game-porting-toolkit-4-is-a-big-improvement-for-modern-game-coders
- Apple Silicon Mac gaming market data (Steam share, AAA port list) was **not researched in depth**. Treat any market-size claim as needing a fresh check.

### Game Center / GameKit / Apple Games app
- The **Apple Games app** is preinstalled on iOS/iPadOS/macOS 26. `[official]` https://developer.apple.com/games-app/
  - It merges App Store games, Game Center social features and Arcade.
  - It surfaces Game Center features and In-App Events.
- WWDC25 session 214, "Get started with Game Center", covers four feature pillars: **Achievements, Leaderboards, Challenges, Activities**. `[official]` https://developer.apple.com/videos/play/wwdc2025/214
  - **Challenges** are async friend competitions built from existing **leaderboards**, so single-player games gain a social loop.
  - **Activities** deep-link players into specific game content.
  - More Game Center integration gives the OS more surfaces to show the game.
- An iPadOS 26 beta forum report says the access-point overlay did not show configured items. Test the overlay on current OS releases. `[forum]`

### StoreKit / IAP / asset delivery
- The original StoreKit API was deprecated at WWDC24 (iOS 18) and renamed "original API for in-app purchase". New features ship only in **StoreKit 2** (Swift async, iOS 15+). `[secondary]` https://www.revenuecat.com/blog/engineering/migrating-from-storekit-1-to-storekit-2
- StoreKit 2 core types: `Transaction`, `AppTransaction` (app purchase metadata; `appTransactionId` is per Apple Account per app) and `RenewalInfo`. WWDC25 session 241/249. `[official]` https://developer.apple.com/videos/play/wwdc2025/249
- Server side: use the **App Store Server API** with the App Store Server Library to verify JWS. Receipt validation is legacy. `[official]` https://developer.apple.com/documentation/appstoreserverapi/app-store-server-api-changelog
- **Apple-hosted Background Assets (WWDC25):** `[official]` https://developer.apple.com/documentation/backgroundassets/creating-managed-asset-packs
  - Up to **200 GB** of compressed asset packs per app, hosted by Apple and included in the program membership.
  - Download policies: essential, prefetch and on-demand. Packs can be updated without a new binary.
  - Replaces deprecated On-Demand Resources. Available on all platforms except watchOS.
- WWDC26 additions: `[official]` https://developer.apple.com/wwdc26/guides/games/ and session 378 "Unlock in-game content with StoreKit and Background Assets"
  - **StoreKit plug-ins for Unity**, plus a Background Assets Unity plug-in.
  - **Localized/language asset packs** (iOS 27). The system picks the nearest language.
  - A **Steam Asset Converter** for App Store media.

### App Store Review Guidelines (games-relevant)
- **3.1.1**: apps selling "loot boxes" or other randomized virtual items **must disclose odds of each item type before purchase**. Added Dec 2017. `[secondary]` https://www.fenwick.com/insights/publications/apple-now-requires-disclosure-of-loot-box-odds
  - Whether it applies to boxes bought with earned currency is ambiguous. Disclose anyway.
- **4.7** (revised Nov 13, 2025) covers HTML5/JS mini apps and mini games, streaming games, chatbots and plug-ins. The developer is responsible for that content. `[secondary]` https://dev.to/arshtechpro/apples-guideline-47-update-what-every-developer-hosting-html5-mini-apps-must-know-90
  - **4.7.2**: no exposing native APIs to non-embedded code without permission.
  - **4.7.5**: must offer age-restriction for content above the app's rating.
  - Retro console emulators may download games.
- A June 2026 update reportedly expanded child-safety requirements. Seen only via a tracker; verify on Apple's page. `[secondary]` https://conductatlas.com/change/2026-06-09-apple-apple-app-store-review-guidelines-2759/
- Authoritative text: https://developer.apple.com/app-store/review/guidelines/

### Game Controller framework
- `GCVirtualController` (iOS 15+) provides on-screen touch controls that appear as a `GCController`. `[official]` https://developer.apple.com/documentation/gamecontroller/adding-virtual-controls-to-games-that-support-game-controllers-in-ios
- `GCDualSenseGamepad` (iOS 14.5+) exposes adaptive triggers. `[official]` https://developer.apple.com/documentation/gamecontroller/gcdualsensegamepad
  - DualSense touchpad and triggers are not exposed via `GCControllerLiveInput` (iOS 17 era). Use `GCPhysicalInputProfile`. `[forum]`
- **iOS 26/27 Game Controller API changes were not found.** Check the framework's release notes.

---

## 2. Android

### Store policy deadlines (critical)
- **Target API**: from **Aug 31, 2026**, new apps and updates must target **Android 16 (API 36)**. `[official]` https://developer.android.com/google/play/requirements/target-sdk
  - Exceptions: Wear OS and Automotive target API 35. TV and XR target API 34.
  - An extension to **Nov 1, 2026** is available on request.
  - Existing apps below the floor become invisible to users on newer OS versions.
- **16 KB page size**: the official page (last updated 2026-09-16) says apps targeting Android 15+ must support 16 KB pages on 64-bit devices. `[official]` https://developer.android.com/guide/practices/page-sizes
  - Enforcement: **"Starting February 1, 2027, if your app updates don't support 16 KB … you won't be able to release these updates."**
  - Earlier secondary sources cited Nov 1, 2025 with an auto-extension to May 31, 2026. **Treat that as superseded by the official Feb 1, 2027 date.**
  - Tooling: **AGP 8.5.1+** and **NDK r28+** align by default. For NDK r27 and older, add `-Wl,-z,max-page-size=16384`.
  - Verify with `zipalign -v -c -P 16 4 app.apk`, `check_elf_alignment.sh`, `llvm-objdump -p lib.so | grep LOAD` (expect `2**14`), and `adb shell getconf PAGE_SIZE`.
  - Every prebuilt .so must be rebuilt, including ad SDKs, physics and audio middleware.
- **Large screens (Android 16 / API 36)**: orientation, resizability and aspect-ratio limits are ignored on sw600dp+ screens. **Games are exempt** if the manifest declares `android:appCategory="game"`. `[official]` https://developer.android.com/develop/adaptive-apps/guides/app-orientation-aspect-ratio-resizability
  - In Unity, set the App Category player setting; `androidIsGame` is gone. `[official]` https://docs.unity3d.com/Manual/android-large-screen-and-foldable-support.html
  - **Android 17 (API 37) removes the opt-out** for non-game apps. `[official]` https://android-developers.googleblog.com/2026/02/prepare-your-app-for-resizability-and.html

### Play Billing Library (PBL)
- **PBL 8+ is required for new apps and updates since Aug 31, 2026**, with an extension to Nov 1, 2026. `[official]` (deprecation FAQ, updated 2026-09-09) https://developer.android.com/google/play/billing/deprecation-faq
  - The table and banner agree. The table row "v7 → Aug 31, 2026" marks v7's last accepted day.
  - Each major version gets about 2 years. v8 is accepted until Aug 31, 2027 and v9 until Aug 31, 2028.
- PBL 8 changes: `[official]` https://developer.android.com/google/play/billing/migrate-gpblv8
  - "In-app items" are renamed **one-time products**, with multiple purchase options and offers.
  - `enableAutoServiceReconnection()`.
  - Sub-response codes such as `PAYMENT_DECLINED_DUE_TO_INSUFFICIENT_FUNDS`.
  - Unfetched-product status codes.
  - Removed: `querySkuDetailsAsync`, the no-argument `enablePendingPurchases()`, and querying expired subscriptions or consumed purchases.
- **PBL 9.0.0 (2026-05-19)**: system-blocked activity (for example OEM kids mode) now returns `BILLING_UNAVAILABLE`, with richer sub-codes. **9.1.0 (2026-06-18)** adds Billing Choice APIs (`getBillingChoiceInfoAsync`, `showBillingProgramInformationDialog`). `[official]` https://developer.android.com/google/play/billing/release-notes
- Gotcha: Play Console detects the PBL version from the merged-manifest entry `com.google.android.play.billingclient.version`. Multi-module merges can drop it. `[secondary]` https://foresightmobile.com/blog/google-play-billing-library-8-migration

### Play Games Services (PGS)
- Official schedule (page updated 2026-10-06): `[official]` https://developer.android.com/games/pgs/deprecation
  - v1 SDK deprecated after Sept 2025.
  - **v1 APIs removed from the SDK on June 15, 2026** (`play-services-games:25.0.0`; do not upgrade to it while still on v1).
  - **Google Sign-In for Android API unsupported from Sept 2026.**
  - **v1 shutdown May/June 2027.**
- v2 automatically signs players in at launch with a platform-level identity. The game must run its own account system (Sign in with Google, Credential Manager or its own backend) for cross-device or cross-platform accounts. `[official]` https://developer.android.com/games/pgs/migration_overview

### Google Play Games on PC
- Left beta (GA) on **Sept 23, 2025**, with 200k+ titles in about 130 countries. Opened to **native PC games**. `[secondary]` https://www.androidauthority.com/google-play-games-pc-no-longer-beta-general-availability-3599973/
- **Play Games Sidekick** is an overlay with Gemini Live tips in select games. `[secondary]`
- Native PC titles that call Play Billing directly must migrate to the **PC SDK**. `[official]` https://developer.android.com/games/playgames/native-pc/migrate_api_sdk
- Play Integrity on PC returns `meets-virtual-integrity`. `[official]` https://developer.android.com/google/play/integrity/improvements

### AGDK (Android Game Development Kit)
- Status per the overview page (last updated 2026-02-26). `[official]` https://developer.android.com/games/agdk/overview
  - **GameActivity** (replaces NativeActivity; C/C++ lifecycle, input and text; API 19+).
  - **GameTextInput**.
  - **Game Controller library** (formerly Paddleboat).
  - **Frame Pacing** (Swappy): consistent present timing for GL and Vulkan.
  - **Memory Advice API**: **Beta**. It estimates native plus GL/Vulkan memory and warns at thresholds.
  - **Oboe** (low-latency audio).
  - **Android Performance Tuner (APT)**.
  - **AGI**.
  - **AGDE** (Visual Studio extension).
  - No deprecations are listed.
- **APT** (page updated 2026-02-26) collects frame time (CPU vs GPU split) and loading time plus abandonment by quality level, annotation and device. Results show in Play Console Android vitals. Works on Android 4.1+. `[official]` https://developer.android.com/games/sdk/performance-tuner

### ADPF (Android Dynamic Performance Framework)
- **Thermal API** (Android 11 / API 30+): `getThermalHeadroom(forecastSeconds)` returns 1.0 at severe throttling. Scale quality before the device throttles. `[official]` https://developer.android.com/games/optimize/adpf
- **Performance Hint API** (Android 12 / API 31+): create a session for the render and game threads. Call `updateTargetWorkDuration()` and `reportActualWorkDuration()` every frame so the scheduler right-sizes CPU clocks.
- Also part of ADPF: Game Mode and Game State APIs, and Fixed Performance Mode for benchmarking.
- Engine support:
  - Unity: Adaptive Performance Android provider (hint calls are automatic).
  - Unreal: ADPF plugin (API 31+).
  - Cocos Creator: Thermal API from 3.8.2, Hint API from 3.8.3.
  - Defold: ADPF extension.
- Best practice: map headroom to your own quality knobs (resolution scale, frame-rate cap, effects) rather than engine Low/Medium/High presets. `[official]` https://developer.android.com/games/optimize/adpf/best-practices-adpf
- MediaTek case study reports a 25% drop in FPS standard deviation (vendor demo). `[official]` https://developer.android.com/stories/games/mediatek-adpf

### Graphics API: Vulkan first, ANGLE for GLES
- Vulkan has been available since Android 7. All 64-bit devices on Android 10+ support **Vulkan 1.1**, and about 85% of active devices support Vulkan. OpenGL ES is "no longer under active feature development". Unity and Unreal default to Vulkan where compatible. `[official]` (page updated 2025-07-27) https://developer.android.com/games/develop/vulkan/overview
- **ANGLE** (GLES on top of Vulkan) ships as an optional layer on Android 15+. Test with adb. Long-term direction is GLES via ANGLE on the Vulkan driver. `[official]` (same page, localized versions)
- **Android Vulkan Profiles / Android Baseline profile** helps pick a feature floor. `[bg]`

### Play Asset Delivery (PAD)
- Delivery modes (page updated 2026-10-06): `[official]` https://developer.android.com/guide/playcore/asset-delivery
  - **install-time** packs are split APKs and count toward install size.
  - **fast-follow** downloads automatically after install.
  - **on-demand** downloads at runtime.
  - Fast-follow and on-demand packs may be deleted or moved by the OS or user. Query their location through the PAD library every time.
- **Texture Compression Format Targeting**: ship ASTC, ETC2 and others in one AAB, and Play serves the best format per device.
- Size limits: `[official]` https://support.google.com/googleplay/android-developer/answer/9859372#size_limits
  - Base module: 200 MB.
  - Asset pack: 1.5 GB each.
  - Install-time total: 4 GB.
  - On-demand plus fast-follow total: **4 GB, or 30 GB for Level Up program / XR titles**.
  - Maximum 100 packs.
  - Older docs cited 10 GB for the Partner Program. **Probably superseded.**

### Integrity, profiling and quality
- **Play Integrity API**: `[official]` https://developer.android.com/google/play/integrity/improvements
  - From **May 2025**, the device verdict on Android 13+ requires **hardware-backed** signals (key attestation plus verified boot).
  - Use **standard requests** (cached, a few hundred ms, replay protection built in) for per-action checks, rather than classic requests.
  - Optional `MEETS_STRONG_INTEGRITY` adds a security-patch recency check.
  - SafetyNet Attestation is gone. `[bg]`
  - A device integrity verdict is a risk signal; keep game logic server-authoritative.
- **AGI (Android GPU Inspector)**: `[official]` https://developer.android.com/agi/sys-trace/system-profiler
  - System profiler (built on **Perfetto**): CPU scheduling, GPU counters, Vulkan call traces, memory and power.
  - Frame profiler: per-draw analysis for Vulkan and GLES.
- **Perfetto** supports long traces and a web UI (ui.perfetto.dev). `[official]` https://developer.android.com/games/tools
- **Android vitals bad-behavior thresholds**: 1.09% user-perceived crash rate, 0.47% user-perceived ANR rate, and 8% per device model. These cause reduced Play visibility and store-listing warnings. `[official]` (from 2022, **possibly outdated**) https://android-developers.googleblog.com/2022/10/raising-bar-on-technical-quality-on-google-play.html

### Kotlin + Jetpack Compose in game shells (practice guidance, not an announcement)
- Pattern: run GameActivity or an engine activity for the native render loop on a SurfaceView. Use Kotlin plus Compose for out-of-loop UI such as store, settings, account and live-ops inbox.
  - Either use a separate Activity, or add a `ComposeView` sibling over the surface (`addContentView`) and handle touch pass-through explicitly.
  - Never draw game-rate content on a Compose Canvas, since it runs on the main thread.
  - GameActivity docs: `[official]` https://developer.android.com/games/agdk/game-activity
  - The overlay approach itself is an unverified pattern. `[secondary]` https://proandroiddev.com/demystifying-androids-surface-your-secret-weapon-for-high-performance-graphics-7219f9caf0f8
- Unity "as a Library" or Unreal embedding lets you host the engine inside a Kotlin/Compose app shell. Startup cost and memory need measuring. `[bg]`

---

## 3. Cross-platform engines

### Unity 6 line
- **6.0 LTS** (Oct 2024). Support ends around Oct 2026. `[secondary]`
- **6.3 LTS** (Dec 4, 2025): 2 years of support (3 for Enterprise/Industry), through about Dec 2027. Recommended for live games. `[official]` https://unity.com/blog/unity-6-3-lts-is-now-available
- **6.4** (Mar 2026, "Supported" update release): **ECS core packages ship with the Editor** (Entities, Collections, Mathematics, Entities Graphics). Their versions are locked to the Editor. `[official]` https://docs.unity3d.com/Manual/WhatsNewUnity64.html and https://discussions.unity.com/t/ecs-development-status-december-2025/1699284/1
- **6.5** (about June 2026): **Built-in Render Pipeline deprecated**. `[official]` https://unity.com/topics/render-pipelines-strategy-for-2026
  - BiRP remains available at least through 6.7 LTS, with no removal date set.
  - **HDRP is in maintenance.** Investment goes to **URP**.
  - Use URP for all new mobile work.
- **6.6** (Sept 2–3, 2026): last non-LTS release before 6.7. Fast Enter Play Mode is the default. Adds experimental **CoreCLR desktop player** and C++ player previews. `[secondary]` https://www.digitaltoday.co.kr/jp/view/99090/unity-releases-unity-6-6-to-improve-development-and-build-speeds
- **6.7 LTS** expected in **Q4 2026**; alpha since July 2026. **Unity 7** was announced at Unite Seoul (July 2026): beta Dec 2026, release **Q1 2027**, described as a "direct continuation" of Unity 6 with a CoreCLR runtime. `[secondary]` https://www.invenglobal.com/articles/24003/unity-engine-7-changing-the-development-paradigm-and-the-roadmap-ahead
  - Unity has reset its roadmap before; treat these dates as provisional.
- **Runtime Fee cancelled on Sept 12, 2024.** `[official]` https://unity.com/blog/unity-is-canceling-the-runtime-fee
  - Unity returned to seat-based pricing.
  - Pro is $2,200 per seat per year and is required above $200k annual revenue plus funding.
  - Enterprise is required above $25M.
  - The Personal tier cap is $200k, and the splash screen is optional in Unity 6.
  - Unity says future price changes will be annual, and users can stay on the terms of their current Editor version.
- **Netcode for GameObjects 1.x is unsupported from the 6000.3 editor onward.** Use NGO 2.x, which adds the Distributed Authority topology. `[official]` https://discussions.unity.com/t/netcode-for-gameobjects-1-x-deprecation-in-6000-3-editor/1674997
- **Addressables 2.x**: `[official]` https://docs.unity3d.com/Packages/com.unity.addressables@2.8/manual/remote-content-intro.html
  - The remote catalog must be enabled in the shipped player, or content updates can't be detected.
  - "Update a previous build" yields delta bundles.
  - `UpdateCatalogs` blocks other Addressables requests while it runs.
  - Hosting can be CCD or any CDN.
- Code hot-update (Asia/China practice): **HybridCLR** extends IL2CPP to AOT plus an interpreter. Apple and Google policies on downloaded executable code apply; downloaded code may not change the app's primary purpose (Apple 2.5.2/4.7). `[secondary]` https://github.com/DSHGFHDS/hybridclr/blob/main/README_en.md

### Unreal Engine
- **5.6** (June 3, 2025): smaller mobile package sizes, revised mobile scalability defaults, on-device iteration and mobile preview. `[secondary]` https://80.lv/articles/new-mobile-game-development-features-in-unreal-engine-5-6
- **5.7** (Nov 12–13, 2025): Nanite Foliage. PCG and Substrate are production-ready. In-editor AI assistant. `[secondary]` https://gamefromscratch.com/unreal-engine-5-7-released/
- **5.8** (June 17, 2026, State of Unreal):
  - **Lumen Lite**: cheaper GI, claimed about 2x faster than Lumen.
  - MegaLights and Iris networking are production-ready.
  - Experimental Mesh Terrain.
  - Unreal MCP server plugin.
  - Probably the last 5.x release, with UE6 previews around late 2027 (one source; another says 5.9 is possible).
  - Source: `[secondary]` https://www.guru3d.com/story/unreal-engine-58-debuts-lumen-lite-and-productionready-megalights/
- Mobile rendering choices: the Mobile Forward or Mobile Deferred renderer, Vulkan on Android, Metal on iOS. Use the "Desktop renderer on mobile" only for flagship devices. `[bg]`
- Use ADPF via the Android Dynamic Performance plugin. `[official]`
- Royalty: 5% above $1M lifetime gross per product. `[bg]`

### Godot
- **4.5** (Sept 15, 2025): AccessKit screen-reader support (partial), stencil buffer, and a **shader baker** that cuts startup shader compiles. 4.5.1 followed on Oct 15, 2025. `[official]` https://github.com/godotengine/godot/releases
- **4.6** (early 2026; **date conflict**, Jan 27 vs Feb 27): `[official]` https://godotengine.org/releases/4.6/
  - **Jolt is the default 3D physics** for new projects.
  - Unique node IDs.
  - **LibGodot**, which embeds the engine in other apps.
  - C++ tracing profiler and rewritten SSR.
  - New editor theme.
- MIT license. Mobile is good for 2D and mid-tier 3D, but its console story depends on third parties. `[bg]`

### Defold and Cocos
- **Defold** 1.10.x (2025) upgraded to Box2D v3 and added runtime SDF fonts; it is now on 1.12.x. Free, source-available license, 2D-focused, very small builds. King originated it. `[official]` https://defold.com/blog
- **Cocos Creator 3.8.x** LTS line (3.8.6 in Mar 2025; 3.8.8 reported) covers HarmonyOS, mini-games (WeChat/Douyin) and web. `[official]` https://docs.cocos.com/creator/manual/en
  - "Acquired by Suddenly Technology, Nov 2025" comes from a single aggregator. **Unconfirmed.** `[secondary]` https://www.cbinsights.com/company/cocos

### What top studios use
- **Unity** dominates mobile. Estimates run to about 70% of top-grossing mobile games, roughly 48% overall share, and 65.7% of mobile devs in a PocketGamer survey. Methodology varies; treat these as directional. `[secondary]` https://appradar.com/blog/mobile-game-engines-development-platforms
- **Royal Match** (Dream Games) uses Unity. `[secondary]` https://en.wikipedia.org/wiki/Royal_Match
- **Genshin Impact** (miHoYo) uses Unity. `[secondary]`
- **Supercell** uses its in-house **Titan** engine for all games: about 300M MAU, a roughly 70-person org covering engine, tools and live-ops infrastructure. mo.co got a new rendering backend. `[official]` https://supercell.com/en/news/game-engine-called-titan
- **King**: the Candy Crush client is a large proprietary C++ codebase. `[job-posting]`
- Honor of Kings (Unity, heavily modified) `[bg]` and Monopoly GO (Unity) `[bg]` were not verified this session.
- PC/console context: custom engines fell below 50% of units sold for the first time (42%), with Unreal gaining. `[secondary]` https://sensortower.com/blog/the-big-game-engines-report-of-2025

---

## 4. Backend, platform and netcode

### Backend-as-a-service / game backends
- **Nakama** (Heroic Labs): `[official]` https://heroiclabs.com/docs/nakama/server-framework/introduction/
  - Open-source Go server under Apache-2.0, a single binary with an embedded console.
  - Server runtime in Go plugins, Lua or **TypeScript/JS** (JS recommended).
  - Requires **CockroachDB or Postgres**.
  - Features: realtime sockets, authoritative matches, leaderboards, tournaments, groups, chat, storage and matchmaker.
  - Sister products: **Hiro** (metagame: economy, inventory, energy, event leaderboards), **Satori** (live-ops: events, feature flags, experiments, audiences) and **Heroic Cloud** (managed hosting; 2.0 in Jan 2026).
  - No acquisition was found. `[official]` https://heroiclabs.com/blog/10-year-anniversary/
- **PlayFab** (Microsoft): `[official]` https://developer.microsoft.com/en-us/games/articles/2026/04/playfab-digest-march-feature-updates/
  - Services: Economy v2, Multiplayer Servers (MPS), Party, Lobby/Matchmaking and CloudScript (Azure Functions).
  - **Foundation Mode** (2026) gives Xbox devs core PlayFab services cross-platform at no extra cost.
  - `GetPlayersInSegment` was retired Mar 31, 2026.
- **AccelByte (AGS)**: a managed, hosted full-stack backend (identity, social, matchmaking, commerce, AMS server hosting). `[vendor]` https://accelbyte.io/compare/accelbyte-vs-pragma
- **Pragma**: `[secondary]` https://www.cbinsights.com/company/pragma-3
  - Engine-agnostic backend that runs in the **customer's own cloud**.
  - Raised $12.75M in Mar 2025.
  - Acquired FirstLook (playtest/community) in 2025; FirstLook 1.0 shipped Feb 2026.
- **Unity Gaming Services (UGS)** includes Authentication, Cloud Save, Cloud Code, Economy, Remote Config, Lobby, Relay, Matchmaker, Distributed Authority, CCD, Analytics and Leaderboards.
  - **Multiplay Game Server Hosting: Unity ended direct support on Mar 31, 2026.** Unity licensed the software to **Rocket Science Group** (founded by ex-Multiplay staff). `[official]` https://docs.unity.com/en-us/multiplay-hosting and https://www.rocketscience.gg/multiplay/
  - Matchmaker now supports third-party hosts.
  - Global UGS (Economy, Cloud Code, Remote Config) ended for **mainland China, Hong Kong and Macau orgs on June 30, 2026**. The replacement is UOS. `[official]` https://support.unity.com/hc/en-us/articles/48560161446804
- **Photon** (Exit Games): `[official]` https://doc.photonengine.com/photon/current/photon-products
  - **Fusion 2** for Unity uses state sync, with host/server and shared topologies. Fusion for Unreal/Godot is in early access.
  - **Quantum 3** is a deterministic ECS engine with predict/rollback, sending only inputs. It suits fighting, sports and MOBA-style games.
  - Free tier is 100 CCU. `[secondary]`

### Dedicated game server orchestration
- **Agones** (Google/Ubisoft, open source, Kubernetes CRDs: GameServer, Fleet, FleetAutoscaler, GameServerAllocation): `[official]` https://github.com/googleforgames/agones/releases
  - Latest release **v1.61.0, published Sept 24**. The year was inferred as 2026 from support for **Kubernetes 1.34–1.36** in v1.60.
  - v1.61 moved to Helm v4 (breaking), added a restricted-PSS sidecar, and marks GameServers Unhealthy when the game container exits.
  - v1.58 added a **Python SDK**.
  - PortRanges and PortPolicyNone are now Stable.
- **Open Match**:
  - Latest confirmed 1.x line is **v1.8.x**. `[secondary]` https://newreleases.io/project/github/googleforgames/open-match/release/v0.2.0-alpha
  - **Open Match 2** (`googleforgames/open-match2`) is in "public preview". It is a single horizontally scalable `om-core` container, gRPC with a grpc-gateway REST proxy, and language-agnostic matchmaking functions. No tagged release was visible. `[official]` https://github.com/googleforgames/open-match2
- **Amazon GameLift Servers** (renamed from "Amazon GameLift" when **GameLift Streams** launched; Streams does 1080p60 browser streaming). `[official]` https://repost.aws/articles/ARK7UPPDp4QIuP5Rd4qdgKBQ/amazon-gamelift-is-now-amazon-gamelift-servers
  - **Managed containers GA on Nov 13, 2024**, on ECS. `[official]` https://aws.amazon.com/about-aws/whats-new/2024/11/amazon-gamelift-containers-dev-iteration-management
  - **Anywhere** fleets register your own hardware or other clouds. FlexMatch handles matchmaking and FleetIQ handles Spot.
- **Hathora**: game hosting **shut down May 5, 2026** after its pivot to AI inference and acquisition by Fireworks AI. Customers were steered to **Nitrado GameFabric**. Stormgate went offline-only. `[secondary]` https://www.techspot.com/news/111969-stormgate-servers-go-dark-following-ai-focused-hosting.html and https://docs.edgegap.com/docs/tools-and-integrations/switch-from-hathora
  - Lesson: keep the hosting layer swappable (Agones-compatible containers plus an abstracted allocator).
- **Edgegap**: edge orchestration (deploys near players across many PoPs), bare-metal option, free tier of 1 app and 1 concurrent deployment. `[official]` https://edgegap.com/pricing
  - **Pricing conflict:** $0.012/vCPU-hr (third party) vs $0.00115/vCPU-min (Edgegap page, about $0.069/hr). Check the live page.
- Other providers: Gameye, Nitrado GameFabric, Rocket Science (Multiplay), i3D.net, PlayFab MPS. `[vendor]` https://gameye.com/blog/game-server-shake-up-2026

### Netcode models (reference)
- **Deterministic lockstep**:
  - Send only inputs. Every peer simulates identically, which needs fixed-point math or strict float determinism.
  - Very low bandwidth, but stalls on the slowest peer. Best for 2–4 players or RTS.
  - Source: `[official-author]` https://gafferongames.com/post/deterministic_lockstep/ (Fiedler has moved to https://mas-bandwidth.com)
- **Rollback (predict-rollback)**:
  - Run local input immediately, predict remote input, and re-simulate on mismatch.
  - **GGPO** has been MIT-licensed open source since Oct 2019 (Skullgirls, Brawlhalla, Killer Instinct). `[secondary]` https://www.gamingonlinux.com/2019/10/ggpo-a-rollback-networking-sdk-for-peer-to-peer-games-has-gone-open-source/
  - **GGRS** is the Rust equivalent.
  - Riot's **2XKO** uses **server-based rollback** over Riot Direct. Riot has shared few technical details. `[secondary]` https://www.shacknews.com/article/138850/2xko-sever-based-rollback-netcode
- **Client-side prediction plus server reconciliation, with entity interpolation and lag compensation** (authoritative server; the FPS/action default):
  - Canonical series: Gambetta Parts I–III, plus a JS demo. `[official-author]` https://gabrielgambetta.com/client-side-prediction-server-reconciliation.html and https://gabrielgambetta.com/entity-interpolation.html
- **Snapshot interpolation**:
  - The server sends state snapshots and the client renders about 100 ms in the past, interpolating between them. No client simulation is needed. Bandwidth is heavy, so use delta compression and quantization.
  - `[official-author]` https://gafferongames.com/post/snapshot_interpolation
- **Overwatch** (GDC 2017, Tim Ford, "Overwatch Gameplay Architecture and Netcode"): `[official]` https://gdcvault.com/play/1024001/-Overwatch-Gameplay-Architecture-and
  - ECS design and fixed command frames: 16 ms, or 7 ms in tournament mode.
  - Predicts abilities by default.
  - Server-authoritative rollback and reconciliation.
  - Time dilation to keep the input buffer filled.
  - Summary: `[vendor]` https://edgegap.com/blog/game-backend-deep-dive-overwatch-2016-netcode-architecture-rollback
- **Valorant**: `[official]` https://technology.riotgames.com/node/112 and `[secondary]` https://pcgamer.com/valorant-peekers-advantage-interview
  - **128-tick** dedicated servers give a frame budget of **7.8125 ms**. Server frame time was cut from 50 ms to under 2 ms.
  - Riot Direct backbone.
  - Goal: a peeker's-advantage window under about 60–80 ms.
  - Server-side rewind for hit registration.
- **League of Legends determinism series** (Riot): `[official]` https://technology.riotgames.com/node/67 and https://technology.riotgames.com/node/73
  - The server was made deterministic for **Chronobreak** (esports rewind) and disaster recovery.
  - A "Unified Clock" was the largest piece of work.
  - Divergence detection compares state logs.
- **Clash Royale lockstep** is claimed only by a dev-services blog. **Unverified**; no Supercell source was found. `[secondary]` https://sdlccorp.com/post/how-to-develop-a-game-like-clash-royale/

### Studio engineering notes
- **Supercell**:
  - Supercell ID: an HTTP account API evolved into a proxy fleet plus event routing that pushes to clients. Layers are APIs, proxies and event routing/storage. `[secondary]` https://thenewstack.io/inside-supercells-minimalist-massive-social-network/
  - Backend uses **Java** (some Rust in hot paths), **AWS**, Terraform and ZooKeeper-style coordination. `[job-posting]` https://supercell.com/en/careers/senior-backend-engineer-liveops/2262179
- **Riot** has a rich public engineering blog: https://technology.riotgames.com
- **King**:
  - Moved its core data and ML platform from on-prem Hadoop to **Google Cloud** in 2018. `[secondary]` https://www.datacenterdynamics.com/en/news/mobile-gaming-giant-king-moving-google-cloud/
  - Backend uses Java, server-authoritative services, GKE, Terraform and Helm. `[job-posting]`
  - Uses AI tooling for level creation and retuning of 18k+ levels (AP, May 2025). `[secondary]` https://fortune.com/article/candy-crush-gaming-ai-technology-art-jobs-puzzles/
  - techblog.king.com could not be reached this session.
- **Scopely (Monopoly GO)**: C#, DynamoDB, Redis, and "20M+ DAU" workloads. `[job-posting]` https://job-boards.greenhouse.io/scopely/jobs/4666681008
- **Playrix and Dream Games**: no public engineering blog or backend write-up was found. That is itself useful: their architecture is not publicly documented.

---

## 5. Ops, serving, privacy, desktop

### Remote config, feature flags and experiments
- **Firebase Remote Config** has **real-time** updates. `addOnConfigUpdateListener` keeps a persistent connection, paused in the background. Use A/B Testing with GA4 audiences. `[official]` https://firebase.google.com/docs/remote-config/real-time
- **Statsig was acquired by OpenAI** (announced Sept 2, 2025; about $1.1B in stock) and operates independently. Weigh vendor-continuity risk. `[secondary]` https://pulse2.com/openai-acquires-statsig-for-a-reported-1-1-billion/
- Other options: **LaunchDarkly** (JSON flags, kill switches), Unity Remote Config, PlayFab Title Data/Experiments, and Satori (Heroic). `[official]` https://launchdarkly.com/docs/home/flags/toggle
- Practice: ship config as signed, versioned JSON with a bundled fallback. Never block boot on config fetch, and make every risky feature kill-switchable. `[bg]`

### Live-ops content delivery
- Apple: **Apple-hosted Background Assets**, 200 GB, updatable without a binary (see §1). Android: **PAD** fast-follow and on-demand (see §2). Unity: **Addressables** remote catalog plus CCD or any CDN (see §3).
- Executable code hot-update (Lua, HybridCLR, JS) is common in Asian markets. On Apple, it must stay within guideline 2.5.2 and 4.7 limits. `[bg]`

### Phased rollouts
- **App Store phased release**: 7 days at **1%, 2%, 5%, 10%, 20%, 50%, 100%**. `[secondary]` https://helm-app.com/guides/manage-phased-release/
  - It applies only to **automatic** updaters; manual updates get the build immediately.
  - The schedule can't be customized.
  - Pause for up to 30 days total.
  - It does not roll back users who already updated, so you need a server-side kill switch.
- **Google Play staged rollout**: `[official]` https://support.google.com/googleplay/android-developer/answer/6346149
  - Any percentage, increased manually.
  - **Halt** stops new installs; users who already have the build keep it.
  - Resume uses the same user cohort.
  - Country targeting is available for production updates, and countries can't be removed once the rollout starts.
  - Not available for the first publish.
  - **Managed publishing** controls go-live timing.

### Crash reporting
- **Firebase Crashlytics (Unity)**: `[official]` https://firebase.google.com/docs/crashlytics/unity/get-deobfuscated-reports
  - SDK 8.6.1+ auto-reports IL2CPP native crashes on Android.
  - **IL2CPP needs symbol upload**: enable "Create symbols.zip", then run `firebase crashlytics:symbols:upload --app=<APP_ID> <path>`. Apple dSYM upload is auto-configured.
- **Sentry**: Unity, Unreal and Native SDKs. It accepts the Unreal Crash Reporter (desktop) without an SDK. **Console crash reporting (Xbox, PlayStation, Switch) is GA.** Users include Riot and CCP. `[official]` https://sentry.io/for/gaming/ and https://docs.sentry.io/platforms/unreal
- **Backtrace** was acquired by **Sauce Labs in July 2021** and is now "Sauce Error Reporting". It covers console, desktop, mobile and server crash and minidump analysis. `[official]` https://saucelabs.com/platform/error-reporting
- Also watch Android vitals in Play Console and **MetricKit** on iOS, which now includes Metal frame rate (§1).

### Anti-cheat and integrity (mobile)
- **Android: Play Integrity API** (see §2). Use standard requests per sensitive action and verify server-side via Google's decrypt endpoint. Hardware-backed verdicts apply on Android 13+ since May 2025.
- **Apple: App Attest** (`DCAppAttestService`): `[official]` https://developer.apple.com/documentation/devicecheck/assessing-fraud-risk and WWDC26 session 201 https://developer.apple.com/videos/play/wwdc2026/201
  - A Secure Enclave key attests the app instance. The **server validates** the attestation (there is no Apple verify endpoint for the object itself). Use assertions with counters per request.
  - **Fraud risk metric**: the server POSTs the receipt to Apple and gets an approximate 30-day count of attested keys on the device. Fold it into risk scoring rather than hard-blocking.
  - **DeviceCheck** offers 2 per-device bits that persist across reinstall, for example "promo claimed" or "flagged".
- Core rule: never trust the client. Use a server-authoritative economy, server-validated IAP (App Store Server API / Play Developer API) and server-side physics sanity checks. Shield or obfuscate IL2CPP metadata if needed. `[bg]`

### Privacy and attribution
- **ATT** (iOS 14.5+). Average opt-in among users shown the prompt: 35% in Q2 2025 and **38% in Q1 2026**. **Gaming leads at about 39%**; sports games about 54% and action about 50% (Adjust). `[secondary]` https://www.adjust.com/blog/att-opt-in-rates-2025
- **AdAttributionKit (AAK)** is the successor to SKAdNetwork 4. There was no SKAN 5. `[secondary]` https://www.adjust.com/blog/wwdc-adattributionkit-2025/
  - iOS 18.4 added configurable attribution windows (defaults: 30-day click, 1-day view), cooldowns and **overlapping re-engagement conversions**. Overlapping conversions need the Info.plist `EligibleForAdAttributionKitOverlappingConversions = YES` and conversion tags.
  - Development postback testing is under Settings, then Developer.
  - From **iOS 26.2, Apple Ads postbacks use AAK** instead of SKAN. Configure both SKAN and AAK postback copies. `[vendor]` https://support.appsflyer.com/hc/en-us/articles/34395758837137-Bulletin-Apple-Ads-now-supports-SKAN-attribution
  - Whether SKAN is formally deprecated is **disputed**: it is effectively frozen, and one source claims late-2026 endpoint deprecation (unverified). Apple's page: https://developer.apple.com/app-store/ad-attribution
- **Privacy Sandbox on Android: retired.** In mid-Oct 2025 Google retired the Attribution Reporting API, Protected Audience, Topics (Chrome and Android), **SDK Runtime**, Protected App Signals and On-Device Personalization. CHIPS, FedCM and Private State Tokens survive. `[secondary]` https://engadget.com/cybersecurity/google-has-killed-privacy-sandbox-130029899.html
  - The Android GAID remains. Do not build on Sandbox APIs.

### Steam and desktop
- **Steamworks**: `[official]` https://partner.steamgames.com/doc/store/application/platforms
  - Since Oct 14, 2019, new macOS apps must be **64-bit and notarized**. Tick "App Bundles Are Notarized".
  - Required hardened-runtime entitlements for the overlay and SDK: `com.apple.security.cs.disable-library-validation` and `com.apple.security.cs.allow-dyld-environment-variables`.
  - **App Sandbox is incompatible with Steam.**
- **macOS notarization**: `[official]` https://developer.apple.com/videos/play/wwdc2019/703
  - Sign all nested code deepest-first with **Developer ID Application** and a secure timestamp.
  - **Hardened runtime** (`codesign --options runtime`) on executables.
  - No `get-task-allow` entitlement.
  - Submit with `xcrun notarytool submit … --wait`, then `xcrun stapler staple`, then verify with `spctl -a -vv`.
  - Godot 4 users must also sign the bundled Steam framework. `[secondary]` https://godotsteam.com/tutorials/mac_export/
- **Steam Deck Verified**: 1280×800/720 legibility, controller-first defaults and no launcher issues. `[secondary]`
- **Steam Machine** launched with Valve's randomized reservation queue, purchase emails June 29, 2026. Price is **$1,049 (512 GB) / $1,349 (2 TB)**. `[secondary]` https://tbreak.com/valve-steam-machine-price-release-date/
  - **Steam Machine Verified** requires **native 1080p at a stable 30 FPS**, full controller support and good default settings. Deck Verified titles auto-qualify, but not the reverse. `[secondary]` https://heise.de/-11208466
- **Steam Frame** (ARM VR headset running x86 via FEX): $1,059 (256 GB) / $1,299 (1 TB), purchase emails from Sept 18, 2026. Deck ratings do **not** carry over; each game is tested. `[secondary]` https://roadtovr.com/valve-steam-frame-price-release-pre-orders/

---

## Known conflicts / verify before use
1. **Android 16 KB enforcement date.** The official page says Feb 1, 2027 for updates; older secondary sources said Nov 1, 2025 (extension to May 31, 2026). Use the official date and re-check Play Console.
2. **MetalFX Frame Interpolation ratio** (1 generated frame per 2 rendered vs more). Check WWDC25 session 211.
3. **Godot 4.6 release date** (Jan 27 vs Feb 27, 2026).
4. **Agones v1.61.0 year** is inferred as 2026.
5. **Edgegap per-vCPU price.** The two figures are incompatible.
6. **Unity 6.5 date** (mid-June vs a forum post in Aug 2026). The Unity 7 timeline is press-sourced and Unity has reset roadmaps before.
7. **Android vitals thresholds** (1.09% / 0.47% / 8%) come from 2022.
8. **SKAN deprecation status** is unclear.
9. **Cocos acquisition** is unconfirmed.
10. **Clash Royale lockstep** is unconfirmed.
11. **Play partner 10 GB PAD allowance** is likely superseded by the Level Up 30 GB limit.
12. **iOS 27 shipping status**, and whether `LSSupportsGameMode`, MetricKit Metal FPS and localized asset packs are live, is assumed but not confirmed.
13. **Thin areas.** Apple Silicon Mac gaming market data, iOS 26/27 Game Controller API changes, and Playrix/Dream Games backend details were not found. Do not invent them.
