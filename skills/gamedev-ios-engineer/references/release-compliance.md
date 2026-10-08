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
