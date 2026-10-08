---
name: gamedev-audio-designer
description: >-
  Game audio design and implementation, mobile-first: SFX and music direction, adaptive music, FMOD and
  Wwise versus engine audio, memory and voice budgets, compression formats and load types, mix buses and
  loudness targets in LUFS, latency, and iOS and Android audio session and interruption handling. Use when
  the user asks to plan or budget game audio, choose middleware or formats, design adaptive or layered
  music, fix audio that dies after a phone call, kills the player's own music, crackles, lags, or eats
  memory, or set loudness and mix standards.
license: MIT
metadata:
  pack: gamedev-studio
  version: "1.0.0"
  category: art-audio
---

# Game Audio Designer

Game audio is information first, emotion second, and a budget always. The fastest feedback channel a game has is a sound that lands within 50 ms of a tap; the most memorable is music that follows what the player is doing. Both live inside hard limits: a few dozen real voices, tens of megabytes of memory, a CPU slice on a phone that is already thermally throttling, and an operating system that owns the audio session and will interrupt you for calls, alarms, and the player's own playlist. On mobile a large share of play is muted, so audio must never be the only carrier of information, and when it is on, it must earn its place without annoying anyone sitting nearby.

## Role Profile

Audio and sound designers at large studios create SFX and implement them in middleware, manage Wwise project structure, gameplay parameters, and optimizations, and (Riot) "improve memory budgets, streaming look-ahead times, audio compression types" across platforms. On mobile they tune compression formats and sample rates.

- **Hard skills:** Wwise (more common in postings) or FMOD, Unity or Unreal, a DAW (Reaper or Pro Tools), Perforce, and C# or C++ scripting. Riot's senior technical sound designer needs 5+ years with 3+ technical and "exceptional Wwise"; EA Mobile asks for 3+ years with Unity, Wwise or FMOD, and Python or C#. Scripting appears in about half of postings.
- **Seniority signals:** owning the audio pipeline and repository setup, and cross-platform budgets.
- **Judged on:** audio memory and CPU within budget (near-quoted from postings), delivery against the content schedule, and bug counts on audio triggers (inferred).
- **Collaborators:** game and combat design, VFX and animation, engine engineers, external composers.
- Sources: https://hitmarker.net/jobs/riot-games-senior-technical-sound-designer-valorant-366196, https://hitmarker.net/jobs/electronic-arts-mobile-technical-sound-artist-362339, https://www.gamesoundcon.com/post/game-audio-job-skills-how-to-get-hired-as-a-game-sound-designer

## When to Use / Not

Use for: audio direction, SFX and music lists, middleware choice, budgets, formats and load types, voice management, mix and loudness, adaptive music, latency, and audio session behavior.

Not for:
- Timing of hit-stop, shake, and haptic patterns that accompany sounds: `gamedev-game-feel-designer`.
- VO script writing and line counts: `gamedev-script-writer`.
- Localized VO pipeline and per-language delivery: `gamedev-localization-specialist`.
- Captions, mono audio, and visual twins as accessibility features: `gamedev-accessibility-specialist`.
- Engine-level native audio plugins and 16 KB page alignment work: `gamedev-android-engineer`, `gamedev-ios-engineer`.
- The general interruption contract (save on background, pause on call): if installed, `mobile-game-ux-designer`. This skill owns the audio detail behind it.

## Inputs to Gather

- **Platforms and device tiers.** Default: iOS plus Android, low tier 3 GB RAM.
- **Engine and audio stack.** Engine built-in, FMOD, or Wwise. Default: Unity built-in for casual, middleware for mid-core and up.
- **Content volume.** SFX count, music minutes, VO lines times languages, ambience beds.
- **Session context.** Commute play with the player's own music, couch play with headphones, competitive play where audio cues matter.
- **Memory and download budget** from the optimization owner. Default: 25 MB resident audio, 60 MB on disk for casual.
- **Haptics plan**, since paired audio and haptics must be timed together.

## Method

