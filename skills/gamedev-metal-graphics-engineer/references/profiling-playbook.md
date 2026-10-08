# Metal Profiling Playbook

Tool names and commands as of 2026-10; WWDC26 additions (Game Performance Overview, look-back, StateReporting, MetricKit Metal frame rate) should be verified against the shipping OS and Xcode. Sources: https://developer.apple.com/documentation/xcode/analyzing-the-performance-of-your-metal-app , https://developer.apple.com/videos/play/wwdc2026/388/

## 1. Triage in 15 minutes

1. Warm the floor device: 20 minutes of gameplay, off the charger. Cold numbers lie.
2. Enable the Metal Performance HUD (debug builds, or the `MTL_HUD_ENABLED=1` environment variable in the scheme; verify for your Xcode). Note FPS, frame interval spread, memory.
3. Record a 60 s **Game Performance** trace in the worst scene.
4. Classify:

| Trace pattern | Verdict | Go to |
| --- | --- | --- |
| GPU track busy end to end, CPU has gaps | GPU-bound | Section 2 |
| CPU main or render thread busy, GPU has gaps | CPU-bound | Section 3 |
| Both have gaps, frames late | Stall / serialization | Section 4 |
| Mostly fine, occasional long frames | Hitches | Section 5 |
| Fine at start, degrades over minutes | Thermal | Section 6 |

## 2. GPU-bound

Take a GPU frame capture in Xcode. In order:

1. **Per-pass cost.** Sort encoders by GPU time. Any pass over 25% of the frame is the first target.
2. **Bandwidth.** Look at load/store and memory bandwidth counters per pass. Cross-check against the render pass ledger; every unexpected `store` or `load` is a fix.
3. **Limiter counters per shader** (ALU, texture sample, texture write, buffer read/write, occupancy). Texture-sample-limited: lower mip bias, cheaper filtering, smaller formats. ALU-limited: half precision (`half`), hoist uniform math to the CPU, cut variants.
4. **Overdraw.** Sort opaque front to back; keep alpha-blended particles small; use the overdraw view if available.
5. **Resolution.** If every pass is proportionally heavy, the frame is fill-bound: lower render scale and adopt MetalFX.

## 3. CPU-bound

- Time Profiler on the render thread. Typical culprits: per-draw `setFragmentTexture` and `setBuffer` calls (move to argument buffers), state-change churn (sort by pipeline), per-frame allocation of buffers or descriptors (pool them), Swift ARC traffic in hot loops (use unowned/value types, avoid closures per draw).
- Encode on multiple threads with parallel render command encoders or multiple command buffers, then commit in order.

## 4. Stalls

- Search the trace for `waitUntilCompleted`, `waitUntilScheduled`, and long `nextDrawable` waits.
- Check frames in flight: one shared uniform buffer forces serialization.
- Acquire the drawable after encoding offscreen work.
- Readbacks (`getBytes`, CPU reading a `.shared` buffer the GPU just wrote) in the same frame serialize everything; delay readbacks by N frames.

## 5. Hitches

- Points of Interest plus the shader-compilation track: any compile during gameplay is a bug. Fix with offline `.metallib`, async pipeline creation, and binary archives.
- Texture uploads: stream through a blit encoder over several frames; avoid `replace(region:)` on large textures on the main thread.
- Memory warnings: large purges or reallocation. Check the VM track.
- Tag states with **StateReporting** (`SRStateReporter reporterForDomain:`) so hitches are attributed to "level load", "shop open", "boss intro".

## 6. Thermal and long sessions

- Use the **Game Performance Overview** template for captures longer than a few minutes.
- **Look-back** collection captures the past without pre-arming: macOS `metalperftrace collect /tmp --last 5h` then `metalperftrace overview --json`; iOS Settings, Developer, Performance Trace, Lookback (also a Control Center button).
- Correlate frame interval with thermal state transitions. If the drop coincides with `serious`, the fix is less work per frame (bandwidth first), not micro-optimizing one shader.

## 7. Field data

- **MetricKit**: Metal frame rate broken down by game state (macOS, iOS 27) and memory-limit terminations. Build a dashboard of p50/p10 fps per state per device model.
- Compare field p10 against lab p50. A gap above ~20% usually means thermal or background-app pressure the lab never reproduces (heuristic).

## 8. Game Porting Toolkit evaluation (Windows title to Mac)

1. Run the unmodified Windows build in the GPTK evaluation environment (D3DMetal) on Apple silicon. GPTK 4 supports Metal 4 for DX12 titles; DX11 goes to Metal 3.
2. Capture with the command-line Metal capture/profile tools (GPTK 4) to find translation hot spots: unsupported features, heavy geometry shaders, tessellation, sparse resources.
3. Decide: if evaluation reaches about 70% of the target frame rate untouched (heuristic), a native port with targeted rewrites is usually viable.
4. Native port: convert HLSL/DXIL with Metal shader converter, replace the D3D backend with Metal, then redo pass design for TBDR. The evaluation layer is not a shipping path.
5. The open-source agent skills and sample code at https://github.com/apple/game-porting-toolkit (WWDC26 session 357) can automate parts of steps 2 and 4.
6. Ship via `gamedev-desktop-engineer` checklists: notarization, Steam entitlements, Mac App Store differences.
