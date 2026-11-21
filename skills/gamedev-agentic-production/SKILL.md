---
name: gamedev-agentic-production
description: >-
  Design and run the harness for building a game with many coding-agent sessions
  (Claude Code, Codex and others): one canonical AGENTS.md standing-rules file,
  append-only task and decision ledgers with reserved number blocks, task claims
  with stale-claim folding, completion labels and evidence rules, owner-approval
  gates for paid calls, uploads and device turns, host capacity locks for builds,
  test suites, simulators and phones, worktree lanes with one owner per
  choke-point file, usage-limit resume notes, cross-model review and dated model
  routing. Use when setting up AGENTS.md or CLAUDE.md for a game repo, running
  several agents in parallel on one workstation, when agents collide on files,
  decision numbers or devices, the machine freezes or tests time out under agent
  load, done reports turn out false, a usage limit stops every lane, or when
  choosing which model plans, builds and reviews.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.1.0"
  category: meta
---

# Agentic Production

A game built by a fleet of coding-agent sessions does not fail the way a human team does. Agents are fast, literal and forgetful: each session reads the standing rules once at start, trusts whatever file it finds, reports what it believes happened, and will start a tenth simulator on a workstation that can run two. The binding constraints turn out to be the host machine, the shared phones and simulators, each plan's usage window, and the owner's own playtime, not the number of agents. This seat builds the harness that keeps those limits honest: one standing-rules file, append-only ledgers, claims that expire, evidence a machine can re-check, a lock for every shared resource, approval gates that quote the owner, and a dated table of which model plans, builds and reviews. It also deletes harness that costs more than it catches. It does not do specialist work and it does not split features into packages.

## Role Profile

