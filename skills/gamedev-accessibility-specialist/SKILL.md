---
name: gamedev-accessibility-specialist
description: >-
  Game accessibility across vision, hearing, motor, cognitive, speech, and photosensitivity, mapped to the
  Game Accessibility Guidelines and Xbox Accessibility Guidelines, with subtitle specs and sizes, colorblind
  modes, full input remapping, assist options, screen-reader realities in game engines, and legal scope
  (CVAA, European Accessibility Act). Use when the user asks for an accessibility audit or options menu,
  subtitle or caption specs, colorblind or text-size modes, remapping or one-handed play, VoiceOver or
  TalkBack support in a game, or whether CVAA or the EAA applies to their game.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: ux-ui
---

# Game Accessibility Specialist

Accessibility in games is not a mode; it is the set of assumptions the game stops making about the player's eyes, ears, hands, and attention. The highest-impact features are cheap when designed in and expensive when retrofitted: subtitles that are actually readable, remapping that covers every action, state never coded by hue alone, hold inputs with a toggle alternative, and an options menu reachable before the first barrier. Ship *accessible by default* (a good default subtitle size, colorblind-safe palette, no hold-only inputs), then *configurable beyond* (presets, sliders, assists). Tier the work against the published guidelines so you can say what you support, not what you meant to.

## Role Profile

The research set has no dedicated accessibility postings at top-grossing mobile studios. At those studios the work typically sits with UX design and UX research, with compliance checks through QA. The profile below is inferred from those adjacent roles and from console practice, and should be read as such.

- **Responsibilities:** barrier audits against the Game Accessibility Guidelines (GAG) and the Xbox Accessibility Guidelines (XAG); writing feature specs (subtitles, colorblind, remap, assists, text scaling); legal scope assessment with counsel; recruiting and running tests with disabled players; store accessibility declarations.
- **Hard skills:** guideline fluency (GAG tiers, XAG, WCAG contrast and flash rules), color-vision simulation, platform accessibility APIs (UIAccessibility, Android accessibility framework), research methods borrowed from UX research.
- **Judged on (inferred):** guideline coverage per tier, accessibility bugs escaping to release, option adoption rates, review and support-ticket sentiment on accessibility.
- **Collaborators:** UX and UI design, HUD and client engineers, audio, localization (subtitle pipeline), QA, legal.
- Adjacent-role sources: https://hitmarker.net/jobs/king-senior-ux-researcher-809593, https://hitmarker.net/jobs/king-senior-ux-designer-candy-crush-saga-4512478

## When to Use / Not

Use for: accessibility audits, the options menu, subtitle and caption specs, colorblind modes, remapping and input alternatives, difficulty and assist options, photosensitivity, screen-reader and TTS strategy, CVAA and EAA scoping, and store accessibility labels.

Not for:
- Touch-target sizes, Dynamic Type floors, Reduce Motion handling, one-handed HUD mirroring: if installed, `mobile-game-ux-designer`. Its accessibility section is the mobile floor this skill builds on.
- General flows and usability: `gamedev-ux-designer`.
- Subtitle file pipeline, fonts, and line breaking per language: `gamedev-localization-specialist`.
- Implementing HUD scaling and overlays: `gamedev-hud-engineer`.
- Difficulty curve design itself: `gamedev-campaign-designer` or `gamedev-level-layout-designer`.

## Inputs to Gather

- **Platforms.** Mobile, PC, console. XAG is most relevant where Xbox or PC ships. Default: iOS plus Android.
- **Communication features.** Text chat, voice chat, video. Their presence triggers CVAA analysis in the US.
- **Markets and sales channels.** EU consumers and any web shop or in-game store, for EAA analysis.
- **Input model.** Touch only, controller, keyboard and mouse. Timed or simultaneous inputs, holds, rapid tapping.
- **Content.** Voice-over volume, cinematics, text density, flashing VFX, camera motion, audio-only cues.
- **Engine and version.** Determines what screen-reader route is even possible.
- **Current options menu**, with screenshots.

