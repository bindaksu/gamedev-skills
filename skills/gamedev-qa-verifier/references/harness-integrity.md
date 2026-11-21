# Harness Integrity, Runner Quirks and Visual Baselines

Read when writing or auditing a test runner, a release gate script or a screenshot baseline. Tool behavior below was observed on Xcode 27.2 with iOS 27.x simulators and devices (as of 2026-11; verify on your toolchain).

## 1. Fail-closed harness contract

| Rule | Why |
| --- | --- |
| Default exit status is nonzero; only a fully parsed, complete result sets 0 | A crashed launcher, a typo in a flag or an empty results file otherwise reads as green |
| Distinct exit codes: e.g. 1 failed checks, 2 timeout, 3 missing exit status, 4 malformed or empty results, 5 missing artifact | Triage starts from the code, and a gate can treat each class differently |
| Every requested sequence or test produces a manifest row naming its expected checks | A mistyped sequence name silently skipped every check in one runner |
| Launch the binary directly; never through a desktop opener, `open`, or a wrapper whose last step is a file move | One wrapper returned the exit code of the step that moved the evidence folder, so failing captures exited 0 |
| `set -euo pipefail` in every shell step | Pipes hide the producer's exit code |
| Watchdogs run on unscaled wall time | A watchdog on game time stops when the game pauses or hit-stop scales time |
| Flags are validated: unknown or misplaced flags abort, and owner-gated steps default to dry-run | A check-only flag read from the wrong argument position started a paid generation |
| Verdict = AND of all steps, derived from individual results | A summary reported "all passed" alongside failed checks |
| Totals summed across every test bundle; tests lost to runner restarts count as failures | One gate manifest counted about half the tests that existed |
| Gate output names the full commit hash, tree state (clean/dirty) and content hash of what was tested | A prefix match once accepted "1" as a commit; an archive must match the hash the gates recorded |

## 2. Controls

- Before a new check is trusted, run it against a control: the pre-fix build, or a seeded defect. A check that cannot fail is not a check.
- Tests call the production function. A test that feeds the function's expected output to the assertion proves nothing.
- Count starts and completions as separate events (a death that started is not a completed death).
- Sensory checks measure output: an audio master-bus peak probe that fails at -60 dB or lower; pixel or OCR checks for visuals. Load counters and "asset loaded" logs do not prove the player hears or sees anything.

## 3. iOS automation quirks (XCUITest, simulators)

- On iOS 27.2 simulators, `isHittable` reported false for buttons inside SwiftUI `ScrollView` overlays; check reachability by the element's frame against the window instead.
- Trace and UI-test with the Xcode whose major version matches the device OS [inference]; Xcode 26.4 could not run XCUITest on iOS 27 phones.
- Read back the simulator's Content Size and Increase Contrast settings before accessibility cells; an OS-level poll in the app can silently undo a value a test pinned.
- Use accessibility identifiers, not English labels, in localized runs.
- Pin the simulator runtime used for gesture automation and re-check after each OS update that scripted strokes still reach the handler.
- Never quit the simulator host app from a test or a cleanup script: it shuts down every simulator, including other sessions' runs.

## 4. Maestro (React Native and native views)

- An element below the fold but inside the screen bounds reports as visible; scroll it into view before asserting.
- No multi-pointer command: test pinch and two-finger gestures in XCUITest (or Espresso), with one control case that should pass and one that should fail.
- Keep flows in the same change as the UI they drive; a release smoke failed on outdated flows, not on the app.

## 5. Visual baselines

- Pin OS accessibility state (text size, contrast, reduce motion), locale, and clocks before capture.
- Tolerances that held up in practice: about 12/255 per channel and 0.4% changed pixels (heuristic; tune per art style).
- A person looks at every updated baseline; an automated "accept new baseline" defeats the test.
- Waivers name the full commit hash and a reason; changed pixels mean a recapture, not a carried-over waiver.

## 6. Shared hosts

- One test worker per suite on a shared machine; set timeouts to catch hangs (e.g. 60 s per test), not to absorb load.
- Record host load with every gate run; failures under load average far above core count are infrastructure, not product, and are rerun, not waived [inference; a load average several times the core count once produced a run of false wall-clock failures].
- Over-deadline proofs move to an opt-in lane unchanged; never shorten them to fit the gate.
- Locking, lane caps and owner approvals for agent sessions: gamedev-agentic-production.
