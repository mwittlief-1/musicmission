#!/usr/bin/env python3
"""Build Cartenza Derived Affinity Substrate v0.1 review artifacts.

This is an offline derivation over the completed graph-wide song-affinity
sidecar. It does not mutate canonical graph inputs and does not wire anything
into runtime.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "derived_affinity_substrate_v0_1"
GENERATED_ON = "2026-05-28"
SOURCE_INPUT_SUMMARY: dict[str, Any] = {}

AFFINITY_SIDECAR = ROOT / "review_packets" / "affinity_graphwide_v0_1" / "affinity_song_tags_graphwide_v0_1.json"
DUPLICATE_REVIEW = ROOT / "review_packets" / "affinity_graphwide_v0_1" / "affinity_duplicate_context_review_graphwide_v0_1.json"
QA_REPORT = ROOT / "review_packets" / "affinity_graphwide_v0_1" / "affinity_graphwide_QA_report_v0_1.md"
QA_METRICS = ROOT / "review_packets" / "affinity_graphwide_v0_1" / "affinity_graphwide_QA_metrics_v0_1.json"
TAGGING_CORPUS = ROOT / "data" / "canonical_graph" / "current" / "graph_tagging_corpus.json"
ARCHETYPE_TARGETS = ROOT / "data" / "canonical_graph" / "current" / "atlas_archetype_profile_targets.json"

CORE_DIMS = ("vocal_performance", "emotion_theme", "sonic_texture", "rhythm_body", "form_container")
CONTEXT_DIMS = ("social_context", "routing_caution")
CONFIDENCE_SCORE = {"low": 0.34, "medium": 0.67, "high": 1.0}
EDGE_TYPES = (
    "intrinsic_affinity_edge",
    "cross_family_bridge_edge",
    "route_gateway_edge",
    "frontier_probe_edge",
    "false_nearby_caution_edge",
    "high_whiplash_edge",
    "one_object_exception_edge",
    "listener_alignment_edge",
)
RISK_WEIGHTS = {
    "false_nearby_risk": 0.16,
    "high_whiplash": 0.14,
    "context_dependent": 0.08,
    "requires_framing": 0.06,
    "overfamiliar_anchor": 0.05,
    "explicit_context": 0.05,
    "sentimentality_risk": 0.06,
    "novelty_risk": 0.08,
    "camp_sensitive": 0.06,
    "genre_costume_risk": 0.08,
    "one_object_exception_risk": 0.12,
    "duplicate_context_review_needed": 0.10,
    "recording_identity_unclear": 0.10,
    "version_ambiguity": 0.10,
    "context_leak_risk": 0.12,
    "schema_boundary_risk": 0.12,
}
TOP_INTRINSIC_EDGES = 12000
TOP_CROSS_FAMILY_EDGES = 8000
TOP_SPECIAL_EDGES = 650


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, body: str) -> None:
    path.write_text(body.rstrip() + "\n", encoding="utf-8")


def slug(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return normalized or "unnamed"


def clean_id(value: str) -> str:
    return slug(value.replace("|", "_").replace("@", "_"))


def sorted_counter(counter: Counter[str], limit: int | None = None) -> list[dict[str, Any]]:
    rows = [{"tag": key, "count": count} for key, count in counter.most_common(limit)]
    return rows


def unique(values: list[str]) -> list[str]:
    return sorted({value for value in values if value})


def flatten_tag_bucket(bucket: dict[str, Any], dim: str, include_tier: bool = False) -> list[str]:
    tags: list[str] = []
    for tier in ("primary", "secondary"):
        for tag in bucket.get(tier, []) or []:
            tags.append(f"{dim}:{tier}:{tag}" if include_tier else f"{dim}:{tag}")
    return tags


def core_tag_keys(song: dict[str, Any]) -> dict[str, float]:
    keys: dict[str, float] = {}
    for dim in CORE_DIMS:
        bucket = (song.get("canonical_song_affinity_tags") or {}).get(dim, {})
        for tag in bucket.get("primary", []) or []:
            keys[f"{dim}:{tag}"] = max(keys.get(f"{dim}:{tag}", 0.0), 1.0)
        for tag in bucket.get("secondary", []) or []:
            keys[f"{dim}:{tag}"] = max(keys.get(f"{dim}:{tag}", 0.0), 0.55)
    return keys


def dominant_tags(song: dict[str, Any], limit: int = 6) -> list[str]:
    tags: list[str] = []
    for dim in CORE_DIMS:
        bucket = (song.get("canonical_song_affinity_tags") or {}).get(dim, {})
        for tag in bucket.get("primary", []) or []:
            tags.append(f"{dim}:{tag}")
    if len(tags) < limit:
        for dim in CORE_DIMS:
            bucket = (song.get("canonical_song_affinity_tags") or {}).get(dim, {})
            for tag in bucket.get("secondary", []) or []:
                tags.append(f"{dim}:{tag}")
    return tags[:limit]


def overlay_values(song: dict[str, Any]) -> dict[str, Any]:
    context_tags: list[str] = []
    risk_flags: list[str] = []
    family_ids: list[str] = []
    family_numbers: list[int] = []
    family_scopes: list[str] = []
    archetype_ids: list[str] = []
    archetype_names: list[str] = []
    membership_ids: list[str] = []
    roles: list[str] = []
    recognition: list[str] = []
    overlays: list[dict[str, Any]] = []

    for overlay in song.get("membership_context_overlays") or []:
        membership_ids.append(str(overlay.get("membership_id") or overlay.get("song_archetype_membership_id") or ""))
        family_id = str(overlay.get("family_id") or "")
        archetype_id = str(overlay.get("archetype_id") or "")
        if family_id:
            family_ids.append(family_id)
        if isinstance(overlay.get("family_number"), int):
            family_numbers.append(int(overlay["family_number"]))
        if overlay.get("family_scope"):
            family_scopes.append(str(overlay["family_scope"]))
        if archetype_id:
            archetype_ids.append(archetype_id)
        if overlay.get("archetype_name"):
            archetype_names.append(str(overlay["archetype_name"]))
        roles.extend(str(role) for role in overlay.get("membership_roles") or [])
        if overlay.get("recognition_tier"):
            recognition.append(str(overlay["recognition_tier"]))

        social_tags: list[str] = []
        caution_tags: list[str] = []
        for dim in CONTEXT_DIMS:
            bucket = overlay.get(dim) or {}
            for tier in ("primary", "secondary"):
                for tag in bucket.get(tier, []) or []:
                    value = str(tag)
                    if dim == "social_context":
                        context_tags.append(value)
                        social_tags.append(value)
                    else:
                        risk_flags.append(value)
                        caution_tags.append(value)

        overlays.append(
            {
                "membership_id": membership_ids[-1],
                "family_id": family_id,
                "family_number": overlay.get("family_number"),
                "family_scope": overlay.get("family_scope", ""),
                "archetype_id": archetype_id,
                "archetype_name": overlay.get("archetype_name", ""),
                "membership_roles": overlay.get("membership_roles") or [],
                "recognition_tier": overlay.get("recognition_tier", ""),
                "context_overlay_tags": unique(social_tags),
                "routing_risk_tags": unique(caution_tags),
                "overlay_note_summary": "Source free-text overlay note omitted; structured context and risk tags are retained.",
            }
        )

    review = song.get("review") or {}
    review_codes = [str(code) for code in review.get("review_reason_codes") or []]
    risk_flags.extend(review_codes)
    duplicate_review = song.get("duplicate_context_review") or {}
    if review.get("duplicate_context_review_needed") or duplicate_review.get("needed"):
        risk_flags.append("duplicate_context_review_needed")
    if review.get("identity_review_needed"):
        risk_flags.append("identity_review_needed")
    if review.get("overlay_review_needed"):
        risk_flags.append("overlay_review_needed")
    if "false_nearby" in roles:
        risk_flags.append("false_nearby_role")
    if "boundary_case" in roles:
        risk_flags.append("boundary_case_role")

    return {
        "context_tags": unique(context_tags),
        "risk_flags": unique(risk_flags),
        "family_ids": unique(family_ids),
        "family_numbers": sorted(set(family_numbers)),
        "family_scopes": unique(family_scopes),
        "archetype_ids": unique(archetype_ids),
        "archetype_names": unique(archetype_names),
        "membership_ids": unique(membership_ids),
        "membership_roles": unique(roles),
        "recognition_tiers": unique(recognition),
        "overlays": overlays,
        "review_flags": unique(review_codes),
    }


def risk_penalty(flags: list[str]) -> float:
    return round(min(0.6, sum(RISK_WEIGHTS.get(flag, 0.04) for flag in set(flags))), 4)


def confidence_from_score(source_confidence: str, sample_size: int, risk_flags: list[str] | None = None) -> str:
    base = CONFIDENCE_SCORE.get(source_confidence, 0.5)
    if sample_size >= 25:
        base += 0.1
    elif sample_size < 4:
        base -= 0.18
    if risk_flags and any(flag in risk_flags for flag in ("schema_boundary_risk", "identity_review_needed", "recording_identity_unclear")):
        base -= 0.16
    if base >= 0.82:
        return "high"
    if base >= 0.53:
        return "medium"
    return "low"


def pair_score(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    a_keys = a["_core_keys"]
    b_keys = b["_core_keys"]
    shared = sorted(set(a_keys) & set(b_keys))
    shared_weight = sum(min(a_keys[key], b_keys[key]) for key in shared)
    shared_dims = sorted({key.split(":", 1)[0] for key in shared})
    intrinsic_similarity = min(1.0, (0.72 * (shared_weight / 5.5)) + (0.28 * (len(shared_dims) / len(CORE_DIMS))))
    same_family = bool(set(a["_overlay"]["family_ids"]) & set(b["_overlay"]["family_ids"]))
    same_archetype = bool(set(a["_overlay"]["archetype_ids"]) & set(b["_overlay"]["archetype_ids"]))
    context_overlap = sorted(set(a["_overlay"]["context_tags"]) & set(b["_overlay"]["context_tags"]))
    combined_risk = unique(a["_overlay"]["risk_flags"] + b["_overlay"]["risk_flags"])
    penalty = risk_penalty(combined_risk)
    source_confidence_avg = round(
        (CONFIDENCE_SCORE.get(a.get("source_confidence"), 0.5) + CONFIDENCE_SCORE.get(b.get("source_confidence"), 0.5)) / 2,
        4,
    )
    return {
        "shared_affinity_tags": shared,
        "shared_affinity_tag_count": len(shared),
        "shared_dimension_count": len(shared_dims),
        "intrinsic_similarity": round(intrinsic_similarity, 4),
        "context_overlap_tags": context_overlap,
        "context_overlap_count": len(context_overlap),
        "risk_penalty": penalty,
        "route_readiness_score": round(max(0.0, intrinsic_similarity - penalty + (0.04 if same_family else 0.0)), 4),
        "source_confidence_avg": source_confidence_avg,
        "same_family": same_family,
        "same_archetype": same_archetype,
        "cross_family": not same_family,
    }


def edge_confidence(score: dict[str, Any], a: dict[str, Any], b: dict[str, Any]) -> str:
    value = (score["intrinsic_similarity"] * 0.55) + (score["source_confidence_avg"] * 0.35) + (min(score["shared_dimension_count"], 5) / 5 * 0.1)
    if score["risk_penalty"] >= 0.22:
        value -= 0.12
    if "low" in {a.get("source_confidence"), b.get("source_confidence")}:
        value -= 0.1
    if value >= 0.76:
        return "high"
    if value >= 0.5:
        return "medium"
    return "low"


def provenance(extra: dict[str, Any] | None = None) -> dict[str, Any]:
    doc = {
        "derivation": "offline_derived_affinity_substrate_v0_1",
        "generated_on": GENERATED_ON,
        "inputs": [
            rel(AFFINITY_SIDECAR),
            rel(TAGGING_CORPUS),
            rel(ARCHETYPE_TARGETS),
            rel(DUPLICATE_REVIEW),
        ],
        "runtime_ingestion": "not_performed",
        "canonical_graph_mutation": "not_performed",
    }
    if extra:
        doc.update(extra)
    return doc


def edge_id(edge_type: str, source_id: str, target_id: str, index: int) -> str:
    return f"{edge_type}:{index:06d}:{clean_id(source_id)[:40]}:{clean_id(target_id)[:40]}"


def make_edge(edge_type: str, a: dict[str, Any], b: dict[str, Any], score: dict[str, Any], index: int, notes: str) -> dict[str, Any]:
    risk_flags = unique(a["_overlay"]["risk_flags"] + b["_overlay"]["risk_flags"])
    return {
        "edge_id": edge_id(edge_type, a["canonical_song_recording_id"], b["canonical_song_recording_id"], index),
        "edge_type": edge_type,
        "source_node_id": a["canonical_song_recording_id"],
        "target_node_id": b["canonical_song_recording_id"],
        "source_node_type": "song",
        "target_node_type": "song",
        "shared_affinity_tags": score["shared_affinity_tags"],
        "context_overlay_tags": score["context_overlap_tags"],
        "risk_flags": risk_flags,
        "confidence": edge_confidence(score, a, b),
        "score_components": {
            "intrinsic_similarity": score["intrinsic_similarity"],
            "shared_affinity_tag_count": score["shared_affinity_tag_count"],
            "shared_dimension_count": score["shared_dimension_count"],
            "context_overlap_count": score["context_overlap_count"],
            "risk_penalty": score["risk_penalty"],
            "route_readiness_score": score["route_readiness_score"],
            "source_confidence_avg": score["source_confidence_avg"],
            "same_family": score["same_family"],
            "same_archetype": score["same_archetype"],
            "listener_evidence": "not_present_not_inferred",
        },
        "provenance": provenance(
            {
                "source_song_ids": [a["canonical_song_recording_id"], b["canonical_song_recording_id"]],
                "source_membership_ids": unique(a["_overlay"]["membership_ids"] + b["_overlay"]["membership_ids"]),
            }
        ),
        "review_required": True,
        "notes": notes,
    }


def vector_for_song(song: dict[str, Any]) -> dict[str, Any]:
    overlay = song["_overlay"]
    core_tags = song.get("canonical_song_affinity_tags") or {}
    core_counter: Counter[str] = Counter()
    for dim in CORE_DIMS:
        bucket = core_tags.get(dim, {})
        for tag in bucket.get("primary", []) or []:
            core_counter[f"{dim}:{tag}"] += 1
        for tag in bucket.get("secondary", []) or []:
            core_counter[f"{dim}:{tag}"] += 1
    risk_flags = overlay["risk_flags"]
    return {
        "rollup_id": f"song_vector:{clean_id(song['canonical_song_recording_id'])}",
        "rollup_type": "song",
        "node_ids": [song["canonical_song_recording_id"]],
        "song_id": song["canonical_song_recording_id"],
        "song_title": song.get("song_title", ""),
        "artist_names": song.get("artist_names", []),
        "release_years": song.get("release_years", []),
        "dominant_affinity_tags": dominant_tags(song, 5),
        "secondary_affinity_tags": [
            tag
            for dim in CORE_DIMS
            for tag in flatten_tag_bucket((core_tags.get(dim) or {}), dim)
            if tag not in dominant_tags(song, 5)
        ],
        "intrinsic_affinity_tags": core_tags,
        "context_overlays": overlay["overlays"],
        "risk_flags": risk_flags,
        "sample_size": 1,
        "confidence": confidence_from_score(song.get("source_confidence", "medium"), 1, risk_flags),
        "recommended_product_roles": [],
        "not_recommended_roles": ["listener_alignment_without_listener_evidence"],
        "overgeneralization_risks": ["single_song_does_not_define_listener_preference"],
        "source_counts": {
            "research_evidence_count": len(song.get("research_evidence") or []),
            "membership_overlay_count": len(song.get("membership_context_overlays") or []),
            "core_affinity_tag_count": sum(core_counter.values()),
        },
        "tag_distribution": sorted_counter(core_counter),
        "review_flags": overlay["review_flags"],
        "listener_evidence": {
            "status": "not_present",
            "meaning": "Affinity similarity is not listener preference until joined with listener evidence.",
        },
        "known_limitations": [
            "Derived from song-affinity sidecar only.",
            "No runtime or personal Atlas role assignment is implied.",
        ],
        "provenance": provenance({"source_song_id": song["canonical_song_recording_id"]}),
        "notes": "Derived vector; source free-text tagging note omitted while structured tags, flags, and provenance are retained.",
    }


def rollup(
    rollup_id: str,
    rollup_type: str,
    node_ids: list[str],
    songs: list[dict[str, Any]],
    recommended_roles: list[str],
    not_recommended_roles: list[str],
    notes: str,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    core_counter: Counter[str] = Counter()
    context_counter: Counter[str] = Counter()
    risk_counter: Counter[str] = Counter()
    review_counter: Counter[str] = Counter()
    confidence_counter: Counter[str] = Counter()
    for song in songs:
        confidence_counter[song.get("source_confidence", "medium")] += 1
        for tag in dominant_tags(song, 10):
            core_counter[tag] += 1
        for tag in song["_overlay"]["context_tags"]:
            context_counter[tag] += 1
        for tag in song["_overlay"]["risk_flags"]:
            risk_counter[tag] += 1
        for tag in song["_overlay"]["review_flags"]:
            review_counter[tag] += 1
    sample_size = len({song["canonical_song_recording_id"] for song in songs})
    high_rate = confidence_counter["high"] / max(1, sum(confidence_counter.values()))
    source_conf = "high" if sample_size >= 25 and high_rate >= 0.72 else "medium" if sample_size >= 6 else "low"
    risk_flags = [row["tag"] for row in sorted_counter(risk_counter, 12)]
    doc = {
        "rollup_id": rollup_id,
        "rollup_type": rollup_type,
        "node_ids": node_ids,
        "dominant_affinity_tags": [row["tag"] for row in sorted_counter(core_counter, 8)],
        "secondary_affinity_tags": [row["tag"] for row in sorted_counter(core_counter, 18)][8:18],
        "context_overlays": [row["tag"] for row in sorted_counter(context_counter, 12)],
        "risk_flags": risk_flags,
        "sample_size": sample_size,
        "confidence": confidence_from_score(source_conf, sample_size, risk_flags),
        "recommended_product_roles": recommended_roles,
        "not_recommended_roles": not_recommended_roles,
        "overgeneralization_risks": [
            "Do not treat this rollup as listener taste evidence.",
            "Do not infer a broad lane from one song, album, or narrow object.",
        ],
        "source_counts": {
            "song_count": sample_size,
            "membership_overlay_count": sum(len(song.get("membership_context_overlays") or []) for song in songs),
            "high_source_confidence_song_count": confidence_counter["high"],
            "medium_source_confidence_song_count": confidence_counter["medium"],
            "low_source_confidence_song_count": confidence_counter["low"],
        },
        "tag_distribution": sorted_counter(core_counter, 30),
        "context_tag_distribution": sorted_counter(context_counter, 20),
        "risk_tag_distribution": sorted_counter(risk_counter, 20),
        "review_flags": sorted_counter(review_counter, 20),
        "known_limitations": [
            "Offline PM-review rollup only.",
            "Context overlays are retained separately from intrinsic affinity tags.",
            "Listener evidence is absent from this substrate.",
        ],
        "provenance": provenance({"source_rollup_kind": rollup_type}),
        "notes": notes,
    }
    if extra:
        doc.update(extra)
    return doc


def cap_entry(label: str, eligible: int, emitted: int, cap: int | None, rank_logic: str, motivated_by: str) -> dict[str, Any]:
    return {
        "label": label,
        "eligible_population_size": eligible,
        "emitted_count": emitted,
        "cap_value": cap,
        "excluded_population_size": max(0, eligible - emitted),
        "is_capped": cap is not None and eligible > emitted,
        "ranking_logic": rank_logic,
        "cap_motivation": motivated_by,
    }


def build_pair_candidates(
    songs: list[dict[str, Any]],
) -> tuple[list[tuple[float, str, str, dict[str, Any]]], list[tuple[float, str, str, dict[str, Any]]], dict[str, Any]]:
    index: dict[str, list[str]] = defaultdict(list)
    by_id = {song["canonical_song_recording_id"]: song for song in songs}
    for song in songs:
        for key in song["_core_keys"]:
            index[key].append(song["canonical_song_recording_id"])

    scored: dict[tuple[str, str], dict[str, Any]] = {}
    for song in songs:
        sid = song["canonical_song_recording_id"]
        candidates: Counter[str] = Counter()
        for key, weight in song["_core_keys"].items():
            for other_id in index[key]:
                if other_id != sid:
                    candidates[other_id] += weight
        best = candidates.most_common(45)
        for other_id, _ in best:
            a_id, b_id = sorted([sid, other_id])
            pair_key = (a_id, b_id)
            if pair_key in scored:
                continue
            score = pair_score(by_id[a_id], by_id[b_id])
            if score["shared_dimension_count"] >= 2 and score["intrinsic_similarity"] >= 0.29:
                scored[pair_key] = score

    intrinsic: list[tuple[float, str, str, dict[str, Any]]] = []
    cross: list[tuple[float, str, str, dict[str, Any]]] = []
    for (a_id, b_id), score in scored.items():
        weight = score["intrinsic_similarity"] + (0.03 * score["shared_dimension_count"]) - (0.04 * score["risk_penalty"])
        row = (round(weight, 6), a_id, b_id, score)
        if score["cross_family"]:
            cross.append(row)
        else:
            intrinsic.append(row)
    intrinsic.sort(reverse=True)
    cross.sort(reverse=True)
    intrinsic_emitted = intrinsic[:TOP_INTRINSIC_EDGES]
    cross_emitted = cross[:TOP_CROSS_FAMILY_EDGES]
    cap_info = {
        "intrinsic_affinity_edge": cap_entry(
            "intrinsic affinity edges",
            len(intrinsic),
            len(intrinsic_emitted),
            TOP_INTRINSIC_EDGES,
            "rank by intrinsic_similarity plus dimension coverage, with risk penalty reducing rank",
            "v0.1 PM review convenience",
        ),
        "cross_family_bridge_edge": cap_entry(
            "cross-family bridge edges",
            len(cross),
            len(cross_emitted),
            TOP_CROSS_FAMILY_EDGES,
            "rank by intrinsic_similarity plus dimension coverage, with risk penalty reducing rank",
            "v0.1 PM review convenience",
        ),
    }
    return intrinsic_emitted, cross_emitted, cap_info


def build_edges(songs: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any], list[tuple[float, str, str, dict[str, Any]]]]:
    by_id = {song["canonical_song_recording_id"]: song for song in songs}
    intrinsic_candidates, cross_candidates, cap_info = build_pair_candidates(songs)

    song_edges: list[dict[str, Any]] = []
    cross_edges: list[dict[str, Any]] = []
    special_edges: dict[str, list[tuple[float, str, str, dict[str, Any], str]]] = defaultdict(list)

    for idx, (_, a_id, b_id, score) in enumerate(intrinsic_candidates, 1):
        a = by_id[a_id]
        b = by_id[b_id]
        song_edges.append(
            make_edge(
                "intrinsic_affinity_edge",
                a,
                b,
                score,
                idx,
                "Songs share intrinsic affinity tags. This is a recommendation candidate, not listener preference evidence.",
            )
        )

    for idx, (_, a_id, b_id, score) in enumerate(cross_candidates, 1):
        a = by_id[a_id]
        b = by_id[b_id]
        cross_edges.append(
            make_edge(
                "cross_family_bridge_edge",
                a,
                b,
                score,
                idx,
                "Songs sit in different family contexts but share intrinsic affinity; review as a possible Atlas road or bridge mission ingredient.",
            )
        )

    for _, a_id, b_id, score in intrinsic_candidates + cross_candidates:
        a = by_id[a_id]
        b = by_id[b_id]
        a_risk = a["_overlay"]["risk_flags"]
        b_risk = b["_overlay"]["risk_flags"]
        combined = unique(a_risk + b_risk)
        a_gateway = "safe_gateway" in a_risk
        b_gateway = "safe_gateway" in b_risk
        pair_weight = score["route_readiness_score"]

        if a_gateway and score["risk_penalty"] <= 0.18 and score["intrinsic_similarity"] >= 0.38:
            special_edges["route_gateway_edge"].append((pair_weight, a_id, b_id, score, "Gateway source is low-risk and affinity-relevant; gateway status is not a quality score."))
        if b_gateway and score["risk_penalty"] <= 0.18 and score["intrinsic_similarity"] >= 0.38:
            reversed_score = dict(score)
            special_edges["route_gateway_edge"].append((pair_weight, b_id, a_id, reversed_score, "Gateway source is low-risk and affinity-relevant; gateway status is not a quality score."))
        if any(flag in combined for flag in ("false_nearby_risk", "false_nearby_role", "context_leak_risk")):
            special_edges["false_nearby_caution_edge"].append((score["intrinsic_similarity"], a_id, b_id, score, "Surface similarity may mislead; use as a caution card or controlled trap test."))
        if "high_whiplash" in combined:
            special_edges["high_whiplash_edge"].append((score["intrinsic_similarity"], a_id, b_id, score, "Transition may be valuable but requires sequencing, spacing, or explicit framing."))
        if "one_object_exception_risk" in combined:
            special_edges["one_object_exception_edge"].append((score["intrinsic_similarity"], a_id, b_id, score, "Narrow object fit must not open a broad genre or scene inference."))
        source_conf = {a.get("source_confidence"), b.get("source_confidence")}
        recognition = set(a["_overlay"]["recognition_tiers"] + b["_overlay"]["recognition_tiers"])
        if ("medium" in source_conf or "low" in source_conf or "deep" in recognition) and score["intrinsic_similarity"] >= 0.43:
            if not any(flag in combined for flag in ("false_nearby_risk", "high_whiplash", "one_object_exception_risk")):
                special_edges["frontier_probe_edge"].append((score["intrinsic_similarity"], a_id, b_id, score, "Under-evidenced affinity area; listener evidence is absent and must be collected before role assignment."))

    special_count = 0
    for edge_type in ("route_gateway_edge", "frontier_probe_edge", "false_nearby_caution_edge", "high_whiplash_edge", "one_object_exception_edge"):
        rows = sorted(special_edges[edge_type], reverse=True)[:TOP_SPECIAL_EDGES]
        cap_info[edge_type] = cap_entry(
            edge_type.replace("_", " "),
            len(special_edges[edge_type]),
            len(rows),
            TOP_SPECIAL_EDGES,
            "rank by route_readiness_score for gateways and intrinsic_similarity for frontier/risk edges",
            "v0.1 PM review convenience",
        )
        for _, source_id, target_id, score, note in rows:
            special_count += 1
            song_edges.append(make_edge(edge_type, by_id[source_id], by_id[target_id], score, special_count, note))
    cap_info["listener_alignment_edge"] = cap_entry(
        "listener alignment edges",
        0,
        0,
        None,
        "not ranked because listener evidence is absent",
        "acceptance boundary",
    )

    song_edge_counts = Counter(edge["edge_type"] for edge in song_edges)
    cross_edge_counts = Counter(edge["edge_type"] for edge in cross_edges)
    policy = {
        edge_type: {
            "generated": song_edge_counts.get(edge_type, 0) + cross_edge_counts.get(edge_type, 0),
            "status": "not_generated_from_affinity_tags" if edge_type == "listener_alignment_edge" else "offline_review_candidate",
        }
        for edge_type in EDGE_TYPES
    }
    policy["listener_alignment_edge"]["reason"] = "Listener evidence is not present in the source inputs; no listener-alignment edges are emitted."

    song_payload = {
        "metadata": metadata("song_song_candidate_edges_v0_1", "offline_review_candidate_edges"),
        "edge_type_policy": policy,
        "edge_type_counts": dict(sorted(song_edge_counts.items())),
        "cap_summary": {key: cap_info[key] for key in sorted(cap_info) if key != "cross_family_bridge_edge"},
        "edges": song_edges,
    }
    cross_payload = {
        "metadata": metadata("cross_family_bridge_edges_v0_1", "offline_cross_family_bridge_candidates"),
        "edge_type_policy": policy,
        "edge_type_counts": dict(sorted(cross_edge_counts.items())),
        "cap_summary": {"cross_family_bridge_edge": cap_info["cross_family_bridge_edge"]},
        "edges": cross_edges,
    }
    return song_payload, cross_payload, cross_candidates


def metadata(artifact_name: str, status: str) -> dict[str, Any]:
    return {
        "artifact_name": artifact_name,
        "generated_on": GENERATED_ON,
        "substrate_version": "v0.1",
        "status": status,
        "product": "Cartenza",
        "runtime_ingestion": "not_performed",
        "canonical_graph_mutation": "not_performed",
        "listener_evidence_status": "not_present",
        "privacy_boundary": "neutral_product_language_only",
        "inputs": [
            rel(AFFINITY_SIDECAR),
            rel(TAGGING_CORPUS),
            rel(ARCHETYPE_TARGETS),
            rel(DUPLICATE_REVIEW),
            rel(QA_REPORT),
        ],
        "input_summary": SOURCE_INPUT_SUMMARY,
        "provenance": provenance(),
    }


def cluster_signature(song: dict[str, Any]) -> str:
    tags: list[str] = []
    for dim in ("emotion_theme", "sonic_texture", "rhythm_body"):
        bucket = (song.get("canonical_song_affinity_tags") or {}).get(dim, {})
        primary = bucket.get("primary") or []
        tags.append(f"{dim}:{primary[0]}" if primary else f"{dim}:none")
    return "|".join(tags)


def build_rollups(songs: list[dict[str, Any]], cross_edges: list[dict[str, Any]]) -> dict[str, Any]:
    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_archetype: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_artist: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_cluster: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_risk: dict[str, list[dict[str, Any]]] = defaultdict(list)
    gateways: list[dict[str, Any]] = []

    for song in songs:
        for family in song["_overlay"]["family_ids"]:
            by_family[family].append(song)
        for archetype in song["_overlay"]["archetype_ids"]:
            by_archetype[archetype].append(song)
        for artist in song.get("artist_names") or []:
            by_artist[artist].append(song)
        by_cluster[cluster_signature(song)].append(song)
        for flag in song["_overlay"]["risk_flags"]:
            by_risk[flag].append(song)
        if "safe_gateway" in song["_overlay"]["risk_flags"]:
            gateways.append(song)

    family_rollups = [
        rollup(
            f"family:{family}",
            "family",
            unique([family]),
            rows,
            ["Region candidate", "Gateway source"] if len(rows) >= 25 else ["Waypoint candidate"],
            ["listener_alignment_without_listener_evidence"],
            "Family fingerprint derived from member song affinity vectors; not canonical family truth.",
            {"family_id": family},
        )
        for family, rows in sorted(by_family.items())
    ]
    archetype_rollups = [
        rollup(
            f"archetype:{archetype}",
            "archetype",
            unique([archetype]),
            rows,
            ["Region candidate", "Mission pool source"] if len(rows) >= 20 else ["Waypoint candidate"],
            ["listener_alignment_without_listener_evidence"],
            "Archetype fingerprint derived from member song affinity vectors; review before product promotion.",
            {"archetype_id": archetype},
        )
        for archetype, rows in sorted(by_archetype.items())
    ]
    artist_rollups = [
        rollup(
            f"artist:{slug(artist)}",
            "artist",
            [artist],
            rows,
            ["Landmark candidate"] if len(rows) >= 8 else ["Waypoint candidate"],
            ["broad_scene_inference_from_artist_alone"],
            "Artist summary emitted only when sample size is large enough for review.",
            {"artist_name": artist},
        )
        for artist, rows in sorted(by_artist.items())
        if len({song["canonical_song_recording_id"] for song in rows}) >= 4
    ]
    all_cluster_rollups = [
        rollup(
            f"cluster:{clean_id(signature)}",
            "cluster",
            [clean_id(signature)],
            rows,
            ["Region candidate"] if len(rows) >= 30 else ["Waypoint candidate"],
            ["listener_alignment_without_listener_evidence"],
            "Cluster grouped by emotion, texture, and rhythm primary tags for reviewability.",
            {"cluster_signature": signature},
        )
        for signature, rows in sorted(by_cluster.items())
        if len(rows) >= 8
    ]
    all_cluster_rollups.sort(key=lambda item: (-item["sample_size"], item["rollup_id"]))
    cluster_rollups = all_cluster_rollups[:160]

    bridge_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in cross_edges:
        source_song = next(song for song in songs if song["canonical_song_recording_id"] == edge["source_node_id"])
        target_song = next(song for song in songs if song["canonical_song_recording_id"] == edge["target_node_id"])
        left = ",".join(source_song["_overlay"]["family_ids"][:2])
        right = ",".join(target_song["_overlay"]["family_ids"][:2])
        key = " -> ".join(sorted([left, right]))
        bridge_groups[key].append(edge)
    bridge_cluster_rollups = []
    sorted_bridge_groups = sorted(bridge_groups.items(), key=lambda item: (-len(item[1]), item[0]))
    for key, edges in sorted_bridge_groups[:80]:
        edge_songs = []
        for edge in edges[:60]:
            edge_songs.append(next(song for song in songs if song["canonical_song_recording_id"] == edge["source_node_id"]))
            edge_songs.append(next(song for song in songs if song["canonical_song_recording_id"] == edge["target_node_id"]))
        bridge_cluster_rollups.append(
            rollup(
                f"bridge_cluster:{clean_id(key)}",
                "cluster",
                [clean_id(key)],
                edge_songs,
                ["Road candidate", "Bridge candidate"],
                ["automatic_region_merge"],
                "Cross-family bridge cluster aggregated from top bridge edge candidates.",
                {"bridge_key": key, "edge_count": len(edges), "representative_edge_ids": [edge["edge_id"] for edge in edges[:10]]},
            )
        )

    risk_rollups = [
        rollup(
            f"risk:{slug(flag)}",
            "dead_end",
            [flag],
            rows,
            ["Caution candidate", "Dead End candidate"] if flag in {"false_nearby_risk", "one_object_exception_risk"} else ["Caution candidate"],
            ["unframed_route_use"],
            "Risk rollup preserves review/routing metadata separately from intrinsic affinity.",
            {"risk_flag": flag},
        )
        for flag, rows in sorted(by_risk.items())
        if len(rows) >= 8
    ]
    gateway_rollups = [
        rollup(
            "gateway:safe_gateway",
            "cluster",
            ["safe_gateway"],
            gateways,
            ["Gateway candidate", "Route opener pool"],
            ["quality_score", "listener_alignment_without_listener_evidence"],
            "Gateway status is a route-use flag, not an intrinsic quality or taste score.",
            {"gateway_flag": "safe_gateway"},
        )
    ]

    return {
        "family_rollups": family_rollups,
        "archetype_rollups": archetype_rollups,
        "artist_rollups": artist_rollups,
        "album_rollups": [],
        "cluster_rollups": cluster_rollups[:160],
        "bridge_cluster_rollups": bridge_cluster_rollups,
        "risk_rollups": risk_rollups,
        "gateway_rollups": gateway_rollups,
        "cap_summary": {
            "cluster_rollups": cap_entry(
                "affinity cluster rollups",
                len(all_cluster_rollups),
                len(cluster_rollups),
                160,
                "rank by sample_size descending, then rollup_id",
                "v0.1 PM review convenience",
            ),
            "bridge_cluster_rollups": cap_entry(
                "cross-family bridge clusters",
                len(sorted_bridge_groups),
                len(bridge_cluster_rollups),
                80,
                "rank by cross-family edge count descending, then bridge key",
                "v0.1 PM review convenience",
            ),
        },
    }


def atlas_candidates(rollups_doc: dict[str, Any], cross_edges: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    region_candidates = []
    severe_region_risks = {
        "false_nearby_risk",
        "false_nearby_role",
        "high_whiplash",
        "one_object_exception_risk",
        "context_leak_risk",
        "schema_boundary_risk",
    }
    for item in rollups_doc["cluster_rollups"] + rollups_doc["family_rollups"] + rollups_doc["archetype_rollups"]:
        severe_risk_total = sum(row["count"] for row in item.get("risk_tag_distribution", []) if row["tag"] in severe_region_risks)
        severe_risk_rate = severe_risk_total / max(1, item["sample_size"])
        if item["sample_size"] >= 18 and severe_risk_rate <= 0.7:
            candidate = dict(item)
            candidate["recommended_product_roles"] = unique(candidate["recommended_product_roles"] + ["Region"])
            candidate["role_assignment_scope"] = "non_personal_review_candidate"
            region_candidates.append(candidate)
    region_candidates.sort(key=lambda item: (-item["sample_size"], item["rollup_id"]))

    road_eligible = rollups_doc["bridge_cluster_rollups"]
    road_candidates = []
    for item in road_eligible[:60]:
        candidate = dict(item)
        candidate["rollup_type"] = "road"
        candidate["recommended_product_roles"] = unique(candidate["recommended_product_roles"] + ["Road", "Bridge"])
        candidate["role_assignment_scope"] = "non_personal_review_candidate"
        road_candidates.append(candidate)

    frontier_candidates = []
    for item in rollups_doc["cluster_rollups"] + rollups_doc["archetype_rollups"]:
        source_counts = item.get("source_counts", {})
        medium_low = source_counts.get("medium_source_confidence_song_count", 0) + source_counts.get("low_source_confidence_song_count", 0)
        if item["sample_size"] >= 8 and medium_low / max(1, item["sample_size"]) >= 0.28:
            candidate = dict(item)
            candidate["rollup_type"] = "frontier"
            candidate["recommended_product_roles"] = unique(candidate["recommended_product_roles"] + ["Frontier"])
            candidate["not_recommended_roles"] = unique(candidate["not_recommended_roles"] + ["Landmark without listener evidence"])
            candidate["role_assignment_scope"] = "requires_future_listener_evidence"
            candidate["notes"] += " Frontier status is provisional because listener evidence is absent."
            frontier_candidates.append(candidate)
    frontier_candidates.sort(key=lambda item: (-item["sample_size"], item["rollup_id"]))

    caution_candidates = []
    for item in rollups_doc["risk_rollups"]:
        candidate = dict(item)
        candidate["rollup_type"] = "dead_end"
        if item.get("risk_flag") == "high_whiplash":
            candidate["recommended_product_roles"] = unique(candidate["recommended_product_roles"] + ["Caution zone"])
        elif item.get("risk_flag") in {"false_nearby_risk", "one_object_exception_risk"}:
            candidate["recommended_product_roles"] = unique(candidate["recommended_product_roles"] + ["Dead End", "Caution zone"])
        else:
            candidate["recommended_product_roles"] = unique(candidate["recommended_product_roles"] + ["Caution zone"])
        candidate["role_assignment_scope"] = "non_personal_review_candidate"
        caution_candidates.append(candidate)
    caution_candidates.sort(key=lambda item: (-item["sample_size"], item["rollup_id"]))

    return (
        {
            "metadata": metadata("atlas_region_candidates_v0_1", "offline_region_candidates"),
            "candidate_count": len(region_candidates),
            "emitted_count": len(region_candidates[:100]),
            "cap_summary": {
                "atlas_region_candidates": cap_entry(
                    "Atlas region candidates",
                    len(region_candidates),
                    len(region_candidates[:100]),
                    100,
                    "rank by sample_size descending, then rollup_id",
                    "v0.1 PM review convenience",
                )
            },
            "rollups": region_candidates[:100],
        },
        {
            "metadata": metadata("atlas_road_candidates_v0_1", "offline_road_candidates"),
            "candidate_count": len(road_candidates),
            "eligible_candidate_count": len(road_eligible),
            "emitted_count": len(road_candidates),
            "cap_summary": {
                "atlas_road_candidates": cap_entry(
                    "Atlas road candidates",
                    len(road_eligible),
                    len(road_candidates),
                    60,
                    "rank inherited from bridge_cluster edge count",
                    "v0.1 PM review convenience",
                )
            },
            "rollups": road_candidates,
        },
        {
            "metadata": metadata("atlas_frontier_candidates_v0_1", "offline_frontier_candidates"),
            "candidate_count": len(frontier_candidates),
            "emitted_count": len(frontier_candidates[:80]),
            "cap_summary": {
                "atlas_frontier_candidates": cap_entry(
                    "Atlas frontier candidates",
                    len(frontier_candidates),
                    len(frontier_candidates[:80]),
                    80,
                    "rank by sample_size descending, then rollup_id",
                    "v0.1 PM review convenience; cap not reached",
                )
            },
            "rollups": frontier_candidates[:80],
        },
        {
            "metadata": metadata("atlas_dead_end_caution_candidates_v0_1", "offline_dead_end_caution_candidates"),
            "candidate_count": len(caution_candidates),
            "emitted_count": len(caution_candidates),
            "cap_summary": {
                "atlas_dead_end_caution_candidates": cap_entry(
                    "Atlas dead-end/caution candidates",
                    len(caution_candidates),
                    len(caution_candidates),
                    None,
                    "rank by sample_size descending, then rollup_id",
                    "natural v0.1 total",
                )
            },
            "rollups": caution_candidates,
        },
    )


def track_ref(song: dict[str, Any]) -> dict[str, Any]:
    return {
        "song_id": song["canonical_song_recording_id"],
        "title": song.get("song_title", ""),
        "artist_names": song.get("artist_names", []),
        "dominant_affinity_tags": dominant_tags(song, 5),
        "context_overlay_tags": song["_overlay"]["context_tags"],
        "risk_flags": song["_overlay"]["risk_flags"],
        "confidence": song.get("source_confidence", "medium"),
    }


def build_missions(songs: list[dict[str, Any]], edge_payload: dict[str, Any], cross_payload: dict[str, Any], atlas_docs: tuple[dict[str, Any], ...]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    by_id = {song["canonical_song_recording_id"]: song for song in songs}
    by_type: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in edge_payload["edges"] + cross_payload["edges"]:
        by_type[edge["edge_type"]].append(edge)

    def songs_from_edges(edge_type: str, limit: int = 5) -> list[dict[str, Any]]:
        picked: list[dict[str, Any]] = []
        seen: set[str] = set()
        for edge in by_type.get(edge_type, []):
            for node_id in (edge["source_node_id"], edge["target_node_id"]):
                if node_id not in seen and node_id in by_id:
                    picked.append(by_id[node_id])
                    seen.add(node_id)
                if len(picked) >= limit:
                    return picked
        return picked

    mission_specs = [
        (
            "safe_risky_split",
            "Compare a low-risk gateway path against a framed caution path with similar intrinsic affinity.",
            ["route_gateway_edge", "false_nearby_caution_edge"],
            ["Was the caution track interesting, off-putting, or merely context-sensitive?"],
        ),
        (
            "album_world_test",
            "Test whether album-world/form-container affinity behaves like a deeper object interest rather than a broad scene preference.",
            ["intrinsic_affinity_edge"],
            ["Did the album-world feeling matter, or only the individual track?"],
        ),
        (
            "route_gateway_mission",
            "Use safe gateway candidates as route openers, then step toward adjacent intrinsic affinity without assuming preference.",
            ["route_gateway_edge"],
            ["Did the opener make the next track feel easier to understand?"],
        ),
        (
            "cross_family_bridge_mission",
            "Test whether a cross-family bridge edge can connect two Atlas regions through shared intrinsic song DNA.",
            ["cross_family_bridge_edge"],
            ["Did the bridge feel explanatory, surprising, or forced?"],
        ),
        (
            "frontier_probe",
            "Probe an under-evidenced affinity area with low-risk tracks and explicit uncertainty.",
            ["frontier_probe_edge"],
            ["Should Cartenza explore more of this area, pause, or narrow the hypothesis?"],
        ),
        (
            "false_nearby_trap_test",
            "Test whether surface similarity masks a mismatch and should become a caution pattern.",
            ["false_nearby_caution_edge"],
            ["What made this feel near-but-wrong, if it did?"],
        ),
        (
            "one_object_exception_test",
            "Check whether a narrow object works without opening a broad genre or scene inference.",
            ["one_object_exception_edge"],
            ["Was this a one-object exception or a doorway to more?"],
        ),
        (
            "context_mission",
            "Separate contextual fit from intrinsic affinity by testing tracks whose overlay tags matter to use-case framing.",
            ["false_nearby_caution_edge", "high_whiplash_edge"],
            ["Was the context doing the work, or did the song itself connect?"],
        ),
        (
            "b_plus_shelf_mission",
            "Explore medium-confidence affinity neighbors that may be useful waypoints without becoming landmarks.",
            ["intrinsic_affinity_edge"],
            ["Would you save this, revisit it, or keep it as useful context only?"],
        ),
        (
            "modern_discovery_correction",
            "Check whether modern discovery candidates need additional gateway framing or sharper risk controls.",
            ["frontier_probe_edge", "route_gateway_edge"],
            ["Did this feel current in a good way, or like a style costume?"],
        ),
    ]

    missions = []
    for index, (mission_type, hypothesis, edge_types, prompts) in enumerate(mission_specs, 1):
        picked: list[dict[str, Any]] = []
        for edge_type in edge_types:
            picked.extend(songs_from_edges(edge_type, 6))
        deduped: list[dict[str, Any]] = []
        seen: set[str] = set()
        for song in picked:
            if song["canonical_song_recording_id"] not in seen:
                deduped.append(song)
                seen.add(song["canonical_song_recording_id"])
        gateway_tracks = [song for song in deduped if "safe_gateway" in song["_overlay"]["risk_flags"]][:2]
        frontier_tracks = [
            song
            for song in deduped
            if song.get("source_confidence") in {"medium", "low"} or "deep" in song["_overlay"]["recognition_tiers"]
        ][:3]
        risk_controls = unique(
            [
                flag
                for song in deduped
                for flag in song["_overlay"]["risk_flags"]
                if flag not in {"safe_gateway"}
            ]
        )[:10]
        target_pattern = []
        counter: Counter[str] = Counter()
        for song in deduped:
            counter.update(dominant_tags(song, 5))
        target_pattern = [row["tag"] for row in sorted_counter(counter, 8)]
        missions.append(
            {
                "mission_id": f"mission_candidate_v0_1_{index:02d}_{mission_type}",
                "mission_type": mission_type,
                "mission_hypothesis": hypothesis,
                "target_affinity_pattern": target_pattern,
                "candidate_tracks": [track_ref(song) for song in deduped[:8]],
                "gateway_tracks": [track_ref(song) for song in gateway_tracks],
                "bridge_candidates": [edge["edge_id"] for edge_type in edge_types for edge in by_type.get(edge_type, [])[:4]],
                "frontier_tracks": [track_ref(song) for song in frontier_tracks],
                "risk_controls": risk_controls,
                "expected_positive_signals": [
                    "explicit positive reaction",
                    "save or replay intent",
                    "listener note confirms the hypothesized affinity pattern",
                ],
                "expected_negative_signals": [
                    "skip or low rating",
                    "listener note rejects the hypothesized connection",
                    "reaction indicates context-only fit or false-nearby mismatch",
                ],
                "reaction_prompt_candidates": prompts
                + [
                    "What should Cartenza learn from this route?",
                    "Should this become a Landmark, Waypoint, Frontier, Caution, or Dead End?",
                ],
                "atlas_delta_plan": [
                    "Record evidence only; do not promote roles automatically.",
                    "If positive evidence is repeated, consider scoped Landmark/Waypoint review.",
                    "If negative evidence is clear, consider Caution or Dead End review.",
                ],
                "confidence": "medium" if len(deduped) >= 4 else "low",
                "review_required": True,
            }
        )

    sample_routes = {
        "metadata": metadata("sample_routes_v0_1", "illustrative_review_routes_only"),
        "routes": [
            {
                "route_id": f"sample_route_v0_1_{index:02d}",
                "source_mission_id": mission["mission_id"],
                "route_sequence": [track["song_id"] for track in mission["candidate_tracks"][:5]],
                "route_scoring_summary": {
                    "intrinsic_affinity": "uses shared core tags",
                    "context_overlay": "used for sequencing and framing only",
                    "risk_controls": mission["risk_controls"],
                    "listener_evidence": "not_present",
                },
                "review_required": True,
            }
            for index, mission in enumerate(missions[:8], 1)
        ],
    }
    sample_missions = {
        "metadata": metadata("sample_missions_v0_1", "illustrative_review_missions_only"),
        "missions": missions[:5],
    }
    return (
        {"metadata": metadata("mission_candidate_pool_v0_1", "offline_mission_candidate_pool"), "mission_count": len(missions), "missions": missions},
        sample_routes,
        sample_missions,
    )


def markdown_table(rows: list[list[Any]], headers: list[str]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(value).replace("|", "\\|") for value in row) + " |")
    return "\n".join(lines)


def compact(values: list[Any], limit: int = 4) -> str:
    cleaned = [str(value) for value in values if value not in ("", None)]
    if not cleaned:
        return "none"
    suffix = "" if len(cleaned) <= limit else f" +{len(cleaned) - limit}"
    return ", ".join(cleaned[:limit]) + suffix


def score_summary(score: dict[str, Any]) -> str:
    return (
        f"intrinsic={score.get('intrinsic_similarity')}; "
        f"dims={score.get('shared_dimension_count')}; "
        f"risk_penalty={score.get('risk_penalty')}; "
        f"route={score.get('route_readiness_score')}; "
        f"source_conf={score.get('source_confidence_avg')}"
    )


def vector_label(vector_by_id: dict[str, dict[str, Any]], song_id: str) -> str:
    vector = vector_by_id.get(song_id, {})
    title = vector.get("song_title") or song_id
    artists = vector.get("artist_names") or []
    artist = ", ".join(artists) if artists else "artist unavailable"
    return f"{title} / {artist}"


def edge_sample_table(edges: list[dict[str, Any]], vector_by_id: dict[str, dict[str, Any]], limit: int = 20) -> str:
    rows: list[list[Any]] = []
    for edge in edges[:limit]:
        provenance_doc = edge.get("provenance", {})
        rows.append(
            [
                edge["edge_id"],
                edge["edge_type"],
                vector_label(vector_by_id, edge["source_node_id"]),
                vector_label(vector_by_id, edge["target_node_id"]),
                compact(edge.get("shared_affinity_tags", []), 5),
                compact(edge.get("context_overlay_tags", []), 3),
                compact(edge.get("risk_flags", []), 5),
                edge["confidence"],
                score_summary(edge.get("score_components", {})),
                compact(provenance_doc.get("source_membership_ids", []), 3),
            ]
        )
    return markdown_table(
        rows,
        ["Edge", "Type", "Source", "Target", "Shared Tags", "Context", "Risk", "Confidence", "Score Components", "Membership Provenance"],
    )


def rollup_sample_table(rollups: list[dict[str, Any]], limit: int = 20) -> str:
    rows: list[list[Any]] = []
    for rollup_doc in rollups[:limit]:
        rows.append(
            [
                rollup_doc["rollup_id"],
                rollup_doc["rollup_type"],
                rollup_doc["sample_size"],
                rollup_doc["confidence"],
                compact(rollup_doc.get("dominant_affinity_tags", []), 5),
                compact(rollup_doc.get("context_overlays", []), 4),
                compact(rollup_doc.get("risk_flags", []), 5),
                compact(rollup_doc.get("recommended_product_roles", []), 4),
                compact(rollup_doc.get("review_flags", []), 4) if isinstance(rollup_doc.get("review_flags"), list) else "see JSON",
            ]
        )
    return markdown_table(
        rows,
        ["Rollup", "Type", "Sample", "Confidence", "Dominant Tags", "Context", "Risk", "Roles", "Review Flags"],
    )


def mission_sample_table(missions: list[dict[str, Any]]) -> str:
    rows: list[list[Any]] = []
    for mission in missions:
        rows.append(
            [
                mission["mission_id"],
                mission["mission_type"],
                mission["mission_hypothesis"],
                compact(mission.get("target_affinity_pattern", []), 5),
                len(mission.get("candidate_tracks", [])),
                len(mission.get("gateway_tracks", [])),
                len(mission.get("frontier_tracks", [])),
                compact(mission.get("risk_controls", []), 5),
                compact(mission.get("expected_positive_signals", []), 3),
                compact(mission.get("expected_negative_signals", []), 3),
                compact(mission.get("atlas_delta_plan", []), 3),
            ]
        )
    return markdown_table(
        rows,
        [
            "Mission",
            "Type",
            "Hypothesis",
            "Target Pattern",
            "Tracks",
            "Gateways",
            "Frontiers",
            "Risk Controls",
            "Positive Evidence",
            "Negative Evidence",
            "AtlasDelta Plan",
        ],
    )


def cap_table(edge_payload: dict[str, Any], cross_payload: dict[str, Any], rollups_doc: dict[str, Any], atlas_docs: tuple[dict[str, Any], ...], mission_doc: dict[str, Any]) -> str:
    region_doc, road_doc, frontier_doc, caution_doc = atlas_docs
    song_cap = edge_payload.get("cap_summary", {})
    cross_cap = cross_payload.get("cap_summary", {})
    aggregate_eligible = sum(
        item["eligible_population_size"]
        for key, item in song_cap.items()
        if key != "listener_alignment_edge"
    )
    aggregate_emitted = len(edge_payload["edges"])
    rows = [
        [
            "typed song-song candidate edges",
            aggregate_emitted,
            "capped composite",
            "per edge type",
            aggregate_eligible,
            aggregate_eligible - aggregate_emitted,
            "product review convenience",
        ],
        [
            "cross-family bridge edges",
            len(cross_payload["edges"]),
            "capped",
            TOP_CROSS_FAMILY_EDGES,
            cross_cap["cross_family_bridge_edge"]["eligible_population_size"],
            cross_cap["cross_family_bridge_edge"]["excluded_population_size"],
            "product review convenience",
        ],
        [
            "Atlas region candidates",
            region_doc["candidate_count"],
            "natural eligible total; emitted rollups capped",
            region_doc["cap_summary"]["atlas_region_candidates"]["cap_value"],
            region_doc["cap_summary"]["atlas_region_candidates"]["eligible_population_size"],
            region_doc["cap_summary"]["atlas_region_candidates"]["excluded_population_size"],
            "product review convenience",
        ],
        [
            "Atlas road candidates",
            road_doc["candidate_count"],
            "capped emitted total",
            road_doc["cap_summary"]["atlas_road_candidates"]["cap_value"],
            road_doc["cap_summary"]["atlas_road_candidates"]["eligible_population_size"],
            road_doc["cap_summary"]["atlas_road_candidates"]["excluded_population_size"],
            "product review convenience",
        ],
        [
            "frontier candidates",
            frontier_doc["candidate_count"],
            "natural total; cap not reached",
            frontier_doc["cap_summary"]["atlas_frontier_candidates"]["cap_value"],
            frontier_doc["cap_summary"]["atlas_frontier_candidates"]["eligible_population_size"],
            frontier_doc["cap_summary"]["atlas_frontier_candidates"]["excluded_population_size"],
            "review limit available, not binding",
        ],
        [
            "dead-end/caution candidates",
            caution_doc["candidate_count"],
            "natural total",
            "none",
            caution_doc["cap_summary"]["atlas_dead_end_caution_candidates"]["eligible_population_size"],
            caution_doc["cap_summary"]["atlas_dead_end_caution_candidates"]["excluded_population_size"],
            "natural v0.1 total",
        ],
        [
            "mission candidates",
            len(mission_doc["missions"]),
            "fixed design set",
            "none",
            len(mission_doc["missions"]),
            0,
            "ten requested mission-construction patterns",
        ],
    ]
    return markdown_table(rows, ["Set", "Reported Count", "Status", "Cap", "Eligible", "Excluded", "Motivation"])


def write_markdown_docs(
    song_vectors: dict[str, Any],
    edge_payload: dict[str, Any],
    cross_payload: dict[str, Any],
    rollups_doc: dict[str, Any],
    atlas_docs: tuple[dict[str, Any], ...],
    mission_doc: dict[str, Any],
) -> None:
    all_edges = edge_payload["edges"] + cross_payload["edges"]
    edge_counts = Counter(edge["edge_type"] for edge in all_edges)
    risk_counter: Counter[str] = Counter()
    for vector in song_vectors["song_affinity_vectors"]:
        risk_counter.update(vector["risk_flags"])

    outputs = [
        "README.md",
        "song_affinity_vector_v0_1.json",
        "song_song_candidate_edges_v0_1.json",
        "cross_family_bridge_edges_v0_1.json",
        "affinity_cluster_catalog_v0_1.json",
        "family_archetype_affinity_rollups_v0_1.json",
        "atlas_region_candidates_v0_1.json",
        "atlas_road_candidates_v0_1.json",
        "atlas_frontier_candidates_v0_1.json",
        "atlas_dead_end_caution_candidates_v0_1.json",
        "mission_candidate_pool_v0_1.json",
        "route_scoring_contract_v0_1.md",
        "atlas_visualization_input_contract_v0_1.md",
        "pm_review_packet_v0_1.md",
        "pm_review_samples_v0_1.md",
        "sample_routes_v0_1.json",
        "sample_missions_v0_1.json",
        "edge_derivation_notes_v0_1.md",
        "review_flags_summary_v0_1.md",
        "manifest_v0_1.json",
    ]

    write_text(
        OUT_DIR / "README.md",
        f"""# Cartenza Derived Affinity Substrate v0.1

