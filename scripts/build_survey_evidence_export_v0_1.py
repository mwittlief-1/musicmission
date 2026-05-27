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
EXPORT_DIR = SIM_DIR / "survey_evidence_export"
DEFAULT_SOURCE_PACKET = (
    SIM_DIR
    / "llm_profile_review"
    / "api_pilot_3x3"
    / "public_packets"
    / "waymark_survey_output_packet_public_profile_01_A3_Al1_S2.json"
)
DEFAULT_OUTPUT = EXPORT_DIR / "samples" / "public_profile_01_A3_Al1_S2_survey_evidence_export.json"


REACTION_OPERATIONS = {
    "love": {
        "normalized_operation": "positive_high",
        "taste_polarity": "positive",
        "atlas_signal": "strong_positive",
    },
    "like": {
        "normalized_operation": "positive_medium",
        "taste_polarity": "positive",
        "atlas_signal": "positive",
    },
    "ok": {
        "normalized_operation": "waypoint_context",
        "taste_polarity": "contextual",
        "atlas_signal": "weak_positive_or_familiarity",
    },
    "dont_like": {
        "normalized_operation": "negative_scope_carefully",
        "taste_polarity": "negative",
        "atlas_signal": "negative_scope_carefully",
    },
    "dont_know_enough": {
        "normalized_operation": "familiarity_uncertainty",
        "taste_polarity": "none",
        "atlas_signal": "familiarity_uncertainty",
    },
}

EVIDENCE_STRENGTH_HINTS = {
    "love": "strong_positive_basis",
    "like": "medium_positive_basis",
    "ok": "waypoint_or_context_basis",
    "dont_like": "negative_scope_basis",
    "dont_know_enough": "familiarity_uncertainty_basis",
}

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


def stable_export_id(packet: dict[str, Any]) -> str:
    return f"survey_evidence_export:{packet['profile_public_id']}:{packet['page_count_config']['config_id']}"


def public_music_object_ref(ref: dict[str, Any]) -> dict[str, Any]:
    allowed_keys = [
        "object_type",
        "ref_source",
        "canonical_artist_id",
        "canonical_album_id",
        "canonical_song_recording_id",
        "display_name",
        "artist_display_name",
        "resolution_state",
    ]
    return {key: ref[key] for key in allowed_keys if key in ref}


def apple_exposure_prior(summary: dict[str, Any]) -> dict[str, Any]:
    dimensions = {
        key: summary.get(key, 0.0)
        for key in APPLE_EXPOSURE_FIELDS
        if key in summary
    }
    signal_ids = list(summary.get("signal_ids", []))
    has_signal = bool(signal_ids) or any(float(value or 0.0) > 0.0 for value in dimensions.values())
    return {
        "source": "apple_music",
        "interpretation": "exposure_prior",
        "is_present": has_signal,
        "taste_truth": False,
        "signal_ids": signal_ids,
        "dimensions": dimensions,
    }


def graph_refs(graph_context: dict[str, Any]) -> dict[str, Any]:
    return {
        "family_numbers": list(graph_context.get("family_numbers", [])),
        "archetype_ids": list(graph_context.get("archetype_ids", [])),
        "roles": list(graph_context.get("roles", [])),
        "best_recognition_tier": graph_context.get("best_recognition_tier", "unknown"),
        "best_survey_tier": graph_context.get("best_survey_tier", "unknown"),
    }


def build_comparison_sets(packet: dict[str, Any]) -> dict[str, dict[str, Any]]:
    comparison_sets = {}
    for page in packet["pages"]:
        peer_refs = sorted(tile["evidence_ref"] for tile in page["tiles"])
        comparison_sets[page["page_id"]] = {
            "comparison_set_id": f"{page['page_id']}:visible_response_set",
            "stage": page["stage"],
            "page_number": page["page_number"],
            "peer_count": len(peer_refs),
            "peer_response_refs": peer_refs,
        }
    return comparison_sets


