# Bots, Conduct and Guild War Policies

Read when writing a bot policy, a conduct/penalty system, smurf handling, or a guild war spec. Numbers are heuristics unless stated; tune them on your own telemetry.

## 1. Bot policy

**Stance.** Bots are acceptable as practice, as onboarding, and as backfill when a human left or a casual queue cannot fill. They are not acceptable where the player believes the opponent is human and something of value depends on it: ranked rating, leaderboards, prizes, tournaments, or anything with real-money value. Disguising bots there is deception, corrupts ratings, and carries consumer-protection exposure; verify per market with counsel.

```
BOT POLICY: [mode]
ALLOWED IN:       practice | FTUE matches | casual backfill after [X] s | leaver replacement
NEVER IN:         ranked, leaderboards, tournaments, prize or real-money modes, guild war
DISCLOSURE:       label on results screen and match history ("AI opponent" / "AI teammate");
                  rules page states when bots are used; no fake player names in competitive UI
RATING EFFECT:    bot matches never change MMR or visible rank
REWARDS:          casual rewards allowed; no progress toward competitive rewards
DIFFICULTY:       tuned to a target win rate per maturity bucket (below)
MONETIZATION:     bots must never be scheduled around offers (no engineered loss streaks before a sale)
OWNER / AUDIT:    [name]; monthly bot_share by maturity bucket
```

Falloff schedule by account maturity (heuristic):

| Bucket | Bot eligibility | Queue time before bot backfill | Target win rate vs bots |
| --- | --- | --- | --- |
| Matches 1-3 (FTUE) | up to 100% | immediate | 70-80% |
| Matches 4-10 | up to 50% | 15 s | 60-65% |
| Matches 11-30 | up to 20% | 30 s | 55% |
| Matches 31+ | backfill only (leavers, off-hours casual) | 45-60 s | 50% |

Exit criterion: once a player is eligible for ranked, their casual bot share should be under 10% at peak. If it is not, the casual pool is too small; merge queues rather than add bots.

## 2. Conduct system

### Reporting

- Post-match report in **3 taps or fewer**: player, category, optional note.
- Categories: cheating, verbal abuse, griefing/intentional feeding, AFK, inappropriate name or avatar.
- **Reporter feedback**: notify when action was taken against someone they reported. Without it, report volume decays and the signal goes with it.
- Weight reports by reporter accuracy history; one account's reports against the same player count once per day.

### Chat defaults

- Mobile default: quick-chat and pings on; free text off in ranked unless opted in (heuristic).
- Minors (by age gate or platform signal): free text off, or filtered to an allow-list.
- Filter on by default for everyone; one tap to mute all; per-player mute persists across matches.

### Honor / endorsement

- Post-match endorsement of teammates (limited to 1-2 per match to keep it meaningful).
- Honor level gates cosmetic rewards and ranked queue access at the low end; it never raises rating.
- Decay honor slowly with inactivity; drop it quickly on confirmed penalties.

### Leaver penalty ladder

```
Offense (rolling 7 days) | Penalty                                   | Ranked points
1                        | warning + reconnect reminder              | full loss
2                        | 5 min queue lockout                       | full loss
3                        | 30 min lockout                            | full loss + 25%
4                        | 2 h lockout                               | full loss + 50%
5+                       | 24 h lockout, ranked suspended for 24 h   | full loss + 50%
Decay: one level per 7 clean days or per 10 completed matches, whichever comes first.
Teammates of a leaver: 50-100% loss forgiveness; offer reconnect window of 60-120 s first.
```

Distinguish crash/disconnect from quit: a reconnect within the window clears the offense. Mobile networks drop; punishing every disconnect as a quit punishes commuters.

### Smurf handling

- Gate ranked behind account level or ~10-20 hours of play (heuristic) and, where acceptable, phone verification.
- Fast-track: performance-based K multiplier for the first 20 games (see rating-math reference).
- Seed placement from account signals: prior linked accounts, early win rate, per-match performance z-score above 2.
- Duo restrictions: cap party rank spread at 2 major tiers; boosted duos are the main smurf use case.

## 3. Guild / alliance war spec

```
WAR FORMAT:       prep [24] h + battle [24] h   | league tiers with promotion/relegation
ROSTER:           [15-50] members; locked at prep start; opt-in, not auto-enlist
WAR WEIGHT:       sum over top-K members of weight_i x power_i, weights descending
                  (e.g. 1.0 for ranks 1-5, 0.8 for 6-15, 0.5 for 16+) - heuristic
MATCH RULE:       war weight within +-5%; widen to +-10% after [X] min; league tier must match
ATTACKS:          [2] per member; stars 0-3 per target; tiebreak by destruction %
TIMEZONE:         battle window covers 24 h; no single-hour objectives in wars
REWARDS:          participation reward per attack used; winner bonus;
                  loser total >= 40-50% of winner total
INACTIVITY:       members with 0 attacks in last 2 wars excluded from weight and roster by default
ANTI-ABUSE:       no roster changes during battle; alt-account detection on war participants
```

Health metrics: blowout share (star margin above half the maximum) under 30%; war participation (attacks used / attacks available) above 70%; guilds entering next war after a loss above 85%.

## 4. Async PvP spec

```
OPPONENT POOL:    trophies +-[150] and defense power +-[15]%; offer 3: safe / even / stretch
TARGET:           attack win rate 55-70% overall; stretch ~35-45%, safe ~80%
EXCHANGE:         attacker +[30] / defender -[20]; net creation measured weekly; decay above top tier
DEFENSE SNAPSHOT: last saved formation and power; no live-buffs applied to offline defenders
SHIELD:           [8-12] h after losing above [X]% of a resource or trophies; breaks when the player attacks
REVENGE:          one tap from defense log; [+25]% reward; once per attacker per day
LOSS CAP:         defender can lose at most [X] resource per day to raids
```