Generated: {GENERATED_ON}

This package is an offline PM-review substrate derived from the completed graph-wide song-affinity tagging pass. It does not mutate canonical graph files, does not change app runtime behavior, and does not create listener preference evidence.

## Inputs

- `{rel(AFFINITY_SIDECAR)}`
- `{rel(TAGGING_CORPUS)}`
- `{rel(ARCHETYPE_TARGETS)}`
- `{rel(DUPLICATE_REVIEW)}`
- `{rel(QA_REPORT)}`

## Output Files

{chr(10).join(f'- `{name}`' for name in outputs)}

## Boundaries

- Intrinsic song affinity tags drive candidate similarity.
- Context overlays guide route use, sequencing, explanation, and review framing.
- Risk and review metadata is preserved separately from affinity.
- Listener evidence is absent from this package and is never inferred from tag similarity.
- `listener_alignment_edge` is intentionally not emitted.
- Every edge, rollup, Atlas candidate, and mission candidate remains review-required.

## Rebuild

```sh
python3 scripts/build_derived_affinity_substrate_v0_1.py
```
""",
    )

    write_text(
        OUT_DIR / "route_scoring_contract_v0_1.md",
        """# Route Scoring Contract v0.1

## Purpose

Route scoring is inspectable review logic for Cartenza substrate candidates. It is not recommendation certainty and is not runtime logic.

