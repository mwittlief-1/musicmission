import XCTest
@testable import MusicAtlasController

final class SessionExporterTests: XCTestCase {
    func testReactionStoreAllowsOptionalNotes() async throws {
        let store = await ReactionStore()
        let now = Date()
        let selectedTag = ReactionTag(
            tagID: "TAG_DARK_PULL",
            label: "dark pull",
            primaryReactionValue: .hit,
            description: nil
        )

        try await store.saveReaction(
            for: "ITEM_TEST",
            value: .hit,
            note: "   ",
            selectedTags: [selectedTag],
            at: now
        )

        let reaction = await store.reaction(for: "ITEM_TEST")
        XCTAssertEqual(reaction?.reactionValue, .hit)
        XCTAssertEqual(reaction?.notes.text, "")
        XCTAssertEqual(reaction?.selectedTags, [selectedTag])
    }

    func testDevelopmentExportContainsStubEvidenceAndDecodes() async throws {
        let mission = try loadSampleMission()
        let item = try XCTUnwrap(mission.items.first)
        let now = try XCTUnwrap(ISO8601DateFormatter().date(from: "2026-05-17T12:00:00Z"))
        let resolution = try await StubMusicSearchService().resolve(item: item, at: now)
        let playback = PlaybackRecord.simulatedPlayed(at: now)
        let reaction = ReactionRecord(
            reactionValue: .hit,
            reactedAt: now,
            selectedTags: [
                ReactionTag(
                    tagID: "TAG_BITE",
                    label: "Bite",
                    primaryReactionValue: .hit,
                    description: "The guitar pressure or attack is part of why it works."
                )
            ],
            notes: ReactionNotes(text: "better with bite", voiceNoteRefs: nil)
        )

        let preview = try SessionExporter().makeDevelopmentExport(
            mission: mission,
            item: item,
            resolution: resolution,
            playback: playback,
            reaction: reaction,
            authorizationStatus: "notDetermined",
            now: now
        )

        XCTAssertTrue(preview.jsonFilename.hasPrefix("stub_reaction_session_"))
        XCTAssertEqual(preview.kind, .developmentStub)
        XCTAssertTrue(preview.markdownFilename.hasPrefix("stub_discovery_log_"))
        XCTAssertTrue(preview.markdownString.contains("development/stub export"))
        XCTAssertTrue(preview.markdownString.contains("does not count as physical-device acceptance evidence"))

        let data = try XCTUnwrap(preview.jsonString.data(using: .utf8))
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let session = try decoder.decode(ReactionSession.self, from: data)

        XCTAssertEqual(session.schemaVersion, "reaction_session.v0.2")
        XCTAssertEqual(session.missionID, mission.missionID)
        XCTAssertEqual(session.reconciliationStatus, .notReconciled)
        XCTAssertFalse(session.deviceContext.isPhysicalDevice)
        XCTAssertEqual(session.itemResults.count, 1)
        XCTAssertEqual(session.itemResults[0].resolution.status, .resolved)
        XCTAssertEqual(session.itemResults[0].playback.status, .played)
        XCTAssertEqual(session.itemResults[0].reaction.reactionValue, .hit)
        XCTAssertEqual(session.itemResults[0].reaction.selectedTags?.first?.tagID, "TAG_BITE")
        XCTAssertEqual(session.itemResults[0].reaction.notes.text, "better with bite")
        XCTAssertTrue(preview.markdownString.contains("Tags: Bite"))
    }

