import AuthenticationServices
import Combine
import CryptoKit
import Foundation
import Security

enum AlphaMissionGenerationConfig {
    static let requiredMissionCount = 6
    static let minimumUsableMissionCount = requiredMissionCount
    static let maxGenerationAttemptCount = requiredMissionCount * 2
    static let requestTimeoutSeconds: TimeInterval = 75
}

struct MissionGenerationProgress: Equatable {
    let completedCount: Int
    let targetCount: Int
    let activeMissionNumber: Int?
    let detail: String

    static let idle = MissionGenerationProgress(
        completedCount: 0,
        targetCount: AlphaMissionGenerationConfig.requiredMissionCount,
        activeMissionNumber: nil,
        detail: "Ready to generate the first Alpha mission batch."
    )

    var fractionCompleted: Double {
        guard targetCount > 0 else {
            return 0
        }

        return min(1, max(0, Double(completedCount) / Double(targetCount)))
    }
}

struct TimeoutError: LocalizedError {
    let seconds: TimeInterval

    var errorDescription: String? {
        "Operation timed out after \(Int(seconds)) seconds."
    }
}

enum AlphaMissionGenerationError: LocalizedError {
    case localStarterPackResponseDisallowed
    case emptyLiveGenerationImport
    case noImportableMissionsAfterAttempts(attempts: Int, lastIssue: String?)

    var errorDescription: String? {
        switch self {
        case .localStarterPackResponseDisallowed:
            return "Mission generation returned a deprecated starter-pack response that cannot be imported by this build."
        case .emptyLiveGenerationImport:
            return "Mission construction returned no importable app missions."
        case .noImportableMissionsAfterAttempts(let attempts, let lastIssue):
            let suffix = lastIssue.map { " Last issue: \($0)" } ?? ""
            return "Mission construction did not return enough app-importable missions after \(attempts) build attempt\(attempts == 1 ? "" : "s").\(suffix)"
        }
    }
}

struct AlphaLegacyDataQuarantine {
    private let fileManager: FileManager
    private let applicationSupportURL: URL?
    private let documentURL: URL?

    init(
        fileManager: FileManager = .default,
        applicationSupportURL: URL? = nil,
        documentURL: URL? = nil
    ) {
        self.fileManager = fileManager
        self.applicationSupportURL = applicationSupportURL
        self.documentURL = documentURL
    }

    @discardableResult
    func quarantineKnownLocalState(now: Date = Date()) throws -> [URL] {
        let supportRoot = try resolvedApplicationSupportURL()
        let documentRoot = try resolvedDocumentURL()
        let batchDirectory = supportRoot
            .appendingPathComponent("MusicAtlasControllerAlphaQuarantine", isDirectory: true)
            .appendingPathComponent(batchName(now: now), isDirectory: true)
        var movedURLs = [URL]()

        let sources: [(source: URL, destinationName: String)] = [
            (
                supportRoot.appendingPathComponent("MusicAtlasController", isDirectory: true),
                "application_support_MusicAtlasController"
            ),
            (
                documentRoot.appendingPathComponent("MusicAtlasControllerExports", isDirectory: true),
                "documents_MusicAtlasControllerExports"
            )
        ]

        for source in sources where fileManager.fileExists(atPath: source.source.path) {
            try fileManager.createDirectory(at: batchDirectory, withIntermediateDirectories: true)
            let destination = uniqueDestination(
                batchDirectory.appendingPathComponent(source.destinationName, isDirectory: true)
            )
            try fileManager.moveItem(at: source.source, to: destination)
            movedURLs.append(destination)
        }

        return movedURLs
    }

    private func resolvedApplicationSupportURL() throws -> URL {
        if let applicationSupportURL {
            return applicationSupportURL
        }

        return try fileManager.url(
            for: .applicationSupportDirectory,
            in: .userDomainMask,
            appropriateFor: nil,
            create: true
        )
    }

    private func resolvedDocumentURL() throws -> URL {
        if let documentURL {
            return documentURL
        }

        return try fileManager.url(
            for: .documentDirectory,
            in: .userDomainMask,
            appropriateFor: nil,
            create: true
        )
    }

    private func batchName(now: Date) -> String {
        let formatter = DateFormatter()
        formatter.calendar = Calendar(identifier: .gregorian)
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone(secondsFromGMT: 0)
        formatter.dateFormat = "yyyyMMdd_HHmmss"
        return "legacy_state_\(formatter.string(from: now))_\(UUID().uuidString)"
    }

    private func uniqueDestination(_ destination: URL) -> URL {
        guard fileManager.fileExists(atPath: destination.path) else {
            return destination
        }

        return destination
            .deletingLastPathComponent()
            .appendingPathComponent("\(destination.lastPathComponent)_\(UUID().uuidString)", isDirectory: true)
    }
}

@MainActor
final class AppModel: ObservableObject {
    enum LoadState: Equatable {
        case idle
        case loading
        case loaded
        case failed(String)
    }

    @Published private(set) var availableMissions: [Mission] = []
    @Published private(set) var missionCatalog: MissionCatalog = .empty
    @Published private(set) var mission: Mission?
    @Published private(set) var missionLoadState: LoadState = .idle
    @Published var selectedItemID: String?
    @Published private(set) var resolutions: [String: AppleMusicResolution] = [:]
    @Published private(set) var playbackRecords: [String: PlaybackRecord] = [:]
    @Published private(set) var exportPreview: ExportPreview?
    @Published private(set) var savedExport: SavedExport?
    @Published private(set) var savedExports: [SavedExport] = []
    @Published private(set) var lastActionMessage: String?
    @Published private(set) var reactionRevision = 0
    @Published private(set) var isResolvingMission = false
    @Published private(set) var activePlaybackSnapshot: PlaybackSnapshot = .idle
    @Published private(set) var observedPlaybackItemID: String?
    @Published private(set) var playerActionLog: [PlayerActionLogEntry] = []
    @Published private(set) var musicAuthorizationSnapshot: MusicAuthorizationSnapshot
    @Published private(set) var musicEnvironmentSnapshot: MusicEnvironmentSnapshot
    @Published private(set) var supabaseAuthSnapshot: SupabaseAuthSnapshot
    @Published private(set) var firstMissionGenerationState: LoadState = .idle
    @Published private(set) var firstMissionGenerationProgress: MissionGenerationProgress = .idle
    @Published private(set) var isEvidenceUploadInFlight = false
    @Published private(set) var lastEvidenceUploadResult: EvidenceUploadResult?
    @Published private(set) var isDiagnosticUploadInFlight = false
    @Published private(set) var lastDiagnosticUploadResult: DiagnosticUploadBatchResult?
    @Published private(set) var savedSupportDiagnosticsPackage: SavedClientDiagnosticPackage?
    @Published var musicServiceMode: MusicServiceMode = DeviceContextProvider.currentContext().isPhysicalDevice ? .liveMusicKit : .developmentStub {
        didSet {
            stopPlaybackPolling()
            exportPreview = nil
            savedExport = nil
            activePlaybackSnapshot = .idle
            observedPlaybackItemID = nil
            lastActionMessage = "Switched to \(musicServiceMode.displayName)."
        }
    }

    let musicAuthorization: MusicAuthorizationService
    let reactionStore = ReactionStore()
    let supabaseAuth: SupabaseAuthService
    let atlasExplainerStore: AtlasExplainerStore

    private let supabaseConfig: SupabaseAlphaConfig
    private let missionGenerationClient: any MissionGenerationClient
    private let evidenceUploadClient: any EvidenceUploadClient
    private let diagnosticUploadClient: any DiagnosticUploadClient
    private let surveyEvidenceBuilder: SurveyEvidenceExportBuilder
    private let clientDiagnosticStore: ClientDiagnosticArtifactStore
    private let missionProvider: any MissionProviding
    private let stubSearchService: any MusicSearchServing
    private let liveSearchService: any MusicSearchServing
    private let stubPlaybackService: any MusicPlaybackServing
    private let livePlaybackService: any MusicPlaybackServing
    private let sessionExporter: SessionExporter
    private let exportFileStore: ExportFileStore
    private let sessionPersistenceStore: SessionPersistenceStore
    private var persistedSessionLibrary: PersistedSessionLibrary = .empty
    private var playbackPollingTask: Task<Void, Never>?
    private var playbackPollingSuppressedUntil: Date?
    private var cancellables: Set<AnyCancellable> = []
    private var pendingAppleSignInNonce: String?
    private let shouldClearLegacyAlphaUATFixturesOnLoad: Bool

    init(
        stubSearchService: any MusicSearchServing = StubMusicSearchService(),
        liveSearchService: any MusicSearchServing = MusicKitCatalogSearchService(),
        stubPlaybackService: any MusicPlaybackServing = StubMusicPlaybackService(),
        livePlaybackService: any MusicPlaybackServing = MusicKitPlaybackService(),
        sessionExporter: SessionExporter = SessionExporter(),
        exportFileStore: ExportFileStore = ExportFileStore(),
        sessionPersistenceStore: SessionPersistenceStore = SessionPersistenceStore(),
        missionProvider: any MissionProviding = LocalMissionProvider(),
        atlasExplainerStore: AtlasExplainerStore = AtlasExplainerStore(),
        supabaseConfig: SupabaseAlphaConfig = .fromBundle(),
        supabaseAuthService: SupabaseAuthService? = nil,
        missionGenerationClient: (any MissionGenerationClient)? = nil,
        evidenceUploadClient: (any EvidenceUploadClient)? = nil,
        diagnosticUploadClient: (any DiagnosticUploadClient)? = nil,
        surveyEvidenceBuilder: SurveyEvidenceExportBuilder = SurveyEvidenceExportBuilder(),
        clientDiagnosticStore: ClientDiagnosticArtifactStore = ClientDiagnosticArtifactStore(),
        shouldClearLegacyAlphaUATFixturesOnLoad: Bool? = nil
    ) {
        let resolvedMusicAuthorization = MusicAuthorizationService()
        let resolvedAuthService = supabaseAuthService ?? SupabaseAuthService(config: supabaseConfig)
        self.musicAuthorization = resolvedMusicAuthorization
        self.musicAuthorizationSnapshot = resolvedMusicAuthorization.snapshot
        self.musicEnvironmentSnapshot = resolvedMusicAuthorization.environmentSnapshot
        self.stubSearchService = stubSearchService
        self.liveSearchService = liveSearchService
        self.stubPlaybackService = stubPlaybackService
        self.livePlaybackService = livePlaybackService
        self.sessionExporter = sessionExporter
        self.exportFileStore = exportFileStore
        self.sessionPersistenceStore = sessionPersistenceStore
        self.missionProvider = missionProvider
        self.atlasExplainerStore = atlasExplainerStore
        self.supabaseConfig = supabaseConfig
        self.supabaseAuth = resolvedAuthService
        self.supabaseAuthSnapshot = resolvedAuthService.snapshot
        self.missionGenerationClient = missionGenerationClient ?? LiveSupabaseMissionGenerationClient(config: supabaseConfig)
        self.evidenceUploadClient = evidenceUploadClient ?? LiveEvidenceUploadClient(config: supabaseConfig)
        self.diagnosticUploadClient = diagnosticUploadClient ?? LiveDiagnosticUploadClient(config: supabaseConfig)
        self.surveyEvidenceBuilder = surveyEvidenceBuilder
        self.clientDiagnosticStore = clientDiagnosticStore
        self.shouldClearLegacyAlphaUATFixturesOnLoad = shouldClearLegacyAlphaUATFixturesOnLoad
            ?? Self.defaultShouldClearLegacyAlphaUATFixturesOnLoad

        resolvedAuthService.$snapshot
            .sink { [weak self] snapshot in
                self?.supabaseAuthSnapshot = snapshot
            }
            .store(in: &cancellables)

        resolvedMusicAuthorization.$snapshot
            .sink { [weak self] snapshot in
                self?.musicAuthorizationSnapshot = snapshot
            }
            .store(in: &cancellables)

        resolvedMusicAuthorization.$environmentSnapshot
            .sink { [weak self] snapshot in
                self?.musicEnvironmentSnapshot = snapshot
            }
            .store(in: &cancellables)
    }

    deinit {
        playbackPollingTask?.cancel()
    }

    func loadSampleMission() {
        loadMissionLibrary()
    }

    func loadAtlasExplainers() {
        atlasExplainerStore.load()
    }

    func loadMissionLibrary() {
        guard missionLoadState != .loaded || availableMissions.isEmpty else {
            return
        }

        missionLoadState = .loading

        do {
            var loadedCatalog = try missionProvider.loadMissionCatalog()
            var restoredLibrary = sessionPersistenceStore.load()
            if shouldClearLegacyAlphaUATFixturesOnLoad,
               Self.containsOnlyLegacyAlphaUATFixtureAssignments(loadedCatalog.reviewedAssignments) {
                try missionProvider.resetReviewedAssignments()
                try sessionPersistenceStore.reset()
                loadedCatalog = try missionProvider.loadMissionCatalog()
                restoredLibrary = .empty
                firstMissionGenerationState = .idle
                firstMissionGenerationProgress = .idle
                lastActionMessage = "Cleared prior static UAT fixture missions so Cartenza can build survey-derived Alpha missions."
            }
            missionCatalog = loadedCatalog
            availableMissions = loadedCatalog.allMissions
            persistedSessionLibrary = restoredLibrary
            savedExports = restoredLibrary.savedExports
            savedExport = restoredLibrary.savedExports.first

            let restoredMission = restoredLibrary.activeMissionID.flatMap { activeMissionID in
                availableMissions.first { $0.missionID == activeMissionID }
            }
            let selectedMission = restoredMission ?? availableMissions.first

            if let selectedMission {
                restoreSessionState(for: selectedMission, persistedSession: restoredLibrary.sessionsByMissionID[selectedMission.missionID])
            } else {
                clearActiveMissionState()
            }
            savedExport = savedExports.first
            missionLoadState = .loaded
        } catch {
            missionLoadState = .failed(error.localizedDescription)
        }
    }

