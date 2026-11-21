# Harness Templates

Read when creating or repairing a repo's agent harness. Copy, then cut what your fleet size does not need (SKILL.md, "Harness size by fleet"). Paths are repo-relative; host-wide locks live under $HOME so every project and worktree on the machine shares them. Tool facts are as of 2026-11; verify (sources in SKILL.md Technical Reference).

## 1. AGENTS.md skeleton (the only required read)

```markdown
# AGENTS.md: standing rules for every agent session

This is the only rules file. CLAUDE.md only points here. Live state is in docs/handoff/
(newest dated file). This file changes only between sessions; if it changed after your
session started, finish your step, write your resume note and stop.

## Read first
1. This file. 2. The newest docs/handoff/HANDOFF-<date>.md. 3. Your task spec and its resume note.
Source beats docs: when they disagree, trust src/ and append a ledger row about the mismatch.

## Never
- Read, print or copy .env files or secrets. A worktree sources the main checkout's .env in a subshell.
- Run a paid call, upload, store action, deploy, production query, external-tester invite or
  phone turn without an approval record in ledger/approvals.jsonl. Submit, deploy and phone use
  also need the owner's exact word in the current turn.
- Weaken, skip or delete a test, gate config, golden file or balance seed to make a gate pass.
- Report unrun work as run. A missing metric is "not measured", never 0.
- Spawn workers recursively. Kill processes by name pattern. Quit the simulator host app.
- Delete or clean anything your project did not create (simulators, caches, build products).
- Commit anywhere but your own task branch, or push, unless your task says so. Do commit to your task branch at
  each green step (explicit paths only), so every session leaves a rollback point. Never bump versions (L0 does).
- Keep harness and release scripts outside the repo. They live in tools/; only lock state lives under $HOME.

## Gotchas
- <one line per trap this repo has already hit, with the decision ID that recorded it>

## Completion labels (every task ends with exactly one)
VERIFIED | IMPLEMENTED — VERIFICATION PENDING | BLOCKED (blocker + next action) | DEFERRED (reason)
Evidence level in the note: compiled / tested / observed on <device>. Only a verifier in a
fresh session writes VERIFIED, from a gate manifest. Status lines describe your own work only.
Simulator numbers and numbers from a loaded host are directional.

## Gates
- tools/gate.sh <gate>: serial, under the suite lock, writes gates/<full sha>/<gate>.json.
- Targeted gate per task; the full blocking gate before any upload. Known failures are listed
  one per line with a reason in gates/known-failures.txt; anything else fails.
- Evidence cited in a ledger row must be tracked by git (tools/check-evidence.sh).

## Write scopes and choke points
| Path | Owner lane |
|---|---|
| <project file>, <lockfile>, version and build number | L0 |
| <string catalog> | L2 (others append a request row) |
| docs/DECISIONS.md | append-only, numbers from your lane's block |

## Ledgers (append-only; .gitattributes: ledger/*.jsonl merge=union)
- ledger/tasks.jsonl: claim before work; heartbeat each step; stale claims fold after 2 h.
- docs/DECISIONS.md: reversals are new rows; owner quotes verbatim; every row has "reverse by".
- ledger/questions.jsonl: product questions become ASSUMED rows; keep working.
- Number blocks: ledger/number-blocks.md. Ticket creation: tools/agent-lock.sh tickets 1 ...

## Host capacity and locks
- Heavy work (build, full suite, simulator, engine editor) only through tools/agent-lock.sh:
  build 1 slot, suite 1, test 2, sim 1. Tests run with one worker.
- Before heavy work: load average under <n>, free disk over <GB>; otherwise wait.
- Phones and simulators: tools/agent-lock.sh device-<alias> 1 "<purpose>" with AGENT_LOCK_MAX_S=3600;
  never while an OWNER_HOLD file sits in that lock dir. Warn other sessions before long UI runs.

## Worktrees
- One worktree per task outside the repo tree (../wt/<lane>-<task>); branch task/<id>.
- Merge into integ/build-<NN>; the merge guard (tools/merge-guard.sh) runs after every merge.
- Push your branch when the task ends.

## Usage limits and handoff
- Keep the resume note at the top of your spec current after every step; write it for a
  session on another account or model.
- On a limit or crash warning: write the resume note, release locks, append a ledger row.

## Models
- Pinned IDs per role are in docs/agents/models.md. Log the served model in your first
  ledger row; stop on a mismatch.

## Code Review Rules
(Codex reads this section for reviews on GitHub.)
- Read-only. Cite file:line or an evidence row for every finding. Label each finding
  confirmed / source-derived / reconstruction.
```

