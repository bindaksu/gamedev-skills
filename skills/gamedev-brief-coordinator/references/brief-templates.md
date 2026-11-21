# Brief Templates

Read when the mode is not fix-feedback, when a step is owner-gated, when the brief targets Claude Code or Codex specifically, or when converting an existing long prompt into a short one. Each block replaces step 3 of "How to work" and may add lines to "Done means".

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
   No perf claim without before/after numbers. Write the keep/revert rule before measuring; confirm a
   winning median with fresh paired runs, and re-measure the last shipped build on the same device the same day.
   On a 60 Hz screen, frame p95 can only read 16.7 or 33.3 ms; judge presented frames, not callback times.
Done means adds: budget lines (e.g. p95 ≤ 25 ms uncapped, no frame > 100 ms) and the trace/report path.
```

### release
```
3. Run the release gates (<list or "per RELEASE doc">) on the full commit SHA. Prepare store metadata and builds;
   STOP before submit, phased-release start, or price changes and ask for approval. If the Xcode/SDK or engine
   version changed since the last shipped build, launch that exact signed build on a device on the newest OS first.
   Read every store action's result back from the store API. Record build number, commit, and gate results.
Done means adds: go/no-go table with each gate's result and owner sign-off status.
```

### research
```
3. Answer only these questions: <Q1…Qn>. Cite a source per claim. No code changes. Write findings to <path>.
Done means adds: each question answered or marked unknown with what would resolve it.
```

### assessment
Use gamedev-assessment-manager's run brief (`references/run-brief.md` in that skill) as the body.

## Gated commands (check form only)

For any step that spends money, uploads, touches the store, deploys, queries production or uses a phone, the brief carries only the form that checks and changes nothing. The generating form is written after the owner approves, quoting the owner.
```
Gated (owner approval required, do not run): paid image batch for FB-007 art.
You may run: tools/gen.py jobs.json --dry-run   (prints cost and job list; must exit without calling the vendor)
If the tool has no dry-run default, or accepts the flag only at one argument position, stop and report: BLOCKED.
```

## Claude Code vs Codex notes (as of 2026-11; verify)

Write tool-neutral by default. Add at most one line per target when the user names one:
- Claude Code: "Read CLAUDE.md (it points to AGENTS.md). Use subagents for independent lenses or batches and worktrees (--worktree, /batch) for isolated parallel edits; keep integration in the main session. Load skills as /gamedev-…." Claude Code loads AGENTS.md by itself only when no CLAUDE.md or CLAUDE.local.md exists, and never reads AGENTS.override.md (https://code.claude.com/docs/en/memory).
- Codex: "Read AGENTS.md. Use worktrees for parallel batches; keep one coordinator thread owning the ledger. Load skills as $gamedev-…." Codex merges AGENTS.override.md or AGENTS.md from the repo root down to the working directory, capped at 32 KiB by default (https://learn.chatgpt.com/docs/agent-configuration/agents-md.md). Its skills live in .agents/skills (repo) or $HOME/.agents/skills and are invoked with $skill-name or /skills, or picked implicitly from the description (https://learn.chatgpt.com/docs/build-skills.md).
- Both: "Split implementation between them where independent; the other tool reviews each diff read-only." Name a pinned model ID per role, not an alias; aliases move and resolve differently per provider (gamedev-agentic-production, references/model-routing.md).
- Night or unattended lanes: "Write the morning report file even if you fail; leave no claim In Progress."

## Worked example: long prompt → short brief

Input: a 1,700-word "Playtest Fix Pass" prompt for a top-down roguelite with 11 feedback items (dodge roll dropped right after an attack, relic pickup text under the virtual joystick, unreadable boss slam telegraph, run summary missing relics, shop reroll charging a different price than it shows, Brazilian Portuguese text clipped in relic descriptions and the shop, resuming after backgrounding restarts the room, haptics firing with haptics off, run summary should show damage per relic, crit relics stacking too strongly, run lost after a phone call).

What was cut: a page of studio background and tone guidance, generic engineering advice (clean code, small commits), a tool list the agent already has, an eight-section template, the "don't break saves" warning repeated four times (kept once, under Rules), regression checks for screens no item touches.

What was kept: all 11 items (merged to 9: item 4 with 9, item 7 with 11), the device test for interrupted runs, the Brazilian Portuguese locale check, the balance protocol, completion labels.

Output (≈ 540 words):
```
# Fix 9 playtest items in combat, run summary, shop and saves

