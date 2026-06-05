import Foundation

final class AlphaDynamicSurveyPageProvider: SurveyPageProviding {
    private enum ResourceName {
        static let artistSurface = "survey_artist_candidates_v0_2"
        static let albumSurface = "survey_album_candidates_v0_2"
        static let songSurface = "survey_song_candidates_v0_2"
        static let artists = "canonical_artists"
        static let albums = "canonical_albums"
        static let songs = "canonical_song_recordings"
        static let songAffinityTags = "canonical_song_affinity_tags_v0_1"
        static let alphaBlocklist = "alpha_candidate_blocklist_alpha_v0"
    }

    private let candidatesByKind: [SurveyItemKind: [AlphaSurveyRuntimeCandidate]]
    private let candidatesByItemID: [String: AlphaSurveyRuntimeCandidate]
    private let lookup: [String: SurveyItem]
    private let appleCatalogIndex: AlphaAppleCatalogEvidenceStore
    private var appleEvidence = AlphaAppleEvidenceIndex.empty
    private static var cachedCandidates: [AlphaSurveyRuntimeCandidate]?
    private static var cachedAppleCatalogIndex: AlphaAppleCatalogEvidenceStore?
    private static var cachedSongAffinityTags: AlphaSongAffinityTagStore?

    init(bundle: Bundle = .main) {
        let candidates: [AlphaSurveyRuntimeCandidate]
        if let cachedCandidates = Self.cachedCandidates {
            candidates = cachedCandidates
        } else {
            let metadata = Self.loadCanonicalMetadata(bundle: bundle)
            let songAffinityTags = Self.loadSongAffinityTags(bundle: bundle)
            let blocklist = Self.loadBlocklist(bundle: bundle)
            candidates = Self.loadCandidates(
                bundle: bundle,
                metadata: metadata,
                songAffinityTags: songAffinityTags,
                blocklist: blocklist
            )
            Self.cachedCandidates = candidates
        }
        if let cachedAppleCatalogIndex = Self.cachedAppleCatalogIndex {
            appleCatalogIndex = cachedAppleCatalogIndex
        } else {
            appleCatalogIndex = Self.loadAppleCatalogIndex(bundle: bundle)
            Self.cachedAppleCatalogIndex = appleCatalogIndex
        }
        candidatesByKind = Dictionary(grouping: candidates) { $0.kind }
            .mapValues { $0.sortedForFallback() }
        candidatesByItemID = Dictionary(uniqueKeysWithValues: candidates.map { ($0.itemID, $0) })
        lookup = Dictionary(uniqueKeysWithValues: candidates.map { ($0.itemID, $0.surveyItem) })
    }

    func updateAppleMusicSignalPayload(_ payload: AppleMusicSignalPayload?) {
        appleEvidence = AlphaAppleEvidenceIndex(
            payload: payload,
            candidates: Array(candidatesByItemID.values),
            catalogIndex: appleCatalogIndex
        )
    }

    func page(for step: SurveyStep, responses: [String: SurveyResponse]) -> SurveyGridPage? {
        page(for: step, responses: responses, displayedPages: [:])
    }

    func page(
        for step: SurveyStep,
        responses: [String: SurveyResponse],
        displayedPages: [String: SurveyGridPage]
    ) -> SurveyGridPage? {
        guard let descriptor = AlphaSurveyStepDescriptor(step: step) else {
            return nil
        }

        let priorCandidates = priorVisibleCandidates(
            before: step,
            responses: responses,
            displayedPages: displayedPages
        )
        let selected = selectCandidates(
            for: descriptor,
            responses: responses,
            excluding: priorCandidates,
            displayedPages: displayedPages
        )

        return SurveyGridPage(
            id: descriptor.pageID,
            title: descriptor.title,
            subtitle: subtitle(for: descriptor),
            kind: descriptor.kind,
            pageIndex: descriptor.pageNumber,
            isOptional: false,
            items: selected.map {
                $0.surveyItem(appleDerived: appleEvidence.score(for: $0).strength >= 0.10)
            }
        )
    }

    func advancedPage(for filter: SurveyAdvancedFilter, responses: [String: SurveyResponse]) -> SurveyGridPage {
        SurveyFixtureLibrary.advancedPage(for: filter, responses: responses)
    }

    func itemLookup() -> [String: SurveyItem] {
        var merged = SurveyFixtureLibrary.itemLookup()
        for (id, item) in lookup {
            merged[id] = item
        }
        return merged
    }

    func shouldOfferArtistPage3(responses: [String: SurveyResponse]) -> Bool {
        false
    }

    private func priorVisibleCandidates(
        before step: SurveyStep,
        responses: [String: SurveyResponse],
        displayedPages: [String: SurveyGridPage]
    ) -> AlphaPriorVisibleCandidates {
        var priorCandidates = AlphaPriorVisibleCandidates()
        var reconstructionResponses = [String: SurveyResponse]()
        for priorStep in AlphaSurveyStepDescriptor.requiredStepOrder {
            guard priorStep != step else {
                return priorCandidates
            }

            if let displayedPage = displayedPages[priorStep.rawValue] {
                priorCandidates.itemIDs.formUnion(displayedPage.items.map(\.id))
                priorCandidates.displayKeys.formUnion(displayedPage.items.map(displayKey(for:)))
                for itemID in displayedPage.items.map(\.id) {
                    reconstructionResponses[itemID] = responses[itemID]
                }
                continue
            }

            guard let descriptor = AlphaSurveyStepDescriptor(step: priorStep) else {
                continue
            }
            let selected = selectCandidates(
                for: descriptor,
                responses: reconstructionResponses,
                excluding: priorCandidates,
                displayedPages: displayedPages,
                excludeAnsweredCandidates: false
            )
            priorCandidates.itemIDs.formUnion(selected.map(\.itemID))
            priorCandidates.displayKeys.formUnion(selected.map(\.displayKey))
            for itemID in selected.map(\.itemID) {
                reconstructionResponses[itemID] = responses[itemID]
            }
        }
        return priorCandidates
    }

    private func displayKey(for item: SurveyItem) -> String {
        candidatesByItemID[item.id]?.displayKey ?? AlphaStringNormalizer.key(item.title)
    }

    private func selectCandidates(
        for descriptor: AlphaSurveyStepDescriptor,
        responses: [String: SurveyResponse],
        excluding priorCandidates: AlphaPriorVisibleCandidates,
        displayedPages: [String: SurveyGridPage] = [:],
        excludeAnsweredCandidates: Bool = true
    ) -> [AlphaSurveyRuntimeCandidate] {
        let answeredIDs = Set(responses.keys)
        let answeredDisplayKeys = Set(responses.keys.compactMap { candidatesByItemID[$0]?.displayKey })
        let pool = candidatesByKind[descriptor.kind] ?? []
        let baseScored = pool
            .filter { candidate in
                isEligibleForAlphaIntake(candidate, descriptor: descriptor, responses: responses)
            }
            .map { candidate in
                AlphaScoredSurveyCandidate(
                    candidate: candidate,
                    score: score(candidate, for: descriptor, responses: responses),
                    intentBucket: intentBucket(for: candidate, descriptor: descriptor, responses: responses)
                )
            }
            .sorted()
        let scored = baseScored
            .filter { candidate in
                !priorCandidates.itemIDs.contains(candidate.candidate.itemID) &&
                    !priorCandidates.displayKeys.contains(candidate.candidate.displayKey) &&
                    (!excludeAnsweredCandidates || (
                        !answeredIDs.contains(candidate.candidate.itemID) &&
                        !answeredDisplayKeys.contains(candidate.candidate.displayKey)
                    ))
            }

        if appleEvidence.hasUsableSignals,
           let policySelection = policyCandidates(
            for: descriptor,
            responses: responses,
            displayedPages: displayedPages,
            priorCandidates: priorCandidates,
            baseScored: baseScored,
            availableScored: scored
           ),
           !policySelection.isEmpty {
            return policySelection.prefix(SurveyFixtureLibrary.gridPageItemLimit).map(\.candidate)
        }

        let targets = targetMix(for: descriptor)
        var selected: [AlphaScoredSurveyCandidate] = []
        var usedItemIDs = Set<String>()
        var usedDisplayKeys = Set<String>()
        var familyCounts: [Int: Int] = [:]
        var archetypeCounts: [String: Int] = [:]
        var repetitionGovernor = AlphaSurveyRepetitionGovernor(
            kind: descriptor.kind,
            priorCandidates: priorCandidates,
            candidatesByItemID: candidatesByItemID
        )
        let limit = SurveyFixtureLibrary.gridPageItemLimit

        func canAdd(_ scored: AlphaScoredSurveyCandidate, strict: Bool) -> Bool {
            let candidate = scored.candidate
            guard selected.count < limit,
                  !usedItemIDs.contains(candidate.itemID),
                  !usedDisplayKeys.contains(candidate.displayKey) else {
                return false
            }
            guard repetitionGovernor.canAdd(candidate) else {
                return false
            }
            guard strict else {
                return true
            }
            if candidate.familyIDs.contains(where: { (familyCounts[$0] ?? 0) >= descriptor.familyQuota }) {
                return false
            }
            if candidate.archetypeIDs.contains(where: { (archetypeCounts[$0] ?? 0) >= descriptor.archetypeQuota }) {
                return false
            }
            return true
        }

        func append(_ scored: AlphaScoredSurveyCandidate) {
            selected.append(scored)
            usedItemIDs.insert(scored.candidate.itemID)
            usedDisplayKeys.insert(scored.candidate.displayKey)
            for familyID in scored.candidate.familyIDs {
                familyCounts[familyID, default: 0] += 1
            }
            for archetypeID in scored.candidate.archetypeIDs {
                archetypeCounts[archetypeID, default: 0] += 1
            }
            repetitionGovernor.record(scored.candidate)
        }

        for scored in reservedCandidates(for: descriptor, scored: scored) where canAdd(scored, strict: false) {
            append(scored)
            if selected.count >= limit {
                break
            }
        }

        if descriptor.kind == .artist && descriptor.pageNumber <= 2 && appleEvidence.hasUsableSignals {
            for scored in scored where !scored.candidate.isFalseNearby && canAdd(scored, strict: false) {
                append(scored)
                if selected.count >= limit {
                    break
                }
            }
            return selected.prefix(limit).map(\.candidate)
        }

        for (bucket, count) in targets {
            guard selected.count < limit else {
                break
            }
            guard selected.filter({ $0.intentBucket == bucket }).count < count else {
                continue
            }
            for scored in scored where scored.intentBucket == bucket && canAdd(scored, strict: true) {
                guard selected.filter({ $0.intentBucket == bucket }).count < count,
                      selected.count < limit else {
                    break
                }
                append(scored)
                if selected.filter({ $0.intentBucket == bucket }).count >= count ||
                    selected.count >= limit {
                    break
                }
            }
        }

        for strict in [true, false] where selected.count < limit {
            for scored in scored where canAdd(scored, strict: strict) {
                append(scored)
                if selected.count >= limit {
                    break
                }
            }
        }

        return selected.prefix(limit).map(\.candidate)
    }

    private func policyCandidates(
        for descriptor: AlphaSurveyStepDescriptor,
        responses: [String: SurveyResponse],
        displayedPages: [String: SurveyGridPage],
        priorCandidates: AlphaPriorVisibleCandidates,
        baseScored: [AlphaScoredSurveyCandidate],
        availableScored: [AlphaScoredSurveyCandidate]
    ) -> [AlphaScoredSurveyCandidate]? {
        switch (descriptor.kind, descriptor.pageNumber) {
        case (.artist, 1), (.artist, 2):
            let batch = artistIntroPolicyBatch(scored: baseScored)
            return policyPageSlice(batch: batch, fallback: availableScored, priorCandidates: priorCandidates)
        case (.artist, 3), (.artist, 4):
            let introPrior = displayedCandidates(
                for: [.artistPage1, .artistPage2],
                displayedPages: displayedPages
            )
            let followupBase = baseScored.filter {
                !introPrior.itemIDs.contains($0.candidate.itemID) &&
                    !introPrior.displayKeys.contains($0.candidate.displayKey)
            }
            let batch = artistFollowupPolicyBatch(
                scored: followupBase,
                responses: responses,
                displayedPages: displayedPages
            )
            return policyPageSlice(batch: batch, fallback: availableScored, priorCandidates: priorCandidates)
        case (.album, 1), (.album, 2):
            let batch = albumPolicyBatch(scored: baseScored, responses: responses, displayedPages: displayedPages)
            return policyPageSlice(
                batch: batch,
                fallback: availableScored,
                priorCandidates: priorCandidates,
                repetitionGovernor: AlphaSurveyRepetitionGovernor(
                    kind: descriptor.kind,
                    priorCandidates: priorCandidates,
                    candidatesByItemID: candidatesByItemID
                )
            )
        case (.song, _):
            return songPolicyPage(
                descriptor: descriptor,
                scored: availableScored,
                baseScored: baseScored,
                responses: responses,
                displayedPages: displayedPages,
                priorCandidates: priorCandidates
            )
        default:
            return nil
        }
    }

    private func policyPageSlice(
        batch: [AlphaScoredSurveyCandidate],
        fallback: [AlphaScoredSurveyCandidate],
        priorCandidates: AlphaPriorVisibleCandidates,
        repetitionGovernor: AlphaSurveyRepetitionGovernor? = nil
    ) -> [AlphaScoredSurveyCandidate] {
        var selected = [AlphaScoredSurveyCandidate]()
        var usedItemIDs = Set<String>()
        var usedDisplayKeys = Set<String>()
        var repetitionGovernor = repetitionGovernor

        func canUse(_ scored: AlphaScoredSurveyCandidate) -> Bool {
            !priorCandidates.itemIDs.contains(scored.candidate.itemID) &&
                !priorCandidates.displayKeys.contains(scored.candidate.displayKey) &&
                !usedItemIDs.contains(scored.candidate.itemID) &&
                !usedDisplayKeys.contains(scored.candidate.displayKey) &&
                (repetitionGovernor?.canAdd(scored.candidate) ?? true)
        }

        func append(_ candidates: [AlphaScoredSurveyCandidate]) {
            for scored in candidates where selected.count < SurveyFixtureLibrary.gridPageItemLimit && canUse(scored) {
                selected.append(scored)
                usedItemIDs.insert(scored.candidate.itemID)
                usedDisplayKeys.insert(scored.candidate.displayKey)
                repetitionGovernor?.record(scored.candidate)
            }
        }

        append(batch)
        append(fallback)
        return selected
    }