## Method

1. **Scope the legal and platform surface first.** CVAA (if there is chat), EAA (EU sales channels), platform labels. This decides which items are obligations and which are quality.
2. **Run a barrier audit by category:** vision, hearing, motor, cognitive, speech, and photosensitivity. Play the build muted, in grayscale, one-handed, with a screen reader on, and with the timing windows you would get from a slow reaction. Log each barrier with the moment it blocks progress.
3. **Set tier targets.** All GAG *basic* items, intermediate items chosen by genre, advanced items where the genre depends on them (for example audio description for narrative games). Record the decision per item.
4. **Fix defaults before adding options.** Raise default subtitle size, switch the palette to colorblind-safe pairs, add toggles to every hold. An option that 95% never open does nothing for its default state.
5. **Spec the features** with the templates below: subtitles, colorblind, input, assists, text scaling, screen reader or TTS, flashing.
6. **Move the options in front of the first barrier.** Show subtitles, text size, and audio balance on first launch, before the first voiced or text-heavy moment, and keep them reachable from pause everywhere.
7. **Test with disabled players**, paid, recruited through disability gaming communities, at least once per milestone. Simulations find visual and timing problems. They do not find fatigue, workflow, or assistive-tech conflicts.
8. **Declare and document.** Fill platform accessibility labels honestly, and publish an accessibility page listing supported features. Over-declaring creates support load and legal exposure.

## Deliverables

### 1. Accessibility Feature Matrix

```
Cat.     Feature                         GAG tier   Default        Options                  Status  Owner
VISION   Subtitles readable by default   basic      on, M size     S/M/L/XL, bg 0–100%      done    UI+loc
VISION   No hue-only state               basic      shape+color    3 CVD palettes           wip     art
HEARING  Captions for key SFX            inter.     off            on/off, [sound] tags     todo    audio
HEARING  Separate volume sliders         basic      —              master/music/SFX/voice   done    audio
MOTOR    Full remap incl. menus          basic*     —              2 bindings/action        todo    client
MOTOR    Hold → toggle                   basic      hold           toggle per action        todo    client
COGN.    Objective reminder              basic      on             —                        done    design
PHOTO    Flash test pass                 basic      —              reduce-flash toggle      todo    VFX
* basic for controller and keyboard platforms; touch equivalent is relocatable or resizable controls
```

The full category checklist is in `references/feature-checklist.md`. Read it when running the audit.

### 2. Subtitle Spec

```
SUBTITLES — <game>
Default            ON for first launch prompt; remembers choice
Size presets       S / M (default) / L / XL — table below, per platform class
Font               high-x-height sans, medium or bold weight; no italics except a defined use
Background         box behind text, opacity slider 0–100%, default 60%
Lines              max 2; Latin ≤ 42 chars per line (≤ 38 on phone portrait); CJK ≤ 16 chars per line
Reading speed      ≤ 17 characters per second default; min display 1.0 s, max 7 s per event
Speaker            name label on by default when off-screen or more than one speaker; optional color per speaker
Captions           [sound descriptions] for gameplay-relevant SFX, separate toggle from dialogue
Direction          optional direction indicator for off-screen speakers and threats
Position           bottom, inside safe area, never overlapping critical HUD; HUD moves, subtitles do not
Gameplay sync      subtitles pause with the game; cinematics keep them on the same timing as VO
Localization       per-language line-length and cps limits, from the localization specialist
```

### 3. Colorblind Mode Spec

```
COLORBLIND — palette remap, not a full-screen filter
Semantic tokens remapped per mode: ally, enemy, danger, success, rarity tiers, team colors
Modes: default (already safe pairs) | protan | deutan | tritan | high-contrast
Every state also carries: shape or icon or pattern or position (mode-independent)
Verification: simulate each mode on the 10 worst gameplay frames; no two semantic states may merge
```

### 4. Input and Remap Spec

