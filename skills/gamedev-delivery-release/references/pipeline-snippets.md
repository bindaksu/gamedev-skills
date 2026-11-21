# Pipeline Snippets

Read when building or fixing a game build pipeline. Action versions, plugin versions and inputs change; verify against current docs before use (as of 2026-10; verify).

## GitHub Actions with GameCI (Unity)

```yaml
name: release-android
on:
  push:
    branches: [ "release/*" ]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { lfs: true }
      - uses: actions/cache@v4
        with:
          path: Library
          key: Library-Android-${{ hashFiles('Packages/packages-lock.json') }}
      - uses: game-ci/unity-test-runner@v4
        env:
          UNITY_LICENSE: ${{ secrets.UNITY_LICENSE }}
          UNITY_EMAIL: ${{ secrets.UNITY_EMAIL }}
          UNITY_PASSWORD: ${{ secrets.UNITY_PASSWORD }}
        with:
          testMode: editmode
      - uses: game-ci/unity-builder@v4
        env:
          UNITY_LICENSE: ${{ secrets.UNITY_LICENSE }}
          UNITY_EMAIL: ${{ secrets.UNITY_EMAIL }}
          UNITY_PASSWORD: ${{ secrets.UNITY_PASSWORD }}
        with:
          targetPlatform: Android
          androidExportType: androidAppBundle
          versioning: Custom
          version: ${{ vars.MARKETING_VERSION }}
          androidVersionCode: ${{ github.run_number }}
          androidKeystoreName: upload.keystore
          androidKeystoreBase64: ${{ secrets.ANDROID_KEYSTORE_BASE64 }}
          androidKeystorePass: ${{ secrets.ANDROID_KEYSTORE_PASS }}
          androidKeyaliasName: ${{ secrets.ANDROID_KEYALIAS_NAME }}
          androidKeyaliasPass: ${{ secrets.ANDROID_KEYALIAS_PASS }}
      - uses: actions/upload-artifact@v4
        with:
          name: aab
          path: build/Android/*.aab
```

For iOS, `targetPlatform: iOS` exports an Xcode project; build and sign it on a macOS runner with fastlane (below) or Xcode Cloud.

## Fastfile (iOS and Android lanes)

```ruby
default_platform(:ios)

platform :ios do
  lane :beta do
    api_key = app_store_connect_api_key(
      key_id: ENV["ASC_KEY_ID"],
      issuer_id: ENV["ASC_ISSUER_ID"],
      key_content: ENV["ASC_KEY_P8"]
    )
    setup_ci
    match(type: "appstore", readonly: true, api_key: api_key)
    increment_build_number(
      xcodeproj: "build/iOS/Unity-iPhone.xcodeproj",
      build_number: ENV["CI_BUILD_NUMBER"]
    )
    build_app(
      project: "build/iOS/Unity-iPhone.xcodeproj",
      scheme: "Unity-iPhone",
      export_method: "app-store"
    )
    upload_to_testflight(api_key: api_key, skip_waiting_for_build_processing: true)
  end
end

platform :android do
  lane :internal do
    upload_to_play_store(
      track: "internal",
      aab: Dir["../build/Android/*.aab"].first,
      json_key_data: ENV["PLAY_JSON_KEY"]
    )
  end

  lane :production_staged do |options|
    upload_to_play_store(
      track: "production",
      aab: Dir["../build/Android/*.aab"].first,
      rollout: options[:rollout] || "0.05",   # 5% staged rollout
      json_key_data: ENV["PLAY_JSON_KEY"]
    )
  end
end
```

## Gradle signing from environment (Kotlin DSL, native Android shell)

```kotlin
android {
    signingConfigs {
        create("release") {
            storeFile = file(System.getenv("UPLOAD_KEYSTORE_PATH") ?: "missing.jks")
            storePassword = System.getenv("UPLOAD_KEYSTORE_PASS")
            keyAlias = System.getenv("UPLOAD_KEY_ALIAS")
            keyPassword = System.getenv("UPLOAD_KEY_PASS")
        }
    }
    defaultConfig {
        versionCode = (System.getenv("CI_BUILD_NUMBER") ?: "1").toInt()
        versionName = System.getenv("MARKETING_VERSION") ?: "0.0.0"
    }
    buildTypes {
        getByName("release") {
            signingConfig = signingConfigs.getByName("release")
            isMinifyEnabled = true
        }
    }
}
```

## 16 KB page-size verification step (Android)

```bash
# Fail the release lane if any native library is not 16 KB aligned
bundletool build-apks --bundle=app.aab --output=app.apks --mode=universal
unzip -o app.apks -d apks
zipalign -v -c -P 16 4 apks/universal.apk
for so in $(unzip -l apks/universal.apk | awk '/\.so$/{print $4}'); do
  unzip -o -q apks/universal.apk "$so" -d so_check
  llvm-objdump -p "so_check/$so" | grep LOAD | grep -q '2\*\*14' || { echo "Not aligned: $so"; exit 1; }
done
```

Source for the checks: https://developer.android.com/guide/practices/page-sizes (enforcement for updates from Feb 1, 2027; as of 2026-10; verify).

## Post-archive gate (iOS and Mac, before upload)

