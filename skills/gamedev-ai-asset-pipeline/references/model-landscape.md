# Generative Model Landscape for Game Assets (as of 2026-11; verify)

Read this when choosing a vendor or model for an asset class, pricing a batch, filling the Model Register, or when a pinned model ID starts failing. Every row here is a dated fact: re-check the source URL before you buy a plan or start a batch.

Tags: **[O]** official page read on 2026-11-21 · **[S]** secondary source (press, reseller, law firm) · **[U]** unverified · **[inference]** a reading of the facts, not a quote. Prices are list API prices in USD unless noted.

Research caveats: the research pass that produced these tables had no final review (the reviewer was rate-limited). Midjourney's docs and OpenAI's Images 2.6 announcement would not load, so those rows rest on secondary sources. The Udio status, the Kling 4.0 API, Rodin per-generation cost and Tripo USD-per-credit figures are also secondary or unverified.

## 1. Image

| Vendor | IDs (as of 2026-11; verify) | Alpha | Strengths for game art | Commercial terms | Price per image |
|---|---|---|---|---|---|
| OpenAI | `gpt-image-2.6-sunburst` (detail, precise edits), `gpt-image-2.6-flare` (fast); Images 2.6 launched 2026-11-04 [S]. `gpt-image-2.5-*` and `gpt-image-2` still listed [O] | `background: "transparent"` with png or webp [O]; host-dependent for `gpt-image-2` (see conflicts) | Several reference images; mask edits (the mask guides, it is not exact); markup edits; SVG and animated-GIF output; `complexity` and quality levels [O] | User owns output per ToS [U] (terms page not read) | $30/M image-output tokens, Batch $15/M [O]; docs calculator about $0.025 at 823 tokens [O]. `gpt-image-2` at 1024²: about $0.006 / $0.053 / $0.211 low / med / high [S] |
| Google | `gemini-nano-banana-2.1` (2026-10-06, recommended), `gemini-3.1-flash-image` (Nano Banana 2), `gemini-3.1-flash-lite-image` (NB2 Lite), `gemini-3-pro-image` (Nano Banana Pro) [O] | None described in the docs [O]; generate on a key colour and cut | Up to 14 reference images (character consistency), multi-turn editing, 512 px to 4K; SynthID watermark on every output [O] | "Google won't claim ownership" of generated content [O] | NB2.1 $0.034 1K / $0.050 2K / $0.113 4K; NB2 $0.067 / $0.101 / $0.151; Lite $0.034 at 1K; Pro $0.134 at 1–2K, $0.24 at 4K [O] |
| Midjourney | V8.2 default since 2026-07-24 [S] | None [U] | Concept and key art; no official public API [S], so it cannot sit behind a spend wrapper | Paid plans allow commercial use; companies over $1M gross revenue need Pro or Mega [S] | Plans $10 / $30 / $60 / $120 per month [S] |
| Black Forest Labs | FLUX 3 family: Image, Image Klein (5.6B, open weights), Max, Video, Action; announced 2026-07-23 [S]. FLUX.2 still supported [O] | Not stated in research [U] | Text-to-image, image-to-image editing, outpaint, erase; LoRA training on Klein [O] | API outputs commercial. Self-hosting FLUX 3 Klein or FLUX.2 [dev] commercially needs a paid licence tier. FLUX.2 [klein] ships as Apache 2.0 **and** Non-Commercial variants [O] | FLUX 3 Image $0.048 1K / $0.10 2K / $0.607 4K; Klein $0.009 1K / $0.014 2K [O] |
| Recraft | V4.1 (default), V4.1 Flash V2, V4 Styles, V4 [O] | Background removal $0.01 [O] | Native SVG vectors (UI icons), style references, vectorize $0.01 [O] | Paid plans: you own outputs. Free plan: Recraft owns them, no commercial use [S] | Raster $0.035 (Flash V2 $0.007), vector $0.08, pro vector $0.30 [O] |
| Ideogram | 4.6 newest (native 4K) after 4.5 (around 2026-10-01) [S]; 4.0 released as open weights under a commercial licence 2026-06-03 [O] | Transparent-background endpoint [O] (see conflicts) | Best text-in-image; character reference on 3.0 [O] | 4.0 weights carry a commercial licence [O] | 4.0 $0.03 / $0.06 / $0.10; 4.0 Transparent $0.03–0.10 at 1–2K [O]; 4.6 at 4K top tier $0.20 [S] |
| Adobe Firefly | Firefly Image Model 5 (Oct 2025) still Adobe's newest own model [S]; 2026-11-10 update added partner models GPT Image 2.6, Nano Banana 2.1, Seedance 2.5, Kling 4.0 [O] | Layered editing in Adobe apps [O] | Precise, layered edits inside Photoshop-class tools [O] | Own models trained on licensed data with IP indemnity on qualifying business plans [S]; partner models not covered [S] | Credit-based [S] |
| Stability (open weights) | SD 3.5 still newest; no SD4 on Stability's news page [O]; SD4 claims [U] | Pipeline-dependent | Local ControlNet and LoRA pipelines | Community Licence free under $1M annual revenue; Enterprise above [O] | Self-hosted |

