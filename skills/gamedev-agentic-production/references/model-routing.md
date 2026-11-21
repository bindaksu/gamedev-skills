# Model Routing for Coding Agents (as of 2026-11; verify)

Read before pinning model IDs in agent configs or briefs, when choosing which model plans, implements, reviews or triages, and when a lane's quality or cost changes without a code change (an alias moved). Every row is a dated fact; re-check the source before changing a lane.

Tags: **[O]** official vendor page read on 2026-11-21 · **[S]** secondary source · **[U]** unverified · **[inference]** a synthesis, not a quote. Prices are USD per million tokens (MTok), input / output, standard tier. Source numbers (S1...) refer to the list at the end.

## 1. Routing rules

1. **Pin full model IDs** in configs, role files and briefs. Aliases move to newer models, and the same alias resolves to different models on different providers (section 3) [O S6].
2. **Verify the served model** at lane start: compare the model name the API response or session reports with the ID you requested, log both in the lane's first ledger row, and stop the lane on a mismatch. One team's probe found a cheap-tier alias serving a mid-tier model; it then pinned dated IDs and refused unverified bindings [inference from practice].
3. **Tune effort before switching models.** Anthropic's guidance is to raise or lower effort first, and to move to a bigger model only when evals at high effort still fall short [O S3, S4].
4. **Review with a different family** from the builder, read-only. The same model shares the builder's blind spots [inference].
5. **Spread lanes across plans and vendors** so one usage limit or quota cut does not stop every lane; keep a resume note in every task so another model can continue [inference from practice].
6. **Check the CLI version** a model needs before routing to it (section 3 and 4); an older binary may refuse or silently fall back.

## 2. Suggested tiers [inference]

Synthesised from the vendor guidance in section 7; not a vendor table.

| Role | Claude | Codex / OpenAI | Gemini |
|---|---|---|---|
| Planning, architecture, review of hard diffs | claude-opus-5-5 (escalate to claude-fable-5-2) | gpt-6.2-astra | gemini-4-carbon / gemini-4-neon |
| Bulk implementation and edits | claude-sonnet-5-5 | gpt-6.2-sol | gemini-4-hydrogen |
| Cheap triage, search, extraction subagents | claude-haiku-5-5 | gpt-6-luna | gemini-3.5-flash-lite |
| Visual work and computer use | claude-opus-5-5 | gpt-6.1-terra | - |

Other implementer: kimi-k3.1-pro (section 6). Practice in small teams: the planning model also reviews, cheaper models implement and test, 3-4 parallel implementation lanes [inference from practice].

## 3. Anthropic [O S1, S2, S5]

| Model | API ID | Context / max output | $ per MTok in / out | Cache hit | Default effort | Launched |
|---|---|---|---|---|---|---|
| Fable 5.2 | claude-fable-5-2 | 1M / 128K | 8 / 40 | 0.20 | high | 2026-11-09 |
| Opus 5.5 | claude-opus-5-5 | 1M / 128K | 4 / 20 | 0.20 | medium | 2026-09-22 |
| Sonnet 5.5 | claude-sonnet-5-5 | 1M / 128K | 2 / 10 | 0.10 | high | 2026-09-28 |
| Haiku 5.5 | claude-haiku-5-5 | 1M / 128K | 0.10 / 0.50 up to 100K-token prompts; 0.50 / 2.50 above | 0.01 / 0.05 | medium | 2026-10-07 [S S30] |

- All four have adaptive thinking (always on for Fable 5.2 and Opus 5.5) and a June 2026 knowledge cutoff [O S1].
- Claude Mythos 5.2 (claude-mythos-5-2) matches Fable 5.2 but is open only to verified organizations [O S3].
- Bedrock IDs differ, e.g. global.anthropic.claude-fable-5-2 and anthropic.claude-opus-5-5 [O S1].
- Fast mode: up to 2.5x output speed at 2x price, on Fable 5.2 and Opus 5.5 [O S2, S4].
- Claude 4.7 and later use a tokenizer that produces about 30% more tokens for the same text; re-budget token caps when moving from older models [O S2].
- Legacy still listed: Fable 5.1 $10/$50; Opus 5 and Opus 4.8 $5/$25; Sonnet 5 $2/$10; Haiku 4.5 $1/$5 with 200K context [O S1, S2].