```bash
#!/usr/bin/env bash
# Usage: REQUIRED_MODULES="GameKit" FORBIDDEN_MODULES="StoreKit GoogleMobileAds" \
#        post_archive_check.sh build/Game.xcarchive last-shipped/Info.plist
set -euo pipefail
ARCHIVE="$1"; LAST_INFO="$2"
fail() { echo "POST-ARCHIVE FAIL: $*"; exit 1; }
APP=$(find "$ARCHIVE/Products/Applications" -maxdepth 1 -name "*.app" | head -1)
[ -n "$APP" ] || fail "no .app in archive"
if [ -d "$APP/Contents" ]; then ROOT="$APP/Contents"; MAC=1; else ROOT="$APP"; MAC=0; fi
PLIST="$ROOT/Info.plist"
EXE=$(/usr/libexec/PlistBuddy -c 'Print :CFBundleExecutable' "$PLIST")
if [ "$MAC" = 1 ]; then BIN="$ROOT/MacOS/$EXE"; else BIN="$APP/$EXE"; fi

# 0. The gate log must name the full HEAD hash and a clean tree.
HEAD=$(git rev-parse HEAD)
LOG="gates/$HEAD.log"
[ -f "$LOG" ] || fail "no gate log for full HEAD $HEAD"
grep -qx "commit: $HEAD" "$LOG" || fail "gate log does not name full HEAD $HEAD"
grep -qx "tree: clean" "$LOG" || fail "gate ran on a dirty tree"

# 1. Required and forbidden modules per flavor, across every binary, embedded framework
#    and the entitlements. A no-purchase flavor links zero store code anywhere.
read -ra REQUIRED <<<"${REQUIRED_MODULES:-GameKit}"
read -ra FORBIDDEN <<<"${FORBIDDEN_MODULES:-}"
LINKED="$(
  otool -L "$BIN" 2>&1 || true
  if [ -d "$ROOT/Frameworks" ]; then
    ls "$ROOT/Frameworks"
    find "$ROOT/Frameworks" -type f -perm -u+x -exec otool -L {} \; 2>/dev/null || true
  fi
  codesign -d --entitlements - "$APP" 2>/dev/null || true
)"
for m in ${REQUIRED[@]+"${REQUIRED[@]}"}; do      # empty-array safe under set -u (bash 3.2)
  grep -q "$m" <<<"$LINKED" || fail "missing $m"
done
for m in ${FORBIDDEN[@]+"${FORBIDDEN[@]}"}; do
  if grep -q "$m" <<<"$LINKED"; then fail "forbidden $m found"; fi
done

# 2. Required plist keys: iOS 27 SDK builds need the UIScene life cycle;
#    Mac App Store packages need a top-level LSMinimumSystemVersion.
if [ "$MAC" = 0 ]; then
  /usr/libexec/PlistBuddy -c 'Print :UIApplicationSceneManifest' "$PLIST" >/dev/null 2>&1 || fail "no scene manifest"
else
  /usr/libexec/PlistBuddy -c 'Print :LSMinimumSystemVersion' "$PLIST" >/dev/null 2>&1 || fail "no top-level LSMinimumSystemVersion"
fi

# 3. Toolchain change needs a newest-OS device launch of this exact signed build.
for k in DTSDKName DTXcodeBuild; do
  now=$(/usr/libexec/PlistBuddy -c "Print :$k" "$PLIST")
  was=$(/usr/libexec/PlistBuddy -c "Print :$k" "$LAST_INFO")
  if [ "$now" != "$was" ] && [ "${NEWEST_OS_LAUNCH_OK:-0}" != "1" ]; then
    fail "$k changed ($was -> $now); launch this signed build on the newest OS first"
  fi
done

# 4. Packaging hygiene: no AppleDouble sidecars, every file world-readable.
[ -z "$(find "$APP" -name '._*' -print -quit)" ] || fail "AppleDouble ._ files present"
[ -z "$(find "$APP" ! -perm -o=r -print -quit)" ] || fail "files not world-readable"
echo "post-archive checks passed"
```

Set the module lists per flavor; entries can be framework names, SDK names or entitlement keys. Prove the script against a control before trusting it: a bundle seeded with a forbidden framework, a missing key and a `._` file must each fail. For Android, inspect the AAB's dex and `lib/` for the billing client and plugin `.so` files the same way. The device launch that sets `NEWEST_OS_LAUNCH_OK` must fail unless a content screen appears.

## Headless signing and export (Xcode)

```bash
# Xcode 27 CI images that compile .metal files need the separate Metal Toolchain component.
xcodebuild -downloadComponent metaltoolchain

# -allowProvisioningUpdates needs a signed-in account or these three key flags.
xcodebuild -exportArchive -archivePath build/Game.xcarchive -exportPath build/export \
  -exportOptionsPlist ExportOptions.plist -allowProvisioningUpdates \
  -authenticationKeyPath "$ASC_KEY_PATH" -authenticationKeyID "$ASC_KEY_ID" \
  -authenticationKeyIssuerID "$ASC_ISSUER_ID"
```

Flags checked against `xcodebuild -help` on Xcode 27.2 (as of 2026-11; verify). After upload, read the build's processing state from the App Store Connect API before marking the lane green.

## Crash symbols

```bash
# Unity IL2CPP Android: enable "Create symbols.zip" in build settings, then
firebase crashlytics:symbols:upload --app="$FIREBASE_ANDROID_APP_ID" build/Android/symbols.zip
# Apple dSYM upload is auto-configured by the Crashlytics Unity SDK; verify it ran in the build log
```

## Secret scan step

```bash
# Block commits/PRs that contain signing material
git ls-files | grep -E '\.(jks|keystore|p8|p12|mobileprovision)$' && { echo "Signing material in repo"; exit 1; } || true
```