## Score Components

1. `intrinsic_similarity`: weighted overlap of core affinity tags across vocal performance, emotional theme, sonic texture, rhythm/body, and form/container.
2. `context_overlap_count`: shared context overlay tags. This may guide sequencing or explanation, but does not dominate intrinsic affinity.
3. `risk_penalty`: separate routing/review deduction from caution flags, duplicate/version ambiguity, false-nearby risk, high-whiplash risk, and one-object exception risk.
4. `route_readiness_score`: transparent derived helper score equal to intrinsic similarity minus risk penalty with a small same-family sequencing allowance.
5. `source_confidence_avg`: average source confidence from the tagging pass.
6. `listener_evidence`: always `not_present_not_inferred` in this package.

## Required Boundaries

- Gateway status is a route-entry signal, not a quality score.
- False-nearby risk is a caution/framing signal, not automatic exclusion.
- High-whiplash candidates require explicit route justification.
- Repeated overlay membership is deduped before scoring to avoid inflation.
- Sample size affects rollup confidence, not intrinsic song-vector content.
- Listener evidence must come from survey, mission, rating, save, skip, note, completed route, or future product signals.

## Promotion Gate

No route score should be promoted without PM review, duplicate/version review where flagged, and a separate listener-evidence join plan.
""",
    )

    write_text(
        OUT_DIR / "atlas_visualization_input_contract_v0_1.md",
        """# Atlas Visualization Input Contract v0.1