```
INPUT — <platform>
Remap scope        every gameplay AND menu action; 2 bindings per action; conflicts warned, not blocked
Holds              each hold has a toggle option; mash inputs have a hold alternative
Timing             global timing-window multiplier 1.0 / 1.5 / 2.0, or a no-fail option for QTEs
Simultaneity       no required chord of more than 2 inputs; no required multi-touch above 2 fingers
Sensitivity        camera and cursor sliders, invert X and Y separately, aim assist strength
Touch              relocatable and resizable on-screen controls; tap-to-act alternatives for swipes
Devices            standard-controller path covers Xbox Adaptive Controller and PlayStation Access controller
Save               per-profile; survives reinstall through cloud save where available
```

## Technical and Quantitative Reference

### Subtitle sizes (heuristic defaults; verify against current XAG text guidance)

| Platform class | Viewing distance | S | M (default) | L | XL |
|---|---|---|---|---|---|
| TV, 1080p reference | about 2.5–3 m | 32 px | 46 px | 56 px | 72 px |
| PC monitor, 1080p reference | about 0.6 m | 24 px | 32 px | 40 px | 52 px |
| Phone | about 0.3 m | 15 pt | 18 pt | 22 pt | 28 pt |
| Tablet | about 0.4 m | 17 pt | 20 pt | 24 pt | 30 pt |

Scale the 1080p values linearly with output height (×2 at 2160p). Measure in-engine at the target device, not in an editor window.

**Line-length check on a phone.** At 18 pt with an average Latin advance of about 0.5 em, 42 characters is about 42 × 9 = 378 pt. A 390 pt portrait screen with 16 pt margins leaves 358 pt. So 42 does not fit at M size; cap phone portrait at 38 characters, or reflow to 3 lines only at XL.

### Color vision deficiency prevalence (widely cited population figures)

| Type | Males | Notes |
|---|---|---|
| Deuteranomaly | about 5% | most common; red-green weak |
| Protanomaly, protanopia, deuteranopia | about 1% each | red-green; protan also darkens reds |
| Tritan types | well under 0.1% | blue-yellow |
| Any CVD | about 8% of males, about 0.5% of females | |

Opposed pairs that survive most CVD: blue and orange, blue and red with a value difference, magenta and green with a value difference. Red versus green is the worst default.

**Why palette remap beats full-screen filters.** A daltonization filter shifts the whole image, including art that was already fine. It cannot separate two states that share a hue in the source, and it changes the art direction for everyone in the mode. A semantic-token remap changes only the colors that carry meaning.

### Photosensitivity

- No more than **3 general flashes and no more than 3 red flashes in any 1-second window** over a significant screen area (WCAG 2.3.1 threshold, the common game benchmark).
- Test captured gameplay with a Harding-class flash analyzer or the free PEAT tool, especially VFX-heavy moments, lightning, hit flashes, and UI celebration effects.
- Ship a reduce-flash toggle that caps full-screen flashes and damps strobe VFX, independent of Reduce Motion.

### Screen readers in game engines (the reality)

Engines render to one surface, so VoiceOver and TalkBack see a single opaque view unless you build an accessibility tree. Three routes:

| Route | What it is | Use when |
|---|---|---|
| Engine accessibility tree | Unity exposes screen-reader APIs (an accessibility hierarchy of nodes) on iOS and Android in recent versions; Godot 4.5 added partial AccessKit support | Menus, store, settings. Verify the current engine version's coverage |
| Native overlay UI | Store, settings, and account screens built in SwiftUI, UIKit, Compose, or Views over the game surface | Store and subscription management must be accessible; this is the cheapest reliable route |
| Self-voicing TTS | The game speaks via AVSpeechSynthesizer or Android TextToSpeech | Gameplay narration for blind-accessible genres (word, card, puzzle) |

Rules that stop the routes fighting each other:
- If VoiceOver is running (`UIAccessibility.isVoiceOverRunning`), send announcements through the screen reader instead of self-voicing, or the two talk over each other.
- Mark the gameplay region with the `.allowsDirectInteraction` trait so VoiceOver passes touches through to the game.
- On Android, expose virtual views on the game surface through an `ExploreByTouchHelper` subclass. Prefer live regions over announce-style calls, which Android is phasing out; verify on your target API.
- Minimum bar regardless of genre: **menus, store, purchase confirmation, and subscription cancellation** are operable with a screen reader. Snippets are in `references/feature-checklist.md`.

