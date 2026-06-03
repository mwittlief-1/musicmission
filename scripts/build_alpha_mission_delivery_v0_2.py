#!/usr/bin/env python3
"""Build the Cartenza Alpha Mission Delivery v0.2 readiness packet.

This script derives a compact app-import readiness fixture set from the accepted
Phase 1G offline song-pack simulation. Hidden oracle reactions remain outside
the generated app-import payloads; Phase 1G scores are used only to classify the
offline golden examples for PM review.
"""

from __future__ import annotations

import copy
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PHASE1G_RESULTS = ROOT / "data/product_contracts/mission_opportunity_selection_v0_1/evaluations/phase1g_construction_policy_llm_review/phase1g_song_pack_results_v0_1.json"
OUT = ROOT / "data/product_contracts/alpha_mission_delivery_v0_2"

CONTRACT_VERSION = "alpha_mission_delivery_v0_2"
CREATED_AT = "2026-05-29T00:00:00Z"

ACTIVE_MISSION_TYPES = [
    "context_dependence_test",
    "boundary_test",
    "bridge_test",
    "archetype_depth_test",
    "gateway_test",
]

DEFERRED_MISSION_TYPES = [
    "artist_depth_test",
    "album_container_test",
    "false_nearby_test",
    "evidence_repair_test",
    "exception_scope_test",
]

MISSION_ARCHETYPE = {
    "context_dependence_test": "Nearby Road",
    "boundary_test": "Dead End Check",
    "bridge_test": "Frontier Route",
    "archetype_depth_test": "Nearby Road",
    "gateway_test": "Start Here",
    "artist_depth_test": "Artist Route",
    "album_container_test": "Album Route",
    "false_nearby_test": "Dead End Check",
    "evidence_repair_test": "Correction Route",
    "exception_scope_test": "Correction Route",
}

MISSION_GOALS = {
    "context_dependence_test": "Clarify whether the listener responds to the music itself, the surrounding context, or both.",
    "boundary_test": "Find the edge between a known positive area and a nearby uncertain or mixed area without making the route punitive.",
    "bridge_test": "Test whether a known positive source area can carry into an under-tested target through a plausible path.",
    "archetype_depth_test": "Test whether the listener likes deeper or less obvious material inside an already promising archetype.",
    "gateway_test": "Use a low-risk entry point to introduce an under-tested family or archetype.",
    "artist_depth_test": "Deferred for Alpha auto-import; requires stricter artist-specific construction before automation.",
    "album_container_test": "Deferred for Alpha auto-import; requires stricter album-container construction before automation.",
    "false_nearby_test": "Deferred for Alpha auto-import except manual review because the negative-risk profile is high.",
    "evidence_repair_test": "Deferred for Alpha auto-import until repair-specific route policy exists.",
    "exception_scope_test": "Deferred for Alpha auto-import until scope-isolation policy exists.",
}

ROLE_MAP = {
    "anchor": "anchor",
    "probe": "probe",
    "boundary": "boundary",
    "bridge": "bridge",
    "context": "context",
    "false_nearby": "boundary",
    "control": "control",
    "comparator": "comparator",
}


def slug(value: str) -> str:
    out = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return out or "unknown"


def load_phase1g() -> dict[str, Any]:
    if not PHASE1G_RESULTS.exists():
        raise FileNotFoundError(f"Missing accepted Phase 1G results: {PHASE1G_RESULTS}")
    return json.loads(PHASE1G_RESULTS.read_text())


def pick_unique(
    packs: list[dict[str, Any]],
    count: int,
    used_ids: set[str],
    *,
    mission_type: str | None = None,
    alpha: bool | None = None,
    reverse: bool = True,
    extra_filter=None,
) -> list[dict[str, Any]]:
    filtered = []
    for pack in packs:
        if pack["pack_id"] in used_ids:
            continue
        if mission_type and pack["mission_type"] != mission_type:
            continue
        if alpha is not None and bool(pack.get("alpha_plausible")) != alpha:
            continue
        if extra_filter and not extra_filter(pack):
            continue
        filtered.append(pack)

    filtered.sort(
        key=lambda p: (
            p.get("mission_type_adjusted_smell_score", 0),
            p.get("non_failure_rate", 0),
            -p.get("negative_hit_rate", 0),
            p.get("pack_id", ""),
        ),
        reverse=reverse,
    )
    out = filtered[:count]
    used_ids.update(p["pack_id"] for p in out)
    return out


