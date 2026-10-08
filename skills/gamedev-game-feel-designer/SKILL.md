---
name: gamedev-game-feel-designer
description: >-
  Design and tune game feel: input responsiveness, hit-stop, screen shake, easing curves,
  squash and stretch, particles, sound and haptic timing, so every action reads and satisfies
  without slowing play. Use when a game feels floaty, laggy, mushy or flat, when tuning combat
  impact or a match-3 cascade, when specifying juice for a core verb, when adding phone haptics,
  when setting animation and UI transition timings, or when deciding how much feedback is too much.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: design
---

# Game Feel Designer

Feel is the player's proof that the game heard them. Every input gets an acknowledgment fast enough to feel caused, and every outcome gets feedback proportional to how much it matters. Most "bad feel" is not missing juice; it is latency, uniform intensity, or feedback that blocks the next input. Fix latency first, build a hierarchy second, add juice last. Juice on top of 150 ms of lag is a louder version of lag.

## Role Profile

No top-grossing studio in the research posts a "game feel designer" title. Feel is a shared responsibility owned in practice by the combat or gameplay designer, gameplay engineers, animators, VFX artists and audio, and polished by the most senior of them:

- HoYoverse's senior combat designer is asked to "prototype and polish with level designers, engineers and animators" across player mechanics, camera and traversal (https://builtin.com/job/senior-combat-designer-ca/1624266).
- Scopely spent more than a year tuning Monopoly GO's dice roll alone after pivoting the game to a casual "big red button" loop (https://mobilegamer.biz/scopelys-monopoly-go-three-years-of-iterating-to-greatness-and-one-big-pivot/). On a one-verb game, the verb's feel is the product.
- Dream Games' CEO describes a "Pixar's approach": few titles, extreme polish (https://www.pocketgamer.biz/dream-games-ceo-soner-aydemir-on-the-companys-expansion-into-new-markets).
- Playrix VFX roles list "atlases, batching, effects mechanics" — feel is constrained by the effects budget.

**Hard skills:** animation timing literacy (anticipation, follow-through, overshoot), easing and spring math, camera math, input pipeline and latency measurement, audio sync, haptics APIs, profiling. **Tools:** the engine's tween/timeline systems, a debug tuning panel, high-speed camera (240 fps) for latency, profilers, haptic design tools. **KPIs** (inferred): playtest feel ratings, first-session retention and session length, input-to-response latency on the low-tier device, frame time during peak effects. **Collaborators:** combat and level designers, animators, VFX/technical art, audio, gameplay and UI engineers, accessibility.

## When to Use / Not

**Use** for feedback design on any player verb, timing and intensity tuning, latency budgets, camera shake/zoom, hit-stop and slow motion, UI motion timing, haptics, and "feels off" diagnosis.

**Not:** combat numbers, frame data and TTK (`gamedev-combat-designer`); shader and particle implementation and overdraw budgets (`gamedev-technical-artist`); SFX creation and mixing (`gamedev-audio-designer`); HUD and damage-number layout (`gamedev-hud-engineer`); touch target sizes and gesture conflicts (if installed, `mobile-game-ux-designer`); motion sensitivity settings policy (`gamedev-accessibility-specialist`).

## Inputs to Gather

- **Feel target** — three adjectives and two reference clips. Default: "responsive, weighty, readable".
- **Verb inventory** — each player action and its frequency per minute. Frequency decides intensity budget.
- **Platform and frame rate** — target fps (30/60/120), input device (touch, pad, mouse), low-tier device model.
- **Measured latency** — input-to-photon on the low-tier device. If unmeasured, measure before anything else.
- **Engine systems available** — tween library, timeline, camera rig, haptics plugin, audio middleware.
- **Accessibility constraints** — reduce-motion setting, photosensitivity rules, haptics toggle. Default: all required.

## Method