    func testDevelopmentExportCanIncludeMultipleMissionItems() async throws {
        let mission = try loadLithuanianAlphaMission()
        let firstItem = try XCTUnwrap(mission.items.first)
        let secondItem = try XCTUnwrap(mission.items.dropFirst().first)
        let now = try XCTUnwrap(ISO8601DateFormatter().date(from: "2026-05-18T12:00:00Z"))

        let firstEvidence = SessionItemEvidence(
            item: firstItem,
            resolution: try await StubMusicSearchService().resolve(item: firstItem, at: now),
            playback: PlaybackRecord.simulatedPlayed(at: now),
            reaction: ReactionRecord(
                reactionValue: .hit,
                reactedAt: now,
                selectedTags: firstItem.feedbackChips(for: .hit).prefix(1).map {
                    $0.reactionTag(primaryReactionValue: .hit)
                },
                notes: ReactionNotes(text: "", voiceNoteRefs: nil)
            )
        )
        let secondEvidence = SessionItemEvidence(
            item: secondItem,
            resolution: try await StubMusicSearchService().resolve(item: secondItem, at: now),
            playback: PlaybackRecord.simulatedPlayed(at: now),
            reaction: ReactionRecord(
                reactionValue: .partial,
                reactedAt: now,
                selectedTags: secondItem.feedbackChips(for: .partial).prefix(1).map {
                    $0.reactionTag(primaryReactionValue: .partial)
                },
                notes: ReactionNotes(text: "album-world maybe", voiceNoteRefs: nil)
            )
        )

        let preview = try SessionExporter().makeDevelopmentExport(
            mission: mission,
            evidenceItems: [secondEvidence, firstEvidence],
            authorizationStatus: "authorized",
            now: now
        )

        let data = try XCTUnwrap(preview.jsonString.data(using: .utf8))
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let session = try decoder.decode(ReactionSession.self, from: data)

        XCTAssertEqual(session.itemResults.map(\.sequence), [1, 2])
        XCTAssertEqual(session.sessionSummary?.resolvedCount, 2)
        XCTAssertEqual(session.sessionSummary?.playedCount, 2)
        XCTAssertEqual(session.sessionSummary?.reactionCount, 2)
        XCTAssertTrue(preview.markdownString.contains("### 1. Solo Ansamblis - Netildai"))
        XCTAssertTrue(preview.markdownString.contains("### 2. Solo Ansamblis - Malda"))
    }

    func testAcceptanceExportRequiresPhysicalNonStubEvidence() async throws {
        let mission = try loadSampleMission()
        let item = try XCTUnwrap(mission.items.first)
        let now = try XCTUnwrap(ISO8601DateFormatter().date(from: "2026-05-17T12:00:00Z"))
        let reaction = ReactionRecord(
            reactionValue: .hit,
            reactedAt: now,
            notes: ReactionNotes(text: "better with bite", voiceNoteRefs: nil)
        )
        let liveResolution = Self.liveResolution(for: item, at: now)
        let playback = await StubMusicPlaybackService().play(resolution: liveResolution, at: now)
        let exporter = SessionExporter()

        XCTAssertThrowsError(
            try exporter.makeAcceptanceExport(
                mission: mission,
                item: item,
                resolution: liveResolution,
                playback: playback,
                reaction: reaction,
                authorizationStatus: "authorized",
                deviceContext: Self.deviceContext(isPhysicalDevice: false),
                now: now
            )
        ) { error in
            XCTAssertEqual(error as? SessionExporterError, .physicalDeviceRequired)
        }

        let stubResolution = try await StubMusicSearchService().resolve(item: item, at: now)

        XCTAssertThrowsError(
            try exporter.makeAcceptanceExport(
                mission: mission,
                item: item,
                resolution: stubResolution,
                playback: playback,
                reaction: reaction,
                authorizationStatus: "authorized",
                deviceContext: Self.deviceContext(isPhysicalDevice: true),
                now: now
            )
        ) { error in
            XCTAssertEqual(error as? SessionExporterError, .stubEvidenceCannotBeAcceptance)
        }

        let preview = try exporter.makeAcceptanceExport(
            mission: mission,
            item: item,
            resolution: liveResolution,
            playback: playback,
            reaction: reaction,
            authorizationStatus: "authorized",
            deviceContext: Self.deviceContext(isPhysicalDevice: true),
            now: now
        )

        XCTAssertTrue(preview.jsonFilename.hasPrefix("acceptance_reaction_session_"))
        XCTAssertEqual(preview.kind, .acceptance)
        XCTAssertTrue(preview.markdownString.contains("physical-device acceptance"))

        let data = try XCTUnwrap(preview.jsonString.data(using: .utf8))
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let session = try decoder.decode(ReactionSession.self, from: data)

        XCTAssertTrue(session.deviceContext.isPhysicalDevice)
        XCTAssertEqual(session.musicContext.authorizationStatus, "authorized")
        XCTAssertEqual(session.musicContext.playbackCapabilityStatus, "capable")
        XCTAssertEqual(session.itemResults[0].resolution.catalogID, "123456789")
        XCTAssertEqual(session.itemResults[0].resolution.resolver, .automaticSearch)
    }

