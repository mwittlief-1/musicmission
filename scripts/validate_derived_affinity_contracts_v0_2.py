#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DIR = REPO_ROOT / "data/product_contracts/derived_affinity_v0_2"

DEFAULT_ATLAS_SCHEMA = (
    CONTRACT_DIR / "schemas/atlas_visualization_input_contract_v0_2.schema.json"
)
DEFAULT_MISSION_SCHEMA = (
    CONTRACT_DIR / "schemas/mission_construction_contract_v0_2.schema.json"
)
DEFAULT_ATLAS_FIXTURE = (
    CONTRACT_DIR / "fixtures/atlas_visualization_input_sample_v0_2.json"
)
DEFAULT_MISSION_FIXTURE = (
    CONTRACT_DIR / "fixtures/mission_construction_sample_v0_2.json"
)

ATLAS_CONTRACT_VERSION = "atlas_visualization_input_v0_2"
MISSION_CONTRACT_VERSION = "mission_construction_v0_2"
SOURCE_SUBSTRATE_VERSION = "derived_affinity_substrate_v0_1_1"
SOURCE_PACKAGE = "derived_affinity_substrate_v0_1_1/"

REQUIRED_ATLAS_SURFACE_TYPES = {
    "Region",
    "Road",
    "Frontier",
    "Dead End",
    "Caution",
    "Gateway",
    "Landmark",
    "Waypoint",
    "Bridge",
    "Recent Learning",
}

APPROVED_MISSION_TYPES = {
    "safe_risky_split",
    "album_world_test",
    "route_gateway_mission",
    "cross_family_bridge_mission",
    "frontier_probe",
    "false_nearby_trap_test",
    "one_object_exception_test",
    "context_mission",
    "b_b_plus_shelf_mission",
    "modern_discovery_correction",
}

GRAPH_ITEM_ROLES = {
    "canonical_anchor",
    "major_representative",
    "gateway",
    "bridge",
    "deep_cut",
    "contextual_object",
    "unknown",
}

IDENTITY_OR_DUPLICATE_FLAGS = {
    "duplicate_context_review_needed",
    "duplicate_context_unclear",
    "identity_review_needed",
    "recording_identity_unclear",
    "version_ambiguity",
}

ACCEPTED_SUBSTRATE_PREFIX = "derived_affinity_substrate_v0_1_1/"


@dataclass
class ValidationResult:
    passes: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)

    def pass_(self, message: str) -> None:
        self.passes.append(message)

    def fail(self, message: str) -> None:
        self.failures.append(message)

    @property
    def ok(self) -> bool:
        return not self.failures


def load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        raise SystemExit(f"File not found: {path}") from None
    except json.JSONDecodeError as error:
        raise SystemExit(f"Invalid JSON in {path}: {error}") from None


def format_path(path_parts: Iterable[object]) -> str:
    parts = [str(part) for part in path_parts]
    return "/" + "/".join(parts) if parts else "/"


def validate_json_schema(
    schema_path: Path,
    document_path: Path,
    label: str,
    result: ValidationResult,
) -> None:
    try:
        from jsonschema import Draft202012Validator
    except ModuleNotFoundError:
        result.fail(
            "jsonschema is required for schema validation. "
            "Install with `python3 -m pip install -r scripts/requirements.txt`."
        )
        return

    schema = load_json(schema_path)
    document = load_json(document_path)

    try:
        Draft202012Validator.check_schema(schema)
    except Exception as error:  # pragma: no cover - message is for CLI diagnostics.
        result.fail(f"{label} schema is invalid: {error}")
        return

    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(document), key=lambda error: list(error.path))
    if not errors:
        result.pass_(f"{label} JSON Schema validation passed")
        return

    for error in errors:
        result.fail(f"{label} schema {format_path(error.path)}: {error.message}")


def expect_const(
    actual: Any,
    expected: Any,
    pointer: str,
    result: ValidationResult,
) -> None:
    if actual != expected:
        result.fail(f"{pointer} must be {expected!r}; got {actual!r}")


def expect_false(actual: Any, pointer: str, result: ValidationResult) -> None:
    if actual is not False:
        result.fail(f"{pointer} must be false for offline review-only use")


def expect_true(actual: Any, pointer: str, result: ValidationResult) -> None:
    if actual is not True:
        result.fail(f"{pointer} must be true")


def is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and len(value.strip()) > 0


