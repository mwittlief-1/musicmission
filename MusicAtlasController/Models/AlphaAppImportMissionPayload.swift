import Foundation

struct AlphaAppImportMissionPayloadV0_2: Decodable, Identifiable {
    let missionID: String
    let contractVersion: String
    let appImportStatus: AlphaAppImportStatus
    let missionType: MissionType
    let missionArchetype: String
    let title: String
    let brief: String
    let hypothesis: String
    let whyThisMissionNow: String
    let coherenceSentence: String
    let riskLevel: String
    let route: [AlphaAppImportRouteItemV0_2]
    let feedbackModel: AlphaFeedbackModel
    let sourceTrace: AlphaSourceTrace
    let validation: AlphaPayloadValidation

    var id: String {
        missionID
    }

    var isApprovedCandidate: Bool {
        appImportStatus == .appImportCandidate &&
            validation.expectedClass == "approved_app_import_candidate"
    }

    var isApprovedReady: Bool {
        appImportStatus == .appImportReady &&
            validation.expectedClass == "approved_app_import_ready" &&
            route.allSatisfy { item in
                item.resolutionStatus == .resolved &&
                    (item.appleMusicID?.isEmpty == false || item.appleMusicURL != nil)
            }
    }

    var isApprovedForLocalImport: Bool {
        isApprovedCandidate || isApprovedReady
    }

    enum CodingKeys: String, CodingKey {
        case missionID = "mission_id"
        case contractVersion = "contract_version"
        case appImportStatus = "app_import_status"
        case missionType = "mission_type"
        case missionArchetype = "mission_archetype"
        case title
        case brief
        case hypothesis
        case whyThisMissionNow = "why_this_mission_now"
        case coherenceSentence = "coherence_sentence"
        case riskLevel = "risk_level"
        case route
        case feedbackModel = "feedback_model"
        case sourceTrace = "source_trace"
        case validation
    }
}

enum AlphaAppImportStatus: String, Codable {
    case reviewOnly = "review_only"
    case schemaValid = "schema_valid"
    case contractValid = "contract_valid"
    case needsRevision = "needs_revision"
    case rejectedProduct = "rejected_product"
    case appImportCandidate = "app_import_candidate"
    case appImportBlockedUnresolved = "app_import_blocked_unresolved"
    case appImportBlockedPolicy = "app_import_blocked_policy"
    case appImportReady = "app_import_ready"
}

struct AlphaAppImportRouteItemV0_2: Decodable {
    let missionItemID: String
    let sequenceIndex: Int
    let role: AlphaRouteItemRole
    let songTitle: String
    let artistName: String
    let albumTitle: String?
    let canonicalSongID: String?
    let canonicalArtistID: String?
    let canonicalAlbumID: String?
    let appleMusicID: String?
    let appleMusicURL: URL?
    let durationMS: Int
    let artworkURL: URL?
    let previewURL: URL?
    let resolutionStatus: AlphaResolutionStatus
    let expectedSignal: String
    let whyInRoute: String
    let reactionChipSetID: String?
    let riskFlags: [String]
    let sourceOpportunityID: String?
    let sourceMissionType: String?
    let targetObjectIDs: [String]
    let graphContextRefs: [String]

    enum CodingKeys: String, CodingKey {
        case missionItemID = "mission_item_id"
        case sequenceIndex = "sequence_index"
        case role
        case songTitle = "song_title"
        case artistName = "artist_name"
        case albumTitle = "album_title"
        case canonicalSongID = "canonical_song_id"
        case canonicalArtistID = "canonical_artist_id"
        case canonicalAlbumID = "canonical_album_id"
        case appleMusicID = "apple_music_id"
        case appleMusicURL = "apple_music_url"
        case durationMS = "duration_ms"
        case artworkURL = "artwork_url"
        case previewURL = "preview_url"
        case resolutionStatus = "resolution_status"
        case expectedSignal = "expected_signal"
        case whyInRoute = "why_in_route"
        case reactionChipSetID = "reaction_chip_set_id"
        case riskFlags = "risk_flags"
        case sourceOpportunityID = "source_opportunity_id"
        case sourceMissionType = "source_mission_type"
        case targetObjectIDs = "target_object_ids"
        case graphContextRefs = "graph_context_refs"
    }
}

