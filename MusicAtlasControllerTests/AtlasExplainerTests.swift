import XCTest
@testable import MusicAtlasController

@MainActor
final class AtlasExplainerTests: XCTestCase {
    func testLoadsApprovedRenderPackBundle() throws {
        let library = try loadLibrary()

        XCTAssertEqual(library.packCount, 120)
        XCTAssertEqual(library.pack(archetypeID: "005")?.displayTitle, "Brill Building, Girl Group, and Early 60s Pop Craft")
        XCTAssertEqual(library.pack(archetypeID: "054")?.displayTitle, "CBGB, Art-Punk, and Downtown New York")
        XCTAssertEqual(library.pack(archetypeID: "082")?.displayTitle, "Techno / Detroit / Minimal Electronic")
    }

    func testRenderModulesArePresentForProofAndNonProofPacks() throws {
        let library = try loadLibrary()
        let packs = try [
            XCTUnwrap(library.pack(archetypeID: "005")),
            XCTUnwrap(library.pack(archetypeID: "054")),
            XCTUnwrap(library.pack(archetypeID: "082"))
        ]

        for pack in packs {
            XCTAssertFalse(pack.modules.atlasHomeRegionCard.standard.isEmpty)
            XCTAssertFalse(pack.modules.regionScenePage.standard.isEmpty)
            XCTAssertFalse(pack.modules.missionDetailHistoryModule.standard.isEmpty)
            XCTAssertFalse(pack.modules.didYouKnowCard.standard.isEmpty)
            XCTAssertFalse(pack.modules.whatToListenForPrompt.standard.isEmpty)
            XCTAssertFalse(pack.modules.relatedRoadsLineageModule.standard.isEmpty)
            XCTAssertFalse(pack.modules.deadEndFalseNearbyCautionModule.standard.isEmpty)
            XCTAssertFalse(pack.canonicalExamples.isEmpty)
        }
    }

    func testMissionDetailConsumerUsesExistingGraphRefsOnly() throws {
        let library = try loadLibrary()

        XCTAssertEqual(
            library.pack(matchingRouteRefs: ["song_recording:elvis-presley-all-shook-up"])?.identity.archetypeID,
            "001"
        )
        XCTAssertEqual(
            library.pack(matchingRouteRefs: ["route:track:song_recording:the-ronettes-be-my-baby"])?.identity.archetypeID,
            "005"
        )
        XCTAssertNil(library.pack(matchingRouteRefs: ["song_recording:synthetic-no-match"]))
    }

    func testMissionDetailMatchingPrefersSpecificRouteEvidence() throws {
        let library = try loadLibrary()

        XCTAssertEqual(
            library.pack(matchingRouteRefs: [
                "artist:artist-pink-floyd",
                "song_recording:song-money-1973"
            ])?.identity.archetypeID,
            "018"
        )
        XCTAssertEqual(
            library.pack(matchingRouteRefs: [
                "artist:black-sabbath",
                "song_recording:sleep-dragonaut"
            ])?.identity.archetypeID,
            "064"
        )
        XCTAssertEqual(
            library.pack(matchingRouteRefs: [
                "family_03/archetype_018",
                "artist:artist-led-zeppelin"
            ])?.identity.archetypeID,
            "018"
        )
    }

    func testMissingPersonalizationStateFallsBackCleanly() throws {
        let library = try loadLibrary()
        let pack = try XCTUnwrap(library.pack(archetypeID: "005"))
        let hook = try XCTUnwrap(pack.personalizationHooks.first)

        XCTAssertEqual(library.personalizationCopy(for: pack, state: .empty), hook.fallbackCopy)
    }

    func testUserFacingRenderCopyHasNoForbiddenMissionOrSourceLanguage() throws {
        let library = try loadLibrary()
        let forbiddenPhrases = [
            "generate mission from this node",
            "create a new mission",
            "launch arbitrary mission",
            "open a dynamic route from here",
            "ask ai to build a mission",
            "do not cite",
            "source-deepening",
            "graph-defined road",
            "draft road",
            "until pm",
            "atlas overlay",
            "copy depth",
            "repeated positive evidence",
            "stronger personal lane",
            "personalization"
        ]

        for text in library.userFacingStrings() {
            let lowercased = text.lowercased()
            for phrase in forbiddenPhrases {
                XCTAssertFalse(lowercased.contains(phrase), "Forbidden phrase '\(phrase)' found in: \(text)")
            }
        }
    }

    func testV02AlphaRenderingUsesFixedStandardCopyDepth() {
        XCTAssertEqual(AtlasExplainerRuntimePolicy.alphaCopyDepth, .standard)
    }

    func testExplainerRuntimeCopyHasNoFounderSpecificTasteData() throws {
        let library = try loadLibrary()
        let forbiddenFounderMarkers = [
            "matt wittlief",
            "matt_wittlief",
            "founder-specific",
            "founder taste",
            "founder profile"
        ]

        for text in library.userFacingStrings() {
            let lowercased = text.lowercased()
            for marker in forbiddenFounderMarkers {
                XCTAssertFalse(lowercased.contains(marker), "Founder-specific marker '\(marker)' found in: \(text)")
            }
        }
    }

    private func loadLibrary() throws -> AtlasExplainerLibrary {
        try AtlasExplainerStore.loadLibrary(bundle: Bundle(for: AtlasExplainerTests.self))
    }
}
