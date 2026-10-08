# Frame Data, Hit/Hurt Boxes, and Touch-Control Combat

Read when writing a frame table for player or enemy moves, defining cancel and buffer rules, setting hitbox policy, or adapting real-time combat to a phone. All numbers marked "heuristic" are starting points to validate in playtests, not standards.

## 1. Timing model

Every attack is a timeline of four phases, stored in fixed simulation ticks and documented in milliseconds.

```
 |--- startup ---|-- active --|------ recovery ------|
 ^ input         ^ hitbox on  ^ hitbox off           ^ next action allowed (without cancel)
                 |<- hit-stop inserted here on contact (freezes both sides)
         |<--------- cancel window (into: dodge / skill / next combo link) --------->|
 |<- buffer: inputs pressed this long before "next action allowed" are queued ->|
```

| Tick rate | 1 tick | 100 ms = | 250 ms = | 500 ms = |
| --- | --- | --- | --- | --- |
| 30 Hz | 33.3 ms | 3 ticks | 7.5 ticks | 15 ticks |
| 60 Hz | 16.7 ms | 6 ticks | 15 ticks | 30 ticks |
| 120 Hz | 8.3 ms | 12 ticks | 30 ticks | 60 ticks |

Rules:
- **Simulation tick is fixed** (60 Hz is the common choice for action combat); rendering interpolates. A device throttled to 30 fps renders fewer frames but the combat clock does not change.
- **Round to ticks, not frames.** At 30 Hz any window under 33 ms vanishes; a 2-tick active window at 60 Hz (33 ms) is the practical minimum for anything a player is meant to hit deliberately.
- **Animation clips are authored to the frame table**, not the other way round. Hand animation a spec of the form below before the clip exists.

## 2. Frame table template

```
MOVE:      [name]            OWNER: [player hero / enemy]      SIM TICK: 60 Hz
           startup   active   recovery   total   hit-stop   hitstun   blockstun   adv(hit)   adv(block)
ms         [ ]       [ ]      [ ]        [ ]     [ ]        [ ]       [ ]         [ ]        [ ]
ticks      [ ]       [ ]      [ ]        [ ]     [ ]        [ ]       [ ]         [ ]        [ ]
CANCELS:   into [dodge | skill | light 2] from tick [ ] to tick [ ]
BUFFER:    [ms] before end of recovery / cancel start
ARMOR:     [none | hyper-armor ticks a–b | super-armor]   (hyper-armor = takes damage, ignores stagger)
INVULN:    [ticks a–b, if any]
TELEGRAPH: earliest readable cue at tick [ ] (= [ms] before first active tick); cue type [anim pose | VFX | audio | ground decal]
```

### Reference frame tables (heuristic, 60 Hz)

| Move class | Startup | Active | Recovery | Notes |
| --- | --- | --- | --- | --- |
| Player light (combo 1) | 5–9 ticks (80–150 ms) | 2–4 | 10–16 | Cancel into dodge from first active tick |
| Player light finisher | 8–12 | 3–5 | 18–26 | Bigger damage, punishable recovery |
| Player heavy | 15–27 (250–450 ms) | 3–6 | 20–35 | Hyper-armor during late startup is common |
| Player dodge | 2–4 | i-frames 9–18 (150–300 ms) | 8–14 | Perfect-dodge window = first 4–6 i-frame ticks |
| Enemy fodder swing | 24–36 (400–600 ms) | 3–6 | 20–40 | Generous recovery = free punish |
| Enemy rusher lunge | 18–30 + travel | 6–10 | 30–45 | Telegraph by pose, not only VFX |
| Enemy brute slam | 42–60 (700–1,000 ms) | 4–8 | 45–70 | Ground decal at startup tick 0 |
| Boss heavy | 42–72 (700–1,200 ms) | varies | 40–90 | Audio cue for off-screen attacks |

### Frame advantage

```
adv_on_hit   = hitstun   − (active_remaining + recovery)
adv_on_block = blockstun − (active_remaining + recovery)
punishable   if  −adv_on_block > fastest_opponent_startup
```

Use: every heavy commit is punishable on block by at least the fastest light; every light poke is at worst −2 to +2 on block (heuristic). In PvE-only games, apply the same idea to enemies: their recovery after a whiff is the player's reward window, and it must exceed the player's light-attack startup plus reaction time if you want punishes to be reactive rather than pre-planned.

## 3. Reaction budget

```
required_telegraph_ms ≥ reaction_ms + input_latency_ms + defensive_startup_ms + margin_ms
```

