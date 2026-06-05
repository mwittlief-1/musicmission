#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DIR = REPO_ROOT / "data/product_contracts/mission_opportunity_selection_v0_1"
PROFILE_SIM_DIR = CONTRACT_DIR / "fixtures/profile_simulation"

VISIBLE_INPUTS = PROFILE_SIM_DIR / "visible_profile_selector_inputs_v0_1.json"
HIDDEN_ORACLES = PROFILE_SIM_DIR / "hidden_profile_oracles_v0_1.json"
OUTPUT_PATH = PROFILE_SIM_DIR / "hidden_oracle_evaluation_design_v0_1.json"

PROFILE_SELECTOR_OUTPUTS = {
    "public_profile_01": PROFILE_SIM_DIR / "public_profile_01_selector_output_v0_1.json",
    "public_profile_05": PROFILE_SIM_DIR / "public_profile_05_selector_output_v0_1.json",
    "public_profile_06": PROFILE_SIM_DIR / "public_profile_06_selector_output_v0_1.json",
}

OPPORTUNITIES_PER_PROFILE = 10

VARIANT_SUFFIX_PREFIXES = ("_candidate_", "_floor_fail_", "_low_score_")

DIAGNOSTIC_PRIORS = {
    "boundary_test": 0.50,
    "false_nearby_test": 0.46,
    "context_dependence_test": 0.46,
    "bridge_test": 0.42,
    "evidence_repair_test": 0.42,
    "exception_scope_test": 0.38,
    "song_to_archetype_test": 0.34,
    "artist_depth_test": 0.32,
    "album_container_test": 0.32,
    "archetype_depth_test": 0.30,
    "gateway_test": 0.28,
    "archetype_survey": 0.24,
    "family_survey": 0.22,
    "initial_profile_survey": 0.16,
}

OVERFIT_GUARD_PRIORS = {
    "exception_scope_test": 0.58,
    "song_to_archetype_test": 0.50,
    "artist_depth_test": 0.48,
    "album_container_test": 0.46,
    "false_nearby_test": 0.40,
    "boundary_test": 0.38,
    "context_dependence_test": 0.36,
    "bridge_test": 0.34,
    "archetype_depth_test": 0.28,
    "evidence_repair_test": 0.28,
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def repo_rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 4)


def strip_variant_suffix(target_id: str) -> str:
    value = str(target_id)
    for prefix in VARIANT_SUFFIX_PREFIXES:
        if prefix in value:
            return value.split(prefix, 1)[0]
    return value


def expanded_target_ids(target_ids: list[str]) -> list[str]:
    expanded: list[str] = []
    for raw_target_id in target_ids:
        base = strip_variant_suffix(raw_target_id)
        pieces = [piece for piece in base.split("->") if piece]
        expanded.extend(pieces or [base])
    return list(dict.fromkeys(expanded))


def normalize_song_id(target_id: str) -> str:
    value = target_id.removeprefix("song-")
    return value


def oracle_maps(hidden_profile: dict[str, Any]) -> dict[str, Any]:
    oracle = hidden_profile["hidden_oracle"]
    patterns = oracle.get("affinity_pattern_reactions", {})
    song_reactions = {
        str(item.get("song_id")): str(item.get("reaction"))
        for item in oracle.get("song_reactions", [])
        if item.get("song_id")
    }
    return {
        "primary": {
            str(item["archetype_id"]): float(item["weight"])
            for item in patterns.get("primary_archetype_affinities", [])
        },
        "secondary": {
            str(item["archetype_id"]): float(item["weight"])
            for item in patterns.get("secondary_archetype_affinities", [])
        },
        "anti": {
            str(item["archetype_id"]): float(item["weight"])
            for item in patterns.get("hidden_anti_affinities", [])
        },
        "false_nearby": patterns.get("false_nearby_lane", {}),
        "context": patterns.get("context_lane", {}),
        "song_reactions": song_reactions,
    }


def direct_song_counts(base_target_ids: list[str], song_reactions: dict[str, str]) -> dict[str, int]:
    counts = Counter({"love": 0, "like": 0, "ok": 0, "dont_like": 0, "unknown": 0})
    for target_id in base_target_ids:
        reaction = song_reactions.get(normalize_song_id(target_id))
        if reaction in {"love", "like", "ok", "dont_like"}:
            counts[reaction] += 1
        elif str(target_id).startswith("song-"):
            counts["unknown"] += 1
    return {
        "love": counts["love"],
        "like": counts["like"],
        "ok": counts["ok"],
        "dont_like": counts["dont_like"],
        "unknown": counts["unknown"],
    }


