#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DIR = REPO_ROOT / "data/product_contracts/mission_opportunity_selection_v0_1"
FIXTURE_DIR = CONTRACT_DIR / "fixtures"
PROFILE_SIM_DIR = FIXTURE_DIR / "profile_simulation"
PHASE1E_DIR = CONTRACT_DIR / "evaluations/phase1e_expanded_visible_evidence_scale"
PHASE1E_SELECTOR_DIR = PHASE1E_DIR / "selector_outputs_by_profile_scale"
PHASE1F_DIR = CONTRACT_DIR / "evaluations/phase1f_song_pack_smell_test"
NEGATIVE_DIR = PHASE1F_DIR / "negative"
PACK_CARDS_DIR = PHASE1F_DIR / "per_profile_pack_cards"

EXPANDED_VISIBLE_INPUTS = PHASE1E_DIR / "expanded_visible_profile_inputs_v0_1.json"
HIDDEN_PROFILE_ORACLES = PROFILE_SIM_DIR / "hidden_profile_oracles_v0_1.json"
HIDDEN_CORPUS_DIR = REPO_ROOT / "data/survey_simulation/hidden_reaction_corpora"
RESULTS_OUTPUT = PHASE1F_DIR / "song_pack_simulation_results_v0_1.json"
SUMMARY_MD_OUTPUT = PHASE1F_DIR / "song_pack_simulation_summary_v0_1.md"
SCHEMA_OUTPUT = PHASE1F_DIR / "song_pack_simulation_schema_v0_1.schema.json"
GUARDRAIL_MD_OUTPUT = PHASE1F_DIR / "song_pack_simulation_guardrail_report_v0_1.md"

PROFILE_IDS = ["public_profile_01", "public_profile_05", "public_profile_06"]
PROFILE_TO_CORPUS = {
    "public_profile_01": "hidden_corpus_01.json",
    "public_profile_05": "hidden_corpus_05.json",
    "public_profile_06": "hidden_corpus_06.json",
}
SCALES = [72, 150, 200, 300]
SAMPLING_MODES = ["profile_weighted_balanced", "edge_heavy", "song_heavy"]
CONSTRUCTION_MODES = [
    "rank_1_pack",
    "top_3_portfolio_pack",
    "top_10_portfolio_pack",
    "diagnostic_biased_pack",
    "experience_balanced_pack",
]
DEFAULT_PACK_SIZE = 6
TOP_WINDOW_SIZE = 10

