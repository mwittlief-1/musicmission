export type MissionTypeRegistryContractVersionV01 = "mission_type_registry_v0_1";

export type MissionTypeV01 =
  | "initial_profile_survey"
  | "family_survey"
  | "archetype_survey"
  | "gateway_test"
  | "song_to_archetype_test"
  | "artist_depth_test"
  | "album_container_test"
  | "archetype_depth_test"
  | "exception_scope_test"
  | "false_nearby_test"
  | "context_dependence_test"
  | "bridge_test"
  | "boundary_test"
  | "evidence_repair_test";

export type MissionValueBandV01 =
  | "low"
  | "lower_medium"
  | "medium"
  | "high"
  | "very_high";

export type TargetObjectTypeV01 =
  | "family"
  | "archetype"
  | "artist"
  | "album"
  | "song"
  | "archetype_pair"
  | "family_pair"
  | "song_cluster";

export interface MissionTypeRegistryV01 {
  contract_version: MissionTypeRegistryContractVersionV01;
  fixture_status: "synthetic_contract_fixture";
  runtime_allowed: false;
  production_mission_generation_allowed: false;
  canonical_graph_mutation_allowed: false;
  listener_preference_inference_from_affinity_allowed: false;
  global_top_k_opportunities: 25;
  mission_types: MissionTypeDefinitionV01[];
}

export interface MissionTypeDefinitionV01 {
  mission_type: MissionTypeV01;
  value_band: MissionValueBandV01;
  score_floor: number;
  score_ceiling: number;
  floor_summary: string;
  ceiling_summary: string;
  required_blob_shape: RequiredOpportunityBlobShapeV01;
  scoring_weights: OpportunityScoreWeightsV01;
  candidate_generation_caps: CandidateGenerationCapsV01;
  runtime_allowed: false;
  production_mission_generation_allowed: false;
}

export interface RequiredOpportunityBlobShapeV01 {
  target_object_types: TargetObjectTypeV01[];
  requires_graph_context: true;
  requires_evidence_rollup: boolean;
  requires_affinity_context: boolean;
  requires_risk_context: boolean;
  requires_candidate_generation_summary: true;
  requires_floor_details: true;
  requires_score_components: true;
  requires_bridge_readiness?: boolean;
  requires_gateway_availability?: boolean;
}

export interface OpportunityScoreWeightsV01 {
  mission_type_value: number;
  mission_fit_score: number;
  readiness_score: number;
  learning_value_score: number;
  risk_penalty: number;
  repetition_penalty: number;
  complexity_penalty: number;
}

export interface CandidateGenerationCapsV01 {
  max_targets: number;
  max_candidates_per_target: number;
  batch_size: number;
  max_candidates_total: number;
  cap_reason: string;
}
