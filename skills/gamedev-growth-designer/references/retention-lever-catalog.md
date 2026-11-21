# Retention Lever Catalog

Read when choosing a specific lever and you need implementation notes, genre fit and known failure modes. Effect sizes are deliberately omitted: they vary by an order of magnitude across games, so treat every lever as a hypothesis for the experiment backlog and size it with your own holdout.

## D1 levers (first-session promise)

| Lever | Implementation notes | Genre fit | Failure mode |
| --- | --- | --- | --- |
| Early win within 60 s | Core action reachable fast; first success guaranteed | All | Fake win with no skill read; player feels patronized |
| Visible long goal | Show the renovation, the castle, the roster page before the player can afford it | Puzzle meta, builders, RPG | Goal shown but path unclear — show the next step, not only the end |
| End-of-session cliffhanger | Start a timer, half-finish a build, leave a chest locked until tomorrow | Builders, 4X, idle, casual | Timer too long (over 8 h) on day 1 — player forgets |
| Name and identity investment | Player names the town, picks an avatar, customizes something | Social, builders | Long forms in FTUE cost more D1 than they earn |
| First reward preview | "Come back tomorrow for X" with X visible | All | Preview of a reward that turns out to be minor |

## D7 levers (habit)

| Lever | Implementation notes | Genre fit | Failure mode |
| --- | --- | --- | --- |
| Dailies (3–5 tasks) | Completable in one normal session; pay into a weekly meter | All F2P | Tasks that force modes the player dislikes |
| Daily challenge / puzzle of the day | One shared, comparable attempt | Puzzle, word, roguelite | No social comparison — loses most of its pull |
| Staggered timers | 4 h / 8 h / 24 h appointment slots | Builders, 4X, farming | Every timer the same length — collapses to one session/day |
| Login calendar | 7-day loop with a day-7 milestone; resets cycle, not progress | All | Calendar resets to day 1 on a miss — punishes the habit you want |
| Streaks | Freeze, repair, milestone at 7/30/100 | Puzzle, education-like casual | Streak on "open app" — rewards nothing meaningful |
| Energy / lives refill | Full refill aligned with sleep cycle or a session interval | Match-3, RPG | Refill so slow it reads as a paywall |
| Weekly meter | Dailies feed a weekly chest | All | Weekly goal unreachable for 3-session/week players |

## D30 levers (investment, social, live)

| Lever | Implementation notes | Genre fit | Failure mode |
| --- | --- | --- | --- |
| Collections / albums | Sets with set-completion rewards; duplicates tradeable or convertible | Casual board, puzzle, RPG | Last item of a set gated by luck with no pity |
| Guilds / teams | Donations, help timers, shared chests, team events | 4X, RPG, puzzle (team events) | Guild unlocked in FTUE; dead guilds not merged |
| Guild health tooling | Auto-kick inactive, merge suggestions, recruitment board | All with guilds | Leaving a player in a guild of inactives — they churn with it |
| Friends and gifting | Daily gift sends, request lives | Casual | Spammy requests through OS share sheets |
| Leaderboards | Bucketed into small leagues (e.g. 30–50) with promotion/relegation | Puzzle, PvP, idle | One global board — 99% see an unreachable rank |
| Prestige / rebirth | Reset with permanent multiplier | Idle, roguelite | First prestige before the player understands the loop |
| Season and events | Calendar-driven; see the LiveOps skill | All live games | Event fatigue — overlapping events with no rest |
| Status and cosmetics | Visible to others (guild, profile, PvP) | Social, PvP | Cosmetics nobody else sees |

## Social loop design notes

- **Give-and-get symmetry.** A healthy guild loop has members both giving (donations, help) and receiving. Track the share of members who gave in the last 7 days; below roughly half the guild is dying.
- **Guild size.** Keep it small enough that each member's absence is noticed. Many casual team systems use 20–50; 4X alliances run larger because the obligation is territorial.
- **Matchmaking for teams.** Place new players into active guilds (recent activity score), not the largest. Offer a one-tap "recommended team".
- **Async first.** Real-time co-op requires concurrency most casual games do not have. Async help, donations and shared goals work at any DAU.
- **Moderation.** Open chat requires reporting, muting, word filters and, for minors, often no free chat at all. Budget moderation before shipping chat.

## Viral moment design

- Ask at peaks: level clear with a rare result, collection completion, guild needing one more member, a funny or surprising outcome.
- Make the shared artifact interesting to a non-player (a replay, a before/after of a renovation), not an ad.
- Deep-link to a context: the inviter's guild, a specific challenge, a gift waiting. Generic store links convert worst.
- Track the full chain: share sheet opened, share completed, link clicked, install, first open with referral context, milestone reached.

## Win-back segment playbook

| Segment | Message | Offer | Re-entry |
| --- | --- | --- | --- |
| Lapsed 7–13 d, non-payer | "Your X is ready / your team misses you" | Small free catch-up bundle | One guided goal, then normal loop |
| Lapsed 7–13 d, payer | Content news, not discount | Free catch-up; avoid discounting their usual purchase | Same |
| Lapsed 14–29 d | "What's new" summary | Catch-up to current content floor | 3-card what's new, then guided goal |
| Lapsed 30+ d | Paid re-engagement only if measured ROI positive | Returning-player pass or event track | Fresh-start option (skip to current chapter) |

Measure 14-day re-churn of returners against a no-contact holdout. A win-back that returns players who churn again within a week has bought a session, not a player.
