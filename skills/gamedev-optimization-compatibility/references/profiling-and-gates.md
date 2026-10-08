# Profiling Commands and CI Performance Gates

Tool names and flags as of 2026-10; verify against current SDK/Xcode docs before scripting them into CI.

## Android: adb and Perfetto

```bash
PKG=com.studio.game
ACT=$PKG/com.unity3d.player.UnityPlayerActivity      # or your GameActivity subclass

# Cold start (TotalTime in ms). Repeat 10x, report median and p90.
adb shell am force-stop $PKG
adb shell am start -W -n $ACT | grep -E "TotalTime|WaitTime"

# Frame stats from the platform (HWUI-based apps; engine-rendered SurfaceViews may report little)
adb shell dumpsys gfxinfo $PKG reset
# ... play 60 s ...
adb shell dumpsys gfxinfo $PKG framestats > gfx.txt

# Memory: PSS / RSS breakdown incl. Graphics, GL mtrack
adb shell dumpsys meminfo $PKG > mem.txt

# Thermal status and throttling history
adb shell dumpsys thermalservice

# Force a thermal status to test the adaptive ladder (testing only; reset afterwards)
adb shell cmd thermalservice override-status 3
adb shell cmd thermalservice reset

# Battery: reset, play a fixed scenario unplugged (or with USB charging disabled), then dump
adb shell dumpsys batterystats --reset
adb shell dumpsys batterystats $PKG > battery.txt

# Page size check (16 KB devices / emulator images)
adb shell getconf PAGE_SIZE
```

### Perfetto system trace

```bash
# 20 s trace with scheduling, frequency, GPU-adjacent and app atrace categories
adb shell perfetto -o /data/misc/perfetto-traces/game.perfetto-trace -t 20s \
  sched freq idle am wm gfx view binder_driver hal dalvik input res memory power thermal
adb pull /data/misc/perfetto-traces/game.perfetto-trace
# Open in https://ui.perfetto.dev
```

For long soaks, use a config file with ring buffer and `duration_ms`, and add GPU counters through AGI's system profiler (built on Perfetto) when the device's driver exposes them.

What to read in the trace:
- Main/game thread and render thread slices per frame; gaps waiting on GPU fences mean GPU-bound.
- CPU frequency tracks dropping over time with flat workload means thermal throttling.
- Threads running on little cores during gameplay: candidates for Performance Hint sessions.
- Long `binder` transactions or file I/O on the main thread: ANR candidates.

### AGI

- **System profiler:** CPU scheduling, GPU counters (ALU, texture, bandwidth where exposed), Vulkan call traces, memory, power. Use for CPU vs GPU attribution and bandwidth.
- **Frame profiler:** single-frame capture, per-draw cost, render passes, state. Use for overdraw, expensive shaders, redundant passes. Works with Vulkan and GLES.

### Android Performance Tuner

APT collects frame time (CPU vs GPU split) and load time plus abandonment, broken down by quality level, annotation (scene/state) and device, and shows them in Play Console Android vitals. Annotate every distinct game state so the field data maps to your tier budgets.

## Apple: Instruments and Metal tools

```bash
# List devices
xcrun xctrace list devices

# Record Game Performance template attached to the running game for 30 s
xcrun xctrace record --template 'Game Performance' --device "$UDID" \
  --attach "$PROCESS_NAME" --time-limit 30s --output game.trace

# Metal System Trace for CPU/GPU parallelism
xcrun xctrace record --template 'Metal System Trace' --device "$UDID" \
  --attach "$PROCESS_NAME" --time-limit 15s --output metal.trace

# macOS look-back collection (WWDC26): capture the last 5 hours without pre-arming
metalperftrace collect /tmp --last 5h
metalperftrace overview --json
```

iOS look-back: Developer settings, then Performance Trace, then Lookback, plus a Control Center button (as of 2026-10; verify).

Templates and what they answer:
- **Game Performance:** Metal System Trace plus thread states, system calls, virtual memory, Points of Interest — the stutter hunting default.
- **Game Performance Overview:** long captures for session-level trends.
- **Metal System Trace:** CPU encode vs GPU execution overlap, drawable waits, Metal memory.
- **Allocations / VM Tracker:** footprint growth; compare against `os_proc_available_memory()` minima.
- **Metal Performance HUD:** in-game overlay (FPS, frame interval, memory) for QA passes; enable in test builds, never ship it on.

Tag captures with game state using `os_signpost` Points of Interest and, on WWDC26 SDKs, the StateReporting API (`SRStateReporter reporterForDomain:`), so a 30-minute trace can be filtered to "level 3, combat".

## Engines

