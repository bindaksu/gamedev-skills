---
name: gamedev-localization-specialist
description: >-
  Game localization and culturalization as a pipeline: string keys and metadata, ICU MessageFormat plurals
  and gender, text expansion budgets, pseudo-localization, CJK, Arabic and RTL support, font fallback and
  glyph atlases, LQA, store listing localization, and regional content rules including China licensing at a
  high level. Use when the user asks to add languages, set up a string or TMS pipeline, fix truncated or
  broken translated text, missing glyphs or tofu boxes, support Arabic or Japanese, plan LQA, localize store
  pages, or check what content must change for a market.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: ux-ui
---

# Game Localization Specialist

Localization fails in the source code long before it reaches a translator. Concatenated sentences, plural logic in `if` statements, buttons sized to English, fonts with no Cyrillic, prices baked into art, and strings with no context are developer bugs that no translator can fix. So the job is internationalization first (make the build able to carry any language), then a pipeline (keys, context, freezes, pseudo-loc, LQA), and only then translation. Culturalization sits beside it: some content does not need translating, it needs changing or removing before a market will accept it.

## Role Profile

The research set has no dedicated localization postings at top-grossing studios. The adjacent evidence is narrative: writers are judged partly on being "localization-ready on time" and work from localization docs, and Scopely writers implement scripts in-engine. On the platform side, Apple announced localized language asset packs for iOS 27 at WWDC26 (shipping status unconfirmed in research). The profile below is inferred from that and from standard practice.

- **Responsibilities:** i18n audits; string pipeline and key scheme; TMS and vendor management; glossary, style guides, and translation memory; font and script support; pseudo-localization in CI; LQA planning; culturalization reviews; store listing localization; regional compliance with legal and the publisher.
- **Hard skills:** ICU MessageFormat and CLDR plural rules, Unicode and bidi, font tech (subsetting, SDF atlases, fallback), TMS and CAT tools, scripting (Python) for string tooling, engine text systems.
- **Judged on (inferred):** loc-ready on time for each release, LQA bug escape rate, truncation and missing-glyph defects, revenue share from localized markets.
- **Collaborators:** writers, UI designers, client engineers, audio (VO), QA, marketing (store pages), legal and publishing partners.
- Sources: https://hitmarker.net/jobs/scopely-senior-narrative-designer-768551, https://developer.apple.com/wwdc26/guides/games/

## When to Use / Not

Use for: adding languages, i18n audits, string keys and metadata, ICU messages, fonts and scripts, RTL, pseudo-loc, LQA, culturalization, store listing localization, and high-level regional rules.

Not for:
- Writing source copy and dialogue voice: `gamedev-script-writer`.
- Visual layout of screens once expansion budgets are set: `gamedev-ui-designer`.
- Subtitle presentation (size, background, speaker labels): `gamedev-accessibility-specialist`.
- Loot box and monetization law in depth: `gamedev-monetization-designer`.
- Shipping localized builds, asset packs, and store submission: `gamedev-delivery-release`.

## Inputs to Gather

- **Language list and ship order**, with a reason per language (revenue, UA plan, platform feature). Default tier 1: EN, FR, IT, DE, ES, PT-BR, JA, KO, ZH-Hans; ask about ZH-Hant, RU, TR, AR.
- **String inventory.** Count and word count, by type: UI, narrative, event, store, legal, push.
- **Engine and text stack.** TextMeshPro, UI Toolkit, UMG, custom. Whether a shaping engine (HarfBuzz class) is available.
- **Release cadence.** A weekly LiveOps event means continuous loc, not a final loc pass.
- **Voice-over** languages, if any.
- **Markets with content or licensing rules:** mainland China, Korea, Japan, Germany, the Middle East.
- **Current TMS and vendor**, or none.

## Method