1. **Measure latency before adding anything.** Film the screen and the finger with a 240 fps camera, count frames from contact to first visible change. Subtract nothing; this is what the player feels. Remove buffering (extra render queue frames, input polling on the wrong thread, animation that waits a frame to start) until the game adds no more than 1–2 frames over the device baseline.
2. **Acknowledge in one frame, resolve within 100 ms.** Every input gets an immediate state change (press scale, highlight, sound) on the next rendered frame, even if the outcome needs a server or a longer animation. The acknowledgment is what makes the game feel responsive.
3. **Rank verbs by frequency and weight.** High-frequency verbs (taps, swaps, basic attacks) get short, subtle, non-blocking feedback. Rare, high-stakes verbs (kills, level wins, rare drops) get the big effects. Write the ladder before tuning any single effect.
4. **Build the feedback stack per verb**: anticipation, action, impact (hit-stop, flash, shake, particles, SFX, haptic), follow-through, result (numbers, UI update). Specify each layer in milliseconds, not frames, so tuning survives a frame-rate change.
5. **Never block the next input with feedback.** Celebration plays in parallel with control, or is skippable on tap. A 600 ms win animation on a verb used 20 times a minute costs 12 seconds of every minute.
6. **Put every parameter on a live tuning panel.** Hit-stop ms, shake amplitude, easing durations, particle counts, haptic intensity: sliders, on-device, with A/B toggles. Feel is tuned by feel; a recompile per change kills iteration.
7. **Tune with on/off comparisons.** Play each effect enabled and disabled in alternation. Keep only what players miss when it is gone.
8. **Escalate, do not repeat.** Combos and cascades escalate one dimension per step (pitch, scale, particle count, shake), capped. Identical feedback on step 1 and step 8 reads as a machine.
9. **Check readability.** Effects must not hide the information the next decision needs: enemy telegraphs, board state, health. If a particle covers a telegraph, the particle loses.
10. **Ship accessibility and performance gates.** Reduce-motion and shake sliders, haptics toggle, flash limits, and a profiler pass on the low-tier device during the worst case (biggest combo, most enemies).

Read `references/feel-code.md` when implementing hit-stop, trauma-based shake, a tuning panel, or iOS and Android haptics — it holds short engine-level snippets.

## Deliverables

### 1. Feel Target Sheet

```
GAME/FEATURE:   [name]
ADJECTIVES:     [3 words, e.g. snappy / weighty / clean]
REFERENCES:     [2 clips, with timestamps and what to copy]
FRAME RATE:     [target fps]   LOW-TIER DEVICE: [model]
LATENCY BUDGET: input-to-photon ≤ [ms] measured on low tier (baseline [ms] + game ≤ 2 frames)
NEVER:          [e.g. no feedback blocks input > 100 ms on high-frequency verbs]
```

### 2. Feedback Stack Spec (one row per verb)

```
Verb │ Freq/min │ Weight (1–5) │ Ack (ms, what) │ Anticipation ms │ Hit-stop ms │ Flash ms │ Shake (trauma add) │
Particles (count, life ms) │ SFX (id, pitch var) │ Haptic (type, intensity) │ Follow-through ms │ Blocks input? (Y/N, ms) │ Reduce-motion variant
```

### 3. Escalation Ladder

```
Tier │ Trigger example        │ Hit-stop │ Shake trauma │ Particles │ SFX layer        │ Haptic     │ Camera
 1   │ tap / swap / light hit │ 0–40 ms  │ 0            │ 5–15      │ base             │ light tick │ none
 2   │ medium hit / 3-match   │ 40–80    │ +0.1–0.2     │ 15–40     │ base + body      │ medium     │ none
 3   │ heavy hit / special    │ 80–150   │ +0.3–0.4     │ 40–80     │ + low sweetener  │ heavy      │ 2–4% zoom punch
 4   │ kill / combo finisher  │ 150–250  │ +0.5–0.6     │ 80–150    │ + stinger        │ pattern    │ zoom + slow-mo 0.3×
 5   │ boss kill / level win  │ 250–400  │ +0.8         │ budget max│ + music stinger  │ pattern    │ slow-mo, freeze frame
```

### 4. Latency Report

```
Device │ fps │ Contact-to-first-pixel (ms, median of 20 taps) │ Baseline OS app (ms) │ Game overhead (ms) │ Fixes applied │ After
```

## Quantitative Reference

All ranges are heuristics from common practice; tune on device.

### Frame time and latency

| fps | Frame time | Note |
| --- | --- | --- |
| 30 | 33.3 ms | Each buffered frame is felt in action games |
| 60 | 16.7 ms | Default target for action on mobile mid/high tier |
| 120 | 8.3 ms | ProMotion/high-refresh; halve frame-based timings or use ms |

