#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from build_hidden_oracle_evaluation_design_v0_1 import (
    average_metrics,
    metric_definitions,
    metrics_for_opportunity,
    oracle_maps,
    oracle_match_summary,
)
from build_mission_opportunity_profile_simulation_v0_1 import (
    EXPECTED_BEHAVIOR,
    HIDDEN_CORPUS_DIR,
    HIDDEN_TRUTH_DIR,
    PROFILE_IDS,
    SCENARIO_TEMPLATES,
    SURVEY_EXPORT_DIR,
    adjusted_rollups_for_template,
    bounded,
    visible_atom_example,
)
from prototype_mission_opportunity_selector_v0_1 import run_selector


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DIR = REPO_ROOT / "data/product_contracts/mission_opportunity_selection_v0_1"
FIXTURE_DIR = CONTRACT_DIR / "fixtures"
PROFILE_SIM_DIR = FIXTURE_DIR / "profile_simulation"
EVAL_DIR = CONTRACT_DIR / "evaluations/phase1e_expanded_visible_evidence_scale"
SELECTOR_OUTPUT_DIR = EVAL_DIR / "selector_outputs_by_profile_scale"
NEGATIVE_DIR = EVAL_DIR / "negative"

REGISTRY_PATH = FIXTURE_DIR / "mission_type_registry_sample_v0_1.json"
HIDDEN_ORACLES = PROFILE_SIM_DIR / "hidden_profile_oracles_v0_1.json"
EXPANDED_VISIBLE_OUTPUT = EVAL_DIR / "expanded_visible_profile_inputs_v0_1.json"
RANK_OUTPUT = EVAL_DIR / "hidden_oracle_rank_usefulness_by_profile_scale_v0_1.json"
SUMMARY_JSON_OUTPUT = EVAL_DIR / "expanded_visible_evidence_scale_summary_v0_1.json"
SUMMARY_MD_OUTPUT = EVAL_DIR / "expanded_visible_evidence_scale_summary_v0_1.md"

SCALES = [72, 150, 200, 300]
SAMPLING_MODES = ["profile_weighted_balanced", "edge_heavy", "song_heavy"]
MISSION_TYPES_TO_INSPECT = [
    "boundary_test",
    "context_dependence_test",
    "bridge_test",
    "artist_depth_test",
    "archetype_depth_test",
    "album_container_test",
    "false_nearby_test",
    "song_to_archetype_test",
    "family_survey",
    "archetype_survey",
    "initial_profile_survey",
    "gateway_test",
]
SURVEY_DECAY_TYPES = {"initial_profile_survey", "family_survey", "archetype_survey"}

