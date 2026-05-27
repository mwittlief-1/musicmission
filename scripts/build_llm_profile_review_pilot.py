#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = REPO_ROOT / "data/survey_simulation"
BACKTEST_DIR = SIM_DIR / "page_count_backtest"
OUT_DIR = SIM_DIR / "llm_profile_review"
GENERATED_AT = "2026-05-20T12:00:00Z"

REFERENCE_PROFILE_PUBLIC_ID = "public_profile_01"
REFERENCE_CONFIG = {"artist_pages": 2, "album_pages": 1, "song_pages": 1}
REFERENCE_CONFIG_ID = "A2_Al1_S1"
REFERENCE_RUN_ID = "llm_profile_review_public_profile_01_A2_Al1_S1"
REFERENCE_PUBLIC_PACKET_FILENAME = "cartenza_survey_output_packet_public_profile_01_A2_Al1_S1.json"

REACTIONS = ["love", "like", "ok", "dont_like", "dont_know_enough"]
REACTION_SCORE = {"love": 4, "like": 3, "ok": 2, "dont_like": 1, "dont_know_enough": None}
STAGE_NORMALIZATION = {"artists": "artist", "albums": "album", "songs": "song"}
EMPTY_APPLE_EVIDENCE = {
    "exact_signal_weight": 0.0,
    "exposure_score": 0.0,
    "recency_score": 0.0,
    "repetition_score": 0.0,
    "library_commitment_score": 0.0,
    "favorite_or_rating_score": 0.0,
    "playlist_context_score": 0.0,
    "album_completion_hint": 0.0,
    "artist_depth_hint": 0.0,
    "probable_affinity_score": 0.0,
    "signal_ids": [],
}


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


def canonical_ref_key(ref: dict[str, Any]) -> tuple[str, str]:
    object_type = ref["object_type"]
    if object_type == "artist":
        return object_type, ref["canonical_artist_id"]
    if object_type == "album":
        return object_type, ref["canonical_album_id"]
    if object_type == "song_recording":
        return object_type, ref["canonical_song_recording_id"]
    raise ValueError(f"Unsupported object_type: {object_type}")


def canonical_id(ref: dict[str, Any]) -> str:
    return canonical_ref_key(ref)[1]


def stable_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def fingerprint(payload: Any) -> str:
    return hashlib.sha256(stable_json(payload).encode("utf-8")).hexdigest()


def selected_pages(path: dict[str, Any]) -> list[tuple[str, dict[str, Any], dict[str, Any]]]:
    selected: list[tuple[str, dict[str, Any], dict[str, Any]]] = []
    for stage, count in [
        ("artist", REFERENCE_CONFIG["artist_pages"]),
        ("album", REFERENCE_CONFIG["album_pages"]),
        ("song", REFERENCE_CONFIG["song_pages"]),
    ]:
        pages = path["pages_by_stage"][stage][:count]
        recordings = path["recorded_responses_by_stage"][stage][:count]
        for page, recorded in zip(pages, recordings):
            selected.append((stage, page, recorded))
    return selected


def evidence_ref(stage: str, page: dict[str, Any], tile: dict[str, Any], response: dict[str, Any]) -> str:
    display = tile["music_object_ref"]["display_name"].replace(":", " -")
    return f"{page['page_id']}:{stage}:{tile['position']:02d}:{display}:{response['reaction']}"


def normalized_apple_evidence(tile: dict[str, Any]) -> dict[str, Any]:
    source = dict(EMPTY_APPLE_EVIDENCE)
    apple_evidence = tile.get("apple_evidence") or {}
    for key in source:
        if key in apple_evidence:
            source[key] = apple_evidence[key]
    return source