| Input-to-response | Perception |
| --- | --- |
| under ~50 ms | Feels instant for taps |
| 50–100 ms | Acceptable for taps and menus |
| 100–150 ms | Noticeable lag in action play |
| over ~150–200 ms | Sluggish; players overcorrect and miss |

Phone touch hardware and the OS compositor already consume a large share of this; measure the baseline with a native blank app and treat the remainder as your budget.

### Hit-stop (hit-lag)

| Hit weight | Duration | Notes |
| --- | --- | --- |
| Light | 0–50 ms | Often only on the victim |
| Medium | 50–100 ms | Attacker and victim |
| Heavy | 100–180 ms | Add flash 1–2 frames |
| Finisher | 180–300 ms + slow-mo 0.2–0.4× for 200–500 ms | Rare by design |

Freeze gameplay time only; keep audio, UI and input buffering running. Buffer inputs during hit-stop so a mashed attack lands the moment the freeze ends.

### Screen shake (trauma model)

- `trauma` in 0–1; each event adds to it; decay 1.0–2.5 per second (so a 0.5 add lasts ~200–500 ms).
- `shake = trauma²` (or `trauma³` for a sharper tail) multiplied by max offset.
- Max translation: 0.5–1.5% of the short screen edge on phones, 1–3% on TV/PC; max rotation 1–3°.
- Drive with smooth noise at 15–30 Hz, not per-frame random values, which jitter instead of shake.
- Directional shake along the hit vector reads better than omnidirectional for single hits.
- Expose a 0–100% shake slider; default 100%, and honor the system reduce-motion setting by defaulting lower.

### Easing and UI motion

| Element | Duration | Curve |
| --- | --- | --- |
| Button press | 50–80 ms to 0.92–0.96 scale | ease-out |
| Button release | 100–150 ms | ease-out with slight overshoot |
| Popup enter | 200–300 ms | ease-out-back (overshoot 1.1–1.7) |
| Popup exit | 150–200 ms | ease-in; exits 20–30% faster than entries |
| Screen transition | 250–400 ms | ease-in-out |
| Reward fly-to-wallet | 400–800 ms, stagger 30–60 ms per item | arc + ease-in on arrival, punch the counter |
| Counter roll-up | 0.5–1.5 s scaled by amount | ease-out; skippable |

Spring alternative: damping ratio 0.5–0.7 for playful bounce, 0.8–1.0 for crisp UI.

### Movement (platformer/action)

| Parameter | Typical | Why |
| --- | --- | --- |
| Coyote time | 60–120 ms | Jump just after leaving a ledge still counts |
| Jump buffer | 80–150 ms | Jump pressed just before landing still fires |
| Fall gravity | 1.5–2.5× rise gravity | Removes floatiness |
| Jump cut on release | velocity × 0.4–0.6 | Variable height |
| Time to max run speed | 50–200 ms | Above ~250 ms reads as ice |

### Squash, stretch, particles

- Squash and stretch 10–25% for UI and casual pieces, up to 30–50% for cartoon characters; preserve area (`sx × sy ≈ 1`).
- Particle bursts: 5–15 light, 15–40 medium, 40–150 heavy; lifetimes 200–600 ms for impacts. Set a global live-particle cap per device tier with `gamedev-technical-artist`; overdraw, not count, is the usual mobile cost.

### Haptics and audio sync

- Fire the haptic on the impact frame, within ±1 frame of the visual and the SFX onset. Prepare/warm the haptic engine before the expected event to cut start latency.
- Transient ticks 10–30 ms; avoid continuous vibration over ~300–500 ms on phones.
- Rate-limit: above ~10–12 haptic events per second they blur into a buzz; on cascades, haptic the first and the biggest step only.
- Repeated SFX: randomize pitch ±5–10% and rotate 3–5 variants to avoid machine-gunning. Cascades: raise pitch one semitone per step, cap at 6–8 steps.
- Android audio output latency varies widely by device; use the platform's low-latency path and preloaded samples for impact sounds.

### Match-3 / puzzle feel (heuristic)

Swap 120–200 ms; invalid swap snaps back with a small shake in 150–250 ms; clear 100–200 ms; pieces fall under acceleration (not linear) and land with a 60–100 ms squash; cascade step delay 50–120 ms; leftover moves convert into a celebration at level end, skippable on tap.

