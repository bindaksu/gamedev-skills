# Game Studio Skill Pack

**46 agent skills that give Claude Code and OpenAI Codex the working knowledge of a full live-service game team.** There are 37 specialist seats, from combat design to Metal graphics to LiveOps to generative asset pipelines, and 9 orchestration skills that assess, brief, coordinate, run agent fleets, review, verify, ship and serve. One set of files works in both agents.

Each skill is written from how top-grossing mobile and PC studios actually staff and run that seat: its responsibilities, its method, the numbers it checks, its anti-patterns and its deliverables. Where a fact changes over time (store deadlines, SDK versions, model IDs), the skill marks it "as of 2026-10; verify" or "as of 2026-11; verify" and links its source. Version 1.1 adds field lessons from production use, written at genre level.

## Quick start

```bash
git clone git@github.com:bindaksu/gamedev-skills.git
cd gamedev-skills
./install.sh            # Claude Code (~/.claude/skills) + Codex (~/.codex/skills)
```

Restart Claude Code or Codex, then ask a game question in plain words. The matching skill loads from its description:

```text
> Our mage deck wins 42% against the knight deck. Design a buff and tell me how to prove it.
> Plan the soft launch for our puzzle RPG: markets, KPIs, kill criteria.
> Score our game across nine dimensions and list the top moves.
```

You can also call a skill by name: `/gamedev-combat-designer` in Claude Code, `$gamedev-combat-designer` in Codex.

## Where to start

| You want to… | Start with |
|---|---|
| Plan a feature that spans several disciplines | `gamedev-coordinator`: splits the work, names one owner per package, settles conflicts |
| Score a whole game and pick the next moves | `gamedev-assessment-manager`: evidence-backed editions with deltas and a machine-provable rubric |
| Hand a task to another agent or session | `gamedev-brief-coordinator`: turns a short ask into a paste-ready 400–900 word brief |
| Check work before it ships | `gamedev-reviewer` (severity-ranked review), `gamedev-qa-verifier` (test plans, honest evidence) |
| Ship or run a live game | `gamedev-delivery-release` (CI/CD, store rollout, force update), `gamedev-live-serving` (SLOs, incidents, kill switches) |
| Build a game with many coding-agent sessions | `gamedev-agentic-production`: standing rules, ledgers, locks, gates, model routing |
| Generate art, 3D, audio or video with AI models | `gamedev-ai-asset-pipeline`: model choice, spend caps, provenance, review, disclosure |
| Ship LLM-powered NPCs or chat inside a game | `gamedev-llm-features-engineer`: on-device vs cloud, guardrails, cost, store and rating rules |

## Install options

```bash
./install.sh                         # Claude Code + Codex, user scope
./install.sh --claude                # Claude Code only ($CLAUDE_CONFIG_DIR/skills, default ~/.claude/skills)
./install.sh --codex                 # Codex only ($CODEX_SKILLS_DIR, default $CODEX_HOME/skills = ~/.codex/skills)
./install.sh --project ~/code/game   # project scope: .claude/skills + .agents/skills
./install.sh --only gamedev-coordinator,gamedev-unity-engineer
./install.sh --uninstall             # remove pack skills from the chosen targets (Codex: both skill dirs)
./install.sh --dry-run               # print actions only
```

Codex reads user skills from both `$CODEX_HOME/skills` and `~/.agents/skills`; keep the pack in one of them (set `CODEX_SKILLS_DIR` to choose) or every skill shows twice. Every installed skill's description loads into each session. If you only need a few disciplines, install a subset with `--only`. To update, `git pull` and run `./install.sh` again.

## How a skill is built

```text
skills/gamedev-combat-designer/
├── SKILL.md            # YAML frontmatter (name, description, license, metadata) + instructions
├── references/         # longer tables, formulas and templates, loaded only when needed
└── agents/openai.yaml  # Codex display name, short description (25–64 chars), default prompt using $skill-name
```

Frontmatter uses only the keys every target accepts (`name`, `description`, `license`, `metadata`); Claude Code-only keys would break uploads to the Skills API and OpenAI's validator. Every `SKILL.md` has the same sections: **Role Profile** (what the seat owns at real studios, with sources), **When to Use / Not**, **Inputs to Gather**, **Method**, **Diagnostics**, **Anti-Patterns**, **Deliverables**, **Quality Checklist** and **Related Skills**. Many also carry a quantitative or technical reference. Specialist skills hand off to each other by name, so a combat question that touches the economy points at `gamedev-monetization-designer` instead of improvising.

