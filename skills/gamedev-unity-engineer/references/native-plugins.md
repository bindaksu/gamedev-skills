# Native Plugins: iOS and Android Bridges

One C# interface, three implementations (Editor stub, iOS, Android), one Platform assembly. Native code never calls Unity APIs off the main thread.

## C# side (shared)

```csharp
public interface IHaptics { void Play(HapticKind kind); }
public enum HapticKind { Light = 0, Medium = 1, Heavy = 2, Success = 3 }

public static class PlatformFactory
{
    public static IHaptics CreateHaptics()
    {
#if UNITY_IOS && !UNITY_EDITOR
        return new IosHaptics();
#elif UNITY_ANDROID && !UNITY_EDITOR
        return new AndroidHaptics();
#else
        return new EditorHapticsStub();
#endif
    }
}

public sealed class EditorHapticsStub : IHaptics
{
    public void Play(HapticKind kind) => Debug.Log($"[Haptics] {kind}");
}
```

## iOS: Swift exposed through a C symbol

Place files under `Assets/Plugins/iOS/`. Unity's Xcode project compiles `.swift`, `.m` and `.mm` there.

```swift
// Assets/Plugins/iOS/Haptics.swift
import UIKit

@_cdecl("game_haptics_play")
public func game_haptics_play(_ kind: Int32) {
    DispatchQueue.main.async {
        switch kind {
        case 0: UIImpactFeedbackGenerator(style: .light).impactOccurred()
        case 1: UIImpactFeedbackGenerator(style: .medium).impactOccurred()
        case 2: UIImpactFeedbackGenerator(style: .heavy).impactOccurred()
        default: UINotificationFeedbackGenerator().notificationOccurred(.success)
        }
    }
}
```

`@_cdecl` is an underscored (unofficial but widely used) attribute. The fully supported alternative is an Objective-C `.mm` shim with `extern "C"` that calls an `@objc` Swift class:

```objc
// Assets/Plugins/iOS/HapticsBridge.mm
#import <UnityFramework/UnityFramework-Swift.h>   // generated header name depends on target; verify in your Xcode project
extern "C" void game_haptics_play_objc(int kind) {
    [HapticsBridge playWithKind:kind];
}
```

```csharp
public sealed class IosHaptics : IHaptics
{
    [DllImport("__Internal")] private static extern void game_haptics_play(int kind);
    public void Play(HapticKind kind) => game_haptics_play((int)kind);
}
```

### Callbacks from iOS into C#

```csharp
public sealed class IosStoreReview
{
    private delegate void ResultCallback(int code);
    [DllImport("__Internal")] private static extern void game_request_review(ResultCallback cb);

    private static Action<int> pending;

    public void Request(Action<int> onDone)
    {
        pending = onDone;
        game_request_review(OnResult);
    }

    [AOT.MonoPInvokeCallback(typeof(ResultCallback))]
    private static void OnResult(int code) => MainThreadDispatcher.Enqueue(() => pending?.Invoke(code));
}
```

IL2CPP requires the callback to be a static method marked `MonoPInvokeCallback`. Native may call it on any thread, so enqueue to a dispatcher drained in `Update`. `UnitySendMessage("GameObjectName", "Method", "payload")` works too but is string-based, slower, and fails silently if the object is renamed.

### Xcode post-processing

```csharp
#if UNITY_IOS
public static class IosPostBuild
{
    [PostProcessBuild(100)]
    public static void OnPostprocessBuild(BuildTarget target, string path)
    {
        if (target != BuildTarget.iOS) return;
        var projPath = PBXProject.GetPBXProjectPath(path);
        var proj = new PBXProject();
        proj.ReadFromFile(projPath);
        string fw = proj.GetUnityFrameworkTargetGuid();
        proj.AddFrameworkToProject(fw, "CoreHaptics.framework", weak: true);
        proj.SetBuildProperty(fw, "SWIFT_VERSION", "5.0");
        proj.WriteToFile(projPath);

        var plistPath = Path.Combine(path, "Info.plist");
        var plist = new PlistDocument();
        plist.ReadFromFile(plistPath);
        plist.root.SetBoolean("CADisableMinimumFrameDurationOnPhone", true); // allow 120 Hz on ProMotion iPhones
        plist.WriteToFile(plistPath);
    }
}
#endif
```

Game Mode eligibility keys `GCSupportsGameMode` (iOS 18+) and `LSSupportsGameMode` (iOS 26+) can be set the same way (as of 2026-10; verify).

## Android: Kotlin class called through AndroidJavaObject

