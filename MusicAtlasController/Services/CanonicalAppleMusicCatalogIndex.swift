import Foundation

struct CanonicalAppleMusicCatalogIndex {
    static let empty = CanonicalAppleMusicCatalogIndex(entries: [])

    private let entries: [Entry]
    private let entriesByKey: [String: Entry]

    init(entries: [Entry]) {
        let sortedEntries = entries.sorted {
            if $0.priority != $1.priority {
                return $0.priority > $1.priority
            }
            return $0.entryID < $1.entryID
        }
        self.entries = sortedEntries
        self.entriesByKey = sortedEntries.reduce(into: [String: Entry]()) { result, entry in
            for key in entry.matchKeys where result[key] == nil {
                result[key] = entry
            }
        }
    }

    static func loadFromBundle(_ bundle: Bundle = .main) -> CanonicalAppleMusicCatalogIndex {
        let bundles = [bundle, Bundle.main] + Bundle.allBundles + Bundle.allFrameworks
        guard let url = bundles.lazy.compactMap({
            $0.url(forResource: "canonical_apple_music_catalog_index_v1", withExtension: "json")
        }).first,
              let data = try? Data(contentsOf: url),
              let payload = try? JSONDecoder().decode(Payload.self, from: data) else {
            return .empty
        }
        return CanonicalAppleMusicCatalogIndex(entries: payload.entries)
    }

    func resolution(for item: MissionItem, at date: Date) -> AppleMusicResolution? {
        guard let entry = lookupEntry(for: item) else {
            return nil
        }

        return AppleMusicResolution(
            status: .resolved,
            catalogID: entry.appleCatalogID,
            catalogURL: entry.appleCatalogURL.flatMap(URL.init(string:)),
            artworkURL: nil,
            storefront: entry.storefront,
            resolvedTitle: entry.resolvedTitle.nilIfBlank ?? item.title,
            resolvedArtist: entry.resolvedArtist.nilIfBlank ?? item.artist,
            resolvedAlbum: entry.resolvedAlbum.nilIfBlank ?? item.album,
            confidence: entry.confidence,
            resolver: .cached,
            resolvedAt: date,
            reason: "canonical_apple_music_catalog_index_v1:\(entry.sourceType):\(entry.matchStatus)",
            candidateCount: 1,
            errorCode: nil,
            errorMessage: nil
        )
    }

    private func lookupEntry(for item: MissionItem) -> Entry? {
        for key in Self.matchKeys(for: item) {
            if let entry = entriesByKey[key], entry.itemType == item.indexItemType {
                return entry
            }
        }
        return nil
    }

    private static func matchKeys(for item: MissionItem) -> [String] {
        let routeType = item.itemType == .album ? "album" : "track"
        let routeDisplayIdentity = item.routeDisplayIdentityKey.nilIfBlank
            ?? [routeType, item.artist, item.title].map(normalizedIdentityPart).joined(separator: ":")

        var keys = [
            item.itemID.nilIfBlank.map { "candidate_id:\($0)" },
            item.candidateID.nilIfBlank.map { "candidate_id:\($0)" },
            item.routeCandidateKey.nilIfBlank.map { "route_candidate_key:\($0)" },
            item.routeBatchDedupeKey.nilIfBlank.map { "route_batch_dedupe_key:\($0)" },
            "route_display_identity_key:\(routeDisplayIdentity)",
            "normalized_identity:\(routeDisplayIdentity)"
        ].compactMap { $0 }

        if let routeCandidateKey = item.routeCandidateKey.nilIfBlank,
           let canonicalID = routeCandidateKey.split(separator: ":").last {
            keys.append("canonical_entity_id:\(canonicalID)")
        }

        if let routeBatchDedupeKey = item.routeBatchDedupeKey.nilIfBlank,
           let canonicalID = routeBatchDedupeKey.split(separator: ":").last {
            keys.append("canonical_entity_id:\(canonicalID)")
        }

        var seen = Set<String>()
        return keys.filter { seen.insert($0).inserted }
    }

    private static func normalizedIdentityPart(_ value: String) -> String {
        value
            .folding(options: [.diacriticInsensitive, .caseInsensitive], locale: .current)
            .lowercased()
            .replacingOccurrences(of: "&", with: " and ")
            .components(separatedBy: CharacterSet.alphanumerics.inverted)
            .filter { !$0.isEmpty }
            .joined(separator: "-")
    }
}

extension CanonicalAppleMusicCatalogIndex {
    struct Entry: Decodable {
        let entryID: String
        let sourceType: String
        let sourceRef: String
        let itemType: String
        let appleCatalogID: String
        let appleResourceType: String
        let appleAlbumID: String?
        let appleCatalogURL: String?
        let storefront: String?
        let resolvedTitle: String?
        let resolvedArtist: String?
        let resolvedAlbum: String?
        let confidence: Double?
        let matchStatus: String
        let matchBasis: String?
        let priority: Int
        let matchKeys: [String]

        enum CodingKeys: String, CodingKey {
            case entryID = "entry_id"
            case sourceType = "source_type"
            case sourceRef = "source_ref"
            case itemType = "item_type"
            case appleCatalogID = "apple_catalog_id"
            case appleResourceType = "apple_resource_type"
            case appleAlbumID = "apple_album_id"
            case appleCatalogURL = "apple_catalog_url"
            case storefront
            case resolvedTitle = "resolved_title"
            case resolvedArtist = "resolved_artist"
            case resolvedAlbum = "resolved_album"
            case confidence
            case matchStatus = "match_status"
            case matchBasis = "match_basis"
            case priority
            case matchKeys = "match_keys"
        }
    }

    private struct Payload: Decodable {
        let entries: [Entry]
    }
}

private extension MissionItem {
    var indexItemType: String {
        itemType == .album ? "album" : "track"
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
