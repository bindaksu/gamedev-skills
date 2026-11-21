# Expo Build, Release and Test Lanes for Games

Read this when writing config plugins, the signed build lane, purchase or audio code, an OTA update policy, or UI tests. API names were checked against expo-iap 6.5.1, expo-audio 58.0.12, expo-haptics 58.0.8, expo-updates 58.0.22, @expo/config-plugins 58.0.13 and @expo/env (npm registry, 2026-11-21); production games also ship on SDK 57 with expo-iap 4.x-5.x, whose APIs differ. Verify against the versions you pin.

## 1. Toolchain changes are release risks

```bash
# tools/check_toolchain.sh <new.ipa> <last-shipped.ipa>   exit 2 = launch on newest iOS first
set -euo pipefail
plist_of() { local d; d=$(mktemp -d); unzip -q "$1" 'Payload/*.app/Info.plist' -d "$d"; find "$d/Payload" -maxdepth 2 -name Info.plist -print -quit; }
key() { /usr/libexec/PlistBuddy -c "Print :$2" "$1" 2>/dev/null || echo "-"; }
NEW=$(plist_of "$1"); OLD=$(plist_of "$2"); changed=0
if [ "$(key "$NEW" UIApplicationSceneManifest)" = "-" ]; then echo "FAIL: no scene manifest"; exit 1; fi
for k in DTXcodeBuild DTSDKName; do
  if [ "$(key "$NEW" "$k")" != "$(key "$OLD" "$k")" ]; then
    echo "CHANGED $k: $(key "$OLD" "$k") -> $(key "$NEW" "$k")"; changed=1
  fi
done
if [ "$changed" = 1 ]; then echo "Launch this exact signed build on a device running the newest iOS."; exit 2; fi
echo "toolchain unchanged"
```

