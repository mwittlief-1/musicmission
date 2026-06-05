#!/usr/bin/env python3
from __future__ import annotations

import argparse
import heapq
import json
from collections import Counter
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DIR = REPO_ROOT / "data/product_contracts/mission_opportunity_selection_v0_1"
FIXTURE_DIR = CONTRACT_DIR / "fixtures"

DEFAULT_REGISTRY = FIXTURE_DIR / "mission_type_registry_sample_v0_1.json"
DEFAULT_SCENARIOS = FIXTURE_DIR / "synthetic_selector_scenarios_v0_1.json"
DEFAULT_OUTPUT = FIXTURE_DIR / "prototype_selector_output_synthetic_v0_1.json"
DEFAULT_EARLY_STOP_OUTPUT = FIXTURE_DIR / "prototype_selector_output_early_stop_synthetic_v0_1.json"

TOP_K = 25

MISSION_SCENARIOS = {
    "initial_profile_survey": "sparse_post_intake_survey_ok",
    "family_survey": "family_positive_weak_archetype_clarity",
    "archetype_survey": "family_positive_weak_archetype_clarity",
    "gateway_test": "bridge_source_positive_target_gap",
    "song_to_archetype_test": "one_strong_song_weak_archetype",
    "artist_depth_test": "one_artist_shallow_depth",
    "album_container_test": "one_album_container_signal",
    "archetype_depth_test": "strong_archetype_shallow_depth",
    "exception_scope_test": "recent_surprise_signal",
    "false_nearby_test": "mixed_nearby_boundary",
    "context_dependence_test": "context_heavy_signals",
    "bridge_test": "bridge_source_positive_target_gap",
    "boundary_test": "mixed_nearby_boundary",
    "evidence_repair_test": "recent_surprise_signal",
}

COVERAGE_ELIGIBLE_COUNTS = {
    "very_high": 3,
    "high": 2,
    "medium": 1,
    "lower_medium": 1,
    "low": 2,
}

EARLY_STOP_ELIGIBLE_COUNTS = {
    "very_high": 8,
    "high": 5,
    "medium": 2,
    "lower_medium": 1,
    "low": 1,
}


@dataclass(frozen=True)
class CandidateSpec:
    mission_type: str
    scenario_id: str
    profile_id: str
    variant_kind: str
    variant_index: int
    target_object_type: str
    target_rollup_level: str
    target_id_suffix: str
    target_display_suffix: str
    mission_type_value_input: float
    mission_fit_input: float
    readiness_input: float
    learning_value_input: float
    risk_input: float
    repetition_input: float
    complexity_input: float
    floor_score: float
    required_inputs_available: bool
    graph_context_available: bool
    generation_reasons: tuple[str, ...]

    @property
    def opportunity_id(self) -> str:
        profile_slug = self.profile_id.replace("public_", "").replace("_", "-")
        return (
            f"opp_{profile_slug}_{self.mission_type}_{self.scenario_id}_"
            f"{self.variant_kind}_{self.variant_index:02d}"
        )


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")


def bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 4)


VARIANT_SUFFIX_PREFIXES = ("_candidate_", "_floor_fail_", "_low_score_")


MISSION_TARGET_ROLLUP_LEVEL = {
    "initial_profile_survey": "family",
    "family_survey": "family",
    "archetype_survey": "archetype",
    "gateway_test": "family",
    "song_to_archetype_test": "song",
    "artist_depth_test": "artist",
    "album_container_test": "album",
    "archetype_depth_test": "archetype",
    "exception_scope_test": "song",
    "false_nearby_test": "song_cluster",
    "context_dependence_test": "song_cluster",
    "bridge_test": "family_pair",
    "boundary_test": "archetype_pair",
    "evidence_repair_test": "song_cluster",
}

BAND_COMPLEXITY = {
    "low": 0.04,
    "lower_medium": 0.06,
    "medium": 0.08,
    "high": 0.12,
    "very_high": 0.16,
}


def scenario_base_target_id(scenario: dict[str, Any], object_type: str) -> str:
    if object_type == "family":
        return str(scenario["family_id"])
    if object_type == "archetype":
        return str(scenario["archetype_id"])
    if object_type == "artist":
        return str(scenario["artist_id"])
    if object_type == "album":
        return str(scenario["album_id"])
    if object_type == "song":
        return str(scenario["song_id"])
    if object_type == "family_pair":
        return f"{scenario['family_id']}->{scenario['family_id']}_target"
    if object_type == "archetype_pair":
        return f"{scenario['archetype_id']}->{scenario['archetype_id']}_target"
    if object_type == "song_cluster":
        return f"cluster_{scenario['scenario_id']}"
    raise ValueError(f"unsupported target object type: {object_type}")


def split_rollup_target_ids(target_object_id: str, object_type: str) -> list[str]:
    if object_type in {"family_pair", "archetype_pair"}:
        parts = [part for part in target_object_id.split("->") if part]
        if len(parts) >= 2:
            return parts[:2]
    return [target_object_id]


def strip_variant_suffix(target_id: str) -> str:
    for prefix in VARIANT_SUFFIX_PREFIXES:
        if prefix in target_id:
            return target_id.split(prefix, 1)[0]
    return target_id


def target_ref_from_rollup(
    rollup: dict[str, Any],
    object_type: str,
    target_id_suffix: str = "",
    target_display_suffix: str = "",
) -> dict[str, Any]:
    base_target_id = str(rollup.get("target_object_id", "unknown_target"))
    object_ids = split_rollup_target_ids(base_target_id, object_type)
    if target_id_suffix:
        object_ids = [f"{object_id}{target_id_suffix}" for object_id in object_ids]
    display_name = str(rollup.get("display_name") or base_target_id)
    if target_display_suffix:
        display_name = f"{display_name} {target_display_suffix}"

    return {
        "object_type": object_type,
        "object_ids": object_ids,
        "display_name": display_name,
    }