def select_golden_packs(packs: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    used: set[str] = set()
    approved: list[dict[str, Any]] = []

    for mission_type in ["context_dependence_test", "boundary_test", "bridge_test", "archetype_depth_test"]:
        approved.extend(
            pick_unique(
                packs,
                2,
                used,
                mission_type=mission_type,
                alpha=True,
                extra_filter=lambda p: p.get("negative_hit_rate", 1) <= 0.3334
                and p.get("non_failure_rate", 0) >= 0.67
                and not p.get("too_random_flag"),
            )
        )

    approved.extend(
        pick_unique(
            packs,
            2,
            used,
            alpha=True,
            extra_filter=lambda p: p["mission_type"] in ACTIVE_MISSION_TYPES
            and p["mission_type"] != "gateway_test",
        )
    )

    revise = pick_unique(
        packs,
        6,
        used,
        alpha=False,
        extra_filter=lambda p: p["mission_type"] in ["context_dependence_test", "boundary_test", "bridge_test", "archetype_depth_test"],
    )

    rejected: list[dict[str, Any]] = []
    for mission_type in ["artist_depth_test", "album_container_test"]:
        rejected.extend(pick_unique(packs, 2, used, mission_type=mission_type))

    rejected.extend(
        pick_unique(
            packs,
            1,
            used,
            alpha=False,
            extra_filter=lambda p: p["mission_type"] in ACTIVE_MISSION_TYPES
            and p.get("negative_hit_rate", 0) >= 0.5,
        )
    )
    rejected.extend(
        pick_unique(
            packs,
            1,
            used,
            alpha=True,
            extra_filter=lambda p: p["mission_type"] in ACTIVE_MISSION_TYPES,
        )
    )

    return {"approved": approved[:10], "revise": revise[:6], "rejected": rejected[:6]}


def route_role_counts(songs: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(ROLE_MAP.get(song.get("source_role", "probe"), "probe") for song in songs))


def risk_level_for_pack(pack: dict[str, Any]) -> str:
    mission_type = pack["mission_type"]
    if mission_type in {"boundary_test", "false_nearby_test"}:
        return "medium"
    if pack.get("negative_hit_rate", 0) > 0.33 or pack.get("negative_overload_flag"):
        return "high"
    if mission_type in {"bridge_test", "context_dependence_test"}:
        return "medium"
    return "low"


def expected_signal_for_role(mission_type: str, role: str) -> str:
    if role == "anchor":
        return "Confirm the known signal is still a usable anchor."
    if role == "bridge":
        return "Show whether the source-to-target path produces non-failure evidence."
    if role == "boundary":
        return "Clarify whether the listener accepts or rejects the nearby edge case."
    if role == "context":
        return "Separate context-heavy response from context-light response."
    if role == "comparator":
        return "Provide a nearby comparison point for the target uncertainty."
    if role == "control":
        return "Keep the route interpretable by isolating one contrast dimension."
    if mission_type == "archetype_depth_test":
        return "Test whether deeper same-archetype material remains tolerable."
    return "Probe the selected uncertainty without assuming preference."


def role_to_risk_flags(role: str, mission_type: str) -> list[str]:
    flags: list[str] = []
    if role in {"boundary", "false_nearby"}:
        flags.append("controlled_negative_risk")
    if mission_type == "bridge_test" and role in {"bridge", "probe"}:
        flags.append("target_area_uncertainty")
    if mission_type == "context_dependence_test" and role == "context":
        flags.append("context_overlay")
    return flags


def source_trace_for_pack(pack: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_layer": "offline_phase1g_synthetic_song_pack",
        "source_selector_output_ref": pack.get("source_selector_output_ref"),
        "source_opportunity_refs": pack.get("source_opportunity_ids", []),
        "source_opportunity_summary": pack.get("source_opportunity_summary", []),
        "source_evidence_summary": {
            "profile_id": pack.get("profile_id"),
            "evidence_scale": pack.get("evidence_scale"),
            "sampling_mode": pack.get("sampling_mode"),
            "visible_evidence_only_for_selector": True,
            "survey_ok_semantics": "ignored/no signal",
            "mission_ok_semantics": "weak non-failure/waypoint evidence",
        },
        "multi_source_route": len(set(pack.get("source_opportunity_ids", []))) > 1,
        "multi_source_route_reason": "Phase 1G top-window construction combined compatible opportunities for offline review."
        if len(set(pack.get("source_opportunity_ids", []))) > 1
        else None,
        "held_out_review_data_used_for_runtime": False,
        "selector_read_held_out_review_data": False,
        "canonical_graph_mutation_allowed": False,
    }


def convert_pack(
    pack: dict[str, Any],
    *,
    expected_class: str,
    sequence_number: int,
    forced_status: str,
    forced_reason: str | None = None,
) -> dict[str, Any]:
    mission_type = pack["mission_type"]
    mission_id = f"alpha-mission-v0-2-{sequence_number:03d}-{slug(pack['pack_id'])}"
    role_counts = route_role_counts(pack["songs"])
    title = {
        "context_dependence_test": "Context Check: Same Feeling, Different Frame",
        "boundary_test": "Boundary Check: Where the Edge Starts",
        "bridge_test": "Bridge Route: From Known Ground to New Ground",
        "archetype_depth_test": "Depth Route: Past the Obvious Signal",
        "artist_depth_test": "Deferred Artist Depth Route",
        "album_container_test": "Deferred Album Container Route",
    }.get(mission_type, "Alpha Mission Route")

    route = []
    for index, song in enumerate(pack["songs"], start=1):
        role = ROLE_MAP.get(song.get("source_role", "probe"), "probe")
        artist = song.get("artist_display_name") or "Unknown Artist"
        title_text = song.get("title") or "Unknown Title"
        song_id = song.get("song_id") or f"synthetic-song-{index}"
        resolution_status = "candidate"
        route.append(
            {
                "mission_item_id": f"{mission_id}-item-{index:02d}",
                "sequence_index": index,
                "role": role,
                "song_title": title_text,
                "artist_name": artist,
                "album_title": None,
                "canonical_song_id": song_id,
                "canonical_artist_id": f"artist-{slug(artist)}",
                "canonical_album_id": None,
                "apple_music_id": None,
                "apple_music_url": None,
                "duration_ms": 0,
                "artwork_url": None,
                "preview_url": None,
                "resolution_status": resolution_status,
                "expected_signal": expected_signal_for_role(mission_type, role),
                "why_in_route": song.get("why_selected", "").replace("hidden", "held-out").strip()
                or f"{role} selected from the source opportunity for {mission_type}.",
                "reaction_chip_set_id": "alpha_v0_2_standard_reactions",
                "risk_flags": role_to_risk_flags(role, mission_type),
                "source_opportunity_id": song.get("source_opportunity_id"),
                "source_mission_type": song.get("source_mission_type"),
                "target_object_ids": song.get("target_object_ids", []),
                "graph_context_refs": song.get("graph_context_refs", []),
            }
        )

    status = forced_status
    if expected_class == "approved_app_import_candidate":
        status = "app_import_candidate"
    elif expected_class == "revise_needed":
        status = "needs_revision"
    elif expected_class == "rejected_product" and not forced_status:
        status = "rejected_product"

    if forced_reason == "unresolved_playback_item" and route:
        route[0]["resolution_status"] = "unresolved"
        route[0]["canonical_song_id"] = None
        status = "app_import_blocked_unresolved"

    if forced_reason == "source_opportunity_contamination":
        status = "app_import_blocked_policy"

    why_now = (
        f"You got this mission because visible {pack.get('sampling_mode')} evidence at {pack.get('evidence_scale')} atoms "
        f"suggests a {mission_type.replace('_', ' ')} is testable, and these songs test the specific uncertainty without using hidden oracle truth."
    )

    if forced_reason == "missing_explanation":
        why_now = ""

    source_trace = source_trace_for_pack(pack)
    if forced_reason == "source_opportunity_contamination":
        source_trace["multi_source_route"] = True
        source_trace["multi_source_route_reason"] = None

    mission = {
        "mission_id": mission_id,
        "contract_version": CONTRACT_VERSION,
        "app_import_status": status,
        "mission_type": mission_type,
        "mission_archetype": MISSION_ARCHETYPE.get(mission_type, "Nearby Road"),
        "title": title,
        "brief": pack.get("mission_goal") or MISSION_GOALS.get(mission_type, ""),
        "hypothesis": MISSION_GOALS.get(mission_type, ""),
        "why_this_mission_now": why_now,
        "coherence_sentence": why_now,
        "risk_level": risk_level_for_pack(pack),
        "route": route,
        "completion_criteria": {
            "minimum_items_played": min(4, len(route)),
            "minimum_primary_reactions": min(4, len(route)),
            "teaches": "Whether the selected opportunity can produce interpretable route-level evidence.",
        },
        "feedback_model": {
            "chip_set_id": "alpha_v0_2_standard_reactions",
            "display_labels": ["Love", "Like", "Ok / Keep", "Dislike", "Skip", "Wrong version", "Unavailable"],
            "operation_mapping": {
                "Love": "strong_positive",
                "Like": "qualified_positive",
                "Ok / Keep": "keep_waypoint",
                "Dislike": "negative",
                "Skip": "skip_or_no_signal",
                "Wrong version": "issue_wrong_version",
                "Unavailable": "issue_unavailable",
            },
            "survey_ok_semantics": "ignored/no signal",
            "mission_ok_semantics": "weak non-failure/waypoint evidence",
        },
        "source_trace": source_trace,
        "validation": {
            "expected_class": expected_class,
            "offline_review_source_pack_id": pack["pack_id"],
            "offline_phase1g_alpha_plausible": bool(pack.get("alpha_plausible")),
            "offline_phase1g_gate_fail_reasons": pack.get("alpha_gate_fail_reasons", []),
            "golden_classification_reasons": classification_reasons(pack, expected_class, forced_reason),
        },
        "resolution": {
            "resolved_count": 0,
            "candidate_count": sum(1 for item in route if item["resolution_status"] == "candidate"),
            "unresolved_count": sum(1 for item in route if item["resolution_status"] == "unresolved"),
            "blocked_count": sum(1 for item in route if item["resolution_status"] == "blocked"),
            "ordinary_alpha_ready_requires_no_unresolved": True,
            "apple_music_resolution_remaining": True,
        },
        "runtime_flags": {
            "runtime_selector_wiring": False,
            "real_listener_evidence_connected": False,
            "production_mission_generation_allowed": False,
            "final_mission_content": False,
            "canonical_graph_mutation_allowed": False,
        },
    }
    mission["validation"]["role_counts"] = role_counts
    return mission


def classification_reasons(pack: dict[str, Any], expected_class: str, forced_reason: str | None) -> list[str]:
    reasons: list[str] = []
    mission_type = pack["mission_type"]
    if mission_type in DEFERRED_MISSION_TYPES:
        reasons.append("mission_type_deferred_for_alpha_auto_import")
    if pack.get("negative_hit_rate", 0) > 0.33 or pack.get("negative_overload_flag"):
        reasons.append("too_negative")
    if pack.get("too_random_flag"):
        reasons.append("too_random")
    if pack.get("mission_coherence_score", 1) < 0.65:
        reasons.append("route_coherence_below_preferred_gate")
    if pack.get("non_failure_rate", 1) < 0.67:
        reasons.append("weak_or_punitive_route_evidence")
    if forced_reason:
        reasons.append(forced_reason)
    if expected_class == "approved_app_import_candidate":
        reasons.append("approved_for_app_fixture_import_after_music_resolution")
    if expected_class == "revise_needed" and not reasons:
        reasons.append("needs_human_revision_before_alpha_import")
    if expected_class == "rejected_product" and not reasons:
        reasons.append("not_alpha_safe")
    return sorted(set(reasons))


def construction_contract() -> dict[str, Any]:
    active_policy = {
        "context_dependence_test": {
            "product_question": MISSION_GOALS["context_dependence_test"],
            "eligible_target_object_types": ["archetype", "artist_within_archetype", "album", "song_cluster"],
            "required_source_opportunity_purity": "single coherent opportunity preferred; top-window mixing allowed only when all source opportunities share the same target uncertainty.",
            "allowed_route_item_roles": ["anchor", "context", "comparator", "control"],
            "required_role_counts": {"anchor": {"min": 1}, "context": {"min": 2}, "comparator": {"min": 1}, "control": {"min": 1}},
            "minimum_route_size": 5,
            "maximum_route_size": 6,
            "default_alpha_route_size": 6,
            "anchor_requirements": "At least one visible-evidence anchor or low-risk representative.",
            "probe_requirements": "Context-heavy and context-light items must be balanced.",
            "comparator_control_requirements": "At least one comparator or control isolates the relevant context dimension.",
            "maximum_negative_risk_exposure": 1,
            "maximum_known_conflict_exposure": 1,
            "source_opportunity_mixing_policy": "Allowed only for same target/context question with multi_source_route=true and explanation.",
            "required_user_facing_explanation_fields": ["brief", "hypothesis", "why_this_mission_now", "coherence_sentence", "why_in_route"],
            "rejection_conditions": ["unresolved ordinary route item", "no context contrast", "hidden oracle leakage", "random/unexplainable route"],
            "revise_conditions": ["weak control", "overly safe with no context contrast", "too much unknown material"],
            "app_import_eligibility_rules": "Eligible when route is coherent, concrete, and no ordinary unresolved playback items remain.",
        },
        "boundary_test": {
            "product_question": MISSION_GOALS["boundary_test"],
            "eligible_target_object_types": ["archetype_pair", "family_pair", "song_cluster"],
            "required_source_opportunity_purity": "Pair target IDs must match the source opportunity pair.",
            "allowed_route_item_roles": ["anchor", "boundary", "comparator", "control"],
            "required_role_counts": {"anchor": {"min": 2}, "boundary": {"min": 1}, "comparator": {"min": 1}, "control": {"min": 1}},
            "minimum_route_size": 5,
            "maximum_route_size": 6,
            "default_alpha_route_size": 6,
            "anchor_requirements": "Two likely-safe anchors from the positive side.",
            "probe_requirements": "Boundary items must test a specific edge, not random contrast.",
            "comparator_control_requirements": "Comparator/control must clarify the differentiating dimension.",
            "maximum_negative_risk_exposure": 2,
            "maximum_known_conflict_exposure": 2,
            "source_opportunity_mixing_policy": "Normally disallowed; allowed only for same pair target and explicit multi_source_route reason.",
            "required_user_facing_explanation_fields": ["brief", "hypothesis", "why_this_mission_now", "coherence_sentence", "why_in_route"],
            "rejection_conditions": ["3+ negative-risk items", "anchor fails thesis with multiple high-risk probes", "unresolved playback", "no differentiating dimension"],
            "revise_conditions": ["one anchor only", "contrast too harsh", "control missing"],
            "app_import_eligibility_rules": "Eligible only with bounded contrast and a clear one-sentence explanation.",
        },
        "bridge_test": {
            "product_question": MISSION_GOALS["bridge_test"],
            "eligible_target_object_types": ["family_pair", "archetype_pair"],
            "required_source_opportunity_purity": "Source and target endpoints must match source opportunity endpoint refs.",
            "allowed_route_item_roles": ["anchor", "bridge", "probe", "comparator", "control"],
            "required_role_counts": {"anchor": {"min": 1}, "bridge": {"min": 1}, "probe": {"min": 1}, "control": {"min": 1}},
            "minimum_route_size": 5,
            "maximum_route_size": 6,
            "default_alpha_route_size": 6,
            "anchor_requirements": "One source-side anchor grounded in visible evidence.",
            "probe_requirements": "Target probes must use low-to-medium risk paths.",
            "comparator_control_requirements": "At least one comparator/control keeps source-to-target continuity interpretable.",
            "maximum_negative_risk_exposure": 1,
            "maximum_known_conflict_exposure": 1,
            "source_opportunity_mixing_policy": "Allowed only across compatible bridge opportunities sharing the same source or target endpoint.",
            "required_user_facing_explanation_fields": ["brief", "hypothesis", "why_this_mission_now", "coherence_sentence", "why_in_route"],
            "rejection_conditions": ["jump too far", "unrelated target dump", "hidden oracle leakage", "unresolved ordinary playback"],
            "revise_conditions": ["weak source anchor", "control missing", "target path not explained"],
            "app_import_eligibility_rules": "Eligible when continuity is explicit and target risk remains bounded.",
        },
        "archetype_depth_test": {
            "product_question": MISSION_GOALS["archetype_depth_test"],
            "eligible_target_object_types": ["archetype"],
            "required_source_opportunity_purity": "Single archetype target preferred; variants must preserve provenance to the same base target.",
            "allowed_route_item_roles": ["anchor", "probe", "comparator", "control"],
            "required_role_counts": {"anchor": {"min": 1}, "probe": {"min": 2}, "comparator": {"min": 1}, "control": {"min": 1}},
            "minimum_route_size": 5,
            "maximum_route_size": 6,
            "default_alpha_route_size": 6,
            "anchor_requirements": "One visible anchor or strong representative.",
            "probe_requirements": "Deeper candidates must remain plausible; no forced negative probe.",
            "comparator_control_requirements": "Comparator/control stays inside broad family.",
            "maximum_negative_risk_exposure": 1,
            "maximum_known_conflict_exposure": 1,
            "source_opportunity_mixing_policy": "Allowed only for same archetype base target and explicit reason.",
            "required_user_facing_explanation_fields": ["brief", "hypothesis", "why_this_mission_now", "coherence_sentence", "why_in_route"],
            "rejection_conditions": ["obscure/random pile", "multiple high-risk probes", "no visible anchor", "unresolved playback"],
            "revise_conditions": ["too safe/no depth", "too many uncertain items", "weak source evidence"],
            "app_import_eligibility_rules": "Eligible only with strict negative budget and coherent depth progression.",
        },
        "gateway_test": {
            "product_question": MISSION_GOALS["gateway_test"],
            "eligible_target_object_types": ["family", "archetype"],
            "required_source_opportunity_purity": "One under-tested target with a clean gateway and representative follow-up.",
            "allowed_route_item_roles": ["anchor", "bridge", "probe", "comparator", "control"],
            "required_role_counts": {"anchor": {"min": 1}, "bridge": {"min": 1}, "probe": {"min": 1}},
            "minimum_route_size": 5,
            "maximum_route_size": 6,
            "default_alpha_route_size": 6,
            "anchor_requirements": "Low-risk gateway anchor.",
            "probe_requirements": "Representative follow-up must be available.",
            "comparator_control_requirements": "Comparator/control recommended for interpretability.",
            "maximum_negative_risk_exposure": 1,
            "maximum_known_conflict_exposure": 1,
            "source_opportunity_mixing_policy": "Normally disallowed.",
            "required_user_facing_explanation_fields": ["brief", "hypothesis", "why_this_mission_now", "coherence_sentence", "why_in_route"],
            "rejection_conditions": ["overfamiliar gateway only", "no representative follow-up", "unresolved playback"],
            "revise_conditions": ["weak target explanation", "gateway does not cohere with representative"],
            "app_import_eligibility_rules": "Optional Alpha-active when low risk and concrete playback refs exist.",
        },
    }

    deferred = {
        mission_type: {
            "alpha_auto_allowed": False,
            "manual_only": True,
            "deferred": True,
            "rationale": MISSION_GOALS[mission_type],
            "app_import_eligibility_rules": "Blocked from automatic Alpha import until a stricter mission-specific construction contract is accepted.",
        }
        for mission_type in DEFERRED_MISSION_TYPES
    }

    return {
        "contract_version": CONTRACT_VERSION,
        "created_at": CREATED_AT,
        "product_name": "Cartenza",
        "scope": "Offline/app-import readiness contract for Alpha-safe mission pack construction.",
        "runtime_wiring_allowed": False,
        "production_mission_generation_allowed": False,
        "canonical_graph_mutation_allowed": False,
        "hidden_oracle_runtime_knowledge_allowed": False,
        "universal_alpha_route_rules": {
            "default_route_size": "5-6 songs",
            "short_route_allowed_only_when_marked": True,
            "short_route_size": 3,
            "ordinary_alpha_unresolved_tracks_allowed": False,
            "requires_concrete_music_object_refs_or_preresolved_playback_metadata": True,
            "requires_one_sentence_explanation": True,
            "requires_hypothesis": True,
            "requires_route_rationale": True,
            "requires_expected_signal_per_item": True,
            "requires_risk_level": True,
            "requires_completion_criteria": True,
        },
        "negative_budget": {
            "ordinary_alpha_max_high_risk_negative_candidates": 1,
            "boundary_or_correction_max_high_risk_negative_candidates": 2,
            "first_run_alpha_hard_max_negative_risk_items_in_six_song_route": 2,
            "never_allow_three_or_more_negative_risk_items": True,
            "diagnostic_not_punitive": True,
        },
        "source_purity": {
            "default": "single coherent source opportunity",
            "mixed_source_allowed_only_when_contract_allows": True,
            "multi_source_route_flag_required": True,
            "multi_source_route_reason_required": True,
        },
        "active_mission_type_policies": active_policy,
        "deferred_mission_type_policies": deferred,
        "app_import_status_enum": [
            "review_only",
            "schema_valid",
            "contract_valid",
            "needs_revision",
            "rejected_product",
            "app_import_candidate",
            "app_import_blocked_unresolved",
            "app_import_blocked_policy",
            "app_import_ready",
        ],
    }


def payload_schema() -> dict[str, Any]:
    mission_type_enum = ACTIVE_MISSION_TYPES + DEFERRED_MISSION_TYPES
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://cartenza.local/schemas/alpha_mission_delivery_v0_2/app_import_mission_payload_v0_2.schema.json",
        "title": "Cartenza Alpha App-Import Mission Payload v0.2",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "mission_id",
            "contract_version",
            "app_import_status",
            "mission_type",
            "mission_archetype",
            "title",
            "brief",
            "hypothesis",
            "why_this_mission_now",
            "coherence_sentence",
            "risk_level",
            "route",
            "completion_criteria",
            "feedback_model",
            "source_trace",
            "validation",
            "resolution",
            "runtime_flags",
        ],
        "properties": {
            "mission_id": {"type": "string", "minLength": 1},
            "contract_version": {"const": CONTRACT_VERSION},
            "app_import_status": {
                "enum": [
                    "review_only",
                    "schema_valid",
                    "contract_valid",
                    "needs_revision",
                    "rejected_product",
                    "app_import_candidate",
                    "app_import_blocked_unresolved",
                    "app_import_blocked_policy",
                    "app_import_ready",
                ]
            },
            "mission_type": {"enum": mission_type_enum},
            "mission_archetype": {
                "enum": [
                    "Nearby Road",
                    "Frontier Route",
                    "Dead End Check",
                    "Correction Route",
                    "Artist Route",
                    "Album Route",
                    "Memory Route",
                    "Start Here",
                ]
            },
            "title": {"type": "string", "minLength": 1},
            "brief": {"type": "string", "minLength": 1},
            "hypothesis": {"type": "string", "minLength": 1},
            "why_this_mission_now": {"type": "string"},
            "coherence_sentence": {"type": "string"},
            "risk_level": {"enum": ["low", "medium", "high"]},
            "route": {
                "type": "array",
                "minItems": 1,
                "items": {"$ref": "#/$defs/route_item"},
            },
            "completion_criteria": {"type": "object", "additionalProperties": True},
            "feedback_model": {"type": "object", "additionalProperties": True},
            "source_trace": {"type": "object", "additionalProperties": True},
            "validation": {"type": "object", "additionalProperties": True},
            "resolution": {"type": "object", "additionalProperties": True},
            "runtime_flags": {
                "type": "object",
                "required": [
                    "runtime_selector_wiring",
                    "real_listener_evidence_connected",
                    "production_mission_generation_allowed",
                    "final_mission_content",
                    "canonical_graph_mutation_allowed",
                ],
                "properties": {
                    "runtime_selector_wiring": {"const": False},
                    "real_listener_evidence_connected": {"const": False},
                    "production_mission_generation_allowed": {"const": False},
                    "final_mission_content": {"const": False},
                    "canonical_graph_mutation_allowed": {"const": False},
                },
                "additionalProperties": False,
            },
        },
        "$defs": {
            "route_item": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "mission_item_id",
                    "sequence_index",
                    "role",
                    "song_title",
                    "artist_name",
                    "album_title",
                    "canonical_song_id",
                    "canonical_artist_id",
                    "canonical_album_id",
                    "apple_music_id",
                    "apple_music_url",
                    "duration_ms",
                    "artwork_url",
                    "preview_url",
                    "resolution_status",
                    "expected_signal",
                    "why_in_route",
                    "reaction_chip_set_id",
                    "risk_flags",
                    "source_opportunity_id",
                    "source_mission_type",
                    "target_object_ids",
                    "graph_context_refs",
                ],
                "properties": {
                    "mission_item_id": {"type": "string", "minLength": 1},
                    "sequence_index": {"type": "integer", "minimum": 1},
                    "role": {"enum": ["anchor", "context", "bridge", "boundary", "probe", "comparator", "control"]},
                    "song_title": {"type": "string", "minLength": 1},
                    "artist_name": {"type": "string", "minLength": 1},
                    "album_title": {"type": ["string", "null"]},
                    "canonical_song_id": {"type": ["string", "null"]},
                    "canonical_artist_id": {"type": ["string", "null"]},
                    "canonical_album_id": {"type": ["string", "null"]},
                    "apple_music_id": {"type": ["string", "null"]},
                    "apple_music_url": {"type": ["string", "null"]},
                    "duration_ms": {"type": "integer", "minimum": 0},
                    "artwork_url": {"type": ["string", "null"]},
                    "preview_url": {"type": ["string", "null"]},
                    "resolution_status": {"enum": ["resolved", "candidate", "unresolved", "blocked"]},
                    "expected_signal": {"type": "string", "minLength": 1},
                    "why_in_route": {"type": "string", "minLength": 1},
                    "reaction_chip_set_id": {"type": ["string", "null"]},
                    "risk_flags": {"type": "array", "items": {"type": "string"}},
                    "source_opportunity_id": {"type": ["string", "null"]},
                    "source_mission_type": {"type": ["string", "null"]},
                    "target_object_ids": {"type": "array", "items": {"type": "string"}},
                    "graph_context_refs": {"type": "array", "items": {"type": "string"}},
                },
            }
        },
    }


