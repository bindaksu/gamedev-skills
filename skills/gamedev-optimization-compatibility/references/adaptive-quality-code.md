# Adaptive Quality, Thermal and Memory Code

Shapes to adapt, not drop-in libraries. API levels and names as of 2026-10; verify against current SDK docs.

## 1. Android: ADPF thermal headroom + Performance Hint (Kotlin)

```kotlin
import android.content.Context
import android.os.Build
import android.os.PerformanceHintManager
import android.os.PowerManager
import android.os.Process

class AdpfController(context: Context) {
    private val power = context.getSystemService(PowerManager::class.java)
    private val hintManager: PerformanceHintManager? =
        if (Build.VERSION.SDK_INT >= 31) context.getSystemService(PerformanceHintManager::class.java) else null
    private var session: PerformanceHintManager.Session? = null
    private var lastHeadroomPollNs = 0L
    private var cachedHeadroom = 0f

    /** Call once from the game thread after the render thread exists. */
    fun startSession(renderThreadTid: Int, targetFrameNs: Long) {
        if (Build.VERSION.SDK_INT < 31) return
        val tids = intArrayOf(Process.myTid(), renderThreadTid)
        session = hintManager?.createHintSession(tids, targetFrameNs)
    }

    /** Call every frame with measured CPU work (not wall time incl. vsync wait). */
    fun reportFrame(actualWorkNs: Long) {
        session?.reportActualWorkDuration(actualWorkNs)
    }

    fun setTargetFps(fps: Int) {
        session?.updateTargetWorkDuration(1_000_000_000L / fps)
    }

    /**
     * 0.0 = no throttling, 1.0 = severe throttling. NaN if unsupported.
     * Poll at most about once per second; frequent calls return stale or NaN values.
     */
    fun thermalHeadroom(nowNs: Long, forecastSeconds: Int = 10): Float {
        if (Build.VERSION.SDK_INT < 30) return Float.NaN
        if (nowNs - lastHeadroomPollNs >= 1_000_000_000L) {
            cachedHeadroom = power.getThermalHeadroom(forecastSeconds)
            lastHeadroomPollNs = nowNs
        }
        return cachedHeadroom
    }

    fun close() { session?.close(); session = null }
}
```

Fallback for API 29: `PowerManager.addThermalStatusListener` with `THERMAL_STATUS_*` levels (coarser, reactive rather than predictive). Native engines use the NDK equivalents (`APerformanceHint_*`, `AThermal_*`); Unity's Adaptive Performance Android provider and Unreal's ADPF plugin wrap these.

## 2. Android: memory pressure (Kotlin)

```kotlin
import android.app.ActivityManager
import android.app.ApplicationExitInfo
import android.content.ComponentCallbacks2
import android.content.Context
import android.os.Build

class MemoryWatcher(private val context: Context, private val onPressure: (Level) -> Unit) : ComponentCallbacks2 {
    enum class Level { BACKGROUND, LOW }

    private val am = context.getSystemService(ActivityManager::class.java)

    fun snapshot(): String {
        val info = ActivityManager.MemoryInfo().also { am.getMemoryInfo(it) }
        return "avail=${info.availMem / 1_048_576}MB total=${info.totalMem / 1_048_576}MB " +
               "low=${info.lowMemory} threshold=${info.threshold / 1_048_576}MB lowRam=${am.isLowRamDevice}"
    }

    override fun onTrimMemory(level: Int) {
        // Running-level constants are deprecated on recent API levels; treat UI_HIDDEN/BACKGROUND as signals to drop caches.
        if (level >= ComponentCallbacks2.TRIM_MEMORY_BACKGROUND) onPressure(Level.BACKGROUND)
        else if (level >= ComponentCallbacks2.TRIM_MEMORY_UI_HIDDEN) onPressure(Level.LOW)
    }
    override fun onConfigurationChanged(newConfig: android.content.res.Configuration) {}
    @Deprecated("Deprecated in Java") override fun onLowMemory() = onPressure(Level.LOW)

    /** Report previous-session kills (API 30+) to telemetry on next launch. */
    fun reportPreviousExits(send: (String) -> Unit) {
        if (Build.VERSION.SDK_INT < 30) return
        am.getHistoricalProcessExitReasons(context.packageName, 0, 5).forEach { e ->
            if (e.reason == ApplicationExitInfo.REASON_LOW_MEMORY || e.reason == ApplicationExitInfo.REASON_ANR) {
                send("exit reason=${e.reason} pss=${e.pss}KB rss=${e.rss}KB ts=${e.timestamp}")
            }
        }
    }
}
```

Register with `context.registerComponentCallbacks(watcher)`. The Memory Advice API (AGDK, Beta) estimates native plus GL/Vulkan memory and warns at thresholds; evaluate it before rolling your own estimator.

## 3. iOS: thermal state + memory (Swift)

