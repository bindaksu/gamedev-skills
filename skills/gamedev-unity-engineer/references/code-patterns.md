# Unity Code Patterns (C#)

Short, compile-shaped snippets for the architecture decisions in SKILL.md. Adapt names; keep the shapes.

## 1. Assembly definition for pure-logic Core

```json
{
  "name": "Game.Core",
  "rootNamespace": "Game.Core",
  "references": [],
  "noEngineReferences": true,
  "allowUnsafeCode": false,
  "autoReferenced": false
}
```

`noEngineReferences` means Core compiles without UnityEngine: it is unit-testable in EditMode in milliseconds and cannot accidentally depend on scenes or MonoBehaviours. `autoReferenced: false` stops the default `Assembly-CSharp` from reaching into it implicitly.

## 2. Composition root with constructor injection

```csharp
// Game.Runtime/Boot/CompositionRoot.cs
public sealed class CompositionRoot : MonoBehaviour
{
    [SerializeField] private GameConfig config;      // authored ScriptableObject
    [SerializeField] private HudView hudView;

    private IGameServices services;

    private void Awake()
    {
        DontDestroyOnLoad(gameObject);
        var clock    = new UnityClock();
        var save     = new FileSaveStore(Application.persistentDataPath);
        var remote   = new RemoteConfigService(config.RemoteDefaults);
        var economy  = new EconomyService(remote, save);
        var haptics  = PlatformFactory.CreateHaptics();   // EditorStub / iOS / Android
        services = new GameServices(clock, save, remote, economy, haptics);
        hudView.Bind(new HudPresenter(economy));
    }
}
```

Rules: constructors take interfaces, never `FindObjectOfType`. MonoBehaviours receive dependencies through a `Bind`/`Construct` method called by the root or a factory. A container (VContainer, Extenject) is fine when the graph exceeds ~30 services; the rule (one root, no ambient statics) is what matters.

## 3. Resetting statics when domain reload is off

```csharp
public static class AnalyticsQueue
{
    private static readonly List<AnalyticsEvent> Pending = new(64);

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
    private static void ResetStatics() => Pending.Clear();
}
```

Fast Enter Play Mode skips domain reload, so statics carry values between play sessions. Every static that holds state needs this hook.

## 4. Read-only ScriptableObject config

```csharp
[CreateAssetMenu(menuName = "Game/Weapon Config")]
public sealed class WeaponConfig : ScriptableObject
{
    [SerializeField, Min(0f)] private float damage = 10f;
    [SerializeField, Min(0.01f)] private float cooldownSeconds = 0.5f;

    public float Damage => damage;
    public float CooldownSeconds => cooldownSeconds;

    // Runtime state lives elsewhere:
    public WeaponState CreateState() => new WeaponState(this);
}

public sealed class WeaponState
{
    public WeaponState(WeaponConfig config) { Config = config; }
    public WeaponConfig Config { get; }
    public float CooldownRemaining { get; private set; }
    public void Tick(float dt) => CooldownRemaining = Mathf.Max(0f, CooldownRemaining - dt);
}
```

Getters only, no public setters. Validation in `OnValidate` for cross-field rules. Live-tuned values come from remote config and override defaults at load, never by mutating the asset.

## 5. Pooling with UnityEngine.Pool

```csharp
public sealed class ProjectileSpawner : MonoBehaviour
{
    [SerializeField] private Projectile prefab;
    private ObjectPool<Projectile> pool;

    private void Awake()
    {
        pool = new ObjectPool<Projectile>(
            createFunc: () => Instantiate(prefab),
            actionOnGet: p => p.gameObject.SetActive(true),
            actionOnRelease: p => p.gameObject.SetActive(false),
            actionOnDestroy: p => Destroy(p.gameObject),
            collectionCheck: false,          // true in development builds only
            defaultCapacity: 64,
            maxSize: 256);
        Prewarm(64);
    }

    private void Prewarm(int count)
    {
        var tmp = new List<Projectile>(count);
        for (int i = 0; i < count; i++) tmp.Add(pool.Get());
        foreach (var p in tmp) pool.Release(p);
    }

    public Projectile Spawn(Vector3 pos, Quaternion rot)
    {
        var p = pool.Get();
        p.transform.SetPositionAndRotation(pos, rot);
        p.Init(pool);                         // projectile releases itself on hit/timeout
        return p;
    }
}
```

