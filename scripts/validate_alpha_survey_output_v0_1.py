#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
HANDOFF_DIR = REPO_ROOT / "data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff"
DEFAULT_PAGE_PACKET = HANDOFF_DIR / "public_profile_01_A2_Al1_S1_alpha_survey_page_packet.json"
DEFAULT_PAGE_PACKET_SCHEMA = HANDOFF_DIR / "alpha_survey_page_packet_v0_1.schema.json"
DEFAULT_EVIDENCE_EXPORT = HANDOFF_DIR / "public_profile_01_A2_Al1_S1_survey_evidence_export.json"
DEFAULT_REPORT = HANDOFF_DIR / "alpha_survey_output_validation_report.md"

EXPECTED_STATES = {
    "love": "positive_high",
    "like": "positive_medium",
    "ok": "waypoint_context",
    "dont_like": "negative_scope_carefully",
    "dont_know_enough": "familiarity_uncertainty",
}

EXPECTED_ATLAS_FLOW = [
    "Survey Evidence Export",
    "Signal",
    "AtlasNode",
    "provisional AtlasRoleAssignment",
    "PossibleAtlasUpdateCandidate",
    "AtlasDigestView",
]

FORBIDDEN_KEYS = {
    "adaptive_context",
    "display_label",
    "fake_profile_id",
    "generation_prompt",
    "generator_visible_inputs",
    "hidden_anti_affinities",
    "hidden_lookup_status",
    "hidden_reaction_corpus_id",
    "lookup_status",
    "object_id",
    "page_mode",
    "primary_archetype_affinities",
    "probable_affinity_score",
    "randomization_seed",
    "raw_model_output",
    "reason_tags",
    "scores",
    "secondary_archetype_affinities",
    "suppression_warnings",
    "target_mix",
    "tile_id",
}

FORBIDDEN_TEXT_MARKERS = {
    "hidden_truth",
    "hidden_reaction_corpus",
    "hidden corpus",
    "hidden reason",
    "lookup_status",
    "raw_response_",
    "generated_taste_profiles",
    "profile_writer_output",
}


class ValidationError(Exception):
    pass


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValidationError(f"Missing file: {path}") from None
    except json.JSONDecodeError as error:
        raise ValidationError(f"Invalid JSON in {path}: {error}") from None


def format_path(path_parts: Iterable[object]) -> str:
    parts = [str(part) for part in path_parts]
    return ".".join(parts) if parts else "<root>"