def graph_context(
    scenario: dict[str, Any],
    rollup: dict[str, Any],
    object_type: str,
    opportunity_id: str,
    target_id_suffix: str = "",
    target_display_suffix: str = "",
) -> dict[str, Any]:
    ref = target_ref_from_rollup(
        rollup,
        object_type,
        target_id_suffix,
        target_display_suffix,
    )
    base_ids = [strip_variant_suffix(target_id) for target_id in ref["object_ids"]]
    return {
        "target_object_ref": ref,
        "family_ids": base_ids if object_type in {"family", "family_pair"} else [scenario["family_id"]],
        "family_names": [scenario["family_name"]],
        "archetype_ids": base_ids if object_type in {"archetype", "archetype_pair"} else [scenario["archetype_id"]],
        "archetype_names": [scenario["archetype_name"]],
        "artist_ids": base_ids if object_type == "artist" else [scenario["artist_id"]],
        "album_ids": base_ids if object_type == "album" else [scenario["album_id"]],
        "song_ids": base_ids if object_type in {"song", "song_cluster"} else [scenario["song_id"]],
        "node_tier": scenario["node_tier"],
        "graph_item_role": scenario["graph_item_role"],
        "track_tier_within_archetype": scenario["node_tier"],
        "album_tier_within_archetype": "supporting",
        "artist_tier_within_archetype": "major",
        "context_overlays": scenario["context_overlays"],
        "risk_flags": scenario["risk_flags"],
        "identity_flags": scenario["identity_flags"],
        "provenance": {
            "source": "synthetic_selector_scenarios_v0_1",
            "source_refs": [
                scenario["scenario_id"],
                str(rollup.get("rollup_id", "")),
                opportunity_id,
            ],
            "synthetic_only": True,
        },
    }


def score_candidate(
    mission_definition: dict[str, Any],
    spec: CandidateSpec,
) -> dict[str, float]:
    components = {
        "mission_type_value": bounded(
            mission_definition["score_floor"] * 0.46 * spec.mission_type_value_input
        ),
        "mission_fit_score": bounded(0.34 * spec.mission_fit_input),
        "readiness_score": bounded(0.20 * spec.readiness_input),
        "learning_value_score": bounded(0.30 * spec.learning_value_input),
        "risk_penalty": bounded(0.10 * spec.risk_input),
        "repetition_penalty": bounded(0.04 * spec.repetition_input),
        "complexity_penalty": bounded(0.04 * spec.complexity_input),
    }
    raw_score = bounded(
        components["mission_type_value"]
        + components["mission_fit_score"]
        + components["readiness_score"]
        + components["learning_value_score"]
        - components["risk_penalty"]
        - components["repetition_penalty"]
        - components["complexity_penalty"]
    )
    components["raw_score"] = raw_score
    components["final_opportunity_score"] = bounded(
        min(raw_score, mission_definition["score_ceiling"])
    )
    return components


def fallback_target_rollup(scenario: dict[str, Any], level: str) -> dict[str, Any]:
    signal = scenario["signal_summary"]
    computed = scenario["computed_fields"]
    target_object_id = scenario_base_target_id(scenario, level)
    display_name = (
        f"{scenario['family_name']} -> Synthetic Target Family"
        if level == "family_pair"
        else f"{scenario['archetype_name']} -> Synthetic Target Archetype"
        if level == "archetype_pair"
        else f"{scenario['display_name']} Cluster"
        if level == "song_cluster"
        else scenario.get(f"{level}_name")
        or scenario.get("display_name")
        or scenario.get("archetype_name")
    )
    return {
        "rollup_id": f"synthetic_rollup:{level}:{target_object_id}:{scenario['scenario_id']}",
        "object_level": level,
        "target_object_id": target_object_id,
        "display_name": display_name,
        "positive_signal_count": signal["positive_signal_count"],
        "negative_signal_count": signal["negative_signal_count"],
        "weak_non_failure_signal_count": signal["weak_non_failure_signal_count"],
        "survey_ok_ignored_count": signal["survey_ok_ignored_count"],
        "mission_ok_weak_count": signal["mission_ok_weak_count"],
        "evidence_density": signal["evidence_density"],
        "coverage_gap_score": computed["coverage_gap_score"],
        "conflict_score": signal["conflict_score"],
        "context_variability_score": computed["context_variability_score"],
        "context_skew_score": computed["context_skew_score"],
        "tier_coverage_score": computed["tier_coverage_score"],
        "tier_depth_score": computed["tier_depth_score"],
        "depth_gap_score": computed["depth_gap_score"],
        "bridge_readiness_score": computed["bridge_readiness_score"],
        "gateway_to_representative_coherence_score": computed[
            "gateway_to_representative_coherence_score"
        ],
        "recency_score": signal["recency_score"],
        "risk_flags": scenario["risk_flags"],
        "identity_flags": scenario["identity_flags"],
    }


def target_rollup_for_spec(scenario: dict[str, Any], spec: CandidateSpec) -> dict[str, Any]:
    rollups = scenario.get("target_level_rollups", {})
    return deepcopy(
        rollups.get(spec.target_rollup_level)
        or rollups.get(spec.target_object_type)
        or fallback_target_rollup(scenario, spec.target_rollup_level)
    )


def rollup_metric(rollup: dict[str, Any], key: str, default: float = 0.0) -> float:
    value = rollup.get(key, default)
    return bounded(float(value)) if isinstance(value, (int, float)) else default


def risk_input_for_rollup(rollup: dict[str, Any]) -> float:
    risk_flags = [
        flag
        for flag in rollup.get("risk_flags", [])
        if flag not in {"safe_gateway", "visible_bridge_context"}
    ]
    identity_flags = rollup.get("identity_flags", [])
    return bounded(0.10 * len(risk_flags) + 0.22 * len(identity_flags))


def signal_strengths(rollup: dict[str, Any]) -> dict[str, float]:
    positive = float(rollup.get("positive_signal_count", 0))
    negative = float(rollup.get("negative_signal_count", 0))
    weak = float(rollup.get("weak_non_failure_signal_count", 0))
    ok_ignored = float(rollup.get("survey_ok_ignored_count", 0))
    total_visible = max(1.0, positive + negative + weak + ok_ignored)
    preference_total = max(1.0, positive + negative)
    return {
        "positive": bounded(positive / min(6.0, total_visible)),
        "negative": bounded(negative / min(6.0, total_visible)),
        "non_failure": bounded((positive + weak * 0.35) / min(6.0, total_visible)),
        "positive_balance": bounded(positive / preference_total),
        "negative_balance": bounded(negative / preference_total),
        "weak": bounded(weak / min(4.0, total_visible)),
        "survey_uncertainty": bounded(ok_ignored / total_visible),
    }


def floor_details(
    mission_definition: dict[str, Any],
    spec: CandidateSpec,
) -> tuple[bool, list[str], list[str]]:
    failed_requirements: list[str] = []
    fail_reasons: list[str] = []

    if spec.floor_score < mission_definition["score_floor"]:
        failed_requirements.append("mission_type_score_floor")
        fail_reasons.append(
            f"computed floor score {spec.floor_score:.4f} is below "
            f"{mission_definition['score_floor']:.4f}"
        )
    if not spec.required_inputs_available:
        failed_requirements.append("required_inputs_available")
        fail_reasons.append("synthetic candidate is missing required inputs")
    if not spec.graph_context_available:
        failed_requirements.append("graph_context")
        fail_reasons.append("synthetic candidate is missing graph context")

    return not failed_requirements, failed_requirements, fail_reasons