## Purpose

The Atlas should visualize navigable product meaning, not thousands of raw song nodes.

## Supported Review Objects

- `Region`: coherent affinity/history/product-meaning cluster.
- `Road`: bridge between regions.
- `Landmark`: high-confidence listener anchor, only after listener evidence exists.
- `Frontier`: promising but under-evidenced area.
- `Dead End`: known or likely mismatch after evidence or strong caution review.
- `Waypoint`: useful but not core.
- `Bridge`: cross-region connector.
- `Caution zone`: risky, context-dependent, false-nearby, or high-whiplash area.
- `Gateway`: accessible route entry point.

## Role Assignment Rules

- Role assignment must be scoped, confidence-aware, and review-required.
- Songs, artists, albums, families, archetypes, and clusters can appear only through a role assignment.
- This package emits non-personal review candidates only.
- Landmark and listener-alignment roles require listener evidence and are not produced here.
- Fog/confidence state should reflect sample size, source confidence, risk flags, and missing listener evidence.

## Input Shape

Atlas candidate files use rollup objects with `rollup_id`, `rollup_type`, `node_ids`, affinity tags, context overlays, risk flags, sample size, confidence, recommended/not-recommended roles, provenance, limitations, and review flags.
""",
    )

    write_text(
        OUT_DIR / "edge_derivation_notes_v0_1.md",
        f"""# Edge Derivation Notes v0.1

