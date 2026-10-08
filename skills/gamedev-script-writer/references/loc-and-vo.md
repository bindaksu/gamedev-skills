# Loc-Ready Writing and VO Script Prep

Read when preparing strings for translation, writing anything with numbers, names or gendered words, or preparing a VO recording session. Pipeline tooling, fonts and LQA belong to `gamedev-localization-specialist`; recording logistics and middleware to `gamedev-audio-designer`.

## Placeholders and plurals (ICU MessageFormat)

Bad — concatenation, positional, English-only plural:

```
"You have " + lives + " lives left"
"%s defeated %s"
```

Good — one message, named placeholders, plural and select inside the message:

```
lives_left = {count, plural,
  =0 {No lives left}
  one {# life left}
  other {# lives left}}

duel_result = {winner} defeated {loser}.

friend_joined = {gender, select,
  female {{name} joined her team.}
  male {{name} joined his team.}
  other {{name} joined their team.}}
```

Rules:
- Translators receive the whole sentence; never split a sentence across string IDs.
- English needs `one`/`other`; Russian and Polish use `one`/`few`/`many`/`other`; Arabic uses all six categories (`zero`, `one`, `two`, `few`, `many`, `other`). Write the English with `=0` and `other` at minimum so the structure exists.
- Avoid placeholders that change grammatical case of surrounding words (item names inside sentences in Slavic languages). Prefer "Reward: {item}" over "You got {item}!" when the item list is large.
- Never embed text in images or textures; never build words from styled fragments.

## Context note template (attach to every non-obvious string)

```
ID:            [string id]
WHERE:         [screen / scene; screenshot link]
WHO → WHOM:    [speaker → listener; genders; formality]
MEANING:       [plain-English paraphrase of intent]
CONSTRAINTS:   [max chars; voiced? max seconds; must rhyme/alliterate?]
DO NOT TRANSLATE: [brand names, character names if fixed, UI key names]
WORDPLAY:      [explain the joke; permission to replace with a local joke]
```

## Writing habits that translate

- Short, complete sentences; one clause per idea.
- Avoid idioms and sports metaphors unless the context note explains intent and grants freedom.
- Keep terminology consistent: one term per concept across the game (keep a glossary column). "Gems" in the shop and "crystals" in a quest is a bug.
- Avoid "it/this/that" across bubbles; pronoun reference often fails when bubbles are translated separately.
- Do not rely on capitalization or spacing for meaning; CJK has no capitals and no spaces between words.
- Leave numbers, dates and currency to the formatter (locale-aware), never hand-written in the string.

## Pseudo-localization check

Before any translation, run a pseudo-locale that:
- Expands every string by 40% (more for strings under 20 chars).
- Wraps strings in markers to reveal concatenation and hard-coded text, e.g. `[!! Ŝţåŕţ Ĝåɱé !!]`.
- Uses accented and tall glyphs to catch clipped ascenders/descenders.

Every truncated, overlapping or unmarked string found is a bug filed against the line sheet, not the translator.

## VO recording script

Columns for the session script (one row per line, sorted by character then scene so the actor stays in one voice):

```
Line ID │ Character │ Scene │ Line │ Context (what just happened, who is listening) │ Direction (emotion, intensity 1–5, pace) │
Max sec │ Pronunciation (names, invented words, phonetic) │ Takes wanted (e.g. 3; 1 alt read) │ Effort/combat? │ File name │ Selected take
```

Practices (heuristic):
- File naming: `VO_<CHAR>_<SCENE>_<LINEID>_<LANG>.wav` — the line ID makes the file traceable to the sheet.
- Group vocal-strain lines (screams, combat efforts) at the end of a session; they tire the voice.
- Record 2–3 takes per line plus one alternate read for key lines; budget 5–10% pickups after implementation.
- Rough throughput for planning: narrative dialogue 80–150 finished lines per studio hour, barks and efforts faster, emotional scenes slower. Confirm with your recording partner.
- Lock English before booking translated VO; every post-lock English change multiplies across languages.
- Time-locked lines (lip-sync, cutscene) carry max seconds in every language column.

## Line ID conventions

```
<SYSTEM>_<SCOPE>_<NNN>[_<VARIANT>]
DLG_CH03_GATE_014      chapter dialogue
BRK_LOWHP_006          bark pool member
TUT_SWAP_002           tutorial tip
UI_SHOP_BTN_BUY        UI label
EVT_S12_INTRO_003      live event copy (season 12)
```

IDs never change after lock; deleted lines retire their IDs instead of reusing them.
