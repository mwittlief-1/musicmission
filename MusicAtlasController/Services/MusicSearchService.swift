import Foundation

#if canImport(MusicKit)
import MusicKit
#endif

protocol MusicSearchServing {
    func resolve(item: MissionItem, at date: Date) async throws -> AppleMusicResolution
}

struct StubMusicSearchService: MusicSearchServing {
    func resolve(item: MissionItem, at date: Date) async throws -> AppleMusicResolution {
        AppleMusicResolution(
            status: .resolved,
            catalogID: "stub_\(item.itemID.lowercased())",
            catalogURL: URL(string: "https://music.apple.com/us/song/dev-stub-\(item.itemID.lowercased())"),
            artworkURL: nil,
            storefront: "dev_stub",
            resolvedTitle: item.title,
            resolvedArtist: item.artist,
            resolvedAlbum: item.album,
            confidence: 0.95,
            resolver: .system,
            resolvedAt: date,
            reason: "stubbed_simulated_resolution_for_dev_export",
            candidateCount: 1,
            errorCode: nil,
            errorMessage: nil
        )
    }
}

struct MusicKitCatalogSearchService: MusicSearchServing {
    private let canonicalIndex: CanonicalAppleMusicCatalogIndex

    init(canonicalIndex: CanonicalAppleMusicCatalogIndex = .loadFromBundle()) {
        self.canonicalIndex = canonicalIndex
    }

    func resolve(item: MissionItem, at date: Date) async throws -> AppleMusicResolution {
        if let indexedResolution = canonicalIndex.resolution(for: item, at: date) {
            return indexedResolution
        }

        #if canImport(MusicKit)
        do {
            let searchTerm = Self.searchTerm(for: item)
            var request = MusicCatalogSearchRequest(term: searchTerm, types: [Song.self])
            request.limit = 5

            let response = try await request.response()
            let candidates = Array(response.songs.prefix(5))
            let storefront = try? await MusicDataRequest.currentCountryCode

            guard let bestMatch = candidates.first else {
                return AppleMusicResolution(
                    status: .unresolved,
                    catalogID: nil,
                    catalogURL: nil,
                    artworkURL: nil,
                    storefront: storefront,
                    resolvedTitle: nil,
                    resolvedArtist: nil,
                    resolvedAlbum: nil,
                    confidence: nil,
                    resolver: .automaticSearch,
                    resolvedAt: date,
                    reason: "music_kit_catalog_search_returned_no_song_results",
                    candidateCount: 0,
                    errorCode: nil,
                    errorMessage: nil
                )
            }

            let confidence = Self.confidence(for: bestMatch, item: item)
            let status: ResolutionStatus = confidence >= 0.7 ? .resolved : .ambiguous

            return AppleMusicResolution(
                status: status,
                catalogID: bestMatch.id.rawValue,
                catalogURL: bestMatch.url,
                artworkURL: bestMatch.artwork?.url(width: 600, height: 600),
                storefront: storefront,
                resolvedTitle: bestMatch.title,
                resolvedArtist: bestMatch.artistName,
                resolvedAlbum: bestMatch.albumTitle,
                confidence: confidence,
                resolver: .automaticSearch,
                resolvedAt: date,
                reason: status == .resolved ? "music_kit_catalog_search_top_result" : "music_kit_catalog_search_top_result_needs_manual_review",
                candidateCount: candidates.count,
                errorCode: nil,
                errorMessage: nil
            )
        } catch {
            return .failed(
                resolver: .automaticSearch,
                resolvedAt: date,
                reason: "music_kit_catalog_search_failed",
                error: error
            )
        }
        #else
        throw MusicSearchServiceError.musicKitUnavailable
        #endif
    }

    private static func searchTerm(for item: MissionItem) -> String {
        [item.title, item.artist, item.album]
            .compactMap { $0?.trimmingCharacters(in: .whitespacesAndNewlines) }
            .filter { !$0.isEmpty }
            .joined(separator: " ")
    }

    #if canImport(MusicKit)
    private static func confidence(for song: Song, item: MissionItem) -> Double {
        let titleScore = stringMatchScore(candidate: song.title, expected: item.title)
        let artistScore = stringMatchScore(candidate: song.artistName, expected: item.artist)
        let albumScore = stringMatchScore(candidate: song.albumTitle, expected: item.album)

        if item.album == nil {
            return min(0.99, (titleScore * 0.6) + (artistScore * 0.4))
        }

        return min(0.99, (titleScore * 0.5) + (artistScore * 0.35) + (albumScore * 0.15))
    }
    #endif

    private static func stringMatchScore(candidate: String?, expected: String?) -> Double {
        guard let expected = expected?.normalizedForCatalogMatching, !expected.isEmpty else {
            return 1
        }

        guard let candidate = candidate?.normalizedForCatalogMatching, !candidate.isEmpty else {
            return 0
        }

        if candidate == expected {
            return 1
        }

        if candidate.contains(expected) || expected.contains(candidate) {
            return 0.82
        }

        let candidateTerms = Set(candidate.split(separator: " "))
        let expectedTerms = Set(expected.split(separator: " "))
        guard !candidateTerms.isEmpty, !expectedTerms.isEmpty else {
            return 0
        }

        let overlap = candidateTerms.intersection(expectedTerms).count
        return Double(overlap) / Double(max(candidateTerms.count, expectedTerms.count))
    }
}

enum MusicSearchServiceError: LocalizedError {
    case musicKitUnavailable

    var errorDescription: String? {
        switch self {
        case .musicKitUnavailable:
            return "MusicKit is not available in this build environment."
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
