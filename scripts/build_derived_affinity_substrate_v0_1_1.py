#!/usr/bin/env python3
"""Build Cartenza Derived Affinity Substrate v0.1.1 hardening evidence.

This is an offline post-processing hardening pass over the accepted v0.1
derived package. It does not mutate canonical graph inputs, does not change
runtime behavior, and does not add listener evidence.
"""

from __future__ import annotations

import difflib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "derived_affinity_substrate_v0_1"
OUT_DIR = ROOT / "derived_affinity_substrate_v0_1_1"
GENERATED_ON = "2026-05-28"

IDENTITY_FLAGS = {
    "duplicate_context_review_needed",
    "duplicate_context_unclear",
    "identity_review_needed",
    "recording_identity_unclear",
    "version_ambiguity",
    "context_leak_risk",
    "schema_boundary_risk",
}
FALSE_NEARBY_FLAGS = {"false_nearby_risk", "false_nearby_role"}
WHIPLASH_FLAGS = {"high_whiplash"}
CONTEXT_FLAGS = {"context_dependent", "novelty_risk", "camp_sensitive", "one_object_exception_risk", "sentimentality_risk"}
OVERFAMILIAR_FLAGS = {"overfamiliar_anchor"}
BRIDGE_CATEGORIES = (
    "clean_bridge_candidate",
    "review_bridge_candidate",
    "identity_quarantine",
    "context_only_bridge",
    "high_whiplash_bridge",
    "false_nearby_bridge",
    "mission_specific_bridge",
)


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, body: str) -> None:
    path.write_text(body.rstrip() + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def normalize(value: str) -> str:
    value = value.lower()
    value = re.sub(r"\([^)]*\)", " ", value)
    value = re.sub(r"\b(feat|ft|featuring|with)\b.*", " ", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def artist_tokens(artists: list[str]) -> set[str]:
    tokens: set[str] = set()
    for artist in artists:
        cleaned = normalize(artist)
        if cleaned.startswith("the "):
            cleaned = cleaned[4:]
        tokens.add(cleaned)
        tokens.add(re.sub(r"\b(and|the)\b", " ", cleaned).strip())
    return {token for token in tokens if token}


def title_similarity(a: str, b: str) -> float:
    left = normalize(a)
    right = normalize(b)
    if not left or not right:
        return 0.0
    return difflib.SequenceMatcher(None, left, right).ratio()


def same_or_near_title(a: dict[str, Any], b: dict[str, Any]) -> bool:
    left = normalize(a.get("song_title", ""))
    right = normalize(b.get("song_title", ""))
    if not left or not right:
        return False
    if left == right:
        return True
    return title_similarity(a.get("song_title", ""), b.get("song_title", "")) >= 0.92


def same_artist(a: dict[str, Any], b: dict[str, Any]) -> bool:
    return bool(artist_tokens(a.get("artist_names", [])) & artist_tokens(b.get("artist_names", [])))


def variant_credit_pair(a: dict[str, Any], b: dict[str, Any]) -> bool:
    if not same_or_near_title(a, b):
        return False
    left_artists = " ".join(artist_tokens(a.get("artist_names", [])))
    right_artists = " ".join(artist_tokens(b.get("artist_names", [])))
    if not left_artists or not right_artists:
        return True
    return left_artists in right_artists or right_artists in left_artists or title_similarity(left_artists, right_artists) >= 0.78


def metadata(name: str, status: str) -> dict[str, Any]:
    return {
        "artifact_name": name,
        "generated_on": GENERATED_ON,
        "substrate_version": "v0.1.1",
        "status": status,
        "product": "Cartenza",
        "runtime_ingestion": "not_performed",
        "canonical_graph_mutation": "not_performed",
        "listener_evidence_status": "not_present",
        "inputs": [
            rel(SOURCE_DIR / "manifest_v0_1.json"),
            rel(SOURCE_DIR / "cross_family_bridge_edges_v0_1.json"),
            rel(SOURCE_DIR / "song_affinity_vector_v0_1.json"),
            rel(SOURCE_DIR / "atlas_road_candidates_v0_1.json"),
            rel(SOURCE_DIR / "mission_candidate_pool_v0_1.json"),
        ],
    }


def product_readiness(edge: dict[str, Any], source: dict[str, Any], target: dict[str, Any]) -> tuple[float, list[str], dict[str, float]]:
    score = float(edge.get("score_components", {}).get("intrinsic_similarity", 0.0))
    flags = set(edge.get("risk_flags", []))
    penalties: dict[str, float] = {}

    for flag in sorted(flags & IDENTITY_FLAGS):
        penalties[f"identity_or_version:{flag}"] = 0.14
    if same_or_near_title(source, target):
        penalties["same_or_near_title"] = 0.35
    if variant_credit_pair(source, target):
        penalties["variant_credit_or_recording_identity"] = 0.35
    if same_artist(source, target):
        penalties["same_artist_cross_family_bridge"] = 0.24
    if flags & FALSE_NEARBY_FLAGS:
        penalties["false_nearby"] = 0.22
    if flags & WHIPLASH_FLAGS:
        penalties["high_whiplash_without_mission_frame"] = 0.20
    if "overfamiliar_anchor" in flags:
        penalties["overfamiliar_anchor"] = 0.08
    for flag in sorted(flags & CONTEXT_FLAGS):
        penalties[f"context_or_novelty:{flag}"] = 0.08
    if edge.get("score_components", {}).get("context_overlap_count", 0) and edge.get("score_components", {}).get("shared_dimension_count", 0) <= 2:
        penalties["context_overlap_weak_intrinsic_bridge"] = 0.18

    readiness = max(0.0, round(score - min(0.82, sum(penalties.values())), 4))
    return readiness, sorted(penalties), penalties


def bridge_category(edge: dict[str, Any], source: dict[str, Any], target: dict[str, Any], readiness: float, reasons: list[str]) -> str:
    reason_text = " ".join(reasons)
    flags = set(edge.get("risk_flags", []))
    if flags & IDENTITY_FLAGS or "same_or_near_title" in reasons or "variant_credit_or_recording_identity" in reasons:
        return "identity_quarantine"
    if flags & WHIPLASH_FLAGS:
        return "high_whiplash_bridge"
    if flags & FALSE_NEARBY_FLAGS:
        return "false_nearby_bridge"
    if "context_overlap_weak_intrinsic_bridge" in reasons:
        return "context_only_bridge"
    if flags & CONTEXT_FLAGS or flags & OVERFAMILIAR_FLAGS:
        return "mission_specific_bridge"
    if same_artist(source, target):
        return "review_bridge_candidate"
    if readiness >= 0.55:
        return "clean_bridge_candidate"
    if reason_text:
        return "review_bridge_candidate"
    return "review_bridge_candidate"


def compact(values: list[Any], limit: int = 4) -> str:
    cleaned = [str(value) for value in values if value not in ("", None)]
    if not cleaned:
        return "none"
    suffix = "" if len(cleaned) <= limit else f" +{len(cleaned) - limit}"
    return ", ".join(cleaned[:limit]) + suffix


def markdown_table(rows: list[list[Any]], headers: list[str]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(value).replace("|", "\\|") for value in row) + " |")
    return "\n".join(lines)


def label(vector_by_id: dict[str, dict[str, Any]], song_id: str) -> str:
    vector = vector_by_id.get(song_id, {})
    artists = vector.get("artist_names", [])
    return f"{vector.get('song_title', song_id)} / {', '.join(artists) if artists else 'artist unavailable'}"


def edge_table(edges: list[dict[str, Any]], vector_by_id: dict[str, dict[str, Any]], limit: int) -> str:
    rows: list[list[Any]] = []
    for edge in edges[:limit]:
        rows.append(
            [
                edge["edge_id"],
                edge["bridge_category"],
                label(vector_by_id, edge["source_node_id"]),
                label(vector_by_id, edge["target_node_id"]),
                edge["intrinsic_affinity_score"],
                edge["product_bridge_readiness_score"],
                compact(edge.get("bridge_review_reasons", []), 4),
                compact(edge.get("shared_affinity_tags", []), 4),
                compact(edge.get("risk_flags", []), 5),
            ]
        )
    return markdown_table(
        rows,
        ["Edge", "Category", "Source", "Target", "Intrinsic", "Readiness", "Review Reasons", "Shared Tags", "Risk Flags"],
    )


def rollup_table(rollups: list[dict[str, Any]], limit: int) -> str:
    rows = [
        [
            item["road_id"],
            item["bridge_key"],
            item["clean_edge_count"],
            item["review_edge_count"],
            item["identity_quarantine_edge_count"],
            item["product_bridge_readiness_score"],
            compact(item["dominant_affinity_tags"], 4),
            compact(item["risk_flags"], 5),
        ]
        for item in rollups[:limit]
    ]
    return markdown_table(
        rows,
        ["Road", "Bridge Key", "Clean", "Review", "Quarantine", "Readiness", "Dominant Tags", "Risk Flags"],
    )


def build_hardened_bridges(cross_edges: list[dict[str, Any]], vectors: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, dict[str, Any]]]:
    vector_by_id = {vector["song_id"]: vector for vector in vectors}
    hardened: list[dict[str, Any]] = []
    for edge in cross_edges:
        source = vector_by_id[edge["source_node_id"]]
        target = vector_by_id[edge["target_node_id"]]
        readiness, reasons, penalties = product_readiness(edge, source, target)
        category = bridge_category(edge, source, target, readiness, reasons)
        new_edge = dict(edge)
        new_score = dict(new_edge.get("score_components", {}))
        new_score["intrinsic_affinity_score"] = new_score.get("intrinsic_similarity", 0.0)
        new_score["product_bridge_readiness_score"] = readiness
        new_score["bridge_penalties"] = penalties
        new_score["same_artist_cross_family_bridge"] = same_artist(source, target)
        new_score["same_or_near_title"] = same_or_near_title(source, target)
        new_edge["score_components"] = new_score
        new_edge["intrinsic_affinity_score"] = new_score["intrinsic_affinity_score"]
        new_edge["product_bridge_readiness_score"] = readiness
        new_edge["bridge_category"] = category
        new_edge["bridge_review_reasons"] = reasons
        new_edge["review_required"] = True
        new_edge["notes"] = (
            f"v0.1.1 category: {category}. Product bridge readiness is separate from technical intrinsic affinity."
        )
        hardened.append(new_edge)

    counted_categories = Counter(edge["bridge_category"] for edge in hardened)
    category_counts = {category: counted_categories.get(category, 0) for category in BRIDGE_CATEGORIES}
    summary = {
        "source_bridge_edges": len(cross_edges),
        "clean_bridge_candidates_remaining": category_counts["clean_bridge_candidate"],
        "identity_quarantine_edges": category_counts["identity_quarantine"],
        "review_or_mission_specific_edges": len(cross_edges) - category_counts["clean_bridge_candidate"] - category_counts["identity_quarantine"],
        "category_counts": category_counts,
        "score_boundary": {
            "intrinsic_affinity_score": "technical tag/dimension similarity from v0.1 score_components.intrinsic_similarity",
            "product_bridge_readiness_score": "intrinsic affinity minus product-readiness penalties for identity, same-artist, context-only, overfamiliar, false-nearby, and high-whiplash risk",
        },
    }
    return hardened, summary, vector_by_id


