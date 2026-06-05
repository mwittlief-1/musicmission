import AuthenticationServices
import Foundation
import SwiftUI

enum AppTab: Hashable {
    case atlas
    case survey
    case mission
    case resolve
    case player
    case review
    case evidence
    case account
}

enum AppFeatureFlags {
    static var showAlphaUATFixtureControls: Bool {
        #if DEBUG
        true
        #else
        Bundle.main.object(forInfoDictionaryKey: "CartenzaAlphaUATFixturesEnabled") as? Bool == true
        #endif
    }

    static var showSurveyTab: Bool {
        #if DEBUG
        true
        #else
        false
        #endif
    }

    static var showDiagnosticTabs: Bool {
        #if DEBUG
        true
        #else
        false
        #endif
    }

    static var showExportDebugPanels: Bool {
        #if DEBUG
        true
        #else
        false
        #endif
    }

    static var showEvidenceTab: Bool {
        showExportDebugPanels || showAlphaUATFixtureControls
    }

    static var initialTab: AppTab {
        .mission
    }
}

private enum FirstRunConstants {
    static let currentTermsVersion = "alpha_terms_2026_05_23"
    static let currentStateVersion = "alpha1_resolved_uat_mission_pack_2026_05_30_01"
    static let appStoragePrefix = "waymark.alpha1."
}

private enum AlphaGenerationStatus: String {
    case notStarted = "not_started"
    case waitingForAssignment = "waiting_for_assignment"
    case generationFailed = "generation_failed"
    case coreReady = "core_ready"
}

private enum FirstRunStage {
    case consent
    case access
    case onboarding
    case survey
    case generation

    var diagnosticValue: String {
        switch self {
        case .consent:
            return "consent"
        case .access:
            return "access"
        case .onboarding:
            return "onboarding"
        case .survey:
            return "survey"
        case .generation:
            return "generation"
        }
    }
}

struct RootView: View {
    @EnvironmentObject private var appModel: AppModel
    @AppStorage(FirstRunConstants.appStoragePrefix + "accepted_terms_version") private var acceptedTermsVersion = ""
    @AppStorage(FirstRunConstants.appStoragePrefix + "access_completed") private var accessCompleted = false
    @AppStorage(FirstRunConstants.appStoragePrefix + "onboarding_completed") private var onboardingCompleted = false
    @AppStorage(FirstRunConstants.appStoragePrefix + "survey_completed") private var surveyCompleted = false
    @AppStorage(FirstRunConstants.appStoragePrefix + "generation_status") private var generationStatusRaw = AlphaGenerationStatus.notStarted.rawValue
    @AppStorage(FirstRunConstants.appStoragePrefix + "generation_failure_message") private var generationFailureMessage = ""
    @AppStorage(FirstRunConstants.appStoragePrefix + "state_version") private var alphaStateVersion = ""

    @State private var selectedTab: AppTab = AppFeatureFlags.initialTab
    @State private var generationTask: Task<Void, Never>?
    @State private var generationRetryMessage: String?

    private var generationStatus: AlphaGenerationStatus {
        AlphaGenerationStatus(rawValue: generationStatusRaw) ?? .notStarted
    }

    private var firstRunStage: FirstRunStage? {
        if alphaStateVersion != FirstRunConstants.currentStateVersion {
            return .consent
        }

        if acceptedTermsVersion != FirstRunConstants.currentTermsVersion {
            return .consent
        }

        if !accessCompleted {
            return .access
        }

        if !onboardingCompleted {
            return .onboarding
        }

        if !surveyCompleted {
            return .survey
        }

        if generationStatus != .coreReady {
            return .generation
        }

        return nil
    }

    var body: some View {
        Group {
            if let firstRunStage {
                FirstRunFlowView(
                    stage: firstRunStage,
                    generationFailureMessage: generationFailureMessage,
                    generationRetryMessage: generationRetryMessage,
                    acceptTerms: acceptTerms,
                    completeAccess: completeAccess,
                    completeOnboarding: completeOnboarding,
                    completeSurvey: completeSurvey,
                    retryGeneration: retryGeneration,
                    repairAccountAccess: repairAccountAccessForGeneration,
                    cancelGeneration: cancelGeneration,
                    prepareSupportDiagnostics: prepareFirstRunSupportDiagnostics,
                    uploadSupportDiagnostics: uploadFirstRunSupportDiagnostics,
                    enterCoreApp: enterCoreApp,
                    loadResolvedUATFixtures: loadResolvedUATFixturesForSmoke,
                    resetFirstRun: resetFirstRunForSupport
                )
            } else {
                CoreTabShell(
                    selectedTab: $selectedTab,
                    resetFirstRun: resetFirstRunForSupport
                )
            }
        }
        .preferredColorScheme(.dark)
        .task {
            applyAlphaStateVersionResetIfNeeded()
            appModel.loadAtlasHomeReadout()
            appModel.loadAtlasExplainers()
            appModel.loadMissionLibrary()
            if surveyCompleted,
               generationStatus == .coreReady,
               appModel.reviewedMissionAssignmentCount < AlphaMissionGenerationConfig.minimumUsableMissionCount {
                generationStatusRaw = AlphaGenerationStatus.waitingForAssignment.rawValue
                generationFailureMessage = ""
                generationRetryMessage = "Prior static fixture missions were cleared. Rebuilding from saved Survey evidence."
            }
            await appModel.refreshSupabaseAuthSessionIfPossible()
            resumeAlphaGenerationIfNeeded()
        }
    }

    private func acceptTerms() {
        acceptedTermsVersion = FirstRunConstants.currentTermsVersion
    }

    private func completeAccess() {
        accessCompleted = true
        if onboardingCompleted,
           surveyCompleted,
           generationStatus != .coreReady {
            retryGeneration()
        }
    }

    private func completeOnboarding() {
        onboardingCompleted = true
    }