def validate_atlas_domain(
    atlas: dict[str, Any],
    result: ValidationResult,
    require_all_surface_types: bool,
) -> None:
    expect_const(atlas.get("contract_version"), ATLAS_CONTRACT_VERSION, "/contract_version", result)
    expect_const(
        atlas.get("source_substrate_version"),
        SOURCE_SUBSTRATE_VERSION,
        "/source_substrate_version",
        result,
    )
    expect_const(atlas.get("source_package"), SOURCE_PACKAGE, "/source_package", result)
    expect_false(atlas.get("runtime_allowed"), "/runtime_allowed", result)
    expect_false(
        atlas.get("canonical_graph_mutation_allowed"),
        "/canonical_graph_mutation_allowed",
        result,
    )
    expect_false(
        atlas.get("listener_preference_inference_allowed"),
        "/listener_preference_inference_allowed",
        result,
    )

    surfaces = atlas.get("surfaces")
    if not isinstance(surfaces, list) or not surfaces:
        result.fail("/surfaces must be a non-empty array")
        return

    seen_surface_types: set[str] = set()
    seen_surface_ids: set[str] = set()
    for index, surface in enumerate(surfaces):
        pointer = f"/surfaces/{index}"
        if not isinstance(surface, dict):
            result.fail(f"{pointer} must be an object")
            continue

        surface_id = surface.get("surface_id")
        if not is_non_empty_string(surface_id):
            result.fail(f"{pointer}/surface_id must be a non-empty string")
        elif surface_id in seen_surface_ids:
            result.fail(f"{pointer}/surface_id duplicates {surface_id}")
        else:
            seen_surface_ids.add(surface_id)

        surface_type = surface.get("surface_type")
        seen_surface_types.add(str(surface_type))

        expect_const(
            surface.get("contract_version"),
            ATLAS_CONTRACT_VERSION,
            f"{pointer}/contract_version",
            result,
        )
        expect_const(
            surface.get("source_substrate_version"),
            SOURCE_SUBSTRATE_VERSION,
            f"{pointer}/source_substrate_version",
            result,
        )

        risk_review = surface.get("risk_review") or {}
        readiness = surface.get("readiness") or {}
        listener_evidence = surface.get("listener_evidence") or {}
        role_assignment = surface.get("role_assignment") or {}
        display_policy = surface.get("display_policy") or {}
        provenance = surface.get("provenance") or {}

        expect_true(
            risk_review.get("review_required"),
            f"{pointer}/risk_review/review_required",
            result,
        )
        expect_true(
            listener_evidence.get("not_inferred_from_affinity"),
            f"{pointer}/listener_evidence/not_inferred_from_affinity",
            result,
        )
        expect_false(
            display_policy.get("can_render_in_product"),
            f"{pointer}/display_policy/can_render_in_product",
            result,
        )
        expect_const(
            provenance.get("canonical_graph_mutation"),
            "not_performed",
            f"{pointer}/provenance/canonical_graph_mutation",
            result,
        )
        expect_const(
            provenance.get("runtime_ingestion"),
            "not_performed",
            f"{pointer}/provenance/runtime_ingestion",
            result,
        )

        if listener_evidence.get("status") == "present":
            result.fail(f"{pointer}/listener_evidence/status cannot be present in this offline fixture")
        if listener_evidence.get("evidence_ids"):
            result.fail(f"{pointer}/listener_evidence/evidence_ids must remain empty")
        if role_assignment.get("assigned_role") is not None:
            result.fail(f"{pointer}/role_assignment/assigned_role must remain null")
        if role_assignment.get("status") == "assigned_after_review":
            result.fail(f"{pointer}/role_assignment/status cannot assign roles in this package")

        bridge_category = risk_review.get("bridge_category")
        quarantine_status = risk_review.get("quarantine_status")
        risk_flags = set(risk_review.get("risk_flags") or [])
        review_flags = set(risk_review.get("review_flags") or [])
        all_review_risk_flags = risk_flags | review_flags

        if surface_type in {"Road", "Bridge"} and bridge_category == "clean_bridge_candidate":
            if quarantine_status != "none":
                result.fail(f"{pointer} clean Road/Bridge must have quarantine_status=none")
            overlap = sorted(all_review_risk_flags & IDENTITY_OR_DUPLICATE_FLAGS)
            if overlap:
                result.fail(f"{pointer} clean Road/Bridge carries identity or duplicate flags: {overlap}")

        if bridge_category == "identity_quarantine":
            expect_const(
                quarantine_status,
                "identity_quarantine",
                f"{pointer}/risk_review/quarantine_status",
                result,
            )
            expect_const(
                readiness.get("fog_state"),
                "blocked",
                f"{pointer}/readiness/fog_state",
                result,
            )

        if surface_type in {"Landmark", "Recent Learning"}:
            expect_const(
                role_assignment.get("status"),
                "not_assignable_from_substrate",
                f"{pointer}/role_assignment/status",
                result,
            )
            expect_const(
                listener_evidence.get("status"),
                "required_before_assignment",
                f"{pointer}/listener_evidence/status",
                result,
            )
            expect_const(
                readiness.get("fog_state"),
                "blocked",
                f"{pointer}/readiness/fog_state",
                result,
            )

        if surface_type == "Dead End":
            expect_const(
                role_assignment.get("status"),
                "not_assignable_from_substrate",
                f"{pointer}/role_assignment/status",
                result,
            )

        if surface_type == "Gateway":
            score_components = (surface.get("intrinsic_affinity") or {}).get("score_components") or {}
            if score_components.get("quality_score") != "not_applicable":
                result.fail(f"{pointer} gateway must state quality_score is not_applicable")

    if require_all_surface_types:
        missing = sorted(REQUIRED_ATLAS_SURFACE_TYPES - seen_surface_types)
        if missing:
            result.fail(f"/surfaces missing required fixture surface types: {missing}")

    result.pass_(f"atlas domain gates checked surfaces={len(surfaces)}")


