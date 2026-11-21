# Calendar and Pipeline Worked Reference

Read when building a calendar from scratch, onboarding a new LiveOps team, or reconstructing a T-minus plan after a slip. All durations and percentages are **heuristics** for a mid-size casual or mid-core mobile live team.

## 1. Four-week calendar grid (season 1 of a 30-day pass)

Layers: always-on (login, dailies), Beat A (Mon-Thu), Beat B (Thu-Sun), Season pass (28-30 days), Tentpole (week 3), Offer slot.

```
Wk | Day | Beat A (Mon-Thu)       | Beat B (Thu-Sun)       | Pass | Tentpole            | Offer slot          | New-player track | Rest
1  | Mon | Milestone: Harvest     |                        | S1 d1| -                   | Pass launch         | Beginner 7-day   |
1  | Tue | Milestone              |                        | d2   |                     |                     | Beginner         |
1  | Wed | Milestone              |                        | d3   |                     |                     | Beginner         | yes (no competitive)
1  | Thu | (ends 10:00 UTC)       | Leaderboard: Sprint    | d4   |                     |                     | Beginner         |
1  | Fri |                        | Leaderboard            | d5   |                     |                     | Beginner         |
1  | Sat |                        | Leaderboard            | d6   |                     | Weekend bundle      | Beginner         |
1  | Sun |                        | (ends 20:00 UTC)       | d7   |                     |                     | Beginner (ends)  |
2  | Mon | Collection: Album p1   |                        | d8   |                     |                     |                  |
2  | Tue | Collection             |                        | d9   |                     |                     |                  |
2  | Wed | Collection             | Race (24h)             | d10  |                     |                     |                  |
2  | Thu | Collection             | Team: Guild Build      | d11  |                     |                     |                  |
2  | Fri | Collection             | Team                   | d12  |                     |                     |                  |
2  | Sat | Collection             | Team                   | d13  |                     |                     |                  |
2  | Sun | Collection             | (ends)                 | d14  |                     |                     |                  | yes
3  | Mon | Collection (cont.)     |                        | d15  | Mini-game LTM start | Spend milestone(2d) |                  |
3  | Tue | Collection             |                        | d16  | Mini-game           | Spend milestone     |                  |
3  | Wed | Collection             |                        | d17  | Mini-game           |                     |                  | yes
3  | Thu | Collection             | Leaderboard: Sprint    | d18  | Mini-game           |                     |                  |
3  | Fri | Collection             | Leaderboard            | d19  | Mini-game           | Tentpole pack       |                  |
3  | Sat | Collection             | Leaderboard            | d20  | Mini-game           |                     |                  |
3  | Sun | Collection (album ends)| (ends)                 | d21  | Mini-game (ends)    |                     |                  |
4  | Mon | Milestone: re-skin     |                        | d22  |                     |                     |                  |
4  | Tue | Milestone              |                        | d23  |                     |                     |                  |
4  | Wed | Milestone              |                        | d24  |                     |                     |                  | yes
4  | Thu |                        | Race (24h)             | d25  |                     | Pass last-call      |                  |
4  | Fri |                        | Login: S2 teaser       | d26  |                     |                     |                  |
4  | Sat |                        | Login                  | d27  |                     |                     |                  |
4  | Sun |                        | Login                  | d28  |                     |                     |                  |
```

Collision checks applied:
- Never more than one competitive event (leaderboard, race) on the same day; week 2 Wednesday race ends before the team event starts its first full day.
- Week 3 runs the tentpole mini-game alongside the album and one leaderboard: three event progress bars plus the pass on Thursday to Sunday, at the ceiling.
- The spend milestone lands Monday-Tuesday of week 3 only (album + mini-game + spend = three bars), once in the season, never in week 1 when new players are densest, and ends before the Wednesday rest day.
- Rest days carry no competitive or spend-ranked event.
- New players see the beginner track plus at most one other event during week 1.

Reward budget check (soft currency, p50 weekly faucet 20,000):

```
Week | Events (full completer)                 | Sum   | % of weekly faucet
1    | Milestone 2,000 + Leaderboard top10% 2,500 | 4,500 | 22%
2    | Collection (wk share) 2,000 + Race 800 + Team 2,500 | 5,300 | 27%
3    | Collection 2,000 + Mini-game 4,000 + Leaderboard 1,500 | 7,500 | 38%  (tentpole week, at ceiling)
4    | Milestone 2,000 + Race 800 + Login 600     | 3,400 | 17%
```

Week 3 sits under the 40% ceiling only because the leaderboard was trimmed from 2,500 to 1,500. Send the table to the economy owner for a ledger pass.

## 2. Season arc (LiveOps event campaign)

A season arc strings the calendar into one story and one reward ladder so each event feels like a chapter, not noise.

```
SEASON:           [name / theme]
ARC (4 beats):    setup (wk1) -> complication (wk2) -> climax / tentpole (wk3) -> resolution + teaser (wk4)
NARRATIVE OWNER:  gamedev-narrative-designer (brief at T-10w, copy lock at T-6w for client-build items)
HEADLINE REWARD:  [season-defining cosmetic / character], obtainable free via play at the median, faster via pass
THROUGH-LINE:     season currency or meter fed by every event in the arc, converting at season end
TEASER:           next season revealed in the last 3-5 days to bridge the gap
```

## 3. T-minus checklist (client-build tentpole, go-live = T)

```
T-10w  Concept, job, template choice, delivery class = client build
T-9w   Art brief out; narrative brief out
T-8w   Economy table approved with economy owner
T-6w   Copy lock -> localization starts (10 working days + LQA)
T-5w   Code complete in release branch; feature flag default off
T-4w   Final assets; hot-update bundle built; store/featuring assets delivered (verify current platform lead times)
T-3w   Config built in staging; QA time-shifted run of the full event from start to end + grace window
T-14d  Client build submitted (leaves one rejection-and-resubmit cycle)
T-7d   Build live in stores; adoption tracking starts; old-build players get "update to join"
T-2d   Go/no-go: config diffed against spec; comms (push, in-game news) scheduled; on-call confirmed with live-serving
T      Go live; first-hour dashboard check: joins, progress events, claim errors
T+1d   Participation vs target; economy p50 balance check
T+end+3d  Post-event review filed
```

For config-only events, start at T-6w and drop the code, build and submission rows.

## 4. Config hygiene

- All times in UTC in the spec; show local time to players.
- Event IDs are immutable and never reused; reruns get new IDs so telemetry does not merge.
- Every config change after QA sign-off triggers a re-sign-off.
- Keep a calendar diff: what was planned at T-6w vs what shipped, reviewed quarterly to measure slip rates.
