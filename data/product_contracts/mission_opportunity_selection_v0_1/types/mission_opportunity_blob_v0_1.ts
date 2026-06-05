import type { MissionTypeV01, TargetObjectTypeV01 } from "./mission_type_registry_v0_1";
import type { GraphContextV01, TargetObjectRefV01 } from "./evidence_rollup_v0_1";

export type MissionOpportunityBlobContractVersionV01 = "mission_opportunity_blob_v0_1";

export interface MissionOpportunityBlobV01 {
  contract_version: MissionOpportunityBlobContractVersionV01;
  opportunity_id: string;
  mission_type: MissionTypeV01;
  target_object_type: TargetObjectTypeV01;
  target_object_ids: string[];
  target_object_ref: TargetObjectRefV01;
  floor_passed: boolean;
  floor_details: OpportunityFloorDetailsV01;
  filled_requirements: FilledOpportunityRequirementsV01;
  source_signal_summary: SourceSignalSummaryV01;
  graph_context_summary: GraphContextSummaryV01;
  affinity_context_summary: AffinityContextSummaryV01;
  risk_context_summary: RiskContextSummaryV01;
  candidate_generation_summary: OpportunityCandidateGenerationSummaryV01;
  score_components: OpportunityScoreComponentsV01;
  activation_reasons: string[];
  risk_reasons: string[];
  suppression_reasons: string[];
  required_inputs_available: boolean;
  opportunity_only: true;
  construction_status: "not_constructed";
  runtime_allowed: false;
  production_mission_generation_allowed: false;
  canonical_graph_mutation_allowed: false;
  listener_preference_inference_from_affinity_allowed: false;
}

export interface OpportunityFloorDetailsV01 {
  mission_type_score_floor: number;
  mission_type_score_ceiling: number;
  computed_floor_score: number;
  floor_passed: boolean;
  failed_requirements: string[];
  fail_reasons: string[];
  floor_evidence_refs: string[];
}

export interface FilledOpportunityRequirementsV01 {
  required_evidence_rollup_refs: string[];
  required_graph_object_refs: TargetObjectRefV01[];
  candidate_refs: string[];
  required_inputs_available: boolean;
}

export interface SourceSignalSummaryV01 {
  target_rollup_ref: string;
  target_object_type: TargetObjectTypeV01;
  target_object_ids: string[];
  target_display_name: string;
  positive_signal_count: number;
  negative_signal_count: number;
  weak_non_failure_signal_count: number;
  survey_ok_ignored_count: number;
  mission_ok_weak_count: number;
  evidence_density: number;
  conflict_score: number;
  recency_score: number;
}

export interface GraphContextSummaryV01 {
  graph_contexts: GraphContextV01[];
  endpoint_graph_contexts: GraphContextV01[];
  tier_coverage_score: number;
  tier_depth_score: number;
  coverage_gap_score: number;
  depth_gap_score: number;
}

export interface AffinityContextSummaryV01 {
  dominant_affinity_tags: string[];
  context_overlays: string[];
  bridge_readiness_score: number | null;
  gateway_availability: {
    available: boolean;
    gateway_candidate_refs: string[];
    gateway_to_representative_coherence_score: number | null;
  };
  context_variability_score: number;
  context_skew_score: number;
}

export interface RiskContextSummaryV01 {
  risk_flags: string[];
  identity_flags: string[];
  risk_penalty_basis: string[];
  identity_or_version_risk_present: boolean;
}

export interface OpportunityCandidateGenerationSummaryV01 {
  generator_id: string;
  batch_index: number;
  input_rollup_refs: string[];
  eligible_candidate_count: number;
  emitted_candidate_count: number;
  pruned_candidate_count: number;
  floor_failed_candidate_count: number;
  cap_applied: boolean;
  cap_value: number;
  batch_size: number;
  generation_notes: string[];
}

export interface OpportunityScoreComponentsV01 {
  mission_type_value: number;
  mission_fit_score: number;
  readiness_score: number;
  learning_value_score: number;
  risk_penalty: number;
  repetition_penalty: number;
  complexity_penalty: number;
  raw_score: number;
  final_opportunity_score: number;
}