def validate_graph_context(context: Any, pointer: str, result: ValidationResult) -> None:
    if not isinstance(context, dict):
        result.fail(f"{pointer}/graph_context must be an object")
        return

    for key in [
        "family_ids",
        "family_names",
        "archetype_ids",
        "archetype_names",
    ]:
        if not isinstance(context.get(key), list):
            result.fail(f"{pointer}/graph_context/{key} must be an array")

    if context.get("graph_item_role") not in GRAPH_ITEM_ROLES:
        result.fail(
            f"{pointer}/graph_context/graph_item_role must be one of "
            f"{sorted(GRAPH_ITEM_ROLES)}"
        )
    if not is_non_empty_string(context.get("role_basis")):
        result.fail(f"{pointer}/graph_context/role_basis must explain the planning role")

    provenance = context.get("provenance")
    if not isinstance(provenance, dict):
        result.fail(f"{pointer}/graph_context/provenance must be an object")
        return

    source_files = provenance.get("source_files")
    source_candidate_ids = provenance.get("source_candidate_ids")
    source_fields = provenance.get("source_fields")
    for key, value in [
        ("source_files", source_files),
        ("source_candidate_ids", source_candidate_ids),
        ("source_fields", source_fields),
    ]:
        if not isinstance(value, list) or not value:
            result.fail(f"{pointer}/graph_context/provenance/{key} must be non-empty")

    for source_file in source_files or []:
        if not isinstance(source_file, str):
            result.fail(f"{pointer}/graph_context/provenance/source_files values must be strings")
            continue
        blocked_canonical_prefix = "data/canonical" + "_graph/"
        if source_file.startswith(blocked_canonical_prefix):
            result.fail(f"{pointer}/graph_context cannot source canonical graph files: {source_file}")
        if not source_file.startswith(ACCEPTED_SUBSTRATE_PREFIX):
            result.fail(
                f"{pointer}/graph_context source file must come from accepted v0.1.1 "
                f"substrate package: {source_file}"
            )

    if not is_non_empty_string(provenance.get("notes")):
        result.fail(f"{pointer}/graph_context/provenance/notes must explain claim limits")


