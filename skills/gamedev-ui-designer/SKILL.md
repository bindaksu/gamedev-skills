---
name: gamedev-ui-designer
description: >-
  Visual UI design for games as a production system: screen layout grids, resolution and aspect-ratio strategy,
  design tokens, component states, 9-slice, iconography, game typography, shop and store screens, and a
  Figma-to-engine handoff spec engineers can build without guessing. Use when the user asks to design or
  restyle a game screen, build a UI kit or token set, lay out a shop or store page, fix UI that breaks on
  tablets, foldables or tall phones, make icons or text read on busy art, or write a handoff for Unity or a
  native UI layer.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: ux-ui
---

# Game UI Designer

Game UI is a production system that happens to be drawn. A mockup that looks right at one resolution, in English, with round numbers, is a sketch; a screen ships when it survives a 1.33 to 2.2 aspect range, a German string 35% longer than the English one, a 9-slice stretched to three sizes, a nine-digit currency balance, and an atlas budget. Every value an engineer has to guess becomes a bug that QA files against your screen. So the core deliverable is not the picture. It is the contract behind it: canvas rules, a token set, component states, slicing, and a handoff spec precise enough that two engineers build the same screen.

**Scope note.** "Layout design" in a studio brief usually means level, map, or board layout, which belongs to `gamedev-level-layout-designer`. This skill owns *screen* layout: grids, anchoring, and composition of UI.

## Role Profile

At Supercell, Scopely, Playrix and similar studios the UI artist or UI designer turns wireframes and feature designs "into visually polished, production-ready UI" (Supercell, Clash Royale), benchmarks mockups and then implements them in Unity (Scopely, Yahtzee), and at principal level sets the UI style for an IP and owns the asset pipeline into the engine.

- **Hard skills:** Photoshop (near-universal), Illustrator, Figma, UI motion in After Effects or Animate, the Unity UGUI pipeline, a casual-style portfolio. Playrix also lists AI tools.
- **Seniority signal:** setting UI style for an IP, owning the art-to-engine pipeline, mentoring.
- **Judged on (inferred):** screen readability and usability, on-time feature and event UI, consistency with the style guide.
- **Collaborators:** UX designer, game designers, UI engineers, LiveOps (event visual identity), marketing.
- Sources: https://hitmarker.net/jobs/supercell-senior-ui-artist-2312825, https://designproject.io/jobs/senior-ui-artist-yahtzee-with-buddies-at-scopely-w1oo96, https://hitmarker.net/jobs/playrix-senior-ui-artist-1617130

## When to Use / Not

Use for: screen composition and grids, canvas and aspect strategy, tokens and UI kits, component state design, icon families, game typography, shop and store visuals, 9-slice and sprite prep, and the handoff spec.

Not for:
- Flows, information architecture, FTUE strategy, heuristic audits: `gamedev-ux-designer`.
- Touch targets, thumb zones, safe-area insets, haptics: if installed, `mobile-game-ux-designer`.
- HUD information hierarchy and UI runtime performance (canvas rebuilds, batching): `gamedev-hud-engineer`.
- What the shop sells, offer value, and price ladder: `gamedev-monetization-designer`; pure math goes to `game-economy-balancer` if installed.
- World art style, palette ramps, and the style bible: if installed, `game-asset-art-director`.
- Board, level, or map layout: `gamedev-level-layout-designer`.

## Inputs to Gather

- **Orientation and platforms.** Portrait, landscape, or both; phone, tablet, foldable, PC. Default: portrait phone plus iPad, no foldable-specific layout.
- **Engine and UI framework.** Unity UGUI, UI Toolkit, Unreal UMG, a custom engine, or native SwiftUI or Compose shells. Default: Unity 6 with UGUI and TextMeshPro.
- **Style bible.** Palette, value structure, and rendering style from art direction. If none exists, write a three-line UI style thesis and get it signed before drawing screens.
- **Language list.** Drives string space, fonts, and RTL mirroring. Default: EFIGS plus PT-BR, JA, KO, ZH-Hans; ask explicitly about Arabic.
- **Memory tier.** The lowest-RAM device you support sets atlas count and size. Default: 3 GB Android.
- **Screen inventory.** Every screen, popup, and state. Count honestly; it is usually 2 to 3 times the first estimate.
- **Shop catalogue.** Offer types and how many SKUs show at once, from monetization.

