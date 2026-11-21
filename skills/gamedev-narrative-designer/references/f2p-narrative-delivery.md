# F2P and Live Narrative Delivery

Read when designing a story-in-meta layer, an event or season theme, or a gacha/RPG character narrative cadence. Numbers are planning heuristics.

## Story-in-meta model (renovation and decoration puzzle games)

The pattern popularized by Playrix's "-scapes" games (a butler restoring a family estate) and by Dream Games' Royal Match (a king restoring his castle area by area): the player clears puzzle levels, earns a meta currency (stars), and spends it on tasks; each task is both a visible world change and a story beat.

```
level win → star(s) → task in current area → world state change + 0–4 bubbles → next task
                                     └─ area complete → cliffhanger → new area unlocks
```

Design rules:
- **Task = beat.** Every task produces a visible change, even if it has no dialogue. Dialogue is optional seasoning.
- **Choice on cosmetic tasks.** Offering 2–3 style options for a task (pick the fountain style) creates ownership at near-zero narrative cost.
- **Area arc shape:** opening question (task 1) → clue tasks → twist near 70% of the area → resolution near 95% → new question on the last task.
- **Tie story pace to the level curve.** Tasks per area × levels per task = area duration; check that a hard-level spike does not land on the twist (players stuck on a level cannot reach the payoff). Coordinate with `gamedev-level-layout-designer` and `gamedev-meta-progression-designer`.
- **Recurring cast:** a host character (butler, king), a foil, a family/romance thread, a comic relief. New faces arrive through events.
- **Marketing reuse.** Meta characters are the face of UA creatives; keep them visually consistent with ads so the game delivers what the ad promised.

### Area beat sheet

```
Area │ Tasks │ Stars total │ Est. levels │ Est. days (p50) │ Opening question │ Twist task # │ Resolution task # │
Closing hook │ New characters │ World-state set pieces │ Hard levels in range (avoid on twist)
```

## Event and season theming (hand ownership of the calendar to gamedev-liveops-designer)

- **Theme in four places**: board/level art, character costumes or reactions, reward art, music sting. Copy alone is not a theme.
- **One-line event premise**: "The butler's niece is visiting and has lost her cat in the garden." Event mechanics are the verbs; the premise explains why.
- **Season arc** (4–8 weeks typical for battle-pass-style seasons): week 1 opening question, mid-season escalation, final-week resolution, next-season tease in the last 3 days.
- **Pausable arcs**: each season resolves its own question; the overarching mystery advances by one clue. If a season slips, nothing is left hanging.
- **Calendar sync with marketing**: Supercell's Hay Day live-ops roles explicitly align event narratives, timing and messaging with marketing. Treat the narrative calendar as a row in the live-ops calendar, not a separate document.

## Gacha / character-driven live narrative

- **Character story per banner**: every new limited character ships with a personal story quest or scene; it is the emotional sales argument and must be playable by non-owners (preview) without spoiling the main story.
- **Main story per patch**: one chapter or act per major patch; patches every ~6 weeks at HoYoverse scale imply scripts locked well ahead because of multi-language VO (Genshin ships VO in four languages).
- **Lore drip outside the game**: trailers, character teasers and social posts are canon channels; route them through the lore bible.
- **Power vs story**: never make the story progress gated on owning a limited character; it converts story into a paywall and drives backlash.

## Storylets for live cadence

A storylet is a small self-contained narrative unit with prerequisites (state, time, location) and effects (state changes). They suit live games because each one can ship independently.

```
STORYLET:   [id]
REQUIRES:   [flags/variables, e.g. greenhouse_done AND day >= 3]
CONTENT:    [beat summary; line IDs from the script writer]
EFFECTS:    [flags set, items granted, world state changes]
PRIORITY:   [when several are eligible]
EXPIRES:    [never / event end date]
```

Keep storylet state flat (booleans and small counters) so the server can evaluate eligibility and live-ops can author new storylets without client releases.

## Retention reading around narrative beats

- Compare next-day return for players who just saw a cliffhanger beat vs players in the same level range who did not (cohort by area completion date).
- Track skip rate per bubble and dwell time; rewrite the top 10% most-skipped beats each quarter.
- Ask in surveys: "What is happening in the story right now?" Comprehension under ~50% means the critical beats are in the wrong channel.
