import XCTest
@testable import MusicAtlasController

@MainActor
final class AtlasExplainerTests: XCTestCase {
    func testLoadsApprovedRenderPackBundle() throws {
        let library = try loadLibrary()

        XCTAssertEqual(library.sourcePackage, "AtlasExplainerPack_v0_3_ProfileLadders")
        XCTAssertEqual(library.packCount, 120)
        XCTAssertLessThanOrEqual(library.homePackCount, AtlasExplainerRuntimePolicy.alphaHomePackLimit)
        XCTAssertEqual(library.pack(archetypeID: "005")?.displayTitle, "Brill Building, Girl Group, and Early 60s Pop Craft")
        XCTAssertEqual(library.pack(archetypeID: "054")?.displayTitle, "CBGB, Art-Punk, and Downtown New York")
        XCTAssertEqual(library.pack(archetypeID: "082")?.displayTitle, "Techno / Detroit / Minimal Electronic")
    }

    func testAtlasHomeFallbackUsesThreeCappedSurveyLikeGroups() throws {
        let library = try loadLibrary()
        let sections = library.homeSections

        XCTAssertEqual(sections.map(\.kind), [.likelyRegions, .frontiers, .boundaries])
        XCTAssertLessThanOrEqual(library.homePackCount, AtlasExplainerRuntimePolicy.alphaHomePackLimit)
        XCTAssertEqual(
            sections.first { $0.kind == .likelyRegions }?.packs.map(\.identity.archetypeID),
            ["070", "069", "075"]
        )
        XCTAssertEqual(
            sections.first { $0.kind == .frontiers }?.packs.map(\.identity.archetypeID),
            ["016", "017", "061"]
        )
        XCTAssertEqual(
            sections.first { $0.kind == .boundaries }?.packs.map(\.identity.archetypeID),
            ["059", "056", "060"]
        )
    }

    func testAtlasHomeUsesFinalSurveyScoreBucketsAndCapsAtTen() throws {
        let library = try loadLibrary().withScoredArchetypes([
            AtlasSurveyArchetypeScore(archetypeID: "070", positiveScore: 28, fineScore: 0, unknownScore: 0, negativeScore: 0, surveySignalCount: 9),
            AtlasSurveyArchetypeScore(archetypeID: "069", positiveScore: 18, fineScore: 1, unknownScore: 0, negativeScore: 0, surveySignalCount: 7),
            AtlasSurveyArchetypeScore(archetypeID: "075", positiveScore: 12, fineScore: 0, unknownScore: 0, negativeScore: 0, surveySignalCount: 5),
            AtlasSurveyArchetypeScore(archetypeID: "016", positiveScore: 8, fineScore: 0, unknownScore: 0, negativeScore: 0, surveySignalCount: 4),
            AtlasSurveyArchetypeScore(archetypeID: "017", positiveScore: 3, fineScore: 1, unknownScore: 0, negativeScore: 0, surveySignalCount: 4),
            AtlasSurveyArchetypeScore(archetypeID: "061", positiveScore: 2.5, fineScore: 0, unknownScore: 0, negativeScore: 0, surveySignalCount: 4),
            AtlasSurveyArchetypeScore(archetypeID: "056", positiveScore: 1, fineScore: 4, unknownScore: 0.35, negativeScore: 0, surveySignalCount: 6),
            AtlasSurveyArchetypeScore(archetypeID: "059", positiveScore: 3, fineScore: 2, unknownScore: 0, negativeScore: 4, surveySignalCount: 6),
            AtlasSurveyArchetypeScore(archetypeID: "060", positiveScore: 2, fineScore: 0, unknownScore: 1.4, negativeScore: 0, surveySignalCount: 5),
            AtlasSurveyArchetypeScore(archetypeID: "064", positiveScore: 1, fineScore: 0, unknownScore: 0, negativeScore: 8, surveySignalCount: 4),
            AtlasSurveyArchetypeScore(archetypeID: "080", positiveScore: 2, fineScore: 0, unknownScore: 0, negativeScore: 0, surveySignalCount: 4),
            AtlasSurveyArchetypeScore(archetypeID: "081", positiveScore: 1.5, fineScore: 0, unknownScore: 0, negativeScore: 0, surveySignalCount: 4)
        ])

        let sections = library.homeSections
        let likely = sections.first { $0.kind == .likelyRegions }?.packs.map(\.identity.archetypeID)
        let frontiers = sections.first { $0.kind == .frontiers }?.packs.map(\.identity.archetypeID)
        let openQuestions = sections.first { $0.kind == .boundaries }?.packs.map(\.identity.archetypeID)
        let totalVisible = sections.reduce(0) { $0 + $1.packs.count }

        XCTAssertEqual(sections.map(\.kind), [.likelyRegions, .frontiers, .boundaries])
        XCTAssertLessThanOrEqual(totalVisible, AtlasExplainerRuntimePolicy.alphaHomePackLimit)
        XCTAssertEqual(likely, ["070", "069", "075", "016"])
        XCTAssertTrue(frontiers?.contains("017") == true)
        XCTAssertTrue(frontiers?.contains("061") == true)
        XCTAssertEqual(openQuestions, ["064", "059", "056"])
    }

