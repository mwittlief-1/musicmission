#!/usr/bin/env python3
"""Validate the Cartenza Derived Affinity Substrate v0.1 package."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "derived_affinity_substrate_v0_1"

REQUIRED_FILES = [
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

EDGE_FIELDS = {
    "edge_id",
    "edge_type",
    "source_node_id",
    "target_node_id",
    "source_node_type",
    "target_node_type",
    "shared_affinity_tags",
    "context_overlay_tags",
    "risk_flags",
    "confidence",
    "score_components",
    "provenance",
    "review_required",
    "notes",
}

ROLLUP_FIELDS = {
    "rollup_id",
    "rollup_type",
    "node_ids",
    "dominant_affinity_tags",
    "secondary_affinity_tags",
    "context_overlays",
    "risk_flags",
    "sample_size",
    "confidence",
    "recommended_product_roles",
    "not_recommended_roles",
    "overgeneralization_risks",
    "provenance",
    "notes",
}

MISSION_FIELDS = {
    "mission_id",
    "mission_type",
    "mission_hypothesis",
    "target_affinity_pattern",
    "candidate_tracks",
    "gateway_tracks",
    "frontier_tracks",
    "risk_controls",
    "expected_positive_signals",
    "expected_negative_signals",
    "reaction_prompt_candidates",
    "atlas_delta_plan",
    "confidence",
    "review_required",
}


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    missing = [name for name in REQUIRED_FILES if not (PACKAGE / name).exists()]
    if missing:
        print(f"FAIL required_files missing={','.join(missing)}")
        return 1
    print(f"PASS required_files present={len(REQUIRED_FILES)}")

    json_docs: dict[str, Any] = {}
    for path in sorted(PACKAGE.glob("*.json")):
        json_docs[path.name] = load_json(path)
    print(f"PASS json_parse files={len(json_docs)}")

    manifest = json_docs["manifest_v0_1.json"]
    counts = manifest["counts"]
    expected_counts = {
        "song_vectors": len(json_docs["song_affinity_vector_v0_1.json"]["song_affinity_vectors"]),
        "song_song_edges": len(json_docs["song_song_candidate_edges_v0_1.json"]["edges"]),
        "cross_family_edges": len(json_docs["cross_family_bridge_edges_v0_1.json"]["edges"]),
        "missions": len(json_docs["mission_candidate_pool_v0_1.json"]["missions"]),
        "region_candidates": json_docs["atlas_region_candidates_v0_1.json"]["candidate_count"],
        "road_candidates": json_docs["atlas_road_candidates_v0_1.json"]["candidate_count"],
        "frontier_candidates": json_docs["atlas_frontier_candidates_v0_1.json"]["candidate_count"],
        "dead_end_caution_candidates": json_docs["atlas_dead_end_caution_candidates_v0_1.json"]["candidate_count"],
    }
    if counts != expected_counts:
        print(f"FAIL manifest_counts expected={expected_counts} actual={counts}")
        return 1
    print(
        "PASS manifest_counts "
        + " ".join(f"{key}={value}" for key, value in sorted(counts.items()))
    )

    edges = json_docs["song_song_candidate_edges_v0_1.json"]["edges"] + json_docs["cross_family_bridge_edges_v0_1.json"]["edges"]
    edge_missing = sum(1 for edge in edges if EDGE_FIELDS - set(edge))
    listener_alignment = sum(1 for edge in edges if edge.get("edge_type") == "listener_alignment_edge")
    if edge_missing or listener_alignment:
        print(f"FAIL edge_schema missing_records={edge_missing} listener_alignment_edges={listener_alignment}")
        return 1
    print(f"PASS edge_schema records={len(edges)} missing_records=0 listener_alignment_edges=0")

    rollups: list[dict[str, Any]] = []
    vector_doc = json_docs["song_affinity_vector_v0_1.json"]
    rollups.extend(vector_doc["song_affinity_vectors"])
    for name in (
        "affinity_cluster_catalog_v0_1.json",
        "family_archetype_affinity_rollups_v0_1.json",
        "atlas_region_candidates_v0_1.json",
        "atlas_road_candidates_v0_1.json",
        "atlas_frontier_candidates_v0_1.json",
        "atlas_dead_end_caution_candidates_v0_1.json",
    ):
        doc = json_docs[name]
        for key in (
            "cluster_rollups",
            "cross_family_bridge_clusters",
            "risk_rollups",
            "gateway_rollups",
            "family_rollups",
            "archetype_rollups",
            "artist_rollups",
            "album_rollups",
            "rollups",
        ):
            rollups.extend(doc.get(key, []))
    rollup_missing = sum(1 for rollup in rollups if ROLLUP_FIELDS - set(rollup))
    if rollup_missing:
        print(f"FAIL rollup_schema records={len(rollups)} missing_records={rollup_missing}")
        return 1
    print(f"PASS rollup_schema records={len(rollups)} missing_records=0")

    missions = json_docs["mission_candidate_pool_v0_1.json"]["missions"]
    mission_missing = sum(1 for mission in missions if MISSION_FIELDS - set(mission))
    if mission_missing:
        print(f"FAIL mission_schema records={len(missions)} missing_records={mission_missing}")
        return 1
    print(f"PASS mission_schema records={len(missions)} missing_records=0")

    metadata_docs = [
        json_docs["song_affinity_vector_v0_1.json"]["metadata"],
        json_docs["song_song_candidate_edges_v0_1.json"]["metadata"],
        json_docs["cross_family_bridge_edges_v0_1.json"]["metadata"],
    ]
    if any(doc.get("runtime_ingestion") != "not_performed" for doc in metadata_docs):
        print("FAIL runtime_boundary")
        return 1
    if any(doc.get("canonical_graph_mutation") != "not_performed" for doc in metadata_docs):
        print("FAIL canonical_boundary")
        return 1
    print("PASS boundaries runtime_ingestion=not_performed canonical_graph_mutation=not_performed listener_evidence=not_present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