def oracle_match_summary(opportunity: dict[str, Any], maps: dict[str, Any]) -> dict[str, Any]:
    base_target_ids = expanded_target_ids(opportunity["target_object_ids"])
    matched_primary = [target_id for target_id in base_target_ids if target_id in maps["primary"]]
    matched_secondary = [target_id for target_id in base_target_ids if target_id in maps["secondary"]]
    matched_anti = [target_id for target_id in base_target_ids if target_id in maps["anti"]]
    known = set(matched_primary + matched_secondary + matched_anti)

    false_lane = maps["false_nearby"]
    false_archetype = str(false_lane.get("archetype_id", ""))
    false_family = str(false_lane.get("family_number", ""))
    false_family_id = f"family_{false_family}" if false_family else ""
    false_match = any(
        target_id in {false_archetype, false_family, false_family_id}
        for target_id in base_target_ids
    )
    context_match = bool(maps["context"].get("lane_id")) and opportunity["mission_type"] in {
        "context_dependence_test",
        "evidence_repair_test",
        "album_container_test",
    }
    unknown_targets = [
        target_id
        for target_id in base_target_ids
        if target_id not in known
        and target_id not in {false_archetype, false_family, false_family_id}
        and not target_id.startswith("song-")
    ]

    return {
        "matched_primary_archetype_ids": matched_primary,
        "matched_secondary_archetype_ids": matched_secondary,
        "matched_anti_archetype_ids": matched_anti,
        "matched_unknown_target_ids": unknown_targets,
        "false_nearby_lane_match": false_match,
        "context_lane_match": context_match,
        "direct_song_reaction_counts": direct_song_counts(
            base_target_ids,
            maps["song_reactions"],
        ),
    }


def max_weight(ids: list[str], weights: dict[str, float]) -> float:
    return max((weights[target_id] for target_id in ids if target_id in weights), default=0.0)


def metrics_for_opportunity(
    opportunity: dict[str, Any],
    match: dict[str, Any],
    maps: dict[str, Any],
    visible_expected: set[str],
    survey_decay_score: float,
) -> dict[str, float]:
    mission_type = opportunity["mission_type"]
    selector_score = float(opportunity["score_components"]["final_opportunity_score"])
    primary_weight = max_weight(match["matched_primary_archetype_ids"], maps["primary"])
    secondary_weight = max_weight(match["matched_secondary_archetype_ids"], maps["secondary"])
    anti_weight = max_weight(match["matched_anti_archetype_ids"], maps["anti"])
    direct = match["direct_song_reaction_counts"]
    direct_positive = min(1.0, direct["love"] * 0.48 + direct["like"] * 0.32 + direct["ok"] * 0.12)
    expected_bonus = 0.18 if mission_type in visible_expected else 0.0
    unknown_bonus = min(0.14, len(match["matched_unknown_target_ids"]) * 0.035)

    hidden_hit_rate_proxy = bounded(
        0.22
        + primary_weight * 0.42
        + secondary_weight * 0.27
        + direct_positive
        - anti_weight * 0.30
        + (0.06 if match["context_lane_match"] else 0.0)
    )
    opportunity_relevance = bounded(selector_score * 0.58 + expected_bonus + unknown_bonus)
    diagnostic_value = bounded(
        selector_score * 0.28
        + DIAGNOSTIC_PRIORS.get(mission_type, 0.25)
        + unknown_bonus
        + (0.12 if anti_weight and (primary_weight or secondary_weight or unknown_bonus) else 0.0)
    )
    boundary_discovery = bounded(
        (0.62 if mission_type == "boundary_test" else 0.30 if mission_type in {"false_nearby_test", "bridge_test"} else 0.08)
        + min(primary_weight + secondary_weight, 0.32) * 0.28
        + min(anti_weight + unknown_bonus, 0.34) * 0.40
    )
    false_nearby_detection = bounded(
        (0.54 if mission_type == "false_nearby_test" else 0.22 if mission_type == "boundary_test" else 0.08)
        + (0.28 if match["false_nearby_lane_match"] else 0.0)
        + anti_weight * 0.28
    )
    context_detection = bounded(
        (0.58 if mission_type == "context_dependence_test" else 0.26 if mission_type in {"album_container_test", "evidence_repair_test"} else 0.08)
        + (0.24 if match["context_lane_match"] else 0.0)
    )
    overfit_prevention = bounded(
        OVERFIT_GUARD_PRIORS.get(mission_type, 0.18)
        + (0.16 if anti_weight else 0.0)
        + unknown_bonus
        + (0.10 if mission_type in visible_expected else 0.0)
    )
    learning_usefulness = bounded(
        opportunity_relevance * 0.22
        + hidden_hit_rate_proxy * 0.18
        + diagnostic_value * 0.22
        + max(boundary_discovery, false_nearby_detection, context_detection, overfit_prevention) * 0.26
        + survey_decay_score * 0.12
    )

    return {
        "opportunity_relevance": opportunity_relevance,
        "hidden_hit_rate_proxy": hidden_hit_rate_proxy,
        "diagnostic_value": diagnostic_value,
        "boundary_discovery_potential": boundary_discovery,
        "false_nearby_detection_potential": false_nearby_detection,
        "context_detection_potential": context_detection,
        "overfit_prevention_score": overfit_prevention,
        "survey_decay_score": survey_decay_score,
        "learning_usefulness_score": learning_usefulness,
    }


