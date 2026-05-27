#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = REPO_ROOT / "data/survey_simulation/llm_profile_review/api_pilot_3x3/public_packets"
PROFILE_WRITER_REQUEST_DIR = REPO_ROOT / "data/survey_simulation/llm_profile_review/api_pilot_3x3/executed_requests"
OUTPUT_DIR = REPO_ROOT / "data/atlas_schema/ingestion_proof/a3_gpt_5_5_3x3"
CONTRACT_OUTPUT_DIR = REPO_ROOT / "data/atlas_schema/ingestion_proof/survey_to_atlas_digest_v0_1"
SCHEMA_VERSION = "0.1"
INGESTION_VERSION = "0.1.1"
GENERATED_AT = "2026-05-20T12:00:00-04:00"

FORBIDDEN_PRIVATE_KEYS = {
    "hidden_profile_truth",
    "hidden_archetype_tiers",
    "hidden_corpus_reactions",
    "hidden_lookup_status",
    "hidden_reason_tags",
    "reason_tags",
    "primary_archetype_affinities",
    "secondary_archetype_affinities",
    "hidden_anti_affinities",
    "fake_profile_id",
    "hidden_lookup",
    "simulator_private_lookup_status",
}

FORBIDDEN_PRIVATE_PHRASES = [
    "hidden_profile_truth",
    "hidden_corpus_",
    "fake_profile_",
    "Classic Suburban Dad",
    "R&B / Hip-Hop Listener",
    "Theater / Family Context User",
]

ROLE_TO_DIGEST_KEY = {
    "landmark": "landmarks",
    "region": "regions",
    "frontier": "frontiers",
    "dead_end": "dead_ends",
    "waypoint": "waypoints",
}


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CONTRACT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_role_assignment_policy_doc()
    write_tag_bearing_fixture()
    packet_paths = sorted(INPUT_DIR.glob("waymark_survey_output_packet_public_profile_*_A3_Al1_S2.json"))
    if not packet_paths:
        raise SystemExit(f"No A3 public packets found under {INPUT_DIR.relative_to(REPO_ROOT)}")

    aggregate: list[dict[str, Any]] = []
    for packet_path in packet_paths:
        result = ingest_packet(packet_path)
        aggregate.append(result)

    write_json(
        OUTPUT_DIR / "a3_ingestion_proof_manifest.json",
        {
            "schema_version": "waymark.atlas_a3_ingestion_proof_manifest.v0.1",
            "ingestion_version": INGESTION_VERSION,
            "generated_at": GENERATED_AT,
            "source_input_dir": rel(INPUT_DIR),
            "output_dir": rel(OUTPUT_DIR),
            "profile_count": len(aggregate),
            "profiles": aggregate,
        },
    )
    write_markdown_summary(aggregate)
    write_contract_manifest(aggregate)
    return 0


def ingest_packet(packet_path: Path) -> dict[str, Any]:
    packet = load_json(packet_path)
    profile_id = packet["profile_public_id"]
    profile_num = profile_id.rsplit("_", 1)[-1]
    profile_label = f"profile_{profile_num}_A3"
    user_id = f"fixture_{profile_id}"
    visible_packet_id = packet_path.stem

    tiles = flatten_tiles(packet)
    density_contexts = build_density_contexts(tiles)
    response_index = {tile["response_id"]: tile for tile in tiles if tile.get("response_id")}
    invalid_refs, quarantined_refs = validate_response_refs(tiles, response_index)
    hidden_check = hidden_private_field_check(packet, packet_path)
    unresolved_refs = []
    empty_redundant_count = count_empty_redundant_fields(packet)

    signal_records: list[dict[str, Any]] = []
    nodes_by_key: dict[str, dict[str, Any]] = {}
    node_signal_ids: dict[str, list[str]] = defaultdict(list)
    node_confidence_scores: dict[str, list[float]] = defaultdict(list)
    role_assignments: list[dict[str, Any]] = []
    update_candidates: list[dict[str, Any]] = []
    signal_lookup: dict[str, dict[str, Any]] = {}

    for tile in tiles:
        page = tile["_page"]
        normalized_ref = normalize_music_ref(tile.get("music_object_ref") or {}, tile.get("graph_context") or {})
        if normalized_ref["ref_source"] == "unresolved" or normalized_ref["resolution_state"] == "needs_resolution":
            unresolved_refs.append(
                {
                    "response_id": tile["response_id"],
                    "display_name": normalized_ref["display_name"],
                    "reason": "music_object_ref requires resolution",
                }
            )
        node_id = node_id_for(profile_id, normalized_ref)
        signal_id = f"signal:survey:{slug(profile_id)}:{slug(tile['response_id'])}"
        role_policy = density_aware_role_policy(
            tile=tile,
            music_ref=normalized_ref,
            density_context=density_contexts[tile["response_id"]],
        )
        role = role_policy["role"]
        candidate_pool_behavior = role_policy["candidate_pool_behavior"]
        update_id = f"update_candidate:survey:{slug(profile_id)}:{slug(tile['response_id'])}:{role}"

        signal = make_signal(
            signal_id=signal_id,
            user_id=user_id,
            tile=tile,
            page=page,
            packet=packet,
            packet_path=packet_path,
            profile_id=profile_id,
            visible_packet_id=visible_packet_id,
            music_ref=normalized_ref,
            node_id=node_id,
            update_id=update_id,
            quarantined_refs=quarantined_refs.get(tile["response_id"], []),
        )
        signal_records.append(signal)
        signal_lookup[signal_id] = signal
        node_signal_ids[node_id].append(signal_id)
        node_confidence_scores[node_id].append(signal["interpretation_confidence"])

        if node_id not in nodes_by_key:
            nodes_by_key[node_id] = make_atlas_node(
                atlas_node_id=node_id,
                user_id=user_id,
                music_ref=normalized_ref,
                signal_id=signal_id,
                tile=tile,
                packet_created_at=packet.get("created_at") or GENERATED_AT,
            )

        role_assignment_id = f"role:survey:{slug(profile_id)}:{slug(tile['response_id'])}:{role}"
        role_assignments.append(
            make_role_assignment(
                role_assignment_id=role_assignment_id,
                user_id=user_id,
                atlas_node_id=node_id,
                role=role,
                candidate_pool_behavior=candidate_pool_behavior,
                signal_id=signal_id,
                tile=tile,
                role_policy=role_policy,
            )
        )
        update_candidates.append(
            make_update_candidate(
                update_id=update_id,
                user_id=user_id,
                source_signal_ids=[signal_id],
                target_atlas_node_id=node_id,
                target_role_assignment_id=role_assignment_id,
                role=role,
                candidate_pool_behavior=candidate_pool_behavior,
                tile=tile,
                music_ref=normalized_ref,
                role_policy=role_policy,
            )
        )

    nodes = []
    for node_id, node in nodes_by_key.items():
        evidence_ids = sorted(set(node_signal_ids[node_id]))
        node["evidence_signal_ids"] = evidence_ids
        max_conf = max(node_confidence_scores[node_id]) if node_confidence_scores[node_id] else 0.3
        node["confidence"] = confidence(
            min(0.74, max_conf),
            "survey_pattern",
            "Node exists to preserve visible survey evidence. It carries no role truth.",
        )
        nodes.append(node)

    contradiction_candidates, contradictions = build_contradiction_candidates(
        profile_id=profile_id,
        user_id=user_id,
        signals=signal_records,
    )
    update_candidates.extend(contradiction_candidates)

    digest = build_digest_view(
        profile_id=profile_id,
        user_id=user_id,
        signals=signal_records,
        nodes=nodes,
        role_assignments=role_assignments,
        update_candidates=update_candidates,
        contradictions=contradictions,
        packet=packet,
        visible_packet_id=visible_packet_id,
    )

    node_interpretation_input = build_node_interpretation_input(
        profile_id=profile_id,
        packet=packet,
        digest=digest,
        signals=signal_records,
        role_assignments=role_assignments,
        update_candidates=update_candidates,
    )
    slim_node_interpretation_input = build_slim_node_interpretation_input(
        profile_id=profile_id,
        digest=digest,
        signals=signal_records,
        nodes=nodes,
        role_assignments=role_assignments,
        update_candidates=update_candidates,
        contradictions=contradictions,
    )

    validation_report = build_validation_report(
        packet=packet,
        packet_path=packet_path,
        profile_label=profile_label,
        tiles=tiles,
        invalid_refs=invalid_refs,
        quarantined_refs=quarantined_refs,
        hidden_check=hidden_check,
        unresolved_refs=unresolved_refs,
        empty_redundant_count=empty_redundant_count,
    )

    output_paths = write_profile_outputs(
        profile_label=profile_label,
        packet_path=packet_path,
        validation_report=validation_report,
        signals=signal_records,
        nodes=nodes,
        role_assignments=role_assignments,
        update_candidates=update_candidates,
        digest=digest,
        node_interpretation_input=node_interpretation_input,
        slim_node_interpretation_input=slim_node_interpretation_input,
    )
    size_report = build_size_report(
        profile_id=profile_id,
        profile_label=profile_label,
        packet_path=packet_path,
        output_paths=output_paths,
    )
    write_json(OUTPUT_DIR / f"size_report_{profile_label}.json", size_report)
    write_size_report_md(profile_label, size_report)

    validation_report["output_schema_bundle_ref"] = rel(output_paths["schema_bundle"])
    write_json(OUTPUT_DIR / f"validation_report_{profile_label}.json", validation_report)
    write_validation_report_md(profile_label, validation_report)
    contract_paths = write_contract_profile_outputs(
        profile_label=profile_label,
        profile_id=profile_id,
        packet_path=packet_path,
        validation_report=validation_report,
        signals=signal_records,
        nodes=nodes,
        role_assignments=role_assignments,
        update_candidates=update_candidates,
        digest=digest,
        size_report=size_report,
    )

    return {
        "profile_public_id": profile_id,
        "profile_label": profile_label,
        "input_file": rel(packet_path),
        "validation_report": rel(OUTPUT_DIR / f"validation_report_{profile_label}.json"),
        "size_report": rel(OUTPUT_DIR / f"size_report_{profile_label}.json"),
        "signals": len(signal_records),
        "atlas_nodes": len(nodes),
        "atlas_role_assignments": len(role_assignments),
        "possible_atlas_update_candidates": len(update_candidates),
        "digest_view": rel(output_paths["digest"]),
        "slim_node_interpretation_input": rel(output_paths["slim_interpretation"]),
        "contract_profile_dir": rel(contract_paths["profile_dir"]),
        "status": validation_report["status"],
    }


