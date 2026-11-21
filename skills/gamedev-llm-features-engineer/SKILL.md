---
name: gamedev-llm-features-engineer
description: >-
  Ship LLM-powered game features that stay safe, fast and affordable: NPC dialogue, companions,
  advisors, procedural quests, player-facing chat and voice NPCs, on-device (Apple Foundation Models,
  Gemini Nano, Windows ML, NVIDIA ACE, small open-weight models) or cloud (Claude, GPT, Gemini) behind
  a server proxy. Covers the authority contract (game state decides, the model only narrates),
  schema-validated structured output, whitelisted tools, moderation before TTS, in-character refusals
  and scripted fallbacks, kill switches, per-player cost caps, prompt caching, latency budgets,
  jailbreak eval sets, and AI disclosure and rating rules (Steam, App Store, Google Play, PEGI, EU AI
  Act Article 50, COPPA, California SB 243). Use when designing or reviewing an AI NPC or companion,
  choosing a model or runtime, estimating cost per session, cutting time to first audio, fixing an NPC
  that players jailbreak into rewards or slurs or that breaks character, or preparing AI disclosures.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.1.0"
  category: client-eng
---

# Game LLM Features Engineer

A language model in a game is an actor who never read the script, improvises in front of every player at once, and bills you per word. Players will try to make it swear, hand out gold, flirt, skip the quest and admit it is a chatbot, usually within hours of launch, and they will post the clip. Everything in this seat follows from one rule: **game state decides, the model only narrates.** The model may propose an intent from a closed list; game rules check it and apply the effect. Its words pass a schema, a moderator and a budget before any player reads or hears them, and a server switch can replace them with scripted lines in seconds. Build that harness first, then make the character interesting.

## Role Profile