1. **Run an i18n audit on the code, not the strings.** Grep for concatenation, string formatting with positional English grammar, hardcoded text, `ToUpper` and `ToLower` on display text, fixed-width text boxes, and text in textures. Fix these before the first translation order, since each fix later is multiplied by the language count.
2. **Define the key scheme and string metadata.** Stable semantic keys, a context note, a max-length or expansion budget, a screenshot, and a description of every placeholder (template below). Why: translators without context guess, and guesses produce the classic wrong-gender or wrong-meaning bugs.
3. **Move all variable grammar to ICU MessageFormat.** Plurals, gender, and select live in the message, never in code.
4. **Put pseudo-localization in CI.** Every build gets a pseudo locale with accents, +40% padding, and brackets. Truncation and hardcoded strings show up before translators are paid.
5. **Plan fonts per script.** Choose a fallback chain, atlas strategy (static or dynamic), and size budget per script. Generate static atlases from the actual string table character set.
6. **Make RTL a layout mode, not a translation.** Mirror containers, not content. Use bidi isolation for embedded LTR such as player names and numbers.
7. **Set a string freeze for each release**, for example 10 working days before an event for text and 20 for VO, with a hotfix path through remote config for late text.
8. **Brief vendors with a loc kit:** glossary, style guide per language, character bible, screenshots, and a query channel with a 24-hour answer SLA.
9. **Run LQA in context on device**, not in a spreadsheet. Linguistic and functional bugs go into one tracker with the taxonomy below.
10. **Do a culturalization review** per target market before content lock (sheet below), and pull regional rules in early, since a licensing review can take months.
11. **Localize store listings** with market-specific keywords and screenshots showing localized UI. Do not translate English keywords literally.

The i18n grep patterns, pseudo-locale generator, character-set extractor, CI gates, and LiveOps loc calendar are in `references/pipeline-tooling.md`. Read it when setting up the pipeline or CI.

## Deliverables

### 1. String Record

```json
{
  "key": "shop.offer.gems_bonus",
  "source": "{count, plural, one {# gem} other {# gems}} + {bonus}% bonus",
  "context": "Shop card subtitle under the gem pack art. Bonus is a whole number.",
  "placeholders": { "count": "integer 1-99999", "bonus": "integer 5-120" },
  "max_length": { "type": "expansion", "budget_pct": 60 },
  "screenshot": "loc/screens/shop_main_card.png",
  "tags": ["ui", "shop", "liveops-safe"],
  "glossary_terms": ["gem"]
}
```

`glossary_terms` lists glossary-locked terms: translated once per language, then reused verbatim. Never let the brand name of a currency drift between screens.

### 2. ICU Messages (common game cases)

```
lives.left      = {n, plural, =0 {No lives left} one {# life left} other {# lives left}}
team.joined     = {gender, select, female {{name} joined her team} male {{name} joined his team}
                   other {{name} joined their team}}
reward.items    = You got {count, plural, one {# chest} other {# chests}}!
timer.ends      = Ends in {time}            ← time pre-formatted by locale-aware duration formatter
rank.place      = {place, selectordinal, one {#st} two {#nd} few {#rd} other {#th}} place
```

Rules: one complete sentence per key; never build a sentence from fragments; numbers, dates, and durations are formatted by a locale-aware formatter before insertion; prices are always the store's own formatted price string.

### 3. Font Fallback Plan

```
Script        Primary face          Fallback                Atlas      Sampling  Glyphs       Memory
Latin+Cyr     Game-Display          Noto Sans               static 2K  64 px     ~600         4 MB
JA            Game JA face          Noto Sans JP            dynamic 4K 48 px     kana+kanji   16 MB/atlas
ZH-Hans       Game SC face          Noto Sans SC            static 4K  48 px     string set   16 MB/atlas
KO            Game KR face          Noto Sans KR            static 4K  48 px     2,350 + set  16 MB/atlas
AR            Game Arabic face      Noto Sans Arabic        static 2K  64 px     + shaping    4 MB
Chat / names  dynamic, all scripts  Noto fallback chain     dynamic    40 px     on demand    capped
Load rule: only the active language's atlases are resident; chat atlas is capped and evicts
```

### 4. LQA Bug Report

```
ID       LQA-JA-0142            Build 1.42.0 (ja)      Device  Pixel 6a
Key      event.halloween.intro
Type     truncation | overlap | mistranslation | untranslated | placeholder broken |
         missing glyph | wrong plural | wrong gender | inconsistent term | cultural | legal
Sev      S1 blocks progress or legal / S2 wrong meaning / S3 cosmetic / S4 preference
Current  <screenshot + text>    Expected  <text>    Glossary ref  <term>
Fix by   translator | developer (code or layout) | designer (budget)
```

