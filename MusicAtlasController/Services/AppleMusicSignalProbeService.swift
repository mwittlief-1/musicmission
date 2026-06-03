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

private extension String {
    var nilIfBlank: String? {
        let trimmed = trimmingCharacters(in: .whitespacesAndNewlines)
        return trimmed.isEmpty ? nil : trimmed
    }
}

private extension Optional where Wrapped == String {
    var nilIfBlank: String? {
        self?.nilIfBlank
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
                filename: "apple_music_signal_probe_v0_4_\(timestamp).json"
            )
            lastMessage = "Saved Apple Music signal payload."
        } catch {
            lastMessage = error.localizedDescription
        }
    }
}

struct AppleMusicSignalProbeService {
    private static let recentlyPlayedTracksCap = 500
    private static let recentlyPlayedTracksPageLimit = 30
    private static let replayTopArtistsCap = 50
    private static let replayTopAlbumsCap = 50
    private static let replayTopSongsCap = 200
    private static let replaySummaryAggregateCap = 1 + replayTopArtistsCap + replayTopSongsCap + replayTopAlbumsCap

    func capture(now: Date = Date()) async -> AppleMusicSignalPayload {
        #if canImport(MusicKit)
        await captureWithMusicKit(now: now)
        #else
        let error = AppleMusicSignalProbeError(
            source: "music_kit",
            code: "unavailable",
            message: "MusicKit is not available in the current build environment."
        )
        return AppleMusicSignalPayload.unavailable(
            capturedAt: now,
            authorizationStatus: "unavailable",
            canRequestAuthorization: false,
            storefront: nil,
            error: error
        )
        #endif
    }

    #if canImport(MusicKit)
    private func captureWithMusicKit(now: Date) async -> AppleMusicSignalPayload {
        let authorizationStatus = MusicAuthorization.currentStatus
        guard authorizationStatus == .authorized else {
            let error = AppleMusicSignalProbeError(
                source: "authorization",
                code: "not_authorized",
                message: "Apple Music access must be authorized before account-specific signals can be fetched."
            )
            return AppleMusicSignalPayload.unavailable(
                capturedAt: now,
                authorizationStatus: Self.label(for: authorizationStatus),
                canRequestAuthorization: authorizationStatus == .notDetermined,
                storefront: nil,
                error: error
            )
        }

        var storefront: String?
        var authorizationErrors: [AppleMusicSignalProbeError] = []
        var subscriptionStatus = "unknown"
        var tokenStatus = "automatic_music_data_request_attempted"

        do {
            async let currentStorefront = MusicDataRequest.currentCountryCode
            async let subscription = MusicSubscription.current
            storefront = try await currentStorefront
            let resolvedSubscription = try await subscription
            subscriptionStatus = Self.subscriptionStatus(for: resolvedSubscription)
            tokenStatus = "automatic_music_data_request"
        } catch {
            authorizationErrors.append(Self.error(source: "authorization", error: error))
            tokenStatus = "music_user_token_unverified"
        }

        async let heavyRotation = fetchRawAppleMusicAPISection(
            sourceID: "heavy_rotation",
            path: "/v1/me/history/heavy-rotation",
            queryItems: [URLQueryItem(name: "limit", value: "10")],
            cap: 10,
            capturedAt: now,
            evidenceBasis: .heavyRotation,
            sourceConfidence: .rankedByApple
        )
        async let recentlyPlayed = fetchPaginatedRawAppleMusicAPISection(
            sourceID: "recently_played_tracks",
            path: "/v1/me/recent/played/tracks",
            queryItems: [
                URLQueryItem(name: "types", value: "songs,library-songs")
            ],
            pageLimit: Self.recentlyPlayedTracksPageLimit,
            cap: Self.recentlyPlayedTracksCap,
            capturedAt: now,
            evidenceBasis: .recentlyPlayed,
            sourceConfidence: .explicitObserved
        )
        async let playCount = fetchLibrarySongs(
            sourceID: "library_song_play_count",
            cap: 200,
            capturedAt: now,
            evidenceBasis: .librarySongPlayCount,
            sourceConfidence: .librarySorted,
            sort: .playCount
        )
        async let lastPlayed = fetchLibrarySongs(
            sourceID: "library_song_last_played",
            cap: 100,
            capturedAt: now,
            evidenceBasis: .librarySongLastPlayed,
            sourceConfidence: .librarySorted,
            sort: .lastPlayed
        )
        async let libraryAddedSongs = fetchLibrarySongs(
            sourceID: "library_song_library_added",
            cap: 100,
            capturedAt: now,
            evidenceBasis: .librarySongLibraryAdded,
            sourceConfidence: .librarySorted,
            sort: .libraryAdded
        )
        let replayStorefront = storefront
        async let libraryAddedAlbums = fetchLibraryAlbumsSortedByLibraryAdded(capturedAt: now)
        async let recommendations = fetchPersonalRecommendations(capturedAt: now)
        async let playlistContexts = fetchPlaylistContexts(capturedAt: now)
        async let replaySummary = fetchReplaySummary(capturedAt: now, storefront: replayStorefront)

        let primary = await AppleMusicPrimarySignalSources(
            heavyRotation: heavyRotation,
            recentlyPlayedTracks: recentlyPlayed,
            librarySongPlayCount: playCount,
            librarySongLastPlayed: lastPlayed,
            librarySongLibraryAdded: libraryAddedSongs,
            libraryAlbumLibraryAdded: libraryAddedAlbums,
            personalRecommendations: recommendations
        )

        let replay = await replaySummary
        let context = await AppleMusicContextSignalSources(
            playlistContexts: playlistContexts,
            playlistTrackSamples: .unavailable(
                sourceID: "playlist_track_samples",
                cap: 250,
                capturedAt: now,
                error: AppleMusicSignalProbeError(
                    source: "playlist_track_samples",
                    code: "not_implemented_in_v0_4_probe",
                    message: "Playlist track sampling requires a qualifying-playlist loader and is emitted as unavailable for this Alpha build."
                )
            ),
            replaySummary: replay.aggregate,
            replayTopArtists: replay.topArtists,
            replayTopAlbums: replay.topAlbums,
            replayTopSongs: replay.topSongs
        )

        return AppleMusicSignalPayload.make(
            capturedAt: now,
            storefront: storefront,
            authorization: AppleMusicSignalAuthorization(
                musicAuthorizationStatus: Self.label(for: authorizationStatus),
                canRequestAuthorization: authorizationStatus == .notDetermined,
                subscriptionStatus: subscriptionStatus,
                tokenStatus: tokenStatus,
                errors: authorizationErrors
            ),
            primarySignalSources: primary,
            contextSources: context,
            observedResourceAnnotations: .empty(capturedAt: now),
            excludedOrDiagnosticSources: Self.diagnosticExcludedSources(capturedAt: now)
        )
    }

