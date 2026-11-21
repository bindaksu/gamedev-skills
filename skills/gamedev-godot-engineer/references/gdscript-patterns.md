# GDScript Patterns for Shipping Godot Games

Every snippet here was parse-checked with `godot --check-only` on 4.7.2.stable, and the behaviour notes marked "checked on 4.7.2" were observed in headless runs of that build (as of 2026-11; verify on your pinned build, https://github.com/godotengine/godot/releases). Read the section you need; each is self-contained.

## 1. Signals bound to methods

```gdscript
extends Control

@onready var buy_button: Button = %BuyButton
var _sku := "starter_pack"

func _ready() -> void:
	# Method callables compare equal, can be disconnected, and are dropped when this node is freed.
	buy_button.pressed.connect(_on_buy_pressed.bind(_sku))
	# Not this: a lambda cannot be found again for disconnect() or is_connected(),
	# because each func(): ... is a new Callable that never equals the last one.
	# buy_button.pressed.connect(func(): _start_purchase(_sku))

func _exit_tree() -> void:
	if buy_button.pressed.is_connected(_on_buy_pressed):
		buy_button.pressed.disconnect(_on_buy_pressed)

func _on_buy_pressed(sku: String) -> void:
	_start_purchase(sku)

func _start_purchase(_sku_id: String) -> void:
	pass
```

Rules:
- Connect to methods; pass context with `.bind()`. Two lambdas with the same body never compare equal (checked on 4.7.2), so `disconnect()` and `is_connected()` cannot find a lambda connection.
- Both kinds of connection are dropped when the object that made them is freed (checked on 4.7.2). The lambda problem is screens that are hidden or pooled rather than freed: they keep receiving signals you can no longer disconnect, and a lambda that captured another node can outlive that node [inference].
- Use `CONNECT_ONE_SHOT` for one-time events instead of a self-disconnecting lambda.

## 2. Gamepad acceptance in menus

```gdscript
# Autoload. Godot 4.7.2's default ui_accept holds only Enter, keypad Enter and Space
# (checked headless), so a gamepad cannot press focused buttons until you add events.
extends Node

func _ready() -> void:
	_ensure_joy_button("ui_accept", JOY_BUTTON_A)
	_ensure_joy_button("ui_cancel", JOY_BUTTON_B)

func _ensure_joy_button(action: StringName, button: JoyButton) -> void:
	for ev in InputMap.action_get_events(action):
		if ev is InputEventJoypadButton and ev.button_index == button:
			return
	var joy := InputEventJoypadButton.new()
	joy.button_index = button
	joy.device = -1   # all devices
	InputMap.action_add_event(action, joy)
```

Map gameplay to your own actions (`move_left`, `confirm`), never to raw buttons. Decide the confirm button per platform family (Nintendo layouts swap A and B) and show glyphs for the last device used.

## 3. Glyph priming at the viewport oversampling

```gdscript
# GlyphPrimer: add under an opaque loading panel AFTER the window size and stretch settle.
# It draws every glyph once through the real text path, so the cache entries match the
# viewport's current oversampling. Priming at a nominal size (oversampling 1.0) misses.
class_name GlyphPrimer
extends Control

signal primed

@export var fonts: Array[Font] = []
@export var sizes: PackedInt32Array = [16, 22, 32, 48]
@export_multiline var charset := "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,:;!?%+-/()"

var _drawn_at_oversampling := -1.0

func _ready() -> void:
	get_viewport().size_changed.connect(_on_viewport_size_changed)
	queue_redraw()

func _on_viewport_size_changed() -> void:
	if not is_equal_approx(get_viewport().oversampling, _drawn_at_oversampling):
		queue_redraw()   # display scale or window moved to another screen: re-prime

func _draw() -> void:
	var y := 0.0
	for font in fonts:
		for size in sizes:
			y += size
			draw_string(font, Vector2(0, y), charset, HORIZONTAL_ALIGNMENT_LEFT, -1, size)
	_drawn_at_oversampling = get_viewport().oversampling
	primed.emit.call_deferred()
```

- Add the primer under an opaque loading panel for one frame after the window and stretch settings are final, then free it.
- `Viewport.oversampling` is read-only; `oversampling_override` is settable (checked on 4.7.2). If you force an override, prime after setting it.
- Prime every (font, size, outline) your UI uses, including the largest dynamic sizes and every language's character set. CJK sets are large: prime the screen's own strings, not the whole block.

## 4. Translation overrides over an OptimizedTranslation

```gdscript
# Overrides (hotfix strings, platform-specific copy) on top of an OptimizedTranslation.
# Checked on 4.7.2: OptimizedTranslation.add_message() silently does nothing and
# get_message_list() returns []. For one locale, the translation added FIRST wins,
# and a more specific locale (de_DE) beats its base (de).
extends Node

func install(base: OptimizedTranslation, overrides: Dictionary) -> void:
	var overlay := Translation.new()
	overlay.locale = base.locale
	for key: StringName in overrides:
		overlay.add_message(key, overrides[key])
	TranslationServer.remove_translation(base)
	TranslationServer.add_translation(overlay)   # first: wins for its keys
	TranslationServer.add_translation(base)      # second: serves everything else
```

Checked on 4.7.2: `add_message()` on an OptimizedTranslation changes nothing and reports nothing, `get_message_list()` returns an empty array with a warning, the first translation added for a locale wins, and a regional locale beats its base. Keep the source CSV or PO as the editable master; the optimized resource is a build product.

## 5. Accessibility: labels and OS preferences

```gdscript
# Autoload: OS accessibility preferences, merged with in-game settings.
# DisplayServer returns -1 (unknown), 0 or 1 and emits no change signal, so poll.
extends Node

signal changed

enum Pref { FOLLOW_OS, ON, OFF }

var reduce_motion_setting := Pref.FOLLOW_OS   # bound to the in-game options screen
var high_contrast_setting := Pref.FOLLOW_OS
var poll_enabled := true                       # tests set false, or the poll undoes their pins

var reduce_motion := false
var high_contrast := false
var _timer := 0.0

func _process(delta: float) -> void:
	if not poll_enabled:
		return
	_timer += delta
	if _timer >= 1.0:
		_timer = 0.0
		refresh()

func refresh() -> void:
	var motion := _resolve(reduce_motion_setting, DisplayServer.accessibility_should_reduce_animation())
	var contrast := _resolve(high_contrast_setting, DisplayServer.accessibility_should_increase_contrast())
	if motion != reduce_motion or contrast != high_contrast:
		reduce_motion = motion
		high_contrast = contrast
		changed.emit()

static func _resolve(setting: Pref, os_value: int) -> bool:
	match setting:
		Pref.ON:
			return true
		Pref.OFF:
			return false
		_:
			return os_value == 1   # -1 (unknown) counts as off

func pin_for_test(motion: bool, contrast: bool) -> void:
	poll_enabled = false
	reduce_motion = motion
	high_contrast = contrast
	changed.emit()
```

```gdscript
extends Control

func _ready() -> void:
	var play: Button = %PlayButton
	play.accessibility_name = tr("MENU_PLAY")
	play.accessibility_description = tr("MENU_PLAY_HINT")
```

- `DisplayServer.accessibility_should_reduce_animation()`, `accessibility_should_increase_contrast()` and `accessibility_should_reduce_transparency()` return -1 (unknown), 0 or 1; all three returned -1 headless (checked on 4.7.2). DisplayServer exposes no signal for preference changes, so poll about once a second.
- The in-game setting overrides the OS value. Tests that pin a value must stop the poll, or the next poll silently undoes the pin.
- Give every focusable Control an `accessibility_name` from the string table; set `accessibility_description` where the name alone is ambiguous. Test with VoiceOver on a device: support coverage varies by platform and engine version, so hand the audit to the accessibility seat.

## 6. Audio gate: master-bus peak probe

```gdscript
# Audio gate. Checked on 4.7.2: headless runs mix through the Dummy driver and the bus
# peak is still real (a test tone read -0.8 dB), so a headless run catches engine-side
# silence (missing streams, muted buses, failed loads). It cannot see device output
# (audio session, routing, silent switch): also run it once per platform on hardware.
# Exit 1 = silent build.
extends Node

const SILENCE_DB := -60.0
const SAMPLE_SECONDS := 2.0

@export var cue: AudioStream

func _ready() -> void:
	var player := AudioStreamPlayer.new()
	player.stream = cue
	player.bus = &"Master"
	add_child(player)
	player.play()
	var loudest := -200.0
	var elapsed := 0.0
	while elapsed < SAMPLE_SECONDS:
		await get_tree().process_frame
		elapsed += get_process_delta_time()
		var left := AudioServer.get_bus_peak_volume_left_db(0, 0)
		var right := AudioServer.get_bus_peak_volume_right_db(0, 0)
		loudest = maxf(loudest, maxf(left, right))
	print("audio_peak_db=%.1f" % loudest)
	get_tree().quit(0 if loudest > SILENCE_DB else 1)
```

A build can load every stream, report every player as playing, and still be silent: missing imports, a bus layout left out of the export, a muted bus, or a stream that failed to load through `FileAccess`. Load counters do not catch that; measured output does. Run the probe inside every exported pack in CI (headless is fine for the engine mix) and once per platform on hardware, with a cue that is loud by design.

## 7. Saves: canonical bytes and one write in flight

```gdscript
# Save writer: canonical bytes, one write in flight, newest request wins.
# Checked on 4.7.2: JSON.parse_string turns every number into a float, so a value that
# went through JSON (cloud copy) re-serializes as 1.0 where the live state says 1.
extends Node

const PATH := "user://save.json"

var _in_flight := -1
var _pending: PackedByteArray = []
var _last_requested: PackedByteArray = []   # newest state asked for: pending, in flight or written

static func canonical_bytes(state: Dictionary) -> PackedByteArray:
	return JSON.stringify(_normalize(state), "", true).to_utf8_buffer()   # sorted keys

static func _normalize(v: Variant) -> Variant:
	match typeof(v):
		TYPE_FLOAT:
			# exact integrality only: 0.999995 and 1000.004 must stay floats
			return int(v) if v == floorf(v) and absf(v) < 9.0e15 else v
		TYPE_DICTIONARY:
			var d := {}
			for k in v:
				d[str(k)] = _normalize(v[k])
			return d
		TYPE_ARRAY:
			return (v as Array).map(_normalize)
		_:
			return v

func request_save(state: Dictionary) -> void:
	var bytes := canonical_bytes(state)
	if bytes == _last_requested:
		return                      # unchanged: no write, no cloud push, no echo
	_last_requested = bytes
	_pending = bytes
	if _in_flight == -1:
		_start_write()

# Call before applying a state that arrived from the cloud, so it is not pushed back.
func note_applied_from_cloud(state: Dictionary) -> void:
	_last_requested = canonical_bytes(state)

func _start_write() -> void:
	var bytes := _pending
	_pending = PackedByteArray()
	_in_flight = WorkerThreadPool.add_task(_write_atomic.bind(bytes))

func _process(_delta: float) -> void:
	if _in_flight != -1 and WorkerThreadPool.is_task_completed(_in_flight):
		WorkerThreadPool.wait_for_task_completion(_in_flight)
		_in_flight = -1
		if not _pending.is_empty():
			_start_write()           # only the newest pending state is written

func _write_atomic(bytes: PackedByteArray) -> void:
	var tmp := PATH + ".tmp"
	var f := FileAccess.open(tmp, FileAccess.WRITE)
	if f == null:
		return
	f.store_buffer(bytes)
	f.close()
	DirAccess.rename_absolute(tmp, PATH)
```

- Checked on 4.7.2: `JSON.parse_string()` returns floats for every number, so `{"a":1}` re-serializes as `{"a":1.0}`. A cloud merge that compares re-serialized JSON sees a change on every pass, pushes, receives its own update and applies it again: a hitch once per sync interval. Compare canonical bytes and push only real changes.
- For local-only saves prefer `FileAccess.store_var()` / `var_to_bytes()`, which keep int and float types, inside the versioned envelope from the engine-architect seat.
- Compare each request with the newest requested bytes, not the last written ones: if state returns to the written bytes while another write is in flight, the stale write would land last. Call `note_applied_from_cloud()` before applying a cloud state so it is not pushed straight back.
- Retry cloud saves that are still downloading at launch instead of treating them as absent.

## 8. GUT tests

```gdscript
# test/unit/test_save_writer.gd
extends GutTest

const SaveWriter := preload("res://autoload/save_writer.gd")

func test_json_round_trip_keeps_canonical_bytes() -> void:
	var state := {"gold": 120, "day": 7, "ratio": 0.25}
	var once := SaveWriter.canonical_bytes(state)
	var echoed: Dictionary = JSON.parse_string(once.get_string_from_utf8())
	assert_eq(SaveWriter.canonical_bytes(echoed), once, "a cloud echo must not look like a change")

func test_ui_accept_has_gamepad_button() -> void:
	var has_joy := InputMap.action_get_events("ui_accept").any(
		func(e: InputEvent) -> bool: return e is InputEventJoypadButton)
	assert_true(has_joy, "menus must accept the gamepad confirm button")
```

```bash
# CI: headless GUT run with JUnit output (flag names as of GUT 9.x; check your version's --help)
godot --headless --path . -s addons/gut/gut_cmdln.gd \
  -gdir=res://test -ginclude_subdirs -gexit -gjunit_xml_file=build/gut.xml
```

- Keep the simulation in plain classes (`RefCounted` or static functions) so most tests need no scene tree.
- A lambda used as a predicate inside a test is fine; the method-only rule is for signal connections.
- Parse the JUnit file and fail on any failure line. The gate verdict is the AND of every step, never a summary line.
- Tours and automated sessions use their own save folder (a separate `user://` profile or a command-line flag) and never touch the player's cloud saves or achievements.

## 9. Wall-clock tests in a fresh process

```bash
# One process per timing test: earlier tests warm ResourceLoader, shader and glyph caches,
# and parallel jobs on a loaded host produce false failures.
mkdir -p build/perf; fail=0
for t in test/perf/test_*.gd; do
  load1=$(sysctl -n vm.loadavg | awk '{print $2}')
  godot --headless --path . -s addons/gut/gut_cmdln.gd -gtest="res://$t" -gexit \
    -gjunit_xml_file="build/perf/$(basename "$t" .gd).xml" || fail=1
  echo "$t host_load_1m=$load1" >> build/perf/host_load.txt
done
exit $fail
```

Headless runs use a dummy renderer: `Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME` reads 0, so draw-call and GPU budgets must run windowed on real hardware. Load-time, sim-throughput and engine-mix audio checks can run headless.
