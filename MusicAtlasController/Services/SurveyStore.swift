import Combine
import Foundation

struct PersistedSurveySession: Codable, Equatable {
    var currentStep: SurveyStep
    var responses: [String: SurveyResponse]
    var freeformSignals: [SurveyFreeformSignal]
    var advancedFilter: SurveyAdvancedFilter
    var updatedAt: Date?

    enum CodingKeys: String, CodingKey {
        case currentStep = "current_step"
        case responses
        case freeformSignals = "freeform_signals"
        case advancedFilter = "advanced_filter"
        case updatedAt = "updated_at"
    }

    static let empty = PersistedSurveySession(
        currentStep: .welcome,
        responses: [:],
        freeformSignals: [],
        advancedFilter: .era,
        updatedAt: nil
    )
}

struct SurveyPersistenceStore {
    private let fileManager: FileManager
    private let baseDirectoryURL: URL?
    private let isEnabled: Bool
    private let filename = "waymark_survey_session_v0_1.json"

    init(
        fileManager: FileManager = .default,
        baseDirectoryURL: URL? = nil,
        isEnabled: Bool = true
    ) {
        self.fileManager = fileManager
        self.baseDirectoryURL = baseDirectoryURL
        self.isEnabled = isEnabled
    }

    static let disabled = SurveyPersistenceStore(isEnabled: false)

    func load() -> PersistedSurveySession {
        guard isEnabled else {
            return .empty
        }

        do {
            let url = try storeURL()
            guard fileManager.fileExists(atPath: url.path) else {
                return .empty
            }

            let data = try Data(contentsOf: url)
            let decoder = JSONDecoder()
            decoder.dateDecodingStrategy = .iso8601
            return try decoder.decode(PersistedSurveySession.self, from: data)
        } catch {
            return .empty
        }
    }

    func save(_ session: PersistedSurveySession) throws {
        guard isEnabled else {
            return
        }

        let url = try storeURL()
        try fileManager.createDirectory(
            at: url.deletingLastPathComponent(),
            withIntermediateDirectories: true
        )

        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        let data = try encoder.encode(session)
        try data.write(to: url, options: .atomic)
    }

    func reset() throws {
        guard isEnabled else {
            return
        }

        let url = try storeURL()
        if fileManager.fileExists(atPath: url.path) {
            try fileManager.removeItem(at: url)
        }
    }

    private func storeURL() throws -> URL {
        if let baseDirectoryURL {
            return baseDirectoryURL.appendingPathComponent(filename, isDirectory: false)
        }

        let rootURL = try fileManager.url(
            for: .applicationSupportDirectory,
            in: .userDomainMask,
            appropriateFor: nil,
            create: true
        )
        .appendingPathComponent("MusicAtlasController", isDirectory: true)

        return rootURL.appendingPathComponent(filename, isDirectory: false)
    }
}

@MainActor
final class SurveyStore: ObservableObject {
    @Published private(set) var currentStep: SurveyStep
    @Published private(set) var responses: [String: SurveyResponse]
    @Published private(set) var freeformSignals: [SurveyFreeformSignal]
    @Published private(set) var advancedFilter: SurveyAdvancedFilter
    @Published private(set) var lastPersistenceError: String?

    private let persistenceStore: SurveyPersistenceStore
    private let pageProvider: any SurveyPageProviding
    private let itemLookup: [String: SurveyItem]
    private var hasPreparedRequiredAlphaIntake = false

    init(
        persistenceStore: SurveyPersistenceStore = SurveyPersistenceStore(),
        pageProvider: any SurveyPageProviding = FixtureSurveyPageProvider()
    ) {
        self.persistenceStore = persistenceStore
        self.pageProvider = pageProvider
        self.itemLookup = pageProvider.itemLookup()

        let restoredSession = persistenceStore.load()
        currentStep = restoredSession.currentStep
        responses = restoredSession.responses
        freeformSignals = restoredSession.freeformSignals
        advancedFilter = restoredSession.advancedFilter
    }

    var currentPage: SurveyGridPage? {
        if currentStep == .advancedSurvey {
            return pageProvider.advancedPage(for: advancedFilter, responses: responses)
        }

        return pageProvider.page(for: currentStep, responses: responses)
    }

    var shouldSuggestArtistPage3: Bool {
        pageProvider.shouldOfferArtistPage3(responses: responses)
    }

    var canMoveBackward: Bool {
        currentStep != .welcome
    }

    func state(for item: SurveyItem) -> SurveySignalState {
        responses[item.id]?.state ?? .dontKnow
    }

    func nuances(for item: SurveyItem) -> [SurveyNuance] {
        responses[item.id]?.nuances ?? []
    }

    func note(for item: SurveyItem) -> String {
        responses[item.id]?.note ?? ""
    }

    func cycleState(for item: SurveyItem, at date: Date = Date()) {
        setState(state(for: item).next, for: item, at: date)
    }

    func setState(_ state: SurveySignalState, for item: SurveyItem, at date: Date = Date()) {
        var response = response(for: item, at: date)
        response.state = state
        response.updatedAt = date
        responses[item.id] = response
        persist()
    }

    func toggleNuance(_ nuance: SurveyNuance, for item: SurveyItem, at date: Date = Date()) {
        var response = response(for: item, at: date)
        if response.nuances.contains(nuance) {
            response.nuances.removeAll { $0 == nuance }
        } else {
            response.nuances.append(nuance)
        }
        response.updatedAt = date
        responses[item.id] = response
        persist()
    }

    func updateNote(_ note: String, for item: SurveyItem, at date: Date = Date()) {
        var response = response(for: item, at: date)
        response.note = note.trimmingCharacters(in: .whitespacesAndNewlines)
        response.updatedAt = date
        responses[item.id] = response
        persist()
    }

    func setAdvancedFilter(_ filter: SurveyAdvancedFilter) {
        advancedFilter = filter
        persist()
    }

    func addFreeformSignal(_ text: String, at date: Date = Date()) {
        let trimmed = text.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else {
            return
        }

        freeformSignals.append(
            SurveyFreeformSignal(
                id: UUID(),
                text: trimmed,
                parsedClaims: [],
                confidence: "user_asserted",
                requiresConfirmation: true,
                capturedAt: date
            )
        )
        persist()
    }