    private enum SongSort {
        case playCount
        case lastPlayed
        case libraryAdded
    }

    private struct ReplaySignalSections {
        let aggregate: AppleMusicSignalSourceSection
        let topArtists: AppleMusicSignalSourceSection
        let topAlbums: AppleMusicSignalSourceSection
        let topSongs: AppleMusicSignalSourceSection
    }

    private struct ReplayRef {
        let type: AppleMusicSignalResourceType
        let appleID: String
    }

    private func fetchRawAppleMusicAPISection(
        sourceID: String,
        path: String,
        queryItems: [URLQueryItem],
        cap: Int,
        capturedAt: Date,
        evidenceBasis: AppleMusicEvidenceBasis,
        sourceConfidence: AppleMusicSignalSourceConfidence
    ) async -> AppleMusicSignalSourceSection {
        do {
            var components = URLComponents()
            components.scheme = "https"
            components.host = "api.music.apple.com"
            components.path = path
            components.queryItems = queryItems

            guard let url = components.url else {
                throw AppleMusicSignalProbeError(
                    source: sourceID,
                    code: "invalid_apple_music_api_url",
                    message: "Could not build Apple Music API URL for \(path)."
                )
            }

            var urlRequest = URLRequest(url: url)
            urlRequest.httpMethod = "GET"
            let response = try await MusicDataRequest(urlRequest: urlRequest).response()
            let json = try JSONDecoder().decode(JSONValue.self, from: response.data)
            return .captured(
                sourceID: sourceID,
                cap: cap,
                capturedAt: capturedAt,
                items: Self.resources(
                    from: json,
                    sourceID: sourceID,
                    cap: cap,
                    evidenceBasis: evidenceBasis,
                    sourceConfidence: sourceConfidence
                )
            )
        } catch {
            return .unavailable(
                sourceID: sourceID,
                cap: cap,
                capturedAt: capturedAt,
                error: Self.error(source: sourceID, error: error)
            )
        }
    }