    private func artistIntroPolicyBatch(scored: [AlphaScoredSurveyCandidate]) -> [AlphaScoredSurveyCandidate] {
        let artistScored = scored.filter { $0.candidate.kind == .artist }
        let archetypeIDs = appleEvidence.topArchetypeIDs
        guard !artistScored.isEmpty, !archetypeIDs.isEmpty else {
            return []
        }

        var result = [AlphaScoredSurveyCandidate]()
        var usedItemIDs = Set<String>()

        func appendFirst(_ candidates: [AlphaScoredSurveyCandidate]) -> Bool {
            for scored in candidates where usedItemIDs.insert(scored.candidate.itemID).inserted {
                result.append(scored)
                return true
            }
            return false
        }

        func topArtistCandidates(archetypeID: String) -> [AlphaScoredSurveyCandidate] {
            artistScored
                .filter {
                    $0.candidate.archetypeIDs.contains(archetypeID) &&
                        appleEvidence.directStrength(for: $0.candidate) > 0
                }
                .sorted { lhs, rhs in
                    let lhsApple = appleEvidence.directStrength(for: lhs.candidate)
                    let rhsApple = appleEvidence.directStrength(for: rhs.candidate)
                    if lhsApple != rhsApple {
                        return lhsApple > rhsApple
                    }
                    return canonicalRecognitionSort(lhs, rhs)
                }
        }

        func recognitionArtists(archetypeID: String, tiers: [String]) -> [AlphaScoredSurveyCandidate] {
            artistScored
                .filter {
                    $0.candidate.archetypeIDs.contains(archetypeID) &&
                        !$0.candidate.isFalseNearby &&
                        tiers.contains($0.candidate.recognitionTier)
                }
                .sorted { lhs, rhs in
                    if lhs.candidate.priorityScore != rhs.candidate.priorityScore {
                        return lhs.candidate.priorityScore > rhs.candidate.priorityScore
                    }
                    let lhsApple = appleEvidence.directStrength(for: lhs.candidate)
                    let rhsApple = appleEvidence.directStrength(for: rhs.candidate)
                    if lhsApple != rhsApple {
                        return lhsApple > rhsApple
                    }
                    return lhs.candidate.displayKey < rhs.candidate.displayKey
                }
        }

        func fallbackArtists(archetypeID: String) -> [AlphaScoredSurveyCandidate] {
            artistScored
                .filter {
                    $0.candidate.archetypeIDs.contains(archetypeID) &&
                        !$0.candidate.isFalseNearby
                }
                .sorted { lhs, rhs in
                    let lhsApple = appleEvidence.directStrength(for: lhs.candidate)
                    let rhsApple = appleEvidence.directStrength(for: rhs.candidate)
                    if lhsApple != rhsApple {
                        return lhsApple > rhsApple
                    }
                    return canonicalRecognitionSort(lhs, rhs)
                }
        }

        func slotCandidates(archetypeID: String, slotIndex: Int) -> [AlphaScoredSurveyCandidate] {
            switch slotIndex {
            case 0:
                return topArtistCandidates(archetypeID: archetypeID) + fallbackArtists(archetypeID: archetypeID)
            case 1:
                return recognitionArtists(archetypeID: archetypeID, tiers: ["high"]) +
                    recognitionArtists(archetypeID: archetypeID, tiers: ["mass"]) +
                    recognitionArtists(archetypeID: archetypeID, tiers: ["low"]) +
                    recognitionArtists(archetypeID: archetypeID, tiers: ["cult"])
            default:
                return recognitionArtists(archetypeID: archetypeID, tiers: ["medium"]) +
                    recognitionArtists(archetypeID: archetypeID, tiers: ["high"]) +
                    recognitionArtists(archetypeID: archetypeID, tiers: ["mass"]) +
                    recognitionArtists(archetypeID: archetypeID, tiers: ["low"]) +
                    recognitionArtists(archetypeID: archetypeID, tiers: ["cult"])
            }
        }

        func appendSlot(archetypeID: String, slotIndex: Int) -> Bool {
            appendFirst(slotCandidates(archetypeID: archetypeID, slotIndex: slotIndex))
        }

        let directArtistGuarantees = artistScored
            .filter {
                appleEvidence.directStrength(for: $0.candidate) > 0
            }
            .sorted { lhs, rhs in
                let lhsApple = appleEvidence.directStrength(for: lhs.candidate)
                let rhsApple = appleEvidence.directStrength(for: rhs.candidate)
                if lhsApple != rhsApple {
                    return lhsApple > rhsApple
                }
                return canonicalRecognitionSort(lhs, rhs)
            }
            .prefix(10)
        for candidate in directArtistGuarantees {
            _ = appendFirst([candidate])
        }

        var fallbackIndex = 8
        for archetypeID in archetypeIDs.prefix(8) {
            for slotIndex in 0..<3 {
                if appendSlot(archetypeID: archetypeID, slotIndex: slotIndex) {
                    continue
                }
                while fallbackIndex < archetypeIDs.count {
                    let fallbackArchetypeID = archetypeIDs[fallbackIndex]
                    fallbackIndex += 1
                    if appendSlot(archetypeID: fallbackArchetypeID, slotIndex: slotIndex) {
                        break
                    }
                }
            }
        }

        if result.count < 24 {
            let topFamilyIDs = Set(appleEvidence.topFamilyIDs)
            let familyFallback = artistScored
                .filter {
                    !$0.candidate.isFalseNearby &&
                        !$0.candidate.familyIDs.isDisjoint(with: topFamilyIDs)
                }
                .sorted { lhs, rhs in
                    let lhsFamilyRank = lhs.candidate.familyIDs.map { appleEvidence.stableFamilyRank($0) }.min() ?? Int.max
                    let rhsFamilyRank = rhs.candidate.familyIDs.map { appleEvidence.stableFamilyRank($0) }.min() ?? Int.max
                    if lhsFamilyRank != rhsFamilyRank {
                        return lhsFamilyRank < rhsFamilyRank
                    }
                    return canonicalRecognitionSort(lhs, rhs)
                }
            for scored in familyFallback where result.count < 24 {
                if usedItemIDs.insert(scored.candidate.itemID).inserted {
                    result.append(scored)
                }
            }
        }

        if result.count < 24 {
            for scored in stableShuffle(
                artistScored.filter { !$0.candidate.isFalseNearby },
                seed: "artist-intro-sparse-fallback-v0-3"
            ) where result.count < 24 {
                if usedItemIDs.insert(scored.candidate.itemID).inserted {
                    result.append(scored)
                }
            }
        }

        return stableShuffle(result.prefix(24).map { $0 }, seed: "artist-intro-policy-v0-3")
    }

    private func artistFollowupPolicyBatch(
        scored: [AlphaScoredSurveyCandidate],
        responses: [String: SurveyResponse],
        displayedPages: [String: SurveyGridPage]
    ) -> [AlphaScoredSurveyCandidate] {
        let artistScored = scored.filter { $0.candidate.kind == .artist }
        let archetypeIDs = appleEvidence.topArchetypeIDs
        guard !artistScored.isEmpty, !archetypeIDs.isEmpty else {
            return []
        }

        var result = [AlphaScoredSurveyCandidate]()
        var usedItemIDs = Set<String>()

        func appendFirst(_ candidates: [AlphaScoredSurveyCandidate]) -> Bool {
            for scored in candidates where usedItemIDs.insert(scored.candidate.itemID).inserted {
                result.append(scored)
                return true
            }
            return false
        }

        func topPayloadArtists(archetypeID: String) -> [AlphaScoredSurveyCandidate] {
            artistScored
                .filter {
                    $0.candidate.archetypeIDs.contains(archetypeID) &&
                        appleEvidence.directStrength(for: $0.candidate) > 0
                }
                .sorted { lhs, rhs in
                    let lhsApple = appleEvidence.directStrength(for: lhs.candidate)
                    let rhsApple = appleEvidence.directStrength(for: rhs.candidate)
                    if lhsApple != rhsApple {
                        return lhsApple > rhsApple
                    }
                    return canonicalRecognitionSort(lhs, rhs)
                }
        }

        for archetypeID in archetypeIDs.dropFirst(8).prefix(6) {
            var addedForArchetype = 0
            for candidate in topPayloadArtists(archetypeID: archetypeID) where addedForArchetype < 2 && result.count < 12 {
                guard usedItemIDs.insert(candidate.candidate.itemID).inserted else {
                    continue
                }
                result.append(candidate)
                addedForArchetype += 1
            }
        }

        var fallbackIndex = 14
        while result.count < 12 && fallbackIndex < archetypeIDs.count {
            let fallbackArchetypeID = archetypeIDs[fallbackIndex]
            fallbackIndex += 1
            _ = appendFirst(topPayloadArtists(archetypeID: fallbackArchetypeID))
        }

        let rankedArchetypeSet = Set(archetypeIDs.prefix(20))
        let multiCanonical = artistScored
            .filter {
                !$0.candidate.isFalseNearby &&
                    $0.candidate.archetypeIDs.count > 1 &&
                    !$0.candidate.archetypeIDs.isDisjoint(with: rankedArchetypeSet)
            }
            .sorted { lhs, rhs in
                if lhs.candidate.archetypeIDs.count != rhs.candidate.archetypeIDs.count {
                    return lhs.candidate.archetypeIDs.count > rhs.candidate.archetypeIDs.count
                }
                return canonicalRecognitionSort(lhs, rhs)
            }
        for candidate in multiCanonical where result.count < 18 {
            if usedItemIDs.insert(candidate.candidate.itemID).inserted {
                result.append(candidate)
            }
        }

        if result.count < 18 {
            for candidate in artistScored.sorted(by: canonicalRecognitionSort) where result.count < 18 {
                guard !candidate.candidate.isFalseNearby,
                      !candidate.candidate.archetypeIDs.isDisjoint(with: rankedArchetypeSet),
                      usedItemIDs.insert(candidate.candidate.itemID).inserted else {
                    continue
                }
                result.append(candidate)
            }
        }

        let introScores = archetypeSurveyScores(
            responses: responsesForDisplayedPages(
                [.artistPage1, .artistPage2],
                responses: responses,
                displayedPages: displayedPages
            )
        )
        let lowestIntroArchetypes = Array(archetypeIDs.prefix(8))
            .sorted { lhs, rhs in
                let lhsScore = introScores[lhs] ?? 0
                let rhsScore = introScores[rhs] ?? 0
                if lhsScore != rhsScore {
                    return lhsScore < rhsScore
                }
                return originalArchetypeRank(lhs) < originalArchetypeRank(rhs)
            }
            .prefix(6)

        for archetypeID in lowestIntroArchetypes where result.count < 24 {
            let candidates = artistScored
                .filter {
                    !$0.candidate.isFalseNearby &&
                        $0.candidate.archetypeIDs.contains(archetypeID)
                }
                .sorted { lhs, rhs in
                    if lhs.candidate.archetypeIDs.count != rhs.candidate.archetypeIDs.count {
                        return lhs.candidate.archetypeIDs.count > rhs.candidate.archetypeIDs.count
                    }
                    return canonicalRecognitionSort(lhs, rhs)
                }
            _ = appendFirst(candidates)
        }

        if result.count < 24 {
            let topIntroSet = Set(archetypeIDs.prefix(8))
            for candidate in artistScored.sorted(by: canonicalRecognitionSort) where result.count < 24 {
                guard !candidate.candidate.isFalseNearby,
                      !candidate.candidate.archetypeIDs.isDisjoint(with: topIntroSet),
                      usedItemIDs.insert(candidate.candidate.itemID).inserted else {
                    continue
                }
                result.append(candidate)
            }
        }

        return stableShuffle(result.prefix(24).map { $0 }, seed: "artist-followup-policy-v0-3")
    }

    private func albumPolicyBatch(
        scored: [AlphaScoredSurveyCandidate],
        responses: [String: SurveyResponse],
        displayedPages: [String: SurveyGridPage]
    ) -> [AlphaScoredSurveyCandidate] {
        let albumScored = scored.filter { $0.candidate.kind == .album }
        guard !albumScored.isEmpty else {
            return []
        }

        let positiveArtists = positiveArtistCandidates(responses: responses)
        let positiveArtistKeys = Set(positiveArtists.flatMap { Array($0.artistNames) + [$0.displayKey] })
        let rankedArchetypes = rankedArchetypeIDs(responses: responses, displayedPages: displayedPages)
        let topEightArchetypes = Set(rankedArchetypes.prefix(8))
        var result = [AlphaScoredSurveyCandidate]()
        var usedItemIDs = Set<String>()

        func appendUnique(_ candidates: [AlphaScoredSurveyCandidate], limit: Int) {
            guard limit > 0 else {
                return
            }
            var added = 0
            for candidate in candidates where result.count < 24 && added < limit {
                guard usedItemIDs.insert(candidate.candidate.itemID).inserted else {
                    continue
                }
                result.append(candidate)
                added += 1
            }
        }

        let directAppleAlbums = albumScored
            .filter { appleEvidence.topDirectStrength(for: $0.candidate) > 0 }
            .sorted { lhs, rhs in
                let lhsStrength = appleEvidence.topDirectStrength(for: lhs.candidate)
                let rhsStrength = appleEvidence.topDirectStrength(for: rhs.candidate)
                if lhsStrength != rhsStrength {
                    return lhsStrength > rhsStrength
                }
                return canonicalRecognitionSort(lhs, rhs)
            }
        appendUnique(directAppleAlbums, limit: 6)

        let positiveAlbums = albumScored
            .filter { !$0.candidate.artistNames.isDisjoint(with: positiveArtistKeys) }
            .sorted { lhs, rhs in
                let lhsArtistScore = positiveArtistScore(for: lhs.candidate, responses: responses)
                let rhsArtistScore = positiveArtistScore(for: rhs.candidate, responses: responses)
                if lhsArtistScore != rhsArtistScore {
                    return lhsArtistScore > rhsArtistScore
                }
                return canonicalRecognitionSort(lhs, rhs)
            }

        let multiArtists = positiveArtists
            .filter { $0.archetypeIDs.count > 1 }
            .sorted { lhs, rhs in
                let lhsScore = responseScore(for: responses[lhs.itemID]?.state, kind: .artist)
                let rhsScore = responseScore(for: responses[rhs.itemID]?.state, kind: .artist)
                if lhsScore != rhsScore {
                    return lhsScore > rhsScore
                }
                return lhs.displayKey < rhs.displayKey
            }
        var usedArtistArchetypePairs = Set<String>()
        var multiArtistAlbums = [AlphaScoredSurveyCandidate]()
        for artist in multiArtists {
            for album in positiveAlbums where !album.candidate.artistNames.isDisjoint(with: artist.artistNames.union([artist.displayKey])) {
                guard let albumArchetype = album.candidate.archetypeIDs
                    .sorted(by: archetypeRankSort)
                    .first else {
                    continue
                }
                let pairKey = "\(artist.displayKey)::\(albumArchetype)"
                guard usedArtistArchetypePairs.insert(pairKey).inserted,
                      !multiArtistAlbums.contains(where: { $0.candidate.itemID == album.candidate.itemID }) else {
                    continue
                }
                multiArtistAlbums.append(album)
                if multiArtistAlbums.count >= 8 {
                    break
                }
            }
            if multiArtistAlbums.count >= 8 {
                break
            }
        }
        appendUnique(multiArtistAlbums, limit: 8)

        let highRecognitionTopArchetypeAlbums = albumScored
            .filter {
                !$0.candidate.archetypeIDs.isDisjoint(with: topEightArchetypes) &&
                    ["mass", "high"].contains($0.candidate.recognitionTier)
            }
            .sorted { lhs, rhs in
                let lhsRank = bestArchetypeRank(for: lhs.candidate, in: rankedArchetypes)
                let rhsRank = bestArchetypeRank(for: rhs.candidate, in: rankedArchetypes)
                if lhsRank != rhsRank {
                    return lhsRank < rhsRank
                }
                return canonicalRecognitionSort(lhs, rhs)
            }
        appendUnique(highRecognitionTopArchetypeAlbums, limit: 24 - result.count)
        appendUnique(positiveAlbums, limit: 24 - result.count)

        if result.count < 24 {
            let fallback = albumScored.sorted { lhs, rhs in
                let lhsRank = bestArchetypeRank(for: lhs.candidate, in: rankedArchetypes)
                let rhsRank = bestArchetypeRank(for: rhs.candidate, in: rankedArchetypes)
                if lhsRank != rhsRank {
                    return lhsRank < rhsRank
                }
                return canonicalRecognitionSort(lhs, rhs)
            }
            appendUnique(fallback, limit: 24 - result.count)
        }

        let cappedResult = result.prefix(24).map { $0 }
        let directAlbums = cappedResult
            .filter { appleEvidence.topDirectStrength(for: $0.candidate) > 0 }
            .sorted { lhs, rhs in
                let lhsStrength = appleEvidence.topDirectStrength(for: lhs.candidate)
                let rhsStrength = appleEvidence.topDirectStrength(for: rhs.candidate)
                if lhsStrength != rhsStrength {
                    return lhsStrength > rhsStrength
                }
                return canonicalRecognitionSort(lhs, rhs)
            }
        let indirectAlbums = stableShuffle(
            cappedResult.filter { appleEvidence.topDirectStrength(for: $0.candidate) <= 0 },
            seed: "album-policy-v0-3"
        )
        return directAlbums + indirectAlbums
    }

