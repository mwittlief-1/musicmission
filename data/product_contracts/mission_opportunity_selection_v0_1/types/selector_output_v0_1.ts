import type { MissionTypeV01 } from "./mission_type_registry_v0_1";
import type { MissionOpportunityBlobV01 } from "./mission_opportunity_blob_v0_1";

export type SelectorOutputContractVersionV01 = "selector_output_v0_1";

export interface SelectorOutputV01 {
  contract_version: SelectorOutputContractVersionV01;
  fixture_status: "synthetic_contract_fixture";
  selector_run_id: string;
  created_at: string;
  runtime_allowed: false;
  production_mission_generation_allowed: false;
  canonical_graph_mutation_allowed: false;
  listener_preference_inference_from_affinity_allowed: false;
  opportunity_only: true;
  source_registry_ref: string;
  source_evidence_rollup_ref: string;
  global_top_k_opportunities: 25;
  selector_audit: SelectorAuditV01;
  ranked_opportunities: MissionOpportunityBlobV01[];
}

export interface SelectorAuditV01 {
  selection_mode: "offline_synthetic_fixture";
  mission_types_considered: MissionTypeV01[];
  mission_types_skipped_by_early_stop: MissionTypeV01[];
  mission_types_sorted_by_descending_ceiling: boolean;
  global_heap_maintained: boolean;
  heap_max_size: 25;
  candidate_blobs_generated: number;
  candidate_blobs_floor_passed: number;
  candidate_blobs_scored: number;
  candidate_blobs_pruned: number;
  final_heap_size: number;
  early_stop_applied: boolean;
  early_stop_reason: string | null;
  remaining_ceiling_at_stop: number | null;
  cutoff_score: number | null;
  floor_failure_examples: SelectorFloorFailureExampleV01[];
  non_generation_reasons: SelectorNonGenerationReasonV01[];
  candidate_generation_summaries: SelectorCandidateGenerationSummaryV01[];
  duplicate_control_summary: SelectorDuplicateControlSummaryV01;
  audit_notes: string[];
}

export interface SelectorFloorFailureExampleV01 {
  mission_type: MissionTypeV01;
  opportunity_id: string;
  failed_requirements: string[];
  fail_reasons: string[];
}

export interface SelectorNonGenerationReasonV01 {
  mission_type: MissionTypeV01;
  reason: string;
  evidence_refs: string[];
}

export interface SelectorCandidateGenerationSummaryV01 {
  mission_type: MissionTypeV01;
  generator_id: string;
  eligible_candidate_count: number;
  emitted_candidate_count: number;
  floor_failed_candidate_count: number;
  pruned_candidate_count: number;
  cap_applied: boolean;
  cap_value: number;
}

export interface SelectorDuplicateControlSummaryV01 {
  exact_duplicate_mission_type_target_count: number;
  duplicate_target_object_count: number;
  mission_type_concentration: SelectorMissionTypeConcentrationEntryV01[];
  suppressed_exact_duplicate_count: number;
  suppressed_duplicate_examples: SelectorSuppressedDuplicateExampleV01[];
}

export interface SelectorMissionTypeConcentrationEntryV01 {
  mission_type: MissionTypeV01;
  count: number;
  share: number;
}

export interface SelectorSuppressedDuplicateExampleV01 {
  mission_type: MissionTypeV01;
  opportunity_id: string;
  duplicate_of_opportunity_id: string;
  target_object_ids: string[];
  reason: string;
}
