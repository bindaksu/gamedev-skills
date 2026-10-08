---
name: gamedev-qa-verifier
description: >-
  QA and verification for mobile and cross-platform games: test strategy and
  pyramid, device matrix by market share and GPU family, regression suites,
  automation (AltTester, GameDriver, Appium, XCUITest, Espresso, Unity Test
  Framework, Airtest/Poco), soak, perf, battery and network tests, economy and
  IAP test cases, store certification and compliance, bug severity and
  priority, release exit criteria, and evidence-based verification of claimed
  fixes. Use when writing a test plan, picking test devices, automating a
  Unity game, preparing for App Store, Play or Steam Deck review, triaging
  bugs, or confirming that a fix actually works.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: meta
---

# Game QA Verifier

A claim is not a fix and a passing editor run is not a test. Game QA has to cover a combinatorial space nobody can test exhaustively (thousands of Android device models, GPU driver families, OS versions, network conditions, store sandboxes, live-ops configs that change without a build), so it is a risk-allocation discipline: put automated coverage where regressions are cheap to catch (logic, economy math, server contracts, smoke flows), put human and device time where only humans and devices find bugs (feel, readability, thermals, interruptions, store rules), and demand evidence for every "fixed". The money path deserves paranoia: a duplicated-currency bug or a lost purchase costs more trust than any crash. And because mobile releases cannot be rolled back, the exit criteria are the last gate that actually holds.

## Role Profile

