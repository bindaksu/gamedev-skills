---
name: gamedev-ux-designer
description: >-
  Game UX design: player flows, information architecture, navigation depth, FTUE and progressive-disclosure
  strategy, popup and interrupt policy, heuristic audits, friction logs, and UX research plans that end in a
  decision. Use when the user asks to map or fix game flows or menus, plan what to teach and unlock across
  the first week, audit a build for usability, explain why players get lost or miss features, cut popup spam
  at session start, or plan UX research for a feature. Touch and thumb specifics go to mobile-game-ux-designer.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: ux-ui
---

# Game UX Designer

Game design adds friction on purpose; UX removes the friction nobody chose. A level that takes nine attempts is the game. A reward the player cannot find, a feature they never noticed unlocking, or five popups between launch and the Play button is a UX defect, and it costs the same churn. The craft is telling those apart, then proving it. Map what the player must understand and do, measure where comprehension breaks, and change the flow, not the player. The player's mind is the platform: attention is scarce, working memory holds about four things under load, and anything taught but not used within a session is mostly forgotten.

## Role Profile

At King, the Senior UX Designer on Candy Crush is asked to "own UX strategy for Player Value" across progression, rewards, streaks, challenges, onboarding, and engagement. They lead discovery and deliver flows, prototypes, and specs end to end, iterating with UX Research and Data. UX researchers design mixed-methods studies (surveys, interviews, usability tests, lab and remote) and need a portfolio showing research *impact*. King also hires UX Writers.

- **Hard skills:** flows and prototyping (Figma plus engine prototypes), systems thinking, mixed-methods research, usability testing, reading telemetry with data science, FTUE design, stakeholder facilitation.
- **Judged on (inferred):** FTUE and onboarding funnel completion, D1/D7 lift from UX changes, research insights adopted into the roadmap.
- **Collaborators:** product, game design, UI, art, data, engineering, UX research.
- **Market note:** King cut about 200 roles in July 2025, including UX and user research, per anonymous reports. UX that cannot show measured impact is exposed.
- Sources: https://hitmarker.net/jobs/king-senior-ux-designer-candy-crush-saga-4512478, https://hitmarker.net/jobs/king-senior-ux-researcher-809593, https://www.videogameschronicle.com/news/laid-off-king-staff-are-reportedly-being-replaced-by-ai-tools-they-helped-build

## When to Use / Not

Use for: flows, IA, navigation, back behavior, FTUE strategy across days, feature-unlock pacing, popup policy, heuristic audits, friction logs, research planning, and UX specs.

Not for:
- Thumb zones, touch targets, safe areas, haptics, the first-60-seconds beat sheet: if installed, `mobile-game-ux-designer`.
- Test method choice, sample sizing, funnel and cohort statistics: if installed, `game-playtest-analyst`.
- Visual design, tokens, and handoff: `gamedev-ui-designer`.
- Retention loops, notifications, and re-engagement strategy: `gamedev-growth-designer`.
- Tutorial and UI copy voice: `gamedev-script-writer`.
- Disability-specific barriers: `gamedev-accessibility-specialist`.

## Inputs to Gather

- **Core loop and meta map.** Which systems exist and how they connect. If missing, get it from `core-loop-designer` (if installed) before mapping IA.
- **Screen and popup inventory.** Every screen, modal, toast, and badge, with what triggers each.
- **Funnel data.** FTUE step completion, feature discovery rates, and time to first use of each feature. If none exists, the first deliverable is an event list, not a redesign.
- **Audience and session archetype.** Casual commuter or mid-core lean-back. Default: casual, 3 to 5 minute sessions, 4 sessions a day.
- **Monetization and LiveOps surfaces.** Offers and events compete for the same attention as features. List them.
- **Platform back behavior.** Android system back, controller B button, Escape on PC.

## Method