def iter_keys(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from iter_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_keys(child)


def validate_schema(schema_path: Path, document_path: Path) -> list[str]:
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ModuleNotFoundError:
        raise ValidationError("Missing dependency: jsonschema") from None

    schema = load_json(schema_path)
    document = load_json(document_path)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [
        f"{format_path(error.path)}: {error.message}"
        for error in sorted(validator.iter_errors(document), key=lambda item: list(item.path))
    ]


def all_tiles(packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [tile for page in packet["pages"] for tile in page["tiles"]]


def check_no_private_or_construction_data(packet: dict[str, Any]) -> list[str]:
    errors = []
    exported_keys = set(iter_keys(packet))
    for key in sorted(exported_keys & FORBIDDEN_KEYS):
        errors.append(f"Forbidden key in app page packet: `{key}`")
    serialized = json.dumps(packet, sort_keys=True).lower()
    for marker in sorted(FORBIDDEN_TEXT_MARKERS):
        if marker in serialized:
            errors.append(f"Forbidden private/debug marker in app page packet: `{marker}`")
    return errors


def check_response_states(packet: dict[str, Any]) -> list[str]:
    errors = []
    states = {item["state"]: item["normalized_operation"] for item in packet["response_state_contract"]}
    if states != EXPECTED_STATES:
        errors.append(f"response_state_contract mismatch: {states}")
    for tile in all_tiles(packet):
        capture = tile["response_capture"]
        if set(capture["allowed_states"]) != set(EXPECTED_STATES):
            errors.append(f"{tile['evidence_ref']} does not preserve all five response states")
        expected_op = EXPECTED_STATES[capture["captured_state"]]
        if capture["normalized_operation"] != expected_op:
            errors.append(
                f"{tile['evidence_ref']} maps {capture['captured_state']} to "
                f"{capture['normalized_operation']}, expected {expected_op}"
            )
    return errors


def check_capture_fields(packet: dict[str, Any]) -> list[str]:
    errors = []
    contract = packet.get("tag_and_note_contract", {})
    if contract.get("selected_tags", {}).get("signal_semantics") != "visible_signal_evidence":
        errors.append("tag_and_note_contract.selected_tags is not marked visible Signal evidence")
    if contract.get("shown_unselected_tags", {}).get("signal_semantics") != "weak_non_selected_context":
        errors.append("tag_and_note_contract.shown_unselected_tags is not marked weak/non-selected context")
    for tile in all_tiles(packet):
        capture = tile["response_capture"]
        if not isinstance(capture.get("selected_tags"), list):
            errors.append(f"{tile['evidence_ref']} selected_tags is not an array")
        if not isinstance(capture.get("shown_unselected_tags"), list):
            errors.append(f"{tile['evidence_ref']} shown_unselected_tags is not an array")
        if capture.get("selected_tags_semantics") != "visible_signal_evidence":
            errors.append(f"{tile['evidence_ref']} selected_tags_semantics is not visible_signal_evidence")
        if capture.get("shown_unselected_tags_semantics") != "weak_non_selected_context":
            errors.append(f"{tile['evidence_ref']} shown_unselected_tags_semantics is not weak_non_selected_context")
        overlap = set(capture.get("selected_tags") or []).intersection(capture.get("shown_unselected_tags") or [])
        if overlap:
            errors.append(
                f"{tile['evidence_ref']} tags cannot be both selected evidence and non-selected context: "
                f"{sorted(overlap)}"
            )
        if "note" not in capture:
            errors.append(f"{tile['evidence_ref']} missing note field")
    return errors


def check_apple_priors(packet: dict[str, Any]) -> list[str]:
    errors = []
    for tile in all_tiles(packet):
        prior = tile["apple_exposure_prior"]
        if prior["interpretation"] != "exposure_prior":
            errors.append(f"{tile['evidence_ref']} Apple prior is not exposure_prior")
        if prior["taste_truth"] is not False:
            errors.append(f"{tile['evidence_ref']} Apple prior is taste truth")
        if "probable_affinity_score" in prior.get("dimensions", {}):
            errors.append(f"{tile['evidence_ref']} exports probable_affinity_score")
    return errors


def check_approved_graph_surfaces(packet: dict[str, Any]) -> list[str]:
    errors = []
    for tile in all_tiles(packet):
        surface = tile["approved_graph_surface_ref"]
        if surface["review_status"] != "approved":
            errors.append(f"{tile['evidence_ref']} is not backed by an approved graph surface")
    return errors


def check_target_atlas_flow(packet: dict[str, Any]) -> list[str]:
    actual = packet.get("evidence_export_compatibility", {}).get("target_atlas_flow")
    if actual != EXPECTED_ATLAS_FLOW:
        return [f"target_atlas_flow mismatch: {actual}"]
    return []


def check_evidence_export_compatibility(packet: dict[str, Any], evidence_export: dict[str, Any]) -> list[str]:
    errors = []
    atom_by_ref = {
        atom["evidence_ref"]: atom
        for atom in evidence_export["atlas_ingestable"]["evidence_atoms"]
    }
    tiles = all_tiles(packet)
    if len(atom_by_ref) != len(tiles):
        errors.append(f"Evidence atom count {len(atom_by_ref)} != app tile count {len(tiles)}")
    for tile in tiles:
        atom = atom_by_ref.get(tile["evidence_ref"])
        if atom is None:
            errors.append(f"{tile['evidence_ref']} missing from evidence export")
            continue
        if atom["response_id"] != tile["response_id"]:
            errors.append(f"{tile['evidence_ref']} response_id mismatch")
        if atom["reaction"]["raw_value"] != tile["response_capture"]["captured_state"]:
            errors.append(f"{tile['evidence_ref']} reaction mismatch between app packet and evidence export")
        if atom["reaction"]["normalized_operation"] != tile["response_capture"]["normalized_operation"]:
            errors.append(f"{tile['evidence_ref']} normalized operation mismatch")
        if atom["apple_exposure_prior"]["taste_truth"] is not False:
            errors.append(f"{tile['evidence_ref']} evidence export Apple prior is taste truth")
        atom_tags = atom.get("tags", {})
        if atom_tags.get("selected_semantics") != tile["response_capture"].get("selected_tags_semantics"):
            errors.append(f"{tile['evidence_ref']} selected tag semantics mismatch")
        if atom_tags.get("shown_but_unselected_semantics") != tile["response_capture"].get("shown_unselected_tags_semantics"):
            errors.append(f"{tile['evidence_ref']} shown-unselected tag semantics mismatch")
        for ref in atom["supporting_visible_response_refs"]:
            if ref["evidence_ref"] not in atom_by_ref:
                errors.append(f"{tile['evidence_ref']} evidence export has unresolved supporting ref")
    return errors


def validate(page_packet_path: Path, schema_path: Path, evidence_export_path: Path) -> list[str]:
    errors = validate_schema(schema_path, page_packet_path)
    packet = load_json(page_packet_path)
    evidence_export = load_json(evidence_export_path)
    errors.extend(check_no_private_or_construction_data(packet))
    errors.extend(check_response_states(packet))
    errors.extend(check_capture_fields(packet))
    errors.extend(check_apple_priors(packet))
    errors.extend(check_approved_graph_surfaces(packet))
    errors.extend(check_target_atlas_flow(packet))
    errors.extend(check_evidence_export_compatibility(packet, evidence_export))
    return errors


def write_report(report_path: Path, page_packet_path: Path, evidence_export_path: Path, errors: list[str]) -> None:
    status = "passed" if not errors else "failed"
    body = [
        "# Alpha Survey Output v0.1 Validation Report",
        "",
        f"- Page packet: `{page_packet_path.relative_to(REPO_ROOT)}`",
        f"- Evidence export: `{evidence_export_path.relative_to(REPO_ROOT)}`",
        f"- Status: `{status}`",
        "",
        "## Checks",
        "",
        "- app page packet JSON Schema compliance",
        "- five response states preserved",
        "- selected/shown-unselected tag arrays and note field present",
        "- selected tags marked as visible Signal evidence",
        "- shown-unselected tags marked as weak/non-selected context",
        "- Apple data exported as exposure prior with `taste_truth: false`",
        "- approved canonical graph survey surface backing for each tile",
        "- private simulator truth and construction/debug data excluded",
        "- one Survey Evidence Export v0.1 atom per visible app response",
        "- target Atlas flow preserved from export to digest",
        "- response/reaction/linkage compatibility between app packet and evidence export",
        "",
    ]
    if errors:
        body.append("## Errors")
        body.append("")
        for error in errors:
            body.append(f"- {error}")
    else:
        body.append("No validation errors found.")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(body) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Alpha app-renderable Survey output v0.1.")
    parser.add_argument("--page-packet", type=Path, default=DEFAULT_PAGE_PACKET)
    parser.add_argument("--schema", type=Path, default=DEFAULT_PAGE_PACKET_SCHEMA)
    parser.add_argument("--evidence-export", type=Path, default=DEFAULT_EVIDENCE_EXPORT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    page_packet_path = args.page_packet.resolve()
    schema_path = args.schema.resolve()
    evidence_export_path = args.evidence_export.resolve()
    report_path = args.report.resolve()

    try:
        errors = validate(page_packet_path, schema_path, evidence_export_path)
    except ValidationError as error:
        print(f"INVALID: {error}", file=sys.stderr)
        return 2

    write_report(report_path, page_packet_path, evidence_export_path, errors)
    if errors:
        print(f"INVALID: Alpha Survey Output failed {len(errors)} check(s)")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"OK: Alpha Survey Output validates at {page_packet_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
