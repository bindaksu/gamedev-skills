# Runbooks, Comms Templates and Post-Incident Review

Read during an incident, before a maintenance window, and when writing a post-incident review.

## Incident runbook

```
0. DETECT     Alert, player reports, community manager, store reviews spike
1. DECLARE    Open incident channel; assign IC, ops lead, comms lead, scribe; set SEV
2. ASSESS     Which journeys (login, match, purchase, claim, download)? Which regions, versions, platforms? Since when?
              What changed in the last 2 h: server deploy, config publish, CDN catalog, client rollout, third party?
3. MITIGATE   In order of speed and safety:
              a. Revert the last config / catalog version
              b. Flip kill switch on the suspect feature
              c. Roll back the last server deploy (if backward compatible)
              d. Shed load: disable non-core features, enable login queue, rate limit
              e. Halt client rollout (gamedev-delivery-release)
              f. Maintenance mode (last resort; announce)
4. COMMUNICATE Within 15 min (SEV1) / 30 min (SEV2); then every 30/60 min until resolved
5. VERIFY     SLIs back inside SLO for 30+ min; player reports falling
6. RESOLVE    Close incident; announce resolution and compensation if any
7. REVIEW     PIR within 5 working days
```

Decision rule: if a mitigation has not shown effect in 15 minutes, try the next one; the IC decides, the ops lead executes.

## Severity quick reference

| SEV | Examples | Page | Status page | Compensation review |
|---|---|---|---|---|
| 1 | Login down in a top region; purchases failing; progress loss; active dupe | Yes, immediately | Yes | Yes |
| 2 | Matchmaking broken in one mode; event rewards delayed; one platform degraded | Yes | Yes if player-visible | Case by case |
| 3 | Leaderboard stale; cosmetic shop images missing | No (working hours) | No | No |
| 4 | Internal tool broken | No | No | No |

## Player comms templates

Keep messages factual, short, without blame, with the next update time. Do not disclose exploit mechanics.

**Investigating**
```
We're aware some players can't [log in / complete purchases / receive event rewards]. The team is investigating. Next update by [HH:MM UTC].
```

**Identified / mitigating**
```
We've found the cause of [issue] and are rolling out a fix. Purchases made during this time are safe and will be delivered. Next update by [HH:MM UTC].
```

**Resolved**
```
[Issue] is resolved as of [HH:MM UTC]. Thanks for your patience. Everyone who logged in between [start] and [end] will receive [compensation] in their inbox within 24 hours.
```

**Planned maintenance (24–72 h ahead)**
```
Scheduled maintenance: [date], [HH:MM]–[HH:MM UTC] (about [N] minutes). The game will be unavailable. Event timers have been extended by [N] hours. Maintenance reward: [item].
```

**Extended maintenance**
```
Maintenance is taking longer than planned. New estimate: [HH:MM UTC]. We'll add [extra compensation] for the delay.
```

**Economy correction (exploit)**
```
A bug let some accounts receive extra [currency] between [start] and [end]. It's fixed. We've removed amounts received through the bug; nothing else on your account changed. If you think this affected you incorrectly, contact support with code [CODE].
```

## Compensation scale [policy guidance; set your own values]

| Event | Compensation |
|---|---|
| Planned maintenance on time | Small token (e.g., energy refill) |
| Maintenance overrun | Token plus scale by overrun length |
| SEV2 outage over 1 h | Moderate bundle; extend affected event timers |
| SEV1 outage | Larger bundle; extend events; restore lost progress from ledger |
| Lost purchase | Deliver the purchase plus apology item; never require a receipt from the player if the ledger shows it |

Rules: compensation is never premium-currency-heavy enough to distort the price ladder; extending event timers is often worth more to players than currency; send via inbox with expiry of at least 7 days.

## Maintenance window checklist

- [ ] Window chosen at lowest traffic across top revenue regions; no event final hours inside it
- [ ] Announcement 24–72 h ahead: in-game banner, social, status page
- [ ] Event timers extended by window length
- [ ] Server-driven maintenance message works on all supported client versions
- [ ] Rollback plan and go/no-go point inside the window
- [ ] Smoke test plan for reopening (login, purchase, claim, match)
- [ ] Staged reopening (internal, then 10%, then all) to avoid a login spike

## Status page components

Login and accounts; Store and purchases; Matchmaking (per mode); Events and rewards; Content downloads; Chat and social. Each with region breakdown if you run regional shards.

## Post-incident review (PIR) template

```
TITLE / SEV / DATE / DURATION (detect to mitigate, mitigate to resolve)
IMPACT: players affected, regions, versions, revenue impact, SLO budget consumed
TIMELINE (UTC): detection, declaration, each mitigation attempt, resolution
ROOT CAUSE: technical cause and the process gap that allowed it
DETECTION: how we found out; could an alert have caught it earlier?
WHAT WENT WELL / WHAT HURT
ACTIONS: | Action | Type (prevent / detect / mitigate) | Owner | Due | Status |
PLAYER COMMS AND COMPENSATION: what was sent, when
```

Blameless: describe decisions given the information available at the time. Track actions weekly until closed.
