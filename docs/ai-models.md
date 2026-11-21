# AI models for game production: research notes (as of 2026-11-21)

Research date: 2026-11-21. Facts were collected by web search and direct reads of vendor pages. Model IDs, prices and policy dates move fast: treat every row as "as of 2026-11; verify" and re-check the linked source before relying on it.

Confidence tags: `[official]`/`[O]` vendor page read directly; `[official-snip]` official URL seen only in a search snippet; `[secondary]`/`[S]` press, law firm or third party; `[unverified]`/`[U]` weak or no source; `[inference]` the researcher's reading.

Skills that use these notes: `gamedev-ai-asset-pipeline` (part 1), `gamedev-agentic-production` and `gamedev-brief-coordinator` (part 2), `gamedev-llm-features-engineer` (part 3).

---

## Part 1. Generative models for production assets

Tags: [O] official page read on 2026-11-21 · [S] secondary · [U] unverified. Prices are list API prices in USD unless noted.

**1) IMAGE**

| Vendor | Latest IDs | Game-art fit (alpha, refs, edit) | Commercial terms | ~Price/image |
|---|---|---|---|---|
| OpenAI | `gpt-image-2.6-sunburst` (detail, precise edits) and `gpt-image-2.6-flare` (fast). Images 2.6 launched 2026-11-04 [S]. `gpt-image-2.5-*` and `gpt-image-2` are still listed [O] | `background:"transparent"` with png or webp; several reference images; mask edits (the mask guides the prompt, not exact); markup edits; SVG and animated-GIF output; `complexity` low/med/high; quality low to max [O] | User owns output per ToS [U] (terms page not read) | $30/M image-output tokens, Batch $15/M [O]. Docs calculator ≈$0.025 per image at 823 tokens [O]. `gpt-image-2` at 1024²: ≈$0.006 / $0.053 / $0.211 for low / med / high [S] |
| Google | `gemini-nano-banana-2.1` (released 2026-10-06, recommended), `gemini-3.1-flash-image` (Nano Banana 2), `gemini-3.1-flash-lite-image` (NB2 Lite), `gemini-3-pro-image` (Nano Banana Pro) [O] | Up to 14 reference images (character consistency), multi-turn editing, 512px to 4K, SynthID watermark on every output; the docs describe no transparent output [O] | "Google won't claim ownership" of generated content [O] | NB2.1: $0.034 1K / $0.050 2K / $0.113 4K. NB2: $0.067 / $0.101 / $0.151. Lite: $0.034 at 1K. Pro: $0.134 at 1–2K, $0.24 at 4K [O] |
| Midjourney | V8.2 has been the default since 2026-07-24; V8.1 was default before it [S] | Strong for concept and key art; no official public API [S]; no alpha [U] | Paid plans allow commercial use; companies with more than $1M gross revenue need Pro or Mega [S] | Plans are $10 / $30 / $60 / $120 per month [S] |
| Black Forest Labs | FLUX 3 family: Image, Image Klein (5.6B, open weights), Max, Video, Action. Announced 2026-07-23 [S]. FLUX.2 is still supported [O] | Text-to-image and image-to-image editing, outpaint and erase tools, LoRA training on Klein [O] | API outputs are commercial. Self-hosting FLUX 3 Klein or FLUX.2 [dev] commercially needs a paid licence tier. FLUX.2 [klein] comes in Apache 2.0 and Non-Commercial variants [O] | FLUX 3 Image: $0.048 1K / $0.10 2K / $0.607 4K. Klein: $0.009 1K / $0.014 2K [O] |
| Recraft | V4.1 (default), V4.1 Flash V2, V4 Styles, V4 [O] | Native SVG vectors (good for UI icons), style references, background removal $0.01, vectorize $0.01 [O] | Paid plans: you own the outputs. Free plan: Recraft owns them and commercial use is not allowed [S] | Raster $0.035 (Flash V2 $0.007), vector $0.08, pro vector $0.30 [O] |
| Ideogram | 4.6 is newest (native 4K), after 4.5 (around 2026-10-01) [S]. 4.0 was released as open weights under a commercial licence on 2026-06-03 [O] | Best for text inside images; has a Transparent-background endpoint; character reference on 3.0 [O] | 4.0 weights carry a commercial licence [O] | 4.0: $0.03 / $0.06 / $0.10. 4.0 Transparent: $0.03–0.10 at 1–2K [O]. 4.6 at 4K, top tier: $0.20 [S] |
| Adobe Firefly | Firefly Image Model 5 (Oct 2025) is still Adobe's newest own model [S]. The 2026-11-10 announcement added editing tools and partner models: GPT Image 2.6, Nano Banana 2.1, Seedance 2.5, Kling 4.0 [O] | Layered, precise editing inside Adobe apps [O] | Adobe's own models are trained on licensed data, with IP indemnity on qualifying business plans [S]; partner models are not covered [S] | Credit-based [S] |
| Stability (open weights) | SD 3.5 is still the newest Stable Diffusion; Stability's news page shows no SD4 [O]. Claims of an SD4 release are [U] | Local ControlNet and LoRA pipelines | Community Licence is free under $1M annual revenue; Enterprise licence above that [O] | Self-hosted |

Conflicts:
- **OpenAI Batch for 2.6:** a secondary source says Batch is not supported, but OpenAI's pricing page lists Batch at $15/M.
- **Ideogram transparency:** the 4.0 press release says alpha comes from a Background Remover cutout, while the API price list has a Transparent generation endpoint.
- **gpt-image-2 alpha:** some secondary sources say it lacks alpha through the Responses tool or Replicate. Check your host.

Google shutdowns [O]: the `-preview` image IDs shut 2026-06-25; `gemini-2.5-flash-image` shuts 2027-03-15; Imagen 4 shut 2026-08-17.

Sources: developers.openai.com/api/docs/guides/image-generation and /api/docs/pricing; ai.google.dev/gemini-api/docs/pricing, /deprecations and /image-generation (these now load from aistudio.google.com/docs); bfl.ai/pricing; recraft.ai/docs/api-reference/pricing; ideogram.ai/news/ideogram-4.0 (2026-06-03); ideogram.ai/pricing (API tab); stability.ai/license; news.adobe.com/news/2026/11/adobe-firefly-expands.

**2) 3D**