At top-grossing studios the QA lead owns "QA planning, resourcing, standards, tooling, automation and quality strategy across gameplay, backend and live operations" and coordinates external QA partners (King, https://builtinlondon.uk/job/qa-lead-minecraft-blast/10599689 [proxy]). A King senior QA lead line-manages 10–15 QA specialists and writes end-of-testing reports (https://hitmarker.net/jobs/king-senior-qa-lead-882572 [proxy, closed]). Scopely asks QA to "own end-to-end quality strategy... high confidence releases"; Playtika builds a "multiplatform and multilayer framework" for Unity client automation plus client-server and API tests (https://www.skillshot.pl/jobs/34050-qa-automation-engineer-at-playtika-poland [proxy]).

- **Hard skills:** regression, exploratory and performance testing; Java/Python/C# automation; team leadership.
- **Tools:** Jira, TestRail, Appium, AltTester, Selenium, device farms.
- **KPIs:** "high confidence releases" [quoted, Scopely]; "balance between speed and quality" [quoted, King]; escaped defects and post-release crash rate [inferred].
- **Collaborators:** production, design, engineering, external QA vendors, LiveOps, release.

## When to Use / Not

Use for test strategy, device matrices, regression and automation plans, perf/soak/network testing, IAP and economy testing, certification prep, bug triage, release exit criteria, and verifying claimed fixes.

Not for: reading code or design for defects (gamedev-reviewer); setting perf budgets and device tiers themselves (gamedev-optimization-compatibility; QA tests against them); pipeline, submission and rollout mechanics (gamedev-delivery-release); exploit design and anti-tamper (gamedev-anti-cheat-security); playtest method for fun and comprehension (if installed, game-playtest-analyst).

## Inputs to Gather

- **Build under test:** version, build number, platform, commit, config version.
- **Change scope:** release notes, diff summary, new live-ops configs.
- **Target markets** with device share data (from analytics or store consoles). Default: top 10 geos by revenue.
- **Perf budgets and device tiers** from gamedev-optimization-compatibility. Default: 60 fps high tier, 30 fps low tier, low tier at 3–4 GB RAM.
- **Monetization surface:** SKUs, offers, randomized items, subscriptions, ads.
- **Release type:** client binary, server deploy, remote config, CDN content (each needs a different suite).
- **Known risks** from gamedev-reviewer findings and the producer's risk register.

## Method

1. **Map risk to test layers.** For each change, ask what breaks if it is wrong (money, progress, crash, perf, compliance, feel) and assign the cheapest layer that can catch it.
2. **Build or update the device matrix** from real install share (method below and references/device-matrix.md, read when constructing or refreshing the matrix).
3. **Pick suites by release type:** smoke for every build; targeted regression for the changed area; full regression before a client release; config regression for live-ops changes; IAP suite whenever SKUs, offers or billing code change.
4. **Automate the stable, repeated paths:** boot, login, FTUE, core loop, store open, purchase in sandbox, event entry. Keep exploratory and feel testing manual.
5. **Run non-functional tests on physical devices:** soak, thermal, battery, memory, network conditions. Editor and emulator numbers do not count for perf sign-off.
6. **Run store compliance checks** before submission (references/compliance-checklists.md, read before any store submission or Steam review).
7. **Triage bugs** with the severity and priority scales below; one owner per bug.
8. **Verify claimed fixes with evidence** (protocol below). Close only on evidence.
9. **Report against exit criteria** and give a clear go or no-go input to gamedev-delivery-release.

## Test Strategy Pyramid for Games

| Layer | What | Tools | Share of automated tests [heuristic] |
|---|---|---|---|
| Unit / logic | Economy formulas, reward tables, damage math, state machines, save serialization, deterministic sim | Unity Test Framework (EditMode, NUnit), XCTest, JUnit, server unit tests | 50–60% |
| Service / contract | API contracts, receipt validation, idempotency, config schema validation, old-client compatibility | Server test suites, contract tests, schema validators | 20–30% |
| Integration in engine | Scene loads, Addressables catalogs, PlayMode flows | Unity Test Framework (PlayMode) | 10–15% |
| Device UI / gameplay automation | Boot, login, FTUE, store, purchase, event entry on real devices | AltTester, GameDriver, Airtest/Poco, Appium, XCUITest, Espresso | 5–10% |
| Manual: exploratory, feel, compatibility, cert | What automation cannot judge | Device lab, checklists | Time-boxed per release |

Rule: if a bug escapes, add a test at the lowest layer that would have caught it.

### Regression suites

| Suite | Trigger | Scope | Duration [heuristic] | Devices |
|---|---|---|---|---|
| Smoke | Every build | Boot, login, FTUE step 1, core loop, store open, sandbox purchase | 15–30 min, automated | P0 subset |
| Targeted | Every change | Changed area plus neighbors from the diff | 0.5–2 h | P0 |
| Full | Every client release | All features, saves, interruptions, localization smoke | 1–3 days | P0 + P1 |
| Config | Every live-ops config publish | Event start/end, offers, kill switches, old-client parsing | 1–2 h, staging | P0 subset |
| IAP | Any SKU, offer, billing or grant change (code or config) | references/test-cases.md IAP and ECO sets | 2–4 h | iOS + Android P0 |

## Automation Frameworks

Versions change; verify current releases before adopting (as of 2026-10; verify).

| Framework | Sees | Best for | Limits |
|---|---|---|---|
| AltTester | Unity object hierarchy via an in-game SDK; works with Appium | Object-level Unity UI and gameplay tests on device | Requires instrumented build; strip from production |
| GameDriver | Unity and Unreal object hierarchy (commercial) | Cross-engine gameplay automation with an editor workflow | License cost; instrumented build |
| Airtest + Poco (NetEase, open source) | Image recognition (Airtest) plus UI hierarchy via Poco SDK for Unity, Cocos and others | Image-based smoke tests, mixed native and engine UI | Image matching is brittle across resolutions |
| Appium | Native accessibility tree, cross-platform | Native shells (login, store sheets, permission dialogs), device-farm orchestration | Cannot see inside an engine-rendered surface without AltTester/Poco |
| XCUITest | iOS native UI | System dialogs, StoreKit sheets, native screens | Same: engine surface is opaque |
| Espresso | Android native views in-process | Native Android shell screens | Engine surface opaque; use UI Automator for system UI |
| Unity Test Framework | EditMode and PlayMode tests in Unity | Logic, scenes, prefabs, Addressables in CI | Not a substitute for device tests |

## Device Matrix (construction)

1. Pull install share by device model, OS version, GPU family and RAM for your target geos (store consoles, analytics).
2. Cover the **top devices to roughly 70–80% of installs** for P0 [heuristic], then fill gaps by **GPU family** (Apple GPU, Qualcomm Adreno, Arm Mali, Imagination PowerVR, Samsung Xclipse), **RAM tier**, **OS version floor and newest**, **screen shape** (notch, punch-hole, tall, tablet, foldable).
3. Always include: your min-spec device; the most common low-RAM Android device in your top geo; the oldest supported iOS device; the newest OS beta; a device with 16 KB memory pages (Android 15+), since enforcement for updates starts Feb 1, 2027 (as of 2026-10; verify).
4. Tier: **P0** every release (8–12 devices), **P1** before client releases (20–30), **P2** cloud device farm sweep for crash-on-launch and rendering (100+). Refresh quarterly.

## Non-Functional Tests

| Test | Protocol [heuristic] | Pass |
|---|---|---|
| Soak | 2–4 h continuous core loop plus menu cycling, on low and mid tier | No crash; memory growth under 5% per hour after warm-up |
| Thermal | 30 min core loop at room temp, frame time logged | p90 frame time within budget after throttling |
| Battery | 30 min play at 50% brightness, sound on | Drain recorded per tier; flag regressions over 10% vs last release |
| Memory | Peak and steady-state per tier; background/foreground 20x | No OOM kill on low tier |
| Load / boot | Cold start to interactive, first launch and warm | Within budget set by gamedev-optimization-compatibility |
| Network | Profiles: high latency (300 ms), loss (3–5%), 3G-like bandwidth, offline, Wi-Fi to cellular handover | No soft-lock; purchases resolve; reconnect works |
| Interruptions | Call, notification, app switch, lock, low-battery dialog, permission prompt mid-flow | State restored, audio focus correct |
| Server load | Owned by gamedev-live-serving; QA verifies client behavior under server errors and throttling | Clear retry and error UX |

Network shaping: Network Link Conditioner on iOS and macOS, emulator or proxy throttling on Android.

## Economy and IAP Test Cases (core set)

Full list with steps: references/test-cases.md (read when testing purchases, refunds, currency or rewards).

- Purchase each SKU in sandbox (App Store sandbox or StoreKit testing configuration; Play license testers); currency or item granted exactly once.
- Interrupt mid-purchase (kill app after pay, before grant); relaunch; item granted exactly once.
- Ask to Buy / pending purchase (Play pending state): no grant until approved.
- Double-tap buy; rapid repeated purchase: no double charge or double grant.
- Refund: App Store refund notification and Play voided purchase processed; policy applied (revoke, negative balance, or flag).
- Restore purchases / reinstall: non-consumables and subscriptions restored; consumables not duplicated.
- Device clock manipulation: timers, daily rewards and event windows use server time.
- Offline then online: queued actions reconciled without duplicates.
- Randomized items: displayed odds match configured odds; pity counter increments and triggers at the stated count (simulate N draws on a test account).
- Price display: localized price strings from the store, not hard-coded.

## Deliverables

Test plan (one per release), device matrix sheet (references/device-matrix.md), bug reports, exit-criteria report, fix-verification records.

```
TEST PLAN: release 1.15.0     TYPE: client binary + config     OWNER: QA lead
SCOPE: changed areas (from release notes / diff), out of scope
RISKS: top 5 from gamedev-reviewer findings and the risk register, each mapped to a suite
SUITES: smoke (P0) | targeted regression: guild war, store | full regression (P0+P1) | IAP | config | perf/soak
DEVICES: P0 list, P1 list, farm sweep
AUTOMATION: suites automated (framework), manual charters (exploratory, feel, interruptions)
ENTRY: build passes smoke; symbols uploaded; staging configs published
EXIT: release exit criteria below
SCHEDULE: dates per suite; report to gamedev-delivery-release by go/no-go
```

## Bug Report Template

```
TITLE: [Area] Observable symptom on condition (e.g., [Store] Gems not granted after app killed during purchase)
BUILD: 1.14.0 (4123), commit abc123, config v87, server env: staging
DEVICE / OS: Samsung Galaxy A15, Android 15, 4 GB RAM, Mali GPU
FREQUENCY: 3/5 attempts
STEPS:
  1. ...
EXPECTED:
ACTUAL:
EVIDENCE: video, logs (client + server trace id), screenshot, crash id
SEVERITY: S1 | S2 | S3 | S4        PRIORITY: P0 | P1 | P2 | P3
SCOPE: devices/platforms affected, % of players exposed if known
WORKAROUND:
OWNER:
```

| Severity | Definition |
|---|---|
| S1 critical | Crash/hang on a common path, data or progress loss, money lost or duplicated, security hole, store-policy violation |
| S2 major | Feature broken without workaround, severe perf regression on a supported tier, wrong rewards |
| S3 minor | Defect with workaround or limited reach; visual issues that do not block understanding |
| S4 trivial | Cosmetic, typo |

Priority is the business decision: **P0** fix now / hotfix; **P1** fix before release; **P2** next release; **P3** backlog. Severity does not change with deadlines; priority may.

## Release Exit Criteria

```
[ ] 0 open S1; 0 open S2 without written waiver from the accountable owner
[ ] Smoke + full regression passed on P0 devices; P1 sweep passed for client releases
[ ] Crash-free sessions in internal/beta at or above target (e.g., 99.5%+ [heuristic]); no new top-10 crash
[ ] Perf within budget on min tier (device-measured): frame time, memory, boot
[ ] IAP suite passed in sandbox on both stores; refund path verified
[ ] Live-ops configs for the release window validated in staging
[ ] Old client vs new server and new client vs old server tested (N-2)
[ ] Store compliance checklist passed for each target store
[ ] Localization smoke for shipped languages (truncation, fonts, RTL)
[ ] All fixed bugs verified with evidence; reopened rate reviewed
[ ] Known issues list written for support and community
```

## Verification of Claimed Fixes

A fix is verified only with evidence. Required for closure:

1. **Build identity:** build number and commit containing the fix, plus config version.
2. **Original repro re-run:** the exact steps from the bug, same device class and OS, at least as many attempts as the original frequency implied (an intermittent 1-in-5 bug needs 10+ clean attempts [heuristic]).
3. **Before/after artifact:** video, log excerpt, crash dashboard trend, or test result for both the failing and the fixed build.
4. **Regression check:** the surrounding area (same screen, same service call) smoke-tested.
5. **Production evidence for crash fixes:** crash cluster rate drops in the released version over a meaningful session count, not just "not reproduced locally".

Statements like "should be fixed", "works on my machine" or "could not reproduce" are not evidence. "Could not reproduce" on the old build means the repro is wrong; fix the repro first.

## Quantitative Reference

| Item | Value |
|---|---|
| P0 device coverage | top devices to ~70–80% of installs [heuristic] |
| Matrix tiers | P0 8–12 devices; P1 20–30; P2 100+ farm [heuristic] |
| Soak | 2–4 h; memory growth under 5%/h after warm-up [heuristic] |
| Thermal | 30 min continuous play, p90 frame time within budget [heuristic] |
| Battery regression flag | over 10% worse than last release [heuristic] |
| Intermittent fix proof | 10+ clean attempts for a 1-in-5 repro [heuristic] |
| Crash-free sessions gate | 99.5%+ [heuristic] |
| Android vitals bad behavior | 1.09% crash, 0.47% ANR, 8% per device (2022 thresholds, possibly outdated; as of 2026-10; verify) |
| 16 KB page enforcement | updates blocked without support from Feb 1, 2027 (as of 2026-10; verify) |
| Play unacknowledged purchases | refunded after 3 days |

## Diagnostics

| Symptom | Likely cause | Fix |
|---|---|---|
| Bugs escape on low-end Android | Matrix built from team devices, not install share | Rebuild matrix from analytics; add RAM and GPU-family coverage |
| Automation flaky | Image matching, fixed sleeps, shared test accounts | Object-level selectors (AltTester/Poco), explicit waits, account per run |
| Purchase bugs found by players | IAP suite skipped on "config-only" releases | Run IAP suite whenever offers or SKUs change, config included |
| Reopened bugs | Closed on claims without evidence | Enforce the verification protocol |
| Perf passed in QA, complaints live | Editor or short-session tests | Device soak and thermal runs on min tier |
| Store rejection | Compliance checked late | Run checklists at alpha and before each submission |
| Live-ops event broke without a build | Config not in regression scope | Config regression and staging validation for every event |

## Anti-Patterns

**Editor Sign-Off** — performance or stability approved from editor runs.

**The Flagship Lab** — testing on the team's own new phones while players use 4 GB Android devices.

**Closed on Claim** — bugs closed because a developer said "fixed".

**Automate Everything** — automating feel and exploratory testing; brittle suites, missed fun-breaking bugs.

**Config Is Not Code** — live-ops configs skip QA; they change player experience as much as builds do.

**Sandbox Once** — IAP tested at launch and never again while offers change weekly.

**Severity Inflation** — everything S1, so nothing is.

## Quality Checklist

- [ ] Each change mapped to risk and test layer
- [ ] Device matrix derived from install share with GPU, RAM, OS and screen-shape coverage; min-spec and 16 KB-page devices included
- [ ] Suite selection matches release type (binary, server, config, CDN)
- [ ] Automation uses object-level selectors where possible; instrumentation stripped from production builds
- [ ] Soak, thermal, battery, memory and network tests on physical devices
- [ ] IAP and economy suite run whenever monetization or currency code/config changes
- [ ] Store compliance checklist run per target store
- [ ] Every bug has severity, priority, owner and evidence
- [ ] Every fix verified with build identity, re-run, before/after artifact and regression check
- [ ] Exit criteria report delivered to gamedev-delivery-release

## Related Skills

gamedev-reviewer finds defects by reading; this skill confirms them and their fixes at runtime. gamedev-optimization-compatibility sets the budgets and tiers tested here. gamedev-delivery-release consumes the exit-criteria report at go/no-go. gamedev-live-serving owns server load tests and incident verification in production. gamedev-anti-cheat-security supplies exploit test cases; gamedev-monetization-designer and game-economy-balancer (if installed) supply the expected values for economy tests. gamedev-accessibility-specialist and gamedev-localization-specialist supply their LQA and a11y checklists.