def quarantine_reason_for_response_ref(
    raw_ref: Any,
    *,
    visible_refs: set[str],
    visible_ref_by_response_id: dict[str, str],
    visible_page_ids: set[str],
) -> str:
    if isinstance(raw_ref, dict):
        page_id = raw_ref.get("page_id")
        response_id = raw_ref.get("response_id")
        if not page_id or page_id not in visible_page_ids:
            return "missing_displayed_page"
        if not response_id or response_id not in visible_ref_by_response_id:
            return "missing_tile_or_ref"
        return "schema_mismatch"

    if isinstance(raw_ref, str) and raw_ref not in visible_refs:
        return "missing_tile_or_ref"
    return "schema_mismatch"


def build_atom(
    *,
    packet: dict[str, Any],
    page: dict[str, Any],
    tile: dict[str, Any],
    comparison_set: dict[str, Any],
    visible_refs: set[str],
    visible_ref_by_response_id: dict[str, str],
    visible_page_ids: set[str],
    quarantined_response_refs: list[dict[str, Any]],
    exported_at: str,
) -> dict[str, Any]:
    reaction = tile["reaction"]
    operation = REACTION_OPERATIONS[reaction]

    supporting_refs = []
    for raw_ref in tile.get("response_evidence_refs", []):
        ref = raw_ref
        unresolved_ref = str(raw_ref)
        if isinstance(raw_ref, dict):
            ref = visible_ref_by_response_id.get(raw_ref.get("response_id"))
            unresolved_ref = f"{raw_ref.get('page_id', 'unknown_page')}:{raw_ref.get('response_id', 'unknown_response')}"
        if isinstance(ref, str) and ref in visible_refs:
            supporting_refs.append(
                {
                    "evidence_ref": ref,
                    "relation": "visible_prior_response_used_by_selector",
                }
            )
        else:
            reason = quarantine_reason_for_response_ref(
                raw_ref,
                visible_refs=visible_refs,
                visible_ref_by_response_id=visible_ref_by_response_id,
                visible_page_ids=visible_page_ids,
            )
            quarantined_response_refs.append(
                {
                    "source_response_id": tile["response_id"],
                    "source_evidence_ref": tile["evidence_ref"],
                    "unresolved_response_ref": unresolved_ref,
                    "reason": reason,
                }
            )

    return {
        "evidence_atom_id": f"survey_response:{tile['response_id']}",
        "atom_type": "survey_response",
        "atlas_ingestable": True,
        "response_id": tile["response_id"],
        "evidence_ref": tile["evidence_ref"],
        "music_object_ref": public_music_object_ref(tile["music_object_ref"]),
        "reaction": {
            "raw_value": reaction,
            "normalized_operation": operation["normalized_operation"],
            "taste_polarity": operation["taste_polarity"],
            "atlas_signal": operation["atlas_signal"],
        },
        "evidence_strength_hint": {
            "source": "survey",
            "basis": "reaction_operation_and_visible_page_context",
            "hint": EVIDENCE_STRENGTH_HINTS[reaction],
            "is_final_atlas_confidence": False,
            "note": (
                "Survey-side evidence-basis hint only. Atlas must calculate final "
                "confidence from its own model and accumulated ledger state."
            ),
        },
        "tags": {
            "selected": list(tile.get("observed_selected_tags", [])),
            "selected_semantics": "visible_signal_evidence",
            "shown_but_unselected": list(tile.get("shown_unselected_tags", [])),
            "shown_but_unselected_semantics": "weak_non_selected_context",
        },
        "note": None,
        "page_context": {
            "page_id": page["page_id"],
            "stage": page["stage"],
            "page_number": page["page_number"],
            "page_intent": tile["page_intent"],
            "candidate_basis": list(tile.get("candidate_basis", [])),
        },
        "comparison_set": comparison_set,
        "supporting_visible_response_refs": supporting_refs,
        "graph_refs": graph_refs(tile.get("graph_context", {})),
        "apple_exposure_prior": apple_exposure_prior(tile.get("apple_evidence_summary", {})),
        "provenance": {
            "source_packet_schema_version": packet["schema_version"],
            "source_run_id": packet["run_id"],
            "source_input_fingerprint": packet["input_fingerprint"],
            "source_public_packet_sha256": None,
            "response_id": tile["response_id"],
            "evidence_ref": tile["evidence_ref"],
        },
        "timestamps": {
            "survey_packet_created_at": packet["created_at"],
            "exported_at": exported_at,
        },
    }


