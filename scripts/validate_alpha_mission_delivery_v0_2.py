#!/usr/bin/env python3
"""Validate Cartenza Alpha Mission Delivery v0.2 contracts and fixtures."""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

try:
    import jsonschema
except ImportError:  # pragma: no cover - local environment fallback
    jsonschema = None


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/product_contracts/alpha_mission_delivery_v0_2"
CONTRACT_VERSION = "alpha_mission_delivery_v0_2"

ACTIVE_MISSION_TYPES = {
    "context_dependence_test",
    "boundary_test",
    "bridge_test",
    "archetype_depth_test",
    "gateway_test",
}

DEFERRED_MISSION_TYPES = {
    "artist_depth_test",
    "album_container_test",
    "false_nearby_test",
    "evidence_repair_test",
    "exception_scope_test",
}

APP_IMPORT_STATUSES = {
    "review_only",
    "schema_valid",
    "contract_valid",
    "needs_revision",
    "rejected_product",
    "app_import_candidate",
    "app_import_blocked_unresolved",
    "app_import_blocked_policy",
    "app_import_ready",
}

LEAKY_KEY_FRAGMENTS = [
    "hidden_oracle",
    "hidden_reaction",
    "hidden_lane",
    "oracle_usefulness",
    "oracle_score",
    "final_mission_copy",
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def walk_json(value: Any, path: str = "$"):
    if isinstance(value, dict):
        for key, child in value.items():
            yield f"{path}.{key}", key, child
            yield from walk_json(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk_json(child, f"{path}[{index}]")


def contains_leakage(value: Any) -> list[str]:
    leaks: list[str] = []
    for path, key, child in walk_json(value):
        lowered = str(key).lower()
        if any(fragment in lowered for fragment in LEAKY_KEY_FRAGMENTS):
            leaks.append(path)
        if isinstance(child, str):
            lowered_value = child.lower()
            if "hidden oracle reaction" in lowered_value or "hidden lane" in lowered_value:
                leaks.append(path)
    return leaks


def _type_matches(expected: str, value: Any) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return True


def _resolve_ref(ref: str, root_schema: dict[str, Any]) -> dict[str, Any]:
    if not ref.startswith("#/"):
        return {}
    node: Any = root_schema
    for part in ref[2:].split("/"):
        node = node.get(part, {})
    return node if isinstance(node, dict) else {}


def _minimal_schema_errors(schema: dict[str, Any], value: Any, path: str, root_schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if "$ref" in schema:
        return _minimal_schema_errors(_resolve_ref(schema["$ref"], root_schema), value, path, root_schema)

    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: expected const {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: expected one of {schema['enum']!r}")

    expected_type = schema.get("type")
    if expected_type:
        types = expected_type if isinstance(expected_type, list) else [expected_type]
        if not any(_type_matches(item, value) for item in types):
            errors.append(f"{path}: expected type {expected_type!r}")
            return errors

    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                errors.append(f"{path}: missing required key {key!r}")

        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extra = sorted(set(value) - set(properties))
            for key in extra:
                errors.append(f"{path}: unexpected key {key!r}")

        for key, child_schema in properties.items():
            if key in value:
                errors.extend(_minimal_schema_errors(child_schema, value[key], f"{path}.{key}", root_schema))

    if isinstance(value, list):
        min_items = schema.get("minItems")
        if min_items is not None and len(value) < min_items:
            errors.append(f"{path}: expected at least {min_items} items")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                errors.extend(_minimal_schema_errors(item_schema, item, f"{path}[{index}]", root_schema))

    if isinstance(value, str):
        min_length = schema.get("minLength")
        if min_length is not None and len(value) < min_length:
            errors.append(f"{path}: expected string length >= {min_length}")

    if isinstance(value, int) and not isinstance(value, bool):
        minimum = schema.get("minimum")
        if minimum is not None and value < minimum:
            errors.append(f"{path}: expected integer >= {minimum}")

    return errors


def validate_schema(path: Path, schema: dict[str, Any], value: Any) -> list[str]:
    if jsonschema is not None:
        validator = jsonschema.Draft202012Validator(schema)
        return [f"{list(error.absolute_path)}: {error.message}" for error in validator.iter_errors(value)]
    return _minimal_schema_errors(schema, value, "$", schema)


def role_counts(mission: dict[str, Any]) -> Counter:
    return Counter(item["role"] for item in mission.get("route", []))


def mission_policy(contract: dict[str, Any], mission_type: str) -> dict[str, Any] | None:
    return contract["active_mission_type_policies"].get(mission_type)


def route_gate_failures(mission: dict[str, Any], contract: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    mission_type = mission["mission_type"]
    route = mission.get("route", [])
    status = mission["app_import_status"]
    expected_class = mission.get("validation", {}).get("expected_class")

    if mission_type in DEFERRED_MISSION_TYPES:
        if status in {"app_import_candidate", "app_import_ready"}:
            failures.append("deferred_mission_type_marked_import_eligible")
        failures.append("mission_type_deferred_for_alpha_auto_import")

    if mission_type not in ACTIVE_MISSION_TYPES and mission_type not in DEFERRED_MISSION_TYPES:
        failures.append("unsupported_mission_type")

    if not (5 <= len(route) <= 6):
        failures.append("route_size_not_alpha_5_or_6")

    if mission_type in ACTIVE_MISSION_TYPES:
        policy = mission_policy(contract, mission_type)
        if not policy:
            failures.append("missing_active_mission_policy")
        else:
            counts = role_counts(mission)
            for role, rule in policy.get("required_role_counts", {}).items():
                min_count = rule.get("min", 0)
                if counts[role] < min_count:
                    failures.append(f"missing_required_role_{role}_min_{min_count}")

    high_risk_count = sum(1 for item in route if "controlled_negative_risk" in item.get("risk_flags", []))
    max_allowed = 2 if mission_type in {"boundary_test", "false_nearby_test", "evidence_repair_test"} else 1
    if high_risk_count > max_allowed:
        failures.append("negative_budget_exceeded")
    if len(route) == 6 and high_risk_count >= 3:
        failures.append("three_or_more_negative_risk_items")

    source_trace = mission.get("source_trace", {})
    source_refs = source_trace.get("source_opportunity_refs", [])
    if not source_refs:
        failures.append("missing_source_opportunity_refs")

    if source_trace.get("multi_source_route") and not source_trace.get("multi_source_route_reason"):
        failures.append("multi_source_route_missing_reason")

    if not mission.get("why_this_mission_now", "").strip():
        failures.append("missing_why_this_mission_now")
    if not mission.get("coherence_sentence", "").strip():
        failures.append("missing_coherence_sentence")

    if "because" not in mission.get("coherence_sentence", "").lower() or "test" not in mission.get("coherence_sentence", "").lower():
        failures.append("coherence_sentence_not_user_explainable")

    for item in route:
        if not item.get("expected_signal", "").strip():
            failures.append("route_item_missing_expected_signal")
        if not item.get("why_in_route", "").strip():
            failures.append("route_item_missing_why_in_route")
        if not item.get("reaction_chip_set_id"):
            failures.append("route_item_missing_feedback_chip_plan")
        if not item.get("song_title", "").strip() or not item.get("artist_name", "").strip():
            failures.append("route_item_missing_display_music_ref")
        if not item.get("canonical_song_id") and not item.get("apple_music_id") and item.get("resolution_status") not in {"unresolved", "blocked"}:
            failures.append("route_item_missing_concrete_music_ref")

    unresolved_count = sum(1 for item in route if item["resolution_status"] == "unresolved")
    blocked_count = sum(1 for item in route if item["resolution_status"] == "blocked")
    candidate_count = sum(1 for item in route if item["resolution_status"] == "candidate")
    resolved_count = sum(1 for item in route if item["resolution_status"] == "resolved")

    if status == "app_import_ready":
        if unresolved_count or blocked_count or candidate_count:
            failures.append("app_import_ready_requires_all_route_items_resolved")
        for item in route:
            if not item.get("apple_music_id") and not item.get("apple_music_url"):
                failures.append("app_import_ready_missing_apple_music_ref")

    if status == "app_import_candidate":
        if unresolved_count or blocked_count:
            failures.append("app_import_candidate_has_unresolved_or_blocked_route_item")

    if unresolved_count and expected_class == "approved_app_import_candidate":
        failures.append("approved_candidate_has_unresolved_route_item")

    feedback = mission.get("feedback_model", {})
    mapping = feedback.get("operation_mapping", {})
    for op in ["strong_positive", "qualified_positive", "keep_waypoint", "negative", "skip_or_no_signal", "issue_wrong_version", "issue_unavailable"]:
        if op not in mapping.values():
            failures.append(f"feedback_operation_missing_{op}")

    runtime_flags = mission.get("runtime_flags", {})
    for key in [
        "runtime_selector_wiring",
        "real_listener_evidence_connected",
        "production_mission_generation_allowed",
        "final_mission_content",
        "canonical_graph_mutation_allowed",
    ]:
        if runtime_flags.get(key) is not False:
            failures.append(f"runtime_flag_not_false_{key}")

    leaks = contains_leakage(mission)
    if leaks:
        failures.append("hidden_oracle_or_final_copy_leakage:" + ",".join(leaks[:5]))

    return sorted(set(failures))


def status_from_failures(mission: dict[str, Any], failures: list[str]) -> tuple[str, bool, bool, str]:
    mission_type = mission["mission_type"]
    status = mission["app_import_status"]
    if mission_type in DEFERRED_MISSION_TYPES:
        return "rejected_product", False, False, "mission_type_deferred_for_alpha_auto_import"
    if "app_import_ready_requires_all_route_items_resolved" in failures:
        return "app_import_blocked_unresolved", False, False, "app_import_ready_requires_all_route_items_resolved"
    if any(reason.startswith("hidden_oracle") for reason in failures):
        return "app_import_blocked_policy", False, False, "hidden_oracle_or_final_copy_leakage"
    if "app_import_candidate_has_unresolved_or_blocked_route_item" in failures:
        return "app_import_blocked_unresolved", False, False, "app_import_candidate_has_unresolved_or_blocked_route_item"
    if status == "needs_revision" or any(
        reason in failures
        for reason in [
            "negative_budget_exceeded",
            "missing_required_role_anchor_min_1",
            "missing_required_role_control_min_1",
            "coherence_sentence_not_user_explainable",
        ]
    ):
        return "needs_revision", False, False, failures[0] if failures else "needs_revision"
    if failures:
        return "app_import_blocked_policy", False, False, failures[0]

    if status == "app_import_ready":
        return "app_import_ready", True, True, "none"
    if status == "app_import_candidate":
        return "app_import_candidate", True, False, "apple_music_resolution_remaining"
    return status, False, False, "not_marked_as_import_candidate"


def validate_negative_fixture(path: Path, schema: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    data = load_json(path)
    expected_fail = True
    schema_errors: list[str] = []
    gate_failures: list[str] = []

    if isinstance(data, dict) and "mission_id" in data:
        schema_errors = validate_schema(path, schema, data)
        if not schema_errors:
            gate_failures = route_gate_failures(data, contract)
    else:
        leaks = contains_leakage(data)
        if leaks:
            gate_failures.append("hidden_oracle_or_final_copy_leakage")
        if data.get("first_run_hash") != data.get("second_run_hash"):
            gate_failures.append("determinism_mismatch")

    did_fail = bool(schema_errors or gate_failures)
    return {
        "fixture": str(path.relative_to(ROOT)),
        "expected_fail": expected_fail,
        "did_fail": did_fail,
        "schema_errors": schema_errors,
        "gate_failures": gate_failures,
    }


def markdown_report(report: dict[str, Any]) -> str:
    mission_rows = []
    for item in report["fixture_results"]:
        mission_rows.append(
            f"| `{item['mission_id']}` | `{item['mission_type']}` | {item['expected_class']} | {item['computed_status']} | {item['alpha_import_eligible']} | {item['app_import_ready']} | {item['top_blocking_reason']} |"
        )

    negative_rows = []
    for item in report["negative_fixture_results"]:
        negative_rows.append(
            f"| `{Path(item['fixture']).name}` | {item['expected_fail']} | {item['did_fail']} | {', '.join(item['gate_failures'][:2] or item['schema_errors'][:1] or ['none'])} |"
        )

    return f"""# Alpha Mission Delivery Validation Report v0.2

Overall result: **{report['overall_result']}**

Approved app-import candidates: {report['approved_candidate_count']}

App-import ready: {report['app_import_ready_count']}

Schema errors: {report['schema_error_count']}

Gate failures: {report['gate_failure_count']}

Gate failures include intentional rejected/deferred golden examples; approved app-import candidates have no blocking product-policy failures except the declared Apple Music resolution step.

## Fixture Results

| mission_id | mission_type | expected_class | computed_status | alpha_import_eligible | app_import_ready | top_blocking_reason |
| --- | --- | --- | --- | --- | --- | --- |
{chr(10).join(mission_rows)}

## Negative Fixture Results

| fixture | expected_fail | did_fail | reason |
| --- | --- | --- | --- |
{chr(10).join(negative_rows)}

## Guardrail Summary

- Runtime selector wiring remains false.
- Real listener evidence connection remains false.
- Production mission generation remains false.
- Final mission construction remains false.
- Canonical graph mutation remains false.
- Hidden oracle reactions are not present in app-import payload fixtures.
- Ordinary app-import-ready missions with unresolved route items are blocked.
"""


def main() -> int:
    payload_schema = load_json(OUT / "app_import_mission_payload_v0_2.schema.json")
    contract_schema = load_json(OUT / "mission_construction_contract_v0_2.schema.json")
    contract = load_json(OUT / "mission_construction_contract_v0_2.json")
    fixtures = load_json(OUT / "fixtures/golden/golden_alpha_mission_fixture_set_v0_2.json")

    contract_schema_errors = validate_schema(OUT / "mission_construction_contract_v0_2.json", contract_schema, contract)

    all_missions = []
    for key in ["approved_app_import_candidates", "revise_needed", "rejected"]:
        all_missions.extend(fixtures[key])

    fixture_results: list[dict[str, Any]] = []
    schema_error_count = 0
    gate_failure_count = 0
    approved_candidate_count = 0
    app_import_ready_count = 0

    for mission in all_missions:
        schema_errors = validate_schema(Path(mission["mission_id"]), payload_schema, mission)
        gate_failures = [] if schema_errors else route_gate_failures(mission, contract)
        computed_status, alpha_import_eligible, app_import_ready, top_reason = status_from_failures(mission, gate_failures)
        schema_error_count += len(schema_errors)
        gate_failure_count += len(gate_failures)
        approved_candidate_count += 1 if alpha_import_eligible else 0
        app_import_ready_count += 1 if app_import_ready else 0
        fixture_results.append(
            {
                "mission_id": mission["mission_id"],
                "mission_type": mission["mission_type"],
                "expected_class": mission.get("validation", {}).get("expected_class"),
                "declared_status": mission["app_import_status"],
                "computed_status": computed_status,
                "alpha_import_eligible": alpha_import_eligible,
                "app_import_ready": app_import_ready,
                "top_blocking_reason": top_reason,
                "schema_errors": schema_errors,
                "gate_failures": gate_failures,
            }
        )

    negative_results = []
    for path in sorted((OUT / "fixtures/negative").glob("*.json")):
        negative_results.append(validate_negative_fixture(path, payload_schema, contract))

    expected_negative_ok = all(item["did_fail"] for item in negative_results)
    accepted_candidates = [
        item
        for item in fixture_results
        if item["expected_class"] == "approved_app_import_candidate" and item["computed_status"] in {"app_import_candidate", "app_import_ready"}
    ]
    deferred_blocked_ok = all(
        item["computed_status"] == "rejected_product"
        for item in fixture_results
        if item["mission_type"] in DEFERRED_MISSION_TYPES
    )

    overall_ok = (
        not contract_schema_errors
        and schema_error_count == 0
        and len(accepted_candidates) >= 6
        and expected_negative_ok
        and deferred_blocked_ok
    )

    report = {
        "contract_version": CONTRACT_VERSION,
        "overall_result": "PASS" if overall_ok else "FAIL",
        "contract_schema_errors": contract_schema_errors,
        "fixture_count": len(all_missions),
        "approved_candidate_count": len(accepted_candidates),
        "app_import_ready_count": app_import_ready_count,
        "schema_error_count": schema_error_count,
        "gate_failure_count": gate_failure_count,
        "fixture_results": fixture_results,
        "negative_fixture_results": negative_results,
        "guardrails": {
            "runtime_selector_wiring": False,
            "real_listener_evidence_connected": False,
            "production_mission_generation_allowed": False,
            "final_mission_construction": False,
            "canonical_graph_mutation_allowed": False,
            "held_out_review_reactions_in_app_import_payloads": False,
        },
        "notes": [
            "Approved app-import candidates are not app_import_ready because Apple Music resolution remains.",
            "Deferred artist-depth and album-container fixtures are blocked from automatic Alpha import.",
        ],
    }

    reports_dir = OUT / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "alpha_mission_delivery_validation_report_v0_2.json").write_text(json.dumps(report, indent=2) + "\n")
    (reports_dir / "alpha_mission_delivery_validation_report_v0_2.md").write_text(markdown_report(report))

    print(json.dumps({
        "overall_result": report["overall_result"],
        "fixture_count": report["fixture_count"],
        "approved_candidate_count": report["approved_candidate_count"],
        "app_import_ready_count": report["app_import_ready_count"],
        "schema_error_count": report["schema_error_count"],
        "gate_failure_count": report["gate_failure_count"],
        "negative_fixtures_failed_as_expected": expected_negative_ok,
    }, indent=2))
    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main())
