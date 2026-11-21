# Spatial Layout Reference — action, shooter, lane and strategy maps

Read when greyboxing a 3D/2D action level, a competitive map, a MOBA/lane map, or an RTS/4X world. All numbers are heuristics: they are starting points to be overwritten by your own metrics gym. Measure first, then derive.

## Metrics gym (build before any map)

A flat test level containing, at minimum:

- Jump/climb blocks at 0.25 m increments up to 1.5× max jump height (find the exact "can't quite make it" height).
- Gap widths at 0.5 m increments up to 1.5× max jump distance.
- Corridors at 1.5, 2, 3, 4, 6 m widths; doors at 1, 1.5, 2 m.
- Cover pieces at 0.6, 1.0, 1.4, 2.0 m.
- Range lines every 5 m to 100 m with targets, for each weapon class.
- A timed route (start pad to end pad) for travel-time measurements.

Record the results in the Spatial Layout Brief. Every later rule is expressed relative to these values, so a speed change later is a single recalculation, not a redesign.

## Dimensions (heuristic, human-scale 3D character ~1.8 m)

| Element | Starting value | Why |
| --- | --- | --- |
| Single-file door | 1.5–2.0 m wide | Camera clipping under 1.5 m in third person |
| Two-abreast corridor | 3–4 m | Allows passing and strafing |
| Combat room | 3–6× engagement radius per side | Room for movement decisions |
| Low cover (crouch) | ~1.0 m | Hides crouched body, exposes standing |
| Full cover | ≥ 2.0 m | Blocks standing body |
| Ledge "must jump" | ≤ 80% of max jump height | Margin for imprecise input |
| Gap "must jump" | ≤ 85% of max jump distance | Same; fail rates spike past 90% |
| Third-person camera clearance | ≥ 2.5 m ceiling in combat spaces | Camera collision ruins aim |

## Engagement ranges and sightlines (shooter)

| Band | Distance | Layout implication |
| --- | --- | --- |
| Close | under 10 m | Corners, doorways, verticality; favors shotguns/melee |
| Mid | 10–30 m | Default for most rooms and courtyards |
| Long | 30–60 m+ | One or two lanes per map, with cover breaks every ~15–20 m |

Rule: break any uninterrupted sightline longer than the median weapon's effective range, unless the line is a deliberate sniper lane with a counter-route.

## Timing targets

| Map type | Spawn-to-first-contact | Notes |
| --- | --- | --- |
| Arena shooter / brawler | 5–15 s | Short loops, constant pickups |
| Tactical round-based | 15–40 s | Defender should reach the site 3–8 s before the attacker's fastest route |
| Objective mode (payload/zone) | 10–25 s | Respawn walk must be short enough not to decide the match |
| Mobile MOBA lane | 20–45 s base-to-lane | Match length 10–20 min on mobile |
| Mobile top-down arena (3–5 min matches) | 5–12 s | Players expect action within the first quarter minute |

Flank routes: 10–30% longer travel time than the main route. Under 10% and the main route is pointless; over 30% and nobody takes the flank.

## Flow patterns

- **Loop, not dead end.** Every area has at least two exits, except deliberate reward pockets.
- **Three-lane rule** for competitive maps: left, middle, right, with 2–3 connectors between them. More lanes splits teams too thin at 5v5 and under.
- **High ground costs exposure.** Any position with height advantage has at least one approach that reaches it with cover.
- **Landmarks per decision point.** A unique silhouette, color or light visible from every junction.
- **Leading lines.** Lighting, geometry and contrast point at the critical path; the player should find the exit without a waypoint marker at least 80% of the time in playtests.
- **Rest beats.** After every high-intensity encounter, a low-threat space of 15–60 s for reload, loot and narrative.

## Competitive fairness checks

- Mirror or rotational symmetry for ranked modes unless asymmetry is the design.
- Asymmetric maps: spawn-to-objective travel times per side within ±5%; per-side win rate 45–55% after 1,000+ matches; adjust timings, not just geometry.
- Pickups and power positions equidistant from each spawn within ±5% travel time.
- No spawn in line of sight of any position reachable by enemies within 5 s.

## RTS / 4X / strategy maps

| Check | Target (heuristic) |
| --- | --- |
| Starting position distance to nearest opponent | Equal across slots within ±5% path length |
| Safe expansion sites per player | Same count, same travel time ±10% |
| Contested resource sites | On or near the axis between players, not behind either base |
| Rush distance (fastest unit, base to base) | Long enough that scouting can see it coming: 60–120 s in RTS |
| 4X tile resources | Per-start yield within ±10% in a radius of 3–5 tiles; validate across 100+ generated seeds |
| Chokepoints on main routes | Each has a bypass costing 20–40% more travel |

For mobile 4X (city on a shared world map), the layout problem shifts to density: plan alliance-territory zoning, resource-tile tiers by ring from the center, and migration rules so new servers do not leave late joiners boxed in.

## Validation with telemetry

- **Death and engagement heatmaps.** Expect clusters at designed contact zones; clusters elsewhere mean an unplanned sightline or choke.
- **Route usage.** Each designed route should carry at least 15% of traversals; under 5% means it is dead geometry.
- **Time in combat.** Action levels typically land at 30–60% of play time in combat; above 70% exhausts, below 20% bores (genre-dependent).
- **Exit-finding time.** Median time from room entry to correct exit; spikes mean the critical path is unreadable.
