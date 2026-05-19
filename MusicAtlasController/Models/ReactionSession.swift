import Foundation

struct ReactionSession: Codable {
    let schemaVersion: String
    let sessionID: String
    let missionID: String
    let missionVersion: String
    let createdAt: Date
    let startedAt: Date
    let endedAt: Date?
    let reconciliationStatus: ReconciliationStatus
    let deviceContext: DeviceContext
    let musicContext: MusicContext
    let itemResults: [ItemResult]
    let sessionSummary: SessionSummary?
    let export: ExportRecord

    enum CodingKeys: String, CodingKey {
        case schemaVersion = "schema_version"
        case sessionID = "session_id"
        case missionID = "mission_id"
        case missionVersion = "mission_version"
        case createdAt = "created_at"
        case startedAt = "started_at"
        case endedAt = "ended_at"
        case reconciliationStatus = "reconciliation_status"
        case deviceContext = "device_context"
        case musicContext = "music_context"
        case itemResults = "item_results"
        case sessionSummary = "session_summary"
        case export
    }
}

enum ReconciliationStatus: String, Codable {
    case notReconciled = "not_reconciled"
    case reconciliationCandidate = "reconciliation_candidate"
    case reconciled
    case ignored
}

struct DeviceContext: Codable {
    let deviceModel: String
    let osVersion: String
    let appVersion: String
    let isPhysicalDevice: Bool

    enum CodingKeys: String, CodingKey {
        case deviceModel = "device_model"
        case osVersion = "os_version"
        case appVersion = "app_version"
        case isPhysicalDevice = "is_physical_device"
    }
}

struct MusicContext: Codable {
    let authorizationStatus: String
    let playbackCapabilityStatus: String
    let storefront: String?
    let subscriptionNotes: String?

    enum CodingKeys: String, CodingKey {
        case authorizationStatus = "authorization_status"
        case playbackCapabilityStatus = "playback_capability_status"
        case storefront
        case subscriptionNotes = "subscription_notes"
    }
}

struct ItemResult: Codable {
    let missionItemID: String
    let sequence: Int
    let itemType: MissionItemType
    let artist: String
    let title: String
    let album: String?
    let resolution: AppleMusicResolution
    let playback: PlaybackRecord
    let reaction: ReactionRecord
    let timestamps: ItemTimestamps

    enum CodingKeys: String, CodingKey {
        case missionItemID = "mission_item_id"
        case sequence
        case itemType = "item_type"
        case artist
        case title
        case album
        case resolution
        case playback
        case reaction
        case timestamps
    }
}

struct PlaybackRecord: Codable {
    let status: PlaybackStatus
    let attemptedAt: Date?
    let startedAt: Date?
    let endedAt: Date?
    let durationSeconds: Double?
    let errorCode: String?
    let errorMessage: String?

    enum CodingKeys: String, CodingKey {
        case status
        case attemptedAt = "attempted_at"
        case startedAt = "started_at"
        case endedAt = "ended_at"
        case durationSeconds = "duration_seconds"
        case errorCode = "error_code"
        case errorMessage = "error_message"
    }

    static func notAttempted() -> PlaybackRecord {
        PlaybackRecord(
            status: .notAttempted,
            attemptedAt: nil,
            startedAt: nil,
            endedAt: nil,
            durationSeconds: nil,
            errorCode: nil,
            errorMessage: nil
        )
    }

    static func simulatedPlayed(at date: Date) -> PlaybackRecord {
        PlaybackRecord(
            status: .played,
            attemptedAt: date,
            startedAt: date,
            endedAt: date,
            durationSeconds: 0,
            errorCode: nil,
            errorMessage: nil
        )
    }

    static func skipped(at date: Date) -> PlaybackRecord {
        PlaybackRecord(
            status: .skipped,
            attemptedAt: date,
            startedAt: nil,
            endedAt: nil,
            durationSeconds: nil,
            errorCode: nil,
            errorMessage: nil
        )
    }

    func endedAsSkipped(at date: Date) -> PlaybackRecord {
        let effectiveStartedAt = startedAt ?? attemptedAt
        let duration = effectiveStartedAt.map { max(0, date.timeIntervalSince($0)) }

        return PlaybackRecord(
            status: .skipped,
            attemptedAt: attemptedAt ?? date,
            startedAt: effectiveStartedAt,
            endedAt: date,
            durationSeconds: duration,
            errorCode: nil,
            errorMessage: nil
        )
    }

