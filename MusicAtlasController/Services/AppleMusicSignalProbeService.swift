import Combine
import Foundation

#if canImport(MusicKit)
import MusicKit
#endif

struct AppleMusicSignalSavedPayload {
    let directoryURL: URL
    let jsonURL: URL

    var shareURLs: [URL] {
        [jsonURL]
    }
}

struct AppleMusicSignalProbeFileStore {
    private let fileManager: FileManager
    private let baseDirectoryURL: URL?

    init(fileManager: FileManager = .default, baseDirectoryURL: URL? = nil) {
        self.fileManager = fileManager
        self.baseDirectoryURL = baseDirectoryURL
    }

    func save(jsonString: String, filename: String) throws -> AppleMusicSignalSavedPayload {
        let directoryURL = try exportDirectory()
        try fileManager.createDirectory(at: directoryURL, withIntermediateDirectories: true)

        let jsonURL = directoryURL.appendingPathComponent(filename, isDirectory: false)
        guard let data = jsonString.data(using: .utf8) else {
            throw AppleMusicSignalProbeError(source: "file_store", code: "encoding_failed", message: "Could not encode signal payload as UTF-8.")
        }

        try data.write(to: jsonURL, options: .atomic)
        return AppleMusicSignalSavedPayload(directoryURL: directoryURL, jsonURL: jsonURL)
    }

    private func exportDirectory() throws -> URL {
        let rootURL: URL
        if let baseDirectoryURL {
            rootURL = baseDirectoryURL
        } else {
            rootURL = try fileManager.url(
                for: .documentDirectory,
                in: .userDomainMask,
                appropriateFor: nil,
                create: true
            )
            .appendingPathComponent("MusicAtlasControllerExports", isDirectory: true)
        }

        return rootURL.appendingPathComponent("apple_music_signal_probe", isDirectory: true)
    }
}

enum AppleMusicSignalProbeState: Equatable {
    case idle
    case scanning
    case ready
    case failed(String)

    var displayName: String {
        switch self {
        case .idle:
            return "Idle"
        case .scanning:
            return "Scanning"
        case .ready:
            return "Ready"
        case .failed:
            return "Failed"
        }
    }
}

@MainActor
final class AppleMusicSignalProbeStore: ObservableObject {
    @Published private(set) var state: AppleMusicSignalProbeState = .idle
    @Published private(set) var payload: AppleMusicSignalPayload?
    @Published private(set) var jsonString: String?
    @Published private(set) var savedPayload: AppleMusicSignalSavedPayload?
    @Published private(set) var lastMessage: String?

    private let probeService: AppleMusicSignalProbeService
    private let fileStore: AppleMusicSignalProbeFileStore
    private let encoder: JSONEncoder
    private let timestampFormatter: DateFormatter

    init(
        probeService: AppleMusicSignalProbeService = AppleMusicSignalProbeService(),
        fileStore: AppleMusicSignalProbeFileStore = AppleMusicSignalProbeFileStore()
    ) {
        self.probeService = probeService
        self.fileStore = fileStore

        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        self.encoder = encoder

        let formatter = DateFormatter()
        formatter.calendar = Calendar(identifier: .gregorian)
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone(secondsFromGMT: 0)
        formatter.dateFormat = "yyyyMMdd_HHmmss"
        self.timestampFormatter = formatter
    }

    func scan() async {
        state = .scanning
        savedPayload = nil
        lastMessage = "Scanning Apple Music signals..."

        let capturedPayload = await probeService.capture()
        do {
            let data = try encoder.encode(capturedPayload)
            guard let renderedJSON = String(data: data, encoding: .utf8) else {
                throw AppleMusicSignalProbeError(source: "encoder", code: "encoding_failed", message: "Could not render signal payload as UTF-8.")
            }

            payload = capturedPayload
            jsonString = renderedJSON
            state = .ready
            lastMessage = "Signal payload ready. \(capturedPayload.summaryDescription)"
        } catch {
            state = .failed(error.localizedDescription)
            lastMessage = error.localizedDescription
        }
    }

    func savePayload() {
        guard let payload, let jsonString else {
            lastMessage = "Run the signal probe before saving."
            return
        }

        do {
            let timestamp = timestampFormatter.string(from: payload.capturedAt)
            savedPayload = try fileStore.save(
                jsonString: jsonString,
                filename: "apple_music_signal_probe_\(timestamp).json"
            )
            lastMessage = "Saved Apple Music signal payload."
        } catch {
            lastMessage = error.localizedDescription
        }
    }
}

