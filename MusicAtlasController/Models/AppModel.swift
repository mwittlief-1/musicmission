import Foundation
import Combine

@MainActor
final class AppModel: ObservableObject {
    enum LoadState: Equatable {
        case idle
        case loading
        case loaded
        case failed(String)
    }

    @Published private(set) var availableMissions: [Mission] = []
    @Published private(set) var mission: Mission?
    @Published private(set) var missionLoadState: LoadState = .idle
    @Published var selectedItemID: String?
    @Published private(set) var resolutions: [String: AppleMusicResolution] = [:]
    @Published private(set) var playbackRecords: [String: PlaybackRecord] = [:]
    @Published private(set) var exportPreview: ExportPreview?
    @Published private(set) var savedExport: SavedExport?
    @Published private(set) var lastActionMessage: String?
    @Published private(set) var reactionRevision = 0
    @Published private(set) var isResolvingMission = false
    @Published private(set) var activePlaybackSnapshot: PlaybackSnapshot = .idle
    @Published private(set) var observedPlaybackItemID: String?
    @Published private(set) var playerActionLog: [PlayerActionLogEntry] = []
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

    let musicAuthorization = MusicAuthorizationService()
    let reactionStore = ReactionStore()

    private let missionLoader = MissionLoader()
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

    init(
        stubSearchService: any MusicSearchServing = StubMusicSearchService(),
        liveSearchService: any MusicSearchServing = MusicKitCatalogSearchService(),
        stubPlaybackService: any MusicPlaybackServing = StubMusicPlaybackService(),
        livePlaybackService: any MusicPlaybackServing = MusicKitPlaybackService(),
        sessionExporter: SessionExporter = SessionExporter(),
        exportFileStore: ExportFileStore = ExportFileStore(),
        sessionPersistenceStore: SessionPersistenceStore = SessionPersistenceStore()
    ) {
        self.stubSearchService = stubSearchService
        self.liveSearchService = liveSearchService
        self.stubPlaybackService = stubPlaybackService
        self.livePlaybackService = livePlaybackService
        self.sessionExporter = sessionExporter
        self.exportFileStore = exportFileStore
        self.sessionPersistenceStore = sessionPersistenceStore
    }

    deinit {
        playbackPollingTask?.cancel()
    }

    func loadSampleMission() {
        loadMissionLibrary()
    }

    func loadMissionLibrary() {
        guard availableMissions.isEmpty else {
            return
        }

        missionLoadState = .loading

        do {
            let loadedMissions = try missionLoader.loadBundledMissionLibrary()
            let restoredLibrary = sessionPersistenceStore.load()
            availableMissions = loadedMissions
            persistedSessionLibrary = restoredLibrary

            let restoredMission = restoredLibrary.activeMissionID.flatMap { activeMissionID in
                loadedMissions.first { $0.missionID == activeMissionID }
            }
            let selectedMission = restoredMission ?? loadedMissions.first

            if let selectedMission {
                restoreSessionState(for: selectedMission, persistedSession: restoredLibrary.sessionsByMissionID[selectedMission.missionID])
            }
            missionLoadState = .loaded
        } catch {
            missionLoadState = .failed(error.localizedDescription)
        }
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
                authorizationStatus: musicAuthorization.snapshot.status
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
                authorizationStatus: musicAuthorization.snapshot.status,
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
            savedExport = try exportFileStore.save(exportPreview)
            lastActionMessage = "Saved \(exportPreview.kind.displayName.lowercased()) JSON and Markdown export files."
        } catch {
            savedExport = nil
            lastActionMessage = error.localizedDescription
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

        if musicAuthorization.snapshot.status != "authorized",
           musicAuthorization.snapshot.canRequestAuthorization {
            await musicAuthorization.requestAuthorization()
        } else {
            musicAuthorization.refreshStatus()
        }

        guard musicAuthorization.snapshot.status == "authorized" else {
            lastActionMessage = "Apple Music authorization is \(musicAuthorization.snapshot.status). Request access before using Live MusicKit."
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