## Method

1. **Fix the canvas contract before any pixels.** Choose the reference resolution, scale mode, supported aspect range, and safe-area policy. Every later decision depends on it, and changing it after 40 screens means redoing 40 screens.
2. **Build the grid.** Use an 8-unit base with a 4-unit half-step for type and icon padding. Define columns per class: phone portrait 4 columns, tablet 8, landscape 12. Margins sit *inside* the safe area.
3. **Write tokens before components.** Color (semantic, not raw), type scale, spacing, radii, stroke and outline, elevation and shadow, motion durations. A component may reference only tokens, so a reskin or LiveOps event theme becomes a token swap.
4. **Design components with every state.** Normal, pressed, disabled, selected, locked, loading, notification badge, and empty. Missing states are the top source of engineer-invented UI.
5. **Comp each screen at the reference size and at both aspect extremes**, plus the smallest supported phone. Do this side by side in one frame, not in sequence.
6. **Stress-pass every screen.** Use the longest-language string (pseudo-localized at +40%), max values (999,999,999, 99:59:59, a 24-character player name), the empty state, and the error state. Fix layout, not copy.
7. **Plan slicing and atlases.** Mark each asset as 9-slice, 3-slice, tiled, or fixed, and assign it to an atlas. One screen should draw from at most 1 to 2 UI atlases plus font atlases. Why: every extra atlas on screen is another draw call and another texture resident in memory.
8. **Write the handoff spec** (template below) and walk an engineer through it before they build.
9. **Review in engine, on device**, at real size against the comp with a screenshot overlay. Figma at 100% zoom on a 27-inch monitor lies about legibility.

## Deliverables

### 1. Canvas and Resolution Contract

```
CANVAS CONTRACT — <game>
Orientation            portrait | landscape | both (both = two layouts, never one rotated)
Reference resolution   1080 x 1920 px portrait  (1920 x 1080 landscape)
Unit                   1 ref px; 1 pt ≈ 2.77 ref px at a 390 pt-wide phone
Scale mode             Scale With Screen Size; match = adaptive (see code)
Aspect range           h/w 1.33 (iPad) … 2.22 (20:9 Android); foldable inner ≈ 1.0–1.2
Safe area              all interactive + critical-read elements inside SafeArea rect
Bleed layers           backgrounds and frames extend to full screen, never letterbox
Overflow rule          extra space on tall screens goes to: <list region, e.g. scroll list>
                       extra space on wide screens goes to: <side gutters / art>
Min supported          360 x 640 dp Android; 375 x 667 pt iPhone SE
```

### 2. Token Set (DTCG-style JSON, source of truth exported from Figma Variables)

```json
{
  "color": {
    "surface":      { "base": {"$value": "#1B2440"}, "raised": {"$value": "#26335A"} },
    "text":         { "primary": {"$value": "#FFFFFF"}, "muted": {"$value": "#B8C2E0"} },
    "action":       { "primary": {"$value": "#3FC35A"}, "primary-pressed": {"$value": "#2E9A45"} },
    "currency":     { "soft": {"$value": "#FFC93C"}, "hard": {"$value": "#59D4FF"} },
    "rarity":       { "common": {"$value": "#9AA3B5"}, "rare": {"$value": "#3D8BFF"},
                      "epic": {"$value": "#A45CFF"}, "legendary": {"$value": "#FF9A1F"} }
  },
  "space":   { "1": {"$value": 8}, "2": {"$value": 16}, "3": {"$value": 24}, "4": {"$value": 32}, "6": {"$value": 48} },
  "radius":  { "s": {"$value": 12}, "m": {"$value": 20}, "pill": {"$value": 999} },
  "stroke":  { "text-outline": {"$value": 3}, "panel": {"$value": 4} },
  "type":    { "body": {"$value": {"size": 44, "font": "Body-Bold"}},
               "title": {"$value": {"size": 78, "font": "Display"}} },
  "motion":  { "press": {"$value": 70}, "fast": {"$value": 150}, "base": {"$value": 250}, "panel": {"$value": 350} }
}
```

