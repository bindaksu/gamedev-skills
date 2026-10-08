---
name: gamedev-anti-cheat-security
description: >-
  Defend a mobile or PC game against cheating, fraud and account abuse: threat model,
  server authority as the primary control, Play Integrity and App Attest/DeviceCheck
  as risk signals, root and jailbreak realities, memory editing, speed hacks and packet
  tampering, receipt fraud and refund abuse, bot and farm detection from telemetry,
  ban and appeal systems with shadow bans and delayed waves, account security and
  privacy limits. Use when leaderboards fill with impossible scores, a dupe or fake
  purchase is reported, bots farm an event, or a team asks how to add attestation or
  design bans. Defensive only.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: backend
---

# Game Anti-Cheat & Security

The client is in the attacker's hands, so the client cannot be the referee. Every mobile anti-cheat program that works rests on one control — **the server decides every outcome that has value** — and treats everything else (attestation, root detection, obfuscation, telemetry models) as cost-raising and risk-scoring around it. Detection is an economic game: you win when cheating costs more than it pays and when cheaters cannot tell which signal caught them. That is why enforcement is delayed and batched, why verdicts drive restrictions rather than hard blocks, and why every ban must be explainable to a human reviewer and reversible when you are wrong. This skill is defensive; it describes attack classes only at the level needed to design controls.

## Role Profile

At top studios this splits into anti-cheat engineering and application security. Tencent hires for overseas anti-cheat on PC and mobile; Krafton's mobile role covers root/jailbreak detection, integrity verification and obfuscation in live games; Supercell's AppSec engineers work with game teams to close security gaps, with anti-reverse-engineering only a nice-to-have — a signal that server authority carries the load.

- **Responsibilities:** threat models per feature, integrity attestation integration, detection rules and models, ban pipeline and ban waves, appeal tooling, fraud/refund abuse, account takeover defense, security reviews of APIs.
- **Hard skills:** C/C++, ARM/x86 assembly, Android NDK/JNI, Mach-O/ELF, reverse-engineering tools (IDA, Ghidra, Frida, LLDB) for analysis of cheats found in the wild; Python; server-side validation and anomaly detection with data science.
- **KPIs (inferred):** detection rate, time-to-detect a new cheat, false-positive rate (appeal overturn rate), fraud loss as % of revenue.
- **Collaborators:** backend (server authority), data science (models), community/support (appeals), legal/privacy.
- Sources: https://hitmarker.net/jobs/tencent-senior-game-anti-cheat-engineer-978946, https://job-boards.greenhouse.io/kraftonamericas/jobs/8645891002, https://supercell.com/en/careers/application-security-engineer/2189023

## When to Use / Not

Use for: threat modeling, attestation design, detection rules, enforcement ladders, ban waves, appeals, purchase fraud and refund abuse policy, account security, privacy review of anti-cheat telemetry.

Not for:
- Building the ledger, idempotency, receipt verification code → `gamedev-backend-engineer` (this skill sets the requirements).
- Netcode authority model, lag compensation → `gamedev-netcode-engineer`.
- PvP fairness, toxicity and report UX → `gamedev-pvp-designer`.
- DDoS capacity and network infrastructure → `gamedev-infrastructure-engineer`.
- Telemetry pipeline and event schema → `gamedev-analytics-engineer`.

## Inputs to Gather

- Genre and what has value: currencies, ranked ladders, leaderboards with prizes, tradeable items, real-money tournaments. Default: currency + ranked + event leaderboards.
- Authority map: which outcomes the server computes vs accepts from the client. This is the first thing to audit.
- Platforms and minimum OS: attestation coverage depends on them.
- Current loss data: refund rate by country/payment method, chargebacks, top-leaderboard anomalies, support tickets about cheaters.
- Telemetry already collected and its privacy basis (consent, legitimate interest, retention).
- Enforcement owner and appeal capacity (support headcount). Default: appeals answered within 7 days.

## Method