    func goTo(_ step: SurveyStep) {
        currentStep = step
        persist()
    }

    func advance() {
        switch currentStep {
        case .welcome:
            goTo(.connectAppleMusic)
        case .connectAppleMusic:
            goTo(.artistPage1)
        case .artistPage1:
            goTo(.artistPage2)
        case .artistPage2:
            goTo(.artistPage3)
        case .artistPage3Prompt:
            goTo(.artistPage3)
        case .artistPage3:
            goTo(.artistPage4)
        case .artistPage4:
            goTo(.albumPage1)
        case .albumPage1:
            goTo(.albumPage2)
        case .albumPage2:
            goTo(.songPage1)
        case .songPage1:
            goTo(.songPage2)
        case .songPage2:
            goTo(.songPage3)
        case .songPage3:
            goTo(.songPage4)
        case .songPage4:
            goTo(.readout)
        case .deeperPrompt:
            goTo(.readout)
        case .advancedSurvey:
            goTo(.readout)
        case .readout:
            goTo(.readout)
        }
    }

    func goBack() {
        switch currentStep {
        case .welcome:
            break
        case .connectAppleMusic:
            goTo(.welcome)
        case .artistPage1:
            goTo(.connectAppleMusic)
        case .artistPage2:
            goTo(.artistPage1)
        case .artistPage3Prompt:
            goTo(.artistPage2)
        case .artistPage3:
            goTo(.artistPage2)
        case .artistPage4:
            goTo(.artistPage3)
        case .albumPage1:
            goTo(.artistPage4)
        case .albumPage2:
            goTo(.albumPage1)
        case .songPage1:
            goTo(.albumPage2)
        case .songPage2:
            goTo(.songPage1)
        case .songPage3:
            goTo(.songPage2)
        case .songPage4:
            goTo(.songPage3)
        case .deeperPrompt:
            goTo(.songPage4)
        case .advancedSurvey:
            goTo(.deeperPrompt)
        case .readout:
            goTo(.songPage4)
        }
    }

    func prepareRequiredAlphaIntake(resetExistingResponses: Bool = true) {
        guard !hasPreparedRequiredAlphaIntake else {
            return
        }
        hasPreparedRequiredAlphaIntake = true

        if resetExistingResponses {
            currentStep = .artistPage1
            responses = [:]
            freeformSignals = []
            advancedFilter = .era
            persist()
            return
        }

        switch currentStep {
        case .welcome, .connectAppleMusic, .artistPage3Prompt, .deeperPrompt, .advancedSurvey:
            goTo(.artistPage1)
        default:
            break
        }
    }

    func makeSummary() -> SurveySummary {
        let knownResponses = responses.values.compactMap { response -> (SurveyResponse, SurveyItem)? in
            guard let item = itemLookup[response.itemID] else {
                return nil
            }
            return (response, item)
        }

        return SurveySummary(
            totalResponses: responses.count,
            favorites: knownResponses.filter { $0.0.state == .favorite }.map(\.1),
            likes: knownResponses.filter { $0.0.state == .like }.map(\.1),
            fine: knownResponses.filter { $0.0.state == .fine }.map(\.1),
            notForMe: knownResponses.filter { $0.0.state == .notForMe }.map(\.1),
            unknownCount: responses.values.filter { $0.state == .dontKnow }.count,
            freeformSignals: freeformSignals
        )
    }

    private func response(for item: SurveyItem, at date: Date) -> SurveyResponse {
        responses[item.id] ?? SurveyResponse(
            itemID: item.id,
            itemKind: item.kind,
            state: .dontKnow,
            nuances: [],
            note: "",
            updatedAt: date
        )
    }

    private func persist() {
        do {
            try persistenceStore.save(
                PersistedSurveySession(
                    currentStep: currentStep,
                    responses: responses,
                    freeformSignals: freeformSignals,
                    advancedFilter: advancedFilter,
                    updatedAt: Date()
                )
            )
            lastPersistenceError = nil
        } catch {
            lastPersistenceError = error.localizedDescription
        }
    }
}

struct SurveyEvidenceExportBuilder {
    private let persistenceStore: SurveyPersistenceStore
    private let pageProvider: any SurveyPageProviding
    private let itemLookup: [String: SurveyItem]

    init(
        persistenceStore: SurveyPersistenceStore = SurveyPersistenceStore(),
        pageProvider: any SurveyPageProviding = FixtureSurveyPageProvider()
    ) {
        self.persistenceStore = persistenceStore
        self.pageProvider = pageProvider
        self.itemLookup = pageProvider.itemLookup()
    }

    func makeFirstMissionGenerationRequest(
        testerAlias: String,
        requestedBatchSize: Int = AlphaMissionGenerationConfig.requiredMissionCount,
        sourceAppVersion: String,
        sourceAppBuild: String,
        batchMissionIndex: Int? = nil,
        batchMissionTotal: Int? = nil,
        batchSeed: String? = nil,
        storefront: String = "us",
        now: Date = Date()
    ) throws -> MissionGenerationRequest {
        let session = persistenceStore.load()
        let missionNumber = batchMissionIndex ?? 1
        let plan = AtlasSignalMissionPlanner.plan(
            for: session,
            missionNumber: missionNumber,
            missionTotal: batchMissionTotal ?? requestedBatchSize,
            itemLookup: itemLookup
        )
        return MissionGenerationRequest(
            clientRequestID: "ios_first_batch_\(UUID().uuidString)",
            testerAlias: testerAlias,
            requestedBatchSize: requestedBatchSize,
            surveyEvidenceExport: try makeSurveyEvidenceExportData(session: session, now: now),
            missionGenerationDigestView: try makeMissionGenerationDigestViewData(session: session, now: now),
            candidatePool: try makeCandidatePoolData(session: session, plan: plan, now: now),
            promptContext: MissionGenerationPromptContext(
                alphaScope: "first_batch_after_required_survey",
                generationMode: "live_app_generation_atlas_signal_constrained",
                sourceAppVersion: sourceAppVersion,
                sourceAppBuild: sourceAppBuild,
                storefront: storefront,
                surveyPageCount: SurveyPageCount(artist: 4, album: 2, song: 4),
                batchMissionIndex: batchMissionIndex,
                batchMissionTotal: batchMissionTotal,
                batchSeed: batchSeed,
                diversityDirective: batchMissionTotal.map {
                    "Generate one distinct \(plan.missionArchetype) mission for generic Atlas-signal slot \(missionNumber) of \($0). Use the supplied mission_intent and candidate pool; avoid repeating route structure, risk mix, or opening candidate from earlier slots."
                },
                missionPortfolioSlot: plan.portfolioSlot,
                missionArchetype: plan.missionArchetype,
                missionObjective: plan.objective,
                missionRequestID: plan.requestID,
                sourceCandidatePoolID: plan.candidatePoolID
            )
        )
    }

