import Foundation

enum MissionAssignmentSource: String, Codable, CaseIterable {
    case generatedReviewed = "generated_reviewed"
    case manualReviewed = "manual_reviewed"
    case localAlphaFixture = "local_alpha_fixture"

    var displayName: String {
        switch self {
        case .generatedReviewed:
            return "Generated"
        case .manualReviewed:
            return "Manual"
        case .localAlphaFixture:
            return "Local Fixture"
        }
    }
}

struct SupabaseMissionClientConfig: Codable, Equatable {
    let projectURL: URL?
    let anonKey: String?
    let generateFirstMissionBatchFunctionName: String

    static let unconfigured = SupabaseMissionClientConfig(
        projectURL: nil,
        anonKey: nil,
        generateFirstMissionBatchFunctionName: "generate-first-mission-batch"
    )

    var isConfiguredForRemoteCalls: Bool {
        projectURL != nil && anonKey?.isEmpty == false
    }

    enum CodingKeys: String, CodingKey {
        case projectURL = "project_url"
        case anonKey = "anon_key"
        case generateFirstMissionBatchFunctionName = "generate_first_mission_batch_function_name"
    }
}

struct SupabaseAlphaConfig: Equatable {
    let projectURL: URL?
    let anonKey: String?
    let generateFirstMissionBatchFunctionName: String
    let submitAlphaEvidenceFunctionName: String
    let submitAlphaDiagnosticFunctionName: String
    let testerAlias: String

    static let unconfigured = SupabaseAlphaConfig(
        projectURL: nil,
        anonKey: nil,
        generateFirstMissionBatchFunctionName: "generate-first-mission-batch",
        submitAlphaEvidenceFunctionName: "submit-alpha-evidence",
        submitAlphaDiagnosticFunctionName: "submit-alpha-diagnostic",
        testerAlias: "trusted-alpha-001"
    )

    static func fromBundle(_ bundle: Bundle = .main) -> SupabaseAlphaConfig {
        let info = bundle.infoDictionary ?? [:]
        let projectURL = configuredInfoString(
            info,
            cartenzaKey: "CartenzaSupabaseProjectURL",
            legacyKey: "WaymarkSupabaseProjectURL"
        )
            .flatMap(URL.init(string:))
        let anonKey = configuredInfoString(
            info,
            cartenzaKey: "CartenzaSupabaseAnonKey",
            legacyKey: "WaymarkSupabaseAnonKey"
        )
        let generateFunctionName = configuredInfoString(
            info,
            cartenzaKey: "CartenzaSupabaseGenerateFunctionName",
            legacyKey: "WaymarkSupabaseGenerateFunctionName"
        )
            ?? "generate-first-mission-batch"
        let evidenceFunctionName = configuredInfoString(
            info,
            cartenzaKey: "CartenzaSupabaseEvidenceFunctionName",
            legacyKey: "WaymarkSupabaseEvidenceFunctionName"
        )
            ?? "submit-alpha-evidence"
        let diagnosticFunctionName = configuredInfoString(
            info,
            cartenzaKey: "CartenzaSupabaseDiagnosticFunctionName",
            legacyKey: "WaymarkSupabaseDiagnosticFunctionName"
        )
            ?? "submit-alpha-diagnostic"
        let testerAlias = configuredInfoString(
            info,
            cartenzaKey: "CartenzaSupabaseTesterAlias",
            legacyKey: "WaymarkSupabaseTesterAlias"
        )
            ?? "trusted-alpha-001"

        return SupabaseAlphaConfig(
            projectURL: projectURL,
            anonKey: anonKey,
            generateFirstMissionBatchFunctionName: generateFunctionName,
            submitAlphaEvidenceFunctionName: evidenceFunctionName,
            submitAlphaDiagnosticFunctionName: diagnosticFunctionName,
            testerAlias: testerAlias
        )
    }

    var isConfiguredForRemoteCalls: Bool {
        projectURL != nil && anonKey?.isEmpty == false
    }

    private static func configuredInfoString(
        _ info: [String: Any],
        cartenzaKey: String,
        legacyKey: String
    ) -> String? {
        sanitizedInfoString(info[cartenzaKey]) ?? sanitizedInfoString(info[legacyKey])
    }

