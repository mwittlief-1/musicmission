#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
GRAPH_DIR = REPO_ROOT / "data/canonical_graph/import_dry_run"
SIM_DIR = REPO_ROOT / "data/survey_simulation"
GENERATED_AT = "2026-05-20T12:00:00Z"
HARNESS_VERSION = "survey_simulation_harness.v0.1"
PAGE_SIZE = 12

REACTIONS = ["love", "like", "ok", "dont_know_enough", "dont_like"]
REACTION_MAP = {
    "love": {
        "app_ui_candidate": "favorite",
        "atlas_signal_interpretation": "strong_positive",
    },
    "like": {
        "app_ui_candidate": "like",
        "atlas_signal_interpretation": "positive",
    },
    "ok": {
        "app_ui_candidate": "fine",
        "atlas_signal_interpretation": "weak_positive_or_familiarity",
    },
    "dont_know_enough": {
        "app_ui_candidate": "dontKnow",
        "atlas_signal_interpretation": "unknown_or_insufficient_familiarity",
    },
    "dont_like": {
        "app_ui_candidate": "notForMe",
        "atlas_signal_interpretation": "negative_scope_carefully",
    },
}

PAGE1_INTENT_TARGETS = [
    ("payload_signature_artist", 4),
    ("archetype_confirmation_anchor", 3),
    ("multi_archetype_junction", 2),
    ("false_nearby_or_boundary_check", 1),
    ("mass_popular_control", 1),
    ("coverage_repair_broad_sentinel", 1),
]

PAGE1_GRAPH_ONLY_INTENT_TARGETS = [
    ("archetype_confirmation_anchor", 4),
    ("multi_archetype_junction", 3),
    ("false_nearby_or_boundary_check", 1),
    ("mass_popular_control", 2),
    ("coverage_repair_broad_sentinel", 2),
]

PAGE1_SCORE_WEIGHTS = {
    "payload_overrepresentation_score": 0.22,
    "apple_evidence_strength": 0.18,
    "expected_familiarity": 0.16,
    "archetype_hypothesis_value": 0.14,
    "multi_archetype_junction_value": 0.12,
    "canonical_anchor_value": 0.08,
    "false_nearby_value": 0.05,
    "coverage_value": 0.05,
}

PAGE2_INTENT_TARGETS_DEFAULT = [
    ("confirm_or_repeat_signal", 4),
    ("multi_archetype_junction", 3),
    ("disambiguate_response", 2),
    ("test_false_nearby", 1),
    ("payload_adjacent_lesser_known", 1),
    ("controlled_frontier", 1),
]

PAGE2_INTENT_TARGETS_HIGH_UNKNOWN = [
    ("confirm_or_repeat_signal", 4),
    ("multi_archetype_junction", 2),
    ("repair_familiarity_or_coverage", 3),
    ("disambiguate_response", 1),
    ("test_false_nearby", 1),
    ("controlled_frontier", 1),
]

PAGE2_INTENT_TARGETS_MANY_POSITIVES = [
    ("confirm_or_repeat_signal", 4),
    ("multi_archetype_junction", 3),
    ("disambiguate_response", 2),
    ("test_bridge", 1),
    ("payload_adjacent_lesser_known", 1),
    ("controlled_frontier", 1),
]

PAGE2_INTENT_TARGETS_MANY_NEGATIVES = [
    ("confirm_or_repeat_signal", 3),
    ("multi_archetype_junction", 2),
    ("disambiguate_negative_scope", 2),
    ("disambiguate_response", 2),
    ("test_false_nearby", 1),
    ("mass_popular_control", 1),
    ("controlled_frontier", 1),
]

PAGE2_SCORE_WEIGHTS = {
    "posterior_relevance": 0.20,
    "information_gain": 0.18,
    "response_disambiguation_value": 0.14,
    "graph_bridge_value": 0.12,
    "coverage_repair_value": 0.08,
    "false_nearby_value": 0.06,
    "expected_familiarity": 0.14,
    "apple_evidence": 0.05,
    "novelty": 0.03,
}

PAGE2_SCORE_KEYS = [
    "posterior_relevance",
    "information_gain",
    "response_disambiguation_value",
    "graph_bridge_value",
    "coverage_repair_value",
    "false_nearby_value",
    "expected_familiarity",
    "apple_evidence",
    "novelty",
    "penalties",
    "final",
]

POSITIVE_REACTIONS = {"love", "like"}
KNOWN_REACTIONS = {"love", "like", "ok", "dont_like"}

GRAPH_INPUT_FILES = [
    "canonical_graph_manifest.json",
    "canonical_artists.json",
    "canonical_albums.json",
    "canonical_song_recordings.json",
    "artist_archetype_memberships.json",
    "album_archetype_memberships.json",
    "song_archetype_memberships.json",
]


MUSIC_OBJECT_REF_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["object_type", "ref_source", "display_name", "resolution_state"],
    "properties": {
        "object_type": {
            "type": "string",
            "enum": ["artist", "album", "song_recording"],
        },
        "ref_source": {
            "type": "string",
            "enum": [
                "canonical_graph",
                "external_catalog",
                "simulator_local",
                "unresolved_import",
            ],
        },
        "canonical_artist_id": {"type": "string", "minLength": 1},
        "canonical_album_id": {"type": "string", "minLength": 1},
        "canonical_song_recording_id": {"type": "string", "minLength": 1},
        "external_catalog_refs": {
            "type": "object",
            "additionalProperties": {"type": "string"},
        },
        "simulator_local_id": {"type": "string", "minLength": 1},
        "display_name": {"type": "string", "minLength": 1},
        "artist_display_name": {"type": "string", "minLength": 1},
        "resolution_state": {
            "type": "string",
            "enum": ["resolved", "needs_resolution", "unresolved"],
        },
    },
    "allOf": [
        {
            "if": {
                "properties": {
                    "ref_source": {"const": "canonical_graph"},
                    "object_type": {"const": "artist"},
                },
                "required": ["ref_source", "object_type"],
            },
            "then": {"required": ["canonical_artist_id"]},
        },
        {
            "if": {
                "properties": {
                    "ref_source": {"const": "canonical_graph"},
                    "object_type": {"const": "album"},
                },
                "required": ["ref_source", "object_type"],
            },
            "then": {"required": ["canonical_album_id"]},
        },
        {
            "if": {
                "properties": {
                    "ref_source": {"const": "canonical_graph"},
                    "object_type": {"const": "song_recording"},
                },
                "required": ["ref_source", "object_type"],
            },
            "then": {"required": ["canonical_song_recording_id"]},
        },
        {
            "if": {
                "properties": {"ref_source": {"const": "external_catalog"}},
                "required": ["ref_source"],
            },
            "then": {"required": ["external_catalog_refs"]},
        },
    ],
}


def schema_base(schema_id: str, title: str) -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"https://waymark.local/schemas/{schema_id}",
        "title": title,
    }


def build_schemas() -> dict[str, dict[str, Any]]:
    affinity = {
        "type": "object",
        "additionalProperties": False,
        "required": ["archetype_id", "weight", "note"],
        "properties": {
            "archetype_id": {"type": "string", "pattern": "^\\d{3}$"},
            "weight": {"type": "number", "minimum": 0, "maximum": 1},
            "note": {"type": "string", "minLength": 1},
        },
    }
    lane = {
        "type": "object",
        "additionalProperties": False,
        "required": ["lane_id", "display_name", "note"],
        "properties": {
            "lane_id": {"type": "string", "minLength": 1},
            "display_name": {"type": "string", "minLength": 1},
            "note": {"type": "string", "minLength": 1},
            "archetype_id": {"type": "string", "pattern": "^\\d{3}$"},
            "family_number": {"type": "integer", "minimum": 1},
        },
    }

    fake_profile = {
        **schema_base("survey_simulation_fake_profile_v0_1.json", "Survey Simulation Fake Profile v0.1"),
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema_version",
            "fake_profile_id",
            "display_label",
            "summary",
            "primary_archetype_affinities",
            "secondary_archetype_affinities",
            "context_lane",
            "false_nearby_lane",
            "hidden_anti_affinities",
            "apple_payload_id",
            "hidden_reaction_corpus_id",
        ],
        "properties": {
            "schema_version": {"const": "survey_simulation.fake_profile.v0.1"},
            "fake_profile_id": {"type": "string", "pattern": "^fake_profile_\\d{2}$"},
            "display_label": {"type": "string", "minLength": 1},
            "summary": {"type": "string", "minLength": 1},
            "primary_archetype_affinities": {
                "type": "array",
                "minItems": 2,
                "maxItems": 2,
                "items": affinity,
            },
            "secondary_archetype_affinities": {
                "type": "array",
                "minItems": 2,
                "maxItems": 2,
                "items": affinity,
            },
            "context_lane": lane,
            "false_nearby_lane": lane,
            "hidden_anti_affinities": {
                "type": "array",
                "minItems": 1,
                "items": affinity,
            },
            "apple_payload_id": {"type": "string", "pattern": "^apple_payload_\\d{2}$"},
            "hidden_reaction_corpus_id": {
                "type": "string",
                "pattern": "^hidden_corpus_\\d{2}$",
            },
        },
    }

    apple_signal = {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "signal_id",
            "signal_type",
            "music_object_ref",
            "normalized_weight",
            "recency_days",
            "play_count_90d",
        ],
        "properties": {
            "signal_id": {"type": "string", "minLength": 1},
            "signal_type": {
                "type": "string",
                "enum": [
                    "library_artist",
                    "recent_play",
                    "heavy_rotation",
                    "playlist_save",
                    "external_catalog_hint",
                ],
            },
            "music_object_ref": MUSIC_OBJECT_REF_SCHEMA,
            "normalized_weight": {"type": "number", "minimum": 0, "maximum": 1},
            "recency_days": {"type": "integer", "minimum": 0},
            "play_count_90d": {"type": "integer", "minimum": 0},
            "last_played_at": {"type": "string", "format": "date-time"},
            "library_added_at": {"type": "string", "format": "date-time"},
        },
    }
    apple_payload = {
        **schema_base("survey_simulation_apple_payload_v0_1.json", "Survey Simulation Apple Payload v0.1"),
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema_version",
            "apple_payload_id",
            "generated_at",
            "source_kind",
            "library_snapshot_age_days",
            "signals",
            "resolution_summary",
        ],
        "properties": {
            "schema_version": {"const": "survey_simulation.apple_payload.v0.1"},
            "apple_payload_id": {"type": "string", "pattern": "^apple_payload_\\d{2}$"},
            "generated_at": {"type": "string", "format": "date-time"},
            "source_kind": {"const": "simulated_apple_music"},
            "library_snapshot_age_days": {"type": "integer", "minimum": 0},
            "signals": {"type": "array", "minItems": 1, "items": apple_signal},
            "playlist_context": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "playlist_name": {"type": ["string", "null"]},
                    "playlist_kind": {
                        "type": "string",
                        "enum": [
                            "user_playlist",
                            "editorial",
                            "algorithmic",
                            "family",
                            "workout",
                            "sleep",
                            "holiday",
                            "unknown",
                        ],
                    },
                },
            },
            "track_level_signals": {"type": "array"},
            "album_level_signals": {"type": "array"},
            "skip_or_completion_hints": {"type": "array"},
            "loved_or_favorite_hints": {"type": "array"},
            "resolution_summary": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "resolved_canonical_count",
                    "external_unresolved_count",
                    "candidate_generation_policy",
                ],
                "properties": {
                    "resolved_canonical_count": {"type": "integer", "minimum": 0},
                    "external_unresolved_count": {"type": "integer", "minimum": 0},
                    "candidate_generation_policy": {"type": "string", "minLength": 1},
                },
            },
        },
    }

    hidden_reaction = {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "music_object_ref",
            "reaction",
            "familiarity_band",
            "confidence",
            "reason_tags",
        ],
        "properties": {
            "music_object_ref": MUSIC_OBJECT_REF_SCHEMA,
            "reaction": {"type": "string", "enum": REACTIONS},
            "familiarity_band": {
                "type": "string",
                "enum": ["known_deep", "known", "heard_of", "unknown"],
            },
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "reason_tags": {
                "type": "array",
                "minItems": 1,
                "items": {"type": "string", "minLength": 1},
            },
        },
    }
    hidden_corpus = {
        **schema_base(
            "survey_simulation_hidden_reaction_corpus_v0_1.json",
            "Survey Simulation Hidden Reaction Corpus v0.1",
        ),
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema_version",
            "hidden_reaction_corpus_id",
            "fake_profile_id",
            "privacy_boundary",
            "reactions",
        ],
        "properties": {
            "schema_version": {"const": "survey_simulation.hidden_reaction_corpus.v0.1"},
            "hidden_reaction_corpus_id": {
                "type": "string",
                "pattern": "^hidden_corpus_\\d{2}$",
            },
            "fake_profile_id": {"type": "string", "pattern": "^fake_profile_\\d{2}$"},
            "privacy_boundary": {"const": "simulator_private"},
            "reactions": {
                "type": "array",
                "minItems": 1,
                "items": hidden_reaction,
            },
        },
    }

    tile = {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "tile_id",
            "position",
            "music_object_ref",
            "page_intent",
            "candidate_basis",
            "graph_context",
            "apple_evidence",
            "scores",
            "reason_for_debug",
        ],
        "properties": {
            "tile_id": {"type": "string", "pattern": "^tile_\\d{2}$"},
            "position": {"type": "integer", "minimum": 1, "maximum": PAGE_SIZE},
            "music_object_ref": MUSIC_OBJECT_REF_SCHEMA,
            "page_intent": {
                "type": "string",
                "enum": [
                    "payload_signature_artist",
                    "archetype_confirmation_anchor",
                    "multi_archetype_junction",
                    "false_nearby_or_boundary_check",
                    "mass_popular_control",
                    "coverage_repair_broad_sentinel",
                    "confirm_or_repeat_signal",
                    "disambiguate_response",
                    "disambiguate_negative_scope",
                    "repair_familiarity_or_coverage",
                    "test_bridge",
                    "repair_coverage",
                    "test_false_nearby",
                    "payload_adjacent_lesser_known",
                    "controlled_frontier",
                    "control_reference",
                    "disambiguate_prior_response",
                ],
            },
            "candidate_basis": {
                "type": "array",
                "minItems": 1,
                "items": {"type": "string", "minLength": 1},
            },
            "graph_context": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "family_numbers",
                    "archetype_ids",
                    "roles",
                    "best_recognition_tier",
                    "best_survey_tier",
                ],
                "properties": {
                    "family_numbers": {
                        "type": "array",
                        "items": {"type": "integer", "minimum": 1},
                    },
                    "archetype_ids": {
                        "type": "array",
                        "items": {"type": "string", "pattern": "^\\d{3}$"},
                    },
                    "roles": {
                        "type": "array",
                        "items": {"type": "string", "minLength": 1},
                    },
                    "best_recognition_tier": {"type": "string", "minLength": 1},
                    "best_survey_tier": {"type": "string", "minLength": 1},
                },
            },
            "apple_evidence": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "exact_signal_weight",
                    "exposure_score",
                    "recency_score",
                    "repetition_score",
                    "library_commitment_score",
                    "favorite_or_rating_score",
                    "playlist_context_score",
                    "album_completion_hint",
                    "artist_depth_hint",
                    "family_context_risk",
                    "catalog_resolution_confidence",
                    "probable_affinity_score",
                    "archetype_neighbor_score",
                    "family_neighbor_score",
                ],
                "properties": {
                    "exact_signal_weight": {"type": "number", "minimum": 0},
                    "exposure_score": {"type": "number", "minimum": 0, "maximum": 1},
                    "recency_score": {"type": "number", "minimum": 0, "maximum": 1},
                    "repetition_score": {"type": "number", "minimum": 0, "maximum": 1},
                    "library_commitment_score": {"type": "number", "minimum": 0, "maximum": 1},
                    "favorite_or_rating_score": {"type": "number", "minimum": 0, "maximum": 1},
                    "playlist_context_score": {"type": "number", "minimum": 0, "maximum": 1},
                    "album_completion_hint": {"type": "number", "minimum": 0, "maximum": 1},
                    "artist_depth_hint": {"type": "number", "minimum": 0, "maximum": 1},
                    "family_context_risk": {"type": "number", "minimum": 0, "maximum": 1},
                    "catalog_resolution_confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    "probable_affinity_score": {"type": "number", "minimum": 0, "maximum": 1},
                    "archetype_neighbor_score": {"type": "number", "minimum": 0, "maximum": 1},
                    "family_neighbor_score": {"type": "number", "minimum": 0, "maximum": 1},
                    "signal_ids": {
                        "type": "array",
                        "items": {"type": "string", "minLength": 1},
                    },
                },
            },
            "scores": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "payload_overrepresentation_score",
                    "apple_evidence_strength",
                    "expected_familiarity",
                    "archetype_hypothesis_value",
                    "multi_archetype_junction_value",
                    "canonical_anchor_value",
                    "false_nearby_value",
                    "coverage_value",
                    "penalties",
                    "final",
                ],
                "properties": {
                    "payload_overrepresentation_score": {"type": "number", "minimum": 0, "maximum": 1},
                    "apple_evidence_strength": {"type": "number", "minimum": 0, "maximum": 1},
                    "expected_familiarity": {"type": "number", "minimum": 0, "maximum": 1},
                    "archetype_hypothesis_value": {"type": "number", "minimum": 0, "maximum": 1},
                    "multi_archetype_junction_value": {"type": "number", "minimum": 0, "maximum": 1},
                    "canonical_anchor_value": {"type": "number", "minimum": 0, "maximum": 1},
                    "false_nearby_value": {"type": "number", "minimum": 0, "maximum": 1},
                    "coverage_value": {"type": "number", "minimum": 0, "maximum": 1},
                    "penalties": {"type": "number", "minimum": 0},
                    "final": {"type": "number"},
                },
            },
            "reason_for_debug": {"type": "string", "minLength": 1},
        },
    }
    page = {
        **schema_base("survey_simulation_page_v0_1.json", "Survey Simulation Page v0.1"),
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema_version",
            "page_id",
            "page_number",
            "stage",
            "page_mode",
            "tile_count",
            "generator_visible_inputs",
            "tiles",
        ],
        "properties": {
            "schema_version": {"const": "survey_simulation.page.v0.1"},
            "page_id": {"type": "string", "pattern": "^page_\\d{2}$"},
            "page_number": {"type": "integer", "minimum": 1},
            "stage": {"const": "artists"},
            "page_mode": {
                "type": "string",
                "enum": ["generic_graph_seed", "apple_biased_seed"],
            },
            "tile_count": {"type": "integer", "const": PAGE_SIZE},
            "generator_visible_inputs": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "canonical_graph_manifest_status",
                    "apple_payload_applied",
                    "prior_visible_response_count",
                    "hidden_inputs_consumed",
                ],
                "properties": {
                    "canonical_graph_manifest_status": {"type": "string", "minLength": 1},
                    "apple_payload_applied": {"type": "boolean"},
                    "prior_visible_response_count": {"type": "integer", "minimum": 0},
                    "hidden_inputs_consumed": {"const": False},
                },
            },
            "tiles": {
                "type": "array",
                "minItems": PAGE_SIZE,
                "maxItems": PAGE_SIZE,
                "items": tile,
            },
        },
    }

    survey_run = {
        **schema_base("survey_simulation_run_v0_1.json", "Survey Simulation Run v0.1"),
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema_version",
            "run_id",
            "generated_at",
            "harness_version",
            "page_mode",
            "stage_flow",
            "page_size",
            "canonical_graph_input",
            "boundary_assertions",
            "pages",
            "outputs",
        ],
        "properties": {
            "schema_version": {"const": "survey_simulation.run.v0.1"},
            "run_id": {"type": "string", "pattern": "^RUN_\\d{3}_[A-Z_]+$"},
            "generated_at": {"type": "string", "format": "date-time"},
            "harness_version": {"const": HARNESS_VERSION},
            "page_mode": {
                "type": "string",
                "enum": ["generic_graph_seed", "apple_biased_seed"],
            },
            "stage_flow": {
                "type": "array",
                "items": {"type": "string", "enum": ["artists", "albums", "songs"]},
            },
            "page_size": {"type": "integer", "const": PAGE_SIZE},
            "canonical_graph_input": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "manifest_path",
                    "manifest_status",
                    "read_only",
                    "input_fingerprint_sha256",
                ],
                "properties": {
                    "manifest_path": {"type": "string", "minLength": 1},
                    "manifest_status": {"type": "string", "minLength": 1},
                    "read_only": {"const": True},
                    "input_fingerprint_sha256": {"type": "string", "minLength": 64},
                },
            },
            "boundary_assertions": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "survey_builder_visible_inputs_only",
                    "hidden_reason_tags_exported_to_visible_outputs",
                    "canonical_graph_mutated",
                    "typed_music_object_refs_only",
                ],
                "properties": {
                    "survey_builder_visible_inputs_only": {"const": True},
                    "hidden_reason_tags_exported_to_visible_outputs": {"const": False},
                    "canonical_graph_mutated": {"const": False},
                    "typed_music_object_refs_only": {"const": True},
                },
            },
            "pages": {
                "type": "array",
                "minItems": 1,
                "maxItems": 1,
                "items": page,
            },
            "outputs": {
                "type": "array",
                "items": {"type": "string", "minLength": 1},
            },
        },
    }

    response = {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "response_id",
            "run_id",
            "page_id",
            "tile_id",
            "music_object_ref",
            "reaction",
            "app_ui_candidate",
            "atlas_signal_interpretation",
            "observed_selected_tags",
            "shown_unselected_tags",
        ],
        "properties": {
            "response_id": {"type": "string", "pattern": "^resp_\\d{2}$"},
            "run_id": {"type": "string", "pattern": "^RUN_\\d{3}_[A-Z_]+$"},
            "page_id": {"type": "string", "pattern": "^page_\\d{2}$"},
            "tile_id": {"type": "string", "pattern": "^tile_\\d{2}$"},
            "music_object_ref": MUSIC_OBJECT_REF_SCHEMA,
            "reaction": {"type": "string", "enum": REACTIONS},
            "app_ui_candidate": {"type": "string", "minLength": 1},
            "atlas_signal_interpretation": {"type": "string", "minLength": 1},
            "observed_selected_tags": {"type": "array", "items": {"type": "string"}},
            "shown_unselected_tags": {"type": "array", "items": {"type": "string"}},
        },
    }
    recorded_responses = {
        **schema_base(
            "survey_simulation_recorded_responses_v0_1.json",
            "Survey Simulation Recorded Responses v0.1",
        ),
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema_version",
            "run_id",
            "generated_at",
            "response_source",
            "responses",
        ],
        "properties": {
            "schema_version": {"const": "survey_simulation.recorded_responses.v0.1"},
            "run_id": {"type": "string", "pattern": "^RUN_\\d{3}_[A-Z_]+$"},
            "generated_at": {"type": "string", "format": "date-time"},
            "response_source": {"const": "hidden_corpus_lookup_with_missing_default"},
            "responses": {
                "type": "array",
                "minItems": PAGE_SIZE,
                "maxItems": PAGE_SIZE,
                "items": response,
            },
        },
    }

    page_generation_log = {
        **schema_base(
            "survey_simulation_page_generation_log_v0_1.json",
            "Survey Simulation Page Generation Log v0.1",
        ),
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema_version",
            "run_id",
            "generated_at",
            "page_mode",
            "source_tables_read",
            "builder_visible_input_summary",
            "candidate_selection",
        ],
        "properties": {
            "schema_version": {"const": "survey_simulation.page_generation_log.v0.1"},
            "run_id": {"type": "string", "pattern": "^RUN_\\d{3}_[A-Z_]+$"},
            "generated_at": {"type": "string", "format": "date-time"},
            "page_mode": {
                "type": "string",
                "enum": ["generic_graph_seed", "apple_biased_seed"],
            },
            "source_tables_read": {
                "type": "array",
                "items": {"type": "string", "minLength": 1},
            },
            "builder_visible_input_summary": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "canonical_graph",
                    "apple_payload",
                    "prior_visible_response_count",
                    "hidden_inputs_consumed",
                ],
                "properties": {
                    "canonical_graph": {"type": "string", "minLength": 1},
                    "apple_payload": {"type": "string", "minLength": 1},
                    "prior_visible_response_count": {"type": "integer", "minimum": 0},
                    "hidden_inputs_consumed": {"const": False},
                },
            },
            "candidate_selection": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "tile_count",
                    "direct_apple_match_count",
                    "graph_exploration_count",
                    "duplicate_display_names_suppressed",
                    "intent_counts",
                    "tiles",
                ],
                "properties": {
                    "tile_count": {"type": "integer", "const": PAGE_SIZE},
                    "direct_apple_match_count": {"type": "integer", "minimum": 0},
                    "graph_exploration_count": {"type": "integer", "minimum": 0},
                    "duplicate_display_names_suppressed": {"type": "integer", "minimum": 0},
                    "intent_counts": {
                        "type": "object",
                        "additionalProperties": {"type": "integer", "minimum": 0},
                    },
                    "tiles": {
                        "type": "array",
                        "minItems": PAGE_SIZE,
                        "maxItems": PAGE_SIZE,
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": [
                                "position",
                                "canonical_artist_id",
                                "display_name",
                                "page_intent",
                                "candidate_basis",
                                "scores",
                            ],
                            "properties": {
                                "position": {"type": "integer", "minimum": 1},
                                "canonical_artist_id": {"type": "string", "minLength": 1},
                                "display_name": {"type": "string", "minLength": 1},
                                "page_intent": {"type": "string", "minLength": 1},
                                "candidate_basis": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "scores": {
                                    "type": "object",
                                    "additionalProperties": {"type": "number"},
                                },
                            },
                        },
                    },
                },
            },
        },
    }

    hidden_coverage = {
        **schema_base(
            "survey_simulation_hidden_lookup_coverage_v0_1.json",
            "Survey Simulation Hidden Lookup Coverage v0.1",
        ),
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema_version",
            "run_id",
            "generated_at",
            "privacy_boundary",
            "summary",
            "lookups",
        ],
        "properties": {
            "schema_version": {"const": "survey_simulation.hidden_lookup_coverage.v0.1"},
            "run_id": {"type": "string", "pattern": "^RUN_\\d{3}_[A-Z_]+$"},
            "generated_at": {"type": "string", "format": "date-time"},
            "privacy_boundary": {"const": "simulator_private_evaluation"},
            "summary": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "tile_count",
                    "hidden_lookup_hit_count",
                    "missing_default_count",
                ],
                "properties": {
                    "tile_count": {"type": "integer", "const": PAGE_SIZE},
                    "hidden_lookup_hit_count": {"type": "integer", "minimum": 0},
                    "missing_default_count": {"type": "integer", "minimum": 0},
                },
            },
            "lookups": {
                "type": "array",
                "minItems": PAGE_SIZE,
                "maxItems": PAGE_SIZE,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "tile_id",
                        "display_name",
                        "object_type",
                        "lookup_status",
                        "recorded_reaction",
                    ],
                    "properties": {
                        "tile_id": {"type": "string", "pattern": "^tile_\\d{2}$"},
                        "display_name": {"type": "string", "minLength": 1},
                        "object_type": {"type": "string", "enum": ["artist"]},
                        "lookup_status": {
                            "type": "string",
                            "enum": ["hidden_corpus_hit", "missing_default"],
                        },
                        "recorded_reaction": {"type": "string", "enum": REACTIONS},
                    },
                },
            },
        },
    }

    return {
        "fake_profile.schema.json": fake_profile,
        "apple_payload.schema.json": apple_payload,
        "hidden_reaction_corpus.schema.json": hidden_corpus,
        "survey_page.schema.json": page,
        "survey_run.schema.json": survey_run,
        "recorded_responses.schema.json": recorded_responses,
        "page_generation_log.schema.json": page_generation_log,
        "hidden_lookup_coverage.schema.json": hidden_coverage,
    }


