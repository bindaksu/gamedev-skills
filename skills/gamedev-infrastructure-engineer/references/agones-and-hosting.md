# Agones Fleets, Autoscaling, Allocation, and Hosting Portability

Read when writing Fleet, FleetAutoscaler, or GameServerAllocation manifests, or when moving a fleet between hosts. Targets Agones v1.61 (as of 2026-10; verify against https://github.com/googleforgames/agones/releases — v1.61 moved the Helm chart to Helm v4, which is a breaking install change).

## Game server lifecycle (SDK contract)

```
Scheduled -> RequestReady -> Ready -> Allocated -> (match runs) -> Shutdown
                 ^ server calls SDK.Ready() after loading map/assets
                                      ^ allocator flips Ready -> Allocated
                                                     ^ server calls SDK.Shutdown() when the match ends
Health: server calls SDK.Health() every few seconds; missed pings -> Unhealthy -> replaced.
Since v1.61 a GameServer is marked Unhealthy when the game container exits.
```

Rules: never call `Ready()` before the server can accept players; always call `Shutdown()` after the match (servers are single-use unless you implement re-allocation with Counters/Lists); write match results to the backend *before* `Shutdown()`.

## Fleet

```yaml
apiVersion: agones.dev/v1
kind: Fleet
metadata:
  name: arena-euw1
spec:
  replicas: 50                      # FleetAutoscaler overrides this
  scheduling: Packed                # bin-pack to let Cluster Autoscaler remove empty nodes
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 25%           # only Ready servers are replaced; Allocated ones finish their match
  template:
    metadata:
      labels:
        mode: arena
        build: "1.42.0"
    spec:
      ports:
        - name: default
          portPolicy: Dynamic       # host port from the Agones range (default 7000-8000)
          containerPort: 7777
          protocol: UDP
      health:
        initialDelaySeconds: 10
        periodSeconds: 5
        failureThreshold: 3
      template:
        spec:
          terminationGracePeriodSeconds: 900   # >= longest match
          nodeSelector:
            role: gameserver
          tolerations:
            - key: role
              operator: Equal
              value: gameserver
              effect: NoSchedule
          containers:
            - name: arena
              image: europe-docker.pkg.dev/acme/game/arena:1.42.0
              resources:                       # requests == limits -> Guaranteed QoS, no CPU throttling surprises
                requests: { cpu: "1000m", memory: "1Gi" }
                limits:   { cpu: "1000m", memory: "1Gi" }
```

Blue/green builds: run two Fleets (`arena-euw1-1-42`, `arena-euw1-1-43`), allocate by `build` label matching the client's protocol, scale the old one to 0 when its clients age out. This is how a server build serves the client compatibility window.

## FleetAutoscaler

```yaml
apiVersion: autoscaling.agones.dev/v1
kind: FleetAutoscaler
metadata:
  name: arena-euw1
spec:
  fleetName: arena-euw1
  policy:
    type: Buffer
    buffer:
      bufferSize: 20%               # Ready servers kept as a fraction of total; or an absolute integer
      minReplicas: 40               # raise before scheduled events
      maxReplicas: 3000
  sync:
    type: FixedInterval
    fixedInterval:
      seconds: 30
```

Sizing the buffer:

```
allocs_per_min_peak  = match_starts_per_min at event peak
node_lead_min        = time from scale-up to Ready game server on a new node (measure: often 2–5 min)
server_boot_min      = container start to SDK.Ready()
buffer_needed        = allocs_per_min_peak × (node_lead_min + server_boot_min) × 1.2
```

Other policy types: `Webhook` (your service returns desired replicas — useful for schedule-aware scaling or forecasts), and Counter/List-based policies for servers that host multiple sessions. Recent Agones releases also added Schedule and Chain policies for time-window scaling; confirm their feature stage in your version's release notes before relying on them. Without them, run a CronJob that patches `minReplicas` 30–60 minutes before an event.

## Allocation

```yaml
apiVersion: allocation.agones.dev/v1
kind: GameServerAllocation
spec:
  selectors:
    - matchLabels:
        agones.dev/fleet: arena-euw1-1-42
  scheduling: Packed
  metadata:
    labels:
      match-id: "m-7f3a"            # stamped on the GameServer for traceability
    annotations:
      players: "p1,p2,p3,p4"
```

Front the allocator with your own service (matchmaker → allocation service → Agones allocator gRPC/REST with mTLS, or a cross-cluster allocation policy). The game backend talks to your interface, not to Agones directly — that interface is what you re-implement on GameLift Servers or an edge provider if you move.

Return to the client: address, port, and a short-lived signed join token that the game server validates. Never hand out addresses without a token.

## Node pools and networking (GKE)

- Separate pools: `agones-system` (controllers; label `agones.dev/agones-system=true`, taint `agones.dev/agones-system=true:NoExecute`), `gameserver` (label + taint `role=gameserver`), `default` (APIs).
- Game server nodes need public IPs or a UDP proxy; open the Agones port range (UDP 7000-8000 by default) with a firewall rule scoped to the game server node tag.
- Disable or schedule node auto-upgrade and maintenance windows outside peak hours; set PodDisruptionBudgets for Allocated servers (Agones sets a safe-to-evict annotation behavior — verify your `eviction` setting on the GameServer spec).
- Spot/preemptible: buffer only. Allocated matches on Spot will be killed with short notice.

## GameLift Servers containers (AWS alternative)

- Managed containers GA 2024-11-13, running on ECS; Anywhere fleets register your own or other-cloud hardware; FlexMatch for matchmaking; FleetIQ for Spot game servers. https://aws.amazon.com/about-aws/whats-new/2024/11/amazon-gamelift-containers-dev-iteration-management
- Portability rule: keep one OCI image; abstract the lifecycle calls (`ready`, `health`, `shutdown`, `allocate`) behind a thin interface in the server so the Agones SDK and the GameLift Server SDK are two adapters.

## Migration checklist (host A -> host B)

- [ ] Server image runs on both with adapter switch (env var), tested in CI
- [ ] Allocator interface implemented for B; matchmaker points to the interface
- [ ] Per-region capacity on B load-tested at event peak
- [ ] Dual-run: route a percentage of matches per region to B; compare tick p99, crash rate, allocation latency
- [ ] Join-token validation identical on both
- [ ] Cutover per region; keep A at minReplicas for one week as rollback