    func makeSurveyEvidenceExportData(session: PersistedSurveySession, now: Date = Date()) throws -> Data {
        try encodeJSONObject(makeSurveyEvidenceExport(session: session, now: now))
    }

    func makeMissionGenerationDigestViewData(session: PersistedSurveySession, now: Date = Date()) throws -> Data {
        try encodeJSONObject(makeMissionGenerationDigestView(session: session, now: now))
    }

    func makeCandidatePoolData(session: PersistedSurveySession, now: Date = Date()) throws -> Data {
        let plan = AtlasSignalMissionPlanner.plan(
            for: session,
            missionNumber: 1,
            missionTotal: AlphaMissionGenerationConfig.requiredMissionCount,
            itemLookup: itemLookup
        )
        return try makeCandidatePoolData(session: session, plan: plan, now: now)
    }

    func makeCandidatePoolData(
        session: PersistedSurveySession,
        plan: AtlasMissionPlan,
        now: Date = Date()
    ) throws -> Data {
        try encodeJSONObject(makeCandidatePool(session: session, plan: plan, now: now))
    }

    private func makeSurveyEvidenceExport(session: PersistedSurveySession, now: Date) -> [String: Any] {
        let responses = sortedResponses(session.responses).map { response -> [String: Any] in
            let item = itemLookup[response.itemID]
            return compactDictionary([
                "evidence_atom_id": "survey_response:\(response.itemID)",
                "atom_type": "survey_response",
                "atlas_ingestable": true,
                "item_id": response.itemID,
                "item_kind": response.itemKind.rawValue,
                "title": item?.title,
                "artist_or_subtitle": item?.subtitle,
                "state": response.state.rawValue,
                "reaction_operation": reactionOperation(for: response.state),
                "nuances": response.nuances.map(\.rawValue),
                "note": response.note.isEmpty ? nil : response.note,
                "source": item?.source.rawValue,
                "batch_objective": item?.objective.rawValue,
                "rationale": item?.rationale,
                "updated_at": isoString(response.updatedAt),
                "confidence": "user_visible_survey_response",
                "requires_confirmation": true
            ])
        }

        return compactDictionary([
            "schema_version": "waymark.survey_evidence_export.v0.1.app",
            "export_id": "survey_evidence_export:\(UUID().uuidString)",
            "created_at": isoString(now),
            "source": [
                "producer": "MusicAtlasController",
                "scope": "alpha_required_intake",
                "private_data_boundary": "user_visible_survey_responses_only"
            ],
            "ledger_semantics": [
                "survey_responses_are_evidence_not_verdicts",
                "apple_music_context_is_exposure_not_taste_truth",
                "atlas_truth_writes_disallowed"
            ],
            "reaction_operation_legend": [
                "favorite": "love",
                "like": "like",
                "fine": "keep",
                "not_for_me": "not_for_me",
                "dont_know": "unknown"
            ],
            "atlas_ingestable": [
                "evidence_atoms": responses
            ],
            "freeform_signals": session.freeformSignals.map { signal in
                compactDictionary([
                    "type": "survey_freeform_signal",
                    "id": signal.id.uuidString,
                    "text": signal.text,
                    "parsed_claims": signal.parsedClaims,
                    "confidence": signal.confidence,
                    "requires_confirmation": signal.requiresConfirmation,
                    "captured_at": isoString(signal.capturedAt)
                ])
            },
            "summary": makeSummaryDictionary(session: session)
        ])
    }

    private func makeMissionGenerationDigestView(session: PersistedSurveySession, now: Date) -> [String: Any] {
        let grouped = groupedResponses(session.responses)
        return compactDictionary([
            "schema_version": "waymark.mission_generation_digest_view.v0.1.app",
            "record_type": "mission_generation_digest_view",
            "digest_id": "mission_generation_digest_view:\(UUID().uuidString)",
            "generated_at": isoString(now),
            "mission_context": "first_batch_after_required_survey",
            "read_policy": [
                "use_as_generation_context_only",
                "do_not_promote_to_atlas_truth",
                "prefer_concrete_song_or_album_candidates_for_route_items"
            ],
            "anti_overfitting_rules": [
                "Survey responses create evidence, not final verdicts.",
                "Do not broaden one-object exceptions into genre approval.",
                "Do not treat Apple Music exposure as taste truth.",
                "Use positive and negative signals to design an experiment, not a comfort playlist."
            ],
            "core_taste_summary": makeCoreTasteSummary(grouped: grouped),
            "landmarks": grouped[.favorite] ?? [],
            "strong_regions": grouped[.like] ?? [],
            "useful_waypoints": grouped[.fine] ?? [],
            "known_dead_ends": grouped[.notForMe] ?? [],
            "unknowns": grouped[.dontKnow] ?? [],
            "frontiers": [],
            "promising_frontiers": [],
            "dead_ends": grouped[.notForMe] ?? [],
            "waypoints": grouped[.fine] ?? [],
            "user_vocabulary_terms": userVocabularyTerms(session: session),
            "unresolved_questions": [
                "First mission should test whether Survey positives survive actual playback.",
                "Negative survey evidence must remain scoped until repeated.",
                "Song and album exceptions should be preferred over broad genre inference."
            ],
            "candidate_pool_behavior": AtlasSignalMissionPlanner.behaviorHints(
                for: session,
                itemLookup: itemLookup
            ),
            "first_batch_portfolio": AtlasSignalMissionPlanner.portfolioSummary(
                for: session,
                itemLookup: itemLookup
            )
        ])
    }

