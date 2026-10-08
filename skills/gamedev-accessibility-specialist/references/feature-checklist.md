# Accessibility Feature Checklist and Platform Snippets

Read this when running a barrier audit or implementing screen-reader support. The tiers below follow the Game Accessibility Guidelines' basic / intermediate / advanced structure as a planning aid. Wording is paraphrased; check the current GAG and XAG text before quoting either.

## 1. Audit checklist by category

Suggested tier: B = basic (do for every game), I = intermediate (do where the genre needs it), A = advanced (do where the genre depends on it).

### Vision

| Item | Tier | Test |
|---|---|---|
| Default text readable at target viewing distance | B | Device at real distance, smallest supported screen |
| Text size option for UI and subtitles separately | I | Max size reflows, never truncates critical text |
| No essential info by color alone | B | Grayscale screenshot of 10 worst frames |
| Contrast of text and UI against worst-case background | B | 4.5:1 text, 3:1 large text and component edges |
| Colorblind palette remap modes | I | Simulate protan, deutan, tritan |
| High-contrast mode (outlines on actors, flat backgrounds) | A | Playable in grayscale at 50% brightness |
| Screen-reader access to menus, store, settings | I (B for store and cancel flows) | VoiceOver and TalkBack full pass |
| Audio description for cinematics | A | Narrative-heavy games |
| Camera options: field of view, motion blur off, shake off | B | Each independent toggle or slider |

### Hearing

| Item | Tier | Test |
|---|---|---|
| Subtitles for all speech, on by first-launch choice | B | Size, box, line length, cps per spec |
| Separate volume sliders (master, music, SFX, voice, UI) | B | Each bus independently to zero |
| Visual or haptic twin for every gameplay-relevant audio cue | B | Play muted end to end |
| Captions for important non-speech sound | I | [sound] tags toggle |
| Directional indicators for off-screen sounds | I | Muted play still locates threats |
| Mono audio | I | Single-earbud play loses no cues |
| Speech-to-text and text-to-speech for voice chat | I (CVAA-relevant if chat exists) | Chat usable without hearing or speech |

### Motor

| Item | Tier | Test |
|---|---|---|
| Full remap including menus; 2 bindings per action | B on controller and PC | Remap every action, then complete the FTUE |
| Toggle alternative for every hold | B | No sustained hold required anywhere |
| No rapid mashing required | B | Hold alternative or auto-repeat |
| Timing-window multiplier or no-fail for QTEs | I | 2.0x completes all timed sections |
| Relocatable and resizable touch controls | I | Left-handed and one-handed layouts saved |
| Sensitivity sliders and aim assist strength | I | Low-precision input completes combat |
| Simultaneous inputs capped at 2 | B | No chords above 2 inputs |
| Works with adaptive controllers via standard controller mapping | I | Xbox Adaptive Controller or PlayStation Access controller run-through |

### Cognitive

| Item | Tier | Test |
|---|---|---|
| Objective reminder always available | B | Return after 24 h; next step clear in 10 s |
| Tutorials replayable from settings | B | Every tutorial reachable post-completion |
| Pause anywhere in single-player content | B | Pause during cinematics and timed reading |
| Difficulty and assist options without penalty labels | I | Wording review; no locked rewards for assists |
| Consistent icons and controls across modes | B | Same action, same icon, same button everywhere |
| Plain-language tutorial text, about grade 6 to 8 (heuristic) | I | Readability scorer on source strings |
| Reduce clutter option (hide non-critical HUD) | A | HUD minimal preset |

### Speech

| Item | Tier | Test |
|---|---|---|
| No required voice input | B | Every voice feature has a non-voice path |
| Quick-chat or ping system as voice alternative | I | Team play without voice |

### Photosensitivity and vestibular

