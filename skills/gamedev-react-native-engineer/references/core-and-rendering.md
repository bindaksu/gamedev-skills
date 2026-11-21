# Sim Core, Threads and Rendering for React Native Games

Read the section you need. TypeScript snippets were syntax-checked with TypeScript 5.9; API names were checked against the published type definitions of react-native-reanimated 4.8.0, react-native-worklets 0.14.0, @shopify/react-native-skia 2.14.0 and metro-config 0.88 (npm registry, 2026-11-21). Verify against the versions you pin.

## 1. Package layout

```text
packages/core     pure TypeScript sim: no react-native imports, no Date.now(), no Math.random();
                  seeded RNG and fixed ticks; runs unchanged in Node (tests, server) and Hermes
packages/app      Expo app: screens, Skia renderer, gestures -> commands, platform modules
packages/native   optional Rust crate: wasm32 build for Node, xcframework / Android library via JSI
packages/tools    generators, corpora, perf harness; API keys live here, never in the app
```

Rules:
- The app imports the core; the core never imports the app. A lint rule forbids `react-native`, `expo-*` and wall-clock APIs inside `packages/core`.
- Commands are plain serializable objects; the core's state is plain data that can be snapshotted to bytes.
- Determinism, tick model and save envelope design come from the engine-architect seat; this seat makes them run on Hermes and on device.

## 2. Inline requires in hot loops

React Native's default Metro config turns inline requires on (checked in @react-native/metro-config 0.88.1). Each read of an imported binding then compiles to a require call plus a property get. In a tick loop that reads imported helpers thousands of times per simulated day, exempting the sim modules raised throughput by 15-26% in one strategy sim.

```js
// metro.config.js
const path = require('path');
const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

// Modules whose imported bindings are read inside the tick loop.
const hotSimModules = [
  '../../packages/core/src/sim/tick.ts',
  '../../packages/core/src/sim/systems.ts',
  '../../packages/core/src/sim/pathing.ts',
].map((p) => path.resolve(__dirname, p));

config.transformer.getTransformOptions = async () => ({
  transform: {
    experimentalImportSupport: false,
    // Inline requires defer module init (good for cold start) but turn every read of an
    // imported binding into a require call plus a property get. Exempt the hot modules;
    // keep the package barrel and UI inline.
    inlineRequires: { blockList: Object.fromEntries(hotSimModules.map((p) => [p, true])) },
  },
});

module.exports = config;
```

- Keep inline requires for the package barrel and UI: they protect cold start.
- Metro 0.88 also has `unstable_memoizeInlineRequires`, which caches the module in a local variable; treat it as experimental and measure both.
- Confirm on a Release build on device; dev builds run different transforms.

## 3. Where the sim runs

| Option | Use when | Cost |
|---|---|---|
| JS thread, time-sliced | Turn-based, light per-tick work, early prototypes | Competes with React commits and touch handling; must yield |
| Worklet runtime (`createWorkletRuntime` with `scheduleOnRuntime` / `runOnRuntime`) | Real-time sims that must not block the JS thread | Separate heap; data crosses by serialization; debugging is harder |
| Native core through JSI (Rust or C++) | Heavy sims, long fast-forward, shared core with a server | Build pipeline per platform; boundary design matters most |

```ts
// Long passes on the JS thread (cloud sync, catch-up after resume, save load) must yield,
// or timers, touches and React commits wait for the whole pass.
export async function runSliced<T>(
  items: readonly T[],
  work: (item: T) => void,
  budgetMs = 12,
): Promise<void> {
  let sliceStart = performance.now();
  for (const item of items) {
    work(item);
    if (performance.now() - sliceStart >= budgetMs) {
      await new Promise<void>((resolve) => setTimeout(resolve, 0));
      sliceStart = performance.now();
    }
  }
}
```

A sync pass that never yielded stalled JS timers for seconds; yielding every 10-15 ms brought the gap under 100 ms.

## 4. Worklets without leaks