1. **Write the audio direction and priority stack.** Critical gameplay feedback above UI, above VO, above music, above ambience. Priority decides what gets stolen when voices run out, so it is a design decision, not a technical one.
2. **Choose the stack.** Use the engine's built-in audio when you have under roughly 200 SFX, simple music, and no adaptive layers. Use FMOD or Wwise when you need adaptive music, a sound designer iterating without engineers, complex mixing, or many VO languages. Verify current middleware licensing tiers for your revenue band.
3. **Set budgets per tier:** resident memory, real voices, CPU on the audio thread, and download size (template below).
4. **Assign format and load type per class** (matrix below). This is where most mobile memory goes wrong.
5. **Design events, not files.** Every sound is an event with variations, randomization, a voice limit, a priority, a bus, and a cooldown.
6. **Build the mix bus tree and ducking rules.** Mix on a phone speaker, cheap earbuds, and good headphones, in that order of importance for mobile.
7. **Design adaptive music** as a state machine with transitions quantized to bars or beats.
8. **Implement session handling** for iOS categories, interruptions, and route changes, and Android audio focus. Default to letting the player's own music keep playing in casual games.
9. **Measure.** Tap-to-sound latency on the low tier, integrated loudness and true peak on a 10-minute capture, memory, and voice counts at peak moments.
10. **Run the interruption matrix** (call, alarm, Siri or Assistant, headphones unplugged, Bluetooth connect, background and foreground) on both platforms before every release.

## Deliverables

### 1. Audio Budget Sheet

```
AUDIO BUDGET — <game>                      low tier      mid tier      high tier
Resident memory (all banks loaded)          20 MB         35 MB         60 MB
Streaming buffers                           ≤ 2 streams   ≤ 3 streams   ≤ 4 streams
Real voices                                 16–24         32            48
Virtual voices                              128           256           512
Audio thread CPU (one core)                 ≤ 5%          ≤ 8%          ≤ 10%
Tap-to-sound latency (UI, gameplay)         ≤ 80 ms       ≤ 50 ms       ≤ 50 ms
Download size (base + packs)                base 25 MB, music and VO in on-demand packs
Values are working heuristics; replace with measured numbers from your low-tier device.
```

### 2. Format and Load-Type Matrix (Unity naming; middleware equivalents in brackets)

```
Class            Length     Channels  Rate     Format            Load type
UI clicks         < 0.3 s   mono      44.1–48k PCM or ADPCM     Decompress on load   (in memory, uncompressed)
Frequent SFX      < 2 s     mono      32–48k   ADPCM             Decompress on load
Occasional SFX    1–5 s     mono      32–48k   Vorbis q≈0.5      Compressed in memory
Long SFX, stingers 3–10 s   stereo    44.1–48k Vorbis            Compressed in memory
Ambience beds     loops     stereo    32–44.1k Vorbis            Streaming
Music             minutes   stereo    44.1–48k Vorbis or AAC     Streaming
VO                lines     mono      24–32k   Vorbis (or Opus in middleware)  Compressed in memory / streaming for long lines
Sources archived at 48 kHz 24-bit; conversion is a build step, never a manual export.
```

### 3. Sound Event Spec

```
EVENT: sfx_coin_collect           bus: SFX/Gameplay     priority: 60/100
Variations       5 (shuffle, no immediate repeat)
Randomization    pitch ±5% (about ±1 semitone), volume ±1.5 dB
Voice limit      4 instances; steal oldest; cooldown 40 ms between triggers
Rate-up rule     on chains: pitch step +1 semitone per coin, reset after 600 ms idle
Spatial          2D (UI-space reward)
Ducking          none
Visual twin      coin counter pulse (required; assume muted play)
Haptic pair      light impact on first coin of a chain only
```

### 4. Music System Spec