struct AppleMusicSignalProbeService {
    func capture(now: Date = Date()) async -> AppleMusicSignalPayload {
        #if canImport(MusicKit)
        await captureWithMusicKit(now: now)
        #else
        AppleMusicSignalPayload(
            schemaVersion: "apple_music_signal_probe.v0.1",
            capturedAt: now,
            authorization: AppleMusicSignalAuthorization(
                musicAuthorizationStatus: "unavailable",
                canRequestAuthorization: false
            ),
            environment: AppleMusicSignalEnvironment(
                storefront: nil,
                canPlayCatalogContent: nil,
                hasCloudLibraryEnabled: nil,
                deviceContext: DeviceContextProvider.currentContext()
            ),
            rawEndpoints: [],
            libraryArtistsSample: [],
            libraryAlbumsSample: [],
            librarySongsSample: [],
            libraryPlaylistsSample: [],
            personalRecommendations: [],
            errors: [
                AppleMusicSignalProbeError(
                    source: "music_kit",
                    code: "unavailable",
                    message: "MusicKit is not available in the current build environment."
                )
            ],
            notes: Self.payloadNotes
        )
        #endif
    }

    #if canImport(MusicKit)
    private func captureWithMusicKit(now: Date) async -> AppleMusicSignalPayload {
        var errors: [AppleMusicSignalProbeError] = []
        var environment = AppleMusicSignalEnvironment(
            storefront: nil,
            canPlayCatalogContent: nil,
            hasCloudLibraryEnabled: nil,
            deviceContext: DeviceContextProvider.currentContext()
        )

        let authorizationStatus = MusicAuthorization.currentStatus
        let authorization = AppleMusicSignalAuthorization(
            musicAuthorizationStatus: Self.label(for: authorizationStatus),
            canRequestAuthorization: authorizationStatus == .notDetermined
        )

        guard authorizationStatus == .authorized else {
            errors.append(
                AppleMusicSignalProbeError(
                    source: "authorization",
                    code: "not_authorized",
                    message: "Apple Music access must be authorized before account-specific signals can be fetched."
                )
            )

            return AppleMusicSignalPayload(
                schemaVersion: "apple_music_signal_probe.v0.1",
                capturedAt: now,
                authorization: authorization,
                environment: environment,
                rawEndpoints: [],
                libraryArtistsSample: [],
                libraryAlbumsSample: [],
                librarySongsSample: [],
                libraryPlaylistsSample: [],
                personalRecommendations: [],
                errors: errors,
                notes: Self.payloadNotes
            )
        }

        do {
            async let storefront = MusicDataRequest.currentCountryCode
            async let subscription = MusicSubscription.current
            let resolvedStorefront = try await storefront
            let resolvedSubscription = try await subscription
            environment = AppleMusicSignalEnvironment(
                storefront: resolvedStorefront,
                canPlayCatalogContent: resolvedSubscription.canPlayCatalogContent,
                hasCloudLibraryEnabled: resolvedSubscription.hasCloudLibraryEnabled,
                deviceContext: DeviceContextProvider.currentContext()
            )
        } catch {
            errors.append(Self.error(source: "environment", error: error))
        }

        async let rawEndpoints = fetchRawEndpoints()
        async let artists = fetchLibraryArtists()
        async let albums = fetchLibraryAlbums()
        async let songs = fetchLibrarySongs()
        async let playlists = fetchLibraryPlaylists()
        async let recommendations = fetchRecommendations()

        let rawResult = await rawEndpoints
        let artistResult = await artists
        let albumResult = await albums
        let songResult = await songs
        let playlistResult = await playlists
        let recommendationResult = await recommendations

        errors.append(contentsOf: rawResult.errors)
        errors.append(contentsOf: artistResult.errors)
        errors.append(contentsOf: albumResult.errors)
        errors.append(contentsOf: songResult.errors)
        errors.append(contentsOf: playlistResult.errors)
        errors.append(contentsOf: recommendationResult.errors)

        return AppleMusicSignalPayload(
            schemaVersion: "apple_music_signal_probe.v0.1",
            capturedAt: now,
            authorization: authorization,
            environment: environment,
            rawEndpoints: rawResult.items,
            libraryArtistsSample: artistResult.items,
            libraryAlbumsSample: albumResult.items,
            librarySongsSample: songResult.items,
            libraryPlaylistsSample: playlistResult.items,
            personalRecommendations: recommendationResult.items,
            errors: errors,
            notes: Self.payloadNotes
        )
    }