Values are reference px or ms. Rarity is never hue-only: pair each tier with frame shape or gem count. The token-to-engine importer and USS mapping are in `references/tokens-and-handoff.md`; read it when wiring tokens into Unity.

### 3. Component Spec

```
COMPONENT: Button/Primary          tokens only, no raw values
Size        min 160 x 96 ref px (≈ 58 x 35 pt); hit rect +12 ref px each side
States      normal | pressed (scale 0.94, 70 ms, color action.primary-pressed)
            | disabled (40% sat, no shadow, NOT hidden) | loading (spinner replaces label)
            | locked (lock glyph + requirement text) | badge (red dot + count, max "99+")
Label       type.body, 1 line, auto-size floor 80% of base size then ellipsis never; wrap 2 lines
Slicing     9-slice, source 96 x 96, borders L/R/T/B = 40/40/36/44 (shadow sits in bottom border)
Atlas       ui_common
Audio/haptic hooks  ui_tap_primary (audio), light impact (haptic) — names only
```

### 4. Shop Screen Anatomy

```
┌──────────────── header: currencies (soft, hard, +buttons) ──────┐
│ HERO OFFER CARD   1.6–2.0x standard card height, 1 per screen  │
│   art | title | contents list (icons + exact quantities)       │
│   timer (tabular figures) | price button                       │
├────────────── section header ──────────────────────────────────┤
│ [card] [card] [card]   3 columns phone portrait, 4–5 tablet    │
│  icon 128 ref px | quantity | value badge | price button       │
│  price buttons share one baseline across the row               │
├────────────── currency packs: ascending price, left→right ─────┤
└────── bottom nav (tabs) — safe area aware ─────────────────────┘
```

Rules: quantities are explicit numbers, never "a pile"; a value badge shows a number the monetization designer can justify; localized store prices come from the store API and are never baked into art; the price button is the most contrasted element on each card.

### 5. Handoff Spec (per screen)

```
SCREEN: shop_main              Figma frame: <link>   comp sizes: 1080x1920, 1536x2048, 1080x2400
Root anchoring     header: top-stretch inside SafeArea | nav: bottom-stretch inside SafeArea
                   content: stretch between header and nav, vertical scroll
Element table
  id            anchor/pivot      size (ref px)   tokens               slice     atlas      states
  hdr_soft      top-left/0,1      260 x 72        currency.soft        9s 24px   ui_common  n/p
  card_offer    top-stretch/0.5,1 full-48 x 520   surface.raised r.m   9s 40px   ui_shop    n/p/sold-out
  btn_price     bottom-ctr/0.5,0  220 x 88        action.primary       9s        ui_common  all 6
Text           key | style | max chars EN | expansion budget | overflow behavior
  shop_title   | title | 12 | +60% | auto-size to 80% then wrap
Motion         card enter: fade+rise 24 px, 250 ms, ease-out, 40 ms stagger, max 6 staggered
Dynamic data   prices from store API; timer server-authoritative; badge from config
Edge states    empty section hidden; all sold out → "Come back in hh:mm"; offline → cached + banner
Acceptance     overlay diff ≤ 4 ref px at all three comp sizes; zero clipped strings in pseudo-loc
```

### 6. Icon Spec

