# Data-Driven Config, Save Systems and Scripting Layers

## 1. Config pipeline

```
Spreadsheet / editor tool
   │  export (CI job or editor button)
   ▼
Validator ── schema (JSON Schema / protobuf / FlatBuffers) + cross-reference checks
   │           (every item_id referenced exists; drop tables sum to 1.0; no reused IDs)
   ▼
Typed binary or JSON config, versioned: config_v{schema}_{contentHash}
   │
   ├─ bundled in binary (fallback, first session)
   └─ remote (live-ops overrides; signed; fetched non-blocking)
```

Rules:
- IDs are stable strings or integers assigned once. Removing an item reserves its ID forever.
- Validation errors fail the export, not the game session.
- The client loads bundled config synchronously, then applies a remote override when it arrives; never block boot on the fetch.
- Every config file carries `schema_version`; the client rejects configs newer than it understands and keeps the last good one.

### Example schema fragment (JSON Schema)

```json
{
  "$id": "weapon.schema.json",
  "type": "object",
  "required": ["id", "damage", "cooldown_ms"],
  "properties": {
    "id":          { "type": "string", "pattern": "^wpn_[a-z0-9_]+$" },
    "damage":      { "type": "integer", "minimum": 1, "maximum": 100000 },
    "cooldown_ms": { "type": "integer", "minimum": 16 },
    "tags":        { "type": "array", "items": { "type": "string" }, "uniqueItems": true }
  },
  "additionalProperties": false
}
```

Integers in milliseconds and basis points avoid float parsing differences — important when the config feeds a deterministic sim.

### Hot reload in editor / dev builds

```csharp
public sealed class ConfigStore
{
    private ImmutableConfig current;
    public event Action<ImmutableConfig> Changed;

    public ImmutableConfig Current => current;

    public void Replace(ImmutableConfig next)
    {
        var errors = ConfigValidator.Validate(next);
        if (errors.Count > 0) { Log.Error(string.Join("\n", errors)); return; }   // keep last good
        current = next;                                                          // swap whole object
        Changed?.Invoke(next);
    }
}
```

Consumers read `Current` each time or subscribe to `Changed`; they never cache individual values across frames unless they also subscribe.

## 2. Save envelope and migration chain

```csharp
public static class SaveCodec
{
    private const uint Magic = 0x56415347; // "GSAV" little-endian
    public const ushort CurrentVersion = 4;

    public static byte[] Encode(SaveDataV4 data)
    {
        byte[] payload = Serializer.Serialize(data);            // protobuf/MessagePack/etc.
        using var ms = new MemoryStream();
        using var w = new BinaryWriter(ms);
        w.Write(Magic);
        w.Write(CurrentVersion);
        w.Write(payload.Length);
        w.Write(Crc32.Compute(payload));
        w.Write(payload);
        return ms.ToArray();
    }

    public static SaveDataV4 Decode(byte[] bytes)
    {
        using var r = new BinaryReader(new MemoryStream(bytes));
        if (r.ReadUInt32() != Magic) throw new CorruptSaveException("magic");
        ushort version = r.ReadUInt16();
        int len = r.ReadInt32();
        uint crc = r.ReadUInt32();
        byte[] payload = r.ReadBytes(len);
        if (Crc32.Compute(payload) != crc) throw new CorruptSaveException("crc");
        if (version > CurrentVersion) throw new SaveFromFutureException(version);  // downgrade: keep file, refuse load
        return Migrate(version, payload);
    }

    private static SaveDataV4 Migrate(ushort version, byte[] payload) => version switch
    {
        1 => V3ToV4(V2ToV3(V1ToV2(Serializer.Deserialize<SaveDataV1>(payload)))),
        2 => V3ToV4(V2ToV3(Serializer.Deserialize<SaveDataV2>(payload))),
        3 => V3ToV4(Serializer.Deserialize<SaveDataV3>(payload)),
        4 => Serializer.Deserialize<SaveDataV4>(payload),
        _ => throw new CorruptSaveException($"unknown version {version}")
    };

    // Each migration is pure: old object in, new object out, no IO, no globals.
    private static SaveDataV2 V1ToV2(SaveDataV1 s) => new SaveDataV2(s.Coins, s.Level, Settings.Default);
    private static SaveDataV3 V2ToV3(SaveDataV2 s) => new SaveDataV3(s.Coins, s.Level, s.Settings, tutorialDone: s.Level > 3);
    private static SaveDataV4 V3ToV4(SaveDataV3 s) => new SaveDataV4(s.Level, s.Settings, s.TutorialDone); // coins moved server-side
}
```