    private func completeSurvey() {
        surveyCompleted = true
        generationStatusRaw = AlphaGenerationStatus.waitingForAssignment.rawValue
        generationFailureMessage = ""
        retryGeneration()
    }

    private func retryGeneration() {
        generationTask?.cancel()
        generationRetryMessage = "Building from saved Survey evidence."
        generationTask = Task { @MainActor in
            generationStatusRaw = AlphaGenerationStatus.waitingForAssignment.rawValue
            let didGenerate = await appModel.generateFirstMissionBatchAfterSurveyCompletion()
            generationTask = nil
            if didGenerate,
               appModel.reviewedMissionAssignmentCount >= AlphaMissionGenerationConfig.minimumUsableMissionCount {
                generationStatusRaw = AlphaGenerationStatus.coreReady.rawValue
                generationFailureMessage = ""
                generationRetryMessage = nil
                selectedTab = .mission
            } else if !didGenerate {
                generationStatusRaw = AlphaGenerationStatus.generationFailed.rawValue
                generationFailureMessage = appModel.lastActionMessage ?? "Mission generation failed before the first Alpha batch was complete."
                generationRetryMessage = nil
            }
        }
    }

    private func repairAccountAccessForGeneration() {
        generationTask?.cancel()
        generationTask = nil
        generationRetryMessage = nil
        generationFailureMessage = "Reconnect Apple ID, then Cartenza will retry from saved Survey evidence."
        generationStatusRaw = AlphaGenerationStatus.generationFailed.rawValue
        accessCompleted = false
    }

    private func cancelGeneration() {
        generationTask?.cancel()
        generationTask = nil
        generationRetryMessage = nil
        generationStatusRaw = AlphaGenerationStatus.generationFailed.rawValue
        appModel.markMissionGenerationCancelledForSupport()
        generationFailureMessage = appModel.lastActionMessage ?? "Mission generation cancelled."
        prepareFirstRunSupportDiagnostics()
    }

    private func enterCoreApp() {
        generationStatusRaw = AlphaGenerationStatus.coreReady.rawValue
        selectedTab = appModel.hasReviewedMissionAssignments ? .mission : .account
    }

    private func loadResolvedUATFixturesForSmoke() {
        generationTask?.cancel()
        generationTask = nil
        appModel.importLocalAlphaAppImportReadyUATFixtures()
        guard appModel.reviewedMissionAssignmentCount >= AlphaMissionGenerationConfig.minimumUsableMissionCount else {
            generationStatusRaw = AlphaGenerationStatus.generationFailed.rawValue
            generationFailureMessage = appModel.lastActionMessage ?? "Resolved UAT fixture import did not produce the expected Alpha mission batch."
            return
        }

        generationStatusRaw = AlphaGenerationStatus.coreReady.rawValue
        generationFailureMessage = ""
        generationRetryMessage = nil
        selectedTab = .mission
    }

    private func resetFirstRunForSupport() {
        generationTask?.cancel()
        generationTask = nil
        purgeLegacyFirstRunUserDefaults()
        acceptedTermsVersion = ""
        accessCompleted = false
        onboardingCompleted = false
        surveyCompleted = false
        generationStatusRaw = AlphaGenerationStatus.notStarted.rawValue
        generationFailureMessage = ""
        generationRetryMessage = nil
        alphaStateVersion = FirstRunConstants.currentStateVersion
        selectedTab = AppFeatureFlags.initialTab
        appModel.resetAllLocalAlphaState(signOut: true)
    }

    private func prepareFirstRunSupportDiagnostics() {
        appModel.saveFirstRunSupportDiagnosticPackage(rootStateSnapshot: rootDiagnosticSnapshot())
    }

    private func uploadFirstRunSupportDiagnostics() {
        prepareFirstRunSupportDiagnostics()
        Task {
            await appModel.uploadSupportDiagnosticsManually(termsVersion: FirstRunConstants.currentTermsVersion)
        }
    }

    private func resumeAlphaGenerationIfNeeded() {
        guard acceptedTermsVersion == FirstRunConstants.currentTermsVersion,
              alphaStateVersion == FirstRunConstants.currentStateVersion,
              onboardingCompleted,
              surveyCompleted,
              generationStatus == .waitingForAssignment,
              appModel.reviewedMissionAssignmentCount < AlphaMissionGenerationConfig.minimumUsableMissionCount,
              !appModel.firstMissionGenerationState.isLoading else {
            return
        }

        generationStatusRaw = AlphaGenerationStatus.waitingForAssignment.rawValue
        retryGeneration()
    }

    private func rootDiagnosticSnapshot() -> [String: Any] {
        [
            "schema_version": "waymark.alpha_root_state.v0.1",
            "computed_root_stage": firstRunStage?.diagnosticValue ?? "core",
            "current_terms_version": FirstRunConstants.currentTermsVersion,
            "current_state_version": FirstRunConstants.currentStateVersion,
            "app_storage_prefix": FirstRunConstants.appStoragePrefix,
            "accepted_terms_version": acceptedTermsVersion,
            "access_completed": accessCompleted,
            "onboarding_completed": onboardingCompleted,
            "survey_completed": surveyCompleted,
            "generation_status": generationStatusRaw,
            "generation_failure_message": generationFailureMessage,
            "generation_retry_message": generationRetryMessage ?? "",
            "alpha_state_version": alphaStateVersion,
            "supabase_authenticated": appModel.isSupabaseAuthenticated,
            "music_authorization_status": appModel.musicAuthorizationSnapshot.status,
            "reviewed_mission_count": appModel.reviewedMissionAssignmentCount,
            "required_mission_count": AlphaMissionGenerationConfig.requiredMissionCount,
            "generation_task_active": generationTask != nil
        ]
    }