## 2. CLAUDE.md pointer

Claude Code reads AGENTS.md on its own only when no CLAUDE.md or CLAUDE.local.md exists (setting claude-md-or-agents-md; claude-md-and-agents-md loads both). If the repo needs a CLAUDE.md, keep it to this:

```markdown
# CLAUDE.md
Before anything else, read AGENTS.md in the repo root and follow it. It is the only rules file.
Do not add rules here.
```

## 3. Role files, generated from one source

Keep roles in one table (docs/agents/roles.md: name, purpose, write scope, model, effort) and generate both tool formats from it, so they cannot drift.

Codex (.codex/agents/verifier.toml; required name, description, developer_instructions):

```toml
name = "verifier"
description = "Re-runs a claimed task's gates from its manifest in a fresh session; read-only except ledger/verifications.jsonl."
developer_instructions = """
Read AGENTS.md. For the task named in your prompt: check out the manifest's full SHA read-only,
re-run the gate under tools/agent-lock.sh, compare every step with the manifest, and append one
verification row with VERIFIED or the failing step. Never edit source. Never run paid or gated commands.
"""
model = "gpt-6.2-astra"
model_reasoning_effort = "high"
```

Claude Code (.claude/agents/verifier.md): the same name, description and instructions as a markdown subagent file with a pinned model; check that your Claude Code version accepts a full model ID in the subagent model field, and otherwise verify the served model at start.

## 4. Ledger rows

### Task queue (ledger/tasks.jsonl; last record per id wins)

```json
{"id":"T-0231","ev":"created","by":"L0","at":"2026-11-21T09:00:00Z","title":"Pause during hit-stop resumes at scale 0","scope":["src/combat/**"],"spec":"docs/tasks/T-0231.md"}
{"id":"T-0231","ev":"claimed","by":"L1","session":"s-7f3a","pid":48213,"host":"host-a","model_requested":"<pinned id>","model_served":"<reported id>","at":"2026-11-21T09:05:00Z"}
{"id":"T-0231","ev":"heartbeat","by":"L1","pid":48213,"host":"host-a","at":"2026-11-21T10:10:00Z"}
{"id":"T-0231","ev":"done","by":"L1","label":"IMPLEMENTED — VERIFICATION PENDING","level":"tested","sha":"<40-hex sha>","evidence":["gates/<40-hex sha>/targeted.json"],"at":"2026-11-21T10:40:00Z"}
{"id":"T-0231","ev":"verified","by":"V1","label":"VERIFIED","manifest":"gates/<40-hex sha>/targeted.json","at":"2026-11-21T12:00:00Z"}
{"id":"T-0232","ev":"failed","by":"L2","n":3,"why":"suite out of memory on step unit","at":"2026-11-21T12:30:00Z"}
```

Third failure: append `{"ev":"blocked"}` with the next action. Oversized: append `{"ev":"split","into":["T-0232a","T-0232b"]}`.

Stale-claim fold (run under the ledger lock at each wave start and from the morning report):

```python
# tools/fold_claims.py: append "folded" rows for claims older than 2 h whose pid is gone
import datetime, json, os, socket, time
STALE_S, LEDGER = 2 * 3600, "ledger/tasks.jsonl"
last = {}
with open(LEDGER) as f:
    for line in f:
        if line.strip():
            r = json.loads(line); last[r["id"]] = r          # last record per id wins
def alive(r):
    if r.get("host") != socket.gethostname(): return True   # other host: cannot check from here
    try: os.kill(int(r["pid"]), 0); return True
    except (OSError, ValueError, KeyError): return False
now = time.time()
with open(LEDGER, "a") as out:
    for tid, r in last.items():
        if r["ev"] not in ("claimed", "heartbeat"): continue
        at = datetime.datetime.fromisoformat(r["at"].replace("Z", "+00:00")).timestamp()
        if now - at > STALE_S and not alive(r):
            stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            out.write(json.dumps({"id": tid, "ev": "folded", "from": r["by"], "at": stamp}) + "\n")
```

