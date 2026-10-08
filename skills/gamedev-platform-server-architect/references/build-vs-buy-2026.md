# Build vs Buy — Game Backend Landscape (as of 2026-10; verify)

Read when scoring the build vs buy scorecard or writing an ADR that names a vendor. Every row here can change in a quarter; re-check the vendor page before signing.

## Vendor matrix

| Option | What it is | Strong at | Weak at / risk | Hosting model | Source |
| --- | --- | --- | --- | --- | --- |
| **Nakama** (Heroic Labs) | Open-source Go server (Apache-2.0), single binary; runtime in Go, Lua or TypeScript/JS; needs Postgres or CockroachDB | Sockets, authoritative matches, leaderboards, tournaments, groups, chat, storage, matchmaker; self-hostable = low exit cost | You operate it unless you pay for Heroic Cloud; economy/inventory needs Hiro | Self-host or Heroic Cloud (2.0, Jan 2026) | https://heroiclabs.com/docs/nakama/server-framework/introduction/ |
| **Hiro / Satori** (Heroic) | Metagame (economy, inventory, energy, event leaderboards) / LiveOps (events, flags, experiments, audiences) | Fast path to a full F2P meta on Nakama | Commercial; couples you to Heroic data model | Heroic Cloud or licensed | https://heroiclabs.com/blog/10-year-anniversary/ |
| **PlayFab** (Microsoft) | Managed BaaS: Economy v2, Multiplayer Servers (MPS), Party, Lobby/Matchmaking, CloudScript (Azure Functions) | Broad managed feature set; Xbox alignment; Foundation Mode (2026) gives Xbox devs core services cross-platform at no extra cost | API retirements happen (`GetPlayersInSegment` retired 2026-03-31); data model is PlayFab's | Fully managed (Azure) | https://developer.microsoft.com/en-us/games/articles/2026/04/playfab-digest-march-feature-updates/ |
| **AccelByte (AGS)** | Managed full-stack: identity, social, matchmaking, commerce, AMS server hosting | Console + PC cross-platform identity and commerce | Cost at scale; vendor-sourced comparisons only | Managed or private cloud | https://accelbyte.io/compare/accelbyte-vs-pragma |
| **Pragma** | Engine-agnostic backend running in the customer's own cloud; raised $12.75M (Mar 2025); acquired FirstLook (FirstLook 1.0 Feb 2026) | Ownership of data and infra; mid/large PC-console teams | Smaller vendor; you still run the cloud | Customer cloud | https://www.cbinsights.com/company/pragma-3 |
| **Unity Gaming Services** | Auth, Cloud Save, Cloud Code, Economy, Remote Config, Lobby, Relay, Matchmaker, Distributed Authority, CCD, Analytics, Leaderboards | Fastest path for small Unity teams | **Multiplay hosting: Unity ended direct support 2026-03-31** (licensed to Rocket Science Group); **global UGS ended for mainland China/HK/Macau orgs 2026-06-30** (UOS replaces) | Managed | https://docs.unity.com/en-us/multiplay-hosting, https://www.rocketscience.gg/multiplay/, https://support.unity.com/hc/en-us/articles/48560161446804 |
| **Photon** (Exit Games) | Fusion 2 (state sync, host/server + shared), Quantum 3 (deterministic ECS predict/rollback) | Real-time netcode + relay hosting with little ops | Not a meta/economy backend; free tier 100 CCU | Managed cloud | https://doc.photonengine.com/photon/current/photon-products |
| **Amazon GameLift Servers** | Dedicated server hosting (renamed when GameLift Streams launched); managed containers GA 2024-11-13 on ECS; Anywhere fleets; FlexMatch; FleetIQ (Spot) | AWS-native session hosting with matchmaking | AWS lock-in for the allocator API | Managed (AWS) | https://repost.aws/articles/ARK7UPPDp4QIuP5Rd4qdgKBQ/amazon-gamelift-is-now-amazon-gamelift-servers, https://aws.amazon.com/about-aws/whats-new/2024/11/amazon-gamelift-containers-dev-iteration-management |
| **Agones** | Open-source K8s CRDs: GameServer, Fleet, FleetAutoscaler, GameServerAllocation; latest v1.61.0 (Sept 24; year inferred 2026), Helm v4 move is breaking | Portable, cloud-agnostic session hosting on GKE/EKS/AKS/bare metal | You operate K8s; you build the allocator front door | Self-run | https://github.com/googleforgames/agones/releases |
| **Open Match 2** | Single `om-core` container, gRPC + REST gateway, language-agnostic matchmaking functions | Custom matchmaking logic at scale on K8s | **Public preview**, no tagged release seen; Open Match 1.x latest confirmed v1.8.x | Self-run | https://github.com/googleforgames/open-match2 |
| **Edgegap** | Edge orchestration across many PoPs; bare-metal option | Latency-sensitive session games, small ops team | Pricing figures conflict between sources — check the live page | Managed | https://edgegap.com/pricing |
| Others | Gameye, Nitrado GameFabric, Rocket Science (Multiplay), i3D.net, PlayFab MPS | Session hosting alternatives | Evaluate continuity | Managed | https://gameye.com/blog/game-server-shake-up-2026 |

