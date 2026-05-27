#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from collections.abc import Iterable
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = REPO_ROOT / "data/survey_simulation"
EXPORT_DIR = SIM_DIR / "survey_evidence_export"
DEFAULT_EXPORT = EXPORT_DIR / "samples" / "public_profile_01_A3_Al1_S2_survey_evidence_export.json"
DEFAULT_SCHEMA = EXPORT_DIR / "survey_evidence_export_v0_1.schema.json"
DEFAULT_REPORT = EXPORT_DIR / "survey_evidence_export_v0_1_validation_report.md"


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
    "position",
    "primary_archetype_affinities",
    "randomization_seed",
    "reason_tags",
    "scores",
    "secondary_archetype_affinities",
    "suppression_warnings",
    "target_mix",
    "tile_id",
}

FORBIDDEN_TEXT_MARKERS = {
    "hidden_truth_packet",
    "hidden_reaction_corpus",
    "hidden corpus",
    "hidden reason",
    "lookup_status",
    "raw_response_",
    "generated_taste_profiles",
}

EXPECTED_REACTION_OPERATIONS = {
    "love": ("positive_high", "positive"),
    "like": ("positive_medium", "positive"),
    "ok": ("waypoint_context", "contextual"),
    "dont_like": ("negative_scope_carefully", "negative"),
    "dont_know_enough": ("familiarity_uncertainty", "none"),
}

EXPECTED_EVIDENCE_STRENGTH_HINTS = {
    "love": "strong_positive_basis",
    "like": "medium_positive_basis",
    "ok": "waypoint_or_context_basis",
    "dont_like": "negative_scope_basis",
    "dont_know_enough": "familiarity_uncertainty_basis",
}

QUARANTINE_REASONS = {
    "missing_displayed_page",
    "missing_tile_or_ref",
    "invalid_response_state",
    "duplicate_response",
    "schema_mismatch",
    "non_visible_construction_data",
    "apple_only_unmatched_object",
}


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValidationError(f"Missing file: {path}") from None
    except json.JSONDecodeError as error:
        raise ValidationError(f"Invalid JSON in {path}: {error}") from None


class ValidationError(Exception):
    pass


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


def validate_schema(schema_path: Path, export_path: Path) -> list[str]:
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ModuleNotFoundError:
        raise ValidationError("Missing dependency: jsonschema") from None

    schema = load_json(schema_path)
    document = load_json(export_path)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [
        f"{format_path(error.path)}: {error.message}"
        for error in sorted(validator.iter_errors(document), key=lambda item: list(item.path))
    ]


def check_no_forbidden_keys(document: dict[str, Any]) -> list[str]:
    errors = []
    for key in sorted(set(iter_keys(document)) & FORBIDDEN_KEYS):
        errors.append(f"Forbidden key exported: `{key}`")
    serialized = json.dumps(document, sort_keys=True).lower()
    for marker in sorted(FORBIDDEN_TEXT_MARKERS):
        if marker in serialized:
            errors.append(f"Forbidden private/debug marker exported: `{marker}`")
    return errors


def check_music_object_refs(atoms: list[dict[str, Any]]) -> list[str]:
    errors = []
    for atom in atoms:
        ref = atom["music_object_ref"]
        object_type = ref["object_type"]
        if object_type == "artist" and "canonical_artist_id" not in ref:
            errors.append(f"{atom['evidence_ref']} missing canonical_artist_id")
        if object_type == "album" and "canonical_album_id" not in ref:
            errors.append(f"{atom['evidence_ref']} missing canonical_album_id")
        if object_type == "song_recording" and "canonical_song_recording_id" not in ref:
            errors.append(f"{atom['evidence_ref']} missing canonical_song_recording_id")
    return errors


