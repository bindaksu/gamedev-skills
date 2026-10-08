---
name: gamedev-technical-artist
description: >-
  Technical art for games, mobile-first: shader cost and variant control, VFX budgets and overdraw, texture
  compression choice (ASTC block sizes, ETC2 fallback), atlasing and texture arrays, batching and draw-call
  mechanics, LOD and skinning limits, and asset import pipelines with automated validation. Use when the user
  asks why a scene or effect drops frames on mid or low-end phones, to set shader, VFX, or skinning budgets,
  pick texture formats, fix draw calls or batching, cut shader variants or build size, or build import
  presets and CI checks so artists cannot ship broken assets.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: art-audio
---

# Game Technical Artist

The technical artist turns an art direction into something the slowest supported phone renders at a stable frame rate, and makes it impossible for an artist to accidentally break that. Budgets set in a document are wishes; budgets enforced by import presets, shader stripping, and a CI check are facts. The two expensive mistakes on mobile are almost never "too many triangles". They are fill (overdraw, full-screen alpha, heavy fragment shaders on tile-based GPUs) and state (materials, shader variants, and textures that defeat batching). Measure on the low tier, fix by construction, and automate the rule so the fix stays fixed.

## Role Profile

At top studios the technical artist owns shaders, materials, VFX, lighting, and visual systems (King), pipeline and tooling (Supercell Clash of Clans), and DCC plugins for Maya, Blender, and Houdini (Supercell Art Lab). Brawl Stars VFX artists combine stylized 2D VFX with basic tech art; Playrix Gardenscapes' principal VFX role lists "atlases, batching, effects mechanics".

- **Hard skills:** Shader Graph and HLSL, URP, VFX Graph and particle systems, Maya, Blender, Houdini, Python and C# tools, profilers for batching, draw calls, and overdraw. Supercell lists Python and JavaScript for one TA role and C++ preferred with Python or C# for another. Senior is 5+ years.
- **Seniority signals:** defining technical-art standards, owning the art pipeline and tools.
- **Judged on (inferred):** art adherence to frame-time and memory budgets, artist iteration speed and pipeline throughput, the visual quality bar.
- **Collaborators:** art director, rendering and engine engineers, artists, game designers.
- Sources: https://hitmarker.net/jobs/supercell-senior-technical-artist-706543, https://hitmarker.net/jobs/supercell-senior-game-artist-vfx-brawl-stars-851905

## When to Use / Not

Use for: shader authoring rules and cost, variants, VFX budgets, texture formats per class, atlases, batching, skinning and LOD mechanics, lighting setup for mobile, import presets, and asset validation tooling.

Not for:
- Style bible, texel density targets, triangle budgets per class, texture memory ceilings by RAM, and the overdraw target: if installed, `game-asset-art-director`. This skill makes assets *hit* those numbers.
- Device tiers, whole-frame CPU, memory, thermal budgets, and app size: `gamedev-optimization-compatibility`.
- Engine-level rendering code (Metal or Vulkan backends): `gamedev-metal-graphics-engineer`, `gamedev-android-engineer`.
- UI runtime cost (canvas rebuilds): `gamedev-hud-engineer`.
- Feel and timing of effects: `gamedev-game-feel-designer`.

## Inputs to Gather

- **Device tiers** with one named reference device per tier and target fps. Default: low = 3 GB Android with a Mali-G52 or Adreno 610 class GPU at 30 fps; mid = 4–6 GB at 60 fps; high = recent flagship at 60 or 120 fps.
- **Engine, version, pipeline.** Default: Unity 6.3 LTS with URP. The Built-in pipeline is deprecated from Unity 6.5, so all new mobile work goes to URP.
- **Art direction budgets** from the style bible, if one exists.
- **Captures.** A GPU capture of the worst scene on the low tier device (RenderDoc, Xcode Metal debugger, or Android GPU Inspector), plus the engine frame debugger.
- **Asset counts** per class and the planned content cadence (LiveOps adds assets weekly).
- **Distribution:** whether Play Asset Delivery and texture compression format targeting are in use.

## Method