def contract_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://cartenza.local/schemas/alpha_mission_delivery_v0_2/mission_construction_contract_v0_2.schema.json",
        "title": "Cartenza Alpha Mission Construction Contract v0.2",
        "type": "object",
        "required": [
            "contract_version",
            "active_mission_type_policies",
            "deferred_mission_type_policies",
            "universal_alpha_route_rules",
            "negative_budget",
            "source_purity",
        ],
        "properties": {
            "contract_version": {"const": CONTRACT_VERSION},
            "active_mission_type_policies": {"type": "object"},
            "deferred_mission_type_policies": {"type": "object"},
            "universal_alpha_route_rules": {"type": "object"},
            "negative_budget": {"type": "object"},
            "source_purity": {"type": "object"},
        },
        "additionalProperties": True,
    }


def typescript_types() -> str:
    return """// Generated by scripts/build_alpha_mission_delivery_v0_2.py
// Offline contract types only; do not import app runtime code here.

export type AlphaMissionType =
  | "context_dependence_test"
  | "boundary_test"
  | "bridge_test"
  | "archetype_depth_test"
  | "gateway_test"
  | "artist_depth_test"
  | "album_container_test"
  | "false_nearby_test"
  | "evidence_repair_test"
  | "exception_scope_test";

export type AppImportStatus =
  | "review_only"
  | "schema_valid"
  | "contract_valid"
  | "needs_revision"
  | "rejected_product"
  | "app_import_candidate"
  | "app_import_blocked_unresolved"
  | "app_import_blocked_policy"
  | "app_import_ready";

export type RouteItemRole =
  | "anchor"
  | "context"
  | "bridge"
  | "boundary"
  | "probe"
  | "comparator"
  | "control";

export type ResolutionStatus = "resolved" | "candidate" | "unresolved" | "blocked";

export interface AlphaMissionRouteItemV0_2 {
  mission_item_id: string;
  sequence_index: number;
  role: RouteItemRole;
  song_title: string;
  artist_name: string;
  album_title: string | null;
  canonical_song_id: string | null;
  canonical_artist_id: string | null;
  canonical_album_id: string | null;
  apple_music_id: string | null;
  apple_music_url: string | null;
  duration_ms: number;
  artwork_url: string | null;
  preview_url: string | null;
  resolution_status: ResolutionStatus;
  expected_signal: string;
  why_in_route: string;
  reaction_chip_set_id: string | null;
  risk_flags: string[];
  source_opportunity_id: string | null;
  source_mission_type: string | null;
  target_object_ids: string[];
  graph_context_refs: string[];
}

export interface AlphaAppImportMissionPayloadV0_2 {
  mission_id: string;
  contract_version: "alpha_mission_delivery_v0_2";
  app_import_status: AppImportStatus;
  mission_type: AlphaMissionType;
  mission_archetype:
    | "Nearby Road"
    | "Frontier Route"
    | "Dead End Check"
    | "Correction Route"
    | "Artist Route"
    | "Album Route"
    | "Memory Route"
    | "Start Here";
  title: string;
  brief: string;
  hypothesis: string;
  why_this_mission_now: string;
  coherence_sentence: string;
  risk_level: "low" | "medium" | "high";
  route: AlphaMissionRouteItemV0_2[];
  completion_criteria: Record<string, unknown>;
  feedback_model: Record<string, unknown>;
  source_trace: Record<string, unknown>;
  validation: Record<string, unknown>;
  resolution: Record<string, unknown>;
  runtime_flags: {
    runtime_selector_wiring: false;
    real_listener_evidence_connected: false;
    production_mission_generation_allowed: false;
    final_mission_content: false;
    canonical_graph_mutation_allowed: false;
  };
}
"""