1. **Write job statements per mode.** "When I open the game on a break, I want to play a level within 5 seconds." Every flow is judged against a job, not against a feature list.
2. **Build the IA map** as a tree with depth, and mark how often each node is visited. Why: frequency times depth is the tax players pay. A daily task three taps deep is paid 4 times a day.
3. **Flow the top 10 tasks** with tap counts, decision points, and error states. Compare each against the depth targets below.
4. **Set the progressive-disclosure schedule.** Decide what unlocks when across days 0 to 7, one new system per session early on, each taught by use and verified by an event. Why: a feature taught but not used in that session is largely forgotten.
5. **Write the interrupt policy** that decides what may block the player, in what order, and how often (template below).
6. **Run a heuristic audit** with the game heuristic set below. Score severity 0 to 4.
7. **Write a friction log** from a fresh-install playthrough on a mid-tier device, in real time, as a player would.
8. **Plan research only where a decision depends on it.** Name the decision, the question, the method, and the threshold that changes the decision. Hand method and sample size to `game-playtest-analyst` if installed.
9. **Prototype the riskiest flow** and test with 5 to 8 target players per round. Iterate in RITE style when fixes are cheap.
10. **Spec and instrument.** Every flow step gets an analytics event, so the redesign is measurable. Hand the taxonomy to `gamedev-analytics-engineer`.

## Deliverables

### 1. IA Map

```
HOME (depth 0)                              visits/session
├─ Play / next level         [1 tap]        2.8   ← primary, largest target
├─ Events hub                [1 tap]        0.9
│  └─ Event detail           [2 taps]       0.6
│     └─ Event rewards track [3 taps]       0.2   ← candidate: surface on hub card
├─ Shop                      [1 tap]        0.4
├─ Team / guild              [1 tap]        0.5
│  └─ Team chat              [2 taps]       0.4
└─ Settings (gear)           [1 tap]        0.05  ← low frequency, may sit deep
Back rule: system back closes top modal → returns one level → at HOME asks to exit
```

### 2. Task Flow Table

```
Task                 Freq/day  Entry       Taps now  Target  Decisions  Error states covered
Start next level       12      Home          1         1        0         offline, no lives
Claim daily reward      1      popup         2         1        0         already claimed, clock skew
Join an event           0.5    Events hub    4         2        1         event ended mid-flow
Send lives to team      2      Team tab      5         2        1         team full, cap reached
```

### 3. Progressive Disclosure Schedule

```
Feature        Unlock trigger         Typical day/session  Teach method              Comprehension event
Boosters       level 6                D0 s1                forced use on a board     booster_used_unprompted
Daily reward   first session end      D0 s1                auto-open once, then badge daily_reward_claim
Team           level 25               D1 s2                card on home + 1 tooltip  team_joined | team_browsed
Events         level 30 or D2         D2                   event hub card, no modal  event_entered
Shop offers    first real fail wall   varies               contextual, non-blocking  shop_viewed_from_context
Rule: ≤ 1 new system per session for the first 5 sessions; nothing unlocks in a session that already failed
```

### 4. Interrupt Policy

```
INTERRUPT POLICY — session start and level end
Max blocking modals before first playable tap:  1
Max blocking modals per level-end screen:       1 (others queue to next idle moment)
Priority order: 1 legal/consent  2 data-loss/compensation  3 reward the player already earned
                4 feature unlock  5 event start  6 news  7 offer
Offers: never at session start in the first 3 sessions; never twice in a row; never after a loss twice
Coalesce: 3+ queued rewards → one "You got" summary screen
Every modal: one primary action, a close or back that works, and no hidden auto-purchase state
```

### 5. Friction Log

```
FRICTION LOG — build 1.42.0, Pixel 6a, fresh install, Wi-Fi, 2026-10-08
t       Where              What happened                         Expected            Sev  Type
00:04   splash             3 logos, 6.5 s, not skippable           ≤ 2.5 s               2   wait
00:41   level 1            hand-pointer hides the tile it points at pointer offset       3   clarity
02:10   home               5 popups queued; Play obscured 14 s     1 max                 4   interrupt
03:02   booster unlock     modal text 41 words                     ≤ 12 words, do-it     2   workload
05:30   event hub          ended event still listed, tap = error   hide or "ended"       3   state
Types: wait | clarity | feedback | interrupt | workload | consistency | error-recovery | dead-end
```

### 6. Heuristic Audit Sheet

```
#  Heuristic                       Finding                         Screens     Sev(0-4)  Fix owner
H3 Feedback within 100 ms          reward claim has 600 ms dead     reward      3         UI eng
H6 Consistency                     back closes modal on 4/7 popups  popups      3         UX + eng
```

### 7. Research Plan (one page)

```
Decision at stake     Ship the team-tab redesign A or keep current?
Question              Do new players find "send lives" without help in their first team session?
Method                moderated task test, 6 players who never used team features (method: game-playtest-analyst)
Success threshold     ≥ 5/6 complete in < 30 s without hints → ship A; ≤ 3/6 → redesign entry point
Instrumentation       team_tab_open, send_lives_tap, time_between
Deadline / owner      2 weeks / UX designer
```