def average_metrics(items: list[dict[str, float]]) -> dict[str, float]:
    keys = [
        "opportunity_relevance",
        "hidden_hit_rate_proxy",
        "diagnostic_value",
        "boundary_discovery_potential",
        "false_nearby_detection_potential",
        "context_detection_potential",
        "overfit_prevention_score",
        "survey_decay_score",
        "learning_usefulness_score",
    ]
    if not items:
        return {key: 0.0 for key in keys}
    return {
        key: bounded(sum(item[key] for item in items) / len(items))
        for key in keys
    }


def metric_definitions() -> list[dict[str, Any]]:
    return [
        {
            "metric_name": "opportunity_relevance",
            "meaning": "Whether the selected opportunity matches the visible evidence state that the selector was allowed to see.",
            "uses_hidden_oracle": False,
            "visible_selector_input": True,
        },
        {
            "metric_name": "hidden_hit_rate_proxy",
            "meaning": "Post-selection estimate that constructed candidates would include love/like or weak non-failure outcomes.",
            "uses_hidden_oracle": True,
            "visible_selector_input": False,
        },
        {
            "metric_name": "diagnostic_value",
            "meaning": "Expected chance that the opportunity clarifies an unknown, conflict, boundary, context, or overfit question.",
            "uses_hidden_oracle": True,
            "visible_selector_input": True,
        },
        {
            "metric_name": "boundary_discovery_potential",
            "meaning": "Expected ability to reveal a true like/dislike or like/unknown boundary.",
            "uses_hidden_oracle": True,
            "visible_selector_input": True,
        },
        {
            "metric_name": "false_nearby_detection_potential",
            "meaning": "Expected ability to test misleading graph-near or tag-near similarities.",
            "uses_hidden_oracle": True,
            "visible_selector_input": True,
        },
        {
            "metric_name": "context_detection_potential",
            "meaning": "Expected ability to identify context-heavy or context-only preference behavior.",
            "uses_hidden_oracle": True,
            "visible_selector_input": True,
        },
        {
            "metric_name": "overfit_prevention_score",
            "meaning": "Expected ability to avoid overgeneralizing from one song, artist, album, or context.",
            "uses_hidden_oracle": True,
            "visible_selector_input": True,
        },
        {
            "metric_name": "survey_decay_score",
            "meaning": "Whether low-value survey opportunities disappear when better evidence-driven opportunities exist.",
            "uses_hidden_oracle": False,
            "visible_selector_input": True,
        },
        {
            "metric_name": "learning_usefulness_score",
            "meaning": "Composite review score for whether the selected opportunity would likely produce useful learning later.",
            "uses_hidden_oracle": True,
            "visible_selector_input": True,
        },
    ]


