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

    func testLocalMissionProviderImportsAppImportCandidateResponse() throws {
        let importedAt = try XCTUnwrap(ISO8601DateFormatter().date(from: "2026-05-21T12:00:00Z"))
        let mission = try loadSampleMission()
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
    }

    func testLocalMissionProviderPreservesRouteIdentityMetadataFromAppMissions() throws {
        let mission = try loadMissionFromData(try makeMissionDataWithFirstItemRouteIdentity(
            try loadSampleMission(),
            candidateID: "candidate_alpha_001",
            routeCandidateKey: "route:track:alpha:001",
            routeBatchDedupeKey: "song_recording:alpha:001",
            routeDisplayIdentityKey: "track:alpha-artist:alpha-title"
        ))
        let provider = try makeImportTestProvider()
        let response = TestGenerationResponse(
            run_id: "run_alpha_route_identity_001",
            status: "app_import_candidate",
            app_missions: [mission]
        )

        let imported = try provider.importSupabaseMissionBatchResponseData(
            try JSONEncoder.missionTestEncoder.encode(response)
        )
        let importedItem = try XCTUnwrap(imported.first?.mission.items.first)

        XCTAssertEqual(importedItem.candidateID, "candidate_alpha_001")
        XCTAssertEqual(importedItem.routeCandidateKey, "route:track:alpha:001")
        XCTAssertEqual(importedItem.routeBatchDedupeKey, "song_recording:alpha:001")
        XCTAssertEqual(importedItem.routeDisplayIdentityKey, "track:alpha-artist:alpha-title")
        XCTAssertEqual(MissionImportGate.routeDisplayIdentityKey(for: importedItem), "track:alpha-artist:alpha-title")
        XCTAssertEqual(MissionImportGate.routeCandidateIDs(in: imported), Set(["candidate_alpha_001"]))
    }

    func testLocalSupabaseMissionClientStubReturnsAppImportCandidateShape() async throws {
        let mission = try loadSampleMission()
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

    @MainActor
    func testGraphNativeStarterPackBuildsSixImportableEightSongMissions() throws {
        let tempDirectory = FileManager.default.temporaryDirectory
            .appendingPathComponent("waymark_graph_native_starter_tests", isDirectory: true)
            .appendingPathComponent(UUID().uuidString, isDirectory: true)
        defer {
            try? FileManager.default.removeItem(at: tempDirectory)
        }

        let surveyPersistenceStore = SurveyPersistenceStore(baseDirectoryURL: tempDirectory)
        let surveyStore = SurveyStore(persistenceStore: surveyPersistenceStore)
        surveyStore.prepareRequiredAlphaIntake()
        surveyStore.goTo(.artistPage1)
        XCTAssertNotNil(surveyStore.currentPage)

        let builder = SurveyEvidenceExportBuilder(persistenceStore: surveyPersistenceStore)
        let responseData = try builder.makeGraphNativeStarterMissionBatchResponseData(
            testerAlias: "unit-alpha",
            requestedMissionCount: 6,
            sourceAppVersion: "test",
            sourceAppBuild: "test"
        )
        let provider = LocalMissionProvider(
            reviewedMissionStore: ReviewedMissionStore(baseDirectoryURL: tempDirectory)
        )

        let imported = try provider.importSupabaseMissionBatchResponseData(responseData)
        let items = imported.flatMap(\.mission.items)

        XCTAssertEqual(imported.count, 6)
        XCTAssertEqual(items.count, 48)
        XCTAssertTrue(imported.allSatisfy { $0.mission.items.count == 8 })
        XCTAssertEqual(items.map(\.itemID).count, Set(items.map(\.itemID)).count)
        XCTAssertEqual(items.compactMap(\.routeDisplayIdentityKey).count, items.count)
        XCTAssertEqual(items.compactMap(\.routeDisplayIdentityKey).count, Set(items.compactMap(\.routeDisplayIdentityKey)).count)
        XCTAssertTrue(items.allSatisfy { $0.appleMusicResolution.status == .unresolved })
        XCTAssertTrue(imported.allSatisfy { $0.sourceRunID?.hasPrefix("local_graph_native_starter_pack_") == true })
    }

    @MainActor
    func testSurveyOpportunityBatchBuildsResolvedSurveyDerivedMissions() throws {
        let tempDirectory = FileManager.default.temporaryDirectory
            .appendingPathComponent("cartenza_survey_opportunity_tests", isDirectory: true)
            .appendingPathComponent(UUID().uuidString, isDirectory: true)
        defer {
            try? FileManager.default.removeItem(at: tempDirectory)
        }

        let surveyPersistenceStore = SurveyPersistenceStore(baseDirectoryURL: tempDirectory)
        let surveyStore = SurveyStore(persistenceStore: surveyPersistenceStore)
        surveyStore.prepareRequiredAlphaIntake()
        var ratedSongDisplayKeys = Set<String>()

        let requiredSteps: [SurveyStep] = [
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

        for step in requiredSteps {
            surveyStore.goTo(step)
            let page = try XCTUnwrap(surveyStore.currentPage)
            for (index, item) in page.items.enumerated() {
                let state: SurveySignalState
                switch index % 6 {
                case 0:
                    state = .favorite
                case 1:
                    state = .like
                case 2:
                    state = .fine
                case 3, 4:
                    state = .notForMe
                default:
                    state = .dontKnow
                }
                surveyStore.setState(state, for: item)
                if item.kind == .song {
                    ratedSongDisplayKeys.insert(Self.routeDisplayIdentityKey(title: item.title, artist: item.subtitle ?? ""))
                }
            }
        }

        let builder = SurveyEvidenceExportBuilder(persistenceStore: surveyPersistenceStore)
        let responseData = try builder.makeSurveyOpportunityMissionBatchResponseData(
            testerAlias: "unit-alpha",
            requestedMissionCount: 6,
            sourceAppVersion: "test",
            sourceAppBuild: "test"
        )
        let responseObject = try XCTUnwrap(SupabaseJSON.object(from: responseData) as? [String: Any])
        let selectionAudit = try XCTUnwrap(responseObject["selection_audit"] as? [String: Any])
        let auditMissions = try XCTUnwrap(selectionAudit["missions"] as? [[String: Any]])
        let firstAuditMission = try XCTUnwrap(auditMissions.first)
        let firstAuditItems = try XCTUnwrap(firstAuditMission["selected_route_items"] as? [[String: Any]])
        let firstCandidateScreen = try XCTUnwrap(firstAuditMission["candidate_screen"] as? [String: Any])

        XCTAssertEqual(selectionAudit["schema_version"] as? String, "cartenza.local_mission_selection_audit.v0.1")
        XCTAssertEqual(selectionAudit["no_openai_call"] as? Bool, true)
        XCTAssertEqual(selectionAudit["no_supabase_generation_call"] as? Bool, true)
        XCTAssertEqual(selectionAudit["no_static_public_profile_fixture"] as? Bool, true)
        XCTAssertEqual(selectionAudit["selected_mission_count"] as? Int, 6)
        XCTAssertEqual(selectionAudit["selected_route_item_count"] as? Int, 36)
        XCTAssertEqual(auditMissions.count, 6)
        XCTAssertEqual(firstAuditItems.count, 6)
        XCTAssertGreaterThan(firstCandidateScreen["eligible_count"] as? Int ?? 0, 0)
        XCTAssertTrue(firstAuditItems.allSatisfy { item in
            let appleMusic = item["apple_music"] as? [String: Any]
            return appleMusic?["status"] as? String == "resolved" &&
                appleMusic?["catalog_id"] as? String != nil &&
                item["canonical_song_recording_id"] as? String != nil &&
                item["score"] as? Double != nil
        })

        let provider = LocalMissionProvider(
            reviewedMissionStore: ReviewedMissionStore(baseDirectoryURL: tempDirectory)
        )

        let imported = try provider.importSupabaseMissionBatchResponseData(responseData)
        let missions = imported.map(\.mission)
        let items = missions.flatMap(\.items)

        XCTAssertEqual(imported.count, 6)
        XCTAssertEqual(items.count, 36)
        XCTAssertTrue(missions.allSatisfy { $0.alphaAppImportStatus == .appImportReady })
        XCTAssertTrue(missions.allSatisfy(\.isPlaybackReady))
        XCTAssertTrue(items.allSatisfy { $0.appleMusicResolution.status == .resolved })
        XCTAssertTrue(items.allSatisfy { $0.appleMusicResolution.catalogID?.isEmpty == false || $0.appleMusicResolution.catalogURL != nil })
        XCTAssertEqual(items.map(\.itemID).count, Set(items.map(\.itemID)).count)
        XCTAssertEqual(items.compactMap(\.routeDisplayIdentityKey).count, Set(items.compactMap(\.routeDisplayIdentityKey)).count)
        XCTAssertTrue(items.allSatisfy { item in
            !ratedSongDisplayKeys.contains(Self.routeDisplayIdentityKey(title: item.title, artist: item.artist))
        })
        XCTAssertTrue(imported.allSatisfy { $0.sourceRunID?.hasPrefix("local_survey_opportunity_selection_") == true })
    }

    func testLocalMissionProviderImportsReviewNeededWhenAppValid() throws {
        let mission = try loadSampleMission()
        let provider = try makeImportTestProvider()
        let response = TestGenerationResponse(
            run_id: "run_alpha_002",
            status: "review_needed",
            app_missions: [mission]
        )
        let data = try JSONEncoder.missionTestEncoder.encode(response)

        let imported = try provider.importSupabaseMissionBatchResponseData(data)

        XCTAssertEqual(imported.count, 1)
        XCTAssertEqual(imported.first?.mission.missionID, mission.missionID)
        XCTAssertEqual(imported.first?.source, .generatedReviewed)
        XCTAssertEqual(imported.first?.sourceRunID, "run_alpha_002")
        XCTAssertTrue(imported.first?.importNote?.contains("review_needed") == true)
        XCTAssertEqual(try provider.loadMissionCatalog().reviewedAssignments.count, 1)
    }

    func testLocalMissionProviderRejectsBlockedGenerationStatus() throws {
        let mission = try loadSampleMission()
        let provider = try makeImportTestProvider()
        let response = TestGenerationResponse(
            run_id: "run_alpha_blocked_001",
            status: "blocked",
            app_missions: [mission]
        )
        let data = try JSONEncoder.missionTestEncoder.encode(response)

        XCTAssertThrowsError(try provider.importSupabaseMissionBatchResponseData(data)) { error in
            XCTAssertEqual(error as? MissionImportError, .blockedStatus("blocked"))
        }

        XCTAssertTrue(try provider.loadMissionCatalog().reviewedAssignments.isEmpty)
    }

    func testMissionImportGateRejectsPreResolvedMissionEvidence() throws {
        let mission = try loadSampleMission()
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
        let mission = try loadSampleMission()
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

    func testMissionImportGateRejectsDuplicateDisplayIdentity() throws {
        let mission = try loadSampleMission()
        let provider = try makeImportTestProvider()
        let data = try makeMissionDataWithDuplicateDisplayIdentity(mission)

        XCTAssertThrowsError(try provider.importReviewedMissionData(data, source: .manualReviewed, importedAt: Date())) { error in
            guard case .invalidMission(let reason) = error as? MissionImportError else {
                XCTFail("Expected invalidMission import error, got \(error)")
                return
            }
            XCTAssertTrue(reason.contains("duplicate display identity"))
        }
    }

    func testMissionImportGateRejectsDuplicateRouteDisplayIdentityMetadata() throws {
        let mission = try loadSampleMission()
        let provider = try makeImportTestProvider()
        let data = try makeMissionDataWithDuplicateRouteDisplayIdentity(mission)

        XCTAssertThrowsError(try provider.importReviewedMissionData(data, source: .manualReviewed, importedAt: Date())) { error in
            guard case .invalidMission(let reason) = error as? MissionImportError else {
                XCTFail("Expected invalidMission import error, got \(error)")
                return
            }
            XCTAssertTrue(reason.contains("duplicate display identity track:duplicate-explicit-route"))
        }
    }

    func testLocalMissionProviderRejectsRouteItemAlreadyInAlphaBatch() throws {
        let mission = try loadSampleMission()
        let provider = try makeImportTestProvider()
        let firstResponse = TestGenerationResponse(
            run_id: "run_alpha_batch_001",
            status: "app_import_candidate",
            app_missions: [mission]
        )
        let firstData = try JSONEncoder.missionTestEncoder.encode(firstResponse)
        let imported = try provider.importSupabaseMissionBatchResponseData(firstData)
        let secondResponse = TestGenerationResponse(
            run_id: "run_alpha_batch_002",
            status: "app_import_candidate",
            app_missions: [mission]
        )
        let secondData = try JSONEncoder.missionTestEncoder.encode(secondResponse)

        XCTAssertThrowsError(
            try provider.importSupabaseMissionBatchResponseData(
                secondData,
                importedAt: Date(),
                excludingRouteItemIDs: MissionImportGate.routeItemIDs(in: imported),
                excludingRouteDisplayIdentityKeys: MissionImportGate.routeDisplayIdentityKeys(in: imported)
            )
        ) { error in
            guard case .invalidMission(let reason) = error as? MissionImportError else {
                XCTFail("Expected invalidMission import error, got \(error)")
                return
            }
            XCTAssertTrue(reason.contains("already exists in the Alpha mission batch"))
        }
    }

    func testLocalMissionProviderResetClearsReviewedAssignments() throws {
        let mission = try loadSampleMission()
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
            reviewedMissionStore: .disabled
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
            reviewedMissionStore: ReviewedMissionStore(baseDirectoryURL: tempDirectory)
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

        let mission = try loadSampleMission()
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

    func testLiveResolverUsesCanonicalAppleMusicIndexBeforeCatalogSearch() async throws {
        let now = try XCTUnwrap(ISO8601DateFormatter().date(from: "2026-05-29T12:00:00Z"))
        let item = MissionItem(
            itemID: "ITEM_ALPHA_TRACK_TEST",
            sequence: 1,
            itemType: .track,
            artist: "Test Artist",
            title: "Test Song",
            album: nil,
            year: 2026,
            whyIncluded: "Test fixture.",
            expectedTestSignal: "Index lookup should resolve before search.",
            playerCard: MissionPlayerCard(flipSide: MissionPlayerCardFlipSide(songHypothesis: "Index fixture.", detail: nil)),
            feedbackChipSets: [
                "hit": [FeedbackChipOption(tagID: "hit_test", label: "Hit", description: nil)],
                "partial": [FeedbackChipOption(tagID: "partial_test", label: "Partial", description: nil)],
                "miss": [FeedbackChipOption(tagID: "miss_test", label: "Miss", description: nil)]
            ],
            appleMusicResolution: .unresolved(),
            candidateID: "survey-test-song",
            routeCandidateKey: "route:track:song_recording:test-artist-test-song",
            routeBatchDedupeKey: "song_recording:test-artist-test-song",
            routeDisplayIdentityKey: "track:test-artist:test-song",
            notes: nil
        )
        let index = CanonicalAppleMusicCatalogIndex(entries: [
            CanonicalAppleMusicCatalogIndex.Entry(
                entryID: "graph_song:song|test artist|test song",
                sourceType: "graph_song",
                sourceRef: "song|test artist|test song",
                itemType: "track",
                appleCatalogID: "123456789",
                appleResourceType: "song",
                appleAlbumID: "987654321",
                appleCatalogURL: "https://music.apple.com/us/album/example/987654321?i=123456789",
                storefront: "us",
                resolvedTitle: "Test Song",
                resolvedArtist: "Test Artist",
                resolvedAlbum: "Test Album",
                confidence: 0.95,
                matchStatus: "verified",
                matchBasis: "unit_test",
                priority: 1000,
                matchKeys: [
                    "route_candidate_key:route:track:song_recording:test-artist-test-song",
                    "route_display_identity_key:track:test-artist:test-song"
                ]
            )
        ])

        let resolution = try await MusicKitCatalogSearchService(canonicalIndex: index).resolve(item: item, at: now)

        XCTAssertEqual(resolution.status, .resolved)
        XCTAssertEqual(resolution.catalogID, "123456789")
        XCTAssertEqual(resolution.catalogURL?.absoluteString, "https://music.apple.com/us/album/example/987654321?i=123456789")
        XCTAssertEqual(resolution.resolver, .cached)
        XCTAssertEqual(resolution.reason, "canonical_apple_music_catalog_index_v1:graph_song:verified")
        XCTAssertEqual(resolution.resolvedAt, now)
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

    func testAlphaApprovedMissionFixturesDecodeAndAdaptForLocalImport() throws {
        let data = try loadAlphaMissionDeliveryFixture("approved_app_import_candidates_v0_2")
        let payloads = try AlphaAppImportAdapter.decodeCandidatePayloads(from: data)
        let missions = try payloads.map(AlphaAppImportAdapter.makeMission)

        XCTAssertEqual(payloads.count, 10)
        XCTAssertEqual(missions.count, 10)
        XCTAssertTrue(missions.allSatisfy { $0.alphaAppImportStatus == .appImportCandidate })
        XCTAssertTrue(missions.allSatisfy { $0.items.count == 6 })
        XCTAssertTrue(missions.allSatisfy { !$0.isPlaybackReady })

        let missionTypes = Set(missions.map(\.missionType))
        XCTAssertTrue(missionTypes.contains(.contextDependenceTest))
        XCTAssertTrue(missionTypes.contains(.boundaryTest))
        XCTAssertTrue(missionTypes.contains(.bridgeTest))
        XCTAssertTrue(missionTypes.contains(.archetypeDepthTest))

        let firstMission = try XCTUnwrap(missions.first)
        XCTAssertEqual(firstMission.items.map(\.sequence), [1, 2, 3, 4, 5, 6])
        XCTAssertEqual(firstMission.items.compactMap(\.alphaRouteRole).count, 6)
        XCTAssertTrue(firstMission.items.allSatisfy { $0.alphaResolutionStatus == .candidate })
        XCTAssertTrue(firstMission.items.allSatisfy { $0.appleMusicResolution.status == .candidate })
        XCTAssertNotNil(firstMission.brief)
        XCTAssertNotNil(firstMission.whyThisMissionNow)
        XCTAssertNotNil(firstMission.sourceTraceSummary)
    }

    func testAlphaReviseAndRejectedFixturesAreIgnoredByNormalLocalImport() throws {
        let reviseData = try loadAlphaMissionDeliveryFixture("revise_needed_v0_2")
        let rejectedData = try loadAlphaMissionDeliveryFixture("rejected_v0_2")

        XCTAssertTrue(try AlphaAppImportAdapter.decodeCandidatePayloads(from: reviseData).isEmpty)
        XCTAssertTrue(try AlphaAppImportAdapter.decodeCandidatePayloads(from: rejectedData).isEmpty)
    }

    func testLocalMissionProviderImportsApprovedAlphaCandidatesAsDebugFixtures() throws {
        let provider = try makeImportTestProvider()
        let data = try loadAlphaMissionDeliveryFixture("approved_app_import_candidates_v0_2")

        let imported = try provider.importAlphaAppImportCandidateData(data, importedAt: Date())
        let catalog = try provider.loadMissionCatalog()

        XCTAssertEqual(imported.count, 10)
        XCTAssertEqual(catalog.reviewedAssignments.count, 10)
        XCTAssertTrue(imported.allSatisfy { $0.source == .localAlphaFixture })
        XCTAssertTrue(imported.allSatisfy { $0.mission.alphaAppImportStatus == .appImportCandidate })
        XCTAssertTrue(imported.allSatisfy { !$0.mission.isPlaybackReady })
    }

    func testAlphaFeedbackOperationMappingPreservesMissionOkAsWaypoint() {
        XCTAssertEqual(AlphaFeedbackMapping.operation(for: .hit), .strongPositive)
        XCTAssertEqual(AlphaFeedbackMapping.operation(for: .partial), .qualifiedPositive)
        XCTAssertEqual(AlphaFeedbackMapping.operation(for: .okShelf), .keepWaypoint)
        XCTAssertEqual(AlphaFeedbackMapping.operation(for: .miss), .negative)
        XCTAssertEqual(AlphaFeedbackMapping.operation(for: .skipped), .skipOrNoSignal)
        XCTAssertNil(AlphaFeedbackMapping.operation(for: .unresolved))
        XCTAssertEqual(AlphaFeedbackMapping.missingPrimaryUIOperations, [.issueWrongVersion, .issueUnavailable])
    }

    func testAlphaCandidateItemsBlockPlaybackReadyUntilResolved() throws {
        let candidateData = try loadAlphaMissionDeliveryFixture("approved_app_import_candidates_v0_2")
        let candidatePayload = try XCTUnwrap(try AlphaAppImportAdapter.decodeCandidatePayloads(from: candidateData).first)
        let candidateMission = try AlphaAppImportAdapter.makeMission(from: candidatePayload)

        XCTAssertFalse(candidateMission.isPlaybackReady)
        XCTAssertTrue(candidateMission.items.allSatisfy { $0.appleMusicResolution.status == .candidate })

        let resolvedData = try makeResolvedAlphaFixtureData(from: candidateData)
        let resolvedPayload = try XCTUnwrap(try AlphaAppImportAdapter.decodeCandidatePayloads(from: resolvedData).first)
        let resolvedMission = try AlphaAppImportAdapter.makeMission(from: resolvedPayload)

        XCTAssertTrue(resolvedMission.isPlaybackReady)
        XCTAssertTrue(resolvedMission.items.allSatisfy { $0.appleMusicResolution.status == .resolved })
    }

    func testAlphaAppImportReadyUATFixturesDecodeAsPlaybackReady() throws {
        let readyData = try loadAlphaUATFixture("app_import_ready_alpha_uat_fixtures_v0_2")
        let candidatePayloads = try AlphaAppImportAdapter.decodeCandidatePayloads(from: readyData)
        let readyPayloads = try AlphaAppImportAdapter.decodeImportablePayloads(from: readyData)
        let missions = try readyPayloads.map(AlphaAppImportAdapter.makeMission)

        XCTAssertTrue(candidatePayloads.isEmpty)
        XCTAssertEqual(readyPayloads.count, 6)
        XCTAssertTrue(readyPayloads.allSatisfy(\.isApprovedReady))
        XCTAssertTrue(missions.allSatisfy { $0.alphaAppImportStatus == .appImportReady })
        XCTAssertTrue(missions.allSatisfy(\.isPlaybackReady))
        XCTAssertTrue(missions.allSatisfy { $0.items.count == 6 })
        XCTAssertTrue(missions.flatMap(\.items).allSatisfy { item in
            item.appleMusicResolution.status == .resolved &&
                (item.appleMusicResolution.catalogID?.isEmpty == false || item.appleMusicResolution.catalogURL != nil)
        })
        XCTAssertTrue(missions.flatMap(\.items).allSatisfy { $0.alphaRouteRole != nil })

        let missionTypes = Set(missions.map(\.missionType))
        XCTAssertTrue(missionTypes.contains(.contextDependenceTest))
        XCTAssertTrue(missionTypes.contains(.boundaryTest))
        XCTAssertTrue(missionTypes.contains(.archetypeDepthTest))
    }

    func testAlphaUATFixturesExcludeSuspectMixedSourceContextRoutes() throws {
        let readyData = try loadAlphaUATFixture("app_import_ready_alpha_uat_fixtures_v0_2")
        let missions = try AlphaAppImportAdapter.decodeImportablePayloads(from: readyData)
        let missionIDs = Set(missions.map(\.missionID))

        XCTAssertFalse(missionIDs.contains("alpha-mission-v0-2-009-phase1g-public-profile-06-song-heavy-200-context-dependence-test-mission-type-native-policy-v0-1"))
        XCTAssertFalse(missionIDs.contains("alpha-mission-v0-2-010-phase1g-public-profile-06-song-heavy-200-context-dependence-test-diagnostic-biased-policy-v0-1"))
    }

    func testLocalMissionProviderImportsResolvedUATFixturesAsPlaybackReady() throws {
        let provider = try makeImportTestProvider()
        let data = try loadAlphaUATFixture("app_import_ready_alpha_uat_fixtures_v0_2")

        let imported = try provider.importAlphaAppImportCandidateData(data, importedAt: Date())
        let catalog = try provider.loadMissionCatalog()

        XCTAssertEqual(imported.count, 6)
        XCTAssertEqual(catalog.reviewedAssignments.count, 6)
        XCTAssertTrue(imported.allSatisfy { $0.source == .localAlphaFixture })
        XCTAssertTrue(imported.allSatisfy { $0.mission.alphaAppImportStatus == .appImportReady })
        XCTAssertTrue(imported.allSatisfy { $0.mission.isPlaybackReady })
        XCTAssertNotNil(imported.first?.mission.items.first?.appleMusicResolution.catalogID)
        XCTAssertNotNil(imported.first?.mission.items.first?.appleMusicResolution.catalogURL)
    }

    @MainActor
    func testResolvedUATFixtureCanBeSelectedForPlaybackSmoke() throws {
        let tempDirectory = FileManager.default.temporaryDirectory
            .appendingPathComponent("waymark_alpha_uat_fixture_tests", isDirectory: true)
            .appendingPathComponent(UUID().uuidString, isDirectory: true)
        defer {
            try? FileManager.default.removeItem(at: tempDirectory)
        }

        let provider = LocalMissionProvider(
            reviewedMissionStore: ReviewedMissionStore(baseDirectoryURL: tempDirectory)
        )
        let appModel = AppModel(
            sessionPersistenceStore: .disabled,
            missionProvider: provider
        )

        let data = try loadAlphaUATFixture("app_import_ready_alpha_uat_fixtures_v0_2")
        try provider.importAlphaAppImportCandidateData(data, importedAt: Date())
        appModel.loadMissionLibrary()

        let selectedMission = try XCTUnwrap(appModel.mission)
        let selectedItem = try XCTUnwrap(appModel.selectedItem)
        XCTAssertTrue(selectedMission.isPlaybackReady)
        XCTAssertEqual(selectedItem.appleMusicResolution.status, .resolved)
        XCTAssertNotNil(selectedItem.appleMusicResolution.catalogID)
    }

    @MainActor
    func testAppModelClearsLegacyUATFixturesWhenSurveyDerivedBuildDisablesFixtureControls() throws {
        let tempDirectory = FileManager.default.temporaryDirectory
            .appendingPathComponent("cartenza_alpha_uat_fixture_migration_tests", isDirectory: true)
            .appendingPathComponent(UUID().uuidString, isDirectory: true)
        defer {
            try? FileManager.default.removeItem(at: tempDirectory)
        }

        let provider = LocalMissionProvider(
            reviewedMissionStore: ReviewedMissionStore(baseDirectoryURL: tempDirectory)
        )
        let persistenceStore = SessionPersistenceStore(baseDirectoryURL: tempDirectory)
        let data = try loadAlphaUATFixture("app_import_ready_alpha_uat_fixtures_v0_2")
        try provider.importAlphaAppImportCandidateData(data, importedAt: Date())

        let appModel = AppModel(
            sessionPersistenceStore: persistenceStore,
            missionProvider: provider,
            shouldClearLegacyAlphaUATFixturesOnLoad: true
        )
        appModel.loadMissionLibrary()

        XCTAssertEqual(appModel.missionLoadState, .loaded)
        XCTAssertTrue(appModel.availableMissions.isEmpty)
        XCTAssertNil(appModel.mission)
        XCTAssertTrue(try provider.loadMissionCatalog().reviewedAssignments.isEmpty)
        XCTAssertTrue(appModel.lastActionMessage?.contains("Cleared prior static UAT fixture missions") == true)
    }

    @MainActor
    func testAppModelResolvedUATFixtureImportReplacesPriorAssignmentsAndPersistsSelection() throws {
        let tempDirectory = FileManager.default.temporaryDirectory
            .appendingPathComponent("waymark_alpha_uat_fixture_replace_tests", isDirectory: true)
            .appendingPathComponent(UUID().uuidString, isDirectory: true)
        defer {
            try? FileManager.default.removeItem(at: tempDirectory)
        }

        let provider = LocalMissionProvider(
            reviewedMissionStore: ReviewedMissionStore(baseDirectoryURL: tempDirectory)
        )
        let persistenceStore = SessionPersistenceStore(baseDirectoryURL: tempDirectory)
        let appModel = AppModel(
            sessionPersistenceStore: persistenceStore,
            missionProvider: provider
        )
        let oldMission = try loadSampleMission()
        let oldData = try JSONEncoder.missionTestEncoder.encode(oldMission)
        try provider.importReviewedMissionData(oldData, source: .manualReviewed)

        appModel.loadMissionLibrary()
        XCTAssertEqual(appModel.availableMissions.map(\.missionID), [oldMission.missionID])

        appModel.importLocalAlphaAppImportReadyUATFixtures()

        XCTAssertEqual(appModel.availableMissions.count, 6)
        XCTAssertFalse(appModel.availableMissions.contains { $0.missionID == oldMission.missionID })
        XCTAssertTrue(appModel.availableMissions.allSatisfy { $0.alphaAppImportStatus == .appImportReady })
        XCTAssertTrue(appModel.availableMissions.allSatisfy { $0.items.count == 6 })
        XCTAssertTrue(appModel.availableMissions.allSatisfy(\.isPlaybackReady))

        let persistedLibrary = persistenceStore.load()
        let selectedMissionID = try XCTUnwrap(appModel.mission?.missionID)
        XCTAssertEqual(persistedLibrary.activeMissionID, selectedMissionID)
        XCTAssertNotNil(persistedLibrary.sessionsByMissionID[selectedMissionID])
    }

    @MainActor
    func testAppModelRegeneratesMissionsFromCurrentSurveyWithLocalSelector() async throws {
        let tempDirectory = FileManager.default.temporaryDirectory
            .appendingPathComponent("cartenza_manual_regeneration_tests", isDirectory: true)
            .appendingPathComponent(UUID().uuidString, isDirectory: true)
        defer {
            try? FileManager.default.removeItem(at: tempDirectory)
        }

        let surveyPersistenceStore = SurveyPersistenceStore(baseDirectoryURL: tempDirectory)
        let surveyStore = SurveyStore(persistenceStore: surveyPersistenceStore)
        surveyStore.prepareRequiredAlphaIntake()

        let requiredSteps: [SurveyStep] = [
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

        for step in requiredSteps {
            surveyStore.goTo(step)
            let page = try XCTUnwrap(surveyStore.currentPage)
            for (index, item) in page.items.enumerated() {
                let state: SurveySignalState
                switch index % 6 {
                case 0:
                    state = .favorite
                case 1:
                    state = .like
                case 2:
                    state = .fine
                case 3, 4:
                    state = .notForMe
                default:
                    state = .dontKnow
                }
                surveyStore.setState(state, for: item)
            }
        }

        let provider = LocalMissionProvider(
            reviewedMissionStore: ReviewedMissionStore(baseDirectoryURL: tempDirectory)
        )
        let sessionPersistenceStore = SessionPersistenceStore(baseDirectoryURL: tempDirectory)
        let oldMission = try loadSampleMission()
        try provider.importReviewedMissionData(
            try JSONEncoder.missionTestEncoder.encode(oldMission),
            source: .manualReviewed
        )

        let client = RecordingMissionGenerationClient(responses: [])
        let appModel = AppModel(
            sessionPersistenceStore: sessionPersistenceStore,
            missionProvider: provider,
            supabaseConfig: .unconfigured,
            missionGenerationClient: client,
            surveyEvidenceBuilder: SurveyEvidenceExportBuilder(persistenceStore: surveyPersistenceStore)
        )
        appModel.loadMissionLibrary()
        XCTAssertEqual(appModel.availableMissions.map(\.missionID), [oldMission.missionID])

        let didRegenerate = await appModel.regenerateMissionBatchFromCurrentSurvey()

        XCTAssertTrue(didRegenerate)
        XCTAssertTrue(client.requests.isEmpty)
        XCTAssertEqual(appModel.reviewedMissionAssignmentCount, AlphaMissionGenerationConfig.requiredMissionCount)
        XCTAssertFalse(appModel.availableMissions.contains { $0.missionID == oldMission.missionID })
        XCTAssertTrue(appModel.availableMissions.allSatisfy { $0.missionID.hasPrefix("MIS_ALPHA_SURVEY_OPPORTUNITY_") })
        XCTAssertTrue(appModel.availableMissions.allSatisfy(\.isPlaybackReady))
        XCTAssertTrue(appModel.reviewedMissionAssignments.allSatisfy { $0.sourceRunID?.hasPrefix("local_survey_opportunity_selection_") == true })
        XCTAssertEqual(appModel.firstMissionGenerationState, .loaded)
        XCTAssertEqual(appModel.firstMissionGenerationProgress.completedCount, AlphaMissionGenerationConfig.requiredMissionCount)
        XCTAssertNotNil(sessionPersistenceStore.load().activeMissionID)
    }

    func testBlockedAlphaFixtureItemCannotImportAsPlaybackReady() throws {
        let candidateData = try loadAlphaMissionDeliveryFixture("approved_app_import_candidates_v0_2")
        let blockedData = try makeBlockedAlphaFixtureData(from: candidateData)
        let blockedPayload = try XCTUnwrap(try AlphaAppImportAdapter.decodeImportablePayloads(from: blockedData).first)
        let blockedMission = try AlphaAppImportAdapter.makeMission(from: blockedPayload)

        XCTAssertFalse(blockedMission.isPlaybackReady)
        XCTAssertEqual(blockedMission.items.first?.appleMusicResolution.status, .blocked)

        let provider = try makeImportTestProvider()
        XCTAssertThrowsError(try provider.importAlphaAppImportCandidateData(blockedData, importedAt: Date())) { error in
            guard case .invalidMission(let reason) = error as? MissionImportError else {
                XCTFail("Expected invalidMission import error, got \(error)")
                return
            }
            XCTAssertTrue(reason.contains("must enter the app unresolved"))
        }
    }

    private static func routeDisplayIdentityKey(title: String, artist: String) -> String {
        "track:\(normalizedRoutePart(artist)):\(normalizedRoutePart(title))"
    }

    private static func normalizedRoutePart(_ value: String) -> String {
        value
            .folding(options: [.caseInsensitive, .diacriticInsensitive], locale: Locale(identifier: "en_US_POSIX"))
            .lowercased()
            .components(separatedBy: CharacterSet.alphanumerics.inverted)
            .filter { !$0.isEmpty }
            .joined(separator: "-")
    }
}

func loadSampleMission(file: StaticString = #filePath, line: UInt = #line) throws -> Mission {
    try loadMissionResource("sample_mission_love_tributaries_v0_2", file: file, line: line)
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

private func loadAlphaMissionDeliveryFixture(_ resourceName: String) throws -> Data {
    let repoRoot = URL(fileURLWithPath: #filePath)
        .deletingLastPathComponent()
        .deletingLastPathComponent()
    let url = repoRoot
        .appendingPathComponent("data/product_contracts/alpha_mission_delivery_v0_2/fixtures/golden", isDirectory: true)
        .appendingPathComponent("\(resourceName).json")
    return try Data(contentsOf: url)
}

private func loadAlphaUATFixture(_ resourceName: String) throws -> Data {
    let repoRoot = URL(fileURLWithPath: #filePath)
        .deletingLastPathComponent()
        .deletingLastPathComponent()
    let url = repoRoot
        .appendingPathComponent("data/product_contracts/alpha_mission_delivery_v0_2/fixtures/uat", isDirectory: true)
        .appendingPathComponent("\(resourceName).json")
    return try Data(contentsOf: url)
}

private func makeResolvedAlphaFixtureData(from data: Data) throws -> Data {
    guard var missions = try JSONSerialization.jsonObject(with: data) as? [[String: Any]],
          !missions.isEmpty,
          var route = missions[0]["route"] as? [[String: Any]] else {
        throw TestResourceError.malformedMissionJSON
    }

    for index in route.indices {
        route[index]["resolution_status"] = "resolved"
        route[index]["apple_music_id"] = "alpha_resolved_\(index + 1)"
        route[index]["apple_music_url"] = "https://music.apple.com/us/song/alpha-resolved-\(index + 1)"
    }
    missions[0]["route"] = route

    return try JSONSerialization.data(withJSONObject: [missions[0]], options: [.sortedKeys])
}

private func makeBlockedAlphaFixtureData(from data: Data) throws -> Data {
    guard var missions = try JSONSerialization.jsonObject(with: data) as? [[String: Any]],
          !missions.isEmpty,
          var route = missions[0]["route"] as? [[String: Any]],
          !route.isEmpty else {
        throw TestResourceError.malformedMissionJSON
    }

    route[0]["resolution_status"] = "blocked"
    route[0]["apple_music_id"] = nil
    route[0]["apple_music_url"] = nil
    missions[0]["route"] = route

    return try JSONSerialization.data(withJSONObject: [missions[0]], options: [.sortedKeys])
}

private func loadMissionFromData(_ data: Data) throws -> Mission {
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
        reviewedMissionStore: ReviewedMissionStore(baseDirectoryURL: directoryURL)
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

private func makeMissionDataWithFirstItemRouteIdentity(
    _ mission: Mission,
    candidateID: String,
    routeCandidateKey: String,
    routeBatchDedupeKey: String,
    routeDisplayIdentityKey: String
) throws -> Data {
    let data = try JSONEncoder.missionTestEncoder.encode(mission)
    guard var object = try JSONSerialization.jsonObject(with: data) as? [String: Any],
          var items = object["items"] as? [[String: Any]],
          !items.isEmpty else {
        throw TestResourceError.malformedMissionJSON
    }

    items[0]["candidate_id"] = candidateID
    items[0]["route_candidate_key"] = routeCandidateKey
    items[0]["route_batch_dedupe_key"] = routeBatchDedupeKey
    items[0]["route_display_identity_key"] = routeDisplayIdentityKey
    object["items"] = items
    return try JSONSerialization.data(withJSONObject: object)
}

private func makeMissionDataWithIdentitySuffix(_ mission: Mission, suffix: String) throws -> Data {
    let data = try JSONEncoder.missionTestEncoder.encode(mission)
    guard var object = try JSONSerialization.jsonObject(with: data) as? [String: Any],
          var items = object["items"] as? [[String: Any]] else {
        throw TestResourceError.malformedMissionJSON
    }

    let normalizedSuffix = suffix
        .uppercased()
        .components(separatedBy: CharacterSet.alphanumerics.inverted)
        .filter { !$0.isEmpty }
        .joined(separator: "_")
    object["mission_id"] = "MIS_REGENERATED_ALPHA_\(normalizedSuffix)"
    object["mission_title"] = "Regenerated Alpha \(normalizedSuffix)"

    for index in items.indices {
        let itemNumber = index + 1
        items[index]["item_id"] = "ITEM_REGENERATED_ALPHA_\(normalizedSuffix)_\(itemNumber)"
        items[index]["title"] = "\(items[index]["title"] as? String ?? "Route Item") \(normalizedSuffix)"
        items[index]["candidate_id"] = "candidate_regenerated_alpha_\(suffix)_\(itemNumber)"
        items[index]["route_candidate_key"] = "route:regenerated:\(suffix):\(itemNumber)"
        items[index]["route_batch_dedupe_key"] = "song_recording:regenerated:\(suffix):\(itemNumber)"
        items[index]["route_display_identity_key"] = "track:regenerated-\(suffix)-\(itemNumber)"
    }

    object["items"] = items
    return try JSONSerialization.data(withJSONObject: object)
}

private func makeMissionDataWithDuplicateDisplayIdentity(_ mission: Mission) throws -> Data {
    let data = try JSONEncoder.missionTestEncoder.encode(mission)
    guard var object = try JSONSerialization.jsonObject(with: data) as? [String: Any],
          var items = object["items"] as? [[String: Any]],
          items.count > 1 else {
        throw TestResourceError.malformedMissionJSON
    }

    items[1]["artist"] = items[0]["artist"]
    items[1]["title"] = items[0]["title"]
    object["items"] = items
    return try JSONSerialization.data(withJSONObject: object)
}

private func makeMissionDataWithDuplicateRouteDisplayIdentity(_ mission: Mission) throws -> Data {
    let data = try JSONEncoder.missionTestEncoder.encode(mission)
    guard var object = try JSONSerialization.jsonObject(with: data) as? [String: Any],
          var items = object["items"] as? [[String: Any]],
          items.count > 1 else {
        throw TestResourceError.malformedMissionJSON
    }

    items[0]["route_display_identity_key"] = "track:duplicate-explicit-route"
    items[1]["route_display_identity_key"] = "track:duplicate-explicit-route"
    object["items"] = items
    return try JSONSerialization.data(withJSONObject: object)
}

private struct TestGenerationResponse: Encodable {
    let run_id: String?
    let status: String
    let app_missions: [Mission]
}

private final class RecordingMissionGenerationClient: MissionGenerationClient {
    private var responses: [Data]
    private(set) var requests: [MissionGenerationRequest] = []

    init(responses: [Data]) {
        self.responses = responses
    }

    func generateFirstMissionBatch(request: MissionGenerationRequest, accessToken: String) async throws -> Data {
        requests.append(request)
        guard !responses.isEmpty else {
            throw TestResourceError.missingGenerationResponse
        }
        return responses.removeFirst()
    }
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
        MissionCatalog(reviewedAssignments: assignments)
    }

    func importReviewedMissionData(_ data: Data, source: MissionAssignmentSource, importedAt: Date) throws -> [MissionAssignment] {
        assignments
    }

    func importAlphaAppImportCandidateData(_ data: Data, importedAt: Date) throws -> [MissionAssignment] {
        assignments
    }

    func importSupabaseMissionBatchResponseData(
        _ data: Data,
        importedAt: Date,
        excludingRouteItemIDs: Set<String>,
        excludingRouteDisplayIdentityKeys: Set<String>
    ) throws -> [MissionAssignment] {
        assignments
    }

    func resetReviewedAssignments() throws {}
}

private final class TestBundleMarker {}

private enum TestResourceError: Error {
    case missingSampleMission
    case malformedMissionJSON
    case missingGenerationResponse
}