enum AlphaRouteItemRole: String, Codable, CaseIterable {
    case anchor
    case context
    case bridge
    case boundary
    case probe
    case comparator
    case control

    var displayName: String {
        switch self {
        case .anchor:
            return "Anchor"
        case .context:
            return "Context"
        case .bridge:
            return "Bridge"
        case .boundary:
            return "Boundary"
        case .probe:
            return "Probe"
        case .comparator:
            return "Comparator"
        case .control:
            return "Control"
        }
    }
}

enum AlphaResolutionStatus: String, Codable, CaseIterable {
    case candidate
    case resolved
    case unresolved
    case blocked

    var mapsToPlaybackReady: Bool {
        self == .resolved
    }
}

struct AlphaFeedbackModel: Decodable {
    let chipSetID: String?
    let operationMapping: [String: AlphaFeedbackOperation]
    let surveyOKSemantics: String?
    let missionOKSemantics: String?

    enum CodingKeys: String, CodingKey {
        case chipSetID = "chip_set_id"
        case operationMapping = "operation_mapping"
        case surveyOKSemantics = "survey_ok_semantics"
        case missionOKSemantics = "mission_ok_semantics"
    }
}

enum AlphaFeedbackOperation: String, Codable, CaseIterable {
    case strongPositive = "strong_positive"
    case qualifiedPositive = "qualified_positive"
    case keepWaypoint = "keep_waypoint"
    case negative
    case skipOrNoSignal = "skip_or_no_signal"
    case issueWrongVersion = "issue_wrong_version"
    case issueUnavailable = "issue_unavailable"
}

enum AlphaFeedbackMapping {
    static func operation(for reactionValue: ReactionValue) -> AlphaFeedbackOperation? {
        switch reactionValue {
        case .hit:
            return .strongPositive
        case .partial:
            return .qualifiedPositive
        case .okShelf:
            return .keepWaypoint
        case .miss, .slop:
            return .negative
        case .skipped:
            return .skipOrNoSignal
        case .unresolved:
            return nil
        }
    }

    static let missingPrimaryUIOperations: [AlphaFeedbackOperation] = [
        .issueWrongVersion,
        .issueUnavailable
    ]
}

struct AlphaSourceTrace: Decodable {
    let sourceLayer: String?
    let sourceSelectorOutputRef: String?
    let sourceOpportunityRefs: [String]
    let sourceEvidenceSummary: AlphaSourceEvidenceSummary?
    let multiSourceRoute: Bool?
    let multiSourceRouteReason: String?

    enum CodingKeys: String, CodingKey {
        case sourceLayer = "source_layer"
        case sourceSelectorOutputRef = "source_selector_output_ref"
        case sourceOpportunityRefs = "source_opportunity_refs"
        case sourceEvidenceSummary = "source_evidence_summary"
        case multiSourceRoute = "multi_source_route"
        case multiSourceRouteReason = "multi_source_route_reason"
    }
}

struct AlphaSourceEvidenceSummary: Decodable {
    let profileID: String?
    let evidenceScale: Int?
    let samplingMode: String?
    let visibleEvidenceOnlyForSelector: Bool?
    let surveyOKSemantics: String?
    let missionOKSemantics: String?

    enum CodingKeys: String, CodingKey {
        case profileID = "profile_id"
        case evidenceScale = "evidence_scale"
        case samplingMode = "sampling_mode"
        case visibleEvidenceOnlyForSelector = "visible_evidence_only_for_selector"
        case surveyOKSemantics = "survey_ok_semantics"
        case missionOKSemantics = "mission_ok_semantics"
    }
}

struct AlphaPayloadValidation: Decodable {
    let expectedClass: String?
    let offlineReviewSourcePackID: String?

    enum CodingKeys: String, CodingKey {
        case expectedClass = "expected_class"
        case offlineReviewSourcePackID = "offline_review_source_pack_id"
    }
}