A folded task is pending again; the next claimant reads the resume note first and reconciles the dead lane's diff (git status in its worktree, file timestamps) before starting.

### Decision log (docs/DECISIONS.md, append-only)

```
| ID | Date | Decision | Why (evidence) | Owner quote (verbatim) | Reverse by | Supersedes |
|----|------|----------|----------------|------------------------|------------|------------|
| D-312 | 2026-11-21 | Sim draws only the newest state at 4x speed | Device run gates/<sha>/perf.json | "<quote>" | 2026-12-15, or p95 over budget on the floor device | D-207 |
```

### Number blocks (ledger/number-blocks.md)

```
| Lane | Decisions | Constants | Questions | Tickets |
|------|-----------|-----------|-----------|---------|
| L0   | D-000..099 | K-000..099 | Q-000..099 | T-0000..0999 |
| L1   | D-100..199 | K-100..199 | Q-100..199 | T-1000..1999 |
```

### Question (ledger/questions.jsonl)

```json
{"id":"Q-104","by":"L1","status":"ASSUMED","question":"Does pause freeze the combo timer?","assumption":"Yes; timer uses gameplay time","reversible":"one constant","at":"2026-11-21T09:30:00Z"}
```

### Approval (ledger/approvals.jsonl)

```json
{"id":"A-014","action":"upload","target":"build 57 internal testing","owner_said":"<verbatim quote>","channel":"chat","turn_at":"2026-11-21T15:02:00Z","cap":"1 upload","plan_sha256":"<hash of the command list shown>","expires":"2026-11-21T18:00:00Z","used_by":null,"readback":null}
```

The tool that runs the action fills used_by and readback (the state read from the store or API afterwards), and refuses a record that is expired, already used, or whose plan hash differs from the commands it is about to run.

## 5. Lock script (host-wide mkdir slots)

```bash
#!/usr/bin/env bash
# tools/agent-lock.sh: run a command while holding one of N slots of a named host-wide lock.
#   tools/agent-lock.sh suite 1 "full suite T-0231" -- npm test -- --maxWorkers=1
#   AGENT_LOCK_MAX_S=3600 tools/agent-lock.sh device-phone-a 1 "ui suite build 57" -- ./run-ui.sh
# mkdir is atomic on a local filesystem. All lanes must run as the same OS user, because
# kill -0 cannot see another user's processes. A file named OWNER_HOLD in the lock dir
# refuses every agent until the owner deletes it.
set -euo pipefail
name=$1; slots=$2; purpose=$3; shift 3
[ "${1:-}" = "--" ] && shift
root="${AGENT_LOCK_ROOT:-$HOME/.agent-locks}/$name"
mkdir -p "$root"
SLOT=""

owner_pid() { sed -n 's/^pid=//p' "$1/owner" 2>/dev/null | head -n 1; }

fold_if_stale() {                      # free a slot whose holder process is gone
  local d=$1 pid
  pid=$(owner_pid "$d")
  if [ -z "$pid" ]; then               # owner not written yet: give the writer a minute
    [ -n "$(find "$d" -maxdepth 0 -mmin +1 2>/dev/null)" ] || return 0
  elif kill -0 "$pid" 2>/dev/null; then
    return 0
  fi
  [ "$(owner_pid "$d")" = "$pid" ] || return 0      # re-check just before removing
  if mv "$d" "$d.stale.$$" 2>/dev/null; then
    rm -rf "$d.stale.$$"
    echo "agent-lock: folded stale $name slot (pid ${pid:-none})" >&2
  fi
}

acquire() {
  local i d
  for i in $(seq 1 "$slots"); do
    d="$root/slot-$i"
    if mkdir "$d" 2>/dev/null; then
      printf 'holder=%s\npid=%s\nstarted=%s\npurpose=%s\nproject=%s\nmax_s=%s\n' \
        "${AGENT_LANE:-unknown}" "$$" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$purpose" \
        "$(basename "$PWD")" "${AGENT_LOCK_MAX_S:-none}" > "$d/owner.tmp"
      mv "$d/owner.tmp" "$d/owner"
      SLOT=$d; return 0
    fi
    fold_if_stale "$d"
  done
  return 1
}

deadline=$(( $(date +%s) + ${AGENT_LOCK_WAIT_S:-3600} ))
while :; do
  if [ -e "$root/OWNER_HOLD" ]; then echo "agent-lock: $name is on owner hold" >&2; exit 75; fi
  acquire && break
  if [ "$(date +%s)" -ge "$deadline" ]; then
    echo "agent-lock: no free $name slot after ${AGENT_LOCK_WAIT_S:-3600} s" >&2; exit 75
  fi
  sleep "${AGENT_LOCK_POLL_S:-15}"
done

child=""; watchdog=""
cleanup() {
  [ -n "$watchdog" ] && kill "$watchdog" 2>/dev/null || true
  [ -n "$SLOT" ] && rm -rf "$SLOT"
}
trap cleanup EXIT
trap '[ -n "$child" ] && kill -TERM "$child" 2>/dev/null; exit 130' INT TERM

"$@" & child=$!
if [ -n "${AGENT_LOCK_MAX_S:-}" ]; then     # watchdog: device turns and long suites
  ( sleep "$AGENT_LOCK_MAX_S"; kill -TERM "$child" 2>/dev/null ) & watchdog=$!
fi
rc=0; wait "$child" || rc=$?
exit "$rc"
```

