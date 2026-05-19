import Foundation

enum SurveyItemKind: String, Codable, CaseIterable, Identifiable {
    case artist
    case album
    case song

    var id: String {
        rawValue
    }

    var displayName: String {
        switch self {
        case .artist:
            return "Artists"
        case .album:
            return "Albums"
        case .song:
            return "Songs"
        }
    }
}

enum SurveySignalState: String, Codable, CaseIterable, Identifiable {
    case dontKnow = "dont_know"
    case fine
    case like
    case favorite
    case notForMe = "not_for_me"

    var id: String {
        rawValue
    }

    var displayName: String {
        switch self {
        case .dontKnow:
            return "Don't Know"
        case .fine:
            return "Fine"
        case .like:
            return "Like"
        case .favorite:
            return "Favorite"
        case .notForMe:
            return "Not For Me"
        }
    }

    var next: SurveySignalState {
        switch self {
        case .dontKnow:
            return .fine
        case .fine:
            return .like
        case .like:
            return .favorite
        case .favorite:
            return .notForMe
        case .notForMe:
            return .dontKnow
        }
    }
}

enum SurveyNuance: String, Codable, CaseIterable, Identifiable {
    case usedToLike = "used_to_like"
    case respectMoreThanCrave = "respect_more_than_crave"
    case oneSongOnly = "one_song_only"
    case oneAlbumOnly = "one_album_only"
    case goodButNotFavorite = "good_but_not_favorite"
    case nostalgia = "nostalgia_cultural_furniture"
    case wrongVersionOrEra = "wrong_version_or_era"
    case knowButNotWell = "know_but_not_well"

    var id: String {
        rawValue
    }

    var label: String {
        switch self {
        case .usedToLike:
            return "Used to like this"
        case .respectMoreThanCrave:
            return "Respect more than crave"
        case .oneSongOnly:
            return "One song only"
        case .oneAlbumOnly:
            return "One album only"
        case .goodButNotFavorite:
            return "Good, not favorite"
        case .nostalgia:
            return "Nostalgia / furniture"
        case .wrongVersionOrEra:
            return "Wrong version / era"
        case .knowButNotWell:
            return "Know this, not well"
        }
    }
}

enum SurveyItemSource: String, Codable, CaseIterable {
    case appleMusicDerived = "apple_music_derived"
    case broadCalibration = "broad_calibration"
    case responseAdjacent = "response_adjacent"
    case sleeperProbe = "sleeper_probe"
    case rejectionProbe = "rejection_probe"
    case appleMusicLooseEnd = "apple_music_loose_end"
    case objectSpecific = "object_specific"
    case advancedFilter = "advanced_filter"
}

enum SurveyBatchObjective: String, Codable, CaseIterable {
    case recognizeKnownTerritory = "recognize_known_territory"
    case confirmLikelyRegion = "confirm_likely_region"
    case testAdjacentRoad = "test_adjacent_road"
    case probeSleeperFrontier = "probe_sleeper_frontier"
    case checkDeadEnd = "check_dead_end"
    case resolveContradiction = "resolve_contradiction"
    case separateObjectTaste = "separate_object_taste"
    case calibrateBroadly = "calibrate_broadly"
}

struct SurveyItem: Codable, Identifiable, Hashable {
    let id: String
    let kind: SurveyItemKind
    let title: String
    let subtitle: String?
    let artworkURL: URL?
    let source: SurveyItemSource
    let objective: SurveyBatchObjective
    let rationale: String
    let artworkSeed: String
}

struct SurveyGridPage: Identifiable {
    let id: String
    let title: String
    let subtitle: String
    let kind: SurveyItemKind
    let pageIndex: Int
    let isOptional: Bool
    let items: [SurveyItem]
}

struct SurveyResponse: Codable, Equatable {
    let itemID: String
    let itemKind: SurveyItemKind
    var state: SurveySignalState
    var nuances: [SurveyNuance]
    var note: String
    var updatedAt: Date

    enum CodingKeys: String, CodingKey {
        case itemID = "item_id"
        case itemKind = "item_kind"
        case state
        case nuances
        case note
        case updatedAt = "updated_at"
    }
}

struct SurveyFreeformSignal: Codable, Identifiable, Equatable {
    let id: UUID
    let text: String
    let parsedClaims: [String]
    let confidence: String
    let requiresConfirmation: Bool
    let capturedAt: Date

    enum CodingKeys: String, CodingKey {
        case id
        case text
        case parsedClaims = "parsed_claims"
        case confidence
        case requiresConfirmation = "requires_confirmation"
        case capturedAt = "captured_at"
    }
}

enum SurveyStep: String, Codable, CaseIterable {
    case welcome
    case connectAppleMusic
    case artistPage1
    case artistPage2
    case artistPage3Prompt
    case artistPage3
    case albumPage1
    case songPage1
    case deeperPrompt
    case advancedSurvey
    case readout
}

enum SurveyAdvancedFilter: String, Codable, CaseIterable, Identifiable {
    case era
    case genre
    case countryRegion = "country_region"
    case scene
    case popularity
    case likelyDeadEnds = "likely_dead_ends"
    case sleepers
    case libraryUnrated = "library_unrated"

    var id: String {
        rawValue
    }

    var label: String {
        switch self {
        case .era:
            return "Era"
        case .genre:
            return "Genre"
        case .countryRegion:
            return "Country"
        case .scene:
            return "Scene"
        case .popularity:
            return "Popularity"
        case .likelyDeadEnds:
            return "Dead Ends"
        case .sleepers:
            return "Sleepers"
        case .libraryUnrated:
            return "Library"
        }
    }
}

struct SurveySummary {
    let totalResponses: Int
    let favorites: [SurveyItem]
    let likes: [SurveyItem]
    let fine: [SurveyItem]
    let notForMe: [SurveyItem]
    let unknownCount: Int
    let freeformSignals: [SurveyFreeformSignal]

    var visibleSignalCount: Int {
        totalResponses + freeformSignals.count
    }
}
