import XCTest
@testable import MusicAtlasController

final class MissionDecodingTests: XCTestCase {
    func testSampleMissionDecodes() throws {
        let mission = try loadSampleMission()

        XCTAssertEqual(mission.schemaVersion, "mission.v0.2")
        XCTAssertEqual(mission.missionID, "MIS_LOVE_TRIBUTARIES_V02_SPIKE")
        XCTAssertEqual(mission.items.count, 4)
        XCTAssertEqual(mission.successBar.minimumItemsToResolve, 1)
        XCTAssertTrue(mission.successBar.requiresPhysicalIPhone)
        XCTAssertEqual(mission.items.first?.itemID, "ITEM_LOVE_A_HOUSE_IS_NOT_A_MOTEL")
        XCTAssertEqual(mission.items.first?.appleMusicResolution.status, .unresolved)
    }

    func testLithuanianAlphaMissionDecodesContextualFeedback() throws {
        let mission = try loadLithuanianAlphaMission()

        XCTAssertEqual(mission.missionID, "MIS_LITHUANIAN_DISCOVERY_BALTIC_PRESSURE_V01_ALPHA")
        XCTAssertEqual(mission.items.count, 14)
        XCTAssertEqual(mission.runInstructions?.listenInOrder, true)
        XCTAssertEqual(mission.runInstructions?.shuffleAllowed, false)

        let firstItem = try XCTUnwrap(mission.items.first)
        XCTAssertEqual(firstItem.title, "Netildai")
        XCTAssertEqual(firstItem.playerCard?.flipSide?.songHypothesis, "Does this open a Lithuanian dark-post-punk/electronic-rock lane?")
        XCTAssertEqual(firstItem.feedbackChips(for: .hit).map(\.label), [
            "dark pull",
            "body + gloom",
            "opens lane"
        ])
        XCTAssertEqual(firstItem.feedbackChips(for: .miss).map(\.label), [
            "too electronic?",
            "good but not me"
        ])
    }

    func testPersonalMissionPackDecodes() throws {
        let missions = try loadPersonalMissionPack()

        XCTAssertEqual(missions.count, 10)
        XCTAssertEqual(missions.first?.missionID, "MIS_LOST_NIRVANA_TIMELINE")

        let firstMission = try XCTUnwrap(missions.first)
        XCTAssertEqual(firstMission.items.count, 12)
        XCTAssertTrue(firstMission.items.allSatisfy { $0.playerCard?.flipSide?.songHypothesis?.isEmpty == false })
        XCTAssertTrue(firstMission.items.allSatisfy { item in
            !item.feedbackChips(for: .hit).isEmpty &&
            !item.feedbackChips(for: .partial).isEmpty &&
            !item.feedbackChips(for: .okShelf).isEmpty &&
            !item.feedbackChips(for: .miss).isEmpty
        })
    }

    func testLocalMissionProviderImportsAppImportCandidateResponse() throws {
        let importedAt = try XCTUnwrap(ISO8601DateFormatter().date(from: "2026-05-21T12:00:00Z"))
        let mission = try loadLithuanianAlphaMission()
        let provider = try makeImportTestProvider()
        let response = TestGenerationResponse(
            run_id: "run_alpha_001",
            status: "app_import_candidate",
            app_missions: [mission]
        )
        let data = try JSONEncoder.missionTestEncoder.encode(response)

        let imported = try provider.importSupabaseMissionBatchResponseData(data, importedAt: importedAt)
        let catalog = try provider.loadMissionCatalog()

        XCTAssertEqual(imported.count, 1)
        XCTAssertEqual(imported.first?.mission.missionID, mission.missionID)
        XCTAssertEqual(imported.first?.source, .generatedReviewed)
        XCTAssertEqual(imported.first?.sourceRunID, "run_alpha_001")
        XCTAssertEqual(catalog.reviewedAssignments.count, 1)
        XCTAssertTrue(catalog.debugAssignments.isEmpty)
    }

