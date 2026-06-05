#!/usr/bin/env python3
"""Validate MissionEnrichmentOutput_v0_2 against schema and product rules."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import jsonschema
except ImportError as exc:  # pragma: no cover - exercised only in missing dependency environments.
    jsonschema = None
    JSONSCHEMA_IMPORT_ERROR = exc
else:
    JSONSCHEMA_IMPORT_ERROR = None


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
INPUT_SCHEMA_PATH = PACKAGE_ROOT / "schemas" / "mission_enrichment_input_v0_2.schema.json"
OUTPUT_SCHEMA_PATH = PACKAGE_ROOT / "schemas" / "mission_enrichment_output_v0_2.schema.json"
REGISTRY_SCHEMA_PATH = PACKAGE_ROOT / "schemas" / "secondary_reaction_tag_registry_v0_2.schema.json"
DEFAULT_REGISTRY_PATH = PACKAGE_ROOT / "registry" / "secondary_reaction_tag_registry_v0_2.json"

RAW_AFFINITY_RE = re.compile(r"\b[a-z_]+:[a-z0-9_]+\b")
RAW_ID_RE = re.compile(r"\b(?:MISSION|ITEM|SONG|CANONICAL|GRAPH|REGION|PATTERN|BOUNDARY)_[A-Z0-9_]+\b|canonical_[a-z0-9_]+|song_[a-z0-9_]+", re.IGNORECASE)
BANNED_COPY_PATTERNS = [
    "slop",
    "true taste",
    "final map",
    "cartenza knows",
    "you love",
    "you are",
    "objectively",
    "obviously",
    "final truth",
]
FINAL_TASTE_PATTERNS = [
    "your identity",
    "your permanent",
    "we know",
    "cartenza learned",
]

VOICE_TAGS = {"VOICE_WORKED", "VOICE_DID_NOT_WORK"}
LYRIC_STORY_TAGS = {"LYRICS_WORKED", "LYRICS_DID_NOT_WORK", "STORY_WORKED"}
REQUIRED_COMPLETION_CONDITIONS = {"mostly_positive", "mixed", "mostly_negative"}
CONTEXT_MISSION_TYPES = {"album_container_test", "context_dependence_test"}


@dataclass
class ValidationReport:
    passed: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, message: str) -> None:
        self.passed = False
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def as_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings,
        }


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _schema_validate(instance: Any, schema_path: Path, report: ValidationReport, label: str) -> None:
    if jsonschema is None:
        report.error(f"jsonschema is not available; cannot validate {label}: {JSONSCHEMA_IMPORT_ERROR}")
        return
    schema = load_json(schema_path)
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda err: list(err.path))
    for error in errors:
        path = "/".join(str(part) for part in error.path) or "<root>"
        report.error(f"{label} schema error at {path}: {error.message}")


def _copy_strings(output: dict[str, Any]) -> list[tuple[str, str]]:
    strings: list[tuple[str, str]] = []
    mission_copy = output.get("mission_copy", {})
    for field_name in ("title", "subtitle", "short_description", "why_now", "mission_hypothesis_user_facing"):
        value = mission_copy.get(field_name)
        if isinstance(value, str):
            strings.append((f"mission_copy.{field_name}", value))
    for idx, value in enumerate(mission_copy.get("listen_for", [])):
        if isinstance(value, str):
            strings.append((f"mission_copy.listen_for[{idx}]", value))
    for item_idx, item_copy in enumerate(output.get("route_item_copy", [])):
        for field_name in ("pre_play_line", "why_this_song"):
            value = item_copy.get(field_name)
            if isinstance(value, str):
                strings.append((f"route_item_copy[{item_idx}].{field_name}", value))
        for idx, value in enumerate(item_copy.get("listen_for", [])):
            if isinstance(value, str):
                strings.append((f"route_item_copy[{item_idx}].listen_for[{idx}]", value))
    return strings


def _has_artist_context(route_item: dict[str, Any], mission_type: str, user_brief: dict[str, Any]) -> bool:
    if route_item.get("artist_context_available") is True:
        return True
    if mission_type == "artist_depth_test":
        return True
    for section in ("confirmed_positive_patterns", "open_questions", "known_boundaries"):
        for entry in user_brief.get(section, []):
            if "artist" in entry.get("label", "").lower():
                return True
    return False


def _has_context_gate(route_item: dict[str, Any], mission_type: str) -> bool:
    flags = route_item.get("applicability_flags", {})
    facets = {entry["facet"] for entry in route_item.get("song_affinity_tags", [])}
    return (
        mission_type in CONTEXT_MISSION_TYPES
        or flags.get("album_context_relevant") is True
        or flags.get("long_form_context_relevant") is True
        or "context_rule" in facets
        or "activity_context" in facets
        or "social_context" in facets
    )


def validate_contract(
    input_payload: dict[str, Any],
    output_payload: dict[str, Any],
    registry_payload: dict[str, Any],
) -> ValidationReport:
    report = ValidationReport()

    _schema_validate(input_payload, INPUT_SCHEMA_PATH, report, "input")
    _schema_validate(output_payload, OUTPUT_SCHEMA_PATH, report, "output")
    _schema_validate(registry_payload, REGISTRY_SCHEMA_PATH, report, "registry")

    registry = registry_payload.get("tags", {})
    allowed_registry = input_payload.get("allowed_secondary_reaction_tags", {})
    mission_context = input_payload.get("mission_context", {})
    mission_type = mission_context.get("mission_type", "")
    user_brief = input_payload.get("user_atlas_context_brief", {})
    max_tags = input_payload.get("runtime_context", {}).get("max_secondary_tags_per_song", 6)
    route_items = sorted(input_payload.get("route_items", []), key=lambda item: item.get("sequence", 0))
    route_ids = [item.get("item_id") for item in route_items]
    route_by_id = {item.get("item_id"): item for item in route_items}

    if output_payload.get("mission_id") != mission_context.get("mission_id"):
        report.error("mission_id does not match input mission_context.mission_id")

    route_copy_ids = [item.get("item_id") for item in output_payload.get("route_item_copy", [])]
    if route_copy_ids != route_ids:
        report.error(f"route_item_copy item order/coverage mismatch: expected {route_ids}, got {route_copy_ids}")

    candidate_item_ids = [item.get("item_id") for item in output_payload.get("secondary_reaction_tag_candidates", [])]
    if candidate_item_ids != route_ids:
        report.error(f"secondary_reaction_tag_candidates item order/coverage mismatch: expected {route_ids}, got {candidate_item_ids}")

    conditions = {seed.get("condition") for seed in output_payload.get("post_completion_interpretation_seeds", [])}
    if conditions != REQUIRED_COMPLETION_CONDITIONS:
        report.error(f"post_completion_interpretation_seeds conditions mismatch: expected {sorted(REQUIRED_COMPLETION_CONDITIONS)}, got {sorted(conditions)}")

    for candidate_block in output_payload.get("secondary_reaction_tag_candidates", []):
        item_id = candidate_block.get("item_id")
        route_item = route_by_id.get(item_id)
        if route_item is None:
            report.error(f"secondary tag block references unknown route item {item_id!r}")
            continue

        prefiltered = set(route_item.get("prefiltered_secondary_tag_ids", []))
        song_tags = {entry["tag"] for entry in route_item.get("song_affinity_tags", [])}
        alignments = {entry["alignment"] for entry in route_item.get("user_alignment_hints", [])}
        flags = route_item.get("applicability_flags", {})
        tags = candidate_block.get("tags", [])

        if len(tags) > max_tags:
            report.error(f"{item_id}: more than {max_tags} secondary tags")

        seen: set[str] = set()
        for expected_rank, tag in enumerate(tags, start=1):
            tag_id = tag.get("tag_id")
            if tag_id in seen:
                report.error(f"{item_id}: duplicate tag_id {tag_id}")
            seen.add(tag_id)

            if tag.get("rank") != expected_rank:
                report.error(f"{item_id}: tag {tag_id} rank must be sequential; expected {expected_rank}, got {tag.get('rank')}")

            registry_tag = registry.get(tag_id)
            allowed_tag = allowed_registry.get(tag_id)
            if registry_tag is None:
                report.error(f"{item_id}: unknown registry tag_id {tag_id}")
                continue
            if allowed_tag is None:
                report.error(f"{item_id}: tag_id {tag_id} is not present in allowed_secondary_reaction_tags")
            if tag_id not in prefiltered:
                report.error(f"{item_id}: tag_id {tag_id} is not prefiltered for this route item")

            if tag.get("display_label") != registry_tag.get("display_label"):
                report.error(f"{item_id}: display_label mismatch for {tag_id}")
            if tag.get("atlas_effect") != registry_tag.get("atlas_effect"):
                report.error(f"{item_id}: atlas_effect mismatch for {tag_id}")

            valid_primary = set(tag.get("valid_primary_reactions", []))
            registry_valid = set(registry_tag.get("valid_primary_reactions", []))
            if not valid_primary or not valid_primary <= registry_valid:
                report.error(f"{item_id}: invalid primary reactions for {tag_id}: {sorted(valid_primary)}")

            if tag_id == "LESS_LIKE_THIS" and valid_primary != {"dislike"}:
                report.error(f"{item_id}: LESS_LIKE_THIS must be dislike-only")
            if tag_id == "RIGHT_ARTIST_WRONG_TRACK" and not _has_artist_context(route_item, mission_type, user_brief):
                report.error(f"{item_id}: RIGHT_ARTIST_WRONG_TRACK requires artist context")
            if tag_id == "NEEDS_MORE_CONTEXT" and not _has_context_gate(route_item, mission_type):
                report.error(f"{item_id}: NEEDS_MORE_CONTEXT requires album/context/long-form applicability")
            if tag_id in VOICE_TAGS and (flags.get("has_vocals") is False or flags.get("is_instrumental") is True):
                report.error(f"{item_id}: {tag_id} is not allowed without applicable vocals")
            if tag_id in LYRIC_STORY_TAGS and (
                flags.get("has_lyrics") is False
                or flags.get("lyrics_language_known") is False
                or flags.get("is_instrumental") is True
            ):
                report.error(f"{item_id}: {tag_id} is not allowed without applicable lyrics/story evidence")

            linked_song_tags = set(tag.get("linked_song_affinity_tags", []))
            if not linked_song_tags <= song_tags:
                report.error(f"{item_id}: linked_song_affinity_tags contain tags not on route item for {tag_id}")

            linked_alignments = set(tag.get("linked_user_alignment_hints", []))
            if not linked_alignments <= alignments:
                report.error(f"{item_id}: linked_user_alignment_hints contain hints not on route item for {tag_id}")

            target_labels = tag.get("atlas_signal_target", {}).get("target_labels", [])
            for label in target_labels:
                if RAW_AFFINITY_RE.search(label) or RAW_ID_RE.search(label):
                    report.error(f"{item_id}: atlas_signal_target target label is not display-safe for {tag_id}")

    for location, value in _copy_strings(output_payload):
        lowered = value.lower()
        if RAW_AFFINITY_RE.search(value):
            report.error(f"{location}: display copy exposes a raw affinity tag")
        if RAW_ID_RE.search(value):
            report.error(f"{location}: display copy exposes a raw graph/canonical ID")
        for pattern in BANNED_COPY_PATTERNS:
            if pattern in lowered:
                report.error(f"{location}: display copy uses banned/founder-specific language {pattern!r}")
        for pattern in FINAL_TASTE_PATTERNS:
            if pattern in lowered:
                report.error(f"{location}: display copy makes or implies final taste truth via {pattern!r}")

    return report


def write_markdown_report(report: ValidationReport, path: Path) -> None:
    lines = [
        "# Mission Enrichment Validation Report v0.2",
        "",
        f"Passed: `{str(report.passed).lower()}`",
        f"Errors: {len(report.errors)}",
        f"Warnings: {len(report.warnings)}",
        "",
        "## Errors",
        "",
    ]
    lines.extend([f"- {error}" for error in report.errors] or ["- None"])
    lines.extend(["", "## Warnings", ""])
    lines.extend([f"- {warning}" for warning in report.warnings] or ["- None"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--registry", default=DEFAULT_REGISTRY_PATH, type=Path)
    parser.add_argument("--report-json", type=Path)
    parser.add_argument("--report-md", type=Path)
    args = parser.parse_args()

    input_payload = load_json(args.input)
    output_payload = load_json(args.output)
    registry_payload = load_json(args.registry)
    report = validate_contract(input_payload, output_payload, registry_payload)

    if args.report_json:
        args.report_json.parent.mkdir(parents=True, exist_ok=True)
        args.report_json.write_text(json.dumps(report.as_dict(), indent=2) + "\n")
    if args.report_md:
        write_markdown_report(report, args.report_md)

    print(json.dumps(report.as_dict(), indent=2))
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