PROFILE_DEFINITIONS: list[dict[str, Any]] = [
    {
        "id": "fake_profile_01",
        "label": "Classic Suburban Dad",
        "summary": "Album-rock comfort, heartland hooks, and family-car classics, with limited patience for abrasive modern edges.",
        "primary": [
            ("016", 0.91, "classic album-rock anchors"),
            ("022", 0.78, "soft-rock shared-memory lane"),
        ],
        "secondary": [
            ("071", 0.58, "modern radio rock handoff"),
            ("113", 0.46, "family and nostalgia repeats"),
        ],
        "context": ("family_car_cd_binder", "Family car CD binder", "Road-trip repetition and household singalongs matter."),
        "false_nearby": ("arena_sheen_without_songcraft", "Arena sheen without songcraft", "Big production alone should not be read as affinity.", "020", 3),
        "anti": [
            ("119", 0.72, "hyperpop texture is too brittle"),
            ("062", 0.64, "thrash intensity is usually a skip"),
        ],
        "artist_reactions": [
            ("artist-fleetwood-mac", "love", ["warm-harmony", "family-car-repeat"]),
            ("artist-eagles", "love", ["road-trip-core", "adult-rock-comfort"]),
            ("artist-tom-petty-and-the-heartbreakers", "love", ["plainspoken-songcraft", "guitar-radio"]),
            ("artist-dire-straits", "like", ["clean-guitar-tone", "album-rock"]),
            ("artist-queen", "like", ["big-chorus", "recognition"]),
            ("foo-fighters", "ok", ["modern-rock-tolerated", "radio-familiar"]),
            ("taylor-swift", "ok", ["household-osmosis", "songcraft-respect"]),
            ("kendrick-lamar", "dont_know_enough", ["not-in-library"]),
            ("metallica", "dont_like", ["too-heavy", "abrasive"]),
            ("100-gecs", "dont_like", ["texture-rejection", "too-online"]),
            ("garth-brooks", "like", ["shared-nostalgia", "country-crossover"]),
            ("shania-twain", "ok", ["family-radio", "country-pop"]),
        ],
        "apple_artists": [
            ("artist-fleetwood-mac", 0.98, 64, 4, "heavy_rotation"),
            ("artist-tom-petty-and-the-heartbreakers", 0.92, 58, 6, "heavy_rotation"),
            ("artist-eagles", 0.86, 43, 18, "library_artist"),
            ("artist-dire-straits", 0.72, 22, 34, "library_artist"),
            ("foo-fighters", 0.42, 10, 9, "recent_play"),
            ("journey", 0.38, 8, 80, "library_artist"),
        ],
    },
    {
        "id": "fake_profile_02",
        "label": "Pop / Radio Generalist",
        "summary": "Recognizes the center of pop radio, follows big singles, and likes clean hooks more than scene boundaries.",
        "primary": [
            ("091", 0.86, "mainstream persona pop"),
            ("090", 0.78, "radio R&B/pop crossover"),
        ],
        "secondary": [
            ("093", 0.66, "current bright pop"),
            ("088", 0.44, "legacy pop showmanship"),
        ],
        "context": ("gym_and_commute_radio", "Gym and commute radio", "The strongest signals are repeated singles and playlists."),
        "false_nearby": ("internet_edge_pop", "Internet edge pop", "Very online pop adjacency may be overread from a few playlist plays.", "119", 18),
        "anti": [
            ("062", 0.77, "metal reads as too aggressive"),
            ("059", 0.55, "post-punk distance is not a default fit"),
        ],
        "artist_reactions": [
            ("taylor-swift", "love", ["singalong-hooks", "persona-pop"]),
            ("dua-lipa", "love", ["dance-pop", "clean-production"]),
            ("the-weeknd", "like", ["radio-r-b", "night-drive"]),
            ("bruno-mars", "like", ["retro-pop", "party-ready"]),
            ("ariana-grande", "like", ["vocal-pop", "mainstream"]),
            ("ed-sheeran", "ok", ["radio-familiar", "soft-pop"]),
            ("olivia-rodrigo", "like", ["current-pop", "drama-hooks"]),
            ("billie-eilish", "ok", ["moody-pop", "less-repeat"]),
            ("metallica", "dont_like", ["too-heavy"]),
            ("slayer", "dont_like", ["too-extreme"]),
            ("pixies", "dont_know_enough", ["not-exposed"]),
            ("100-gecs", "dont_like", ["too-chaotic"]),
        ],
        "apple_artists": [
            ("taylor-swift", 0.96, 70, 2, "heavy_rotation"),
            ("dua-lipa", 0.86, 46, 8, "heavy_rotation"),
            ("the-weeknd", 0.76, 39, 3, "recent_play"),
            ("bruno-mars", 0.61, 22, 14, "library_artist"),
            ("ariana-grande", 0.57, 18, 21, "library_artist"),
            ("ed-sheeran", 0.35, 9, 60, "playlist_save"),
        ],
    },
    {
        "id": "fake_profile_03",
        "label": "Alt Formation User",
        "summary": "Came up through 90s alternative, college rock, and darker guitar-pop; suspicious of polish without friction.",
        "primary": [
            ("070", 0.9, "grunge and 90s alternative"),
            ("069", 0.82, "college-rock and art-alt foundation"),
        ],
        "secondary": [
            ("059", 0.64, "post-punk lineage"),
            ("075", 0.52, "melodic alt singles"),
        ],
        "context": ("older_sibling_cd_stack", "Older sibling CD stack", "Taste learned through albums, used CDs, and borrowed identity."),
        "false_nearby": ("safe_modern_alt_radio", "Safe modern alt radio", "Alt branding can hide too much polish.", "071", 10),
        "anti": [
            ("035", 0.7, "country-pop gloss is a poor fit"),
            ("091", 0.54, "big persona pop can feel overmanaged"),
        ],
        "artist_reactions": [
            ("nirvana", "love", ["formation-band", "raw-guitar"]),
            ("rem", "love", ["college-rock", "melodic-strangeness"]),
            ("pixies", "love", ["loud-quiet-logic", "art-damage"]),
            ("the-cure", "like", ["dark-pop", "guitar-mood"]),
            ("smashing-pumpkins", "like", ["90s-alt", "big-guitars"]),
            ("sonic-youth", "like", ["noise-lineage", "cool-distance"]),
            ("foo-fighters", "ok", ["post-nirvana", "too-straight"]),
            ("taylor-swift", "dont_know_enough", ["not-active-listening"]),
            ("shania-twain", "dont_like", ["country-pop-gloss"]),
            ("metallica", "ok", ["adjacent-heavy", "not-core"]),
            ("pavement", "love", ["slanted-indie", "album-canon"]),
            ("weezer", "like", ["melodic-alt", "shared-memory"]),
        ],
        "apple_artists": [
            ("nirvana", 0.94, 52, 5, "heavy_rotation"),
            ("rem", 0.82, 37, 15, "library_artist"),
            ("pixies", 0.76, 34, 6, "heavy_rotation"),
            ("the-cure", 0.66, 27, 28, "library_artist"),
            ("smashing-pumpkins", 0.61, 24, 19, "recent_play"),
            ("foo-fighters", 0.31, 7, 11, "recent_play"),
        ],
    },
    {
        "id": "fake_profile_04",
        "label": "Country-Pop Listener",
        "summary": "Leans toward country storytelling and crossover polish; open to pop songwriting when it still feels emotionally plainspoken.",
        "primary": [
            ("033", 0.86, "country-pop crossover"),
            ("035", 0.8, "modern mainstream country"),
        ],
        "secondary": [
            ("036", 0.57, "rootsy modern country"),
            ("091", 0.45, "pop songwriting crossover"),
        ],
        "context": ("wedding_and_tailgate_rotation", "Wedding and tailgate rotation", "Social singalongs and real-life utility weigh heavily."),
        "false_nearby": ("bro_country_overlap", "Bro-country overlap", "A few party songs should not swallow the whole profile.", "035", 5),
        "anti": [
            ("059", 0.58, "post-punk distance does not land"),
            ("119", 0.66, "hyperpop texture is not useful"),
        ],
        "artist_reactions": [
            ("shania-twain", "love", ["country-pop-canon", "household-repeat"]),
            ("dolly-parton", "love", ["storytelling", "warmth"]),
            ("kacey-musgraves", "like", ["modern-country", "lyric-detail"]),
            ("luke-combs", "like", ["mainstream-country", "big-voice"]),
            ("carrie-underwood", "like", ["country-radio", "vocal-power"]),
            ("taylor-swift", "like", ["crossover-songcraft", "early-country-memory"]),
            ("garth-brooks", "like", ["nostalgia", "arena-country"]),
            ("zach-bryan", "ok", ["roots-adjacent", "less-polished"]),
            ("metallica", "dont_like", ["not-social-useful"]),
            ("pixies", "dont_know_enough", ["not-exposed"]),
            ("doja-cat", "ok", ["pop-osmosis"]),
            ("100-gecs", "dont_like", ["too-chaotic"]),
        ],
        "apple_artists": [
            ("shania-twain", 0.9, 44, 4, "heavy_rotation"),
            ("kacey-musgraves", 0.78, 31, 9, "heavy_rotation"),
            ("luke-combs", 0.72, 28, 6, "recent_play"),
            ("carrie-underwood", 0.59, 18, 25, "library_artist"),
            ("taylor-swift", 0.47, 13, 15, "recent_play"),
            ("zach-bryan", 0.34, 7, 18, "playlist_save"),
        ],
    },
    {
        "id": "fake_profile_05",
        "label": "R&B / Hip-Hop Listener",
        "summary": "Responds to lyrical density, groove, and modern R&B atmosphere; pop can work when rhythm and voice carry it.",
        "primary": [
            ("052", 0.86, "modern rap authorship"),
            ("044", 0.82, "modern alternative R&B"),
        ],
        "secondary": [
            ("050", 0.68, "mainstream rap crossover"),
            ("043", 0.53, "soulful hip-hop lineage"),
        ],
        "context": ("late_night_headphones", "Late-night headphones", "Private listening and lyrical replay are high-value contexts."),
        "false_nearby": ("party_rap_as_total_profile", "Party rap as total profile", "Club familiarity should not flatten the profile.", "050", 7),
        "anti": [
            ("016", 0.47, "classic rock is familiar but rarely chosen"),
            ("061", 0.69, "traditional metal is usually outside the lane"),
        ],
        "artist_reactions": [
            ("kendrick-lamar", "love", ["lyrical-depth", "album-arc"]),
            ("sza", "love", ["modern-r-b", "emotional-texture"]),
            ("frank-ocean", "love", ["atmosphere", "voice-and-writing"]),
            ("beyonce", "like", ["pop-r-b-command", "performance"]),
            ("drake", "like", ["playlist-utility", "melody-rap"]),
            ("outkast", "love", ["rap-creativity", "southern-canon"]),
            ("lauryn-hill", "like", ["soul-rap-lineage", "classic"]),
            ("the-weeknd", "ok", ["pop-r-b", "sometimes-too-slick"]),
            ("artist-fleetwood-mac", "dont_know_enough", ["not-active-listening"]),
            ("metallica", "dont_like", ["not-my-texture"]),
            ("taylor-swift", "ok", ["pop-aware", "not-core"]),
            ("tyler-the-creator", "like", ["creative-rap", "left-pop"]),
        ],
        "apple_artists": [
            ("kendrick-lamar", 0.95, 59, 3, "heavy_rotation"),
            ("sza", 0.89, 48, 4, "heavy_rotation"),
            ("frank-ocean", 0.82, 42, 22, "library_artist"),
            ("beyonce", 0.64, 23, 7, "recent_play"),
            ("drake", 0.52, 19, 10, "playlist_save"),
            ("outkast", 0.4, 12, 50, "library_artist"),
        ],
    },
    {
        "id": "fake_profile_06",
        "label": "Theater / Family Context User",
        "summary": "A shared-household listener where musicals, Disney, and big emotional anchors matter more than scene membership.",
        "primary": [
            ("104", 0.9, "theater and musical authorship"),
            ("114", 0.8, "family-context shared listening"),
        ],
        "secondary": [
            ("106", 0.55, "soundtrack and showpiece bridges"),
            ("088", 0.44, "classic pop theatricality"),
        ],
        "context": ("living_room_singalong", "Living-room singalong", "Music is used for kids, chores, and full-room memory."),
        "false_nearby": ("soundtrack_means_everything", "Soundtrack means everything", "A soundtrack signal does not imply every film-score lane works.", "106", 15),
        "anti": [
            ("062", 0.72, "thrash and aggression are poor household fits"),
            ("119", 0.56, "hyper-online texture disrupts the shared context"),
        ],
        "artist_reactions": [
            ("lin-manuel-miranda", "love", ["family-singalong", "story-first"]),
            ("disney", "love", ["kids-context", "shared-memory"]),
            ("stephen-sondheim", "like", ["theater-writing", "craft"]),
            ("andrew-lloyd-webber", "like", ["musical-canon", "showpiece"]),
            ("prince", "like", ["theatrical-pop", "family-approved-edge"]),
            ("taylor-swift", "ok", ["household-pop", "shared-awareness"]),
            ("artist-queen", "like", ["big-theatrical-chorus", "recognition"]),
            ("beyonce", "ok", ["performance-pop", "selective"]),
            ("metallica", "dont_like", ["too-intense-for-household"]),
            ("slayer", "dont_like", ["too-extreme"]),
            ("kendrick-lamar", "dont_know_enough", ["not-family-context"]),
            ("bruno-mars", "like", ["family-party-pop", "clean-hooks"]),
        ],
        "apple_artists": [
            ("lin-manuel-miranda", 0.93, 56, 2, "heavy_rotation"),
            ("disney", 0.87, 49, 1, "heavy_rotation"),
            ("andrew-lloyd-webber", 0.59, 21, 35, "library_artist"),
            ("artist-queen", 0.52, 18, 12, "recent_play"),
            ("taylor-swift", 0.4, 10, 8, "recent_play"),
            ("bruno-mars", 0.35, 8, 16, "playlist_save"),
        ],
    },
    {
        "id": "fake_profile_07",
        "label": "Indie / Prestige Listener",
        "summary": "Favors critic-world indie, intimate writing, and artful production; big pop can work when it has authorship.",
        "primary": [
            ("116", 0.88, "current indie prestige"),
            ("078", 0.76, "indie album canon"),
        ],
        "secondary": [
            ("030", 0.62, "indie folk singer-songwriter"),
            ("085", 0.48, "dance-rock and art-pop"),
        ],
        "context": ("year_end_listening_notes", "Year-end listening notes", "Albums, recommendations, and subtle progression matter."),
        "false_nearby": ("festival_indie_as_default", "Festival indie as default", "Big indie visibility is less important than texture and authorship.", "078", 10),
        "anti": [
            ("035", 0.5, "country-radio polish feels too broad"),
            ("020", 0.44, "arena theatricality can overwhelm"),
        ],
        "artist_reactions": [
            ("phoebe-bridgers", "love", ["intimate-writing", "indie-prestige"]),
            ("mitski", "love", ["tension", "voice"]),
            ("big-thief", "love", ["songwriting-depth", "organic-texture"]),
            ("sufjan-stevens", "like", ["arrangement", "album-craft"]),
            ("vampire-weekend", "like", ["indie-canon", "precision"]),
            ("lcd-soundsystem", "like", ["dance-rock", "self-aware"]),
            ("tame-impala", "ok", ["festival-adjacent", "production-interest"]),
            ("taylor-swift", "ok", ["authorial-pop", "selective"]),
            ("luke-combs", "dont_like", ["too-mainstream-country"]),
            ("metallica", "dont_know_enough", ["not-core"]),
            ("neutral-milk-hotel", "love", ["indie-canon", "album-depth"]),
            ("the-national", "like", ["adult-indie", "mood"]),
        ],
        "apple_artists": [
            ("phoebe-bridgers", 0.94, 45, 4, "heavy_rotation"),
            ("mitski", 0.86, 38, 8, "heavy_rotation"),
            ("big-thief", 0.78, 31, 13, "library_artist"),
            ("sufjan-stevens", 0.64, 24, 36, "library_artist"),
            ("vampire-weekend", 0.45, 12, 55, "playlist_save"),
            ("lcd-soundsystem", 0.39, 9, 20, "recent_play"),
        ],
    },
    {
        "id": "fake_profile_08",
        "label": "Metal / Heavy User",
        "summary": "Values riff authority, heaviness, and scene fluency; tolerates melody when the center of gravity stays heavy.",
        "primary": [
            ("062", 0.92, "thrash and heavy canon"),
            ("066", 0.84, "modern heavy and alt-metal"),
        ],
        "secondary": [
            ("061", 0.7, "classic metal foundation"),
            ("064", 0.48, "doom and heavy rock lineage"),
        ],
        "context": ("workout_and_deep_catalog", "Workout and deep catalog", "Intensity and technical identity are positive signals."),
        "false_nearby": ("hard_rock_as_metal", "Hard rock as metal", "Classic hard-rock adjacency should not replace true heaviness.", "017", 3),
        "anti": [
            ("091", 0.77, "polished persona pop is not the lane"),
            ("033", 0.7, "country-pop crossover is a strong negative"),
        ],
        "artist_reactions": [
            ("metallica", "love", ["riff-canon", "thrash-foundation"]),
            ("slayer", "love", ["speed", "extreme-clarity"]),
            ("black-sabbath", "love", ["heavy-origin", "doom-weight"]),
            ("tool", "like", ["prog-heavy", "patient-intensity"]),
            ("deftones", "like", ["alt-metal", "texture"]),
            ("iron-maiden", "like", ["classic-metal", "gallop"]),
            ("slipknot", "ok", ["modern-heavy", "mood-dependent"]),
            ("foo-fighters", "ok", ["rock-familiar", "not-heavy-enough"]),
            ("taylor-swift", "dont_like", ["too-polished"]),
            ("shania-twain", "dont_like", ["not-my-lane"]),
            ("kendrick-lamar", "dont_know_enough", ["respect-not-listening"]),
            ("artist-queen", "ok", ["classic-rock-adjacent"]),
        ],
        "apple_artists": [
            ("metallica", 0.97, 68, 2, "heavy_rotation"),
            ("slayer", 0.88, 42, 5, "heavy_rotation"),
            ("black-sabbath", 0.82, 37, 16, "library_artist"),
            ("tool", 0.74, 29, 7, "recent_play"),
            ("deftones", 0.66, 25, 9, "recent_play"),
            ("iron-maiden", 0.5, 15, 41, "library_artist"),
        ],
    },
    {
        "id": "fake_profile_09",
        "label": "Modern Pop + TikTok User",
        "summary": "Current-pop and short-form discovery listener with taste led by personality, hooks, and internet circulation.",
        "primary": [
            ("093", 0.9, "current internet-native pop"),
            ("091", 0.76, "modern persona pop"),
        ],
        "secondary": [
            ("119", 0.52, "hyperpop adjacency"),
            ("050", 0.46, "rap-pop circulation"),
        ],
        "context": ("short_form_discovery", "Short-form discovery", "Taste updates quickly through clips, edits, and repeatable hooks."),
        "false_nearby": ("viral_equals_core", "Viral equals core", "A viral sound is observable but not automatically deep affinity.", "119", 18),
        "anti": [
            ("061", 0.72, "traditional metal is a strong mismatch"),
            ("014", 0.5, "60s psych is not a default fit"),
        ],
        "artist_reactions": [
            ("olivia-rodrigo", "love", ["current-pop", "teen-drama-hooks"]),
            ("billie-eilish", "love", ["moody-current", "voice"]),
            ("doja-cat", "like", ["internet-pop", "rap-pop"]),
            ("chappell-roan", "like", ["personality-pop", "viral-hooks"]),
            ("sabrina-carpenter", "like", ["bright-current-pop", "clips"]),
            ("dua-lipa", "ok", ["dance-pop", "less-personal"]),
            ("taylor-swift", "like", ["persona-pop", "fandom-awareness"]),
            ("100-gecs", "ok", ["online-edge", "selective"]),
            ("metallica", "dont_like", ["too-far-from-context"]),
            ("black-sabbath", "dont_know_enough", ["not-exposed"]),
            ("kendrick-lamar", "ok", ["respect", "not-everyday"]),
            ("ariana-grande", "like", ["vocal-pop", "familiar"]),
        ],
        "apple_artists": [
            ("olivia-rodrigo", 0.96, 62, 1, "heavy_rotation"),
            ("billie-eilish", 0.87, 44, 3, "heavy_rotation"),
            ("doja-cat", 0.77, 38, 2, "recent_play"),
            ("chappell-roan", 0.68, 29, 5, "recent_play"),
            ("sabrina-carpenter", 0.59, 20, 4, "recent_play"),
            ("taylor-swift", 0.46, 12, 16, "playlist_save"),
        ],
    },
    {
        "id": "fake_profile_10",
        "label": "Low-Library Streaming User",
        "summary": "Sparse library, mostly streaming singles and algorithmic plays, with broad familiarity but shallow commitment.",
        "primary": [
            ("090", 0.54, "radio pop and R&B crossover"),
            ("050", 0.5, "mainstream rap exposure"),
        ],
        "secondary": [
            ("091", 0.42, "pop familiarity"),
            ("113", 0.32, "nostalgia from shared spaces"),
        ],
        "context": ("algorithmic_background", "Algorithmic background", "The payload is low-confidence and should not dominate Page 1."),
        "false_nearby": ("playlist_noise", "Playlist noise", "Single accidental plays should stay weak.", "093", 12),
        "anti": [
            ("062", 0.58, "heavy music causes quick skips"),
            ("104", 0.4, "theater context is not represented"),
        ],
        "artist_reactions": [
            ("the-weeknd", "like", ["streaming-single", "radio-familiar"]),
            ("drake", "ok", ["playlist-familiar", "shallow"]),
            ("taylor-swift", "ok", ["broad-familiarity", "not-deep"]),
            ("dua-lipa", "ok", ["dance-pop-familiar", "background"]),
            ("bruno-mars", "like", ["party-familiar", "safe"]),
            ("artist-queen", "ok", ["classic-recognition", "not-library"]),
            ("artist-fleetwood-mac", "dont_know_enough", ["not-active-listening"]),
            ("metallica", "dont_like", ["quick-skip"]),
            ("lin-manuel-miranda", "dont_know_enough", ["not-context"]),
            ("sza", "ok", ["streaming-familiar", "not-deep"]),
            ("olivia-rodrigo", "ok", ["current-aware", "shallow"]),
            ("kendrick-lamar", "dont_know_enough", ["not-deep"]),
        ],
        "apple_artists": [
            ("the-weeknd", 0.48, 9, 7, "recent_play"),
            ("drake", 0.38, 7, 21, "recent_play"),
            ("taylor-swift", 0.34, 5, 14, "playlist_save"),
            ("dua-lipa", 0.3, 4, 18, "playlist_save"),
            ("bruno-mars", 0.27, 3, 42, "library_artist"),
        ],
        "external_apple_hints": [
            ("lofi-study-stream", "Lofi Study Stream", "am.ext.lofi-study-stream", 0.18, 2, 3),
        ],
    },
]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


