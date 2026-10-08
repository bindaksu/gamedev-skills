# Skill Roster (41 pack skills + 6 companions)

Read when routing an unfamiliar request or checking where a boundary falls. Names are exact; use them verbatim in handoffs.

## Design (narrative + game design)

| Skill | Scope |
|---|---|
| gamedev-script-writer | Dialogue, barks, VO scripts, cutscene scripts, tutorial/UI copy voice, branching dialogue formats (Ink/Yarn), loc-ready writing |
| gamedev-narrative-designer | Premise, world, characters, arcs, environmental storytelling, narrative delivery in F2P/live games, story-in-meta |
| gamedev-campaign-designer | Single-player campaign/mission/chapter structure, difficulty and pacing across a campaign, boss gates; section on LiveOps season arcs |
| gamedev-level-layout-designer | Level/map/board layout: spatial flow, sightlines, chokepoints, match-3/puzzle board design and difficulty tuning, procedural vs authored |
| gamedev-combat-designer | Hit/hurt boxes, frame data, TTK, DPS/EHP math, abilities, enemy archetypes, auto-battler and turn combat, mobile combat controls |
| gamedev-pvp-designer | PvP modes, matchmaking (Elo/Glicko-2/TrueSkill/MMR), ranked ladders, seasons, fairness, P2W boundaries, async PvP, guild wars, anti-toxicity |
| gamedev-simulation-designer | Idle/incremental, builders, agent sims, production chains, offline progress, determinism, tick models |
| gamedev-meta-progression-designer | Collections, hero rosters, gear, decor meta, account level, unlock pacing, power curves |
| gamedev-liveops-designer | Events, battle/season pass, event calendars, limited-time modes, content cadence, event templates, event economy |
| gamedev-game-feel-designer | Juice: feedback, hit-stop, screen shake, easing, particles, haptics timing, input latency perception |

## UX/UI

| Skill | Scope |
|---|---|
| gamedev-ui-designer | Visual UI style, screen layout grids, iconography, typography, UI design system/tokens, shop screens, Figma-to-engine handoff |
| gamedev-ux-designer | Flows, IA, onboarding/FTUE strategy, UX research, game usability heuristics, friction audit |
| gamedev-hud-engineer | HUD design and implementation: hierarchy, diegetic/non-diegetic, damage numbers, minimaps, safe areas, HUD perf |
| gamedev-accessibility-specialist | GAG/XAG guidelines, colorblind, subtitles, remapping, motor and cognitive access, platform a11y APIs |
| gamedev-localization-specialist | String pipeline, ICU plurals, CJK/RTL fonts, text expansion, LQA, region-specific content rules |

## Art and audio

| Skill | Scope |
|---|---|
| gamedev-technical-artist | Shaders, VFX, asset pipeline, LOD, atlasing, ASTC/ETC2, draw-call budgets, tooling |
| gamedev-audio-designer | SFX, music, adaptive audio, FMOD/Wwise, mobile audio budgets, audio focus and interruptions |

## Growth and business

| Skill | Scope |
|---|---|
| gamedev-growth-designer | Retention loops, D1/D7/D30 levers, social/viral loops, referral, guilds, notifications, re-engagement, FTUE-to-habit |
| gamedev-monetization-designer | IAP offers, shop, starter packs, battle pass value, gacha with disclosure and pity, ads placement, personalization, ethics and regulation |
| gamedev-financial-growth-strategist | Unit economics, LTV/ARPDAU/ROAS/payback, cohort LTV, UA scaling, soft-launch KPI gates, P&L, platform fees, forecasting, portfolio greenlight |
| gamedev-analytics-engineer | Event taxonomy, KPI definitions, data pipeline, A/B infra and stats, dashboards, attribution (SKAN/AdAttributionKit) |

## Client engineering