def build_export(source_packet_path: Path) -> dict[str, Any]:
    source_packet_path = source_packet_path.resolve()
    packet = load_json(source_packet_path)
    exported_at = utc_now()
    visible_refs = {tile["evidence_ref"] for page in packet["pages"] for tile in page["tiles"]}
    visible_page_ids = {page["page_id"] for page in packet["pages"]}
    visible_ref_by_response_id = {
        tile["response_id"]: tile["evidence_ref"]
        for page in packet["pages"]
        for tile in page["tiles"]
    }
    comparison_sets = build_comparison_sets(packet)
    quarantined_response_refs: list[dict[str, Any]] = []

    atoms = []
    for page in packet["pages"]:
        comparison_set = comparison_sets[page["page_id"]]
        for tile in page["tiles"]:
            atom = build_atom(
                packet=packet,
                page=page,
                tile=tile,
                comparison_set=comparison_set,
                visible_refs=visible_refs,
                visible_ref_by_response_id=visible_ref_by_response_id,
                visible_page_ids=visible_page_ids,
                quarantined_response_refs=quarantined_response_refs,
                exported_at=exported_at,
            )
            atom["provenance"]["source_public_packet_sha256"] = sha256_file(source_packet_path)
            atoms.append(atom)

    evidence_ref_index = sorted(atom["evidence_ref"] for atom in atoms)
    response_id_index = sorted(atom["response_id"] for atom in atoms)

    return {
        "schema_version": "waymark.survey_evidence_export.v0.1",
        "export_id": stable_export_id(packet),
        "created_at": exported_at,
        "source": {
            "profile_public_id": packet["profile_public_id"],
            "apple_payload_id": packet["apple_payload_id"],
            "survey_run_id": packet["run_id"],
            "source_packet_path": str(source_packet_path.relative_to(REPO_ROOT)),
            "source_packet_schema_version": packet["schema_version"],
            "source_input_fingerprint": packet["input_fingerprint"],
            "source_public_packet_sha256": sha256_file(source_packet_path),
            "page_count_config": packet["page_count_config"],
        },
        "ledger_semantics": {
            "mode": "append_only",
            "mutation_policy": "do_not_rewrite_existing_evidence_atoms",
            "correction_policy": "append_superseding_evidence_or_correction_atom",
        },
        "private_data_boundary": {
            "private_simulator_data_excluded": True,
            "profile_writer_prose_excluded": True,
            "raw_page_construction_payloads_excluded": True,
            "raw_ranking_scores_excluded": True,
            "graph_meanings_unavailable_to_visible_packet_excluded": True,
        },
        "reaction_operation_legend": REACTION_OPERATIONS,
        "atlas_ingestable": {
            "evidence_atoms": atoms,
            "response_ref_index": {
                "evidence_refs": evidence_ref_index,
                "response_ids": response_id_index,
            },
        },
        "construction_only_excluded": {
            "atlas_ingestable": False,
            "excluded_field_categories": [
                "tile_id",
                "tile_position",
                "page_mode",
                "adaptive_context",
                "generator_visible_inputs",
                "raw_candidate_scores",
                "suppression_warnings",
                "generation_prompts",
                "adaptive_target_mixes",
                "randomization_seeds",
                "simulator_private_truth",
                "simulator_lookup_state",
                "profile_writer_prose",
            ],
            "excluded_field_counts": {
                "tile_ids": len(atoms),
                "tile_positions": len(atoms),
                "raw_candidate_score_blocks": len(atoms),
                "suppression_warning_blocks": len(atoms),
            },
            "quarantined_response_refs": quarantined_response_refs,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Survey Evidence Export v0.1 sample from a public packet.")
    parser.add_argument("--source-packet", type=Path, default=DEFAULT_SOURCE_PACKET)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    output_path = args.output.resolve()
    export = build_export(args.source_packet)
    write_json(output_path, export)
    print(output_path.relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