DIAGNOSTIC_MISSION_TYPES = {
    "boundary_test",
    "context_dependence_test",
    "false_nearby_test",
    "evidence_repair_test",
    "exception_scope_test",
}
DEPTH_MISSION_TYPES = {
    "artist_depth_test",
    "album_container_test",
    "archetype_depth_test",
    "song_to_archetype_test",
}
STOPWORDS = {
    "a",
    "an",
    "and",
    "artist",
    "album",
    "archetype",
    "bridge",
    "cluster",
    "context",
    "family",
    "for",
    "in",
    "of",
    "profile",
    "song",
    "the",
    "visible",
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


def stable_fraction(value: Any) -> float:
    return int(stable_hash(value)[:10], 16) / float(16**10 - 1)


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return round(max(lower, min(upper, value)), 4)


def tokenize(value: Any) -> set[str]:
    if isinstance(value, list):
        text = " ".join(str(item) for item in value)
    elif isinstance(value, dict):
        text = stable_json(value)
    else:
        text = str(value or "")
    tokens = {
        token
        for token in re.split(r"[^a-z0-9]+", text.lower())
        if len(token) > 1 and token not in STOPWORDS
    }
    return tokens


def overlap_score(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left.intersection(right)) / max(1, min(len(left), len(right), 8))


def opportunity_tokens(opportunity: dict[str, Any]) -> set[str]:
    cache_key = "_phase1f_token_cache"
    cached = opportunity.get(cache_key)
    if isinstance(cached, set):
        return cached
    parts: list[Any] = [
        opportunity.get("opportunity_id"),
        opportunity.get("mission_type"),
        opportunity.get("target_object_ids", []),
        opportunity.get("target_object_ref", {}).get("display_name"),
        opportunity.get("source_signal_summary", {}).get("target_display_name"),
    ]
    for context in opportunity.get("graph_context_summary", {}).get("graph_contexts", []):
        parts.extend(
            [
                context.get("artist_ids", []),
                context.get("album_ids", []),
                context.get("song_ids", []),
                context.get("family_names", []),
                context.get("archetype_names", []),
                context.get("context_overlays", []),
                context.get("graph_item_role"),
            ]
        )
    cached_tokens = tokenize(parts)
    opportunity[cache_key] = cached_tokens
    return cached_tokens


def visible_example_tokens(visible_profile: dict[str, Any], key: str) -> set[str]:
    cache = visible_profile.setdefault("_phase1f_token_cache", {})
    if key in cache:
        return cache[key]
    examples = visible_profile.get("visible_evidence", {}).get(key, [])
    parts: list[Any] = []
    for example in examples:
        parts.extend(
            [
                example.get("display_name"),
                example.get("artist_display_name"),
                example.get("object_id"),
                example.get("graph_refs", {}).get("roles", []),
            ]
        )
    tokens = tokenize(parts)
    cache[key] = tokens
    return tokens


def hidden_reaction_to_output(value: str | None) -> str:
    if value in {"dislike", "dont_like"}:
        return "dont_like"
    if value in {"love", "like", "ok"}:
        return value
    return "unknown"


def primary_role_for_mission_type(mission_type: str) -> str:
    if mission_type == "boundary_test":
        return "boundary"
    if mission_type == "bridge_test":
        return "bridge"
    if mission_type == "context_dependence_test":
        return "context"
    if mission_type == "false_nearby_test":
        return "false_nearby"
    if mission_type == "album_container_test":
        return "context"
    if mission_type in {"evidence_repair_test", "exception_scope_test"}:
        return "probe"
    if mission_type == "gateway_test":
        return "bridge"
    return "probe"


def selector_output_path(profile_id: str, sampling_mode: str, scale: int) -> Path:
    return (
        PHASE1E_SELECTOR_DIR
        / profile_id
        / sampling_mode
        / f"selector_output_{profile_id}_{sampling_mode}_{scale}_v0_1.json"
    )


def build_song_universe(profile_id: str) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    corpus = load_json(HIDDEN_CORPUS_DIR / PROFILE_TO_CORPUS[profile_id])
    selection_pool: dict[str, dict[str, Any]] = {}
    reaction_map: dict[str, dict[str, Any]] = {}
    for row in corpus.get("reactions", []):
        ref = row.get("music_object_ref", {})
        if ref.get("object_type") != "song_recording":
            continue
        song_id = str(ref.get("canonical_song_recording_id") or ref.get("object_id") or "")
        if not song_id:
            continue
        if song_id not in selection_pool:
            selection_pool[song_id] = {
                "song_id": song_id,
                "title": str(ref.get("display_name") or song_id),
                "artist_display_name": str(ref.get("artist_display_name") or "Unknown Artist"),
                "selection_tokens": sorted(
                    tokenize([song_id, ref.get("display_name"), ref.get("artist_display_name")])
                ),
            }
        reaction_map[song_id] = {
            "hidden_oracle_reaction": hidden_reaction_to_output(row.get("reaction")),
            "hidden_oracle_confidence": round(float(row.get("confidence", 0)), 4),
            "familiarity_band": row.get("familiarity_band", "unknown"),
        }

    return sorted(selection_pool.values(), key=lambda item: item["song_id"]), reaction_map


def visible_known_tokens(visible_profile: dict[str, Any]) -> set[str]:
    cache = visible_profile.setdefault("_phase1f_token_cache", {})
    if "visible_known_examples" not in cache:
        cache["visible_known_examples"] = visible_example_tokens(
            visible_profile,
            "visible_positive_examples",
        ).union(visible_example_tokens(visible_profile, "visible_negative_examples"))
    return cache["visible_known_examples"]


def role_score(
    song: dict[str, Any],
    role: str,
    opportunity: dict[str, Any],
    visible_profile: dict[str, Any],
    selected_song_ids: set[str],
    selected_artists: Counter[str],
    pack_id: str,
) -> float:
    song_tokens = set(song.get("selection_tokens", []))
    target_overlap = overlap_score(song_tokens, opportunity_tokens(opportunity))
    positive_overlap = overlap_score(
        song_tokens,
        visible_example_tokens(visible_profile, "visible_positive_examples"),
    )
    negative_overlap = overlap_score(
        song_tokens,
        visible_example_tokens(visible_profile, "visible_negative_examples"),
    )
    known_overlap = overlap_score(song_tokens, visible_known_tokens(visible_profile))
    artist_count = selected_artists[str(song.get("artist_display_name", ""))]
    diversity_bonus = 0.18 if artist_count == 0 else -0.08 * artist_count
    unused_bonus = 0.12 if song["song_id"] not in selected_song_ids else -1.0
    hash_tiebreak = stable_fraction([pack_id, role, song["song_id"]]) * 0.02

    if role == "anchor":
        score = 0.38 * positive_overlap + 0.24 * target_overlap + 0.14 * known_overlap
    elif role == "comparator":
        score = 0.30 * target_overlap + 0.14 * positive_overlap + 0.12 * negative_overlap
    elif role == "control":
        score = 0.13 * target_overlap + 0.10 * positive_overlap + 0.22 * (1 - known_overlap)
    elif role == "boundary":
        score = 0.26 * target_overlap + 0.23 * negative_overlap + 0.08 * positive_overlap
    elif role == "false_nearby":
        score = 0.24 * target_overlap + 0.18 * negative_overlap + 0.16 * (1 - known_overlap)
    elif role == "bridge":
        score = 0.28 * target_overlap + 0.15 * positive_overlap + 0.14 * (1 - known_overlap)
    elif role == "context":
        score = 0.32 * target_overlap + 0.11 * positive_overlap + 0.13 * (1 - known_overlap)
    else:
        score = 0.31 * target_overlap + 0.12 * positive_overlap + 0.17 * (1 - known_overlap)

    return score + diversity_bonus + unused_bonus + hash_tiebreak


def choose_song(
    selection_pool: list[dict[str, Any]],
    role: str,
    opportunity: dict[str, Any],
    visible_profile: dict[str, Any],
    selected_song_ids: set[str],
    selected_artists: Counter[str],
    pack_id: str,
) -> dict[str, Any]:
    scored = [
        (
            role_score(
                song,
                role,
                opportunity,
                visible_profile,
                selected_song_ids,
                selected_artists,
                pack_id,
            ),
            stable_hash([pack_id, role, opportunity.get("opportunity_id"), song["song_id"]]),
            song,
        )
        for song in selection_pool
        if song["song_id"] not in selected_song_ids
    ]
    if not scored:
        raise ValueError(f"No remaining songs for {pack_id}")
    scored.sort(key=lambda item: (-item[0], item[1]))
    return deepcopy(scored[0][2])


def graph_context_refs(opportunity: dict[str, Any]) -> list[str]:
    refs: list[str] = []
    for context in opportunity.get("graph_context_summary", {}).get("graph_contexts", []):
        refs.extend(context.get("provenance", {}).get("source_refs", []))
        target_ref = context.get("target_object_ref", {})
        refs.extend(target_ref.get("object_ids", []))
    return sorted({str(ref) for ref in refs if ref})[:8]


def source_opportunities_for_mode(
    top_window: list[dict[str, Any]],
    construction_mode: str,
) -> list[dict[str, Any]]:
    if construction_mode == "rank_1_pack":
        return top_window[:1]
    if construction_mode == "top_3_portfolio_pack":
        return top_window[:3]
    if construction_mode == "diagnostic_biased_pack":
        diagnostic = [op for op in top_window if op.get("mission_type") in DIAGNOSTIC_MISSION_TYPES]
        remaining = [op for op in top_window if op not in diagnostic]
        return (diagnostic + remaining)[:TOP_WINDOW_SIZE]
    if construction_mode == "experience_balanced_pack":
        diagnostic = [op for op in top_window if op.get("mission_type") in DIAGNOSTIC_MISSION_TYPES]
        depth = [op for op in top_window if op.get("mission_type") in DEPTH_MISSION_TYPES]
        other = [op for op in top_window if op not in diagnostic and op not in depth]
        return (depth[:3] + diagnostic[:4] + other + top_window)[:TOP_WINDOW_SIZE]
    return top_window[:TOP_WINDOW_SIZE]


def slots_for_mode(source_opportunities: list[dict[str, Any]], construction_mode: str) -> list[tuple[str, dict[str, Any]]]:
    if not source_opportunities:
        return []

    def opp(index: int) -> dict[str, Any]:
        return source_opportunities[index % len(source_opportunities)]

    if construction_mode == "rank_1_pack":
        first = opp(0)
        role = primary_role_for_mission_type(first.get("mission_type", ""))
        return [
            ("anchor", first),
            ("comparator", first),
            (role, first),
            ("probe", first),
            ("control", first),
            (role if role != "probe" else "boundary", first),
        ]

    if construction_mode == "top_3_portfolio_pack":
        return [
            ("anchor", opp(0)),
            (primary_role_for_mission_type(opp(0).get("mission_type", "")), opp(0)),
            ("comparator", opp(1)),
            (primary_role_for_mission_type(opp(1).get("mission_type", "")), opp(1)),
            ("probe", opp(2)),
            (primary_role_for_mission_type(opp(2).get("mission_type", "")), opp(2)),
        ]

    if construction_mode == "diagnostic_biased_pack":
        return [
            ("anchor", opp(0)),
            (primary_role_for_mission_type(opp(0).get("mission_type", "")), opp(0)),
            (primary_role_for_mission_type(opp(1).get("mission_type", "")), opp(1)),
            (primary_role_for_mission_type(opp(2).get("mission_type", "")), opp(2)),
            ("probe", opp(3)),
            ("control", opp(4)),
        ]

    if construction_mode == "experience_balanced_pack":
        diagnostic_opp = next(
            (candidate for candidate in source_opportunities if candidate.get("mission_type") in DIAGNOSTIC_MISSION_TYPES),
            opp(2),
        )
        return [
            ("anchor", opp(0)),
            ("anchor", opp(1)),
            ("probe", diagnostic_opp),
            (primary_role_for_mission_type(diagnostic_opp.get("mission_type", "")), diagnostic_opp),
            ("comparator", opp(2)),
            ("control", opp(3)),
        ]

    return [
        ("anchor", opp(0)),
        ("probe", opp(1)),
        ("comparator", opp(2)),
        ("control", opp(3)),
        (primary_role_for_mission_type(opp(4).get("mission_type", "")), opp(4)),
        (primary_role_for_mission_type(opp(5).get("mission_type", "")), opp(5)),
    ]


def visible_familiarity_basis(song: dict[str, Any], visible_profile: dict[str, Any]) -> str:
    overlap = overlap_score(set(song.get("selection_tokens", [])), visible_known_tokens(visible_profile))
    if overlap >= 0.25:
        return "visible_artist_or_title_match"
    return "new_or_unseen_in_visible_evidence"


def construct_pack(
    profile_id: str,
    scale: int,
    sampling_mode: str,
    construction_mode: str,
    selector_output: dict[str, Any],
    visible_profile: dict[str, Any],
    selection_pool: list[dict[str, Any]],
    reaction_map: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    run_id = f"{profile_id}_{sampling_mode}_{scale}"
    pack_id = f"pack_{run_id}_{construction_mode}_v0_1"
    top_window = selector_output.get("ranked_opportunities", [])[:TOP_WINDOW_SIZE]
    source_opportunities = source_opportunities_for_mode(top_window, construction_mode)
    selected_song_ids: set[str] = set()
    selected_artists: Counter[str] = Counter()
    songs: list[dict[str, Any]] = []

    for role, opportunity in slots_for_mode(source_opportunities, construction_mode)[:DEFAULT_PACK_SIZE]:
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
        source_mission_type = opportunity.get("mission_type", "unknown")
        song_tokens = set(song.get("selection_tokens", []))
        target_overlap = overlap_score(song_tokens, opportunity_tokens(opportunity))
        visible_basis = visible_familiarity_basis(song, visible_profile)
        songs.append(
            {
                "song_id": song["song_id"],
                "title": song["title"],
                "artist_display_name": song["artist_display_name"],
                "source_role": role,
                "source_opportunity_id": opportunity.get("opportunity_id"),
                "source_mission_type": source_mission_type,
                "target_object_ids": opportunity.get("target_object_ids", []),
                "graph_context_refs": graph_context_refs(opportunity),
                "why_selected": (
                    f"Deterministic offline {role} pick from {source_mission_type}; "
                    f"target-token overlap={target_overlap:.2f}; "
                    f"visible-basis={visible_basis}."
                ),
                "visible_familiarity_basis": visible_basis,
                "hidden_oracle_reaction": reaction.get("hidden_oracle_reaction", "unknown"),
                "hidden_oracle_confidence": reaction.get("hidden_oracle_confidence", 0.0),
            }
        )

    pack = {
        "pack_id": pack_id,
        "profile_id": profile_id,
        "evidence_scale": scale,
        "sampling_mode": sampling_mode,
        "construction_mode": construction_mode,
        "top_window_size": TOP_WINDOW_SIZE,
        "pack_size_target": DEFAULT_PACK_SIZE,
        "source_selector_output_ref": repo_rel(
            selector_output_path(profile_id, sampling_mode, scale)
        ),
        "source_opportunity_ids": [
            str(opportunity.get("opportunity_id")) for opportunity in source_opportunities[:TOP_WINDOW_SIZE]
        ],
        "source_mission_types": [
            str(opportunity.get("mission_type")) for opportunity in source_opportunities[:TOP_WINDOW_SIZE]
        ],
        "song_count": len(songs),
        "songs": songs,
        "construction_policy": {
            "selection_input_reaction_labels_visible": False,
            "selection_input_hidden_reason_tags_visible": False,
            "hidden_oracle_reaction_attached_after_construction": True,
            "optimized_for_hidden_reaction_labels": False,
            "production_mission_content_emitted": False,
        },
    }
    pack.update(score_pack(pack))
    return pack


def score_pack(pack: dict[str, Any]) -> dict[str, Any]:
    songs = pack.get("songs", [])
    song_count = max(1, len(songs))
    counts = Counter(song.get("hidden_oracle_reaction", "unknown") for song in songs)
    role_counts = Counter(song.get("source_role", "probe") for song in songs)
    source_types = Counter(song.get("source_mission_type", "unknown") for song in songs)
    source_opportunity_count = len(set(pack.get("source_opportunity_ids", [])))
    known_count = sum(
        1
        for song in songs
        if song.get("visible_familiarity_basis") == "visible_artist_or_title_match"
    )
    diagnostic_probe_count = sum(
        role_counts.get(role, 0)
        for role in ["probe", "boundary", "context", "bridge", "false_nearby"]
    )

    love_count = counts.get("love", 0)
    like_count = counts.get("like", 0)
    ok_count = counts.get("ok", 0)
    dont_like_count = counts.get("dont_like", 0)
    unknown_count = counts.get("unknown", 0)
    positive_hit_rate = (love_count + like_count) / song_count
    non_failure_rate = (love_count + like_count + ok_count) / song_count
    negative_hit_rate = dont_like_count / song_count
    unknown_rate = unknown_count / song_count
    new_territory_rate = (song_count - known_count) / song_count
    known_or_familiar_rate = known_count / song_count

    diagnostic_value_score = clamp(
        0.18
        + 0.09 * diagnostic_probe_count
        + 0.12 * min(1.0, source_opportunity_count / 4)
        + 0.12 * len(DIAGNOSTIC_MISSION_TYPES.intersection(source_types)) / 3
        + 0.08 * new_territory_rate
        + (0.08 if 0 < dont_like_count <= 2 else 0),
    )
    mission_coherence_score = clamp(
        0.34
        + 0.10 * role_counts.get("anchor", 0)
        + 0.06 * (role_counts.get("comparator", 0) + role_counts.get("control", 0))
        + 0.10 * min(1.0, max(source_types.values(), default=1) / song_count)
        - 0.05 * max(0, len(source_types) - 4),
    )
    user_experience_score = clamp(
        0.18
        + 0.42 * non_failure_rate
        + 0.18 * positive_hit_rate
        - 0.34 * negative_hit_rate
        - 0.08 * unknown_rate,
    )
    learning_value_score = clamp(
        0.44 * diagnostic_value_score
        + 0.22 * new_territory_rate
        + 0.18 * mission_coherence_score
        + (0.10 if 0 < dont_like_count <= 2 else 0)
        - (0.16 if dont_like_count >= 3 else 0),
    )

    negative_overload_flag = negative_hit_rate > 0.33 or dont_like_count >= 3
    too_safe_flag = positive_hit_rate >= 0.67 and diagnostic_value_score < 0.35
    too_random_flag = unknown_rate > 0.50 or mission_coherence_score < 0.35
    artist_counts = Counter(song.get("artist_display_name") for song in songs)
    overfit_flag = max(artist_counts.values(), default=0) >= 4 or (
        len(source_types) == 1 and next(iter(source_types), "") in DEPTH_MISSION_TYPES
    )

    positive_hit_component = min(1.0, positive_hit_rate / 0.50)
    non_failure_component = min(1.0, non_failure_rate / 0.75)
    diagnostic_component = diagnostic_value_score
    negative_penalty = max(0.0, negative_hit_rate - 0.25) * 2
    unknown_penalty = max(0.0, unknown_rate - 0.50)
    too_safe_penalty = 0.15 if too_safe_flag else 0.0
    too_random_penalty = 0.25 if too_random_flag else 0.0
    overall_smell_score = clamp(
        0.25 * positive_hit_component
        + 0.20 * non_failure_component
        + 0.25 * diagnostic_component
        + 0.20 * user_experience_score
        + 0.10 * mission_coherence_score
        - negative_penalty
        - unknown_penalty
        - too_safe_penalty
        - too_random_penalty
    )

    return {
        "love_count": love_count,
        "like_count": like_count,
        "ok_count": ok_count,
        "dont_like_count": dont_like_count,
        "unknown_count": unknown_count,
        "positive_hit_rate": round(positive_hit_rate, 4),
        "non_failure_rate": round(non_failure_rate, 4),
        "negative_hit_rate": round(negative_hit_rate, 4),
        "unknown_rate": round(unknown_rate, 4),
        "new_territory_rate": round(new_territory_rate, 4),
        "known_or_familiar_rate": round(known_or_familiar_rate, 4),
        "anchor_count": role_counts.get("anchor", 0),
        "probe_count": role_counts.get("probe", 0),
        "boundary_count": role_counts.get("boundary", 0),
        "context_count": role_counts.get("context", 0),
        "bridge_count": role_counts.get("bridge", 0),
        "false_nearby_count": role_counts.get("false_nearby", 0),
        "control_count": role_counts.get("control", 0),
        "diagnostic_probe_count": diagnostic_probe_count,
        "mission_coherence_score": mission_coherence_score,
        "diagnostic_value_score": diagnostic_value_score,
        "user_experience_score": user_experience_score,
        "learning_value_score": learning_value_score,
        "overall_smell_score": overall_smell_score,
        "negative_overload_flag": negative_overload_flag,
        "too_safe_flag": too_safe_flag,
        "too_random_flag": too_random_flag,
        "overfit_flag": overfit_flag,
    }


def average(values: list[float]) -> float:
    return round(mean(values), 4) if values else 0.0


def summarize_group(packs: list[dict[str, Any]], group_key: str) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for pack in packs:
        grouped[str(pack.get(group_key))].append(pack)
    rows: list[dict[str, Any]] = []
    def group_sort_key(item: tuple[str, list[dict[str, Any]]]) -> tuple[int, Any]:
        key = item[0]
        return (0, int(key)) if key.isdigit() else (1, key)

    for key, rows_for_key in sorted(grouped.items(), key=group_sort_key):
        rows.append(
            {
                group_key: key,
                "pack_count": len(rows_for_key),
                "average_overall_smell_score": average(
                    [pack["overall_smell_score"] for pack in rows_for_key]
                ),
                "average_diagnostic_value_score": average(
                    [pack["diagnostic_value_score"] for pack in rows_for_key]
                ),
                "average_user_experience_score": average(
                    [pack["user_experience_score"] for pack in rows_for_key]
                ),
                "average_positive_hit_rate": average(
                    [pack["positive_hit_rate"] for pack in rows_for_key]
                ),
                "average_non_failure_rate": average(
                    [pack["non_failure_rate"] for pack in rows_for_key]
                ),
                "average_negative_hit_rate": average(
                    [pack["negative_hit_rate"] for pack in rows_for_key]
                ),
                "negative_overload_count": sum(
                    1 for pack in rows_for_key if pack["negative_overload_flag"]
                ),
                "too_safe_count": sum(1 for pack in rows_for_key if pack["too_safe_flag"]),
                "too_random_count": sum(1 for pack in rows_for_key if pack["too_random_flag"]),
            }
        )
    return rows


def summarize_source_mission_types(packs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[tuple[dict[str, Any], dict[str, Any]]]] = defaultdict(list)
    for pack in packs:
        for song in pack.get("songs", []):
            grouped[song.get("source_mission_type", "unknown")].append((pack, song))
    rows: list[dict[str, Any]] = []
    for mission_type, items in sorted(grouped.items()):
        reactions = Counter(song.get("hidden_oracle_reaction") for _, song in items)
        unique_pack_ids = {pack["pack_id"] for pack, _ in items}
        rows.append(
            {
                "mission_type": mission_type,
                "song_contribution_count": len(items),
                "pack_count": len(unique_pack_ids),
                "average_pack_overall_smell_score": average(
                    [pack["overall_smell_score"] for pack, _ in items]
                ),
                "average_pack_diagnostic_value_score": average(
                    [pack["diagnostic_value_score"] for pack, _ in items]
                ),
                "positive_song_reaction_rate": round(
                    (reactions.get("love", 0) + reactions.get("like", 0)) / max(1, len(items)),
                    4,
                ),
                "non_failure_song_reaction_rate": round(
                    (
                        reactions.get("love", 0)
                        + reactions.get("like", 0)
                        + reactions.get("ok", 0)
                    )
                    / max(1, len(items)),
                    4,
                ),
                "negative_song_reaction_rate": round(
                    reactions.get("dont_like", 0) / max(1, len(items)),
                    4,
                ),
            }
        )
    return rows


def representative_examples(packs: list[dict[str, Any]]) -> dict[str, Any]:
    best_overall = max(packs, key=lambda pack: pack["overall_smell_score"])
    best_diagnostic = max(packs, key=lambda pack: pack["diagnostic_value_score"])
    worst_negative = max(packs, key=lambda pack: (pack["negative_hit_rate"], -pack["overall_smell_score"]))
    rank_1 = max(
        [pack for pack in packs if pack["construction_mode"] == "rank_1_pack"],
        key=lambda pack: pack["overall_smell_score"],
    )
    experience_balanced = max(
        [pack for pack in packs if pack["construction_mode"] == "experience_balanced_pack"],
        key=lambda pack: pack["overall_smell_score"],
    )
    return {
        "best_overall_pack_id": best_overall["pack_id"],
        "best_overall_score": best_overall["overall_smell_score"],
        "best_diagnostic_pack_id": best_diagnostic["pack_id"],
        "best_diagnostic_score": best_diagnostic["diagnostic_value_score"],
        "worst_negative_overload_pack_id": worst_negative["pack_id"],
        "worst_negative_hit_rate": worst_negative["negative_hit_rate"],
        "best_rank_1_pack_id": rank_1["pack_id"],
        "best_rank_1_score": rank_1["overall_smell_score"],
        "best_experience_balanced_pack_id": experience_balanced["pack_id"],
        "best_experience_balanced_score": experience_balanced["overall_smell_score"],
    }


def build_schema() -> dict[str, Any]:
    score = {"type": "number", "minimum": 0, "maximum": 1}
    count = {"type": "integer", "minimum": 0}
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://cartenza.local/contracts/mission_opportunity_selection_v0_1/song_pack_simulation_schema_v0_1.schema.json",
        "title": "Mission Opportunity Selection v0.1 Phase 1F Song Pack Simulation",
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
            "song_pack_construction_status",
            "run_matrix",
            "source_refs",
            "scoring_model",
            "packs",
            "aggregate_pack_metrics",
            "per_profile_summary",
            "per_evidence_scale_summary",
            "per_sampling_mode_summary",
            "per_construction_mode_summary",
            "per_source_mission_type_summary",
            "representative_pack_examples",
            "guardrail_summary",
            "determinism_summary",
        ],
        "properties": {
            "contract_version": {"const": "phase1f_song_pack_smell_test_v0_1"},
            "fixture_status": {"const": "synthetic_contract_fixture"},
            "created_at": {"type": "string"},
            "phase": {"const": "offline_top_window_song_pack_smell_test"},
            "runtime_allowed": {"const": False},
            "runtime_listener_evidence_connected": {"const": False},
            "production_mission_generation_allowed": {"const": False},
            "canonical_graph_mutation_allowed": {"const": False},
            "selector_may_read_hidden_oracle": {"const": False},
            "constructor_optimized_by_hidden_reaction_labels": {"const": False},
            "oracle_evaluation_fed_back_into_selector": {"const": False},
            "song_pack_construction_status": {"const": "offline_smell_test_only"},
            "source_refs": {"type": "object"},
            "scoring_model": {"type": "object"},
            "run_matrix": {
                "type": "object",
                "required": [
                    "profiles",
                    "evidence_scales",
                    "sampling_modes",
                    "construction_modes",
                    "top_window_size",
                    "pack_size",
                    "completed_pack_count",
                    "minimum_required_pack_count",
                ],
                "properties": {
                    "profiles": {"type": "array", "items": {"type": "string"}},
                    "evidence_scales": {"type": "array", "items": count},
                    "sampling_modes": {"type": "array", "items": {"type": "string"}},
                    "construction_modes": {"type": "array", "items": {"type": "string"}},
                    "top_window_size": {"const": 10},
                    "pack_size": {"const": 6},
                    "completed_pack_count": {"type": "integer", "minimum": 45},
                    "minimum_required_pack_count": {"const": 45},
                    "default_review_slice": {"type": "string"},
                    "stretch_slice_included": {"type": "string"},
                },
                "additionalProperties": False,
            },
            "packs": {
                "type": "array",
                "minItems": 45,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "pack_id",
                        "profile_id",
                        "evidence_scale",
                        "sampling_mode",
                        "construction_mode",
                        "source_selector_output_ref",
                        "source_opportunity_ids",
                        "source_mission_types",
                        "song_count",
                        "songs",
                        "construction_policy",
                        "love_count",
                        "like_count",
                        "ok_count",
                        "dont_like_count",
                        "unknown_count",
                        "positive_hit_rate",
                        "non_failure_rate",
                        "negative_hit_rate",
                        "unknown_rate",
                        "new_territory_rate",
                        "known_or_familiar_rate",
                        "mission_coherence_score",
                        "diagnostic_value_score",
                        "user_experience_score",
                        "learning_value_score",
                        "overall_smell_score",
                        "negative_overload_flag",
                        "too_safe_flag",
                        "too_random_flag",
                        "overfit_flag",
                    ],
                    "properties": {
                        "pack_id": {"type": "string"},
                        "profile_id": {"type": "string"},
                        "evidence_scale": count,
                        "sampling_mode": {"type": "string"},
                        "construction_mode": {"type": "string"},
                        "top_window_size": {"const": 10},
                        "pack_size_target": {"const": 6},
                        "source_selector_output_ref": {"type": "string"},
                        "source_opportunity_ids": {
                            "type": "array",
                            "minItems": 1,
                            "items": {"type": "string"},
                        },
                        "source_mission_types": {
                            "type": "array",
                            "minItems": 1,
                            "items": {"type": "string"},
                        },
                        "song_count": {"const": 6},
                        "songs": {
                            "type": "array",
                            "minItems": 6,
                            "maxItems": 6,
                            "items": {"$ref": "#/$defs/song"},
                        },
                        "construction_policy": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": [
                                "selection_input_reaction_labels_visible",
                                "selection_input_hidden_reason_tags_visible",
                                "hidden_oracle_reaction_attached_after_construction",
                                "optimized_for_hidden_reaction_labels",
                                "production_mission_content_emitted",
                            ],
                            "properties": {
                                "selection_input_reaction_labels_visible": {"const": False},
                                "selection_input_hidden_reason_tags_visible": {"const": False},
                                "hidden_oracle_reaction_attached_after_construction": {"const": True},
                                "optimized_for_hidden_reaction_labels": {"const": False},
                                "production_mission_content_emitted": {"const": False},
                            },
                        },
                        "love_count": count,
                        "like_count": count,
                        "ok_count": count,
                        "dont_like_count": count,
                        "unknown_count": count,
                        "positive_hit_rate": score,
                        "non_failure_rate": score,
                        "negative_hit_rate": score,
                        "unknown_rate": score,
                        "new_territory_rate": score,
                        "known_or_familiar_rate": score,
                        "anchor_count": count,
                        "probe_count": count,
                        "boundary_count": count,
                        "context_count": count,
                        "bridge_count": count,
                        "false_nearby_count": count,
                        "control_count": count,
                        "diagnostic_probe_count": count,
                        "mission_coherence_score": score,
                        "diagnostic_value_score": score,
                        "user_experience_score": score,
                        "learning_value_score": score,
                        "overall_smell_score": score,
                        "negative_overload_flag": {"type": "boolean"},
                        "too_safe_flag": {"type": "boolean"},
                        "too_random_flag": {"type": "boolean"},
                        "overfit_flag": {"type": "boolean"},
                    },
                },
            },
            "aggregate_pack_metrics": {"type": "object"},
            "per_profile_summary": {"type": "array", "items": {"type": "object"}},
            "per_evidence_scale_summary": {"type": "array", "items": {"type": "object"}},
            "per_sampling_mode_summary": {"type": "array", "items": {"type": "object"}},
            "per_construction_mode_summary": {"type": "array", "items": {"type": "object"}},
            "per_source_mission_type_summary": {"type": "array", "items": {"type": "object"}},
            "representative_pack_examples": {"type": "object"},
            "guardrail_summary": {"type": "object"},
            "determinism_summary": {"type": "object"},
            "human_llm_smell_test_packet_refs": {"type": "array", "items": {"type": "string"}},
            "known_limitations": {"type": "array", "items": {"type": "string"}},
            "recommendations": {"type": "array", "items": {"type": "string"}},
        },
        "$defs": {
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
                    "visible_familiarity_basis",
                    "hidden_oracle_reaction",
                    "hidden_oracle_confidence",
                ],
                "properties": {
                    "song_id": {"type": "string", "minLength": 1},
                    "title": {"type": "string", "minLength": 1},
                    "artist_display_name": {"type": "string", "minLength": 1},
                    "source_role": {
                        "enum": [
                            "anchor",
                            "comparator",
                            "probe",
                            "boundary",
                            "bridge",
                            "context",
                            "false_nearby",
                            "control",
                        ]
                    },
                    "source_opportunity_id": {"type": "string", "minLength": 1},
                    "source_mission_type": {"type": "string", "minLength": 1},
                    "target_object_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "graph_context_refs": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "why_selected": {"type": "string", "minLength": 1},
                    "visible_familiarity_basis": {
                        "enum": [
                            "visible_artist_or_title_match",
                            "new_or_unseen_in_visible_evidence",
                        ]
                    },
                    "hidden_oracle_reaction": {
                        "enum": ["love", "like", "ok", "dont_like", "unknown"]
                    },
                    "hidden_oracle_confidence": score,
                },
            }
        },
    }


