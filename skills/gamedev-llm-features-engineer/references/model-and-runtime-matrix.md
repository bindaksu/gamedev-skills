# Model and Runtime Matrix for In-Game LLM Features

As of 2026-11; verify. Every price, ID, version and device list here changes; re-check the source before quoting a number in a cost sheet or a store form. Read this file when choosing a model or runtime, filling the Cost and Latency Sheet, checking which devices can run an on-device model, or explaining a failure with a shipped precedent.

Tags: [official] official page read 2026-11-21; [official-snip] official URL seen only in a search snippet; [secondary] press or law firm; [unverified] weak or no source; [inference] this pack's reading. Numbers in brackets point to the source list at the end.

## 1. Cloud text models (as of 2026-11; verify)

Use full IDs in production. Aliases and provider defaults move.

### Anthropic [official S1, S2]

| Model | API ID | Context / max output | $ per 1M tokens in / out | Cache hit | Default effort |
| --- | --- | --- | --- | --- | --- |
| Haiku 5.5 | `claude-haiku-5-5` | 1M / 128K | 0.10 / 0.50 for prompts up to 100K tokens; 0.50 / 2.50 above | 0.01 (0.05 above 100K) | medium |
| Sonnet 5.5 | `claude-sonnet-5-5` | 1M / 128K | 2 / 10 | 0.10 | high |
| Opus 5.5 | `claude-opus-5-5` | 1M / 128K | 4 / 20 | 0.20 | medium |
| Fable 5.2 | `claude-fable-5-2` | 1M / 128K | 8 / 40 | 0.20 | high |

- Haiku 5.5 launched 2026-10-07 [secondary S30]; prices and IDs are from the official pages.
- Adaptive thinking is always on for Fable 5.2 and Opus 5.5 [official S1]. For latency-critical turns, start from Haiku or Sonnet and tune effort before switching models, as Anthropic advises [official S3, S4].
- Fast mode: up to 2.5x output speed at 2x price, on Fable 5.2 and Opus 5.5 only [official S2, S4].
- Claude 4.7 and later use a tokenizer that yields about 30% more tokens for the same text [official S2]. Re-count prompts when migrating from older models.
- Bedrock IDs differ (for example `anthropic.claude-opus-5-5`) [official S1].
- Legacy still listed: Haiku 4.5 at $1 / $5 with 200K context; Sonnet 5 at $2 / $10 [official S1, S2]. Secondary sites say Sonnet 5 costs $3 / $15; the official pricing page wins (conflict 8).
- Cache-write premiums, cache lifetimes and minimum cacheable prefix sizes were not captured in the research; read them from S2 before finalising a cost sheet.

### OpenAI [official S14]

Standard rates for prompts up to 272K tokens; above 272K the higher rate applies to the whole request.

| ID | Vendor role | $ per 1M in / cached / out | Above 272K in / out |
| --- | --- | --- | --- |
| `gpt-6-luna` | Focused, high-volume, repeatable tasks | 0.10 / 0.01 / 0.50 | 0.20 / 0.75 |
| `gpt-6.1-terra` | Fast; writing, visual work, computer use | 1 / 0.05 / 5 | 2 / 7.50 |
| `gpt-6.2-sol` | Everyday work | 2 / 0.10 / 10 | 4 / 15 |
| `gpt-6.2-astra` | Hardest end-to-end work | 8 / 0.40 / 40 | 16 / 60 |
| `gpt-6-astra` | Earlier flagship | 10 / 1 / 50 | 20 / 75 |

- Realtime speech: `gpt-realtime-2.1-mini` costs $10 in / $20 out per 1M audio tokens (cached $0.30) and $0.60 / $2.40 for text [official 26].
- Rate modifiers [official S14]: Batch at 50% of standard; Fast mode at 2x; eligible background requests 30% cheaper with a 2-hour window and 40% cheaper with an 8-hour window. Batch and background suit offline generation, never live turns [inference].
- The research captured context sizes only as Codex defaults, which are not API limits. Check each model page for the API context window.

