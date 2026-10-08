# Content Delivery and Config Rollout Details

Read when designing the content pipeline or a remote-config rollout.

## CDN layout

```
cdn.example.com/content/
  catalogs/
    android/catalog_v1042.json        # versioned, immutable once published
    ios/catalog_v1042.json
    android/current.json               # tiny pointer, short TTL (~60 s), or signed
  bundles/
    android/9f2c1e...a7.bundle         # content-hash names, immutable
    ios/41be0d...c3.bundle
```

Headers:
- Bundles: `Cache-Control: public, max-age=31536000, immutable`
- Versioned catalogs: same as bundles
- Pointer (`current.json`): `Cache-Control: public, max-age=60` (or sign it and include a version and expiry)

Publish order: upload bundles, verify availability in every region, upload versioned catalog, then flip the pointer. Rollback: flip the pointer back.

## Catalog pointer schema

```json
{
  "catalog_version": 1042,
  "catalog_url": "catalogs/android/catalog_v1042.json",
  "min_client_build": 4100,
  "fallback_catalog_version": 1038,
  "published_at": "2026-10-08T09:00:00Z",
  "signature": "base64..."
}
```

Client rule: if its build is below `min_client_build`, use `fallback_catalog_version`; if download fails, keep the last verified catalog and show content already cached.

## Client update flow (Unity Addressables)

```csharp
// Run at boot before gameplay loads; UpdateCatalogs blocks other Addressables requests while running
IEnumerator UpdateContent()
{
    var check = Addressables.CheckForCatalogUpdates(false);
    yield return check;
    if (check.Status == AsyncOperationStatus.Succeeded && check.Result.Count > 0)
    {
        var update = Addressables.UpdateCatalogs(check.Result, false);
        yield return update;
        Addressables.Release(update);
    }
    Addressables.Release(check);

    var size = Addressables.GetDownloadSizeAsync("event_current");
    yield return size;
    if (size.Result > 0) { /* show download prompt with size; respect cellular settings */ }
    Addressables.Release(size);
}
```

The remote catalog must be enabled in the shipped player build, or updates cannot be detected (as of 2026-10; verify against Addressables 2.x docs).

## Platform-hosted alternatives (as of 2026-10; verify)

| Path | Limits | Notes |
|---|---|---|
| Apple-hosted Background Assets | up to 200 GB compressed asset packs per app | Essential, prefetch and on-demand policies; packs updatable without a new binary; replaces On-Demand Resources |
| Play Asset Delivery | asset pack 1.5 GB each; install-time 4 GB; on-demand + fast-follow 4 GB (30 GB Level Up / XR); 100 packs | Fast-follow/on-demand may be moved or deleted by the OS; query location every time |
| Own CDN (Addressables / custom) | your cost | Full control of versioning and rollback |

## Remote config

Config document example:

```json
{
  "config_version": 87,
  "min_client_build": 4000,
  "features": {
    "guild_war": { "enabled": true, "rollout_percent": 10, "kill": false },
    "starter_pack_v3": { "enabled": false }
  },
  "events": [
    { "id": "halloween_2026", "start": "2026-10-24T10:00:00Z", "end": "2026-11-03T10:00:00Z", "start_jitter_min": 10 }
  ]
}
```

Rules:
- Schema-validate in CI and at publish; reject unknown keys for target client builds.
- Bucket players deterministically: `hash(player_id + feature_key) % 100 < rollout_percent`, so a player stays in or out across sessions.
- Stage: internal, 1%, 10%, 50%, 100%; check guardrails between steps (crash-free sessions, login success, purchase success, feature metric); hold each step long enough to see a full daily cycle for anything touching retention or revenue.
- Server-side guard as well: the server refuses actions for a killed feature even if a stale client tries.
- Keep config history; one-click revert to the previous version.

## Burn-rate alert example (Prometheus rule)

```yaml
groups:
  - name: login-slo
    rules:
      - alert: LoginSLOFastBurn
        expr: |
          (
            sum(rate(login_attempts_total{result!="success"}[1h]))
            / sum(rate(login_attempts_total[1h]))
          ) > (14.4 * 0.001)
          and
          (
            sum(rate(login_attempts_total{result!="success"}[5m]))
            / sum(rate(login_attempts_total[5m]))
          ) > (14.4 * 0.001)
        for: 2m
        labels: { severity: page }
        annotations:
          summary: "Login error rate burning the 99.9% SLO budget fast"
```

A 14.4x burn rate over 1 h consumes about 2% of a 30-day budget; pair it with a slower window (for example 6x over 6 h) for ticket-level alerts [standard multiwindow burn-rate pattern; tune to your SLO window].
