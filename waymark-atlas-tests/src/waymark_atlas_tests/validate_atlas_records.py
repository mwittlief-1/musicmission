from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from .atlas_utils import make_bundle, records_by_type


def validate_records(
    *,
    records: List[Dict[str, Any]],
    digest_record: Dict[str, Any],
    expanded_digest: Dict[str, Any],
    schema_path: Path,
    expected_summary: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    all_records = records + [digest_record]
    bundle = make_bundle(
        "atlas_ingestion_generated_records_v0_1",
        "Generated Atlas ingestion harness records plus AtlasDigestView.",
        all_records,
    )
    schema_result = validate_against_contract(bundle, schema_path)
    invariant_checks = run_invariant_checks(
        records=records,
        digest_record=digest_record,
        expanded_digest=expanded_digest,
        expected_summary=expected_summary or {},
    )
    return {
        "schema_validation": schema_result,
        "invariant_checks": invariant_checks,
        "valid": schema_result["valid"] and all(check["status"] == "pass" for check in invariant_checks),
        "record_counts": record_counts(all_records),
    }


def validate_against_contract(bundle: Dict[str, Any], schema_path: Path) -> Dict[str, Any]:
    schema = _load_json(schema_path)
    try:
        import jsonschema  # type: ignore
    except Exception as error:  # noqa: BLE001 - optional dependency fallback.
        return _fallback_validate(bundle, schema, f"jsonschema_unavailable: {error}")

    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(bundle), key=lambda item: list(item.path))
    return {
        "validator": "jsonschema.Draft202012Validator",
        "valid": not errors,
        "error_count": len(errors),
        "errors": [
            {
                "path": ".".join(str(part) for part in error.path),
                "message": error.message,
            }
            for error in errors
        ],
    }


