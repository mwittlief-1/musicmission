import Foundation

#if canImport(MusicKit)
import MusicKit
#endif

protocol SurveyArtworkServing {
    func artworkURL(for item: SurveyItem) async -> URL?
}

struct MusicKitSurveyArtworkService: SurveyArtworkServing {
    func artworkURL(for item: SurveyItem) async -> URL? {
        if let artworkURL = item.artworkURL {
            return artworkURL
        }

        #if canImport(MusicKit)
        do {
            switch item.kind {
            case .artist:
                var request = MusicCatalogSearchRequest(term: item.title, types: [Artist.self])
                request.limit = 3
                let response = try await request.response()
                return response.artists.first?.artwork?.url(width: 320, height: 320)
            case .album:
                var request = MusicCatalogSearchRequest(term: Self.searchTerm(for: item), types: [Album.self])
                request.limit = 5
                let response = try await request.response()
                let match = Self.bestAlbumMatch(from: response.albums, item: item)
                return match?.artwork?.url(width: 320, height: 320)
            case .song:
                var request = MusicCatalogSearchRequest(term: Self.searchTerm(for: item), types: [Song.self])
                request.limit = 5
                let response = try await request.response()
                let match = Self.bestSongMatch(from: response.songs, item: item)
                return match?.artwork?.url(width: 320, height: 320)
            }
        } catch {
            return nil
        }
        #else
        return nil
        #endif
    }

    private static func searchTerm(for item: SurveyItem) -> String {
        [item.title, item.subtitle]
            .compactMap { $0?.trimmingCharacters(in: .whitespacesAndNewlines) }
            .filter { !$0.isEmpty }
            .joined(separator: " ")
    }

    #if canImport(MusicKit)
    private static func bestAlbumMatch(from albums: MusicItemCollection<Album>, item: SurveyItem) -> Album? {
        guard let subtitle = item.subtitle?.normalizedForCatalogMatching, !subtitle.isEmpty else {
            return albums.first
        }

        return albums.first { album in
            album.artistName.normalizedForCatalogMatching.contains(subtitle)
        } ?? albums.first
    }

    private static func bestSongMatch(from songs: MusicItemCollection<Song>, item: SurveyItem) -> Song? {
        guard let subtitle = item.subtitle?.normalizedForCatalogMatching, !subtitle.isEmpty else {
            return songs.first
        }

        return songs.first { song in
            song.artistName.normalizedForCatalogMatching.contains(subtitle)
        } ?? songs.first
    }
    #endif
}

@MainActor
final class SurveyArtworkStore: ObservableObject {
    @Published private var artworkURLs: [String: URL] = [:]

    private let service: SurveyArtworkServing
    private var inFlightItemIDs = Set<String>()

    init(service: SurveyArtworkServing = MusicKitSurveyArtworkService()) {
        self.service = service
    }

    func artworkURL(for item: SurveyItem) -> URL? {
        artworkURLs[item.id] ?? item.artworkURL
    }

    func fetchArtwork(for items: [SurveyItem]) async {
        for item in items where artworkURLs[item.id] == nil && !inFlightItemIDs.contains(item.id) {
            inFlightItemIDs.insert(item.id)
            let artworkURL = await service.artworkURL(for: item)
            inFlightItemIDs.remove(item.id)

            if let artworkURL {
                artworkURLs[item.id] = artworkURL
            }
        }
    }
}

private extension String {
    var normalizedForCatalogMatching: String {
        folding(options: [.diacriticInsensitive, .caseInsensitive], locale: .current)
            .components(separatedBy: CharacterSet.alphanumerics.inverted)
            .filter { !$0.isEmpty }
            .joined(separator: " ")
    }
}