| Item | Tier | Test |
|---|---|---|
| Flash analyzer pass (3 per second rule) | B | Captured footage of VFX-heavy moments |
| Reduce-flash toggle | I | Full-screen flashes damped or removed |
| Screen shake slider 0–100% | B | Independent of OS Reduce Motion |
| Motion blur, chromatic aberration, head-bob toggles | I | Each independent |

## 2. iOS: game surface with VoiceOver

```swift
import UIKit
import AVFoundation

final class GameViewController: UIViewController {
    private let synth = AVSpeechSynthesizer()
    var selfVoicingEnabled = false

    override func viewDidLoad() {
        super.viewDidLoad()
        view.isAccessibilityElement = true
        view.accessibilityLabel = "Game board"
        view.accessibilityTraits = .allowsDirectInteraction   // touches pass to the game
        NotificationCenter.default.addObserver(
            self, selector: #selector(voiceOverChanged),
            name: UIAccessibility.voiceOverStatusDidChangeNotification, object: nil)
    }

    @objc private func voiceOverChanged() {
        if UIAccessibility.isVoiceOverRunning { synth.stopSpeaking(at: .immediate) }
    }

    func announce(_ text: String) {
        if UIAccessibility.isVoiceOverRunning {
            UIAccessibility.post(notification: .announcement, argument: text)
        } else if selfVoicingEnabled {
            synth.speak(AVSpeechUtterance(string: text))
        }
    }
}
```

Menus built in UIKit or SwiftUI over the game view get VoiceOver for free if labeled. That is why store and settings overlays are often native even in engine games.

## 3. Android: virtual views on a game surface

```kotlin
class BoardAccessHelper(
    private val host: View,
    private val board: BoardModel
) : ExploreByTouchHelper(host) {

    override fun getVirtualViewAt(x: Float, y: Float): Int =
        board.cellAt(x, y)?.id ?: INVALID_ID

    override fun getVisibleVirtualViews(ids: MutableList<Int>) {
        board.cells.forEach { ids.add(it.id) }
    }

    override fun onPopulateNodeForVirtualView(id: Int, node: AccessibilityNodeInfoCompat) {
        val cell = board.cell(id)
        node.contentDescription = cell.describe()      // "Red gem, row 3 column 5"
        node.setBoundsInParent(cell.bounds)            // required by ExploreByTouchHelper
        node.addAction(AccessibilityNodeInfoCompat.ACTION_CLICK)
    }

    override fun onPerformActionForVirtualView(id: Int, action: Int, args: Bundle?): Boolean =
        if (action == AccessibilityNodeInfoCompat.ACTION_CLICK) { board.tap(id); true } else false
}

// Host view wiring
class BoardView(ctx: Context) : SurfaceView(ctx) {
    lateinit var helper: BoardAccessHelper
    fun attach(board: BoardModel) {
        helper = BoardAccessHelper(this, board)
        ViewCompat.setAccessibilityDelegate(this, helper)
    }
    override fun dispatchHoverEvent(e: MotionEvent): Boolean =
        helper.dispatchHoverEvent(e) || super.dispatchHoverEvent(e)
}
// After a board change: helper.invalidateVirtualView(cellId) or helper.invalidateRoot()
```

Detect screen-reader mode with `AccessibilityManager.isTouchExplorationEnabled` and switch the game into a turn-paced, describe-on-focus interaction model where the genre allows.

## 4. Option menu IA (recommended order)

```
ACCESSIBILITY
  Presets: Vision | Hearing | Motor | Cognitive   (each sets several options; all remain editable)
  Text & Subtitles   subtitles, captions, size, background, speaker names, UI text size
  Color              colorblind mode, high contrast, HUD opacity
  Audio              volume buses, mono, visual sound indicators
  Controls           remap, hold/toggle, timing multiplier, sensitivity, touch layout editor
  Motion & Flash     shake, flash reduction, motion blur, camera bob
  Assists            difficulty, aim assist, skip puzzle or QTE, objective reminder
```

Presets help players who do not know which options they need; they must never lock individual settings.