def build_opportunity(
    mission_definition: dict[str, Any],
    scenario: dict[str, Any],
    spec: CandidateSpec,
    score_components: dict[str, float],
    floor_passed: bool,
    failed_requirements: list[str],
    fail_reasons: list[str],
    candidate_generation_summary: dict[str, Any],
) -> dict[str, Any]:
    rollup = target_rollup_for_spec(scenario, spec)
    ref = target_ref_from_rollup(
        rollup,
        spec.target_object_type,
        spec.target_id_suffix,
        spec.target_display_suffix,
    )
    context = graph_context(
        scenario,
        rollup,
        spec.target_object_type,
        spec.opportunity_id,
        spec.target_id_suffix,
        spec.target_display_suffix,
    )
    rollup_ref = str(rollup.get("rollup_id", f"synthetic_rollup:{scenario['scenario_id']}"))
    source_summary = {
        "target_rollup_ref": rollup_ref,
        "target_object_type": spec.target_object_type,
        "target_object_ids": ref["object_ids"],
        "target_display_name": ref["display_name"],
        "positive_signal_count": int(rollup.get("positive_signal_count", 0)),
        "negative_signal_count": int(rollup.get("negative_signal_count", 0)),
        "weak_non_failure_signal_count": int(
            rollup.get("weak_non_failure_signal_count", 0)
        ),
        "survey_ok_ignored_count": int(rollup.get("survey_ok_ignored_count", 0)),
        "mission_ok_weak_count": int(rollup.get("mission_ok_weak_count", 0)),
        "evidence_density": rollup_metric(rollup, "evidence_density"),
        "conflict_score": rollup_metric(rollup, "conflict_score"),
        "recency_score": rollup_metric(rollup, "recency_score", 0.7),
    }

    return {
        "contract_version": "mission_opportunity_blob_v0_1",
        "opportunity_id": spec.opportunity_id,
        "mission_type": spec.mission_type,
        "target_object_type": spec.target_object_type,
        "target_object_ids": ref["object_ids"],
        "target_object_ref": ref,
        "floor_passed": floor_passed,
        "floor_details": {
            "mission_type_score_floor": mission_definition["score_floor"],
            "mission_type_score_ceiling": mission_definition["score_ceiling"],
            "computed_floor_score": bounded(spec.floor_score),
            "floor_passed": floor_passed,
            "failed_requirements": failed_requirements,
            "fail_reasons": fail_reasons,
            "floor_evidence_refs": [
                rollup_ref,
                f"synthetic_candidate:{spec.variant_kind}:{spec.variant_index:02d}",
            ],
        },
        "filled_requirements": {
            "required_evidence_rollup_refs": [
                rollup_ref
            ],
            "required_graph_object_refs": [ref],
            "candidate_refs": [f"synthetic_candidate:{spec.opportunity_id}"],
            "required_inputs_available": spec.required_inputs_available,
        },
        "source_signal_summary": source_summary,
        "graph_context_summary": {
            "graph_contexts": [context],
            "endpoint_graph_contexts": [context]
            if spec.target_object_type in {"family_pair", "archetype_pair"}
            else [],
            "tier_coverage_score": rollup_metric(rollup, "tier_coverage_score", 0.5),
            "tier_depth_score": rollup_metric(rollup, "tier_depth_score", 0.5),
            "coverage_gap_score": rollup_metric(rollup, "coverage_gap_score", 0.5),
            "depth_gap_score": rollup_metric(rollup, "depth_gap_score", 0.5),
        },
        "affinity_context_summary": {
            "dominant_affinity_tags": [
                f"synthetic_scenario:{scenario['scenario_id']}",
                f"mission_type:{spec.mission_type}",
                f"target_rollup:{spec.target_rollup_level}",
            ],
            "context_overlays": scenario["context_overlays"],
            "bridge_readiness_score": rollup_metric(
                rollup,
                "bridge_readiness_score",
                0.4,
            ),
            "gateway_availability": {
                "available": rollup_metric(
                    rollup,
                    "gateway_to_representative_coherence_score",
                    0.4,
                )
                >= 0.6,
                "gateway_candidate_refs": [
                    f"synthetic_gateway:{scenario['scenario_id']}:{spec.variant_index:02d}"
                ],
                "gateway_to_representative_coherence_score": rollup_metric(
                    rollup,
                    "gateway_to_representative_coherence_score",
                    0.4,
                ),
            },
            "context_variability_score": rollup_metric(
                rollup,
                "context_variability_score",
            ),
            "context_skew_score": rollup_metric(rollup, "context_skew_score"),
        },
        "risk_context_summary": {
            "risk_flags": rollup.get("risk_flags", scenario["risk_flags"]),
            "identity_flags": rollup.get("identity_flags", scenario["identity_flags"]),
            "risk_penalty_basis": rollup.get("risk_flags", scenario["risk_flags"]),
            "identity_or_version_risk_present": bool(
                rollup.get("identity_flags", scenario["identity_flags"])
            ),
        },
        "candidate_generation_summary": candidate_generation_summary,
        "score_components": score_components,
        "activation_reasons": [
            f"synthetic scenario: {scenario['description']}",
            f"{spec.mission_type} candidate generated from offline rollup fixture",
            *spec.generation_reasons,
        ],
        "risk_reasons": rollup.get("risk_flags", scenario["risk_flags"]),
        "suppression_reasons": []
        if score_components["final_opportunity_score"] >= mission_definition["score_floor"]
        else ["final score below mission type floor"],
        "required_inputs_available": spec.required_inputs_available,
        "opportunity_only": True,
        "construction_status": "not_constructed",
        "runtime_allowed": False,
        "production_mission_generation_allowed": False,
        "canonical_graph_mutation_allowed": False,
        "listener_preference_inference_from_affinity_allowed": False,
    }


def eligible_inputs(
    mission_definition: dict[str, Any],
    profile: str,
    variant_index: int,
) -> tuple[float, float, float, float, float, float, float]:
    mission_type = mission_definition["mission_type"]
    if profile == "coverage" and mission_type == "family_survey":
        return (0.85, 0.12, 0.14, 0.14, 0.1, 0.1, 0.1)

    decay = max(0, variant_index - 1) * 0.025
    return (
        max(0.78, 1.0 - decay),
        max(0.72, 0.94 - decay),
        max(0.72, 0.92 - decay),
        max(0.72, 0.9 - decay),
        min(0.25, 0.05 + decay),
        min(0.2, 0.04 + decay),
        min(0.2, 0.04 + decay),
    )


