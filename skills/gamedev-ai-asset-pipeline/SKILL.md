---
name: gamedev-ai-asset-pipeline
description: >-
  Run generative asset production for games: 2D sprites and UI art, image-to-3D with rigging, retargeting
  and sprite baking, generated motion, SFX, voice and music, and video for trailers, behind a spend wrapper
  with a reserved ledger line, a content-hash cache, per-attempt provenance, a requested-versus-reported
  model check, an owner approval ledger, IP term bans in prompts, licence checks per exact checkpoint and
  store AI disclosure built from the ledger. Use when a team wants to generate game art, 3D models,
  animation, sound, voice or trailer footage with AI models, pick a model or vendor, cap or reconcile
  generation spend, fix halos, perspective drift, welded meshes or mirrored back views, prove where an
  asset came from, or answer Steam, App Store, Google Play or EU AI Act questions about generated content.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.1.0"
  category: art-audio
---

# AI Asset Pipeline

A generated asset is a paid, non-deterministic, legally loaded file. Four things go wrong with it, and none of them is "the model is not good enough". Money leaks when parallel agents each think they are under the cap. Provenance breaks when nobody can say which model, prompt and references made the file that shipped. Semantics slip when a sprite passes every pixel check and is still the wrong thing (a fused prop, a mirrored back view, a trademark in the corner). Rights fail when the plan tier, checkpoint licence or store disclosure was never checked. This seat owns the machinery from brief to shipped file: what gets generated at all, which model, the spend wrapper and ledger, the cache, the manifest, the owner's review ledger, the post-processing rules per modality, and the disclosure answers. Style itself stays with the art director, and engine import budgets stay with the technical artist and audio designer.

## Role Profile

Studios hire this seat as "AI Artist" or "AI Creator". From search-result summaries of 2026 postings (pages not opened; verify before quoting):

- **Playrix, AI Artist:** stylized 2D backgrounds, characters, match-3 and UI elements, mainly with FLUX in ComfyUI or Forge; LoRA or DreamBooth fine-tuning and custom ComfyUI nodes in Python are pluses.
- **Tactile Games, AI Artist:** production pipelines for game art, LiveOps and marketing using ComfyUI, Stable Diffusion, FLUX and video tools such as Runway or Kling.
- **Round8 (Neowiz), AI Creator:** concept art with Stable Diffusion, Midjourney and Photoshop; understanding of AI ethics and copyright preferred.

| Dimension | What it looks like |
|---|---|
| Hard skills | Node-graph pipelines (ComfyUI), vendor APIs and their job models, LoRA training, Python image and audio tooling, headless Blender, retopology and rigging basics, a DAW for audio cleanup |
| Seniority signals [inference] | Owns the spend wrapper and provenance schema; says no to generation where authoring or code is cheaper; can defend every shipped file's rights |
| Judged on [inference] | Cost per accepted asset, owner acceptance rate and rework rounds, share of shipped files that trace to a manifest row (target 100%), zero rights or disclosure incidents |
| Collaborators | Art director, technical artist, audio designer, script writer, producer (budget), legal, release engineering |

Sources: https://playrix.com/job/open/art/ai-artist [posting not re-read; verify] · https://www.mediabistro.com/jobs/3540515642-ai-artist (Tactile Games listing on a job aggregator) [posting not re-read; verify] · https://www.invenglobal.com/articles/21761/round8-studio-launches-major-recruitment-drive-introduces-ai-creator-role [posting not re-read; verify]

## When to Use / Not

Use for: deciding what to generate, choosing models and plans, brief and prompt rules, the spend wrapper and ledger, caching, provenance, owner review, 2D extraction and layering, image-to-3D inputs, rigging and retarget choices, sprite baking, generated motion clean-up, generated SFX, voice and music, trailer footage, licence checks and store AI disclosure.

