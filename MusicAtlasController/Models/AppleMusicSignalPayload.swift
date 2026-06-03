import Foundation

struct AppleMusicSignalPayload: Codable, Equatable {
    static let currentSchemaVersion = "apple_music_signal_payload.v0.2"
    static let currentProbeVersion = "apple_probe.v0.5"

    let schemaVersion: String
    let payloadID: String
    let probeVersion: String
    let capturedAt: Date
    let storefront: String?
    let authorization: AppleMusicSignalAuthorization
    let primarySignalSources: AppleMusicPrimarySignalSources
    let contextSources: AppleMusicContextSignalSources
    let observedResourceAnnotations: AppleMusicObservedResourceAnnotations
    let catalogHydration: AppleMusicCatalogHydration
    let excludedOrDiagnosticSources: [AppleMusicSignalSourceSection]

    enum CodingKeys: String, CodingKey {
        case schemaVersion = "schema_version"
        case payloadID = "payload_id"
        case probeVersion = "probe_version"
        case capturedAt = "captured_at"
        case storefront
        case authorization
        case primarySignalSources = "primary_signal_sources"
        case contextSources = "context_sources"
        case observedResourceAnnotations = "observed_resource_annotations"
        case catalogHydration = "catalog_hydration"
        case excludedOrDiagnosticSources = "excluded_or_diagnostic_sources"
    }

    init(
        payloadID: String,
        capturedAt: Date,
        storefront: String?,
        authorization: AppleMusicSignalAuthorization,
        primarySignalSources: AppleMusicPrimarySignalSources,
        contextSources: AppleMusicContextSignalSources,
        observedResourceAnnotations: AppleMusicObservedResourceAnnotations,
        catalogHydration: AppleMusicCatalogHydration,
        excludedOrDiagnosticSources: [AppleMusicSignalSourceSection],
        schemaVersion: String = AppleMusicSignalPayload.currentSchemaVersion,
        probeVersion: String = AppleMusicSignalPayload.currentProbeVersion
    ) {
        self.schemaVersion = schemaVersion
        self.payloadID = payloadID
        self.probeVersion = probeVersion
        self.capturedAt = capturedAt
        self.storefront = storefront
        self.authorization = authorization
        self.primarySignalSources = primarySignalSources
        self.contextSources = contextSources
        self.observedResourceAnnotations = observedResourceAnnotations
        self.catalogHydration = catalogHydration
        self.excludedOrDiagnosticSources = excludedOrDiagnosticSources
    }

    var usefulPrimarySignalCount: Int {
        primarySignalSources.sections.filter { $0.status == .captured && !$0.items.isEmpty }.count
    }

    var allObservedResources: [AppleMusicSignalResource] {
        primarySignalSources.sections.flatMap(\.items) +
            contextSources.sections.flatMap(\.items) +
            observedResourceAnnotations.sections.flatMap(\.items)
    }

    var allProbeErrors: [AppleMusicSignalProbeError] {
        authorization.errors +
            primarySignalSources.sections.flatMap(\.errors) +
            contextSources.sections.flatMap(\.errors) +
            observedResourceAnnotations.sections.flatMap(\.errors) +
            catalogHydration.errors +
            excludedOrDiagnosticSources.flatMap(\.errors)
    }

    var summaryDescription: String {
        [
            "\(usefulPrimarySignalCount) useful primary sources",
            "\(allObservedResources.count) observed resources",
            "\(catalogHydration.resources.count) catalog identities",
            "\(excludedOrDiagnosticSources.count) diagnostic-only sources"
        ].joined(separator: ", ")
    }

