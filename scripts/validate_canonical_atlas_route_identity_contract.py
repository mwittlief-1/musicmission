#!/usr/bin/env python3
"""Validate the Alpha route identity/display contract against a candidate pool."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANDIDATE_POOL = REPO_ROOT / "data/alpha_consumable_layer/alpha_v0/sample_compact_candidate_pool_alpha_v0.json"
DEFAULT_CONTRACT = (
    REPO_ROOT
    / "data/atlas_schema/alpha_hardening/canonical_atlas_route_identity_contract_alpha_v0_1.json"
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Canonical/Atlas route identity contract fields.")
    parser.add_argument("--candidate-pool", type=Path, default=DEFAULT_CANDIDATE_POOL)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    args = parser.parse_args()

    candidate_pool = load_json(args.candidate_pool)
    contract = load_json(args.contract)
    findings = validate(candidate_pool, contract)

    if findings:
        print(f"ROUTE_IDENTITY_CONTRACT_VALIDATION_FAIL ({len(findings)} finding(s))")
        for finding in findings:
            print(f"- {finding}")
        return 1

    rows = flatten_candidates(candidate_pool)
    print("ROUTE_IDENTITY_CONTRACT_VALIDATION_PASS")
    print(f"candidate_pool={rel(args.candidate_pool)}")
    print(f"contract={rel(args.contract)}")
    print(f"route_ready_candidates={len(rows)}")
    print(f"object_types={dict(sorted(Counter(row.get('object_type') for row in rows).items()))}")
    print(f"candidate_ids={len({row['candidate_id'] for row in rows})}")
    print(f"dedupe_groups={len({row['dedupe_group'] for row in rows})}")
    return 0


def validate(candidate_pool: dict[str, Any], contract: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    rows = flatten_candidates(candidate_pool)
    if not rows:
        return ["candidate pool has no route candidates"]

    if contract.get("atlas_evidence_boundary", {}).get("candidate_pool_membership_is_taste_truth") is not False:
        findings.append("contract must state candidate_pool_membership_is_taste_truth=false")
    if contract.get("candidate_pool_source_rule", {}).get("route_items_must_come_from_supplied_candidate_pool") is not True:
        findings.append("contract must require route items to come from supplied candidate pool")
    if candidate_pool.get("graph_metadata_taste_truth") is not False:
        findings.append("candidate pool must mark graph_metadata_taste_truth=false")
    if candidate_pool.get("atlas_promotion_created") is not False:
        findings.append("candidate pool must mark atlas_promotion_created=false")

    candidate_ids: list[str] = []
    dedupe_groups: list[str] = []
    canonical_keys: list[str] = []
    display_keys: list[str] = []

    for row in rows:
        label = f"{row.get('source_pool', 'pool')}:{row.get('candidate_id', 'missing_candidate_id')}"
        required_fields = [
            "candidate_id",
            "candidate_role",
            "candidate_pool_behavior",
            "route_item_type",
            "object_type",
            "canonical_object_type",
            "canonical_entity_id",
            "display_name",
            "display_label",
            "credited_artist",
            "dedupe_group",
            "music_kit_search_hint",
            "music_object_ref",
            "route_item",
            "source_evidence_refs",
            "review_status",
        ]
        for field in required_fields:
            if field not in row or row[field] in (None, "", []):
                findings.append(f"{label} missing required field {field}")

        object_type = row.get("object_type")
        route_item_type = row.get("route_item_type")
        canonical_object_type = row.get("canonical_object_type")
        if object_type not in {"track", "album"}:
            findings.append(f"{label} object_type must be track or album, got {object_type}")
        if route_item_type != object_type:
            findings.append(f"{label} route_item_type must equal object_type")
        if object_type == "track" and canonical_object_type != "song_recording":
            findings.append(f"{label} track route item must map to canonical song_recording")
        if object_type == "album" and canonical_object_type != "album":
            findings.append(f"{label} album route item must map to canonical album")
        if row.get("artist_level_candidate") is not False:
            findings.append(f"{label} artist_level_candidate must be false")
        if row.get("playable_route_ready") is not True:
            findings.append(f"{label} playable_route_ready must be true")
        if row.get("review_status") != "approved":
            findings.append(f"{label} review_status must be approved")
        if row.get("eligible_for_openai") is not True or row.get("eligible_for_supabase") is not True:
            findings.append(f"{label} must be eligible_for_openai and eligible_for_supabase")

        music_ref = row.get("music_object_ref") if isinstance(row.get("music_object_ref"), dict) else {}
        if object_type == "track" and music_ref.get("object_type") != "song_recording":
            findings.append(f"{label} track music_object_ref.object_type must be song_recording")
        if object_type == "album" and music_ref.get("object_type") != "album":
            findings.append(f"{label} album music_object_ref.object_type must be album")
        if music_ref.get("ref_source") != "canonical_graph":
            findings.append(f"{label} music_object_ref.ref_source must be canonical_graph")
        if music_ref.get("resolution_state") != "resolved":
            findings.append(f"{label} music_object_ref.resolution_state must be resolved")

        route_item = row.get("route_item") if isinstance(row.get("route_item"), dict) else {}
        if route_item.get("route_item_type") != object_type:
            findings.append(f"{label} route_item.route_item_type must equal object_type")
        if route_item.get("canonical_entity_id") != row.get("canonical_entity_id"):
            findings.append(f"{label} route_item canonical_entity_id mismatch")
        if not route_item.get("music_kit_search_hint"):
            findings.append(f"{label} route_item missing music_kit_search_hint")

        display_label = str(row.get("display_label") or "")
        display_name = str(row.get("display_name") or "")
        credited_artist = str(row.get("credited_artist") or "")
        internal_values = {str(row.get("candidate_id")), str(row.get("canonical_entity_id")), str(row.get("dedupe_group"))}
        if display_label in internal_values or display_name in internal_values or credited_artist in internal_values:
            findings.append(f"{label} display fields must not prefer internal IDs/slugs")

        candidate_ids.append(str(row.get("candidate_id")))
        dedupe_groups.append(str(row.get("dedupe_group")))
        canonical_keys.append(f"{canonical_object_type}:{row.get('canonical_entity_id')}")
        display_keys.append(normalized_display_key(object_type, credited_artist, display_label or display_name))

    findings.extend(duplicate_findings("candidate_id", candidate_ids))
    findings.extend(duplicate_findings("dedupe_group", dedupe_groups))
    findings.extend(duplicate_findings("canonical route key", canonical_keys))
    findings.extend(duplicate_findings("candidate display key", display_keys))

    return findings


def flatten_candidates(candidate_pool: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    pools = candidate_pool.get("pools") or {}
    if isinstance(pools, dict):
        for pool_name, pool_rows in pools.items():
            if not isinstance(pool_rows, list):
                continue
            for row in pool_rows:
                if isinstance(row, dict):
                    row = dict(row)
                    row.setdefault("source_pool", pool_name)
                    rows.append(row)
    if isinstance(candidate_pool.get("candidates"), list):
        for row in candidate_pool["candidates"]:
            if isinstance(row, dict):
                rows.append(row)
    return rows


def duplicate_findings(label: str, values: list[str]) -> list[str]:
    counts = Counter(value for value in values if value and value != "None")
    return [f"duplicate {label}: {value}" for value, count in sorted(counts.items()) if count > 1]


def normalized_display_key(object_type: Any, artist: str, title: str) -> str:
    return ":".join([normalize(str(object_type or "")), normalize(artist), normalize(title)])


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    sys.exit(main())