    func testAcceptanceExportFinalizesActivePlaybackAsPlayed() async throws {
        let mission = try loadSampleMission()
        let item = try XCTUnwrap(mission.items.first)
        let startedAt = try XCTUnwrap(ISO8601DateFormatter().date(from: "2026-05-17T12:00:00Z"))
        let exportedAt = try XCTUnwrap(ISO8601DateFormatter().date(from: "2026-05-17T12:00:35Z"))
        let reaction = ReactionRecord(
            reactionValue: .hit,
            reactedAt: exportedAt,
            notes: ReactionNotes(text: "better with bite", voiceNoteRefs: nil)
        )
        let playback = PlaybackRecord(
            status: .playing,
            attemptedAt: startedAt,
            startedAt: startedAt,
            endedAt: nil,
            durationSeconds: nil,
            errorCode: nil,
            errorMessage: nil
        )

        let preview = try SessionExporter().makeAcceptanceExport(
            mission: mission,
            item: item,
            resolution: Self.liveResolution(for: item, at: startedAt),
            playback: playback,
            reaction: reaction,
            authorizationStatus: "authorized",
            deviceContext: Self.deviceContext(isPhysicalDevice: true),
            now: exportedAt
        )

        let data = try XCTUnwrap(preview.jsonString.data(using: .utf8))
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let session = try decoder.decode(ReactionSession.self, from: data)
        let exportedPlayback = session.itemResults[0].playback

        XCTAssertEqual(exportedPlayback.status, .played)
        XCTAssertEqual(exportedPlayback.endedAt, exportedAt)
        XCTAssertEqual(try XCTUnwrap(exportedPlayback.durationSeconds), 35, accuracy: 0.001)
    }

    func testExportFileStoreWritesJsonAndMarkdownUnderKindDirectory() async throws {
        let mission = try loadSampleMission()
        let item = try XCTUnwrap(mission.items.first)
        let now = try XCTUnwrap(ISO8601DateFormatter().date(from: "2026-05-17T12:00:00Z"))
        let resolution = try await StubMusicSearchService().resolve(item: item, at: now)
        let playback = PlaybackRecord.simulatedPlayed(at: now)
        let reaction = ReactionRecord(
            reactionValue: .hit,
            reactedAt: now,
            notes: ReactionNotes(text: "better with bite", voiceNoteRefs: nil)
        )
        let preview = try SessionExporter().makeDevelopmentExport(
            mission: mission,
            item: item,
            resolution: resolution,
            playback: playback,
            reaction: reaction,
            authorizationStatus: "notDetermined",
            now: now
        )
        let tempDirectory = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString, isDirectory: true)
        defer {
            try? FileManager.default.removeItem(at: tempDirectory)
        }

        let savedExport = try ExportFileStore(baseDirectoryURL: tempDirectory).save(preview)

