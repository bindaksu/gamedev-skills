---
name: gamedev-producer
description: >-
  Game production management for mobile and cross-platform F2P: lifecycle
  stages from concept to live with exit criteria and kill gates, team
  composition and size by stage, roadmaps and milestones, risk registers,
  scope cutting with MoSCoW cut lines, live-ops content cadence, rituals,
  estimation, outsourcing vendors and stakeholder reporting. Use when asked to
  plan a milestone or roadmap, decide whether to greenlight or kill a project,
  staff a team, cut scope to hit a date, set a content cadence for a live game,
  run a soft launch schedule, or write a status report for leadership.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: meta
---

# Game Producer

Production is the management of uncertainty, and the only honest tool for it is a gate written before the stage starts. Top-grossing studios are not better at predicting hits; they are better at killing non-hits early and cheaply. Supercell killed 30+ games against 5 hits in 12 years, Royal Kingdom spent 19 months in soft launch, Monopoly GO took about six years and a full genre pivot. A producer who lets a project drift from prototype to alpha without a written kill criterion has converted a cheap question into an expensive one. Every stage has one question it must answer, a team sized to answer it, a timebox, and a pre-agreed number that ends it. Everything else here (roadmaps, risk registers, cut lines, rituals) exists to make that gate decision on time and to make the live game ship content on a cadence players can set a clock by.

## Role Profile