    private func makeCandidatePool(session: PersistedSurveySession, plan: AtlasMissionPlan, now: Date) -> [String: Any] {
        return compactDictionary([
            "schema_version": "waymark.candidate_pool.v0.1",
            "pool_id": plan.candidatePoolID,
            "created_at": isoString(now),
            "candidate_policy": "Use approved Alpha route-ready candidates only. Do not use visible Survey grid songs as mission content unless the candidate survives the exact-repeat filter and serves the generic mission_intent. Keep all Atlas effects review-gated.",
            "source_contracts": [
                "data/product_contracts/app_local_candidate_pool_contract_alpha_v0.md",
                "data/product_contracts/mission_generation_alpha_handoff_v0_1.md",
                "data/alpha_consumable_layer/alpha_v0/sample_compact_candidate_pool_alpha_v0.json"
            ],
            "mission_portfolio_slot": [
                "slot": plan.portfolioSlot,
                "mission_archetype": plan.missionArchetype,
                "objective": plan.objective
            ],
            "mission_intent": plan.missionRequestDictionary,
            "mission_request": plan.missionRequestDictionary,
            "survey_response_focus": AtlasSignalMissionPlanner.behaviorHints(
                for: session,
                itemLookup: itemLookup
            ),
            "exclusions": [
                "visible_survey_tile_reuse_policy": "Survey-visible objects are evidence refs, not the mission route pool.",
                "atlas_truth_policy": "No Landmark, Region, Frontier, Dead End, or Waypoint is promoted by generation.",
                "raw_apple_payload_policy": "Apple Music exposure may bias candidate selection only through sanitized candidate refs."
            ],
            "candidates": plan.candidateDictionaries
        ])
    }

    private func sortedResponses(_ responses: [String: SurveyResponse]) -> [SurveyResponse] {
        responses.values.sorted { lhs, rhs in
            lhs.itemID < rhs.itemID
        }
    }

    private func groupedResponses(_ responses: [String: SurveyResponse]) -> [SurveySignalState: [[String: Any]]] {
        Dictionary(grouping: sortedResponses(responses)) { $0.state }
            .mapValues { responses in
                responses.compactMap { response in
                    guard let item = itemLookup[response.itemID] else {
                        return nil
                    }
                    return compactDictionary([
                        "item_id": item.id,
                        "kind": item.kind.rawValue,
                        "name": item.title,
                        "subtitle": item.subtitle,
                        "state": response.state.rawValue,
                        "nuances": response.nuances.map(\.rawValue),
                        "note": response.note.isEmpty ? nil : response.note
                    ])
                }
            }
    }

    private func makeSummaryDictionary(session: PersistedSurveySession) -> [String: Any] {
        let responses = Array(session.responses.values)
        return [
            "total_responses": responses.count,
            "favorite_count": responses.filter { $0.state == .favorite }.count,
            "like_count": responses.filter { $0.state == .like }.count,
            "fine_count": responses.filter { $0.state == .fine }.count,
            "not_for_me_count": responses.filter { $0.state == .notForMe }.count,
            "dont_know_count": responses.filter { $0.state == .dontKnow }.count,
            "freeform_signal_count": session.freeformSignals.count
        ]
    }

    private func makeCoreTasteSummary(grouped: [SurveySignalState: [[String: Any]]]) -> String {
        let favorites = grouped[.favorite]?.compactMap { $0["name"] as? String }.prefix(6).joined(separator: ", ")
        let likes = grouped[.like]?.compactMap { $0["name"] as? String }.prefix(6).joined(separator: ", ")
        let negatives = grouped[.notForMe]?.compactMap { $0["name"] as? String }.prefix(4).joined(separator: ", ")

        return [
            favorites?.isEmpty == false ? "Love: \(favorites!)" : nil,
            likes?.isEmpty == false ? "Like: \(likes!)" : nil,
            negatives?.isEmpty == false ? "Not for me: \(negatives!)" : nil
        ]
        .compactMap { $0 }
        .joined(separator: " | ")
    }

    private func userVocabularyTerms(session: PersistedSurveySession) -> [String] {
        let responseNotes = session.responses.values
            .map(\.note)
            .filter { !$0.isEmpty }
        return responseNotes + session.freeformSignals.map(\.text)
    }

    private func reactionOperation(for state: SurveySignalState) -> String {
        switch state {
        case .favorite:
            return "love"
        case .like:
            return "like"
        case .fine:
            return "keep"
        case .notForMe:
            return "not_for_me"
        case .dontKnow:
            return "unknown"
        }
    }

    private func candidateBehavior(for state: SurveySignalState) -> String {
        switch state {
        case .favorite:
            return "anchor"
        case .like:
            return "bridge"
        case .fine:
            return "waypoint"
        case .notForMe:
            return "trap"
        case .dontKnow:
            return "probe"
        }
    }

    private func riskClass(for state: SurveySignalState) -> String {
        switch state {
        case .favorite, .like:
            return "safe"
        case .fine:
            return "medium"
        case .notForMe:
            return "dead_end_check"
        case .dontKnow:
            return "risky"
        }
    }

    private func expectedFeatureHints(for state: SurveySignalState, item: SurveyItem) -> [String] {
        var hints = [item.objective.rawValue, item.source.rawValue]
        switch state {
        case .favorite:
            hints.append("strong_positive_survey_signal")
        case .like:
            hints.append("positive_survey_signal")
        case .fine:
            hints.append("possible_waypoint")
        case .notForMe:
            hints.append("boundary_or_dead_end_signal")
        case .dontKnow:
            hints.append("frontier_or_calibration_probe")
        }
        return hints
    }

    private func notesWarning(for state: SurveySignalState) -> String {
        switch state {
        case .favorite, .like:
            return "Positive survey evidence must survive playback before Atlas promotion."
        case .fine:
            return "Ok survey evidence may be waypoint, cultural furniture, or weak appetite."
        case .notForMe:
            return "Negative survey evidence must stay scoped and may be useful as a trap check."
        case .dontKnow:
            return "Unknown survey evidence is familiarity uncertainty, not negative taste."
        }
    }

    private func encodeJSONObject(_ object: [String: Any]) throws -> Data {
        try JSONSerialization.data(withJSONObject: object, options: [.prettyPrinted, .sortedKeys])
    }

