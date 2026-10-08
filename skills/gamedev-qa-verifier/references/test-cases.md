# Economy, IAP, Live-Ops and Network Test Cases

Read when testing purchases, refunds, currency, rewards, live-ops configs or network resilience. Every case records build, device, account and evidence.

## IAP (both stores)

| ID | Case | Steps | Expected |
|---|---|---|---|
| IAP-01 | Purchase each SKU | Buy in sandbox / license tester account | Charged once, granted once, receipt validated server-side |
| IAP-02 | Kill during purchase | Confirm payment, force-kill before grant UI | On relaunch, granted once; transaction finished/acknowledged after grant |
| IAP-03 | Network drop after payment | Disable network after confirming | Grant on reconnect; no duplicate |
| IAP-04 | Pending / Ask to Buy | Child account or Play pending payment method | No grant until approved; grant on approval |
| IAP-05 | Double tap | Tap buy twice rapidly | One purchase sheet; one grant |
| IAP-06 | Refund (iOS) | Process refund in sandbox; server receives refund notification | Policy applied: revoke, negative balance or flag |
| IAP-07 | Voided purchase (Android) | Refund via Play Console; poll voided purchases | Same policy applied |
| IAP-08 | Restore | Reinstall; restore | Non-consumables and subscriptions restored; consumables not duplicated |
| IAP-09 | Unacknowledged (Android) | Block acknowledgement in test build | Monitoring alerts; purchases are refunded after 3 days if not acknowledged |
| IAP-10 | Price display | Switch storefront country | Localized price from store, correct currency symbol |
| IAP-11 | Receipt replay | Resend a used receipt/token to server | Rejected; no grant |
| IAP-12 | Subscription lifecycle | Purchase, renew, lapse, grace period, resubscribe | Entitlement follows store state |

## Economy and rewards

| ID | Case | Expected |
|---|---|---|
| ECO-01 | Reward claim retried (same request id) | Granted once |
| ECO-02 | Claim from two devices simultaneously | Granted once |
| ECO-03 | Device clock forward/back | Timers, dailies and events use server time |
| ECO-04 | Currency at cap | Overflow handled per spec (blocked, mailed or lost with warning) |
| ECO-05 | Negative balance after refund | Spending blocked or handled per policy; no crash |
| ECO-06 | Randomized item odds | 10,000 simulated draws on test env match configured odds within statistical tolerance |
| ECO-07 | Pity counter | Guarantee triggers at stated count; counter persists across sessions and devices |
| ECO-08 | Offer eligibility | Offer appears only for target segment; purchase limit enforced server-side |
| ECO-09 | Rewarded ad | Reward granted only on completion callback; cap per day enforced server-side |

## Live-ops config

| ID | Case | Expected |
|---|---|---|
| LO-01 | Event start/end at boundary | Starts and ends at configured UTC time in all time zones |
| LO-02 | Config schema invalid | Rejected by validation before publish |
| LO-03 | Old client receives new config | Ignores unknown fields; no crash |
| LO-04 | Kill switch | Feature disabled within the stated propagation time; UI degrades gracefully |
| LO-05 | Event overlap | Two events sharing currency or UI slots behave per spec |
| LO-06 | Event ended while player in flow | Results and rewards delivered; no soft-lock |

## Network

| ID | Profile | Expected |
|---|---|---|
| NET-01 | 300 ms RTT | Playable per design; timeouts above RTT |
| NET-02 | 3–5% packet loss | No desync; retries succeed |
| NET-03 | Offline at boot | Clear message; offline mode if designed |
| NET-04 | Wi-Fi to cellular handover mid-session | Session continues or reconnects transparently |
| NET-05 | Server 5xx / throttled | Backoff with jitter; no retry storm; clear UX |
| NET-06 | Maintenance mode response | Maintenance screen with ETA; no data loss |

## Save and progress

| ID | Case | Expected |
|---|---|---|
| SAV-01 | Kill during save | No corruption; last good state restored |
| SAV-02 | Cross-device login | Server state wins per conflict rule; player warned if local progress discarded |
| SAV-03 | App update with save migration | Old save migrates; no progress loss |
| SAV-04 | Storage full | Graceful error; no corruption |
