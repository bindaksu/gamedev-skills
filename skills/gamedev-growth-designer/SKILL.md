---
name: gamedev-growth-designer
description: >-
  Design the retention and organic-growth layer of a free-to-play game: the
  D1/D7/D30 lever map, habit loops, streaks with forgiveness, appointment
  timers, guild and social loops, referral and viral mechanics with k-factor
  math, notification strategy with caps, and win-back flows. Use when D7 or D30
  is below target, when asked how to make players come back tomorrow, when
  designing daily login, streaks, push notifications or a referral program,
  when planning a returning-player flow, or when building a prioritized
  retention experiment backlog.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: growth-business
---

# Growth Designer

Retention is not a feature. It is the count of unresolved reasons a player has to open the game again, and each horizon runs on a different reason. D1 is earned by the first session's promise (did the player see where this goes and want it). D7 is earned by habit and visible goals (is there a thing due tomorrow, and a thing I am three days from). D30 is earned by investment, other people and live content (what do I lose, and who notices, if I stop). Most retention work fails because it applies a D30 lever to a D1 problem — a guild system cannot rescue a player who quit in minute four. Find the horizon that leaks, pull only the levers that act on it, and measure every one against a holdout. Social loops are the only levers that compound; everything else decays with novelty.

## Role Profile

At a top-grossing studio this is the growth or retention product manager, sometimes titled "PM, LiveOps & Monetization" (Supercell) or folded into a generalist "Product Specialist / PM, Games" role (Dream Games, Peak) that owns design, data and A/B together.