def README() -> str:
    return f"""# Cartenza Alpha Mission Delivery v0.2

This package is an offline, app-import readiness slice for Cartenza Alpha mission delivery.

It defines how accepted Mission Opportunity Selection outputs may be converted into guarded Alpha mission payloads that the app team can wire against. It is not a production mission generator and it does not connect runtime listener evidence.

## Included

- Mission Construction Contract v0.2 for Alpha-safe mission types.
- App-import mission payload JSON Schema v0.2.
- TypeScript contract types.
- Validator and product gates for route coherence, source purity, negative budget, playback/import readiness, explanation completeness, hidden-oracle leakage, and runtime/canonical mutation flags.
- Golden approved/revise/rejected fixture sets derived from accepted Phase 1G offline song-pack simulations.
- Backend endpoint contract draft for a future first mission batch Supabase function.
- App wiring readiness/gap report.

## Guardrails

- No runtime selector wiring.
- No real listener evidence connection.
- No production mission generation.
- No final mission copy generation.
- No canonical graph mutation.
- Hidden synthetic reactions are not written into app-import payloads.
- Ordinary Alpha app-import-ready missions may not contain unresolved route items.

## Commands

```bash
python3 scripts/build_alpha_mission_delivery_v0_2.py
python3 scripts/validate_alpha_mission_delivery_v0_2.py
```

## Current Bottom Line

App wiring can begin against these local fixtures/contracts for schema, route-card, reaction, validation, and resolution-adapter work. TestFlight UAT is still blocked until Apple Music resolution and app model/schema compatibility are closed.
"""