You are the gameplay engineer for this repo. Goal: every item below is fixed and shown working in a real run.

## Context
- Repo: infer from workspace. Read AGENTS.md / CLAUDE.md first; they win over this brief.
- Playtest notes: notes.md, in the players' words. Reports to reproduce, not facts.
- Platforms: iOS and Android phones. Locales: English and Brazilian Portuguese (pt-BR).

## Items (every one needs a final status)
FB-001 Dodge roll is dropped when pressed right after an attack → gamedev-combat-designer
FB-002 Relic pickup text sits under the virtual joystick on small phones → gamedev-hud-engineer
FB-003 Boss slam telegraph is unreadable; players die before they see it → gamedev-combat-designer
FB-004 Run summary lists every relic with the damage each dealt (merges 4 and 9) → gamedev-ui-designer
FB-005 Shop reroll charges a different price than it shows → gamedev-ui-designer
FB-006 pt-BR text clipped in relic descriptions and the shop → gamedev-localization-specialist
FB-007 Backgrounding the app or taking a call restarts the room or loses the run (merges 7 and 11) → gamedev-engine-architect
FB-008 Haptics fire with haptics turned off → gamedev-accessibility-specialist
FB-009 Crit relics stack too strongly; most winning runs take them → gamedev-combat-designer (balance)

## Done means
- FB-001: a dodge pressed inside the input buffer after an attack always rolls. Evidence: input-replay test at 30 and 60 fps.
- FB-002: pickup text clears the joystick and the safe areas. Evidence: screenshot on the smallest supported phone.
- FB-003: the slam winds up for at least <ms> with a ground marker before damage. Evidence: frame data and a recording.
- FB-004: after a seeded run with known relics, the summary lists each one with its damage. Evidence: screenshot plus the seed.
- FB-005: shown and charged reroll prices come from one function and match at every reroll count. Evidence: unit test.
- FB-006: no clipped or sub-minimum pt-BR text. Evidence: screenshots of every changed screen on the smallest supported phone.
- FB-007: background mid-room or take a call, then return: same room, health, relics and gold. Evidence: device test on iOS and Android; existing saves still load.
- FB-008: with haptics off, a full run makes zero haptic calls. Evidence: a test that counts the calls.
- FB-009: rule-defect check first (does stacking follow the written formula?), then before/after sims over fixed seeds; report N and bot limits; tuning PROVISIONAL unless measured.

## How to work
1. Baseline build and checks; reproduce each item; record failures that predate you.
2. Batch by subsystem: input and boss, summary and shop, localization, saves, balance. Numbers shown in UI come from the same function as gameplay.
3. Saves (FB-007): reproduce with a scripted background-and-resume cycle before touching the save path.
4. Balance (FB-009): defect check → hypothesis → controlled comparison → provisional label.
5. Roles: one agent with self-review; an independent reviewer reads the save change before it merges.
6. Verify the changed flows in a real run, in English and pt-BR.

## Rules
- Preserve uncommitted work. No pushes, store actions or deletes without approval.
- Never break loading of existing saves.
- Never report a check, review or delegation that did not happen.

## Finish with
Per FB: VERIFIED | IMPLEMENTED — VERIFICATION PENDING | BLOCKED (+ next action) | DEFERRED (+ reason). Then evidence list (build, device, locale), risks, next action.
```