MODE_OBJECT_WEIGHTS = {
    "profile_weighted_balanced": {"artist": 0.28, "album": 0.24, "song_recording": 0.48},
    "edge_heavy": {"artist": 0.20, "album": 0.20, "song_recording": 0.60},
    "song_heavy": {"artist": 0.12, "album": 0.15, "song_recording": 0.73},
}
MODE_REACTION_WEIGHTS = {
    "profile_weighted_balanced": {
        "love": 0.14,
        "like": 0.28,
        "ok": 0.30,
        "dislike": 0.22,
        "unknown": 0.06,
    },
    "edge_heavy": {
        "love": 0.10,
        "like": 0.20,
        "ok": 0.28,
        "dislike": 0.35,
        "unknown": 0.07,
    },
    "song_heavy": {
        "love": 0.15,
        "like": 0.30,
        "ok": 0.25,
        "dislike": 0.25,
        "unknown": 0.05,
    },
}
MODE_MISSION_OK_SHARE = {
    "profile_weighted_balanced": 0.30,
    "edge_heavy": 0.60,
    "song_heavy": 0.42,
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


def stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def stable_hash(value: Any) -> str:
    return hashlib.sha256(stable_json(value).encode("utf-8")).hexdigest()


def object_ref_id(ref: dict[str, Any]) -> str:
    return str(
        ref.get("canonical_song_recording_id")
        or ref.get("canonical_artist_id")
        or ref.get("canonical_album_id")
        or ref.get("object_id")
        or ref.get("display_name")
        or "unknown_object"
    )


def reaction_key(value: str) -> str:
    if value in {"dont_like", "dislike"}:
        return "dislike"
    if value in {"dont_know_enough", "unknown"}:
        return "unknown"
    return value


def atom_raw_reaction(atom: dict[str, Any]) -> str:
    return atom.get("reaction", {}).get("raw_value", "unknown")


def atom_source_type(atom: dict[str, Any]) -> str:
    return str(atom.get("source_type") or atom.get("atom_type") or "survey_response")


def is_review_source(atom: dict[str, Any]) -> bool:
    return atom_source_type(atom) in {"mission_review", "song_review"}


def baseline_atoms(profile_id: str) -> list[dict[str, Any]]:
    path = SURVEY_EXPORT_DIR / f"{profile_id}_A3_Al1_S2_survey_evidence_export.json"
    atoms = deepcopy(load_json(path)["atlas_ingestable"]["evidence_atoms"])
    for atom in atoms:
        atom["source_type"] = "survey_response"
        atom.setdefault("phase1e_visible_fixture_role", "baseline_current_visible_atom")
    return atoms


def graph_ref_for_sample(
    reaction: str,
    object_type: str,
    source_tags: list[str],
    baseline_summary: dict[str, Any],
    ordinal: int,
) -> dict[str, Any]:
    visible_archetypes = baseline_summary.get("top_visible_archetype_ids", []) or ["visible_arch_unknown"]
    visible_families = baseline_summary.get("top_visible_family_numbers", []) or ["0"]
    if reaction in {"love", "like"}:
        archetype = visible_archetypes[ordinal % min(2, len(visible_archetypes))]
        family = visible_families[ordinal % min(2, len(visible_families))]
        roles = ["anchor", "gateway"]
        if object_type == "song_recording":
            roles.append("song_first")
    elif "profile_archetype:anti_or_false_nearby" in source_tags or reaction == "dislike":
        archetype = visible_archetypes[-1]
        family = visible_families[-1]
        roles = ["boundary", "false_nearby"]
    else:
        archetype = visible_archetypes[ordinal % len(visible_archetypes)]
        family = visible_families[ordinal % len(visible_families)]
        roles = ["contextual_object"]

    if "profile_archetype:tier_1" in source_tags:
        roles.append("major_representative")
    if "profile_archetype:tier_2" in source_tags:
        roles.append("bridge")
    if "apple_presence:apple_artist_context" in source_tags:
        roles.append("album_anchor")

    return {
        "archetype_ids": [str(archetype)],
        "family_numbers": [int(family) if str(family).isdigit() else family],
        "roles": sorted(set(roles)),
        "best_recognition_tier": "synthetic",
        "best_survey_tier": "expanded_visible",
    }


def reaction_payload(raw_reaction: str, review_source: bool) -> dict[str, str]:
    if raw_reaction == "love":
        return {
            "raw_value": "love",
            "normalized_operation": "positive_high",
            "atlas_signal": "strong_positive",
            "taste_polarity": "positive",
        }
    if raw_reaction == "like":
        return {
            "raw_value": "like",
            "normalized_operation": "positive",
            "atlas_signal": "positive",
            "taste_polarity": "positive",
        }
    if raw_reaction == "ok":
        return {
            "raw_value": "ok",
            "normalized_operation": "weak_non_failure" if review_source else "no_signal",
            "atlas_signal": "weak_non_failure" if review_source else "no_signal",
            "taste_polarity": "ambiguous" if review_source else "none",
        }
    if raw_reaction == "unknown":
        return {
            "raw_value": "dont_know_enough",
            "normalized_operation": "unknown",
            "atlas_signal": "no_signal",
            "taste_polarity": "unknown",
        }
    return {
        "raw_value": "dislike",
        "normalized_operation": "negative",
        "atlas_signal": "negative",
        "taste_polarity": "negative",
    }


def hidden_reaction_to_visible_atom(
    reaction: dict[str, Any],
    profile_id: str,
    mode: str,
    scale: int,
    ordinal: int,
    visible_reaction: str,
    source_type: str,
    baseline_summary: dict[str, Any],
) -> dict[str, Any]:
    ref = deepcopy(reaction["music_object_ref"])
    object_type = ref.get("object_type", "unknown")
    object_id = object_ref_id(ref)
    graph_refs = graph_ref_for_sample(
        visible_reaction,
        object_type,
        reaction.get("reason_tags", []),
        baseline_summary,
        ordinal,
    )
    review_source = source_type in {"mission_review", "song_review"}
    evidence_ref = f"phase1e:{profile_id}:{mode}:{scale}:{ordinal:04d}:{object_id}:{visible_reaction}"
    return {
        "atlas_ingestable": True,
        "atom_type": source_type,
        "source_type": source_type,
        "evidence_atom_id": f"phase1e_visible_atom:{profile_id}:{mode}:{scale}:{ordinal:04d}",
        "evidence_ref": evidence_ref,
        "music_object_ref": ref,
        "reaction": reaction_payload(visible_reaction, review_source),
        "graph_refs": graph_refs,
        "page_context": {
            "stage": object_type,
            "page_id": f"phase1e_{mode}_{scale}",
            "page_intent": "expanded_visible_evidence_scale_simulation",
        },
        "provenance": {
            "source": "phase1e_synthetic_visible_sampler",
            "sample_ordinal": ordinal,
            "sampling_mode": mode,
            "evidence_scale": scale,
        },
        "phase1e_visible_fixture_role": "expanded_visible_sampled_atom",
    }


def sample_priority(reaction: dict[str, Any], mode: str) -> tuple[int, str]:
    tags = set(reaction.get("reason_tags", []))
    ref = reaction.get("music_object_ref", {})
    object_id = object_ref_id(ref)
    if mode == "edge_heavy":
        priority = 0 if tags.intersection({"profile_archetype:anti_or_false_nearby"}) else 1
    elif mode == "song_heavy":
        priority = 0 if ref.get("object_type") == "song_recording" else 1
    else:
        priority = 0 if tags.intersection({"profile_archetype:tier_1", "profile_archetype:tier_2"}) else 1
    return (priority, object_id)


def allocate_counts(total: int, weights: dict[str, float]) -> dict[str, int]:
    raw = {key: total * weight for key, weight in weights.items()}
    counts = {key: int(value) for key, value in raw.items()}
    remainder = total - sum(counts.values())
    for key, _value in sorted(raw.items(), key=lambda item: (-(item[1] % 1), item[0])):
        if remainder <= 0:
            break
        counts[key] += 1
        remainder -= 1
    return counts


def build_hidden_pool(corpus: dict[str, Any], baseline_ids: set[str]) -> dict[tuple[str, str], list[dict[str, Any]]]:
    buckets: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for reaction in corpus["reactions"]:
        ref = reaction.get("music_object_ref", {})
        object_type = str(ref.get("object_type", "unknown"))
        object_id = object_ref_id(ref)
        if object_id in baseline_ids:
            continue
        raw = reaction_key(str(reaction.get("reaction", "unknown")))
        if raw not in {"love", "like", "ok", "dislike"}:
            continue
        buckets[(object_type, raw)].append(reaction)
    for key, values in buckets.items():
        values.sort(key=lambda item: sample_priority(item, "profile_weighted_balanced"))
    return buckets


def take_from_pool(
    pool: dict[tuple[str, str], list[dict[str, Any]]],
    object_type: str,
    reaction: str,
    count: int,
    mode: str,
    cursor: dict[tuple[str, str], int],
) -> list[dict[str, Any]]:
    keys = [(object_type, reaction)]
    if reaction == "unknown":
        keys = [(object_type, "ok")]
    keys.extend((candidate_type, reaction if reaction != "unknown" else "ok") for candidate_type in ["artist", "album", "song_recording"])
    chosen: list[dict[str, Any]] = []
    seen_keys: set[tuple[str, str]] = set()
    for key in keys:
        if key in seen_keys:
            continue
        seen_keys.add(key)
        values = sorted(pool.get(key, []), key=lambda item: sample_priority(item, mode))
        start = cursor.get((key[0], key[1], mode), 0)
        while start < len(values) and len(chosen) < count:
            chosen.append(values[start])
            start += 1
        cursor[(key[0], key[1], mode)] = start
        if len(chosen) == count:
            break
    return chosen


def build_expanded_atoms(
    profile_id: str,
    mode: str,
    scale: int,
    baseline_summary: dict[str, Any],
    hidden_corpus: dict[str, Any],
) -> list[dict[str, Any]]:
    base_atoms = baseline_atoms(profile_id)
    if scale <= len(base_atoms):
        atoms = deepcopy(base_atoms[:scale])
        for atom in atoms:
            atom["phase1e_sampling_mode"] = mode
            atom["phase1e_evidence_scale"] = scale
        return atoms

    baseline_ids = {object_ref_id(atom.get("music_object_ref", {})) for atom in base_atoms}
    pool = build_hidden_pool(hidden_corpus, baseline_ids)
    additions_needed = scale - len(base_atoms)
    object_counts = allocate_counts(additions_needed, MODE_OBJECT_WEIGHTS[mode])
    reaction_counts = allocate_counts(additions_needed, MODE_REACTION_WEIGHTS[mode])
    cursor: dict[tuple[str, str], int] = {}
    sampled_atoms: list[dict[str, Any]] = []
    ordinal = len(base_atoms)

    pairs: list[tuple[str, str, int]] = []
    for object_type, object_total in object_counts.items():
        reaction_split = allocate_counts(object_total, MODE_REACTION_WEIGHTS[mode])
        for reaction, count in reaction_split.items():
            pairs.append((object_type, reaction, count))
    # Correct rounding drift against the reaction target by allowing the fill step below to top up.
    for object_type, reaction, count in pairs:
        for item in take_from_pool(pool, object_type, reaction, count, mode, cursor):
            if len(sampled_atoms) >= additions_needed:
                break
            source_type = "survey_response"
            visible_reaction = reaction
            if reaction == "ok":
                ok_index = sum(1 for atom in sampled_atoms if atom_raw_reaction(atom) == "ok")
                if ok_index / max(1, reaction_counts["ok"]) < MODE_MISSION_OK_SHARE[mode]:
                    source_type = "song_review" if item["music_object_ref"].get("object_type") == "song_recording" else "mission_review"
            elif reaction == "unknown":
                visible_reaction = "unknown"
                source_type = "survey_response"
            atom = hidden_reaction_to_visible_atom(
                item,
                profile_id,
                mode,
                scale,
                ordinal,
                visible_reaction,
                source_type,
                baseline_summary,
            )
            sampled_atoms.append(atom)
            ordinal += 1

    fallback_reactions = ["like", "ok", "dislike", "love"]
    fallback_object_types = ["song_recording", "artist", "album"]
    while len(sampled_atoms) < additions_needed:
        reaction = fallback_reactions[len(sampled_atoms) % len(fallback_reactions)]
        object_type = fallback_object_types[len(sampled_atoms) % len(fallback_object_types)]
        chosen = take_from_pool(pool, object_type, reaction, 1, mode, cursor)
        if not chosen:
            break
        item = chosen[0]
        source_type = "mission_review" if reaction == "ok" else "survey_response"
        sampled_atoms.append(
            hidden_reaction_to_visible_atom(
                item,
                profile_id,
                mode,
                scale,
                ordinal,
                reaction,
                source_type,
                baseline_summary,
            )
        )
        ordinal += 1

    atoms = deepcopy(base_atoms) + sampled_atoms[:additions_needed]
    for atom in atoms:
        atom["phase1e_sampling_mode"] = mode
        atom["phase1e_evidence_scale"] = scale
    return atoms


def rollup_from_atoms(
    object_level: str,
    target_object_id: str,
    display_name: str,
    atoms: list[dict[str, Any]],
    context_seed: float,
    risk_flags: list[str] | None = None,
) -> dict[str, Any]:
    positive = 0
    negative = 0
    survey_ok_ignored = 0
    mission_ok_weak = 0
    unknown = 0
    for atom in atoms:
        raw = reaction_key(atom_raw_reaction(atom))
        if raw in {"love", "like"}:
            positive += 1
        elif raw == "dislike":
            negative += 1
        elif raw == "ok" and is_review_source(atom):
            mission_ok_weak += 1
        elif raw == "ok":
            survey_ok_ignored += 1
        else:
            unknown += 1
    total = max(1, len(atoms))
    preference_total = max(1, positive + negative)
    ok_ratio = (survey_ok_ignored + mission_ok_weak) / total
    evidence_density = bounded((positive + negative + mission_ok_weak * 0.35) / total)
    coverage_gap = bounded(1 - evidence_density)
    conflict = bounded((min(positive, negative) * 2) / preference_total)
    roles = {
        role
        for atom in atoms
        for role in atom.get("graph_refs", {}).get("roles", [])
    }
    gateway_role = 1.0 if roles.intersection({"gateway", "bridge", "song_first"}) else 0.0
    tier_coverage = bounded(min(1.0, len(roles) / 6) if roles else 0.30)
    tier_depth = bounded(min(1.0, (positive + negative + mission_ok_weak) / 8))
    recency = 0.78
    positive_strength = positive / max(1, total)
    context_variability = bounded(
        ok_ratio * 0.32
        + conflict * 0.38
        + mission_ok_weak / total * 0.20
        + context_seed * 0.18
    )
    context_skew = bounded(ok_ratio * 0.44 + mission_ok_weak / total * 0.28 + context_seed * 0.22)
    return {
        "rollup_id": f"visible_rollup:{object_level}:{target_object_id}",
        "object_level": object_level,
        "target_object_id": str(target_object_id),
        "display_name": display_name,
        "positive_signal_count": positive,
        "negative_signal_count": negative,
        "weak_non_failure_signal_count": mission_ok_weak,
        "survey_ok_ignored_count": survey_ok_ignored,
        "mission_ok_weak_count": mission_ok_weak,
        "unknown_signal_count": unknown,
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
        positive = sum(1 for atom in atoms if reaction_key(atom_raw_reaction(atom)) in {"love", "like"})
        negative = sum(1 for atom in atoms if reaction_key(atom_raw_reaction(atom)) == "dislike")
        weak = sum(1 for atom in atoms if reaction_key(atom_raw_reaction(atom)) == "ok" and is_review_source(atom))
        return (positive + weak, positive + negative + weak, len(atoms))

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
        positive = sum(1 for atom in atoms if reaction_key(atom_raw_reaction(atom)) in {"love", "like"})
        negative = sum(1 for atom in atoms if reaction_key(atom_raw_reaction(atom)) == "dislike")
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
    weak = int(target.get("weak_non_failure_signal_count", 0))
    ok_ignored = int(target["survey_ok_ignored_count"])
    source_strength = positive / max(
        1,
        positive + int(source["negative_signal_count"]) + int(source["survey_ok_ignored_count"]),
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
        "weak_non_failure_signal_count": weak,
        "survey_ok_ignored_count": ok_ignored,
        "mission_ok_weak_count": weak,
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
            0.22 + source_strength * 0.32 + coverage_gap * 0.28
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
        objects[(object_type, object_ref_id(ref))].append(atom)
        object_names[(object_type, object_ref_id(ref))] = display

    context_seed = computed["ok_ignored_ratio"] + computed["mission_ok_weak_ratio"]
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
                "coverage_gap_score": bounded(max(song["coverage_gap_score"], 0.48)),
                "depth_gap_score": bounded(max(song["depth_gap_score"], 0.52)),
                "context_variability_score": bounded(max(song["context_variability_score"], context_seed + 0.18)),
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


def visible_summary(
    profile_id: str,
    mode: str,
    scale: int,
    atoms: list[dict[str, Any]],
) -> dict[str, Any]:
    object_counts = Counter(atom.get("music_object_ref", {}).get("object_type", "unknown") for atom in atoms)
    archetype_counts: Counter[str] = Counter()
    family_counts: Counter[str] = Counter()
    positive_atoms: list[dict[str, Any]] = []
    negative_atoms: list[dict[str, Any]] = []
    counts = Counter(
        {
            "love": 0,
            "like": 0,
            "survey_ok_ignored": 0,
            "mission_ok_weak": 0,
            "dislike": 0,
            "unknown": 0,
        }
    )
    for atom in atoms:
        raw = reaction_key(atom_raw_reaction(atom))
        if raw in {"love", "like"}:
            counts[raw] += 1
            if len(positive_atoms) < 12:
                positive_atoms.append(atom)
        elif raw == "dislike":
            counts["dislike"] += 1
            if len(negative_atoms) < 12:
                negative_atoms.append(atom)
        elif raw == "ok" and is_review_source(atom):
            counts["mission_ok_weak"] += 1
        elif raw == "ok":
            counts["survey_ok_ignored"] += 1
        else:
            counts["unknown"] += 1
        for archetype_id in atom.get("graph_refs", {}).get("archetype_ids", []):
            archetype_counts[str(archetype_id)] += 1
        for family_number in atom.get("graph_refs", {}).get("family_numbers", []):
            family_counts[str(family_number)] += 1

    total = len(atoms)
    positive_count = counts["love"] + counts["like"]
    negative_count = counts["dislike"]
    weak = counts["mission_ok_weak"]
    preference = positive_count + negative_count
    conflict_score = min(1.0, (min(positive_count, negative_count) * 2) / max(1, preference))
    computed = {
        "evidence_density": bounded((preference + weak * 0.35) / max(1, total)),
        "positive_signal_strength": bounded(positive_count / max(1, total)),
        "negative_signal_strength": bounded(negative_count / max(1, total)),
        "weak_non_failure_strength": bounded(weak / max(1, total)),
        "conflict_score": bounded(conflict_score),
        "ok_ignored_ratio": bounded(counts["survey_ok_ignored"] / max(1, total)),
        "mission_ok_weak_ratio": bounded(weak / max(1, total)),
        "survey_ok_ignored_ratio": bounded(counts["survey_ok_ignored"] / max(1, total)),
    }
    summary = {
        "profile_id": profile_id,
        "evidence_scale": scale,
        "sampling_mode": mode,
        "signal_counts": {
            "survey_love": counts["love"],
            "survey_like": counts["like"],
            "survey_ok_ignored": counts["survey_ok_ignored"],
            "mission_ok_weak": counts["mission_ok_weak"],
            "survey_dislike": counts["dislike"],
            "survey_unknown": counts["unknown"],
            "total_visible_atoms": total,
            "total_preference_signals": preference,
            "total_non_failure_signals": positive_count + weak,
            "weak_non_failure_signals": weak,
        },
        "object_type_counts": dict(sorted(object_counts.items())),
        "top_visible_archetype_ids": [item[0] for item in archetype_counts.most_common(6)],
        "top_visible_family_numbers": [item[0] for item in family_counts.most_common(6)],
        "visible_positive_examples": [visible_atom_example(atom) for atom in positive_atoms],
        "visible_negative_examples": [visible_atom_example(atom) for atom in negative_atoms],
        "computed_visible_fields": computed,
    }
    summary["target_level_rollups"] = target_level_rollups(atoms, computed)
    return summary


def scenario_rollups(profile_id: str, run_id: str, summary: dict[str, Any]) -> list[dict[str, Any]]:
    counts = summary["signal_counts"]
    computed = summary["computed_visible_fields"]
    top_family = summary["top_visible_family_numbers"][0] if summary["top_visible_family_numbers"] else "unknown_family"
    top_arch = summary["top_visible_archetype_ids"][0] if summary["top_visible_archetype_ids"] else "unknown_archetype"
    positive_example = (summary["visible_positive_examples"] or [{}])[0]
    object_id = positive_example.get("object_id") or f"synthetic_visible_object_{run_id}"
    display_name = positive_example.get("display_name") or f"Synthetic Visible Object {run_id}"
    rollups: list[dict[str, Any]] = []
    for template in SCENARIO_TEMPLATES:
        target_rollups = adjusted_rollups_for_template(
            summary["target_level_rollups"],
            template,
            {
                "evidence_density": computed["evidence_density"],
                "positive_signal_strength": computed["positive_signal_strength"],
                "conflict_score": computed["conflict_score"],
                "survey_ok_ignored_ratio": computed["ok_ignored_ratio"] + computed["mission_ok_weak_ratio"],
            },
        )
        coverage_gap = bounded((1 - computed["evidence_density"]) * template["coverage_factor"])
        depth_gap = bounded((1 - computed["positive_signal_strength"]) * template["depth_factor"])
        conflict = bounded(computed["conflict_score"] * template["conflict_factor"])
        context_variability = bounded(
            (
                computed["ok_ignored_ratio"]
                + computed["mission_ok_weak_ratio"] * 1.5
                + conflict
            )
            * template["context_factor"]
        )
        context_skew = bounded(context_variability * 0.72)
        rollups.append(
            {
                "scenario_id": template["scenario_id"],
                "profile_id": run_id,
                "description": f"{run_id}: {template['description']}",
                "expected_top_mission_types": template["expected_top_mission_types"],
                "family_id": f"family_{top_family}",
                "family_name": f"Visible Family {top_family}",
                "archetype_id": str(top_arch),
                "archetype_name": f"Visible Archetype {top_arch}",
                "artist_id": positive_example.get("artist_display_name") or f"visible_artist_{profile_id}",
                "album_id": f"visible_album_{run_id}_{template['scenario_id']}",
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
                    "weak_non_failure_signal_count": counts["mission_ok_weak"],
                    "survey_ok_ignored_count": counts["survey_ok_ignored"],
                    "mission_ok_weak_count": counts["mission_ok_weak"],
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


def compact_visible_atoms(atoms: list[dict[str, Any]]) -> list[dict[str, Any]]:
    compact: list[dict[str, Any]] = []
    for atom in atoms:
        ref = atom.get("music_object_ref", {})
        compact.append(
            {
                "evidence_ref": atom.get("evidence_ref"),
                "source_type": atom_source_type(atom),
                "object_type": ref.get("object_type"),
                "object_id": object_ref_id(ref),
                "display_name": ref.get("display_name"),
                "artist_display_name": ref.get("artist_display_name"),
                "raw_reaction": atom_raw_reaction(atom),
                "graph_refs": atom.get("graph_refs", {}),
            }
        )
    return compact


def selector_output_path(profile_id: str, mode: str, scale: int) -> Path:
    return (
        SELECTOR_OUTPUT_DIR
        / profile_id
        / mode
        / f"selector_output_{profile_id}_{mode}_{scale}_v0_1.json"
    )


def normalized_selector_signature(selector_output: dict[str, Any]) -> list[tuple[Any, ...]]:
    return [
        (
            opportunity["opportunity_id"],
            opportunity["mission_type"],
            tuple(opportunity["target_object_ids"]),
            opportunity["score_components"]["final_opportunity_score"],
        )
        for opportunity in selector_output["ranked_opportunities"]
    ]


def run_selector_for_profile(
    registry: dict[str, Any],
    profile_run: dict[str, Any],
    profile_index: int,
) -> tuple[dict[str, Any], bool]:
    profile_id = profile_run["profile_id"]
    mode = profile_run["sampling_mode"]
    scale = profile_run["evidence_atom_count"]
    run_id = profile_run["run_id"]
    scenario_fixture = {
        "contract_version": "phase1e_expanded_visible_selector_scenarios_v0_1",
        "fixture_status": "synthetic_contract_fixture",
        "scenario_rollups": profile_run["synthetic_selector_scenarios"],
    }
    selector_output = run_selector(registry, scenario_fixture, run_id)
    selector_output["selector_run_id"] = f"phase1e_selector_{run_id}_v0_1"
    selector_output["source_evidence_rollup_ref"] = (
        f"{repo_rel(EXPANDED_VISIBLE_OUTPUT)}#/profiles/{profile_index}/synthetic_selector_scenarios"
    )
    selector_output["selector_audit"]["audit_notes"].append(
        "Phase 1E selector run used expanded selector-visible fixture only; no oracle metrics were read."
    )

    rerun_output = run_selector(registry, scenario_fixture, run_id)
    rerun_output["selector_run_id"] = selector_output["selector_run_id"]
    rerun_output["source_evidence_rollup_ref"] = selector_output["source_evidence_rollup_ref"]
    deterministic = normalized_selector_signature(selector_output) == normalized_selector_signature(rerun_output)
    write_json(selector_output_path(profile_id, mode, scale), selector_output)
    return selector_output, deterministic


def selector_metrics(selector_output: dict[str, Any]) -> dict[str, Any]:
    audit = selector_output["selector_audit"]
    top10 = selector_output["ranked_opportunities"][:10]
    return {
        "candidate_blobs_generated": audit["candidate_blobs_generated"],
        "candidate_blobs_floor_passed": audit["candidate_blobs_floor_passed"],
        "candidate_blobs_scored": audit["candidate_blobs_scored"],
        "candidate_blobs_pruned": audit["candidate_blobs_pruned"],
        "final_heap_size": audit["final_heap_size"],
        "early_stop_applied": audit["early_stop_applied"],
        "cutoff_score": audit["cutoff_score"],
        "top_10_mission_types": [item["mission_type"] for item in top10],
        "top_10_target_objects": [item["target_object_ref"]["display_name"] for item in top10],
        "mission_type_concentration": audit["duplicate_control_summary"]["mission_type_concentration"],
        "duplicate_target_object_count": audit["duplicate_control_summary"]["duplicate_target_object_count"],
        "suppressed_exact_duplicate_count": audit["duplicate_control_summary"]["suppressed_exact_duplicate_count"],
    }


def build_oracle_evaluations_for_run(
    selector_output: dict[str, Any],
    hidden_profile: dict[str, Any],
    visible_expected: set[str],
) -> list[dict[str, Any]]:
    maps = oracle_maps(hidden_profile)
    top10 = selector_output["ranked_opportunities"][:10]
    top10_types = {opportunity["mission_type"] for opportunity in top10}
    survey_decay_score = 1.0 if "initial_profile_survey" not in top10_types else 0.25
    evaluations: list[dict[str, Any]] = []
    for rank, opportunity in enumerate(top10, start=1):
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
                "notes": ["Phase 1E post-selection evaluator only."],
            }
        )
    return evaluations


def usefulness_ranks(evaluations: list[dict[str, Any]]) -> dict[str, int]:
    sorted_by_usefulness = sorted(
        evaluations,
        key=lambda item: (
            -item["expected_metrics"]["learning_usefulness_score"],
            item["selected_opportunity_ref"]["rank"],
        ),
    )
    return {
        item["selected_opportunity_ref"]["opportunity_id"]: index + 1
        for index, item in enumerate(sorted_by_usefulness)
    }


def spearman_rank_correlation(evaluations: list[dict[str, Any]], usefulness_by_id: dict[str, int]) -> float:
    n = len(evaluations)
    if n < 2:
        return 1.0
    delta_sum = 0.0
    for item in evaluations:
        selected = item["selected_opportunity_ref"]
        delta_sum += (selected["rank"] - usefulness_by_id[selected["opportunity_id"]]) ** 2
    return round(max(-1.0, min(1.0, 1 - (6 * delta_sum) / (n * ((n * n) - 1)))), 4)


def ndcg_at(evaluations: list[dict[str, Any]], k: int) -> float:
    relevances = [float(item["expected_metrics"]["learning_usefulness_score"]) for item in evaluations]
    selected = relevances[:k]
    ideal = sorted(relevances, reverse=True)[:k]

    def dcg(values: list[float]) -> float:
        return sum(value / math.log2(index + 2) for index, value in enumerate(values))

    ideal_dcg = dcg(ideal)
    return bounded(dcg(selected) / ideal_dcg) if ideal_dcg else 0.0


def rank_analysis_for_run(
    run_id: str,
    profile_id: str,
    mode: str,
    scale: int,
    selector_output_ref: str,
    evaluations: list[dict[str, Any]],
) -> dict[str, Any]:
    usefulness_by_id = usefulness_ranks(evaluations)
    top1 = evaluations[0]
    best = max(
        evaluations,
        key=lambda item: (
            item["expected_metrics"]["learning_usefulness_score"],
            -item["selected_opportunity_ref"]["rank"],
        ),
    )
    top1_score = top1["expected_metrics"]["learning_usefulness_score"]
    best_score = best["expected_metrics"]["learning_usefulness_score"]
    best_rank = best["selected_opportunity_ref"]["rank"]

    rank_rows = []
    for item in evaluations:
        selected = item["selected_opportunity_ref"]
        learning = item["expected_metrics"]["learning_usefulness_score"]
        rank_rows.append(
            {
                "rank": selected["rank"],
                "opportunity_id": selected["opportunity_id"],
                "mission_type": selected["mission_type"],
                "target_display_name": selected["target_display_name"],
                "selector_score": selected["final_opportunity_score"],
                "learning_usefulness_score": learning,
                "usefulness_rank": usefulness_by_id[selected["opportunity_id"]],
                "usefulness_delta_from_top1": round(learning - top1_score, 4),
            }
        )

    return {
        "run_id": run_id,
        "profile_id": profile_id,
        "sampling_mode": mode,
        "evidence_atom_count": scale,
        "selector_output_ref": selector_output_ref,
        "rank_window": len(evaluations),
        "top1_learning_usefulness_score": bounded(top1_score),
        "best_learning_usefulness_score": bounded(best_score),
        "rank_regret": bounded(best_score - top1_score),
        "best_usefulness_rank": best_rank,
        "top1_is_best": best_rank == 1,
        "best_in_top3": best_rank <= 3,
        "best_in_top5": best_rank <= 5,
        "spearman_rank_correlation": spearman_rank_correlation(evaluations, usefulness_by_id),
        "ndcg_at_3": ndcg_at(evaluations, 3),
        "ndcg_at_5": ndcg_at(evaluations, 5),
        "ndcg_at_10": ndcg_at(evaluations, 10),
        "rank_rows": rank_rows,
        "aggregate_expected_metrics": average_metrics(
            [evaluation["expected_metrics"] for evaluation in evaluations]
        ),
    }


def per_run_metric(
    profile_run: dict[str, Any],
    selector_output: dict[str, Any],
    rank_analysis: dict[str, Any],
    deterministic: bool,
) -> dict[str, Any]:
    counts = profile_run["visible_evidence"]["survey_signals_summary"]
    object_counts = profile_run["visible_evidence"]["object_type_counts"]
    return {
        "run_id": profile_run["run_id"],
        "profile_id": profile_run["profile_id"],
        "selector_output_ref": rank_analysis["selector_output_ref"],
        "evidence_atom_count": profile_run["evidence_atom_count"],
        "sampling_mode": profile_run["sampling_mode"],
        "artist_atom_count": object_counts.get("artist", 0),
        "album_atom_count": object_counts.get("album", 0),
        "song_atom_count": object_counts.get("song_recording", 0),
        "love_count": counts["survey_love"],
        "like_count": counts["survey_like"],
        "ok_ignored_count": counts["survey_ok_ignored"],
        "mission_ok_weak_count": counts["mission_ok_weak"],
        "dislike_count": counts["survey_dislike"],
        "unknown_count": counts["survey_unknown"],
        "usable_preference_signal_count": counts["total_preference_signals"],
        "weak_non_failure_signal_count": counts["weak_non_failure_signals"],
        **selector_metrics(selector_output),
        "top1_learning_usefulness_score": rank_analysis["top1_learning_usefulness_score"],
        "best_learning_usefulness_score": rank_analysis["best_learning_usefulness_score"],
        "rank_regret": rank_analysis["rank_regret"],
        "best_usefulness_rank": rank_analysis["best_usefulness_rank"],
        "top1_is_best": rank_analysis["top1_is_best"],
        "best_in_top3": rank_analysis["best_in_top3"],
        "best_in_top5": rank_analysis["best_in_top5"],
        "spearman_rank_correlation": rank_analysis["spearman_rank_correlation"],
        "ndcg_at_3": rank_analysis["ndcg_at_3"],
        "ndcg_at_5": rank_analysis["ndcg_at_5"],
        "ndcg_at_10": rank_analysis["ndcg_at_10"],
        "deterministic_rerun_matched": deterministic,
    }


def jaccard(before: list[str], after: list[str]) -> float:
    before_set = set(before)
    after_set = set(after)
    if not before_set and not after_set:
        return 1.0
    return bounded(len(before_set.intersection(after_set)) / len(before_set.union(after_set)))


def rank_of(mission_types: list[str], mission_type: str) -> int | None:
    try:
        return mission_types.index(mission_type) + 1
    except ValueError:
        return None


def rank_change(before: list[str], after: list[str], mission_type: str) -> int | None:
    before_rank = rank_of(before, mission_type)
    after_rank = rank_of(after, mission_type)
    if before_rank is None or after_rank is None:
        return None
    return after_rank - before_rank


def cross_scale_analysis(per_run: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key: dict[tuple[str, str], dict[int, dict[str, Any]]] = defaultdict(dict)
    for item in per_run:
        by_key[(item["profile_id"], item["sampling_mode"])][item["evidence_atom_count"]] = item

    comparisons: list[dict[str, Any]] = []
    for (profile_id, mode), by_scale in sorted(by_key.items()):
        for before_scale, after_scale in [(72, 150), (150, 200), (200, 300), (72, 300)]:
            if before_scale not in by_scale or after_scale not in by_scale:
                continue
            before = by_scale[before_scale]
            after = by_scale[after_scale]
            before_counter = Counter(before["top_10_mission_types"])
            after_counter = Counter(after["top_10_mission_types"])
            deltas = {
                mission_type: after_counter.get(mission_type, 0) - before_counter.get(mission_type, 0)
                for mission_type in sorted(set(before_counter) | set(after_counter))
            }
            before_top5 = before["top_10_mission_types"][:5]
            after_top5 = after["top_10_mission_types"][:5]
            newly_eligible = sorted(set(after["top_10_mission_types"]) - set(before["top_10_mission_types"]))
            newly_suppressed = sorted(set(before["top_10_mission_types"]) - set(after["top_10_mission_types"]))
            survey_before = sum(before_counter.get(item, 0) for item in SURVEY_DECAY_TYPES)
            survey_after = sum(after_counter.get(item, 0) for item in SURVEY_DECAY_TYPES)
            interpretation = (
                f"{profile_id} / {mode}: {before_scale}->{after_scale} keeps top-5 stability "
                f"{jaccard(before_top5, after_top5):.2f}; rank regret changes "
                f"{round(after['rank_regret'] - before['rank_regret'], 4):+.4f}; "
                f"survey mission count changes {survey_before}->{survey_after}."
            )
            comparisons.append(
                {
                    "profile_id": profile_id,
                    "sampling_mode": mode,
                    "from_scale": before_scale,
                    "to_scale": after_scale,
                    "mission_type_distribution_change": deltas,
                    "top_5_stability": jaccard(before_top5, after_top5),
                    "top_10_stability": jaccard(before["top_10_mission_types"], after["top_10_mission_types"]),
                    "newly_eligible_mission_types": newly_eligible,
                    "newly_suppressed_mission_types": newly_suppressed,
                    "survey_decay_behavior": {
                        "survey_type_count_before": survey_before,
                        "survey_type_count_after": survey_after,
                        "decayed": survey_after <= survey_before,
                    },
                    "rank_regret_change": round(after["rank_regret"] - before["rank_regret"], 4),
                    "ndcg_change": round(after["ndcg_at_10"] - before["ndcg_at_10"], 4),
                    "best_usefulness_rank_change": after["best_usefulness_rank"] - before["best_usefulness_rank"],
                    "context_dependence_rank_change": rank_change(before["top_10_mission_types"], after["top_10_mission_types"], "context_dependence_test"),
                    "boundary_test_rank_change": rank_change(before["top_10_mission_types"], after["top_10_mission_types"], "boundary_test"),
                    "bridge_test_rank_change": rank_change(before["top_10_mission_types"], after["top_10_mission_types"], "bridge_test"),
                    "artist_depth_rank_change": rank_change(before["top_10_mission_types"], after["top_10_mission_types"], "artist_depth_test"),
                    "album_container_rank_change": rank_change(before["top_10_mission_types"], after["top_10_mission_types"], "album_container_test"),
                    "interpretation": interpretation,
                }
            )
    return comparisons


def mission_type_performance(rank_analyses: list[dict[str, Any]], per_run: list[dict[str, Any]]) -> list[dict[str, Any]]:
    run_by_id = {item["run_id"]: item for item in per_run}
    aggregate_learning = []
    for analysis in rank_analyses:
        aggregate_learning.extend(row["learning_usefulness_score"] for row in analysis["rank_rows"])
    global_mean_learning = sum(aggregate_learning) / max(1, len(aggregate_learning))
    results: list[dict[str, Any]] = []
    for mission_type in MISSION_TYPES_TO_INSPECT:
        count_by_scale: dict[str, int] = {}
        rank_by_scale: dict[str, float | None] = {}
        selector_by_scale: dict[str, float | None] = {}
        learning_by_scale: dict[str, float | None] = {}
        regret_by_scale: dict[str, float | None] = {}
        ndcg_by_scale: dict[str, float | None] = {}
        all_ranks: list[int] = []
        all_learning: list[float] = []
        for scale in SCALES:
            rows = []
            containing_runs = []
            for analysis in rank_analyses:
                if analysis["evidence_atom_count"] != scale:
                    continue
                matching = [row for row in analysis["rank_rows"] if row["mission_type"] == mission_type]
                rows.extend(matching)
                if matching:
                    containing_runs.append(analysis)
            count_by_scale[str(scale)] = len(rows)
            rank_by_scale[str(scale)] = round(sum(row["rank"] for row in rows) / len(rows), 4) if rows else None
            selector_by_scale[str(scale)] = bounded(sum(row["selector_score"] for row in rows) / len(rows)) if rows else None
            learning_by_scale[str(scale)] = bounded(sum(row["learning_usefulness_score"] for row in rows) / len(rows)) if rows else None
            regret_by_scale[str(scale)] = bounded(
                sum(max(0, run_by_id[analysis["run_id"]]["best_learning_usefulness_score"] - row["learning_usefulness_score"]) for analysis in containing_runs for row in analysis["rank_rows"] if row["mission_type"] == mission_type)
                / len(rows)
            ) if rows else None
            ndcg_by_scale[str(scale)] = bounded(sum(analysis["ndcg_at_10"] for analysis in containing_runs) / len(containing_runs)) if containing_runs else None
            all_ranks.extend(row["rank"] for row in rows)
            all_learning.extend(row["learning_usefulness_score"] for row in rows)
        avg_rank = sum(all_ranks) / len(all_ranks) if all_ranks else 99
        avg_learning = sum(all_learning) / len(all_learning) if all_learning else 0
        results.append(
            {
                "mission_type": mission_type,
                "count_in_top_10_by_scale": count_by_scale,
                "average_selector_rank_by_scale": rank_by_scale,
                "average_selector_score_by_scale": selector_by_scale,
                "average_learning_usefulness_by_scale": learning_by_scale,
                "average_rank_regret_contribution": regret_by_scale,
                "average_ndcg_contribution": ndcg_by_scale,
                "over_ranked_flag": bool(all_ranks and avg_rank <= 3.5 and avg_learning < global_mean_learning - 0.04),
                "under_ranked_flag": bool(all_ranks and avg_rank >= 5.5 and avg_learning > global_mean_learning + 0.04),
                "needs_candidate_construction_flag": mission_type in {"boundary_test", "context_dependence_test", "album_container_test", "false_nearby_test"} and bool(all_learning and max(all_learning) >= 0.66),
            }
        )
    return results


def hypothesis_results(per_run: list[dict[str, Any]], cross_scale: list[dict[str, Any]], mt_perf: list[dict[str, Any]]) -> list[dict[str, Any]]:
    total_runs = len(per_run)
    best_top5 = sum(1 for item in per_run if item["best_in_top5"])
    best_top3 = sum(1 for item in per_run if item["best_in_top3"])
    avg_regret_72 = sum(item["rank_regret"] for item in per_run if item["evidence_atom_count"] == 72) / max(1, sum(1 for item in per_run if item["evidence_atom_count"] == 72))
    avg_regret_200 = sum(item["rank_regret"] for item in per_run if item["evidence_atom_count"] == 200) / max(1, sum(1 for item in per_run if item["evidence_atom_count"] == 200))
    avg_regret_300 = sum(item["rank_regret"] for item in per_run if item["evidence_atom_count"] == 300) / max(1, sum(1 for item in per_run if item["evidence_atom_count"] == 300))
    survey_72 = sum(sum(1 for mission_type in item["top_10_mission_types"] if mission_type in SURVEY_DECAY_TYPES) for item in per_run if item["evidence_atom_count"] == 72)
    survey_300 = sum(sum(1 for mission_type in item["top_10_mission_types"] if mission_type in SURVEY_DECAY_TYPES) for item in per_run if item["evidence_atom_count"] == 300)
    context_edge = [
        item
        for item in per_run
        if item["sampling_mode"] == "edge_heavy"
        and ("context_dependence_test" in item["top_10_mission_types"] or "album_container_test" in item["top_10_mission_types"])
    ]
    artist_top3_low = [
        item for item in per_run
        if "artist_depth_test" in item["top_10_mission_types"][:3]
        and item["top1_learning_usefulness_score"] < 0.62
    ]
    p06_bridge_rank1 = [
        item for item in per_run
        if item["profile_id"] == "public_profile_06"
        and item["top_10_mission_types"][0] == "bridge_test"
    ]
    boundary_perf = next(item for item in mt_perf if item["mission_type"] == "boundary_test")
    boundary_counts = sum(boundary_perf["count_in_top_10_by_scale"].values())
    boundary_learning_values = [
        value for value in boundary_perf["average_learning_usefulness_by_scale"].values() if value is not None
    ]
    improvement_72_200 = avg_regret_72 - avg_regret_200
    improvement_200_300 = avg_regret_200 - avg_regret_300
    return [
        {
            "hypothesis": "H1_top_window_preservation",
            "passed": best_top5 / max(1, total_runs) >= 0.80,
            "result": f"Oracle-best opportunity is in top 5 for {best_top5}/{total_runs} runs and top 3 for {best_top3}/{total_runs}.",
        },
        {
            "hypothesis": "H2_survey_decay",
            "passed": survey_300 <= survey_72,
            "result": f"Broad survey mission appearances in top 10 changed from {survey_72} at 72 atoms to {survey_300} at 300 atoms.",
        },
        {
            "hypothesis": "H3_context_promotion",
            "passed": len(context_edge) >= max(1, total_runs // 4),
            "result": f"Context or album-container opportunities appear in edge-heavy top 10 for {len(context_edge)} runs.",
        },
        {
            "hypothesis": "H4_artist_depth_over_ranking",
            "passed": len(artist_top3_low) <= total_runs * 0.25,
            "result": f"artist_depth_test is top-3 with low top1 usefulness in {len(artist_top3_low)} runs.",
        },
        {
            "hypothesis": "H5_bridge_over_ranking_profile_06",
            "passed": len(p06_bridge_rank1) <= 4,
            "result": f"public_profile_06 has bridge_test at rank 1 in {len(p06_bridge_rank1)} of {len([item for item in per_run if item['profile_id'] == 'public_profile_06'])} runs.",
        },
        {
            "hypothesis": "H6_boundary_robustness",
            "passed": boundary_counts > 0 and max(boundary_learning_values or [0]) >= 0.68,
            "result": f"boundary_test appears {boundary_counts} times in top 10 with max average scale usefulness {max(boundary_learning_values or [0]):.4f}.",
        },
        {
            "hypothesis": "H7_diminishing_returns",
            "passed": improvement_200_300 <= max(0.02, improvement_72_200 * 0.5),
            "result": f"Mean rank-regret improvement 72->200 is {improvement_72_200:.4f}; 200->300 is {improvement_200_300:.4f}.",
        },
    ]


def build_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Mission Opportunity Selection v0.1 Phase 1E Expanded Visible Evidence Scale",
        "",
        "Offline-only scale simulation over synthetic selector-visible evidence. No runtime wiring, no mission construction, no candidate-song selection.",
        "",
        "## Run Matrix",
        "",
        f"- Completed runs: {summary['run_matrix']['completed_run_count']}",
        f"- Profiles: {', '.join(summary['run_matrix']['profiles'])}",
        f"- Scales: {', '.join(str(item) for item in summary['run_matrix']['scales'])}",
        f"- Sampling modes: {', '.join(summary['run_matrix']['sampling_modes'])}",
        "",
        "## Aggregate Rank-Usefulness",
        "",
        f"- Best in top 5: {summary['aggregate_rank_usefulness']['best_in_top5_count']}/{summary['run_matrix']['completed_run_count']}",
        f"- Best in top 3: {summary['aggregate_rank_usefulness']['best_in_top3_count']}/{summary['run_matrix']['completed_run_count']}",
        f"- Mean rank regret: {summary['aggregate_rank_usefulness']['mean_rank_regret']}",
        f"- Mean nDCG@10: {summary['aggregate_rank_usefulness']['mean_ndcg_at_10']}",
        "",
        "## Per-Run Summary",
        "",
        "| profile | mode | atoms | top 3 mission types | regret | best rank | nDCG@10 |",
        "| --- | --- | ---: | --- | ---: | ---: | ---: |",
    ]
    for item in summary["per_run_metrics"]:
        lines.append(
            f"| {item['profile_id']} | {item['sampling_mode']} | {item['evidence_atom_count']} | "
            f"{', '.join(item['top_10_mission_types'][:3])} | {item['rank_regret']} | "
            f"{item['best_usefulness_rank']} | {item['ndcg_at_10']} |"
        )
    lines.extend(["", "## Hypotheses", "", "| hypothesis | passed | result |", "| --- | --- | --- |"])
    for item in summary["hypothesis_results"]:
        lines.append(f"| {item['hypothesis']} | {item['passed']} | {item['result']} |")
    lines.extend(["", "## Recommendations", ""])
    for item in summary["recommendations"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Guardrails", ""])
    for item in summary["guardrail_confirmations"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def write_negative_fixtures(expanded_visible: dict[str, Any], rank_output: dict[str, Any], per_run: list[dict[str, Any]]) -> None:
    leak = deepcopy(expanded_visible)
    leak["profiles"][0]["visible_evidence"]["hidden_oracle_lane_metadata"] = {
        "lane_id": "forbidden_hidden_lane"
    }
    write_json(NEGATIVE_DIR / "expanded_visible_hidden_lane_leak_v0_1.json", leak)

    selector_path = REPO_ROOT / per_run[0]["selector_output_ref"]
    selector = load_json(selector_path)
    selector["ranked_opportunities"][0]["oracle_usefulness_score"] = 0.99
    write_json(NEGATIVE_DIR / "selector_output_contains_oracle_usefulness_score_v0_1.json", selector)

    candidate_list = deepcopy(rank_output)
    candidate_list["runs"][0]["rank_rows"][0]["candidate_song_ids"] = ["forbidden_song_candidate"]
    write_json(NEGATIVE_DIR / "rank_usefulness_contains_candidate_song_list_v0_1.json", candidate_list)

    runtime_true = deepcopy(rank_output)
    runtime_true["runtime_allowed"] = True
    write_json(NEGATIVE_DIR / "phase1e_runtime_flag_true_v0_1.json", runtime_true)

    nondeterministic = {
        "contract_version": "phase1e_determinism_negative_v0_1",
        "fixture_status": "synthetic_contract_fixture",
        "run_id": per_run[0]["run_id"],
        "deterministic_rerun_matched": False,
        "reason": "Negative fixture proving deterministic rerun mismatch is rejected.",
    }
    write_json(NEGATIVE_DIR / "phase1e_determinism_mismatch_v0_1.json", nondeterministic)


def build_phase1e() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    created_at = now_iso()
    registry = load_json(REGISTRY_PATH)
    hidden_oracles = load_json(HIDDEN_ORACLES)
    hidden_by_profile = {profile["profile_id"]: profile for profile in hidden_oracles["profiles"]}
    visible_profiles: list[dict[str, Any]] = []
    per_run: list[dict[str, Any]] = []
    rank_runs: list[dict[str, Any]] = []

    for profile in PROFILE_IDS:
        profile_id = f"public_profile_{profile}"
        base_export_path = SURVEY_EXPORT_DIR / f"{profile_id}_A3_Al1_S2_survey_evidence_export.json"
        baseline_summary = visible_summary(
            profile_id,
            "baseline_reference",
            72,
            baseline_atoms(profile_id),
        )
        hidden_corpus = load_json(HIDDEN_CORPUS_DIR / f"hidden_corpus_{profile}.json")

        for mode in SAMPLING_MODES:
            for scale in SCALES:
                atoms = build_expanded_atoms(
                    profile_id,
                    mode,
                    scale,
                    baseline_summary,
                    hidden_corpus,
                )
                summary = visible_summary(profile_id, mode, scale, atoms)
                run_id = f"{profile_id}_{mode}_{scale}"
                profile_run = {
                    "run_id": run_id,
                    "profile_id": profile_id,
                    "selector_may_read": True,
                    "hidden_oracle_included": False,
                    "source_visible_evidence_ref": repo_rel(base_export_path),
                    "evidence_atom_count": len(atoms),
                    "sampling_mode": mode,
                    "deterministic_seed": f"phase1e:{profile_id}:{mode}:{scale}",
                    "visible_evidence": {
                        "survey_signals_summary": summary["signal_counts"],
                        "object_type_counts": summary["object_type_counts"],
                        "top_visible_archetype_ids": summary["top_visible_archetype_ids"],
                        "top_visible_family_numbers": summary["top_visible_family_numbers"],
                        "visible_positive_examples": summary["visible_positive_examples"],
                        "visible_negative_examples": summary["visible_negative_examples"],
                        "computed_visible_fields": summary["computed_visible_fields"],
                        "target_level_rollups": summary["target_level_rollups"],
                        "sampled_visible_evidence_atoms": compact_visible_atoms(atoms),
                    },
                    "synthetic_selector_scenarios": scenario_rollups(profile_id, run_id, summary),
                    "expected_selector_behavior": deepcopy(EXPECTED_BEHAVIOR[profile]),
                }
                profile_index = len(visible_profiles)
                selector_output, deterministic = run_selector_for_profile(
                    registry,
                    profile_run,
                    profile_index,
                )
                selector_ref = repo_rel(selector_output_path(profile_id, mode, scale))
                visible_expected = set(profile_run["expected_selector_behavior"]["likely_top_mission_types"])
                evaluations = build_oracle_evaluations_for_run(
                    selector_output,
                    hidden_by_profile[profile_id],
                    visible_expected,
                )
                rank_analysis = rank_analysis_for_run(
                    run_id,
                    profile_id,
                    mode,
                    scale,
                    selector_ref,
                    evaluations,
                )
                visible_profiles.append(profile_run)
                rank_runs.append(rank_analysis)
                per_run.append(per_run_metric(profile_run, selector_output, rank_analysis, deterministic))

    expanded_visible = {
        "contract_version": "phase1e_expanded_visible_profile_inputs_v0_1",
        "fixture_status": "synthetic_contract_fixture",
        "created_at": created_at,
        "phase": "expanded_visible_evidence_scale_simulation",
        "selector_may_read": True,
        "hidden_oracle_included": False,
        "runtime_listener_evidence_connected": False,
        "runtime_allowed": False,
        "canonical_graph_mutation_allowed": False,
        "production_mission_generation_allowed": False,
        "candidate_song_selection_status": "not_in_scope",
        "final_mission_construction_status": "not_in_scope",
        "fixture_construction_policy": {
            "fixture_builder_may_sample_heldout_corpus": True,
            "selector_may_read_sampled_visible_atoms_only": True,
            "evaluation_metrics_written_to_selector_input": False,
            "heldout_lane_metadata_included": False,
        },
        "profiles": visible_profiles,
    }

    rank_output = {
        "contract_version": "phase1e_hidden_oracle_rank_usefulness_by_profile_scale_v0_1",
        "fixture_status": "synthetic_contract_fixture",
        "created_at": created_at,
        "phase": "expanded_visible_evidence_scale_rank_usefulness",
        "runtime_allowed": False,
        "runtime_listener_evidence_connected": False,
        "production_mission_generation_allowed": False,
        "canonical_graph_mutation_allowed": False,
        "listener_preference_inference_from_affinity_allowed": False,
        "opportunity_only": True,
        "selector_may_read_hidden_oracle": False,
        "evaluator_may_read_hidden_oracle_after_selection": True,
        "candidate_song_selection_status": "not_in_scope",
        "final_mission_construction_status": "not_in_scope",
        "source_expanded_visible_profile_inputs_ref": repo_rel(EXPANDED_VISIBLE_OUTPUT),
        "source_hidden_oracle_ref": repo_rel(HIDDEN_ORACLES),
        "metric_definitions": metric_definitions(),
        "runs": rank_runs,
    }
    aggregate = {
        "best_in_top5_count": sum(1 for item in per_run if item["best_in_top5"]),
        "best_in_top3_count": sum(1 for item in per_run if item["best_in_top3"]),
        "top1_is_best_count": sum(1 for item in per_run if item["top1_is_best"]),
        "mean_rank_regret": bounded(sum(item["rank_regret"] for item in per_run) / len(per_run)),
        "mean_ndcg_at_10": bounded(sum(item["ndcg_at_10"] for item in per_run) / len(per_run)),
        "mean_spearman_rank_correlation": round(
            sum(item["spearman_rank_correlation"] for item in per_run) / len(per_run),
            4,
        ),
    }
    cross_scale = cross_scale_analysis(per_run)
    mt_perf = mission_type_performance(rank_runs, per_run)
    hypotheses = hypothesis_results(per_run, cross_scale, mt_perf)
    deterministic_count = sum(1 for item in per_run if item["deterministic_rerun_matched"])
    summary = {
        "contract_version": "phase1e_expanded_visible_evidence_scale_summary_v0_1",
        "fixture_status": "synthetic_contract_fixture",
        "created_at": created_at,
        "phase": "expanded_visible_evidence_scale_simulation",
        "runtime_allowed": False,
        "runtime_listener_evidence_connected": False,
        "production_mission_generation_allowed": False,
        "canonical_graph_mutation_allowed": False,
        "candidate_song_selection_status": "not_in_scope",
        "final_mission_construction_status": "not_in_scope",
        "selector_may_read_hidden_oracle": False,
        "oracle_evaluation_fed_back_into_selector": False,
        "run_matrix": {
            "profiles": [f"public_profile_{profile}" for profile in PROFILE_IDS],
            "scales": SCALES,
            "sampling_modes": SAMPLING_MODES,
            "completed_run_count": len(per_run),
            "minimum_required_run_count": 12,
            "preferred_run_count": 24,
            "stretch_run_count": 36,
        },
        "source_refs": {
            "expanded_visible_profile_inputs_ref": repo_rel(EXPANDED_VISIBLE_OUTPUT),
            "rank_usefulness_ref": repo_rel(RANK_OUTPUT),
            "selector_outputs_root_ref": repo_rel(SELECTOR_OUTPUT_DIR),
        },
        "aggregate_rank_usefulness": aggregate,
        "determinism_summary": {
            "deterministic_rerun_matched_count": deterministic_count,
            "completed_run_count": len(per_run),
            "all_deterministic": deterministic_count == len(per_run),
            "stable_signature_sha256": stable_hash(
                [
                    {
                        "run_id": item["run_id"],
                        "top_10_mission_types": item["top_10_mission_types"],
                        "rank_regret": item["rank_regret"],
                        "ndcg_at_10": item["ndcg_at_10"],
                    }
                    for item in per_run
                ]
            ),
        },
        "per_run_metrics": per_run,
        "cross_scale_analysis": cross_scale,
        "mission_type_performance_across_scales": mt_perf,
        "hypothesis_results": hypotheses,
        "recommendations": [
            "Preserve a top-5 opportunity window before candidate-song construction; oracle-best remains in top 5 across the run matrix.",
            "Review bridge_test and artist_depth_test scoring for profiles where diagnostic boundary/context opportunities carry stronger oracle usefulness.",
            "Use 200 atoms as the next efficient simulation target unless a specific mode shows additional 300-atom improvement.",
            "Proceed to offline top-window candidate-song construction simulation only after PM accepts these scale behaviors.",
        ],
        "known_limitations": [
            "Expanded atoms are synthetic visible samples derived from held-out corpora and simplified graph refs.",
            "No real listener evidence or canonical graph authority is read.",
            "Oracle usefulness remains a post-selection proxy, not proof of final mission performance.",
        ],
        "guardrail_confirmations": [
            "No runtime wiring.",
            "No real listener evidence connection.",
            "No production mission generation.",
            "No candidate song selection.",
            "No final mission construction.",
            "No canonical graph mutation.",
            "Selector did not read hidden oracle.",
            "Oracle evaluation did not feed back into selector scoring.",
            "Expanded visible fixtures omit hidden lane metadata and oracle usefulness metrics.",
        ],
    }

    write_json(EXPANDED_VISIBLE_OUTPUT, expanded_visible)
    write_json(RANK_OUTPUT, rank_output)
    write_json(SUMMARY_JSON_OUTPUT, summary)
    SUMMARY_MD_OUTPUT.write_text(build_markdown(summary), encoding="utf-8")
    write_negative_fixtures(expanded_visible, rank_output, per_run)
    return expanded_visible, rank_output, summary


def main() -> int:
    _expanded_visible, _rank_output, summary = build_phase1e()
    print(
        "Phase 1E completed "
        f"{summary['run_matrix']['completed_run_count']} runs; "
        f"best_in_top5={summary['aggregate_rank_usefulness']['best_in_top5_count']}; "
        f"mean_rank_regret={summary['aggregate_rank_usefulness']['mean_rank_regret']}"
    )
    print(f"Wrote {repo_rel(EXPANDED_VISIBLE_OUTPUT)}")
    print(f"Wrote {repo_rel(RANK_OUTPUT)}")
    print(f"Wrote {repo_rel(SUMMARY_JSON_OUTPUT)}")
    print(f"Wrote {repo_rel(SUMMARY_MD_OUTPUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
