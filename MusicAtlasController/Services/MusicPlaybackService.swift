import Foundation

#if canImport(MusicKit)
import MusicKit
#endif

protocol MusicPlaybackServing {
    func play(resolution: AppleMusicResolution, at date: Date) async -> PlaybackRecord
    func resume(currentPlayback: PlaybackRecord, at date: Date) async -> PlaybackRecord
    func pause(currentPlayback: PlaybackRecord, at date: Date) async -> PlaybackRecord
    func stop(currentPlayback: PlaybackRecord, at date: Date) async -> PlaybackRecord
    func seek(to elapsedSeconds: TimeInterval, currentPlayback: PlaybackRecord, at date: Date) async -> PlaybackRecord
    func snapshot(currentPlayback: PlaybackRecord) -> PlaybackSnapshot
}

extension MusicPlaybackServing {
    func seek(to elapsedSeconds: TimeInterval, currentPlayback: PlaybackRecord, at date: Date) async -> PlaybackRecord {
        currentPlayback
    }
}

struct StubMusicPlaybackService: MusicPlaybackServing {
    func play(resolution: AppleMusicResolution, at date: Date) async -> PlaybackRecord {
        guard resolution.status == .resolved else {
            return PlaybackRecord(
                status: .failed,
                attemptedAt: date,
                startedAt: nil,
                endedAt: nil,
                durationSeconds: nil,
                errorCode: "stub_playback_requires_resolved_item",
                errorMessage: "Resolve the selected item before simulating playback."
            )
        }

        return .simulatedPlayed(at: date)
    }

    func pause(currentPlayback: PlaybackRecord, at date: Date) async -> PlaybackRecord {
        currentPlayback
    }

    func resume(currentPlayback: PlaybackRecord, at date: Date) async -> PlaybackRecord {
        currentPlayback
    }

    func stop(currentPlayback: PlaybackRecord, at date: Date) async -> PlaybackRecord {
        currentPlayback.hasPlaybackStarted ? currentPlayback.endedAsPlayed(at: date) : currentPlayback
    }

    func seek(to elapsedSeconds: TimeInterval, currentPlayback: PlaybackRecord, at date: Date) async -> PlaybackRecord {
        currentPlayback
    }

    func snapshot(currentPlayback: PlaybackRecord) -> PlaybackSnapshot {
        PlaybackSnapshot.from(record: currentPlayback)
    }
}

struct MusicKitPlaybackService: MusicPlaybackServing {
    func play(resolution: AppleMusicResolution, at date: Date) async -> PlaybackRecord {
        #if canImport(MusicKit)
        guard resolution.status == .resolved, let catalogID = resolution.catalogID else {
            return PlaybackRecord(
                status: .failed,
                attemptedAt: date,
                startedAt: nil,
                endedAt: nil,
                durationSeconds: nil,
                errorCode: "music_kit_playback_requires_resolved_catalog_id",
                errorMessage: "Resolve the selected item to an Apple Music catalog ID before playback."
            )
        }

        do {
            var request = MusicCatalogResourceRequest<Song>(
                matching: \.id,
                equalTo: MusicItemID(catalogID)
            )
            request.limit = 1

            let response = try await request.response()
            guard let song = response.items.first else {
                return PlaybackRecord(
                    status: .failed,
                    attemptedAt: date,
                    startedAt: nil,
                    endedAt: nil,
                    durationSeconds: nil,
                    errorCode: "music_kit_catalog_id_not_found",
                    errorMessage: "MusicKit could not fetch the resolved catalog item for playback."
                )
            }

            let player = ApplicationMusicPlayer.shared
            player.queue = ApplicationMusicPlayer.Queue(for: [song])
            try await player.prepareToPlay()
            try await player.play()

            return PlaybackRecord(
                status: .playing,
                attemptedAt: date,
                startedAt: Date(),
                endedAt: nil,
                durationSeconds: song.duration,
                errorCode: nil,
                errorMessage: nil
            )
        } catch {
            let nsError = error as NSError
            return PlaybackRecord(
                status: .failed,
                attemptedAt: date,
                startedAt: nil,
                endedAt: nil,
                durationSeconds: nil,
                errorCode: "music_kit_playback_failed:\(nsError.domain)#\(nsError.code)",
                errorMessage: error.musicAtlasDiagnosticDescription
            )
        }
        #else
        return PlaybackRecord(
            status: .failed,
            attemptedAt: date,
            startedAt: nil,
            endedAt: nil,
            durationSeconds: nil,
            errorCode: "music_kit_unavailable",
            errorMessage: "MusicKit is not available in this build environment."
        )
        #endif
    }