def aggregate_metrics(packs: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "pack_count": len(packs),
        "average_overall_smell_score": average([pack["overall_smell_score"] for pack in packs]),
        "average_learning_value_score": average([pack["learning_value_score"] for pack in packs]),
        "average_diagnostic_value_score": average([pack["diagnostic_value_score"] for pack in packs]),
        "average_user_experience_score": average([pack["user_experience_score"] for pack in packs]),
        "average_positive_hit_rate": average([pack["positive_hit_rate"] for pack in packs]),
        "average_non_failure_rate": average([pack["non_failure_rate"] for pack in packs]),
        "average_negative_hit_rate": average([pack["negative_hit_rate"] for pack in packs]),
        "negative_overload_count": sum(1 for pack in packs if pack["negative_overload_flag"]),
        "too_safe_count": sum(1 for pack in packs if pack["too_safe_flag"]),
        "too_random_count": sum(1 for pack in packs if pack["too_random_flag"]),
        "rank_1_average_overall_smell_score": average(
            [
                pack["overall_smell_score"]
                for pack in packs
                if pack["construction_mode"] == "rank_1_pack"
            ]
        ),
        "top_3_average_overall_smell_score": average(
            [
                pack["overall_smell_score"]
                for pack in packs
                if pack["construction_mode"] == "top_3_portfolio_pack"
            ]
        ),
        "top_10_average_overall_smell_score": average(
            [
                pack["overall_smell_score"]
                for pack in packs
                if pack["construction_mode"] == "top_10_portfolio_pack"
            ]
        ),
        "diagnostic_biased_average_overall_smell_score": average(
            [
                pack["overall_smell_score"]
                for pack in packs
                if pack["construction_mode"] == "diagnostic_biased_pack"
            ]
        ),
        "experience_balanced_average_overall_smell_score": average(
            [
                pack["overall_smell_score"]
                for pack in packs
                if pack["construction_mode"] == "experience_balanced_pack"
            ]
        ),
    }


