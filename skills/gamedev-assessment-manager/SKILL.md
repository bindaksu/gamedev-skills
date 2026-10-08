---
name: gamedev-assessment-manager
description: >-
  Run a full, scored assessment of a game build as a numbered edition: ten
  dimensions scored 0-10 on a machine-provable evidence rubric, each with a
  ceiling and a delta against the previous edition, produced by parallel
  read-only lens reviews that load the pack's specialist skills, then verified
  at file and line, with a verdict, top moves N1-Nn, a release blocker list, an
  as-built revenue model, and a published page updated in place. Use when the
  user asks to assess, score, audit or re-assess a game, wants the next edition
  of an existing assessment, asks will this game succeed, or wants a scorecard
  before a release or after a batch of fixes.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: meta
---

# Assessment Manager

An assessment is a measurement, not a review. Its value is that the next edition can say exactly what moved and why. That requires three things held constant across editions: the **subject** (a named build and commit, not "the game"), the **rubric** (what evidence earns each score), and the **dimensions**. Everything else (lenses, depth, page design) can change. A score that cannot be traced to evidence at a file, gate, or measurement is an opinion; an assessment made of opinions drifts toward whatever the last conversation felt like.

The default rubric scores what the machine can prove. Human playtests are valuable, but their absence is not scored as a defect unless the owner asks for it: docking every edition for "no human has played it" makes every edition read the same and hides the real gate and evidence gaps.

## Role Profile

