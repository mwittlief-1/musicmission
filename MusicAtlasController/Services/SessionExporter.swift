import Foundation

#if canImport(UIKit)
import UIKit
#endif

struct ExportPreview {
    let kind: ExportKind
    let jsonString: String
    let markdownString: String
    let jsonFilename: String
    let markdownFilename: String
}

enum ExportKind: String, Equatable {
    case developmentStub = "development_stub"
    case acceptance

    var directoryName: String {
        switch self {
        case .developmentStub:
            return "dev"
        case .acceptance:
            return "acceptance"
        }
    }

    var displayName: String {
        switch self {
        case .developmentStub:
            return "Development stub"
        case .acceptance:
            return "Acceptance"
        }
    }
}

struct SavedExport {
    let kind: ExportKind
    let directoryURL: URL
    let jsonURL: URL
    let markdownURL: URL

    var shareURLs: [URL] {
        [jsonURL, markdownURL]
    }
}

struct SessionItemEvidence {
    let item: MissionItem
    let resolution: AppleMusicResolution
    let playback: PlaybackRecord
    let reaction: ReactionRecord
}

struct ExportFileStore {
    private let fileManager: FileManager
    private let baseDirectoryURL: URL?

    init(fileManager: FileManager = .default, baseDirectoryURL: URL? = nil) {
        self.fileManager = fileManager
        self.baseDirectoryURL = baseDirectoryURL
    }

    func save(_ preview: ExportPreview) throws -> SavedExport {
        let directoryURL = try exportDirectory(for: preview.kind)
        try fileManager.createDirectory(at: directoryURL, withIntermediateDirectories: true)

        let jsonURL = directoryURL.appendingPathComponent(preview.jsonFilename, isDirectory: false)
        let markdownURL = directoryURL.appendingPathComponent(preview.markdownFilename, isDirectory: false)

        guard let jsonData = preview.jsonString.data(using: .utf8),
              let markdownData = preview.markdownString.data(using: .utf8) else {
            throw SessionExporterError.encodingFailed
        }

        try jsonData.write(to: jsonURL, options: .atomic)
        try markdownData.write(to: markdownURL, options: .atomic)

        return SavedExport(
            kind: preview.kind,
            directoryURL: directoryURL,
            jsonURL: jsonURL,
            markdownURL: markdownURL
        )
    }

    private func exportDirectory(for kind: ExportKind) throws -> URL {
        let rootURL: URL
        if let baseDirectoryURL {
            rootURL = baseDirectoryURL
        } else {
            rootURL = try fileManager.url(
                for: .documentDirectory,
                in: .userDomainMask,
                appropriateFor: nil,
                create: true
            )
            .appendingPathComponent("MusicAtlasControllerExports", isDirectory: true)
        }

        return rootURL.appendingPathComponent(kind.directoryName, isDirectory: true)
    }
}

struct SessionExporter {
    private let encoder: JSONEncoder
    private let timestampFormatter: DateFormatter

    init() {
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        self.encoder = encoder

        let formatter = DateFormatter()
        formatter.calendar = Calendar(identifier: .gregorian)
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone(secondsFromGMT: 0)
        formatter.dateFormat = "yyyyMMdd_HHmmss"
        self.timestampFormatter = formatter
    }

    func makeDevelopmentExport(
        mission: Mission,
        item: MissionItem,
        resolution: AppleMusicResolution,
        playback: PlaybackRecord,
        reaction: ReactionRecord,
        authorizationStatus: String,
        now: Date = Date()
    ) throws -> ExportPreview {
        try makeDevelopmentExport(
            mission: mission,
            evidenceItems: [
                SessionItemEvidence(
                    item: item,
                    resolution: resolution,
                    playback: playback,
                    reaction: reaction
                )
            ],
            authorizationStatus: authorizationStatus,
            now: now
        )
    }

    func makeDevelopmentExport(
        mission: Mission,
        evidenceItems: [SessionItemEvidence],
        authorizationStatus: String,
        now: Date = Date()
    ) throws -> ExportPreview {
        try makeExport(
            kind: .developmentStub,
            mission: mission,
            evidenceItems: evidenceItems,
            authorizationStatus: authorizationStatus,
            deviceContext: DeviceContextProvider.developmentStubContext(),
            now: now
        )
    }