Rules around it:
- Slot counts are policy, set once in AGENTS.md: build 1, suite 1, test 2, sim 1, engine editor 1, image job 1, tickets 1, ledger 1.
- Stop a lane by sending TERM to the pid in its lock's owner file; the script stops its child and frees the slot. Never kill by name pattern.
- A device turn's watchdog must also restore the owner's build on the phone; put that in the turn's own cleanup, not in the lock script.
- Run heavy commands at background priority inside the lock: nice -n 10, or taskpolicy -c utility on macOS.
- Shut down simulators by their own ID (xcrun simctl shutdown with the ID you booted), never with "all", and never quit the simulator host app.

## 6. Gate script and manifest

```bash
#!/usr/bin/env bash
# tools/gate.sh <gate>: run a gate's steps serially and write gates/<full sha>/<gate>.json
# Steps live in tools/gates/<gate>.steps (part of the hashed subject), one "name|command" per line. Each step's output goes to a
# log file by redirection, never through a pipe, so its exit code is the command's own.
set -euo pipefail
gate=$1
sha=$(git rev-parse HEAD)
# Evidence and ledgers are excluded, so committing a manifest or a ledger row keeps the same hash.
content() {
  { git ls-tree -r HEAD | awk -F'\t' '$2 !~ /^(gates|ledger)\//'
    git diff --binary HEAD -- . ':(exclude)gates' ':(exclude)ledger'; } | shasum -a 256 | cut -d' ' -f1
}
load1() { uptime | awk -F'load averages?: ' '{split($2, a, /[ ,]+/); print a[1]}'; }
dirty=false
[ -z "$(git status --porcelain --untracked-files=no -- . ':(exclude)gates' ':(exclude)ledger')" ] || dirty=true
c0=$(content); out="gates/$sha"; mkdir -p "$out/$gate"
started=$(date -u +%Y-%m-%dT%H:%M:%SZ); load_start=$(load1)
steps=""; verdict=pass; ran=0
while IFS='|' read -r step cmd || [ -n "$step" ]; do    # also reads a last line without newline
  [ -z "$step" ] && continue
  ran=$((ran + 1)); rc=0; bash -c "$cmd" > "$out/$gate/$step.log" 2>&1 < /dev/null || rc=$?
  [ "$rc" -eq 0 ] || verdict=fail
  steps="$steps{\"name\":\"$step\",\"exit\":$rc,\"log\":\"$out/$gate/$step.log\"},"
done < "tools/gates/$gate.steps"
[ "$ran" -gt 0 ] || { verdict=fail; echo "gate: no steps ran" >&2; }
[ "$(git rev-parse HEAD)" = "$sha" ] || { verdict=fail; echo "gate: HEAD moved during the gate" >&2; }
[ "$(content)" = "$c0" ] || { verdict=fail; echo "gate: tree changed during the gate" >&2; }
printf '{"gate":"%s","sha":"%s","dirty":%s,"content_sha256":"%s","started":"%s","finished":"%s","load_1m":[%s,%s],"steps":[%s],"verdict":"%s"}\n' \
  "$gate" "$sha" "$dirty" "$c0" "$started" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  "$load_start" "$(load1)" "${steps%,}" "$verdict" > "$out/$gate.json"
[ "$verdict" = pass ]
```