def mission_contract_md(contract: dict[str, Any]) -> str:
    rows = []
    for mission_type, policy in contract["active_mission_type_policies"].items():
        rows.append(
            f"| `{mission_type}` | yes | no | no | {policy['product_question']} | max negative risk {policy['maximum_negative_risk_exposure']} |"
        )
    for mission_type, policy in contract["deferred_mission_type_policies"].items():
        rows.append(
            f"| `{mission_type}` | no | yes | yes | {policy['rationale']} | blocked from automatic Alpha import |"
        )
    return f"""# Mission Construction Contract v0.2

Scope: convert approved mission opportunity blobs into offline Alpha mission packs that can become app-import candidates after playback resolution.

This contract keeps mission opportunity selection and mission construction separate. It does not generate production missions and does not mutate canonical graph truth.

## Universal Alpha Route Rules

- Default route size: 5-6 songs.
- A 3-song short mission is allowed only when intentionally marked short.
- Ordinary Alpha missions may not include unresolved/search-placeholder tracks.
- Every route item must include concrete music object refs sufficient for Apple Music resolution or pre-resolved playback metadata.
- Every mission needs a one-sentence explanation, hypothesis, route rationale, expected signal per item, risk level, and completion criteria.
- Every mission must produce enough evidence to answer what it taught us.

## Negative Budget

- Max 1 high-risk negative candidate by default.
- Max 2 only for boundary/correction-style missions.
- Never allow a route where the anchor fails the thesis and multiple probes are high risk.
- Never allow 3+ negative-risk items in a 6-song first-run Alpha mission.
- Diagnostic routes must not feel punitive.

## Source Purity

One coherent source opportunity is preferred. Mixed opportunities require `multi_source_route=true` and a clear explanation.

## Mission Type Readiness

| mission_type | alpha_auto_allowed | manual_only | deferred | rationale | Alpha constraint |
| --- | --- | --- | --- | --- | --- |
{chr(10).join(rows)}

The machine-readable form is in `mission_construction_contract_v0_2.json`.
"""


