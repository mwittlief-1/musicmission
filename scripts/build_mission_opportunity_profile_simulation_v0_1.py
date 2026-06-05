#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DIR = REPO_ROOT / "data/product_contracts/mission_opportunity_selection_v0_1"
FIXTURE_DIR = CONTRACT_DIR / "fixtures"
PROFILE_SIM_DIR = FIXTURE_DIR / "profile_simulation"
VISIBLE_OUTPUT = PROFILE_SIM_DIR / "visible_profile_selector_inputs_v0_1.json"
HIDDEN_OUTPUT = PROFILE_SIM_DIR / "hidden_profile_oracles_v0_1.json"
SUMMARY_OUTPUT = PROFILE_SIM_DIR / "profile_selector_phase1_summary_v0_1.json"
REGISTRY_PATH = FIXTURE_DIR / "mission_type_registry_sample_v0_1.json"

SURVEY_EXPORT_DIR = REPO_ROOT / "data/survey_simulation/survey_evidence_export/samples"
HIDDEN_TRUTH_DIR = (
    REPO_ROOT
    / "data/survey_simulation/llm_profile_review/api_pilot_3x3/simulator_private/hidden_truth_packets"
)
HIDDEN_CORPUS_DIR = REPO_ROOT / "data/survey_simulation/hidden_reaction_corpora"

PROFILE_IDS = ["01", "05", "06"]

EXPECTED_BEHAVIOR = {
    "01": {
        "likely_top_mission_types": [
            "bridge_test",
            "boundary_test",
            "evidence_repair_test",
            "album_container_test",
        ],
        "mission_types_that_should_fail_floors": [
            "artist_depth_test",
            "song_to_archetype_test",
        ],
        "mission_types_that_should_be_suppressed": [
            "initial_profile_survey",
        ],
    },
    "05": {
        "likely_top_mission_types": [
            "boundary_test",
            "evidence_repair_test",
            "context_dependence_test",
            "song_to_archetype_test",
        ],
        "mission_types_that_should_fail_floors": [
            "family_survey",
        ],
        "mission_types_that_should_be_suppressed": [
            "initial_profile_survey",
        ],
    },
    "06": {
        "likely_top_mission_types": [
            "context_dependence_test",
            "boundary_test",
            "evidence_repair_test",
            "album_container_test",
        ],
        "mission_types_that_should_fail_floors": [
            "false_nearby_test",
        ],
        "mission_types_that_should_be_suppressed": [
            "initial_profile_survey",
        ],
    },
}