    var reviewedMissionAssignments: [MissionAssignment] {
        missionCatalog.reviewedAssignments
    }

    var hasReviewedMissionAssignments: Bool {
        !missionCatalog.reviewedAssignments.isEmpty
    }

    var reviewedMissionAssignmentCount: Int {
        missionCatalog.reviewedAssignments.count
    }

    var isSupabaseAuthenticated: Bool {
        supabaseAuthSnapshot.isAuthenticated
    }

    var isAppleMusicAuthorized: Bool {
        musicAuthorizationSnapshot.status == "authorized"
    }

    var supabaseAuthStatusDetail: String {
        supabaseAuthSnapshot.detail
    }

    func configureAppleSignInRequest(_ request: ASAuthorizationAppleIDRequest) -> String {
        let rawNonce = SupabaseAuthService.randomNonceString()
        pendingAppleSignInNonce = rawNonce
        request.requestedScopes = [.fullName, .email]
        request.nonce = SupabaseAuthService.sha256(rawNonce)
        return rawNonce
    }

    func completeSupabaseAppleSignIn(result: Result<ASAuthorization, Error>, rawNonce: String?) async {
        let nonce = rawNonce ?? pendingAppleSignInNonce
        pendingAppleSignInNonce = nil

        do {
            try await supabaseAuth.signInWithApple(result: result, rawNonce: nonce)
            if !isAppleMusicAuthorized {
                if musicAuthorizationSnapshot.canRequestAuthorization {
                    await musicAuthorization.requestAuthorization()
                } else {
                    musicAuthorization.refreshStatus()
                }
            }
            lastActionMessage = isAppleMusicAuthorized
                ? "Signed in with Apple and Apple Music connected."
                : "Signed in with Apple. Apple Music still needs access."
        } catch {
            lastActionMessage = error.localizedDescription
        }
    }

    func refreshSupabaseAuthSessionIfPossible() async {
        do {
            _ = try await supabaseAuth.validAccessToken()
        } catch {
            if supabaseAuthSnapshot.status == .unconfigured {
                lastActionMessage = "Supabase is not configured for this build."
            }
        }
    }

    func signOutSupabase() {
        supabaseAuth.signOut()
        lastActionMessage = "Signed out of Supabase."
    }

    func resetAllLocalAlphaState(signOut: Bool = true) {
        stopPlaybackPolling()

        var cleanupMessages = [String]()
        let quarantinedLocations: [URL]
        do {
            quarantinedLocations = try AlphaLegacyDataQuarantine().quarantineKnownLocalState()
        } catch {
            quarantinedLocations = []
            cleanupMessages.append("legacy quarantine: \(error.localizedDescription)")
        }

        do {
            try missionProvider.resetReviewedAssignments()
            try sessionPersistenceStore.reset()
            try SurveyPersistenceStore().reset()
            try clientDiagnosticStore.reset()
        } catch {
            cleanupMessages.append("store reset: \(error.localizedDescription)")
        }

        persistedSessionLibrary = .empty
        missionCatalog = .empty
        availableMissions = []
        savedExports = []
        savedExport = nil
        firstMissionGenerationState = .idle
        firstMissionGenerationProgress = .idle
        isDiagnosticUploadInFlight = false
        lastEvidenceUploadResult = nil
        lastDiagnosticUploadResult = nil
        savedSupportDiagnosticsPackage = nil
        clearActiveMissionState()
        missionLoadState = .idle

        if signOut {
            supabaseAuth.signOut()
        }

        var message = "Reset local Alpha intake, missions, sessions, Survey evidence, and account session."
        if !quarantinedLocations.isEmpty {
            message += " Quarantined \(quarantinedLocations.count) legacy state folder\(quarantinedLocations.count == 1 ? "" : "s")."
        }
        if !cleanupMessages.isEmpty {
            message += " Cleanup note: \(cleanupMessages.joined(separator: "; "))."
        }
        lastActionMessage = message
    }

    func missionAssignment(for mission: Mission) -> MissionAssignment? {
        missionCatalog.assignment(for: mission.missionID)
    }

    func importReviewedMissionJSON(_ rawJSON: String) {
        guard let data = rawJSON.data(using: .utf8) else {
            lastActionMessage = "Reviewed mission import was not valid UTF-8 text."
            return
        }

        do {
            let assignments = try missionProvider.importReviewedMissionData(
                data,
                source: .manualReviewed,
                importedAt: Date()
            )
            reloadMissionCatalog(selectMissionID: assignments.first?.mission.missionID)
            lastActionMessage = "Imported \(assignments.count) reviewed mission assignment\(assignments.count == 1 ? "" : "s")."
        } catch {
            lastActionMessage = error.localizedDescription
        }
    }

    func importSupabaseMissionBatchResponseJSON(_ rawJSON: String) {
        guard let data = rawJSON.data(using: .utf8) else {
            lastActionMessage = "Generation response import was not valid UTF-8 text."
            return
        }

        do {
            let assignments = try missionProvider.importSupabaseMissionBatchResponseData(
                data,
                importedAt: Date()
            )
            reloadMissionCatalog(selectMissionID: assignments.first?.mission.missionID)
            lastActionMessage = "Imported \(assignments.count) app-import candidate mission\(assignments.count == 1 ? "" : "s")."
        } catch {
            lastActionMessage = error.localizedDescription
        }
    }

    func importLocalAlphaApprovedCandidateFixtures() {
        do {
            let data = try AlphaLocalFixtureLoader.approvedCandidateData()
            let assignments = try missionProvider.importAlphaAppImportCandidateData(
                data,
                importedAt: Date()
            )
            reloadMissionCatalog(selectMissionID: assignments.first?.mission.missionID)
            lastActionMessage = "Loaded \(assignments.count) local Alpha app-import candidate fixture\(assignments.count == 1 ? "" : "s") for MusicKit resolution staging."
        } catch {
            lastActionMessage = error.localizedDescription
        }
    }

    func importLocalAlphaAppImportReadyUATFixtures() {
        do {
            let data = try AlphaLocalFixtureLoader.appImportReadyData()
            try missionProvider.resetReviewedAssignments()
            try sessionPersistenceStore.reset()
            persistedSessionLibrary = .empty
            savedExports = []
            savedExport = nil
            clearActiveMissionState()
            let assignments = try missionProvider.importAlphaAppImportCandidateData(
                data,
                importedAt: Date()
            )
            reloadMissionCatalog(selectMissionID: assignments.first?.mission.missionID)
            persistCurrentSession()
            lastActionMessage = "Loaded \(assignments.count) resolved Alpha UAT fixture\(assignments.count == 1 ? "" : "s") and cleared prior mission assignments/sessions for physical playback smoke."
        } catch {
            lastActionMessage = error.localizedDescription
        }
    }

    func markMissionGenerationWaitingForResolvedUATFixtures() {
        let targetMissionCount = AlphaMissionGenerationConfig.requiredMissionCount
        firstMissionGenerationState = .idle
        firstMissionGenerationProgress = MissionGenerationProgress(
            completedCount: 0,
            targetCount: targetMissionCount,
            activeMissionNumber: nil,
            detail: "Survey complete. Load the resolved Alpha UAT mission pack before playback smoke."
        )
        lastActionMessage = "Survey complete. Use the resolved Alpha UAT mission pack for this TestFlight smoke pass."
    }

    @discardableResult
    func generateFirstMissionBatchAfterSurveyCompletion() async -> Bool {
        guard !firstMissionGenerationState.isLoading else {
            return false
        }

        let targetMissionCount = AlphaMissionGenerationConfig.requiredMissionCount
        firstMissionGenerationProgress = MissionGenerationProgress(
            completedCount: 0,
            targetCount: targetMissionCount,
            activeMissionNumber: nil,
            detail: "Selecting deterministic Alpha missions from saved Survey evidence and canonical Apple Music refs."
        )
        firstMissionGenerationState = .loading

        var generatedDataForDiagnostics: Data?
        var recordedSelectionAudit = false

        do {
            try missionProvider.resetReviewedAssignments()
            try sessionPersistenceStore.reset()
            persistedSessionLibrary = .empty
            savedExports = []
            savedExport = nil
            clearActiveMissionState()

            let generatedData = try surveyEvidenceBuilder.makeSurveyOpportunityMissionBatchResponseData(
                testerAlias: supabaseConfig.testerAlias,
                requestedMissionCount: targetMissionCount,
                sourceAppVersion: Self.appVersion,
                sourceAppBuild: Self.appBuild
            )
            generatedDataForDiagnostics = generatedData
            let assignments = try missionProvider.importSupabaseMissionBatchResponseData(
                generatedData,
                importedAt: Date()
            )
            let localImportStatus = assignments.count >= AlphaMissionGenerationConfig.minimumUsableMissionCount
                ? "imported"
                : "too_few_imported"
            recordLocalMissionSelectionAuditDiagnostic(
                responseData: generatedData,
                importedAssignments: assignments,
                localImportStatus: localImportStatus
            )
            recordedSelectionAudit = true
            guard assignments.count >= AlphaMissionGenerationConfig.minimumUsableMissionCount else {
                throw AlphaMissionGenerationError.noImportableMissionsAfterAttempts(
                    attempts: 1,
                    lastIssue: "Survey opportunity selector imported \(assignments.count) missions."
                )
            }

            reloadMissionCatalog(selectMissionID: assignments.first?.mission.missionID)
            persistCurrentSession()
            firstMissionGenerationProgress = MissionGenerationProgress(
                completedCount: assignments.count,
                targetCount: targetMissionCount,
                activeMissionNumber: nil,
                detail: "Loaded \(assignments.count) survey-derived Alpha missions with resolved Apple Music metadata."
            )
            firstMissionGenerationState = .loaded
            lastActionMessage = "Loaded \(assignments.count) survey-derived Alpha missions. Static public-profile UAT fixtures were not used."
            return true
        } catch {
            if !recordedSelectionAudit, let generatedDataForDiagnostics {
                recordLocalMissionSelectionAuditDiagnostic(
                    responseData: generatedDataForDiagnostics,
                    importedAssignments: [],
                    localImportStatus: "failed",
                    importError: error
                )
            }
            firstMissionGenerationState = .failed(error.localizedDescription)
            firstMissionGenerationProgress = MissionGenerationProgress(
                completedCount: min(reviewedMissionAssignmentCount, targetMissionCount),
                targetCount: targetMissionCount,
                activeMissionNumber: nil,
                detail: "Survey-derived Alpha mission selection failed before a usable batch was imported."
            )
            recordClientErrorDiagnostic(error, category: "survey_opportunity_mission_generation_failed")
            lastActionMessage = error.localizedDescription
            return false
        }
    }

    func resetReviewedMissionAssignmentsAndSessions() {
        do {
            try missionProvider.resetReviewedAssignments()
            try sessionPersistenceStore.reset()
            persistedSessionLibrary = .empty
            savedExports = []
            savedExport = nil
            reloadMissionCatalog()
            lastActionMessage = "Reset reviewed mission assignments and local mission sessions."
        } catch {
            lastActionMessage = "Reset failed: \(error.localizedDescription)"
        }
    }

    func markMissionGenerationCancelledForSupport() {
        let targetMissionCount = AlphaMissionGenerationConfig.requiredMissionCount
        let availableMissionCount = reviewedMissionAssignmentCount
        firstMissionGenerationProgress = MissionGenerationProgress(
            completedCount: min(availableMissionCount, targetMissionCount),
            targetCount: targetMissionCount,
            activeMissionNumber: nil,
            detail: "Mission generation was cancelled with \(min(availableMissionCount, targetMissionCount)) of \(targetMissionCount) Alpha missions ready."
        )
        firstMissionGenerationState = .failed("Mission generation cancelled.")
        lastActionMessage = "Mission generation was cancelled. Prepare support diagnostics, retry, or start fresh."
    }

    func selectMission(_ mission: Mission) {
        if self.mission?.missionID == mission.missionID {
            return
        }

        persistCurrentSession()
        restoreSessionState(for: mission, persistedSession: persistedSessionLibrary.sessionsByMissionID[mission.missionID])
        persistCurrentSession()
    }

    func isActiveMission(_ mission: Mission) -> Bool {
        self.mission?.missionID == mission.missionID
    }

    var selectedItem: MissionItem? {
        guard let mission, let selectedItemID else {
            return mission?.items.first
        }

        return mission.items.first { $0.itemID == selectedItemID }
    }

    var selectedItemIndex: Int? {
        guard let mission, let selectedItemID else {
            return nil
        }

        return mission.items.firstIndex { $0.itemID == selectedItemID }
    }