### Google Gemini API [official S23, S24, 25]

The models with IDs in this table have a 1M-token context [official S23]; the research did not capture Gemini 3.1 Flash-Lite's context size.

| Model | $ per 1M in / out | Cached input | Notes |
| --- | --- | --- | --- |
| Gemini 3.1 Flash-Lite | 0.25 / 1.50 | 0.025; storage $1 per 1M tokens per hour | ID not captured in the research; check the models page |
| `gemini-3.5-flash-lite` | 0.30 / 2.50 | 0.03 | Google suggests it for high-throughput routing work |
| `gemini-3.8-flash` | 0.75 / 3.75 until 2026-12-31, then 1.50 / 7.50 | - | Price doubles on Jan 1 |
| `gemini-4-hydrogen` | 1.50 / 7.50 | - | Google's recommended default for coding and agent work |
| `gemini-4-carbon` | 2 / 10 until 2026-11-30, then 4 / 20 from Dec 1 | - | Strongest reasoning |
| `gemini-4-neon` | 3 / 15 | - | Frontier reasoning |
| `gemini-4-argon` | Carbon's prices on the pricing page | - | Missing from the latest-models overview (conflict 7) |

Cache storage is billed per hour per cached prefix, so cost scales with the number of distinct personas kept warm, not with traffic [inference].

### Routing for in-game roles [inference]

| Role | Default tier | Escalate to | Reason |
| --- | --- | --- | --- |
| Barks, small talk, short NPC lines | Haiku 5.5 / gpt-6-luna / Gemini Flash-Lite class | - | Price and first-token latency dominate |
| Companion conversation with memory | Haiku 5.5 / gpt-6.1-terra / gemini-3.8-flash | Sonnet 5.5 / gpt-6.2-sol / gemini-4-hydrogen | Escalate only after evals fail |
| Strategy advisor reasoning over game data | Sonnet 5.5 / gpt-6.2-sol / gemini-4-hydrogen | Opus 5.5 / gpt-6.2-astra / gemini-4-carbon | Advice quality, tolerant of 2-5 s |
| Speech-to-speech voice partner | gpt-realtime-2.1-mini, or STT + text model + TTS | - | Cascade gives sentence-level moderation before audio |
| Second-opinion output classifier | Cheapest tier with a fixed rubric | - | Runs on every sentence; must be cheap |
| Pre-generated variants and quest text | Top tier via Batch | - | Shipped content; review via `gamedev-ai-asset-pipeline` |

A speech-to-speech model produces audio directly, so text moderation cannot sit between the model and the speaker; budget an audio-output classifier or use the cascade for anything player-facing [inference].

## 2. Voice: TTS, STT and voice platforms (as of 2026-11; verify)

| Vendor | Product | Price | Notes |
| --- | --- | --- | --- |
| Inworld [official 28] | TTS-2 | $25 per 1M characters on-demand, about $5 at enterprise | Now a general voice and inference platform; still lists games and media |
| Inworld | TTS-2 Flash | $15 per 1M characters | A 1-minute line (about 1,000 characters) costs about $0.015 [inference from price] |
| Inworld | STT | $0.15 per hour | |
| Inworld | LLM | from $0.07 per 1M tokens | Plans $0, $25, $100, $300, $1,500 a month |
| ElevenLabs [official E1, E2] | `eleven_v4` | $0.08 per 1K characters | 90+ languages; 100K-character limit; launched 2026-09-28 [secondary] |
| ElevenLabs | `eleven_v4_turbo` | $0.04 per 1K characters | About 100 ms latency |
| ElevenLabs | `eleven_flash_v2_5` | $0.04 per 1K characters | Listed in the models overview; the notes advise flash over deprecated turbo models |
| ElevenLabs | `eleven_v3_conversational`, `eleven_multilingual_v2` | $0.08 (multilingual) | Voice design uses `eleven_ttv_v3` |

