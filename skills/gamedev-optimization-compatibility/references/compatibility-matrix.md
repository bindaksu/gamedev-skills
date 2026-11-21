# Device Tiers, Test Matrix, GPU Blocklists and Size Reduction

## 1. Tier assignment

Tier is a server-side decision with a client-side fallback, so you can move a device between tiers with a config push.

```json
{
  "version": 42,
  "rules": [
    { "match": { "platform": "android", "model": ["SM-A145F", "SM-A055F"] }, "tier": "low" },
    { "match": { "platform": "android", "gpu_renderer_prefix": "Mali-G52" },   "tier": "low" },
    { "match": { "platform": "android", "ram_mb_lt": 4096 },                   "tier": "low" },
    { "match": { "platform": "ios", "soc_lt": "A14" },                         "tier": "low" },
    { "match": { "platform": "ios", "soc_gte": "A17" },                        "tier": "high" }
  ],
  "default": "benchmark",
  "benchmark": { "seconds": 3, "low_below_score": 4000, "high_above_score": 12000 }
}
```

Model strings above are placeholders: build the real table from your install data. Matching order: exact model, then GPU renderer, then RAM/SoC rules, then a short first-launch benchmark (a fixed GPU and CPU workload behind the loading screen) for unknown devices. Cache the result; re-run when the OS version changes.

Signals to collect on first launch (and send with every perf event):

| Signal | Android source | iOS source |
|---|---|---|
| Model | `Build.MODEL`, `Build.MANUFACTURER` | `utsname.machine` (e.g. iPhone15,2) |
| SoC | `Build.SOC_MODEL` (API 31+) | derived from machine identifier |
| GPU | `GL_RENDERER` / `VkPhysicalDeviceProperties.deviceName`, driver version | `MTLDevice.name`, GPU family support |
| RAM | `ActivityManager.MemoryInfo.totalMem` | `ProcessInfo.physicalMemory` |
| OS | `Build.VERSION.SDK_INT` | `UIDevice.systemVersion` |
| Low-RAM flag | `ActivityManager.isLowRamDevice()` | — |
| Display | refresh rates, resolution, density | max FPS (`UIScreen.maximumFramesPerSecond`) |

## 2. Test-matrix construction

1. Export active installs by model for the last 28 days per platform. Join revenue by model.
2. Assign tiers with the rules above.
3. Within each tier, sort by install share. Add devices until cumulative coverage reaches ~70–80% of the tier (heuristic) or the lab budget is spent.
4. Add one device per GPU family/driver line not yet represented: Qualcomm Adreno, Arm Mali, Imagination PowerVR, Samsung Xclipse, Apple.
5. Add worst cases: lowest RAM still supported, oldest OS still supported, a large-screen/foldable device, the highest refresh-rate device.
6. Add the top 3 devices by revenue even if already covered by share — regressions there cost the most.
7. Re-run quarterly and at soft launch → global launch, because install mix shifts with UA geography.

```
MATRIX v[n] (date)          Android installs covered: [..]%   iOS installs covered: [..]%
Device         │ Tier │ GPU line      │ RAM │ OS  │ Share │ Rev share │ Why included
[model]        │ low  │ Mali-G5x      │ 3GB │ 13  │ 4.1%  │ 2.0%      │ floor, top share in tier
[model]        │ mid  │ Adreno 6xx    │ 6GB │ 14  │ 3.3%  │ 5.2%      │ median device
[model]        │ high │ Apple A17     │ 8GB │ 26  │ 2.9%  │ 9.8%      │ top revenue
[model]        │ low  │ PowerVR       │ 4GB │ 12  │ 0.6%  │ 0.3%      │ GPU line coverage
```

Cloud device farms widen coverage for smoke tests and crash repro; keep owned devices for perf and thermal work, because farm devices vary in thermal environment and background load.

## 3. GPU driver issues and blocklists

Driver bugs are a fact of Android life and occasionally of Apple GPUs after OS updates. Typical classes (not a list of specific bugs — collect your own from crash data):

| Class | How it shows | Typical mitigation |
|---|---|---|
| Shader compiler crash/hang | Native crash in vendor driver library at pipeline/shader creation | Simplify shader variant; disable feature for that driver; precompile/warm on a loading screen |
| Precision differences | Banding, flicker, NaNs on some GPUs with `mediump` | Use `highp` for positions/UV math that needs it |
| Extension misreporting | Feature reported but broken | Blocklist the extension/feature by renderer + driver version |
| Vulkan driver instability on older devices | Crashes or corruption only on Vulkan | Force GLES (or GLES via ANGLE on Android 15+) for that device set |
| Memory reporting quirks | OOM kills earlier than footprint suggests | Lower tier memory budget for that GPU line |