1. **Capture before changing anything.** Take a GPU capture on the low tier device of the worst-case frame: peak VFX, max units, and UI open. Record GPU ms, draw calls, SetPass calls, overdraw, texture memory, and shader variant count.
2. **Split the frame budget by pass** (table below). Every art feature must fit inside its pass's slice, and a new feature takes time from a named pass.
3. **Fix fill first.** Overdraw, full-screen transparents, alpha-tested foliage, and heavy fragment shaders. On tile-based mobile GPUs fragment and bandwidth cost dominates, so fill fixes buy the most milliseconds.
4. **Fix state second.** Collapse materials into shared shaders with atlases or texture arrays so the SRP Batcher and instancing can do their work; strip variants.
5. **Set texture formats per class** in import presets, never per asset. Ship ASTC with an ETC2 fallback through Play's texture compression format targeting where low-end Android matters.
6. **Set skinning and LOD rules per class** (bones per vertex, bone count, LOD count, cull distance), enforced at import.
7. **Write the validators.** An import postprocessor, a shader-variant report, and a scene budget check in CI. A rule that is only in a document gets broken within a sprint.
8. **Give artists a preview of cost.** Overdraw view, a per-material cost label, and a budget readout in the editor. Artists hit budgets they can see.
9. **Re-capture on device and log the delta** against step 1. Keep the capture set as a regression suite for every content drop.

## Deliverables

### 1. Frame Budget by Pass (fill in per tier)

```
TIER: low   device: <name>   target 30 fps = 33.3 ms   work budget 70% = 23 ms GPU
Pass                 GPU ms   Draw calls   SetPass   Notes
Opaque world          8.0       60           15      atlased environment, 1 lit shader
Characters            3.0       20            6      GPU skinning, 2 bones/vertex
Transparent / VFX     4.0       25           10      overdraw avg ≤ 2.5x
Post                  2.0        3            3      bloom half-res, tonemap; no SSAO or DOF
UI                    2.0       15            5      1–2 atlases per screen
Headroom              4.0        —            —      for spikes and thermal drift
```

### 2. Shader Spec

```
SHADER: env_lit_atlas        owner: TA      pipeline: URP 17.x
Purpose      all static environment props
Inputs       albedo atlas (ASTC 6x6, sRGB), ORM atlas (ASTC 6x6, linear), no normal on low tier
Precision    half by default; float only for positions, UV math over large ranges, depth
Samples      ≤ 3 per fragment (low), ≤ 4 (mid and high)
Branches     no per-pixel dynamic branching on low tier; tier switch via keyword
Alpha        opaque only; cutout variant forbidden on low tier (use geometry for holes)
Keywords     shader_feature_local: _NORMALMAP, _EMISSION ; multi_compile only for engine lighting needs
Variants     ≤ 64 after stripping (report attached)
Cost         offline compiler cycles ≤ 1.0x baseline lit shader
SRP Batcher  compatible (all material props in UnityPerMaterial CBUFFER)
```

### 3. VFX Spec

```
EFFECT: vfx_level_complete_burst      tier variants: low / mid / high
System        CPU particles (Particle System); GPU (VFX Graph) only on compute-capable mid and high tiers
Max alive     low 80 / mid 200 / high 400
Emitters      ≤ 4
Screen cover  peak overdraw contribution ≤ 1.0x (measured in overdraw view)
Textures      one 1024 flipbook atlas, ASTC 6x6 (alpha), shared with other UI bursts
Shader        additive, unlit, no soft particles on low (avoids depth texture copy)
Duration      1.2 s; no full-screen quad; light flashes ≤ 3 per second
Fallback      low tier: 40% particle count, no distortion, no trails
```

### 4. Import Preset Matrix

```
Class         Max size  Format (iOS / Android)              sRGB  Mips  Read/Write  Other
UI sprite      2048     ASTC 4x4 / ASTC 4x4 + ETC2 fallback  on    off   off         atlas, no compression on 1-px lines
Albedo world   1024     ASTC 6x6                              on    on    off         aniso 1–2
Normal         1024     ASTC 5x5 or 4x4                       off   on    off         flagged as normal map
ORM / mask      512     ASTC 6x6 or 8x8                       off   on    off
VFX flipbook   1024     ASTC 6x6                              on    on    off         mips on unless pixel art
Background big 2048     ASTC 8x8                              on    on    off         visible blur check at device
Character mesh  —       —                                      —     —     off         2 or 4 bones/vertex per tier
```

