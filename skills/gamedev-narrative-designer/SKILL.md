---
name: gamedev-narrative-designer
description: >-
  Design how a game tells its story: premise, world, characters, arcs, quest and chapter story
  structure, environmental storytelling, and narrative delivery in free-to-play and live games,
  including story-in-meta layers like renovation puzzle games. Use when asked to build a world
  or character bible, structure a story arc or season narrative, design a story-in-meta beat map,
  pick delivery channels, fix players skipping the story, or align narrative with gameplay.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: design
---

# Narrative Designer

Narrative design is the delivery system for meaning, not the story itself. A story the player does not experience does not exist, and in a free-to-play game most players experience it in 30-second slices, between levels, over months, with the skip button under their thumb. So the job is to decide which story moments carry weight, through which channel, at what cost, and to make the story survive skipping. In live games narrative is retention infrastructure: a curiosity hook that pulls the player into the next session and a theme that makes this week's event feel like news.

## Role Profile

At top-grossing studios narrative is either a dedicated team (story-heavy gacha and RPG) or folded into game and live-ops design (casual):

- Scopely's senior narrative designer owns several of: writers' room, character arcs, worldbuilding, screenplay, dialogue, quest design — and implements scripts in-engine (https://hitmarker.net/jobs/scopely-senior-narrative-designer-768551).
- HoYoverse hires screenwriters with IP familiarity and expects "advanced screenplay and interactive storytelling techniques" (https://www.marketingmonk.so/jobboard/jobs/game-writer-at-hoyoverse-e0j9x8). Genshin ships major content patches roughly every six weeks (fan-sourced figure), so narrative runs on a release train.
- In casual and mid-core, narrative appears as event theming inside senior game-designer roles (Zynga) and as live-ops work that aligns event narratives with marketing (Supercell Hay Day). TapBlaze asks for 3+ years and a shipped title (https://www.builtinla.com/job/narrative-designer/10387540).

**Hard skills:** structure (arcs, quest graphs, storylets), character design for recognizability, environmental storytelling, channel cost estimation, collaboration with level and systems design, narrative implementation in engine or dialogue tools. **Tools:** the engine, articy:draft or proprietary story tools, Ink/Yarn, wikis for the lore bible, spreadsheets for beat maps. **KPIs** (inferred): content cadence, story skip and completion rates, retention around narrative beats, event engagement driven by theming, loc-ready on time. **Collaborators:** script writers, quest and level designers, art and concept art, audio/VO, localization, marketing, live-ops, producers.

## When to Use / Not

**Use** for premise, world, characters, arcs, chapter and quest story structure, delivery-channel choice, environmental storytelling, story-in-meta design, season and event narrative themes.

**Not:** writing the actual lines, barks, VO scripts or UI copy (`gamedev-script-writer`); mission order, difficulty and pacing across a campaign (`gamedev-campaign-designer`); the meta system mechanics (stars, tasks, collections) (`gamedev-meta-progression-designer`); event calendar and event economy (`gamedev-liveops-designer`); cultural review of content per region (`gamedev-localization-specialist`).

## Inputs to Gather

- **Genre and story weight** — story-first (RPG, gacha, adventure), story-supporting (casual meta), or systemic (sandbox, PvP). Default: story-supporting.
- **Session shape** — median session length and sessions per day. Default for casual: 5–8 min, 3–5 sessions/day.
- **Delivery budget** — cutscenes allowed, VO languages, animation and art capacity per month. Default: no VO, 2D character art, speech bubbles.
- **Content cadence** — how often new story ships (weekly levels, monthly areas, 6-week patches).
- **Existing IP and lore** — bible, canon constraints, licensor rules.
- **Audience and regions** — age rating, target markets, culturalization constraints.
- **Core verbs** — what the player actually does; the story must be about the same thing.

## Method

1. **Write the premise in one sentence**: who wants what, what stops them, why now. If it needs two sentences, it is two stories.
2. **Align theme with verbs.** List the core verbs; the story's central conflict must be expressible through them. A renovation game's story is about restoring and belonging; a squad shooter's is about loyalty under pressure. When the verb and theme disagree, the player feels it as fake.
3. **Build the cast small and readable.** Casual: 3–5 recurring characters, each with one dominant trait, a silhouette recognizable at thumbnail size, and a want. Story-heavy: tier the cast (core, recurring, local) and cap how many new named characters each chapter introduces.
4. **Design the arc at three scales.** Season or game arc (months), chapter or area arc (days to weeks), beat (one session). Each scale needs a question opened and later answered; a beat without a question is wallpaper.
5. **Choose structure deliberately.** Linear, branch-and-bottleneck, hub-and-spoke, open quest graph, or storylets (small self-contained units gated by state). Pick by production budget: branching multiplies content; storylets scale with live cadence.
6. **Assign each beat a delivery channel** by weight and skip resilience (table below). Put the critical beat in the most skip-resilient channel; put lore in optional channels.
7. **Make it survive skipping.** The essential "what is happening" must be inferable from the visual state of the world (the room is repaired, the villain's flag is up) without reading a line.
8. **Plan environmental storytelling.** For each space, write "what happened here" in one line, then place 3 clues that tell it without text. Hand the brief to level design and art.
9. **Map story onto the content calendar.** Every narrative beat has a ship date, a production lead time and a dependency (art, VO, loc). Live narratives must be pausable: a season can end on a resolved beat even if the next season slips.
10. **Instrument and read.** Track skip rate per node, cutscene completion, quest completion, and retention around cliffhangers. Rework the beats players skip most before adding new ones.

Read `references/f2p-narrative-delivery.md` when designing a story-in-meta layer, an event or season theme, or a gacha character narrative cadence.

## Deliverables

### 1. Narrative One-Pager

```
TITLE:          [working title]
PREMISE:        [one sentence: who wants what, what stops them, why now]
THEME:          [one word or phrase] — expressed through verbs: [verb list]
TONE:           [3 adjectives; 2 reference works and what to borrow from each]
CORE CAST:      [name — role — dominant trait — want]  (3–5 for casual)
STRUCTURE:      [linear / branch-and-bottleneck / hub / quest graph / storylets]
DELIVERY:       [channels in use, with budget per month]
CADENCE:        [what ships when: area per X days, chapter per patch, event per week]
OPEN QUESTION:  [the question that keeps a player returning; when it is answered]
```

### 2. Character Sheet

```
NAME:            ROLE (function in story and in game):
DOMINANT TRAIT:  WANT:  NEED (what they don't know they need):
SILHOUETTE/COLOR KEY:  [readable at 64 px?]
VOICE:           [hand to gamedev-script-writer's voice sheet]
ARC:             [start state → end state per season]
GAMEPLAY TIE:    [what the player does with/for this character]
NEVER:           [what this character would never do — continuity guard]
```

### 3. Arc / Beat Map (per chapter or area)

```
Beat │ Scale (season/chapter/beat) │ Question opened │ Question answered │ Channel │ Skip-resilient carrier
(visual state change) │ Characters │ Gameplay tie │ Est. player day │ Dependencies (art/VO/loc) │ Ship date
```

### 4. Delivery Channel Plan

```
Channel │ Beats assigned │ Units per month │ Cost per unit (art/anim/VO/loc days) │ Skippable? │ Replayable? │ Owner
```

### 5. Lore Bible Entry

```
ENTRY:        [place/faction/item/event]   CANON STATUS: [locked / provisional]   VERSION: [n]
SUMMARY:      [2–3 sentences]
FIRST SEEN:   [chapter/event, date]       REFERENCED IN: [list]
CONTRADICTIONS RESOLVED: [log]            DO NOT: [things that would break canon]
```

## Quantitative Reference

All values are heuristics for planning; validate against your own skip and retention data.

### Delivery channels: cost and skip resilience

| Channel | Relative cost | Skip resilience | Best for |
| --- | --- | --- | --- |
| World state change (room restored, map changes) | Medium (art) | Very high | Critical "what happened" beats |
| Character reaction animation / emote | Low–medium | High | Emotional beats in casual |
| Speech bubbles (2–4 per beat) | Low | Medium | Character voice, humor |
| In-engine scene with VO | High | Medium | Turning points in story-first games |
| Pre-rendered cinematic | Very high | Low (watched once) | Launch, season openers, marketing reuse |
| Item/collectible text | Very low | Low (optional) | Lore for the 5–15% who read |
| Environmental storytelling (props, layout) | Medium | High | World history, mystery |
| Event theming (art, names, copy) | Medium | High | Live freshness |
| Social/trailer content | High | n/a | Hooks outside the game |

### Pacing targets

| Game type | Beat frequency | Arc length | Notes |
| --- | --- | --- | --- |
| Casual story-in-meta | A story beat every 1–3 sessions | Area/room arc: 10–30 tasks, ~3–10 days | Cliffhanger at each area end |
| Mid-core RPG | Chapter every 1–2 weeks of play | Season arc 4–12 weeks | Boss = narrative climax |
| Gacha live (patch train) | Main story per patch, character story per banner | Patch ~6 weeks (Genshin cadence) | Character story tied to banner |
| Premium narrative | Scene every 5–15 min | Chapter 1–3 h | Branch reconvergence per chapter |

### Story attention (heuristic)

- Assume 40–70% of casual players skip optional dialogue; design the critical beat for the skipper.
- Lore readership in optional text is typically single-digit to low double-digit percent; never put plot-critical information there.
- A cast beyond 5 recurring characters in a casual game reduces character recall sharply; introduce new faces through events, then retire or promote them.
- Lead time for voiced live content in multiple VO languages commonly runs 10–16 weeks from script lock to ship; unvoiced bubble text 3–6 weeks including loc. Confirm with your audio and loc partners.

## Diagnostics

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Skip rate above ~70% on main beats | Bubbles too long, no question opened, wrong channel | Cut to one beat per bubble; move the beat into a visual state change |
| Players can't say what the story is about | No premise question; too many characters | Rewrite the one-sentence premise; cut cast to 3–5 |
| Story feels disconnected from play | Theme not expressed through verbs | Rebuild beats around what the player just did |
| Live season ends on unresolved cliffhanger, next delayed | Arc not pausable | End seasons on a resolved beat with a new open question |
| Continuity complaints from community | No lore bible or canon status | Version the bible; route every new entry through review |
| Event theme ignored | Theme lives only in copy | Put it in the board, characters, music and reward art |
| Loc and VO slip every patch | Script lock too late | Lock scripts at the lead time above; track as dependency |

## Anti-Patterns

**The Lore Dump** — opening with history the player has no reason to care about yet. Ask the question before giving the answer.

**The Cutscene Hostage** — unskippable, unreplayable scenes in a game played in short sessions. Players resent the wait and miss the beat anyway.

**The Wiki Story** — plot-critical information hidden in optional text. The 90% who skip are lost; the community writes the story for you, often wrongly.

**Story Wallpaper** — a meta story whose beats change nothing in the world. Players learn it is decoration and stop looking.

**Ludonarrative Mismatch** — a story about peace in a game about grinding kills, or about urgency in a game that rewards waiting. The verbs win; the story looks fake.

**Too Many Faces** — a new named character every chapter. Nobody remembers who anyone is by chapter five.

**Branch Explosion** — branches that never reconverge, budgeted after writing. Content cost doubles per choice and the live cadence collapses.

**The Orphaned Cliffhanger** — a season that ends mid-question when the next season slips. Players feel abandoned, not intrigued.

## Worked Example — story-in-meta area arc

Home-renovation puzzle game; players earn one star per level and spend stars on tasks. Area: "The Greenhouse", 18 tasks, median ~1.5 levels per task at this point ⇒ ~27 levels ⇒ ~5 days for a p50 player at 6 levels/day.

- **Opening question (task 1):** the greenhouse is locked, and the butler won't say why. Channel: locked door visual plus 2 bubbles.
- **Development (tasks 2–12):** each repair reveals a clue about the former gardener (an engraved trowel, a photo, a planted name). Channel: environmental props appear as tasks complete; one bubble each. Skip-resilient: props stay in the world.
- **Twist (task 13):** the gardener was the butler's sister. Channel: character reaction animation plus 3 bubbles.
- **Resolution (task 17):** the restored greenhouse blooms; the butler plants her favorite flower. Channel: big world state change.
- **New question (task 18):** a letter arrives from the sister — "I'm coming home." Opens the next area.

Measure: skip rate per beat, area completion time p50, D-return after task 18 versus the area before.

## Quality Checklist

- [ ] Premise fits in one sentence and names who, want, obstacle and why now
- [ ] Theme expressible through the core verbs
- [ ] Casual cast is 3–5 recurring characters with distinct silhouettes and dominant traits
- [ ] Every beat opens or answers a question; arcs exist at season, chapter and beat scale
- [ ] Each critical beat has a skip-resilient carrier (world state or animation)
- [ ] No plot-critical information lives only in optional text
- [ ] Environmental storytelling briefs exist for key spaces (one line plus three clues)
- [ ] Lore bible versioned with canon status
- [ ] Every beat has a ship date, lead time and dependencies; seasons end on a resolved beat
- [ ] Skip, completion and around-beat retention instrumented

## Related Skills

- `gamedev-script-writer` — turns beats into lines, barks, VO and copy with IDs and loc notes.
- `gamedev-campaign-designer` — mission order and difficulty; narrative supplies the arc and the climaxes it maps onto.
- `gamedev-meta-progression-designer` — the task/star/area system that story-in-meta rides on.
- `gamedev-liveops-designer` — event and season calendars; narrative supplies themes and season arcs.
- `gamedev-level-layout-designer` — environmental storytelling placement and readable spaces.
- `gamedev-localization-specialist` — culturalization review, names, region rules.
- `gamedev-audio-designer` — VO casting, music themes per character and area.
- If installed, `game-asset-art-director` for character silhouettes and world-state art; `game-playtest-analyst` for skip and comprehension tests.