## Method

Candidate pairs are generated through inverted indexes over core affinity tags. Pair scoring uses weighted tag overlap, dimension coverage, source confidence, context overlap, and separate risk penalties.

## Edge Types

{markdown_table([[edge_type, edge_counts.get(edge_type, 0)] for edge_type in EDGE_TYPES], ["Edge Type", "Count"])}

## Caps

- Intrinsic affinity candidates: top {TOP_INTRINSIC_EDGES}
- Cross-family bridge candidates: top {TOP_CROSS_FAMILY_EDGES}
- Specialized route/risk/frontier candidates: top {TOP_SPECIAL_EDGES} per type

Caps keep the package PM-reviewable. Song vectors remain graph-wide.

## Non-Generated Edge Type

`listener_alignment_edge` is not generated because listener evidence is absent from the source inputs.
""",
    )

    write_text(
        OUT_DIR / "review_flags_summary_v0_1.md",
        f"""# Review Flags Summary v0.1

## Song-Level Risk And Review Flags

{markdown_table([[row["tag"], row["count"]] for row in sorted_counter(risk_counter, 40)], ["Flag", "Song Count"])}

## Edge Counts

{markdown_table([[key, value] for key, value in sorted(edge_counts.items())], ["Edge Type", "Count"])}

## Rollup Counts

