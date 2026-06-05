import Foundation

enum AtlasHomeReadoutSignalRole: String, Codable, CaseIterable {
    case strongestCenter = "strongest_center"
    case soundShape = "sound_shape"
    case secondaryBranch = "secondary_branch"
    case sparseCleanSignal = "sparse_clean_signal"
    case openQuestionBoundary = "open_question_boundary"

    var displayLabel: String {
        switch self {
        case .strongestCenter:
            return "Strongest Center"
        case .soundShape:
            return "Sound Shape"
        case .secondaryBranch:
            return "Secondary Branch"
        case .sparseCleanSignal:
            return "Small Signal"
        case .openQuestionBoundary:
            return "Open Question"
        }
    }

    var systemImage: String {
        switch self {
        case .strongestCenter:
            return "scope"
        case .soundShape:
            return "waveform"
        case .secondaryBranch:
            return "point.3.connected.trianglepath.dotted"
        case .sparseCleanSignal:
            return "sparkle.magnifyingglass"
        case .openQuestionBoundary:
            return "signpost.right"
        }
    }
}

struct AtlasHomeReadoutCard: Codable, Identifiable, Equatable {
    let signalRole: AtlasHomeReadoutSignalRole
    let title: String
    let body: String
    let evidenceExamples: [String]

    var id: AtlasHomeReadoutSignalRole {
        signalRole
    }

    enum CodingKeys: String, CodingKey {
        case signalRole = "signal_role"
        case title
        case body
        case evidenceExamples = "evidence_examples"
    }
}

struct AtlasHomeReadoutDisplayModel: Codable, Equatable {
    let moduleName: String
    let openingInsight: String
    let insightCards: [AtlasHomeReadoutCard]
    let setupLine: String?

    enum CodingKeys: String, CodingKey {
        case moduleName = "module_name"
        case openingInsight = "opening_insight"
        case insightCards = "insight_cards"
        case setupLine = "setup_line"
    }
}

struct AtlasHomeSparseSignalDebug: Codable, Equatable {
    let candidates: [AtlasHomeSparseSignalCandidate]
}

struct AtlasHomeSparseSignalCandidate: Codable, Identifiable, Equatable {
    let label: String
    let positiveExamples: [String]
    let negativeExamples: [String]
    let neutralExamples: [String]
    let neutralEvidenceNote: String
    let hasMeaningfulGraphCoherence: Bool
    let hasFutureTestValue: Bool
    let eligible: Bool
    let decision: String
    let surfacedCardTitle: String?

    var id: String {
        label
    }

    var satisfiesSparseCleanRule: Bool {
        positiveExamples.count >= 2
            && negativeExamples.isEmpty
            && neutralExamples.isEmpty
            && hasMeaningfulGraphCoherence
            && hasFutureTestValue
    }

    enum CodingKeys: String, CodingKey {
        case label
        case positiveExamples = "positive_examples"
        case negativeExamples = "negative_examples"
        case neutralExamples = "neutral_examples"
        case neutralEvidenceNote = "neutral_evidence_note"
        case hasMeaningfulGraphCoherence = "has_meaningful_graph_coherence"
        case hasFutureTestValue = "has_future_test_value"
        case eligible
        case decision
        case surfacedCardTitle = "surfaced_card_title"
    }
}

struct AtlasHomeReadoutAcceptanceAudit: Codable, Equatable {
    let moduleWordCount: Int
    let openingWordCount: Int
    let cardCount: Int
    let cardRoles: [AtlasHomeReadoutSignalRole]
    let cardTitleWordCounts: [Int]
    let cardBodyWordCounts: [Int]
    let evidenceExamplesPerCard: [Int]
    let sparseCleanSignalPresent: Bool
    let forbiddenPatternsPresent: [String]
    let usesSyntheticFixtureStateOnly: Bool
    let runtimeGenerationRequired: Bool

    enum CodingKeys: String, CodingKey {
        case moduleWordCount = "module_word_count"
        case openingWordCount = "opening_word_count"
        case cardCount = "card_count"
        case cardRoles = "card_roles"
        case cardTitleWordCounts = "card_title_word_counts"
        case cardBodyWordCounts = "card_body_word_counts"
        case evidenceExamplesPerCard = "evidence_examples_per_card"
        case sparseCleanSignalPresent = "sparse_clean_signal_present"
        case forbiddenPatternsPresent = "forbidden_patterns_present"
        case usesSyntheticFixtureStateOnly = "uses_synthetic_fixture_state_only"
        case runtimeGenerationRequired = "runtime_generation_required"
    }
}

struct AtlasHomeReadoutFixture: Codable, Equatable {
    let schemaVersion: String
    let sourceFixtureID: String
    let displayModel: AtlasHomeReadoutDisplayModel
    let sparseSignalDebug: AtlasHomeSparseSignalDebug
    let acceptanceAudit: AtlasHomeReadoutAcceptanceAudit

    enum CodingKeys: String, CodingKey {
        case schemaVersion = "schema_version"
        case sourceFixtureID = "source_fixture_id"
        case displayModel = "display_model"
        case sparseSignalDebug = "sparse_signal_debug"
        case acceptanceAudit = "acceptance_audit"
    }
}
