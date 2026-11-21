# Prediction, Reconciliation, Interpolation and Lag Compensation (C#)

Engine-agnostic C# shapes. They assume a fixed simulation step shared by client and server (`TickDt`), integer tick numbers, and a deterministic-enough movement function run identically on both sides. Canonical background: https://gabrielgambetta.com/client-side-prediction-server-reconciliation.html and https://gabrielgambetta.com/entity-interpolation.html

## 1. Input and state ring buffers

```csharp
public struct InputCmd
{
    public uint Tick;
    public sbyte MoveX, MoveY;     // quantized stick, -127..127
    public ushort AimYaw;          // 0..65535 => 0..360 deg
    public byte Buttons;           // bit flags
}

public struct PlayerState
{
    public uint Tick;
    public Vector2 Position;
    public Vector2 Velocity;
}

public sealed class Ring<T> where T : struct
{
    private readonly T[] items;
    private readonly uint[] ticks;
    public Ring(int capacity) { items = new T[capacity]; ticks = new uint[capacity]; }

    public void Put(uint tick, in T value)
    {
        int i = (int)(tick % (uint)items.Length);
        items[i] = value; ticks[i] = tick;
    }

    public bool TryGet(uint tick, out T value)
    {
        int i = (int)(tick % (uint)items.Length);
        value = items[i];
        return ticks[i] == tick;
    }
}
```

Capacity: enough ticks to cover max RTT plus jitter. At 30 Hz and a 1 s ceiling, 32 slots; use 64 for safety. Ring buffers avoid per-tick allocation.

## 2. Client prediction loop

```csharp
public sealed class PredictedPlayer
{
    private const int Size = 64;
    private readonly Ring<InputCmd> inputs = new(Size);
    private readonly Ring<PlayerState> predicted = new(Size);
    private PlayerState current;
    private uint tick;

    public Vector2 RenderPosition { get; private set; }
    private Vector2 visualError;                       // smoothed correction offset

    public InputCmd SampleAndPredict(InputCmd raw)
    {
        raw.Tick = ++tick;
        inputs.Put(tick, raw);
        current = Movement.Step(current, raw, Net.TickDt);   // shared with server
        current.Tick = tick;
        predicted.Put(tick, current);
        return raw;                                    // caller sends last N inputs redundantly
    }

    public void OnServerState(in PlayerState authoritative)
    {
        if (!predicted.TryGet(authoritative.Tick, out var mine)) return;   // too old
        if ((mine.Position - authoritative.Position).sqrMagnitude < Net.EpsilonSq) return;

        // Mismatch: rewind to server truth, replay unacknowledged inputs.
        Vector2 before = current.Position;
        var s = authoritative;
        for (uint t = authoritative.Tick + 1; t <= tick; t++)
        {
            if (inputs.TryGet(t, out var cmd)) s = Movement.Step(s, cmd, Net.TickDt);
            s.Tick = t;
            predicted.Put(t, s);
        }
        current = s;

        Vector2 jump = before - current.Position;
        if (jump.magnitude > Net.SnapDistance) visualError = Vector2.zero;   // teleport: snap
        else visualError += jump;                                           // hide small error
    }

    public void Render(float frameDt)
    {
        // Exponential decay of the visual error over ~100–200 ms (heuristic).
        visualError *= MathF.Exp(-frameDt / 0.1f);
        RenderPosition = current.Position + visualError;
    }
}
```

Rules:
- The simulation state snaps; only the rendered position is smoothed.
- Count corrections per minute in telemetry. A healthy game corrects rarely on good networks; frequent corrections at low RTT indicate client/server code divergence, not latency.
- Inputs travel in every packet as the last 3–8 commands so one lost packet loses nothing.

## 3. Server side: input queue per player

```csharp
public sealed class ServerPlayer
{
    private readonly SortedList<uint, InputCmd> pending = new();
    private InputCmd lastApplied;
    public PlayerState State;

    public void Receive(ReadOnlySpan<InputCmd> redundantInputs)
    {
        foreach (var cmd in redundantInputs)
            if (cmd.Tick > lastApplied.Tick && !pending.ContainsKey(cmd.Tick))
                pending.Add(cmd.Tick, Validate(cmd));
    }

    public void Simulate(uint serverTick)
    {
        // Consume exactly one input per tick; repeat the last one if missing (packet loss).
        InputCmd cmd = lastApplied;
        if (pending.Count > 0 && pending.Keys[0] <= serverTick)
        {
            cmd = pending.Values[0];
            pending.RemoveAt(0);
        }
        State = Movement.Step(State, cmd, Net.TickDt);
        State.Tick = cmd.Tick;            // ack the client's tick, not the server's
        lastApplied = cmd;
    }

    private static InputCmd Validate(InputCmd c)
    {
        c.MoveX = (sbyte)Math.Clamp((int)c.MoveX, -127, 127);
        c.MoveY = (sbyte)Math.Clamp((int)c.MoveY, -127, 127);
        return c;                          // never trust magnitudes, rates or positions from clients
    }
}
```