    func endedAsPlayed(at date: Date) -> PlaybackRecord {
        let effectiveStartedAt = startedAt ?? attemptedAt
        let duration = effectiveStartedAt.map { max(0, date.timeIntervalSince($0)) }

        return PlaybackRecord(
            status: .played,
            attemptedAt: attemptedAt ?? date,
            startedAt: effectiveStartedAt,
            endedAt: date,
            durationSeconds: duration,
            errorCode: nil,
            errorMessage: nil
        )
    }

    func movedPlaybackPosition(to elapsedSeconds: TimeInterval, at date: Date) -> PlaybackRecord {
        guard status == .playing else {
            return self
        }

        let boundedElapsed = max(0, elapsedSeconds)
        return PlaybackRecord(
            status: status,
            attemptedAt: attemptedAt ?? date,
            startedAt: date.addingTimeInterval(-boundedElapsed),
            endedAt: nil,
            durationSeconds: durationSeconds,
            errorCode: errorCode,
            errorMessage: errorMessage
        )
    }

    var hasPlaybackStarted: Bool {
        startedAt != nil || status == .playing || status == .played
    }

    func completionFraction(at date: Date) -> Double? {
        guard let startedAt, let durationSeconds, durationSeconds > 0 else {
            return nil
        }

        return max(0, date.timeIntervalSince(startedAt)) / durationSeconds
    }

    func hasReachedCompletionThreshold(at date: Date, threshold: Double = 0.9) -> Bool {
        guard let completionFraction = completionFraction(at: date) else {
            return false
        }

        return completionFraction >= threshold
    }

    var hasExportablePlaybackEvidence: Bool {
        status == .played || status == .playing || status == .skipped
    }
}

enum PlaybackStatus: String, Codable {
    case notAttempted = "not_attempted"
    case queued
    case playing
    case played
    case skipped
    case failed
}

struct PlaybackSnapshot: Equatable {
    let runtimeStatus: PlaybackRuntimeStatus
    let elapsedSeconds: TimeInterval
    let totalDurationSeconds: TimeInterval?

    var isPlaying: Bool {
        runtimeStatus == .playing
    }

    var progress: Double {
        guard let totalDurationSeconds, totalDurationSeconds > 0 else {
            switch runtimeStatus {
            case .completed:
                return 1
            case .playing, .paused, .interrupted, .seeking:
                return 0.04
            case .idle, .stopped:
                return 0
            }
        }

        return min(1, max(0, elapsedSeconds / totalDurationSeconds))
    }

    var remainingSeconds: TimeInterval? {
        guard let totalDurationSeconds else {
            return nil
        }

        return max(0, totalDurationSeconds - elapsedSeconds)
    }

    static let idle = PlaybackSnapshot(
        runtimeStatus: .idle,
        elapsedSeconds: 0,
        totalDurationSeconds: nil
    )

    static func from(record: PlaybackRecord) -> PlaybackSnapshot {
        switch record.status {
        case .notAttempted, .queued, .failed:
            return .idle
        case .playing:
            let elapsed = record.startedAt.map { max(0, Date().timeIntervalSince($0)) } ?? 0
            return PlaybackSnapshot(
                runtimeStatus: .playing,
                elapsedSeconds: elapsed,
                totalDurationSeconds: record.durationSeconds
            )
        case .played:
            return PlaybackSnapshot(
                runtimeStatus: .completed,
                elapsedSeconds: record.durationSeconds ?? 0,
                totalDurationSeconds: record.durationSeconds
            )
        case .skipped:
            return PlaybackSnapshot(
                runtimeStatus: .stopped,
                elapsedSeconds: record.durationSeconds ?? 0,
                totalDurationSeconds: nil
            )
        }
    }
}

enum PlaybackRuntimeStatus: Equatable {
    case idle
    case playing
    case paused
    case stopped
    case interrupted
    case seeking
    case completed
}

struct ReactionRecord: Codable {
    let reactionValue: ReactionValue
    let reactedAt: Date
    let selectedTags: [ReactionTag]?
    let notes: ReactionNotes