```kotlin
// Assets/Plugins/Android/haptics/src/main/java/com/studio/game/Haptics.kt  (or ship as an .aar)
package com.studio.game

import android.app.Activity
import android.os.Build
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager

class Haptics(private val activity: Activity) {
    private val vibrator: Vibrator =
        if (Build.VERSION.SDK_INT >= 31)
            (activity.getSystemService(VibratorManager::class.java)).defaultVibrator
        else
            @Suppress("DEPRECATION") activity.getSystemService(Vibrator::class.java)

    fun play(kind: Int) {
        val effect = when (kind) {
            0 -> VibrationEffect.EFFECT_TICK
            1 -> VibrationEffect.EFFECT_CLICK
            2 -> VibrationEffect.EFFECT_HEAVY_CLICK
            else -> VibrationEffect.EFFECT_DOUBLE_CLICK
        }
        vibrator.vibrate(VibrationEffect.createPredefined(effect))   // API 29+
    }
}
```

```csharp
public sealed class AndroidHaptics : IHaptics, IDisposable
{
    private readonly AndroidJavaObject impl;

    public AndroidHaptics()
    {
        using var player = new AndroidJavaClass("com.unity3d.player.UnityPlayer");
        var activity = player.GetStatic<AndroidJavaObject>("currentActivity");
        impl = new AndroidJavaObject("com.studio.game.Haptics", activity);
    }

    public void Play(HapticKind kind) => impl.Call("play", (int)kind);
    public void Dispose() => impl?.Dispose();
}
```

Cache the `AndroidJavaObject`; each `new AndroidJavaClass` is a JNI lookup. `using` disposes local references; leaking them across thousands of calls exhausts the JNI local reference table. Verify the activity accessor against your Unity version's activity class (GameActivity-based players differ from the legacy UnityPlayerActivity).

### Callbacks from Android into C#

```csharp
public sealed class BillingListener : AndroidJavaProxy
{
    private readonly Action<string> onPurchase;
    public BillingListener(Action<string> onPurchase)
        : base("com.studio.game.PurchaseListener") { this.onPurchase = onPurchase; }

    // Called on a Java thread: marshal before touching Unity APIs.
    public void onPurchaseUpdated(string json) => MainThreadDispatcher.Enqueue(() => onPurchase(json));
}
```

```kotlin
interface PurchaseListener { fun onPurchaseUpdated(json: String) }
```

### Native C/C++ on Android (JNI or plain P/Invoke)

```cpp
// game_native.cpp — built with the NDK into libgame_native.so
extern "C" __attribute__((visibility("default")))
int game_checksum(const unsigned char* data, int len) {
    unsigned int h = 2166136261u;                  // FNV-1a
    for (int i = 0; i < len; ++i) { h ^= data[i]; h *= 16777619u; }
    return static_cast<int>(h);
}
```

```csharp
[DllImport("game_native")] private static extern int game_checksum(byte[] data, int len);
```

### 16 KB page size (as of 2026-10; verify)

- Apps targeting Android 15+ must support 16 KB pages on 64-bit devices; Play blocks updates without support from Feb 1, 2027.
- NDK r28+ and AGP 8.5.1+ align by default. For NDK r27 and older add `-Wl,-z,max-page-size=16384`.
- Every prebuilt `.so` must be rebuilt — ad SDKs, physics, audio middleware included.
- Verify: `zipalign -v -c -P 16 4 app.apk`; `llvm-objdump -p libX.so | grep LOAD` expects `2**14`; on device `adb shell getconf PAGE_SIZE`.

## Main-thread dispatcher

```csharp
public sealed class MainThreadDispatcher : MonoBehaviour
{
    private static readonly ConcurrentQueue<Action> Queue = new();
    public static void Enqueue(Action a) => Queue.Enqueue(a);

    private void Update()
    {
        while (Queue.TryDequeue(out var a)) a();
    }

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
    private static void Reset() { while (Queue.TryDequeue(out _)) { } }
}
```

## Plugin review checklist

- [ ] C# interface + editor stub; game code never references the platform class directly
- [ ] Every native → C# path marshals to main thread
- [ ] No Unity API calls in native callbacks
- [ ] iOS: `MonoPInvokeCallback` on all static callbacks; weak-link frameworks newer than the deployment target
- [ ] Android: `AndroidJavaObject` cached and disposed; local references released
- [ ] `.so` 16 KB aligned for arm64-v8a; armeabi-v7a only if you still ship 32-bit
- [ ] Binary size and method count delta recorded
