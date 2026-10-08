---
name: gamedev-delivery-release
description: >-
  Delivery and release engineering for mobile and desktop games: CI/CD with
  fastlane, Gradle, GameCI, Unity Build Automation and Xcode Cloud, code
  signing and secrets, build numbering, store submission, App Store phased
  release vs Google Play staged rollout, choosing between hotfix, client
  patch, server fix and remote-config fix, force and soft update with minimum
  version gating, release trains, go/no-go and rollback realities. Use when
  setting up a game build pipeline, planning a release or rollout, a bad build
  is live and you need to decide how to fix it, defining a force-update
  policy, or running a go/no-go meeting.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: meta
---

# Game Delivery and Release

On mobile there is no rollback. Once a player auto-updates to a bad binary, that binary stays on their device until you ship a new one through store review, and a phased release or staged rollout only limits how many players get it next. Everything in game release engineering follows from that fact: keep binaries small in blast radius by putting risky behavior behind server-side switches, make every build reproducible and signed by machines rather than laptops, gate old clients with a minimum-version check you can raise in minutes, and ship on a train so that a missed feature waits for the next one instead of delaying everything. The release manager's real product is not the build; it is the confidence that any release can be contained within an hour of something going wrong.

## Role Profile

Release managers and build engineers at large mobile studios own Unity build workflows ("asset import, automated packaging, build scripts"), CI/CD, iOS release ("certificates, provisioning profiles, TestFlight, App Store submission"), Perforce streams during release windows, and "coordinate cert and submission schedule with Production", plus "pipelines for patches and dynamic content" (EA Apex Legends Mobile, https://hitmarker.net/jobs/electronic-arts-build-and-release-manager-apex-legends-mobile-645772 [proxy]; https://en.wizbii.com/company/ubisoft/job/release-and-build-specialist-unity [proxy]).

- **Tools:** Jenkins, TeamCity, GitHub Actions, fastlane, Perforce/Git, Gradle, Xcode, Unity Build Automation / Unreal BuildGraph, App Store Connect, Play Console.
- **KPIs [inferred]:** build time and success rate; on-schedule releases and store rejection count; hotfix turnaround.
- **Collaborators:** QA, production, client engineering, LiveOps (dynamic content), platform holders.

## When to Use / Not

Use for pipelines, signing, versioning, submission, rollout plans, fix-path decisions, update policy, release calendars and go/no-go.

Not for: test strategy and exit criteria content (gamedev-qa-verifier supplies the report this skill consumes); incident response, kill-switch operation and CDN serving at runtime (gamedev-live-serving); engine-specific build settings (gamedev-unity-engineer, gamedev-ios-engineer, gamedev-android-engineer); desktop notarization and Steam depots in depth (gamedev-desktop-engineer).

## Inputs to Gather

- **Engine and version**, platforms, VCS (Git or Perforce), current CI. Default: Unity 6.3 LTS, Git, GitHub Actions.
- **Release cadence** and live-ops calendar. Default: 2-week client train for a live game.
- **Backend compatibility window**: how many old client versions the server supports. Default: N-2.
- **Current adoption curve**: share of DAU on latest version by day after release.
- **Signing assets location** and who has access.
- **Store accounts** and roles; review timing history.

## Method

1. **Make builds reproducible.** Pin engine version, SDK versions and build images; build from a clean checkout on CI only. A laptop-built release is unauditable.
2. **Move signing to CI.** Certificates, profiles and keystores live in a secret store or encrypted repo; CI fetches them per run. Humans never hold the Android upload key on a laptop.
3. **Number every build automatically.** Marketing version (semver) set by the release branch; build number from a monotonic CI counter.
4. **Branch per release train.** Cut on schedule; only fixes merge into the release branch after cut, via cherry-pick from main.
5. **Gate on QA exit criteria** from gamedev-qa-verifier and open findings from gamedev-reviewer.
6. **Ship behind switches.** Every risky feature in the binary is off or percentage-gated by remote config; turning it on is a config change, not a release.
7. **Submit early.** Submit to review as soon as the release branch passes; use manual release or managed publishing to control the go-live moment.
8. **Roll out in stages** with explicit halt criteria (below) watched by a named person.
9. **Choose the fix path** with the decision tree when something breaks.
10. **Raise minimum version** only when you must, with soft update first.
11. **Close the release:** adoption report, incidents, rejection notes, retro.

## Deliverables

Pipeline definition (references/pipeline-snippets.md), release plan per train, go/no-go record, rollout log, fix-path decision record, update-policy table.

```
RELEASE PLAN: 1.15.0 (build 4123)   TRAIN: Oct 12–26   RELEASE MANAGER: ______
CONTENTS: features (flag key + default state), fixes, SDK/engine changes
COMPATIBILITY: server api=37 supports builds 3950+ (N-2); config cfg=87; save migration from 1.13
ROLLOUT: iOS phased release on, manual release Oct 19 10:00 UTC
         Android 5% Oct 19, 20% Oct 21, 50% Oct 23, 100% Oct 26 (if halt criteria clear)
HALT CRITERIA: crash-free -0.3 pts; new top-5 crash; purchase success -2 pts; login success drop; currency anomaly
WATCHER: name, hours covered          KILL SWITCHES: list of keys
UPDATE POLICY: soft prompt for < 1.14 on Oct 26; force for < 1.13 when under 3% DAU
BLACKOUTS / EVENTS IN WINDOW: ______
```

## CI/CD Pipeline

```
commit/PR ──► lint + unit tests (Unity Test Framework EditMode, server tests)
          ──► build dev (IL2CPP, development flag) ──► smoke on device farm
release branch ──► build release (signed) ──► upload symbols (dSYM / IL2CPP symbols.zip)
          ──► TestFlight + Play internal testing ──► QA regression ──► store submission
```

| Tool | Role | Notes |
|---|---|---|
| fastlane | iOS and Android lanes: signing (match), build (gym), TestFlight (pilot), metadata/submission (deliver), Play upload (supply) | Use an App Store Connect API key, not a personal Apple ID |
| Gradle | Android AAB build and signing config | Signing values from environment, never in the repo |
| GameCI | Open-source Unity builder/test runner for GitHub Actions, GitLab CI and others | Needs a Unity license activation step on CI |
| Unity Build Automation (formerly Unity Cloud Build) | Hosted Unity builds | Simple to start; less control over build machines |
| Xcode Cloud | Apple-hosted iOS/macOS builds and TestFlight | Fits native Swift games; Unity exports an Xcode project you can build there |
| Jenkins / TeamCity | Self-hosted orchestration | Common at large studios with Perforce |

Tool versions change quickly; verify current releases and license terms before adopting (as of 2026-10; verify). Pipeline snippets (GitHub Actions with GameCI, Fastfile lanes, Gradle signing): references/pipeline-snippets.md (read when building or fixing a pipeline).

Crash symbols are part of the release: Crashlytics needs IL2CPP symbols uploaded (`firebase crashlytics:symbols:upload --app=APP_ID path`); dSYM upload is auto-configured for Apple. A release without symbols is a release you cannot debug.

## Signing and Secrets

- **iOS:** distribution certificate and provisioning profiles in an encrypted store (fastlane match or a secret manager); App Store Connect API key (issuer id, key id, .p8) as CI secrets.
- **Android:** enroll in Play App Signing; Google holds the app signing key, you hold an upload key. Upload keystore and passwords in the secret manager. Losing the upload key is recoverable through Play support; losing a self-managed app signing key is not.
- **Never** commit keystores, .p8 files, certificates or passwords; scan the repo for them in CI.
- Rotate CI tokens; restrict who can trigger release lanes.

## Build Numbering

```
Marketing version:  MAJOR.MINOR.PATCH        1.14.0  (train = MINOR, hotfix = PATCH)
iOS CFBundleVersion: monotonic integer        4123    (CI run counter)
Android versionCode: monotonic integer        1014004123 style or CI counter; max 2100000000
Server compat key:   protocol/API version     api=37  (what min-version gating compares)
Config version:      monotonic per env        cfg=87
```

Rule: one build number maps to exactly one commit, one engine version and one signed artifact. Record all of them in the release notes.

## Rollout: App Store Phased Release vs Google Play Staged Rollout

| | App Store phased release | Google Play staged rollout |
|---|---|---|
| Schedule | Fixed 7 days: 1%, 2%, 5%, 10%, 20%, 50%, 100% | Any percentage you choose, raised manually |
| Who gets it | Only automatic updaters; anyone can update manually from the store immediately | Random cohort of users at the chosen percentage |
| Pause | Pause allowed, up to 30 days total | Halt stops new installs; resume uses the same cohort |
| Users already updated | Keep the build; no rollback | Keep the build; no rollback |
| Targeting | None | Country targeting for production updates; countries cannot be removed once started |
| First release | Available | Not available for the first publish |
| Go-live control | Manual release after approval | Managed publishing |

Sources: https://helm-app.com/guides/manage-phased-release/ [secondary]; https://support.google.com/googleplay/android-developer/answer/6346149 (as of 2026-10; verify).

Because manual updaters bypass the App Store schedule, the effective exposure on day 1 is higher than 1%. Treat phased release as a crash early-warning, not as containment; containment is the server-side kill switch.

**Halt criteria** (watch hourly for the first 48 h) [heuristic]: crash-free sessions drop more than 0.3 points vs previous version; a new crash cluster in the top 5; purchase success rate down more than 2 points; login success down; any currency anomaly. On halt: pause/halt, flip kill switches, choose fix path.

## Fix-Path Decision Tree

```
Problem found in live build
├─ Is it server logic or data? ──────────────► Server fix (deploy; minutes to hours)
├─ Can remote config or a kill switch neutralize it?
│     └─ yes ──► Config fix now (minutes), then client fix on the next train
├─ Is it content/data in downloadable bundles (Addressables, Background Assets, PAD)?
│     └─ yes ──► CDN content patch (new bundle version + catalog); old bundles stay cached
│                with versioned URLs (see gamedev-live-serving)
├─ Is it a crash/soft-lock/money-loss on a common path in the binary?
│     └─ yes ──► Hotfix binary: PATCH version from release branch, expedited review
│                request if justified, halt rollout meanwhile, consider min-version raise
└─ Otherwise ──► Fix on next release train
```

Executable code hot-update (Lua, JS, HybridCLR) is common in Asian markets but must respect Apple guidelines 2.5.2 and 4.7: downloaded code may not change the app's primary purpose (as of 2026-10; verify).

## Force and Soft Update Policy

- **Client sends** its build number and API version on every session start; the server returns `ok`, `soft_update` (dismissible prompt) or `force_update` (blocking screen with store link).
- **Soft first.** Prompt soft update for 1–2 weeks; force only when an old client is unsafe (exploit, money loss, protocol break) or below the support window.
- **Force-update threshold [heuristic]:** force when the old version is under 3–5% of DAU, unless a security or economy issue requires it immediately.
- **Phased-release interaction:** do not force-update to a version still in phased release; players not yet offered it cannot get it automatically.
- **Store check:** confirm the new version is live in every storefront before raising the minimum (regional review/propagation delays).
- **Fallback:** the force screen must work offline-safe and never trap a player who cannot update (OS too old): show a clear message.

## Release Train

```
Week 1 Mon  Feature cut for 1.15; release branch created
Week 1 Tue–Thu  QA regression on P0/P1 devices; fixes cherry-picked
Week 1 Fri  Go/no-go #1; submit to both stores (manual release / managed publishing)
Week 2 Mon  Approved; go/no-go #2; release; phased (iOS) + staged 5% (Android)
Week 2 Tue–Fri  Monitor; Android 5% → 20% → 50% → 100% if halt criteria clear
Week 2 Sun  1.16 feature cut (next train)
Blackouts: no releases 48 h before major events, store holiday shutdowns, or launch days of marketing beats
```

Two-week trains suit most live mobile games [heuristic]; weekly needs strong automation; monthly invites feature pile-ups.

## Go / No-Go Checklist (condensed)

Full checklist plus hotfix runbook and calendar template: references/release-checklists.md (read before every go/no-go and during any hotfix).

- [ ] QA exit criteria met (gamedev-qa-verifier report); no open blockers from gamedev-reviewer
- [ ] Build identity recorded: version, build number, commit, engine version, config version
- [ ] Symbols uploaded; crash reporting verified in the release build
- [ ] Server supports new client and N-2; new client tested against production-like server
- [ ] Remote config defaults safe; kill switches tested for every risky feature
- [ ] Store metadata, screenshots, privacy forms, age ratings current
- [ ] Platform requirements met: Play target API 36 (Aug 31, 2026, ext. Nov 1), PBL 8+, 16 KB pages for updates from Feb 1, 2027 (as of 2026-10; verify)
- [ ] Rollout plan with halt criteria and a named watcher for 48 h
- [ ] Support and community briefed; known-issues list ready
- [ ] On-call coverage confirmed with gamedev-live-serving

## Rollback Realities

- **Binary:** cannot roll back on either store; users who updated keep the version. Your options are halt, kill switch, server-side workaround, and a new hotfix build with a higher build number.
- **Server:** roll back freely only if the deploy was backward compatible; migrations need a down path or forward fix.
- **Config:** instant rollback if configs are versioned; keep the previous version one click away.
- **CDN content:** publish the previous bundle set under a new version; never overwrite a URL in place (caches will serve mixed content).

## Quantitative Reference

| Item | Value |
|---|---|
| App Store phased release | 7 days, 1/2/5/10/20/50/100%, auto-updaters only, pause up to 30 days total (as of 2026-10; verify) |
| Play staged rollout | any %, halt and resume same cohort, not for first publish |
| Play target API | API 36 for new apps and updates from Aug 31, 2026; extension to Nov 1, 2026 |
| Play Billing Library | v8+ required since Aug 31, 2026; v8 accepted until Aug 31, 2027 |
| 16 KB pages | updates without support blocked from Feb 1, 2027; AGP 8.5.1+ and NDK r28+ align by default |
| Android versionCode max | 2100000000 |
| Android vitals bad behavior | 1.09% crash, 0.47% ANR (2022 thresholds, possibly outdated) |
| Adoption heuristic | 50–70% of DAU on new version within 7 days for auto-update-heavy audiences [heuristic; measure yours] |

## Diagnostics

| Symptom | Likely cause | Fix |
|---|---|---|
| "Works on CI, fails on store build" | Different signing or build flags between lanes | One release lane; same flags; diff build logs |
| Crash reports unreadable | Symbols not uploaded | Make symbol upload a release-lane step that fails the build |
| Upload rejected for version | Build number not monotonic | CI-generated build numbers only |
| Hotfix takes 3 days | No release branch; main too far ahead | Branch per train; cherry-pick fixes |
| Force update locks out players | Min version raised before new version live everywhere | Check every storefront; soft prompt first |
| Bad build reached 30% of iOS users day 1 | Manual updaters bypass phased release | Kill switches on risky features; watch first hours |
| Signing breaks when one engineer leaves | Certificates on a laptop | Move to match or secret manager with team access |
| Store rejection late in train | Compliance checked after submission | Run compliance checklist at branch cut |

## Anti-Patterns

**Laptop Releases** — builds signed on a developer machine; irreproducible and a security risk.

**Phased Release as Rollback** — believing pausing undoes damage. It only stops new automatic updates.

**Feature Flags Off by Hope** — risky code shipped without a kill switch because "it's tested".

**The Feature-Waiting Train** — delaying a release for one feature; the train leaves on time.

**Force-Update First** — blocking players before a soft prompt and before the build is live everywhere.

**Overwrite-in-Place Content** — replacing a CDN file at the same URL; caches serve mixed versions.

**Secrets in the Repo** — keystores or .p8 keys committed "temporarily".

## Quality Checklist

- [ ] Builds are produced only by CI from pinned engine and SDK versions
- [ ] Signing material in a secret store; nothing in the repo; access limited
- [ ] Build numbers monotonic and mapped to commit, engine version and config version
- [ ] Symbols uploaded automatically for every release build
- [ ] Release branch per train; fixes cherry-picked; blackout dates on the calendar
- [ ] Rollout plan names halt criteria and a watcher; kill switches tested
- [ ] Fix-path decision recorded for every live issue
- [ ] Min-version gating with soft-then-force policy and storefront check
- [ ] Platform deadlines tracked with dates (as of 2026-10; verify)
- [ ] Go/no-go checklist completed and signed for every release

## Related Skills

gamedev-qa-verifier supplies exit criteria and verified-fix evidence. gamedev-reviewer supplies the open-finding list. gamedev-live-serving operates kill switches, remote config rollouts, CDN content and incidents after release. gamedev-producer owns the train calendar against the roadmap. Engine and platform build details: gamedev-unity-engineer, gamedev-ios-engineer, gamedev-android-engineer, gamedev-desktop-engineer. Server compatibility windows: gamedev-backend-engineer.