    private func applyAlphaStateVersionResetIfNeeded() {
        guard alphaStateVersion != FirstRunConstants.currentStateVersion else {
            return
        }

        purgeLegacyFirstRunUserDefaults()
        acceptedTermsVersion = ""
        accessCompleted = false
        onboardingCompleted = false
        surveyCompleted = false
        generationStatusRaw = AlphaGenerationStatus.notStarted.rawValue
        generationFailureMessage = ""
        generationRetryMessage = nil
        selectedTab = AppFeatureFlags.initialTab
        appModel.resetAllLocalAlphaState(signOut: true)
        alphaStateVersion = FirstRunConstants.currentStateVersion
    }

    private func purgeLegacyFirstRunUserDefaults() {
        let defaults = UserDefaults.standard
        for key in defaults.dictionaryRepresentation().keys where key.hasPrefix(FirstRunConstants.appStoragePrefix) {
            defaults.removeObject(forKey: key)
        }
    }
}

private struct FirstRunFlowView: View {
    @EnvironmentObject private var appModel: AppModel

    let stage: FirstRunStage
    let generationFailureMessage: String
    let generationRetryMessage: String?
    let acceptTerms: () -> Void
    let completeAccess: () -> Void
    let completeOnboarding: () -> Void
    let completeSurvey: () -> Void
    let retryGeneration: () -> Void
    let repairAccountAccess: () -> Void
    let cancelGeneration: () -> Void
    let prepareSupportDiagnostics: () -> Void
    let uploadSupportDiagnostics: () -> Void
    let enterCoreApp: () -> Void
    let loadResolvedUATFixtures: () -> Void
    let resetFirstRun: () -> Void

    var body: some View {
        ZStack {
            WaymarkSurface.background.ignoresSafeArea()

            switch stage {
            case .consent:
                ConsentGateView(acceptTerms: acceptTerms)
            case .access:
                AccountAccessView(completeAccess: completeAccess)
            case .onboarding:
                OnboardingWalkthroughView(completeOnboarding: completeOnboarding)
            case .survey:
                SurveyView(isFirstRunIntake: true, onComplete: completeSurvey)
            case .generation:
                GenerationStatusView(
                    hasMissionBatch: appModel.hasReviewedMissionAssignments,
                    missionCount: appModel.reviewedMissionAssignmentCount,
                    targetMissionCount: AlphaMissionGenerationConfig.requiredMissionCount,
                    generationState: appModel.firstMissionGenerationState,
                    generationProgress: appModel.firstMissionGenerationProgress,
                    retryMessage: generationRetryMessage,
                    lastActionMessage: appModel.lastActionMessage ?? (generationFailureMessage.isEmpty ? nil : generationFailureMessage),
                    retryGeneration: retryGeneration,
                    repairAccountAccess: repairAccountAccess,
                    cancelGeneration: cancelGeneration,
                    prepareSupportDiagnostics: prepareSupportDiagnostics,
                    uploadSupportDiagnostics: uploadSupportDiagnostics,
                    enterCoreApp: enterCoreApp,
                    loadResolvedUATFixtures: loadResolvedUATFixtures,
                    resetFirstRun: resetFirstRun
                )
            }
        }
    }
}

private struct CoreTabShell: View {
    @EnvironmentObject private var appModel: AppModel

    @Binding var selectedTab: AppTab
    let resetFirstRun: () -> Void

    var body: some View {
        TabView(selection: $selectedTab) {
            AtlasExplainerHomeView(
                store: appModel.atlasExplainerStore,
                readoutStore: appModel.atlasHomeReadoutStore
            )
                .tabItem {
                    Label("Atlas", systemImage: "map")
                }
                .tag(AppTab.atlas)

            if AppFeatureFlags.showSurveyTab {
                SurveyView()
                    .tabItem {
                        Label("Survey", systemImage: "square.grid.3x3")
                    }
                    .tag(AppTab.survey)
            }

            MissionListView()
                .tabItem {
                    Label("Mission", systemImage: "music.note.list")
                }
                .tag(AppTab.mission)

            if AppFeatureFlags.showDiagnosticTabs {
                ResolverStatusView()
                    .tabItem {
                        Label("Resolve", systemImage: "magnifyingglass")
                    }
                    .tag(AppTab.resolve)
            }

            NowTestingView(
                openMissionReview: {
                    selectedTab = .review
                },
                openResolveIssue: {
                    selectedTab = AppFeatureFlags.showDiagnosticTabs ? .resolve : .review
                }
            )
                .tabItem {
                    Label("Player", systemImage: "play.circle")
                }
                .tag(AppTab.player)

            MissionReviewView()
                .tabItem {
                    Label("Review", systemImage: "list.clipboard")
                }
                .tag(AppTab.review)

            if AppFeatureFlags.showEvidenceTab {
                ExportPreviewView()
                    .tabItem {
                        Label("Evidence", systemImage: "square.and.arrow.up")
                    }
                    .tag(AppTab.evidence)
            }

            AccountView(resetFirstRun: resetFirstRun)
                .tabItem {
                    Label("Account", systemImage: "person.crop.circle")
                }
                .tag(AppTab.account)
        }
    }
}

private struct ConsentGateView: View {
    let acceptTerms: () -> Void

