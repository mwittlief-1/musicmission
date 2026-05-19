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

    func testSurveyGridPagesStayWithinOneScreenLimit() throws {
        let steps: [SurveyStep] = [.artistPage1, .artistPage2, .artistPage3, .albumPage1, .songPage1]

        for step in steps {
            let page = try XCTUnwrap(SurveyFixtureLibrary.page(for: step, responses: [:]))
            XCTAssertLessThanOrEqual(page.items.count, SurveyFixtureLibrary.gridPageItemLimit)
        }
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