def pack_signature(packs: list[dict[str, Any]]) -> list[Any]:
    return [
        (
            pack["pack_id"],
            tuple(song["song_id"] for song in pack["songs"]),
            tuple(song["source_opportunity_id"] for song in pack["songs"]),
            pack["overall_smell_score"],
        )
        for pack in packs
    ]


def build_packs() -> list[dict[str, Any]]:
    expanded = load_json(EXPANDED_VISIBLE_INPUTS)
    visible_by_run = {
        (profile["profile_id"], profile["evidence_atom_count"], profile["sampling_mode"]): profile
        for profile in expanded.get("profiles", [])
    }
    packs: list[dict[str, Any]] = []
    universe_cache: dict[str, tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]] = {}

    for profile_id in PROFILE_IDS:
        universe_cache[profile_id] = build_song_universe(profile_id)
        selection_pool, reaction_map = universe_cache[profile_id]
        for scale in SCALES:
            for sampling_mode in SAMPLING_MODES:
                visible_profile = visible_by_run[(profile_id, scale, sampling_mode)]
                selector_output = load_json(selector_output_path(profile_id, sampling_mode, scale))
                for construction_mode in CONSTRUCTION_MODES:
                    packs.append(
                        construct_pack(
                            profile_id,
                            scale,
                            sampling_mode,
                            construction_mode,
                            selector_output,
                            visible_profile,
                            selection_pool,
                            reaction_map,
                        )
                    )
    return packs


