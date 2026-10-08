# Campaign Structures Reference

Read when working on power-gated stage campaigns, open-world quest graphs, mission objective variety, or the livesheet schema. Numbers are heuristics.

## Structure families

| Family | Shape | Best for | Main risk |
| --- | --- | --- | --- |
| Linear chapters | Fixed mission order | Premium action, mobile mid-core | Flat middle; one wall blocks everything |
| Stage campaign (power-gated) | Hundreds of short stages, recommended power per stage | Idle RPG, hero collectors, puzzle-RPG | Walls feel like paywalls without side doors |
| Branching chapters | Choice of 2–3 missions per node, reconverge at boss | Strategy, roguelite campaigns | Players optimize, skip variety |
| Hub and spoke | Hub unlocks parallel mission sets | Open-ended action, mission-select games | Uneven difficulty between spokes |
| Open-world quest graph | Main quest acts plus side quests gated by state | Open-world RPG and gacha RPG | Level/power mismatch, players over- or under-leveled |
| Live quest chains | Daily/weekly chains, event chains | Any live game | Repetition; chores instead of beats |

## Mission objective archetypes (rotate them)

| Archetype | Verb emphasis | Pace | Notes |
| --- | --- | --- | --- |
| Eliminate | Combat | High | Default; overuse flattens the curve |
| Survive / defend | Positioning | High, timed | Clear timer and wave count in UI |
| Escort | Protection | Medium | Escortee must match player speed and be durable; hated when fragile |
| Reach / chase | Traversal | High | Good set pieces; strong checkpointing |
| Collect / gather | Exploration | Low–medium | Use as rest beats |
| Puzzle / manipulate | Reasoning | Low | Good valley after peaks |
| Stealth | Avoidance | Low, tense | Fail-forward options reduce frustration |
| Boss | Exam | Peak | Examines mechanics taught in chapter |
| Story / rest | Narrative | Low | Short; ends with a question |

Rule of thumb: in any window of 5 missions, at least 3 archetypes.

## Stage campaign (power-gated) specifics

- **Stage count and pacing.** Stages are short (1–3 min); hundreds exist. Plan in bands of 20–40 stages with a boss stage per band.
- **Recommended power curve.** Fit recommended power to projected p50 player power on the expected day of arrival, then decide where gap exceeds 1.0 on purpose.
- **Alternate progress sources** during walls: idle/AFK rewards, daily dungeons, tower/trial modes, event rewards, hero/gear upgrades from duplicates. At least two must be active when a hard wall is planned.
- **Auto-battle / sweep.** Cleared stages should be sweepable; replaying cleared content manually is a chore, not a beat.
- **Wall messaging.** Show the gap ("Recommended 12,400 — yours 10,900") with one-tap routes to the upgrades that close it; hiding the gap converts it into confusion.
- **Ethics.** A wall whose only realistic resolution is payment within its planned duration is a paywall; review with `gamedev-monetization-designer`.

## Open-world quest graph specifics

- **Main quest acts** gated by state flags, not by level alone; recommended level displayed per quest.
- **Side quest density**: a side activity within ~1–3 minutes of travel from any point on the main path (heuristic).
- **Over-leveling control**: scale rewards, not enemies, when the player is far above recommended level; scaling enemies to the player erases the feeling of growth.
- **Quest log hygiene**: no more than ~5–8 active tracked quests surfaced at once; more becomes a to-do list.

## Livesheet schema (mission tunables in data)

```yaml
mission:
  id: ch02_m04
  type: combat
  objective: { kind: eliminate, count: 24 }
  space: docks_b
  mechanics: { teach: [], test: [], twist: [dash, shield_foes] }
  tension: 4
  targets:
    first_attempt_win: 0.75
    minutes: 4
  waves:
    - { enemies: { grunt: 6, shield: 2 }, delay_s: 0 }
    - { enemies: { grunt: 4, shield: 4 }, delay_s: 20 }
  recommended_power: 3200        # omit for skill-gated campaigns
  checkpoints: [wave_2]
  rewards:
    first_clear: { soft: 600, xp: 120, item: shard_common_x5 }
    stars: { 1: clear, 2: hp_above_50, 3: under_180s }
  version: 7
```

Every change bumps `version`, and analytics events carry `mission_id` plus `version`, so funnels before and after a retune are never mixed.

## Mission funnel events (minimum set)

```
mission_start   { mission_id, version, attempt_n, player_power, boosters }
mission_end     { mission_id, version, attempt_n, result: win|fail|quit, duration_s, fail_cause, stars }
```

`attempt_n` and `fail_cause` are the two fields most often missing; without them first-attempt win rate and boss diagnosis are impossible.
