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

enum AtlasExplainerRuntimePolicy {
    static let alphaCopyDepth: AtlasExplainerCopyDepth = .standard

    static let atlasTitle = "Atlas"
    static let atlasSubtitle = "Explore the music-history roads behind the Atlas."
    static let loadingTitle = "Loading Atlas explainers"
    static let unavailableTitle = "Atlas explainers unavailable"
    static let unavailableDetail = "Atlas explainers are temporarily unavailable."
    static let roadCountSuffix = "roads"
    static let featuredRoadsTitle = "Featured Roads"
    static let featuredBadge = "Featured"
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
        featuredRoadsTitle,
        featuredBadge,
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
        case whyThisExampleMatters = "why_this_example_matters"
        case whatToListenFor = "what_to_listen_for"
        case graphRefValidationStatus = "graph_ref_validation_status"
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