    func makeAcceptanceExport(
        mission: Mission,
        item: MissionItem,
        resolution: AppleMusicResolution,
        playback: PlaybackRecord,
        reaction: ReactionRecord,
        authorizationStatus: String,
        deviceContext: DeviceContext,
        now: Date = Date()
    ) throws -> ExportPreview {
        try makeAcceptanceExport(
            mission: mission,
            evidenceItems: [
                SessionItemEvidence(
                    item: item,
                    resolution: resolution,
                    playback: playback,
                    reaction: reaction
                )
            ],
            authorizationStatus: authorizationStatus,
            deviceContext: deviceContext,
            now: now
        )
    }

    func makeAcceptanceExport(
        mission: Mission,
        evidenceItems: [SessionItemEvidence],
        authorizationStatus: String,
        deviceContext: DeviceContext,
        now: Date = Date()
    ) throws -> ExportPreview {
        guard deviceContext.isPhysicalDevice else {
            throw SessionExporterError.physicalDeviceRequired
        }

        return try makeExport(
            kind: .acceptance,
            mission: mission,
            evidenceItems: evidenceItems,
            authorizationStatus: authorizationStatus,
            deviceContext: deviceContext,
            now: now
        )
    }

    private func makeExport(
        kind: ExportKind,
        mission: Mission,
        evidenceItems: [SessionItemEvidence],
        authorizationStatus: String,
        deviceContext: DeviceContext,
        now: Date
    ) throws -> ExportPreview {
        guard !evidenceItems.isEmpty else {
            throw SessionExporterError.noExportableItems
        }

        for evidenceItem in evidenceItems {
            guard evidenceItem.resolution.status == .resolved else {
                throw SessionExporterError.itemNotResolved
            }

            if kind == .acceptance {
                guard !evidenceItem.resolution.isDevelopmentStubEvidence else {
                    throw SessionExporterError.stubEvidenceCannotBeAcceptance
                }
            }

            guard evidenceItem.playback.hasExportablePlaybackEvidence else {
                throw SessionExporterError.itemNotPlayed
            }
        }

        let timestamp = timestampFormatter.string(from: now)
        let jsonFilename: String
        let markdownFilename: String
        let sessionID: String
        let subscriptionNotes: String
        let summaryNote: String

        switch kind {
        case .developmentStub:
            jsonFilename = "stub_reaction_session_\(timestamp).json"
            markdownFilename = "stub_discovery_log_\(timestamp).md"
            sessionID = "SESS_DEV_STUB_\(timestamp)"
            subscriptionNotes = "Development stub export. Resolver and playback are simulated; this is not physical-device acceptance evidence."
            summaryNote = "Development stub export for local loop validation."
        case .acceptance:
            jsonFilename = "acceptance_reaction_session_\(timestamp).json"
            markdownFilename = "acceptance_discovery_log_\(timestamp).md"
            sessionID = "SESS_ACCEPTANCE_\(timestamp)"
            subscriptionNotes = "Physical-device acceptance export. Resolver and playback are live MusicKit evidence; no Atlas canon reconciliation has been applied."
            summaryNote = "Physical-device acceptance export for mission listening evidence."
        }

        let itemResults = evidenceItems
            .sorted { $0.item.sequence < $1.item.sequence }
            .map { evidenceItem in
                ItemResult(
                    missionItemID: evidenceItem.item.itemID,
                    sequence: evidenceItem.item.sequence,
                    itemType: evidenceItem.item.itemType,
                    artist: evidenceItem.item.artist,
                    title: evidenceItem.item.title,
                    album: evidenceItem.item.album,
                    resolution: evidenceItem.resolution,
                    playback: evidenceItem.playback.finalizedForExport(at: now),
                    reaction: evidenceItem.reaction,
                    timestamps: ItemTimestamps(createdAt: now, updatedAt: now)
                )
            }

        let firstResolvedStorefront = itemResults.compactMap(\.resolution.storefront).first
        let playbackCapabilityStatus: String
        if itemResults.contains(where: { $0.playback.status == .failed }) {
            playbackCapabilityStatus = "failed"
        } else if itemResults.contains(where: { $0.playback.hasExportablePlaybackEvidence }) {
            playbackCapabilityStatus = kind == .acceptance ? "capable" : "unknown"
        } else {
            playbackCapabilityStatus = "unknown"
        }

        let session = ReactionSession(
            schemaVersion: "reaction_session.v0.2",
            sessionID: sessionID,
            missionID: mission.missionID,
            missionVersion: mission.missionVersion,
            createdAt: now,
            startedAt: itemResults.compactMap(\.playback.startedAt).min() ?? now,
            endedAt: now,
            reconciliationStatus: .notReconciled,
            deviceContext: deviceContext,
            musicContext: MusicContext(
                authorizationStatus: Self.schemaAuthorizationStatus(from: authorizationStatus),
                playbackCapabilityStatus: playbackCapabilityStatus,
                storefront: firstResolvedStorefront,
                subscriptionNotes: subscriptionNotes
            ),
            itemResults: itemResults,
            sessionSummary: SessionSummary(
                itemCount: mission.items.count,
                resolvedCount: itemResults.filter { $0.resolution.status == .resolved }.count,
                playedCount: itemResults.filter { $0.playback.hasExportablePlaybackEvidence }.count,
                reactionCount: itemResults.count,
                summaryNote: summaryNote
            ),
            export: ExportRecord(
                exportedAt: now,
                jsonFilename: jsonFilename,
                markdownFilename: markdownFilename,
                validationStatus: "not_validated",
                validationErrors: nil
            )
        )

        let data = try encoder.encode(session)
        guard let jsonString = String(data: data, encoding: .utf8) else {
            throw SessionExporterError.encodingFailed
        }

        let markdownString: String
        switch kind {
        case .developmentStub:
            markdownString = MarkdownDiscoveryLogRenderer.renderDevelopmentStub(
                mission: mission,
                itemResults: itemResults,
                exportedAt: now
            )
        case .acceptance:
            markdownString = MarkdownDiscoveryLogRenderer.renderAcceptance(
                mission: mission,
                itemResults: itemResults,
                deviceContext: deviceContext,
                exportedAt: now
            )
        }

        return ExportPreview(
            kind: kind,
            jsonString: jsonString,
            markdownString: markdownString,
            jsonFilename: jsonFilename,
            markdownFilename: markdownFilename
        )
    }