```
MUSIC: world_map + level        middleware parameter: intensity 0–1, state: map | level | boss | win | lose
Structure        horizontal segments (intro, A, B, bridge) at 96 BPM, 4/4
Vertical layers  L1 pads (always), L2 rhythm (intensity > 0.3), L3 lead (intensity > 0.7)
Layer fades      2 bars (5 s at 96 BPM)
Transitions      map → level: on next bar, 1-bar crossfade
                 level → win: stinger on next beat, music out over 1 beat
                 level → lose: stinger on next beat, then soft map loop
Loop lengths     map loop ≥ 2:30 with 3 alternates; it is the most-heard music in the game
Silence          level start has 2–4 s of no music by design; silence is a dynamic tool
```

### 5. Mix Bus Tree and Ducking

```
Master (limiter: ceiling −1 dBTP)
├─ Music        −6 dB under SFX reference at default slider
├─ SFX
│  ├─ Gameplay
│  └─ UI
├─ VO           ducks Music −8 dB (attack 80 ms, release 400 ms)
└─ Ambience     ducked −4 dB by big reward stingers
Player sliders: Master, Music, SFX, VO (persisted; default music 70%)
```

### 6. Interruption Test Matrix

```
Event                         iOS expected                          Android expected                Pass
Incoming call                 pause game + audio; resume on return  focus loss transient → pause
Alarm, timer                  same as call                          same
Siri / Assistant              duck or pause; resume after           duck or pause
Player's own music playing    game music muted, SFX on (casual)     game music not started
Headphones unplugged          pause music, no speaker blast         pause or duck music
Bluetooth connect mid-game    no restart; latency compensation off  same
Background → foreground       session reactivated; music resumes    focus re-requested
Media services reset (iOS)    engine rebuilt, no silent game        n/a
```

The platform session and focus code is in `references/platform-audio-session.md`. Read it when implementing or debugging interruptions.

## Technical Reference

### Memory math

PCM size = sample rate × bytes per sample × channels × seconds.
- 48 kHz, 16-bit, mono: 96,000 bytes per second, so a 0.8 s SFX is about 77 KB decompressed.
- 44.1 kHz, 16-bit, stereo: 176,400 bytes per second, so a 2:30 track is about 26.5 MB as PCM. Never decompress music on load.
- ADPCM is about 3.5:1 against 16-bit PCM with very cheap decode. It suits short, frequent SFX.
- Vorbis at medium quality is roughly 8–12:1 (heuristic), and costs CPU per playing voice when compressed in memory.
- Streaming holds only a small buffer per stream but costs I/O and a decoder per stream. Cap concurrent streams.

### Voices

- A *real* voice is mixed and decoded; a *virtual* voice is tracked but silent and costs almost nothing. Set real voices low and virtual voices generous, and let priority decide what is audible.
- Unity's project defaults are 32 real and 512 virtual voices. FMOD and Wwise set limits per platform in their project or init settings. Verify current defaults in your version.
- Every frequent event gets an instance limit (2–6) and a cooldown (30–50 ms). Ten identical coin sounds in one frame add phasing and clipping, not information.

### Latency

- Target tap-to-sound at or under 50 ms, matching the mobile feedback budget, and at or under 80 ms on the low tier.
- Smaller DSP buffers cut latency and raise CPU cost and crackle risk. Pick per platform and test on the low tier.
- On Android, low-latency output goes through AAudio, usually via Google's Oboe library (part of the Android Game Development Kit). Device output latency varies widely; measure it, do not assume it.
- Bluetooth output adds substantial latency (commonly 100 ms or more, heuristic). Rhythm and timing games need a calibration screen. iOS Game Mode lowers AirPods latency where it applies.
- Preload the first-use sounds of a scene during loading. A first-play disk read is a latency spike.

### Loudness

- Measure integrated loudness (LUFS, per ITU-R BS.1770) on a 10-minute representative gameplay capture, and true peak in dBTP.
- Sony's Audio Standards Working Group recommendation (ASWG-R001) is widely used as a reference: about −24 LUFS integrated for console and home play and about −18 LUFS for portable devices, each with a small tolerance. Verify the current revision.
- Mobile games in practice often mix hotter, around −16 to −14 LUFS, for phone speakers and noisy places (heuristic). Pick one target, document it, and hold every feature to it within ±2 LU.
- Hold true peak at or under −1 dBTP with a master limiter. Lossy encoding can push peaks over 0 dBFS after decode.