enum AlphaAppImportAdapter {
    private static let fixtureDate: Date = {
        ISO8601DateFormatter().date(from: "2026-05-29T00:00:00Z") ?? Date(timeIntervalSince1970: 0)
    }()

    static func decodeCandidatePayloads(from data: Data) throws -> [AlphaAppImportMissionPayloadV0_2] {
        let decoder = JSONDecoder()
        if let payloads = try? decoder.decode([AlphaAppImportMissionPayloadV0_2].self, from: data) {
            return payloads.filter(\.isApprovedCandidate)
        }

        if let fixtureSet = try? decoder.decode(AlphaGoldenFixtureSet.self, from: data) {
            return fixtureSet.approvedAppImportCandidates.filter(\.isApprovedCandidate)
        }

        throw DecodingError.dataCorrupted(
            DecodingError.Context(
                codingPath: [],
                debugDescription: "Expected Alpha app-import candidate array or golden fixture wrapper."
            )
        )
    }

    static func decodeImportablePayloads(from data: Data) throws -> [AlphaAppImportMissionPayloadV0_2] {
        let decoder = JSONDecoder()
        if let payloads = try? decoder.decode([AlphaAppImportMissionPayloadV0_2].self, from: data) {
            return payloads.filter(\.isApprovedForLocalImport)
        }

        if let fixtureSet = try? decoder.decode(AlphaGoldenFixtureSet.self, from: data) {
            return fixtureSet.approvedAppImportCandidates.filter(\.isApprovedForLocalImport)
        }

        throw DecodingError.dataCorrupted(
            DecodingError.Context(
                codingPath: [],
                debugDescription: "Expected Alpha app-import payload array or golden fixture wrapper."
            )
        )
    }

    static func makeMission(from payload: AlphaAppImportMissionPayloadV0_2) throws -> Mission {
        guard payload.isApprovedForLocalImport else {
            throw MissionImportError.blockedStatus(payload.appImportStatus.rawValue)
        }

        let items = payload.route
            .sorted { $0.sequenceIndex < $1.sequenceIndex }
            .enumerated()
            .map { index, item in
                makeMissionItem(
                    from: item,
                    missionID: normalizedMissionID(from: payload.missionID),
                    fallbackIndex: index + 1,
                    missionType: payload.missionType
                )
            }

        return Mission(
            schemaVersion: "mission.v0.2",
            missionID: normalizedMissionID(from: payload.missionID),
            missionTitle: payload.title,
            missionVersion: payload.contractVersion,
            createdAt: fixtureDate,
            missionType: payload.missionType,
            recommendedFormat: .playItemsInOrder,
            hypothesis: payload.hypothesis,
            inflationWarning: inflationWarning(for: payload),
            successBar: SuccessBar(
                minimumItemsToResolve: payload.route.count,
                minimumItemsToPlay: min(4, payload.route.count),
                minimumReactionsRequired: min(4, payload.route.count),
                requiresPhysicalIPhone: true,
                notes: successBarNotes(for: payload)
            ),
            runInstructions: MissionRunInstructions(
                listenInOrder: true,
                shuffleAllowed: false,
                rawText: payload.whyThisMissionNow
            ),
            postRunInferenceRules: nil,
            items: items,
            alphaAppImportStatus: payload.appImportStatus,
            alphaMissionArchetype: payload.missionArchetype,
            brief: payload.brief,
            whyThisMissionNow: payload.whyThisMissionNow,
            riskLevel: payload.riskLevel,
            sourceTraceSummary: sourceTraceSummary(for: payload)
        )
    }

    private static func inflationWarning(for payload: AlphaAppImportMissionPayloadV0_2) -> String {
        switch payload.appImportStatus {
        case .appImportReady:
            return "Local Alpha UAT fixture. Every route item has resolved Apple Music metadata; physical iPhone playback smoke is still required."
        default:
            return "Local Alpha fixture candidate. Music resolution is pending; do not treat as playback-ready until every item resolves."
        }
    }

    private static func successBarNotes(for payload: AlphaAppImportMissionPayloadV0_2) -> String {
        switch payload.appImportStatus {
        case .appImportReady:
            return "Converted from Alpha app_import_ready UAT fixture; route items are resolved for playback smoke."
        default:
            return "Converted from Alpha app_import_candidate fixture; candidate items must resolve before TestFlight playback."
        }
    }