def profile_sensitive_fixture(scenarios: dict[str, dict[str, Any]]) -> bool:
    return any(str(scenario.get("profile_id", "")).startswith("public_profile_") for scenario in scenarios.values())


def target_rollup_for_mission(
    mission_definition: dict[str, Any],
    scenario: dict[str, Any],
    target_object_type: str,
) -> tuple[str, dict[str, Any]]:
    mission_type = mission_definition["mission_type"]
    level = MISSION_TARGET_ROLLUP_LEVEL.get(mission_type, target_object_type)
    rollups = scenario.get("target_level_rollups", {})
    rollup = (
        deepcopy(rollups.get(level))
        or deepcopy(rollups.get(target_object_type))
        or fallback_target_rollup(scenario, level)
    )
    return level, rollup


def generation_check(
    mission_definition: dict[str, Any],
    scenario: dict[str, Any],
    rollup: dict[str, Any],
    sensitive: bool,
) -> tuple[bool, list[str]]:
    mission_type = mission_definition["mission_type"]
    if not sensitive:
        return True, ["coverage fixture emits this approved mission type"]

    signals = signal_strengths(rollup)
    positive_count = int(rollup.get("positive_signal_count", 0))
    negative_count = int(rollup.get("negative_signal_count", 0))
    weak_count = int(rollup.get("weak_non_failure_signal_count", 0))
    total_preference = positive_count + negative_count
    evidence_density = rollup_metric(rollup, "evidence_density")
    coverage_gap = rollup_metric(rollup, "coverage_gap_score")
    conflict = rollup_metric(rollup, "conflict_score")
    context_variability = rollup_metric(rollup, "context_variability_score")
    context_skew = rollup_metric(rollup, "context_skew_score")
    depth_gap = rollup_metric(rollup, "depth_gap_score")
    bridge = rollup_metric(rollup, "bridge_readiness_score")
    gateway = rollup_metric(rollup, "gateway_to_representative_coherence_score")
    tier_depth = rollup_metric(rollup, "tier_depth_score")
    reasons: list[str] = []

    def fail(message: str) -> tuple[bool, list[str]]:
        return False, [message]

    if mission_type == "initial_profile_survey":
        visible_count = int(scenario.get("profile_visible_signal_count", total_preference))
        if visible_count < 35 and total_preference < 20:
            return True, ["sparse visible profile has too little usable evidence"]
        return fail("sparse-profile floor not met by visible survey evidence")

    if mission_type == "family_survey":
        if coverage_gap >= 0.20 and total_preference >= 3 and conflict >= 0.18:
            reasons.append("family has usable but uneven visible evidence")
            return True, reasons
        return fail("family coverage gap or uneven-evidence floor not met")

    if mission_type == "archetype_survey":
        if coverage_gap >= 0.18 and total_preference >= 2 and signals["positive_balance"] < 0.85:
            return True, ["archetype has direct evidence gap with nearby signal"]
        return fail("archetype survey floor needs low direct evidence plus nearby signal")

    if mission_type == "gateway_test":
        if coverage_gap >= 0.22 and positive_count >= 1 and gateway >= 0.55:
            return True, ["under-tested target has a visible gateway path"]
        return fail("gateway floor needs target gap, positive source, and coherent gateway")

    if mission_type == "song_to_archetype_test":
        if positive_count >= 1 and coverage_gap >= 0.20 and depth_gap >= 0.25:
            return True, ["strong song seed has weak surrounding archetype evidence"]
        return fail("song-to-archetype floor needs a positive song seed and surrounding gap")

    if mission_type == "artist_depth_test":
        if positive_count >= 1 and depth_gap >= 0.35 and tier_depth <= 0.75:
            return True, ["artist positive evidence has shallow depth coverage"]
        return fail("artist depth floor needs artist positivity plus shallow depth")

    if mission_type == "album_container_test":
        album_signal = positive_count >= 1 or "visible_album_context" in scenario.get("context_overlays", [])
        if album_signal and (depth_gap >= 0.28 or context_variability >= 0.35):
            return True, ["visible signal can test album/container context"]
        return fail("album container floor needs album signal or context-sidecar opportunity")

    if mission_type == "archetype_depth_test":
        if positive_count >= 2 and depth_gap >= 0.25 and signals["negative_balance"] <= 0.55:
            return True, ["positive archetype signal has shallow depth coverage"]
        return fail("archetype depth floor needs positive archetype signal and depth gap")

    if mission_type == "exception_scope_test":
        if positive_count >= 1 and (coverage_gap >= 0.22 or conflict >= 0.45):
            return True, ["strong seed object has uncertain generalization scope"]
        return fail("exception scope floor needs strong seed plus weak or mixed surroundings")

    if mission_type == "false_nearby_test":
        if positive_count >= 1 and negative_count >= 1 and conflict >= 0.55:
            return True, ["nearby positive and negative evidence can test misleading similarity"]
        return fail("false-nearby floor needs positive area, risky similar candidate, and control")

    if mission_type == "context_dependence_test":
        if context_variability >= 0.48 and context_skew >= 0.25 and positive_count + weak_count >= 1:
            return True, ["visible context variability leaves an unresolved context question"]
        return fail("context-dependence floor needs visible context variability and non-failure evidence")

    if mission_type == "bridge_test":
        if positive_count >= 1 and coverage_gap >= 0.20 and bridge >= 0.52:
            return True, ["positive source and under-tested target have bridge readiness"]
        return fail("bridge floor needs source positive evidence, target gap, and bridge readiness")

    if mission_type == "boundary_test":
        if positive_count >= 1 and negative_count >= 1 and conflict >= 0.45:
            return True, ["nearby visible reactions are mixed enough for a boundary test"]
        return fail("boundary floor needs visible mixed reactions in nearby graph space")

    if mission_type == "evidence_repair_test":
        if conflict >= 0.45 or context_variability >= 0.55 or rollup_metric(rollup, "recency_score") >= 0.85:
            return True, ["visible evidence has conflict, contamination, or recent surprise"]
        return fail("evidence repair floor needs a visible evidence issue")

    return fail("unsupported mission type for target-sensitive prototype")