    private func compactDictionary(_ dictionary: [String: Any?]) -> [String: Any] {
        dictionary.reduce(into: [String: Any]()) { result, pair in
            if let value = pair.value {
                result[pair.key] = value
            }
        }
    }

    private func isoString(_ date: Date) -> String {
        ISO8601DateFormatter().string(from: date)
    }
}

struct AtlasMissionPlan: Equatable {
    let intent: AtlasMissionIntent
    let sourceSignalRefs: [[String: String]]
    let candidatePoolID: String
    let candidates: [AlphaRouteCandidate]

    var requestID: String { intent.intentID }
    var portfolioSlot: String { intent.portfolioSlot }
    var missionArchetype: String { intent.missionArchetype }
    var objective: String { intent.objective }

    var missionRequestDictionary: [String: Any] {
        [
            "request_id": intent.intentID,
            "portfolio_slot": intent.portfolioSlot,
            "mission_archetype": intent.missionArchetype,
            "objective": intent.objective,
            "prompt": intent.prompt,
            "why_now": intent.whyNow,
            "route_shape": intent.routeShape,
            "target_candidate_pool_behaviors": intent.targetCandidatePoolBehaviors,
            "risk_mix": intent.riskMix,
            "source_signal_refs": sourceSignalRefs,
            "expected_route_item_count": [
                "min": intent.expectedRouteItemMin,
                "max": intent.expectedRouteItemMax
            ],
            "candidate_pool_id": candidatePoolID,
            "constraints": [
                "allow_duplicate_songs": false,
                "candidate_constrained_allowed": true,
                "personal_example_missions_allowed": false,
                "named_artist_or_scene_intents_allowed": false,
                "visible_survey_tile_exact_repeat_allowed": false,
                "atlas_truth_promotion_allowed": false
            ]
        ]
    }

    var candidateDictionaries: [[String: Any]] {
        candidates.map { $0.dictionary }
    }
}

struct AtlasMissionIntent: Equatable {
    let intentID: String
    let portfolioSlot: String
    let missionArchetype: String
    let objective: String
    let prompt: String
    let whyNow: String
    let routeShape: String
    let targetCandidatePoolBehaviors: [String]
    let riskMix: [String: Int]
    let expectedRouteItemMin: Int
    let expectedRouteItemMax: Int
}

struct AlphaRouteCandidate: Decodable, Equatable {
    let candidateID: String
    let candidateRole: String?
    let missionCandidateRole: String?
    let candidatePoolBehavior: String
    let routeItemType: String
    let objectType: String
    let canonicalObjectType: String?
    let canonicalEntityID: String?
    let displayName: String
    let displayLabel: String?
    let creditedArtist: String?
    let familyID: Int?
    let archetypeIDs: [String]
    let surveyIntent: String?
    let dedupeGroup: String?
    let priorityScore: Double?
    let whySelected: String?
    let expectedSignal: String?
    let riskClass: String
    let familiarityAssumption: String?
    let positiveInference: [String]
    let negativeInference: [String]
    let doNotInfer: [String]
    let musicKitSearchHint: String
    let musicKitResolutionStatus: String?
    let appleMusicResolutionPolicy: String?
    let versionRiskNote: String?
    let sourcePool: String
    let eligibleForSupabase: Bool?
    let eligibleForOpenAI: Bool?

    enum CodingKeys: String, CodingKey {
        case candidateID = "candidate_id"
        case candidateRole = "candidate_role"
        case missionCandidateRole = "mission_candidate_role"
        case candidatePoolBehavior = "candidate_pool_behavior"
        case routeItemType = "route_item_type"
        case objectType = "object_type"
        case canonicalObjectType = "canonical_object_type"
        case canonicalEntityID = "canonical_entity_id"
        case displayName = "display_name"
        case displayLabel = "display_label"
        case creditedArtist = "credited_artist"
        case familyID = "family_id"
        case archetypeIDs = "archetype_ids"
        case surveyIntent = "survey_intent"
        case dedupeGroup = "dedupe_group"
        case priorityScore = "priority_score"
        case whySelected = "why_selected"
        case expectedSignal = "expected_signal"
        case riskClass = "risk_class"
        case familiarityAssumption = "familiarity_assumption"
        case positiveInference = "positive_inference"
        case negativeInference = "negative_inference"
        case doNotInfer = "do_not_infer"
        case musicKitSearchHint = "music_kit_search_hint"
        case musicKitResolutionStatus = "music_kit_resolution_status"
        case appleMusicResolutionPolicy = "apple_music_resolution_policy"
        case versionRiskNote = "version_risk_note"
        case sourcePool = "source_pool"
        case eligibleForSupabase = "eligible_for_supabase"
        case eligibleForOpenAI = "eligible_for_openai"
    }

    var dictionary: [String: Any] {
        var output: [String: Any] = [
            "candidate_id": candidateID,
            "item_type": routeItemType,
            "route_item_type": routeItemType,
            "object_type": objectType,
            "display_name": displayName,
            "title": displayName,
            "archetype_ids": archetypeIDs,
            "risk_class": riskClass,
            "candidate_pool_behavior": candidatePoolBehavior,
            "candidate_reason": whySelected ?? expectedSignal ?? "Selected from approved Alpha route-ready candidate pool.",
            "expected_signal": expectedSignal ?? "Use listening feedback to test this candidate's provisional route role.",
            "expected_feature_hints": expectedFeatureHints,
            "positive_inference": positiveInference,
            "negative_inference": negativeInference,
            "do_not_infer": doNotInfer,
            "music_kit_search_hint": [
                "search_query": musicKitSearchHint,
                "artist": creditedArtist ?? "",
                "title": displayName,
                "preferred_version_notes": versionRiskNote ?? "Use the canonical Apple Music version when available.",
                "avoid_versions": "Avoid live, karaoke, tribute, remix, demo, and re-recording versions unless explicitly canonical.",
                "resolution_status_placeholder": "unresolved"
            ],
            "review_state": [
                "needs_human_review": needsHumanReview,
                "review_notes": "Preserve candidate-pool role. Do not promote this item into Atlas truth without listening evidence.",
                "uncertainty_flags": needsHumanReview ? ["review_gated_candidate_role"] : []
            ],
            "source_pool": sourcePool
        ]

        output["artist"] = creditedArtist
        output["credited_artist"] = creditedArtist
        output["canonical_object_type"] = canonicalObjectType
        output["canonical_entity_id"] = canonicalEntityID
        output["candidate_role"] = candidateRole
        output["mission_candidate_role"] = missionCandidateRole
        output["family_id"] = familyID
        output["survey_intent"] = surveyIntent
        output["dedupe_group"] = dedupeGroup
        output["priority_score"] = priorityScore
        output["familiarity_assumption"] = familiarityAssumption
        output["music_kit_resolution_status"] = musicKitResolutionStatus
        output["apple_music_resolution_policy"] = appleMusicResolutionPolicy
        output["version_risk_note"] = versionRiskNote
        output["eligible_for_supabase"] = eligibleForSupabase
        output["eligible_for_openai"] = eligibleForOpenAI
        return output
    }

