# Rating Math Reference

Read when implementing, auditing or explaining a rating system. All formulas are the published forms; parameter choices marked heuristic are design defaults, not standards.

## Elo

```
E_A  = 1 / (1 + 10^((R_B - R_A) / 400))
R'_A = R_A + K (S_A - E_A)            S_A in {1, 0.5, 0}
```

- 400 is the scale: a 400-point gap means 10:1 odds.
- Zero-sum per match when both sides use the same K. Different K per player (placement vs settled) creates or destroys points; track the population mean.
- FIDE chess K: 40 for the first 30 games, 20 below 2400, 10 once 2400 is reached.
- Game heuristic: K 40-60 placement, 24-32 normal, 16 for the top tier.
- Teams in Elo: use team mean rating for E, apply the same delta to each member (or scale by a contribution score, which invites stat-padding; avoid in ranked).

Performance-based smurf fast-track (heuristic): for the first 20 games, `K_eff = K x clamp(1 + (winrate_so_far - 0.5) x 4, 1, 3)`. A 75% early win rate triples K and halves time-to-true-rating.

## Glicko-2 (Glickman)

Defaults: r = 1500, RD = 350, sigma = 0.06. System constant tau, typically 0.3-1.2. Convergence tolerance epsilon = 0.000001.

```
Step 1  Scale down
        mu  = (r - 1500) / 173.7178
        phi = RD / 173.7178

Step 2  For each opponent j in the rating period
        g(phi_j) = 1 / sqrt(1 + 3 phi_j^2 / pi^2)
        E_j      = 1 / (1 + exp(-g(phi_j) (mu - mu_j)))

Step 3  Estimated variance
        v = 1 / sum_j [ g(phi_j)^2 E_j (1 - E_j) ]

Step 4  Estimated improvement
        Delta = v * sum_j [ g(phi_j) (s_j - E_j) ]

Step 5  New volatility sigma' (Illinois algorithm)
        a = ln(sigma^2)
        f(x) = e^x (Delta^2 - phi^2 - v - e^x) / (2 (phi^2 + v + e^x)^2) - (x - a) / tau^2
        A = a
        if Delta^2 > phi^2 + v:  B = ln(Delta^2 - phi^2 - v)
        else: k = 1; while f(a - k tau) < 0: k += 1;  B = a - k tau
        fA = f(A); fB = f(B)
        while |B - A| > epsilon:
            C  = A + (A - B) fA / (fB - fA);  fC = f(C)
            if fC * fB <= 0:  A = B; fA = fB
            else:             fA = fA / 2
            B = C; fB = fC
        sigma' = e^(A / 2)

Step 6  Pre-period RD
        phi* = sqrt(phi^2 + sigma'^2)

Step 7  New rating and RD
        phi' = 1 / sqrt(1 / phi*^2 + 1 / v)
        mu'  = mu + phi'^2 * sum_j [ g(phi_j) (s_j - E_j) ]

Step 8  Scale up
        r'  = 173.7178 mu' + 1500
        RD' = 173.7178 phi'
```

No games in a period: rating and volatility unchanged; `phi' = sqrt(phi^2 + sigma^2)`.

**Glickman's worked example** (tau = 0.5). Player r = 1500, RD = 200, sigma = 0.06. Opponents: 1400/RD 30 (win), 1550/RD 100 (loss), 1700/RD 300 (loss). Intermediate v = 1.7785, Delta = -0.4834. Result: **r' = 1464.06, RD' = 151.52, sigma' = 0.05999**. Use this as the unit test for any implementation.

### Operational notes

