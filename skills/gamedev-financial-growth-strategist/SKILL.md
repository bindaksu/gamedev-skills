---
name: gamedev-financial-growth-strategist
description: >-
  Run the money side of a mobile game: unit economics (CPI, LTV, ARPDAU, ROAS
  at D7 to D365, payback), retention-curve LTV models, UA scaling and creative
  testing, channel mix and marginal ROAS, soft-launch KPI gates and greenlight
  or kill calls, P&L with platform and webshop fees, DAU and revenue
  forecasting, portfolio and reskin strategy, and privacy-era measurement with
  ATT, SKAN, AdAttributionKit, MMM and incrementality. Use when asked whether a
  game can scale, what CPI is affordable, how long payback takes, whether to
  kill or launch after soft launch, how to build a P&L or forecast, or how to
  allocate a UA budget.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: growth-business
---

# Financial Growth Strategist

A mobile game is a cohort-financing machine. You pay for installs today and get paid back over months, so the business is the spread between what a player is worth and what they cost — measured at the margin, not the average — multiplied by how much volume you can buy at that spread, minus a team that costs the same whether the spread is positive or not. Three numbers decide almost everything: the shape of the retention curve (it sets lifetime days), net ARPDAU by cohort age (it sets value per day), and the marginal CPI curve (it sets how far you can scale). Revenue charts mislead because trackers mix gross and net and miss webshops; average ROAS misleads because the last dollar is always worse than the first; and soft-launch dashboards mislead because cheap tier-3 installs flatter every metric except the one that matters. Model it, then let the model kill games early.

## Role Profile

At a top-grossing studio this work sits with the game's GM or franchise owner (the P&L holder), a central UA and marketing-science team, and finance/BI. Leadership is a GM or "franchise" owner rather than a director hierarchy, and UA plus creative production usually sit centrally beside a shared live-ops and data platform (companies research synthesis: Scopely Playgami, Playtika Boost, Supercell MAKE).