The validator that enforces this matrix is in `references/validation-tools.md`. Read it when building the import pipeline.

## Technical Reference

### Fill and overdraw on tile-based GPUs

Mobile GPUs (Apple, Mali, Adreno, PowerVR-derived designs) are tile-based. Opaque geometry benefits from hidden-surface removal or early depth tests, but **alpha-tested (`discard`/`clip`) and alpha-blended surfaces defeat or weaken it**. Rules:
- Prefer opaque geometry with cut-out mesh shapes over alpha-test on low tier. A foliage card with 60% transparent texels pays for the whole quad.
- Trim particle quads to the texture's opaque hull (mesh particles or tight sprite meshes). This cuts covered pixels by 30–50% on typical round sprites (heuristic).
- Never put a full-screen transparent quad in the scene for a color tint; do it in the post pass once.
- Measure overdraw with the engine's overdraw view and confirm in a GPU capture. The target (average and peak) comes from the art director's budget.

### Shader cost rules

| Rule | Why |
|---|---|
| `half` precision by default | Mobile GPUs run half at higher throughput and lower register pressure |
| ≤ 3–4 texture samples per fragment on low and mid | Bandwidth, not ALU, is the usual bottleneck |
| Avoid dependent texture reads in fragment shaders | UV computed per pixel prevents prefetch on some GPUs |
| Move math to the vertex stage where it interpolates linearly | Vertices are far fewer than pixels on most mobile meshes |
| No `discard` on opaque-tier shaders | Breaks hidden-surface removal |
| Keyword tiering, not runtime branches, for quality levels | Uniform branches are cheap, but divergent ones are not; variants are explicit |

Use the GPU vendors' offline compilers (for example Arm's Mali Offline Compiler) to read per-shader cycle estimates. Set ceilings relative to your baseline lit shader rather than absolute cycle counts, since absolute numbers change per GPU: opaque ≤ 1.0x baseline, hero character ≤ 1.5x, full-screen post pass ≤ 0.5x.

**Variants.** Variant count grows multiplicatively: 6 `multi_compile` keywords with 2 states each gives 64 variants per pass, times passes, times platforms. Use `shader_feature_local` for material toggles (only used combinations compile), strip engine keywords you do not use with a build preprocessor, and log variant counts per build. A sudden jump in build time or app size is usually variants. Prewarm the variants a scene needs during loading to avoid first-use hitches.

### Batching mechanics (Unity URP)

| Mechanism | What it saves | Requirements and costs |
|---|---|---|
| SRP Batcher | CPU cost of SetPass and material setup between draws | Same shader variant; properties in the per-material constant buffer. Does not reduce draw call count |
| GPU instancing | Draw calls for many copies of one mesh and material | Same mesh and material; per-instance data via instanced properties |
| Static batching | Draw calls for static, shared-material geometry | Stores a combined copy of meshes, which costs memory |
| Dynamic batching | Draw calls for tiny meshes | Under 300 vertices and 900 vertex attributes; CPU cost often exceeds the saving; usually off |
| Atlases and texture arrays | Material count, so the above can work | Atlases need padding against mip bleeding; arrays need same size and format per slice |

### Texture compression choices

Bit rates and memory math are in the art director's reference (ASTC 4x4 is 8 bpp, 6x6 is 3.56 bpp, 8x8 is 2 bpp; ETC2 RGB 4 bpp and RGBA 8 bpp). Choosing per class:
- **ASTC 4x4** for UI, SDF fonts (or uncompressed single-channel), and normals that band.
- **ASTC 5x5 or 6x6** for world albedo and VFX; 6x6 is the default.
- **ASTC 8x8** for large soft backgrounds and skies; check at device size for blockiness.
- **ETC2** is the baseline every OpenGL ES 3.0 and Vulkan Android device decodes. Ship it as a fallback rather than primary, because ASTC gives better quality per bit.
- Play's texture compression format targeting serves ASTC, ETC2, and others from one AAB per device. Without it, picking ASTC-only means a slow software decode or a failure on devices without ASTC; verify the share of your audience on such devices before dropping ETC2.
- Texture size must be chosen against the block size: ASTC pads to whole blocks, and odd sizes waste memory and can tile-artifact at edges.

