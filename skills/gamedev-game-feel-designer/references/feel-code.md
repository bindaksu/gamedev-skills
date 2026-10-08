# Feel Implementation Snippets

Read when implementing hit-stop, trauma shake, a tuning panel, or platform haptics. Snippets are minimal and engine-idiomatic; verify API availability against your engine and OS versions before shipping.

## Hit-stop (Unity, C#)

Freeze gameplay time, keep UI, audio and input alive. Use unscaled time for the wait so the freeze can end.

```csharp
using System.Collections;
using UnityEngine;

public sealed class HitStop : MonoBehaviour
{
    [SerializeField] float maxStackMs = 300f;   // cap so chained hits never freeze for seconds
    float pendingUntil;                          // unscaled time when the freeze ends
    Coroutine running;

    public void Request(float ms)
    {
        float end = Mathf.Max(pendingUntil, Time.unscaledTime) + ms / 1000f;
        pendingUntil = Mathf.Min(end, Time.unscaledTime + maxStackMs / 1000f);
        running ??= StartCoroutine(Freeze());
    }

    IEnumerator Freeze()
    {
        float previous = Time.timeScale;
        Time.timeScale = 0f;
        while (Time.unscaledTime < pendingUntil) yield return null;
        Time.timeScale = previous;
        running = null;
    }
}
```

Notes: UI animations must use unscaled time; Animator components that should keep moving need `AnimatorUpdateMode.UnscaledTime`. Input buffering keeps reading during the freeze because input is not time-scaled.

## Trauma-based shake (engine-agnostic C#)

```csharp
public sealed class TraumaShake
{
    public float Trauma { get; private set; }        // 0..1
    public float DecayPerSecond = 1.5f;
    public float MaxOffset = 0.012f;                 // fraction of short screen edge
    public float MaxRotationDeg = 2f;
    public float Frequency = 22f;                    // Hz, smooth noise
    public float UserScale = 1f;                     // accessibility slider 0..1

    public void Add(float amount) => Trauma = System.Math.Min(1f, Trauma + amount);

    // returns (x, y, rotDeg); t = unscaled time, dt = unscaled delta
    public (float x, float y, float rot) Sample(float t, float dt, System.Func<float, float, float> noise)
    {
        Trauma = System.Math.Max(0f, Trauma - DecayPerSecond * dt);
        float s = Trauma * Trauma * UserScale;       // trauma^2 gives a fast-falling tail
        float n = t * Frequency;
        return (MaxOffset * s * noise(1f, n),
                MaxOffset * s * noise(2f, n),
                MaxRotationDeg * s * noise(3f, n));  // noise returns -1..1, e.g. Perlin remapped
    }
}
```

Apply the offset to a camera child transform, never to the gameplay camera's logical position, or aiming and hit tests drift.

## Tuning panel parameters (data, not code)

Keep feel values in one data asset that a debug overlay can edit live and serialize back:

```yaml
feel:
  hitstop_ms:      { light: 30, medium: 70, heavy: 130, finisher: 220 }
  shake_trauma:    { light: 0.0, medium: 0.15, heavy: 0.35, finisher: 0.6 }
  shake_decay:     1.5
  ui:
    press_ms: 60
    press_scale: 0.94
    popup_in_ms: 240
    popup_out_ms: 170
    overshoot: 1.4
  cascade:
    step_delay_ms: 80
    pitch_step_semitones: 1
    pitch_cap_steps: 7
  haptics:
    enabled: true
    max_per_second: 10
```

## iOS haptics (Swift, UIKit + Core Haptics)

```swift
import UIKit
import CoreHaptics

final class Haptics {
    private let impact = UIImpactFeedbackGenerator(style: .medium)
    private var engine: CHHapticEngine?

    init() {
        if CHHapticEngine.capabilitiesForHardware().supportsHaptics {
            engine = try? CHHapticEngine()
            try? engine?.start()
        }
    }

    /// Call shortly before an expected impact to cut start latency.
    func prepare() { impact.prepare() }

    func hit(intensity: CGFloat) { impact.impactOccurred(intensity: intensity) }

    /// Sharp transient for a heavy hit; falls back to UIKit when Core Haptics is unavailable.
    func heavyTransient() {
        guard let engine else { return hit(intensity: 1.0) }
        let event = CHHapticEvent(
            eventType: .hapticTransient,
            parameters: [
                CHHapticEventParameter(parameterID: .hapticIntensity, value: 1.0),
                CHHapticEventParameter(parameterID: .hapticSharpness, value: 0.8)
            ],
            relativeTime: 0)
        if let pattern = try? CHHapticPattern(events: [event], parameters: []),
           let player = try? engine.makePlayer(with: pattern) {
            try? player.start(atTime: CHHapticTimeImmediate)
        }
    }
}
```

Handle engine reset/stopped handlers (the engine stops when the app backgrounds) and respect an in-game haptics toggle.

## Android haptics (Kotlin)

```kotlin
import android.os.Build
import android.os.VibrationEffect
import android.os.Vibrator
import android.view.HapticFeedbackConstants
import android.view.View

class Haptics(private val vibrator: Vibrator, private val view: View) {

    fun tap() {
        // Respects the user's system touch-feedback setting.
        view.performHapticFeedback(HapticFeedbackConstants.KEYBOARD_TAP)
    }

    fun hit(scale: Float) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R &&
            vibrator.areAllPrimitivesSupported(VibrationEffect.Composition.PRIMITIVE_CLICK)) {
            vibrator.vibrate(
                VibrationEffect.startComposition()
                    .addPrimitive(VibrationEffect.Composition.PRIMITIVE_CLICK, scale.coerceIn(0f, 1f))
                    .compose())
        } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            vibrator.vibrate(VibrationEffect.createPredefined(VibrationEffect.EFFECT_CLICK))
        } else {
            vibrator.vibrate(VibrationEffect.createOneShot(20L, VibrationEffect.DEFAULT_AMPLITUDE))
        }
    }
}
```

Obtain the `Vibrator` through `VibratorManager` on API 31+. Actuator quality varies widely on Android; on devices without primitive support, prefer fewer, shorter effects over long one-shots.

## Rate limiter (any engine)

```csharp
public sealed class RateLimiter
{
    readonly double minIntervalSec; double last = double.NegativeInfinity;
    public RateLimiter(double perSecond) => minIntervalSec = 1.0 / perSecond;
    public bool TryFire(double now)
    {
        if (now - last < minIntervalSec) return false;
        last = now; return true;
    }
}
```

Wrap every haptic and every high-frequency SFX in a limiter; on cascades, also allow the largest step to bypass the limiter once.