    private func songPolicyPage(
        descriptor: AlphaSurveyStepDescriptor,
        scored: [AlphaScoredSurveyCandidate],
        baseScored: [AlphaScoredSurveyCandidate],
        responses: [String: SurveyResponse],
        displayedPages: [String: SurveyGridPage],
        priorCandidates: AlphaPriorVisibleCandidates
    ) -> [AlphaScoredSurveyCandidate] {
        let songScored = scored.filter { $0.candidate.kind == .song }
        guard !songScored.isEmpty else {
            return []
        }

        let rankedArchetypes = rankedArchetypeIDs(responses: responses, displayedPages: displayedPages)
        let allowedPrefix: Int
        switch descriptor.pageNumber {
        case 1:
            allowedPrefix = 8
        case 2:
            allowedPrefix = 12
        default:
            allowedPrefix = 20
        }
        let allowedArchetypes = Set(rankedArchetypes.prefix(allowedPrefix))
        let tagScores = rankedAffinityTagScores(from: baseScored)
        let blockedPageThreeArchetypes: Set<String>
        if descriptor.pageNumber == 3 {
            let displayedEarlySongArchetypes = displayedCandidates(
                for: [.songPage1, .songPage2],
                displayedPages: displayedPages
            )
            let earlyIDs = displayedEarlySongArchetypes.itemIDs.isEmpty
                ? priorCandidates.itemIDs
                : displayedEarlySongArchetypes.itemIDs
            blockedPageThreeArchetypes = Set(earlyIDs.compactMap { candidatesByItemID[$0] }.flatMap(\.archetypeIDs))
        } else {
            blockedPageThreeArchetypes = []
        }

        var selected = [AlphaScoredSurveyCandidate]()
        var usedItemIDs = Set<String>()
        var usedDisplayKeys = Set<String>()
        var repetitionGovernor = AlphaSurveyRepetitionGovernor(
            kind: descriptor.kind,
            priorCandidates: priorCandidates,
            candidatesByItemID: candidatesByItemID
        )

        func allowed(_ candidate: AlphaSurveyRuntimeCandidate, tiers: Set<String>?) -> Bool {
            guard !candidate.archetypeIDs.isDisjoint(with: allowedArchetypes),
                  usedItemIDs.contains(candidate.itemID) == false,
                  usedDisplayKeys.contains(candidate.displayKey) == false,
                  repetitionGovernor.canAdd(candidate) else {
                return false
            }
            if descriptor.pageNumber == 3,
               !candidate.archetypeIDs.isDisjoint(with: blockedPageThreeArchetypes) {
                return false
            }
            if let tiers {
                return tiers.contains(candidate.recognitionTier)
            }
            return true
        }

        func appendUnique(_ candidates: [AlphaScoredSurveyCandidate], targetCount: Int) {
            for scored in candidates where selected.count < targetCount {
                let candidate = scored.candidate
                guard !usedItemIDs.contains(candidate.itemID),
                      !usedDisplayKeys.contains(candidate.displayKey),
                      repetitionGovernor.canAdd(candidate) else {
                    continue
                }
                usedItemIDs.insert(candidate.itemID)
                usedDisplayKeys.insert(candidate.displayKey)
                selected.append(scored)
                repetitionGovernor.record(candidate)
            }
        }

        let tierPasses: [Set<String>?] = descriptor.pageNumber == 3
            ? [Set(["mass", "high"]), Set(["medium"]), Set(["low"]), Set(["cult", "unknown"]), nil]
            : [nil]

        for tiers in tierPasses where selected.count < 6 {
            let directSongs = songScored
                .filter {
                    appleEvidence.topDirectStrength(for: $0.candidate) > 0 &&
                        allowed($0.candidate, tiers: tiers)
                }
                .sorted { lhs, rhs in
                    let lhsApple = appleEvidence.topDirectStrength(for: lhs.candidate)
                    let rhsApple = appleEvidence.topDirectStrength(for: rhs.candidate)
                    if lhsApple != rhsApple {
                        return lhsApple > rhsApple
                    }
                    return canonicalRecognitionSort(lhs, rhs)
                }
            appendUnique(directSongs, targetCount: 6)
        }

        for tiers in tierPasses where selected.count < 12 {
            let tagSongs = songScored
                .filter {
                    allowed($0.candidate, tiers: tiers) &&
                        affinityTagScore(for: $0.candidate, tagScores: tagScores) > 0
                }
                .sorted { lhs, rhs in
                    let lhsTag = affinityTagScore(for: lhs.candidate, tagScores: tagScores)
                    let rhsTag = affinityTagScore(for: rhs.candidate, tagScores: tagScores)
                    if lhsTag != rhsTag {
                        return lhsTag > rhsTag
                    }
                    return canonicalRecognitionSort(lhs, rhs)
                }
            appendUnique(tagSongs, targetCount: 12)
        }

        if selected.count < SurveyFixtureLibrary.gridPageItemLimit {
            let fallback = songScored
                .filter { allowed($0.candidate, tiers: nil) }
                .sorted(by: canonicalRecognitionSort)
            appendUnique(fallback, targetCount: SurveyFixtureLibrary.gridPageItemLimit)
        }

        return selected
    }

    private func rankedArchetypeIDs(
        responses: [String: SurveyResponse],
        displayedPages: [String: SurveyGridPage]
    ) -> [String] {
        let scores = archetypeSurveyScores(responses: responses)
        var ids = Set(appleEvidence.topArchetypeIDs)
        for response in responses.values {
            if let candidate = candidatesByItemID[response.itemID] {
                ids.formUnion(candidate.archetypeIDs)
            }
        }
        if ids.isEmpty {
            ids.formUnion((candidatesByKind[.artist] ?? []).flatMap(\.archetypeIDs))
        }
        return ids.sorted { lhs, rhs in
            let lhsScore = scores[lhs] ?? 0
            let rhsScore = scores[rhs] ?? 0
            if lhsScore != rhsScore {
                return lhsScore > rhsScore
            }
            return archetypeRankSort(lhs, rhs)
        }
    }

    private func archetypeSurveyScores(responses: [String: SurveyResponse]) -> [String: Double] {
        responses.values.reduce(into: [String: Double]()) { result, response in
            guard let candidate = candidatesByItemID[response.itemID] else {
                return
            }
            let score = responseScore(for: response.state, kind: candidate.kind)
            guard score != 0 else {
                return
            }
            for archetypeID in candidate.archetypeIDs {
                result[archetypeID, default: 0] += score
            }
        }
    }

    private func responsesForDisplayedPages(
        _ steps: [SurveyStep],
        responses: [String: SurveyResponse],
        displayedPages: [String: SurveyGridPage]
    ) -> [String: SurveyResponse] {
        let ids = Set(steps.flatMap { step in
            displayedPages[step.rawValue]?.items.map(\.id) ?? []
        })
        guard !ids.isEmpty else {
            return responses.filter { candidatesByItemID[$0.key]?.kind == .artist }
        }
        return responses.filter { ids.contains($0.key) }
    }

    private func displayedCandidates(
        for steps: [SurveyStep],
        displayedPages: [String: SurveyGridPage]
    ) -> AlphaPriorVisibleCandidates {
        var prior = AlphaPriorVisibleCandidates()
        for step in steps {
            guard let page = displayedPages[step.rawValue] else {
                continue
            }
            prior.itemIDs.formUnion(page.items.map(\.id))
            prior.displayKeys.formUnion(page.items.map(displayKey(for:)))
        }
        return prior
    }

    private func positiveArtistCandidates(responses: [String: SurveyResponse]) -> [AlphaSurveyRuntimeCandidate] {
        responses.values.compactMap { response in
            guard response.itemKind == .artist,
                  [.favorite, .like, .fine].contains(response.state),
                  let candidate = candidatesByItemID[response.itemID] else {
                return nil
            }
            return candidate
        }
    }

    private func positiveArtistScore(
        for candidate: AlphaSurveyRuntimeCandidate,
        responses: [String: SurveyResponse]
    ) -> Double {
        responses.values.compactMap { response -> Double? in
            guard response.itemKind == .artist,
                  let source = candidatesByItemID[response.itemID],
                  !candidate.artistNames.isDisjoint(with: source.artistNames.union([source.displayKey])) else {
                return nil
            }
            return max(0, responseScore(for: response.state, kind: .artist))
        }
        .max() ?? 0
    }

    private func responseScore(for state: SurveySignalState?, kind: SurveyItemKind) -> Double {
        guard let state else {
            return 0
        }
        let fullScore: Double
        switch state {
        case .favorite:
            fullScore = 4
        case .like:
            fullScore = 3
        case .fine:
            fullScore = 1
        case .dontKnow:
            fullScore = 0
        case .notForMe:
            fullScore = -2
        }
        return kind == .song ? fullScore * 0.5 : fullScore
    }

    private func rankedAffinityTagScores(from scored: [AlphaScoredSurveyCandidate]) -> [String: Double] {
        let topSongs = scored
            .filter {
                $0.candidate.kind == .song &&
                    appleEvidence.topDirectStrength(for: $0.candidate) > 0
            }
            .sorted { lhs, rhs in
                let lhsApple = appleEvidence.topDirectStrength(for: lhs.candidate)
                let rhsApple = appleEvidence.topDirectStrength(for: rhs.candidate)
                if lhsApple != rhsApple {
                    return lhsApple > rhsApple
                }
                return lhs.candidate.displayKey < rhs.candidate.displayKey
            }
            .prefix(50)

        let tagCounts = topSongs.reduce(into: [String: Int]()) { result, scored in
            for tag in scored.candidate.affinityTags where isSurveyAffinityTag(tag) {
                result[tag, default: 0] += 1
            }
        }
        let rankedTags = tagCounts.sorted {
            if $0.value != $1.value {
                return $0.value > $1.value
            }
            return $0.key < $1.key
        }
        var result = [String: Double]()
        for (index, pair) in rankedTags.prefix(10).enumerated() {
            switch index {
            case 0, 1:
                result[pair.key] = 8
            case 2, 3:
                result[pair.key] = 6
            case 4, 5:
                result[pair.key] = 4
            default:
                result[pair.key] = 3
            }
        }
        return result
    }

    private func isSurveyAffinityTag(_ tag: String) -> Bool {
        let prefix = tag.split(separator: ":").first.map(String.init) ?? ""
        let allowedPrefixes: Set<String> = [
            "emotion_theme",
            "form_container",
            "lyric_theme",
            "lyrical_theme",
            "rhythm_body",
            "sonic_texture",
            "vocal_performance"
        ]
        guard allowedPrefixes.contains(prefix) else {
            return false
        }
        let lowered = tag.lowercased()
        return !lowered.contains("risk") &&
            !lowered.contains("safety") &&
            !lowered.contains("quarantine")
    }

    private func affinityTagScore(
        for candidate: AlphaSurveyRuntimeCandidate,
        tagScores: [String: Double]
    ) -> Double {
        candidate.affinityTags.reduce(0) { $0 + (tagScores[$1] ?? 0) }
    }

    private func stableShuffle(
        _ candidates: [AlphaScoredSurveyCandidate],
        seed: String
    ) -> [AlphaScoredSurveyCandidate] {
        candidates.sorted { lhs, rhs in
            let lhsRank = appleEvidence.stableSelectionRank("\(seed)::\(lhs.candidate.itemID)")
            let rhsRank = appleEvidence.stableSelectionRank("\(seed)::\(rhs.candidate.itemID)")
            if lhsRank != rhsRank {
                return lhsRank < rhsRank
            }
            return lhs < rhs
        }
    }

    private func canonicalRecognitionSort(
        _ lhs: AlphaScoredSurveyCandidate,
        _ rhs: AlphaScoredSurveyCandidate
    ) -> Bool {
        let lhsRecognition = recognitionRank(lhs.candidate.recognitionTier)
        let rhsRecognition = recognitionRank(rhs.candidate.recognitionTier)
        if lhsRecognition != rhsRecognition {
            return lhsRecognition > rhsRecognition
        }
        if lhs.candidate.priorityScore != rhs.candidate.priorityScore {
            return lhs.candidate.priorityScore > rhs.candidate.priorityScore
        }
        let lhsApple = appleEvidence.directStrength(for: lhs.candidate)
        let rhsApple = appleEvidence.directStrength(for: rhs.candidate)
        if lhsApple != rhsApple {
            return lhsApple > rhsApple
        }
        return lhs.candidate.displayKey < rhs.candidate.displayKey
    }