SCENARIO_TEMPLATES = [
    {
        "scenario_id": "sparse_post_intake_survey_ok",
        "description": "Visible public survey export with survey ok values ignored.",
        "expected_top_mission_types": ["initial_profile_survey", "family_survey"],
        "node_tier": "gateway",
        "graph_item_role": "gateway",
        "context_overlays": [],
        "risk_flags": [],
        "coverage_factor": 1.0,
        "depth_factor": 1.0,
        "conflict_factor": 0.3,
        "context_factor": 0.2,
    },
    {
        "scenario_id": "one_strong_song_weak_archetype",
        "description": "Visible evidence has one strong song/artist/album anchor and weak surrounding detail.",
        "expected_top_mission_types": ["song_to_archetype_test", "exception_scope_test"],
        "node_tier": "primary",
        "graph_item_role": "canonical_anchor",
        "context_overlays": [],
        "risk_flags": ["one_object_overfit_risk"],
        "coverage_factor": 0.75,
        "depth_factor": 1.0,
        "conflict_factor": 0.35,
        "context_factor": 0.25,
    },
    {
        "scenario_id": "family_positive_weak_archetype_clarity",
        "description": "Visible family-level signal has several positives but archetype detail remains uneven.",
        "expected_top_mission_types": ["family_survey", "archetype_survey", "gateway_test"],
        "node_tier": "major",
        "graph_item_role": "major_representative",
        "context_overlays": [],
        "risk_flags": [],
        "coverage_factor": 0.65,
        "depth_factor": 0.85,
        "conflict_factor": 0.3,
        "context_factor": 0.2,
    },
    {
        "scenario_id": "strong_archetype_shallow_depth",
        "description": "Visible archetype signal is strong but depth coverage is shallow.",
        "expected_top_mission_types": ["archetype_depth_test"],
        "node_tier": "primary",
        "graph_item_role": "canonical_anchor",
        "context_overlays": ["visible_depth_probe"],
        "risk_flags": [],
        "coverage_factor": 0.45,
        "depth_factor": 1.0,
        "conflict_factor": 0.25,
        "context_factor": 0.3,
    },
    {
        "scenario_id": "one_artist_shallow_depth",
        "description": "Visible artist-level anchor has limited depth proof.",
        "expected_top_mission_types": ["artist_depth_test", "exception_scope_test"],
        "node_tier": "major",
        "graph_item_role": "artist_anchor",
        "context_overlays": [],
        "risk_flags": ["one_artist_overfit_risk"],
        "coverage_factor": 0.55,
        "depth_factor": 1.0,
        "conflict_factor": 0.3,
        "context_factor": 0.2,
    },
    {
        "scenario_id": "one_album_container_signal",
        "description": "Visible album signal suggests possible container learning.",
        "expected_top_mission_types": ["album_container_test"],
        "node_tier": "supporting",
        "graph_item_role": "album_world",
        "context_overlays": ["visible_album_context"],
        "risk_flags": ["single_hit_overfit_risk"],
        "coverage_factor": 0.55,
        "depth_factor": 0.85,
        "conflict_factor": 0.35,
        "context_factor": 0.45,
    },
    {
        "scenario_id": "bridge_source_positive_target_gap",
        "description": "Visible positive source area plus under-tested adjacent target.",
        "expected_top_mission_types": ["bridge_test", "gateway_test"],
        "node_tier": "major",
        "graph_item_role": "bridge",
        "context_overlays": ["visible_bridge_context"],
        "risk_flags": ["safe_gateway"],
        "coverage_factor": 0.7,
        "depth_factor": 0.7,
        "conflict_factor": 0.3,
        "context_factor": 0.35,
    },
    {
        "scenario_id": "mixed_nearby_boundary",
        "description": "Visible survey has mixed nearby positive and negative reactions.",
        "expected_top_mission_types": ["boundary_test", "false_nearby_test", "evidence_repair_test"],
        "node_tier": "contextual",
        "graph_item_role": "boundary",
        "context_overlays": ["visible_boundary_context"],
        "risk_flags": ["requires_framing"],
        "coverage_factor": 0.45,
        "depth_factor": 0.6,
        "conflict_factor": 1.0,
        "context_factor": 0.55,
    },
    {
        "scenario_id": "context_heavy_signals",
        "description": "Visible survey suggests context may explain inconsistent reactions.",
        "expected_top_mission_types": ["context_dependence_test", "evidence_repair_test"],
        "node_tier": "contextual",
        "graph_item_role": "contextual_object",
        "context_overlays": ["visible_context_heavy", "visible_comparator_needed"],
        "risk_flags": ["context_only_risk"],
        "coverage_factor": 0.5,
        "depth_factor": 0.65,
        "conflict_factor": 0.65,
        "context_factor": 1.0,
    },
    {
        "scenario_id": "recent_surprise_signal",
        "description": "Visible evidence includes a recent surprising love/dislike pattern.",
        "expected_top_mission_types": ["evidence_repair_test", "exception_scope_test"],
        "node_tier": "major",
        "graph_item_role": "boundary",
        "context_overlays": ["visible_recent_learning"],
        "risk_flags": ["recent_contradiction"],
        "coverage_factor": 0.5,
        "depth_factor": 0.75,
        "conflict_factor": 0.8,
        "context_factor": 0.5,
    },
    {
        "scenario_id": "high_signal_low_survey_dominated",
        "description": "Visible high-signal profile where low-value survey missions should be dominated.",
        "expected_top_mission_types": ["boundary_test", "bridge_test", "evidence_repair_test"],
        "node_tier": "primary",
        "graph_item_role": "canonical_anchor",
        "context_overlays": ["visible_high_signal"],
        "risk_flags": [],
        "coverage_factor": 0.35,
        "depth_factor": 0.35,
        "conflict_factor": 0.7,
        "context_factor": 0.65,
    },
]


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


def atom_raw_reaction(atom: dict[str, Any]) -> str:
    return atom.get("reaction", {}).get("raw_value", "unknown")


def atom_object_id(atom: dict[str, Any]) -> str:
    ref = atom.get("music_object_ref", {})
    return str(
        ref.get("canonical_song_recording_id")
        or ref.get("canonical_artist_id")
        or ref.get("canonical_album_id")
        or ref.get("object_id")
        or ref.get("display_name")
        or "unknown_object"
    )


def bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 4)


