#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = REPO_ROOT / "data/survey_simulation"
GRAPH_SURFACE_DIR = REPO_ROOT / "data/canonical_graph/normalization_pass_2"
HANDOFF_DIR = SIM_DIR / "survey_evidence_export/alpha_fast_survey_app_handoff"
DEFAULT_SOURCE_PACKET = (
    SIM_DIR
    / "llm_profile_review/api_pilot_3x3/public_packets"
    / "waymark_survey_output_packet_public_profile_01_A2_Al1_S1.json"
)
DEFAULT_OUTPUT = HANDOFF_DIR / "public_profile_01_A2_Al1_S1_alpha_survey_page_packet.json"


RESPONSE_STATES = [
    {
        "state": "love",
        "app_label": "Love",
        "normalized_operation": "positive_high",
        "atlas_signal": "strong_positive",
        "taste_polarity": "positive",
    },
    {
        "state": "like",
        "app_label": "Like",
        "normalized_operation": "positive_medium",
        "atlas_signal": "positive",
        "taste_polarity": "positive",
    },
    {
        "state": "ok",
        "app_label": "OK",
        "normalized_operation": "waypoint_context",
        "atlas_signal": "weak_positive_or_familiarity",
        "taste_polarity": "contextual",
    },
    {
        "state": "dont_like",
        "app_label": "Not for me",
        "normalized_operation": "negative_scope_carefully",
        "atlas_signal": "negative_scope_carefully",
        "taste_polarity": "negative",
    },
    {
        "state": "dont_know_enough",
        "app_label": "Don't know enough",
        "normalized_operation": "familiarity_uncertainty",
        "atlas_signal": "familiarity_uncertainty",
        "taste_polarity": "none",
    },
]

RESPONSE_STATE_BY_VALUE = {item["state"]: item for item in RESPONSE_STATES}

