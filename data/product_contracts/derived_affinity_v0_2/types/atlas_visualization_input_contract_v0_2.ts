export type AtlasVisualizationContractVersion = "atlas_visualization_input_v0_2";
export type DerivedAffinitySubstrateVersion = "derived_affinity_substrate_v0_1_1";

export type AtlasSurfaceType =
  | "Region"
  | "Road"
  | "Frontier"
  | "Dead End"
  | "Caution"
  | "Gateway"
  | "Landmark"
  | "Waypoint"
  | "Bridge"
  | "Recent Learning";

export type AffinityConfidence = "low" | "medium" | "high";
export type AtlasFogState = "clear" | "hazy" | "fogged" | "blocked";

export type BridgeCategory =
  | "clean_bridge_candidate"
  | "review_bridge_candidate"
  | "identity_quarantine"
  | "context_only_bridge"
  | "high_whiplash_bridge"
  | "false_nearby_bridge"
  | "mission_specific_bridge";

export type QuarantineStatus =
  | "none"
  | "review"
  | "identity_quarantine"
  | "not_applicable";

export type ListenerEvidenceStatus =
  | "absent"
  | "present"
  | "required_before_assignment";

export type RoleAssignmentStatus =
  | "candidate_only"
  | "not_assignable_from_substrate"
  | "assigned_after_review";

export type RoleAssignmentScope =
  | "non_personal_review_candidate"
  | "requires_listener_evidence"
  | "blocked";

export type ScoreComponents = Record<string, unknown>;

export interface AtlasVisualizationInputV02 {
  contract_version: AtlasVisualizationContractVersion;
  fixture_status: string;
  source_substrate_version: DerivedAffinitySubstrateVersion;
  source_package: "derived_affinity_substrate_v0_1_1/";
  runtime_allowed: false;
  canonical_graph_mutation_allowed: false;
  listener_preference_inference_allowed: false;
  surfaces: AtlasSurfaceV02[];
}

export interface AtlasSurfaceV02 {
  surface_id: string;
  surface_type: AtlasSurfaceType;
  contract_version: AtlasVisualizationContractVersion;
  source_substrate_version: DerivedAffinitySubstrateVersion;
  source_candidate_ids: string[];
  source_candidate_types: string[];
  intrinsic_affinity: AtlasIntrinsicAffinityV02;
  context_overlays: string[];
  risk_review: AtlasRiskReviewV02;
  readiness: AtlasReadinessV02;
  listener_evidence: AtlasListenerEvidenceV02;
  role_assignment: AtlasRoleAssignmentV02;
  display_policy: AtlasDisplayPolicyV02;
  provenance: AtlasProvenanceV02;
}

export interface AtlasIntrinsicAffinityV02 {
  dominant_tags: string[];
  secondary_tags: string[];
  shared_tags: string[];
  intrinsic_affinity_score: number | null;
  score_components: ScoreComponents;
}

export interface AtlasRiskReviewV02 {
  risk_flags: string[];
  review_flags: string[];
  bridge_category: BridgeCategory | null;
  quarantine_status: QuarantineStatus;
  review_required: true;
}

export interface AtlasReadinessV02 {
  product_bridge_readiness_score: number | null;
  confidence: AffinityConfidence;
  fog_state: AtlasFogState;
  readiness_notes: string[];
}

export interface AtlasListenerEvidenceV02 {
  status: ListenerEvidenceStatus;
  evidence_ids: string[];
  not_inferred_from_affinity: true;
}

export interface AtlasRoleAssignmentV02 {
  status: RoleAssignmentStatus;
  scope: RoleAssignmentScope;
  requires_pm_approval: true;
  assigned_role: string | null;
}

export interface AtlasDisplayPolicyV02 {
  can_render_in_review: boolean;
  can_render_in_product: false;
  label: string;
  explanation: string;
}

export interface AtlasProvenanceV02 {
  source_files: string[];
  canonical_graph_mutation: "not_performed";
  runtime_ingestion: "not_performed";
}