def check_response_ref_integrity(export: dict[str, Any]) -> list[str]:
    errors = []
    atoms = export["atlas_ingestable"]["evidence_atoms"]
    evidence_refs = {atom["evidence_ref"] for atom in atoms}
    response_ids = {atom["response_id"] for atom in atoms}

    if len(evidence_refs) != len(atoms):
        errors.append("Duplicate evidence_ref values found in Atlas-ingestable atoms")
    if len(response_ids) != len(atoms):
        errors.append("Duplicate response_id values found in Atlas-ingestable atoms")

    index = export["atlas_ingestable"]["response_ref_index"]
    if set(index["evidence_refs"]) != evidence_refs:
        errors.append("response_ref_index.evidence_refs does not match evidence atoms")
    if set(index["response_ids"]) != response_ids:
        errors.append("response_ref_index.response_ids does not match evidence atoms")

    for atom in atoms:
        own_ref = atom["evidence_ref"]
        if own_ref not in evidence_refs:
            errors.append(f"{own_ref} does not resolve to a visible atom")
        for ref in atom["comparison_set"]["peer_response_refs"]:
            if ref not in evidence_refs:
                errors.append(f"{own_ref} has unresolved comparison_set peer ref: {ref}")
        if atom["comparison_set"]["peer_count"] != len(atom["comparison_set"]["peer_response_refs"]):
            errors.append(f"{own_ref} comparison_set peer_count mismatch")
        for ref in atom["supporting_visible_response_refs"]:
            evidence_ref = ref["evidence_ref"]
            if evidence_ref not in evidence_refs:
                errors.append(f"{own_ref} has unresolved supporting response ref: {evidence_ref}")

    quarantined = export["construction_only_excluded"]["quarantined_response_refs"]
    for item in quarantined:
        reason = item.get("reason")
        if reason not in QUARANTINE_REASONS:
            errors.append(f"Unknown quarantine reason `{reason}` for {item.get('source_response_id')}")
        if item["unresolved_response_ref"] in evidence_refs:
            errors.append(
                "construction_only_excluded quarantined a response ref that actually "
                f"resolves inside the export: {item['unresolved_response_ref']}"
            )
    return errors


def response_count_summary(export: dict[str, Any]) -> dict[str, Any]:
    atoms = export["atlas_ingestable"]["evidence_atoms"]
    quarantined = export["construction_only_excluded"]["quarantined_response_refs"]
    reason_counts = Counter(item.get("reason", "unknown") for item in quarantined)
    return {
        "total_responses": len(atoms) + len(quarantined),
        "atlas_ingestable_count": len(atoms),
        "quarantined_count": len(quarantined),
        "quarantine_reason_counts": dict(sorted(reason_counts.items())),
    }


def check_reaction_operations(atoms: list[dict[str, Any]]) -> list[str]:
    errors = []
    for atom in atoms:
        reaction = atom["reaction"]
        raw = reaction["raw_value"]
        expected_operation, expected_polarity = EXPECTED_REACTION_OPERATIONS[raw]
        if reaction["normalized_operation"] != expected_operation:
            errors.append(
                f"{atom['evidence_ref']} maps {raw} to {reaction['normalized_operation']}, "
                f"expected {expected_operation}"
            )
        if reaction["taste_polarity"] != expected_polarity:
            errors.append(
                f"{atom['evidence_ref']} maps {raw} to polarity {reaction['taste_polarity']}, "
                f"expected {expected_polarity}"
            )
        if raw == "dont_know_enough" and (
            reaction["normalized_operation"] != "familiarity_uncertainty"
            or reaction["taste_polarity"] == "negative"
            or reaction["atlas_signal"] == "negative_scope_carefully"
        ):
            errors.append(f"{atom['evidence_ref']} treats dont_know_enough as taste-negative")
        hint = atom["evidence_strength_hint"]
        if hint["hint"] != EXPECTED_EVIDENCE_STRENGTH_HINTS[raw]:
            errors.append(
                f"{atom['evidence_ref']} has evidence_strength_hint {hint['hint']}, "
                f"expected {EXPECTED_EVIDENCE_STRENGTH_HINTS[raw]}"
            )
        if hint["source"] != "survey":
            errors.append(f"{atom['evidence_ref']} evidence_strength_hint source is not survey")
        if hint["is_final_atlas_confidence"] is not False:
            errors.append(f"{atom['evidence_ref']} treats evidence_strength_hint as Atlas confidence")
    return errors