- The research notes list `eleven_v4_turbo` and also say "the turbo models are deprecated; use flash instead" (conflict 9). Confirm which turbo IDs are deprecated before building on one.
- Vendors cite about 250-300 ms to first audio and about 1 s per voice turn [secondary 24].
- Per-character TTS dwarfs per-token LLM cost: by these prices one voiced minute costs about 75 text turns on a Flash-Lite model [inference].

## 3. Middleware and platform NPC features (as of 2026-11; verify)

| Offer | What it is | Price or limit | Source |
| --- | --- | --- | --- |
| Convai | NPC conversation middleware | Free (100 interactions/month), Indie $29 (3,000), Professional $99 (10,000), Scale $499 (50,000), Business $1,199 (125,000) or $499/month billed yearly as a "limited time offer", Enterprise custom. Third-party listings of $5/$15 tiers are out of date | [official 29] |
| Roblox TextGenerator | Runtime LLM for NPCs, no external API setup | Starts at 100 requests per minute, scales with concurrent users | [official 31] |
| Fortnite "Conversations" (formerly the Persona device) | UEFN Experimental since v40.20 (Apr 16 2026), Gemini Flash-Lite plus ElevenLabs | Islands using it cannot be published until the feature reaches Beta; rule 1.22 bans medical or mental-health personas, romantic companions and attempts to bypass safety | [secondary 32]; Epic's pages blocked the headless browser; model version disputed (conflict 2) |
| Ubisoft "Teammates" | NEO NPC research became a playable FPS prototype (Nov 2025) with a voice AI and two squad NPCs | Closed playtest of a few hundred players; middleware runs on Snowdrop and Anvil; no 2026 release found | [official 30], [secondary 30a] |

Middleware saves the voice and memory plumbing but not the authority contract, evals or disclosure work; those stay with the studio [inference].

## 4. On-device

### Apple Foundation Models framework [official 1-7]

| Item | Fact |
| --- | --- |
| Model | About 3B parameters [official 4]. Replaced in iOS 26.4 (better instruction following and tool calling, fewer false-positive guardrail blocks) and again in iOS 27 ("rebuilt from the ground up", accepts images). Apple says to retest prompts after every model change [official 1, 3] |
| Context | 4,096 tokens per session, shared by instructions, prompts, tool schemas, tool input and output, @Generable schemas and the output. Exceeding it throws. iOS 26.4 added `contextSize` and `tokenCount(for:)` [official 1, 2] |
| APIs | Guided generation (@Generable), Tool protocol. iOS 27 adds ToolCallingMode, DynamicProfile and the LanguageModel protocol (Anthropic and Google Swift packages, CoreAILanguageModel, MLXLanguageModel), an Evaluations framework, the fm CLI and a Python SDK (Mar 2026); the framework core is going open source [official 1, 3] |
| Server tier | PrivateCloudComputeLanguageModel: 32K context, reasoning levels [official 3]. No cloud API cost for Small Business Program members under 2M first-time downloads [official 6]; terms for others not found [unverified] |
| Guardrails | Check input and output; set with SystemLanguageModel.Guardrails; `permissiveContentTransformations` is only for transforming text. Private Cloud Compute guardrails cannot be configured. Errors: guardrailViolation and refusal; a refusal can also come back as plain text [official 5]. Violent fiction may trip guardrails [inference] |
| Devices (iOS 27) | iPhone 15 Pro/Pro Max, iPhone 16 or later, Air, Duo; iPad mini A17 Pro/A20 Pro; iPad and Mac with M1 or later; MacBook Neo; Vision Pro; Apple Watch S9+/Ultra 2+/SE 3 (paired). Needs up to 14 GB of storage; device and Siri language must match [official 7]. Check availability at runtime |
| Terms | DPLA 3.3.8(I) sets requirements for using the framework [official 41] |

Conflict 4: press claims next-generation Apple models are built with Google Gemini; Apple's pages do not say so.

