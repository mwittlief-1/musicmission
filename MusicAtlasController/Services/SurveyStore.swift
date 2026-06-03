import Combine
import Foundation

struct PersistedSurveySession: Codable {
    var surveySessionID: String
    var currentStep: SurveyStep
    var responses: [String: SurveyResponse]
    var freeformSignals: [SurveyFreeformSignal]
    var advancedFilter: SurveyAdvancedFilter
    var displayedPages: [String: SurveyGridPage]
    var appleMusicSignalPayload: AppleMusicSignalPayload?
    var updatedAt: Date?

    enum CodingKeys: String, CodingKey {
        case surveySessionID = "survey_session_id"
        case currentStep = "current_step"
        case responses
        case freeformSignals = "freeform_signals"
        case advancedFilter = "advanced_filter"
        case displayedPages = "displayed_pages"
        case appleMusicSignalPayload = "apple_music_signal_payload"
        case updatedAt = "updated_at"
    }

    init(
        surveySessionID: String = PersistedSurveySession.makeSurveySessionID(),
        currentStep: SurveyStep,
        responses: [String: SurveyResponse],
        freeformSignals: [SurveyFreeformSignal],
        advancedFilter: SurveyAdvancedFilter,
        displayedPages: [String: SurveyGridPage] = [:],
        appleMusicSignalPayload: AppleMusicSignalPayload? = nil,
        updatedAt: Date?
    ) {
        self.surveySessionID = surveySessionID
        self.currentStep = currentStep
        self.responses = responses
        self.freeformSignals = freeformSignals
        self.advancedFilter = advancedFilter
        self.displayedPages = displayedPages
        self.appleMusicSignalPayload = appleMusicSignalPayload
        self.updatedAt = updatedAt
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        surveySessionID = try container.decodeIfPresent(String.self, forKey: .surveySessionID)
            ?? PersistedSurveySession.makeSurveySessionID()
        currentStep = try container.decodeIfPresent(SurveyStep.self, forKey: .currentStep) ?? .welcome
        responses = try container.decodeIfPresent([String: SurveyResponse].self, forKey: .responses) ?? [:]
        freeformSignals = try container.decodeIfPresent([SurveyFreeformSignal].self, forKey: .freeformSignals) ?? []
        advancedFilter = try container.decodeIfPresent(SurveyAdvancedFilter.self, forKey: .advancedFilter) ?? .era
        displayedPages = try container.decodeIfPresent([String: SurveyGridPage].self, forKey: .displayedPages) ?? [:]
        appleMusicSignalPayload = try container.decodeIfPresent(
            AppleMusicSignalPayload.self,
            forKey: .appleMusicSignalPayload
        )
        updatedAt = try container.decodeIfPresent(Date.self, forKey: .updatedAt)
    }

    static func makeSurveySessionID() -> String {
        "survey_session:\(UUID().uuidString)"
    }

    static let empty = PersistedSurveySession(
        surveySessionID: PersistedSurveySession.makeSurveySessionID(),
        currentStep: .welcome,
        responses: [:],
        freeformSignals: [],
        advancedFilter: .era,
        displayedPages: [:],
        appleMusicSignalPayload: nil,
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
    @Published private(set) var displayedPages: [String: SurveyGridPage]
    @Published private(set) var lastPersistenceError: String?

    private(set) var surveySessionID: String
    private var appleMusicSignalPayload: AppleMusicSignalPayload?
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
        surveySessionID = restoredSession.surveySessionID
        currentStep = restoredSession.currentStep
        responses = restoredSession.responses
        freeformSignals = restoredSession.freeformSignals
        advancedFilter = restoredSession.advancedFilter
        displayedPages = restoredSession.displayedPages
        appleMusicSignalPayload = restoredSession.appleMusicSignalPayload
        pageProvider.updateAppleMusicSignalPayload(restoredSession.appleMusicSignalPayload)
    }

    var currentPage: SurveyGridPage? {
        pageForCurrentStep()
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
        invalidateFutureDisplayedPages(afterRespondingTo: item.id)
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
        invalidateFutureDisplayedPages(afterRespondingTo: item.id)
        persist()
    }

    func updateNote(_ note: String, for item: SurveyItem, at date: Date = Date()) {
        var response = response(for: item, at: date)
        response.note = note.trimmingCharacters(in: .whitespacesAndNewlines)
        response.updatedAt = date
        responses[item.id] = response
        invalidateFutureDisplayedPages(afterRespondingTo: item.id)
        persist()
    }

    func setAdvancedFilter(_ filter: SurveyAdvancedFilter) {
        advancedFilter = filter
        persist()
    }