    private static func sanitizedInfoString(_ rawValue: Any?) -> String? {
        guard let value = rawValue as? String else {
            return nil
        }

        let trimmed = value.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty, !trimmed.contains("$(") else {
            return nil
        }

        return trimmed
    }
}

struct MissionGenerationPromptContext: Codable, Equatable {
    let alphaScope: String
    let generationMode: String
    let sourceAppVersion: String
    let sourceAppBuild: String
    let storefront: String
    let surveyPageCount: SurveyPageCount
    let batchMissionIndex: Int?
    let batchMissionTotal: Int?
    let batchSeed: String?
    let diversityDirective: String?
    let missionPortfolioSlot: String?
    let missionArchetype: String?
    let missionObjective: String?
    let missionRequestID: String?
    let sourceCandidatePoolID: String?
    let alreadySelectedRouteItemIDs: [String]
    let alreadySelectedRouteDisplayIdentityKeys: [String]
    let alreadySelectedDisplayKeys: [String]
    let batchMemoryDirective: String?

    init(
        alphaScope: String,
        generationMode: String,
        sourceAppVersion: String,
        sourceAppBuild: String,
        storefront: String,
        surveyPageCount: SurveyPageCount,
        batchMissionIndex: Int? = nil,
        batchMissionTotal: Int? = nil,
        batchSeed: String? = nil,
        diversityDirective: String? = nil,
        missionPortfolioSlot: String? = nil,
        missionArchetype: String? = nil,
        missionObjective: String? = nil,
        missionRequestID: String? = nil,
        sourceCandidatePoolID: String? = nil,
        alreadySelectedRouteItemIDs: [String] = [],
        alreadySelectedRouteDisplayIdentityKeys: [String] = [],
        alreadySelectedDisplayKeys: [String]? = nil,
        batchMemoryDirective: String? = nil
    ) {
        self.alphaScope = alphaScope
        self.generationMode = generationMode
        self.sourceAppVersion = sourceAppVersion
        self.sourceAppBuild = sourceAppBuild
        self.storefront = storefront
        self.surveyPageCount = surveyPageCount
        self.batchMissionIndex = batchMissionIndex
        self.batchMissionTotal = batchMissionTotal
        self.batchSeed = batchSeed
        self.diversityDirective = diversityDirective
        self.missionPortfolioSlot = missionPortfolioSlot
        self.missionArchetype = missionArchetype
        self.missionObjective = missionObjective
        self.missionRequestID = missionRequestID
        self.sourceCandidatePoolID = sourceCandidatePoolID
        self.alreadySelectedRouteItemIDs = alreadySelectedRouteItemIDs
        self.alreadySelectedRouteDisplayIdentityKeys = alreadySelectedRouteDisplayIdentityKeys
        self.alreadySelectedDisplayKeys = alreadySelectedDisplayKeys ?? alreadySelectedRouteDisplayIdentityKeys
        self.batchMemoryDirective = batchMemoryDirective
    }

