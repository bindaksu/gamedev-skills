# Steamworks Snippets

Steamworks SDK C++ API. Names are long-standing, but the SDK changes yearly (for example `SteamAPI_InitEx` arrived in 1.58, and recent SDKs fetch user stats automatically where older ones needed `RequestCurrentStats`); verify against the SDK version you ship. Authoritative docs: Steamworks partner documentation.

## 1. Steam Input with action sets

Define actions in the In-Game Actions (IGA) VDF file shipped with the game and configured on the partner site. Code then reads actions, never physical buttons.

```cpp
struct SteamActions {
    InputActionSetHandle_t gameplay = 0, menu = 0;
    InputDigitalActionHandle_t jump = 0, pause = 0;
    InputAnalogActionHandle_t move = 0, camera = 0;

    void resolve() {                                  // after SteamInput()->Init
        auto* in = SteamInput();
        gameplay = in->GetActionSetHandle("Gameplay");
        menu     = in->GetActionSetHandle("Menu");
        jump     = in->GetDigitalActionHandle("jump");
        pause    = in->GetDigitalActionHandle("pause");
        move     = in->GetAnalogActionHandle("move");
        camera   = in->GetAnalogActionHandle("camera");
    }
};

void pollSteamInput(const SteamActions& a, bool inMenu, PlayerInput& out) {
    InputHandle_t pads[STEAM_INPUT_MAX_COUNT];
    int n = SteamInput()->GetConnectedControllers(pads);  // after RunFrame this tick
    for (int i = 0; i < n; ++i) {
        SteamInput()->ActivateActionSet(pads[i], inMenu ? a.menu : a.gameplay);
        auto mv = SteamInput()->GetAnalogActionData(pads[i], a.move);
        out.moveX += mv.x; out.moveY += mv.y;
        out.jump  |= SteamInput()->GetDigitalActionData(pads[i], a.jump).bState;
        out.pause |= SteamInput()->GetDigitalActionData(pads[i], a.pause).bState;
    }
}
```

Glyphs: `GetDigitalActionOrigins` returns the physical origins bound to an action; `GetGlyphPNGForActionOrigin` (or the SVG variant) returns the image path. Show glyphs for the last device that produced input.

## 2. Stats and achievements

```cpp
class SteamStats {
public:
    void addWins(int delta) {
        int32 wins = 0;
        SteamUserStats()->GetStat("wins", &wins);
        SteamUserStats()->SetStat("wins", wins + delta);
        dirty_ = true;
        if (wins + delta >= 100) SteamUserStats()->SetAchievement("ACH_WIN_100");
    }
    void flushIfDirty() {                 // at level end / menu, not every frame
        if (dirty_) { SteamUserStats()->StoreStats(); dirty_ = false; }
    }
private:
    bool dirty_ = false;
    STEAM_CALLBACK(SteamStats, onStored, UserStatsStored_t);   // check m_eResult
};
```

Achievement-with-progress stats are defined on the partner site; `IndicateAchievementProgress` shows a progress toast.

## 3. Steam Cloud

Prefer **Steam Auto-Cloud** (configured on the partner site: root path, file pattern, quotas) for simple per-user saves; no code needed. Use the API only when you need explicit control:

```cpp
bool cloudWrite(const char* name, const std::vector<uint8_t>& bytes) {
    return SteamRemoteStorage()->FileWrite(name, bytes.data(), static_cast<int32>(bytes.size()));
}
std::optional<std::vector<uint8_t>> cloudRead(const char* name) {
    if (!SteamRemoteStorage()->FileExists(name)) return std::nullopt;
    std::vector<uint8_t> buf(SteamRemoteStorage()->GetFileSize(name));
    SteamRemoteStorage()->FileRead(name, buf.data(), static_cast<int32>(buf.size()));
    return buf;
}
```

If the game has cross-platform progress on your backend, do not also put that save in Steam Cloud. Use Steam Cloud only for local settings.

## 4. On-screen keyboard on Deck

```cpp
void requestText(int x, int y, int w, int h) {
    if (SteamUtils()->IsSteamRunningOnSteamDeck() || SteamUtils()->IsSteamInBigPictureMode()) {
        SteamUtils()->ShowFloatingGamepadTextInput(
            k_EFloatingGamepadTextInputModeModeSingleLine, x, y, w, h);  // text arrives as key events
    }
}
```

`ShowGamepadTextInput` is the older full-screen variant that returns text via `GamepadTextInputDismissed_t`.

## 5. Backend identity: Web API auth ticket

```cpp
// Client: request a ticket for a named web service identity, send it to your server.
class SteamAuth {
public:
    void requestWebTicket() { SteamUser()->GetAuthTicketForWebApi("studio-backend"); }
private:
    STEAM_CALLBACK(SteamAuth, onWebTicket, GetTicketForWebApiResponse_t);
};

void SteamAuth::onWebTicket(GetTicketForWebApiResponse_t* r) {
    if (r->m_eResult != k_EResultOK) return;
    // r->m_rgubTicket[0 .. r->m_cubTicket) -> hex encode -> POST /auth/steam { ticket }
}
```

Server: call `ISteamUserAuth/AuthenticateUserTicket` with your publisher Web API key, the app ID, the hex ticket, and the same identity string. The response carries the verified SteamID. Never accept a raw SteamID from the client.

## 6. Microtransactions (server side, verify current policy)

In-game purchases in Steam builds go through Steam's microtransaction Web API (`ISteamMicroTxn`: InitTxn, then the overlay authorization callback `MicroTxnAuthorizationResponse_t` on the client, then FinalizeTxn from the server). The server grants only after FinalizeTxn succeeds, with idempotency on the order ID. Check current Steamworks policy on third-party payment before designing anything else.

## 7. SteamPipe build script

```
"AppBuild"
{
    "AppID" "480"                       // your app ID
    "Desc" "build 1.4.2 (git abc123)"
    "BuildOutput" "../output/"
    "SetLive" ""                        // never auto-live; promote from the partner site
    "Depots"
    {
        "481"                           // Windows depot
        {
            "FileMapping" { "LocalPath" "../build/win64/*" "DepotPath" "." "recursive" "1" }
            "FileExclusion" "*.pdb"
        }
        "482"                           // macOS depot (notarized bundle)
        {
            "FileMapping" { "LocalPath" "../build/mac/*" "DepotPath" "." "recursive" "1" }
        }
    }
}
```

Upload: `steamcmd +login <builder_account> +run_app_build ../scripts/app_build.vdf +quit`. Use a dedicated builder account with limited permissions; keep PDBs and dSYMs in your symbol store, not in depots.
