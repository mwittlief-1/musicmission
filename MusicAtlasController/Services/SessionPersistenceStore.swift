import Foundation

struct PersistedSessionLibrary: Codable {
    var activeMissionID: String?
    var sessionsByMissionID: [String: PersistedMissionSession]
    var updatedAt: Date?

    static let empty = PersistedSessionLibrary(
        activeMissionID: nil,
        sessionsByMissionID: [:],
        updatedAt: nil
    )
}

struct PersistedMissionSession: Codable {
    let missionID: String
    let selectedItemID: String?
    let resolutions: [String: AppleMusicResolution]
    let playbackRecords: [String: PlaybackRecord]
    let reactions: [String: ReactionRecord]
    let updatedAt: Date

    enum CodingKeys: String, CodingKey {
        case missionID = "mission_id"
        case selectedItemID = "selected_item_id"
        case resolutions
        case playbackRecords = "playback_records"
        case reactions
        case updatedAt = "updated_at"
    }
}

struct SessionPersistenceStore {
    private let fileManager: FileManager
    private let baseDirectoryURL: URL?
    private let isEnabled: Bool
    private let filename = "waymark_session_library_v0_1.json"

    init(
        fileManager: FileManager = .default,
        baseDirectoryURL: URL? = nil,
        isEnabled: Bool = true
    ) {
        self.fileManager = fileManager
        self.baseDirectoryURL = baseDirectoryURL
        self.isEnabled = isEnabled
    }

    static let disabled = SessionPersistenceStore(isEnabled: false)

    func load() -> PersistedSessionLibrary {
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
            return try decoder.decode(PersistedSessionLibrary.self, from: data)
        } catch {
            return .empty
        }
    }

    func save(_ library: PersistedSessionLibrary) throws {
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
        let data = try encoder.encode(library)
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
