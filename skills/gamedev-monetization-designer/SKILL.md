---
name: gamedev-monetization-designer
description: >-
  Design how a free-to-play game earns: IAP offer architecture (first purchase,
  starter packs, personalized, limited-time, endless offers, piggy banks), shop
  layout, subscriptions and VIP, battle pass value, gacha with odds disclosure
  and pity, ad placement and frequency caps, hybrid IAP plus ads, webshops and
  direct payments, and the ethics and loot-box regulation that bound all of it.
  Use when conversion or ARPPU is low, when designing a shop, offer or gacha,
  when adding ads to an IAP game, when planning a webshop, or when checking a
  monetization feature against loot-box, minors or dark-pattern rules.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: growth-business
---

# Monetization Designer

Players pay for one of four things: to go faster, to express themselves, to belong, or to keep something they would otherwise lose. Every offer you design sells one of those, at a moment when the player already wants it, to someone who already loves the game. Monetization that works is an offer architecture — who sees what, when, at what price anchor, and how often — sitting on an economy that makes the thing worth wanting. The math of that economy (ladders, curves, exchange rates, ad reward values) is not this skill's job; the sequencing, presentation, segmentation and the ethical and legal line are. That line has moved: regulators now treat confusing purchase flows, hidden odds and spending by minors as consumer-protection violations, not design choices, and a dark pattern that lifts revenue 5% can cost a nine-figure settlement.

## Role Profile

At a top-grossing studio this is the monetization or economy designer, or the PM who owns "LiveOps & Monetization" for a title.