def check_apple_priors(atoms: list[dict[str, Any]]) -> list[str]:
    errors = []
    for atom in atoms:
        prior = atom["apple_exposure_prior"]
        if prior["interpretation"] != "exposure_prior":
            errors.append(f"{atom['evidence_ref']} Apple prior is not exposure_prior")
        if prior["taste_truth"] is not False:
            errors.append(f"{atom['evidence_ref']} Apple prior is treated as taste truth")
        if "probable_affinity_score" in prior.get("dimensions", {}):
            errors.append(f"{atom['evidence_ref']} exports probable_affinity_score to Atlas")
    return errors


def check_tag_semantics(atoms: list[dict[str, Any]]) -> list[str]:
    errors = []
    for atom in atoms:
        tags = atom["tags"]
        selected = set(tags.get("selected") or [])
        shown_unselected = set(tags.get("shown_but_unselected") or [])
        if tags.get("selected_semantics") != "visible_signal_evidence":
            errors.append(f"{atom['evidence_ref']} selected tags are not marked visible Signal evidence")
        if tags.get("shown_but_unselected_semantics") != "weak_non_selected_context":
            errors.append(f"{atom['evidence_ref']} shown-unselected tags are not marked weak/non-selected context")
        overlap = selected.intersection(shown_unselected)
        if overlap:
            errors.append(
                f"{atom['evidence_ref']} tags cannot be both selected evidence and non-selected context: "
                f"{sorted(overlap)}"
            )
    return errors


def validate_export(export_path: Path, schema_path: Path) -> list[str]:
    errors = validate_schema(schema_path, export_path)
    export = load_json(export_path)
    atoms = export.get("atlas_ingestable", {}).get("evidence_atoms", [])
    if export.get("ledger_semantics", {}).get("mode") != "append_only":
        errors.append("ledger_semantics.mode must be append_only")
    errors.extend(check_no_forbidden_keys(export))
    errors.extend(check_music_object_refs(atoms))
    errors.extend(check_response_ref_integrity(export))
    errors.extend(check_reaction_operations(atoms))
    errors.extend(check_apple_priors(atoms))
    errors.extend(check_tag_semantics(atoms))
    return errors


def write_report(report_path: Path, export_path: Path, export: dict[str, Any], errors: list[str]) -> None:
    status = "passed" if not errors else "failed"
    counts = response_count_summary(export)
    body = [
        "# Survey Evidence Export v0.1 Validation Report",
        "",
        f"- Export: `{export_path.relative_to(REPO_ROOT)}`",
        f"- Status: `{status}`",
        f"- Total responses reviewed: `{counts['total_responses']}`",
        f"- Atlas-ingestable responses: `{counts['atlas_ingestable_count']}`",
        f"- Quarantined responses: `{counts['quarantined_count']}`",
        "",
        "## Checks",
        "",
        "- JSON Schema compliance",
        "- private/simulator/debug leakage guard",
        "- raw page-construction payload exclusion",
        "- typed music object refs",
        "- append-only ledger semantics",
        "- `evidence_strength_hint` as Survey-side hint, not Atlas confidence",
        "- selected tags as visible Signal evidence",
        "- shown-unselected tags as weak/non-selected context",
        "- response-ref closure for Atlas-ingestable refs",
        "- `dont_know_enough` as `familiarity_uncertainty`",
        "- Apple Music as `exposure_prior`, not taste truth",
        "- quarantine reason taxonomy and counts",
        "",
    ]
    body.append("## Quarantine Reason Counts")
    body.append("")
    if counts["quarantine_reason_counts"]:
        for reason, count in counts["quarantine_reason_counts"].items():
            body.append(f"- `{reason}`: `{count}`")
    else:
        body.append("- none")
    body.append("")
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
    parser = argparse.ArgumentParser(description="Validate Survey Evidence Export v0.1.")
    parser.add_argument("--export", type=Path, default=DEFAULT_EXPORT)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    export_path = args.export.resolve()
    schema_path = args.schema.resolve()
    report_path = args.report.resolve()

    try:
        errors = validate_export(export_path, schema_path)
    except ValidationError as error:
        print(f"INVALID: {error}", file=sys.stderr)
        return 2

    export = load_json(export_path)
    write_report(report_path, export_path, export, errors)
    if errors:
        print(f"INVALID: Survey Evidence Export failed {len(errors)} check(s)")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"OK: Survey Evidence Export validates at {export_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
