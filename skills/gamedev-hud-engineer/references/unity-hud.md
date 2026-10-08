# Unity HUD Implementation (UGUI + TextMeshPro, UI Toolkit)

Snippets follow the rules in SKILL.md: change-only updates, canvases split by update frequency, pooled transient elements, safe-area-aware roots.

## 1. Canvas split

```
HUD_Root (Canvas, Screen Space - Overlay or Camera, CanvasScaler 1920x1080, match 0.5–1.0)
├── SafeArea (RectTransform + SafeAreaFitter)
│   ├── Static     (Canvas, no GraphicRaycaster)        frame art, labels that never change
│   ├── Slow       (Canvas, no GraphicRaycaster)        currency, level, quest tracker
│   ├── Fast       (Canvas, no GraphicRaycaster)        HP/energy bars, cooldown fills, timers
│   ├── Controls   (Canvas, GraphicRaycaster)           buttons, joystick (only interactive canvas)
│   └── Toasts     (Canvas, GraphicRaycaster if tappable)
└── Transient (Canvas, full-screen, no raycaster)       damage numbers (positions from world → screen)
```

A nested Canvas isolates its children: a change inside "Fast" re-batches only "Fast". Keep the interactive canvas small so GraphicRaycaster walks few graphics.

## 2. Safe-area fitter

```csharp
[RequireComponent(typeof(RectTransform))]
public sealed class SafeAreaFitter : MonoBehaviour
{
    private RectTransform rect;
    private Rect lastSafe;
    private Vector2Int lastSize;
    private ScreenOrientation lastOrientation;

    private void Awake() { rect = (RectTransform)transform; Apply(); }

    private void Update()
    {
        // Cheap comparison; Screen.safeArea changes on rotation, split screen, foldable posture.
        if (Screen.safeArea != lastSafe || Screen.width != lastSize.x || Screen.height != lastSize.y
            || Screen.orientation != lastOrientation)
            Apply();
    }

    private void Apply()
    {
        Rect safe = Screen.safeArea;
        lastSafe = safe;
        lastSize = new Vector2Int(Screen.width, Screen.height);
        lastOrientation = Screen.orientation;
        if (Screen.width <= 0 || Screen.height <= 0) return;

        Vector2 min = safe.position;
        Vector2 max = safe.position + safe.size;
        min.x /= Screen.width;  min.y /= Screen.height;
        max.x /= Screen.width;  max.y /= Screen.height;
        rect.anchorMin = min;
        rect.anchorMax = max;
        rect.offsetMin = Vector2.zero;
        rect.offsetMax = Vector2.zero;
    }
}
```

Backgrounds stay outside SafeArea (full-bleed); everything readable or tappable goes inside. Test with the Device Simulator, then on real notch/cutout devices.

## 3. Presenter with change-only updates

```csharp
public sealed class PlayerHudPresenter : IDisposable
{
    private readonly PlayerModel model;     // raises events on change
    private readonly HudView view;
    private int shownGold = int.MinValue;

    public PlayerHudPresenter(PlayerModel model, HudView view)
    {
        this.model = model;
        this.view = view;
        model.HealthChanged += OnHealthChanged;
        model.GoldChanged += OnGoldChanged;
        OnHealthChanged(model.Health, model.MaxHealth);
        OnGoldChanged(model.Gold);
    }

    private void OnHealthChanged(int hp, int max) => view.HealthBar.SetTarget(hp / (float)max);

    private void OnGoldChanged(int gold)
    {
        if (gold == shownGold) return;
        shownGold = gold;
        view.GoldLabel.SetText("{0}", gold);   // TMP: no string allocation for numeric formats
    }

    public void Dispose()
    {
        model.HealthChanged -= OnHealthChanged;
        model.GoldChanged -= OnGoldChanged;
    }
}
```

## 4. Health bar with ghost (delayed) fill

