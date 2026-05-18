import Foundation
#if canImport(MusicKit)
import MusicKit
#endif

struct Mission: Decodable, Identifiable {
    let schemaVersion: String
    let missionID: String
    let missionTitle: String
    let missionVersion: String
    let createdAt: Date
    let missionType: MissionType
    let recommendedFormat: RecommendedFormat
    let hypothesis: String
    let inflationWarning: String
    let successBar: SuccessBar
    let runInstructions: MissionRunInstructions?
    let postRunInferenceRules: [MissionInferenceRule]?
    let items: [MissionItem]

    var id: String {
        missionID
    }

    enum CodingKeys: String, CodingKey {
        case schemaVersion = "schema_version"
        case missionID = "mission_id"
        case missionTitle = "mission_title"
        case missionVersion = "mission_version"
        case createdAt = "created_at"
        case missionType = "mission_type"
        case recommendedFormat = "recommended_format"
        case hypothesis
        case inflationWarning = "inflation_warning"
        case successBar = "success_bar"
        case runInstructions = "run_instructions"
        case postRunInferenceRules = "post_run_inference_rules"
        case items
    }
}

enum MissionType: String, Decodable {
    case trackProbe = "track_probe"
    case albumTest = "album_test"
    case stationSeed = "station_seed"
    case playlistBleed = "playlist_bleed"
    case falseNearbyTest = "false_nearby_test"
}

enum RecommendedFormat: String, Decodable {
    case playItemsInOrder = "play_items_in_order"
    case albumFirst = "album_first"
    case stationFromSeed = "station_from_seed"
    case manualPlaylist = "manual_playlist"
    case singleTrackSpike = "single_track_spike"
}

struct SuccessBar: Decodable {
    let minimumItemsToResolve: Int
    let minimumItemsToPlay: Int
    let minimumReactionsRequired: Int
    let requiresPhysicalIPhone: Bool
    let notes: String?

    enum CodingKeys: String, CodingKey {
        case minimumItemsToResolve = "minimum_items_to_resolve"
        case minimumItemsToPlay = "minimum_items_to_play"
        case minimumReactionsRequired = "minimum_reactions_required"
        case requiresPhysicalIPhone = "requires_physical_iphone"
        case notes
    }
}

struct MissionItem: Decodable, Identifiable {
    let itemID: String
    let sequence: Int
    let itemType: MissionItemType
    let artist: String
    let title: String
    let album: String?
    let year: Int?
    let whyIncluded: String?
    let expectedTestSignal: String?
    let playerCard: MissionPlayerCard?
    let feedbackChipSets: [String: [FeedbackChipOption]]?
    let appleMusicResolution: AppleMusicResolution
    let notes: String?

    var id: String {
        itemID
    }

    enum CodingKeys: String, CodingKey {
        case itemID = "item_id"
        case sequence
        case itemType = "item_type"
        case artist
        case title
        case album
        case year
        case whyIncluded = "why_included"
        case expectedTestSignal = "expected_test_signal"
        case playerCard = "player_card"
        case feedbackChipSets = "feedback_chip_sets"
        case appleMusicResolution = "apple_music_resolution"
        case notes
    }

    func feedbackChips(for reactionValue: ReactionValue) -> [FeedbackChipOption] {
        feedbackChipSets?[reactionValue.rawValue] ?? []
    }
}

struct MissionRunInstructions: Decodable {
    let listenInOrder: Bool?
    let shuffleAllowed: Bool?
    let rawText: String?

    enum CodingKeys: String, CodingKey {
        case listenInOrder = "listen_in_order"
        case shuffleAllowed = "shuffle_allowed"
        case rawText = "raw_text"
    }
}

struct MissionInferenceRule: Decodable {
    let trigger: String
    let inference: String
}

struct MissionPlayerCard: Decodable {
    let flipSide: MissionPlayerCardFlipSide?

    enum CodingKeys: String, CodingKey {
        case flipSide = "flip_side"
    }
}

struct MissionPlayerCardFlipSide: Decodable {
    let songHypothesis: String?
    let detail: String?

    enum CodingKeys: String, CodingKey {
        case songHypothesis = "song_hypothesis"
        case detail
    }
}

struct FeedbackChipOption: Codable, Identifiable, Hashable {
    let tagID: String
    let label: String
    let description: String?

    var id: String {
        tagID
    }

    enum CodingKeys: String, CodingKey {
        case tagID = "tag_id"
        case label
        case description
    }

    func reactionTag(primaryReactionValue: ReactionValue) -> ReactionTag {
        ReactionTag(
            tagID: tagID,
            label: label,
            primaryReactionValue: primaryReactionValue,
            description: description
        )
    }
}

enum MissionItemType: String, Codable {
    case track
    case album
}

