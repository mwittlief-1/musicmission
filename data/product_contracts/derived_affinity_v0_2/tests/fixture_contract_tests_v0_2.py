#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


CONTRACT_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CONTRACT_DIR.parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from validate_derived_affinity_contracts_v0_2 import (  # noqa: E402
    ACCEPTED_SUBSTRATE_PREFIX,
    APPROVED_MISSION_TYPES,
    REQUIRED_ATLAS_SURFACE_TYPES,
    validate_contracts,
)


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def main() -> int:
    failures: list[str] = []

    result = validate_contracts()
    failures.extend(result.failures)

    atlas_schema_path = CONTRACT_DIR / "schemas/atlas_visualization_input_contract_v0_2.schema.json"
    mission_schema_path = CONTRACT_DIR / "schemas/mission_construction_contract_v0_2.schema.json"
    atlas_fixture_path = CONTRACT_DIR / "fixtures/atlas_visualization_input_sample_v0_2.json"
    mission_fixture_path = CONTRACT_DIR / "fixtures/mission_construction_sample_v0_2.json"

    atlas_schema = load_json(atlas_schema_path)
    mission_schema = load_json(mission_schema_path)
    atlas_fixture = load_json(atlas_fixture_path)
    mission_fixture = load_json(mission_fixture_path)

    for label, schema in [("atlas", atlas_schema), ("mission", mission_schema)]:
        schema_id = schema.get("$id", "")
        if not str(schema_id).startswith("https://cartenza.local/contracts/"):
            fail(f"{label} schema id must use the Cartenza contract namespace", failures)

    surface_types = {surface["surface_type"] for surface in atlas_fixture["surfaces"]}
    if surface_types != REQUIRED_ATLAS_SURFACE_TYPES:
        fail(f"atlas fixture surface coverage mismatch: {sorted(surface_types)}", failures)

    for surface in atlas_fixture["surfaces"]:
        if surface["display_policy"]["can_render_in_product"] is not False:
            fail(f"{surface['surface_id']} may not render in product", failures)
        if surface["role_assignment"]["assigned_role"] is not None:
            fail(f"{surface['surface_id']} assigns a role", failures)
        if surface["listener_evidence"]["evidence_ids"]:
            fail(f"{surface['surface_id']} carries listener evidence", failures)

    for mission in mission_fixture["mission_candidates"]:
        if mission["mission_type"] not in APPROVED_MISSION_TYPES:
            fail(f"{mission['mission_id']} uses an unapproved mission_type", failures)
        if mission["atlas_delta_plan"]["write_mode"] != "evidence_only":
            fail(f"{mission['mission_id']} must use evidence_only AtlasDelta write mode", failures)
        if mission["review"]["runtime_allowed"] is not False:
            fail(f"{mission['mission_id']} enables runtime use", failures)
        if mission["review"]["production_mission_allowed"] is not False:
            fail(f"{mission['mission_id']} enables production mission use", failures)
        if mission["listener_evidence"]["evidence_ids"]:
            fail(f"{mission['mission_id']} carries listener evidence", failures)
        for section_name in [
            "known_anchors",
            "gateway_candidates",
            "bridge_candidates",
            "frontier_probes",
            "caution_high_whiplash_controls",
            "route_sequence",
        ]:
            for index, item in enumerate(mission[section_name]):
                graph_context = item.get("graph_context")
                if not graph_context:
                    fail(f"{mission['mission_id']}/{section_name}/{index} missing graph_context", failures)
                    continue
                provenance = graph_context.get("provenance", {})
                for source_file in provenance.get("source_files", []):
                    if not source_file.startswith(ACCEPTED_SUBSTRATE_PREFIX):
                        fail(
                            f"{mission['mission_id']}/{section_name}/{index} "
                            f"graph_context source is outside accepted substrate: {source_file}",
                            failures,
                        )
                if section_name == "route_sequence":
                    for required_key in [
                        "intrinsic_affinity_tags",
                        "context_overlays",
                        "confidence",
                        "readiness_notes",
                    ]:
                        if required_key not in item:
                            fail(
                                f"{mission['mission_id']}/{section_name}/{index} "
                                f"missing {required_key}",
                                failures,
                            )

    type_files = [
        CONTRACT_DIR / "types/atlas_visualization_input_contract_v0_2.ts",
        CONTRACT_DIR / "types/mission_construction_contract_v0_2.ts",
        CONTRACT_DIR / "types/index.ts",
    ]
    for type_file in type_files:
        if not type_file.exists():
            fail(f"missing TypeScript type file: {type_file}", failures)
            continue
        text = type_file.read_text(encoding="utf-8")
        forbidden_paths = ["MusicAtlas" + "Controller", "supabase" + "/functions"]
        for forbidden_path in forbidden_paths:
            if forbidden_path in text:
                fail(f"{type_file} must not import or reference runtime code", failures)

    if failures:
        print("FAIL Derived Affinity v0.2 fixture tests")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("PASS Derived Affinity v0.2 fixture tests")
    print("PASS schemas parse and fixture payloads satisfy offline domain gates")
    print("PASS TypeScript domain type files are present and runtime-disconnected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
