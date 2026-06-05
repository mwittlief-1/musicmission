import XCTest
@testable import MusicAtlasController

final class SessionExporterTests: XCTestCase {
    func testReactionStoreAllowsOptionalNotes() async throws {
        let store = await ReactionStore()
        let now = Date()
        let selectedTag = ReactionTag(
            tagID: "TAG_BODY_PRESSURE",
            label: "body pressure",
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
        let atlasBundle = try XCTUnwrap(session.atlasSignalCandidateBundle)
        XCTAssertEqual(atlasBundle.recordType, "atlas_signal_candidate_bundle")
        XCTAssertEqual(atlasBundle.schemaVersion, "atlas_signal_candidate_bundle.v0.1")
        XCTAssertEqual(atlasBundle.candidateStatus, "ingestion_candidate")
        XCTAssertEqual(atlasBundle.promotionState, "not_promoted")
        XCTAssertFalse(atlasBundle.writesAtlasTruth)
        XCTAssertFalse(atlasBundle.canonicalGraphMutationAllowed)
        XCTAssertEqual(atlasBundle.candidates.count, 6)
        XCTAssertEqual(preview.atlasSignalCandidateCount, atlasBundle.candidates.count)
        XCTAssertFalse(atlasBundle.candidates.contains { $0.writesAtlasTruth })

        let reactionCandidate = try XCTUnwrap(atlasBundle.candidates.first { $0.eventType == .reaction })
        XCTAssertEqual(reactionCandidate.evidence.reactionValue, .hit)
        XCTAssertEqual(reactionCandidate.evidence.reactionOperation, .strongPositive)
        XCTAssertEqual(reactionCandidate.evidence.reactionLabel, "Love")
        XCTAssertEqual(reactionCandidate.evidence.selectedChips?.first?.tagID, "TAG_BITE")
        XCTAssertFalse(reactionCandidate.evidence.shownUnselectedChips?.contains { $0.tagID == "TAG_BITE" } ?? true)

        let chipCandidate = try XCTUnwrap(atlasBundle.candidates.first { $0.eventType == .chip })
        XCTAssertEqual(chipCandidate.evidence.selectedChip?.tagID, "TAG_BITE")

        let noteCandidate = try XCTUnwrap(atlasBundle.candidates.first { $0.eventType == .note })
        XCTAssertEqual(noteCandidate.evidence.noteText, "better with bite")
        XCTAssertTrue(preview.markdownString.contains("Tags: Bite"))
        XCTAssertTrue(preview.markdownString.contains("Atlas Signal Candidates"))
    }

    func testDevelopmentExportCanIncludeMultipleMissionItems() async throws {
        let mission = try loadSampleMission()
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
        XCTAssertTrue(preview.markdownString.contains("### 1. Love - A House Is Not a Motel"))
        XCTAssertTrue(preview.markdownString.contains("### 2. The Move - I Can Hear the Grass Grow"))
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
            sessionPersistenceStore: .disabled,
            missionProvider: TestMissionProvider(missions: [try loadSampleMission()])
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
            sessionPersistenceStore: persistenceStore,
            missionProvider: TestMissionProvider(missions: [try loadSampleMission()])
        )
        appModel.loadSampleMission()
        let firstItem = try XCTUnwrap(appModel.selectedItem)

        await appModel.resolveSelectedItemWithStub()
        appModel.saveReactionForSelectedItem(value: .hit, note: "restore this", selectedTags: [])
        appModel.selectNextItem()

        let restoredModel = AppModel(
            exportFileStore: ExportFileStore(baseDirectoryURL: tempDirectory),
            sessionPersistenceStore: persistenceStore,
            missionProvider: TestMissionProvider(missions: [try loadSampleMission()])
        )
        restoredModel.loadSampleMission()

        XCTAssertEqual(restoredModel.mission?.missionID, appModel.mission?.missionID)
        XCTAssertEqual(restoredModel.selectedItemID, appModel.selectedItemID)
        XCTAssertEqual(restoredModel.resolution(for: firstItem).status, .resolved)
        XCTAssertEqual(restoredModel.reaction(for: firstItem)?.reactionValue, .hit)
        XCTAssertEqual(restoredModel.reaction(for: firstItem)?.notes.text, "restore this")
    }