def backend_contract_md() -> str:
    return """# Backend Endpoint Contract Draft v0.2

This is a contract/stub only. No Supabase function is implemented in this slice.

## Endpoint

`POST /functions/v1/generate-first-mission-batch`

## Input

- `tester_id`, `user_id` or `session_id`
- survey evidence export
- starter digest/profile substrate
- candidate pool or opportunity window
- requested mission batch size, default `3`
- allowed mission types
- contract versions
- safety constraints

## Output

- `run_id`
- `status`
- `missions[]`
- validation report
- `app_import_ready_count`
- `blocked_count`
- repair attempts
- error/fallback info

## Logging Requirements

- prompt/template version
- model/version/cost/latency when generation is added
- debug-safe input packet/run record
- output persistence
- validation status
- repair/retry status where implemented
- app-import readiness status

## First Batch Composition

Default batch size: 3 missions.

Suggested composition:

1. one low-risk context/gateway/nearby mission;
2. one boundary or bridge mission;
3. one deeper/archetype-depth mission if safety gates pass.
"""


def status_model_md() -> str:
    return """# App-Import Readiness Status Model v0.2

This status model separates offline product review from app import readiness.

| status | meaning | may show in app as ordinary mission? |
| --- | --- | --- |
| `review_only` | Shape exists for PM/harness review only. | no |
| `schema_valid` | JSON shape passes schema but product gates have not passed. | no |
| `contract_valid` | Mission-type contract gates pass, but import readiness is not established. | no |
| `needs_revision` | Route could become useful, but currently misses a product gate. | no |
| `rejected_product` | Route is not Alpha-safe or mission type is deferred. | no |
| `app_import_candidate` | Route is coherent, concrete enough for resolution, and eligible after playback metadata/Apple Music resolution. | dev/debug only until resolved |
| `app_import_blocked_unresolved` | One or more route items are unresolved or blocked. | no |
| `app_import_blocked_policy` | A policy guardrail failed. | no |
| `app_import_ready` | All schema, contract, policy, explanation, and playback/import gates pass. | yes |

`alpha_plausible` from earlier simulations is intentionally not reused as app readiness.
"""