        XCTAssertEqual(savedExport.kind, .developmentStub)
        XCTAssertEqual(savedExport.directoryURL.lastPathComponent, "dev")
        XCTAssertTrue(FileManager.default.fileExists(atPath: savedExport.jsonURL.path))
        XCTAssertTrue(FileManager.default.fileExists(atPath: savedExport.markdownURL.path))
        XCTAssertEqual(try String(contentsOf: savedExport.jsonURL), preview.jsonString)
        XCTAssertEqual(try String(contentsOf: savedExport.markdownURL), preview.markdownString)
    }

    @MainActor
    func testAppModelMissionReadinessTracksStubLoop() async throws {
        let tempDirectory = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString, isDirectory: true)
        defer {
            try? FileManager.default.removeItem(at: tempDirectory)
        }
        let appModel = AppModel(
            exportFileStore: ExportFileStore(baseDirectoryURL: tempDirectory),
            sessionPersistenceStore: .disabled
        )
        appModel.loadSampleMission()

        XCTAssertFalse(appModel.canGenerateDevelopmentMissionExport)
        XCTAssertEqual(appModel.missionProgress.resolvedCount, 0)

        await appModel.resolveSelectedItemWithStub()
        XCTAssertEqual(appModel.missionProgress.resolvedCount, 1)
        XCTAssertEqual(appModel.missionProgress.playedCount, 0)
        XCTAssertFalse(appModel.canGenerateDevelopmentMissionExport)

        await appModel.playSelectedItem()
        XCTAssertEqual(appModel.missionProgress.playedCount, 1)

        appModel.saveReactionForSelectedItem(value: .hit, note: "")
        XCTAssertEqual(appModel.missionProgress.reactionCount, 1)
        XCTAssertTrue(appModel.canGenerateDevelopmentMissionExport)
        XCTAssertFalse(appModel.canGenerateAcceptanceMissionExport)

        appModel.generateDevelopmentExportPreview()
        XCTAssertNotNil(appModel.exportPreview)

        appModel.saveCurrentExportFiles()
        XCTAssertNotNil(appModel.savedExport)
    }

    @MainActor
    func testAppModelRestoresPersistedMissionSession() async throws {
        let tempDirectory = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString, isDirectory: true)
        defer {
            try? FileManager.default.removeItem(at: tempDirectory)
        }
        let persistenceStore = SessionPersistenceStore(baseDirectoryURL: tempDirectory)
        let appModel = AppModel(
            exportFileStore: ExportFileStore(baseDirectoryURL: tempDirectory),
            sessionPersistenceStore: persistenceStore
        )
        appModel.loadSampleMission()
        let firstItem = try XCTUnwrap(appModel.selectedItem)

        await appModel.resolveSelectedItemWithStub()
        appModel.saveReactionForSelectedItem(value: .hit, note: "restore this", selectedTags: [])
        appModel.selectNextItem()

        let restoredModel = AppModel(
            exportFileStore: ExportFileStore(baseDirectoryURL: tempDirectory),
            sessionPersistenceStore: persistenceStore
        )
        restoredModel.loadSampleMission()

        XCTAssertEqual(restoredModel.mission?.missionID, appModel.mission?.missionID)
        XCTAssertEqual(restoredModel.selectedItemID, appModel.selectedItemID)
        XCTAssertEqual(restoredModel.resolution(for: firstItem).status, .resolved)
        XCTAssertEqual(restoredModel.reaction(for: firstItem)?.reactionValue, .hit)
        XCTAssertEqual(restoredModel.reaction(for: firstItem)?.notes.text, "restore this")
    }

    @MainActor
    func testNextAfterStartedPlaybackAutoCapturesSkippedNoSignal() async throws {
        let tempDirectory = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString, isDirectory: true)
        defer {
            try? FileManager.default.removeItem(at: tempDirectory)
        }
        let appModel = AppModel(
            stubPlaybackService: StartedPlaybackService(),
            exportFileStore: ExportFileStore(baseDirectoryURL: tempDirectory),
            sessionPersistenceStore: .disabled
        )
        appModel.loadSampleMission()
        let firstItem = try XCTUnwrap(appModel.selectedItem)

        await appModel.resolveSelectedItemWithStub()
        await appModel.playSelectedItem()
        await appModel.playNextItem()

        XCTAssertEqual(appModel.playback(for: firstItem).status, .skipped)
        XCTAssertEqual(appModel.reaction(for: firstItem)?.reactionValue, .unresolved)
        XCTAssertEqual(appModel.selectedItem?.sequence, 2)
        XCTAssertEqual(appModel.playback(for: try XCTUnwrap(appModel.selectedItem)).status, .playing)
        XCTAssertTrue(appModel.canGenerateDevelopmentMissionExport)

        appModel.generateDevelopmentExportPreview()
        let preview = try XCTUnwrap(appModel.exportPreview)
        let data = try XCTUnwrap(preview.jsonString.data(using: .utf8))
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let session = try decoder.decode(ReactionSession.self, from: data)
        let skippedResult = try XCTUnwrap(session.itemResults.first { $0.missionItemID == firstItem.itemID })

        XCTAssertEqual(skippedResult.playback.status, .skipped)
        XCTAssertEqual(skippedResult.reaction.reactionValue, .unresolved)
        XCTAssertEqual(session.sessionSummary?.playedCount, 1)
        XCTAssertEqual(session.sessionSummary?.reactionCount, 1)
    }

    @MainActor
    func testNextAfterStartedPlaybackPreservesExplicitReaction() async throws {
        let appModel = AppModel(
            stubPlaybackService: StartedPlaybackService(),
            sessionPersistenceStore: .disabled
        )
        appModel.loadSampleMission()
        let firstItem = try XCTUnwrap(appModel.selectedItem)

        await appModel.resolveSelectedItemWithStub()
        await appModel.playSelectedItem()
        appModel.saveReactionForSelectedItem(value: .hit, note: "")
        await appModel.playNextItem()

        XCTAssertEqual(appModel.playback(for: firstItem).status, .skipped)
        XCTAssertEqual(appModel.reaction(for: firstItem)?.reactionValue, .hit)
    }

    @MainActor
    func testNextBeforePlaybackStartedLogsSkipButCreatesNoEvidence() async throws {
        let appModel = AppModel(sessionPersistenceStore: .disabled)
        appModel.loadSampleMission()
        let firstItem = try XCTUnwrap(appModel.selectedItem)

        await appModel.resolveSelectedItemWithStub()
        await appModel.playNextItem()

        XCTAssertEqual(appModel.playback(for: firstItem).status, .notAttempted)
        XCTAssertNil(appModel.reaction(for: firstItem))
        XCTAssertEqual(appModel.playerActionLog.first?.action, .skipBeforeStart)
        XCTAssertEqual(appModel.playerActionLog.first?.itemID, firstItem.itemID)
        XCTAssertEqual(appModel.selectedItem?.sequence, 2)
    }

    @MainActor
    func testNinetyPercentCompletionAutoStartsNextPlayableItem() async throws {
        let appModel = AppModel(
            stubPlaybackService: CompletedPlaybackService(),
            sessionPersistenceStore: .disabled
        )
        appModel.loadSampleMission()
        let firstItem = try XCTUnwrap(appModel.selectedItem)

        await appModel.resolveSelectedItemWithStub()
        await appModel.playSelectedItem()
        await appModel.refreshActivePlaybackSnapshot()

        XCTAssertEqual(appModel.playback(for: firstItem).status, .played)
        XCTAssertEqual(appModel.reaction(for: firstItem)?.reactionValue, .unresolved)
        XCTAssertEqual(appModel.playerActionLog.first?.action, .completedByThreshold)
        XCTAssertEqual(appModel.selectedItem?.sequence, 2)
        XCTAssertEqual(appModel.playback(for: try XCTUnwrap(appModel.selectedItem)).status, .playing)
    }

    @MainActor
    func testNinetyPercentPlayingProgressAutoStartsNextPlayableItem() async throws {
        let appModel = AppModel(
            stubPlaybackService: PlayingAtCompletionThresholdService(),
            sessionPersistenceStore: .disabled
        )
        appModel.loadSampleMission()
        let firstItem = try XCTUnwrap(appModel.selectedItem)

        await appModel.resolveSelectedItemWithStub()
        await appModel.playSelectedItem()
        await appModel.refreshActivePlaybackSnapshot()

        XCTAssertEqual(appModel.playback(for: firstItem).status, .played)
        XCTAssertEqual(appModel.playerActionLog.first?.action, .completedByThreshold)
        XCTAssertEqual(appModel.selectedItem?.sequence, 2)
        XCTAssertEqual(appModel.playback(for: try XCTUnwrap(appModel.selectedItem)).status, .playing)
    }

    @MainActor
    func testPausedPlaybackAtCompletionThresholdDoesNotAutoAdvance() async throws {
        let appModel = AppModel(
            stubPlaybackService: PausedAtCompletionThresholdService(),
            sessionPersistenceStore: .disabled
        )
        appModel.loadSampleMission()
        let firstItem = try XCTUnwrap(appModel.selectedItem)

        await appModel.resolveSelectedItemWithStub()
        await appModel.playSelectedItem()
        await appModel.refreshActivePlaybackSnapshot()

        XCTAssertEqual(appModel.selectedItem?.itemID, firstItem.itemID)
        XCTAssertEqual(appModel.playback(for: firstItem).status, .playing)
        XCTAssertTrue(appModel.playerActionLog.isEmpty)
    }

    @MainActor
    func testSeekSelectedPlaybackUpdatesPlaybackSnapshot() async throws {
        let appModel = AppModel(
            stubPlaybackService: StartedPlaybackService(),
            sessionPersistenceStore: .disabled
        )
        appModel.loadSampleMission()
        let firstItem = try XCTUnwrap(appModel.selectedItem)

        await appModel.resolveSelectedItemWithStub()
        await appModel.playSelectedItem()
        await appModel.seekSelectedPlayback(to: 75)

        let snapshot = appModel.playbackSnapshot(for: firstItem)
        XCTAssertEqual(snapshot.runtimeStatus, .playing)
        XCTAssertEqual(snapshot.elapsedSeconds, 75)
        XCTAssertEqual(snapshot.totalDurationSeconds, 180)
    }

    @MainActor
    func testSeekBackwardResetsCompletionClock() async throws {
        let appModel = AppModel(
            stubPlaybackService: RecordBackedPlaybackService(startingElapsedSeconds: 170),
            sessionPersistenceStore: .disabled
        )
        appModel.loadSampleMission()
        let firstItem = try XCTUnwrap(appModel.selectedItem)

        await appModel.resolveSelectedItemWithStub()
        await appModel.playSelectedItem()
        await appModel.seekSelectedPlayback(to: 20)
        await appModel.refreshActivePlaybackSnapshot()

        XCTAssertEqual(appModel.selectedItem?.itemID, firstItem.itemID)
        XCTAssertEqual(appModel.playback(for: firstItem).status, .playing)
        XCTAssertTrue(appModel.playerActionLog.isEmpty)
    }

    @MainActor
    func testMissionReviewSnapshotSurfacesSkippedNoSignalAndAllowsReviewEdit() async throws {
        let appModel = AppModel(
            stubPlaybackService: StartedPlaybackService(),
            sessionPersistenceStore: .disabled
        )
        appModel.loadSampleMission()
        let firstItem = try XCTUnwrap(appModel.selectedItem)

        await appModel.resolveSelectedItemWithStub()
        await appModel.playSelectedItem()
        await appModel.playNextItem()

        var snapshot = appModel.missionReviewSnapshot
        var skippedEvidence = try XCTUnwrap(snapshot.items.first { $0.item.itemID == firstItem.itemID })

        XCTAssertEqual(snapshot.summary.skippedCount, 1)
        XCTAssertEqual(snapshot.summary.playbackEvidenceCount, 2)
        XCTAssertTrue(skippedEvidence.flags.contains(.skippedNoSignal))
        XCTAssertEqual(skippedEvidence.reaction?.reactionValue, .unresolved)

        appModel.saveReaction(for: firstItem, value: .hit, note: "reviewed after skip")

        snapshot = appModel.missionReviewSnapshot
        skippedEvidence = try XCTUnwrap(snapshot.items.first { $0.item.itemID == firstItem.itemID })

        XCTAssertFalse(skippedEvidence.flags.contains(.skippedNoSignal))
        XCTAssertEqual(skippedEvidence.reaction?.reactionValue, .hit)
        XCTAssertEqual(skippedEvidence.noteText, "reviewed after skip")
    }

    func testReactionOperationsKeepDisplayLabelsConfigurable() {
        XCTAssertEqual(ReactionOperation.strongPositive.defaultReactionValue, .hit)
        XCTAssertEqual(ReactionOperation.qualifiedPositive.defaultReactionValue, .partial)
        XCTAssertEqual(ReactionOperation.keepWaypoint.defaultReactionValue, .okShelf)
        XCTAssertEqual(ReactionOperation.negative.defaultReactionValue, .miss)
        XCTAssertEqual(ReactionDisplayConfiguration.current.label(for: .hit), "Love")
        XCTAssertEqual(ReactionDisplayConfiguration.current.label(for: .partial), "Like")
        XCTAssertEqual(ReactionDisplayConfiguration.current.label(for: .okShelf), "Ok")
        XCTAssertEqual(ReactionDisplayConfiguration.current.label(for: .miss), "Dislike")
        XCTAssertEqual(ReactionDisplayConfiguration.current.label(for: .unresolved), "No Signal")
    }

    private static func liveResolution(for item: MissionItem, at date: Date) -> AppleMusicResolution {
        AppleMusicResolution(
            status: .resolved,
            catalogID: "123456789",
            catalogURL: URL(string: "https://music.apple.com/us/song/example/123456789"),
            artworkURL: URL(string: "https://example.com/artwork.jpg"),
            storefront: "us",
            resolvedTitle: item.title,
            resolvedArtist: item.artist,
            resolvedAlbum: item.album,
            confidence: 0.94,
            resolver: .automaticSearch,
            resolvedAt: date,
            reason: "music_kit_catalog_search_top_result",
            candidateCount: 3,
            errorCode: nil,
            errorMessage: nil
        )
    }

    private static func deviceContext(isPhysicalDevice: Bool) -> DeviceContext {
        DeviceContext(
            deviceModel: isPhysicalDevice ? "iPhone" : "iPhone Simulator",
            osVersion: "iOS 26.5",
            appVersion: "0.2-test",
            isPhysicalDevice: isPhysicalDevice
        )
    }
}

