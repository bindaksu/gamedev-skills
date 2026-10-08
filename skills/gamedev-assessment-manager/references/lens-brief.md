# Lens Brief and Output Contract

Read before briefing lens reviewers. Give every lens the same subject and rubric; give each only its own dimensions and previous findings.

## Lens brief template (≈ 250 words)

```
You are lens <L#> (<name>) for assessment edition <N> of <game>.
Subject: <version> (<build>) @ <sha>, read-only checkout at <path>. Do not edit files, run installs, or push.
Run mode: <read-only | full: you may run these gates: …>.
Read first: AGENTS.md/CLAUDE.md, <ledger/gates file>, <DECISIONS>, <design docs for your dimensions>.
Load skills: <list from the lens table>.
Score these dimensions with the attached rubric: <dims>. Evidence on this subject only.
Previous findings you own (classify each closed/improved/unchanged/worsened with evidence): <list>.
Human-playtest absence is not a finding unless the owner opted in.
Return ONLY the JSON below. Every finding needs file:line, gate row, or measurement path.
```

## Output contract (JSON)

```json
{
  "lens": "L2",
  "subject": {"build": "1.2.0 (43)", "sha": "65748c3"},
  "scores": [
    {"dimension": "Economy", "score": 8.5, "ceiling": 9, "evidence": "tools/econ_sim passes 365-day run (docs/econ/run-0105.json)", "recalibrated": false}
  ],
  "deltas": [
    {"prior": "Campaign currency refund lockout", "status": "closed", "evidence": "CampaignEconomy.swift:212 + test testRefundRestoresCampaignCurrency"}
  ],
  "findings": [
    {"id": "L2-F1", "severity": "blocker|major|minor", "dimension": "Monetization", "claim": "Buy gated behind account link", "evidence": "ShopPurchaseGate.swift:44", "fix": "Allow guest purchase; link later", "owner_skill": "gamedev-monetization-designer"}
  ],
  "moves": [
    {"action": "Add guest purchase path", "dimension": "Monetization", "lift": "7 → 8", "proof": "sandbox purchase UI test on guest account", "owner_skill": "gamedev-monetization-designer"}
  ],
  "unverified": ["claims the lens could not check, with why"]
}
```

## Controller verification

For each blocker/major: open the cited location, confirm the claim on the subject SHA, then mark it `verified` or move it to `unverified` with a reason. Merge duplicate findings across lenses under the owner lens of the dimension.
