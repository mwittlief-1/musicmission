import CryptoKit
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
    let atlasSignalCandidateCount: Int
}

enum ExportKind: String, Codable, Equatable {
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

struct SavedExport: Codable, Equatable {
    let kind: ExportKind
    let directoryURL: URL
    let jsonURL: URL
    let markdownURL: URL

    var shareURLs: [URL] {
        [jsonURL, markdownURL]
    }
}

struct EvidenceUploadClientConfig: Equatable {
    let baseURL: URL?
    let endpointPath: String
    let anonKey: String?
    let uploadCadence: EvidenceUploadCadence

    static let disabled = EvidenceUploadClientConfig(
        baseURL: nil,
        endpointPath: "/functions/v1/submit-alpha-evidence",
        anonKey: nil,
        uploadCadence: .manualShare
    )
}

enum EvidenceUploadCadence: String, Codable, Equatable {
    case manualShare = "manual_share"
    case afterSavedEvidence = "after_saved_evidence"
    case scheduled = "scheduled"
}

struct EvidenceUploadRequest: Equatable {
    let testerAlias: String
    let savedExport: SavedExport
    let requestedAt: Date
    let sourceAppVersion: String
    let sourceAppBuild: String
    let termsVersion: String
    let acceptedAt: Date
}

struct EvidenceUploadResult: Codable, Equatable {
    let uploadID: String
    let status: String
    let receivedAt: Date?
    let userIDPresent: Bool?

    enum CodingKeys: String, CodingKey {
        case uploadID = "upload_id"
        case status
        case receivedAt = "received_at"
        case userIDPresent = "user_id_present"
    }
}

struct DiagnosticUploadRequest: Equatable {
    let testerAlias: String
    let package: SavedClientDiagnosticPackage
    let requestedAt: Date
    let sourceAppVersion: String
    let sourceAppBuild: String
    let termsVersion: String
    let acceptedAt: Date
}

struct DiagnosticArtifactUploadResult: Codable, Equatable {
    let uploadID: String
    let status: String
    let receivedAt: Date?
    let artifactType: String?
    let schemaVersion: String?
    let payloadSha256: String?
    let userIDPresent: Bool?

    enum CodingKeys: String, CodingKey {
        case uploadID = "upload_id"
        case status
        case receivedAt = "received_at"
        case artifactType = "artifact_type"
        case schemaVersion = "schema_version"
        case payloadSha256 = "payload_sha256"
        case userIDPresent = "user_id_present"
    }
}

struct DiagnosticUploadBatchResult: Equatable {
    let status: String
    let uploadedCount: Int
    let uploadIDs: [String]
    let userIDPresent: Bool?
}

enum ClientDiagnosticArtifactType: String, Codable, CaseIterable {
    case appleMusicSignalPayload = "apple_music_signal_payload"
    case surveyPageSelectionAudit = "survey_page_selection_audit"
    case surveyEvidenceExport = "survey_evidence_export"
    case missionGenerationRequestPacket = "mission_generation_request_packet"
    case missionGenerationResult = "mission_generation_result"
    case missionImportResult = "mission_import_result"
    case missionSelectionAudit = "mission_selection_audit"
    case clientStateSnapshot = "client_state_snapshot"
    case clientErrorEvent = "client_error_event"
}

struct ClientDiagnosticLinkContext: Equatable {
    var testerAlias: String?
    var supabaseUserID: String?
    var surveySessionID: String?
    var clientRequestID: String?
    var generationRunID: String?
    var missionID: String?
    var sourceAppVersion: String
    var sourceAppBuild: String
}

struct SavedClientDiagnosticPackage: Equatable {
    let directoryURL: URL
    let indexURL: URL
    let artifactURLs: [URL]

    var shareURLs: [URL] {
        [indexURL] + artifactURLs
    }
}

struct ClientDiagnosticArtifactStore {
    private let fileManager: FileManager
    private let baseDirectoryURL: URL?
    private let isEnabled: Bool

    init(
        fileManager: FileManager = .default,
        baseDirectoryURL: URL? = nil,
        isEnabled: Bool = true
    ) {
        self.fileManager = fileManager
        self.baseDirectoryURL = baseDirectoryURL
        self.isEnabled = isEnabled
    }

    static let disabled = ClientDiagnosticArtifactStore(isEnabled: false)

    @discardableResult
    func saveArtifact(
        type: ClientDiagnosticArtifactType,
        payload: [String: Any],
        context: ClientDiagnosticLinkContext,
        now: Date = Date()
    ) throws -> URL? {
        guard isEnabled else {
            return nil
        }

        let envelope = try makeEnvelope(type: type, payload: payload, context: context, now: now)
        let data = try JSONSerialization.data(withJSONObject: envelope, options: [.prettyPrinted, .sortedKeys])
        let artifactID = envelope["artifact_id"] as? String ?? "client_diagnostic:\(UUID().uuidString)"
        let filename = sanitizedFilename(artifactID) + ".json"
        let url = (try artifactDirectoryURL()).appendingPathComponent(filename, isDirectory: false)
        try fileManager.createDirectory(at: url.deletingLastPathComponent(), withIntermediateDirectories: true)
        try data.write(to: url, options: .atomic)
        return url
    }