Most S1 and S2 "translation" bugs are developer bugs: broken placeholders, concatenation, and truncation. Route them by the Fix-by field, not to the vendor by default.

### 5. Culturalization Review Sheet

```
Market  Item                                  Issue                              Action        Owner
CN      skeleton enemies (world 3)             skeletons and corpses sensitive     reskin        art
CN/KR   world map in event                    borders and disputed territories     remove map    design
MENA    character outfit, event "Pub Night"   alcohol, revealing clothing          alt variant   art + liveops
DE      symbols in WW2 cosmetic                anti-constitutional symbols         remove        legal
ALL     hand gesture emoji "OK", thumbs up     offensive in some regions           review        UI
JP      gacha "complete the set" mechanic      kompu gacha prohibited              redesign      monetization
```

### 6. Language Tier Plan

```
Tier  Scope                                            Languages
1     UI + narrative + events + store + LQA + VO opt.  EN FR IT DE ES PT-BR JA KO ZH-Hans
2     UI + events + store + LQA spot-check             RU TR PL ZH-Hant
3     store listing + key UI only                      others by UA plan
Rule: never ship a language you cannot keep current with LiveOps cadence; a stale half-English event is worse than no language
```

## Quantitative Reference

### Text expansion from English (heuristics; measure per project)

| Source length | Budget |
|---|---|
| 1–10 characters | +100–200% |
| 11–20 | +80–100% |
| 21–30 | +60–80% |
| 31–50 | +40–60% |
| 51–70 | +30–40% |
| over 70 | +30% |

Per-language averages on running text, also heuristic: DE +20–35%, FR, ES, IT, and PT-BR +15–30%, RU and PL +15–30%, FI up to +40%, AR +20–25%. CJK are shorter in characters (often 30–50% fewer than English) but need larger point sizes for legibility. Budget their height, not width.

### CLDR plural categories (stable reference set)

| Language | Categories used for integers |
|---|---|
| EN, DE, NL, SV, TR | one, other |
| FR, ES, IT, PT | one, other, plus many for large round or compact numbers (1 000 000) in recent CLDR; FR and PT-BR count 0 as one. Verify against the CLDR version your ICU ships |
| RU, UK, PL | one, few, many (plus other for fractions) |
| CS | one, few, other (many for fractions) |
| AR | zero, one, two, few, many, other |
| JA, ZH, KO, TH, ID, VI | other only |

Never encode "1 = singular, else plural" in code. Russian "21 жизнь", "22 жизни", "25 жизней" need three forms; Arabic needs six.

### Glyph and atlas sizing

| Set | Characters |
|---|---|
| Simplified Chinese common set (General Standard level 1) | 3,500 |
| GB2312 hanzi | 6,763 |
| Japanese Jōyō kanji (plus about 180 kana and symbols) | 2,136 |
| Korean KS X 1001 Hangul syllables (all modern syllables: 11,172) | 2,350 |

**SDF atlas math.** A glyph cell is roughly (sampling size + 2 × padding) squared. At 48 px sampling with 5 px padding, about 58² = 3,364 px² per glyph. A 4096² atlas is 16.8 M px², and at about 80% packing that holds about 4,000 glyphs, for 16 MB as Alpha8. A 3,500-character static Simplified Chinese set therefore fits one 4K atlas at 48 px, or a 2K atlas at 24 px sampling (lower quality at large sizes). Build static sets from the string table plus a common-set floor. Use a capped dynamic atlas only for user text such as names and chat.

**Font files.** Full CJK families run roughly 15–20 MB per weight. Subset to the shipped character set plus a common floor (heuristic: 2–5 MB per weight), and deliver non-default languages as downloadable packs where the platform supports it.

### Scripts and bidi