def rollup_from_atoms(
    object_level: str,
    target_object_id: str,
    display_name: str,
    atoms: list[dict[str, Any]],
    context_seed: float,
    risk_flags: list[str] | None = None,
) -> dict[str, Any]:
    counts = Counter(atom_raw_reaction(atom) for atom in atoms)
    positive = counts["love"] + counts["like"]
    negative = counts["dont_like"] + counts["dislike"]
    ok_ignored = counts["ok"]
    total = max(1, len(atoms))
    preference_total = max(1, positive + negative)
    ok_ratio = ok_ignored / total
    evidence_density = bounded((positive + negative) / total)
    coverage_gap = bounded(1 - evidence_density)
    conflict = bounded((min(positive, negative) * 2) / preference_total)
    roles = {
        role
        for atom in atoms
        for role in atom.get("graph_refs", {}).get("roles", [])
    }
    gateway_role = 1.0 if roles.intersection({"gateway", "bridge", "song_first"}) else 0.0
    tier_coverage = bounded(min(1.0, len(roles) / 5) if roles else 0.35)
    tier_depth = bounded(min(1.0, preference_total / 5))
    recency_values = [
        atom.get("apple_exposure_prior", {})
        .get("dimensions", {})
        .get("recency_score")
        for atom in atoms
    ]
    recency_numbers = [float(value) for value in recency_values if isinstance(value, (int, float))]
    recency = bounded(sum(recency_numbers) / len(recency_numbers)) if recency_numbers else 0.74
    positive_strength = positive / max(1, total)
    context_variability = bounded(ok_ratio * 0.42 + conflict * 0.38 + context_seed * 0.20)
    context_skew = bounded(ok_ratio * 0.58 + context_seed * 0.24)

    return {
        "rollup_id": f"visible_rollup:{object_level}:{target_object_id}",
        "object_level": object_level,
        "target_object_id": str(target_object_id),
        "display_name": display_name,
        "positive_signal_count": positive,
        "negative_signal_count": negative,
        "weak_non_failure_signal_count": 0,
        "survey_ok_ignored_count": ok_ignored,
        "mission_ok_weak_count": 0,
        "evidence_density": evidence_density,
        "coverage_gap_score": coverage_gap,
        "conflict_score": conflict,
        "context_variability_score": context_variability,
        "context_skew_score": context_skew,
        "tier_coverage_score": tier_coverage,
        "tier_depth_score": tier_depth,
        "depth_gap_score": bounded(1 - tier_depth),
        "bridge_readiness_score": bounded(
            0.18 + positive_strength * 0.42 + coverage_gap * 0.25 + gateway_role * 0.15
        ),
        "gateway_to_representative_coherence_score": bounded(
            0.18 + gateway_role * 0.34 + tier_coverage * 0.24 + positive_strength * 0.24
        ),
        "recency_score": recency,
        "risk_flags": risk_flags or [],
        "identity_flags": [],
    }


def empty_rollup(object_level: str, target_object_id: str, display_name: str) -> dict[str, Any]:
    return rollup_from_atoms(object_level, target_object_id, display_name, [], 0.2)


def best_group(
    groups: dict[str, list[dict[str, Any]]],
    names: dict[str, str],
    object_level: str,
    context_seed: float,
) -> dict[str, Any]:
    if not groups:
        return empty_rollup(object_level, f"visible_{object_level}_unknown", f"Visible {object_level.title()} Unknown")

    def score(atoms: list[dict[str, Any]]) -> tuple[int, int, int]:
        counts = Counter(atom_raw_reaction(atom) for atom in atoms)
        positive = counts["love"] + counts["like"]
        negative = counts["dont_like"] + counts["dislike"]
        return (positive, positive + negative, len(atoms))

    target_id, atoms = next(iter(groups.items()))
    best_score = score(atoms)
    for candidate_id, candidate_atoms in groups.items():
        candidate_score = score(candidate_atoms)
        if candidate_score > best_score:
            target_id = candidate_id
            atoms = candidate_atoms
            best_score = candidate_score
    return rollup_from_atoms(
        object_level,
        target_id,
        names.get(target_id, f"Visible {object_level.title()} {target_id}"),
        atoms,
        context_seed,
    )


def mixed_group(
    groups: dict[str, list[dict[str, Any]]],
    names: dict[str, str],
    object_level: str,
    context_seed: float,
) -> dict[str, Any]:
    if not groups:
        return empty_rollup(object_level, f"visible_{object_level}_mixed", f"Visible {object_level.title()} Mixed")

    def score(atoms: list[dict[str, Any]]) -> tuple[float, int]:
        counts = Counter(atom_raw_reaction(atom) for atom in atoms)
        positive = counts["love"] + counts["like"]
        negative = counts["dont_like"] + counts["dislike"]
        preference_total = max(1, positive + negative)
        conflict = (min(positive, negative) * 2) / preference_total
        return (conflict, preference_total)

    target_id, atoms = next(iter(groups.items()))
    best_score = score(atoms)
    for candidate_id, candidate_atoms in groups.items():
        candidate_score = score(candidate_atoms)
        if candidate_score > best_score:
            target_id = candidate_id
            atoms = candidate_atoms
            best_score = candidate_score
    return rollup_from_atoms(
        object_level,
        target_id,
        names.get(target_id, f"Visible {object_level.title()} {target_id}"),
        atoms,
        context_seed,
    )