```
ICON FAMILY: <items>       master 256 x 256, live area 224 (16 px keyline)
Light source top-left 45°; shading steps 3 (shadow, base, highlight) + 1 rim
Outline 8 px at master (= 1.5 px at 48 px display), color = darkest shade of icon hue, not black
Silhouette test: at 32 px, 5/5 reviewers name it in < 2 s
Display sizes: currency 32–40 pt, inventory 64–96 pt, reward popup 120–160 pt
Variants: rarity via frame + background, never by recoloring the object itself
```

## Quantitative Reference

### Aspect and resolution

| Device class | Aspect h:w (portrait) | Logical size | Note |
|---|---|---|---|
| iPad (10th gen) | 1.44 | 820 x 1180 pt | widest phone-UI case short of 4:3 |
| iPad 4:3 classes | 1.33 | 768 x 1024 pt | worst case for width-matched UI |
| 16:9 legacy phone | 1.78 | 375 x 667 pt | iPhone SE |
| iPhone 6.1" | 2.16 | 390 x 844 pt | the common target |
| Android 20:9 | 2.22 | 360 x 800 dp | tallest common case |
| Foldable inner | about 1.0–1.2 | varies | near-square; test or block |

Android 16 (API 36) ignores orientation and aspect locks on sw600dp+ screens for non-games; games are exempt when the manifest declares `android:appCategory="game"` (Unity: App Category player setting). Set it, or the shop must survive arbitrary resizing.

**Adaptive match rule.** Match width when the screen is taller than the reference, and match height when it is wider. A fixed match of 0.5 under-serves both extremes.

```csharp
using UnityEngine; using UnityEngine.UI;
[RequireComponent(typeof(CanvasScaler))]
public sealed class AdaptiveCanvasMatch : MonoBehaviour {
    [SerializeField] Vector2 reference = new(1080f, 1920f);
    void OnEnable() => Apply();
    void OnRectTransformDimensionsChange() => Apply(); // foldables, split screen
    void Apply() {
        var s = GetComponent<CanvasScaler>();
        if (s == null || Screen.width == 0) return;
        float screen = (float)Screen.height / Screen.width, refA = reference.y / reference.x;
        s.matchWidthOrHeight = screen >= refA ? 0f : 1f;
    }
}
```

### Typography (portrait reference 1080 px wide, 1 pt ≈ 2.77 px)

| Role | pt | ref px | Weight and treatment |
|---|---|---|---|
| Caption, legal | 13 | 36 | regular, never on busy art |
| Body | 16 | 44 | bold; game body is usually bold |
| Button | 18 | 50 | bold or display, outline 3 px |
| Title H2 | 22 | 61 | display |
| Title H1 | 28 | 78 | display, outline 4 px plus drop shadow 0,4 px |
| Reward number | 40+ | 111+ | display, tabular figures |

Heuristic scale ratio is 1.2 to 1.25 per step. Floors for readability and contrast are owned by `mobile-game-ux-designer` if installed. Treat those as hard minimums. Text on art needs an outline of 2 to 4 ref px, or a 40 to 60% scrim, not a lighter color. Timers, counters, and prices use **tabular figures**, or the layout jitters every second. Pick a display font for personality and a body font for coverage. The body font must cover every shipped script, or carry a fallback chain designed with `gamedev-localization-specialist`.

**TextMeshPro SDF settings (heuristic defaults).** Use sampling point size 64 to 90, padding about 10% of sampling size (outlines and glows need it), and a 1024 to 2048 atlas for Latin. Use a static atlas for Latin and dynamic atlases for CJK. Outline width over 0.3 in material units starts eating thin glyphs. Bake a heavier outline into a dedicated font material preset instead.

### 9-slice