    static func make(
        capturedAt: Date,
        storefront: String?,
        authorization: AppleMusicSignalAuthorization,
        primarySignalSources: AppleMusicPrimarySignalSources,
        contextSources: AppleMusicContextSignalSources,
        observedResourceAnnotations: AppleMusicObservedResourceAnnotations,
        excludedOrDiagnosticSources: [AppleMusicSignalSourceSection]
    ) -> AppleMusicSignalPayload {
        let observedResources = primarySignalSources.sections.flatMap(\.items) +
            contextSources.sections.flatMap(\.items) +
            observedResourceAnnotations.sections.flatMap(\.items)
        return AppleMusicSignalPayload(
            payloadID: "apple_music_signal_payload:\(UUID().uuidString)",
            capturedAt: capturedAt,
            storefront: storefront,
            authorization: authorization,
            primarySignalSources: primarySignalSources,
            contextSources: contextSources,
            observedResourceAnnotations: observedResourceAnnotations,
            catalogHydration: AppleMusicCatalogHydration(
                status: observedResources.isEmpty ? .empty : .captured,
                resources: catalogHydrationResources(from: observedResources),
                errors: []
            ),
            excludedOrDiagnosticSources: excludedOrDiagnosticSources
        )
    }

    static func unavailable(
        capturedAt: Date,
        authorizationStatus: String,
        canRequestAuthorization: Bool,
        storefront: String?,
        error: AppleMusicSignalProbeError
    ) -> AppleMusicSignalPayload {
        let authorization = AppleMusicSignalAuthorization(
            musicAuthorizationStatus: authorizationStatus,
            canRequestAuthorization: canRequestAuthorization,
            subscriptionStatus: "unavailable",
            tokenStatus: "unavailable",
            errors: [error]
        )
        return make(
            capturedAt: capturedAt,
            storefront: storefront,
            authorization: authorization,
            primarySignalSources: .unavailable(capturedAt: capturedAt, error: error),
            contextSources: .unavailable(capturedAt: capturedAt, error: error),
            observedResourceAnnotations: .empty(capturedAt: capturedAt),
            excludedOrDiagnosticSources: []
        )
    }

    static func catalogHydrationResources(from observedResources: [AppleMusicSignalResource]) -> [AppleMusicSignalResource] {
        var seen = Set<String>()
        return observedResources.compactMap { resource in
            let identity = resource.catalogID ?? resource.appleID ?? resource.libraryID ?? resource.sourceItemID
            guard seen.insert("\(resource.resourceType.rawValue):\(identity)").inserted else {
                return nil
            }
            return resource.catalogIdentityCopy()
        }
    }
}

struct AppleMusicSignalAuthorization: Codable, Equatable {
    let musicAuthorizationStatus: String
    let canRequestAuthorization: Bool
    let subscriptionStatus: String
    let tokenStatus: String
    let errors: [AppleMusicSignalProbeError]

    var probeErrors: [AppleMusicSignalProbeError] { errors }

    init(
        musicAuthorizationStatus: String,
        canRequestAuthorization: Bool,
        subscriptionStatus: String = "unknown",
        tokenStatus: String = "unknown",
        errors: [AppleMusicSignalProbeError] = []
    ) {
        self.musicAuthorizationStatus = musicAuthorizationStatus
        self.canRequestAuthorization = canRequestAuthorization
        self.subscriptionStatus = subscriptionStatus
        self.tokenStatus = tokenStatus
        self.errors = errors
    }

    init(
        musicAuthorizationStatus: String,
        canRequestAuthorization: Bool,
        subscriptionStatus: String = "unknown",
        tokenStatus: String = "unknown",
        probeErrors: [AppleMusicSignalProbeError]
    ) {
        self.init(
            musicAuthorizationStatus: musicAuthorizationStatus,
            canRequestAuthorization: canRequestAuthorization,
            subscriptionStatus: subscriptionStatus,
            tokenStatus: tokenStatus,
            errors: probeErrors
        )
    }