    private func bestArchetypeRank(
        for candidate: AlphaSurveyRuntimeCandidate,
        in rankedArchetypes: [String]
    ) -> Int {
        candidate.archetypeIDs
            .map { rankedArchetypes.firstIndex(of: $0) ?? originalArchetypeRank($0) }
            .min() ?? Int.max
    }

    private func archetypeRankSort(_ lhs: String, _ rhs: String) -> Bool {
        let lhsRank = originalArchetypeRank(lhs)
        let rhsRank = originalArchetypeRank(rhs)
        if lhsRank != rhsRank {
            return lhsRank < rhsRank
        }
        return lhs < rhs
    }

    private func originalArchetypeRank(_ archetypeID: String) -> Int {
        appleEvidence.topArchetypeIDs.firstIndex(of: archetypeID) ?? Int.max
    }

    private func recognitionRank(_ tier: String) -> Int {
        switch tier {
        case "mass":
            return 5
        case "high":
            return 4
        case "medium":
            return 3
        case "low":
            return 2
        case "cult":
            return 1
        default:
            return 0
        }
    }

    private func reservedCandidates(
        for descriptor: AlphaSurveyStepDescriptor,
        scored: [AlphaScoredSurveyCandidate]
    ) -> [AlphaScoredSurveyCandidate] {
        guard appleEvidence.hasUsableSignals else {
            return []
        }

        var result: [AlphaScoredSurveyCandidate] = []
        var usedItemIDs = Set<String>()

        @discardableResult
        func appendUnique(_ candidates: [AlphaScoredSurveyCandidate], limit: Int) -> Int {
            guard limit > 0 else {
                return 0
            }
            var added = 0
            for candidate in candidates where result.count < SurveyFixtureLibrary.gridPageItemLimit {
                guard usedItemIDs.insert(candidate.candidate.itemID).inserted else {
                    continue
                }
                result.append(candidate)
                added += 1
                if added >= limit {
                    break
                }
            }
            return added
        }

        func topDirect(kind: SurveyItemKind, limit: Int) -> [AlphaScoredSurveyCandidate] {
            scored
                .filter {
                    $0.candidate.kind == kind &&
                        appleEvidence.topDirectStrength(for: $0.candidate) > 0
                }
                .sorted { lhs, rhs in
                    let lhsStrength = appleEvidence.topDirectStrength(for: lhs.candidate)
                    let rhsStrength = appleEvidence.topDirectStrength(for: rhs.candidate)
                    if lhsStrength != rhsStrength {
                        return lhsStrength > rhsStrength
                    }
                    return lhs < rhs
                }
                .prefix(limit)
                .map { $0 }
        }

        func recognitionArtists(archetypeID: String, tiers: [String], limit: Int) -> [AlphaScoredSurveyCandidate] {
            scored
                .filter {
                    $0.candidate.kind == .artist &&
                        $0.candidate.archetypeIDs.contains(archetypeID) &&
                        !$0.candidate.isFalseNearby &&
                        tiers.contains($0.candidate.recognitionTier)
                }
                .sorted {
                    let lhsApple = appleEvidence.directStrength(for: $0.candidate)
                    let rhsApple = appleEvidence.directStrength(for: $1.candidate)
                    if $0.candidate.priorityScore != $1.candidate.priorityScore {
                        return $0.candidate.priorityScore > $1.candidate.priorityScore
                    }
                    if lhsApple != rhsApple {
                        return lhsApple > rhsApple
                    }
                    return $0.candidate.displayKey < $1.candidate.displayKey
                }
                .prefix(limit)
                .map { $0 }
        }

        func recognitionArtists(familyID: Int, limit: Int) -> [AlphaScoredSurveyCandidate] {
            scored
                .filter {
                    $0.candidate.kind == .artist &&
                        $0.candidate.familyIDs.contains(familyID) &&
                        !$0.candidate.isFalseNearby &&
                        $0.candidate.isTopRecognitionTier
                }
                .sorted {
                    if $0.candidate.priorityScore != $1.candidate.priorityScore {
                        return $0.candidate.priorityScore > $1.candidate.priorityScore
                    }
                    return $0.candidate.displayKey < $1.candidate.displayKey
                }
                .prefix(limit)
                .map { $0 }
        }

        func archetypeOneFamilyRecognitionArtists(limit: Int) -> [AlphaScoredSurveyCandidate] {
            guard let archetypeID = appleEvidence.topArchetypeIDs.first else {
                return stableRecognitionFamilyMix(limit: limit)
            }
            let familyIDs = Set(scored.flatMap { scoredCandidate -> [Int] in
                let candidate = scoredCandidate.candidate
                guard candidate.kind == .artist,
                      candidate.archetypeIDs.contains(archetypeID) else {
                    return []
                }
                return Array(candidate.familyIDs)
            })
                .sorted {
                    let lhsIndex = appleEvidence.topFamilyIDs.firstIndex(of: $0) ?? Int.max
                    let rhsIndex = appleEvidence.topFamilyIDs.firstIndex(of: $1) ?? Int.max
                    if lhsIndex != rhsIndex {
                        return lhsIndex < rhsIndex
                    }
                    let lhsRank = appleEvidence.stableFamilyRank($0)
                    let rhsRank = appleEvidence.stableFamilyRank($1)
                    if lhsRank != rhsRank {
                        return lhsRank < rhsRank
                    }
                    return $0 < $1
                }
            let candidates = familyIDs.flatMap {
                recognitionArtists(familyID: $0, limit: SurveyFixtureLibrary.gridPageItemLimit)
            }
            if !candidates.isEmpty {
                return candidates
            }
            let archetypeCandidates = recognitionArtists(
                archetypeID: archetypeID,
                tiers: ["mass", "high"],
                limit: SurveyFixtureLibrary.gridPageItemLimit,
            )
            return archetypeCandidates.isEmpty ? stableRecognitionFamilyMix(limit: limit) : archetypeCandidates
        }

        func stableRecognitionFamilyMix(limit: Int) -> [AlphaScoredSurveyCandidate] {
            let familyIDs = Set(scored.flatMap { $0.candidate.kind == .artist ? $0.candidate.familyIDs : [] })
                .sorted {
                    let lhs = appleEvidence.stableFamilyRank($0)
                    let rhs = appleEvidence.stableFamilyRank($1)
                    if lhs != rhs {
                        return lhs < rhs
                    }
                    return $0 < $1
                }
            var candidates: [AlphaScoredSurveyCandidate] = []
            for familyID in familyIDs {
                candidates.append(contentsOf: recognitionArtists(familyID: familyID, limit: 1))
                if candidates.count >= limit {
                    break
                }
            }
            if candidates.count < limit {
                let fallbackArtists = scored
                    .filter { $0.candidate.kind == .artist }
                .sorted {
                    if $0.candidate.isTopRecognitionTier != $1.candidate.isTopRecognitionTier {
                        return $0.candidate.isTopRecognitionTier
                    }
                    if $0.candidate.priorityScore != $1.candidate.priorityScore {
                        return $0.candidate.priorityScore > $1.candidate.priorityScore
                        }
                        return $0.candidate.displayKey < $1.candidate.displayKey
                    }
                candidates.append(contentsOf: fallbackArtists)
            }
            return candidates
        }

        func topologySongCandidates(archetypeID: String? = nil, topFamilyOnly: Bool = false, limit: Int) -> [AlphaScoredSurveyCandidate] {
            let topFamilyID = appleEvidence.topFamilyIDs.first
            return scored
                .filter { scoredCandidate in
                    let candidate = scoredCandidate.candidate
                    guard candidate.kind == .song,
                          appleEvidence.topologySongScore(for: candidate) > 0 else {
                        return false
                    }
                    if let archetypeID {
                        return candidate.archetypeIDs.contains(archetypeID)
                    }
                    if topFamilyOnly, let topFamilyID {
                        return candidate.familyIDs.contains(topFamilyID)
                    }
                    return true
                }
                .sorted { lhs, rhs in
                    let lhsStrength = appleEvidence.topologySongScore(for: lhs.candidate)
                    let rhsStrength = appleEvidence.topologySongScore(for: rhs.candidate)
                    if lhsStrength != rhsStrength {
                        return lhsStrength > rhsStrength
                    }
                    return lhs < rhs
                }
                .prefix(limit)
                .map { $0 }
        }

        func topArtistCandidates(archetypeID: String, limit: Int) -> [AlphaScoredSurveyCandidate] {
            scored
                .filter {
                    $0.candidate.kind == .artist &&
                        $0.candidate.archetypeIDs.contains(archetypeID) &&
                        appleEvidence.directStrength(for: $0.candidate) > 0
                }
                .sorted {
                    let lhsApple = appleEvidence.directStrength(for: $0.candidate)
                    let rhsApple = appleEvidence.directStrength(for: $1.candidate)
                    if lhsApple != rhsApple {
                        return lhsApple > rhsApple
                    }
                    if $0.candidate.priorityScore != $1.candidate.priorityScore {
                        return $0.candidate.priorityScore > $1.candidate.priorityScore
                    }
                    return $0.candidate.displayKey < $1.candidate.displayKey
                }
                .prefix(limit)
                .map { $0 }
        }

        func fallbackArtists(archetypeID: String, limit: Int) -> [AlphaScoredSurveyCandidate] {
            scored
                .filter {
                    $0.candidate.kind == .artist &&
                        $0.candidate.archetypeIDs.contains(archetypeID) &&
                        !$0.candidate.isFalseNearby
                }
                .sorted {
                    let lhsApple = appleEvidence.directStrength(for: $0.candidate)
                    let rhsApple = appleEvidence.directStrength(for: $1.candidate)
                    if lhsApple != rhsApple {
                        return lhsApple > rhsApple
                    }
                    if $0.candidate.priorityScore != $1.candidate.priorityScore {
                        return $0.candidate.priorityScore > $1.candidate.priorityScore
                    }
                    return $0.candidate.displayKey < $1.candidate.displayKey
                }
                .prefix(limit)
                .map { $0 }
        }

        func artistSlotCandidates(archetypeID: String, slotIndex: Int) -> [AlphaScoredSurveyCandidate] {
            switch slotIndex {
            case 0:
                return topArtistCandidates(archetypeID: archetypeID, limit: SurveyFixtureLibrary.gridPageItemLimit) +
                    fallbackArtists(archetypeID: archetypeID, limit: SurveyFixtureLibrary.gridPageItemLimit)
            case 1:
                return recognitionArtists(archetypeID: archetypeID, tiers: ["high"], limit: SurveyFixtureLibrary.gridPageItemLimit) +
                    recognitionArtists(archetypeID: archetypeID, tiers: ["mass"], limit: SurveyFixtureLibrary.gridPageItemLimit) +
                    recognitionArtists(archetypeID: archetypeID, tiers: ["low"], limit: SurveyFixtureLibrary.gridPageItemLimit) +
                    recognitionArtists(archetypeID: archetypeID, tiers: ["cult"], limit: SurveyFixtureLibrary.gridPageItemLimit)
            default:
                return recognitionArtists(archetypeID: archetypeID, tiers: ["medium"], limit: SurveyFixtureLibrary.gridPageItemLimit) +
                    recognitionArtists(archetypeID: archetypeID, tiers: ["high"], limit: SurveyFixtureLibrary.gridPageItemLimit) +
                    recognitionArtists(archetypeID: archetypeID, tiers: ["mass"], limit: SurveyFixtureLibrary.gridPageItemLimit) +
                    recognitionArtists(archetypeID: archetypeID, tiers: ["low"], limit: SurveyFixtureLibrary.gridPageItemLimit) +
                    recognitionArtists(archetypeID: archetypeID, tiers: ["cult"], limit: SurveyFixtureLibrary.gridPageItemLimit)
            }
        }

        func appendArtistPolicyCandidate(archetypeID: String, slotIndex: Int) -> Bool {
            appendUnique(artistSlotCandidates(archetypeID: archetypeID, slotIndex: slotIndex), limit: 1) > 0
        }

        func appendNextArchetypeFallback(startingAt index: inout Int, slotIndex: Int) {
            while index < appleEvidence.topArchetypeIDs.count {
                let fallbackArchetypeID = appleEvidence.topArchetypeIDs[index]
                index += 1
                if appendArtistPolicyCandidate(archetypeID: fallbackArchetypeID, slotIndex: slotIndex) {
                    return
                }
            }
        }

        func appendArtistPolicyPage(pageNumber: Int) {
            let startIndex = pageNumber == 1 ? 0 : 4
            let targetArchetypeIDs = Array(appleEvidence.topArchetypeIDs.dropFirst(startIndex).prefix(4))
            var fallbackIndex = startIndex + targetArchetypeIDs.count
            for archetypeID in targetArchetypeIDs {
                for slotIndex in 0..<3 {
                    if !appendArtistPolicyCandidate(archetypeID: archetypeID, slotIndex: slotIndex) {
                        appendNextArchetypeFallback(startingAt: &fallbackIndex, slotIndex: slotIndex)
                    }
                }
            }
        }

        switch (descriptor.kind, descriptor.pageNumber) {
        case (.artist, 1):
            appendArtistPolicyPage(pageNumber: 1)
        case (.artist, 2):
            appendArtistPolicyPage(pageNumber: 2)
        case (.album, 1):
            appendUnique(topDirect(kind: .album, limit: 6), limit: 6)
        case (.song, 1):
            appendUnique(topDirect(kind: .song, limit: 8), limit: 8)
        case (.song, 2):
            appendUnique(topologySongCandidates(topFamilyOnly: true, limit: 6), limit: 6)
        case (.song, 3):
            appendUnique(topDirect(kind: .song, limit: 4), limit: 4)
        case (.song, 4):
            for archetypeID in appleEvidence.topArchetypeIDs.prefix(2) {
                appendUnique(topologySongCandidates(archetypeID: archetypeID, limit: 3), limit: 3)
            }
        default:
            break
        }

        return result
    }

    private func targetMix(for descriptor: AlphaSurveyStepDescriptor) -> [(AlphaSurveyIntentBucket, Int)] {
        switch (descriptor.kind, descriptor.pageNumber) {
        case (.artist, 1) where appleEvidence.hasUsableSignals:
            return [
                (.payloadSignature, 4),
                (.archetypeConfirmation, 3),
                (.junction, 2),
                (.falseNearby, 1),
                (.massPopularControl, 1),
                (.coverageRepair, 1)
            ]
        case (.artist, 1):
            return [
                (.archetypeConfirmation, 4),
                (.junction, 3),
                (.falseNearby, 1),
                (.massPopularControl, 2),
                (.coverageRepair, 2)
            ]
        case (.artist, 2):
            return [
                (.confirmRepeat, 4),
                (.junction, 3),
                (.disambiguate, 2),
                (.falseNearby, 1),
                (.payloadAdjacent, 1),
                (.frontier, 1)
            ]
        case (.artist, _):
            return [
                (.confirmRepeat, 3),
                (.disambiguate, 3),
                (.junction, 2),
                (.falseNearby, 1),
                (.frontier, 2),
                (.coverageRepair, 1)
            ]
        case (.album, _):
            return [
                (.confirmRepeat, 4),
                (.objectSpecific, 3),
                (.disambiguate, 2),
                (.falseNearby, 1),
                (.frontier, 1),
                (.coverageRepair, 1)
            ]
        case (.song, _):
            return [
                (.payloadSignature, 3),
                (.confirmRepeat, 3),
                (.objectSpecific, 2),
                (.disambiguate, 2),
                (.falseNearby, 1),
                (.coverageRepair, 1)
            ]
        }
    }