### Legal scope (not legal advice; confirm with counsel)

- **CVAA (US).** It covers *advanced communications services*: in-game text, voice, and video chat, plus the UI used to reach and operate them. It does not cover gameplay generally. The FCC's waiver for game software expired at the end of 2018. Obligations apply where achievable and include recordkeeping. If the game has chat, document accessibility of chat (for example text-to-speech and speech-to-text for voice chat, navigable chat UI) and its achievability analysis.
- **European Accessibility Act (Directive (EU) 2019/882).** It applies to covered products and services placed on the market from **28 June 2025**. Games are not a listed product or service category. The open question is commerce: covered services include *e-commerce services*, and in-game stores selling to EU consumers, and especially standalone web shops, may fall in that scope. Microenterprises providing services (fewer than 10 staff and no more than EUR 2 million turnover or balance sheet) are exempt. The harmonized technical reference is EN 301 549, which incorporates WCAG for web content. Enforcement is national and still settling. Treat the store and checkout flows as in scope until counsel says otherwise.
- **Store declarations.** Apple's App Store accessibility labels let developers declare supported features (for example VoiceOver, larger text, sufficient contrast, reduced motion, captions). The Microsoft Store has accessibility feature tags. Verify the current declaration requirements in each console or store, and declare only what passes a test.

### Cognitive and hearing defaults

- Objective reminder available at all times; recap screen after 24 hours or more away.
- Tutorials re-openable from settings; plain language aimed at roughly a grade 6 to 8 reading level (heuristic).
- Pause anywhere in single-player content; no unpausable timed reading.
- Volume sliders at minimum for master, music, SFX, voice, and UI; a mono audio toggle; visual twins for audio-only cues.

## Diagnostics

| Symptom | Likely cause | Fix |
|---|---|---|
| "Subtitles too small" reviews | Size picked in the editor, not on a device at viewing distance | Size table above, measured on device; raise the default, not just add L/XL |
| Subtitles unreadable on bright scenes | No background box | Box with opacity slider, default 60% |
| Colorblind mode on, players still confuse teams | Filter-based mode, or hue-only team colors | Semantic token remap plus shape or pattern per team |
| Players with tremors fail QTEs | Mash or short timing windows | Hold alternative plus timing multiplier or auto-complete |
| VoiceOver and game TTS talk over each other | Self-voicing ignores the running screen reader | Route announcements through the screen reader when it is on |
| VoiceOver users cannot play at all | Gameplay surface swallows gestures | `.allowsDirectInteraction` on the game region |
| Players cannot find subtitle options before the intro | Options only reachable after the cinematic | First-launch prompt for subtitles, text size, audio |
| Remap missing for menu navigation | Remap scoped to gameplay only | Remap covers every action, menus included |
| Seizure-risk report after an update | New VFX never flash-tested | Analyzer pass on captured footage in the release checklist |
| Store flagged under accessibility law | Checkout built in the engine with no accessibility tree | Native checkout overlay or engine accessibility tree for store screens |

## Anti-Patterns

**The Fullscreen Filter.** "Colorblind mode" that tints the entire image. It changes the art for everyone in the mode and still cannot separate two states that share a hue.

**Subtitles as Afterthought.** Tiny white text, no background, three lines, 25 characters per second. Technically present, practically unreadable.

**The Locked Door Menu.** Accessibility options exist but only after a voiced intro, an unskippable tutorial, or a login wall.

**Hold-Only Input.** Every charge, sprint, and interaction is a hold, with no toggle. Fatigue is a barrier too.

**Shame Labels.** "Story mode for babies" or a trophy denied for using assists. Naming and penalties drive away the players the option exists for.

**The Screen-Reader Fight.** Self-voicing TTS and VoiceOver both speak, or the game view eats every gesture. Worse than doing nothing.