**Claude Code aliases** [O S6]: default, best (same as opus), fable, opus, sonnet, haiku, sonnet[1m], opus[1m], opusplan (Opus in plan mode, Sonnet for execution).
- On the Anthropic API: opus, sonnet and haiku resolve to the 5.5 models; fable to Fable 5.2.
- On Bedrock and Google's Agent Platform, sonnet and haiku resolve to 4.5; on Microsoft Foundry, opus resolves to 4.6. The same config therefore runs different models per provider.
- No plan defaults to Fable; it must be picked.
- Minimum Claude Code versions: Fable 5.2 v2.1.321, Opus 5.5 v2.1.280, Sonnet 5.5 v2.1.284, Haiku 5.5 v2.1.293.
- Built-in Explore subagent is read-only and runs on the parent's model; under a Fable parent it uses Opus on subscription and Console accounts. Custom subagents can set their own model [O S9].
- Models with a native 1M window auto-compact at about 967K tokens; /autocompact changes it [O S6].

## 4. OpenAI and Codex [O S13, S14, S20, S21]

Prices apply to prompts up to 272K tokens; above that the higher rate applies to the whole request.

| ID | Vendor role | Default context in Codex | $ per MTok in / cached / out | Above 272K in / out |
|---|---|---|---|---|
| gpt-6.2-astra | Hardest end-to-end work | 272K, up to 1M | 8 / 0.40 / 40 | 16 / 60 |
| gpt-6.2-sol | Everyday coding (Codex default from CLI 0.171.0) | 500K, up to 1M | 2 / 0.10 / 10 | 4 / 15 |
| gpt-6.1-terra | Fast; writing, visual work, computer use (needs CLI 0.159.0+) | n.d. | 1 / 0.05 / 5 | 2 / 7.50 |
| gpt-6-luna | Focused, high-volume, repeatable tasks | n.d. | 0.10 / 0.01 / 0.50 | 0.20 / 0.75 |
| gpt-6-astra | Earlier flagship | n.d. | 10 / 1 / 50 | 20 / 75 |
| gpt-6.1-sol | Suggested for a config shared with the IDE extension | 500K | 2 / 0.10 / 10 | 4 / 15 |

- Rate modifiers [O S14]: Batch 50% of standard; Fast mode 2x (renamed from Priority on 2026-07-30); Ultrafast on 6.2 3x through 2027-02-28, then 6x; eligible background requests 30% cheaper with a 2-hour window, 40% with an 8-hour window. The GPT-5.6 Sol promotional price ends 2026-11-30.
- Codex CLI 0.171.0 (2026-11-20) added GPT-6.2 Sol and Astra, with Sol as default [O S20]. GPT-6.2 reached Codex on 2026-11-17 [S].
- Retired in Codex under ChatGPT sign-in (API-key sessions unaffected) [O S13]: gpt-5.3-codex-spark (2026-09-14), gpt-5.4 and gpt-5.4-mini (2026-08-31), gpt-5.5 (2026-10-14). Deprecated: gpt-5.2, gpt-5.3-codex. No Codex-branded model is current; Copilot still uses gpt-5.3-codex as its fallback [O S29].
- Reasoning effort in Codex [O S13]: Light (Low in the CLI), Medium, High, Extra High; Max gives one task more time; Ultra splits work across subagents (most tasks do not need it; Luna does not support it).
- Custom agents: TOML in ~/.codex/agents or .codex/agents with name, description, developer_instructions, optional model and model_reasoning_effort; [agents] holds defaults such as default_subagent_model [O S19].

## 5. Google [O S23, S24, S25, S26]

All have a 1M-token context.

| ID | Vendor role | $ per MTok in / out |
|---|---|---|
| gemini-4-carbon | Strongest reasoning | 2 / 10 until 2026-11-30; 4 / 20 from 2026-12-01 |
| gemini-4-neon | Frontier reasoning | 3 / 15 |
| gemini-4-hydrogen | Recommended default for coding and agent work | 1.50 / 7.50 |
| gemini-3.8-flash | Fast | 0.75 / 3.75 until 2026-12-31, then 1.50 / 7.50 |
| gemini-3.5-flash-lite | High-throughput subagents and routing | 0.30 / 2.50 |

- Gemini CLI was replaced by Antigravity CLI (agy) for unpaid-tier and Google One users on 2026-06-18; Antigravity keeps Agent Skills, hooks, subagents and extensions (now plugins) [O S25, S26].

## 6. Moonshot Kimi [O S27]

- Current: kimi-k3.1-pro (flagship, 1M context), kimi-k3.1-pro-highspeed, kimi-k3 (previous flagship).
- kimi-k2.7-code, kimi-k2.7-code-highspeed and kimi-k2.6 are closed to new users; deprecation expected late December 2026.
- Prices: K3.1 Pro $2/$10, K3 $3/$15 [S].
- A quota cut on one vendor stopped a lane mid-task in practice; keep resume notes current on lanes routed to smaller vendors [inference from practice].