    enum CodingKeys: String, CodingKey {
        case alphaScope = "alpha_scope"
        case generationMode = "generation_mode"
        case sourceAppVersion = "source_app_version"
        case sourceAppBuild = "source_app_build"
        case storefront
        case surveyPageCount = "survey_page_count"
        case batchMissionIndex = "batch_mission_index"
        case batchMissionTotal = "batch_mission_total"
        case batchSeed = "batch_seed"
        case diversityDirective = "diversity_directive"
        case missionPortfolioSlot = "mission_portfolio_slot"
        case missionArchetype = "mission_archetype"
        case missionObjective = "mission_objective"
        case missionRequestID = "mission_request_id"
        case sourceCandidatePoolID = "source_candidate_pool_id"
        case alreadySelectedRouteItemIDs = "already_selected_route_item_ids"
        case alreadySelectedRouteDisplayIdentityKeys = "already_selected_route_display_identity_keys"
        case alreadySelectedDisplayKeys = "already_selected_display_keys"
        case batchMemoryDirective = "batch_memory_directive"
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        alphaScope = try container.decode(String.self, forKey: .alphaScope)
        generationMode = try container.decode(String.self, forKey: .generationMode)
        sourceAppVersion = try container.decode(String.self, forKey: .sourceAppVersion)
        sourceAppBuild = try container.decode(String.self, forKey: .sourceAppBuild)
        storefront = try container.decode(String.self, forKey: .storefront)
        surveyPageCount = try container.decode(SurveyPageCount.self, forKey: .surveyPageCount)
        batchMissionIndex = try container.decodeIfPresent(Int.self, forKey: .batchMissionIndex)
        batchMissionTotal = try container.decodeIfPresent(Int.self, forKey: .batchMissionTotal)
        batchSeed = try container.decodeIfPresent(String.self, forKey: .batchSeed)
        diversityDirective = try container.decodeIfPresent(String.self, forKey: .diversityDirective)
        missionPortfolioSlot = try container.decodeIfPresent(String.self, forKey: .missionPortfolioSlot)
        missionArchetype = try container.decodeIfPresent(String.self, forKey: .missionArchetype)
        missionObjective = try container.decodeIfPresent(String.self, forKey: .missionObjective)
        missionRequestID = try container.decodeIfPresent(String.self, forKey: .missionRequestID)
        sourceCandidatePoolID = try container.decodeIfPresent(String.self, forKey: .sourceCandidatePoolID)
        alreadySelectedRouteItemIDs = try container.decodeIfPresent([String].self, forKey: .alreadySelectedRouteItemIDs) ?? []
        alreadySelectedRouteDisplayIdentityKeys = try container.decodeIfPresent([String].self, forKey: .alreadySelectedRouteDisplayIdentityKeys) ?? []
        alreadySelectedDisplayKeys = try container.decodeIfPresent([String].self, forKey: .alreadySelectedDisplayKeys)
            ?? alreadySelectedRouteDisplayIdentityKeys
        batchMemoryDirective = try container.decodeIfPresent(String.self, forKey: .batchMemoryDirective)
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(alphaScope, forKey: .alphaScope)
        try container.encode(generationMode, forKey: .generationMode)
        try container.encode(sourceAppVersion, forKey: .sourceAppVersion)
        try container.encode(sourceAppBuild, forKey: .sourceAppBuild)
        try container.encode(storefront, forKey: .storefront)
        try container.encode(surveyPageCount, forKey: .surveyPageCount)
        try container.encodeIfPresent(batchMissionIndex, forKey: .batchMissionIndex)
        try container.encodeIfPresent(batchMissionTotal, forKey: .batchMissionTotal)
        try container.encodeIfPresent(batchSeed, forKey: .batchSeed)
        try container.encodeIfPresent(diversityDirective, forKey: .diversityDirective)
        try container.encodeIfPresent(missionPortfolioSlot, forKey: .missionPortfolioSlot)
        try container.encodeIfPresent(missionArchetype, forKey: .missionArchetype)
        try container.encodeIfPresent(missionObjective, forKey: .missionObjective)
        try container.encodeIfPresent(missionRequestID, forKey: .missionRequestID)
        try container.encodeIfPresent(sourceCandidatePoolID, forKey: .sourceCandidatePoolID)
        try container.encode(alreadySelectedRouteItemIDs, forKey: .alreadySelectedRouteItemIDs)
        try container.encode(alreadySelectedRouteDisplayIdentityKeys, forKey: .alreadySelectedRouteDisplayIdentityKeys)
        try container.encode(alreadySelectedDisplayKeys, forKey: .alreadySelectedDisplayKeys)
        try container.encodeIfPresent(batchMemoryDirective, forKey: .batchMemoryDirective)
    }
}

struct SurveyPageCount: Codable, Equatable {
    let artist: Int
    let album: Int
    let song: Int
}

struct MissionGenerationRequest: Equatable {
    let clientRequestID: String
    let testerAlias: String
    let requestedBatchSize: Int
    let surveyEvidenceExport: Data
    let missionGenerationDigestView: Data
    let candidatePool: Data
    let promptContext: MissionGenerationPromptContext
    let alreadySelectedRouteItemIDs: [String]
    let alreadySelectedRouteDisplayIdentityKeys: [String]