def tile_packet(stage: str, page: dict[str, Any], tile: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
    page_stage = STAGE_NORMALIZATION.get(page["stage"], stage)
    graph_context = tile.get("graph_context") or {
        "family_numbers": [],
        "archetype_ids": [],
        "roles": [],
        "best_recognition_tier": "unknown",
        "best_survey_tier": "unknown",
    }
    return {
        "evidence_ref": evidence_ref(page_stage, page, tile, response),
        "position": tile["position"],
        "tile_id": tile["tile_id"],
        "response_id": response["response_id"],
        "music_object_ref": tile["music_object_ref"],
        "reaction": response["reaction"],
        "atlas_signal_interpretation": response["atlas_signal_interpretation"],
        "app_ui_candidate": response["app_ui_candidate"],
        "page_intent": tile["page_intent"],
        "candidate_basis": tile.get("candidate_basis", []),
        "graph_context": graph_context,
        "apple_evidence_summary": normalized_apple_evidence(tile),
        "scores": tile.get("scores", {}),
        "response_evidence_refs": tile.get("response_evidence_refs", []),
        "shown_unselected_tags": response.get("shown_unselected_tags", []),
        "observed_selected_tags": response.get("observed_selected_tags", []),
        "suppression_warnings": tile.get("suppression_warnings", []),
    }


def build_pages(path: dict[str, Any]) -> list[dict[str, Any]]:
    pages = []
    for stage, page, recorded in selected_pages(path):
        responses_by_tile = {item["tile_id"]: item for item in recorded["responses"]}
        tiles = [tile_packet(stage, page, tile, responses_by_tile[tile["tile_id"]]) for tile in page["tiles"]]
        pages.append(
            {
                "page_id": page["page_id"],
                "stage": STAGE_NORMALIZATION.get(page["stage"], stage),
                "page_number": page["page_number"],
                "page_mode": page["page_mode"],
                "tile_count": page["tile_count"],
                "generator_visible_inputs": page.get("generator_visible_inputs", {}),
                "adaptive_context": page.get("adaptive_context"),
                "tiles": tiles,
            }
        )
    return pages


def response_counts_by_stage(pages: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    counts = {stage: {reaction: 0 for reaction in REACTIONS} for stage in ["artist", "album", "song"]}
    for page in pages:
        stage_counts = counts[page["stage"]]
        for tile in page["tiles"]:
            stage_counts[tile["reaction"]] += 1
    return counts


def cluster_summary(pages: list[dict[str, Any]]) -> dict[str, Any]:
    buckets = {
        "positive_clusters": [],
        "negative_clusters": [],
        "ok_waypoint_clusters": [],
        "unknown_clusters": [],
    }
    grouped: dict[str, Counter[str]] = {key: Counter() for key in buckets}
    evidence_refs: dict[tuple[str, str], list[str]] = defaultdict(list)
    for page in pages:
        for tile in page["tiles"]:
            reaction = tile["reaction"]
            if reaction in {"love", "like"}:
                bucket = "positive_clusters"
            elif reaction == "dont_like":
                bucket = "negative_clusters"
            elif reaction == "ok":
                bucket = "ok_waypoint_clusters"
            else:
                bucket = "unknown_clusters"
            labels = [f"archetype:{item}" for item in tile["graph_context"]["archetype_ids"]]
            labels.extend(f"family:{item}" for item in tile["graph_context"]["family_numbers"])
            if not labels:
                labels = ["unclustered"]
            for label in labels:
                grouped[bucket][label] += 1
                evidence_refs[(bucket, label)].append(tile["evidence_ref"])

    for bucket, counter in grouped.items():
        for label, count in counter.most_common(8):
            buckets[bucket].append(
                {
                    "label": label,
                    "visible_response_count": count,
                    "evidence_refs": evidence_refs[(bucket, label)][:8],
                }
            )
    return buckets


def apple_payload_summary(apple_payload: dict[str, Any], pages: list[dict[str, Any]]) -> dict[str, Any]:
    payload_signature_refs = []
    for page in pages:
        for tile in page["tiles"]:
            if tile["page_intent"] == "payload_signature_artist":
                payload_signature_refs.append(
                    {
                        "display_name": tile["music_object_ref"]["display_name"],
                        "music_object_ref": tile["music_object_ref"],
                        "payload_overrepresentation_score": tile["scores"].get("payload_overrepresentation_score", 0.0),
                        "apple_evidence_strength": tile["scores"].get("apple_evidence_strength", 0.0),
                        "evidence_ref": tile["evidence_ref"],
                    }
                )
    top_signals = []
    for signal in apple_payload.get("signals", [])[:12]:
        top_signals.append(
            {
                "signal_id": signal["signal_id"],
                "signal_type": signal["signal_type"],
                "music_object_ref": signal["music_object_ref"],
                "normalized_weight": signal.get("normalized_weight", 0.0),
                "recency_days": signal.get("recency_days"),
                "play_count_90d": signal.get("play_count_90d"),
                "library_added_at": signal.get("library_added_at"),
            }
        )
    return {
        "apple_payload_id": apple_payload["apple_payload_id"],
        "signal_count": len(apple_payload.get("signals", [])),
        "top_visible_signals": top_signals,
        "apple_overrepresented_artists": payload_signature_refs,
        "optional_future_fields": {
            "playlist_context": apple_payload.get(
                "playlist_context",
                {"playlist_name": None, "playlist_kind": "unknown"},
            ),
            "track_level_signals": apple_payload.get("track_level_signals", []),
            "album_level_signals": apple_payload.get("album_level_signals", []),
            "skip_or_completion_hints": apple_payload.get("skip_or_completion_hints", []),
            "loved_or_favorite_hints": apple_payload.get("loved_or_favorite_hints", []),
        },
    }


def visible_summary(pages: list[dict[str, Any]]) -> dict[str, Any]:
    summary = cluster_summary(pages)
    summary["multi_archetype_junctions_seen"] = [
        {
            "display_name": tile["music_object_ref"]["display_name"],
            "reaction": tile["reaction"],
            "evidence_ref": tile["evidence_ref"],
            "archetype_ids": tile["graph_context"]["archetype_ids"],
        }
        for page in pages
        for tile in page["tiles"]
        if tile["page_intent"] == "multi_archetype_junction"
    ]
    summary["false_nearby_tests_seen"] = [
        {
            "display_name": tile["music_object_ref"]["display_name"],
            "reaction": tile["reaction"],
            "evidence_ref": tile["evidence_ref"],
            "page_intent": tile["page_intent"],
        }
        for page in pages
        for tile in page["tiles"]
        if "false" in tile["page_intent"] or "boundary" in tile["page_intent"]
    ]
    return summary


def build_public_packet(path: dict[str, Any], apple_payload: dict[str, Any]) -> dict[str, Any]:
    pages = build_pages(path)
    packet = {
        "schema_version": "waymark.profile_writer_input.v0.1",
        "purpose": "Blind Profile Writer input",
        "profile_public_id": REFERENCE_PROFILE_PUBLIC_ID,
        "apple_payload_id": apple_payload["apple_payload_id"],
        "run_id": REFERENCE_RUN_ID,
        "created_at": GENERATED_AT,
        "input_fingerprint": "",
        "page_count_config": {
            **REFERENCE_CONFIG,
            "config_id": REFERENCE_CONFIG_ID,
            "tile_count": sum(REFERENCE_CONFIG.values()) * 12,
        },
        "blindness_contract": {
            "hidden_inputs_used_for_generation": False,
            "public_packet_contains_hidden_truth": False,
            "forbidden_context_absent": [
                "hidden_profile_label",
                "hidden_archetype_tiers",
                "unshown_hidden_reactions",
                "hidden_reason_tags",
                "hidden_lookup_status",
            ],
        },
        "allowed_context": {
            "canonical_graph_metadata_included": [
                "family_numbers",
                "archetype_ids",
                "roles",
                "best_recognition_tier",
                "best_survey_tier",
            ],
            "page_metadata_included": [
                "page_intent",
                "candidate_basis",
                "scores",
                "generator_visible_inputs",
            ],
            "survey_responses_included": [
                "reaction",
                "atlas_signal_interpretation",
                "app_ui_candidate",
                "observed_selected_tags",
                "shown_unselected_tags",
            ],
        },
        "reaction_scale": {
            reaction: {
                "numeric_score_for_backtests": REACTION_SCORE[reaction],
                "profile_writer_guidance": {
                    "love": "strong positive, but scope remains unknown unless reinforced",
                    "like": "qualified positive or partial positive",
                    "ok": "waypoint, context, or familiarity signal rather than landmark evidence",
                    "dont_like": "negative signal with careful scope control",
                    "dont_know_enough": "familiarity failure, not taste failure",
                }[reaction],
            }
            for reaction in REACTIONS
        },
        "observed_response_counts_by_stage": response_counts_by_stage(pages),
        "apple_payload_summary": apple_payload_summary(apple_payload, pages),
        "deterministic_visible_evidence_summary": visible_summary(pages),
        "canonical_graph_dictionary": {
            "dictionary_available": False,
            "families": [],
            "archetypes": [],
            "instruction": "Do not invent human-readable meanings for family numbers or archetype IDs.",
        },
        "pages": pages,
    }
    packet["input_fingerprint"] = fingerprint({**packet, "input_fingerprint": ""})
    return packet


def hidden_truth_packet(public_packet: dict[str, Any], hidden_corpus: dict[str, Any], fake_profile: dict[str, Any]) -> dict[str, Any]:
    observed_keys = {
        canonical_ref_key(tile["music_object_ref"])
        for page in public_packet["pages"]
        for tile in page["tiles"]
    }
    heldout = []
    for item in hidden_corpus["reactions"]:
        ref = item["music_object_ref"]
        key = canonical_ref_key(ref)
        if key in observed_keys:
            continue
        heldout.append(
            {
                "music_object_ref": ref,
                "reaction": item["reaction"],
                "familiarity_band": item.get("familiarity_band"),
                "confidence": item.get("confidence"),
            }
        )
    by_type: dict[str, Counter[str]] = defaultdict(Counter)
    by_archetype: dict[str, Counter[str]] = defaultdict(Counter)
    for item in heldout:
        ref = item["music_object_ref"]
        by_type[ref["object_type"]][item["reaction"]] += 1
    for item in fake_profile.get("primary_archetype_affinities", []):
        by_archetype[item["archetype_id"]]["primary_affinity_weight_x100"] = int(round(item["weight"] * 100))
    for item in fake_profile.get("secondary_archetype_affinities", []):
        by_archetype[item["archetype_id"]]["secondary_affinity_weight_x100"] = int(round(item["weight"] * 100))
    return {
        "schema_version": "waymark.simulator_private_hidden_truth_packet.v0.1",
        "profile_public_id": public_packet["profile_public_id"],
        "page_count_config_id": public_packet["page_count_config"]["config_id"],
        "simulation_only": True,
        "not_allowed_for_profile_writer": True,
        "hidden_profile_truth": {
            "display_label": fake_profile.get("display_label"),
            "summary": fake_profile.get("summary"),
            "context_lane": fake_profile.get("context_lane"),
            "false_nearby_lane": fake_profile.get("false_nearby_lane"),
            "primary_archetype_affinities": fake_profile.get("primary_archetype_affinities", []),
            "secondary_archetype_affinities": fake_profile.get("secondary_archetype_affinities", []),
            "hidden_anti_affinities": fake_profile.get("hidden_anti_affinities", []),
        },
        "observed_survey_key_count": len(observed_keys),
        "heldout_populated_reaction_count": len(heldout),
        "heldout_reaction_distribution_by_object_type": {
            object_type: {reaction: counter.get(reaction, 0) for reaction in REACTIONS}
            for object_type, counter in sorted(by_type.items())
        },
        "hidden_profile_archetype_weight_summary": {
            archetype_id: dict(counter)
            for archetype_id, counter in sorted(by_archetype.items())
        },
        "heldout_reaction_examples": heldout[:80],
        "private_field_redactions": [
            "reason_tags removed",
            "hidden lookup status removed",
            "private corpus identifier removed",
        ],
    }


def string_schema() -> dict[str, Any]:
    return {"type": "string"}


def number_schema() -> dict[str, Any]:
    return {"type": "number"}


def string_const_schema(value: str) -> dict[str, Any]:
    return {"type": "string", "enum": [value]}


def boolean_const_schema(value: bool) -> dict[str, Any]:
    return {"type": "boolean", "enum": [value]}


def reaction_count_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": REACTIONS,
        "properties": {reaction: {"type": "integer"} for reaction in REACTIONS},
    }


def ref_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": True,
        "required": ["object_type", "ref_source", "display_name", "resolution_state"],
        "properties": {
            "object_type": {"enum": ["artist", "album", "song_recording", "region", "archetype"]},
            "ref_source": {"type": "string"},
            "canonical_artist_id": {"type": "string"},
            "canonical_album_id": {"type": "string"},
            "canonical_song_recording_id": {"type": "string"},
            "display_name": {"type": "string"},
            "artist_display_name": {"type": "string"},
            "resolution_state": {"type": "string"},
        },
    }