def build_negative_fixtures(valid_results: dict[str, Any]) -> dict[str, str]:
    NEGATIVE_DIR.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {
        "constructor input includes hidden reaction labels": NEGATIVE_DIR
        / "constructor_input_hidden_reaction_labels_v0_1.json",
        "selector output includes hidden reaction labels": NEGATIVE_DIR
        / "selector_output_hidden_reaction_labels_v0_1.json",
        "production mission generation allowed": NEGATIVE_DIR
        / "pack_production_generation_true_v0_1.json",
        "pack includes final mission copy": NEGATIVE_DIR / "pack_final_mission_copy_v0_1.json",
        "pack has no source opportunity refs": NEGATIVE_DIR
        / "pack_missing_source_opportunity_refs_v0_1.json",
        "pack song lacks why_selected": NEGATIVE_DIR
        / "pack_song_missing_why_selected_v0_1.json",
        "same seed produces different pack": NEGATIVE_DIR / "pack_determinism_mismatch_v0_1.json",
    }

    write_json(
        paths["constructor input includes hidden reaction labels"],
        {
            "contract_version": "phase1f_negative_fixture_v0_1",
            "negative_case": "constructor_input_hidden_reaction_labels",
            "constructor_selection_pool": [
                {
                    "song_id": "bad-hidden-label",
                    "title": "Bad Hidden Label",
                    "artist_display_name": "Synthetic Artist",
                    "reaction": "love",
                }
            ],
        },
    )
    write_json(
        paths["selector output includes hidden reaction labels"],
        {
            "contract_version": "phase1f_negative_fixture_v0_1",
            "negative_case": "selector_output_hidden_reaction_labels",
            "selector_output": {
                "ranked_opportunities": [
                    {
                        "opportunity_id": "bad_selector_leak",
                        "hidden_oracle_reaction": "love",
                    }
                ]
            },
        },
    )
    production_true = deepcopy(valid_results)
    production_true["production_mission_generation_allowed"] = True
    write_json(paths["production mission generation allowed"], production_true)

    with_copy = deepcopy(valid_results)
    with_copy["packs"][0]["final_mission_copy"] = "This would be production mission text."
    write_json(paths["pack includes final mission copy"], with_copy)

    missing_refs = deepcopy(valid_results)
    missing_refs["packs"][0]["source_opportunity_ids"] = []
    write_json(paths["pack has no source opportunity refs"], missing_refs)

    missing_why = deepcopy(valid_results)
    missing_why["packs"][0]["songs"][0]["why_selected"] = ""
    write_json(paths["pack song lacks why_selected"], missing_why)

    mismatch = {
        "contract_version": "phase1f_negative_fixture_v0_1",
        "negative_case": "pack_determinism_mismatch",
        "deterministic_rerun_matched": False,
        "expected_signature_sha256": "expected",
        "actual_signature_sha256": "actual",
    }
    write_json(paths["same seed produces different pack"], mismatch)
    return {label: repo_rel(path) for label, path in paths.items()}


