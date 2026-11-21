# Platform Audio Session and Focus Code

Read this when implementing or debugging audio interruptions, the player's own music, headphone changes, or Android audio focus. Engines and middleware wrap some of this; native plugins or engine callbacks still need to implement the behavior. Verify API details against current SDK docs.

## 1. iOS: AVAudioSession wrapper

```swift
import AVFoundation

final class GameAudioSession {
    private let session = AVAudioSession.sharedInstance()
    private var observersInstalled = false

    // Hooks into the engine or middleware
    var pauseAudio: () -> Void = {}
    var resumeAudio: () -> Void = {}
    var setMusicMuted: (Bool) -> Void = { _ in }
    var rebuildEngine: () -> Void = {}

    func configure() throws {
        // .ambient: mixes with the player's music, respects the silent switch
        try session.setCategory(.ambient, mode: .default, options: [])
        try session.setActive(true)
        setMusicMuted(session.secondaryAudioShouldBeSilencedHint)
        installObserversOnce()
    }

    private func installObserversOnce() {
        guard !observersInstalled else { return }
        observersInstalled = true
        let nc = NotificationCenter.default
        nc.addObserver(self, selector: #selector(onInterruption(_:)),
                       name: AVAudioSession.interruptionNotification, object: session)
        nc.addObserver(self, selector: #selector(onSilenceHint(_:)),
                       name: AVAudioSession.silenceSecondaryAudioHintNotification, object: session)
        nc.addObserver(self, selector: #selector(onRouteChange(_:)),
                       name: AVAudioSession.routeChangeNotification, object: session)
        nc.addObserver(self, selector: #selector(onMediaReset(_:)),
                       name: AVAudioSession.mediaServicesWereResetNotification, object: session)
    }

    @objc private func onInterruption(_ n: Notification) {
        guard let raw = n.userInfo?[AVAudioSessionInterruptionTypeKey] as? UInt,
              let type = AVAudioSession.InterruptionType(rawValue: raw) else { return }
        switch type {
        case .began:
            pauseAudio()                       // gameplay pause is handled by the app lifecycle
        case .ended:
            try? session.setActive(true)       // without this the game stays silent
            let optRaw = n.userInfo?[AVAudioSessionInterruptionOptionKey] as? UInt ?? 0
            if AVAudioSession.InterruptionOptions(rawValue: optRaw).contains(.shouldResume) {
                resumeAudio()                  // audio resumes; gameplay stays paused until the player taps
            }
        @unknown default:
            break
        }
    }

    @objc private func onSilenceHint(_ n: Notification) {
        guard let raw = n.userInfo?[AVAudioSessionSilenceSecondaryAudioHintTypeKey] as? UInt,
              let type = AVAudioSession.SilenceSecondaryAudioHintType(rawValue: raw) else { return }
        setMusicMuted(type == .begin)          // other app started or stopped playing
    }

    @objc private func onRouteChange(_ n: Notification) {
        guard let raw = n.userInfo?[AVAudioSessionRouteChangeReasonKey] as? UInt,
              AVAudioSession.RouteChangeReason(rawValue: raw) == .oldDeviceUnavailable else { return }
        pauseAudio()                           // headphones removed: never blast the speaker
    }

    @objc private func onMediaReset(_ n: Notification) {
        rebuildEngine()                        // all audio objects are invalid after a reset
        try? configure()
    }
}
```

Category decision rule: start with `.ambient`. Move to `.soloAmbient` only if design decides the game's music is essential and accepts stopping the player's audio. Use `.playback` only for games where audio is the game, and still expose a mute.

## 2. Android: audio focus

```kotlin
import android.content.Context
import android.media.AudioAttributes
import android.media.AudioFocusRequest
import android.media.AudioManager

class GameAudioFocus(context: Context, private val audio: GameAudio) {
    private val am = context.getSystemService(AudioManager::class.java)

    private val attributes = AudioAttributes.Builder()
        .setUsage(AudioAttributes.USAGE_GAME)
        .setContentType(AudioAttributes.CONTENT_TYPE_MUSIC)
        .build()

    // On Android 8+ the system ducks automatically for transient "can duck" losses
    // unless you call setWillPauseWhenDucked(true) and handle it yourself.
    private val request = AudioFocusRequest.Builder(AudioManager.AUDIOFOCUS_GAIN)
        .setAudioAttributes(attributes)
        .setOnAudioFocusChangeListener { change ->
            when (change) {
                AudioManager.AUDIOFOCUS_LOSS -> { audio.stopMusic(); release() }
                AudioManager.AUDIOFOCUS_LOSS_TRANSIENT -> audio.pauseAll()
                AudioManager.AUDIOFOCUS_GAIN -> audio.resumeAll()
            }
        }
        .build()

    fun startMusicIfAppropriate() {
        if (am.isMusicActive) {           // the player's own music wins in casual games
            audio.muteMusic()
            return
        }
        if (am.requestAudioFocus(request) == AudioManager.AUDIOFOCUS_REQUEST_GRANTED) {
            audio.playMusic()
        }
    }

    fun release() {
        am.abandonAudioFocusRequest(request)
    }
}

interface GameAudio {
    fun playMusic(); fun stopMusic(); fun muteMusic()
    fun pauseAll(); fun resumeAll()
}
```

Headphone removal on Android arrives as the `AudioManager.ACTION_AUDIO_BECOMING_NOISY` broadcast. Register a receiver while audio plays and pause or duck music on it.

## 3. Low-latency output on Android

- Use AAudio through Oboe for custom native audio paths; middleware and engines usually have their own low-latency settings, so check those first.
- Request the device's native sample rate and burst size; mismatches force resampling and add latency.
- Use a performance mode of low latency for gameplay SFX streams, and a power-saving mode for long music streams if your engine separates them.
- Measure round-trip or tap-to-sound latency on each low-tier test device and keep a table; device variance is large.

## 4. Release-blocking interruption checks (both platforms)

1. Incoming call during gameplay, decline, return: audio resumes, gameplay paused.
2. Incoming call, accept, talk 30 s, hang up, return: same.
3. Alarm fires mid-level: same.
4. Start music in another app, then open the game: game music muted or not started, SFX audible.
5. Unplug wired headphones and disconnect Bluetooth mid-music: no speaker blast.
6. Background for 10 minutes, foreground: audio returns without restart.
7. iOS only: trigger a media services reset from developer settings where available: no permanent silence.
8. Silent switch on (iOS) with `.ambient`: game silent; haptics still fire if designed.
