import type {
  AffinityConfidence,
  BridgeCategory,
  DerivedAffinitySubstrateVersion
} from "./atlas_visualization_input_contract_v0_2";

export type MissionConstructionContractVersion = "mission_construction_v0_2";
export type AtlasDeltaWriteMode = "evidence_only";
export type MissionTypeV02 =
  | "safe_risky_split"
  | "album_world_test"
  | "route_gateway_mission"
  | "cross_family_bridge_mission"
  | "frontier_probe"
  | "false_nearby_trap_test"
  | "one_object_exception_test"
  | "context_mission"
  | "b_b_plus_shelf_mission"
  | "modern_discovery_correction";

export type GraphItemRoleV02 =
  | "canonical_anchor"
  | "major_representative"
  | "gateway"
  | "bridge"
  | "deep_cut"
  | "contextual_object"
  | "unknown";

export interface MissionConstructionInputV02 {
  contract_version: MissionConstructionContractVersion;
  fixture_status: string;
  source_substrate_version: DerivedAffinitySubstrateVersion;
  source_package: "derived_affinity_substrate_v0_1_1/";
  runtime_allowed: false;
  production_mission_allowed: false;
  canonical_graph_mutation_allowed: false;
  listener_preference_inference_allowed: false;
  mission_candidates: MissionCandidateV02[];
}

export interface MissionCandidateV02 {
  mission_id: string;
  contract_version: MissionConstructionContractVersion;
  source_substrate_version: DerivedAffinitySubstrateVersion;
  mission_type: MissionTypeV02;
  mission_hypothesis: string;
  target_affinity_pattern: string[];
  known_anchors: MissionTrackCandidateV02[];
  gateway_candidates: MissionTrackCandidateV02[];
  bridge_candidates: MissionBridgeCandidateV02[];
  frontier_probes: MissionTrackCandidateV02[];
  caution_high_whiplash_controls: MissionTrackCandidateV02[];
  identity_duplicate_quarantine_exclusions: MissionQuarantineExclusionV02[];
  route_sequence: MissionRouteItemV02[];
  reaction_prompts: string[];
  expected_evidence: MissionExpectedEvidenceV02;
  atlas_delta_plan: MissionAtlasDeltaPlanV02;
  listener_evidence: MissionListenerEvidenceV02;
  review: MissionReviewPolicyV02;
  provenance: MissionProvenanceV02;
}

export interface MissionTrackCandidateV02 {
  candidate_id: string;
  track_id: string;
  title: string;
  artist_names: string[];
  inclusion_reason: string;
  intrinsic_affinity_tags: string[];
  context_overlays: string[];
  risk_flags: string[];
  graph_context: MissionGraphContextV02;
  confidence: AffinityConfidence;
  evidence_gap?: string;
  framing_required?: boolean;
}

export interface MissionBridgeCandidateV02 {
  candidate_id: string;
  bridge_category: BridgeCategory;
  source_track_id: string;
  target_track_id: string;
  inclusion_reason: string;
  shared_affinity_tags: string[];
  context_overlays: string[];
  risk_flags: string[];
  intrinsic_affinity_score: number;
  product_bridge_readiness_score: number;
  graph_context: MissionGraphContextV02;
  confidence: AffinityConfidence;
}

export interface MissionGraphContextV02 {
  family_ids: string[];
  family_names: string[];
  archetype_ids: string[];
  archetype_names: string[];
  archetype_role: string | null;
  membership_role: string | null;
  track_tier_within_archetype: string | null;
  album_tier_within_archetype: string | null;
  artist_tier_within_archetype: string | null;
  graph_item_role: GraphItemRoleV02;
  role_basis: string;
  provenance: MissionGraphContextProvenanceV02;
}

export interface MissionGraphContextProvenanceV02 {
  source_files: string[];
  source_candidate_ids: string[];
  source_fields: string[];
  notes: string;
}

export interface MissionQuarantineExclusionV02 {
  candidate_id: string;
  exclusion_reason: string;
  bridge_category: BridgeCategory;
  risk_flags: string[];
}

export type MissionRouteRole =
  | "gateway"
  | "clean_bridge"
  | "target_pattern_reinforcement"
  | "frontier_probe"
  | "caution_control"
  | "high_whiplash_control"
  | "closing_prompt";

export interface MissionRouteItemV02 {
  sequence_index: number;
  route_role: MissionRouteRole;
  candidate_id: string;
  track_id: string;
  inclusion_reason: string;
  tests: string;
  intrinsic_affinity_tags: string[];
  context_overlays: string[];
  risk_flags: string[];
  graph_context: MissionGraphContextV02;
  confidence: AffinityConfidence;
  readiness_notes: string[];
}

export interface MissionExpectedEvidenceV02 {
  confirming: string[];
  falsifying: string[];
  ambiguous: string[];
}

export interface MissionAtlasDeltaPlanV02 {
  if_confirmed: string[];
  if_falsified: string[];
  if_ambiguous: string[];
  write_mode: AtlasDeltaWriteMode;
}

export interface MissionListenerEvidenceV02 {
  status: "absent_at_construction";
  evidence_ids: string[];
  not_inferred_from_affinity: true;
}

export interface MissionReviewPolicyV02 {
  pm_review_required: true;
  runtime_allowed: false;
  production_mission_allowed: false;
}

export interface MissionProvenanceV02 {
  source_files: string[];
  canonical_graph_mutation: "not_performed";
  runtime_ingestion: "not_performed";
}