    init(
        clientRequestID: String,
        testerAlias: String,
        requestedBatchSize: Int,
        surveyEvidenceExport: Data,
        missionGenerationDigestView: Data,
        candidatePool: Data,
        promptContext: MissionGenerationPromptContext,
        alreadySelectedRouteItemIDs: [String] = [],
        alreadySelectedRouteDisplayIdentityKeys: [String] = []
    ) {
        self.clientRequestID = clientRequestID
        self.testerAlias = testerAlias
        self.requestedBatchSize = requestedBatchSize
        self.surveyEvidenceExport = surveyEvidenceExport
        self.missionGenerationDigestView = missionGenerationDigestView
        self.candidatePool = candidatePool
        self.promptContext = promptContext
        self.alreadySelectedRouteItemIDs = alreadySelectedRouteItemIDs
        self.alreadySelectedRouteDisplayIdentityKeys = alreadySelectedRouteDisplayIdentityKeys
    }
}

protocol MissionGenerationClient {
    func generateFirstMissionBatch(request: MissionGenerationRequest, accessToken: String) async throws -> Data
}

struct LocalSupabaseMissionClientStub: MissionGenerationClient {
    let responseData: Data

    func generateFirstMissionBatch(request: MissionGenerationRequest, accessToken: String) async throws -> Data {
        responseData
    }
}

struct LiveSupabaseMissionGenerationClient: MissionGenerationClient {
    let config: SupabaseAlphaConfig
    var urlSession: URLSession = Self.defaultGenerationURLSession

    private static let defaultGenerationURLSession: URLSession = {
        let configuration = URLSessionConfiguration.default
        configuration.timeoutIntervalForRequest = 180
        configuration.timeoutIntervalForResource = 240
        return URLSession(configuration: configuration)
    }()

    func generateFirstMissionBatch(request: MissionGenerationRequest, accessToken: String) async throws -> Data {
        let urlRequest = try makeURLRequest(request: request, accessToken: accessToken)
        let (data, response) = try await urlSession.data(for: urlRequest)
        try SupabaseHTTP.validate(response: response, data: data)
        return data
    }

    func makeURLRequest(request: MissionGenerationRequest, accessToken: String) throws -> URLRequest {
        guard let projectURL = config.projectURL,
              let anonKey = config.anonKey,
              !anonKey.isEmpty else {
            throw SupabaseClientError.missingConfiguration
        }

        let url = projectURL
            .appendingPathComponent("functions")
            .appendingPathComponent("v1")
            .appendingPathComponent(config.generateFirstMissionBatchFunctionName)

        let payload: [String: Any] = [
            "client_request_id": request.clientRequestID,
            "tester_alias": request.testerAlias,
            "requested_batch_size": request.requestedBatchSize,
            "survey_evidence_export": try SupabaseJSON.object(from: request.surveyEvidenceExport),
            "mission_generation_digest_view": try SupabaseJSON.object(from: request.missionGenerationDigestView),
            "candidate_pool": try SupabaseJSON.object(from: request.candidatePool),
            "prompt_context": try SupabaseJSON.object(from: request.promptContext),
            "already_selected_route_item_ids": request.alreadySelectedRouteItemIDs,
            "already_selected_route_display_identity_keys": request.alreadySelectedRouteDisplayIdentityKeys,
            "already_selected_display_keys": request.alreadySelectedRouteDisplayIdentityKeys
        ]

        var urlRequest = URLRequest(url: url)
        urlRequest.timeoutInterval = 180
        urlRequest.httpMethod = "POST"
        urlRequest.setValue(anonKey, forHTTPHeaderField: "apikey")
        urlRequest.setValue("Bearer \(accessToken)", forHTTPHeaderField: "Authorization")
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.httpBody = try JSONSerialization.data(withJSONObject: payload, options: [.sortedKeys])
        return urlRequest
    }
}

enum SupabaseClientError: LocalizedError, Equatable {
    case missingConfiguration
    case invalidJSONPayload
    case invalidHTTPResponse
    case httpFailure(statusCode: Int, body: String)
    case missingIdentityToken
    case missingAppleCredential
    case missingNonce
    case keychainFailure(String)