    static func sourceTraceSummary(for payload: AlphaAppImportMissionPayloadV0_2) -> String {
        let profile = payload.sourceTrace.sourceEvidenceSummary?.profileID ?? "unknown profile"
        let scale = payload.sourceTrace.sourceEvidenceSummary?.evidenceScale.map(String.init) ?? "unknown"
        let mode = payload.sourceTrace.sourceEvidenceSummary?.samplingMode ?? "unknown mode"
        return "\(profile), \(scale) visible atoms, \(mode), \(payload.sourceTrace.sourceOpportunityRefs.count) source opportunity refs"
    }

    private static func makeMissionItem(
        from item: AlphaAppImportRouteItemV0_2,
        missionID: String,
        fallbackIndex: Int,
        missionType: MissionType
    ) -> MissionItem {
        let sequence = max(1, item.sequenceIndex)
        let displayIdentityKey = [
            "track",
            normalizedIdentityComponent(item.artistName),
            normalizedIdentityComponent(item.songTitle)
        ].joined(separator: ":")
        let sourceOpportunityID = item.sourceOpportunityID ?? "alpha_source_unknown"

        return MissionItem(
            itemID: normalizedItemID(from: item.missionItemID, missionID: missionID, index: sequence),
            sequence: sequence,
            itemType: .track,
            artist: item.artistName,
            title: item.songTitle,
            album: item.albumTitle,
            year: nil,
            whyIncluded: item.whyInRoute,
            expectedTestSignal: item.expectedSignal,
            playerCard: MissionPlayerCard(
                flipSide: MissionPlayerCardFlipSide(
                    songHypothesis: item.expectedSignal,
                    detail: "\(item.role.displayName): \(item.whyInRoute)"
                )
            ),
            feedbackChipSets: defaultFeedbackChipSets(role: item.role),
            appleMusicResolution: appleMusicResolution(from: item),
            candidateID: item.canonicalSongID ?? item.missionItemID,
            routeCandidateKey: "alpha:\(missionType.rawValue):\(sourceOpportunityID)",
            routeBatchDedupeKey: "song_recording:\(normalizedIdentityComponent(item.artistName)):\(normalizedIdentityComponent(item.songTitle))",
            routeDisplayIdentityKey: displayIdentityKey,
            notes: "Alpha role=\(item.role.rawValue); source_opportunity=\(sourceOpportunityID); source_mission_type=\(item.sourceMissionType ?? "unknown")",
            alphaRouteRole: item.role,
            alphaResolutionStatus: item.resolutionStatus,
            alphaSourceOpportunityID: item.sourceOpportunityID,
            alphaSourceMissionType: item.sourceMissionType,
            alphaTargetObjectIDs: item.targetObjectIDs,
            alphaGraphContextRefs: item.graphContextRefs
        )
    }

    private static func appleMusicResolution(from item: AlphaAppImportRouteItemV0_2) -> AppleMusicResolution {
        switch item.resolutionStatus {
        case .candidate:
            return AppleMusicResolution(
                status: .candidate,
                catalogID: nil,
                catalogURL: nil,
                artworkURL: item.artworkURL,
                storefront: nil,
                resolvedTitle: nil,
                resolvedArtist: nil,
                resolvedAlbum: nil,
                confidence: nil,
                resolver: .notAttempted,
                resolvedAt: nil,
                reason: "alpha_app_import_candidate_music_resolution_pending",
                candidateCount: nil,
                errorCode: nil,
                errorMessage: nil
            )
        case .resolved:
            return AppleMusicResolution(
                status: .resolved,
                catalogID: item.appleMusicID,
                catalogURL: item.appleMusicURL,
                artworkURL: item.artworkURL,
                storefront: nil,
                resolvedTitle: item.songTitle,
                resolvedArtist: item.artistName,
                resolvedAlbum: item.albumTitle,
                confidence: 1,
                resolver: .cached,
                resolvedAt: fixtureDate,
                reason: "alpha_app_import_payload_resolved",
                candidateCount: 1,
                errorCode: nil,
                errorMessage: nil
            )
        case .unresolved:
            return .unresolved(reason: "alpha_app_import_payload_unresolved")
        case .blocked:
            return AppleMusicResolution.marked(
                .blocked,
                reason: "alpha_app_import_payload_blocked",
                resolvedAt: fixtureDate
            )
        }
    }