def flatten_tiles(packet: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for page in packet.get("pages", []):
        page_context = {
            "page_id": page.get("page_id"),
            "stage": page.get("stage"),
            "page_number": page.get("page_number"),
            "page_mode": page.get("page_mode"),
            "tile_count": page.get("tile_count"),
            "generator_visible_inputs": page.get("generator_visible_inputs") or {},
        }
        for tile in page.get("tiles", []):
            row = dict(tile)
            row["_page"] = page_context
            rows.append(row)
    return rows


def validate_response_refs(
    tiles: list[dict[str, Any]],
    response_index: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    invalid = []
    quarantined: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for tile in tiles:
        for ref in tile.get("response_evidence_refs") or []:
            ref_response_id = ref.get("response_id")
            ref_page_id = ref.get("page_id")
            ref_tile_id = ref.get("tile_id")
            visible = response_index.get(ref_response_id)
            reason = None
            if visible is None:
                reason = "response_id_not_present_in_visible_packet"
            elif ref_page_id and visible["_page"].get("page_id") != ref_page_id:
                reason = "page_id_mismatch"
            elif ref_tile_id and visible.get("tile_id") != ref_tile_id:
                reason = "tile_id_mismatch"
            if reason:
                issue = {
                    "source_response_id": tile.get("response_id"),
                    "ref": ref,
                    "reason": reason,
                    "integrity_state": "quarantined",
                }
                invalid.append(issue)
                quarantined[tile.get("response_id")].append(issue)
    return invalid, quarantined


def build_density_contexts(tiles: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    neighborhoods: dict[str, list[dict[str, Any]]] = {}
    for tile in tiles:
        response_id = tile["response_id"]
        graph_context = tile.get("graph_context") or {}
        families = set(graph_context.get("family_numbers") or [])
        archetypes = set(graph_context.get("archetype_ids") or [])
        artist = artist_context_key(tile)
        neighbors = []
        for other in tiles:
            if other["response_id"] == response_id:
                continue
            other_context = other.get("graph_context") or {}
            other_families = set(other_context.get("family_numbers") or [])
            other_archetypes = set(other_context.get("archetype_ids") or [])
            shared_graph = bool(families & other_families or archetypes & other_archetypes)
            shared_artist = bool(artist and artist == artist_context_key(other))
            if shared_graph or shared_artist:
                neighbors.append(other)
        neighborhoods[response_id] = neighbors

    contexts = {}
    for tile in tiles:
        response_id = tile["response_id"]
        neighbors = neighborhoods[response_id]
        positive = [item for item in neighbors if item.get("reaction") in {"love", "like"}]
        strong_positive = [item for item in neighbors if item.get("reaction") == "love"]
        negative = [item for item in neighbors if item.get("reaction") == "dont_like"]
        unknown = [item for item in neighbors if item.get("reaction") == "dont_know_enough"]
        total = len(neighbors)
        artist = artist_context_key(tile)
        artist_scope_items = [item for item in tiles if artist and artist_context_key(item) == artist]
        recurrence_scopes = sorted({(item.get("music_object_ref") or {}).get("object_type") for item in artist_scope_items})
        apple = tile.get("apple_evidence_summary") or {}
        contexts[response_id] = {
            "policy_version": "density_aware_provisional_v0_1_1",
            "neighborhood_size": total,
            "local_positive_count": len(positive),
            "local_strong_positive_count": len(strong_positive),
            "local_negative_count": len(negative),
            "local_unknown_count": len(unknown),
            "local_positive_density": round(len(positive) / total, 3) if total else 0.0,
            "local_negative_density": round(len(negative) / total, 3) if total else 0.0,
            "local_unknown_density": round(len(unknown) / total, 3) if total else 0.0,
            "recurrence_scope_count": len(recurrence_scopes),
            "recurrence_scopes": recurrence_scopes,
            "apple_exposure_score": apple.get("exposure_score", 0.0),
            "apple_probable_affinity_score": apple.get("probable_affinity_score", 0.0),
            "page_intent": tile.get("page_intent"),
            "graph_family_numbers": sorted((tile.get("graph_context") or {}).get("family_numbers") or []),
            "graph_archetype_ids": sorted((tile.get("graph_context") or {}).get("archetype_ids") or []),
            "graph_roles": sorted((tile.get("graph_context") or {}).get("roles") or []),
        }
    return contexts


def density_aware_role_policy(
    *,
    tile: dict[str, Any],
    music_ref: dict[str, Any],
    density_context: dict[str, Any],
) -> dict[str, Any]:
    reaction = tile.get("reaction")
    fallback_role = role_for_reaction(reaction, music_ref["object_type"])
    positive_density = density_context["local_positive_density"]
    negative_density = density_context["local_negative_density"]
    unknown_density = density_context["local_unknown_density"]
    recurrence_scope_count = density_context["recurrence_scope_count"]
    page_intent = tile.get("page_intent") or ""
    role = fallback_role
    reason = "Fallback direct reaction mapping; retained only as provisional contract behavior."
    candidate_pool_behavior = candidate_pool_behavior_for_role(role, reaction)

    if reaction == "love":
        if negative_density >= 0.28:
            role = "waypoint"
            candidate_pool_behavior = "bridge"
            reason = "Love occurs in a mixed/negative neighborhood; treat as bridge or one-object exception, not automatic Landmark."
        elif positive_density >= 0.55 or recurrence_scope_count >= 2:
            role = "landmark"
            candidate_pool_behavior = "anchor"
            reason = "Love is supported by dense positive neighborhood or recurrence across object scopes."
        else:
            role = "frontier"
            candidate_pool_behavior = "probe"
            reason = "Love is relatively isolated or underexplored; treat as high-value Frontier opportunity."
    elif reaction == "like":
        if negative_density >= 0.32:
            role = "waypoint"
            candidate_pool_behavior = "bridge"
            reason = "Like sits near meaningful negative evidence; use as scoped bridge rather than broad Frontier."
        elif positive_density >= 0.5 or music_ref["object_type"] == "album":
            role = "waypoint"
            candidate_pool_behavior = "bridge"
            reason = "Like is supported by adjacent positive evidence or album-level scope; use as route-building Waypoint."
        else:
            role = "frontier"
            candidate_pool_behavior = "probe"
            reason = "Like has limited local support; use as Frontier probe."
    elif reaction == "ok":
        if unknown_density >= 0.35 and positive_density < 0.35:
            role = "unknown"
            candidate_pool_behavior = "probe"
            reason = "Ok response is surrounded by unknown territory; preserve as uncertainty."
        else:
            role = "waypoint"
            candidate_pool_behavior = "waypoint"
            reason = "Ok response is weak positive/familiarity evidence; use as low-confidence Waypoint only."
    elif reaction == "dont_like":
        if positive_density >= 0.35:
            role = "unknown"
            candidate_pool_behavior = "risky_probe"
            reason = "Negative response conflicts with nearby positive evidence; create contradiction/dead-end-check candidate instead of broad Dead End."
        else:
            role = "dead_end"
            candidate_pool_behavior = "trap"
            reason = "Negative response has limited positive counterweight; keep as scoped Dead End hypothesis."
    elif reaction == "dont_know_enough":
        role = "unknown"
        candidate_pool_behavior = "probe"
        reason = "Insufficient familiarity remains unknown/underexplored evidence, not negative taste."

    if "version_specificity" in page_intent and music_ref["object_type"] == "song_recording" and role == "landmark":
        role = "waypoint"
        candidate_pool_behavior = "bridge"
        reason = "Song/version-specific page intent limits a loved recording to Waypoint until recurrence confirms a broader anchor."

    return {
        "role": role,
        "candidate_pool_behavior": candidate_pool_behavior,
        "fallback_role": fallback_role,
        "reason": reason,
        "inputs": density_context,
        "policy_notes": [
            "This is provisional v0.1.1 policy, not final product behavior.",
            "like_to_frontier remains fallback only and is not a final product rule.",
            "Future policy should jointly consider page intent, object scope, recurrence, Apple exposure, graph context, and comparison set.",
        ],
    }


def hidden_private_field_check(packet: dict[str, Any], packet_path: Path) -> dict[str, Any]:
    key_hits = sorted(FORBIDDEN_PRIVATE_KEYS.intersection(iter_keys(packet)))
    text = packet_path.read_text(encoding="utf-8")
    phrase_hits = sorted({phrase for phrase in FORBIDDEN_PRIVATE_PHRASES if phrase in text})
    blindness = packet.get("blindness_contract") or {}
    blindness_failures = []
    if blindness.get("public_packet_contains_hidden_truth") is not False:
        blindness_failures.append("public_packet_contains_hidden_truth_not_false")
    if blindness.get("hidden_inputs_used_for_generation") is not False:
        blindness_failures.append("hidden_inputs_used_for_generation_not_false")
    return {
        "passed": not key_hits and not phrase_hits and not blindness_failures,
        "forbidden_key_hits": key_hits,
        "forbidden_phrase_hits": phrase_hits,
        "blindness_contract_failures": blindness_failures,
        "blindness_contract": blindness,
    }


def normalize_music_ref(raw_ref: dict[str, Any], graph_context: dict[str, Any]) -> dict[str, Any]:
    object_type = raw_ref.get("object_type") or "artist"
    if object_type == "song":
        object_type = "song_recording"
    ref_source = raw_ref.get("ref_source") or "unresolved"
    resolution_state = raw_ref.get("resolution_state")
    if ref_source == "unresolved":
        resolution_state = "needs_resolution"
    elif not resolution_state:
        resolution_state = "resolved"

    display_name = raw_ref.get("display_name") or raw_ref.get("title") or "Unresolved survey object"
    credited_artist = raw_ref.get("credited_artist_name") or raw_ref.get("artist_display_name")
    if object_type == "artist" and not credited_artist:
        credited_artist = display_name

    if object_type == "composition_placeholder":
        composition_policy_status = "composition_first_required"
    elif object_type == "song_recording":
        composition_policy_status = raw_ref.get("composition_policy_status") or "no_review_needed"
    else:
        composition_policy_status = raw_ref.get("composition_policy_status") or "not_applicable"

    external_refs = raw_ref.get("external_catalog_refs") or {}
    normalized = {
        "object_type": object_type,
        "ref_source": ref_source,
        "canonical_artist_id": raw_ref.get("canonical_artist_id"),
        "canonical_album_id": raw_ref.get("canonical_album_id"),
        "canonical_song_recording_id": raw_ref.get("canonical_song_recording_id"),
        "composition_placeholder_id": raw_ref.get("composition_placeholder_id"),
        "user_music_object_id": raw_ref.get("user_music_object_id"),
        "external_catalog_refs": external_refs,
        "display_name": display_name,
        "credited_artist_name": credited_artist,
        "credit_context": raw_ref.get("credit_context") or "unknown",
        "resolution_state": resolution_state,
        "composition_policy_status": composition_policy_status,
        "recording_variant_type": raw_ref.get("recording_variant_type") or ("unknown" if object_type == "song_recording" else None),
        "canonical_membership_context": {
            "family_numbers": graph_context.get("family_numbers") or [],
            "archetype_ids": graph_context.get("archetype_ids") or [],
            "membership_role_notes": "Survey graph roles are canonical membership context only, not Atlas role truth.",
        },
    }

    if ref_source == "canonical_graph":
        if object_type == "artist" and not normalized["canonical_artist_id"]:
            normalized["ref_source"] = "unresolved"
            normalized["resolution_state"] = "needs_resolution"
        if object_type == "album" and not normalized["canonical_album_id"]:
            normalized["ref_source"] = "unresolved"
            normalized["resolution_state"] = "needs_resolution"
        if object_type == "song_recording" and not normalized["canonical_song_recording_id"]:
            normalized["ref_source"] = "unresolved"
            normalized["resolution_state"] = "needs_resolution"
    return normalized


def make_signal(
    *,
    signal_id: str,
    user_id: str,
    tile: dict[str, Any],
    page: dict[str, Any],
    packet: dict[str, Any],
    packet_path: Path,
    profile_id: str,
    visible_packet_id: str,
    music_ref: dict[str, Any],
    node_id: str,
    update_id: str,
    quarantined_refs: list[dict[str, Any]],
) -> dict[str, Any]:
    reaction = tile.get("reaction")
    signal_strength, interpretation_confidence, basis, summary = signal_confidence(reaction)
    occurred_at = packet.get("created_at") or GENERATED_AT
    valid_refs = [
        ref
        for ref in (tile.get("response_evidence_refs") or [])
        if not any(issue.get("ref") == ref for issue in quarantined_refs)
    ]
    return {
        "record_type": "signal",
        "schema_version": SCHEMA_VERSION,
        "signal_id": signal_id,
        "user_id": user_id,
        "source": "survey",
        "event_type": event_type_for_reaction(reaction),
        "occurred_at": occurred_at,
        "captured_at": occurred_at,
        "subject_music_object_ref": music_ref,
        "subject_atlas_node_id": node_id,
        "reaction_value": schema_reaction_value(reaction),
        "raw_reaction": reaction,
        "normalized_signal": normalized_signal(reaction, tile.get("atlas_signal_interpretation")),
        "observed_user_tags": tile.get("observed_selected_tags") or [],
        "shown_unselected_tags": tile.get("shown_unselected_tags") or [],
        "user_note": tile.get("free_text_note") or tile.get("note") or tile.get("user_note"),
        "source_context": {
            "source_session_id": packet.get("run_id"),
            "source_payload_ref": visible_packet_id,
            "source_file_ref": rel(packet_path),
            "source_item_id": tile.get("evidence_ref"),
            "survey_item_id": tile.get("response_id"),
            "response_id": tile.get("response_id"),
            "visible_packet_id": visible_packet_id,
            "simulation_profile_id": profile_id,
            "payload_version": packet.get("schema_version"),
            "input_fingerprint": packet.get("input_fingerprint"),
            "valid_response_evidence_refs": valid_refs,
            "quarantined_response_evidence_refs": quarantined_refs,
        },
        "page_context": {
            "survey_session_id": packet.get("run_id"),
            "page_id": page.get("page_id"),
            "stage": page.get("stage"),
            "page_number": page.get("page_number"),
            "page_mode": page.get("page_mode"),
            "page_intent": tile.get("page_intent"),
            "comparison_set_id": tile.get("comparison_set_id"),
            "tile_id": tile.get("tile_id"),
            "position": tile.get("position"),
            "candidate_basis": tile.get("candidate_basis") or [],
            "graph_context": tile.get("graph_context") or {},
            "best_recognition_tier": (tile.get("graph_context") or {}).get("best_recognition_tier"),
            "best_survey_tier": (tile.get("graph_context") or {}).get("best_survey_tier"),
        },
        "apple_exposure_context": {
            "context_type": "exposure_import_familiarity_not_taste_truth",
            "apple_payload_id": packet.get("apple_payload_id"),
            "apple_evidence_summary": tile.get("apple_evidence_summary") or {},
            "apple_evidence_refs": (tile.get("apple_evidence_summary") or {}).get("signal_ids") or [],
        },
        "integrity_state": "needs_review" if quarantined_refs else "valid",
        "debug_provenance": {
            "non_user_facing": True,
            "scores_retained_for_qa_only": tile.get("scores") or {},
            "suppression_warnings": tile.get("suppression_warnings") or [],
            "page_generator_visible_inputs_summary": page.get("generator_visible_inputs") or {},
        },
        "signal_strength": signal_strength,
        "interpretation_confidence": interpretation_confidence,
        "confidence": confidence(interpretation_confidence, basis, summary),
        "derived_update_candidate_ids": [update_id],
        "lifecycle": lifecycle("active", "needs_review" if quarantined_refs else "unreviewed", "proposed"),
    }


def make_atlas_node(
    *,
    atlas_node_id: str,
    user_id: str,
    music_ref: dict[str, Any],
    signal_id: str,
    tile: dict[str, Any],
    packet_created_at: str,
) -> dict[str, Any]:
    return {
        "record_type": "atlas_node",
        "schema_version": SCHEMA_VERSION,
        "atlas_node_id": atlas_node_id,
        "user_id": user_id,
        "node_type": music_ref["object_type"],
        "display_name": music_ref["display_name"],
        "subtitle": f"Survey-visible {music_ref['object_type'].replace('_', ' ')}",
        "music_object_ref": music_ref,
        "origin": "survey",
        "render_hints": {
            "primary_label": music_ref["display_name"],
            "secondary_label": "Survey-seeded provisional object",
            "card_summary": "Created from visible Survey evidence so Atlas can reason about the object without storing role truth on the node.",
        },
        "lifecycle": lifecycle("provisional", "unreviewed", "candidate"),
        "confidence": confidence(0.35, "survey_pattern", "Placeholder confidence set during node aggregation."),
        "evidence_signal_ids": [signal_id],
        "created_at": packet_created_at,
        "updated_at": packet_created_at,
    }


def make_role_assignment(
    *,
    role_assignment_id: str,
    user_id: str,
    atlas_node_id: str,
    role: str,
    candidate_pool_behavior: str,
    signal_id: str,
    tile: dict[str, Any],
    role_policy: dict[str, Any],
) -> dict[str, Any]:
    _, interpretation_confidence, basis, _ = signal_confidence(tile.get("reaction"))
    review_state = "needs_review" if role in {"landmark", "dead_end", "waypoint"} else "unreviewed"
    return {
        "record_type": "atlas_role_assignment",
        "schema_version": SCHEMA_VERSION,
        "atlas_role_assignment_id": role_assignment_id,
        "user_id": user_id,
        "atlas_node_id": atlas_node_id,
        "role": role,
        "scope": {
            "scope_type": "global",
            "scope_id": None,
            "scope_label": None,
        },
        "candidate_pool_behavior": candidate_pool_behavior,
        "assignment_summary": role_assignment_summary(role, candidate_pool_behavior, tile.get("reaction"), role_policy),
        "lifecycle": lifecycle("provisional", review_state, "candidate"),
        "confidence": confidence(
            min(0.74, interpretation_confidence),
            basis,
            "Survey-created role assignment is provisional and cannot be treated as promoted Atlas truth.",
        ),
        "evidence_signal_ids": [signal_id],
        "created_at": GENERATED_AT,
        "updated_at": GENERATED_AT,
    }


def make_update_candidate(
    *,
    update_id: str,
    user_id: str,
    source_signal_ids: list[str],
    target_atlas_node_id: str | None,
    target_role_assignment_id: str | None,
    role: str,
    candidate_pool_behavior: str,
    tile: dict[str, Any],
    music_ref: dict[str, Any],
    role_policy: dict[str, Any],
) -> dict[str, Any]:
    review_required = role in {"landmark", "dead_end"} or tile.get("reaction") in {"ok", "dont_like"}
    required_count = 2 if role in {"landmark", "frontier", "dead_end", "waypoint"} else 1
    return {
        "record_type": "possible_atlas_update_candidate",
        "schema_version": SCHEMA_VERSION,
        "update_candidate_id": update_id,
        "user_id": user_id,
        "source": "survey",
        "source_signal_ids": source_signal_ids,
        "target_atlas_node_id": target_atlas_node_id,
        "target_role_assignment_id": target_role_assignment_id,
        "proposed_record_type": "atlas_role_assignment",
        "proposed_action": "create",
        "proposed_payload": {
            "atlas_node_id": target_atlas_node_id,
            "role": role,
            "scope": {
                "scope_type": "global",
                "scope_id": None,
                "scope_label": None,
            },
            "candidate_pool_behavior": candidate_pool_behavior,
            "role_policy_version": role_policy["inputs"]["policy_version"],
            "role_policy_reason": role_policy["reason"],
            "fallback_direct_reaction_role": role_policy["fallback_role"],
            "density_context": role_policy["inputs"],
            "role_policy_notes": role_policy["policy_notes"],
            "survey_seed_only": True,
            "source_response_id": tile.get("response_id"),
            "raw_reaction": tile.get("reaction"),
            "normalized_signal": normalized_signal(tile.get("reaction"), tile.get("atlas_signal_interpretation")),
            "scope_limit": scope_limit_for(music_ref, tile.get("reaction")),
            "apple_music_context_policy": "exposure_import_familiarity_not_taste_truth",
            "failure_or_edge_conditions": edge_conditions_for(tile.get("reaction"), music_ref),
        },
        "confidence_delta": confidence_delta(tile.get("reaction")),
        "recurrence_requirement": {
            "required_count": required_count,
            "min_distinct_sources": 1,
            "satisfied": False,
        },
        "review_requirement": {
            "required": review_required,
            "reviewer_type": "human" if review_required else "none",
            "reason": review_reason_for(role, tile.get("reaction")),
        },
        "canonical_graph_mutation_allowed": False,
        "generated_hypothesis_only": False,
        "lifecycle": lifecycle("provisional", "needs_review" if review_required else "unreviewed", "candidate"),
        "created_at": GENERATED_AT,
        "updated_at": GENERATED_AT,
    }


def build_contradiction_candidates(
    *,
    profile_id: str,
    user_id: str,
    signals: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_artist: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for signal in signals:
        ref = signal["subject_music_object_ref"]
        artist = ref.get("credited_artist_name") or ref.get("display_name")
        if artist:
            by_artist[artist].append(signal)

    candidates = []
    contradictions = []
    for artist, artist_signals in sorted(by_artist.items()):
        positives = [s for s in artist_signals if s.get("raw_reaction") in {"love", "like"}]
        negatives = [s for s in artist_signals if s.get("raw_reaction") == "dont_like"]
        if not positives or not negatives:
            continue
        source_ids = [s["signal_id"] for s in positives + negatives]
        contradiction = {
            "cluster_id": f"contradiction:{slug(profile_id)}:{slug(artist)}",
            "label": artist,
            "positive_signal_ids": [s["signal_id"] for s in positives],
            "negative_signal_ids": [s["signal_id"] for s in negatives],
            "scope_warning": "Mixed artist/object evidence. Do not broaden the negative signal into a genre-level rejection.",
        }
        contradictions.append(contradiction)
        candidates.append(
            {
                "record_type": "possible_atlas_update_candidate",
                "schema_version": SCHEMA_VERSION,
                "update_candidate_id": f"update_candidate:survey:{slug(profile_id)}:contradiction:{slug(artist)}",
                "user_id": user_id,
                "source": "survey",
                "source_signal_ids": source_ids,
                "target_atlas_node_id": None,
                "target_role_assignment_id": None,
                "proposed_record_type": "atlas_role_assignment",
                "proposed_action": "resolution_request",
                "proposed_payload": {
                    "candidate_type": "contradiction_cluster",
                    "recommended_role": "unknown",
                    "candidate_pool_behavior": "risky_probe",
                    "cluster_label": artist,
                    "positive_signal_ids": contradiction["positive_signal_ids"],
                    "negative_signal_ids": contradiction["negative_signal_ids"],
                    "scope_limit": "object_or_recording_level_until_tested",
                    "failure_or_edge_conditions": [
                        contradiction["scope_warning"],
                        "Needs a mission test before any broad role assignment.",
                    ],
                },
                "confidence_delta": 0.08,
                "recurrence_requirement": {
                    "required_count": 2,
                    "min_distinct_sources": 1,
                    "satisfied": True,
                },
                "review_requirement": {
                    "required": True,
                    "reviewer_type": "human",
                    "reason": "Contradictory visible survey evidence requires scoped review or mission testing.",
                },
                "canonical_graph_mutation_allowed": False,
                "generated_hypothesis_only": False,
                "lifecycle": lifecycle("provisional", "needs_review", "candidate"),
                "created_at": GENERATED_AT,
                "updated_at": GENERATED_AT,
            }
        )
    return candidates, contradictions


def build_digest_view(
    *,
    profile_id: str,
    user_id: str,
    signals: list[dict[str, Any]],
    nodes: list[dict[str, Any]],
    role_assignments: list[dict[str, Any]],
    update_candidates: list[dict[str, Any]],
    contradictions: list[dict[str, Any]],
    packet: dict[str, Any],
    visible_packet_id: str,
) -> dict[str, Any]:
    nodes_by_id = {node["atlas_node_id"]: node for node in nodes}
    role_ids = {key: [] for key in ["landmarks", "regions", "frontiers", "dead_ends", "waypoints"]}
    candidate_buckets = {
        "candidate_landmarks": [],
        "candidate_regions": [],
        "candidate_frontiers": [],
        "candidate_dead_end_hypotheses": [],
        "candidate_waypoints": [],
    }
    for role in top_role_assignments(role_assignments, limit_per_role=8):
        key = ROLE_TO_DIGEST_KEY.get(role["role"])
        if key:
            role_ids[key].append(role["atlas_role_assignment_id"])
        node = nodes_by_id.get(role["atlas_node_id"])
        summary = digest_role_summary(role, node)
        if role["role"] == "landmark":
            candidate_buckets["candidate_landmarks"].append(summary)
        elif role["role"] == "region":
            candidate_buckets["candidate_regions"].append(summary)
        elif role["role"] == "frontier":
            candidate_buckets["candidate_frontiers"].append(summary)
        elif role["role"] == "dead_end":
            candidate_buckets["candidate_dead_end_hypotheses"].append(summary)
        elif role["role"] == "waypoint":
            candidate_buckets["candidate_waypoints"].append(summary)

    suggested_roles = []
    for role in top_role_assignments(role_assignments, limit_per_role=6):
        node = nodes_by_id.get(role["atlas_node_id"])
        if not node or role["role"] == "signal_only":
            continue
        suggested_roles.append(
            {
                "music_object_ref": node["music_object_ref"],
                "suggested_role": role["role"],
                "candidate_pool_behavior": role["candidate_pool_behavior"],
                "confidence": role["confidence"],
                "source_signal_ids": role["evidence_signal_ids"],
                "review_required": role["lifecycle"]["review_state"] == "needs_review",
                "reason": role["assignment_summary"],
            }
        )

    recent_signals = signals[-12:]
    unresolved_questions = []
    if contradictions:
        unresolved_questions.append("Mixed positive and negative evidence needs scoped mission testing.")
    if packet.get("canonical_graph_dictionary", {}).get("dictionary_available") is False:
        unresolved_questions.append("Canonical family/archetype dictionary unavailable; do not infer family or archetype names.")
    unknown_count = sum(1 for signal in signals if signal.get("raw_reaction") == "dont_know_enough")
    if unknown_count:
        unresolved_questions.append(f"{unknown_count} visible responses indicate insufficient familiarity, not negative taste.")

    recent_signal_summaries = [compact_signal(signal) for signal in recent_signals]
    digest = {
        "record_type": "atlas_digest_view",
        "schema_version": SCHEMA_VERSION,
        "digest_id": f"atlas_digest_view:survey:{slug(profile_id)}:A3",
        "user_id": user_id,
        "generated_at": GENERATED_AT,
        "mission_context": "wwtsf_and_first_mission_generation_from_survey_ingestion",
        "relevant_role_assignment_ids": role_ids,
        "user_taste_feature_state_ids": [],
        "user_vocabulary_term_ids": [],
        "user_taste_feature_states": [],
        "user_vocabulary_terms": [],
        "anti_overfitting_rules": [
            "Do not treat Survey-created roles as promoted Atlas truth.",
            "Do not broaden negative responses into genre-level dislikes without scoped recurrence.",
            "Treat dont_know_enough as familiarity uncertainty, not negative evidence.",
            "Apple Music evidence is exposure/import/familiarity context, not taste truth.",
            "Do not infer family or archetype names when canonical_graph_dictionary.dictionary_available=false.",
        ],
        "recent_signal_ids": [signal["signal_id"] for signal in recent_signals],
        "unresolved_questions": unresolved_questions,
        "mission_relevant_constraints": [
            "Use AtlasRoleAssignment and this digest, not AtlasNode role-like summaries.",
            "Generated mission hypotheses must return PossibleAtlasUpdateCandidate records only.",
            "No canonical graph mutation path is available from this digest.",
        ],
        "suggested_candidate_roles": suggested_roles,
        "recent_signals": recent_signal_summaries,
        "signal_summaries": recent_signal_summaries,
        "candidate_pool_behavior_hints": candidate_pool_hints(role_assignments, nodes_by_id),
        "contradictions": contradictions,
        "user_taste_feature_summaries": [],
        "starter_atlas_state": {
            "node_count": len(nodes),
            "signal_count": len(signals),
            "role_assignment_count": len(role_assignments),
            "possible_update_candidate_count": len(update_candidates),
            "candidate_role_assignment_ids": role_ids,
            "source_of_role_truth": "AtlasRoleAssignment only; AtlasNode has no authoritative role truth.",
        },
        "mission_generation_inputs": {
            "first_batch_source": "candidate landmarks, frontiers, dead-end hypotheses, waypoints, contradictions, and unresolved questions in this digest",
            "second_batch_source": "post-review Signals and PossibleAtlasUpdateCandidate outcomes should update AtlasDigestView before the second batch",
            "mission_objects_created_here": False,
            "candidate_pool_boundary": "Candidate Pool Builder may consume role assignments and digest hints, but role semantics remain outside AtlasNode.",
        },
        "wwtsf_inputs": {
            "source": "AtlasDigestView plus evidence Signal summaries",
            "final_copy_generated_here": False,
            "copy_policy": "Use bullets and summaries as substrate, not final user-facing truth.",
        },
        "evidence_audit": {
            "all_signals_trace_to_user_visible_events": True,
            "source_event_types": sorted({signal["event_type"] for signal in signals}),
            "signal_id_count": len({signal["signal_id"] for signal in signals}),
            "recent_signal_ids": [signal["signal_id"] for signal in recent_signals],
            "raw_payload_required_for_audit": False,
        },
        "future_correction": {
            "correction_source_records": [
                "Signal",
                "AtlasRoleAssignment",
                "PossibleAtlasUpdateCandidate",
                "AtlasDigestView",
            ],
            "promotion_requires_separate_policy_or_review": True,
            "canonical_graph_mutation_allowed": False,
        },
        "debug_provenance": {
            "source": "survey_a3_ingestion_proof",
            "visible_packet_id": visible_packet_id,
            "profile_public_id": profile_id,
            "visible_signal_count": len(signals),
            "role_assignment_count": len(role_assignments),
            "possible_update_candidate_count": len(update_candidates),
            "not_user_facing": True,
        },
    }
    digest.update(candidate_buckets)
    return digest


def build_node_interpretation_input(
    *,
    profile_id: str,
    packet: dict[str, Any],
    digest: dict[str, Any],
    signals: list[dict[str, Any]],
    role_assignments: list[dict[str, Any]],
    update_candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": "waymark.node_interpretation_input.v0.1",
        "profile_public_id": profile_id,
        "created_at": GENERATED_AT,
        "instruction": "Do not generate a taste profile from raw survey payload. Interpret Atlas substrate records and return structured possible update recommendations only.",
        "atlas_digest_view": digest,
        "relevant_signal_summaries": [compact_signal(signal) for signal in signals],
        "provisional_atlas_role_assignments": [compact_role(role) for role in role_assignments],
        "possible_atlas_update_candidates": [compact_update(update) for update in update_candidates],
        "user_taste_feature_states": [],
        "user_vocabulary_terms": [],
        "anti_overfitting_rules": digest["anti_overfitting_rules"],
        "allowed_graph_metadata": packet.get("allowed_context", {}).get("canonical_graph_metadata_included", []),
        "visible_page_intent_summaries": page_intent_summaries(packet),
        "llm_output_policy": {
            "allowed": [
                "friendly region names",
                "scope warnings",
                "confidence explanations",
                "dead-end explanations",
                "frontier hypotheses",
                "mission hints",
                "WWTSF-ready bullets",
            ],
            "must_return_structured_records_only": True,
            "must_not_create_promoted_atlas_truth": True,
            "canonical_graph_mutation_allowed": False,
        },
        "excluded_context": [
            "full raw Survey payload",
            "hidden profile truth",
            "hidden corpus reactions",
            "simulator-private lookup status",
            "Profile Writer output",
            "canonical graph mutation instructions",
            "family/archetype names when dictionary_available=false",
        ],
    }


def build_slim_node_interpretation_input(
    *,
    profile_id: str,
    digest: dict[str, Any],
    signals: list[dict[str, Any]],
    nodes: list[dict[str, Any]],
    role_assignments: list[dict[str, Any]],
    update_candidates: list[dict[str, Any]],
    contradictions: list[dict[str, Any]],
) -> dict[str, Any]:
    nodes_by_id = {node["atlas_node_id"]: node for node in nodes}
    high_value_roles = []
    for role in top_role_assignments(role_assignments, limit_per_role=4):
        if role["role"] == "signal_only":
            continue
        node = nodes_by_id.get(role["atlas_node_id"])
        if not node:
            continue
        high_value_roles.append(
            {
                "atlas_role_assignment_id": role["atlas_role_assignment_id"],
                "node_name": node["display_name"],
                "music_object_ref": compact_music_ref(node["music_object_ref"]),
                "provisional_role": role["role"],
                "candidate_pool_behavior": role["candidate_pool_behavior"],
                "confidence": role["confidence"],
                "lifecycle": role["lifecycle"],
                "evidence_signal_ids": role["evidence_signal_ids"],
                "summary": role["assignment_summary"],
            }
        )

    top_evidence = sorted(
        signals,
        key=lambda signal: (
            signal["interpretation_confidence"],
            signal["signal_strength"],
            1 if signal.get("raw_reaction") in {"love", "dont_like"} else 0,
        ),
        reverse=True,
    )[:18]

    contradiction_updates = [
        compact_update(update)
        for update in update_candidates
        if (update.get("proposed_payload") or {}).get("candidate_type") == "contradiction_cluster"
    ]

    return {
        "schema_version": "waymark.node_interpretation_input.slim.v0.1.1",
        "profile_public_id": profile_id,
        "created_at": GENERATED_AT,
        "source_digest_id": digest["digest_id"],
        "purpose": "Structured node/update-candidate interpretation from Atlas substrate only. Do not use raw Survey payload or construction mechanics.",
        "atlas_digest_summary": {
            "digest_id": digest["digest_id"],
            "mission_context": digest["mission_context"],
            "unresolved_questions": digest["unresolved_questions"],
            "anti_overfitting_rules": digest["anti_overfitting_rules"],
            "mission_relevant_constraints": digest["mission_relevant_constraints"],
        },
        "high_value_candidate_role_summaries": high_value_roles,
        "contradiction_clusters": contradictions,
        "contradiction_update_summaries": contradiction_updates,
        "top_evidence_refs": [
            {
                "signal_id": signal["signal_id"],
                "response_id": signal["source_context"]["response_id"],
                "subject_display_name": signal["subject_music_object_ref"]["display_name"],
                "object_type": signal["subject_music_object_ref"]["object_type"],
                "raw_reaction": signal["raw_reaction"],
                "normalized_signal": signal["normalized_signal"],
                "signal_strength": signal["signal_strength"],
                "interpretation_confidence": signal["interpretation_confidence"],
                "selected_tags": signal["observed_user_tags"],
                "shown_unselected_tags": signal.get("shown_unselected_tags", []),
                "page_intent": signal["page_context"].get("page_intent"),
                "apple_context_policy": signal["apple_exposure_context"]["context_type"],
            }
            for signal in top_evidence
        ],
        "excluded_context": [
            "raw Survey payload",
            "debug_provenance",
            "construction scores",
            "generator_visible_inputs",
            "full possible update candidate dumps",
            "Profile Writer output",
            "hidden profile truth",
            "hidden corpus reactions",
            "simulator-private lookup status",
        ],
        "llm_output_policy": {
            "must_return_structured_records_only": True,
            "must_not_create_promoted_atlas_truth": True,
            "canonical_graph_mutation_allowed": False,
        },
    }


def build_validation_report(
    *,
    packet: dict[str, Any],
    packet_path: Path,
    profile_label: str,
    tiles: list[dict[str, Any]],
    invalid_refs: list[dict[str, Any]],
    quarantined_refs: dict[str, list[dict[str, Any]]],
    hidden_check: dict[str, Any],
    unresolved_refs: list[dict[str, Any]],
    empty_redundant_count: dict[str, int],
) -> dict[str, Any]:
    visible_page_counts = defaultdict(int)
    for page in packet.get("pages", []):
        visible_page_counts[page.get("stage") or "unknown"] += 1
    visible_response_counts = defaultdict(int)
    for tile in tiles:
        visible_response_counts[tile["_page"].get("stage") or "unknown"] += 1
    status = "pass"
    integrity_gate_status = "pass"
    if invalid_refs:
        integrity_gate_status = "pass_with_quarantined_refs"
    if not hidden_check["passed"]:
        status = "fail"
        integrity_gate_status = "fail"
    return {
        "schema_version": "waymark.atlas_a3_ingestion_validation_report.v0.1",
        "profile_label": profile_label,
        "input_file_name": packet_path.name,
        "input_file_ref": rel(packet_path),
        "payload_version": packet.get("schema_version"),
        "visible_page_counts": dict(sorted(visible_page_counts.items())),
        "visible_response_counts": dict(sorted(visible_response_counts.items())),
        "invalid_response_evidence_refs": invalid_refs,
        "quarantined_refs": quarantined_refs,
        "hidden_private_field_check": hidden_check,
        "unresolved_object_refs": unresolved_refs,
        "empty_redundant_field_count": empty_redundant_count,
        "apple_music_evidence_policy": {
            "status": "pass",
            "handling": "retained as apple_exposure_context only; not used as taste truth or role promotion truth",
        },
        "page_construction_metadata_policy": {
            "status": "pass",
            "handling": "scores and generator_visible_inputs retained only under debug_provenance, not render copy",
        },
        "integrity_gate_status": integrity_gate_status,
        "status": status,
    }


def write_profile_outputs(
    *,
    profile_label: str,
    packet_path: Path,
    validation_report: dict[str, Any],
    signals: list[dict[str, Any]],
    nodes: list[dict[str, Any]],
    role_assignments: list[dict[str, Any]],
    update_candidates: list[dict[str, Any]],
    digest: dict[str, Any],
    node_interpretation_input: dict[str, Any],
    slim_node_interpretation_input: dict[str, Any],
) -> dict[str, Path]:
    signal_path = OUTPUT_DIR / f"signals_{profile_label}.jsonl"
    write_jsonl(signal_path, signals)
    nodes_path = OUTPUT_DIR / f"atlas_nodes_{profile_label}.json"
    roles_path = OUTPUT_DIR / f"atlas_role_assignments_{profile_label}.json"
    updates_path = OUTPUT_DIR / f"possible_atlas_update_candidates_{profile_label}.json"
    digest_path = OUTPUT_DIR / f"atlas_digest_view_{profile_label}.json"
    interpretation_path = OUTPUT_DIR / f"node_interpretation_input_{profile_label}.json"
    slim_interpretation_path = OUTPUT_DIR / f"slim_node_interpretation_input_{profile_label}.json"
    bundle_path = OUTPUT_DIR / f"atlas_records_bundle_{profile_label}.json"
    write_json(nodes_path, nodes)
    write_json(roles_path, role_assignments)
    write_json(updates_path, update_candidates)
    write_json(digest_path, digest)
    write_json(interpretation_path, node_interpretation_input)
    write_json(slim_interpretation_path, slim_node_interpretation_input)
    write_json(
        bundle_path,
        {
            "record_type": "atlas_example_bundle",
            "schema_version": SCHEMA_VERSION,
            "example_name": f"a3_ingestion_{profile_label}",
            "description": "Schema-validation bundle for generated A3 survey ingestion Atlas records.",
            "records": signals + nodes + role_assignments + update_candidates + [digest],
        },
    )
    return {
        "signals": signal_path,
        "nodes": nodes_path,
        "roles": roles_path,
        "updates": updates_path,
        "digest": digest_path,
        "interpretation": interpretation_path,
        "slim_interpretation": slim_interpretation_path,
        "schema_bundle": bundle_path,
    }


def write_contract_profile_outputs(
    *,
    profile_label: str,
    profile_id: str,
    packet_path: Path,
    validation_report: dict[str, Any],
    signals: list[dict[str, Any]],
    nodes: list[dict[str, Any]],
    role_assignments: list[dict[str, Any]],
    update_candidates: list[dict[str, Any]],
    digest: dict[str, Any],
    size_report: dict[str, Any],
) -> dict[str, Path]:
    profile_dir = CONTRACT_OUTPUT_DIR / profile_label
    profile_dir.mkdir(parents=True, exist_ok=True)
    consumer_digest = dict(digest)
    consumer_digest.pop("debug_provenance", None)
    consumer_digest["consumer_contract"] = {
        "intended_consumers": [
            "WWTSF",
            "Mission Generation",
            "Candidate Pool Builder",
            "node interpretation",
            "evidence audit",
            "future correction",
        ],
        "raw_survey_payload_required": False,
        "canonical_graph_mutation_allowed": False,
        "survey_role_promotion_allowed": False,
    }
    write_json(profile_dir / "validation_report.json", validation_report)
    write_jsonl(profile_dir / "signals.jsonl", signals)
    write_json(profile_dir / "atlas_nodes.json", nodes)
    write_json(profile_dir / "atlas_role_assignments.json", role_assignments)
    write_json(profile_dir / "possible_atlas_update_candidates.json", update_candidates)
    write_json(profile_dir / "atlas_digest_view.json", consumer_digest)
    write_text(profile_dir / "size_report.md", render_contract_size_report(profile_id, profile_label, packet_path, size_report, profile_dir))
    return {
        "profile_dir": profile_dir,
        "validation_report": profile_dir / "validation_report.json",
        "signals": profile_dir / "signals.jsonl",
        "nodes": profile_dir / "atlas_nodes.json",
        "roles": profile_dir / "atlas_role_assignments.json",
        "updates": profile_dir / "possible_atlas_update_candidates.json",
        "digest": profile_dir / "atlas_digest_view.json",
        "size_report": profile_dir / "size_report.md",
    }


def render_contract_size_report(
    profile_id: str,
    profile_label: str,
    packet_path: Path,
    report: dict[str, Any],
    profile_dir: Path,
) -> str:
    digest = report["atlas_digest_view"]
    signals = report["normalized_signal_ledger"]
    candidates = report["candidate_bundle"]
    prior = report["prior_profile_writer_input"]
    lines = [
        f"# Size Report: {profile_label}",
        "",
        "## Scope",
        "",
        f"- Profile: `{profile_id}`",
        f"- Source Survey Evidence Export: `{rel(packet_path)}`",
        f"- Contract output directory: `{rel(profile_dir)}`",
        "",
        "## Sizes",
        "",
        f"- Raw Survey Evidence Export: `{report['raw_a3_survey_payload']['bytes']}` bytes",
        f"- Signals JSONL: `{signals['bytes']}` bytes; ratio vs raw `{signals['size_vs_raw_ratio']}`",
        f"- PossibleAtlasUpdateCandidate bundle: `{candidates['bytes']}` bytes; ratio vs raw `{candidates['size_vs_raw_ratio']}`",
        f"- AtlasDigestView: `{digest['bytes']}` bytes; ratio vs raw `{digest['size_vs_raw_ratio']}`",
        f"- Raw-to-digest reduction: `{digest['raw_to_digest_reduction_percent']}`%",
        "",
        "## Acceptance Notes",
        "",
        "- Digest contains candidate role summaries, recent Signal summaries, contradictions, unresolved questions, anti-overfitting rules, mission constraints, candidate-pool behavior hints, and correction/audit metadata.",
        "- Digest is sufficient substrate for starter Atlas state, WWTSF, first and second mission-batch planning, evidence audit, and future correction without returning to the full raw Survey payload.",
        "- Survey-created role assignments remain provisional/candidate only.",
        "- AtlasNode remains role-free; user-specific role truth lives in AtlasRoleAssignment.",
    ]
    if prior["bytes"] is not None:
        lines.append(f"- Prior Profile Writer input: `{prior['bytes']}` bytes")
        lines.append(f"- Digest/Profile Writer input ratio: `{prior['digest_vs_profile_writer_input_ratio']}`")
    return "\n".join(lines) + "\n"


def build_size_report(profile_id: str, profile_label: str, packet_path: Path, output_paths: dict[str, Path]) -> dict[str, Any]:
    writer_request = PROFILE_WRITER_REQUEST_DIR / f"profile_writer_request_{profile_id}_A3_Al1_S2.json"
    raw_size = packet_path.stat().st_size
    digest_size = output_paths["digest"].stat().st_size
    candidate_bundle_size = output_paths["updates"].stat().st_size
    signal_size = output_paths["signals"].stat().st_size
    current_interpretation_size = output_paths["interpretation"].stat().st_size
    slim_interpretation_size = output_paths["slim_interpretation"].stat().st_size
    writer_size = writer_request.stat().st_size if writer_request.exists() else None
    return {
        "schema_version": "waymark.atlas_a3_ingestion_size_report.v0.1",
        "profile_label": profile_label,
        "profile_public_id": profile_id,
        "raw_a3_survey_payload": {
            "path": rel(packet_path),
            "bytes": raw_size,
        },
        "normalized_signal_ledger": {
            "path": rel(output_paths["signals"]),
            "bytes": signal_size,
            "size_vs_raw_ratio": ratio(signal_size, raw_size),
        },
        "candidate_bundle": {
            "path": rel(output_paths["updates"]),
            "bytes": candidate_bundle_size,
            "size_vs_raw_ratio": ratio(candidate_bundle_size, raw_size),
        },
        "atlas_digest_view": {
            "path": rel(output_paths["digest"]),
            "bytes": digest_size,
            "size_vs_raw_ratio": ratio(digest_size, raw_size),
            "raw_to_digest_reduction_percent": round((1 - (digest_size / raw_size)) * 100, 2) if raw_size else None,
        },
        "current_node_interpretation_input": {
            "path": rel(output_paths["interpretation"]),
            "bytes": current_interpretation_size,
            "size_vs_raw_ratio": ratio(current_interpretation_size, raw_size),
        },
        "slim_node_interpretation_input": {
            "path": rel(output_paths["slim_interpretation"]),
            "bytes": slim_interpretation_size,
            "size_vs_raw_ratio": ratio(slim_interpretation_size, raw_size),
            "raw_to_slim_reduction_percent": round((1 - (slim_interpretation_size / raw_size)) * 100, 2) if raw_size else None,
            "slim_vs_current_node_interpretation_ratio": ratio(slim_interpretation_size, current_interpretation_size),
            "current_to_slim_reduction_percent": round((1 - (slim_interpretation_size / current_interpretation_size)) * 100, 2)
            if current_interpretation_size
            else None,
        },
        "prior_profile_writer_input": {
            "path": rel(writer_request) if writer_request.exists() else None,
            "bytes": writer_size,
            "digest_vs_profile_writer_input_ratio": ratio(digest_size, writer_size) if writer_size else None,
        },
    }


def write_markdown_summary(aggregate: list[dict[str, Any]]) -> None:
    lines = [
        "# A3 Survey to Atlas Ingestion Proof",
        "",
        "Generated: 2026-05-20",
        "",
        f"Ingestion version: `{INGESTION_VERSION}`",
        "",
        "## Scope",
        "",
        "Input packets: GPT-5.5 3x3 A3 public survey packets for public profiles 01, 05, and 06.",
        "",
        "The pipeline is deterministic and does not read hidden truth packets or Profile Writer output as evidence.",
        "",
        "## Profile Outputs",
        "",
        "| profile | status | signals | nodes | role assignments | update candidates | digest | slim interpretation |",
        "|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in aggregate:
        lines.append(
            f"| {row['profile_public_id']} | {row['status']} | {row['signals']} | {row['atlas_nodes']} | "
            f"{row['atlas_role_assignments']} | {row['possible_atlas_update_candidates']} | `{row['digest_view']}` | "
            f"`{row['slim_node_interpretation_input']}` |"
        )
    lines.extend(
        [
            "",
            "## Boundary Checks",
            "",
            "- AtlasNode records contain no authoritative role truth.",
            "- Survey-created role assignments use provisional/candidate lifecycle only.",
            "- PossibleAtlasUpdateCandidate records pin `canonical_graph_mutation_allowed=false`.",
            "- Apple Music evidence is retained only as exposure/import/familiarity context.",
            "- `dont_know_enough` responses are preserved as unknown/familiarity signals, not negative evidence.",
            "- Negative responses create scoped dead-end hypotheses, not blanket genre rejections.",
            "- v0.1.1 role assignment is density-aware; direct reaction mapping is fallback only.",
            "- Slim node-interpretation packets exclude debug provenance, construction scores, generator-visible inputs, and full candidate dumps.",
        ]
    )
    (OUTPUT_DIR / "a3_ingestion_proof_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_contract_manifest(aggregate: list[dict[str, Any]]) -> None:
    manifest = {
        "schema_version": "waymark.survey_to_atlas_digest_ingestion_proof_manifest.v0.1",
        "atlas_schema_contract_version": SCHEMA_VERSION,
        "ingestion_version": INGESTION_VERSION,
        "generated_at": GENERATED_AT,
        "source": "Survey Evidence Export",
        "source_input_dir": rel(INPUT_DIR),
        "output_dir": rel(CONTRACT_OUTPUT_DIR),
        "required_flow": [
            "Survey Evidence Export",
            "Signal",
            "AtlasNode if needed",
            "provisional AtlasRoleAssignment",
            "PossibleAtlasUpdateCandidate",
            "AtlasDigestView",
        ],
        "hard_rules": {
            "canonical_graph_mutation_allowed": False,
            "promoted_roles_from_survey_alone_allowed": False,
            "role_truth_on_atlas_node_allowed": False,
            "road_is_role": False,
            "lineage_is_role": False,
            "lifecycle_fields_separate": True,
            "signal_strength_and_interpretation_confidence_separate": True,
        },
        "profile_count": len(aggregate),
        "profiles": [
            {
                "profile_public_id": row["profile_public_id"],
                "profile_label": row["profile_label"],
                "profile_dir": row["contract_profile_dir"],
                "required_outputs": {
                    "validation_report": f"{row['contract_profile_dir']}/validation_report.json",
                    "signals": f"{row['contract_profile_dir']}/signals.jsonl",
                    "atlas_nodes": f"{row['contract_profile_dir']}/atlas_nodes.json",
                    "atlas_role_assignments": f"{row['contract_profile_dir']}/atlas_role_assignments.json",
                    "possible_atlas_update_candidates": f"{row['contract_profile_dir']}/possible_atlas_update_candidates.json",
                    "atlas_digest_view": f"{row['contract_profile_dir']}/atlas_digest_view.json",
                    "size_report": f"{row['contract_profile_dir']}/size_report.md",
                },
                "status": row["status"],
            }
            for row in aggregate
        ],
    }
    write_json(CONTRACT_OUTPUT_DIR / "manifest.json", manifest)
    lines = [
        "# Survey to AtlasDigestView Ingestion Proof v0.1",
        "",
        f"Generated: {GENERATED_AT}",
        "",
        "## Flow",
        "",
        "`Survey Evidence Export -> Signal -> AtlasNode if needed -> provisional AtlasRoleAssignment -> PossibleAtlasUpdateCandidate -> AtlasDigestView`",
        "",
        "## Contract Boundaries",
        "",
        "- Canonical graph is read/reference-only.",
        "- AtlasNode represents the thing and stores no authoritative role truth.",
        "- AtlasRoleAssignment carries user-specific role truth.",
        "- Survey writes Signals, provisional role assignments, and possible update candidates only.",
        "- AtlasDigestView is the downstream substrate for WWTSF, Mission Generation, Candidate Pool Builder, later node interpretation, evidence audit, and correction.",
        "",
        "## Profiles",
        "",
        "| profile | status | output directory |",
        "|---|---:|---|",
    ]
    for row in aggregate:
        lines.append(f"| {row['profile_public_id']} | {row['status']} | `{row['contract_profile_dir']}` |")
    write_text(CONTRACT_OUTPUT_DIR / "README.md", "\n".join(lines) + "\n")


def write_role_assignment_policy_doc() -> None:
    path = OUTPUT_DIR / "role_assignment_policy_v0_1_1.md"
    lines = [
        "# Provisional Atlas Role Assignment Policy v0.1.1",
        "",
        "Generated: 2026-05-20",
        "",
        "## Status",
        "",
        "This is a provisional density-aware repair for the A3 ingestion proof. It is not a final product policy.",
        "",
        "The previous direct reaction mapping remains as fallback only. In particular, `like -> frontier` is not a final product rule.",
        "",
        "## Inputs",
        "",
        "The v0.1.1 policy considers:",
        "",
        "- reaction strength",
        "- object scope: artist, album, song_recording, composition_placeholder",
        "- local positive density",
        "- local negative density",
        "- unknown or underexplored density",
        "- graph family and archetype adjacency",
        "- recurrence across artist, album, and song levels",
        "- Apple exposure and familiarity context",
        "- page intent",
        "- contradiction patterns",
        "",
        "Apple Music context is exposure/import/familiarity evidence only. It must not independently promote Atlas truth.",
        "",
        "## Provisional Behavior",
        "",
        "- A `love` response can become a candidate Landmark only when supported by dense positive neighborhood evidence or recurrence across object scopes.",
        "- An isolated `love` usually becomes a high-value Frontier opportunity.",
        "- A `love` in a mixed or negative neighborhood becomes a Waypoint/bridge or one-object exception candidate.",
        "- A `like` response becomes a Waypoint when supported by adjacent positive evidence or album-level scope; otherwise it may remain a Frontier probe.",
        "- An `ok` response is weak positive/familiarity evidence and usually remains a low-confidence Waypoint or Unknown.",
        "- A `dont_like` response becomes a scoped Dead End hypothesis only when local positive counterevidence is limited.",
        "- A `dont_like` response near meaningful positive evidence becomes Unknown/risky_probe plus a contradiction/dead-end-check candidate.",
        "- A `dont_know_enough` response is Unknown/familiarity evidence, not negative taste.",
        "",
        "## Output Contract",
        "",
        "The policy produces provisional `AtlasRoleAssignment` and `PossibleAtlasUpdateCandidate` records only.",
        "",
        "It must not produce promoted Atlas truth and must not mutate canonical graph entities.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_tag_bearing_fixture() -> None:
    fixture = {
        "record_type": "atlas_example_bundle",
        "schema_version": SCHEMA_VERSION,
        "example_name": "tag_bearing_survey_signal_v0_1_1",
        "description": "Non-empty selected and shown-unselected tag sample for Survey Signal ingestion.",
        "records": [
            {
                "record_type": "signal",
                "schema_version": SCHEMA_VERSION,
                "signal_id": "signal:survey:tag_fixture:artist_001",
                "user_id": "fixture_tag_bearing_profile",
                "source": "survey",
                "event_type": "reaction",
                "occurred_at": GENERATED_AT,
                "captured_at": GENERATED_AT,
                "subject_music_object_ref": {
                    "object_type": "artist",
                    "ref_source": "canonical_graph",
                    "canonical_artist_id": "nirvana",
                    "canonical_album_id": None,
                    "canonical_song_recording_id": None,
                    "composition_placeholder_id": None,
                    "user_music_object_id": None,
                    "external_catalog_refs": {},
                    "display_name": "Nirvana",
                    "credited_artist_name": "Nirvana",
                    "credit_context": "group",
                    "resolution_state": "resolved",
                    "composition_policy_status": "not_applicable",
                    "recording_variant_type": None,
                },
                "subject_atlas_node_id": "atlas_node:survey:tag_fixture:artist:nirvana",
                "reaction_value": "like",
                "raw_reaction": "like",
                "normalized_signal": "positive",
                "observed_user_tags": ["has body", "sharp guitar"],
                "shown_unselected_tags": ["nostalgic", "too polished"],
                "user_note": "The weight works; the polish tag does not apply.",
                "source_context": {
                    "source_session_id": "tag_fixture_session",
                    "source_payload_ref": "tag_fixture_visible_packet",
                    "source_file_ref": "generated_fixture",
                    "survey_item_id": "tag_fixture_resp_001",
                    "response_id": "tag_fixture_resp_001",
                    "visible_packet_id": "tag_fixture_visible_packet",
                    "payload_version": "tag_fixture.v0.1.1",
                    "valid_response_evidence_refs": [],
                    "quarantined_response_evidence_refs": [],
                },
                "page_context": {
                    "page_id": "tag_fixture_page_001",
                    "stage": "artist",
                    "page_number": 1,
                    "page_intent": "tag_preservation_fixture",
                    "tile_id": "tile_001",
                    "position": 1,
                    "candidate_basis": ["fixture"],
                    "graph_context": {},
                },
                "apple_exposure_context": {
                    "context_type": "exposure_import_familiarity_not_taste_truth",
                    "apple_payload_id": None,
                    "apple_evidence_summary": {},
                    "apple_evidence_refs": [],
                },
                "integrity_state": "valid",
                "signal_strength": 0.68,
                "interpretation_confidence": 0.58,
                "confidence": confidence(
                    0.58,
                    "direct_user_reaction",
                    "Selected tags are user-visible Signal evidence; shown-unselected tags are retained as weak non-selected context.",
                ),
                "derived_update_candidate_ids": [],
                "lifecycle": lifecycle("active", "unreviewed", "proposed"),
            }
        ],
    }
    write_json(OUTPUT_DIR / "tag_bearing_signal_sample_v0_1_1.json", fixture)
    write_json(
        OUTPUT_DIR / "tag_bearing_signal_validation_report_v0_1_1.json",
        {
            "schema_version": "waymark.tag_bearing_signal_validation_report.v0.1.1",
            "status": "pass",
            "selected_tags": {
                "field": "observed_user_tags",
                "expected_non_empty": True,
                "interpretation": "user-visible Signal evidence",
            },
            "shown_unselected_tags": {
                "field": "shown_unselected_tags",
                "expected_non_empty": True,
                "interpretation": "weak non-selected context; not positive evidence",
            },
            "fixture_ref": rel(OUTPUT_DIR / "tag_bearing_signal_sample_v0_1_1.json"),
        },
    )


def write_validation_report_md(profile_label: str, report: dict[str, Any]) -> None:
    lines = [
        f"# Validation Report {profile_label}",
        "",
        f"- Input file: `{report['input_file_ref']}`",
        f"- Payload version: `{report['payload_version']}`",
        f"- Status: `{report['status']}`",
        f"- Integrity gate status: `{report['integrity_gate_status']}`",
        f"- Visible page counts: `{json.dumps(report['visible_page_counts'], sort_keys=True)}`",
        f"- Visible response counts: `{json.dumps(report['visible_response_counts'], sort_keys=True)}`",
        f"- Invalid response evidence refs: `{len(report['invalid_response_evidence_refs'])}`",
        f"- Quarantined ref source responses: `{len(report['quarantined_refs'])}`",
        f"- Hidden/private field check: `{'pass' if report['hidden_private_field_check']['passed'] else 'fail'}`",
        f"- Unresolved object refs: `{len(report['unresolved_object_refs'])}`",
        f"- Empty/redundant field count: `{json.dumps(report['empty_redundant_field_count'], sort_keys=True)}`",
        "",
        "Apple Music evidence is preserved as exposure/import/familiarity context only.",
    ]
    (OUTPUT_DIR / f"validation_report_{profile_label}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_size_report_md(profile_label: str, report: dict[str, Any]) -> None:
    digest = report["atlas_digest_view"]
    slim = report["slim_node_interpretation_input"]
    lines = [
        f"# Size Report {profile_label}",
        "",
        f"- Raw A3 survey payload: `{report['raw_a3_survey_payload']['bytes']}` bytes",
        f"- Normalized Signal ledger: `{report['normalized_signal_ledger']['bytes']}` bytes",
        f"- Candidate bundle: `{report['candidate_bundle']['bytes']}` bytes",
        f"- AtlasDigestView: `{digest['bytes']}` bytes",
        f"- Raw to digest reduction: `{digest['raw_to_digest_reduction_percent']}`%",
        f"- Current node interpretation input: `{report['current_node_interpretation_input']['bytes']}` bytes",
        f"- Slim node interpretation input: `{slim['bytes']}` bytes",
        f"- Raw to slim reduction: `{slim['raw_to_slim_reduction_percent']}`%",
        f"- Current node interpretation to slim reduction: `{slim['current_to_slim_reduction_percent']}`%",
    ]
    prior = report["prior_profile_writer_input"]
    if prior["bytes"] is not None:
        lines.append(f"- Prior Profile Writer input: `{prior['bytes']}` bytes")
        lines.append(f"- Digest/Profile Writer input ratio: `{prior['digest_vs_profile_writer_input_ratio']}`")
    (OUTPUT_DIR / f"size_report_{profile_label}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def top_role_assignments(role_assignments: list[dict[str, Any]], limit_per_role: int) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for role in role_assignments:
        grouped[role["role"]].append(role)
    selected = []
    for role_name in ["landmark", "region", "frontier", "dead_end", "waypoint", "unknown", "signal_only"]:
        rows = sorted(
            grouped.get(role_name, []),
            key=lambda row: row["confidence"]["confidence_score"],
            reverse=True,
        )
        selected.extend(rows[:limit_per_role])
    return selected


def candidate_pool_hints(role_assignments: list[dict[str, Any]], nodes_by_id: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    hints = []
    for role in top_role_assignments(role_assignments, limit_per_role=5):
        node = nodes_by_id.get(role["atlas_node_id"])
        hints.append(
            {
                "name": node["display_name"] if node else role["atlas_node_id"],
                "role": role["role"],
                "candidate_pool_behavior": role["candidate_pool_behavior"],
                "confidence_band": role["confidence"]["confidence_band"],
                "review_state": role["lifecycle"]["review_state"],
                "promotion_state": role["lifecycle"]["promotion_state"],
                "music_object_ref": compact_music_ref(node["music_object_ref"]) if node else None,
                "evidence_signal_ids": role["evidence_signal_ids"],
            }
        )
    return hints


def digest_role_summary(role: dict[str, Any], node: dict[str, Any] | None) -> dict[str, Any]:
    lifecycle_state = role["lifecycle"]
    return {
        "atlas_role_assignment_id": role["atlas_role_assignment_id"],
        "atlas_node_id": role["atlas_node_id"],
        "name": node["display_name"] if node else role["atlas_node_id"],
        "music_object_ref": compact_music_ref(node["music_object_ref"]) if node else None,
        "role": role["role"],
        "candidate_pool_behavior": role["candidate_pool_behavior"],
        "status": lifecycle_state["status"],
        "review_state": lifecycle_state["review_state"],
        "promotion_state": lifecycle_state["promotion_state"],
        "confidence": role["confidence"],
        "evidence_signal_ids": role["evidence_signal_ids"],
        "summary": role["assignment_summary"],
        "survey_seed_only": True,
        "authoritative_role_truth_source": "atlas_role_assignment",
    }


def compact_signal(signal: dict[str, Any]) -> dict[str, Any]:
    ref = signal["subject_music_object_ref"]
    return {
        "signal_id": signal["signal_id"],
        "source": signal["source"],
        "event_type": signal["event_type"],
        "subject_display_name": ref["display_name"],
        "object_type": ref["object_type"],
        "raw_reaction": signal.get("raw_reaction"),
        "reaction_value": signal["reaction_value"],
        "normalized_signal": signal.get("normalized_signal"),
        "selected_tags": signal["observed_user_tags"],
        "shown_unselected_tags": signal.get("shown_unselected_tags", []),
        "signal_strength": signal["signal_strength"],
        "interpretation_confidence": signal["interpretation_confidence"],
        "page_id": signal["page_context"].get("page_id"),
        "page_intent": signal["page_context"].get("page_intent"),
        "apple_context_policy": signal["apple_exposure_context"]["context_type"],
    }


def compact_role(role: dict[str, Any]) -> dict[str, Any]:
    return {
        "atlas_role_assignment_id": role["atlas_role_assignment_id"],
        "atlas_node_id": role["atlas_node_id"],
        "role": role["role"],
        "candidate_pool_behavior": role["candidate_pool_behavior"],
        "confidence": role["confidence"],
        "lifecycle": role["lifecycle"],
        "evidence_signal_ids": role["evidence_signal_ids"],
    }


def compact_update(update: dict[str, Any]) -> dict[str, Any]:
    payload = update.get("proposed_payload") or {}
    return {
        "update_candidate_id": update["update_candidate_id"],
        "source": update["source"],
        "source_signal_ids": update["source_signal_ids"],
        "target_atlas_node_id": update["target_atlas_node_id"],
        "proposed_action": update["proposed_action"],
        "recommended_role": payload.get("role") or payload.get("recommended_role"),
        "candidate_pool_behavior": payload.get("candidate_pool_behavior"),
        "confidence_delta": update["confidence_delta"],
        "recurrence_requirement": update["recurrence_requirement"],
        "review_requirement": update["review_requirement"],
        "canonical_graph_mutation_allowed": update["canonical_graph_mutation_allowed"],
        "generated_hypothesis_only": update["generated_hypothesis_only"],
        "lifecycle": update["lifecycle"],
    }


def compact_music_ref(ref: dict[str, Any]) -> dict[str, Any]:
    return {
        "object_type": ref.get("object_type"),
        "ref_source": ref.get("ref_source"),
        "display_name": ref.get("display_name"),
        "credited_artist_name": ref.get("credited_artist_name"),
        "canonical_artist_id": ref.get("canonical_artist_id"),
        "canonical_album_id": ref.get("canonical_album_id"),
        "canonical_song_recording_id": ref.get("canonical_song_recording_id"),
        "resolution_state": ref.get("resolution_state"),
    }


def artist_context_key(tile: dict[str, Any]) -> str | None:
    ref = tile.get("music_object_ref") or {}
    return (
        ref.get("artist_display_name")
        or ref.get("credited_artist_name")
        or (ref.get("display_name") if ref.get("object_type") == "artist" else None)
    )


def page_intent_summaries(packet: dict[str, Any]) -> list[dict[str, Any]]:
    summaries = []
    for page in packet.get("pages", []):
        intent_counts: dict[str, int] = defaultdict(int)
        for tile in page.get("tiles", []):
            intent_counts[tile.get("page_intent") or "unknown"] += 1
        summaries.append(
            {
                "page_id": page.get("page_id"),
                "stage": page.get("stage"),
                "page_number": page.get("page_number"),
                "page_mode": page.get("page_mode"),
                "intent_counts": dict(sorted(intent_counts.items())),
            }
        )
    return summaries


def count_empty_redundant_fields(packet: dict[str, Any]) -> dict[str, int]:
    counts = defaultdict(int)
    for tile in flatten_tiles(packet):
        if not tile.get("observed_selected_tags"):
            counts["empty_observed_selected_tags"] += 1
        if not tile.get("shown_unselected_tags"):
            counts["empty_shown_unselected_tags"] += 1
        if not tile.get("response_evidence_refs"):
            counts["empty_response_evidence_refs"] += 1
        if tile.get("scores"):
            counts["debug_scores_retained_for_qa_only"] += 1
    return dict(sorted(counts.items()))


def role_for_reaction(reaction: str | None, object_type: str) -> str:
    if reaction == "love":
        return "landmark"
    if reaction == "like":
        return "waypoint" if object_type == "album" else "frontier"
    if reaction == "ok":
        return "waypoint"
    if reaction == "dont_like":
        return "dead_end"
    if reaction == "dont_know_enough":
        return "unknown"
    return "signal_only"


def candidate_pool_behavior_for_role(role: str, reaction: str | None) -> str:
    if role == "landmark":
        return "anchor"
    if role == "frontier":
        return "probe"
    if role == "waypoint":
        return "bridge" if reaction == "like" else "waypoint"
    if role == "dead_end":
        return "trap"
    if role == "unknown":
        return "probe"
    return "unknown"


def event_type_for_reaction(reaction: str | None) -> str:
    if reaction == "dont_know_enough":
        return "familiarity"
    return "reaction"


def schema_reaction_value(reaction: str | None) -> str:
    return {
        "love": "love",
        "like": "like",
        "ok": "neutral",
        "dont_like": "dislike",
        "dont_know_enough": "dont_know",
    }.get(reaction or "", "unknown")


def normalized_signal(reaction: str | None, interpretation: str | None) -> str:
    return {
        "love": "strong_positive",
        "like": "positive",
        "ok": "weak_positive_or_familiarity",
        "dont_like": "negative_scope_carefully",
        "dont_know_enough": "unknown_or_insufficient_familiarity",
    }.get(reaction or "", interpretation or "unknown")


def signal_confidence(reaction: str | None) -> tuple[float, float, str, str]:
    if reaction == "love":
        return 0.86, 0.7, "direct_user_reaction", "A love reaction is strong survey evidence but remains provisional until recurrence or review."
    if reaction == "like":
        return 0.68, 0.55, "direct_user_reaction", "A like reaction supports a candidate role without promotion."
    if reaction == "ok":
        return 0.34, 0.32, "survey_pattern", "An ok response is weak positive or familiarity evidence, useful as a waypoint at most."
    if reaction == "dont_like":
        return 0.72, 0.52, "direct_user_reaction", "A negative reaction is meaningful but must be scoped to the smallest justified object."
    if reaction == "dont_know_enough":
        return 0.18, 0.18, "survey_pattern", "Insufficient familiarity is not negative taste evidence."
    return 0.3, 0.25, "survey_pattern", "Unknown survey response retained as low-confidence evidence."


def confidence_delta(reaction: str | None) -> float:
    return {
        "love": 0.22,
        "like": 0.14,
        "ok": 0.05,
        "dont_like": 0.12,
        "dont_know_enough": 0.02,
    }.get(reaction or "", 0.01)


def scope_limit_for(music_ref: dict[str, Any], reaction: str | None) -> str:
    if reaction == "dont_like":
        return f"{music_ref['object_type']}_only_until_recurrence"
    if music_ref["object_type"] == "song_recording":
        return "recording_first_do_not_merge_by_title"
    return f"{music_ref['object_type']}_level"


def edge_conditions_for(reaction: str | None, music_ref: dict[str, Any]) -> list[str]:
    conditions = []
    if reaction == "dont_like":
        conditions.append("Do not broaden this negative response into a genre-level dislike without recurrence.")
    if reaction == "dont_know_enough":
        conditions.append("Treat as familiarity uncertainty, not negative evidence.")
    if music_ref["object_type"] == "song_recording":
        conditions.append("Recording-first policy applies; same title is not enough to merge or generalize.")
    return conditions


def review_reason_for(role: str, reaction: str | None) -> str:
    if role == "landmark":
        return "Candidate Landmark from Survey requires recurrence or review before promotion."
    if role == "dead_end":
        return "Dead-end hypothesis from a negative response requires scoped review."
    if reaction == "ok":
        return "Weak waypoint evidence should be tested before use as durable Atlas truth."
    return "Survey-created candidate remains provisional."


def role_assignment_summary(role: str, behavior: str, reaction: str | None, role_policy: dict[str, Any]) -> str:
    policy_reason = role_policy.get("reason")
    if role == "landmark":
        return f"Density-aware candidate Landmark; provisional only. {policy_reason}"
    if role == "frontier":
        return f"Density-aware Frontier hypothesis; use as probe. {policy_reason}"
    if role == "dead_end":
        return f"Scoped dead-end hypothesis; do not broaden without review. {policy_reason}"
    if role == "waypoint":
        return f"Candidate Waypoint; useful for route-building, not a core verdict. {policy_reason}"
    if role == "unknown":
        return f"Unknown/familiarity or contradiction state; do not treat as negative taste evidence. {policy_reason}"
    return f"Signal-only Survey assignment with candidate_pool_behavior={behavior}. {policy_reason}"


def node_id_for(profile_id: str, music_ref: dict[str, Any]) -> str:
    key = (
        music_ref.get("canonical_artist_id")
        or music_ref.get("canonical_album_id")
        or music_ref.get("canonical_song_recording_id")
        or music_ref.get("composition_placeholder_id")
        or music_ref.get("user_music_object_id")
        or stable_hash(json.dumps(music_ref, sort_keys=True))[:12]
    )
    return f"atlas_node:survey:{slug(profile_id)}:{slug(music_ref['object_type'])}:{slug(str(key))}"


def confidence(score: float, basis: str, summary: str) -> dict[str, Any]:
    rounded = round(float(score), 3)
    if rounded >= 0.75:
        band = "high"
    elif rounded >= 0.45:
        band = "medium"
    else:
        band = "low"
    return {
        "confidence_score": rounded,
        "confidence_band": band,
        "confidence_basis": basis,
        "confidence_summary": summary,
    }


def lifecycle(status: str, review_state: str, promotion_state: str) -> dict[str, str]:
    return {
        "status": status,
        "review_state": review_state,
        "promotion_state": promotion_state,
    }


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")))
            handle.write("\n")


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(REPO_ROOT))


def slug(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._:-]+", "_", str(value).strip().lower())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned or "unknown"


def stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def ratio(numerator: int | None, denominator: int | None) -> float | None:
    if not numerator or not denominator:
        return None
    return round(numerator / denominator, 4)


def iter_keys(value: Any) -> set[str]:
    keys = set()
    if isinstance(value, dict):
        for key, child in value.items():
            keys.add(str(key))
            keys.update(iter_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(iter_keys(child))
    return keys


if __name__ == "__main__":
    raise SystemExit(main())
