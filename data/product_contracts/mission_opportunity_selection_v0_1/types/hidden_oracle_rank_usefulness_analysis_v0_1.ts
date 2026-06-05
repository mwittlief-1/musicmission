import type { MissionTypeV01, TargetObjectTypeV01 } from "./mission_type_registry_v0_1";

export type HiddenOracleRankUsefulnessAnalysisContractVersionV01 =
  "hidden_oracle_rank_usefulness_analysis_v0_1";

export type RankUsefulnessAlignmentLabelV01 = "strong" | "mixed" | "weak";

export interface HiddenOracleRankUsefulnessAnalysisV01 {
  contract_version: HiddenOracleRankUsefulnessAnalysisContractVersionV01;
  fixture_status: "synthetic_contract_fixture";
  created_at: string;
  phase: "hidden_oracle_rank_usefulness_analysis";
  runtime_allowed: false;
  runtime_listener_evidence_connected: false;
  production_mission_generation_allowed: false;
  canonical_graph_mutation_allowed: false;
  listener_preference_inference_from_affinity_allowed: false;
  opportunity_only: true;
  selector_may_read_hidden_oracle: false;
  evaluator_may_read_hidden_oracle_after_selection: true;
  source_hidden_oracle_evaluation_design_ref: string;
  analysis_scope: RankUsefulnessAnalysisScopeV01;
  aggregate_summary: RankUsefulnessAggregateSummaryV01;
  profiles: RankUsefulnessProfileAnalysisV01[];
}

export interface RankUsefulnessAnalysisScopeV01 {
  analysis_subject: "selected_opportunity_rank_order";
  rank_window: number;
  rank_score_field: "selected_opportunity_ref.final_opportunity_score";
  usefulness_score_field: "expected_metrics.learning_usefulness_score";
  hidden_oracle_use: "post_selection_metrics_only";
  selector_input_rule: "visible_evidence_only";
  construction_simulation_status: "not_implemented";
  candidate_song_selection_status: "not_in_scope";
  allowed_outputs: Array<
    | "rank_rows"
    | "rank_usefulness_metrics"
    | "mission_type_usefulness_summary"
    | "aggregate_rank_alignment"
    | "review_notes"
  >;
}

export interface RankUsefulnessAggregateSummaryV01 {
  profile_count: number;
  mean_top1_learning_usefulness_score: number;
  mean_best_learning_usefulness_score: number;
  mean_rank_regret: number;
  top1_is_best_count: number;
  best_in_top3_count: number;
  best_in_top5_count: number;
  mean_spearman_rank_correlation: number;
  mean_ndcg_at_3: number;
  mean_ndcg_at_5: number;
  mean_ndcg_at_10: number;
  alignment_label: RankUsefulnessAlignmentLabelV01;
  aggregate_findings: string[];
}

export interface RankUsefulnessProfileAnalysisV01 {
  profile_id: string;
  selector_output_ref: string;
  evaluation_design_profile_ref: string;
  rank_window: number;
  top_selector_opportunity: RankUsefulnessOpportunityRefV01;
  best_oracle_usefulness_opportunity: RankUsefulnessOpportunityRefV01;
  top1_learning_usefulness_score: number;
  best_learning_usefulness_score: number;
  rank_regret: number;
  best_usefulness_rank: number;
  top1_is_best: boolean;
  best_in_top3: boolean;
  best_in_top5: boolean;
  spearman_rank_correlation: number;
  ndcg_at_3: number;
  ndcg_at_5: number;
  ndcg_at_10: number;
  rank_rows: RankUsefulnessRankRowV01[];
  mission_type_usefulness_summary: RankUsefulnessMissionTypeSummaryV01[];
  diagnostic_findings: string[];
  recommended_selector_tuning_notes: string[];
}

export interface RankUsefulnessOpportunityRefV01 {
  opportunity_id: string;
  rank: number;
  mission_type: MissionTypeV01;
  target_object_type: TargetObjectTypeV01;
  target_object_ids: string[];
  target_display_name: string;
  selector_score: number;
  learning_usefulness_score: number;
}

export interface RankUsefulnessRankRowV01 {
  rank: number;
  opportunity_id: string;
  mission_type: MissionTypeV01;
  target_display_name: string;
  selector_score: number;
  learning_usefulness_score: number;
  usefulness_rank: number;
  usefulness_delta_from_top1: number;
  oracle_match_tags: string[];
}

export interface RankUsefulnessMissionTypeSummaryV01 {
  mission_type: MissionTypeV01;
  count: number;
  best_selector_rank: number;
  best_usefulness_rank: number;
  mean_learning_usefulness_score: number;
  max_learning_usefulness_score: number;
}
