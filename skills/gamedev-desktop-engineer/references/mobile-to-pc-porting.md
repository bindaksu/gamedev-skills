# Porting a Mobile Game to PC and Mac

Use as the port plan template. Numbers marked heuristic are starting points, not platform rules.

## 1. Scope decision

| Question | Default answer |
| --- | --- |
| Same account and progress as mobile? | Yes; cross-progression through the studio backend |
| Same economy? | No; remove energy and ad gates, keep cosmetics and expansions, review prices |
| Cross-play with mobile? | Only if matchmaking can separate or balance input types (mouse aim vs touch) |
| Same content cadence? | Yes, same live-ops calendar; PC builds ship via SteamPipe on the same day |
| Separate SKU or same app? | Separate store SKUs; one codebase with platform targets |

## 2. Input

- Action map shared by touch, KB/M and gamepad; touch gestures become explicit actions (drag to pan becomes mouse drag, WASD, and right stick).
- Hover states for every interactive element (mobile has none).
- Right-click, scroll wheel, keyboard shortcuts for frequent actions; Esc always opens pause or backs out.
- Full rebinding for keyboard and gamepad; save bindings per device type.
- Glyphs switch to the last device used within one frame.
- Text entry: physical keyboard on desktop, Steam on-screen keyboard on Deck.

## 3. UI and layout

| Item | Mobile | Desktop target |
| --- | --- | --- |
| Hit target | 44 pt / 48 dp touch targets | Mouse precision allows denser layouts; keep gamepad focus targets clearly separated |
| Viewing distance | ~30 cm | 60 cm monitor, ~3 m TV, ~30 cm Deck at 1280x800 |
| Aspect | 19.5:9 portrait or landscape, safe areas | 16:9, 16:10, 21:9, 32:9; no notches except MacBook fullscreen |
| Density | One primary action per screen | More information per screen; side panels; tooltips |
| Text | Scales with OS settings | User UI-scale slider (heuristic: 75% to 150%) plus resolution scaling |
| Portrait games | Native | Pillarbox with art in the side bars, or a landscape relayout; decide early |

## 4. Performance targets

- Steam Machine Verified: native 1080p, stable 30 fps. Deck: 1280x800, stable frame pacing at default settings; most players expect a 30 or 40 fps cap option (heuristic).
- Desktop: uncapped or 60/120/144 options; simulation fixed-step and frame-rate independent.
- Mobile assets: raise texture resolution where UI and characters are viewed close up; keep ASTC sources and add BC formats for Windows and Apple silicon Macs.

## 5. Monetization and store rules

- Remove: energy timers, forced interstitials, rewarded video (no PC ad ecosystem worth the reviews).
- Keep: cosmetics, battle pass if it exists on mobile, expansions, a premium price option.
- Payment: Steam in-game purchases via Steam microtransactions; Epic and Microsoft have their own rules; Mac App Store uses Apple IAP. Verify each store's current policy.
- Purchases from mobile appearing on PC: entitlements live on the server; check each store's rules on content bought elsewhere (Apple's guideline 3.1.3(b) covers multiplatform services; verify current text).
- Randomized items: odds disclosure everywhere, same as mobile.
- Steam refunds are generally available within 14 days and under 2 hours played (verify); a weak first two hours shows up directly as refunds.

## 6. Platform services mapping

| Mobile | Steam | Epic | Mac App Store |
| --- | --- | --- | --- |
| Game Center / PGS achievements | Steam achievements | EOS achievements | Game Center |
| StoreKit 2 / Play Billing | Steam microtransactions | Epic payments (verify) | StoreKit 2 |
| Cloud save via backend | Backend (Steam Cloud for settings only) | Backend | Backend (iCloud optional) |
| Push notifications | none (use in-game inbox) | none | Local notifications only |
| Integrity: App Attest / Play Integrity | Server authority, PC anti-cheat | EOS Anti-Cheat | App Attest on Mac |

## 7. Port milestones

1. **Boot:** desktop target compiles; platform services interface stubbed; windowed 16:9.
2. **Input:** action map, KB/M and gamepad, glyphs, rebinding.
3. **Layout:** UI density pass at 16:9, 16:10, 21:9; Deck 1280x800 legibility.
4. **Services:** Steamworks achievements, auth ticket to backend, cross-progression linking.
5. **Economy:** PC monetization changes shipped behind config.
6. **Packaging:** signed Windows build, notarized Mac build, SteamPipe depots, beta branch.
7. **Verification:** Deck readiness sheet, Steam Machine 1080p/30 check, hardware matrix (NVIDIA, AMD, Intel; base M1).
8. **Launch:** store page assets, refund-window playtest of the first two hours, day-one patch plan.
