# Rollback, Lockstep, Serialization, Server Tick and Async Moves

Background: Fiedler on deterministic lockstep and snapshot interpolation (https://gafferongames.com/post/deterministic_lockstep/ , https://gafferongames.com/post/snapshot_interpolation), GGPO (MIT, open source since Oct 2019), GGRS (Rust).

## 1. Rollback loop skeleton (C++)

```cpp
struct Input   { uint16_t buttons; int8_t sx, sy; };
struct GameState;                                    // POD, fixed-point, no pointers
void     Simulate(GameState& s, const Input in[kMaxPlayers]);  // deterministic
uint32_t Checksum(const GameState& s);

class RollbackSession {
public:
    static constexpr int kMaxRollback = 8;           // frames (heuristic; GGPO-style default range)
    static constexpr int kInputDelay  = 2;           // frames of local input delay

    void AddLocalInput(int frame, const Input& in) { inputs_[slot(frame + kInputDelay)][local_] = in; confirmed_[slot(frame + kInputDelay)][local_] = true; }

    void OnRemoteInput(int player, int frame, const Input& in) {
        Input& predicted = inputs_[slot(frame)][player];
        bool mismatch = !confirmed_[slot(frame)][player] && memcmp(&predicted, &in, sizeof in) != 0;
        predicted = in; confirmed_[slot(frame)][player] = true;
        if (mismatch && frame < current_) rollbackTo_ = std::min(rollbackTo_, frame);
    }

    void AdvanceFrame() {
        if (rollbackTo_ < current_) {                 // re-simulate from the first wrong frame
            state_ = saved_[slot(rollbackTo_)];
            for (int f = rollbackTo_; f < current_; ++f) {
                saved_[slot(f)] = state_;
                PredictMissing(f);
                Simulate(state_, inputs_[slot(f)]);
            }
            rollbackTo_ = INT_MAX;
        }
        if (current_ - lastConfirmedFrame() >= kMaxRollback) return;   // stall: too far ahead
        saved_[slot(current_)] = state_;
        PredictMissing(current_);
        Simulate(state_, inputs_[slot(current_)]);
        ++current_;
    }

private:
    void PredictMissing(int f) {                      // repeat last known input
        for (int p = 0; p < kMaxPlayers; ++p)
            if (!confirmed_[slot(f)][p]) inputs_[slot(f)][p] = inputs_[slot(f - 1)][p];
    }
    static int slot(int f) { return (f + kRing) % kRing; }
    static constexpr int kRing = 64;
    GameState saved_[kRing]; Input inputs_[kRing][kMaxPlayers]; bool confirmed_[kRing][kMaxPlayers]{};
    GameState state_{}; int current_ = 0, local_ = 0, rollbackTo_ = INT_MAX;
    int lastConfirmedFrame() const;
};
```

Requirements:
- Save/restore must be cheap: keep `GameState` a flat POD block (a few KB to tens of KB). Worst case per frame = `kMaxRollback × Simulate()` + render, so `Simulate()` must fit in 1/(kMaxRollback+1) of the frame budget.
- Rendering, audio and VFX read state but never feed back into it. Spawn effects idempotently by (frame, event id) so a re-simulated frame does not double-play them.
- Exchange checksums for confirmed frames every N frames; on mismatch, dump both states and the input log for offline diff.
- Frame advantage: if one side runs ahead, the leader inserts brief waits (frame skips of 1) to rebalance.

## 2. Deterministic lockstep turn loop (C#)

```csharp
public sealed class LockstepRunner
{
    private const int TurnTicks = 4;          // e.g. 4 × 50 ms sim ticks = 200 ms turns (heuristic)
    private const int TurnDelay = 2;          // commands scheduled 2 turns ahead
    private readonly Dictionary<int, List<Command>[]> commandsByTurn = new();
    private int turn;

    public void IssueLocal(Command c) => Send(turn + TurnDelay, c);       // also stores locally

    public void Tick()
    {
        if (!HaveAllPlayersCommands(turn)) { StallUi(); return; }         // stall; never guess in lockstep
        foreach (var cmd in OrderedCommands(turn)) cmd.Apply(World);      // order by (player id, seq)
        for (int i = 0; i < TurnTicks; i++) World.Step(FixedDt);          // fixed-point
        if (turn % 10 == 0) SendChecksum(turn, World.Checksum());
        turn++;
    }
}
```

Players send an empty "no-op" command for every turn so others can advance. Adapt `TurnDelay` to measured RTT; drop and AI-replace a peer that stalls everyone for more than a few seconds.

Determinism rules (details with `gamedev-engine-architect`): fixed-point or integer math in the sim; no `Dictionary`/`HashSet` iteration order in logic; one seeded RNG living in game state; no wall-clock or frame-time inputs; identical sim code version on all peers (send a build hash in the handshake).

## 3. Bit writer and quantization (C#)

```csharp
public ref struct BitWriter
{
    private readonly Span<byte> buffer;
    private ulong scratch; private int scratchBits; private int bytePos;

    public BitWriter(Span<byte> buffer) { this.buffer = buffer; scratch = 0; scratchBits = 0; bytePos = 0; }

    public void Write(uint value, int bits)
    {
        scratch |= (ulong)(value & ((1u << bits) - 1)) << scratchBits;
        scratchBits += bits;
        while (scratchBits >= 8) { buffer[bytePos++] = (byte)scratch; scratch >>= 8; scratchBits -= 8; }
    }

    public int Flush() { if (scratchBits > 0) buffer[bytePos++] = (byte)scratch; scratchBits = 0; return bytePos; }
}

public static class Quant
{
    // Map [min,max] to an integer of `bits` bits.
    public static uint Encode(float v, float min, float max, int bits)
    {
        float t = Math.Clamp((v - min) / (max - min), 0f, 1f);
        return (uint)MathF.Round(t * ((1u << bits) - 1));
    }
    public static float Decode(uint q, float min, float max, int bits)
        => min + (max - min) * q / (float)((1u << bits) - 1);

    public static int BitsFor(float range, float precision) => (int)MathF.Ceiling(MathF.Log2(range / precision + 1));
}
```

Examples: `BitsFor(512f, 0.01f)` = 16 bits per axis; yaw at ~0.35° = 10 bits. Run the server simulation on dequantized values too, or client and server will disagree by the quantization error every tick.

## 4. Delta compression against an acked baseline

```
Server per client keeps: lastAckedSnapshotId, ring of sent snapshots (id → entity states)
Encode(snapshot S for client C):
  base = sent[C.lastAckedSnapshotId] or EMPTY (forces full)
  for each relevant entity e:
     if e not in base: write(1 bit new) + full quantized state
     elif state equal: write(1 bit unchanged)
     else: write changed-field mask + changed fields only
  for each entity in base not in S: write despawn
Client acks snapshot ids in every packet (ack + 32-bit ack bitfield).
If lastAcked older than ring size → send keyframe (full).
```

Interest management first, delta second: an entity outside the relevance set costs zero bits. A distance grid with per-entity priority accumulators (higher priority ⇒ sent more often) keeps packets under the MTU-safe ~1200 B.

## 5. Packet header

```
uint16 sequence        // wraps; compare with sequence-greater-than helper
uint16 ack             // latest received remote sequence
uint32 ackBits         // previous 32 received sequences
uint32 serverTick      // or clientTick for inputs
uint8  channel/flags
```

Reliable events ride on top: resend until acked, deliver in order per channel, bound the queue and drop the connection if it overflows rather than buffering minutes of events.

## 6. Server tick loop (Go)

```go
func (m *Match) Run(ctx context.Context) {
    const hz = 30
    tick := time.NewTicker(time.Second / hz)
    defer tick.Stop()
    for {
        select {
        case <-ctx.Done():
            return
        case <-tick.C:
            start := time.Now()
            m.drainInputs()                // non-blocking read of per-player queues
            m.simulate(1.0 / hz)           // fixed dt, never wall-clock delta
            m.recordHitboxes(m.tick)       // for lag compensation
            if m.tick%(hz/m.snapshotHz) == 0 {
                m.broadcastSnapshots()     // per-client delta vs acked baseline
            }
            m.tick++
            m.metrics.TickDuration.Observe(time.Since(start).Seconds())
        }
    }
}
```

`time.Ticker` drops ticks when the loop overruns rather than bursting; track overruns as a metric. Alert on tick-duration p99 above 50% of the budget (heuristic): above that, one GC pause or noisy neighbour turns into missed ticks. One goroutine per match, matches packed per core up to the measured CPU budget.

## 7. Async move endpoint (Go)

```go
type MoveReq struct {
    MatchID         string          `json:"match_id"`
    MoveID          string          `json:"move_id"`          // client UUID, idempotency key
    ExpectedVersion int64           `json:"expected_version"`
    Payload         json.RawMessage `json:"payload"`
}

func (s *Service) SubmitMove(ctx context.Context, playerID string, r MoveReq) (*MatchState, error) {
    if prior, ok, err := s.store.MoveResult(ctx, r.MatchID, r.MoveID); err != nil {
        return nil, err
    } else if ok {
        return prior, nil                                   // retry: return stored result
    }
    st, err := s.store.Load(ctx, r.MatchID)
    if err != nil { return nil, err }
    if st.Version != r.ExpectedVersion { return nil, ErrStaleVersion }  // client must refresh
    if st.CurrentPlayer != playerID { return nil, ErrNotYourTurn }
    next, err := rules.Apply(st, playerID, r.Payload)               // validates legality
    if err != nil { return nil, err }
    next.Version = st.Version + 1
    next.TurnDeadline = time.Now().Add(st.TurnTimeout)
    if err := s.store.SaveIfVersion(ctx, next, st.Version, r.MoveID); err != nil { return nil, err }  // CAS
    s.notify.TurnReady(ctx, next.CurrentPlayer, r.MatchID)          // push + socket; best effort
    return next, nil
}
```

A scheduled job enforces `TurnDeadline` (auto-move or forfeit). Push is a hint; the client always re-fetches state on open.

## 8. Desync triage checklist

- [ ] Same build hash on all peers
- [ ] Checksums logged per confirmed frame; first divergent frame identified
- [ ] State dumps diffed field by field at that frame
- [ ] Inputs for that frame identical on both sides
- [ ] Suspects: float math, transcendental functions, unordered containers, uninitialized memory, RNG called from render code, time-based logic, physics engine not in deterministic mode