    func savePackage(
        additionalArtifacts: [(type: ClientDiagnosticArtifactType, payload: [String: Any], context: ClientDiagnosticLinkContext)] = [],
        now: Date = Date()
    ) throws -> SavedClientDiagnosticPackage? {
        guard isEnabled else {
            return nil
        }

        for artifact in additionalArtifacts {
            try saveArtifact(type: artifact.type, payload: artifact.payload, context: artifact.context, now: now)
        }

        let existingArtifactURLs = try existingArtifactURLs()
        let packageDirectory = try packageDirectoryURL(now: now)
        try fileManager.createDirectory(at: packageDirectory, withIntermediateDirectories: true)

        var copiedArtifactURLs: [URL] = []
        for sourceURL in existingArtifactURLs {
            let targetURL = packageDirectory.appendingPathComponent(sourceURL.lastPathComponent, isDirectory: false)
            if fileManager.fileExists(atPath: targetURL.path) {
                try fileManager.removeItem(at: targetURL)
            }
            try fileManager.copyItem(at: sourceURL, to: targetURL)
            copiedArtifactURLs.append(targetURL)
        }

        let indexURL = packageDirectory.appendingPathComponent("waymark_support_diagnostics_index.json", isDirectory: false)
        let index: [String: Any] = [
            "schema_version": "waymark.support_diagnostics_package.v0.1",
            "package_id": "support_diagnostics_package:\(UUID().uuidString)",
            "created_at": isoString(now),
            "artifact_count": copiedArtifactURLs.count,
            "upload_posture": "manual_share_or_authenticated_support_upload",
            "atlas_truth_policy": "diagnostics_only_not_promoted",
            "artifacts": copiedArtifactURLs.map { $0.lastPathComponent }
        ]
        let indexData = try JSONSerialization.data(withJSONObject: index, options: [.prettyPrinted, .sortedKeys])
        try indexData.write(to: indexURL, options: .atomic)

        return SavedClientDiagnosticPackage(
            directoryURL: packageDirectory,
            indexURL: indexURL,
            artifactURLs: copiedArtifactURLs.sorted { $0.lastPathComponent < $1.lastPathComponent }
        )
    }

    func reset() throws {
        guard isEnabled else {
            return
        }

        let root = try diagnosticsRootURL()
        if fileManager.fileExists(atPath: root.path) {
            try fileManager.removeItem(at: root)
        }
    }

    private func makeEnvelope(
        type: ClientDiagnosticArtifactType,
        payload: [String: Any],
        context: ClientDiagnosticLinkContext,
        now: Date
    ) throws -> [String: Any] {
        let payloadData = try JSONSerialization.data(withJSONObject: payload, options: [.sortedKeys])
        let payloadHash = sha256Hex(payloadData)
        let artifactID = [
            "client_diag",
            type.rawValue,
            context.surveySessionID,
            context.clientRequestID,
            context.generationRunID,
            UUID().uuidString
        ]
        .compactMap { $0 }
        .joined(separator: ":")

        return compactDictionary([
            "schema_version": "waymark.alpha_client_diagnostic_artifact.v0.1",
            "artifact_id": artifactID,
            "artifact_type": type.rawValue,
            "tester_alias": context.testerAlias,
            "supabase_user_id": context.supabaseUserID,
            "survey_session_id": context.surveySessionID,
            "client_request_id": context.clientRequestID,
            "generation_run_id": context.generationRunID,
            "mission_id": context.missionID,
            "source_app_version": context.sourceAppVersion,
            "source_app_build": context.sourceAppBuild,
            "client_created_at": isoString(now),
            "redaction_level": "support_diagnostic",
            "payload_sha256": payloadHash,
            "payload": payload
        ])
    }

    private func existingArtifactURLs() throws -> [URL] {
        let directory = try artifactDirectoryURL()
        guard fileManager.fileExists(atPath: directory.path) else {
            return []
        }

        return try fileManager
            .contentsOfDirectory(at: directory, includingPropertiesForKeys: nil)
            .filter { $0.pathExtension == "json" }
            .sorted { $0.lastPathComponent < $1.lastPathComponent }
    }

    private func artifactDirectoryURL() throws -> URL {
        try diagnosticsRootURL().appendingPathComponent("artifacts", isDirectory: true)
    }

    private func packageDirectoryURL(now: Date) throws -> URL {
        let formatter = DateFormatter()
        formatter.calendar = Calendar(identifier: .gregorian)
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone(secondsFromGMT: 0)
        formatter.dateFormat = "yyyyMMdd_HHmmss"
        return (try diagnosticsRootURL())
            .appendingPathComponent("packages", isDirectory: true)
            .appendingPathComponent("support_diagnostics_\(formatter.string(from: now))", isDirectory: true)
    }