### iOS audio session (AVAudioSession)

| Category | Mixes with other apps | Silent switch | Use for |
|---|---|---|---|
| `.ambient` | yes | silences | Casual games where the player's music should keep playing |
| `.soloAmbient` (default) | no, stops other audio | silences | Games whose music is essential and that accept stopping the player's music |
| `.playback` | configurable | ignores | Only where audio is the game (rhythm, audio games) |

- `secondaryAudioShouldBeSilencedHint` is true when another app is playing audio. Mute game music, keep SFX.
- Handle `interruptionNotification` (began and ended, with the `shouldResume` option). Reactivate the session after an interruption ends, or the game stays silent.
- Handle `routeChangeNotification` with reason `oldDeviceUnavailable` (headphones removed). Pause or duck music so it does not blast from the speaker.
- Handle `mediaServicesWereResetNotification` by rebuilding the audio engine.
- Unity exposes a "Mute Other Audio Sources" player setting for iOS. Leave it off for casual games unless design requires exclusive audio.

### Android audio focus

- Request focus with `AudioFocusRequest` (API 26+), usage `USAGE_GAME`, when starting music. Abandon it when music stops.
- `AUDIOFOCUS_LOSS`: stop music and release focus. `AUDIOFOCUS_LOSS_TRANSIENT`: pause. Transient loss that permits ducking: the system ducks automatically on Android 8+ unless you opt to handle it yourself.
- If `AudioManager.isMusicActive` at launch, do not start game music (casual default). There is no silent switch; players expect game audio to follow media volume.
- Middleware ships prebuilt native libraries. Every prebuilt `.so`, audio middleware included, must be rebuilt for 16 KB page support; Play blocks updates without it from February 1, 2027.

## Diagnostics

| Symptom | Likely cause | Fix |
|---|---|---|
| Game silent after a phone call | Session not reactivated on interruption end | Reactivate on `.ended`; rebuild on media reset |
| Player's Spotify stops when the game opens | Default `.soloAmbient` or exclusive focus at launch | `.ambient` plus silence hint; skip music if other audio is active |
| Speaker blasts after headphones unplug | Route change not handled | Pause or duck music on `oldDeviceUnavailable` |
| Crackling on low-end Android | DSP buffer too small, or too many compressed-in-memory voices decoding | Larger buffer on low tier; ADPCM for frequent SFX; cut real voices |
| Tap sound feels late | Large buffer, first-use disk read, or Bluetooth | Preload; tune buffer; Oboe path; calibration for timing games |
| Memory spike entering a level | Long clips set to decompress on load | Matrix: stream music and ambience; compress long SFX in memory |
| Coin chains sound harsh and clip | No voice limit or cooldown | Instance limit 4, 40 ms cooldown, pitch rate-up |
| Repetition fatigue in reviews | One variation per frequent sound; short menu loop | 3–5 variations; map loop at least 2:30 with alternates |
| Features differ wildly in loudness | No loudness target | One LUFS target ±2 LU; measured per feature drop |
| Music restarts on every scene load | Music owned by a scene object | Persistent music system with state transitions |
| Audio middleware blocks Play upload | Prebuilt `.so` not 16 KB aligned | Update middleware to an aligned build; verify alignment |

## Anti-Patterns

**Decompress Everything.** Every clip set to decompress on load because it was the default. Music alone eats the memory budget.

**The Music Hijack.** The game stops the player's podcast or playlist at launch. It is the fastest way to get audio turned off forever.

**The Coin Machine Gun.** Unlimited instances of a frequent sound. Volume sums, phase cancels, and the limiter pumps.

**Studio-Monitor Mixing.** Mixed only on good speakers. On a phone speaker the bass-carried impacts vanish and the hi-hats dominate.