def score_inputs_from_rollup(
    mission_definition: dict[str, Any],
    rollup: dict[str, Any],
    scenario: dict[str, Any],
    variant_index: int,
) -> tuple[float, float, float, float, float, float, float]:
    mission_type = mission_definition["mission_type"]
    signals = signal_strengths(rollup)
    positive = signals["positive"]
    negative = signals["negative"]
    non_failure = signals["non_failure"]
    survey_uncertainty = signals["survey_uncertainty"]
    coverage_gap = rollup_metric(rollup, "coverage_gap_score")
    conflict = rollup_metric(rollup, "conflict_score")
    context_variability = rollup_metric(rollup, "context_variability_score")
    context_skew = rollup_metric(rollup, "context_skew_score")
    tier_coverage = rollup_metric(rollup, "tier_coverage_score", 0.5)
    tier_depth = rollup_metric(rollup, "tier_depth_score", 0.5)
    depth_gap = rollup_metric(rollup, "depth_gap_score")
    bridge = rollup_metric(rollup, "bridge_readiness_score")
    gateway = rollup_metric(rollup, "gateway_to_representative_coherence_score")
    recency = rollup_metric(rollup, "recency_score", 0.7)
    risk = risk_input_for_rollup(rollup)

    if mission_type == "initial_profile_survey":
        fit = 0.58 * coverage_gap + 0.22 * survey_uncertainty + 0.20 * gateway
        readiness = 0.45 * tier_coverage + 0.35 * gateway + 0.20 * (1 - risk)
        learning = 0.60 * coverage_gap + 0.25 * survey_uncertainty + 0.15 * recency
    elif mission_type == "family_survey":
        fit = 0.42 * coverage_gap + 0.24 * conflict + 0.20 * non_failure + 0.14 * gateway
        readiness = 0.48 * tier_coverage + 0.30 * gateway + 0.22 * (1 - risk)
        learning = 0.48 * coverage_gap + 0.30 * conflict + 0.22 * depth_gap
    elif mission_type == "archetype_survey":
        fit = 0.42 * coverage_gap + 0.25 * non_failure + 0.18 * gateway + 0.15 * conflict
        readiness = 0.48 * tier_coverage + 0.32 * gateway + 0.20 * (1 - risk)
        learning = 0.46 * coverage_gap + 0.28 * depth_gap + 0.26 * conflict
    elif mission_type == "gateway_test":
        fit = 0.38 * coverage_gap + 0.32 * gateway + 0.20 * non_failure + 0.10 * bridge
        readiness = 0.48 * gateway + 0.28 * tier_coverage + 0.24 * (1 - risk)
        learning = 0.44 * coverage_gap + 0.34 * gateway + 0.22 * bridge
    elif mission_type == "song_to_archetype_test":
        fit = 0.42 * positive + 0.30 * coverage_gap + 0.18 * depth_gap + 0.10 * tier_coverage
        readiness = 0.40 * tier_coverage + 0.30 * non_failure + 0.30 * (1 - risk)
        learning = 0.42 * coverage_gap + 0.33 * depth_gap + 0.25 * positive
    elif mission_type == "artist_depth_test":
        fit = 0.38 * positive + 0.38 * depth_gap + 0.16 * tier_depth + 0.08 * coverage_gap
        readiness = 0.38 * tier_coverage + 0.32 * non_failure + 0.30 * (1 - risk)
        learning = 0.46 * depth_gap + 0.32 * positive + 0.22 * coverage_gap
    elif mission_type == "album_container_test":
        fit = 0.35 * positive + 0.28 * context_variability + 0.24 * depth_gap + 0.13 * tier_coverage
        readiness = 0.36 * tier_coverage + 0.30 * non_failure + 0.20 * context_variability + 0.14 * (1 - risk)
        learning = 0.34 * context_variability + 0.32 * depth_gap + 0.20 * coverage_gap + 0.14 * positive
    elif mission_type == "archetype_depth_test":
        fit = 0.40 * positive + 0.34 * depth_gap + 0.18 * tier_depth + 0.08 * (1 - negative)
        readiness = 0.42 * tier_coverage + 0.34 * non_failure + 0.24 * (1 - risk)
        learning = 0.46 * depth_gap + 0.34 * positive + 0.20 * coverage_gap
    elif mission_type == "exception_scope_test":
        fit = 0.34 * positive + 0.26 * conflict + 0.24 * coverage_gap + 0.16 * depth_gap
        readiness = 0.40 * tier_coverage + 0.32 * non_failure + 0.28 * (1 - risk)
        learning = 0.36 * conflict + 0.34 * coverage_gap + 0.20 * depth_gap + 0.10 * recency
    elif mission_type == "false_nearby_test":
        fit = 0.32 * conflict + 0.26 * positive + 0.22 * negative + 0.20 * tier_coverage
        readiness = 0.42 * tier_coverage + 0.28 * non_failure + 0.30 * (1 - risk)
        learning = 0.46 * conflict + 0.28 * coverage_gap + 0.26 * negative
    elif mission_type == "context_dependence_test":
        fit = 0.68 * context_variability + 0.24 * context_skew + 0.20 * conflict + 0.10 * non_failure
        readiness = 0.30 * tier_coverage + 0.24 * non_failure + 0.32 * context_variability + 0.14 * (1 - risk)
        learning = 0.64 * context_variability + 0.22 * conflict + 0.18 * coverage_gap + 0.18 * context_skew
    elif mission_type == "bridge_test":
        fit = 0.34 * bridge + 0.26 * positive + 0.24 * coverage_gap + 0.16 * gateway
        readiness = 0.36 * bridge + 0.28 * gateway + 0.22 * tier_coverage + 0.14 * (1 - risk)
        learning = 0.38 * coverage_gap + 0.32 * bridge + 0.18 * positive + 0.12 * recency
    elif mission_type == "boundary_test":
        fit = 0.42 * conflict + 0.20 * positive + 0.20 * negative + 0.18 * context_variability
        readiness = 0.40 * tier_coverage + 0.26 * non_failure + 0.20 * conflict + 0.14 * (1 - risk)
        learning = 0.48 * conflict + 0.22 * coverage_gap + 0.18 * context_variability + 0.12 * negative
    elif mission_type == "evidence_repair_test":
        fit = 0.70 * conflict + 0.25 * recency + 0.20 * context_variability + 0.10 * coverage_gap
        readiness = 0.34 * tier_coverage + 0.24 * non_failure + 0.28 * recency + 0.14 * (1 - risk)
        learning = 0.62 * conflict + 0.22 * context_variability + 0.18 * coverage_gap + 0.20 * recency
    else:
        fit = readiness = learning = 0.0

    decay = max(0, variant_index - 1) * 0.075
    fit = bounded(fit - decay)
    readiness = bounded(readiness - decay * 0.75)
    learning = bounded(learning - decay * 0.65)
    value_input = bounded(0.60 + 0.24 * fit + 0.16 * learning - risk * 0.08)
    repetition = bounded(max(0.0, rollup_metric(rollup, "evidence_density") - coverage_gap * 0.35))
    complexity = bounded(BAND_COMPLEXITY[mission_definition["value_band"]] + risk * 0.25)
    return (value_input, fit, readiness, learning, risk, repetition, complexity)


