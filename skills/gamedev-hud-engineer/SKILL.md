---
name: gamedev-hud-engineer
description: >-
  Design and implement game HUDs that read in a glance and cost almost nothing
  per frame: information hierarchy, diegetic vs non-diegetic choices, damage
  numbers, minimaps, health and resource bars, notification queues, safe areas
  and notches, aspect-ratio scaling, and HUD performance in Unity UGUI, UI
  Toolkit, SpriteKit, Compose overlays and UMG. Use when a user asks to lay out
  or rebuild a HUD, fix canvas rebuild or overdraw spikes, add combat text or a
  minimap, handle the Dynamic Island or ultra-wide screens, or test whether
  players can read the HUD mid-fight.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: ux-ui
---

# HUD Engineer

The HUD is the only UI the player reads while their attention belongs to something else. Everything on it competes with the game for the same 200 milliseconds of glance, and every element that does not change a decision in the next few seconds is stealing that glance and some frame time besides. A good HUD is a priority queue rendered to screen: a handful of persistent facts the player checks constantly, transient events that appear only when they matter and leave on their own, and nothing that rebuilds a canvas because a number did not change. Design the hierarchy first, then make the implementation update only what changed, only when it changed.

Interpretation note: screen layout grids, visual style, iconography and the UI design system belong to `gamedev-ui-designer`. This skill owns HUD information design (what is shown, when, with what priority) and its implementation and performance.

## Role Profile

At top studios the HUD/UI engineer owns the in-game UI framework and the HUD that every feature team plugs into. Supercell's Project R.I.S.E. posting (Unreal) asks to "build and maintain a modular, data-driven UI framework" for progression surfaces such as talent trees and season passes, keep UI responsive in fast combat across mouse, keyboard and touch, and profile memory and frame-time budgets. Unity variants own menus, HUD and inventory in C# and are judged on cutting draw calls, memory and frame drops.

- **Hard skills:** Unity UGUI and/or UI Toolkit (or Unreal UMG), C#, sprite atlases, data binding, multi-resolution and safe-area layout, profiling UI cost on mobile.
- **Seniority signals:** owns the UI framework and data-binding architecture used by all feature teams.
- **Judged on (inferred):** UI frame time and draw calls, UI feature throughput, UI bug and regression rate.
- **Collaborators:** UI artists, UX designers, client, server and tools engineers.
- Sources: https://jobs.accel.com/companies/space-ape-games-2/jobs/68314184-senior-ui-programmer-project-r-i-s-e , https://dynamic.jobgether.com/offer/67d48b8cc1e6069f46f5b47e-senior-unity-developer-ui

## When to Use / Not

Use for HUD information hierarchy, combat feedback text, minimaps, bars, notification stacking, safe-area and aspect handling, HUD performance, and HUD readability testing.

Not for:
- Screen layout grids, visual style, icon set, typography system, shop screens: `gamedev-ui-designer`.
- Flows, menus IA, FTUE strategy: `gamedev-ux-designer`.
- Thumb zones, touch targets, virtual stick placement: if installed, `mobile-game-ux-designer`.
- Hit-stop, shake, juice timing: `gamedev-game-feel-designer`.
- Colorblind modes, text scaling, subtitles as a program: `gamedev-accessibility-specialist`.
- Whole-game frame budget and device tiers: `gamedev-optimization-compatibility`.

## Inputs to Gather

- **Genre and attention model:** twitch combat, tactical, puzzle, idle. Default: action-mobile, glance under 300 ms.
- **The decision list:** what the player must decide every few seconds, every minute, every session. The HUD serves this list, nothing else.
- **Platform and input:** touch, gamepad, KB/M; orientation. Default: landscape touch phone.
- **Tech stack:** UGUI, UI Toolkit, SpriteKit, Compose shell, UMG. Default: Unity UGUI with TextMeshPro.
- **Frame budget for UI** from `gamedev-optimization-compatibility`. Default: HUD at or under 1.0 ms CPU and 2 draw-call batches per canvas on the floor device at 60 fps.
- **Aspect range:** from 4:3 iPad to 21:9+ phones and foldables. Default: design at 16:9, verify 4:3 and 20:9/21:9.
- **Localization:** longest language, CJK/RTL needs (`gamedev-localization-specialist`).
- **Peak event rates:** damage events per second, simultaneous notifications at worst case (boss fight, reward burst).

