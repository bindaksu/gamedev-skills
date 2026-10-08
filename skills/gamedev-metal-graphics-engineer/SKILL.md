---
name: gamedev-metal-graphics-engineer
description: >-
  Design, write and profile Metal renderers for Apple GPUs: Metal 3 and Metal 4 (A14 and M1 or later),
  MetalFX upscaling, frame interpolation and denoising, MSL shaders, argument buffers, heaps, triple
  buffering, and tile-based deferred rendering with memoryless targets. Use when someone asks to build
  or port a Metal renderer, cut GPU frame time, bandwidth or heat on iPhone, iPad or Mac, adopt MetalFX,
  read a GPU capture or Metal System Trace, port a Windows game with Game Porting Toolkit, or interpret
  MetricKit frame-rate data.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: client-eng
---

# Metal Graphics Engineer

Apple GPUs are tile-based deferred renderers, and almost every mobile rendering mistake is a desktop habit that ignores the tile. On a phone, the expensive thing is not math; it is moving bytes between tile memory and system memory, because bandwidth is heat and heat is lost frames ten minutes into a session. A Metal engineer earns their keep by keeping intermediate data on-chip (memoryless targets, correct load and store actions, programmable blending), by never letting the CPU and GPU wait on each other (frames in flight, precompiled pipelines), and by measuring on the device with the trace tools rather than guessing in the editor. Metal 4 raises the ceiling with explicit command memory and argument tables, but it raises the floor too: A14 and M1 or later only.

## Role Profile

At top-grossing studios this is a C++ engine or rendering engineer who owns the Metal backend of a cross-platform renderer, almost never a Swift-only role. Research on job postings found native iOS work concentrated in rendering: Scopely asks for "rendering features ... for Vulkan (Android) and Metal (iOS)" and "GPU-driven geometry ... culling, LOD"; Supercell's Clash Royale rendering role owns "CPU/GPU budgets, memory, bandwidth, battery, and device fragmentation"; Playrix's in-house C++ engine targets OpenGL ES and Metal; Sony and EA mobile ask for 5+ years of C++ plus Metal/Vulkan. Supercell's in-house Titan engine recently gained a new rendering backend for mo.co.

| Dimension | What it looks like |
| --- | --- |
| Responsibilities | Metal backend of the renderer; render graph and pass structure; shader authoring and pipeline cache; upscaling and dynamic resolution; GPU budgets per device tier; capture-driven optimization; porting desktop features to TBDR |
| Hard skills | C++ and MSL, Swift/Obj-C for the platform layer, GPU architecture (TBDR, tile memory, bandwidth), frame graphs, temporal techniques, compute culling |
| Tools | Xcode GPU frame capture, shader profiler, Instruments (Game Performance, Metal System Trace), Metal Performance HUD, `metalperftrace`, Game Porting Toolkit, Metal shader converter, RenderDoc on other backends |
| KPIs (inferred) | GPU frame time p50/p90 per device tier; sustained frame rate after 20 minutes; bandwidth per frame; shader-compile hitches per session; memory footprint |
| Collaborators | Technical artists, engine architects, iOS platform engineers, optimization/compat engineers, art direction |

Sources: https://www.workingnomads.com/jobs/senior-engineer-graphics-unannounced-project-scopely , https://hitmarker.net/jobs/supercell-senior-engine-programmer-rendering-clash-royale-4410230 , https://supercell.com/en/news/game-engine-called-titan

## When to Use / Not

Use for anything below the draw call on Apple GPUs: pass design, MSL, resource binding, synchronization, MetalFX, GPU profiling, Mac ports of Windows renderers.

Not for: Swift game loop, StoreKit, GameKit, thermal policy plumbing (`gamedev-ios-engineer`); shader look development, VFX and texture compression choices (`gamedev-technical-artist`); device tier matrix and cross-platform budgets (`gamedev-optimization-compatibility`); Unity URP configuration (`gamedev-unity-engineer`); Steam/Mac packaging and notarization (`gamedev-desktop-engineer`); engine-wide architecture (`gamedev-engine-architect`).

## Inputs to Gather

