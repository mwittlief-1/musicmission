import XCTest
@testable import MusicAtlasController

@MainActor
final class SurveyTests: XCTestCase {
    func testSurveyStateCycleUsesFiveStates() {
        XCTAssertEqual(SurveySignalState.dontKnow.next, .fine)
        XCTAssertEqual(SurveySignalState.fine.next, .like)
        XCTAssertEqual(SurveySignalState.like.next, .favorite)
        XCTAssertEqual(SurveySignalState.favorite.next, .notForMe)
        XCTAssertEqual(SurveySignalState.notForMe.next, .dontKnow)
    }

    func testArtistPageOneIsAppleMusicHeavyTwelveItemSeed() throws {
        let page = try XCTUnwrap(SurveyFixtureLibrary.page(for: .artistPage1, responses: [:]))

        XCTAssertEqual(page.items.count, SurveyFixtureLibrary.gridPageItemLimit)
        XCTAssertEqual(page.kind, .artist)
        XCTAssertEqual(page.items.filter { $0.source == .appleMusicDerived }.count, 8)
        XCTAssertTrue(page.items.contains { $0.source == .broadCalibration })
        XCTAssertTrue(page.items.contains { $0.source == .sleeperProbe })
        XCTAssertTrue(page.items.contains { $0.source == .rejectionProbe })
    }

    func testAlphaSurveyGridPagesStayWithinOneScreenLimit() throws {
        let steps: [SurveyStep] = [
            .artistPage1,
            .artistPage2,
            .artistPage3,
            .artistPage4,
            .albumPage1,
            .albumPage2,
            .songPage1,
            .songPage2,
            .songPage3,
            .songPage4
        ]

        for step in steps {
            let page = try XCTUnwrap(SurveyFixtureLibrary.page(for: step, responses: [:]))
            XCTAssertLessThanOrEqual(page.items.count, SurveyFixtureLibrary.gridPageItemLimit)
        }
    }

    func testRequiredAlphaSurveyPagesDoNotRepeatWithinObjectType() throws {
        let objectStepGroups: [[SurveyStep]] = [
            [.artistPage1, .artistPage2, .artistPage3, .artistPage4],
            [.albumPage1, .albumPage2],
            [.songPage1, .songPage2, .songPage3, .songPage4]
        ]

        for steps in objectStepGroups {
            var seenIDs = Set<String>()
            for step in steps {
                let page = try XCTUnwrap(SurveyFixtureLibrary.page(for: step, responses: [:]))
                let ids = page.items.map(\.id)
                XCTAssertEqual(ids.count, Set(ids).count, "\(step.rawValue) contains duplicate items.")
                XCTAssertTrue(seenIDs.isDisjoint(with: ids), "\(step.rawValue) repeats items from an earlier page.")
                seenIDs.formUnion(ids)
            }
        }
    }

    func testFirstMissionCandidatePoolUsesArchetypeCandidatesNotSurveyTiles() throws {
        let tempDirectory = FileManager.default.temporaryDirectory
            .appendingPathComponent("survey-candidate-pool-\(UUID().uuidString)", isDirectory: true)
        defer {
            try? FileManager.default.removeItem(at: tempDirectory)
        }

        let persistenceStore = SurveyPersistenceStore(baseDirectoryURL: tempDirectory)
        let store = SurveyStore(persistenceStore: persistenceStore)
        store.prepareRequiredAlphaIntake()

        let page = try XCTUnwrap(SurveyFixtureLibrary.page(for: .songPage1, responses: [:]))
        let surveySong = try XCTUnwrap(page.items.first)
        store.setState(.favorite, for: surveySong)

        let builder = SurveyEvidenceExportBuilder(persistenceStore: persistenceStore)
        let poolData = try builder.makeCandidatePoolData(session: persistenceStore.load())
        let pool = try XCTUnwrap(JSONSerialization.jsonObject(with: poolData) as? [String: Any])
        let candidates = try XCTUnwrap(pool["candidates"] as? [[String: Any]])

        XCTAssertEqual(pool["schema_version"] as? String, "waymark.candidate_pool.v0.1")
        XCTAssertGreaterThan(candidates.count, 0)
        XCTAssertNotEqual(pool["pool_id"] as? String, "app_local_survey_candidate_pool_alpha1")
        XCTAssertFalse(candidates.contains { $0["source_item_id"] != nil })
        XCTAssertFalse(candidates.contains { $0["candidate_id"] as? String == "APP_SURVEY_001" })

        let encodedPool = String(data: poolData, encoding: .utf8) ?? ""
        XCTAssertFalse(encodedPool.localizedCaseInsensitiveContains("nirvana_to_current"))
        XCTAssertFalse(encodedPool.localizedCaseInsensitiveContains("lithuanian_artists_frontier"))
        XCTAssertFalse(encodedPool.localizedCaseInsensitiveContains("candidate_pool_nirvana"))
    }