- **Responsibilities.** Own a slice of the live game end to end: set roadmaps and goals that feed game-level targets, "design, run and analyze A/B tests and multivariate experiments", and report from high-level KPIs down to initiative deep dives (https://hitmarker.net/jobs/supercell-senior-product-manager-live-ops-monetization-hay-day-2311776). Write PRDs, define tests and run post-launch analysis (https://swooped.co/job-postings/product-manager-herzliya-playtika-ltd-29389).
- **Bar.** 5–6+ years of live F2P PM; a "hypothesis based analytical approach" (Zynga); daily AI-tool use is now an explicit ask at Supercell and Playtika.
- **Tools.** SQL, an A/B platform, BI (Looker/Tableau), product analytics (Amplitude), remote config. Century Games reports over 60% of staff — PMs, designers, live operators, UA — use ThinkingData to monitor friction and ship zero-code live fixes (https://naavik.co/digest/century-games-4x-portfolio-strategy/).
- **KPIs.** D1/D7/D30 retention (quoted in Zynga postings as "player engagement and retention"), sessions per DAU, DAU/MAU stickiness, experiment win rate and cumulative lift.
- **Context.** King tests new ideas inside live games first because they reach tens of millions of players on day one — the live game is the lab. Collaborators: LiveOps, design, UX, data/BI, UA/marketing, engineering.

## When to Use / Not

Use for: diagnosing which retention horizon leaks and choosing levers; daily-return mechanics (login calendars, streaks, timers, dailies); social, guild, referral and viral loops; notification and re-engagement strategy; win-back; the experiment backlog.

Not for: reading a cohort curve or fitting it (if installed, `game-playtest-analyst`); the FTUE screen flow itself (`gamedev-ux-designer`, touch specifics in `mobile-game-ux-designer`); event calendars and pass structure (`gamedev-liveops-designer`); offers and pricing (`gamedev-monetization-designer`); LTV, CPI and paid UA (`gamedev-financial-growth-strategist`); experiment statistics and event schemas (`gamedev-analytics-engineer`); the core loop itself (if installed, `core-loop-designer`).

## Inputs to Gather

- **Cohort curve** D1, D3, D7, D14, D30 by install week, platform and country tier. Missing: assume the genre median and say so; never design against the all-genre average.
- **Session shape:** sessions/DAU/day and P50 session length. Missing: assume 2–3 sessions and 8–12 min for casual, 3–5 and 15–25 min for mid-core.
- **Where in progression players stop** (level or chapter of last session for churned users). This decides FTUE vs content-exhaustion.
- **Existing return mechanics:** timers, dailies, energy, streaks, login rewards, guilds, chat, friends, push.
- **Push opt-in rate** per platform and how the prompt is timed.
- **Install volume per day** — decides which tests are affordable (a 2pp D7 test needs thousands per arm).
- **Genre and audience** — older casual audiences respond to routine and collection; mid-core to competition and guilds.
- **Constraints:** server support for social, moderation capacity, minors in audience (limits chat, referral rewards and push timing).

## Method

1. **Locate the leaking horizon before choosing a lever.** Compute three ratios: D1 (first-session promise), D7/D1 (habit formation) and D30/D7 (long-term investment). Compare each with the genre band below. Fix the earliest horizon that is out of band first — later horizons inherit its losses, so a D1 fix lifts D30 for free and the reverse is never true.
2. **Split by progression, not calendar.** Plot churn by the last level or chapter reached. A spike at one node is a content or difficulty wall (send to the level or economy owner), not a retention-mechanic problem. Only flat, node-independent churn is a return-reason problem.
3. **Write the return reason for each horizon** as a sentence the player could say: "I come back because my crops are ready", "because my streak is 12", "because my guild needs my donation by Friday". If you cannot write it, the horizon has no lever.
4. **Design the daily loop as an appointment, not a reward.** A login reward pays for showing up; an appointment gives a reason that only exists today (timer completing, daily challenge, guild request, limited shop slot). Stack 2–3 appointments at staggered intervals (e.g. 4 h, 8 h, 24 h) so two to three sessions per day each have a purpose.
5. **Build streaks with forgiveness from day one.** An unforgiving streak converts a loyal player's single missed day into a churn event. Give one free freeze per week, earnable or purchasable extra freezes, and a repair window of 24–48 h. Without forgiveness, a 30-day streak at 85% daily return probability survives 0.8% of the time; with 4 forgiven misses it survives 52%.
6. **Add social only where the core loop has a cooperative or comparative hook.** Guilds work when members can give each other something the solo player lacks (donations, help timers, shared boss damage, team events). A guild with only chat is a dead room. Gate guild unlock after the player has a habit (typically day 3–7 or the equivalent progression node), not in the FTUE.
7. **Engineer virality where the game produces shareable moments.** Compute k = invites per user × invite conversion. Design the invite at the moment of peak emotion (big win, rare drop, guild need), reward both sides, and cap referral rewards so they cannot be farmed.
8. **Treat notifications as a contract, not a channel.** Every push must refer to something the player set in motion (timer done, streak at risk, friend needs help). Ask for permission after the player has a reason to want reminders, cap frequency, and suppress for 24 h after any session.
9. **Design win-back as a re-entry, not a gift.** A lapsed player returns to a game that moved on. Give a catch-up package, a summary of what changed, and a short path to the current content floor; a pile of currency without direction churns again within days.
10. **Score the backlog and test against holdouts.** Every lever ships behind a remote-config flag with a persistent 5–10% holdout for the horizon it targets. Read D7 levers at D7+, not earlier; send sample sizing to `gamedev-analytics-engineer`.

## Deliverables

### 1. Retention Lever Map

```
GAME: ____  GENRE: ____  COHORT: install wk __  PLATFORM/GEO: ____
HORIZON │ CURRENT │ GENRE BAND │ GAP │ RETURN REASON (player sentence) │ LEVERS LIVE │ LEVER PROPOSED │ OWNER
D1      │  __%    │  __–__%    │     │                                  │             │                │
D7/D1   │  __     │  __–__     │     │                                  │             │                │
D30/D7  │  __     │  __–__     │     │                                  │             │                │
Progression churn spikes (node, % of churners): ____
Leaking horizon (earliest out of band): ____   Decision: ____
```

### 2. Habit Loop Spec

```
LOOP NAME:        ____
CUE:              [internal (boredom slot, commute) / external (push, badge, timer)]
ACTION:           [what the player does, seconds to complete]
REWARD:           [variable? fixed? progress toward a visible goal?]
INVESTMENT:       [what the player leaves behind that makes tomorrow better: planted timer, streak, guild contribution]
CADENCE:          [interval(s); sessions/day it is meant to create]
FAILURE STATE:    [what happens if missed — must not punish more than one cadence]
METRIC:           [sessions/DAU, return rate within cadence + 25%]
```

### 3. Streak Spec

```
STREAK UNIT:        [day / week; "day" = local midnight or rolling 24 h — choose and document]
QUALIFYING ACTION:  [one meaningful action, not just app open]
REWARD LADDER:      day 1..7 escalating, day 7 milestone, repeat; milestone at 30/100
FREEZES:            1 free per week; earn more via ____; buy cap __ / month
REPAIR WINDOW:      __ h after break, cost ____
BREAK UX:           show what was kept (best streak, partial reward), never a shame screen
METRICS:            streak-holder share of DAU, P(streak survives 7/30), freeze usage, D30 of holders vs non-holders (holdout)
```

### 4. Notification Matrix

```
ID │ Trigger (player-caused) │ Copy intent │ Delay │ Quiet hours │ Cap group │ Suppress if │ Opt-out category │ Metric
N1 │ build timer complete     │ ready        │ 0     │ 22:00–08:00 │ timers    │ session <1h │ "Progress"       │ open rate, uninstall Δ
N2 │ streak at risk           │ save streak  │ 20:00 │             │ streak    │ played today│ "Reminders"      │ streak save rate
N3 │ guild request open       │ teammate     │ 30m   │             │ social    │             │ "Guild"          │ fill rate
GLOBAL CAP: __/day, __/week   PERMISSION ASK: after ____ (never at first launch)
```

### 5. Referral / Viral Spec

```
SHARE MOMENT:      [event that triggers the ask]
INVITE MECHANIC:   [link / code / contact pick]; deep link lands on: ____
REWARD:            inviter ____ (on invitee reaching milestone ____), invitee ____ (on install)
FRAUD CONTROLS:    reward on invitee milestone (not install), device + account dedupe, cap __ rewards / month
MEASURED:          i (invites/active user/period) = __, c (install conversion) = __, k = i × c = __, cycle time t = __ days
```

### 6. Win-back Playbook

```
SEGMENT:        lapsed 7–13 d / 14–29 d / 30+ d; payer vs non-payer
CHANNEL:        push (if opted in) / email (if consented) / paid re-engagement
OFFER:          catch-up pack sized to reach current content floor in ≤ 3 sessions
RE-ENTRY FLOW:  "what's new" (≤ 3 cards) → one guided goal → normal loop
GUARDRAIL:      do not discount payers' usual purchase (teaches lapsing); measure 14-day re-churn
```

### 7. Experiment Backlog

```
ID │ Hypothesis (if we X, horizon Y moves because Z) │ Horizon │ Reach % DAU │ Expected Δ (pp) │ Confidence 1–5 │ Effort (dev-days) │ Score │ n/arm needed │ Days to read │ Guardrails │ Status
Score = Reach × Expected Δ × Confidence ÷ Effort.  Kill any test whose n/arm exceeds 4 weeks of eligible installs.
```

## Quantitative Reference

### Horizon ratios by genre (heuristic targets, all-install denominator)

Raw D1/D7/D30 median and average bands live in `game-playtest-analyst`. For lever choice the ratios matter more, because they isolate which horizon leaks.

| Genre | D1 top-quartile | D7/D1 | D30/D7 | Dominant D30 lever |
| --- | --- | --- | --- | --- |
| Match-3 / puzzle | 40–45% | 0.40–0.50 | 0.45–0.55 | Level cadence, meta (renovation/collection), team events |
| Casual board / social (Monopoly GO-style) | 40–50% | 0.40–0.50 | 0.45–0.55 | Social stealing/attacks, sticker albums, partner events |
| 4X / SLG | 35–40% | 0.40–0.45 | 0.55–0.65 | Alliance obligations, territory, server events |
| Mid-core RPG / gacha | 40–50% | 0.45–0.55 | 0.50–0.60 | Roster investment, banners, guild bosses |
| Idle / incremental | 35–45% | 0.35–0.45 | 0.40–0.50 | Offline progress, prestige resets |
| Hybrid-casual | 35–45% | 0.30–0.40 | 0.30–0.40 | Meta layer bolted onto the core |
| Hypercasual | 35–40% | 0.20–0.30 | 0.15–0.25 | Content volume; retention is not the model |

Heuristics compiled from practitioner benchmarks; validate against your own mature cohorts. If D7/D1 is in band but D1 is low, you have an FTUE problem, not a habit problem.

### Lever-to-horizon map

| Lever | D1 | D7 | D30 | Notes |
| --- | --- | --- | --- | --- |
| FTUE pacing, early win, visible next goal | ●●● | ● | | Owned by UX; growth sets the target |
| First-session cliffhanger (timer, chest, unfinished build) | ●●● | ●● | | The single cheapest D1 lever |
| Daily login calendar | | ●● | ● | Weak alone; strong with a day-7 milestone |
| Dailies / daily challenge | | ●●● | ●● | Must be completable in one session |
| Appointment timers (4/8/24 h) | ● | ●●● | ● | Sets sessions/day |
| Streaks with forgiveness | | ●●● | ●● | Without forgiveness: net negative at D30 |
| Collections / albums | | ●● | ●●● | Long visible goal; drives trade loops |
| Guilds / teams | | ● | ●●● | Unlock after habit forms |
| Friends, gifting, leaderboards | | ●● | ●● | Needs social graph or contact import |
| LiveOps events | | ●● | ●●● | See `gamedev-liveops-designer` |
| Push notifications | ● | ●● | ● | Only player-caused triggers |
| Win-back flow | | | ●● | Reactivation, not prevention |

### Viral and referral math

- **k-factor:** `k = i × c` where i = invites sent per active user over the cycle and c = invite-to-install conversion.
- **Amplification:** each paid install yields `1 + k + k² + … = 1/(1 − k)` total installs for k under 1. k = 0.1 → 1.11×; 0.2 → 1.25×; 0.3 → 1.43×; 0.5 → 2.0×. Most games sit at k = 0.05–0.25 (heuristic); claims above 0.5 usually count re-installs or organic baseline.
- **Cycle time t** matters as much as k: installs after n days ≈ seed × Σ kʲ for j ≤ n/t. Halving t doubles the rate at which a k under 1 converges.
- **Feed the blended CPI:** effective CPI = paid CPI ÷ (1 + organic uplift). Hand the uplift number to `gamedev-financial-growth-strategist`; do not let UA count it twice.
- **Referral rewards:** reward the inviter on the invitee's milestone (e.g. reaching level 10 or day 3), not on install — this kills most self-referral farming. Value the inviter reward at no more than the blended CPI you would otherwise pay.

### Streak forgiveness math

`P(30-day streak survives) = Σ_{j=0..m} C(30, j)(1 − p)^j p^(30−j)` for daily return probability p and m forgiven misses.

| p (daily return of a habitual player) | 0 freezes | 2 freezes | 4 freezes |
| --- | --- | --- | --- |
| 0.70 | ~0% | 0.2% | 3% |
| 0.85 | 0.8% | 15% | 52% |
| 0.95 | 22% | 81% | 98% |

The design point: forgiveness converts a lottery into an achievable goal for exactly the players you most want to keep.

### Notifications

- **Permission.** iOS requires an explicit prompt; Android 13+ requires the `POST_NOTIFICATIONS` runtime permission. Pre-prompt with an in-game explanation tied to a concrete benefit ("tell me when my crops are ready") after the first timer exists — never at first launch.
- **Caps (heuristic).** 1–2 per day, 5–8 per week for casual; up to 3 per day only when each is player-caused (timers in 4X/builders). Suppress for 24 h after a session ends unless the player started a timer. Respect local quiet hours.
- **Health metrics.** Open rate, session-attributed rate, opt-out and uninstall within 24 h of a send. A notification that lifts opens but raises uninstalls is net negative — measure both against a no-send holdout.

### Win-back

- Define lapse by inactivity (7, 14, 30 days); reactivation rates fall steeply with lapse length, so the 7–13 day segment is where the money is.
- A returning player must reach the current content floor in about three sessions (the catch-up rule in `game-economy-balancer`, if installed).
- Paid re-engagement on iOS: AdAttributionKit supports overlapping re-engagement conversions from iOS 18.4 (needs the `EligibleForAdAttributionKitOverlappingConversions` Info.plist key) (https://www.adjust.com/blog/wwdc-adattributionkit-2025/). Measure re-engagement against a holdout; attribution alone over-credits players who would have returned.

Read `references/retention-lever-catalog.md` when you need the full catalog of levers by genre with implementation notes and known failure modes.

## Diagnostics

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| D1 low, D7/D1 normal | First-session promise missing; no unresolved goal at session end | Add a first-session cliffhanger (timer, half-built thing); hand FTUE flow to UX |
| D1 fine, D7/D1 low | No daily appointment; nothing due tomorrow | Add dailies + 4/8/24 h timers; daily goal completable in one session |
| D30/D7 low, flat across progression | No long goal or social obligation | Collections, guild unlock at day 3–7, weekly team event |
| D30/D7 low, spike at one level/chapter | Content wall or exhaustion | Route to level/economy owner; not a growth-mechanic problem |
| Sessions/DAU near 1.0 | Single-appointment design | Stagger timers; add a second daily touchpoint |
| Streak holders churn right after a break | No forgiveness, shame UX | Freezes, repair window, show what was kept |
| Push opt-in low | Asked at first launch, no reason given | Pre-prompt after first timer with concrete benefit |
| Push opens up, uninstalls up | Non-player-caused sends, too frequent | Cut to player-caused triggers, cap, quiet hours |
| Guild join rate high, D30 flat | Guild has nothing to give | Add donations, help timers, shared goals |
| Referral installs spike, retention of referred low | Reward on install; farming | Reward on invitee milestone; dedupe devices |
| Win-back returns churn within 7 days | Currency gift without direction | Re-entry flow, guided goal, catch-up to content floor |
| Lift disappears after 3–4 weeks | Novelty effect | Keep holdout running 4+ weeks before declaring a win |

## Anti-Patterns

**The Guild Rescue** — shipping a social system to fix a D1 problem. Players who quit in the first session never see it.

**The Login Bribe** — a login calendar with no appointment. Players open, claim and close; sessions rise, engagement does not.

**The Unforgiving Streak** — one missed day resets a 40-day streak. You have converted your most loyal player's bad Tuesday into a churn event.

**The Spam Cannon** — notifications on a schedule rather than a trigger. Opt-outs climb, and the channel dies for the messages that mattered.

**The First-Launch Permission Ask** — requesting push before the player knows what there is to be reminded about. The OS prompt is often one-shot; you burned it.

**The Vanity k** — counting re-installs and organic baseline as viral installs. UA then double-counts the uplift and overbids.

**The Currency Win-back** — a returning player gets a pile of currency and no path. They spend it on the wrong things and lapse again.

**The Holdout-Free Win** — shipping a lever to 100% and reading a before/after. Seasonality and UA mix shifts will make anything look like it worked.

## Quality Checklist

- [ ] Leaking horizon identified from D1, D7/D1 and D30/D7 against a named genre band (median or top quartile stated)
- [ ] Churn split by progression node; walls routed to their owner, not treated as retention mechanics
- [ ] Each horizon has a written player-sentence return reason
- [ ] Daily loop has 2–3 staggered appointments; each completable in one session
- [ ] Streaks have free weekly forgiveness and a repair window; break UX shows what was kept
- [ ] Guild/social unlock is after habit formation, and the social system lets members give each other something
- [ ] k computed as i × c from measured data, with re-installs excluded; uplift handed to finance once
- [ ] Referral rewards paid on invitee milestone with device/account dedupe
- [ ] Every notification is player-caused, capped, quiet-hour aware, suppressible, and in an opt-out category
- [ ] Push permission requested after a concrete reason exists, with an in-game pre-prompt
- [ ] Win-back gets lapsed players to the content floor in about 3 sessions
- [ ] Every lever behind a remote-config flag with a persistent holdout; read no earlier than its horizon matures
- [ ] Backlog scored; tests whose n/arm exceeds 4 weeks of eligible installs are cut or redesigned
- [ ] Minors in audience: no open chat, no referral cash rewards, no late-night pushes

## Related Skills

Send cohort-curve reading, power-law fitting and the residual rule to `game-playtest-analyst` (if installed), and progression-node walls to `gamedev-level-layout-designer` or, if installed, `game-economy-balancer`. The FTUE flow belongs to `gamedev-ux-designer` and touch-level onboarding to `mobile-game-ux-designer` (if installed); this skill sets their D1 target and the end-of-session cliffhanger. Events, passes and the content calendar that power D30 are `gamedev-liveops-designer`; long collection and roster goals are `gamedev-meta-progression-designer`; guild wars and competitive ladders are `gamedev-pvp-designer`. Offers attached to win-back or streak repair go to `gamedev-monetization-designer`. Organic uplift, LTV impact of a retention change and re-engagement budgets go to `gamedev-financial-growth-strategist`. Event definitions, holdout assignment and test sizing go to `gamedev-analytics-engineer`. Push delivery, guild services and referral attribution endpoints are `gamedev-backend-engineer`. When the loop itself gives no reason to return, stop adding levers and go to `core-loop-designer` (if installed).