    private func diagnosticsRootURL() throws -> URL {
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

        return rootURL.appendingPathComponent("support_diagnostics", isDirectory: true)
    }

    private func sanitizedFilename(_ value: String) -> String {
        value
            .replacingOccurrences(of: ":", with: "_")
            .replacingOccurrences(of: "/", with: "_")
            .replacingOccurrences(of: " ", with: "_")
    }

    private func sha256Hex(_ data: Data) -> String {
        SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined()
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

protocol EvidenceUploadClient {
    func uploadEvidence(_ request: EvidenceUploadRequest, accessToken: String) async throws -> EvidenceUploadResult
}

protocol DiagnosticUploadClient {
    func uploadDiagnostics(_ request: DiagnosticUploadRequest, accessToken: String) async throws -> DiagnosticUploadBatchResult
}

struct LocalEvidenceUploadClientStub: EvidenceUploadClient {
    func uploadEvidence(_ request: EvidenceUploadRequest, accessToken: String) async throws -> EvidenceUploadResult {
        EvidenceUploadResult(
            uploadID: "local_upload_stub_\(request.savedExport.jsonURL.deletingPathExtension().lastPathComponent)",
            status: "not_uploaded_manual_share_required",
            receivedAt: nil,
            userIDPresent: nil
        )
    }
}

struct LocalDiagnosticUploadClientStub: DiagnosticUploadClient {
    func uploadDiagnostics(_ request: DiagnosticUploadRequest, accessToken: String) async throws -> DiagnosticUploadBatchResult {
        DiagnosticUploadBatchResult(
            status: "not_uploaded_manual_share_required",
            uploadedCount: 0,
            uploadIDs: [],
            userIDPresent: nil
        )
    }
}

struct LiveEvidenceUploadClient: EvidenceUploadClient {
    let config: SupabaseAlphaConfig
    var urlSession: URLSession = .shared

    func uploadEvidence(_ request: EvidenceUploadRequest, accessToken: String) async throws -> EvidenceUploadResult {
        let urlRequest = try makeURLRequest(request: request, accessToken: accessToken)
        let (data, response) = try await urlSession.data(for: urlRequest)
        try SupabaseHTTP.validate(response: response, data: data)

        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return try decoder.decode(EvidenceUploadResult.self, from: data)
    }

    func makeURLRequest(request: EvidenceUploadRequest, accessToken: String) throws -> URLRequest {
        guard let projectURL = config.projectURL,
              let anonKey = config.anonKey,
              !anonKey.isEmpty else {
            throw SupabaseClientError.missingConfiguration
        }

        let url = projectURL
            .appendingPathComponent("functions")
            .appendingPathComponent("v1")
            .appendingPathComponent(config.submitAlphaEvidenceFunctionName)
        let payloadData = try Data(contentsOf: request.savedExport.jsonURL)
        let payloadObject = try SupabaseJSON.object(from: payloadData)
        let schemaVersion = Self.schemaVersion(from: payloadObject) ?? "reaction_session.v0.2"

        let uploadPayload: [String: Any] = [
            "client_artifact_id": request.savedExport.jsonURL.deletingPathExtension().lastPathComponent,
            "tester_alias": request.testerAlias,
            "artifact_type": "reaction_session",
            "schema_version": schemaVersion,
            "client_created_at": ISO8601DateFormatter().string(from: request.requestedAt),
            "source_app_version": request.sourceAppVersion,
            "source_app_build": request.sourceAppBuild,
            "upload_cadence": EvidenceUploadCadence.manualShare.rawValue,
            "consent": [
                "evidence_upload_allowed": true,
                "terms_version": request.termsVersion,
                "accepted_at": ISO8601DateFormatter().string(from: request.acceptedAt)
            ],
            "payload": payloadObject
        ]

        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue(anonKey, forHTTPHeaderField: "apikey")
        urlRequest.setValue("Bearer \(accessToken)", forHTTPHeaderField: "Authorization")
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.httpBody = try JSONSerialization.data(withJSONObject: uploadPayload, options: [.sortedKeys])
        return urlRequest
    }

    private static func schemaVersion(from object: Any) -> String? {
        guard let dictionary = object as? [String: Any] else {
            return nil
        }
        return dictionary["schema_version"] as? String
    }
}

struct LiveDiagnosticUploadClient: DiagnosticUploadClient {
    let config: SupabaseAlphaConfig
    var urlSession: URLSession = .shared

    func uploadDiagnostics(_ request: DiagnosticUploadRequest, accessToken: String) async throws -> DiagnosticUploadBatchResult {
        var uploadResults: [DiagnosticArtifactUploadResult] = []
        var failures: [String] = []

        for artifactURL in request.package.artifactURLs {
            do {
                let urlRequest = try makeURLRequest(
                    artifactURL: artifactURL,
                    request: request,
                    accessToken: accessToken
                )
                let (data, response) = try await urlSession.data(for: urlRequest)
                try SupabaseHTTP.validate(response: response, data: data)

                let decoder = JSONDecoder()
                decoder.dateDecodingStrategy = .iso8601
                uploadResults.append(try decoder.decode(DiagnosticArtifactUploadResult.self, from: data))
            } catch {
                failures.append("\(artifactURL.lastPathComponent): \(error.localizedDescription)")
            }
        }

        if uploadResults.isEmpty, !failures.isEmpty {
            throw DiagnosticUploadBatchFailure(failures: failures)
        }

        let allAccepted = uploadResults.allSatisfy { $0.status.hasPrefix("accepted") }
        return DiagnosticUploadBatchResult(
            status: failures.isEmpty && allAccepted ? "accepted" : "partial",
            uploadedCount: uploadResults.count,
            uploadIDs: uploadResults.map(\.uploadID),
            userIDPresent: uploadResults.contains { $0.userIDPresent == true }
        )
    }

    func makeURLRequest(
        artifactURL: URL,
        request: DiagnosticUploadRequest,
        accessToken: String
    ) throws -> URLRequest {
        guard let projectURL = config.projectURL,
              let anonKey = config.anonKey,
              !anonKey.isEmpty else {
            throw SupabaseClientError.missingConfiguration
        }

        let url = projectURL
            .appendingPathComponent("functions")
            .appendingPathComponent("v1")
            .appendingPathComponent(config.submitAlphaDiagnosticFunctionName)
        let artifactData = try Data(contentsOf: artifactURL)
        let artifactObject = try SupabaseJSON.object(from: artifactData)
        guard let artifact = artifactObject as? [String: Any],
              let payload = artifact["payload"] as? [String: Any] else {
            throw SupabaseClientError.invalidJSONPayload
        }

        let clientArtifactID = artifact["artifact_id"] as? String
            ?? artifactURL.deletingPathExtension().lastPathComponent
        let uploadPayload = Self.compactDictionary([
            "client_artifact_id": clientArtifactID,
            "tester_alias": artifact["tester_alias"] as? String ?? request.testerAlias,
            "artifact_type": artifact["artifact_type"],
            "schema_version": artifact["schema_version"],
            "survey_session_id": artifact["survey_session_id"],
            "client_request_id": artifact["client_request_id"],
            "generation_run_id": Self.uuidString(artifact["generation_run_id"]),
            "mission_id": artifact["mission_id"],
            "source_app_version": artifact["source_app_version"] as? String ?? request.sourceAppVersion,
            "source_app_build": artifact["source_app_build"] as? String ?? request.sourceAppBuild,
            "redaction_level": artifact["redaction_level"] as? String ?? "support_diagnostic",
            "upload_cadence": EvidenceUploadCadence.manualShare.rawValue,
            "client_created_at": artifact["client_created_at"] as? String ?? ISO8601DateFormatter().string(from: request.requestedAt),
            "consent": [
                "diagnostic_upload_allowed": true,
                "terms_version": request.termsVersion,
                "accepted_at": ISO8601DateFormatter().string(from: request.acceptedAt)
            ],
            "payload": payload
        ])

        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue(anonKey, forHTTPHeaderField: "apikey")
        urlRequest.setValue("Bearer \(accessToken)", forHTTPHeaderField: "Authorization")
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.httpBody = try JSONSerialization.data(withJSONObject: uploadPayload, options: [.sortedKeys])
        return urlRequest
    }

    private static func uuidString(_ value: Any?) -> String? {
        guard let string = value as? String,
              UUID(uuidString: string) != nil else {
            return nil
        }
        return string
    }

    private static func compactDictionary(_ dictionary: [String: Any?]) -> [String: Any] {
        dictionary.reduce(into: [String: Any]()) { result, pair in
            if let value = pair.value {
                result[pair.key] = value
            }
        }
    }
}

private struct DiagnosticUploadBatchFailure: LocalizedError {
    let failures: [String]

    var errorDescription: String? {
        let details = failures.prefix(3).joined(separator: "; ")
        let suffix = failures.count > 3 ? " and \(failures.count - 3) more" : ""
        return "Support diagnostics upload failed for all artifacts: \(details)\(suffix)"
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
        let exportID: String
        let sessionID: String
        let subscriptionNotes: String
        let summaryNote: String

        switch kind {
        case .developmentStub:
            jsonFilename = "stub_reaction_session_\(timestamp).json"
            markdownFilename = "stub_discovery_log_\(timestamp).md"
            exportID = "EXPORT_DEV_STUB_\(timestamp)"
            sessionID = "SESS_DEV_STUB_\(timestamp)"
            subscriptionNotes = "Development stub export. Resolver and playback are simulated; this is not physical-device acceptance evidence."
            summaryNote = "Development stub export for local loop validation."
        case .acceptance:
            jsonFilename = "acceptance_reaction_session_\(timestamp).json"
            markdownFilename = "acceptance_discovery_log_\(timestamp).md"
            exportID = "EXPORT_ACCEPTANCE_\(timestamp)"
            sessionID = "SESS_ACCEPTANCE_\(timestamp)"
            subscriptionNotes = "Physical-device acceptance export. Resolver and playback are live MusicKit evidence; no Atlas canon reconciliation has been applied."
            summaryNote = "Physical-device acceptance export for mission listening evidence."
        }

        let sortedEvidenceItems = evidenceItems.sorted { $0.item.sequence < $1.item.sequence }
        let itemResults = sortedEvidenceItems
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
        let atlasSignalCandidateBundle = AtlasSignalCandidateBuilder.makeBundle(
            mission: mission,
            evidenceItems: sortedEvidenceItems,
            itemResults: itemResults,
            deviceContext: deviceContext,
            sessionID: sessionID,
            exportID: exportID,
            generatedAt: now
        )

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
            atlasSignalCandidateBundle: atlasSignalCandidateBundle,
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
                atlasSignalCandidateBundle: atlasSignalCandidateBundle,
                exportedAt: now
            )
        case .acceptance:
            markdownString = MarkdownDiscoveryLogRenderer.renderAcceptance(
                mission: mission,
                itemResults: itemResults,
                atlasSignalCandidateBundle: atlasSignalCandidateBundle,
                deviceContext: deviceContext,
                exportedAt: now
            )
        }

        return ExportPreview(
            kind: kind,
            jsonString: jsonString,
            markdownString: markdownString,
            jsonFilename: jsonFilename,
            markdownFilename: markdownFilename,
            atlasSignalCandidateCount: atlasSignalCandidateBundle.candidates.count
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

private enum AtlasSignalCandidateBuilder {
    static func makeBundle(
        mission: Mission,
        evidenceItems: [SessionItemEvidence],
        itemResults: [ItemResult],
        deviceContext: DeviceContext,
        sessionID: String,
        exportID: String,
        generatedAt: Date
    ) -> AtlasSignalCandidateBundle {
        let evidenceByItemID = Dictionary(uniqueKeysWithValues: evidenceItems.map { ($0.item.itemID, $0) })
        let candidates = itemResults.flatMap { itemResult -> [AtlasSignalCandidate] in
            guard let evidenceItem = evidenceByItemID[itemResult.missionItemID] else {
                return []
            }

            return makeCandidates(
                mission: mission,
                evidenceItem: evidenceItem,
                itemResult: itemResult,
                sessionID: sessionID,
                exportID: exportID,
                capturedAt: generatedAt
            )
        }

        return AtlasSignalCandidateBundle(
            recordType: "atlas_signal_candidate_bundle",
            schemaVersion: "atlas_signal_candidate_bundle.v0.1",
            candidateStatus: "ingestion_candidate",
            promotionState: "not_promoted",
            writesAtlasTruth: false,
            canonicalGraphMutationAllowed: false,
            exportID: exportID,
            sessionID: sessionID,
            missionID: mission.missionID,
            generatedAt: generatedAt,
            sourceAppSchemaVersion: "reaction_session.v0.2",
            sourceAppVersion: deviceContext.appVersion,
            isPhysicalDevice: deviceContext.isPhysicalDevice,
            guardrails: [
                "candidate_only",
                "requires_atlas_ingestion_review",
                "no_atlas_truth_write",
                "no_canonical_graph_mutation"
            ],
            candidates: candidates
        )
    }

    private static func makeCandidates(
        mission: Mission,
        evidenceItem: SessionItemEvidence,
        itemResult: ItemResult,
        sessionID: String,
        exportID: String,
        capturedAt: Date
    ) -> [AtlasSignalCandidate] {
        let subject = makeSubject(from: itemResult)
        let selectedChips = makeSelectedChips(from: itemResult.reaction)
        let shownUnselectedChips = makeShownUnselectedChips(
            item: evidenceItem.item,
            reaction: itemResult.reaction,
            selectedChips: selectedChips
        )
        let reviewFlags = makeReviewFlags(from: itemResult)
        let reviewNeeded = !reviewFlags.isEmpty
        let reviewState = reviewNeeded ? "needs_review" : "unreviewed"

        var candidates: [AtlasSignalCandidate] = [
            candidate(
                sessionID: sessionID,
                exportID: exportID,
                missionID: mission.missionID,
                itemResult: itemResult,
                subject: subject,
                eventType: .resolution,
                occurredAt: itemResult.resolution.resolvedAt,
                capturedAt: capturedAt,
                reviewState: reviewState,
                evidence: AtlasSignalCandidateEvidence(
                    resolutionStatus: itemResult.resolution.status,
                    candidateCount: itemResult.resolution.candidateCount,
                    confidence: itemResult.resolution.confidence,
                    resolver: itemResult.resolution.resolver,
                    playbackStatus: nil,
                    playbackStartedAt: nil,
                    playbackEndedAt: nil,
                    playbackDurationSeconds: nil,
                    skipPolicy: nil,
                    reactionValue: nil,
                    reactionOperation: nil,
                    reactionLabel: nil,
                    selectedChip: nil,
                    selectedChips: nil,
                    shownUnselectedChips: nil,
                    noteText: nil,
                    reviewFlags: reviewFlags,
                    reviewNeeded: reviewNeeded
                )
            ),
            candidate(
                sessionID: sessionID,
                exportID: exportID,
                missionID: mission.missionID,
                itemResult: itemResult,
                subject: subject,
                eventType: .playback,
                occurredAt: itemResult.playback.endedAt ?? itemResult.playback.startedAt ?? itemResult.playback.attemptedAt,
                capturedAt: capturedAt,
                reviewState: reviewState,
                evidence: AtlasSignalCandidateEvidence(
                    resolutionStatus: nil,
                    candidateCount: nil,
                    confidence: nil,
                    resolver: nil,
                    playbackStatus: itemResult.playback.status,
                    playbackStartedAt: itemResult.playback.startedAt,
                    playbackEndedAt: itemResult.playback.endedAt,
                    playbackDurationSeconds: itemResult.playback.durationSeconds,
                    skipPolicy: itemResult.playback.status == .skipped ? "started_track_then_user_advanced" : nil,
                    reactionValue: nil,
                    reactionOperation: nil,
                    reactionLabel: nil,
                    selectedChip: nil,
                    selectedChips: nil,
                    shownUnselectedChips: nil,
                    noteText: nil,
                    reviewFlags: reviewFlags,
                    reviewNeeded: reviewNeeded
                )
            )
        ]

        if itemResult.playback.status == .skipped {
            candidates.append(
                candidate(
                    sessionID: sessionID,
                    exportID: exportID,
                    missionID: mission.missionID,
                    itemResult: itemResult,
                    subject: subject,
                    eventType: .skip,
                    occurredAt: itemResult.playback.endedAt ?? itemResult.playback.attemptedAt,
                    capturedAt: capturedAt,
                    reviewState: "needs_review",
                    evidence: AtlasSignalCandidateEvidence(
                        resolutionStatus: nil,
                        candidateCount: nil,
                        confidence: nil,
                        resolver: nil,
                        playbackStatus: itemResult.playback.status,
                        playbackStartedAt: itemResult.playback.startedAt,
                        playbackEndedAt: itemResult.playback.endedAt,
                        playbackDurationSeconds: itemResult.playback.durationSeconds,
                        skipPolicy: "started_track_then_user_advanced",
                        reactionValue: itemResult.reaction.reactionValue,
                        reactionOperation: itemResult.reaction.reactionValue.operation,
                        reactionLabel: ReactionDisplayConfiguration.current.label(for: itemResult.reaction.reactionValue),
                        selectedChip: nil,
                        selectedChips: selectedChips,
                        shownUnselectedChips: shownUnselectedChips,
                        noteText: nil,
                        reviewFlags: reviewFlags,
                        reviewNeeded: true
                    )
                )
            )
        }

        candidates.append(
            candidate(
                sessionID: sessionID,
                exportID: exportID,
                missionID: mission.missionID,
                itemResult: itemResult,
                subject: subject,
                eventType: .reaction,
                occurredAt: itemResult.reaction.reactedAt,
                capturedAt: capturedAt,
                reviewState: reviewState,
                evidence: AtlasSignalCandidateEvidence(
                    resolutionStatus: nil,
                    candidateCount: nil,
                    confidence: nil,
                    resolver: nil,
                    playbackStatus: itemResult.playback.status,
                    playbackStartedAt: nil,
                    playbackEndedAt: nil,
                    playbackDurationSeconds: nil,
                    skipPolicy: itemResult.playback.status == .skipped ? "started_track_then_user_advanced" : nil,
                    reactionValue: itemResult.reaction.reactionValue,
                    reactionOperation: itemResult.reaction.reactionValue.operation,
                    reactionLabel: ReactionDisplayConfiguration.current.label(for: itemResult.reaction.reactionValue),
                    selectedChip: nil,
                    selectedChips: selectedChips,
                    shownUnselectedChips: shownUnselectedChips,
                    noteText: nil,
                    reviewFlags: reviewFlags,
                    reviewNeeded: reviewNeeded
                )
            )
        )

        for selectedChip in selectedChips {
            candidates.append(
                candidate(
                    sessionID: sessionID,
                    exportID: exportID,
                    missionID: mission.missionID,
                    itemResult: itemResult,
                    subject: subject,
                    eventType: .chip,
                    occurredAt: itemResult.reaction.reactedAt,
                    capturedAt: capturedAt,
                    reviewState: reviewState,
                    suffix: selectedChip.tagID,
                    evidence: AtlasSignalCandidateEvidence(
                        resolutionStatus: nil,
                        candidateCount: nil,
                        confidence: nil,
                        resolver: nil,
                        playbackStatus: itemResult.playback.status,
                        playbackStartedAt: nil,
                        playbackEndedAt: nil,
                        playbackDurationSeconds: nil,
                        skipPolicy: itemResult.playback.status == .skipped ? "started_track_then_user_advanced" : nil,
                        reactionValue: itemResult.reaction.reactionValue,
                        reactionOperation: itemResult.reaction.reactionValue.operation,
                        reactionLabel: ReactionDisplayConfiguration.current.label(for: itemResult.reaction.reactionValue),
                        selectedChip: selectedChip,
                        selectedChips: selectedChips,
                        shownUnselectedChips: shownUnselectedChips,
                        noteText: nil,
                        reviewFlags: reviewFlags,
                        reviewNeeded: reviewNeeded
                    )
                )
            )
        }

        let trimmedNote = itemResult.reaction.notes.text.trimmingCharacters(in: .whitespacesAndNewlines)
        if !trimmedNote.isEmpty {
            candidates.append(
                candidate(
                    sessionID: sessionID,
                    exportID: exportID,
                    missionID: mission.missionID,
                    itemResult: itemResult,
                    subject: subject,
                    eventType: .note,
                    occurredAt: itemResult.reaction.reactedAt,
                    capturedAt: capturedAt,
                    reviewState: reviewState,
                    evidence: AtlasSignalCandidateEvidence(
                        resolutionStatus: nil,
                        candidateCount: nil,
                        confidence: nil,
                        resolver: nil,
                        playbackStatus: itemResult.playback.status,
                        playbackStartedAt: nil,
                        playbackEndedAt: nil,
                        playbackDurationSeconds: nil,
                        skipPolicy: itemResult.playback.status == .skipped ? "started_track_then_user_advanced" : nil,
                        reactionValue: itemResult.reaction.reactionValue,
                        reactionOperation: itemResult.reaction.reactionValue.operation,
                        reactionLabel: ReactionDisplayConfiguration.current.label(for: itemResult.reaction.reactionValue),
                        selectedChip: nil,
                        selectedChips: selectedChips,
                        shownUnselectedChips: shownUnselectedChips,
                        noteText: trimmedNote,
                        reviewFlags: reviewFlags,
                        reviewNeeded: reviewNeeded
                    )
                )
            )
        }

        candidates.append(
            candidate(
                sessionID: sessionID,
                exportID: exportID,
                missionID: mission.missionID,
                itemResult: itemResult,
                subject: subject,
                eventType: .review,
                occurredAt: itemResult.timestamps.updatedAt,
                capturedAt: capturedAt,
                reviewState: reviewState,
                evidence: AtlasSignalCandidateEvidence(
                    resolutionStatus: itemResult.resolution.status,
                    candidateCount: itemResult.resolution.candidateCount,
                    confidence: itemResult.resolution.confidence,
                    resolver: itemResult.resolution.resolver,
                    playbackStatus: itemResult.playback.status,
                    playbackStartedAt: itemResult.playback.startedAt,
                    playbackEndedAt: itemResult.playback.endedAt,
                    playbackDurationSeconds: itemResult.playback.durationSeconds,
                    skipPolicy: itemResult.playback.status == .skipped ? "started_track_then_user_advanced" : nil,
                    reactionValue: itemResult.reaction.reactionValue,
                    reactionOperation: itemResult.reaction.reactionValue.operation,
                    reactionLabel: ReactionDisplayConfiguration.current.label(for: itemResult.reaction.reactionValue),
                    selectedChip: nil,
                    selectedChips: selectedChips,
                    shownUnselectedChips: shownUnselectedChips,
                    noteText: trimmedNote.isEmpty ? nil : trimmedNote,
                    reviewFlags: reviewFlags,
                    reviewNeeded: reviewNeeded
                )
            )
        )

        return candidates
    }

    private static func candidate(
        sessionID: String,
        exportID: String,
        missionID: String,
        itemResult: ItemResult,
        subject: AtlasSignalCandidateSubject,
        eventType: AtlasSignalCandidateEventType,
        occurredAt: Date?,
        capturedAt: Date,
        reviewState: String,
        suffix: String? = nil,
        evidence: AtlasSignalCandidateEvidence
    ) -> AtlasSignalCandidate {
        AtlasSignalCandidate(
            candidateID: makeCandidateID(
                sessionID: sessionID,
                missionItemID: itemResult.missionItemID,
                eventType: eventType,
                suffix: suffix
            ),
            source: "mission_review",
            eventType: eventType,
            occurredAt: occurredAt,
            capturedAt: capturedAt,
            missionID: missionID,
            missionItemID: itemResult.missionItemID,
            exportID: exportID,
            subjectMusicObjectRef: subject,
            evidence: evidence,
            reviewState: reviewState,
            promotionState: "not_promoted",
            writesAtlasTruth: false
        )
    }

    private static func makeSubject(from itemResult: ItemResult) -> AtlasSignalCandidateSubject {
        AtlasSignalCandidateSubject(
            objectType: itemResult.itemType == .track ? "song_recording" : "album",
            refSource: itemResult.resolution.catalogID == nil ? "mission_item" : "apple_music_catalog",
            missionItemID: itemResult.missionItemID,
            itemType: itemResult.itemType,
            catalogID: itemResult.resolution.catalogID,
            catalogURL: itemResult.resolution.catalogURL,
            artworkURL: itemResult.resolution.artworkURL,
            displayName: itemResult.resolution.resolvedTitle ?? itemResult.title,
            creditedArtistName: itemResult.resolution.resolvedArtist ?? itemResult.artist,
            albumName: itemResult.resolution.resolvedAlbum ?? itemResult.album,
            resolutionState: itemResult.resolution.status,
            resolver: itemResult.resolution.resolver,
            storefront: itemResult.resolution.storefront
        )
    }

    private static func makeSelectedChips(from reaction: ReactionRecord) -> [AtlasSignalCandidateChip] {
        reaction.selectedTags?.map {
            AtlasSignalCandidateChip(
                tagID: $0.tagID,
                label: $0.label,
                primaryReactionValue: $0.primaryReactionValue,
                description: $0.description
            )
        } ?? []
    }

    private static func makeShownUnselectedChips(
        item: MissionItem,
        reaction: ReactionRecord,
        selectedChips: [AtlasSignalCandidateChip]
    ) -> [AtlasSignalCandidateChip] {
        let selectedIDs = Set(selectedChips.map(\.tagID))
        return item.feedbackChips(for: reaction.reactionValue)
            .filter { !selectedIDs.contains($0.tagID) }
            .map {
                AtlasSignalCandidateChip(
                    tagID: $0.tagID,
                    label: $0.label,
                    primaryReactionValue: reaction.reactionValue,
                    description: $0.description
                )
            }
    }

    private static func makeReviewFlags(from itemResult: ItemResult) -> [String] {
        var flags: [String] = []

        if itemResult.resolution.status != .resolved {
            flags.append("needs_resolution")
        }

        if itemResult.playback.status == .failed {
            flags.append("playback_failed")
        }

        if itemResult.playback.status == .skipped, itemResult.reaction.reactionValue == .unresolved {
            flags.append("skipped_no_signal")
        } else if itemResult.playback.hasExportablePlaybackEvidence, itemResult.reaction.reactionValue == .unresolved {
            flags.append("no_signal")
        }

        return flags
    }

    private static func makeCandidateID(
        sessionID: String,
        missionItemID: String,
        eventType: AtlasSignalCandidateEventType,
        suffix: String?
    ) -> String {
        let parts = ["SIGC", sessionID, missionItemID, eventType.rawValue, suffix]
            .compactMap { $0 }
            .map(normalizedIdentifier)
        return parts.joined(separator: "_")
    }

    private static func normalizedIdentifier(_ value: String) -> String {
        let allowed = CharacterSet.alphanumerics
        var result = ""

        for scalar in value.uppercased().unicodeScalars {
            result.append(allowed.contains(scalar) ? Character(scalar) : "_")
        }

        while result.contains("__") {
            result = result.replacingOccurrences(of: "__", with: "_")
        }

        return result.trimmingCharacters(in: CharacterSet(charactersIn: "_"))
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

    static func renderDevelopmentStub(
        mission: Mission,
        itemResults: [ItemResult],
        atlasSignalCandidateBundle: AtlasSignalCandidateBundle? = nil,
        exportedAt: Date
    ) -> String {
        """
        # Cartenza Discovery Log

        - Mission: \(mission.missionTitle)
        - Mission ID: \(mission.missionID)
        - Export type: development stub
        - Exported at: \(ISO8601DateFormatter().string(from: exportedAt))
        - Reconciliation status: not_reconciled

        ## Acceptance Notice

        This is a development/stub export. Resolver and playback are simulated, `device_context.is_physical_device` is false, and this file does not count as physical-device acceptance evidence.

        ## Items Tested

        \(Self.renderItemResults(itemResults))

        \(Self.renderAtlasSignalCandidateNotice(atlasSignalCandidateBundle))

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
        atlasSignalCandidateBundle: AtlasSignalCandidateBundle? = nil,
        deviceContext: DeviceContext,
        exportedAt: Date
    ) -> String {
        """
        # Cartenza Discovery Log

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

        \(Self.renderAtlasSignalCandidateNotice(atlasSignalCandidateBundle))

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

    private static func renderAtlasSignalCandidateNotice(_ bundle: AtlasSignalCandidateBundle?) -> String {
        guard let bundle else {
            return ""
        }

        return """
        ## Atlas Signal Candidates

        - Candidate bundle schema: \(bundle.schemaVersion)
        - Candidate count: \(bundle.candidates.count)
        - Candidate status: \(bundle.candidateStatus)
        - Writes Atlas truth: \(bundle.writesAtlasTruth ? "true" : "false")

        These records are ingestion candidates only. They preserve playback, reaction, chip, skip, note, resolution, and review evidence for a later Atlas lane review, but they do not update Atlas truth or canonical graph state.
        """
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