### Android: Gemini Nano via ML Kit GenAI on AICore (page updated 2026-11-10) [official 8]

| Item | Fact |
| --- | --- |
| API status | Direct model access Beta (artifact genai-prompt); system instructions Beta; structured output Alpha; function calling Preview; AgentRunner agents Preview; prefix caching Experimental; on-device speech recognition and TTS Alpha |
| Nano 4 devices | Pixel 10/11, Galaxy S25/S26 and Z7/Z8, OnePlus 13/15, Honor, OPPO Find, vivo X, Xperia 1 VIII and others |
| Nano 3 devices | Pixel 9 series, OPPO Reno Pro, Googlebooks |
| Nano 2 devices | Xiaomi, POCO, realme |
| Version | Depends on RAM, OS and AICore; output differs by version; read it with `getBaseModelName()` |
| Limits | Per-app quota (BUSY error), long-duration battery quota, foreground use only |

Flagships only: mid-range Android needs a bundled model or a cloud path [inference]. Structured output at Alpha means validating everything yourself [inference].

### Windows and PC

- **Windows ML:** a Windows-maintained ONNX Runtime with managed execution providers across NPU, GPU and CPU [official 13]; generally available since Sep 2025 [official-snip 13a]. DirectML is in "sustained engineering"; new work goes to Windows ML [official 14].
- **NVIDIA In-Game Inferencing (NVIGI) 1.7.0, x64 and ARM64** [official 9]: in-process from C++; uses CUDA in Graphics to run inference alongside rendering; backends TensorRT, ONNX Runtime, llama.cpp; LLMs Nemotron 3 Nano 4B, Nemotron 2 Nano 9B, Qwen3-0.6B, Qwen3.5-4B/8B; speech Riva ASR/TTS and Chatterbox TTS.
- **NVIDIA ACE** [official 10]: Game Agent SDK (Beta) with C/C++ Agent, Chat and RAG APIs; Unreal Engine 5.5-5.7 plugins under MIT (ASR, LLM with function calling, TTS, Audio2Face-3D); models Nemotron ASR (25 languages), Qwen3 TTS, Nemotron 3.5 Bolt, Nemotron 3 Nano 4B/9B, described as running on "multi-vendor GPUs and CPUs".
- Inference shares the GPU with the frame: budget VRAM and frame time for it with `gamedev-optimization-compatibility` [inference].

### Small open-weight models

| Family | Latest small | Notes |
| --- | --- | --- |
| Gemma 4 | E2B, E4B (Apr 2 2026) | Apache 2.0, 128K context, native audio input [official 16]; basis of Gemini Nano 4 [secondary 16a] |
| Qwen3.5 | 0.8B / 2B / 4B / 9B (Mar 2026) [secondary 17a] | Apache 2.0, 262K native context [official 17]; high hallucination rate on 4B/9B [secondary 17a] |
| Ministral 3 | 3B / 8B / 14B (Dec 2025) | Apache 2.0; base, instruct and reasoning [official-snip 18] |
| Nemotron 3 Nano | 4B / 9B | Distributed through ACE [official 10] |
| Llama | Nothing new small | Still Llama 3.2 1B/3B; Meta's 2026 open model is a 30B dense model [secondary 19] |
| Phi | Phi-4-mini (3.8B) | Newest Phi found is a 15B reasoning-vision model, Mar 2026 [secondary 20] |

Sizes that shipped in games: 0.5B (inZOI) and a quantized 2B (PUBG Ally, 8 GB VRAM minimum) [official 11, 12]. Check each license for redistribution inside a game binary before bundling [inference].

### Runtimes

| Runtime | Version | Notes |
| --- | --- | --- |
| llama.cpp | Rolling builds; b12606 on 2026-11-21 | [official 21] Pin a build per release |
| ExecuTorch | v1.6.0 on 2026-11-12 (1.0 GA Oct 2025) | [official 22] |
| MLC LLM | No 2026 release on its GitHub releases page | [unverified] Treat as unmaintained until shown otherwise |
| Unity Sentis 2.6 (renamed from Inference Engine in 2.4) | ONNX opset 25, a tokenizer, PyTorch and LiteRT import | No first-party LLM runtime [official 23] |