- **Responsibilities.** Own payback and scale targets, set CPI and ROAS bids by channel and geo, run soft-launch gates and the greenlight/kill decision, build the P&L and forecasts, and allocate the UA budget across a portfolio. Senior live-game PMs at Supercell carry "P&L-level ownership" of their LiveOps and monetization area.
- **Practice signals.** Scopely used Monopoly GO's soft launch to pre-train UA channels such as Moloco's ML models (https://moloco.com/case-studies/scopely-monopoly-go). Century Games runs AI- and ROAS-driven UA and reuses proven 4X systems across titles (https://naavik.co/digest/century-games-4x-portfolio-strategy/). Supercell has killed 30+ games against 5 hits in 12 years (https://mobidictum.com/supercell-ceo-ilkka-paananen-talks-about-nfts-and-why-they-kill-so-many-games/).
- **Hard skills.** Cohort modeling, SQL, spreadsheet and Python forecasting, UA bidding and creative analytics, MMP/SKAN/AAK data, MMM and incrementality design, P&L construction.
- **KPIs.** ROAS at D7/D30/D90 against target, payback day, marginal ROAS, contribution margin, UA spend scale at target ROAS, revenue per employee.
- **Collaborators.** UA and creative teams, data science, monetization, growth, LiveOps, finance, producer.

## When to Use / Not

Use for: LTV and ROAS modeling, CPI affordability, payback, UA budget and channel allocation, creative testing cadence, soft-launch gates and kill calls, P&L and fee modeling, DAU/revenue forecasts, portfolio and reskin strategy, measurement under ATT and AAK.

Not for: fitting or diagnosing the retention curve (if installed, `game-playtest-analyst`); retention levers (`gamedev-growth-designer`); offer and pricing design (`gamedev-monetization-designer`); economy math (if installed, `game-economy-balancer`); event pipelines, attribution joins and experiment stats (`gamedev-analytics-engineer`); milestone planning and team staffing (`gamedev-producer`).

## Inputs to Gather

- **Cohort retention** by install week, platform, country tier and channel: D1, D3, D7, D14, D30, D60, D90+. Missing: fit a power law from what exists and label all downstream numbers as projections.
- **ARPDAU by cohort age**, split IAP gross, ads and webshop. Missing: assume flat ARPDAU (conservative) and show a rising-ARPDAU sensitivity.
- **Fee status:** platform mix, small-business or subscription rates, webshop share and its cost.
- **CPI by channel and geo, and spend at each CPI** (the spend curve). Missing: use heuristic CPI ranges below and say so.
- **Payback target and cash runway** — they set the D7 ROAS target and the maximum scale.
- **Team cost** (fully loaded monthly) and fixed costs (servers, tools, outsourcing).
- **Organic uplift** from growth (k-factor, store features) — counted once.
- **Measurement stack:** MMP, SKAN/AAK conversion-value schema, ATT prompt strategy, MMM or incrementality tests in place.

## Method

1. **Normalize revenue to net.** IAP net = gross × (1 − effective store fee); ad revenue is already net of the network; webshop net = gross minus processing, tax handling and fraud. Every LTV and ROAS in the model uses the same basis — mixing gross LTV with spend is the most common ROAS overstatement.
2. **Fit retention and compute lifetime days.** Use the power-law fit (method in `game-playtest-analyst`) on all observed days, not only D1/D7; compute `L(D)` below. Re-fit weekly as cohorts mature.
3. **Model ARPDAU by cohort age.** Retained players monetize more over time; measure it per cohort day. Flat ARPDAU understates LTV and is the safe default until D90 data exists.
4. **Compute LTV and ROAS curves** at D7, D30, D90, D180, D365 per channel and geo.
5. **Derive the D7 ROAS target from the payback target.** From mature cohorts, compute the multiplier `M = LTV(payback day) ÷ LTV(7)`; target D7 ROAS = 1 ÷ M. Bid on early signals, judge on matured ones.
6. **Allocate budget on marginal, not average, ROAS.** For each channel/geo, measure installs at successive spend levels; marginal CPI = Δspend ÷ Δinstalls. Stop scaling where marginal ROAS at the payback horizon reaches 100%, then move budget to the channel with the best marginal ROAS.
7. **Run creative testing as the main lever.** Audience targeting is now algorithmic on every major network; creative is what you control. Keep a weekly test cadence, rotate before fatigue, and judge creatives on IPM first and ROAS second.
8. **Gate soft launch in stages** (technical → retention → monetization → scale) with written thresholds before entry; kill or pivot if a stage fails twice after iterations.
9. **Build the P&L** from gross bookings to contribution and EBITDA; check revenue per employee against benchmarks.
10. **Forecast DAU and revenue** as installs × retention convolution, by channel and geo, with low/base/high cases.
11. **Decide portfolio moves**: reskin or extend a proven loop before inventing one; greenlight new games only through the gates.
12. **Triangulate measurement**: MMP for consented users, SKAN/AAK for iOS aggregates, MMM for budget split, incrementality tests for truth.

## Deliverables

### 1. Unit Economics Sheet

```
COHORT: install wk __  GEO: __  PLATFORM: __  CHANNEL: __
Retention:   D1 __  D3 __  D7 __  D14 __  D30 __  D90 __   fit: R1 = __  b = __
ARPDAU net:  d0–7 $__  d8–30 $__  d31–90 $__  d91+ $__   (basis: net of __% store fee, ads net, webshop net)
Lifetime days L(D):  D7 __  D30 __  D90 __  D180 __  D365 __
LTV(D):              D7 $__ D30 $__ D90 $__ D180 $__ D365 $__
CPI $__   ROAS(D):   D7 __% D30 __% D90 __% D180 __% D365 __%
Payback day: __   Multiplier M = LTV(payback target) / LTV(7) = __   D7 ROAS target = __%
```

### 2. Soft-Launch Gate Sheet

```
STAGE        │ GEOS                       │ ENTRY │ EXIT THRESHOLDS (write before entry)                 │ MAX DURATION │ RESULT
Technical    │ cheap-CPI, stable networks │       │ crash-free ≥ 99.5% sessions, load time, D1 ≥ __      │ 4–8 wk       │
Retention    │ + tier-1 proxy (CA/AU/NZ)  │       │ D1 ≥ __  D7 ≥ __  D30 ≥ __ (genre gate)              │ 8–16 wk      │
Monetization │ tier-1 proxy               │       │ ARPDAU ≥ __  payer% ≥ __  D7 ROAS ≥ __ at CPI __     │ 8–16 wk      │
Scale test   │ US/UK/DE small spend       │       │ marginal CPI at $__/day ≤ __; payback ≤ __ days      │ 4–8 wk       │
Kill rule: a stage failed twice after iteration → kill or pivot memo within 2 weeks.
```

### 3. P&L Template (monthly)

```
Gross bookings        IAP store $__ + webshop $__ + ads $__       = $__
− Store fees          IAP store × __% (blend of 30/15)             = $__
− Webshop costs       webshop × __% (processing, MoR/tax, fraud)   = $__
= Net revenue                                                       = $__
− UA spend            (__% of net revenue)                         = $__
− Hosting, tools, SDK fees                                          = $__
= Contribution margin                                               = $__  (__%)
− Team (headcount __ × loaded $__)                                  = $__
− Outsourcing, marketing (non-UA), G&A                              = $__
= EBITDA                                                            = $__  (__%)
Revenue per employee (annualized net) = $__
```

### 4. Budget Allocation Table

```
CHANNEL / GEO │ Spend/day │ Installs │ Avg CPI │ Marginal CPI (last step) │ LTV(payback) │ Avg ROAS │ Marginal ROAS │ Action (+/−/hold)
```

### 5. Forecast

```
Month │ Installs paid │ Installs organic │ DAU (convolution) │ ARPDAU net │ Net revenue │ UA │ Contribution │ Cum. cash
Cases: low (CPI +20%, R −10%) / base / high (CPI −10%, ARPDAU +10%)
```

## Quantitative Reference

### LTV from a fitted retention curve

```
R(0) = 1,   R(d) = R1 · d^(−b)                          (fit R1, b from cohort data)
L(D) = Σ_{d=0..D} R(d) ≈ 1 + R1 · [ (D^(1−b) − 1)/(1−b) + (1 + D^(−b))/2 ]
LTV(D) = Σ_{d=0..D} R(d) · ARPDAU_net(d)    = ARPDAU_net · L(D) if flat
ROAS(D) = LTV(D) / CPI
Payback day = min D such that LTV(D) ≥ CPI
DAU(t) = Σ_s installs(s) · R(t − s)      → constant installs I: DAU(t) = I · L(t)
Marginal CPI = Δspend / Δinstalls;  marginal ROAS(D) = LTV(D) / marginal CPI
```

The closed form agrees with the day-by-day sum to within 0.1 lifetime days for b between 0.3 and 0.7. A power law over-predicts very late days for games that run out of content; cap the horizon at the content you have or switch to a fitted exponential tail after D90.

### ROAS milestones and multipliers (heuristic)

| Payback target | Typical D7 ROAS needed | Typical D30 ROAS needed | Fits |
| --- | --- | --- | --- |
| 90 days | 25–35% | 50–70% | Hybrid-casual, ad-heavy |
| 180 days | 15–25% | 35–55% | Casual puzzle, board |
| 365 days | 8–15% | 25–40% | 4X, mid-core RPG with deep D365 |

Derive your own multiplier from mature cohorts; these are planning priors only.

### CPI by genre (heuristic, US, blended platforms, as of 2026-10; verify against your own spend)

| Genre | iOS CPI | Android CPI |
| --- | --- | --- |
| Hypercasual | $0.40–1.00 | $0.20–0.60 |
| Hybrid-casual | $1–3 | $0.60–2 |
| Puzzle / match-3 | $3–7 | $1.50–4 |
| Casual board / social | $3–8 | $2–5 |
| Mid-core RPG / gacha | $5–12 | $3–8 |
| 4X / SLG | $8–20+ | $4–12 |

Tier-2/3 geos are often 3–10× cheaper and monetize correspondingly less; never mix them into a tier-1 ROAS.

### Channels (as of 2026-10; verify product names and features)

| Channel | Strength | Watch |
| --- | --- | --- |
| Meta (app campaigns) | Scale, broad audiences, value optimization | Creative fatigue fast; iOS signal loss |
| Google App Campaigns | Search + YouTube + Play inventory, Android depth | Little placement control |
| AppLovin (AppDiscovery) | In-game inventory, strong ROAS bidding for games | Concentration risk on one network |
| Unity Ads / LevelPlay network | In-game inventory, casual audiences | Quality varies by placement |
| Moloco, Mintegral, other DSPs | Programmatic scale, ML bidding | Needs volume to learn |
| TikTok | Younger audiences, creative-led | Native-feeling creative required |
| Apple Ads | High intent on App Store search; postbacks via AAK from iOS 26.2 (https://support.appsflyer.com/hc/en-us/articles/34395758837137-Bulletin-Apple-Ads-now-supports-SKAN-attribution) | Limited volume; brand-term cannibalization |

### Creative testing (heuristic)

- Test velocity: scaling games test tens of new concepts per month per major network; the hit rate for a concept that beats control is commonly 5–15%.
- Metrics funnel: thumb-stop/hook rate → CTR → IPM (installs per mille) → D7 ROAS. Kill on IPM early; promote on ROAS.
- Fatigue: winners commonly decay within 2–6 weeks; keep 2–3 challengers live behind every winner.
- Iterate on winners (hooks, first 3 seconds, end cards) before searching for new concepts.

### Soft-launch gates by genre (heuristic, tier-1-proxy geos)

| Genre | D1 | D7 | D30 | Other gate |
| --- | --- | --- | --- | --- |
| Match-3 / puzzle | 40%+ | 15%+ | 6%+ | D7 ROAS at projected CPI on target path |
| Casual board / social | 40%+ | 15%+ | 6%+ | Social-feature adoption |
| 4X / SLG | 35%+ | 15%+ | 7%+ | Payer % by D7; D30 ARPPU |
| Mid-core RPG / gacha | 40%+ | 18%+ | 8%+ | First-banner conversion |
| Hybrid-casual | 35%+ | 12%+ | 4%+ | Ad ARPDAU and D3 ROAS |
| Hypercasual (prototype test) | 35%+ | — | — | CPI under ~$0.50 on a creative test |

Durations are long at the top: Royal Kingdom spent 19 months in soft launch (https://www.pocketgamer.biz/dream-games-launches-royal-kingdom-worldwide-as-royal-match-nears-4-billion); Clash Mini was killed after 2+ years of soft launch; Monopoly GO took about 6 years from concept, including a full genre pivot. Lilith gates on retention and avoids short-term kills. Habby's soft launches earn real money: Archero 2 made $65.3m including soft launch against $32.8m in its first 30 days global (https://www.pocketgamer.biz/archero-2-makes-328m-in-first-30-days-from-player-spending).

### P&L benchmarks

- **Store fees:** 30% standard; 15% for Apple Small Business Program and Google's first $1M per year; 15% for Apple subscriptions after year one and Google subscriptions (as of 2026-10; verify). Jurisdictional link-out terms differ; see `gamedev-monetization-designer`.
- **Webshops:** FunPlus reports webshops above 25% of mobile revenue (https://funplus.com/info/chris-petrovic-predictions-for-2026/). Web costs are processing, merchant-of-record/tax and fraud — commonly high single to low double digits % of gross (heuristic). AppMagic figures are net of the store cut and exclude ads and webshop; Sensor Tower is gross IAP (https://mobilegamer.biz/the-top-grossing-mobile-games-of-2025/). Never compare your gross to their net.
- **UA as % of net revenue** (heuristic): 40–70% while scaling a new title, 15–35% for a mature evergreen.
- **Profitability anchor:** Supercell reported €2.65bn revenue and €932m EBITDA (~35%) for 2025 with 890 staff (https://www.pocketgamer.biz/supercell-revenue-declines-4-to-3bn-in-2025).
- **Revenue per employee** (mixed bases, so directional): Dream Games ~$5m/head, Supercell ~€3m/head, Playtika and Moon Active ~$0.8–0.9m/head (companies research synthesis). Small, senior teams on a mature platform win; headcount is no moat.

### Portfolio strategy

- **Reuse proven loops.** Century built Kingshot on Whiteout's core 4X systems, hero kits and events with a brighter casual skin; Naavik reports lower production cost and no observed cannibalization (https://naavik.co/digest/century-games-4x-portfolio-strategy/). Dream Games built on Toon Blast lineage; Habby repeats roguelite plus idle; Last War follows Top War.
- **Kill early and cheaply.** Fund many small prototypes, few soft launches, very few global launches. Write the kill gates before money is spent.
- **Budget for live.** A successful game's live team grows; plan headcount from contribution, not hope.

### Privacy-era measurement (as of 2026-10; verify)

- **ATT:** average opt-in among users shown the prompt was 38% in Q1 2026; gaming about 39% (https://www.adjust.com/blog/att-opt-in-rates-2025). Most iOS installs remain unattributed at user level.
- **AdAttributionKit** is the successor to SKAdNetwork 4; there was no SKAN 5. iOS 18.4 added configurable windows and overlapping re-engagement. SKAN is effectively frozen; deprecation timing is disputed (https://www.adjust.com/blog/wwdc-adattributionkit-2025/). Configure both SKAN and AAK postbacks.
- **Android:** Privacy Sandbox was retired in Oct 2025; GAID remains (https://engadget.com/cybersecurity/google-has-killed-privacy-sandbox-130029899.html).
- **Stack:** MMP for consented and Android users → SKAN/AAK conversion-value schema tuned to predict D7 value in the first 24–48 h → MMM for cross-channel budget → incrementality (geo holdouts, conversion lift) to calibrate both. When they disagree, trust incrementality for direction and MMM for split.

Read `references/forecast-and-gates.md` when building a full forecast model, a conversion-value schema, or an incrementality test plan.

## Worked Example — "Tile Harbor", match-3, US scale test

Measured: D1 40%, D7 17.7%, D30 9.6% → fit R1 = 0.40, b = 0.42. ARPDAU gross $0.30 = IAP $0.24 + ads $0.06. Blended store fee 27% → **net ARPDAU = 0.24 × 0.73 + 0.06 = $0.235**. CPI $3.50.

| Horizon | L(D) lifetime days | Net LTV (flat ARPDAU) | ROAS |
| --- | --- | --- | --- |
| D7 | 2.74 | $0.65 | 18% |
| D30 | 5.53 | $1.30 | 37% |
| D90 | 9.93 | $2.34 | 67% |
| D180 | 14.56 | $3.43 | 98% |
| D365 | 21.66 | $5.10 | 146% |

**Payback day 188** with flat ARPDAU. With ARPDAU rising with cohort age (`× (1 + 0.15 ln(1+d))`, 1.78× by D180), payback moves to **day 98** and D365 ROAS to 237% — which is why ARPDAU by cohort age must be measured, not assumed.

**D7 target.** M(180) = 14.56 / 2.74 = 5.3 → D7 ROAS target for 180-day payback = 1/5.3 = **18.9%**. Current 18.4% is on the line; any CPI rise breaks it.

**Marginal scale.** Spend $10k/day at CPI $3.00 (3,333 installs); $20k at average $3.60 (5,556); $40k at average $4.50 (8,889). Marginal CPI of the last step = $20k ÷ 3,333 = **$6.00** → marginal D365 ROAS = 5.10 / 6.00 = **85%** even though the average is 113%. Hold at ~$20k/day (marginal CPI $4.50, marginal D365 ROAS 113%) and spend the next dollar on creative testing, not bids.

**DAU and P&L at 5,000 paid installs/day:** DAU = 27.2k at month 1, 49.4k at month 3, 72.6k at month 6, ~108k at month 12. At month 12: net revenue ≈ 108.3k × $0.235 × 30 = **$764k/month**; UA = 5,000 × $3.50 × 30 = $525k → contribution $239k. A 40-person team at $12k loaded/month costs $480k → **EBITDA −$241k/month**. Unit economics are positive; scale is not enough. Decision: the game needs +30% ARPDAU (offers, webshop) or −20% CPI (creative) before scaling further — not more spend.

## Diagnostics

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| ROAS looks great, cash keeps falling | Gross LTV vs spend, or payback longer than runway | Rebuild on net; set payback ≤ runway |
| D7 ROAS on target, D90 misses | Early multiplier taken from a different genre/cohort | Recompute M from own mature cohorts |
| Scaling spend drops ROAS sharply | Average-ROAS bidding; marginal CPI rising | Allocate on marginal ROAS; cap channel at marginal 100% |
| CPI rising across all channels | Creative fatigue | Raise test velocity; iterate hooks on winners |
| Soft-launch metrics great, global launch weak | Tier-3 or proxy geos flattered retention/CPI | Gate on tier-1 proxy geos; run a scale test |
| Forecast DAU far above actual | Power-law tail over-predicting late days, or organics double-counted | Exponential tail after D90; count organics once |
| iOS ROAS invisible or erratic | ATT signal loss; poor conversion-value schema | Model iOS via SKAN/AAK + MMM; redesign schema to predict D7 value |
| Revenue benchmark gap vs charts | Comparing gross to AppMagic net, or ignoring webshop | Normalize bases before comparing |
| Positive unit economics, negative EBITDA | Volume too low for team size | Raise ARPDAU or lower CPI before adding spend; size team to contribution |

## Anti-Patterns

**The Gross ROAS** — LTV computed on gross bookings against net spend. Every bid is 30% too high.

**The Average Bidder** — scaling a channel because its average ROAS is above target while the last 30% of spend loses money.

**The Borrowed Multiplier** — a D7→D365 multiplier copied from a different genre. Mid-core multipliers applied to hybrid-casual fund a loss.

**The Tier-3 Mirage** — soft-launch KPIs from cheap geos used to approve a tier-1 launch.

**The Endless Soft Launch** — no written gates or maximum duration, so a game that will never pass burns a team for two years.

**The Double-Counted Organic** — UA claims organic uplift in its CPI and growth claims it again in its forecast.

**The Attribution Monotheist** — trusting one measurement source (MMP last-touch, or SKAN alone) for budget decisions in an ATT world.

**The Headcount Moat** — adding team ahead of contribution. Revenue per employee spans more than 5× across top studios; size follows margin.

## Quality Checklist

- [ ] All LTV, ROAS and P&L numbers on one stated basis (net of store fee, ads net, webshop net)
- [ ] Retention fit uses all observed days; R1, b and fit date recorded
- [ ] ARPDAU modeled by cohort age, with flat as the conservative case
- [ ] D7 ROAS target derived from own mature-cohort multiplier for the stated payback day
- [ ] Budget decisions use marginal CPI and marginal ROAS per channel/geo
- [ ] Creative test cadence, kill metric (IPM) and promote metric (ROAS) written down
- [ ] Soft-launch stages have thresholds and maximum durations written before entry
- [ ] Tier-1 proxy geos used for monetization and scale gates
- [ ] P&L runs gross bookings → fees → net → UA → contribution → team → EBITDA
- [ ] Forecast is an installs × retention convolution with low/base/high cases
- [ ] Organic uplift counted once
- [ ] iOS measurement triangulates SKAN/AAK, MMM and incrementality; ATT facts dated
- [ ] Every fee, policy or platform fact tagged with a date and marked to verify

## Related Skills

Cohort reading, retention fitting and the D30 residual check come from `game-playtest-analyst` (if installed); this skill turns the fit into money. Retention levers that change R1 or b are `gamedev-growth-designer`; offers, webshop design and pricing that change ARPDAU are `gamedev-monetization-designer`, with price-ladder math in `game-economy-balancer` (if installed). Event pipelines, attribution data joins, SKAN/AAK postback ingestion and experiment statistics are `gamedev-analytics-engineer`. Milestones, staffing and kill-gate governance coordinate with `gamedev-producer`; prototype kill criteria with `game-prototype-planner` (if installed). LiveOps cadence that drives late-cohort ARPDAU is `gamedev-liveops-designer`. For cross-discipline requests, start at `gamedev-coordinator`.
