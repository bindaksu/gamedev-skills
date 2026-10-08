---
name: gamedev-brief-coordinator
description: >-
  Turn a short or messy game request into one detailed, paste-ready brief for a
  coding agent (Claude Code, Codex, or a teammate) that stays short enough to be
  read in full: goal, context, feedback ledger with IDs, skills to load,
  acceptance criteria, evidence, agent roles and completion labels. Use when the
  user says write a prompt, make a brief, turn this into a task for Codex or
  Claude, hand this to an agent, or pastes raw playtest feedback, an assessment
  link, or a one-line feature idea that needs to become an executable assignment.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: meta
---

# Brief Coordinator

A brief is a contract written for a reader with no memory. The agent that receives it knows nothing of the conversation, the repo's history, or what the owner meant by "make it feel better". Everything it needs must be on the page; everything it does not need costs attention. Long prompts fail the same way short ones do: the agent skims, then follows the loudest sentence. The job is to keep the user's every requested item, compress everything else, and make "done" checkable.

The reference standard is a full delivery prompt (assessment → ledger → batches → review → verification → honest completion labels), which typically runs 2,000+ words. This skill produces the same coverage in **400–900 words** by stating rules once, using the repo's own docs by reference instead of restating them, and cutting any line the agent would follow by default anyway.

## Role Profile

Studios do not hire a "prompt writer"; this is the producer's task-writing skill plus the tech lead's acceptance criteria, applied to agent work. At top-grossing studios the equivalent artifacts are the feature brief a GM or producer hands a strike team and the ticket a lead writes for an outsourcing vendor: one owner, explicit scope, measurable acceptance, a definition of done. The KPI is the same as for any brief: how often the work comes back right the first time, without clarifying questions that the brief could have answered.

## When to Use / Not

Use for: generating a prompt or brief from a one-liner, raw feedback, bug lists, an assessment's top moves, a design note, or a release task; converting a long prompt into a short one; adapting one brief for Claude Code vs Codex.

Not for: decomposing a large multi-discipline feature into owned work packages with RACI (gamedev-coordinator does that, and this skill then writes one brief per package); scoring the game (gamedev-assessment-manager); doing the work itself.

## Inputs to Gather

Read before writing. Ask only when an answer changes the brief materially; otherwise assume the default and state it in the brief.

- **Raw ask** (verbatim). Keep the user's words for any item where interpretation matters.
- **Target agent**: Claude Code, Codex, both, or a human. Default: either; write tool-neutral.
- **Repo facts** (inspect cheaply if a workspace is available): engine, platforms, build/test commands, instruction files (AGENTS.md, CLAUDE.md), task ledger location, current branch. Default: "infer from the workspace" and tell the agent to read the instruction files first.
- **Linked evidence**: assessment URL or file, screenshots, logs, feedback docs. Pass links, do not paste their content.
- **Constraints**: deadlines, frozen contracts, files not to touch, budget (models, time), approval gates (store submission, pushes, deletes). Default: no pushes, no store actions, no deletions without approval.
- **Mode** (pick one; see Method step 2).

## Method

1. **Capture every requested item.** Number them FB-001… in the user's order, verbatim when short. Merge exact duplicates (and say "FB-005 merges 5 and 12"); never drop one. This list is the part of the brief that must not be compressed.
2. **Pick the mode** that sets the skeleton:

   | Mode | Trigger | Core of the brief |
   |---|---|---|
   | fix-feedback | Bug or playtest list | Ledger, reproduce, root cause, batch, verify per FB |
   | feature | New mechanic, mode, screen | Player flow end to end, data/state owner, acceptance scenarios |
   | balance | "X is too strong/weak" | Defect check first, hypothesis, controlled before/after, provisional label |
   | assessment-followup | Top moves from an assessment | Moves → tasks, score each targets, evidence that would raise it |
   | perf | Jank, heat, memory, size | Baseline numbers, budget, measure before and after on named device |
   | release | Ship a build | Gates, store steps needing approval, go/no-go evidence |
   | assessment | Run an assessment | Hand to gamedev-assessment-manager's run brief template |
   | research | Unknowns before building | Questions, sources allowed, output file, no code changes |