    var body: some View {
        WaymarkFirstRunScroll {
            WaymarkStepHeader(step: "Alpha Access")
            CartenzaBrandLockup()

            Text("A private Alpha needs clear ground rules.")
                .font(.largeTitle.weight(.bold))
                .foregroundStyle(WaymarkTheme.text)
                .fixedSize(horizontal: false, vertical: true)

            Text("Before Survey or evidence capture, accept the Alpha privacy and terms acknowledgement.")
                .font(.body)
                .foregroundStyle(WaymarkTheme.mutedText)
                .fixedSize(horizontal: false, vertical: true)

            VStack(alignment: .leading, spacing: 10) {
                WaymarkDisclosureRow(title: "Evidence is provisional", detail: "Survey, playback, notes, chips, and skips create Alpha evidence. They do not directly change Atlas truth.")
                WaymarkDisclosureRow(title: "Music access is explicit", detail: "Apple Music permission is requested before playback or MusicKit-derived signals.")
                WaymarkDisclosureRow(title: "Sharing is controlled", detail: "Share Evidence prepares a support backup only when you choose it. Cartenza will say clearly if an Alpha build adds account sync later.")
            }
            .padding(.top, 8)

            Text("This private Alpha stores Survey, mission, playback, notes, and support diagnostics on this device for testing. Sharing evidence is optional and deliberate, and every Atlas signal remains provisional while Cartenza learns from your feedback.")
                .font(.caption)
                .foregroundStyle(WaymarkTheme.waypoint)
                .fixedSize(horizontal: false, vertical: true)
                .padding(12)
                .background(WaymarkTheme.panel, in: RoundedRectangle(cornerRadius: WaymarkTheme.smallRadius))

            Button(action: acceptTerms) {
                Label("Accept Alpha Terms", systemImage: "checkmark.shield")
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
            .controlSize(.large)
        }
    }
}

private struct AccountAccessView: View {
    @EnvironmentObject private var appModel: AppModel
    let completeAccess: () -> Void

    private var musicIsAuthorized: Bool {
        appModel.isAppleMusicAuthorized
    }

    private var hasMinimumAlphaAccess: Bool {
        true
    }

    private var accessSummary: String {
        switch (appModel.isSupabaseAuthenticated, musicIsAuthorized) {
        case (true, true):
            return "Apple ID and Apple Music are connected."
        case (true, false):
            return "Apple ID is connected. Apple Music can be repaired from My Account before playback."
        case (false, true):
            return "Apple Music is connected. Cartenza can continue locally while account sign-in is repaired."
        case (false, false):
            return "This internal Alpha build can continue locally. Repair Apple ID or Apple Music from My Account before playback or evidence upload."
        }
    }

    var body: some View {
        WaymarkFirstRunScroll {
            WaymarkStepHeader(step: "Connect")
            WaymarkHeroIcon(systemImage: "person.badge.key.fill", tint: WaymarkTheme.route)

            Text("Connect once. Stay signed in when we can.")
                .font(.largeTitle.weight(.bold))
                .foregroundStyle(WaymarkTheme.text)
                .fixedSize(horizontal: false, vertical: true)

            Text("This is one guided access step. Apple ID sign-in and Apple Music authorization are separate Apple capabilities, but Cartenza keeps them together here.")
                .font(.body)
                .foregroundStyle(WaymarkTheme.mutedText)
                .fixedSize(horizontal: false, vertical: true)

            SignInWithAppleButton(
                .signIn,
                onRequest: { request in
                    _ = appModel.configureAppleSignInRequest(request)
                },
                onCompletion: { result in
                    Task {
                        await appModel.completeSupabaseAppleSignIn(
                            result: result,
                            rawNonce: nil
                        )
                    }
                }
            )
            .signInWithAppleButtonStyle(.white)
            .frame(height: 48)
            .clipShape(RoundedRectangle(cornerRadius: 9))
            .disabled(appModel.supabaseAuthSnapshot.status == .signingIn)

            Text(appModel.supabaseAuthStatusDetail)
                .font(.caption)
                .foregroundStyle(appModel.isSupabaseAuthenticated ? WaymarkTheme.positive : WaymarkTheme.mutedText)
                .fixedSize(horizontal: false, vertical: true)

            if let message = appModel.lastActionMessage {
                Text(message)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(appModel.isSupabaseAuthenticated || musicIsAuthorized ? WaymarkTheme.positive : WaymarkTheme.waypoint)
                    .fixedSize(horizontal: false, vertical: true)
            }

            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    VStack(alignment: .leading, spacing: 3) {
                        Text("Cartenza Account")
                            .font(.headline)
                            .foregroundStyle(WaymarkTheme.text)
                        Text(appModel.supabaseAuthStatusDetail)
                            .font(.caption)
                            .foregroundStyle(WaymarkTheme.mutedText)
                    }

                    Spacer()

                    Image(systemName: appModel.isSupabaseAuthenticated ? "checkmark.circle.fill" : "circle")
                        .foregroundStyle(appModel.isSupabaseAuthenticated ? WaymarkTheme.positive : WaymarkTheme.mutedText)
                        .imageScale(.large)
                }

                HStack {
                    VStack(alignment: .leading, spacing: 3) {
                        Text("Apple Music")
                            .font(.headline)
                            .foregroundStyle(WaymarkTheme.text)
                        Text(appModel.musicAuthorizationSnapshot.detail)
                            .font(.caption)
                            .foregroundStyle(WaymarkTheme.mutedText)
                    }

                    Spacer()

                    Image(systemName: musicIsAuthorized ? "checkmark.circle.fill" : "circle")
                        .foregroundStyle(musicIsAuthorized ? WaymarkTheme.positive : WaymarkTheme.mutedText)
                        .imageScale(.large)
                }

                Button {
                    Task {
                        await appModel.musicAuthorization.requestAuthorization()
                    }
                } label: {
                    Label(musicIsAuthorized ? "Apple Music Connected" : "Connect Apple Music", systemImage: "music.note")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
                .disabled(musicIsAuthorized || !appModel.musicAuthorizationSnapshot.canRequestAuthorization)
            }
            .padding(14)
            .background(WaymarkTheme.panel, in: RoundedRectangle(cornerRadius: WaymarkTheme.radius))
            .overlay(
                RoundedRectangle(cornerRadius: WaymarkTheme.radius)
                    .stroke(WaymarkTheme.line, lineWidth: 1)
            )

            if !musicIsAuthorized {
                Text("If Apple Music does not prompt, check iPhone Settings > Privacy & Security > Media & Apple Music. This build can continue locally after Apple ID sign-in while account services are repaired.")
                    .font(.caption)
                    .foregroundStyle(WaymarkTheme.waypoint)
                    .fixedSize(horizontal: false, vertical: true)
            }

            VStack(alignment: .leading, spacing: 10) {
                Text(accessSummary)
                    .font(.callout.weight(.semibold))
                    .foregroundStyle(WaymarkTheme.text)
                    .fixedSize(horizontal: false, vertical: true)

                Button(action: completeAccess) {
                    Label("Continue", systemImage: "arrow.right")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
                .controlSize(.large)
                .disabled(!hasMinimumAlphaAccess)
            }
            .padding(14)
            .background(WaymarkTheme.raisedPanel, in: RoundedRectangle(cornerRadius: WaymarkTheme.radius))
            .overlay(
                RoundedRectangle(cornerRadius: WaymarkTheme.radius)
                    .stroke(WaymarkTheme.line, lineWidth: 1)
            )
        }
    }
}

private struct OnboardingWalkthroughView: View {
    let completeOnboarding: () -> Void