    var errorDescription: String? {
        switch self {
        case .missingConfiguration:
            return "Supabase project URL or publishable key is not configured for this build."
        case .invalidJSONPayload:
            return "Supabase request payload could not be encoded as a JSON object."
        case .invalidHTTPResponse:
            return "Supabase returned an invalid HTTP response."
        case .httpFailure(let statusCode, let body):
            return "Supabase request failed with HTTP \(statusCode): \(body)"
        case .missingIdentityToken:
            return "Apple did not return an identity token for Supabase sign-in."
        case .missingAppleCredential:
            return "Apple sign-in did not return an Apple ID credential."
        case .missingNonce:
            return "Apple sign-in nonce was missing. Try signing in again."
        case .keychainFailure(let detail):
            return "Could not persist Supabase session in Keychain: \(detail)"
        }
    }
}

enum SupabaseHTTP {
    static func validate(response: URLResponse, data: Data) throws {
        guard let httpResponse = response as? HTTPURLResponse else {
            throw SupabaseClientError.invalidHTTPResponse
        }

        guard (200..<300).contains(httpResponse.statusCode) else {
            let body = String(data: data, encoding: .utf8) ?? "<binary response>"
            throw SupabaseClientError.httpFailure(statusCode: httpResponse.statusCode, body: body)
        }
    }
}

enum SupabaseJSON {
    static func object(from data: Data) throws -> Any {
        let object = try JSONSerialization.jsonObject(with: data)
        guard JSONSerialization.isValidJSONObject(object) else {
            throw SupabaseClientError.invalidJSONPayload
        }
        return object
    }

    static func object<T: Encodable>(from value: T) throws -> Any {
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        return try object(from: encoder.encode(value))
    }
}

struct MissionAssignment: Codable, Identifiable {
    let mission: Mission
    let source: MissionAssignmentSource
    let importedAt: Date
    let sourceRunID: String?
    let importNote: String?

    var id: String {
        mission.missionID
    }
}

struct MissionCatalog {
    let reviewedAssignments: [MissionAssignment]

    static let empty = MissionCatalog(reviewedAssignments: [])

    var allAssignments: [MissionAssignment] {
        reviewedAssignments
    }

    var allMissions: [Mission] {
        allAssignments.map(\.mission)
    }

    func assignment(for missionID: String) -> MissionAssignment? {
        allAssignments.first { $0.mission.missionID == missionID }
    }
}

protocol MissionProviding {
    func loadMissionCatalog() throws -> MissionCatalog
    @discardableResult
    func importReviewedMissionData(_ data: Data, source: MissionAssignmentSource, importedAt: Date) throws -> [MissionAssignment]
    @discardableResult
    func importAlphaAppImportCandidateData(_ data: Data, importedAt: Date) throws -> [MissionAssignment]
    @discardableResult
    func importSupabaseMissionBatchResponseData(
        _ data: Data,
        importedAt: Date,
        excludingRouteItemIDs: Set<String>,
        excludingRouteDisplayIdentityKeys: Set<String>
    ) throws -> [MissionAssignment]
    func resetReviewedAssignments() throws
}

extension MissionProviding {
    @discardableResult
    func importSupabaseMissionBatchResponseData(_ data: Data, importedAt: Date = Date()) throws -> [MissionAssignment] {
        try importSupabaseMissionBatchResponseData(
            data,
            importedAt: importedAt,
            excludingRouteItemIDs: [],
            excludingRouteDisplayIdentityKeys: []
        )
    }
}

struct ReviewedMissionStore {
    private let fileManager: FileManager
    private let baseDirectoryURL: URL?
    private let isEnabled: Bool
    private let filename = "waymark_reviewed_missions_v0_1.json"

    init(
        fileManager: FileManager = .default,
        baseDirectoryURL: URL? = nil,
        isEnabled: Bool = true
    ) {
        self.fileManager = fileManager
        self.baseDirectoryURL = baseDirectoryURL
        self.isEnabled = isEnabled
    }

    static let disabled = ReviewedMissionStore(isEnabled: false)