    var exactSurveyRepeatKey: String {
        AtlasSignalMissionPlanner.displayKey(title: displayName, subtitle: creditedArtist)
    }

    private var expectedFeatureHints: [String] {
        var hints = [
            candidatePoolBehavior,
            riskClass,
            sourcePool
        ]
        if let surveyIntent {
            hints.append(surveyIntent)
        }
        if let expectedSignal {
            hints.append(expectedSignal)
        }
        return Array(NSOrderedSet(array: hints).compactMap { $0 as? String })
    }

    private var needsHumanReview: Bool {
        let highRiskValues = ["trap", "dead_end_check", "risky", "high", "boundary"]
        return highRiskValues.contains(candidatePoolBehavior)
            || highRiskValues.contains(riskClass)
            || candidatePoolBehavior.contains("probe")
            || sourcePool.contains("probe")
    }
}

struct AlphaCandidatePoolArtifact: Decodable {
    let artifact: String?
    let version: String?
    let sourceContract: String?
    let routeReadinessStatus: String?
    let pools: [String: [AlphaRouteCandidate]]

    enum CodingKeys: String, CodingKey {
        case artifact
        case version
        case sourceContract = "source_contract"
        case routeReadinessStatus = "route_readiness_status"
        case pools
    }

    static let empty = AlphaCandidatePoolArtifact(
        artifact: nil,
        version: nil,
        sourceContract: nil,
        routeReadinessStatus: nil,
        pools: [:]
    )

    static func load(bundle: Bundle = .main) -> AlphaCandidatePoolArtifact {
        guard let url = bundle.url(forResource: "alpha_compact_candidate_pool_alpha_v0", withExtension: "json") else {
            return .empty
        }

        do {
            let data = try Data(contentsOf: url)
            return try JSONDecoder().decode(AlphaCandidatePoolArtifact.self, from: data)
        } catch {
            return .empty
        }
    }
}

enum AtlasSignalMissionPlanner {
    static func plan(
        for session: PersistedSurveySession,
        missionNumber: Int,
        missionTotal: Int,
        itemLookup: [String: SurveyItem]
    ) -> AtlasMissionPlan {
        let profile = SignalProfile(session: session, itemLookup: itemLookup)
        let ranked = rankedIntents(for: profile, missionTotal: missionTotal)
        let boundedIndex = max(0, min(max(missionTotal, 1) - 1, missionNumber - 1))
        let intent = ranked[boundedIndex % ranked.count]
        let artifact = AlphaCandidatePoolArtifact.load()
        let candidates = selectCandidates(
            for: intent,
            from: artifact,
            excluding: exactSurveyRepeatKeys(itemLookup: itemLookup),
            missionNumber: missionNumber
        )
        return AtlasMissionPlan(
            intent: intent,
            sourceSignalRefs: profile.sourceSignalRefs(for: intent),
            candidatePoolID: "alpha_v0_\(intent.intentID)_slot_\(missionNumber)",
            candidates: candidates
        )
    }

    static func portfolioSummary(
        for session: PersistedSurveySession,
        itemLookup: [String: SurveyItem]
    ) -> [[String: Any]] {
        let profile = SignalProfile(session: session, itemLookup: itemLookup)
        return rankedIntents(for: profile, missionTotal: AlphaMissionGenerationConfig.requiredMissionCount).enumerated().map { index, intent in
            [
                "slot_index": index + 1,
                "request_id": intent.intentID,
                "portfolio_slot": intent.portfolioSlot,
                "mission_archetype": intent.missionArchetype,
                "objective": intent.objective,
                "selection_basis": "generic_atlas_signal_profile"
            ]
        }
    }

    static func behaviorHints(
        for session: PersistedSurveySession,
        itemLookup: [String: SurveyItem]
    ) -> [[String: Any]] {
        session.responses.values
            .sorted { $0.itemID < $1.itemID }
            .compactMap { response -> [String: Any]? in
                guard let item = itemLookup[response.itemID] else {
                    return nil
                }
                return [
                    "source_item_id": item.id,
                    "object_type": item.kind.rawValue,
                    "display_name": item.subtitle.map { "\(item.title) - \($0)" } ?? item.title,
                    "survey_state": response.state.rawValue,
                    "candidate_pool_behavior": behavior(for: response.state),
                    "scope_note": "Visible Survey response only; use as provisional candidate-pool cue."
                ]
            }
    }

    private static func behavior(for state: SurveySignalState) -> String {
        switch state {
        case .favorite:
            return "anchor"
        case .like:
            return "bridge"
        case .fine:
            return "waypoint"
        case .notForMe:
            return "trap"
        case .dontKnow:
            return "unknown"
        }
    }

    static func displayKey(title: String, subtitle: String?) -> String {
        [
            title.trimmingCharacters(in: .whitespacesAndNewlines).lowercased(),
            subtitle?.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        ]
        .compactMap { value in
            guard let value, !value.isEmpty else { return nil }
            return value
        }
        .joined(separator: "::")
    }

    private static func exactSurveyRepeatKeys(itemLookup: [String: SurveyItem]) -> Set<String> {
        Set(itemLookup.values.map { displayKey(title: $0.title, subtitle: $0.subtitle) })
    }