## Quantitative Reference

All thresholds here are working heuristics from casual and mid-core practice unless marked otherwise.

| Rule | Target | Why |
|---|---|---|
| Taps from home to core action | 1 | It is the reason the app was opened |
| Taps to any daily-use feature | ≤ 2 | Paid several times a day |
| Taps to any feature at all | ≤ 3 | Beyond this, discovery rate collapses without a pointer |
| Blocking modals before first playable tap | ≤ 1 | Each extra modal adds 2 to 4 s and a dismissal habit |
| New systems per session, first 5 sessions | ≤ 1 | Working memory under load holds about 4 items |
| Tooltip text | ≤ 12 words, dismissed by doing | Matches the mobile FTUE rule in `mobile-game-ux-designer` |
| Primary options on a decision screen | ≤ 5 | Hick-Hyman: decision time grows with log2(n+1) |
| Badges lit on the nav bar at once | ≤ 2 | Beyond that players stop reading badges |
| Feedback after any tap | ≤ 100 ms | Above this the tap feels unregistered |
| Feature discovery | ≥ 70% of eligible players use it within 2 sessions of unlock | Lower means the unlock moment failed |

**Hick-Hyman, computed.** `T = a + b · log2(n + 1)`, with b around 150 ms per bit (heuristic). Going from 8 shop tabs to 4 cuts log2(9) = 3.17 bits to log2(5) = 2.32 bits, about 130 ms saved per visit. It is small per visit and large for a screen opened 3 times a day.

**Game heuristic set (adapted from Nielsen, Desurvire's PLAY, and Hodent's usability and engage-ability pillars):**

| # | Heuristic | Game-specific test |
|---|---|---|
| H1 | Signs and feedback | Every state change has a visible, audible, or haptic response within 100 ms |
| H2 | Clarity | A new player can name the goal of any screen in 3 s |
| H3 | Form follows function | Interactive things look interactive; decorations do not |
| H4 | Consistency | Back, close, confirm, and currency icons behave identically everywhere |
| H5 | Minimum workload | No screen asks the player to remember something from another screen |
| H6 | Error prevention and recovery | Irreversible spends confirm; misclicks can be undone within 3 to 5 s |
| H7 | Flexibility | Skip for veterans, replay for the confused (tutorials re-openable from settings) |
| H8 | Motivation | The next goal and its reward are visible from home |
| H9 | Game flow | Difficulty and teaching never peak in the same session |
| H10 | Interruption-safe | Leaving mid-flow never loses earned rewards |

Severity scale (Nielsen): 0 not a problem, 1 cosmetic, 2 minor, 3 major (fix before the next release), 4 catastrophe (blocks launch).

**Platform back behavior.** On Android, system back must close the top modal, then go up one level, then at home offer exit. Android 16 moves apps targeting API 36 to predictive back by default. Verify in current Android docs whether the legacy back key is still dispatched to your engine version, because Play requires target API 36 from Aug 31, 2026. On controllers, B is back everywhere; on PC, Escape is back and never quits without a confirm.

**Research instruments** (name them in plans, run them through `game-playtest-analyst` if installed): usability task tests, think-aloud, RITE, diary studies, and validated questionnaires such as GUESS, PENS, and the Player Experience Inventory. Pick one questionnaire per study, not three.

## Diagnostics

| Symptom | Likely cause | Fix |
|---|---|---|
| Feature used by < 30% of eligible players | Unlock moment had no teach-by-use step, or it unlocked in a crowded session | Move the unlock to a quiet session; force one guided use |
| Players ask "where are my rewards?" | Rewards granted into an inbox 3 taps deep | Grant in place with an animation to the wallet, or show a summary screen |
| D0 session 1 long but session 2 rare | Session ended on a modal or offer, not a hook | End session 1 on next-goal preview; move the offer |
| Play button tapped late at session start | Popup avalanche | Interrupt policy: 1 blocking modal max, queue the rest |
| Rising misclicks on "Buy" | Primary action sits where "Continue" was | Keep primary-action position stable across modals |
| Tutorial skip rate > 50% and D1 low | Tutorial teaches what players already know | Cut the steps veterans skip; teach only genre-novel mechanics |
| Players stuck on a meta screen | Two goals compete equally on screen | One primary call to action per screen; demote the other |
| Back button exits the game unexpectedly | No back stack | Implement modal stack plus exit confirm at root |
| Research report filed, nothing changed | No decision attached to the study | Research plan template: decision and threshold first |
| Event participation low despite traffic | Event entry buried in a hub | Card on home with progress and time left |
| Badges ignored | Every tab badged permanently | Badge only actionable items; clear on view |