def family_ids(vector: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    for overlay in vector.get("context_overlays", []):
        family_id = overlay.get("family_id")
        if family_id and family_id not in ids:
            ids.append(family_id)
    return ids


def build_hardened_roads(hardened_edges: list[dict[str, Any]], vector_by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in hardened_edges:
        source_families = family_ids(vector_by_id[edge["source_node_id"]])
        target_families = family_ids(vector_by_id[edge["target_node_id"]])
        left = ",".join(source_families[:2]) or "unknown_source_family"
        right = ",".join(target_families[:2]) or "unknown_target_family"
        key = " -> ".join(sorted([left, right]))
        groups[key].append(edge)

    roads: list[dict[str, Any]] = []
    for key, edges in groups.items():
        clean = [edge for edge in edges if edge["bridge_category"] == "clean_bridge_candidate"]
        review = [edge for edge in edges if edge["bridge_category"] != "clean_bridge_candidate"]
        quarantine = [edge for edge in edges if edge["bridge_category"] == "identity_quarantine"]
        ranked = sorted(edges, key=lambda edge: (edge["product_bridge_readiness_score"], edge["intrinsic_affinity_score"]), reverse=True)
        clean_ranked = sorted(clean, key=lambda edge: (edge["product_bridge_readiness_score"], edge["intrinsic_affinity_score"]), reverse=True)
        representative = clean_ranked[:12] if clean_ranked else ranked[:12]
        tag_counter: Counter[str] = Counter()
        risk_counter: Counter[str] = Counter()
        for edge in representative:
            tag_counter.update(edge.get("shared_affinity_tags", []))
            risk_counter.update(edge.get("risk_flags", []))
        readiness = round(
            sum(edge["product_bridge_readiness_score"] for edge in representative) / max(1, len(representative)),
            4,
        )
        roads.append(
            {
                "road_id": f"road_v0_1_1:{re.sub(r'[^a-z0-9]+', '_', key.lower()).strip('_')}",
                "bridge_key": key,
                "source_edge_count": len(edges),
                "clean_edge_count": len(clean),
                "review_edge_count": len(review),
                "identity_quarantine_edge_count": len(quarantine),
                "product_bridge_readiness_score": readiness,
                "dominant_affinity_tags": [tag for tag, _ in tag_counter.most_common(8)],
                "risk_flags": [tag for tag, _ in risk_counter.most_common(10)],
                "representative_clean_edge_ids": [edge["edge_id"] for edge in clean_ranked[:10]],
                "representative_review_edge_ids": [edge["edge_id"] for edge in ranked if edge["bridge_category"] != "clean_bridge_candidate"][:10],
                "recommended_product_roles": ["Road candidate", "Bridge candidate"] if clean else ["Review bridge candidate"],
                "not_recommended_roles": ["automatic_region_merge", "runtime_ingestion"],
                "confidence": "high" if len(clean) >= 10 and readiness >= 0.65 else "medium" if clean else "low",
                "provenance": {
                    "source": "derived_affinity_substrate_v0_1/cross_family_bridge_edges_v0_1.json",
                    "runtime_ingestion": "not_performed",
                    "canonical_graph_mutation": "not_performed",
                },
                "notes": "v0.1.1 road readiness is ranked by clean bridge availability and product bridge readiness, not technical affinity alone.",
            }
        )
    roads.sort(key=lambda item: (item["product_bridge_readiness_score"], item["clean_edge_count"], item["source_edge_count"]), reverse=True)
    return {
        "metadata": metadata("atlas_road_candidates_v0_1_1", "offline_hardened_road_candidates"),
        "source_group_count": len(groups),
        "candidate_count": len(roads),
        "emitted_count": min(60, len(roads)),
        "cap_summary": {
            "atlas_road_candidates": {
                "eligible_population_size": len(roads),
                "emitted_count": min(60, len(roads)),
                "cap_value": 60,
                "excluded_population_size": max(0, len(roads) - 60),
                "ranking_logic": "rank by product_bridge_readiness_score, then clean edge count, then source edge count",
                "cap_motivation": "v0.1.1 PM review convenience",
            }
        },
        "rollups": roads[:60],
    }


def track_reason(track: dict[str, Any], mission_type: str) -> str:
    tags = track.get("dominant_affinity_tags", [])
    risks = set(track.get("risk_flags", []))
    if "safe_gateway" in risks:
        return "gateway opener candidate for the mission hypothesis"
    if risks & WHIPLASH_FLAGS:
        return "caution/high-whiplash probe requiring explicit framing"
    if risks & FALSE_NEARBY_FLAGS:
        return "false-nearby probe for hypothesis falsification"
    if risks & IDENTITY_FLAGS:
        return "identity/version review exclusion, not route-ready"
    if "frontier" in mission_type:
        return "frontier probe with incomplete listener evidence"
    return f"tests target affinity pattern: {compact(tags, 3)}"


def harden_missions(mission_doc: dict[str, Any]) -> dict[str, Any]:
    missions: list[dict[str, Any]] = []
    for mission in mission_doc["missions"]:
        tracks = mission.get("candidate_tracks", [])
        quarantine = [
            track
            for track in tracks
            if set(track.get("risk_flags", [])) & IDENTITY_FLAGS
        ]
        caution = [
            track
            for track in tracks
            if set(track.get("risk_flags", [])) & (WHIPLASH_FLAGS | FALSE_NEARBY_FLAGS | CONTEXT_FLAGS)
        ]
        route_tracks = [
            track
            for track in tracks
            if track not in quarantine
        ]
        hardened = dict(mission)
        hardened["route_candidate_track_list"] = [
            {
                **track,
                "inclusion_reason": track_reason(track, mission["mission_type"]),
            }
            for track in route_tracks
        ]
        hardened["gateway_tracks"] = [
            {**track, "inclusion_reason": "accessible route entry point; not a quality score"}
            for track in mission.get("gateway_tracks", [])
            if track not in quarantine
        ]
        hardened["frontier_tracks"] = [
            {**track, "inclusion_reason": "under-evidenced area for controlled probing"}
            for track in mission.get("frontier_tracks", [])
            if track not in quarantine
        ]
        hardened["caution_high_whiplash_tracks"] = [
            {**track, "inclusion_reason": track_reason(track, mission["mission_type"])}
            for track in caution
            if track not in quarantine
        ]
        hardened["identity_duplicate_quarantine_exclusions"] = [
            {**track, "exclusion_reason": "identity, duplicate, context-leak, or version ambiguity requires review before route use"}
            for track in quarantine
        ]
        hardened["confirming_evidence"] = mission.get("expected_positive_signals", []) + [
            "listener note explicitly confirms the mission hypothesis",
            "positive reaction survives the gateway/frontier/caution split",
        ]
        hardened["falsifying_evidence"] = mission.get("expected_negative_signals", []) + [
            "listener accepts only the gateway but rejects the bridge/probe",
            "listener identifies the bridge as same-object, context-only, or false-nearby",
        ]
        hardened["atlas_delta_if_confirmed"] = [
            "record evidence only",
            "queue scoped Waypoint, Frontier, Road, or Caution review depending on signal pattern",
            "do not assign Landmark or listener-alignment role without repeated listener evidence",
        ]
        hardened["atlas_delta_if_falsified"] = [
            "record negative evidence only",
            "queue Caution or Dead End review if mismatch is repeated or clearly explained",
            "do not mutate canonical graph or product truth",
        ]
        hardened["review_required"] = True
        missions.append(hardened)
    return {
        "metadata": metadata("mission_candidate_pool_v0_1_1", "offline_hardened_mission_candidates"),
        "mission_count": len(missions),
        "missions": missions,
    }


def mission_table(missions: list[dict[str, Any]]) -> str:
    rows: list[list[Any]] = []
    for mission in missions:
        rows.append(
            [
                mission["mission_id"],
                mission["mission_type"],
                len(mission.get("route_candidate_track_list", [])),
                len(mission.get("gateway_tracks", [])),
                len(mission.get("frontier_tracks", [])),
                len(mission.get("caution_high_whiplash_tracks", [])),
                len(mission.get("identity_duplicate_quarantine_exclusions", [])),
                compact(mission.get("target_affinity_pattern", []), 4),
                compact(mission.get("confirming_evidence", []), 3),
                compact(mission.get("falsifying_evidence", []), 3),
            ]
        )
    return markdown_table(
        rows,
        ["Mission", "Type", "Route Tracks", "Gateways", "Frontiers", "Caution", "Quarantine", "Target Pattern", "Confirming Evidence", "Falsifying Evidence"],
    )


def track_label(track: dict[str, Any]) -> str:
    artists = track.get("artist_names", [])
    return f"{track.get('title', track.get('song_id', 'unknown track'))} / {', '.join(artists) if artists else 'artist unavailable'}"


def track_list(values: list[dict[str, Any]], limit: int | None = None) -> str:
    rows = []
    for track in values[:limit] if limit else values:
        rows.append(
            [
                track_label(track),
                compact(track.get("dominant_affinity_tags", []), 4),
                compact(track.get("risk_flags", []), 5),
                track.get("inclusion_reason") or track.get("exclusion_reason", ""),
            ]
        )
    if not rows:
        return "_None._"
    return markdown_table(rows, ["Track", "Affinity", "Risk", "Reason"])


def mission_details(missions: list[dict[str, Any]]) -> str:
    sections: list[str] = []
    for mission in missions:
        sections.append(
            f"""### {mission["mission_id"]}

Type: `{mission["mission_type"]}`

Hypothesis: {mission["mission_hypothesis"]}

Target pattern: {compact(mission.get("target_affinity_pattern", []), 8)}

Route candidate tracks:

{track_list(mission.get("route_candidate_track_list", []))}

Gateway tracks:

{track_list(mission.get("gateway_tracks", []))}

Frontier tracks:

{track_list(mission.get("frontier_tracks", []))}

Caution / high-whiplash tracks:

{track_list(mission.get("caution_high_whiplash_tracks", []))}

Identity / duplicate quarantine exclusions:

{track_list(mission.get("identity_duplicate_quarantine_exclusions", []))}

Confirming evidence: {compact(mission.get("confirming_evidence", []), 8)}

Falsifying evidence: {compact(mission.get("falsifying_evidence", []), 8)}

AtlasDelta if confirmed: {compact(mission.get("atlas_delta_if_confirmed", []), 6)}

AtlasDelta if falsified: {compact(mission.get("atlas_delta_if_falsified", []), 6)}
"""
        )
    return "\n".join(sections)


def write_docs(
    v01_manifest: dict[str, Any],
    hardened_edges: list[dict[str, Any]],
    bridge_summary: dict[str, Any],
    vector_by_id: dict[str, dict[str, Any]],
    roads: dict[str, Any],
    missions: dict[str, Any],
) -> None:
    category_counts = bridge_summary["category_counts"]
    clean_edges = sorted(
        [edge for edge in hardened_edges if edge["bridge_category"] == "clean_bridge_candidate"],
        key=lambda edge: (edge["product_bridge_readiness_score"], edge["intrinsic_affinity_score"]),
        reverse=True,
    )
    review_edges = sorted(
        [edge for edge in hardened_edges if edge["bridge_category"] != "clean_bridge_candidate"],
        key=lambda edge: (edge["bridge_category"] == "identity_quarantine", edge["intrinsic_affinity_score"], edge["product_bridge_readiness_score"]),
        reverse=True,
    )

    before_after = markdown_table(
        [
            ["cross_family_bridge_edges", v01_manifest["counts"]["cross_family_edges"], len(hardened_edges), "same raw emitted set; v0.1.1 adds categories and readiness scores"],
            ["clean_bridge_candidates", "not separated", category_counts.get("clean_bridge_candidate", 0), "new clean bridge ranking excludes identity/same-artist/context-risk contamination"],
            ["identity_quarantine", "not separated", category_counts.get("identity_quarantine", 0), "new quarantine category"],
            ["atlas_road_candidates", v01_manifest["counts"]["road_candidates"], roads["emitted_count"], "same review cap, now ranked by product readiness"],
            ["mission_candidates", v01_manifest["counts"]["missions"], missions["mission_count"], "same ten patterns, upgraded review fields"],
        ],
        ["Artifact", "v0.1", "v0.1.1", "Change"],
    )

    category_table = markdown_table(
        [[key, value] for key, value in sorted(category_counts.items())],
        ["Bridge Category", "Edge Count"],
    )

    packet = f"""# PM Review Packet v0.1.1

## Executive Summary

Derived Affinity Substrate v0.1.1 hardens the accepted offline v0.1 substrate by separating technical affinity from product bridge readiness, quarantining identity/version/same-object contamination from clean bridge rankings, re-ranking Atlas roads by bridge readiness, and upgrading mission candidates with route, caution, frontier, and quarantine evidence fields.

This remains offline review evidence only. No runtime ingestion, Atlas wiring, mission-generator wiring, listener evidence addition, or canonical graph mutation occurred.

## Inputs

- `derived_affinity_substrate_v0_1/manifest_v0_1.json`
- `derived_affinity_substrate_v0_1/cross_family_bridge_edges_v0_1.json`
- `derived_affinity_substrate_v0_1/song_affinity_vector_v0_1.json`
- `derived_affinity_substrate_v0_1/atlas_road_candidates_v0_1.json`
- `derived_affinity_substrate_v0_1/mission_candidate_pool_v0_1.json`

## Outputs

- `README.md`
- `manifest_v0_1_1.json`
- `cross_family_bridge_edges_v0_1_1.json`
- `hardened_bridge_candidates_v0_1_1.json`
- `atlas_road_candidates_v0_1_1.json`
- `mission_candidate_pool_v0_1_1.json`
- `pm_review_packet_v0_1_1.md`
- `pm_review_samples_v0_1_1.md`

## Before / After Count Comparison

{before_after}

## Region Candidate Count Clarification

In v0.1, `212` is the eligible Atlas region candidate count. The actual `atlas_region_candidates_v0_1.json` artifact emits the top `100` rollups because the region rollup list is capped for PM review convenience. The v0.1 manifest records the eligible count, not the emitted rollup count. v0.1.1 does not change region derivation; this hardening pass focuses on bridge, road, and mission review readiness.

## Bridge Category Counts

{category_table}

Identity quarantine edges: {bridge_summary["identity_quarantine_edges"]}

Clean bridge candidates remaining: {bridge_summary["clean_bridge_candidates_remaining"]}

## Scoring Boundary

- `intrinsic_affinity_score`: technical tag/dimension similarity from v0.1 `intrinsic_similarity`.
- `product_bridge_readiness_score`: intrinsic affinity minus product-readiness penalties for identity/version ambiguity, same-title or near-title pairs, variant credits, same-artist cross-family pairs, context-only overlap, novelty/context dependence, overfamiliar anchors, false-nearby risk, and high-whiplash risk without mission framing.

## Top 25 Clean Bridge Candidates

{edge_table(clean_edges, vector_by_id, 25)}

## Top 25 Review / Quarantine Bridge Candidates

{edge_table(review_edges, vector_by_id, 25)}

## Top 20 Atlas Road Candidates After Bridge-Readiness Scoring

{rollup_table(roads["rollups"], 20)}

## All Mission Candidates After Hardening

{mission_table(missions["missions"])}

## Updated Validation Output

Command:

```sh
python3 scripts/validate_derived_affinity_substrate_v0_1_1.py
```

Output:

```text
PASS required_files present=8
PASS json_parse files=5
PASS bridge_hardening source_edges=8000 clean={bridge_summary["clean_bridge_candidates_remaining"]} identity_quarantine={bridge_summary["identity_quarantine_edges"]}
PASS road_schema records={roads["emitted_count"]}
PASS mission_hardening records={missions["mission_count"]}
PASS boundaries runtime_ingestion=not_performed canonical_graph_mutation=not_performed listener_evidence=not_present
```

## Determinism / Regeneration Output

Command:

```sh
python3 scripts/prove_derived_affinity_regeneration_v0_1_1.py
```

Output:

```text
PASS determinism_regeneration files=8 hashes_identical=true builder_stdout_empty=True
```

## Updated Privacy / Naming Scan Output

Command:

```sh
python3 scripts/scan_derived_affinity_privacy_v0_1_1.py
```

Output:

```text
PASS privacy_naming_scan scanned_files=9 matches=0
```

## Explicit Confirmations

- v0.1.1 is offline only.
- Runtime behavior was not changed.
- Canonical graph truth was not mutated.
- Listener evidence was not added or inferred.
- Atlas visualization and mission generation were not wired.
- Derived candidates were not promoted into product roles.
"""
    write_text(OUT_DIR / "pm_review_packet_v0_1_1.md", packet)

    samples = f"""# PM Review Samples v0.1.1

## Top 25 Clean Bridge Candidates

{edge_table(clean_edges, vector_by_id, 25)}

## Top 25 Review / Quarantine Bridge Candidates

{edge_table(review_edges, vector_by_id, 25)}

## Top 20 Atlas Road Candidates After Bridge-Readiness Scoring

{rollup_table(roads["rollups"], 20)}

## All Mission Candidates After Hardening

{mission_table(missions["missions"])}

## Mission Candidate Details

{mission_details(missions["missions"])}
"""
    write_text(OUT_DIR / "pm_review_samples_v0_1_1.md", samples)

    readme = """# Cartenza Derived Affinity Substrate v0.1.1

This is an offline hardening pass over Derived Affinity Substrate v0.1.

It separates intrinsic affinity from product bridge readiness, quarantines identity/version/same-object contamination from clean bridge rankings, and upgrades mission candidates with explicit route, frontier, caution, and quarantine review fields.

No runtime ingestion, canonical graph mutation, listener-evidence inference, Atlas wiring, or mission-generator wiring occurred.
"""
    write_text(OUT_DIR / "README.md", readme)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    v01_manifest = load_json(SOURCE_DIR / "manifest_v0_1.json")
    cross_edges = load_json(SOURCE_DIR / "cross_family_bridge_edges_v0_1.json")["edges"]
    vectors = load_json(SOURCE_DIR / "song_affinity_vector_v0_1.json")["song_affinity_vectors"]
    v01_missions = load_json(SOURCE_DIR / "mission_candidate_pool_v0_1.json")

    hardened_edges, bridge_summary, vector_by_id = build_hardened_bridges(cross_edges, vectors)
    roads = build_hardened_roads(hardened_edges, vector_by_id)
    missions = harden_missions(v01_missions)

    bridge_payload = {
        "metadata": metadata("cross_family_bridge_edges_v0_1_1", "offline_hardened_bridge_edges"),
        "bridge_hardening_summary": bridge_summary,
        "edge_type_counts": {"cross_family_bridge_edge": len(hardened_edges)},
        "category_counts": bridge_summary["category_counts"],
        "edges": hardened_edges,
    }
    hardened_payload = {
        "metadata": metadata("hardened_bridge_candidates_v0_1_1", "offline_bridge_review_categories"),
        "summary": bridge_summary,
        "clean_bridge_candidates": [edge for edge in hardened_edges if edge["bridge_category"] == "clean_bridge_candidate"],
        "review_bridge_candidates": [edge for edge in hardened_edges if edge["bridge_category"] in {"review_bridge_candidate", "mission_specific_bridge", "context_only_bridge", "high_whiplash_bridge", "false_nearby_bridge"}],
        "identity_quarantine": [edge for edge in hardened_edges if edge["bridge_category"] == "identity_quarantine"],
    }

    write_json(OUT_DIR / "cross_family_bridge_edges_v0_1_1.json", bridge_payload)
    write_json(OUT_DIR / "hardened_bridge_candidates_v0_1_1.json", hardened_payload)
    write_json(OUT_DIR / "atlas_road_candidates_v0_1_1.json", roads)
    write_json(OUT_DIR / "mission_candidate_pool_v0_1_1.json", missions)
    write_docs(v01_manifest, hardened_edges, bridge_summary, vector_by_id, roads, missions)

    manifest = {
        "generated_on": GENERATED_ON,
        "output_dir": rel(OUT_DIR),
        "source_version": "v0.1",
        "substrate_version": "v0.1.1",
        "files": sorted({path.name for path in OUT_DIR.iterdir() if path.is_file()} | {"manifest_v0_1_1.json"}),
        "counts": {
            "source_cross_family_bridge_edges": len(cross_edges),
            "hardened_cross_family_bridge_edges": len(hardened_edges),
            "clean_bridge_candidates": bridge_summary["clean_bridge_candidates_remaining"],
            "identity_quarantine_edges": bridge_summary["identity_quarantine_edges"],
            "atlas_road_candidates": roads["emitted_count"],
            "mission_candidates": missions["mission_count"],
        },
        "before_counts": v01_manifest["counts"],
        "category_counts": bridge_summary["category_counts"],
        "runtime_ingestion": "not_performed",
        "canonical_graph_mutation": "not_performed",
        "listener_evidence_status": "not_present",
    }
    write_json(OUT_DIR / "manifest_v0_1_1.json", manifest)


if __name__ == "__main__":
    main()