## Method

1. **Write the decision inventory.** For each HUD candidate record: the decision it informs, how often it is read, cost of misreading. Elements that inform no decision within a session are menu content, not HUD.
2. **Assign glance tiers** (see Technical Reference). Tier 1 earns persistent, high-contrast, fixed-position space; tier 3 appears on demand. Why: fixed position is what makes a glance cheap — the eye goes there without search.
3. **Choose the representation per element** on the diegetic / non-diegetic / spatial / meta axis. Prefer spatial or diegetic for information tied to a world object (enemy health over the enemy), non-diegetic for player-owned state.
4. **Place within safe areas, by corner role.** Persistent state in the corners away from thumbs, transient events near the center-top, critical warnings close to the point of action. Read the platform safe area at runtime; never hardcode notch insets.
5. **Define event rules before art:** max concurrent damage numbers, merge window, notification priority classes, TTLs, and what is dropped under load. Why: the HUD fails at peak load, not in the mockup.
6. **Architect for change-only updates.** HUD views subscribe to model change events (or poll a version counter) and touch text/graphics only when the value differs. No per-frame `text =` assignments.
7. **Split canvases by update frequency**: static frame, slow (currency, level), fast (bars, timers), and transient (damage text, toasts). Any change dirties the whole canvas it sits on.
8. **Pool all transient elements** and prewarm to the measured worst-case concurrency.
9. **Scale for aspect** with a reference resolution and match rule, then anchor to safe-area-aware containers. Test at 4:3, 16:9, 19.5:9, 21:9 and a foldable inner screen.
10. **Profile on the floor device** at peak event rate: UI CPU (layout, rebuild, batch), draw calls, and GPU overdraw.
11. **Run readability tests** — glance tests, small-device and distance tests, contrast and colorblind simulation, and a combat playtest — and fix misreads before polishing art.

## Deliverables

### 1. HUD element spec (one row per element)

```
Element        │ Decision it serves        │ Tier │ Type        │ Position (safe-area anchor) │ Update trigger    │ Canvas │ Pool │ Max on screen
Health bar     │ retreat / heal now?       │ 1    │ non-diegetic│ top-left                    │ on HP change      │ Fast   │ —    │ 1
Ability CDs    │ which ability is ready    │ 1    │ non-diegetic│ bottom-right (thumb arc)    │ on CD start/end   │ Fast   │ —    │ 4
Enemy HP       │ focus target              │ 2    │ spatial     │ world-anchored above unit   │ on damage         │ World  │ yes  │ 8
Damage numbers │ is my build working       │ 2    │ spatial     │ world → screen              │ on hit (merged)   │ Trans. │ yes  │ 24
Currency       │ can I afford upgrade      │ 3    │ non-diegetic│ top-right                   │ on change         │ Slow   │ —    │ 1
Toasts         │ new reward / quest done   │ 3    │ meta        │ top-center                  │ queued            │ Trans. │ yes  │ 3
```

### 2. Event rules sheet

```
DAMAGE TEXT:   merge window [150] ms per target   max concurrent [24]   crit: scale [1.4x] + color + 2nd font weight
               overflow: drop lowest-value non-crit first   lifetime [0.6–0.9] s   rise [40–80] px
BARS:          main bar snaps on damage; ghost bar holds [0.3–0.5] s then lerps at [~1.5x] HP/s; heal: ghost leads
NOTIFICATIONS: classes P0 critical (interrupt) / P1 gameplay / P2 reward / P3 social
               max visible [3]   TTL P1 [2.5] s, P2 [3.5] s   coalesce same key within [1.5] s ("+3 Gems" → "+7 Gems")
               combat-suppressed classes: [P2, P3] queued until combat ends
MINIMAP:       mode [icon layer | render texture]   refresh [10] Hz   icons max [40]   culled outside radius
```

### 3. HUD performance report

```
DEVICE / BUILD / SCENE STATE (peak: boss + 20 damage events/s)
Canvas        │ Rebuilds/s │ Batches │ Layout ms │ Graphic rebuild ms │ BuildBatch ms │ Verts
Static        │ 0          │         │           │                    │               │
Slow          │ ≤ 1        │         │           │                    │               │
Fast          │ ≤ 60       │         │           │                    │               │
Transient     │ ≤ 60       │         │           │                    │               │
Total UI CPU [..] ms (budget 1.0)   UI draw calls [..]   overdraw (full-screen layers) [..]
FINDING → CHANGE → DELTA
```

