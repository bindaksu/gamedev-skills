---
name: gamedev-desktop-engineer
description: >-
  Ship games on PC and Mac storefronts: Steamworks achievements, Steam Cloud and Steam Input, Steam Deck
  and Steam Machine Verified readiness, keyboard-mouse plus gamepad input, display modes, HDR and
  ultrawide, Windows packaging, macOS notarization and entitlements, Mac App Store, Epic and Microsoft
  Store, and cross-progression with mobile. Use when someone asks to port a mobile game to PC or Mac,
  integrate Steamworks, pass Deck or Steam Machine verification, notarize a Mac build, pick desktop
  stores, or fix input, resolution, HDR or save-sync problems on desktop.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: client-eng
---

# Desktop Engineer

A desktop port is not a bigger phone build. The PC player sits 60 cm from a 27-inch monitor, or 3 m from a TV, or holds a 7-inch Deck; drives the game with a mouse, a keyboard, a gamepad, or all three in one session; expects alt-tab, ultrawide, rebinding and a frame-rate cap; and writes a Steam review the day a mobile-style energy timer appears. The engineering is mostly platform plumbing done exactly right: Steamworks callbacks pumped every frame, saves that sync without clobbering, input that hot-switches glyphs, a window that survives monitor changes, and a Mac bundle that is signed, hardened and notarized so Gatekeeper lets it launch. Treat every store as a separate build target with its own rules, because the Mac App Store and Steam have mutually exclusive requirements.

## Role Profile

**Be honest about the evidence.** The role research covered top-grossing mobile studios and found no dedicated PC/Steam engineer postings; desktop work at those studios appears as a responsibility inside client or UI roles. Adjacent evidence:

- Supercell's Project R.I.S.E. (Unreal) UI role requires UI "responsiveness in fast combat across mouse, keyboard and touch".
- Rovio lists "a Switch port is a plus" for senior Unity engineers, the same porting skill set.
- Google Play Games on PC went GA in Sept 2025 and opened to native PC games, and NetEase's newer titles (Marvel Rivals) are largely PC/console, so mobile-first studios increasingly ship desktop SKUs.
- For cross-progression, Supercell ID evolved from an HTTP account API into proxies plus event routing that pushes to clients; one account across devices is the model to copy.

| Dimension | What it looks like |
| --- | --- |
| Responsibilities | Steamworks/EOS/GDK integration; input layer (KB/M, gamepad, Steam Input); window, display and HDR handling; Windows and macOS packaging, signing and notarization; Deck/Machine verification; store submissions; cross-progression client side |
| Hard skills | C++ or C# (engine-dependent), Win32/DXGI basics, macOS bundles and codesign, Steamworks SDK, VDF/SteamPipe, Proton behavior, platform identity and auth tickets |
| Tools | Steamworks partner site and steamcmd, Steam Deck dev kit or retail Deck, Xcode and `notarytool`, signtool, PIX/RenderDoc, Instruments for Mac |
| KPIs (inferred) | Steam review score; Deck/Machine verification status; crash rate by GPU vendor and driver; refund rate within 2 hours played; save-sync conflict rate |
| Collaborators | UI/UX designers (scaling, glyphs), engine and rendering, backend (accounts, entitlements), monetization, QA (hardware matrix), release |

Sources: https://jobs.accel.com/companies/space-ape-games-2/jobs/68314184-senior-ui-programmer-project-r-i-s-e , https://www.androidauthority.com/google-play-games-pc-no-longer-beta-general-availability-3599973/ , https://thenewstack.io/inside-supercells-minimalist-massive-social-network/

## When to Use / Not

Use for PC and Mac builds, desktop storefront SDKs, Deck/Machine/Frame readiness, desktop input and display, desktop packaging and signing, and the client side of cross-progression.

Not for: Metal renderer port work and Game Porting Toolkit evaluation (`gamedev-metal-graphics-engineer`); account and save services (`gamedev-platform-server-architect`, `gamedev-backend-engineer`); UI scaling visuals and glyph art (`gamedev-ui-designer`); rebinding and subtitle requirements (`gamedev-accessibility-specialist`); PC anti-cheat (`gamedev-anti-cheat-security`); CI and depot automation beyond the build script (`gamedev-delivery-release`); PC monetization model choice (`gamedev-monetization-designer`).

