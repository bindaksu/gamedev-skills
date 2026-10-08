# Stage Gate Checklists

Read when preparing a gate review. Each stage lists evidence that must exist at the gate. A "no" on any MUST line means the gate fails or the stage is extended once with a narrower question. Numbers are [heuristic] unless sourced; soft-launch KPI thresholds come from gamedev-financial-growth-strategist.

## Concept gate

MUST
- [ ] One-sentence fantasy and 3–5 pillars
- [ ] Target audience and 3+ comparables with public revenue/downloads signals
- [ ] Why us: team has shipped or deeply played the genre
- [ ] Rough P&L envelope and UA cost assumption (gamedev-financial-growth-strategist)
- [ ] Riskiest assumption named, and the prototype that tests it (if installed, game-prototype-planner)
SHOULD
- [ ] Monetization model sketched (IAP, ads, hybrid) with comparables
- [ ] Platform and engine choice with reason

## Prototype gate

MUST
- [ ] Core loop playable on target device class, not only in editor
- [ ] Playtest evidence: replay intent, comprehension, session length (if installed, game-playtest-analyst)
- [ ] Kill criteria from the stage plan evaluated honestly and recorded
- [ ] Decision on prototype code: delete, harvest, or keep
SHOULD
- [ ] Meta layer sketched (gamedev-meta-progression-designer)
- [ ] Art direction exploration (if installed, game-asset-art-director)

## Vertical slice gate

MUST
- [ ] One full session at ship quality: FTUE start to first meta reward
- [ ] Measured content cost: person-days per level/event/hero, and resulting cost per hour of play
- [ ] Min-spec device runs at target frame rate and memory (gamedev-optimization-compatibility)
- [ ] Backend architecture chosen, build vs buy decided (gamedev-platform-server-architect)
- [ ] Analytics event taxonomy draft (gamedev-analytics-engineer)
SHOULD
- [ ] Economy ledger v1 (if installed, game-economy-balancer)
- [ ] Live-ops tooling plan: config-driven events

## Alpha / soft-launch readiness gate

MUST
- [ ] Content for the first 30 days of a median player
- [ ] FTUE funnel instrumented end to end
- [ ] Crash reporting with symbols; crash-free sessions measured on min tier
- [ ] IAP server-validated; refund handling; odds disclosure where randomized items are sold
- [ ] Remote config and kill switches on risky features
- [ ] At least 2 event templates operable without a client build
- [ ] Store compliance checklist passed (gamedev-qa-verifier)
- [ ] Soft-launch geo plan and KPI gates signed (gamedev-financial-growth-strategist)
SHOULD
- [ ] Localization for soft-launch geos
- [ ] Community and support channel ready

## Soft-launch exit (global greenlight)

MUST
- [ ] Retention and monetization at or above the signed gates for 2+ consecutive cohorts
- [ ] CPI measured in target geos; payback model closes within plan
- [ ] Live-ops cadence held for 8+ weeks without slips
- [ ] Load test passed at planned launch peak multiple (gamedev-live-serving)
- [ ] Phased release and rollback plan (gamedev-delivery-release)
KILL / PIVOT
- [ ] If retention plateaued after 2–3 major iterations: kill or pivot decision recorded. Precedents: Clash Mini killed after 2+ years of soft launch; Monopoly GO pivoted genre (see team-profiles in gamedev-coordinator)

## Live health review (quarterly)

- [ ] DAU, D30, ARPDAU, payer conversion trends vs plan
- [ ] Content cadence hit rate (events shipped on date / planned)
- [ ] QoL backlog size and age
- [ ] Crash-free sessions and incident count (gamedev-live-serving)
- [ ] Contribution margin after UA; sunset criteria evaluated