### 4. Readability test plan

```
GLANCE TEST:   show frozen HUD frame [250] ms → ask [HP state, ability ready, threat dir]   pass: ≥ 85% correct
DEVICE TEST:   smallest supported phone, arm's length; largest tablet; 21:9 phone
CONTRAST:      tier-1 text/icons ≥ 4.5:1 against worst-case background capture; bars ≥ 3:1
COLOR:         protan/deutan/tritan simulation; no state carried by hue alone
MOTION:        reduce-motion setting removes shake/scale pulses on HUD
PLAYTEST:      deaths with "didn't see low HP"; missed ability ready; toast-tap mis-taps
```

Read `references/unity-hud.md` when implementing in Unity (UGUI or UI Toolkit). Read `references/native-hud.md` when implementing in SpriteKit/SwiftUI or a Compose overlay on Android.

## Technical Reference

### Glance tiers

| Tier | Read frequency | Examples | Treatment |
|---|---|---|---|
| 1 Critical state | every 1–3 s | HP, ammo, ability readiness, timer in a race | Persistent, fixed position, largest, highest contrast, peripheral-readable (shape/fill, not text) |
| 2 Situational | every 5–30 s | Enemy HP, objective direction, combo, minimap | Spatial or contextual; appears when relevant, fades when not |
| 3 Session | per minute or menu | Currency, XP, quest log, social | Small, corner, or hidden during combat |
| Events | on occurrence | Damage, rewards, kills, warnings | Transient, queued, TTL, merged |

Heuristic: no more than 5–7 persistent tier-1/2 elements during combat; beyond that players stop reading and start ignoring.

### Representation taxonomy

| Type | Exists in game world | Exists in fiction | Example | Use when |
|---|---|---|---|---|
| Diegetic | yes | yes | Ammo counter on the gun, Dead Space spine HP | Immersion matters and the info sits on a world object |
| Non-diegetic | no | no | Classic HP bar, currency | Player-owned state, needs fixed position |
| Spatial | yes | no | Enemy HP above head, waypoint marker | Info tied to a world location |
| Meta | no | yes | Blood-splatter screen edges, cracked screen | Mood/state feedback, never sole carrier of exact values |

### Damage text

- Pool and prewarm to measured worst-case concurrency; 16–32 is typical for mobile action (heuristic).
- Merge hits on the same target within a 100–200 ms window into one rising number; DoT ticks always merge.
- Crit styling uses at least two channels (size + color, or size + weight) so it reads without color.
- Stagger spawn offset (random ±20–30 px horizontal) to avoid stacking on one pixel.
- Overflow policy: drop the smallest non-crit, never queue — late damage text is wrong information.
- Use world-space projection once per frame per number, or a single mesh-batched text system; one canvas per number is a classic mistake.

### Bars

- Main fill snaps to the new value immediately (truth); a ghost/delayed bar holds 0.3–0.5 s then catches up — the ghost shows how much was just lost.
- On heal, invert: ghost jumps ahead in the heal color, main fill lerps up.
- Segment bars when integer thresholds matter (every 100 HP, shield pips); segments read faster than a percentage.
- Low-HP threshold (e.g. under 25%) adds a non-color cue: pulse, icon, or edge vignette.
- Lerp with frame-rate-independent smoothing: `value = target + (value - target) * exp(-k * dt)`.

### Minimap

| Approach | Cost | Use when |
|---|---|---|
| Icon layer over a static pre-baked map image | Very low: a few quads | Most mobile games; map is static |
| Second camera to a RenderTexture | An extra scene render; at 256x256 still a full culling and draw pass | Dynamic terrain, fog of war needs world geometry |
| Shader-masked circular icon layer | Low | Rotating minimap with many icons |

Update icon positions at 10–15 Hz, not every frame; cull icons outside the radius before positioning; cap icon count and cluster the excess.

### Safe areas and aspect ratio

