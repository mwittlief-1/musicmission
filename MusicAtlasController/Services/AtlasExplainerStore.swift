import Foundation

enum AtlasExplainerLoadState: Equatable {
    case idle
    case loading
    case loaded
    case failed(String)
}

struct AtlasExplainerFamilySection: Identifiable, Equatable {
    let familyID: Int
    let familyName: String
    let packs: [AtlasExplainerRenderPack]

    var id: Int {
        familyID
    }
}

struct AtlasExplainerLibrary: Equatable {
    let sourcePackage: String
    let packs: [AtlasExplainerRenderPack]

    static let empty = AtlasExplainerLibrary(sourcePackage: "", packs: [])

    var packCount: Int {
        packs.count
    }

    var familySections: [AtlasExplainerFamilySection] {
        Dictionary(grouping: packs, by: { $0.identity.familyID })
            .map { familyID, packs in
                AtlasExplainerFamilySection(
                    familyID: familyID,
                    familyName: packs.first?.identity.familyName ?? "Family \(familyID)",
                    packs: packs.sorted(by: Self.archetypeSort)
                )
            }
            .sorted { $0.familyID < $1.familyID }
    }

    var proofPacks: [AtlasExplainerRenderPack] {
        ["005", "054"].compactMap(pack(archetypeID:))
    }

    func pack(archetypeID: String) -> AtlasExplainerRenderPack? {
        packs.first { $0.identity.archetypeID == archetypeID }
    }

    func pack(canonicalGraphRef: String) -> AtlasExplainerRenderPack? {
        packs.first { $0.identity.canonicalGraphRef == canonicalGraphRef }
    }

    func pack(matchingRouteRefs routeRefs: Set<String>) -> AtlasExplainerRenderPack? {
        pack(matchingRouteRefs: routeRefs.sorted())
    }

    func pack(matchingRouteRefs routeRefs: [String]) -> AtlasExplainerRenderPack? {
        let expandedRouteRefs = Self.expandedRouteRefsInOrder(from: routeRefs)
        let expandedRouteRefSet = Set(expandedRouteRefs)
        let firstIndexByRef = Dictionary(uniqueKeysWithValues: expandedRouteRefs.enumerated().map { ($0.element, $0.offset) })

        return packs
            .compactMap { pack -> AtlasExplainerPackMatch? in
                let matchingRefs = pack.matchingGraphRefs.intersection(expandedRouteRefSet)
                guard !matchingRefs.isEmpty else {
                    return nil
                }

                return AtlasExplainerPackMatch(
                    pack: pack,
                    hasCanonicalGraphRefMatch: matchingRefs.contains(pack.identity.canonicalGraphRef),
                    matchedRefCount: matchingRefs.count,
                    firstMatchIndex: matchingRefs.compactMap { firstIndexByRef[$0] }.min() ?? Int.max
                )
            }
            .sorted(by: Self.matchSort)
            .first?
            .pack
    }

    func pack(matching mission: Mission) -> AtlasExplainerRenderPack? {
        pack(matchingRouteRefs: Self.routeRefs(in: mission))
    }

    func personalizationCopy(
        for pack: AtlasExplainerRenderPack,
        state: AtlasExplainerState = .empty
    ) -> String {
        guard let hook = pack.personalizationHooks.first else {
            return pack.modules.personalizedAtlasOverlay.standard
        }

        return state.canResolve(hook) ? hook.copyVariant : hook.fallbackCopy
    }

    func userFacingStrings() -> [String] {
        let depth = AtlasExplainerRuntimePolicy.alphaCopyDepth
        return packs.flatMap { pack in
            [
                pack.identity.familyName,
                pack.identity.editorialDisplayTitle,
                pack.modules.atlasHomeRegionCard.copy(for: depth),
                pack.modules.regionScenePage.copy(for: depth),
                pack.modules.missionDetailHistoryModule.copy(for: depth),
                pack.modules.didYouKnowCard.copy(for: depth),
                pack.modules.whatToListenForPrompt.copy(for: depth),
                pack.modules.whatToListenForPrompt.compact,
                pack.modules.canonicalExamplesBlock.copy(for: depth),
                pack.modules.relatedRoadsLineageModule.copy(for: depth),
                pack.modules.deadEndFalseNearbyCautionModule.copy(for: depth)
            ] + pack.canonicalExamples.flatMap { example in
                [example.displayLabel, example.whyThisExampleMatters] + example.whatToListenFor
            }
        } + AtlasExplainerRuntimePolicy.userFacingChromeStrings
    }

    static func routeRefs(in mission: Mission) -> [String] {
        var refs = [String]()

        for item in mission.items.sorted(by: { $0.sequence < $1.sequence }) {
            [
                item.candidateID,
                item.routeCandidateKey,
                item.routeBatchDedupeKey,
                item.routeDisplayIdentityKey
            ]
            .compactMap { $0?.trimmingCharacters(in: .whitespacesAndNewlines) }
            .filter { !$0.isEmpty }
            .forEach { appendUnique($0, to: &refs) }

            let normalizedArtist = normalizedRefComponent(item.artist)
            let normalizedTitle = normalizedRefComponent(item.title)
            guard !normalizedArtist.isEmpty, !normalizedTitle.isEmpty else {
                continue
            }

            switch item.itemType {
            case .album:
                appendUnique("album:\(normalizedArtist)-\(normalizedTitle)", to: &refs)
            case .track:
                appendUnique("song_recording:\(normalizedArtist)-\(normalizedTitle)", to: &refs)
            }
        }

        return refs
    }

    private static func expandedRouteRefsInOrder(from routeRefs: [String]) -> [String] {
        var refs = [String]()

        for ref in routeRefs {
            expandedRouteRefs(from: ref).forEach { appendUnique($0, to: &refs) }
        }

        return refs
    }