```tsx
import { useFrameCallback, useSharedValue } from 'react-native-reanimated';

// Camera inertia on the UI runtime. Scalars in shared values; no per-frame allocation,
// no worklet created inside the frame callback, nothing sent back to JS per frame.
export function useCameraInertia(friction = 0.9) {
  const x = useSharedValue(0);
  const y = useSharedValue(0);
  const vx = useSharedValue(0);
  const vy = useSharedValue(0);

  useFrameCallback((frame) => {
    'worklet';
    const dt = frame.timeSincePreviousFrame ?? 16.7;
    x.value += vx.value * dt;
    y.value += vy.value * dt;
    const decay = Math.pow(friction, dt / 16.7);
    vx.value *= decay;
    vy.value *= decay;
  });

  return { x, y, vx, vy };
}

// Not this, inside a frame callback:
//   runOnJS(setHud)({ ...hudState })          // new object serialized every frame
//   scheduleOnRN(() => store.tick())          // new inline worklet created every frame
```

Rules:
- Define worklets once (module scope, or hooks with stable dependencies). Never create an inline worklet inside a frame callback.
- The serializer caches a native copy keyed by the JS object it was given (worklets 0.14 exposes the mapping through `getSerializableMapping`, `hasSerializableMapping` and `removeSerializableMapping`). A long-lived sender object keeps its native copy alive; a fresh object per call costs a serialization per call. Send ids, numbers and typed arrays.
- Per-frame values live in shared values on the UI runtime. Cross to JS at most a few times per second for HUD text.
- `makeShareable` and related names are deprecated in worklets 0.14; use the `createSerializable*` family when you need explicit control.

## 5. Heaps and profiling

- Each runtime has its own heap: the React Native (Hermes) runtime, the UI worklet runtime, and each worker runtime. Native memory (Skia textures, decoded images, audio) sits outside all of them. Sample each one separately; one heap looking flat proves nothing about the others.
- Release Hermes builds cannot take heap snapshots. Find leaks in a profiling build, and confirm in Release with the process footprint (Instruments, or the OS memory report).
- For sim hot spots, `node --no-opt --no-maglev --no-sparkplug` runs V8's interpreter only (flags present in Node 22). Its ranking of hot functions approximates an interpreter-only device engine [inference]; confirm every win on device.
- Time-compressed sims leak per simulated day, not per minute. Soak at the top game speed across the full campaign horizon, report growth per simulated day and per minute, then load the soak's late save in a fresh process: the difference between the two footprints is accumulated garbage, not game state. The OS can kill the app at the memory limit with no crash report.

## 6. Skia rendering budgets

| Approach | Cost moves to | Use when |
|---|---|---|
| Vector paths every frame | CPU/GPU rasterization | Few, simple shapes; zoom-dependent detail |
| `createPicture` / `drawAsPicture` for static layers | Recording once, replaying cheaply | Layers that change rarely |
| Prebaked raster tiles | Decode and GPU upload; resident texture memory | Very complex static art, only if the resident set fits the GPU cache |
| `Atlas` with `useRSXformBuffer` | One draw for many sprites | Units, particles, icons |

- Prebaking tiles removed path rasterization entirely in one map renderer, yet pan p99 rose from 33 to 83 ms: the tile working set (204-397 MB RGBA8) exceeded a 256 MB GPU resource cache, so tiles re-uploaded on every pan, and upload bursts risked a memory kill. Size the resident set per zoom band against the cache, prefer compressed or palette formats, upload off-frame, and keep vectors where the tile set would be largest.
- Skia's Ganesh resource cache defaults to 256 MB unless the host sets it. react-native-skia 2.14 exposes no JS setter (checked in the package source); setting it means a native patch (production apps capped it at 192 MiB), and that patch must be verified inside the built archive (see the build reference).
- Decode images asynchronously (`useImage`, or `Skia.Data.fromURI` then `Skia.Image.MakeImageFromEncoded` off the UI thread). Never call `dispose()` from JS on an object the UI thread may still draw; drop references and let the owner release it.
- Find native Skia crashes with AddressSanitizer in a Release-configured build; debug builds hide timing-dependent use-after-free.