- Unity: `Screen.safeArea` (pixels, bottom-left origin); recompute on resolution or orientation change.
- iOS: `view.safeAreaInsets` / `safeAreaLayoutGuide`; landscape iPhones with a notch or Dynamic Island have left/right insets and a bottom home-indicator inset. Inset values vary by model; example magnitudes are roughly 44–62 pt on the sensor side in landscape and about 21 pt at the bottom (example only; read at runtime).
- Android: `WindowInsets` with `displayCutout()` and `systemBars()`; set `layoutInDisplayCutoutMode` (`shortEdges` or `always` in landscape games) or the system letterboxes the cutout side.
- Keep backgrounds full-bleed; keep interactive and readable content inside the safe area.
- Canvas Scaler (UGUI): Scale With Screen Size at 1920x1080 reference; match 0.5 is a common compromise; landscape games that must keep vertical size for readability lean toward height (1.0); portrait toward width (0.0). Check 4:3 (iPad: the long side shrinks, corners collide) and 21:9 (elements drift outward; cap max width of the center column).
- Foldables: treat inner screen as near-square tablet; reload layout on configuration change rather than stretching.

### Performance: Unity UGUI

| Cause | Mechanism | Fix |
|---|---|---|
| Any change dirties its Canvas | Canvas re-batches all its children (`Canvas.BuildBatch` in profiler) | Split static / slow / fast / transient canvases; nested canvases isolate rebuilds |
| Layout Groups / ContentSizeFitter on dynamic elements | A text change triggers layout rebuild up the hierarchy | Fixed anchors in HUD; layout groups only on static or rarely-changing panels |
| Setting text every frame | Graphic rebuild + allocation | Change-only updates; TMP `SetText("{0}", value)` avoids string allocation |
| Animator on UI elements | Animator dirties every frame even when idle | Tween library or code-driven animation that stops when done |
| Raycast Target on decorative graphics | GraphicRaycaster walks them on every touch | Disable Raycast Target on everything not clickable; remove GraphicRaycaster from non-interactive canvases |
| Mixed atlases / fonts / materials | Batch breaks | Sprite Atlas per HUD; one font asset per weight; avoid interleaving text and images in sibling order |
| Full-screen transparent images (vignettes, dim layers) | Overdraw, each pixel shaded repeatedly | Disable when alpha 0 (set inactive, not alpha 0); use smaller sliced or mesh vignettes |
| Disabling via `SetActive` on canvas children constantly | Triggers rebuilds | Toggle `Canvas.enabled` or `CanvasGroup.alpha` with `blocksRaycasts` false for frequent show/hide |

Heuristic targets: zero rebuilds on the static canvas after load; HUD batches under 10; UI CPU at or under 1 ms on the floor device.

### Performance: other stacks

- **UI Toolkit:** retained mode; style with USS; change only bound values. Set `usageHints` (e.g. `DynamicTransform` for elements that move every frame) so transforms update without re-tessellation. Dynamic atlas packs small textures automatically; oversized textures fall out of it and break batching. World-space and some HUD features differ by Unity version (as of 2026-10; verify).
- **SpriteKit:** watch `SKView.showsNodeCount`, `showsDrawCount` and `showsFPS`; use texture atlases; set `ignoresSiblingOrder = true` and use `zPosition` for layering so the renderer can batch; avoid `SKLabelNode` text updates every frame. SpriteKit is not deprecated but stagnant, with reported frame-rate regressions across iOS 26.x (as of 2026-10; verify).
- **Compose overlay on Android:** run the game on a SurfaceView/GameActivity; add a `ComposeView` sibling for menus and light HUD; handle touch pass-through explicitly; never draw game-rate content on a Compose Canvas, since it runs on the main thread. The overlay pattern is practice, not an official recommendation (as of 2026-10; verify).
- **Unreal UMG:** use Invalidation Boxes around static widget trees and Retainer Boxes to render rarely changing panels at reduced rate; avoid property bindings (polled every frame) in favor of event-driven updates.

## Diagnostics

