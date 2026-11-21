# Export, Native Code and Release Gates for Godot

Read this when setting up export presets, adding a native plugin or GDExtension, wiring GodotSteam, packaging for the Mac App Store, or writing the release gate. Version facts are as of 2026-11; verify against https://github.com/godotengine/godot/releases , https://godotsteam.com and the add-on's own release page.

## 1. What an export actually contains

| Trap | What happens | Rule |
|---|---|---|
| Exports keep only imported resources | A PNG, WAV or OGG ships as its imported form plus an `.import` remap; the source file is not in the pack | Load assets with `load()` / `ResourceLoader` only |
| `FileAccess` ignores import remaps | `FileAccess.open("res://art/hero.png")` and `Image.load()` work in the editor and fail in the export | Never open imported assets with `FileAccess`; it is for your own data files |
| `DirAccess` lists remap files | In an export a folder shows `hero.png.import` or `.remap` entries | `ResourceLoader.list_directory()` (present in 4.7.2) |
| Non-resource files are skipped | JSON, TXT or YAML data is missing unless matched by the preset's non-resource filter | Add `*.json, *.txt` to the filter; the selftest reads one |
| CSV is imported as a translation by default | A data CSV becomes a translation resource and the raw table is gone | Set that file's Import As to "Keep File (exported as is)" |
| Preset feature tags | `OS.has_feature("steam")` is false unless the preset adds the tag | One preset per store; tags name the store and edition |
| Headless renderer and audio | Draw calls read 0; audio mixes into the Dummy driver, so bus peaks are real but device output is untested | Render gates run windowed; the audio probe runs headless in CI and once per platform on hardware |

The first four rows were checked inside a pack exported with `--export-pack` on 4.7.2: `FileAccess.file_exists("res://art/hero.png")` was false, `ResourceLoader.exists()` true, `DirAccess` listed `hero.png.import`, `ResourceLoader.list_directory()` listed `hero.png`, and a `.txt` manifest was present only when the preset's filter named it.

Export smoke test, run in CI for every preset (this flow was run end to end on 4.7.2):

```gdscript
# tests/export_selftest.gd: runs inside the exported pack, not the editor.
# godot --headless --export-pack "macOS" build/selftest.pck
# godot --headless --main-pack build/selftest.pck --script res://tests/export_selftest.gd
extends SceneTree

const MANIFEST := "res://data/required_assets.txt"   # one res:// path per line, exported via filter

func _init() -> void:
	var missing: PackedStringArray = []
	var f := FileAccess.open(MANIFEST, FileAccess.READ)    # plain text file, listed in export filters
	if f == null:
		printerr("manifest not exported: add *.txt to the non-resource export filter")
		quit(2)
		return
	while not f.eof_reached():
		var path := f.get_line().strip_edges()
		if path.is_empty():
			continue
		# ResourceLoader follows .import/.remap files; FileAccess does not.
		if not ResourceLoader.exists(path) or load(path) == null:
			missing.append(path)
	for p in missing:
		printerr("not loadable in export: ", p)
	quit(1 if missing.size() > 0 else 0)
```

Folder listing that works in exports:

```gdscript
extends Node

# Lists imported assets in a folder in the editor and in exports.
# DirAccess sees "hero.png.import" / ".remap" files in an export, not "hero.png".
func list_textures(dir: String) -> Array[Texture2D]:
	var out: Array[Texture2D] = []
	for file_name in ResourceLoader.list_directory(dir):
		if file_name.ends_with(".png") or file_name.ends_with(".webp"):
			out.append(load(dir.path_join(file_name)) as Texture2D)
	return out
```

## 2. Engine pin and API probe

```text
TOOLCHAIN (commit this file)
engine:            4.7.2.stable.official.<hash>      export templates: same string
add-ons:           GUT <ver>, GodotSteam <ver> (Steamworks SDK <ver>), godot-cpp <ver>
native artifacts:  path, sha256, built-from commit, build command   (one line each)
mac floor:         macOS <ver>, universal          iOS floor: <ver>
xcode:             <ver> (record which Xcode built each archive)
```

```gdscript
# tools/api_probe.gd: run at every engine bump and milestone.
# godot --headless --path . --script res://tools/api_probe.gd
extends SceneTree

const EXPECTED_VERSION := "4.7.2-stable (official)"
const REQUIRED := {
	"DisplayServer": ["accessibility_should_reduce_animation", "accessibility_should_increase_contrast"],
	"Control": ["set_accessibility_name", "set_accessibility_description"],
	"ResourceLoader": ["list_directory"],
	"AudioServer": ["get_bus_peak_volume_left_db"],
}

func _init() -> void:
	var failures := 0
	var version: String = Engine.get_version_info().string
	if version != EXPECTED_VERSION:
		printerr("engine is %s, toolchain pins %s" % [version, EXPECTED_VERSION])
		failures += 1
	for cls: String in REQUIRED:
		for method: String in REQUIRED[cls]:
			if not ClassDB.class_has_method(cls, method):
				printerr("missing %s.%s" % [cls, method])
				failures += 1
	if Engine.has_singleton("Steam") == false and OS.has_feature("steam"):
		printerr("steam feature tag set but GodotSteam is not loaded")
		failures += 1
	quit(1 if failures > 0 else 0)
```