## Anti-Patterns

**Popup Avalanche.** Five modals between launch and play, each owned by a different team, and each "only one tap". Players learn to dismiss without reading, which breaks the one modal that mattered.

**Tutorial Hostage.** A forced 4-minute tutorial with no skip, teaching the genre basics every match-3 player already knows.

**Feature Dump.** Guilds, events, collections, and the shop all unlock at level 10 because that is when the content was ready.

**Mystery Meat Navigation.** Icon-only tabs that the team can read because they built them. Label nav icons.

**Red Dot Inflation.** Badges on everything, forever. The badge stops carrying information and players miss the one that mattered.

**Research Theater.** Studies with no decision attached. The deck is admired and the roadmap is unchanged.

**The Happy-Path Spec.** Flows designed for the online, first-time, sufficient-currency case. Offline, already-claimed, and event-ended states get invented by engineers.

**Modal Maze.** Back closes some popups, X closes others, and tapping outside closes a third kind. Consistency is a feature.

## Worked Example: Merge Game Session Start

Telemetry on a merge game shows median time from launch to first merge of 19 s, and D1 of 28%. A friction log on a mid-tier Android finds:

| Step | Time |
|---|---|
| Splash and logos | 4.0 s |
| Login sync | 2.5 s |
| Daily reward modal | 3.0 s |
| Event start modal | 3.5 s |
| Offer modal | 3.0 s |
| Unlocked-feature modal | 3.0 s |

That is 19 s to first play, with four blocking modals.

Apply the interrupt policy. The daily reward is earned, so it stays as the one blocking modal, cut to a 1.2 s auto-claim animation. The event start becomes a home-screen card with a badge. The offer is suppressed at session start for the first 3 sessions, then shown at the first idle moment after a merge chain. The feature unlock moves to the next level end. Logos drop to 2.0 s and are skippable. Login sync runs behind the board.

The new path is 2.0 + 1.2 = 3.2 s to first merge. Expected effects to test as an A/B, not assume: event entry rate may drop when it is no longer forced. Track `event_entered` per DAU alongside D1, and set a guardrail that event entry may not fall more than 10% relative. If it does, keep the event card but add a single one-time modal on event day 1 only.

## Quality Checklist

- [ ] Job statements written for each mode; every flow traced to one
- [ ] IA map with depth and visit frequency; no daily task deeper than 2 taps
- [ ] Top 10 tasks flowed with tap counts, decisions, and error states
- [ ] Progressive-disclosure schedule with a comprehension event per feature
- [ ] Interrupt policy written, with priority order and max blocking modals per moment
- [ ] Back behavior consistent across all modals; Android predictive back verified on target API 36
- [ ] Heuristic audit with severity on every finding and a named fix owner
- [ ] Fresh-install friction log on a mid-tier device, timestamped
- [ ] Every research study names its decision and threshold before it runs
- [ ] Every flow step instrumented, and the event list handed to analytics
- [ ] Offline, already-claimed, ended, and insufficient-currency states specified
- [ ] Touch and FTUE beat sheet checked with `mobile-game-ux-designer` if installed

## Related Skills

- `mobile-game-ux-designer` (if installed) owns touch, reach, safe areas, haptics, and the first-60-seconds beat sheet. This skill sets the multi-day strategy it executes inside.
- `game-playtest-analyst` (if installed) owns method choice, sample size, and funnel statistics. Send it research plans; take back findings.
- `gamedev-ui-designer` turns flows and IA into visual screens and the engine handoff.
- `gamedev-growth-designer` owns retention loops and notifications. Coordinate the unlock schedule with its D1/D7 levers.
- `gamedev-monetization-designer` owns offers. The interrupt policy decides when they may appear.
- `gamedev-analytics-engineer` implements the flow-step events.
- `gamedev-accessibility-specialist` reviews flows for motor, cognitive, and sensory barriers.
- `gamedev-script-writer` writes tutorial and UI copy to the word budgets set here.
- `gamedev-reviewer` uses this skill's heuristic set as its UX review rubric.