    private static func rankedIntents(for profile: SignalProfile, missionTotal: Int) -> [AtlasMissionIntent] {
        var intents = baseIntents

        if profile.negativeCount >= 4 {
            move("dead_end_or_contradiction_check_01", to: 2, in: &intents)
        }
        if profile.unknownCount >= 8 {
            move("frontier_probe_01", to: 2, in: &intents)
        }
        if profile.waypointCount >= 4 {
            move("waypoint_check_01", to: 3, in: &intents)
        }
        if profile.positiveCount == 0 {
            move("wildcard_delight_01", to: 0, in: &intents)
        }

        while intents.count < max(missionTotal, baseIntents.count) {
            let source = baseIntents[intents.count % baseIntents.count]
            let suffix = intents.count + 1
            intents.append(
                AtlasMissionIntent(
                    intentID: "\(source.intentID)_variant_\(suffix)",
                    portfolioSlot: source.portfolioSlot,
                    missionArchetype: source.missionArchetype,
                    objective: source.objective,
                    prompt: source.prompt,
                    whyNow: source.whyNow,
                    routeShape: "\(source.routeShape) Variant \(suffix) must use different candidates and a different opening role.",
                    targetCandidatePoolBehaviors: source.targetCandidatePoolBehaviors,
                    riskMix: source.riskMix,
                    expectedRouteItemMin: source.expectedRouteItemMin,
                    expectedRouteItemMax: source.expectedRouteItemMax
                )
            )
        }

        return intents
    }

    private static func move(_ intentID: String, to targetIndex: Int, in intents: inout [AtlasMissionIntent]) {
        guard let currentIndex = intents.firstIndex(where: { $0.intentID == intentID }) else {
            return
        }
        let intent = intents.remove(at: currentIndex)
        intents.insert(intent, at: min(max(0, targetIndex), intents.count))
    }

    private static func selectCandidates(
        for intent: AtlasMissionIntent,
        from artifact: AlphaCandidatePoolArtifact,
        excluding exactSurveyKeys: Set<String>,
        missionNumber: Int
    ) -> [AlphaRouteCandidate] {
        let poolPlan = poolPlan(for: intent)
        var selected = [AlphaRouteCandidate]()
        var seenDedupeGroups = Set<String>()

        for poolNeed in poolPlan {
            let candidates = artifact.pools[poolNeed.poolName] ?? []
            let filtered = candidates.filter { candidate in
                !exactSurveyKeys.contains(candidate.exactSurveyRepeatKey)
            }
            let source = filtered.isEmpty ? candidates : filtered
            appendCandidates(
                from: source,
                count: poolNeed.count,
                offset: missionNumber + selected.count,
                selected: &selected,
                seenDedupeGroups: &seenDedupeGroups
            )
        }

        if selected.count < intent.expectedRouteItemMin {
            let overflow = artifact.pools.values.flatMap { $0 }
                .filter { !exactSurveyKeys.contains($0.exactSurveyRepeatKey) }
            appendCandidates(
                from: overflow,
                count: intent.expectedRouteItemMin - selected.count,
                offset: missionNumber * 2,
                selected: &selected,
                seenDedupeGroups: &seenDedupeGroups
            )
        }

        return Array(selected.prefix(intent.expectedRouteItemMax))
    }

    private static func appendCandidates(
        from candidates: [AlphaRouteCandidate],
        count: Int,
        offset: Int,
        selected: inout [AlphaRouteCandidate],
        seenDedupeGroups: inout Set<String>
    ) {
        guard !candidates.isEmpty, count > 0 else {
            return
        }

        let sorted = candidates.sorted {
            ($0.priorityScore ?? 0, $0.candidateID) > ($1.priorityScore ?? 0, $1.candidateID)
        }
        let rotated = rotate(sorted, by: offset)
        var appendedCount = 0
        for candidate in rotated {
            let dedupe = candidate.dedupeGroup ?? candidate.exactSurveyRepeatKey
            guard seenDedupeGroups.insert(dedupe).inserted else {
                continue
            }
            selected.append(candidate)
            appendedCount += 1
            if appendedCount >= count {
                break
            }
        }
    }

    private static func rotate<T>(_ values: [T], by offset: Int) -> [T] {
        guard !values.isEmpty else {
            return values
        }
        let index = ((offset % values.count) + values.count) % values.count
        return Array(values[index...]) + Array(values[..<index])
    }

    private static func poolPlan(for intent: AtlasMissionIntent) -> [(poolName: String, count: Int)] {
        switch intent.portfolioSlot {
        case "safe_anchor":
            return [("anchors", 3), ("bridges", 3), ("waypoints", 1), ("boundary_probes", 1)]
        case "nearby_road":
            return [("bridges", 4), ("anchors", 2), ("probes", 2), ("dead_end_checks", 1)]
        case "frontier":
            return [("probes", 4), ("boundary_probes", 2), ("bridges", 2), ("anchors", 1)]
        case "dead_end_or_contradiction_check":
            return [("dead_end_checks", 4), ("boundary_probes", 2), ("anchors", 1), ("waypoints", 1)]
        case "waypoint_useful_not_canon":
            return [("waypoints", 4), ("anchors", 2), ("bridges", 2), ("dead_end_checks", 1)]
        case "wildcard_delight":
            return [("probes", 3), ("bridges", 2), ("boundary_probes", 2), ("anchors", 1)]
        default:
            return [("anchors", 2), ("bridges", 2), ("probes", 2), ("waypoints", 1)]
        }
    }