- **Arabic and Persian** need contextual shaping and bidi. Verify that your text stack shapes Arabic. Engines with a HarfBuzz-class shaper do; plain glyph-by-glyph renderers do not. Unity UI Toolkit offers an advanced text generator for complex scripts in Unity 6; verify for your version. TextMeshPro typically needs a shaping plugin.
- **Bidi isolation** for embedded LTR (player names, numbers in RTL sentences): wrap with FSI U+2068 and PDI U+2069. Use LRM U+200E and RLM U+200F only for single-character fixes.
- **Mirror in RTL:** navigation, back arrows, progress bars, list alignment, and tab order. **Do not mirror:** logos, play and media icons, clocks, numbers, checkmarks, or gameplay boards.
- **Thai, Lao, Khmer, Burmese** have no spaces between words. Line breaking needs a dictionary-based breaker.
- **Hindi (Devanagari)** needs shaping for conjuncts.
- **Japanese line breaking (kinsoku):** no small kana or closing brackets at a line start, no opening brackets at a line end.
- **Case mapping is locale-specific.** Turkish dotted and dotless i (i and İ, ı and I) and German ß break when display text is upper-cased with the invariant culture. Uppercase display text in the font or style, or with the target culture. Use the invariant culture only for IDs.

### Store listing limits

| Field | App Store | Google Play |
|---|---|---|
| Name or title | 30 | 30 |
| Subtitle or short description | 30 | 80 |
| Keywords | 100 | none (indexed from text) |
| Promotional text | 170 | — |
| Description | 4,000 | 4,000 |

### Regional rules (high level; verify with the publisher and counsel)

- **Mainland China.** Online games need NPPA approval (the publishing license often called the "ISBN" or banhao), obtained through a licensed domestic publisher; foreign studios partner rather than publish directly. The App Store in China has required this license number for games with paid content or IAP since 2020. Real-name verification and strict playtime limits for minors apply, along with content review (for example skeletons, blood, gambling imagery, maps, historical and political content). There is no Google Play; Android ships through domestic stores. Approval timelines run months.
- **Korea.** GRAC rating; probability disclosure for paid random items is a legal obligation since March 2024.
- **Japan.** "Kompu gacha" (complete-the-set mechanics) has been prohibited since 2012.
- **Germany.** USK rating; anti-constitutional symbols are restricted, with case-by-case assessment for games since 2018.
- **MENA.** Religious symbols, alcohol, gambling imagery, and clothing need review per market.

## Diagnostics

| Symptom | Likely cause | Fix |
|---|---|---|
| Tofu boxes (□) in JA, ZH, KO | Font lacks glyphs; static atlas built from an old string set | Rebuild atlas from current strings; add fallback chain |
| "1 lives", "2 life" | Plural logic in code | ICU plural message |
| Wrong gender or meaning in a translation | No context or screenshot on the key | Context note, screenshot, placeholder description |
| German buttons truncated | English-width UI | Expansion budgets plus pseudo-loc in CI |
| Arabic letters disconnected, reversed | No shaping or bidi in the text stack | Shaping-capable text generator; RTL layout mode |
| Turkish "İ" bugs in titles | Invariant uppercase on display text | Target-culture case mapping or style-based caps |
| Event ships half English | String freeze missed; no continuous loc | Freeze dates per event; remote-config text hotfix |
| Store conversion low in a market | Literal translation of English keywords and screenshots | Market keyword research; localized screenshots |
| Translators asking the same questions | No glossary or character bible | Loc kit with glossary and 24-hour query SLA |
| Memory spike on language switch | All-language atlases resident | Load only the active language; cap the chat atlas |
| CN build rejected | Content or license issue found late | Culturalization review and licensing at concept stage |

## Anti-Patterns

**String Concatenation.** `"You have " + n + " gems"`. Word order, case, and plurals differ across languages; the sentence cannot be translated.

**The Plural If-Else.** `n == 1 ? "life" : "lives"` works for English and German and is wrong for Russian, Polish, Arabic, and French zero.

**Context-Free Keys.** A spreadsheet of 8,000 strings with no screenshots. "Play" is a verb, a noun, or a theatre play; the translator guesses.

**Baked Text in Art.** Logos, banners, and prices painted into textures. Each language needs an art pass, so it never happens.