### Atlasing

- Pack by **co-occurrence on screen**, not by asset type. Everything on screen together shares an atlas; that is the point.
- Padding: at least 2 px for no-mip UI; for mipped atlases, padding must survive the mip levels you use (each level halves it). Cap the mip count or use texture arrays when bleeding shows.
- **Texture arrays** remove bleeding and allow different materials in one batch when slices share size and format; supported on Metal, Vulkan, and OpenGL ES 3.0.
- Max atlas size 2048 on low tier, 4096 only where memory allows. One 4096² ASTC 6x6 atlas is about 10 MB with mips (4096² × 3.56 / 8 × 1.33).

### Skinning and animation (heuristics per tier; verify on device)

| Class | Bones per skeleton | Bones per vertex | Blend shapes |
|---|---|---|---|
| Hero character (close camera) | 50–80 | 4 (mid and high), 2 (low) | face only, high tier |
| Standard NPC or enemy | 25–45 | 2–4 | none |
| Crowd (over 30 on screen) | 12–20, or vertex animation textures | 1–2 | none |

- Set the engine's skin-weight quality per tier (Unity quality settings expose 1, 2, 4, or unlimited bones per vertex), and author with 4 so the downgrade is a setting, not a re-skin.
- Enable GPU skinning where the target supports it, and profile: on some low-end devices the CPU path is faster.
- Above roughly 50 skinned instances on screen on mobile, bake animations to **vertex animation textures** and render with instancing.
- Cull animation updates for off-screen characters (animator culling mode) and drop update rate for distant ones.

### LOD and lighting on mobile

- LOD tier counts and switch thresholds come from the art director. TA owns the mechanics: per-tier LOD bias, cull distances, and **no dithered cross-fade on low tier** (it is alpha-test in disguise).
- Bake lighting for static scenes (lightmaps plus light probes). Realtime shadows at 1 cascade with short distance on mid tier; blob or baked shadows on low tier.
- URP Forward caps additional lights per object; Forward+ removes the per-object cap but costs a clustering pass. Measure both on the low tier. Verify current limits in your URP version.
- Render scale 0.7–0.85 on low tier with the UI at native resolution is often the single largest GPU saving.

## Diagnostics

| Symptom | Likely cause | Fix |
|---|---|---|
| Frame drops only during big VFX | Overdraw from large transparent quads | Trim quads to hull, cut count on low tier, no full-screen quads |
| Foliage scene slow on low tier only | Alpha-tested cards defeat hidden-surface removal | Geometry cutouts or opaque cards with tighter meshes |
| Many draw calls with few objects | Unique material per prop | Shared shader with atlas or texture array; check SRP Batcher compatibility |
| SetPass calls high, draw calls fine | Too many shader variants or shaders in one frame | Consolidate shaders; strip variants |
| Hitch the first time an effect plays | Shader compiled on first use | Prewarm variants during load |
| Build size jumped 80 MB | Variant explosion or uncompressed textures | Variant report; import preset audit |
| Texture memory 2x budget | Formats on "Automatic", Read/Write on, mips on UI | Enforce presets with the validator |
| Blurry backgrounds on tablets only | 8x8 ASTC or max size too low for large screens | Per-tier size override or 6x6 for those assets |
| Character joints collapse on low tier | Authored for 4 bones, played with 1 | Author for 4, set 2 as floor, test on device |
| Crowds tank CPU | Per-instance skinning and animators | Vertex animation textures with instancing |
| Seams in atlased props at distance | Mip bleeding from insufficient padding | More padding, fewer mips, or texture arrays |
| Effects look different on Android vs iOS | Precision or format differences | Test `half` math ranges; check sRGB flags per platform |

## Anti-Patterns

**Automatic Compression.** Leaving formats on the engine default per asset. Memory explodes two weeks before submission.

**The Alpha-Test Forest.** Every leaf a cutout card on a tile-based GPU. Hidden-surface removal stops working exactly where the scene is densest.

**Keyword Explosion.** Every material toggle as `multi_compile`. Build times, memory, and first-use hitches grow geometrically.

**Smoke Over Everything.** Large soft particles stacked across the screen for atmosphere. It is the costliest pixel in the game, repeated eight times.