The studio equivalent is the greenlight or milestone review that a GM, executive producer, or publishing lead runs before soft launch, global launch, or a funding decision (Supercell's kill-or-continue calls, Dream Games' 19-month soft launch for Royal Kingdom, Lilith's retention gate). Those reviews pull one senior voice per discipline, demand data over taste, and end in a decision and a short list of what must change. This skill reproduces that panel with lens reviews built from the pack's specialist skills and keeps the result comparable edition to edition.

## When to Use / Not

Use for: first assessment of a game; the next edition after fixes; a pre-release scorecard; "will this succeed"; reconciling an old assessment with the current repo.

Not for: reviewing one diff or doc (gamedev-reviewer); test plans and verifying a single fix (gamedev-qa-verifier); generating the implementation prompt that follows (gamedev-brief-coordinator, assessment-followup mode); kill or greenlight economics alone (gamedev-financial-growth-strategist).

## Inputs to Gather

- **Subject**: app version + build number, commit SHA, branch, dirty-tree status, server revision if separate. Default: current HEAD; record dirty files.
- **Previous edition**: its URL or file, its scores, ceilings and top moves. If none, this is edition 1 and deltas are "—".
- **Run mode**: `full` (lenses + targeted gate re-runs), `read-only` (lenses, no test runs), or `controller-only` (re-score from the delta without lenses, when budget is low). Default: read-only. State the mode on the page.
- **Rubric overrides**: whether human-playtest evidence counts (default: not scored), extra dimensions (e.g. PvP, Live Ops), platforms to score apart.
- **Project truth sources**: AGENTS.md/CLAUDE.md, acceptance ledger or gates file, DECISIONS log, release docs, revenue model script if any.
- **Publishing target**: existing page URL to update in place, or a new page; local markdown path as fallback.

## Method

1. **Pin the subject.** Record build, commit, dirty files. Work from a detached worktree or read-only checkout so the assessment cannot change the repo it measures.
2. **Load the previous edition.** Extract its scores, ceilings, findings and top moves into a list; each becomes a delta row to classify.
3. **Brief the lenses.** Four parallel read-only lens reviews (subagents, worktrees, or sequential passes if parallelism is unavailable). Each gets the subject, its dimensions, its skills to load, the rubric, the previous findings it owns, and the JSON output contract in `references/lens-brief.md`.

   | Lens | Dimensions | Load (pack + companions if installed) |
   |---|---|---|
   | L1 Gameplay | Core loop, Campaign/Content | core-loop-designer, gamedev-campaign-designer, gamedev-combat-designer, gamedev-level-layout-designer, gamedev-pvp-designer, gamedev-simulation-designer, gamedev-narrative-designer |
   | L2 Economy & growth | Economy, Retention, Monetization, revenue model | game-economy-balancer, gamedev-meta-progression-designer, gamedev-growth-designer, gamedev-liveops-designer, gamedev-monetization-designer, gamedev-financial-growth-strategist |
   | L3 Experience | Mobile UX, Art & feel | gamedev-ux-designer, mobile-game-ux-designer, gamedev-ui-designer, gamedev-hud-engineer, gamedev-game-feel-designer, game-asset-art-director, gamedev-audio-designer, gamedev-accessibility-specialist, gamedev-localization-specialist |
   | L4 Engineering & ship | Performance, Evidence, Shippability, platform parity | gamedev-optimization-compatibility, the platform skills in use (gamedev-ios-engineer, gamedev-android-engineer, gamedev-unity-engineer, …), gamedev-qa-verifier, gamedev-delivery-release, gamedev-backend-engineer, gamedev-anti-cheat-security |

4. **Verify.** Re-check every blocker and major claim yourself at its cited file:line, gate row, or measurement. Demote or drop claims that do not reproduce; note "lens claim not verified" rather than silently keeping it. This is the step that makes editions trustworthy.
5. **Classify deltas.** For each previous finding and move: closed, improved, unchanged, worsened, with evidence. A finding is closed only with evidence on this subject, not because a commit message says so.
6. **Score.** Apply `references/rubric.md` per dimension; record the evidence that sets the score, the ceiling (best score reachable with the work already planned or in flight), and the delta. When a previous score was too high, say "recalibrated" and why, so the mean dropping is not mistaken for regression.
7. **Compute** the unweighted mean of scored dimensions and the ceiling mean. Platforms without parity evidence are scored apart and excluded from the mean.
8. **Write the verdict**: one paragraph answering "will it succeed, and what decides it", plus a one-line headline.
9. **Rank top moves** N1…Nn (≤ 9): each names the dimension, expected score lift, the evidence that would prove it, and the owner skill. Order by lift per effort, blockers first.
10. **Release list**: blockers for the next store submission, separate from the moves.
11. **Revenue section** (if a model or enough data exists): as-built MRR/ARR at a stated DAU base, every assumption listed (L2 with gamedev-financial-growth-strategist). Label it a model, not a forecast.
12. **Publish** the edition (page template in `references/page-structure.md`), updating the existing page in place so the URL stays stable; keep a local markdown copy. Save an edition note (URL, subject, scores, top moves) wherever the project keeps durable notes.
13. **Hand off**: offer the follow-up implementation brief via gamedev-brief-coordinator in assessment-followup mode, one task per top move.

## Deliverables

### Scorecard (the core of every edition)

```
Edition <N> · <date> · Subject: <app version> (<build>) @ <sha> [+dirty: n files] · Mode: <full|read-only|controller-only>

| Dimension    | Score | Ceiling | Δ vs <N-1> | Evidence that sets the score                  |
|--------------|-------|---------|------------|-----------------------------------------------|
| Core loop    |       |         |            |                                               |
| Economy      |       |         |            |                                               |
| Retention    |       |         |            |                                               |
| Campaign     |       |         |            |                                               |
| Mobile UX    |       |         |            |                                               |
| Art & feel   |       |         |            |                                               |
| Monetization |       |         |            |                                               |
| Evidence     |       |         |            |                                               |
| Shippability |       |         |            |                                               |
| Performance  |       |         |            |                                               |
| Mean         |       |         |            | Platform scored apart: <platform> <score>     |
```

### Delta table

```
| Prior finding / move | Status (closed/improved/unchanged/worsened) | Evidence on this subject |
```

### Top moves

```
N1 <action> — Dimension: <x> (<score> → <target>) — Proof: <gate/test/measurement> — Owner: <gamedev-…>
```

### Release list

```
| # | Blocker | Why it blocks review/launch | Fix path | Owner |
```

Full page section order, lens JSON contract and the run brief for agents are in `references/` (read `rubric.md` before scoring, `lens-brief.md` before briefing lenses, `page-structure.md` before publishing, `run-brief.md` when another agent will run the assessment).

## Quantitative Reference

Default rubric anchors (all dimensions; per-dimension evidence in `references/rubric.md`):

| Score | Evidence on this subject |
|---|---|
| 0–2 | Missing or broken on the main path |
| 3 | Structural gap: the design or system cannot deliver the dimension as built |
| 5 | Built and reachable, no gate or measurement covers it |
| 6–7 | Built, partial gate (some paths, simulator only, or stale build) |
| 8 | A passing gate covers the main path on this subject |
| 9 | Gate plus measured run on a real device or the full content set |
| 10 | Committed, re-runnable artifact plus a measured instrumented run, both on this subject |

Rules: owner dogfooding on a real device counts as machine evidence when logged. Half points allowed. A gate from an older build counts at most 7 unless the changed files provably do not touch it. Never average away a blocker: a dimension with an open release blocker scores at most 6.

Typical calibration (heuristic): a first edition of a playable build usually lands at a 5–6.5 mean; a store-ready build with gates lands 7.5–8.5; above 9 needs instrumented device runs across most dimensions.

## Diagnostics

| Symptom | Likely cause | Fix |
|---|---|---|
| Every edition reads the same | Scoring on an unchanging factor (no playtests, genre ceiling) | Apply the rubric; move unchanging context to the verdict |
| Mean jumps after a quiet week | Scores followed commit messages, not evidence | Re-verify at file:line; recalibrate and say so |
| Lenses contradict each other | Overlapping dimensions or different subjects | One owner lens per dimension; same SHA for all |
| Top moves never get done | Moves lack proof criteria or owners | Each move names proof and owner skill; hand to brief coordinator |
| Old findings vanish | No delta table | Carry every prior finding forward until closed with evidence |
| Android looks fine because iOS is | Platforms blended | Score platforms without parity apart |
| Page URL changes each edition | New page per run | Update in place; record the URL in the edition note |

## Anti-Patterns

**Vibes Scoring** — numbers set by impression, then justified. Evidence first, number second.
**The Moving Subject** — lenses read different commits or a tree that changes mid-run.
**Docs-as-Evidence** — a design doc or ledger row says "passed"; the gate file says failed. The gate wins.
**Silent Recalibration** — lowering a score without saying the earlier one was too high, so the owner sees a regression that is not one.
**The Human-Factor Cap** — capping every dimension for missing playtests unless the owner asked for it.
**Unverified Lens Claims** — pasting a lens report's criticals onto the page without re-checking them.
**Fifteen Top Moves** — a list too long to act on. Nine at most, ordered.
**Revenue as Forecast** — an as-built model at an assumed DAU presented as expected income.

## Quality Checklist

- [ ] Subject pinned: build, SHA, dirty files, server revision
- [ ] Mode stated (full / read-only / controller-only); no claim of tests that did not run
- [ ] Every previous finding and move has a delta status with evidence
- [ ] Every score cites the evidence that sets it; ceiling and delta filled
- [ ] Blockers and majors verified at file:line by the controller, not only by a lens
- [ ] Recalibrations labeled; platforms without parity scored apart
- [ ] Verdict, ≤ 9 ranked top moves with proof and owner, release list
- [ ] Revenue section labeled as a model with assumptions (or omitted)
- [ ] Page updated in place; local copy and edition note saved
- [ ] Follow-up brief offered

## Related Skills

- gamedev-brief-coordinator — writes the lens briefs and the follow-up implementation brief.
- gamedev-coordinator — routes any top move that spans several disciplines.
- gamedev-reviewer — rubric details for code and design findings inside lenses.
- gamedev-qa-verifier — gate definitions and evidence standards behind the 8–10 scores.
- gamedev-financial-growth-strategist — revenue model and greenlight economics.
- gamedev-producer — turns top moves into milestones; owns kill or continue after the verdict.