Keep the per-player input buffer at 1–2 ticks of slack. Overwatch-style time dilation: if the buffer runs dry, tell the client to simulate slightly faster (e.g., 1–2%) until it refills; if it grows, slightly slower.

## 4. Snapshot interpolation buffer for remote entities

```csharp
public struct Snapshot { public double ServerTime; public Vector2 Pos; public float Yaw; }

public sealed class InterpolationBuffer
{
    private readonly Snapshot[] buf = new Snapshot[32];
    private int count;

    public void Add(in Snapshot s)
    {
        if (count > 0 && s.ServerTime <= buf[count - 1].ServerTime) return;  // drop out-of-order
        if (count == buf.Length) { Array.Copy(buf, 1, buf, 0, count - 1); count--; }
        buf[count++] = s;
    }

    public bool Sample(double renderTime, double maxExtrapolation, out Snapshot result)
    {
        result = default;
        if (count == 0) return false;
        for (int i = count - 1; i > 0; i--)
        {
            ref var a = ref buf[i - 1]; ref var b = ref buf[i];
            if (a.ServerTime <= renderTime && renderTime <= b.ServerTime)
            {
                float t = (float)((renderTime - a.ServerTime) / (b.ServerTime - a.ServerTime));
                result = new Snapshot {
                    ServerTime = renderTime,
                    Pos = Vector2.Lerp(a.Pos, b.Pos, t),
                    Yaw = LerpAngle(a.Yaw, b.Yaw, t) };
                return true;
            }
        }
        // Underrun: extrapolate briefly from the last two, then hold.
        var last = buf[count - 1];
        double over = renderTime - last.ServerTime;
        if (count >= 2 && over > 0 && over <= maxExtrapolation)
        {
            var prev = buf[count - 2];
            var vel = (last.Pos - prev.Pos) / (float)(last.ServerTime - prev.ServerTime);
            result = last; result.Pos = last.Pos + vel * (float)over;
            return true;
        }
        result = last;
        return true;
    }

    private static float LerpAngle(float a, float b, float t)
    {
        float d = ((b - a + 540f) % 360f) - 180f;
        return a + d * t;
    }
}
```

Render time on the client: `renderTime = estimatedServerTime − interpDelay`, where `estimatedServerTime` comes from a smoothed clock sync (server time stamps in each snapshot, RTT/2 offset, filtered). Never use the client's wall clock directly.

Adaptive delay: `interpDelay = clamp(2 × snapshotInterval + 2 × jitterP95, 2 × snapshotInterval, 250 ms)`. Change it slowly (a few ms per second) to avoid visible time warps.

## 5. Lag compensation: server-side rewind

```csharp
public sealed class HitboxHistory
{
    private struct Frame { public uint Tick; public Bounds[] Boxes; }
    private readonly Frame[] frames;
    public HitboxHistory(int ticks, int players)
    {
        frames = new Frame[ticks];
        for (int i = 0; i < ticks; i++) frames[i].Boxes = new Bounds[players];
    }

    public void Record(uint tick, ReadOnlySpan<Bounds> boxes)
    {
        ref var f = ref frames[tick % (uint)frames.Length];
        f.Tick = tick;
        boxes.CopyTo(f.Boxes);
    }

    public bool TryGet(uint tick, out Bounds[] boxes)
    {
        ref var f = ref frames[tick % (uint)frames.Length];
        boxes = f.Boxes;
        return f.Tick == tick;
    }
}

public static class LagCompensation
{
    // clientViewTick = tick the shooter was rendering remote players at (sent with the shot).
    public static uint RewindTick(uint serverTick, uint clientViewTick, uint maxRewindTicks)
    {
        uint earliest = serverTick > maxRewindTicks ? serverTick - maxRewindTicks : 0;
        return Math.Max(clientViewTick, earliest);      // cap protects targets from extreme ping
    }
}
```

Flow: client sends the shot with the interpolated server tick it was viewing (including interp delay). Server validates it is not in the future and not older than the cap, rewinds hitboxes to that tick, raycasts, applies damage at the current tick. Log `(shooterRtt, rewindTicks, hit)` for disputed kills; the peeker's-advantage window is a product of RTT, interp delay and tick rate, which is why Valorant pushed all three down (https://technology.riotgames.com/node/112).

Cap guidance (heuristic): 200–250 ms of rewind. Beyond it, the shooter must lead the target; the shot is evaluated at the capped tick.

## 6. Clock sync sketch

```csharp
public sealed class ServerClock
{
    private double offset;          // serverTime - localTime
    private bool initialized;

    public void OnPong(double clientSendLocal, double serverTime, double clientRecvLocal)
    {
        double rtt = clientRecvLocal - clientSendLocal;
        double sample = serverTime + rtt / 2 - clientRecvLocal;
        offset = initialized ? offset + (sample - offset) * 0.1 : sample;   // EMA; discard samples with rtt > p90
        initialized = true;
    }

    public double Now(double localTime) => localTime + offset;
}
```

Reject samples whose RTT exceeds the recent p90; asymmetric routes on cellular make the RTT/2 assumption worst on spikes.