    private static let baseIntents: [AtlasMissionIntent] = [
        AtlasMissionIntent(
            intentID: "safe_anchor_01",
            portfolioSlot: "safe_anchor",
            missionArchetype: "Anchor Confirmation Route",
            objective: "Test whether visible positive Survey evidence survives actual playback without turning one object into broad canon.",
            prompt: "Build a bounded route around strong positive signals, with bridge and boundary checks.",
            whyNow: "The first Alpha batch needs at least one safer mission that establishes playback evidence around likely-fit territory.",
            routeShape: "Open with anchor/bridge candidates, then add one scoped boundary item and one review-gated waypoint.",
            targetCandidatePoolBehaviors: ["anchor", "bridge", "waypoint"],
            riskMix: ["safe": 6, "risky": 1, "trap": 1],
            expectedRouteItemMin: 7,
            expectedRouteItemMax: 10
        ),
        AtlasMissionIntent(
            intentID: "nearby_road_01",
            portfolioSlot: "nearby_road",
            missionArchetype: "Adjacent Road Route",
            objective: "Probe nearby candidate roads suggested by positive evidence while preserving explicit false-nearby risk.",
            prompt: "Build a route that tests adjacency, not sameness.",
            whyNow: "Survey positives need a second-order road test before the app can infer a durable region.",
            routeShape: "Use bridge candidates as the center, with a small number of anchors, probes, and traps.",
            targetCandidatePoolBehaviors: ["bridge", "anchor", "risky_probe", "trap"],
            riskMix: ["safe": 5, "risky": 2, "trap": 1],
            expectedRouteItemMin: 7,
            expectedRouteItemMax: 10
        ),
        AtlasMissionIntent(
            intentID: "frontier_probe_01",
            portfolioSlot: "frontier",
            missionArchetype: "Frontier Probe Route",
            objective: "Use unknown or under-tested territory as a controlled probe, not a claim of taste.",
            prompt: "Build a frontier mission with review-needed candidates and clear failure conditions.",
            whyNow: "The first Alpha batch should include at least one unknown or sleeper test so discovery is not only comfort confirmation.",
            routeShape: "Open with a bridge, run several probes, then close with an anchor or trap for contrast.",
            targetCandidatePoolBehaviors: ["probe", "risky_probe", "bridge"],
            riskMix: ["safe": 2, "risky": 5, "trap": 1],
            expectedRouteItemMin: 7,
            expectedRouteItemMax: 10
        ),
        AtlasMissionIntent(
            intentID: "dead_end_or_contradiction_check_01",
            portfolioSlot: "dead_end_or_contradiction_check",
            missionArchetype: "Boundary Check Route",
            objective: "Learn from negative or contradictory evidence without making the mission feel punitive.",
            prompt: "Build a route that tests a likely boundary and gives each candidate a possible rescue condition.",
            whyNow: "Negative evidence is useful only when scoped; Alpha needs one mission that prevents false-nearby overfitting.",
            routeShape: "Use trap/dead-end candidates with one anchor and one waypoint to keep the route interpretable.",
            targetCandidatePoolBehaviors: ["trap", "risky_probe", "anchor", "waypoint"],
            riskMix: ["safe": 2, "risky": 2, "trap": 4],
            expectedRouteItemMin: 7,
            expectedRouteItemMax: 10
        ),
        AtlasMissionIntent(
            intentID: "waypoint_check_01",
            portfolioSlot: "waypoint_useful_not_canon",
            missionArchetype: "Waypoint Check Route",
            objective: "Separate useful, familiar, or culturally relevant objects from true appetite.",
            prompt: "Build a route that tests whether kept/ok signals are useful waypoints or weak appetite.",
            whyNow: "Ok/fine survey responses can help navigation without becoming canon; the first batch should test that distinction.",
            routeShape: "Center waypoint candidates, then compare against anchors, bridges, and one scoped trap.",
            targetCandidatePoolBehaviors: ["waypoint", "anchor", "bridge", "trap"],
            riskMix: ["safe": 4, "risky": 2, "trap": 1],
            expectedRouteItemMin: 7,
            expectedRouteItemMax: 10
        ),
        AtlasMissionIntent(
            intentID: "wildcard_delight_01",
            portfolioSlot: "wildcard_delight",
            missionArchetype: "Wildcard Route",
            objective: "Create one controlled surprise route that can reveal unexpected appetite while staying candidate-constrained.",
            prompt: "Build a wildcard mission that is varied, review-gated, and clearly not an Atlas claim yet.",
            whyNow: "Trusted Alpha should feel alive enough to discover something, but the surprise needs guardrails.",
            routeShape: "Use probes and bridges with one anchor for orientation and one boundary item for calibration.",
            targetCandidatePoolBehaviors: ["probe", "bridge", "risky_probe", "anchor"],
            riskMix: ["safe": 3, "risky": 4, "trap": 1],
            expectedRouteItemMin: 7,
            expectedRouteItemMax: 10
        )
    ]

    private struct SignalProfile {
        let responses: [SurveyResponse]
        let itemLookup: [String: SurveyItem]
        let positiveCount: Int
        let negativeCount: Int
        let unknownCount: Int
        let waypointCount: Int

        init(session: PersistedSurveySession, itemLookup: [String: SurveyItem]) {
            self.responses = session.responses.values.sorted { $0.itemID < $1.itemID }
            self.itemLookup = itemLookup
            self.positiveCount = responses.filter { $0.state == .favorite || $0.state == .like }.count
            self.negativeCount = responses.filter { $0.state == .notForMe }.count
            self.unknownCount = responses.filter { $0.state == .dontKnow }.count
            self.waypointCount = responses.filter { $0.state == .fine }.count
        }

        func sourceSignalRefs(for intent: AtlasMissionIntent) -> [[String: String]] {
            let preferredStates: [SurveySignalState]
            switch intent.portfolioSlot {
            case "safe_anchor", "nearby_road":
                preferredStates = [.favorite, .like, .fine, .notForMe, .dontKnow]
            case "frontier", "wildcard_delight":
                preferredStates = [.dontKnow, .like, .favorite, .fine, .notForMe]
            case "dead_end_or_contradiction_check":
                preferredStates = [.notForMe, .fine, .like, .favorite, .dontKnow]
            case "waypoint_useful_not_canon":
                preferredStates = [.fine, .favorite, .like, .notForMe, .dontKnow]
            default:
                preferredStates = SurveySignalState.allCases
            }

            return preferredStates.flatMap { state in
                responses.filter { $0.state == state }.prefix(4).compactMap { response in
                    guard let item = itemLookup[response.itemID] else {
                        return nil
                    }
                    return [
                        "evidence_atom_id": "survey_response:\(response.itemID)",
                        "item_kind": item.kind.rawValue,
                        "display_name": item.subtitle.map { "\(item.title) - \($0)" } ?? item.title,
                        "survey_state": response.state.rawValue,
                        "candidate_pool_behavior": behavior(for: response.state)
                    ]
                }
            }
            .prefix(12)
            .map { $0 }
        }
    }
}
