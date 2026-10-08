---
name: gamedev-netcode-engineer
description: >-
  Design and implement real-time and async multiplayer netcode that feels local
  on bad mobile networks: choose lockstep, rollback, client prediction with
  server reconciliation or snapshot interpolation, set tick rates and bandwidth
  budgets, add lag compensation, and pick Photon, Netcode for GameObjects or
  Entities, Mirror or FishNet. Use when a user asks which netcode model fits a
  game, reports rubber-banding, desyncs, hits that do not register or high
  bandwidth, plans tick rate or packet format, builds turn-based or async PvP,
  or must survive Wi-Fi to cellular handoff.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: client-eng
---

# Netcode Engineer

Netcode is the art of lying consistently. Every player sees a different present: their own inputs immediately, everyone else's somewhere in the past, and the server's truth arriving late. The job is not to remove latency — light in fiber and a congested 4G cell tower forbid that — but to decide, per piece of state, who is authoritative, where the player is allowed to be wrong, and how the correction is hidden. Pick the model from the game's genre and player count before writing a line of transport code; the model decides bandwidth, cheat surface, server cost and how the game feels at 150 ms with 2% loss, which is a normal evening on mobile.

## Role Profile

Top mobile studios rarely post a "netcode engineer" title; the work sits with senior client engineers (Unity/C#, or in-house C++ at King and Playrix) and server engineers on real-time titles such as Brawl Stars and Clash Royale. Client postings ask for gameplay ownership, profiling and memory discipline (Rovio, Dream Games, Moon Active); server postings ask for "server-side Java, concurrency and distributed systems" (Supercell) and on-call ownership of what they ship (King). Riot's public engineering blog is the best open record of the craft: Valorant's 128-tick servers and peeker's-advantage work, and League of Legends' deterministic server for Chronobreak.

- **Hard skills:** C#/C++ (Go/Java/Rust server side), UDP transport, serialization and bit-packing, deterministic simulation, prediction/reconciliation, interpolation, lag compensation, network emulation and profiling.
- **Judged on (inferred):** match completion and disconnect rate, rubber-band/correction rate, hit-registration complaints, bandwidth per player, server cost per CCU, desync rate.
- **Collaborators:** gameplay and combat designers, backend/platform, infrastructure, anti-cheat, QA.
- Sources: https://jobs.lever.co/rovio-2/bb258566-0434-4025-ae4a-1d4b7a57896e , https://jobs.accel.com/companies/space-ape-games-2/jobs/66661349-senior-server-engineer-central-tech , https://technology.riotgames.com/node/112

## When to Use / Not

Use for choosing a sync model, tick and send rates, packet design, prediction, interpolation, rollback, lag compensation, network SDK choice, reconnect, and async/turn-based move protocols.

Not for:
- Matchmaking ratings, ranked ladders, fairness rules: `gamedev-pvp-designer`.
- Server fleets, regions, Agones, autoscaling and hosting vendors: `gamedev-infrastructure-engineer`.
- Lobby, account, inventory and service decomposition: `gamedev-platform-server-architect`; implementing those services: `gamedev-backend-engineer`.
- Speed hacks, packet tampering, bot detection beyond server authority: `gamedev-anti-cheat-security`.
- Fixed timestep, fixed-point math and engine determinism foundations: `gamedev-engine-architect`.

## Inputs to Gather

- **Genre and player count per match.** Default: assume 2–10 players, action-casual, mobile-first.
- **What must be fair vs what must feel instant.** Hit registration, scoring and economy are fair; own movement and UI are instant.
- **Latency tolerance of the core verb.** Frame-precise (fighting, rhythm), aim-precise (shooter), positional (MOBA, brawler), strategic (RTS, card, turn-based).
- **Determinism available?** Engine physics, float math, third-party plugins. Default: not deterministic unless proven by cross-device checksum tests.
- **Platforms and network mix** (cellular share, regions). Default: 50%+ of sessions on cellular, players up to 150 ms RTT from the nearest region.
- **Engine and SDK constraints**: Unity version (NGO 1.x is out on 6000.3+), existing Photon/Mirror code, hosting contract.
- **Cheat threat** (competitive ranking, real-money rewards). Default: ranked = server-authoritative.
- **Budget:** server cost per CCU-hour target and bandwidth cap per player. Default: under 20 KB/s down per mobile client.

## Method

1. **Classify the game and pick the model** with the decision table below. Write it down as an ADR with the rejected options; this decision is near-irreversible after vertical slice.
2. **Draw the authority map.** For every replicated piece of state: owner (server, client, shared), sync method (input, state, event), and who corrects whom. Unowned state is where desyncs breed.
3. **Fix the simulation tick before the send rate.** The sim runs at a fixed step (see `gamedev-engine-architect`); send rate is a divisor of it. Typical mobile action: 30 Hz sim/server, 15–30 Hz snapshots (heuristic).
4. **Budget bandwidth on paper** (formula below) before building serialization. If the paper number misses the cap, change the model or the data, not the compression.
5. **Build the transport layer once**: UDP with sequence numbers, acks, a reliable-ordered channel for events and an unreliable channel for state. Do not send gameplay state over TCP or WebSockets for action games — one lost packet stalls everything behind it.
6. **Implement prediction for the local player only**, with an input ring buffer and replay on correction. Predict remote entities only in rollback/deterministic models.
7. **Interpolate remote entities** behind a jitter buffer of 2–3 snapshot intervals; extrapolate at most one interval, then freeze.
8. **Add lag compensation for hitscan and fast projectiles** with a capped rewind window, and decide explicitly who wins edge cases (shooter's view vs target's cover).
9. **Smooth corrections**: blend visual position toward corrected position over 100–200 ms (heuristic) while the simulation state snaps; snap outright above a distance threshold.
10. **Build reconnect into the protocol from day one**: session token, resume from server snapshot, input replay window. Wi-Fi to cellular handoff changes the client IP; a socket bound to the 5-tuple dies.
11. **Test under emulated bad networks every sprint** with the network test matrix. Instrument corrections per minute, rollback frames, snapshot buffer underruns and RTT percentiles in production telemetry.
12. **Keep hosting swappable**: containerized headless server, an allocator interface, no vendor SDK calls in gameplay code. Two hosting vendors shut down or exited in 2026.

## Model Decision Table

| Model | Sends | Best for | Players | Strengths | Costs |
|---|---|---|---|---|---|
| Deterministic lockstep | Inputs | RTS, large unit counts, puzzle-battle | 2–8 | Tiny bandwidth regardless of unit count; replays for free | Stalls on slowest peer; needs strict determinism; input delay felt |
| Rollback (GGPO-style) | Inputs | Fighting, sports, 1v1/2v2 precision | 2–4 (up to ~8) | Local inputs instant; fair | Re-simulating N frames per frame; determinism; visual pops on misprediction |
| Client prediction + server reconciliation + interpolation | Inputs up, state down | Shooters, brawlers, MOBA, action RPG | 2–100+ | Server authority (cheat-resistant), tolerates non-determinism | Server CPU per match; complexity; remote entities shown in the past |
| Snapshot interpolation (no client sim) | State | Physics-heavy, spectators, low-skill casual | 2–32 | Simple, robust, no determinism needed | Bandwidth-heavy; input latency = RTT unless locally predicted |
| Distributed/shared authority | State per owner | Co-op, social, casual | 2–64 | No dedicated server needed | Cheatable; conflict resolution on shared objects |
| Async / turn-based | Moves (HTTP/socket) | Card, board, puzzle PvP, async raids | 2–N | Cheap, works on any network, push-driven | Not real time; idempotency and timeouts required |

Public reference points:
- **Overwatch** (GDC 2017): ECS architecture, fixed 16 ms command frames (7 ms in tournament mode), abilities predicted by default, server-authoritative rollback and reconciliation, time dilation to keep the server's input buffer filled. https://gdcvault.com/play/1024001/-Overwatch-Gameplay-Architecture-and
- **Valorant**: 128-tick dedicated servers (7.8125 ms budget; server frame time cut from 50 ms to under 2 ms), Riot Direct backbone, peeker's-advantage window target under about 60–80 ms, server-side rewind for hits. https://technology.riotgames.com/node/112
- **League of Legends**: the server was made deterministic for Chronobreak (esports rewind) and disaster recovery; a unified clock was the largest piece of work; divergence detected by comparing state logs. https://technology.riotgames.com/node/67
- **2XKO** (Riot) runs rollback on servers rather than peer-to-peer; few details are public (as of 2026-10; verify). https://www.shacknews.com/article/138850/2xko-sever-based-rollback-netcode
- **GGPO** is MIT open source since Oct 2019 (Skullgirls, Brawlhalla, Killer Instinct); **GGRS** is the Rust equivalent. https://www.gamingonlinux.com/2019/10/ggpo-a-rollback-networking-sdk-for-peer-to-peer-games-has-gone-open-source/
- Canonical explanations: Gambetta on prediction/reconciliation and entity interpolation (https://gabrielgambetta.com/client-side-prediction-server-reconciliation.html , https://gabrielgambetta.com/entity-interpolation.html); Fiedler on lockstep and snapshot interpolation (https://gafferongames.com/post/deterministic_lockstep/ , https://gafferongames.com/post/snapshot_interpolation ; he now writes at https://mas-bandwidth.com).

## Deliverables

### 1. Netcode ADR

```
GAME / MODE:         [name, players per match, match length]
CORE VERB LATENCY:   frame-precise / aim-precise / positional / strategic
MODEL:               [chosen]          REJECTED: [models + one-line reason each]
TOPOLOGY:            dedicated server / host / relay / P2P / shared authority
DETERMINISM:         required? [y/n]  proof: [cross-device checksum test id]
SIM TICK:            [Hz]   SNAPSHOT/SEND RATE: [Hz]   CLIENT INPUT RATE: [Hz]
INTERP DELAY:        [ms]   MAX EXTRAPOLATION: [ms]  MAX REWIND: [ms]  ROLLBACK WINDOW: [frames]
BANDWIDTH BUDGET:    down [KB/s]  up [KB/s]  per player, p95
SDK / TRANSPORT:     [Fusion 2 / Quantum 3 / NGO 2.x / Netcode for Entities / Mirror / FishNet / custom UDP]
HOSTING INTERFACE:   [allocator abstraction; current vendor]   owner: infrastructure
RECONNECT:           window [s], resume method, token lifetime
CHEAT POSTURE:       server-authoritative for [list]; client-trusted for [list, justified]
```

### 2. Authority map

```
State               │ Owner  │ Sync      │ Rate      │ Reliability │ Predicted? │ Correction
Local player move   │ Server │ input→state│ 30 Hz     │ unreliable  │ yes        │ replay inputs
Remote player move  │ Server │ snapshot  │ 20 Hz     │ unreliable  │ no         │ interpolate
Projectile spawn    │ Server │ event     │ on fire   │ reliable    │ yes (cosmetic)│ reconcile by id
Health / score      │ Server │ state     │ on change │ reliable    │ no         │ authoritative
Cosmetic emote      │ Client │ event     │ on use    │ unreliable  │ n/a        │ none
```

### 3. Bandwidth budget sheet

```
Entity type │ Count │ Bits/entity (quantized) │ Change rate │ Bits/tick (delta) │ × send Hz │ = bps
...
Packet header (seq, ack, ack bits, tick): [bits]   UDP+IPv4 header: 28 B (IPv6: 48 B) per packet
TOTAL down per client: [KB/s]   cap: [KB/s]   headroom: [%]
```

### 4. Network test matrix

```
Profile        │ RTT     │ Jitter │ Loss       │ Notes
Good Wi-Fi     │ 20 ms   │ 5 ms   │ 0%         │ baseline
Typical 4G     │ 60 ms   │ 20 ms  │ 0.5%       │
Bad 4G         │ 150 ms  │ 50 ms  │ 2% (burst) │ evening cell congestion
Edge region    │ 200 ms  │ 30 ms  │ 1%         │ far from server region
Handoff        │ Wi-Fi→cell switch at t=30 s, 1–5 s outage, IP change
Spike          │ 1 s freeze every 60 s      │ elevator / tunnel
PASS when: corrections/min < [x], no desync, reconnect < [y] s, match completion unaffected
```

Values are heuristics; replace with measured RTT/loss percentiles from your own telemetry. Emulate with Apple's Network Link Conditioner, Linux `tc netem`, or Clumsy on Windows.

Read `references/prediction-and-interpolation.md` when implementing the input ring buffer, reconciliation, the snapshot jitter buffer or lag-compensation rewind. Read `references/rollback-lockstep-serialization.md` when implementing rollback or lockstep loops, bit-packing, quantization, delta compression, the server tick loop or async move validation.

## Technical Reference

### Tick and send rates

| Genre | Server sim | Snapshot send | Client input send | Note |
|---|---|---|---|---|
| Competitive PC shooter | 64–128 Hz | 64–128 Hz | per frame | Valorant 128 Hz (7.8125 ms) |
| Hero shooter / brawler | 30–60 Hz | 20–30 Hz | 30–60 Hz | Overwatch command frame 16 ms |
| Mobile action / MOBA | 15–30 Hz | 10–20 Hz | 15–30 Hz | Heuristic; cellular and battery bound |
| Fighting (rollback) | 60 Hz | inputs every frame | 60 Hz | Redundant input history in each packet |
| RTS lockstep | 10–20 Hz turns | inputs per turn | per turn | Turn 50–200 ms (heuristic) |

Server frame budget = 1000 / tick Hz. At 128 Hz you have 7.8 ms for every match on the core; at 30 Hz you have 33 ms, which is why mobile servers pack more matches per core.

### Bandwidth math

```
bps_down_per_client = send_Hz × (header_bits + Σ_entities bits_changed_per_snapshot) + 28 B × 8 × send_Hz
server_egress       = bps_down_per_client × players × concurrent_matches
```

Worked check: 10 players, 20 Hz snapshots, 10 visible entities × 64 bits quantized each = 640 bits + 64-bit header ≈ 88 B payload + 28 B UDP/IPv4 ≈ 116 B/packet ⇒ 2.3 KB/s per client. Unquantized float position+rotation (28 B each) would be 280 B + 8 B header = 288 B payload, about 3.3× more. Keep packets under ~1200 B payload to avoid IP fragmentation on mobile paths (heuristic; QUIC uses the same floor).

Quantization defaults (heuristic): position in a 512 m arena at 1 cm precision = 16 bits per axis; yaw at 0.35° = 10 bits; health 0–1000 = 10 bits; velocity often derivable, do not send. Quaternions: smallest-three with 3 × 9–10 bits + 2-bit index.

Delta compression: encode each snapshot against the last snapshot the client acked (baseline), not the previous one sent. If no ack within N snapshots, send a full keyframe. Unacked-baseline deltas are the common source of "teleporting" after loss bursts.

### Interpolation, extrapolation and rewind

- Interpolation delay = 2–3 × snapshot interval + jitter allowance. At 20 Hz that lands near the classic **100 ms**.
- Adapt the delay dynamically from measured jitter (p95), within bounds; shrinking it too eagerly causes buffer underruns.
- Extrapolate at most one snapshot interval, then hold; long extrapolation draws players through walls.
- Lag compensation rewinds hitboxes to `server_now − one_way_latency − interp_delay`. Cap rewind at 200–250 ms (heuristic) so high-ping players cannot hit targets that have long since taken cover.

### Mobile network realities (heuristics; measure your own)

| Network | Typical RTT to in-region server | Jitter | Loss | Failure mode |
|---|---|---|---|---|
| Home Wi-Fi | 10–40 ms | 5–20 ms | under 0.5% | Bufferbloat during uploads; 2.4 GHz interference |
| 4G/LTE | 40–80 ms | 10–40 ms | 0.5–2% | Scheduler-induced spikes 200–500 ms; cell congestion at peak hours |
| 5G (NSA) | 20–60 ms | 5–30 ms | under 1% | Falls back to LTE mid-match; similar tail to LTE |
| Wi-Fi to cellular handoff | — | — | 1–5 s outage | New IP address; UDP flow and NAT mapping lost |

Design implications: send redundant recent inputs in every packet (last 3–8), identify the session by a token rather than IP:port, keep a 10–30 s reconnect window, and pause or bot-fill rather than forfeit on first disconnect. iOS and Android may suspend the socket within seconds of backgrounding; treat backgrounding as a disconnect with resume.

### SDK landscape (as of 2026-10; verify current versions)

| SDK | Model | Notes |
|---|---|---|
| Photon Fusion 2 (Unity) | State sync with prediction; host/server and shared topologies | Unreal/Godot versions in early access; free tier ~100 CCU [secondary] |
| Photon Quantum 3 | Deterministic ECS, predict/rollback, inputs only | Fighting, sports, MOBA-style; determinism handled by the engine's fixed-point math |
| Netcode for GameObjects 2.x | Server/host authority plus Distributed Authority topology | NGO 1.x unsupported from the 6000.3 editor |
| Netcode for Entities | Server-authoritative, client prediction, ghost snapshots | For DOTS projects; pairs with ECS shipping in the 6.4 Editor |
| Mirror | Open-source, server-authoritative, community-driven | Check maintenance cadence before committing |
| FishNet | Open-source, built-in prediction | Check current major version and prediction API |
| GGPO / GGRS | Rollback libraries (C++ / Rust) | Bring your own deterministic sim |

### Async and turn-based patterns

- The server owns game state; the client submits a **move** with `match_id`, `expected_state_version`, `move_id` (client UUID for idempotency) and payload.
- Server validates legality against the authoritative state, applies with optimistic concurrency (`version = expected + 1`), and returns the new state. A retried `move_id` returns the stored result instead of re-applying.
- Notify the opponent with a push notification plus an in-app socket if connected; never rely on push delivery for correctness.
- Turn timers with auto-forfeit or auto-move; store deadlines server-side.
- Async PvP against stored defenses (raid a player's base): simulate the battle deterministically on the server, or replay the client's input log server-side to verify the claimed result.

### Hosting landscape (brief; owner `gamedev-infrastructure-engineer`) (as of 2026-10; verify)

- Unity ended direct Multiplay Game Server Hosting support on Mar 31, 2026; the software is licensed to Rocket Science Group. UGS Matchmaker supports third-party hosts.
- Hathora's game hosting shut down on May 5, 2026; customers were steered to Nitrado GameFabric, and at least one title went offline-only.
- Agones (Kubernetes game-server CRDs) is at v1.61; Amazon GameLift Servers offers managed containers and Anywhere fleets; Edgegap, Gameye, i3D.net and PlayFab MPS are alternatives. Pricing varies and changes; check live pages.
- Lesson: ship a headless server container that runs on Agones or any allocator, behind your own allocation interface.

## Diagnostics

| Symptom | Likely cause | Fix |
|---|---|---|
| Local player rubber-bands under normal latency | Prediction mismatch: client sim differs from server (different dt, missing input, non-replayed state) | Replay from the acked tick with stored inputs; ensure the same fixed dt and code path on both |
| Remote players stutter or warp | Interpolation buffer underrun from jitter | Raise interp delay to 3 intervals; adaptive delay from p95 jitter |
| "I shot him first" complaints | No lag compensation, or rewind uses wrong timestamp | Rewind with server tick + client interp delay; log both views on disputed kills |
| Dying behind cover | Rewind window too large for high-ping shooters | Cap rewind 200–250 ms; favor defender above the cap |
| Lockstep match freezes for everyone | One peer slow or lost packets; no input redundancy | Redundant inputs, adaptive turn length, drop/AI-replace stalled peer |
| Desync after minutes in lockstep/rollback | Float non-determinism, unordered iteration, unseeded RNG, platform math libs | Fixed-point, ordered containers, seeded RNG in state; per-frame checksum and desync dump |
| Rollback visibly pops characters | Rollback window too large, no input delay | 1–3 frames input delay, cap rollback at ~7–8 frames (heuristic), interpolate visuals |
| Bandwidth far above estimate | Full state every tick, unquantized floats, deltas against unacked baseline | Quantize, delta vs acked baseline, interest management by distance/relevance |
| Players drop on commute | Wi-Fi to cellular handoff kills socket | Session-token resume, 10–30 s reconnect window, input replay |
| Server CPU spikes at match peaks | Per-player O(n²) relevance or physics checks | Spatial grid for interest management; profile tick time p99 |
| Massive bandwidth only on iOS background return | Full resync burst after resume | Rate-limit resync; send keyframe then deltas |

## Anti-Patterns

**TCP for Movement** — one lost segment stalls every newer update behind it; on 1–2% cellular loss the game freezes in bursts.

**Trust the Client's Position** — client-authoritative movement in a ranked mode. Speed hacks and teleports ship on day one.

**Model by Tutorial** — picking an SDK because of its sample, then discovering the genre needs rollback or determinism it cannot give.

**Unbounded Rewind** — lag compensation with no cap. The 300 ms player becomes the best player in the lobby.

**Float Lockstep** — deterministic lockstep on platform floats across ARM and x86 devices. Desyncs appear after weeks in rare matches nobody can reproduce.

**IP-Bound Sessions** — identifying players by address and port. Every Wi-Fi handoff becomes a disconnect and a loss.

**Perfect-Network Development** — all testing on office Wi-Fi. The first soft-launch market finds every bug in week one.

**Vendor-Welded Gameplay** — hosting SDK calls inside gameplay code. When the vendor exits, the port is a rewrite.

**Predict Everything** — predicting other players' outcomes or server-only results (damage, loot). Corrections become visible lies.

## Quality Checklist

- [ ] Netcode ADR written with rejected models and reasons
- [ ] Authority map covers every replicated state; nothing is unowned
- [ ] Sim tick fixed; send rates are divisors of it
- [ ] Bandwidth budget computed on paper and measured p95 within cap
- [ ] State on unreliable channel; events on reliable channel; no gameplay state over TCP
- [ ] Inputs sent redundantly (last 3–8) in each packet
- [ ] Local prediction replays from acked tick; correction smoothing in place
- [ ] Interp delay adapts to jitter within bounds; extrapolation capped at one interval
- [ ] Lag compensation rewind capped and logged for disputed hits
- [ ] Deterministic models: per-frame checksum, desync dump, cross-device (ARM/x86) test
- [ ] Delta compression against acked baseline with keyframe fallback
- [ ] Reconnect by session token survives Wi-Fi to cellular handoff in test
- [ ] Network test matrix run each sprint; results tracked
- [ ] Telemetry: RTT p50/p95, loss, corrections/min, rollback frames, buffer underruns, disconnect rate
- [ ] Headless server runs in a container behind an allocator interface; no vendor calls in gameplay code
- [ ] Async moves idempotent by move_id with version checks and server-side deadlines

## Related Skills

`gamedev-engine-architect` owns the fixed timestep, fixed-point math and deterministic simulation this skill depends on. `gamedev-pvp-designer` sets matchmaking, regions-per-queue and fairness rules that constrain acceptable RTT. `gamedev-combat-designer` and `gamedev-game-feel-designer` decide which actions must feel instant and how corrections can be masked with animation and effects. `gamedev-anti-cheat-security` builds on the authority map to detect speed hacks, packet tampering and bots. `gamedev-platform-server-architect` places the match server among lobby, matchmaking and session services; `gamedev-backend-engineer` implements async move endpoints and persistence. `gamedev-infrastructure-engineer` owns fleets, regions, Agones and hosting vendors. `gamedev-unity-engineer` integrates the chosen SDK into the client architecture; `gamedev-optimization-compatibility` owns battery and thermal cost of radio use. `gamedev-qa-verifier` runs the network test matrix on the device lab. If installed, `game-prototype-planner` scopes a netcode spike before the model is locked.