## 5. Shipped examples and what went wrong

| Title (date) | Tech | Outcome | Response |
| --- | --- | --- | --- |
| Fortnite AI Darth Vader (May 2025) | Cloud LLM plus a licensed voice clone | Players drew profanity and slurs out of it within hours; SAG-AFTRA filed an unfair-labor-practice charge [secondary 33] | Same-day filter hotfix [secondary 33a] |
| inZOI Smart Zoi (early access Mar 28 2025) | 0.5B Mistral-NeMo-Minitron on-device, RTX GPUs only, experimental toggle [official 12] | No outcome data beyond demo impressions [unverified] | Opt-in toggle |
| Whispers from the Star (Aug 15 2025) | Voice-driven LLM chat built with an actor | Steam Very Positive, 81% of 1,670 reviews [official 34] | |
| Where Winds Meet (Nov 14 2025) | Steam disclosure: "AI-driven NPC text and voice chat" [official 35] | Players talked NPCs into skipping quests, handing out rewards and sexual roleplay [secondary 36]; 86% positive across 65K English reviews [official 35] | No developer fix statement found [unverified] |
| PUBG Ally (public beta Jun 17-30 2026) | Quantized Minitron-2B, 8 GB VRAM minimum; a behavior tree handles reflexes, the small model handles reasoning; distilled to one map and mode; 1,000+ testers [official 11] | No full-release date (conflict 1) | Narrow domain, on-device |
| Total War: PHARAOH advisor | On-device small model connected to game data [official 10] | Status unclear | |
| Dead Meat | LLM interrogation game | Unreleased; Steam now says 2027 [official 37] | |

Lessons [inference]: never let model judgment gate rewards; moderate before TTS and keep a server kill switch; validate structured output and tool calls and cap output tokens; write in-character refusals; settle voice-actor consent and union terms first; narrow the domain (one map, one role) before widening it.

## 6. Conflicts to keep flagged

1. PUBG Ally: public beta in June 2026 [11] versus "PUBG to follow" in Gamescom 2026 coverage (cowcotland.com).
2. Fortnite Conversations model: Gemini 1.5 Flash-Lite (TweakTown) versus 3.1 Flash-Lite (Wccftech) [32].
3. Apple guideline 1.2 wording: the Oct 16 2026 news post says apps must "proactively prevent and remove" NCII [41]; the live guideline text has no "proactively" [40].
4. Apple and Gemini: "next-gen Apple Foundation Models built with Google/Gemini" appears only in press (fonearena.com); Apple's pages do not say so [6].
5. EU marking grace period: Dec 2 2026 versus Feb 2027 (details in policy-and-ratings.md).
6. SAG-AFTRA Vader charge: one gaming site reported it withdrawn; never confirmed [unverified].
7. Gemini 4 Argon: priced on the pricing page and offered by third-party tools, but missing from Google's latest-models overview; public availability disputed.
8. Sonnet 5 price: $2 / $10 officially versus $3 / $15 on secondary sites.
9. ElevenLabs turbo: `eleven_v4_turbo` is listed while "turbo models are deprecated" also appears.

## 7. Sources