    enum CodingKeys: String, CodingKey {
        case musicAuthorizationStatus = "music_authorization_status"
        case canRequestAuthorization = "can_request_authorization"
        case subscriptionStatus = "subscription_status"
        case tokenStatus = "token_status"
        case errors
        case legacyProbeErrors = "probe_errors"
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        musicAuthorizationStatus = try container.decode(String.self, forKey: .musicAuthorizationStatus)
        canRequestAuthorization = try container.decode(Bool.self, forKey: .canRequestAuthorization)
        subscriptionStatus = try container.decodeIfPresent(String.self, forKey: .subscriptionStatus) ?? "unknown"
        tokenStatus = try container.decodeIfPresent(String.self, forKey: .tokenStatus) ?? "unknown"
        errors = try container.decodeIfPresent([AppleMusicSignalProbeError].self, forKey: .errors)
            ?? container.decodeIfPresent([AppleMusicSignalProbeError].self, forKey: .legacyProbeErrors)
            ?? []
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(musicAuthorizationStatus, forKey: .musicAuthorizationStatus)
        try container.encode(canRequestAuthorization, forKey: .canRequestAuthorization)
        try container.encode(subscriptionStatus, forKey: .subscriptionStatus)
        try container.encode(tokenStatus, forKey: .tokenStatus)
        try container.encode(errors, forKey: .errors)
    }
}

struct AppleMusicPrimarySignalSources: Codable, Equatable {
    let heavyRotation: AppleMusicSignalSourceSection
    let recentlyPlayedTracks: AppleMusicSignalSourceSection
    let librarySongPlayCount: AppleMusicSignalSourceSection
    let librarySongLastPlayed: AppleMusicSignalSourceSection
    let librarySongLibraryAdded: AppleMusicSignalSourceSection
    let libraryAlbumLibraryAdded: AppleMusicSignalSourceSection
    let personalRecommendations: AppleMusicSignalSourceSection

    enum CodingKeys: String, CodingKey {
        case heavyRotation = "heavy_rotation"
        case recentlyPlayedTracks = "recently_played_tracks"
        case librarySongPlayCount = "library_song_play_count"
        case librarySongLastPlayed = "library_song_last_played"
        case librarySongLibraryAdded = "library_song_library_added"
        case libraryAlbumLibraryAdded = "library_album_library_added"
        case personalRecommendations = "personal_recommendations"
    }

    var sections: [AppleMusicSignalSourceSection] {
        [heavyRotation, recentlyPlayedTracks, librarySongPlayCount, librarySongLastPlayed, librarySongLibraryAdded, libraryAlbumLibraryAdded, personalRecommendations]
    }

    static func unavailable(capturedAt: Date, error: AppleMusicSignalProbeError? = nil) -> AppleMusicPrimarySignalSources {
        AppleMusicPrimarySignalSources(
            heavyRotation: .unavailable(sourceID: "heavy_rotation", cap: 10, capturedAt: capturedAt, error: error),
            recentlyPlayedTracks: .unavailable(sourceID: "recently_played_tracks", cap: 500, capturedAt: capturedAt, error: error),
            librarySongPlayCount: .unavailable(sourceID: "library_song_play_count", cap: 200, capturedAt: capturedAt, error: error),
            librarySongLastPlayed: .unavailable(sourceID: "library_song_last_played", cap: 100, capturedAt: capturedAt, error: error),
            librarySongLibraryAdded: .unavailable(sourceID: "library_song_library_added", cap: 100, capturedAt: capturedAt, error: error),
            libraryAlbumLibraryAdded: .unavailable(sourceID: "library_album_library_added", cap: 100, capturedAt: capturedAt, error: error),
            personalRecommendations: .unavailable(sourceID: "personal_recommendations", cap: 50, capturedAt: capturedAt, error: error)
        )
    }
}

struct AppleMusicContextSignalSources: Codable, Equatable {
    let playlistContexts: AppleMusicSignalSourceSection
    let playlistTrackSamples: AppleMusicSignalSourceSection
    let replaySummary: AppleMusicSignalSourceSection
    let replayTopArtists: AppleMusicSignalSourceSection?
    let replayTopAlbums: AppleMusicSignalSourceSection?
    let replayTopSongs: AppleMusicSignalSourceSection?

    enum CodingKeys: String, CodingKey {
        case playlistContexts = "playlist_contexts"
        case playlistTrackSamples = "playlist_track_samples"
        case replaySummary = "replay_summary"
        case replayTopArtists = "replay_top_artists"
        case replayTopAlbums = "replay_top_albums"
        case replayTopSongs = "replay_top_songs"
    }