    private static func defaultFeedbackChipSets(role: AlphaRouteItemRole) -> [String: [FeedbackChipOption]] {
        [
            ReactionValue.hit.rawValue: [
                FeedbackChipOption(
                    tagID: "TAG_ALPHA_STRONG_POSITIVE",
                    label: "Love",
                    description: "Strong positive signal for this route item."
                )
            ],
            ReactionValue.partial.rawValue: [
                FeedbackChipOption(
                    tagID: "TAG_ALPHA_QUALIFIED_POSITIVE",
                    label: "Like",
                    description: "Qualified positive signal."
                )
            ],
            ReactionValue.okShelf.rawValue: [
                FeedbackChipOption(
                    tagID: "TAG_ALPHA_KEEP_WAYPOINT",
                    label: "Ok / Keep",
                    description: "Weak non-failure waypoint evidence for mission listening, not a survey preference."
                )
            ],
            ReactionValue.miss.rawValue: [
                FeedbackChipOption(
                    tagID: "TAG_ALPHA_NEGATIVE",
                    label: role == .boundary ? "Boundary miss" : "Dislike",
                    description: "Negative signal for this route item."
                )
            ]
        ]
    }

    private static func normalizedMissionID(from rawValue: String) -> String {
        "MIS_\(normalizedToken(rawValue, maxLength: 96))"
    }

    private static func normalizedItemID(from rawValue: String, missionID: String, index: Int) -> String {
        let base = rawValue.isEmpty ? "\(missionID)_\(index)" : rawValue
        let token = normalizedToken(base, maxLength: 96)
        let prefix = String(format: "%02d", index)
        return token.isEmpty ? "\(missionID)_ITEM_\(prefix)" : "ITEM_\(prefix)_\(token)"
    }

    private static func normalizedToken(_ rawValue: String, maxLength: Int) -> String {
        let normalized = rawValue
            .uppercased()
            .components(separatedBy: CharacterSet.alphanumerics.inverted)
            .filter { !$0.isEmpty }
            .joined(separator: "_")
        return String(normalized.prefix(maxLength)).trimmingCharacters(in: CharacterSet(charactersIn: "_"))
    }

    private static func normalizedIdentityComponent(_ rawValue: String) -> String {
        rawValue
            .folding(options: [.caseInsensitive, .diacriticInsensitive], locale: Locale(identifier: "en_US_POSIX"))
            .components(separatedBy: CharacterSet.alphanumerics.inverted)
            .filter { !$0.isEmpty }
            .joined(separator: "-")
    }
}

private struct AlphaGoldenFixtureSet: Decodable {
    let approvedAppImportCandidates: [AlphaAppImportMissionPayloadV0_2]

    enum CodingKeys: String, CodingKey {
        case approvedAppImportCandidates = "approved_app_import_candidates"
    }
}

enum AlphaLocalFixtureLoader {
    static let approvedCandidateResourceName = "approved_alpha_app_import_candidates_v0_2"
    static let appImportReadyResourceName = "app_import_ready_alpha_uat_fixtures_v0_2"

    static func approvedCandidateData(bundle: Bundle = .main) throws -> Data {
        guard let url = bundle.url(forResource: approvedCandidateResourceName, withExtension: "json") else {
            throw MissionImportError.invalidMission("Missing bundled \(approvedCandidateResourceName).json.")
        }
        return try Data(contentsOf: url)
    }

    static func appImportReadyData(bundle: Bundle = .main) throws -> Data {
        guard let url = bundle.url(forResource: appImportReadyResourceName, withExtension: "json") else {
            throw MissionImportError.invalidMission("Missing bundled \(appImportReadyResourceName).json.")
        }
        return try Data(contentsOf: url)
    }
}