    @MainActor
    func testSupportDiagnosticsIncludesReviewedMissionCatalogWithoutClearingSurveyResponses() throws {
        let tempDirectory = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString, isDirectory: true)
        defer {
            try? FileManager.default.removeItem(at: tempDirectory)
        }
        let surveyPersistenceStore = SurveyPersistenceStore(baseDirectoryURL: tempDirectory)
        let surveyStore = SurveyStore(persistenceStore: surveyPersistenceStore)
        surveyStore.prepareRequiredAlphaIntake()
        surveyStore.goTo(.artistPage1)
        let firstSurveyItem = try XCTUnwrap(surveyStore.currentPage?.items.first)
        surveyStore.setState(.favorite, for: firstSurveyItem)
        let persistedSurveyBeforeDiagnostics = surveyPersistenceStore.load()

        XCTAssertEqual(persistedSurveyBeforeDiagnostics.responses.count, 1)

        let mission = try loadSampleMission()
        let appModel = AppModel(
            exportFileStore: ExportFileStore(baseDirectoryURL: tempDirectory),
            sessionPersistenceStore: .disabled,
            missionProvider: TestMissionProvider(missions: [mission]),
            surveyEvidenceBuilder: SurveyEvidenceExportBuilder(persistenceStore: surveyPersistenceStore),
            clientDiagnosticStore: ClientDiagnosticArtifactStore(baseDirectoryURL: tempDirectory)
        )

        appModel.saveSupportDiagnosticPackage()

        let persistedSurveyAfterDiagnostics = surveyPersistenceStore.load()
        XCTAssertEqual(persistedSurveyAfterDiagnostics.surveySessionID, persistedSurveyBeforeDiagnostics.surveySessionID)
        XCTAssertEqual(persistedSurveyAfterDiagnostics.responses.count, 1)
        XCTAssertEqual(persistedSurveyAfterDiagnostics.responses[firstSurveyItem.id]?.state, .favorite)

        let package = try XCTUnwrap(appModel.savedSupportDiagnosticsPackage)
        let artifactObjects = try package.artifactURLs.map { url in
            try XCTUnwrap(JSONSerialization.jsonObject(with: Data(contentsOf: url)) as? [String: Any])
        }
        let clientStateArtifact = try XCTUnwrap(artifactObjects.first { artifact in
            guard artifact["artifact_type"] as? String == ClientDiagnosticArtifactType.clientStateSnapshot.rawValue,
                  let payload = artifact["payload"] as? [String: Any],
                  payload["schema_version"] as? String == "waymark.client_state_snapshot.v0.1" else {
                return false
            }
            return payload["reviewed_mission_catalog_snapshot"] is [String: Any]
        })
        let clientStatePayload = try XCTUnwrap(clientStateArtifact["payload"] as? [String: Any])
        let payload = try XCTUnwrap(clientStatePayload["reviewed_mission_catalog_snapshot"] as? [String: Any])
        let surveyLink = try XCTUnwrap(payload["survey_link"] as? [String: Any])
        let missionCatalog = try XCTUnwrap(payload["mission_catalog"] as? [String: Any])
        let appMissions = try XCTUnwrap(payload["app_missions"] as? [[String: Any]])
        let missionSummaries = try XCTUnwrap(payload["mission_summaries"] as? [[String: Any]])
        let firstMission = try XCTUnwrap(appMissions.first)
        let firstMissionItems = try XCTUnwrap(firstMission["items"] as? [[String: Any]])