**The Flag Picker.** Languages chosen by national flag. Spanish is not Spain, Portuguese is not Portugal, and Arabic has no single flag. List language names in their own language.

**Locale Collapse.** Treating pt-PT as pt-BR, es-ES as es-419, or zh-Hant as zh-Hans. Players notice immediately.

**Unreviewed Machine Translation on the Store Page.** The store listing is the first and sometimes only text a player reads.

**Late Culturalization.** A content change for China discovered after art lock costs a reskin; at concept stage it cost a sketch.

## Worked Example: Adding German, Japanese, and Arabic to a Puzzle Game

The game has 4,200 strings (38,000 words), a TextMeshPro UI, and weekly events.

**i18n audit.** It finds 140 concatenations (mostly reward lines), 31 plural `if`s, 9 textures with baked text, and invariant uppercase on all titles. Concatenations become ICU messages; reward lines collapse into 6 ICU keys. Baked banners become text over art.

**Expansion.** Pseudo-loc at +40% truncates 212 strings. 160 are buttons under 10 characters, where the budget is +100–200%. Buttons get auto-size to an 80% floor plus 2-line wrap, and the remaining 52 get rewritten source copy with the writer.

**Japanese fonts.** A string-set scan finds 1,940 unique kanji and kana. A static 4K atlas at 48 px holds about 4,000 glyphs, so one atlas (16 MB) covers the shipped strings. Player names use a capped dynamic 2K atlas that evicts least-recently-used glyphs.

**Arabic.** The text stack does not shape Arabic. Options are a shaping plugin for TextMeshPro or moving menus to a shaping-capable generator; the team picks the plugin for this release. An RTL layout mode mirrors 18 screen containers. The level board, timers, and logo stay unmirrored. Player names are wrapped in FSI and PDI.

**Plurals.** `lives.left` needs one/other in DE, other in JA, and zero/one/two/few/many/other in AR. All live in the ICU message; no code change per language.

**Cadence.** The string freeze is 10 working days before each event. Late text fixes ship through remote config. LQA runs 2 days in context per event per language.

**Store.** The DE listing uses researched keywords such as "Rätsel" and "Denkspiel" instead of translating "puzzle game". JA screenshots show the JA UI.

## Quality Checklist

- [ ] i18n audit done: zero concatenation, zero code plurals, zero baked text, zero invariant case mapping on display text
- [ ] Every key has context, placeholder descriptions, expansion budget, and screenshot
- [ ] Pseudo-locale runs in CI; zero truncation at +40%
- [ ] All variable grammar in ICU MessageFormat; plurals checked against CLDR categories per language
- [ ] Numbers, dates, durations locale-formatted; prices from the store's formatted string
- [ ] Font fallback chain per script; static atlases built from the current string set; tofu check per language
- [ ] RTL mode mirrors containers, not content; bidi isolation around embedded LTR
- [ ] Locales distinguished (pt-BR and pt-PT, es-ES and es-419, zh-Hans and zh-Hant)
- [ ] String freeze dates per release and a remote-config text hotfix path
- [ ] Loc kit: glossary, style guides, character bible, query SLA
- [ ] LQA in context on device, bugs routed by Fix-by owner
- [ ] Culturalization review per market before content lock
- [ ] Store listings localized with market keywords and localized screenshots
- [ ] Regional licensing (China, Korea) started with the publisher at concept stage

## Related Skills

- `gamedev-script-writer` writes loc-ready source copy: no fragments, gender-aware, inside expansion budgets.
- `gamedev-ui-designer` designs screens to the expansion budgets and RTL mode set here.
- `gamedev-accessibility-specialist` owns subtitle presentation; this skill supplies per-language line and cps limits.
- `gamedev-unity-engineer` implements the text stack, shaping, and atlas loading.
- `gamedev-audio-designer` coordinates localized VO and lip-sync timing.
- `gamedev-monetization-designer` owns loot box and gacha regulation by market.
- `gamedev-liveops-designer` aligns event calendars with string freezes.
- `gamedev-delivery-release` ships language asset packs and localized store metadata.
- `gamedev-qa-verifier` runs functional LQA alongside linguistic review.
- `gamedev-producer` holds regional licensing timelines in the risk register.