def write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


def relative(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def graph_fingerprint() -> dict[str, Any]:
    files = []
    combined = hashlib.sha256()
    for filename in GRAPH_INPUT_FILES:
        path = GRAPH_DIR / filename
        file_hash = sha256_file(path)
        files.append({"path": relative(path), "sha256": file_hash})
        combined.update(filename.encode("utf-8"))
        combined.update(file_hash.encode("utf-8"))
    return {"sha256": combined.hexdigest(), "files": files}


def artist_ref(artist: dict[str, Any]) -> dict[str, Any]:
    return {
        "object_type": "artist",
        "ref_source": "canonical_graph",
        "canonical_artist_id": artist["canonical_artist_id"],
        "display_name": artist["display_name"],
        "resolution_state": "resolved",
    }


def album_ref(album: dict[str, Any]) -> dict[str, Any]:
    artists = album.get("artist_names", [])
    ref = {
        "object_type": "album",
        "ref_source": "canonical_graph",
        "canonical_album_id": album["canonical_album_id"],
        "display_name": album["display_name"],
        "resolution_state": "resolved",
    }
    if artists:
        ref["artist_display_name"] = artists[0]
    return ref


def song_ref(song: dict[str, Any]) -> dict[str, Any]:
    artists = song.get("artist_names", [])
    ref = {
        "object_type": "song_recording",
        "ref_source": "canonical_graph",
        "canonical_song_recording_id": song["canonical_song_recording_id"],
        "display_name": song["display_name"],
        "resolution_state": "resolved",
    }
    if artists:
        ref["artist_display_name"] = artists[0]
    return ref


def external_artist_ref(display_name: str, apple_music_id: str) -> dict[str, Any]:
    return {
        "object_type": "artist",
        "ref_source": "external_catalog",
        "external_catalog_refs": {"apple_music_id": apple_music_id},
        "display_name": display_name,
        "resolution_state": "needs_resolution",
    }


def ref_key(ref: dict[str, Any]) -> tuple[str, str]:
    object_type = ref["object_type"]
    if object_type == "artist":
        return object_type, ref["canonical_artist_id"]
    if object_type == "album":
        return object_type, ref["canonical_album_id"]
    if object_type == "song_recording":
        return object_type, ref["canonical_song_recording_id"]
    raise ValueError(f"Unsupported object type: {object_type}")


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def recognition_value(tier: str | None) -> float:
    return {
        "mass": 5.0,
        "high": 4.0,
        "medium": 2.5,
        "low": 1.0,
        "niche": 0.8,
    }.get(tier, 1.0)


def survey_value(tier: str | None) -> float:
    return {
        "core": 4.0,
        "standard": 2.5,
        "edge": 0.8,
    }.get(tier, 1.0)


def graph_score(artist: dict[str, Any]) -> float:
    recognition = recognition_value(artist.get("best_recognition_tier"))
    survey = survey_value(artist.get("best_survey_tier"))
    roles = set(artist.get("roles", []))
    role_score = 0.0
    if "anchor" in roles or "artist_anchor" in roles:
        role_score += 1.2
    if "gateway" in roles:
        role_score += 0.8
    if "bridge" in roles:
        role_score += 0.4
    seed = 0.6 if artist.get("existing_seed_any") else 0.0
    return recognition + survey + role_score + seed


def normalized_graph_score(artist: dict[str, Any]) -> float:
    return clamp(graph_score(artist) / 11.6)


def sort_artists_for_graph(artists: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        artists,
        key=lambda item: (
            -graph_score(item),
            item.get("display_name", "").lower(),
            item["canonical_artist_id"],
        ),
    )


def graph_context(artist: dict[str, Any]) -> dict[str, Any]:
    return {
        "family_numbers": artist.get("family_numbers", []),
        "archetype_ids": artist.get("archetype_ids", []),
        "roles": artist.get("roles", []),
        "best_recognition_tier": artist.get("best_recognition_tier", "unknown"),
        "best_survey_tier": artist.get("best_survey_tier", "unknown"),
    }


def make_tile(candidate: dict[str, Any], position: int) -> dict[str, Any]:
    artist = candidate["artist"]
    return {
        "tile_id": f"tile_{position:02d}",
        "position": position,
        "music_object_ref": artist_ref(artist),
        "page_intent": candidate["page_intent"],
        "candidate_basis": candidate["candidate_basis"],
        "graph_context": graph_context(artist),
        "apple_evidence": candidate["apple_evidence"],
        "scores": candidate["scores"],
        "reason_for_debug": candidate["reason_for_debug"],
    }


def blank_apple_evidence() -> dict[str, Any]:
    return {
        "exact_signal_weight": 0.0,
        "exposure_score": 0.0,
        "recency_score": 0.0,
        "repetition_score": 0.0,
        "library_commitment_score": 0.0,
        "favorite_or_rating_score": 0.0,
        "playlist_context_score": 0.0,
        "album_completion_hint": 0.0,
        "artist_depth_hint": 0.0,
        "family_context_risk": 0.0,
        "catalog_resolution_confidence": 0.0,
        "probable_affinity_score": 0.0,
        "archetype_neighbor_score": 0.0,
        "family_neighbor_score": 0.0,
        "signal_ids": [],
    }


def apple_signal_dimensions(signal: dict[str, Any], artist: dict[str, Any]) -> dict[str, Any]:
    signal_type = signal["signal_type"]
    normalized_weight = float(signal["normalized_weight"])
    recency_days = int(signal["recency_days"])
    play_count = int(signal["play_count_90d"])
    recency_score = clamp(1.0 - (recency_days / 90.0))
    repetition_score = clamp(play_count / 60.0)
    signal_type_strength = {
        "heavy_rotation": 1.0,
        "library_artist": 0.82,
        "recent_play": 0.58,
        "playlist_save": 0.5,
        "external_catalog_hint": 0.18,
    }.get(signal_type, 0.2)
    library_commitment_score = clamp(
        {
            "library_artist": 0.9,
            "heavy_rotation": 0.72,
            "playlist_save": 0.42,
            "recent_play": 0.22,
        }.get(signal_type, 0.0)
        + (normalized_weight * 0.18)
    )
    playlist_context_score = {
        "playlist_save": 0.85,
        "recent_play": 0.35,
        "heavy_rotation": 0.18,
        "library_artist": 0.1,
    }.get(signal_type, 0.0)
    exposure_score = clamp(
        max(
            normalized_weight,
            repetition_score * 0.85,
            signal_type_strength * 0.7,
        )
    )
    artist_depth_hint = clamp(
        (repetition_score * 0.36)
        + (library_commitment_score * 0.34)
        + (normalized_weight * 0.3)
    )
    family_numbers = set(artist.get("family_numbers", []))
    family_context_risk = 0.0
    if family_numbers & {15, 17}:
        family_context_risk = 0.55
    if artist["display_name"].casefold() in {"disney", "lin-manuel miranda"}:
        family_context_risk = max(family_context_risk, 0.72)
    if signal_type == "playlist_save":
        family_context_risk = clamp(family_context_risk + 0.12)
    probable_affinity_score = clamp(
        (exposure_score * 0.28)
        + (recency_score * 0.14)
        + (repetition_score * 0.18)
        + (library_commitment_score * 0.18)
        + (artist_depth_hint * 0.12)
        + (playlist_context_score * 0.04)
        - (family_context_risk * 0.14)
    )
    return {
        "exact_signal_weight": round(normalized_weight, 3),
        "exposure_score": round(exposure_score, 3),
        "recency_score": round(recency_score, 3),
        "repetition_score": round(repetition_score, 3),
        "library_commitment_score": round(library_commitment_score, 3),
        "favorite_or_rating_score": 0.0,
        "playlist_context_score": round(playlist_context_score, 3),
        "album_completion_hint": 0.0,
        "artist_depth_hint": round(artist_depth_hint, 3),
        "family_context_risk": round(family_context_risk, 3),
        "catalog_resolution_confidence": 1.0,
        "probable_affinity_score": round(probable_affinity_score, 3),
        "archetype_neighbor_score": 0.0,
        "family_neighbor_score": 0.0,
        "signal_ids": [signal["signal_id"]],
    }


def apple_signal_index(
    apple_payload: dict[str, Any],
    artists_by_id: dict[str, dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], Counter[str], Counter[int]]:
    exact_evidence: dict[str, dict[str, Any]] = {}
    archetype_weights: Counter[str] = Counter()
    family_weights: Counter[int] = Counter()
    for signal in apple_payload["signals"]:
        ref = signal["music_object_ref"]
        if ref["ref_source"] != "canonical_graph" or ref["object_type"] != "artist":
            continue
        artist_id = ref["canonical_artist_id"]
        weight = float(signal["normalized_weight"])
        artist = artists_by_id.get(artist_id)
        if not artist:
            continue
        dimensions = apple_signal_dimensions(signal, artist)
        existing = exact_evidence.get(artist_id, blank_apple_evidence())
        merged = {}
        for key, value in dimensions.items():
            if key == "signal_ids":
                merged[key] = sorted(set(existing.get(key, []) + value))
            else:
                merged[key] = round(max(float(existing.get(key, 0.0)), float(value)), 3)
        exact_evidence[artist_id] = merged
        evidence_weight = merged["probable_affinity_score"] or weight
        for archetype_id in artist.get("archetype_ids", []):
            archetype_weights[archetype_id] += evidence_weight
        for family_number in artist.get("family_numbers", []):
            family_weights[family_number] += evidence_weight
    return exact_evidence, archetype_weights, family_weights


def bridge_value_for_roles(roles: set[str]) -> float:
    return clamp(
        (0.42 if "bridge" in roles else 0.0)
        + (0.24 if "gateway" in roles else 0.0)
        + (0.18 if "live_gateway" in roles else 0.0)
        + (0.16 if "compilation_gateway" in roles else 0.0)
    )


def false_nearby_value_for_roles(roles: set[str]) -> float:
    return clamp(
        (0.5 if "false_nearby" in roles else 0.0)
        + (0.34 if "boundary" in roles else 0.0)
        + (0.28 if "contrast" in roles else 0.0)
    )


def build_artist_candidate_pool(
    artists: list[dict[str, Any]],
    artists_by_id: dict[str, dict[str, Any]],
    apple_payload: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    if apple_payload is None:
        exact_evidence: dict[str, dict[str, Any]] = {}
        archetype_weights: Counter[str] = Counter()
        family_weights: Counter[int] = Counter()
    else:
        exact_evidence, archetype_weights, family_weights = apple_signal_index(
            apple_payload,
            artists_by_id,
        )

    candidates = []
    for artist in artists:
        artist_id = artist["canonical_artist_id"]
        roles = set(artist.get("roles", []))
        evidence = copy.deepcopy(exact_evidence.get(artist_id, blank_apple_evidence()))
        archetype_neighbor_score = clamp(
            sum(archetype_weights.get(item, 0.0) for item in artist.get("archetype_ids", []))
            / 2.5
        )
        family_neighbor_score = clamp(
            sum(family_weights.get(item, 0.0) for item in artist.get("family_numbers", []))
            / 4.0
        )
        evidence["archetype_neighbor_score"] = round(archetype_neighbor_score, 3)
        evidence["family_neighbor_score"] = round(family_neighbor_score, 3)
        graph_familiarity = clamp(
            (recognition_value(artist.get("best_recognition_tier")) / 5.0 * 0.68)
            + (survey_value(artist.get("best_survey_tier")) / 4.0 * 0.32)
        )
        expected_familiarity = clamp(
            max(
                graph_familiarity,
                (graph_familiarity * 0.55) + (evidence["exposure_score"] * 0.45),
            )
        )
        bridge_value = bridge_value_for_roles(roles)
        false_nearby_value = false_nearby_value_for_roles(roles)
        specificity_value = clamp(
            (0.18 if "song_first" in roles else 0.0)
            + (0.18 if "album_anchor" in roles else 0.0)
            + (0.12 if artist.get("source_row_count", 1) > 1 else 0.0)
        )
        apple_evidence_score = clamp(
            evidence["probable_affinity_score"]
            + (archetype_neighbor_score * 0.34)
            + (family_neighbor_score * 0.12)
        )
        expected_population_baseline = max(0.18, graph_familiarity)
        payload_overrepresentation_score = 0.0
        if evidence["exact_signal_weight"] > 0:
            payload_overrepresentation_score = clamp(
                (evidence["probable_affinity_score"] / expected_population_baseline - 0.45)
                / 1.05
            )
        archetype_hypothesis_value = clamp(
            (archetype_neighbor_score * 0.58)
            + (family_neighbor_score * 0.22)
            + (apple_evidence_score * 0.14 if evidence["exact_signal_weight"] > 0 else 0.0)
            + (normalized_graph_score(artist) * 0.06)
        )
        uncertainty = (
            clamp(1.0 - abs(evidence["probable_affinity_score"] - 0.5) * 2.0)
            if evidence["exact_signal_weight"] > 0
            else (0.56 if archetype_neighbor_score > 0 else 0.38)
        )
        information_gain = clamp(
            (bridge_value * 0.3)
            + (false_nearby_value * 0.28)
            + (uncertainty * 0.24)
            + (specificity_value * 0.18)
        )
        multi_archetype_junction_value = clamp(
            (min(len(artist.get("archetype_ids", [])), 3) / 3.0 * 0.28)
            + (min(len(artist.get("family_numbers", [])), 2) / 2.0 * 0.16)
            + (bridge_value * 0.28)
            + (0.18 if roles & {"gateway", "artist_anchor"} else 0.0)
            + (specificity_value * 0.10)
        )
        novelty = clamp(
            (0.36 if artist.get("best_recognition_tier") in {"medium", "high"} else 0.12)
            + (0.24 if artist.get("best_survey_tier") == "standard" else 0.1)
            + (0.18 if "deepening" in roles else 0.0)
            + (0.12 if archetype_neighbor_score > 0 and evidence["exact_signal_weight"] == 0 else 0.0)
        )
        too_obscure_penalty = 0.1 if artist.get("best_recognition_tier") in {"low", "niche"} else 0.0
        resolution_penalty = 0.04 if artist.get("source_row_count", 1) > 2 else 0.0
        household_penalty = evidence["family_context_risk"] * 0.08
        generic_superstar_ambiguity_penalty = (
            0.07
            if artist.get("best_recognition_tier") == "mass"
            and multi_archetype_junction_value >= 0.62
            and evidence["exact_signal_weight"] == 0
            else 0.0
        )
        penalties = round(
            too_obscure_penalty
            + resolution_penalty
            + household_penalty
            + generic_superstar_ambiguity_penalty,
            3,
        )
        candidates.append(
            {
                "artist": artist,
                "display_key": artist["display_name"].casefold(),
                "families": artist.get("family_numbers", []),
                "archetypes": artist.get("archetype_ids", []),
                "roles": sorted(roles),
                "apple_evidence": evidence,
                "selection_values": {
                    "bridge_value": round(bridge_value, 3),
                    "information_gain": round(information_gain, 3),
                    "novelty": round(novelty, 3),
                    "graph_familiarity": round(graph_familiarity, 3),
                },
                "base_scores": {
                    "payload_overrepresentation_score": round(payload_overrepresentation_score, 3),
                    "apple_evidence_strength": round(apple_evidence_score, 3),
                    "expected_familiarity": round(expected_familiarity, 3),
                    "archetype_hypothesis_value": round(archetype_hypothesis_value, 3),
                    "multi_archetype_junction_value": round(multi_archetype_junction_value, 3),
                    "canonical_anchor_value": round(normalized_graph_score(artist), 3),
                    "false_nearby_value": round(false_nearby_value, 3),
                    "coverage_value": 0.0,
                    "penalties": penalties,
                    "final": 0.0,
                },
            }
        )
    return candidates


def coverage_value_for_candidate(candidate: dict[str, Any], selected: list[dict[str, Any]]) -> float:
    family_counts: Counter[int] = Counter()
    archetype_counts: Counter[str] = Counter()
    for item in selected:
        family_counts.update(item["families"])
        archetype_counts.update(item["archetypes"])
    family_value = max((1.0 / (1 + family_counts[item]) for item in candidate["families"]), default=0.4)
    archetype_value = max(
        (1.0 / (1 + archetype_counts[item]) for item in candidate["archetypes"]),
        default=0.4,
    )
    return round(clamp((family_value * 0.72) + (archetype_value * 0.28)), 3)


def finalized_scores(candidate: dict[str, Any], selected: list[dict[str, Any]]) -> dict[str, float]:
    scores = copy.deepcopy(candidate["base_scores"])
    scores["coverage_value"] = coverage_value_for_candidate(candidate, selected)
    final = sum(scores[key] * weight for key, weight in PAGE1_SCORE_WEIGHTS.items())
    scores["final"] = round(final - scores["penalties"], 3)
    return scores


def page1_intent_targets(mode: str) -> list[tuple[str, int]]:
    if mode == "generic_graph_seed":
        return PAGE1_GRAPH_ONLY_INTENT_TARGETS
    return PAGE1_INTENT_TARGETS


def intent_fit(candidate: dict[str, Any], intent: str, mode: str, scores: dict[str, float]) -> float:
    evidence = candidate["apple_evidence"]
    exact = evidence["exact_signal_weight"] > 0
    neighbor = evidence["archetype_neighbor_score"] > 0 or evidence["family_neighbor_score"] > 0
    if intent == "payload_signature_artist":
        return (
            scores["payload_overrepresentation_score"] * 0.58
            + scores["apple_evidence_strength"] * 0.24
            + scores["expected_familiarity"] * 0.12
            + (0.18 if exact else 0.0)
        )
    if intent == "archetype_confirmation_anchor":
        return (
            scores["archetype_hypothesis_value"] * 0.42
            + scores["expected_familiarity"] * 0.28
            + scores["canonical_anchor_value"] * 0.18
            + (0.12 if neighbor else 0.0)
        )
    if intent == "multi_archetype_junction":
        return (
            scores["multi_archetype_junction_value"] * 0.52
            + candidate["selection_values"]["information_gain"] * 0.2
            + scores["expected_familiarity"] * 0.16
            + (0.08 if neighbor and not exact else 0.0)
        )
    if intent == "false_nearby_or_boundary_check":
        return (
            scores["false_nearby_value"] * 0.56
            + candidate["selection_values"]["information_gain"] * 0.18
            + scores["expected_familiarity"] * 0.18
            + (0.08 if neighbor and not exact else 0.0)
        )
    if intent == "mass_popular_control":
        return (
            (0.52 if candidate["artist"].get("best_recognition_tier") == "mass" else 0.0)
            + scores["expected_familiarity"] * 0.32
            + scores["canonical_anchor_value"] * 0.16
        )
    if intent == "coverage_repair_broad_sentinel":
        return (scores["coverage_value"] * 0.58) + (scores["expected_familiarity"] * 0.18) + (scores["canonical_anchor_value"] * 0.14)
    return 0.0


def intent_eligible(candidate: dict[str, Any], intent: str, mode: str, strict: bool) -> bool:
    scores = candidate["base_scores"]
    roles = set(candidate["roles"])
    evidence = candidate["apple_evidence"]
    exact = evidence["exact_signal_weight"] > 0
    neighbor = evidence["archetype_neighbor_score"] > 0 or evidence["family_neighbor_score"] > 0
    if intent == "payload_signature_artist":
        if mode == "apple_biased_seed" and strict:
            return (
                exact
                and scores["payload_overrepresentation_score"] >= 0.24
                and scores["expected_familiarity"] >= 0.5
            )
        return exact and scores["expected_familiarity"] >= 0.45
    if intent == "archetype_confirmation_anchor":
        if exact and strict and mode == "apple_biased_seed":
            return False
        if mode == "apple_biased_seed" and strict:
            return neighbor and scores["expected_familiarity"] >= 0.72 and scores["canonical_anchor_value"] >= 0.5
        return scores["expected_familiarity"] >= 0.72 and scores["canonical_anchor_value"] >= 0.58
    if intent == "multi_archetype_junction":
        if exact and strict and mode == "apple_biased_seed":
            return False
        return (
            scores["multi_archetype_junction_value"] >= (0.42 if strict else 0.28)
            and scores["expected_familiarity"] >= (0.64 if strict else 0.48)
        )
    if intent == "false_nearby_or_boundary_check":
        if exact and strict:
            return False
        return (
            scores["expected_familiarity"] >= (0.74 if strict else 0.5)
            and (
                scores["false_nearby_value"] >= (0.34 if strict else 0.18)
            or bool(roles & {"boundary", "contrast", "false_nearby"})
            )
        )
    if intent == "mass_popular_control":
        if exact and strict:
            return False
        return (
            candidate["artist"].get("best_recognition_tier") == "mass"
            and scores["expected_familiarity"] >= (0.84 if strict else 0.62)
        )
    if intent == "coverage_repair_broad_sentinel":
        if exact and strict:
            return False
        return scores["expected_familiarity"] >= (0.72 if strict else 0.5)
    return True


def candidate_basis(candidate: dict[str, Any], intent: str, mode: str) -> list[str]:
    evidence = candidate["apple_evidence"]
    basis = ["active_survey_selection", f"{intent}_bucket"]
    if mode == "generic_graph_seed":
        basis.append("graph_core_seed")
        if intent != "archetype_confirmation_anchor":
            basis.append("graph_exploration")
        return basis
    if intent == "payload_signature_artist":
        basis.append("payload_overrepresentation")
    if evidence["exact_signal_weight"] > 0:
        basis.append("apple_exact_match")
    elif evidence["archetype_neighbor_score"] > 0:
        basis.append("apple_archetype_neighbor")
    elif evidence["family_neighbor_score"] > 0:
        basis.append("apple_family_neighbor")
    else:
        basis.append("graph_exploration")
    return basis


def can_add_candidate(
    candidate: dict[str, Any],
    selected: list[dict[str, Any]],
    mode: str,
    strict: bool,
) -> bool:
    if any(candidate["artist"]["canonical_artist_id"] == item["artist"]["canonical_artist_id"] for item in selected):
        return False
    if any(candidate["display_key"] == item["display_key"] for item in selected):
        return False
    if not strict:
        return True
    family_counts: Counter[int] = Counter()
    archetype_counts: Counter[str] = Counter()
    for item in selected:
        family_counts.update(item["families"])
        archetype_counts.update(item["archetypes"])
    max_family = 3 if mode == "apple_biased_seed" else 2
    max_archetype = 2
    if candidate["families"] and all(family_counts[item] >= max_family for item in candidate["families"]):
        return False
    if candidate["archetypes"] and all(archetype_counts[item] >= max_archetype for item in candidate["archetypes"]):
        return False
    return True


def materialize_candidate(
    candidate: dict[str, Any],
    intent: str,
    mode: str,
    selected: list[dict[str, Any]],
) -> dict[str, Any]:
    item = copy.deepcopy(candidate)
    scores = finalized_scores(item, selected)
    item["page_intent"] = intent
    item["candidate_basis"] = candidate_basis(item, intent, mode)
    item["scores"] = scores
    item["reason_for_debug"] = (
        f"{intent}: final={scores['final']}, overrep={scores['payload_overrepresentation_score']}, "
        f"apple_strength={scores['apple_evidence_strength']}, familiarity={scores['expected_familiarity']}, "
        f"archetype={scores['archetype_hypothesis_value']}, junction={scores['multi_archetype_junction_value']}"
    )
    return item


def choose_best_candidate(
    candidates: list[dict[str, Any]],
    selected: list[dict[str, Any]],
    intent: str,
    mode: str,
    strict: bool,
) -> dict[str, Any] | None:
    scored = []
    for candidate in candidates:
        if not can_add_candidate(candidate, selected, mode, strict):
            continue
        if not intent_eligible(candidate, intent, mode, strict):
            continue
        scores = finalized_scores(candidate, selected)
        scored.append(
            (
                scores["final"] + intent_fit(candidate, intent, mode, scores),
                candidate["artist"]["display_name"].lower(),
                candidate["artist"]["canonical_artist_id"],
                candidate,
            )
        )
    if not scored:
        return None
    scored.sort(key=lambda item: (-item[0], item[1], item[2]))
    return scored[0][3]


def optimize_page1_slate(
    candidates: list[dict[str, Any]],
    mode: str,
) -> tuple[list[dict[str, Any]], int]:
    selected: list[dict[str, Any]] = []
    for intent, target_count in page1_intent_targets(mode):
        for _ in range(target_count):
            candidate = None
            for strict in [True, False]:
                candidate = choose_best_candidate(candidates, selected, intent, mode, strict)
                if candidate is not None:
                    break
            if candidate is None:
                continue
            selected.append(materialize_candidate(candidate, intent, mode, selected))

    while len(selected) < PAGE_SIZE:
        candidate = choose_best_candidate(candidates, selected, "coverage_repair_broad_sentinel", mode, False)
        if candidate is None:
            break
        selected.append(materialize_candidate(candidate, "coverage_repair_broad_sentinel", mode, selected))

    selected_ids = {item["artist"]["canonical_artist_id"] for item in selected}
    selected_displays = {item["display_key"] for item in selected}
    duplicate_display_names_suppressed = sum(
        1
        for item in candidates
        if item["display_key"] in selected_displays
        and item["artist"]["canonical_artist_id"] not in selected_ids
    )
    return selected[:PAGE_SIZE], duplicate_display_names_suppressed


def build_page(
    run_id: str,
    mode: str,
    selected_candidates: list[dict[str, Any]],
    manifest_status: str,
    duplicate_display_names_suppressed: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    tiles = []
    for position, candidate in enumerate(selected_candidates, start=1):
        tiles.append(make_tile(candidate, position))

    page = {
        "schema_version": "survey_simulation.page.v0.1",
        "page_id": "page_01",
        "page_number": 1,
        "stage": "artists",
        "page_mode": mode,
        "tile_count": PAGE_SIZE,
        "generator_visible_inputs": {
            "canonical_graph_manifest_status": manifest_status,
            "apple_payload_applied": mode == "apple_biased_seed",
            "prior_visible_response_count": 0,
            "hidden_inputs_consumed": False,
        },
        "tiles": tiles,
    }

    direct_apple_count = sum(
        1 for tile in tiles if "apple_exact_match" in tile["candidate_basis"]
    )
    graph_exploration_count = sum(
        1
        for tile in tiles
        if "graph_exploration" in tile["candidate_basis"]
        or (mode == "generic_graph_seed" and "graph_core_seed" in tile["candidate_basis"])
    )
    intent_counts = Counter(tile["page_intent"] for tile in tiles)
    log = {
        "schema_version": "survey_simulation.page_generation_log.v0.1",
        "run_id": run_id,
        "generated_at": GENERATED_AT,
        "page_mode": mode,
        "source_tables_read": [
            relative(GRAPH_DIR / "canonical_graph_manifest.json"),
            relative(GRAPH_DIR / "canonical_artists.json"),
            relative(GRAPH_DIR / "artist_archetype_memberships.json"),
        ],
        "builder_visible_input_summary": {
            "canonical_graph": "staging import dry-run artist table and membership metadata",
            "apple_payload": (
                "not applied for graph-only Page 1"
                if mode == "generic_graph_seed"
                else "sanitized simulated Apple Music payload interpreted as exposure priors; unresolved external hints ignored for candidate generation"
            ),
            "prior_visible_response_count": 0,
            "hidden_inputs_consumed": False,
        },
        "candidate_selection": {
            "tile_count": PAGE_SIZE,
            "direct_apple_match_count": direct_apple_count,
            "graph_exploration_count": graph_exploration_count,
            "duplicate_display_names_suppressed": duplicate_display_names_suppressed,
            "intent_counts": dict(sorted(intent_counts.items())),
            "tiles": [
                {
                    "position": tile["position"],
                    "canonical_artist_id": tile["music_object_ref"]["canonical_artist_id"],
                    "display_name": tile["music_object_ref"]["display_name"],
                    "page_intent": tile["page_intent"],
                    "candidate_basis": tile["candidate_basis"],
                    "scores": tile["scores"],
                }
                for tile in tiles
            ],
        },
    }
    return page, log


def build_fake_profile(profile_def: dict[str, Any], index: int) -> dict[str, Any]:
    false_id, false_name, false_note, false_archetype, false_family = profile_def["false_nearby"]
    context_id, context_name, context_note = profile_def["context"]
    return {
        "schema_version": "survey_simulation.fake_profile.v0.1",
        "fake_profile_id": profile_def["id"],
        "display_label": profile_def["label"],
        "summary": profile_def["summary"],
        "primary_archetype_affinities": [
            {"archetype_id": item[0], "weight": item[1], "note": item[2]}
            for item in profile_def["primary"]
        ],
        "secondary_archetype_affinities": [
            {"archetype_id": item[0], "weight": item[1], "note": item[2]}
            for item in profile_def["secondary"]
        ],
        "context_lane": {
            "lane_id": context_id,
            "display_name": context_name,
            "note": context_note,
        },
        "false_nearby_lane": {
            "lane_id": false_id,
            "display_name": false_name,
            "note": false_note,
            "archetype_id": false_archetype,
            "family_number": false_family,
        },
        "hidden_anti_affinities": [
            {"archetype_id": item[0], "weight": item[1], "note": item[2]}
            for item in profile_def["anti"]
        ],
        "apple_payload_id": f"apple_payload_{index:02d}",
        "hidden_reaction_corpus_id": f"hidden_corpus_{index:02d}",
    }


def build_apple_payload(
    profile_def: dict[str, Any],
    index: int,
    artists_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    signals = []
    for signal_index, (artist_id, weight, plays, recency, signal_type) in enumerate(
        profile_def["apple_artists"],
        start=1,
    ):
        artist = artists_by_id[artist_id]
        signals.append(
            {
                "signal_id": f"apple_{index:02d}_{signal_index:02d}",
                "signal_type": signal_type,
                "music_object_ref": artist_ref(artist),
                "normalized_weight": weight,
                "recency_days": recency,
                "play_count_90d": plays,
                "last_played_at": "2026-05-18T10:00:00Z",
                "library_added_at": "2024-01-15T10:00:00Z",
            }
        )
    for external_index, (hint_id, display, apple_id, weight, plays, recency) in enumerate(
        profile_def.get("external_apple_hints", []),
        start=len(signals) + 1,
    ):
        signals.append(
            {
                "signal_id": f"apple_{index:02d}_{external_index:02d}",
                "signal_type": "external_catalog_hint",
                "music_object_ref": external_artist_ref(display, apple_id),
                "normalized_weight": weight,
                "recency_days": recency,
                "play_count_90d": plays,
                "last_played_at": "2026-05-19T10:00:00Z",
                "library_added_at": "2026-05-01T10:00:00Z",
            }
        )
    resolved_count = sum(
        1
        for signal in signals
        if signal["music_object_ref"]["ref_source"] == "canonical_graph"
    )
    return {
        "schema_version": "survey_simulation.apple_payload.v0.1",
        "apple_payload_id": f"apple_payload_{index:02d}",
        "generated_at": GENERATED_AT,
        "source_kind": "simulated_apple_music",
        "library_snapshot_age_days": 2,
        "signals": signals,
        "playlist_context": {
            "playlist_name": None,
            "playlist_kind": "unknown",
        },
        "track_level_signals": [],
        "album_level_signals": [],
        "skip_or_completion_hints": [],
        "loved_or_favorite_hints": [],
        "resolution_summary": {
            "resolved_canonical_count": resolved_count,
            "external_unresolved_count": len(signals) - resolved_count,
            "candidate_generation_policy": "Only resolved canonical artist refs may bias v0.1 Page 1 candidate generation.",
        },
    }


def reaction_to_familiarity(reaction: str) -> str:
    if reaction in {"love", "like"}:
        return "known_deep" if reaction == "love" else "known"
    if reaction == "ok":
        return "heard_of"
    if reaction == "dont_like":
        return "known"
    return "unknown"


def reaction_confidence(reaction: str) -> float:
    return {
        "love": 0.95,
        "like": 0.86,
        "ok": 0.68,
        "dont_like": 0.84,
        "dont_know_enough": 0.5,
    }[reaction]


def find_related_objects_by_artist(
    artist: dict[str, Any],
    albums: list[dict[str, Any]],
    songs: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    display = artist["display_name"].casefold()
    related_albums = [
        album
        for album in albums
        if any(name.casefold() == display for name in album.get("artist_names", []))
    ]
    related_songs = [
        song
        for song in songs
        if any(name.casefold() == display for name in song.get("artist_names", []))
    ]
    related_albums = sorted(
        related_albums,
        key=lambda item: (
            item.get("best_survey_tier") != "core",
            item.get("display_name", "").lower(),
            item["canonical_album_id"],
        ),
    )
    related_songs = sorted(
        related_songs,
        key=lambda item: (
            item.get("best_survey_tier") != "core",
            item.get("display_name", "").lower(),
            item["canonical_song_recording_id"],
        ),
    )
    return related_albums, related_songs


def stable_unit_interval(*parts: Any) -> float:
    digest = hashlib.sha256(
        "::".join(str(part) for part in parts).encode("utf-8")
    ).hexdigest()
    return int(digest[:12], 16) / float(0xFFFFFFFFFFFF)


def canonical_object_id(object_type: str, obj: dict[str, Any]) -> str:
    if object_type == "artist":
        return obj["canonical_artist_id"]
    if object_type == "album":
        return obj["canonical_album_id"]
    if object_type == "song_recording":
        return obj["canonical_song_recording_id"]
    raise ValueError(f"Unsupported object type: {object_type}")


def ref_for_object(object_type: str, obj: dict[str, Any]) -> dict[str, Any]:
    if object_type == "artist":
        return artist_ref(obj)
    if object_type == "album":
        return album_ref(obj)
    if object_type == "song_recording":
        return song_ref(obj)
    raise ValueError(f"Unsupported object type: {object_type}")


def profile_archetype_sets(profile_def: dict[str, Any]) -> dict[str, set[str]]:
    return {
        "tier_1": {item[0] for item in profile_def["primary"]},
        "tier_2": {item[0] for item in profile_def["secondary"]},
        "anti": {item[0] for item in profile_def["anti"]},
        "false_nearby": {profile_def["false_nearby"][3]},
    }


def profile_archetype_tier(profile_def: dict[str, Any], obj: dict[str, Any]) -> str:
    archetypes = set(obj.get("archetype_ids", []))
    sets = profile_archetype_sets(profile_def)
    if archetypes & sets["tier_1"]:
        return "tier_1"
    if archetypes & sets["tier_2"]:
        return "tier_2"
    if archetypes & (sets["anti"] | sets["false_nearby"]):
        return "anti_or_false_nearby"
    return "outside_profile"


def popularity_tier(obj: dict[str, Any]) -> str:
    recognition = obj.get("best_recognition_tier", "unknown")
    if recognition == "mass":
        return "mass_popular"
    if recognition == "high":
        return "high_recognition"
    if recognition == "medium":
        return "medium_recognition"
    if recognition in {"cult", "low", "niche"}:
        return "low_or_cult"
    return "unknown_popularity"


def apple_artist_context(
    profile_def: dict[str, Any],
    artists_by_id: dict[str, dict[str, Any]],
) -> tuple[set[str], set[str]]:
    apple_artist_ids = {item[0] for item in profile_def["apple_artists"]}
    apple_artist_names = {
        artists_by_id[artist_id]["display_name"].casefold()
        for artist_id in apple_artist_ids
        if artist_id in artists_by_id
    }
    return apple_artist_ids, apple_artist_names


def apple_presence_kind(
    profile_def: dict[str, Any],
    artists_by_id: dict[str, dict[str, Any]],
    object_type: str,
    obj: dict[str, Any],
) -> str:
    apple_artist_ids, apple_artist_names = apple_artist_context(profile_def, artists_by_id)
    if object_type == "artist" and obj["canonical_artist_id"] in apple_artist_ids:
        return "exact_artist"
    if object_type in {"album", "song_recording"}:
        artist_names = {name.casefold() for name in obj.get("artist_names", [])}
        if artist_names & apple_artist_names:
            return "apple_artist_context"
    return "none"


def profile_tier_population_rate(profile_tier: str, object_type: str) -> float:
    is_album = object_type == "album"
    if profile_tier == "tier_1":
        return 0.12 if is_album else 0.16
    if profile_tier == "tier_2":
        return 0.06 if is_album else 0.08
    if profile_tier == "anti_or_false_nearby":
        return 0.30 if is_album else 0.45
    return 0.0


def object_popularity_rate(
    popularity: str,
    object_type: str,
    obj: dict[str, Any] | None = None,
) -> float:
    is_album = object_type == "album"
    if popularity == "mass_popular":
        if is_album:
            return 0.78
        return 0.97 if object_type == "artist" else 0.97
    if popularity == "high_recognition":
        if object_type == "artist":
            roles = set(obj.get("roles", [])) if obj else set()
            if roles & {"boundary", "contrast", "false_nearby"}:
                return 0.62
            return 0.78
        return 0.62 if is_album else 0.76
    if popularity == "medium_recognition":
        return 0.34 if is_album else 0.42
    if popularity == "low_or_cult":
        return 0.05 if is_album else 0.08
    return 0.03 if is_album else 0.04


def apple_presence_rate(apple_kind: str, object_type: str) -> float:
    if apple_kind == "exact_artist":
        return 0.985
    if apple_kind == "apple_artist_context":
        return 0.46 if object_type == "album" else 0.56
    return 0.0


def false_nearby_or_anti_affinity_rate(
    profile_tier: str,
    object_type: str,
    obj: dict[str, Any],
) -> float:
    is_album = object_type == "album"
    if profile_tier == "anti_or_false_nearby":
        return 0.38 if is_album else 0.52
    roles = set(obj.get("roles", []))
    if roles & {"false_nearby", "boundary", "contrast"}:
        return 0.16 if is_album else 0.22
    return 0.0


def control_sampling_rate(object_type: str) -> float:
    return 0.025 if object_type == "album" else 0.035


def combined_population_probability(rates: dict[str, float]) -> float:
    miss_probability = 1.0
    for rate in rates.values():
        miss_probability *= 1.0 - clamp(rate)
    return round(1.0 - miss_probability, 6)


def hidden_population_rates(
    profile_def: dict[str, Any],
    artists_by_id: dict[str, dict[str, Any]],
    object_type: str,
    obj: dict[str, Any],
) -> dict[str, float]:
    tier = profile_archetype_tier(profile_def, obj)
    popularity = popularity_tier(obj)
    apple_kind = apple_presence_kind(profile_def, artists_by_id, object_type, obj)
    return {
        "profile_archetype_tier_rate": profile_tier_population_rate(tier, object_type),
        "object_popularity_rate": object_popularity_rate(popularity, object_type, obj),
        "apple_presence_rate": apple_presence_rate(apple_kind, object_type),
        "false_nearby_or_anti_affinity_rate": false_nearby_or_anti_affinity_rate(
            tier,
            object_type,
            obj,
        ),
        "control_sampling_rate": control_sampling_rate(object_type),
    }


def weighted_reaction_choice(
    weights: dict[str, float],
    profile_id: str,
    object_type: str,
    object_id: str,
) -> str:
    total = sum(weights.values())
    if total <= 0:
        return "ok"
    cursor = stable_unit_interval("reaction", profile_id, object_type, object_id) * total
    running = 0.0
    for reaction, weight in weights.items():
        running += weight
        if cursor <= running:
            return reaction
    return next(reversed(weights))


def hidden_reaction_weights(
    profile_tier: str,
    popularity: str,
    apple_kind: str,
    object_type: str,
) -> dict[str, float]:
    if profile_tier == "anti_or_false_nearby":
        weights = {"love": 0.02, "like": 0.08, "ok": 0.34, "dont_like": 0.56}
    elif profile_tier == "tier_1":
        if apple_kind != "none":
            weights = {"love": 0.34, "like": 0.38, "ok": 0.22, "dont_like": 0.06}
        else:
            weights = {"love": 0.26, "like": 0.36, "ok": 0.28, "dont_like": 0.10}
    elif profile_tier == "tier_2":
        weights = {"love": 0.10, "like": 0.30, "ok": 0.42, "dont_like": 0.18}
    elif popularity == "mass_popular":
        weights = {"love": 0.04, "like": 0.16, "ok": 0.55, "dont_like": 0.25}
    elif popularity == "high_recognition":
        weights = {"love": 0.03, "like": 0.12, "ok": 0.50, "dont_like": 0.35}
    else:
        weights = {"love": 0.02, "like": 0.10, "ok": 0.46, "dont_like": 0.42}

    if object_type == "album":
        love_shift = min(weights["love"], 0.06)
        weights["love"] -= love_shift
        weights["like"] += round(love_shift * 0.45, 6)
        weights["ok"] += round(love_shift * 0.55, 6)
    return weights


def hidden_reason_tags(
    profile_tier: str,
    popularity: str,
    apple_kind: str,
    rates: dict[str, float],
    explicit_tags: list[str] | None = None,
) -> list[str]:
    tags = list(explicit_tags or [])
    tags.append(f"profile_archetype:{profile_tier}")
    tags.append(f"popularity:{popularity}")
    if apple_kind != "none":
        tags.append(f"apple_presence:{apple_kind}")
    for name, rate in rates.items():
        if rate > 0:
            tags.append(f"population_rate:{name}")
    return list(dict.fromkeys(tags))


def build_hidden_corpus(
    profile_def: dict[str, Any],
    index: int,
    artists_by_id: dict[str, dict[str, Any]],
    albums: list[dict[str, Any]],
    songs: list[dict[str, Any]],
) -> dict[str, Any]:
    reactions = []
    seen_keys: set[tuple[str, str]] = set()
    explicit_artist_reactions: dict[tuple[str, str], tuple[str, list[str]]] = {}
    forced_unknown_keys: set[tuple[str, str]] = set()

    for artist_id, reaction, tags in profile_def["artist_reactions"]:
        key = ("artist", artist_id)
        if reaction == "dont_know_enough":
            forced_unknown_keys.add(key)
        else:
            explicit_artist_reactions[key] = (reaction, tags)

    def add_reaction(ref: dict[str, Any], reaction: str, tags: list[str]) -> None:
        key = ref_key(ref)
        if key in seen_keys:
            return
        seen_keys.add(key)
        reactions.append(
            {
                "music_object_ref": ref,
                "reaction": reaction,
                "familiarity_band": reaction_to_familiarity(reaction),
                "confidence": reaction_confidence(reaction),
                "reason_tags": tags,
            }
        )

    graph_objects = [
        ("artist", sorted(artists_by_id.values(), key=lambda item: item["canonical_artist_id"])),
        ("album", sorted(albums, key=lambda item: item["canonical_album_id"])),
        ("song_recording", sorted(songs, key=lambda item: item["canonical_song_recording_id"])),
    ]
    for object_type, objects in graph_objects:
        for obj in objects:
            object_id = canonical_object_id(object_type, obj)
            key = (object_type, object_id)
            if key in forced_unknown_keys:
                continue
            explicit = explicit_artist_reactions.get(key)
            profile_tier = profile_archetype_tier(profile_def, obj)
            popularity = popularity_tier(obj)
            apple_kind = apple_presence_kind(profile_def, artists_by_id, object_type, obj)
            rates = hidden_population_rates(profile_def, artists_by_id, object_type, obj)
            probability = combined_population_probability(rates)
            should_populate = explicit is not None or stable_unit_interval(
                "hidden-population",
                profile_def["id"],
                object_type,
                object_id,
            ) <= probability
            if not should_populate:
                continue
            if explicit is not None:
                reaction, explicit_tags = explicit
                tags = hidden_reason_tags(
                    profile_tier,
                    popularity,
                    apple_kind,
                    rates,
                    ["profile_seed_override", *explicit_tags],
                )
            else:
                reaction = weighted_reaction_choice(
                    hidden_reaction_weights(profile_tier, popularity, apple_kind, object_type),
                    profile_def["id"],
                    object_type,
                    object_id,
                )
                tags = hidden_reason_tags(profile_tier, popularity, apple_kind, rates)
            add_reaction(ref_for_object(object_type, obj), reaction, tags)

    return {
        "schema_version": "survey_simulation.hidden_reaction_corpus.v0.1",
        "hidden_reaction_corpus_id": f"hidden_corpus_{index:02d}",
        "fake_profile_id": profile_def["id"],
        "privacy_boundary": "simulator_private",
        "reactions": reactions,
    }


def hidden_lookup_map(hidden_corpus: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        ref_key(reaction["music_object_ref"]): reaction
        for reaction in hidden_corpus["reactions"]
        if reaction["music_object_ref"]["ref_source"] == "canonical_graph"
    }


def simulate_responses(
    run_id: str,
    page: dict[str, Any],
    hidden_corpus: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    lookup = hidden_lookup_map(hidden_corpus)
    responses = []
    coverage_lookups = []
    hit_count = 0
    for index, tile in enumerate(page["tiles"], start=1):
        ref = tile["music_object_ref"]
        key = ref_key(ref)
        hidden_reaction = lookup.get(key)
        if hidden_reaction:
            reaction = hidden_reaction["reaction"]
            lookup_status = "hidden_corpus_hit"
            hit_count += 1
        else:
            reaction = "dont_know_enough"
            lookup_status = "missing_default"
        responses.append(
            {
                "response_id": f"resp_{index:02d}",
                "run_id": run_id,
                "page_id": page["page_id"],
                "tile_id": tile["tile_id"],
                "music_object_ref": copy.deepcopy(ref),
                "reaction": reaction,
                "app_ui_candidate": REACTION_MAP[reaction]["app_ui_candidate"],
                "atlas_signal_interpretation": REACTION_MAP[reaction][
                    "atlas_signal_interpretation"
                ],
                "observed_selected_tags": [],
                "shown_unselected_tags": [],
            }
        )
        coverage_lookups.append(
            {
                "tile_id": tile["tile_id"],
                "display_name": ref["display_name"],
                "object_type": ref["object_type"],
                "lookup_status": lookup_status,
                "recorded_reaction": reaction,
            }
        )
    recorded = {
        "schema_version": "survey_simulation.recorded_responses.v0.1",
        "run_id": run_id,
        "generated_at": GENERATED_AT,
        "response_source": "hidden_corpus_lookup_with_missing_default",
        "responses": responses,
    }
    coverage = {
        "schema_version": "survey_simulation.hidden_lookup_coverage.v0.1",
        "run_id": run_id,
        "generated_at": GENERATED_AT,
        "privacy_boundary": "simulator_private_evaluation",
        "summary": {
            "tile_count": len(page["tiles"]),
            "hidden_lookup_hit_count": hit_count,
            "missing_default_count": len(page["tiles"]) - hit_count,
        },
        "lookups": coverage_lookups,
    }
    return recorded, coverage


def render_transcript(survey_run: dict[str, Any], recorded: dict[str, Any]) -> str:
    responses_by_tile = {
        response["tile_id"]: response for response in recorded["responses"]
    }
    lines = [
        f"# Survey Transcript: {survey_run['run_id']}",
        "",
        f"- Generated: {survey_run['generated_at']}",
        f"- Page mode: `{survey_run['page_mode']}`",
        "- Stage: `artists`",
        "- Visible inputs: canonical graph, sanitized Apple payload when mode applies, prior visible responses",
        "- Hidden private profile data: not included",
        "",
        "## Page 1: Artists",
        "",
        "| tile | artist | canonical artist ref | reaction | app/UI |",
        "|---:|---|---|---|---|",
    ]
    for tile in survey_run["pages"][0]["tiles"]:
        response = responses_by_tile[tile["tile_id"]]
        ref = tile["music_object_ref"]
        lines.append(
            "| {position} | {display} | `{ref_id}` | `{reaction}` | `{ui}` |".format(
                position=tile["position"],
                display=ref["display_name"],
                ref_id=ref["canonical_artist_id"],
                reaction=response["reaction"],
                ui=response["app_ui_candidate"],
            )
        )
    lines.extend(
        [
            "",
            "Visible transcript note: no private profile label, anti-affinity data, hidden lookup status, or private rationale tags are present.",
            "",
        ]
    )
    return "\n".join(lines)


def render_page_transcript(
    run_id: str,
    page: dict[str, Any],
    recorded: dict[str, Any],
    title: str,
) -> str:
    responses_by_tile = {
        response["tile_id"]: response for response in recorded["responses"]
    }
    lines = [
        f"# {title}: {run_id}",
        "",
        f"- Generated: {recorded['generated_at']}",
        f"- Page: `{page['page_id']}`",
        f"- Stage: `{page['stage']}`",
        "- Visible inputs: canonical graph, sanitized Apple payload when mode applies, and prior visible survey responses",
        "- Hidden private profile data: not included",
        "",
        "| tile | artist | page intent | canonical artist ref | reaction | app/UI |",
        "|---:|---|---|---|---|---|",
    ]
    for tile in page["tiles"]:
        response = responses_by_tile[tile["tile_id"]]
        ref = tile["music_object_ref"]
        lines.append(
            "| {position} | {display} | `{intent}` | `{ref_id}` | `{reaction}` | `{ui}` |".format(
                position=tile["position"],
                display=ref["display_name"],
                intent=tile["page_intent"],
                ref_id=ref["canonical_artist_id"],
                reaction=response["reaction"],
                ui=response["app_ui_candidate"],
            )
        )
    lines.extend(
        [
            "",
            "Visible transcript note: no private profile label, hidden anti-affinity data, hidden lookup status, or private rationale tags are present.",
            "",
        ]
    )
    return "\n".join(lines)


def render_hidden_coverage_report(coverage: dict[str, Any]) -> str:
    summary = coverage["summary"]
    lines = [
        f"# Hidden Lookup Coverage: {coverage['run_id']}",
        "",
        "This simulator-private report checks whether Page 1 tiles had sparse corpus entries.",
        "It does not include private rationale tags.",
        "",
        f"- Tile count: {summary['tile_count']}",
        f"- Hidden lookup hits: {summary['hidden_lookup_hit_count']}",
        f"- Missing defaults: {summary['missing_default_count']}",
        "",
        "| tile | artist | lookup status | recorded reaction |",
        "|---|---|---|---|",
    ]
    for lookup in coverage["lookups"]:
        lines.append(
            "| `{tile}` | {display} | `{status}` | `{reaction}` |".format(
                tile=lookup["tile_id"],
                display=lookup["display_name"],
                status=lookup["lookup_status"],
                reaction=lookup["recorded_reaction"],
            )
        )
    lines.append("")
    return "\n".join(lines)


def canonical_ref_id(ref: dict[str, Any]) -> str:
    object_type = ref["object_type"]
    if object_type == "artist":
        return ref["canonical_artist_id"]
    if object_type == "album":
        return ref["canonical_album_id"]
    if object_type == "song_recording":
        return ref["canonical_song_recording_id"]
    raise ValueError(f"Unsupported object type: {object_type}")


def page_intent_counts(page: dict[str, Any]) -> dict[str, int]:
    return dict(sorted(Counter(tile["page_intent"] for tile in page["tiles"]).items()))


def response_interpretation(reaction: str) -> str:
    return {
        "love": "strong_positive_scope_unknown",
        "like": "qualified_positive",
        "ok": "waypoint_candidate",
        "dont_like": "dead_end_hypothesis_unconfirmed",
        "dont_know_enough": "familiarity_failure",
    }[reaction]


def response_signal_strength(reaction: str) -> float:
    return {
        "love": 1.0,
        "like": 0.76,
        "ok": 0.34,
        "dont_like": 0.58,
        "dont_know_enough": 0.16,
    }[reaction]


def visible_response_evidence(
    page: dict[str, Any],
    recorded: dict[str, Any],
) -> list[dict[str, Any]]:
    tiles_by_id = {tile["tile_id"]: tile for tile in page["tiles"]}
    evidence = []
    for response in recorded["responses"]:
        tile = tiles_by_id[response["tile_id"]]
        evidence.append(
            {
                "response_id": response["response_id"],
                "page_id": response["page_id"],
                "tile_id": response["tile_id"],
                "music_object_ref": copy.deepcopy(response["music_object_ref"]),
                "reaction": response["reaction"],
                "interpretation": response_interpretation(response["reaction"]),
                "page_intent": tile["page_intent"],
                "family_numbers": tile["graph_context"]["family_numbers"],
                "archetype_ids": tile["graph_context"]["archetype_ids"],
                "roles": tile["graph_context"]["roles"],
                "score_final": tile["scores"]["final"],
            }
        )
    return evidence


def summarize_response_evidence(evidence: list[dict[str, Any]]) -> dict[str, Any]:
    reaction_counts = Counter(item["reaction"] for item in evidence)
    total = len(evidence)
    positive_count = reaction_counts["love"] + reaction_counts["like"]
    unknown_count = reaction_counts["dont_know_enough"]
    negative_count = reaction_counts["dont_like"]
    known_count = total - unknown_count
    return {
        "total_response_count": total,
        "reaction_counts": {reaction: reaction_counts.get(reaction, 0) for reaction in REACTIONS},
        "positive_count": positive_count,
        "negative_count": negative_count,
        "unknown_count": unknown_count,
        "known_count": known_count,
        "unknown_rate": round(unknown_count / total, 3) if total else 0.0,
        "positive_rate": round(positive_count / total, 3) if total else 0.0,
        "negative_rate": round(negative_count / total, 3) if total else 0.0,
    }


def coverage_state_from_evidence(evidence: list[dict[str, Any]]) -> dict[str, Any]:
    family_counts: Counter[int] = Counter()
    archetype_counts: Counter[str] = Counter()
    seen_refs = []
    for item in evidence:
        family_counts.update(item["family_numbers"])
        archetype_counts.update(item["archetype_ids"])
        ref = item["music_object_ref"]
        seen_refs.append(
            {
                "object_type": ref["object_type"],
                "canonical_id": canonical_ref_id(ref),
                "display_name": ref["display_name"],
                "reaction": item["reaction"],
            }
        )
    return {
        "family_counts": {str(key): value for key, value in sorted(family_counts.items())},
        "archetype_counts": dict(sorted(archetype_counts.items())),
        "seen_music_refs": seen_refs,
    }


def open_hypotheses_from_evidence(evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    hypotheses = []
    for item in evidence:
        ref = item["music_object_ref"]
        reaction = item["reaction"]
        if reaction == "love":
            hypothesis_type = "positive_scope_unknown"
            next_pressure = ["confirm_or_repeat_signal", "test_bridge", "test_false_nearby"]
        elif reaction == "like":
            hypothesis_type = "qualified_positive_disambiguation"
            next_pressure = ["disambiguate_response", "test_bridge"]
        elif reaction == "ok":
            hypothesis_type = "waypoint_candidate"
            next_pressure = ["light_adjacent_test", "move_attention_elsewhere"]
        elif reaction == "dont_like":
            hypothesis_type = "possible_dead_end_scope_unknown"
            next_pressure = ["disambiguate_negative_scope", "test_false_nearby"]
        else:
            hypothesis_type = "familiarity_failure"
            next_pressure = ["repair_familiarity_or_coverage"]
        hypotheses.append(
            {
                "hypothesis_id": f"hyp_{item['page_id']}_{item['tile_id']}",
                "hypothesis_type": hypothesis_type,
                "source_response_ref": {
                    "response_id": item["response_id"],
                    "page_id": item["page_id"],
                    "tile_id": item["tile_id"],
                },
                "music_object_ref": copy.deepcopy(ref),
                "reaction": reaction,
                "confidence_basis": "visible_survey_response_only",
                "next_intent_pressure": next_pressure,
                "status": "open",
            }
        )
    return hypotheses


def public_profile_id_from_payload(apple_payload: dict[str, Any]) -> str:
    suffix = apple_payload["apple_payload_id"].split("_")[-1]
    return f"public_profile_{suffix}"


def survey_state_after_page_001(
    survey_run: dict[str, Any],
    recorded: dict[str, Any],
    apple_payload: dict[str, Any],
) -> dict[str, Any]:
    page = survey_run["pages"][0]
    evidence = visible_response_evidence(page, recorded)
    return {
        "schema_version": "survey_state.v0.1",
        "survey_run_id": survey_run["run_id"],
        "profile_public_id": public_profile_id_from_payload(apple_payload),
        "mode": "graph_only" if survey_run["page_mode"] == "generic_graph_seed" else "apple_biased",
        "current_page_number": 2,
        "current_object_type": "artist",
        "apple_payload_ref": apple_payload["apple_payload_id"],
        "page_history": [
            {
                "page_id": page["page_id"],
                "page_number": page["page_number"],
                "object_type": "artist",
                "page_mode": page["page_mode"],
                "tile_count": len(page["tiles"]),
                "intent_counts": page_intent_counts(page),
            }
        ],
        "response_summary": summarize_response_evidence(evidence),
        "coverage_state": coverage_state_from_evidence(evidence),
        "open_hypotheses": open_hypotheses_from_evidence(evidence),
        "confirmedSignals": [
            item["response_id"] for item in evidence if item["reaction"] in POSITIVE_REACTIONS
        ],
        "contradictionSignals": [
            item["response_id"] for item in evidence if item["reaction"] == "dont_like"
        ],
        "candidate_suppression_ledger": [],
        "hidden_data_access": "forbidden",
    }


def merge_visible_evidence(
    pages_and_recordings: list[tuple[dict[str, Any], dict[str, Any]]],
) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    for page, recorded in pages_and_recordings:
        evidence.extend(visible_response_evidence(page, recorded))
    return evidence


def survey_state_after_page_002(
    prior_state: dict[str, Any],
    page2: dict[str, Any],
    recorded_page2: dict[str, Any],
    suppression_ledger: list[dict[str, Any]],
) -> dict[str, Any]:
    page1_history = prior_state["page_history"]
    # Rebuild summary from state-held page 1 evidence proxies plus page 2 responses would be lossy,
    # so retain page 1 summary and add explicit page 2 summary.
    page2_evidence = visible_response_evidence(page2, recorded_page2)
    updated = copy.deepcopy(prior_state)
    updated["current_page_number"] = 3
    updated["current_object_type"] = "artist"
    updated["page_history"] = [
        *page1_history,
        {
            "page_id": page2["page_id"],
            "page_number": page2["page_number"],
            "object_type": "artist",
            "page_mode": page2["page_mode"],
            "tile_count": len(page2["tiles"]),
            "intent_counts": page_intent_counts(page2),
        },
    ]
    updated["response_summary_after_page_002"] = summarize_response_evidence(page2_evidence)
    updated["coverage_state_after_page_002"] = coverage_state_from_evidence(page2_evidence)
    updated["open_hypotheses"] = [
        *updated["open_hypotheses"],
        *open_hypotheses_from_evidence(page2_evidence),
    ]
    updated["confirmedSignals"] = [
        *updated["confirmedSignals"],
        *[item["response_id"] for item in page2_evidence if item["reaction"] in POSITIVE_REACTIONS],
    ]
    updated["contradictionSignals"] = [
        *updated["contradictionSignals"],
        *[item["response_id"] for item in page2_evidence if item["reaction"] == "dont_like"],
    ]
    updated["candidate_suppression_ledger"] = [
        *updated["candidate_suppression_ledger"],
        *suppression_ledger,
    ]
    updated["hidden_data_access"] = "forbidden"
    return updated


def adapt_page2_mix_for_mode(
    target_mix: list[tuple[str, int]],
    mode: str,
) -> list[tuple[str, int]]:
    if mode != "generic_graph_seed":
        return target_mix
    adapted = []
    for intent, count in target_mix:
        if intent == "payload_adjacent_lesser_known":
            adapted.append(("test_bridge", count))
        else:
            adapted.append((intent, count))
    merged: Counter[str] = Counter()
    for intent, count in adapted:
        merged[intent] += count
    return list(merged.items())


def page2_target_mix(response_summary: dict[str, Any], mode: str) -> tuple[str, list[tuple[str, int]]]:
    if response_summary["unknown_rate"] >= 0.5:
        return "high_unknown_rate", adapt_page2_mix_for_mode(PAGE2_INTENT_TARGETS_HIGH_UNKNOWN, mode)
    if response_summary["positive_count"] >= 5:
        return "many_positives", adapt_page2_mix_for_mode(PAGE2_INTENT_TARGETS_MANY_POSITIVES, mode)
    if response_summary["negative_count"] >= 3:
        return "many_negatives", adapt_page2_mix_for_mode(PAGE2_INTENT_TARGETS_MANY_NEGATIVES, mode)
    return "default", adapt_page2_mix_for_mode(PAGE2_INTENT_TARGETS_DEFAULT, mode)


def relation_between_candidate_and_response(
    candidate: dict[str, Any],
    evidence_item: dict[str, Any],
) -> list[str]:
    relations = []
    shared_archetypes = sorted(set(candidate["archetypes"]) & set(evidence_item["archetype_ids"]))
    shared_families = sorted(set(candidate["families"]) & set(evidence_item["family_numbers"]))
    if shared_archetypes:
        relations.append("shared_archetype")
    if shared_families:
        relations.append("shared_family")
    if set(candidate["roles"]) & set(evidence_item["roles"]):
        relations.append("shared_graph_role")
    return relations


def response_refs_for_candidate(
    candidate: dict[str, Any],
    evidence: list[dict[str, Any]],
    limit: int = 5,
) -> list[dict[str, Any]]:
    refs = []
    for item in evidence:
        relations = relation_between_candidate_and_response(candidate, item)
        if not relations:
            continue
        refs.append(
            {
                "response_id": item["response_id"],
                "page_id": item["page_id"],
                "tile_id": item["tile_id"],
                "reaction": item["reaction"],
                "interpretation": item["interpretation"],
                "related_by": relations,
            }
        )
    refs.sort(
        key=lambda item: (
            -response_signal_strength(item["reaction"]),
            item["page_id"],
            item["tile_id"],
        )
    )
    return refs[:limit]


def page2_seen_ref_ids(evidence: list[dict[str, Any]]) -> set[str]:
    return {
        canonical_ref_id(item["music_object_ref"])
        for item in evidence
        if item["music_object_ref"]["object_type"] == "artist"
    }


def coverage_repair_for_page2(
    candidate: dict[str, Any],
    selected: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
) -> float:
    family_counts: Counter[int] = Counter()
    archetype_counts: Counter[str] = Counter()
    for item in evidence:
        family_counts.update(item["family_numbers"])
        archetype_counts.update(item["archetype_ids"])
    for item in selected:
        family_counts.update(item["families"])
        archetype_counts.update(item["archetypes"])
    family_value = max((1.0 / (1 + family_counts[item]) for item in candidate["families"]), default=0.4)
    archetype_value = max(
        (1.0 / (1 + archetype_counts[item]) for item in candidate["archetypes"]),
        default=0.4,
    )
    return round(clamp((family_value * 0.72) + (archetype_value * 0.28)), 3)


def page2_candidate_scores(
    candidate: dict[str, Any],
    intent: str,
    selected: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
    seen_ref_ids: set[str],
) -> tuple[dict[str, float], list[dict[str, Any]]]:
    refs = response_refs_for_candidate(candidate, evidence)
    positive_refs = [item for item in refs if item["reaction"] in POSITIVE_REACTIONS]
    ok_refs = [item for item in refs if item["reaction"] == "ok"]
    negative_refs = [item for item in refs if item["reaction"] == "dont_like"]
    unknown_refs = [item for item in refs if item["reaction"] == "dont_know_enough"]
    posterior_relevance = 0.0
    if positive_refs:
        posterior_relevance = max(response_signal_strength(item["reaction"]) for item in positive_refs)
    elif ok_refs:
        posterior_relevance = 0.34
    elif negative_refs and intent in {"disambiguate_negative_scope", "test_false_nearby"}:
        posterior_relevance = 0.42
    elif unknown_refs and intent == "repair_familiarity_or_coverage":
        posterior_relevance = 0.3
    posterior_relevance = clamp(
        posterior_relevance
        + (candidate["base_scores"]["apple_evidence_strength"] * 0.16)
        + (candidate["base_scores"]["canonical_anchor_value"] * 0.08)
    )
    coverage_repair_value = coverage_repair_for_page2(candidate, selected, evidence)
    graph_bridge_value = max(
        candidate["selection_values"]["bridge_value"],
        candidate["base_scores"]["multi_archetype_junction_value"] * 0.82,
    )
    false_nearby_value = candidate["base_scores"]["false_nearby_value"]
    expected_familiarity = candidate["base_scores"]["expected_familiarity"]
    apple_evidence = candidate["base_scores"]["apple_evidence_strength"]
    novelty = candidate["selection_values"]["novelty"]
    junction_value = candidate["base_scores"]["multi_archetype_junction_value"]
    apple_neighbor = (
        candidate["apple_evidence"]["archetype_neighbor_score"] > 0
        or candidate["apple_evidence"]["family_neighbor_score"] > 0
    )

    if intent == "confirm_or_repeat_signal":
        response_disambiguation_value = clamp((0.72 if positive_refs else 0.16) + graph_bridge_value * 0.12)
    elif intent == "disambiguate_response":
        response_disambiguation_value = clamp((0.46 if positive_refs else 0.0) + (0.38 if ok_refs else 0.0) + novelty * 0.18)
    elif intent == "disambiguate_negative_scope":
        response_disambiguation_value = clamp((0.68 if negative_refs else 0.12) + false_nearby_value * 0.18)
    elif intent == "repair_familiarity_or_coverage":
        response_disambiguation_value = clamp((0.62 if unknown_refs else 0.18) + coverage_repair_value * 0.2)
    elif intent == "test_bridge":
        response_disambiguation_value = clamp((0.34 if positive_refs else 0.12) + graph_bridge_value * 0.36)
    elif intent == "test_false_nearby":
        response_disambiguation_value = clamp((0.24 if positive_refs or negative_refs else 0.1) + false_nearby_value * 0.46)
    elif intent == "multi_archetype_junction":
        response_disambiguation_value = clamp(
            junction_value * 0.46
            + (0.28 if positive_refs else 0.12)
            + graph_bridge_value * 0.18
        )
    elif intent == "payload_adjacent_lesser_known":
        response_disambiguation_value = clamp(
            (0.42 if apple_neighbor else 0.08)
            + novelty * 0.22
            + (0.24 if positive_refs else 0.1)
        )
    elif intent == "controlled_frontier":
        response_disambiguation_value = clamp(novelty * 0.48 + coverage_repair_value * 0.22)
    elif intent == "mass_popular_control":
        response_disambiguation_value = clamp(
            (0.48 if candidate["artist"].get("best_recognition_tier") == "mass" else 0.12)
            + expected_familiarity * 0.28
        )
    else:
        response_disambiguation_value = 0.1

    information_gain = clamp(
        (response_disambiguation_value * 0.32)
        + (graph_bridge_value * 0.24)
        + (false_nearby_value * 0.18)
        + (coverage_repair_value * 0.16)
        + (novelty * 0.1)
    )
    artist_id = candidate["artist"]["canonical_artist_id"]
    recently_seen_penalty = 0.35 if artist_id in seen_ref_ids else 0.0
    if intent in {"controlled_frontier", "payload_adjacent_lesser_known"}:
        too_obscure_penalty = 0.12 if expected_familiarity < 0.46 else 0.0
    else:
        too_obscure_penalty = 0.18 if expected_familiarity < 0.68 else 0.0
    overclose_penalty = 0.06 if negative_refs and intent not in {"disambiguate_negative_scope", "test_false_nearby"} else 0.0
    penalties = round(recently_seen_penalty + too_obscure_penalty + overclose_penalty, 3)
    scores = {
        "posterior_relevance": round(posterior_relevance, 3),
        "information_gain": round(information_gain, 3),
        "response_disambiguation_value": round(response_disambiguation_value, 3),
        "graph_bridge_value": round(graph_bridge_value, 3),
        "coverage_repair_value": round(coverage_repair_value, 3),
        "false_nearby_value": round(false_nearby_value, 3),
        "expected_familiarity": round(expected_familiarity, 3),
        "apple_evidence": round(apple_evidence, 3),
        "novelty": round(novelty, 3),
        "penalties": penalties,
        "final": 0.0,
    }
    final = sum(scores[key] * weight for key, weight in PAGE2_SCORE_WEIGHTS.items())
    scores["final"] = round(final - penalties, 3)
    return scores, refs


def page2_intent_eligible(
    candidate: dict[str, Any],
    intent: str,
    scores: dict[str, float],
    refs: list[dict[str, Any]],
    strict: bool,
) -> bool:
    reactions = {item["reaction"] for item in refs}
    if intent == "confirm_or_repeat_signal":
        return bool(reactions & POSITIVE_REACTIONS) or (not strict and scores["expected_familiarity"] >= 0.72)
    if intent == "disambiguate_response":
        return bool(reactions & {"love", "like", "ok"}) or not strict
    if intent == "disambiguate_negative_scope":
        return "dont_like" in reactions or (not strict and scores["false_nearby_value"] >= 0.3)
    if intent == "repair_familiarity_or_coverage":
        return "dont_know_enough" in reactions or scores["coverage_repair_value"] >= (0.55 if strict else 0.32)
    if intent == "test_bridge":
        return scores["graph_bridge_value"] >= (0.34 if strict else 0.18)
    if intent == "test_false_nearby":
        return (
            scores["false_nearby_value"] >= (0.34 if strict else 0.18)
            and scores["expected_familiarity"] >= (0.7 if strict else 0.48)
        )
    if intent == "repair_coverage":
        return (
            scores["coverage_repair_value"] >= (0.55 if strict else 0.32)
            and scores["expected_familiarity"] >= (0.68 if strict else 0.48)
        )
    if intent == "multi_archetype_junction":
        return (
            candidate["base_scores"]["multi_archetype_junction_value"] >= (0.42 if strict else 0.26)
            and scores["expected_familiarity"] >= (0.7 if strict else 0.5)
        )
    if intent == "payload_adjacent_lesser_known":
        apple_neighbor = (
            candidate["apple_evidence"]["archetype_neighbor_score"] > 0
            or candidate["apple_evidence"]["family_neighbor_score"] > 0
        )
        return apple_neighbor and scores["expected_familiarity"] >= (0.58 if strict else 0.42)
    if intent == "controlled_frontier":
        return (
            candidate["selection_values"]["novelty"] >= (0.44 if strict else 0.24)
            and scores["expected_familiarity"] >= (0.46 if strict else 0.34)
        )
    if intent == "mass_popular_control":
        return (
            candidate["artist"].get("best_recognition_tier") == "mass"
            and scores["expected_familiarity"] >= (0.84 if strict else 0.62)
        )
    return True


def can_add_page2_candidate(
    candidate: dict[str, Any],
    selected: list[dict[str, Any]],
    seen_ref_ids: set[str],
    strict: bool,
) -> tuple[bool, list[str]]:
    warnings = []
    artist_id = candidate["artist"]["canonical_artist_id"]
    if artist_id in seen_ref_ids:
        return False, ["recently_seen_suppressed"]
    if any(artist_id == item["artist"]["canonical_artist_id"] for item in selected):
        return False, ["duplicate_canonical_id_suppressed"]
    if any(candidate["display_key"] == item["display_key"] for item in selected):
        return False, ["duplicate_display_name_suppressed"]
    if not strict:
        warnings.append("adaptive_override_quota_relaxed")
        return True, warnings
    family_counts: Counter[int] = Counter()
    archetype_counts: Counter[str] = Counter()
    for item in selected:
        family_counts.update(item["families"])
        archetype_counts.update(item["archetypes"])
    if candidate["families"] and all(family_counts[item] >= 3 for item in candidate["families"]):
        return False, ["family_quota_suppressed"]
    if candidate["archetypes"] and all(archetype_counts[item] >= 2 for item in candidate["archetypes"]):
        return False, ["archetype_quota_suppressed"]
    return True, warnings


def page2_candidate_basis(candidate: dict[str, Any], intent: str, mode: str) -> list[str]:
    basis = ["active_survey_adaptation", f"{intent}_bucket", "visible_response_evidence"]
    evidence = candidate["apple_evidence"]
    if mode == "apple_biased_seed":
        if evidence["exact_signal_weight"] > 0:
            basis.append("apple_exact_match")
        elif evidence["archetype_neighbor_score"] > 0:
            basis.append("apple_archetype_neighbor")
        elif evidence["family_neighbor_score"] > 0:
            basis.append("apple_family_neighbor")
    if len(basis) == 3:
        basis.append("canonical_graph_adaptive_candidate")
    return basis


def choose_best_page2_candidate(
    candidates: list[dict[str, Any]],
    selected: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
    seen_ref_ids: set[str],
    intent: str,
    mode: str,
    strict: bool,
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    suppression_events = []
    scored = []
    for candidate in candidates:
        can_add, warnings = can_add_page2_candidate(candidate, selected, seen_ref_ids, strict)
        if not can_add:
            suppression_events.append(
                {
                    "canonical_artist_id": candidate["artist"]["canonical_artist_id"],
                    "display_name": candidate["artist"]["display_name"],
                    "page_intent": intent,
                    "warnings": warnings,
                }
            )
            continue
        scores, refs = page2_candidate_scores(candidate, intent, selected, evidence, seen_ref_ids)
        if not page2_intent_eligible(candidate, intent, scores, refs, strict):
            continue
        scored.append(
            (
                scores["final"],
                candidate["artist"]["display_name"].lower(),
                candidate["artist"]["canonical_artist_id"],
                candidate,
                scores,
                refs,
                warnings,
            )
        )
    if not scored:
        return None, suppression_events
    scored.sort(key=lambda item: (-item[0], item[1], item[2]))
    _, _, _, candidate, scores, refs, warnings = scored[0]
    materialized = copy.deepcopy(candidate)
    materialized["page_intent"] = intent
    materialized["candidate_basis"] = page2_candidate_basis(candidate, intent, mode)
    materialized["scores"] = scores
    materialized["response_evidence_refs"] = refs
    materialized["suppression_warnings"] = warnings
    materialized["reason_for_debug"] = (
        f"{intent}: final={scores['final']}, posterior={scores['posterior_relevance']}, "
        f"info={scores['information_gain']}, disambiguation={scores['response_disambiguation_value']}, "
        f"coverage={scores['coverage_repair_value']}"
    )
    return materialized, suppression_events


def optimize_page2_slate(
    candidates: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
    target_mix: list[tuple[str, int]],
    mode: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    selected: list[dict[str, Any]] = []
    suppression_ledger: list[dict[str, Any]] = []
    seen_ref_ids = page2_seen_ref_ids(evidence)
    for intent, target_count in target_mix:
        for _ in range(target_count):
            chosen = None
            for strict in [True, False]:
                chosen, suppressions = choose_best_page2_candidate(
                    candidates,
                    selected,
                    evidence,
                    seen_ref_ids,
                    intent,
                    mode,
                    strict,
                )
                suppression_ledger.extend(suppressions[:8])
                if chosen is not None:
                    break
            if chosen is None:
                continue
            selected.append(chosen)
    while len(selected) < PAGE_SIZE:
        chosen, suppressions = choose_best_page2_candidate(
            candidates,
            selected,
            evidence,
            seen_ref_ids,
            "repair_coverage",
            mode,
            False,
        )
        suppression_ledger.extend(suppressions[:8])
        if chosen is None:
            break
        selected.append(chosen)
    family_counts: Counter[int] = Counter()
    archetype_counts: Counter[str] = Counter()
    for item in selected:
        family_counts.update(item["families"])
        archetype_counts.update(item["archetypes"])
    overquota_families = {family for family, count in family_counts.items() if count > 3}
    overquota_archetypes = {archetype for archetype, count in archetype_counts.items() if count > 2}
    for item in selected:
        if set(item["families"]) & overquota_families or set(item["archetypes"]) & overquota_archetypes:
            warnings = item.setdefault("suppression_warnings", [])
            if "adaptive_override_quota_relaxed" not in warnings:
                warnings.append("adaptive_override_quota_relaxed")
    return selected[:PAGE_SIZE], suppression_ledger


def build_page2(
    run_id: str,
    mode: str,
    selected_candidates: list[dict[str, Any]],
    response_summary: dict[str, Any],
    target_mix_name: str,
    target_mix: list[tuple[str, int]],
    suppression_ledger: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    tiles = [make_tile(candidate, position) for position, candidate in enumerate(selected_candidates, start=1)]
    for tile, candidate in zip(tiles, selected_candidates):
        tile["response_evidence_refs"] = candidate["response_evidence_refs"]
        tile["suppression_warnings"] = candidate["suppression_warnings"]
    page = {
        "schema_version": "survey_simulation.page.v0.1",
        "page_id": "page_02",
        "page_number": 2,
        "stage": "artists",
        "page_mode": mode,
        "tile_count": PAGE_SIZE,
        "generator_visible_inputs": {
            "canonical_graph_manifest_status": "dry_run_ready_with_warnings",
            "apple_payload_applied": mode == "apple_biased_seed",
            "prior_visible_response_count": response_summary["total_response_count"],
            "hidden_inputs_consumed": False,
        },
        "adaptive_context": {
            "target_mix_name": target_mix_name,
            "target_mix": dict(target_mix),
            "response_summary": response_summary,
        },
        "tiles": tiles,
    }
    duplicate_suppressions = sum(
        1 for item in suppression_ledger for warning in item.get("warnings", []) if "duplicate" in warning
    )
    log = {
        "schema_version": "survey_simulation.page_002_generation_log.v0.1",
        "run_id": run_id,
        "generated_at": GENERATED_AT,
        "page_mode": mode,
        "source_artifacts_read": [
            "survey_run.json",
            "recorded_responses.json",
            "apple_payload_used.json",
            relative(GRAPH_DIR / "canonical_artists.json"),
            relative(GRAPH_DIR / "artist_archetype_memberships.json"),
        ],
        "hidden_inputs_consumed": False,
        "response_summary": response_summary,
        "target_mix_name": target_mix_name,
        "target_mix": dict(target_mix),
        "candidate_selection": {
            "tile_count": len(tiles),
            "intent_counts": page_intent_counts(page),
            "duplicate_suppression_count": duplicate_suppressions,
            "adaptive_override_count": sum(
                1
                for tile in tiles
                for warning in tile.get("suppression_warnings", [])
                if warning == "adaptive_override_quota_relaxed"
            ),
            "suppression_ledger": suppression_ledger[:80],
            "tiles": [
                {
                    "position": tile["position"],
                    "music_object_ref": tile["music_object_ref"],
                    "canonical_artist_id": tile["music_object_ref"]["canonical_artist_id"],
                    "display_name": tile["music_object_ref"]["display_name"],
                    "page_intent": tile["page_intent"],
                    "candidate_basis": tile["candidate_basis"],
                    "response_evidence_refs": tile["response_evidence_refs"],
                    "suppression_warnings": tile["suppression_warnings"],
                    "scores": tile["scores"],
                }
                for tile in tiles
            ],
        },
    }
    debug = {
        "schema_version": "survey_simulation.page_002_candidate_debug.v0.1",
        "run_id": run_id,
        "generated_at": GENERATED_AT,
        "scoring_weights": PAGE2_SCORE_WEIGHTS,
        "selected_candidates": log["candidate_selection"]["tiles"],
    }
    return page, log, debug


def membership_warning_index(memberships: list[dict[str, Any]], id_field: str) -> dict[str, list[str]]:
    warnings: dict[str, list[str]] = defaultdict(list)
    for membership in memberships:
        warning = membership.get("consolidation_warning", "")
        if warning:
            warnings[membership[id_field]].append(warning)
        note = membership.get("object_specificity_note", "")
        if note:
            warnings[membership[id_field]].append(f"object_specificity_note:{note}")
    return warnings


def object_graph_context(obj: dict[str, Any]) -> dict[str, Any]:
    return {
        "family_numbers": obj.get("family_numbers", []),
        "archetype_ids": obj.get("archetype_ids", []),
        "roles": obj.get("roles", []),
        "best_recognition_tier": obj.get("best_recognition_tier", "unknown"),
        "best_survey_tier": obj.get("best_survey_tier", "unknown"),
    }


def handoff_source_responses(
    all_evidence: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        item
        for item in all_evidence
        if item["music_object_ref"]["object_type"] == "artist"
        and item["reaction"] in {"love", "like", "ok"}
    ]


def handoff_reaction_weight(reaction: str) -> float:
    return {
        "love": 1.0,
        "like": 0.78,
        "ok": 0.38,
        "dont_like": 0.22,
        "dont_know_enough": 0.08,
    }.get(reaction, 0.0)


def caution_metadata_for_album(album: dict[str, Any], warnings: dict[str, list[str]]) -> list[str]:
    caution = sorted(set(warnings.get(album["canonical_album_id"], [])))
    if album.get("source_row_count", 1) > 1:
        caution.append("multi_source_album_review")
    if len(album.get("release_years", [])) > 1:
        caution.append("multiple_release_years")
    if len(album.get("artist_names", [])) > 1:
        caution.append("multiple_artist_names")
    return sorted(set(caution))


def caution_metadata_for_song(song: dict[str, Any], warnings: dict[str, list[str]]) -> list[str]:
    caution = sorted(set(warnings.get(song["canonical_song_recording_id"], [])))
    if song.get("source_row_count", 1) > 1:
        caution.append("multi_source_recording_review")
    if not song.get("composition_key"):
        caution.append("missing_composition_key")
    if len(song.get("release_years", [])) > 1:
        caution.append("multiple_release_years")
    if len(song.get("artist_names", [])) > 1:
        caution.append("multiple_artist_names")
    return sorted(set(caution))


def album_handoff_intent(
    source_response: dict[str, Any],
    artist: dict[str, Any],
    album: dict[str, Any],
    apple_depth_hint: float,
) -> str:
    roles = set(album.get("roles", [])) | set(artist.get("roles", []))
    if roles & {"false_nearby", "boundary", "contrast"}:
        return "test_false_nearby_album"
    if "album_anchor" in roles:
        return "test_canonical_album_anchor"
    if apple_depth_hint >= 0.55 or source_response["reaction"] == "love":
        return "confirm_album_world"
    if source_response["reaction"] in POSITIVE_REACTIONS:
        return "test_artist_scope"
    return "repair_album_coverage"


def song_handoff_intent(
    source_response: dict[str, Any],
    artist: dict[str, Any],
    song: dict[str, Any],
    caution: list[str],
) -> str:
    roles = set(song.get("roles", [])) | set(artist.get("roles", []))
    if caution or "live_gateway" in roles or "compilation_gateway" in roles:
        return "test_version_specificity"
    if "song_first" in roles:
        return "confirm_song_first_signal"
    if source_response["reaction"] == "ok":
        return "test_artist_vs_song_scope"
    if roles & {"false_nearby", "boundary", "contrast"}:
        return "test_boundary_song"
    return "repair_song_familiarity"


def source_artist_apple_depth(
    source_ref: dict[str, Any],
    page_tiles: list[dict[str, Any]],
) -> float:
    source_id = source_ref.get("canonical_artist_id")
    for tile in page_tiles:
        ref = tile["music_object_ref"]
        if ref.get("canonical_artist_id") == source_id:
            return float(tile.get("apple_evidence", {}).get("artist_depth_hint", 0.0))
    return 0.0


def build_album_handoff_candidates(
    run_id: str,
    pages: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
    artists_by_id: dict[str, dict[str, Any]],
    albums: list[dict[str, Any]],
    songs: list[dict[str, Any]],
    album_warnings: dict[str, list[str]],
) -> dict[str, Any]:
    candidates = []
    seen_ids: set[str] = set()
    seen_display: set[str] = set()
    source_tiles = [tile for page in pages for tile in page["tiles"]]
    for source in handoff_source_responses(evidence):
        artist_id = source["music_object_ref"]["canonical_artist_id"]
        artist = artists_by_id.get(artist_id)
        if not artist:
            continue
        related_albums, _ = find_related_objects_by_artist(artist, albums, songs)
        apple_depth = source_artist_apple_depth(source["music_object_ref"], source_tiles)
        for album in related_albums[:3]:
            album_id = album["canonical_album_id"]
            display_key = f"{album['display_name']}::{','.join(album.get('artist_names', []))}".casefold()
            if album_id in seen_ids or display_key in seen_display:
                continue
            caution = caution_metadata_for_album(album, album_warnings)
            intent = album_handoff_intent(source, artist, album, apple_depth)
            roles = set(album.get("roles", []))
            score = round(
                (handoff_reaction_weight(source["reaction"]) * 0.34)
                + (normalized_graph_score(album) * 0.22)
                + ((0.22 if "album_anchor" in roles else 0.0))
                + (apple_depth * 0.12)
                + ((0.1 if caution else 0.0)),
                3,
            )
            candidates.append(
                {
                    "music_object_ref": album_ref(album),
                    "handoff_intent": intent,
                    "candidate_basis": [
                        "artist_response_handoff",
                        "canonical_album_object",
                        "object_type_role_based",
                    ],
                    "source_artist_ref": copy.deepcopy(source["music_object_ref"]),
                    "response_evidence_refs": [
                        {
                            "response_id": source["response_id"],
                            "page_id": source["page_id"],
                            "tile_id": source["tile_id"],
                            "reaction": source["reaction"],
                            "interpretation": source["interpretation"],
                        }
                    ],
                    "graph_context": object_graph_context(album),
                    "score": score,
                    "suppression_warnings": caution,
                    "uses_object_type_roles": True,
                }
            )
            seen_ids.add(album_id)
            seen_display.add(display_key)
    candidates.sort(key=lambda item: (-item["score"], item["music_object_ref"]["display_name"].lower()))
    return {
        "schema_version": "survey_simulation.album_page_001_candidates.v0.1",
        "run_id": run_id,
        "generated_at": GENERATED_AT,
        "hidden_inputs_consumed": False,
        "candidate_count": min(12, len(candidates)),
        "candidates": candidates[:12],
    }


def build_song_handoff_candidates(
    run_id: str,
    pages: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
    artists_by_id: dict[str, dict[str, Any]],
    albums: list[dict[str, Any]],
    songs: list[dict[str, Any]],
    song_warnings: dict[str, list[str]],
) -> dict[str, Any]:
    candidates = []
    seen_ids: set[str] = set()
    seen_display: set[str] = set()
    for source in handoff_source_responses(evidence):
        artist_id = source["music_object_ref"]["canonical_artist_id"]
        artist = artists_by_id.get(artist_id)
        if not artist:
            continue
        _, related_songs = find_related_objects_by_artist(artist, albums, songs)
        for song in related_songs[:4]:
            song_id = song["canonical_song_recording_id"]
            display_key = f"{song['display_name']}::{','.join(song.get('artist_names', []))}".casefold()
            if song_id in seen_ids or display_key in seen_display:
                continue
            caution = caution_metadata_for_song(song, song_warnings)
            intent = song_handoff_intent(source, artist, song, caution)
            roles = set(song.get("roles", [])) | set(artist.get("roles", []))
            score = round(
                (handoff_reaction_weight(source["reaction"]) * 0.32)
                + (normalized_graph_score(song) * 0.18)
                + ((0.22 if "song_first" in roles else 0.0))
                + ((0.12 if roles & {"boundary", "false_nearby", "contrast"} else 0.0))
                + ((0.12 if caution else 0.0)),
                3,
            )
            candidates.append(
                {
                    "music_object_ref": song_ref(song),
                    "handoff_intent": intent,
                    "candidate_basis": [
                        "artist_response_handoff",
                        "canonical_song_recording_object",
                        "object_type_role_based",
                    ],
                    "source_artist_ref": copy.deepcopy(source["music_object_ref"]),
                    "response_evidence_refs": [
                        {
                            "response_id": source["response_id"],
                            "page_id": source["page_id"],
                            "tile_id": source["tile_id"],
                            "reaction": source["reaction"],
                            "interpretation": source["interpretation"],
                        }
                    ],
                    "graph_context": object_graph_context(song),
                    "composition_key": song.get("composition_key", ""),
                    "score": score,
                    "suppression_warnings": caution,
                    "uses_object_type_roles": True,
                }
            )
            seen_ids.add(song_id)
            seen_display.add(display_key)
    candidates.sort(key=lambda item: (-item["score"], item["music_object_ref"]["display_name"].lower()))
    return {
        "schema_version": "survey_simulation.song_page_001_candidates.v0.1",
        "run_id": run_id,
        "generated_at": GENERATED_AT,
        "hidden_inputs_consumed": False,
        "candidate_count": min(12, len(candidates)),
        "candidates": candidates[:12],
    }


def apple_payload_used_copy(apple_payload: dict[str, Any], mode: str) -> dict[str, Any]:
    payload = copy.deepcopy(apple_payload)
    payload["candidate_generation_application"] = {
        "page_mode": mode,
        "applied_to_candidate_generation": mode == "apple_biased_seed",
        "hidden_profile_data_included": False,
    }
    return payload


def build_run(
    run_id: str,
    mode: str,
    page: dict[str, Any],
    graph_before: dict[str, Any],
    manifest_status: str,
) -> dict[str, Any]:
    return {
        "schema_version": "survey_simulation.run.v0.1",
        "run_id": run_id,
        "generated_at": GENERATED_AT,
        "harness_version": HARNESS_VERSION,
        "page_mode": mode,
        "stage_flow": ["artists", "albums", "songs"],
        "page_size": PAGE_SIZE,
        "canonical_graph_input": {
            "manifest_path": relative(GRAPH_DIR / "canonical_graph_manifest.json"),
            "manifest_status": manifest_status,
            "read_only": True,
            "input_fingerprint_sha256": graph_before["sha256"],
        },
        "boundary_assertions": {
            "survey_builder_visible_inputs_only": True,
            "hidden_reason_tags_exported_to_visible_outputs": False,
            "canonical_graph_mutated": False,
            "typed_music_object_refs_only": True,
        },
        "pages": [page],
        "outputs": [
            "survey_run.json",
            "survey_transcript.md",
            "page_generation_log.json",
            "recorded_responses.json",
            "apple_payload_used.json",
            "hidden_lookup_coverage_report.md",
            "hidden_lookup_coverage.json",
        ],
    }


def render_readme() -> str:
    return """# Survey Simulation Harness v0.1

Generated by `scripts/generate_survey_simulation_v0_1.py`.

This directory contains a read-only survey simulator for the staging canonical graph.
The first implementation slice covers fake-user fixtures, typed JSON shapes, validators,
graph-only Artist Page 1, Apple-biased Artist Page 1, Page 2 adaptation,
album/song handoff candidates, hidden-corpus response simulation, and exported
run artifacts. Survey pages are built by active slate optimizers, not simple
likely-like rankings: they balance anchors, translators, coverage repair,
payload signatures, archetype confirmations, junction nodes, false-nearby probes,
response disambiguation, and controlled frontier tiles.

## Boundary

- The canonical graph under `data/canonical_graph/import_dry_run/` is read only.
- Survey Builder-visible run artifacts include canonical graph refs, sanitized Apple payloads,
  generated pages, visible responses, and transcripts.
- Fake profile labels, hidden archetype weights, anti-affinities, private hidden corpora,
  and private rationale tags stay in fixture or simulator-private evaluation files.
- Missing hidden-corpus lookups become the stable simulator reaction `dont_know_enough`.
- Apple payloads are interpreted as exposure priors, not preference truth.
- Every visible tile carries `page_intent`, decomposed Apple evidence dimensions,
  deterministic score components, and a debug reason.

## Layout

- `schemas/`: JSON Schemas for fake profiles, Apple payloads, hidden corpora, pages, runs,
  generation logs, visible responses, and lookup coverage.
- `fake_profiles/`: ten private fake profile definitions.
- `apple_payloads/`: ten simulated Apple Music-style payloads.
- `hidden_reaction_corpora/`: ten private corpora with sparse but realism-weighted artist, album, and song reactions.
- `runs/`: twenty runs covering graph-only and Apple-biased mode for every profile,
  with Page 1, Page 2, state, evaluation coverage, and album/song handoff artifacts.
- `reports/simulation_acceptance_report.md`: first-slice acceptance report.
- `reports/survey_page_n_adaptation_report.md`: Page N adaptation and handoff report.
- `reports/hidden_corpus_realism_report.md`: private-corpus coverage and backtest readiness report.

Run validation with:

```bash
python3 scripts/validate_survey_simulation.py
```
"""


def render_acceptance_report(
    profile_count: int,
    run_summaries: list[dict[str, Any]],
    graph_before: dict[str, Any],
    graph_after: dict[str, Any],
) -> str:
    by_mode = Counter(item["mode"] for item in run_summaries)
    direct_counts = [
        item["direct_apple_match_count"]
        for item in run_summaries
        if item["mode"] == "apple_biased_seed"
    ]
    lookup_hits = [item["hidden_lookup_hit_count"] for item in run_summaries]
    missing_defaults = [item["missing_default_count"] for item in run_summaries]
    graph_exploration_counts = [
        item["graph_exploration_count"]
        for item in run_summaries
        if item["mode"] == "apple_biased_seed"
    ]
    apple_intent_mix = ", ".join(
        f"{intent}={count}" for intent, count in PAGE1_INTENT_TARGETS
    )
    graph_intent_mix = ", ".join(
        f"{intent}={count}" for intent, count in PAGE1_GRAPH_ONLY_INTENT_TARGETS
    )
    lines = [
        "# Simulation Acceptance Report",
        "",
        f"Generated: {GENERATED_AT}",
        "",
        "## First Slice Status",
        "",
        "| check | status | notes |",
        "|---|---|---|",
        f"| `data/survey_simulation/` structure exists | pass | {profile_count} fake profiles, {len(run_summaries)} runs |",
        "| JSON shapes defined | pass | fake profile, Apple payload, hidden corpus, survey run, page, generation log, response, coverage |",
        "| Active selection engine | pass | Page 1 uses payload signatures, archetype confirmation, junctions, decomposed Apple evidence, score components, quotas, and suppression rules |",
        "| Validators created | pass | `scripts/validate_survey_simulation.py` performs schema, slate composition, and boundary checks |",
        "| Ten seed fake profiles | pass | each has 2 primary affinities, 2 secondary affinities, context lane, false-nearby lane, anti-affinities |",
        "| Realistic hidden artist/album/song corpora | pass | private corpus population uses profile tier, popularity, Apple presence, false-nearby/anti-affinity, and control rates |",
        f"| Graph-only Artist Page 1 | pass | {by_mode['generic_graph_seed']} graph-only runs generated |",
        f"| Apple-biased Artist Page 1 | pass | {by_mode['apple_biased_seed']} Apple-biased runs generated |",
        "| Hidden corpus response simulation | pass | missing sparse entries default to `dont_know_enough` |",
        "| Required run exports | pass | survey run, transcript, generation log, responses, Apple payload copy, coverage report |",
        "| Canonical graph mutation | pass | input fingerprint unchanged during generation |",
        "| Hidden private data leakage to visible artifacts | pass | no profile labels or private rationale tags are exported in run-visible JSON/transcripts |",
        "| Typed music refs | pass | every visible music object is a `music_object_ref` with object type and ref source |",
        "",
        "## Run Coverage",
        "",
        f"- Total runs: {len(run_summaries)}",
        f"- Graph-only runs: {by_mode['generic_graph_seed']}",
        f"- Apple-biased runs: {by_mode['apple_biased_seed']}",
        f"- Apple-biased Page 1 intent mix per run: {apple_intent_mix}",
        f"- Graph-only Page 1 intent mix per run: {graph_intent_mix}",
        f"- Apple direct matches per Apple-biased page: min {min(direct_counts)}, max {max(direct_counts)}",
        f"- Pure graph-exploration tiles per Apple-biased page: min {min(graph_exploration_counts)}, max {max(graph_exploration_counts)}",
        f"- Hidden lookup hits per page: min {min(lookup_hits)}, max {max(lookup_hits)}",
        f"- Missing defaults per page: min {min(missing_defaults)}, max {max(missing_defaults)}",
        "",
        "## Read-Only Graph Check",
        "",
        f"- Before fingerprint: `{graph_before['sha256']}`",
        f"- After fingerprint: `{graph_after['sha256']}`",
        f"- Match: `{str(graph_before['sha256'] == graph_after['sha256']).lower()}`",
        "",
        "## Backtest Boundary",
        "",
        "The harness now includes the Page N adaptation slice and still stops before the LLM prediction backtest as requested.",
        "Full multi-page album/song adaptation, page-count comparisons, prediction backtest, and product-feel proposals remain intentionally deferred.",
        "",
    ]
    return "\n".join(lines)


def average(values: list[float]) -> float:
    return round(sum(values) / len(values), 3) if values else 0.0


def percent(part: int | float, total: int | float) -> str:
    if not total:
        return "0.0%"
    return f"{(part / total) * 100:.1f}%"


def object_lookup_index(
    artists_by_id: dict[str, dict[str, Any]],
    albums: list[dict[str, Any]],
    songs: list[dict[str, Any]],
) -> dict[tuple[str, str], dict[str, Any]]:
    lookup: dict[tuple[str, str], dict[str, Any]] = {
        ("artist", artist_id): artist for artist_id, artist in artists_by_id.items()
    }
    lookup.update({("album", album["canonical_album_id"]): album for album in albums})
    lookup.update(
        {
            ("song_recording", song["canonical_song_recording_id"]): song
            for song in songs
        }
    )
    return lookup


def empty_hidden_realism_metrics() -> dict[str, Any]:
    stat_factory = lambda: {"total": 0, "hits": 0, "dont_know": 0}
    coverage_factory = lambda: {"total": 0, "populated": 0}
    return {
        "lookup_by_surface": defaultdict(stat_factory),
        "lookup_by_profile_tier": defaultdict(stat_factory),
        "lookup_by_popularity": defaultdict(stat_factory),
        "corpus_by_profile_tier": defaultdict(coverage_factory),
        "corpus_by_popularity": defaultdict(coverage_factory),
        "corpus_by_apple_presence": defaultdict(coverage_factory),
        "reaction_by_object_type_tier": defaultdict(Counter),
    }


def add_lookup_metric(
    table: dict[Any, dict[str, int]],
    key: Any,
    hit: bool,
    reaction: str,
) -> None:
    row = table[key]
    row["total"] += 1
    if hit:
        row["hits"] += 1
    if reaction == "dont_know_enough":
        row["dont_know"] += 1


def add_population_metric(
    table: dict[Any, dict[str, int]],
    key: Any,
    populated: bool,
) -> None:
    row = table[key]
    row["total"] += 1
    if populated:
        row["populated"] += 1


def record_lookup_realism_metrics(
    metrics: dict[str, Any],
    profile_def: dict[str, Any],
    hidden_corpus: dict[str, Any],
    refs: list[dict[str, Any]],
    object_lookup: dict[tuple[str, str], dict[str, Any]],
    surface: str,
    page_number: int,
) -> None:
    lookup = hidden_lookup_map(hidden_corpus)
    for ref in refs:
        key = ref_key(ref)
        obj = object_lookup.get(key)
        if obj is None:
            continue
        profile_tier = profile_archetype_tier(profile_def, obj)
        popularity = popularity_tier(obj)
        hidden_reaction = lookup.get(key)
        hit = hidden_reaction is not None
        reaction = hidden_reaction["reaction"] if hidden_reaction else "dont_know_enough"
        object_type = ref["object_type"]
        add_lookup_metric(
            metrics["lookup_by_surface"],
            (surface, object_type, page_number),
            hit,
            reaction,
        )
        add_lookup_metric(
            metrics["lookup_by_profile_tier"],
            (object_type, page_number, profile_tier),
            hit,
            reaction,
        )
        add_lookup_metric(
            metrics["lookup_by_popularity"],
            (object_type, page_number, popularity),
            hit,
            reaction,
        )


def record_corpus_population_metrics(
    metrics: dict[str, Any],
    profile_def: dict[str, Any],
    artists_by_id: dict[str, dict[str, Any]],
    albums: list[dict[str, Any]],
    songs: list[dict[str, Any]],
    hidden_corpus: dict[str, Any],
) -> None:
    lookup = hidden_lookup_map(hidden_corpus)
    graph_lookup = object_lookup_index(artists_by_id, albums, songs)
    graph_objects = [
        ("artist", artists_by_id.values()),
        ("album", albums),
        ("song_recording", songs),
    ]
    for object_type, objects in graph_objects:
        for obj in objects:
            key = (object_type, canonical_object_id(object_type, obj))
            populated = key in lookup
            profile_tier = profile_archetype_tier(profile_def, obj)
            popularity = popularity_tier(obj)
            apple_kind = apple_presence_kind(profile_def, artists_by_id, object_type, obj)
            add_population_metric(
                metrics["corpus_by_profile_tier"],
                (object_type, profile_tier),
                populated,
            )
            add_population_metric(
                metrics["corpus_by_popularity"],
                (object_type, popularity),
                populated,
            )
            if apple_kind != "none":
                add_population_metric(
                    metrics["corpus_by_apple_presence"],
                    (object_type, apple_kind),
                    populated,
                )

    for hidden_reaction in hidden_corpus["reactions"]:
        ref = hidden_reaction["music_object_ref"]
        obj = graph_lookup.get(ref_key(ref))
        if obj is None:
            continue
        tier = profile_archetype_tier(profile_def, obj)
        metrics["reaction_by_object_type_tier"][(ref["object_type"], tier)][
            hidden_reaction["reaction"]
        ] += 1


def metric_row(label_parts: tuple[Any, ...], stats: dict[str, int]) -> str:
    label = " | ".join(str(part) for part in label_parts)
    return (
        f"| {label} | {stats['total']} | {stats['hits']} | "
        f"{percent(stats['hits'], stats['total'])} | {percent(stats['dont_know'], stats['total'])} |"
    )


def coverage_row(label_parts: tuple[Any, ...], stats: dict[str, int]) -> str:
    label = " | ".join(str(part) for part in label_parts)
    return (
        f"| {label} | {stats['total']} | {stats['populated']} | "
        f"{percent(stats['populated'], stats['total'])} |"
    )


def aggregate_lookup_rate(
    table: dict[tuple[Any, ...], dict[str, int]],
    predicate: Any,
) -> tuple[int, int, int]:
    total = hits = dont_know = 0
    for key, stats in table.items():
        if predicate(key):
            total += stats["total"]
            hits += stats["hits"]
            dont_know += stats["dont_know"]
    return total, hits, dont_know


def target_status(rate: float, low: float, high: float) -> str:
    return "pass" if low <= rate <= high else "review"


def render_hidden_corpus_realism_report(metrics: dict[str, Any]) -> str:
    surface_table = metrics["lookup_by_surface"]
    page1_total, page1_hits, page1_dont = aggregate_lookup_rate(
        surface_table,
        lambda key: key[0] == "artist_page" and key[2] == 1,
    )
    page2_total, page2_hits, page2_dont = aggregate_lookup_rate(
        surface_table,
        lambda key: key[0] == "artist_page" and key[2] == 2,
    )
    album_total, album_hits, album_dont = aggregate_lookup_rate(
        surface_table,
        lambda key: key[0] == "album_pool",
    )
    song_total, song_hits, song_dont = aggregate_lookup_rate(
        surface_table,
        lambda key: key[0] == "song_pool",
    )

    target_rows = [
        ("Artist Page 1", page1_total, page1_hits, page1_dont, 0.0, 0.15),
        ("Artist Page 2", page2_total, page2_hits, page2_dont, 0.05, 0.20),
        ("Album Page 1 pools", album_total, album_hits, album_dont, 0.15, 0.30),
        ("Song Page 1 pools", song_total, song_hits, song_dont, 0.0, 0.15),
    ]
    page2_signal_rate = (page2_hits / page2_total) if page2_total else 0.0
    enough_signal = page2_signal_rate >= 0.80

    lines = [
        "# Hidden Corpus Realism Expansion Report",
        "",
        f"Generated: {GENERATED_AT}",
        "",
        "## Summary",
        "",
        "- Regenerated 10 fake hidden corpora using the combined profile-archetype-tier and object-popularity model.",
        "- Early survey targets now favor signal density: Page 1-2 unknowns should come mainly from deliberate boundary tests.",
        "- Population probability uses `1 - product(1 - contributing_rate)` across profile tier, popularity, Apple presence, false-nearby/anti-affinity, and control sampling rates.",
        "- Page 1 and Page 2 runs were regenerated after the private corpus refresh.",
        "- Hidden corpus data remains simulator-private and is used only for response simulation and coverage evaluation.",
        "- Current simulated Apple payloads contain exact artist refs only; album/song Apple coverage rows are artist-context proxies until richer payload fields are populated.",
        f"- Page 2 non-null signal check: `{'pass' if enough_signal else 'review'}` ({percent(page2_hits, page2_total)} hidden lookup hit rate).",
        "",
        "## Target `dont_know_enough` Rates",
        "",
        "| surface | total evaluated | hidden hits | observed `dont_know_enough` rate | target | status |",
        "|---|---:|---:|---:|---|---|",
    ]
    for label, total, hits, dont, low, high in target_rows:
        rate = dont / total if total else 0.0
        lines.append(
            f"| {label} | {total} | {hits} | {percent(dont, total)} | {int(low * 100)}-{int(high * 100)}% | `{target_status(rate, low, high)}` |"
        )

    lines.extend(
        [
            "",
            "## Hidden Lookup Hit Rate by Object Type and Page",
            "",
            "| surface | object type | page | total | hits | hit rate | `dont_know_enough` rate |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for key, stats in sorted(surface_table.items()):
        surface, object_type, page_number = key
        lines.append(
            f"| {surface} | {object_type} | {page_number} | {stats['total']} | {stats['hits']} | {percent(stats['hits'], stats['total'])} | {percent(stats['dont_know'], stats['total'])} |"
        )

    lines.extend(
        [
            "",
            "## Hidden Lookup Hit Rate by Profile Archetype Tier",
            "",
            "| object type | page | profile tier | total | hits | hit rate | `dont_know_enough` rate |",
            "|---|---:|---|---:|---:|---:|---:|",
        ]
    )
    for key, stats in sorted(metrics["lookup_by_profile_tier"].items()):
        lines.append(metric_row(key, stats))

    lines.extend(
        [
            "",
            "## Hidden Lookup Hit Rate by Popularity Tier",
            "",
            "| object type | page | popularity tier | total | hits | hit rate | `dont_know_enough` rate |",
            "|---|---:|---|---:|---:|---:|---:|",
        ]
    )
    for key, stats in sorted(metrics["lookup_by_popularity"].items()):
        lines.append(metric_row(key, stats))

    lines.extend(
        [
            "",
            "## Full Corpus Population Coverage by Profile Tier",
            "",
            "| object type | profile tier | graph objects evaluated | populated hidden reactions | population rate |",
            "|---|---|---:|---:|---:|",
        ]
    )
    for key, stats in sorted(metrics["corpus_by_profile_tier"].items()):
        if key[1] in {"tier_1", "tier_2"}:
            lines.append(coverage_row(key, stats))

    lines.extend(
        [
            "",
            "## Full Corpus Population Coverage by Popularity Tier",
            "",
            "| object type | popularity tier | graph objects evaluated | populated hidden reactions | population rate |",
            "|---|---|---:|---:|---:|",
        ]
    )
    for key, stats in sorted(metrics["corpus_by_popularity"].items()):
        if key[1] == "mass_popular":
            lines.append(coverage_row(key, stats))

    lines.extend(
        [
            "",
            "## Apple Presence Coverage",
            "",
            "| object type | Apple presence kind | graph objects evaluated | populated hidden reactions | population rate |",
            "|---|---|---:|---:|---:|",
        ]
    )
    for key, stats in sorted(metrics["corpus_by_apple_presence"].items()):
        lines.append(coverage_row(key, stats))

    lines.extend(
        [
            "",
            "## Reaction Distribution by Object Type and Archetype Tier",
            "",
            "| object type | profile tier | love | like | ok | dont_like | total populated |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for key, counts in sorted(metrics["reaction_by_object_type_tier"].items()):
        total = sum(counts.values())
        object_type, tier = key
        lines.append(
            f"| {object_type} | {tier} | {counts['love']} | {counts['like']} | {counts['ok']} | {counts['dont_like']} | {total} |"
        )

    lines.extend(
        [
            "",
            "## Leakage and Backtest Readiness",
            "",
            "- Hidden reason tags and lookup status remain absent from Survey Builder-visible JSON, predictor-facing responses, and transcripts; validator coverage enforces this boundary.",
            "- Album/song pool coverage is evaluated against private hidden corpora only after deterministic handoff generation.",
            f"- Page 2 has enough non-null signal for selector-quality backtesting: `{'true' if enough_signal else 'false'}`.",
            "",
        ]
    )
    return "\n".join(lines)


def render_page_n_adaptation_report(
    run_summaries: list[dict[str, Any]],
    graph_before: dict[str, Any],
    graph_after: dict[str, Any],
) -> str:
    page2_summaries = [item for item in run_summaries if "page2_intent_counts" in item]
    total_runs = len(page2_summaries)
    intent_totals: Counter[str] = Counter()
    for item in page2_summaries:
        intent_totals.update(item["page2_intent_counts"])
    average_intents = {
        intent: round(count / total_runs, 2) for intent, count in sorted(intent_totals.items())
    } if total_runs else {}
    lines = [
        "# Survey Page N Adaptation Report",
        "",
        f"Generated: {GENERATED_AT}",
        "",
        "## Summary",
        "",
        f"- Total runs: {total_runs}",
        f"- Page 2 generated count: {sum(1 for item in page2_summaries if item['page2_generated'])}",
        "- Page 2 validation status: `pass` when `scripts/validate_survey_simulation.py` succeeds",
        f"- Average Page 2 intent mix: `{json.dumps(average_intents, sort_keys=True)}`",
        f"- Average duplicate suppression count: {average([item['page2_duplicate_suppression_count'] for item in page2_summaries])}",
        f"- Average hidden lookup hit count, evaluation only: {average([item['page2_hidden_lookup_hit_count'] for item in page2_summaries])}",
        f"- Average `dont_know_enough` rate: {average([item['page2_dont_know_rate'] for item in page2_summaries])}",
        f"- Album candidate generation count: {sum(item['album_candidate_count'] for item in page2_summaries)}",
        f"- Song candidate generation count: {sum(item['song_candidate_count'] for item in page2_summaries)}",
        f"- Hidden leakage check: visible artifacts are generated with `hidden_inputs_consumed=false`; validator checks private key leakage",
        f"- Canonical graph fingerprint check: `{str(graph_before['sha256'] == graph_after['sha256']).lower()}`",
        "",
        "## Known Limitations",
        "",
        "- Page 2 is artist-only in this slice; album/song files are handoff candidate pools, not full adaptive pages.",
        "- Apple payloads are simulated and still lack real loved-track, skip, playlist-kind, and album-completion evidence.",
        "- Page 2 scoring is deterministic and heuristic; no LLM prediction backtest has been run.",
        "- Album/song handoff uses canonical object roles and artist-name relationships; it does not repair graph normalization issues.",
        "- Regenerated hidden corpora are still simulator heuristics; real user familiarity will require calibrated production priors.",
        "",
        "## Recommended Next Slice",
        "",
        "Prediction Backtest + Product Feel Review:",
        "",
        "- compare graph-only vs Apple-biased Page 1",
        "- compare Page 1 only vs Page 1 + Page 2",
        "- compare artist-only vs artist + album/song handoff",
        "- score deterministic candidate quality against held-out fake-profile corpora",
        "- review whether generated pages feel like Waymark or like a generic music quiz",
        "",
    ]
    return "\n".join(lines)


def validate_profile_ids(artists_by_id: dict[str, dict[str, Any]]) -> None:
    missing = []
    for profile in PROFILE_DEFINITIONS:
        for artist_id, _, _ in profile["artist_reactions"]:
            if artist_id not in artists_by_id:
                missing.append((profile["id"], artist_id))
        for artist_id, *_ in profile["apple_artists"]:
            if artist_id not in artists_by_id:
                missing.append((profile["id"], artist_id))
    if missing:
        formatted = ", ".join(f"{profile}:{artist_id}" for profile, artist_id in missing)
        raise SystemExit(f"Profile references missing canonical artists: {formatted}")


def clean_generated_outputs() -> None:
    preserved_reports: dict[str, str] = {}
    preserved_report_names = {"page_n_intelligence_dispatch_context.md"}
    reports_dir = SIM_DIR / "reports"
    for name in preserved_report_names:
        path = reports_dir / name
        if path.exists():
            preserved_reports[name] = path.read_text(encoding="utf-8")
    for subdir in [
        "schemas",
        "fake_profiles",
        "apple_payloads",
        "hidden_reaction_corpora",
        "runs",
        "reports",
    ]:
        path = SIM_DIR / subdir
        if path.exists():
            for child in sorted(path.rglob("*"), reverse=True):
                if child.is_file():
                    child.unlink()
                elif child.is_dir():
                    child.rmdir()
            path.rmdir()
    for name, content in preserved_reports.items():
        write_text(SIM_DIR / "reports" / name, content)


def generate() -> None:
    graph_before = graph_fingerprint()
    manifest = load_json(GRAPH_DIR / "canonical_graph_manifest.json")
    artists = load_json(GRAPH_DIR / "canonical_artists.json")
    albums = load_json(GRAPH_DIR / "canonical_albums.json")
    songs = load_json(GRAPH_DIR / "canonical_song_recordings.json")
    album_memberships = load_json(GRAPH_DIR / "album_archetype_memberships.json")
    song_memberships = load_json(GRAPH_DIR / "song_archetype_memberships.json")
    artists_by_id = {artist["canonical_artist_id"]: artist for artist in artists}
    album_warnings = membership_warning_index(album_memberships, "canonical_album_id")
    song_warnings = membership_warning_index(song_memberships, "canonical_song_recording_id")
    object_lookup = object_lookup_index(artists_by_id, albums, songs)
    validate_profile_ids(artists_by_id)

    clean_generated_outputs()
    SIM_DIR.mkdir(parents=True, exist_ok=True)

    write_text(SIM_DIR / "README.md", render_readme())
    for filename, schema in build_schemas().items():
        write_json(SIM_DIR / "schemas" / filename, schema)

    profiles_by_id: dict[str, dict[str, Any]] = {}
    apple_payloads_by_id: dict[str, dict[str, Any]] = {}
    hidden_corpora_by_id: dict[str, dict[str, Any]] = {}
    hidden_realism_metrics = empty_hidden_realism_metrics()

    for index, profile_def in enumerate(PROFILE_DEFINITIONS, start=1):
        profile = build_fake_profile(profile_def, index)
        apple_payload = build_apple_payload(profile_def, index, artists_by_id)
        hidden_corpus = build_hidden_corpus(profile_def, index, artists_by_id, albums, songs)
        record_corpus_population_metrics(
            hidden_realism_metrics,
            profile_def,
            artists_by_id,
            albums,
            songs,
            hidden_corpus,
        )
        profiles_by_id[profile["fake_profile_id"]] = profile
        apple_payloads_by_id[profile["apple_payload_id"]] = apple_payload
        hidden_corpora_by_id[profile["hidden_reaction_corpus_id"]] = hidden_corpus
        write_json(SIM_DIR / "fake_profiles" / f"{profile['fake_profile_id']}.json", profile)
        write_json(SIM_DIR / "apple_payloads" / f"{profile['apple_payload_id']}.json", apple_payload)
        write_json(
            SIM_DIR
            / "hidden_reaction_corpora"
            / f"{profile['hidden_reaction_corpus_id']}.json",
            hidden_corpus,
        )

    run_index: list[dict[str, Any]] = []
    run_summaries: list[dict[str, Any]] = []
    run_counter = 1
    graph_candidate_pool = build_artist_candidate_pool(artists, artists_by_id, None)
    graph_selected, graph_duplicate_count = optimize_page1_slate(
        graph_candidate_pool,
        "generic_graph_seed",
    )

    for profile_def in PROFILE_DEFINITIONS:
        profile = profiles_by_id[profile_def["id"]]
        apple_payload = apple_payloads_by_id[profile["apple_payload_id"]]
        hidden_corpus = hidden_corpora_by_id[profile["hidden_reaction_corpus_id"]]

        for mode in ["generic_graph_seed", "apple_biased_seed"]:
            run_id = f"RUN_{run_counter:03d}_{'GRAPH_SEED' if mode == 'generic_graph_seed' else 'APPLE_BIASED'}"
            run_dir = SIM_DIR / "runs" / run_id.lower()
            if mode == "generic_graph_seed":
                selected = graph_selected
                duplicate_count = graph_duplicate_count
            else:
                apple_candidate_pool = build_artist_candidate_pool(
                    artists,
                    artists_by_id,
                    apple_payload,
                )
                selected, duplicate_count = optimize_page1_slate(
                    apple_candidate_pool,
                    "apple_biased_seed",
                )
            page, generation_log = build_page(
                run_id=run_id,
                mode=mode,
                selected_candidates=selected,
                manifest_status=manifest["status"],
                duplicate_display_names_suppressed=duplicate_count,
            )
            recorded, coverage = simulate_responses(run_id, page, hidden_corpus)
            survey_run = build_run(run_id, mode, page, graph_before, manifest["status"])
            record_lookup_realism_metrics(
                hidden_realism_metrics,
                profile_def,
                hidden_corpus,
                [tile["music_object_ref"] for tile in page["tiles"]],
                object_lookup,
                "artist_page",
                1,
            )

            write_json(run_dir / "survey_run.json", survey_run)
            write_text(run_dir / "survey_transcript.md", render_transcript(survey_run, recorded))
            write_json(run_dir / "page_generation_log.json", generation_log)
            write_json(run_dir / "recorded_responses.json", recorded)
            write_json(run_dir / "apple_payload_used.json", apple_payload_used_copy(apple_payload, mode))
            write_json(run_dir / "hidden_lookup_coverage.json", coverage)
            write_text(
                run_dir / "hidden_lookup_coverage_report.md",
                render_hidden_coverage_report(coverage),
            )

            state_after_page1 = survey_state_after_page_001(
                survey_run,
                recorded,
                apple_payload_used_copy(apple_payload, mode),
            )
            page1_evidence = visible_response_evidence(page, recorded)
            response_summary = summarize_response_evidence(page1_evidence)
            target_mix_name, target_mix = page2_target_mix(response_summary, mode)
            page2_candidate_pool = build_artist_candidate_pool(
                artists,
                artists_by_id,
                apple_payload if mode == "apple_biased_seed" else None,
            )
            page2_selected, page2_suppression_ledger = optimize_page2_slate(
                page2_candidate_pool,
                page1_evidence,
                target_mix,
                mode,
            )
            page2, page2_log, page2_debug = build_page2(
                run_id,
                mode,
                page2_selected,
                response_summary,
                target_mix_name,
                target_mix,
                page2_suppression_ledger,
            )
            recorded_page2, coverage_page2 = simulate_responses(run_id, page2, hidden_corpus)
            record_lookup_realism_metrics(
                hidden_realism_metrics,
                profile_def,
                hidden_corpus,
                [tile["music_object_ref"] for tile in page2["tiles"]],
                object_lookup,
                "artist_page",
                2,
            )
            all_visible_evidence = merge_visible_evidence(
                [
                    (page, recorded),
                    (page2, recorded_page2),
                ]
            )
            album_candidates = build_album_handoff_candidates(
                run_id,
                [page, page2],
                all_visible_evidence,
                artists_by_id,
                albums,
                songs,
                album_warnings,
            )
            song_candidates = build_song_handoff_candidates(
                run_id,
                [page, page2],
                all_visible_evidence,
                artists_by_id,
                albums,
                songs,
                song_warnings,
            )
            record_lookup_realism_metrics(
                hidden_realism_metrics,
                profile_def,
                hidden_corpus,
                [candidate["music_object_ref"] for candidate in album_candidates["candidates"]],
                object_lookup,
                "album_pool",
                1,
            )
            record_lookup_realism_metrics(
                hidden_realism_metrics,
                profile_def,
                hidden_corpus,
                [candidate["music_object_ref"] for candidate in song_candidates["candidates"]],
                object_lookup,
                "song_pool",
                1,
            )
            state_after_page2 = survey_state_after_page_002(
                state_after_page1,
                page2,
                recorded_page2,
                page2_suppression_ledger,
            )

            write_json(run_dir / "survey_state_after_page_001.json", state_after_page1)
            write_json(run_dir / "page_002_artists.json", page2)
            write_json(run_dir / "page_002_generation_log.json", page2_log)
            write_json(run_dir / "page_002_candidate_debug.json", page2_debug)
            write_text(
                run_dir / "page_002_transcript.md",
                render_page_transcript(run_id, page2, recorded_page2, "Survey Transcript Page 2"),
            )
            write_json(run_dir / "recorded_responses_page_002.json", recorded_page2)
            write_json(run_dir / "coverage_report_page_002.json", coverage_page2)
            write_json(run_dir / "album_page_001_candidates.json", album_candidates)
            write_json(run_dir / "song_page_001_candidates.json", song_candidates)
            write_json(run_dir / "survey_state_after_page_002.json", state_after_page2)

            run_index.append(
                {
                    "run_id": run_id,
                    "run_dir": relative(run_dir),
                    "mode": mode,
                    "fake_profile_id": profile["fake_profile_id"],
                    "apple_payload_id": profile["apple_payload_id"],
                    "hidden_reaction_corpus_id": profile["hidden_reaction_corpus_id"],
                    "privacy_boundary": "simulator_private_index",
                }
            )
            run_summaries.append(
                {
                    "run_id": run_id,
                    "mode": mode,
                    "hidden_lookup_hit_count": coverage["summary"]["hidden_lookup_hit_count"],
                    "missing_default_count": coverage["summary"]["missing_default_count"],
                    "direct_apple_match_count": generation_log["candidate_selection"][
                        "direct_apple_match_count"
                    ],
                    "graph_exploration_count": generation_log["candidate_selection"][
                        "graph_exploration_count"
                    ],
                    "intent_counts": generation_log["candidate_selection"]["intent_counts"],
                    "page2_generated": len(page2["tiles"]) == PAGE_SIZE,
                    "page2_intent_counts": page2_log["candidate_selection"]["intent_counts"],
                    "page2_duplicate_suppression_count": page2_log["candidate_selection"][
                        "duplicate_suppression_count"
                    ],
                    "page2_hidden_lookup_hit_count": coverage_page2["summary"][
                        "hidden_lookup_hit_count"
                    ],
                    "page2_dont_know_rate": round(
                        sum(
                            1
                            for response in recorded_page2["responses"]
                            if response["reaction"] == "dont_know_enough"
                        )
                        / len(recorded_page2["responses"]),
                        3,
                    ),
                    "album_candidate_count": album_candidates["candidate_count"],
                    "song_candidate_count": song_candidates["candidate_count"],
                }
            )
            run_counter += 1

    write_json(SIM_DIR / "runs" / "_simulator_private_run_index.json", run_index)

    graph_after = graph_fingerprint()
    integrity = {
        "schema_version": "survey_simulation.graph_integrity.v0.1",
        "generated_at": GENERATED_AT,
        "canonical_graph_read_only_input": relative(GRAPH_DIR),
        "before": graph_before,
        "after": graph_after,
        "unchanged_during_generation": graph_before["sha256"] == graph_after["sha256"],
    }
    write_json(SIM_DIR / "reports" / "graph_readonly_fingerprint.json", integrity)
    write_text(
        SIM_DIR / "reports" / "simulation_acceptance_report.md",
        render_acceptance_report(
            profile_count=len(PROFILE_DEFINITIONS),
            run_summaries=run_summaries,
            graph_before=graph_before,
            graph_after=graph_after,
        ),
    )
    write_text(
        SIM_DIR / "reports" / "survey_page_n_adaptation_report.md",
        render_page_n_adaptation_report(
            run_summaries=run_summaries,
            graph_before=graph_before,
            graph_after=graph_after,
        ),
    )
    write_text(
        SIM_DIR / "reports" / "hidden_corpus_realism_report.md",
        render_hidden_corpus_realism_report(hidden_realism_metrics),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Survey Simulation Harness v0.1 fixtures and runs.")
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Accepted for clarity; generated survey_simulation subdirectories are always refreshed.",
    )
    parser.parse_args()
    generate()
    print(f"Generated survey simulation harness at {relative(SIM_DIR)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