- **Responsibilities.** "Price the game's virtual currencies", build simulations and predictive models of content changes, monitor player balances, design A/B tests (Moon Active Product Economy Manager: https://jobs.insightpartners.com/companies/moon-active/jobs/14935239-product-economy-manager). At Zynga the principal is the expert on "all economic aspects including features, live operations, and pricing" (https://builtin.com/job/director-economy-design-zynga/2550491). Supercell's Sr PM takes "full ownership and accountability" for monetization elements and is judged on "monetization performance" (https://hitmarker.net/jobs/supercell-senior-product-manager-live-ops-monetization-hay-day-2311776).
- **Hard skills.** Offer and pricing design, segmentation, A/B design, Excel simulation, SQL; Python at senior or technical-economy level.
- **KPIs.** Retention and revenue together (quoted in Moon Active postings), payer conversion, ARPPU, ARPDAU, offer conversion, refund and chargeback rates.
- **Context.** Monetization is moving off-store: FunPlus reports webshops above 25% of mobile revenue (source in `references/regulation-and-payments.md`), and Monopoly GO's webshop revenue is invisible to chart trackers. Web-commerce is now part of the role.
- **Collaborators.** Economy design, LiveOps, UI, data science, finance/BI, legal and platform/backend for receipts and refunds.

## When to Use / Not

Use for: offer architecture and sequencing, shop and store screen structure, personalization rules, subscription and VIP design, battle pass value proposition, gacha rates/pity/disclosure, ad placement and caps, hybrid monetization, webshop strategy, refund and regulatory review.

Not for: price ladder, cost curves, currency exchange rates, rewarded-ad reward value, pity tail math, spend-segment distributions (if installed, `game-economy-balancer`); pass tier and XP curves (`gamedev-liveops-designer`); shop visual design (`gamedev-ui-designer`); LTV, ROAS and the P&L impact of fees (`gamedev-financial-growth-strategist`); receipt validation and entitlement code (`gamedev-backend-engineer`); purchase fraud (`gamedev-anti-cheat-security`).

## Inputs to Gather

- **KPIs:** daily and monthly payer %, ARPPU, ARPDAU split IAP/ads, first-purchase day distribution, repeat-purchase rate. Missing: assume genre heuristics below and flag as unvalidated.
- **Economy artifacts:** price ladder, currency time values, what hard currency gates (from the economy owner). Without these, offer values are guesses.
- **Spend distribution** by segment and the top SKUs by revenue.
- **Genre and retention** — ad-led models only work with high volume and short sessions; IAP-led needs D30 depth.
- **Markets and audience age:** countries served, share of under-18s, platform mix. This determines which loot-box and minors rules apply.
- **Platform and payments setup:** store-only vs webshop, account system (webshops need account linking), refund handling.
- **Existing offers and calendar:** what fires, how often, overlaps with events.

## Method

1. **Decompose revenue before designing.** `ARPDAU = daily payer % × ARPPU(daily) + ad ARPDAU`. Low conversion and low ARPPU need opposite fixes — a bottom-rung offer versus a deeper ladder — so name which term is short.
2. **Choose the model mix by genre and retention.** IAP-led when D30 is deep and the economy has hard-currency gates; hybrid when sessions are short and conversion is low; ad-led only at hypercasual volume. Ads in an IAP game must be opt-in first (rewarded), interstitials last.
3. **Design the offer architecture as a ladder of commitment.** First purchase (remove the barrier) → starter pack (prove value) → recurring value (pass, subscription) → event offers (tied to desire spikes) → personalized and high-value offers (whales). Each step's job is to make the next one natural.
4. **Place the first offer at the first genuine friction point**, not on day 1. The timing and price band rules are in `game-economy-balancer`; this step picks the moment in the flow (first lost level with lives at 0, first build queue full, first hero that cannot be upgraded).
5. **Lay out the shop for scanning, not browsing.** Featured offer first, then time-limited, then currency packs, then the rest. Show value as units plus a bonus badge, never a fake "was" price.
6. **Personalize with rules, not just models.** Segment by payer tier, last purchase price and recency. Anchor the next offer near the last purchase price; step up gently. Cap pop-ups per session and per day so personalization does not become pressure.
7. **Sell the pass as a value proposition.** Premium must show its total value up front and be completable by the median engaged player; tier and XP sizing goes to `gamedev-liveops-designer`.
8. **Design gacha for trust.** Publish rates per item type before purchase, show the pity counter, state the real-money cost of the guarantee, and never let pity reset across banners silently. Pity tail math is in `game-economy-balancer`.
9. **Place ads where they do not cost IAP.** Rewarded at natural decision points; interstitials only at natural breaks and never for recent payers; banners only in ad-led games and never over the play area.
10. **Plan the webshop as a parallel channel**, with value pass-through to players, account linking, server-side fulfillment and refunds — and check the current rules for each storefront jurisdiction before linking out.
11. **Run a compliance pass on every feature** (see the Regulation table and `references/regulation-and-payments.md`), then A/B with retention guardrails. A monetization test that wins revenue and loses D30 is a loss at LTV.

## Deliverables

### 1. Offer Spec

```
OFFER ID / NAME:   ____
TYPE:              first-purchase / starter / limited-time / personalized / endless / piggy bank / bundle / subscription / pass
JOB:               [which barrier or desire it addresses]
TRIGGER:           [event or state, e.g. lives = 0 after loss on level 15+]
ELIGIBILITY:       [segment, payer tier, cooldown, max shows per day, excluded if purchased in last __ h]
CONTENTS:          [items and quantities]
PRICE:             $__ (store tier __)    VALUE: __× vs base shop rate (from economy ladder)
DURATION / LIMIT:  [timer — real, not resetting; purchase limit]
PRESENTATION:      [pop-up / shop slot / in-context]; dismiss always visible; no countdown faked
MINORS / REGION:   [suppressed for under-18 accounts? regions excluded?]
METRICS:           show→buy conversion, revenue/DAU, cannibalization of shop packs, D7 retention of buyers vs holdout
```

### 2. Offer Architecture Map

```
STAGE              │ OFFER(S)                 │ TRIGGER                   │ PRICE BAND │ VALUE × │ CAP
First purchase     │                          │ first friction point      │ $0.99–4.99 │         │ once
Starter            │                          │ day 1–3 after FP or gate  │ $2.99–9.99 │         │ once / 72 h
Recurring value    │ pass / sub / VIP         │ season start / day 7+     │            │         │
Event              │ event bundles            │ event start, near-finish  │            │         │ per event
Personalized       │ anchored to last price   │ recency + tier            │ 1–2× last  │         │ 1/session, 3/day
High value         │ whale bundles, collect.  │ tier 1 payers             │ $49.99+    │         │
Webshop            │ web-exclusive bonus      │ account-linked payers     │            │         │
```

### 3. Shop Layout Spec

```
SECTION ORDER:   1 Featured (one offer, rotating) 2 Limited-time (≤ 3) 3 Daily deals / free daily item
                 4 Currency packs (ladder, best-value badge on one rung) 5 Bundles 6 Cosmetics 7 Pass / VIP entry
PER TILE:        icon, units, bonus %, price in local currency, timer if limited, "best value" on max one tile
RULES:           no dark-pattern scarcity, no pre-checked boxes, no hidden currency conversion,
                 hard-currency price shown with its real-money equivalent where required
FREE ITEM:       one free daily claim in shop (habit + shop visit)
```

### 4. Gacha Disclosure Sheet

```
BANNER:          ____   DURATION: ____   PULL COST: __ hard (= $__ at bottom-rung rate)
RATES (per pull):  tier/item type │ base rate % │ featured share % │ shown in-game where (pre-purchase)
SOFT PITY:       starts at pull __, rate +__% per pull
HARD PITY:       guaranteed at pull __ → real-money cost to guarantee = __ pulls × $__ = $__
CARRY-OVER:      pity persists across banners? Y/N (state explicitly in UI)
DUPLICATES:      convert to ____ at ____
COUNTER UI:      visible on banner screen: Y
REGIONS:         sold for real money in: ____   disabled / earned-only in: ____
AGE:             under-__ requires ____
```

### 5. Ad Placement Plan

```
FORMAT       │ PLACEMENT               │ FIRST ELIGIBLE           │ MIN GAP │ CAP/SESSION │ CAP/DAY │ SUPPRESSED FOR
Rewarded     │ continue, double reward │ day 1                    │  —      │             │ see economy │ —
Interstitial │ level end, mode exit    │ level __ / session __    │ __ s    │ __          │ __      │ payers (__ d), first session
Banner       │ menu bottom, safe area  │                          │         │             │         │ in gameplay, payers
NO-ADS SKU:  removes interstitial + banner; rewarded stays (player-opt-in)
```

## Quantitative Reference

### KPI bands by genre (heuristic, gross, tier-1 heavy mix)

| Genre | Monthly payer % | ARPDAU (IAP + ads) | IAP share | Notes |
| --- | --- | --- | --- | --- |
| Match-3 / puzzle | 2–5% | $0.15–0.60 | 85–95% | Top titles above band |
| Casual board / social | 3–6% | $0.40–1.00+ | 90%+ | Webshop not in chart data |
| 4X / SLG | 3–8% | $0.50–1.50 | 95%+ | Whiteout ~$1.21, Kingshot ~$1.45 (Naavik, 2025 YTD: https://naavik.co/digest/century-games-4x-portfolio-strategy/) |
| Mid-core RPG / gacha | 3–7% | $0.30–1.20 | 90%+ | Banner-driven spikes |
| Hybrid-casual | 1–3% | see `game-economy-balancer` | 30–60% | IAP + rewarded + interstitial |
| Hypercasual | under 1% | see `game-economy-balancer` | under 10% | Ad-led |

All heuristics from practitioner benchmarks except the sourced 4X anchors; ad-led ARPDAU bands live in `game-economy-balancer` (if installed). Daily payer % is roughly a tenth to a twentieth of monthly payer % in IAP-led games. Compare like with like: gross vs net of store fee, and with or without webshop revenue.

### Offer patterns (value multipliers are heuristic; compute "base rate" from the economy ladder)

| Pattern | Mechanic | Typical value vs base rate | Watch-outs |
| --- | --- | --- | --- |
| First-purchase bonus | 2× units on first buy of each rung | 2× | Must not compete with starter pack |
| Starter pack | One-time, time-limited, mixes currency + accelerator + cosmetic | 5–10× | Shown after the player knows what the items do |
| Limited-time event bundle | Tied to event start or near-completion | 2–4× | Real timers only; no auto-renewing "last chance" |
| Personalized | Price anchored to last purchase; step up 1–2× | 2–4× | Cap frequency; log the rule that fired for audits |
| Endless offer | Chain of steps alternating free and paid; each claim unlocks next | 3–6× across chain | Free steps are the hook — do not make paid steps mandatory to see free ones without saying so |
| Piggy bank | Hard currency accumulates from play; break for a fixed price | 3–6× | Show fill and break price from the start |
| Subscription / VIP | Daily drip + perks; $4.99–14.99/month | 3–5× over the month | Clear cancel path; drip must be claimed daily (habit) |
| Battle / season pass premium | $4.99–9.99, premium track value shown | 5–10× if completed | Value only real if median engaged player completes |

Full pattern notes with sequencing and anti-cannibalization rules: read `references/offer-patterns.md` when designing a specific offer type.

### Platform fees (as of 2026-10; verify)

Standard store commission is 30% on IAP. Apple: 15% under the Small Business Program (under $1M prior-year proceeds) and 15% on auto-renewing subscriptions after the first year. Google Play: 15% on the first $1M of annual earnings and 15% on subscriptions. Jurisdiction-specific alternative billing and link-out terms differ (US, EU, Japan, South Korea) — read `references/regulation-and-payments.md` and verify current terms before modeling.

### Ads (frequency heuristics)

- **Interstitials:** none in the first session; first one after level 5–10 or day 2; minimum 90–120 s between; never mid-action, never right after a purchase or a rewarded view. Suppress for any payer for 7–30 days.
- **Banners:** only in ad-led or hybrid games, outside the play area, inside safe areas; adaptive sizes.
- **Rewarded:** opt-in at decision points (continue, double, extra spin). Reward value and caps are set by `game-economy-balancer`.
- **Mediation:** AppLovin MAX, Unity LevelPlay and Google AdMob are the common stacks; run bidding, not waterfalls, where available. Verify SDK versions against store target-API and privacy-manifest requirements.
- **Hybrid guardrail:** if interstitials lower IAP conversion or D7 in a holdout, the ad revenue is borrowed from IAP.

### Gacha and loot boxes

- Apple guideline 3.1.1 requires apps selling loot boxes or other randomized virtual items to disclose the odds of each item type before purchase (https://www.fenwick.com/insights/publications/apple-now-requires-disclosure-of-loot-box-odds). Whether this covers boxes bought with earned currency is ambiguous; disclose anyway.
- Hard pity is the norm in gacha (Genshin Impact's 5-star guarantee at 90 pulls is the reference point players compare against). Soft pity raises rates in the last 10–20% of the pity window.
- Show the cost of the guarantee in real money. If you cannot write that sentence without discomfort, the pity is set too high.
- Regional rules (Belgium, Netherlands, South Korea, China, Japan, Australia, Brazil, US FTC) are summarized below and detailed in the reference file.

### Regulation snapshot (as of 2026-10; verify)

| Jurisdiction | Position |
| --- | --- |
| Belgium | Gaming Commission (2018) treats paid loot boxes as gambling; disable paid random items for Belgian users |
| Netherlands | Council of State (2022) overturned the regulator's fine on EA's FIFA packs; check for newer legislation |
| South Korea | Probability disclosure legally mandatory since March 2024 |
| China | Odds disclosure required; daily draw limits and minors' playtime limits apply |
| Japan | "Kompu gacha" (complete-the-set gacha) prohibited since 2012 |
| Australia | Since Sept 2024, games with paid loot boxes rated at least M; simulated gambling R18+ |
| Brazil | 2025 child-protection law restricts loot boxes in games accessible to minors; check effective date |
| US (FTC) | Epic 2022: $520m total — $275m COPPA penalty and $245m refunds over dark-pattern purchases. HoYoverse 2025: $20m and limits on loot-box sales to under-16s |
| UK | No loot-box legislation; industry principles instead |

### Refunds and minors

- Listen to App Store Server Notifications (REFUND, CONSUMPTION_REQUEST) and the Google Play Voided Purchases API; revoke entitlements server-side, and answer Apple consumption requests honestly.
- Track refund rate per SKU; a SKU with a refund rate several times the game average is usually confusing, not fraudulent.
- For accounts flagged under 18 (or under 13 in COPPA scope): no personalized high-value offers, no paid random items in restrictive regions, spend limits, and parental controls respected.

## Diagnostics

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Conversion low, ARPPU high | No low-barrier entry | First-purchase bonus + $0.99–4.99 offer at first friction point |
| Conversion fine, ARPPU low | Ladder too short, no recurring value | Pass/subscription; extend high-value bundles (ladder depth via economy) |
| Starter pack converts poorly | Shown before the player values its contents | Move trigger to first friction; show what each item does |
| Personalized offers lift revenue, D7 drops | Frequency pressure | Cap 1/session, 3/day; exclude recent buyers for 24–48 h |
| Shop visits low | Nothing new to see | Free daily claim, rotating featured, daily deals |
| Pass attach high, renewal low | Premium track not completable | Retune XP with LiveOps; show progress to completion |
| Gacha spend spikes then reviews tank | Pity too high or hidden; unclear rates | Visible counter, lower hard pity, real-money cost displayed |
| Interstitials up, IAP conversion down | Ads hitting would-be payers | Suppress for payers and engaged non-payers; later first ad |
| Refund rate high on one SKU | Misleading contents or accidental purchase | Clarify contents; add confirmation; check minors |
| Webshop share flat | No reason to switch or friction to link | Web-exclusive bonus value; one-tap account link |
| Revenue concentrated in a few spenders, they plateau | Content ceiling for whales | High-value collections/cosmetics; ladder extension via economy |

## Anti-Patterns

**The Day-One Paywall** — the starter pack fires in the first session, before the player knows what anything is worth. It sells to nobody and teaches everyone to dismiss pop-ups.

**The Fake Clock** — countdowns that reset or "last chance" offers that recur weekly. Players learn the timers lie; regulators call it deceptive.

**The Pop-up Gauntlet** — three offers between the player and the play button. Session starts drop and the offers stop converting.

**The Hidden Odds** — rates disclosed only on a web page or not per item type. Store violation, regulatory exposure, and the review that defines the store page.

**The Pity Reset** — pity silently reset when a banner ends. It reads as theft the moment a player notices.

**The Interstitial on a Payer** — showing forced ads to a player who just spent money. You trade dollars of IAP for cents of ad revenue.

**The Currency Fog** — prices shown only in hard currency, several conversions removed from money, to obscure spend. The FTC's 2025 HoYoverse case cited confusing virtual-currency pricing (as of 2026-10; verify).

**The Minor Blind Spot** — personalized high-value offers and paid random items shown to accounts that are, or are likely to be, children.

## Quality Checklist

- [ ] Revenue decomposed into payer %, ARPPU and ad ARPDAU; the short term named
- [ ] Offer architecture covers first purchase → starter → recurring → event → personalized → high value
- [ ] First offer triggered at a named friction point, not first launch
- [ ] Every offer spec has trigger, eligibility, cooldown, daily cap, real timer, visible dismiss
- [ ] Offer values derived from the economy ladder, not set by feel
- [ ] Shop: one "best value" badge maximum, no fake strikethrough prices, free daily claim present
- [ ] Pass premium value shown up front and completable by the median engaged player
- [ ] Gacha: rates per item type pre-purchase, visible pity counter, real-money cost of guarantee stated, carry-over rule stated
- [ ] Paid random items disabled or altered per region (Belgium at minimum); minors rules applied
- [ ] Interstitials absent from first session, gapped, suppressed for payers; banners never over play area
- [ ] Refund notifications handled server-side with entitlement revocation
- [ ] Webshop plan checked against current storefront rules per jurisdiction, with account linking and server fulfillment
- [ ] Every monetization test has D7/D30 retention and refund-rate guardrails
- [ ] Every jurisdictional statement tagged with a date and marked for legal verification

## Related Skills

All numeric economy work — price ladder, currency time value, rewarded-ad reward caps, pity tail math, spend-segment ceilings — goes to `game-economy-balancer` (if installed); this skill consumes its outputs. Pass tiers, XP curves and the event calendar that offers attach to are `gamedev-liveops-designer`; collection and roster sinks for high spenders are `gamedev-meta-progression-designer`. Shop and offer screens are drawn by `gamedev-ui-designer`, with honest paywall UX guidance in `mobile-game-ux-designer` (if installed). LTV impact, fee modeling and webshop P&L go to `gamedev-financial-growth-strategist`; offer telemetry, test assignment and guardrails to `gamedev-analytics-engineer`. Receipt validation, entitlement grants, refund revocation and webshop fulfillment are `gamedev-backend-engineer`, with fraud and chargeback abuse in `gamedev-anti-cheat-security`. StoreKit 2 and Play Billing specifics belong to `gamedev-ios-engineer` and `gamedev-android-engineer`. Retention side effects of offers (win-back bundles, streak repair) coordinate with `gamedev-growth-designer`.