    private func fetchReplaySummary(capturedAt: Date, storefront: String?) async -> ReplaySignalSections {
        do {
            let root = try await fetchRawAppleMusicAPIJSON(
                path: "/v1/me/music-summaries",
                queryItems: [
                    URLQueryItem(name: "filter[year]", value: "latest"),
                    URLQueryItem(name: "views", value: "top-artists,top-albums,top-songs")
                ],
                sourceID: "replay_summary"
            )

            async let topArtists = fetchReplayViewSection(
                rootJSON: root,
                viewID: "top-artists",
                sourceID: "replay_top_artists",
                cap: Self.replayTopArtistsCap,
                capturedAt: capturedAt
            )
            async let topAlbums = fetchReplayViewSection(
                rootJSON: root,
                viewID: "top-albums",
                sourceID: "replay_top_albums",
                cap: Self.replayTopAlbumsCap,
                capturedAt: capturedAt
            )
            async let topSongs = fetchReplayViewSection(
                rootJSON: root,
                viewID: "top-songs",
                sourceID: "replay_top_songs",
                cap: Self.replayTopSongsCap,
                capturedAt: capturedAt
            )

            let periodItems = Self.rootDataResources(
                from: root,
                sourceID: "replay_summary",
                cap: 1,
                evidenceBasis: .replaySummary,
                sourceConfidence: .rankedByApple
            )
            let rawTopArtists = await topArtists
            let rawTopAlbums = await topAlbums
            let rawTopSongs = await topSongs

            async let hydratedTopArtists = hydrateReplayViewSection(
                rawTopArtists,
                replayType: .artist,
                storefront: storefront,
                capturedAt: capturedAt
            )
            async let hydratedTopAlbums = hydrateReplayViewSection(
                rawTopAlbums,
                replayType: .album,
                storefront: storefront,
                capturedAt: capturedAt
            )
            async let hydratedTopSongs = hydrateReplayViewSection(
                rawTopSongs,
                replayType: .song,
                storefront: storefront,
                capturedAt: capturedAt
            )

            let resolvedTopArtists = await hydratedTopArtists
            let resolvedTopAlbums = await hydratedTopAlbums
            let resolvedTopSongs = await hydratedTopSongs
            let aggregateItems = periodItems +
                resolvedTopArtists.items.map { $0.copyForReplayAggregate(sourceID: "replay_summary") } +
                resolvedTopSongs.items.map { $0.copyForReplayAggregate(sourceID: "replay_summary") } +
                resolvedTopAlbums.items.map { $0.copyForReplayAggregate(sourceID: "replay_summary") }
            let aggregateErrors = resolvedTopArtists.errors + resolvedTopAlbums.errors + resolvedTopSongs.errors

            return ReplaySignalSections(
                aggregate: .captured(
                    sourceID: "replay_summary",
                    cap: Self.replaySummaryAggregateCap,
                    capturedAt: capturedAt,
                    items: aggregateItems,
                    errors: aggregateErrors
                ),
                topArtists: resolvedTopArtists,
                topAlbums: resolvedTopAlbums,
                topSongs: resolvedTopSongs
            )
        } catch {
            let probeError = Self.error(source: "replay_summary", error: error)
            return ReplaySignalSections(
                aggregate: .unavailable(sourceID: "replay_summary", cap: Self.replaySummaryAggregateCap, capturedAt: capturedAt, error: probeError),
                topArtists: .unavailable(sourceID: "replay_top_artists", cap: Self.replayTopArtistsCap, capturedAt: capturedAt, error: probeError),
                topAlbums: .unavailable(sourceID: "replay_top_albums", cap: Self.replayTopAlbumsCap, capturedAt: capturedAt, error: probeError),
                topSongs: .unavailable(sourceID: "replay_top_songs", cap: Self.replayTopSongsCap, capturedAt: capturedAt, error: probeError)
            )
        }
    }

    private func hydrateReplayViewSection(
        _ section: AppleMusicSignalSourceSection,
        replayType: AppleMusicSignalResourceType,
        storefront: String?,
        capturedAt: Date
    ) async -> AppleMusicSignalSourceSection {
        let replayRefs = section.items.compactMap { item -> (AppleMusicSignalResource, ReplayRef)? in
            guard let ref = Self.replayRef(
                from: item.catalogID ?? item.appleID,
                expectedType: replayType
            ) else {
                return nil
            }
            return (item, ref)
        }
        guard !replayRefs.isEmpty else {
            return section
        }

        var errors = section.errors
        let hydratedByID: [String: AppleMusicSignalResource]
        if let storefront = storefront?.nilIfBlank {
            let ids = replayRefs.map(\.1.appleID)
            let chunks = stride(from: 0, to: ids.count, by: 100).map {
                Array(ids[$0..<min($0 + 100, ids.count)])
            }
            var hydrated = [String: AppleMusicSignalResource]()
            for chunk in chunks {
                do {
                    let json = try await fetchRawAppleMusicAPIJSON(
                        path: "/v1/catalog/\(storefront)/\(Self.catalogPath(for: replayType))",
                        queryItems: [URLQueryItem(name: "ids", value: chunk.joined(separator: ","))],
                        sourceID: section.sourceID
                    )
                    for resource in Self.resources(
                        from: json,
                        sourceID: section.sourceID,
                        cap: chunk.count,
                        evidenceBasis: .replaySummary,
                        sourceConfidence: .rankedByApple
                    ) {
                        if let catalogID = resource.catalogID ?? resource.appleID {
                            hydrated[catalogID] = resource
                        }
                    }
                } catch {
                    errors.append(Self.error(source: section.sourceID, error: error))
                }
            }
            hydratedByID = hydrated
        } else {
            hydratedByID = [:]
        }

        let items = replayRefs.map { original, ref in
            hydratedByID[ref.appleID] ?? Self.normalizedReplayResource(
                from: original,
                replayType: replayType,
                appleID: ref.appleID
            )
        }

        return .captured(
            sourceID: section.sourceID,
            cap: section.cap,
            capturedAt: capturedAt,
            items: items,
            errors: errors
        )
    }