**Conflicts (flagged by the research):**
- OpenAI Batch for 2.6: a secondary source says Batch is not supported; OpenAI's pricing page lists Batch at $15/M.
- Ideogram transparency: the 4.0 press release says alpha comes from a Background Remover cutout; the API price list has a Transparent generation endpoint.
- `gpt-image-2` alpha: some secondary sources say it lacks alpha through the Responses tool or Replicate. Check your host with one paid test before a batch.

**Shutdowns [O]:** Google `-preview` image IDs shut 2026-06-25; `gemini-2.5-flash-image` shuts 2027-03-15; Imagen 4 shut 2026-08-17.

Sources: https://developers.openai.com/api/docs/guides/image-generation · https://developers.openai.com/api/docs/pricing · https://ai.google.dev/gemini-api/docs/pricing · https://ai.google.dev/gemini-api/docs/deprecations · https://ai.google.dev/gemini-api/docs/image-generation (these now load from aistudio.google.com/docs) · https://bfl.ai/pricing · https://www.recraft.ai/docs/api-reference/pricing · https://ideogram.ai/news/ideogram-4.0 · https://ideogram.ai/pricing · https://stability.ai/license · https://news.adobe.com/news/2026/11/adobe-firefly-expands

## 2. 3D (image-to-3D, rigging, retarget)

| Vendor | IDs (as of 2026-11; verify) | Rigging and animation | Topology and texture | Terms | Price |
|---|---|---|---|---|---|
| Tripo | H3.1 = `v3.1-20260211` (default); texture model `v3.5-20260815` [O]. P2.0 with native quads official late Sep 2026 [S] | Rigging `v3.0-20260909`: biped, 6 other creature types and "others". Bone naming presets: tripo, mixamo, actorcore, unity, unreal, vrm. Rig Check free; Auto Rig 25 cr; Retarget 10 cr per animation, 100+ presets, in-place mode [O] | `quad=true` gives FBX quads (+5 cr, up to 150k faces); `smart_low_poly` (+10 cr, 500–20k faces); parts (+20 cr); PBR; delighting; up to 2M faces [O] | Not covered by research; verify on the vendor's terms page | Image-to-3D 20 / 30 / 40 / 50 cr for no texture / standard / detailed / 8K; page shows ¥0.07 per credit [O]; USD per credit [U] |
| Meshy | `meshy-7.1` latest; `meshy-7` stops working as `ai_model` on 2026-12-31 [O] | Rigging 5 cr; biped `skeleton_template` (mixamo, ue5_mannequin) and `include_fingers` (2026-11-10); quadruped added 2026-11-18; animation 3 cr per action; text-to-motion [O] | Remesh 5 cr, UV unwrap 5 cr, PBR 2K–8K [O] | Not covered by research; verify | Image-to-3D 20 cr mesh only, 30 textured, 35 at 8K [O]; about $0.015–0.02 per credit implied by plans [S] |
| Hyper3D Rodin | Gen-2.5 (May 2026); no Gen-3 [S] | No auto-rig listed [U] | Smart Low-Poly, quads on Business plan, baked normals [O]; 4K PBR [S] | Business plan ($60–96/mo) includes API and a commercial licence [O] | $1.50 per direct credit; Creator $15–24/mo [O]; base generation 0.5 cr [S] |
| Tencent Hunyuan3D | 3.0 and 3.1 hosted only [S]; newest open weights Hunyuan3D-2.1, plus 2mini and Omni [O] | Omni accepts skeleton-pose conditions [S]; no rigging | PBR; needs retopology | Weights free, but the licence **excludes the EU, UK and South Korea**, and products over 1M MAU need a Tencent licence [O] | Self-hosted or Tencent Cloud |
| Microsoft TRELLIS.2 | TRELLIS.2-4B, MIT; training code 2026-01-10 [O] | None | Any topology, PBR GLB, dense mesh needing retopology; Linux, NVIDIA GPU with 24 GB or more [O] | MIT, but its nvdiffrast/nvdiffrec dependencies are licensed for research only [S] | Self-hosted |
| CSM | Bought by Google (DeepMind) Jan 2026; Cube API future unclear [S] | | | | Pricing page did not load |
| Luma | Genie text-to-3D shut 2026-01-01 [S] | | | | |