| Symptom | Likely cause | Fix |
|---|---|---|
| UI CPU spikes during combat | Damage text and bars on the same canvas as static frame | Split canvases; move transient text to its own canvas or batched text mesh |
| GC allocations every frame from HUD | `text = value.ToString()` per frame | Change-only updates; TMP `SetText` with format |
| `Canvas.SendWillRenderCanvases` heavy | Layout rebuilds from Layout Groups/ContentSizeFitter | Remove layout components from dynamic HUD |
| HUD clipped by notch on some phones | Hardcoded margins or ignoring left inset in landscape | Safe-area fitter on root container, recompute on change |
| Android black bar on cutout side | `layoutInDisplayCutoutMode` default | Set `shortEdges`/`always`, then apply insets |
| Players die "without noticing" low HP | Low-HP state only a color change, or bar in a cold corner | Add shape/motion cue, move bar nearer focus, test glance |
| Toasts cover action during fights | No combat suppression or priority | Priority queue, suppress P2/P3 during combat |
| Damage numbers unreadable in AoE | No merge, no cap | Merge window per target, cap concurrency, drop lowest |
| GPU-bound only on menus over gameplay | Full-screen blur/dim layers stacked | One dim layer, half-res blur once, disable gameplay camera when fully covered |
| HUD drifts to screen edges on 21:9 | Corner anchors with width match | Cap center column width; anchor clusters to safe-area-aware containers |
| Minimap costs 2+ ms | Second camera rendering full scene each frame | Static map image + icon layer, or lower refresh rate and layer mask |

## Anti-Patterns

**The Dashboard HUD** — every stat persistent on screen because designers might want it. Nothing reads in a glance; the player ignores all of it.

**The Mega-Canvas** — the entire HUD on one canvas. A ticking timer re-batches every icon on screen 60 times a second.

**Per-Frame Text Assignment** — `label.text = hp.ToString()` in Update. Allocations, graphic rebuilds and layout passes for a number that did not change.

**The Hardcoded Notch** — margins tuned on one iPhone. Breaks on the next model, on Android cutouts, and in the other landscape orientation.

**Color-Only State** — low HP, crits or ready abilities signaled only by hue. Fails for colorblind players and in bright sunlight.

**The Unbounded Toast** — every event spawns a notification immediately. Reward bursts bury the screen and the critical warning arrives fourth in line.

**The Live Minimap Camera** — a second full scene render for a 200-pixel map. Icons on a static image would have done it for a few quads.

**Invisible But Rendered** — faded elements left active at alpha 0. Still batched, still overdrawn, still raycast.

**Layout Groups in Combat** — auto-layout on elements that change every frame. Layout rebuilds cascade up the hierarchy.

## Quality Checklist

- [ ] Every HUD element maps to a named player decision and a glance tier
- [ ] At most 5–7 persistent elements visible during combat
- [ ] Tier-1 state readable without color (shape, fill, position, or motion)
- [ ] Root containers fitted to the runtime safe area; recompute on orientation/resolution change
- [ ] Verified at 4:3, 16:9, 19.5:9, 21:9 and a foldable inner screen
- [ ] Canvases split by update frequency; static canvas shows zero rebuilds after load
- [ ] No Layout Groups or ContentSizeFitter on per-frame-changing elements
- [ ] Raycast Target disabled on all non-interactive graphics
- [ ] HUD values update only on change; no per-frame text assignment; 0 B GC per frame from HUD
- [ ] Damage text pooled, merged per target, capped, with an overflow drop policy
- [ ] Notification queue has priority classes, TTL, coalescing, max visible and combat suppression
- [ ] Minimap cost measured; updates at 10–15 Hz; icons culled and capped
- [ ] UI CPU at or under budget on the floor device at peak event rate
- [ ] Glance test pass rate at or above 85% for tier-1 questions
- [ ] Contrast at or above 4.5:1 for tier-1 text against worst-case backgrounds
- [ ] Longest localized strings fit without overflow in all HUD text slots

## Related Skills

`gamedev-ui-designer` owns the visual system, layout grids and icon set this HUD renders; `gamedev-ux-designer` owns flows and menu IA around it. Thumb reach, touch targets and control placement come from `mobile-game-ux-designer` if installed. `gamedev-game-feel-designer` sets the timing of hit feedback that damage text and bar animation must agree with; `gamedev-combat-designer` defines which combat facts the player must read. `gamedev-accessibility-specialist` sets text scale, colorblind and reduce-motion requirements; `gamedev-localization-specialist` covers text expansion, CJK and RTL in HUD slots. Engine-side implementation and GC discipline pair with `gamedev-unity-engineer`; native stacks with `gamedev-ios-engineer` (SpriteKit, safe areas) and `gamedev-android-engineer` (cutouts, Compose shells). UI frame budgets per device tier come from `gamedev-optimization-compatibility`; atlases, UI shaders and overdraw art fixes go to `gamedev-technical-artist`.
