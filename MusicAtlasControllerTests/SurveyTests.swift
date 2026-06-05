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

    func testDiagnosticOnlyAppleMusicPayloadDoesNotInfluenceSurveyPageConstruction() throws {
        let baselineProvider = FixtureSurveyPageProvider()
        let baselinePage = try XCTUnwrap(baselineProvider.page(for: .artistPage1, responses: [:]))

        let provider = FixtureSurveyPageProvider()
        provider.updateAppleMusicSignalPayload(Self.makeApplePayload(diagnosticArtistNames: [
            "Nirvana",
            "Wipers",
            "Sonic Youth",
            "Prince"
        ]))
        let page = try XCTUnwrap(provider.page(for: .artistPage1, responses: [:]))

        XCTAssertEqual(page.items.count, SurveyFixtureLibrary.gridPageItemLimit)
        XCTAssertEqual(page.kind, .artist)
        XCTAssertEqual(page.id, "artist_page_001")
        XCTAssertEqual(page.items.map(\.id), baselinePage.items.map(\.id))
        XCTAssertFalse(page.items.contains { $0.source == .appleMusicDerived })
        XCTAssertTrue(page.items.contains { $0.source == .broadCalibration })
        XCTAssertTrue(page.items.contains { $0.source == .rejectionProbe })
    }

    func testRecentlyPlayedAndReplaySummarySeedSurveyStartingPages() throws {
        let provider = FixtureSurveyPageProvider()
        provider.updateAppleMusicSignalPayload(Self.makeAppleEvidencePayload())

        let artistPage = try XCTUnwrap(provider.page(for: .artistPage1, responses: [:]))
        let albumPage = try XCTUnwrap(provider.page(for: .albumPage1, responses: [:]))
        let albumPage2 = try XCTUnwrap(provider.page(
            for: .albumPage2,
            responses: [:],
            displayedPages: [SurveyStep.albumPage1.rawValue: albumPage]
        ))
        let songPage = try XCTUnwrap(provider.page(for: .songPage1, responses: [:]))
        let albumItems = albumPage.items + albumPage2.items

        XCTAssertEqual(artistPage.items.count, SurveyFixtureLibrary.gridPageItemLimit)
        XCTAssertEqual(artistPage.items.map(\.id).count, Set(artistPage.items.map(\.id)).count)
        XCTAssertTrue(albumItems.contains {
            $0.title == "Nevermind" && $0.subtitle == "Nirvana" && $0.source == .appleMusicDerived
        })
        XCTAssertTrue(songPage.items.contains {
            $0.title == "Smells Like Teen Spirit" && $0.subtitle == "Nirvana" && $0.source == .appleMusicDerived
        })
        XCTAssertTrue(songPage.items.contains {
            $0.title == "Buddy Holly" && $0.subtitle == "Weezer" && $0.source == .appleMusicDerived
        })
    }

    func testReplaySummaryArtistRefsResolveThroughCanonicalAppleIndex() throws {
        let provider = FixtureSurveyPageProvider()
        provider.updateAppleMusicSignalPayload(Self.makeReplayArtistRefPayload())

        let artistPage1 = try XCTUnwrap(provider.page(for: .artistPage1, responses: [:]))
        let artistPage2 = try XCTUnwrap(provider.page(
            for: .artistPage2,
            responses: [:],
            displayedPages: [SurveyStep.artistPage1.rawValue: artistPage1]
        ))
        let artistItems = artistPage1.items + artistPage2.items

        XCTAssertTrue(
            artistItems.contains { $0.title == "Sonic Youth" && $0.source == .appleMusicDerived },
            artistItems.map { "\($0.title):\($0.source.rawValue)" }.joined(separator: ", ")
        )
    }

    func testReplayTopSongVariantFallsBackToCanonicalArtistAndTitle() throws {
        let provider = FixtureSurveyPageProvider()
        provider.updateAppleMusicSignalPayload(Self.makeReplayTopSongVariantPayload())

        let artistPage = try XCTUnwrap(provider.page(for: .artistPage1, responses: [:]))
        let songPage = try XCTUnwrap(provider.page(for: .songPage1, responses: [:]))

        XCTAssertTrue(
            artistPage.items.contains { $0.title == "Nirvana" && $0.source == .appleMusicDerived },
            artistPage.items.map { "\($0.title):\($0.source.rawValue)" }.joined(separator: ", ")
        )
        XCTAssertTrue(
            songPage.items.contains { $0.title == "Smells Like Teen Spirit" && $0.source == .appleMusicDerived },
            songPage.items.map { "\($0.title):\($0.source.rawValue)" }.joined(separator: ", ")
        )
    }

    func testReplaySummaryAndRecentlyPlayedBothSeedSurveyWithoutOrdinalWeighting() throws {
        let provider = FixtureSurveyPageProvider()
        provider.updateAppleMusicSignalPayload(Self.makeReplayDominatesRecentContextPayload())

        let artistPage1 = try XCTUnwrap(provider.page(for: .artistPage1, responses: [:]))
        let artistPage2 = try XCTUnwrap(provider.page(
            for: .artistPage2,
            responses: [:],
            displayedPages: [SurveyStep.artistPage1.rawValue: artistPage1]
        ))
        let songPage = try XCTUnwrap(provider.page(for: .songPage1, responses: [:]))

        let artistTitles = (artistPage1.items + artistPage2.items).map(\.title)
        let songTitles = songPage.items.map(\.title)
        XCTAssertTrue(artistTitles.contains("Nirvana"), "artist titles: \(artistTitles)")
        XCTAssertTrue(artistTitles.contains("ABBA"), "artist titles: \(artistTitles)")
        XCTAssertTrue(songTitles.contains("Smells Like Teen Spirit"), "song titles: \(songTitles)")
        XCTAssertTrue(songTitles.contains("Dancing Queen"), "song titles: \(songTitles)")
    }

    func testAppleSeededArtistPageOneUsesPolicySlotsOnly() throws {
        let provider = FixtureSurveyPageProvider()
        provider.updateAppleMusicSignalPayload(Self.makeDenseArtistPolicyApplePayload())

        let page = try XCTUnwrap(provider.page(for: .artistPage1, responses: [:]))
        let page2 = try XCTUnwrap(provider.page(
            for: .artistPage2,
            responses: [:],
            displayedPages: [SurveyStep.artistPage1.rawValue: page]
        ))
        let batchItems = page.items + page2.items

        XCTAssertEqual(page.items.count, SurveyFixtureLibrary.gridPageItemLimit)
        XCTAssertEqual(page.items.map(\.id).count, Set(page.items.map(\.id)).count)
        XCTAssertTrue(
            batchItems.contains { $0.title == "ABBA" && $0.source == .appleMusicDerived },
            batchItems.map { "\($0.title):\($0.source.rawValue)" }.joined(separator: ", ")
        )
        XCTAssertTrue(
            batchItems.contains { $0.title == "Nirvana" && $0.source == .appleMusicDerived },
            batchItems.map { "\($0.title):\($0.source.rawValue)" }.joined(separator: ", ")
        )
        XCTAssertTrue(
            batchItems.contains { $0.title == "Sonic Youth" && $0.source == .appleMusicDerived },
            batchItems.map { "\($0.title):\($0.source.rawValue)" }.joined(separator: ", ")
        )
        XCTAssertFalse(page.items.contains { $0.title == "2Pac" }, page.items.map(\.title).joined(separator: ", "))
        XCTAssertFalse(page.items.contains { $0.source == .rejectionProbe }, page.items.map { "\($0.title):\($0.source.rawValue)" }.joined(separator: ", "))
    }

    func testAppleSeededArtistPageTwoUsesArchetypePolicySlotsOnly() throws {
        let provider = FixtureSurveyPageProvider()
        provider.updateAppleMusicSignalPayload(Self.makeDenseArtistPolicyApplePayload())

        let page1 = try XCTUnwrap(provider.page(for: .artistPage1, responses: [:]))
        let page2 = try XCTUnwrap(provider.page(
            for: .artistPage2,
            responses: [:],
            displayedPages: [SurveyStep.artistPage1.rawValue: page1]
        ))

        XCTAssertEqual(page2.items.count, SurveyFixtureLibrary.gridPageItemLimit)
        XCTAssertTrue(Set(page1.items.map(\.id)).isDisjoint(with: Set(page2.items.map(\.id))))
        XCTAssertTrue(
            (page1.items + page2.items).contains { $0.title == "Weezer" && $0.source == .appleMusicDerived },
            (page1.items + page2.items).map { "\($0.title):\($0.source.rawValue)" }.joined(separator: ", ")
        )
        XCTAssertFalse(page2.items.contains { $0.source == .rejectionProbe }, page2.items.map { "\($0.title):\($0.source.rawValue)" }.joined(separator: ", "))
        XCTAssertFalse(page2.items.contains { $0.title == "2Pac" }, page2.items.map(\.title).joined(separator: ", "))
        XCTAssertFalse(page2.items.contains { $0.title == "Doja Cat" }, page2.items.map(\.title).joined(separator: ", "))
    }

    func testArtistPageTwoDoesNotRepeatDislikedPriorObjects() throws {
        let provider = FixtureSurveyPageProvider()

        let page1 = try XCTUnwrap(provider.page(for: .artistPage1, responses: [:]))
        let disliked = Array(page1.items.prefix(3))
        XCTAssertEqual(disliked.count, 3)

        let responses = Dictionary(uniqueKeysWithValues: disliked.map { item in
            (
                item.id,
                SurveyResponse(
                    itemID: item.id,
                    itemKind: item.kind,
                    state: .notForMe,
                    nuances: [],
                    note: "",
                    updatedAt: Date()
                )
            )
        })

        let page2 = try XCTUnwrap(provider.page(for: .artistPage2, responses: responses))
        XCTAssertEqual(page2.items.count, SurveyFixtureLibrary.gridPageItemLimit)
        XCTAssertTrue(Set(page1.items.map(\.id)).isDisjoint(with: Set(page2.items.map(\.id))))
        XCTAssertTrue(Set(disliked.map(\.id)).isDisjoint(with: Set(page2.items.map(\.id))))
        XCTAssertTrue(page2.items.contains { $0.source == .rejectionProbe || $0.objective == .testAdjacentRoad })
    }

    func testAlphaSurveyProviderFiltersCanonicalAlphaBlocklist() {
        let provider = FixtureSurveyPageProvider()

        XCTAssertFalse(provider.itemLookup().keys.contains("ALPHA_ALBUM_robin-s-show-me-love"))
    }

    func testAlphaSurveyGridPagesStayWithinOneScreenLimit() throws {
        let provider = FixtureSurveyPageProvider()
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
            let page = try XCTUnwrap(provider.page(for: step, responses: [:]))
            XCTAssertLessThanOrEqual(page.items.count, SurveyFixtureLibrary.gridPageItemLimit)
        }
    }

    func testArtistPageOneWithDenseApplePayloadDoesNotOverfillGrid() throws {
        let provider = FixtureSurveyPageProvider()
        provider.updateAppleMusicSignalPayload(Self.makeApplePayload(diagnosticArtistNames: [
            "Nirvana",
            "Wipers",
            "Sonic Youth",
            "Prince",
            "Doja Cat",
            "The Killers",
            "Dolly Parton",
            "2Pac",
            "Adele",
            "Black Sabbath",
            "Bjork",
            "Kraftwerk"
        ]))

        let page = try XCTUnwrap(provider.page(for: .artistPage1, responses: [:]))

        XCTAssertEqual(page.items.count, SurveyFixtureLibrary.gridPageItemLimit)
        XCTAssertEqual(page.items.map(\.id).count, Set(page.items.map(\.id)).count)
        XCTAssertFalse(page.items.contains { $0.source == .appleMusicDerived })
    }

    func testRequiredAlphaSurveyPagesDoNotRepeatWithinObjectType() throws {
        let provider = FixtureSurveyPageProvider()
        let objectStepGroups: [[SurveyStep]] = [
            [.artistPage1, .artistPage2, .artistPage3, .artistPage4],
            [.albumPage1, .albumPage2],
            [.songPage1, .songPage2, .songPage3, .songPage4]
        ]

        for steps in objectStepGroups {
            var seenIDs = Set<String>()
            var seenDisplayKeys = Set<String>()
            for step in steps {
                let page = try XCTUnwrap(provider.page(for: step, responses: [:]))
                let ids = page.items.map(\.id)
                let displayKeys = page.items.map(Self.displayKey)
                XCTAssertEqual(ids.count, Set(ids).count, "\(step.rawValue) contains duplicate items.")
                XCTAssertEqual(displayKeys.count, Set(displayKeys).count, "\(step.rawValue) contains duplicate display identities.")
                XCTAssertTrue(seenIDs.isDisjoint(with: ids), "\(step.rawValue) repeats items from an earlier page.")
                XCTAssertTrue(seenDisplayKeys.isDisjoint(with: displayKeys), "\(step.rawValue) repeats display identities from an earlier page.")
                seenIDs.formUnion(ids)
                seenDisplayKeys.formUnion(displayKeys)
            }
        }
    }

    func testRequiredAlphaSurveyPagesRespectAlbumAndSongRepetitionGovernors() throws {
        let provider = FixtureSurveyPageProvider()
        provider.updateAppleMusicSignalPayload(Self.makeAppleEvidencePayload())

        var displayedPages = [String: SurveyGridPage]()
        let albumPages = try [SurveyStep.albumPage1, .albumPage2].map { step in
            let page = try XCTUnwrap(provider.page(for: step, responses: [:], displayedPages: displayedPages))
            displayedPages[step.rawValue] = page
            return page
        }
        let albumArtistCounts = Self.countsByNormalizedSubtitle(in: albumPages.flatMap(\.items))
        XCTAssertLessThanOrEqual(albumArtistCounts.values.max() ?? 0, 2, "Album artist counts: \(albumArtistCounts)")

        displayedPages.removeAll()
        let songPages = try [SurveyStep.songPage1, .songPage2, .songPage3, .songPage4].map { step in
            let page = try XCTUnwrap(provider.page(for: step, responses: [:], displayedPages: displayedPages))
            displayedPages[step.rawValue] = page
            return page
        }
        let songItems = songPages.flatMap(\.items)
        let songArtistCounts = Self.countsByNormalizedSubtitle(in: songItems)
        XCTAssertLessThanOrEqual(songArtistCounts.values.max() ?? 0, 3, "Song artist counts: \(songArtistCounts)")

        let archetypeIDsBySongID = try Self.archetypeIDsBySurveySongID()
        var songArchetypeCounts = [String: Int]()
        for item in songItems {
            for archetypeID in archetypeIDsBySongID[item.id] ?? [] {
                songArchetypeCounts[archetypeID, default: 0] += 1
            }
        }
        XCTAssertLessThanOrEqual(songArchetypeCounts.values.max() ?? 0, 6, "Song archetype counts: \(songArchetypeCounts)")
    }

    func testDisplayedPageHistoryPreventsLaterArtistRepeatsAndCurrentPageReshuffle() throws {
        let tempDirectory = FileManager.default.temporaryDirectory
            .appendingPathComponent("survey-displayed-history-repeat-\(UUID().uuidString)", isDirectory: true)
        defer {
            try? FileManager.default.removeItem(at: tempDirectory)
        }

        let persistenceStore = SurveyPersistenceStore(baseDirectoryURL: tempDirectory)
        let store = SurveyStore(persistenceStore: persistenceStore)
        store.prepareRequiredAlphaIntake()
        store.updateAppleMusicSignalPayload(Self.makeApplePayload(diagnosticArtistNames: [
            "Nirvana",
            "Wipers",
            "Sonic Youth",
            "Prince",
            "Doja Cat",
            "The Killers",
            "Dolly Parton",
            "2Pac"
        ]))

        store.goTo(.artistPage1)
        let page1 = try XCTUnwrap(store.currentPage)
        store.setState(.like, for: try XCTUnwrap(page1.items.first))

        store.goTo(.artistPage2)
        let page2 = try XCTUnwrap(store.currentPage)
        store.setState(.favorite, for: try XCTUnwrap(page2.items.first))

        store.goTo(.artistPage3)
        let page3 = try XCTUnwrap(store.currentPage)
        let priorArtistIDs = Set((page1.items + page2.items).map(\.id))
        XCTAssertTrue(priorArtistIDs.isDisjoint(with: Set(page3.items.map(\.id))))

        let page3IDs = page3.items.map(\.id)
        store.setState(.notForMe, for: try XCTUnwrap(page3.items.first))
        XCTAssertEqual(store.currentPage?.items.map(\.id), page3IDs)
    }

    func testRejectedArtistSuppressesExactArtistAlbumsAndSongs() throws {
        let provider = FixtureSurveyPageProvider()
        let lookup = provider.itemLookup()
        let doja = try XCTUnwrap(lookup["ALPHA_ARTIST_doja-cat"])
        let killers = try XCTUnwrap(lookup["ALPHA_ARTIST_the-killers"])
        let now = Date()
        let responses = Dictionary(uniqueKeysWithValues: [doja, killers].map { item in
            (
                item.id,
                SurveyResponse(
                    itemID: item.id,
                    itemKind: item.kind,
                    state: .notForMe,
                    nuances: [],
                    note: "",
                    updatedAt: now
                )
            )
        })

        let albumPages = try [.albumPage1, .albumPage2].map { step in
            try XCTUnwrap(provider.page(for: step, responses: responses))
        }
        let songPages = try [.songPage1, .songPage2, .songPage3, .songPage4].map { step in
            try XCTUnwrap(provider.page(for: step, responses: responses))
        }
        let blockedArtists = Set(["Doja Cat", "The Killers"])

        XCTAssertFalse(albumPages.flatMap(\.items).contains { item in
            item.subtitle.map(blockedArtists.contains) ?? false
        })
        XCTAssertFalse(songPages.flatMap(\.items).contains { item in
            item.subtitle.map(blockedArtists.contains) ?? false
        })
    }

    func testSongSubtitlesUseDisplayArtistNames() throws {
        let lookup = FixtureSurveyPageProvider().itemLookup()
        let jolene = try XCTUnwrap(lookup["ALPHA_SONG_dolly-parton-jolene"])

        XCTAssertEqual(jolene.subtitle, "Dolly Parton")
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

        let page = try XCTUnwrap(FixtureSurveyPageProvider().page(for: .songPage1, responses: [:]))
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
        for candidate in candidates {
            XCTAssertFalse((candidate["app_route_item_id"] as? String ?? "").isEmpty)
            XCTAssertFalse((candidate["route_candidate_key"] as? String ?? "").isEmpty)
            XCTAssertFalse((candidate["route_batch_dedupe_key"] as? String ?? "").isEmpty)
            XCTAssertFalse((candidate["route_display_identity_key"] as? String ?? "").isEmpty)
        }

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

        let page = try XCTUnwrap(FixtureSurveyPageProvider().page(for: .artistPage1, responses: [:]))
        let positive = try XCTUnwrap(page.items.first)
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
        XCTAssertEqual(request.promptContext.alreadySelectedDisplayKeys, request.promptContext.alreadySelectedRouteDisplayIdentityKeys)
        XCTAssertFalse((request.promptContext.sourceCandidatePoolID ?? "").localizedCaseInsensitiveContains("nirvana"))
    }

    func testAlphaSurveyStoreForcedIntakeSequence() throws {
        let store = SurveyStore(persistenceStore: .disabled)
        store.prepareRequiredAlphaIntake()

        XCTAssertEqual(store.currentStep, .connectAppleMusic)

        let expectedSteps: [SurveyStep] = [
            .artistPage1,
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
        let page = try XCTUnwrap(FixtureSurveyPageProvider().page(for: .artistPage1, responses: [:]))
        let item = try XCTUnwrap(page.items.first)
        let previousStore = SurveyStore(persistenceStore: persistenceStore)
        previousStore.setState(.favorite, for: item)
        previousStore.addFreeformSignal("carryover should clear")
        previousStore.goTo(.albumPage2)

        let requiredStore = SurveyStore(persistenceStore: persistenceStore)
        requiredStore.prepareRequiredAlphaIntake()

        XCTAssertEqual(requiredStore.currentStep, .connectAppleMusic)
        XCTAssertEqual(requiredStore.state(for: item), .dontKnow)
        XCTAssertTrue(requiredStore.freeformSignals.isEmpty)
        XCTAssertEqual(requiredStore.makeSummary().visibleSignalCount, 0)
    }

    func testSurveyStorePersistsResponsesAndFreeformSignals() throws {
        let tempDirectory = FileManager.default.temporaryDirectory
            .appendingPathComponent("survey-store-\(UUID().uuidString)", isDirectory: true)
        let persistenceStore = SurveyPersistenceStore(baseDirectoryURL: tempDirectory)
        let store = SurveyStore(persistenceStore: persistenceStore)
        let page = try XCTUnwrap(FixtureSurveyPageProvider().page(for: .artistPage1, responses: [:]))
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

    func testSurveyStorePersistsDisplayedDynamicPagesAndApplePayload() throws {
        let tempDirectory = FileManager.default.temporaryDirectory
            .appendingPathComponent("survey-page-history-\(UUID().uuidString)", isDirectory: true)
        defer {
            try? FileManager.default.removeItem(at: tempDirectory)
        }

        let persistenceStore = SurveyPersistenceStore(baseDirectoryURL: tempDirectory)
        let store = SurveyStore(persistenceStore: persistenceStore)
        store.prepareRequiredAlphaIntake()
        store.updateAppleMusicSignalPayload(Self.makeApplePayload(diagnosticArtistNames: [
            "Nirvana",
            "Wipers",
            "Sonic Youth"
        ]))
        store.goTo(.artistPage1)

        let page1 = try XCTUnwrap(store.currentPage)
        XCTAssertEqual(page1.id, "artist_page_001")
        XCTAssertFalse(page1.items.contains { $0.source == .appleMusicDerived })

        let item = try XCTUnwrap(page1.items.first)
        store.setState(.favorite, for: item)
        store.goTo(.artistPage2)
        let page2 = try XCTUnwrap(store.currentPage)

        let restoredStore = SurveyStore(persistenceStore: persistenceStore)

        XCTAssertEqual(restoredStore.currentStep, .artistPage2)
        XCTAssertEqual(restoredStore.displayedPages.count, 2)
        XCTAssertEqual(restoredStore.currentPage?.items.map(\.id), page2.items.map(\.id))
        let persistedApplePayload = try XCTUnwrap(persistenceStore.load().appleMusicSignalPayload)
        XCTAssertEqual(persistedApplePayload.schemaVersion, AppleMusicSignalPayload.currentSchemaVersion)
        XCTAssertEqual(
            persistedApplePayload.excludedOrDiagnosticSources.flatMap(\.items).map(\.displayName),
            ["Nirvana", "Wipers", "Sonic Youth"]
        )
    }

    func testAppleMusicSignalPayloadV02FixtureDecodesAndReencodesDeterministically() throws {
        let fixtureData = try Self.fixtureData(named: "apple_music_signal_payload_v0_2_sample")
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let payload = try decoder.decode(AppleMusicSignalPayload.self, from: fixtureData)

        XCTAssertEqual(payload.schemaVersion, AppleMusicSignalPayload.currentSchemaVersion)
        XCTAssertEqual(payload.probeVersion, "apple_probe.v0.2")
        let artistSnapshot = try XCTUnwrap(payload.excludedOrDiagnosticSources.first { $0.sourceID == "library_artists_alphabetical_snapshot" })
        XCTAssertEqual(artistSnapshot.items.first?.evidenceBasis, .diagnosticExcluded)
        XCTAssertEqual(artistSnapshot.excludedFromSurveyEvidence, true)

        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        encoder.outputFormatting = [.sortedKeys]
        let encoded = try encoder.encode(payload)
        let decodedAgain = try decoder.decode(AppleMusicSignalPayload.self, from: encoded)

        XCTAssertEqual(decodedAgain.payloadID, payload.payloadID)
        XCTAssertEqual(decodedAgain.primarySignalSources.librarySongPlayCount.items.map(\.sourceItemID), payload.primarySignalSources.librarySongPlayCount.items.map(\.sourceItemID))
        XCTAssertEqual(decodedAgain.catalogHydration.resources.map(\.sourceItemID), payload.catalogHydration.resources.map(\.sourceItemID))
    }

    func testSurveyEvidenceExportUsesDisplayedPagesAndQuarantinesUnshownResponses() throws {
        let tempDirectory = FileManager.default.temporaryDirectory
            .appendingPathComponent("survey-evidence-export-\(UUID().uuidString)", isDirectory: true)
        defer {
            try? FileManager.default.removeItem(at: tempDirectory)
        }

        let persistenceStore = SurveyPersistenceStore(baseDirectoryURL: tempDirectory)
        let store = SurveyStore(persistenceStore: persistenceStore)
        store.prepareRequiredAlphaIntake()
        store.goTo(.artistPage1)
        let page = try XCTUnwrap(store.currentPage)
        let visibleItem = try XCTUnwrap(page.items.first)
        let now = try XCTUnwrap(ISO8601DateFormatter().date(from: "2026-05-18T12:00:00Z"))

        store.setState(.favorite, for: visibleItem, at: now)
        store.toggleNuance(.oneAlbumOnly, for: visibleItem, at: now)

        var session = persistenceStore.load()
        session.responses["UNSHOWN_ARTIST_RESPONSE"] = SurveyResponse(
            itemID: "UNSHOWN_ARTIST_RESPONSE",
            itemKind: .artist,
            state: .like,
            nuances: [],
            note: "",
            updatedAt: now
        )
        try persistenceStore.save(session)

        let builder = SurveyEvidenceExportBuilder(persistenceStore: persistenceStore)
        let exportData = try builder.makeSurveyEvidenceExportData(session: persistenceStore.load(), now: now)
        let export = try XCTUnwrap(JSONSerialization.jsonObject(with: exportData) as? [String: Any])
        let atlasIngestable = try XCTUnwrap(export["atlas_ingestable"] as? [String: Any])
        let evidenceAtoms = try XCTUnwrap(atlasIngestable["evidence_atoms"] as? [[String: Any]])
        let atom = try XCTUnwrap(evidenceAtoms.first)

        XCTAssertEqual(evidenceAtoms.count, 1)
        XCTAssertEqual(atom["survey_session_id"] as? String, session.surveySessionID)
        XCTAssertEqual(atom["survey_item_id"] as? String, visibleItem.id)
        XCTAssertEqual(atom["normalized_reaction_operation"] as? String, "preference_positive_strong")
        XCTAssertEqual(atom["evidence_strength_hint"] as? Double, 0.88)
        XCTAssertEqual(atom["selected_tags"] as? [String], ["one_album_only"])
        XCTAssertFalse((atom["shown_unselected_tags"] as? [String] ?? []).isEmpty)

        let pageContext = try XCTUnwrap(atom["page_context"] as? [String: Any])
        XCTAssertEqual(pageContext["page_id"] as? String, page.id)
        XCTAssertEqual(pageContext["stage"] as? String, "artist")
        XCTAssertEqual(pageContext["page_number"] as? Int, 1)

        let appleExposurePrior = try XCTUnwrap(atom["apple_exposure_prior"] as? [String: Any])
        XCTAssertEqual(appleExposurePrior["prior_type"] as? String, "apple_exposure_prior")
        XCTAssertEqual(appleExposurePrior["taste_truth"] as? Bool, false)

        let constructionOnly = try XCTUnwrap(export["construction_only_excluded"] as? [String: Any])
        XCTAssertEqual(constructionOnly["outside_atlas_ingestion"] as? Bool, true)
        let quarantined = try XCTUnwrap(constructionOnly["quarantined_response_refs"] as? [[String: Any]])
        XCTAssertEqual(quarantined.count, 1)
        XCTAssertEqual(quarantined.first?["survey_item_id"] as? String, "UNSHOWN_ARTIST_RESPONSE")
        XCTAssertEqual(quarantined.first?["reason"] as? String, "missing_tile_or_ref")
        XCTAssertEqual(quarantined.first?["atlas_ingestable"] as? Bool, false)
        let reasonCounts = try XCTUnwrap(constructionOnly["quarantine_reason_counts"] as? [String: Int])
        XCTAssertEqual(reasonCounts["missing_tile_or_ref"], 1)
    }

    func testSurveyPageSelectionAuditExplainsDisplayedPagesWithoutAtlasIngestion() throws {
        let tempDirectory = FileManager.default.temporaryDirectory
            .appendingPathComponent("survey-page-selection-audit-\(UUID().uuidString)", isDirectory: true)
        defer {
            try? FileManager.default.removeItem(at: tempDirectory)
        }

        let persistenceStore = SurveyPersistenceStore(baseDirectoryURL: tempDirectory)
        let store = SurveyStore(persistenceStore: persistenceStore)
        store.prepareRequiredAlphaIntake()
        store.updateAppleMusicSignalPayload(Self.makeApplePayload(diagnosticArtistNames: [
            "Nirvana",
            "Wipers"
        ]))
        store.goTo(.artistPage1)
        let page = try XCTUnwrap(store.currentPage)
        let item = try XCTUnwrap(page.items.first)
        store.setState(.like, for: item)
        store.goTo(.artistPage2)
        XCTAssertNotNil(store.currentPage)

        let builder = SurveyEvidenceExportBuilder(persistenceStore: persistenceStore)
        let auditData = try builder.makeSurveyPageSelectionAuditData(session: persistenceStore.load())
        let audit = try XCTUnwrap(JSONSerialization.jsonObject(with: auditData) as? [String: Any])

        XCTAssertEqual(audit["schema_version"] as? String, "waymark.survey_page_selection_audit.v0.1.app")
        let constructionOnly = try XCTUnwrap(audit["construction_only_excluded"] as? [String: Any])
        XCTAssertEqual(constructionOnly["hidden_simulator_truth"] as? Bool, true)
        XCTAssertEqual(constructionOnly["raw_scoring_internals"] as? Bool, true)

        let pages = try XCTUnwrap(audit["pages"] as? [[String: Any]])
        let firstPage = try XCTUnwrap(pages.first)
        XCTAssertEqual(firstPage["page_id"] as? String, "artist_page_001")
        XCTAssertFalse((firstPage["displayed_tiles"] as? [[String: Any]] ?? []).isEmpty)
        XCTAssertEqual((firstPage["prior_response_trace_inputs"] as? [[String: Any]])?.count, 0)

        let secondPage = try XCTUnwrap(pages.first { $0["step"] as? String == SurveyStep.artistPage2.rawValue })
        let priorSummary = try XCTUnwrap(secondPage["prior_response_summary_inputs"] as? [String: Any])
        XCTAssertEqual(priorSummary["response_count"] as? Int, 1)
        let stateCounts = try XCTUnwrap(priorSummary["state_counts"] as? [String: Int])
        XCTAssertEqual(stateCounts["like"], 1)

        let priorTrace = try XCTUnwrap(secondPage["prior_response_trace_inputs"] as? [[String: Any]])
        let priorResponse = try XCTUnwrap(priorTrace.first)
        XCTAssertEqual(priorTrace.count, 1)
        XCTAssertEqual(priorResponse["survey_item_id"] as? String, item.id)
        XCTAssertEqual(priorResponse["state"] as? String, "like")
        XCTAssertEqual(priorResponse["source_page_id"] as? String, page.id)
        XCTAssertEqual(priorResponse["source_step"] as? String, SurveyStep.artistPage1.rawValue)
        XCTAssertEqual(priorResponse["source_position"] as? Int, 1)
        XCTAssertEqual(priorResponse["note_present"] as? Bool, false)

        let serialized = String(data: auditData, encoding: .utf8) ?? ""
        XCTAssertFalse(serialized.localizedCaseInsensitiveContains("hidden_reaction_corpus"))
        XCTAssertFalse(serialized.localizedCaseInsensitiveContains("raw_candidate_scores"))
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

    private static func makeApplePayload(diagnosticArtistNames: [String]) -> AppleMusicSignalPayload {
        let now = Date(timeIntervalSince1970: 1_778_221_200)
        let diagnosticReason = "Diagnostic-only alphabetical artist snapshot excluded from Survey evidence: \(diagnosticArtistNames.joined(separator: ", "))."
        let diagnosticItems = diagnosticArtistNames.enumerated().map { index, name in
            AppleMusicSignalResource(
                sourceItemID: "library_artists_alphabetical_snapshot:unit_test:\(index)",
                resourceType: .artist,
                libraryID: "unit_test_artist_\(index)",
                displayName: name,
                artistName: name,
                evidenceBasis: .diagnosticExcluded,
                sourceConfidence: .diagnosticExcluded,
                observedSourceRefs: ["library_artists_alphabetical_snapshot"]
            )
        }
        return AppleMusicSignalPayload(
            payloadID: "apple_music_signal_payload:unit_test",
            capturedAt: now,
            storefront: "us",
            authorization: AppleMusicSignalAuthorization(
                musicAuthorizationStatus: "authorized",
                canRequestAuthorization: false,
                subscriptionStatus: "can_play_catalog_content",
                tokenStatus: "automatic_music_data_request",
                errors: []
            ),
            primarySignalSources: Self.emptyPrimarySources(now: now),
            contextSources: Self.emptyContextSources(now: now),
            observedResourceAnnotations: .empty(capturedAt: now),
            catalogHydration: AppleMusicCatalogHydration(status: .empty, resources: [], errors: []),
            excludedOrDiagnosticSources: [
                .diagnosticExcluded(
                    sourceID: "library_artists_alphabetical_snapshot",
                    cap: 50,
                    capturedAt: now,
                    reason: diagnosticReason,
                    items: diagnosticItems
                )
            ]
        )
    }

    private static func makeAppleEvidencePayload() -> AppleMusicSignalPayload {
        let now = Date(timeIntervalSince1970: 1_778_221_200)
        let recentlyPlayed = [
            AppleMusicSignalResource(
                sourceItemID: "recently_played_tracks:unit_test:0",
                resourceType: .song,
                appleID: "1440783625",
                catalogID: "1440783625",
                displayName: "Smells Like Teen Spirit",
                artistName: "Nirvana",
                albumTitle: "Nevermind",
                evidenceBasis: .recentlyPlayed,
                sourceConfidence: .rankedByApple,
                observedSourceRefs: ["recently_played_tracks"]
            ),
            AppleMusicSignalResource(
                sourceItemID: "recently_played_tracks:unit_test:1",
                resourceType: .song,
                appleID: "1440798133",
                catalogID: "1440798133",
                displayName: "Buddy Holly",
                artistName: "Weezer",
                albumTitle: "Weezer (Blue Album)",
                evidenceBasis: .recentlyPlayed,
                sourceConfidence: .rankedByApple,
                observedSourceRefs: ["recently_played_tracks"]
            )
        ]
        let replaySummary = [
            AppleMusicSignalResource(
                sourceItemID: "replay_summary:unit_test:0",
                resourceType: .song,
                appleID: "eWVhci0yMDI2LXNvbmctMTQ0MDc4MzYyNQ",
                catalogID: "eWVhci0yMDI2LXNvbmctMTQ0MDc4MzYyNQ",
                displayName: "Smells Like Teen Spirit",
                artistName: "Nirvana",
                albumTitle: "Nevermind",
                evidenceBasis: .replaySummary,
                sourceConfidence: .rankedByApple,
                observedSourceRefs: ["replay_summary"]
            ),
            AppleMusicSignalResource(
                sourceItemID: "replay_summary:unit_test:1",
                resourceType: .album,
                appleID: "eWVhci0yMDI2LWFsYnVtLTE0NDA3ODM2MTc",
                catalogID: "eWVhci0yMDI2LWFsYnVtLTE0NDA3ODM2MTc",
                displayName: "Nevermind",
                artistName: "Nirvana",
                evidenceBasis: .replaySummary,
                sourceConfidence: .rankedByApple,
                observedSourceRefs: ["replay_summary"]
            )
        ]

        return AppleMusicSignalPayload(
            payloadID: "apple_music_signal_payload:unit_test:evidence",
            capturedAt: now,
            storefront: "us",
            authorization: AppleMusicSignalAuthorization(
                musicAuthorizationStatus: "authorized",
                canRequestAuthorization: false,
                subscriptionStatus: "can_play_catalog_content",
                tokenStatus: "automatic_music_data_request",
                errors: []
            ),
            primarySignalSources: AppleMusicPrimarySignalSources(
                heavyRotation: .empty(sourceID: "heavy_rotation", cap: 10, capturedAt: now),
                recentlyPlayedTracks: .captured(
                    sourceID: "recently_played_tracks",
                    cap: 150,
                    capturedAt: now,
                    items: recentlyPlayed
                ),
                librarySongPlayCount: .empty(sourceID: "library_song_play_count", cap: 200, capturedAt: now),
                librarySongLastPlayed: .empty(sourceID: "library_song_last_played", cap: 100, capturedAt: now),
                librarySongLibraryAdded: .empty(sourceID: "library_song_library_added", cap: 100, capturedAt: now),
                libraryAlbumLibraryAdded: .empty(sourceID: "library_album_library_added", cap: 100, capturedAt: now),
                personalRecommendations: .empty(sourceID: "personal_recommendations", cap: 50, capturedAt: now)
            ),
            contextSources: AppleMusicContextSignalSources(
                playlistContexts: .empty(sourceID: "playlist_contexts", cap: 50, capturedAt: now),
                playlistTrackSamples: .empty(sourceID: "playlist_track_samples", cap: 250, capturedAt: now),
                replaySummary: .captured(
                    sourceID: "replay_summary",
                    cap: 120,
                    capturedAt: now,
                    items: replaySummary
                )
            ),
            observedResourceAnnotations: .empty(capturedAt: now),
            catalogHydration: AppleMusicCatalogHydration(
                status: .captured,
                resources: AppleMusicSignalPayload.catalogHydrationResources(from: recentlyPlayed + replaySummary),
                errors: []
            ),
            excludedOrDiagnosticSources: []
        )
    }

    private static func makeReplayDominatesRecentContextPayload() -> AppleMusicSignalPayload {
        let now = Date(timeIntervalSince1970: 1_778_221_200)
        let recentlyPlayed = [
            AppleMusicSignalResource(
                sourceItemID: "recently_played_tracks:context:0",
                resourceType: .song,
                displayName: "Knowing Me, Knowing You",
                artistName: "ABBA",
                albumTitle: "Gold: Greatest Hits",
                evidenceBasis: .recentlyPlayed,
                sourceConfidence: .explicitObserved,
                observedSourceRefs: ["recently_played_tracks"]
            ),
            AppleMusicSignalResource(
                sourceItemID: "recently_played_tracks:context:1",
                resourceType: .song,
                displayName: "Dancing Queen",
                artistName: "ABBA",
                albumTitle: "Gold: Greatest Hits",
                evidenceBasis: .recentlyPlayed,
                sourceConfidence: .explicitObserved,
                observedSourceRefs: ["recently_played_tracks"]
            )
        ]
        let replaySummary = [
            AppleMusicSignalResource(
                sourceItemID: "replay_summary:context:0",
                resourceType: .song,
                appleID: "eWVhci0yMDI2LXNvbmctMTQ0MDc4MzYyNQ",
                catalogID: "eWVhci0yMDI2LXNvbmctMTQ0MDc4MzYyNQ",
                displayName: "Smells Like Teen Spirit",
                artistName: "Nirvana",
                albumTitle: "Nevermind",
                evidenceBasis: .replaySummary,
                sourceConfidence: .rankedByApple,
                observedSourceRefs: ["replay_summary"]
            ),
            AppleMusicSignalResource(
                sourceItemID: "replay_summary:context:1",
                resourceType: .album,
                appleID: "eWVhci0yMDI2LWFsYnVtLTE0NDA3ODM2MTc",
                catalogID: "eWVhci0yMDI2LWFsYnVtLTE0NDA3ODM2MTc",
                displayName: "Nevermind",
                artistName: "Nirvana",
                evidenceBasis: .replaySummary,
                sourceConfidence: .rankedByApple,
                observedSourceRefs: ["replay_summary"]
            )
        ]

        return AppleMusicSignalPayload(
            payloadID: "apple_music_signal_payload:unit_test:replay_context",
            capturedAt: now,
            storefront: "us",
            authorization: AppleMusicSignalAuthorization(
                musicAuthorizationStatus: "authorized",
                canRequestAuthorization: false,
                subscriptionStatus: "can_play_catalog_content",
                tokenStatus: "automatic_music_data_request",
                errors: []
            ),
            primarySignalSources: AppleMusicPrimarySignalSources(
                heavyRotation: .empty(sourceID: "heavy_rotation", cap: 10, capturedAt: now),
                recentlyPlayedTracks: .captured(
                    sourceID: "recently_played_tracks",
                    cap: 150,
                    capturedAt: now,
                    items: recentlyPlayed
                ),
                librarySongPlayCount: .empty(sourceID: "library_song_play_count", cap: 200, capturedAt: now),
                librarySongLastPlayed: .empty(sourceID: "library_song_last_played", cap: 100, capturedAt: now),
                librarySongLibraryAdded: .empty(sourceID: "library_song_library_added", cap: 100, capturedAt: now),
                libraryAlbumLibraryAdded: .empty(sourceID: "library_album_library_added", cap: 100, capturedAt: now),
                personalRecommendations: .empty(sourceID: "personal_recommendations", cap: 50, capturedAt: now)
            ),
            contextSources: AppleMusicContextSignalSources(
                playlistContexts: .empty(sourceID: "playlist_contexts", cap: 50, capturedAt: now),
                playlistTrackSamples: .empty(sourceID: "playlist_track_samples", cap: 250, capturedAt: now),
                replaySummary: .captured(
                    sourceID: "replay_summary",
                    cap: 120,
                    capturedAt: now,
                    items: replaySummary
                )
            ),
            observedResourceAnnotations: .empty(capturedAt: now),
            catalogHydration: AppleMusicCatalogHydration(
                status: .captured,
                resources: AppleMusicSignalPayload.catalogHydrationResources(from: recentlyPlayed + replaySummary),
                errors: []
            ),
            excludedOrDiagnosticSources: []
        )
    }

    private static func makeReplayArtistRefPayload() -> AppleMusicSignalPayload {
        let now = Date(timeIntervalSince1970: 1_778_221_200)
        let replaySummary = [
            AppleMusicSignalResource(
                sourceItemID: "replay_summary:artist_ref:0",
                resourceType: .artist,
                appleID: "eWVhci0yMDI2LWFydGlzdC0zNjAzNA",
                catalogID: "eWVhci0yMDI2LWFydGlzdC0zNjAzNA",
                displayName: "Sonic Youth",
                artistName: "Sonic Youth",
                evidenceBasis: .replaySummary,
                sourceConfidence: .rankedByApple,
                observedSourceRefs: ["replay_summary"]
            )
        ]

        return AppleMusicSignalPayload(
            payloadID: "apple_music_signal_payload:unit_test:replay_artist_ref",
            capturedAt: now,
            storefront: "us",
            authorization: AppleMusicSignalAuthorization(
                musicAuthorizationStatus: "authorized",
                canRequestAuthorization: false,
                subscriptionStatus: "can_play_catalog_content",
                tokenStatus: "automatic_music_data_request",
                errors: []
            ),
            primarySignalSources: Self.emptyPrimarySources(now: now),
            contextSources: AppleMusicContextSignalSources(
                playlistContexts: .empty(sourceID: "playlist_contexts", cap: 50, capturedAt: now),
                playlistTrackSamples: .empty(sourceID: "playlist_track_samples", cap: 250, capturedAt: now),
                replaySummary: .captured(
                    sourceID: "replay_summary",
                    cap: 120,
                    capturedAt: now,
                    items: replaySummary
                )
            ),
            observedResourceAnnotations: .empty(capturedAt: now),
            catalogHydration: AppleMusicCatalogHydration(
                status: .captured,
                resources: AppleMusicSignalPayload.catalogHydrationResources(from: replaySummary),
                errors: []
            ),
            excludedOrDiagnosticSources: []
        )
    }

    private static func makeReplayTopSongVariantPayload() -> AppleMusicSignalPayload {
        let now = Date(timeIntervalSince1970: 1_778_221_200)
        let replayTopSongs = [
            AppleMusicSignalResource(
                sourceItemID: "replay_top_songs:variant:0",
                resourceType: .song,
                appleID: "1586410661",
                catalogID: "1586410661",
                displayName: "Smells Like Teen Spirit (Remastered)",
                artistName: "Nirvana",
                albumTitle: "Nevermind (30th Anniversary Super Deluxe)",
                evidenceBasis: .replaySummary,
                sourceConfidence: .rankedByApple,
                observedSourceRefs: ["replay_top_songs"]
            )
        ]

        return AppleMusicSignalPayload(
            payloadID: "apple_music_signal_payload:unit_test:replay_top_variant",
            capturedAt: now,
            storefront: "us",
            authorization: AppleMusicSignalAuthorization(
                musicAuthorizationStatus: "authorized",
                canRequestAuthorization: false,
                subscriptionStatus: "can_play_catalog_content",
                tokenStatus: "automatic_music_data_request",
                errors: []
            ),
            primarySignalSources: Self.emptyPrimarySources(now: now),
            contextSources: AppleMusicContextSignalSources(
                playlistContexts: .empty(sourceID: "playlist_contexts", cap: 50, capturedAt: now),
                playlistTrackSamples: .empty(sourceID: "playlist_track_samples", cap: 250, capturedAt: now),
                replaySummary: .empty(sourceID: "replay_summary", cap: 0, capturedAt: now),
                replayTopArtists: .empty(sourceID: "replay_top_artists", cap: 50, capturedAt: now),
                replayTopAlbums: .empty(sourceID: "replay_top_albums", cap: 50, capturedAt: now),
                replayTopSongs: .captured(
                    sourceID: "replay_top_songs",
                    cap: 200,
                    capturedAt: now,
                    items: replayTopSongs
                )
            ),
            observedResourceAnnotations: .empty(capturedAt: now),
            catalogHydration: AppleMusicCatalogHydration(
                status: .captured,
                resources: AppleMusicSignalPayload.catalogHydrationResources(from: replayTopSongs),
                errors: []
            ),
            excludedOrDiagnosticSources: []
        )
    }

    private static func makeDenseArtistPolicyApplePayload() -> AppleMusicSignalPayload {
        let now = Date(timeIntervalSince1970: 1_778_221_200)
        let recentlyPlayed = [
            AppleMusicSignalResource(
                sourceItemID: "recently_played_tracks:policy:0",
                resourceType: .song,
                displayName: "Dancing Queen",
                artistName: "ABBA",
                albumTitle: "Gold: Greatest Hits",
                evidenceBasis: .recentlyPlayed,
                sourceConfidence: .rankedByApple,
                observedSourceRefs: ["recently_played_tracks"]
            ),
            AppleMusicSignalResource(
                sourceItemID: "recently_played_tracks:policy:1",
                resourceType: .song,
                appleID: "1440783625",
                catalogID: "1440783625",
                displayName: "Smells Like Teen Spirit",
                artistName: "Nirvana",
                albumTitle: "Nevermind",
                evidenceBasis: .recentlyPlayed,
                sourceConfidence: .rankedByApple,
                observedSourceRefs: ["recently_played_tracks"]
            ),
            AppleMusicSignalResource(
                sourceItemID: "recently_played_tracks:policy:2",
                resourceType: .song,
                appleID: "1440798133",
                catalogID: "1440798133",
                displayName: "Buddy Holly",
                artistName: "Weezer",
                albumTitle: "Weezer (Blue Album)",
                evidenceBasis: .recentlyPlayed,
                sourceConfidence: .rankedByApple,
                observedSourceRefs: ["recently_played_tracks"]
            ),
            AppleMusicSignalResource(
                sourceItemID: "recently_played_tracks:policy:3",
                resourceType: .song,
                displayName: "Teen Age Riot",
                artistName: "Sonic Youth",
                albumTitle: "Daydream Nation",
                evidenceBasis: .recentlyPlayed,
                sourceConfidence: .rankedByApple,
                observedSourceRefs: ["recently_played_tracks"]
            )
        ]

        return AppleMusicSignalPayload(
            payloadID: "apple_music_signal_payload:unit_test:artist_policy",
            capturedAt: now,
            storefront: "us",
            authorization: AppleMusicSignalAuthorization(
                musicAuthorizationStatus: "authorized",
                canRequestAuthorization: false,
                subscriptionStatus: "can_play_catalog_content",
                tokenStatus: "automatic_music_data_request",
                errors: []
            ),
            primarySignalSources: AppleMusicPrimarySignalSources(
                heavyRotation: .empty(sourceID: "heavy_rotation", cap: 10, capturedAt: now),
                recentlyPlayedTracks: .captured(
                    sourceID: "recently_played_tracks",
                    cap: 150,
                    capturedAt: now,
                    items: recentlyPlayed
                ),
                librarySongPlayCount: .empty(sourceID: "library_song_play_count", cap: 200, capturedAt: now),
                librarySongLastPlayed: .empty(sourceID: "library_song_last_played", cap: 100, capturedAt: now),
                librarySongLibraryAdded: .empty(sourceID: "library_song_library_added", cap: 100, capturedAt: now),
                libraryAlbumLibraryAdded: .empty(sourceID: "library_album_library_added", cap: 100, capturedAt: now),
                personalRecommendations: .empty(sourceID: "personal_recommendations", cap: 50, capturedAt: now)
            ),
            contextSources: Self.emptyContextSources(now: now),
            observedResourceAnnotations: .empty(capturedAt: now),
            catalogHydration: AppleMusicCatalogHydration(
                status: .captured,
                resources: AppleMusicSignalPayload.catalogHydrationResources(from: recentlyPlayed),
                errors: []
            ),
            excludedOrDiagnosticSources: []
        )
    }

    private static func emptyPrimarySources(now: Date) -> AppleMusicPrimarySignalSources {
        AppleMusicPrimarySignalSources(
            heavyRotation: .empty(sourceID: "heavy_rotation", cap: 50, capturedAt: now),
            recentlyPlayedTracks: .empty(sourceID: "recently_played_tracks", cap: 150, capturedAt: now),
            librarySongPlayCount: .empty(sourceID: "library_song_play_count", cap: 200, capturedAt: now),
            librarySongLastPlayed: .empty(sourceID: "library_song_last_played", cap: 100, capturedAt: now),
            librarySongLibraryAdded: .empty(sourceID: "library_song_library_added", cap: 100, capturedAt: now),
            libraryAlbumLibraryAdded: .empty(sourceID: "library_album_library_added", cap: 100, capturedAt: now),
            personalRecommendations: .empty(sourceID: "personal_recommendations", cap: 50, capturedAt: now)
        )
    }

    private static func emptyContextSources(now: Date) -> AppleMusicContextSignalSources {
        AppleMusicContextSignalSources(
            playlistContexts: .empty(sourceID: "playlist_contexts", cap: 50, capturedAt: now),
            playlistTrackSamples: .empty(sourceID: "playlist_track_samples", cap: 250, capturedAt: now),
            replaySummary: .empty(sourceID: "replay_summary", cap: 0, capturedAt: now)
        )
    }

    private static func displayKey(for item: SurveyItem) -> String {
        "\(normalized(item.title))::\(normalized(item.subtitle ?? ""))"
    }

    private static func countsByNormalizedSubtitle(in items: [SurveyItem]) -> [String: Int] {
        items.reduce(into: [String: Int]()) { counts, item in
            guard let subtitle = item.subtitle, !subtitle.isEmpty else {
                return
            }
            counts[normalized(subtitle), default: 0] += 1
        }
    }

    private static func archetypeIDsBySurveySongID() throws -> [String: [String]] {
        let data = try bundledResourceData(named: "canonical_song_recordings")
        let songs = try JSONDecoder().decode([SurveyTestCanonicalSongRecord].self, from: data)
        var result = [String: [String]]()
        for song in songs {
            result["ALPHA_SONG_\(song.canonicalSongRecordingID)"] = song.archetypeIDs
        }
        return result
    }

    private static func bundledResourceData(named name: String) throws -> Data {
        let bundles = [Bundle(for: SurveyTests.self), Bundle.main] + Bundle.allBundles + Bundle.allFrameworks
        if let url = bundles.lazy.compactMap({ $0.url(forResource: name, withExtension: "json") }).first {
            return try Data(contentsOf: url)
        }
        throw XCTSkip("Missing bundled resource \(name).json")
    }

    private static func normalized(_ value: String) -> String {
        value
            .folding(options: [.diacriticInsensitive, .caseInsensitive], locale: .current)
            .lowercased()
            .components(separatedBy: CharacterSet.alphanumerics.inverted)
            .filter { !$0.isEmpty }
            .joined(separator: "-")
    }

    private static func fixtureData(named name: String) throws -> Data {
        let testFileURL = URL(fileURLWithPath: #filePath)
        let fixtureURL = testFileURL
            .deletingLastPathComponent()
            .appendingPathComponent("Fixtures", isDirectory: true)
            .appendingPathComponent("\(name).json", isDirectory: false)
        return try Data(contentsOf: fixtureURL)
    }
}

private struct SurveyTestCanonicalSongRecord: Decodable {
    let canonicalSongRecordingID: String
    let archetypeIDs: [String]

    enum CodingKeys: String, CodingKey {
        case canonicalSongRecordingID = "canonical_song_recording_id"
        case archetypeIDs = "archetype_ids"
    }
}