def app_wiring_report_md() -> str:
    return """# App Wiring Readiness Report v0.2

## Current App Observations

- Current runtime mission model is `MusicAtlasController/Models/Mission.swift`.
- Current app `MissionType` enum is legacy-shaped: `track_probe`, `album_test`, `station_seed`, `playlist_bleed`, `false_nearby_test`.
- New Alpha mission types (`context_dependence_test`, `boundary_test`, `bridge_test`, `archetype_depth_test`, `gateway_test`) are not currently first-class app mission enum cases.
- Current app schema `schema_mission_v0_2.json` is not the same as this app-import payload contract.
- Current app `MissionLoader` validation expects imported route items to enter unresolved so MusicKit resolution evidence is captured in-app.
- The new product contract hard-blocks ordinary app-import-ready missions with unresolved route items. This is a real mismatch to reconcile.
- Current reaction model has stable operations: `strong_positive`, `qualified_positive`, `keep_waypoint`, and `negative`.

## Shortest Safe Wiring Path

1. Add an app-side adapter or separate decoder for `AlphaAppImportMissionPayloadV0_2`.
2. Map Alpha mission types into app display/navigation without collapsing product semantics.
3. Decide whether `resolution_status=candidate` should be imported as a pre-resolution staging state before the existing unresolved MusicKit pass.
4. Resolve or attach Apple Music IDs before promoting any fixture to `app_import_ready`.
5. Keep local golden fixtures behind a dev/debug import path until endpoint generation is trusted.

## Can App Wiring Start?

Yes, for local fixture import, route-card rendering, feedback model mapping, validation UI, and MusicKit resolution adapter work.

## Can TestFlight UAT Start?

No. Playback-ready UAT remains blocked by Apple Music resolution and app model/schema compatibility.
"""


def readiness_packet_md(fixtures: dict[str, Any], contract: dict[str, Any]) -> str:
    all_missions = fixtures["approved_app_import_candidates"] + fixtures["revise_needed"] + fixtures["rejected"]
    fixture_rows = []
    for mission in all_missions:
        fixture_rows.append(
            f"| `{mission['mission_id']}` | `{mission['mission_type']}` | {mission['validation']['expected_class']} | {mission['app_import_status']} | {mission['app_import_status'] in {'app_import_candidate', 'app_import_ready'}} | {', '.join(mission['validation']['golden_classification_reasons'][:2])} |"
        )

    readiness_rows = []
    for mission_type in ACTIVE_MISSION_TYPES:
        readiness_rows.append(f"| `{mission_type}` | yes | no | no | Alpha-active with contract gates |")
    for mission_type in DEFERRED_MISSION_TYPES:
        readiness_rows.append(f"| `{mission_type}` | no | yes | yes | Deferred from automatic Alpha import |")

    blockers = [
        ("Apple Music IDs/resolution missing from golden app-import candidates", "high", "App/Backend", "Resolve candidates or add staging adapter", "yes", "yes"),
        ("App mission enum/schema mismatch", "high", "App", "Add Alpha payload decoder/adapter", "yes", "yes"),
        ("Existing app importer expects unresolved route items", "medium", "App/Product", "Reconcile candidate vs unresolved semantics", "yes", "yes"),
        ("Live backend generation not implemented", "medium", "Backend", "Implement guarded endpoint after local fixture wiring", "no", "yes"),
        ("Artist/album mission types deferred", "low", "PM/Construction", "Write stricter contracts before broad automation", "no", "no"),
    ]
    blocker_rows = "\n".join(f"| {b} | {s} | {o} | {a} | {aw} | {tf} |" for b, s, o, a, aw, tf in blockers)

    return f"""# Cartenza Alpha Mission Wiring Readiness Packet v0.2

Decision: PARTIAL

## What Was Completed

- Mission Construction Contract v0.2 for Alpha-safe mission types.
- App-import mission payload schema and TypeScript types.
- Route validator/product gates.
- Golden approved/revise/rejected fixture set.
- Backend endpoint contract draft.
- App wiring readiness/gap report.
- Deterministic validation report.

## What Was Changed

New offline contract artifacts were added under `data/product_contracts/alpha_mission_delivery_v0_2/` plus two scripts under `scripts/`.

## What Was Intentionally Not Changed

- No iOS runtime files were modified.
- No Supabase function was implemented.
- No Apple Music/API calls were made.
- No canonical graph truth was mutated.
- No production mission generation was added.

## Can App Wiring Start Now?

Yes, against the local app-import payload contract and golden fixtures for decoder/adapter, route-card, feedback, validation, and resolution work.

## Can TestFlight UAT Start Now?

No. TestFlight UAT remains blocked by playback resolution and app schema/model compatibility.

## Top Blockers

| blocker | severity | owner | proposed next action | blocks app wiring? | blocks TestFlight? |
| --- | --- | --- | --- | --- | --- |
{blocker_rows}

## Mission Type Readiness

| mission_type | alpha_auto_allowed | manual_only | deferred | rationale |
| --- | --- | --- | --- | --- |
{chr(10).join(readiness_rows)}

## Fixture Results

| pack_id | mission_type | expected_class | validator_status | app_import_candidate_or_ready | top_reason |
| --- | --- | --- | --- | --- | --- |
{chr(10).join(fixture_rows)}

## Required Artifacts

1. Mission Construction Contract v0.2: `mission_construction_contract_v0_2.md` and `.json`
2. Mission payload JSON Schema: `app_import_mission_payload_v0_2.schema.json`
3. TypeScript types: `types/app_import_mission_payload_v0_2.ts`
4. Validator script: `scripts/validate_alpha_mission_delivery_v0_2.py`
5. Golden approved fixtures: `fixtures/golden/approved_app_import_candidates_v0_2.json`
6. Golden revise/reject fixtures: `fixtures/golden/revise_needed_v0_2.json`, `fixtures/golden/rejected_v0_2.json`
7. Validation report: `reports/alpha_mission_delivery_validation_report_v0_2.*`
8. App-import readiness report: `reports/app_wiring_readiness_report_v0_2.md`
9. Backend endpoint contract: `backend/generate_first_mission_batch_endpoint_contract_v0_2.md`
10. App-import status model: `app_import_readiness_status_model_v0_2.md`

## Commands

```bash
python3 scripts/build_alpha_mission_delivery_v0_2.py
python3 scripts/validate_alpha_mission_delivery_v0_2.py
```

## Recommended Next Codex Dispatch

Implement the app-side local fixture import adapter behind a dev/debug flag, reconcile candidate/unresolved MusicKit resolution semantics, and run a tiny route-card/playback smoke against the approved app-import candidates after Apple Music ID resolution.
"""


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def create_negative_fixtures(example: dict[str, Any]) -> dict[str, Any]:
    negative_dir = OUT / "fixtures/negative"
    negative_dir.mkdir(parents=True, exist_ok=True)
    fixtures: dict[str, Any] = {}

    def clone(name: str) -> dict[str, Any]:
        item = copy.deepcopy(example)
        item["mission_id"] = f"negative-{name}"
        return item

    hidden = clone("constructor-input-hidden-reaction-labels")
    hidden["route"][0]["hidden_oracle_reaction"] = "love"
    fixtures["constructor_input_hidden_reaction_labels_v0_2.json"] = hidden

    selector = {
        "selector_output_id": "negative-selector-output-hidden-reaction-labels",
        "ranked_opportunities": [{"opportunity_id": "bad", "hidden_oracle_reaction": "love"}],
    }
    fixtures["selector_output_hidden_reaction_labels_v0_2.json"] = selector

    prod = clone("production-generation-true")
    prod["runtime_flags"]["production_mission_generation_allowed"] = True
    fixtures["pack_production_generation_true_v0_2.json"] = prod

    copy_fixture = clone("final-mission-copy")
    copy_fixture["final_mission_copy"] = "Listen to this final production mission copy."
    fixtures["pack_final_mission_copy_v0_2.json"] = copy_fixture

    no_source = clone("missing-source-opportunity-refs")
    no_source["source_trace"]["source_opportunity_refs"] = []
    fixtures["pack_missing_source_opportunity_refs_v0_2.json"] = no_source

    missing_why = clone("song-missing-why-in-route")
    missing_why["route"][0]["why_in_route"] = ""
    fixtures["pack_song_missing_why_in_route_v0_2.json"] = missing_why

    unresolved_ready = clone("unresolved-app-ready")
    unresolved_ready["app_import_status"] = "app_import_ready"
    unresolved_ready["route"][0]["resolution_status"] = "unresolved"
    unresolved_ready["route"][0]["canonical_song_id"] = None
    fixtures["pack_unresolved_app_ready_v0_2.json"] = unresolved_ready

    deterministic = {
        "fixture_id": "negative-same-seed-determinism-mismatch",
        "seed": "alpha-v0-2-fixed",
        "first_run_hash": "aaa",
        "second_run_hash": "bbb",
    }
    fixtures["same_seed_determinism_mismatch_v0_2.json"] = deterministic

    for filename, data in fixtures.items():
        write_json(negative_dir / filename, data)
    return fixtures