    private static func replayRef(
        from rawValue: String?,
        expectedType: AppleMusicSignalResourceType
    ) -> ReplayRef? {
        guard let rawValue = rawValue?.nilIfBlank else {
            return nil
        }
        if let decoded = decodedReplayValue(rawValue) {
            let parts = decoded.split(separator: "-", omittingEmptySubsequences: false)
            guard parts.count == 4,
                  parts[0] == "year",
                  let type = replayType(from: String(parts[2])),
                  type == expectedType else {
                return nil
            }
            return ReplayRef(type: type, appleID: String(parts[3]))
        }
        if rawValue.allSatisfy(\.isNumber) {
            return ReplayRef(type: expectedType, appleID: rawValue)
        }
        return nil
    }

    private static func decodedReplayValue(_ rawValue: String) -> String? {
        if rawValue.hasPrefix("year-") {
            return rawValue
        }
        var base64 = rawValue
            .replacingOccurrences(of: "-", with: "+")
            .replacingOccurrences(of: "_", with: "/")
        let padding = base64.count % 4
        if padding > 0 {
            base64 += String(repeating: "=", count: 4 - padding)
        }
        guard let data = Data(base64Encoded: base64) else {
            return nil
        }
        return String(data: data, encoding: .utf8)
    }

    private static func replayType(from rawType: String) -> AppleMusicSignalResourceType? {
        switch rawType {
        case "artist":
            return .artist
        case "album":
            return .album
        case "song":
            return .song
        default:
            return nil
        }
    }

    private static func catalogPath(for replayType: AppleMusicSignalResourceType) -> String {
        switch replayType {
        case .artist:
            return "artists"
        case .album:
            return "albums"
        case .song:
            return "songs"
        case .playlist, .station, .genre, .unknown:
            return "songs"
        }
    }

    private static func normalizedReplayResource(
        from resource: AppleMusicSignalResource,
        replayType: AppleMusicSignalResourceType,
        appleID: String
    ) -> AppleMusicSignalResource {
        AppleMusicSignalResource(
            sourceItemID: resource.sourceItemID,
            resourceType: replayType,
            appleID: appleID,
            catalogID: appleID,
            libraryID: resource.libraryID,
            persistentID: resource.persistentID,
            displayName: resource.displayName,
            artistName: resource.artistName,
            albumTitle: resource.albumTitle,
            playlistName: resource.playlistName,
            curatorName: resource.curatorName,
            genreNames: resource.genreNames,
            playCount: resource.playCount,
            lastPlayedAt: resource.lastPlayedAt,
            libraryAddedAt: resource.libraryAddedAt,
            releaseDate: resource.releaseDate,
            url: resource.url,
            artworkURL: resource.artworkURL,
            evidenceBasis: resource.evidenceBasis,
            sourceConfidence: resource.sourceConfidence,
            observedSourceRefs: resource.observedSourceRefs
        )
    }

    private func fetchReplayViewSection(
        rootJSON: JSONValue,
        viewID: String,
        sourceID: String,
        cap: Int,
        capturedAt: Date
    ) async -> AppleMusicSignalSourceSection {
        var items = [AppleMusicSignalResource]()
        var errors = [AppleMusicSignalProbeError]()
        var seen = Set<String>()

        func appendUnique(_ pageItems: [AppleMusicSignalResource]) {
            for item in pageItems {
                let identity = item.catalogID ?? item.appleID ?? item.libraryID ?? item.sourceItemID
                guard seen.insert("\(item.resourceType.rawValue):\(identity)").inserted else {
                    continue
                }
                items.append(item)
                if items.count >= cap {
                    break
                }
            }
        }

        if let viewObject = Self.replayViewObject(from: rootJSON, viewID: viewID) {
            appendUnique(
                Self.resourcesFromData(
                    Self.dataValue(from: viewObject),
                    sourceID: sourceID,
                    cap: cap,
                    evidenceBasis: .replaySummary,
                    sourceConfidence: .rankedByApple
                )
            )

            var nextURL = Self.nextURL(from: viewObject)
            while items.count < cap, let pageURL = nextURL {
                do {
                    let pageJSON = try await fetchRawAppleMusicAPIJSON(
                        url: pageURL,
                        sourceID: sourceID
                    )
                    appendUnique(
                        Self.resources(
                            from: pageJSON,
                            sourceID: sourceID,
                            cap: cap - items.count,
                            evidenceBasis: .replaySummary,
                            sourceConfidence: .rankedByApple
                        )
                    )
                    nextURL = Self.nextURL(from: pageJSON)
                } catch {
                    errors.append(Self.error(source: sourceID, error: error))
                    break
                }
            }
        }

        return .captured(sourceID: sourceID, cap: cap, capturedAt: capturedAt, items: items, errors: errors)
    }

