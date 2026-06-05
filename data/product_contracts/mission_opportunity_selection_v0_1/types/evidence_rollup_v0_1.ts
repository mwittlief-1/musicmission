import type { TargetObjectTypeV01 } from "./mission_type_registry_v0_1";

export type EvidenceRollupContractVersionV01 = "evidence_rollup_v0_1";

export type EvidenceSourceTypeV01 =
  | "survey"
  | "mission_review"
  | "song_review"
  | "synthetic";

export type RawSignalV01 = "love" | "like" | "ok" | "dislike" | "unknown";

export type SignalClassV01 =
  | "strong_positive"
  | "positive"
  | "weak_non_failure"
  | "negative"
  | "no_signal"
  | "unknown";

export type NodeTierV01 =
  | "primary"
  | "major"
  | "supporting"
  | "deep"
  | "contextual"
  | "gateway"
  | "unknown";

export type GraphItemRoleV01 =
  | "canonical_anchor"
  | "major_representative"
  | "gateway"
  | "bridge"
  | "deep_cut"
  | "contextual_object"
  | "boundary"
  | "false_nearby"
  | "album_world"
  | "artist_anchor"
  | "unknown";

export interface EvidenceRollupV01 {
  contract_version: EvidenceRollupContractVersionV01;
  fixture_status: "synthetic_contract_fixture";
  listener_state_id: string;
  created_at: string;
  runtime_listener_evidence_connected: false;
  canonical_graph_mutation_allowed: false;
  listener_preference_inference_from_affinity_allowed: false;
  reaction_semantics: ReactionSemanticsV01;
  evidence_signals: EvidenceSignalV01[];
  rollups: EvidenceRollupSetsV01;
}

export interface ReactionSemanticsV01 {
  survey_ok_signal_class: "no_signal";
  mission_ok_signal_class: "weak_non_failure";
  mission_ok_is_positive_preference: false;
}

export interface TargetObjectRefV01 {
  object_type: TargetObjectTypeV01;
  object_ids: string[];
  display_name: string;
}

export interface GraphContextV01 {
  target_object_ref: TargetObjectRefV01;
  family_ids: string[];
  family_names: string[];
  archetype_ids: string[];
  archetype_names: string[];
  artist_ids: string[];
  album_ids: string[];
  song_ids: string[];
  node_tier: NodeTierV01;
  graph_item_role: GraphItemRoleV01;
  track_tier_within_archetype: NodeTierV01;
  album_tier_within_archetype: NodeTierV01;
  artist_tier_within_archetype: NodeTierV01;
  context_overlays: string[];
  risk_flags: string[];
  identity_flags: string[];
  provenance: {
    source: string;
    source_refs: string[];
    synthetic_only: boolean;
  };
}

export interface EvidenceSignalV01 {
  evidence_id: string;
  source_type: EvidenceSourceTypeV01;
  raw_signal: RawSignalV01;
  signal_class: SignalClassV01;
  signal_weight: number;
  contributes_to_preference: boolean;
  can_support_non_failure: boolean;
  target_object_ref: TargetObjectRefV01;
  graph_context: GraphContextV01;
  occurred_at: string;
  notes?: string;
}

export interface EvidenceRollupSetsV01 {
  by_family: EvidenceTargetRollupV01[];
  by_archetype: EvidenceTargetRollupV01[];
  by_artist: EvidenceTargetRollupV01[];
  by_album: EvidenceTargetRollupV01[];
  by_song: EvidenceTargetRollupV01[];
}

export interface EvidenceTargetRollupV01 {
  rollup_id: string;
  target_object_ref: TargetObjectRefV01;
  graph_context: GraphContextV01;
  signal_counts: EvidenceSignalCountsV01;
  computed_fields: EvidenceComputedFieldsV01;
  supporting_evidence_ids: string[];
}

export interface EvidenceSignalCountsV01 {
  survey_love: number;
  survey_like: number;
  survey_ok_ignored: number;
  survey_dislike: number;
  mission_love: number;
  mission_like: number;
  mission_ok_weak: number;
  mission_dislike: number;
  song_review_love: number;
  song_review_like: number;
  song_review_ok_weak: number;
  song_review_dislike: number;
  unknown: number;
  total_preference_signals: number;
  total_non_failure_signals: number;
}

export interface EvidenceComputedFieldsV01 {
  evidence_density: number;
  positive_signal_strength: number;
  negative_signal_strength: number;
  weak_non_failure_strength: number;
  conflict_score: number;
  context_variability_score: number;
  context_skew_score: number;
  tier_coverage_score: number;
  tier_depth_score: number;
  coverage_gap_score: number;
  depth_gap_score: number;
  recency_score: number;
  recent_surprise_score: number;
  repetition_count: number;
}
