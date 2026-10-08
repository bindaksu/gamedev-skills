# Asset Validation Tools

Read this when building the import pipeline or CI checks. Snippets target Unity 6 with URP and Blender 4.x; verify API names against your exact versions before relying on them.

## 1. Texture import rules (AssetPostprocessor)

```csharp
using UnityEditor;

public sealed class TextureImportRules : AssetPostprocessor {
    void OnPreprocessTexture() {
        var ti = (TextureImporter)assetImporter;
        string p = assetPath.ToLowerInvariant();
        ti.isReadable = false;                                   // no CPU copy, ever

        if (p.Contains("/ui/")) {
            ti.textureType = TextureImporterType.Sprite;
            ti.mipmapEnabled = false;                            // mips on UI waste 33%
            ti.sRGBTexture = true;
            SetFormat(ti, 2048, TextureImporterFormat.ASTC_4x4);
        } else if (p.EndsWith("_n.png") || p.EndsWith("_n.tga")) {
            ti.textureType = TextureImporterType.NormalMap;      // linear, normal-encoded
            SetFormat(ti, 1024, TextureImporterFormat.ASTC_5x5);
        } else if (p.Contains("_orm") || p.Contains("_m.")) {
            ti.sRGBTexture = false;                              // data, not color
            SetFormat(ti, 512, TextureImporterFormat.ASTC_6x6);
        } else if (p.Contains("/vfx/")) {
            ti.sRGBTexture = true;
            SetFormat(ti, 1024, TextureImporterFormat.ASTC_6x6);
        } else {
            ti.sRGBTexture = true;
            ti.mipmapEnabled = true;
            SetFormat(ti, 1024, TextureImporterFormat.ASTC_6x6);
        }
    }

    static void SetFormat(TextureImporter ti, int maxSize, TextureImporterFormat fmt) {
        foreach (var platform in new[] { "iPhone", "Android" }) {
            var s = ti.GetPlatformTextureSettings(platform);
            s.overridden = true;
            s.maxTextureSize = maxSize;
            s.format = fmt;
            ti.SetPlatformTextureSettings(s);
        }
    }
}
```

Path conventions drive the rules, so the folder taxonomy is part of the pipeline contract. Changing a rule re-imports every matching asset; schedule it.

## 2. Model import rules

```csharp
using UnityEditor;
using UnityEngine;

public sealed class ModelImportRules : AssetPostprocessor {
    const int MaxBonesHero = 80, MaxBonesNpc = 45;

    void OnPreprocessModel() {
        var mi = (ModelImporter)assetImporter;
        mi.isReadable = false;
        mi.optimizeMeshPolygons = true;
        mi.optimizeMeshVertices = true;
        mi.skinWeights = ModelImporterSkinWeights.Custom;
        mi.maxBonesPerVertex = 4;                 // author at 4; tier quality setting lowers at runtime
        mi.importBlendShapes = assetPath.Contains("/characters/hero/");
    }

    void OnPostprocessModel(GameObject root) {
        int limit = assetPath.Contains("/characters/hero/") ? MaxBonesHero : MaxBonesNpc;
        foreach (var smr in root.GetComponentsInChildren<SkinnedMeshRenderer>())
            if (smr.bones.Length > limit)
                Debug.LogError($"{assetPath}: {smr.name} has {smr.bones.Length} bones (limit {limit})");
    }
}
```

## 3. Shader variant stripping

```csharp
using System.Collections.Generic;
using UnityEditor.Build;
using UnityEditor.Rendering;
using UnityEngine;
using UnityEngine.Rendering;

sealed class StripUnusedVariants : IPreprocessShaders {
    public int callbackOrder => 10;   // after the render pipeline's own stripping
    static readonly ShaderKeyword FogExp2 = new("FOG_EXP2");
    static readonly ShaderKeyword FogExp = new("FOG_EXP");

    public void OnProcessShader(Shader shader, ShaderSnippetData snippet, IList<ShaderCompilerData> data) {
        int before = data.Count;
        for (int i = data.Count - 1; i >= 0; i--) {
            var k = data[i].shaderKeywordSet;
            if (k.IsEnabled(FogExp2) || k.IsEnabled(FogExp)) data.RemoveAt(i);   // project uses linear fog only
        }
        if (before - data.Count > 0)
            Debug.Log($"[strip] {shader.name}/{snippet.passName}: {before} -> {data.Count}");
    }
}
```

Use the render pipeline asset's own feature toggles and stripping settings first (disable features you never use per quality tier); write custom strippers only for what those settings cannot express. Log counts every build and alert on a jump of more than 20%.

## 4. CI audit entry point

```csharp
using System.Linq;
using UnityEditor;
using UnityEngine;

public static class AssetAudit {
    public static void Run() {
        int violations = 0;
        foreach (var guid in AssetDatabase.FindAssets("t:Texture2D", new[] { "Assets/Art", "Assets/UI" })) {
            string path = AssetDatabase.GUIDToAssetPath(guid);
            if (AssetImporter.GetAtPath(path) is not TextureImporter ti) continue;
            var android = ti.GetPlatformTextureSettings("Android");
            if (ti.isReadable) { Debug.LogError($"{path}: Read/Write enabled"); violations++; }
            if (!android.overridden) { Debug.LogError($"{path}: no Android override"); violations++; }
            if (path.Contains("/UI/") && ti.mipmapEnabled) { Debug.LogError($"{path}: UI mips on"); violations++; }
        }
        Debug.Log($"AssetAudit: {violations} violations");
        EditorApplication.Exit(violations == 0 ? 0 : 1);
    }
}
```

```bash
Unity -batchmode -nographics -projectPath . -executeMethod AssetAudit.Run -logFile -
```

## 5. Blender export validator

```python
# Run: blender -b scene.blend --python validate_export.py
import re
import sys
import bpy

NAME = re.compile(r"^(chr|npc|wpn|prp|env|vfx)_[a-z0-9]+(_[a-z0-9]+)*$")
TRI_BUDGET = {"prp": 1500, "env": 2000, "npc": 4000, "chr": 8000}   # from the art director's table

errors = []
for ob in bpy.context.scene.objects:
    if ob.type != "MESH":
        continue
    if not NAME.match(ob.name):
        errors.append(f"{ob.name}: name does not match convention")
    if any(abs(s - 1.0) > 1e-4 for s in ob.scale):
        errors.append(f"{ob.name}: unapplied scale {tuple(ob.scale)}")
    polys = ob.data.polygons
    if any(len(p.vertices) > 4 for p in polys):
        errors.append(f"{ob.name}: contains n-gons")
    tris = sum(len(p.vertices) - 2 for p in polys)
    cls = ob.name.split("_")[0]
    if cls in TRI_BUDGET and tris > TRI_BUDGET[cls]:
        errors.append(f"{ob.name}: {tris} tris over budget {TRI_BUDGET[cls]}")
    if len(ob.data.uv_layers) == 0:
        errors.append(f"{ob.name}: no UVs")

print("\n".join(errors) or "export validation passed")
sys.exit(1 if errors else 0)
```

## 6. What to validate, by stage

| Stage | Check | Tool |
|---|---|---|
| DCC export | Names, scale, n-gons, tri budget, UVs | Blender or Maya script, run on save or export |
| Engine import | Format, max size, sRGB, mips, Read/Write, bones | AssetPostprocessor |
| Build | Variant counts, total texture memory per bundle | IPreprocessShaders plus build report parsing |
| Scene | Draw calls, SetPass, particle caps, light counts | Editor script plus device capture for the record |
| Device | GPU ms per pass on the low tier | Captures in a nightly perf job |