1. **Map assets and attackers** (Deliverable 1). Rank threats by `value to attacker × ease × reach`. A leaderboard with cash prizes and a client-reported score is a top threat; a cosmetic-only offline mode is not.
2. **Move authority to the server** for every ranked threat. The client sends inputs and intents; the server computes rewards, validates results, and owns timers. For single-player puzzle/level results, send the move list and validate or re-simulate server-side (deterministic simulation makes this cheap). Where full validation is too expensive, bound it: plausibility limits per level, per minute, per session.
3. **Use server time** for every cooldown, energy timer and event window. Device clocks are attacker-controlled; speed hacks and clock changes then do nothing to the economy.
4. **Harden the transport**: TLS everywhere, request signing with a per-session key, replay protection (nonce + timestamp window), idempotency on writes. Certificate pinning raises cost but is not a control — assume traffic is readable.
5. **Add attestation as a risk signal** (Technical Reference; read `references/attestation-server-checks.md` when implementing). Gate sensitive actions (purchase verify, ranked entry, reward claims, account linking) on fresh verdicts; map verdicts to graduated responses, not to a hard block.
6. **Build detection** (read `references/detection-and-enforcement.md` for rule catalog and schema): deterministic rules first (impossible values, rate limits), then statistical outliers per cohort, then account-graph clustering for farms, then models. Every detection writes evidence.
7. **Design the enforcement ladder and ban waves** (Deliverable 3): restrict silently, batch bans on a cadence, roll back ill-gotten gains through the ledger, keep evidence for appeals.
8. **Close purchase fraud**: server-side verification only, binding purchases to the player, refund/voided-purchase handling with clawback, repeat-refunder thresholds, sandbox-on-production detection.
9. **Protect accounts**: credential stuffing defenses, session revocation, step-up for linking/recovery, support verification scripts.
10. **Run the privacy review** before shipping telemetry or automated bans (Technical Reference).

## Deliverables

### 1. Threat model sheet

```
ASSET              | THREAT CLASS              | ATTACKER         | VALUE | EASE | REACH | CURRENT CONTROL         | GAP / ACTION
currency balance   | client-side value edit    | casual cheater   | H     | H    | H     | server ledger           | none if no client-reported amounts remain
level result       | forged result / speed     | casual + tools   | H     | M    | H     | none                    | move list + server validation
ranked match       | aim/wallhack, packet edit | dedicated cheater| H     | M    | M     | server authority        | stats outliers, report pipeline
event leaderboard  | score injection           | scripted         | H     | M    | M     | rate limits             | plausibility + top-N review before payout
store              | fake/replayed receipts    | fraud ring       | H     | M    | H     | server verify           | binding check, sandbox-on-prod alert
store              | refund abuse              | players          | M     | H    | H     | none                    | voided-purchase clawback + threshold
accounts           | credential stuffing / ATO | fraud ring       | H     | M    | M     | rate limits             | breached-password check, step-up, alerts
economy            | race-condition dupes      | scripted         | H     | L    | H     | idempotency             | concurrency tests on every write path
event rewards      | bot/emulator farms        | farm operators   | M     | M    | H     | none                    | device/IP/graph clustering, attestation gate
```

### 2. Verdict-to-action policy

```
SIGNAL                                     | ACTION
Play Integrity: app not PLAY_RECOGNIZED    | block purchases + ranked; allow casual play; flag
Play Integrity: no MEETS_DEVICE_INTEGRITY  | allow play; exclude from prize leaderboards; raise risk score
Play Integrity: no MEETS_BASIC_INTEGRITY   | restrict economy-affecting actions; review if combined with anomalies
App Attest: attestation/assertion invalid  | treat as untrusted client: same as "not recognized"
App Attest: unsupported device             | no penalty; rely on server validation (do not punish old hardware)
Fraud risk metric high (many keys/device)  | add to risk score; never sole reason for a ban
Verdict unavailable (API error/timeout)    | fail open for play, fail closed only for high-value actions; retry
```

### 3. Enforcement ladder

```
LEVEL | NAME                 | EFFECT                                            | TRIGGER                       | VISIBLE TO PLAYER
0     | flag                 | risk score up, evidence logged                    | any single weak signal        | no
1     | shadow restriction   | excluded from prize boards, matched in a separate pool, trade/gift disabled | strong signal or repeated weak | no
2     | rollback             | ledger reversal of gains from the offending window| confirmed exploit             | yes (notice)
3     | temporary suspension | 1–14 days                                         | confirmed, first offense      | yes, with appeal link
4     | permanent ban        | account (and device bit, if policy allows)        | confirmed repeat / commercial cheating, fraud | yes, with appeal link
```

