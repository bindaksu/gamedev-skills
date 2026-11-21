# Tokens to Engine, and Figma-to-Engine Mapping

Read this when wiring a Figma token set into Unity (UGUI or UI Toolkit), or when an engineer asks how a Figma property maps to an engine property.

## 1. Token pipeline

```
Figma Variables (modes: default, event_halloween, high_contrast)
   │  export plugin or REST API → tokens.json (DTCG-style: $value, $type)
   ▼
CI step: validate (no raw hex in components, every alias resolves, contrast pairs pass)
   ▼
Importer → UGUI: ScriptableObject UiTheme asset per mode
         → UI Toolkit: generated .uss with custom properties (--color-action-primary)
   ▼
Runtime: theme switch = swap one asset / one stylesheet; no prefab edits
```

Modes are the lever: LiveOps event themes and the accessibility high-contrast theme are both just token modes. If an event reskin needs prefab edits, a component is bypassing tokens.

## 2. UGUI: ScriptableObject theme

```csharp
using UnityEngine;

[CreateAssetMenu(menuName = "UI/Theme")]
public sealed class UiTheme : ScriptableObject {
    [System.Serializable] public struct ColorToken { public string key; public Color value; }
    [System.Serializable] public struct FloatToken { public string key; public float value; }
    public ColorToken[] colors;
    public FloatToken[] spacing;
    public FloatToken[] motionMs;

    public Color Color(string key) {
        foreach (var t in colors) if (t.key == key) return t.value;
        Debug.LogError($"Missing color token {key}");
        return UnityEngine.Color.magenta; // loud on purpose
    }
}

// Component binding: components store token keys, never colors.
[RequireComponent(typeof(UnityEngine.UI.Graphic))]
public sealed class TokenColor : MonoBehaviour {
    [SerializeField] string token = "action.primary";
    public void Apply(UiTheme theme) => GetComponent<UnityEngine.UI.Graphic>().color = theme.Color(token);
}
```

Cache lookups into a dictionary at load if more than a few hundred bindings exist; linear search is shown for clarity.

## 3. UI Toolkit: generated USS

```css
:root {
  --color-action-primary: #3FC35A;
  --color-action-primary-pressed: #2E9A45;
  --color-text-primary: #FFFFFF;
  --space-2: 16px;
  --radius-m: 20px;
}
.btn-primary {
  background-color: var(--color-action-primary);
  border-radius: var(--radius-m);
  padding: var(--space-2);
  -unity-font-style: bold;
}
.btn-primary:active { background-color: var(--color-action-primary-pressed); scale: 0.94 0.94; }
.btn-primary:disabled { opacity: 0.6; }
```

UI Toolkit layout is flexbox (Yoga), so Figma auto layout maps closely. UGUI layout groups do not, and nested layout groups trigger expensive rebuilds; prefer anchors in UGUI and hand rebuild cost to the HUD engineer.

## 4. Figma property → engine mapping

| Figma | UGUI | UI Toolkit | Gotcha |
|---|---|---|---|
| Constraints left/right | RectTransform anchors min.x=0, max.x=1 | `position` + `left`/`right` or flex-grow | Figma "scale" constraint has no UGUI equivalent; spec it explicitly |
| Auto layout, horizontal, gap 16 | HorizontalLayoutGroup spacing 16 | `flex-direction: row` + margins | UI Toolkit has no `gap` in older versions; verify current version, else use margins |
| Hug contents | ContentSizeFitter | default flex behavior | ContentSizeFitter inside a LayoutGroup fights it; use one or the other |
| Corner radius | 9-slice sprite | `border-radius` | UGUI needs art; UI Toolkit draws it, but per-element radius breaks batching less than you fear; still profile |
| Drop shadow | baked into sprite border or Shadow component | no native box-shadow; use a sliced sprite | Shadow component duplicates vertices; bake it |
| Text outline | TMP material outline | TMP/Text Core outline via font asset material | Outline width is material-wide; make presets, not per-label tweaks |
| Blend modes | custom shader | not supported broadly | Bake blends into the sprite |
| Effects: background blur | expensive grab-pass | not native | Avoid on mobile; use a pre-blurred static capture |

Native shells (store, settings, account screens in SwiftUI or Jetpack Compose): Figma constraints map to `.frame(maxWidth: .infinity)` or `Modifier.fillMaxWidth()`, auto layout to `HStack`/`VStack` or `Row`/`Column` with `spacing` or `Arrangement.spacedBy`, and color tokens to an asset catalog or a Compose `ColorScheme` generated from the same tokens.json.

## 5. Export rules

- Export each raster at the size it renders on the **largest supported device** at full scale, not at reference size, or tablets look soft.
- Trim transparent padding, but keep 2 px padding inside the atlas (packer setting) to stop bleeding.
- PNG, sRGB, straight alpha. No baked text. No baked prices.
- File names: `ui_<screen-or-common>_<element>_<state>.png`, lowercase snake case, no version numbers.
- Every 9-slice sprite ships with its four border values in the import settings and in the handoff table.

## 6. Handoff review script (10 minutes, with the implementing engineer)

1. Walk the canvas contract; confirm the match rule code is in the scene.
2. Walk the element table top to bottom; engineer reads back anchor and pivot per element.
3. Show all states per component; engineer confirms each has a trigger in code.
4. Show the pseudo-loc frame and the max-value frame.
5. Agree on the overlay-diff acceptance threshold and which devices it is checked on.