- **Device floor:** oldest GPU family supported. Default: A13 and M1 for Metal 3 work; A14 and M1 if Metal 4 is required. Intel/AMD Macs need non-TBDR fallbacks (no memoryless).
- **Frame targets per tier:** default 60 fps (16.67 ms) with a sustained-GPU target of about 80% of budget; 120 fps only on ProMotion tiers with headroom.
- **Native resolution policy:** fixed scale, dynamic resolution, or MetalFX? Default: render at 0.6 to 0.75 of display on phones and upscale.
- **Renderer shape:** forward, forward+, deferred, visibility buffer; number of passes; post stack.
- **Content:** draw count, material count, texture memory, shader variant count. Variant count drives compile hitches.
- **Captures:** a GPU frame capture and a 60 s Game Performance trace from the worst scene on the floor device. Without these, any advice is conjecture.
- **Port source:** if porting, DX11 or DX12? It decides the Game Porting Toolkit path.

## Method

1. **Capture before changing anything.** Take a Game Performance trace on the floor device in the worst scene, plus a GPU frame capture. Decide whether the frame is CPU-bound, GPU-bound, or stalled (CPU and GPU both idle while waiting on each other). Optimizing the wrong side is the most common wasted week.
2. **Fix synchronization first.** Use 3 frames in flight with a semaphore, never `waitUntilCompleted` in the frame, and acquire the drawable as late as possible. Stalls masquerade as GPU cost in naive measurements.
3. **Design passes around the tile.** For each render pass, write down every attachment's load action, store action and storage mode. Intermediates that are never sampled later (depth after the opaque pass, MSAA color, G-buffer in a single-pass deferred) become `.memoryless` with `.dontCare` store. Every unnecessary `.store` is a full-resolution write to system memory.
4. **Merge passes where the tile allows it.** Single-pass deferred via programmable blending (framebuffer fetch), tile shaders, and imageblocks keep the G-buffer on-chip. Splitting into separate passes because "that's how the desktop renderer does it" multiplies bandwidth.
5. **Bind with argument buffers and heaps.** Use Metal 3 bindless (`gpuResourceID`, `gpuAddress`) to cut per-draw CPU cost, sub-allocate from heaps, alias transient render targets, and make residency explicit (`useHeap`, `useResource`, or residency sets). Heaps default to untracked hazards, so add fences or barriers yourself.
6. **Kill shader-compile hitches.** Precompile `.metallib` offline, build pipelines asynchronously at load, and harvest pipeline descriptors into a binary archive during QA play so release builds compile nothing in gameplay.
7. **Render fewer pixels, then upscale.** Adopt the MetalFX temporal upscaler with correct jitter, motion vectors and reset on camera cuts. Consider frame interpolation and denoising only after base frame pacing is stable, and read WWDC25 session 211 for the generated-frame ratio rather than trusting press numbers.
8. **Gate Metal 4 behind a capability check.** Adopt `MTL4CommandAllocator` (one per encoding thread), `MTL4CommandBuffer`, and `MTL4ArgumentTable` in a backend that can fall back to Metal 3 for A13 and older Macs.
9. **Instrument for the field.** Tag game states with StateReporting, ship the Metal Performance HUD behind a debug flag, and read MetricKit Metal frame rate by state after release. Lab numbers on a cold device overstate field performance.

## Deliverables

### 1. Render Pass Ledger (one row per attachment per pass)

```
Pass │ Attachment │ Format       │ Storage     │ Load     │ Store    │ Sampled later? │ Bytes/frame to memory
Opaq │ color0     │ bgra8Unorm 4x│ memoryless  │ clear    │ multisampleResolve │ resolve -> drawable │ W*H*4 (resolve only)
Opaq │ depth      │ depth32Float │ memoryless  │ clear    │ dontCare │ no             │ 0
...
TOTAL bandwidth estimate: [MB/frame] x fps = [GB/s]   (target: as low as the look allows)
```

Any row with `store` and "Sampled later? = no" is a bug.

### 2. GPU Budget Sheet

```
Tier │ Device floor │ Target fps │ Frame ms │ GPU budget (80%) │ Render scale │ Upscaler │ Measured GPU p50/p90 │ Sustained after 20 min
A    │              │ 120 / 60   │          │                  │              │          │                      │
B    │              │ 60         │ 16.67    │ 13.3             │              │          │                      │
C    │              │ 30-60      │          │                  │              │          │                      │
```