- Apps linked against the iOS 27 SDK crash at launch on iOS 27 unless they adopt the UIScene life cycle; React Native and Unity shells are included (seen across several apps, as of 2026-11; verify against Apple's release notes for your SDK). If your SDK's generated project lacks a scene delegate, add one with a config plugin and fail any signed build without a scene manifest.
- Older-OS devices and simulators run the same binary fine, so only a launch on the newest OS catches it.
- Compiling Expo modules from source can hit compiler crashes on a new Swift toolchain; prefer precompiled modules or pin Xcode until the SDK supports it.

## 2. Config plugins and entitlements

```js
// plugins/withoutEntitlements.js: remove entitlements a module adds on its own
// (push, Game Center, external purchase) from flavors that must not carry them.
const { withEntitlementsPlist } = require('expo/config-plugins');

module.exports = function withoutEntitlements(config, keys = []) {
  return withEntitlementsPlist(config, (cfg) => {
    for (const key of keys) delete cfg.modResults[key];
    return cfg;
  });
};

// app.config.ts: plugins: [..., ['./plugins/withoutEntitlements', ['aps-environment']]]
// Then prove it: run prebuild and inspect ios/<App>/<App>.entitlements, and after signing run
//   codesign -d --entitlements :- build/App.app
```

Modules add entitlements and plist keys on their own (push, Game Center, external purchase links). Every flavor declares the entitlements it must have and must not have, and the signed-archive check enforces both.

## 3. Release environment switches

Expo CLI loads `.env`, `.env.local` and mode-specific `.env*` files and inlines every `EXPO_PUBLIC_*` value at build time. An unset switch in the release lane is silently filled from a developer's `.env.local`.

```bash
# Release lane excerpt: no .env files, every switch set explicitly, then checked in the bundle
set -euo pipefail
export EXPO_NO_DOTENV=1
export EXPO_PUBLIC_API_URL="https://api.example.com"
export EXPO_PUBLIC_DEBUG_MENU=0
export EXPO_PUBLIC_EDITION=store
missing=""
for v in $(grep -rhoE "process\.env\.EXPO_PUBLIC_[A-Z0-9_]+" packages/app/src | sed 's/process\.env\.//' | sort -u); do
  printenv "$v" >/dev/null || missing="$missing $v"
done
if [ -n "$missing" ]; then echo "unset in release lane:$missing"; exit 1; fi
# after the build: forbidden strings in the Hermes bundle
hits=$(strings -a build/App.app/main.jsbundle | grep -cE "staging\.|localhost|dev-menu" || true)
if [ "$hits" -gt 0 ]; then echo "dev strings in release bundle"; exit 1; fi
```

## 4. Native patches must reach the archive

Source patches (pnpm patch, patch-package) do nothing when the module is linked precompiled. Production builds silently linked an unpatched Skia this way. Put a marker in the patched native code and require it in the signed app.

```bash
# The patch adds: static const char kPatchMarker[] __attribute__((used)) = "patch:skia-cache-cap";
count=$(find build/App.app -type f \( -perm -u+x -o -name '*.dylib' \) -exec strings -a {} \; | grep -c "patch:skia-cache-cap" || true)
if [ "$count" -eq 0 ]; then echo "patched Skia not linked"; exit 1; fi
```

Use `grep -c` or a here-string in gates: with `pipefail`, `grep -q` can exit early, kill the writer with SIGPIPE and fail a check that matched.

## 5. Purchases with expo-iap

```ts
import {
  finishTransaction,
  initConnection,
  purchaseErrorListener,
  purchaseUpdatedListener,
  type Purchase,
} from 'expo-iap';

type Verdict = 'granted' | 'retry';

// Start at launch, before any shop UI: purchases also arrive from Ask to Buy, other devices,
// interrupted sessions and restores, not only from the Buy button.
export async function startStore(
  verifyOnServer: (purchase: Purchase) => Promise<Verdict>,
  isConsumable: (productId: string) => boolean,
  reportError: (code: string) => void,
): Promise<() => void> {
  await initConnection();
  const updated = purchaseUpdatedListener(async (purchase) => {
    const verdict = await verifyOnServer(purchase);   // the server grants; the client never self-grants
    if (verdict === 'granted') {
      await finishTransaction({ purchase, isConsumable: isConsumable(purchase.productId) });
    }
    // 'retry': leave it unfinished; the store delivers it again at the next launch
  });
  const failed = purchaseErrorListener((error) => reportError(String(error.code)));
  return () => {
    updated.remove();
    failed.remove();
  };
}
```

- Finish only after the server grants. Server-side verification, refunds and token rules belong to the backend seat.
- Test the store as a guest or signed-out player and as a refunded player. A disabled Buy or Restore button must say why when tapped; a silent no-op for guests went unnoticed across releases in one game.
- Premium unlocks without a server: re-check entitlements each time the app returns to the foreground and re-lock only when the store marks the purchase revoked; keep progress so buying again restores everything.
- An Apple Arcade or no-purchase flavor must not link the purchase module at all: exclude it from autolinking for that flavor and prove absence with the archive check (no StoreKit-backed purchase module, no ad SDKs).
- StoreKit configuration tests are sensitive to the simulator runtime; pin the runtime the tests run on.

## 6. Audio and haptics

```ts
import { createAudioPlayer, setAudioModeAsync, type AudioPlayer, type AudioSource } from 'expo-audio';
import { ImpactFeedbackStyle, impactAsync } from 'expo-haptics';

export async function initAudio(): Promise<void> {
  // Casual default: respect the silent switch and mix with the player's music.
  await setAudioModeAsync({ playsInSilentMode: false, interruptionMode: 'mixWithOthers', shouldPlayInBackground: false });
}

// A few reusable voices per cue, created once at load: no player creation on the hot path.
export class SfxPool {
  private readonly players: AudioPlayer[];
  private next = 0;

  constructor(source: AudioSource, voices = 3) {
    this.players = Array.from({ length: voices }, () => createAudioPlayer(source));
  }

  play(): void {
    const player = this.players[this.next];
    this.next = (this.next + 1) % this.players.length;
    void player.seekTo(0);
    player.play();
  }

  dispose(): void {
    for (const player of this.players) player.remove();
  }
}

// Fire and forget: never await haptics or audio on a gesture or frame path.
export function tapFeedback(): void {
  void impactAsync(ImpactFeedbackStyle.Light);
}
```

- Use expo-audio for new work; production games no longer ship expo-av.
- Create players at load and reuse them; creating and releasing players per shot puts allocation and cleanup on the hot path.
- Preloading, shader warm-ups and OS game mode each won a median in device runs and then failed paired confirmation. Keep a perf change only after fresh paired runs confirm it.
- Sound must be proved by measurement on device (a recorded output check or an audio-session peak meter), not by "player.playing".

## 7. OTA updates versus store review

| Change | OTA | Needs a store build |
|---|---|---|
| JS bug fix, copy, balance data, art in the JS bundle | Yes, within the same runtime version | |
| New native module, permission, entitlement or SDK | | Yes |
| Purchase flow, prices shown, review-relevant features | | Yes, and update review notes |
| Sim rules change that alters replays, goldens or saves | Only with a rules revision stamped in saves and replays, and old revisions still loadable | Prefer a store build |
| Kill switch or feature flag flip | Remote config, not a bundle | |

```ts
// app.config.ts excerpt
export default {
  expo: {
    runtimeVersion: { policy: 'fingerprint' },   // native changes get a new runtime; old binaries never get new JS
    updates: { checkAutomatically: 'ON_LOAD', fallbackToCacheTimeout: 0 },
  },
};
```

```ts
import * as Updates from 'expo-updates';

// Report every launch that fell back to the embedded bundle after a failed update.
export function reportUpdateHealth(track: (event: string, props: Record<string, string>) => void): void {
  if (Updates.isEmergencyLaunch) {
    track('ota_emergency_launch', { reason: Updates.emergencyLaunchReason ?? 'unknown' });
  }
  track('ota_launch', {
    channel: Updates.channel ?? 'none',
    runtime: Updates.runtimeVersion ?? 'none',
    embedded: String(Updates.isEmbeddedLaunch),
  });
}
```

- One channel per build flavor; an evaluation or Arcade build never reads the store channel.
- Apple allows downloaded interpreted code only if it does not change the app's primary purpose or bypass review (App Review guidelines 2.5.2 and 4.7; verify current wording at https://developer.apple.com/app-store/review/guidelines/).
- Roll an update to a small share first and watch emergency launches; roll back by republishing the previous update.

## 8. Tests

- **Sim suites (Vitest or Jest):** the pure core runs in Node; keep the parity corpus and golden saves there, run with one worker and timeouts that catch hangs (for example 60 s), not host load. Move slow proofs to an opt-in lane unchanged.
- **Component tests:** Jest with the Expo preset for screens and hooks.
- **Maestro:** fast flows for menus, shop and onboarding. Maestro reports an element below the fold but inside the screen bounds as visible, so scroll before asserting. It has no multi-pointer command.

```yaml
appId: com.example.game
---
- launchApp:
    clearState: true
- tapOn:
    id: "play-button"
- scrollUntilVisible:
    element:
      id: "shop-row-starter"
    direction: DOWN
- assertVisible:
    id: "shop-row-starter"
```

- **XCUITest for gestures:** pinch and multi-finger checks, each with one control that must pass and one that must fail.

```swift
func testPinchZoomsMapButNotHud() {
    let app = XCUIApplication()
    app.launch()
    let map = app.otherElements["map-canvas"]
    let zoomBefore = app.staticTexts["debug-zoom"].label
    map.pinch(withScale: 2.0, velocity: 1.0)
    XCTAssertNotEqual(app.staticTexts["debug-zoom"].label, zoomBefore)        // should change
    let hud = app.otherElements["hud-bar"]
    let hudZoom = app.staticTexts["debug-zoom"].label
    hud.pinch(withScale: 2.0, velocity: 1.0)
    XCTAssertEqual(app.staticTexts["debug-zoom"].label, hudZoom)              // control: must not
}
```

- Detox is the alternative gray-box runner when the team wants JS-side synchronization; check its support for your React Native version first.
- Before every submission run the full suite, sum the totals of every test bundle, and count tests lost to runner restarts as failures.

## 9. Perf evidence on device

- Write the keep/revert rule before measuring, then confirm a winning median with fresh paired runs.
- Re-measure the last shipped build on the same phone the same day as the candidate.
- On a 60 Hz screen, frame-time p95 can only read 16.7 or 33.4 ms; judge presented frames, not callback timestamps.
- Sample power source, Low Power Mode and thermal state during runs; simulator numbers are directional only.