- **Riggable humanoids through a first-party API:** only Tripo and Meshy [O].
- **Game-ready topology without manual retopo:** Tripo (quads, smart low-poly, P2.0), Meshy (remesh), Rodin (Smart Low-Poly, quads).
- **Manual retopology and rigging needed:** Hunyuan3D and TRELLIS output.
- **Model IDs seen in production use differ in format from vendor docs** (for example a dated "P2-..." quad ID): pin the ID string exactly as the vendor's current docs list it, and log the ID the response reports [inference].

Sources: https://developers.tripo3d.com/en/models/v3-1 (and /rig, /animation) · https://docs.meshy.ai/api/pricing.md · https://docs.meshy.ai/api/changelog.md · https://hyper3d.ai/pricing · https://github.com/Tencent-Hunyuan · https://huggingface.co/tencent/Hunyuan3D-2.1/blob/main/LICENSE · https://github.com/microsoft/TRELLIS.2

## 3. Audio (SFX, voice, music)

| Vendor | IDs (as of 2026-11; verify) | Use | Commercial terms | Price | Removal dates |
|---|---|---|---|---|---|
| ElevenLabs TTS | `eleven_v4` (launched 2026-09-28 [S]; 90+ languages, 100k-character limit), `eleven_v4_turbo` (about 100 ms latency), `eleven_v3` (5k characters, multi-speaker dialogue), `eleven_v3_conversational`, `eleven_multilingual_v2`, `eleven_flash_v2_5` [O] | Character VO, barks, placeholder VO | See rights-and-disclosure.md (performer consent) | v4 $0.08 / 1K chars; v4 turbo $0.04; v3 $0.08; multilingual v2 $0.08; flash v2.5 $0.04 [O] | Older turbo models deprecated; use flash [O] |
| ElevenLabs voice design | `eleven_ttv_v3` [O] | Designed (non-cloned) voices | | | |
| ElevenLabs SFX | `eleven_text_to_sound_v3` [O] | SFX, short loops | | $0.12/min [O] | **v2 removed 2027-03-01** [O] |
| ElevenLabs music | `music_v2_5` newest; `music_v2` (5-minute cap) [O] | Music beds | Commercial use licensed on Starter and above [O] | `music_v2` $0.15/min [O] | **`music_v1` removed 2027-01-31** [O] |
| Suno | v6, v6-wild (paid), v6-mini (free) [O] | Songs | Commercial rights only for songs made on a paid plan, **not retroactive** [O/S]; Warner licence deal Nov 2025 [S] | Plan-based [O]; public API [U] | |
| Udio | n/a | Avoid for shipped audio | Settled with UMG (Oct 2025) and WMG (Nov 2025); downloads disabled since Oct 2025; licensed walled-garden app planned, launch unconfirmed [S] | | |
| Stable Audio 3.0 | Open weights trained on licensed data (2026-05-20); DAW plugin 2026-08-18 [O] | Local SFX and music | Stability Community Licence [O] | Self-hosted | |
| Google Lyria | `lyria-3.5` (2026-09-03, full songs), `lyria-3-clip-preview` (30 s loops), `lyria-3-pro-preview` (legacy), `lyria-realtime-exp` [O] | Songs, loops | Not covered by research; verify | lyria-3.5 $0.08/song; clip preview $0.04 [O] | Preview IDs can shut on short notice [inference] |

Sources: https://elevenlabs.io/docs/overview/models · https://elevenlabs.io/pricing/api · https://suno.com/pricing · https://stability.ai/news-updates · https://ai.google.dev/gemini-api/docs/pricing

## 4. Video (trailers, ads, flipbook sources)