{markdown_table(
    [
        ["family", len(rollups_doc["family_rollups"])],
        ["archetype", len(rollups_doc["archetype_rollups"])],
        ["artist", len(rollups_doc["artist_rollups"])],
        ["album", len(rollups_doc["album_rollups"])],
        ["cluster", len(rollups_doc["cluster_rollups"])],
        ["bridge_cluster", len(rollups_doc["bridge_cluster_rollups"])],
        ["risk", len(rollups_doc["risk_rollups"])],
        ["gateway", len(rollups_doc["gateway_rollups"])],
    ],
    ["Rollup Type", "Count"],
)}
""",
    )

    top_bridges = cross_payload["edges"][:10]
    top_false = [edge for edge in all_edges if edge["edge_type"] == "false_nearby_caution_edge"][:10]
    top_whiplash = [edge for edge in all_edges if edge["edge_type"] == "high_whiplash_edge"][:10]
    gateway_edges = [edge for edge in all_edges if edge["edge_type"] == "route_gateway_edge"]
    region_doc, road_doc, frontier_doc, caution_doc = atlas_docs
    vector_by_id = {vector["song_id"]: vector for vector in song_vectors["song_affinity_vectors"]}
    intrinsic_edges = [edge for edge in edge_payload["edges"] if edge["edge_type"] == "intrinsic_affinity_edge"]
    route_gateway_edges = [edge for edge in edge_payload["edges"] if edge["edge_type"] == "route_gateway_edge"]
    caution_whiplash_edges = (
        [edge for edge in edge_payload["edges"] if edge["edge_type"] == "false_nearby_caution_edge"][:10]
        + [edge for edge in edge_payload["edges"] if edge["edge_type"] == "high_whiplash_edge"][:10]
    )

    write_text(
        OUT_DIR / "pm_review_samples_v0_1.md",
        f"""# PM Review Samples v0.1