def combine_pair_rollup(
    object_level: str,
    source: dict[str, Any],
    target: dict[str, Any],
    context_seed: float,
) -> dict[str, Any]:
    positive = int(source["positive_signal_count"])
    negative = int(target["negative_signal_count"])
    ok_ignored = int(target["survey_ok_ignored_count"])
    source_strength = positive / max(
        1,
        positive
        + int(source["negative_signal_count"])
        + int(source["survey_ok_ignored_count"]),
    )
    coverage_gap = bounded(max(source["coverage_gap_score"] * 0.25, target["coverage_gap_score"]))
    conflict = bounded(max(source["conflict_score"] * 0.5, target["conflict_score"]))
    return {
        "rollup_id": f"visible_rollup:{object_level}:{source['target_object_id']}->{target['target_object_id']}",
        "object_level": object_level,
        "target_object_id": f"{source['target_object_id']}->{target['target_object_id']}",
        "display_name": f"{source['display_name']} -> {target['display_name']}",
        "positive_signal_count": positive,
        "negative_signal_count": negative,
        "weak_non_failure_signal_count": 0,
        "survey_ok_ignored_count": ok_ignored,
        "mission_ok_weak_count": 0,
        "evidence_density": bounded((source["evidence_density"] + target["evidence_density"]) / 2),
        "coverage_gap_score": coverage_gap,
        "conflict_score": conflict,
        "context_variability_score": bounded(
            (source["context_variability_score"] + target["context_variability_score"]) / 2
            + context_seed * 0.18
        ),
        "context_skew_score": bounded(
            (source["context_skew_score"] + target["context_skew_score"]) / 2
            + context_seed * 0.12
        ),
        "tier_coverage_score": bounded((source["tier_coverage_score"] + target["tier_coverage_score"]) / 2),
        "tier_depth_score": bounded((source["tier_depth_score"] + target["tier_depth_score"]) / 2),
        "depth_gap_score": bounded(max(source["depth_gap_score"], target["depth_gap_score"])),
        "bridge_readiness_score": bounded(
            0.22
            + source_strength * 0.32
            + coverage_gap * 0.28
            + target["gateway_to_representative_coherence_score"] * 0.18
        ),
        "gateway_to_representative_coherence_score": bounded(
            (source["gateway_to_representative_coherence_score"] + target["gateway_to_representative_coherence_score"]) / 2
        ),
        "recency_score": bounded(max(source["recency_score"], target["recency_score"])),
        "risk_flags": [],
        "identity_flags": [],
    }