def writer_input_schema() -> dict[str, Any]:
    graph_context = {
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
            "family_numbers": {"type": "array", "items": {"type": "integer"}},
            "archetype_ids": {"type": "array", "items": {"type": "string"}},
            "roles": {"type": "array", "items": {"type": "string"}},
            "best_recognition_tier": {"type": "string"},
            "best_survey_tier": {"type": "string"},
        },
    }
    apple_evidence = {
        "type": "object",
        "additionalProperties": False,
        "required": list(EMPTY_APPLE_EVIDENCE.keys()),
        "properties": {
            **{key: {"type": "number"} for key in EMPTY_APPLE_EVIDENCE if key != "signal_ids"},
            "signal_ids": {"type": "array", "items": {"type": "string"}},
        },
    }
    tile = {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "evidence_ref",
            "position",
            "tile_id",
            "response_id",
            "music_object_ref",
            "reaction",
            "atlas_signal_interpretation",
            "app_ui_candidate",
            "page_intent",
            "candidate_basis",
            "graph_context",
            "apple_evidence_summary",
            "scores",
            "response_evidence_refs",
            "shown_unselected_tags",
            "observed_selected_tags",
            "suppression_warnings",
        ],
        "properties": {
            "evidence_ref": string_schema(),
            "position": {"type": "integer"},
            "tile_id": string_schema(),
            "response_id": string_schema(),
            "music_object_ref": ref_schema(),
            "reaction": {"enum": REACTIONS},
            "atlas_signal_interpretation": string_schema(),
            "app_ui_candidate": string_schema(),
            "page_intent": string_schema(),
            "candidate_basis": {"type": "array", "items": {"type": "string"}},
            "graph_context": graph_context,
            "apple_evidence_summary": apple_evidence,
            "scores": {"type": "object", "additionalProperties": {"type": "number"}},
            "response_evidence_refs": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
            "shown_unselected_tags": {"type": "array", "items": {"type": "string"}},
            "observed_selected_tags": {"type": "array", "items": {"type": "string"}},
            "suppression_warnings": {"type": "array", "items": {"type": "string"}},
        },
    }
    page = {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "page_id",
            "stage",
            "page_number",
            "page_mode",
            "tile_count",
            "generator_visible_inputs",
            "adaptive_context",
            "tiles",
        ],
        "properties": {
            "page_id": string_schema(),
            "stage": {"enum": ["artist", "album", "song"]},
            "page_number": {"type": "integer"},
            "page_mode": string_schema(),
            "tile_count": {"type": "integer"},
            "generator_visible_inputs": {"type": "object", "additionalProperties": True},
            "adaptive_context": {"type": ["object", "null"], "additionalProperties": True},
            "tiles": {"type": "array", "minItems": 12, "maxItems": 12, "items": tile},
        },
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "waymark.profile_writer_input.v0.1",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema_version",
            "purpose",
            "profile_public_id",
            "apple_payload_id",
            "run_id",
            "created_at",
            "input_fingerprint",
            "page_count_config",
            "blindness_contract",
            "allowed_context",
            "reaction_scale",
            "observed_response_counts_by_stage",
            "apple_payload_summary",
            "deterministic_visible_evidence_summary",
            "canonical_graph_dictionary",
            "pages",
        ],
        "properties": {
            "schema_version": string_const_schema("waymark.profile_writer_input.v0.1"),
            "purpose": string_schema(),
            "profile_public_id": string_schema(),
            "apple_payload_id": string_schema(),
            "run_id": string_schema(),
            "created_at": string_schema(),
            "input_fingerprint": string_schema(),
            "page_count_config": {"type": "object", "additionalProperties": True},
            "blindness_contract": {"type": "object", "additionalProperties": True},
            "allowed_context": {"type": "object", "additionalProperties": True},
            "reaction_scale": {"type": "object", "additionalProperties": True},
            "observed_response_counts_by_stage": {"type": "object", "additionalProperties": True},
            "apple_payload_summary": {"type": "object", "additionalProperties": True},
            "deterministic_visible_evidence_summary": {"type": "object", "additionalProperties": True},
            "canonical_graph_dictionary": {"type": "object", "additionalProperties": True},
            "pages": {"type": "array", "minItems": 4, "maxItems": 4, "items": page},
        },
    }