private struct StartedPlaybackService: MusicPlaybackServing {
    func play(resolution: AppleMusicResolution, at date: Date) async -> PlaybackRecord {
        PlaybackRecord(
            status: .playing,
            attemptedAt: date,
            startedAt: date,
            endedAt: nil,
            durationSeconds: 180,
            errorCode: nil,
            errorMessage: nil
        )
    }

    func resume(currentPlayback: PlaybackRecord, at date: Date) async -> PlaybackRecord {
        currentPlayback
    }

    func pause(currentPlayback: PlaybackRecord, at date: Date) async -> PlaybackRecord {
        currentPlayback
    }

    func stop(currentPlayback: PlaybackRecord, at date: Date) async -> PlaybackRecord {
        currentPlayback.endedAsPlayed(at: date)
    }

    func snapshot(currentPlayback: PlaybackRecord) -> PlaybackSnapshot {
        PlaybackSnapshot(
            runtimeStatus: currentPlayback.status == .playing ? .playing : .idle,
            elapsedSeconds: 12,
            totalDurationSeconds: currentPlayback.durationSeconds
        )
    }
}

private struct CompletedPlaybackService: MusicPlaybackServing {
    func play(resolution: AppleMusicResolution, at date: Date) async -> PlaybackRecord {
        PlaybackRecord(
            status: .playing,
            attemptedAt: date,
            startedAt: date.addingTimeInterval(-162),
            endedAt: nil,
            durationSeconds: 180,
            errorCode: nil,
            errorMessage: nil
        )
    }