### 3. Frames-in-flight renderer skeleton (Metal 3)

```swift
import MetalKit

final class Renderer: NSObject, MTKViewDelegate {
    static let framesInFlight = 3
    private let device: MTLDevice
    private let queue: MTLCommandQueue
    private let inFlight = DispatchSemaphore(value: Renderer.framesInFlight)
    private let uniforms: [MTLBuffer]          // one per frame in flight, .storageModeShared
    private var frame = 0

    init?(view: MTKView) {
        guard let device = view.device, let queue = device.makeCommandQueue() else { return nil }
        self.device = device; self.queue = queue
        uniforms = (0..<Renderer.framesInFlight).compactMap { _ in
            device.makeBuffer(length: MemoryLayout<FrameUniforms>.stride, options: .storageModeShared)
        }
        super.init()
    }

    func draw(in view: MTKView) {
        inFlight.wait()                                    // CPU never overwrites data the GPU is reading
        frame = (frame + 1) % Renderer.framesInFlight
        writeUniforms(into: uniforms[frame])
        guard let cb = queue.makeCommandBuffer() else { inFlight.signal(); return }
        cb.addCompletedHandler { [inFlight] _ in inFlight.signal() }

        encodeOffscreenPasses(cb)                          // shadows, compute culling: no drawable needed
        if let pass = view.currentRenderPassDescriptor,    // acquire the drawable as late as possible
           let drawable = view.currentDrawable,
           let enc = cb.makeRenderCommandEncoder(descriptor: pass) {
            encodeMainPass(enc, uniforms: uniforms[frame])
            enc.endEncoding()
            cb.present(drawable)
        }
        cb.commit()
    }

    func mtkView(_ view: MTKView, drawableSizeWillChange size: CGSize) { resizeTargets(size) }
}
```

### 4. Memoryless depth and MSAA for a single on-chip pass

```swift
func makeTransientTargets(device: MTLDevice, size: MTLSize) -> (MTLTexture, MTLTexture)? {
    let depth = MTLTextureDescriptor.texture2DDescriptor(pixelFormat: .depth32Float,
                    width: size.width, height: size.height, mipmapped: false)
    depth.usage = .renderTarget
    depth.storageMode = .memoryless                       // lives only in tile memory (Apple GPUs)
    let msaa = MTLTextureDescriptor.texture2DDescriptor(pixelFormat: .bgra8Unorm, // must match resolve target
                    width: size.width, height: size.height, mipmapped: false)
    msaa.textureType = .type2DMultisample; msaa.sampleCount = 4
    msaa.usage = .renderTarget; msaa.storageMode = .memoryless
    guard let d = device.makeTexture(descriptor: depth), let m = device.makeTexture(descriptor: msaa) else { return nil }
    return (d, m)
}
// pass.depthAttachment: loadAction = .clear, storeAction = .dontCare
// pass.colorAttachments[0]: texture = msaa, resolveTexture = drawable, storeAction = .multisampleResolve
```

Read `references/metal-snippets.md` when writing MSL (single-pass deferred with framebuffer fetch, argument buffers, compute culling), heaps with aliasing, MetalFX upscaler setup, binary archives, or the Metal 4 command model. Read `references/profiling-playbook.md` when running a capture, a long trace, field MetricKit analysis, or a Game Porting Toolkit evaluation.

## Technical Reference

### Metal versions and hardware floor (as of 2026-10; verify)

| Version | Floor | What it adds |
| --- | --- | --- |
| Metal 3 (WWDC22) | A13 and M1 or later on Apple GPUs (verify exact family list) | Bindless argument buffers via `gpuResourceID` / `gpuAddress`, mesh shaders, fast resource loading, MetalFX spatial and temporal upscaling |
| Metal 4 (WWDC25) | **A14 Bionic (iPhone 12) or later, M1 or later**, Apple Vision Pro | `MTL4CommandAllocator` (explicit command memory, one per encoding thread, reusable after `endCommandBuffer`), `MTL4CommandBuffer` with `beginCommandBuffer(allocator:)`, `MTL4ArgumentTable` replacing per-encoder binding, tensors and ML inside shaders, MetalFX frame interpolation and denoising |
| WWDC26 additions | Neural Accelerators on M5 Pro / M5 Max for the new upscaler | Redesigned MetalFX temporal upscaler using the Neural Engine; subrect processing for dynamic resolution; caller-supplied motion vectors; distortion fields; quantized tensor formats |