    private static func schemaAuthorizationStatus(from status: String) -> String {
        let allowed = ["notDetermined", "denied", "restricted", "authorized"]
        return allowed.contains(status) ? status : "notDetermined"
    }

    private static func schemaPlaybackCapabilityStatus(from playback: PlaybackRecord) -> String {
        switch playback.status {
        case .playing, .played, .skipped:
            return "capable"
        case .failed:
            return "failed"
        case .notAttempted, .queued:
            return "unknown"
        }
    }
}

enum SessionExporterError: LocalizedError, Equatable {
    case noExportableItems
    case itemNotResolved
    case itemNotPlayed
    case emptyReactionNote
    case encodingFailed
    case physicalDeviceRequired
    case stubEvidenceCannotBeAcceptance

    var errorDescription: String? {
        switch self {
        case .noExportableItems:
            return "Play and react to at least one item before exporting."
        case .itemNotResolved:
            return "Resolve the selected item before exporting."
        case .itemNotPlayed:
            return "The selected item needs played playback status before exporting."
        case .emptyReactionNote:
            return "Enter a non-empty reaction note before exporting."
        case .encodingFailed:
            return "Could not encode the reaction session JSON."
        case .physicalDeviceRequired:
            return "Acceptance export requires a physical iPhone."
        case .stubEvidenceCannotBeAcceptance:
            return "Stub resolver evidence cannot be exported as physical-device acceptance evidence."
        }
    }
}

private extension PlaybackRecord {
    func finalizedForExport(at date: Date) -> PlaybackRecord {
        status == .playing ? endedAsPlayed(at: date) : self
    }
}

