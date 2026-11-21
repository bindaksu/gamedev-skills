# Event Template Library

Eight templates cover nearly every F2P live calendar. Each block is a starting spec: copy it into the Event Spec, then tune. All numbers are **heuristics** for casual and mid-core mobile; calibrate against your own runs and holdouts.

Shared rules for every template:
- Progress comes from a core-loop action the player already performs. An event that asks for a new action is a feature, not an event.
- Rewards for a full completer are budgeted as a share of the weekly faucet (see SKILL.md, Event reward budget).
- Every template's second run must be config-only.

---

## 1. Milestone (points ladder)

```
JOB:            engagement depth
DURATION:       2-4 days
ENTRY:          automatic; points per core action (e.g. 1 pt per level won, 3 per hard level)
STRUCTURE:      8-15 milestones; first reward within the first session (<= 10 min)
SIZING:         final milestone at p50-p60 of event-window activity of engaged players;
                1-2 stretch milestones at p80
REWARDS:        mostly soft currency and boosters; one headline reward at final milestone
BUDGET:         5-15% of weekly faucet
TARGETS:        participation 50-70% DAU; completion 15-30%
KNOBS:          points per action, milestone spacing (front-load: first 3 milestones in 20% of total points)
FAILURE MODE:   flat spacing -> players stall mid-ladder with nothing in sight
```

## 2. Leaderboard / tournament

```
JOB:            engagement depth among mid/late tenure; competitive spend
DURATION:       1-3 days (short boards keep intensity; long boards reward only time)
ENTRY:          automatic or opt-in at account level gate
BRACKETS:       groups of 50-100, matched by power band and recent activity (not global)
REWARDS:        by percentile: top 1-3 / top 10% / top 25% / top 50% / participation
BUDGET:         10-20% of weekly faucet for top-10% finisher
TARGETS:        participation 25-45% DAU; median bracket score spread visible but reachable
KNOBS:          bracket size, score per action, point multipliers (time-limited only)
ETHICS:         if brackets are back-filled with bots, follow gamedev-pvp-designer disclosure and fairness rules
FAILURE MODE:   unbracketed boards -> same accounts win every run; participation collapses
```

## 3. Collection (sets / album)

```
JOB:            engagement breadth; social trading if enabled
DURATION:       1-6 weeks (album seasons are long-running)
ENTRY:          items drop from core actions and event chests
STRUCTURE:      sets of 6-12 items; rarity tiers; set-completion rewards plus album-completion grand prize
DUPLICATES:     convert to a currency or trade tokens; never dead drops
PITY:           guarantee a missing item after a fixed number of duplicate drops (coordinate with gamedev-monetization-designer if items are purchasable)
BUDGET:         spread across weeks; album grand prize may be the season's headline
TARGETS:        set completion curve, not single completion %; monitor p50 missing-item count over time
FAILURE MODE:   last item rate so low the p95 player never completes; the grind gets posted
```

## 4. Team / co-op

```
JOB:            social retention, guild activity
DURATION:       2-5 days
ENTRY:          guild or ad-hoc team of 3-30; contribution from core actions
STRUCTURE:      shared team milestones + individual contribution floor to claim rewards
FREE-RIDER RULE: reward only members above a minimal contribution (e.g. >= 5% of team median)
BUDGET:         10-20% of weekly faucet
TARGETS:        participation among guild members 60-80%; team completion 30-60%
FAILURE MODE:   reward equal regardless of contribution -> resentment, guild churn
```

## 5. Race (timed head-to-head or small group)

```
JOB:            short-burst intensity; reactivation
DURATION:       hours to 1 day
ENTRY:          opt-in; small group of 2-10 matched by activity
STRUCTURE:      first to N points, or most points by deadline; visible opponent progress
REWARDS:        top 1-3 in group; consolation for finishing
BUDGET:         3-8% of weekly faucet per race
TARGETS:        opt-in 20-40% of DAU; finish rate among opt-ins 40-60%
FAILURE MODE:   matched against far more active players -> instant loss perception; match by recent activity
```

## 6. Mini-game

```
JOB:            novelty spike, content consumption
DURATION:       3-7 days
ENTRY:          event currency earned from core actions, spent on mini-game plays
STRUCTURE:      self-contained board/wheel/dig/path; progress persists within event
COST:           highest production cost of all templates; first run usually needs a client build
REUSE:          design the mini-game as data (board layouts, reward tables) so reruns are config-only
BUDGET:         10-25% of weekly faucet
TARGETS:        participation 40-60% DAU; currency fully spent by >= 70% of participants
FAILURE MODE:   mini-game more rewarding per minute than the core loop -> core loop becomes optional
```

## 7. Login / calendar

```
JOB:            return frequency; reactivation
DURATION:       7 days (rolling) or 14-28 days (seasonal)
STRUCTURE:      claim once per day; escalating rewards with a day-7 headline
MISSED DAYS:    non-consecutive (count logins, not streak) for seasonal calendars; streaks only for 7-day cycles
BUDGET:         2-5% of weekly faucet
TARGETS:        D-count completion among actives 60-80%
FAILURE MODE:   punishing streak resets -> one missed day ends engagement with the calendar
```

## 8. Spend / purchase-milestone

```
JOB:            monetization
DURATION:       1-3 days, at most once per 2 weeks (heuristic)
ENTRY:          purchases of any size progress a ladder
STRUCTURE:      milestones at real price points of the ladder; first milestone at the cheapest pack
GUARDRAILS:     never shown to D0-7 players or minors; no countdown pressure beyond the event window;
                displayed rewards are exact (no "up to"); coordinate with gamedev-monetization-designer
TARGETS:        measure 14-day revenue vs holdout, not event-window revenue
FAILURE MODE:   frequent spend events -> pull-forward; revenue in event window up, 14-day flat
```

---

## Limited-time modes (LTMs)

An LTM is a rule variation of the core game run for a fixed window: new board/map, modified rules, special characters, or a remixed mode.

```
LTM:            [name]
RULE DELTA:     [exactly what differs from the core mode; one or two changes]
DURATION:       3-14 days; rotate 1-3 LTMs per season
QUEUE IMPACT:   (multiplayer) concurrent modes split the player pool; check queue times with gamedev-pvp-designer
REWARDS:        cosmetic or event currency; avoid exclusive power
EXIT:           what returns to the core mode (often a successful LTM becomes permanent)
PROMOTION RULE: an LTM that holds >= 25% of mode play-time over two runs is a candidate for the permanent rotation
```

Keep LTMs inside the existing ruleset and assets so they can run as config. An LTM that needs new code is a feature.

---

## Remix knobs (to rerun a template without fatigue)

| Knob | Example | Production cost |
| --- | --- | --- |
| Theme / skin | Halloween vs spring | Art only |
| Entry action | points from hard levels only | Config |
| Reward table | new headline cosmetic | Art + config |
| Structure twist | milestone ladder with a mid-event bonus hour | Config |
| Social layer | solo milestone becomes team milestone | Code (first time) |
| Scoring multiplier window | 2x points for 2 hours, announced | Config |

Change at least one non-skin knob when a template's participation has decayed > 15% over two runs.