    private func fetchPaginatedRawAppleMusicAPISection(
        sourceID: String,
        path: String,
        queryItems: [URLQueryItem],
        pageLimit: Int,
        cap: Int,
        capturedAt: Date,
        evidenceBasis: AppleMusicEvidenceBasis,
        sourceConfidence: AppleMusicSignalSourceConfidence
    ) async -> AppleMusicSignalSourceSection {
        var items: [AppleMusicSignalResource] = []
        var errors: [AppleMusicSignalProbeError] = []
        var seen = Set<String>()
        var offset = 0

        while items.count < cap {
            do {
                var pageQueryItems = queryItems
                pageQueryItems.append(URLQueryItem(name: "limit", value: "\(min(pageLimit, cap - items.count))"))
                if offset > 0 {
                    pageQueryItems.append(URLQueryItem(name: "offset", value: "\(offset)"))
                }

                let json = try await fetchRawAppleMusicAPIJSON(path: path, queryItems: pageQueryItems, sourceID: sourceID)
                let pageItems = Self.resources(
                    from: json,
                    sourceID: sourceID,
                    cap: pageLimit,
                    evidenceBasis: evidenceBasis,
                    sourceConfidence: sourceConfidence
                )
                for item in pageItems {
                    let identity = item.catalogID ?? item.appleID ?? item.libraryID ?? item.sourceItemID
                    guard seen.insert("\(item.resourceType.rawValue):\(identity)").inserted else {
                        continue
                    }
                    items.append(item)
                    if items.count >= cap {
                        break
                    }
                }

                guard Self.hasNextPage(json), !pageItems.isEmpty else {
                    break
                }
                offset += pageLimit
            } catch {
                errors.append(Self.error(source: sourceID, error: error))
                break
            }
        }

        if items.isEmpty, let error = errors.first {
            return .unavailable(sourceID: sourceID, cap: cap, capturedAt: capturedAt, error: error)
        }

        return .captured(sourceID: sourceID, cap: cap, capturedAt: capturedAt, items: items, errors: errors)
    }

    private func fetchRawAppleMusicAPIJSON(
        path: String,
        queryItems: [URLQueryItem],
        sourceID: String
    ) async throws -> JSONValue {
        var components = URLComponents()
        components.scheme = "https"
        components.host = "api.music.apple.com"
        components.path = path
        components.queryItems = queryItems

        guard let url = components.url else {
            throw AppleMusicSignalProbeError(
                source: sourceID,
                code: "invalid_apple_music_api_url",
                message: "Could not build Apple Music API URL for \(path)."
            )
        }

        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "GET"
        let response = try await MusicDataRequest(urlRequest: urlRequest).response()
        return try JSONDecoder().decode(JSONValue.self, from: response.data)
    }

    private func fetchRawAppleMusicAPIJSON(
        url: URL,
        sourceID: String
    ) async throws -> JSONValue {
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "GET"
        let response = try await MusicDataRequest(urlRequest: urlRequest).response()
        return try JSONDecoder().decode(JSONValue.self, from: response.data)
    }

    private func fetchLibrarySongs(
        sourceID: String,
        cap: Int,
        capturedAt: Date,
        evidenceBasis: AppleMusicEvidenceBasis,
        sourceConfidence: AppleMusicSignalSourceConfidence,
        sort: SongSort
    ) async -> AppleMusicSignalSourceSection {
        do {
            var request = MusicLibraryRequest<Song>()
            request.limit = cap
            switch sort {
            case .playCount:
                request.sort(by: \.playCount, ascending: false)
            case .lastPlayed:
                request.sort(by: \.lastPlayedDate, ascending: false)
            case .libraryAdded:
                request.sort(by: \.libraryAddedDate, ascending: false)
            }
            let response = try await request.response()
            return .captured(
                sourceID: sourceID,
                cap: cap,
                capturedAt: capturedAt,
                items: response.items.map { Self.songResource($0, sourceID: sourceID, evidenceBasis: evidenceBasis, sourceConfidence: sourceConfidence) }
            )
        } catch {
            return .captured(sourceID: sourceID, cap: cap, capturedAt: capturedAt, items: [], errors: [Self.error(source: sourceID, error: error)])
        }
    }

    private func fetchLibraryAlbumsSortedByLibraryAdded(capturedAt: Date) async -> AppleMusicSignalSourceSection {
        do {
            var request = MusicLibraryRequest<Album>()
            request.limit = 100
            request.sort(by: \.libraryAddedDate, ascending: false)
            let response = try await request.response()
            return .captured(
                sourceID: "library_album_library_added",
                cap: 100,
                capturedAt: capturedAt,
                items: response.items.map {
                    Self.albumResource($0, sourceID: "library_album_library_added", evidenceBasis: .libraryAlbumLibraryAdded, sourceConfidence: .librarySorted)
                }
            )
        } catch {
            return .captured(sourceID: "library_album_library_added", cap: 100, capturedAt: capturedAt, items: [], errors: [Self.error(source: "library_album_library_added", error: error)])
        }
    }