- Border at least corner radius plus stroke plus outer shadow on that side. Shadows make borders asymmetric; record all four values.
- Flat-color center: shrink the source so the stretch region is 2 to 4 px. Memory drops and the result looks identical.
- Use **3-slice**, not 9-slice, for horizontal gradients. A vertical gradient stretched horizontally is fine. Stretched across its own axis, it smears.
- Patterned centers **tile** rather than stretch. Tile size must divide the minimum panel size, or the seam shows at one edge.
- One source drawn at several corner sizes uses Pixels Per Unit Multiplier (UGUI) or slice scale (UI Toolkit), not separate sprites.
- Never 9-slice an asset with art in the corners that must not scale (rivets, ornaments). Split it into a frame plus decorations.

### Motion tokens (heuristic, hand juice to `gamedev-game-feel-designer`)

| Token | ms | Use |
|---|---|---|
| press | 60–80 | button scale to 0.92–0.95 |
| fast | 120–180 | toggles, tab underline |
| base | 200–300 | popup in, card enter |
| panel | 300–400 | full-screen transitions; exit at 70% of enter time |
| stagger | 30–50 per item | cap at 6 items, then all at once |

## Diagnostics

| Symptom | Likely cause | Fix |
|---|---|---|
| UI huge and clipped on iPad, fine on phones | Fixed width-match at 4:3 | Adaptive match rule; comp at h/w 1.33 |
| Huge empty band on tall phones | No overflow rule | Assign extra height to a scroll region or art |
| Corners blurry or stretched | 9-slice borders smaller than radius plus shadow | Re-measure borders with shadow included |
| Button labels truncated in DE, RU, FR | Width fixed to English | Pseudo-loc +40% pass; auto-size floor plus 2-line wrap |
| Timer text wobbles every second | Proportional digits | Tabular figures or monospaced digit glyphs |
| Icons read as mush at small size | Detail painted at master scale | 32 px silhouette test; simplify interior detail |
| Rarity misread by colorblind players | Hue-only tiers | Add frame shape or gem count per tier |
| Engineers rebuild screens differently | Comp without anchoring or state spec | Handoff element table with anchor, pivot, states |
| Shop screen draw calls spike | Icons spread over many atlases | Shop atlas per screen; 1–2 UI atlases plus fonts |
| Event reskin takes a sprint | Raw hex in components | Move to semantic tokens; theme equals token set |
| Text crisp in Figma, soft on device | Sprite exported at reference size, shown on a larger tablet | Export at largest-device render size; mips off |
| Popups stack three deep | Missing UX flow ownership | Hand to `gamedev-ux-designer` for a popup queue policy |

## Anti-Patterns

**The Single-Device Comp.** Every screen is designed at one phone size, so tablets and 20:9 phones are discovered in QA. Always comp three sizes side by side.

**Raw Hex in Components.** No tokens, so a seasonal reskin or accessibility contrast fix touches 300 sprites instead of 20 tokens.

**The English-Width Button.** A button sized to "Buy" breaks on "Kaufen" and destroys "Приобрести". Budget +40% on short strings.

**Baked-In Text and Prices.** Text or store prices painted into sprites cannot be localized, A/B tested, or legally corrected without a new build.

**Hue-Only Rarity.** Five rarities that differ only by color are unreadable for roughly 8% of male players and in sunlight.

**The State Gap.** A comp shows only the happy state. Engineers invent disabled, loading, sold-out, and empty, and each feature invents them differently.

**Ornament in the Stretch Zone.** Decorative corners inside a 9-slice warp at every size except the one it was drawn for.

**Atlas Scatter.** Each feature ships its own atlas, so a reward popup over the shop over the map draws from six textures.

## Worked Example: Puzzle Game Shop, Portrait

Reference 1080 x 1920 (h/w 1.78). Targets are an iPhone at h/w 2.16, an iPad at 1.33, and a 20:9 Android at 2.22.

