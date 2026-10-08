# Native (C++/NDK) Snippets

AGDK and NDK APIs as of 2026-10. Function names for the Game Controller library and Memory Advice (beta) should be checked against the current AGDK headers ("verify").

## 1. GameActivity main loop

```cpp
#include <game-activity/native_app_glue/android_native_app_glue.h>

struct Engine { bool hasWindow = false; bool focused = false; /* renderer, sim, input */ };

static void onCmd(android_app* app, int32_t cmd) {
    auto* e = static_cast<Engine*>(app->userData);
    switch (cmd) {
        case APP_CMD_INIT_WINDOW: e->hasWindow = true;  /* create swapchain on app->window */ break;
        case APP_CMD_TERM_WINDOW: e->hasWindow = false; /* destroy swapchain, keep device */ break;
        case APP_CMD_GAINED_FOCUS: e->focused = true;  break;
        case APP_CMD_LOST_FOCUS:  e->focused = false; /* pause sim, mute audio */ break;
        case APP_CMD_SAVE_STATE:  /* write save to disk now; process may die */ break;
        case APP_CMD_LOW_MEMORY:  /* shed caches */ break;
        default: break;
    }
}

void android_main(android_app* app) {        // runs on its own thread, not the UI thread
    Engine engine;
    app->userData = &engine;
    app->onAppCmd = onCmd;

    while (!app->destroyRequested) {
        android_poll_source* source = nullptr;
        // Block when paused (timeout -1); spin when rendering (timeout 0).
        int timeout = (engine.hasWindow && engine.focused) ? 0 : -1;
        if (ALooper_pollOnce(timeout, nullptr, nullptr, reinterpret_cast<void**>(&source)) >= 0
            && source) {
            source->process(app, source);
        }

        if (auto* input = android_app_swap_input_buffers(app)) {
            // input->motionEvents[0..motionEventsCount), input->keyEvents[...]
            android_app_clear_motion_events(input);
            android_app_clear_key_events(input);
        }

        if (engine.hasWindow && engine.focused) {
            // fixed-step sim + render + present via Swappy
        }
    }
}
```

`ALooper_pollAll` is deprecated in recent NDKs; use `ALooper_pollOnce` in a loop.

## 2. Swappy frame pacing (Vulkan)

```cpp
#include "swappy/swappyVk.h"

void initPacing(JNIEnv* env, jobject activity, VkPhysicalDevice phys, VkDevice dev,
                VkSwapchainKHR swapchain, uint32_t queueFamily, VkQueue queue) {
    SwappyVk_setQueueFamilyIndex(dev, queue, queueFamily);
    uint64_t refreshNs = 0;
    SwappyVk_initAndGetRefreshCycleDuration(env, activity, phys, dev, swapchain, &refreshNs);
    SwappyVk_setSwapIntervalNS(dev, swapchain, SWAPPY_SWAP_60FPS);   // or SWAPPY_SWAP_30FPS per tier
    SwappyVk_setAutoSwapInterval(true);    // let Swappy drop to 30 when 60 is unsustainable
}

VkResult present(VkQueue queue, const VkPresentInfoKHR* info) {
    return SwappyVk_queuePresent(queue, info);      // replaces vkQueuePresentKHR
}
// On swapchain destroy: SwappyVk_destroySwapchain(dev, swapchain);
```

GL variant: `SwappyGL_init(env, activity)`, `SwappyGL_setSwapIntervalNS(SWAPPY_SWAP_60FPS)`, and `SwappyGL_swap(display, surface)` in place of `eglSwapBuffers`.

## 3. ADPF from native (no JNI)

```cpp
#include <android/thermal.h>          // API 30+ (headroom: API 31 NDK)
#include <android/performance_hint.h> // API 33 NDK

struct Adpf {
    AThermalManager* thermal = nullptr;
    APerformanceHintSession* hint = nullptr;

    void init(const int32_t* tids, size_t count, int64_t targetNs) {
        thermal = AThermal_acquireManager();
        if (auto* mgr = APerformanceHint_getManager())
            hint = APerformanceHint_createSession(mgr, tids, count, targetNs);
    }
    // Call about once per second at most.
    float headroom() const { return thermal ? AThermal_getThermalHeadroom(thermal, 10) : 0.f; }
    // Every frame: CPU work time for game+render threads, excluding vsync wait.
    void report(int64_t actualNs) { if (hint) APerformanceHint_reportActualWorkDuration(hint, actualNs); }
    void retarget(int64_t ns)     { if (hint) APerformanceHint_updateTargetWorkDuration(hint, ns); }
    ~Adpf() {
        if (hint) APerformanceHint_closeSession(hint);
        if (thermal) AThermal_releaseManager(thermal);
    }
};
```

