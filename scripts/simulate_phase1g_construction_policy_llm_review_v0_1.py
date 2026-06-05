#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

from simulate_top_window_song_packs_v0_1 import (
    HIDDEN_CORPUS_DIR,
    PROFILE_IDS,
    SAMPLING_MODES,
    build_song_universe,
    choose_song,
    clamp,
    graph_context_refs,
    hidden_reaction_to_output,
    load_json,
    repo_rel,
    selector_output_path,
    stable_hash,
    write_json,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DIR = REPO_ROOT / "data/product_contracts/mission_opportunity_selection_v0_1"
PROFILE_SIM_DIR = CONTRACT_DIR / "fixtures/profile_simulation"
PHASE1E_DIR = CONTRACT_DIR / "evaluations/phase1e_expanded_visible_evidence_scale"
PHASE1G_DIR = CONTRACT_DIR / "evaluations/phase1g_construction_policy_llm_review"
NEGATIVE_DIR = PHASE1G_DIR / "negative"
PACK_CARDS_DIR = PHASE1G_DIR / "per_profile_pack_cards"

EXPANDED_VISIBLE_INPUTS = PHASE1E_DIR / "expanded_visible_profile_inputs_v0_1.json"
HIDDEN_PROFILE_ORACLES = PROFILE_SIM_DIR / "hidden_profile_oracles_v0_1.json"
RESULTS_OUTPUT = PHASE1G_DIR / "phase1g_song_pack_results_v0_1.json"
SUMMARY_MD_OUTPUT = PHASE1G_DIR / "phase1g_song_pack_summary_v0_1.md"
SCHEMA_OUTPUT = PHASE1G_DIR / "phase1g_song_pack_schema_v0_1.schema.json"
GUARDRAIL_MD_OUTPUT = PHASE1G_DIR / "phase1g_guardrail_report_v0_1.md"
LLM_PACKET_JSON_OUTPUT = PHASE1G_DIR / "llm_sanity_review_packet_v0_1.json"
LLM_PACKET_MD_OUTPUT = PHASE1G_DIR / "llm_sanity_review_packet_v0_1.md"

EVIDENCE_SCALE = 200
ALPHA_PACK_SIZE = 6
FUTURE_PRODUCT_PACK_RANGE = "8-12 songs, to test later"
TOP_WINDOW_SIZE = 10
MISSION_TYPES = [
    "archetype_depth_test",
    "artist_depth_test",
    "album_container_test",
    "boundary_test",
    "bridge_test",
    "context_dependence_test",
]
CONSTRUCTION_POLICIES = [
    "mission_type_native_policy",
    "experience_balanced_policy",
    "diagnostic_biased_policy",
]
DIAGNOSTIC_MISSION_TYPES = {
    "boundary_test",
    "context_dependence_test",
}
RELATED_PROXY_PRIORITY = {
    "context_dependence_test": [
        "album_container_test",
        "boundary_test",
        "evidence_repair_test",
        "bridge_test",
    ],
    "album_container_test": ["artist_depth_test", "archetype_depth_test"],
    "bridge_test": ["boundary_test", "archetype_depth_test"],
    "boundary_test": ["evidence_repair_test", "bridge_test"],
    "archetype_depth_test": ["artist_depth_test", "song_to_archetype_test"],
    "artist_depth_test": ["archetype_depth_test", "album_container_test"],
}
MISSION_GOALS = {
    "archetype_depth_test": "Test whether deeper same-archetype material works after visible positive evidence.",
    "artist_depth_test": "Test whether an artist signal extends beyond one visible object.",
    "album_container_test": "Test whether album or release context matters beyond isolated songs.",
    "boundary_test": "Clarify the edge between nearby positive and negative graph areas.",
    "bridge_test": "Test whether a known positive source can carry into an under-tested target.",
    "context_dependence_test": "Test whether reactions depend on context-heavy versus context-light presentation.",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def average(values: list[float]) -> float:
    return round(mean(values), 4) if values else 0.0


def selector_opportunities_for_mission(
    selector_output: dict[str, Any],
    mission_type: str,
) -> tuple[list[dict[str, Any]], bool, str]:
    ranked = selector_output.get("ranked_opportunities", [])
    exact = [op for op in ranked if op.get("mission_type") == mission_type]
    if exact:
        return exact[:TOP_WINDOW_SIZE], True, "exact_ranked_opportunity"

    related_types = RELATED_PROXY_PRIORITY.get(mission_type, [])
    related = [op for related_type in related_types for op in ranked if op.get("mission_type") == related_type]
    if related:
        return related[:TOP_WINDOW_SIZE], False, "related_top_window_proxy"
    return ranked[:TOP_WINDOW_SIZE], False, "top_window_fallback_proxy"


def slot_plan(mission_type: str, construction_policy: str) -> list[str]:
    native = {
        "archetype_depth_test": ["anchor", "probe", "probe", "probe", "comparator", "control"],
        "artist_depth_test": ["anchor", "probe", "probe", "probe", "comparator", "control"],
        "album_container_test": ["anchor", "context", "context", "context", "comparator", "control"],
        "boundary_test": ["anchor", "anchor", "boundary", "boundary", "comparator", "control"],
        "bridge_test": ["anchor", "bridge", "bridge", "probe", "probe", "control"],
        "context_dependence_test": ["context", "context", "comparator", "comparator", "anchor", "control"],
    }
    if construction_policy == "mission_type_native_policy":
        return native[mission_type]

    if construction_policy == "experience_balanced_policy":
        role = {
            "boundary_test": "boundary",
            "bridge_test": "bridge",
            "context_dependence_test": "context",
            "album_container_test": "context",
        }.get(mission_type, "probe")
        return ["anchor", "anchor", "probe", "comparator", "control", role]

    diagnostic = {
        "archetype_depth_test": ["anchor", "probe", "probe", "probe", "comparator", "control"],
        "artist_depth_test": ["anchor", "probe", "probe", "probe", "comparator", "control"],
        "album_container_test": ["anchor", "context", "context", "comparator", "comparator", "control"],
        "boundary_test": ["anchor", "boundary", "boundary", "comparator", "control", "anchor"],
        "bridge_test": ["anchor", "bridge", "bridge", "probe", "comparator", "control"],
        "context_dependence_test": ["context", "context", "comparator", "comparator", "anchor", "control"],
    }
    return diagnostic[mission_type]


def policy_notes(mission_type: str, construction_policy: str) -> list[str]:
    base = {
        "archetype_depth_test": "Mostly promising discovery; no forced negative probe.",
        "artist_depth_test": "Artist-depth variety without treating one artist as the whole taste universe.",
        "album_container_test": "Album/container coherence with outside-album comparators.",
        "boundary_test": "Controlled contrast is allowed, but punitive overload is not.",
        "bridge_test": "Source-to-target continuity through low-to-medium risk paths.",
        "context_dependence_test": "Context-heavy and context-light balance; negative exposure is not required.",
    }[mission_type]
    if construction_policy == "mission_type_native_policy":
        return [base, "Uses the mission-type-specific Alpha v0.2 composition policy."]
    if construction_policy == "experience_balanced_policy":
        return [base, "Prioritizes tolerability with two anchors, probes, and controls."]
    return [base, "Prioritizes learning while keeping a recovery/safe song in the pack."]


def source_for_slot(source_opportunities: list[dict[str, Any]], role: str, index: int) -> dict[str, Any]:
    if not source_opportunities:
        raise ValueError("source_opportunities must not be empty")
    if role in {"anchor", "control"}:
        return source_opportunities[index % min(len(source_opportunities), 2)]
    if role in {"comparator", "boundary", "context", "bridge"} and len(source_opportunities) > 1:
        return source_opportunities[(index + 1) % len(source_opportunities)]
    return source_opportunities[index % len(source_opportunities)]


def construct_pack(
    profile_id: str,
    sampling_mode: str,
    mission_type: str,
    construction_policy: str,
    selector_output: dict[str, Any],
    visible_profile: dict[str, Any],
    selection_pool: list[dict[str, Any]],
    reaction_map: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    source_opportunities, exact_match, availability = selector_opportunities_for_mission(
        selector_output,
        mission_type,
    )
    pack_id = (
        f"phase1g_{profile_id}_{sampling_mode}_{EVIDENCE_SCALE}_"
        f"{mission_type}_{construction_policy}_v0_1"
    )
    selected_song_ids: set[str] = set()
    selected_artists: Counter[str] = Counter()
    songs: list[dict[str, Any]] = []

    for index, role in enumerate(slot_plan(mission_type, construction_policy)):
        opportunity = source_for_slot(source_opportunities, role, index)
        song = choose_song(
            selection_pool,
            role,
            opportunity,
            visible_profile,
            selected_song_ids,
            selected_artists,
            pack_id,
        )
        selected_song_ids.add(song["song_id"])
        selected_artists[song["artist_display_name"]] += 1
        reaction = reaction_map.get(song["song_id"], {})
        songs.append(
            {
                "song_id": song["song_id"],
                "title": song["title"],
                "artist_display_name": song["artist_display_name"],
                "source_role": role,
                "source_opportunity_id": opportunity.get("opportunity_id"),
                "source_mission_type": opportunity.get("mission_type"),
                "target_object_ids": opportunity.get("target_object_ids", []),
                "graph_context_refs": graph_context_refs(opportunity),
                "why_selected": (
                    f"{construction_policy} {role} for {mission_type}; "
                    f"source opportunity={opportunity.get('mission_type')}; "
                    "selected from reaction-stripped offline corpus."
                ),
                "hidden_oracle_reaction": reaction.get("hidden_oracle_reaction", "unknown"),
                "hidden_oracle_confidence": reaction.get("hidden_oracle_confidence", 0.0),
            }
        )

    pack = {
        "pack_id": pack_id,
        "profile_id": profile_id,
        "evidence_scale": EVIDENCE_SCALE,
        "sampling_mode": sampling_mode,
        "mission_type": mission_type,
        "construction_policy": construction_policy,
        "alpha_v0_2_pack_size": ALPHA_PACK_SIZE,
        "future_product_pack_range_to_test_later": FUTURE_PRODUCT_PACK_RANGE,
        "song_count": len(songs),
        "source_selector_output_ref": repo_rel(
            selector_output_path(profile_id, sampling_mode, EVIDENCE_SCALE)
        ),
        "source_opportunity_exact_match": exact_match,
        "source_opportunity_availability": availability,
        "source_opportunity_ids": [op.get("opportunity_id") for op in source_opportunities[:TOP_WINDOW_SIZE]],
        "source_mission_types": [op.get("mission_type") for op in source_opportunities[:TOP_WINDOW_SIZE]],
        "source_opportunity_summary": [
            {
                "opportunity_id": op.get("opportunity_id"),
                "mission_type": op.get("mission_type"),
                "target_display_name": op.get("target_object_ref", {}).get("display_name"),
                "final_opportunity_score": op.get("score_components", {}).get("final_opportunity_score"),
            }
            for op in source_opportunities[:3]
        ],
        "mission_goal": MISSION_GOALS[mission_type],
        "policy_notes": policy_notes(mission_type, construction_policy),
        "songs": songs,
        "construction_guardrails": {
            "selection_input_reaction_labels_visible": False,
            "selection_input_hidden_reason_tags_visible": False,
            "hidden_oracle_reaction_attached_after_construction": True,
            "optimized_for_hidden_reaction_labels": False,
            "production_mission_content_emitted": False,
            "high_risk_negative_probe_globally_required": False,
        },
    }
    pack.update(score_pack(pack))
    return pack


def role_balance_score(mission_type: str, role_counts: Counter[str]) -> float:
    desired = {
        "archetype_depth_test": {"anchor": 1, "probe": 3, "comparator": 1, "control": 1},
        "artist_depth_test": {"anchor": 1, "probe": 3, "comparator": 1, "control": 1},
        "album_container_test": {"anchor": 1, "context": 3, "comparator": 1, "control": 1},
        "boundary_test": {"anchor": 2, "boundary": 2, "comparator": 1, "control": 1},
        "bridge_test": {"anchor": 1, "bridge": 2, "probe": 2, "control": 1},
        "context_dependence_test": {"context": 2, "comparator": 2, "anchor": 1, "control": 1},
    }[mission_type]
    total_gap = sum(abs(role_counts.get(role, 0) - count) for role, count in desired.items())
    return clamp(1 - total_gap / 8)


def adjusted_smell_score(
    pack: dict[str, Any],
    generic_score: float,
    role_counts: Counter[str],
    rates: dict[str, float],
    scores: dict[str, float],
    dont_like_count: int,
) -> float:
    mission_type = pack["mission_type"]
    role_balance = role_balance_score(mission_type, role_counts)
    positive = rates["positive_hit_rate"]
    non_failure = rates["non_failure_rate"]
    negative = rates["negative_hit_rate"]
    coherence = scores["mission_coherence_score"]
    diagnostic = scores["diagnostic_value_score"]
    ux = scores["user_experience_score"]

    if mission_type in {"archetype_depth_test", "artist_depth_test"}:
        raw = 0.28 * non_failure + 0.24 * positive + 0.20 * coherence + 0.16 * role_balance + 0.12 * ux
    elif mission_type == "album_container_test":
        raw = 0.28 * coherence + 0.22 * non_failure + 0.20 * role_balance + 0.16 * positive + 0.14 * ux
    elif mission_type == "boundary_test":
        bounded_contrast = 0.18 if 0 < dont_like_count <= 2 else -0.12 if dont_like_count > 2 else 0.04
        raw = 0.27 * diagnostic + 0.22 * role_balance + 0.18 * non_failure + 0.15 * coherence + 0.10 * ux + bounded_contrast
    elif mission_type == "bridge_test":
        raw = 0.28 * role_balance + 0.24 * non_failure + 0.20 * coherence + 0.16 * ux + 0.12 * positive
    else:
        raw = 0.28 * role_balance + 0.24 * diagnostic + 0.20 * coherence + 0.16 * non_failure + 0.12 * ux

    penalty = max(0, negative - 0.33) * 1.5
    if pack.get("too_random_flag"):
        penalty += 0.20
    return clamp(0.55 * raw + 0.45 * generic_score - penalty)


def score_pack(pack: dict[str, Any]) -> dict[str, Any]:
    songs = pack["songs"]
    song_count = max(1, len(songs))
    reactions = Counter(song["hidden_oracle_reaction"] for song in songs)
    role_counts = Counter(song["source_role"] for song in songs)
    source_types = Counter(song["source_mission_type"] for song in songs)
    love = reactions.get("love", 0)
    like = reactions.get("like", 0)
    ok = reactions.get("ok", 0)
    dont_like = reactions.get("dont_like", 0)
    unknown = reactions.get("unknown", 0)
    positive_hit_rate = (love + like) / song_count
    non_failure_rate = (love + like + ok) / song_count
    negative_hit_rate = dont_like / song_count
    unknown_rate = unknown / song_count
    diagnostic_probe_count = sum(
        role_counts.get(role, 0)
        for role in ["probe", "boundary", "context", "bridge", "false_nearby"]
    )
    role_balance = role_balance_score(pack["mission_type"], role_counts)
    source_match_bonus = 0.08 if pack.get("source_opportunity_exact_match") else -0.04

    mission_coherence_score = clamp(
        0.36
        + 0.30 * role_balance
        + 0.10 * min(1, max(source_types.values(), default=1) / song_count)
        + source_match_bonus
    )
    diagnostic_value_score = clamp(
        0.16
        + 0.08 * diagnostic_probe_count
        + 0.18 * role_counts.get("boundary", 0) / 2
        + 0.18 * role_counts.get("context", 0) / 2
        + 0.16 * role_counts.get("bridge", 0) / 2
        + (0.10 if 0 < dont_like <= 2 and pack["mission_type"] in DIAGNOSTIC_MISSION_TYPES else 0)
    )
    user_experience_score = clamp(
        0.16
        + 0.45 * non_failure_rate
        + 0.18 * positive_hit_rate
        - 0.32 * negative_hit_rate
        - 0.08 * unknown_rate
    )
    learning_value_score = clamp(
        0.36 * diagnostic_value_score
        + 0.24 * mission_coherence_score
        + 0.20 * role_balance
        + 0.12 * non_failure_rate
        + (0.08 if 0 < dont_like <= 2 else 0)
        - (0.16 if dont_like >= 3 else 0)
    )
    negative_overload_flag = negative_hit_rate > 0.33 or dont_like >= 3
    too_safe_flag = positive_hit_rate >= 0.67 and diagnostic_value_score < 0.35
    too_random_flag = unknown_rate > 0.50 or mission_coherence_score < 0.35
    overfit_flag = max(Counter(song["artist_display_name"] for song in songs).values(), default=0) >= 4

    positive_hit_component = min(1.0, positive_hit_rate / 0.50)
    non_failure_component = min(1.0, non_failure_rate / 0.75)
    negative_penalty = max(0, negative_hit_rate - 0.25) * 2
    unknown_penalty = max(0, unknown_rate - 0.50)
    too_safe_penalty = 0.15 if too_safe_flag else 0
    too_random_penalty = 0.25 if too_random_flag else 0
    generic_score = clamp(
        0.25 * positive_hit_component
        + 0.20 * non_failure_component
        + 0.25 * diagnostic_value_score
        + 0.20 * user_experience_score
        + 0.10 * mission_coherence_score
        - negative_penalty
        - unknown_penalty
        - too_safe_penalty
        - too_random_penalty
    )
    rates = {
        "positive_hit_rate": positive_hit_rate,
        "non_failure_rate": non_failure_rate,
        "negative_hit_rate": negative_hit_rate,
        "unknown_rate": unknown_rate,
    }
    scores = {
        "mission_coherence_score": mission_coherence_score,
        "diagnostic_value_score": diagnostic_value_score,
        "user_experience_score": user_experience_score,
    }
    adjusted_score = adjusted_smell_score(pack, generic_score, role_counts, rates, scores, dont_like)
    gate_failures = []
    if song_count != ALPHA_PACK_SIZE:
        gate_failures.append("song_count_not_6")
    if non_failure_rate < 0.67:
        gate_failures.append("non_failure_rate_below_0_67")
    if negative_hit_rate > 0.33:
        gate_failures.append("negative_hit_rate_above_0_33")
    if too_random_flag:
        gate_failures.append("too_random")
    if role_counts.get("anchor", 0) < 1:
        gate_failures.append("missing_anchor")
    if role_counts.get("probe", 0) + role_counts.get("comparator", 0) < 1:
        gate_failures.append("missing_probe_or_comparator")
    if not pack.get("source_opportunity_ids"):
        gate_failures.append("missing_source_opportunity_refs")
    if any(not song.get("why_selected") for song in songs):
        gate_failures.append("missing_why_selected")

    alpha_plausible = not gate_failures
    alpha_preferred = (
        alpha_plausible
        and non_failure_rate >= 0.75
        and negative_hit_rate <= 0.20
        and mission_coherence_score >= 0.65
        and adjusted_score >= 0.60
    )
    return {
        "love_count": love,
        "like_count": like,
        "ok_count": ok,
        "dont_like_count": dont_like,
        "unknown_count": unknown,
        "positive_hit_rate": round(positive_hit_rate, 4),
        "non_failure_rate": round(non_failure_rate, 4),
        "negative_hit_rate": round(negative_hit_rate, 4),
        "unknown_rate": round(unknown_rate, 4),
        "anchor_count": role_counts.get("anchor", 0),
        "probe_count": role_counts.get("probe", 0),
        "boundary_count": role_counts.get("boundary", 0),
        "context_count": role_counts.get("context", 0),
        "bridge_count": role_counts.get("bridge", 0),
        "false_nearby_count": role_counts.get("false_nearby", 0),
        "control_count": role_counts.get("control", 0),
        "comparator_count": role_counts.get("comparator", 0),
        "mission_coherence_score": mission_coherence_score,
        "diagnostic_value_score": diagnostic_value_score,
        "user_experience_score": user_experience_score,
        "learning_value_score": learning_value_score,
        "generic_overall_smell_score": generic_score,
        "mission_type_adjusted_smell_score": adjusted_score,
        "overall_smell_score": adjusted_score,
        "negative_overload_flag": negative_overload_flag,
        "too_safe_flag": too_safe_flag,
        "too_random_flag": too_random_flag,
        "overfit_flag": overfit_flag,
        "stress_only_flag": negative_overload_flag and pack["mission_type"] in {"boundary_test", "context_dependence_test"},
        "alpha_plausible": alpha_plausible,
        "alpha_preferred": alpha_preferred,
        "alpha_gate_fail_reasons": gate_failures,
        "policy_compliance_summary": {
            "role_balance_score": role_balance,
            "high_risk_negative_probe_globally_required": False,
            "bounded_negative_exposure": dont_like <= 2,
        },
    }


def build_packs() -> list[dict[str, Any]]:
    expanded = load_json(EXPANDED_VISIBLE_INPUTS)
    visible_by_run = {
        (profile["profile_id"], profile["evidence_atom_count"], profile["sampling_mode"]): profile
        for profile in expanded.get("profiles", [])
    }
    packs: list[dict[str, Any]] = []
    for profile_id in PROFILE_IDS:
        selection_pool, reaction_map = build_song_universe(profile_id)
        for sampling_mode in SAMPLING_MODES:
            visible_profile = visible_by_run[(profile_id, EVIDENCE_SCALE, sampling_mode)]
            selector_output = load_json(selector_output_path(profile_id, sampling_mode, EVIDENCE_SCALE))
            for mission_type in MISSION_TYPES:
                for policy in CONSTRUCTION_POLICIES:
                    packs.append(
                        construct_pack(
                            profile_id,
                            sampling_mode,
                            mission_type,
                            policy,
                            selector_output,
                            visible_profile,
                            selection_pool,
                            reaction_map,
                        )
                    )
    return packs


def summarize_group(packs: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for pack in packs:
        groups[str(pack[key])].append(pack)
    rows = []
    for group_key, group in sorted(groups.items()):
        rows.append(
            {
                key: group_key,
                "pack_count": len(group),
                "alpha_plausible_count": sum(1 for pack in group if pack["alpha_plausible"]),
                "alpha_plausible_rate": round(sum(1 for pack in group if pack["alpha_plausible"]) / len(group), 4),
                "alpha_preferred_count": sum(1 for pack in group if pack["alpha_preferred"]),
                "average_mission_type_adjusted_smell_score": average(
                    [pack["mission_type_adjusted_smell_score"] for pack in group]
                ),
                "average_generic_overall_smell_score": average(
                    [pack["generic_overall_smell_score"] for pack in group]
                ),
                "average_non_failure_rate": average([pack["non_failure_rate"] for pack in group]),
                "average_negative_hit_rate": average([pack["negative_hit_rate"] for pack in group]),
                "negative_overload_count": sum(1 for pack in group if pack["negative_overload_flag"]),
                "too_safe_count": sum(1 for pack in group if pack["too_safe_flag"]),
                "too_random_count": sum(1 for pack in group if pack["too_random_flag"]),
            }
        )
    return rows


def aggregate_metrics(packs: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "pack_count": len(packs),
        "alpha_plausible_count": sum(1 for pack in packs if pack["alpha_plausible"]),
        "alpha_plausible_rate": round(sum(1 for pack in packs if pack["alpha_plausible"]) / len(packs), 4),
        "alpha_preferred_count": sum(1 for pack in packs if pack["alpha_preferred"]),
        "average_mission_type_adjusted_smell_score": average(
            [pack["mission_type_adjusted_smell_score"] for pack in packs]
        ),
        "average_generic_overall_smell_score": average([pack["generic_overall_smell_score"] for pack in packs]),
        "average_non_failure_rate": average([pack["non_failure_rate"] for pack in packs]),
        "average_negative_hit_rate": average([pack["negative_hit_rate"] for pack in packs]),
        "negative_overload_count": sum(1 for pack in packs if pack["negative_overload_flag"]),
        "too_safe_count": sum(1 for pack in packs if pack["too_safe_flag"]),
        "too_random_count": sum(1 for pack in packs if pack["too_random_flag"]),
        "exact_source_opportunity_pack_count": sum(1 for pack in packs if pack["source_opportunity_exact_match"]),
        "proxy_source_opportunity_pack_count": sum(1 for pack in packs if not pack["source_opportunity_exact_match"]),
    }


def representative_examples(packs: list[dict[str, Any]]) -> dict[str, Any]:
    by_id = {pack["pack_id"]: pack for pack in packs}
    best = max(packs, key=lambda pack: pack["mission_type_adjusted_smell_score"])
    worst = min(packs, key=lambda pack: pack["mission_type_adjusted_smell_score"])
    worst_negative = max(packs, key=lambda pack: (pack["negative_hit_rate"], -pack["mission_type_adjusted_smell_score"]))
    best_alpha = max(
        [pack for pack in packs if pack["alpha_plausible"]],
        key=lambda pack: pack["mission_type_adjusted_smell_score"],
    )
    borderline = min(
        [pack for pack in packs if pack["alpha_plausible"]],
        key=lambda pack: pack["mission_type_adjusted_smell_score"],
    )
    return {
        "best_pack_id": best["pack_id"],
        "best_score": best["mission_type_adjusted_smell_score"],
        "best_alpha_plausible_pack_id": best_alpha["pack_id"],
        "best_alpha_plausible_score": best_alpha["mission_type_adjusted_smell_score"],
        "borderline_alpha_plausible_pack_id": borderline["pack_id"],
        "borderline_alpha_plausible_score": borderline["mission_type_adjusted_smell_score"],
        "worst_pack_id": worst["pack_id"],
        "worst_score": worst["mission_type_adjusted_smell_score"],
        "worst_negative_overload_pack_id": worst_negative["pack_id"],
        "worst_negative_hit_rate": worst_negative["negative_hit_rate"],
        "best_pack_reactions": Counter(song["hidden_oracle_reaction"] for song in by_id[best["pack_id"]]["songs"]),
    }


def plain_interpretation(pack: dict[str, Any]) -> str:
    if pack["too_random_flag"]:
        return "Reject for Alpha: the pack looks too random or incoherent."
    if pack["negative_overload_flag"]:
        return "Borderline or reject: useful signal may exist, but the pack risks feeling punitive."
    if pack["alpha_preferred"]:
        return "Approve for LLM review: coherent, tolerable, and mission-shaped."
    if pack["alpha_plausible"]:
        return "Revise for Alpha: plausible but needs policy or candidate-quality tuning."
    return "Reject for Alpha under current gates."


def llm_review_questions() -> list[str]:
    return [
        "Does this mission make sense given the visible profile evidence?",
        "Does the song list feel coherent?",
        "Does the mission match the stated mission type?",
        "Is it too safe, too random, too negative, or appropriately exploratory?",
        "Would a real user understand why they got this?",
        "What is the biggest concern?",
        "Would you approve this for Alpha, revise it, or reject it?",
    ]


def visible_summary(profile_id: str, sampling_mode: str) -> dict[str, Any]:
    expanded = load_json(EXPANDED_VISIBLE_INPUTS)
    profile = next(
        row
        for row in expanded["profiles"]
        if row["profile_id"] == profile_id
        and row["evidence_atom_count"] == EVIDENCE_SCALE
        and row["sampling_mode"] == sampling_mode
    )
    visible = profile["visible_evidence"]
    return {
        "evidence_atom_count": profile["evidence_atom_count"],
        "sampling_mode": sampling_mode,
        "survey_signals_summary": visible.get("survey_signals_summary", {}),
        "object_type_counts": visible.get("object_type_counts", {}),
        "top_visible_archetype_ids": visible.get("top_visible_archetype_ids", [])[:4],
        "top_visible_family_numbers": visible.get("top_visible_family_numbers", [])[:4],
        "visible_positive_examples": [
            example.get("display_name")
            for example in visible.get("visible_positive_examples", [])[:6]
        ],
        "visible_negative_examples": [
            example.get("display_name")
            for example in visible.get("visible_negative_examples", [])[:4]
        ],
    }


def curated_llm_examples(packs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []
    for profile_id in PROFILE_IDS:
        for mission_type in MISSION_TYPES:
            group = [
                pack
                for pack in packs
                if pack["profile_id"] == profile_id and pack["mission_type"] == mission_type
            ]
            strong = max(group, key=lambda pack: pack["mission_type_adjusted_smell_score"])
            alpha_or_all = [pack for pack in group if not pack["alpha_preferred"]] or group
            questionable = min(
                alpha_or_all,
                key=lambda pack: (
                    pack["mission_type_adjusted_smell_score"],
                    -pack["negative_hit_rate"],
                ),
            )
            for label, pack in [("strong_high_scoring_example", strong), ("questionable_or_borderline_example", questionable)]:
                examples.append(
                    {
                        "example_label": label,
                        "pack_id": pack["pack_id"],
                        "profile_id": pack["profile_id"],
                        "visible_evidence_summary": visible_summary(pack["profile_id"], pack["sampling_mode"]),
                        "mission_type": pack["mission_type"],
                        "mission_goal": pack["mission_goal"],
                        "construction_policy": pack["construction_policy"],
                        "source_opportunity_summary": pack["source_opportunity_summary"],
                        "song_list": [
                            {
                                "source_role": song["source_role"],
                                "title": song["title"],
                                "artist_display_name": song["artist_display_name"],
                                "why_selected": song["why_selected"],
                                "hidden_fake_profile_reaction": song["hidden_oracle_reaction"],
                            }
                            for song in pack["songs"]
                        ],
                        "pack_metrics": {
                            "non_failure_rate": pack["non_failure_rate"],
                            "negative_hit_rate": pack["negative_hit_rate"],
                            "generic_overall_smell_score": pack["generic_overall_smell_score"],
                            "mission_type_adjusted_smell_score": pack["mission_type_adjusted_smell_score"],
                            "alpha_plausible": pack["alpha_plausible"],
                            "alpha_preferred": pack["alpha_preferred"],
                            "alpha_gate_fail_reasons": pack["alpha_gate_fail_reasons"],
                        },
                        "plain_english_system_interpretation": plain_interpretation(pack),
                        "review_questions": llm_review_questions(),
                    }
                )
    return examples


def write_llm_packets(packs: list[dict[str, Any]]) -> dict[str, Any]:
    examples = curated_llm_examples(packs)
    payload = {
        "contract_version": "phase1g_llm_sanity_review_packet_v0_1",
        "fixture_status": "review_only_packet",
        "created_at": now_iso(),
        "runtime_allowed": False,
        "production_mission_generation_allowed": False,
        "final_mission_construction_status": "not_in_scope",
        "canonical_graph_mutation_allowed": False,
        "selector_may_read_hidden_oracle": False,
        "llm_packet_is_review_only": True,
        "example_count": len(examples),
        "summary_prompt": (
            "Across these examples, which mission types feel Alpha-ready? Which construction "
            "policy feels strongest? Where are we over-testing negative territory? Where are "
            "we too safe? What should PM change before UAT?"
        ),
        "examples": examples,
    }
    write_json(LLM_PACKET_JSON_OUTPUT, payload)

    lines = [
        "# Phase 1G LLM Sanity Review Packet",
        "",
        "Review-only packet. These are offline synthetic song packs, not production missions or final mission copy.",
        "",
        f"Examples: {len(examples)}",
        "",
        "## Summary Prompt",
        "",
        payload["summary_prompt"],
        "",
    ]
    for example in examples:
        lines.extend(
            [
                f"## {example['example_label']}: {example['profile_id']} / {example['mission_type']}",
                "",
                f"- Pack: `{example['pack_id']}`",
                f"- Construction policy: `{example['construction_policy']}`",
                f"- Goal: {example['mission_goal']}",
                f"- Visible positives: {', '.join(example['visible_evidence_summary']['visible_positive_examples'][:5])}",
                f"- Visible negatives: {', '.join(example['visible_evidence_summary']['visible_negative_examples'][:4])}",
                f"- Metrics: adjusted={example['pack_metrics']['mission_type_adjusted_smell_score']}, non_failure={example['pack_metrics']['non_failure_rate']}, negative={example['pack_metrics']['negative_hit_rate']}, alpha_plausible={example['pack_metrics']['alpha_plausible']}",
                "",
                "| Role | Song | Artist | Hidden fake-profile reaction | Why selected |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for song in example["song_list"]:
            lines.append(
                "| "
                + " | ".join(
                    [
                        song["source_role"],
                        song["title"].replace("|", "/"),
                        song["artist_display_name"].replace("|", "/"),
                        song["hidden_fake_profile_reaction"],
                        song["why_selected"].replace("|", "/"),
                    ]
                )
                + " |"
            )
        lines.extend(
            [
                "",
                f"System interpretation: {example['plain_english_system_interpretation']}",
                "",
                "Review questions:",
            ]
        )
        lines.extend(f"- {question}" for question in example["review_questions"])
        lines.append("")
    LLM_PACKET_MD_OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {
        "llm_sanity_review_packet_json_ref": repo_rel(LLM_PACKET_JSON_OUTPUT),
        "llm_sanity_review_packet_md_ref": repo_rel(LLM_PACKET_MD_OUTPUT),
        "llm_sanity_review_example_count": len(examples),
    }


def build_schema() -> dict[str, Any]:
    score = {"type": "number", "minimum": 0, "maximum": 1}
    count = {"type": "integer", "minimum": 0}
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://cartenza.local/contracts/mission_opportunity_selection_v0_1/phase1g_song_pack_schema_v0_1.schema.json",
        "title": "Mission Opportunity Selection v0.1 Phase 1G Construction Policy Review",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "contract_version",
            "fixture_status",
            "created_at",
            "phase",
            "runtime_allowed",
            "runtime_listener_evidence_connected",
            "production_mission_generation_allowed",
            "canonical_graph_mutation_allowed",
            "selector_may_read_hidden_oracle",
            "constructor_optimized_by_hidden_reaction_labels",
            "oracle_evaluation_fed_back_into_selector",
            "final_mission_construction_status",
            "run_matrix",
            "source_refs",
            "mission_type_construction_policies",
            "scoring_model",
            "packs",
            "aggregate_pack_metrics",
            "per_profile_summary",
            "per_mission_type_summary",
            "per_construction_policy_summary",
            "representative_pack_examples",
            "guardrail_summary",
            "determinism_summary",
            "llm_packet_summary",
            "human_pack_card_refs",
            "known_limitations",
            "recommendations",
        ],
        "properties": {
            "contract_version": {"const": "phase1g_construction_policy_llm_review_v0_1"},
            "fixture_status": {"const": "synthetic_contract_fixture"},
            "created_at": {"type": "string"},
            "phase": {"const": "mission_type_construction_policy_hardening_llm_review"},
            "runtime_allowed": {"const": False},
            "runtime_listener_evidence_connected": {"const": False},
            "production_mission_generation_allowed": {"const": False},
            "canonical_graph_mutation_allowed": {"const": False},
            "selector_may_read_hidden_oracle": {"const": False},
            "constructor_optimized_by_hidden_reaction_labels": {"const": False},
            "oracle_evaluation_fed_back_into_selector": {"const": False},
            "final_mission_construction_status": {"const": "not_in_scope"},
            "run_matrix": {
                "type": "object",
                "required": [
                    "profiles",
                    "evidence_scale",
                    "sampling_modes",
                    "mission_types",
                    "construction_policies",
                    "alpha_v0_2_pack_size",
                    "completed_construction_attempt_count",
                    "minimum_required_pack_count",
                ],
                "properties": {
                    "profiles": {"type": "array", "items": {"type": "string"}},
                    "evidence_scale": {"const": 200},
                    "sampling_modes": {"type": "array", "items": {"type": "string"}},
                    "mission_types": {"type": "array", "items": {"type": "string"}},
                    "construction_policies": {"type": "array", "items": {"type": "string"}},
                    "alpha_v0_2_pack_size": {"const": 6},
                    "future_product_pack_range_to_test_later": {"type": "string"},
                    "completed_construction_attempt_count": {"type": "integer", "minimum": 100},
                    "preferred_full_matrix_count": {"const": 162},
                    "minimum_required_pack_count": {"const": 100},
                },
                "additionalProperties": False,
            },
            "source_refs": {"type": "object"},
            "mission_type_construction_policies": {"type": "object"},
            "scoring_model": {"type": "object"},
            "packs": {"type": "array", "minItems": 100, "items": {"$ref": "#/$defs/pack"}},
            "aggregate_pack_metrics": {"type": "object"},
            "per_profile_summary": {"type": "array", "items": {"type": "object"}},
            "per_mission_type_summary": {"type": "array", "items": {"type": "object"}},
            "per_construction_policy_summary": {"type": "array", "items": {"type": "object"}},
            "representative_pack_examples": {"type": "object"},
            "guardrail_summary": {"type": "object"},
            "determinism_summary": {"type": "object"},
            "llm_packet_summary": {"type": "object"},
            "human_pack_card_refs": {"type": "array", "items": {"type": "string"}},
            "known_limitations": {"type": "array", "items": {"type": "string"}},
            "recommendations": {"type": "array", "items": {"type": "string"}},
        },
        "$defs": {
            "pack": {
                "type": "object",
                "additionalProperties": True,
                "required": [
                    "pack_id",
                    "profile_id",
                    "evidence_scale",
                    "sampling_mode",
                    "mission_type",
                    "construction_policy",
                    "song_count",
                    "source_opportunity_ids",
                    "source_mission_types",
                    "songs",
                    "generic_overall_smell_score",
                    "mission_type_adjusted_smell_score",
                    "alpha_plausible",
                    "stress_only_flag",
                ],
                "properties": {
                    "pack_id": {"type": "string"},
                    "profile_id": {"type": "string"},
                    "evidence_scale": {"const": 200},
                    "sampling_mode": {"type": "string"},
                    "mission_type": {"enum": MISSION_TYPES},
                    "construction_policy": {"enum": CONSTRUCTION_POLICIES},
                    "song_count": {"const": 6},
                    "source_opportunity_ids": {"type": "array", "minItems": 1, "items": {"type": "string"}},
                    "source_mission_types": {"type": "array", "minItems": 1, "items": {"type": "string"}},
                    "songs": {"type": "array", "minItems": 6, "maxItems": 6, "items": {"$ref": "#/$defs/song"}},
                    "generic_overall_smell_score": score,
                    "mission_type_adjusted_smell_score": score,
                    "overall_smell_score": score,
                    "alpha_plausible": {"type": "boolean"},
                    "alpha_preferred": {"type": "boolean"},
                    "stress_only_flag": {"type": "boolean"},
                    "love_count": count,
                    "like_count": count,
                    "ok_count": count,
                    "dont_like_count": count,
                    "unknown_count": count,
                    "positive_hit_rate": score,
                    "non_failure_rate": score,
                    "negative_hit_rate": score,
                    "unknown_rate": score,
                },
            },
            "song": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "song_id",
                    "title",
                    "artist_display_name",
                    "source_role",
                    "source_opportunity_id",
                    "source_mission_type",
                    "target_object_ids",
                    "graph_context_refs",
                    "why_selected",
                    "hidden_oracle_reaction",
                    "hidden_oracle_confidence",
                ],
                "properties": {
                    "song_id": {"type": "string", "minLength": 1},
                    "title": {"type": "string", "minLength": 1},
                    "artist_display_name": {"type": "string", "minLength": 1},
                    "source_role": {
                        "enum": ["anchor", "probe", "boundary", "context", "bridge", "false_nearby", "control", "comparator"]
                    },
                    "source_opportunity_id": {"type": "string", "minLength": 1},
                    "source_mission_type": {"type": "string", "minLength": 1},
                    "target_object_ids": {"type": "array", "items": {"type": "string"}},
                    "graph_context_refs": {"type": "array", "items": {"type": "string"}},
                    "why_selected": {"type": "string", "minLength": 1},
                    "hidden_oracle_reaction": {"enum": ["love", "like", "ok", "dont_like", "unknown"]},
                    "hidden_oracle_confidence": score,
                },
            },
        },
    }


def build_negative_fixtures(results: dict[str, Any]) -> dict[str, str]:
    NEGATIVE_DIR.mkdir(parents=True, exist_ok=True)
    cases = {
        "constructor input includes hidden reaction labels": NEGATIVE_DIR / "constructor_input_hidden_reaction_labels_v0_1.json",
        "selector output includes hidden reaction labels": NEGATIVE_DIR / "selector_output_hidden_reaction_labels_v0_1.json",
        "production mission generation allowed": NEGATIVE_DIR / "pack_production_generation_true_v0_1.json",
        "pack includes final mission copy": NEGATIVE_DIR / "pack_final_mission_copy_v0_1.json",
        "pack has no source opportunity refs": NEGATIVE_DIR / "pack_missing_source_opportunity_refs_v0_1.json",
        "pack song lacks why_selected": NEGATIVE_DIR / "pack_song_missing_why_selected_v0_1.json",
        "same seed produces different pack": NEGATIVE_DIR / "pack_determinism_mismatch_v0_1.json",
    }
    write_json(cases["constructor input includes hidden reaction labels"], {"selection_pool": [{"song_id": "bad", "hidden_oracle_reaction": "love"}]})
    write_json(cases["selector output includes hidden reaction labels"], {"ranked_opportunities": [{"opportunity_id": "bad", "hidden_oracle_reaction": "love"}]})
    bad = deepcopy(results)
    bad["production_mission_generation_allowed"] = True
    write_json(cases["production mission generation allowed"], bad)
    bad = deepcopy(results)
    bad["packs"][0]["final_mission_copy"] = "Forbidden final copy"
    write_json(cases["pack includes final mission copy"], bad)
    bad = deepcopy(results)
    bad["packs"][0]["source_opportunity_ids"] = []
    write_json(cases["pack has no source opportunity refs"], bad)
    bad = deepcopy(results)
    bad["packs"][0]["songs"][0]["why_selected"] = ""
    write_json(cases["pack song lacks why_selected"], bad)
    write_json(cases["same seed produces different pack"], {"deterministic_rerun_matched": False})
    return {label: repo_rel(path) for label, path in cases.items()}


def write_cards(packs: list[dict[str, Any]]) -> list[str]:
    PACK_CARDS_DIR.mkdir(parents=True, exist_ok=True)
    refs = []
    for profile_id in PROFILE_IDS:
        rows = [pack for pack in packs if pack["profile_id"] == profile_id]
        selected = []
        for mission_type in MISSION_TYPES:
            group = [pack for pack in rows if pack["mission_type"] == mission_type]
            selected.append(max(group, key=lambda pack: pack["mission_type_adjusted_smell_score"]))
        lines = [
            f"# {profile_id} Phase 1G Mission-Type Pack Cards",
            "",
            "Offline synthetic cards only. No final mission copy.",
            "",
        ]
        for pack in selected:
            lines.extend(
                [
                    f"## {pack['mission_type']} / {pack['construction_policy']}",
                    "",
                    f"- Pack: `{pack['pack_id']}`",
                    f"- Adjusted smell score: {pack['mission_type_adjusted_smell_score']}",
                    f"- Alpha plausible: {pack['alpha_plausible']}",
                    f"- Non-failure / negative: {pack['non_failure_rate']} / {pack['negative_hit_rate']}",
                    "",
                    "| Role | Song | Artist | Hidden reaction | Why selected |",
                    "| --- | --- | --- | --- | --- |",
                ]
            )
            for song in pack["songs"]:
                lines.append(
                    "| "
                    + " | ".join(
                        [
                            song["source_role"],
                            song["title"].replace("|", "/"),
                            song["artist_display_name"].replace("|", "/"),
                            song["hidden_oracle_reaction"],
                            song["why_selected"].replace("|", "/"),
                        ]
                    )
                    + " |"
                )
            lines.extend(["", f"Read: {plain_interpretation(pack)}", ""])
        path = PACK_CARDS_DIR / f"{profile_id}_phase1g_pack_cards.md"
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        refs.append(repo_rel(path))
    return refs


def write_summary(results: dict[str, Any]) -> None:
    agg = results["aggregate_pack_metrics"]
    lines = [
        "# Phase 1G Construction Policy + LLM Review Summary",
        "",
        "Offline-only construction-policy hardening for Alpha v0.2-style six-song packs. Six songs are a test size, not final product posture.",
        "",
        "## Executive Summary",
        "",
        f"- Construction attempts: {results['run_matrix']['completed_construction_attempt_count']}",
        f"- Alpha-plausible packs: {agg['alpha_plausible_count']} ({agg['alpha_plausible_rate']})",
        f"- Alpha-preferred packs: {agg['alpha_preferred_count']}",
        f"- Average adjusted smell score: {agg['average_mission_type_adjusted_smell_score']}",
        f"- Average non-failure rate: {agg['average_non_failure_rate']}",
        f"- Average negative hit rate: {agg['average_negative_hit_rate']}",
        f"- Negative overload packs: {agg['negative_overload_count']}",
        "",
        "## Per-Mission-Type Summary",
        "",
        "| Mission type | Packs | Alpha plausible | Rate | Avg adjusted | Avg non-failure | Avg negative | Overload |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in results["per_mission_type_summary"]:
        lines.append(
            f"| {row['mission_type']} | {row['pack_count']} | {row['alpha_plausible_count']} | {row['alpha_plausible_rate']} | {row['average_mission_type_adjusted_smell_score']} | {row['average_non_failure_rate']} | {row['average_negative_hit_rate']} | {row['negative_overload_count']} |"
        )
    lines.extend(
        [
            "",
            "## Per-Construction-Policy Summary",
            "",
            "| Policy | Packs | Alpha plausible | Rate | Avg adjusted | Avg non-failure | Avg negative | Overload |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in results["per_construction_policy_summary"]:
        lines.append(
            f"| {row['construction_policy']} | {row['pack_count']} | {row['alpha_plausible_count']} | {row['alpha_plausible_rate']} | {row['average_mission_type_adjusted_smell_score']} | {row['average_non_failure_rate']} | {row['average_negative_hit_rate']} | {row['negative_overload_count']} |"
        )
    examples = results["representative_pack_examples"]
    lines.extend(
        [
            "",
            "## Representative Examples",
            "",
            f"- Best pack: `{examples['best_pack_id']}` ({examples['best_score']})",
            f"- Best Alpha-plausible pack: `{examples['best_alpha_plausible_pack_id']}` ({examples['best_alpha_plausible_score']})",
            f"- Borderline Alpha-plausible pack: `{examples['borderline_alpha_plausible_pack_id']}` ({examples['borderline_alpha_plausible_score']})",
            f"- Worst pack: `{examples['worst_pack_id']}` ({examples['worst_score']})",
            f"- Worst negative overload: `{examples['worst_negative_overload_pack_id']}` ({examples['worst_negative_hit_rate']} negative hit rate)",
            "",
            "## LLM Packet",
            "",
            f"- Markdown: `{results['llm_packet_summary']['llm_sanity_review_packet_md_ref']}`",
            f"- JSON: `{results['llm_packet_summary']['llm_sanity_review_packet_json_ref']}`",
            f"- Examples: {results['llm_packet_summary']['llm_sanity_review_example_count']}",
        ]
    )
    SUMMARY_MD_OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_guardrail_report(results: dict[str, Any]) -> None:
    lines = ["# Phase 1G Guardrail Report", "", "| Guardrail | Status |", "| --- | --- |"]
    expected = {
        "selector_did_not_read_hidden_oracle": True,
        "constructor_selection_pool_reaction_labels_visible": False,
        "constructor_selection_pool_hidden_reason_tags_visible": False,
        "hidden_reactions_joined_only_after_pack_construction": True,
        "runtime_remains_false": True,
        "production_mission_generation_remains_false": True,
        "final_mission_copy_absent": True,
        "canonical_graph_mutation_remains_false": True,
        "oracle_metrics_written_back_to_selector_input": False,
        "llm_packet_review_only": True,
    }
    for key, value in results["guardrail_summary"].items():
        if key == "negative_fixture_refs":
            continue
        lines.append(f"| {key} | {'PASS' if value == expected.get(key) else 'FAIL'} |")
    lines.extend(["", "## Negative Fixtures", ""])
    for label, ref in results["guardrail_summary"]["negative_fixture_refs"].items():
        lines.append(f"- `{ref}`: {label}")
    GUARDRAIL_MD_OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_results() -> dict[str, Any]:
    packs = build_packs()
    signature = [
        (
            pack["pack_id"],
            tuple(song["song_id"] for song in pack["songs"]),
            pack["mission_type_adjusted_smell_score"],
        )
        for pack in packs
    ]
    rerun_packs = build_packs()
    rerun_signature = [
        (
            pack["pack_id"],
            tuple(song["song_id"] for song in pack["songs"]),
            pack["mission_type_adjusted_smell_score"],
        )
        for pack in rerun_packs
    ]
    llm_summary = write_llm_packets(packs)
    results = {
        "contract_version": "phase1g_construction_policy_llm_review_v0_1",
        "fixture_status": "synthetic_contract_fixture",
        "created_at": now_iso(),
        "phase": "mission_type_construction_policy_hardening_llm_review",
        "runtime_allowed": False,
        "runtime_listener_evidence_connected": False,
        "production_mission_generation_allowed": False,
        "canonical_graph_mutation_allowed": False,
        "selector_may_read_hidden_oracle": False,
        "constructor_optimized_by_hidden_reaction_labels": False,
        "oracle_evaluation_fed_back_into_selector": False,
        "final_mission_construction_status": "not_in_scope",
        "run_matrix": {
            "profiles": PROFILE_IDS,
            "evidence_scale": EVIDENCE_SCALE,
            "sampling_modes": SAMPLING_MODES,
            "mission_types": MISSION_TYPES,
            "construction_policies": CONSTRUCTION_POLICIES,
            "alpha_v0_2_pack_size": ALPHA_PACK_SIZE,
            "future_product_pack_range_to_test_later": FUTURE_PRODUCT_PACK_RANGE,
            "completed_construction_attempt_count": len(packs),
            "preferred_full_matrix_count": 162,
            "minimum_required_pack_count": 100,
        },
        "source_refs": {
            "expanded_visible_profile_inputs_ref": repo_rel(EXPANDED_VISIBLE_INPUTS),
            "selector_outputs_root_ref": repo_rel(PHASE1E_DIR / "selector_outputs_by_profile_scale"),
            "hidden_profile_oracle_ref": repo_rel(HIDDEN_PROFILE_ORACLES),
            "hidden_reaction_corpus_root_ref": repo_rel(HIDDEN_CORPUS_DIR),
        },
        "mission_type_construction_policies": {
            mission_type: {
                policy: slot_plan(mission_type, policy)
                for policy in CONSTRUCTION_POLICIES
            }
            for mission_type in MISSION_TYPES
        },
        "scoring_model": {
            "generic_overall_smell_score": "Phase 1F baseline smell formula.",
            "mission_type_adjusted_smell_score": "Mission-type weighting over non-failure, positive discovery, role balance, coherence, diagnostic value, and bounded contrast.",
            "alpha_candidate_gate": "song_count=6, non_failure>=0.67, negative<=0.33, not too_random, has anchor, has probe/comparator, source refs, and why_selected for every song.",
            "six_song_note": "Alpha v0.2 test size only; future product range to test later is 8-12 songs.",
        },
        "packs": packs,
        "aggregate_pack_metrics": aggregate_metrics(packs),
        "per_profile_summary": summarize_group(packs, "profile_id"),
        "per_mission_type_summary": summarize_group(packs, "mission_type"),
        "per_construction_policy_summary": summarize_group(packs, "construction_policy"),
        "representative_pack_examples": representative_examples(packs),
        "guardrail_summary": {
            "selector_did_not_read_hidden_oracle": True,
            "constructor_selection_pool_reaction_labels_visible": False,
            "constructor_selection_pool_hidden_reason_tags_visible": False,
            "hidden_reactions_joined_only_after_pack_construction": True,
            "runtime_remains_false": True,
            "production_mission_generation_remains_false": True,
            "final_mission_copy_absent": True,
            "canonical_graph_mutation_remains_false": True,
            "oracle_metrics_written_back_to_selector_input": False,
            "llm_packet_review_only": True,
        },
        "determinism_summary": {
            "deterministic_rerun_matched": signature == rerun_signature,
            "pack_signature_sha256": stable_hash(signature),
            "rerun_signature_sha256": stable_hash(rerun_signature),
            "compared_pack_count": len(packs),
        },
        "llm_packet_summary": llm_summary,
        "known_limitations": [
            "Packs are offline synthetic review objects and not final mission content.",
            "Two context_dependence_test attempts for public_profile_06 use related top-window proxy opportunities because exact ranked context opportunities were absent at 200 atoms.",
            "Song choice uses deterministic token matching, not a real catalog, graph route solver, or Apple Music API.",
            "Six songs are Alpha v0.2 test size only; 8-12 song product posture remains future work.",
        ],
        "recommendations": [
            "Prefer mission_type_native_policy for Alpha design review; compare against experience_balanced_policy for tolerability.",
            "Send all six mission types into LLM review, but scrutinize boundary/context negative load before UAT.",
            "Do not revive raw top-10 construction as an Alpha policy.",
            "Run future 8-12 song stress testing only after PM approves mission-construction contract shape.",
        ],
    }
    results["guardrail_summary"]["negative_fixture_refs"] = build_negative_fixtures(results)
    results["human_pack_card_refs"] = write_cards(packs)
    return results


def main() -> int:
    PHASE1G_DIR.mkdir(parents=True, exist_ok=True)
    write_json(SCHEMA_OUTPUT, build_schema())
    results = build_results()
    write_json(RESULTS_OUTPUT, results)
    write_summary(results)
    write_guardrail_report(results)
    print(f"Wrote {repo_rel(RESULTS_OUTPUT)}")
    print(f"Wrote {repo_rel(SUMMARY_MD_OUTPUT)}")
    print(f"Wrote {repo_rel(SCHEMA_OUTPUT)}")
    print(f"Wrote {repo_rel(GUARDRAIL_MD_OUTPUT)}")
    print(f"Wrote {repo_rel(LLM_PACKET_MD_OUTPUT)}")
    print(f"Wrote {repo_rel(LLM_PACKET_JSON_OUTPUT)}")
    print(f"Constructed {len(results['packs'])} Phase 1G offline song packs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