    var body: some View {
        TabView {
            ForEach(Array(Self.pages.enumerated()), id: \.offset) { index, page in
                OnboardingPageView(
                    pageNumber: index + 1,
                    pageCount: Self.pages.count,
                    systemImage: page.systemImage,
                    kicker: page.kicker,
                    title: page.title,
                    bodyText: page.bodyText,
                    helperText: page.helperText,
                    actionTitle: index == Self.pages.count - 1 ? "Start Survey" : nil,
                    action: index == Self.pages.count - 1 ? completeOnboarding : nil
                )
            }
        }
        .tabViewStyle(.page)
        .indexViewStyle(.page(backgroundDisplayMode: .always))
    }

    private static let pages: [OnboardingPage] = [
        OnboardingPage(
            systemImage: "map.fill",
            kicker: "Welcome",
            title: CartenzaBrand.tagline,
            bodyText: "Connect Apple Music and answer a short Survey. Cartenza will build your starter Atlas and generate your first listening missions.",
            helperText: "You are testing the loop, not a finished recommendation engine."
        ),
        OnboardingPage(
            systemImage: "list.number",
            kicker: "What You'll Do",
            title: "The Alpha has four simple steps.",
            bodyText: "Connect Apple Music. Complete the Survey. Try assigned missions. React to songs with quick signals, optional tags, and optional notes.",
            helperText: "You do not need to understand the model, graph, or data format."
        ),
        OnboardingPage(
            systemImage: "square.grid.3x3.fill",
            kicker: "Survey",
            title: "The Survey maps starting territory.",
            bodyText: "You will mark artists, albums, and songs you know, like, love, want to keep around, or do not want. Don't Know, Ok, and Miss are useful signals too.",
            helperText: "Speed matters. Pick the real reaction, not the impressive one."
        ),
        OnboardingPage(
            systemImage: "music.note.list",
            kicker: "Missions",
            title: "Missions are not playlists.",
            bodyText: "A mission is a listening experiment. It may test a nearby road, a possible frontier, a dead end, or a landmark. Some songs are supposed to be risky.",
            helperText: "A good miss can be as useful as a hit."
        ),
        OnboardingPage(
            systemImage: "slider.horizontal.3",
            kicker: "Listen and React",
            title: "React lightly. Add detail when it matters.",
            bodyText: "Use Love, Like, Ok, or Dislike as the primary signal. Tap context chips when they explain the reaction. Add a note only if the chip set is not enough.",
            helperText: "Skipping means unclear/no-signal unless you explicitly react."
        ),
        OnboardingPage(
            systemImage: "point.3.connected.trianglepath.dotted",
            kicker: "Your Atlas",
            title: "Cartenza learns from evidence.",
            bodyText: "The app will start building a working map from your Survey and missions. That map stays cautious: landmarks, frontiers, useful waypoints, and dead-end risks.",
            helperText: "The goal is better next missions, not instant truth."
        )
    ]
}

private struct OnboardingPage {
    let systemImage: String
    let kicker: String
    let title: String
    let bodyText: String
    let helperText: String
}

private struct OnboardingPageView: View {
    let pageNumber: Int
    let pageCount: Int
    let systemImage: String
    let kicker: String
    let title: String
    let bodyText: String
    let helperText: String
    var actionTitle: String?
    var action: (() -> Void)?

    var body: some View {
        VStack(alignment: .leading, spacing: 18) {
            Spacer()
            WaymarkStepHeader(step: "\(pageNumber)/\(pageCount)")
            WaymarkHeroIcon(systemImage: systemImage, tint: pageNumber == pageCount ? WaymarkTheme.signal : WaymarkTheme.route)

            Text(kicker)
                .font(.caption.weight(.bold))
                .foregroundStyle(WaymarkTheme.route)
                .textCase(.uppercase)

            Text(title)
                .font(.largeTitle.weight(.bold))
                .foregroundStyle(WaymarkTheme.text)
                .fixedSize(horizontal: false, vertical: true)

            Text(bodyText)
                .font(.body)
                .foregroundStyle(WaymarkTheme.mutedText)
                .fixedSize(horizontal: false, vertical: true)

            Text(helperText)
                .font(.callout.weight(.semibold))
                .foregroundStyle(WaymarkTheme.text)
                .fixedSize(horizontal: false, vertical: true)
                .padding(14)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(WaymarkTheme.panel, in: RoundedRectangle(cornerRadius: WaymarkTheme.radius))
                .overlay(
                    RoundedRectangle(cornerRadius: WaymarkTheme.radius)
                        .stroke(WaymarkTheme.line, lineWidth: 1)
                )

            Spacer()

            if let actionTitle, let action {
                Button(action: action) {
                    Label(actionTitle, systemImage: "arrow.right")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
                .controlSize(.large)
            }
        }
        .padding(24)
    }
}

private struct CartenzaTopographicBackdrop: View {
    var body: some View {
        ZStack {
            WaymarkTheme.background

            Canvas { context, size in
                var path = Path()
                let spacing: CGFloat = 42
                let amplitude: CGFloat = 18

                for offset in stride(from: -size.height, through: size.width + size.height, by: spacing) {
                    path.move(to: CGPoint(x: offset, y: 0))
                    path.addCurve(
                        to: CGPoint(x: offset - size.height * 0.30, y: size.height),
                        control1: CGPoint(x: offset + amplitude, y: size.height * 0.30),
                        control2: CGPoint(x: offset - amplitude * 2, y: size.height * 0.66)
                    )
                }

                context.stroke(path, with: .color(WaymarkTheme.line.opacity(0.30)), lineWidth: 1)
            }
            .opacity(0.55)
        }
    }
}

private struct GenerationStatusView: View {
    @EnvironmentObject private var appModel: AppModel
    @State private var diagnosticsTapCount = 0
    @State private var diagnosticsTapMessage: String?