**Scale.** On the iPhone the screen is taller than the reference, so match width (0). UI renders at 1080 ref px across, and the extra 2.16 − 1.78 = 0.38 × 1080 ≈ 410 ref px of height goes to the scrolling card list. On the iPad the screen is wider, so match height (1). The canvas is 1920 ref px tall and 1920 / 1.33 ≈ 1444 ref px wide, leaving 364 ref px of extra width. The card grid goes from 3 to 4 columns at about 1380 ref px usable width. The original fixed match of 0.5 made iPad (1536 x 2048 px) cards about 15% oversized (log-mean scale 1.23 vs 1.07) and pushed the price buttons below the fold.

**Price button.** The English label "$4.99" runs 5 characters. The localized store string "4,99 €" runs 6. A JPY price like "¥800" is short, but the ID price "Rp 79.000" runs 9. Budget for 10 characters at button text size: about 10 × 0.55 em × 50 px ≈ 275 ref px plus 2 × 24 padding ≈ 323 ref px. The comp had 220. Widen the button to 320 and drop the card's secondary label to make room. Do not shrink the font below the 80% auto-size floor.

**9-slice.** The card source was 512 x 512 with a 20 px radius, a 4 px stroke, and a 12 px bottom shadow. Borders were set to 24/24/24/36, but the shadow fades over 16 px, so the bottom border must be 20 + 4 + 16 = 40. Shrink the flat center to 4 px, giving a source of 24 + 4 + 24 by 24 + 4 + 40 = 52 x 68. Memory falls from 1 MB to under 15 KB uncompressed for that sprite.

**Atlases.** The shop referenced 4 atlases: common, shop, event, and items. Moving the 22 item icons the shop shows into `ui_shop` and baking the event frame into a token-tinted 9-slice reduced it to 2 atlases plus 1 font atlas.

## Quality Checklist

- [ ] Canvas contract written: reference resolution, match rule, aspect range, overflow rule, minimum device
- [ ] Every screen comped at reference, h/w 1.33, and h/w 2.2, plus the smallest supported phone
- [ ] Components reference tokens only; zero raw hex or px in component specs
- [ ] Every component has normal, pressed, disabled, selected, locked, loading, badge, and empty states
- [ ] Pseudo-loc +40% pass with zero clipped or overlapping strings; RTL mirror reviewed if Arabic or Hebrew ships
- [ ] Max-value pass: 9-digit balances, 24-character names, 99:59:59 timers
- [ ] Timers and counters use tabular figures
- [ ] No text or prices baked into sprites
- [ ] Rarity and state carry a non-hue channel
- [ ] 9-slice borders include shadow; no ornaments in stretch zones; flat centers shrunk
- [ ] Each screen uses 1–2 UI atlases plus fonts; atlas assignment listed in the handoff
- [ ] Handoff element table lists anchor, pivot, size, tokens, slice, atlas, and states for every element
- [ ] Icons pass the 32 px silhouette test
- [ ] In-engine overlay diff within 4 ref px at all comp sizes, reviewed on device
- [ ] Touch-target and safe-area review done against `mobile-game-ux-designer` if installed

## Related Skills

- `gamedev-ux-designer` gives you the flow, screen inventory, and IA. Get it before comping, and send back any popup-stacking or navigation-depth issue.
- `mobile-game-ux-designer` (if installed) owns touch targets, thumb reach, safe areas, and readability floors. Run its audit on every comp.
- `gamedev-hud-engineer` implements the UI. Send it the handoff spec; it owns canvas splitting, rebuild cost, and HUD hierarchy.
- `gamedev-localization-specialist` owns font fallback chains, expansion budgets per language, and RTL rules.
- `gamedev-accessibility-specialist` owns colorblind modes, text scaling, and the subtitle presentation spec.
- `gamedev-monetization-designer` decides shop contents and offer value; this skill makes them legible and honest.
- `game-asset-art-director` (if installed) sets the style bible that UI tokens inherit.
- `gamedev-technical-artist` owns atlas packing, texture compression, and UI shader cost.
- `gamedev-game-feel-designer` owns juice beyond the motion tokens.
- `gamedev-level-layout-designer` owns "layout design" in the level, map, or board sense.