def validate_mission_domain(mission_doc: dict[str, Any], result: ValidationResult) -> None:
    expect_const(
        mission_doc.get("contract_version"),
        MISSION_CONTRACT_VERSION,
        "/contract_version",
        result,
    )
    expect_const(
        mission_doc.get("source_substrate_version"),
        SOURCE_SUBSTRATE_VERSION,
        "/source_substrate_version",
        result,
    )
    expect_const(mission_doc.get("source_package"), SOURCE_PACKAGE, "/source_package", result)
    expect_false(mission_doc.get("runtime_allowed"), "/runtime_allowed", result)
    expect_false(mission_doc.get("production_mission_allowed"), "/production_mission_allowed", result)
    expect_false(
        mission_doc.get("canonical_graph_mutation_allowed"),
        "/canonical_graph_mutation_allowed",
        result,
    )
    expect_false(
        mission_doc.get("listener_preference_inference_allowed"),
        "/listener_preference_inference_allowed",
        result,
    )

    missions = mission_doc.get("mission_candidates")
    if not isinstance(missions, list) or not missions:
        result.fail("/mission_candidates must be a non-empty array")
        return

    for index, mission in enumerate(missions):
        pointer = f"/mission_candidates/{index}"
        if not isinstance(mission, dict):
            result.fail(f"{pointer} must be an object")
            continue

        expect_const(
            mission.get("contract_version"),
            MISSION_CONTRACT_VERSION,
            f"{pointer}/contract_version",
            result,
        )
        expect_const(
            mission.get("source_substrate_version"),
            SOURCE_SUBSTRATE_VERSION,
            f"{pointer}/source_substrate_version",
            result,
        )

        if not is_non_empty_string(mission.get("mission_hypothesis")):
            result.fail(f"{pointer}/mission_hypothesis must be testable prose")
        if mission.get("mission_type") not in APPROVED_MISSION_TYPES:
            result.fail(
                f"{pointer}/mission_type must be an approved affinity-derived pattern"
            )
        if not mission.get("target_affinity_pattern"):
            result.fail(f"{pointer}/target_affinity_pattern must be non-empty")

        listener_evidence = mission.get("listener_evidence") or {}
        review = mission.get("review") or {}
        provenance = mission.get("provenance") or {}
        atlas_delta_plan = mission.get("atlas_delta_plan") or {}

        expect_const(
            listener_evidence.get("status"),
            "absent_at_construction",
            f"{pointer}/listener_evidence/status",
            result,
        )
        expect_true(
            listener_evidence.get("not_inferred_from_affinity"),
            f"{pointer}/listener_evidence/not_inferred_from_affinity",
            result,
        )
        if listener_evidence.get("evidence_ids"):
            result.fail(f"{pointer}/listener_evidence/evidence_ids must remain empty")

        expect_true(review.get("pm_review_required"), f"{pointer}/review/pm_review_required", result)
        expect_false(review.get("runtime_allowed"), f"{pointer}/review/runtime_allowed", result)
        expect_false(
            review.get("production_mission_allowed"),
            f"{pointer}/review/production_mission_allowed",
            result,
        )
        expect_const(
            atlas_delta_plan.get("write_mode"),
            "evidence_only",
            f"{pointer}/atlas_delta_plan/write_mode",
            result,
        )
        expect_const(
            provenance.get("canonical_graph_mutation"),
            "not_performed",
            f"{pointer}/provenance/canonical_graph_mutation",
            result,
        )
        expect_const(
            provenance.get("runtime_ingestion"),
            "not_performed",
            f"{pointer}/provenance/runtime_ingestion",
            result,
        )

        for evidence_key in ["confirming", "falsifying", "ambiguous"]:
            values = (mission.get("expected_evidence") or {}).get(evidence_key)
            if not isinstance(values, list) or not values:
                result.fail(f"{pointer}/expected_evidence/{evidence_key} must be non-empty")

        route_sequence = mission.get("route_sequence") or []
        route_candidate_ids = {
            item.get("candidate_id")
            for item in route_sequence
            if isinstance(item, dict) and item.get("candidate_id")
        }
        sequence_indexes = [
            item.get("sequence_index") for item in route_sequence if isinstance(item, dict)
        ]
        if sequence_indexes != list(range(1, len(route_sequence) + 1)):
            result.fail(f"{pointer}/route_sequence sequence_index must be contiguous from 1")

        for route_index, item in enumerate(route_sequence):
            item_pointer = f"{pointer}/route_sequence/{route_index}"
            if not is_non_empty_string((item or {}).get("inclusion_reason")):
                result.fail(f"{item_pointer}/inclusion_reason is required")
            if not is_non_empty_string((item or {}).get("tests")):
                result.fail(f"{item_pointer}/tests is required")
            if not (item or {}).get("intrinsic_affinity_tags"):
                result.fail(f"{item_pointer}/intrinsic_affinity_tags must be non-empty")
            if not isinstance((item or {}).get("context_overlays"), list):
                result.fail(f"{item_pointer}/context_overlays must be an array")
            if (item or {}).get("confidence") not in {"low", "medium", "high"}:
                result.fail(f"{item_pointer}/confidence is invalid")
            if not (item or {}).get("readiness_notes"):
                result.fail(f"{item_pointer}/readiness_notes must be non-empty")
            validate_graph_context((item or {}).get("graph_context"), item_pointer, result)

        for section_name in [
            "known_anchors",
            "gateway_candidates",
            "frontier_probes",
            "caution_high_whiplash_controls",
        ]:
            for item_index, item in enumerate(mission.get(section_name) or []):
                item_pointer = f"{pointer}/{section_name}/{item_index}"
                validate_graph_context((item or {}).get("graph_context"), item_pointer, result)

        exclusions = mission.get("identity_duplicate_quarantine_exclusions") or []
        for exclusion_index, exclusion in enumerate(exclusions):
            candidate_id = (exclusion or {}).get("candidate_id")
            if candidate_id in route_candidate_ids:
                result.fail(
                    f"{pointer}/identity_duplicate_quarantine_exclusions/{exclusion_index} "
                    "appears in route_sequence"
                )

        for bridge_index, bridge in enumerate(mission.get("bridge_candidates") or []):
            bridge_pointer = f"{pointer}/bridge_candidates/{bridge_index}"
            if bridge.get("bridge_category") == "identity_quarantine":
                result.fail(f"{bridge_pointer} cannot be identity_quarantine in route bridge candidates")
            if "intrinsic_affinity_score" not in bridge:
                result.fail(f"{bridge_pointer}/intrinsic_affinity_score is required")
            if "product_bridge_readiness_score" not in bridge:
                result.fail(f"{bridge_pointer}/product_bridge_readiness_score is required")
            validate_graph_context(bridge.get("graph_context"), bridge_pointer, result)

    result.pass_(f"mission domain gates checked missions={len(missions)}")


