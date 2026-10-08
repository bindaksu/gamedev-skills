# Engine Choice Matrix

All version, licence and pricing facts are (as of 2026-10; verify) against the vendor's current page before a decision is recorded.

## 1. Engine profiles

| Engine | Language | Sweet spot | Weak spot | Licence / cost | Status notes |
|---|---|---|---|---|---|
| Unity 6 | C# (IL2CPP on mobile) | Mobile 2D/3D, casual to mid-core, live ops; dominates top-grossing mobile (directional estimates ~70%) | Large-world AAA, determinism needs custom work, upgrade churn | Seat-based. Personal to $200k revenue; Pro $2,200/seat/yr above; Enterprise above $25M. Runtime Fee cancelled Sept 2024 | 6.3 LTS current live-game pick; 6.4 ships ECS core with the Editor; 6.5 deprecates Built-in RP, HDRP in maintenance; 6.7 LTS expected Q4 2026; Unity 7 (CoreCLR) announced for Q1 2027, provisional |
| Unreal 5 | C++, Blueprint | High-end 3D, shooters, PC/console with a mobile SKU | Mobile build size and memory floor; C++ iteration speed for small teams | 5% royalty above $1M lifetime gross per product (verify) | 5.6 shrank mobile packages; 5.8 (June 2026): Lumen Lite, MegaLights and Iris networking production-ready; likely last 5.x |
| Godot 4 | GDScript, C#, C++ (GDExtension) | 2D and mid-tier 3D, small teams, open source control, embedding (LibGodot) | Console ports only via third parties; smaller mobile ecosystem (ads, attribution SDKs) | MIT, no fees | 4.5: shader baker, stencil buffer. 4.6 (early 2026; date reported as Jan 27 and Feb 27): Jolt default 3D physics, unique node IDs, LibGodot, C++ tracing profiler |
| Defold | Lua | Small 2D games, HTML5/instant, tiny builds | 3D, large teams, hiring pool | Free, source-available | Originated at King; 1.12.x; Box2D v3 and runtime SDF fonts in 1.10 |
| Cocos Creator 3.8 | TypeScript | WeChat/Douyin mini-games, HarmonyOS, web, China market | Western tooling and SDK ecosystem | Free | 3.8.x LTS line; acquisition report unconfirmed |
| Native Apple | Swift, Metal, SpriteKit, RealityKit | Apple-only titles, Apple Arcade, deep platform features | Android parity; SpriteKit stagnant (not deprecated, no roadmap); SceneKit soft-deprecated | Free | Metal 4 needs A14+/M1+; RealityKit thin for genre games |
| Native Android | Kotlin, C++ NDK, Vulkan | Platform tech, SDKs, Android-first studios | iOS parity | Free | AGDK (GameActivity, Swappy, Memory Advice beta) |
| Custom C++ | C++ (+ Lua/other scripting) | Studios with many titles and huge MAU amortising the cost | Everything is your problem: ports, tools, cert, hiring ramp | Engineering headcount | Supercell Titan (~70-person org, ~300M MAU), King's in-house engine, Playrix's C++17 engine, NetEase Messiah |

## 2. What top studios actually run

| Studio / title | Engine | Source quality |
|---|---|---|
| Royal Match, Royal Kingdom (Dream Games) | Unity | Secondary |
| Monopoly GO (Scopely) | Unity | Job postings |
| Genshin Impact (HoYoverse) | Unity, heavily customised pipeline | Secondary |
| All Supercell games | Titan (in-house) | Official |
| Candy Crush (King) | Proprietary C++ + Lua | Job postings |
| Gardenscapes / Township (Playrix) | Proprietary C++ | Job postings |
| Diablo Immortal, Knives Out (NetEase) | Messiah (in-house) | Secondary |
| Honor of Kings: World (Tencent) | Unreal | Secondary |

Pattern: casual and 4X hits mostly ship on Unity; legacy puzzle giants and Chinese majors keep proprietary C++ engines; Unreal appears on high-end projects.

## 3. Decision rules

1. **Team skills dominate.** A team of C# Unity engineers ships faster on Unity than on a technically better fit. Retraining costs months (Playrix runs a Unity-to-C++ bootcamp for exactly this reason).
2. **Mobile floor device decides 3D fidelity.** If the floor is a 3–4 GB Android phone, Unreal's memory floor and package size need proof on that device before commitment.
3. **Determinism need:** cross-platform lockstep or rollback pushes toward a deterministic framework (Photon Quantum in Unity) or a custom fixed-point sim. No mainstream engine's built-in physics is cross-platform deterministic by default.
4. **Mini-game and China channels** (WeChat, Douyin) push toward Cocos or engine exports that target them explicitly.
5. **Licence exposure at scale:** model the cost at your revenue forecast. Seat-based (Unity) scales with headcount; royalty (Unreal) scales with gross revenue.
6. **Console plans:** Unity and Unreal have first-party console support; Godot relies on third-party porters; Defold supports Switch via licence with Nintendo developer access (verify).
7. **Vendor roadmap risk:** Unity has reset roadmaps before; pin to an LTS and treat future-version features as provisional.

## 4. When a custom engine is justified

All of these, not some:
- Multiple concurrent titles or a decade-long live title that amortise an engine team (Supercell's Titan org is ~70 people across engine, tools and live-ops infra).
- A technical requirement no engine meets (extreme build size, a specific determinism or rendering need, a platform no engine supports).
- Senior C++ engine talent on staff, not to be hired.
- Willingness to own platform ports, OS updates, store policy changes (16 KB pages, target API levels, Metal/Vulkan changes) and tools forever.

If any is missing, use an engine and spend the saved headcount on content and live ops.

## 5. Custom-engine building blocks (if you go there)

| Need | Typical choice |
|---|---|
| ECS | EnTT or flecs |
| Rendering abstraction | bgfx, Diligent, or own thin Metal/Vulkan layer |
| Physics | Jolt (used by Godot 4.6 as default), Box2D v3 for 2D |
| Scripting | Lua 5.4 (sol2), or none |
| Serialization | FlatBuffers / protobuf / own versioned binary |
| Audio | FMOD or Wwise (licensed), miniaudio |
| UI | Dear ImGui for tools only; own retained-mode UI for game |
| Profiling | Tracy, plus platform tools (Instruments, AGI, Perfetto) |

Verify current versions and licences for each library before adopting.