    private static func expandedRouteRefs(from ref: String) -> [String] {
        var refs = [String]()
        appendUnique(ref, to: &refs)

        if !ref.hasPrefix("survey_candidate:") {
            appendUnique("survey_candidate:\(ref)", to: &refs)
        }

        if ref.hasPrefix("route:track:song_recording:") {
            appendUnique(ref.replacingOccurrences(of: "route:track:", with: ""), to: &refs)
        }

        if ref.hasPrefix("route:album:album:") {
            appendUnique(ref.replacingOccurrences(of: "route:album:", with: ""), to: &refs)
        }

        if ref.hasPrefix("canonical_entity_id:") {
            let entityID = ref.replacingOccurrences(of: "canonical_entity_id:", with: "")
            appendUnique("artist:\(entityID)", to: &refs)
            appendUnique("album:\(entityID)", to: &refs)
            appendUnique("song_recording:\(entityID)", to: &refs)
        }

        return refs
    }

    private static func appendUnique(_ value: String, to refs: inout [String]) {
        guard !refs.contains(value) else {
            return
        }

        refs.append(value)
    }

    private static func matchSort(
        _ lhs: AtlasExplainerPackMatch,
        _ rhs: AtlasExplainerPackMatch
    ) -> Bool {
        if lhs.hasCanonicalGraphRefMatch != rhs.hasCanonicalGraphRefMatch {
            return lhs.hasCanonicalGraphRefMatch
        }

        if lhs.matchedRefCount != rhs.matchedRefCount {
            return lhs.matchedRefCount > rhs.matchedRefCount
        }

        if lhs.firstMatchIndex != rhs.firstMatchIndex {
            return lhs.firstMatchIndex < rhs.firstMatchIndex
        }

        return archetypeSort(lhs.pack, rhs.pack)
    }

    private static func archetypeSort(
        _ lhs: AtlasExplainerRenderPack,
        _ rhs: AtlasExplainerRenderPack
    ) -> Bool {
        if lhs.identity.familyID != rhs.identity.familyID {
            return lhs.identity.familyID < rhs.identity.familyID
        }

        return lhs.identity.archetypeID < rhs.identity.archetypeID
    }

    private static func normalizedRefComponent(_ value: String) -> String {
        let folded = value.folding(options: [.diacriticInsensitive, .caseInsensitive], locale: Locale(identifier: "en_US_POSIX"))
        var output = ""
        var previousWasSeparator = false

        for scalar in folded.unicodeScalars {
            if CharacterSet.alphanumerics.contains(scalar) {
                output.append(Character(scalar))
                previousWasSeparator = false
            } else if !previousWasSeparator {
                output.append("-")
                previousWasSeparator = true
            }
        }

        return output.trimmingCharacters(in: CharacterSet(charactersIn: "-"))
    }
}

private struct AtlasExplainerPackMatch {
    let pack: AtlasExplainerRenderPack
    let hasCanonicalGraphRefMatch: Bool
    let matchedRefCount: Int
    let firstMatchIndex: Int
}

extension AtlasExplainerRenderPack {
    var matchingGraphRefs: Set<String> {
        Set([identity.canonicalGraphRef, graphAlignment.canonicalGraphRef] + graphAlignment.canonicalExampleRefs + graphAlignment.surveyCandidateRefs)
    }
}

final class AtlasExplainerStore: ObservableObject {
    static let resourceName = "atlas_explainer_render_packs_v0_2_3"

    @Published private(set) var loadState: AtlasExplainerLoadState = .idle
    @Published private(set) var library: AtlasExplainerLibrary = .empty

    private let bundle: Bundle

    init(bundle: Bundle = .main) {
        self.bundle = bundle
    }

    func load() {
        guard loadState != .loaded else {
            return
        }

        loadState = .loading

        do {
            library = try Self.loadLibrary(bundle: bundle)
            loadState = .loaded
        } catch {
            loadState = .failed(error.localizedDescription)
        }
    }

    static func loadLibrary(bundle: Bundle = .main) throws -> AtlasExplainerLibrary {
        guard let url = bundle.url(forResource: resourceName, withExtension: "json") else {
            throw AtlasExplainerStoreError.missingBundleResource(resourceName)
        }

        let data = try Data(contentsOf: url)
        return try loadLibrary(data: data)
    }

    static func loadLibrary(data: Data) throws -> AtlasExplainerLibrary {
        let decoder = JSONDecoder()
        let bundle = try decoder.decode(AtlasExplainerPackBundle.self, from: data)
        guard bundle.schemaVersion == "0.2.3" else {
            throw AtlasExplainerStoreError.unsupportedSchemaVersion(bundle.schemaVersion)
        }
        guard bundle.packCount == bundle.packs.count else {
            throw AtlasExplainerStoreError.packCountMismatch(expected: bundle.packCount, actual: bundle.packs.count)
        }

        return AtlasExplainerLibrary(sourcePackage: bundle.sourcePackage, packs: bundle.packs)
    }
}

enum AtlasExplainerStoreError: LocalizedError {
    case missingBundleResource(String)
    case unsupportedSchemaVersion(String)
    case packCountMismatch(expected: Int, actual: Int)

    var errorDescription: String? {
        switch self {
        case .missingBundleResource(let resourceName):
            return "Missing Atlas Explainer bundle resource \(resourceName)."
        case .unsupportedSchemaVersion(let schemaVersion):
            return "Unsupported Atlas Explainer schema version \(schemaVersion)."
        case .packCountMismatch(let expected, let actual):
            return "Atlas Explainer bundle declared \(expected) packs but decoded \(actual)."
        }
    }
}