def target_level_rollups(
    atoms: list[dict[str, Any]],
    computed: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    families: dict[str, list[dict[str, Any]]] = defaultdict(list)
    family_names: dict[str, str] = {}
    archetypes: dict[str, list[dict[str, Any]]] = defaultdict(list)
    archetype_names: dict[str, str] = {}
    objects: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    object_names: dict[tuple[str, str], str] = {}

    for atom in atoms:
        display = atom.get("music_object_ref", {}).get("display_name", "Visible Object")
        for family_number in atom.get("graph_refs", {}).get("family_numbers", []):
            family_id = f"family_{family_number}"
            families[family_id].append(atom)
            family_names[family_id] = f"Visible Family {family_number}"
        for archetype_id in atom.get("graph_refs", {}).get("archetype_ids", []):
            archetype_key = str(archetype_id)
            archetypes[archetype_key].append(atom)
            archetype_names[archetype_key] = f"Visible Archetype {archetype_id}"
        ref = atom.get("music_object_ref", {})
        object_type = ref.get("object_type", "unknown")
        objects[(object_type, atom_object_id(atom))].append(atom)
        object_names[(object_type, atom_object_id(atom))] = display

    context_seed = computed["survey_ok_ignored_ratio"]
    family = best_group(families, family_names, "family", context_seed)
    archetype = best_group(archetypes, archetype_names, "archetype", context_seed)
    mixed_family = mixed_group(families, family_names, "family", context_seed)
    mixed_archetype = mixed_group(archetypes, archetype_names, "archetype", context_seed)

    def best_object_rollup(object_type: str, object_level: str) -> dict[str, Any]:
        matching = {
            object_id: grouped_atoms
            for (type_name, object_id), grouped_atoms in objects.items()
            if type_name == object_type
        }
        names = {
            object_id: object_names[(object_type, object_id)]
            for (type_name, object_id) in object_names
            if type_name == object_type
        }
        return best_group(matching, names, object_level, context_seed)

    artist = best_object_rollup("artist", "artist")
    album = best_object_rollup("album", "album")
    song = best_object_rollup("song_recording", "song")
    if album["positive_signal_count"] == 0 and song["positive_signal_count"] > 0:
        album = deepcopy(song)
        album.update(
            {
                "rollup_id": f"visible_rollup:album:album_sidecar_{song['target_object_id']}",
                "object_level": "album",
                "target_object_id": f"album_sidecar_{song['target_object_id']}",
                "display_name": f"{song['display_name']} Album Context",
                "coverage_gap_score": bounded(max(song["coverage_gap_score"], 0.58)),
                "depth_gap_score": bounded(max(song["depth_gap_score"], 0.62)),
                "context_variability_score": bounded(
                    max(song["context_variability_score"], context_seed + 0.18)
                ),
            }
        )

    song_cluster = combine_pair_rollup("song_cluster", song, mixed_archetype, context_seed)
    song_cluster["display_name"] = f"{song['display_name']} Context Cluster"
    return {
        "family": family,
        "archetype": archetype,
        "artist": artist,
        "album": album,
        "song": song,
        "family_pair": combine_pair_rollup("family_pair", family, mixed_family, context_seed),
        "archetype_pair": combine_pair_rollup("archetype_pair", archetype, mixed_archetype, context_seed),
        "artist_within_archetype": artist,
        "album_within_archetype": album,
        "song_cluster": song_cluster,
    }


def adjusted_rollups_for_template(
    base_rollups: dict[str, dict[str, Any]],
    template: dict[str, Any],
    computed: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    adjusted: dict[str, dict[str, Any]] = {}
    for level, rollup in base_rollups.items():
        item = deepcopy(rollup)
        item["rollup_id"] = f"{item['rollup_id']}:{template['scenario_id']}"
        item["coverage_gap_score"] = bounded(
            max(item["coverage_gap_score"] * template["coverage_factor"], (1 - computed["evidence_density"]) * template["coverage_factor"])
        )
        item["depth_gap_score"] = bounded(
            max(item["depth_gap_score"] * template["depth_factor"], (1 - computed["positive_signal_strength"]) * template["depth_factor"] * 0.85)
        )
        item["tier_coverage_score"] = bounded(max(0.1, 1 - item["coverage_gap_score"]))
        item["tier_depth_score"] = bounded(max(0.1, 1 - item["depth_gap_score"]))
        item["conflict_score"] = bounded(
            max(item["conflict_score"] * template["conflict_factor"], computed["conflict_score"] * template["conflict_factor"])
        )
        item["context_variability_score"] = bounded(
            max(
                item["context_variability_score"] * template["context_factor"],
                (computed["survey_ok_ignored_ratio"] + item["conflict_score"]) * 0.55 * template["context_factor"],
            )
        )
        item["context_skew_score"] = bounded(
            max(item["context_skew_score"] * template["context_factor"], item["context_variability_score"] * 0.72)
        )
        signal_total = max(
            1,
            item["positive_signal_count"]
            + item["negative_signal_count"]
            + item["survey_ok_ignored_count"],
        )
        positive_strength = item["positive_signal_count"] / signal_total
        item["bridge_readiness_score"] = bounded(
            max(
                item["bridge_readiness_score"],
                0.20 + positive_strength * 0.36 + item["coverage_gap_score"] * 0.30,
            )
        )
        item["gateway_to_representative_coherence_score"] = bounded(
            max(item["gateway_to_representative_coherence_score"], 0.25 + item["tier_coverage_score"] * 0.35)
        )
        item["risk_flags"] = sorted(set(item.get("risk_flags", []) + template["risk_flags"]))
        adjusted[level] = item
    return adjusted


def visible_export_summary(export: dict[str, Any]) -> dict[str, Any]:
    atoms = export["atlas_ingestable"]["evidence_atoms"]
    reaction_counts = Counter(atom_raw_reaction(atom) for atom in atoms)
    object_counts = Counter(atom.get("music_object_ref", {}).get("object_type", "unknown") for atom in atoms)
    archetype_counts: Counter[str] = Counter()
    family_counts: Counter[str] = Counter()
    positive_atoms: list[dict[str, Any]] = []
    negative_atoms: list[dict[str, Any]] = []

    for atom in atoms:
        for archetype_id in atom.get("graph_refs", {}).get("archetype_ids", []):
            archetype_counts[str(archetype_id)] += 1
        for family_number in atom.get("graph_refs", {}).get("family_numbers", []):
            family_counts[str(family_number)] += 1
        raw = atom_raw_reaction(atom)
        if raw in {"love", "like"} and len(positive_atoms) < 12:
            positive_atoms.append(atom)
        if raw in {"dont_like", "dislike"} and len(negative_atoms) < 12:
            negative_atoms.append(atom)

    total = len(atoms)
    positive_count = reaction_counts["love"] + reaction_counts["like"]
    negative_count = reaction_counts["dont_like"] + reaction_counts["dislike"]
    ok_ignored = reaction_counts["ok"]
    conflict_score = min(1.0, (min(positive_count, negative_count) * 2) / max(1, positive_count + negative_count))

    summary = {
        "profile_public_id": export["source"]["profile_public_id"],
        "survey_run_id": export["source"]["survey_run_id"],
        "page_count_config": export["source"]["page_count_config"],
        "signal_counts": {
            "survey_love": reaction_counts["love"],
            "survey_like": reaction_counts["like"],
            "survey_ok_ignored": ok_ignored,
            "survey_dislike": negative_count,
            "survey_unknown": reaction_counts["dont_know_enough"],
            "total_visible_atoms": total,
            "total_preference_signals": positive_count + negative_count,
            "total_non_failure_signals": positive_count,
        },
        "object_type_counts": dict(sorted(object_counts.items())),
        "top_visible_archetype_ids": [item[0] for item in archetype_counts.most_common(6)],
        "top_visible_family_numbers": [item[0] for item in family_counts.most_common(6)],
        "visible_positive_examples": [visible_atom_example(atom) for atom in positive_atoms],
        "visible_negative_examples": [visible_atom_example(atom) for atom in negative_atoms],
        "computed_visible_fields": {
            "evidence_density": round(
                min(1.0, (positive_count + negative_count) / max(1, total)),
                4,
            ),
            "positive_signal_strength": round(min(1.0, positive_count / max(1, total)), 4),
            "negative_signal_strength": round(min(1.0, negative_count / max(1, total)), 4),
            "weak_non_failure_strength": 0,
            "conflict_score": round(conflict_score, 4),
            "survey_ok_ignored_ratio": round(ok_ignored / max(1, total), 4),
        },
    }
    summary["target_level_rollups"] = target_level_rollups(atoms, summary["computed_visible_fields"])
    return summary


def visible_atom_example(atom: dict[str, Any]) -> dict[str, Any]:
    ref = atom.get("music_object_ref", {})
    return {
        "evidence_ref": atom.get("evidence_ref"),
        "object_type": ref.get("object_type"),
        "object_id": (
            ref.get("canonical_song_recording_id")
            or ref.get("canonical_artist_id")
            or ref.get("canonical_album_id")
            or ref.get("object_id")
        ),
        "display_name": ref.get("display_name"),
        "artist_display_name": ref.get("artist_display_name"),
        "raw_reaction": atom_raw_reaction(atom),
        "graph_refs": atom.get("graph_refs", {}),
    }


def scenario_rollups(profile_id: str, summary: dict[str, Any]) -> list[dict[str, Any]]:
    counts = summary["signal_counts"]
    computed = summary["computed_visible_fields"]
    top_family = summary["top_visible_family_numbers"][0] if summary["top_visible_family_numbers"] else "unknown_family"
    top_arch = summary["top_visible_archetype_ids"][0] if summary["top_visible_archetype_ids"] else "unknown_archetype"
    positive_example = (summary["visible_positive_examples"] or [{}])[0]
    object_id = positive_example.get("object_id") or f"synthetic_visible_object_{profile_id}"
    display_name = positive_example.get("display_name") or f"Synthetic Visible Object {profile_id}"

    rollups: list[dict[str, Any]] = []
    for template in SCENARIO_TEMPLATES:
        target_rollups = adjusted_rollups_for_template(
            summary["target_level_rollups"],
            template,
            computed,
        )
        coverage_gap = round(min(1.0, (1 - computed["evidence_density"]) * template["coverage_factor"]), 4)
        depth_gap = round(min(1.0, (1 - computed["positive_signal_strength"]) * template["depth_factor"]), 4)
        conflict = round(min(1.0, computed["conflict_score"] * template["conflict_factor"]), 4)
        context_variability = round(min(1.0, (computed["survey_ok_ignored_ratio"] + conflict) * template["context_factor"]), 4)
        context_skew = round(min(1.0, context_variability * 0.72), 4)

        rollups.append(
            {
                "scenario_id": template["scenario_id"],
                "profile_id": profile_id,
                "description": f"{profile_id}: {template['description']}",
                "expected_top_mission_types": template["expected_top_mission_types"],
                "family_id": f"family_{top_family}",
                "family_name": f"Visible Family {top_family}",
                "archetype_id": str(top_arch),
                "archetype_name": f"Visible Archetype {top_arch}",
                "artist_id": positive_example.get("artist_display_name") or f"visible_artist_{profile_id}",
                "album_id": f"visible_album_{profile_id}_{template['scenario_id']}",
                "song_id": str(object_id),
                "display_name": display_name,
                "node_tier": template["node_tier"],
                "graph_item_role": template["graph_item_role"],
                "context_overlays": template["context_overlays"],
                "risk_flags": template["risk_flags"],
                "identity_flags": [],
                "profile_visible_signal_count": counts["total_visible_atoms"],
                "signal_summary": {
                    "positive_signal_count": counts["survey_love"] + counts["survey_like"],
                    "negative_signal_count": counts["survey_dislike"],
                    "weak_non_failure_signal_count": 0,
                    "survey_ok_ignored_count": counts["survey_ok_ignored"],
                    "mission_ok_weak_count": 0,
                    "evidence_density": computed["evidence_density"],
                    "conflict_score": conflict,
                    "recency_score": 0.82,
                },
                "computed_fields": {
                    "tier_coverage_score": round(max(0.1, 1 - coverage_gap), 4),
                    "tier_depth_score": round(max(0.1, 1 - depth_gap), 4),
                    "coverage_gap_score": coverage_gap,
                    "depth_gap_score": depth_gap,
                    "context_variability_score": context_variability,
                    "context_skew_score": context_skew,
                    "bridge_readiness_score": round(max(0.2, 1 - coverage_gap * 0.8), 4),
                    "gateway_to_representative_coherence_score": round(max(0.2, 1 - depth_gap * 0.7), 4),
                },
                "target_level_rollups": target_rollups,
            }
        )
    return rollups


def hidden_song_sample(corpus: dict[str, Any], per_reaction: int = 8) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {"love": [], "like": [], "ok": [], "dont_like": []}
    for reaction in corpus["reactions"]:
        ref = reaction.get("music_object_ref", {})
        if ref.get("object_type") != "song_recording":
            continue
        raw = reaction.get("reaction")
        if raw not in grouped or len(grouped[raw]) >= per_reaction:
            continue
        grouped[raw].append(
            {
                "song_id": ref.get("canonical_song_recording_id"),
                "title": ref.get("display_name"),
                "artist_display_name": ref.get("artist_display_name"),
                "reaction": raw,
                "familiarity_band": reaction.get("familiarity_band"),
                "confidence": reaction.get("confidence"),
                "reason_tags": reaction.get("reason_tags", []),
            }
        )
    return [item for reaction in ["love", "like", "ok", "dont_like"] for item in grouped[reaction]]


def build_fixtures() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    created_at = now_iso()
    visible_profiles: list[dict[str, Any]] = []
    hidden_profiles: list[dict[str, Any]] = []

    for profile in PROFILE_IDS:
        public_id = f"public_profile_{profile}"
        visible_path = SURVEY_EXPORT_DIR / f"{public_id}_A3_Al1_S2_survey_evidence_export.json"
        hidden_truth_path = HIDDEN_TRUTH_DIR / f"hidden_truth_{public_id}_A3_Al1_S2.json"
        hidden_corpus_path = HIDDEN_CORPUS_DIR / f"hidden_corpus_{profile}.json"
        visible_export = load_json(visible_path)
        hidden_truth = load_json(hidden_truth_path)
        hidden_corpus = load_json(hidden_corpus_path)
        summary = visible_export_summary(visible_export)

        visible_profiles.append(
            {
                "profile_id": public_id,
                "selector_may_read": True,
                "hidden_oracle_included": False,
                "source_visible_evidence_ref": repo_rel(visible_path),
                "visible_evidence": {
                    "survey_signals_summary": summary["signal_counts"],
                    "object_type_counts": summary["object_type_counts"],
                    "top_visible_archetype_ids": summary["top_visible_archetype_ids"],
                    "top_visible_family_numbers": summary["top_visible_family_numbers"],
                    "visible_positive_examples": summary["visible_positive_examples"],
                    "visible_negative_examples": summary["visible_negative_examples"],
                    "computed_visible_fields": summary["computed_visible_fields"],
                    "target_level_rollups": summary["target_level_rollups"],
                },
                "synthetic_selector_scenarios": scenario_rollups(public_id, summary),
                "expected_selector_behavior": deepcopy(EXPECTED_BEHAVIOR[profile]),
            }
        )

        hidden_profiles.append(
            {
                "profile_id": public_id,
                "selector_may_read": False,
                "not_allowed_for_selector": True,
                "source_hidden_truth_packet_ref": repo_rel(hidden_truth_path),
                "source_hidden_reaction_corpus_ref": repo_rel(hidden_corpus_path),
                "hidden_oracle": {
                    "song_reactions": hidden_song_sample(hidden_corpus),
                    "affinity_pattern_reactions": {
                        "primary_archetype_affinities": hidden_truth["hidden_profile_truth"].get(
                            "primary_archetype_affinities", []
                        ),
                        "secondary_archetype_affinities": hidden_truth["hidden_profile_truth"].get(
                            "secondary_archetype_affinities", []
                        ),
                        "hidden_anti_affinities": hidden_truth["hidden_profile_truth"].get(
                            "hidden_anti_affinities", []
                        ),
                        "false_nearby_lane": hidden_truth["hidden_profile_truth"].get("false_nearby_lane"),
                        "context_lane": hidden_truth["hidden_profile_truth"].get("context_lane"),
                    },
                    "notes": "Simulator-private oracle. Not visible to selector. Use only after opportunity selection.",
                },
            }
        )

    visible = {
        "contract_version": "mission_opportunity_profile_visible_selector_inputs_v0_1",
        "fixture_status": "synthetic_contract_fixture",
        "created_at": created_at,
        "selector_may_read": True,
        "hidden_oracle_included": False,
        "runtime_listener_evidence_connected": False,
        "canonical_graph_mutation_allowed": False,
        "production_mission_generation_allowed": False,
        "profiles": visible_profiles,
    }
    hidden = {
        "contract_version": "mission_opportunity_profile_hidden_oracles_v0_1",
        "fixture_status": "synthetic_contract_fixture",
        "created_at": created_at,
        "selector_may_read": False,
        "not_allowed_for_selector": True,
        "runtime_listener_evidence_connected": False,
        "canonical_graph_mutation_allowed": False,
        "production_mission_generation_allowed": False,
        "profiles": hidden_profiles,
    }

    summary = {
        "contract_version": "mission_opportunity_profile_simulation_phase1_summary_v0_1",
        "fixture_status": "synthetic_contract_fixture",
        "created_at": created_at,
        "phase": "selector_only_visible_evidence",
        "visible_selector_input_ref": repo_rel(VISIBLE_OUTPUT),
        "hidden_oracle_ref": repo_rel(HIDDEN_OUTPUT),
        "guardrail": "Selectors may read only visible_selector_input_ref. Hidden oracle is reserved for post-selection evaluation.",
        "profiles": [
            {
                "profile_id": profile["profile_id"],
                "expected_selector_behavior": profile["expected_selector_behavior"],
            }
            for profile in visible_profiles
        ],
    }
    return visible, hidden, summary


def run_profile_selectors(visible: dict[str, Any]) -> list[dict[str, Any]]:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from prototype_mission_opportunity_selector_v0_1 import run_selector

    registry = load_json(REGISTRY_PATH)
    outputs: list[dict[str, Any]] = []
    for index, profile in enumerate(visible["profiles"]):
        profile_id = profile["profile_id"]
        scenario_fixture = {
            "contract_version": "profile_visible_selector_scenarios_v0_1",
            "fixture_status": "synthetic_contract_fixture",
            "scenario_rollups": profile["synthetic_selector_scenarios"],
        }
        selector_output = run_selector(registry, scenario_fixture, profile_id)
        selector_output["selector_run_id"] = f"profile_phase1_selector_{profile_id}_v0_1"
        selector_output["source_evidence_rollup_ref"] = (
            f"{repo_rel(VISIBLE_OUTPUT)}#/profiles/{index}/synthetic_selector_scenarios"
        )
        selector_output["selector_audit"]["audit_notes"].append(
            "Profile phase-1 run used visible selector input only; hidden oracle file was not read by selector."
        )
        output_path = PROFILE_SIM_DIR / f"{profile_id}_selector_output_v0_1.json"
        write_json(output_path, selector_output)
        outputs.append(
            {
                "profile_id": profile_id,
                "selector_output_ref": repo_rel(output_path),
                "top_5_mission_types": [
                    opportunity["mission_type"]
                    for opportunity in selector_output["ranked_opportunities"][:5]
                ],
                "top_10_mission_types": [
                    opportunity["mission_type"]
                    for opportunity in selector_output["ranked_opportunities"][:10]
                ],
                "top_10_target_objects": [
                    opportunity["target_object_ref"]["display_name"]
                    for opportunity in selector_output["ranked_opportunities"][:10]
                ],
                "final_heap_size": selector_output["selector_audit"]["final_heap_size"],
                "candidate_blobs_generated": selector_output["selector_audit"][
                    "candidate_blobs_generated"
                ],
                "candidate_blobs_scored": selector_output["selector_audit"][
                    "candidate_blobs_scored"
                ],
                "candidate_blobs_pruned": selector_output["selector_audit"][
                    "candidate_blobs_pruned"
                ],
                "non_generation_mission_types": [
                    item["mission_type"]
                    for item in selector_output["selector_audit"]["non_generation_reasons"]
                ],
                "duplicate_control_summary": selector_output["selector_audit"][
                    "duplicate_control_summary"
                ],
                "floor_failure_count": len(selector_output["selector_audit"]["floor_failure_examples"]),
            }
        )
    return outputs


def main() -> int:
    visible, hidden, summary = build_fixtures()
    write_json(VISIBLE_OUTPUT, visible)
    write_json(HIDDEN_OUTPUT, hidden)
    selector_runs = run_profile_selectors(visible)
    summary["selector_runs"] = selector_runs
    write_json(SUMMARY_OUTPUT, summary)
    for run in selector_runs:
        print(
            f"{run['profile_id']}: top_5={','.join(run['top_5_mission_types'])} "
            f"heap={run['final_heap_size']} generated={run['candidate_blobs_generated']}"
        )
    print(f"wrote {repo_rel(VISIBLE_OUTPUT)}")
    print(f"wrote {repo_rel(HIDDEN_OUTPUT)}")
    print(f"wrote {repo_rel(SUMMARY_OUTPUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
