# Brief Templates

Read when the mode is not fix-feedback, or when converting an existing long prompt into a short one. Each block replaces step 3 of "How to work" and may add lines to "Done means".

## Mode blocks

### feature
```
3. Specify the full player flow before coding: entry point → interaction → feedback → exit/navigation → errors → persistence.
   Name the authoritative state owner (client, server, GameCore) and the events that update UI.
Done means adds: one scenario per flow step, plus one failure case (offline, insufficient currency, interrupted).
```

### balance
```
3. For each balance item: (a) check costs, triggers, targeting and state updates for a defect that explains it;
   (b) state one hypothesis and the smallest change; (c) compare before/after with fixed seeds, decks, first player,
   N ≥ <sample> games per matchup using the existing sim/bot; (d) report sample size and bot limits.
   Mark tuning PROVISIONAL unless measured. Preserve distinct playstyles; do not force 50% everywhere.
Done means adds: target band per matchup (e.g. 45–55% unless the design says otherwise) and the data file path.
```

### assessment-followup
```
3. Work the moves in order N1…Nn. For each: the dimension it targets, the current score, the evidence that would
   move it (rubric: 5 built-no-gate → 8 passing gate on main path → 10 committed re-runnable artifact + measured run).
   Produce that evidence, not just the code.
Done means adds: per move, the gate/test/measurement name and where its result is committed.
```

### perf
```
3. Record a baseline on <device> (frame p50/p95 ms, worst frame, thermal state over time, memory peak) with the
   project's tool; change one thing per commit; re-measure on the same device, same build config, same scene.
   No perf claim without before/after numbers.
Done means adds: budget lines (e.g. p95 ≤ 25 ms uncapped, no frame > 100 ms) and the trace/report path.
```

### release
```
3. Run the release gates (<list or "per RELEASE doc">). Prepare store metadata and builds; STOP before submit,
   phased-release start, or price changes and ask for approval. Record build number, commit, and gate results.
Done means adds: go/no-go table with each gate's result and owner sign-off status.
```

### research
```
3. Answer only these questions: <Q1…Qn>. Cite a source per claim. No code changes. Write findings to <path>.
Done means adds: each question answered or marked unknown with what would resolve it.
```

### assessment
Use gamedev-assessment-manager's run brief (`references/run-brief.md` in that skill) as the body.

## Claude Code vs Codex notes

Write tool-neutral by default. Add at most one line per target when the user names one:
- Claude Code: "Use subagents for independent lenses or batches; keep integration in the main session."
- Codex: "Use worktrees for parallel batches; keep one coordinator thread owning the ledger."
- Both: "Split implementation between them where independent; cross-review each other's diff."

## Worked example: long prompt → short brief

Input: a 2,300-word "Assessment, Feedback, Implementation, and Review" prompt for a card game with 14 feedback items (played cards not visible after a turn, opponent turn too fast, card inspect should show full health plus buffs and debuffs, End Turn button jumps sides, Poseidon tide glow, tide status in inspect and modal, deck filter not scrolling to top, Turkish text overflow, played-cards list with detail modal, Zeus too strong vs Poseidon, Hades too weak).

What was cut: generic engineering advice (reuse patterns, small batches, root cause), explanation of why ledgers matter, roles prose (kept as one line), a 10-section structure, repeated "do not claim" rules (kept once), the verification checklist items that do not apply to these items.

What was kept: all 14 items, the assessment link, the Turkish locale check, the balance protocol, completion labels.

Output (≈ 560 words):
```
# Fix 14 playtest items in the card battle and deck builder

You are the lead mobile-game engineer for this repo. Goal: every item below is fixed and shown working in the running game.

## Context
- Repo: infer from workspace. Read AGENTS.md / CLAUDE.md first; they win over this brief.
- Assessment: https://claude.ai/artifact/<id> — findings to re-verify, not facts.
- Locales: English and Turkish.

## Items (every one needs a final status)
FB-001 After a turn ends I can't see the cards either side played → gamedev-hud-engineer
FB-002 Opponent's turn goes by too quickly → gamedev-game-feel-designer
FB-003 Inspect shows full health and clearly marks damage, buffs, debuffs → gamedev-ui-designer
FB-004 During the opponent's turn, End Turn switches back to my side → gamedev-hud-engineer
FB-005 Poseidon cards in hand glow by current Tide (merges 5 and 12) → gamedev-game-feel-designer
FB-006 Tide status visible while inspecting a hand card and in the card modal (merges 6 and 10) → gamedev-ui-designer
FB-007 Deck filter: switching 6→7 mana does not scroll to top → gamedev-ux-designer
FB-008 Card detail shows full health without damage; buffs may show → gamedev-ui-designer
FB-009 Turkish text overflows UI boxes → gamedev-localization-specialist
FB-010 Played-cards list on the left, both sides; tap opens detail modal → gamedev-hud-engineer
FB-011 Zeus too strong vs Poseidon → gamedev-combat-designer (balance)
FB-012 Hades generally too weak → gamedev-combat-designer (balance)

## Done means
- FB-001/010: after any turn, the list shows each card played that turn with owner; tapping one opens its modal. Evidence: screenshot iPhone + iPad.
- FB-002: opponent actions are paced so each play is visible ≥ <ms>; skippable. Evidence: recording.
- FB-004: End Turn stays on the active player's side through the whole enemy turn. Evidence: UI test or recording.
- FB-005/006: glow and tide label update when the tide flips with the modal open. Evidence: screenshots High and Low Tide.
- FB-003/008: modal shows base max health, current damage marked separately, buffs/debuffs listed. Evidence: screenshot with a damaged, buffed card.
- FB-007: changing the filter resets scroll to top. Evidence: UI test.
- FB-009: no clipped or sub-minimum text in Turkish on the smallest supported phone. Evidence: screenshots of every changed screen.
- FB-011/012: rule-defect check, then before/after sims with fixed seeds and first player; report N and bot limits; tuning PROVISIONAL unless measured.

## How to work
1. Baseline build, checks, and reproduce each item; record pre-existing failures.
2. Batch by subsystem (battle HUD, card modal, deck builder, localization, balance). Rules shown in UI come from the same source as gameplay.
3. Balance: defect check → hypothesis → controlled comparison → provisional label.
4. Roles: coordinator + 2 implementers (battle UI, deck/loc) + independent reviewer; balance stays with the coordinator.
5. Verify changed flows in the running game, English and Turkish.

## Rules
- Preserve uncommitted work. No pushes, store actions or deletes without approval.
- Never report a check, review or delegation that did not happen.

## Finish with
Per FB: VERIFIED | IMPLEMENTED — VERIFICATION PENDING | BLOCKED (+ next action) | DEFERRED (+ reason). Then evidence list (build, device, locale), risks, next action.
```