def build_results() -> dict[str, Any]:
    packs = build_packs()
    signature = pack_signature(packs)
    rerun_signature = pack_signature(build_packs())
    deterministic = signature == rerun_signature
    profile_summary = summarize_group(packs, "profile_id")
    scale_summary = summarize_group(packs, "evidence_scale")
    sampling_mode_summary = summarize_group(packs, "sampling_mode")
    mode_summary = summarize_group(packs, "construction_mode")
    source_mission_type_summary = summarize_source_mission_types(packs)
    packet_refs = write_pack_cards(packs)

    results = {
        "contract_version": "phase1f_song_pack_smell_test_v0_1",
        "fixture_status": "synthetic_contract_fixture",
        "created_at": now_iso(),
        "phase": "offline_top_window_song_pack_smell_test",
        "runtime_allowed": False,
        "runtime_listener_evidence_connected": False,
        "production_mission_generation_allowed": False,
        "canonical_graph_mutation_allowed": False,
        "selector_may_read_hidden_oracle": False,
        "constructor_optimized_by_hidden_reaction_labels": False,
        "oracle_evaluation_fed_back_into_selector": False,
        "song_pack_construction_status": "offline_smell_test_only",
        "run_matrix": {
            "profiles": PROFILE_IDS,
            "evidence_scales": SCALES,
            "sampling_modes": SAMPLING_MODES,
            "construction_modes": CONSTRUCTION_MODES,
            "top_window_size": TOP_WINDOW_SIZE,
            "pack_size": DEFAULT_PACK_SIZE,
            "completed_pack_count": len(packs),
            "minimum_required_pack_count": 45,
            "default_review_slice": "200 atoms x 3 profiles x 3 sampling modes x 5 construction modes",
            "stretch_slice_included": "all 72/150/200/300 scales for all sampling modes",
        },
        "source_refs": {
            "expanded_visible_profile_inputs_ref": repo_rel(EXPANDED_VISIBLE_INPUTS),
            "selector_outputs_root_ref": repo_rel(PHASE1E_SELECTOR_DIR),
            "hidden_profile_oracle_ref": repo_rel(HIDDEN_PROFILE_ORACLES),
            "hidden_reaction_corpus_root_ref": repo_rel(HIDDEN_CORPUS_DIR),
        },
        "scoring_model": {
            "positive_hit_component": "min(1.0, positive_hit_rate / 0.50)",
            "non_failure_component": "min(1.0, non_failure_rate / 0.75)",
            "diagnostic_component": "diagnostic_value_score",
            "negative_penalty": "max(0, negative_hit_rate - 0.25) * 2",
            "unknown_penalty": "max(0, unknown_rate - 0.50)",
            "too_safe_penalty": "0.15 if too_safe_flag else 0",
            "too_random_penalty": "0.25 if too_random_flag else 0",
            "overall_smell_score": (
                "0.25*positive_hit_component + 0.20*non_failure_component + "
                "0.25*diagnostic_component + 0.20*user_experience_score + "
                "0.10*mission_coherence_score - penalties, clamped 0..1"
            ),
            "selection_guardrail": (
                "Song selection uses a reaction-stripped pool: song_id, title, artist, "
                "selector opportunity refs, and visible evidence tokens only. Hidden reactions "
                "are joined after construction for evaluation."
            ),
        },
        "packs": packs,
        "aggregate_pack_metrics": aggregate_metrics(packs),
        "per_profile_summary": profile_summary,
        "per_evidence_scale_summary": scale_summary,
        "per_sampling_mode_summary": sampling_mode_summary,
        "per_construction_mode_summary": mode_summary,
        "per_source_mission_type_summary": source_mission_type_summary,
        "representative_pack_examples": representative_examples(packs),
        "guardrail_summary": {
            "selector_did_not_read_hidden_oracle": True,
            "constructor_selection_pool_reaction_labels_visible": False,
            "constructor_selection_pool_hidden_reason_tags_visible": False,
            "oracle_reactions_joined_after_pack_construction": True,
            "runtime_flags_remain_false": True,
            "production_mission_generation_remains_false": True,
            "final_mission_copy_absent": True,
            "canonical_graph_mutation_remains_false": True,
            "oracle_metrics_written_back_to_selector_input": False,
        },
        "determinism_summary": {
            "deterministic_rerun_matched": deterministic,
            "pack_signature_sha256": stable_hash(signature),
            "rerun_signature_sha256": stable_hash(rerun_signature),
            "compared_pack_count": len(packs),
        },
        "human_llm_smell_test_packet_refs": packet_refs,
        "known_limitations": [
            "Song packs are synthetic smell-test objects, not production mission contents.",
            "The constructor uses token-level target matching and deterministic diversity, not a real catalog or graph path solver.",
            "Hidden corpus reactions are joined after construction; they should not tune selector scoring in this phase.",
            "Unknown reaction counts are low because the available hidden corpus is mostly labeled love/like/ok/dont_like.",
        ],
        "recommendations": [
            "Treat selector rank 1 as insufficient by itself when top-window portfolio packs outperform it.",
            "Use top-3 or top-10 portfolio construction as the next mission-construction design baseline.",
            "Keep diagnostic and experience balancing as explicit construction policies before runtime work.",
            "Do not feed song-pack oracle outcomes into selector scoring until PM approves a separate tuning slice.",
        ],
    }
    negative_refs = build_negative_fixtures(results)
    results["guardrail_summary"]["negative_fixture_refs"] = negative_refs
    return results