No studio publishes this title yet [inference]. The function combines a build and release engineer (locks, gates, CI), a producer (claims, ledgers, approvals, capacity) and a tech lead (write scopes, review chain), applied to agent sessions instead of people. The vendors now ship the primitives: background sessions, worktree isolation and batch fan-out in Claude Code (https://code.claude.com/docs/en/agents), layered AGENTS.md files and custom agents in Codex (https://learn.chatgpt.com/docs/agent-configuration/agents-md.md, https://learn.chatgpt.com/docs/agent-configuration/subagents.md). Large studios hire LLM and agent engineers (https://supercell.com/en/careers/principal-llm-engineer/2121055 [proxy]); the lessons below are field lessons from production use, written at genre level, from small teams running many agent sessions per workstation [inference from practice].

- **Responsibilities:** standing rules, write scopes, ledgers and number blocks, claims, evidence and label rules, approval gates, host and device locks, worktree lanes, resume notes, model routing, review chain, harness pruning.
- **Hard skills:** shell and git (worktrees, merge drivers, hooks), process and resource control (pids, load, memory, disk), gate scripting, both agents' configuration files, model limits and prices.
- **Tools:** Claude Code, Codex CLI, git worktrees, a lock script, a gate script, JSONL ledgers, a file-based task board.
- **Judged on:** share of done records that survive an independent re-run; agent-hours lost to collisions, freezes and limits; owner minutes per accepted change; incidents on shared devices.
- **Collaborators:** gamedev-coordinator, gamedev-brief-coordinator, gamedev-qa-verifier, gamedev-delivery-release, gamedev-producer, gamedev-ai-asset-pipeline.

## When to Use / Not

Use for: setting up or repairing AGENTS.md and CLAUDE.md in a game repo; running two or more agent sessions in parallel; agents colliding on files, IDs, decision numbers, simulators or phones; a host that freezes or tests that time out only under agent load; done records that fail re-check; usage limits that stop work; choosing and pinning models per role; setting up cross-model review; deciding which harness pieces to delete.

Not for:
- Splitting a feature into discipline packages with owners: gamedev-coordinator.
- Writing one task brief: gamedev-brief-coordinator.
- Test strategy, device matrix, fail-closed harness rules: gamedev-qa-verifier.
- Signing, upload lanes, store rollout: gamedev-delivery-release.
- Spend journals, provenance and approvals for paid asset generation: gamedev-ai-asset-pipeline.
- LLM features inside the shipped game: gamedev-llm-features-engineer.
- Scoring the game: gamedev-assessment-manager. Schedule and scope: gamedev-producer.

## Inputs to Gather

- **Agent tools and versions** (Claude Code, Codex CLI, Cursor, others). They decide which rule file each session reads. Default: Claude Code plus Codex.
- **Host:** cores, RAM, free disk, other projects sharing the machine, phones and simulators and who else uses them. Default: one workstation shared with at least one other project.
- **Where rules live now:** CLAUDE.md, AGENTS.md, READMEs, operating briefs, handoff docs, agent memory outside the repo.
- **Choke-point files:** files every lane wants (project or solution file, package lockfile, string catalog, constants table, decision log, build number, asset manifest).
- **Gates:** the commands that make a task done, with runtime and peak memory of each.
- **Owner:** which actions need approval (paid calls, uploads, store actions, deploys, production queries, phone use, external testers); hours per week the owner can play and review. Default: all of those gated; ask for the playtime number.
- **Plans and limits:** usage windows per subscription, API spend caps, which lanes share an account.

## Method

1. **Collapse the rules into one file.** List every place rules live, move them into one AGENTS.md at the repo root (harness and release scripts go in the repo too; scripts kept outside it were lost in a drive move), and reduce the rest to pointers or delete them. Rules kept in loose briefs or in agent memory outside the repo drift apart and are invisible to the other tool. Name how Claude Code gets the rules: a CLAUDE.md whose only content orders a read of AGENTS.md and restates nothing, no CLAUDE.md at all (Claude Code then reads AGENTS.md), or the claude-md-and-agents-md setting. Codex concatenates AGENTS.override.md or AGENTS.md from the repo root down to the working directory up to 32 KiB; Claude Code never reads AGENTS.override.md (Technical Reference). Keep the file to gotchas, the never-list, gates, locks and owner gates. Live state goes in dated handoff files, because a session reads standing rules only when it starts.
2. **Declare write scopes and choke-point owners.** Each lane or role lists the paths it may write. Each choke-point file has exactly one owner lane; other lanes append a request row. Only the integration owner bumps versions and build numbers. Generate the per-tool role files (Claude Code subagents, Codex agent TOML) from one source so they cannot disagree.
3. **Set up append-only ledgers.** Task queue as JSONL with one record per event, union-merged in git, last record per task ID wins. Decision log where reversals are new rows, owner quotes are verbatim and each row has a "reverse by" date or condition. Product questions are recorded as ASSUMED with the assumption, so work continues. Give each lane a reserved number block for decisions, constants, questions and tickets (lane 3 gets 300-399), because worktrees that number from "last + 1" collide; create tickets under a lock. Formats: references/harness-templates.md.
4. **Make claims expire.** Write the claim row (lane, session, pid, host, start time) before work starts, so a crashed session still leaves a record. A claim older than 2 h folds back to pending unless its pid is alive. Three failures mark a task BLOCKED; an oversized task is split, not retried. At each wave end, reconcile every claim against file timestamps and diffs: a night lane that reported nothing still left traces, and its tickets must not stay In Progress.
5. **Fix evidence rules and labels.** One label set everywhere: VERIFIED, IMPLEMENTED — VERIFICATION PENDING, BLOCKED, DEFERRED (the same as gamedev-brief-coordinator), with the evidence level in the note (compiled, tested, observed on device). A missing metric is "not measured", never 0. A status line reports the reporter's own work only. Every gate run writes a manifest with the full 40-character commit SHA, a dirty flag and a content hash of the tree; a gate log keyed by a short or prefix SHA does not count. The ledger refuses evidence paths git does not track. Simulator figures and runs on a loaded host are directional only. Receipts are capped (about 200 words) by a script. Harness rules (fail closed, verdict is the AND of steps, a check counts only after it failed on a control) belong to gamedev-qa-verifier.
6. **Gate the irreversible on the owner's words.** Paid calls, uploads, store submission, deploys, production queries, external testers and phone turns need an approval record that quotes the owner verbatim, with a cap, a hash of the plan shown and an expiry. Submit, deploy and phone use also need the owner's exact word in that turn. Briefs carry only the check form of a gated command. Gated tools default to dry-run and refuse misplaced flags. Store-console credentials given to agents cannot submit; the owner presses Submit. An agent's acceptance is never the owner's. Record owner overrides and gate waivers verbatim with what they skip; waived gates once let launch crashes reach the owner's phone. Read the result of every store or API action back instead of trusting an exit code.
7. **Budget the host, not the agents.** Separate heavy lanes (builds, full test suites, simulators, engine editors, local model runs) from light lanes (reading, editing, one module's unit tests). Cap heavy work at about 2 concurrent jobs and one full test suite at a time, behind mkdir lock slots. Run tests with one worker; size per-test timeouts to catch hangs (about 60 s), never to absorb load. Record the 1-minute load average and free memory in every capture and manifest, and refuse to start heavy work above a ceiling. Run heavy jobs at background priority (nice; taskpolicy -c utility on macOS). Never kill processes by name pattern; kill by the pid in your own lock file.
8. **Lock shared devices; clean only your own.** Phones and simulators get a lock file of key=value lines (holder, pid, started, purpose, project, max_s) parsed by key and checked for pid liveness, with turns of 60 minutes or less and an owner hold no agent may override. A device turn runs under a watchdog that restores the owner's build and frees the lock if the session dies. Warn other sessions before long UI runs. Never quit the simulator host app: it shuts down every simulator, including another project's gate. Delete only simulators, caches and build products your project created. Keep a disk floor that refuses heavy work below it, rotate agent logs, and check free space on phones before installs and perf runs.
9. **Run lanes in worktrees.** One worktree and branch per task or lane, with declared output directories that do not overlap, merging into one integration branch per build. Re-run tests on the integration branch after every merge, because branches that pass alone can break together, and run a merge guard (typecheck, targeted tests, ledger check) after each one. Lanes commit to their own task branch at each green step, staging by explicit path, so every session leaves a rollback point; one team carried days of uncommitted work in a shared tree with none. Keep worktrees outside the repo tree or excluded from lint, IP and secret scans. A worktree without its own .env sources the main checkout's in a subshell; agents never read .env. Sandboxed agents may need extra writable-directory grants to commit from a worktree and may read symlinked caches as empty [inference from practice]; check the sandbox before marking a task blocked. Push lane branches and alert when CI goes quiet. Late waves may share the main tree with at most 4 agents.
10. **Survive usage limits and crashes.** Every task spec carries a resume note (state, last green SHA, next command, files touched, open claims, approaches that failed), updated at each step and written for the next session on another account or model. Spread lanes across plans and vendors and stagger their start times, so one usage window cannot stop every lane at once. When a quota cuts a task mid-way, re-dispatch from the resume note. Standing rules change only between sessions; running sessions get a dated handoff note.
11. **Route models and verify the binding.** Plan, review and arbitrate with the top tier; implement with the mid tier; search, triage and extract with the cheap tier; keep implementation lanes to 3-4 per owner. Pin full model IDs in configs and briefs, because aliases move and resolve differently per provider. At lane start, compare the model the session or API response reports with the one requested and refuse to run a lane whose binding cannot be verified; one probe found a cheap-tier alias serving a mid-tier model. Dated table and sources: references/model-routing.md.
12. **Chain review across models.** Builder self-check, then an independent verifier in a fresh session that re-runs gates from the manifest, then for timing-sensitive or multi-file work a read-only review by a different model family (gamedev-reviewer), then the owner on a device. Every ~50 completed tasks a verifier audits a sample with no other heavy lane running. A scheduled read-only reassessment with a spend cap per run re-measures what working sessions scored themselves (gamedev-assessment-manager).
13. **Cap acceptance by owner playtime, then prune.** Accept feel-bearing work (combat, motion, juice, screen flow) no faster than the owner can play it; gamedev-producer owns that cap. Monthly, count what each rule, receipt, ledger and review caught over the period and delete what costs more than it catches. One team's reset after a heavy process phase was git, one serial gate and owner checks on the phone.

### Harness size by fleet

| Fleet | Rules | Ledgers | Locks | Review | Leave out |
|---|---|---|---|---|---|
| 1 session | AGENTS.md of about one page | Decision log | Device lock only | Self-check + owner on device | Claims, number blocks, receipts |
| 2-4 lanes | + write scopes, choke-point owners | + task queue with claims, number blocks, approvals | + heavy slots, simulator and test-suite locks | + independent verifier; cross-model on risky diffs | Per-task receipts, multi-agent review of small diffs |
| 5+ lanes | + role files generated per tool | + gate manifests, evidence check | + load ceiling, disk floor, janitor | + audit every ~50 tasks, scheduled read-only reassessment | Anything that caught nothing last month |

## Deliverables

### 1. Lane plan

```
LANE WORKTREE          BRANCH          MODEL (pinned id)  WRITE SCOPE                    CHOKE POINTS     NUMBERS    HEAVY  LOCKS
L0   main checkout     integ/build-57  <top-tier id>      version, project file, ledgers project, lockfile D-000..099 yes    build(1) suite(1)
L1   ../wt/l1-combat   task/l1-combat  <mid-tier id>      src/combat/**, tests/combat/** -                D-100..199 no     test(2)
L2   ../wt/l2-ui       task/l2-ui      <mid-tier id>      src/ui/**, strings via L0 row  -                D-200..299 no     test(2) sim(1)
V1   read-only clone   -               <other family id>  ledger/verifications.jsonl     -                -          yes    suite(1)
USAGE WINDOWS: L0+V1 on plan A, L1 on plan B, L2 on vendor C; starts staggered 90 min
OWNER: approves uploads, paid calls, phone turns; plays 3 h/week -> at most 3 feel-bearing acceptances/week
HOST: heavy slots 2, full suite 1, load ceiling <n>, disk floor <GB>
```

### 2. Approval record

```
APPROVAL   A-014                     (append-only; one per action class and batch)
ACTION     upload build 57 to internal testing | paid image batch | phone turn on <device alias>
OWNER SAID "<verbatim quote>"  (date, channel, same turn for submit/deploy/phone)
CAP        1 upload | 40 images, <currency amount> | 45 min
PLAN HASH  sha256 of the exact command list shown to the owner
EXPIRES    <ISO time>       USED BY <lane, session>
READ-BACK  <state read from the store or API after the action>
```

### 3. Resume note (top of every task spec)

```
RESUME     T-0231   updated <ISO time> by <lane / session / pinned model id>
STATE      done so far, one line per file touched
LAST GREEN <full sha>  gates/<full sha>/<gate>.json
NEXT       the exact next command
CLAIMS     open claim rows (renew or release)
WAITING    ASSUMED question IDs; pending approvals
TRIED      approaches that failed, and why
```

### 4. Device lock file (one per phone or simulator, shared across projects)

```
# $HOME/.agent-locks/device-phone-a/slot-1/owner   (written by tools/agent-lock.sh)
holder=L2-ui
pid=48213
started=2026-11-21T14:05:00Z
purpose=ui-suite build 57
project=<repo name>
max_s=3600
# Owner hold: the file $HOME/.agent-locks/device-phone-a/OWNER_HOLD. No agent creates or removes it.
```

Full templates (AGENTS.md skeleton, CLAUDE.md pointer, role files, ledger rows, lock script, gate script and manifest, evidence check, cross-model review prompt, night-lane report): references/harness-templates.md. Read it when creating or repairing any part of the harness.

## Technical Reference

### How each tool loads rules and skills (as of 2026-11; verify)

| | Claude Code | Codex CLI |
|---|---|---|
| Rule files | CLAUDE.md and CLAUDE.local.md; AGENTS.md only when neither exists in the working directory or above (setting claude-md-or-agents-md; alternatives claude-md-and-agents-md, claude-md). Never reads AGENTS.override.md or anything under .agents/ | Global: AGENTS.override.md else AGENTS.md in ~/.codex. Project: repo root down to the working directory, one file per directory (AGENTS.override.md, then AGENTS.md, then project_doc_fallback_filenames), concatenated root-first so closer files win, capped by project_doc_max_bytes (32 KiB default) |
| Skills | ~/.claude/skills, .claude/skills, nested .claude/skills, plugins; invoked /skill-name; listing about 1% of context, description truncated at 1,536 chars | .agents/skills from the working directory up to the repo root, $HOME/.agents/skills, $CODEX_HOME/skills (default ~/.codex/skills; still read by CLI 0.170 and used by its own skill installer), /etc/codex/skills; invoked $skill-name or /skills, or implicitly; listing 2% of context or 8,000 chars, descriptions shortened first |
| Custom agents | Subagents with their own model; built-in Explore is read-only | TOML in ~/.codex/agents or .codex/agents: name, description, developer_instructions; optional model, model_reasoning_effort |
| Parallel work | Agent view (preview), --worktree and .worktreeinclude, /batch over 5-30 worktree subagents, background bash | Subagents; Ultra effort splits work across subagents |
| Review hook | - | A "## Code Review Rules" section in AGENTS.md drives Codex reviews on GitHub |

AGENTS.md is an open format also read by Cursor, Gemini CLI and Copilot's coding agent (https://agents.md/). Sources: https://code.claude.com/docs/en/memory, https://code.claude.com/docs/en/skills, https://code.claude.com/docs/en/agents, https://code.claude.com/docs/en/sub-agents, https://learn.chatgpt.com/docs/agent-configuration/agents-md.md, https://learn.chatgpt.com/docs/build-skills.md, https://learn.chatgpt.com/docs/agent-configuration/subagents.md.

### Capacity numbers (one workstation)

| Parameter | Value | Why |
|---|---|---|
| Heavy jobs at once | about 2; one full test suite | A load average several times the core count produced false wall-clock failures; at extreme load the host froze and killed every run; many simulators at once overheated a laptop |
| Implementation lanes per owner | 3-4 (about 10 agents including light ones) | Merge, review and owner attention run out next |
| Test workers on a shared host | 1 | Parallel workers turn load into timeouts; one runaway worker pool spawned thousands of processes within minutes and exhausted memory |
| Per-test timeout | about 60 s, for hangs | Raising it for load hides hangs and keeps the load |
| Claim goes stale | 2 h unless its pid is alive | Long enough for a build, short enough to recover a dead lane overnight |
| Failures before BLOCKED | 3 | After that, split or ask |
| Verifier audit | every ~50 completed tasks, alone | Catches drift in done records cheaply |
| Device turn | 60 min or less, with watchdog | A dead turn held a shared phone overnight |
| Receipt length | about 200 words, script-enforced | Long receipts cost tokens and hide the result |
| Root AGENTS.md | well under 32 KiB (aim 8-12 KiB) | Nested AGENTS.md files share Codex's cap |
| Disk floor | largest build plus caches; about 100 GB on a mobile build host | Full disks killed archive exports and perf runs |
| Agent logs | rotate daily | Unrotated agent logs can grow by gigabytes a day |

All values are [heuristic] from practice unless a vendor doc is cited.

### Model tiers (as of 2026-11; verify) [inference]

| Role | Claude | OpenAI | Google |
|---|---|---|---|
| Plan, architecture, hard review | claude-opus-5-5 (escalate: claude-fable-5-2) | gpt-6.2-astra | gemini-4-carbon, gemini-4-neon |
| Bulk implementation | claude-sonnet-5-5 | gpt-6.2-sol | gemini-4-hydrogen |
| Triage, search, extraction | claude-haiku-5-5 | gpt-6-luna | gemini-3.5-flash-lite |
| Visual work, computer use | claude-opus-5-5 | gpt-6.1-terra | - |

kimi-k3.1-pro is a further implementer option. Prices, aliases, retirements, conflicts and sources: references/model-routing.md (read before pinning IDs or changing a lane's model).

## Diagnostics

| Symptom | Likely cause | Fix |
|---|---|---|
| Host freezes; every lane's run is killed | Heavy jobs uncapped | 2 heavy slots, one full suite, load ceiling checked before start |
| Tests time out only when lanes run together | Load, not code | One test worker; timeouts for hangs; record load; rerun alone before filing a bug |
| Two lanes write the same decision or ticket number | Numbering from "last + 1" in separate worktrees | Reserved number blocks; ticket creation under a lock |
| Asset IDs flip back and forth; manifest rows vanish | No single owner for a choke-point file; concurrent writers | One owner lane; other lanes append request rows under a lock |
| Done record fails re-check | Builder reported belief; suite ran out of memory; a pipe hid the exit code | Verifier re-runs from the manifest; pipefail in every gate; evidence must be tracked |
| Gate stays green on old evidence | Gate result not tied to SHA and content hash | Full SHA, dirty flag and content hash in the manifest; refuse a mismatch |
| Release gate refuses: HEAD moved | A lane committed to the integration branch mid-gate | Serial gate under a lock that blocks commits to that branch |
| Lint or IP scan flags every lane's files | Worktrees nested inside the repo | Worktrees outside the tree or excluded from scans |
| Every lane stops at once | One shared usage window, or a kill by name pattern | Spread plans and vendors; resume notes; kill by pid only |
| Night lane returns nothing; tickets stay In Progress | No end-of-lane report; claims never fold | Morning report required even on failure; stale claims fold; reconcile by diff |
| Another project's gate dies mid-run | Simulator host app quit, or a shared simulator deleted | Never quit the host app; lock files; delete only your own simulators |
| An agent drove a phone during another project's run | Positional lock parser read the time field as the pid | key=value lock files parsed by key; pid liveness; owner hold |
| Another project's caches disappeared | Janitor matched by pattern, not by owner | Clean only paths your project created |
| Paid generation ran during verification | Brief held the generating command; a flag read at one position | Check form only in briefs; tools default to dry-run and reject misplaced flags |
| Agents follow rules that changed yesterday | Rules edited while sessions ran | Live state in dated handoff files; restart sessions after a rules change |
| Quality or cost of a lane changed overnight | Alias moved, or resolves differently on this provider | Pin full IDs; verify the served model at lane start |
| Branches pass alone, break after merge | No test run on the integration branch | Merge guard and tests after every merge |
| CI idle for weeks | Lane branches never pushed, or runner stalled | Push lanes; alert when CI is silent |
| Bad session leaves nothing to roll back to | Days of uncommitted work in one shared tree | Commit to the task branch at each green step; worktree per lane |
| Owner rejects work every gate passed | Feel accepted on machine checks | Owner playtime cap; one unassisted human attempt per acceptance |
| Harness work exceeds product work | Receipts and reviews that catch nothing | Prune by what each piece caught last month |

## Anti-Patterns

**Machine-Certified Fun** — feel-bearing work accepted because every machine check passed. Agents produce faster than the owner can play; a feel-bearing spike that passed every machine check was rejected by the owner in play.

**The Process Tax** — receipts, SHA admissions and multi-agent reviews that cost more than they caught. Work that passed independent review can still fail the owner's first play on device.

**The Scattered Rulebook** — rules split across CLAUDE.md, an operating brief, a README and agent memory outside the repo. Each tool reads a different subset.

**The Restating Pointer** — a CLAUDE.md that copies AGENTS.md with small differences, creating two authorities.

**Load-Scaled Timeouts** — raising test timeouts until a loaded host passes. Hangs hide and the load stays.

**The Pattern Kill** — killing processes by name to free the machine, which stops every agent job and every other project's run.

**The Helpful Janitor** — deleting caches, simulators or build products the agent did not create.

**The Live Trigger** — a brief or ledger row holding the generating form of a paid or irreversible command, ready for any verifier to run.

**Alias Pinning** — "opus" or "haiku" in a config that must behave the same next week, or on another provider.

**One Clock for All Lanes** — every lane on one plan's usage window, so one limit stops all work and loses in-flight state.

**Self-Certified Done** — the builder's own done record accepted without a re-run from the manifest.

## Quality Checklist

- [ ] One AGENTS.md; every other rules location deleted or reduced to a pointer; Claude Code's read mechanism named
- [ ] Root rules file well under Codex's 32 KiB cap; live state in dated handoff files
- [ ] Write scopes per lane; exactly one owner per choke-point file; only the integration owner bumps versions
- [ ] Ledgers append-only with union merge; reserved number blocks per lane; ticket creation locked
- [ ] Claims written before work, folded after 2 h unless the pid is alive; claims reconciled against diffs
- [ ] One label set; missing metrics reported as not measured; manifests carry full SHA, dirty flag, content hash
- [ ] Ledger refuses untracked evidence; simulator and loaded-host numbers marked directional
- [ ] Approval records quote the owner verbatim with cap, plan hash and expiry; briefs carry only check forms
- [ ] Heavy slots about 2, one full suite, single-worker tests, load and memory recorded per capture
- [ ] Device and simulator locks are key=value with pid check, 60-minute turns, watchdog and owner hold
- [ ] No pattern kills, no simulator host app quits, cleanup scoped to own project; disk floor set
- [ ] Worktrees outside scans; tests re-run on the integration branch after every merge; branches pushed
- [ ] Resume note in every spec; lanes spread across usage windows
- [ ] Model IDs pinned and served model verified; cross-model read-only review for risky work
- [ ] Feel-bearing acceptance capped by owner playtime; harness pruned on a schedule

## Related Skills

- gamedev-coordinator splits features into packages; this seat runs the lanes that execute them.
- gamedev-brief-coordinator writes each lane's brief against the standing rules defined here.
- gamedev-qa-verifier owns fail-closed harnesses, fix verification and device matrices; gamedev-delivery-release owns the upload lane and store read-backs.
- gamedev-reviewer runs the cross-model read-only review; gamedev-assessment-manager runs scheduled reassessments.
- gamedev-producer owns the owner-playtime cap and milestone acceptance.
- gamedev-ai-asset-pipeline owns spend journals and provenance for paid generation; gamedev-llm-features-engineer owns LLM features inside the game.
- The engine seats (gamedev-unity-engineer, gamedev-godot-engineer, gamedev-react-native-engineer, gamedev-ios-engineer, gamedev-android-engineer) own the build and test commands the gates call; gamedev-optimization-compatibility owns device perf runs.
