import type { MissionTypeV01, TargetObjectTypeV01 } from "./mission_type_registry_v0_1";

export type HiddenOracleEvaluationDesignContractVersionV01 =
  "hidden_oracle_evaluation_design_v0_1";

export type HiddenOracleEvaluationMetricNameV01 =
  | "opportunity_relevance"
  | "hidden_hit_rate_proxy"
  | "diagnostic_value"
  | "boundary_discovery_potential"
  | "false_nearby_detection_potential"
  | "context_detection_potential"
  | "overfit_prevention_score"
  | "survey_decay_score"
  | "learning_usefulness_score";

export interface HiddenOracleEvaluationDesignV01 {
  contract_version: HiddenOracleEvaluationDesignContractVersionV01;
  fixture_status: "synthetic_contract_fixture";
  created_at: string;
  phase: "post_selection_oracle_evaluation_design";
  runtime_allowed: false;
  runtime_listener_evidence_connected: false;
  production_mission_generation_allowed: false;
  canonical_graph_mutation_allowed: false;
  listener_preference_inference_from_affinity_allowed: false;
  opportunity_only: true;
  selector_may_read_hidden_oracle: false;
  evaluator_may_read_hidden_oracle_after_selection: true;
  selector_visible_input_ref: string;
  hidden_oracle_ref: string;
  selector_output_refs: string[];
  evaluation_scope: HiddenOracleEvaluationScopeV01;
  metric_definitions: HiddenOracleMetricDefinitionV01[];
  profiles: HiddenOracleProfileEvaluationV01[];
}

export interface HiddenOracleEvaluationScopeV01 {
  evaluation_subject: "selected_opportunity_blobs_only";
  opportunities_per_profile: number;
  construction_simulation_status: "not_implemented";
  candidate_song_selection_status: "not_in_scope";
  hidden_oracle_use: "post_selection_evaluator_only";
  selector_input_rule: "visible_evidence_only";
  allowed_outputs: Array<
    | "opportunity_refs"
    | "oracle_match_summaries"
    | "expected_metric_scores"
    | "aggregate_profile_scores"
    | "evaluation_notes"
  >;
}

export interface HiddenOracleMetricDefinitionV01 {
  metric_name: HiddenOracleEvaluationMetricNameV01;
  meaning: string;
  uses_hidden_oracle: boolean;
  visible_selector_input: boolean;
}

export interface HiddenOracleProfileEvaluationV01 {
  profile_id: string;
  selector_output_ref: string;
  visible_evidence_ref: string;
  hidden_oracle_profile_ref: string;
  visible_expected_top_mission_types: MissionTypeV01[];
  oracle_summary: HiddenOracleSummaryV01;
  top_opportunity_evaluations: HiddenOracleOpportunityEvaluationV01[];
  aggregate_metrics: HiddenOracleMetricScoresV01;
  expected_useful_top_mission_types: MissionTypeV01[];
  notes: string[];
}

export interface HiddenOracleSummaryV01 {
  primary_archetype_ids: string[];
  secondary_archetype_ids: string[];
  anti_archetype_ids: string[];
  false_nearby_lane_id: string;
  false_nearby_archetype_id: string;
  context_lane_id: string;
}

export interface HiddenOracleOpportunityEvaluationV01 {
  selected_opportunity_ref: HiddenOracleSelectedOpportunityRefV01;
  construction_status: "not_constructed";
  production_generation_allowed: false;
  candidate_song_selection_status: "not_in_scope";
  no_candidate_song_list: true;
  oracle_match_summary: HiddenOracleMatchSummaryV01;
  expected_metrics: HiddenOracleMetricScoresV01;
  evaluator_use_only_hidden_refs: string[];
  notes: string[];
}

export interface HiddenOracleSelectedOpportunityRefV01 {
  opportunity_id: string;
  rank: number;
  mission_type: MissionTypeV01;
  target_object_type: TargetObjectTypeV01;
  target_object_ids: string[];
  target_display_name: string;
  final_opportunity_score: number;
}

export interface HiddenOracleMatchSummaryV01 {
  matched_primary_archetype_ids: string[];
  matched_secondary_archetype_ids: string[];
  matched_anti_archetype_ids: string[];
  matched_unknown_target_ids: string[];
  false_nearby_lane_match: boolean;
  context_lane_match: boolean;
  direct_song_reaction_counts: {
    love: number;
    like: number;
    ok: number;
    dont_like: number;
    unknown: number;
  };
}

export interface HiddenOracleMetricScoresV01 {
  opportunity_relevance: number;
  hidden_hit_rate_proxy: number;
  diagnostic_value: number;
  boundary_discovery_potential: number;
  false_nearby_detection_potential: number;
  context_detection_potential: number;
  overfit_prevention_score: number;
  survey_decay_score: number;
  learning_usefulness_score: number;
}
