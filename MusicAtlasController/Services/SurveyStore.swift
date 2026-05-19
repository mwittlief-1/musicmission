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
    private let itemLookup: [String: SurveyItem]

    init(
        persistenceStore: SurveyPersistenceStore = SurveyPersistenceStore(),
        itemLookup: [String: SurveyItem] = SurveyFixtureLibrary.itemLookup()
    ) {
        self.persistenceStore = persistenceStore
        self.itemLookup = itemLookup

        let restoredSession = persistenceStore.load()
        currentStep = restoredSession.currentStep
        responses = restoredSession.responses
        freeformSignals = restoredSession.freeformSignals
        advancedFilter = restoredSession.advancedFilter
    }

    var currentPage: SurveyGridPage? {
        if currentStep == .advancedSurvey {
            return SurveyFixtureLibrary.advancedPage(for: advancedFilter, responses: responses)
        }

        return SurveyFixtureLibrary.page(for: currentStep, responses: responses)
    }

    var shouldSuggestArtistPage3: Bool {
        SurveyFixtureLibrary.shouldOfferArtistPage3(responses: responses)
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
            goTo(.artistPage3Prompt)
        case .artistPage3Prompt:
            goTo(.albumPage1)
        case .artistPage3:
            goTo(.albumPage1)
        case .albumPage1:
            goTo(.songPage1)
        case .songPage1:
            goTo(.deeperPrompt)
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
            goTo(.artistPage3Prompt)
        case .albumPage1:
            goTo(.artistPage3Prompt)
        case .songPage1:
            goTo(.albumPage1)
        case .deeperPrompt:
            goTo(.songPage1)
        case .advancedSurvey:
            goTo(.deeperPrompt)
        case .readout:
            goTo(.deeperPrompt)
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