| Engine | Capture | Notes |
|---|---|---|
| Unity | Profiler connected to a Development build; Profile Analyzer for multi-frame stats; Memory Profiler snapshots diffed across a level loop | Use `ProfilerRecorder` counters in release builds for field data; development builds skew CPU numbers |
| Unreal | Unreal Insights (`-trace=cpu,gpu,frame,memory,loadtime`), `stat unit`, `stat gpu`, `memreport -full` | Insights traces stream to the trace server or a file on device; use Test configuration, not Debug/Development, for numbers |
| Godot | Built-in profiler and the C++ tracing profiler added in 4.6 | Verify availability per export template |

## Battery measurement protocol (heuristic)

1. Device at 100%, brightness fixed (50%), Wi-Fi on, cellular off, room temperature, notifications muted.
2. Run a scripted 30-minute gameplay loop (bot or replay), no charging.
3. Record % drop and average current where the device or a USB power meter exposes it.
4. Compare tiers and builds; a regression of more than ~10% relative between builds warrants investigation (heuristic).

Battery targets are studio-set; record them in the tier sheet rather than borrowing another title's numbers.

## CI performance gate

```yaml
# .ci/perf-gate.yml — run on merge to main against fixed lab devices
perf_gate:
  devices:
    - { id: low_android,  tier: low,  budget_p90_ms: 33.3, budget_peak_mem_mb: 1100 }
    - { id: mid_android,  tier: mid,  budget_p90_ms: 16.7, budget_peak_mem_mb: 1600 }
    - { id: floor_iphone, tier: low,  budget_p90_ms: 33.3, budget_peak_mem_mb: 1200 }
  scenario: "bench_scene_combat_5min"        # deterministic replay, fixed seed, fixed camera path
  warmup_seconds: 60
  tolerance_pct: 5                           # fail if over budget by more than this
  baseline: last_green_main                  # also fail if p90 regresses >8% vs baseline
  artifacts: [frame_times.csv, memory.csv, trace.perfetto-trace]
```

```python
#!/usr/bin/env python3
"""Fail CI when a perf run exceeds budget or regresses vs baseline."""
import csv, json, statistics, sys

def p(values, q):
    values = sorted(values)
    return values[min(len(values) - 1, int(q * len(values)))]

def main(run_csv, budget_json, baseline_json=None):
    frames = [float(r["frame_ms"]) for r in csv.DictReader(open(run_csv))]
    budget = json.load(open(budget_json))
    p90, p99 = p(frames, 0.90), p(frames, 0.99)
    peak = budget.get("measured_peak_mem_mb", 0)
    fails = []
    tol = 1 + budget["tolerance_pct"] / 100
    if p90 > budget["budget_p90_ms"] * tol:
        fails.append(f"p90 {p90:.1f} ms > budget {budget['budget_p90_ms']} ms")
    if peak > budget["budget_peak_mem_mb"] * tol:
        fails.append(f"peak mem {peak} MB > budget {budget['budget_peak_mem_mb']} MB")
    if baseline_json:
        base = json.load(open(baseline_json))
        if p90 > base["p90"] * 1.08:
            fails.append(f"p90 regressed {p90:.1f} vs baseline {base['p90']:.1f}")
    print(json.dumps({"p50": statistics.median(frames), "p90": p90, "p99": p99, "peak_mem_mb": peak}))
    for f in fails:
        print("PERF FAIL:", f)
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main(*sys.argv[1:])
```

Gate rules that keep the signal honest:
- Same devices, same OS, same thermal starting point (cool-down period between runs, device on a fan-cooled rack or fixed ambient).
- Deterministic scenario: replayed input or bot with fixed seed; no network variance.
- Release-configured build with the telemetry sampler, not a development build.
- Store three runs, gate on the median run, keep artifacts for 30 days so regressions can be bisected.

## Size gate

```bash
# Android: size of the universal APK / per-device split from an AAB via bundletool
java -jar bundletool.jar build-apks --bundle=game.aab --output=game.apks --mode=universal
java -jar bundletool.jar get-size total --apks=game.apks

# 16 KB alignment check for every APK built
zipalign -v -c -P 16 4 app.apk
for so in $(unzip -l app.apk | awk '/\.so$/{print $4}'); do
  unzip -o -q app.apk "$so" -d /tmp/so
  # every LOAD segment must be aligned to 2**14 or higher
  llvm-objdump -p "/tmp/so/$so" | awk '/LOAD/{print $NF}' | grep -qvE '2\*\*(1[4-9]|[2-9][0-9])' && echo "NOT 16KB: $so"
done
```

Fail the build when the base module approaches 200 MB or when download size grows beyond the per-release allowance in the tier sheet.
