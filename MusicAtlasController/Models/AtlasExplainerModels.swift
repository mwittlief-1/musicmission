import Foundation

struct AtlasExplainerPackBundle: Decodable {
    let artifact: String
    let schemaVersion: String
    let sourcePackage: String
    let packCount: Int
    let packs: [AtlasExplainerRenderPack]

    enum CodingKeys: String, CodingKey {
        case artifact
        case schemaVersion = "schema_version"
        case sourcePackage = "source_package"
        case packCount = "pack_count"
        case packs
    }
}

struct AtlasExplainerRenderPack: Decodable, Identifiable, Equatable {
    let schemaVersion: String
    let renderPackID: String
    let identity: AtlasExplainerIdentity
    let graphAlignment: AtlasExplainerGraphAlignment
    let modules: AtlasExplainerModuleSet
    let canonicalExamples: [AtlasExplainerCanonicalExample]
    let personalizationHooks: [AtlasExplainerPersonalizationHook]
    let rightsStatus: String
    let editorialStatus: String
    let nonMutationAssertion: String
    let alphaV0MissionBoundary: AtlasExplainerAlphaMissionBoundary

    var id: String {
        identity.canonicalGraphRef
    }

    var displayTitle: String {
        identity.editorialDisplayTitle
    }

    enum CodingKeys: String, CodingKey {
        case schemaVersion = "schema_version"
        case renderPackID = "render_pack_id"
        case identity
        case graphAlignment = "graph_alignment"
        case modules
        case canonicalExamples = "canonical_examples"
        case personalizationHooks = "personalization_hooks"
        case rightsStatus = "rights_status"
        case editorialStatus = "editorial_status"
        case nonMutationAssertion = "non_mutation_assertion"
        case alphaV0MissionBoundary = "alpha_v0_mission_boundary"
    }
}

struct AtlasExplainerAlphaMissionBoundary: Decodable, Equatable {
    let status: String
    let allowedTermsUsed: [String]
    let forbiddenDynamicMissionLanguagePresent: Bool

    enum CodingKeys: String, CodingKey {
        case status
        case allowedTermsUsed = "allowed_terms_used"
        case forbiddenDynamicMissionLanguagePresent = "forbidden_dynamic_mission_language_present"
    }
}

struct AtlasExplainerIdentity: Decodable, Equatable {
    let familyID: Int
    let familySlug: String
    let familyName: String
    let archetypeID: String
    let archetypeSlug: String
    let canonicalGraphRef: String
    let existingGraphLabelName: String
    let editorialDisplayTitle: String
    let nonMutationAssertion: String

    enum CodingKeys: String, CodingKey {
        case familyID = "family_id"
        case familySlug = "family_slug"
        case familyName = "family_name"
        case archetypeID = "archetype_id"
        case archetypeSlug = "archetype_slug"
        case canonicalGraphRef = "canonical_graph_ref"
        case existingGraphLabelName = "existing_graph_label_name"
        case editorialDisplayTitle = "editorial_display_title"
        case nonMutationAssertion = "non_mutation_assertion"
    }
}

struct AtlasExplainerGraphAlignment: Decodable, Equatable {
    let canonicalGraphRef: String
    let canonicalExampleRefs: [String]
    let surveyCandidateRefs: [String]
    let relatedArchetypeRefs: [String]

    enum CodingKeys: String, CodingKey {
        case canonicalGraphRef = "canonical_graph_ref"
        case canonicalExampleRefs = "canonical_example_refs"
        case surveyCandidateRefs = "survey_candidate_refs"
        case relatedArchetypeRefs = "related_archetype_refs"
    }
}

struct AtlasExplainerModuleSet: Decodable, Equatable {
    let atlasHomeRegionCard: AtlasExplainerCopyVariants
    let regionScenePage: AtlasExplainerCopyVariants
    let missionDetailHistoryModule: AtlasExplainerCopyVariants
    let didYouKnowCard: AtlasExplainerCopyVariants
    let whatToListenForPrompt: AtlasExplainerCopyVariants
    let personalizedAtlasOverlay: AtlasExplainerCopyVariants
    let canonicalExamplesBlock: AtlasExplainerCopyVariants
    let relatedRoadsLineageModule: AtlasExplainerCopyVariants
    let deadEndFalseNearbyCautionModule: AtlasExplainerCopyVariants

    enum CodingKeys: String, CodingKey {
        case atlasHomeRegionCard = "atlas_home_region_card"
        case regionScenePage = "region_scene_page"
        case missionDetailHistoryModule = "mission_detail_history_module"
        case didYouKnowCard = "did_you_know_card"
        case whatToListenForPrompt = "what_to_listen_for_prompt"
        case personalizedAtlasOverlay = "personalized_atlas_overlay"
        case canonicalExamplesBlock = "canonical_examples_block"
        case relatedRoadsLineageModule = "related_roads_lineage_module"
        case deadEndFalseNearbyCautionModule = "dead_end_false_nearby_caution_module"
    }
}

struct AtlasExplainerCopyVariants: Decodable, Equatable {
    let compact: String
    let standard: String
    let deep: String