    var missionProgress: MissionProgress {
        guard let mission else {
            return .empty
        }

        let resolvedCount = mission.items.filter { resolution(for: $0).status == .resolved }.count
        let playedCount = mission.items.filter {
            playback(for: $0).hasExportablePlaybackEvidence
        }.count
        let reactionCount = mission.items.filter { reactionStore.reaction(for: $0.itemID) != nil }.count

        return MissionProgress(
            itemCount: mission.items.count,
            resolvedCount: resolvedCount,
            playedCount: playedCount,
            reactionCount: reactionCount,
            selectedIndex: selectedItemIndex
        )
    }

    var canGenerateDevelopmentMissionExport: Bool {
        musicServiceMode == .developmentStub && !exportableEvidenceItems(includeStubEvidence: true).isEmpty
    }

    var canGenerateAcceptanceMissionExport: Bool {
        musicServiceMode == .liveMusicKit &&
        DeviceContextProvider.currentContext().isPhysicalDevice &&
        !exportableEvidenceItems(includeStubEvidence: false).isEmpty
    }

    var missionReviewSnapshot: MissionReviewSnapshot {
        guard let mission else {
            return .empty
        }

        let items = mission.items.map { item in
            MissionReviewItemEvidence(
                item: item,
                resolution: resolution(for: item),
                playback: playback(for: item),
                reaction: reactionStore.reaction(for: item.itemID)
            )
        }

        return MissionReviewSnapshot(
            mission: mission,
            items: items,
            canGenerateDevelopmentExport: canGenerateDevelopmentMissionExport,
            canGenerateAcceptanceExport: canGenerateAcceptanceMissionExport
        )
    }

    func selectItem(_ item: MissionItem) {
        selectedItemID = item.itemID
        exportPreview = nil
        savedExport = nil
        if observedPlaybackItemID != item.itemID {
            activePlaybackSnapshot = PlaybackSnapshot.from(record: playback(for: item))
        }
        persistCurrentSession()
    }

    func selectPreviousItem() {
        guard let mission, let selectedItemIndex, selectedItemIndex > 0 else {
            lastActionMessage = "Already at the first mission item."
            return
        }

        selectItem(mission.items[selectedItemIndex - 1])
    }

    func selectNextItem() {
        guard let mission, let selectedItemIndex, selectedItemIndex < mission.items.count - 1 else {
            lastActionMessage = "Reached the end of the mission."
            return
        }

        selectItem(mission.items[selectedItemIndex + 1])
    }

    func resolution(for item: MissionItem) -> AppleMusicResolution {
        resolutions[item.itemID] ?? item.appleMusicResolution
    }

    func playback(for item: MissionItem) -> PlaybackRecord {
        playbackRecords[item.itemID] ?? .notAttempted()
    }

    func playbackSnapshot(for item: MissionItem) -> PlaybackSnapshot {
        if observedPlaybackItemID == item.itemID {
            return activePlaybackSnapshot
        }

        return PlaybackSnapshot.from(record: playback(for: item))
    }

    func reaction(for item: MissionItem) -> ReactionRecord? {
        reactionStore.reaction(for: item.itemID)
    }

    func resolveSelectedItemWithStub() async {
        await resolveSelectedItem()
    }

    func resolveAllMissionItems() async {
        guard let mission else {
            lastActionMessage = "Load a mission before resolving."
            return
        }

        guard await ensureCanUseActiveMusicService() else {
            return
        }

        isResolvingMission = true
        defer {
            isResolvingMission = false
        }

        var resolvedCount = 0
        var failedCount = 0

        for item in mission.items {
            let current = resolution(for: item)
            if current.status == .resolved {
                resolvedCount += 1
                continue
            }

            let now = Date()
            do {
                let resolution = try await activeSearchService.resolve(item: item, at: now)
                resolutions[item.itemID] = resolution
                playbackRecords[item.itemID] = .notAttempted()
                persistCurrentSession()

                if resolution.status == .resolved {
                    resolvedCount += 1
                } else {
                    failedCount += 1
                }

                lastActionMessage = "Resolved \(resolvedCount)/\(mission.items.count): \(item.title)."
            } catch {
                let failure = AppleMusicResolution.failed(
                    resolver: musicServiceMode == .liveMusicKit ? .automaticSearch : .system,
                    resolvedAt: now,
                    reason: "\(musicServiceMode.rawValue)_resolution_failed",
                    error: error
                )
                resolutions[item.itemID] = failure
                playbackRecords[item.itemID] = .notAttempted()
                persistCurrentSession()
                failedCount += 1
                lastActionMessage = Self.resolutionMessage(for: failure, item: item, serviceMode: musicServiceMode)
            }
        }

        exportPreview = nil
        savedExport = nil
        lastActionMessage = "Mission resolution complete: \(resolvedCount) resolved, \(failedCount) need review."
    }

    func resolveSelectedItem() async {
        guard let item = selectedItem else {
            lastActionMessage = "Select an item before resolving."
            return
        }

        guard await ensureCanUseActiveMusicService() else {
            return
        }

        let now = Date()

        do {
            let resolution = try await activeSearchService.resolve(item: item, at: now)
            resolutions[item.itemID] = resolution
            playbackRecords[item.itemID] = .notAttempted()
            exportPreview = nil
            savedExport = nil
            persistCurrentSession()
            lastActionMessage = Self.resolutionMessage(for: resolution, item: item, serviceMode: musicServiceMode)
        } catch {
            let failure = AppleMusicResolution.failed(
                resolver: musicServiceMode == .liveMusicKit ? .automaticSearch : .system,
                resolvedAt: now,
                reason: "\(musicServiceMode.rawValue)_resolution_failed",
                error: error
            )
            resolutions[item.itemID] = failure
            playbackRecords[item.itemID] = .notAttempted()
            exportPreview = nil
            savedExport = nil
            persistCurrentSession()
            lastActionMessage = Self.resolutionMessage(for: failure, item: item, serviceMode: musicServiceMode)
        }
    }

    @discardableResult
    func playSelectedItem() async -> Bool {
        guard let item = selectedItem else {
            lastActionMessage = "Select an item before playback."
            return false
        }

        guard await ensureCanUseActiveMusicService() else {
            return false
        }

        let now = Date()
        let playback = await activePlaybackService.play(resolution: resolution(for: item), at: now)
        playbackRecords[item.itemID] = playback
        observedPlaybackItemID = item.itemID
        let playbackSnapshot = activePlaybackService.snapshot(currentPlayback: playback)
        activePlaybackSnapshot = playback.status == .playing
            ? PlaybackSnapshot(
                runtimeStatus: .playing,
                elapsedSeconds: playbackSnapshot.elapsedSeconds,
                totalDurationSeconds: playbackSnapshot.totalDurationSeconds ?? playback.durationSeconds
            )
            : playbackSnapshot
        exportPreview = nil
        savedExport = nil
        persistCurrentSession()

        switch playback.status {
        case .played:
            lastActionMessage = "\(musicServiceMode.displayName) marked \(item.title) as played."
        case .playing:
            lastActionMessage = "\(musicServiceMode.displayName) started playback for \(item.title)."
            suppressPlaybackPollingBriefly()
            startPlaybackPolling(for: item.itemID)
            return true
        case .failed:
            stopPlaybackPolling()
            lastActionMessage = playback.errorMessage ?? "Playback failed for \(item.title)."
            return false
        default:
            stopPlaybackPolling()
            lastActionMessage = "Updated playback status for \(item.title): \(playback.status.rawValue)."
        }

        return playback.status == .played
    }

    @discardableResult
    func playSelectedItemResolvingIfNeeded() async -> Bool {
        guard let item = selectedItem else {
            lastActionMessage = "Select an item before playback."
            return false
        }

        if needsResolutionForActivePlayback(resolution(for: item)) {
            await resolveSelectedItem()
        }

        guard resolution(for: item).status == .resolved else {
            return false
        }

        return await playSelectedItem()
    }

    func playNextItem() async {
        guard let mission, let currentIndex = selectedItemIndex else {
            lastActionMessage = "Select an item before moving through the mission."
            return
        }

        guard currentIndex < mission.items.count - 1 else {
            lastActionMessage = "Reached the end of the mission."
            return
        }

        if let currentItem = selectedItem {
            let currentPlayback = playback(for: currentItem)
            let advancedAt = Date()
            if currentPlayback.status == .playing {
                _ = await activePlaybackService.pause(currentPlayback: currentPlayback, at: advancedAt)

                playbackRecords[currentItem.itemID] = currentPlayback.endedAsSkipped(at: advancedAt)
                ensureDefaultNoSignalReaction(for: currentItem, at: advancedAt)
                appendPlayerAction(.skipAfterStart, item: currentItem, at: advancedAt)
                persistCurrentSession()
                lastActionMessage = "Skipped \(currentItem.title)."
            } else if !currentPlayback.hasPlaybackStarted {
                appendPlayerAction(.skipBeforeStart, item: currentItem, at: advancedAt)
                persistCurrentSession()
            }
        }

        stopPlaybackPolling()
        await playNextPlayableItem(startingAt: currentIndex + 1)
    }

    func pauseSelectedPlayback() async {
        guard let item = selectedItem else {
            lastActionMessage = "Select an item before controlling playback."
            return
        }

        guard await ensureCanUseActiveMusicService() else {
            return
        }

        let currentPlayback = playback(for: item)
        let currentSnapshot = playbackSnapshot(for: item)
        let playback = await activePlaybackService.pause(currentPlayback: currentPlayback, at: Date())
        playbackRecords[item.itemID] = playback
        activePlaybackSnapshot = PlaybackSnapshot(
            runtimeStatus: .paused,
            elapsedSeconds: currentSnapshot.elapsedSeconds,
            totalDurationSeconds: currentSnapshot.totalDurationSeconds ?? playback.durationSeconds
        )
        stopPlaybackPolling()
        exportPreview = nil
        savedExport = nil
        persistCurrentSession()

        if currentPlayback.hasPlaybackStarted {
            lastActionMessage = "Paused \(item.title)."
        } else {
            lastActionMessage = "Paused \(musicServiceMode.displayName) playback. No selected-item playback evidence was active."
        }
    }

    func resumeSelectedPlayback() async {
        guard let item = selectedItem else {
            lastActionMessage = "Select an item before controlling playback."
            return
        }

        guard await ensureCanUseActiveMusicService() else {
            return
        }

        let currentPlayback = playback(for: item)
        guard currentPlayback.status == .playing else {
            await playSelectedItemResolvingIfNeeded()
            return
        }

        let playback = await activePlaybackService.resume(currentPlayback: currentPlayback, at: Date())
        playbackRecords[item.itemID] = playback
        observedPlaybackItemID = item.itemID
        let resumedSnapshot = activePlaybackService.snapshot(currentPlayback: playback)
        activePlaybackSnapshot = PlaybackSnapshot(
            runtimeStatus: .playing,
            elapsedSeconds: resumedSnapshot.elapsedSeconds,
            totalDurationSeconds: resumedSnapshot.totalDurationSeconds ?? playback.durationSeconds
        )
        exportPreview = nil
        savedExport = nil
        persistCurrentSession()

        if playback.status == .failed {
            stopPlaybackPolling()
            lastActionMessage = playback.errorMessage ?? "Playback resume failed for \(item.title)."
        } else {
            suppressPlaybackPollingBriefly()
            startPlaybackPolling(for: item.itemID)
            lastActionMessage = "Resumed \(item.title)."
        }
    }

    func seekSelectedPlayback(to elapsedSeconds: TimeInterval) async {
        guard let item = selectedItem else {
            lastActionMessage = "Select an item before seeking playback."
            return
        }

        guard await ensureCanUseActiveMusicService() else {
            return
        }

        let currentPlayback = playback(for: item)
        guard currentPlayback.hasPlaybackStarted else {
            lastActionMessage = "Start playback before seeking."
            return
        }

        let currentSnapshot = playbackSnapshot(for: item)
        let boundedElapsed: TimeInterval
        if let duration = currentSnapshot.totalDurationSeconds ?? currentPlayback.durationSeconds,
           duration > 0 {
            boundedElapsed = min(max(0, elapsedSeconds), duration)
        } else {
            boundedElapsed = max(0, elapsedSeconds)
        }

        let seekedAt = Date()
        let playback = (await activePlaybackService.seek(to: boundedElapsed, currentPlayback: currentPlayback, at: seekedAt))
            .movedPlaybackPosition(to: boundedElapsed, at: seekedAt)
        playbackRecords[item.itemID] = playback
        activePlaybackSnapshot = PlaybackSnapshot(
            runtimeStatus: currentSnapshot.runtimeStatus == .paused ? .paused : .playing,
            elapsedSeconds: boundedElapsed,
            totalDurationSeconds: currentSnapshot.totalDurationSeconds ?? playback.durationSeconds
        )
        exportPreview = nil
        savedExport = nil
        persistCurrentSession()

        if activePlaybackSnapshot.runtimeStatus == .playing {
            observedPlaybackItemID = item.itemID
            suppressPlaybackPollingBriefly()
            startPlaybackPolling(for: item.itemID)
        }
    }