| Vendor | Latest | Rigging and animation | Topology and texture | Price |
|---|---|---|---|---|
| Tripo | H3.1 = `v3.1-20260211` (default); texture model `v3.5-20260815` [O]. P2.0 with native quads went official in late Sep 2026 [S] | Rigging `v3.0-20260909`: biped, 6 other creature types, and "others". Bone naming: tripo, mixamo, actorcore, unity, unreal, vrm. Rig Check is free; Auto Rig 25 cr; Retarget 10 cr per animation, 100+ presets, in-place mode [O] | `quad=true` gives FBX quads (+5 cr, up to 150k faces); `smart_low_poly` (+10 cr, 500–20k faces); parts (+20 cr); PBR; delighting; up to 2M faces [O] | Image-to-3D: 20 / 30 / 40 / 50 cr for no texture / standard / detailed / 8K. The page shows ¥0.07 per credit [O]; USD per credit [U] |
| Meshy | `meshy-7.1` is the latest. `meshy-7` stops working as `ai_model` on 2026-12-31 [O] | Rigging 5 cr. Biped gets `skeleton_template` (mixamo, ue5_mannequin) and `include_fingers` (2026-11-10); quadruped added 2026-11-18. Animation 3 cr per action; text-to-motion [O] | Remesh 5 cr, UV unwrap 5 cr, PBR textures 2K–8K [O] | Image-to-3D: 20 cr mesh only, 30 textured, 35 at 8K [O]. Plans imply about $0.015–0.02 per credit [S] |
| Hyper3D Rodin | Gen-2.5 (May 2026); no Gen-3 [S] | No auto-rig listed [U] | Smart Low-Poly, quads on the Business plan, baked normals [O]; 4K PBR [S] | $1.50 per direct credit. Creator $15–24/mo. Business $60–96/mo includes API and a commercial licence [O]. Base generation 0.5 cr [S] |
| Tencent Hunyuan3D | 3.0 and 3.1 are hosted only (HY 3D Studio, Tencent Cloud API) [S]. Newest open weights: Hunyuan3D-2.1, plus 2mini and Omni [O] | Omni accepts skeleton-pose conditions [S]; no rigging | PBR; needs retopology | Weights are free, but the licence excludes the EU, UK and South Korea, and products over 1M MAU need a Tencent licence [O] |
| Microsoft TRELLIS.2 | TRELLIS.2-4B, MIT licence; training code released 2026-01-10 [O] | None | Any topology, PBR GLB, dense mesh that needs retopology. Linux only, NVIDIA GPU with at least 24GB [O]. Its nvdiffrast/nvdiffrec dependencies are licensed for research only [S] | Self-hosted |
| CSM | Bought by Google (DeepMind) in Jan 2026; future of the Cube API unclear [S]. Pricing page did not load | | | |
| Luma | Genie text-to-3D shut down 2026-01-01; Luma now does video and 3D capture [S] | | | |

- **Riggable humanoids through a first-party API:** only Tripo and Meshy.
- **Game-ready topology:** Tripo (quads, smart low-poly, P2.0), Meshy (remesh), Rodin (Smart Low-Poly, quads).
- **Needs manual work:** Hunyuan and TRELLIS output needs retopology and manual rigging.

Sources: developers.tripo3d.com/en/models/v3-1, /rig and /animation; docs.meshy.ai/api/pricing.md and /changelog.md; hyper3d.ai/pricing; github.com/Tencent-Hunyuan; huggingface.co/tencent/Hunyuan3D-2.1/blob/main/LICENSE; github.com/microsoft/TRELLIS.2.

**3) AUDIO**

- **ElevenLabs [O]** (elevenlabs.io/docs/overview/models, elevenlabs.io/pricing/api):
  - **Text to speech:**
    - `eleven_v4`: $0.08 per 1K characters, 90+ languages, 100k-character limit; launched 2026-09-28 [S].
    - `eleven_v4_turbo`: $0.04, about 100ms latency.
    - `eleven_v3`: $0.08, 5k characters, multi-speaker dialogue.
    - Also listed: `eleven_v3_conversational`, `eleven_multilingual_v2` ($0.08), `eleven_flash_v2_5` ($0.04).
    - Voice design uses `eleven_ttv_v3`. The turbo models are deprecated; use flash instead.
  - **Sound effects:** `eleven_text_to_sound_v3` at $0.12/min. v2 is removed 2027-03-01.
  - **Music:** `music_v2_5` is the newest. `music_v2` costs $0.15/min with a 5-minute cap, and commercial use is licensed on Starter and above. `music_v1` is removed 2027-01-31.
- **Suno:**
  - Models: v6 and v6-wild on paid plans, v6-mini on free [O suno.com/pricing].
  - Commercial rights only for songs made on a paid plan, and not retroactive [O/S].
  - Warner licence deal Nov 2025 [S]. Public API [U].
- **Udio:**
  - Settled with UMG (Oct 2025) and WMG (Nov 2025); downloads disabled since Oct 2025.
  - A licensed walled-garden app ("Starstruck") is planned for 2026; launch unconfirmed [S].
  - Avoid for shipped game audio until terms are published.
- **Stable Audio 3.0:** open-weight models trained on fully licensed data (2026-05-20), DAW plugin added 2026-08-18; Community Licence applies [O stability.ai/news-updates].
- **Google Lyria [O]:** `lyria-3.5` (2026-09-03, full songs, $0.08/song); `lyria-3-clip-preview` (30s loops, $0.04); `lyria-3-pro-preview` (legacy); `lyria-realtime-exp`.
- **SAG-AFTRA Interactive Media Agreement:** ratified July 2025 with 95.04%, runs to 2028-10-31 [S: fkks.com law-firm summary of the full text, 2026-01-29].
  - **What it covers:** voice and visual digital replicas. Replicas made from non-union material or by prompting with a performer's name also need consent and bargaining.
  - **Consent:** a clear, separate written consent with a reasonably specific description of use. This includes real-time generation (chatbots) and sensitive content. Consent generally cannot be taken at hire for future games.
  - **Pay and reporting:** pay is per generated line (about 10 words). A usage report is due within 90 days of release. Performers can suspend consent during a strike.
  - **Excluded:** "traditional AI" (animation, rigging) and audio processing such as pitch or noise work.

**4) VIDEO (trailers, store videos)**

- **Seedance 2.5 (ByteDance):**
  - Launched 2026-07-31 [O seed.bytedance.com blog]. 30s of audio and video per pass; references up to 30 images, 10 videos and 10 audio clips [O].
  - BytePlus ID `dreamina-seedance-2-5-260628`, priced by token at about $0.10–0.23/s [S].
  - On Runway's API: 30 cr/s at 720p [O].
- **Google:**
  - Veo 3.1 is GA on Vertex AI as `veo-3.1-generate-001` and `veo-3.1-fast-generate-001`, retiring on or after 2027-05-04 [O].
  - In the Gemini API, the Veo previews shut 2026-10-22. The replacement is `gemini-omni-1.2-flash`: 3–15s with audio, about $0.07/s at 720p and $0.104/s at 1080p [O].
  - No Veo 4 [S]. Genie 4 (interactive worlds) released 2026-11-19 [O].
- **OpenAI Sora:** the Sora 2 models and Videos API shut 2026-09-24 with no replacement [O developers.openai.com/api/docs/models/sora-2]. Drop it from pipelines.
- **Kling:**
  - Kling 4.0 launched 2026-10-15: up to 30s, 4K, audio [S].
  - Kuaishou's own API for 4.0 is unconfirmed [S]. It is on Runway's API at 15.7 cr/s list price at 720p [O].
  - Kling 3.0 API: about $0.084–0.42/s [S].
- **Runway:**
  - Gen-4.5 (native audio, multi-shot) is still the flagship; no Gen-5 [S]. Aleph 2.0 editing launched 2026-05-21 [S].
  - API is $0.01 per credit. `gen4.5` is 12 cr/s ($0.12/s) and `veo3.1` is 40 cr/s. Runway also resells Kling, Seedance and Omni [O docs.dev.runwayml.com/guides/pricing].
- **Luma:** Ray3.2 (2026-06-09) supports 16-bit HDR and EXR export [S].
- **Store limit:** Apple guideline 2.3.4 says App Previews "may only use video screen captures of the app itself" [O]. Generated footage is for trailers and ads only.

**5) STORE AND LEGAL**