    func testAtlasHomeRoutesSparseTopScoresToOpenQuestions() throws {
        let library = try loadLibrary().withScoredArchetypes([
            AtlasSurveyArchetypeScore(archetypeID: "070", positiveScore: 28, fineScore: 0, unknownScore: 0, negativeScore: 0, surveySignalCount: 3),
            AtlasSurveyArchetypeScore(archetypeID: "069", positiveScore: 18, fineScore: 0, unknownScore: 0, negativeScore: 0, surveySignalCount: 7),
            AtlasSurveyArchetypeScore(archetypeID: "075", positiveScore: 12, fineScore: 0, unknownScore: 0, negativeScore: 0, surveySignalCount: 5),
            AtlasSurveyArchetypeScore(archetypeID: "016", positiveScore: 8, fineScore: 0, unknownScore: 0, negativeScore: 0, surveySignalCount: 4),
            AtlasSurveyArchetypeScore(archetypeID: "017", positiveScore: 6, fineScore: 0, unknownScore: 0, negativeScore: 0, surveySignalCount: 4),
            AtlasSurveyArchetypeScore(archetypeID: "061", positiveScore: 5, fineScore: 0, unknownScore: 0, negativeScore: 0, surveySignalCount: 4)
        ])

        let sections = library.homeSections
        let likely = sections.first { $0.kind == .likelyRegions }?.packs.map(\.identity.archetypeID) ?? []
        let frontiers = sections.first { $0.kind == .frontiers }?.packs.map(\.identity.archetypeID) ?? []
        let openQuestions = sections.first { $0.kind == .boundaries }?.packs.map(\.identity.archetypeID) ?? []

        XCTAssertFalse(likely.contains("070"))
        XCTAssertFalse(frontiers.contains("070"))
        XCTAssertEqual(openQuestions.first, "070")
    }

    func testCoreRenderModulesArePresentForProofAndNonProofPacks() throws {
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
            XCTAssertFalse(pack.canonicalExamples.isEmpty)
        }
    }

    func testExampleCardListeningTagsAreDistinctFromCardCopy() throws {
        let library = try loadLibrary()

        for pack in library.packs {
            var tagSignatures = Set<String>()

            for example in pack.canonicalExamples {
                XCTAssertFalse(example.whatToListenFor.isEmpty, "\(pack.identity.archetypeID) \(example.displayLabel) is missing visible listening tags")

                let signature = example.whatToListenFor.joined(separator: "|").lowercased()
                XCTAssertFalse(tagSignatures.contains(signature), "\(pack.identity.archetypeID) repeats listening tag set: \(signature)")
                tagSignatures.insert(signature)

                let body = example.whyThisExampleMatters.lowercased()
                for tag in example.whatToListenFor where tag.count >= 4 {
                    XCTAssertFalse(
                        body.contains(tag.lowercased()),
                        "\(pack.identity.archetypeID) repeats listening tag '\(tag)' in card copy for \(example.displayLabel)"
                    )
                }
            }
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

    func testV03AlphaRenderingUsesFixedStandardCopyDepth() {
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