    func updateAppleMusicSignalPayload(_ payload: AppleMusicSignalPayload?) {
        appleMusicSignalPayload = payload
        pageProvider.updateAppleMusicSignalPayload(payload)
        displayedPages = [:]
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
            surveySessionID = PersistedSurveySession.makeSurveySessionID()
            currentStep = .connectAppleMusic
            responses = [:]
            freeformSignals = []
            advancedFilter = .era
            displayedPages = [:]
            appleMusicSignalPayload = nil
            pageProvider.updateAppleMusicSignalPayload(nil)
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

    private func pageForCurrentStep() -> SurveyGridPage? {
        if currentStep == .advancedSurvey {
            return pageProvider.advancedPage(for: advancedFilter, responses: responses)
        }

        let key = pageKey(for: currentStep)
        if let displayedPage = displayedPages[key] {
            return displayedPage
        }

        guard let generatedPage = pageProvider.page(
            for: currentStep,
            responses: responses,
            displayedPages: displayedPages
        ) else {
            return nil
        }

        displayedPages[key] = generatedPage
        persist()
        return generatedPage
    }

    private func invalidateFutureDisplayedPages(afterRespondingTo itemID: String) {
        guard let sourceStep = stepContainingDisplayedItem(itemID: itemID),
              let sourceIndex = Self.requiredAlphaPageSteps.firstIndex(of: sourceStep) else {
            return
        }

        for step in Self.requiredAlphaPageSteps.dropFirst(sourceIndex + 1) {
            displayedPages.removeValue(forKey: pageKey(for: step))
        }
    }

    private func stepContainingDisplayedItem(itemID: String) -> SurveyStep? {
        for step in Self.requiredAlphaPageSteps {
            guard let page = displayedPages[pageKey(for: step)] else {
                continue
            }
            if page.items.contains(where: { $0.id == itemID }) {
                return step
            }
        }
        return nil
    }

    private func pageKey(for step: SurveyStep) -> String {
        step.rawValue
    }

    private func persist() {
        do {
            try persistenceStore.save(
                PersistedSurveySession(
                    surveySessionID: surveySessionID,
                    currentStep: currentStep,
                    responses: responses,
                    freeformSignals: freeformSignals,
                    advancedFilter: advancedFilter,
                    displayedPages: displayedPages,
                    appleMusicSignalPayload: appleMusicSignalPayload,
                    updatedAt: Date()
                )
            )
            lastPersistenceError = nil
        } catch {
            lastPersistenceError = error.localizedDescription
        }
    }

    private static let requiredAlphaPageSteps: [SurveyStep] = [
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

    func loadPersistedSurveySession() -> PersistedSurveySession {
        persistenceStore.load()
    }

    func makeFirstMissionGenerationRequest(
        testerAlias: String,
        requestedBatchSize: Int = AlphaMissionGenerationConfig.requiredMissionCount,
        sourceAppVersion: String,
        sourceAppBuild: String,
        batchMissionIndex: Int? = nil,
        batchMissionTotal: Int? = nil,
        batchSeed: String? = nil,
        alreadySelectedRouteItemIDs: [String] = [],
        alreadySelectedRouteDisplayIdentityKeys: [String] = [],
        storefront: String = "us",
        now: Date = Date()
    ) throws -> MissionGenerationRequest {
        let session = persistenceStore.load()
        let missionNumber = batchMissionIndex ?? 1
        let batchMemoryDirective = alreadySelectedRouteItemIDs.isEmpty && alreadySelectedRouteDisplayIdentityKeys.isEmpty
            ? nil
            : "Do not use any already_selected_route_item_ids or already_selected_display_keys. already_selected_route_display_identity_keys is a legacy alias for the same display-key memory. If the candidate pool cannot support a unique route for this slot, return a blocked/retry-safe result rather than repeating a prior Alpha mission route item."
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
                sourceCandidatePoolID: plan.candidatePoolID,
                alreadySelectedRouteItemIDs: alreadySelectedRouteItemIDs,
                alreadySelectedRouteDisplayIdentityKeys: alreadySelectedRouteDisplayIdentityKeys,
                batchMemoryDirective: batchMemoryDirective
            ),
            alreadySelectedRouteItemIDs: alreadySelectedRouteItemIDs,
            alreadySelectedRouteDisplayIdentityKeys: alreadySelectedRouteDisplayIdentityKeys
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

    func makeSurveyPageSelectionAuditData(session: PersistedSurveySession, now: Date = Date()) throws -> Data {
        try encodeJSONObject(makeSurveyPageSelectionAudit(session: session, now: now))
    }

    func makeGraphNativeStarterMissionBatchResponseData(
        testerAlias: String,
        requestedMissionCount: Int = AlphaMissionGenerationConfig.requiredMissionCount,
        sourceAppVersion: String,
        sourceAppBuild: String,
        excludingRouteItemIDs: Set<String> = [],
        excludingRouteDisplayIdentityKeys: Set<String> = [],
        now: Date = Date()
    ) throws -> Data {
        let session = persistenceStore.load()
        let response = try GraphNativeStarterMissionBatchBuilder.makeResponse(
            session: session,
            itemLookup: itemLookup,
            testerAlias: testerAlias,
            requestedMissionCount: requestedMissionCount,
            sourceAppVersion: sourceAppVersion,
            sourceAppBuild: sourceAppBuild,
            excludingRouteItemIDs: excludingRouteItemIDs,
            excludingRouteDisplayIdentityKeys: excludingRouteDisplayIdentityKeys,
            now: now
        )
        return try encodeJSONObject(response)
    }

    func makeSurveyOpportunityMissionBatchResponseData(
        testerAlias: String,
        requestedMissionCount: Int = AlphaMissionGenerationConfig.requiredMissionCount,
        sourceAppVersion: String,
        sourceAppBuild: String,
        now: Date = Date()
    ) throws -> Data {
        let session = persistenceStore.load()
        let response = try SurveyOpportunityMissionBatchBuilder.makeResponse(
            session: session,
            itemLookup: itemLookup,
            testerAlias: testerAlias,
            requestedMissionCount: requestedMissionCount,
            sourceAppVersion: sourceAppVersion,
            sourceAppBuild: sourceAppBuild,
            now: now
        )
        return try encodeJSONObject(response)
    }

    private func makeSurveyEvidenceExport(session: PersistedSurveySession, now: Date) -> [String: Any] {
        let visibleLookup = visibleResponseContextLookup(session: session)
        var evidenceAtoms = [[String: Any]]()
        var quarantinedResponses = [[String: Any]]()

        for response in sortedResponses(session.responses) {
            guard let visibleContext = visibleLookup[response.itemID] else {
                quarantinedResponses.append(quarantinedResponse(response, session: session))
                continue
            }

            let item = visibleContext.item
            evidenceAtoms.append(compactDictionary([
                "evidence_atom_id": evidenceAtomID(for: response, session: session),
                "evidence_ref": evidenceRef(for: response, context: visibleContext, session: session),
                "atom_type": "survey_response",
                "atlas_ingestable": true,
                "survey_session_id": session.surveySessionID,
                "response_id": responseID(for: response, session: session),
                "survey_item_id": response.itemID,
                "item_id": response.itemID,
                "item_kind": response.itemKind.rawValue,
                "music_object_ref": musicObjectRef(for: item),
                "title": item.title,
                "artist_or_subtitle": item.subtitle,
                "state": response.state.rawValue,
                "normalized_reaction_operation": reactionOperation(for: response.state),
                "reaction_operation": reactionOperation(for: response.state),
                "evidence_strength_hint": evidenceStrengthHint(for: response.state),
                "selected_tags": response.nuances.map(\.rawValue),
                "shown_unselected_tags": shownUnselectedTags(for: response),
                "nuances": response.nuances.map(\.rawValue),
                "note": response.note.isEmpty ? nil : response.note,
                "page_context": [
                    "survey_session_id": session.surveySessionID,
                    "page_id": visibleContext.page.id,
                    "stage": visibleContext.page.kind.rawValue,
                    "page_number": visibleContext.page.pageIndex,
                    "position": visibleContext.position,
                    "page_intent": item.objective.rawValue,
                    "comparison_set_item_ids": visibleContext.page.items.map(\.id),
                    "candidate_basis": candidateBasis(for: item)
                ],
                "apple_exposure_prior": appleExposurePrior(for: item),
                "graph_refs": graphRefs(for: item),
                "source": item.source.rawValue,
                "batch_objective": item.objective.rawValue,
                "page_intent": item.objective.rawValue,
                "candidate_basis": candidateBasis(for: item),
                "updated_at": isoString(response.updatedAt),
                "confidence": "user_visible_survey_response",
                "requires_confirmation": true
            ]))
        }

        return compactDictionary([
            "schema_version": "waymark.survey_evidence_export.v0.1.app",
            "export_id": "survey_evidence_export:\(UUID().uuidString)",
            "survey_session_id": session.surveySessionID,
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
                "favorite": "preference_positive_strong",
                "like": "preference_positive",
                "fine": "waypoint_or_context",
                "not_for_me": "preference_negative",
                "dont_know": "familiarity_uncertainty"
            ],
            "evidence_strength_hint_policy": "Survey-side evidence-basis hint only; Atlas owns final confidence and role assignment.",
            "atlas_ingestable": [
                "evidence_atoms": evidenceAtoms
            ],
            "construction_only_excluded": [
                "outside_atlas_ingestion": true,
                "quarantined_response_refs": quarantinedResponses,
                "quarantine_reason_counts": quarantineReasonCounts(quarantinedResponses),
                "excluded_data_classes": [
                    "hidden_simulator_truth",
                    "hidden_archetype_tiers",
                    "hidden_corpus_reactions",
                    "generator_visible_inputs",
                    "construction_scores",
                    "ranking_internals",
                    "profile_writer_output",
                    "page_layout_mechanics_as_truth"
                ]
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
            "summary": makeSummaryDictionary(session: session).merging([
                "atlas_ingestable_response_count": evidenceAtoms.count,
                "quarantined_response_count": quarantinedResponses.count,
                "quarantine_reason_counts": quarantineReasonCounts(quarantinedResponses),
                "displayed_page_count": session.displayedPages.count
            ]) { _, new in new }
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
                "raw_apple_payload_policy": "Apple Music exposure may bias candidate selection only through sanitized candidate refs.",
                "batch_memory_policy": "Do not repeat any already_selected_route_item_ids or already_selected_display_keys supplied in prompt_context or top-level request fields. already_selected_route_display_identity_keys may appear as a legacy alias."
            ],
            "candidates": plan.candidateDictionaries
        ])
    }

    private func makeSurveyPageSelectionAudit(session: PersistedSurveySession, now: Date) -> [String: Any] {
        let responseContextLookup = visibleResponseContextLookup(session: session)
        let quarantinedResponses = sortedResponses(session.responses)
            .filter { responseContextLookup[$0.itemID] == nil }
            .map { quarantinedResponse($0, session: session) }

        let allVisibleHistory = visibleHistory(before: nil, session: session)
        let pages = session.displayedPages
            .compactMap { key, page -> (Int, [String: Any])? in
                guard let step = SurveyStep(rawValue: key) else {
                    return nil
                }

                let pageAudit = compactDictionary([
                    "page_id": page.id,
                    "step": step.rawValue,
                    "object_type": page.kind.rawValue,
                    "page_index": page.pageIndex,
                    "page_title": page.title,
                    "page_subtitle": page.subtitle,
                    "source_mix": Dictionary(grouping: page.items, by: { $0.source.rawValue }).mapValues(\.count),
                    "objective_mix": Dictionary(grouping: page.items, by: { $0.objective.rawValue }).mapValues(\.count),
                    "prior_response_summary_inputs": priorResponseSummary(before: step, session: session),
                    "prior_response_trace_inputs": priorResponseTrace(before: step, session: session),
                    "visible_history_before_page": visibleHistory(before: step, session: session),
                    "displayed_tiles": page.items.enumerated().map { index, item in
                        compactDictionary([
                            "position": index + 1,
                            "survey_item_id": item.id,
                            "typed_ref": musicObjectRef(for: item),
                            "display_label": item.subtitle.map { "\(item.title) - \($0)" } ?? item.title,
                            "title": item.title,
                            "subtitle": item.subtitle,
                            "source": item.source.rawValue,
                            "page_intent": item.objective.rawValue,
                            "candidate_basis": candidateBasis(for: item),
                            "apple_exposure_prior": appleExposurePrior(for: item),
                            "graph_refs": graphRefs(for: item),
                            "rationale": item.rationale,
                            "artwork_seed": item.artworkSeed
                        ])
                    }
                ])

                return (step.auditOrder, pageAudit)
            }
            .sorted { $0.0 < $1.0 }
            .map(\.1)

        return compactDictionary([
            "schema_version": "waymark.survey_page_selection_audit.v0.1.app",
            "audit_id": "survey_page_selection_audit:\(UUID().uuidString)",
            "survey_session_id": session.surveySessionID,
            "created_at": isoString(now),
            "producer": "MusicAtlasController",
            "redaction_level": "support_diagnostic",
            "construction_only_excluded": [
                "hidden_simulator_truth": true,
                "raw_scoring_internals": true,
                "generator_prompts": true,
                "private_construction_tags": true
            ],
            "summary": [
                "displayed_page_count": session.displayedPages.count,
                "response_count": session.responses.count,
                "quarantined_response_count": quarantinedResponses.count,
                "quarantine_reason_counts": quarantineReasonCounts(quarantinedResponses),
                "required_page_count": [
                    "artist": 4,
                    "album": 2,
                    "song": 4
                ]
            ],
            "visible_history": allVisibleHistory,
            "pages": pages,
            "quarantined_responses": quarantinedResponses
        ])
    }

    private struct VisibleResponseContext {
        let item: SurveyItem
        let page: SurveyGridPage
        let step: SurveyStep?
        let position: Int
    }

    private func visibleResponseContextLookup(session: PersistedSurveySession) -> [String: VisibleResponseContext] {
        visibleResponseContexts(before: nil, session: session).reduce(into: [String: VisibleResponseContext]()) { result, context in
            if result[context.item.id] == nil {
                result[context.item.id] = context
            }
        }
    }

    private func visibleResponseContexts(before step: SurveyStep?, session: PersistedSurveySession) -> [VisibleResponseContext] {
        session.displayedPages
            .compactMap { key, page -> (Int, SurveyStep, SurveyGridPage)? in
                guard let historyStep = SurveyStep(rawValue: key),
                      step.map({ historyStep.auditOrder < $0.auditOrder }) ?? true else {
                    return nil
                }
                return (historyStep.auditOrder, historyStep, page)
            }
            .sorted { $0.0 < $1.0 }
            .flatMap { _, historyStep, page in
                page.items.enumerated().map { index, item in
                    VisibleResponseContext(
                        item: item,
                        page: page,
                        step: historyStep,
                        position: index + 1
                    )
                }
            }
    }

    private func responseID(for response: SurveyResponse, session: PersistedSurveySession) -> String {
        "response:\(session.surveySessionID):\(response.itemID)"
    }

    private func evidenceAtomID(for response: SurveyResponse, session: PersistedSurveySession) -> String {
        "survey_response:\(session.surveySessionID):\(response.itemID)"
    }

    private func evidenceRef(
        for response: SurveyResponse,
        context: VisibleResponseContext,
        session: PersistedSurveySession
    ) -> String {
        "survey_evidence:\(session.surveySessionID):\(context.page.id):\(response.itemID)"
    }

    private func quarantinedResponse(
        _ response: SurveyResponse,
        session: PersistedSurveySession
    ) -> [String: Any] {
        let reason = quarantineReason(for: response, session: session)
        return compactDictionary([
            "response_id": responseID(for: response, session: session),
            "survey_item_id": response.itemID,
            "state": response.state.rawValue,
            "reason": reason,
            "reason_detail": quarantineReasonDetail(for: reason),
            "atlas_ingestable": false,
            "updated_at": isoString(response.updatedAt)
        ])
    }

    private func quarantineReason(for response: SurveyResponse, session: PersistedSurveySession) -> String {
        let displayedPagesForKind = session.displayedPages.values.filter { $0.kind == response.itemKind }
        if displayedPagesForKind.isEmpty {
            return "missing_displayed_page"
        }
        if itemLookup[response.itemID] == nil ||
            displayedPagesForKind.allSatisfy({ page in page.items.contains(where: { $0.id == response.itemID }) == false }) {
            return "missing_tile_or_ref"
        }
        return "schema_mismatch"
    }

    private func quarantineReasonDetail(for reason: String) -> String {
        switch reason {
        case "missing_displayed_page":
            return "No displayed page for this response stage was present in persisted Survey page history."
        case "missing_tile_or_ref":
            return "The response did not resolve to a visible tile/ref in persisted Survey page history."
        case "invalid_response_state":
            return "The response state was outside the five-state Survey enum."
        case "duplicate_response":
            return "The response duplicated an existing visible response ref."
        case "schema_mismatch":
            return "The response shape did not match the Survey Evidence Export v0.1 app contract."
        case "non_visible_construction_data":
            return "The response represented construction/debug state rather than a visible user-facing tile."
        case "apple_only_unmatched_object":
            return "The object came from Apple context but did not resolve to a visible Survey tile/ref."
        default:
            return "Unclassified quarantine reason."
        }
    }

    private func quarantineReasonCounts(_ quarantinedResponses: [[String: Any]]) -> [String: Int] {
        quarantinedResponses.reduce(into: [String: Int]()) { counts, response in
            let reason = response["reason"] as? String ?? "schema_mismatch"
            counts[reason, default: 0] += 1
        }
    }

    private func priorResponseSummary(before step: SurveyStep, session: PersistedSurveySession) -> [String: Any] {
        let priorItemIDs = Set(visibleHistory(before: step, session: session).flatMap { page -> [String] in
            page["tile_ids"] as? [String] ?? []
        })
        let priorResponses = session.responses.values.filter { priorItemIDs.contains($0.itemID) }
        return [
            "response_count": priorResponses.count,
            "state_counts": Dictionary(grouping: priorResponses, by: { $0.state.rawValue }).mapValues(\.count),
            "positive_count": priorResponses.filter { $0.state == .favorite || $0.state == .like }.count,
            "negative_count": priorResponses.filter { $0.state == .notForMe }.count,
            "unknown_count": priorResponses.filter { $0.state == .dontKnow }.count
        ]
    }

    private func priorResponseTrace(before step: SurveyStep, session: PersistedSurveySession) -> [[String: Any]] {
        visibleResponseContexts(before: step, session: session).compactMap { context in
            guard let response = session.responses[context.item.id] else {
                return nil
            }

            return compactDictionary([
                "response_id": responseID(for: response, session: session),
                "survey_item_id": response.itemID,
                "item_kind": response.itemKind.rawValue,
                "title": context.item.title,
                "subtitle": context.item.subtitle,
                "state": response.state.rawValue,
                "selected_tags": response.nuances.map(\.rawValue),
                "note_present": response.note.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty == false,
                "source_page_id": context.page.id,
                "source_step": context.step?.rawValue,
                "source_page_number": context.page.pageIndex,
                "source_position": context.position,
                "updated_at": isoString(response.updatedAt)
            ])
        }
    }

    private func visibleHistory(before step: SurveyStep?, session: PersistedSurveySession) -> [[String: Any]] {
        session.displayedPages
            .compactMap { key, page -> (Int, [String: Any])? in
                guard let historyStep = SurveyStep(rawValue: key),
                      step.map({ historyStep.auditOrder < $0.auditOrder }) ?? true else {
                    return nil
                }
                return (
                    historyStep.auditOrder,
                    compactDictionary([
                        "step": historyStep.rawValue,
                        "page_id": page.id,
                        "object_type": page.kind.rawValue,
                        "page_index": page.pageIndex,
                        "tile_ids": page.items.map(\.id)
                    ])
                )
            }
            .sorted { $0.0 < $1.0 }
            .map(\.1)
    }

    private func shownUnselectedTags(for response: SurveyResponse) -> [String] {
        guard !response.nuances.isEmpty else {
            return []
        }
        let selected = Set(response.nuances)
        return SurveyNuance.allCases
            .filter { !selected.contains($0) }
            .map(\.rawValue)
    }

    private func candidateBasis(for item: SurveyItem) -> [String] {
        [
            item.source.rawValue,
            item.objective.rawValue,
            "canonical_graph_runtime_surface"
        ]
    }

    private func appleExposurePrior(for item: SurveyItem) -> [String: Any] {
        [
            "prior_type": "apple_exposure_prior",
            "taste_truth": false,
            "exposure_or_familiarity_only": true,
            "present_on_visible_tile": item.source == .appleMusicDerived,
            "source": item.source.rawValue
        ]
    }

    private func graphRefs(for item: SurveyItem) -> [String: Any] {
        let canonicalID = canonicalID(from: item)
        return compactDictionary([
            "ref_source": canonicalID == nil ? "app_survey_fixture_or_unresolved" : "canonical_graph",
            "canonical_artist_id": item.kind == .artist ? canonicalID : nil,
            "canonical_album_id": item.kind == .album ? canonicalID : nil,
            "canonical_song_recording_id": item.kind == .song ? canonicalID : nil,
            "resolution_state": canonicalID == nil ? "unresolved" : "resolved"
        ])
    }

    private func musicObjectRef(for item: SurveyItem) -> [String: Any] {
        let canonicalID = canonicalID(from: item)
        return compactDictionary([
            "object_type": musicObjectType(for: item.kind),
            "ref_source": canonicalID == nil ? "app_survey_fixture_or_unresolved" : "canonical_graph",
            "canonical_artist_id": item.kind == .artist ? canonicalID : nil,
            "canonical_album_id": item.kind == .album ? canonicalID : nil,
            "canonical_song_recording_id": item.kind == .song ? canonicalID : nil,
            "display_name": item.title,
            "artist_display_name": item.subtitle,
            "resolution_state": canonicalID == nil ? "unresolved" : "resolved"
        ])
    }

    private func canonicalID(from item: SurveyItem) -> String? {
        let prefixes = [
            "ALPHA_ARTIST_",
            "ALPHA_ALBUM_",
            "ALPHA_SONG_"
        ]
        guard let prefix = prefixes.first(where: { item.id.hasPrefix($0) }) else {
            return nil
        }
        return String(item.id.dropFirst(prefix.count))
    }

    private func musicObjectType(for kind: SurveyItemKind) -> String {
        switch kind {
        case .artist:
            return "artist"
        case .album:
            return "album"
        case .song:
            return "song_recording"
        }
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
            return "preference_positive_strong"
        case .like:
            return "preference_positive"
        case .fine:
            return "waypoint_or_context"
        case .notForMe:
            return "preference_negative"
        case .dontKnow:
            return "familiarity_uncertainty"
        }
    }