    func copy(for depth: AtlasExplainerCopyDepth) -> String {
        switch depth {
        case .compact:
            return compact
        case .standard:
            return standard
        case .deep:
            return deep
        }
    }
}

enum AtlasExplainerCopyDepth: String, CaseIterable, Identifiable {
    case compact
    case standard
    case deep

    var id: String {
        rawValue
    }

    var displayName: String {
        rawValue.capitalized
    }
}

enum AtlasExplainerHomeSectionKind: String, CaseIterable, Identifiable {
    case likelyRegions
    case frontiers
    case boundaries

    var id: String {
        rawValue
    }

    var title: String {
        switch self {
        case .likelyRegions:
            return AtlasExplainerRuntimePolicy.likelyRegionsTitle
        case .frontiers:
            return AtlasExplainerRuntimePolicy.frontiersTitle
        case .boundaries:
            return AtlasExplainerRuntimePolicy.boundariesTitle
        }
    }

    var subtitle: String {
        switch self {
        case .likelyRegions:
            return AtlasExplainerRuntimePolicy.likelyRegionsSubtitle
        case .frontiers:
            return AtlasExplainerRuntimePolicy.frontiersSubtitle
        case .boundaries:
            return AtlasExplainerRuntimePolicy.boundariesSubtitle
        }
    }
}

struct AtlasSurveyArchetypeScore: Equatable {
    let archetypeID: String
    let positiveScore: Double
    let fineScore: Double
    let unknownScore: Double
    let negativeScore: Double
    let surveySignalCount: Int

    init(
        archetypeID: String,
        positiveScore: Double,
        fineScore: Double,
        unknownScore: Double,
        negativeScore: Double,
        surveySignalCount: Int = .max
    ) {
        self.archetypeID = archetypeID
        self.positiveScore = positiveScore
        self.fineScore = fineScore
        self.unknownScore = unknownScore
        self.negativeScore = negativeScore
        self.surveySignalCount = surveySignalCount
    }

    var totalSignalScore: Double {
        positiveScore + fineScore + unknownScore + negativeScore
    }

    var netPositiveScore: Double {
        positiveScore + fineScore * 0.35 + unknownScore * 0.15 - negativeScore
    }

    var questionScore: Double {
        negativeScore + fineScore * 0.65 + unknownScore
    }

    var hasLimitedSurveySignals: Bool {
        surveySignalCount <= 3
    }
}

struct AtlasExplainerHomeSection: Identifiable, Equatable {
    let kind: AtlasExplainerHomeSectionKind
    let packs: [AtlasExplainerRenderPack]

    var id: String {
        kind.rawValue
    }

    var title: String {
        kind.title
    }

    var subtitle: String {
        kind.subtitle
    }
}

enum AtlasExplainerRuntimePolicy {
    static let alphaCopyDepth: AtlasExplainerCopyDepth = .standard
    static let alphaHomePackLimit = 10

    static let atlasTitle = "Atlas"
    static let atlasSubtitle = "Explore the music-history roads behind the Atlas."
    static let loadingTitle = "Loading Atlas explainers"
    static let unavailableTitle = "Atlas explainers unavailable"
    static let unavailableDetail = "Atlas explainers are temporarily unavailable."
    static let roadCountSuffix = "roads"
    static let likelyRegionsTitle = "Likely Regions"
    static let likelyRegionsSubtitle = "The survey-scored roads with the clearest positive signal so far."
    static let frontiersTitle = "Frontiers"
    static let frontiersSubtitle = "Promising adjacent roads that need more evidence before they become centers."
    static let boundariesTitle = "Open Questions"
    static let boundariesSubtitle = "Mixed, negative, unknown, or context-dependent roads worth treating carefully."
    static let missionModuleTitle = "Atlas Explainer"
    static let missionModuleBadge = "Atlas context"
    static let missingMissionExplainer = "No Atlas explainer is available for this mission yet."
    static let didYouKnowTitle = "Did You Know"
    static let listenForTitle = "What To Listen For"
    static let examplesTitle = "Key Examples"
    static let relatedRoadsTitle = "Related Roads"
    static let falseNearbyTitle = "False-Nearby Caution"

    static let userFacingChromeStrings = [
        atlasTitle,
        atlasSubtitle,
        loadingTitle,
        unavailableTitle,
        unavailableDetail,
        roadCountSuffix,
        likelyRegionsTitle,
        likelyRegionsSubtitle,
        frontiersTitle,
        frontiersSubtitle,
        boundariesTitle,
        boundariesSubtitle,
        missionModuleTitle,
        missionModuleBadge,
        missingMissionExplainer,
        didYouKnowTitle,
        listenForTitle,
        examplesTitle,
        relatedRoadsTitle,
        falseNearbyTitle
    ]
}

struct AtlasExplainerCanonicalExample: Decodable, Identifiable, Equatable {
    let exampleRef: String
    let exampleType: String
    let displayLabel: String
    let artistDisplayName: String?
    let title: String?
    let year: Int?
    let recognitionBand: String?
    let missionRole: String?
    let ladderSection: String?
    let whyThisExampleMatters: String
    let whatToListenFor: [String]
    let graphRefValidationStatus: String

