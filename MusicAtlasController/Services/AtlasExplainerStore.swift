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
    let scoredArchetypes: [AtlasSurveyArchetypeScore]

    static let empty = AtlasExplainerLibrary(sourcePackage: "", packs: [], scoredArchetypes: [])

    var packCount: Int {
        packs.count
    }

    var homePackCount: Int {
        homeSections.reduce(0) { $0 + $1.packs.count }
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

    var homeSections: [AtlasExplainerHomeSection] {
        let sections = scoredArchetypes.isEmpty ? fallbackHomeSections() : scoredHomeSections()
        return sections.filter { !$0.packs.isEmpty }
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

    func withScoredArchetypes(_ scoredArchetypes: [AtlasSurveyArchetypeScore]) -> AtlasExplainerLibrary {
        AtlasExplainerLibrary(
            sourcePackage: sourcePackage,
            packs: packs,
            scoredArchetypes: scoredArchetypes
        )
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

    private func scoredHomeSections() -> [AtlasExplainerHomeSection] {
        let packByArchetypeID = Dictionary(uniqueKeysWithValues: packs.map { ($0.identity.archetypeID, $0) })
        let eligibleScores = scoredArchetypes
            .filter { $0.totalSignalScore > 0 && packByArchetypeID[$0.archetypeID] != nil }

        var usedArchetypeIDs = Set<String>()

        let likelyScores = eligibleScores
            .filter { !$0.hasLimitedSurveySignals && $0.positiveScore >= max(4, $0.negativeScore * 1.25) }
            .sorted(by: scoreSort)
            .prefix(4)
        let likelyPacks = packs(for: likelyScores, packByArchetypeID: packByArchetypeID, usedArchetypeIDs: &usedArchetypeIDs)

        let boundaryScores = eligibleScores
            .filter { score in
                guard !usedArchetypeIDs.contains(score.archetypeID) else {
                    return false
                }
                return score.hasLimitedSurveySignals ||
                    score.negativeScore > 0 ||
                    score.questionScore >= max(2, score.positiveScore * 0.8)
            }
            .sorted(by: boundarySort)
            .prefix(3)
        var boundaryPacks = packs(for: boundaryScores, packByArchetypeID: packByArchetypeID, usedArchetypeIDs: &usedArchetypeIDs)

        if boundaryPacks.isEmpty {
            let openQuestionScores = eligibleScores
                .filter { !usedArchetypeIDs.contains($0.archetypeID) }
                .sorted(by: openQuestionSort)
                .prefix(1)
            boundaryPacks = packs(for: openQuestionScores, packByArchetypeID: packByArchetypeID, usedArchetypeIDs: &usedArchetypeIDs)
        }

        let remainingLimit = max(0, AtlasExplainerRuntimePolicy.alphaHomePackLimit - likelyPacks.count - boundaryPacks.count)
        let frontierScores = eligibleScores
            .filter { !usedArchetypeIDs.contains($0.archetypeID) && !$0.hasLimitedSurveySignals }
            .sorted(by: frontierSort)
            .prefix(remainingLimit)
        let frontierPacks = packs(for: frontierScores, packByArchetypeID: packByArchetypeID, usedArchetypeIDs: &usedArchetypeIDs)

        return [
            AtlasExplainerHomeSection(kind: .likelyRegions, packs: likelyPacks),
            AtlasExplainerHomeSection(kind: .frontiers, packs: frontierPacks),
            AtlasExplainerHomeSection(kind: .boundaries, packs: boundaryPacks)
        ]
    }

    private func fallbackHomeSections() -> [AtlasExplainerHomeSection] {
        [
            AtlasExplainerHomeSection(
                kind: .likelyRegions,
                packs: ["070", "069", "075"].compactMap(pack(archetypeID:))
            ),
            AtlasExplainerHomeSection(
                kind: .frontiers,
                packs: ["016", "017", "061"].compactMap(pack(archetypeID:))
            ),
            AtlasExplainerHomeSection(
                kind: .boundaries,
                packs: ["059", "056", "060"].compactMap(pack(archetypeID:))
            )
        ]
    }

    private func packs<S: Sequence>(
        for scores: S,
        packByArchetypeID: [String: AtlasExplainerRenderPack],
        usedArchetypeIDs: inout Set<String>
    ) -> [AtlasExplainerRenderPack] where S.Element == AtlasSurveyArchetypeScore {
        scores.compactMap { score in
            guard !usedArchetypeIDs.contains(score.archetypeID),
                  let pack = packByArchetypeID[score.archetypeID] else {
                return nil
            }
            usedArchetypeIDs.insert(score.archetypeID)
            return pack
        }
    }

    private func scoreSort(_ lhs: AtlasSurveyArchetypeScore, _ rhs: AtlasSurveyArchetypeScore) -> Bool {
        if lhs.netPositiveScore != rhs.netPositiveScore {
            return lhs.netPositiveScore > rhs.netPositiveScore
        }
        if lhs.positiveScore != rhs.positiveScore {
            return lhs.positiveScore > rhs.positiveScore
        }
        return lhs.archetypeID < rhs.archetypeID
    }

    private func frontierSort(_ lhs: AtlasSurveyArchetypeScore, _ rhs: AtlasSurveyArchetypeScore) -> Bool {
        if lhs.netPositiveScore != rhs.netPositiveScore {
            return lhs.netPositiveScore > rhs.netPositiveScore
        }
        if lhs.totalSignalScore != rhs.totalSignalScore {
            return lhs.totalSignalScore > rhs.totalSignalScore
        }
        return lhs.archetypeID < rhs.archetypeID
    }

    private func boundarySort(_ lhs: AtlasSurveyArchetypeScore, _ rhs: AtlasSurveyArchetypeScore) -> Bool {
        if lhs.hasLimitedSurveySignals != rhs.hasLimitedSurveySignals {
            return lhs.hasLimitedSurveySignals
        }
        if lhs.hasLimitedSurveySignals && rhs.hasLimitedSurveySignals {
            if lhs.netPositiveScore != rhs.netPositiveScore {
                return lhs.netPositiveScore > rhs.netPositiveScore
            }
            if lhs.surveySignalCount != rhs.surveySignalCount {
                return lhs.surveySignalCount < rhs.surveySignalCount
            }
        }
        if lhs.questionScore != rhs.questionScore {
            return lhs.questionScore > rhs.questionScore
        }
        if lhs.negativeScore != rhs.negativeScore {
            return lhs.negativeScore > rhs.negativeScore
        }
        return lhs.archetypeID < rhs.archetypeID
    }

    private func openQuestionSort(_ lhs: AtlasSurveyArchetypeScore, _ rhs: AtlasSurveyArchetypeScore) -> Bool {
        if lhs.netPositiveScore != rhs.netPositiveScore {
            return lhs.netPositiveScore < rhs.netPositiveScore
        }
        if lhs.totalSignalScore != rhs.totalSignalScore {
            return lhs.totalSignalScore > rhs.totalSignalScore
        }
        return lhs.archetypeID < rhs.archetypeID
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
    static let resourceName = "atlas_explainer_render_packs_v0_3"
    static let supportedSchemaVersion = "0.3"

    @Published private(set) var loadState: AtlasExplainerLoadState = .idle
    @Published private(set) var library: AtlasExplainerLibrary = .empty

    private let bundle: Bundle
    private let surveyPersistenceStore: SurveyPersistenceStore

    init(
        bundle: Bundle = .main,
        surveyPersistenceStore: SurveyPersistenceStore = SurveyPersistenceStore()
    ) {
        self.bundle = bundle
        self.surveyPersistenceStore = surveyPersistenceStore
    }

    func load() {
        if loadState == .loaded {
            refreshSurveyArchetypeScores()
            return
        }

        loadState = .loading

        do {
            library = try Self.loadLibrary(bundle: bundle)
                .withScoredArchetypes(Self.surveyArchetypeScores(bundle: bundle, persistenceStore: surveyPersistenceStore))
            loadState = .loaded
        } catch {
            loadState = .failed(error.localizedDescription)
        }
    }

    func refreshSurveyArchetypeScores() {
        library = library.withScoredArchetypes(
            Self.surveyArchetypeScores(bundle: bundle, persistenceStore: surveyPersistenceStore)
        )
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
        guard bundle.schemaVersion == supportedSchemaVersion else {
            throw AtlasExplainerStoreError.unsupportedSchemaVersion(bundle.schemaVersion)
        }
        guard bundle.packCount == bundle.packs.count else {
            throw AtlasExplainerStoreError.packCountMismatch(expected: bundle.packCount, actual: bundle.packs.count)
        }

        return AtlasExplainerLibrary(sourcePackage: bundle.sourcePackage, packs: bundle.packs, scoredArchetypes: [])
    }

    private static func surveyArchetypeScores(
        bundle: Bundle,
        persistenceStore: SurveyPersistenceStore
    ) -> [AtlasSurveyArchetypeScore] {
        let session = persistenceStore.load()
        guard !session.responses.isEmpty else {
            return []
        }

        do {
            let songs = try AtlasSurveySongRecord.load(bundle: bundle)
            let itemLookup = FixtureSurveyPageProvider().itemLookup()
            return AtlasSurveyArchetypeScorer.score(session: session, itemLookup: itemLookup, songs: songs)
        } catch {
            return []
        }
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

private struct AtlasSurveyArchetypeScorer {
    static func score(
        session: PersistedSurveySession,
        itemLookup: [String: SurveyItem],
        songs: [AtlasSurveySongRecord]
    ) -> [AtlasSurveyArchetypeScore] {
        var positiveScores = [String: Double]()
        var fineScores = [String: Double]()
        var unknownScores = [String: Double]()
        var negativeScores = [String: Double]()
        var signalItemIDs = [String: Set<String>]()
        let songsByID = Dictionary(uniqueKeysWithValues: songs.map { ($0.canonicalSongRecordingID, $0) })

        for response in session.responses.values {
            guard let item = itemLookup[response.itemID] ?? visibleItem(response.itemID, session: session) else {
                continue
            }

            let matchedSongs = matchingSongs(for: item, songs: songs, songsByID: songsByID)
            guard !matchedSongs.isEmpty else {
                continue
            }

            let scopedSongs = Array(matchedSongs.prefix(24))
            let responseArchetypeIDs = Set(scopedSongs.flatMap(\.archetypeIDs))
            for archetypeID in responseArchetypeIDs {
                signalItemIDs[archetypeID, default: []].insert(response.itemID)
            }

            for song in scopedSongs {
                for archetypeID in song.archetypeIDs {
                    switch response.state {
                    case .favorite:
                        positiveScores[archetypeID, default: 0] += 4
                    case .like:
                        positiveScores[archetypeID, default: 0] += 3
                    case .fine:
                        fineScores[archetypeID, default: 0] += 1
                    case .dontKnow:
                        unknownScores[archetypeID, default: 0] += 0.35
                    case .notForMe:
                        negativeScores[archetypeID, default: 0] += 4
                    }
                }
            }
        }

        let archetypeIDs = Set(positiveScores.keys)
            .union(fineScores.keys)
            .union(unknownScores.keys)
            .union(negativeScores.keys)

        return archetypeIDs
            .map { archetypeID in
                AtlasSurveyArchetypeScore(
                    archetypeID: archetypeID,
                    positiveScore: positiveScores[archetypeID] ?? 0,
                    fineScore: fineScores[archetypeID] ?? 0,
                    unknownScore: unknownScores[archetypeID] ?? 0,
                    negativeScore: negativeScores[archetypeID] ?? 0,
                    surveySignalCount: signalItemIDs[archetypeID]?.count ?? 0
                )
            }
            .sorted { lhs, rhs in
                if lhs.netPositiveScore != rhs.netPositiveScore {
                    return lhs.netPositiveScore > rhs.netPositiveScore
                }
                if lhs.totalSignalScore != rhs.totalSignalScore {
                    return lhs.totalSignalScore > rhs.totalSignalScore
                }
                return lhs.archetypeID < rhs.archetypeID
            }
    }

    private static func visibleItem(_ itemID: String, session: PersistedSurveySession) -> SurveyItem? {
        session.displayedPages.values
            .flatMap(\.items)
            .first { $0.id == itemID }
    }

    private static func matchingSongs(
        for item: SurveyItem,
        songs: [AtlasSurveySongRecord],
        songsByID: [String: AtlasSurveySongRecord]
    ) -> [AtlasSurveySongRecord] {
        if item.kind == .song,
           let canonicalID = canonicalID(from: item.id, prefix: "ALPHA_SONG_"),
           let song = songsByID[canonicalID] {
            return [song]
        }

        let titleKey = normalizedKey(item.title)
        let subtitleKey = item.subtitle.map(normalizedKey)
        switch item.kind {
        case .artist:
            return songs.filter { song in
                song.artistNames.map(normalizedKey).contains(titleKey)
            }
        case .album:
            guard let subtitleKey else {
                return []
            }
            return songs.filter { song in
                song.artistNames.map(normalizedKey).contains(subtitleKey)
            }
        case .song:
            return songs.filter { song in
                normalizedKey(song.displayName) == titleKey &&
                    (subtitleKey == nil || song.artistNames.map(normalizedKey).contains(subtitleKey ?? ""))
            }
        }
    }

    private static func canonicalID(from itemID: String, prefix: String) -> String? {
        guard itemID.hasPrefix(prefix) else {
            return nil
        }
        return String(itemID.dropFirst(prefix.count))
    }

    private static func normalizedKey(_ value: String) -> String {
        value
            .folding(options: [.caseInsensitive, .diacriticInsensitive], locale: Locale(identifier: "en_US_POSIX"))
            .lowercased()
            .components(separatedBy: CharacterSet.alphanumerics.inverted)
            .filter { !$0.isEmpty }
            .joined(separator: "-")
    }
}

private struct AtlasSurveySongRecord: Decodable, Equatable {
    let canonicalSongRecordingID: String
    let displayName: String
    let archetypeIDs: [String]
    let artistNames: [String]

    enum CodingKeys: String, CodingKey {
        case canonicalSongRecordingID = "canonical_song_recording_id"
        case displayName = "display_name"
        case archetypeIDs = "archetype_ids"
        case artistNames = "artist_names"
    }

    static func load(bundle: Bundle) throws -> [AtlasSurveySongRecord] {
        guard let url = bundle.url(forResource: "canonical_song_recordings", withExtension: "json") else {
            throw AtlasExplainerStoreError.missingBundleResource("canonical_song_recordings")
        }
        let data = try Data(contentsOf: url)
        return try JSONDecoder().decode([AtlasSurveySongRecord].self, from: data)
    }
}
