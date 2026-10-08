# Edition Page Structure

Read before publishing. Keep the section order stable across editions so readers can compare; restyle freely.

1. **Masthead**: game, "Assessment <roman or number> · <date>", subject (version, build, SHA, dirty files), run mode, previous edition link.
2. **Verdict**: headline line + one paragraph. What decides success; what changed since last edition.
3. **Scorecard**: table from SKILL.md with score, ceiling, Δ, evidence; mean and ceiling mean; platforms scored apart below the table.
4. **Since <previous date>**: delta table (closed / improved / unchanged / worsened), closed items first.
5. **Dimension sections** (one per dimension, same order as the scorecard): what is there, evidence, findings with severity and file:line, what would raise the score.
6. **Top moves** N1…Nn with dimension, lift, proof, owner.
7. **Release list**: blockers before next submission.
8. **Revenue model** (optional): DAU base, ARPDAU or price × conversion assumptions, platform and payment fees, net MRR/ARR; labeled "model".
9. **Method and limits**: lenses run, skills loaded, what was verified by the controller, tests run or not run, unverified claims.

## Generation

Generate the page from data, not by hand-editing HTML each edition: keep a small script that reads the lens JSON files plus a controller file (subject, verdict, moves, release list) and writes the page. Reuse the previous edition's stylesheet. Republish to the same URL; record the URL, edition number, subject and scores in an edition note.

## Local copy

Write `docs/assessment/ASSESSMENT-<N>-<YYYY-MM-DD>.md` (or the project's existing location) with the scorecard, delta table, moves and release list, so the next edition can be produced without the page.