        XCTAssertEqual(payload["snapshot_status"] as? String, "captured")
        XCTAssertEqual(surveyLink["survey_session_id"] as? String, persistedSurveyBeforeDiagnostics.surveySessionID)
        XCTAssertEqual(surveyLink["survey_response_count"] as? Int, 1)
        XCTAssertEqual(missionCatalog["reviewed_mission_count"] as? Int, 1)
        XCTAssertEqual(missionCatalog["route_item_count"] as? Int, mission.items.count)
        XCTAssertEqual(appMissions.count, 1)
        XCTAssertEqual(firstMission["mission_id"] as? String, mission.missionID)
        XCTAssertEqual(firstMissionItems.count, mission.items.count)
        XCTAssertEqual(missionSummaries.first?["mission_id"] as? String, mission.missionID)
        XCTAssertEqual(
            (missionSummaries.first?["route_items"] as? [[String: Any]])?.count,
            mission.items.count
        )
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
            sessionPersistenceStore: .disabled,
            missionProvider: TestMissionProvider(missions: [try loadSampleMission()])
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
        let atlasBundle = try XCTUnwrap(session.atlasSignalCandidateBundle)
        let skipCandidate = try XCTUnwrap(
            atlasBundle.candidates.first {
                $0.eventType == .skip && $0.missionItemID == firstItem.itemID
            }
        )