    let hasMissionBatch: Bool
    let missionCount: Int
    let targetMissionCount: Int
    let generationState: AppModel.LoadState
    let generationProgress: MissionGenerationProgress
    let retryMessage: String?
    let lastActionMessage: String?
    let retryGeneration: () -> Void
    let repairAccountAccess: () -> Void
    let cancelGeneration: () -> Void
    let prepareSupportDiagnostics: () -> Void
    let uploadSupportDiagnostics: () -> Void
    let enterCoreApp: () -> Void
    let loadResolvedUATFixtures: () -> Void
    let resetFirstRun: () -> Void

    private var hasCompleteMissionBatch: Bool {
        missionCount >= targetMissionCount
    }

    private var installedBuildLabel: String {
        let version = Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "unknown"
        let build = Bundle.main.infoDictionary?["CFBundleVersion"] as? String ?? "unknown"
        return "\(version) (\(build))"
    }

    var body: some View {
        WaymarkFirstRunScroll {
            WaymarkStepHeader(step: "Generation")
            WaymarkHeroIcon(systemImage: "sparkles", tint: WaymarkTheme.signal)

            Text("Building survey-derived missions.")
                .font(.largeTitle.weight(.bold))
                .foregroundStyle(WaymarkTheme.text)
                .fixedSize(horizontal: false, vertical: true)

            Text(AppFeatureFlags.showAlphaUATFixtureControls ? "Cartenza will use saved Survey evidence first. The resolved UAT fixture pack is available only as an explicit support action." : "Cartenza selects a deterministic first mission batch from visible Survey evidence and resolved canonical Apple Music references.")
                .font(.body)
                .foregroundStyle(WaymarkTheme.mutedText)
                .fixedSize(horizontal: false, vertical: true)

            generationStatusCard

            VStack(alignment: .leading, spacing: 12) {
                WaymarkDisclosureRow(title: "Survey evidence captured", detail: "Artist, album, and song responses are stored locally.")
                WaymarkDisclosureRow(
                    title: "Mission source",
                    detail: AppFeatureFlags.showAlphaUATFixtureControls
                        ? "Default path is Survey-derived local opportunity selection. Load UAT fixtures only for playback smoke support."
                        : "Survey-derived local opportunity selection uses visible responses, canonical graph refs, and cached Apple Music IDs."
                )
                WaymarkDisclosureRow(
                    title: hasCompleteMissionBatch ? "Mission batch available" : "Mission assignment in progress",
                    detail: hasCompleteMissionBatch ? "The first Alpha batch has \(targetMissionCount) app-ready missions." : "\(missionCount)/\(targetMissionCount) Alpha missions are ready so far."
                )
            }

            if !hasCompleteMissionBatch || generationState.isFailed {
                Button(action: retryGeneration) {
                    Label("Retry Mission Selection", systemImage: "arrow.clockwise")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.bordered)
                .controlSize(.large)
                .disabled(generationState.isLoading)
            }

            if AppFeatureFlags.showAlphaUATFixtureControls {
                Button(action: loadResolvedUATFixtures) {
                    Label("Load Resolved UAT Fixtures", systemImage: "play.rectangle.on.rectangle")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.bordered)
                .controlSize(.large)
                .disabled(generationState.isLoading)
            }

            if generationState.isLoading {
                Button(action: cancelGeneration) {
                    Label("Stop Waiting", systemImage: "pause.circle")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.bordered)
                .controlSize(.large)
            }

            VStack(alignment: .leading, spacing: 10) {
                Text("Support Diagnostics")
                    .font(.headline)
                    .foregroundStyle(WaymarkTheme.text)
                Text("Package the current root state, Survey handoff, mission source state, and import diagnostics before retrying or starting fresh.")
                    .font(.caption)
                    .foregroundStyle(WaymarkTheme.mutedText)
                    .fixedSize(horizontal: false, vertical: true)
                Text("Installed build: \(installedBuildLabel)")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(WaymarkTheme.signal)

                Button(action: prepareSupportDiagnostics) {
                    Label("Prepare Support Diagnostics", systemImage: "wrench.and.screwdriver")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.bordered)

                if let package = appModel.savedSupportDiagnosticsPackage {
                    ShareLink(items: package.shareURLs) {
                        Label("Share Support Diagnostics", systemImage: "square.and.arrow.up")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.bordered)
                }

                Button {
                    diagnosticsTapCount += 1
                    diagnosticsTapMessage = "Upload tap received for build \(installedBuildLabel). Preparing diagnostics..."
                    uploadSupportDiagnostics()
                } label: {
                    Label(appModel.isDiagnosticUploadInFlight ? "Uploading Diagnostics" : "Upload Diagnostics to Cartenza", systemImage: "icloud.and.arrow.up")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.bordered)
                .controlSize(.large)
                .disabled(appModel.isDiagnosticUploadInFlight)

                if let diagnosticsTapMessage {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Button status")
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(WaymarkTheme.text)
                        Text("\(diagnosticsTapMessage) Tap count: \(diagnosticsTapCount).")
                            .font(.caption)
                            .foregroundStyle(WaymarkTheme.mutedText)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(10)
                    .background(WaymarkTheme.raisedPanel.opacity(0.55), in: RoundedRectangle(cornerRadius: 8))
                    .overlay(
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(WaymarkTheme.line, lineWidth: 1)
                    )
                }

                if let lastActionMessage {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("App status")
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(WaymarkTheme.text)
                        Text(lastActionMessage)
                            .font(.caption)
                            .foregroundStyle(WaymarkTheme.mutedText)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(10)
                    .background(WaymarkTheme.raisedPanel.opacity(0.55), in: RoundedRectangle(cornerRadius: 8))
                    .overlay(
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(WaymarkTheme.line, lineWidth: 1)
                    )
                }
            }
            .padding(14)
            .background(WaymarkTheme.panel, in: RoundedRectangle(cornerRadius: WaymarkTheme.radius))
            .overlay(
                RoundedRectangle(cornerRadius: WaymarkTheme.radius)
                    .stroke(WaymarkTheme.line, lineWidth: 1)
            )

            Button(action: enterCoreApp) {
                Label(hasCompleteMissionBatch ? "Open First Missions" : "Waiting for \(targetMissionCount) Missions", systemImage: "arrow.right")
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
            .controlSize(.large)
            .disabled(generationState.isLoading || !hasCompleteMissionBatch)

            Button(role: .destructive, action: resetFirstRun) {
                Label("Start Fresh", systemImage: "arrow.counterclockwise")
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.bordered)
            .controlSize(.large)
        }
    }

    private var generationStatusCard: some View {
        let presentation = generationPresentation

        return VStack(alignment: .leading, spacing: 12) {
            HStack(alignment: .top, spacing: 12) {
                if generationState.isLoading {
                    ProgressView()
                        .tint(presentation.tint)
                        .frame(width: 24)
                } else {
                    Image(systemName: presentation.icon)
                        .foregroundStyle(presentation.tint)
                        .frame(width: 24)
                }

                VStack(alignment: .leading, spacing: 4) {
                    Text(presentation.title)
                        .font(.headline)
                        .foregroundStyle(WaymarkTheme.text)
                    Text(retryMessage ?? lastActionMessage ?? presentation.detail)
                        .font(.callout)
                        .foregroundStyle(WaymarkTheme.mutedText)
                        .fixedSize(horizontal: false, vertical: true)
                }
            }

            if generationState.isLoading {
                ProgressView(value: generationProgress.fractionCompleted)
                    .tint(WaymarkTheme.signal)
                Text(generationProgress.detail)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(WaymarkTheme.text)
            }
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(WaymarkTheme.panel, in: RoundedRectangle(cornerRadius: WaymarkTheme.radius))
        .overlay(
            RoundedRectangle(cornerRadius: WaymarkTheme.radius)
                .stroke(WaymarkTheme.line, lineWidth: 1)
        )
    }

    private var generationPresentation: (title: String, detail: String, icon: String, tint: Color) {
        switch generationState {
        case .idle:
            return (
                "Ready to build",
                "Cartenza will select a local first mission batch from saved Survey evidence.",
                "sparkles",
                WaymarkTheme.signal
            )
        case .loading:
            return (
                "Selecting",
                "Building resolved survey-derived missions from visible evidence and canonical Apple Music refs.",
                "clock",
                WaymarkTheme.route
            )
        case .loaded:
            return (
                "Ready",
                hasCompleteMissionBatch ? "App-ready mission assignments imported through the app gate." : "Mission import completed with a partial batch.",
                "checkmark.circle.fill",
                hasCompleteMissionBatch ? WaymarkTheme.positive : WaymarkTheme.waypoint
            )
        case .failed(let message):
            return (
                "Generation needs attention",
                message,
                "exclamationmark.triangle.fill",
                WaymarkTheme.waypoint
            )
        }
    }
}

private struct AccountView: View {
    @EnvironmentObject private var appModel: AppModel
    let resetFirstRun: () -> Void

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    WaymarkStepHeader(step: "My Account")

                    Text("Account, access, and support tools.")
                        .font(.largeTitle.weight(.bold))
                        .foregroundStyle(WaymarkTheme.text)
                        .fixedSize(horizontal: false, vertical: true)

                    VStack(alignment: .leading, spacing: 12) {
                        AccountStatusRow(
                            title: "Cartenza Account",
                            detail: appModel.supabaseAuthStatusDetail,
                            systemImage: "person.badge.key",
                            tint: appModel.isSupabaseAuthenticated ? WaymarkTheme.positive : WaymarkTheme.waypoint
                        )
                        AccountStatusRow(
                            title: "Apple Music",
                            detail: appModel.isAppleMusicAuthorized ? "Connected" : "Needs attention",
                            systemImage: "music.note",
                            tint: appModel.isAppleMusicAuthorized ? WaymarkTheme.positive : WaymarkTheme.waypoint
                        )
                    }
                    .padding(14)
                    .background(WaymarkTheme.panel, in: RoundedRectangle(cornerRadius: WaymarkTheme.radius))
                    .overlay(
                        RoundedRectangle(cornerRadius: WaymarkTheme.radius)
                            .stroke(WaymarkTheme.line, lineWidth: 1)
                    )

                    VStack(alignment: .leading, spacing: 10) {
                        Text("FAQ")
                            .font(.title3.weight(.bold))
                            .foregroundStyle(WaymarkTheme.text)
                        ForEach(Self.faqItems, id: \.question) { item in
                            FAQRow(question: item.question, answer: item.answer)
                        }
                    }

                    VStack(alignment: .leading, spacing: 10) {
                        Text("Support")
                            .font(.title3.weight(.bold))
                            .foregroundStyle(WaymarkTheme.text)

                        NavigationLink {
                            ExportPreviewView()
                        } label: {
                            Label("Share Evidence Backup", systemImage: "square.and.arrow.up")
                                .frame(maxWidth: .infinity, alignment: .leading)
                        }
                        .buttonStyle(.borderedProminent)

                        NavigationLink {
                            SurveyView()
                        } label: {
                            Label("Revisit Survey", systemImage: "square.grid.3x3")
                                .frame(maxWidth: .infinity, alignment: .leading)
                        }
                        .buttonStyle(.bordered)

                        MissionRegenerationPanel()

                        Button(role: .destructive, action: resetFirstRun) {
                            Label("Restart First-Run Flow", systemImage: "arrow.counterclockwise")
                                .frame(maxWidth: .infinity, alignment: .leading)
                        }
                        .buttonStyle(.bordered)
                    }
                }
                .padding(18)
                .frame(maxWidth: .infinity, alignment: .leading)
            }
            .background(WaymarkTheme.background.ignoresSafeArea())
            .navigationTitle("My Account")
        }
    }