    func load() -> [MissionAssignment] {
        guard isEnabled else {
            return []
        }

        do {
            let url = try storeURL()
            guard fileManager.fileExists(atPath: url.path) else {
                return []
            }

            let data = try Data(contentsOf: url)
            let decoder = JSONDecoder()
            decoder.dateDecodingStrategy = .iso8601
            return try decoder.decode([MissionAssignment].self, from: data)
        } catch {
            return []
        }
    }

    func save(_ assignments: [MissionAssignment]) throws {
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
        let data = try encoder.encode(assignments)
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

enum MissionImportError: LocalizedError, Equatable {
    case invalidJSON
    case emptyImport
    case blockedStatus(String)
    case missingAppMissions
    case invalidMission(String)

    var errorDescription: String? {
        switch self {
        case .invalidJSON:
            return "The imported mission payload is not valid JSON for a reviewed mission."
        case .emptyImport:
            return "The import payload did not contain any missions."
        case .blockedStatus(let status):
            return "Mission generation returned \(status). Only app_import_candidate or Alpha review-gated app-valid missions can be imported."
        case .missingAppMissions:
            return "The generation response did not include app-import-ready missions."
        case .invalidMission(let reason):
            return "Mission import failed: \(reason)"
        }
    }
}

private struct SupabaseMissionBatchResponse: Decodable {
    let runID: String?
    let status: String
    let appMissions: [Mission]

    enum CodingKeys: String, CodingKey {
        case runID = "run_id"
        case status
        case appMissions = "app_missions"
    }
}

struct MissionImportGate {
    static func validateAppImportCandidate(_ mission: Mission) throws {
        guard mission.schemaVersion == "mission.v0.2" else {
            throw MissionImportError.invalidMission("schema_version must be mission.v0.2.")
        }

        guard mission.missionID.range(of: #"^MIS_[A-Z0-9_]+$"#, options: .regularExpression) != nil else {
            throw MissionImportError.invalidMission("mission_id must match MIS_[A-Z0-9_]+.")
        }

        guard !mission.items.isEmpty else {
            throw MissionImportError.invalidMission("mission must include at least one route item.")
        }

        var seenItemIDs = Set<String>()
        var seenDisplayIdentityKeys = Set<String>()
        for item in mission.items {
            guard item.itemID.range(of: #"^ITEM_[A-Z0-9_]+$"#, options: .regularExpression) != nil else {
                throw MissionImportError.invalidMission("\(item.title) has an invalid item_id.")
            }

            guard seenItemIDs.insert(item.itemID).inserted else {
                throw MissionImportError.invalidMission("duplicate item_id \(item.itemID).")
            }

            let displayIdentityKey = routeDisplayIdentityKey(for: item)
            guard seenDisplayIdentityKeys.insert(displayIdentityKey).inserted else {
                throw MissionImportError.invalidMission("duplicate display identity \(displayIdentityKey).")
            }

            if mission.alphaAppImportStatus == .appImportReady {
                let resolution = item.appleMusicResolution
                guard resolution.status == .resolved &&
                    (resolution.catalogID?.isEmpty == false || resolution.catalogURL != nil) else {
                    throw MissionImportError.invalidMission("\(item.title) must be resolved with Apple Music playback metadata for app_import_ready import.")
                }
            } else {
                guard item.appleMusicResolution.status.canEnterMusicResolutionStaging else {
                    throw MissionImportError.invalidMission("\(item.title) must enter the app unresolved or as a local fixture candidate so MusicKit resolution evidence is captured in-app.")
                }
            }

            guard !item.artist.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty,
                  !item.title.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
                throw MissionImportError.invalidMission("every route item must have artist and title.")
            }

            guard item.expectedTestSignal?.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty == false else {
                throw MissionImportError.invalidMission("\(item.title) must include expected_test_signal.")
            }

            guard item.playerCard?.flipSide?.songHypothesis?.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty == false else {
                throw MissionImportError.invalidMission("\(item.title) must include player_card.flip_side.song_hypothesis.")
            }

            for reactionValue in ReactionValue.primarySignalValues {
                guard !item.feedbackChips(for: reactionValue).isEmpty else {
                    throw MissionImportError.invalidMission("\(item.title) is missing feedback chips for \(reactionValue.rawValue).")
                }
            }
        }
    }

    static func routeItemIDs(in mission: Mission) -> Set<String> {
        Set(mission.items.map(\.itemID))
    }

    static func routeDisplayIdentityKeys(in mission: Mission) -> Set<String> {
        Set(mission.items.map(routeDisplayIdentityKey(for:)))
    }

    static func routeItemIDs(in assignments: [MissionAssignment]) -> Set<String> {
        Set(assignments.flatMap { $0.mission.items.map(\.itemID) })
    }

    static func routeDisplayIdentityKeys(in assignments: [MissionAssignment]) -> Set<String> {
        Set(assignments.flatMap { $0.mission.items.map(routeDisplayIdentityKey(for:)) })
    }

    static func routeCandidateIDs(in assignments: [MissionAssignment]) -> Set<String> {
        Set(assignments.flatMap { assignment in
            assignment.mission.items.compactMap { normalizedOptionalIdentity($0.candidateID) }
        })
    }

    static func routeIdentityMetadata(in assignments: [MissionAssignment]) -> [[String: String]] {
        assignments.flatMap { assignment in
            assignment.mission.items.map { item in
                var output: [String: String] = [
                    "mission_id": assignment.mission.missionID,
                    "item_id": item.itemID,
                    "route_display_identity_key": routeDisplayIdentityKey(for: item)
                ]
                output["candidate_id"] = normalizedOptionalIdentity(item.candidateID)
                output["route_candidate_key"] = normalizedOptionalIdentity(item.routeCandidateKey)
                output["route_batch_dedupe_key"] = normalizedOptionalIdentity(item.routeBatchDedupeKey)
                return output
            }
        }
    }

    static func routeDisplayIdentityKey(for item: MissionItem) -> String {
        if let routeDisplayIdentityKey = normalizedOptionalIdentity(item.routeDisplayIdentityKey) {
            return routeDisplayIdentityKey
        }

        return [
            item.itemType.rawValue,
            normalizedRouteIdentityComponent(item.artist),
            normalizedRouteIdentityComponent(item.title)
        ]
        .filter { !$0.isEmpty }
        .joined(separator: "::")
    }

    static func validateNoRouteOverlap(
        missions: [Mission],
        excludingRouteItemIDs existingItemIDs: Set<String>,
        excludingRouteDisplayIdentityKeys existingDisplayIdentityKeys: Set<String>
    ) throws {
        var seenItemIDs = existingItemIDs
        var seenDisplayIdentityKeys = existingDisplayIdentityKeys

        for mission in missions {
            for item in mission.items {
                guard seenItemIDs.insert(item.itemID).inserted else {
                    throw MissionImportError.invalidMission("route item \(item.itemID) already exists in the Alpha mission batch.")
                }

                let displayIdentityKey = routeDisplayIdentityKey(for: item)
                guard seenDisplayIdentityKeys.insert(displayIdentityKey).inserted else {
                    throw MissionImportError.invalidMission("route item display identity \(displayIdentityKey) already exists in the Alpha mission batch.")
                }
            }
        }
    }

    private static func normalizedRouteIdentityComponent(_ rawValue: String) -> String {
        rawValue
            .folding(options: [.caseInsensitive, .diacriticInsensitive], locale: Locale(identifier: "en_US_POSIX"))
            .components(separatedBy: CharacterSet.alphanumerics.inverted)
            .filter { !$0.isEmpty }
            .joined(separator: "-")
    }

    private static func normalizedOptionalIdentity(_ rawValue: String?) -> String? {
        let trimmed = rawValue?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        return trimmed.isEmpty ? nil : trimmed
    }
}

struct LocalMissionProvider: MissionProviding {
    private let reviewedMissionStore: ReviewedMissionStore

