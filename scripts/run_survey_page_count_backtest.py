#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import math
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = REPO_ROOT / "data/survey_simulation"
GRAPH_DIR = REPO_ROOT / "data/canonical_graph/import_dry_run"
OUT_DIR = SIM_DIR / "page_count_backtest"
GENERATED_AT = "2026-05-20T12:00:00Z"
PAGE_SIZE = 12

ARTIST_PAGE_COUNTS = [2, 3, 4]
ALBUM_PAGE_COUNTS = [1, 2]
SONG_PAGE_COUNTS = [1, 2, 3]
REACTION_SCORE = {"love": 4.0, "like": 3.0, "ok": 2.0, "dont_like": 1.0}
THRESHOLDS = {
    "positive_precision": 0.70,
    "negative_precision": 0.65,
    "spearman": 0.45,
    "top_k_positive_lift": 2.0,
    "marginal_next_page_lift": 0.05,
}


def load_generator_module() -> Any:
    path = REPO_ROOT / "scripts/generate_survey_simulation_v0_1.py"
    spec = importlib.util.spec_from_file_location("survey_sim_generator", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"Cannot import generator module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gen = load_generator_module()


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


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def canonical_id_from_ref(ref: dict[str, Any]) -> str:
    return gen.canonical_ref_id(ref)


def reaction_score(reaction: str) -> float | None:
    return REACTION_SCORE.get(reaction)


def public_profile_id(index: int) -> str:
    return f"public_profile_{index:02d}"


def page_id(stage: str, page_number: int) -> str:
    return f"{stage}_page_{page_number:03d}"


def object_ref(object_type: str, obj: dict[str, Any]) -> dict[str, Any]:
    if object_type == "album":
        return gen.album_ref(obj)
    if object_type == "song_recording":
        return gen.song_ref(obj)
    if object_type == "artist":
        return gen.artist_ref(obj)
    raise ValueError(f"Unsupported object type: {object_type}")


def graph_context(obj: dict[str, Any]) -> dict[str, Any]:
    return gen.object_graph_context(obj)


def simulate_page_responses(
    run_id: str,
    page: dict[str, Any],
    hidden_corpus: dict[str, Any],
) -> dict[str, Any]:
    recorded, _ = gen.simulate_responses(run_id, page, hidden_corpus)
    for response in recorded["responses"]:
        response["response_id"] = f"{page['page_id']}_{response['response_id']}"
    return recorded


def visible_evidence_from_pages(
    pages_and_recordings: list[tuple[dict[str, Any], dict[str, Any]]],
) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    for page, recorded in pages_and_recordings:
        if page["stage"] == "artists":
            evidence.extend(gen.visible_response_evidence(page, recorded))
            continue
        tiles_by_id = {tile["tile_id"]: tile for tile in page["tiles"]}
        for response in recorded["responses"]:
            tile = tiles_by_id[response["tile_id"]]
            ref = response["music_object_ref"]
            evidence.append(
                {
                    "response_id": response["response_id"],
                    "page_id": response["page_id"],
                    "tile_id": response["tile_id"],
                    "music_object_ref": copy.deepcopy(ref),
                    "reaction": response["reaction"],
                    "interpretation": gen.response_interpretation(response["reaction"]),
                    "page_intent": tile["page_intent"],
                    "family_numbers": tile["graph_context"]["family_numbers"],
                    "archetype_ids": tile["graph_context"]["archetype_ids"],
                    "roles": tile["graph_context"]["roles"],
                    "score_final": tile["scores"]["final"],
                }
            )
    return evidence


def build_artist_adaptive_page(
    run_id: str,
    page_number: int,
    mode: str,
    selected_candidates: list[dict[str, Any]],
    target_mix_name: str,
    target_mix: list[tuple[str, int]],
    response_summary: dict[str, Any],
) -> dict[str, Any]:
    tiles = [gen.make_tile(candidate, position) for position, candidate in enumerate(selected_candidates, start=1)]
    for tile, candidate in zip(tiles, selected_candidates):
        if "response_evidence_refs" in candidate:
            tile["response_evidence_refs"] = candidate["response_evidence_refs"]
        if "suppression_warnings" in candidate:
            tile["suppression_warnings"] = candidate["suppression_warnings"]
    return {
        "schema_version": "survey_page_count_backtest.page.v0.1",
        "page_id": page_id("artist", page_number),
        "page_number": page_number,
        "stage": "artists",
        "page_mode": mode,
        "tile_count": len(tiles),
        "generator_visible_inputs": {
            "apple_payload_applied": True,
            "prior_visible_response_count": response_summary["total_response_count"],
            "hidden_inputs_consumed": False,
        },
        "adaptive_context": {
            "target_mix_name": target_mix_name,
            "target_mix": dict(target_mix),
            "response_summary": response_summary,
        },
        "tiles": tiles,
    }


def artist_name_set(ref: dict[str, Any]) -> set[str]:
    names = {ref.get("display_name", "").casefold()}
    if ref.get("artist_display_name"):
        names.add(ref["artist_display_name"].casefold())
    return {name for name in names if name}


def shared_context_score(candidate: dict[str, Any], evidence: list[dict[str, Any]]) -> tuple[float, list[dict[str, Any]]]:
    refs: list[dict[str, Any]] = []
    best = 0.0
    candidate_artists = candidate["artist_names"]
    for item in evidence:
        score = 0.0
        shared_archetypes = set(candidate["archetypes"]) & set(item["archetype_ids"])
        shared_families = set(candidate["families"]) & set(item["family_numbers"])
        shared_roles = set(candidate["roles"]) & set(item["roles"])
        if shared_archetypes:
            score += 0.42
        if shared_families:
            score += 0.22
        if shared_roles:
            score += 0.12
        if candidate_artists & artist_name_set(item["music_object_ref"]):
            score += 0.34
        if score <= 0:
            continue
        score = clamp(score)
        best = max(best, score)
        refs.append(
            {
                "response_id": item["response_id"],
                "page_id": item["page_id"],
                "tile_id": item["tile_id"],
                "reaction": item["reaction"],
                "relatedness": round(score, 3),
            }
        )
    refs.sort(key=lambda item: (-item["relatedness"], item["page_id"], item["tile_id"]))
    return round(best, 3), refs[:5]


def apple_artist_names(apple_payload: dict[str, Any]) -> set[str]:
    names = set()
    for signal in apple_payload["signals"]:
        ref = signal["music_object_ref"]
        if ref["ref_source"] == "canonical_graph":
            names.add(ref["display_name"].casefold())
    return names


def object_candidate_intent(
    object_type: str,
    obj: dict[str, Any],
    related_score: float,
    warnings: list[str],
) -> str:
    roles = set(obj.get("roles", []))
    if object_type == "album":
        if roles & {"false_nearby", "boundary", "contrast"}:
            return "test_false_nearby_album"
        if "album_anchor" in roles:
            return "test_canonical_album_anchor"
        if related_score >= 0.55:
            return "confirm_album_world"
        return "repair_album_coverage"
    if warnings or roles & {"live_gateway", "compilation_gateway"}:
        return "test_version_specificity"
    if "song_first" in roles:
        return "confirm_song_first_signal"
    if roles & {"false_nearby", "boundary", "contrast"}:
        return "test_boundary_song"
    if related_score >= 0.55:
        return "test_artist_vs_song_scope"
    return "repair_song_familiarity"


def build_object_candidate_pool(
    object_type: str,
    objects: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
    apple_payload: dict[str, Any],
    warnings_by_id: dict[str, list[str]],
) -> list[dict[str, Any]]:
    apple_names = apple_artist_names(apple_payload)
    candidates = []
    for obj in objects:
        ref = object_ref(object_type, obj)
        canonical_id = canonical_id_from_ref(ref)
        artist_names = {name.casefold() for name in obj.get("artist_names", [])}
        related_score, refs = shared_context_score(
            {
                "families": obj.get("family_numbers", []),
                "archetypes": obj.get("archetype_ids", []),
                "roles": obj.get("roles", []),
                "artist_names": artist_names,
            },
            evidence,
        )
        recognition = gen.recognition_value(obj.get("best_recognition_tier")) / 5.0
        survey = gen.survey_value(obj.get("best_survey_tier")) / 4.0
        apple_context = 1.0 if artist_names & apple_names else 0.0
        roles = set(obj.get("roles", []))
        role_value = clamp(
            (0.24 if "album_anchor" in roles else 0.0)
            + (0.22 if "song_first" in roles else 0.0)
            + (0.18 if "gateway" in roles else 0.0)
            + (0.14 if "bridge" in roles else 0.0)
            + (0.10 if roles & {"boundary", "false_nearby", "contrast"} else 0.0)
        )
        warnings = sorted(set(warnings_by_id.get(canonical_id, [])))
        expected_familiarity = clamp((recognition * 0.58) + (survey * 0.18) + (apple_context * 0.12) + (related_score * 0.12))
        information_gain = clamp((related_score * 0.34) + (role_value * 0.24) + (recognition * 0.18) + (apple_context * 0.14))
        score = round(
            (expected_familiarity * 0.42)
            + (information_gain * 0.28)
            + (related_score * 0.20)
            + (role_value * 0.10),
            3,
        )
        candidates.append(
            {
                "object": obj,
                "music_object_ref": ref,
                "canonical_id": canonical_id,
                "display_key": f"{ref['display_name']}::{ref.get('artist_display_name', '')}".casefold(),
                "families": obj.get("family_numbers", []),
                "archetypes": obj.get("archetype_ids", []),
                "roles": obj.get("roles", []),
                "artist_names": artist_names,
                "page_intent": object_candidate_intent(object_type, obj, related_score, warnings),
                "candidate_basis": [
                    "page_count_backtest_constant_seed",
                    "visible_response_evidence",
                    "canonical_graph_object",
                ],
                "graph_context": graph_context(obj),
                "response_evidence_refs": refs,
                "suppression_warnings": warnings,
                "scores": {
                    "expected_familiarity": round(expected_familiarity, 3),
                    "information_gain": round(information_gain, 3),
                    "related_response_value": related_score,
                    "role_value": round(role_value, 3),
                    "apple_artist_context": apple_context,
                    "final": score,
                },
                "reason_for_debug": f"constant {object_type} seed: final={score}, related={related_score}, familiarity={round(expected_familiarity, 3)}",
            }
        )
    candidates.sort(key=lambda item: (-item["scores"]["final"], item["music_object_ref"]["display_name"].lower(), item["canonical_id"]))
    return candidates


def select_object_page(
    object_type: str,
    candidates: list[dict[str, Any]],
    seen_keys: set[tuple[str, str]],
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    seen_display: set[str] = set()
    family_counts: Counter[int] = Counter()
    archetype_counts: Counter[str] = Counter()
    artist_counts: Counter[str] = Counter()
    for strict in [True, False]:
        for candidate in candidates:
            ref = candidate["music_object_ref"]
            key = gen.ref_key(ref)
            if key in seen_keys or candidate["display_key"] in seen_display:
                continue
            if strict:
                if candidate["families"] and all(family_counts[item] >= 4 for item in candidate["families"]):
                    continue
                if candidate["archetypes"] and all(archetype_counts[item] >= 3 for item in candidate["archetypes"]):
                    continue
                if candidate["artist_names"] and all(artist_counts[item] >= 3 for item in candidate["artist_names"]):
                    continue
            selected.append(copy.deepcopy(candidate))
            seen_keys.add(key)
            seen_display.add(candidate["display_key"])
            family_counts.update(candidate["families"])
            archetype_counts.update(candidate["archetypes"])
            artist_counts.update(candidate["artist_names"])
            if len(selected) == PAGE_SIZE:
                return selected
    return selected


def build_object_page(
    stage: str,
    object_type: str,
    page_number: int,
    selected: list[dict[str, Any]],
    prior_visible_response_count: int,
) -> dict[str, Any]:
    tiles = []
    for position, candidate in enumerate(selected, start=1):
        tiles.append(
            {
                "tile_id": f"tile_{position:02d}",
                "position": position,
                "music_object_ref": candidate["music_object_ref"],
                "page_intent": candidate["page_intent"],
                "candidate_basis": candidate["candidate_basis"],
                "graph_context": candidate["graph_context"],
                "apple_evidence": gen.blank_apple_evidence(),
                "scores": candidate["scores"],
                "response_evidence_refs": candidate["response_evidence_refs"],
                "suppression_warnings": candidate["suppression_warnings"],
                "reason_for_debug": candidate["reason_for_debug"],
            }
        )
    return {
        "schema_version": "survey_page_count_backtest.page.v0.1",
        "page_id": page_id(stage, page_number),
        "page_number": page_number,
        "stage": f"{stage}s",
        "page_mode": "apple_biased_seed",
        "tile_count": len(tiles),
        "generator_visible_inputs": {
            "apple_payload_applied": True,
            "prior_visible_response_count": prior_visible_response_count,
            "hidden_inputs_consumed": False,
        },
        "tiles": tiles,
    }


def generate_max_depth_path(
    profile_index: int,
    profile_def: dict[str, Any],
    artists: list[dict[str, Any]],
    artists_by_id: dict[str, dict[str, Any]],
    albums: list[dict[str, Any]],
    songs: list[dict[str, Any]],
    apple_payload: dict[str, Any],
    hidden_corpus: dict[str, Any],
    album_warnings: dict[str, list[str]],
    song_warnings: dict[str, list[str]],
) -> dict[str, Any]:
    public_id = public_profile_id(profile_index)
    run_id = f"PAGE_COUNT_{profile_index:02d}"
    pages_by_stage: dict[str, list[dict[str, Any]]] = {"artist": [], "album": [], "song": []}
    recordings_by_stage: dict[str, list[dict[str, Any]]] = {"artist": [], "album": [], "song": []}

    artist_pool = gen.build_artist_candidate_pool(artists, artists_by_id, apple_payload)
    selected_page1, duplicate_count = gen.optimize_page1_slate(artist_pool, "apple_biased_seed")
    artist_page1, _ = gen.build_page(
        run_id,
        "apple_biased_seed",
        selected_page1,
        "dry_run_ready_with_warnings",
        duplicate_count,
    )
    artist_page1["page_id"] = page_id("artist", 1)
    artist_page1["schema_version"] = "survey_page_count_backtest.page.v0.1"
    pages_by_stage["artist"].append(artist_page1)
    recordings_by_stage["artist"].append(simulate_page_responses(run_id, artist_page1, hidden_corpus))

    for page_number in range(2, 5):
        evidence = visible_evidence_from_pages(
            list(zip(pages_by_stage["artist"], recordings_by_stage["artist"]))
        )
        summary = gen.summarize_response_evidence(evidence)
        target_mix_name, target_mix = gen.page2_target_mix(summary, "apple_biased_seed")
        selected, _ = gen.optimize_page2_slate(artist_pool, evidence, target_mix, "apple_biased_seed")
        page = build_artist_adaptive_page(
            run_id,
            page_number,
            "apple_biased_seed",
            selected,
            target_mix_name,
            target_mix,
            summary,
        )
        pages_by_stage["artist"].append(page)
        recordings_by_stage["artist"].append(simulate_page_responses(run_id, page, hidden_corpus))

    all_evidence = visible_evidence_from_pages(
        list(zip(pages_by_stage["artist"], recordings_by_stage["artist"]))
    )
    seen_album_keys: set[tuple[str, str]] = set()
    for page_number in range(1, 3):
        prior_count = len(all_evidence)
        pool = build_object_candidate_pool("album", albums, all_evidence, apple_payload, album_warnings)
        selected = select_object_page("album", pool, seen_album_keys)
        page = build_object_page("album", "album", page_number, selected, prior_count)
        recorded = simulate_page_responses(run_id, page, hidden_corpus)
        pages_by_stage["album"].append(page)
        recordings_by_stage["album"].append(recorded)
        all_evidence = visible_evidence_from_pages(
            [
                *list(zip(pages_by_stage["artist"], recordings_by_stage["artist"])),
                *list(zip(pages_by_stage["album"], recordings_by_stage["album"])),
            ]
        )

    seen_song_keys: set[tuple[str, str]] = set()
    for page_number in range(1, 4):
        prior_count = len(all_evidence)
        pool = build_object_candidate_pool("song_recording", songs, all_evidence, apple_payload, song_warnings)
        selected = select_object_page("song_recording", pool, seen_song_keys)
        page = build_object_page("song", "song_recording", page_number, selected, prior_count)
        recorded = simulate_page_responses(run_id, page, hidden_corpus)
        pages_by_stage["song"].append(page)
        recordings_by_stage["song"].append(recorded)
        all_evidence = visible_evidence_from_pages(
            [
                *list(zip(pages_by_stage["artist"], recordings_by_stage["artist"])),
                *list(zip(pages_by_stage["album"], recordings_by_stage["album"])),
                *list(zip(pages_by_stage["song"], recordings_by_stage["song"])),
            ]
        )

    return {
        "schema_version": "survey_page_count_backtest.max_depth_path.v0.1",
        "generated_at": GENERATED_AT,
        "profile_public_id": public_id,
        "apple_payload_id": apple_payload["apple_payload_id"],
        "hidden_inputs_used_for_generation": False,
        "hidden_inputs_used_for_response_simulation": True,
        "pages_by_stage": pages_by_stage,
        "recorded_responses_by_stage": recordings_by_stage,
    }


def selected_prefix_pairs(path: dict[str, Any], artist_pages: int, album_pages: int, song_pages: int) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    pairs: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for stage, count in [("artist", artist_pages), ("album", album_pages), ("song", song_pages)]:
        pages = path["pages_by_stage"][stage][:count]
        recordings = path["recorded_responses_by_stage"][stage][:count]
        pairs.extend(zip(pages, recordings))
    return pairs


def observed_key_set(pairs: list[tuple[dict[str, Any], dict[str, Any]]]) -> set[tuple[str, str]]:
    keys = set()
    for page, _ in pairs:
        for tile in page["tiles"]:
            keys.add(gen.ref_key(tile["music_object_ref"]))
    return keys


def graph_lookup(artists: list[dict[str, Any]], albums: list[dict[str, Any]], songs: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    artists_by_id = {artist["canonical_artist_id"]: artist for artist in artists}
    return gen.object_lookup_index(artists_by_id, albums, songs)


def observation_stats(observed: list[dict[str, Any]], object_lookup: dict[tuple[str, str], dict[str, Any]]) -> dict[str, Any]:
    stats = {
        "overall": [],
        "object_type": defaultdict(list),
        "archetype": defaultdict(list),
        "family": defaultdict(list),
        "role": defaultdict(list),
        "artist_name": defaultdict(list),
    }
    for item in observed:
        score = reaction_score(item["reaction"])
        if score is None:
            continue
        ref = item["music_object_ref"]
        obj = object_lookup.get(gen.ref_key(ref))
        if not obj:
            continue
        stats["overall"].append(score)
        stats["object_type"][ref["object_type"]].append(score)
        for archetype in obj.get("archetype_ids", []):
            stats["archetype"][archetype].append(score)
        for family in obj.get("family_numbers", []):
            stats["family"][family].append(score)
        for role in obj.get("roles", []):
            stats["role"][role].append(score)
        for name in artist_name_set(ref):
            stats["artist_name"][name].append(score)
        for name in obj.get("artist_names", []):
            stats["artist_name"][name.casefold()].append(score)
    return stats


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def shrunk_mean(values: list[float], prior: float, prior_weight: float) -> float:
    if not values:
        return prior
    return (sum(values) + prior * prior_weight) / (len(values) + prior_weight)


def predict_score_for_object(
    ref: dict[str, Any],
    obj: dict[str, Any],
    stats: dict[str, Any],
) -> float:
    overall = mean(stats["overall"]) if stats["overall"] else 2.1
    recognition_prior = {
        "mass": 2.22,
        "high": 2.08,
        "medium": 1.94,
        "cult": 1.82,
        "low": 1.74,
        "niche": 1.70,
    }.get(obj.get("best_recognition_tier"), 2.0)
    score = (overall * 0.64) + (recognition_prior * 0.36)
    object_type_values = stats["object_type"].get(ref["object_type"], [])
    if object_type_values:
        object_mean = shrunk_mean(object_type_values, overall, 8.0)
        score += (object_mean - overall) * 0.35
    artist_values = []
    for name in artist_name_set(ref):
        artist_values.extend(stats["artist_name"].get(name, []))
    for name in obj.get("artist_names", []):
        artist_values.extend(stats["artist_name"].get(name.casefold(), []))
    if artist_values:
        artist_mean = shrunk_mean(artist_values, overall, 1.5)
        score += (artist_mean - overall) * 1.45
    archetype_values = []
    for archetype in obj.get("archetype_ids", []):
        archetype_values.extend(stats["archetype"].get(archetype, []))
    if archetype_values:
        archetype_mean = shrunk_mean(archetype_values, overall, 2.0)
        score += (archetype_mean - overall) * 1.30
    family_values = []
    for family in obj.get("family_numbers", []):
        family_values.extend(stats["family"].get(family, []))
    if family_values:
        family_mean = shrunk_mean(family_values, overall, 3.0)
        score += (family_mean - overall) * 0.78
    role_values = []
    for role in obj.get("roles", []):
        role_values.extend(stats["role"].get(role, []))
    if role_values:
        role_mean = shrunk_mean(role_values, overall, 5.0)
        score += (role_mean - overall) * 0.28
    return round(max(1.0, min(4.0, score)), 4)


def predicted_label(score: float) -> str:
    if score >= 2.75:
        return "positive"
    if score < 1.75:
        return "negative"
    return "waypoint"


def actual_label(score: float) -> str:
    if score >= 3.0:
        return "positive"
    if score <= 1.0:
        return "negative"
    return "waypoint"


def ranks(values: list[float]) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda item: item[1])
    result = [0.0] * len(values)
    index = 0
    while index < len(indexed):
        end = index + 1
        while end < len(indexed) and indexed[end][1] == indexed[index][1]:
            end += 1
        rank = (index + 1 + end) / 2.0
        for original_index, _ in indexed[index:end]:
            result[original_index] = rank
        index = end
    return result


def spearman(predicted: list[float], actual: list[float]) -> float:
    if len(predicted) < 2:
        return 0.0
    pred_ranks = ranks(predicted)
    actual_ranks = ranks(actual)
    pred_mean = mean(pred_ranks)
    actual_mean = mean(actual_ranks)
    numerator = sum((p - pred_mean) * (a - actual_mean) for p, a in zip(pred_ranks, actual_ranks))
    pred_var = sum((p - pred_mean) ** 2 for p in pred_ranks)
    actual_var = sum((a - actual_mean) ** 2 for a in actual_ranks)
    if pred_var <= 0 or actual_var <= 0:
        return 0.0
    return numerator / math.sqrt(pred_var * actual_var)


def precision_recall(pred_labels: list[str], actual_labels: list[str], label: str) -> tuple[float, float]:
    tp = sum(1 for pred, actual in zip(pred_labels, actual_labels) if pred == label and actual == label)
    fp = sum(1 for pred, actual in zip(pred_labels, actual_labels) if pred == label and actual != label)
    fn = sum(1 for pred, actual in zip(pred_labels, actual_labels) if pred != label and actual == label)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return precision, recall


def top_bottom_lift(predicted: list[float], actual_scores: list[float]) -> tuple[float, float]:
    total = len(predicted)
    if not total:
        return 0.0, 0.0
    k = min(50, max(10, total // 10))
    base_positive = sum(1 for score in actual_scores if score >= 3.0) / total
    base_negative = sum(1 for score in actual_scores if score <= 1.0) / total
    ranked = sorted(zip(predicted, actual_scores), key=lambda item: item[0], reverse=True)
    top_positive = sum(1 for _, score in ranked[:k] if score >= 3.0) / k
    bottom_negative = sum(1 for _, score in ranked[-k:] if score <= 1.0) / k
    return (
        top_positive / base_positive if base_positive else 0.0,
        bottom_negative / base_negative if base_negative else 0.0,
    )


def calibration_error(predicted: list[float], actual_scores: list[float], bins: int = 5) -> float:
    buckets: dict[int, list[tuple[float, float]]] = defaultdict(list)
    for pred, actual in zip(predicted, actual_scores):
        probability = clamp((pred - 1.0) / 3.0)
        bucket = min(bins - 1, int(probability * bins))
        buckets[bucket].append((probability, 1.0 if actual >= 3.0 else 0.0))
    total = len(predicted)
    if not total:
        return 0.0
    return sum(
        (len(items) / total) * abs(mean([item[0] for item in items]) - mean([item[1] for item in items]))
        for items in buckets.values()
    )


def quality_score(metrics: dict[str, float]) -> float:
    spearman_norm = (metrics["spearman"] + 1.0) / 2.0
    mae_score = clamp(1.0 - metrics["mae"] / 3.0)
    lift_score = clamp(metrics["top_k_positive_lift"] / 3.0)
    calibration_score = clamp(1.0 - metrics["calibration_error"])
    return round(
        (spearman_norm * 0.20)
        + (mae_score * 0.18)
        + (metrics["positive_precision"] * 0.16)
        + (metrics["negative_precision"] * 0.14)
        + (lift_score * 0.12)
        + (metrics["classification_accuracy"] * 0.10)
        + (metrics["positive_recall"] * 0.05)
        + (metrics["negative_recall"] * 0.03)
        + (calibration_score * 0.02),
        4,
    )


def evaluate_profile_config(
    path: dict[str, Any],
    hidden_corpus: dict[str, Any],
    object_lookup: dict[tuple[str, str], dict[str, Any]],
    artist_pages: int,
    album_pages: int,
    song_pages: int,
) -> dict[str, Any]:
    pairs = selected_prefix_pairs(path, artist_pages, album_pages, song_pages)
    observed_evidence = visible_evidence_from_pages(pairs)
    known_observed = [item for item in observed_evidence if reaction_score(item["reaction"]) is not None]
    observed_keys = observed_key_set(pairs)
    stats = observation_stats(known_observed, object_lookup)

    predicted: list[float] = []
    actual_scores: list[float] = []
    hidden_lookup = gen.hidden_lookup_map(hidden_corpus)
    for key, hidden_reaction in hidden_lookup.items():
        if key in observed_keys:
            continue
        actual = reaction_score(hidden_reaction["reaction"])
        if actual is None:
            continue
        obj = object_lookup.get(key)
        if obj is None:
            continue
        pred = predict_score_for_object(hidden_reaction["music_object_ref"], obj, stats)
        predicted.append(pred)
        actual_scores.append(actual)

    if not actual_scores:
        raise ValueError("No held-out populated hidden reactions available")

    abs_errors = [abs(pred - actual) for pred, actual in zip(predicted, actual_scores)]
    sq_errors = [(pred - actual) ** 2 for pred, actual in zip(predicted, actual_scores)]
    pred_labels = [predicted_label(score) for score in predicted]
    true_labels = [actual_label(score) for score in actual_scores]
    positive_precision, positive_recall = precision_recall(pred_labels, true_labels, "positive")
    negative_precision, negative_recall = precision_recall(pred_labels, true_labels, "negative")
    waypoint_precision, waypoint_recall = precision_recall(pred_labels, true_labels, "waypoint")
    top_lift, bottom_lift = top_bottom_lift(predicted, actual_scores)
    metrics = {
        "config_id": f"A{artist_pages}_Al{album_pages}_S{song_pages}",
        "artist_pages": artist_pages,
        "album_pages": album_pages,
        "song_pages": song_pages,
        "tiles": (artist_pages + album_pages + song_pages) * PAGE_SIZE,
        "known_responses": len(known_observed),
        "heldout_count": len(actual_scores),
        "mae": round(mean(abs_errors), 4),
        "rmse": round(math.sqrt(mean(sq_errors)), 4),
        "spearman": round(spearman(predicted, actual_scores), 4),
        "classification_accuracy": round(sum(1 for pred, actual in zip(pred_labels, true_labels) if pred == actual) / len(true_labels), 4),
        "positive_precision": round(positive_precision, 4),
        "positive_recall": round(positive_recall, 4),
        "negative_precision": round(negative_precision, 4),
        "negative_recall": round(negative_recall, 4),
        "ok_waypoint_precision": round(waypoint_precision, 4),
        "ok_waypoint_recall": round(waypoint_recall, 4),
        "top_k_positive_lift": round(top_lift, 4),
        "bottom_k_negative_lift": round(bottom_lift, 4),
        "calibration_error": round(calibration_error(predicted, actual_scores), 4),
    }
    metrics["quality_score"] = quality_score(metrics)
    return metrics


def aggregate_config_metrics(per_profile: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_config: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in per_profile:
        by_config[item["config_id"]].append(item)
    aggregated = []
    numeric_keys = [
        "tiles",
        "known_responses",
        "heldout_count",
        "mae",
        "rmse",
        "spearman",
        "classification_accuracy",
        "positive_precision",
        "positive_recall",
        "negative_precision",
        "negative_recall",
        "ok_waypoint_precision",
        "ok_waypoint_recall",
        "top_k_positive_lift",
        "bottom_k_negative_lift",
        "calibration_error",
        "quality_score",
    ]
    for config_id, rows in sorted(by_config.items(), key=lambda item: (item[1][0]["tiles"], item[0])):
        base = {
            "config_id": config_id,
            "artist_pages": rows[0]["artist_pages"],
            "album_pages": rows[0]["album_pages"],
            "song_pages": rows[0]["song_pages"],
        }
        for key in numeric_keys:
            values = [float(row[key]) for row in rows]
            base[key] = round(mean(values), 4)
        base["profile_count"] = len(rows)
        aggregated.append(base)
    max_quality = max(item["quality_score"] for item in aggregated)
    for item in aggregated:
        item["achievable_signal_pct"] = round((item["quality_score"] / max_quality) * 100.0, 2) if max_quality else 0.0
        item["signal_per_tile"] = round(item["quality_score"] / item["tiles"], 6)
        item["fatigue_adjusted_score"] = round(item["quality_score"] - ((item["tiles"] - 48) * 0.001), 4)
    quality_by_dims = {
        (item["artist_pages"], item["album_pages"], item["song_pages"]): item["quality_score"]
        for item in aggregated
    }
    for item in aggregated:
        predecessors = []
        dims = (item["artist_pages"], item["album_pages"], item["song_pages"])
        for delta in [(1, 0, 0), (0, 1, 0), (0, 0, 1)]:
            prev = (dims[0] - delta[0], dims[1] - delta[1], dims[2] - delta[2])
            if prev in quality_by_dims:
                predecessors.append(quality_by_dims[prev])
        if not predecessors:
            item["marginal_lift_per_added_page"] = None
        else:
            item["marginal_lift_per_added_page"] = round(item["quality_score"] - max(predecessors), 4)
    return aggregated


def marginal_lift_by_page_type(config_metrics: list[dict[str, Any]]) -> dict[str, Any]:
    quality = {
        (item["artist_pages"], item["album_pages"], item["song_pages"]): item["quality_score"]
        for item in config_metrics
    }
    output: dict[str, Any] = {}
    comparisons = {
        "artist_A2_to_A3": ((2, None, None), (3, None, None)),
        "artist_A3_to_A4": ((3, None, None), (4, None, None)),
        "album_Al1_to_Al2": ((None, 1, None), (None, 2, None)),
        "song_S1_to_S2": ((None, None, 1), (None, None, 2)),
        "song_S2_to_S3": ((None, None, 2), (None, None, 3)),
    }
    for name, (before, after) in comparisons.items():
        deltas = []
        for dims, score in quality.items():
            a, al, s = dims
            before_match = (
                (before[0] is None or a == before[0])
                and (before[1] is None or al == before[1])
                and (before[2] is None or s == before[2])
            )
            if not before_match:
                continue
            target = (
                after[0] if after[0] is not None else a,
                after[1] if after[1] is not None else al,
                after[2] if after[2] is not None else s,
            )
            if target in quality:
                deltas.append(quality[target] - score)
        output[name] = {
            "mean_quality_lift": round(mean(deltas), 4),
            "comparison_count": len(deltas),
            "deltas": [round(value, 4) for value in deltas],
        }
    return output


def config_passes_thresholds(item: dict[str, Any], next_lift: float | None) -> bool:
    return (
        item["positive_precision"] >= THRESHOLDS["positive_precision"]
        and item["negative_precision"] >= THRESHOLDS["negative_precision"]
        and item["spearman"] >= THRESHOLDS["spearman"]
        and item["top_k_positive_lift"] >= THRESHOLDS["top_k_positive_lift"]
        and (next_lift is None or next_lift < THRESHOLDS["marginal_next_page_lift"])
    )


def best_next_lift(item: dict[str, Any], quality_by_dims: dict[tuple[int, int, int], float]) -> float | None:
    dims = (item["artist_pages"], item["album_pages"], item["song_pages"])
    next_scores = []
    for delta in [(1, 0, 0), (0, 1, 0), (0, 0, 1)]:
        next_dims = (dims[0] + delta[0], dims[1] + delta[1], dims[2] + delta[2])
        if next_dims in quality_by_dims:
            next_scores.append(quality_by_dims[next_dims] - item["quality_score"])
    return max(next_scores) if next_scores else None


def recommended_config(config_metrics: list[dict[str, Any]]) -> dict[str, Any]:
    quality_by_dims = {
        (item["artist_pages"], item["album_pages"], item["song_pages"]): item["quality_score"]
        for item in config_metrics
    }
    candidates = []
    for item in config_metrics:
        next_lift = best_next_lift(item, quality_by_dims)
        if config_passes_thresholds(item, next_lift):
            candidate = copy.deepcopy(item)
            candidate["max_next_page_lift"] = round(next_lift, 4) if next_lift is not None else None
            candidates.append(candidate)
    if candidates:
        candidates.sort(key=lambda item: (item["tiles"], -item["fatigue_adjusted_score"], item["config_id"]))
        recommendation = candidates[0]
        recommendation["decision_status"] = "threshold_pass"
        recommendation["minimum_pages_to_threshold"] = recommendation["config_id"]
        return recommendation
    fallback = max(config_metrics, key=lambda item: (item["fatigue_adjusted_score"], item["quality_score"]))
    recommendation = copy.deepcopy(fallback)
    recommendation["max_next_page_lift"] = round(best_next_lift(fallback, quality_by_dims) or 0.0, 4)
    recommendation["decision_status"] = "fallback_best_fatigue_adjusted"
    recommendation["minimum_pages_to_threshold"] = None
    return recommendation


def report_table(config_metrics: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| Config | Tiles | Known responses | MAE | Spearman | Positive precision | Negative precision | Top-K lift | Marginal lift | Fatigue score |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in sorted(config_metrics, key=lambda row: (row["tiles"], row["artist_pages"], row["album_pages"], row["song_pages"])):
        marginal = "baseline" if item["marginal_lift_per_added_page"] is None else f"{item['marginal_lift_per_added_page']:+.3f}"
        lines.append(
            "| {config} | {tiles} | {known:.1f} | {mae:.3f} | {spearman:.3f} | {pos:.3f} | {neg:.3f} | {lift:.2f} | {marginal} | {fatigue:.3f} |".format(
                config=item["config_id"].replace("_", " "),
                tiles=int(item["tiles"]),
                known=item["known_responses"],
                mae=item["mae"],
                spearman=item["spearman"],
                pos=item["positive_precision"],
                neg=item["negative_precision"],
                lift=item["top_k_positive_lift"],
                marginal=marginal,
                fatigue=item["fatigue_adjusted_score"],
            )
        )
    return lines


def render_backtest_report(
    config_metrics: list[dict[str, Any]],
    marginal: dict[str, Any],
    recommendation: dict[str, Any],
) -> str:
    lines = [
        "# Survey Page Count Backtest Report",
        "",
        f"Generated: {GENERATED_AT}",
        "",
        "## Objective",
        "",
        "Hold the survey page-seeding algorithm constant and test how many artist, album, and song survey pages are needed to predict each fake profile's remaining populated hidden taste map.",
        "",
        "## Matrix",
        "",
        "- Artist pages: 2, 3, 4",
        "- Album pages: 1, 2",
        "- Song pages: 1, 2, 3",
        "- Configurations: 18",
        "- Survey size range: 48 to 108 tiles",
        "",
        "## Decision Thresholds",
        "",
        f"- Positive precision >= {THRESHOLDS['positive_precision']}",
        f"- Negative precision >= {THRESHOLDS['negative_precision']}",
        f"- Spearman >= {THRESHOLDS['spearman']}",
        f"- Top-K positive lift >= {THRESHOLDS['top_k_positive_lift']}x random",
        f"- Max next-page marginal lift < {THRESHOLDS['marginal_next_page_lift']}",
        "",
        "## Config Metrics",
        "",
        *report_table(config_metrics),
        "",
        "## Marginal Lift by Page Type",
        "",
        "| Page addition | Mean quality lift | Comparisons |",
        "|---|---:|---:|",
    ]
    for name, payload in marginal.items():
        lines.append(f"| `{name}` | {payload['mean_quality_lift']:+.4f} | {payload['comparison_count']} |")
    lines.extend(
        [
            "",
            "## Recommended Minimum",
            "",
            f"- Config: `{recommendation['config_id']}`",
            f"- Tiles: {int(recommendation['tiles'])}",
            f"- Decision status: `{recommendation['decision_status']}`",
            f"- Minimum pages to threshold: `{recommendation['minimum_pages_to_threshold']}`",
            f"- Quality score: {recommendation['quality_score']}",
            f"- Fatigue-adjusted score: {recommendation['fatigue_adjusted_score']}",
            f"- Achievable signal: {recommendation['achievable_signal_pct']}%",
            f"- Max next-page lift: {recommendation['max_next_page_lift']}",
            "",
            "No page-count configuration currently clears all pre-declared quality thresholds. The recommendation is therefore the best fatigue-adjusted fallback, not a final product answer.",
            "",
            "## Boundary Checks",
            "",
            "- Hidden corpora are used only to simulate selected responses and evaluate held-out ground truth.",
            "- Page generation consumes canonical graph data, Apple payload evidence, and prior visible responses only.",
            "- Held-out scoring excludes unpopulated/null hidden entries and excludes every object shown in the evaluated prefix.",
            "- Canonical graph data is read-only.",
            "",
        ]
    )
    return "\n".join(lines)


def render_recommendation(recommendation: dict[str, Any], marginal: dict[str, Any]) -> str:
    lines = [
        "# Recommended Minimum Config",
        "",
        f"Recommended config: `{recommendation['config_id']}`",
        "",
        f"- Tiles: {int(recommendation['tiles'])}",
        f"- Decision status: `{recommendation['decision_status']}`",
        f"- Minimum pages to threshold: `{recommendation['minimum_pages_to_threshold']}`",
        f"- Positive precision: {recommendation['positive_precision']}",
        f"- Negative precision: {recommendation['negative_precision']}",
        f"- Spearman: {recommendation['spearman']}",
        f"- Top-K positive lift: {recommendation['top_k_positive_lift']}x",
        f"- Max next-page lift: {recommendation['max_next_page_lift']}",
        "",
        "No configuration reached every pre-declared threshold in this deterministic backtest. Treat this as a harness signal that the predictor and/or fake hidden-map realism needs another pass before deciding final onboarding length.",
        "",
        "Decision doctrine: select the smallest page configuration that reaches the predictive quality threshold and then shows diminishing marginal return relative to asking for another page.",
        "",
        "Page-type lift summary:",
    ]
    for name, payload in marginal.items():
        lines.append(f"- `{name}`: {payload['mean_quality_lift']:+.4f}")
    lines.append("")
    return "\n".join(lines)


def generate() -> None:
    graph_before = gen.graph_fingerprint()
    artists = load_json(GRAPH_DIR / "canonical_artists.json")
    albums = load_json(GRAPH_DIR / "canonical_albums.json")
    songs = load_json(GRAPH_DIR / "canonical_song_recordings.json")
    album_memberships = load_json(GRAPH_DIR / "album_archetype_memberships.json")
    song_memberships = load_json(GRAPH_DIR / "song_archetype_memberships.json")
    artists_by_id = {artist["canonical_artist_id"]: artist for artist in artists}
    object_lookup = graph_lookup(artists, albums, songs)
    album_warnings = gen.membership_warning_index(album_memberships, "canonical_album_id")
    song_warnings = gen.membership_warning_index(song_memberships, "canonical_song_recording_id")

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    paths = []
    per_profile_metrics = []
    for index, profile_def in enumerate(gen.PROFILE_DEFINITIONS, start=1):
        apple_payload = load_json(SIM_DIR / "apple_payloads" / f"apple_payload_{index:02d}.json")
        hidden_corpus = load_json(SIM_DIR / "hidden_reaction_corpora" / f"hidden_corpus_{index:02d}.json")
        path = generate_max_depth_path(
            index,
            profile_def,
            artists,
            artists_by_id,
            albums,
            songs,
            apple_payload,
            hidden_corpus,
            album_warnings,
            song_warnings,
        )
        paths.append(path)
        write_json(OUT_DIR / "max_depth_paths" / f"{public_profile_id(index)}.json", path)
        for artist_pages in ARTIST_PAGE_COUNTS:
            for album_pages in ALBUM_PAGE_COUNTS:
                for song_pages in SONG_PAGE_COUNTS:
                    metrics = evaluate_profile_config(
                        path,
                        hidden_corpus,
                        object_lookup,
                        artist_pages,
                        album_pages,
                        song_pages,
                    )
                    metrics["profile_public_id"] = public_profile_id(index)
                    per_profile_metrics.append(metrics)

    config_metrics = aggregate_config_metrics(per_profile_metrics)
    marginal = marginal_lift_by_page_type(config_metrics)
    recommendation = recommended_config(config_metrics)
    graph_after = gen.graph_fingerprint()
    metadata = {
        "schema_version": "survey_page_count_backtest.metadata.v0.1",
        "generated_at": GENERATED_AT,
        "profile_count": len(paths),
        "config_count": len(config_metrics),
        "page_count_matrix": {
            "artist_pages": ARTIST_PAGE_COUNTS,
            "album_pages": ALBUM_PAGE_COUNTS,
            "song_pages": SONG_PAGE_COUNTS,
        },
        "hidden_inputs_used_for_page_generation": False,
        "hidden_inputs_used_for_response_simulation_and_scoring": True,
        "canonical_graph_fingerprint_unchanged": graph_before["sha256"] == graph_after["sha256"],
        "before_graph_sha256": graph_before["sha256"],
        "after_graph_sha256": graph_after["sha256"],
        "thresholds": THRESHOLDS,
    }
    write_json(OUT_DIR / "config_metrics.json", {"metadata": metadata, "configs": config_metrics})
    write_json(OUT_DIR / "per_profile_metrics.json", {"metadata": metadata, "profiles": per_profile_metrics})
    write_json(OUT_DIR / "marginal_lift_by_page_type.json", {"metadata": metadata, "marginal_lift_by_page_type": marginal})
    write_text(OUT_DIR / "page_count_backtest_report.md", render_backtest_report(config_metrics, marginal, recommendation))
    write_text(OUT_DIR / "recommended_minimum_config.md", render_recommendation(recommendation, marginal))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Survey page-count prediction backtest.")
    parser.parse_args()
    generate()
    print(f"Generated survey page-count backtest at {OUT_DIR.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
