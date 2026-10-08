---
name: gamedev-android-engineer
description: >-
  Build Android games in C++ and Kotlin: NDK and AGDK (GameActivity, GameTextInput, Game Controller
  library, Swappy frame pacing, Memory Advice), Vulkan with ANGLE for GLES, ADPF thermal headroom and
  hint sessions, Play Games Services v2, Play Billing 8+ with server verification, Play Asset Delivery,
  Play Integrity, and Play policy deadlines. Use when someone asks to set up or audit an Android game
  client, fix jank, ANRs, crashes or thermal throttling, migrate Play Billing or Play Games Services,
  meet target API 36 or 16 KB page-size rules, or wrap a native game in a Compose shell.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: client-eng
---

# Android Game Engineer

An Android game ships to ten thousand device models, each with its own GPU driver, thermal envelope, refresh rate and OEM battery policy, and Google Play grades you on the worst of them. The craft is not writing a render loop; it is making one loop behave on all of them: present frames at an even cadence (Swappy), back off before the SoC throttles (ADPF), stay inside memory before the low-memory killer decides for you, and keep the main thread free so the input dispatcher never declares an ANR. The game runs in C++; Kotlin is the shell that talks to Play. Keep that boundary narrow, keep the store server-verified, and treat every Play policy date as a release blocker, because missing one means you cannot ship an update at all.

## Role Profile