    init(
        playlistContexts: AppleMusicSignalSourceSection,
        playlistTrackSamples: AppleMusicSignalSourceSection,
        replaySummary: AppleMusicSignalSourceSection,
        replayTopArtists: AppleMusicSignalSourceSection? = nil,
        replayTopAlbums: AppleMusicSignalSourceSection? = nil,
        replayTopSongs: AppleMusicSignalSourceSection? = nil
    ) {
        self.playlistContexts = playlistContexts
        self.playlistTrackSamples = playlistTrackSamples
        self.replaySummary = replaySummary
        self.replayTopArtists = replayTopArtists
        self.replayTopAlbums = replayTopAlbums
        self.replayTopSongs = replayTopSongs
    }

    var sections: [AppleMusicSignalSourceSection] {
        [playlistContexts, playlistTrackSamples, replaySummary] +
            [replayTopArtists, replayTopAlbums, replayTopSongs].compactMap { $0 }
    }

    static func unavailable(capturedAt: Date, error: AppleMusicSignalProbeError? = nil) -> AppleMusicContextSignalSources {
        AppleMusicContextSignalSources(
            playlistContexts: .unavailable(sourceID: "playlist_contexts", cap: 50, capturedAt: capturedAt, error: error),
            playlistTrackSamples: .unavailable(sourceID: "playlist_track_samples", cap: 250, capturedAt: capturedAt, error: error),
            replaySummary: .unavailable(sourceID: "replay_summary", cap: 301, capturedAt: capturedAt, error: error),
            replayTopArtists: .unavailable(sourceID: "replay_top_artists", cap: 50, capturedAt: capturedAt, error: error),
            replayTopAlbums: .unavailable(sourceID: "replay_top_albums", cap: 50, capturedAt: capturedAt, error: error),
            replayTopSongs: .unavailable(sourceID: "replay_top_songs", cap: 200, capturedAt: capturedAt, error: error)
        )
    }
}

struct AppleMusicObservedResourceAnnotations: Codable, Equatable {
    let favoriteResources: AppleMusicSignalSourceSection
    let ratedResources: AppleMusicSignalSourceSection

    enum CodingKeys: String, CodingKey {
        case favoriteResources = "favorite_resources"
        case ratedResources = "rated_resources"
    }

    var sections: [AppleMusicSignalSourceSection] {
        [favoriteResources, ratedResources]
    }

    static func empty(capturedAt: Date) -> AppleMusicObservedResourceAnnotations {
        AppleMusicObservedResourceAnnotations(
            favoriteResources: .empty(sourceID: "favorite_resources", cap: 100, capturedAt: capturedAt),
            ratedResources: .empty(sourceID: "rated_resources", cap: 100, capturedAt: capturedAt)
        )
    }
}

struct AppleMusicCatalogHydration: Codable, Equatable {
    let status: AppleMusicSignalSourceStatus
    let resources: [AppleMusicSignalResource]
    let errors: [AppleMusicSignalProbeError]
}

struct AppleMusicSignalSourceSection: Codable, Equatable {
    let sourceID: String
    let status: AppleMusicSignalSourceStatus
    let cap: Int
    let capturedAt: Date?
    let items: [AppleMusicSignalResource]
    let errors: [AppleMusicSignalProbeError]
    let excludedFromSurveyEvidence: Bool?
    let diagnosticReason: String?

    enum CodingKeys: String, CodingKey {
        case sourceID = "source_id"
        case status
        case cap
        case capturedAt = "captured_at"
        case items
        case errors
        case excludedFromSurveyEvidence = "excluded_from_survey_evidence"
        case diagnosticReason = "diagnostic_reason"
    }

    init(
        sourceID: String,
        status: AppleMusicSignalSourceStatus,
        cap: Int,
        capturedAt: Date?,
        items: [AppleMusicSignalResource],
        errors: [AppleMusicSignalProbeError],
        excludedFromSurveyEvidence: Bool? = nil,
        diagnosticReason: String? = nil
    ) {
        self.sourceID = sourceID
        self.status = status
        self.cap = cap
        self.capturedAt = capturedAt
        self.items = Array(items.prefix(cap))
        self.errors = errors
        self.excludedFromSurveyEvidence = excludedFromSurveyEvidence
        self.diagnosticReason = diagnosticReason
    }

