# Production Templates

Read when producing a roadmap, milestone sheet, risk register, cut line, vendor SOW or stakeholder report.

## Roadmap (quarter view)

```
GAME: ______   STAGE: ______   QUARTER: ______   OWNER: producer
OUTCOME FOR QUARTER: metric, baseline, target

| Track            | Month 1                    | Month 2                  | Month 3                  |
|------------------|----------------------------|--------------------------|--------------------------|
| Core / features  | Guild wars v1 (M2 gate)    | Guild wars tuning        | Ranked season 2          |
| Live ops         | Event A, B, C (templates)  | Season pass S4           | Event D (new template)   |
| Monetization     | Starter pack test          | Pass value test          | Web shop pilot           |
| Tech / platform  | PBL upgrade, min version   | Addressables catalog v2  | Server cost -10%         |
| Quality          | Crash-free target per tier | Perf pass on min tier    | Accessibility pass       |
| Releases         | 1.14 (client)              | 1.15 (client)            | 1.16 (client)            |
Dependencies: arrows between items, each with owner
Out of scope this quarter: list
```

## Milestone sheet

```
MILESTONE: M2 Guild wars playable      DATE: ______    OWNER: ______
DELIVERABLE (demoable): 2 guilds can complete a full war cycle on staging with real rewards
ACCEPTANCE CRITERIA:
  1. Full state cycle: signup, matchmaking, attack windows, resolution, rewards mail
  2. Telemetry events firing and visible on dashboard
  3. No blocker/major bugs open (severity per gamedev-qa-verifier)
  4. Reviewed by gamedev-reviewer, no open blockers
PACKAGES: P1..P14 with status
BUFFER: x days (held by producer)
DEMO: date, audience
```

## Risk register

```
ID | Category | Risk | Probability 1-5 | Impact 1-5 | Score | Owner | Trigger (risk becomes issue) | Mitigation (in progress) | Contingency (if triggered) | Status | Last reviewed
```

Categories to scan each review: scope, technical, platform/store policy, content throughput, people (key-person, burnout), vendor, live operations, legal/regulatory (loot boxes, minors, data), market (competitor launch, UA cost), dependencies on platform teams. Score 15+ is escalated in the status report.

Common game risks to seed the register:
- Store rejection (odds disclosure, IAP rules, age rating)
- Platform deadline missed (target API level, billing library version, page-size support) (as of 2026-10; verify)
- Min-spec device cannot hold frame/memory budget
- Event content throughput below calendar demand
- Single engineer owns the economy or backend (bus factor 1)
- Third-party service shutdown or acquisition (hosting, experimentation vendor)
- Soft-launch geo CPI not representative of target market

## Cut line

```
| Item | MoSCoW | Owner | Cost (days) | KPI impact if cut | Decision date | Status |
MUST    = the gate cannot be evaluated without it
SHOULD  = measurable KPI loss if cut, but gate still evaluable
COULD   = quality-of-life or polish
WON'T   = explicitly not this stage (written down so it is not re-litigated)
Rule: when a date is at risk, cut from the bottom upward and record it here. Moving the gate date requires sign-off from whoever signed the stage plan.
```

## Vendor statement of work (SOW) checklist

- [ ] Scope as a list of deliverables with counts (e.g., 40 decor items, 3 LODs each)
- [ ] Reference pack: style bible, naming conventions, technical budgets (polys, texture sizes, formats)
- [ ] Pilot batch (5–10% of volume) with acceptance criteria and review turnaround
- [ ] Review cadence and named reviewer on our side
- [ ] Acceptance criteria per deliverable; rejection and rework terms
- [ ] Payment per accepted batch
- [ ] IP assignment, confidentiality, data access limits
- [ ] Tool and file-format requirements; delivery location
- [ ] Escalation contacts and SLA for questions
- [ ] Exit clause and handover of source files

## Stakeholder status report

```
PROJECT: ______   STAGE: ______   WEEK x of y   DATE: ______
OVERALL: GREEN | AMBER | RED   (graded against gate date and gate KPIs, not effort)

1. DECISIONS NEEDED
   - Decision, options, recommendation, decider, needed by
2. GATE KPIs
   | Metric | Gate | Last | Trend | Comment |
3. DELIVERED THIS PERIOD (accepted deliverables only)
4. NEXT PERIOD
5. TOP RISKS (score, change, mitigation status)
6. SCOPE CHANGES (added / cut, with reason)
7. TEAM AND VENDORS (headcount, open roles, vendor batch status)
8. LIVE (if live): incidents, crash-free sessions, events shipped vs planned
```

## Retro format (after milestone or incident)

```
WHAT HAPPENED (facts, timeline)
WHAT WENT WELL
WHAT HURT
ROOT CAUSES (process, not people)
CHANGES (max 3, each with owner and due date)
```
