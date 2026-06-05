#!/usr/bin/env python3
"""Validate the Cartenza Derived Affinity Substrate v0.1.1 hardening package."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "derived_affinity_substrate_v0_1_1"

REQUIRED_FILES = [
    "README.md",
    "manifest_v0_1_1.json",
    "cross_family_bridge_edges_v0_1_1.json",
    "hardened_bridge_candidates_v0_1_1.json",
    "atlas_road_candidates_v0_1_1.json",
    "mission_candidate_pool_v0_1_1.json",
    "pm_review_packet_v0_1_1.md",
    "pm_review_samples_v0_1_1.md",
]

BRIDGE_CATEGORIES = {
    "clean_bridge_candidate",
    "review_bridge_candidate",
    "identity_quarantine",
    "context_only_bridge",
    "high_whiplash_bridge",
    "false_nearby_bridge",
    "mission_specific_bridge",
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

    bridge_doc = json_docs["cross_family_bridge_edges_v0_1_1.json"]
    hardened_doc = json_docs["hardened_bridge_candidates_v0_1_1.json"]
    roads = json_docs["atlas_road_candidates_v0_1_1.json"]
    missions = json_docs["mission_candidate_pool_v0_1_1.json"]
    manifest = json_docs["manifest_v0_1_1.json"]

    edges = bridge_doc["edges"]
    category_counts: dict[str, int] = bridge_doc["category_counts"]
    if sum(category_counts.values()) != len(edges):
        print("FAIL bridge_hardening category_count_mismatch")
        return 1
    bad_categories = [edge["edge_id"] for edge in edges if edge.get("bridge_category") not in BRIDGE_CATEGORIES]
    missing_scores = [
        edge["edge_id"]
        for edge in edges
        if "intrinsic_affinity_score" not in edge or "product_bridge_readiness_score" not in edge
    ]
    if bad_categories or missing_scores:
        print(f"FAIL bridge_hardening bad_categories={len(bad_categories)} missing_scores={len(missing_scores)}")
        return 1
    clean = len(hardened_doc["clean_bridge_candidates"])
    quarantine = len(hardened_doc["identity_quarantine"])
    if clean != category_counts.get("clean_bridge_candidate", 0) or quarantine != category_counts.get("identity_quarantine", 0):
        print("FAIL bridge_hardening split_counts_mismatch")
        return 1
    print(f"PASS bridge_hardening source_edges={len(edges)} clean={clean} identity_quarantine={quarantine}")

    road_missing = [
        road["road_id"]
        for road in roads["rollups"]
        if "product_bridge_readiness_score" not in road or "clean_edge_count" not in road or "identity_quarantine_edge_count" not in road
    ]
    if road_missing:
        print(f"FAIL road_schema missing_records={len(road_missing)}")
        return 1
    print(f"PASS road_schema records={len(roads['rollups'])}")

    mission_missing = []
    for mission in missions["missions"]:
        for field in (
            "route_candidate_track_list",
            "gateway_tracks",
            "frontier_tracks",
            "caution_high_whiplash_tracks",
            "identity_duplicate_quarantine_exclusions",
            "confirming_evidence",
            "falsifying_evidence",
            "atlas_delta_if_confirmed",
            "atlas_delta_if_falsified",
        ):
            if field not in mission:
                mission_missing.append(mission["mission_id"])
                break
    if mission_missing:
        print(f"FAIL mission_hardening missing_records={len(mission_missing)}")
        return 1
    print(f"PASS mission_hardening records={len(missions['missions'])}")

    if manifest["counts"]["hardened_cross_family_bridge_edges"] != len(edges):
        print("FAIL manifest_counts bridge_count_mismatch")
        return 1
    for doc in (bridge_doc, hardened_doc, roads, missions):
        metadata = doc["metadata"]
        if metadata.get("runtime_ingestion") != "not_performed":
            print("FAIL runtime_boundary")
            return 1
        if metadata.get("canonical_graph_mutation") != "not_performed":
            print("FAIL canonical_boundary")
            return 1
        if metadata.get("listener_evidence_status") != "not_present":
            print("FAIL listener_evidence_boundary")
            return 1
    print("PASS boundaries runtime_ingestion=not_performed canonical_graph_mutation=not_performed listener_evidence=not_present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