def graph_context_output_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["family_numbers", "archetype_ids", "roles", "best_recognition_tier", "best_survey_tier"],
        "properties": {
            "family_numbers": {"type": "array", "items": {"type": "integer"}},
            "archetype_ids": {"type": "array", "items": {"type": "string"}},
            "roles": {"type": "array", "items": {"type": "string"}},
            "best_recognition_tier": {"type": "string"},
            "best_survey_tier": {"type": "string"},
        },
    }


def profile_writer_output_schema() -> dict[str, Any]:
    evidence_ref_array = {"type": "array", "items": {"type": "string"}}
    object_ref = {
        "type": "object",
        "additionalProperties": False,
        "required": ["object_type", "display_name", "canonical_id"],
        "properties": {
            "object_type": {"enum": ["artist", "album", "song_recording", "region", "archetype"]},
            "display_name": string_schema(),
            "canonical_id": string_schema(),
        },
    }
    landmark = {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "label",
            "scope",
            "object_refs",
            "confidence",
            "evidence_strength",
            "why_it_may_be_a_landmark",
            "scope_limit",
            "supporting_evidence_refs",
            "counterevidence_refs",
        ],
        "properties": {
            "label": string_schema(),
            "scope": {"enum": ["song", "album", "artist", "region", "archetype", "use_case"]},
            "object_refs": {"type": "array", "items": object_ref},
            "confidence": {"enum": ["low", "medium", "high"]},
            "evidence_strength": number_schema(),
            "why_it_may_be_a_landmark": string_schema(),
            "scope_limit": string_schema(),
            "supporting_evidence_refs": evidence_ref_array,
            "counterevidence_refs": evidence_ref_array,
        },
    }
    region = {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "label",
            "confidence",
            "region_type",
            "description",
            "supporting_objects",
            "supporting_evidence_refs",
            "counterevidence_refs",
            "overclaim_risk",
            "next_test_needed",
        ],
        "properties": {
            "label": string_schema(),
            "confidence": {"enum": ["low", "medium", "high"]},
            "region_type": {"enum": ["confirmed", "tentative", "inferred"]},
            "description": string_schema(),
            "supporting_objects": {"type": "array", "items": {"type": "string"}},
            "supporting_evidence_refs": evidence_ref_array,
            "counterevidence_refs": evidence_ref_array,
            "overclaim_risk": {"enum": ["low", "medium", "high"]},
            "next_test_needed": string_schema(),
        },
    }
    frontier = {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "label",
            "why_promising",
            "confidence",
            "best_next_probe_type",
            "supporting_evidence_refs",
            "risk_note",
        ],
        "properties": {
            "label": string_schema(),
            "why_promising": string_schema(),
            "confidence": {"enum": ["low", "medium", "high"]},
            "best_next_probe_type": {
                "enum": ["song_probe", "album_probe", "artist_probe", "route_probe", "survey_followup"]
            },
            "supporting_evidence_refs": evidence_ref_array,
            "risk_note": string_schema(),
        },
    }
    dead_end = {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "label",
            "status",
            "scope",
            "why_it_looks_nearby",
            "why_it_may_fail",
            "supporting_negative_evidence_refs",
            "positive_or_mixed_evidence_refs",
            "do_not_overgeneralize_beyond",
        ],
        "properties": {
            "label": string_schema(),
            "status": {"enum": ["weak_hypothesis", "moderate_hypothesis", "strong_hypothesis"]},
            "scope": {"enum": ["song", "album", "artist", "region", "archetype", "use_case"]},
            "why_it_looks_nearby": string_schema(),
            "why_it_may_fail": string_schema(),
            "supporting_negative_evidence_refs": evidence_ref_array,
            "positive_or_mixed_evidence_refs": evidence_ref_array,
            "do_not_overgeneralize_beyond": string_schema(),
        },
    }
    waypoint = {
        "type": "object",
        "additionalProperties": False,
        "required": ["label", "scope", "why_keep_it", "use_case", "confidence", "supporting_evidence_refs"],
        "properties": {
            "label": string_schema(),
            "scope": {"enum": ["song", "album", "artist", "use_case"]},
            "why_keep_it": string_schema(),
            "use_case": {"enum": ["playlist", "context", "cultural_furniture", "bridge", "family_safe", "background", "unknown"]},
            "confidence": {"enum": ["low", "medium", "high"]},
            "supporting_evidence_refs": evidence_ref_array,
        },
    }
    ledger_item = {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "evidence_ref",
            "page_id",
            "stage",
            "page_number",
            "position",
            "page_intent",
            "object_type",
            "display_name",
            "artist_display_name",
            "canonical_id",
            "reaction",
            "atlas_signal_interpretation",
            "graph_context",
            "interpretation",
            "inference_scope",
            "confidence",
        ],
        "properties": {
            "evidence_ref": string_schema(),
            "page_id": string_schema(),
            "stage": {"enum": ["artist", "album", "song"]},
            "page_number": {"type": "integer"},
            "position": {"type": "integer"},
            "page_intent": string_schema(),
            "object_type": {"enum": ["artist", "album", "song_recording"]},
            "display_name": string_schema(),
            "artist_display_name": string_schema(),
            "canonical_id": string_schema(),
            "reaction": {"enum": REACTIONS},
            "atlas_signal_interpretation": string_schema(),
            "graph_context": graph_context_output_schema(),
            "interpretation": string_schema(),
            "inference_scope": {"enum": ["song", "album", "artist", "region", "archetype", "use_case"]},
            "confidence": {"enum": ["low", "medium", "high"]},
        },
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "waymark.profile_writer_output.v0.1",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema_version",
            "profile_public_id",
            "input_packet",
            "assessment_status",
            "evidence_audit",
            "profile_summary",
            "atlas_seed",
            "evidence_ledger",
            "contradictions_and_tensions",
            "recommended_next_tests",
            "user_facing_copy",
        ],
        "properties": {
            "schema_version": string_const_schema("waymark.profile_writer_output.v0.1"),
            "profile_public_id": string_schema(),
            "input_packet": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "schema_version",
                    "apple_payload_id",
                    "page_count_config_id",
                    "input_fingerprint",
                    "hidden_inputs_declared_absent",
                ],
                "properties": {
                    "schema_version": string_schema(),
                    "apple_payload_id": string_schema(),
                    "page_count_config_id": string_schema(),
                    "input_fingerprint": string_schema(),
                    "hidden_inputs_declared_absent": boolean_const_schema(True),
                },
            },
            "assessment_status": {
                "type": "object",
                "additionalProperties": False,
                "required": ["status", "reason", "confidence"],
                "properties": {
                    "status": {"enum": ["complete", "partial", "cannot_assess"]},
                    "reason": string_schema(),
                    "confidence": {"enum": ["low", "medium", "high"]},
                },
            },
            "evidence_audit": {
                "type": "object",
                "additionalProperties": False,
                "required": ["total_visible_items", "counts_by_stage", "visible_strengths", "visible_limits", "forbidden_context_check"],
                "properties": {
                    "total_visible_items": {"type": "integer"},
                    "counts_by_stage": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["artist", "album", "song"],
                        "properties": {
                            "artist": reaction_count_schema(),
                            "album": reaction_count_schema(),
                            "song": reaction_count_schema(),
                        },
                    },
                    "visible_strengths": {"type": "array", "items": {"type": "string"}},
                    "visible_limits": {"type": "array", "items": {"type": "string"}},
                    "forbidden_context_check": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["used_hidden_truth", "used_hidden_archetype_tiers", "used_unshown_reactions", "notes"],
                        "properties": {
                            "used_hidden_truth": boolean_const_schema(False),
                            "used_hidden_archetype_tiers": boolean_const_schema(False),
                            "used_unshown_reactions": boolean_const_schema(False),
                            "notes": string_schema(),
                        },
                    },
                },
            },
            "profile_summary": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "headline",
                    "short_read",
                    "waymark_voice_summary",
                    "most_likely_center_of_gravity",
                    "biggest_uncertainties",
                    "what_not_to_overinfer",
                ],
                "properties": {
                    "headline": string_schema(),
                    "short_read": string_schema(),
                    "waymark_voice_summary": string_schema(),
                    "most_likely_center_of_gravity": {"type": "array", "items": {"type": "string"}},
                    "biggest_uncertainties": {"type": "array", "items": {"type": "string"}},
                    "what_not_to_overinfer": {"type": "array", "items": {"type": "string"}},
                },
            },
            "atlas_seed": {
                "type": "object",
                "additionalProperties": False,
                "required": ["landmarks", "regions", "frontiers", "dead_end_hypotheses", "waypoints"],
                "properties": {
                    "landmarks": {"type": "array", "items": landmark},
                    "regions": {"type": "array", "items": region},
                    "frontiers": {"type": "array", "items": frontier},
                    "dead_end_hypotheses": {"type": "array", "items": dead_end},
                    "waypoints": {"type": "array", "items": waypoint},
                },
            },
            "evidence_ledger": {"type": "array", "items": ledger_item},
            "contradictions_and_tensions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["label", "description", "evidence_refs", "recommended_resolution"],
                    "properties": {
                        "label": string_schema(),
                        "description": string_schema(),
                        "evidence_refs": evidence_ref_array,
                        "recommended_resolution": string_schema(),
                    },
                },
            },
            "recommended_next_tests": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "title",
                        "test_type",
                        "why_now",
                        "hypothesis",
                        "suggested_route_shape",
                        "success_criteria",
                        "failure_criteria",
                        "evidence_refs",
                    ],
                    "properties": {
                        "title": string_schema(),
                        "test_type": {
                            "enum": [
                                "survey_followup",
                                "short_mission",
                                "album_mission",
                                "dead_end_check",
                                "frontier_route",
                                "landmark_confirmation",
                            ]
                        },
                        "why_now": string_schema(),
                        "hypothesis": string_schema(),
                        "suggested_route_shape": string_schema(),
                        "success_criteria": string_schema(),
                        "failure_criteria": string_schema(),
                        "evidence_refs": evidence_ref_array,
                    },
                },
            },
            "user_facing_copy": {
                "type": "object",
                "additionalProperties": False,
                "required": ["what_we_think_so_far", "careful_caveat", "first_mission_pitch"],
                "properties": {
                    "what_we_think_so_far": string_schema(),
                    "careful_caveat": string_schema(),
                    "first_mission_pitch": string_schema(),
                },
            },
        },
    }


