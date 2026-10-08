# Native HUD Implementation: SpriteKit, SwiftUI, Compose

## SpriteKit HUD layer pinned to the safe area

```swift
import SpriteKit

final class HUDNode: SKNode {
    private let hpBack = SKSpriteNode(color: .darkGray, size: CGSize(width: 180, height: 14))
    private let hpFill = SKSpriteNode(color: .systemRed, size: CGSize(width: 180, height: 14))
    private let goldLabel = SKLabelNode(fontNamed: "Menlo-Bold")
    private var shownGold = Int.min

    override init() {
        super.init()
        zPosition = 1000
        hpFill.anchorPoint = CGPoint(x: 0, y: 0.5)
        hpBack.anchorPoint = CGPoint(x: 0, y: 0.5)
        hpFill.zPosition = 1
        goldLabel.fontSize = 22
        goldLabel.horizontalAlignmentMode = .right
        [hpBack, hpFill, goldLabel].forEach(addChild)
    }
    required init?(coder: NSCoder) { fatalError() }

    /// Call from didMove(to:) and from viewSafeAreaInsetsDidChange / size changes.
    func layout(in scene: SKScene, insets: UIEdgeInsets) {
        // Scene coordinates: origin bottom-left when anchorPoint == .zero; convert points from view space.
        let w = scene.size.width, h = scene.size.height
        let margin: CGFloat = 12
        hpBack.position = CGPoint(x: insets.left + margin, y: h - insets.top - margin - 7)
        hpFill.position = hpBack.position
        goldLabel.position = CGPoint(x: w - insets.right - margin, y: h - insets.top - margin - 22)
    }

    func setHealth(_ normalized: CGFloat) {
        hpFill.xScale = max(0, min(1, normalized))     // scale, not resize: no texture work
    }

    func setGold(_ gold: Int) {
        guard gold != shownGold else { return }       // SKLabelNode re-renders text on every change
        shownGold = gold
        goldLabel.text = "\(gold)"
    }
}
```

Wiring in the scene (when the scene uses `.resizeFill` scale mode, points map 1:1 to view points):

```swift
final class GameScene: SKScene {
    let hud = HUDNode()
    override func didMove(to view: SKView) {
        anchorPoint = .zero
        camera?.addChild(hud) ?? addChild(hud)         // attach to the camera so it stays screen-fixed
        hud.layout(in: self, insets: view.safeAreaInsets)
    }
    override func didChangeSize(_ oldSize: CGSize) {
        guard let view else { return }
        hud.layout(in: self, insets: view.safeAreaInsets)
    }
}
```

With a camera node, HUD children are positioned relative to the camera center; convert accordingly. With `.aspectFill` scale mode, convert inset points into scene units (`convertPoint(fromView:)`) instead of using them directly.

### SpriteKit performance flags

```swift
skView.showsFPS = true
skView.showsNodeCount = true
skView.showsDrawCount = true
skView.ignoresSiblingOrder = true      // allow batching; order by zPosition explicitly
```

- Put HUD sprites in one texture atlas (`.atlas` folder or `SKTextureAtlas`) so they batch into few draws.
- `SKLabelNode` text changes are expensive; for rapidly changing digits, use a bitmap-font of `SKSpriteNode` digits from an atlas.
- `SKCropNode` and `SKEffectNode` break batching and add offscreen passes; avoid them in the HUD.
- SpriteKit is not deprecated but has no announced roadmap, and developers report frame-rate regressions across iOS 26.x (as of 2026-10; verify). Measure on current OS releases.

## SwiftUI overlay on top of a Metal/SpriteKit view (menus and light HUD only)

