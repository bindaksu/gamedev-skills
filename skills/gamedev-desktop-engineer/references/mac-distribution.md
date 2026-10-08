# Mac Distribution: Signing, Notarization, Store Choice

Facts as of 2026-10. Sources: https://partner.steamgames.com/doc/store/application/platforms , https://developer.apple.com/videos/play/wwdc2019/703 , https://godotsteam.com/tutorials/mac_export/

## Steam vs Mac App Store

| Requirement | Steam (Developer ID) | Mac App Store |
| --- | --- | --- |
| Signing identity | Developer ID Application | Apple Distribution (App Store) |
| Notarization | Required (Steam requires notarized 64-bit bundles since Oct 14, 2019) | Done by App Review |
| App Sandbox | **Must be off** (incompatible with Steam) | **Required** |
| Hardened runtime | Required for notarization | Recommended |
| Entitlements | `cs.disable-library-validation`, `cs.allow-dyld-environment-variables` (Steam overlay and SDK) | Sandbox entitlements only for what you use (network client, game controllers, files) |
| Payments | Steam microtransactions | Apple IAP (StoreKit 2) |
| Achievements | Steamworks | Game Center |
| Updates | SteamPipe depots | App Store Connect |

Conclusion: two build targets, two entitlement files, two platform-service implementations behind one interface.

## Entitlements for the Steam build

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.cs.disable-library-validation</key><true/>
    <key>com.apple.security.cs.allow-dyld-environment-variables</key><true/>
    <!-- No com.apple.security.app-sandbox. No com.apple.security.get-task-allow in release. -->
</dict>
</plist>
```

Engines with JIT or scripting runtimes may also need `com.apple.security.cs.allow-jit` or `allow-unsigned-executable-memory`; add only when a crash proves it is needed.

## Sign, notarize, staple, verify

```bash
#!/usr/bin/env bash
set -euo pipefail
APP="build/mac/MyGame.app"
ID="Developer ID Application: Studio Name (TEAMID)"
ENT="mac/steam.entitlements"

# 1. Sign nested code deepest-first: dylibs, frameworks (incl. libsteam_api.dylib / Steam framework), helpers.
find "$APP/Contents" -type f \( -name "*.dylib" -o -name "*.so" \) -print0 |
  xargs -0 -I{} codesign --force --timestamp --options runtime --sign "$ID" "{}"
find "$APP/Contents/Frameworks" -maxdepth 1 -name "*.framework" -print0 |
  xargs -0 -I{} codesign --force --timestamp --options runtime --sign "$ID" "{}"

# 2. Sign the main bundle last, with entitlements.
codesign --force --timestamp --options runtime --entitlements "$ENT" --sign "$ID" "$APP"
codesign --verify --deep --strict --verbose=2 "$APP"

# 3. Notarize (zip for upload), staple, verify Gatekeeper.
ditto -c -k --keepParent "$APP" build/MyGame.zip
xcrun notarytool submit build/MyGame.zip --keychain-profile "notary" --wait
xcrun stapler staple "$APP"
spctl -a -vv "$APP"     # expect: accepted, source=Notarized Developer ID
```

Store the notary credentials once with `xcrun notarytool store-credentials "notary"`. On rejection, fetch the log with `xcrun notarytool log <submission-id> --keychain-profile "notary"`; the usual causes are an unsigned nested binary, a missing secure timestamp, or `get-task-allow` left in.

Tick "App Bundles Are Notarized" in the Steamworks partner settings for the Mac depot.

## Mac-specific runtime checklist

- [ ] Apple silicon native (arm64); universal only if Intel is a supported floor
- [ ] Game Mode keys set (`GCSupportsGameMode`, `LSSupportsGameMode` on macOS 26+, games category)
- [ ] Controllers via GameController framework or Steam Input; both tested
- [ ] Retina: render at backing pixel size; UI scaled by backing scale factor
- [ ] Notch-aware fullscreen on MacBook Pro/Air (safe area insets at the top)
- [ ] Cmd+Q, Cmd+H, Cmd+Tab behave; menu bar present in windowed mode
- [ ] Save path under `~/Library/Application Support/<bundle id>/` (Steam) or the sandbox container (MAS)
- [ ] EDR/HDR optional, off by default unless calibrated
- [ ] Profiled with Instruments Game Performance on the floor Mac (base M1 class)