- **Steam** [O partner.steamgames.com/doc/gettingstarted/contentsurvey]:
  - The Content Survey's AI section covers content that ships and that players consume: art, sound, narrative, localization. Efficiency tools are not the focus. This was rewritten around 2026-01-16/17 [S].
  - Pre-Generated content is reviewed like any other content.
  - Live-Generated content must also describe the guardrails against illegal output.
  - No live-generated AI is allowed in Adult Only sexual content.
  - Disclosures appear on the store page [S].
- **Apple** (guidelines last updated 2026-10-16) [O]:
  - 1.2 now names "AI content creation apps": they need filtering, reporting, blocking and protections against non-consensual intimate imagery.
  - 5.1.2(i): disclose, and get explicit permission, before sending personal data to a third-party AI.
  - 2.5.19: no hidden features.
- **Google Play AI-Generated Content policy** [O support.google.com/googleplay/android-developer/answer/14094294]:
  - Covers apps that generate content from text, voice or image prompts. They must have in-app reporting or flagging.
  - Bans non-consensual deepfake sexual content, scam voice or video of real people, and similar.
  - An Aug 2026 Android blog post asks for custom input and output moderation [S].
- **EU AI Act Article 50** [O EUR-Lex 32024R1689; Regulation (EU) 2026/1744]:
  - **Applies from 2026-08-02:**
    - 50(1): tell users they are talking to an AI unless it is obvious. This is relevant to LLM-driven NPCs.
    - 50(2): providers must mark output in a machine-readable way.
    - 50(4): deployers must label deepfakes. For clearly artistic or fictional works, the disclosure only has to avoid hampering "the display or enjoyment" of the work.
  - **AI Omnibus (in force 2026-07-27):**
    - For generative systems already on the market before 2026-08-02, the 50(2) marking duty is due by 2026-12-02.
    - Annex III high-risk rules move to 2027-12-02 and Annex I to 2028-08-02.
  - **Code of Practice:** the final transparency/marking code came out 2026-06-10, with EU label icons [O digital-strategy.ec.europa.eu].
  - **Conflict:** Goodwin says Article 50 moved to 2027-12-02, and earlier drafts proposed 2027-02-02 or 2026-11-02. The Official Journal text says 2026-12-02, and that grace period covers marking only.
- **US Copyright Office** [O copyright.gov/ai]:
  - Part 2 (2025-01-29): prompts alone do not make output protectable; human selection, arrangement and modification can be.
  - Part 3 (training) is still a pre-publication draft (2025-05-09). The Office's AI page shows no 2026 update.
  - 2026 change: the Supreme Court denied cert in Thaler v. Perlmutter on 2026-03-02, so the human-authorship rule stands. Allen v. Perlmutter is still undecided [S].

---
Notes:

---

## Part 2. Coding agents and their models

Every fact carries a tag and a source number; the full URLs are listed at the end. Pages were read on 2026-11-21 in a headless browser. Some vendor URLs redirect, so the source list gives the address each page actually loaded from. Where a vendor page shows no date, it is marked n.d.

**Five common assumptions are out of date:**
- Anthropic's current models are 5.5-generation (Opus, Sonnet, Haiku) plus Fable 5.2.
- No Codex-branded model is current. `gpt-5.3-codex` is deprecated in Codex, though Copilot still uses it as its long-term-support fallback. [official S13, S29]
- The OpenAI line is GPT-6.x (Astra, Sol, Terra, Luna), not plain "GPT-6".
- Google's current family is Gemini 4, not 3.x. Gemini CLI was replaced by Antigravity CLI for some users.
- Kimi is on K3.1 Pro; K2.x is deprecated.

---

### 1. Anthropic

**Current models** [official S1, S2; launch dates S5]

| Model | API ID | Context / max output | $ per MTok in/out | Cache hit | Default effort | Launched |
|---|---|---|---|---|---|---|
| Fable 5.2 | `claude-fable-5-2` | 1M / 128K | 8 / 40 | 0.20 | high | 2026-11-09 |
| Opus 5.5 | `claude-opus-5-5` | 1M / 128K | 4 / 20 | 0.20 | medium | 2026-09-22 |
| Sonnet 5.5 | `claude-sonnet-5-5` | 1M / 128K | 2 / 10 | 0.10 | high | 2026-09-28 |
| Haiku 5.5 | `claude-haiku-5-5` | 1M / 128K | 0.10 / 0.50 for prompts up to 100K tokens; 0.50 / 2.50 above that | 0.01 / 0.05 | medium | 2026-10-07 [secondary S30] |

- All four models have adaptive thinking (always on for Fable 5.2 and Opus 5.5) and a Jun 2026 knowledge cutoff. [official S1]
- Claude Mythos 5.2 (`claude-mythos-5-2`) has the same capability as Fable 5.2 but is open only to verified organizations. [official S3]
- Bedrock IDs differ, e.g. `global.anthropic.claude-fable-5-2` and `anthropic.claude-opus-5-5`. [official S1]
- Legacy models still listed [official S1, S2]:
  - Fable 5.1: $10/$50
  - Opus 5 and Opus 4.8: $5/$25
  - Sonnet 5: $2/$10
  - Haiku 4.5: $1/$5, 200K context
- Fast mode gives up to 2.5x output speed at 2x price. It is available on Fable 5.2 and Opus 5.5. [official S2, S4]
- Claude 4.7 and later use a tokenizer that produces about 30% more tokens for the same text. [official S2]
- Release history [secondary]: Fable 5 launched 2026-06-09 (MacRumors) and Opus 5 on 2026-07-24 (Axios).

**Claude Code: models.** The newest changelog entry is v2.1.330; I did not capture its date. [official S11]
- Aliases [official S6]: `default`, `best` (same as opus), `fable`, `opus`, `sonnet`, `haiku`, `sonnet[1m]`, `opus[1m]`, `opusplan`.
- On the Anthropic API, opus, sonnet and haiku resolve to the 5.5 models, and fable to Fable 5.2.
- On Bedrock and Google's Agent Platform, sonnet and haiku resolve to 4.5. On Microsoft Foundry, opus resolves to 4.6.
- No plan uses Fable as its default; users must pick it.
- Minimum Claude Code versions: Fable 5.2 needs v2.1.321, Opus 5.5 v2.1.280, Sonnet 5.5 v2.1.284, Haiku 5.5 v2.1.293.
- Pin a full model ID for reproducible behaviour; aliases move to newer models.

**Claude Code: features that matter for long game projects**
- **Skills** [official S7]
  - Locations: `~/.claude/skills/`, `.claude/skills/`, nested `<subdir>/.claude/skills/`, `--add-dir`, plugin `skills/` (invoked as `/plugin:skill`), and managed settings. Symlinks are followed.
  - The skill listing's budget is about 1% of the context window.
  - Each skill's description plus `when_to_use` is truncated at 1,536 characters in the listing.
  - After compaction, re-attached skills share a 25,000-token budget.
- **Subagents** [official S9]
  - Built-in Explore is read-only and runs on the parent's model. When the parent runs Fable, Explore uses Opus on subscription and Console accounts.
  - Custom subagents can set their own model; Anthropic explicitly suggests Haiku to control cost.
  - Claude Code warns when custom subagent descriptions exceed 15,000 tokens.
- **Parallel work** [official S8]
  - Agent view (`claude agents`, research preview) dispatches and monitors background sessions.
  - Agent teams are experimental and off by default.
  - Dynamic workflows run many subagents from a script (`/workflows`).
  - Projects run cloud sessions (public beta).
  - Worktrees: the `--worktree` flag and `.worktreeinclude`. `/batch` splits one change across 5 to 30 worktree-isolated subagents.
  - Background bash, `/tasks`, and cross-session messaging.