    private static let faqItems: [(question: String, answer: String)] = [
        ("What is Cartenza learning?", "Cartenza is collecting provisional evidence about where your music taste has energy, limits, exceptions, and useful dead ends."),
        ("Does a skip mean dislike?", "No. A skip records no-signal playback evidence unless you add an explicit reaction."),
        ("What does Love mean?", "Love means strong positive signal. Cartenza should treat the song as important evidence."),
        ("What does Like mean?", "Like means positive but qualified signal. The details and chips matter."),
        ("What does Ok mean?", "Ok means useful, tolerable, or a possible waypoint. It is not the same as Love."),
        ("What does Dislike mean?", "Dislike means Cartenza should learn what failed here."),
        ("Why are some missions risky?", "Missions are tests, not comfort playlists. A clear miss can improve the map."),
        ("What gets shared?", "Share Evidence prepares a support backup when you choose it. It can include Alpha evidence such as Survey responses, mission reactions, notes, and diagnostics; it remains provisional."),
        ("Can I edit reactions?", "Yes. Use Mission Review to adjust reactions, tags, and notes after listening."),
        ("Does Cartenza write Atlas truth directly?", "No. Your reactions guide the next tests; Cartenza does not treat a single response as permanent Atlas truth."),
        ("Can I restart the Alpha flow?", "Yes. Use the support reset if your local state gets stuck."),
        ("Why is this still an Alpha?", "This build is testing the evidence loop: Survey, first missions, playback, reactions, and support diagnostics. The map should get clearer through feedback, not pretend to be final on day one.")
    ]
}