### Photosensitivity

No more than three general flashes in any one-second period (WCAG 2.3.1 threshold). Full-screen white flashes on hit are the usual offender; use local flashes or brief tint at under 40% opacity.

## Diagnostics

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| "Laggy" on taps | Animation starts a frame late, render queue depth, input polled in update after logic | Ack on next frame; reduce buffered frames; measure with 240 fps camera |
| "Floaty" jumps | Symmetric gravity, slow acceleration | Fall gravity 1.5–2.5×; faster accel; jump cut |
| Hits feel weightless | No hit-stop, SFX lacks low end, no victim reaction | 60–120 ms hit-stop, victim flash and knockback, low sweetener |
| Everything feels the same | Flat intensity across verbs | Write the escalation ladder; demote frequent verbs |
| Players feel slowed down | Feedback blocks input | Make celebrations parallel or skippable; buffer input |
| Nausea or eye strain reports | Rotational shake, full-screen flashes, constant camera motion | Cap rotation at 1–3°, local flashes, reduce-motion defaults |
| Combat unreadable in big fights | Particle mud over telegraphs | Telegraphs on top layer; cap particles; desaturate hit FX |
| Haptics feel like a buzz | Too many events, too long | Rate-limit; transients only; haptic the peak |
| Feel differs between devices | Frame-based timings, missing low-latency audio | Convert to ms; low-latency audio path; per-tier particle caps |
| Win screen skipped by most players | Celebration too long, not skippable | Shorten to under 2 s before the first tap opportunity |

## Anti-Patterns

**Juice Over Lag** — piling effects on an input path that is 150 ms late. The player feels a louder delay; fix latency first.

**Uniform Loudness** — every action gets the same shake, flash and sound. With no hierarchy, the important moment is invisible.

**The Blocking Celebration** — a high-frequency verb whose feedback locks input. Players feel slowed and start skipping, then quitting.

**Frame-Counted Tuning** — timings specified in frames at 60 fps, then shipped at 30 or 120. Everything is half or double its intended weight.

**Shake Everything** — screen shake on routine actions. It stops carrying meaning and starts causing motion sickness.

**Haptic Spam** — a vibration on every cascade step. The phone buzzes continuously and players turn haptics off, losing the useful ones.

**Particle Mud** — effects layered over the information the next decision needs. Spectacle wins the screenshot and loses the fight.

**Celebration Inflation** — the level-1 win uses the boss-kill fanfare. There is nowhere left to escalate when something big happens.

## Quality Checklist

- [ ] Input-to-photon latency measured on the low-tier device and recorded in the Latency Report
- [ ] Every verb acknowledges input on the next rendered frame
- [ ] Escalation ladder written; frequent verbs sit in tiers 1–2
- [ ] All timings specified in ms, not frames
- [ ] No high-frequency feedback blocks input; celebrations are skippable
- [ ] Inputs are buffered during hit-stop
- [ ] Shake uses trauma decay and smooth noise; rotation capped at 3°
- [ ] Shake slider, reduce-motion support, haptics toggle shipped
- [ ] No more than three full-screen flashes per second
- [ ] Haptics fire within ±1 frame of the visual impact and are rate-limited
- [ ] Repeated SFX have pitch variance and variants
- [ ] Every effect survived an on/off comparison
- [ ] Profiler pass at worst-case effects on the low-tier device stays inside frame budget

## Related Skills

- `gamedev-combat-designer` — frame data, hit windows and TTK; feel tunes how those numbers land, not the numbers.
- `gamedev-technical-artist` — particle, shader and overdraw budgets per device tier.
- `gamedev-audio-designer` — SFX layers, variants, low-latency playback and mix ducking on impacts.
- `gamedev-hud-engineer` — damage numbers, counters and HUD reaction timing.
- `gamedev-accessibility-specialist` — reduce-motion, photosensitivity and haptic alternatives.
- `gamedev-optimization-compatibility` — frame and thermal budgets when effects push the low tier over.
- `gamedev-level-layout-designer` — match-3 cascade feel interacts with board tuning; a fair board that feels flat still churns.
- If installed, `mobile-game-ux-designer` for haptic and touch conventions; `game-playtest-analyst` for on/off preference tests.
