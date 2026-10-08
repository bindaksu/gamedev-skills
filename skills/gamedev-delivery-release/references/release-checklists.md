# Release Checklists

Read before every go/no-go and during any hotfix.

## Go / No-Go (client release)

Quality
- [ ] gamedev-qa-verifier exit report: 0 S1, 0 unwaived S2, regression passed on P0/P1 devices
- [ ] No open blocker findings from gamedev-reviewer; majors waived in writing with dates
- [ ] Crash-free sessions in beta/internal at or above target; no new top crash cluster
- [ ] Perf within budget on min tier (device-measured)

Build
- [ ] Version, build number, commit, engine version, SDK versions, config version recorded
- [ ] Built by CI release lane; signed; symbols uploaded and verified
- [ ] Instrumentation (AltTester/GameDriver/Poco) and debug menus stripped
- [ ] App size within budget; install-time asset packs within store limits

Compatibility
- [ ] Server supports this client and N-2; new client tested against production-like server
- [ ] Config defaults bundled; boot does not block on config fetch
- [ ] Kill switches present and tested for every risky feature
- [ ] Save migration tested from the last 2 versions

Store
- [ ] Metadata, screenshots, what's-new text localized
- [ ] Privacy labels / data safety form current; ATT prompt behavior unchanged or reviewed
- [ ] Age rating current; loot-box odds displayed where randomized items are sold
- [ ] Platform requirements: Play target API 36 (Aug 31, 2026; ext. Nov 1, 2026), PBL 8+, 16 KB page support for updates from Feb 1, 2027 (as of 2026-10; verify)
- [ ] Review notes include demo account and instructions

Operations
- [ ] Rollout plan: iOS phased release on; Android staged percentages and dates
- [ ] Halt criteria written; named watcher for first 48 h; dashboards linked
- [ ] gamedev-live-serving on-call confirmed; no clash with event start or maintenance
- [ ] Support/community briefed; known issues list; player-facing patch notes
- [ ] Min-version policy decided (soft/force, threshold)

Decision: GO / NO-GO / GO WITH CONDITIONS (list), signed by release manager, QA lead, game lead.

## Hotfix runbook

1. **Declare** the issue with severity and exposure (version, % DAU, platforms). Notify gamedev-live-serving incident channel.
2. **Contain:** halt Play rollout; pause App Store phased release; flip kill switch or config if available.
3. **Choose fix path** with the decision tree in SKILL.md: server, config, CDN content, or binary hotfix.
4. **Binary hotfix:** branch from the release tag; minimal diff; bump PATCH and build number; run smoke + targeted regression + IAP suite if purchases touched.
5. **Submit:** request expedited review on iOS only for critical issues and say why; Android release to staged 10–20% first, then widen.
6. **Gate old clients:** soft update immediately; force only per policy (exploit, money loss, protocol break).
7. **Verify** with production evidence (crash cluster rate, purchase success) per gamedev-qa-verifier.
8. **Post-incident review** within 5 working days (template in gamedev-live-serving).

## Release calendar template

```
| Train | Feature cut | Branch QA | Submit | Target release | Rollout end | Owner | Events in window | Blackouts |
|-------|-------------|-----------|--------|----------------|-------------|-------|------------------|-----------|
| 1.15  | Oct 12      | Oct 13-15 | Oct 16 | Oct 19         | Oct 26      | ...   | Halloween Oct 24 | Oct 23-25 |
```

Blackouts: 48 h before major live events; marketing beats; store holiday submission shutdowns (check each store's annual notice); platform OS launch week (expect review delays).

## Store submission checklist

- [ ] Build processed in App Store Connect / Play Console without warnings
- [ ] Encryption export compliance answered
- [ ] IAP products and prices approved and attached to the version where required
- [ ] Release type set: manual release (iOS), managed publishing (Play)
- [ ] Phased release toggled on (iOS); staged rollout percentage set (Play)
- [ ] Country availability correct; pre-orders or pre-registration handled