```swift
import Foundation
import UIKit
import os

final class DevicePressureMonitor {
    enum Thermal: Int { case nominal, fair, serious, critical }

    var onThermal: ((Thermal) -> Void)?
    var onMemoryWarning: (() -> Void)?
    private var observers: [NSObjectProtocol] = []

    func start() {
        let nc = NotificationCenter.default
        observers.append(nc.addObserver(forName: ProcessInfo.thermalStateDidChangeNotification,
                                        object: nil, queue: .main) { [weak self] _ in
            self?.publishThermal()
        })
        observers.append(nc.addObserver(forName: UIApplication.didReceiveMemoryWarningNotification,
                                        object: nil, queue: .main) { [weak self] _ in
            self?.onMemoryWarning?()
        })
        publishThermal()
    }

    private func publishThermal() {
        let state: Thermal
        switch ProcessInfo.processInfo.thermalState {
        case .nominal: state = .nominal
        case .fair: state = .fair
        case .serious: state = .serious
        case .critical: state = .critical
        @unknown default: state = .serious
        }
        onThermal?(state)
    }

    /// Bytes the process can still allocate before hitting its jetsam limit (iOS 13+).
    func availableMemoryBytes() -> Int { Int(os_proc_available_memory()) }

    deinit { observers.forEach(NotificationCenter.default.removeObserver) }
}
```

Poll `availableMemoryBytes()` once per second during loads and log the minimum per session: that minimum is your real headroom on that device. Test thermal states on device by simulating conditions from Xcode's Devices window.

### ProMotion frame rate (Swift)

```swift
let link = CADisplayLink(target: renderer, selector: #selector(Renderer.step(_:)))
link.preferredFrameRateRange = CAFrameRateRange(minimum: 60, maximum: 120, preferred: 120)
link.add(to: .main, forMode: .common)
// Info.plist: CADisableMinimumFrameDurationOnPhone = YES (iPhone only; iPad Pro does not need it)
```

When thermal state reaches `.serious`, set `preferred` to 60 (or 30) rather than letting the OS throttle unpredictably.

### MetricKit field data (Swift)

```swift
import MetricKit

final class MetricsSubscriber: NSObject, MXMetricManagerSubscriber {
    func start() { MXMetricManager.shared.add(self) }
    func didReceive(_ payloads: [MXMetricPayload]) {
        for p in payloads {
            if let exits = p.applicationExitMetrics {
                let fg = exits.foregroundExitData
                upload(["memLimitExits": fg.cumulativeMemoryResourceLimitExitCount,
                        "watchdogExits": fg.cumulativeAppWatchdogExitCount,
                        "abnormalExits": fg.cumulativeAbnormalExitCount])
            }
        }
    }
    private func upload(_ dict: [String: Int]) { /* send to analytics */ }
}
```

Metal frame-rate-by-state in MetricKit is announced for iOS 27 (as of 2026-10; verify availability and API names).

## 4. Unity: quality ladder controller (C#)

```csharp
public sealed class AdaptiveQualityController : MonoBehaviour
{
    [SerializeField] private UniversalRenderPipelineAsset[] tierAssets; // index 0 = best
    [SerializeField] private float[] renderScales = { 1.0f, 0.85f, 0.75f, 0.65f };
    [SerializeField] private int[] fpsCaps = { 60, 60, 30, 30 };
    [SerializeField] private float holdUpSeconds = 60f;

    private int level;
    private float lastChange;
    private readonly FrameTimeWindow window = new(120);     // rolling p90 over ~2 s at 60 fps
    private IThermalSource thermal;                          // ADPF / thermalState / Adaptive Performance

    public void Construct(IThermalSource source) => thermal = source;

    private void Update()
    {
        window.Add(Time.unscaledDeltaTime * 1000f);
        if (Time.unscaledTime - lastChange < 5f) return;    // settle time after any change

        float budgetMs = 1000f / fpsCaps[level];
        float headroom = thermal?.Headroom ?? 0f;            // 0..1, 1 = severe
        bool overBudget = window.P90 > budgetMs * 1.1f;

        if ((headroom >= 0.75f || overBudget) && level < renderScales.Length - 1)
            Apply(level + 1);
        else if (headroom < 0.5f && window.P90 < budgetMs * 0.7f
                 && Time.unscaledTime - lastChange > holdUpSeconds && level > 0)
            Apply(level - 1);
    }

    private void Apply(int newLevel)
    {
        level = newLevel;
        lastChange = Time.unscaledTime;
        var asset = tierAssets[Mathf.Min(level, tierAssets.Length - 1)];
        GraphicsSettings.defaultRenderPipeline = asset;      // per-tier asset, not field toggles
        asset.renderScale = renderScales[level];
        Application.targetFrameRate = fpsCaps[level];
        Telemetry.Log("quality_level", level);               // so field data shows time-in-level
    }
}
```

Hysteresis is the point: down fast (5 s), up slow (60 s+), one step at a time. Log time spent per level; a device that lives at level 3 belongs in a lower tier.

Unity Adaptive Performance exposes thermal warnings through `Holder.Instance.ThermalStatus.ThermalMetrics` (warning level, temperature level and trend) and can drive `IThermalSource`; verify the API shape against the package version you install.

## 5. Menus and idle screens

```csharp
// Unity: render menus at a lower rate while keeping input at full rate.
OnDemandRendering.renderFrameInterval = 2;   // 60 Hz display → 30 fps rendering
```

Menus, shop and map screens uncapped at 60–120 fps are a common, invisible battery and thermal cost that also preheats the device before gameplay.