    static func captured(sourceID: String, cap: Int, capturedAt: Date, items: [AppleMusicSignalResource], errors: [AppleMusicSignalProbeError] = []) -> AppleMusicSignalSourceSection {
        let status: AppleMusicSignalSourceStatus = errors.isEmpty ? (items.isEmpty ? .empty : .captured) : (items.isEmpty ? .error : .captured)
        return AppleMusicSignalSourceSection(sourceID: sourceID, status: status, cap: cap, capturedAt: capturedAt, items: items, errors: errors)
    }

    static func empty(sourceID: String, cap: Int, capturedAt: Date) -> AppleMusicSignalSourceSection {
        AppleMusicSignalSourceSection(sourceID: sourceID, status: .empty, cap: cap, capturedAt: capturedAt, items: [], errors: [])
    }

    static func unavailable(sourceID: String, cap: Int, capturedAt: Date, error: AppleMusicSignalProbeError? = nil) -> AppleMusicSignalSourceSection {
        AppleMusicSignalSourceSection(
            sourceID: sourceID,
            status: .unavailable,
            cap: cap,
            capturedAt: capturedAt,
            items: [],
            errors: [error ?? AppleMusicSignalProbeError(source: sourceID, code: "unavailable", message: "\(sourceID) is unavailable in this probe boundary.")]
        )
    }

    static func diagnosticExcluded(sourceID: String, cap: Int, capturedAt: Date, reason: String, items: [AppleMusicSignalResource]) -> AppleMusicSignalSourceSection {
        AppleMusicSignalSourceSection(
            sourceID: sourceID,
            status: items.isEmpty ? .empty : .captured,
            cap: cap,
            capturedAt: capturedAt,
            items: items.map { $0.diagnosticExcludedCopy(sourceID: sourceID) },
            errors: [],
            excludedFromSurveyEvidence: true,
            diagnosticReason: reason
        )
    }
}

enum AppleMusicSignalSourceStatus: String, Codable, Equatable {
    case captured
    case empty
    case unavailable
    case error
    case notRequested = "not_requested"
}

struct AppleMusicSignalResource: Codable, Equatable, Identifiable {
    let sourceItemID: String
    let resourceType: AppleMusicSignalResourceType
    let appleID: String?
    let catalogID: String?
    let libraryID: String?
    let persistentID: String?
    let displayName: String
    let artistName: String?
    let albumTitle: String?
    let playlistName: String?
    let curatorName: String?
    let genreNames: [String]
    let playCount: Int?
    let lastPlayedAt: Date?
    let libraryAddedAt: Date?
    let releaseDate: String?
    let url: String?
    let artworkURL: String?
    let evidenceBasis: AppleMusicEvidenceBasis
    let sourceConfidence: AppleMusicSignalSourceConfidence
    let observedSourceRefs: [String]

    var id: String { sourceItemID }

    enum CodingKeys: String, CodingKey {
        case sourceItemID = "source_item_id"
        case resourceType = "resource_type"
        case appleID = "apple_id"
        case catalogID = "catalog_id"
        case libraryID = "library_id"
        case persistentID = "persistent_id"
        case displayName = "display_name"
        case artistName = "artist_name"
        case albumTitle = "album_title"
        case playlistName = "playlist_name"
        case curatorName = "curator_name"
        case genreNames = "genre_names"
        case playCount = "play_count"
        case lastPlayedAt = "last_played_at"
        case libraryAddedAt = "library_added_at"
        case releaseDate = "release_date"
        case url
        case artworkURL = "artwork_url"
        case evidenceBasis = "evidence_basis"
        case sourceConfidence = "source_confidence"
        case observedSourceRefs = "observed_source_refs"
    }