    enum CodingKeys: String, CodingKey {
        case reactionValue = "reaction_value"
        case reactedAt = "reacted_at"
        case selectedTags = "selected_tags"
        case notes
    }

    init(
        reactionValue: ReactionValue,
        reactedAt: Date,
        selectedTags: [ReactionTag]? = nil,
        notes: ReactionNotes
    ) {
        self.reactionValue = reactionValue
        self.reactedAt = reactedAt
        self.selectedTags = selectedTags
        self.notes = notes
    }
}

enum ReactionValue: String, Codable, CaseIterable, Identifiable {
    case hit
    case partial
    case okShelf = "ok_shelf"
    case miss
    case slop
    case skipped
    case unresolved

    var id: String {
        rawValue
    }

    var displayName: String {
        ReactionDisplayConfiguration.current.label(for: self)
    }

    var operation: ReactionOperation? {
        switch self {
        case .hit:
            return .strongPositive
        case .partial:
            return .qualifiedPositive
        case .okShelf:
            return .keepWaypoint
        case .miss:
            return .negative
        case .slop:
            return .negative
        case .skipped, .unresolved:
            return nil
        }
    }

    static let primarySignalValues: [ReactionValue] = [.hit, .partial, .okShelf, .miss]
}

enum ReactionOperation: String, CaseIterable, Identifiable {
    case strongPositive = "strong_positive"
    case qualifiedPositive = "qualified_positive"
    case keepWaypoint = "keep_waypoint"
    case negative

    var id: String {
        rawValue
    }

    var defaultReactionValue: ReactionValue {
        switch self {
        case .strongPositive:
            return .hit
        case .qualifiedPositive:
            return .partial
        case .keepWaypoint:
            return .okShelf
        case .negative:
            return .miss
        }
    }
}

struct ReactionDisplayConfiguration {
    var labelsByOperation: [ReactionOperation: String]
    var fallbackLabels: [ReactionValue: String]

    static let current = ReactionDisplayConfiguration(
        labelsByOperation: [
            .strongPositive: "Love",
            .qualifiedPositive: "Like",
            .keepWaypoint: "Ok",
            .negative: "Dislike"
        ],
        fallbackLabels: [
            .slop: "Slop",
            .skipped: "Skipped",
            .unresolved: "No Signal"
        ]
    )

    func label(for reactionValue: ReactionValue) -> String {
        if let operation = reactionValue.operation,
           let label = labelsByOperation[operation] {
            return label
        }

        return fallbackLabels[reactionValue] ?? reactionValue.rawValue
    }

    func label(for operation: ReactionOperation) -> String {
        labelsByOperation[operation] ?? operation.rawValue
    }
}

struct ReactionTag: Codable, Equatable, Hashable {
    let tagID: String
    let label: String
    let primaryReactionValue: ReactionValue
    let description: String?

    enum CodingKeys: String, CodingKey {
        case tagID = "tag_id"
        case label
        case primaryReactionValue = "primary_reaction_value"
        case description
    }
}

struct ReactionNotes: Codable {
    let text: String
    let voiceNoteRefs: [String]?

    enum CodingKeys: String, CodingKey {
        case text
        case voiceNoteRefs = "voice_note_refs"
    }
}

struct ItemTimestamps: Codable {
    let createdAt: Date
    let updatedAt: Date

    enum CodingKeys: String, CodingKey {
        case createdAt = "created_at"
        case updatedAt = "updated_at"
    }
}

struct SessionSummary: Codable {
    let itemCount: Int?
    let resolvedCount: Int?
    let playedCount: Int?
    let reactionCount: Int?
    let summaryNote: String?

    enum CodingKeys: String, CodingKey {
        case itemCount = "item_count"
        case resolvedCount = "resolved_count"
        case playedCount = "played_count"
        case reactionCount = "reaction_count"
        case summaryNote = "summary_note"
    }
}

struct ExportRecord: Codable {
    let exportedAt: Date
    let jsonFilename: String
    let markdownFilename: String
    let validationStatus: String?
    let validationErrors: [String]?

    enum CodingKeys: String, CodingKey {
        case exportedAt = "exported_at"
        case jsonFilename = "json_filename"
        case markdownFilename = "markdown_filename"
        case validationStatus = "validation_status"
        case validationErrors = "validation_errors"
    }
}