def record_counts(records: List[Dict[str, Any]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for record in records:
        record_type = record.get("record_type", "unknown")
        counts[record_type] = counts.get(record_type, 0) + 1
    return counts


def run_invariant_checks(
    *,
    records: List[Dict[str, Any]],
    digest_record: Dict[str, Any],
    expanded_digest: Dict[str, Any],
    expected_summary: Dict[str, Any],
) -> List[Dict[str, str]]:
    checks = [
        _check_expected_counts(records + [digest_record], expected_summary),
        _check_no_canonical_graph_mutation(records),
        _check_atlas_node_has_no_authoritative_role(records),
        _check_survey_does_not_auto_promote_weak_evidence(records),
        _check_mission_review_does_not_auto_promote(records),
        _check_signal_auditability(records),
        _check_signal_strength_separated(records),
        _check_candidate_pool_behavior_present(records, expanded_digest),
        _check_composition_placeholder_support(records),
        _check_vocabulary_terms_not_automatically_canon(records),
        _check_digest_emits_mission_usable_summaries(digest_record, expanded_digest, expected_summary),
    ]
    return checks


def _check_expected_counts(records: List[Dict[str, Any]], expected_summary: Dict[str, Any]) -> Dict[str, str]:
    minimum_counts = expected_summary.get("minimum_counts", {})
    counts = record_counts(records)
    failures = [
        f"{record_type}: expected >= {minimum}, got {counts.get(record_type, 0)}"
        for record_type, minimum in minimum_counts.items()
        if record_type not in {"survey_fixtures", "mission_review_fixtures"} and counts.get(record_type, 0) < minimum
    ]
    return _check("expected_record_counts", not failures, "; ".join(failures) or "Generated record counts meet minimum expectations.")


def _check_no_canonical_graph_mutation(records: List[Dict[str, Any]]) -> Dict[str, str]:
    offenders = [
        record["update_candidate_id"]
        for record in records_by_type(records, "possible_atlas_update_candidate")
        if record.get("canonical_graph_mutation_allowed") is not False
    ]
    return _check("no_canonical_graph_mutation", not offenders, _offender_detail(offenders, "All update candidates pin canonical_graph_mutation_allowed=false."))


def _check_atlas_node_has_no_authoritative_role(records: List[Dict[str, Any]]) -> Dict[str, str]:
    forbidden_keys = {"role", "atlas_roles", "candidate_pool_behavior", "role_truth"}
    offenders = []
    for record in records_by_type(records, "atlas_node"):
        overlap = sorted(forbidden_keys.intersection(record))
        if overlap:
            offenders.append(f"{record['atlas_node_id']} has {','.join(overlap)}")
    return _check("atlas_node_has_no_authoritative_role", not offenders, _offender_detail(offenders, "AtlasNode records contain no role truth fields."))


def _check_survey_does_not_auto_promote_weak_evidence(records: List[Dict[str, Any]]) -> Dict[str, str]:
    signal_sources = _signal_sources(records)
    offenders = []
    for record in records:
        if record.get("record_type") == "atlas_role_assignment":
            if any(signal_sources.get(signal_id) == "survey" for signal_id in record.get("evidence_signal_ids", [])):
                lifecycle = record.get("lifecycle", {})
                if lifecycle.get("promotion_state") == "promoted" or lifecycle.get("status") == "active":
                    offenders.append(record["atlas_role_assignment_id"])
        if record.get("record_type") == "possible_atlas_update_candidate" and record.get("source") == "survey":
            if record.get("lifecycle", {}).get("promotion_state") == "promoted":
                offenders.append(record["update_candidate_id"])
    return _check("survey_does_not_auto_promote_weak_evidence", not offenders, _offender_detail(offenders, "Survey records remain provisional/candidate-level."))


def _check_mission_review_does_not_auto_promote(records: List[Dict[str, Any]]) -> Dict[str, str]:
    offenders = []
    for record in records_by_type(records, "possible_atlas_update_candidate"):
        if record.get("source") != "mission_review":
            continue
        if record.get("review_requirement", {}).get("required") is not True:
            offenders.append(f"{record['update_candidate_id']} missing review requirement")
        if record.get("lifecycle", {}).get("promotion_state") == "promoted":
            offenders.append(f"{record['update_candidate_id']} promoted")
    return _check("mission_review_does_not_auto_promote", not offenders, _offender_detail(offenders, "Mission Review writes review-gated possible updates only."))


def _check_signal_auditability(records: List[Dict[str, Any]]) -> Dict[str, str]:
    signal_ids = {record["signal_id"] for record in records_by_type(records, "signal")}
    offenders = []
    for record in records:
        record_type = record.get("record_type")
        if record_type == "atlas_role_assignment":
            missing = [signal_id for signal_id in record.get("evidence_signal_ids", []) if signal_id not in signal_ids]
            if not record.get("evidence_signal_ids") or missing:
                offenders.append(record["atlas_role_assignment_id"])
        elif record_type == "possible_atlas_update_candidate":
            missing = [signal_id for signal_id in record.get("source_signal_ids", []) if signal_id not in signal_ids]
            if not record.get("source_signal_ids") or missing:
                offenders.append(record["update_candidate_id"])
        elif record_type == "atlas_node":
            missing = [signal_id for signal_id in record.get("evidence_signal_ids", []) if signal_id not in signal_ids]
            if not record.get("evidence_signal_ids") or missing:
                offenders.append(record["atlas_node_id"])
        elif record_type == "user_vocabulary_term":
            missing = [signal_id for signal_id in record.get("source_signal_ids", []) if signal_id not in signal_ids]
            if not record.get("source_signal_ids") or missing:
                offenders.append(record["term_id"])
        elif record_type == "user_taste_feature_state":
            missing = [signal_id for signal_id in record.get("evidence_signal_ids", []) if signal_id not in signal_ids]
            if not record.get("evidence_signal_ids") or missing:
                offenders.append(record["user_taste_feature_state_id"])
    return _check("signal_auditability", not offenders, _offender_detail(offenders, "All stateful records link back to evidence signals."))


def _check_signal_strength_separated(records: List[Dict[str, Any]]) -> Dict[str, str]:
    offenders = []
    skip_seen = False
    note_seen = False
    for signal in records_by_type(records, "signal"):
        if "signal_strength" not in signal or "interpretation_confidence" not in signal:
            offenders.append(signal["signal_id"])
            continue
        if signal["event_type"] == "skip":
            skip_seen = True
            if signal["interpretation_confidence"] > 0.3:
                offenders.append(f"{signal['signal_id']} skip confidence too high")
        if signal["event_type"] == "note":
            note_seen = True
            if signal["interpretation_confidence"] <= signal["signal_strength"]:
                offenders.append(f"{signal['signal_id']} note confidence not separated")
    if not skip_seen:
        offenders.append("no skip signal")
    if not note_seen:
        offenders.append("no note signal")
    return _check("signal_strength_separated_from_interpretation_confidence", not offenders, _offender_detail(offenders, "Signals expose signal_strength separately from interpretation_confidence."))


def _check_candidate_pool_behavior_present(records: List[Dict[str, Any]], expanded_digest: Dict[str, Any]) -> Dict[str, str]:
    offenders = []
    for record in records_by_type(records, "atlas_role_assignment"):
        if not record.get("candidate_pool_behavior"):
            offenders.append(record["atlas_role_assignment_id"])
    for update in records_by_type(records, "possible_atlas_update_candidate"):
        payload = update.get("proposed_payload", {})
        if update.get("proposed_record_type") == "atlas_role_assignment" and not payload.get("candidate_pool_behavior"):
            offenders.append(update["update_candidate_id"])
    if not expanded_digest.get("candidate_pool_behavior_summaries"):
        offenders.append("expanded_digest.candidate_pool_behavior_summaries")
    return _check("candidate_pool_behavior_present", not offenders, _offender_detail(offenders, "Role/update records and digest summaries include candidate_pool_behavior."))


def _check_composition_placeholder_support(records: List[Dict[str, Any]]) -> Dict[str, str]:
    found = False
    for record in records:
        refs = []
        if record.get("record_type") == "signal":
            refs.append(record.get("subject_music_object_ref"))
        if record.get("record_type") == "atlas_node":
            refs.append(record.get("music_object_ref"))
        for ref in refs:
            if isinstance(ref, dict) and ref.get("object_type") == "composition_placeholder":
                found = True
                if ref.get("composition_policy_status") != "composition_first_required":
                    return _check("composition_placeholder_support", False, f"{record.get('record_type')} has composition placeholder without composition_first_required.")
    return _check("composition_placeholder_support", found, "Composition-placeholder evidence validates without pretending final composition layer exists." if found else "No composition-placeholder evidence found.")


def _check_vocabulary_terms_not_automatically_canon(records: List[Dict[str, Any]]) -> Dict[str, str]:
    offenders = [
        term["term_id"]
        for term in records_by_type(records, "user_vocabulary_term")
        if term.get("lifecycle", {}).get("promotion_state") == "promoted"
    ]
    return _check("vocabulary_terms_not_automatically_canon", not offenders, _offender_detail(offenders, "Vocabulary terms remain candidate-level until recurrence/review."))


def _check_digest_emits_mission_usable_summaries(
    digest_record: Dict[str, Any],
    expanded_digest: Dict[str, Any],
    expected_summary: Dict[str, Any],
) -> Dict[str, str]:
    required = set(expected_summary.get("required_digest_sections", []))
    missing = [section for section in sorted(required) if section not in expanded_digest]
    role_ids = digest_record.get("relevant_role_assignment_ids", {})
    if not isinstance(role_ids, dict) or not set(role_ids) >= {"landmarks", "regions", "frontiers", "dead_ends", "waypoints"}:
        missing.append("contract.relevant_role_assignment_ids")
    if not digest_record.get("suggested_candidate_roles"):
        missing.append("contract.suggested_candidate_roles")
    return _check("digest_emits_mission_usable_summaries", not missing, _offender_detail(missing, "Digest has contract IDs and expanded mission/candidate-builder summaries."))


def _signal_sources(records: List[Dict[str, Any]]) -> Dict[str, str]:
    return {record["signal_id"]: record["source"] for record in records_by_type(records, "signal")}


def _check(check_id: str, passed: bool, detail: str) -> Dict[str, str]:
    return {
        "id": check_id,
        "status": "pass" if passed else "fail",
        "detail": detail,
    }


def _offender_detail(offenders: List[str], ok: str) -> str:
    if not offenders:
        return ok
    return "; ".join(offenders)


def _fallback_validate(bundle: Dict[str, Any], schema: Dict[str, Any], reason: str) -> Dict[str, Any]:
    errors = []
    if bundle.get("record_type") != "atlas_example_bundle":
        errors.append({"path": "record_type", "message": "Expected atlas_example_bundle."})
    for index, record in enumerate(bundle.get("records", [])):
        if "record_type" not in record:
            errors.append({"path": f"records.{index}", "message": "Missing record_type."})
        if record.get("schema_version") != "0.1":
            errors.append({"path": f"records.{index}.schema_version", "message": "Expected schema_version 0.1."})
    return {
        "validator": f"fallback_subset ({reason})",
        "valid": not errors,
        "error_count": len(errors),
        "errors": errors,
    }


def _load_json(path: Path) -> Any:
    import json

    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