    private func isEligibleForAlphaIntake(
        _ candidate: AlphaSurveyRuntimeCandidate,
        descriptor: AlphaSurveyStepDescriptor,
        responses: [String: SurveyResponse]
    ) -> Bool {
        if candidate.kind != .artist && isBlockedByRejectedArtist(candidate, responses: responses) {
            return false
        }

        guard candidate.isDeepOnly else {
            return true
        }

        let apple = appleEvidence.score(for: candidate)
        if apple.strength >= 0.10 {
            return true
        }

        let response = responseRelevance(for: candidate, responses: responses)
        return descriptor.pageNumber > 1 &&
            max(response.posteriorRelevance, response.disambiguation, response.negativeShared) >= 0.35
    }

    private func isBlockedByRejectedArtist(
        _ candidate: AlphaSurveyRuntimeCandidate,
        responses: [String: SurveyResponse]
    ) -> Bool {
        let rejectedArtists = rejectedArtistKeys(responses: responses)
        guard !rejectedArtists.isEmpty else {
            return false
        }
        return !candidate.artistNames.isDisjoint(with: rejectedArtists)
    }

    private func rejectedArtistKeys(responses: [String: SurveyResponse]) -> Set<String> {
        responses.values.reduce(into: Set<String>()) { result, response in
            guard response.itemKind == .artist,
                  response.state == .notForMe,
                  let source = candidatesByItemID[response.itemID] else {
                return
            }
            result.formUnion(source.artistNames)
            result.insert(source.displayKey)
        }
    }

    private func score(
        _ candidate: AlphaSurveyRuntimeCandidate,
        for descriptor: AlphaSurveyStepDescriptor,
        responses: [String: SurveyResponse]
    ) -> Double {
        let apple = appleEvidence.score(for: candidate)
        let expectedFamiliarity = candidate.expectedFamiliarity
        let overrepresentation = apple.overrepresentation
        let response = responseRelevance(for: candidate, responses: responses)
        let junction = candidate.junctionValue
        let anchor = candidate.anchorValue
        let falseNearby = candidate.falseNearbyValue
        let coverage = coverageValue(for: candidate, responses: responses)
        let frontier = candidate.frontierValue

        if descriptor.kind == .artist && descriptor.pageNumber == 1 {
            return 0.22 * overrepresentation +
                0.18 * apple.strength +
                0.16 * expectedFamiliarity +
                0.14 * max(response.positiveShared, apple.archetypeHypothesis) +
                0.12 * junction +
                0.08 * anchor +
                0.05 * falseNearby +
                0.05 * coverage -
                candidate.genericSuperstarPenalty
        }

        return 0.22 * response.posteriorRelevance +
            0.18 * response.informationGain +
            0.14 * response.disambiguation +
            0.12 * max(response.bridgeValue, junction) +
            0.10 * coverage +
            0.08 * falseNearby +
            0.06 * expectedFamiliarity +
            0.04 * apple.strength +
            0.04 * frontier -
            response.penalty -
            candidate.genericSuperstarPenalty
    }

    private func intentBucket(
        for candidate: AlphaSurveyRuntimeCandidate,
        descriptor: AlphaSurveyStepDescriptor,
        responses: [String: SurveyResponse]
    ) -> AlphaSurveyIntentBucket {
        let apple = appleEvidence.score(for: candidate)
        let response = responseRelevance(for: candidate, responses: responses)

        if descriptor.kind == .artist && descriptor.pageNumber == 1 {
            if apple.strength >= 0.12 {
                return .payloadSignature
            }
            if candidate.isFalseNearby {
                return .falseNearby
            }
            if candidate.isJunction {
                return .junction
            }
            if candidate.priorityScore >= 94 {
                return .massPopularControl
            }
            if response.coverageGap > 0.5 || candidate.familyIDs.count > 1 {
                return .coverageRepair
            }
            return .archetypeConfirmation
        }

        if apple.strength >= 0.10 && response.posteriorRelevance < 0.25 {
            return .payloadAdjacent
        }
        if candidate.isFalseNearby || response.negativeShared > 0.28 {
            return .falseNearby
        }
        if candidate.kind != .artist && (candidate.isObjectSpecific || apple.strength >= 0.12) {
            return .objectSpecific
        }
        if response.positiveShared >= 0.25 {
            return .confirmRepeat
        }
        if candidate.isJunction {
            return .junction
        }
        if response.disambiguation >= 0.20 {
            return .disambiguate
        }
        if candidate.isFrontier {
            return .frontier
        }
        if response.coverageGap > 0.45 {
            return .coverageRepair
        }
        return .archetypeConfirmation
    }

    private func responseRelevance(
        for candidate: AlphaSurveyRuntimeCandidate,
        responses: [String: SurveyResponse]
    ) -> AlphaResponseRelevance {
        var positiveShared = 0.0
        var negativeShared = 0.0
        var okShared = 0.0
        var unknownShared = 0.0
        var exactArtistMatch = 0.0

        for response in responses.values {
            guard let source = candidatesByItemID[response.itemID] else {
                continue
            }
            let overlap = candidate.overlap(with: source)
            guard overlap > 0 else {
                continue
            }
            if candidate.artistNames.intersection(source.artistNames).isEmpty == false {
                exactArtistMatch = max(exactArtistMatch, 0.35)
            }
            switch response.state {
            case .favorite:
                positiveShared = max(positiveShared, min(1, overlap + 0.24 + exactArtistMatch))
            case .like:
                positiveShared = max(positiveShared, min(1, overlap + 0.16 + exactArtistMatch))
            case .fine:
                okShared = max(okShared, min(1, overlap + 0.12))
            case .notForMe:
                negativeShared = max(negativeShared, min(1, overlap + 0.16))
            case .dontKnow:
                unknownShared = max(unknownShared, min(1, overlap + 0.08))
            }
        }

        let disambiguation = max(okShared, negativeShared * 0.75, unknownShared * 0.45)
        let penalty = unknownShared > 0.35 && candidate.expectedFamiliarity < 0.60 ? 0.08 : 0
        let coverageGap = coverageGap(for: candidate, responses: responses)

        return AlphaResponseRelevance(
            positiveShared: positiveShared,
            negativeShared: negativeShared,
            okShared: okShared,
            unknownShared: unknownShared,
            posteriorRelevance: max(positiveShared, okShared * 0.65, negativeShared * 0.35),
            informationGain: max(candidate.junctionValue, candidate.falseNearbyValue, disambiguation, coverageGap),
            disambiguation: disambiguation,
            bridgeValue: max(candidate.junctionValue, positiveShared * candidate.anchorValue),
            coverageGap: coverageGap,
            penalty: penalty
        )
    }

    private func coverageValue(for candidate: AlphaSurveyRuntimeCandidate, responses: [String: SurveyResponse]) -> Double {
        coverageGap(for: candidate, responses: responses)
    }

    private func coverageGap(for candidate: AlphaSurveyRuntimeCandidate, responses: [String: SurveyResponse]) -> Double {
        let visibleCandidates = responses.values.compactMap { candidatesByItemID[$0.itemID] }
        guard !visibleCandidates.isEmpty else {
            return candidate.familyIDs.isEmpty ? 0.4 : 0.7
        }

        let seenFamilies = Set(visibleCandidates.flatMap(\.familyIDs))
        let seenArchetypes = Set(visibleCandidates.flatMap(\.archetypeIDs))
        let familyGap = candidate.familyIDs.isDisjoint(with: seenFamilies) ? 0.7 : 0.15
        let archetypeGap = candidate.archetypeIDs.isDisjoint(with: seenArchetypes) ? 0.5 : 0.10
        return max(familyGap, archetypeGap)
    }

    private func subtitle(for descriptor: AlphaSurveyStepDescriptor) -> String {
        if descriptor.kind == .artist && descriptor.pageNumber == 1 {
            return appleEvidence.hasUsableSignals
                ? "Apple exposure priors mapped into canonical graph tests"
                : "Canonical graph fallback because Apple exposure is thin"
        }
        return "Canonical graph tests shaped by visible Survey evidence"
    }

    private static func loadCandidates(
        bundle: Bundle,
        metadata: AlphaCanonicalMetadataStore,
        songAffinityTags: AlphaSongAffinityTagStore,
        blocklist: AlphaCandidateBlocklist
    ) -> [AlphaSurveyRuntimeCandidate] {
        let surfaceSpecs: [(SurveyItemKind, String)] = [
            (.artist, ResourceName.artistSurface),
            (.album, ResourceName.albumSurface),
            (.song, ResourceName.songSurface)
        ]

        return surfaceSpecs.flatMap { kind, resourceName in
            guard let surface: AlphaSurveyCandidateSurface = loadJSON(resourceName, bundle: bundle) else {
                return [AlphaSurveyRuntimeCandidate]()
            }

            var groups: [String: AlphaSurveyRuntimeCandidateBuilder] = [:]
            for family in surface.families {
                for row in family.approvedCandidates where !blocklist.blocks(row) {
                    var builder = groups[row.canonicalEntityID] ?? AlphaSurveyRuntimeCandidateBuilder(
                        kind: kind,
                        canonicalEntityID: row.canonicalEntityID,
                        displayLabel: row.displayLabel
                    )
                    builder.add(row: row, familyName: family.familyName)
                    groups[row.canonicalEntityID] = builder
                }
            }

            return groups.values.compactMap {
                $0.build(
                    metadata: metadata.metadata(for: kind, canonicalID: $0.canonicalEntityID),
                    affinityTags: kind == .song ? songAffinityTags.tags(for: $0.canonicalEntityID) : []
                )
            }
        }
    }

    private static func loadCanonicalMetadata(bundle: Bundle) -> AlphaCanonicalMetadataStore {
        let artists: [AlphaCanonicalMetadata] = loadJSON(ResourceName.artists, bundle: bundle) ?? []
        let albums: [AlphaCanonicalMetadata] = loadJSON(ResourceName.albums, bundle: bundle) ?? []
        let songs: [AlphaCanonicalMetadata] = loadJSON(ResourceName.songs, bundle: bundle) ?? []
        return AlphaCanonicalMetadataStore(artists: artists, albums: albums, songs: songs)
    }

    private static func loadAppleCatalogIndex(bundle: Bundle) -> AlphaAppleCatalogEvidenceStore {
        loadJSON("canonical_apple_music_catalog_index_v1", bundle: bundle) ?? .empty
    }

    private static func loadSongAffinityTags(bundle: Bundle) -> AlphaSongAffinityTagStore {
        if let cachedSongAffinityTags = Self.cachedSongAffinityTags {
            return cachedSongAffinityTags
        }
        let tags: AlphaSongAffinityTagStore = loadJSON(ResourceName.songAffinityTags, bundle: bundle) ?? .empty
        Self.cachedSongAffinityTags = tags
        return tags
    }

    private static func loadBlocklist(bundle: Bundle) -> AlphaCandidateBlocklist {
        loadJSON(ResourceName.alphaBlocklist, bundle: bundle) ?? .empty
    }

    private static func loadJSON<T: Decodable>(_ resourceName: String, bundle: Bundle) -> T? {
        let bundles = [bundle, Bundle.main] + Bundle.allBundles + Bundle.allFrameworks
        guard let url = bundles.lazy.compactMap({ $0.url(forResource: resourceName, withExtension: "json") }).first,
              let data = try? Data(contentsOf: url) else {
            return nil
        }
        return try? JSONDecoder().decode(T.self, from: data)
    }
}

private struct AlphaSurveyStepDescriptor {
    let step: SurveyStep
    let kind: SurveyItemKind
    let pageNumber: Int

    static let requiredStepOrder: [SurveyStep] = [
        .artistPage1,
        .artistPage2,
        .artistPage3,
        .artistPage4,
        .albumPage1,
        .albumPage2,
        .songPage1,
        .songPage2,
        .songPage3,
        .songPage4
    ]

    init?(step: SurveyStep) {
        self.step = step
        switch step {
        case .artistPage1:
            kind = .artist
            pageNumber = 1
        case .artistPage2:
            kind = .artist
            pageNumber = 2
        case .artistPage3:
            kind = .artist
            pageNumber = 3
        case .artistPage4:
            kind = .artist
            pageNumber = 4
        case .albumPage1:
            kind = .album
            pageNumber = 1
        case .albumPage2:
            kind = .album
            pageNumber = 2
        case .songPage1:
            kind = .song
            pageNumber = 1
        case .songPage2:
            kind = .song
            pageNumber = 2
        case .songPage3:
            kind = .song
            pageNumber = 3
        case .songPage4:
            kind = .song
            pageNumber = 4
        default:
            return nil
        }
    }

    var pageID: String {
        "\(kind.rawValue)_page_\(String(format: "%03d", pageNumber))"
    }

    var title: String {
        switch kind {
        case .artist:
            return "Artists \(pageNumber) of 4"
        case .album:
            return "Albums \(pageNumber) of 2"
        case .song:
            return "Songs \(pageNumber) of 4"
        }
    }

    var familyQuota: Int {
        kind == .artist ? 3 : 4
    }

    var archetypeQuota: Int {
        kind == .artist ? 2 : 3
    }
}

private enum AlphaSurveyIntentBucket: String {
    case payloadSignature
    case archetypeConfirmation
    case junction
    case falseNearby
    case massPopularControl
    case coverageRepair
    case confirmRepeat
    case disambiguate
    case payloadAdjacent
    case frontier
    case objectSpecific
}

private struct AlphaScoredSurveyCandidate: Comparable {
    let candidate: AlphaSurveyRuntimeCandidate
    let score: Double
    let intentBucket: AlphaSurveyIntentBucket

    static func == (lhs: AlphaScoredSurveyCandidate, rhs: AlphaScoredSurveyCandidate) -> Bool {
        lhs.candidate.itemID == rhs.candidate.itemID &&
            lhs.score == rhs.score &&
            lhs.intentBucket == rhs.intentBucket
    }