**One-Take Repetition.** A single variation for a sound heard 300 times a session.

**Audio-Only Information.** A threat or timer communicated only by sound, in a game most people play muted half the time.

**Silent Resume.** No interruption-ended handling. The game comes back from a call with no audio until restarted.

**Loudness War.** Each feature team pushes its sounds louder than the last. The mix ends at the limiter with no dynamics left.

## Worked Example: Casual Merge Game Audio Pass

Starting state: 180 SFX (average 0.8 s, mono, 48 kHz), 4 music tracks (2:30, stereo, 44.1 kHz), all set to decompress on load. Category `.soloAmbient`. Measured −11 LUFS integrated and +0.8 dBTP true peak.

**Memory.** SFX as PCM cost 180 × 77 KB ≈ 13.8 MB. Music as PCM costs 4 × 26.5 MB = 106 MB, which is the problem. Switch music to streaming Vorbis at about 128 kbps (16 KB per second, so about 2.4 MB per track on disk) with one active stream plus one for crossfades. Switch the 120 frequent SFX to ADPCM (about 3.5:1, so about 2.6 MB) and the 60 occasional ones to compressed-in-memory Vorbis (about 0.5 MB). Resident audio drops from about 120 MB to under 5 MB plus stream buffers.

**Session.** Change to `.ambient`. When `secondaryAudioShouldBeSilencedHint` is true, music is muted and SFX keep playing. On Android, skip game music when `isMusicActive` is true at launch. Track the share of sessions with master volume at zero before and after; the expected effect is that players with their own music keep SFX on instead of muting everything.

**Loudness.** The target is −16 LUFS and −1 dBTP. Pull the master down 5 dB, add a limiter at −1 dBTP, and re-measure: −16.2 LUFS, −1.0 dBTP.

**Voices.** Merge chains fired up to 14 simultaneous merge sounds. An instance limit of 4 with a 40 ms cooldown plus a pitch rate-up per chain step keeps the chain readable and removes the clipping.

## Quality Checklist

- [ ] Priority stack written; event priorities match it
- [ ] Budget sheet per tier: memory, real and virtual voices, CPU, latency, download
- [ ] Every asset class has a format, rate, channel count, and load type per the matrix; no music decompressed on load
- [ ] Frequent events have 3–5 variations, randomization, an instance limit, and a cooldown
- [ ] Mix bus tree with ducking rules; player sliders for master, music, SFX, VO
- [ ] One loudness target in LUFS with ±2 LU tolerance; true peak at or under −1 dBTP after encoding
- [ ] Mixed and checked on a phone speaker, cheap earbuds, and headphones
- [ ] Adaptive music transitions quantized to bars or beats; no restarts on scene load
- [ ] iOS category chosen deliberately; interruption, route change, silence hint, and media reset handled
- [ ] Android audio focus requested and released; other-music check at launch
- [ ] Tap-to-sound latency measured on the low tier device
- [ ] Interruption matrix passed on both platforms before release
- [ ] Every gameplay-relevant sound has a visual twin
- [ ] Middleware native libraries verified for 16 KB page alignment on Android

## Related Skills

- `gamedev-game-feel-designer` owns the timing relationship between sound, hit-stop, shake, and haptics.
- `mobile-game-ux-designer` (if installed) owns the interruption contract and sound-off design rules.
- `gamedev-accessibility-specialist` owns captions, mono audio, and visual twins as accessibility features.
- `gamedev-localization-specialist` owns localized VO delivery and language packs.
- `gamedev-script-writer` writes VO scripts and barks to the line budgets set here.
- `gamedev-optimization-compatibility` sets the device tiers and total memory budget audio fits inside.
- `gamedev-unity-engineer`, `gamedev-ios-engineer`, and `gamedev-android-engineer` implement middleware integration and session code.
- `gamedev-qa-verifier` runs the interruption matrix in regression.
- `gamedev-delivery-release` ships music and VO as downloadable packs.