Sources: https://developer.apple.com/metal/ , https://developer.apple.com/documentation/metal/understanding-the-metal-4-core-api , https://developer.apple.com/wwdc26/guides/metal/

### TBDR rules of thumb

| Rule | Why |
| --- | --- |
| `.memoryless` for anything not sampled after its pass | Zero system-memory allocation and zero store bandwidth |
| `.dontCare` load when every pixel is overwritten; `.clear` instead of a full-screen clear draw | A `.load` reads the whole attachment from memory into tile memory |
| `.dontCare` store for depth after the last depth test | Depth stores are a full-resolution write nobody reads |
| Resolve MSAA in-tile (`.multisampleResolve`) | 4x MSAA on TBDR is nearly free in bandwidth when the samples never leave the tile |
| Programmable blending / tile shaders for deferred lighting | G-buffer stays on-chip; one pass instead of two |
| `.private` storage for GPU-only textures | Enables lossless GPU compression and avoids CPU coherency cost |
| Avoid mid-pass encoder switches and pass splits | Each new pass flushes and reloads tiles |
| ASTC on iOS; check `supportsBCTextureCompression` on Mac and iPad for BC | Avoid shipping two texture sets when one suffices |

### MetalFX

- **Upscaling** (Metal 3): spatial (cheap, no history) and temporal (needs jitter, depth, motion vectors, reset on cuts).
- **Frame interpolation and denoising** (Metal 4, WWDC25 session 211). Sources disagree on the interpolation ratio; treat session 211 as the authority (https://developer.apple.com/videos/play/wwdc2025/211). Interpolation adds latency; never use it to rescue an unstable base frame rate.
- Typical phone render scale: 0.6 to 0.75 of display per axis with temporal upscaling (heuristic; validate per art style, since thin geometry and UI-in-world suffer first). Render UI after the upscaler at native resolution.

### Frame budgets

| Rate | Frame | GPU budget at ~80% (heuristic) |
| --- | --- | --- |
| 30 fps | 33.3 ms | 26.7 ms |
| 60 fps | 16.67 ms | 13.3 ms |
| 120 fps | 8.33 ms | 6.7 ms |

### Profiling and field data

- Instruments **Game Performance** template (Metal System Trace plus thread state, syscalls, VM, Points of Interest) for stutter; **Metal System Trace** for CPU/GPU parallelism; WWDC26 **Game Performance Overview** for long captures.
- Look-back collection: macOS `metalperftrace collect /tmp --last 5h` and `metalperftrace overview --json`; iOS Developer settings, Performance Trace, Lookback.
- **StateReporting** (`SRStateReporter reporterForDomain:`) tags traces with game state.
- **Metal Performance HUD**: in-game FPS, frame interval, memory.
- **MetricKit** reports Metal frame rate by state on macOS and iOS 27, plus memory-limit terminations (as of 2026-10; verify that iOS 27 shipped and the field is live). Source: https://developer.apple.com/videos/play/wwdc2026/388/

### Game Porting Toolkit (as of 2026-10; verify)

- Lineage: GPTK 1 (WWDC23), GPTK 2 (WWDC24), GPTK 3 (WWDC25: sparse buffers and textures, performance insights for Windows games), **GPTK 4 (WWDC26)**: evaluation environment supports Metal 4, command-line Metal capture/debug/profile, and open-source agent skills plus sample code at https://github.com/apple/game-porting-toolkit .
- DX12 titles translate to Metal 4; **DX11 falls back to Metal 3**. One press test reported about 10% more frames for a DX12 title on M3 Max via the Metal 4 path (secondary source; reproduce before quoting).
- The evaluation environment answers "is a port viable"; shipping still means a native Metal backend and shaders converted with Metal shader converter.

## Diagnostics

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| GPU and CPU both under budget, frame rate still low | Synchronization stall: `waitUntilCompleted`, single uniform buffer, early drawable acquisition | Semaphore with 3 frames in flight; acquire drawable last; per-frame buffers |
| Frame time fine for 5 minutes, then degrades | Thermal throttling driven by bandwidth | Pass ledger: remove needless stores, memoryless intermediates, lower render scale, upscale |
| One-off 50 to 200 ms hitches on first sight of an effect | Runtime pipeline compilation | Offline `.metallib`, async pipeline creation at load, binary archive harvested in QA |
| High "Load/Store" or memory bandwidth counters in capture | `.load`/`.store` on transient attachments, or pass split | Fix actions; merge passes; programmable blending |
| Corruption flicker after moving resources into a heap | Untracked hazards in heap resources | Add `MTLFence` (Metal 3) or explicit barriers (Metal 4) between producer and consumer passes |
| Black or missing textures with argument buffers | Resource not made resident | `useResource`/`useHeap` per encoder, or residency sets |
| Ghosting and smearing with temporal upscaler | Missing or wrong-scale motion vectors, no jitter, no reset on camera cut | Provide per-pixel motion in input-resolution pixels, Halton jitter, `reset = true` on cuts |
| Crash or validation error on older iPhone after Metal 4 adoption | Device below A14 | Capability check and Metal 3 fallback path |
| Mac port fast on M-series Pro, slow on base M1 | Bandwidth and memory differences hidden by the big chip | Profile on the floor Mac; tier render scale |
| Field frame rate far below lab | Lab devices cold and on charger; states not tagged | MetricKit by state; StateReporting; test after a 20 min warm-up |

## Anti-Patterns

**The Desktop Pass Graph** — porting a 12-pass desktop renderer pass-for-pass. Every pass boundary is a tile flush; the phone spends its power budget moving G-buffers.

**Store Everything** — default `.store` on every attachment "to be safe". It is the single largest avoidable bandwidth cost on Apple GPUs.

**The Synchronous Frame** — `commandBuffer.waitUntilCompleted()` in the render loop. CPU and GPU take turns idling, and both profilers look fine.

**Compile on First Use** — building pipeline states when an effect first appears. Players see hitches in exactly the moments that matter: first boss, first ultimate.

**Interpolation as a Crutch** — enabling frame interpolation to hide an unstable 30 fps. It adds latency and amplifies pacing errors instead of fixing them.

**Metal 4 Without a Floor** — adopting Metal 4 APIs with no Metal 3 path while the install base still includes A13 devices.

**Profiling the Simulator or a Cold Device** — numbers from the simulator, or from a device that has been idle on a desk, are not your players' numbers.

## Quality Checklist

- [ ] Captures (GPU frame plus 60 s trace) from the floor device exist for the worst scene
- [ ] Render pass ledger complete; no attachment is stored without being sampled later
- [ ] Transient depth, MSAA and G-buffer targets are memoryless on Apple GPUs, with fallbacks on non-TBDR Macs
- [ ] 3 frames in flight with a semaphore; no `waitUntilCompleted` in the frame; drawable acquired last
- [ ] Argument buffers or tables in use; residency explicit; heap hazards fenced
- [ ] All pipelines precompiled; binary archive harvested; zero runtime compiles in a gameplay trace
- [ ] MetalFX temporal path supplies jitter, motion vectors, depth, and resets on cuts; UI rendered at native resolution
- [ ] Metal 4 gated on capability with a Metal 3 fallback for A13 and older Macs
- [ ] GPU p90 within 80% of budget per tier and sustained after a 20 minute warm-up
- [ ] StateReporting tags and MetricKit ingestion in place for field frame rate
- [ ] Date-sensitive version claims carry an as-of tag

## Related Skills

The Swift loop, display link, thermal governor and store live in `gamedev-ios-engineer`; this skill supplies the renderer they drive and the knobs (render scale, frame cap) the thermal policy turns. Shader look, VFX budgets and texture formats are co-owned with `gamedev-technical-artist`. Device tiers, memory budgets and the compatibility matrix belong to `gamedev-optimization-compatibility`. Render graph and engine-wide threading model: `gamedev-engine-architect`. Mac distribution, Steam and notarization after a port: `gamedev-desktop-engineer`. The Android counterpart (Vulkan, AGI) is `gamedev-android-engineer`. Unity URP specifics: `gamedev-unity-engineer`. Art-side poly and texel budgets that feed the GPU budget: if installed, `game-asset-art-director`.