    func resume(currentPlayback: PlaybackRecord, at date: Date) async -> PlaybackRecord {
        currentPlayback
    }

    func pause(currentPlayback: PlaybackRecord, at date: Date) async -> PlaybackRecord {
        currentPlayback
    }

    func stop(currentPlayback: PlaybackRecord, at date: Date) async -> PlaybackRecord {
        currentPlayback.endedAsPlayed(at: date)
    }

    func snapshot(currentPlayback: PlaybackRecord) -> PlaybackSnapshot {
        PlaybackSnapshot(
            runtimeStatus: .stopped,
            elapsedSeconds: 162,
            totalDurationSeconds: currentPlayback.durationSeconds
        )
    }
}

private struct PlayingAtCompletionThresholdService: MusicPlaybackServing {
    func play(resolution: AppleMusicResolution, at date: Date) async -> PlaybackRecord {
        PlaybackRecord(
            status: .playing,
            attemptedAt: date,
            startedAt: date.addingTimeInterval(-163),
            endedAt: nil,
            durationSeconds: 180,
            errorCode: nil,
            errorMessage: nil
        )
    }

    func resume(currentPlayback: PlaybackRecord, at date: Date) async -> PlaybackRecord {
        currentPlayback
    }

    func pause(currentPlayback: PlaybackRecord, at date: Date) async -> PlaybackRecord {
        currentPlayback
    }

