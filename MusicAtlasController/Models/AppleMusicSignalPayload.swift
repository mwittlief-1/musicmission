import Foundation

struct AppleMusicSignalPayload: Codable {
    let schemaVersion: String
    let capturedAt: Date
    let authorization: AppleMusicSignalAuthorization
    let environment: AppleMusicSignalEnvironment
    let rawEndpoints: [AppleMusicSignalRawEndpoint]
    let libraryArtistsSample: [AppleMusicArtistSignal]
    let libraryAlbumsSample: [AppleMusicAlbumSignal]
    let librarySongsSample: [AppleMusicSongSignal]
    let libraryPlaylistsSample: [AppleMusicPlaylistSignal]
    let personalRecommendations: [AppleMusicRecommendationSignal]
    let errors: [AppleMusicSignalProbeError]
    let notes: [String]

    enum CodingKeys: String, CodingKey {
        case schemaVersion = "schema_version"
        case capturedAt = "captured_at"
        case authorization
        case environment
        case rawEndpoints = "raw_endpoints"
        case libraryArtistsSample = "library_artists_sample"
        case libraryAlbumsSample = "library_albums_sample"
        case librarySongsSample = "library_songs_sample"
        case libraryPlaylistsSample = "library_playlists_sample"
        case personalRecommendations = "personal_recommendations"
        case errors
        case notes
    }
}

struct AppleMusicSignalAuthorization: Codable, Equatable {
    let musicAuthorizationStatus: String
    let canRequestAuthorization: Bool

    enum CodingKeys: String, CodingKey {
        case musicAuthorizationStatus = "music_authorization_status"
        case canRequestAuthorization = "can_request_authorization"
    }
}

struct AppleMusicSignalEnvironment: Codable {
    let storefront: String?
    let canPlayCatalogContent: Bool?
    let hasCloudLibraryEnabled: Bool?
    let deviceContext: DeviceContext

    enum CodingKeys: String, CodingKey {
        case storefront
        case canPlayCatalogContent = "can_play_catalog_content"
        case hasCloudLibraryEnabled = "has_cloud_library_enabled"
        case deviceContext = "device_context"
    }
}

struct AppleMusicSignalRawEndpoint: Codable, Equatable, Identifiable {
    let id: String
    let label: String
    let url: URL
    let success: Bool
    let itemCount: Int?
    let json: JSONValue?
    let error: AppleMusicSignalProbeError?

    enum CodingKeys: String, CodingKey {
        case id
        case label
        case url
        case success
        case itemCount = "item_count"
        case json
        case error
    }
}

struct AppleMusicArtistSignal: Codable, Equatable, Identifiable {
    let id: String
    let name: String
    let genreNames: [String]?
    let libraryAddedDate: Date?
    let url: URL?
    let artworkURL: URL?

    enum CodingKeys: String, CodingKey {
        case id
        case name
        case genreNames = "genre_names"
        case libraryAddedDate = "library_added_date"
        case url
        case artworkURL = "artwork_url"
    }
}

struct AppleMusicAlbumSignal: Codable, Equatable, Identifiable {
    let id: String
    let title: String
    let artistName: String
    let genreNames: [String]
    let trackCount: Int?
    let releaseDate: Date?
    let lastPlayedDate: Date?
    let libraryAddedDate: Date?
    let url: URL?
    let artworkURL: URL?

    enum CodingKeys: String, CodingKey {
        case id
        case title
        case artistName = "artist_name"
        case genreNames = "genre_names"
        case trackCount = "track_count"
        case releaseDate = "release_date"
        case lastPlayedDate = "last_played_date"
        case libraryAddedDate = "library_added_date"
        case url
        case artworkURL = "artwork_url"
    }
}

struct AppleMusicSongSignal: Codable, Equatable, Identifiable {
    let id: String
    let title: String
    let artistName: String
    let albumTitle: String?
    let genreNames: [String]
    let durationSeconds: TimeInterval?
    let playCount: Int?
    let lastPlayedDate: Date?
    let libraryAddedDate: Date?
    let url: URL?
    let artworkURL: URL?

    enum CodingKeys: String, CodingKey {
        case id
        case title
        case artistName = "artist_name"
        case albumTitle = "album_title"
        case genreNames = "genre_names"
        case durationSeconds = "duration_seconds"
        case playCount = "play_count"
        case lastPlayedDate = "last_played_date"
        case libraryAddedDate = "library_added_date"
        case url
        case artworkURL = "artwork_url"
    }
}

struct AppleMusicPlaylistSignal: Codable, Equatable, Identifiable {
    let id: String
    let name: String
    let curatorName: String?
    let lastPlayedDate: Date?
    let libraryAddedDate: Date?
    let url: URL?
    let artworkURL: URL?

    enum CodingKeys: String, CodingKey {
        case id
        case name
        case curatorName = "curator_name"
        case lastPlayedDate = "last_played_date"
        case libraryAddedDate = "library_added_date"
        case url
        case artworkURL = "artwork_url"
    }
}

struct AppleMusicRecommendationSignal: Codable, Equatable, Identifiable {
    let id: String
    let title: String?
    let reason: String?
    let albumCount: Int
    let playlistCount: Int
    let stationCount: Int
    let albums: [AppleMusicAlbumSignal]
    let playlists: [AppleMusicPlaylistSignal]

    enum CodingKeys: String, CodingKey {
        case id
        case title
        case reason
        case albumCount = "album_count"
        case playlistCount = "playlist_count"
        case stationCount = "station_count"
        case albums
        case playlists
    }
}

struct AppleMusicSignalProbeError: Codable, Equatable, Identifiable, LocalizedError {
    let id: String
    let source: String
    let code: String
    let message: String

    init(source: String, code: String, message: String) {
        self.id = "\(source)_\(code)_\(UUID().uuidString)"
        self.source = source
        self.code = code
        self.message = message
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