def candidate_specs_for_mission(
    mission_definition: dict[str, Any],
    scenarios: dict[str, dict[str, Any]],
    profile: str,
) -> tuple[list[CandidateSpec], list[dict[str, Any]]]:
    mission_type = mission_definition["mission_type"]
    scenario_id = MISSION_SCENARIOS[mission_type]
    if scenario_id not in scenarios:
        raise KeyError(f"missing synthetic scenario for {mission_type}: {scenario_id}")
    scenario = scenarios[scenario_id]
    band = mission_definition["value_band"]
    target_rollup_level = MISSION_TARGET_ROLLUP_LEVEL.get(
        mission_type,
        mission_definition["required_blob_shape"]["target_object_types"][0],
    )
    allowed_target_types = mission_definition["required_blob_shape"]["target_object_types"]
    target_object_type = (
        target_rollup_level
        if target_rollup_level in allowed_target_types
        else allowed_target_types[0]
    )
    target_rollup_level, rollup = target_rollup_for_mission(
        mission_definition,
        scenario,
        target_object_type,
    )
    sensitive = profile_sensitive_fixture(scenarios)
    should_generate, reasons = generation_check(mission_definition, scenario, rollup, sensitive)
    non_generation_reasons: list[dict[str, Any]] = []
    if not should_generate:
        non_generation_reasons.append(
            {
                "mission_type": mission_type,
                "reason": reasons[0],
                "evidence_refs": [
                    str(rollup.get("rollup_id", f"synthetic_rollup:{scenario_id}"))
                ],
            }
        )
        return [], non_generation_reasons

    if sensitive:
        inputs_seed = score_inputs_from_rollup(mission_definition, rollup, scenario, 0)
        strength = (inputs_seed[1] + inputs_seed[2] + inputs_seed[3]) / 3
        eligible_count = 5 if strength >= 0.56 else 4
    else:
        counts = EARLY_STOP_ELIGIBLE_COUNTS if profile == "early_stop" else COVERAGE_ELIGIBLE_COUNTS
        eligible_count = counts[band]
    specs: list[CandidateSpec] = []

    for index in range(eligible_count):
        inputs = (
            score_inputs_from_rollup(mission_definition, rollup, scenario, index)
            if sensitive
            else eligible_inputs(mission_definition, profile, index)
        )
        duplicate_variant = sensitive and index == 1
        target_suffix = "" if index == 0 or duplicate_variant else f"_candidate_{index:02d}"
        display_suffix = "" if index == 0 or duplicate_variant else f"(candidate {index:02d})"
        specs.append(
            CandidateSpec(
                mission_type=mission_type,
                scenario_id=scenario_id,
                profile_id=str(scenario.get("profile_id", "synthetic")),
                variant_kind="eligible",
                variant_index=index,
                target_object_type=target_object_type,
                target_rollup_level=target_rollup_level,
                target_id_suffix=target_suffix,
                target_display_suffix=display_suffix,
                mission_type_value_input=inputs[0],
                mission_fit_input=inputs[1],
                readiness_input=inputs[2],
                learning_value_input=inputs[3],
                risk_input=inputs[4],
                repetition_input=inputs[5],
                complexity_input=inputs[6],
                floor_score=bounded(
                    mission_definition["score_floor"]
                    + 0.02
                    + min(inputs[1], inputs[2], inputs[3]) * 0.06
                    - max(0, index - 1) * 0.015
                ),
                required_inputs_available=True,
                graph_context_available=True,
                generation_reasons=tuple(reasons),
            )
        )

    low_inputs = (
        score_inputs_from_rollup(mission_definition, rollup, scenario, eligible_count + 1)
        if sensitive
        else (0.35, 0.15, 0.15, 0.15, 0.85, 0.6, 0.6)
    )
    specs.append(
        CandidateSpec(
            mission_type=mission_type,
            scenario_id=scenario_id,
            profile_id=str(scenario.get("profile_id", "synthetic")),
            variant_kind="floor_fail",
            variant_index=eligible_count,
            target_object_type=target_object_type,
            target_rollup_level=target_rollup_level,
            target_id_suffix=f"_floor_fail_{eligible_count:02d}",
            target_display_suffix=f"(floor fail {eligible_count:02d})",
            mission_type_value_input=0.4,
            mission_fit_input=0.2,
            readiness_input=0.2,
            learning_value_input=0.2,
            risk_input=0.4,
            repetition_input=0.2,
            complexity_input=0.2,
            floor_score=bounded(max(0, mission_definition["score_floor"] - 0.08)),
            required_inputs_available=True,
            graph_context_available=True,
            generation_reasons=tuple(reasons),
        )
    )
    specs.append(
        CandidateSpec(
            mission_type=mission_type,
            scenario_id=scenario_id,
            profile_id=str(scenario.get("profile_id", "synthetic")),
            variant_kind="low_score",
            variant_index=eligible_count + 1,
            target_object_type=target_object_type,
            target_rollup_level=target_rollup_level,
            target_id_suffix=f"_low_score_{eligible_count + 1:02d}",
            target_display_suffix=f"(low score {eligible_count + 1:02d})",
            mission_type_value_input=bounded(low_inputs[0] * 0.72),
            mission_fit_input=bounded(low_inputs[1] * 0.45),
            readiness_input=bounded(low_inputs[2] * 0.45),
            learning_value_input=bounded(low_inputs[3] * 0.45),
            risk_input=bounded(max(low_inputs[4], 0.75)),
            repetition_input=bounded(max(low_inputs[5], 0.55)),
            complexity_input=bounded(max(low_inputs[6], 0.55)),
            floor_score=bounded(mission_definition["score_floor"] + 0.02),
            required_inputs_available=True,
            graph_context_available=True,
            generation_reasons=tuple(reasons),
        )
    )

    return specs, non_generation_reasons


def selector_summary_for_mission(
    mission_type: str,
    generator_id: str,
    eligible_candidate_count: int,
    emitted_candidate_count: int,
    floor_failed_candidate_count: int,
    pruned_candidate_count: int,
    cap_value: int,
) -> dict[str, Any]:
    return {
        "mission_type": mission_type,
        "generator_id": generator_id,
        "eligible_candidate_count": eligible_candidate_count,
        "emitted_candidate_count": emitted_candidate_count,
        "floor_failed_candidate_count": floor_failed_candidate_count,
        "pruned_candidate_count": pruned_candidate_count,
        "cap_applied": eligible_candidate_count > cap_value,
        "cap_value": cap_value,
    }