    private func fetchRawEndpoints() async -> ProbeResult<AppleMusicSignalRawEndpoint> {
        let endpoints: [(id: String, label: String, url: URL)] = [
            (
                "recently_played_tracks",
                "Recently played tracks",
                Self.url("https://api.music.apple.com/v1/me/recent/played/tracks?types=songs,library-songs&limit=30")
            ),
            (
                "recently_played_resources",
                "Recently played resources",
                Self.url("https://api.music.apple.com/v1/me/recent/played?types=artists,curators,albums,library-albums,playlists,library-playlists,stations&limit=30")
            ),
            (
                "recently_added_library",
                "Recently added library resources",
                Self.url("https://api.music.apple.com/v1/me/library/recently-added?limit=30")
            ),
            (
                "heavy_rotation",
                "Heavy rotation",
                Self.url("https://api.music.apple.com/v1/me/history/heavy-rotation?limit=30")
            )
        ]

        var items: [AppleMusicSignalRawEndpoint] = []
        var errors: [AppleMusicSignalProbeError] = []

        for endpoint in endpoints {
            do {
                let request = MusicDataRequest(urlRequest: URLRequest(url: endpoint.url))
                let response = try await request.response()
                let object = try JSONSerialization.jsonObject(with: response.data)
                let json = JSONValue.fromJSONObject(object)

                items.append(
                    AppleMusicSignalRawEndpoint(
                        id: endpoint.id,
                        label: endpoint.label,
                        url: endpoint.url,
                        success: true,
                        itemCount: Self.itemCount(from: json),
                        json: json,
                        error: nil
                    )
                )
            } catch {
                let probeError = Self.error(source: endpoint.id, error: error)
                errors.append(probeError)
                items.append(
                    AppleMusicSignalRawEndpoint(
                        id: endpoint.id,
                        label: endpoint.label,
                        url: endpoint.url,
                        success: false,
                        itemCount: nil,
                        json: nil,
                        error: probeError
                    )
                )
            }
        }

        return ProbeResult(items: items, errors: errors)
    }

    private func fetchLibraryArtists() async -> ProbeResult<AppleMusicArtistSignal> {
        do {
            var request = MusicLibraryRequest<Artist>()
            request.limit = 50
            let response = try await request.response()
            return ProbeResult(items: response.items.map(Self.artistSignal), errors: [])
        } catch {
            return ProbeResult(items: [], errors: [Self.error(source: "library_artists", error: error)])
        }
    }

    private func fetchLibraryAlbums() async -> ProbeResult<AppleMusicAlbumSignal> {
        do {
            var request = MusicLibraryRequest<Album>()
            request.limit = 50
            let response = try await request.response()
            return ProbeResult(items: response.items.map(Self.albumSignal), errors: [])
        } catch {
            return ProbeResult(items: [], errors: [Self.error(source: "library_albums", error: error)])
        }
    }

    private func fetchLibrarySongs() async -> ProbeResult<AppleMusicSongSignal> {
        do {
            var request = MusicLibraryRequest<Song>()
            request.limit = 100
            request.sort(by: \.playCount, ascending: false)
            let response = try await request.response()
            return ProbeResult(items: response.items.map(Self.songSignal), errors: [])
        } catch {
            return ProbeResult(items: [], errors: [Self.error(source: "library_songs", error: error)])
        }
    }

    private func fetchLibraryPlaylists() async -> ProbeResult<AppleMusicPlaylistSignal> {
        do {
            var request = MusicLibraryRequest<Playlist>()
            request.limit = 50
            let response = try await request.response()
            return ProbeResult(items: response.items.map(Self.playlistSignal), errors: [])
        } catch {
            return ProbeResult(items: [], errors: [Self.error(source: "library_playlists", error: error)])
        }
    }

    private func fetchRecommendations() async -> ProbeResult<AppleMusicRecommendationSignal> {
        do {
            var request = MusicPersonalRecommendationsRequest()
            request.limit = 10
            let response = try await request.response()
            return ProbeResult(items: response.recommendations.map(Self.recommendationSignal), errors: [])
        } catch {
            return ProbeResult(items: [], errors: [Self.error(source: "personal_recommendations", error: error)])
        }
    }

