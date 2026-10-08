# Run Brief (for another agent to run the assessment)

Paste and fill. ≈ 300 words.

```
# Assessment edition <N> of <game>

You run a scored assessment of <game> on the subject below and publish edition <N>.
Load skill: gamedev-assessment-manager (follow its Method). Lenses load the skills listed in its lens table.

Subject: <version> (<build>) @ <sha> on <branch>. Work in a detached, read-only worktree. Record dirty files.
Previous edition: <URL or path>; its scores: <list>; its moves: N1…Nn.
Mode: <read-only | full (gates allowed: …) | controller-only>.
Rubric: machine-provable anchors (3/5/8/10). Do not score missing human playtests. Owner dogfood on device counts.
Platforms scored apart: <e.g. Android, until parity evidence exists>.
Truth sources: AGENTS.md, <ledger>, <gates>, <DECISIONS>, <revenue script>.

Deliver:
1. Scorecard (10 dimensions: score, ceiling, Δ, evidence), mean and ceiling mean.
2. Delta table for every prior finding and move.
3. Verdict, top moves (≤ 9, each with lift, proof, owner skill), release list, revenue model if data exists.
4. Page updated in place at <URL> (else new page) + local markdown copy + edition note.

Rules: no edits to the product repo; verify every blocker/major at file:line yourself; label recalibrations;
never report a test or review that did not run.
Finish with: page URL, mean (and Δ), top 3 moves, anything unverified.
```