private struct FAQRow: View {
    let question: String
    let answer: String

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(question)
                .font(.headline)
                .foregroundStyle(WaymarkTheme.text)
            Text(answer)
                .font(.callout)
                .foregroundStyle(WaymarkTheme.mutedText)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(WaymarkTheme.panel, in: RoundedRectangle(cornerRadius: WaymarkTheme.smallRadius))
        .overlay(
            RoundedRectangle(cornerRadius: WaymarkTheme.smallRadius)
                .stroke(WaymarkTheme.line, lineWidth: 1)
        )
    }
}

private struct AccountStatusRow: View {
    let title: String
    let detail: String
    let systemImage: String
    let tint: Color

    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: systemImage)
                .foregroundStyle(tint)
                .frame(width: 28)

            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.headline)
                    .foregroundStyle(WaymarkTheme.text)
                Text(detail)
                    .font(.caption)
                    .foregroundStyle(WaymarkTheme.mutedText)
            }

            Spacer()
        }
    }
}

private struct WaymarkFirstRunScroll<Content: View>: View {
    @ViewBuilder let content: Content

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                Spacer(minLength: 16)
                content
            }
            .padding(24)
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .background(CartenzaTopographicBackdrop().ignoresSafeArea())
    }
}

private struct WaymarkHeroIcon: View {
    let systemImage: String
    let tint: Color

    var body: some View {
        CartenzaCompassMark(systemImage: systemImage, tint: tint)
    }
}

private struct WaymarkStepHeader: View {
    let step: String

    var body: some View {
        HStack {
            HStack(spacing: 8) {
                CartenzaCompassMark(size: 30)

                VStack(alignment: .leading, spacing: 0) {
                    Text(CartenzaBrand.name)
                        .font(.headline.weight(.bold))
                        .foregroundStyle(WaymarkTheme.text)
                    Text(CartenzaBrand.tagline)
                        .font(.caption2.weight(.semibold))
                        .tracking(0.8)
                        .foregroundStyle(WaymarkTheme.signal)
                        .textCase(.uppercase)
                }
            }
            Spacer()
            Text(step)
                .font(.caption.weight(.bold))
                .foregroundStyle(WaymarkTheme.text)
                .padding(.horizontal, 10)
                .padding(.vertical, 6)
                .background(WaymarkTheme.raisedPanel, in: Capsule())
                .overlay(
                    Capsule()
                        .stroke(WaymarkTheme.line, lineWidth: 1)
                )
        }
    }
}

private struct WaymarkDisclosureRow: View {
    let title: String
    let detail: String

    var body: some View {
        VStack(alignment: .leading, spacing: 3) {
            Text(title)
                .font(.headline)
                .foregroundStyle(WaymarkTheme.text)
            Text(detail)
                .font(.callout)
                .foregroundStyle(WaymarkTheme.mutedText)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(WaymarkTheme.panel, in: RoundedRectangle(cornerRadius: WaymarkTheme.smallRadius))
    }
}

private enum WaymarkSurface {
    static let background = WaymarkTheme.background
    static let panel = WaymarkTheme.panel
    static let stroke = WaymarkTheme.line
    static let secondaryText = WaymarkTheme.mutedText
}