- **Automation** [official S11]
  - `/goal` keeps Claude working until a completion condition is met.
  - `/loop` and cron scheduling inside a session; cloud scheduled tasks (formerly routines).
  - Hooks, which skills can also register through the `hooks` frontmatter key.
  - Plugins bundle skills, hooks and MCP servers, can declare dependencies with semver ranges, and can be tested with `claude plugin eval`.
- **Compaction**: models with a native 1M window auto-compact at about 967K tokens; `/autocompact` changes this. [official S6]
- **AGENTS.md**: Claude Code reads it only when no CLAUDE.md or CLAUDE.local.md exists in the working directory or above (setting `claude-md-or-agents-md`). Other options are `claude-md-and-agents-md` and `claude-md`. It never reads `AGENTS.override.md` or anything under `.agents/`. [official S10]

**Agent Skills frontmatter: the three validators disagree** [official S7, S12, S17]

| Key | agentskills.io spec | Claude Code | Anthropic upload / Skills API | OpenAI `quick_validate.py` |
|---|---|---|---|---|
| `name` | Required; up to 64 chars of a-z, 0-9 and single hyphens; no hyphen at start or end; must match the folder name | Optional; defaults to the folder name | allowed | allowed, up to 64 |
| `description` | Required, up to 1024 chars | Recommended; listing truncates at 1,536 together with `when_to_use` | allowed | allowed, up to 1024 |
| `license` | optional | accepted, ignored | allowed | allowed |
| `compatibility` | optional, up to 500 chars | accepted, ignored | allowed | **rejected** |
| `metadata` | optional string-to-string map | accepted | allowed | allowed |
| `allowed-tools` | optional, experimental, space-separated | supported | allowed | allowed |

- **Claude Code-only keys:** `when_to_use`, `argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`, `disallowed-tools`, `model`, `effort`, `context: fork`, `agent`, `background`, `hooks`, `paths`, `shell`.
  - Claude Code silently ignores keys it doesn't recognise.
  - The claude.ai upload, Skills API and `package_skill.py` stop with an "Unexpected key(s)" error. [official S7]
- **Portable set for this pack:** `name`, `description`, `license`, `metadata`, `allowed-tools`.
- **Body guidance:** keep SKILL.md under 500 lines and under 5,000 tokens, and keep references one level deep. [official S12]
- **Conflict:** a third-party validator claims Codex limits of 100 characters for the name and 500 for the description [unverified]. OpenAI's own script uses 64 and 1024 [official S17].

---

### 2. OpenAI

**Models.** Prices are standard rates for prompts up to 272K tokens; above 272K the higher rate applies to the whole request. [official S13, S14]

| ID | Vendor role | Default context in Codex | $ per MTok in / cached / out | Above 272K in/out |
|---|---|---|---|---|
| `gpt-6.2-astra` | Hardest end-to-end work | 272K, up to 1M | 8 / 0.40 / 40 | 16 / 60 |
| `gpt-6.2-sol` | Everyday coding | 500K, up to 1M | 2 / 0.10 / 10 | 4 / 15 |
| `gpt-6.1-terra` | Fast; writing, visual work, computer use (needs CLI 0.159.0+) | n.d. | 1 / 0.05 / 5 | 2 / 7.50 |
| `gpt-6-luna` | Focused, high-volume, repeatable tasks | n.d. | 0.10 / 0.01 / 0.50 | 0.20 / 0.75 |
| `gpt-6-astra` | Earlier flagship | n.d. | 10 / 1 / 50 | 20 / 75 |
| `gpt-6.1-sol` | Suggested for a config shared with the IDE extension | 500K | 2 / 0.10 / 10 | 4 / 15 |

- **Rate modifiers** [official S14]:
  - Batch costs 50% of standard.
  - Fast mode costs 2x ("Priority" was renamed Fast on 2026-07-30).
  - Ultrafast on 6.2 costs 3x standard through 2027-02-28, then 6x.
  - Eligible background requests are 30% cheaper with a 2-hour completion window and 40% cheaper with an 8-hour window.
  - The GPT-5.6 Sol promotional price ends 2026-11-30.
- **Release timing:** Codex CLI 0.171.0 (2026-11-20) added GPT-6.2 Sol and Astra to the model catalog, with Sol as the default. [official S20] GPT-6.2 reached ChatGPT Work and Codex on 2026-11-17 [secondary].
- **Retired or deprecated in Codex with ChatGPT sign-in** (API-key sessions are not affected) [official S13]:
  - `gpt-5.3-codex-spark` retired 2026-09-14.
  - `gpt-5.4` and `gpt-5.4-mini` retired 2026-08-31.
  - `gpt-5.5` retired 2026-10-14.
  - `gpt-5.2` and `gpt-5.3-codex` are deprecated.
- **Reasoning effort in Codex** [official S13]:
  - Levels run Light (called Low in the CLI), Medium, High, Extra High.
  - Max gives the model more time to reason on one task.
  - Ultra splits work across subagents; OpenAI says most tasks don't need it, and Luna doesn't support it.

**Codex skills** [official S15]
- **Locations:**
  - `.agents/skills` in each directory from the working directory up to the repo root.
  - `$HOME/.agents/skills` for the user. (Codex CLI 0.170.0 also still reads `$CODEX_HOME/skills`, default `~/.codex/skills`, and its bundled skill installer writes there; observed in the binary, not in the docs page.)
  - `/etc/codex/skills` for admins.
  - Bundled system skills (`skill-creator`, `skill-installer`).
  - Symlinks are followed. Skills that share a name are not merged; both can appear.