def build_profile_evaluation(
    visible_profile: dict[str, Any],
    hidden_profile: dict[str, Any],
    selector_output_path: Path,
) -> dict[str, Any]:
    selector = load_json(selector_output_path)
    maps = oracle_maps(hidden_profile)
    profile_id = visible_profile["profile_id"]
    visible_expected_list = (
        visible_profile
        .get("expected_selector_behavior", {})
        .get("likely_top_mission_types", [])
    )
    visible_expected = set(visible_expected_list)
    ranked = selector["ranked_opportunities"][:OPPORTUNITIES_PER_PROFILE]
    top10_types = {opportunity["mission_type"] for opportunity in ranked}
    survey_decay_score = 1.0 if "initial_profile_survey" not in top10_types else 0.25

    evaluations: list[dict[str, Any]] = []
    for rank, opportunity in enumerate(ranked, start=1):
        match = oracle_match_summary(opportunity, maps)
        metrics = metrics_for_opportunity(
            opportunity,
            match,
            maps,
            visible_expected,
            survey_decay_score,
        )
        evaluations.append(
            {
                "selected_opportunity_ref": {
                    "opportunity_id": opportunity["opportunity_id"],
                    "rank": rank,
                    "mission_type": opportunity["mission_type"],
                    "target_object_type": opportunity["target_object_type"],
                    "target_object_ids": opportunity["target_object_ids"],
                    "target_display_name": opportunity["target_object_ref"]["display_name"],
                    "final_opportunity_score": opportunity["score_components"]["final_opportunity_score"],
                },
                "construction_status": "not_constructed",
                "production_generation_allowed": False,
                "candidate_song_selection_status": "not_in_scope",
                "no_candidate_song_list": True,
                "oracle_match_summary": match,
                "expected_metrics": metrics,
                "evaluator_use_only_hidden_refs": [
                    f"{repo_rel(HIDDEN_ORACLES)}#{profile_id}"
                ],
                "notes": [
                    "Post-selection oracle design only.",
                    "No candidate songs or final mission contents are emitted.",
                ],
            }
        )

    expected_useful = []
    for evaluation in sorted(
        evaluations,
        key=lambda item: item["expected_metrics"]["learning_usefulness_score"],
        reverse=True,
    ):
        mission_type = evaluation["selected_opportunity_ref"]["mission_type"]
        if mission_type not in expected_useful:
            expected_useful.append(mission_type)
        if len(expected_useful) == 3:
            break

    patterns = hidden_profile["hidden_oracle"]["affinity_pattern_reactions"]
    false_lane = patterns.get("false_nearby_lane", {})
    context_lane = patterns.get("context_lane", {})

    return {
        "profile_id": profile_id,
        "selector_output_ref": repo_rel(selector_output_path),
        "visible_evidence_ref": f"{repo_rel(VISIBLE_INPUTS)}#{profile_id}",
        "hidden_oracle_profile_ref": f"{repo_rel(HIDDEN_ORACLES)}#{profile_id}",
        "visible_expected_top_mission_types": visible_expected_list,
        "oracle_summary": {
            "primary_archetype_ids": list(maps["primary"].keys()),
            "secondary_archetype_ids": list(maps["secondary"].keys()),
            "anti_archetype_ids": list(maps["anti"].keys()),
            "false_nearby_lane_id": str(false_lane.get("lane_id", "unknown_false_nearby_lane")),
            "false_nearby_archetype_id": str(false_lane.get("archetype_id", "unknown_false_nearby_archetype")),
            "context_lane_id": str(context_lane.get("lane_id", "unknown_context_lane")),
        },
        "top_opportunity_evaluations": evaluations,
        "aggregate_metrics": average_metrics(
            [evaluation["expected_metrics"] for evaluation in evaluations]
        ),
        "expected_useful_top_mission_types": expected_useful,
        "notes": [
            "This profile-level evaluation may read the hidden oracle only after selector outputs already exist.",
            "Hidden oracle summaries are evaluator inputs and remain forbidden as selector inputs.",
        ],
    }


def build_payload() -> dict[str, Any]:
    visible = load_json(VISIBLE_INPUTS)
    hidden = load_json(HIDDEN_ORACLES)
    hidden_by_id = {profile["profile_id"]: profile for profile in hidden["profiles"]}

    profiles = [
        build_profile_evaluation(
            visible_profile,
            hidden_by_id[visible_profile["profile_id"]],
            PROFILE_SELECTOR_OUTPUTS[visible_profile["profile_id"]],
        )
        for visible_profile in visible["profiles"]
    ]

    return {
        "contract_version": "hidden_oracle_evaluation_design_v0_1",
        "fixture_status": "synthetic_contract_fixture",
        "created_at": now_iso(),
        "phase": "post_selection_oracle_evaluation_design",
        "runtime_allowed": False,
        "runtime_listener_evidence_connected": False,
        "production_mission_generation_allowed": False,
        "canonical_graph_mutation_allowed": False,
        "listener_preference_inference_from_affinity_allowed": False,
        "opportunity_only": True,
        "selector_may_read_hidden_oracle": False,
        "evaluator_may_read_hidden_oracle_after_selection": True,
        "selector_visible_input_ref": repo_rel(VISIBLE_INPUTS),
        "hidden_oracle_ref": repo_rel(HIDDEN_ORACLES),
        "selector_output_refs": [
            repo_rel(path)
            for path in PROFILE_SELECTOR_OUTPUTS.values()
        ],
        "evaluation_scope": {
            "evaluation_subject": "selected_opportunity_blobs_only",
            "opportunities_per_profile": OPPORTUNITIES_PER_PROFILE,
            "construction_simulation_status": "not_implemented",
            "candidate_song_selection_status": "not_in_scope",
            "hidden_oracle_use": "post_selection_evaluator_only",
            "selector_input_rule": "visible_evidence_only",
            "allowed_outputs": [
                "opportunity_refs",
                "oracle_match_summaries",
                "expected_metric_scores",
                "aggregate_profile_scores",
                "evaluation_notes",
            ],
        },
        "metric_definitions": metric_definitions(),
        "profiles": profiles,
    }


def main() -> int:
    payload = build_payload()
    write_json(OUTPUT_PATH, payload)
    print(f"Wrote {repo_rel(OUTPUT_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