def opportunity_summary_for_mission(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "generator_id": summary["generator_id"],
        "batch_index": 0,
        "input_rollup_refs": [f"synthetic_generator:{summary['mission_type']}"],
        "eligible_candidate_count": summary["eligible_candidate_count"],
        "emitted_candidate_count": summary["emitted_candidate_count"],
        "pruned_candidate_count": summary["pruned_candidate_count"],
        "floor_failed_candidate_count": summary["floor_failed_candidate_count"],
        "cap_applied": summary["cap_applied"],
        "cap_value": summary["cap_value"],
        "batch_size": min(summary["eligible_candidate_count"], summary["cap_value"]),
        "generation_notes": [
            "Offline synthetic selector prototype only.",
            "No runtime evidence, catalog, playback, or canonical graph authority was read.",
        ],
    }


def opportunity_duplicate_key(opportunity: dict[str, Any]) -> tuple[str, tuple[str, ...]]:
    return (
        opportunity["mission_type"],
        tuple(opportunity["target_object_ids"]),
    )


def remove_heap_opportunity(
    heap: list[tuple[float, int, dict[str, Any]]],
    opportunity_id: str,
) -> dict[str, Any] | None:
    for index, item in enumerate(heap):
        if item[2]["opportunity_id"] == opportunity_id:
            removed = heap.pop(index)[2]
            heapq.heapify(heap)
            return removed
    return None


def duplicate_control_summary(
    ranked: list[dict[str, Any]],
    suppressed_examples: list[dict[str, Any]],
) -> dict[str, Any]:
    exact_counter = Counter(
        (opportunity["mission_type"], tuple(opportunity["target_object_ids"]))
        for opportunity in ranked
    )
    target_counter = Counter(tuple(opportunity["target_object_ids"]) for opportunity in ranked)
    mission_counter = Counter(opportunity["mission_type"] for opportunity in ranked)
    total = max(1, len(ranked))
    concentration = [
        {
            "mission_type": mission_type,
            "count": count,
            "share": bounded(count / total),
        }
        for mission_type, count in mission_counter.most_common()
    ]
    return {
        "exact_duplicate_mission_type_target_count": sum(
            count - 1 for count in exact_counter.values() if count > 1
        ),
        "duplicate_target_object_count": sum(
            count - 1 for count in target_counter.values() if count > 1
        ),
        "mission_type_concentration": concentration,
        "suppressed_exact_duplicate_count": len(suppressed_examples),
        "suppressed_duplicate_examples": suppressed_examples[:20],
    }


