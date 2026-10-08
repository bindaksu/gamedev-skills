# Offer Patterns

Read when designing a specific offer type. All value multipliers are heuristics; "base rate" means units per dollar at the bottom rung of the price ladder owned by `game-economy-balancer` (if installed).

## Sequencing rules

1. **One active "big" offer at a time.** Starter, event bundle and personalized offers compete; when two are live, the cheaper one cannibalizes the dearer one and both look weak in tests.
2. **First purchase changes the player.** After a first purchase, move the player to the payer track: suppress interstitials, switch personalization anchor to the purchase price, open recurring-value offers (pass, subscription).
3. **Never undercut the last purchase within 72 h.** A player who sees a better deal right after buying asks for a refund or stops buying at full value.
4. **Offer value must decay toward the shop rate over the lifecycle.** If day-90 offers are as rich as day-3 offers, nobody buys from the shop and offers become the price.
5. **Every offer has a reason.** Tie to a state (out of lives, queue full, event 80% complete) or a calendar moment (season start). A reasonless pop-up is noise.

## Pattern notes

### First-purchase bonus
- Doubles units on the first purchase of each rung. Simple, transparent, and pushes the player up one rung.
- Interaction: if the starter pack is cheaper and richer, the first-purchase bonus never fires. Decide which one is the entry point.

### Starter pack
- One-time, typically 48–72 h, priced at the bottom or second rung. Contents: hard currency + one accelerator the player has already used + one cosmetic or exclusive item.
- Trigger at the first genuine friction point. If shown on day 1, re-show once after the friction point for players who dismissed it.
- Measure: conversion among players who reached the trigger, not among all installs.

### Limited-time and event bundles
- Tie to event start (preparation) and to near-completion (the last push). Near-completion offers convert best because the desire is concrete.
- Timers must be real. If the bundle returns next event, do not say "never again".

### Personalized offers
- Inputs: payer tier, last purchase price, days since last purchase, current blockers, inventory.
- Rule-based first: anchor at last purchase price, propose a step up of 1–2×, never more than 3× for a single offer. ML ranking can choose contents within the price band.
- Caps: 1 per session, 3 per day, 24–48 h exclusion after any purchase.
- Log the rule or model version that fired for every impression; you will need it for audits and refunds.

### Endless offer
- A chain of tiles: free, paid, free, paid, with rising value. Claiming one reveals the next.
- Transparent version shows the next 2–3 tiles. Make clear when a free reward sits behind a paid step.
- Measure depth reached per payer tier; a chain nobody gets past step 3 is too steep.

### Piggy bank
- Hard currency accumulates as a by-product of play (e.g. a share of earnings per level). Breaking it costs a fixed price.
- Show the bank from day one with its break price so it reads as a savings product, not a trap. Cap the fill, then "full" becomes the trigger.

### Subscription / VIP
- Value is delivered daily (claim a drip), which builds a habit as well as revenue. Add quality-of-life perks (extra queue, auto-collect) over raw power.
- Show the cancellation path clearly. Subscription regulation on cancellation and renewal disclosure is tightening in several markets; check before launch.
- Apple reduces commission to 15% after a subscriber's first year; Google charges 15% on subscriptions (as of 2026-10; verify).

### Battle / season pass (value side)
- Show the premium track's total value at purchase as units and items.
- The median engaged player must finish the premium track before the season ends; if not, it is a deceptive offer, not a pass. Tier and XP sizing goes to `gamedev-liveops-designer`.
- Tier skips are a separate SKU; never require them to complete.

### Bundles and collections
- Bundles combine currency with items that cannot be bought separately; this hides unit price less if each component's value is listed.
- High-value collections (cosmetic sets, prestige items) are the sink for top spenders; extend before they exhaust it.

## Shop layout notes

- Above the fold: featured offer and limited-time items. Players scan the first screen and leave.
- Currency packs: exactly one "best value" badge. Optional "most popular" on the rung that actually is.
- Local-currency prices from the store APIs; never hard-code prices.
- Free daily claim creates a daily shop visit, which raises exposure to everything else.
- Hard-currency items: show the real-money equivalent where required and consider doing it everywhere.

## Ads in IAP games

- Rewarded first. Interstitials only after a monetization holdout shows no IAP or D7 loss.
- Suppress interstitials for payers, recent rewarded viewers and players in the first session.
- A "no ads" SKU priced at the bottom or second rung converts ad-sensitive players into payers; keep rewarded ads available after purchase because the player opts in.