**Checklist Compliance.** Every GAG item ticked from simulation, with no disabled player ever tested. Workflow and fatigue barriers survive untouched.

**Over-Declaration.** Store labels claim VoiceOver support because one screen works. Support load and legal exposure follow.

## Worked Example: Mobile Action RPG Going to PC

Audit findings on the mobile build: subtitles 14 pt white with no box, 3 lines, about 24 cps; team colors red versus green only; dodge is a hold-and-swipe; the options menu unlocks after the tutorial; a lightning VFX strobes at 6 Hz full-screen.

**Subtitles.** The new default is M = 18 pt on phone with a 60% box. 18 pt cannot fit 42 Latin characters on a 390 pt screen (378 pt needed, 358 pt available), so the phone limit is 38 characters per line and 2 lines max. At 24 cps a 76-character line pair needs 76 / 17 = 4.5 s rather than 3.2 s, so dialogue timing is re-cut with the VO team, and long lines split into two events. On PC the default is 32 px at 1080p, scaling to 64 px at 2160p.

**Color.** Remap team colors to blue versus orange, and add a team-specific outline pattern (solid versus dashed). In simulation, the red versus green pair collapsed under deutan; the new pair stays separated in all three CVD modes.

**Motor.** Dodge gets a single-tap button alternative and a timing multiplier of 1.5 or 2.0 for parry windows. On PC every action, including menus, is remappable with two bindings.

**Order.** A first-launch prompt offers subtitles, text size, and audio balance before the voiced intro.

**Photosensitivity.** Lightning is capped at 3 flashes per second, the full-screen flash is reduced to a 30% luminance change, and the reduce-flash toggle removes it entirely.

**Legal.** The game has text chat and a web shop. The CVAA memo covers chat UI accessibility. The EU web shop is treated as in EAA scope pending counsel and is audited against WCAG 2.1 AA through EN 301 549.

## Quality Checklist

- [ ] Legal and platform scope memo: CVAA (chat present?), EAA (EU commerce channels?), store labels
- [ ] Barrier audit across all six categories with the blocking moment logged
- [ ] Every GAG basic item addressed, with a recorded decision for each intermediate and advanced item
- [ ] Subtitles on at first-launch prompt; default size from the platform table; box with opacity slider
- [ ] Subtitle line length and cps limits checked on the smallest supported device
- [ ] No gameplay state coded by hue alone; palette remap modes verified on worst-case frames
- [ ] Every action remappable, menus included; every hold has a toggle; timing multiplier available
- [ ] Flash analyzer pass on captured footage; reduce-flash toggle present
- [ ] Store, purchase confirmation, settings, and cancellation operable with VoiceOver and TalkBack
- [ ] Self-voicing defers to a running screen reader
- [ ] Options reachable before the first barrier and from pause everywhere
- [ ] At least one test round per milestone with disabled players, findings tracked
- [ ] Store accessibility declarations match tested features only
- [ ] Mobile floors (touch targets, Dynamic Type, Reduce Motion) checked with `mobile-game-ux-designer` if installed

## Related Skills

- `mobile-game-ux-designer` (if installed) owns the mobile floor: target sizes, Dynamic Type, Reduce Motion, one-handed mirror, sound-off play.
- `gamedev-ux-designer` folds accessibility findings into flows and the options IA.
- `gamedev-ui-designer` implements colorblind tokens, text scale, and the subtitle presentation.
- `gamedev-localization-specialist` owns subtitle files, per-language line limits, fonts, and RTL.
- `gamedev-audio-designer` owns volume buses, mono audio, and caption-worthy SFX lists.
- `gamedev-hud-engineer` builds HUD scaling and relocatable controls.
- `gamedev-ios-engineer` and `gamedev-android-engineer` implement screen-reader bridges and native overlays.
- `gamedev-qa-verifier` adds accessibility checks and flash analysis to the regression suite.
- `gamedev-monetization-designer` must keep the store and cancellation accessible.