Not for:
- Visual thesis, style bible, palette and anti-references: if installed, `game-asset-art-director`. This seat turns the bible into prompts and checks.
- Import presets, texture formats, texel density, triangle and skinning budgets, flipbook blending and import validators: `gamedev-technical-artist`.
- Audio formats, memory, loudness and mix: `gamedev-audio-designer`.
- VO scripts and line IDs: `gamedev-script-writer`. Localized VO and LQA: `gamedev-localization-specialist`.
- Content generated at runtime (LLM NPCs, live image or voice generation) and its in-game AI disclosure: `gamedev-llm-features-engineer`.
- Coding-agent lanes, cross-session locks and model routing: `gamedev-agentic-production`.
- Store submission mechanics: `gamedev-delivery-release`. App Review pre-flight: `gamedev-ios-engineer`.
- Engine-side retarget and import specifics: `gamedev-unity-engineer`, `gamedev-godot-engineer`.
- Creative testing of trailers and ads: `gamedev-financial-growth-strategist`.

## Inputs to Gather

- **Asset list** by class (sprite, prop, UI kit, character, creature, animation, SFX, VO line, music cue, trailer shot) with counts and the engine spec for each class from `gamedev-technical-artist`.
- **Style bible and one approved anchor image per class.** No anchor, no batch.
- **Budget:** cap per vendor and per production phase, who may raise it, and whether auto top-up is off. Default: hard cap per phase, renewal only by the owner, auto top-up disabled.
- **Vendors and plan tiers in use.** Output rights follow the plan at generation time.
- **Revenue band, MAU and territories.** Several licences change at $1M revenue, 1M MAU, or exclude regions.
- **Stores and markets:** Steam, App Store, Google Play, EU players.
- **The owner:** one named human who approves art, and the review surface (contact sheets, a local HTML pick page, video for motion).
- **Performers:** union status, written consent on file, child characters in the cast.
- **Machine limits:** GPU for local models, how many agents may call vendors at once.

## Method