## Repository layout

| Path | Contents |
|---|---|
| `skills/` | The 46 skills |
| `install.sh` | Installer for Claude Code, Codex, or one project |
| `tools/validate.py` | Checks frontmatter, name = folder, description limits, Codex metadata, cross-references and line caps |
| `tools/leak_guard.py`, `.githooks/` | Blocks secrets, local paths, hosts and private project names (pre-commit hook and CI) |
| `.github/workflows/checks.yml` | CI: validate, leak guard, catalog up to date |
| `tools/build_site.py`, `tools/site_template.html` | Build the browsable catalog at `site/index.html` |
| `tools/roster.txt` | The canonical skill roster |
| `docs/` | Research notes with source URLs: `companies.md`, `roles.md`, `tech.md` (2026-10), `ai-models.md` (2026-11) |

## Interpretations

- **Layout design** means level, map and board layout (`gamedev-level-layout-designer`). Screen layout lives in `gamedev-ui-designer`.
- **Campaign design** means story and mission campaigns (`gamedev-campaign-designer`). LiveOps event campaigns belong to `gamedev-liveops-designer`.
- **Serving** means the live-service runtime and content serving (`gamedev-live-serving`). The build and ship pipeline is `gamedev-delivery-release`.

## Companion skills (linked, not duplicated)

`core-loop-designer`, `game-economy-balancer`, `game-playtest-analyst`, `game-prototype-planner`, `game-asset-art-director` and `mobile-game-ux-designer` are referenced "if installed". The pack works without them.

## Research

`docs/companies.md`, `docs/roles.md` and `docs/tech.md` are the research notes from 2026-10-08, with source URLs. `docs/ai-models.md` (2026-11-21) covers generative asset models, coding-agent models and in-game LLM runtimes and policy. Field lessons added in 1.1 come from production use and are written as genre-level rules without project names or business figures. LinkedIn profiles were not scraped. Public job postings, careers pages, engineering blogs, filings and trade press stand in for team-member profiles. Claims inferred rather than quoted are tagged `[inference]` or `[proxy]` in the skills.

## Catalog

### Orchestration

| Skill | Scope |
|---|---|
| `gamedev-assessment-manager` | Scored, evidence-backed game assessment editions with deltas and top moves |
| `gamedev-brief-coordinator` | Turn a short game request into a tight, paste-ready agent brief |
| `gamedev-coordinator` | Decompose game features, route to specialist skills, set RACI |
| `gamedev-delivery-release` | Game CI/CD, signing, store rollout, hotfix vs config fix, force update |
| `gamedev-live-serving` | Game SLOs, incidents, event-day scaling, CDN content, kill switches |
| `gamedev-agentic-production` | Coding-agent fleets on one game: standing rules, ledgers, locks, gates, model routing |
| `gamedev-producer` | Stage gates, kill criteria, roadmaps, risk, scope cuts, live cadence |
| `gamedev-qa-verifier` | Game test plans, device matrix, automation, IAP tests, store cert |
| `gamedev-reviewer` | Severity-ranked review of game docs, economy, UX, client/server code |

### Game & narrative design

| Skill | Scope |
|---|---|
| `gamedev-campaign-designer` | Chapters, mission order, difficulty and interest curves, boss gates |
| `gamedev-combat-designer` | TTK, DPS and EHP math, frame data, abilities, enemy archetypes, unit balance |
| `gamedev-game-feel-designer` | Juice, hit-stop, screen shake, easing, haptics, and input latency |
| `gamedev-level-layout-designer` | Match-3 boards, move budgets, win-rate curves, and spatial map layout |
| `gamedev-liveops-designer` | Event calendars, battle pass math, event templates and LiveOps pipelines |
| `gamedev-meta-progression-designer` | Collections, rosters, gear, renovation meta, unlock pacing, power curves |
| `gamedev-narrative-designer` | Premise, world, characters, arcs, and story-in-meta for F2P and live games |
| `gamedev-pvp-designer` | Matchmaking, Elo/Glicko-2/TrueSkill, ranked seasons, async PvP, P2W, bots |
| `gamedev-script-writer` | Dialogue, barks, VO scripts, UI copy, and Ink/Yarn branching, loc-ready |
| `gamedev-simulation-designer` | Idle math, offline progress, production chains, agent sims, determinism |

