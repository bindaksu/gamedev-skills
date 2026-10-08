# Regulation and Payments Reference

Read when shipping a paid random item, a webshop or link-out, a feature visible to minors, or when answering "is this legal in market X". Everything here is a design-time summary, **not legal advice**, and every row is tagged (as of 2026-10; verify). Laws, court orders and store terms in this area change several times a year; confirm with counsel and the current store guidelines before launch.

## Loot boxes and paid random items

| Jurisdiction | Rule or position | Design response |
| --- | --- | --- |
| Apple App Store (global) | Guideline 3.1.1: disclose odds of each item type before purchase (https://www.fenwick.com/insights/publications/apple-now-requires-disclosure-of-loot-box-odds) | Rates screen reachable from the purchase screen; per item type |
| Google Play (global) | Policy requires odds disclosure for randomized items bought with real money or in-app currency (as of 2026-10; verify) | Same rates screen on both platforms |
| Belgium | Gaming Commission (2018) treats paid loot boxes as gambling under the gambling act (as of 2026-10; verify) | Disable real-money and hard-currency random items for Belgian users; earned-only or direct purchase |
| Netherlands | Council of State (March 2022) overturned the regulator's penalty on EA's FIFA Ultimate Team packs; political pressure for a ban continues (as of 2026-10; verify) | Treat as moving; geo-flag random items so they can be switched off |
| South Korea | Probability disclosure became a legal obligation in March 2024 under the Game Industry Promotion Act (as of 2026-10; verify) | Full rates, including pity and enhancement probabilities, in Korean |
| China | Odds disclosure required; draw-count disclosure; minors' playtime and spend limits (as of 2026-10; verify) | Separate China build rules; minors' spend caps |
| Japan | Kompu gacha (set-completion gacha) prohibited since 2012 under premiums law guidance (as of 2026-10; verify) | Never reward completing a set of random items with a further item |
| Australia | Since 22 Sept 2024 classification: paid loot boxes → minimum M; simulated gambling → R18+ (as of 2026-10; verify) | Check the rating impact before shipping random items |
| Brazil | 2025 child-protection law (ECA Digital) restricts loot boxes in games aimed at or accessible to minors (as of 2026-10; verify effective date and scope) | Age-gate random items in Brazil |
| United Kingdom | No loot-box legislation; industry principles (2023) on age assurance and spending controls (as of 2026-10; verify) | Follow the principles; parental spend controls |
| PEGI / ESRB | Content descriptors for in-game purchases including random items (as of 2026-10; verify) | Declare accurately at rating time |

## Consumer protection and dark patterns (US focus)

- **FTC v. Epic Games (Dec 2022)**: $520m total — $275m civil penalty for COPPA violations (default voice/text chat on for children, collecting children's data) and $245m in refunds for dark patterns that caused unintended purchases and for locking accounts of users who disputed charges (as of 2026-10; verify). Design lessons: one-press purchase without confirmation is risky; never punish a chargeback by locking paid content without process; default children's chat off.
- **FTC and HoYoverse (Genshin Impact, Jan 2025)**: $20m settlement; restrictions on selling loot boxes to under-16s without parental consent; requirements around odds and real-money exchange-rate disclosure (as of 2026-10; verify). Design lesson: show the real-money cost of random items and pity.
- **COPPA** applies to under-13s in the US: verifiable parental consent before collecting personal data; affects analytics, ads personalization and chat.

## Storefronts, link-outs and webshops

| Market | Situation | What to verify |
| --- | --- | --- |
| US, iOS | April 2025 district-court order in Epic v. Apple barred Apple from charging commission on purchases made through external links from US storefront apps and from restricting link and button design (as of 2026-10; verify appellate status) | Current US guideline text; whether any commission has been reinstated on appeal |
| US, Android | Epic v. Google injunction requires Play to permit alternative billing and links in the US (as of 2026-10; verify current fee terms and any settlement) | Google's current US external-offers terms |
| EU | Digital Markets Act: Apple and Google offer EU-specific alternative payment and link-out terms with their own fee schedules (as of 2026-10; verify current schedules) | Current EU terms; they have changed more than once |
| Japan | Mobile Software Competition Act in force from Dec 2025, opening alternative payments (as of 2026-10; verify) | Apple and Google Japan-specific terms |
| South Korea | Alternative in-app payment required by law since 2021, with a reduced commission (as of 2026-10; verify) | Current reduced rate |
| Rest of world | Standard store billing for in-app digital goods | Store guidelines |

### Webshop economics (structure, not quotes)

```
Gross web price
 − payment processing (card / wallet / local methods)
 − merchant-of-record or tax/VAT handling (if using a MoR vendor)
 − fraud and chargeback losses
 − platform link-out commission (where any applies)
 = net web revenue   → compare with store net (70% or 85%)
```

All-in web costs are commonly a high-single-digit to low-double-digit percentage of gross (heuristic; get vendor quotes). Pass part of the saving to players as bonus value (often 10–20% extra units) — the player needs a reason to leave the app.

Requirements: account system with one-tap linking, server-side fulfillment by account ID, idempotent grants, refund and chargeback revocation, tax by buyer country, age checks matching in-app rules. FunPlus reports webshops above 25% of mobile revenue (https://funplus.com/info/chris-petrovic-predictions-for-2026/); chart trackers (AppMagic, Sensor Tower) exclude webshop revenue, so benchmarks understate webshop-heavy games.

## Refunds

- **Apple:** App Store Server Notifications V2 send `REFUND` and `CONSUMPTION_REQUEST`. Respond to consumption requests with accurate data; revoke the granted items server-side on refund. Server verification uses the App Store Server API with JWS; receipt validation is legacy.
- **Google:** Voided Purchases API lists refunded and charged-back purchases; poll and revoke.
- **Webshop:** your processor's dispute webhooks; same revocation path.
- **Policy:** if revoked currency is already spent, go negative balance or claw back the item; never lock the whole account without a support path.

## Minors checklist

- [ ] Age signal collected (store age rating, account age gate, platform family settings)
- [ ] Under-13 (US): COPPA consent flow before personal data, ads personalization off
- [ ] Under-16/18: no paid random items where restricted; no personalized high-value offers; spend limits
- [ ] Chat defaults off for children; voice chat off
- [ ] Purchase confirmation on every real-money purchase
- [ ] Parental controls of the platform respected (Ask to Buy, Play family purchase approval)
