# Device Matrix Construction

Read when building or refreshing the test device matrix.

## Inputs

- Install share by device model, OS version and country (Play Console device catalog and Android vitals; App Store Connect analytics; your own analytics).
- Revenue share by device (payers skew to newer devices; crashes on payer devices cost more).
- Device tiers and budgets from gamedev-optimization-compatibility.
- Crash and ANR clusters by device from the crash reporter (Crashlytics, Sentry, Backtrace/Sauce Error Reporting).

## Coverage dimensions

| Dimension | Buckets | Why it matters |
|---|---|---|
| GPU family | Apple GPU generations; Qualcomm Adreno; Arm Mali; Imagination PowerVR; Samsung Xclipse | Driver bugs, shader compile differences, precision, texture format support |
| RAM | 2–3 GB, 4 GB, 6–8 GB, 12 GB+ | OOM kills, texture budgets, background eviction |
| OS version | Floor version, most common, newest, newest beta | API behavior, permissions, billing, page size |
| Screen shape | 16:9, tall (19.5–21:9), notch, punch-hole, tablet 4:3, foldable inner/outer | Safe areas, HUD layout, aspect handling |
| SoC class | Low, mid, flagship per year | Thermal throttling, frame pacing |
| Memory pages | 4 KB and 16 KB (Android 15+ 64-bit) | Native libraries not aligned crash on load; enforcement for updates from Feb 1, 2027 (as of 2026-10; verify) |
| Region-specific | Top local OEMs in each target geo | Market-specific skins, battery killers, CJK fonts |

## Procedure

1. Sort device models by install share in target geos; take the top until cumulative share reaches 70–80% [heuristic]. That set is the P0 candidate pool.
2. Collapse near-duplicates (same SoC, RAM, OS) to one representative.
3. Check each coverage dimension; add the cheapest device that fills each empty bucket.
4. Add mandatory devices: declared min-spec, oldest supported iPhone/iPad, most common low-RAM Android in top geo, newest flagship (for new GPU drivers), a foldable if your share shows them, a 16 KB-page device or emulator image.
5. Assign tiers: P0 (8–12 physical devices, every build); P1 (20–30, every client release); P2 (100+ in a cloud device farm for launch, install, crash-on-boot and screenshot diff).
6. Refresh quarterly and after each major OS release. Retire devices below 0.5% share unless they are min-spec.

## Matrix sheet

```
| Tier | Device | SoC / GPU family | RAM | OS | Screen | Install share | Revenue share | Why included | Owner/location |
|------|--------|------------------|-----|----|--------|---------------|---------------|--------------|----------------|
| P0   | ...    | ... / Mali       | 4GB | 14 | 20:9   | 3.1%          | 1.2%          | top low-RAM  | lab shelf A    |
```

## Desktop / Steam additions

- Steam Deck (LCD and OLED) for Deck Verified: 1280x800 legibility, controller-first defaults, no launcher issues (as of 2026-10; verify).
- Steam Machine Verified (if targeted): native 1080p at a stable 30 fps, full controller support, good defaults; Deck Verified titles auto-qualify, not the reverse (as of 2026-10; verify).
- Windows GPU vendors (NVIDIA, AMD, Intel) at low/mid; macOS Apple Silicon base model.