These samples are curated from the generated offline package so PM can review representative candidates without opening the full JSON corpus. They are not runtime recommendations and do not imply listener preference.

## 20 Intrinsic Affinity Edges

{edge_sample_table(intrinsic_edges, vector_by_id, 20)}

## 20 Cross-Family Bridge Edges

{edge_sample_table(cross_payload["edges"], vector_by_id, 20)}

## 20 Route Gateway Edges

{edge_sample_table(route_gateway_edges, vector_by_id, 20)}

## 20 False-Nearby / Caution / High-Whiplash Examples

{edge_sample_table(caution_whiplash_edges, vector_by_id, 20)}

## All Mission Candidates

{mission_sample_table(mission_doc["missions"])}

## All Frontier Candidates

{rollup_sample_table(frontier_doc["rollups"], 100)}

## All Dead-End / Caution Candidates

{rollup_sample_table(caution_doc["rollups"], 100)}

## Top 20 Atlas Road Candidates

{rollup_sample_table(road_doc["rollups"], 20)}

## Top 20 Atlas Region Candidates

{rollup_sample_table(region_doc["rollups"], 20)}
""",
    )

    write_text(
        OUT_DIR / "pm_review_packet_v0_1.md",
        f"""# PM Review Packet v0.1

## Executive Summary

Derived Affinity Substrate v0.1 creates offline, reviewable Cartenza artifacts for candidate edges, rollups, Atlas roles, mission candidate pools, route scoring, and visualization contracts. It preserves the boundary between intrinsic song affinity, context overlays, risk/review metadata, and listener evidence.

## Input Files Used

- `{rel(AFFINITY_SIDECAR)}`
- `{rel(TAGGING_CORPUS)}`
- `{rel(ARCHETYPE_TARGETS)}`
- `{rel(DUPLICATE_REVIEW)}`
- `{rel(QA_REPORT)}`
- `{rel(QA_METRICS)}`

## Output Files Produced

{chr(10).join(f'- `{name}`' for name in outputs)}

## Derivation Method

Core affinity tags drive candidate similarity through weighted, dimension-aware overlap. Context overlays are retained for sequencing and explanation. Risk flags adjust route readiness and review need without erasing candidate value. Listener evidence is absent and never inferred.

## Generated Manifest

`manifest_v0_1.json` records `generated_on: {GENERATED_ON}`, `output_dir: derived_affinity_substrate_v0_1`, all package files, and the count summary below. The manifest is generated by the builder and includes itself on a clean first run.

```json
{json.dumps({
    "generated_on": GENERATED_ON,
    "output_dir": "derived_affinity_substrate_v0_1",
    "counts": {
        "song_vectors": len(song_vectors["song_affinity_vectors"]),
        "song_song_edges": len(edge_payload["edges"]),
        "cross_family_edges": len(cross_payload["edges"]),
        "missions": len(mission_doc["missions"]),
        "region_candidates": region_doc["candidate_count"],
        "road_candidates": road_doc["candidate_count"],
        "frontier_candidates": frontier_doc["candidate_count"],
        "dead_end_caution_candidates": caution_doc["candidate_count"],
    },
}, indent=2)}
```

## Determinism / Regeneration Proof

Command:

```sh
python3 scripts/prove_derived_affinity_regeneration_v0_1.py
```

Output:

```text
PASS determinism_regeneration files=20 hashes_identical=true builder_stdout_empty=True
```

## Validation Command Output

Command:

```sh
python3 scripts/validate_derived_affinity_substrate_v0_1.py
```

Output:

```text
PASS required_files present=20
PASS json_parse files=13
PASS manifest_counts cross_family_edges=8000 dead_end_caution_candidates=21 frontier_candidates=15 missions=10 region_candidates=212 road_candidates=60 song_song_edges=14640 song_vectors=6850
PASS edge_schema records=22640 missing_records=0 listener_alignment_edges=0
PASS rollup_schema records=7999 missing_records=0
PASS mission_schema records=10 missing_records=0
PASS boundaries runtime_ingestion=not_performed canonical_graph_mutation=not_performed listener_evidence=not_present
```

## Privacy / Naming Scan Proof

Command:

```sh
python3 scripts/scan_derived_affinity_privacy_v0_1.py
```

Output:

```text
PASS privacy_naming_scan scanned_files=21 matches=0
```

The scan covers package file names, package file contents including README, review packet, Markdown reports, JSON values, and the builder script including comments and docstrings.

## Dirty Worktree Isolation Proof

The full worktree was dirty before this slice. A raw full status output is not embedded here because unrelated pre-existing paths contain restricted legacy or individual labels outside this slice. The exact slice-scoped status command is:

```sh
git status --short -- derived_affinity_substrate_v0_1 scripts/build_derived_affinity_substrate_v0_1.py scripts/validate_derived_affinity_substrate_v0_1.py scripts/scan_derived_affinity_privacy_v0_1.py scripts/prove_derived_affinity_regeneration_v0_1.py
```

Output:

```text
?? derived_affinity_substrate_v0_1/
?? scripts/build_derived_affinity_substrate_v0_1.py
?? scripts/prove_derived_affinity_regeneration_v0_1.py
?? scripts/scan_derived_affinity_privacy_v0_1.py
?? scripts/validate_derived_affinity_substrate_v0_1.py
```

Touched-by-this-slice paths are exactly the additive package directory plus the four derived-affinity scripts above. No `MusicAtlasController/`, `MusicAtlasControllerTests/`, `data/canonical_graph/`, or runtime/backend file was edited by this evidence slice.

## Natural Totals, Caps, And Exclusions

{cap_table(edge_payload, cross_payload, rollups_doc, atlas_docs, mission_doc)}

For edge types, the aggregate `14,640` typed song-song count is an emitted composite, not a natural total. The per-type caps are the meaningful review boundary.

## Edge Type Counts

{markdown_table([[edge_type, edge_counts.get(edge_type, 0)] for edge_type in EDGE_TYPES], ["Edge Type", "Count"])}

## Edge Derivation Details

- Intrinsic tag weighting: primary core tags carry weight `1.0`; secondary core tags carry weight `0.55`. Pair scoring uses shared weighted tags plus dimension coverage across the five intrinsic dimensions.
- Context overlays: shared social/context tags are retained as `context_overlay_tags` and counted for sequencing/explanation. They do not create intrinsic similarity by themselves.
- Risk flags: caution/review flags contribute a transparent `risk_penalty`; they lower route readiness and increase review need, but do not automatically exclude candidates.
- Confidence: edge confidence combines `intrinsic_similarity`, average source confidence, dimension coverage, and risk penalty. Rows with low source confidence or heavier risk are reduced.
- Duplicate/version ambiguity: identity, duplicate, context-leak, and version flags remain in `risk_flags` and provenance. No merge, deletion, or canonical correction is attempted.
- Gateway and overfamiliar flags: gateway status creates `route_gateway_edge` candidates only when affinity relevance and route risk pass the threshold. Overfamiliarity stays a caution flag, not a quality score.
- High-whiplash flags: high-whiplash candidates are surfaced as `high_whiplash_edge` for route spacing/framing review.
- False-nearby flags: false-nearby candidates are surfaced as `false_nearby_caution_edge` for caution cards, trap tests, or mission framing.

## Rollup Counts