**Be honest about the market.** Job-post research found Kotlin essentially absent from top-studio game-engine roles; it appears only in SDK roles (for example Netflix's Android Games SDK). Android game work at top studios is **C++ and NDK**:

- **King Shared Tech** ("client technology platform behind Candy Crush"): C++, Android NDK, CMake, Gradle, Lua/Python scripting, Jenkins/GitHub/SonarQube CI; OpenGL/Vulkan/Metal a bonus.
- **thatgamecompany** (Sky's Vulkan port): strong C++, Vulkan, Java/JNI. **Epic:** 5+ years of Android NDK/C++.
- Most top-grossing titles (Dream Games, Monopoly GO, Genshin) ship on Unity; their Android engineers own the native plugin layer, Gradle build, Play SDK integration and device compatibility rather than a Kotlin game.

| Dimension | What it looks like |
| --- | --- |
| Responsibilities | Native platform layer (GameActivity, input, audio, lifecycle); Vulkan/GLES backend support; frame pacing and thermal policy; Play Billing, PGS, PAD, Integrity integration; Gradle/CMake build; Play policy compliance; vitals triage |
| Hard skills | C++17/20, NDK, JNI, CMake, Gradle/AGP, Vulkan, Kotlin for the shell, Android lifecycle and process model, memory and LMK behavior |
| Tools | Android Studio, Perfetto (ui.perfetto.dev), Android GPU Inspector, Android Performance Tuner, Play Console Android vitals, AGDE for Visual Studio, `adb`, `llvm-objdump` |
| KPIs (inferred) | User-perceived ANR and crash rate across device fragmentation; frame pacing / jank; AAB and download size; policy-deadline compliance |
| Collaborators | Engine team, QA device lab, release/build engineering, backend (purchase verification), Unity engineers for plugin work |

Sources: https://www.wearedevelopers.com/en/jobs/ext/5630392/developer , https://hitmarker.net/jobs/thatgamecompany-generalist-software-engineer-android-714679 , https://www.workingnomads.com/jobs/software-engineer-5-android-games-sdk-netflix-1429707

## When to Use / Not

Use for the Android-specific half of any game client: native activity and loop, Android graphics APIs, frame pacing, thermal and memory adaptation, Play services, Play policy, vitals.

Not for: Unity C# and Addressables (`gamedev-unity-engineer`, but this skill owns the Android plugin and Gradle side); Vulkan-agnostic engine architecture (`gamedev-engine-architect`); cross-platform device tiers and budgets (`gamedev-optimization-compatibility`); purchase ledger and Play Developer API server code (`gamedev-backend-engineer`); integrity scoring and ban logic (`gamedev-anti-cheat-security`); staged rollout mechanics (`gamedev-delivery-release`); offer design (`gamedev-monetization-designer`).

## Inputs to Gather

- **Engine:** custom C++, Unity, Unreal, Godot, Defold, Cocos? Default: assume an engine with a native plugin layer you own.
- **minSdk and device floor:** default minSdk 24 with Vulkan 1.1 as the primary API on 64-bit Android 10+ devices and a GLES fallback. ADPF needs API 30 (thermal) and 31 (hint).
- **Frame target per tier:** default 60 fps on tier A, 30 fps on tier C; 90/120 only for action genres on devices with headroom.
- **Play SDK versions in use:** Billing library major, PGS v1 or v2, PAD, Integrity. Any v1 PGS or PBL 7 is an immediate blocker.
- **Native dependencies:** every prebuilt `.so` (ads, physics, audio middleware, analytics). Each must be 16 KB-aligned.
- **Account model:** PGS v2 identity only, or a studio account for cross-device and cross-platform progress? Default: studio account with PGS as one linked identity.
- **Content size:** base module and post-install content. Above ~150 MB, design PAD packs now.

## Method

1. **Split the process cleanly.** Run the game in C++ on GameActivity's `android_main` thread; keep Kotlin for Play SDKs and shell UI. Cross JNI with coarse, batched calls (a purchase request, a sign-in result), never per frame. The main thread must stay idle so input dispatch never times out.
2. **Pick graphics by device, not by preference.** Vulkan first; GLES is frozen ("no longer under active feature development") and its future is ANGLE on the Vulkan driver. Keep a GLES path only for broken-driver denylists and old devices, and test ANGLE (optional layer on Android 15+) with your GLES path now.
3. **Pace frames with Swappy.** Present through Swappy (Vulkan or GL) with an explicit swap interval. Self-timed sleeps and `eglSwapInterval` alone produce 16/33 ms alternation on 60 Hz panels and worse on 90/120 Hz ones.
4. **Adapt to thermals before throttling.** Poll `getThermalHeadroom` at a low rate and map headroom to your own knobs (render scale, frame cap, effects), not engine presets. Create a Performance Hint session for the game and render threads and report actual work duration every frame so the scheduler right-sizes clocks.
5. **Budget memory against the device.** Use the Memory Advice API (beta) or your own `onTrimMemory` handling to shed caches before the low-memory killer acts. A background kill reads as a crash to the player even when vitals do not count it.
6. **Handle input through AGDK.** GameActivity input buffers for touch and keys, the Game Controller library (formerly Paddleboat) for gamepads, GameTextInput for the soft keyboard.
7. **Make the store server-authoritative.** Play Billing 8+ (current 9.x): query with `queryProductDetailsAsync`, buy with an obfuscated account ID, send the purchase token to your server, verify it with the Play Developer API, grant, then acknowledge or consume. Unacknowledged purchases are refunded after 3 days (verify the current window in Play docs). Listen to Real-time developer notifications for refunds and voids.
8. **Move to PGS v2 and your own account.** v2 signs players in automatically; it is not a cross-platform account. Pair it with your backend account via Credential Manager or Sign in with Google, because the legacy Google Sign-In for Android API is unsupported from Sept 2026.
9. **Deliver content with PAD.** Install-time only for the first session, fast-follow for the next chapters, on-demand for optional content. Use texture compression format targeting so each device gets ASTC or ETC2 without shipping both. Query pack locations every time; the OS can move or delete them.
10. **Gate with Play Integrity standard requests** on sensitive actions and verify server-side. Treat verdicts as risk signals; the economy stays server-authoritative.
11. **Run the compliance gate every release:** target API, PBL version, 16 KB alignment, `appCategory="game"`, PGS v2, privacy declarations. These block publishing, not just ranking.
12. **Measure in the field.** Ship Android Performance Tuner or equivalent frame-time telemetry, watch Android vitals per device model, and reproduce outliers in Perfetto and AGI on the actual model.

## Deliverables

### 1. Android Platform Decision Record

```
GAME:                 [title]            DATE: [yyyy-mm-dd]
ENGINE / NATIVE LAYER: [custom C++ on GameActivity | Unity + native plugins | ...]
minSdk / targetSdk:   [24+] / 36         ABIs: arm64-v8a [+ armeabi-v7a? x86_64 for emulators/PC]
GRAPHICS:             Vulkan 1.1 primary; GLES fallback list (GPU/driver denylist); ANGLE tested Y/N
FRAME PACING:         Swappy [Vk|GL], intervals per tier: A [60/90/120] B [60] C [30]
THERMAL / HINT:       headroom thresholds -> knobs (table); hint session threads [game, render]
MEMORY:               budget per tier (MB); Memory Advice / onTrimMemory policy
INPUT:                GameActivity input, Game Controller library, GameTextInput
PLAY SERVICES:        PBL [9.x]; PGS v2; PAD packs; Integrity standard requests
ACCOUNT:              studio account; PGS v2 linked; Credential Manager sign-in
SHELL UI:             Compose in separate Activity / overlay (touch pass-through plan)
COMPLIANCE:           target API 36; 16 KB aligned; appCategory=game; vitals targets
```

### 2. Thermal Policy (headroom-driven)

```
Headroom (10 s forecast) │ Frame cap │ Render scale │ Effects │ Notes
< 0.70                    │ target    │ 1.0          │ full    │
0.70 - 0.85               │ target    │ 0.85         │ reduced │ start trimming before throttle
0.85 - 0.95               │ 60 or 30  │ 0.75         │ low     │
>= 0.95 (1.0 = severe)    │ 30        │ 0.65         │ minimum │ also stop background downloads
Hysteresis: hold a lower tier at least 30 s before stepping up. Thresholds are a starting heuristic.
```

### 3. ADPF wiring (Kotlin side)

```kotlin
class AdpfController(context: Context, private val onTier: (Int) -> Unit) {
    private val power = context.getSystemService(PowerManager::class.java)
    private val hints = context.getSystemService(PerformanceHintManager::class.java)
    private var session: PerformanceHintManager.Session? = null

    /** tids: game + render thread IDs (Process.myTid() from each thread). API 31+. */
    fun startHints(tids: IntArray, targetNanos: Long) {
        session = hints?.createHintSession(tids, targetNanos)
    }

    /** Call every frame with measured CPU work time (not wall time including vsync wait). */
    fun reportFrame(actualNanos: Long) = session?.reportActualWorkDuration(actualNanos)

    fun setTarget(nanos: Long) = session?.updateTargetWorkDuration(nanos)

    /** Poll about once per second at most; frequent calls can return NaN (verify current limit). API 30+. */
    fun pollThermal() {
        val headroom = power?.getThermalHeadroom(10) ?: return
        if (headroom.isNaN()) return
        onTier(when {
            headroom < 0.70f -> 0
            headroom < 0.85f -> 1
            headroom < 0.95f -> 2
            else -> 3
        })
    }
}
```

In pure C++ engines, use the NDK equivalents (`AThermal_getThermalHeadroom`, `APerformanceHint_*`) and skip JNI entirely; see the native reference.

### 4. Release Compliance Gate

```
Check                                         │ Command / where                                  │ Pass
targetSdk = 36                                 │ merged manifest                                   │
PBL >= 8 detected by Play                      │ merged manifest com.google.android.play.billingclient.version │
No PGS v1 APIs; not on play-services-games 25.0.0 while still v1 │ dependency tree                │
16 KB: every .so LOAD align 2**14              │ llvm-objdump -p lib.so | grep LOAD                │
16 KB: APK zip alignment                       │ zipalign -v -c -P 16 4 app.apk                    │
16 KB: boots on 16 KB device/emulator          │ adb shell getconf PAGE_SIZE  (expect 16384)       │
android:appCategory="game"                     │ manifest application tag                          │
Unacknowledged purchases = 0 after 72 h        │ server dashboard                                  │
Vitals below bad-behavior thresholds           │ Play Console, overall and per device model        │
```

Read `references/kotlin-snippets.md` when writing Play Billing, PGS v2 sign-in, Play Integrity, PAD, or the Compose shell around the game surface. Read `references/native-cpp-snippets.md` when writing the GameActivity loop, Swappy, NDK ADPF, Game Controller library, Memory Advice, or the 16 KB build flags.

## Technical Reference

### Play policy dates (as of 2026-10; verify in Play Console)

| Requirement | Status / date | Source |
| --- | --- | --- |
| Target API 36 (Android 16) for new apps and updates | In force since **Aug 31, 2026**; extension to **Nov 1, 2026** on request; Wear OS/Automotive 35, TV/XR 34 | https://developer.android.com/google/play/requirements/target-sdk |
| Play Billing Library 8+ | Required since **Aug 31, 2026** (extension to Nov 1, 2026). v8 accepted until Aug 31, 2027; v9 until Aug 31, 2028. Current: **9.0.0** (May 19, 2026), **9.1.0** (June 18, 2026, Billing Choice APIs) | https://developer.android.com/google/play/billing/deprecation-faq |
| 16 KB page size | Apps targeting Android 15+ must support it on 64-bit devices; from **Feb 1, 2027** updates without support cannot be released. Older secondary sources citing Nov 1, 2025 / May 31, 2026 are superseded | https://developer.android.com/guide/practices/page-sizes |
| PGS v1 | Deprecated after Sept 2025; **v1 APIs removed from the SDK June 15, 2026** (`play-services-games:25.0.0`); Google Sign-In for Android unsupported from **Sept 2026**; v1 shutdown **May/June 2027** | https://developer.android.com/games/pgs/deprecation |
| Large screens | API 36 ignores orientation, resizability and aspect-ratio limits on sw600dp+; **games exempt** with `android:appCategory="game"`; Android 17 (API 37) removes the opt-out for non-games | https://developer.android.com/develop/adaptive-apps/guides/app-orientation-aspect-ratio-resizability |

### Graphics and AGDK

- **Vulkan:** since Android 7; all 64-bit devices on Android 10+ support Vulkan 1.1; about 85% of active devices support Vulkan. GLES is not under active feature development. **ANGLE** ships as an optional layer on Android 15+. Source: https://developer.android.com/games/develop/vulkan/overview
- **AGDK** (overview updated 2026-02-26): GameActivity (replaces NativeActivity), GameTextInput, Game Controller library (formerly Paddleboat), Frame Pacing (Swappy, GL and Vulkan), **Memory Advice API (Beta)**, Oboe, Android Performance Tuner, AGI, AGDE. No deprecations listed. Source: https://developer.android.com/games/agdk/overview
- **ADPF:** Thermal API (API 30+) `getThermalHeadroom(forecastSeconds)`, 1.0 means severe throttling; Performance Hint API (API 31+) with `updateTargetWorkDuration` and `reportActualWorkDuration` each frame; also Game Mode / Game State APIs and Fixed Performance Mode for benchmarking. Map headroom to your own knobs. Source: https://developer.android.com/games/optimize/adpf

### Play services

- **Billing 8 changes:** in-app items renamed one-time products (multiple purchase options and offers); `enableAutoServiceReconnection()`; sub-response codes such as `PAYMENT_DECLINED_DUE_TO_INSUFFICIENT_FUNDS`; removed `querySkuDetailsAsync`, the no-argument `enablePendingPurchases()`, and querying expired subscriptions or consumed purchases. **9.0** returns `BILLING_UNAVAILABLE` for system-blocked activity (OEM kids mode). Multi-module merges can drop the `billingclient.version` manifest entry Play uses to detect the version.
- **PGS v2:** automatic platform sign-in at launch; run your own account system for cross-device/cross-platform progress. Source: https://developer.android.com/games/pgs/migration_overview
- **PAD** (page updated 2026-10-06): install-time (counts toward install size), fast-follow, on-demand; texture compression format targeting. Limits: base module 200 MB; each pack 1.5 GB; install-time total 4 GB; fast-follow plus on-demand 4 GB, or **30 GB** for Level Up program / XR titles; max 100 packs. Source: https://support.google.com/googleplay/android-developer/answer/9859372#size_limits
- **Play Integrity:** hardware-backed device verdict on Android 13+ since May 2025; use standard requests (cached, a few hundred ms, built-in replay protection) per action; optional `MEETS_STRONG_INTEGRITY` adds patch recency. On Google Play Games on PC the verdict includes `meets-virtual-integrity`. Source: https://developer.android.com/google/play/integrity/improvements
- **Google Play Games on PC** went GA Sept 23, 2025 and accepts native PC games; native PC titles calling Play Billing must migrate to the PC SDK.

### Quality thresholds and tools

- **Android vitals bad-behavior thresholds:** 1.09% user-perceived crash rate, 0.47% user-perceived ANR rate, 8% on any single device model (2022 figures; verify current values in Play Console). Crossing them reduces Play visibility and can add a store-listing warning. Source: https://android-developers.googleblog.com/2022/10/raising-bar-on-technical-quality-on-google-play.html
- ANR trigger to design around: input dispatch not handled within about 5 seconds on the main thread.
- **AGI** system profiler (built on Perfetto: CPU scheduling, GPU counters, Vulkan traces, memory, power) and frame profiler (per-draw, Vulkan and GLES). **APT** reports frame time (CPU vs GPU) and load time by quality level and device into Android vitals. Source: https://developer.android.com/agi/sys-trace/system-profiler

### Frame budgets

| Rate | Frame | Sustained CPU/GPU target (~80%, heuristic) |
| --- | --- | --- |
| 30 | 33.3 ms | 26.7 ms |
| 60 | 16.67 ms | 13.3 ms |
| 90 | 11.1 ms | 8.9 ms |
| 120 | 8.33 ms | 6.7 ms |

## Diagnostics

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Average 60 fps but visible stutter | Uneven present timing (16/33 ms alternation) | Swappy with a fixed swap interval; check frame-time histogram, not average fps |
| FPS halves after 10 to 15 minutes | Thermal throttling, no ADPF policy | Headroom tiers; hint session; lower render scale before headroom reaches 0.95 |
| ANRs clustered at startup or store open | Asset loading, JNI-blocking calls, or billing connect on the main thread | Move to background threads; keep `android_main` off the UI thread; async billing |
| Crash only on certain Mali/Adreno driver versions | Driver bug in Vulkan path | Device/driver denylist to GLES (or ANGLE) path; report to vendor; reproduce in AGI |
| Play Console rejects update for 16 KB | A prebuilt `.so` (often ads or middleware) has 4 KB LOAD alignment | `llvm-objdump -p`; upgrade or rebuild the SDK; NDK r28+ or `-Wl,-z,max-page-size=16384` |
| Play says PBL version too old though code uses 9.x | Manifest merge dropped `billingclient.version` | Inspect merged manifest; fix module that strips the meta-data |
| Purchases auto-refunded after 3 days | Server verified and granted but never acknowledged | Acknowledge server-side after grant, or consume for consumables; alert on unacknowledged count |
| Pack files missing after an update or storage cleanup | Cached a fast-follow or on-demand pack path | Call `getPackLocation` every launch; re-fetch when null |
| Sign-in failures from Sept 2026 | Legacy Google Sign-In for Android API | Move to PGS v2 plus Credential Manager |
| Tablet build letterboxed or stretched on Android 16 | Missing game category, so resizability overrides apply | Add `android:appCategory="game"`; still test foldable posture changes |
| Background kill when returning from a purchase or ad | Memory pressure, large native heap | Memory Advice / `onTrimMemory` shedding; lower texture budget on low-RAM tiers |

## Anti-Patterns

**Kotlin Game Loop** — gameplay or rendering on a Compose `Canvas` or on the main thread. It ties frame rate to UI work and produces ANRs under load.

**Chatty JNI** — crossing JNI per entity or per frame. Batch at coarse boundaries; every crossing is overhead and a lifetime bug waiting for a stale `jobject`.

**Preset Thermal Policy** — mapping headroom to the engine's Low/Medium/High preset. Google's guidance is your own knobs; presets drop quality the player notices for savings the SoC does not need.

**Client-Acknowledged Purchases** — granting and acknowledging on the device. Token replay and modded clients mint currency; the server must verify before anything is granted.

**The Silent SDK Bump** — updating a third-party ad or analytics SDK without re-checking 16 KB alignment, PBL detection, and manifest merges. Most compliance failures arrive through dependencies.

**GLES Forever** — new rendering work on GLES because it already works. It is frozen, and its future runs on Vulkan via ANGLE anyway.

**PGS as Account System** — treating the PGS v2 player as the only identity. Players lose progress on iOS, PC, or a new Google account.

**Average-FPS Reporting** — dashboards with mean fps. Jank lives in the p95 frame time and in frame-time variance.

## Quality Checklist

- [ ] Game logic and rendering run off the main thread; JNI crossings are coarse and batched
- [ ] Vulkan primary with a documented GLES/ANGLE fallback and driver denylist
- [ ] Swappy in use with explicit swap intervals per tier; frame-time histogram captured on tier A, B, C devices
- [ ] ADPF thermal tiers and hint session implemented, with hysteresis; tested on a warm device
- [ ] Memory budget per tier; trim handling sheds caches before LMK
- [ ] PBL 8+ (9.x preferred); server verifies tokens, grants idempotently, acknowledges or consumes; RTDN handled
- [ ] PGS v2 only; no v1 APIs; legacy Google Sign-In removed; studio account linking exists
- [ ] PAD packs sized within limits; locations queried every time; TCFT configured
- [ ] Play Integrity standard requests on sensitive actions, verified server-side
- [ ] targetSdk 36; every `.so` 16 KB-aligned; `zipalign -P 16` passes; boots on a 16 KB device
- [ ] `android:appCategory="game"` set; foldable and large-screen behavior tested
- [ ] Crash and ANR rates under vitals thresholds overall and per top-20 device model
- [ ] Every policy date in docs carries an as-of tag and a source link

## Related Skills

Device tiers, memory and app-size budgets, and the compatibility lab plan belong to `gamedev-optimization-compatibility`; this skill implements the hooks they need. Purchase verification, RTDN handling and the entitlement ledger live in `gamedev-backend-engineer`; integrity verdict scoring in `gamedev-anti-cheat-security`. For Unity projects, the C# side is `gamedev-unity-engineer` and the Gradle, plugin and manifest side stays here. Signing, AAB upload, staged rollout and halts: `gamedev-delivery-release`. Engine loop and threading: `gamedev-engine-architect`. Shader and texture-format decisions: `gamedev-technical-artist`. The iOS counterpart is `gamedev-ios-engineer`; Play Games on PC overlaps with `gamedev-desktop-engineer`. Touch layout and safe areas: if installed, `mobile-game-ux-designer`.