def validate_contracts(
    atlas_schema_path: Path = DEFAULT_ATLAS_SCHEMA,
    mission_schema_path: Path = DEFAULT_MISSION_SCHEMA,
    atlas_fixture_path: Path = DEFAULT_ATLAS_FIXTURE,
    mission_fixture_path: Path = DEFAULT_MISSION_FIXTURE,
    use_json_schema: bool = True,
    require_all_surface_types: bool = True,
) -> ValidationResult:
    result = ValidationResult()

    atlas_schema = load_json(atlas_schema_path)
    mission_schema = load_json(mission_schema_path)
    atlas = load_json(atlas_fixture_path)
    mission = load_json(mission_fixture_path)

    expect_const(
        atlas_schema.get("$schema"),
        "https://json-schema.org/draft/2020-12/schema",
        f"{atlas_schema_path}/$schema",
        result,
    )
    expect_const(
        mission_schema.get("$schema"),
        "https://json-schema.org/draft/2020-12/schema",
        f"{mission_schema_path}/$schema",
        result,
    )

    if use_json_schema:
        validate_json_schema(atlas_schema_path, atlas_fixture_path, "atlas fixture", result)
        validate_json_schema(mission_schema_path, mission_fixture_path, "mission fixture", result)

    validate_atlas_domain(atlas, result, require_all_surface_types=require_all_surface_types)
    validate_mission_domain(mission, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate offline Derived Affinity v0.2 contract schemas and fixtures."
    )
    parser.add_argument("--atlas-schema", type=Path, default=DEFAULT_ATLAS_SCHEMA)
    parser.add_argument("--mission-schema", type=Path, default=DEFAULT_MISSION_SCHEMA)
    parser.add_argument("--atlas-fixture", type=Path, default=DEFAULT_ATLAS_FIXTURE)
    parser.add_argument("--mission-fixture", type=Path, default=DEFAULT_MISSION_FIXTURE)
    parser.add_argument(
        "--skip-jsonschema",
        action="store_true",
        help="Run domain gates only; intended for environments without jsonschema installed.",
    )
    parser.add_argument(
        "--no-require-all-atlas-surfaces",
        action="store_true",
        help="Do not require the sample fixture to cover every Atlas surface type.",
    )
    args = parser.parse_args()

    result = validate_contracts(
        atlas_schema_path=args.atlas_schema,
        mission_schema_path=args.mission_schema,
        atlas_fixture_path=args.atlas_fixture,
        mission_fixture_path=args.mission_fixture,
        use_json_schema=not args.skip_jsonschema,
        require_all_surface_types=not args.no_require_all_atlas_surfaces,
    )

    if result.ok:
        for message in result.passes:
            print(f"PASS {message}")
        print("PASS offline boundaries runtime=false canonical_mutation=false listener_inference=false")
        return 0

    print("FAIL Derived Affinity v0.2 contract validation")
    for failure in result.failures:
        print(f"- {failure}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