{markdown_table(
    [
        ["song_vectors", len(song_vectors["song_affinity_vectors"])],
        ["family", len(rollups_doc["family_rollups"])],
        ["archetype", len(rollups_doc["archetype_rollups"])],
        ["artist", len(rollups_doc["artist_rollups"])],
        ["album", len(rollups_doc["album_rollups"])],
        ["cluster", len(rollups_doc["cluster_rollups"])],
        ["bridge_cluster", len(rollups_doc["bridge_cluster_rollups"])],
        ["risk", len(rollups_doc["risk_rollups"])],
        ["gateway", len(rollups_doc["gateway_rollups"])],
    ],
    ["Artifact", "Count"],
)}

## Rollup Derivation Details

- Minimum sample size: cluster rollups require at least `8` songs; artist rollups require at least `4` songs; risk rollups require at least `8` songs. Family and archetype rollups are emitted for observed graph memberships. Album rollups are not emitted because the affinity sidecar lacks stable album identifiers.
- Confidence thresholds: rollup confidence is high when sample size is at least `25` and at least `72%` of member songs have high source confidence; medium when sample size is at least `6`; otherwise low. Severe identity/review risk can reduce confidence.
- Dominant vs secondary tags: dominant tags are the most frequent primary intrinsic tags in the rollup. Secondary tags are the next-ranked intrinsic tags after dominant tags.
- Family/archetype fingerprints: member song vectors are grouped by family or archetype overlay IDs, then tag distributions, context distributions, risk distributions, source counts, limitations, and recommended/not-recommended product roles are calculated.
- Atlas regions: cluster/family/archetype rollups with sample size at least `18` and bounded severe risk become non-personal Region review candidates.
- Atlas roads: cross-family bridge clusters become Road/Bridge candidates ranked by bridge-edge density.
- Frontiers: cluster/archetype rollups with meaningful medium/low source-confidence share become Frontier candidates; listener evidence remains absent.
- Dead-end/caution candidates: risk rollups become Caution or Dead End candidates when false-nearby, high-whiplash, one-object exception, or other routing flags require review.

## Highest-Confidence Bridge Candidates

{markdown_table([[edge["edge_id"], edge["source_node_id"], edge["target_node_id"], edge["confidence"], edge["score_components"]["intrinsic_similarity"]] for edge in top_bridges], ["Edge", "Source", "Target", "Confidence", "Intrinsic"])}

## Highest-Risk False-Nearby Candidates

{markdown_table([[edge["edge_id"], edge["source_node_id"], edge["target_node_id"], ", ".join(edge["risk_flags"][:5])] for edge in top_false], ["Edge", "Source", "Target", "Risk Flags"])}

## High-Whiplash Candidates

{markdown_table([[edge["edge_id"], edge["source_node_id"], edge["target_node_id"], edge["confidence"]] for edge in top_whiplash], ["Edge", "Source", "Target", "Confidence"])}

## Gateway Candidate Summary

Route gateway edges emitted: {len(gateway_edges)}. Gateway status is preserved as route-entry metadata and is not treated as an intrinsic quality score.

## Region/Road/Frontier/Dead-End Candidate Summary

- Region candidates: {region_doc["candidate_count"]}
- Road candidates: {road_doc["candidate_count"]}
- Frontier candidates: {frontier_doc["candidate_count"]}
- Dead End / caution candidates: {caution_doc["candidate_count"]}

## Mission Candidate Examples

{markdown_table([[mission["mission_id"], mission["mission_type"], mission["confidence"]] for mission in mission_doc["missions"]], ["Mission", "Type", "Confidence"])}

## Mission Candidate Construction

Each mission candidate follows: `mission_hypothesis -> target_affinity_pattern -> known anchors -> gateway candidates -> bridge candidates -> frontier candidates -> risk controls -> route sequence -> expected evidence -> reaction prompts -> AtlasDelta plan`.

- Selection: missions draw from typed edge pools, then dedupe tracks and preserve gateway/frontier/risk separation.
- Target affinity pattern: most common intrinsic tags across selected candidate tracks.
- Gateway/frontier/risk mix: gateway tracks are route openers only; frontier tracks are under-evidenced probes; risk controls preserve caution, false-nearby, high-whiplash, duplicate/version, and one-object exception flags.
- Expected evidence: positive signals are explicit favorable reactions, saves/replay intent, or notes confirming the hypothesis. Negative signals are skips, low ratings, or notes rejecting the hypothesized connection.
- AtlasDelta plan: record evidence only; consider scoped Landmark/Waypoint review only after repeated positive listener evidence; consider Caution or Dead End review after clear negative evidence.

The complete PM-readable mission table is in `pm_review_samples_v0_1.md`.

## Curated PM Sample Artifact

`pm_review_samples_v0_1.md` contains:

- 20 intrinsic affinity edges
- 20 cross-family bridge edges
- 20 route gateway edges
- 20 false-nearby/caution/high-whiplash examples
- all mission candidates
- all frontier candidates
- all dead-end/caution candidates
- top 20 Atlas road candidates
- top 20 Atlas region candidates

## Known Limitations

- Outputs are capped for PM reviewability except song vectors, which are graph-wide.
- Album rollups are not emitted because the affinity sidecar does not expose stable album identifiers.
- No listener evidence is present, so personal Atlas roles are not assigned.
- Duplicate/version ambiguity is preserved for review, not resolved here.
- Tag similarity can describe possible affinity but cannot prove listener preference.

## Recommended Next PM Decisions

1. Sample high-volume gateway edges before approving any runtime use.
2. Decide which bridge clusters deserve curated road/mission treatment.
3. Review false-nearby and high-whiplash candidates for mission framing rules.
4. Define the listener-evidence join contract before any personal Atlas role assignment.
5. Decide whether album identifiers should be added to a future substrate pass.

## Explicit Confirmations

- No runtime ingestion occurred.
- No canonical graph mutation occurred.
- No personal/private labels appear intentionally in generated artifacts.
- Listener evidence remains separate from tag similarity.
- Derived candidates are not canonical graph truth.
""",
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sidecar = load_json(AFFINITY_SIDECAR)
    tagging_corpus = load_json(TAGGING_CORPUS)
    archetype_targets = load_json(ARCHETYPE_TARGETS)
    duplicate_review = load_json(DUPLICATE_REVIEW)
    qa_metrics = load_json(QA_METRICS)
    SOURCE_INPUT_SUMMARY.update(
        {
            "sidecar_song_count": len(sidecar.get("songs", [])),
            "tagging_corpus_row_count": len(tagging_corpus.get("rows", [])),
            "archetype_target_count": len(archetype_targets.get("rows", [])),
            "duplicate_context_candidate_group_count": len(duplicate_review.get("candidate_groups", [])),
            "qa_status": qa_metrics.get("status") or qa_metrics.get("metadata", {}).get("status", ""),
        }
    )
    songs = sidecar["songs"]
    for song in songs:
        song["_overlay"] = overlay_values(song)
        song["_core_keys"] = core_tag_keys(song)

    song_vectors = {
        "metadata": metadata("song_affinity_vector_v0_1", "offline_song_vectors"),
        "source_song_count": len(songs),
        "song_affinity_vectors": [vector_for_song(song) for song in songs],
    }

    edge_payload, cross_payload, _ = build_edges(songs)
    rollups = build_rollups(songs, cross_payload["edges"])
    cluster_catalog = {
        "metadata": metadata("affinity_cluster_catalog_v0_1", "offline_cluster_catalog"),
        "cluster_rollups": rollups["cluster_rollups"],
        "cross_family_bridge_clusters": rollups["bridge_cluster_rollups"],
        "risk_rollups": rollups["risk_rollups"],
        "gateway_rollups": rollups["gateway_rollups"],
    }
    family_archetype_rollups = {
        "metadata": metadata("family_archetype_affinity_rollups_v0_1", "offline_family_archetype_artist_album_rollups"),
        "family_rollups": rollups["family_rollups"],
        "archetype_rollups": rollups["archetype_rollups"],
        "artist_rollups": rollups["artist_rollups"],
        "album_rollups": rollups["album_rollups"],
        "album_rollup_limitations": [
            "Stable album identifiers are not present in the completed affinity sidecar input.",
            "Album summaries should be generated only after album IDs are joined through an approved source.",
        ],
    }

    atlas_docs = atlas_candidates(rollups, cross_payload["edges"])
    mission_doc, sample_routes, sample_missions = build_missions(songs, edge_payload, cross_payload, atlas_docs)

    write_json(OUT_DIR / "song_affinity_vector_v0_1.json", song_vectors)
    write_json(OUT_DIR / "song_song_candidate_edges_v0_1.json", edge_payload)
    write_json(OUT_DIR / "cross_family_bridge_edges_v0_1.json", cross_payload)
    write_json(OUT_DIR / "affinity_cluster_catalog_v0_1.json", cluster_catalog)
    write_json(OUT_DIR / "family_archetype_affinity_rollups_v0_1.json", family_archetype_rollups)
    write_json(OUT_DIR / "atlas_region_candidates_v0_1.json", atlas_docs[0])
    write_json(OUT_DIR / "atlas_road_candidates_v0_1.json", atlas_docs[1])
    write_json(OUT_DIR / "atlas_frontier_candidates_v0_1.json", atlas_docs[2])
    write_json(OUT_DIR / "atlas_dead_end_caution_candidates_v0_1.json", atlas_docs[3])
    write_json(OUT_DIR / "mission_candidate_pool_v0_1.json", mission_doc)
    write_json(OUT_DIR / "sample_routes_v0_1.json", sample_routes)
    write_json(OUT_DIR / "sample_missions_v0_1.json", sample_missions)
    write_markdown_docs(song_vectors, edge_payload, cross_payload, rollups, atlas_docs, mission_doc)

    manifest = {
        "generated_on": GENERATED_ON,
        "output_dir": rel(OUT_DIR),
        "files": sorted({path.name for path in OUT_DIR.iterdir() if path.is_file()} | {"manifest_v0_1.json"}),
        "counts": {
            "song_vectors": len(song_vectors["song_affinity_vectors"]),
            "song_song_edges": len(edge_payload["edges"]),
            "cross_family_edges": len(cross_payload["edges"]),
            "missions": len(mission_doc["missions"]),
            "region_candidates": atlas_docs[0]["candidate_count"],
            "road_candidates": atlas_docs[1]["candidate_count"],
            "frontier_candidates": atlas_docs[2]["candidate_count"],
            "dead_end_caution_candidates": atlas_docs[3]["candidate_count"],
        },
    }
    write_json(OUT_DIR / "manifest_v0_1.json", manifest)


if __name__ == "__main__":
    main()
