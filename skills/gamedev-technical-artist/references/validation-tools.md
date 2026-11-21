# Asset Validation Tools

Read this when building the import pipeline or CI checks. Snippets target Unity 6 with URP and Blender 5.2 LTS (as of 2026-11; verify); verify API names against your exact versions before relying on them.

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

## 5b. Generated-mesh checks (image-to-3D output)

Generated meshes fail in ways the export validator above does not see: they arrive facing the wrong way, at arbitrary sizes, with dense topology and missing rig groups. Run this before rigging and again before engine import. Tested headless on Blender 5.2 LTS.

```python
# Run: blender -b --python check_generated.py -- asset.glb chr
# Checks a generated mesh before it is rigged or imported. Exit 1 on any error.
import math
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

SCALE_TABLE_M = {"chr": (1.6, 2.0), "npc": (1.4, 2.2), "prp": (0.2, 1.5), "env": (0.5, 6.0)}  # project table
TRIS_BEFORE_RIG = {"chr": 30000, "npc": 15000, "prp": 3000, "env": 5000}                     # decimate to this first
RIG_GROUPS = ("thumb", "index", "middle", "ring", "pinky", "twist")                          # must exist and carry weight
FORWARD = Vector((0.0, -1.0, 0.0))   # project facing axis in Blender space (front view looks along +Y)
SCREEN_H_PX, FOV_V_DEG, CAM_DIST_M = 1080, 60.0, 5.5                                         # closest game camera


def face_forward(obj, degrees_about_z):
    """Rotate by matrix. glTF import uses QUATERNION mode, so edits to rotation_euler do nothing."""
    obj.matrix_world = Matrix.Rotation(math.radians(degrees_about_z), 4, "Z") @ obj.matrix_world


def world_bbox(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


def uv_area(poly, uv_layer):
    uvs = [uv_layer.data[i].uv for i in poly.loop_indices]
    return abs(sum(uvs[i].x * uvs[i - 1].y - uvs[i - 1].x * uvs[i].y for i in range(len(uvs)))) / 2.0


def texel_density(obj):
    """Mean texels per metre: sqrt(uv_area * W * H / world_area). None if no UVs or image."""
    images = [n.image for s in obj.material_slots if s.material and s.material.node_tree
              for n in s.material.node_tree.nodes if n.type == "TEX_IMAGE" and n.image]
    if not obj.data.uv_layers.active or not images:
        return None
    w, h = images[0].size
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.transform(obj.matrix_world)
    world_area = sum(f.calc_area() for f in bm.faces)
    bm.free()
    uv_total = sum(uv_area(p, obj.data.uv_layers.active) for p in obj.data.polygons)
    return math.sqrt(uv_total * w * h / world_area) if world_area else None


args = sys.argv[sys.argv.index("--") + 1:]
path, cls = args[0], args[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=path)
errors = []
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
arms = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"]

lo, hi = world_bbox(meshes)
height = hi.z - lo.z
lo_ok, hi_ok = SCALE_TABLE_M[cls]
if not lo_ok <= height <= hi_ok:
    errors.append(f"height {height:.2f} m outside {cls} table {lo_ok}-{hi_ok} m: rescale from the table, never auto-size")

for arm in arms:
    # Joint positions survive glTF import; imported bone tails are guessed, so use ankle -> toe heads.
    toes = [b for b in arm.data.bones if "toe" in b.name.lower() and b.parent]
    if not toes:
        errors.append(f"{arm.name}: no toe bone with a parent, facing cannot be asserted")
    for b in toes:
        d = arm.matrix_world.to_3x3() @ (b.head_local - b.parent.head_local)
        d.z = 0.0
        if d.length == 0 or d.normalized().dot(FORWARD) < 0.7:
            errors.append(f"{b.name}: toe points {tuple(round(c, 2) for c in d)}, not forward; fix with face_forward()")

for ob in meshes:
    tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    rigged = any(m.type == "ARMATURE" for m in ob.modifiers)
    if tris > TRIS_BEFORE_RIG[cls]:
        errors.append(f"{ob.name}: {tris} tris; decimate to {TRIS_BEFORE_RIG[cls]} before rigging"
                      + (" (already rigged on the dense source: redo the rig)" if rigged else ""))
    if rigged:
        weighted = {g.group for v in ob.data.vertices for g in v.groups if g.weight > 0.01}
        names = {vg.index: vg.name.lower() for vg in ob.vertex_groups}
        for key in RIG_GROUPS:
            hits = [i for i, n in names.items() if key in n]
            if not hits:
                errors.append(f"{ob.name}: no '{key}' vertex group")
            elif not any(i in weighted for i in hits):
                errors.append(f"{ob.name}: '{key}' groups exist but carry no weight")
    td = texel_density(ob)
    need = SCREEN_H_PX / (2 * CAM_DIST_M * math.tan(math.radians(FOV_V_DEG) / 2))
    if td is not None and td < need:
        errors.append(f"{ob.name}: {td:.0f} px/m texel density, game camera needs {need:.0f}")

print("\n".join(errors) or "generated-mesh checks passed")
sys.exit(1 if errors else 0)
```

Why each check exists:
- **Rotation mode.** glTF import sets objects to quaternion rotation, so an Euler fix silently does nothing. Rotate by matrix and assert the toe direction; joint positions survive import, guessed bone tails do not.
- **Scale table.** Auto-size gives kit pieces arbitrary heights. Rescale against the project's real-height table and reject anything outside it.
- **Finger and twist groups.** List them and require weight; unweighted twist bones are invisible until the forearm candy-wraps in engine.
- **Decimate before rigging.** A rig built on the dense source must be redone after decimation.
- **Texel density at the game camera.** Needed density = `screen_height_px / (2 × distance × tan(fov_v / 2))`. At 1080p, 60° vertical FOV and 5.5 m that is about 170 px/m; generated pieces often land well below the density the camera needs. Set the camera numbers from the real closest game camera, not from the DCC viewport.

## 6. What to validate, by stage

| Stage | Check | Tool |
|---|---|---|
| DCC export | Names, scale, n-gons, tri budget, UVs | Blender or Maya script, run on save or export |
| Generated mesh | Rotation by matrix plus toe direction, height vs scale table, finger and twist groups weighted, triangles before rig, texel density at the game camera | Blender script §5b |
| Engine import | Format, max size, sRGB, mips, Read/Write, bones | AssetPostprocessor |
| Flipbook from generated video | Brightness approved in the engine's blend and colour space, whole-cycle loop, no lens flares or elements leaving frame | Engine preview, side by side with the source |
| Build | Variant counts, total texture memory per bundle | IPreprocessShaders plus build report parsing |
| Scene | Draw calls, SetPass, particle caps, light counts | Editor script plus device capture for the record |
| Device | GPU ms per pass on the low tier | Captures in a nightly perf job |