- Rating period: batch so that active players average 10-15 games per period. For a game with 6 ranked matches/day, a 2-day period. Between batches, show a provisional estimate on the client; the stored rating updates at period close.
- Per-match "Glicko-2 lite" (each game as a period) is common in live games. It works, but volatility then reacts to single results; lower tau (0.3-0.5) compensates (heuristic).
- Inactivity growth with sigma 0.06 is very slow (RD 50 back to 350 takes ~1,100 empty periods). Add an explicit absence bump: `RD = min(sqrt(RD^2 + c^2 t), 350)` with t in days and c chosen so 50 returns to 350 after the absence you consider "unknown" (Glicko-1 form). For 180 days: `c = sqrt((350^2 - 50^2)/180) = 25.8`.
- Matchmaking on Glicko: match on r, but widen faster for high-RD players; their rating is a guess anyway.

## TrueSkill-style Bayesian rating

Defaults: mu0 = 25, sigma0 = 25/3, beta = sigma0/2 (the skill gap that gives ~76% win chance), tau = sigma0/100 (added to variance each game so ratings can move), draw probability 0.10.

### Two-player update (no draw shown; draw adds a margin epsilon)

```
sigma_i^2 += tau^2                          (dynamics, before each game)
c^2   = 2 beta^2 + sigma_w^2 + sigma_l^2
t     = (mu_w - mu_l) / c
v(t)  = pdf(t) / cdf(t)
w(t)  = v(t) (v(t) + t)
mu_w' = mu_w + (sigma_w^2 / c) v(t)
mu_l' = mu_l - (sigma_l^2 / c) v(t)
sigma_w'^2 = sigma_w^2 (1 - (sigma_w^2 / c^2) w(t))
sigma_l'^2 = sigma_l^2 (1 - (sigma_l^2 / c^2) w(t))
```

Two new players, winner (no draw, tau ignored): c^2 = 34.72 + 138.89 = 173.61, c = 13.18; v(0) = 0.798, w(0) = 0.637. mu_w' = 25 + (69.44/13.18)(0.798) = 29.21, mu_l' = 20.79, sigma' = 7.19. Common library defaults with the 10% draw margin give about 29.40 / 7.17. Either way, one game moves a new player by ~half a sigma.

### Teams and quality

```
Team performance variance: n beta^2 + sum sigma_i^2   (n = all players in the match)
P(A beats B) = Phi( (sum mu_A - sum mu_B) / sqrt(n beta^2 + sum sigma_i^2) )
1v1 quality  = sqrt(2 beta^2 / (2 beta^2 + s1^2 + s2^2)) * exp(-(mu1 - mu2)^2 / (2 (2 beta^2 + s1^2 + s2^2)))
```

Quality for two new players is 0.447; as sigma shrinks toward ~1-2, quality for equal mu approaches 1. Gate on quality only after placement, or the new-player queue never fills.

Leaderboard value: `mu - 3 sigma` (starts at 0, grows with evidence). Never show raw mu; it rewards playing very few games.

Licensing: TrueSkill is a Microsoft trademark with patent history. Verify status before shipping. Weng-Lin Bayesian approximations (used by OpenSkill-style libraries) give similar behavior for teams and free-for-all.

## Choosing a model

| Situation | Model | Why |
| --- | --- | --- |
| 1v1, steady daily play, simple to explain | Elo with K schedule | Transparent; points visible to players map to the formula |
| 1v1, bursty play, long absences | Glicko-2 | RD encodes "we have not seen you lately" |
| Teams, FFA, battle royale placements | TrueSkill-style / Weng-Lin | Native team and multi-rank outcomes, fast convergence |
| Async attack/defense | Elo-like trophies, asymmetric exchange plus decay | Defender is offline; outcome is attacker-chosen |
| Guild war | Weighted war weight + league tiers | Rating individuals is wrong unit; the guild is the competitor |

## Team aggregation choices

- **Mean**: default; hides one carry.
- **Max-weighted mean** (`0.4 max + 0.6 mean`, heuristic): for modes where one player dominates outcomes.
- **Party premade bonus**: add 20-50 Elo points per premade member to the team rating for matching only (heuristic); measure premade win rate vs solo at equal rating and tune until the gap is under 3 pp.