At top-grossing studios the producer owns the "production roadmap and delivery timelines" and is the hub between design, art, engineering, QA, marketing, UA and customer support (https://hitmarker.net/jobs/kabam-game-producer-advanced-level-726287 [proxy]). EA asks producers to "craft and communicate the long-term roadmap" and "use data analytics to identify and own the KPIs" (https://jobs.ea.com/en_US/careers/JobDetail/Producer-I/207406 [proxy]). In live games the role becomes the "live show" owner: content, events and offers on schedule (https://hitmarker.net/jobs/scopely-lead-producer-live-operations-1662445 [proxy]). Supercell ran Brawl Stars without a full-time producer until the team passed ~40 people and single-owner burnout forced the hire (2024).

- **Responsibilities:** stage plans and gates, roadmap, milestone definitions, scope and cut lines, risk register, staffing plan, vendor management, live-ops calendar capacity, stakeholder reporting.
- **Hard skills:** Agile/Scrum and milestone planning, estimation, F2P/LiveOps and monetization literacy, KPI reading, negotiation and change management.
- **Tools:** Jira, Confluence, Sheets, Trello/ClickUp, BI dashboards.
- **KPIs:** "ensure new updates are engaging and retaining players" [quoted, Kabam]; on-time releases and content cadence; velocity predictability.
- **Collaborators:** every discipline lead, GM/game lead, publishing/marketing, UA, community, external vendors.

## When to Use / Not

Use for stage plans, greenlight/kill decisions, staffing, roadmaps, milestones, risk, scope cuts, live-ops cadence capacity, vendor plans and status reports.

Not for: decomposing a single feature into specialist work (gamedev-coordinator); deciding which events to run and their design (gamedev-liveops-designer); setting soft-launch KPI thresholds, LTV and ROAS (gamedev-financial-growth-strategist); release mechanics (gamedev-delivery-release); prototype hypothesis design (if installed, game-prototype-planner).

## Inputs to Gather

- **Current stage** and the date it started. Default: assume the stage the evidence supports, not the one the team claims.
- **The stage question** (for example "is the core loop fun for 10 minutes?"). If missing, write it.
- **Team roster** by discipline, with seniority and allocation percentage.
- **Budget and runway** in months. Default: plan to the next gate only.
- **Genre and comparables.** The benchmark set for gates depends on it.
- **Hard dates:** platform deadlines, marketing beats, IP partner approvals, seasonal events.
- **Live data** (if soft launch or live): D1/D7/D30, ARPDAU, payer conversion, crash-free sessions, CPI by geo.

## Method

1. **Name the stage and its one question.** A stage with two questions gets neither answered.
2. **Write exit criteria and kill criteria before work starts.** Kill criteria are numbers or observable outcomes, plus a date. Store them where leadership signed them. Gates written after the data arrives always pass.
3. **Size the team to the question, not the ambition.** Use the stage table. Adding people before the loop is proven buys art for a game that may die.
4. **Timebox the stage.** Pick the duration from the table and set a hard review date. On the date, decide: pass, kill, or one explicit extension with a new, narrower question. Never two extensions.
5. **Build the milestone plan backward from the gate.** Each milestone has a demoable deliverable and acceptance criteria. "70% done" is not a milestone.
6. **Estimate with ranges and reference classes.** Three-point estimates per package; compare with the last similar feature's actual. Add buffer at the milestone, not per task, so it is visible and protected.
7. **Open the risk register on day one.** Score probability x impact, assign one owner, name the trigger that converts risk to issue, and a mitigation that starts now.
8. **Draw the cut line.** MoSCoW every item. Must = the gate cannot be evaluated without it. When the date slips, cut from the bottom; never move the gate date silently.
9. **For live games, plan cadence from capacity.** Count production days per content unit, multiply by calendar slots, compare with team capacity, and leave 20–30% for bugs, live incidents and QoL [heuristic]. Brawl Stars doubled its team because the QoL backlog had no capacity.
10. **Report on a fixed rhythm** with the template below: status against gate, KPI deltas, top risks, decisions needed. Leadership reads the decisions-needed block first.
11. **At the gate, run the decision meeting** with data, pre-written criteria, and the options pass / kill / pivot / extend-once. Record the decision and reasoning. Redeploy people from killed projects quickly, as Supercell did with Squad Busters.

## Lifecycle Stages and Gates

Durations and sizes are [heuristic] ranges drawn from the studio datapoints in Quantitative Reference. Detailed exit checklists per stage: references/stage-gates.md (read when preparing a gate review).

| Stage | Question | Duration | Team | Exit criteria (examples) | Kill triggers (examples) |
|---|---|---|---|---|---|
| Concept | Is there a market and a hook we can execute? | 2–6 wk | 2–4 | Pillars, target audience, comparables with revenue, core fantasy in one sentence, rough P&L from gamedev-financial-growth-strategist | No comparable proves the audience pays; no team member can articulate the hook |
| Prototype | Is the core loop fun and understandable? | 4–16 wk | 5–10 | Playtesters replay unprompted; loop understood without explanation; prototype kill criteria met | Testers do not replay; the fun needs content not yet built |
| Vertical slice | Can we make it at quality and cost? | 2–4 mo | 10–25 | One complete session at ship quality; per-unit content cost measured; tech risks retired | Content cost per hour of play cannot fit the budget; perf on min tier unreachable |
| Alpha / production | Can we build the whole first-30-days game? | 6–12 mo | 20–50 | Feature complete for soft launch; FTUE, economy, live-ops tools, analytics, crash-free target on min tier | Repeated milestone misses with no scope left to cut |
| Soft launch | Do retention and monetization reach the gate? Can UA scale? | 3–24 mo | 20–50 | KPIs at gate for target geo set (gamedev-financial-growth-strategist), CPI and payback modelled, live-ops cadence proven | Retention plateau after 2–3 major iterations; payback model never closes |
| Global launch | Can we scale and operate? | 4–8 wk ramp | 30–150+ | Capacity tested, phased release done, incident runbook drilled | (go/no-go, not kill: see gamedev-delivery-release) |
| Live | Is the game growing or harvested profitably? | years | 20–150+ (genre-dependent) | Content cadence held, KPIs inside plan | Contribution margin negative with no fix; sunset plan triggered |

**Soft-launch gate values belong to gamedev-financial-growth-strategist.** As a placeholder only [heuristic, casual/midcore]: D1 at least 40%, D7 at least 15%, D30 at least 5–8%, payback model under 12 months. Genre and geo change these materially.

## Team Composition by Stage

Sizes come from public datapoints (2019–2025, see Quantitative Reference). Discipline mix is [inference]: no studio publishes a ratio.

| Stage | Size | Shape |
|---|---|---|
| Prototype | 5–10 | 1 design lead, 2–3 engineers, 1–2 artists (Supercell cell example: 2 art, 3 eng, 1 design) |
| Vertical slice | 10–25 | Add tech art, UI/UX, backend, first producer or the game lead acting as one |
| Alpha | 20–50 | Add economy/live-ops design, analytics, QA, audio (often outsourced), tools engineer |
| Live casual/midcore | 20–50 | Approx. 30–40% engineering, 25–35% art, 15–20% design, 10–15% product/data/QA/community |
| Live mass-market hit | 100–150+ | Sub-teams (pods) per feature area plus live-ops pod; leads and producers per pod |

Shared platform (live-ops tooling, data, UA, CRM) usually sits outside the game team at large studios. If you have no platform, budget 3–6 extra engineers for it [heuristic].

## Live-Ops Cadence Planning

gamedev-liveops-designer designs what runs; the producer guarantees it can be built and shipped on time.

- **Calendar slots:** major update every 4–8 weeks (Genshin ships roughly every 6 weeks [fan source]); weekly events; daily rotations. King adds 30–60 Candy Crush levels weekly, typically on Wednesdays [secondary].
- **Lead time:** content locks 2–3 weeks before its live date for QA and localization; anything needing a client binary must also clear store review and phased release (gamedev-delivery-release).
- **Ratio rule [heuristic]:** at least 70% of live events should be config-only reuse of templates. If most events need new code, cadence will slip.
- **Buffer:** 2 events fully built ahead of the calendar ("bank"), so a slip swaps in a banked event instead of leaving a gap.

## Rituals

| Ritual | Cadence | Output |
|---|---|---|
| Stand-up per pod | daily, 15 min | blockers |
| Sprint planning / review | 1–2 weeks | committed scope, demo |
| Milestone review | per milestone | accept / reject with criteria |
| Live-ops calendar review | weekly | next 6 weeks locked, next quarter drafted |
| KPI review | weekly in live | actions with owners |
| Risk review | bi-weekly | updated register |
| Gate review | per stage | pass / kill / pivot / extend-once, recorded |
| Retro | per milestone and after incidents | 1–3 process changes |

## Deliverables

Full fill-in templates (roadmap, milestone sheet, risk register, cut line, vendor SOW, stakeholder report): references/templates.md (read when producing any of them). Minimal forms:

### Stage plan

```
STAGE: Prototype          START: 2026-10-12   GATE DATE: 2026-12-18 (10 wk)
QUESTION: Do players replay the merge-battle loop unprompted?
EXIT: 8 of 12 testers start a 2nd session unprompted; loop explained back correctly by 10 of 12
KILL: fewer than 5 of 12 replay, or loop needs tutorial text to understand
TEAM: 1 design, 3 eng, 2 art (100%)       BUDGET: 6 people x 10 wk
SIGNED: game lead, studio head            EXTENSION USED: no
```

### Risk register row

```
ID | Risk | P(1-5) | I(1-5) | Score | Owner | Trigger | Mitigation (started) | Status
R7 | Store rejection on loot-box odds | 2 | 5 | 10 | monetization lead | review feedback | odds screen in build 0.9; checklist via gamedev-qa-verifier | open
```

### Cut line (MoSCoW)

```
MUST   (gate fails without it): FTUE, core loop, 1 event template, analytics events, crash reporting
SHOULD (hurts KPIs if missing):  guilds, daily login, second event template
COULD  (nice):                   cosmetics shop, replays
WON'T  (this stage):             PvP ranked, web shop
------ CUT LINE moves up when the date is at risk; the gate date does not move ------
```

### Stakeholder status report

```
PROJECT / STAGE / WEEK x of y        STATUS: green | amber | red (against gate, not effort)
DECISIONS NEEDED: (who, by when, options)
GATE KPIs: metric, target, actual, trend
DELIVERED THIS PERIOD / NEXT PERIOD
TOP 3 RISKS: id, change since last report
SCOPE CHANGES: added, cut, reason
TEAM: headcount, open roles, vendor status
```

## Quantitative Reference

| Datapoint | Value | Year | Source |
|---|---|---|---|
| Supercell kill rate | 30+ killed vs 5 hits in 12 yrs | 2023 | https://mobidictum.com/supercell-ceo-ilkka-paananen-talks-about-nfts-and-why-they-kill-so-many-games/ |
| Supercell Spark new-team program | 16 weeks to demo day and greenlight; ~6 per team | 2025 | https://www.pocketgamer.biz/news/83626/supercell-reveal-spark-applying-science-and-psychology-to-build-better-teams-and-games/ |
| Supercell live teams | 20–35 | 2022 | https://supercell.com/en/news/best-days/7600/ |
| Brawl Stars team | ~20 to 45+ | 2020 to 2024 | https://mobilegamer.biz/why-supercell-doubled-the-brawl-stars-team-and-continues-to-evolve-its-culture/ |
| Royal Kingdom soft launch | 19 months | pre-global launch | https://www.pocketgamer.biz/dream-games-launches-royal-kingdom-worldwide-as-royal-match-nears-4-billion |
| Clash Mini | killed after 2+ yrs soft launch | 2024 | https://gameworldobserver.com/2024/03/14/all-games-killed-by-supercell-everdale-hay-day-pop-clash-mini |
| Monopoly GO | ~6 yrs concept to market, genre pivot; 150+ staff | 2023–24 | https://mobilegamer.biz/scopelys-monopoly-go-three-years-of-iterating-to-greatness-and-one-big-pivot/ |
| Dream Games at Royal Match launch | ~30 people (whole company) | 2021 | https://techcrunch.com/2021/06/30/dream-games-raises-155m-at-a-1b-valuation-as-its-royal-match-puzzle-game-hits-a-royal-flush |
| Gardenscapes production | 100+ | ~2019 | https://www.articy.com/en/showcase/gardenscapes/ |
| Genshin Impact | ~700 people | 2021 | [secondary] gamepressure |

**Estimation heuristics.** PERT estimate = (optimistic + 4 x likely + pessimistic) / 6. First-time features run 1.5–2x the engineer's likely estimate; repeat features (a new event on an existing template) run close to the estimate [heuristic]. Milestone buffer 15–25% of the milestone, held by the producer.

**Outsourcing.** Outsource bounded, specifiable work with a review gate: art production to a style bible, audio, localization and LQA, compatibility QA. Keep in-house: core loop, economy, live-ops calendar ownership, anything that is the game's differentiator. Supercell moved live teams to "better tools, outsourcing pipelines" as they grew (2022). Pay per accepted batch, not per hour, and require a pilot batch before volume. Art briefs: if installed, game-asset-art-director.

## Diagnostics

| Symptom | Likely cause | Fix |
|---|---|---|
| Project in prototype for 9+ months | No timebox or kill criteria | Set a gate date and criteria now; one extension max |
| Every milestone 80% done | Milestones defined by effort, not deliverables | Redefine milestones as demoable outcomes with acceptance criteria |
| Soft launch extended repeatedly with flat D7 | Iterating content instead of the core problem | Name the KPI's root cause; one pivot or kill |
| Live events slip every month | Events need new code; no banked events | Template-first events; bank 2 events ahead |
| QoL backlog grows unboundedly | No capacity reserved | Reserve 20–30% capacity; staff a QoL pod |
| Vendor art returns off-style | Brief underspecified; no pilot batch | Pilot batch with acceptance criteria before volume |
| Leadership surprised by delays | Status reported against effort, not gate | Report red/amber/green against the gate date and KPIs |
| Team grows, velocity falls | Coordination overhead past ~40 people | Split into pods with leads; add producer per pod |

## Anti-Patterns

**The Zombie Project** — no written kill criteria, so it never dies; it absorbs the team that could build the next hit.

**Staffing for the Dream** — hiring for global launch at prototype stage. Art and content get built for a loop nobody has validated.

**The Moving Gate** — gate date slides instead of scope. The cut line exists so the date does not move.

**The Second Extension** — "one more month" twice. The second extension is almost always a kill delayed.

**Calendar Without Capacity** — a live-ops calendar drawn by design without production days attached.

**Percent-Done Reporting** — status reported as effort percentages. Only accepted deliverables count.

**Outsourcing the Core** — handing the economy or the core loop to a vendor. You lose the ability to iterate on the thing that decides the game.

## Quality Checklist

- [ ] Stage, one question, gate date and kill criteria written and signed before work starts
- [ ] Team size and mix match the stage table, with reasons for any deviation
- [ ] Milestones are demoable deliverables with acceptance criteria
- [ ] Estimates are ranges; buffer held at milestone level
- [ ] Risk register open with owners, triggers and started mitigations
- [ ] MoSCoW cut line exists and is reviewed when dates move
- [ ] Soft-launch gates sourced from gamedev-financial-growth-strategist, not invented
- [ ] Live calendar has production days, 20–30% reserve and 2 banked events
- [ ] Vendors have SOWs, pilot batches and acceptance criteria
- [ ] Status report leads with decisions needed and is graded against the gate

## Related Skills

gamedev-coordinator decomposes features into packages that the producer schedules. gamedev-financial-growth-strategist sets soft-launch KPI gates, P&L and greenlight economics. gamedev-liveops-designer designs the events whose capacity you plan. gamedev-qa-verifier and gamedev-delivery-release own release exit criteria and the release train; gamedev-live-serving owns event-day operations. gamedev-reviewer gates design docs before milestones. If installed, game-prototype-planner designs the prototype that answers the stage question, and game-playtest-analyst runs the tests the prototype gate reads.