    func pause(currentPlayback: PlaybackRecord, at date: Date) async -> PlaybackRecord {
        #if canImport(MusicKit)
        ApplicationMusicPlayer.shared.pause()
        return currentPlayback
        #else
        return PlaybackRecord(
            status: .failed,
            attemptedAt: date,
            startedAt: nil,
            endedAt: nil,
            durationSeconds: nil,
            errorCode: "music_kit_unavailable",
            errorMessage: "MusicKit is not available in this build environment."
        )
        #endif
    }

    func resume(currentPlayback: PlaybackRecord, at date: Date) async -> PlaybackRecord {
        #if canImport(MusicKit)
        do {
            try await ApplicationMusicPlayer.shared.play()
            return currentPlayback
        } catch {
            let nsError = error as NSError
            return PlaybackRecord(
                status: .failed,
                attemptedAt: currentPlayback.attemptedAt ?? date,
                startedAt: currentPlayback.startedAt,
                endedAt: date,
                durationSeconds: currentPlayback.durationSeconds,
                errorCode: "music_kit_resume_failed:\(nsError.domain)#\(nsError.code)",
                errorMessage: error.musicAtlasDiagnosticDescription
            )
        }
        #else
        return PlaybackRecord(
            status: .failed,
            attemptedAt: currentPlayback.attemptedAt ?? date,
            startedAt: currentPlayback.startedAt,
            endedAt: date,
            durationSeconds: currentPlayback.durationSeconds,
            errorCode: "music_kit_unavailable",
            errorMessage: "MusicKit is not available in this build environment."
        )
        #endif
    }

    func stop(currentPlayback: PlaybackRecord, at date: Date) async -> PlaybackRecord {
        #if canImport(MusicKit)
        ApplicationMusicPlayer.shared.stop()
        return currentPlayback.hasPlaybackStarted ? currentPlayback.endedAsPlayed(at: date) : currentPlayback
        #else
        return PlaybackRecord(
            status: .failed,
            attemptedAt: date,
            startedAt: nil,
            endedAt: nil,
            durationSeconds: nil,
            errorCode: "music_kit_unavailable",
            errorMessage: "MusicKit is not available in this build environment."
        )
        #endif
    }

    func seek(to elapsedSeconds: TimeInterval, currentPlayback: PlaybackRecord, at date: Date) async -> PlaybackRecord {
        #if canImport(MusicKit)
        let boundedElapsed: TimeInterval
        if let duration = currentPlayback.durationSeconds, duration > 0 {
            boundedElapsed = min(max(0, elapsedSeconds), duration)
        } else {
            boundedElapsed = max(0, elapsedSeconds)
        }

        ApplicationMusicPlayer.shared.playbackTime = boundedElapsed
        return currentPlayback
        #else
        return PlaybackRecord(
            status: .failed,
            attemptedAt: date,
            startedAt: nil,
            endedAt: nil,
            durationSeconds: nil,
            errorCode: "music_kit_unavailable",
            errorMessage: "MusicKit is not available in this build environment."
        )
        #endif
    }

    func snapshot(currentPlayback: PlaybackRecord) -> PlaybackSnapshot {
        #if canImport(MusicKit)
        let player = ApplicationMusicPlayer.shared
        let runtimeStatus: PlaybackRuntimeStatus

        switch player.state.playbackStatus {
        case .playing:
            runtimeStatus = .playing
        case .paused:
            runtimeStatus = .paused
        case .stopped:
            runtimeStatus = currentPlayback.status == .played ? .completed : .stopped
        case .interrupted:
            runtimeStatus = .interrupted
        case .seekingForward, .seekingBackward:
            runtimeStatus = .seeking
        @unknown default:
            runtimeStatus = .idle
        }

        return PlaybackSnapshot(
            runtimeStatus: runtimeStatus,
            elapsedSeconds: max(0, player.playbackTime),
            totalDurationSeconds: currentPlayback.durationSeconds
        )
        #else
        return PlaybackSnapshot.from(record: currentPlayback)
        #endif
    }
}