    func stopSelectedPlayback() async {
        guard let item = selectedItem else {
            lastActionMessage = "Select an item before controlling playback."
            return
        }

        guard await ensureCanUseActiveMusicService() else {
            return
        }

        let currentPlayback = playback(for: item)
        let playback = await activePlaybackService.stop(currentPlayback: currentPlayback, at: Date())
        playbackRecords[item.itemID] = playback
        activePlaybackSnapshot = PlaybackSnapshot.from(record: playback)
        stopPlaybackPolling()
        exportPreview = nil
        savedExport = nil
        persistCurrentSession()

        if currentPlayback.hasPlaybackStarted {
            lastActionMessage = "Stopped \(item.title) and recorded playback evidence as played."
        } else {
            lastActionMessage = "Stopped \(musicServiceMode.displayName) playback. No selected-item playback evidence was active."
        }
    }

    func markSelectedItemSkipped() {
        markSelectedItem(.skipped, reason: "user_marked_skipped_in_dev_loop")
    }

    func markSelectedItemUnavailableRegion() {
        markSelectedItem(.unavailableRegion, reason: "user_marked_unavailable_region_in_dev_loop")
    }

    func markSelectedItemUnavailableSubscription() {
        markSelectedItem(.unavailableSubscription, reason: "user_marked_unavailable_subscription_in_dev_loop")
    }

    func resetSelectedItemResolution() {
        guard let item = selectedItem else {
            return
        }

        resolutions[item.itemID] = .unresolved()
        playbackRecords[item.itemID] = .notAttempted()
        exportPreview = nil
        savedExport = nil
        persistCurrentSession()
        lastActionMessage = "Reset \(item.title) to unresolved."
    }

    func saveReactionForSelectedItem(value: ReactionValue?, note: String, selectedTags: [ReactionTag] = []) {
        guard let item = selectedItem else {
            lastActionMessage = "Select an item before saving a reaction."
            return
        }

        saveReaction(for: item, value: value, note: note, selectedTags: selectedTags)
    }

    func saveReaction(for item: MissionItem, value: ReactionValue?, note: String, selectedTags: [ReactionTag] = []) {
        guard let value else {
            lastActionMessage = "Choose a reaction before saving."
            return
        }

        do {
            try reactionStore.saveReaction(
                for: item.itemID,
                value: value,
                note: note,
                selectedTags: selectedTags,
                at: Date()
            )
            reactionRevision += 1
            exportPreview = nil
            savedExport = nil
            persistCurrentSession()
            lastActionMessage = "Saved \(value.displayName) reaction for \(item.title)."
        } catch {
            lastActionMessage = error.localizedDescription
        }
    }

    func generateDevelopmentExportPreview() {
        guard let mission else {
            lastActionMessage = "Load a mission before exporting."
            return
        }

        guard musicServiceMode == .developmentStub else {
            lastActionMessage = "Development stub export is only available in Stub mode. Use acceptance export for live iPhone evidence."
            return
        }

        let evidenceItems = exportableEvidenceItems(includeStubEvidence: true)
        guard !evidenceItems.isEmpty else {
            lastActionMessage = "Play and react to at least one item before exporting."
            return
        }

        do {
            exportPreview = try sessionExporter.makeDevelopmentExport(
                mission: mission,
                evidenceItems: evidenceItems,
                authorizationStatus: musicAuthorizationSnapshot.status
            )
            savedExport = nil
            lastActionMessage = "Generated development stub export preview."
        } catch {
            exportPreview = nil
            savedExport = nil
            lastActionMessage = error.localizedDescription
        }
    }

    func generateAcceptanceExportPreview() {
        guard let mission else {
            lastActionMessage = "Load a mission before exporting."
            return
        }

        guard musicServiceMode == .liveMusicKit else {
            lastActionMessage = "Switch to Live MusicKit mode before generating acceptance evidence."
            return
        }

        let deviceContext = DeviceContextProvider.currentContext()
        guard deviceContext.isPhysicalDevice else {
            lastActionMessage = "Acceptance export requires a physical iPhone."
            return
        }

        let evidenceItems = exportableEvidenceItems(includeStubEvidence: false)
        guard !evidenceItems.isEmpty else {
            lastActionMessage = "Play and react to at least one item before exporting."
            return
        }

        do {
            exportPreview = try sessionExporter.makeAcceptanceExport(
                mission: mission,
                evidenceItems: evidenceItems,
                authorizationStatus: musicAuthorizationSnapshot.status,
                deviceContext: deviceContext
            )
            savedExport = nil
            lastActionMessage = "Generated physical-device acceptance export preview."
        } catch {
            exportPreview = nil
            savedExport = nil
            lastActionMessage = error.localizedDescription
        }
    }

    func saveCurrentExportFiles() {
        guard let exportPreview else {
            lastActionMessage = "Generate an export preview before saving files."
            return
        }

        do {
            let savedExport = try exportFileStore.save(exportPreview)
            self.savedExport = savedExport
            savedExports.removeAll {
                $0.jsonURL == savedExport.jsonURL || $0.markdownURL == savedExport.markdownURL
            }
            savedExports.insert(savedExport, at: 0)
            persistedSessionLibrary.savedExports = savedExports
            persistedSessionLibrary.updatedAt = Date()
            try sessionPersistenceStore.save(persistedSessionLibrary)
            lastActionMessage = "Saved \(exportPreview.kind.displayName.lowercased()) JSON and Markdown export files."
        } catch {
            savedExport = nil
            lastActionMessage = error.localizedDescription
        }
    }

    func uploadSavedEvidenceManually(termsVersion: String = "alpha_terms_2026_05_23") async {
        guard !isEvidenceUploadInFlight else {
            return
        }

        guard let savedExport else {
            lastActionMessage = "Save an evidence package before uploading."
            return
        }

        guard supabaseConfig.isConfiguredForRemoteCalls else {
            lastActionMessage = "Supabase app config is missing. Use Share Evidence Files instead."
            return
        }

        isEvidenceUploadInFlight = true
        defer {
            isEvidenceUploadInFlight = false
        }

        do {
            let accessToken = try await supabaseAuth.validAccessToken()
            let result = try await evidenceUploadClient.uploadEvidence(
                EvidenceUploadRequest(
                    testerAlias: supabaseConfig.testerAlias,
                    savedExport: savedExport,
                    requestedAt: Date(),
                    sourceAppVersion: Self.appVersion,
                    sourceAppBuild: Self.appBuild,
                    termsVersion: termsVersion,
                    acceptedAt: Date()
                ),
                accessToken: accessToken
            )
            lastEvidenceUploadResult = result
            let authDetail = result.userIDPresent == true ? "authenticated" : "missing user id"
            lastActionMessage = "Evidence upload \(result.status) (\(authDetail))."
        } catch {
            lastActionMessage = "Evidence upload failed: \(error.localizedDescription)"
        }
    }

    func saveSupportDiagnosticPackage(rootStateSnapshot: [String: Any]? = nil) {
        do {
            let session = surveyEvidenceBuilder.loadPersistedSurveySession()
            let context = clientDiagnosticContext(surveySessionID: session.surveySessionID)
            let now = Date()
            var additionalArtifacts: [(type: ClientDiagnosticArtifactType, payload: [String: Any], context: ClientDiagnosticLinkContext)] = []

            var stateSnapshot = makeClientStateSnapshotPayload(
                rootStateSnapshot: rootStateSnapshot,
                surveySession: session,
                now: now
            )

            let reviewedMissionCatalogSnapshot = makeReviewedMissionCatalogSnapshotPayload(
                surveySession: session,
                now: now
            )
            stateSnapshot["reviewed_mission_catalog_snapshot"] = reviewedMissionCatalogSnapshot
            additionalArtifacts.append((.clientStateSnapshot, stateSnapshot, context))

            let applePayload: [String: Any]
            if let payload = session.appleMusicSignalPayload {
                applePayload = try SupabaseJSON.object(from: payload) as? [String: Any] ?? [:]
            } else {
                applePayload = [
                    "status": "not_captured",
                    "reason": "No Apple Music signal payload is persisted for this Survey session."
                ]
            }
            additionalArtifacts.append((.appleMusicSignalPayload, applePayload, context))

            let pageAudit = try SupabaseJSON.object(
                from: surveyEvidenceBuilder.makeSurveyPageSelectionAuditData(session: session, now: now)
            ) as? [String: Any] ?? [:]
            additionalArtifacts.append((.surveyPageSelectionAudit, pageAudit, context))

            let evidenceExport = try SupabaseJSON.object(
                from: surveyEvidenceBuilder.makeSurveyEvidenceExportData(session: session, now: now)
            ) as? [String: Any] ?? [:]
            additionalArtifacts.append((.surveyEvidenceExport, evidenceExport, context))

            savedSupportDiagnosticsPackage = try clientDiagnosticStore.savePackage(
                additionalArtifacts: additionalArtifacts,
                now: now
            )
            let artifactCount = savedSupportDiagnosticsPackage?.artifactURLs.count ?? 0
            lastActionMessage = "Saved support diagnostics package with \(artifactCount) artifact\(artifactCount == 1 ? "" : "s")."
        } catch {
            savedSupportDiagnosticsPackage = nil
            lastActionMessage = "Support diagnostics export failed: \(error.localizedDescription)"
        }
    }

    func saveFirstRunSupportDiagnosticPackage(rootStateSnapshot: [String: Any]) {
        saveSupportDiagnosticPackage(rootStateSnapshot: rootStateSnapshot)
    }

    func uploadSupportDiagnosticsManually(termsVersion: String = "alpha_privacy_terms_v0_1") async {
        guard !isDiagnosticUploadInFlight else {
            return
        }

        lastActionMessage = "Preparing support diagnostics upload..."

        if savedSupportDiagnosticsPackage == nil {
            saveSupportDiagnosticPackage()
        }

        guard let package = savedSupportDiagnosticsPackage else {
            lastActionMessage = "Prepare support diagnostics before uploading."
            return
        }

        guard !package.artifactURLs.isEmpty else {
            lastActionMessage = "Support diagnostics package has no artifacts to upload."
            return
        }

        guard supabaseConfig.isConfiguredForRemoteCalls else {
            lastActionMessage = "Support diagnostics upload is not configured in this build. Use Share Support Diagnostics instead."
            return
        }

        isDiagnosticUploadInFlight = true
        lastActionMessage = "Uploading \(package.artifactURLs.count) support diagnostic artifact\(package.artifactURLs.count == 1 ? "" : "s") to Cartenza..."
        defer {
            isDiagnosticUploadInFlight = false
        }

        do {
            let accessToken = try await diagnosticUploadAccessToken()
            let result = try await diagnosticUploadClient.uploadDiagnostics(
                DiagnosticUploadRequest(
                    testerAlias: supabaseConfig.testerAlias,
                    package: package,
                    requestedAt: Date(),
                    sourceAppVersion: Self.appVersion,
                    sourceAppBuild: Self.appBuild,
                    termsVersion: termsVersion,
                    acceptedAt: Date()
                ),
                accessToken: accessToken
            )
            lastDiagnosticUploadResult = result
            let authDetail = result.userIDPresent == true ? "authenticated" : "missing user id"
            lastActionMessage = "Support diagnostics upload \(result.status): \(result.uploadedCount) artifact\(result.uploadedCount == 1 ? "" : "s") (\(authDetail))."
        } catch {
            recordClientErrorDiagnostic(error, category: "diagnostic_upload_failed")
            lastActionMessage = "Support diagnostics upload failed: \(error.localizedDescription)"
        }
    }

    private func diagnosticUploadAccessToken() async throws -> String {
        do {
            return try await supabaseAuth.validAccessToken()
        } catch {
            guard let anonKey = supabaseConfig.anonKey,
                  !anonKey.isEmpty else {
                throw error
            }
            return anonKey
        }
    }

    func switchToLiveMusicKitForPlayback() async {
        musicServiceMode = .liveMusicKit
        _ = await ensureCanUseActiveMusicService()
    }

    private func markSelectedItem(_ status: ResolutionStatus, reason: String) {
        guard let item = selectedItem else {
            lastActionMessage = "Select an item before marking status."
            return
        }

        let now = Date()
        resolutions[item.itemID] = .marked(status, reason: reason, resolvedAt: now)
        playbackRecords[item.itemID] = status == .skipped ? .skipped(at: now) : .notAttempted()
        exportPreview = nil
        savedExport = nil
        persistCurrentSession()
        lastActionMessage = "Marked \(item.title) as \(status.rawValue)."
    }

    private func restoreSessionState(for mission: Mission, persistedSession: PersistedMissionSession?) {
        self.mission = mission
        let itemIDs = Set(mission.items.map(\.itemID))
        let restoredSelectedItemID = persistedSession?.selectedItemID.flatMap { itemIDs.contains($0) ? $0 : nil }
        selectedItemID = restoredSelectedItemID ?? mission.items.first?.itemID
        resolutions = Dictionary(uniqueKeysWithValues: mission.items.map { item in
            (item.itemID, persistedSession?.resolutions[item.itemID] ?? item.appleMusicResolution)
        })
        playbackRecords = Dictionary(uniqueKeysWithValues: mission.items.map { item in
            (item.itemID, persistedSession?.playbackRecords[item.itemID] ?? PlaybackRecord.notAttempted())
        })
        playerActionLog = []
        reactionStore.replaceAll(with: persistedSession?.reactions.filter { itemIDs.contains($0.key) } ?? [:])
        reactionRevision += 1
        exportPreview = nil
        savedExport = nil
        activePlaybackSnapshot = .idle
        observedPlaybackItemID = nil
        stopPlaybackPolling()
        lastActionMessage = nil
    }

