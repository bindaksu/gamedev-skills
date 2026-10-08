---
name: gamedev-script-writer
description: >-
  Write the words players read and hear: dialogue, barks, VO and cutscene scripts, tutorial and
  UI copy, and branching conversations in Ink or Yarn, delivered with string IDs, length budgets
  and localization notes. Use when asked to write or punch up dialogue, design a bark system,
  prepare a VO recording script, write tutorial or button copy, convert a scene to Ink or Yarn,
  or fix lines that truncate, repeat, or break in translation.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: design
---

# Script Writer

Game writing is writing for interruption. A line is heard once, mid-combat, by a player who is already reaching for the skip button, and it will be read in a dozen languages by people who never saw the scene. So every line is a production object before it is prose: it has a trigger, a surface, a length budget in characters and seconds, an ID, a speaker, and a localization note. Good game lines are short, voiced to one character, carry one piece of information, and survive translation. Beautiful lines that truncate in German are bugs.

## Role Profile

At top-grossing studios the writer is an implementer, not only an author:

- Scopely's narrative roles state that "all writers on the game implement scripts in-engine, including this role", and expect ownership across writers' room, character arcs, dialogue and quest design (https://hitmarker.net/jobs/scopely-senior-narrative-designer-768551).
- HoYoverse writers "write compelling, genre-appropriate stories using advanced screenplay and interactive storytelling techniques"; IP fluency is expected (https://www.marketingmonk.so/jobboard/jobs/game-writer-at-hoyoverse-e0j9x8).
- King hires UX Writers on Candy Crush — microcopy is its own specialty (https://hitmarker.net/jobs/king-ux-writer-candy-crush-saga-423781). King also cut narrative copywriting roles in 2025 per anonymous reports, with AI tools taking first drafts; the surviving skill is a sharp voice guide and editing, not volume.
- A writing test is a common hiring gate; a shipped title and 3+ years are typical for mid-level.

**Hard skills:** voice and character consistency, brevity, branching structure, timing for VO, localization-aware writing, scripting in the engine or a dialogue tool. **Tools:** Ink, Yarn Spinner, articy:draft or proprietary dialogue editors, spreadsheets for line sheets, the engine, loc management platforms. **KPIs** (inferred): content delivered on cadence, loc-ready on time, string bugs (truncation, missing context) per release, dialogue skip rate. **Collaborators:** narrative and quest designers, localization, audio/VO, UI/UX, marketing (event copy), producers.

## When to Use / Not

**Use** for any player-facing words: dialogue, barks, VO, cutscene scripts, tutorial text, UI labels, event and store copy, item flavor text; and for formatting branching dialogue in Ink or Yarn.

**Not:** premise, world, character arcs and story structure (`gamedev-narrative-designer`); string pipeline, ICU tooling, fonts, LQA (`gamedev-localization-specialist`); VO recording logistics, middleware and audio implementation (`gamedev-audio-designer`); onboarding flow strategy (`gamedev-ux-designer`); subtitle presentation settings (`gamedev-accessibility-specialist`).

## Inputs to Gather

- **Voice guide and character bible.** Missing: write a one-page voice sheet per speaking character first (template below).
- **Surface for every line** — dialogue box, speech bubble, subtitle, bark, toast, button, tooltip, push notification — and its character limit from UI. Missing: use the defaults in Quantitative Reference and flag them.
- **Target languages.** Default: EFIGS + BR-PT + RU + JA + KO + ZH-Hans; this drives expansion budgets.
- **VO scope** — which lines are voiced, in how many languages, budget in lines. Unvoiced is the default for F2P meta dialogue.
- **Dialogue tool and ID scheme** — Ink, Yarn, articy, spreadsheet, proprietary. Default: spreadsheet line sheet with IDs, exportable.
- **Trigger list** for systemic lines (barks, tutorial prompts) — the game events that can fire them, with frequency.

## Method

1. **Budget before you write.** For each line, fix the surface, max characters (English), max seconds (if voiced), and frequency. Writing first and cutting later produces lines that are short but no longer say anything.
2. **Write voice sheets.** Three traits, sentence length, vocabulary in and out, a verbal habit, two sample lines. Every reviewer checks lines against this, not against taste.
3. **Draft in the target format with IDs from line one.** IDs are stable keys for loc, VO and analytics; renumbering later orphans recordings and translations.
4. **One line, one job.** Each line carries one piece of information or one character beat. A line that explains the mechanic, sets up the villain and makes a joke does none of them.
5. **Write barks as systems.** Group by trigger; set priority, cooldowns and variant count from trigger frequency (table below). Write the variants as one pool, read them in sequence, and cut any two that feel alike.
6. **Branch cheaply.** Prefer branch-and-bottleneck: choices change a line or two and a variable, then reconverge within one to three exchanges. Every non-reconverging binary choice doubles every line downstream.
7. **Read aloud and time it.** Voiced lines are timed at the performance pace, not reading pace; a line that runs longer than its animation or its gameplay window gets cut on the floor.
8. **Make it loc-ready.** No concatenation, named placeholders, ICU plurals and gender select, a context note on every line with a pun, a name, a callback or an ambiguous word, and expansion headroom. Read `references/loc-and-vo.md` when preparing strings for translation or a VO session.
9. **Implement and test in context.** Put the lines in the build. Check truncation at the longest target language (pseudo-localize at +40%), overlap with other audio, readability at device size and the skip path.
10. **Measure and revise.** Read skip rate and dwell time per node or bubble; rewrite the nodes players skip most before writing new ones.

## Deliverables

### 1. Dialogue / Line Sheet (one row per line)

```
Line ID │ Scene/Node │ Speaker │ Listener │ Line (EN) │ Surface │ Max chars │ Chars │ Voiced? │ Max sec │
Est. sec (=words/2.5) │ Direction (emotion, volume, pace) │ Trigger/condition │ Variables read/set │
Context note for loc │ Placeholders │ Plural/gender? │ VO file name │ Status (draft/review/locked/recorded)
```

### 2. Bark Matrix

```
Trigger │ Freq (per min/hour) │ Priority (1 critical–4 flavor) │ Can interrupt? │ Per-line cooldown │
Pool cooldown │ Variants (n) │ Speakers │ Max words │ Line IDs
e.g. low_health │ ~1/min │ 2 │ interrupts 3–4 │ 120 s │ 20 s │ 8 │ all squad │ 6 │ BRK_LH_001–008
```

### 3. Branching Dialogue — Ink

```ink
VAR trust = 0

=== gate_guard ===
Halt. Nobody crosses after sundown. #speaker:guard #id:GG_001
* [Show the royal seal]
    ~ trust += 1
    By order of the Queen. #speaker:player #id:GG_002
    -> guard_relents
* [Claim you live here]
    I live on Tanner Street. #speaker:player #id:GG_003
    Funny. I know every face on Tanner Street. #speaker:guard #id:GG_004
    -> guard_relents

=== guard_relents ===
{trust > 0: Fine. Keep your torch low.|Fine. But I'll remember you.} #speaker:guard #id:GG_005
-> END
```

### 4. Branching Dialogue — Yarn Spinner

```yarn
title: GateGuard
---
<<declare $trust = 0>>
Guard: Halt. Nobody crosses after sundown. #line:gg001
-> Show the royal seal. #line:gg002
    <<set $trust to $trust + 1>>
    Player: By order of the Queen. #line:gg003
-> Claim you live here. #line:gg004
    Guard: Funny. I know every face on this street. #line:gg005
<<if $trust > 0>>
    Guard: Fine. Keep your torch low. #line:gg006
<<else>>
    Guard: Fine. But I'll remember you. #line:gg007
<<endif>>
<<jump TannerStreet>>  // next node, defined elsewhere
===
```

Both formats: one line per spoken unit, a stable ID tag on every line, conditional text kept to whole-line alternatives (half-sentence alternatives cannot be translated).

### 5. Character Voice Sheet

```
CHARACTER:     [name]           ROLE: [function in story/meta]
TRAITS:        [3 adjectives]   SENTENCE LENGTH: [short/medium; avg words]
SAYS:          [vocabulary, habits, e.g. food metaphors, never contractions]
NEVER SAYS:    [banned words, registers, slang]
SAMPLE LINES:  1) [...]  2) [...]
LOC NOTE:      [formality level per language: tu/vous, du/Sie; honorifics for JA/KO]
```

### 6. UI Copy Spec

```
String ID │ Screen │ Element (button/title/body/toast/tooltip/push) │ EN text │ Max chars EN │ Max chars (longest lang) │
Tone │ Placeholders │ Context/screenshot link │ Notes
```

## Quantitative Reference

All values are heuristics unless stated; confirm limits against the real UI at the longest language.

### Length budgets by surface (English)

| Surface | Budget |
| --- | --- |
| Bark | ≤ 6–8 words, ≤ 2.5 s; combat callouts ≤ 4 words |
| Dialogue box / bubble (mobile) | ≤ 80–100 chars, ≤ 2–3 lines |
| Dialogue box (PC/console) | ≤ 120–160 chars |
| Subtitle | ≤ 2 lines × 38–42 chars, ≥ 1 s on screen, ≤ ~15–17 chars/s reading speed |
| Tutorial tip | ≤ 15 words, one instruction, verb first |
| Button | ≤ 12–15 chars, verb first ("Collect", not "OK") |
| Toast | ≤ 50–60 chars |
| Push notification | Title ≤ 30–40 chars; body ≤ 90–110 chars visible before truncation |
| Item flavor text | ≤ 1–2 sentences, ≤ 120 chars |
| Story-in-meta beat (renovation/task) | 2–4 bubbles per task, each ≤ 80 chars |

### Speech pace (VO)

| Delivery | Words per minute | Words per second |
| --- | --- | --- |
| Conversational dialogue | 140–160 | ~2.5 |
| Excited / combat | 170–200 | ~3.0 |
| Narration / trailer | 110–140 | ~2.0 |

Estimate seconds as `words ÷ 2.5`, then add 0.3–0.5 s per line for breath and reaction. Dubbed languages typically run 10–25% longer than English; lip-synced or time-locked lines need English drafts 10–15% under the window.

### Bark variant counts by trigger frequency

| Trigger frequency | Variants | Per-line cooldown |
| --- | --- | --- |
| More than 1 per minute | 8–12 | 120–300 s |
| 1–10 per hour | 3–6 | 10–20 min |
| Rare (a few per session) | 1–2 | session |
| Global gap between any two barks | — | 3–8 s |

### Text expansion from English (common heuristic, IBM-style)

| English length | Expansion headroom |
| --- | --- |
| Up to 10 chars | 100–200% |
| 11–20 | 80–100% |
| 21–30 | 60–80% |
| 31–50 | 40–60% |
| 51–70 | 31–40% |
| Over 70 | 30% |

German, Finnish and Russian run long; French, Spanish, Italian and Portuguese typically +15–30%. Chinese, Japanese and Korean use fewer characters but need larger glyphs, so pixel width shrinks less than character count suggests. Arabic and Hebrew need RTL layout, not just translation.

### Branching cost

`lines ≈ Σ over unique paths of lines on that path`. With reconvergence after every choice, cost grows linearly with choices; without it, each binary choice doubles all downstream lines. Budget branches in lines before you write them.

## Diagnostics

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Lines truncate in DE/RU | No max-char column, no pseudo-loc | Add limits; pseudo-localize at +40%; rewrite to budget |
| Translators ask the same questions | Missing context notes and speaker/listener | Add context, listener, gender and screenshot per line |
| Grammar broken in some languages | String concatenation or positional placeholders | ICU message with named placeholders and plural/select |
| "The squad keeps saying the same thing" | Too few variants for trigger frequency, no cooldown | Size the pool by frequency table; add per-line and pool cooldowns |
| VO lines cut off by animation | Lines timed by reading, not speaking | Time at performance pace; cap seconds per line |
| High skip rate on story bubbles | Bubbles over budget, exposition | Cut to one beat per bubble; move lore to optional surfaces |
| Characters sound alike | No voice sheets | Write sheets; read one character's lines in a row |
| Tutorial ignored | Multiple instructions per tip, noun-first copy | One verb-first instruction, shown at the moment of use |

## Anti-Patterns

**The Concatenated Sentence** — `"You have " + n + " lives"`. It breaks plural rules in most languages and word order in the rest.

**The Wall of Text** — five-line bubbles on a phone. Players skip, then skip the next one without reading.

**The Bark Loop** — a high-frequency trigger with three variants and no cooldown. The line becomes a meme for the wrong reason.

**The Untranslatable Pun** — wordplay load-bearing for a quest, with no context note. Every language ships a different, broken joke.

**The Orphan Line** — a line with no speaker, listener or context. The translator guesses gender and formality; the actor guesses emotion.

**Half-Sentence Branching** — conditional fragments spliced into one sentence. Untranslatable and unrecordable.

**Writing for the Page** — VO lines with parentheticals and long clauses. Actors stumble, and the take runs over its window.

**Voice Drift** — a character who sounds different in every writer's scenes. No voice sheet, no reviewer checking against it.

## Worked Example — fixing a meta beat

Original renovation-task bubble (EN, 150 chars, one bubble): "Wow, the fountain looks amazing now that you've repaired it, and I think we should celebrate by inviting Aunt Mabel, who is arriving tomorrow by boat!"

Budget: mobile bubble ≤ 80 chars, one beat per bubble, voice sheet says the speaker is warm and terse. Rewrite as three bubbles, each with its own ID:

```
MT_204_01  Butler:  The fountain works again! Splendid.               (35 chars)
MT_204_02  Butler:  We should celebrate.                                (20 chars)
MT_204_03  Butler:  Aunt Mabel arrives tomorrow. By boat, naturally.   (48 chars)
```

Longest line at +60% headroom (the 31–50 char band) is ~77 chars — fits. Context note on 03: "'naturally' is wry; she is famously dramatic. Formal register for JA/KO." Skip rate on the chapter's bubbles is the follow-up metric.

## Quality Checklist

- [ ] Every line has a stable ID, speaker, listener, surface and max length
- [ ] Voiced lines have estimated seconds and direction; none exceeds its window
- [ ] Voice sheet exists for every speaking character and lines were checked against it
- [ ] Bark pools sized to trigger frequency, with per-line, pool and global cooldowns
- [ ] Branches reconverge within 1–3 exchanges unless budgeted otherwise
- [ ] No string concatenation; placeholders are named; plural and gender use ICU syntax
- [ ] Context notes on every pun, name, callback, or ambiguous word
- [ ] Pseudo-localized at +40% and checked in the build for truncation
- [ ] Tutorial tips are one verb-first instruction each
- [ ] Skip rate or dwell time instrumented for story nodes

## Related Skills

- `gamedev-narrative-designer` — owns premise, arcs and what each scene must accomplish; this skill writes the lines.
- `gamedev-localization-specialist` — string pipeline, ICU tooling, fonts, LQA; hand it the line sheet with context.
- `gamedev-audio-designer` — VO casting, recording, middleware events and ducking.
- `gamedev-campaign-designer` — mission briefings and objective text tied to mission beats.
- `gamedev-liveops-designer` — event copy, season arc text, offer copy cadence.
- `gamedev-ux-designer` and `gamedev-ui-designer` — tutorial flow and the real character limits of each UI element.
- `gamedev-accessibility-specialist` — subtitle presentation, speaker labels, reading speed options.
- `gamedev-analytics-engineer` — dialogue skip and dwell events.