    init(
        sourceItemID: String,
        resourceType: AppleMusicSignalResourceType,
        appleID: String? = nil,
        catalogID: String? = nil,
        libraryID: String? = nil,
        persistentID: String? = nil,
        displayName: String,
        artistName: String? = nil,
        albumTitle: String? = nil,
        playlistName: String? = nil,
        curatorName: String? = nil,
        genreNames: [String] = [],
        playCount: Int? = nil,
        lastPlayedAt: Date? = nil,
        libraryAddedAt: Date? = nil,
        releaseDate: String? = nil,
        url: String? = nil,
        artworkURL: String? = nil,
        evidenceBasis: AppleMusicEvidenceBasis,
        sourceConfidence: AppleMusicSignalSourceConfidence,
        observedSourceRefs: [String]
    ) {
        self.sourceItemID = sourceItemID
        self.resourceType = resourceType
        self.appleID = appleID
        self.catalogID = catalogID
        self.libraryID = libraryID
        self.persistentID = persistentID
        self.displayName = displayName
        self.artistName = artistName
        self.albumTitle = albumTitle
        self.playlistName = playlistName
        self.curatorName = curatorName
        self.genreNames = genreNames
        self.playCount = playCount
        self.lastPlayedAt = lastPlayedAt
        self.libraryAddedAt = libraryAddedAt
        self.releaseDate = releaseDate
        self.url = url
        self.artworkURL = artworkURL
        self.evidenceBasis = evidenceBasis
        self.sourceConfidence = sourceConfidence
        self.observedSourceRefs = observedSourceRefs
    }

    func catalogIdentityCopy() -> AppleMusicSignalResource {
        AppleMusicSignalResource(
            sourceItemID: "catalog:\(catalogID ?? appleID ?? libraryID ?? sourceItemID)",
            resourceType: resourceType,
            appleID: appleID,
            catalogID: catalogID ?? appleID,
            displayName: displayName,
            artistName: artistName,
            albumTitle: albumTitle,
            playlistName: playlistName,
            curatorName: curatorName,
            genreNames: genreNames,
            releaseDate: releaseDate,
            url: url,
            artworkURL: artworkURL,
            evidenceBasis: .catalogIdentity,
            sourceConfidence: .catalogIdentity,
            observedSourceRefs: [sourceItemID]
        )
    }

    func diagnosticExcludedCopy(sourceID: String) -> AppleMusicSignalResource {
        AppleMusicSignalResource(
            sourceItemID: sourceItemID,
            resourceType: resourceType,
            appleID: appleID,
            catalogID: catalogID,
            libraryID: libraryID,
            persistentID: persistentID,
            displayName: displayName,
            artistName: artistName,
            albumTitle: albumTitle,
            playlistName: playlistName,
            curatorName: curatorName,
            genreNames: genreNames,
            playCount: playCount,
            lastPlayedAt: lastPlayedAt,
            libraryAddedAt: libraryAddedAt,
            releaseDate: releaseDate,
            url: url,
            artworkURL: artworkURL,
            evidenceBasis: .diagnosticExcluded,
            sourceConfidence: .diagnosticExcluded,
            observedSourceRefs: observedSourceRefs.isEmpty ? [sourceID] : observedSourceRefs
        )
    }

    func copyForReplayAggregate(sourceID: String) -> AppleMusicSignalResource {
        let identity = appleID ?? catalogID ?? libraryID ?? sourceItemID
        return AppleMusicSignalResource(
            sourceItemID: "\(sourceID):\(resourceType.rawValue):\(identity)",
            resourceType: resourceType,
            appleID: appleID,
            catalogID: catalogID,
            libraryID: libraryID,
            persistentID: persistentID,
            displayName: displayName,
            artistName: artistName,
            albumTitle: albumTitle,
            playlistName: playlistName,
            curatorName: curatorName,
            genreNames: genreNames,
            playCount: playCount,
            lastPlayedAt: lastPlayedAt,
            libraryAddedAt: libraryAddedAt,
            releaseDate: releaseDate,
            url: url,
            artworkURL: artworkURL,
            evidenceBasis: evidenceBasis,
            sourceConfidence: sourceConfidence,
            observedSourceRefs: observedSourceRefs.isEmpty ? [sourceID] : observedSourceRefs + [sourceID]
        )
    }
}