```tsx
import { useMemo } from 'react';
import { Atlas, Canvas, Skia, useImage, useRSXformBuffer } from '@shopify/react-native-skia';
import type { SharedValue } from 'react-native-reanimated';

const TILE = 32;

// Many sprites from one atlas image: one draw, transforms written on the UI thread.
// The sim assigns a new positions array once per sim tick, never once per frame.
export function UnitLayer({ count, positions }: { count: number; positions: SharedValue<Float32Array> }) {
  const sheet = useImage(require('../assets/units.png')); // decoded asynchronously, not on the UI thread
  const sprites = useMemo(() => Array.from({ length: count }, (_, i) =>
    Skia.XYWHRect((i % 8) * TILE, Math.floor(i / 8) * TILE, TILE, TILE)), [count]);
  const transforms = useRSXformBuffer(count, (val, i) => {
    'worklet';
    const p = positions.value;
    val.set(1, 0, p[i * 2], p[i * 2 + 1]);   // scos, ssin, tx, ty
  });
  if (!sheet) return null;
  return (
    <Canvas style={{ flex: 1 }}>
      <Atlas image={sheet} sprites={sprites} transforms={transforms} />
    </Canvas>
  );
}
```

## 7. Native core boundary

```ts
// The same Rust core runs as wasm32 in Node (tests, server validation) and as a native
// library through JSI on device. With wasm, memory.grow detaches every view over the old
// buffer: re-create views after any call that can allocate.
type CoreExports = {
  memory: WebAssembly.Memory;
  step_day(statePtr: number): void;
  state_ptr(): number;
  state_len(): number;
};

export class WasmCore {
  private bytes: Uint8Array;

  constructor(private readonly core: CoreExports) {
    this.bytes = new Uint8Array(core.memory.buffer);
  }

  private view(): Uint8Array {
    if (this.bytes.buffer !== this.core.memory.buffer) {
      this.bytes = new Uint8Array(this.core.memory.buffer); // old buffer is detached (length 0)
    }
    return this.bytes;
  }

  stepDay(): void {
    this.core.step_day(this.core.state_ptr());
  }

  snapshot(): Uint8Array {
    const ptr = this.core.state_ptr();
    return this.view().slice(ptr, ptr + this.core.state_len()); // copy out, then hash or save
  }
}
```

- Port whole phases in order of measured cost, over shared memory (borrow the JS buffer, or native-owned columns read through views). Leaf kernels called per entity from JS lose their gain to marshalling: a kernel more than ten times faster made the simulated day slower.
- Promote a phase only on byte parity (golden corpus, snapshot bytes, device-runtime checksum), delete the old path, and freeze gameplay edits to that phase while it is being ported.
- Build the Apple slices (device, simulator, macOS if needed) into one xcframework and record the toolchain that built it.

## 8. Determinism on more than one engine

```ts
// Every sort whose output feeds goldens, replays or saves gets a total order.
// An inconsistent comparator leaves the order implementation-defined, and native ports
// often use unstable sorts, so equal keys must still break deterministically.
export interface Ranked { id: number; score: number; tier: number }

export function byScoreThenId(a: Ranked, b: Ranked): number {
  if (a.score !== b.score) return b.score - a.score;
  if (a.tier !== b.tier) return a.tier - b.tier;
  return a.id - b.id; // stable-ID tie-break: never 0 for two different entities
}

// Math.hypot, Math.pow, Math.exp and trig are implementation-approximated in JS and can
// differ between engines and from Rust's libm. Route sim math through one helper module.
export function distSq(ax: number, ay: number, bx: number, by: number): number {
  const dx = ax - bx;
  const dy = ay - by;
  return dx * dx + dy * dy; // + and * are exact IEEE operations everywhere
}
```

```ts
// packages/core/test/parity.test.ts: the corpus is generated once, checked on every engine
import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { newGame, applyCommands, snapshotBytes } from '../src';

type Case = { seed: number; commands: string[]; days: number; sha256: string };
const corpus: Case[] = JSON.parse(readFileSync(new URL('./parity-corpus.json', import.meta.url), 'utf8'));

describe('sim parity corpus', () => {
  for (const c of corpus) {
    it(`seed ${c.seed} over ${c.days} days`, () => {
      const game = applyCommands(newGame(c.seed), c.commands, c.days);
      const digest = createHash('sha256').update(snapshotBytes(game)).digest('hex');
      expect(digest).toBe(c.sha256);
    });
  }
});
```

Generate the corpus once, then check it in Node, in Hermes on a device build (a debug screen or test hook that runs the corpus and reports digests), and in the native port. In one sim, presentation output on the device engine differed from a desktop-made corpus on about 30% of calls until ties were broken by id.