Blocklist entry shape (remote config, applied before graphics init on next launch):

```json
{
  "id": "gpu-2026-031",
  "match": { "gpu_renderer_prefix": "Mali-G", "driver_version_lt": "r38", "os_sdk_lte": 30 },
  "action": { "graphics_api": "gles3", "disable": ["gpu_instancing_path_b"] },
  "evidence": "crash cluster C-1182, 0.9% of sessions on matched devices",
  "added": "2026-10-01",
  "review_by": "2027-01-01"
}
```

Match fields and version formats here are illustrative; driver version strings differ per vendor. Engines provide hooks: Unity exposes Vulkan device filtering in Android player settings (verify the asset/setting name on your version), Unreal uses device profiles and per-device CVars. Because API choice happens before the engine renders, a remote blocklist needs a persisted value read at the next launch.

Facts (as of 2026-10; verify): about 85% of active Android devices support Vulkan; all 64-bit Android 10+ devices support Vulkan 1.1; OpenGL ES receives no new features; ANGLE ships as an optional GLES-on-Vulkan layer on Android 15+. Metal 4 needs A14 / M1 or later.

## 4. OS and API support policy

| Decision | Inputs | Rule of thumb (heuristic) |
|---|---|---|
| Drop an iOS version | Install share, payer share, SDK minimums (ads, billing, attribution), engine minimum | Drop when share < 1–3% and payer share is lower, or a required SDK forces it |
| Android minSdk | Same, plus engine minimum and Vulkan baseline | Raise with engine upgrades; check share by API level first |
| targetSdk | Store rule | API 36 required for new apps and updates from Aug 31, 2026 (extension to Nov 1, 2026) (as of 2026-10; verify) |
| Graphics floor | Vulkan share, GLES fallback cost | Keep GLES fallback while blocklist actions still need it |
| 16 KB pages | Store rule | Updates blocked from Feb 1, 2027 without support (as of 2026-10; verify) |

Announce drops in-game one release ahead. Players on dropped versions keep the last compatible build, so the backend must keep accepting that client version for a defined window — coordinate with backend owners.

## 5. App size reduction

Order of attack (largest wins first in most mobile games — measure your own build report):

1. **Move content out of the binary.** First-session content in the binary; the rest via Play Asset Delivery (fast-follow / on-demand), Apple-hosted Background Assets, or engine remote content (Addressables, Unreal chunking/ChunkDownloader).
2. **Textures.** ASTC for all modern targets with block size chosen per asset class (larger blocks for backgrounds, smaller for UI/characters); ETC2 fallback only if you still ship GLES-only devices. PAD Texture Compression Format Targeting serves the right format per device from one AAB. Cap max resolution per tier; remove unused mip levels on UI.
3. **Audio.** Compressed formats (Vorbis/AAC/Opus), mono for SFX, streaming for music, sample-rate reduction for non-critical sounds.
4. **Code.** IL2CPP managed stripping, C++ compiler size optimizations, remove unused SDKs, arm64 only where the store and install base allow.
5. **Duplicates.** Asset duplication across bundles/packs; fonts with full CJK sets bundled per language instead of on demand.
6. **Shaders.** Strip unused variants; variant explosion inflates both size and load time.

Limits (as of 2026-10; verify):

| Mechanism | Limit |
|---|---|
| Play base module | 200 MB |
| Play asset pack | 1.5 GB each; max 100 packs |
| Play install-time packs total | 4 GB |
| Play on-demand + fast-follow total | 4 GB; 30 GB for Level Up program / XR titles |
| Apple-hosted Background Assets | up to 200 GB compressed per app; essential / prefetch / on-demand policies; updatable without a binary; replaces On-Demand Resources |

Fast-follow and on-demand packs may be deleted or moved by the OS or the user — query their location through the PAD library every time rather than caching paths.

Size report template:

```
BUILD [..]   store download (median device) [..] MB   install [..] MB   first-session content [..] MB
Top 10 contributors: [asset/group, MB, % of total]
Delta vs last release: [+/- MB]  allowance: [..] MB   VERDICT: pass/fail
```