    func testFirstMissionPortfolioUsesGenericAtlasSignalSlots() throws {
        let tempDirectory = FileManager.default.temporaryDirectory
            .appendingPathComponent("survey-generic-mission-planner-\(UUID().uuidString)", isDirectory: true)
        defer {
            try? FileManager.default.removeItem(at: tempDirectory)
        }

        let persistenceStore = SurveyPersistenceStore(baseDirectoryURL: tempDirectory)
        let store = SurveyStore(persistenceStore: persistenceStore)
        store.prepareRequiredAlphaIntake()

        let page = try XCTUnwrap(SurveyFixtureLibrary.page(for: .artistPage1, responses: [:]))
        let positive = try XCTUnwrap(page.items.first { $0.title == "Nirvana" })
        store.setState(.favorite, for: positive)

        let builder = SurveyEvidenceExportBuilder(persistenceStore: persistenceStore)
        let request = try builder.makeFirstMissionGenerationRequest(
            testerAlias: "unit-test",
            sourceAppVersion: "test",
            sourceAppBuild: "test",
            batchMissionIndex: 1,
            batchMissionTotal: 10
        )

        XCTAssertEqual(request.promptContext.generationMode, "live_app_generation_atlas_signal_constrained")
        XCTAssertEqual(request.promptContext.missionPortfolioSlot, "safe_anchor")
        XCTAssertEqual(request.promptContext.missionRequestID, "safe_anchor_01")
        XCTAssertFalse((request.promptContext.sourceCandidatePoolID ?? "").localizedCaseInsensitiveContains("nirvana"))
    }

    func testAlphaSurveyStoreForcedIntakeSequence() throws {
        let store = SurveyStore(persistenceStore: .disabled)
        store.prepareRequiredAlphaIntake()

        XCTAssertEqual(store.currentStep, .artistPage1)

        let expectedSteps: [SurveyStep] = [
            .artistPage2,
            .artistPage3,
            .artistPage4,
            .albumPage1,
            .albumPage2,
            .songPage1,
            .songPage2,
            .songPage3,
            .songPage4,
            .readout
        ]

        for expectedStep in expectedSteps {
            store.advance()
            XCTAssertEqual(store.currentStep, expectedStep)
        }
    }

    func testRequiredAlphaIntakeClearsPersistedPriorResponses() throws {
        let tempDirectory = FileManager.default.temporaryDirectory
            .appendingPathComponent("survey-required-intake-\(UUID().uuidString)", isDirectory: true)
        defer {
            try? FileManager.default.removeItem(at: tempDirectory)
        }

        let persistenceStore = SurveyPersistenceStore(baseDirectoryURL: tempDirectory)
        let page = try XCTUnwrap(SurveyFixtureLibrary.page(for: .artistPage1, responses: [:]))
        let item = try XCTUnwrap(page.items.first)
        let previousStore = SurveyStore(persistenceStore: persistenceStore)
        previousStore.setState(.favorite, for: item)
        previousStore.addFreeformSignal("carryover should clear")
        previousStore.goTo(.albumPage2)

        let requiredStore = SurveyStore(persistenceStore: persistenceStore)
        requiredStore.prepareRequiredAlphaIntake()

        XCTAssertEqual(requiredStore.currentStep, .artistPage1)
        XCTAssertEqual(requiredStore.state(for: item), .dontKnow)
        XCTAssertTrue(requiredStore.freeformSignals.isEmpty)
        XCTAssertEqual(requiredStore.makeSummary().visibleSignalCount, 0)
    }

    func testSurveyStorePersistsResponsesAndFreeformSignals() throws {
        let tempDirectory = FileManager.default.temporaryDirectory
            .appendingPathComponent("survey-store-\(UUID().uuidString)", isDirectory: true)
        let persistenceStore = SurveyPersistenceStore(baseDirectoryURL: tempDirectory)
        let store = SurveyStore(persistenceStore: persistenceStore)
        let page = try XCTUnwrap(SurveyFixtureLibrary.page(for: .artistPage1, responses: [:]))
        let item = try XCTUnwrap(page.items.first)
        let now = try XCTUnwrap(ISO8601DateFormatter().date(from: "2026-05-18T12:00:00Z"))

        store.setState(.favorite, for: item, at: now)
        store.toggleNuance(.oneAlbumOnly, for: item, at: now)
        store.updateNote(" only the early records ", for: item, at: now)
        store.addFreeformSignal("I like some pop if it has bite.", at: now)
        store.goTo(.artistPage2)

        let restoredStore = SurveyStore(persistenceStore: persistenceStore)

        XCTAssertEqual(restoredStore.currentStep, .artistPage2)
        XCTAssertEqual(restoredStore.state(for: item), .favorite)
        XCTAssertEqual(restoredStore.nuances(for: item), [.oneAlbumOnly])
        XCTAssertEqual(restoredStore.note(for: item), "only the early records")
        XCTAssertEqual(restoredStore.freeformSignals.first?.confidence, "user_asserted")
        XCTAssertEqual(restoredStore.freeformSignals.first?.requiresConfirmation, true)
    }

    func testAdvancedLibraryUnratedExcludesAnsweredItems() throws {
        let answeredItem = try XCTUnwrap(SurveyFixtureLibrary.page(for: .artistPage1, responses: [:])?.items.first)
        let response = SurveyResponse(
            itemID: answeredItem.id,
            itemKind: answeredItem.kind,
            state: .like,
            nuances: [],
            note: "",
            updatedAt: Date()
        )

        let page = SurveyFixtureLibrary.advancedPage(
            for: .libraryUnrated,
            responses: [answeredItem.id: response]
        )

        XCTAssertFalse(page.items.contains(answeredItem))
        XCTAssertLessThanOrEqual(page.items.count, SurveyFixtureLibrary.gridPageItemLimit)
    }
}