struct AppleMusicResolution: Codable {
    let status: ResolutionStatus
    let catalogID: String?
    let catalogURL: URL?
    let artworkURL: URL?
    let storefront: String?
    let resolvedTitle: String?
    let resolvedArtist: String?
    let resolvedAlbum: String?
    let confidence: Double?
    let resolver: ResolverKind?
    let resolvedAt: Date?
    let reason: String?
    let candidateCount: Int?
    let errorCode: String?
    let errorMessage: String?

    enum CodingKeys: String, CodingKey {
        case status
        case catalogID = "catalog_id"
        case catalogURL = "catalog_url"
        case artworkURL = "artwork_url"
        case storefront
        case resolvedTitle = "resolved_title"
        case resolvedArtist = "resolved_artist"
        case resolvedAlbum = "resolved_album"
        case confidence
        case resolver
        case resolvedAt = "resolved_at"
        case reason
        case candidateCount = "candidate_count"
        case errorCode = "error_code"
        case errorMessage = "error_message"
    }

    static func unresolved(reason: String = "not_attempted") -> AppleMusicResolution {
        AppleMusicResolution(
            status: .unresolved,
            catalogID: nil,
            catalogURL: nil,
            artworkURL: nil,
            storefront: nil,
            resolvedTitle: nil,
            resolvedArtist: nil,
            resolvedAlbum: nil,
            confidence: nil,
            resolver: .notAttempted,
            resolvedAt: nil,
            reason: reason,
            candidateCount: nil,
            errorCode: nil,
            errorMessage: nil
        )
    }

    static func marked(_ status: ResolutionStatus, reason: String, resolvedAt: Date) -> AppleMusicResolution {
        AppleMusicResolution(
            status: status,
            catalogID: nil,
            catalogURL: nil,
            artworkURL: nil,
            storefront: nil,
            resolvedTitle: nil,
            resolvedArtist: nil,
            resolvedAlbum: nil,
            confidence: nil,
            resolver: .system,
            resolvedAt: resolvedAt,
            reason: reason,
            candidateCount: nil,
            errorCode: nil,
            errorMessage: nil
        )
    }

    static func failed(
        resolver: ResolverKind,
        resolvedAt: Date,
        reason: String,
        error: Error
    ) -> AppleMusicResolution {
        let nsError = error as NSError

        return AppleMusicResolution(
            status: .failed,
            catalogID: nil,
            catalogURL: nil,
            artworkURL: nil,
            storefront: nil,
            resolvedTitle: nil,
            resolvedArtist: nil,
            resolvedAlbum: nil,
            confidence: nil,
            resolver: resolver,
            resolvedAt: resolvedAt,
            reason: reason,
            candidateCount: nil,
            errorCode: "\(nsError.domain)#\(nsError.code)",
            errorMessage: error.musicAtlasDiagnosticDescription
        )
    }
}

enum ResolutionStatus: String, Codable, CaseIterable {
    case unresolved
    case resolved
    case ambiguous
    case skipped
    case unavailableRegion = "unavailable_region"
    case unavailableSubscription = "unavailable_subscription"
    case failed
}

enum ResolverKind: String, Codable {
    case notAttempted = "not_attempted"
    case automaticSearch = "automatic_search"
    case manualSelection = "manual_selection"
    case cached
    case system
}

extension AppleMusicResolution {
    var isDevelopmentStubEvidence: Bool {
        storefront == "dev_stub" ||
        catalogID?.hasPrefix("stub_") == true ||
        reason == "stubbed_simulated_resolution_for_dev_export"
    }
}

extension Error {
    var musicAtlasDiagnosticDescription: String {
        let nsError = self as NSError
        var parts = [
            localizedDescription,
            "domain=\(nsError.domain)",
            "code=\(nsError.code)"
        ]

        if let tokenErrorName = musicAtlasTokenRequestErrorName(nsError: nsError) {
            parts.append("music_token_request_error=\(tokenErrorName)")
        }

        if let failureReason = nsError.localizedFailureReason, !failureReason.isEmpty {
            parts.append("failure_reason=\(failureReason)")
        }

        if let recoverySuggestion = nsError.localizedRecoverySuggestion, !recoverySuggestion.isEmpty {
            parts.append("recovery=\(recoverySuggestion)")
        }

        return parts.joined(separator: " | ")
    }

    private func musicAtlasTokenRequestErrorName(nsError: NSError) -> String? {
        #if canImport(MusicKit)
        if let tokenError = self as? MusicTokenRequestError {
            return tokenError.rawValue
        }
        #endif

        guard nsError.domain == "MusicKit.MusicTokenRequestError"
            || nsError.domain == "MusicKit.MusicTokenReqeustError" else {
            return nil
        }

        switch nsError.code {
        case 0:
            return "unknown"
        case 1:
            return "permissionDenied"
        case 2:
            return "userTokenRevoked"
        case 3:
            return "userNotSignedIn"
        case 4:
            return "privacyAcknowledgementRequired"
        case 5:
            return "developerTokenRequestFailed"
        case 6:
            return "userTokenRequestFailed"
        default:
            return "unmapped_code_\(nsError.code)"
        }
    }
}
