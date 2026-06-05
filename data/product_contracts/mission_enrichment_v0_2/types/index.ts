export type MissionEnrichmentSchemaVersion = "mission_enrichment_input_v0_2";
export type MissionEnrichmentOutputSchemaVersion = "mission_enrichment_output_v0_2";
export type PrimaryReaction = "love" | "like" | "ok" | "dislike";

export type MissionType =
  | "archetype_depth_test"
  | "artist_depth_test"
  | "album_container_test"
  | "bridge_test"
  | "boundary_test"
  | "context_dependence_test"
  | "contrast_test"
  | "frontier_test"
  | "gateway_test"
  | "recovery_test"
  | "user_requested";

export type RouteRole =
  | "anchor"
  | "probe"
  | "stretch"
  | "boundary"
  | "contrast"
  | "control"
  | "bridge"
  | "context"
  | "comparator";

export type AffinityFacet =
  | "form_container"
  | "melody_harmony"
  | "rhythm_body"
  | "production"
  | "sonic_texture"
  | "vocal_performance"
  | "instrumental_performance"
  | "lyrics_language"
  | "narrative_theme"
  | "emotion_theme"
  | "atmosphere"
  | "energy_profile"
  | "dynamic_shape"
  | "arrangement"
  | "activity_context"
  | "social_context"
  | "context_rule";

export type UserAlignment =
  | "matches_known_positive"
  | "matches_known_negative"
  | "supports_confirmed_pattern"
  | "stretches_known_positive"
  | "tests_boundary"
  | "tests_open_question"
  | "frontier_probe"
  | "contrast_item"
  | "control_item"
  | "recovery_item"
  | "overexposure_check"
  | "novelty_check"
  | "context_dependence_check";

export interface SecondaryReactionTagRegistryEntry {
  tag_id?: string;
  display_label: string;
  valid_primary_reactions: PrimaryReaction[];
  atlas_effect: string;
  allowed_facets: AffinityFacet[];
}

export interface ApplicabilityFlags {
  has_vocals: boolean;
  has_lyrics: boolean;
  lyrics_language_known: boolean;
  is_instrumental: boolean;
  is_live_or_alt_version: boolean;
  album_context_relevant: boolean;
  long_form_context_relevant: boolean;
}

export interface SongAffinityTag {
  tag: string;
  facet: AffinityFacet;
}

export interface UserAlignmentHint {
  tag: string;
  alignment: UserAlignment;
}

export interface MissionEnrichmentRouteItem {
  item_id: string;
  canonical_song_recording_id: string;
  sequence: number;
  title: string;
  artist: string;
  year: number | null;
  route_role: RouteRole;
  why_included: string;
  song_affinity_tags: SongAffinityTag[];
  user_alignment_hints: UserAlignmentHint[];
  prefiltered_secondary_tag_ids: string[];
  applicability_flags: ApplicabilityFlags;
  artist_context_available?: boolean;
}

export interface MissionEnrichmentInputV02 {
  schema_version: MissionEnrichmentSchemaVersion;
  runtime_context: {
    surface: "mission_card_and_feedback_chips";
    mission_ordinal_for_user: number;
    max_secondary_tags_per_song: 6;
    copy_mode: "external_alpha";
    language_style: "clear_warm_music_literate";
    avoid_founder_vocabulary: true;
  };
  user_atlas_context_brief: {
    confirmed_positive_patterns: Array<Record<string, unknown>>;
    open_questions: Array<Record<string, unknown>>;
    known_boundaries: Array<Record<string, unknown>>;
    recent_learning_summary: string[];
    coverage_notes: string[];
  };
  mission_context: {
    mission_id: string;
    mission_type: MissionType;
    risk_level: "low" | "medium" | "high";
    mission_hypothesis: string;
    why_this_mission_now: string;
    success_definition: string;
  };
  route_items: MissionEnrichmentRouteItem[];
  allowed_secondary_reaction_tags: Record<string, SecondaryReactionTagRegistryEntry>;
  copy_guardrails: string[];
}

export interface MissionEnrichmentOutputV02 {
  schema_version: MissionEnrichmentOutputSchemaVersion;
  mission_id: string;
  mission_copy: {
    title: string;
    subtitle: string;
    short_description: string;
    why_now: string;
    listen_for: string[];
    mission_hypothesis_user_facing: string;
  };
  route_item_copy: Array<{
    item_id: string;
    pre_play_line: string;
    why_this_song: string;
    listen_for: string[];
  }>;
  secondary_reaction_tag_candidates: Array<{
    item_id: string;
    tags: Array<{
      tag_id: string;
      rank: number;
      display_label: string;
      valid_primary_reactions: PrimaryReaction[];
      why_this_tag_is_relevant: string;
      linked_song_affinity_tags: string[];
      linked_user_alignment_hints: UserAlignment[];
      atlas_effect: string;
      atlas_signal_target: {
        target_type:
          | "affinity_tag"
          | "pattern"
          | "region"
          | "mission_hypothesis"
          | "boundary"
          | "frontier"
          | "context_rule";
        target_labels: string[];
      };
    }>;
  }>;
  post_completion_interpretation_seeds: Array<{
    condition: "mostly_positive" | "mixed" | "mostly_negative";
    readout_seed: string;
    atlas_inference_hint: string;
  }>;
  internal_quality_notes: {
    used_song_affinity_tags: string[];
    used_alignment_hints: UserAlignment[];
    avoided_overclaims: string[];
    risk_flags: string[];
  };
}