    private static func artistSignal(_ artist: Artist) -> AppleMusicArtistSignal {
        AppleMusicArtistSignal(
            id: artist.id.rawValue,
            name: artist.name,
            genreNames: artist.genreNames,
            libraryAddedDate: artist.libraryAddedDate,
            url: artist.url,
            artworkURL: artist.artwork?.url(width: 300, height: 300)
        )
    }

    private static func albumSignal(_ album: Album) -> AppleMusicAlbumSignal {
        AppleMusicAlbumSignal(
            id: album.id.rawValue,
            title: album.title,
            artistName: album.artistName,
            genreNames: album.genreNames,
            trackCount: album.trackCount,
            releaseDate: album.releaseDate,
            lastPlayedDate: album.lastPlayedDate,
            libraryAddedDate: album.libraryAddedDate,
            url: album.url,
            artworkURL: album.artwork?.url(width: 300, height: 300)
        )
    }

    private static func songSignal(_ song: Song) -> AppleMusicSongSignal {
        AppleMusicSongSignal(
            id: song.id.rawValue,
            title: song.title,
            artistName: song.artistName,
            albumTitle: song.albumTitle,
            genreNames: song.genreNames,
            durationSeconds: song.duration,
            playCount: song.playCount,
            lastPlayedDate: song.lastPlayedDate,
            libraryAddedDate: song.libraryAddedDate,
            url: song.url,
            artworkURL: song.artwork?.url(width: 300, height: 300)
        )
    }

    private static func playlistSignal(_ playlist: Playlist) -> AppleMusicPlaylistSignal {
        AppleMusicPlaylistSignal(
            id: playlist.id.rawValue,
            name: playlist.name,
            curatorName: playlist.curatorName,
            lastPlayedDate: playlist.lastPlayedDate,
            libraryAddedDate: playlist.libraryAddedDate,
            url: playlist.url,
            artworkURL: playlist.artwork?.url(width: 300, height: 300)
        )
    }

    private static func recommendationSignal(_ recommendation: MusicPersonalRecommendation) -> AppleMusicRecommendationSignal {
        AppleMusicRecommendationSignal(
            id: recommendation.id.rawValue,
            title: recommendation.title,
            reason: recommendation.reason,
            albumCount: recommendation.albums.count,
            playlistCount: recommendation.playlists.count,
            stationCount: recommendation.stations.count,
            albums: recommendation.albums.prefix(6).map(albumSignal),
            playlists: recommendation.playlists.prefix(6).map(playlistSignal)
        )
    }

    private static func label(for status: MusicAuthorization.Status) -> String {
        switch status {
        case .notDetermined:
            return "notDetermined"
        case .denied:
            return "denied"
        case .restricted:
            return "restricted"
        case .authorized:
            return "authorized"
        @unknown default:
            return "unknown"
        }
    }
    #endif

    private static var payloadNotes: [String] {
        [
            "This payload is read-only Apple Music signal evidence for product analysis.",
            "It is not used to generate Survey grids yet.",
            "Recently played Apple Music API responses are limited snapshots, not full lifetime listening history.",
            "Library samples are capped locally to keep the payload inspectable."
        ]
    }

    private static func url(_ string: String) -> URL {
        guard let url = URL(string: string) else {
            preconditionFailure("Invalid static Apple Music API URL: \(string)")
        }
        return url
    }

    private static func itemCount(from json: JSONValue) -> Int? {
        guard case .object(let object) = json,
              case .array(let data)? = object["data"] else {
            return nil
        }

        return data.count
    }

    private static func error(source: String, error: Error) -> AppleMusicSignalProbeError {
        AppleMusicSignalProbeError(
            source: source,
            code: String(describing: type(of: error)),
            message: error.musicAtlasDiagnosticDescription
        )
    }
}

private struct ProbeResult<Item> {
    let items: [Item]
    let errors: [AppleMusicSignalProbeError]
}

private extension AppleMusicSignalPayload {
    var summaryDescription: String {
        [
            "\(rawEndpoints.filter(\.success).count)/\(rawEndpoints.count) raw endpoints",
            "\(libraryArtistsSample.count) artists",
            "\(libraryAlbumsSample.count) albums",
            "\(librarySongsSample.count) songs",
            "\(libraryPlaylistsSample.count) playlists",
            "\(personalRecommendations.count) recommendations",
            "\(errors.count) errors"
        ].joined(separator: ", ")
    }
}