    init(
        reviewedMissionStore: ReviewedMissionStore = ReviewedMissionStore()
    ) {
        self.reviewedMissionStore = reviewedMissionStore
    }

    func loadMissionCatalog() throws -> MissionCatalog {
        let reviewedAssignments = reviewedMissionStore.load()

        return MissionCatalog(
            reviewedAssignments: reviewedAssignments
        )
    }

    @discardableResult
    func importReviewedMissionData(_ data: Data, source: MissionAssignmentSource, importedAt: Date = Date()) throws -> [MissionAssignment] {
        let missions = try decodeMissionImportPayload(data)
        guard !missions.isEmpty else {
            throw MissionImportError.emptyImport
        }

        let assignments = try missions.map { mission in
            try MissionImportGate.validateAppImportCandidate(mission)
            return MissionAssignment(
                mission: mission,
                source: source,
                importedAt: importedAt,
                sourceRunID: nil,
                importNote: "Reviewed mission import"
            )
        }

        try mergeReviewedAssignments(assignments)
        return assignments
    }

    @discardableResult
    func importAlphaAppImportCandidateData(_ data: Data, importedAt: Date = Date()) throws -> [MissionAssignment] {
        let payloads: [AlphaAppImportMissionPayloadV0_2]
        do {
            payloads = try AlphaAppImportAdapter.decodeImportablePayloads(from: data)
        } catch {
            throw MissionImportError.invalidJSON
        }

        guard !payloads.isEmpty else {
            throw MissionImportError.emptyImport
        }

        let missions = try payloads.map(AlphaAppImportAdapter.makeMission)
        for mission in missions {
            try MissionImportGate.validateAppImportCandidate(mission)
        }

        let assignments = missions.map { mission in
            MissionAssignment(
                mission: mission,
                source: .localAlphaFixture,
                importedAt: importedAt,
                sourceRunID: "alpha_mission_delivery_v0_2",
                importNote: mission.alphaAppImportStatus == .appImportReady
                    ? "Imported from resolved Alpha app_import_ready UAT fixture for physical playback smoke."
                    : "Imported from approved Alpha app_import_candidate golden fixture for local MusicKit resolution staging."
            )
        }

        try mergeReviewedAssignments(assignments)
        return assignments
    }