| Vendor | IDs (as of 2026-11; verify) | Strengths | Terms | Price |
|---|---|---|---|---|
| ByteDance Seedance 2.5 | Launched 2026-07-31 [O]; BytePlus ID `dreamina-seedance-2-5-260628` [S] | 30 s of audio and video per pass; up to 30 reference images, 10 videos, 10 audio clips [O] | Not covered by research; verify per host | About $0.10–0.23/s by token [S]; on Runway's API 30 cr/s at 720p [O] |
| Google Veo 3.1 (Vertex AI) | `veo-3.1-generate-001`, `veo-3.1-fast-generate-001`; **retiring on or after 2027-05-04** [O] | GA on Vertex | Not covered by research | Not covered by research |
| Google Gemini API video | `gemini-omni-1.2-flash` replaced the Veo previews, which **shut 2026-10-22** [O] | 3–15 s with audio [O] | Not covered by research | About $0.07/s at 720p, $0.104/s at 1080p [O] |
| OpenAI Sora | **Sora 2 models and Videos API shut 2026-09-24**, no replacement [O] | Remove from pipelines | | |
| Kling 4.0 | Launched 2026-10-15: up to 30 s, 4K, audio [S]; Kuaishou's own 4.0 API unconfirmed [S] | | Not covered by research | On Runway's API 15.7 cr/s at 720p [O]; Kling 3.0 API about $0.084–0.42/s [S] |
| Runway | Gen-4.5 (native audio, multi-shot) still flagship, no Gen-5 [S]; Aleph 2.0 editing 2026-05-21 [S] | One API reselling Kling, Seedance and Omni [O] | Not covered by research | $0.01 per credit; `gen4.5` 12 cr/s ($0.12/s); `veo3.1` 40 cr/s [O] |
| Luma | Ray3.2 (2026-06-09) [S] | 16-bit HDR and EXR export [S] | Not covered by research | Not covered by research |

Google also released Genie 4 (interactive worlds) on 2026-11-19 [O]; no Veo 4 exists [S].

Sources: https://seed.bytedance.com (blog) · https://docs.dev.runwayml.com/guides/pricing · https://developers.openai.com/api/docs/models/sora-2 · https://ai.google.dev/gemini-api/docs/deprecations

## 5. Choosing by need [inference]

| Need | First choice | Why / caveat |
|---|---|---|
| Sprites with real alpha | A model with native transparent output (OpenAI `background: "transparent"`, Ideogram Transparent) | Saves a cut-out step; still run the halo check after final compression |
| Character consistency across many sheets | A model that takes many reference images (Nano Banana family, up to 14) | Grade every sheet to one master afterwards; references do not stop hue drift |
| UI icons | Recraft vector output | Vectors scale cleanly; keep lettering out and set text in-engine |
| Text inside an image (key art, mock store art) | Ideogram | Shipped in-game text still belongs in the UI layer, not in pixels |
| Local LoRA style training | FLUX 3 Klein or SD 3.5 | Check the exact checkpoint's licence and your revenue band first |
| Riggable humanoid or quadruped from concept | Tripo or Meshy | Both expose engine bone-naming presets; pick the one your engine imports |
| Background 3D props | Rodin or Tripo smart low-poly | Retopo-free output costs less total than cheaper dense meshes plus manual retopo |
| SFX in bulk | ElevenLabs SFX v3 or Stable Audio 3.0 locally | Cache entries keyed to SFX v2 cannot be regenerated after 2027-03-01; keep the raw files and re-key new cues to v3 |
| Music that ships | A model whose plan licenses commercial use at generation time | Suno rights are not retroactive; avoid Udio until terms are published |
| Trailer footage | Seedance, Kling, Veo via one reseller API | One API means one spend wrapper and one ledger; never use generated footage as an App Preview |

## 6. Tool behaviour seen in production (genre-level)

- Coding-agent CLIs with built-in image generation (run on a chat subscription) expose no seed and often no model ID. Provenance must record the CLI version and session id instead, and the output file can land in the tool's session folder rather than the working directory.
- One such tool's largest 16:9 output was 1672×941. Panoramas had to be generated in halves.
- These subscription tools still spend a budget (plan usage) and must sit behind the spend wrapper; one team's ledger stopped covering art when generation moved into one. One vendor's built-in image tool embedded C2PA provenance data in its outputs.
- API tiers and web tiers of the same plan offered different models. Headless web generation hit bot checks; do not attempt a bypass, use the API.
- A 3D vendor's T-pose step called a third-party image-edit model internally. The licence chain can include models you never called directly [inference].