```csharp
public sealed class GhostBar : MonoBehaviour
{
    [SerializeField] private Image fill;       // Image Type: Filled, or scale a RectTransform
    [SerializeField] private Image ghost;
    [SerializeField] private float holdSeconds = 0.4f;
    [SerializeField] private float catchUpRate = 6f;   // exp smoothing constant

    private float target = 1f, ghostValue = 1f, holdTimer;

    public void SetTarget(float normalized)
    {
        normalized = Mathf.Clamp01(normalized);
        if (normalized < target) holdTimer = holdSeconds;          // damage: ghost waits
        else ghostValue = normalized;                              // heal: ghost leads
        target = normalized;
        fill.fillAmount = target;                                  // truth snaps immediately
        ghost.fillAmount = ghostValue;
        enabled = true;
    }

    private void Update()
    {
        if (holdTimer > 0f) { holdTimer -= Time.unscaledDeltaTime; return; }
        ghostValue = target + (ghostValue - target) * Mathf.Exp(-catchUpRate * Time.unscaledDeltaTime);
        if (Mathf.Abs(ghostValue - target) < 0.001f) { ghostValue = target; enabled = false; } // stop dirtying the canvas
        ghost.fillAmount = ghostValue;
    }
}
```

`enabled = false` when idle is the point: an idle bar must not touch its Graphic.

## 5. Damage number pool with merge and cap

```csharp
public sealed class DamageNumbers : MonoBehaviour
{
    [SerializeField] private DamageLabel prefab;     // TMP_Text + simple tween, no Animator
    [SerializeField] private RectTransform layer;    // Transient canvas
    [SerializeField] private int maxConcurrent = 24;
    [SerializeField] private float mergeWindow = 0.15f;

    private readonly Stack<DamageLabel> free = new();
    private readonly List<DamageLabel> active = new(32);
    private Camera cam;

    private void Awake()
    {
        cam = Camera.main;
        for (int i = 0; i < maxConcurrent; i++)
        {
            var l = Instantiate(prefab, layer);
            l.gameObject.SetActive(false);
            free.Push(l);
        }
    }

    public void Show(int targetId, Vector3 worldPos, int amount, bool crit)
    {
        // Merge into a live label for the same target within the window (non-crit only).
        if (!crit)
            for (int i = 0; i < active.Count; i++)
            {
                var a = active[i];
                if (a.TargetId == targetId && !a.IsCrit && a.Age < mergeWindow) { a.Add(amount); return; }
            }

        DamageLabel label;
        if (free.Count > 0) label = free.Pop();
        else
        {
            int victim = SmallestNonCrit();
            if (victim < 0) return;                    // all crits on screen: drop the new non-crit
            label = active[victim];
            active.RemoveAt(victim);
        }

        Vector3 screen = cam.WorldToScreenPoint(worldPos);
        if (screen.z < 0f) { free.Push(label); return; }   // behind camera
        screen.x += Random.Range(-24f, 24f);
        label.Begin(targetId, screen, amount, crit);   // crit: 1.4x scale + color + bold weight
        label.gameObject.SetActive(true);
        active.Add(label);
    }

    private void Update()
    {
        float dt = Time.deltaTime;
        for (int i = active.Count - 1; i >= 0; i--)
            if (!active[i].Tick(dt))
            {
                active[i].gameObject.SetActive(false);
                free.Push(active[i]);
                active.RemoveAt(i);
            }
    }

    private int SmallestNonCrit()
    {
        int idx = -1, min = int.MaxValue;
        for (int i = 0; i < active.Count; i++)
            if (!active[i].IsCrit && active[i].Amount < min) { min = active[i].Amount; idx = i; }
        return idx;
    }
}
```

For very high counts (hundreds of numbers), replace per-label GameObjects with a single mesh of glyph quads rebuilt once per frame, or world-space instanced quads with a digit atlas.

## 6. Notification queue (priority, coalescing, TTL, combat suppression)