Keep every `SaveDataVn` type and migration forever (or until telemetry shows zero loads of that version for 12+ months). A player returning after two years must still load.

## 3. Atomic write with backup

```csharp
public static void WriteAtomic(string path, byte[] bytes)
{
    string tmp = path + ".tmp";
    string bak = path + ".bak";
    using (var fs = new FileStream(tmp, FileMode.Create, FileAccess.Write, FileShare.None))
    {
        fs.Write(bytes, 0, bytes.Length);
        fs.Flush(flushToDisk: true);                 // fsync
    }
    if (File.Exists(path)) File.Replace(tmp, path, bak);   // atomic swap + backup
    else File.Move(tmp, path);
}
```

Load order: primary → `.bak` → fresh state plus a server restore prompt. Report every fallback to telemetry; a rising `.bak` load rate means writes are being interrupted (often app kill during save on background).

Save on: background/pause notifications, level end, after purchases are confirmed by the server. Do not save every frame; coalesce to at most one write per few seconds.

## 4. Device vs server ownership

| Data | Owner | Merge rule |
|---|---|---|
| Hard currency, purchases, inventory with real value | Server | Server wins; client is a cache |
| Progress that gates monetisation (levels, unlocks) | Server or signed client | Max / union with server validation |
| Settings, audio, control layout | Device | Last-writer-wins with timestamp |
| Tutorial flags, seen-popups | Device, synced | Union (once seen, stays seen) |
| Cosmetic loadout | Either | Last-writer-wins |

Whole-blob last-writer-wins is the classic cloud-save data-loss bug: a stale device overwrites newer progress. Merge per field.

## 5. Golden-file tests

```
tests/saves/
  v1_fresh.sav   v1_midgame.sav   v1_maxed.sav
  v2_...         v3_...           v4_...
test: for each file → Decode → assert invariants (level ≥ 1, no negative counts) → Encode → Decode → equal
```

Add a golden file for every shipped version on release day, captured from a real device.

## 6. Embedding Lua (C++ with sol2)

```cpp
#include <sol/sol.hpp>

class ScriptHost {
public:
    ScriptHost() {
        lua_.open_libraries(sol::lib::base, sol::lib::math, sol::lib::table, sol::lib::string);
        // No io, os, package, debug: designers get a sandbox, not a shell.
        lua_.new_usertype<EntityHandle>("Entity",
            "damage", &EntityHandle::damage,
            "position", &EntityHandle::position);
        lua_["log"] = [](const std::string& s) { LOG_INFO("[lua] %s", s.c_str()); };
        lua_gc(lua_.lua_state(), LUA_GCGEN, 0, 0);      // Lua 5.4 generational mode
    }

    void load(const std::string& chunk_name, const std::string& code) {
        auto result = lua_.safe_script(code, sol::script_pass_on_error, chunk_name);
        if (!result.valid()) { sol::error e = result; LOG_ERROR("%s", e.what()); }
    }

    void tick(double budget_ms) {
        Stopwatch sw;
        for (auto& fn : on_tick_) {
            auto r = fn();
            if (!r.valid()) { sol::error e = r; LOG_ERROR("%s", e.what()); }
            if (sw.ms() > budget_ms) { metrics_.script_over_budget++; break; }
        }
        lua_gc(lua_.lua_state(), LUA_GCSTEP, 0);         // small incremental step each frame
    }

private:
    sol::state lua_;
    std::vector<sol::protected_function> on_tick_;
    Metrics metrics_;
};
```

Rules:
- Scripts call a narrow, versioned API; they never hold raw pointers (use handles with generation counters).
- Budget per frame (heuristic: 1–2 ms on the floor device) with a counter when exceeded.
- Scripts in a deterministic sim must use the sim's RNG streams and fixed-point types exposed through the API, never `math.random`.
- LuaJIT's JIT cannot run on iOS; plan for interpreter speed there.

## 7. Handles over pointers

```cpp
struct Handle { uint32_t index; uint32_t generation; };

template <typename T>
class Pool {
public:
    T* get(Handle h) {
        if (h.index >= slots_.size()) return nullptr;
        Slot& s = slots_[h.index];
        return (s.generation == h.generation && s.alive) ? &s.value : nullptr;
    }
private:
    struct Slot { T value; uint32_t generation = 0; bool alive = false; };
    std::vector<Slot> slots_;
};
```

Handles survive serialization, script boundaries and entity deletion (stale handles resolve to null instead of dangling).