struct DeviceContextProvider {
    static func currentContext() -> DeviceContext {
        #if canImport(UIKit)
        let device = UIDevice.current
        let deviceModel = device.model
        let osVersion = "\(device.systemName) \(device.systemVersion)"
        #else
        let deviceModel = "Unknown Device"
        let osVersion = ProcessInfo.processInfo.operatingSystemVersionString
        #endif

        #if os(iOS) && !targetEnvironment(simulator)
        let isPhysicalDevice = true
        #else
        let isPhysicalDevice = false
        #endif

        return DeviceContext(
            deviceModel: deviceModel,
            osVersion: osVersion,
            appVersion: Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "unknown",
            isPhysicalDevice: isPhysicalDevice
        )
    }

    static func developmentStubContext() -> DeviceContext {
        DeviceContext(
            deviceModel: "Development Stub",
            osVersion: ProcessInfo.processInfo.operatingSystemVersionString,
            appVersion: "0.2-dev",
            isPhysicalDevice: false
        )
    }
}

enum MarkdownDiscoveryLogRenderer {
    static func renderDevelopmentStub(mission: Mission, itemResult: ItemResult, exportedAt: Date) -> String {
        renderDevelopmentStub(mission: mission, itemResults: [itemResult], exportedAt: exportedAt)
    }

    static func renderDevelopmentStub(mission: Mission, itemResults: [ItemResult], exportedAt: Date) -> String {
        """
        # Music Atlas Discovery Log

        - Mission: \(mission.missionTitle)
        - Mission ID: \(mission.missionID)
        - Export type: development stub
        - Exported at: \(ISO8601DateFormatter().string(from: exportedAt))
        - Reconciliation status: not_reconciled

        ## Acceptance Notice

        This is a development/stub export. Resolver and playback are simulated, `device_context.is_physical_device` is false, and this file does not count as physical-device acceptance evidence.

        ## Items Tested

        \(Self.renderItemResults(itemResults))

        ## Reconciliation

        Do not update Atlas canon from this export automatically.
        """
    }

    static func renderAcceptance(
        mission: Mission,
        itemResult: ItemResult,
        deviceContext: DeviceContext,
        exportedAt: Date
    ) -> String {
        renderAcceptance(
            mission: mission,
            itemResults: [itemResult],
            deviceContext: deviceContext,
            exportedAt: exportedAt
        )
    }

    static func renderAcceptance(
        mission: Mission,
        itemResults: [ItemResult],
        deviceContext: DeviceContext,
        exportedAt: Date
    ) -> String {
        """
        # Music Atlas Discovery Log

        - Mission: \(mission.missionTitle)
        - Mission ID: \(mission.missionID)
        - Export type: physical-device acceptance
        - Exported at: \(ISO8601DateFormatter().string(from: exportedAt))
        - Reconciliation status: not_reconciled

        ## Device Evidence

        - Device model: \(deviceContext.deviceModel)
        - OS version: \(deviceContext.osVersion)
        - Physical iPhone: \(deviceContext.isPhysicalDevice ? "true" : "false")

        ## Items Tested

        \(Self.renderItemResults(itemResults))

        ## Reconciliation

        Do not update Atlas canon from this export automatically.
        """
    }

    private static func renderSelectedTags(_ selectedTags: [ReactionTag]?) -> String {
        guard let selectedTags, !selectedTags.isEmpty else {
            return "none"
        }

        return selectedTags.map(\.label).joined(separator: ", ")
    }

    private static func renderItemResults(_ itemResults: [ItemResult]) -> String {
        itemResults.map { itemResult in
            """
            ### \(itemResult.sequence). \(itemResult.artist) - \(itemResult.title)

            - Album: \(itemResult.album ?? "")
            - Resolution status: \(itemResult.resolution.status.rawValue)
            - Catalog ID: \(itemResult.resolution.catalogID ?? "")
            - Candidate count: \(itemResult.resolution.candidateCount ?? 0)
            - Confidence: \(itemResult.resolution.confidence ?? 0)
            - Resolver: \(itemResult.resolution.resolver?.rawValue ?? "")
            - Storefront: \(itemResult.resolution.storefront ?? "")
            - Playback status: \(itemResult.playback.status.rawValue)
            - Reaction: \(itemResult.reaction.reactionValue.rawValue)
            - Tags: \(Self.renderSelectedTags(itemResult.reaction.selectedTags))
            - Note: \(itemResult.reaction.notes.text)
            """
        }
        .joined(separator: "\n\n")
    }
}