## 7. What the vendors recommend

- **Anthropic** [O S1, S3, S4, S6, S9]: start with Opus 5.5; move to Fable 5.2 only if evals at xhigh or max effort still fall short. Sonnet 5.5 for everyday coding; Haiku 5.5 for lowest latency and price, including subagents. Anthropic's own measurements: on work larger than one context window, Opus 5.5 with Sonnet 5.5 subagents cost about a third less than Opus alone at about the same score; adding Haiku 5.5 subagents cut cost 32% and pass rate about 4 points (similar to lowering effort); the advisor pattern scored +1.7 points (at the edge of run-to-run noise) for about 2.1x the cost.
- **OpenAI** [O S21]: start with GPT-6.2 Sol; Astra for complex projects; Luna for small, repeatable, frequent automations; Terra for visual and computer-use work. Its effort ladder runs from Luna at Low to Astra at Extra High.
- **Google** [O S23]: Hydrogen is the default for coding and agents; Carbon or Neon for deep reasoning; 3.5 Flash-Lite for high-throughput subagents and routing.

## 8. Availability in other hosts

- **Cursor** [O S28]: own models Composer 2.5 and Grok 4.5-4.7; third-party Claude Fable 5.2, Opus 5.5, Sonnet 5.5, Haiku 5.5; Gemini 4 Carbon, Neon, Hydrogen, Argon, Gemini 3.1 Pro, 3.8 Flash; GPT-5.6 Sol, Terra and Luna. Composer 2.5 $0.50/$2.50 with 200K context [S].
- **GitHub Copilot** [O S29]: GPT-6.2 Astra and Sol, GPT-6.1 Sol and Terra, GPT-6 Astra, Sol and Luna, GPT-5.6, GPT-5.3-Codex (Auto fallback); Claude Fable 5, 5.1, 5.2, Opus 5.5, Sonnet 5.5 and 5, Haiku 5.5; Gemini 4 Argon, Carbon, Hydrogen, Neon and 3.8 Flash; MAI Code 2 family; Kimi K3; Grok 4.5-4.7.

## 9. Conflicts to keep flagged

- **Gemini 4 Argon:** on the pricing page at Carbon's prices and listed by Copilot and Cursor, but missing from Google's Latest models overview; secondary sources disagree on whether it is publicly callable.
- **Cursor naming:** Cursor lists GPT-5.6, not GPT-6.x; its docs may lag.
- **GPT-6.2 in the IDE:** the model cards say "App and CLI" and the docs suggest gpt-6.1-sol for a config shared with the IDE extension; GPT-6.2 may not be in the IDE yet.
- **Sonnet 5 price:** secondary sites say $3/$15; Anthropic's pricing page says $2/$10 [O S2].
- **Codex skill limits:** a third-party validator claims 100-character names and 500-character descriptions [U]; OpenAI's own script uses 64 and 1024 [O S17].

## Sources

- S1 https://platform.claude.com/docs/en/about-claude/models/overview
- S2 https://platform.claude.com/docs/en/about-claude/pricing
- S3 https://platform.claude.com/docs/en/about-claude/models/choosing-a-model
- S4 https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence
- S5 https://platform.claude.com/docs/en/release-notes/overview
- S6 https://code.claude.com/docs/en/model-config
- S9 https://code.claude.com/docs/en/sub-agents
- S13 https://learn.chatgpt.com/docs/models.md (redirected from developers.openai.com/codex/models)
- S14 https://developers.openai.com/api/docs/pricing.md
- S17 https://raw.githubusercontent.com/openai/skills/main/skills/.system/skill-creator/scripts/quick_validate.py
- S19 https://learn.chatgpt.com/docs/agent-configuration/subagents.md
- S20 https://learn.chatgpt.com/docs/changelog (Codex CLI 0.171.0, 2026-11-20)
- S21 https://learn.chatgpt.com/docs/model-selection.md
- S23 https://ai.google.dev/gemini-api/docs/latest-model (loads from aistudio.google.com/docs/latest-model)
- S24 https://aistudio.google.com/docs/pricing
- S25 https://geminicli.com/docs/cli/model-routing/
- S26 https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/ (2026-05-19)
- S27 https://platform.kimi.ai/docs/models
- S28 https://cursor.com/docs/models-and-pricing
- S29 https://docs.github.com/en/copilot/reference/ai-models/supported-models
- S30 https://9to5mac.com/2026/10/07/anthropic-upgrades-claude-with-new-haiku-5-5-model-details-here/ (secondary)