    private func reloadMissionCatalog(selectMissionID: String? = nil) {
        do {
            let loadedCatalog = try missionProvider.loadMissionCatalog()
            missionCatalog = loadedCatalog
            availableMissions = loadedCatalog.allMissions

            guard !availableMissions.isEmpty else {
                clearActiveMissionState()
                missionLoadState = .loaded
                return
            }

            let selectedMission = selectMissionID.flatMap { missionID in
                availableMissions.first { $0.missionID == missionID }
            } ?? persistedSessionLibrary.activeMissionID.flatMap { missionID in
                availableMissions.first { $0.missionID == missionID }
            } ?? availableMissions.first

            if let selectedMission {
                restoreSessionState(
                    for: selectedMission,
                    persistedSession: persistedSessionLibrary.sessionsByMissionID[selectedMission.missionID]
                )
            }
            missionLoadState = .loaded
        } catch {
            missionLoadState = .failed(error.localizedDescription)
        }
    }

    private func clearActiveMissionState() {
        mission = nil
        selectedItemID = nil
        resolutions = [:]
        playbackRecords = [:]
        playerActionLog = []
        reactionStore.replaceAll(with: [:])
        reactionRevision += 1
        exportPreview = nil
        savedExport = nil
        activePlaybackSnapshot = .idle
        observedPlaybackItemID = nil
        stopPlaybackPolling()
    }

    private func persistCurrentSession() {
        guard let mission else {
            return
        }

        let now = Date()
        let session = PersistedMissionSession(
            missionID: mission.missionID,
            selectedItemID: selectedItemID,
            resolutions: resolutions,
            playbackRecords: playbackRecords,
            reactions: reactionStore.allReactions(),
            updatedAt: now
        )

        persistedSessionLibrary.activeMissionID = mission.missionID
        persistedSessionLibrary.sessionsByMissionID[mission.missionID] = session
        persistedSessionLibrary.savedExports = savedExports
        persistedSessionLibrary.updatedAt = now

        do {
            try sessionPersistenceStore.save(persistedSessionLibrary)
        } catch {
            lastActionMessage = "Could not persist session locally: \(error.localizedDescription)"
        }
    }

    private func exportableEvidenceItems(includeStubEvidence: Bool) -> [SessionItemEvidence] {
        guard let mission else {
            return []
        }

        return mission.items.compactMap { item in
            let resolution = resolution(for: item)
            let playback = playback(for: item)

            guard resolution.status == .resolved else {
                return nil
            }

            guard includeStubEvidence || !resolution.isDevelopmentStubEvidence else {
                return nil
            }

            guard playback.hasExportablePlaybackEvidence else {
                return nil
            }

            guard let reaction = reactionStore.reaction(for: item.itemID) else {
                return nil
            }

            return SessionItemEvidence(
                item: item,
                resolution: resolution,
                playback: playback,
                reaction: reaction
            )
        }
    }

    func missionReviewEvidence(for itemID: String) -> MissionReviewItemEvidence? {
        guard let item = mission?.items.first(where: { $0.itemID == itemID }) else {
            return nil
        }

        return MissionReviewItemEvidence(
            item: item,
            resolution: resolution(for: item),
            playback: playback(for: item),
            reaction: reactionStore.reaction(for: item.itemID)
        )
    }

    func refreshActivePlaybackSnapshot() async {
        guard let observedPlaybackItemID else {
            return
        }

        await refreshPlaybackSnapshot(for: observedPlaybackItemID)
    }

    private var activeSearchService: any MusicSearchServing {
        switch musicServiceMode {
        case .developmentStub:
            return stubSearchService
        case .liveMusicKit:
            return liveSearchService
        }
    }

    private var activePlaybackService: any MusicPlaybackServing {
        switch musicServiceMode {
        case .developmentStub:
            return stubPlaybackService
        case .liveMusicKit:
            return livePlaybackService
        }
    }

    private func needsResolutionForActivePlayback(_ resolution: AppleMusicResolution) -> Bool {
        resolution.status != .resolved ||
        (musicServiceMode == .liveMusicKit && resolution.isDevelopmentStubEvidence)
    }

    private func ensureCanUseActiveMusicService() async -> Bool {
        guard musicServiceMode == .liveMusicKit else {
            return true
        }

        if !isAppleMusicAuthorized,
           musicAuthorizationSnapshot.canRequestAuthorization {
            await musicAuthorization.requestAuthorization()
        } else {
            musicAuthorization.refreshStatus()
        }

        guard isAppleMusicAuthorized else {
            lastActionMessage = "Apple Music authorization is \(musicAuthorizationSnapshot.status). Request access before using Live MusicKit."
            return false
        }

        return true
    }

    private func startPlaybackPolling(for itemID: String) {
        guard musicServiceMode == .liveMusicKit else {
            return
        }

        playbackPollingTask?.cancel()
        playbackPollingTask = Task { @MainActor [weak self] in
            while !Task.isCancelled {
                await self?.refreshPlaybackSnapshot(for: itemID)
                try? await Task.sleep(nanoseconds: 500_000_000)
            }
        }
    }

    private func stopPlaybackPolling() {
        playbackPollingTask?.cancel()
        playbackPollingTask = nil
        playbackPollingSuppressedUntil = nil
    }

    private func suppressPlaybackPollingBriefly() {
        guard musicServiceMode == .liveMusicKit else {
            return
        }

        playbackPollingSuppressedUntil = Date().addingTimeInterval(0.85)
    }

    private func refreshPlaybackSnapshot(for itemID: String) async {
        guard observedPlaybackItemID == itemID else {
            stopPlaybackPolling()
            return
        }

        if let playbackPollingSuppressedUntil,
           Date() < playbackPollingSuppressedUntil {
            return
        }
        playbackPollingSuppressedUntil = nil

        guard let item = mission?.items.first(where: { $0.itemID == itemID }) else {
            stopPlaybackPolling()
            return
        }

        let currentPlayback = playback(for: item)
        let snapshot = activePlaybackService.snapshot(currentPlayback: currentPlayback)
        activePlaybackSnapshot = snapshot

        if shouldFinalizePlaybackAsCompleted(currentPlayback, snapshot: snapshot) {
            let completedAt = Date()
            playbackRecords[itemID] = currentPlayback.endedAsPlayed(at: completedAt)
            activePlaybackSnapshot = PlaybackSnapshot.from(record: playbackRecords[itemID] ?? currentPlayback)
            ensureDefaultNoSignalReaction(for: item, at: completedAt)
            appendPlayerAction(.completedByThreshold, item: item, at: completedAt)
            exportPreview = nil
            savedExport = nil
            persistCurrentSession()
            lastActionMessage = "Completed \(item.title)."
            stopPlaybackPolling()
            await playNextPlayableItem(afterCompletedItemID: itemID)
        }
    }

    private func shouldFinalizePlaybackAsCompleted(
        _ playback: PlaybackRecord,
        snapshot: PlaybackSnapshot
    ) -> Bool {
        guard playback.status == .playing else {
            return false
        }

        guard let startedAt = playback.startedAt else {
            return false
        }

        guard snapshot.runtimeStatus == .stopped || snapshot.runtimeStatus == .completed else {
            return false
        }

        guard let totalDuration = snapshot.totalDurationSeconds ?? playback.durationSeconds,
              totalDuration > 0 else {
            return true
        }

        let wallElapsed = max(0, Date().timeIntervalSince(startedAt))
        let observedElapsed = snapshot.elapsedSeconds > 0.5 ? snapshot.elapsedSeconds : wallElapsed
        guard observedElapsed / totalDuration >= 0.9 else {
            return false
        }

        return true
    }

    private func playNextPlayableItem(afterCompletedItemID itemID: String) async {
        guard let mission,
              let completedIndex = mission.items.firstIndex(where: { $0.itemID == itemID }),
              completedIndex < mission.items.count - 1 else {
            return
        }

        await playNextPlayableItem(startingAt: completedIndex + 1)
    }

    private func playNextPlayableItem(startingAt startIndex: Int) async {
        guard let mission, startIndex < mission.items.count else {
            lastActionMessage = "Reached the end of the mission."
            return
        }

        guard await ensureCanUseActiveMusicService() else {
            return
        }

        var skippedUnplayableTitles: [String] = []

        for candidateIndex in startIndex..<mission.items.count {
            let item = mission.items[candidateIndex]
            selectItem(item)

            if await playSelectedItemResolvingIfNeeded() {
                if !skippedUnplayableTitles.isEmpty {
                    lastActionMessage = "Skipped \(skippedUnplayableTitles.count) unresolved item(s), then started \(item.title)."
                }
                return
            }

            if resolution(for: item).status != .resolved {
                skippedUnplayableTitles.append(item.title)
                appendPlayerAction(.skipUnresolved, item: item, at: Date())
                persistCurrentSession()
            } else {
                return
            }
        }

        lastActionMessage = skippedUnplayableTitles.isEmpty
            ? "Reached the end of the mission."
            : "Reached the end of the mission after skipping \(skippedUnplayableTitles.count) unresolved item(s)."
    }

    private func appendPlayerAction(_ action: PlayerActionKind, item: MissionItem, at date: Date) {
        playerActionLog.append(
            PlayerActionLogEntry(
                itemID: item.itemID,
                itemTitle: item.title,
                action: action,
                occurredAt: date
            )
        )
    }

    private struct GenerationResponseSummary {
        let runID: String?
        let status: String
        let appImportStatus: String?
        let promptVersion: String?
        let adapterVersion: String?
        let appMissionCount: Int
        let appMissionIDs: [String]
        let statusReason: String?
        let validationMessages: [String]

        var isLocalStarterPack: Bool {
            runID?.hasPrefix("local_graph_native_starter_pack_") == true ||
                promptVersion == "graph_native_starter_pack_v0_1" ||
                adapterVersion == "local_graph_native_starter_pack_v0_1"
        }

        func retryIssueDescription(fallback: String) -> String {
            if let statusReason, !statusReason.isEmpty {
                return statusReason
            }

            if let firstMessage = validationMessages.first, !firstMessage.isEmpty {
                return firstMessage
            }

            return fallback
        }
    }

    private func clientDiagnosticContext(
        surveySessionID: String? = nil,
        clientRequestID: String? = nil,
        generationRunID: String? = nil,
        missionID: String? = nil
    ) -> ClientDiagnosticLinkContext {
        ClientDiagnosticLinkContext(
            testerAlias: supabaseConfig.testerAlias,
            supabaseUserID: supabaseAuthSnapshot.userID,
            surveySessionID: surveySessionID,
            clientRequestID: clientRequestID,
            generationRunID: generationRunID,
            missionID: missionID,
            sourceAppVersion: Self.appVersion,
            sourceAppBuild: Self.appBuild
        )
    }

    private func makeClientStateSnapshotPayload(
        rootStateSnapshot: [String: Any]?,
        surveySession: PersistedSurveySession,
        now: Date
    ) -> [String: Any] {
        let surveyDisplayedPages = surveySession.displayedPages
            .sorted { $0.key < $1.key }
            .map { key, page in
                [
                    "step": key,
                    "page_id": page.id,
                    "item_count": page.items.count
                ] as [String: Any]
            }
        let environment = musicAuthorization.environmentSnapshot

        return compactDiagnosticDictionary([
            "schema_version": "waymark.client_state_snapshot.v0.1",
            "captured_at": ISO8601DateFormatter().string(from: now),
            "source_app_version": Self.appVersion,
            "source_app_build": Self.appBuild,
            "root_state": rootStateSnapshot,
            "mission_generation": compactDiagnosticDictionary([
                "state": loadStateDiagnosticValue(firstMissionGenerationState),
                "progress_completed_count": firstMissionGenerationProgress.completedCount,
                "progress_target_count": firstMissionGenerationProgress.targetCount,
                "progress_active_mission_number": firstMissionGenerationProgress.activeMissionNumber,
                "progress_detail": firstMissionGenerationProgress.detail,
                "reviewed_mission_count": reviewedMissionAssignmentCount,
                "target_mission_count": AlphaMissionGenerationConfig.requiredMissionCount,
                "minimum_usable_mission_count": AlphaMissionGenerationConfig.minimumUsableMissionCount,
                "max_generation_attempt_count": AlphaMissionGenerationConfig.maxGenerationAttemptCount,
                "mission_ids": availableMissions.map(\.missionID),
                "last_action_message": lastActionMessage
            ]),
            "survey": [
                "survey_session_id": surveySession.surveySessionID,
                "current_step": surveySession.currentStep.rawValue,
                "response_count": surveySession.responses.count,
                "freeform_signal_count": surveySession.freeformSignals.count,
                "displayed_page_count": surveySession.displayedPages.count,
                "displayed_pages": surveyDisplayedPages,
                "apple_music_payload_present": surveySession.appleMusicSignalPayload != nil
            ],
            "auth": compactDiagnosticDictionary([
                "supabase_status": supabaseAuthSnapshot.status.rawValue,
                "supabase_user_id_present": supabaseAuthSnapshot.userID != nil,
                "supabase_expires_at": supabaseAuthSnapshot.expiresAt.map { ISO8601DateFormatter().string(from: $0) },
                "supabase_configured": supabaseConfig.isConfiguredForRemoteCalls,
                "music_authorization_status": musicAuthorizationSnapshot.status,
                "music_authorization_detail": musicAuthorizationSnapshot.detail,
                "music_can_request_authorization": musicAuthorizationSnapshot.canRequestAuthorization,
                "music_environment_status": environment.status,
                "music_storefront": environment.storefront,
                "music_can_play_catalog_content": environment.canPlayCatalogContent,
                "music_cloud_library_enabled": environment.hasCloudLibraryEnabled
            ]),
            "local_session": compactDiagnosticDictionary([
                "active_mission_id": mission?.missionID,
                "selected_item_id": selectedItemID,
                "saved_export_count": savedExports.count,
                "diagnostic_package_prepared": savedSupportDiagnosticsPackage != nil,
                "last_diagnostic_upload_status": lastDiagnosticUploadResult?.status,
                "last_evidence_upload_status": lastEvidenceUploadResult?.status
            ]),
            "redaction": [
                "auth_tokens_included": false,
                "service_role_keys_included": false,
                "apple_identity_tokens_included": false,
                "raw_apple_payload_included": false
            ]
        ])
    }