    static func < (lhs: AlphaScoredSurveyCandidate, rhs: AlphaScoredSurveyCandidate) -> Bool {
        if lhs.score != rhs.score {
            return lhs.score > rhs.score
        }
        if lhs.candidate.priorityScore != rhs.candidate.priorityScore {
            return lhs.candidate.priorityScore > rhs.candidate.priorityScore
        }
        return lhs.candidate.displayKey < rhs.candidate.displayKey
    }
}

private struct AlphaPriorVisibleCandidates {
    var itemIDs = Set<String>()
    var displayKeys = Set<String>()
}

private struct AlphaSurveyRepetitionGovernor {
    private var artistCounts = [String: Int]()
    private var archetypeCounts = [String: Int]()
    private let kind: SurveyItemKind
    private let maxArtistCount: Int?
    private let maxArchetypeCount: Int?

    init(
        kind: SurveyItemKind,
        priorCandidates: AlphaPriorVisibleCandidates,
        candidatesByItemID: [String: AlphaSurveyRuntimeCandidate]
    ) {
        self.kind = kind
        switch kind {
        case .album:
            maxArtistCount = 2
            maxArchetypeCount = nil
        case .song:
            maxArtistCount = 3
            maxArchetypeCount = 6
        case .artist:
            maxArtistCount = nil
            maxArchetypeCount = nil
        }

        for itemID in priorCandidates.itemIDs.sorted() {
            guard let candidate = candidatesByItemID[itemID] else {
                continue
            }
            record(candidate)
        }
    }

    func canAdd(_ candidate: AlphaSurveyRuntimeCandidate) -> Bool {
        guard candidate.kind == kind else {
            return false
        }
        if let maxArtistCount,
           candidate.artistNames.contains(where: { (artistCounts[$0] ?? 0) >= maxArtistCount }) {
            return false
        }
        if let maxArchetypeCount,
           candidate.archetypeIDs.contains(where: { (archetypeCounts[$0] ?? 0) >= maxArchetypeCount }) {
            return false
        }
        return true
    }

    mutating func record(_ candidate: AlphaSurveyRuntimeCandidate) {
        guard candidate.kind == kind else {
            return
        }
        if maxArtistCount != nil {
            for artistName in candidate.artistNames {
                artistCounts[artistName, default: 0] += 1
            }
        }
        if maxArchetypeCount != nil {
            for archetypeID in candidate.archetypeIDs {
                archetypeCounts[archetypeID, default: 0] += 1
            }
        }
    }
}

private struct AlphaResponseRelevance {
    let positiveShared: Double
    let negativeShared: Double
    let okShared: Double
    let unknownShared: Double
    let posteriorRelevance: Double
    let informationGain: Double
    let disambiguation: Double
    let bridgeValue: Double
    let coverageGap: Double
    let penalty: Double
}

private struct AlphaSurveyRuntimeCandidate {
    let kind: SurveyItemKind
    let canonicalID: String
    let displayName: String
    let familyIDs: Set<Int>
    let familyNames: Set<String>
    let archetypeIDs: Set<String>
    let surveyPageRoles: Set<String>
    let surveyIntents: Set<String>
    let dedupeGroups: Set<String>
    let priorityScore: Double
    let artistNames: Set<String>
    let artistDisplayNames: [String]
    let recognitionTier: String
    let surveyTier: String
    let affinityTags: Set<String>

    var itemID: String {
        "ALPHA_\(kind.rawValue.uppercased())_\(canonicalID)"
    }

    var displayKey: String {
        AlphaStringNormalizer.key(displayName)
    }

    var surveyItem: SurveyItem {
        surveyItem(appleDerived: false)
    }

    func surveyItem(appleDerived: Bool) -> SurveyItem {
        SurveyItem(
            id: itemID,
            kind: kind,
            title: displayName,
            subtitle: subtitle,
            artworkURL: nil,
            source: appleDerived ? .appleMusicDerived : source,
            objective: objective,
            rationale: rationale,
            artworkSeed: displayName
        )
    }

    var subtitle: String? {
        if kind == .artist {
            return familyNames.sorted().first
        }
        if let firstArtist = artistDisplayNames.sorted().first {
            return firstArtist
        }
        return familyNames.sorted().first
    }

    var source: SurveyItemSource {
        if isFalseNearby {
            return .rejectionProbe
        }
        if isFrontier {
            return .sleeperProbe
        }
        if isObjectSpecific || kind != .artist {
            return .objectSpecific
        }
        if isJunction {
            return .responseAdjacent
        }
        return .broadCalibration
    }

    var objective: SurveyBatchObjective {
        if isFalseNearby {
            return .checkDeadEnd
        }
        if isFrontier {
            return .probeSleeperFrontier
        }
        if isObjectSpecific || kind != .artist {
            return .separateObjectTaste
        }
        if isJunction {
            return .testAdjacentRoad
        }
        if priorityScore >= 92 {
            return .recognizeKnownTerritory
        }
        return .confirmLikelyRegion
    }

    var rationale: String {
        let intent = surveyIntents.sorted().first ?? "canonical_graph_candidate"
        return "Runtime canonical graph selection via \(intent)."
    }

    var expectedFamiliarity: Double {
        let tierBoost: Double
        switch recognitionTier {
        case "mass":
            tierBoost = 1.0
        case "high":
            tierBoost = 0.86
        case "medium":
            tierBoost = 0.62
        case "low":
            tierBoost = 0.38
        default:
            tierBoost = 0.55
        }
        return min(1, max(tierBoost, priorityScore / 100.0))
    }

    var isTopRecognitionTier: Bool {
        recognitionTier == "mass" || recognitionTier == "high" || priorityScore >= 92
    }

    var anchorValue: Double {
        max(priorityScore / 100.0, surveyPageRoles.contains("page1_core") ? 0.85 : 0.45)
    }

    var junctionValue: Double {
        isJunction ? min(1, 0.55 + (Double(archetypeIDs.count + familyIDs.count) * 0.10)) : 0.15
    }

    var frontierValue: Double {
        isFrontier ? 0.85 : (priorityScore < 70 ? 0.45 : 0.18)
    }

    var falseNearbyValue: Double {
        isFalseNearby ? 0.88 : 0.12
    }

    var genericSuperstarPenalty: Double {
        priorityScore >= 99 && isJunction ? 0.05 : 0
    }

    var isJunction: Bool {
        familyIDs.count > 1 || archetypeIDs.count > 1 || surveyIntents.contains("bridge_test")
    }

    var isFalseNearby: Bool {
        surveyIntents.contains { $0.contains("false") || $0.contains("boundary") }
    }

    var isObjectSpecific: Bool {
        surveyIntents.contains("album_world_test") || surveyIntents.contains("song_first_memory")
    }

    var isFrontier: Bool {
        surveyPageRoles.contains("page3_deep") || surveyIntents.contains("deepening_only") || priorityScore < 72
    }

    var isDeepOnly: Bool {
        !surveyPageRoles.isEmpty && surveyPageRoles.isSubset(of: Set(["page3_deep"]))
    }

    func overlap(with other: AlphaSurveyRuntimeCandidate) -> Double {
        if canonicalID == other.canonicalID && kind == other.kind {
            return 1
        }
        let familyOverlap = familyIDs.isDisjoint(with: other.familyIDs) ? 0.0 : 0.30
        let archetypeOverlap = archetypeIDs.isDisjoint(with: other.archetypeIDs) ? 0.0 : 0.45
        let artistOverlap = artistNames.isDisjoint(with: other.artistNames) ? 0.0 : 0.30
        return min(1, familyOverlap + archetypeOverlap + artistOverlap)
    }
}

private struct AlphaSurveyRuntimeCandidateBuilder {
    let kind: SurveyItemKind
    let canonicalEntityID: String
    let displayLabel: String
    var familyIDs = Set<Int>()
    var familyNames = Set<String>()
    var archetypeIDs = Set<String>()
    var surveyPageRoles = Set<String>()
    var surveyIntents = Set<String>()
    var dedupeGroups = Set<String>()
    var priorityScore = 0.0

    mutating func add(row: AlphaSurfaceCandidate, familyName: String) {
        familyIDs.insert(row.familyID)
        familyNames.insert(familyName)
        archetypeIDs.formUnion(row.archetypeIDs)
        surveyPageRoles.insert(row.surveyPageRole)
        surveyIntents.insert(row.surveyIntent)
        dedupeGroups.insert(row.dedupeGroup)
        priorityScore = max(priorityScore, row.priorityScore)
    }

    func build(metadata: AlphaCanonicalMetadata?, affinityTags: Set<String>) -> AlphaSurveyRuntimeCandidate? {
        let displayName = metadata?.displayName ?? displayLabel
        let metadataFamilies = Set(metadata?.familyNumbers ?? [])
        let metadataArchetypes = Set(metadata?.archetypeIDs ?? [])
        let artistNames = metadata?.artistNames ?? (kind == .artist ? [displayName] : [])

        return AlphaSurveyRuntimeCandidate(
            kind: kind,
            canonicalID: canonicalEntityID,
            displayName: displayName,
            familyIDs: familyIDs.union(metadataFamilies),
            familyNames: familyNames,
            archetypeIDs: archetypeIDs.union(metadataArchetypes),
            surveyPageRoles: surveyPageRoles,
            surveyIntents: surveyIntents,
            dedupeGroups: dedupeGroups,
            priorityScore: priorityScore,
            artistNames: Set(artistNames.map(AlphaStringNormalizer.key)),
            artistDisplayNames: artistNames,
            recognitionTier: metadata?.bestRecognitionTier ?? "unknown",
            surveyTier: metadata?.bestSurveyTier ?? "unknown",
            affinityTags: affinityTags
        )
    }
}

private struct AlphaSurveyCandidateSurface: Decodable {
    let families: [AlphaSurfaceFamily]
}

private struct AlphaSurfaceFamily: Decodable {
    let familyID: Int
    let familyName: String
    let page1Core: [AlphaSurfaceCandidate]
    let page2Adaptive: [AlphaSurfaceCandidate]
    let page3Deep: [AlphaSurfaceCandidate]

    enum CodingKeys: String, CodingKey {
        case familyID = "family_id"
        case familyName = "family_name"
        case page1Core = "page1_core"
        case page2Adaptive = "page2_adaptive"
        case page3Deep = "page3_deep"
    }

    var approvedCandidates: [AlphaSurfaceCandidate] {
        (page1Core + page2Adaptive + page3Deep).filter { $0.reviewStatus == "approved" && $0.quarantineReasons.isEmpty }
    }
}

private struct AlphaSurfaceCandidate: Decodable {
    let candidateID: String
    let canonicalEntityID: String
    let displayLabel: String
    let objectType: String
    let familyID: Int
    let archetypeIDs: [String]
    let surveyPageRole: String
    let surveyIntent: String
    let dedupeGroup: String
    let priorityScore: Double
    let reviewStatus: String
    let quarantineReasons: [String]

    enum CodingKeys: String, CodingKey {
        case candidateID = "candidate_id"
        case canonicalEntityID = "canonical_entity_id"
        case displayLabel = "display_label"
        case objectType = "object_type"
        case familyID = "family_id"
        case archetypeIDs = "archetype_ids"
        case surveyPageRole = "survey_page_role"
        case surveyIntent = "survey_intent"
        case dedupeGroup = "dedupe_group"
        case priorityScore = "priority_score"
        case reviewStatus = "review_status"
        case quarantineReasons = "quarantine_reasons"
    }
}

private struct AlphaCandidateBlocklist: Decodable {
    let blocklist: [Entry]

    static let empty = AlphaCandidateBlocklist(blocklist: [])

    func blocks(_ row: AlphaSurfaceCandidate) -> Bool {
        blocklist.contains { entry in
            guard entry.blockedSurfaces.contains("survey_display") else {
                return false
            }
            return entry.sourceCandidateID == row.candidateID ||
                (entry.objectType == row.objectType && entry.canonicalEntityID == row.canonicalEntityID) ||
                entry.entityRef == "\(row.objectType):\(row.canonicalEntityID)"
        }
    }

    struct Entry: Decodable {
        let entityRef: String
        let objectType: String
        let canonicalEntityID: String
        let sourceCandidateID: String?
        let blockedSurfaces: [String]

        enum CodingKeys: String, CodingKey {
            case entityRef = "entity_ref"
            case objectType = "object_type"
            case canonicalEntityID = "canonical_entity_id"
            case sourceCandidateID = "source_candidate_id"
            case blockedSurfaces = "blocked_surfaces"
        }
    }
}

private struct AlphaCanonicalMetadata: Decodable {
    let canonicalArtistID: String?
    let canonicalAlbumID: String?
    let canonicalSongRecordingID: String?
    let displayName: String
    let familyNumbers: [Int]
    let archetypeIDs: [String]
    let artistNames: [String]?
    let bestRecognitionTier: String
    let bestSurveyTier: String

    enum CodingKeys: String, CodingKey {
        case canonicalArtistID = "canonical_artist_id"
        case canonicalAlbumID = "canonical_album_id"
        case canonicalSongRecordingID = "canonical_song_recording_id"
        case displayName = "display_name"
        case familyNumbers = "family_numbers"
        case archetypeIDs = "archetype_ids"
        case artistNames = "artist_names"
        case bestRecognitionTier = "best_recognition_tier"
        case bestSurveyTier = "best_survey_tier"
    }
}

private struct AlphaCanonicalMetadataStore {
    let artistByID: [String: AlphaCanonicalMetadata]
    let albumByID: [String: AlphaCanonicalMetadata]
    let songByID: [String: AlphaCanonicalMetadata]

    init(artists: [AlphaCanonicalMetadata], albums: [AlphaCanonicalMetadata], songs: [AlphaCanonicalMetadata]) {
        artistByID = Dictionary(uniqueKeysWithValues: artists.compactMap { metadata in
            metadata.canonicalArtistID.map { ($0, metadata) }
        })
        albumByID = Dictionary(uniqueKeysWithValues: albums.compactMap { metadata in
            metadata.canonicalAlbumID.map { ($0, metadata) }
        })
        songByID = Dictionary(uniqueKeysWithValues: songs.compactMap { metadata in
            metadata.canonicalSongRecordingID.map { ($0, metadata) }
        })
    }

    func metadata(for kind: SurveyItemKind, canonicalID: String) -> AlphaCanonicalMetadata? {
        switch kind {
        case .artist:
            return artistByID[canonicalID]
        case .album:
            return albumByID[canonicalID]
        case .song:
            return songByID[canonicalID]
        }
    }
}

private struct AlphaSongAffinityTagStore: Decodable {
    let tagsByCanonicalID: [String: Set<String>]

    static let empty = AlphaSongAffinityTagStore(tagsByCanonicalID: [:])

