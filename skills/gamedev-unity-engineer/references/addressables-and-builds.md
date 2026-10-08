# Addressables Content Updates and Build Automation

API names below match Addressables 1.x/2.x (as of 2026-10; verify against the package version in your manifest).

## Addressables 2.x facts that bite

- The **remote catalog must be enabled in the shipped player**, or the player can never detect content updates. Enable "Build Remote Catalog" in Addressable Asset Settings before the first store build and point its load path at the CDN.
- **"Update a previous build"** (content update build) uses the archived content state file (`addressables_content_state.bin`) to produce delta bundles. Lose the file and the next build re-downloads everything for every player. Archive it per platform per release, next to the symbols.
- **`UpdateCatalogs` blocks other Addressables requests** while it runs. Run it on the boot/loading screen, not mid-gameplay.
- Hosting can be Unity CCD or any CDN. Version the remote path (`/content/{platform}/{appVersion}/`) so a broken content push can be reverted by flipping the catalog, not by purging caches.

## Boot-time update flow

```csharp
public sealed class ContentUpdater
{
    public async Task<bool> RunAsync(IProgress<float> progress, CancellationToken ct)
    {
        await Addressables.InitializeAsync().Task;

        var check = Addressables.CheckForCatalogUpdates(autoReleaseHandle: false);
        List<string> changed = await check.Task;
        Addressables.Release(check);

        if (changed != null && changed.Count > 0)
        {
            var update = Addressables.UpdateCatalogs(changed, autoReleaseHandle: false);
            await update.Task;
            Addressables.Release(update);
        }

        // Download only what the next session needs, not the whole catalog.
        var sizeHandle = Addressables.GetDownloadSizeAsync("preload");
        long bytes = await sizeHandle.Task;
        Addressables.Release(sizeHandle);
        if (bytes == 0) return true;

        // Ask for consent on cellular above a threshold (heuristic: 50 MB).
        var dl = Addressables.DownloadDependenciesAsync("preload", autoReleaseHandle: false);
        while (!dl.IsDone)
        {
            ct.ThrowIfCancellationRequested();
            progress.Report(dl.GetDownloadStatus().Percent);
            await Task.Yield();
        }
        bool ok = dl.Status == AsyncOperationStatus.Succeeded;
        Addressables.Release(dl);
        return ok;
    }
}
```

Failure policy: if the catalog check fails (offline, CDN down), continue with the cached catalog and bundled content. Never block boot on the network; block only the feature that needs new content.

## Load / release discipline

```csharp
public sealed class ScreenLoader : IDisposable
{
    private AsyncOperationHandle<GameObject> handle;
    private GameObject instance;

    public async Task<GameObject> OpenAsync(string key, Transform parent)
    {
        handle = Addressables.LoadAssetAsync<GameObject>(key);
        var prefab = await handle.Task;
        instance = UnityEngine.Object.Instantiate(prefab, parent);
        return instance;
    }

    public void Dispose()
    {
        if (instance != null) UnityEngine.Object.Destroy(instance);
        if (handle.IsValid()) Addressables.Release(handle);
    }
}
```

One owner per handle. A handle released twice throws; a handle never released keeps its bundle (and every dependency bundle) resident.

## Group sizing heuristics

| Rule | Why |
|---|---|
| Group by load-together set and update cadence | Bundles unload only when every asset in them is released |
| Target 1–10 MB per remote bundle (heuristic) | Thousands of tiny bundles cost per-bundle overhead and catalog size; huge bundles defeat partial download and delta updates |
| No asset referenced from two groups unless it is in a shared group | Duplicate dependencies load twice and double memory |
| Labels for download sets (`preload`, `event_x`) | `GetDownloadSizeAsync(label)` gives an honest consent prompt |
| Local groups marked as non-updatable | Changes to them must go through a binary update anyway |

Run the duplicate-dependency analysis and inspect the build layout report before each content release.

## Static build entry point