    private func evidenceStrengthHint(for state: SurveySignalState) -> Double {
        switch state {
        case .favorite:
            return 0.88
        case .like:
            return 0.68
        case .fine:
            return 0.34
        case .notForMe:
            return 0.58
        case .dontKnow:
            return 0.12
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

private enum SurveyOpportunityMissionBatchBuilder {
    static func makeResponse(
        session: PersistedSurveySession,
        itemLookup: [String: SurveyItem],
        testerAlias: String,
        requestedMissionCount: Int,
        sourceAppVersion: String,
        sourceAppBuild: String,
        now: Date
    ) throws -> [String: Any] {
        let songs = try GraphSongRecord.load()
        let profile = GraphSurveySignalProfile(session: session, itemLookup: itemLookup, songs: songs)
        let catalogIndex = CanonicalAppleMusicCatalogIndex.loadFromBundle()
        var usedCanonicalIDs = Set<String>()
        var usedRouteItemIDs = Set<String>()
        var usedRouteDisplayIdentityKeys = Set<String>()
        let specs = missionSpecs(profile: profile)
        let boundedMissionCount = max(0, min(requestedMissionCount, specs.count))
        var importIssues = [String]()
        var missions = [[String: Any]]()
        var missionAudits = [[String: Any]]()
        let runID = "local_survey_opportunity_selection_\(UUID().uuidString)"

        for (index, spec) in specs.prefix(boundedMissionCount).enumerated() {
            let candidateScreen = candidateScreenAudit(
                for: spec,
                profile: profile,
                songs: songs,
                catalogIndex: catalogIndex,
                usedCanonicalIDs: usedCanonicalIDs,
                usedRouteItemIDs: usedRouteItemIDs,
                usedRouteDisplayIdentityKeys: usedRouteDisplayIdentityKeys,
                now: now
            )
            let selectedSongs = selectSongs(
                for: spec,
                profile: profile,
                songs: songs,
                catalogIndex: catalogIndex,
                usedCanonicalIDs: &usedCanonicalIDs,
                usedRouteItemIDs: &usedRouteItemIDs,
                usedRouteDisplayIdentityKeys: &usedRouteDisplayIdentityKeys,
                now: now
            )
            guard selectedSongs.count == spec.routeRoles.count else {
                importIssues.append("\(spec.idSuffix) resolved \(selectedSongs.count) of \(spec.routeRoles.count) required route items")
                missionAudits.append(missionSelectionAudit(
                    spec: spec,
                    missionIndex: index + 1,
                    status: "route_item_shortfall",
                    selectedSongs: selectedSongs,
                    candidateScreen: candidateScreen,
                    profile: profile,
                    catalogIndex: catalogIndex,
                    now: now
                ))
                continue
            }
            let mission = appMission(
                spec: spec,
                missionIndex: index + 1,
                songs: selectedSongs,
                profile: profile,
                testerAlias: testerAlias,
                sourceAppVersion: sourceAppVersion,
                sourceAppBuild: sourceAppBuild,
                catalogIndex: catalogIndex,
                now: now
            )
            missions.append(mission)
            missionAudits.append(missionSelectionAudit(
                spec: spec,
                missionIndex: index + 1,
                status: "selected_for_app_import",
                selectedSongs: selectedSongs,
                candidateScreen: candidateScreen,
                profile: profile,
                catalogIndex: catalogIndex,
                now: now
            ))
        }

        let status = missions.count == boundedMissionCount ? "app_import_candidate" : "blocked"
        let validationErrors = status == "app_import_candidate"
            ? []
            : ["survey_opportunity_builder_returned_\(missions.count)_of_\(boundedMissionCount)_requested_missions"] + importIssues
        let routeItemCount = missions.compactMap { ($0["items"] as? [[String: Any]])?.count }.reduce(0, +)

        return [
            "run_id": runID,
            "status": status,
            "app_import_status": status,
            "prompt_version": "none",
            "model": "none",
            "adapter_version": "local_survey_opportunity_selection_v0_1",
            "mission_output_schema_version": "mission_opportunity_selection_v0_1_to_mission_v0_2",
            "app_mission_schema_version": "mission.v0.2",
            "generation": [
                "schema_version": "cartenza.local_survey_opportunity_selection.v0.1",
                "tester_alias": testerAlias,
                "survey_session_id": session.surveySessionID,
                "requested_mission_count": boundedMissionCount,
                "returned_mission_count": missions.count,
                "route_policy": "survey_visible_atoms_to_canonical_graph_songs_with_cached_apple_music_ids",
                "openai_call_skipped": true,
                "supabase_generation_skipped": true,
                "resolved_route_required": true,
                "survey_response_count": session.responses.count,
                "positive_signal_count": profile.positiveSignalCount,
                "negative_signal_count": profile.negativeSignalCount,
                "fine_signal_count": profile.fineSignalCount,
                "unknown_signal_count": profile.unknownSignalCount,
                "top_archetype_ids": profile.topArchetypeIDs.prefix(6).map { $0 },
                "top_family_ids": profile.topFamilyIDs.prefix(6).map { $0 },
                "negative_archetype_ids": profile.negativeArchetypeIDs.prefix(6).map { $0 },
                "negative_family_ids": profile.negativeFamilyIDs.prefix(6).map { $0 }
            ],
            "selection_audit": [
                "schema_version": "cartenza.local_mission_selection_audit.v0.1",
                "run_id": runID,
                "audit_id": "mission_selection_audit:\(runID)",
                "created_at": isoString(now),
                "tester_alias": testerAlias,
                "survey_session_id": session.surveySessionID,
                "source_app_version": sourceAppVersion,
                "source_app_build": sourceAppBuild,
                "adapter_version": "local_survey_opportunity_selection_v0_1",
                "requested_mission_count": boundedMissionCount,
                "selected_mission_count": missions.count,
                "selected_route_item_count": routeItemCount,
                "no_openai_call": true,
                "no_supabase_generation_call": true,
                "no_static_public_profile_fixture": true,
                "source_inputs": [
                    "survey_response_count": session.responses.count,
                    "displayed_page_count": session.displayedPages.count,
                    "canonical_song_graph_resource": "canonical_song_recordings.json",
                    "apple_music_index_resource": "canonical_apple_music_catalog_index_v1.json"
                ],
                "profile_summary": [
                    "positive_signal_count": profile.positiveSignalCount,
                    "negative_signal_count": profile.negativeSignalCount,
                    "fine_signal_count": profile.fineSignalCount,
                    "unknown_signal_count": profile.unknownSignalCount,
                    "top_archetype_ids": profile.topArchetypeIDs.prefix(8).map { $0 },
                    "top_family_ids": profile.topFamilyIDs.prefix(8).map { $0 },
                    "negative_archetype_ids": profile.negativeArchetypeIDs.prefix(8).map { $0 },
                    "negative_family_ids": profile.negativeFamilyIDs.prefix(8).map { $0 }
                ],
                "eligibility_policy": [
                    "visible_survey_song_reuse_blocked": true,
                    "disliked_artist_blocked": true,
                    "disliked_song_blocked": true,
                    "negative_graph_lane_filter_enabled": true,
                    "cached_apple_music_resolution_required": true,
                    "duplicate_canonical_song_blocked_across_batch": true,
                    "duplicate_route_display_identity_blocked_across_batch": true,
                    "runtime_large_model_generation_allowed": false
                ],
                "missions": missionAudits
            ],
            "app_missions": missions,
            "alpha_import_policy": [
                "policy": "survey_opportunity_selection_local_alpha",
                "app_import_status": status,
                "app_import_allowed_for_trusted_alpha": status == "app_import_candidate",
                "app_missions_returned": status == "app_import_candidate",
                "returned_app_mission_count": missions.count,
                "no_static_public_profile_fixture": true,
                "no_openai_call": true,
                "survey_visible_song_reuse_blocked": true,
                "negative_artist_and_negative_graph_lane_filter_enabled": true
            ],
            "validation": [
                "generation": [
                    "valid": status == "app_import_candidate",
                    "errors": validationErrors
                ],
                "route_identity": [
                    "route_item_count": routeItemCount,
                    "survey_visible_song_reuse_blocked": true,
                    "source": "local_survey_opportunity_selection"
                ],
                "app_mission": [
                    "valid": status == "app_import_candidate",
                    "errors": validationErrors
                ]
            ],
            "usage": [
                "input_tokens": 0,
                "cached_input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0
            ],
            "latency_ms": 0
        ]
    }

    private static func missionSpecs(profile: GraphSurveySignalProfile) -> [SurveyOpportunityMissionSpec] {
        let archetypes = profile.topArchetypeIDs.isEmpty ? ["016", "033", "047", "087"] : profile.topArchetypeIDs
        let families = profile.topFamilyIDs.isEmpty ? [3, 5, 7, 11] : profile.topFamilyIDs
        let primaryArchetype = archetypes[safe: 0]
        let secondaryArchetype = archetypes[safe: 1] ?? primaryArchetype
        let tertiaryArchetype = archetypes[safe: 2] ?? secondaryArchetype
        let primaryFamily = families[safe: 0]
        let secondaryFamily = families[safe: 1] ?? primaryFamily
        let tertiaryFamily = families[safe: 2] ?? secondaryFamily
        let frontierArchetype = profile.frontierArchetypeID ?? tertiaryArchetype ?? primaryArchetype
        let frontierFamily = profile.frontierFamilyID ?? tertiaryFamily ?? primaryFamily
        let boundaryArchetype = profile.negativeArchetypeIDs.first { $0 != primaryArchetype } ?? secondaryArchetype
        let boundaryFamily = profile.negativeFamilyIDs.first { $0 != primaryFamily } ?? secondaryFamily
        let signalSummary = "\(profile.positiveSignalCount) positive, \(profile.fineSignalCount) ok/waypoint, \(profile.negativeSignalCount) negative"

        return [
            SurveyOpportunityMissionSpec(
                idSuffix: "DEPTH_01",
                missionType: .archetypeDepthTest,
                title: "Survey Depth: Strongest Signal",
                alphaMissionArchetype: "Nearby Road",
                riskLevel: "low",
                primaryArchetypeID: primaryArchetype,
                secondaryArchetypeID: nil,
                primaryFamilyID: primaryFamily,
                secondaryFamilyID: nil,
                routeRoles: [.anchor, .probe, .probe, .comparator, .control, .probe],
                brief: "Test whether the strongest Survey signal survives six resolved listening checks.",
                objective: "Confirm whether the first strong Survey lane is durable beyond a few visible grid taps.",
                whyNow: "Built from this Survey session's \(signalSummary) signals. Cartenza is testing the strongest graph lane without reusing songs already rated in the Survey."
            ),
            SurveyOpportunityMissionSpec(
                idSuffix: "DEPTH_02",
                missionType: .archetypeDepthTest,
                title: "Survey Depth: Second Signal",
                alphaMissionArchetype: "Nearby Road",
                riskLevel: "low",
                primaryArchetypeID: secondaryArchetype,
                secondaryArchetypeID: nil,
                primaryFamilyID: secondaryFamily,
                secondaryFamilyID: nil,
                routeRoles: [.anchor, .probe, .probe, .comparator, .control, .probe],
                brief: "Check whether a second Survey-supported lane is real or just familiar surface area.",
                objective: "Separate a secondary positive signal from one-object familiarity.",
                whyNow: "Built from the next strongest Survey lane after exact song repeats and negative graph lanes were filtered."
            ),
            SurveyOpportunityMissionSpec(
                idSuffix: "BRIDGE_01",
                missionType: .bridgeTest,
                title: "Bridge Check: Nearby Road",
                alphaMissionArchetype: "Frontier Route",
                riskLevel: "medium",
                primaryArchetypeID: primaryArchetype,
                secondaryArchetypeID: frontierArchetype,
                primaryFamilyID: primaryFamily,
                secondaryFamilyID: frontierFamily,
                routeRoles: [.anchor, .bridge, .bridge, .probe, .comparator, .control],
                brief: "Test whether a Survey-supported source lane can bridge into nearby unresolved territory.",
                objective: "Find out whether a plausible nearby road connects to the early Survey signal.",
                whyNow: "The Survey has enough positive evidence to try one bounded bridge while avoiding explicit no-signals."
            ),
            SurveyOpportunityMissionSpec(
                idSuffix: "BOUNDARY_01",
                missionType: .boundaryTest,
                title: "Boundary Check: Clean Edge",
                alphaMissionArchetype: "Dead End Check",
                riskLevel: "medium",
                primaryArchetypeID: primaryArchetype,
                secondaryArchetypeID: boundaryArchetype,
                primaryFamilyID: primaryFamily,
                secondaryFamilyID: boundaryFamily,
                routeRoles: [.anchor, .anchor, .boundary, .comparator, .control, .probe],
                brief: "Find the edge between what looked promising and what the Survey pushed away from.",
                objective: "Use a bounded contrast to learn from avoidance without turning the route punitive.",
                whyNow: "The Survey contains \(profile.negativeSignalCount) negative signals, so this route tests the edge indirectly while filtering rated songs and disliked artists."
            ),
            SurveyOpportunityMissionSpec(
                idSuffix: "CONTEXT_01",
                missionType: .contextDependenceTest,
                title: "Context Check: Same Signal, Different Frame",
                alphaMissionArchetype: "Nearby Road",
                riskLevel: "medium",
                primaryArchetypeID: secondaryArchetype ?? primaryArchetype,
                secondaryArchetypeID: tertiaryArchetype,
                primaryFamilyID: secondaryFamily ?? primaryFamily,
                secondaryFamilyID: tertiaryFamily,
                routeRoles: [.anchor, .context, .context, .comparator, .control, .probe],
                brief: "Test whether response changes with framing, role, and neighboring context.",
                objective: "Clarify whether ok/waypoint evidence is neutral, contextual, or a hidden positive.",
                whyNow: "The Survey has \(profile.fineSignalCount) ok/waypoint signals, enough to run a context-sensitive check without claiming a promoted Atlas verdict."
            ),
            SurveyOpportunityMissionSpec(
                idSuffix: "GATEWAY_01",
                missionType: .gatewayTest,
                title: "Gateway Check: Low-Risk Frontier",
                alphaMissionArchetype: "Start Here",
                riskLevel: "low",
                primaryArchetypeID: frontierArchetype,
                secondaryArchetypeID: primaryArchetype,
                primaryFamilyID: frontierFamily,
                secondaryFamilyID: primaryFamily,
                routeRoles: [.anchor, .bridge, .probe, .comparator, .control, .probe],
                brief: "Try a low-risk doorway into under-tested graph territory.",
                objective: "Look for useful new waypoints without using the static public-profile smoke pack.",
                whyNow: "After the required Survey, Cartenza can test one nearby frontier using only resolved canonical tracks and visible user responses."
            )
        ]
    }

    private static func candidateScreenAudit(
        for spec: SurveyOpportunityMissionSpec,
        profile: GraphSurveySignalProfile,
        songs: [GraphSongRecord],
        catalogIndex: CanonicalAppleMusicCatalogIndex,
        usedCanonicalIDs: Set<String>,
        usedRouteItemIDs: Set<String>,
        usedRouteDisplayIdentityKeys: Set<String>,
        now: Date
    ) -> [String: Any] {
        var alreadyUsedCanonicalCount = 0
        var duplicateRouteItemIDCount = 0
        var duplicateDisplayIdentityCount = 0
        var excludedBySurveyOrNegativeLaneCount = 0
        var missingCachedAppleMusicResolutionCount = 0
        var focusedEligible = [(song: GraphSongRecord, resolution: AppleMusicResolution)]()
        var fallbackEligible = [(song: GraphSongRecord, resolution: AppleMusicResolution)]()

        for song in songs {
            if usedCanonicalIDs.contains(song.canonicalSongRecordingID) {
                alreadyUsedCanonicalCount += 1
                continue
            }
            if usedRouteItemIDs.contains(itemID(for: song, spec: spec, sequence: 1)) {
                duplicateRouteItemIDCount += 1
                continue
            }
            if usedRouteDisplayIdentityKeys.contains(routeDisplayIdentityKey(for: song)) {
                duplicateDisplayIdentityCount += 1
                continue
            }
            if profile.isExcluded(song) {
                excludedBySurveyOrNegativeLaneCount += 1
                continue
            }
            guard let resolution = indexedResolution(
                for: song,
                spec: spec,
                sequence: 1,
                role: .probe,
                catalogIndex: catalogIndex,
                now: now
            ) else {
                missingCachedAppleMusicResolutionCount += 1
                continue
            }

            if spec.matches(song) {
                focusedEligible.append((song, resolution))
            } else {
                fallbackEligible.append((song, resolution))
            }
        }

        let eligibleCount = focusedEligible.count + fallbackEligible.count
        let topFocused = rankedAuditCandidates(focusedEligible, spec: spec, profile: profile)
            .prefix(12)
            .map { candidateAuditSummary(song: $0.song, spec: spec, profile: profile, resolution: $0.resolution) }
        let topFallback = rankedAuditCandidates(fallbackEligible, spec: spec, profile: profile)
            .prefix(8)
            .map { candidateAuditSummary(song: $0.song, spec: spec, profile: profile, resolution: $0.resolution) }

        return [
            "candidate_count": songs.count,
            "eligible_count": eligibleCount,
            "focused_eligible_count": focusedEligible.count,
            "fallback_eligible_count": fallbackEligible.count,
            "rejection_reason_counts": [
                "already_used_canonical_song": alreadyUsedCanonicalCount,
                "duplicate_route_item_id": duplicateRouteItemIDCount,
                "duplicate_route_display_identity": duplicateDisplayIdentityCount,
                "excluded_by_visible_survey_or_negative_graph_lane": excludedBySurveyOrNegativeLaneCount,
                "missing_cached_apple_music_resolution": missingCachedAppleMusicResolutionCount
            ],
            "top_focused_candidates": Array(topFocused),
            "top_fallback_candidates": Array(topFallback)
        ]
    }

    private static func missionSelectionAudit(
        spec: SurveyOpportunityMissionSpec,
        missionIndex: Int,
        status: String,
        selectedSongs: [GraphSongRecord],
        candidateScreen: [String: Any],
        profile: GraphSurveySignalProfile,
        catalogIndex: CanonicalAppleMusicCatalogIndex,
        now: Date
    ) -> [String: Any] {
        compactDictionary([
            "mission_index": missionIndex,
            "mission_id": missionID(for: spec),
            "mission_type": spec.missionType.rawValue,
            "title": spec.title,
            "status": status,
            "risk_level": spec.riskLevel,
            "alpha_mission_archetype": spec.alphaMissionArchetype,
            "primary_archetype_id": spec.primaryArchetypeID,
            "secondary_archetype_id": spec.secondaryArchetypeID,
            "primary_family_id": spec.primaryFamilyID,
            "secondary_family_id": spec.secondaryFamilyID,
            "route_roles": spec.routeRoles.map(\.rawValue),
            "required_route_item_count": spec.routeRoles.count,
            "selected_route_item_count": selectedSongs.count,
            "target_object_ids": targetObjectIDs(for: spec),
            "graph_context_refs": graphContextRefs(for: spec),
            "candidate_screen": candidateScreen,
            "selected_route_items": selectedSongs.enumerated().map { index, song in
                selectedRouteItemAudit(
                    song: song,
                    sequence: index + 1,
                    role: spec.routeRoles[safe: index] ?? .probe,
                    spec: spec,
                    profile: profile,
                    catalogIndex: catalogIndex,
                    now: now
                )
            }
        ])
    }

    private static func selectedRouteItemAudit(
        song: GraphSongRecord,
        sequence: Int,
        role: AlphaRouteItemRole,
        spec: SurveyOpportunityMissionSpec,
        profile: GraphSurveySignalProfile,
        catalogIndex: CanonicalAppleMusicCatalogIndex,
        now: Date
    ) -> [String: Any] {
        let resolution = indexedResolution(
            for: song,
            spec: spec,
            sequence: sequence,
            role: role,
            catalogIndex: catalogIndex,
            now: now
        )
        return compactDictionary([
            "sequence": sequence,
            "role": role.rawValue,
            "item_id": itemID(for: song, spec: spec, sequence: sequence),
            "candidate_id": "canonical_song_recording:\(song.canonicalSongRecordingID)",
            "canonical_song_recording_id": song.canonicalSongRecordingID,
            "route_candidate_key": "survey_opportunity:\(spec.missionType.rawValue):\(song.canonicalSongRecordingID)",
            "route_batch_dedupe_key": "song_recording:\(song.canonicalSongRecordingID)",
            "route_display_identity_key": routeDisplayIdentityKey(for: song),
            "title": song.displayName,
            "artist": song.primaryArtist,
            "year": song.releaseYears.first,
            "matches_mission_focus": spec.matches(song),
            "score": score(song, spec: spec, profile: profile),
            "positive_support": profile.positiveSupport(for: song),
            "negative_pressure": profile.negativePressure(for: song),
            "archetype_ids": song.archetypeIDs,
            "family_numbers": song.familyNumbers,
            "graph_roles": song.roles,
            "best_recognition_tier": song.bestRecognitionTier,
            "best_survey_tier": song.bestSurveyTier,
            "apple_music": resolutionDictionary(resolution),
            "selection_guards": [
                "visible_survey_song_reuse_blocked": true,
                "disliked_artist_blocked": true,
                "negative_graph_lane_filter_enabled": true,
                "cached_apple_music_resolution_required": true
            ]
        ])
    }

    private static func candidateAuditSummary(
        song: GraphSongRecord,
        spec: SurveyOpportunityMissionSpec,
        profile: GraphSurveySignalProfile,
        resolution: AppleMusicResolution
    ) -> [String: Any] {
        compactDictionary([
            "canonical_song_recording_id": song.canonicalSongRecordingID,
            "title": song.displayName,
            "artist": song.primaryArtist,
            "route_display_identity_key": routeDisplayIdentityKey(for: song),
            "matches_mission_focus": spec.matches(song),
            "score": score(song, spec: spec, profile: profile),
            "positive_support": profile.positiveSupport(for: song),
            "negative_pressure": profile.negativePressure(for: song),
            "archetype_ids": song.archetypeIDs,
            "family_numbers": song.familyNumbers,
            "apple_catalog_id": resolution.catalogID,
            "apple_catalog_url": resolution.catalogURL?.absoluteString
        ])
    }

    private static func rankedAuditCandidates(
        _ candidates: [(song: GraphSongRecord, resolution: AppleMusicResolution)],
        spec: SurveyOpportunityMissionSpec,
        profile: GraphSurveySignalProfile
    ) -> [(song: GraphSongRecord, resolution: AppleMusicResolution)] {
        candidates.sorted { lhs, rhs in
            let leftScore = score(lhs.song, spec: spec, profile: profile)
            let rightScore = score(rhs.song, spec: spec, profile: profile)
            if leftScore != rightScore {
                return leftScore > rightScore
            }
            return lhs.song.canonicalSongRecordingID < rhs.song.canonicalSongRecordingID
        }
    }

    private static func selectSongs(
        for spec: SurveyOpportunityMissionSpec,
        profile: GraphSurveySignalProfile,
        songs: [GraphSongRecord],
        catalogIndex: CanonicalAppleMusicCatalogIndex,
        usedCanonicalIDs: inout Set<String>,
        usedRouteItemIDs: inout Set<String>,
        usedRouteDisplayIdentityKeys: inout Set<String>,
        now: Date
    ) -> [GraphSongRecord] {
        let desiredCount = spec.routeRoles.count
        var selected = [GraphSongRecord]()
        let eligible = songs.filter { song in
            !usedCanonicalIDs.contains(song.canonicalSongRecordingID) &&
                !profile.isExcluded(song) &&
                !usedRouteItemIDs.contains(itemID(for: song, spec: spec, sequence: 1)) &&
                !usedRouteDisplayIdentityKeys.contains(routeDisplayIdentityKey(for: song)) &&
                indexedResolution(for: song, spec: spec, sequence: 1, role: .probe, catalogIndex: catalogIndex, now: now) != nil
        }
        let focused = eligible.filter { spec.matches($0) }
        appendSongs(
            from: focused.isEmpty ? eligible : focused,
            spec: spec,
            profile: profile,
            catalogIndex: catalogIndex,
            desiredTotalCount: desiredCount,
            selected: &selected,
            usedCanonicalIDs: &usedCanonicalIDs,
            usedRouteItemIDs: &usedRouteItemIDs,
            usedRouteDisplayIdentityKeys: &usedRouteDisplayIdentityKeys,
            now: now
        )

        if selected.count < desiredCount {
            appendSongs(
                from: eligible,
                spec: spec,
                profile: profile,
                catalogIndex: catalogIndex,
                desiredTotalCount: desiredCount,
                selected: &selected,
                usedCanonicalIDs: &usedCanonicalIDs,
                usedRouteItemIDs: &usedRouteItemIDs,
                usedRouteDisplayIdentityKeys: &usedRouteDisplayIdentityKeys,
                now: now
            )
        }

        return selected
    }

    private static func appendSongs(
        from songs: [GraphSongRecord],
        spec: SurveyOpportunityMissionSpec,
        profile: GraphSurveySignalProfile,
        catalogIndex: CanonicalAppleMusicCatalogIndex,
        desiredTotalCount: Int,
        selected: inout [GraphSongRecord],
        usedCanonicalIDs: inout Set<String>,
        usedRouteItemIDs: inout Set<String>,
        usedRouteDisplayIdentityKeys: inout Set<String>,
        now: Date
    ) {
        guard selected.count < desiredTotalCount else {
            return
        }

        let rankedSongs = songs.sorted { lhs, rhs in
            let leftScore = score(lhs, spec: spec, profile: profile)
            let rightScore = score(rhs, spec: spec, profile: profile)
            if leftScore != rightScore {
                return leftScore > rightScore
            }
            return lhs.canonicalSongRecordingID < rhs.canonicalSongRecordingID
        }

        for song in rankedSongs {
            guard selected.count < desiredTotalCount else {
                break
            }
            let sequence = selected.count + 1
            let role = spec.routeRoles[safe: selected.count] ?? .probe
            let itemID = itemID(for: song, spec: spec, sequence: sequence)
            let displayKey = routeDisplayIdentityKey(for: song)
            guard !usedCanonicalIDs.contains(song.canonicalSongRecordingID),
                  !usedRouteItemIDs.contains(itemID),
                  !usedRouteDisplayIdentityKeys.contains(displayKey),
                  !selected.contains(where: { $0.canonicalSongRecordingID == song.canonicalSongRecordingID }),
                  indexedResolution(for: song, spec: spec, sequence: sequence, role: role, catalogIndex: catalogIndex, now: now) != nil else {
                continue
            }
            selected.append(song)
            usedCanonicalIDs.insert(song.canonicalSongRecordingID)
            usedRouteItemIDs.insert(itemID)
            usedRouteDisplayIdentityKeys.insert(displayKey)
        }
    }

    private static func score(_ song: GraphSongRecord, spec: SurveyOpportunityMissionSpec, profile: GraphSurveySignalProfile) -> Double {
        var score = 0.0
        if let primaryArchetypeID = spec.primaryArchetypeID,
           song.archetypeIDs.contains(primaryArchetypeID) {
            score += 34
        }
        if let secondaryArchetypeID = spec.secondaryArchetypeID,
           song.archetypeIDs.contains(secondaryArchetypeID) {
            score += spec.missionType == .bridgeTest ? 24 : 12
        }
        if let primaryFamilyID = spec.primaryFamilyID,
           song.familyNumbers.contains(primaryFamilyID) {
            score += 22
        }
        if let secondaryFamilyID = spec.secondaryFamilyID,
           song.familyNumbers.contains(secondaryFamilyID) {
            score += spec.missionType == .bridgeTest ? 16 : 8
        }
        score += song.roles.contains("anchor") ? 7 : 0
        score += song.roles.contains("gateway") ? 5 : 0
        score += recognitionScore(song.bestRecognitionTier)
        score += surveyTierScore(song.bestSurveyTier)
        score += profile.positiveSupport(for: song) * 2.5
        score -= profile.negativePressure(for: song) * 3.5
        return score
    }

    private static func appMission(
        spec: SurveyOpportunityMissionSpec,
        missionIndex: Int,
        songs: [GraphSongRecord],
        profile: GraphSurveySignalProfile,
        testerAlias: String,
        sourceAppVersion: String,
        sourceAppBuild: String,
        catalogIndex: CanonicalAppleMusicCatalogIndex,
        now: Date
    ) -> [String: Any] {
        [
            "schema_version": "mission.v0.2",
            "mission_id": missionID(for: spec),
            "mission_title": spec.title,
            "mission_version": "survey_opportunity_v0.1",
            "created_at": isoString(now),
            "mission_type": spec.missionType.rawValue,
            "recommended_format": "play_items_in_order",
            "hypothesis": spec.objective,
            "inflation_warning": "Survey-derived Alpha mission. This is a deterministic opportunity-selection handoff, not a promoted Atlas verdict.",
            "success_bar": [
                "minimum_items_to_resolve": spec.routeRoles.count,
                "minimum_items_to_play": spec.routeRoles.count,
                "minimum_reactions_required": spec.routeRoles.count,
                "requires_physical_iphone": true,
                "notes": "Resolved from bundled canonical Apple Music index; no OpenAI or Supabase generation call."
            ],
            "run_instructions": [
                "listen_in_order": true,
                "shuffle_allowed": false,
                "raw_text": "Listen in order and react to each item. The route is testing an opportunity from Survey evidence."
            ],
            "post_run_inference_rules": [
                [
                    "trigger": "After completion, review reactions, skips, wrong-version flags, and notes.",
                    "inference": "Treat results as provisional mission evidence for Alpha review."
                ]
            ],
            "items": songs.enumerated().map { index, song in
                appMissionItem(
                    song: song,
                    sequence: index + 1,
                    role: spec.routeRoles[safe: index] ?? .probe,
                    spec: spec,
                    catalogIndex: catalogIndex,
                    now: now
                )
            },
            "alpha_app_import_status": AlphaAppImportStatus.appImportReady.rawValue,
            "alpha_mission_archetype": spec.alphaMissionArchetype,
            "brief": spec.brief,
            "why_this_mission_now": spec.whyNow,
            "risk_level": spec.riskLevel,
            "source_trace_summary": "local_survey_opportunity_selection_v0_1; tester=\(testerAlias); app=\(sourceAppVersion)(\(sourceAppBuild)); positives=\(profile.positiveSignalCount); negatives=\(profile.negativeSignalCount); no_static_public_profile_fixture=true"
        ]
    }

    private static func missionID(for spec: SurveyOpportunityMissionSpec) -> String {
        "MIS_ALPHA_SURVEY_OPPORTUNITY_\(spec.idSuffix)"
    }

    private static func appMissionItem(
        song: GraphSongRecord,
        sequence: Int,
        role: AlphaRouteItemRole,
        spec: SurveyOpportunityMissionSpec,
        catalogIndex: CanonicalAppleMusicCatalogIndex,
        now: Date
    ) -> [String: Any] {
        let signal = expectedSignal(role: role, spec: spec)
        let resolution = indexedResolution(
            for: song,
            spec: spec,
            sequence: sequence,
            role: role,
            catalogIndex: catalogIndex,
            now: now
        )
        var output: [String: Any] = [
            "item_id": itemID(for: song, spec: spec, sequence: sequence),
            "candidate_id": "canonical_song_recording:\(song.canonicalSongRecordingID)",
            "route_candidate_key": "survey_opportunity:\(spec.missionType.rawValue):\(song.canonicalSongRecordingID)",
            "route_batch_dedupe_key": "song_recording:\(song.canonicalSongRecordingID)",
            "route_display_identity_key": routeDisplayIdentityKey(for: song),
            "sequence": sequence,
            "item_type": "track",
            "artist": song.primaryArtist,
            "title": song.displayName,
            "why_included": whyIncluded(song: song, role: role, spec: spec),
            "expected_test_signal": signal,
            "player_card": [
                "flip_side": [
                    "song_hypothesis": signal,
                    "detail": "\(role.displayName): \(whyIncluded(song: song, role: role, spec: spec))"
                ]
            ],
            "feedback_chip_sets": feedbackChipSets(role: role),
            "apple_music_resolution": resolutionDictionary(resolution),
            "alpha_route_role": role.rawValue,
            "alpha_resolution_status": AlphaResolutionStatus.resolved.rawValue,
            "alpha_source_opportunity_id": "survey_opportunity_\(spec.idSuffix.lowercased())",
            "alpha_source_mission_type": spec.missionType.rawValue,
            "alpha_target_object_ids": targetObjectIDs(for: spec),
            "alpha_graph_context_refs": graphContextRefs(for: spec),
            "notes": "canonical_song_recording_id=\(song.canonicalSongRecordingID); archetypes=\(song.archetypeIDs.joined(separator: ",")); families=\(song.familyNumbers.map(String.init).joined(separator: ",")); exact_survey_song_reuse=false"
        ]
        if let year = song.releaseYears.first {
            output["year"] = year
        }
        if let album = resolution?.resolvedAlbum, !album.isEmpty {
            output["album"] = album
        }
        return output
    }

    private static func indexedResolution(
        for song: GraphSongRecord,
        spec: SurveyOpportunityMissionSpec,
        sequence: Int,
        role: AlphaRouteItemRole,
        catalogIndex: CanonicalAppleMusicCatalogIndex,
        now: Date
    ) -> AppleMusicResolution? {
        let item = MissionItem(
            itemID: itemID(for: song, spec: spec, sequence: sequence),
            sequence: sequence,
            itemType: .track,
            artist: song.primaryArtist,
            title: song.displayName,
            album: nil,
            year: song.releaseYears.first,
            whyIncluded: nil,
            expectedTestSignal: nil,
            playerCard: nil,
            feedbackChipSets: nil,
            appleMusicResolution: .unresolved(),
            candidateID: "canonical_song_recording:\(song.canonicalSongRecordingID)",
            routeCandidateKey: "survey_opportunity:\(spec.missionType.rawValue):\(song.canonicalSongRecordingID)",
            routeBatchDedupeKey: "song_recording:\(song.canonicalSongRecordingID)",
            routeDisplayIdentityKey: routeDisplayIdentityKey(for: song),
            notes: nil,
            alphaRouteRole: role,
            alphaResolutionStatus: .resolved,
            alphaSourceOpportunityID: "survey_opportunity_\(spec.idSuffix.lowercased())",
            alphaSourceMissionType: spec.missionType.rawValue,
            alphaTargetObjectIDs: targetObjectIDs(for: spec),
            alphaGraphContextRefs: graphContextRefs(for: spec)
        )
        guard let resolution = catalogIndex.resolution(for: item, at: now),
              resolution.status == .resolved,
              resolution.catalogID?.isEmpty == false || resolution.catalogURL != nil else {
            return nil
        }
        return resolution
    }

    private static func whyIncluded(song: GraphSongRecord, role: AlphaRouteItemRole, spec: SurveyOpportunityMissionSpec) -> String {
        let archetypeText = song.archetypeIDs.isEmpty ? "canonical graph lane" : "archetype \(song.archetypeIDs.joined(separator: "/"))"
        switch role {
        case .anchor:
            return "Anchor inside \(archetypeText) so the route has a stable Survey-derived reference point."
        case .bridge:
            return "Bridge item selected to test whether the Survey-supported lane connects to nearby graph territory."
        case .boundary:
            return "Boundary item selected to test the edge without using an explicitly disliked Survey artist or rated song."
        case .context:
            return "Context item selected to see whether framing changes the response to this lane."
        case .comparator:
            return "Comparator selected to keep the mission interpretable against the route thesis."
        case .control:
            return "Control item selected so the route is not only a comfort playlist."
        case .probe:
            return "Probe selected from resolved canonical graph songs near the mission opportunity."
        }
    }

    private static func expectedSignal(role: AlphaRouteItemRole, spec: SurveyOpportunityMissionSpec) -> String {
        switch role {
        case .anchor:
            return "Confirms whether the Survey-derived lane has a usable listening anchor."
        case .bridge:
            return "Tests whether the nearby road feels connected rather than random."
        case .boundary:
            return "Tests whether the edge case is a clean miss, a useful waypoint, or a surprise."
        case .context:
            return "Tests whether response depends on context more than the song alone."
        case .comparator:
            return "Provides a comparison point for interpreting the route."
        case .control:
            return "Keeps the mission readable by isolating the route question."
        case .probe:
            return "Collects direct playback evidence for the mission opportunity."
        }
    }

    private static func feedbackChipSets(role: AlphaRouteItemRole) -> [String: [[String: String]]] {
        [
            ReactionValue.hit.rawValue: [
                chip("TAG_ALPHA_STRONG_POSITIVE", "Love", "Strong positive signal for this route item.")
            ],
            ReactionValue.partial.rawValue: [
                chip("TAG_ALPHA_QUALIFIED_POSITIVE", "Like", "Qualified positive signal.")
            ],
            ReactionValue.okShelf.rawValue: [
                chip("TAG_ALPHA_KEEP_WAYPOINT", "Ok / Keep", "Weak non-failure waypoint evidence for mission listening.")
            ],
            ReactionValue.miss.rawValue: [
                chip("TAG_ALPHA_NEGATIVE", role == .boundary ? "Boundary miss" : "Dislike", "Negative signal for this route item.")
            ]
        ]
    }

    private static func chip(_ tagID: String, _ label: String, _ description: String) -> [String: String] {
        [
            "tag_id": tagID,
            "label": label,
            "description": description
        ]
    }

    private static func resolutionDictionary(_ resolution: AppleMusicResolution?) -> [String: Any] {
        guard let resolution else {
            return [
                "status": ResolutionStatus.unresolved.rawValue,
                "reason": "canonical_apple_music_catalog_index_missing",
                "resolver": ResolverKind.notAttempted.rawValue
            ]
        }

        return compactDictionary([
            "status": resolution.status.rawValue,
            "catalog_id": resolution.catalogID,
            "catalog_url": resolution.catalogURL?.absoluteString,
            "artwork_url": resolution.artworkURL?.absoluteString,
            "storefront": resolution.storefront,
            "resolved_title": resolution.resolvedTitle,
            "resolved_artist": resolution.resolvedArtist,
            "resolved_album": resolution.resolvedAlbum,
            "confidence": resolution.confidence,
            "resolver": resolution.resolver?.rawValue,
            "resolved_at": resolution.resolvedAt.map(isoString),
            "reason": resolution.reason,
            "candidate_count": resolution.candidateCount,
            "error_code": resolution.errorCode,
            "error_message": resolution.errorMessage
        ])
    }

    private static func targetObjectIDs(for spec: SurveyOpportunityMissionSpec) -> [String] {
        [
            spec.primaryArchetypeID.map { "archetype:\($0)" },
            spec.secondaryArchetypeID.map { "archetype:\($0)" },
            spec.primaryFamilyID.map { "family:\($0)" },
            spec.secondaryFamilyID.map { "family:\($0)" }
        ].compactMap(\.self)
    }

    private static func graphContextRefs(for spec: SurveyOpportunityMissionSpec) -> [String] {
        targetObjectIDs(for: spec).map { "survey_opportunity_graph_context:\($0)" }
    }

    private static func itemID(for song: GraphSongRecord, spec: SurveyOpportunityMissionSpec, sequence: Int) -> String {
        appID(prefix: "ITEM", rawValue: "ALPHA_SURVEY_\(spec.idSuffix)_\(sequence)_\(song.canonicalSongRecordingID)")
    }

    private static func routeDisplayIdentityKey(for song: GraphSongRecord) -> String {
        "track:\(slug(song.primaryArtist)):\(slug(song.displayName))"
    }

    private static func recognitionScore(_ tier: String) -> Double {
        switch tier {
        case "mass":
            return 9
        case "high":
            return 7
        case "medium":
            return 4
        case "low":
            return 2
        default:
            return 3
        }
    }

    private static func surveyTierScore(_ tier: String) -> Double {
        switch tier {
        case "core":
            return 6
        case "standard":
            return 4
        case "deep":
            return 2
        default:
            return 1
        }
    }

    private static func appID(prefix: String, rawValue: String) -> String {
        let slug = rawValue
            .uppercased()
            .replacingOccurrences(of: #"[^A-Z0-9]+"#, with: "_", options: .regularExpression)
            .trimmingCharacters(in: CharacterSet(charactersIn: "_"))
        let bounded = String(slug.prefix(88)).trimmingCharacters(in: CharacterSet(charactersIn: "_"))
        return bounded.hasPrefix("\(prefix)_") ? bounded : "\(prefix)_\(bounded)"
    }

    private static func slug(_ value: String) -> String {
        value
            .folding(options: [.caseInsensitive, .diacriticInsensitive], locale: Locale(identifier: "en_US_POSIX"))
            .lowercased()
            .components(separatedBy: CharacterSet.alphanumerics.inverted)
            .filter { !$0.isEmpty }
            .joined(separator: "-")
    }

    private static func compactDictionary(_ dictionary: [String: Any?]) -> [String: Any] {
        dictionary.reduce(into: [String: Any]()) { result, pair in
            if let value = pair.value {
                result[pair.key] = value
            }
        }
    }

    private static func isoString(_ date: Date) -> String {
        ISO8601DateFormatter().string(from: date)
    }
}

private struct SurveyOpportunityMissionSpec {
    let idSuffix: String
    let missionType: MissionType
    let title: String
    let alphaMissionArchetype: String
    let riskLevel: String
    let primaryArchetypeID: String?
    let secondaryArchetypeID: String?
    let primaryFamilyID: Int?
    let secondaryFamilyID: Int?
    let routeRoles: [AlphaRouteItemRole]
    let brief: String
    let objective: String
    let whyNow: String

    func matches(_ song: GraphSongRecord) -> Bool {
        if let primaryArchetypeID, song.archetypeIDs.contains(primaryArchetypeID) {
            return true
        }
        if let secondaryArchetypeID, song.archetypeIDs.contains(secondaryArchetypeID) {
            return true
        }
        if let primaryFamilyID, song.familyNumbers.contains(primaryFamilyID) {
            return true
        }
        if let secondaryFamilyID, song.familyNumbers.contains(secondaryFamilyID) {
            return true
        }
        return false
    }
}

private enum GraphNativeStarterMissionBatchBuilder {
    static func makeResponse(
        session: PersistedSurveySession,
        itemLookup: [String: SurveyItem],
        testerAlias: String,
        requestedMissionCount: Int,
        sourceAppVersion: String,
        sourceAppBuild: String,
        excludingRouteItemIDs: Set<String>,
        excludingRouteDisplayIdentityKeys: Set<String>,
        now: Date
    ) throws -> [String: Any] {
        let songs = try GraphSongRecord.load()
        let profile = GraphSurveySignalProfile(session: session, itemLookup: itemLookup, songs: songs)
        var usedCanonicalIDs = Set<String>()
        var usedRouteItemIDs = excludingRouteItemIDs
        var usedRouteDisplayIdentityKeys = excludingRouteDisplayIdentityKeys
        let specs = routeSpecs(profile: profile)
        let boundedMissionCount = max(0, min(requestedMissionCount, specs.count))
        let missions = specs.prefix(boundedMissionCount).enumerated().compactMap { index, spec -> [String: Any]? in
            let selectedSongs = selectSongs(
                for: spec,
                profile: profile,
                songs: songs,
                usedCanonicalIDs: &usedCanonicalIDs,
                usedRouteItemIDs: &usedRouteItemIDs,
                usedRouteDisplayIdentityKeys: &usedRouteDisplayIdentityKeys
            )
            guard selectedSongs.count == 8 else {
                return nil
            }
            return appMission(
                spec: spec,
                missionIndex: index + 1,
                songs: selectedSongs,
                profile: profile,
                sourceAppVersion: sourceAppVersion,
                sourceAppBuild: sourceAppBuild,
                now: now
            )
        }
        let status = missions.count == boundedMissionCount ? "app_import_candidate" : "blocked"
        let validationErrors = missions.count == boundedMissionCount
            ? []
            : ["graph_native_builder_returned_\(missions.count)_of_\(boundedMissionCount)_requested_missions"]

        return [
            "run_id": "local_graph_native_starter_pack_\(UUID().uuidString)",
            "status": status,
            "app_import_status": status,
            "prompt_version": "graph_native_starter_pack_v0_1",
            "model": "none",
            "adapter_version": "local_graph_native_starter_pack_v0_1",
            "mission_output_schema_version": "graph_native_starter_pack.v0.1",
            "app_mission_schema_version": "mission.v0.2",
            "generation": [
                "schema_version": "graph_native_starter_pack.v0.1",
                "tester_alias": testerAlias,
                "survey_session_id": session.surveySessionID,
                "requested_mission_count": boundedMissionCount,
                "returned_mission_count": missions.count,
                "route_policy": "canonical_graph_songs_only_no_openai",
                "route_shape": "six missions target: four archetype depth routes, one bridge route, one frontier route; eight songs each",
                "top_archetype_ids": profile.topArchetypeIDs,
                "top_family_ids": profile.topFamilyIDs
            ],
            "app_missions": missions,
            "alpha_import_policy": [
                "policy": "graph_native_local_alpha",
                "app_import_status": status,
                "app_import_allowed_for_trusted_alpha": status == "app_import_candidate",
                "app_missions_returned": status == "app_import_candidate",
                "returned_app_mission_count": missions.count,
                "openai_call_skipped": true
            ],
            "validation": [
                "generation": [
                    "valid": status == "app_import_candidate",
                    "errors": validationErrors
                ],
                "route_identity": [
                    "route_item_count": missions.compactMap { ($0["items"] as? [[String: Any]])?.count }.reduce(0, +),
                    "checked_batch_memory": !excludingRouteItemIDs.isEmpty || !excludingRouteDisplayIdentityKeys.isEmpty,
                    "source": "local_graph_native_builder"
                ],
                "app_mission": [
                    "valid": status == "app_import_candidate",
                    "errors": validationErrors
                ]
            ],
            "usage": [
                "input_tokens": 0,
                "cached_input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0
            ],
            "latency_ms": 0
        ]
    }

    private static func routeSpecs(profile: GraphSurveySignalProfile) -> [StarterRouteSpec] {
        let archetypes = profile.topArchetypeIDs.isEmpty ? ["001", "010", "033", "047"] : profile.topArchetypeIDs
        let families = profile.topFamilyIDs.isEmpty ? [1, 2, 5, 7] : profile.topFamilyIDs
        let frontierArchetype = profile.frontierArchetypeID ?? archetypes.first ?? "087"
        let frontierFamily = profile.frontierFamilyID ?? families.first ?? 11
        let bridgePrimary = archetypes.first ?? "001"
        let bridgeSecondary = archetypes.dropFirst().first ?? frontierArchetype

        return [
            StarterRouteSpec(
                idSuffix: "DEPTH_01",
                title: "Starter Depth Route I",
                routeKind: .depth,
                primaryArchetypeID: archetypes[safe: 0],
                secondaryArchetypeID: nil,
                primaryFamilyID: families[safe: 0],
                secondaryFamilyID: nil,
                objective: "Confirm whether an apparent archetype signal stays durable across a full eight-song route."
            ),
            StarterRouteSpec(
                idSuffix: "DEPTH_02",
                title: "Starter Depth Route II",
                routeKind: .depth,
                primaryArchetypeID: archetypes[safe: 1] ?? archetypes.first,
                secondaryArchetypeID: nil,
                primaryFamilyID: families[safe: 1] ?? families.first,
                secondaryFamilyID: nil,
                objective: "Check a second strong region without letting one famous example carry the whole signal."
            ),
            StarterRouteSpec(
                idSuffix: "DEPTH_03",
                title: "Starter Depth Route III",
                routeKind: .depth,
                primaryArchetypeID: archetypes[safe: 2] ?? archetypes.first,
                secondaryArchetypeID: nil,
                primaryFamilyID: families[safe: 2] ?? families.first,
                secondaryFamilyID: nil,
                objective: "Separate broad appetite from isolated familiarity in another likely-fit graph lane."
            ),
            StarterRouteSpec(
                idSuffix: "DEPTH_04",
                title: "Starter Depth Route IV",
                routeKind: .depth,
                primaryArchetypeID: archetypes[safe: 3] ?? archetypes.first,
                secondaryArchetypeID: nil,
                primaryFamilyID: families[safe: 3] ?? families.first,
                secondaryFamilyID: nil,
                objective: "Give the Starter Atlas one more clean depth read before bridge and frontier tests."
            ),
            StarterRouteSpec(
                idSuffix: "BRIDGE_01",
                title: "Starter Bridge Route",
                routeKind: .bridge,
                primaryArchetypeID: bridgePrimary,
                secondaryArchetypeID: bridgeSecondary,
                primaryFamilyID: families.first,
                secondaryFamilyID: families.dropFirst().first ?? frontierFamily,
                objective: "Test whether two apparent signals connect as a real bridge instead of sitting as separate likes."
            ),
            StarterRouteSpec(
                idSuffix: "FRONTIER_01",
                title: "Starter Frontier Route",
                routeKind: .frontier,
                primaryArchetypeID: frontierArchetype,
                secondaryArchetypeID: archetypes.first,
                primaryFamilyID: frontierFamily,
                secondaryFamilyID: families.first,
                objective: "Look for positive waypoints in nearby graph territory without using explicit dislikes."
            )
        ]
    }

    private static func selectSongs(
        for spec: StarterRouteSpec,
        profile: GraphSurveySignalProfile,
        songs: [GraphSongRecord],
        usedCanonicalIDs: inout Set<String>,
        usedRouteItemIDs: inout Set<String>,
        usedRouteDisplayIdentityKeys: inout Set<String>
    ) -> [GraphSongRecord] {
        var selected = [GraphSongRecord]()
        let eligible = songs.filter { song in
            !usedCanonicalIDs.contains(song.canonicalSongRecordingID) &&
                !profile.isExcluded(song) &&
                !usedRouteItemIDs.contains(itemID(for: song)) &&
                !usedRouteDisplayIdentityKeys.contains(routeDisplayIdentityKey(for: song))
        }
        let focused = eligible.filter { spec.matches($0) }
        appendSongs(
            from: focused.isEmpty ? eligible : focused,
            spec: spec,
            profile: profile,
            desiredTotalCount: 8,
            selected: &selected,
            usedCanonicalIDs: &usedCanonicalIDs,
            usedRouteItemIDs: &usedRouteItemIDs,
            usedRouteDisplayIdentityKeys: &usedRouteDisplayIdentityKeys
        )

        if selected.count < 8 {
            appendSongs(
                from: eligible,
                spec: spec,
                profile: profile,
                desiredTotalCount: 8,
                selected: &selected,
                usedCanonicalIDs: &usedCanonicalIDs,
                usedRouteItemIDs: &usedRouteItemIDs,
                usedRouteDisplayIdentityKeys: &usedRouteDisplayIdentityKeys
            )
        }

        return selected
    }

    private static func appendSongs(
        from songs: [GraphSongRecord],
        spec: StarterRouteSpec,
        profile: GraphSurveySignalProfile,
        desiredTotalCount: Int,
        selected: inout [GraphSongRecord],
        usedCanonicalIDs: inout Set<String>,
        usedRouteItemIDs: inout Set<String>,
        usedRouteDisplayIdentityKeys: inout Set<String>
    ) {
        guard selected.count < desiredTotalCount else {
            return
        }
        let rankedSongs = songs.sorted { lhs, rhs in
            let leftScore = score(lhs, spec: spec, profile: profile)
            let rightScore = score(rhs, spec: spec, profile: profile)
            if leftScore != rightScore {
                return leftScore > rightScore
            }
            return lhs.canonicalSongRecordingID < rhs.canonicalSongRecordingID
        }

        for song in rankedSongs {
            guard selected.count < desiredTotalCount else {
                break
            }
            let itemID = itemID(for: song)
            let displayKey = routeDisplayIdentityKey(for: song)
            guard !usedCanonicalIDs.contains(song.canonicalSongRecordingID),
                  !usedRouteItemIDs.contains(itemID),
                  !usedRouteDisplayIdentityKeys.contains(displayKey),
                  !selected.contains(where: { $0.canonicalSongRecordingID == song.canonicalSongRecordingID }) else {
                continue
            }
            selected.append(song)
            usedCanonicalIDs.insert(song.canonicalSongRecordingID)
            usedRouteItemIDs.insert(itemID)
            usedRouteDisplayIdentityKeys.insert(displayKey)
            if selected.count >= desiredTotalCount {
                break
            }
        }
    }

    private static func score(_ song: GraphSongRecord, spec: StarterRouteSpec, profile: GraphSurveySignalProfile) -> Double {
        var score = 0.0
        if let primaryArchetypeID = spec.primaryArchetypeID,
           song.archetypeIDs.contains(primaryArchetypeID) {
            score += spec.routeKind == .frontier ? 18 : 28
        }
        if let secondaryArchetypeID = spec.secondaryArchetypeID,
           song.archetypeIDs.contains(secondaryArchetypeID) {
            score += spec.routeKind == .bridge ? 18 : 8
        }
        if let primaryFamilyID = spec.primaryFamilyID,
           song.familyNumbers.contains(primaryFamilyID) {
            score += spec.routeKind == .frontier ? 12 : 18
        }
        if let secondaryFamilyID = spec.secondaryFamilyID,
           song.familyNumbers.contains(secondaryFamilyID) {
            score += spec.routeKind == .bridge ? 12 : 6
        }
        score += song.roles.contains("anchor") ? 6 : 0
        score += song.roles.contains("gateway") ? 4 : 0
        score += recognitionScore(song.bestRecognitionTier)
        score += surveyTierScore(song.bestSurveyTier)
        score += song.archetypeIDs.reduce(0) { $0 + (profile.archetypeWeights[$1] ?? 0) }
        score += song.familyNumbers.reduce(0) { $0 + (profile.familyWeights[$1] ?? 0) }
        return score
    }

    private static func appMission(
        spec: StarterRouteSpec,
        missionIndex: Int,
        songs: [GraphSongRecord],
        profile: GraphSurveySignalProfile,
        sourceAppVersion: String,
        sourceAppBuild: String,
        now: Date
    ) -> [String: Any] {
        [
            "schema_version": "mission.v0.2",
            "mission_id": "MIS_ALPHA_STARTER_\(spec.idSuffix)",
            "mission_title": spec.title,
            "mission_version": "graph_native_v0.1",
            "created_at": isoString(now),
            "mission_type": "track_probe",
            "recommended_format": "play_items_in_order",
            "hypothesis": spec.objective,
            "inflation_warning": "Starter Alpha route. Songs are selected from the canonical graph as learning prompts, not final Atlas verdicts.",
            "success_bar": [
                "minimum_items_to_resolve": 6,
                "minimum_items_to_play": 6,
                "minimum_reactions_required": 6,
                "requires_physical_iphone": true,
                "notes": "Deprecated local starter mission builder; not the v0.2 TestFlight mission source."
            ],
            "run_instructions": [
                "listen_in_order": true,
                "shuffle_allowed": false,
                "raw_text": "Listen in order and react quickly. The route is designed to test the Starter Atlas, not to prove a final preference."
            ],
            "post_run_inference_rules": [
                [
                    "trigger": "After completion, review reactions, chips, notes, skips, and resolver status.",
                    "inference": "Update provisional Atlas signals only through the Alpha review path."
                ]
            ],
            "items": songs.enumerated().map { index, song in
                appMissionItem(
                    song: song,
                    sequence: index + 1,
                    spec: spec,
                    profile: profile
                )
            },
            "notes": [
                "source_app_version": sourceAppVersion,
                "source_app_build": sourceAppBuild,
                "selection_policy": "canonical_graph_songs_only_no_openai"
            ]
        ]
    }

    private static func appMissionItem(
        song: GraphSongRecord,
        sequence: Int,
        spec: StarterRouteSpec,
        profile: GraphSurveySignalProfile
    ) -> [String: Any] {
        let artist = song.primaryArtist
        let signal = expectedSignal(song: song, spec: spec)
        var output: [String: Any] = [
            "item_id": itemID(for: song),
            "candidate_id": "canonical_song_recording:\(song.canonicalSongRecordingID)",
            "route_candidate_key": "route:track:song_recording:\(song.canonicalSongRecordingID)",
            "route_batch_dedupe_key": "song_recording:\(song.canonicalSongRecordingID)",
            "route_display_identity_key": routeDisplayIdentityKey(for: song),
            "sequence": sequence,
            "item_type": "track",
            "artist": artist,
            "title": song.displayName,
            "why_included": whyIncluded(song: song, spec: spec, profile: profile),
            "expected_test_signal": signal,
            "player_card": [
                "flip_side": [
                    "song_hypothesis": signal,
                    "detail": "Canonical graph route item for \(spec.routeKind.displayName.lowercased())."
                ]
            ],
            "feedback_chip_sets": feedbackChipSets(spec: spec),
            "apple_music_resolution": [
                "status": "unresolved",
                "reason": "\(artist) \(song.displayName)",
                "resolver": "not_attempted"
            ],
            "notes": "canonical_song_recording_id=\(song.canonicalSongRecordingID); archetypes=\(song.archetypeIDs.joined(separator: ",")); families=\(song.familyNumbers.map(String.init).joined(separator: ","))"
        ]
        if let year = song.releaseYears.first {
            output["year"] = year
        }
        return output
    }

    private static func whyIncluded(song: GraphSongRecord, spec: StarterRouteSpec, profile: GraphSurveySignalProfile) -> String {
        let archetypeText = song.archetypeIDs.isEmpty ? "canonical graph" : "archetype \(song.archetypeIDs.joined(separator: "/"))"
        switch spec.routeKind {
        case .depth:
            return "Depth read for \(archetypeText), selected from graph songs near your survey signals."
        case .bridge:
            return "Bridge test between early signal regions, using a graph song with plausible connective value."
        case .frontier:
            let knownAnchor = song.archetypeIDs.contains(where: { profile.topArchetypeIDs.contains($0) })
            return knownAnchor
                ? "Anchor inside the frontier route so the nearby territory has orientation."
                : "Nearby graph territory chosen to look for a positive waypoint."
        }
    }

    private static func expectedSignal(song: GraphSongRecord, spec: StarterRouteSpec) -> String {
        switch spec.routeKind {
        case .depth:
            return "Tests whether this graph lane is durable beyond a single familiar example."
        case .bridge:
            return "Tests whether the route from one signaled archetype to another feels natural."
        case .frontier:
            return "Tests whether nearby graph territory contains a positive waypoint without using explicit dislikes."
        }
    }

    private static func feedbackChipSets(spec: StarterRouteSpec) -> [String: [[String: String]]] {
        [
            "hit": [
                chip("TAG_HIT_FITS_MAP", "Fits my map", "Positive evidence for this route question."),
                chip("TAG_HIT_WANT_MORE", "Want more", "Strong appetite for more nearby graph items.")
            ],
            "partial": [
                chip("TAG_PARTIAL_RIGHT_LANE", "Right lane", "The area works, but this exact song is not a full hit."),
                chip("TAG_PARTIAL_SPECIFIC_MOOD", "Mood-specific", "Useful with context or timing.")
            ],
            "ok_shelf": [
                chip("TAG_OK_RESPECT", "Respect it", "Useful waypoint or reference, not a craving."),
                chip("TAG_OK_NEUTRAL", "Neutral", "No strong map movement yet.")
            ],
            "miss": [
                chip("TAG_MISS_NOT_FOR_ME", "Not for me", "Negative evidence for this route item."),
                chip("TAG_MISS_WRONG_EDGE", "Wrong edge", "The nearby region may be misread.")
            ]
        ]
    }

    private static func chip(_ tagID: String, _ label: String, _ description: String) -> [String: String] {
        [
            "tag_id": tagID,
            "label": label,
            "description": description
        ]
    }

    private static func itemID(for song: GraphSongRecord) -> String {
        appID(prefix: "ITEM", rawValue: "GRAPH_\(song.canonicalSongRecordingID)")
    }

    private static func routeDisplayIdentityKey(for song: GraphSongRecord) -> String {
        "track:\(slug(song.primaryArtist)):\(slug(song.displayName))"
    }

    private static func recognitionScore(_ tier: String) -> Double {
        switch tier {
        case "mass":
            return 9
        case "high":
            return 7
        case "medium":
            return 4
        case "low":
            return 2
        default:
            return 3
        }
    }

    private static func surveyTierScore(_ tier: String) -> Double {
        switch tier {
        case "core":
            return 6
        case "standard":
            return 4
        case "deep":
            return 2
        default:
            return 1
        }
    }

    private static func appID(prefix: String, rawValue: String) -> String {
        let slug = rawValue
            .uppercased()
            .replacingOccurrences(of: #"[^A-Z0-9]+"#, with: "_", options: .regularExpression)
            .trimmingCharacters(in: CharacterSet(charactersIn: "_"))
        let bounded = String(slug.prefix(72))
        return bounded.hasPrefix("\(prefix)_") ? bounded : "\(prefix)_\(bounded)"
    }

    private static func slug(_ value: String) -> String {
        value
            .folding(options: [.caseInsensitive, .diacriticInsensitive], locale: Locale(identifier: "en_US_POSIX"))
            .lowercased()
            .components(separatedBy: CharacterSet.alphanumerics.inverted)
            .filter { !$0.isEmpty }
            .joined(separator: "-")
    }

    private static func isoString(_ date: Date) -> String {
        ISO8601DateFormatter().string(from: date)
    }
}

private struct StarterRouteSpec {
    enum RouteKind {
        case depth
        case bridge
        case frontier

        var displayName: String {
            switch self {
            case .depth:
                return "Archetype Depth Route"
            case .bridge:
                return "Archetype Bridge Route"
            case .frontier:
                return "Frontier Route"
            }
        }
    }

    let idSuffix: String
    let title: String
    let routeKind: RouteKind
    let primaryArchetypeID: String?
    let secondaryArchetypeID: String?
    let primaryFamilyID: Int?
    let secondaryFamilyID: Int?
    let objective: String

    func matches(_ song: GraphSongRecord) -> Bool {
        if let primaryArchetypeID, song.archetypeIDs.contains(primaryArchetypeID) {
            return true
        }
        if let secondaryArchetypeID, song.archetypeIDs.contains(secondaryArchetypeID) {
            return true
        }
        if let primaryFamilyID, song.familyNumbers.contains(primaryFamilyID) {
            return true
        }
        if let secondaryFamilyID, song.familyNumbers.contains(secondaryFamilyID) {
            return true
        }
        return false
    }
}

private struct GraphSongRecord: Decodable, Equatable {
    let canonicalSongRecordingID: String
    let displayName: String
    let familyNumbers: [Int]
    let archetypeIDs: [String]
    let roles: [String]
    let songTitle: String?
    let artistNames: [String]
    let releaseYears: [Int]
    let bestRecognitionTier: String
    let bestSurveyTier: String

    enum CodingKeys: String, CodingKey {
        case canonicalSongRecordingID = "canonical_song_recording_id"
        case displayName = "display_name"
        case familyNumbers = "family_numbers"
        case archetypeIDs = "archetype_ids"
        case roles
        case songTitle = "song_title"
        case artistNames = "artist_names"
        case releaseYears = "release_years"
        case bestRecognitionTier = "best_recognition_tier"
        case bestSurveyTier = "best_survey_tier"
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        canonicalSongRecordingID = try container.decode(String.self, forKey: .canonicalSongRecordingID)
        displayName = try container.decode(String.self, forKey: .displayName)
        familyNumbers = try container.decodeIfPresent([Int].self, forKey: .familyNumbers) ?? []
        archetypeIDs = try container.decodeIfPresent([String].self, forKey: .archetypeIDs) ?? []
        roles = try container.decodeIfPresent([String].self, forKey: .roles) ?? []
        songTitle = try container.decodeIfPresent(String.self, forKey: .songTitle)
        artistNames = try container.decodeIfPresent([String].self, forKey: .artistNames) ?? []
        releaseYears = try container.decodeIfPresent([Int?].self, forKey: .releaseYears)?.compactMap(\.self) ?? []
        bestRecognitionTier = try container.decodeIfPresent(String.self, forKey: .bestRecognitionTier) ?? "unknown"
        bestSurveyTier = try container.decodeIfPresent(String.self, forKey: .bestSurveyTier) ?? "standard"
    }

    var primaryArtist: String {
        artistNames.first ?? "Unknown Artist"
    }

    static func load(bundle: Bundle = .main) throws -> [GraphSongRecord] {
        guard let url = bundle.url(forResource: "canonical_song_recordings", withExtension: "json") else {
            throw GraphNativeStarterMissionError.missingCanonicalSongGraph
        }
        let data = try Data(contentsOf: url)
        return try JSONDecoder().decode([GraphSongRecord].self, from: data)
    }
}

private struct GraphSurveySignalProfile {
    let familyWeights: [Int: Double]
    let archetypeWeights: [String: Double]
    let negativeFamilyWeights: [Int: Double]
    let negativeArchetypeWeights: [String: Double]
    let dislikedArtists: Set<String>
    let dislikedSongs: Set<String>
    let ratedSongDisplayKeys: Set<String>
    let topFamilyIDs: [Int]
    let topArchetypeIDs: [String]
    let negativeFamilyIDs: [Int]
    let negativeArchetypeIDs: [String]
    let frontierFamilyID: Int?
    let frontierArchetypeID: String?
    let positiveSignalCount: Int
    let negativeSignalCount: Int
    let fineSignalCount: Int
    let unknownSignalCount: Int

    init(session: PersistedSurveySession, itemLookup: [String: SurveyItem], songs: [GraphSongRecord]) {
        var familyWeights = [Int: Double]()
        var archetypeWeights = [String: Double]()
        var negativeFamilyWeights = [Int: Double]()
        var negativeArchetypeWeights = [String: Double]()
        var dislikedArtists = Set<String>()
        var dislikedSongs = Set<String>()
        var ratedSongDisplayKeys = Set<String>()
        var positiveSignalCount = 0
        var negativeSignalCount = 0
        var fineSignalCount = 0
        var unknownSignalCount = 0
        let songsByID = Dictionary(uniqueKeysWithValues: songs.map { ($0.canonicalSongRecordingID, $0) })

        for response in session.responses.values {
            guard let item = itemLookup[response.itemID] ?? Self.visibleItem(response.itemID, session: session) else {
                continue
            }
            switch response.state {
            case .favorite, .like:
                positiveSignalCount += 1
            case .fine:
                fineSignalCount += 1
            case .notForMe:
                negativeSignalCount += 1
            case .dontKnow:
                unknownSignalCount += 1
            }

            let matchedSongs = Self.matchingSongs(for: item, songs: songs, songsByID: songsByID)
            if item.kind == .song {
                ratedSongDisplayKeys.insert(Self.displayKey(title: item.title, artist: item.subtitle))
            }

            if response.state == .notForMe {
                switch item.kind {
                case .artist:
                    dislikedArtists.insert(Self.normalizedKey(item.title))
                case .song:
                    dislikedSongs.insert(Self.displayKey(title: item.title, artist: item.subtitle))
                case .album:
                    break
                }
                for song in matchedSongs.prefix(24) {
                    for familyID in song.familyNumbers {
                        negativeFamilyWeights[familyID, default: 0] += 4
                    }
                    for archetypeID in song.archetypeIDs {
                        negativeArchetypeWeights[archetypeID, default: 0] += 4
                    }
                }
                continue
            }

            let weight = Self.responseWeight(response.state)
            guard weight > 0 else {
                continue
            }

            for song in matchedSongs.prefix(24) {
                for familyID in song.familyNumbers {
                    familyWeights[familyID, default: 0] += weight
                }
                for archetypeID in song.archetypeIDs {
                    archetypeWeights[archetypeID, default: 0] += weight
                }
            }
        }

        self.familyWeights = familyWeights
        self.archetypeWeights = archetypeWeights
        self.negativeFamilyWeights = negativeFamilyWeights
        self.negativeArchetypeWeights = negativeArchetypeWeights
        self.dislikedArtists = dislikedArtists
        self.dislikedSongs = dislikedSongs
        self.ratedSongDisplayKeys = ratedSongDisplayKeys
        topFamilyIDs = familyWeights.sorted { lhs, rhs in
            lhs.value == rhs.value ? lhs.key < rhs.key : lhs.value > rhs.value
        }.map(\.key)
        topArchetypeIDs = archetypeWeights.sorted { lhs, rhs in
            lhs.value == rhs.value ? lhs.key < rhs.key : lhs.value > rhs.value
        }.map(\.key)
        negativeFamilyIDs = negativeFamilyWeights.sorted { lhs, rhs in
            lhs.value == rhs.value ? lhs.key < rhs.key : lhs.value > rhs.value
        }.map(\.key)
        negativeArchetypeIDs = negativeArchetypeWeights.sorted { lhs, rhs in
            lhs.value == rhs.value ? lhs.key < rhs.key : lhs.value > rhs.value
        }.map(\.key)
        let topFamilies = Set(topFamilyIDs.prefix(4))
        let topArchetypes = Set(topArchetypeIDs.prefix(4))
        frontierFamilyID = songs.flatMap(\.familyNumbers).first { !topFamilies.contains($0) }
        frontierArchetypeID = songs.flatMap(\.archetypeIDs).first { !topArchetypes.contains($0) }
        self.positiveSignalCount = positiveSignalCount
        self.negativeSignalCount = negativeSignalCount
        self.fineSignalCount = fineSignalCount
        self.unknownSignalCount = unknownSignalCount
    }

    func isExcluded(_ song: GraphSongRecord) -> Bool {
        if song.artistNames.map(Self.normalizedKey).contains(where: dislikedArtists.contains) {
            return true
        }
        if dislikedSongs.contains(Self.displayKey(title: song.displayName, artist: song.primaryArtist)) {
            return true
        }
        if ratedSongDisplayKeys.contains(Self.displayKey(title: song.displayName, artist: song.primaryArtist)) {
            return true
        }
        let negative = negativePressure(for: song)
        let positive = positiveSupport(for: song)
        if negative >= max(6, positive * 1.15) {
            return true
        }
        return false
    }

    func positiveSupport(for song: GraphSongRecord) -> Double {
        song.familyNumbers.reduce(0) { $0 + (familyWeights[$1] ?? 0) } +
            song.archetypeIDs.reduce(0) { $0 + (archetypeWeights[$1] ?? 0) }
    }

    func negativePressure(for song: GraphSongRecord) -> Double {
        song.familyNumbers.reduce(0) { $0 + (negativeFamilyWeights[$1] ?? 0) } +
            song.archetypeIDs.reduce(0) { $0 + (negativeArchetypeWeights[$1] ?? 0) }
    }

    private static func visibleItem(_ itemID: String, session: PersistedSurveySession) -> SurveyItem? {
        session.displayedPages.values
            .flatMap(\.items)
            .first { $0.id == itemID }
    }

    private static func responseWeight(_ state: SurveySignalState) -> Double {
        switch state {
        case .favorite:
            return 4
        case .like:
            return 3
        case .fine:
            return 1
        case .dontKnow:
            return 0.35
        case .notForMe:
            return 0
        }
    }

    private static func matchingSongs(
        for item: SurveyItem,
        songs: [GraphSongRecord],
        songsByID: [String: GraphSongRecord]
    ) -> [GraphSongRecord] {
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

    private static func displayKey(title: String, artist: String?) -> String {
        [normalizedKey(artist ?? ""), normalizedKey(title)]
            .filter { !$0.isEmpty }
            .joined(separator: "::")
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

private enum GraphNativeStarterMissionError: LocalizedError {
    case missingCanonicalSongGraph

    var errorDescription: String? {
        switch self {
        case .missingCanonicalSongGraph:
            return "Canonical song graph resource is missing from the app bundle."
        }
    }
}

private extension Array {
    subscript(safe index: Int) -> Element? {
        indices.contains(index) ? self[index] : nil
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
    let appRouteItemID: String?
    let routeCandidateKey: String?
    let routeBatchDedupeKey: String?
    let routeDisplayIdentityKey: String?
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
        case appRouteItemID = "app_route_item_id"
        case routeCandidateKey = "route_candidate_key"
        case routeBatchDedupeKey = "route_batch_dedupe_key"
        case routeDisplayIdentityKey = "route_display_identity_key"
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
        output["app_route_item_id"] = appRouteItemID
        output["route_candidate_key"] = routeCandidateKey
        output["route_batch_dedupe_key"] = routeBatchDedupeKey
        output["route_display_identity_key"] = routeDisplayIdentityKey
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