    init(tagsByCanonicalID: [String: Set<String>]) {
        self.tagsByCanonicalID = tagsByCanonicalID
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        let entries = try container.decode([Entry].self, forKey: .entries)
        tagsByCanonicalID = entries.reduce(into: [String: Set<String>]()) { result, entry in
            result[entry.canonicalSongRecordingID, default: []].formUnion(entry.tags)
        }
    }

    func tags(for canonicalID: String) -> Set<String> {
        tagsByCanonicalID[canonicalID] ?? []
    }

    private enum CodingKeys: String, CodingKey {
        case entries
    }

    private struct Entry: Decodable {
        let canonicalSongRecordingID: String
        let tags: [String]

        enum CodingKeys: String, CodingKey {
            case canonicalSongRecordingID = "canonical_song_recording_id"
            case tags
        }
    }
}

private struct AlphaAppleCatalogEvidenceStore: Decodable {
    let entries: [Entry]

    static let empty = AlphaAppleCatalogEvidenceStore(entries: [])

    private var entriesByCatalogID: [String: [Entry]] {
        Dictionary(grouping: entries.filter { !$0.appleCatalogID.isEmpty }, by: \.appleCatalogID)
    }

    private var entriesByAlbumID: [String: [Entry]] {
        Dictionary(grouping: entries.compactMap { entry in
            entry.appleAlbumID.nilIfBlank.map { ($0, entry) }
        }) { $0.0 }
            .mapValues { pairs in pairs.map(\.1) }
    }

    func catalogEntries(for appleCatalogID: String?) -> [Entry] {
        guard let appleCatalogID = appleCatalogID?.nilIfBlank else {
            return []
        }
        return (entriesByCatalogID[appleCatalogID] ?? []).sortedForAppleEvidence()
    }

    func albumEntries(for appleAlbumID: String?) -> [Entry] {
        guard let appleAlbumID = appleAlbumID?.nilIfBlank else {
            return []
        }
        return (entriesByAlbumID[appleAlbumID] ?? []).sortedForAppleEvidence()
    }

    struct Entry: Decodable {
        let sourceType: String
        let sourceRef: String
        let itemType: String
        let appleCatalogID: String
        let appleAlbumID: String?
        let resolvedTitle: String?
        let resolvedArtist: String?
        let resolvedAlbum: String?
        let priority: Int
        let matchKeys: [String]

        enum CodingKeys: String, CodingKey {
            case sourceType = "source_type"
            case sourceRef = "source_ref"
            case itemType = "item_type"
            case appleCatalogID = "apple_catalog_id"
            case appleAlbumID = "apple_album_id"
            case resolvedTitle = "resolved_title"
            case resolvedArtist = "resolved_artist"
            case resolvedAlbum = "resolved_album"
            case priority
            case matchKeys = "match_keys"
        }
    }
}

private extension Array where Element == AlphaAppleCatalogEvidenceStore.Entry {
    func sortedForAppleEvidence() -> [AlphaAppleCatalogEvidenceStore.Entry] {
        sorted {
            if $0.priority != $1.priority {
                return $0.priority > $1.priority
            }
            return $0.sourceRef < $1.sourceRef
        }
    }
}

private struct AlphaAppleEvidenceIndex {
    struct Score {
        let strength: Double
        let overrepresentation: Double
        let archetypeHypothesis: Double
    }

    static let empty = AlphaAppleEvidenceIndex()

    private let directStrengths: [SurveyItemKind: [String: Double]]
    private let artistStrengths: [String: Double]
    private let topologySongStrengths: [String: Double]
    private let familyMixSeed: Int
    let topArchetypeIDs: [String]
    let topFamilyIDs: [Int]

    private init() {
        directStrengths = [:]
        artistStrengths = [:]
        topologySongStrengths = [:]
        familyMixSeed = 0
        topArchetypeIDs = []
        topFamilyIDs = []
    }

    init(
        payload: AppleMusicSignalPayload?,
        candidates: [AlphaSurveyRuntimeCandidate],
        catalogIndex: AlphaAppleCatalogEvidenceStore
    ) {
        guard let payload else {
            self = .empty
            return
        }

        let candidateIndex = CandidateIndex(candidates: candidates)
        var builder = Builder(candidateIndex: candidateIndex, catalogIndex: catalogIndex)
        builder.ingestRecentlyPlayed(payload.primarySignalSources.recentlyPlayedTracks.items)
        if let replayTopArtists = payload.contextSources.replayTopArtists,
           let replayTopAlbums = payload.contextSources.replayTopAlbums,
           let replayTopSongs = payload.contextSources.replayTopSongs {
            builder.ingestReplayItems(replayTopArtists.items, expectedType: "artist")
            builder.ingestReplayItems(replayTopSongs.items, expectedType: "song")
            builder.ingestReplayItems(replayTopAlbums.items, expectedType: "album")
        } else {
            builder.ingestReplaySummary(payload.contextSources.replaySummary.items)
        }

        directStrengths = builder.directStrengths
        artistStrengths = builder.artistStrengths
        familyMixSeed = Self.stableHash(payload.payloadID)

        let sortedArchetypeWeights = builder.archetypeStrengths.sortedByWeight()
        let topArchetypeWeights = sortedArchetypeWeights.prefix(5)
        let topFamilyWeights = builder.familyStrengths.sortedByWeight().prefix(5)
        topArchetypeIDs = sortedArchetypeWeights.prefix(40).map(\.key)
        topFamilyIDs = topFamilyWeights.map(\.key)
        topologySongStrengths = Self.makeTopologySongStrengths(
            candidates: candidates,
            archetypeWeights: Dictionary(uniqueKeysWithValues: topArchetypeWeights.map { ($0.key, $0.value) }),
            familyWeights: Dictionary(uniqueKeysWithValues: topFamilyWeights.map { ($0.key, $0.value) }),
            directSongStrengths: builder.directStrengths[.song] ?? [:]
        )
    }

    var hasUsableSignals: Bool {
        directStrengths.values.contains { !$0.isEmpty } || !artistStrengths.isEmpty
    }

    func directStrength(for candidate: AlphaSurveyRuntimeCandidate) -> Double {
        let canonicalStrength = directStrengths[candidate.kind]?[candidate.canonicalID] ?? 0
        let artistRollup: Double
        switch candidate.kind {
        case .artist:
            artistRollup = max(
                artistStrengths[candidate.displayKey] ?? 0,
                candidate.artistNames.map { artistStrengths[$0] ?? 0 }.max() ?? 0
            )
        case .album:
            artistRollup = (candidate.artistNames.map { artistStrengths[$0] ?? 0 }.max() ?? 0) * 0.35
        case .song:
            artistRollup = (candidate.artistNames.map { artistStrengths[$0] ?? 0 }.max() ?? 0) * 0.20
        }
        return max(canonicalStrength, artistRollup)
    }

    func topDirectStrength(for candidate: AlphaSurveyRuntimeCandidate) -> Double {
        switch candidate.kind {
        case .artist:
            return directStrength(for: candidate)
        case .album, .song:
            return directStrengths[candidate.kind]?[candidate.canonicalID] ?? 0
        }
    }

    func topologySongScore(for candidate: AlphaSurveyRuntimeCandidate) -> Double {
        guard candidate.kind == .song else {
            return 0
        }
        return topologySongStrengths[candidate.canonicalID] ?? 0
    }

    func stableFamilyRank(_ familyID: Int) -> Int {
        let mixed = (familyID * 1_103_515_245 + familyMixSeed) % 2_147_483_647
        return abs(mixed)
    }

    func stableSelectionRank(_ value: String) -> Int {
        abs(Self.stableHash("\(familyMixSeed)::\(value)"))
    }

    func score(for candidate: AlphaSurveyRuntimeCandidate) -> Score {
        let directStrength = directStrength(for: candidate)
        let baseline = max(0.25, candidate.priorityScore / 100.0)
        return Score(
            strength: min(1, directStrength),
            overrepresentation: min(1, directStrength / baseline),
            archetypeHypothesis: directStrength > 0 ? min(1, 0.40 + directStrength * 0.60) : 0
        )
    }

    private static func makeTopologySongStrengths(
        candidates: [AlphaSurveyRuntimeCandidate],
        archetypeWeights: [String: Double],
        familyWeights: [Int: Double],
        directSongStrengths: [String: Double]
    ) -> [String: Double] {
        candidates.reduce(into: [String: Double]()) { result, candidate in
            guard candidate.kind == .song else {
                return
            }
            let archetypeScore = candidate.archetypeIDs.reduce(0.0) { $0 + (archetypeWeights[$1] ?? 0) }
            let familyScore = candidate.familyIDs.reduce(0.0) { $0 + ((familyWeights[$1] ?? 0) * 0.45) }
            let directPenalty = directSongStrengths[candidate.canonicalID] == nil ? 0 : 0.20
            let score = archetypeScore + familyScore - directPenalty
            if score > 0 {
                result[candidate.canonicalID] = score
            }
        }
    }

    private static func stableHash(_ value: String) -> Int {
        value.unicodeScalars.reduce(0) { partial, scalar in
            (partial * 31 + Int(scalar.value)) % 2_147_483_647
        }
    }

    private struct CandidateIndex {
        let artistsByKey: [String: [AlphaSurveyRuntimeCandidate]]
        let albumsByKey: [String: [AlphaSurveyRuntimeCandidate]]
        let songsByKey: [String: [AlphaSurveyRuntimeCandidate]]
        let candidatesByKindAndCanonicalID: [SurveyItemKind: [String: AlphaSurveyRuntimeCandidate]]

        init(candidates: [AlphaSurveyRuntimeCandidate]) {
            var artistsByKey = [String: [AlphaSurveyRuntimeCandidate]]()
            var albumsByKey = [String: [AlphaSurveyRuntimeCandidate]]()
            var songsByKey = [String: [AlphaSurveyRuntimeCandidate]]()
            var candidatesByKindAndCanonicalID = [SurveyItemKind: [String: AlphaSurveyRuntimeCandidate]]()

            for candidate in candidates {
                candidatesByKindAndCanonicalID[candidate.kind, default: [:]][candidate.canonicalID] = candidate
                switch candidate.kind {
                case .artist:
                    for key in [candidate.displayKey] + Array(candidate.artistNames) {
                        artistsByKey[key, default: []].append(candidate)
                    }
                case .album:
                    for artistKey in candidate.artistNames {
                        albumsByKey[Self.objectKey(title: candidate.displayName, artistKey: artistKey), default: []].append(candidate)
                    }
                case .song:
                    for artistKey in candidate.artistNames {
                        songsByKey[Self.objectKey(title: candidate.displayName, artistKey: artistKey), default: []].append(candidate)
                    }
                }
            }

            self.artistsByKey = artistsByKey.mapValues { $0.sortedForFallback() }
            self.albumsByKey = albumsByKey.mapValues { $0.sortedForFallback() }
            self.songsByKey = songsByKey.mapValues { $0.sortedForFallback() }
            self.candidatesByKindAndCanonicalID = candidatesByKindAndCanonicalID
        }

        func candidates(kind: SurveyItemKind, canonicalID: String?) -> [AlphaSurveyRuntimeCandidate] {
            guard let canonicalID else {
                return []
            }
            return candidatesByKindAndCanonicalID[kind]?[canonicalID].map { [$0] } ?? []
        }

        func artists(named value: String?) -> [AlphaSurveyRuntimeCandidate] {
            guard let value else {
                return []
            }
            return artistsByKey[AlphaStringNormalizer.key(value)] ?? []
        }

        func albums(title: String?, artist: String?) -> [AlphaSurveyRuntimeCandidate] {
            objectCandidates(title: title, artist: artist, table: albumsByKey)
        }

        func songs(title: String?, artist: String?) -> [AlphaSurveyRuntimeCandidate] {
            objectCandidates(title: title, artist: artist, table: songsByKey)
        }

        private func objectCandidates(
            title: String?,
            artist: String?,
            table: [String: [AlphaSurveyRuntimeCandidate]]
        ) -> [AlphaSurveyRuntimeCandidate] {
            guard let title = title?.nilIfBlank,
                  let artist = artist?.nilIfBlank else {
                return []
            }
            let artistKey = AlphaStringNormalizer.key(artist)
            var result = [AlphaSurveyRuntimeCandidate]()
            var seen = Set<String>()
            for key in Self.objectKeys(title: title, artistKey: artistKey) {
                for candidate in table[key] ?? [] where seen.insert(candidate.itemID).inserted {
                    result.append(candidate)
                }
            }
            return result
        }

        private static func objectKey(title: String, artistKey: String) -> String {
            "\(artistKey)::\(AlphaStringNormalizer.key(title))"
        }

        private static func objectKeys(title: String, artistKey: String) -> [String] {
            var result = [String]()
            var seen = Set<String>()
            for variant in titleVariants(title) {
                let key = objectKey(title: variant, artistKey: artistKey)
                if seen.insert(key).inserted {
                    result.append(key)
                }
            }
            return result
        }

        private static func titleVariants(_ title: String) -> [String] {
            let strippedBracketed = title
                .replacingOccurrences(
                    of: #"\s*[\(\[].*?[\)\]]"#,
                    with: "",
                    options: .regularExpression
                )
                .nilIfBlank
            let strippedTrailingVersion = (strippedBracketed ?? title)
                .replacingOccurrences(
                    of: #"(?i)\s*-\s*(remaster(ed)?|.*\bremaster(ed)?\b.*|single|deluxe.*|bonus.*)$"#,
                    with: "",
                    options: .regularExpression
                )
                .nilIfBlank
            return [title, strippedBracketed, strippedTrailingVersion].compactMap { $0 }
        }
    }

    private struct Builder {
        let candidateIndex: CandidateIndex
        let catalogIndex: AlphaAppleCatalogEvidenceStore
        var directStrengths = [SurveyItemKind: [String: Double]]()
        var artistStrengths = [String: Double]()
        var archetypeStrengths = [String: Double]()
        var familyStrengths = [Int: Double]()

        mutating func ingestRecentlyPlayed(_ items: [AppleMusicSignalResource]) {
            for item in items {
                ingestRecentlyPlayed(resource: item)
            }
        }

        mutating func ingestReplaySummary(_ items: [AppleMusicSignalResource]) {
            ingestReplayItems(items, expectedType: nil)
        }