| Skill | Scope |
|---|---|
| gamedev-ios-engineer | Swift, SpriteKit, SceneKit/RealityKit status, GameKit, StoreKit 2, Game Controller, CADisplayLink loop, thermal state, App Store rules |
| gamedev-metal-graphics-engineer | Metal 3/4, MetalFX, MSL shaders, GPU profiling in Instruments, Game Porting Toolkit, Apple Silicon |
| gamedev-android-engineer | Kotlin, NDK/C++, AGDK, Vulkan/ANGLE, ADPF, Play Games Services v2, Play Billing, Play Asset Delivery, 16 KB pages |
| gamedev-unity-engineer | Unity 6 architecture, Addressables, URP, DOTS where justified, IL2CPP, memory/GC, native plugins, build pipeline |
| gamedev-desktop-engineer | Steamworks, Steam Deck verification, KB/M + gamepad, display modes, Windows/macOS packaging, notarization, cross-progression |
| gamedev-engine-architect | Game loop, fixed timestep, ECS vs OOP, determinism, scripting layers, data-driven design, save systems, Godot/custom/C++ |
| gamedev-netcode-engineer | Lockstep, rollback, prediction and reconciliation, snapshot interpolation, tick rates, lag compensation, Photon/Netcode/Mirror |
| gamedev-optimization-compatibility | Frame/thermal/memory/battery budgets, device tiers and matrix, profiling, app size, startup time, ANR/crash, OS support |

## Backend

| Skill | Scope |
|---|---|
| gamedev-platform-server-architect | Service decomposition, build vs buy (Nakama/PlayFab/AccelByte/UGS/Pragma), data model, consistency, scale targets |
| gamedev-backend-engineer | Authoritative economy transactions, idempotent receipt validation, inventory, leaderboards, guilds, mail, remote config, API versioning |
| gamedev-infrastructure-engineer | Kubernetes, Agones, server fleets, regions, autoscaling, asset CDN, databases at scale, observability, cost, IaC, DR |
| gamedev-anti-cheat-security | Client tamper, Play Integrity / App Attest, server authority, receipt fraud, speed hacks, memory editing, bots, bans |

## Meta (orchestration)

| Skill | Scope |
|---|---|
| gamedev-coordinator | Entry point: decompose, route, handoffs/RACI, merge, resolve conflicts |
| gamedev-producer | Lifecycle stages and kill gates, scope, roadmap, risk register, team composition, rituals, vendors |
| gamedev-reviewer | Cross-discipline review rubrics and severity-ranked findings |
| gamedev-qa-verifier | Test strategy, device matrix, regression, automation, soak/perf, certification, bug triage, fix verification |
| gamedev-delivery-release | CI/CD, signing, store submission, phased/staged rollout, hotfix vs patch vs config, force update, go/no-go |
| gamedev-live-serving | SLOs, incident response, launch/event-day capacity, CDN hot content, remote config rollout, kill switches, maintenance, player comms |
| gamedev-brief-coordinator | Turns a short request, feedback list or assessment moves into a paste-ready agent brief (400–900 words) with FB ledger, acceptance, evidence, completion labels |
| gamedev-assessment-manager | Scored assessment editions: 10 dimensions on a machine-provable rubric, ceilings, deltas, lens reviews, verdict, top moves, release list, revenue model, page updated in place |

## Companion skills (outside the pack, use if installed)

| Skill | Scope | Pack fallback if not installed |
|---|---|---|
| core-loop-designer | Core gameplay loop, nested loops, attrition points | gamedev-meta-progression-designer + gamedev-growth-designer |
| game-economy-balancer | Faucets/sinks ledger, cost curves, currency exchange, price-ladder math | gamedev-monetization-designer (design) + gamedev-meta-progression-designer (curves) |
| game-playtest-analyst | Playtest method choice, sample sizing, funnels, retention reading | gamedev-analytics-engineer + gamedev-ux-designer |
| game-prototype-planner | Prototype scoping, hypothesis, timebox, kill criteria | gamedev-producer |
| game-asset-art-director | Art direction, style bible, asset budgets, outsourcing briefs | gamedev-technical-artist + gamedev-ui-designer |
| mobile-game-ux-designer | Touch, thumb zones, safe areas, FTUE, haptics, honest monetization UX | gamedev-ux-designer + gamedev-hud-engineer |

## Interpretation notes

- "Layout design" is level/map/board layout (gamedev-level-layout-designer). Screen layout is gamedev-ui-designer.
- "Campaign design" is story/mission campaign (gamedev-campaign-designer). LiveOps event campaigns are owned by gamedev-liveops-designer.
- "Serving" is live-service runtime plus content serving (gamedev-live-serving). The release pipeline is gamedev-delivery-release.