    private func fetchPersonalRecommendations(capturedAt: Date) async -> AppleMusicSignalSourceSection {
        do {
            var request = MusicPersonalRecommendationsRequest()
            request.limit = 10
            let response = try await request.response()
            return .captured(
                sourceID: "personal_recommendations",
                cap: 50,
                capturedAt: capturedAt,
                items: Array(response.recommendations.flatMap(Self.recommendationResources).prefix(50))
            )
        } catch {
            return .captured(sourceID: "personal_recommendations", cap: 50, capturedAt: capturedAt, items: [], errors: [Self.error(source: "personal_recommendations", error: error)])
        }
    }

    private func fetchPlaylistContexts(capturedAt: Date) async -> AppleMusicSignalSourceSection {
        do {
            var request = MusicLibraryRequest<Playlist>()
            request.limit = 50
            let response = try await request.response()
            return .captured(sourceID: "playlist_contexts", cap: 50, capturedAt: capturedAt, items: response.items.map(Self.playlistResource))
        } catch {
            return .captured(sourceID: "playlist_contexts", cap: 50, capturedAt: capturedAt, items: [], errors: [Self.error(source: "playlist_contexts", error: error)])
        }
    }

    private static func songResource(_ song: Song, sourceID: String, evidenceBasis: AppleMusicEvidenceBasis, sourceConfidence: AppleMusicSignalSourceConfidence) -> AppleMusicSignalResource {
        AppleMusicSignalResource(
            sourceItemID: "\(sourceID):\(song.id.rawValue)",
            resourceType: .song,
            appleID: song.id.rawValue,
            catalogID: song.id.rawValue,
            displayName: song.title,
            artistName: song.artistName,
            albumTitle: song.albumTitle,
            genreNames: song.genreNames,
            playCount: song.playCount,
            lastPlayedAt: song.lastPlayedDate,
            libraryAddedAt: song.libraryAddedDate,
            releaseDate: song.releaseDate.map(Self.yearMonthDayString),
            url: song.url?.absoluteString,
            artworkURL: song.artwork?.url(width: 300, height: 300)?.absoluteString,
            evidenceBasis: evidenceBasis,
            sourceConfidence: sourceConfidence,
            observedSourceRefs: [sourceID]
        )
    }

    private static func albumResource(_ album: Album, sourceID: String, evidenceBasis: AppleMusicEvidenceBasis, sourceConfidence: AppleMusicSignalSourceConfidence) -> AppleMusicSignalResource {
        AppleMusicSignalResource(
            sourceItemID: "\(sourceID):\(album.id.rawValue)",
            resourceType: .album,
            appleID: album.id.rawValue,
            catalogID: album.id.rawValue,
            displayName: album.title,
            artistName: album.artistName,
            albumTitle: album.title,
            genreNames: album.genreNames,
            libraryAddedAt: album.libraryAddedDate,
            releaseDate: album.releaseDate.map(Self.yearMonthDayString),
            url: album.url?.absoluteString,
            artworkURL: album.artwork?.url(width: 300, height: 300)?.absoluteString,
            evidenceBasis: evidenceBasis,
            sourceConfidence: sourceConfidence,
            observedSourceRefs: [sourceID]
        )
    }

    private static func playlistResource(_ playlist: Playlist) -> AppleMusicSignalResource {
        AppleMusicSignalResource(
            sourceItemID: "playlist_contexts:\(playlist.id.rawValue)",
            resourceType: .playlist,
            appleID: playlist.id.rawValue,
            libraryID: playlist.id.rawValue,
            displayName: playlist.name,
            playlistName: playlist.name,
            curatorName: playlist.curatorName,
            lastPlayedAt: playlist.lastPlayedDate,
            libraryAddedAt: playlist.libraryAddedDate,
            url: playlist.url?.absoluteString,
            artworkURL: playlist.artwork?.url(width: 300, height: 300)?.absoluteString,
            evidenceBasis: .playlistContext,
            sourceConfidence: .playlistContext,
            observedSourceRefs: ["playlist_contexts"]
        )
    }

    private static func recommendationResources(_ recommendation: MusicPersonalRecommendation) -> [AppleMusicSignalResource] {
        recommendation.albums.map { album in
            AppleMusicSignalResource(
                sourceItemID: "personal_recommendations:\(recommendation.id.rawValue):album:\(album.id.rawValue)",
                resourceType: .album,
                appleID: album.id.rawValue,
                catalogID: album.id.rawValue,
                displayName: album.title,
                artistName: album.artistName,
                albumTitle: album.title,
                genreNames: album.genreNames,
                releaseDate: album.releaseDate.map(Self.yearMonthDayString),
                url: album.url?.absoluteString,
                artworkURL: album.artwork?.url(width: 300, height: 300)?.absoluteString,
                evidenceBasis: .personalRecommendation,
                sourceConfidence: .recommendationContext,
                observedSourceRefs: ["personal_recommendations:\(recommendation.id.rawValue)"]
            )
        } + recommendation.playlists.map { playlist in
            AppleMusicSignalResource(
                sourceItemID: "personal_recommendations:\(recommendation.id.rawValue):playlist:\(playlist.id.rawValue)",
                resourceType: .playlist,
                appleID: playlist.id.rawValue,
                catalogID: playlist.id.rawValue,
                displayName: playlist.name,
                playlistName: playlist.name,
                curatorName: playlist.curatorName,
                url: playlist.url?.absoluteString,
                artworkURL: playlist.artwork?.url(width: 300, height: 300)?.absoluteString,
                evidenceBasis: .personalRecommendation,
                sourceConfidence: .recommendationContext,
                observedSourceRefs: ["personal_recommendations:\(recommendation.id.rawValue)"]
            )
        }
    }