APPLE_EXPOSURE_FIELDS = [
    "exact_signal_weight",
    "exposure_score",
    "recency_score",
    "repetition_score",
    "library_commitment_score",
    "favorite_or_rating_score",
    "playlist_context_score",
    "album_completion_hint",
    "artist_depth_hint",
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def music_object_ref(ref: dict[str, Any]) -> dict[str, Any]:
    allowed = [
        "object_type",
        "ref_source",
        "canonical_artist_id",
        "canonical_album_id",
        "canonical_song_recording_id",
        "display_name",
        "artist_display_name",
        "resolution_state",
    ]
    return {key: ref[key] for key in allowed if key in ref}


def canonical_entity_id(ref: dict[str, Any]) -> str | None:
    if ref["object_type"] == "artist":
        return ref.get("canonical_artist_id")
    if ref["object_type"] == "album":
        return ref.get("canonical_album_id")
    if ref["object_type"] == "song_recording":
        return ref.get("canonical_song_recording_id")
    return None


def canonical_surface_file(object_type: str) -> Path:
    if object_type == "artist":
        return GRAPH_SURFACE_DIR / "survey_artist_candidates_v0_2.json"
    if object_type == "album":
        return GRAPH_SURFACE_DIR / "survey_album_candidates_v0_2.json"
    if object_type == "song_recording":
        return GRAPH_SURFACE_DIR / "survey_song_candidates_v0_2.json"
    raise ValueError(f"Unsupported object_type: {object_type}")


def load_approved_surface_index() -> dict[tuple[str, str], list[dict[str, Any]]]:
    index: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for object_type in ["artist", "album", "song_recording"]:
        data = load_json(canonical_surface_file(object_type))
        for family in data.get("families", []):
            for bucket in ["page1_core", "page2_adaptive", "page3_deep"]:
                for candidate in family.get(bucket, []):
                    if candidate.get("review_status") != "approved":
                        continue
                    key = (object_type, candidate["canonical_entity_id"])
                    index.setdefault(key, []).append(candidate)
    return index


def surface_ref_for_tile(tile: dict[str, Any], surface_index: dict[tuple[str, str], list[dict[str, Any]]]) -> dict[str, Any]:
    ref = tile["music_object_ref"]
    key = (ref["object_type"], canonical_entity_id(ref) or "")
    matches = surface_index.get(key, [])
    tile_archetypes = set(tile.get("graph_context", {}).get("archetype_ids", []))
    if tile_archetypes:
        archetype_matches = [
            candidate
            for candidate in matches
            if tile_archetypes.intersection(candidate.get("archetype_ids", []))
        ]
        if archetype_matches:
            matches = archetype_matches
    if not matches:
        return {
            "source": "canonical_graph_survey_surface_v0_2",
            "review_status": "not_found_in_approved_surface",
            "candidate_id": None,
            "survey_page_role": None,
            "survey_intent": None,
            "source_membership_id": None,
        }
    candidate = matches[0]
    return {
        "source": "canonical_graph_survey_surface_v0_2",
        "review_status": candidate["review_status"],
        "candidate_id": candidate["candidate_id"],
        "survey_page_role": candidate["survey_page_role"],
        "survey_intent": candidate["survey_intent"],
        "source_membership_id": candidate.get("source_membership_id"),
    }


def graph_refs(graph_context: dict[str, Any]) -> dict[str, Any]:
    return {
        "family_numbers": list(graph_context.get("family_numbers", [])),
        "archetype_ids": list(graph_context.get("archetype_ids", [])),
        "roles": list(graph_context.get("roles", [])),
        "best_recognition_tier": graph_context.get("best_recognition_tier", "unknown"),
        "best_survey_tier": graph_context.get("best_survey_tier", "unknown"),
    }


def apple_exposure_prior(summary: dict[str, Any]) -> dict[str, Any]:
    dimensions = {
        key: summary.get(key, 0.0)
        for key in APPLE_EXPOSURE_FIELDS
        if key in summary
    }
    signal_ids = list(summary.get("signal_ids", []))
    return {
        "source": "apple_music",
        "interpretation": "exposure_prior",
        "taste_truth": False,
        "is_present": bool(signal_ids) or any(float(value or 0.0) > 0.0 for value in dimensions.values()),
        "signal_ids": signal_ids,
        "dimensions": dimensions,
    }


def response_evidence_refs(tile: dict[str, Any], visible_ref_by_response_id: dict[str, str]) -> list[dict[str, str]]:
    refs = []
    for raw_ref in tile.get("response_evidence_refs", []):
        if not isinstance(raw_ref, dict):
            continue
        evidence_ref = visible_ref_by_response_id.get(raw_ref.get("response_id"))
        if evidence_ref:
            refs.append(
                {
                    "response_id": raw_ref["response_id"],
                    "evidence_ref": evidence_ref,
                    "relation": "visible_prior_response_used_by_selector",
                }
            )
    return refs


def build_page_packet(source_packet_path: Path) -> dict[str, Any]:
    source_packet_path = source_packet_path.resolve()
    packet = load_json(source_packet_path)
    surface_index = load_approved_surface_index()
    visible_ref_by_response_id = {
        tile["response_id"]: tile["evidence_ref"]
        for page in packet["pages"]
        for tile in page["tiles"]
    }

    pages = []
    for page in packet["pages"]:
        tiles = []
        for tile in page["tiles"]:
            reaction_state = RESPONSE_STATE_BY_VALUE[tile["reaction"]]
            tiles.append(
                {
                    "render_tile_id": f"{page['page_id']}_tile_{tile['position']:02d}",
                    "display_order": tile["position"],
                    "response_id": tile["response_id"],
                    "evidence_ref": tile["evidence_ref"],
                    "music_object_ref": music_object_ref(tile["music_object_ref"]),
                    "display": {
                        "primary_text": tile["music_object_ref"]["display_name"],
                        "secondary_text": tile["music_object_ref"].get("artist_display_name"),
                        "object_type": tile["music_object_ref"]["object_type"],
                    },
                    "page_intent": tile["page_intent"],
                    "candidate_basis": list(tile.get("candidate_basis", [])),
                    "approved_graph_surface_ref": surface_ref_for_tile(tile, surface_index),
                    "graph_refs": graph_refs(tile.get("graph_context", {})),
                    "apple_exposure_prior": apple_exposure_prior(tile.get("apple_evidence_summary", {})),
                    "response_capture": {
                        "allowed_states": [item["state"] for item in RESPONSE_STATES],
                        "selected_tags": list(tile.get("observed_selected_tags", [])),
                        "selected_tags_semantics": "visible_signal_evidence",
                        "shown_unselected_tags": list(tile.get("shown_unselected_tags", [])),
                        "shown_unselected_tags_semantics": "weak_non_selected_context",
                        "note": None,
                        "captured_state": reaction_state["state"],
                        "normalized_operation": reaction_state["normalized_operation"],
                    },
                    "evidence_export_linkage": {
                        "evidence_atom_id": f"survey_response:{tile['response_id']}",
                        "response_id": tile["response_id"],
                        "evidence_ref": tile["evidence_ref"],
                        "supporting_visible_response_refs": response_evidence_refs(tile, visible_ref_by_response_id),
                    },
                }
            )
        pages.append(
            {
                "page_id": page["page_id"],
                "stage": page["stage"],
                "page_number": page["page_number"],
                "tile_count": len(tiles),
                "rendering": {
                    "layout": "grid",
                    "columns": "app_defined",
                    "requires_ordered_tiles": True,
                },
                "tiles": tiles,
            }
        )

    page_count_config = dict(packet["page_count_config"])
    is_fast_alpha = page_count_config.get("config_id") == "A2_Al1_S1"
    is_required_alpha1_intake = page_count_config.get("config_id") == "A4_Al2_S4"

    return {
        "schema_version": "waymark.alpha_survey_page_packet.v0.1",
        "packet_id": f"alpha_survey_page_packet:{packet['profile_public_id']}:{packet['page_count_config']['config_id']}",
        "created_at": utc_now(),
        "source": {
            "profile_public_id": packet["profile_public_id"],
            "apple_payload_id": packet["apple_payload_id"],
            "survey_run_id": packet["run_id"],
            "source_packet_schema_version": packet["schema_version"],
            "source_packet_path": str(source_packet_path.relative_to(REPO_ROOT)),
            "source_public_packet_sha256": sha256_file(source_packet_path),
            "source_input_fingerprint": packet["input_fingerprint"],
        },
        "page_count_recommendation": {
            "config_id": page_count_config["config_id"],
            "artist_pages": page_count_config["artist_pages"],
            "album_pages": page_count_config["album_pages"],
            "song_pages": page_count_config["song_pages"],
            "tile_count": page_count_config["tile_count"],
            "alpha_status": (
                "recommended_fast_survey_fallback"
                if is_fast_alpha
                else "required_alpha1_intake"
                if is_required_alpha1_intake
                else "evaluated_page_count_config"
            ),
            "qualification": (
                "best fatigue-adjusted fallback; not final public onboarding length"
                if is_fast_alpha
                else "required Alpha 1 first-run intake: 4 artist pages, 2 album pages, 4 song pages, no normal early exit"
                if is_required_alpha1_intake
                else "page-count backtest configuration; not the current recommended fast Alpha default"
            ),
        },
        "response_state_contract": RESPONSE_STATES,
        "tag_and_note_contract": {
            "selected_tags": {
                "type": "array",
                "required": True,
                "empty_allowed": True,
                "signal_semantics": "visible_signal_evidence",
            },
            "shown_unselected_tags": {
                "type": "array",
                "required": True,
                "empty_allowed": True,
                "signal_semantics": "weak_non_selected_context",
            },
            "note": {
                "type": "string_or_null",
                "required": True,
                "empty_allowed": True,
            },
        },
        "private_data_boundary": {
            "private_simulator_truth_excluded": True,
            "hidden_corpus_reactions_excluded": True,
            "hidden_reason_tags_excluded": True,
            "lookup_state_excluded": True,
            "raw_candidate_scores_excluded": True,
            "generation_prompts_excluded": True,
            "profile_writer_prose_excluded": True,
        },
        "evidence_export_compatibility": {
            "target_schema_version": "waymark.survey_evidence_export.v0.1",
            "target_atlas_flow": [
                "Survey Evidence Export",
                "Signal",
                "AtlasNode",
                "provisional AtlasRoleAssignment",
                "PossibleAtlasUpdateCandidate",
                "AtlasDigestView",
            ],
            "one_atom_per_visible_response": True,
            "apple_exports_as_exposure_prior": True,
            "apple_taste_truth_required_value": False,
            "construction_only_excluded_outside_atlas_ingestion": True,
        },
        "blocking_dependencies": [
            "Atlas ingestion semantics",
            "App decision on whether Survey appears in this TestFlight build",
            "Final Canonical family/label policy",
        ],
        "pages": pages,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Alpha app-renderable Survey page packet v0.1.")
    parser.add_argument("--source-packet", type=Path, default=DEFAULT_SOURCE_PACKET)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = args.output.resolve()
    packet = build_page_packet(args.source_packet)
    write_json(output, packet)
    print(output.relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