- S1 https://platform.claude.com/docs/en/about-claude/models/overview
- S2 https://platform.claude.com/docs/en/about-claude/pricing
- S3 https://platform.claude.com/docs/en/about-claude/models/choosing-a-model
- S4 https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence
- S14 https://developers.openai.com/api/docs/pricing.md
- S23 https://ai.google.dev/gemini-api/docs/latest-model (redirects to aistudio.google.com/docs/latest-model)
- S24 https://aistudio.google.com/docs/pricing
- S30 https://9to5mac.com/2026/10/07/anthropic-upgrades-claude-with-new-haiku-5-5-model-details-here/ (secondary)
- E1 https://elevenlabs.io/docs/overview/models
- E2 https://elevenlabs.io/pricing/api
- 1 https://developer.apple.com/documentation/updates/foundationmodels
- 2 https://developer.apple.com/documentation/technotes/tn3193-managing-the-on-device-foundation-model-s-context-window
- 3 https://developer.apple.com/videos/play/wwdc2026/241/
- 4 https://machinelearning.apple.com/research/apple-foundation-models-2025-updates
- 5 https://developer.apple.com/documentation/foundationmodels/improving-the-safety-of-generative-model-output
- 6 https://developer.apple.com/apple-intelligence/
- 7 https://support.apple.com/en-us/121115
- 8 https://developers.google.com/ml-kit/genai
- 9 https://developer.nvidia.com/rtx/in-game-inferencing
- 10 https://developer.nvidia.com/ace-for-games
- 11 https://developer.nvidia.com/blog/how-krafton-built-pubg-ally-a-co-playable-character-powered-by-nvidia-ace/ (Jun 25 2026)
- 12 https://nvidia.com/en-gb/geforce/news/nvidia-ace-naraka-bladepoint-inzoi-launch-this-month/
- 13 https://learn.microsoft.com/en-us/windows/ai/new-windows-ml/overview
- 13a https://blogs.windows.com/windowsdeveloper/2025/09/23/windows-ml-is-generally-available
- 14 https://onnxruntime.ai/docs/execution-providers/DirectML-ExecutionProvider.html
- 16 https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/
- 16a https://thenextweb.com/news/google-gemma-4-open-models-apache-2-launch
- 17 https://huggingface.co/Qwen/Qwen3.5-4B
- 17a https://artificialanalysis.ai/articles/qwen3-5-small-models
- 18 https://docs.mistral.ai/models/ministral-3-8b-25-12
- 19 https://artificialanalysis.ai/articles/muse-glimmer
- 20 https://en.wikipedia.org/wiki/Phi_(language_model)
- 21 https://github.com/ggml-org/llama.cpp/releases
- 22 https://github.com/pytorch/executorch/releases
- 23 https://docs.unity3d.com/Packages/com.unity.ai.inference@2.6/manual/whats-new.html
- 24 https://deepgram.com/blog/low-latency-voice-ai
- 25 https://aistudio.google.com/docs/pricing
- 26 https://developers.openai.com/api/docs/pricing
- 28 https://inworld.ai/pricing
- 29 https://convai.com/pricing
- 30 https://news.ubisoft.com/en-us/article/3mWlITIuWuu0MoVuR6o8ps (Nov 21 2025)
- 30a https://engadget.com/gaming/ubisoft-made-a-prototype-game-with-voice-controlled-ai-teammates-200834163.html
- 31 https://create.roblox.com/docs/characters/generate-text
- 32 https://wccftech.com/fortnite-uefn-ai-npc-conversations-gemini-elevenlabs/ ; https://tweaktown.com/news/111153/
- 33 https://pcgamer.com/games/battle-royale/sag-aftra-files-unfair-labor-practice-complaint-against-epic-over-fortnites-ai-powered-darth-vader-we-must-protect-our-right-to-bargain-terms-and-conditions-around-uses-of-voice-that-replace-the-work-of-our-members
- 33a https://insider-gaming.com/ai-darth-vader-fortnite-slurs-epic-patching-fix/
- 34 https://store.steampowered.com/app/3730100/
- 35 https://store.steampowered.com/app/3564740/
- 36 https://kotaku.com/where-winds-meet-ai-npc-llm-chatgpt-steam-2000650074
- 37 https://store.steampowered.com/app/2628740/
- 40 https://developer.apple.com/app-store/review/guidelines/
- 41 https://developer.apple.com/news/ (Nov 2 and Oct 16 2026 items)