3. **Route skills.** For each item, name the one pack skill that owns it (use gamedev-coordinator's routing table) and at most two supporting skills. Write them into the brief as "Load: …". Agents without these skills installed lose nothing; agents with them get the domain rules for free.
4. **Write acceptance as scenarios.** Starting state → player action → visible result → state result. One line each. "Works correctly" is not acceptance.
5. **State evidence required per item**: test name, screenshot at named size and locale, measured number on named device, or diff inspection. Match it to the risk; a copy change needs a screenshot, a damage formula needs a test.
6. **Set roles only if parallelism helps**: coordinator, implementers with owned files, independent reviewer, runtime QA. For a single small batch, one agent plus a self-review pass is fine; say which.
7. **Add guardrails once**: preserve user work and dirty trees; follow repo instruction files; no unapproved irreversible actions; never claim a check that did not run.
8. **Close with completion labels and the report shape** (VERIFIED / IMPLEMENTED — VERIFICATION PENDING / BLOCKED / DEFERRED; every FB has one).
9. **Compress.** Run the cut pass below, then count words. Over budget: cut context before cutting the ledger or acceptance.

## The cut pass

Delete a line when any of these is true:
- The agent would do it anyway (read the code before editing, write clean code).
- It restates something the repo's instruction files already say; reference the file instead.
- It explains *why* to an agent that does not need to make a judgment call there.
- It is a second phrasing of an earlier rule.
- It is generic quality advice with no checkable outcome.

Keep a line when it carries: a user requirement, a constraint the agent cannot infer, an acceptance criterion, a required evidence type, an approval gate, or a decision the user already made (so the agent does not re-litigate it).

## Deliverables

### Brief (default output, one fenced block, paste-ready)

```
# <Title: verb + object, e.g. "Fix 14 playtest issues in Twelve Thrones battle UI">

You are the <role> for <repo/game>. Goal: <one sentence: the player-visible outcome>.

## Context
- Repo: <path or "infer from workspace">. Read AGENTS.md / CLAUDE.md first; they win over this brief.
- Platforms/build: <engine, targets, build+test commands or "discover">.
- Evidence: <links: assessment, screenshots, logs>. Treat them as findings to re-verify, not facts.
- Decisions already made: <bullets, or omit>.

## Items (every one needs a final status)
FB-001 <verbatim or tight paraphrase> → owner skill: <gamedev-…>
FB-002 …

## Done means
- FB-001: <scenario: state → action → visible result → state result>. Evidence: <type>.
- …

## How to work
1. Baseline: build, run existing checks, reproduce each FB; record failures that predate you.
2. Batch by subsystem; root-cause fixes; one source of truth for rules shown in UI.
3. <mode-specific step, e.g. balance: check for rule defects first, then controlled before/after, mark tuning provisional>
4. Roles: <single agent + self-review | coordinator + N implementers (owned files) + independent reviewer>.
5. Verify the changed flows in the running game on <devices/sizes/locales>.

## Rules
- Preserve existing and uncommitted work. No pushes, store actions or deletes without approval.
- Never report a check, review or delegation that did not happen.
- Load skills: <list>.

## Finish with
Per FB: VERIFIED | IMPLEMENTED — VERIFICATION PENDING | BLOCKED (blocker + next action) | DEFERRED (reason).
Then: evidence list (build/revision, device, locale), remaining risks, exact next action.
```

Mode-specific blocks and a worked long-to-short conversion are in `references/brief-templates.md` (read when the mode is not fix-feedback, or when converting an existing long prompt).

### Optional companions
- **Short form** (≤ 150 words) when the user asks for a one-message prompt: Goal, Items, Done means, Finish with.
- **Split briefs**: when gamedev-coordinator produced work packages, one brief per package with its handoff contract pasted as "Done means".

## Quantitative Reference

| Element | Budget (heuristic) |
|---|---|
| Whole brief | 400–900 words; hard cap 1,200. Short form ≤ 150 |
| Goal | 1 sentence, ≤ 30 words |
| Context | ≤ 6 bullets |
| Each FB line | ≤ 25 words, verbatim if the user's wording matters |
| Each acceptance line | 1 scenario, ≤ 35 words |
| Rules | ≤ 5 bullets; anything in AGENTS.md is referenced, not repeated |
| Skills to load | 1 owner per item, ≤ 2 supporting, ≤ 8 total |

Heuristic for size vs work: briefs for 1–3 items rarely need roles or batching; 4–15 items need batching by subsystem; 16+ items or 3+ subsystems should go through gamedev-coordinator first, then one brief per package.

## Diagnostics

| Symptom in the agent's output | Likely cause in the brief | Fix |
|---|---|---|
| Items silently skipped | Ledger compressed into prose | Numbered FB list; "every one needs a final status" |
| Asks questions the user already answered | Decisions not recorded | Add "Decisions already made" |
| Claims done without evidence | Evidence type unspecified | Add evidence per FB in Done means |
| Rewrites unrelated systems | No scope line | Add "unrelated findings → follow-up list, not this batch" |
| Re-tunes balance by feel | Balance item treated as a bug | Use balance mode: defect check, hypothesis, controlled comparison |
| Contradicts repo rules | Brief restated rules differently | Reference AGENTS.md instead of restating |
| Stops after the first batch | No continuation rule | "Continue until each FB has a status" |

## Anti-Patterns

**The Kitchen-Sink Prompt** — every best practice ever written, 3,000 words; the agent follows the last screenful.
**The Paraphrased Feedback** — the user's "the opponent's turn goes by too quickly" becomes "improve pacing"; the actual ask is lost.
**Acceptance by Adjective** — "smooth", "clean", "correct". Nothing to check, so nothing gets checked.
**Pasted Evidence** — a whole assessment pasted inline; link it and name the findings that matter.
**The Duplicate Rulebook** — restating AGENTS.md with small differences, creating two authorities.
**Fake Parallelism** — five agents for three coupled edits in one file.
**Tool-Locked Brief** — instructions that only work in one agent's harness when the user asked for Claude and Codex.

## Quality Checklist

- [ ] Every user item appears as an FB line; merges are stated
- [ ] Mode chosen and its specific step present
- [ ] Each FB has an owner skill and a scenario-form acceptance line with an evidence type
- [ ] Repo instruction files referenced, not restated
- [ ] Irreversible actions gated on approval
- [ ] Completion labels and finish report present
- [ ] Word count within budget; cut pass applied
- [ ] Readable by an agent with zero conversation context

## Related Skills

- gamedev-coordinator — run first when the ask spans 3+ disciplines; then write one brief per package.
- gamedev-assessment-manager — produces the top moves that assessment-followup briefs turn into work; also uses this skill to brief its lens agents.
- gamedev-producer — scope cut lines and milestone context when the brief must fit a date.
- gamedev-reviewer and gamedev-qa-verifier — define the review and verification evidence a brief should demand.