### 4. Ban wave record

```
WAVE ID / DATE:
DETECTION(S):        [rule ids + versions]
ACCOUNTS:            [count by level]   EVIDENCE STORED: [where, retention]
FALSE-POSITIVE CHECK:[sample size reviewed by human, overturn rate in sample]
ROLLBACK TOTALS:     [currency/items reversed]
COMMS:               [notice text, community post y/n]
APPEALS OPENED/OVERTURNED (D+14):
```

## Technical Reference

### Attestation facts (as of 2026-10; verify)

- **Play Integrity API:** use **standard requests** (cached, a few hundred ms, replay protection built in) per sensitive action; verify server-side via Google's decrypt endpoint. From May 2025 the device verdict on Android 13+ requires hardware-backed signals (key attestation + verified boot); optional `MEETS_STRONG_INTEGRITY` adds a security-patch recency check. SafetyNet Attestation is gone. https://developer.android.com/google/play/integrity/improvements
- **App Attest** (`DCAppAttestService`): a Secure Enclave key attests the app instance; **your server validates** the attestation (Apple provides no verify endpoint for the attestation object); use assertions with per-request counters. https://developer.apple.com/documentation/devicecheck/assessing-fraud-risk
- **Fraud risk metric:** server sends the attestation receipt to Apple and gets an approximate 30-day count of attested keys on the device — fold into risk scoring, do not hard-block (WWDC26 session 201: https://developer.apple.com/videos/play/wwdc2026/201).
- **DeviceCheck:** two per-device bits that persist across reinstall (e.g., "promo claimed", "flagged").
- A device verdict is a risk signal; keep game logic server-authoritative (research note on Play Integrity).

### Root and jailbreak realities

- Detection is an arms race; root-hiding tools defeat client checks routinely. Hardware-backed Play Integrity verdicts are much harder to spoof than client-side checks, which is why they matter more than any in-app root detector.
- Legitimate players root, use custom ROMs, emulators (and Google Play Games on PC). Blocking them outright costs revenue and reviews; restrict competitive and economic surfaces instead.
- Client obfuscation (IL2CPP metadata protection, string encryption, symbol stripping) buys time against casual tooling; budget it as cost-raising, never as a control.

### Attack classes and server-side controls

| Class | Defensive control |
| --- | --- |
| Memory editing of values | No value of consequence lives only on the client; server recomputes; client values are display-only |
| Speed hacks / clock manipulation | Server time for timers; server-side rate bounds (actions per second, level completion time minimums); in real-time games server tick authority |
| Packet tampering / replay | TLS, request signing, nonce + timestamp window, idempotency keys, schema validation, server-side plausibility |
| Modified / repackaged client | Play Integrity app recognition, App Attest, version gating; restrict economy/ranked for unrecognized apps |
| Real-time PvP aim/visibility cheats | Server authority, do not send hidden enemy state to clients (interest management), statistical outliers, replay review |
| Receipt fraud | Server verification (App Store Server API JWS / Play Developer API), purchase binding (`appAccountToken` / `obfuscatedAccountId`), uniqueness on store transaction id, sandbox-on-production alerts |
| Refund abuse | Clawback via ledger on REFUND / voided purchases, repeat-refunder thresholds, debt wallets |
| Race-condition dupes | Idempotency and conditional updates on every write path; concurrency tests in CI |
| Bots and farms | Telemetry features + account graph clustering; attestation gates on reward claims; per-device/IP/payment account caps |
| Account takeover | Breached-password screening, login rate limits, new-device step-up, session revocation, alerting on linking changes |

### Privacy limits

- **Data minimization:** collect what detection needs; set retention (e.g., raw input telemetry 30–90 days, evidence for enforced cases for the appeal window plus legal hold).
- **Automated decisions:** under GDPR Art. 22, decisions based solely on automated processing with significant effects need safeguards including the right to human intervention — permanent bans should have human review or a human appeal path.
- **Transparency:** describe anti-cheat processing in the privacy policy and ToS; document lawful basis (usually legitimate interest for fraud prevention — confirm with counsel).
- **Platform rules:** Google Play restricts broad installed-app visibility (`QUERY_ALL_PACKAGES`); do not scan the device for "cheat apps" beyond policy. No kernel-level anti-cheat exists or is permitted on mobile.
- **Minors:** stricter limits on profiling; coordinate with the age gate.
- Device bits and hashed device IDs are still personal data in the EU when linkable to an account.

## Diagnostics

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Impossible scores on event leaderboard | Client-reported score accepted | Move list + server validation; plausibility bounds; hold top-N payouts for review |
| Currency appears with no matching ledger source | Write path outside the ledger, or a dupe race | Audit query by source; idempotency + conditional updates; close the side door |
| Cheaters return days after bans | Ban on account only; free account creation | Device bit (DeviceCheck), hardware-backed verdict linkage, cluster by payment/device; raise cost of new accounts for ranked (level gate) |
| Cheat devs adapt within hours of bans | Immediate, per-detection bans reveal the signal | Shadow restrictions + weekly ban waves; rotate detections |
| Appeal overturn rate above 10% | Rule thresholds too aggressive, or no human review | Tighten rules, add human sampling before waves, track precision per rule |
| Refund rate spikes in one country or payment method | Refund abuse ring or friendly fraud | Clawback, thresholds per account, report to store partner team, adjust offers |
| Event rewards drained by thousands of fresh accounts | Farms on emulators | Attestation gate on claims, account-age/level gate, graph clustering on device/IP/gift flows |
| Legit players locked out after attestation rollout | Hard-blocking on verdict | Verdict-to-action policy: restrict, do not block; monitor verdict distribution by device |

## Anti-Patterns

**The Client Referee** — trusting client-computed results because "it is a single-player level". The leaderboard and the economy are multiplayer.

**The Attestation Wall** — hard-blocking every non-perfect verdict. You lose real players on old or custom devices and cheaters adapt anyway.

**The Instant Ban** — banning the moment a rule fires. You teach cheat makers exactly which change got caught.

**The Unappealable Ban** — no evidence stored and no human path. One false-positive wave becomes a community crisis and a GDPR complaint.

**The Ban Without Rollback** — removing the cheater but leaving their gains in the economy and on the leaderboard.

**The Obfuscation Strategy** — investing in client hardening instead of server authority. Hardening buys weeks; authority buys the game.

**The Surveillance Creep** — collecting device inventories and personal data "for anti-cheat" without a retention or legal basis.

**The Receipt Cache** — validating a purchase once and never hearing about the refund.

## Quality Checklist

- [ ] Threat model ranked by value × ease × reach; top threats have an owner and an action
- [ ] Every outcome of value is computed or validated server-side; client values display-only
- [ ] All timers and event windows use server time
- [ ] Requests signed, replay-protected, idempotent on writes
- [ ] Play Integrity standard requests and App Attest assertions verified server-side on sensitive actions
- [ ] Verdict-to-action policy graduated; unsupported devices not punished
- [ ] Purchase binding to player verified; store transaction id unique; refund clawback live
- [ ] Detection rules versioned, each with measured precision; evidence stored per enforcement
- [ ] Shadow restrictions and batched ban waves; human sample review before each wave
- [ ] Ledger rollback used for confirmed exploit gains; leaderboards recomputed
- [ ] Appeal path with SLA; overturn rate tracked per rule
- [ ] Account security: breached-password screening, rate limits, step-up for linking/recovery
- [ ] Privacy review done: data minimized, retention set, Art. 22 human review for permanent bans, policy disclosure

## Related Skills

- `gamedev-backend-engineer` — implements ledger, idempotency, receipt verification and clawback that these controls require.
- `gamedev-platform-server-architect` — authority and consistency per domain; escalate any client-authoritative design.
- `gamedev-netcode-engineer` — server authority, interest management and lag compensation in real-time modes.
- `gamedev-analytics-engineer` — telemetry features for detection; `gamedev-pvp-designer` — report UX, ranked integrity, matchmaking pools for restricted accounts.
- `gamedev-ios-engineer` / `gamedev-android-engineer` — client integration of App Attest and Play Integrity.
- `gamedev-monetization-designer` — refund policy and offer design that limits abuse value.
- `gamedev-live-serving` — ban-wave scheduling, player comms, incident handling for exploits.
- `gamedev-infrastructure-engineer` — DDoS protection, network hardening, secrets.