def run_selector(
    registry: dict[str, Any],
    scenario_fixture: dict[str, Any],
    profile: str,
) -> dict[str, Any]:
    scenarios = {
        scenario["scenario_id"]: scenario
        for scenario in scenario_fixture["scenario_rollups"]
    }
    registry_order = {
        mission["mission_type"]: index
        for index, mission in enumerate(registry["mission_types"])
    }
    mission_definitions = sorted(
        registry["mission_types"],
        key=lambda mission: (-mission["score_ceiling"], registry_order[mission["mission_type"]]),
    )

    heap: list[tuple[float, int, dict[str, Any]]] = []
    selected_duplicate_keys: dict[tuple[str, tuple[str, ...]], tuple[str, float]] = {}
    sequence = 0
    audit_summaries: list[dict[str, Any]] = []
    floor_failure_examples: list[dict[str, Any]] = []
    non_generation_reasons: list[dict[str, Any]] = []
    suppressed_duplicate_examples: list[dict[str, Any]] = []
    mission_types_considered: list[str] = []
    mission_types_skipped: list[str] = []
    candidate_blobs_generated = 0
    candidate_blobs_floor_passed = 0
    candidate_blobs_scored = 0
    candidate_blobs_pruned = 0
    early_stop_applied = False
    early_stop_reason: str | None = None
    remaining_ceiling_at_stop: float | None = None

    for index, mission_definition in enumerate(mission_definitions):
        remaining_ceiling = max(
            mission["score_ceiling"] for mission in mission_definitions[index:]
        )
        cutoff = heap[0][0] if len(heap) == TOP_K else None
        if len(heap) == TOP_K and cutoff is not None and cutoff > remaining_ceiling:
            early_stop_applied = True
            remaining_ceiling_at_stop = remaining_ceiling
            early_stop_reason = (
                f"25th best score {cutoff:.4f} exceeded remaining ceiling "
                f"{remaining_ceiling:.4f}"
            )
            mission_types_skipped = [
                mission["mission_type"] for mission in mission_definitions[index:]
            ]
            for skipped_definition in mission_definitions[index:]:
                _skipped_specs, skipped_non_generation = candidate_specs_for_mission(
                    skipped_definition,
                    scenarios,
                    profile,
                )
                non_generation_reasons.extend(skipped_non_generation)
            break

        mission_type = mission_definition["mission_type"]
        mission_types_considered.append(mission_type)
        specs, generation_suppression = candidate_specs_for_mission(
            mission_definition,
            scenarios,
            profile,
        )
        non_generation_reasons.extend(generation_suppression)
        cap_value = mission_definition["candidate_generation_caps"]["max_candidates_total"]
        specs = specs[:cap_value]
        generator_id = f"synthetic_{mission_type}_selector_generator_v0_1"
        mission_heap_candidates: list[dict[str, Any]] = []
        mission_floor_failed = 0
        mission_pruned = 0
        mission_emitted = 0

        for spec in specs:
            scenario = scenarios[spec.scenario_id]
            candidate_blobs_generated += 1
            floor_passed, failed_requirements, fail_reasons = floor_details(
                mission_definition,
                spec,
            )
            components = score_candidate(mission_definition, spec)
            provisional_summary = opportunity_summary_for_mission(
                selector_summary_for_mission(
                    mission_type,
                    generator_id,
                    len(specs),
                    0,
                    0,
                    0,
                    cap_value,
                )
            )
            opportunity = build_opportunity(
                mission_definition,
                scenario,
                spec,
                components,
                floor_passed,
                failed_requirements,
                fail_reasons,
                provisional_summary,
            )

            if not floor_passed:
                mission_floor_failed += 1
                if len(floor_failure_examples) < 20:
                    floor_failure_examples.append(
                        {
                            "mission_type": mission_type,
                            "opportunity_id": spec.opportunity_id,
                            "failed_requirements": failed_requirements,
                            "fail_reasons": fail_reasons,
                        }
                    )
                continue

            candidate_blobs_floor_passed += 1
            candidate_blobs_scored += 1

            if components["final_opportunity_score"] < mission_definition["score_floor"]:
                mission_pruned += 1
                candidate_blobs_pruned += 1
                continue

            duplicate_key = opportunity_duplicate_key(opportunity)
            existing = selected_duplicate_keys.get(duplicate_key)
            if existing is not None:
                existing_id, existing_score = existing
                if existing_score >= components["final_opportunity_score"]:
                    candidate_blobs_pruned += 1
                    mission_pruned += 1
                    if len(suppressed_duplicate_examples) < 20:
                        suppressed_duplicate_examples.append(
                            {
                                "mission_type": mission_type,
                                "opportunity_id": opportunity["opportunity_id"],
                                "duplicate_of_opportunity_id": existing_id,
                                "target_object_ids": opportunity["target_object_ids"],
                                "reason": "exact mission_type + target_object_ids duplicate suppressed",
                            }
                        )
                    continue
                removed = remove_heap_opportunity(heap, existing_id)
                if removed is not None:
                    candidate_blobs_pruned += 1
                    if len(suppressed_duplicate_examples) < 20:
                        suppressed_duplicate_examples.append(
                            {
                                "mission_type": removed["mission_type"],
                                "opportunity_id": removed["opportunity_id"],
                                "duplicate_of_opportunity_id": opportunity["opportunity_id"],
                                "target_object_ids": removed["target_object_ids"],
                                "reason": "lower-scoring exact duplicate replaced",
                            }
                        )

            heapq.heappush(heap, (components["final_opportunity_score"], sequence, opportunity))
            selected_duplicate_keys[duplicate_key] = (
                opportunity["opportunity_id"],
                components["final_opportunity_score"],
            )
            sequence += 1
            mission_emitted += 1
            mission_heap_candidates.append(opportunity)
            if len(heap) > TOP_K:
                popped = heapq.heappop(heap)[2]
                popped_key = opportunity_duplicate_key(popped)
                if selected_duplicate_keys.get(popped_key, ("", 0))[0] == popped["opportunity_id"]:
                    selected_duplicate_keys.pop(popped_key, None)
                candidate_blobs_pruned += 1
                if popped["mission_type"] == mission_type:
                    mission_pruned += 1

        summary = selector_summary_for_mission(
            mission_type,
            generator_id,
            len(specs),
            mission_emitted,
            mission_floor_failed,
            mission_pruned,
            cap_value,
        )
        for opportunity in mission_heap_candidates:
            opportunity["candidate_generation_summary"] = opportunity_summary_for_mission(summary)
        audit_summaries.append(summary)

    ranked = [
        item[2]
        for item in sorted(heap, key=lambda entry: (-entry[0], entry[1]))
    ]
    cutoff_score = ranked[-1]["score_components"]["final_opportunity_score"] if ranked else None
    duplicate_summary = duplicate_control_summary(ranked, suppressed_duplicate_examples)

    return {
        "contract_version": "selector_output_v0_1",
        "fixture_status": "synthetic_contract_fixture",
        "selector_run_id": f"synthetic_selector_prototype_{profile}_v0_1",
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "runtime_allowed": False,
        "production_mission_generation_allowed": False,
        "canonical_graph_mutation_allowed": False,
        "listener_preference_inference_from_affinity_allowed": False,
        "opportunity_only": True,
        "source_registry_ref": str(DEFAULT_REGISTRY.relative_to(REPO_ROOT)),
        "source_evidence_rollup_ref": str(DEFAULT_SCENARIOS.relative_to(REPO_ROOT)),
        "global_top_k_opportunities": TOP_K,
        "selector_audit": {
            "selection_mode": "offline_synthetic_fixture",
            "mission_types_considered": mission_types_considered,
            "mission_types_skipped_by_early_stop": mission_types_skipped,
            "mission_types_sorted_by_descending_ceiling": True,
            "global_heap_maintained": True,
            "heap_max_size": TOP_K,
            "candidate_blobs_generated": candidate_blobs_generated,
            "candidate_blobs_floor_passed": candidate_blobs_floor_passed,
            "candidate_blobs_scored": candidate_blobs_scored,
            "candidate_blobs_pruned": candidate_blobs_pruned,
            "final_heap_size": len(ranked),
            "early_stop_applied": early_stop_applied,
            "early_stop_reason": early_stop_reason,
            "remaining_ceiling_at_stop": remaining_ceiling_at_stop,
            "cutoff_score": cutoff_score,
            "floor_failure_examples": floor_failure_examples,
            "non_generation_reasons": non_generation_reasons,
            "candidate_generation_summaries": audit_summaries,
            "duplicate_control_summary": duplicate_summary,
            "audit_notes": [
                "Offline synthetic selector prototype output.",
                "Scoring uses score floors as a mission-type prior; target fit/readiness/learning are weighted more heavily than mission type value.",
                "Survey ok is ignored; mission/song-review ok is weak non-failure only.",
                "Conditional generation suppresses mission types whose visible target rollups do not plausibly support floors.",
                "No final mission content, playback plan, catalog resolution, app storage, or canonical graph mutation is present.",
            ],
        },
        "ranked_opportunities": ranked,
    }


def summarize(selector_output: dict[str, Any]) -> str:
    audit = selector_output["selector_audit"]
    top_types = [
        opportunity["mission_type"]
        for opportunity in selector_output["ranked_opportunities"][:10]
    ]
    return "\n".join(
        [
            f"selector_run_id: {selector_output['selector_run_id']}",
            f"ranked_opportunities: {len(selector_output['ranked_opportunities'])}",
            f"top_10_mission_types: {', '.join(top_types)}",
            f"candidate_blobs_generated: {audit['candidate_blobs_generated']}",
            f"candidate_blobs_floor_passed: {audit['candidate_blobs_floor_passed']}",
            f"candidate_blobs_scored: {audit['candidate_blobs_scored']}",
            f"candidate_blobs_pruned: {audit['candidate_blobs_pruned']}",
            f"cutoff_score: {audit['cutoff_score']}",
            f"early_stop_applied: {audit['early_stop_applied']}",
            f"early_stop_reason: {audit['early_stop_reason']}",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the offline synthetic Mission Opportunity Selection v0.1 prototype."
    )
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--scenarios", type=Path, default=DEFAULT_SCENARIOS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--profile",
        choices=["coverage", "early_stop"],
        default="coverage",
        help="coverage processes all mission types; early_stop demonstrates ceiling-based stop.",
    )
    args = parser.parse_args()

    registry = load_json(args.registry)
    scenario_fixture = load_json(args.scenarios)
    output = run_selector(registry, scenario_fixture, args.profile)
    write_json(args.output, output)
    print(summarize(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