```csharp
public enum ToastPriority { Critical = 0, Gameplay = 1, Reward = 2, Social = 3 }

public readonly struct Toast
{
    public Toast(string key, ToastPriority p, int amount, float ttl) { Key = key; Priority = p; Amount = amount; Ttl = ttl; }
    public string Key { get; }
    public ToastPriority Priority { get; }
    public int Amount { get; }
    public float Ttl { get; }
    public Toast WithAmount(int a) => new Toast(Key, Priority, a, Ttl);
}

public sealed class ToastQueue
{
    private readonly List<Toast> pending = new(16);
    private readonly int maxVisible;
    private readonly float coalesceWindow;
    private readonly Dictionary<string, float> lastSeen = new();
    public bool InCombat { get; set; }

    public ToastQueue(int maxVisible = 3, float coalesceWindow = 1.5f)
    { this.maxVisible = maxVisible; this.coalesceWindow = coalesceWindow; }

    public void Enqueue(Toast t, float now)
    {
        // Coalesce: same key still pending within the window → replace with summed amount.
        for (int i = 0; i < pending.Count; i++)
            if (pending[i].Key == t.Key && now - lastSeen[t.Key] < coalesceWindow)
            {
                pending[i] = pending[i].WithAmount(pending[i].Amount + t.Amount);
                lastSeen[t.Key] = now;
                return;
            }
        lastSeen[t.Key] = now;
        int at = pending.FindIndex(p => p.Priority > t.Priority);   // stable by priority
        if (at < 0) pending.Add(t); else pending.Insert(at, t);
    }

    public bool TryDequeue(int visibleNow, out Toast next)
    {
        next = default;
        if (visibleNow >= maxVisible || pending.Count == 0) return false;
        var head = pending[0];
        if (InCombat && head.Priority >= ToastPriority.Reward) return false;   // hold until combat ends
        pending.RemoveAt(0);
        next = head;
        return true;
    }
}
```

Critical toasts may preempt: if a P0 arrives and the screen is full, dismiss the oldest lowest-priority visible toast. The `FindIndex` lambda captures `t` and allocates a closure per call; replace it with a plain loop if the enqueue rate is high.

## 7. Show/hide without rebuilds

```csharp
public static class HudVisibility
{
    public static void Set(CanvasGroup g, bool visible)
    {
        g.alpha = visible ? 1f : 0f;
        g.blocksRaycasts = visible;
        g.interactable = visible;
    }

    // For panels hidden for long periods, disable the Canvas component itself:
    public static void SetCanvas(Canvas c, bool visible) => c.enabled = visible;
}
```

Alpha 0 still costs batching and overdraw. For anything hidden longer than a few seconds, disable the Canvas (keeps layout, skips rendering) rather than `SetActive(false)` (which triggers OnEnable/OnDisable and rebuilds on return).

## 8. UI Toolkit HUD binding

```csharp
public sealed class HudDocument : MonoBehaviour
{
    [SerializeField] private UIDocument doc;
    private Label goldLabel;
    private VisualElement hpFill;
    private int shownGold = int.MinValue;

    private void OnEnable()
    {
        var root = doc.rootVisualElement;
        goldLabel = root.Q<Label>("gold");
        hpFill = root.Q<VisualElement>("hp-fill");
        hpFill.usageHints = UsageHints.DynamicTransform;   // scale changes every hit: avoid re-tessellation
    }

    public void SetGold(int gold)
    {
        if (gold == shownGold) return;
        shownGold = gold;
        goldLabel.text = gold.ToString();                  // allocates; acceptable at change frequency only
    }

    public void SetHp(float normalized) => hpFill.style.scale = new Scale(new Vector3(normalized, 1f, 1f));
}
```

```css
/* hud.uss */
#hp-fill { transform-origin: left; background-color: rgb(220, 60, 60); }
.toast { transition-property: opacity, translate; transition-duration: 0.2s; }
```

Use `scale`/`translate` (transform) rather than `width`/`left` for animated elements: transform changes skip layout. Respect `Screen.safeArea` by padding the root element on geometry change.

## 9. Profiler checklist for UGUI

- `Canvas.BuildBatch` / `Canvas.SendWillRenderCanvases` time and frequency per canvas.
- `Layout.PerformLayout` / `Graphic.Rebuild` counts — should be zero on idle frames.
- Frame Debugger: count UI batches; look for breaks caused by font/atlas interleaving.
- GC Alloc from UI code paths at peak event rate: target 0 B.
- GPU: enable overdraw view in the Scene view or use a GPU tool on device to measure full-screen transparent layers.