### UX, UI & HUD

| Skill | Scope |
|---|---|
| `gamedev-accessibility-specialist` | GAG/XAG audits, subtitles, colorblind, remapping, screen readers, CVAA/EAA |
| `gamedev-hud-engineer` | Game HUD hierarchy, combat text, safe areas, and HUD performance |
| `gamedev-localization-specialist` | String pipeline, ICU plurals, CJK/RTL fonts, LQA, culturalization, store loc |
| `gamedev-ui-designer` | Game screen grids, tokens, 9-slice, icons, type, shop UI, engine handoff |
| `gamedev-ux-designer` | Game flows, IA, FTUE strategy, popup policy, heuristic audits, friction logs |

### Art & audio

| Skill | Scope |
|---|---|
| `gamedev-ai-asset-pipeline` | Generative image, 3D, audio and video production: models, spend caps, provenance, disclosure |
| `gamedev-audio-designer` | SFX, adaptive music, FMOD/Wwise, mobile audio budgets, LUFS, interruptions |
| `gamedev-technical-artist` | Shader and VFX budgets, ASTC/ETC2, atlasing, batching, skinning, asset checks |

### Growth, money & data

| Skill | Scope |
|---|---|
| `gamedev-analytics-engineer` | Event taxonomy, KPI SQL, BigQuery/dbt pipeline, A/B stats, attribution, consent |
| `gamedev-financial-growth-strategist` | LTV/ROAS models, UA scaling, soft-launch gates, P&L, forecasts, measurement |
| `gamedev-growth-designer` | Retention levers, habit loops, streaks, viral loops, notifications, win-back |
| `gamedev-monetization-designer` | IAP offers, shop, pass value, gacha disclosure, ads caps, webshops, regulation |

### Client engineering

| Skill | Scope |
|---|---|
| `gamedev-android-engineer` | Android games: NDK/AGDK, Vulkan, ADPF, Play Billing/PGS/PAD, Play policy |
| `gamedev-desktop-engineer` | Steam/PC/Mac: Steamworks, Deck Verified, input, display, notarization, stores |
| `gamedev-engine-architect` | Game loop, fixed timestep, ECS, determinism, saves, scripting, engine choice |
| `gamedev-godot-engineer` | Godot 4 games on mobile, Mac and Steam: exports, GDExtension, plugins, tests |
| `gamedev-ios-engineer` | Swift games on Apple platforms: loop, StoreKit 2, Game Center, thermals, review |
| `gamedev-llm-features-engineer` | LLM NPCs, companions and chat in games: on-device vs cloud, guardrails, cost, policy |
| `gamedev-metal-graphics-engineer` | Metal 3/4 renderers, MSL, MetalFX, TBDR bandwidth, GPU profiling, GPTK ports |
| `gamedev-netcode-engineer` | Multiplayer sync models, prediction, rollback, tick rates, mobile networks |
| `gamedev-optimization-compatibility` | Per-tier perf budgets, device matrix, thermals, memory, vitals, app size |
| `gamedev-react-native-engineer` | React Native/Expo games with Skia and worklets: Hermes perf, native cores, releases |
| `gamedev-unity-engineer` | Unity 6 mobile client architecture, Addressables, URP, IL2CPP, GC, plugins |

### Platform & backend

| Skill | Scope |
|---|---|
| `gamedev-anti-cheat-security` | Server authority, Play Integrity, App Attest, fraud, bot detection, ban systems |
| `gamedev-backend-engineer` | Idempotent economy ledger, receipt validation, refunds, leaderboards, mail |
| `gamedev-infrastructure-engineer` | Kubernetes, Agones fleets, regions, autoscaling, databases, CDN, cost and DR |
| `gamedev-platform-server-architect` | Service map, build vs buy, consistency, sharding and scale for game backends |

## Contributing

1. Edit or add a skill under `skills/<name>/`. The folder name must equal the frontmatter `name`, and new skills go in `tools/roster.txt`.
2. Enable the leak guard once per clone, then validate and rebuild the catalog:

   ```bash
   git config core.hooksPath .githooks
   python3 tools/validate.py --all skills
   python3 tools/leak_guard.py
   python3 tools/build_site.py
   ```

   Lessons from real projects go in at genre level. Keep project names, people, hosts and business figures out; see [SECURITY.md](SECURITY.md).

3. Re-run `./install.sh` to refresh your installed copies.

## License

[MIT](LICENSE)