    private func recordMissionGenerationRequestDiagnostic(request: MissionGenerationRequest) {
        let context = clientDiagnosticContext(
            surveySessionID: currentSurveySessionID(),
            clientRequestID: request.clientRequestID
        )
        let payload: [String: Any] = [
            "client_request_id": request.clientRequestID,
            "requested_batch_size": request.requestedBatchSize,
            "tester_alias": request.testerAlias,
            "already_selected_route_item_ids": request.alreadySelectedRouteItemIDs,
            "already_selected_route_display_identity_keys": request.alreadySelectedRouteDisplayIdentityKeys,
            "already_selected_display_keys": request.alreadySelectedRouteDisplayIdentityKeys,
            "prompt_context": (try? SupabaseJSON.object(from: request.promptContext)) ?? [:],
            "survey_evidence_export": (try? SupabaseJSON.object(from: request.surveyEvidenceExport)) ?? [:],
            "mission_generation_digest_view": (try? SupabaseJSON.object(from: request.missionGenerationDigestView)) ?? [:],
            "candidate_pool": (try? SupabaseJSON.object(from: request.candidatePool)) ?? [:],
            "diagnostic_policy": [
                "support_only": true,
                "automatic_upload_enabled": false,
                "atlas_truth_writes_allowed": false
            ]
        ]
        recordClientDiagnosticArtifact(
            type: .missionGenerationRequestPacket,
            payload: payload,
            context: context
        )
    }

    @discardableResult
    private func recordMissionGenerationResultDiagnostic(
        responseData: Data,
        request: MissionGenerationRequest
    ) -> GenerationResponseSummary {
        let responseObject = (try? SupabaseJSON.object(from: responseData)) as? [String: Any] ?? [:]
        let summary = generationResponseSummary(from: responseObject)
        let context = clientDiagnosticContext(
            surveySessionID: currentSurveySessionID(),
            clientRequestID: request.clientRequestID,
            generationRunID: summary.runID
        )
        let payload = compactDiagnosticDictionary([
            "client_request_id": request.clientRequestID,
            "generation_run_id": summary.runID,
            "status": summary.status,
            "app_import_status": summary.appImportStatus,
            "app_mission_count": summary.appMissionCount,
            "app_mission_ids": summary.appMissionIDs,
            "status_reason": summary.statusReason,
            "validation_messages": summary.validationMessages,
            "raw_response": responseObject
        ])
        recordClientDiagnosticArtifact(
            type: .missionGenerationResult,
            payload: payload,
            context: context
        )
        return summary
    }

    private func recordMissionImportResultDiagnostic(
        status: String,
        request: MissionGenerationRequest,
        responseSummary: GenerationResponseSummary,
        importedAssignments: [MissionAssignment],
        validationErrors: [String]
    ) {
        let context = clientDiagnosticContext(
            surveySessionID: currentSurveySessionID(),
            clientRequestID: request.clientRequestID,
            generationRunID: responseSummary.runID,
            missionID: importedAssignments.first?.mission.missionID
        )
        let payload = compactDiagnosticDictionary([
            "client_request_id": request.clientRequestID,
            "generation_run_id": responseSummary.runID,
            "generation_status": responseSummary.status,
            "local_import_status": status,
            "backend_app_mission_count": responseSummary.appMissionCount,
            "backend_app_mission_ids": responseSummary.appMissionIDs,
            "imported_mission_ids": importedAssignments.map { $0.mission.missionID },
            "already_selected_route_item_ids_sent": request.alreadySelectedRouteItemIDs,
            "already_selected_route_display_identity_keys_sent": request.alreadySelectedRouteDisplayIdentityKeys,
            "already_selected_display_keys_sent": request.alreadySelectedRouteDisplayIdentityKeys,
            "imported_route_item_ids": Array(MissionImportGate.routeItemIDs(in: importedAssignments)).sorted(),
            "imported_route_display_identity_keys": Array(MissionImportGate.routeDisplayIdentityKeys(in: importedAssignments)).sorted(),
            "imported_candidate_ids": Array(MissionImportGate.routeCandidateIDs(in: importedAssignments)).sorted(),
            "imported_route_identity": MissionImportGate.routeIdentityMetadata(in: importedAssignments),
            "imported_item_counts": importedAssignments.map { assignment in
                [
                    "mission_id": assignment.mission.missionID,
                    "item_count": assignment.mission.items.count
                ]
            },
            "local_validation_errors": validationErrors,
            "local_mission_catalog_count_after_attempt": reviewedMissionAssignmentCount + importedAssignments.count
        ])
        recordClientDiagnosticArtifact(
            type: .missionImportResult,
            payload: payload,
            context: context
        )
    }

    private func makeReviewedMissionCatalogSnapshotPayload(
        surveySession: PersistedSurveySession,
        now: Date
    ) -> [String: Any] {
        do {
            let catalog = try missionProvider.loadMissionCatalog()
            let assignments = catalog.reviewedAssignments
            let appMissions = try jsonObject(from: assignments.map(\.mission)) as? [[String: Any]] ?? []
            let reviewedAssignments = try jsonObject(from: assignments) as? [[String: Any]] ?? []
            let routeItemCount = assignments.flatMap { $0.mission.items }.count

            return compactDiagnosticDictionary([
                "schema_version": "cartenza.reviewed_mission_catalog_snapshot.v0.1",
                "captured_at": ISO8601DateFormatter().string(from: now),
                "survey_session_id": surveySession.surveySessionID,
                "source_app_version": Self.appVersion,
                "source_app_build": Self.appBuild,
                "snapshot_status": "captured",
                "artifact_role": "reviewed_mission_catalog_snapshot",
                "survey_link": compactDiagnosticDictionary([
                    "survey_session_id": surveySession.surveySessionID,
                    "survey_response_count": surveySession.responses.count,
                    "displayed_page_count": surveySession.displayedPages.count,
                    "freeform_signal_count": surveySession.freeformSignals.count,
                    "survey_updated_at": surveySession.updatedAt.map { ISO8601DateFormatter().string(from: $0) },
                    "apple_music_payload_present": surveySession.appleMusicSignalPayload != nil,
                    "companion_artifact_types": [
                        ClientDiagnosticArtifactType.surveyEvidenceExport.rawValue,
                        ClientDiagnosticArtifactType.surveyPageSelectionAudit.rawValue,
                        ClientDiagnosticArtifactType.appleMusicSignalPayload.rawValue
                    ]
                ]),
                "mission_catalog": [
                    "reviewed_mission_count": assignments.count,
                    "route_item_count": routeItemCount,
                    "all_missions_playback_ready": !assignments.isEmpty && assignments.allSatisfy { $0.mission.isPlaybackReady },
                    "mission_ids": assignments.map { $0.mission.missionID },
                    "source_run_ids": Array(Set(assignments.compactMap(\.sourceRunID))).sorted()
                ],
                "mission_summaries": assignments.map(reviewedMissionDiagnosticSummary),
                "app_missions": appMissions,
                "reviewed_assignments": reviewedAssignments,
                "diagnostic_policy": [
                    "support_only": true,
                    "read_only_snapshot": true,
                    "survey_responses_preserved": true,
                    "mission_catalog_preserved": true,
                    "generation_not_invoked": true,
                    "atlas_truth_writes_allowed": false,
                    "copy_review_allowed": true,
                    "composition_review_allowed": true
                ]
            ])
        } catch {
            return [
                "schema_version": "cartenza.reviewed_mission_catalog_snapshot.v0.1",
                "captured_at": ISO8601DateFormatter().string(from: now),
                "survey_session_id": surveySession.surveySessionID,
                "source_app_version": Self.appVersion,
                "source_app_build": Self.appBuild,
                "snapshot_status": "capture_failed",
                "artifact_role": "reviewed_mission_catalog_snapshot",
                "error_description": error.localizedDescription,
                "diagnostic_policy": [
                    "support_only": true,
                    "read_only_snapshot": true,
                    "survey_responses_preserved": true,
                    "mission_catalog_preserved": true,
                    "generation_not_invoked": true,
                    "atlas_truth_writes_allowed": false
                ]
            ]
        }
    }

    private func reviewedMissionDiagnosticSummary(_ assignment: MissionAssignment) -> [String: Any] {
        let mission = assignment.mission
        return compactDiagnosticDictionary([
            "mission_id": mission.missionID,
            "mission_title": mission.missionTitle,
            "mission_type": mission.missionType.rawValue,
            "mission_version": mission.missionVersion,
            "alpha_app_import_status": mission.alphaAppImportStatus?.rawValue,
            "alpha_mission_archetype": mission.alphaMissionArchetype,
            "brief": mission.brief,
            "hypothesis": mission.hypothesis,
            "why_this_mission_now": mission.whyThisMissionNow,
            "risk_level": mission.riskLevel,
            "source_trace_summary": mission.sourceTraceSummary,
            "source": assignment.source.rawValue,
            "source_run_id": assignment.sourceRunID,
            "import_note": assignment.importNote,
            "imported_at": ISO8601DateFormatter().string(from: assignment.importedAt),
            "item_count": mission.items.count,
            "is_playback_ready": mission.isPlaybackReady,
            "route_items": mission.items.map(reviewedMissionRouteItemDiagnosticSummary)
        ])
    }

    private func reviewedMissionRouteItemDiagnosticSummary(_ item: MissionItem) -> [String: Any] {
        compactDiagnosticDictionary([
            "item_id": item.itemID,
            "sequence": item.sequence,
            "item_type": item.itemType.rawValue,
            "artist": item.artist,
            "title": item.title,
            "album": item.album,
            "year": item.year,
            "why_included": item.whyIncluded,
            "expected_test_signal": item.expectedTestSignal,
            "alpha_route_role": item.alphaRouteRole?.rawValue,
            "alpha_resolution_status": item.alphaResolutionStatus?.rawValue,
            "alpha_source_opportunity_id": item.alphaSourceOpportunityID,
            "alpha_source_mission_type": item.alphaSourceMissionType,
            "alpha_target_object_ids": item.alphaTargetObjectIDs,
            "alpha_graph_context_refs": item.alphaGraphContextRefs,
            "candidate_id": item.candidateID,
            "route_candidate_key": item.routeCandidateKey,
            "route_batch_dedupe_key": item.routeBatchDedupeKey,
            "route_display_identity_key": item.routeDisplayIdentityKey,
            "apple_catalog_id": item.appleMusicResolution.catalogID,
            "apple_catalog_url": item.appleMusicResolution.catalogURL?.absoluteString,
            "apple_resolution_status": item.appleMusicResolution.status.rawValue,
            "apple_resolved_title": item.appleMusicResolution.resolvedTitle,
            "apple_resolved_artist": item.appleMusicResolution.resolvedArtist,
            "apple_resolved_album": item.appleMusicResolution.resolvedAlbum,
            "feedback_chip_sets": item.feedbackChipSets?.mapValues { chips in
                chips.map { chip in
                    compactDiagnosticDictionary([
                        "tag_id": chip.tagID,
                        "label": chip.label,
                        "description": chip.description
                    ])
                }
            }
        ])
    }

    private func recordLocalMissionSelectionAuditDiagnostic(
        responseData: Data,
        importedAssignments: [MissionAssignment],
        localImportStatus: String,
        importError: Error? = nil
    ) {
        let responseObject = (try? SupabaseJSON.object(from: responseData)) as? [String: Any] ?? [:]
        let summary = generationResponseSummary(from: responseObject)
        let selectionAudit = responseObject["selection_audit"] as? [String: Any]
        let context = clientDiagnosticContext(
            surveySessionID: currentSurveySessionID(),
            missionID: importedAssignments.first?.mission.missionID
        )
        let importedItems = importedAssignments.flatMap { assignment in
            assignment.mission.items.map { item in
                compactDiagnosticDictionary([
                    "mission_id": assignment.mission.missionID,
                    "item_id": item.itemID,
                    "sequence": item.sequence,
                    "title": item.title,
                    "artist": item.artist,
                    "candidate_id": item.candidateID,
                    "route_display_identity_key": item.routeDisplayIdentityKey,
                    "apple_catalog_id": item.appleMusicResolution.catalogID,
                    "apple_catalog_url": item.appleMusicResolution.catalogURL?.absoluteString,
                    "alpha_route_role": item.alphaRouteRole?.rawValue,
                    "alpha_resolution_status": item.alphaResolutionStatus?.rawValue
                ])
            }
        }
        let payload = compactDiagnosticDictionary([
            "schema_version": "cartenza.local_mission_selection_audit_diagnostic.v0.1",
            "captured_at": ISO8601DateFormatter().string(from: Date()),
            "run_id": summary.runID,
            "status": summary.status,
            "app_import_status": summary.appImportStatus,
            "adapter_version": summary.adapterVersion,
            "local_import_status": localImportStatus,
            "import_error": importError.map(\.localizedDescription),
            "app_mission_count": summary.appMissionCount,
            "app_mission_ids": summary.appMissionIDs,
            "imported_mission_ids": importedAssignments.map { $0.mission.missionID },
            "imported_route_item_count": importedItems.count,
            "imported_route_items": importedItems,
            "selection_audit": selectionAudit,
            "generation": responseObject["generation"] as? [String: Any],
            "alpha_import_policy": responseObject["alpha_import_policy"] as? [String: Any],
            "validation": responseObject["validation"] as? [String: Any],
            "diagnostic_policy": [
                "support_only": true,
                "automatic_upload_enabled": false,
                "atlas_truth_writes_allowed": false,
                "generation_run_id_context_omitted": "Local selector run ids are diagnostic strings, not Supabase UUIDs."
            ],
            "raw_response": responseObject
        ])
        recordClientDiagnosticArtifact(
            type: .missionSelectionAudit,
            payload: payload,
            context: context
        )
    }

