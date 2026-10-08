---
name: gamedev-liveops-designer
description: >-
  Design the live-ops layer of a free-to-play game: event calendars, battle and
  season pass structure and value math, reusable event templates, limited-time
  modes, event economies, and the content pipeline that ships them on time. Owns
  LiveOps event campaigns and season arcs. Use when planning a weekly, monthly or
  seasonal event calendar, sizing pass tiers and XP so the median player
  finishes, writing an event spec or template, diagnosing event fatigue or
  falling participation, budgeting event rewards against the core economy, or
  building a T-minus production schedule for an update.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: design
---

# LiveOps Designer

A live game is a calendar, not a feature list. Players do not experience your events one at a time; they experience the overlap of whatever is running today, on top of a core loop they have already mastered. So the unit of design is the week, not the event: what is running, what it asks of each player segment, what it pays relative to the core economy, and what it leaves behind when it ends. Good LiveOps is a small library of proven templates, re-skinned and re-tuned on a rhythm players can feel, with every event shipped as data, measured against a holdout, and retired when its participation curve says so. Novelty is expensive; rhythm is cheap. Spend novelty where the calendar needs a spike and rhythm everywhere else.

## Role Profile

At a top-grossing live studio this is the LiveOps designer or LiveOps manager inside a game team, working against a central events platform (Scopely's Playgami, Playtika's Boost, Playrix's unified LiveOps Platform; see companies.md synthesis).

- **Responsibilities.** Invent and remix events and the monetization mechanics around them; plan the LiveOps economy so players "always have intuitive incentives to engage with the calendar"; keep each event "built on a healthy, well-balanced economy"; align event narrative, timing and messaging with marketing; deconstruct competitors' event calendars (https://hitmarker.net/jobs/supercell-live-ops-designer-hay-day-3571823 ; https://jobs.accel.com/companies/space-ape-games-2/jobs/68314161-live-ops-manager-hay-day).
- **Delivery.** At Scopely the Lead Producer LiveOps delivers the "live show" of content, events and offers (https://hitmarker.net/jobs/scopely-lead-producer-live-operations-1662445). King runs a dedicated in-game events team in Stockholm and treats the whole of Candy Crush as being "in live operations mode" (https://www.globalgamesforum.com/news/inside-live-ops-at-king-how-candy-crush-stays-fresh-after-14-years ; https://mobilegamer.biz/candy-crush-boss-todd-green-on-live-ops-excellence-new-games-and-that-microsoft-takeover/).
- **Hard skills.** Event and calendar design, LiveOps economy, offer placement, A/B testing, spreadsheets, competitor deconstruction, and now explicitly AI-assisted content and automation. Bar for senior: 5+ years in live-service F2P mobile.
- **Tools.** In-house LiveOps CMS / calendar and remote-config tools, A/B platform, spreadsheets, BI dashboards. Configuration is often executed by a separate LiveOps configuration engineer who schedules events from the designer's spec and validates them with QA (https://builtin.com/job/senior-configuration-engineer-valid-us-visa-mandate/6738922) — so the spec must be exact enough to configure without a meeting.
- **KPIs.** "Player engagement and business growth" (quoted); event participation and completion; event revenue and offer conversion; config error rate on the events you own (inferred).
- **Collaborators.** Economy designer, monetization/PM, LiveOps artists and UI, narrative, analytics, marketing/community, LiveOps QA and config engineering.

## When to Use / Not

Use for: the event calendar at any horizon, battle/season pass design, event templates and specs, limited-time modes (LTMs), event currencies and shops, event reward budgets, content cadence, and the T-minus production schedule. **This skill owns LiveOps event campaigns and season arcs** — the multi-week narrative/reward arc that strings events together. `gamedev-campaign-designer` covers single-player story and mission campaigns and only points here for event campaigns.

Not for:
- Offer pricing, pass price points, gacha disclosure and spend ethics — `gamedev-monetization-designer`.
- Pure economy math (faucet/sink ledger, cost curves, exchange rates) — if installed, `game-economy-balancer`.
- Ranked seasons, MMR resets and competitive ladders — `gamedev-pvp-designer` (you schedule them; they design them).
- Runtime operations on event day: kill switches, scaling, incident comms — `gamedev-live-serving`.
- Store submission, phased rollout and hotfix-vs-config decisions — `gamedev-delivery-release`.
- Permanent progression layers (collections, decor meta, account level) — `gamedev-meta-progression-designer`.

## Inputs to Gather

- **Segments and their play pattern**: DAU split by tenure (D0–7, D8–30, D31+) and by payer tier; active days per week for p25/p50/p75. Default if missing: median engaged player active 5 of 7 days, casual 3 of 7.
- **Core economy numbers**: weekly faucet per currency at p50 and the free hard-currency trickle. Without these you cannot budget rewards; ask the economy owner or, if installed, `game-economy-balancer`.
- **Current calendar** for the last 8–12 weeks with participation, completion and revenue per event, and any holdout data.
- **Template inventory**: which event types the client can already run from config alone, and which need code or new assets.
- **Release train**: client update cadence, store review assumptions, asset hot-update capability, localization turnaround. Default: client update every 4 weeks, localization 10 working days.
- **Business targets** for the period (revenue, retention, reactivation) and fixed dates: holidays, IP/marketing beats, platform featuring windows.
- **Team capacity**: art and config hours per week available to LiveOps. The calendar must fit it; a calendar the team cannot produce is fiction.

## Method

1. **Map the beat structure before naming events.** Lay out four layers: always-on (login, dailies), weekly beats (2–4 rotating events), the season (pass, 4–8 weeks), and quarterly tentpoles (major update, holiday). Decide the rhythm first; events are slotted into it.
2. **Assign one job per slot.** Each event exists to move one metric: engagement depth, reactivation, monetization, social, or content consumption. An event with two jobs gets tuned for neither.
3. **Pick from the template library first.** New mechanics cost 4–10× a re-skin in production time (heuristic). Budget at most one genuinely new template per quarter; everything else is remix — new theme, new reward table, new rule twist. Read `references/event-templates.md` when writing a spec.
4. **Apply the overlap rules** (Quantitative Reference). Check every day of the calendar against them; collisions are the most common self-inflicted wound.
5. **Budget rewards against the core faucet.** Size each event's total reward for a full completer as a share of the weekly faucet, sum concurrent events, and stay under the ceiling. Hand the resulting numbers to the economy owner for a ledger pass — events are faucets.
6. **Design the event currency lifecycle.** Every event currency expires or converts at end. Specify the conversion rate, the grace window for spending, and what happens to unspent tokens. Non-expiring event currency is an unledgered faucet.
7. **Split the calendar by tenure.** New players (roughly D0–7) see a beginner track and no competitive or spend-ranked events; veterans see the full calendar. Gate by account level or install day, not by luck of when they installed.
8. **Size the pass** with the formulas below. Solve for the median engaged player finishing at 75–85% of the season, then check what a casual player reaches and whether that is still worth the price.
9. **Build the T-minus schedule** backward from the go-live date. Mark which events are config-only and which need a client build; the latter move 4+ weeks earlier.
10. **Instrument and hold out.** Every event ships with start/progress/claim/complete events, and recurring templates run with a 5% holdout (heuristic) at least once per quarter to measure incrementality instead of attributing all event-day revenue to the event.
11. **Review after every run.** Participation, completion, revenue in a 14-day window (to catch pull-forward), and run-over-run decay for the template. Retire, rest or remix based on the decay rule.

## Deliverables

### 1. Event Spec (one per event; configurable without a meeting)

```
EVENT:            [name]                     TEMPLATE: [milestone/leaderboard/collection/team/race/mini-game/login/spend]
JOB:              [single metric it moves]   TARGET:   [e.g. participation >= 45% of DAU, completion 15-25%]
WINDOW:           [start UTC] - [end UTC]    DURATION: [h]   GRACE (shop/claim): [h]
ELIGIBILITY:      [account level >= N / install day >= N / segment]
ENTRY ACTION:     [what earns progress; must be a core-loop action]
PROGRESS:         [points per action; caps per day]
MILESTONES:       [table: points | reward | currency value]
EVENT CURRENCY:   [name | expires at end? | converts to X at rate R, cap C]
REWARD BUDGET:    [full-completer value] = [s]% of weekly faucet (ceiling [s_max]%)
OVERLAPS WITH:    [events running concurrently; overlap rule check: pass/fail]
CONTENT DEPS:     [art / copy / loc keys / audio / new code? Y/N]
DELIVERY:         [config-only | asset hot-update | client build vX.Y]
TELEMETRY:        event_view, event_join, event_progress, milestone_claim, event_complete, event_shop_purchase
HOLDOUT:          [% or "none this run"]
SUCCESS / KILL:   [metric and threshold that decides rerun, remix or retire]
OWNER / CONFIG:   [designer] / [config engineer]   QA SIGN-OFF: [date]
```

### 2. Calendar Grid (8–12 weeks, one row per day)

```
Date | Weekday | Always-on | Weekly beat A | Weekly beat B | Season/pass | Tentpole | Offer slot | New-player track | Rest? | Collision check
```

Fill the collision check per day; a blank cell means the day was not checked. A worked 4-week grid lives in `references/calendar-and-pipeline.md` — read when building a calendar from scratch.

### 3. Pass Design Sheet

```
SEASON LENGTH D:          [days]
TIERS N / XP per tier:    [N] / [flat or curve]       TOTAL XP T: [N x XP]
XP SOURCES:               daily quests [n x xp, completion%] | weekly [n x xp, completion%] | per-match/per-level [xp x count]
SEGMENT ACTIVE RATIO p:   engaged [0.7] | casual [0.4]
XP/CALENDAR DAY:          engaged [x] | casual [x]
COMPLETION DAY:           engaged [T / x] -> [% of D]   (target 75-85%)
CASUAL REACHES TIER:      [x_casual x D / XP per tier]
PRICE / PREMIUM+:         [$] / [$, +K tiers]
PREMIUM VALUE V:          [sum shop-equivalent value / price]       (target 5-10x)
VALUE AT CASUAL TIER:     [value / price]                            (must be >= 2x)
HARD-CURRENCY RETURN:     [currency returned / price in currency]    (decide <100% or >=100% deliberately)
TIER SKIP PRICE:          [currency per tier]
CATCH-UP:                 [mechanism, cap]
FREE TRACK SHARE:         [free value / premium value]               (target 15-30%)
```

### 4. T-Minus Production Schedule

```
Milestone                      | Config-only event | Client-build event | Owner
Concept + job + template pick  | T-6w              | T-10w              | LiveOps design
Economy/reward table approved  | T-5w              | T-8w               | LiveOps + economy
Art brief out                  | T-5w              | T-9w               | LiveOps art
Copy lock -> localization      | T-4w              | T-6w               | Narrative / loc
Code complete in build         | n/a               | T-5w (in release branch) | Engineering
Assets final + hot-update pack | T-2w              | T-4w               | Art / tech art
Config built in staging        | T-2w              | T-3w               | Config engineer
QA pass (staging, time-shifted)| T-10d             | T-3w (with build)  | LiveOps QA
Store / featuring assets       | T-3w              | T-4w               | Marketing (verify platform lead times)
Build submitted                | n/a               | T-14d              | Release
Go/no-go + comms scheduled     | T-2d              | T-2d               | Producer / live-serving
```

All lead times are heuristics for a mid-size live team; replace with your measured cycle times after two quarters.

### 5. Post-Event Review (one page)

Job and target; participation, completion and milestone funnel; revenue in event window and 14-day window vs baseline or holdout; economy delta (p50 balance before/after); run-over-run decay; verdict: rerun / remix / rest / retire, with the metric that will confirm it next run.

## Quantitative Reference

All thresholds in this section are **heuristics** from common F2P practice unless a source is named. Calibrate against your own holdouts.

### Cadence

| Layer | Typical rhythm | Notes |
| --- | --- | --- |
| Always-on | daily reset, 7-day login cycle | Never change the reset time once live |
| Weekly beat | 2–4 events, each 2–5 days | Stagger starts (e.g., Mon and Thu) so something new lands twice a week |
| Season / pass | 28–35 days casual/mobile; 6–10 weeks mid-core | Shorter seasons sell more passes per year but increase fatigue |
| Content update | 4–8 weeks | HoYoverse ships major patches roughly every 6 weeks (companies.md, fan source) |
| Content drip | weekly | King adds Candy Crush levels weekly, typically Wednesdays, in batches of 30–60 (companies.md, secondary source) |
| Tentpole | quarterly + 3–5 holidays/yr | Holidays are fixed dates; produce them first |

### Overlap rules

- At most **one competitive (ranked/leaderboard) event, one collection or milestone event, and one pass** running at once; a second competitive event splits the same players' attention and halves both leaderboards' intensity.
- At most **3 event progress bars plus the pass** on the home screen at any time; past that, players stop reading them.
- Never run two events whose entry actions are different core-loop actions that compete for the same energy or lives — players must choose, and the loser event under-participates.
- **One low-intensity day per week** with no competitive or spend-ranked event. Login and dailies continue. Rest days lift participation in the next event and protect against fatigue.
- New players (D0–7, or below the competitive unlock level) see at most one event besides a beginner track.

### Event reward budget

```
Budget_event = W_faucet × s
```

where W_faucet is the p50 weekly faucet of that currency. Starting shares: minor weekly event s = 5–10%; major weekly event 15–25%; tentpole 30–50% spread over its duration. **Sum of all concurrent events ≤ 40% of the weekly faucet** for a full completer; above that, events become the economy and the core loop becomes optional. Hard currency from events ≤ 50% of the free weekly hard-currency trickle. Validate at p90 participation, not p50 — completers are where inflation shows.

### Event currency lifecycle

- Expires at event end, or converts at a punitive rate (5:1 to 20:1 into soft currency), capped per event.
- Grace window 24–48 h for the event shop and unclaimed milestones; auto-claim anything earned.
- Never carry event currency across runs unless the template is designed as a long-running token economy with its own sinks.

### Battle / season pass math

```
T          = N × XP_tier                                     (total XP)
x(p)       = p × (Σ daily XP × completion) + weekly XP × completion / 7 + passive XP × p
             (XP per calendar day for a segment with active-day ratio p)
Day_done   = T / x(p)          target: 0.75–0.85 × D for the median engaged player (p ≈ 0.7)
Tier_casual= min(N, x(0.4) × D / XP_tier)
V          = Σ shop-equivalent value of premium rewards / price           target 5–10×
V_casual   = value of premium rewards up to Tier_casual / price           floor 2×
Skip price ≥ price / 10 per tier, so buying the last 10 tiers costs ≥ the pass itself
```

- **Free track** carries 15–30% of total pass value and must include something visible the premium track then upgrades — the free track is the premium track's advertisement.
- **Premium+ bundle** = pass + 20–25% of tiers, priced 2–2.5× the pass.
- **Catch-up.** Weekly challenges unlock cumulatively so late joiners can bank them; optionally an XP boost scaled on the gap to expected pace, capped at 2×, ending at parity. Never let catch-up make a late buyer finish faster than an on-time player.
- **Hard-currency return.** Returning ≥ 100% of the pass's currency price makes the pass self-funding for completers — strong for retention and repeat purchase, weak for revenue per completer. Decide it deliberately with `gamedev-monetization-designer`.

### KPI bands (heuristic, casual/mid-core mobile)

| KPI | Healthy | Investigate |
| --- | --- | --- |
| Participation (% DAU with ≥1 progress action) | 40–70% for core weekly events | < 30% |
| Completion (% of participants hitting final milestone) | 10–30% for milestone events | > 50% (too easy) or < 5% |
| Run-over-run participation decay, same template | < 10% | > 15% for two runs: rest or remix |
| Pass purchase, among season-active players | 5–15% mid-core; 2–6% casual | below range with high free-track progress = value problem |
| Event revenue lift vs holdout, 14-day window | positive | positive in-window, negative 14-day = pull-forward |

### Delivery classes

| Class | What changes | Lead time | Risk |
| --- | --- | --- | --- |
| Config-only | Rules, rewards, dates, existing assets | 2–6 weeks | Config error; validate in staging with time shift |
| Asset hot-update | New art/audio via downloadable bundles | 4–6 weeks | Download failures on poor networks; ship fallback art |
| Client build | New code or template | 8–10 weeks | Store review, adoption lag — players on old builds must see a graceful "update to join" |

Design every new template so its second run is config-only. A template that needs code every time is not a template.

## Worked Example — 30-day pass, mid-core mobile

Price $9.99 (≈1,000 gems; gem value $0.01). 50 tiers.

**First draft:** 1,000 XP/tier ⇒ T = 50,000. Dailies 3 × 300 XP at 85% = 765; matches 8 × 40 = 320; weekly 7 × 600 at 70% = 2,940/week = 420/day. Engaged p = 0.71: x = 0.71 × (765 + 320) + 420 = **1,190 XP/day** ⇒ Day_done = 42 days. The median engaged player never finishes a 30-day season. Purchase rate collapses in week 2 as players project they cannot finish.

**Fix:** raise quest XP and lower tier cost. Dailies 3 × 500 at 85% = 1,275; matches 320; weekly 7 × 900 at 70% = 4,410/week = 630/day. x(0.71) = 0.71 × 1,595 + 630 = **1,762 XP/day**. 50 tiers × 850 XP = 42,500 ⇒ Day_done = **24.1 days = 80% of D**. Inside the 75–85% band, with six days of slack for missed sessions.

**Casual check:** p = 0.4, weekly completion 50%: x = 0.4 × 1,595 + 6,300 × 0.5 / 7 = 638 + 450 = 1,088/day × 30 = 32,640 XP ⇒ **tier 38**.

**Value:** premium track = 1,200 gems ($12) + three epic skins (1,200 gems each, $36) + one legendary skin at tier 50 ($20) + consumables ($15) = **$83 ⇒ V = 8.3×**. At tier 38 the casual has ~912 gems, two skins and most consumables ≈ $44 ⇒ **V_casual = 4.4×**, above the 2× floor. Hard-currency return 1,200/1,000 = 120%: completers can fund the next pass — accepted deliberately as a retention lever, and logged with the economy owner as a 1,200-gem per-season faucet for payers.

**Skip price:** 150 gems/tier ⇒ last 12 tiers = 1,800 gems ($18) > pass price, so buying skips never undercuts the pass. **Premium+:** pass + 12 tiers at $24.99 (2.5×).

## Diagnostics

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Participation < 30% of DAU | Entry action is not a core-loop action, or event is buried behind a 4th progress bar | Make progress come from normal play; enforce the 3-bar rule |
| Completion > 50% | Milestones sized to median, not to the event's job | Add 1–2 stretch milestones sized at p80 activity; keep the main reward at p50 |
| Same template's participation falls > 15% two runs in a row | Template fatigue | Rest it for 2–4 weeks, then return with a rule twist, not only a new skin |
| Revenue spikes during event, 14-day revenue flat or down | Pull-forward; event is moving spend, not creating it | Measure against holdout; reduce spend-event frequency; move offers to friction points |
| p50 soft balance jumps after every tentpole | Event rewards over budget, or event currency converting too generously | Re-sum concurrent budgets ≤ 40% of weekly faucet; tighten conversion to ≥ 10:1 |
| Pass purchases concentrated in the last week | Players buy only once they are sure to finish | Show projected completion on the pass screen; make early tiers carry visible premium value |
| Leaderboard top ranks are the same accounts every run | Global or unbracketed boards | Bracket by power/spend band into groups of 50–100; reward by percentile, not absolute rank |
| D0–7 players churn during big events | Competitive and spend events shown to new players | Gate by install day/level; give a beginner track |
| Event launched with wrong rewards or dates | Spec ambiguous; no staging QA with time shift | Use the full Event Spec; QA sign-off in staging at T-10d |
| New event slips a week | Needed code but planned as config-only | Classify delivery class at concept; client-build events start at T-10w |
| Veterans report "nothing to do" | Calendar tuned for mid-tenure; no stretch content | Add endgame milestone tier or leaderboard bracket for top power band |
| Holiday event underperforms last year | Same template, same rewards, novelty spent | Keep the theme, change one mechanic; compare to prior-year holdout |

## Anti-Patterns

**The Always-On Treadmill** — something competitive or spend-ranked every single day. Participation decays run over run and the players most engaged are the first to burn out.

**The Leaky Token** — event currency that never expires and never converts. It accumulates across runs into a faucet nobody ledgered, and the third event shop is trivially affordable.

**The Unfinishable Pass** — tiers sized by feel. The median engaged player projects a miss in week two and stops buying; the pass is a revenue line that shrinks every season.

**The Calendar Collision** — two events competing for the same energy or the same competitive attention. Both under-participate and the post-mortem blames the templates.

**The Code-Every-Time Template** — an event type that needs a client build on each run. Cadence is then capped by the release train instead of by design.

**The Whale Podium** — unbracketed leaderboards. The same handful of spenders win every run, everyone else learns the board is not for them, and participation in that template collapses.

**The Day-One Firehose** — new players dropped into the full veteran calendar. They see five progress bars, understand none, and churn before the core loop lands.

**The Unmeasured Event** — attributing all event-day revenue to the event. Without a holdout and a 14-day window you are counting pull-forward as growth.

**The Late Copy Lock** — event text finalized after localization's window. The event ships in English in 14 languages or slips a week.

## Quality Checklist

- [ ] Every event has a single named job and a numeric target
- [ ] Every event uses an existing template, or is the quarter's one new template
- [ ] Calendar checked day by day against the overlap rules; ≤ 1 competitive event, ≤ 3 event progress bars plus the pass, ≥ 1 rest day per week
- [ ] New-player track defined; competitive and spend events gated by install day or level
- [ ] Each event's full-completer reward expressed as % of weekly faucet; concurrent sum ≤ 40%; reviewed by the economy owner
- [ ] Every event currency expires or converts, with rate, cap and grace window specified
- [ ] Pass: median engaged completion day at 75–85% of season; casual tier computed; V 5–10×; V_casual ≥ 2×
- [ ] Hard-currency return of the pass chosen deliberately and logged as a faucet
- [ ] Tier-skip price makes the last 10 tiers cost ≥ the pass
- [ ] Delivery class assigned at concept; client-build events scheduled from T-10w
- [ ] Copy locked before the localization window; QA sign-off in staging with time shift
- [ ] Telemetry events defined; holdout planned for recurring templates at least quarterly
- [ ] Leaderboards bracketed and rewarded by percentile
- [ ] Post-event review filed with rerun / remix / rest / retire verdict

## Related Skills

- `gamedev-monetization-designer` — pass price points, offers inside events, spend-event ethics; you place offers on the calendar, they design them.
- If installed, `game-economy-balancer` — ledger pass on every event budget and on the pass's hard-currency return.
- `gamedev-campaign-designer` — single-player campaigns; it hands LiveOps event campaigns and season arcs to this skill.
- `gamedev-narrative-designer` — event themes and season story arcs; brief at concept, lock at copy lock.
- `gamedev-pvp-designer` — ranked seasons and resets you schedule; bracket matchmaking and bots-in-brackets ethics.
- `gamedev-meta-progression-designer` — permanent collections or decor that events feed into.
- `gamedev-growth-designer` — reactivation and retention events, push and notification timing.
- `gamedev-analytics-engineer` — event telemetry taxonomy, holdouts, dashboards.
- `gamedev-localization-specialist` — localization window and text expansion for event UI.
- `gamedev-qa-verifier` — staging time-shift tests and config validation.
- `gamedev-delivery-release` — client builds and submission dates for client-build events.
- `gamedev-live-serving` — event-day runtime: kill switches, scaling, remote-config rollout, player comms.
- `gamedev-producer` — capacity, roadmap and the go/no-go gate.