| Term | Value to assume (heuristic) | Source of the number |
| --- | --- | --- |
| reaction_ms | 250 for a mobile audience, 200 for core PC/console audiences | Measure in a playtest with a reaction mini-task |
| input_latency_ms | touch 50–100 ms beyond display latency; controller lower | Measure on the slowest supported device tier |
| defensive_startup_ms | your dodge/block startup | Frame table |
| margin_ms | 100 | Covers frame drops and attention split |

Worked: 250 + 80 + 66 (4-tick dodge) + 100 = **496 ms**. A 400 ms enemy swing is not reactable on touch; it becomes a memorization check. Fixes, in order: lengthen startup, add an earlier cue (audio/decal at tick 0), shorten dodge startup, widen i-frames. Do not "fix" it with more HP for the player — that hides the problem and inflates TTD.

## 4. Hit and hurt boxes

Fairness is perceived. The player compares the hitbox against the art, not against the collision shape.

| Box | Policy (heuristic) | Why |
| --- | --- | --- |
| Player hurtbox | 80–90% of the sprite/mesh silhouette, torso-weighted; exclude weapon and trailing limbs | Near-misses read as skill, not luck |
| Player attack hitbox | 100–115% of the weapon trail, active only on active ticks | Hits that look like they connect must connect |
| Enemy attack hitbox | ≤ 100% of the visible weapon/VFX; never extends past the decal | A hit outside the art is a "cheap" death report |
| Enemy hurtbox | 100–110% of silhouette | Generous targeting, especially on touch |
| Projectile | Hitbox ≤ visual core; grazing near-miss feedback optional | Bullet-hell players read the core, not the glow |

Additional rules:
- **Hitbox active only on active ticks.** A hitbox that lingers into recovery causes "I got hit after the swing ended".
- **One hit per target per swing** unless the move is designed as multi-hit; track a per-swing hit set.
- **Hurtbox shrinks during dodges** only if i-frames are not used; do not stack both.
- **Networked PvP:** hit resolution policy (server rewind, favor-the-shooter windows) belongs to `gamedev-netcode-engineer`; give them this table and the frame data.
- **Debug draw is mandatory** in dev builds: boxes colored by type, tick counter overlay, and a slow-motion toggle. Disputes about hits are settled by replay, not memory.

## 5. Real-time combat on touch

| Element | Spec (heuristic) | Note |
| --- | --- | --- |
| Virtual stick | Floating origin in the left 40% of the screen; dead zone 10–15% of radius; max radius 60–80 pt | Fixed sticks drift away from the thumb |
| Skill buttons | Right-thumb arc, 3–4 buttons, primary ≥ 64 pt, others ≥ 48 pt | Thumb-reach mapping is in `mobile-game-ux-designer` if installed |
| Auto-attack | Fires when stationary or on attack button hold; target chosen by priority list | Removes tap-spam fatigue |
| Target priority | In-facing-cone nearest → lowest HP% → last attacked; boss always selectable by tap | Write it as an ordered list in the spec |
| Soft lock / magnetism | Cone 30–45°, range 1.2× attack reach; slide up to 0.5 m toward target on attack startup | Touch aim cannot be precise |
| Aimed skills | Drag from button to aim; release to cast; cancel by dragging back to button | Show the AoE shape while dragging |
| Dodge | Swipe or dedicated button; swipe direction from stick, not swipe vector, if both thumbs busy | Swipe on the stick side conflicts with movement |
| One-thumb mode | Move-or-attack: attack automatically when stationary, move by dragging (Archero-style) | The entire skill expression becomes positioning |

**One-thumb design consequence:** when attacking and moving are exclusive, enemy projectile density and telegraph lengths become the difficulty dial. Budget "stationary time" per room: if enemies leave less than 40% of time safe to stand still (heuristic), DPS uptime collapses and TTK balloons — the uptime term in the DPS equation is now controlled by enemy design.

## 6. Cancel and combo rules

- **Gatling/link list per move:** which moves it may cancel into and from which tick. Keep it a table, not prose.
- **Dodge-cancel from active frames** is the single biggest responsiveness lever in mobile action; the cost is that heavy commits lose meaning, so heavy attacks should cancel into dodge only after active frames end.
- **Combo damage scaling** to stop infinite or touch-of-death combos: each successive hit in a combo deals `max(floor, 1 − 0.1 × (n − 1))` of base (heuristic, floor 0.3–0.5).
- **Juggle/stagger limits:** a stagger meter that fills per hit and grants brief poise when full prevents permanent lock on enemies and on players.