        XCTAssertEqual(skipCandidate.reviewState, "needs_review")
        XCTAssertEqual(skipCandidate.evidence.skipPolicy, "started_track_then_user_advanced")
        XCTAssertEqual(skipCandidate.evidence.reviewFlags, ["skipped_no_signal"])
        XCTAssertEqual(skipCandidate.evidence.reviewNeeded, true)
    }

    @MainActor
    func testNextAfterStartedPlaybackPreservesExplicitReaction() async throws {
        let appModel = AppModel(
            stubPlaybackService: StartedPlaybackService(),
            sessionPersistenceStore: .disabled,
            missionProvider: TestMissionProvider(missions: [try loadSampleMission()])
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
        let appModel = AppModel(
            sessionPersistenceStore: .disabled,
            missionProvider: TestMissionProvider(missions: [try loadSampleMission()])
        )
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
            sessionPersistenceStore: .disabled,
            missionProvider: TestMissionProvider(missions: [try loadSampleMission()])
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
    func testNinetyPercentPlayingProgressDoesNotAutoAdvanceWhileStillPlaying() async throws {
        let appModel = AppModel(
            stubPlaybackService: PlayingAtCompletionThresholdService(),
            sessionPersistenceStore: .disabled,
            missionProvider: TestMissionProvider(missions: [try loadSampleMission()])
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
    func testPausedPlaybackAtCompletionThresholdDoesNotAutoAdvance() async throws {
        let appModel = AppModel(
            stubPlaybackService: PausedAtCompletionThresholdService(),
            sessionPersistenceStore: .disabled,
            missionProvider: TestMissionProvider(missions: [try loadSampleMission()])
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
            sessionPersistenceStore: .disabled,
            missionProvider: TestMissionProvider(missions: [try loadSampleMission()])
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
            sessionPersistenceStore: .disabled,
            missionProvider: TestMissionProvider(missions: [try loadSampleMission()])
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
            sessionPersistenceStore: .disabled,
            missionProvider: TestMissionProvider(missions: [try loadSampleMission()])
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

    func testLiveMissionGenerationRequestUsesSupabaseSessionBearer() throws {
        let config = SupabaseAlphaConfig(
            projectURL: try XCTUnwrap(URL(string: "https://example.supabase.co")),
            anonKey: "sb_publishable_test",
            generateFirstMissionBatchFunctionName: "generate-first-mission-batch",
            enrichMissionFunctionName: "enrich-mission",
            submitAlphaEvidenceFunctionName: "submit-alpha-evidence",
            submitAlphaDiagnosticFunctionName: "submit-alpha-diagnostic",
            testerAlias: "trusted-alpha-test"
        )
        let client = LiveSupabaseMissionGenerationClient(config: config)
        let request = MissionGenerationRequest(
            clientRequestID: "client-request-1",
            testerAlias: "trusted-alpha-test",
            requestedBatchSize: 3,
            surveyEvidenceExport: Data(#"{"schema_version":"survey"}"#.utf8),
            missionGenerationDigestView: Data(#"{"schema_version":"digest"}"#.utf8),
            candidatePool: Data(#"{"candidates":[]}"#.utf8),
            promptContext: MissionGenerationPromptContext(
                alphaScope: "first_batch_after_required_survey",
                generationMode: "live_app_generation",
                sourceAppVersion: "0.2",
                sourceAppBuild: "2",
                storefront: "us",
                surveyPageCount: SurveyPageCount(artist: 4, album: 2, song: 4),
                alreadySelectedRouteItemIDs: ["ITEM_ALREADY_USED"],
                alreadySelectedRouteDisplayIdentityKeys: ["track::already::used"],
                batchMemoryDirective: "Do not repeat imported route items."
            ),
            alreadySelectedRouteItemIDs: ["ITEM_ALREADY_USED"],
            alreadySelectedRouteDisplayIdentityKeys: ["track::already::used"]
        )

        let urlRequest = try client.makeURLRequest(request: request, accessToken: "session.jwt")
        XCTAssertEqual(urlRequest.value(forHTTPHeaderField: "apikey"), "sb_publishable_test")
        XCTAssertEqual(urlRequest.value(forHTTPHeaderField: "Authorization"), "Bearer session.jwt")
        XCTAssertEqual(urlRequest.url?.absoluteString, "https://example.supabase.co/functions/v1/generate-first-mission-batch")

        let body = try XCTUnwrap(urlRequest.httpBody)
        let object = try XCTUnwrap(JSONSerialization.jsonObject(with: body) as? [String: Any])
        XCTAssertEqual(object["client_request_id"] as? String, "client-request-1")
        XCTAssertNotNil(object["survey_evidence_export"] as? [String: Any])
        XCTAssertNotNil(object["mission_generation_digest_view"] as? [String: Any])
        XCTAssertNotNil(object["candidate_pool"] as? [String: Any])
        XCTAssertEqual(object["already_selected_route_item_ids"] as? [String], ["ITEM_ALREADY_USED"])
        XCTAssertEqual(object["already_selected_route_display_identity_keys"] as? [String], ["track::already::used"])
        XCTAssertEqual(object["already_selected_display_keys"] as? [String], ["track::already::used"])
        let promptContext = try XCTUnwrap(object["prompt_context"] as? [String: Any])
        XCTAssertEqual(promptContext["already_selected_route_item_ids"] as? [String], ["ITEM_ALREADY_USED"])
        XCTAssertEqual(promptContext["already_selected_route_display_identity_keys"] as? [String], ["track::already::used"])
        XCTAssertEqual(promptContext["already_selected_display_keys"] as? [String], ["track::already::used"])
    }

    func testLiveEvidenceUploadRequestUsesSessionBearerAndConsent() throws {
        let config = SupabaseAlphaConfig(
            projectURL: try XCTUnwrap(URL(string: "https://example.supabase.co")),
            anonKey: "sb_publishable_test",
            generateFirstMissionBatchFunctionName: "generate-first-mission-batch",
            enrichMissionFunctionName: "enrich-mission",
            submitAlphaEvidenceFunctionName: "submit-alpha-evidence",
            submitAlphaDiagnosticFunctionName: "submit-alpha-diagnostic",
            testerAlias: "trusted-alpha-test"
        )
        let client = LiveEvidenceUploadClient(config: config)
        let directoryURL = FileManager.default.temporaryDirectory
            .appendingPathComponent("waymark-evidence-upload-test-\(UUID().uuidString)", isDirectory: true)
        try FileManager.default.createDirectory(at: directoryURL, withIntermediateDirectories: true)
        let jsonURL = directoryURL.appendingPathComponent("acceptance_reaction_session_test.json")
        let markdownURL = directoryURL.appendingPathComponent("acceptance_reaction_session_test.md")
        try Data(#"{"schema_version":"reaction_session.v0.2","payload":"ok"}"#.utf8).write(to: jsonURL)
        try Data("ok".utf8).write(to: markdownURL)

        let savedExport = SavedExport(
            kind: .acceptance,
            directoryURL: directoryURL,
            jsonURL: jsonURL,
            markdownURL: markdownURL
        )
        let requestedAt = try XCTUnwrap(ISO8601DateFormatter().date(from: "2026-05-22T12:00:00Z"))
        let request = EvidenceUploadRequest(
            testerAlias: "trusted-alpha-test",
            savedExport: savedExport,
            requestedAt: requestedAt,
            sourceAppVersion: "0.2",
            sourceAppBuild: "2",
            termsVersion: "alpha_terms_2026_05_22",
            acceptedAt: requestedAt
        )

        let urlRequest = try client.makeURLRequest(request: request, accessToken: "session.jwt")
        XCTAssertEqual(urlRequest.value(forHTTPHeaderField: "apikey"), "sb_publishable_test")
        XCTAssertEqual(urlRequest.value(forHTTPHeaderField: "Authorization"), "Bearer session.jwt")
        XCTAssertEqual(urlRequest.url?.absoluteString, "https://example.supabase.co/functions/v1/submit-alpha-evidence")

        let body = try XCTUnwrap(urlRequest.httpBody)
        let object = try XCTUnwrap(JSONSerialization.jsonObject(with: body) as? [String: Any])
        XCTAssertEqual(object["artifact_type"] as? String, "reaction_session")
        XCTAssertEqual(object["schema_version"] as? String, "reaction_session.v0.2")
        let consent = try XCTUnwrap(object["consent"] as? [String: Any])
        XCTAssertEqual(consent["evidence_upload_allowed"] as? Bool, true)
        XCTAssertEqual(consent["terms_version"] as? String, "alpha_terms_2026_05_22")
        XCTAssertNotNil(object["payload"] as? [String: Any])
    }

    func testLiveDiagnosticUploadRequestUsesSessionBearerAndConsent() throws {
        let config = SupabaseAlphaConfig(
            projectURL: try XCTUnwrap(URL(string: "https://example.supabase.co")),
            anonKey: "sb_publishable_test",
            generateFirstMissionBatchFunctionName: "generate-first-mission-batch",
            enrichMissionFunctionName: "enrich-mission",
            submitAlphaEvidenceFunctionName: "submit-alpha-evidence",
            submitAlphaDiagnosticFunctionName: "submit-alpha-diagnostic",
            testerAlias: "trusted-alpha-test"
        )
        let client = LiveDiagnosticUploadClient(config: config)
        let directoryURL = FileManager.default.temporaryDirectory
            .appendingPathComponent("waymark-diagnostic-upload-test-\(UUID().uuidString)", isDirectory: true)
        try FileManager.default.createDirectory(at: directoryURL, withIntermediateDirectories: true)
        let artifactURL = directoryURL.appendingPathComponent("client_diag_mission_import_result.json")
        let requestedAt = try XCTUnwrap(ISO8601DateFormatter().date(from: "2026-05-24T12:00:00Z"))
        let artifact = """
        {
          "schema_version": "waymark.alpha_client_diagnostic_artifact.v0.1",
          "artifact_id": "client_diag:mission_import_result:request-1",
          "artifact_type": "mission_import_result",
          "tester_alias": "trusted-alpha-test",
          "survey_session_id": "survey-session-1",
          "client_request_id": "request-1",
          "generation_run_id": "00000000-0000-4000-8000-000000000001",
          "mission_id": "mission-1",
          "source_app_version": "0.2",
          "source_app_build": "8",
          "client_created_at": "2026-05-24T12:00:00Z",
          "redaction_level": "support_diagnostic",
          "payload": {
            "local_import_status": "imported",
            "imported_mission_ids": ["mission-1"]
          }
        }
        """
        try Data(artifact.utf8).write(to: artifactURL)
        let package = SavedClientDiagnosticPackage(
            directoryURL: directoryURL,
            indexURL: directoryURL.appendingPathComponent("index.json"),
            artifactURLs: [artifactURL]
        )
        let request = DiagnosticUploadRequest(
            testerAlias: "trusted-alpha-test",
            package: package,
            requestedAt: requestedAt,
            sourceAppVersion: "0.2",
            sourceAppBuild: "8",
            termsVersion: "alpha_privacy_terms_v0_1",
            acceptedAt: requestedAt
        )

        let urlRequest = try client.makeURLRequest(
            artifactURL: artifactURL,
            request: request,
            accessToken: "session.jwt"
        )
        XCTAssertEqual(urlRequest.value(forHTTPHeaderField: "apikey"), "sb_publishable_test")
        XCTAssertEqual(urlRequest.value(forHTTPHeaderField: "Authorization"), "Bearer session.jwt")
        XCTAssertEqual(urlRequest.url?.absoluteString, "https://example.supabase.co/functions/v1/submit-alpha-diagnostic")

        let body = try XCTUnwrap(urlRequest.httpBody)
        let object = try XCTUnwrap(JSONSerialization.jsonObject(with: body) as? [String: Any])
        XCTAssertEqual(object["client_artifact_id"] as? String, "client_diag:mission_import_result:request-1")
        XCTAssertEqual(object["artifact_type"] as? String, "mission_import_result")
        XCTAssertEqual(object["schema_version"] as? String, "waymark.alpha_client_diagnostic_artifact.v0.1")
        XCTAssertEqual(object["generation_run_id"] as? String, "00000000-0000-4000-8000-000000000001")
        XCTAssertEqual(object["upload_cadence"] as? String, "manual_share")
        let consent = try XCTUnwrap(object["consent"] as? [String: Any])
        XCTAssertEqual(consent["diagnostic_upload_allowed"] as? Bool, true)
        XCTAssertEqual(consent["terms_version"] as? String, "alpha_privacy_terms_v0_1")
        let payload = try XCTUnwrap(object["payload"] as? [String: Any])
        XCTAssertEqual(payload["local_import_status"] as? String, "imported")
    }

    func testLiveDiagnosticUploadRequestOmitsNonUUIDGenerationRunID() throws {
        let config = SupabaseAlphaConfig(
            projectURL: try XCTUnwrap(URL(string: "https://example.supabase.co")),
            anonKey: "sb_publishable_test",
            generateFirstMissionBatchFunctionName: "generate-first-mission-batch",
            enrichMissionFunctionName: "enrich-mission",
            submitAlphaEvidenceFunctionName: "submit-alpha-evidence",
            submitAlphaDiagnosticFunctionName: "submit-alpha-diagnostic",
            testerAlias: "trusted-alpha-test"
        )
        let client = LiveDiagnosticUploadClient(config: config)
        let directoryURL = FileManager.default.temporaryDirectory
            .appendingPathComponent("waymark-diagnostic-upload-local-run-id-test-\(UUID().uuidString)", isDirectory: true)
        try FileManager.default.createDirectory(at: directoryURL, withIntermediateDirectories: true)
        let artifactURL = directoryURL.appendingPathComponent("client_diag_local_selector.json")
        let requestedAt = try XCTUnwrap(ISO8601DateFormatter().date(from: "2026-05-24T12:00:00Z"))
        let artifact = """
        {
          "schema_version": "waymark.alpha_client_diagnostic_artifact.v0.1",
          "artifact_id": "client_diag:mission_generation_result:local-selector-run",
          "artifact_type": "mission_generation_result",
          "tester_alias": "trusted-alpha-test",
          "generation_run_id": "local-selector-run-2026-05-24",
          "source_app_version": "0.3",
          "source_app_build": "42",
          "client_created_at": "2026-05-24T12:00:00Z",
          "redaction_level": "support_diagnostic",
          "payload": {
            "generation_run_id": "local-selector-run-2026-05-24",
            "generation_run_id_context_omitted": "Local selector run ids are diagnostic strings, not Supabase UUIDs."
          }
        }
        """
        try Data(artifact.utf8).write(to: artifactURL)
        let package = SavedClientDiagnosticPackage(
            directoryURL: directoryURL,
            indexURL: directoryURL.appendingPathComponent("index.json"),
            artifactURLs: [artifactURL]
        )
        let request = DiagnosticUploadRequest(
            testerAlias: "trusted-alpha-test",
            package: package,
            requestedAt: requestedAt,
            sourceAppVersion: "0.3",
            sourceAppBuild: "42",
            termsVersion: "alpha_privacy_terms_v0_1",
            acceptedAt: requestedAt
        )

        let urlRequest = try client.makeURLRequest(
            artifactURL: artifactURL,
            request: request,
            accessToken: "session.jwt"
        )
        let body = try XCTUnwrap(urlRequest.httpBody)
        let object = try XCTUnwrap(JSONSerialization.jsonObject(with: body) as? [String: Any])
        XCTAssertNil(object["generation_run_id"])

        let payload = try XCTUnwrap(object["payload"] as? [String: Any])
        XCTAssertEqual(payload["generation_run_id"] as? String, "local-selector-run-2026-05-24")
    }

    func testAlphaLegacyDataQuarantineMovesKnownLocalStateRoots() throws {
        let rootURL = FileManager.default.temporaryDirectory
            .appendingPathComponent("waymark-alpha-quarantine-test-\(UUID().uuidString)", isDirectory: true)
        defer {
            try? FileManager.default.removeItem(at: rootURL)
        }

        let applicationSupportURL = rootURL.appendingPathComponent("Application Support", isDirectory: true)
        let documentURL = rootURL.appendingPathComponent("Documents", isDirectory: true)
        let appStateURL = applicationSupportURL.appendingPathComponent("MusicAtlasController", isDirectory: true)
        let exportStateURL = documentURL.appendingPathComponent("MusicAtlasControllerExports", isDirectory: true)
        try FileManager.default.createDirectory(at: appStateURL, withIntermediateDirectories: true)
        try FileManager.default.createDirectory(at: exportStateURL, withIntermediateDirectories: true)
        try Data("legacy app state".utf8)
            .write(to: appStateURL.appendingPathComponent("waymark_survey_session_v0_1.json"))
        try Data("legacy export state".utf8)
            .write(to: exportStateURL.appendingPathComponent("support.json"))

        let quarantine = AlphaLegacyDataQuarantine(
            applicationSupportURL: applicationSupportURL,
            documentURL: documentURL
        )
        let movedURLs = try quarantine.quarantineKnownLocalState(
            now: try XCTUnwrap(ISO8601DateFormatter().date(from: "2026-05-24T12:00:00Z"))
        )

        XCTAssertEqual(movedURLs.count, 2)
        XCTAssertFalse(FileManager.default.fileExists(atPath: appStateURL.path))
        XCTAssertFalse(FileManager.default.fileExists(atPath: exportStateURL.path))
        let destinationNames = Set(movedURLs.map(\.lastPathComponent))
        XCTAssertEqual(
            destinationNames,
            [
                "application_support_MusicAtlasController",
                "documents_MusicAtlasControllerExports"
            ]
        )
        let appStateArchive = try XCTUnwrap(movedURLs.first { $0.lastPathComponent == "application_support_MusicAtlasController" })
        let exportStateArchive = try XCTUnwrap(movedURLs.first { $0.lastPathComponent == "documents_MusicAtlasControllerExports" })
        XCTAssertTrue(FileManager.default.fileExists(atPath: appStateArchive.appendingPathComponent("waymark_survey_session_v0_1.json").path))
        XCTAssertTrue(FileManager.default.fileExists(atPath: exportStateArchive.appendingPathComponent("support.json").path))
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