        mutating func ingestReplayItems(_ items: [AppleMusicSignalResource], expectedType: String?) {
            let replayItems = items.compactMap { item -> (AppleMusicSignalResource, (type: String, appleID: String))? in
                guard let ref = Self.replayRef(from: item.catalogID ?? item.appleID, expectedType: expectedType) else {
                    return nil
                }
                return (item, ref)
            }

            for replayType in ["artist", "song", "album"] {
                let group = replayItems.filter { $0.1.type == replayType }
                for pair in group {
                    let item = pair.0
                    let replayRef = pair.1
                    let weight = Self.uniformAppleSourceWeight
                    switch replayRef.type {
                    case "artist":
                        let entries = catalogIndex.catalogEntries(for: replayRef.appleID).prefix(3)
                        if entries.isEmpty {
                            ingestFallbackArtist(resource: item, weight: weight)
                        } else {
                            for entry in entries {
                                ingest(catalogEntry: entry, weight: weight)
                            }
                        }
                    case "song":
                        let entries = catalogIndex.catalogEntries(for: replayRef.appleID).prefix(3)
                        if entries.isEmpty {
                            ingestFallbackSong(resource: item, weight: weight)
                        } else {
                            for entry in entries {
                                ingest(catalogEntry: entry, weight: weight)
                            }
                        }
                    case "album":
                        let entries = catalogIndex.albumEntries(for: replayRef.appleID).prefix(3)
                        if entries.isEmpty {
                            ingestFallbackAlbum(resource: item, weight: weight)
                        } else {
                            for entry in entries {
                                ingest(catalogEntry: entry, weight: weight)
                            }
                        }
                    default:
                        break
                    }
                }
            }
        }

        private mutating func ingestFallbackSong(resource: AppleMusicSignalResource, weight: Double) {
            add(
                candidates: candidateIndex.songs(title: resource.displayName, artist: resource.artistName),
                weight: weight,
                directMultiplier: 1.0
            )
            add(
                candidates: candidateIndex.albums(title: resource.albumTitle, artist: resource.artistName),
                weight: weight,
                directMultiplier: 0.55
            )
            addArtists(named: resource.artistName, weight: weight * 0.70)
        }

        private mutating func ingestFallbackAlbum(resource: AppleMusicSignalResource, weight: Double) {
            add(
                candidates: candidateIndex.albums(title: resource.displayName, artist: resource.artistName),
                weight: weight,
                directMultiplier: 1.0
            )
            addArtists(named: resource.artistName, weight: weight * 0.75)
        }

        private mutating func ingestFallbackArtist(resource: AppleMusicSignalResource, weight: Double) {
            addArtists(named: resource.artistName ?? resource.displayName, weight: weight)
        }

        private mutating func ingestRecentlyPlayed(resource: AppleMusicSignalResource) {
            let entries = catalogIndex.catalogEntries(for: resource.catalogID ?? resource.appleID).prefix(3)
            for entry in entries {
                ingestRecentlyPlayed(catalogEntry: entry)
            }
            if !entries.isEmpty {
                return
            }

            switch resource.resourceType {
            case .song:
                add(
                    candidates: candidateIndex.songs(title: resource.displayName, artist: resource.artistName),
                    weight: Self.recentlyPlayedDirectBonus,
                    directMultiplier: 1.0,
                    directCap: Self.recentlyPlayedSongCap,
                    topologyWeight: Self.recentlyPlayedTopologyBonus
                )
                add(
                    candidates: candidateIndex.albums(title: resource.albumTitle, artist: resource.artistName),
                    weight: Self.recentlyPlayedDirectBonus,
                    directMultiplier: Self.recentlyPlayedAlbumRollupMultiplier,
                    directCap: Self.recentlyPlayedAlbumCap,
                    topologyWeight: Self.recentlyPlayedTopologyBonus
                )
                addArtists(
                    named: resource.artistName,
                    weight: Self.recentlyPlayedArtistRollupBonus,
                    strengthCap: Self.recentlyPlayedArtistCap,
                    topologyWeight: Self.recentlyPlayedTopologyBonus
                )
            case .album:
                add(
                    candidates: candidateIndex.albums(title: resource.displayName, artist: resource.artistName),
                    weight: Self.recentlyPlayedDirectBonus,
                    directMultiplier: 1.0,
                    directCap: Self.recentlyPlayedAlbumCap,
                    topologyWeight: Self.recentlyPlayedTopologyBonus
                )
                addArtists(
                    named: resource.artistName,
                    weight: Self.recentlyPlayedArtistRollupBonus,
                    strengthCap: Self.recentlyPlayedArtistCap,
                    topologyWeight: Self.recentlyPlayedTopologyBonus
                )
            case .artist:
                addArtists(
                    named: resource.displayName,
                    weight: Self.recentlyPlayedDirectBonus,
                    strengthCap: Self.recentlyPlayedArtistCap,
                    topologyWeight: Self.recentlyPlayedTopologyBonus
                )
            case .playlist, .station, .genre, .unknown:
                break
            }
        }

        private mutating func ingestRecentlyPlayed(catalogEntry: AlphaAppleCatalogEvidenceStore.Entry) {
            let canonicalID = Self.canonicalID(from: catalogEntry)
            switch catalogEntry.itemType {
            case "artist":
                add(
                    candidates: candidateIndex.artists(named: catalogEntry.resolvedArtist ?? catalogEntry.resolvedTitle) +
                        candidateIndex.candidates(kind: .artist, canonicalID: canonicalID),
                    weight: Self.recentlyPlayedDirectBonus,
                    directMultiplier: 1.0,
                    directCap: Self.recentlyPlayedArtistCap,
                    topologyWeight: Self.recentlyPlayedTopologyBonus
                )
            case "track":
                add(
                    candidates: candidateIndex.songs(title: catalogEntry.resolvedTitle, artist: catalogEntry.resolvedArtist) +
                        candidateIndex.candidates(kind: .song, canonicalID: canonicalID),
                    weight: Self.recentlyPlayedDirectBonus,
                    directMultiplier: 1.0,
                    directCap: Self.recentlyPlayedSongCap,
                    topologyWeight: Self.recentlyPlayedTopologyBonus
                )
                add(
                    candidates: candidateIndex.albums(title: catalogEntry.resolvedAlbum, artist: catalogEntry.resolvedArtist),
                    weight: Self.recentlyPlayedDirectBonus,
                    directMultiplier: Self.recentlyPlayedAlbumRollupMultiplier,
                    directCap: Self.recentlyPlayedAlbumCap,
                    topologyWeight: Self.recentlyPlayedTopologyBonus
                )
                addArtists(
                    named: catalogEntry.resolvedArtist,
                    weight: Self.recentlyPlayedArtistRollupBonus,
                    strengthCap: Self.recentlyPlayedArtistCap,
                    topologyWeight: Self.recentlyPlayedTopologyBonus
                )
            case "album":
                add(
                    candidates: candidateIndex.albums(title: catalogEntry.resolvedAlbum, artist: catalogEntry.resolvedArtist) +
                        candidateIndex.candidates(kind: .album, canonicalID: canonicalID),
                    weight: Self.recentlyPlayedDirectBonus,
                    directMultiplier: 1.0,
                    directCap: Self.recentlyPlayedAlbumCap,
                    topologyWeight: Self.recentlyPlayedTopologyBonus
                )
                addArtists(
                    named: catalogEntry.resolvedArtist,
                    weight: Self.recentlyPlayedArtistRollupBonus,
                    strengthCap: Self.recentlyPlayedArtistCap,
                    topologyWeight: Self.recentlyPlayedTopologyBonus
                )
            default:
                break
            }
        }

        private mutating func ingest(resource: AppleMusicSignalResource, weight: Double) {
            for entry in catalogIndex.catalogEntries(for: resource.catalogID ?? resource.appleID).prefix(3) {
                ingest(catalogEntry: entry, weight: weight * 1.08)
            }

            switch resource.resourceType {
            case .song:
                add(candidates: candidateIndex.songs(title: resource.displayName, artist: resource.artistName), weight: weight, directMultiplier: 1.0)
                add(candidates: candidateIndex.albums(title: resource.albumTitle, artist: resource.artistName), weight: weight, directMultiplier: 0.55)
                addArtists(named: resource.artistName, weight: weight * 0.70)
            case .album:
                add(candidates: candidateIndex.albums(title: resource.displayName, artist: resource.artistName), weight: weight, directMultiplier: 1.0)
                addArtists(named: resource.artistName, weight: weight * 0.75)
            case .artist:
                addArtists(named: resource.displayName, weight: weight)
            case .playlist, .station, .genre, .unknown:
                break
            }
        }

        private mutating func ingest(catalogEntry: AlphaAppleCatalogEvidenceStore.Entry, weight: Double) {
            let canonicalID = Self.canonicalID(from: catalogEntry)
            switch catalogEntry.itemType {
            case "artist":
                add(
                    candidates: candidateIndex.artists(named: catalogEntry.resolvedArtist ?? catalogEntry.resolvedTitle) +
                        candidateIndex.candidates(kind: .artist, canonicalID: canonicalID),
                    weight: weight,
                    directMultiplier: 1.0
                )
            case "track":
                add(
                    candidates: candidateIndex.songs(title: catalogEntry.resolvedTitle, artist: catalogEntry.resolvedArtist) +
                        candidateIndex.candidates(kind: .song, canonicalID: canonicalID),
                    weight: weight,
                    directMultiplier: 1.0
                )
                addArtists(named: catalogEntry.resolvedArtist, weight: weight * 0.70)
            case "album":
                add(
                    candidates: candidateIndex.albums(title: catalogEntry.resolvedAlbum, artist: catalogEntry.resolvedArtist) +
                        candidateIndex.candidates(kind: .album, canonicalID: canonicalID),
                    weight: weight,
                    directMultiplier: 1.0
                )
                addArtists(named: catalogEntry.resolvedArtist, weight: weight * 0.75)
            default:
                break
            }
        }

        private mutating func addArtists(
            named value: String?,
            weight: Double,
            strengthCap: Double? = nil,
            topologyWeight: Double? = nil
        ) {
            let artists = candidateIndex.artists(named: value)
            add(
                candidates: artists,
                weight: weight,
                directMultiplier: 1.0,
                directCap: strengthCap,
                topologyWeight: topologyWeight
            )
            if let value {
                Self.addStrength(
                    key: AlphaStringNormalizer.key(value),
                    weight: weight,
                    cap: strengthCap,
                    to: &artistStrengths
                )
            }
        }

        private mutating func add(
            candidates: [AlphaSurveyRuntimeCandidate],
            weight: Double,
            directMultiplier: Double,
            directCap: Double? = nil,
            topologyWeight: Double? = nil
        ) {
            var seen = Set<String>()
            for candidate in candidates where seen.insert(candidate.itemID).inserted {
                let directWeight = weight * directMultiplier
                addDirectStrength(
                    kind: candidate.kind,
                    canonicalID: candidate.canonicalID,
                    weight: directWeight,
                    cap: directCap
                )
                if candidate.kind == .artist {
                    Self.addStrength(
                        key: candidate.displayKey,
                        weight: directWeight,
                        cap: directCap,
                        to: &artistStrengths
                    )
                    for artistName in candidate.artistNames {
                        Self.addStrength(
                            key: artistName,
                            weight: directWeight,
                            cap: directCap,
                            to: &artistStrengths
                        )
                    }
                }
                let topologyContribution = topologyWeight ?? weight
                for archetypeID in candidate.archetypeIDs {
                    archetypeStrengths[archetypeID, default: 0] += topologyContribution
                }
                for familyID in candidate.familyIDs {
                    familyStrengths[familyID, default: 0] += topologyContribution
                }
            }
        }

        private mutating func addDirectStrength(
            kind: SurveyItemKind,
            canonicalID: String,
            weight: Double,
            cap: Double?
        ) {
            var strengths = directStrengths[kind] ?? [:]
            Self.addStrength(key: canonicalID, weight: weight, cap: cap, to: &strengths)
            directStrengths[kind] = strengths
        }

        private static func addStrength(
            key: String,
            weight: Double,
            cap: Double?,
            to strengths: inout [String: Double]
        ) {
            guard !key.isEmpty else {
                return
            }
            let next = strengths[key, default: 0] + weight
            strengths[key] = cap.map { min($0, next) } ?? next
        }

        private static func replayRef(from rawValue: String?, expectedType: String? = nil) -> (type: String, appleID: String)? {
            guard let rawValue = rawValue?.nilIfBlank else {
                return nil
            }
            if let decodedRef = decodedReplayRef(from: rawValue) {
                return decodedRef
            }
            if let expectedType, rawValue.allSatisfy(\.isNumber) {
                return (expectedType, rawValue)
            }
            return nil
        }

        private static func decodedReplayRef(from rawValue: String) -> (type: String, appleID: String)? {
            let decoded = rawValue.hasPrefix("year-") ? rawValue : base64URLDecoded(rawValue)
            guard let decoded else {
                return nil
            }
            let parts = decoded.split(separator: "-", omittingEmptySubsequences: false)
            guard parts.count == 4,
                  parts[0] == "year" else {
                return nil
            }
            return (String(parts[2]), String(parts[3]))
        }

        private static func base64URLDecoded(_ rawValue: String) -> String? {
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

        private static let uniformAppleSourceWeight = 1.0
        private static let recentlyPlayedDirectBonus = uniformAppleSourceWeight
        private static let recentlyPlayedArtistRollupBonus = uniformAppleSourceWeight
        private static let recentlyPlayedAlbumRollupMultiplier = 0.50
        private static let recentlyPlayedSongCap = 5.0
        private static let recentlyPlayedArtistCap = 4.0
        private static let recentlyPlayedAlbumCap = 3.0
        private static let recentlyPlayedTopologyBonus = uniformAppleSourceWeight

        private static func canonicalID(from entry: AlphaAppleCatalogEvidenceStore.Entry) -> String? {
            for key in entry.matchKeys where key.hasPrefix("canonical_entity_id:") {
                return String(key.dropFirst("canonical_entity_id:".count))
            }
            let parts = entry.sourceRef.split(separator: "|", omittingEmptySubsequences: false)
            guard parts.count >= 3 else {
                return nil
            }
            let artist = AlphaStringNormalizer.key(String(parts[1]))
            let title = AlphaStringNormalizer.key(String(parts[2]))
            guard !title.isEmpty else {
                return nil
            }
            return artist.isEmpty ? title : "\(artist)-\(title)"
        }
    }
}

private extension Dictionary where Value == Double {
    func sortedByWeight() -> [(key: Key, value: Double)] where Key: Comparable {
        sorted {
            if $0.value != $1.value {
                return $0.value > $1.value
            }
            return $0.key < $1.key
        }
    }
}

private enum AlphaStringNormalizer {
    static func key(_ value: String) -> String {
        value
            .folding(options: [.diacriticInsensitive, .caseInsensitive], locale: .current)
            .lowercased()
            .replacingOccurrences(of: "&", with: " and ")
            .components(separatedBy: CharacterSet.alphanumerics.inverted)
            .filter { !$0.isEmpty }
            .joined(separator: "-")
    }
}

private extension Array where Element == AlphaSurveyRuntimeCandidate {
    func sortedForFallback() -> [AlphaSurveyRuntimeCandidate] {
        sorted {
            if $0.priorityScore != $1.priorityScore {
                return $0.priorityScore > $1.priorityScore
            }
            return $0.displayKey < $1.displayKey
        }
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
