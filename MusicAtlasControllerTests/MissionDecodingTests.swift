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

private final class TestBundleMarker {}

private enum TestResourceError: Error {
    case missingSampleMission
}