```csharp
// Assets/Editor/Build/BuildScript.cs  (Game.Editor assembly)
public static class BuildScript
{
    public static void Android() => Build(BuildTarget.Android, "Builds/Android/game.aab");
    public static void IOS()     => Build(BuildTarget.iOS,     "Builds/iOS");

    private static void Build(BuildTarget target, string output)
    {
        var args = CommandLine.Parse(Environment.GetCommandLineArgs());
        string buildNumber = args.GetValueOrDefault("-buildNumber", "0");
        var named = NamedBuildTarget.FromBuildTargetGroup(BuildPipeline.GetBuildTargetGroup(target));

        PlayerSettings.SetScriptingBackend(named, ScriptingImplementation.IL2CPP);
        PlayerSettings.SetManagedStrippingLevel(named, ManagedStrippingLevel.Medium);

        if (target == BuildTarget.Android)
        {
            PlayerSettings.Android.bundleVersionCode = int.Parse(buildNumber);
            PlayerSettings.Android.targetArchitectures = AndroidArchitecture.ARM64;
            EditorUserBuildSettings.buildAppBundle = true;
            EditorUserBuildSettings.androidCreateSymbols = AndroidCreateSymbols.Public;
            // Keystore values come from CI secrets via environment variables, never from the repo.
            PlayerSettings.Android.useCustomKeystore = true;
            PlayerSettings.Android.keystoreName = Environment.GetEnvironmentVariable("ANDROID_KEYSTORE_PATH");
            PlayerSettings.Android.keystorePass = Environment.GetEnvironmentVariable("ANDROID_KEYSTORE_PASS");
            PlayerSettings.Android.keyaliasName = Environment.GetEnvironmentVariable("ANDROID_KEY_ALIAS");
            PlayerSettings.Android.keyaliasPass = Environment.GetEnvironmentVariable("ANDROID_KEY_PASS");
        }
        else if (target == BuildTarget.iOS)
        {
            PlayerSettings.iOS.buildNumber = buildNumber;
        }

        // 1. Addressables content first, so the player embeds the right catalog.
        AddressableAssetSettings.BuildPlayerContent(out var contentResult);
        if (!string.IsNullOrEmpty(contentResult.Error))
            throw new BuildFailedException($"Addressables: {contentResult.Error}");

        // 2. Player.
        var options = new BuildPlayerOptions
        {
            scenes = EditorBuildSettings.scenes.Where(s => s.enabled).Select(s => s.path).ToArray(),
            locationPathName = output,
            target = target,
            options = BuildOptions.None,          // add Development | ConnectWithProfiler only for perf builds
        };
        BuildReport report = BuildPipeline.BuildPlayer(options);
        if (report.summary.result != BuildResult.Succeeded)
            throw new BuildFailedException($"Player build {report.summary.result}, errors: {report.summary.totalErrors}");

        Debug.Log($"Built {output} size={report.summary.totalSize / (1024 * 1024)} MB in {report.summary.totalTime}");
    }
}
```

Unity 6 also has Build Profiles; a profile can be passed to the build API instead of setting PlayerSettings in code (verify the exact API on your version). Either way the source of truth must be versioned in the repo.

## Content-only update build

```csharp
public static void AndroidContentUpdate()
{
    var settings = AddressableAssetSettingsDefaultObject.Settings;
    string statePath = ContentUpdateScript.GetContentStateDataPath(false);   // archived file restored by CI
    var result = ContentUpdateScript.BuildContentUpdate(settings, statePath);
    if (!string.IsNullOrEmpty(result.Error)) throw new BuildFailedException(result.Error);
}
```

## Command line

```bash
"$UNITY_PATH" -batchmode -nographics -quit \
  -projectPath "$PWD" \
  -buildTarget Android \
  -executeMethod BuildScript.Android \
  -buildNumber "$CI_BUILD_NUMBER" \
  -logFile -
```

`-logFile -` streams the log to stdout so CI captures it. Exit code is non-zero when the build method throws. Cache the `Library/` folder between CI runs keyed on Unity version + `Packages/packages-lock.json`; a cold import of a mid-size mobile project can take 20–60 minutes (heuristic).

## CI pipeline shape

```
on push main:
  1. restore Library cache
  2. EditMode tests (Game.Core, fast)            → fail fast
  3. Android release build (IL2CPP, Medium strip) → aab + symbols.zip
  4. iOS build → Xcode project → xcodebuild archive (macOS runner)
  5. PlayMode smoke test on device farm (boot, first level, store open)
  6. upload symbols (Crashlytics / Sentry), archive content state file
  7. publish internal track / TestFlight  → hand off to delivery-release process
```

Hosted options: GameCI (open-source Docker images and GitHub Actions), Unity Build Automation, or self-hosted Jenkins/TeamCity with licensed runners. Signing, store tracks, phased rollout and force-update policy belong to `gamedev-delivery-release`.