    func stop(currentPlayback: PlaybackRecord, at date: Date) async -> PlaybackRecord {
        currentPlayback.endedAsPlayed(at: date)
    }

    func snapshot(currentPlayback: PlaybackRecord) -> PlaybackSnapshot {
        PlaybackSnapshot(
            runtimeStatus: .playing,
            elapsedSeconds: 163,
            totalDurationSeconds: currentPlayback.durationSeconds
        )
    }
}

private struct PausedAtCompletionThresholdService: MusicPlaybackServing {
    func play(resolution: AppleMusicResolution, at date: Date) async -> PlaybackRecord {
        PlaybackRecord(
            status: .playing,
            attemptedAt: date,
            startedAt: date.addingTimeInterval(-170),
            endedAt: nil,
            durationSeconds: 180,
            errorCode: nil,
            errorMessage: nil
        )
    }

    func resume(currentPlayback: PlaybackRecord, at date: Date) async -> PlaybackRecord {
        currentPlayback
    }

    func pause(currentPlayback: PlaybackRecord, at date: Date) async -> PlaybackRecord {
        currentPlayback
    }

    func stop(currentPlayback: PlaybackRecord, at date: Date) async -> PlaybackRecord {
        currentPlayback.endedAsPlayed(at: date)
    }

    func snapshot(currentPlayback: PlaybackRecord) -> PlaybackSnapshot {
        PlaybackSnapshot(
            runtimeStatus: .paused,
            elapsedSeconds: 170,
            totalDurationSeconds: currentPlayback.durationSeconds
        )
    }
}

private struct RecordBackedPlaybackService: MusicPlaybackServing {
    let startingElapsedSeconds: TimeInterval

    func play(resolution: AppleMusicResolution, at date: Date) async -> PlaybackRecord {
        PlaybackRecord(
            status: .playing,
            attemptedAt: date,
            startedAt: date.addingTimeInterval(-startingElapsedSeconds),
            endedAt: nil,
            durationSeconds: 180,
            errorCode: nil,
            errorMessage: nil
        )
    }

    func resume(currentPlayback: PlaybackRecord, at date: Date) async -> PlaybackRecord {
        currentPlayback
    }

    func pause(currentPlayback: PlaybackRecord, at date: Date) async -> PlaybackRecord {
        currentPlayback
    }

    func stop(currentPlayback: PlaybackRecord, at date: Date) async -> PlaybackRecord {
        currentPlayback.endedAsPlayed(at: date)
    }

    func snapshot(currentPlayback: PlaybackRecord) -> PlaybackSnapshot {
        PlaybackSnapshot.from(record: currentPlayback)
    }
}