def evaluator_output_schema() -> dict[str, Any]:
    score_block = {
        "type": "object",
        "additionalProperties": False,
        "required": ["score_0_to_10", "notes"],
        "properties": {"score_0_to_10": {"type": "integer", "minimum": 0, "maximum": 10}, "notes": string_schema()},
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "waymark.profile_evaluator_output.v0.1",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema_version",
            "evaluation_mode",
            "profile_public_id",
            "profile_writer_output_schema_version",
            "overall_decision",
            "overall_score_100",
            "score_breakdown",
            "red_flags",
            "best_output_features",
            "prompt_revision_recommendations",
            "schema_revision_recommendations",
            "pilot_readiness",
        ],
        "properties": {
            "schema_version": string_const_schema("waymark.profile_evaluator_output.v0.1"),
            "evaluation_mode": {"enum": ["evidence_only", "truth_scored_simulation"]},
            "profile_public_id": string_schema(),
            "profile_writer_output_schema_version": string_schema(),
            "overall_decision": {
                "enum": [
                    "approve_for_pilot",
                    "approve_with_minor_revisions",
                    "revise_prompt",
                    "revise_schema",
                    "reject_output",
                ]
            },
            "overall_score_100": {"type": "integer", "minimum": 0, "maximum": 100},
            "score_breakdown": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "schema_compliance",
                    "blindness_and_forbidden_context",
                    "evidence_fidelity",
                    "object_specificity_and_scope_control",
                    "uncertainty_and_contradiction_handling",
                    "waymark_voice_and_atlas_fit",
                    "next_test_actionability",
                    "simulation_truth_alignment",
                ],
                "properties": {
                    "schema_compliance": score_block,
                    "blindness_and_forbidden_context": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["score_0_to_15", "notes", "suspected_leakage", "leakage_examples"],
                        "properties": {
                            "score_0_to_15": {"type": "integer", "minimum": 0, "maximum": 15},
                            "notes": string_schema(),
                            "suspected_leakage": {"type": "boolean"},
                            "leakage_examples": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                    "evidence_fidelity": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["score_0_to_20", "notes", "unsupported_claims"],
                        "properties": {
                            "score_0_to_20": {"type": "integer", "minimum": 0, "maximum": 20},
                            "notes": string_schema(),
                            "unsupported_claims": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                    "object_specificity_and_scope_control": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["score_0_to_15", "notes", "overbroad_claims"],
                        "properties": {
                            "score_0_to_15": {"type": "integer", "minimum": 0, "maximum": 15},
                            "notes": string_schema(),
                            "overbroad_claims": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                    "uncertainty_and_contradiction_handling": score_block,
                    "waymark_voice_and_atlas_fit": score_block,
                    "next_test_actionability": score_block,
                    "simulation_truth_alignment": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": [
                            "score_0_to_10_or_null",
                            "notes",
                            "accurate_inferences",
                            "missed_truth_signals",
                            "false_positive_inferences",
                        ],
                        "properties": {
                            "score_0_to_10_or_null": {"type": ["integer", "null"], "minimum": 0, "maximum": 10},
                            "notes": string_schema(),
                            "accurate_inferences": {"type": "array", "items": {"type": "string"}},
                            "missed_truth_signals": {"type": "array", "items": {"type": "string"}},
                            "false_positive_inferences": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                },
            },
            "red_flags": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["severity", "category", "description", "evidence_or_output_ref", "recommended_fix"],
                    "properties": {
                        "severity": {"enum": ["minor", "major", "blocking"]},
                        "category": {
                            "enum": [
                                "schema",
                                "hidden_context",
                                "overclaim",
                                "unsupported_claim",
                                "poor_voice",
                                "weak_actionability",
                                "truth_miss",
                            ]
                        },
                        "description": string_schema(),
                        "evidence_or_output_ref": string_schema(),
                        "recommended_fix": string_schema(),
                    },
                },
            },
            "best_output_features": {"type": "array", "items": {"type": "string"}},
            "prompt_revision_recommendations": {"type": "array", "items": {"type": "string"}},
            "schema_revision_recommendations": {"type": "array", "items": {"type": "string"}},
            "pilot_readiness": {
                "type": "object",
                "additionalProperties": False,
                "required": ["ready_for_single_packet_pilot", "ready_for_batch_pilot", "required_before_batch"],
                "properties": {
                    "ready_for_single_packet_pilot": {"type": "boolean"},
                    "ready_for_batch_pilot": {"type": "boolean"},
                    "required_before_batch": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
    }


PROFILE_WRITER_SYSTEM = """You are the Cartenza Profile Writer.

Cartenza is a music taste-mapping product. Your job is to read visible survey evidence and generate a provisional taste profile that can seed a user's Atlas.

You must treat survey evidence as evidence, not verdict. Apple Music data is an exposure prior, not taste truth. Keep every inference at the smallest justified object: song, album, artist, archetype, region, or use-case. Preserve uncertainty. Do not make broad genre claims from one object.

You must use only the input packet provided. You must not infer, invent, or rely on hidden profile truth, hidden archetype tiers, hidden corpus reactions, hidden reason tags, simulator-private lookup status, or any private data not present in the packet.

Output must conform exactly to the provided JSON schema.
"""

PROFILE_WRITER_DEVELOPER = """Cartenza vocabulary:
- Landmark = high-confidence favorite or anchor.
- Region = cluster of related taste evidence.
- Frontier = promising but underexplored area.
- Dead End = false-nearby or caution hypothesis, not a blanket rejection unless strongly supported.
- Waypoint = useful or contextual music that is worth keeping but not a landmark.
- Signal = evidence from survey, playback, reaction, tag, skip, familiarity, or mission context.
- Route/Mission = future listening test.

Interpretation rules:
1. Apple evidence is exposure prior, not taste truth.
2. Love/strong_positive may support landmark evidence only when repeated or reinforced.
3. Like/positive is useful evidence but usually not enough for a landmark.
4. Ok is usually waypoint/context/familiarity evidence, not love.
5. Dont_like is negative evidence, but scope carefully.
6. Dont_know_enough is familiarity failure, not dislike.
7. Page intent matters. A reaction on a false-nearby/boundary item should be interpreted differently from a reaction on a payload signature item.
8. Canonical graph metadata may be used only as visible metadata. Do not invent hidden archetype meanings unless a human-readable label is provided.
9. Shown-but-unselected tags are weak evidence only.
10. Selected tags are explicit evidence, but still scoped to the object and page context.
11. Prefer promising frontier over confirmed region when evidence is thin.
12. Prefer dead-end risk over dead end when evidence is thin.
13. Never say the user loves a genre from one artist, album, or song.
14. Mention contradictions and mixed evidence.
15. The output should feel like Cartenza: warm, specific, curious, map-like, and honest about uncertainty.

Evidence reference rules:
- Every major claim must cite one or more visible evidence references from the packet.
- Evidence references should use the packet's evidence_ref values.
- Do not cite absent or hidden evidence.
"""

PROFILE_EVALUATOR_SYSTEM = """You are the Cartenza Profile Evaluator.

Your job is to evaluate whether a generated Cartenza taste profile is faithful to the visible evidence, properly scoped, useful for Atlas seeding, and safe for pilot use.

You are not evaluating whether the writer guessed aggressively. You should penalize overconfident claims, hidden-context leakage, broad genre overclaims, unsupported landmarks, and failure to preserve uncertainty.

If hidden truth is supplied, use it only for simulation scoring. Do not assume hidden truth was available to the Profile Writer unless the output contains unsupported claims that appear to leak it.
"""

PROFILE_EVALUATOR_DEVELOPER = """Evaluate the profile on these principles:
1. Evidence fidelity: claims must be supported by visible survey evidence.
2. Blindness: no hidden truth, hidden archetype tiers, unshown reactions, hidden reason tags, or simulator-private lookup status.
3. Object specificity: claims stay at the smallest justified object.
4. Apple-data handling: Apple data treated as exposure prior, not taste truth.
5. Reaction handling: love/like/ok/dont_like/dont_know_enough interpreted according to the packet's scale.
6. Page-intent handling: page intent, candidate basis, false-nearby checks, and boundary probes are used carefully.
7. Uncertainty: contradictions and thin evidence are preserved.
8. Cartenza voice: output feels like an Atlas seed, not generic recommender copy.
9. Actionability: recommended next tests are specific and useful.
10. Schema compliance: output conforms to expected schema and provides evidence references.

Scoring should be candid. Do not give high scores for pretty prose that overclaims.
"""


def response_request(
    system_prompt: str,
    developer_prompt: str,
    user_payload: dict[str, Any],
    output_schema: dict[str, Any],
    schema_name: str,
) -> dict[str, Any]:
    return {
        "model": "REPLACE_WITH_OPENAI_MODEL",
        "input": [
            {"role": "system", "content": [{"type": "input_text", "text": system_prompt}]},
            {"role": "developer", "content": [{"type": "input_text", "text": developer_prompt}]},
            {"role": "user", "content": [{"type": "input_text", "text": json.dumps(user_payload, indent=2)}]},
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": schema_name,
                "strict": True,
                "schema": output_schema,
            }
        },
    }


