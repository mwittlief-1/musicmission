#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = REPO_ROOT / "data/survey_simulation"
GRAPH_SURFACE_DIR = REPO_ROOT / "data/canonical_graph/normalization_pass_2"
DEFAULT_SOURCE_PACKET_CANDIDATES = (
    SIM_DIR
    / "llm_profile_review/api_pilot_3x3/public_packets"
    / "cartenza_survey_output_packet_public_profile_01_A4_Al2_S3.json",
    SIM_DIR
    / "llm_profile_review/api_pilot_3x3/public_packets"
    / "waymark_survey_output_packet_public_profile_01_A4_Al2_S3.json",
)
DEFAULT_SOURCE_PACKET = next(
    (path for path in DEFAULT_SOURCE_PACKET_CANDIDATES if path.exists()),
    DEFAULT_SOURCE_PACKET_CANDIDATES[0],
)
DEFAULT_OUTPUT = (
    SIM_DIR
    / "survey_evidence_export/alpha1_required_intake"
    / "waymark_survey_output_packet_public_profile_01_A4_Al2_S4_alpha1_intake.json"
)

ZERO_APPLE_EVIDENCE = {
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

FIXTURE_REACTION_PATTERN = [
    "like",
    "ok",
    "dont_like",
    "dont_know_enough",
    "like",
    "ok",
    "dont_like",
    "ok",
    "like",
    "dont_know_enough",
    "ok",
    "dont_like",
]

OBJECT_ID_KEYS = {
    "artist": "canonical_artist_id",
    "album": "canonical_album_id",
    "song_recording": "canonical_song_recording_id",
}

SURFACE_FILES = {
    "artist": "survey_artist_candidates_v0_2.json",
    "album": "survey_album_candidates_v0_2.json",
    "song_recording": "survey_song_candidates_v0_2.json",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "untitled"


def stable_fingerprint(packet: dict[str, Any]) -> str:
    payload = {
        "profile_public_id": packet["profile_public_id"],
        "run_id": packet["run_id"],
        "page_count_config": packet["page_count_config"],
        "page_ids": [page["page_id"] for page in packet["pages"]],
        "response_ids": [
            tile["response_id"]
            for page in packet["pages"]
            for tile in page["tiles"]
        ],
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def load_surface_candidates(object_type: str) -> list[dict[str, Any]]:
    data = load_json(GRAPH_SURFACE_DIR / SURFACE_FILES[object_type])
    candidates = []
    for family in data.get("families", []):
        for bucket in ["page1_core", "page2_adaptive", "page3_deep"]:
            for candidate in family.get(bucket, []):
                if candidate.get("review_status") != "approved":
                    continue
                candidates.append({**candidate, "source_bucket": bucket})
    return candidates


def surface_indexes() -> tuple[dict[str, set[str]], dict[str, list[dict[str, Any]]]]:
    by_type = {object_type: load_surface_candidates(object_type) for object_type in SURFACE_FILES}
    approved_ids = {
        object_type: {candidate["canonical_entity_id"] for candidate in candidates}
        for object_type, candidates in by_type.items()
    }
    return approved_ids, by_type


def canonical_recording_credit() -> dict[str, dict[str, str]]:
    rows = load_json(GRAPH_SURFACE_DIR / "canonical_recording_versions.json")
    return {
        row["recording_id"]: {
            "artist_display_name": row.get("display_artist_credit", ""),
            "display_name": row.get("recording_title", ""),
        }
        for row in rows
    }


def ref_id(ref: dict[str, Any]) -> str | None:
    return ref.get(OBJECT_ID_KEYS[ref["object_type"]])


def evidence_ref(page_id: str, stage: str, position: int, display_name: str, reaction: str) -> str:
    return f"{page_id}:{stage}:{position:02d}:{display_name}:{reaction}"


def graph_context_for(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "family_numbers": [candidate["family_id"]],
        "archetype_ids": list(candidate.get("archetype_ids", [])),
        "roles": [],
        "best_recognition_tier": "unknown",
        "best_survey_tier": "unknown",
    }


def replacement_tile(
    *,
    tile: dict[str, Any],
    page: dict[str, Any],
    candidates: list[dict[str, Any]],
    used_ids: set[str],
    recording_credit: dict[str, dict[str, str]],
) -> dict[str, Any]:
    object_type = tile["music_object_ref"]["object_type"]
    source_families = tile.get("graph_context", {}).get("family_numbers") or []
    source_family = source_families[0] if source_families else None
    replacement = next(
        (
            candidate
            for candidate in candidates
            if candidate["canonical_entity_id"] not in used_ids
            and (source_family is None or candidate.get("family_id") == source_family)
        ),
        None,
    )
    if replacement is None:
        replacement = next(
            candidate
            for candidate in candidates
            if candidate["canonical_entity_id"] not in used_ids
        )

    display_name = replacement["display_label"]
    ref: dict[str, Any] = {
        "object_type": object_type,
        "ref_source": "canonical_graph",
        OBJECT_ID_KEYS[object_type]: replacement["canonical_entity_id"],
        "display_name": display_name,
        "resolution_state": "resolved",
    }
    if object_type == "song_recording":
        credit = recording_credit.get(replacement["canonical_entity_id"], {})
        if credit.get("artist_display_name"):
            ref["artist_display_name"] = credit["artist_display_name"]
        if credit.get("display_name"):
            ref["display_name"] = credit["display_name"]
            display_name = credit["display_name"]

    reaction = "dont_know_enough"
    return {
        "evidence_ref": evidence_ref(page["page_id"], page["stage"], tile["position"], display_name, reaction),
        "position": tile["position"],
        "tile_id": tile["tile_id"],
        "response_id": tile["response_id"],
        "music_object_ref": ref,
        "reaction": reaction,
        "atlas_signal_interpretation": "familiarity_uncertainty",
        "app_ui_candidate": "unknown",
        "page_intent": replacement["survey_intent"],
        "candidate_basis": [
            "alpha1_required_intake_contract_fixture",
            "approved_canonical_graph_surface",
            "replacement_for_unapproved_source_tile",
        ],
        "graph_context": graph_context_for(replacement),
        "apple_evidence_summary": ZERO_APPLE_EVIDENCE,
        "scores": {},
        "response_evidence_refs": [],
        "shown_unselected_tags": [],
        "observed_selected_tags": [],
        "suppression_warnings": [],
    }


def normalize_existing_pages(packet: dict[str, Any]) -> dict[str, Any]:
    approved_ids, candidates_by_type = surface_indexes()
    recording_credit = canonical_recording_credit()
    used_ids = {
        ref_id(tile["music_object_ref"])
        for page in packet["pages"]
        for tile in page["tiles"]
        if ref_id(tile["music_object_ref"])
    }
    for page in packet["pages"]:
        for index, tile in enumerate(list(page["tiles"])):
            object_type = tile["music_object_ref"]["object_type"]
            if ref_id(tile["music_object_ref"]) not in approved_ids[object_type]:
                replacement = replacement_tile(
                    tile=tile,
                    page=page,
                    candidates=candidates_by_type[object_type],
                    used_ids=used_ids,
                    recording_credit=recording_credit,
                )
                used_ids.add(ref_id(replacement["music_object_ref"]) or "")
                page["tiles"][index] = replacement
    return packet


def choose_song_page_004_candidates(packet: dict[str, Any]) -> list[dict[str, Any]]:
    existing_ids = {
        tile["music_object_ref"].get("canonical_song_recording_id")
        for page in packet["pages"]
        for tile in page["tiles"]
        if tile["music_object_ref"]["object_type"] == "song_recording"
    }
    candidates = [
        candidate
        for candidate in load_surface_candidates("song_recording")
        if candidate["canonical_entity_id"] not in existing_ids
    ]
    candidates.sort(key=lambda row: (-float(row.get("priority_score", 0)), row["family_id"], row["canonical_entity_id"]))

    selected = []
    used_families: set[int] = set()
    for candidate in candidates:
        if candidate["family_id"] in used_families:
            continue
        selected.append(candidate)
        used_families.add(candidate["family_id"])
        if len(selected) == 12:
            return selected
    for candidate in candidates:
        if candidate not in selected:
            selected.append(candidate)
        if len(selected) == 12:
            return selected
    raise ValueError("Could not select 12 approved song candidates for Alpha intake page 4")


def build_song_page_004(packet: dict[str, Any]) -> dict[str, Any]:
    recording_credit = canonical_recording_credit()
    candidates = choose_song_page_004_candidates(packet)
    tiles = []
    for index, candidate in enumerate(candidates, start=1):
        reaction = FIXTURE_REACTION_PATTERN[index - 1]
        credit = recording_credit.get(candidate["canonical_entity_id"], {})
        display_name = credit.get("display_name") or candidate["display_label"]
        ref = {
            "object_type": "song_recording",
            "ref_source": "canonical_graph",
            "canonical_song_recording_id": candidate["canonical_entity_id"],
            "display_name": display_name,
            "resolution_state": "resolved",
        }
        if credit.get("artist_display_name"):
            ref["artist_display_name"] = credit["artist_display_name"]
        tiles.append(
            {
                "evidence_ref": evidence_ref("song_page_004", "song", index, display_name, reaction),
                "position": index,
                "tile_id": f"tile_{index:02d}",
                "response_id": f"song_page_004_resp_{index:02d}",
                "music_object_ref": ref,
                "reaction": reaction,
                "atlas_signal_interpretation": {
                    "love": "strong_positive",
                    "like": "positive",
                    "ok": "weak_positive_or_familiarity",
                    "dont_like": "negative_scope_carefully",
                    "dont_know_enough": "familiarity_uncertainty",
                }[reaction],
                "app_ui_candidate": {
                    "love": "favorite",
                    "like": "like",
                    "ok": "keep",
                    "dont_like": "not_for_me",
                    "dont_know_enough": "unknown",
                }[reaction],
                "page_intent": candidate["survey_intent"],
                "candidate_basis": [
                    "alpha1_required_intake_contract_fixture",
                    "approved_canonical_graph_surface",
                    "song_page_004_extension",
                ],
                "graph_context": graph_context_for(candidate),
                "apple_evidence_summary": ZERO_APPLE_EVIDENCE,
                "scores": {},
                "response_evidence_refs": [],
                "shown_unselected_tags": [],
                "observed_selected_tags": [],
                "suppression_warnings": [],
            }
        )
    return {
        "page_id": "song_page_004",
        "stage": "song",
        "page_number": 4,
        "tile_count": 12,
        "tiles": tiles,
    }


def response_counts(packet: dict[str, Any]) -> dict[str, dict[str, int]]:
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    for page in packet["pages"]:
        stage = page["stage"]
        for tile in page["tiles"]:
            counts[stage][tile["reaction"]] += 1
    reactions = ["love", "like", "ok", "dont_like", "dont_know_enough"]
    return {
        stage: {reaction: counts[stage][reaction] for reaction in reactions}
        for stage in ["artist", "album", "song"]
    }


def cluster_summary(packet: dict[str, Any]) -> dict[str, Any]:
    buckets = {
        "positive_clusters": {"love", "like"},
        "negative_clusters": {"dont_like"},
        "ok_waypoint_clusters": {"ok"},
        "unknown_clusters": {"dont_know_enough"},
    }
    output: dict[str, Any] = {}
    for bucket_name, reactions in buckets.items():
        refs_by_label: dict[str, list[str]] = defaultdict(list)
        for page in packet["pages"]:
            for tile in page["tiles"]:
                if tile["reaction"] not in reactions:
                    continue
                graph = tile.get("graph_context", {})
                labels = [f"family:{family}" for family in graph.get("family_numbers", [])]
                labels.extend(f"archetype:{archetype}" for archetype in graph.get("archetype_ids", []))
                for label in labels:
                    refs_by_label[label].append(tile["evidence_ref"])
        output[bucket_name] = [
            {
                "label": label,
                "visible_response_count": len(refs),
                "evidence_refs": refs[:10],
            }
            for label, refs in sorted(refs_by_label.items(), key=lambda item: (-len(item[1]), item[0]))[:10]
        ]

    output["multi_archetype_junctions_seen"] = [
        {
            "display_name": tile["music_object_ref"]["display_name"],
            "reaction": tile["reaction"],
            "evidence_ref": tile["evidence_ref"],
            "archetype_ids": tile.get("graph_context", {}).get("archetype_ids", []),
        }
        for page in packet["pages"]
        for tile in page["tiles"]
        if len(tile.get("graph_context", {}).get("archetype_ids", [])) > 1
    ][:12]
    output["false_nearby_tests_seen"] = [
        {
            "display_name": tile["music_object_ref"]["display_name"],
            "reaction": tile["reaction"],
            "evidence_ref": tile["evidence_ref"],
            "page_intent": tile.get("page_intent"),
        }
        for page in packet["pages"]
        for tile in page["tiles"]
        if "false" in tile.get("page_intent", "") or "boundary" in tile.get("page_intent", "")
    ][:12]
    return output


def build_fixed_packet(source_packet_path: Path) -> dict[str, Any]:
    packet = copy.deepcopy(load_json(source_packet_path))
    packet = normalize_existing_pages(packet)
    packet["schema_version"] = packet.get("schema_version", "waymark.profile_writer_input.v0.1")
    packet["purpose"] = "Alpha 1 required Survey intake fixture"
    packet["run_id"] = f"{packet['profile_public_id']}_alpha1_required_intake_A4_Al2_S4"
    packet["created_at"] = utc_now()
    packet["page_count_config"] = {
        "config_id": "A4_Al2_S4",
        "artist_pages": 4,
        "album_pages": 2,
        "song_pages": 4,
        "tile_count": 120,
    }
    packet["alpha1_required_intake_policy"] = {
        "required_first_run": True,
        "optional_early_exit": False,
        "artist_pages": 4,
        "album_pages": 2,
        "song_pages": 4,
        "page_004_song_generation": "approved_canonical_graph_surface_extension",
        "page_004_response_policy": "deterministic_contract_fixture_not_hidden_truth",
        "hidden_inputs_used_for_page_generation": False,
    }
    packet["pages"].append(build_song_page_004(packet))
    packet["observed_response_counts_by_stage"] = response_counts(packet)
    packet["deterministic_visible_evidence_summary"] = cluster_summary(packet)
    packet["input_fingerprint"] = stable_fingerprint(packet)
    return packet


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Alpha 1 required A4/Al2/S4 Survey intake public packet.")
    parser.add_argument("--source-packet", type=Path, default=DEFAULT_SOURCE_PACKET)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    packet = build_fixed_packet(args.source_packet.resolve())
    output = args.output.resolve()
    write_json(output, packet)
    print(output.relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