Run the probe after every engine bump and at each milestone. Pin exact versions of the engine build, export templates, GUT, GodotSteam with its Steamworks SDK, and godot-cpp together, and set the macOS deployment target of a universal GDExtension explicitly; check each upstream release page before pinning (as of 2026-11; verify).

## 3. iOS plugins versus macOS GDExtensions

Keep two separate native packages even when they wrap the same feature.

```ini
; res://addons/store_bridge/store_bridge.gdextension   (desktop: godot-cpp)
[configuration]
entry_symbol = "store_bridge_library_init"
compatibility_minimum = "4.5"
reloadable = false

[libraries]
macos.debug = "res://addons/store_bridge/bin/libstore_bridge.macos.template_debug.framework"
macos.release = "res://addons/store_bridge/bin/libstore_bridge.macos.template_release.framework"
```

```ini
; res://ios/plugins/store_bridge/StoreBridge.gdip     (iOS plugin: one framework per plugin)
[config]
name="StoreBridge"
binary="StoreBridge.xcframework"
initialization="store_bridge_init"
deinitialization="store_bridge_deinit"

[dependencies]
linked=[]
embedded=[]
system=["StoreKit.framework"]
capabilities=[]
files=[]
linker_flags=[]
```

Rules:
- Build each GDExtension library with the same target (`template_debug` or `template_release`), float precision and API level as the export template that loads it, and give every target a feature-tagged key. A missing `macos.release` key fails only in release exports.
- Keep preprocessor defines identical between the plugin build and the code that calls it; a define set only on one side compiles both halves of an `#if` into different shapes.
- One iOS plugin per framework. Never link the same library through both a plugin and a GDExtension.
- Build macOS libraries universal (arm64 + x86_64) unless the store listing is Apple-silicon-only, and set the deployment target to the floor you declared.
- The 4.7.2 editor binary still recognizes `.gdip` descriptors (checked); check GDExtension-on-iOS support and the plugin docs for your exact version before starting, because both have changed across 4.x.

## 4. Clean checkouts and silent fallbacks

Native binaries are usually untracked build products. A clean CI checkout exports without them, and the engine continues without the missing plugin, so the store or Steam feature quietly disappears from the build.

```bash
# tools/check_native_artifacts.sh: run before every export; fails on a missing or wrong binary
set -euo pipefail
status=0
while read -r path sha; do
  [ -z "$path" ] && continue
  if [ ! -e "$path" ]; then echo "MISSING $path"; status=1; continue; fi
  actual=$(find "$path" -type f -print0 | sort -z | xargs -0 shasum -a 256 | shasum -a 256 | cut -d' ' -f1)
  [ "$actual" = "$sha" ] || { echo "HASH MISMATCH $path"; status=1; }
done < native_artifacts.txt
exit $status
```

## 5. After every archive: required and forbidden code

```bash
# tools/check_archive.sh <App.app> <edition>   e.g. editions: store | nopurchase | steam
set -euo pipefail
APP="$1"; EDITION="$2"
PLIST="$APP/Info.plist"; [ -f "$PLIST" ] || PLIST="$APP/Contents/Info.plist"
EXE_NAME=$(/usr/libexec/PlistBuddy -c "Print :CFBundleExecutable" "$PLIST")
if [ -f "$APP/Contents/MacOS/$EXE_NAME" ]; then EXE="$APP/Contents/MacOS/$EXE_NAME"; else EXE="$APP/$EXE_NAME"; fi
linked=$(otool -L "$EXE")
classes=$(strings -a "$EXE")        # ObjC class names survive symbol stripping
# here-strings, not pipes: with pipefail, "echo | grep -q" can fail on SIGPIPE
need() { grep -q "$1" <<<"$2" || { echo "MISSING $1"; exit 1; }; }
forbid() { if grep -q "$1" <<<"$2"; then echo "FORBIDDEN $1"; exit 1; fi; }
case "$EDITION" in
  store)      need StoreKit.framework "$linked"; need StoreBridgePlugin "$classes" ;;
  nopurchase) forbid StoreKit.framework "$linked"; forbid StoreBridgePlugin "$classes" ;;
  steam)      need libsteam_api "$(find "$APP" -name 'libsteam_api*')" ;;
esac
/usr/libexec/PlistBuddy -c "Print :CFBundleShortVersionString" "$PLIST" >/dev/null
echo "archive check passed for $EDITION"
```

