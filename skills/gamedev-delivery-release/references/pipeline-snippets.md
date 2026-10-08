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