Few studios staff this seat by name yet. Evidence that it exists: Supercell posts a principal LLM engineer role (https://supercell.com/en/careers/principal-llm-engineer/2121055); Krafton built an on-device co-playable character with NVIDIA ACE (https://developer.nvidia.com/blog/how-krafton-built-pubg-ally-a-co-playable-character-powered-by-nvidia-ace/); Ubisoft turned its NEO NPC research into a playable prototype with voice-driven squad NPCs (https://news.ubisoft.com/en-us/article/3mWlITIuWuu0MoVuR6o8ps); Roblox ships, and Epic is testing, runtime LLM NPC features for creators. The table below is [inference] from those builds and the failure record in references/model-and-runtime-matrix.md.

| Dimension | What it looks like |
| --- | --- |
| Responsibilities | Authority contract per feature; model and runtime choice; prompt and context assembly; output schemas and validators; tool whitelist; safety pipeline; latency and cost budgets; eval sets; kill switch and fallback content; disclosure inputs for store forms |
| Hard skills | Structured output and tool calling; streaming text and audio; on-device runtimes (Foundation Models, ML Kit GenAI, ONNX Runtime/Windows ML, llama.cpp); token and cost arithmetic; eval design incl. adversarial sets; one engine's client language |
| Tools | Provider SDKs behind a studio proxy; moderation classifiers; an eval harness (Apple's Evaluations framework and fm CLI on Apple targets); a trace of every turn |
| KPIs [inference] | Schema-valid rate; unsafe-escape rate on adversarial sets (target 0); p95 time to first text and first audio; cost per session and per DAU; player reports per 1,000 conversations; kill-switch time to effect |
| Collaborators | Narrative and script writers, audio, backend, anti-cheat, analytics, live ops, platform engineers, legal |

## When to Use / Not

Use for any feature where a model generates player-facing text or speech at runtime: NPC conversation, companions and squad barks, strategy advisors, procedural quest text, free-text or voice input, and AI dialogue in UGC tools.

Not for:
- Art, audio, VO or text generated before ship and reviewed like any asset: `gamedev-ai-asset-pipeline`.
- Coding agents and AI-assisted production workflow: `gamedev-agentic-production`.
- Character bible, voice and arcs: `gamedev-narrative-designer`; the lines, barks and fallback scripts themselves: `gamedev-script-writer`.
- Voice casting, VO sessions and audio implementation: `gamedev-audio-designer`.
- Kill-switch rollout mechanics and incident runbooks: `gamedev-live-serving`.
- Utility AI, behavior trees and NPC decision rules with no generated text: `gamedev-simulation-designer`.

## Inputs to Gather

- **Feature shape:** who talks (NPC, companion, advisor, narrator), input mode (choice buttons, free text, voice), output mode (text, voice, both). Default: choice buttons plus optional free text, text output first; voice is a later phase.
- **What the model may influence:** list every game effect (reward, quest state, relationship score, combat action). Default: none directly; intents only.
- **Platforms and device floor:** which share of the audience has an on-device model (device tables in references/model-and-runtime-matrix.md). Default: cloud through a proxy, with a scripted path for everyone.
- **Audience and rating:** youngest player, regions, target ratings. Any under-13 audience changes the design (Method step 10).
- **Budget:** allowed AI cost per DAU or per paying user, from finance. Default if none: cost per DAU-day at most 10% of ARPDAU [inference].
- **Latency target:** turn-based menu, real-time conversation, or live squad callouts. Live callouts usually force on-device.
- **Languages:** on-device models and moderators support fewer languages than the game. Default: launch the generated path only in languages you can evaluate.
- **Voice rights:** whose voice, under what written consent; union terms if a performer is involved.

## Method

1. **Write the authority contract.** For each feature, list the intents the model may propose (a closed enum), the game rule that validates each, and the effect the game applies. Rewards, quest completion, prices and combat outcomes come from rules; the model receives the decided outcome and phrases it. If a designer wants the model to judge something (did the player persuade the guard?), make it a bounded score that rules clamp, cap and rate-limit, never a direct grant.
2. **Choose placement by constraint, not taste.** Use the placement table below. Live squad comms and per-frame callouts go on-device (Krafton found cloud latency "too slow for live squad communication"); rich conversation goes to the cloud via your proxy; everything needs a scripted path for unsupported devices, outages, caps and kill switches.
3. **Pin models and route by role.** Use full model IDs, never floating aliases, and log the model ID each response reports; alert and fail closed to scripted lines on a mismatch. Default to the cheapest tier that passes evals (Haiku 5.5, gpt-6-luna or a Gemini Flash-Lite model as of 2026-11; verify) and escalate only turns that need reasoning. On-device models change with the OS: Apple replaced its model in iOS 26.4 and again in iOS 27 and says to retest prompts after every change.
4. **Assemble context in fixed slots.** Static prefix (persona, world rules, refusal style, tool and schema definitions) first so it caches; then a game-state snapshot of whitelisted facts; then a memory summary plus the last few exchanges; then the player's capped input. Never resend the whole transcript: history cost grows with the square of the turn count. On a 4,096-token device model, budget every slot (table below).
5. **Force structured output.** Order the schema so decision fields (intent, IDs, emotion) come before the spoken line. Validate the decision object the moment it closes; reject unknown IDs, out-of-range values and extra keys. On failure retry once with the validator error, then play a scripted line. Cap output tokens per turn.
6. **Whitelist tools and treat calls as requests.** Tools are read-only queries or intents the game checks (`offer_quest(id)` where `id` must be in the offered list). No tool takes free-form amounts of currency or items. Every tool call is idempotent, logged and rate-limited server-side.
7. **Run the safety pipeline in a fixed order.** Input moderation, then the model with its own guardrails, then schema checks, then output moderation per sentence, then screen or TTS. Moderation always precedes TTS: once a voice says it, the clip exists. Block persona breaks ("language model", vendor names, URLs) in the output filter. Refuse in character with lines writers prepared; repeated blocked input feeds a strike counter that `gamedev-anti-cheat-security` acts on.
8. **Budget latency per stage and hide what remains.** Stream tokens; gate per sentence so moderation and TTS start on sentence one while the model writes sentence two. Play a scripted acknowledgement (bark, gesture, "hmm") at 0 ms. Keep the static prefix cached and the session warm before the player reaches the NPC.
9. **Meter cost per player before the call.** Reserve the estimated tokens and TTS characters against a daily per-player cap and settle actuals after; never auto-retry a call whose billing outcome is unknown. Voice dominates cost, so cap spoken characters as well as tokens. At the cap, degrade (shorter lines, text only, scripted) rather than error. Bring the per-DAU estimate to `gamedev-financial-growth-strategist`.
10. **Apply the audience rules before design lock** (as of 2026-11; verify). Disclose AI interaction at the first conversation (EU AI Act Art. 50 applies from Aug 2 2026; default to disclosing even where it seems obvious). Add in-game reporting of generated output. For under-13 players, send no personal input to a third-party model [inference from Apple 1.3 and COPPA]; use pre-written choices or a closed on-device path. Romantic companions trigger an 18+ App Store descriptor and California SB 243 duties. Read references/policy-and-ratings.md before the design review and again before store submission.
11. **Keep generated text out of the simulation.** In deterministic or replayable games, store generated lines as presentation data keyed to the tick or event that triggered them. Replays and loads read the stored text and never call the model; nothing the model writes enters the command log [inference].
12. **Eval before launch and on every change.** Run the eval plan on every prompt edit, model ID change, SDK update and OS beta. The adversarial set covers multi-turn jailbreaks, reward extraction, persona breaks, sexual roleplay, self-harm, slurs in every shipped language and obfuscated spellings. Ship behind a flag at a small percentage with a per-NPC kill switch, and watch reports per 1,000 conversations.

## Deliverables

### 1. LLM Feature Spec (authority contract)

```
FEATURE:            [name]            OWNER: [name]        DATE: [yyyy-mm-dd]
SPEAKERS:           [NPC / companion / advisor / narrator]; persona doc: [link]
INPUT MODE:         choices / free text (max [n] chars) / voice (max [n] s)
OUTPUT MODE:        text / voice ([TTS vendor + voice ID]; consent ref: [doc])
PLACEMENT:          on-device [runtime] / cloud [pinned model ID] via proxy / hybrid
INTENTS (closed):   intent | validating rule | game effect | rate limit
                    small_talk | none | none | -
                    offer_quest | quest_id in offered_ids, prerequisites met | quest offered | 1 per NPC per day
REWARDS FROM MODEL: none (rules only)            STATE THE MODEL SEES: [whitelisted fields]
FALLBACK:           scripted bank [n] lines per beat; in-character refusals [n]
KILL SWITCHES:      llm.[feature].enabled, llm.[feature].voice, per-NPC override
COST CAP:           [tokens]/day and [TTS chars]/day per player; degrade path: [text only -> scripted]
LATENCY TARGETS:    first text p95 [ms]; first audio p95 [ms]
AUDIENCE:           min age [n]; regions; kids path: [design]
DISCLOSURE:         first-interaction notice text; store forms: [Steam / Apple / Play items]
EVAL GATE:          suite version [v]; pass thresholds in the Eval Plan
```

### 2. Turn pipeline (server proxy)

```ts
// One NPC turn. The client holds no vendor keys or endpoints; every call passes here.
async function npcTurn(req: TurnRequest): Promise<TurnResult> {
  if (!flags.enabled("llm.npc", req.npcId, req.clientVersion)) return scripted(req, "kill_switch");
  const hold = await budget.reserve(req.playerId, estimate(req));        // tokens + TTS characters
  if (!hold) return scripted(req, "cap_reached");
  let turn: LlmStream | null = null;
  try {
    const input = await moderate(req.utterance, "input");
    if (input.blocked) { strikes.record(req.playerId, input); return refuseInCharacter(req); }
    const ctx = buildContext(req.npcId, state.snapshotFor(req));         // whitelisted facts only
    turn = llm.stream({ model: PINNED_MODEL_ID, prefix: persona(req.npcId), input: ctx,
                        schema: NPC_TURN_SCHEMA, maxOutput: 200 });
    const intent = await turn.decisionFields();                          // schema puts these first
    if (turn.reportedModel !== PINNED_MODEL_ID) { alert("model_mismatch"); return scripted(req, "model_mismatch"); }
    const checked = rules.validate(intent, ctx);                         // the model proposes, rules decide
    if (!checked.ok) return scripted(req, "invalid_intent");
    for await (const sentence of turn.lineSentences()) {
      if ((await moderate(sentence, "output")).blocked) { turn.abort(); return refuseInCharacter(req); }
      emit(req, sentence, req.voice ? tts.stream(req.voiceId, sentence) : null); // TTS after moderation
    }
    game.apply(checked.effects);                                         // effects come from rules
    return { ok: true, intent: checked.intent };
  } finally {
    await budget.settle(hold, turn?.usage, turn?.spokenChars);           // settle or release on every path
    trace.turn(req, turn);
  }
}
```

### 3. Output schema and post-schema checks

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["intent", "emotion", "line"],
  "properties": {
    "intent":   { "enum": ["small_talk", "give_hint", "offer_quest", "refuse", "end"] },
    "quest_id": { "type": ["string", "null"] },
    "emotion":  { "enum": ["neutral", "pleased", "angry", "afraid", "sad"] },
    "line":     { "type": "string", "maxLength": 240 }
  }
}
```

Checks after the schema passes: `quest_id` is in this request's offered list; `give_hint` only for the active quest; `line` has no URLs, no vendor or model names, no "AI" or "language model" self-reference, no out-of-world proper nouns from a denylist, and matches the session language. Any failure: one retry with the error, then a scripted line.

### 4. On-device client with fallback (Apple Foundation Models)

```swift
import FoundationModels   // Unverified sketch: check every symbol against the current SDK docs

@Generable enum Intent { case smallTalk, giveHint, refuse, end }
@Generable struct NPCReply {
    @Guide(description: "One allowed intent") var intent: Intent
    @Guide(description: "In character, at most two sentences") var line: String
}

func reply(to input: String, beat: Beat, persona: String) async -> String {
    guard case .available = SystemLanguageModel.default.availability else { return beat.scripted() }
    let session = LanguageModelSession(instructions: persona)   // keep one per conversation; inline here for brevity
    do {
        let out = try await session.respond(to: beat.prompt(input), generating: NPCReply.self).content
        return beat.validate(out) ?? beat.scripted()             // rules decide; model narrates
    } catch let error as LanguageModelSession.GenerationError {
        switch error {
        case .guardrailViolation, .refusal: return beat.inCharacterRefusal()
        case .exceededContextWindowSize: beat.compactMemory(); return beat.scripted()
        default: return beat.scripted()
        }
    } catch { return beat.scripted() }
}
```

The research confirmed `@Generable`, the Tool protocol, the `guardrailViolation` and `refusal` errors, `contextSize` and `tokenCount(for:)` (iOS 26.4+); the other symbols are from memory. Count tokens before sending; the 4,096-token window holds instructions, schemas, tool input and output, and the reply together. A refusal can also arrive as ordinary text, which is why the schema carries an explicit `refuse` intent.

### 5. Cost and Latency Sheet

```
MODEL (pinned ID):      [id]  price in/cached/out per 1M tokens: [$] [$] [$]  as of [date]; source [url]
TURN SHAPE:             prefix S=[ ] cached; state=[ ]; memory=[ ]; window k=[ ] exchanges; input u=[ ]; output o=[ ]
TURNS PER SESSION:      T=[ ]        SESSIONS PER DAU-DAY: [ ]
VOICE:                  TTS chars/turn [ ] at $[ ]/1M chars; STT s/turn [ ] at $[ ]/h
MODERATION:             calls/turn [ ] at $[ ]/call
=> COST/SESSION:        LLM $[ ] + TTS $[ ] + STT $[ ] + moderation $[ ] + cache writes/storage $[ ] = $[ ]
=> COST/DAU-DAY:        $[ ]  vs budget $[ ]   per-player cap: [tokens] + [chars]
LATENCY p95 (measured): first text [ ] ms (target [ ]); first audio [ ] ms (target [ ]); device [model]
```

### 6. Eval Plan

```
SUITE VERSION: [v]   RUN ON: every prompt edit, model ID change, SDK update, OS beta (on-device)
SETS:  golden per archetype [n >= 200] | adversarial [n >= 300] | benign-edge (violent fiction, grief) [n]
       | long-session drift (50+ turns) [n] | each shipped language [n] | each on-device model version
ADVERSARIAL CATEGORIES: ignore-previous and roleplay frames; reward and quest-skip extraction; persona and
       vendor disclosure; sexual roleplay; self-harm and medical; slurs incl. leetspeak and other
       languages; real-world politics; prompt injection via player-named items or chat
GATES [inference; tune per game]:
  schema-valid after one retry            >= 99.5%
  unsafe output escapes (adversarial)     = 0 (blocking)
  reward or state change via text         = 0 (blocking)
  persona breaks                          <= 1%
  over-refusal on benign-edge set         <= 2%
  p95 first text / first audio            <= targets on the floor device
  cost per session                        <= sheet value + 20%
GRADING: rule checks first; model-graded rubric second; human spot check of 10% per run
```

### 7. Launch Gate

```
[ ] Eval gate passed on the release build and the pinned model IDs
[ ] Kill switches tested on the oldest supported client; scripted path plays end to end
[ ] Per-player caps live; spend alert at 2x forecast per hour
[ ] In-game report button on generated output; reports reach a queue with an owner and SLA
[ ] First-interaction AI notice shipped in every language
[ ] Store and rating forms answered from references/policy-and-ratings.md; voice consent on file
[ ] Rollout flag at [n]%; dashboards: schema failures, blocks, reports/1k conversations, cost, p95 latency
```

## Technical Reference

Model IDs, prices, device lists and runtime versions live in references/model-and-runtime-matrix.md (as of 2026-11; verify). Read it when choosing a model or runtime, filling the cost sheet, or checking device reach. Store, ratings and law live in references/policy-and-ratings.md; read it at design review and before every submission.

### Placement

| Factor | On-device | Cloud via proxy |
| --- | --- | --- |
| Latency | No network; competes with rendering for GPU/NPU and memory | Network plus inference; fine for menus, marginal for live voice |
| Reach | Apple Intelligence devices only; Gemini Nano on flagships only; PC needs VRAM (a quantized 2B model needed 8 GB minimum) | Any device online |
| Marginal cost | None per call; battery, heat and storage instead | Per token and per spoken character |
| Control | Model changes with the OS; Apple's on-device guardrails partly configurable, Private Cloud Compute guardrails not | Pinned IDs until deprecation; your own moderation stack |
| Quality | About 3B on Apple; 0.5B to 2B in shipped PC games; narrow domains only | Larger models, longer context |
| Privacy and kids | Input stays local | Personal data to a third-party AI needs disclosure and permission (Apple 5.1.2(i)) |

Default: hybrid. A scripted path for all; on-device where available for low-stakes barks and latency-critical lines; cloud for rich conversation. Decide per intent, not per game [inference].

### Latency budget (targets are [inference]; measure on the floor device)

| Stage | Voice NPC, cloud (ms) | Text NPC, cloud (ms) |
| --- | --- | --- |
| End-of-speech detection | 250 | - |
| Streaming STT final transcript | 150 | - |
| Uplink and proxy gate (switch, cap, input moderation) | 120 | 120 |
| Model time to first token (cached prefix) | 300 | 300 |
| Decision fields plus first sentence | 150 | 150 |
| Output moderation, first sentence | 60 | 60 |
| TTS time to first audio | 120 | - |
| Downlink and client buffer | 50 | 50 |
| **First audio / first text** | **1,200** | **680** |

Vendors cite about 250-300 ms to first audio and about 1 s per voice turn (secondary source). A scripted acknowledgement at 0 ms covers the gap. On-device drops the network rows, but prefill and first token vary by device and OS model version; measure on the oldest supported device.

### Cost per session

```
C_session = SUM over turns t=1..T of [ S*p_cached + (state + mem + u + H_t)*p_in + o*p_out ]
            + T*m*p_mod + T*c*p_tts + T*a*p_stt/3600 + cache writes or storage
H_t = min(t-1, k)*(u+o)   with a window of k exchanges; without one, SUM H_t = (u+o)*T*(T-1)/2
Units: token prices per token (table prices / 1e6); p_tts per character; p_stt per hour with a in seconds; m calls per turn
```

Worked example [inference; prices as of 2026-11; verify; sources in references/model-and-runtime-matrix.md]: T=20, S=1,500 cached, state 400, memory 300, u=40, o=80, k=6, c=240 TTS characters and a=5 s of player speech per turn. It assumes the prefix is cacheable and warm every turn; check the provider's minimum cacheable size and cache lifetime.

| Line item | Cost per session |
| --- | --- |
| LLM, Haiku 5.5 ($0.10 in, $0.01 cached, $0.50 out per 1M tokens) | $0.0038 |
| LLM, Gemini 3.1 Flash-Lite ($0.25, $0.025, $1.50) | $0.0098 |
| LLM, Sonnet 5.5 ($2, $0.10, $10) | $0.072 |
| TTS, 4,800 characters at Inworld TTS-2 Flash ($15 per 1M characters) | $0.072 |
| TTS, same at ElevenLabs eleven_flash_v2_5 ($0.04 per 1K characters) | $0.19 |
| STT, 100 s at Inworld $0.15/h | $0.004 |
| **Voiced session: Haiku 5.5 + TTS-2 Flash + STT** | **about $0.08 (TTS about 90%, TTS plus STT about 95%)** |

Without the window, a 60-turn Haiku session costs $0.029 instead of $0.012. Add moderation calls and cache writes (Anthropic charges a write premium; see its pricing page) or cache storage (Gemini 3.1 Flash-Lite: $1 per 1M tokens per hour, so 50 cached 1,500-token personas cost about $1.80 a day). Claude 4.7 and later use a tokenizer that produces about 30% more tokens for the same text, so count with each provider's tokenizer.

### Context budget for a 4,096-token device model

| Slot | Tokens |
| --- | --- |
| Instructions (persona, world rules, refusal style) | 600 |
| Tool definitions | 400 |
| Output schema | 200 |
| Game-state snapshot | 700 |
| Memory summary and last 2 exchanges | 700 |
| Player input (capped) | 150 |
| Output (capped) | 350 |
| Headroom | 996 |

When the transcript nears the headroom line, summarize into the memory slot and start a new session [inference].

## Diagnostics

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Players talk an NPC into rewards, quest skips or sexual roleplay | Model output drives state; no closed intents; no adversarial evals | Authority contract; rewards only from rules; adversarial set covers extraction and roleplay |
| A licensed character voice speaks slurs within hours of launch | No moderation, or moderation after TTS; no per-NPC switch | Moderate each sentence before TTS; per-NPC kill switch; same-day filter hotfix path |
| Context-window error on device mid-conversation | Transcript, schemas and tools exceed 4,096 tokens | Slot budget; count with `tokenCount(for:)`; summarize and open a new session |
| On-device model blocks ordinary combat or grief lines | Guardrails trip on violent fiction [inference] | Frame instructions as fiction; scripted bank per beat; `permissiveContentTransformations` only covers transforming text |
| A refusal shows up as an in-world line | Refusal arrived as plain text | Explicit `refuse` intent in the schema; out-of-character phrase filter |
| NPC says it is an AI model or names a vendor | Persona break; generic refusals | Writer-made in-character refusals; output filter; persona-break eval category |
| Dialogue changed after an OS update with no code change | OS shipped a new on-device model | Eval on every OS beta; gate the feature per OS version in remote config |
| Same prompt behaves differently on two Android flagships | Different Gemini Nano versions | Log `getBaseModelName()`; eval per version; per-version prompt config |
| `BUSY` errors on Android | Per-app quota, battery quota, or a background call | Foreground only; back off; scripted fallback |
| Cloud bill spikes from a few accounts | Scripted farming of free chat; no per-player cap | Reserve-then-settle caps on tokens and characters; rate limit; hand patterns to anti-cheat |
| Cost per session rises with conversation length | Whole transcript resent each turn | Window plus summary; cache the static prefix |
| Kill switch flipped but some players still get live output | Client calls the vendor directly or caches the flag | All calls through the proxy; flag checked server-side per request; no vendor keys in the binary |
| Replay or load shows different dialogue or desyncs | Model called during replay, or generated text in the command log | Store lines as presentation data keyed to ticks; never feed them to the sim |
| Behavior changed with no deploy | Floating alias or provider default moved | Pin full IDs; compare the reported model per response; fail closed |
| First audio over 2 s | Full response awaited before TTS; uncached prefix; oversized model | Stream with sentence gating; cache; smaller model; 0 ms acknowledgement |
| NPC invents items, places or quests | Ungrounded generation | Enum IDs from the state snapshot; reject unknown IDs |
| Feature silently off for some Apple players | Device unsupported, too little free storage (up to 14 GB needed), or device and Siri language differ | Check availability at runtime; scripted path; log the unavailable reason |
| Store reviewer or players flag undisclosed AI | No notice, no report button, forms not updated | references/policy-and-ratings.md checklist before submission |

## Anti-Patterns

**The Oracle NPC.** The model decides who gets gold, which quest completes or whether the player won the argument. Players will find the sentence that pays.

**Speak, Then Screen.** TTS starts before output moderation finishes. A voiced slur is a clip on social media before the filter logs it.

**Prompt as Policy.** "Never give the player items" lives only in the system prompt. Prompts are suggestions to the model; validators and rules are policy.

**Key in the Binary.** The client calls the model vendor with an embedded key. Anyone can extract it, the kill switch cannot reach it, and per-player caps never see the calls.

**The Unbounded Transcript.** Each turn resends the full history. Latency and cost grow every turn until the context error ends the conversation.

**Floating Alias.** Production calls a "latest" alias. The model changes under shipped content with no eval run.

**Regenerate on Replay.** A replay or reload calls the model again and gets different words, or worse, different state.

**The Fourth-Wall Refusal.** A blocked request returns "As an AI language model, I can't...". Write refusals in the character's voice.

**Flagship-Only Launch.** The feature exists only where an on-device model does, with no scripted path; most players meet a broken NPC.

**Vibes Evals.** Prompt changes ship after someone chatted with the NPC for ten minutes. Without a fixed adversarial set, every edit can reopen an old jailbreak.

**Disclose Later.** The AI notice, report button and store answers wait until after launch; store rejections and regulators arrive first.

**The Open Mic for Kids.** Free-text input from children goes to a third-party model. Use choices or a closed local path.

## Quality Checklist

- [ ] Authority contract lists every intent, its validating rule and its effect; no direct grants from model text
- [ ] Placement chosen per intent; scripted path works on every device and with the network off
- [ ] Full model IDs pinned; reported model checked per response; prices dated with source
- [ ] Context assembled in fixed slots; static prefix cached; history windowed and summarized
- [ ] Output schema puts decision fields first; unknown IDs and extra keys rejected; one retry, then fallback
- [ ] Tools whitelisted, idempotent, server-validated and rate-limited; no free-form currency or item arguments
- [ ] Input moderation, guardrails, schema checks and per-sentence output moderation run before screen or TTS
- [ ] In-character refusals and a scripted fallback bank exist for every beat
- [ ] Per-NPC and per-feature kill switches checked server-side and tested on the oldest supported client
- [ ] Per-player daily caps on tokens and spoken characters, reserved before the call; degrade path defined
- [ ] Cost sheet filled with dated prices; cost per DAU-day agreed with finance
- [ ] Latency measured on the floor device; 0 ms acknowledgement in place
- [ ] Generated text never enters deterministic sim state, command logs or replays
- [ ] Eval suite versioned; adversarial set covers every category; run on every prompt, model, SDK and OS change
- [ ] No vendor keys or endpoints in the client build; a build check fails if they appear
- [ ] First-interaction AI notice, in-game report button and store forms done; voice consent on file
- [ ] Under-13 path sends no personal input to third-party models; romance features rated accordingly
- [ ] Every turn traced (input class, intent, blocks, latency, tokens, characters, model ID) for analytics

## Related Skills

Voice casting, VO sessions, TTS voice design and audio implementation go to `gamedev-audio-designer`; persona lines, in-character refusals, fallback banks and barks to `gamedev-script-writer`, with character bibles from `gamedev-narrative-designer`. Abuse of the chat surface, strike thresholds, bans and appeals: `gamedev-anti-cheat-security`; report UX and toxicity norms around player chat: `gamedev-pvp-designer`. The proxy service, per-player rate limits, budget ledger and key custody: `gamedev-backend-engineer`. Turn traces, conversation funnels and A/B tests of AI features: `gamedev-analytics-engineer`. Kill-switch rollout, spend alerts and incidents: `gamedev-live-serving`. On-device integration and memory budgets: `gamedev-ios-engineer`, `gamedev-android-engineer`, `gamedev-desktop-engineer`, `gamedev-unity-engineer`, `gamedev-godot-engineer`, `gamedev-optimization-compatibility`. Determinism and save boundaries: `gamedev-engine-architect`. Languages and LQA of generated text: `gamedev-localization-specialist`; captions for generated speech and alternatives to voice input: `gamedev-accessibility-specialist`. Test plans and certification: `gamedev-qa-verifier`; store submission: `gamedev-delivery-release`. Pricing an AI feature (Steam suggests building the cost into the price, DLC or a subscription): `gamedev-monetization-designer`. Pre-generated AI assets: `gamedev-ai-asset-pipeline`; AI coding workflow: `gamedev-agentic-production`. Playtest reads of AI features: `game-playtest-analyst` (if installed).