```swift
struct GameScreen: View {
    @State private var model = HUDModel()          // @Observable; update only on change
    var body: some View {
        ZStack {
            GameViewRepresentable(model: model)    // MTKView / SKView wrapper, full-bleed
                .ignoresSafeArea()
            VStack {
                HStack {
                    HealthBar(value: model.health).frame(width: 180, height: 14)
                    Spacer()
                    Text(model.gold, format: .number).monospacedDigit().font(.headline)
                }
                Spacer()
            }
            .padding(12)                           // SwiftUI respects the safe area by default
            .allowsHitTesting(false)               // let touches reach the game view
        }
    }
}
```

SwiftUI diffing is fine for values that change a few times per second. Do not drive per-frame animation (timers ticking at 60 Hz, damage numbers) through `@State`; render those in the game renderer.

## Compose overlay over a game SurfaceView (Android)

Pattern: GameActivity or an engine activity owns the render loop on a SurfaceView; a `ComposeView` sibling draws out-of-loop UI. Never draw game-rate content on a Compose Canvas — it runs on the main thread. The overlay pattern is common practice, not an official recommendation (as of 2026-10; verify).

```kotlin
class GameHostActivity : GameActivity() {
    private val hud = HudState()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        WindowCompat.setDecorFitsSystemWindows(window, false)
        window.attributes = window.attributes.apply {
            layoutInDisplayCutoutMode =
                WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES
        }
        val overlay = ComposeView(this).apply {
            setContent { HudOverlay(hud) }
        }
        addContentView(
            overlay,
            ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT)
        )
    }
}

@Stable
class HudState {
    var health by mutableFloatStateOf(1f)
    var gold by mutableIntStateOf(0)
}

@Composable
fun HudOverlay(state: HudState) {
    Box(
        Modifier
            .fillMaxSize()
            .windowInsetsPadding(WindowInsets.safeDrawing)   // system bars + display cutout
            .padding(12.dp)
    ) {
        Row(Modifier.align(Alignment.TopStart), verticalAlignment = Alignment.CenterVertically) {
            HealthBar(value = { state.health })               // lambda: read deferred to draw phase
        }
        Text(
            text = state.gold.toString(),
            modifier = Modifier.align(Alignment.TopEnd),
            style = MaterialTheme.typography.titleMedium
        )
    }
}

@Composable
fun HealthBar(value: () -> Float) {
    Box(
        Modifier
            .size(180.dp, 14.dp)
            .background(Color.DarkGray)
            .drawBehind { drawRect(Color.Red, size = size.copy(width = size.width * value())) }
    )
}
```

Touch pass-through: a `ComposeView` that fills the screen consumes touches only where a composable handles pointer input. Non-interactive HUD elements without `clickable`/`pointerInput` let events fall through to the SurfaceView below; verify on device, because a full-screen `View` with a background or click listener will swallow all touches. For gameplay-critical input, route touches to the native side first and forward only UI regions to Compose.

Performance notes:
- Push values from the game thread to `HudState` at most on change, and post to the main thread; batch updates per frame rather than per event.
- Use lambda-based modifiers (`drawBehind { value() }`, `Modifier.offset { }`) so changes skip recomposition and only redraw.
- Keep Compose off the frame-critical path: the game must render even if the main thread is busy with Compose.

## Reading insets correctly

| Platform | API | Notes |
|---|---|---|
| Unity | `Screen.safeArea` | Pixels, bottom-left origin; recompute on rotation/resize |
| iOS UIKit | `view.safeAreaInsets`, `viewSafeAreaInsetsDidChange()` | Landscape notch/Dynamic Island devices have left and right insets plus a bottom home-indicator inset |
| SwiftUI | default safe-area layout, `.ignoresSafeArea()` for backgrounds | |
| Android Views | `ViewCompat.setOnApplyWindowInsetsListener` with `WindowInsetsCompat.Type.displayCutout() or systemBars()` | Set `layoutInDisplayCutoutMode` or the cutout side is letterboxed |
| Compose | `WindowInsets.safeDrawing`, `displayCutout`, `systemBars` | |

Never hardcode inset values; example magnitudes differ per device and orientation and change with new hardware.