    private func recordClientErrorDiagnostic(_ error: Error, category: String, clientRequestID: String? = nil) {
        let context = clientDiagnosticContext(
            surveySessionID: currentSurveySessionID(),
            clientRequestID: clientRequestID
        )
        let payload: [String: Any] = [
            "error_category": category,
            "error_description": error.localizedDescription,
            "auth_status": supabaseAuthSnapshot.status.rawValue,
            "supabase_configured": supabaseConfig.isConfiguredForRemoteCalls,
            "first_mission_generation_state": String(describing: firstMissionGenerationState),
            "reviewed_mission_count": reviewedMissionAssignmentCount
        ]
        recordClientDiagnosticArtifact(
            type: .clientErrorEvent,
            payload: payload,
            context: context
        )
    }

    private func recordClientDiagnosticArtifact(
        type: ClientDiagnosticArtifactType,
        payload: [String: Any],
        context: ClientDiagnosticLinkContext
    ) {
        do {
            try clientDiagnosticStore.saveArtifact(
                type: type,
                payload: payload,
                context: context
            )
        } catch {
            lastActionMessage = "Support diagnostic capture failed: \(error.localizedDescription)"
        }
    }

    private func generationResponseSummary(from responseObject: [String: Any]) -> GenerationResponseSummary {
        let appMissions = responseObject["app_missions"] as? [[String: Any]] ?? []
        let appMissionIDs = appMissions.compactMap { $0["mission_id"] as? String }
        let validation = responseObject["validation"] as? [String: Any] ?? [:]
        let alphaImportPolicy = validation["alpha_import_policy"] as? [String: Any] ?? [:]
        return GenerationResponseSummary(
            runID: responseObject["run_id"] as? String,
            status: responseObject["status"] as? String ?? "unknown",
            appImportStatus: responseObject["app_import_status"] as? String,
            promptVersion: responseObject["prompt_version"] as? String,
            adapterVersion: responseObject["adapter_version"] as? String,
            appMissionCount: appMissions.count,
            appMissionIDs: appMissionIDs,
            statusReason: alphaImportPolicy["status_reason"] as? String,
            validationMessages: generationValidationMessages(from: validation)
        )
    }

    private func generationValidationMessages(from validation: [String: Any]) -> [String] {
        var messages = [String]()
        if let generation = validation["generation"] as? [String: Any] {
            messages.append(contentsOf: stringArray(generation["errors"]))
        }
        if let appMission = validation["app_mission"] as? [String: Any] {
            messages.append(contentsOf: stringArray(appMission["errors"]))
        }
        if let routeIdentity = validation["route_identity"] as? [String: Any] {
            messages.append(contentsOf: routeIdentityIssueMessages(from: routeIdentity))
        }

        return Array(NSOrderedSet(array: messages.compactMap { message in
            let trimmed = message.trimmingCharacters(in: .whitespacesAndNewlines)
            return trimmed.isEmpty ? nil : trimmed
        })) as? [String] ?? []
    }

    private func routeIdentityIssueMessages(from routeIdentity: [String: Any]) -> [String] {
        let issueKeys = [
            "duplicate_route_item_ids": "duplicate route item",
            "duplicate_candidate_ids": "duplicate candidate",
            "duplicate_display_identity_keys": "duplicate display identity",
            "missing_candidate_id_refs": "missing candidate ref",
            "non_candidate_ids": "non-candidate",
            "repeated_route_item_ids_from_batch_memory": "repeated route item",
            "repeated_candidate_ids_from_batch_memory": "repeated candidate",
            "repeated_display_keys_from_batch_memory": "repeated display identity"
        ]
        return issueKeys.flatMap { key, label in
            stringArray(routeIdentity[key]).map { "\(label): \($0)" }
        }
    }

    private func stringArray(_ rawValue: Any?) -> [String] {
        if let values = rawValue as? [String] {
            return values
        }

        if let values = rawValue as? [Any] {
            return values.compactMap { $0 as? String }
        }

        return []
    }

    private func localImportStatus(for error: Error, generationStatus: String) -> String {
        if generationStatus == "review_needed" {
            return "skipped_review_needed"
        }

        guard let importError = error as? MissionImportError else {
            return "client_error"
        }

        switch importError {
        case .blockedStatus(let status):
            return status == "review_needed" ? "skipped_review_needed" : "blocked"
        case .missingAppMissions:
            return generationStatus == "review_needed" ? "skipped_review_needed" : "missing_app_missions"
        case .invalidMission:
            return "validation_failed"
        case .invalidJSON, .emptyImport:
            return "client_error"
        }
    }

    private func shouldContinueGeneration(after error: Error, generationStatus: String) -> Bool {
        if generationStatus == "review_needed" {
            return true
        }

        if let importError = error as? MissionImportError {
            switch importError {
            case .missingAppMissions:
                return generationStatus == "app_import_candidate" ||
                    generationStatus == "review_needed" ||
                    generationStatus == "blocked"
            case .blockedStatus(let status):
                return status == "blocked" || status == "review_needed"
            case .invalidMission:
                return true
            case .invalidJSON, .emptyImport:
                return false
            }
        }

        return false
    }

    private func currentSurveySessionID() -> String? {
        surveyEvidenceBuilder.loadPersistedSurveySession().surveySessionID
    }

    private func compactDiagnosticDictionary(_ dictionary: [String: Any?]) -> [String: Any] {
        dictionary.reduce(into: [String: Any]()) { result, pair in
            if let value = pair.value {
                result[pair.key] = value
            }
        }
    }

    private func jsonObject<T: Encodable>(from value: T) throws -> Any {
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        encoder.outputFormatting = [.sortedKeys]
        let data = try encoder.encode(value)
        return try JSONSerialization.jsonObject(with: data)
    }

    private func loadStateDiagnosticValue(_ state: LoadState) -> String {
        switch state {
        case .idle:
            return "idle"
        case .loading:
            return "loading"
        case .loaded:
            return "loaded"
        case .failed(let message):
            return "failed: \(message)"
        }
    }

    private func withTimeout<T>(
        seconds: TimeInterval,
        operation: @escaping @Sendable () async throws -> T
    ) async throws -> T {
        try await withThrowingTaskGroup(of: T.self) { group in
            group.addTask {
                try await operation()
            }
            group.addTask {
                try await Task.sleep(nanoseconds: UInt64(seconds * 1_000_000_000))
                throw TimeoutError(seconds: seconds)
            }

            guard let result = try await group.next() else {
                throw CancellationError()
            }
            group.cancelAll()
            return result
        }
    }

    private func ensureDefaultNoSignalReaction(for item: MissionItem, at date: Date) {
        guard reactionStore.reaction(for: item.itemID) == nil else {
            return
        }

        do {
            try reactionStore.saveReaction(
                for: item.itemID,
                value: .unresolved,
                note: "",
                selectedTags: [],
                at: date
            )
            reactionRevision += 1
        } catch {
            lastActionMessage = error.localizedDescription
        }
    }

    private static var appVersion: String {
        Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "0.2"
    }

    private static var appBuild: String {
        Bundle.main.infoDictionary?["CFBundleVersion"] as? String ?? "0"
    }

    private static var defaultShouldClearLegacyAlphaUATFixturesOnLoad: Bool {
        #if DEBUG
        return false
        #else
        return Bundle.main.object(forInfoDictionaryKey: "CartenzaAlphaUATFixturesEnabled") as? Bool != true
        #endif
    }

    private static func containsOnlyLegacyAlphaUATFixtureAssignments(_ assignments: [MissionAssignment]) -> Bool {
        guard !assignments.isEmpty else {
            return false
        }

        return assignments.allSatisfy(isLegacyAlphaUATFixtureAssignment)
    }

    private static func isLegacyAlphaUATFixtureAssignment(_ assignment: MissionAssignment) -> Bool {
        let missionID = assignment.mission.missionID.uppercased()
        let importNote = assignment.importNote?.lowercased() ?? ""
        return assignment.source == .localAlphaFixture &&
            (assignment.sourceRunID == "alpha_mission_delivery_v0_2" || importNote.contains("uat fixture")) &&
            missionID.hasPrefix("MIS_ALPHA_MISSION_V0_2_")
    }

    private static func resolutionMessage(
        for resolution: AppleMusicResolution,
        item: MissionItem,
        serviceMode: MusicServiceMode
    ) -> String {
        if resolution.status == .failed {
            return [
                "\(serviceMode.displayName) resolution failed for \(item.title).",
                "reason=\(resolution.reason ?? "none")",
                "code=\(resolution.errorCode ?? "none")",
                "message=\(resolution.errorMessage ?? "none")"
            ].joined(separator: " ")
        }

        return "\(serviceMode.displayName) returned \(resolution.status.rawValue) for \(item.title)."
    }
}

extension AppModel.LoadState {
    var isLoading: Bool {
        if case .loading = self {
            return true
        }
        return false
    }

    var isFailed: Bool {
        if case .failed = self {
            return true
        }
        return false
    }
}

enum SupabaseAuthStatus: String, Codable, Equatable {
    case unconfigured
    case signedOut = "signed_out"
    case signingIn = "signing_in"
    case authenticated
    case expired
    case failed
}

struct SupabaseAuthSnapshot: Equatable {
    let status: SupabaseAuthStatus
    let detail: String
    let userID: String?
    let expiresAt: Date?

    static let unconfigured = SupabaseAuthSnapshot(
        status: .unconfigured,
        detail: "Supabase is not configured for this build.",
        userID: nil,
        expiresAt: nil
    )

    static let signedOut = SupabaseAuthSnapshot(
        status: .signedOut,
        detail: "Sign in with Apple to create a Cartenza Alpha session.",
        userID: nil,
        expiresAt: nil
    )

    var isAuthenticated: Bool {
        status == .authenticated
    }
}

@MainActor
final class SupabaseAuthService: ObservableObject {
    @Published private(set) var snapshot: SupabaseAuthSnapshot

    private let config: SupabaseAlphaConfig
    private let sessionStore: SupabaseSessionKeychainStore
    private var session: SupabaseAuthSession?
    private var urlSession: URLSession

    init(
        config: SupabaseAlphaConfig,
        sessionStore: SupabaseSessionKeychainStore = SupabaseSessionKeychainStore(),
        urlSession: URLSession = .shared
    ) {
        self.config = config
        self.sessionStore = sessionStore
        self.urlSession = urlSession

        if !config.isConfiguredForRemoteCalls {
            self.snapshot = .unconfigured
            self.session = nil
        } else if let storedSession = sessionStore.load() {
            self.session = storedSession
            self.snapshot = Self.snapshot(from: storedSession)
        } else {
            self.session = nil
            self.snapshot = .signedOut
        }
    }

    func signInWithApple(result: Result<ASAuthorization, Error>, rawNonce: String?) async throws {
        guard config.isConfiguredForRemoteCalls else {
            snapshot = .unconfigured
            throw SupabaseClientError.missingConfiguration
        }

        guard let rawNonce else {
            snapshot = SupabaseAuthSnapshot(
                status: .failed,
                detail: SupabaseClientError.missingNonce.localizedDescription,
                userID: nil,
                expiresAt: nil
            )
            throw SupabaseClientError.missingNonce
        }

        let authorization = try result.get()
        guard let credential = authorization.credential as? ASAuthorizationAppleIDCredential else {
            throw SupabaseClientError.missingAppleCredential
        }

        guard let identityToken = credential.identityToken,
              let identityTokenString = String(data: identityToken, encoding: .utf8),
              !identityTokenString.isEmpty else {
            throw SupabaseClientError.missingIdentityToken
        }

        snapshot = SupabaseAuthSnapshot(
            status: .signingIn,
            detail: "Signing in with Supabase.",
            userID: nil,
            expiresAt: nil
        )

        let session = try await exchangeAppleIDToken(identityTokenString, rawNonce: rawNonce)
        try sessionStore.save(session)
        self.session = session
        snapshot = Self.snapshot(from: session)
    }