def render_report(public_packet: dict[str, Any], hidden_truth: dict[str, Any]) -> str:
    counts = public_packet["observed_response_counts_by_stage"]
    lines = [
        "# LLM Profile Review Pilot Harness",
        "",
        f"Generated: {GENERATED_AT}",
        "",
        "## Scope",
        "",
        "This artifact set prepares a narrow two-call API pilot for Cartenza taste-profile qualitative review.",
        "",
        "- Profile Writer input is visible survey evidence only.",
        "- Evidence-only Evaluator mode uses the public packet plus a Profile Writer output.",
        "- Truth-scored Evaluator mode is simulator-private and may use the hidden truth packet.",
        "- No OpenAI API call is executed by this generator.",
        "",
        "## Reference Fixture",
        "",
        f"- Profile: `{public_packet['profile_public_id']}`",
        f"- Config: `{REFERENCE_CONFIG_ID}`",
        f"- Tiles: `{public_packet['page_count_config']['tile_count']}`",
        f"- Input fingerprint: `{public_packet['input_fingerprint']}`",
        "",
        "## Visible Response Counts",
        "",
        "| Stage | Love | Like | Ok | Dont like | Dont know enough |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for stage in ["artist", "album", "song"]:
        stage_counts = counts[stage]
        lines.append(
            f"| {stage} | {stage_counts['love']} | {stage_counts['like']} | {stage_counts['ok']} | {stage_counts['dont_like']} | {stage_counts['dont_know_enough']} |"
        )
    lines.extend(
        [
            "",
            "## Boundary Checks",
            "",
            f"- Public packet declares hidden generation inputs absent: `{public_packet['blindness_contract']['hidden_inputs_used_for_generation'] is False}`",
            f"- Public packet declares hidden truth absent: `{public_packet['blindness_contract']['public_packet_contains_hidden_truth'] is False}`",
            f"- Simulator-private held-out populated reactions summarized: `{hidden_truth['heldout_populated_reaction_count']}`",
            "- Hidden reason tags and lookup status are not exported to the public packet.",
            "- Canonical graph data remains read-only; this generator consumes only existing simulation artifacts.",
            "",
            "## Next Pilot Step",
            "",
            "Run the Profile Writer request template through the OpenAI API with a chosen reasoning-capable model. Then insert the writer JSON into the Evaluator templates and run evidence-only first, truth-scored second.",
            "",
        ]
    )
    return "\n".join(lines)


def build() -> None:
    max_depth_path = load_json(BACKTEST_DIR / "max_depth_paths" / f"{REFERENCE_PROFILE_PUBLIC_ID}.json")
    apple_payload = load_json(SIM_DIR / "apple_payloads" / "apple_payload_01.json")
    hidden_corpus = load_json(SIM_DIR / "hidden_reaction_corpora" / "hidden_corpus_01.json")
    fake_profile = load_json(SIM_DIR / "fake_profiles" / "fake_profile_01.json")

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    public_packet = build_public_packet(max_depth_path, apple_payload)
    hidden_truth = hidden_truth_packet(public_packet, hidden_corpus, fake_profile)
    input_schema = writer_input_schema()
    writer_schema = profile_writer_output_schema()
    evaluator_schema = evaluator_output_schema()

    public_packet_path = OUT_DIR / "public_packets" / REFERENCE_PUBLIC_PACKET_FILENAME
    hidden_truth_path = OUT_DIR / "simulator_private" / "hidden_truth_packets" / "hidden_truth_public_profile_01_A2_Al1_S1.json"

    write_json(public_packet_path, public_packet)
    write_json(hidden_truth_path, hidden_truth)
    write_json(OUT_DIR / "schemas" / "profile_writer_input.schema.json", input_schema)
    write_json(OUT_DIR / "schemas" / "profile_writer_output.schema.json", writer_schema)
    write_json(OUT_DIR / "schemas" / "profile_evaluator_output.schema.json", evaluator_schema)
    write_text(OUT_DIR / "prompts" / "profile_writer_system.md", PROFILE_WRITER_SYSTEM)
    write_text(OUT_DIR / "prompts" / "profile_writer_developer.md", PROFILE_WRITER_DEVELOPER)
    write_text(OUT_DIR / "prompts" / "profile_evaluator_system.md", PROFILE_EVALUATOR_SYSTEM)
    write_text(OUT_DIR / "prompts" / "profile_evaluator_developer.md", PROFILE_EVALUATOR_DEVELOPER)

    writer_user_payload = {
        "task": "Generate a provisional Cartenza taste profile from the visible survey output packet. Return only schema-valid JSON.",
        "visible_survey_output_packet": public_packet,
    }
    evidence_eval_payload = {
        "task": "Evaluate the Profile Writer output in evidence-only mode. Return only schema-valid JSON.",
        "evaluation_mode": "evidence_only",
        "visible_survey_output_packet": public_packet,
        "profile_writer_output": {"replace_with": "waymark.profile_writer_output.v0.1 JSON"},
        "optional_hidden_truth_packet_for_simulation_only": None,
        "optional_backtest_results": None,
    }
    truth_eval_payload = {
        "task": "Evaluate the Profile Writer output in truth-scored simulation mode. Return only schema-valid JSON.",
        "evaluation_mode": "truth_scored_simulation",
        "visible_survey_output_packet": public_packet,
        "profile_writer_output": {"replace_with": "waymark.profile_writer_output.v0.1 JSON"},
        "optional_hidden_truth_packet_for_simulation_only": hidden_truth,
        "optional_backtest_results": None,
    }
    write_json(
        OUT_DIR / "api_requests" / "profile_writer_reference_request.json",
        response_request(
            PROFILE_WRITER_SYSTEM,
            PROFILE_WRITER_DEVELOPER,
            writer_user_payload,
            writer_schema,
            "waymark_profile_writer_output_v0_1",
        ),
    )
    write_json(
        OUT_DIR / "api_requests" / "evaluator_evidence_only_reference_request.json",
        response_request(
            PROFILE_EVALUATOR_SYSTEM,
            PROFILE_EVALUATOR_DEVELOPER,
            evidence_eval_payload,
            evaluator_schema,
            "waymark_profile_evaluator_output_v0_1",
        ),
    )
    write_json(
        OUT_DIR / "simulator_private" / "api_requests" / "evaluator_truth_scored_reference_request.json",
        response_request(
            PROFILE_EVALUATOR_SYSTEM,
            PROFILE_EVALUATOR_DEVELOPER,
            truth_eval_payload,
            evaluator_schema,
            "waymark_profile_evaluator_output_v0_1",
        ),
    )
    write_text(OUT_DIR / "reports" / "qualitative_profile_review_report.md", render_report(public_packet, hidden_truth))
    write_text(
        OUT_DIR / "README.md",
        "\n".join(
            [
                "# LLM Profile Review Pilot",
                "",
                "This directory contains the single-fixture Profile Writer / Evaluator pilot harness.",
                "",
                "- `public_packets/` is safe Profile Writer input.",
                "- `api_requests/` contains public/blind request templates.",
                "- `simulator_private/` contains truth-scored evaluator material only.",
                "- `schemas/` contains strict Structured Output contracts.",
                "",
            ]
        ),
    )


def main() -> int:
    build()
    print(f"Generated LLM profile review pilot at {OUT_DIR.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