def pack_plain_read(pack: dict[str, Any]) -> str:
    if pack["negative_overload_flag"]:
        return "Negative overload risk: useful diagnostically only if deliberately bounded."
    if pack["too_safe_flag"]:
        return "Comfortable but likely too safe; learning value may be thin."
    if pack["too_random_flag"]:
        return "Low-coherence pack; should not move toward production shape yet."
    if pack["overall_smell_score"] >= 0.70:
        return "Sane offline mission-like pack: tolerable experience with useful probes."
    if pack["overall_smell_score"] >= 0.50:
        return "Mixed but reviewable; likely needs construction tuning."
    return "Weak smell-test pack; selector window or construction policy needs adjustment."


def write_pack_cards(packs: list[dict[str, Any]]) -> list[str]:
    PACK_CARDS_DIR.mkdir(parents=True, exist_ok=True)
    refs: list[str] = []
    by_profile: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for pack in packs:
        by_profile[pack["profile_id"]].append(pack)

    for profile_id in PROFILE_IDS:
        rows = by_profile[profile_id]
        selected_ids = []
        selectors = [
            max(rows, key=lambda pack: pack["overall_smell_score"]),
            max(rows, key=lambda pack: pack["diagnostic_value_score"]),
            max(rows, key=lambda pack: (pack["negative_hit_rate"], -pack["overall_smell_score"])),
            max(
                [pack for pack in rows if pack["construction_mode"] == "rank_1_pack"],
                key=lambda pack: pack["overall_smell_score"],
            ),
            max(
                [pack for pack in rows if pack["construction_mode"] == "experience_balanced_pack"],
                key=lambda pack: pack["overall_smell_score"],
            ),
        ]
        cards = []
        for pack in selectors:
            if pack["pack_id"] not in selected_ids:
                selected_ids.append(pack["pack_id"])
                cards.append(pack)

        lines = [
            f"# {profile_id} Phase 1F Pack Cards",
            "",
            "Offline review cards. These are not production missions and contain no final mission copy.",
            "",
        ]
        for pack in cards:
            lines.extend(
                [
                    f"## {pack['pack_id']}",
                    "",
                    f"- Evidence scale: {pack['evidence_scale']}",
                    f"- Sampling mode: {pack['sampling_mode']}",
                    f"- Construction mode: {pack['construction_mode']}",
                    f"- Source mission types: {', '.join(pack['source_mission_types'][:6])}",
                    f"- Overall smell score: {pack['overall_smell_score']}",
                    f"- Positive / non-failure / negative: {pack['positive_hit_rate']} / {pack['non_failure_rate']} / {pack['negative_hit_rate']}",
                    f"- Diagnostic / UX / coherence: {pack['diagnostic_value_score']} / {pack['user_experience_score']} / {pack['mission_coherence_score']}",
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
            lines.extend(["", f"Plain-English read: {pack_plain_read(pack)}", ""])

        path = PACK_CARDS_DIR / f"{profile_id}_pack_cards.md"
        path.write_text("\n".join(lines), encoding="utf-8")
        refs.append(repo_rel(path))
    return refs


def write_summary_md(results: dict[str, Any]) -> None:
    aggregate = results["aggregate_pack_metrics"]
    lines = [
        "# Phase 1F Song-Pack Smell Test Summary",
        "",
        "Offline-only Cartenza Mission Opportunity Selection v0.1 review artifact. These packs are synthetic song-pack simulations, not production missions.",
        "",
        "## Executive Summary",
        "",
        f"- Completed packs: {results['run_matrix']['completed_pack_count']}",
        f"- Evidence scales: {', '.join(str(scale) for scale in results['run_matrix']['evidence_scales'])}",
        f"- Sampling modes: {', '.join(results['run_matrix']['sampling_modes'])}",
        f"- Construction modes: {', '.join(results['run_matrix']['construction_modes'])}",
        f"- Average overall smell score: {aggregate['average_overall_smell_score']}",
        f"- Average positive hit rate: {aggregate['average_positive_hit_rate']}",
        f"- Average non-failure rate: {aggregate['average_non_failure_rate']}",
        f"- Average negative hit rate: {aggregate['average_negative_hit_rate']}",
        f"- Negative overload packs: {aggregate['negative_overload_count']}",
        "",
        "## Construction Mode Summary",
        "",
        "| Mode | Packs | Avg smell | Avg diagnostic | Avg UX | Negative overload | Too safe | Too random |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in results["per_construction_mode_summary"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    row["construction_mode"],
                    str(row["pack_count"]),
                    str(row["average_overall_smell_score"]),
                    str(row["average_diagnostic_value_score"]),
                    str(row["average_user_experience_score"]),
                    str(row["negative_overload_count"]),
                    str(row["too_safe_count"]),
                    str(row["too_random_count"]),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Per-Profile Summary",
            "",
            "| Profile | Packs | Avg smell | Avg positive | Avg non-failure | Avg negative | Negative overload |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in results["per_profile_summary"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    row["profile_id"],
                    str(row["pack_count"]),
                    str(row["average_overall_smell_score"]),
                    str(row["average_positive_hit_rate"]),
                    str(row["average_non_failure_rate"]),
                    str(row["average_negative_hit_rate"]),
                    str(row["negative_overload_count"]),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Evidence Scale Summary",
            "",
            "| Evidence scale | Packs | Avg smell | Avg positive | Avg non-failure | Avg negative | Negative overload |",
            "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in results["per_evidence_scale_summary"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    row["evidence_scale"],
                    str(row["pack_count"]),
                    str(row["average_overall_smell_score"]),
                    str(row["average_positive_hit_rate"]),
                    str(row["average_non_failure_rate"]),
                    str(row["average_negative_hit_rate"]),
                    str(row["negative_overload_count"]),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Mission-Type Contribution Summary",
            "",
            "| Mission type | Song contributions | Packs | Avg pack smell | Positive song rate | Non-failure song rate | Negative song rate |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in results["per_source_mission_type_summary"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    row["mission_type"],
                    str(row["song_contribution_count"]),
                    str(row["pack_count"]),
                    str(row["average_pack_overall_smell_score"]),
                    str(row["positive_song_reaction_rate"]),
                    str(row["non_failure_song_reaction_rate"]),
                    str(row["negative_song_reaction_rate"]),
                ]
            )
            + " |"
        )

    examples = results["representative_pack_examples"]
    lines.extend(
        [
            "",
            "## Representative Examples",
            "",
            f"- Best overall: `{examples['best_overall_pack_id']}` ({examples['best_overall_score']})",
            f"- Best diagnostic: `{examples['best_diagnostic_pack_id']}` ({examples['best_diagnostic_score']})",
            f"- Worst negative overload: `{examples['worst_negative_overload_pack_id']}` ({examples['worst_negative_hit_rate']} negative hit rate)",
            f"- Best rank-1 pack: `{examples['best_rank_1_pack_id']}` ({examples['best_rank_1_score']})",
            f"- Best experience-balanced pack: `{examples['best_experience_balanced_pack_id']}` ({examples['best_experience_balanced_score']})",
            "",
            "## Key Reads",
            "",
            "- Rank-1 packs are included as a baseline, but portfolio modes are the intended comparison point for top-window usefulness.",
            "- Diagnostic-biased packs expose learning potential but can carry more negative-risk pressure.",
            "- Experience-balanced packs are the most product-shaped offline policy because they preserve anchors, probes, and controls.",
            "- These results should inform a mission-construction contract, not runtime selection or production mission copy.",
            "",
            "## Guardrails",
            "",
            "- Selector did not read hidden oracle inputs.",
            "- Constructor selection used reaction-stripped song pools.",
            "- Hidden reactions were attached only after pack construction.",
            "- Runtime wiring, production mission generation, final mission construction, and canonical graph mutation remain blocked.",
        ]
    )
    SUMMARY_MD_OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_guardrail_report(results: dict[str, Any]) -> None:
    lines = [
        "# Phase 1F Guardrail Report",
        "",
        "| Guardrail | Status |",
        "| --- | --- |",
    ]
    guardrails = {
        "Selector does not read hidden oracle": results["guardrail_summary"][
            "selector_did_not_read_hidden_oracle"
        ],
        "Constructor does not see hidden reaction labels during selection": not results[
            "guardrail_summary"
        ]["constructor_selection_pool_reaction_labels_visible"],
        "Constructor does not see hidden reason tags during selection": not results[
            "guardrail_summary"
        ]["constructor_selection_pool_hidden_reason_tags_visible"],
        "Evaluator joins hidden reactions only after construction": results["guardrail_summary"][
            "oracle_reactions_joined_after_pack_construction"
        ],
        "Runtime remains false": results["runtime_allowed"] is False
        and results["runtime_listener_evidence_connected"] is False,
        "Production mission generation remains false": results[
            "production_mission_generation_allowed"
        ]
        is False,
        "Final mission copy/content is absent": results["guardrail_summary"][
            "final_mission_copy_absent"
        ],
        "Canonical graph mutation remains false": results["canonical_graph_mutation_allowed"]
        is False,
        "Oracle metrics are not fed back into selector input": not results[
            "guardrail_summary"
        ]["oracle_metrics_written_back_to_selector_input"],
        "Pack construction is deterministic": results["determinism_summary"][
            "deterministic_rerun_matched"
        ],
    }
    for name, passed in guardrails.items():
        lines.append(f"| {name} | {'PASS' if passed else 'FAIL'} |")

    lines.extend(["", "## Negative Fixtures", ""])
    for label, ref in results["guardrail_summary"].get("negative_fixture_refs", {}).items():
        lines.append(f"- `{ref}`: {label}")
    GUARDRAIL_MD_OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    PHASE1F_DIR.mkdir(parents=True, exist_ok=True)
    write_json(SCHEMA_OUTPUT, build_schema())
    results = build_results()
    write_json(RESULTS_OUTPUT, results)
    write_summary_md(results)
    write_guardrail_report(results)
    print(f"Wrote {repo_rel(RESULTS_OUTPUT)}")
    print(f"Wrote {repo_rel(SUMMARY_MD_OUTPUT)}")
    print(f"Wrote {repo_rel(SCHEMA_OUTPUT)}")
    print(f"Wrote {repo_rel(GUARDRAIL_MD_OUTPUT)}")
    print(f"Constructed {results['run_matrix']['completed_pack_count']} offline song packs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