**One Material per Prop.** Beautiful, unique, and unbatchable. Atlas or array before authoring, not after.

**The PC Post Stack.** SSAO, depth of field, and screen-space reflections ported unchanged to a phone running at 30 fps.

**Validation by Review.** Budgets enforced by a senior TA looking at assets. It works until the first content crunch, then never again.

**The Hero Shader Everywhere.** The showcase character shader becomes the default for props because it looked good in the pitch.

## Worked Example: Merge Game Celebration Screen

Low tier reference: 3 GB Android, Mali-G52 class GPU, target 30 fps. Celebration screen capture shows 41 ms GPU, 96 draw calls, 44 SetPass calls, overdraw peak 7.2x, and 210 MB textures.

**Fill.** 3 burst emitters spawn 90 large round sprites, each about 10% of screen area, alive simultaneously at peak. That is roughly 9x screen coverage from particles alone. Changes: trim quads to an 8-vertex hull (about 35% fewer covered pixels), drop low-tier count to 36, and replace the full-screen "glow" quad with bloom already in the post pass. Peak overdraw falls to 3.1x and GPU time to 27 ms.

**State.** 14 effect materials use 6 different shaders. Collapse to 2 shaders (additive and alpha-blend unlit) with one 1024 flipbook atlas. SetPass falls from 44 to 17 and draw calls from 96 to 58.

**Memory.** 30 VFX flipbooks at 1024² RGBA32 cost 1024² × 4 bytes × 1.33 ≈ 5.3 MB each, 160 MB total. At ASTC 6x6: 1024² × 3.56 / 8 ≈ 0.45 MB, × 1.33 ≈ 0.59 MB each, about 18 MB total. Texture memory falls from 210 MB to 68 MB.

**Variants.** The particle shader carried 5 `multi_compile` keywords (32 variants per pass across 3 passes). Moving 4 to `shader_feature_local` and stripping unused fog and lightmap variants leaves 12 compiled variants.

**Result.** GPU time is 24.5 ms on the low tier, still over the 23 ms work budget; render scale 0.85 with native-resolution UI brings it to 22.1 ms. An import validator and a CI scene check now fail any new effect over 80 alive particles or with RGBA32 textures.

## Quality Checklist

- [ ] Worst-case frame captured on the low tier reference device; baseline numbers logged
- [ ] Frame budget split by pass per tier, with headroom of at least 15%
- [ ] Average and peak overdraw within the art director's targets; no full-screen transparent quads
- [ ] No alpha-test on low-tier opaque shaders
- [ ] Shaders use `half` by default, ≤ 3–4 samples per fragment on low and mid tiers
- [ ] Shader variant counts reported per build; material toggles use `shader_feature_local`
- [ ] Variants a scene needs are prewarmed during loading
- [ ] All materials in a scene SRP Batcher compatible; shared shaders with atlases or arrays
- [ ] Texture formats set per class by preset; ETC2 fallback decided with audience data
- [ ] Read/Write off, UI mips off, normal maps linear: enforced by the validator
- [ ] Skinning: bones per vertex and skeleton bone counts per class and tier, tested on device
- [ ] VFX each have a low-tier variant with particle cap and no distortion or soft particles
- [ ] Validators run in CI and fail the build on violations
- [ ] Capture set re-run for every content drop and compared to baseline

## Related Skills

- `game-asset-art-director` (if installed) sets texel density, triangle budgets, memory ceilings, LOD tiers, and the overdraw target. This skill makes assets hit them.
- `gamedev-optimization-compatibility` owns device tiers and whole-frame budgets. Get your pass budgets from it.
- `gamedev-unity-engineer` owns URP configuration, Addressables, and build pipeline hooks the validators plug into.
- `gamedev-metal-graphics-engineer` and `gamedev-android-engineer` own backend-level GPU issues found in captures.
- `gamedev-hud-engineer` owns UI batching and canvas cost; share atlas policy.
- `gamedev-game-feel-designer` owns what an effect must communicate; this skill makes it affordable.
- `gamedev-ui-designer` supplies UI atlas groupings per screen.
- `gamedev-accessibility-specialist` sets the flash limits VFX must respect.
- `gamedev-delivery-release` ships texture-format-targeted bundles and asset packs.