## 2026 landscape changes that should change your ADR

1. **Hathora game hosting shut down 2026-05-05** after its pivot to AI inference and acquisition by Fireworks AI; customers were pointed to Nitrado GameFabric and Stormgate went offline-only (https://www.techspot.com/news/111969-stormgate-servers-go-dark-following-ai-focused-hosting.html, https://docs.edgegap.com/docs/tools-and-integrations/switch-from-hathora). Lesson: Agones-compatible containers plus an abstracted allocator interface.
2. **Unity Multiplay** direct support ended 2026-03-31; Unity Matchmaker now supports third-party hosts.
3. **UGS China exit** 2026-06-30 for mainland China, Hong Kong and Macau orgs.
4. **PlayFab** retired `GetPlayersInSegment` 2026-03-31; Foundation Mode launched.
5. **Heroic Cloud 2.0** (Jan 2026); no Heroic Labs acquisition found.
6. **Statsig acquired by OpenAI** (announced 2025-09-02) — weigh vendor continuity for experimentation (https://pulse2.com/openai-acquires-statsig-for-a-reported-1-1-billion/).
7. **Open Match 2** in public preview — fine for new builds if you accept preview risk; keep matchmaking functions portable.

## Decision heuristics

| Situation | Default |
| --- | --- |
| Under 3 backend engineers, async mobile, under 1M DAU target | Buy a BaaS (Nakama+Hiro managed, PlayFab, or UGS minus hosting). Keep IAP validation and entitlement in your own thin service so you can leave. |
| Top-grossing ambition, 5+ backend engineers, weekly LiveOps | Build ledger, store/entitlement, LiveOps config, segmentation. Buy push, chat (or Nakama), CDN, crash, auth federation. |
| Real-time session PvP | Netcode stack (Photon/Netcode/custom) + hosting (Agones on GKE, GameLift Servers, or managed edge). Keep server images Agones-compatible regardless of vendor. |
| Console + PC cross-platform with platform-store commerce | AccelByte, Pragma, or PlayFab; compare cert-tooling depth. |
| China launch | Separate stack with local publisher/cloud; do not plan on global UGS. |

## Exit-cost checklist (score each 0–3; 0 = trivial)

- Player identity export with all credential links
- Wallet balances and full journal export (not just balances)
- Inventory and entitlement export
- Leaderboard history and season snapshots
- Config/experiment definitions in a portable format
- SDK calls confined to one adapter layer in the client
- Server images runnable outside the vendor (OCI + Agones SDK)
- Contract terms: data return format, notice period on sunset

Total above 12: you are not buying a service, you are adopting a platform. Say so in the ADR.

Studio context (secondary/job-posting sources): Supercell runs Java (some Rust) on AWS with Terraform and DynamoDB/Redis; King runs Java on GKE with Terraform/Helm after moving data/ML to GCP in 2018; Scopely's Monopoly GO lists C#, DynamoDB, Redis at 20M+ DAU; Dream Games lists Java/Spring Boot on AWS with Redis and MySQL. Playrix and Dream Games have no public backend write-up — do not cite architectures for them.