    var id: String {
        exampleRef
    }

    enum CodingKeys: String, CodingKey {
        case exampleRef = "example_ref"
        case exampleType = "example_type"
        case displayLabel = "display_label"
        case artistDisplayName = "artist_display_name"
        case title
        case year
        case recognitionBand = "recognition_band"
        case missionRole = "mission_role"
        case ladderSection = "ladder_section"
        case whyThisExampleMatters = "why_this_example_matters"
        case whatToListenFor = "what_to_listen_for"
        case graphRefValidationStatus = "graph_ref_validation_status"
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        exampleRef = try container.decode(String.self, forKey: .exampleRef)
        exampleType = try container.decode(String.self, forKey: .exampleType)
        displayLabel = try container.decode(String.self, forKey: .displayLabel)
        artistDisplayName = try container.decodeIfPresent(String.self, forKey: .artistDisplayName)
        title = try container.decodeIfPresent(String.self, forKey: .title)
        year = try container.decodeIfPresent(Int.self, forKey: .year)
        recognitionBand = try container.decodeIfPresent(String.self, forKey: .recognitionBand)
        missionRole = try container.decodeIfPresent(String.self, forKey: .missionRole)
        ladderSection = try container.decodeIfPresent(String.self, forKey: .ladderSection)
        whyThisExampleMatters = try container.decode(String.self, forKey: .whyThisExampleMatters)
        whatToListenFor = try container.decode([String].self, forKey: .whatToListenFor)
        graphRefValidationStatus = try container.decode(String.self, forKey: .graphRefValidationStatus)
    }
}

struct AtlasExplainerPersonalizationHook: Decodable, Identifiable, Equatable {
    let hookID: String
    let requiredStateFields: [String]
    let predicate: String
    let copyVariant: String
    let fallbackCopy: String
    let stateFieldStatus: String

    var id: String {
        hookID
    }

    enum CodingKeys: String, CodingKey {
        case hookID = "hook_id"
        case requiredStateFields = "required_state_fields"
        case predicate
        case copyVariant = "copy_variant"
        case fallbackCopy = "fallback_copy"
        case stateFieldStatus = "state_field_status"
    }
}

struct AtlasExplainerState: Equatable {
    var familyAffinity: [Int: Double] = [:]
    var archetypeAffinity: [String: Double] = [:]
    var completedMissionIDs: Set<String> = []
    var activeMissionID: String?
    var firstBatchMissionIDs: Set<String> = []
    var relatedMissionIDs: Set<String> = []
    var surveyPositiveCandidateRefs: Set<String> = []
    var surveyNegativeCandidateRefs: Set<String> = []
    var boundaryQuestionResults: [String: String] = [:]
    var deadEndProbeResults: [String: String] = [:]
    var userKnownSongRefs: Set<String> = []
    var userDislikedSongRefs: Set<String> = []
    var userSavedArtistRefs: Set<String> = []
    var userSkippedArtistRefs: Set<String> = []

    static let empty = AtlasExplainerState()

    static let genericPreview = AtlasExplainerState(
        firstBatchMissionIDs: ["MISSION_ALPHA_PREVIEW_01"],
        relatedMissionIDs: ["MISSION_ALPHA_PREVIEW_RELATED"]
    )

    func canResolve(_ hook: AtlasExplainerPersonalizationHook) -> Bool {
        guard hook.stateFieldStatus != "proposed" else {
            return false
        }

        return hook.requiredStateFields.allSatisfy(hasImplementedStateField)
    }

    private func hasImplementedStateField(_ field: String) -> Bool {
        switch field {
        case let value where value.hasPrefix("atlas_state.family_affinity["):
            return !familyAffinity.isEmpty
        case let value where value.hasPrefix("atlas_state.archetype_affinity["):
            return !archetypeAffinity.isEmpty
        case "atlas_state.completed_mission_ids":
            return !completedMissionIDs.isEmpty
        case "atlas_state.active_mission_id":
            return activeMissionID != nil
        case "atlas_state.first_batch_mission_ids":
            return !firstBatchMissionIDs.isEmpty
        case "atlas_state.related_mission_ids":
            return !relatedMissionIDs.isEmpty
        case "atlas_state.survey_positive_candidate_refs":
            return !surveyPositiveCandidateRefs.isEmpty
        case "atlas_state.survey_negative_candidate_refs":
            return !surveyNegativeCandidateRefs.isEmpty
        case "atlas_state.boundary_question_results":
            return !boundaryQuestionResults.isEmpty
        case "atlas_state.dead_end_probe_results":
            return !deadEndProbeResults.isEmpty
        case "atlas_state.user_known_song_refs":
            return !userKnownSongRefs.isEmpty
        case "atlas_state.user_disliked_song_refs":
            return !userDislikedSongRefs.isEmpty
        case "atlas_state.user_saved_artist_refs":
            return !userSavedArtistRefs.isEmpty
        case "atlas_state.user_skipped_artist_refs":
            return !userSkippedArtistRefs.isEmpty
        default:
            return false
        }
    }
}
