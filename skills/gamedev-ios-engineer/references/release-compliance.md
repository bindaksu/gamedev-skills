# App Review and Platform Pre-flight for Games

Run before every submission. Dates and rule text are as of 2026-10; verify against https://developer.apple.com/app-store/review/guidelines/ before relying on them.

## Info.plist and capabilities

| Key / capability | Value | Why |
| --- | --- | --- |
| `CADisableMinimumFrameDurationOnPhone` | YES (if targeting 120 Hz on iPhone) | Without it iPhone ProMotion caps at 60 |
| `GCSupportsGameMode` | YES | Game Mode eligibility, iOS 18+ / macOS 14+ |
| `LSSupportsGameMode` | YES | Newer key, iOS/iPadOS/macOS 26+; set both |
| `LSApplicationCategoryType` | a games category | Required alongside Game Mode keys |
| `GCSupportsControllerUserInteraction` | YES if menus are controller-navigable | UIKit focus from controllers |
| Game Center capability | enabled | GameKit APIs |
| In-App Purchase capability | enabled | StoreKit |
| `NSUserTrackingUsageDescription` | present only if you call ATT | Missing string with an ATT call is a crash and a rejection |
| Privacy manifest | `PrivacyInfo.xcprivacy` for app and every third-party SDK | Required-reason API declarations |
| `UIApplicationSceneManifest` plus a scene delegate | present | Builds linked against the iOS 27 SDK crashed at launch on iOS 27 without the UIScene life cycle (observed on Xcode 27.2; as of 2026-11; verify) |
| `UIRequiresFullScreen` | YES on a landscape-only iPad build that lists fewer than four orientations | Upload validation rejects the build (ITMS-90474) without it, although iPadOS 26+ ignores the key at runtime (Apple TN3192; Xcode 27.2 also documents `UIRequiresFullScreenIgnoredStartingWithVersion`). Keep it for validation only; enforce landscape through the app delegate and `UIWindowScene` size restrictions |

### Resizable windows on iPadOS 26+ and Mac

- Games get no full-screen exemption: the scene resizes whatever the plist says. Pick a minimum supported window, test every screen at it, letterbox a landscape stage inside portrait or small windows, and pause below the minimum. Minimum-window sizes, UI-scale caps and layout rules: `gamedev-ui-designer`.
- An iPad app on a Mac resizes only with multitasking on: full screen off and all four iPad orientations listed.

## Guidelines that most often reject games

| Guideline | Requirement | Pre-flight check |
| --- | --- | --- |
| 3.1.1 | Randomized virtual items (loot boxes, gacha) must disclose odds of each item type before purchase | Odds visible on the purchase screen, before the buy button; also disclose for earned-currency boxes |
| 3.1.1 | Digital goods sold in-app use In-App Purchase (regional and court-ordered exceptions vary; check current text) | No external purchase links unless the current guideline text for that storefront allows it |
| 4.7 (rev. Nov 13, 2025) | HTML5/JS mini games, streaming games, plug-ins: developer responsible for content | 4.7.2 no native API exposure to non-embedded code; 4.7.5 age gate for content above app rating |
| 2.5.2 | Downloaded code may not change primary purpose or add features beyond review | Lua/JS hot updates limited to content and bug fixes |
| 5.1.1 | Account creation needs account deletion in-app | Delete-account path reachable from settings |
| 4.8 | Third-party login requires an equivalent privacy-focused option (Sign in with Apple qualifies) | Check if you offer Google/Facebook login |
| Game Mode keys | Non-games that set them risk rejection | Category matches the app |
| 2.3.7 | Screenshots and captions must not state prices | Before upload, OCR every localized screenshot for prices, currency symbols, "free" and "buy" words; review each hit by eye (an in-game coin glyph is fine); run the same banned-word check on the caption source |
| 2.3.4 | App Previews "may only use video screen captures of the app itself" (as of 2026-11; verify, https://developer.apple.com/app-store/review/guidelines/) | Generated or rendered footage goes to trailers and ads only |
| 1.3 Kids Category | Parental gate before any price, external link or purchase; no personal or device data to third parties and no third-party analytics (as of 2026-11; verify, same URL) | Full checklist in `gamedev-qa-verifier` compliance checklists |

A June 2026 guideline update reportedly expanded child-safety requirements; it was seen only via a tracker. Read the current Apple page.

## StoreKit configuration

- [ ] Every product exists in App Store Connect with review screenshot and localized display name
- [ ] StoreKit configuration file in Xcode mirrors the catalog for local testing
- [ ] Sandbox purchase, Ask to Buy (pending), refund, and interrupted purchase tested
- [ ] Restore button present for non-consumables and subscriptions
- [ ] Server rejects Sandbox transactions in Production environment

## Lifecycle and interruption tests (device, not simulator)

- [ ] Incoming call mid-level: game pauses, audio stops, resumes to a pause menu
- [ ] Background for 10 minutes, return: no huge simulation jump, network reconnects
- [ ] Low Power Mode on: frame cap honored, no thermal spiral
- [ ] Controller disconnect mid-match: game pauses, virtual controller appears if configured
- [ ] Airplane mode at launch: game boots, Game Center fails gracefully, store shows offline state
- [ ] Storage nearly full: Background Assets download failure handled with a retry

## Content delivery

- [ ] Binary under your cellular-download target; post-install content in Background Assets packs
- [ ] Essential pack set is the minimum for first session
- [ ] Pack versions can update without a binary; client tolerates an older pack for one release

## Release

- [ ] Phased release on (7 days: 1, 2, 5, 10, 20, 50, 100%); it affects automatic updaters only and does not roll back users who already updated
- [ ] Server-side kill switch for every new risky feature, because phased release cannot undo an install
- [ ] dSYMs uploaded to the crash reporter
- [ ] Exact signed build launched on the newest OS on device; `DTSDKName` and `DTXcodeBuild` compared with the last shipped build
- [ ] Pricing and Availability checked before submit (China mainland needs a game approval number; see `gamedev-delivery-release`)
- [ ] Evaluation builds (for example for publishers) are a separate no-purchase flavor that can never be attached to a store version (`gamedev-delivery-release`)

## Apple Arcade builds

- [ ] Release scan of code, entitlements and linked frameworks finds no StoreKit, In-App Purchase or ad SDK
- [ ] Every Apple device class planned: iPhone, iPad, iPad app on Mac, Vision Pro compatibility
- [ ] Every offered locale complete; Game Center and iCloud saves working
- [ ] Products created earlier left unsubmitted, never deleted (a deleted product ID cannot be reused)
- [ ] Game Center vendor IDs use only letters, digits, `_` and `.`; app-side IDs mapped explicitly