    func validAccessToken(now: Date = Date()) async throws -> String {
        guard config.isConfiguredForRemoteCalls else {
            snapshot = .unconfigured
            throw SupabaseClientError.missingConfiguration
        }

        guard let session else {
            snapshot = .signedOut
            throw SupabaseClientError.httpFailure(statusCode: 401, body: "No Supabase Auth session is available.")
        }

        if session.isValid(now: now) {
            snapshot = Self.snapshot(from: session)
            return session.accessToken
        }

        guard !session.refreshToken.isEmpty else {
            snapshot = SupabaseAuthSnapshot(
                status: .expired,
                detail: "Supabase session expired. Sign in again.",
                userID: session.user?.id,
                expiresAt: session.expiresAtDate
            )
            throw SupabaseClientError.httpFailure(statusCode: 401, body: "Supabase session expired and cannot be refreshed.")
        }

        let refreshedSession = try await refreshSession(session.refreshToken)
        try sessionStore.save(refreshedSession)
        self.session = refreshedSession
        snapshot = Self.snapshot(from: refreshedSession)
        return refreshedSession.accessToken
    }

    func signOut() {
        sessionStore.clear()
        session = nil
        snapshot = config.isConfiguredForRemoteCalls ? .signedOut : .unconfigured
    }

    private func exchangeAppleIDToken(_ identityToken: String, rawNonce: String) async throws -> SupabaseAuthSession {
        let payload: [String: Any] = [
            "provider": "apple",
            "id_token": identityToken,
            "nonce": rawNonce
        ]
        return try await authTokenRequest(query: "grant_type=id_token", payload: payload)
    }

    private func refreshSession(_ refreshToken: String) async throws -> SupabaseAuthSession {
        try await authTokenRequest(
            query: "grant_type=refresh_token",
            payload: ["refresh_token": refreshToken]
        )
    }

    private func authTokenRequest(query: String, payload: [String: Any]) async throws -> SupabaseAuthSession {
        guard let projectURL = config.projectURL,
              let anonKey = config.anonKey,
              !anonKey.isEmpty else {
            throw SupabaseClientError.missingConfiguration
        }

        let url = projectURL
            .appendingPathComponent("auth")
            .appendingPathComponent("v1")
            .appendingPathComponent("token")
            .appending(queryItems: [URLQueryItem(name: "grant_type", value: query.replacingOccurrences(of: "grant_type=", with: ""))])

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue(anonKey, forHTTPHeaderField: "apikey")
        request.setValue("Bearer \(anonKey)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONSerialization.data(withJSONObject: payload, options: [.sortedKeys])

        let (data, response) = try await urlSession.data(for: request)
        try SupabaseHTTP.validate(response: response, data: data)

        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let session = try decoder.decode(SupabaseAuthSession.self, from: data)
        return session.withComputedExpiry()
    }

    private static func snapshot(from session: SupabaseAuthSession) -> SupabaseAuthSnapshot {
        guard session.isValid() else {
            return SupabaseAuthSnapshot(
                status: .expired,
                detail: "Supabase session expired. Sign in again.",
                userID: session.user?.id,
                expiresAt: session.expiresAtDate
            )
        }

        let userDetail = session.user?.id.map { "Supabase user \($0)" } ?? "Supabase session active."
        return SupabaseAuthSnapshot(
            status: .authenticated,
            detail: userDetail,
            userID: session.user?.id,
            expiresAt: session.expiresAtDate
        )
    }

    static func randomNonceString(length: Int = 32) -> String {
        precondition(length > 0)
        let charset = Array("0123456789ABCDEFGHIJKLMNOPQRSTUVXYZabcdefghijklmnopqrstuvwxyz-._")
        var result = ""
        var remainingLength = length

        while remainingLength > 0 {
            var random: UInt8 = 0
            let status = SecRandomCopyBytes(kSecRandomDefault, 1, &random)
            if status != errSecSuccess {
                fatalError("Unable to generate nonce. SecRandomCopyBytes failed with OSStatus \(status).")
            }

            if random < charset.count {
                result.append(charset[Int(random)])
                remainingLength -= 1
            }
        }

        return result
    }

    static func sha256(_ input: String) -> String {
        let inputData = Data(input.utf8)
        let hashedData = SHA256.hash(data: inputData)
        return hashedData.map { String(format: "%02x", $0) }.joined()
    }
}

struct SupabaseAuthSession: Codable, Equatable {
    let accessToken: String
    let refreshToken: String
    let expiresIn: TimeInterval?
    let expiresAt: TimeInterval?
    let tokenType: String?
    let user: SupabaseAuthUser?

    enum CodingKeys: String, CodingKey {
        case accessToken = "access_token"
        case refreshToken = "refresh_token"
        case expiresIn = "expires_in"
        case expiresAt = "expires_at"
        case tokenType = "token_type"
        case user
    }

    var expiresAtDate: Date? {
        expiresAt.map { Date(timeIntervalSince1970: $0) }
    }

    func isValid(now: Date = Date()) -> Bool {
        guard !accessToken.isEmpty else {
            return false
        }

        guard let expiresAtDate else {
            return true
        }

        return expiresAtDate.timeIntervalSince(now) > 60
    }

    func withComputedExpiry(now: Date = Date()) -> SupabaseAuthSession {
        guard expiresAt == nil, let expiresIn else {
            return self
        }

        return SupabaseAuthSession(
            accessToken: accessToken,
            refreshToken: refreshToken,
            expiresIn: expiresIn,
            expiresAt: now.timeIntervalSince1970 + expiresIn,
            tokenType: tokenType,
            user: user
        )
    }
}

struct SupabaseAuthUser: Codable, Equatable {
    let id: String?
    let email: String?
}

struct SupabaseSessionKeychainStore {
    private let service = "com.vytisstudios.MusicAtlasController.supabaseAuth"
    private let account = "supabase_session_v0_1"

    func load() -> SupabaseAuthSession? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]

        var item: CFTypeRef?
        let status = SecItemCopyMatching(query as CFDictionary, &item)
        guard status == errSecSuccess, let data = item as? Data else {
            return nil
        }

        return try? JSONDecoder().decode(SupabaseAuthSession.self, from: data)
    }

    func save(_ session: SupabaseAuthSession) throws {
        let data = try JSONEncoder().encode(session)
        let baseQuery: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account
        ]
        let attributes: [String: Any] = [
            kSecValueData as String: data,
            kSecAttrAccessible as String: kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly
        ]

        let updateStatus = SecItemUpdate(baseQuery as CFDictionary, attributes as CFDictionary)
        if updateStatus == errSecSuccess {
            return
        }

        guard updateStatus == errSecItemNotFound else {
            throw SupabaseClientError.keychainFailure("update status \(updateStatus)")
        }

        var addQuery = baseQuery
        attributes.forEach { addQuery[$0.key] = $0.value }
        let addStatus = SecItemAdd(addQuery as CFDictionary, nil)
        guard addStatus == errSecSuccess else {
            throw SupabaseClientError.keychainFailure("add status \(addStatus)")
        }
    }

    func clear() {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account
        ]
        SecItemDelete(query as CFDictionary)
    }
}

struct MissionProgress {
    let itemCount: Int
    let resolvedCount: Int
    let playedCount: Int
    let reactionCount: Int
    let selectedIndex: Int?

    var selectedDisplay: String {
        guard let selectedIndex else {
            return "0/\(itemCount)"
        }

        return "\(selectedIndex + 1)/\(itemCount)"
    }

    static let empty = MissionProgress(
        itemCount: 0,
        resolvedCount: 0,
        playedCount: 0,
        reactionCount: 0,
        selectedIndex: nil
    )
}

struct MissionReviewSnapshot {
    let mission: Mission?
    let items: [MissionReviewItemEvidence]
    let canGenerateDevelopmentExport: Bool
    let canGenerateAcceptanceExport: Bool

    var summary: MissionReviewSummary {
        MissionReviewSummary(
            itemCount: items.count,
            resolvedCount: items.filter { $0.resolution.status == .resolved }.count,
            playbackEvidenceCount: items.filter { $0.playback.hasExportablePlaybackEvidence }.count,
            completedCount: items.filter { $0.playback.status == .played }.count,
            skippedCount: items.filter { $0.playback.status == .skipped }.count,
            reactionCount: items.filter { $0.reaction != nil }.count,
            reviewNeededCount: items.filter { $0.needsReview }.count,
            exportableEvidenceCount: items.filter { $0.isExportableEvidenceCandidate }.count,
            canGenerateDevelopmentExport: canGenerateDevelopmentExport,
            canGenerateAcceptanceExport: canGenerateAcceptanceExport
        )
    }

    static let empty = MissionReviewSnapshot(
        mission: nil,
        items: [],
        canGenerateDevelopmentExport: false,
        canGenerateAcceptanceExport: false
    )
}

struct MissionReviewSummary {
    let itemCount: Int
    let resolvedCount: Int
    let playbackEvidenceCount: Int
    let completedCount: Int
    let skippedCount: Int
    let reactionCount: Int
    let reviewNeededCount: Int
    let exportableEvidenceCount: Int
    let canGenerateDevelopmentExport: Bool
    let canGenerateAcceptanceExport: Bool

    var readinessLabel: String {
        if canGenerateAcceptanceExport {
            return "Acceptance export ready"
        }

        if canGenerateDevelopmentExport {
            return "Development export ready"
        }

        if exportableEvidenceCount > 0 {
            return "Evidence captured"
        }

        return "Keep listening"
    }
}

struct PlayerActionLogEntry: Identifiable, Equatable {
    let itemID: String
    let itemTitle: String
    let action: PlayerActionKind
    let occurredAt: Date

    var id: String {
        "\(itemID)-\(action.rawValue)-\(occurredAt.timeIntervalSince1970)"
    }
}

enum PlayerActionKind: String, Equatable {
    case skipBeforeStart = "skip_before_start"
    case skipAfterStart = "skip_after_start"
    case skipUnresolved = "skip_unresolved"
    case completedByThreshold = "completed_by_threshold"
}

struct MissionReviewItemEvidence: Identifiable {
    let item: MissionItem
    let resolution: AppleMusicResolution
    let playback: PlaybackRecord
    let reaction: ReactionRecord?

    var id: String {
        item.itemID
    }

    var flags: [MissionReviewFlag] {
        var flags: [MissionReviewFlag] = []

        if resolution.status != .resolved {
            flags.append(.needsResolution)
        }

        if playback.status == .failed {
            flags.append(.playbackFailed)
        }

        if playback.hasExportablePlaybackEvidence && reaction == nil {
            flags.append(.missingReaction)
        }

        if playback.status == .skipped && reaction?.reactionValue == .unresolved {
            flags.append(.skippedNoSignal)
        }

        return flags
    }

    var needsReview: Bool {
        !flags.isEmpty
    }

    var isExportableEvidenceCandidate: Bool {
        resolution.status == .resolved &&
        playback.hasExportablePlaybackEvidence &&
        reaction != nil
    }

    var playbackLabel: String {
        switch playback.status {
        case .notAttempted:
            return "Not played"
        case .queued:
            return "Queued"
        case .playing:
            return "Playing"
        case .played:
            return "Completed"
        case .skipped:
            return "Skipped"
        case .failed:
            return "Playback failed"
        }
    }

    var reactionLabel: String {
        reaction?.reactionValue.displayName ?? "No reaction"
    }

    var selectedTagLabel: String {
        guard let tags = reaction?.selectedTags, !tags.isEmpty else {
            return "No tags"
        }

        return tags.map(\.label).joined(separator: ", ")
    }

    var noteText: String {
        reaction?.notes.text ?? ""
    }
}

enum MissionReviewFlag: String, Identifiable {
    case needsResolution = "needs_resolution"
    case playbackFailed = "playback_failed"
    case missingReaction = "missing_reaction"
    case skippedNoSignal = "skipped_no_signal"

    var id: String {
        rawValue
    }

    var label: String {
        switch self {
        case .needsResolution:
            return "Needs resolution"
        case .playbackFailed:
            return "Playback issue"
        case .missingReaction:
            return "Missing reaction"
        case .skippedNoSignal:
            return "Skipped/no signal"
        }
    }

    var systemImage: String {
        switch self {
        case .needsResolution:
            return "magnifyingglass"
        case .playbackFailed:
            return "exclamationmark.triangle"
        case .missingReaction:
            return "circle.dashed"
        case .skippedNoSignal:
            return "forward.end"
        }
    }
}

enum MusicServiceMode: String, CaseIterable, Identifiable {
    case developmentStub = "development_stub"
    case liveMusicKit = "live_music_kit"

    var id: String {
        rawValue
    }

    var displayName: String {
        switch self {
        case .developmentStub:
            return "Development Stub"
        case .liveMusicKit:
            return "Live MusicKit"
        }
    }

    var resolveButtonTitle: String {
        switch self {
        case .developmentStub:
            return "Resolve With Stub"
        case .liveMusicKit:
            return "Resolve With MusicKit"
        }
    }

    var playbackButtonTitle: String {
        switch self {
        case .developmentStub:
            return "Simulate Playback"
        case .liveMusicKit:
            return "Play With MusicKit"
        }
    }

    var detail: String {
        switch self {
        case .developmentStub:
            return "Simulator-safe local loop; exports are dev/stub only."
        case .liveMusicKit:
            return "Uses MusicKit catalog search and ApplicationMusicPlayer for iPhone proof."
        }
    }
}