    func testLocalSupabaseMissionClientStubReturnsAppImportCandidateShape() async throws {
        let mission = try loadLithuanianAlphaMission()
        let provider = try makeImportTestProvider()
        let response = TestGenerationResponse(
            run_id: "run_alpha_stub_001",
            status: "app_import_candidate",
            app_missions: [mission]
        )
        let responseData = try JSONEncoder.missionTestEncoder.encode(response)
        let client = LocalSupabaseMissionClientStub(responseData: responseData)
        let request = MissionGenerationRequest(
            clientRequestID: "client_request_local_001",
            testerAlias: "trusted_alpha_local",
            requestedBatchSize: 3,
            surveyEvidenceExport: Data(#"{"schema_version":"survey"}"#.utf8),
            missionGenerationDigestView: Data(#"{"schema_version":"digest"}"#.utf8),
            candidatePool: Data(#"{"candidates":[]}"#.utf8),
            promptContext: MissionGenerationPromptContext(
                alphaScope: "first_batch_after_required_survey",
                generationMode: "local_stub",
                sourceAppVersion: "0.2",
                sourceAppBuild: "2",
                storefront: "us",
                surveyPageCount: SurveyPageCount(artist: 4, album: 2, song: 4)
            )
        )

        let generatedData = try await client.generateFirstMissionBatch(request: request, accessToken: "local.jwt")
        let imported = try provider.importSupabaseMissionBatchResponseData(generatedData)

        XCTAssertEqual(imported.count, 1)
        XCTAssertEqual(imported.first?.source, .generatedReviewed)
        XCTAssertEqual(imported.first?.sourceRunID, "run_alpha_stub_001")
    }

    func testLocalMissionProviderRejectsNonCandidateGenerationStatus() throws {
        let mission = try loadLithuanianAlphaMission()
        let provider = try makeImportTestProvider()
        let response = TestGenerationResponse(
            run_id: "run_alpha_002",
            status: "review_needed",
            app_missions: [mission]
        )
        let data = try JSONEncoder.missionTestEncoder.encode(response)

        XCTAssertThrowsError(try provider.importSupabaseMissionBatchResponseData(data)) { error in
            XCTAssertEqual(error as? MissionImportError, .blockedStatus("review_needed"))
        }

        XCTAssertTrue(try provider.loadMissionCatalog().reviewedAssignments.isEmpty)
    }

    func testMissionImportGateRejectsPreResolvedMissionEvidence() throws {
        let mission = try loadLithuanianAlphaMission()
        let provider = try makeImportTestProvider()
        let data = try makeMissionDataWithFirstItemResolutionStatus(mission, status: "resolved")

        XCTAssertThrowsError(try provider.importReviewedMissionData(data, source: .manualReviewed, importedAt: Date())) { error in
            guard case .invalidMission(let reason) = error as? MissionImportError else {
                XCTFail("Expected invalidMission import error, got \(error)")
                return
            }
            XCTAssertTrue(reason.contains("must enter the app unresolved"))
        }
    }

    func testMissionImportGateRequiresExpectedSignalAndPlayerCard() throws {
        let mission = try loadLithuanianAlphaMission()
        let provider = try makeImportTestProvider()
        let data = try makeMissionDataWithFirstItemField(mission, field: "expected_test_signal", value: "")

        XCTAssertThrowsError(try provider.importReviewedMissionData(data, source: .manualReviewed, importedAt: Date())) { error in
            guard case .invalidMission(let reason) = error as? MissionImportError else {
                XCTFail("Expected invalidMission import error, got \(error)")
                return
            }
            XCTAssertTrue(reason.contains("expected_test_signal"))
        }
    }

    func testLocalMissionProviderResetClearsReviewedAssignments() throws {
        let mission = try loadLithuanianAlphaMission()
        let provider = try makeImportTestProvider()
        let data = try JSONEncoder.missionTestEncoder.encode(mission)

        XCTAssertEqual(try provider.importReviewedMissionData(data, source: .manualReviewed).count, 1)
        XCTAssertEqual(try provider.loadMissionCatalog().reviewedAssignments.count, 1)

        try provider.resetReviewedAssignments()

        XCTAssertTrue(try provider.loadMissionCatalog().reviewedAssignments.isEmpty)
    }

    @MainActor
    func testAppModelStartsMissionlessWhenNoReviewedOrDebugAssignments() {
        let provider = LocalMissionProvider(
            reviewedMissionStore: .disabled,
            includeDebugBundledMissions: false
        )
        let appModel = AppModel(
            sessionPersistenceStore: .disabled,
            missionProvider: provider
        )

        appModel.loadMissionLibrary()

        XCTAssertEqual(appModel.missionLoadState, .loaded)
        XCTAssertTrue(appModel.availableMissions.isEmpty)
        XCTAssertNil(appModel.mission)
    }

    @MainActor
    func testAlphaMissionlessImportListenRelaunchExportFlow() async throws {
        let tempDirectory = FileManager.default.temporaryDirectory
            .appendingPathComponent("waymark_alpha_smoke_tests", isDirectory: true)
            .appendingPathComponent(UUID().uuidString, isDirectory: true)
        defer {
            try? FileManager.default.removeItem(at: tempDirectory)
        }

        let provider = LocalMissionProvider(
            reviewedMissionStore: ReviewedMissionStore(baseDirectoryURL: tempDirectory),
            includeDebugBundledMissions: false
        )
        let persistenceStore = SessionPersistenceStore(baseDirectoryURL: tempDirectory)
        let exportStore = ExportFileStore(baseDirectoryURL: tempDirectory)
        let appModel = AppModel(
            exportFileStore: exportStore,
            sessionPersistenceStore: persistenceStore,
            missionProvider: provider
        )
        appModel.loadMissionLibrary()

        XCTAssertNil(appModel.mission)
        XCTAssertTrue(appModel.availableMissions.isEmpty)

        let mission = try loadLithuanianAlphaMission()
        let response = TestGenerationResponse(
            run_id: "run_alpha_smoke_001",
            status: "app_import_candidate",
            app_missions: [mission]
        )
        let responseData = try JSONEncoder.missionTestEncoder.encode(response)
        let responseJSON = try XCTUnwrap(String(data: responseData, encoding: .utf8))

        appModel.importSupabaseMissionBatchResponseJSON(responseJSON)

        let selectedItem = try XCTUnwrap(appModel.selectedItem)
        XCTAssertEqual(appModel.mission?.missionID, mission.missionID)
        XCTAssertEqual(selectedItem.sequence, 1)

        await appModel.resolveSelectedItemWithStub()
        _ = await appModel.playSelectedItem()
        appModel.saveReactionForSelectedItem(
            value: .hit,
            note: "alpha smoke note",
            selectedTags: selectedItem.feedbackChips(for: .hit).prefix(1).map {
                $0.reactionTag(primaryReactionValue: .hit)
            }
        )

        let restoredModel = AppModel(
            exportFileStore: exportStore,
            sessionPersistenceStore: persistenceStore,
            missionProvider: provider
        )
        restoredModel.loadMissionLibrary()

        XCTAssertEqual(restoredModel.mission?.missionID, mission.missionID)
        XCTAssertEqual(restoredModel.selectedItem?.itemID, selectedItem.itemID)
        XCTAssertEqual(restoredModel.resolution(for: selectedItem).status, .resolved)
        XCTAssertEqual(restoredModel.reaction(for: selectedItem)?.notes.text, "alpha smoke note")

        restoredModel.generateDevelopmentExportPreview()
        restoredModel.saveCurrentExportFiles()

        XCTAssertNotNil(restoredModel.savedExport)
        XCTAssertEqual(restoredModel.savedExports.count, 1)

        let restoredAfterExport = AppModel(
            exportFileStore: exportStore,
            sessionPersistenceStore: persistenceStore,
            missionProvider: provider
        )
        restoredAfterExport.loadMissionLibrary()

        XCTAssertEqual(restoredAfterExport.savedExports.count, 1)
        XCTAssertEqual(restoredAfterExport.savedExport?.jsonURL.lastPathComponent, restoredModel.savedExport?.jsonURL.lastPathComponent)
    }


    func testStubResolverProducesSchemaCompatibleResolution() async throws {
        let mission = try loadSampleMission()
        let item = try XCTUnwrap(mission.items.first)
        let now = try XCTUnwrap(ISO8601DateFormatter().date(from: "2026-05-17T12:00:00Z"))

        let resolution = try await StubMusicSearchService().resolve(item: item, at: now)

        XCTAssertEqual(resolution.status, .resolved)
        XCTAssertEqual(resolution.catalogID, "stub_item_love_a_house_is_not_a_motel")
        XCTAssertEqual(resolution.resolvedTitle, "A House Is Not a Motel")
        XCTAssertEqual(resolution.resolvedArtist, "Love")
        XCTAssertEqual(resolution.resolver, .system)
        XCTAssertEqual(resolution.candidateCount, 1)
        XCTAssertEqual(resolution.storefront, "dev_stub")
    }

    func testStubPlaybackRequiresResolvedResolution() async throws {
        let now = try XCTUnwrap(ISO8601DateFormatter().date(from: "2026-05-17T12:00:00Z"))
        let playbackService = StubMusicPlaybackService()

        let failedPlayback = await playbackService.play(resolution: .unresolved(), at: now)

        XCTAssertEqual(failedPlayback.status, .failed)
        XCTAssertEqual(failedPlayback.errorCode, "stub_playback_requires_resolved_item")

        let mission = try loadSampleMission()
        let item = try XCTUnwrap(mission.items.first)
        let resolution = try await StubMusicSearchService().resolve(item: item, at: now)

        let simulatedPlayback = await playbackService.play(resolution: resolution, at: now)

        XCTAssertEqual(simulatedPlayback.status, .played)
        XCTAssertEqual(simulatedPlayback.attemptedAt, now)
        XCTAssertEqual(simulatedPlayback.durationSeconds, 0)
    }

    func testPlaybackControlsFinishStartedPlaybackAsPlayedEvidence() async throws {
        let startedAt = try XCTUnwrap(ISO8601DateFormatter().date(from: "2026-05-17T12:00:00Z"))
        let stoppedAt = try XCTUnwrap(ISO8601DateFormatter().date(from: "2026-05-17T12:00:30Z"))
        let playing = PlaybackRecord(
            status: .playing,
            attemptedAt: startedAt,
            startedAt: startedAt,
            endedAt: nil,
            durationSeconds: nil,
            errorCode: nil,
            errorMessage: nil
        )

        let stopped = await StubMusicPlaybackService().stop(currentPlayback: playing, at: stoppedAt)

        XCTAssertEqual(stopped.status, .played)
        XCTAssertEqual(stopped.startedAt, startedAt)
        XCTAssertEqual(stopped.endedAt, stoppedAt)
        XCTAssertEqual(stopped.durationSeconds, 30)
    }
}

func loadSampleMission(file: StaticString = #filePath, line: UInt = #line) throws -> Mission {
    try loadMissionResource("sample_mission_love_tributaries_v0_2", file: file, line: line)
}

func loadLithuanianAlphaMission(file: StaticString = #filePath, line: UInt = #line) throws -> Mission {
    try loadMissionResource("sample_mission_lithuanian_discovery_v0_3_alpha", file: file, line: line)
}

func loadPersonalMissionPack(file: StaticString = #filePath, line: UInt = #line) throws -> [Mission] {
    let bundle = Bundle(for: TestBundleMarker.self)
    guard let url = bundle.url(forResource: "waymark_matt_10_personal_missions_v0_1", withExtension: "json") else {
        XCTFail("Missing waymark_matt_10_personal_missions_v0_1 test resource", file: file, line: line)
        throw TestResourceError.missingSampleMission
    }

    let data = try Data(contentsOf: url)
    let decoder = JSONDecoder()
    decoder.dateDecodingStrategy = .iso8601
    return try decoder.decode([Mission].self, from: data)
}

private func loadMissionResource(_ resourceName: String, file: StaticString = #filePath, line: UInt = #line) throws -> Mission {
    let bundle = Bundle(for: TestBundleMarker.self)
    guard let url = bundle.url(forResource: resourceName, withExtension: "json") else {
        XCTFail("Missing \(resourceName) test resource", file: file, line: line)
        throw TestResourceError.missingSampleMission
    }

    let data = try Data(contentsOf: url)
    let decoder = JSONDecoder()
    decoder.dateDecodingStrategy = .iso8601
    return try decoder.decode(Mission.self, from: data)
}

private func makeImportTestProvider() throws -> LocalMissionProvider {
    let directoryURL = FileManager.default.temporaryDirectory
        .appendingPathComponent("waymark_import_provider_tests", isDirectory: true)
        .appendingPathComponent(UUID().uuidString, isDirectory: true)
    try FileManager.default.createDirectory(at: directoryURL, withIntermediateDirectories: true)

    return LocalMissionProvider(
        reviewedMissionStore: ReviewedMissionStore(baseDirectoryURL: directoryURL),
        includeDebugBundledMissions: false
    )
}

private func makeMissionDataWithFirstItemResolutionStatus(_ mission: Mission, status: String) throws -> Data {
    let data = try JSONEncoder.missionTestEncoder.encode(mission)
    guard var object = try JSONSerialization.jsonObject(with: data) as? [String: Any],
          var items = object["items"] as? [[String: Any]],
          !items.isEmpty,
          var resolution = items[0]["apple_music_resolution"] as? [String: Any] else {
        throw TestResourceError.malformedMissionJSON
    }

    resolution["status"] = status
    items[0]["apple_music_resolution"] = resolution
    object["items"] = items
    return try JSONSerialization.data(withJSONObject: object)
}

private func makeMissionDataWithFirstItemField(_ mission: Mission, field: String, value: Any?) throws -> Data {
    let data = try JSONEncoder.missionTestEncoder.encode(mission)
    guard var object = try JSONSerialization.jsonObject(with: data) as? [String: Any],
          var items = object["items"] as? [[String: Any]],
          !items.isEmpty else {
        throw TestResourceError.malformedMissionJSON
    }

    items[0][field] = value
    object["items"] = items
    return try JSONSerialization.data(withJSONObject: object)
}

private struct TestGenerationResponse: Encodable {
    let run_id: String?
    let status: String
    let app_missions: [Mission]
}

private extension JSONEncoder {
    static var missionTestEncoder: JSONEncoder {
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        encoder.outputFormatting = [.sortedKeys]
        return encoder
    }
}

struct TestMissionProvider: MissionProviding {
    private let assignments: [MissionAssignment]

    init(missions: [Mission]) {
        self.assignments = missions.map {
            MissionAssignment(
                mission: $0,
                source: .manualReviewed,
                importedAt: $0.createdAt,
                sourceRunID: nil,
                importNote: "Unit test mission fixture"
            )
        }
    }

    func loadMissionCatalog() throws -> MissionCatalog {
        MissionCatalog(reviewedAssignments: assignments, debugAssignments: [])
    }

    func importReviewedMissionData(_ data: Data, source: MissionAssignmentSource, importedAt: Date) throws -> [MissionAssignment] {
        assignments
    }

    func importSupabaseMissionBatchResponseData(_ data: Data, importedAt: Date) throws -> [MissionAssignment] {
        assignments
    }

    func resetReviewedAssignments() throws {}
}

private final class TestBundleMarker {}

private enum TestResourceError: Error {
    case missingSampleMission
    case malformedMissionJSON
}
