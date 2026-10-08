# Store Compliance and Certification Checklists

Read before any store submission or Steam review. Policies change; every line is (as of 2026-10; verify) against the live policy page. Authoritative App Store text: https://developer.apple.com/app-store/review/guidelines/

## Apple App Store

- [ ] **3.1.1 loot boxes:** apps offering loot boxes or other randomized virtual items for purchase disclose the odds of receiving each type of item before purchase. Disclose for earned-currency boxes too; applicability there is ambiguous (https://www.fenwick.com/insights/publications/apple-now-requires-disclosure-of-loot-box-odds).
- [ ] **3.1.1 IAP:** digital goods and currency unlocked through Apple IAP in apps where required; no external purchase links or buttons except where a region-specific entitlement or ruling allows (verify per storefront).
- [ ] Restore purchases available for non-consumables and subscriptions.
- [ ] Subscription terms, price, period and cancellation shown before purchase.
- [ ] **4.7** (revised Nov 13, 2025): HTML5/JS mini games, streaming games and plug-ins; developer is responsible for that content; 4.7.2 no exposing native APIs to non-embedded code without permission; 4.7.5 age restriction for content above the app's rating (https://dev.to/arshtechpro/apples-guideline-47-update-what-every-developer-hosting-html5-mini-apps-must-know-90).
- [ ] **2.5.2 / 4.7:** downloaded code must not change the app's primary purpose (relevant to Lua, JS or HybridCLR hot-update).
- [ ] Age rating questionnaire answered for randomized purchases, user-generated content and chat.
- [ ] Account deletion available in-app if account creation is offered.
- [ ] Sign in with Apple offered where other third-party social logins are offered (check current exemptions).
- [ ] Privacy nutrition labels match SDKs; ATT prompt shown before tracking; privacy manifest for required-reason APIs and third-party SDKs.
- [ ] Review notes include a demo account and instructions to reach gated content; any server-side features enabled for review.
- [ ] A June 2026 update reportedly expanded child-safety requirements; confirm on Apple's page (https://conductatlas.com/change/2026-06-09-apple-apple-app-store-review-guidelines-2759/ [secondary]).

## Google Play

- [ ] **Target API:** new apps and updates target Android 16 (API 36) from Aug 31, 2026; extension to Nov 1, 2026 on request (https://developer.android.com/google/play/requirements/target-sdk).
- [ ] **Play Billing Library 8+** for new apps and updates since Aug 31, 2026 (extension to Nov 1, 2026); Play Console reads the version from the merged-manifest entry `com.google.android.play.billingclient.version` (https://developer.android.com/google/play/billing/deprecation-faq).
- [ ] **16 KB page size:** all native libraries (including ad, physics and audio SDKs) aligned; updates without support blocked from Feb 1, 2027. Verify with `zipalign -v -c -P 16 4 app.apk` and `llvm-objdump -p lib.so | grep LOAD` (expect `2**14`) (https://developer.android.com/guide/practices/page-sizes).
- [ ] **Large screens:** manifest declares `android:appCategory="game"` to keep orientation/aspect behavior on sw600dp+ (Unity: App Category player setting) (https://developer.android.com/develop/adaptive-apps/guides/app-orientation-aspect-ratio-resizability).
- [ ] **Android vitals:** user-perceived crash rate under 1.09%, ANR under 0.47%, per-device under 8% (2022 thresholds, possibly outdated) (https://android-developers.googleblog.com/2022/10/raising-bar-on-technical-quality-on-google-play.html).
- [ ] Loot box odds disclosed (Play payments policy requires disclosure of odds for randomized purchasable items; verify current wording).
- [ ] Data safety form matches SDK behavior; families policy if targeting children; account deletion path and web link.
- [ ] Play Asset Delivery limits respected: base module 200 MB, asset pack 1.5 GB each, install-time total 4 GB, max 100 packs (https://support.google.com/googleplay/android-developer/answer/9859372#size_limits).
- [ ] Play Integrity used per sensitive action, verified server-side (https://developer.android.com/google/play/integrity/improvements).

## Steam / desktop

- [ ] **Steam Deck Verified:** text legible at 1280x800/720, controller-first defaults with correct glyphs, no launcher problems, on-screen keyboard where text entry is required.
- [ ] **Steam Machine Verified** (if targeted): native 1080p at a stable 30 fps, full controller support, good default settings (https://heise.de/-11208466 [secondary]).
- [ ] macOS: 64-bit, notarized, hardened runtime; Steam overlay entitlements `com.apple.security.cs.disable-library-validation` and `com.apple.security.cs.allow-dyld-environment-variables`; App Sandbox off (incompatible with Steam) (https://partner.steamgames.com/doc/store/application/platforms).
- [ ] Steam Cloud saves conflict handling tested; achievements unlock correctly.

## Cross-store

- [ ] Age ratings consistent (IARC questionnaire on Play; Apple's questionnaire).
- [ ] Regional rules: loot-box restrictions or bans in specific markets checked with gamedev-monetization-designer.
- [ ] Localized store listings and in-game legal text (terms, privacy, odds pages) for each language.