    @discardableResult
    func importSupabaseMissionBatchResponseData(
        _ data: Data,
        importedAt: Date = Date(),
        excludingRouteItemIDs: Set<String> = [],
        excludingRouteDisplayIdentityKeys: Set<String> = []
    ) throws -> [MissionAssignment] {
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let response: SupabaseMissionBatchResponse
        do {
            response = try decoder.decode(SupabaseMissionBatchResponse.self, from: data)
        } catch {
            throw MissionImportError.invalidJSON
        }

        guard response.status == "app_import_candidate" || response.status == "review_needed" else {
            throw MissionImportError.blockedStatus(response.status)
        }

        guard !response.appMissions.isEmpty else {
            throw MissionImportError.missingAppMissions
        }

        for mission in response.appMissions {
            try MissionImportGate.validateAppImportCandidate(mission)
        }

        try MissionImportGate.validateNoRouteOverlap(
            missions: response.appMissions,
            excludingRouteItemIDs: excludingRouteItemIDs,
            excludingRouteDisplayIdentityKeys: excludingRouteDisplayIdentityKeys
        )

        let assignments = response.appMissions.map { mission in
            return MissionAssignment(
                mission: mission,
                source: .generatedReviewed,
                importedAt: importedAt,
                sourceRunID: response.runID,
                importNote: response.status == "review_needed"
                    ? "Imported from review_needed generation response after local app validation for trusted Alpha."
                    : "Imported from app_import_candidate generation response"
            )
        }

        try mergeReviewedAssignments(assignments)
        return assignments
    }

    func resetReviewedAssignments() throws {
        try reviewedMissionStore.reset()
    }

    private func decodeMissionImportPayload(_ data: Data) throws -> [Mission] {
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601

        if let missions = try? decoder.decode([Mission].self, from: data) {
            return missions
        }

        if let mission = try? decoder.decode(Mission.self, from: data) {
            return [mission]
        }

        throw MissionImportError.invalidJSON
    }

    private func mergeReviewedAssignments(_ assignments: [MissionAssignment]) throws {
        var existing = reviewedMissionStore.load()
        let importedMissionIDs = Set(assignments.map { $0.mission.missionID })
        existing.removeAll { importedMissionIDs.contains($0.mission.missionID) }
        existing.append(contentsOf: assignments)
        existing.sort { $0.importedAt > $1.importedAt }
        try reviewedMissionStore.save(existing)
    }
}