Guard by `android_get_device_api_level()`; on API 30 to 32 use the Java APIs through one JNI call or skip hints.

## 4. Game Controller library (formerly Paddleboat) (verify names)

```cpp
#include "paddleboat/paddleboat.h"

void controllersInit(JNIEnv* env, jobject context) { Paddleboat_init(env, context); }

// In the input pass, give GameActivity events to the library first.
bool routeKey(const GameActivityKeyEvent* e) {
    return Paddleboat_processGameActivityKeyInputEvent(e, sizeof(GameActivityKeyEvent)) != 0;
}
bool routeMotion(const GameActivityMotionEvent* e) {
    return Paddleboat_processGameActivityMotionInputEvent(e, sizeof(GameActivityMotionEvent)) != 0;
}

void controllersPoll(JNIEnv* env, PlayerInput& out) {
    Paddleboat_update(env);                                   // once per frame
    for (int32_t i = 0; i < PADDLEBOAT_MAX_CONTROLLERS; ++i) {
        if (Paddleboat_getControllerStatus(i) != PADDLEBOAT_CONTROLLER_ACTIVE) continue;
        Paddleboat_Controller_Data d;
        if (Paddleboat_getControllerData(i, &d) == PADDLEBOAT_NO_ERROR) {
            out.moveX = d.leftStick.stickX;
            out.jump  = (d.buttonsDown & PADDLEBOAT_BUTTON_A) != 0;
        }
    }
}
// On shutdown: Paddleboat_destroy(env);
```

## 5. Memory Advice API (beta) (verify names)

```cpp
#include "memory_advice/memory_advice.h"

static void onMemoryState(MemoryAdvice_MemoryState state, void* user) {
    auto* cache = static_cast<AssetCache*>(user);
    if (state == MEMORYADVICE_STATE_APPROACHING_LIMIT) cache->trimTo(0.5f);
    if (state == MEMORYADVICE_STATE_CRITICAL)         cache->trimTo(0.0f);   // drop everything droppable
}

void memoryInit(JNIEnv* env, jobject context, AssetCache* cache) {
    MemoryAdvice_init(env, context);
    MemoryAdvice_registerWatcher(/* intervalMillis = */ 1000, onMemoryState, cache);
}
```

Beta status means the device model it uses may lag new hardware; keep `onTrimMemory`/`APP_CMD_LOW_MEMORY` handling as a backstop.

## 6. 16 KB page size: build and verify

```cmake
# NDK r28+ and AGP 8.5.1+ align to 16 KB by default.
# NDK r27 and older: add explicitly to every native target you build.
target_link_options(game PRIVATE "-Wl,-z,max-page-size=16384")
```

```bash
# Every .so, including prebuilt ads/physics/audio middleware: expect 2**14 on LOAD segments
for so in $(unzip -Z1 app-release.apk 'lib/arm64-v8a/*.so'); do
  unzip -p app-release.apk "$so" > /tmp/check.so
  echo "$so"; llvm-objdump -p /tmp/check.so | grep LOAD
done
zipalign -v -c -P 16 4 app-release.apk          # zip alignment of uncompressed libs
adb shell getconf PAGE_SIZE                      # 16384 on a 16 KB device/emulator image
```

Code assumptions to grep for: hard-coded `4096`, `PAGE_SIZE` macros, `mmap` offsets aligned to 4 KB. Use `sysconf(_SC_PAGESIZE)` at runtime.

## 7. Perfetto quick capture

```bash
adb shell perfetto -o /data/misc/perfetto-traces/game.pftrace -t 20s \
  sched freq idle am wm gfx view binder_driver hal dalvik input
adb pull /data/misc/perfetto-traces/game.pftrace
# open in ui.perfetto.dev; look at the render thread, SurfaceFlinger, and GPU completion
```

Add `ATrace_beginSection("sim")` / `ATrace_endSection()` (from `android/trace.h`) around sim, render, and present so engine phases appear in the trace.