Prewarm behind the loading screen; size `maxSize` from the measured p99 concurrent count.

## 6. Non-allocating physics query

```csharp
private readonly RaycastHit[] hits = new RaycastHit[16];

private int ScanTargets(Vector3 origin, Vector3 dir, float range, int mask)
{
    int count = Physics.RaycastNonAlloc(origin, dir, hits, range, mask, QueryTriggerInteraction.Ignore);
    // hits[0..count) valid; order is not guaranteed — sort by distance if needed
    return count;
}
```

## 7. Burst job: schedule early, complete late

```csharp
[BurstCompile]
public struct SteerJob : IJobParallelFor
{
    [ReadOnly] public NativeArray<float3> Targets;
    public NativeArray<float3> Positions;
    public float Speed;
    public float DeltaTime;

    public void Execute(int i)
    {
        float3 to = Targets[i] - Positions[i];
        float len = math.length(to);
        if (len > 1e-4f)
            Positions[i] += to / len * math.min(Speed * DeltaTime, len);
    }
}

public sealed class CrowdSystem : MonoBehaviour
{
    private NativeArray<float3> positions, targets;
    private JobHandle handle;

    private void Update()
    {
        var job = new SteerJob { Targets = targets, Positions = positions, Speed = 3f, DeltaTime = Time.deltaTime };
        handle = job.Schedule(positions.Length, 64);   // batch 32–128 for cheap per-item work
    }

    private void LateUpdate()
    {
        handle.Complete();                             // as late as possible
        // copy positions into transforms (or use IJobParallelForTransform)
    }

    private void OnDestroy()
    {
        handle.Complete();
        if (positions.IsCreated) positions.Dispose();
        if (targets.IsCreated) targets.Dispose();
    }
}
```

Allocator choice: `Temp` (one frame, inside a job or method), `TempJob` (up to 4 frames, passed to jobs), `Persistent` (long-lived, dispose explicitly). Leak detection in the editor reports undisposed `Persistent` arrays.

## 8. Field telemetry with ProfilerRecorder

```csharp
public sealed class FrameStatsSampler : MonoBehaviour
{
    private ProfilerRecorder mainThread, gcAlloc, totalUsed;
    private readonly float[] frameMs = new float[600];
    private int index;

    private void OnEnable()
    {
        mainThread = ProfilerRecorder.StartNew(ProfilerCategory.Internal, "Main Thread", 15);
        gcAlloc    = ProfilerRecorder.StartNew(ProfilerCategory.Memory, "GC Allocated In Frame");
        totalUsed  = ProfilerRecorder.StartNew(ProfilerCategory.Memory, "Total Used Memory");
    }

    private void OnDisable() { mainThread.Dispose(); gcAlloc.Dispose(); totalUsed.Dispose(); }

    private void Update()
    {
        frameMs[index++ % frameMs.Length] = Time.unscaledDeltaTime * 1000f;
        // Every N seconds: compute p50/p90/p99 off-thread and send with device model, tier, scene state.
    }
}
```

These counters work in release builds, so the same sampler feeds the per-device percentiles in the performance report.

## 9. Custom ProfilerMarker for hot code

```csharp
private static readonly ProfilerMarker PathfindMarker = new("Game.Pathfind");

public void Pathfind()
{
    using (PathfindMarker.Auto())
    {
        // work
    }
}
```

Markers show in the Profiler timeline and Profile Analyzer and cost almost nothing when not recording. Whether they also appear in native traces (Perfetto, Instruments) depends on the platform profiler integration in your Unity version — verify before relying on it.
