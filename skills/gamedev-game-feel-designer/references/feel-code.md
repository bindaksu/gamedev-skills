# Feel Implementation Snippets

Read when implementing hit-stop, trauma shake, a tuning panel, or platform haptics. Snippets are minimal and engine-idiomatic; verify API availability against your engine and OS versions before shipping.

## Hit-stop with a single time-scale owner (Unity, C#)

Freeze gameplay time, keep UI, audio and input alive. **One component is the only writer of `Time.timeScale`**, and it recomputes the scale every frame from live state: 0 if paused, 0 during hit-stop, otherwise the pace scale.

Do not use the save-and-restore pattern (`previous = Time.timeScale; Time.timeScale = 0; ... Time.timeScale = previous;`). It breaks as soon as a second system touches the scale: a pause opened 20 ms into a 60 ms freeze is overwritten when the freeze writes 1 back, so the game runs behind the open menu; a resume that writes 1 inserts a full-speed frame into a freeze.

```csharp
using UnityEngine;

// The only writer of Time.timeScale. Nothing else saves, sets or restores it.
[DefaultExecutionOrder(10000)]                    // LateUpdate runs after every other script's
public sealed class TimeScaleOwner : MonoBehaviour
{
    [SerializeField] float maxStackMs = 300f;     // cap so chained hits never freeze for seconds
    float hitStopLeft;                            // seconds of freeze still owed
    bool frameHeldByHitStop;                      // the frame now running was frozen by hit-stop, not by pause

    public bool Paused { get; set; }              // the pause menu flips this and nothing else
    public float PaceScale { get; set; } = 1f;    // slow-mo, fast-forward, assist speed

    public void RequestHitStop(float ms) =>
        hitStopLeft = Mathf.Min(hitStopLeft + ms / 1000f, maxStackMs / 1000f);

    // Decide the scale for the next frame after gameplay and animation have run.
    void LateUpdate()
    {
        if (frameHeldByHitStop)                   // spend only frames that really ran frozen by the hit
            hitStopLeft = Mathf.Max(0f, hitStopLeft - Time.unscaledDeltaTime);
        bool freezeNext = hitStopLeft > 0f;
        Time.timeScale = (Paused || freezeNext) ? 0f : PaceScale;   // recomputed, never restored
        frameHeldByHitStop = freezeNext && !Paused;
    }
}
```

In a frame-loop model (not a device run) at 20, 30 and 60 fps with 40, 60 and 150 ms requests: every request freezes at least one whole frame, the frozen total is within one frame of the request, a pause inside a freeze holds the remainder until the menu closes, and no frame between freeze start and end runs at the pace scale.

Rules that go with it:
- Pause, resume, slow-mo and hit-stop only change inputs to the owner (`Paused`, `PaceScale`, `RequestHitStop`). A resume inside a freeze keeps the scale at 0 until the freeze ends; a pause inside a freeze holds the remainder until the menu closes.
- **Never advance animation clocks on a frame whose gameplay update is skipped.** Gameplay code that skips work while frozen gates on the scale that frame actually runs at (for example `Time.deltaTime == 0f`), not on the menu's live pause flag; otherwise the frame that opens the pause can advance animation while logic stands still [inference: confirm how your Unity version applies a mid-frame time-scale change].
- Test a pause and a resume that each land inside a freeze, at 20 fps (`Application.targetFrameRate = 20`): the scale stays 0 under the menu, and no frame between freeze start and end runs at the pace scale.
- UI animations use unscaled time; Animators that must keep moving use `AnimatorUpdateMode.UnscaledTime`. Input buffering keeps reading during the freeze because input is not time-scaled.

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