1. **Decide what not to generate.** Lettering, logos, flags, insignia, UI glyphs and anything with exact geometry are drawn as vectors or set in-engine. Sparks and hit flashes are code particles. Generate where variation is cheap to judge and expensive to author: backgrounds, props, portraits, concept and part sheets, SFX beds, trailer plates.
2. **Register every model before first use.** One row per exact checkpoint or API ID: modality, plan tier, licence URL and read date, revenue, MAU and territory limits, alpha support, shutdown date. Pin dated IDs, never aliases. A row that fails any licence axis is blocked in the wrapper. Name a fallback provider per class in advance; switching to it changes the cache key and sends the batch back through owner review with the same anchor. Facts and dates live in `references/model-landscape.md`; licence rules in `references/rights-and-disclosure.md`.
3. **Write the brief, then lint it.** Lock one style block per class and attach approved sibling assets as references; prompting each item on its own returns one style per item. Every prompt also carries a fixed hard-rule block (no lettering, no logos, no existing-game or franchise names, no real people, no flags, no watermark), hex palette values, text-contrast zones and a scale reference. A linter bans IP terms and category terms dominated by one brand (naming such a category can pull a publisher's trademark lines into the output). References come only from the project's approved art, never from a competitor or benchmark game. State what must vary: "keep the costume exactly" once made male and female variants identical. Validate each brief item alone, so one bad item is quarantined instead of blocking the batch. Run image agents from a folder outside the game repo, so the repo's agent rules do not leak into image prompts.
4. **Put every paid call behind one spend wrapper.** Caps cover every provider, including image tools built into coding agents on a subscription: log their calls as usage units, or the ledger silently stops covering art when generation moves there. It holds a lock across summing spend (reconciled plus reserved), checking the cap, writing a reserved ledger line and submitting, and reconciles that line from the vendor's receipt at finish. Vendors often charge at submit, so a ledger written at finish lets parallel agents overshoot. One run id per asset, shared by every agent, so two lanes never pay for the same asset. Default to dry-run with a cost quote, require an explicit flag to spend, reject unknown or misplaced flags, and pass prompts by file (a variadic reference flag once swallowed the prompt). Concurrency 1 per vendor by default. Never meter spend by the account balance; auto top-up refilled one mid-run. Notify the owner before any paid run, and an agent never raises a cap itself. Treat an out-of-credits error (HTTP 402) as a cap stop and resume from the ledger, not from memory.
5. **Cache by content hash; never auto-retry an ambiguous call.** The key is sha256 over the canonical model ID, prompt, reference hashes, parameters, variant index and tool version. A hit returns the stored raw file. There is no force flag: a new attempt changes the variant index and is recorded. A timeout or dropped connection is ambiguous paid work: mark it, poll the vendor job id, and reconcile before any resubmit.
6. **Record provenance per attempt and keep raw bytes.** Manifest row per attempt (template below). Where a tool exposes no seed or model ID, record its version and session id. Verify the output file exists and hash it before marking the attempt done; some tools write to their own session folder and the copy can fail silently. Derived files point to the raw hash. Log human edits (repaint, composite, selection) per asset.
7. **Check the model the vendor reports.** Compare the model in the response or job metadata with the one requested. On mismatch, stop, block that model in the register and resolve before the next call. A request for one image tier once came back reporting a cheaper one.
8. **2D: one camera, layers, no invented angles.** Keep lettering out of art: paint out any that appears and use live UI text, or every language needs a repaint. Generate sprites on a flat key colour (magenta is common) and key it out, unless the model has native alpha. Never re-render an approved base to make a variant, because re-renders drift the base pixels; make variants as edits or layers and diff the base region. Generate props as edits of the approved empty backdrop and extract them by diffing, because separately generated props drift in perspective and rotation cannot fix it. Size props from a real-height table and render shadows as a separate layer with one outline rule. Build characters as layered paper-doll parts (body, hair, outfit, hat), never pre-baked combinations, and check every combination that ships for occlusion. Never trust a model for an object's opposite view: it repeats the source view or mirrors asymmetric parts, and pixel checks pass both; bake opposite angles from a 3D model or draw them. Grade every sheet to one master on hue, saturation and value and check the spread numerically. Upscale only with a detail-adding upscaler chosen by decision, never plain resampling.
9. **3D: part sheets in, game mesh out.** Feed image-to-3D the inputs in the image-to-3D table below. Fix the input before paying for a better model tier. Decimate to the class budget before rigging; never rig the dense source. Choose bone naming that matches the engine at rig time, and retarget library clips onto that rig. The engine avatar is built once from a T-pose file imported without animation, never from an animation-only file. Weapons and gear become rigid attachments on sockets, with a procedural fallback when auto-rig fails. Hand the mesh to `gamedev-technical-artist` checks: facing asserted after a matrix rotation, height against the scale table, finger and twist weights.
10. **Sprite baking.** Render sprites from the rigged 3D model headless with a fixed camera rig per direction, fixed lights, shadow on its own pass, and at least one source pixel per device pixel at the largest drawn size. This also solves opposite angles and perspective consistency.
11. **Motion: generated clips are raw takes.** Measure per-frame hand speed, hip height and foot contacts before use; reject preset clips that float, sit or hold one action in a long take. For video-to-pose, resample at the source fps, level the floor and gate contacts on foot height. Drive bespoke moves from 5–10 consistent key poses, not frame-by-frame drawings, whose drift becomes jitter. These rules are medium confidence: confirm on your rig [inference].
12. **Audio, voice and music.** SFX and voice requests go through the same wrapper and cache, with a character or minute cap per phase. Voices are designed from text descriptions, never cloned without written consent; never prompt with a real performer's name. Plan adult voices for child characters (vendors can refuse child descriptions) and never upload a child's photo or voice. Run invented-language lines through speech-to-text in every shipped language to catch real words. Generate music only on a plan and model that license commercial use at generation time, or ship no generated music. State key and tempo in the brief and verify both with an audio analysis tool before review; generated music has come back in the wrong key. Formats and loudness go to `gamedev-audio-designer`.
13. **Video for trailers and flipbooks.** Get a cost quote and a reservation before every video call. Generated footage is for trailers and ads, never store App Previews, which must be screen captures. Realistic people or places need an EU deepfake label. When video becomes VFX flipbooks, review whole loop cycles, reject sources with lens flares or elements leaving frame, and approve brightness in the engine's own blend and colour space with `gamedev-technical-artist`.
14. **Review: owner ledger, then byte gate.** The owner sees contact sheets at most 1200 px wide (video for motion) and records approve, fix or reject with a verbatim note. Approval by an agent counts as unapproved. A rejection stays sticky: a later pixel pass never clears a semantic reject, only a new attempt the owner approves does. After approval, the byte gate checks dimensions, file-size budgets, halos after final compression, sharpness, corners for watermarks, extraction holes and manifest hashes. Two batch gates run beside it: a near-duplicate gate (perceptual hash plus colour and edge style metrics, which also flags style drift) and a symbol audit keyed to each file's hash, because models add religious and cultural symbols nobody asked for (one unrequested symbol in a shipped set can force an audit of a whole library). Vision-model checks are advisory, like agent reviews.
15. **Disclose from the ledger and track unit cost.** Build store AI answers by querying shipped file hashes against the manifest (`references/rights-and-disclosure.md` section 6) and re-run on every content drop [inference: planned in production, not yet shipped]. A human confirms vendor terms rows before any rights answer. Keep provenance metadata that tools embed (some image tools write C2PA data) instead of stripping it. Report cost per accepted asset per class each phase.

## Deliverables

### 1. Asset Brief

```
ASSET: [id]   class: [prop/character/UI/SFX/VO/music/trailer shot]   run id: [asset-id/phase]
Purpose        [what the player reads from it in one glance]
Anchor         [approved anchor image path + sha256]
References     [approved project art only: path + sha256, max N]
Hard rules     no lettering · no logos · no franchise, publisher or artist names · no real people · no flags · no watermark
Palette        [hex list]   contrast zone for text: [region or none]
Scale          [real-height row from the scale table]   camera: [backdrop id or 3D camera rig id]
Must vary      [what changes across variants]   Must hold: [what stays fixed]
Model          [register row id]   variants: [n]   cap for this asset: [credits or currency]
Output spec    [size, alpha, format, layers] from the technical-artist import spec
Owner          [name]   review surface: [contact sheet / pick page / video]
```

### 2. Model Register (one row per exact checkpoint or API ID)

```
ID   Modality  Vendor/host  Exact model ID or weights file   Plan tier  Licence URL (read date)  Commercial  Revenue/MAU limit  Territories  Alpha  Shutdown date  Status
M01  image     [host]       [dated id]                       [tier]     [url] ([yyyy-mm-dd])     yes/no      [limit]            [exclusions] y/n    [date/none]    allowed/blocked
```

### 3. Spend Ledger (append-only JSONL, fsync per line)

```
{"t":"[iso]","event":"reserve","vendor":"[v]","run_id":"[asset/phase]","attempt":3,"cache_key":"[sha256]","quote":[n],"cap":[n],"spent_before":[n],"agent":"[lane]"}
{"t":"[iso]","event":"submitted","run_id":"[..]","attempt":3,"job_id":"[vendor job id]"}
{"t":"[iso]","event":"ambiguous","run_id":"[..]","attempt":3,"job_id":"[..]","reason":"timeout"}
{"t":"[iso]","event":"reconcile","run_id":"[..]","attempt":3,"job_id":"[..]","actual":[n],"receipt":"[vendor receipt ref]"}
```

### 4. Provenance Manifest (one row per attempt)

```
{"run_id":"[..]","attempt":3,"asset_id":"[..]","vendor":"[..]","model_requested":"[id]","model_reported":"[id or none]",
 "tool_version":"[cli or sdk version]","session_id":"[..]","seed":"[value or none]","job_id":"[..]",
 "prompt_sha256":"[..]","prompt_path":"[..]","refs":[{"path":"[..]","sha256":"[..]"}],"params":{"size":"[..]","quality":"[..]"},
 "raw_sha256":"[..]","derived":[{"path":"[..]","sha256":"[..]","steps":"cut, fringe trim, grade"}],
 "human_edits":"[none / repaint / composite / selection notes]","embedded_provenance":"[C2PA present / none]",
 "symbol_audit":"[pass / flagged: note]","cost_actual":[n],"register_row":"M01",
 "review":"[ledger row id]","created":"[iso]"}
```

### 5. Owner Review Ledger

```
Row  Asset   Attempt  Verdict           Owner note (verbatim)                 Pixel gate  Final
R12  [id]    3        reject-semantic   "fog reads as solid blocks"           pass        rejected (sticky)
R13  [id]    4        approve           "yes, ship"                           pass        approved
Rule: Final = approved only when Verdict = approve by the owner AND Pixel gate = pass. Agent verdicts are advisory.
```

The store AI disclosure worksheet is in `references/rights-and-disclosure.md`, section 6.

## Technical Reference

### Spend wrapper sequence

```
lock(vendor)                                   # one lock per vendor, shared by every agent and script
  spent = sum(reconcile.actual) + sum(open reserve.quote)
  if attempt for (run_id, cache_key) exists: unlock; return it      # cache or in-flight
  if any ambiguous line for run_id is unresolved: unlock; poll it   # never resubmit
  if spent + quote > cap: unlock; exit 3 (cap)                       # distinct exit codes
  append reserve; fsync
  job_id = submit()                            # vendor may charge here
  append submitted(job_id); fsync
unlock
poll(job_id): done -> download, hash, check reported model, append reconcile(actual from receipt)
              failed -> append reconcile(actual as charged)
              timeout -> append ambiguous; the next run polls job_id first
```

Hold the lock only across the short submit, not across the poll. Exit codes: 0 done or cache hit, 2 usage error, 3 cap, 4 model mismatch, 5 ambiguous pending, 6 licence blocked, 7 dry-run only. Tested reference code is in `references/spend-wrapper.md`.

### Cache key

`sha256(canonical_json({model_id, tool_version, prompt_text, [ref sha256...], params sorted, variant_index}))`. Canonical JSON means sorted keys, no whitespace, normalized number formatting. The key never includes timestamps or file paths, and a vendor model migration changes the key on purpose.

### Image-to-3D inputs

| Input sheet | Rule | Failure it prevents |
|---|---|---|
| Body | Strict front A-pose, arms clear of the torso, open hands, nothing held, plain background | Held props weld to the hand (a spear became a second fist) and cannot be weighted or split |
| Each weapon, gear piece, moving part | Its own sheet at the same scale reference | Rigid attachments on sockets instead of fused geometry |
| Hair, hats, capes that swap | Separate part sheets; the body sheet shows the bare base [inference] | Hair fused into the mesh survived many re-prompts to remove it |
| Mounted units | Rider and mount as separate inputs | Auto-rig fails on the combined mesh |
| Doors, lids, clustered props | One sheet per separable piece [inference: same class, not retested] | Welded doors and fused clusters |

Cap attempts per asset and prompt variant (3–5 is a sane default [inference]); after the cap, change the input sheet, not the tier.

### 2D extraction from a backdrop edit

1. Approve the empty backdrop; it fixes the camera.
2. For each prop, request an edit of the backdrop that adds only that prop.
3. Diff edit against backdrop to get the mask; clean it, then recover soft alpha at the edge.
4. Reject the attempt if the diff touches pixels outside the prop's region (the model repainted the scene), if the mask has holes, or if a corner holds a watermark.
5. Scale from the real-height table; put the contact shadow on its own layer.

### Alpha, halos and the byte gate

- Prefer models with native transparent output. Otherwise generate on a key colour far from the art's palette and cut.
- Decontaminate edge colour, then fill the RGB of fully transparent pixels with the nearest opaque colour before encoding. Otherwise bilinear filtering and mips pull the key colour back in.
- Lossy formats re-introduce halos (magenta fringes appeared after lossy WebP), so run the halo check on the **final encoded file**, at the sizes and filtering the engine uses.
- **Halo check:** count pixels within 2 px of the alpha edge whose colour is near the key colour. Start by failing above 0.5% of edge pixels within RGB distance 60 of the key [inference: tune per palette].
- **Sharpness:** source pixels ÷ (largest drawn size in points × device scale) must be at least 1.0.
- **Byte gate also checks:** dimensions and file budgets per class, layer count, manifest hash equals file hash, and no vendor endpoints or keys in shipped source. Regenerating rarely fixes an oversized file (redraws fixed under a third in one library); fix size by resampling, palette or encoder settings with `gamedev-technical-artist`.

### Cost per accepted asset (illustrative numbers)

A prop batch: 40 props, 150 attempts at 4 credits = 600 credits, 3 extraction reworks, owner accepts 32. Cost per accepted prop = 600 ÷ 32 ≈ 19 credits, plus review time. If the next batch's accepted rate drops below the last phase's, fix the brief or the inputs before raising the cap.

### References

- `references/model-landscape.md`: read when picking a vendor or model, pricing a batch, filling the Model Register, or when a pinned ID fails. Dated: as of 2026-11; verify.
- `references/rights-and-disclosure.md`: read before buying a plan, before the first generated asset ships, before any store submission or voice work, and when building the disclosure worksheet.
- `references/spend-wrapper.md`: read when implementing or auditing the spend wrapper, cache key, halo check or sharpness check.

## Diagnostics

| Symptom | Likely cause | Fix |
|---|---|---|
| Spend over the cap with every agent reporting under it | Ledger line written at finish; vendor charges at submit | Reserve under the lock before submit; reconcile at finish |
| Balance looks fine but the invoice is high | Auto top-up refilled mid-run; spend metered by balance | Turn auto top-up off; meter from the ledger and receipts |
| Same asset paid for twice | Two lanes used different run ids or retried a timeout | One run id per asset; poll ambiguous jobs instead of resubmitting |
| Verifier "checked" and a paid job ran | Gated tool parsed a flag by position | Dry-run default, real argument parser, refuse unknown or misplaced flags |
| Whole batch blocked by one entry | Brief validated as one file | Validate per item; quarantine the bad one |
| Output missing from the working folder | Tool wrote to its session folder and the copy failed | Verify and hash after each call; recover from the session folder |
| Image reports a different model than requested | Vendor fallback or routing | Stop, block the model in the register, resolve before the next call |
| Output carries a publisher's trademark lines | Prompt named a brand-dominated category | Ban category terms; quarantine outputs; scan for text and logos |
| Materials drift (paper reads as concrete, wrong rim colour) | No anchor, no hex palette, soft material words | Anchor image, hex values and a hard-rule block in every prompt |
| Variants come out identical | "Keep X exactly" over-constrained the edit | State what must vary and what must hold, separately |
| Props look miniature or tilted in the scene | Generated separately; perspective drift | Backdrop-edit extraction with a real-height table |
| Back view is the front again or mirrored | Models cannot invent an opposite angle | Bake from a 3D model or draw it; never accept by pixel checks |
| Hat-and-hair pairs look bald or faces are hidden | Pre-baked or unchecked layer combinations | Paper-doll layers; check every shipped combination for occlusion |
| Sheets differ in hue despite one reference | Per-generation colour drift | Grade to one master; check hue, saturation and value spread numerically |
| Magenta or green fringe on sprites in-game | Key colour bled back after lossy encode or filtering | Decontaminate edges, fill transparent RGB, check halos on the final file |
| Sprite soft on large phones or tablets | Under one source pixel per device pixel, or plain upscale | Regenerate larger or use a detail-adding upscaler by decision |
| Held weapon fused to the hand; fingers will not weight | Held or touching objects in the input concept | A-pose body sheet with nothing held; separate part sheets |
| Auto-rig fails on a character or mounted unit | Painted weapon joined to the body; rider fused to mount | Rigid attachments on sockets; separate inputs; procedural fallback |
| Rigging takes forever or weights are noisy | Rig built on the dense source mesh | Decimate to the class budget first |
| Generated clip floats, slides or jitters | Raw take used as final; drift between drawn frames | Measure hand speed, hip height, contacts; key poses, not frame-by-frame |
| Flipbook from video looks dimmer in game than in preview | Premultiply and colour-space order differ from the preview | Approve in the engine's blend and colour space |
| Voice vendor refuses a character prompt | Child or real-person description | Adult voice for child roles; designed voices; no real names |
| Store disclosure answer contradicts the build | Written from memory | Generate it from shipped hashes against the manifest |
| Ledger shows no art spend while art keeps arriving | Generation moved to a coding agent's built-in image tool | Route that tool through the wrapper; log usage units |
| Batch dies halfway with HTTP 402 | No ledger or cap; credits ran out | Budget the batch up front; treat 402 as a cap stop; resume from the ledger |
| Every item in a set has its own style | Items prompted one by one | Locked style block plus approved sibling assets as references |
| Hundreds of near-identical images | Shared key light or composition in every prompt | Perceptual-hash near-duplicate gate; vary staging deliberately |
| Approved base changes when a variant is made | Re-render drift | Variants as edits or layers; diff the base region |
| Localized build needs art repaints | Text baked into images | Paint lettering out; live UI text |
| Crosses or other symbols appear unprompted | Model priors for the subject | Symbol audit keyed to file hash; owner rules per symbol |
| Image prompts quote repo coding rules | Image agent ran inside the repo | Run it from a folder outside the repo |
| Generated cue clashes with the score | Wrong key or tempo | Specify both; verify with audio analysis before review |
| Retargeted clips sit crouched or offset | Engine avatar built from an animation-only file | Build it once from a T-pose file with an explicit bone map |
| Pinned model ID suddenly errors | Vendor shutdown date passed | Track shutdown dates in the register; switch to the fallback with a new cache key |
| Wide backgrounds come back cropped or small | Tool's maximum output size | Generate halves on one backdrop and stitch [inference: with overlap] |

## Anti-Patterns

**Balance as Meter.** Watching the account balance instead of the ledger. Auto top-up and charge-at-submit make the balance lie at exactly the wrong time.

**Retry on Timeout.** Resubmitting a paid call whose outcome is unknown. You pay twice and get two assets with one manifest row.

**The Force Flag.** A switch that bypasses the cache "just this once". Every regeneration must be a recorded new attempt.

**Pixel-Pass Approval.** Letting a green byte gate clear an owner's semantic rejection. Pixels cannot see a fused prop or a mirrored crest.

**Agent-Approved Art.** Counting an agent's "accepted" as acceptance. Only the owner's ledger row ships an asset.

**The Category Prompt.** Naming a genre that one brand dominates and getting that brand's trade dress back.

**Holding It in the Concept.** Feeding image-to-3D a concept where the character holds a weapon, then paying for a higher tier to fix the weld.

**Turnaround by Prompt.** Asking an image model for the back view and shipping its mirrored front.

**Separate-Shot Props.** Generating each prop in its own image and rotating it to fit the scene.

**Baked Combinatorics.** Pre-rendering every hair-by-outfit pair: 20 × 20 is 400 baked sheets against 40 layers.

**Upscale to Ship.** Bilinear-upscaling an undersized output to hit the size spec.

**The Free-Tier Asset.** Shipping output made on a plan that never granted commercial rights; upgrading later does not cover it.

**Disclosure from Memory.** Filling store AI questions from what the team remembers using.

**One Prompt per Item.** Prompting each card or icon separately and getting a different style per item.

**The Uncounted Tool.** Generating through a coding agent's built-in image tool that the spend ledger does not see.

## Quality Checklist

- [ ] Every model in use has a Model Register row with exact ID, licence URL, read date, limits and shutdown date
- [ ] Blocked checkpoints are refused by the wrapper, not just noted
- [ ] Every brief has an anchor, hex palette, scale reference and the hard-rule block; the linter bans IP, category and real-person terms
- [ ] References come only from approved project art
- [ ] All paid calls go through one wrapper per vendor with a lock, a reserve line before submit and reconcile from receipts
- [ ] Auto top-up is off; spend is metered from the ledger
- [ ] One run id per asset across all agents; dry-run is the default
- [ ] Ambiguous calls are polled and reconciled, never resubmitted
- [ ] Cache keyed by content hash; no force flag exists
- [ ] Manifest row per attempt with requested and reported model, tool version, prompt and reference hashes, raw and derived hashes, human edits
- [ ] Model mismatch stops the run and blocks the model
- [ ] 2D props come from backdrop edits; characters are paper-doll layers; no generated opposite angles
- [ ] Image-to-3D inputs are part sheets with nothing held; meshes decimated before rigging; weapons are rigid attachments
- [ ] Generated motion measured for speed, height and contacts before use
- [ ] Voices are designed or consented; no real names in prompts; no child photos or voices uploaded
- [ ] Music ships only from plans that license commercial use at generation time
- [ ] Generated video is used for trailers and ads only, never App Previews
- [ ] Owner ledger enforced by the gate; semantic rejections are sticky; agent approvals do not count
- [ ] Byte gate runs on final encoded files: halos, sharpness at least 1.0, dimensions, watermark corners, manifest hashes
- [ ] Store AI disclosure generated from shipped hashes and re-run on every content drop; vendor terms rows confirmed by a human
- [ ] Cost per accepted asset reported per class per phase
- [ ] Caps cover every provider, including coding-agent image tools; agents never raise a cap
- [ ] Locked style block and approved sibling references per class; image agents run outside the repo
- [ ] No lettering in art; approved bases never re-rendered for variants
- [ ] Near-duplicate gate and symbol audit run per batch, keyed to file hashes
- [ ] Music key and tempo verified; a fallback provider named per class
- [ ] Vendor keys only in tooling; a test fails on keys or endpoints in shipped source

## Related Skills

- `game-asset-art-director` (if installed) owns the visual thesis, style bible and anti-references this seat encodes into briefs.
- `gamedev-technical-artist` owns import presets, texture formats, texel density, mesh and skinning budgets, flipbook blending and the import validators that run after this seat's byte gate.
- `gamedev-audio-designer` owns audio formats, memory, loudness and the mix that generated SFX and music must fit.
- `gamedev-script-writer` supplies VO lines with IDs; `gamedev-localization-specialist` owns localized VO and LQA.
- `gamedev-llm-features-engineer` owns content generated at runtime and its in-game AI disclosure.
- `gamedev-agentic-production` owns agent lanes, shared locks and owner gates for the agents that call this pipeline.
- `gamedev-unity-engineer` and `gamedev-godot-engineer` own engine-side import and retarget setup.
- `gamedev-delivery-release` submits the build and store metadata; `gamedev-ios-engineer` runs App Review pre-flight.
- `gamedev-producer` sets phase budgets and caps; `gamedev-financial-growth-strategist` tests trailer and ad creatives.