enum AppleMusicSignalResourceType: String, Codable, Equatable {
    case artist
    case album
    case song
    case playlist
    case station
    case genre
    case unknown
}

enum AppleMusicEvidenceBasis: String, Codable, Equatable {
    case heavyRotation = "heavy_rotation"
    case recentlyPlayed = "recently_played"
    case librarySongPlayCount = "library_song_play_count"
    case librarySongLastPlayed = "library_song_last_played"
    case librarySongLibraryAdded = "library_song_library_added"
    case libraryAlbumLibraryAdded = "library_album_library_added"
    case personalRecommendation = "personal_recommendation"
    case playlistContext = "playlist_context"
    case playlistTrackSample = "playlist_track_sample"
    case replaySummary = "replay_summary"
    case favoriteAnnotation = "favorite_annotation"
    case ratingAnnotation = "rating_annotation"
    case catalogIdentity = "catalog_identity"
    case diagnosticExcluded = "diagnostic_excluded"
}

enum AppleMusicSignalSourceConfidence: String, Codable, Equatable {
    case explicitObserved = "explicit_observed"
    case rankedByApple = "ranked_by_apple"
    case deviceReported = "device_reported"
    case librarySorted = "library_sorted"
    case recommendationContext = "recommendation_context"
    case playlistContext = "playlist_context"
    case userAnnotation = "user_annotation"
    case catalogIdentity = "catalog_identity"
    case diagnosticExcluded = "diagnostic_excluded"
    case unavailable
}

struct AppleMusicSignalProbeError: Codable, Equatable, Identifiable, LocalizedError {
    let id: String
    let source: String
    let code: String
    let message: String

    init(source: String, code: String, message: String) {
        self.id = "\(source):\(code):\(message)"
        self.source = source
        self.code = code
        self.message = message
    }

    enum CodingKeys: String, CodingKey {
        case source
        case code
        case message
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        source = try container.decode(String.self, forKey: .source)
        code = try container.decode(String.self, forKey: .code)
        message = try container.decode(String.self, forKey: .message)
        id = "\(source):\(code):\(message)"
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(source, forKey: .source)
        try container.encode(code, forKey: .code)
        try container.encode(message, forKey: .message)
    }

    var errorDescription: String? {
        "\(source): \(message)"
    }
}

enum JSONValue: Codable, Equatable {
    case object([String: JSONValue])
    case array([JSONValue])
    case string(String)
    case number(Double)
    case bool(Bool)
    case null

    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        if container.decodeNil() {
            self = .null
        } else if let value = try? container.decode(Bool.self) {
            self = .bool(value)
        } else if let value = try? container.decode(Double.self) {
            self = .number(value)
        } else if let value = try? container.decode(String.self) {
            self = .string(value)
        } else if let value = try? container.decode([JSONValue].self) {
            self = .array(value)
        } else {
            self = .object(try container.decode([String: JSONValue].self))
        }
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        switch self {
        case .object(let value):
            try container.encode(value)
        case .array(let value):
            try container.encode(value)
        case .string(let value):
            try container.encode(value)
        case .number(let value):
            try container.encode(value)
        case .bool(let value):
            try container.encode(value)
        case .null:
            try container.encodeNil()
        }
    }

    static func fromJSONObject(_ object: Any) -> JSONValue {
        switch object {
        case let dictionary as [String: Any]:
            return .object(dictionary.mapValues(JSONValue.fromJSONObject))
        case let array as [Any]:
            return .array(array.map(JSONValue.fromJSONObject))
        case let string as String:
            return .string(string)
        case let number as NSNumber:
            if CFGetTypeID(number) == CFBooleanGetTypeID() {
                return .bool(number.boolValue)
            }
            return .number(number.doubleValue)
        case _ as NSNull:
            return .null
        default:
            return .string(String(describing: object))
        }
    }
}