## Inputs to Gather

- **Source platform and engine:** mobile Unity/Unreal/Godot/custom port, or desktop-first? Default: mobile Unity port.
- **Target stores:** Steam, Epic, Microsoft Store/PC Game Pass, Mac App Store, Google Play Games on PC. Default: Steam first (Windows plus Deck), Mac on Steam second.
- **Handheld and living-room targets:** Deck Verified, Steam Machine Verified, Steam Frame. Default: aim for Deck Verified, which also qualifies for Steam Machine.
- **Business model on PC:** premium, F2P with cosmetics, or mobile F2P economy unchanged? Default: assume the mobile economy needs rework, and confirm with monetization.
- **Account model:** studio account exists? Platform identities to link? Default: link Steam, Game Center, PGS v2 and Epic to one studio account.
- **Anti-cheat and online:** competitive PvP needs Proton-compatible anti-cheat to pass Deck review.
- **Mac hardware floor:** Apple silicon only is the reasonable default for new ports.

## Method

1. **Treat each store as a build target.** Define targets (Steam-Win, Steam-Mac, Epic-Win, MS Store, MAS) with their SDK, entitlements and payment rules. The Mac App Store requires App Sandbox and Apple IAP; Steam requires no sandbox. One Mac binary cannot serve both.
2. **Wire the store SDK at the edges.** Initialize Steamworks (or EOS/GDK) once, pump callbacks every frame, and wrap it behind an interface (`IPlatformServices`) so non-Steam builds compile without it. Gate store-only features (overlay, achievements) behind capability checks.
3. **Rebuild input as action-based.** Map actions, not keys or buttons. Support KB/M and gamepad simultaneously, switch glyphs to the last device used, allow full rebinding, and use Steam Input action sets on Steam so Deck and every controller Steam supports work without per-device code.
4. **Make the window a citizen.** Borderless fullscreen default, windowed and exclusive optional; per-monitor DPI awareness on Windows; survive monitor hot-plug and resolution changes; pause or mute on focus loss as a setting; frame-rate cap and VSync options.
5. **Lay out UI for every aspect ratio.** 16:9, 16:10 (Deck), 21:9 and 32:9. Anchor HUD to the edges of a safe region, scale UI by both resolution and a user slider, and use Hor+ field of view. Mobile layouts with 44 pt touch targets become oversized and sparse on a monitor; redesign density with `gamedev-ui-designer`.
6. **Hit the handheld bar early.** Test at 1280x800 on a Deck from the first playable: legible text, controller-only path through every screen including launcher and login, on-screen keyboard for text fields, sane default graphics settings. Steam Machine needs native 1080p at a stable 30 fps.
7. **Sync saves deliberately.** Steam Auto-Cloud for simple per-user files, or your backend for cross-platform progress. Never both for the same data. Write atomically (temp file then rename), version every save, and resolve conflicts with an explicit rule plus a player choice when the rule is ambiguous.
8. **Rework monetization for the audience.** Remove energy gates and forced ads, keep cosmetics and expansions, honor platform payment rules (Steam in-game purchases through Steam's microtransaction flow; verify current Steamworks policy), and decide how purchases made on mobile appear on PC. Hand the economics to `gamedev-monetization-designer`.
9. **Package and sign every build.** Windows: Authenticode-sign executables to reduce SmartScreen friction, ship through SteamPipe depots. Mac: sign nested code deepest-first with Developer ID, hardened runtime, the two Steam entitlements, notarize, staple, verify.
10. **Link identities for cross-progression.** On Steam, obtain a Web API auth ticket and let the server verify it; link to the studio account. Do the same with Game Center, PGS v2 and Epic. The server, not the client, decides which platform identity owns which account.

## Deliverables

### 1. Store Target Matrix

```
Target      │ SDK / services          │ Payment            │ Sandbox │ Signing                    │ Anti-cheat │ Owner
Steam-Win   │ Steamworks              │ Steam microtxn     │ n/a     │ Authenticode               │            │
Steam-Mac   │ Steamworks              │ Steam microtxn     │ NO      │ Developer ID + notarize    │            │
Epic-Win    │ EOS SDK                 │ Epic / own (verify)│ n/a     │ Authenticode               │ EOS AC?    │
MS Store    │ GDK / Store APIs        │ Microsoft Store    │ n/a     │ Store-signed MSIX / Win32  │            │
MAS         │ GameKit, StoreKit 2     │ Apple IAP          │ YES     │ Apple Distribution         │            │
GPG-PC      │ Play Games PC SDK       │ Play Billing PC SDK│ n/a     │ per Play Games on PC docs  │            │
```

### 2. Deck / Steam Machine Readiness Sheet

```
Area          │ Requirement                                              │ Status │ Evidence (video/screens)
Input         │ Full controller support, correct glyphs, no KB/M needed │        │
Text entry    │ On-screen keyboard invoked for every text field         │        │
Display       │ Supports 1280x800/720; text legible at that resolution   │        │
Defaults      │ Good default settings on first launch, no config needed │        │
Seamlessness  │ Launcher and login fully controller-navigable            │        │
Compatibility │ Runs under Proton (or native Linux); anti-cheat works    │        │
Machine only  │ Native 1080p, stable 30 fps, full controller, defaults   │        │
Frame         │ Tested separately; Deck rating does not carry over       │        │
```

### 3. Steamworks core (C++)

```cpp
#include "steam/steam_api.h"

bool PlatformSteam::init(uint32_t appId) {
    if (SteamAPI_RestartAppIfNecessary(appId)) return false;   // relaunch through Steam
    SteamErrMsg err{};
    if (SteamAPI_InitEx(&err) != k_ESteamAPIInitResult_OK) {   // SDK 1.58+; older: SteamAPI_Init()
        log("Steam init failed: %s", err);
        return false;                                           // run without Steam features
    }
    SteamInput()->Init(true);   // true = we call RunFrame explicitly in tick()
    onDeck_ = SteamUtils()->IsSteamRunningOnSteamDeck();
    return true;
}

void PlatformSteam::tick() {
    SteamAPI_RunCallbacks();          // every frame, on one thread
    SteamInput()->RunFrame();
}

void PlatformSteam::unlock(const char* apiName) {
    SteamUserStats()->SetAchievement(apiName);
    SteamUserStats()->StoreStats();   // batch: call after a group of changes, not per stat tick
}

void PlatformSteam::shutdown() { SteamInput()->Shutdown(); SteamAPI_Shutdown(); }
```

Read `references/steamworks-snippets.md` when writing Steam Input action sets, stats, Steam Cloud, the on-screen keyboard, Web API auth tickets for the backend, or SteamPipe build scripts. Read `references/mac-distribution.md` when signing, notarizing, choosing entitlements, or deciding between Steam and the Mac App Store. Read `references/mobile-to-pc-porting.md` when planning a port from a mobile codebase.

## Technical Reference

### Steam hardware programs (as of 2026-10; verify)

| Program | Bar | Source |
| --- | --- | --- |
| Steam Deck Verified | Legible at 1280x800/720, controller-first defaults, no launcher issues; Valve's full criteria cover input, display, seamlessness and system support (Proton, anti-cheat) | secondary summary; read Valve's current criteria page in the Steamworks docs |
| Steam Machine Verified | **Native 1080p at a stable 30 fps**, full controller support, good default settings; Deck Verified titles auto-qualify, not the reverse | https://heise.de/-11208466 |
| Steam Machine hardware | $1,049 (512 GB) / $1,349 (2 TB); reservation-queue purchase emails from June 29, 2026 | https://tbreak.com/valve-steam-machine-price-release-date/ |
| Steam Frame (ARM VR headset, x86 via FEX) | $1,059 / $1,299; emails from Sept 18, 2026; Deck ratings do **not** carry over, each game is tested | https://roadtovr.com/valve-steam-frame-price-release-pre-orders/ |

### Mac distribution

- Steam: since Oct 14, 2019 new macOS apps must be **64-bit and notarized** ("App Bundles Are Notarized" checkbox). Hardened-runtime entitlements Steam needs: `com.apple.security.cs.disable-library-validation` and `com.apple.security.cs.allow-dyld-environment-variables`. **App Sandbox is incompatible with Steam.** Source: https://partner.steamgames.com/doc/store/application/platforms
- Notarization: sign nested code deepest-first with **Developer ID Application** and a secure timestamp; `codesign --options runtime`; no `get-task-allow`; `xcrun notarytool submit ... --wait`; `xcrun stapler staple`; verify with `spctl -a -vv`. Godot exports must also sign the bundled Steam framework. Source: https://developer.apple.com/videos/play/wwdc2019/703
- Mac App Store: App Sandbox required, Apple IAP for digital goods, Game Center available; WWDC26 added a Steam Asset Converter for App Store media (as of 2026-10; verify).
- Game Mode on Mac: macOS 14+ automatic; `GCSupportsGameMode` and `LSSupportsGameMode` (macOS 26+) plus a games `LSApplicationCategoryType`.
- Porting a Windows renderer to Metal: Game Porting Toolkit 4 (WWDC26) evaluation and Metal shader converter; hand to `gamedev-metal-graphics-engineer`.

### Display

| Topic | Rule |
| --- | --- |
| Default mode | Borderless fullscreen at desktop resolution; on Windows 10/11 flip-model swapchains make borderless nearly as fast as exclusive |
| DPI | Per-monitor DPI aware (v2) manifest on Windows; on Mac use backing scale factor and render at pixel size |
| Aspect | 16:9 baseline, 16:10 (Deck, many laptops and Macs), 21:9, 32:9; Hor+ FOV; HUD anchored to a safe region with an optional max-width |
| Frame rate | Cap options (30/60/120/uncapped) and VSync; never tie simulation to frame rate |
| HDR (Windows) | scRGB FP16 or HDR10 (PQ, Rec.2020) swapchain; user paper-white and peak calibration; tone-map UI separately |
| HDR (Mac) | EDR via `CAMetalLayer.wantsExtendedDynamicRangeContent`; query `NSScreen.maximumExtendedDynamicRangeColorComponentValue` |
| Distance | Text size must work at 60 cm (monitor), 3 m (TV, Steam Machine), and 30 cm on a 7-inch 1280x800 screen (Deck) |

### Store economics and SDKs (verify current terms)

- Steam revenue share 30%, dropping to 25% above $10M and 20% above $50M per app (long-standing tiers; verify). Epic Games Store 12%. Microsoft Store terms vary by product type; check current policy.
- Epic Online Services: free, cross-store account, achievements, lobbies and anti-cheat. Microsoft GDK targets PC Game Pass and Xbox services.
- Google Play Games on PC: GA Sept 23, 2025, opened to native PC games; native titles calling Play Billing must use the PC SDK. Source: https://developer.android.com/games/playgames/native-pc/migrate_api_sdk

## Diagnostics

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Achievements never unlock in builds launched outside Steam | No `steam_appid.txt` in dev, or `RestartAppIfNecessary` skipped | Launch via Steam in release; dev builds use `steam_appid.txt` |
| Achievements unlock locally, not on the profile | `StoreStats` never called, or called before stats were ready | Call `StoreStats` after changes; check `UserStatsStored_t` result |
| Callbacks never fire | `SteamAPI_RunCallbacks` not pumped, or pumped on a thread that blocks | Pump once per frame on the main loop thread |
| Deck review fails "input" | Mouse needed in launcher, login or a menu; wrong glyphs | Controller path through every screen; Steam Input glyph APIs |
| Text unreadable on Deck | Mobile UI scaled down from 1080p | UI scale based on physical size; minimum text size test at 1280x800 |
| Mac build "is damaged" or will not open | Not notarized, nested framework unsigned, or quarantine on unstapled build | Sign deepest-first, notarize, staple, `spctl -a -vv` |
| Steam overlay missing on Mac | Missing `disable-library-validation` / `allow-dyld-environment-variables` | Add both entitlements under hardened runtime |
| Saves lost or reverted across PC and mobile | Steam Cloud and backend both syncing the same file, or last-write-wins on clocks | One sync authority; versioned saves; server timestamps; conflict UI |
| HUD stretched or clipped on ultrawide | UI anchored to screen edges with 16:9 assumptions | Safe-region anchoring with max width; test 21:9 and 32:9 |
| Negative Steam reviews citing "mobile port" | Energy timers, ads, touch-sized UI, no rebinding | Port checklist: monetization rework, density pass, full rebinding |
| SmartScreen warns on first launch | Unsigned or newly signed executable without reputation | Authenticode signing on every build; consistent publisher identity |

## Anti-Patterns

**The Scaled-Up Phone** — shipping the mobile UI at 2x. Oversized buttons, empty space, hover-less interactions, and a review score that says "lazy port".

**Key-Bound Input** — gameplay code reading specific keys or buttons. Rebinding, Steam Input and Deck support all become rewrites.

**One Mac Binary for Every Store** — trying to satisfy both App Sandbox (Mac App Store) and Steam's unsandboxed overlay. Build two targets.

**Double Cloud** — Steam Auto-Cloud and the backend both owning the same save. Whichever syncs last silently destroys the other's progress.

**Mobile Economy, PC Audience** — energy timers and forced interstitials on Steam. Refunds within two hours and a review bomb follow.

**Deck Test at the End** — first Deck test after content lock. The fixes (text size, controller paths, keyboard) touch every screen.

**Client-Trusted Identity** — sending a Steam ID instead of an auth ticket the server verifies. Anyone can claim any account.

## Quality Checklist

- [ ] Store target matrix filled; each target builds in CI with its own SDK and entitlements
- [ ] Platform services behind an interface; non-Steam builds compile and run without Steam
- [ ] `SteamAPI_RunCallbacks` and `SteamInput()->RunFrame` pumped every frame; init failure handled gracefully
- [ ] Action-based input; KB/M and gamepad hot-switch glyphs; full rebinding; Steam Input action sets
- [ ] Borderless default; DPI aware; monitor hot-plug and resolution change survive; frame cap and VSync options
- [ ] UI verified at 16:9, 16:10, 21:9, 32:9 and at 1280x800 on Deck hardware
- [ ] Deck readiness sheet complete with evidence; Steam Machine 1080p/30 stable checked
- [ ] One save-sync authority; atomic writes; versioned saves; conflict resolution defined
- [ ] Mac: deepest-first signing, hardened runtime, Steam entitlements, notarized, stapled, `spctl` passes
- [ ] Windows executables Authenticode-signed
- [ ] Platform identities verified server-side (Steam auth ticket) and linked to the studio account
- [ ] Monetization reviewed for PC norms and platform payment rules
- [ ] Every store rule and hardware claim carries an as-of date and source

## Related Skills

Renderer ports and Game Porting Toolkit work go to `gamedev-metal-graphics-engineer`; the Mac's Swift-side services (GameKit, StoreKit for the Mac App Store, controllers) overlap with `gamedev-ios-engineer`. Account, identity linking and save services are designed in `gamedev-platform-server-architect` and built in `gamedev-backend-engineer`. UI density, scaling and glyph art: `gamedev-ui-designer` and `gamedev-hud-engineer`. Rebinding and subtitle standards: `gamedev-accessibility-specialist`. PC anti-cheat and auth-ticket abuse: `gamedev-anti-cheat-security`. Business model and PC pricing: `gamedev-monetization-designer` and `gamedev-financial-growth-strategist`. Depot uploads, branches and release checklists: `gamedev-delivery-release`. Hardware matrix testing: `gamedev-qa-verifier`. Google Play Games on PC overlaps with `gamedev-android-engineer`. Unity-specific build settings: `gamedev-unity-engineer`.