Baseline the lists on a known-good build first: engine templates link some system frameworks on their own. Run the script in the lane that uploads, so a failure blocks the upload.

## 6. GodotSteam

```gdscript
# Autoload for Steam builds only (feature tag "steam" on the Steam export presets).
extends Node

var steam_ok := false

func _ready() -> void:
	if not OS.has_feature("steam") or not Engine.has_singleton("Steam"):
		return
	var steam: Object = Engine.get_singleton("Steam")
	var result: Dictionary = steam.steamInitEx()      # check the signature for your GodotSteam release
	steam_ok = int(result.get("status", -1)) == 0
	if not steam_ok:
		push_warning("Steam init failed: %s" % result.get("verbal", "unknown"))

func _process(_delta: float) -> void:
	if steam_ok:
		Engine.get_singleton("Steam").run_callbacks()   # every frame, one thread

func unlock(achievement_api_name: String) -> void:
	if steam_ok:
		var steam: Object = Engine.get_singleton("Steam")
		steam.setAchievement(achievement_api_name)
		steam.storeStats()
```

- Only Steam presets carry the GodotSteam binaries and the `steam` feature tag; Mac App Store and mobile presets exclude them, and the archive check proves it.
- On macOS, sign the bundled Steam library inside the app before signing the app, use the two hardened-runtime entitlements Steam needs, and never enable App Sandbox for the Steam build. Hand notarization, Deck and Steam Input work to the desktop seat.
- Achievements and stats from automated test sessions must go to a separate Steam account or be disabled by a command-line flag.

## 7. Mac App Store packaging

```bash
# Runs on internal APFS only. On exFAT the signature seals AppleDouble "._" files,
# files become root-only, and App Store Connect rejects the package.
set -euo pipefail
APP="build/mas/Game.app"; PLIST="$APP/Contents/Info.plist"
if [ -n "$(find "$APP" -name '._*' -print -quit)" ]; then echo "AppleDouble files present"; exit 1; fi
# 1. Top-level minimum OS (an export may write only per-architecture keys)
/usr/libexec/PlistBuddy -c "Print :LSMinimumSystemVersion" "$PLIST" >/dev/null 2>&1 \
  || /usr/libexec/PlistBuddy -c "Add :LSMinimumSystemVersion string $MAC_FLOOR" "$PLIST"
# 2. Provisioning profile: Game Center and iCloud entitlements without it kill the app at launch
cp "$MAS_PROFILE" "$APP/Contents/embedded.provisionprofile"
# 3. World-readable files
chmod -R a+rX "$APP"
# 4. Sign nested code deepest-first, then the app with App Sandbox entitlements
find "$APP/Contents/Frameworks" -depth \( -name '*.dylib' -o -name '*.framework' \) \
  -exec codesign --force --sign "$APP_SIGN_ID" {} \;
codesign --force --sign "$APP_SIGN_ID" --entitlements mas.entitlements "$APP"
# 5. Package and re-check
productbuild --component "$APP" /Applications --sign "$INSTALLER_SIGN_ID" build/mas/Game.pkg
codesign --verify --deep --strict "$APP"
```

- `LSMinimumSystemVersion` must equal the package minimum.
- Add the macOS platform to the app record in App Store Connect before the first upload.
- Launch the exact signed build once before upload; an entitlement or profile mistake shows up as a crash at launch, not as a validation error.
- A mobile port's fallback development store bridge must fail closed in release builds.

## 8. Android export

- Use the Gradle build export for anything with native code, and produce an AAB for Play. Android plugins are packaged as AARs and added through an editor export plugin in Godot 4.x (check the plugin docs for your version); keep one preset per store edition as on iOS.
- Every native `.so` you ship (GDExtensions, plugin libraries) must be 16 KB page aligned for current Play requirements; check alignment on the built AAB, and hand Play policy, target API and Play Billing details to the Android seat.
- Run the archive idea on the AAB too: `unzip -l` the bundle and require or forbid each plugin's libraries and classes per edition.

## 9. iOS export checks

- The Godot iOS export produces an Xcode project. Record the Xcode and SDK that built each archive (`DTXcodeBuild`, `DTSDKName` in the IPA's Info.plist) and compare them with the last shipped build.
- When either changed, launch that exact signed build on a device running the newest iOS before upload. Builds linked against the iOS 27 SDK must adopt the UIScene life cycle or they crash at launch on iOS 27; confirm your export template's generated project has a scene manifest [inference: check per engine version].
- Run the archive check (section 5) on the IPA's app bundle, and the App Review pre-flight from the iOS seat.