- **Invocation:** explicitly with `$skill` or `/skills`, or implicitly when the task matches the description.
- **Listing budget:** 2% of the context window, or 8,000 characters if unknown. Descriptions are shortened first, so front-load the trigger words. `skills.max_context_tokens` raises it to at most 10,000.
- **Disabling:** `[[skills.config]]` with `path` or `name` and `enabled = false`; `[skills.bundled] enabled = false` turns off the system skills.
- **Distribution:** plugins in the plugin directory shared by ChatGPT and Codex.
- Codex has added a local-only migration for Claude Code skills (PR #60492). [official S20]

**`agents/openai.yaml` fields** [official S15, S16]
- `interface`: `display_name`, `short_description` (25–64 characters), `icon_small`, `icon_large`, `brand_color`, `default_prompt`.
  - `default_prompt` should be about one sentence and mention the skill as `$skill-name`.
  - Quote every string value.
- `policy.allow_implicit_invocation` defaults to true. It appears in the docs but not in the repo's reference file.
- `dependencies.tools[]`: `type` (only `"mcp"` for now), `value`, `description`, `transport`, `url`.
- I found no newer fields.

**Codex custom agents** [official S19]
- Each agent is a TOML file in `~/.codex/agents/` or `.codex/agents/`.
- Required: `name`, `description`, `developer_instructions`. Optional: `model`, `model_reasoning_effort`.
- Built-in agents: `default`, `worker`, `explorer`.
- Global defaults live under `[agents]`, e.g. `default_subagent_model`.

**AGENTS.md in Codex** [official S18]
- **Global layer:** in `~/.codex` (or `CODEX_HOME`), `AGENTS.override.md` is used if present, otherwise `AGENTS.md`.
- **Project layer:** Codex walks from the repo root down to the working directory and takes at most one file per directory, in this order: `AGENTS.override.md`, `AGENTS.md`, then names in `project_doc_fallback_filenames`.
- **Merge and cap:** files are concatenated root-first, so closer files win. The total is capped by `project_doc_max_bytes` (32 KiB default).
- **Code review:** a `## Code Review Rules` section drives Codex reviews on GitHub.
- **Standard:** the open format at agents.md lists Codex, Cursor, Gemini CLI, Copilot's coding agent and others as supporting it. [official S22] It is stewarded by the Agentic AI Foundation under the Linux Foundation [secondary].

---

### 3. Other agents (model names only)

- **Google Gemini API** [official S23, S24]. All have a 1M-token context.
  - `gemini-4-carbon`: strongest reasoning. $2/$10 until Nov 30, then $4/$20 from Dec 1.
  - `gemini-4-neon`: frontier reasoning. $3/$15.
  - `gemini-4-hydrogen`: the recommended default for coding and agent work. $1.50/$7.50.
  - `gemini-3.8-flash`: $0.75/$3.75 until Dec 31, then $1.50/$7.50.
  - `gemini-3.5-flash-lite`: $0.30/$2.50.
  - `gemini-4-argon` is on the pricing page at Carbon's prices but missing from the Latest models overview (see conflicts).
- **Gemini CLI → Antigravity CLI (`agy`).** Google announced the move on 2026-05-19. [official S26]
  - Gemini CLI's docs say it was replaced for unpaid-tier and Google One users on 2026-06-18, and that it is not optimised for Gemini 4 Argon. [official S25]
  - Antigravity CLI keeps Agent Skills, Hooks, Subagents, and Extensions (now Antigravity plugins). [official S26]
- **Moonshot Kimi** [official S27]
  - Current: `kimi-k3.1-pro` (flagship, 3T-class, 1M context), `kimi-k3.1-pro-highspeed`, and `kimi-k3` (previous flagship).
  - `kimi-k2.7-code`, `kimi-k2.7-code-highspeed` and `kimi-k2.6` are closed to new users, with deprecation expected late Dec 2026.
  - Prices: K3.1 Pro $2/$10, K3 $3/$15 [secondary].
  - Kimi Code is a Moonshot product; the claim that its CLI is at v2.1.0 (2026-09-23) is [unverified].
- **Cursor** [official S28]
  - Its own models: Composer 2.5 and Grok 4.7, 4.6 and 4.5.
  - Third-party models: Claude Fable 5.2, Opus 5.5, Sonnet 5.5, Haiku 5.5; Gemini 4 Carbon, Neon, Hydrogen and Argon; Gemini 3.1 Pro and 3.8 Flash; Muse Wonder; GPT-5.6 Sol, Terra and Luna.
  - Composer 2.5 costs $0.50/$2.50 with a 200K context [secondary].
- **GitHub Copilot** (generally available) [official S29]
  - OpenAI: GPT-6.2 Astra and Sol, GPT-6.1 Sol and Terra, GPT-6 Astra, Sol and Luna, GPT-5.6, GPT-5.3-Codex (fallback for Auto model selection).
  - Anthropic: Claude Fable 5, 5.1 and 5.2, Opus 5.5, Sonnet 5.5 and 5, Haiku 5.5.
  - Google: Gemini 4 Argon, Carbon, Hydrogen and Neon; Gemini 3.8 Flash.
  - Others: MAI Code 2, MAI Code 2 Flash and MAI-Code-1.1-Flash; Kimi K3; Grok 4.5 to 4.7.
  - MAI Code 2 was announced 2026-11-17 [secondary].

---

### 4. Model routing

**What the vendors say**
- **Anthropic** [official S1, S3, S4, S6, S9]
  - Start with Opus 5.5 for most work. Move to Fable 5.2 only if evals at xhigh or max effort still fall short.
  - Sonnet 5.5 for everyday coding; Haiku 5.5 for the lowest latency and price, including subagent tasks.
  - Tune effort before you switch models.
  - Anthropic's own measurements:
    - On work bigger than one context window, Opus 5.5 with Sonnet 5.5 subagents cost about a third less than Opus alone at about the same score.
    - Adding Haiku 5.5 subagents cut cost 32% and pass rate about 4 points, roughly the same as lowering effort.
    - The advisor pattern scored +1.7 points (at the edge of run-to-run noise) for about 2.1x the cost.
  - In Claude Code, `opusplan` runs Opus in plan mode and Sonnet for execution.
- **OpenAI** [official S21]
  - Start with GPT-6.2 Sol; use Astra for complex projects.
  - Luna for small, repeatable, frequent automations; Terra for visual and computer-use work.
  - Its effort ladder runs from Luna at Low (small edits) up to Astra at Extra High (open-ended trade-offs).
- **Google** [official S23]
  - Hydrogen is the default for coding and agent work; Carbon or Neon for deep reasoning.
  - 3.5 Flash-Lite for high-throughput subagents and routing.

**Suggested tiers.** This table is my own synthesis, built from the vendor lines above.

| Role | Claude | Codex / OpenAI | Gemini |
|---|---|---|---|
| Planning, architecture, review of hard diffs | Opus 5.5 (Fable 5.2 to escalate) | gpt-6.2-astra | gemini-4-carbon / neon |
| Bulk implementation and edits | Sonnet 5.5 | gpt-6.2-sol | gemini-4-hydrogen |
| Cheap triage, search, extraction subagents | Haiku 5.5 | gpt-6-luna | gemini-3.5-flash-lite |
| Visual work and computer use | Opus 5.5 | gpt-6.1-terra | n/a |

---

### 5. Conflicts to keep flagged

- **Gemini 4 Argon:** the pricing page calls it "efficient", it is listed by Copilot and Cursor, and the Gemini CLI banner points users to Antigravity for it. But the Latest models overview leaves it out. Secondary sources disagree on whether it is publicly callable.
- **Cursor naming:** Cursor lists GPT-5.6, not GPT-6.x. Its docs may be lagging.
- **GPT-6.2 in the IDE:** the GPT-6.2 cards say "App and CLI", and the docs suggest `gpt-6.1-sol` for a config shared with the IDE extension. GPT-6.2 may not be in the IDE yet.
- **Sonnet 5 price:** secondary sites say $3/$15; Anthropic's pricing page says $2/$10. [official S2]
- **Codex skill limits:** 100/500 per a third-party tool versus 64/1024 in OpenAI's script.
- **`compatibility` key:** allowed by the spec and by Anthropic, rejected by OpenAI's validator.

---

### Sources

- S1 https://platform.claude.com/docs/en/about-claude/models/overview (n.d.)
- S2 https://platform.claude.com/docs/en/about-claude/pricing (n.d.)
- S3 https://platform.claude.com/docs/en/about-claude/models/choosing-a-model (n.d.)
- S4 https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence (n.d.)
- S5 https://platform.claude.com/docs/en/release-notes/overview (dated entries)
- S6 https://code.claude.com/docs/en/model-config
- S7 https://code.claude.com/docs/en/skills
- S8 https://code.claude.com/docs/en/agents
- S9 https://code.claude.com/docs/en/sub-agents
- S10 https://code.claude.com/docs/en/memory
- S11 https://code.claude.com/docs/llms.txt and https://code.claude.com/docs/en/changelog
- S12 https://agentskills.io/specification
- S13 https://learn.chatgpt.com/docs/models.md (redirected from developers.openai.com/codex/models)
- S14 https://developers.openai.com/api/docs/pricing.md
- S15 https://learn.chatgpt.com/docs/build-skills.md
- S16 https://github.com/openai/skills/blob/main/skills/.system/skill-creator/references/openai_yaml.md
- S17 https://raw.githubusercontent.com/openai/skills/main/skills/.system/skill-creator/scripts/quick_validate.py
- S18 https://learn.chatgpt.com/docs/agent-configuration/agents-md.md
- S19 https://learn.chatgpt.com/docs/agent-configuration/subagents.md
- S20 https://learn.chatgpt.com/docs/changelog (Codex CLI 0.171.0, 2026-11-20)
- S21 https://learn.chatgpt.com/docs/model-selection.md
- S22 https://agents.md/
- S23 https://ai.google.dev/gemini-api/docs/latest-model (redirected to aistudio.google.com/docs/latest-model)
- S24 https://aistudio.google.com/docs/pricing
- S25 https://geminicli.com/docs/cli/model-routing/ (banner)
- S26 https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/ (2026-05-19)
- S27 https://platform.kimi.ai/docs/models
- S28 https://cursor.com/docs/models-and-pricing
- S29 https://docs.github.com/en/copilot/reference/ai-models/supported-models
- S30 https://9to5mac.com/2026/10/07/anthropic-upgrades-claude-with-new-haiku-5-5-model-details-here/ (secondary)
- Other [secondary] items: MacRumors 2026-06-09 (Fable 5), Axios 2026-07-24 (Opus 5), github.blog changelog 2026-11-17 (MAI Code 2), and WebSearch summaries for the Kimi and Composer prices.

---

## Part 3. LLM features inside games

Tags: [official] official page opened 2026-11-21 · [official-snip] official URL seen only in a search snippet · [secondary] press or law firm · [unverified] weak source or none found · [inference] my reading, not a claim from a source. [n] = source list at the end.

### 1. On-device
#### Apple Foundation Models (FM) framework
| Item | Fact |
|---|---|
| Model | About 3B parameters on-device [official 4, 2025]. Apple replaced the model in iOS 26.4 (better instruction following and tool calling, fewer false-positive guardrail blocks). It replaced it again in iOS 27 ("rebuilt from the ground up", now accepts images). Apple says to retest prompts after every model change [official 1,3] |
| Context | 4,096 tokens per session. Instructions, prompts, tool schemas, tool input and output, @Generable schemas and the model's output all share it. Going over throws an error. iOS 26.4 added contextSize and tokenCount(for:) [official 1,2] |
| APIs | Guided generation (@Generable) and the Tool protocol. iOS 27 adds ToolCallingMode, DynamicProfile and the LanguageModel protocol (Anthropic and Google Swift packages, CoreAILanguageModel, MLXLanguageModel). Also new: an Evaluations framework, the fm CLI and a Python SDK (Mar 2026). The framework core is going open source [official 1,3] |
| Server tier | PrivateCloudComputeLanguageModel: 32K context, reasoning levels [official 3]. No cloud API cost for apps in the Small Business Program with under 2M first-time downloads [official 6]. Terms for everyone else not found [unverified] |
| Guardrails | On-device guardrails check both input and output. You set them with SystemLanguageModel.Guardrails; permissiveContentTransformations is only for transforming text. Private Cloud Compute (PCC) guardrails can't be configured. Errors are guardrailViolation and refusal. A refusal can come back as plain text that code can't reliably detect [official 5]. Violent fiction may trip the guardrails, so script fallback lines [inference] |
| Devices (iOS 27) | iPhone 15 Pro/Pro Max, iPhone 16 or later, Air, Duo; iPad mini A17 Pro/A20 Pro; iPad and Mac with M1 or later; MacBook Neo; Vision Pro; Apple Watch S9+/Ultra 2+/SE 3 (paired). Needs up to 14 GB of storage, and device and Siri language must match [official 7]. Check model availability at runtime |
| Terms | DPLA 3.3.8(I) sets requirements for using the FM framework [official 41] |

#### Android Gemini Nano (ML Kit GenAI on AICore; page updated 2026-11-10) [official 8]
- **APIs:** Direct model access (Beta, artifact genai-prompt), system instructions (Beta), structured output (Alpha), function calling (Preview), AgentRunner agents (Preview), prefix caching (Experimental), on-device speech recognition and TTS (Alpha).
- **Device tiers:**
  - Nano 4: Pixel 10/11, Galaxy S25/S26 and Z7/Z8, OnePlus 13/15, Honor, OPPO Find, vivo X, Xperia 1 VIII and others.
  - Nano 3: Pixel 9 series, OPPO Reno Pro, Googlebooks.
  - Nano 2: Xiaomi, POCO, realme.
  - The version a device gets depends on RAM, OS and AICore, and output differs by version (check with getBaseModelName()).
- **Limits:** a per-app quota (BUSY error), a long-duration battery quota, and foreground use only.
- **Reach:** flagship phones only, so mid-range Android needs a bundled model or a cloud fallback [inference].

#### Windows / PC
- **Windows ML:** a Windows-maintained ONNX Runtime with managed execution providers across NPU, GPU and CPU [official 13]. Generally available since Sep 2025 [official-snip 13a]. DirectML is in "sustained engineering", and new work goes to WinML [official 14].
- **NVIDIA In-Game Inferencing (NVIGI) 1.7.0, x64 and ARM64:**
  - Runs in-process from C++ and uses CUDA in Graphics to run inference alongside rendering.
  - Backends: TensorRT, ONNX Runtime, llama.cpp.
  - LLMs: Nemotron 3 Nano 4B, Nemotron 2 Nano 9B, Qwen3-0.6B, Qwen3.5-4B/8B. Speech: Riva ASR/TTS, Chatterbox TTS [official 9].
- **NVIDIA ACE:**
  - Game Agent SDK (Beta) with C/C++ Agent, Chat and RAG APIs.
  - UE 5.5-5.7 plugins under MIT: ASR, LLM with function calling, TTS, Audio2Face-3D.
  - Models: Nemotron ASR (25 languages), Qwen3 TTS, Nemotron 3.5 Bolt, Nemotron 3 Nano 4B/9B, described as running on "multi-vendor GPUs and CPUs" [official 10].

#### Small open-weight models
| Family | Latest small | Notes |
|---|---|---|
| Gemma 4 | E2B, E4B (Apr 2 2026) | Apache 2.0, 128K context, native audio input [official 16]; basis of Gemini Nano 4 [secondary 16a] |
| Qwen3.5 | 0.8B/2B/4B/9B (Mar 2026 [secondary 17a]) | Apache 2.0, 262K native context [official 17]; high hallucination rate on 4B/9B [secondary 17a] |
| Ministral 3 | 3B/8B/14B (Dec 2025) | Apache 2.0, base/instruct/reasoning [official-snip 18] |
| Nemotron 3 Nano | 4B/9B | Distributed through ACE [official 10] |
| Llama | nothing new | The small Llamas are still Llama 3.2 1B/3B; Meta's 2026 open model is Muse Glimmer, 30B dense [secondary 19] |
| Phi | Phi-4-mini (3.8B) | Newest Phi found: Phi-4-reasoning-vision-15B, Mar 2026 [secondary 20] |

Sizes that have actually shipped in games: 0.5B (inZOI) and a quantized 2B (PUBG Ally) [official 11,12].

#### Runtimes
- **llama.cpp:** rolling builds; b12606 on 2026-11-21 [official 21].
- **ExecuTorch:** v1.6.0 on 2026-11-12 (1.0 reached GA in Oct 2025) [official 22].
- **MLC LLM:** no 2026 release on its GitHub releases page [unverified].
- **Unity Sentis 2.6** (renamed from Inference Engine in 2.4): ONNX opset 25, a tokenizer, PyTorch and LiteRT import. No first-party LLM runtime [official 23].

### 2. Cloud
- **Latency:** Krafton found cloud network plus inference latency "too slow for live squad communication" and moved PUBG Ally on-device [official 11]. Vendors cite about 250-300 ms to first audio and about 1 s per voice turn [secondary 24].
- **Prices per 1M tokens:**
  - Gemini 3.1 Flash-Lite: $0.25 in, $1.50 out, cached input $0.025, cache storage $1 per 1M tokens per hour [official 25].
  - Gemini 3.5 Flash-Lite: $0.30 in, $2.50 out, cached $0.03 [official 25].
  - OpenAI gpt-realtime-2.1-mini: audio $10 in, $20 out (cached $0.30); text $0.60 in, $2.40 out [official 26].
- **Worked arithmetic [inference]:** a turn with a 2K-token cached persona prefix and 100 output tokens on Gemini 3.1 Flash-Lite costs about $0.0002 (about $0.00065 uncached). A 1-minute voiced line (about 1,000 characters) on Inworld TTS-2 Flash on-demand costs about $0.015. Blog figures of $0.001-$0.10 per conversation are [unverified].
- **Paying for per-call costs:** Steam's FAQ suggests building the cost into the price, or selling microtransactions, a subscription or an unlock DLC [official 27].
- **Middleware:**
  - **Inworld:** now a general voice and inference platform, though it still lists "Games and media" [official 28]. Prices:
    - TTS-2: $25/1M characters on-demand, down to about $5 at enterprise.
    - TTS-2 Flash: $15/1M characters.
    - STT: $0.15/hr.
    - LLM: from $0.07/1M tokens.
    - Plans: $0, $25, $100, $300 and $1,500 a month.
  - **Convai** [official 29], monthly interactions in brackets:
    - Free (100), Indie $29 (3,000), Professional $99 (10,000), Scale $499 (50,000).
    - Business $1,199 (125,000), or $499/mo billed yearly as a "limited time offer".
    - Enterprise is custom. Third-party listings showing $5/$15 tiers are out of date.
  - **Ubisoft:** NEO NPC became "Teammates" (Nov 2025), a playable research FPS with the voice AI Jaspar and two squad NPCs [official 30]. It had a closed playtest of a few hundred players, and its middleware runs on Snowdrop and Anvil [secondary 30a]. No 2026 release found [unverified].
  - **Roblox TextGenerator:** a runtime LLM for NPCs that needs no external API setup. It starts at 100 requests per minute and scales with concurrent users [official 31].
  - **Fortnite "Conversations"** (formerly the Persona device) [secondary 32]; Epic's official pages blocked the headless browser.
    - UEFN Experimental since v40.20 (Apr 16 2026), using Gemini Flash-Lite and ElevenLabs.
    - Rule 1.22 bans medical or mental-health personas, romantic companions and attempts to bypass safety systems.
    - Islands using it can't be published until the feature reaches Beta.

### 3. Shipped examples
| Title (date) | Tech | Outcome | Response |
|---|---|---|---|
| Fortnite AI Darth Vader (May 2025) | Cloud LLM + licensed voice clone | Players got profanity and slurs out of it within hours; SAG-AFTRA filed an unfair-labor-practice charge [secondary 33] | Same-day filter hotfix [secondary 33a] |
| inZOI Smart Zoi (early access Mar 28 2025) | 0.5B Mistral-NeMo-Minitron on-device, RTX GPUs only, experimental toggle [official 12] | No outcome data beyond press demo impressions [unverified] | Opt-in toggle |
| Whispers from the Star (Aug 15 2025) | Voice-driven LLM chat made with an actor | Steam Very Positive, 81% of 1,670 reviews [official 34] | |
| Where Winds Meet (Nov 14 2025) | Steam disclosure: "AI-driven NPC text and voice chat" [official 35] | Players talked NPCs into skipping quests, handing out rewards and sexual roleplay [secondary 36]. No developer fix statement found [unverified]. 86% positive across 65K English reviews [official 35] | |
| PUBG Ally (public beta Jun 17-30 2026) | Quantized Minitron-2B, needs 8 GB VRAM minimum; a behavior tree handles reflexes and the small model handles reasoning; distilled to one map and mode; 1,000+ testers [official 11] | No full-release date | Narrow domain, on-device |
| Total War: PHARAOH advisor | On-device small model connected to game data [official 10] | Status unclear | |
| Dead Meat | LLM interrogation game | Unreleased; Steam now says 2027 (earlier coverage said 2026) [official 37] | |

**Lessons [inference]:**
- Never let LLM judgment gate rewards: game state decides, and the LLM only narrates.
- Moderate text before it reaches TTS, and keep a server-side kill switch.
- Validate structured outputs and tool calls, and cap output tokens.
- Write in-character refusal lines.
- Settle voice-actor consent and union terms first.

### 4. Policy
| Body | Rule |
|---|---|
| Steam | The Content Survey splits AI content into Pre-Generated and Live-Generated. Live-Generated games must describe their guardrails against illegal content [official 27]. The disclosure appears on the store page, and players can report illegal live output through the in-game overlay (since Jan 10 2024) [official 38]. Live-generated Adult Only sexual content is not allowed [official 27]. The Jan 2026 rewrite says disclosure covers what players consume, not development efficiency tools [secondary 39] |
| Apple | **1.2** covers "AI content creation apps": they need filtering, a report mechanism with timely responses, user blocking and published contact details. Random or anonymous chat apps may be removed. **4.7:** chatbots not embedded in the binary are still your responsibility. **5.1.2(i):** disclose personal data sent to third-party AI and get explicit permission. **1.3 Kids:** no personal or device information to third parties and no third-party analytics [official 40], which in practice rules out a third-party LLM on kids' input [inference]. **Age ratings:** new descriptors arrive in App Store Connect on Nov 16 2026 and must be answered by Jan 12 2027. "Dating and Relationships" covers a companion in romantic or sexual exchanges "whether scripted or generated", with a minimum rating of 18+ [official 41,42]. AI assistants and chatbots count toward how often sensitive content appears [official-snip 43] |
| Google Play | Apps must offer in-app reporting or flagging that works without leaving the app, and must prevent restricted content. The policy's scope names text-to-text chatbots that are "central" to the app [official 44,45]. Aug 2026: reinforced rules on non-consensual intimate imagery (NCII) and adversarial testing [official-snip 46] |
| ESRB | "Users Interact" means "possible exposure to unfiltered/uncensored user-generated content, including user-to-user communications". The ratings guide has no AI-specific element [official 47] |
| IARC | The globalratings.com homepage and two searches turned up nothing AI-specific [unverified] |
| PEGI | Descriptors now include Unrestricted communication, Safe Online Gameplay, Pressure to play, Time-limited offers, Paid random items and Cryptocurrency [official 48]. From June 2026, fully unrestricted player communication (no blocking or reporting) means PEGI 18, and paid random items default to PEGI 16 [secondary 49]. AI chat is not addressed [unverified] |
| EU AI Act Art. 50 | Applies from Aug 2 2026. Systems that talk directly with people (chatbots, agents, avatars) must tell users from the start of the first interaction, unless that is obvious to a reasonably well-informed person [official 50]. Systems already on the market have until Dec 2 2026 to add machine-readable marking of AI output [secondary 51]. Fines go up to EUR 15M or 3% of turnover [secondary 51]. The FAQ and the guidelines landing page give no game or NPC example; I did not read the full guidelines [unverified] |
| US | **COPPA:** amended rule, compliance date Apr 22 2026 [official-snip 52]. **FTC:** 6(b) study of companion chatbots launched Sep 2025; no report found [official-snip 53]. **California SB 243** (from Jan 1 2026): duties for companion chatbots and private lawsuits at $1,000 per violation. Game bots are exempt only if their replies stay on the game and they can't discuss mental health, self-harm or sexual content or hold off-topic conversations [secondary 54] |

### Conflicts
1. **PUBG Ally:** public beta in June 2026 [11] vs "PUBG to follow" in Gamescom 2026 coverage [secondary].
2. **Fortnite Conversations model:** Gemini 1.5 Flash-Lite (TweakTown) vs 3.1 Flash-Lite (Wccftech) [32].
3. **Apple 1.2 wording:** the Oct 16 2026 news post says apps must "proactively prevent and remove" NCII [41], but the live guideline text has no "proactively" [40].
4. **Apple and Gemini:** "next-gen Apple Foundation Models built with Google/Gemini" appears only in press (fonearena.com/blog/484623); Apple's pages don't say so [6].
5. **EU marking grace period:** Dec 2 2026 (final Omnibus, per CMS [51]) vs Feb 2027 (Nov 2025 proposal).
6. **SAG-AFTRA Vader charge:** one gaming site reported it was withdrawn; never confirmed [unverified].

### Sources
1 developer.apple.com/documentation/updates/foundationmodels · 2 developer.apple.com/documentation/technotes/tn3193-managing-the-on-device-foundation-model-s-context-window · 3 developer.apple.com/videos/play/wwdc2026/241/ · 4 machinelearning.apple.com/research/apple-foundation-models-2025-updates · 5 developer.apple.com/documentation/foundationmodels/improving-the-safety-of-generative-model-output · 6 developer.apple.com/apple-intelligence/ · 7 support.apple.com/en-us/121115 · 8 developers.google.com/ml-kit/genai · 9 developer.nvidia.com/rtx/in-game-inferencing · 10 developer.nvidia.com/ace-for-games · 11 developer.nvidia.com/blog/how-krafton-built-pubg-ally-a-co-playable-character-powered-by-nvidia-ace/ (Jun 25 2026) · 12 nvidia.com/en-gb/geforce/news/nvidia-ace-naraka-bladepoint-inzoi-launch-this-month/ · 13 learn.microsoft.com/en-us/windows/ai/new-windows-ml/overview · 13a blogs.windows.com/windowsdeveloper/2025/09/23/windows-ml-is-generally-available · 14 onnxruntime.ai/docs/execution-providers/DirectML-ExecutionProvider.html · 16 blog.google/innovation-and-ai/technology/developers-tools/gemma-4/ · 16a thenextweb.com/news/google-gemma-4-open-models-apache-2-launch · 17 huggingface.co/Qwen/Qwen3.5-4B · 17a artificialanalysis.ai/articles/qwen3-5-small-models · 18 docs.mistral.ai/models/ministral-3-8b-25-12 · 19 artificialanalysis.ai/articles/muse-glimmer · 20 en.wikipedia.org/wiki/Phi_(language_model) · 21 github.com/ggml-org/llama.cpp/releases · 22 github.com/pytorch/executorch/releases · 23 docs.unity3d.com/Packages/com.unity.ai.inference@2.6/manual/whats-new.html · 24 deepgram.com/blog/low-latency-voice-ai · 25 aistudio.google.com/docs/pricing · 26 developers.openai.com/api/docs/pricing · 27 partner.steamgames.com/doc/gettingstarted/contentsurvey · 28 inworld.ai/pricing · 29 convai.com/pricing · 30 news.ubisoft.com/en-us/article/3mWlITIuWuu0MoVuR6o8ps (Nov 21 2025) · 30a engadget.com/gaming/ubisoft-made-a-prototype-game-with-voice-controlled-ai-teammates-200834163.html · 31 create.roblox.com/docs/characters/generate-text · 32 wccftech.com/fortnite-uefn-ai-npc-conversations-gemini-elevenlabs/ ; tweaktown.com/news/111153/ · 33 pcgamer.com/games/battle-royale/sag-aftra-files-unfair-labor-practice-complaint-against-epic-over-fortnites-ai-powered-darth-vader-we-must-protect-our-right-to-bargain-terms-and-conditions-around-uses-of-voice-that-replace-the-work-of-our-members · 33a insider-gaming.com/ai-darth-vader-fortnite-slurs-epic-patching-fix/ · 34 store.steampowered.com/app/3730100/ · 35 store.steampowered.com/app/3564740/ · 36 kotaku.com/where-winds-meet-ai-npc-llm-chatgpt-steam-2000650074 ; pcgamer.com/games/rpg/wuxia-mmo-where-winds-meet-is-full-of-ai-chatbot-npcs-and-people-are-doing-all-the-standard-obscene-stuff-to-them-i-made-him-think-that-my-character-was-pregnant-with-his-child · 37 store.steampowered.com/app/2628740/ · 38 store.steampowered.com/news/group/4145017/view/3862463747997849618 (Jan 10 2024) · 39 gamingonlinux.com/2026/01/valve-tweak-steam-ai-disclosure-form-for-developers-to-clarify-its-for-content-consumed-by-players · 40 developer.apple.com/app-store/review/guidelines/ · 41 developer.apple.com/news/ (Nov 2 and Oct 16 2026 items) · 42 developer.apple.com/help/app-store-connect/reference/app-information/age-ratings-values-and-definitions · 43 developer.apple.com/news/?id=ks775ehf (Jul 2025) · 44 support.google.com/googleplay/android-developer/answer/13985936 · 45 support.google.com/googleplay/android-developer/answer/14094294 · 46 android-developers.googleblog.com/2026/08/ensuring-safety-genai-preventing-non-consensual-intimate-content.html · 47 esrb.org/ratings-guide/ · 48 pegi.info/page/pegi-age-ratings · 49 rpclegal.com/snapshots/consumer/summer-2026/pegi-updates-age-ratings-and-interactive-risk-criteria-for-video-games/ · 50 digital-strategy.ec.europa.eu/en/faqs/transparency-obligations-under-article-50-ai-act · 51 cms.law/en/bel/legal-updates/eu-ai-act-developments-key-political-agreement-on-the-digital-omnibus-on-ai-implementation-timeline-and-transparency-consultation · 52 federalregister.gov/documents/2025/04/22/2025-05904/childrens-online-privacy-protection-rule · 53 ftc.gov/news-events/news/press-releases/2025/09/ftc-launches-inquiry-ai-chatbots-acting-companions · 54 skadden.com/insights/publications/2025/10/new-california-companion-chatbot-law
