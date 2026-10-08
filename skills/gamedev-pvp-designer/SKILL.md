---
name: gamedev-pvp-designer
description: >-
  Design PvP that feels fair and fills fast: skill rating (Elo, Glicko-2,
  TrueSkill), hidden MMR versus visible rank, queue time versus match quality,
  seasons and soft resets, async PvP, guild wars, pay-to-win boundaries, bots
  and anti-toxicity. Use when tuning a matchmaker or rating formula, when
  players complain about stomps, smurfs, long queues or rigged matches, when
  designing a ranked ladder, season reset, async raid or guild war, when
  deciding what money may buy in competitive modes, or when considering bots
  for a low-population queue.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: design
---

# PvP Designer

A PvP system is a promise that the outcome was decided by the players: not by the matchmaker, not by the wallet, not by the clock. Every competitive design trades three quantities that cannot all be maximized: **match quality**, **queue time**, and **population split** (modes x regions x party sizes x rating brackets). The rating formula is the cheapest part to get right. The expensive failures are a ladder that lies about skill, a top bracket that cannot fill at 3 a.m., and a store that sells win rate. Size the population first, choose the rating model second, and write down what money may never buy before the first offer ships.

## Role Profile

At a top-grossing studio this is the competitive-systems designer: owner of matchmaking, skill rating, ranked ladders, seasons and the fairness contract. PvP sits at the top of the chart (Honor of Kings was the #1 grossing mobile game of 2025 at $1.68bn net; Clash Royale had a record year, https://mobilegamer.biz/the-top-grossing-mobile-games-of-2025/).

- **Responsibilities.** Riot's ranked/matchmaking posting: "Tune and propose new features for matchmaking and skill systems to ensure fair, enjoyable, and competitive games" and "articulate tradeoffs and risks with designs" (https://builtin.com/job/game-designer-ii-league-legends-competitive-ranked-matchmaking-systems/3842623). VALORANT's competitive-systems role balances "competitive integrity with satisfying game systems" across ranked ladders and seasons (https://us.joinrise.co/jobs/riot-games-game-designer-iii-valorant-competitive-systems-mh6f). Supercell runs a separate "Competitive Experience Manager" title.
- **Bar.** 1+ years on matchmaking/ranked plus 3+ on competitive PvP (mid-level); 5-7+ years and a shipped online competitive title (senior). Seniority shows as decision frameworks handed to cross-disciplinary partners.
- **Hard skills.** Rating models (Elo, Glicko, TrueSkill-style Bayesian), SQL on match telemetry, queue simulation, matchmaker configuration, ladder and reward design, written tradeoff docs.
- **KPIs (inferred from responsibilities, not quoted).** Predicted-win-probability spread around 50%; queue time p50/p90 per bracket; ranked participation and retention; smurf, leaver and toxicity report rates.
- **Collaborators.** Metasystems lead, data science, server/matchmaking engineers, anti-cheat, esports and community.

## When to Use / Not

Use for: rating math, matchmaker rules, ranked tiers, seasons, async attack/defense loops, guild/alliance wars, P2W policy for competitive modes, bot policy, conduct and penalty systems.

Not for: hit/hurt boxes, TTK and unit balance (`gamedev-combat-designer`); rollback, prediction, tick rate (`gamedev-netcode-engineer`); the matchmaker service, leaderboard storage and data model (`gamedev-platform-server-architect`, `gamedev-backend-engineer`); cheat and bot-account detection (`gamedev-anti-cheat-security`); offer and pass pricing (`gamedev-monetization-designer`); season calendar and event cadence (`gamedev-liveops-designer`); guild social loops beyond war (`gamedev-growth-designer`).

## Inputs to Gather

- **Format.** Sync real-time (1v1, team), async (attack a snapshot), alliance/guild war, tournament. Match size N and team size. Default: assume sync 1v1 if unstated, then ask.
- **Population.** Peak and trough ranked queue arrivals per minute, per region and mode. If missing, derive from DAU x PvP participation x matches/day / active hours, and say it is an estimate.
- **Skill expression.** How much of the outcome is skill vs. draft vs. randomness vs. account power. Default: measure the favored side's win rate at a 200-point rating gap; a small edge means high noise, so use smaller K and longer placement.
- **Power.** Does account progression (levels, cards, gear) affect ranked stats? Default: assume yes for mobile F2P until proven otherwise; this is the P2W surface.
- **Latency.** Max acceptable RTT (real-time action: assume 80 ms; turn-based or card: assume 200 ms+), number of server regions.
- **Constraints.** Age rating, real-money prizes or esports, platform rules on chat, existing ladders the community is attached to.
- **Telemetry available.** Match-level rows with both sides' pre-match ratings, queue join and match start timestamps, spend tier, party size, leaver flags, reports.

## Method

1. **Classify each mode** as competitive (ranked, prizes, leaderboards), casual, or practice. The fairness bar, bot policy and P2W rules differ per class; one rule set for all modes guarantees a wrong rule somewhere.
2. **Size the pool per queue.** Compute arrivals per second per mode x region x party bucket at peak and trough. Apply the fill formula below to the median and the top 0.5% bracket. Merge queues that cannot fill the top bracket within the target wait at trough; queue fragmentation is the most common cause of bad matches, not the rating formula.
3. **Choose the rating model.** Elo for 1v1 with steady play; Glicko-2 when play is bursty or returns after absence matter; TrueSkill-style Bayesian for teams, free-for-all and fast convergence. Keep MMR hidden; it is a measurement, not a reward.
4. **Define match quality numerically.** Use predicted win probability of the favored side (or TrueSkill match quality) and set a per-class target. A matchmaker without a quality number cannot be tuned, only argued about.
5. **Write the search-widening schedule** and cap it. After the cap, choose an explicit fallback (cross-region within latency budget, wider party rules, or bot backfill in casual only), never silent infinite widening.
6. **Balance teams** after selecting the players: partition by rating to minimize the gap of team means, then cap party-vs-solo mismatches (premade bonus or party-matched-to-party).
7. **Design the visible rank** (tiers, points, shields) as a slow, readable function that converges to MMR. Visible rank is the reward surface; MMR is the truth.
8. **Plan seasons**: length, soft-reset compression, uncertainty bump, placement matches, end-of-season rewards by peak or final tier.
9. **Write the P2W Boundary Charter** with the measurement that enforces it, and get it signed by monetization before any competitive offer exists.
10. **Write the bot policy** with disclosure rules and a falloff schedule by account maturity.
11. **Design conduct systems**: report flow, chat defaults, honor, leaver ladder, smurf fast-tracking.
12. **Simulate before shipping.** Run a queue simulation with real arrival curves and a rating simulation with synthetic true skills; check convergence games, wait percentiles and quality percentiles. Read `references/matchmaking-sim.md` when building the harness.
13. **Instrument and review weekly**: quality and wait by bracket, win rate by spend tier at equal MMR, leaver and report rates, tier distribution drift.

## Deliverables

### 1. Mode Sheet (one per PvP mode)

```
MODE:            [name]         CLASS: competitive / casual / practice
FORMAT:          sync | async | guild war    TEAM x TEAMS: [3x2]    MATCH LEN: [min]
RATING MODEL:    Elo K=[ ] | Glicko-2 tau=[ ] | Bayesian (mu0, sigma0, beta)
POOL @ PEAK:     [arrivals/min per region]     POOL @ TROUGH: [ ]
QUALITY TARGET:  P(favored) <= [0.60] for [80]% of matches; hard cap [0.70]
WAIT TARGET:     p50 [ ]s  p90 [ ]s  top-0.5% p90 [ ]s
FALLBACK:        [cross-region <= X ms | party relax | bot backfill (casual only)]
POWER RULE:      [normalized | power band +-X% | unrestricted (casual only)]
BOTS:            [never | FTUE only | backfill after X s, labeled]
```

### 2. Matchmaker Config

```yaml
queue: ranked_3v3_eu
rating: { model: glicko2, tau: 0.5, period_games: 10 }
window:                       # Elo-scale points; heuristic schedule
  start: 50
  widen_per_5s: 25
  cap: 250
  cap_at_s: 45
after_cap: { fallback: cross_region, max_rtt_ms: 80 }
team_balance: { method: min_mean_gap, max_mean_gap: 40 }
party: { premade_bonus_mmr: 30, max_party_rank_spread_tiers: 2 }
power_band: { enabled: false }   # ranked uses normalized stats
quality_floor: { p_favored_max: 0.70 }
```

### 3. Ranked Ladder Table

```
Tier     | Divs | Pts/div | MMR band (entry) | Target % of active | Demotion shield | Season floor
Bronze   |  3   |  100    | < 1150           | 5-10%              | none            | no
Silver   |  3   |  100    | 1150-1350        | 15-20%             | 3 games         | no
Gold     |  3   |  100    | 1350-1550        | 25-30%             | 3 games         | yes
...
Master   |  -   | open    | top 1-2%         | 1-2%               | n/a             | yes
Champion |  -   | ladder  | top 0.1-0.5%     | <=0.5%             | n/a             | no
```

### 4. Season Spec

```
LENGTH:          [weeks]   PLACEMENT GAMES: [5-10]
RESET:           R_new = R_center + c (R_old - R_center), c = [0.5-0.8]
UNCERTAINTY:     RD_new = min(sqrt(RD^2 + bump^2), RD_max)   bump = [ ]
REWARD BASIS:    peak tier | final tier   (peak reduces end-of-season decay play)
DECAY:           top tiers only, [X] pts/day after [7] idle days
```

### 5. P2W Boundary Charter

```
MONEY MAY BUY:        cosmetics; time (faster unlocks of items F2P also reach);
                      breadth (more options, sidegrades); convenience (slots, replays)
MONEY MAY NOT BUY:    in-match stat advantage in ranked; power unreachable for F2P;
                      rating, rank points, or matchmaking priority; outcome items
RANKED STAT RULE:     normalized levels | power band +-[10]% | none (justify)
ENFORCEMENT METRIC:   win-rate delta by spend tier at equal MMR (logistic model)
GATE:                 ranked delta <= 3 pp; power-band modes <= 8 pp  (heuristics)
OWNER / REVIEW:       [names], every content drop that adds power
```

### 6. Bot Policy and 7. Conduct Ladder

Templates in `references/policies.md`; read when writing bot disclosure, falloff, leaver penalties, report flows or guild war specs.

## Quantitative Reference

### Elo

`E_A = 1 / (1 + 10^((R_B - R_A)/400))`, `R'_A = R_A + K (S_A - E_A)`, S = 1 / 0.5 / 0.

| Gap (points) | 0 | 100 | 200 | 300 | 400 |
| --- | --- | --- | --- | --- | --- |
| E (favored) | 0.50 | 0.64 | 0.76 | 0.85 | 0.91 |

K schedule: FIDE chess uses 40 for a player's first 30 games, 20 below 2400, 10 at 2400+. For games, a common pattern (heuristic) is K = 40-60 for placement, 24-32 normal, 16 at the top, because noisy outcomes with large K produce rating random walks of about `K x sqrt(games)/2` with no skill change.

### Glicko-2

Published defaults: rating 1500, RD 350, volatility 0.06; system constant tau typically 0.3-1.2 (smaller tau = volatility changes slowly). Internal scale: `mu = (r - 1500)/173.7178`, `phi = RD/173.7178`. Works best with a rating period containing roughly 10-15 games per active player; per-game periods make volatility unstable.

- 95% interval of true skill: `r +- 2 RD`. RD 350 means "unknown"; RD 50-60 means settled.
- **Inactivity is slow.** With no games, `phi* = sqrt(phi^2 + sigma^2)`. At sigma 0.06 an RD of 50 grows to only 51.1 after one period and needs about 1,100 periods to return to 350. A returning player after six months is treated as near-certain. Add an explicit season or absence bump.
- Full update, Illinois volatility solver and Glickman's worked example are in `references/rating-math.md`; read when implementing or auditing an implementation.

### TrueSkill-style Bayesian rating

Defaults: `mu0 = 25`, `sigma0 = 25/3 = 8.333`, `beta = sigma0/2 = 4.167` (skill gap giving ~76% win odds), `tau = sigma0/100` (dynamics), draw probability 10%. Display conservative skill `mu - 3 sigma`, which starts at 0 and only rises with evidence.

- Team win probability: `P(A) = Phi((sum mu_A - sum mu_B) / sqrt(n beta^2 + sum sigma^2))`, n = total players.
- 1v1 match quality: `q = sqrt(2b2/(2b2 + s1^2 + s2^2)) x exp(-(mu1 - mu2)^2 / (2(2b2 + s1^2 + s2^2)))`, b2 = beta^2. Two brand-new players score q = 0.447: uncertainty, not mismatch, caps quality early.
- TrueSkill is a Microsoft trademark with patent history; verify licensing before shipping it. Weng-Lin Bayesian approximations (the basis of OpenSkill-style libraries) are the usual open alternative.

### Population and queue time

First-order fill estimate (Poisson arrivals; simulate for real numbers):

```
lambda_eff = lambda_queue x f(window)        f = fraction of arrivals inside the rating window
wait       = (N - 1) / lambda_eff             N = players per match
needed     = lambda_queue >= (N - 1) / (f x W_target)
in_queue   = lambda_queue x mean_wait         (Little's law; size servers and UI on this)
```

With ratings ~ Normal(1500, 300), a +-100 window covers 26% of arrivals at the median but about 1.1% at the top 0.5% (z = 2.58). The top bracket needs ~25x the population of the median for the same wait. That ratio, not the median wait, decides how many queues a game can afford.

**Targets (heuristics, mobile):** casual p50 <= 10 s, p90 <= 30 s; ranked p50 <= 30 s, p90 <= 90 s; top 1% p90 <= 180 s. Quality: P(favored) <= 0.60 for 80% of ranked matches, never above 0.70; casual tolerates 0.70 for speed.

### Visible rank vs MMR

Points per game converge visible rank toward MMR (heuristic shape):

```
gain = base x clamp(1 + (MMR - R_vis)/D, 0.5, 1.75)
loss = base x clamp(1 - (MMR - R_vis)/D, 0.5, 1.75)        base 20, D 400
```

A player 200 above their visible rank gains 30 and loses 10, netting +10/game at 50% win rate: about 10 games per 100-point division. If every win/loss is symmetric and ignores MMR, a smurf needs 5x as many games to reach their level and stomps everyone on the way.

- Demotion shield: 3 games at 0 points after a promotion (heuristic). Tier floors at 1-2 major tiers per season; more floors flatten the distribution into the floor tier.
- Watch **point creation**: any asymmetry (win bonus, streak bonus, shield) creates net points. Measure mean visible points per active player weekly; inflation over ~2% per week means the top tier will exceed its target share before season end.

### Seasons

Soft reset: `R_new = R_center + c (R_old - R_center)`, c = 0.5-0.8 (heuristic). c below 0.4 puts veterans into new-player matches for weeks (stomp season). c = 1.0 with a visible-rank reset only is fine if visible rank re-converges within placement plus ~20 games. Add an RD bump of 50-100 Glicko points so the first games of a season move rating faster. Mobile season length: 4-8 weeks is common; shorter seasons need lower c because there is less time to re-climb.

### Async PvP

The attacker picks the fight and knows the defense; target **attack win rate 55-70%** (heuristic) for opponents served by the matchmaker, and offer a 3-opponent choice (safe/even/stretch) with reward scaled by expected difficulty. Snapshot the defense at last save; never let the defender lose more than they could have prevented offline. Asymmetric point exchange (attacker +30, defender -20) creates 10 net points per battle: pair it with decay or a reset, or the ladder inflates. After a heavy defense loss, a shield of several hours (heuristic 8-12 h) prevents farming; a one-tap revenge with bonus reward converts the loss into a session.

### Guild / alliance war

Match on **war weight** (sum of the top-K members' power, with descending weights so one whale cannot carry the number), within +-5% (heuristic). Lock rosters at prep start; give each member a fixed attack count (typically 1-3) so participation, not activity hours, decides outcomes; use a 24 h battle window for timezone fairness. Losers should earn at least 40-50% of winner rewards (heuristic) so weaker guilds keep enlisting. Details: `references/policies.md`.

### Rules per mode class

| Rule | Competitive (ranked, prizes) | Casual | Practice |
| --- | --- | --- | --- |
| Match on | hidden MMR, power normalized or banded | MMR + power band | none |
| P(favored) cap | 0.70 | 0.75 | n/a |
| Bots | never | backfill, labeled | yes |
| Account power | normalized or +-10% band | +-15-20% band (heuristic) | free |
| Leaver penalty | full ladder | lockouts only | none |
| Rating change | yes | separate casual MMR | no |

Keep a separate casual MMR. Matching casual on ranked MMR punishes experimentation; not matching casual on skill at all turns it into a stomp queue that new players meet first.

### Conduct numbers (heuristics)

- Leaver rate under 3% of ranked matches; above 5% the penalty ladder or match length is wrong.
- Report rate per 1,000 matches tracked by category; reporter-feedback notices sent for 100% of actioned reports.
- Report review SLA: automated action on high-confidence chat offenses within minutes; human review queue under 48 h.
- Ranked gate: account level or ~10-20 hours played before ranked unlocks; this is the cheapest smurf filter.

### P2W measurement

Fit `win ~ logistic(a x MMR_gap + b x spend_tier + c x party)` on ranked matches. Convert b into percentage points at equal MMR. Ranked gate <= 3 pp; power-band modes <= 8 pp (heuristic gates). Power-band matchmaking: team power within +-10% before rating window widens. If b rises after a content drop, the drop sold power into ranked.

### Worked example: 3v3 mobile brawler, EU ranked

Ratings ~ Normal(1500, 300). Peak arrivals 600/min = 10/s; trough 60/min = 1/s. N = 6, so 5 others needed.

- Median player, window +-100: f = 0.261, lambda_eff = 2.6/s, wait = 5/2.6 = **1.9 s**.
- Top 0.5% (R = 2273), window +-100: f = Phi(2.909) - Phi(2.243) = 0.0106. Peak: 0.106/s, wait **47 s**. Trough: **472 s**. Fails the 180 s target.
- Widen to the +-300 cap at trough: f = 0.0573, wait = 5/0.0573 = **87 s**. Passes, at the cost of quality.
- Team balance on the six found: 1720, 1650, 1600, 1580, 1510, 1440 (sum 9500). Partition {1720, 1580, 1440} = 4740 vs {1650, 1600, 1510} = 4760. Mean gap 6.7 points, P(favored) = 0.51. Wide individual spread is fine if team means match and the top player is not on a team of floor players; cap individual spread at 400 in ranked.
- Decision: one EU ranked 3v3 queue, no separate duo queue (it would halve f for the top bracket), cross-region fallback to ME after 60 s within 80 ms.
- Season reset with c = 0.6 around 1500: 2273 becomes 1964; 1200 becomes 1320.
- Elo check at K = 32 for a 1600 vs 1400 match: E = 0.760; the winner gains 7.7 if favored, 24.3 if the upset.

## Diagnostics

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| "Every match is a stomp" but median wait is fine | Window widens too fast, or teams balanced on sum while one player dominates | Slow widening; balance on means plus cap individual spread; check stomp rate by bracket |
| Top 1% queues > 5 min at night | Pool fragmented across modes, regions, party buckets | Merge queues at trough; cross-region within RTT budget; scheduled ranked hours for top tiers |
| Win rates far from 50% after 100 games for many players | MMR not converging: K too small, or ranking on visible points | Raise K or initial RD; match on hidden MMR; verify inputs |
| New accounts at 75%+ win rate | Smurfs, or placement seeded too low | Performance-based K multiplier for early games; seed from account signals; phone/account-level gate |
| Rank distribution bunched at a floor tier | Too many tier floors or shields | Remove a floor; shields to 3 games |
| Top tier share doubles mid-season | Point inflation from asymmetric exchange | Measure net points/game; add decay or symmetric exchange |
| Ranked participation drops after week 2 | Reset too harsh, or rewards only for top tiers | Raise c; add rewards at every tier crossing; peak-tier rewards |
| Spenders win 8+ pp more at equal MMR in ranked | Power leaking into ranked | Normalize stats or power-band; freeze the offending item from ranked |
| Async attack win rate under 45% | Matchmaker serves too-strong defenses; defense snapshot over-buffed | Pick opponents by expected win; cap defense bonuses |
| Guild war blowouts > 30% of wars | War weight ignores top-heavy rosters or inactive members | Weighted top-K weight; roster lock; exclude inactive from weight |
| Players accuse game of rigging after loss streaks | Streak-based or engagement-based matching, or bots unlabeled | Remove engagement terms from matching; label bots; publish matching principles |
| Report volume high, repeat offenders unchanged | Reports not actioned or no feedback | Feedback notifications; penalty ladder; review queue SLA |
| Leaver rate > 5% of matches | No penalty ladder, or matches too long for mobile | Escalating lockouts; reconnect window; loss forgiveness for teammates |

## Anti-Patterns

**The Lying Ladder** - visible rank decoupled from MMR with asymmetric point gains. The badge inflates, and players matched by hidden MMR feel they are "stuck with low ranks".

**The Infinite Window** - widening with no cap or fallback. The top player gets a 0.95 match at minute four and remembers only that.

**The Queue Shatter** - a new mode, a duo queue and a regional split shipped without a population check. Every queue now fails its top bracket.

**The Paid Stat Check** - ranked outcomes measurably bought. Ranked becomes a spend leaderboard and the skill audience leaves first.

**The Secret Bot Ladder** - unlabeled bots in ranked or prize modes. It is deception, it corrupts ratings, and it is a consumer-protection exposure (verify with counsel per market).

**Engagement-Rigged Matching** - choosing opponents to create loss streaks before an offer or win streaks after a purchase. It works for a quarter and then becomes the community's explanation for every loss.

**The Hard Reset** - full rating reset each season. Veterans farm new players for weeks; new-player D7 in PvP drops.

**The Silent Report Box** - a report button with no visible outcome. Reports fall, toxicity does not.

## Quality Checklist

- [ ] Every mode classified competitive / casual / practice, with rules per class
- [ ] Arrivals per queue computed at peak and trough per region; top 0.5% bracket fill time computed
- [ ] Rating model chosen with stated reason; parameters recorded (K schedule, tau, sigma0, beta)
- [ ] Match quality defined numerically with targets and a hard cap
- [ ] Widening schedule has a cap and an explicit fallback; bots never the ranked fallback
- [ ] Team balancing minimizes team-mean gap and caps individual spread
- [ ] Visible rank converges to MMR within placement + ~20 games in simulation
- [ ] Net point creation per game measured; inflation under ~2%/week
- [ ] Season reset formula, c, RD bump and placement count specified
- [ ] P2W Charter signed; spend-tier win-rate delta at equal MMR monitored, ranked <= 3 pp
- [ ] Bot policy: disclosure, mode restrictions, falloff schedule by account maturity
- [ ] Conduct: report in <= 3 taps, reporter feedback, leaver ladder, smurf fast-track
- [ ] Async: attack win rate 55-70%, shields, revenge, point exchange balanced or decayed
- [ ] Guild war: weighted war weight, roster lock, fixed attacks, loser reward floor
- [ ] Queue and rating simulations run before ship; results attached
- [ ] Weekly dashboard: quality and wait by bracket, leavers, reports, tier distribution

## Related Skills

Unit and weapon balance that changes skill expression goes to `gamedev-combat-designer`; if a 200-point gap gives under 60% win odds, the game is noisy and the rating parameters here must change too. Real-time latency limits that decide region merges go to `gamedev-netcode-engineer`. The matchmaker service, party system and leaderboards are built by `gamedev-platform-server-architect` and `gamedev-backend-engineer`. Smurf and cheat detection signals and ban enforcement belong to `gamedev-anti-cheat-security`. Any offer that touches competitive power is co-reviewed with `gamedev-monetization-designer` against the P2W Charter. Season dates, pass tie-ins and event modes are scheduled with `gamedev-liveops-designer`. Guild recruitment and social retention around wars go to `gamedev-growth-designer`. Match telemetry, rating-input logging and experiment design go to `gamedev-analytics-engineer`. If installed, `game-economy-balancer` sizes PvP reward faucets, and `game-playtest-analyst` reads ranked retention cohorts.