Run it under the suite lock: `tools/agent-lock.sh suite 1 "gate targeted" -- tools/gate.sh targeted`. Manifest rules:
- The verdict is the AND of every step plus "at least one step ran", "HEAD unchanged" and "content unchanged"; a summary line never overrides a failed step.
- Name gate results by the full 40-character SHA; anything matched by prefix is refused by the upload lane.
- A dirty-tree manifest is evidence for the lane, never for an upload. The content hash excludes gates/ and ledger/, so committing evidence keeps it; the archive step recomputes it at its own HEAD and refuses a mismatch with the manifest it cites.
- Add per-step counts where the runner reports them (tests_expected, tests_counted, skipped, todo); counted below expected fails the step, because restarts and crashed bundles lose tests silently.
- Record the served model and lane in the ledger row that cites the manifest, not in the manifest.

## 7. Evidence check (ledger refuses untracked evidence)

```bash
#!/usr/bin/env bash
# tools/check-evidence.sh <path>...: fail if any cited evidence is untracked or ignored
bad=0
for p in "$@"; do
  if ! git ls-files --error-unmatch -- "$p" > /dev/null 2>&1; then
    echo "evidence not tracked by git: $p" >&2; bad=1
  fi
done
exit "$bad"
```

Call it from the ledger writer for every evidence path in a done or verified row. Gitignored logs (*.log) are the usual offender: commit a trimmed copy under gates/ or cite the manifest instead.

## 8. Merge guard (after every merge into the integration branch)

```
1. agent-lock test 2: typecheck + targeted tests for every path the merge touched
2. tools/check-evidence.sh on every evidence path added by the merged ledger rows
3. Duplicate-ID check: no decision, constant, question or ticket ID appears twice
4. Choke-point check: files outside the merging lane's write scope changed -> refuse
5. Append a merge row: lane, branch, merged SHA, guard result
```

## 9. Night-lane morning report (written even when the lane failed)

```
NIGHT LANE  L3   window <start>-<end>   model <served id>   plan <account>
CLAIMED     T-... (state per task: done / folded / blocked)
COMMITS     <sha list> or none        DIFF SINCE START  <files>
GATES       gates/<sha>/<gate>.json verdicts, or "not run" with why
STOPPED BY  completed | usage limit at <time> | crash | lock timeout | owner hold
NEXT        first command for the day session; resume notes updated: yes/no
```

## 10. Receipt (script-capped at about 200 words)

```
T-0231  IMPLEMENTED — VERIFICATION PENDING (tested)
Changed: src/combat/TimeScale.cs, tests/combat/PauseInFreezeTests.cs
Gate: gates/<full sha>/targeted.json pass (12/12 steps)
Not measured: device frame time (no phone turn approved)
Assumed: Q-104
Next: verifier re-run; owner check on device
```

## 11. Cross-model read-only review prompt

```
You are a read-only reviewer from a different model family than the builder.
Subject: <full sha>, task T-0231, manifest gates/<sha>/targeted.json, spec docs/tasks/T-0231.md.
Do not edit, commit, install or run gated commands. You may re-run read-only checks and re-measure
from saved evidence files.
For each finding give: file:line or evidence row, severity (blocker/major/minor), problem, fix,
and a basis label: confirmed (reproduced now), source-derived (read from code, not run),
reconstruction (inferred from logs or reports). Load gamedev-reviewer for severity rules.
End with counts by severity and the findings that block acceptance.
```

## 12. Janitor (own project only)

- Scope every delete to paths recorded as created by this project: its worktrees, its derived-data and build folders, its simulators (IDs logged at creation), its caches under the repo or under a project-named directory.
- Never match by pattern across $HOME or system caches; another project's cache can share a name.
- Rotate agent and gate logs daily; keep gate manifests and the logs they cite.
- Refuse heavy work below the disk floor and report free space in the morning report; check phone free space before installs and perf runs.