def main() -> None:
    phase1g = load_phase1g()
    packs = phase1g["packs"]
    selected = select_golden_packs(packs)

    approved = []
    revise = []
    rejected = []
    seq = 1
    for pack in selected["approved"]:
        approved.append(convert_pack(pack, expected_class="approved_app_import_candidate", sequence_number=seq, forced_status="app_import_candidate"))
        seq += 1
    for pack in selected["revise"]:
        revise.append(convert_pack(pack, expected_class="revise_needed", sequence_number=seq, forced_status="needs_revision"))
        seq += 1
    for idx, pack in enumerate(selected["rejected"]):
        forced = None
        if idx == len(selected["rejected"]) - 1:
            forced = "unresolved_playback_item"
        rejected.append(convert_pack(pack, expected_class="rejected_product", sequence_number=seq, forced_status="rejected_product", forced_reason=forced))
        seq += 1

    fixtures = {
        "contract_version": CONTRACT_VERSION,
        "created_at": CREATED_AT,
        "source_phase": "phase1g_construction_policy_llm_review",
        "held_out_review_reactions_included": False,
        "approved_app_import_candidates": approved,
        "revise_needed": revise,
        "rejected": rejected,
    }

    contract = construction_contract()

    write_text(OUT / "README.md", README())
    write_json(OUT / "mission_construction_contract_v0_2.json", contract)
    write_text(OUT / "mission_construction_contract_v0_2.md", mission_contract_md(contract))
    write_json(OUT / "mission_construction_contract_v0_2.schema.json", contract_schema())
    write_json(OUT / "app_import_mission_payload_v0_2.schema.json", payload_schema())
    write_text(OUT / "app_import_readiness_status_model_v0_2.md", status_model_md())
    write_text(OUT / "types/app_import_mission_payload_v0_2.ts", typescript_types())
    write_text(OUT / "types/index.ts", 'export * from "./app_import_mission_payload_v0_2";\n')
    write_json(OUT / "fixtures/golden/approved_app_import_candidates_v0_2.json", approved)
    write_json(OUT / "fixtures/golden/revise_needed_v0_2.json", revise)
    write_json(OUT / "fixtures/golden/rejected_v0_2.json", rejected)
    write_json(OUT / "fixtures/golden/golden_alpha_mission_fixture_set_v0_2.json", fixtures)
    if approved:
        create_negative_fixtures(approved[0])
    write_text(OUT / "backend/generate_first_mission_batch_endpoint_contract_v0_2.md", backend_contract_md())
    write_text(OUT / "reports/app_wiring_readiness_report_v0_2.md", app_wiring_report_md())
    write_text(OUT / "reports/alpha_mission_wiring_readiness_packet_v0_2.md", readiness_packet_md(fixtures, contract))

    summary = {
        "contract_version": CONTRACT_VERSION,
        "approved_count": len(approved),
        "revise_count": len(revise),
        "rejected_count": len(rejected),
        "active_mission_types": ACTIVE_MISSION_TYPES,
        "deferred_mission_types": DEFERRED_MISSION_TYPES,
        "held_out_review_reactions_included_in_payloads": False,
        "runtime_wiring_allowed": False,
        "production_mission_generation_allowed": False,
        "canonical_graph_mutation_allowed": False,
    }
    write_json(OUT / "reports/alpha_mission_delivery_build_summary_v0_2.json", summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