    private static func subscriptionStatus(for subscription: MusicSubscription) -> String {
        let catalog = subscription.canPlayCatalogContent ? "catalog_playback_allowed" : "catalog_playback_unavailable"
        let library = subscription.hasCloudLibraryEnabled ? "cloud_library_enabled" : "cloud_library_disabled"
        return "\(catalog)_\(library)"
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

    private static func resources(
        from json: JSONValue,
        sourceID: String,
        cap: Int,
        evidenceBasis: AppleMusicEvidenceBasis,
        sourceConfidence: AppleMusicSignalSourceConfidence
    ) -> [AppleMusicSignalResource] {
        resources(
            fromValues: resourceValues(from: json),
            sourceID: sourceID,
            cap: cap,
            evidenceBasis: evidenceBasis,
            sourceConfidence: sourceConfidence
        )
    }

    private static func rootDataResources(
        from json: JSONValue,
        sourceID: String,
        cap: Int,
        evidenceBasis: AppleMusicEvidenceBasis,
        sourceConfidence: AppleMusicSignalSourceConfidence
    ) -> [AppleMusicSignalResource] {
        guard case .object(let root) = json else {
            return []
        }
        return resourcesFromData(
            root["data"],
            sourceID: sourceID,
            cap: cap,
            evidenceBasis: evidenceBasis,
            sourceConfidence: sourceConfidence
        )
    }

    private static func resourcesFromData(
        _ data: JSONValue?,
        sourceID: String,
        cap: Int,
        evidenceBasis: AppleMusicEvidenceBasis,
        sourceConfidence: AppleMusicSignalSourceConfidence
    ) -> [AppleMusicSignalResource] {
        var values = [JSONValue]()
        appendResourceValues(fromData: data, to: &values)
        return resources(
            fromValues: values,
            sourceID: sourceID,
            cap: cap,
            evidenceBasis: evidenceBasis,
            sourceConfidence: sourceConfidence
        )
    }

    private static func resources(
        fromValues values: [JSONValue],
        sourceID: String,
        cap: Int,
        evidenceBasis: AppleMusicEvidenceBasis,
        sourceConfidence: AppleMusicSignalSourceConfidence
    ) -> [AppleMusicSignalResource] {
        var seen = Set<String>()
        let resources: [AppleMusicSignalResource] = values.compactMap { value in
            guard case .object(let object) = value,
                  case .string(let rawID)? = object["id"],
                  case .string(let rawType)? = object["type"] else {
                return nil
            }
            guard seen.insert("\(rawType):\(rawID)").inserted else {
                return nil
            }
            let attributes: [String: JSONValue]
            if case .object(let rawAttributes)? = object["attributes"] {
                attributes = rawAttributes
            } else {
                attributes = [:]
            }
            let isLibrary = rawType.hasPrefix("library-")
            let resourceType = Self.resourceType(from: rawType)
            let displayName = string(attributes["title"]) ?? string(attributes["name"]) ?? rawID
            return AppleMusicSignalResource(
                sourceItemID: "\(sourceID):\(rawID)",
                resourceType: resourceType,
                appleID: rawID,
                catalogID: isLibrary ? nil : rawID,
                libraryID: isLibrary ? rawID : nil,
                displayName: displayName,
                artistName: string(attributes["artistName"]),
                albumTitle: string(attributes["albumName"]),
                playlistName: resourceType == .playlist ? displayName : nil,
                genreNames: stringArray(attributes["genreNames"]),
                lastPlayedAt: date(from: attributes["lastPlayedDate"]),
                releaseDate: string(attributes["releaseDate"]),
                url: string(attributes["url"]),
                artworkURL: artworkURL(from: attributes["artwork"]),
                evidenceBasis: evidenceBasis,
                sourceConfidence: sourceConfidence,
                observedSourceRefs: [sourceID]
            )
        }
        return Array(resources.prefix(cap))
    }

    private static func resourceValues(from json: JSONValue) -> [JSONValue] {
        guard case .object(let root) = json else {
            return []
        }

        var values: [JSONValue] = []
        appendResourceValues(fromData: root["data"], to: &values)

        let topLevelResources = values
        for value in topLevelResources {
            guard case .object(let object) = value else {
                continue
            }

            if case .object(let relationships)? = object["relationships"] {
                for relationship in relationships.values {
                    guard case .object(let relationshipObject) = relationship else {
                        continue
                    }
                    appendResourceValues(fromData: relationshipObject["data"], to: &values)
                }
            }

            if case .object(let views)? = object["views"] {
                for view in views.values {
                    guard case .object(let viewObject) = view else {
                        continue
                    }
                    appendResourceValues(fromData: viewObject["data"], to: &values)
                }
            }
        }

        return values
    }

    private static func dataValue(from json: JSONValue) -> JSONValue? {
        guard case .object(let root) = json else {
            return nil
        }
        return root["data"]
    }

    private static func hasNextPage(_ json: JSONValue) -> Bool {
        nextURL(from: json) != nil
    }

    private static func nextURL(from json: JSONValue) -> URL? {
        guard case .object(let root) = json,
              case .string(let next)? = root["next"],
              !next.isEmpty else {
            return nil
        }
        if let url = URL(string: next), url.scheme != nil {
            return url
        }
        return URL(string: "https://api.music.apple.com\(next)")
    }

    private static func replayViewObject(from json: JSONValue, viewID: String) -> JSONValue? {
        guard case .object(let root) = json else {
            return nil
        }
        let topLevelData: [JSONValue]
        switch root["data"] {
        case .array(let array)?:
            topLevelData = array
        case .object?:
            topLevelData = [root["data"]].compactMap { $0 }
        case .string, .number, .bool, .null, nil:
            topLevelData = []
        }

        for value in topLevelData {
            guard case .object(let object) = value,
                  case .object(let views)? = object["views"],
                  let view = views[viewID] else {
                continue
            }
            return view
        }
        return nil
    }

    private static func appendResourceValues(fromData data: JSONValue?, to values: inout [JSONValue]) {
        switch data {
        case .array(let array):
            values.append(contentsOf: array)
        case .object:
            if let data {
                values.append(data)
            }
        case .string, .number, .bool, .null, nil:
            break
        }
    }

    private static func diagnosticExcludedSources(capturedAt: Date) -> [AppleMusicSignalSourceSection] {
        [
            .diagnosticExcluded(sourceID: "library_artists_alphabetical_snapshot", cap: 50, capturedAt: capturedAt, reason: "Unsorted MusicLibraryRequest<Artist> snapshots are disabled and excluded from Survey evidence in v0.2.", items: []),
            .diagnosticExcluded(sourceID: "library_albums_alphabetical_snapshot", cap: 50, capturedAt: capturedAt, reason: "Unsorted MusicLibraryRequest<Album> snapshots are disabled and excluded from Survey evidence in v0.2.", items: []),
            .diagnosticExcluded(sourceID: "library_songs_alphabetical_snapshot", cap: 100, capturedAt: capturedAt, reason: "Unsorted MusicLibraryRequest<Song> snapshots are disabled and excluded from Survey evidence; only sorted song windows are primary evidence.", items: [])
        ]
    }

    private static func url(_ string: String) -> URL {
        guard let url = URL(string: string) else {
            preconditionFailure("Invalid static Apple Music API URL: \(string)")
        }
        return url
    }

    private static func resourceType(from rawType: String) -> AppleMusicSignalResourceType {
        let normalized = rawType.replacingOccurrences(of: "library-", with: "")
        switch normalized {
        case "artist", "artists":
            return .artist
        case "album", "albums":
            return .album
        case "song", "songs":
            return .song
        case "playlist", "playlists":
            return .playlist
        case "station", "stations":
            return .station
        case "genre", "genres":
            return .genre
        default:
            return .unknown
        }
    }

    private static func string(_ value: JSONValue?) -> String? {
        guard case .string(let string)? = value else {
            return nil
        }
        return string
    }

    private static func stringArray(_ value: JSONValue?) -> [String] {
        guard case .array(let array)? = value else {
            return []
        }
        return array.compactMap { value in
            guard case .string(let string) = value else {
                return nil
            }
            return string
        }
    }

    private static func artworkURL(from value: JSONValue?) -> String? {
        guard case .object(let artwork)? = value,
              let template = string(artwork["url"]) else {
            return nil
        }
        return template
            .replacingOccurrences(of: "{w}", with: "300")
            .replacingOccurrences(of: "{h}", with: "300")
    }

    private static func date(from value: JSONValue?) -> Date? {
        guard let string = string(value) else {
            return nil
        }
        return ISO8601DateFormatter().date(from: string)
    }

    private static func yearMonthDayString(_ date: Date) -> String {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withFullDate]
        return formatter.string(from: date)
    }

    private static func error(source: String, error: Error) -> AppleMusicSignalProbeError {
        #if canImport(MusicKit)
        if let requestError = error as? MusicDataRequest.Error {
            return AppleMusicSignalProbeError(
                source: source,
                code: "music_data_request_http_\(requestError.status)",
                message: [
                    requestError.title,
                    requestError.detailText
                ]
                .filter { !$0.isEmpty }
                .joined(separator: ": ")
            )
        }
        #endif

        return AppleMusicSignalProbeError(
            source: source,
            code: String(describing: type(of: error)),
            message: error.musicAtlasDiagnosticDescription
        )
    }
}
