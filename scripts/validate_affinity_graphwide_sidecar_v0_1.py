#!/usr/bin/env python3
"""Validate Cartenza graph-wide affinity sidecar output against Pass D IDs."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


CORE_DIMS = (
    "vocal_performance",
    "emotion_theme",
    "sonic_texture",
    "rhythm_body",
    "form_container",
)
OVERLAY_DIMS = ("social_context", "routing_caution")
REVIEW_CODES = {
    "recording_identity_unclear",
    "tag_definition_ambiguous",
    "missing_tag_candidate",
    "social_context_unclear",
    "routing_caution_unclear",
    "over_tagged",
    "under_tagged",
    "duplicate_context_unclear",
    "context_leak_risk",
    "version_ambiguity",
    "schema_boundary_risk",
}
SONG_ID_FIELDS = ("canonical_song_recording_id", "candidate_identity_key", "song_identity_key")
OVERLAY_MEMBERSHIP_ID_FIELDS = (
    "song_archetype_membership_id",
    "membership_id",
    "v1_membership_id",
)
OVERLAY_SONG_ID_FIELDS = ("canonical_song_recording_id", "candidate_identity_key", "song_identity_key")
OVERLAY_METADATA_FIELDS = {
    *OVERLAY_MEMBERSHIP_ID_FIELDS,
    *OVERLAY_SONG_ID_FIELDS,
    "family_id",
    "family_number",
    "family_scope",
    "archetype_id",
    "archetype_name",
    "membership_roles",
    "mission_role",
    "recognition_band",
    "recognition_tier",
    "risk_status",
    "source_file",
    "source_layer",
    "survey_tier",
    "overlay_notes",
}
DUPLICATE_REVIEW_CODES_BY_TYPE = {
    "context_surface_duplicate": {"duplicate_context_unclear", "context_leak_risk"},
    "composition_variant": {
        "duplicate_context_unclear",
        "recording_identity_unclear",
        "version_ambiguity",
    },
    "version_ambiguity": {"recording_identity_unclear", "version_ambiguity"},
}
SAMPLE_LIMIT = 25


class IssueBuckets:
    def __init__(self) -> None:
        self._buckets: dict[str, dict[str, Any]] = {}

    def add(self, code: str, message: str, sample: dict[str, Any] | None = None) -> None:
        bucket = self._buckets.setdefault(code, {"code": code, "message": message, "count": 0, "samples": []})
        bucket["count"] += 1
        if sample is not None and len(bucket["samples"]) < SAMPLE_LIMIT:
            bucket["samples"].append(sample)

    def count(self, code: str) -> int:
        return int(self._buckets.get(code, {}).get("count", 0))

    def total(self) -> int:
        return sum(int(bucket["count"]) for bucket in self._buckets.values())

    def as_list(self) -> list[dict[str, Any]]:
        return [self._buckets[code] for code in sorted(self._buckets)]


def load_json(path: str | Path) -> Any:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def clean_string(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def is_trueish(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "1", "needed", "required"}
    return bool(value)


def rows_from_doc(doc: Any, key: str, issue_code: str, errors: IssueBuckets) -> list[Any]:
    if isinstance(doc, list):
        return doc
    if isinstance(doc, dict) and isinstance(doc.get(key), list):
        return doc[key]
    errors.add(issue_code, f"Input JSON must be a list or contain a top-level `{key}` list.")
    return []


def tag_rows_from_doc(doc: Any, errors: IssueBuckets) -> list[Any]:
    if isinstance(doc, list):
        return doc
    if isinstance(doc, dict):
        for key in ("songs", "rows", "song_tags"):
            if isinstance(doc.get(key), list):
                return doc[key]
    errors.add("tags_rows_not_found", "Tags JSON must be a list or contain `songs`, `rows`, or `song_tags`.")
    return []


def load_allowed_by_dimension(doc: Any, errors: IssueBuckets) -> dict[str, set[str]]:
    raw: dict[str, Any] = {}
    if isinstance(doc, dict) and isinstance(doc.get("allowed_tags_by_dimension"), dict):
        raw = doc["allowed_tags_by_dimension"]
    elif isinstance(doc, dict):
        canonical = doc.get("canonical_song_affinity_tags_allowed_tags")
        overlays = doc.get("membership_context_overlays_allowed_tags")
        if isinstance(canonical, dict):
            raw.update(canonical)
        if isinstance(overlays, dict):
            raw.update(overlays)

    allowed: dict[str, set[str]] = {}
    for dim in (*CORE_DIMS, *OVERLAY_DIMS):
        values = raw.get(dim)
        if not isinstance(values, list):
            errors.add("allowed_dimension_missing", "Allowed tag file is missing an allowed-tag list for a required dimension.", {"dimension": dim})
            allowed[dim] = set()
            continue
        allowed[dim] = {clean_string(value) for value in values if clean_string(value)}
    return allowed


def first_consistent_id(
    obj: dict[str, Any],
    fields: tuple[str, ...],
    errors: IssueBuckets,
    code: str,
    message: str,
    sample_base: dict[str, Any],
) -> str:
    values = [(field, clean_string(obj.get(field))) for field in fields if clean_string(obj.get(field))]
    distinct = sorted({value for _, value in values})
    if len(distinct) > 1:
        sample = dict(sample_base)
        sample["values"] = {field: value for field, value in values}
        errors.add(code, message, sample)
    return values[0][1] if values else ""


def tags_in_bucket(bucket: Any, path: str, errors: IssueBuckets) -> list[str]:
    if bucket is None:
        return []
    if not isinstance(bucket, dict):
        errors.add("tag_bucket_not_object", "Tag dimension buckets must be objects with `primary` and `secondary` arrays.", {"path": path})
        return []

    tags: list[str] = []
    for slot in ("primary", "secondary"):
        raw_values = bucket.get(slot, [])
        if raw_values is None:
            continue
        if not isinstance(raw_values, list):
            errors.add("tag_bucket_slot_not_array", "`primary` and `secondary` tag slots must be arrays.", {"path": f"{path}.{slot}"})
            continue
        for index, raw_tag in enumerate(raw_values):
            tag = clean_string(raw_tag)
            if not isinstance(raw_tag, str) or not tag:
                errors.add("invalid_tag_value", "Tags must be non-empty strings.", {"path": f"{path}.{slot}[{index}]", "value": raw_tag})
                continue
            tags.append(tag)
    return tags


def looks_like_tag_bucket(value: Any) -> bool:
    return isinstance(value, dict) and ("primary" in value or "secondary" in value)


def validate_tag(
    tag: str,
    dim: str,
    allowed_by_dim: dict[str, set[str]],
    tag_to_dims: dict[str, set[str]],
    errors: IssueBuckets,
    sample: dict[str, Any],
) -> None:
    if tag in allowed_by_dim.get(dim, set()):
        return
    if tag in tag_to_dims:
        rich_sample = dict(sample)
        rich_sample["allowed_dimensions"] = sorted(tag_to_dims[tag])
        errors.add("misplaced_allowed_tag", "Canonical tag appears under the wrong dimension.", rich_sample)
    else:
        errors.add("noncanonical_tag", "Tag is not present in the allowed canonical tag list.", sample)


def review_codes_for_row(row: dict[str, Any], row_index: int, song_id: str, errors: IssueBuckets) -> set[str]:
    codes: set[str] = set()
    sources = (
        ("review.review_reason_codes", row.get("review", {}).get("review_reason_codes") if isinstance(row.get("review"), dict) else None),
        ("review.reason_codes", row.get("review", {}).get("reason_codes") if isinstance(row.get("review"), dict) else None),
        (
            "duplicate_context_review.reason_codes",
            row.get("duplicate_context_review", {}).get("reason_codes") if isinstance(row.get("duplicate_context_review"), dict) else None,
        ),
        (
            "duplicate_context_review.review_reason_codes",
            row.get("duplicate_context_review", {}).get("review_reason_codes") if isinstance(row.get("duplicate_context_review"), dict) else None,
        ),
    )
    for path, raw_codes in sources:
        if raw_codes is None:
            continue
        if not isinstance(raw_codes, list):
            errors.add(
                "review_reason_codes_not_array",
                "Review reason code fields must be arrays.",
                {"row_index": row_index, "song_id": song_id, "path": path},
            )
            continue
        for raw_code in raw_codes:
            code = clean_string(raw_code)
            if not code:
                continue
            codes.add(code)
            if code not in REVIEW_CODES:
                errors.add(
                    "unknown_review_reason_code",
                    "Review reason code is not in the approved QA contract list.",
                    {"row_index": row_index, "song_id": song_id, "path": path, "code": code},
                )
    return codes


def row_has_duplicate_review_flag(row: dict[str, Any], expected_codes: set[str]) -> bool:
    duplicate_review = row.get("duplicate_context_review")
    review = row.get("review")
    if isinstance(duplicate_review, dict):
        if is_trueish(duplicate_review.get("needed")) or is_trueish(duplicate_review.get("duplicate_context_review_needed")):
            return True
        codes = duplicate_review.get("reason_codes") or duplicate_review.get("review_reason_codes")
        if isinstance(codes, list) and expected_codes.intersection(clean_string(code) for code in codes):
            return True
    if isinstance(review, dict):
        if is_trueish(review.get("duplicate_context_review_needed")):
            return True
        codes = review.get("review_reason_codes") or review.get("reason_codes")
        if isinstance(codes, list) and expected_codes.intersection(clean_string(code) for code in codes):
            return True
    if is_trueish(row.get("duplicate_context_review_needed")):
        return True
    return False


def build_pass_d_indexes(pass_d_rows: list[Any], errors: IssueBuckets) -> tuple[dict[str, list[dict[str, Any]]], dict[str, dict[str, Any]]]:
    song_to_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    membership_to_row: dict[str, dict[str, Any]] = {}
    seen_memberships: set[str] = set()

    for index, raw_row in enumerate(pass_d_rows):
        if not isinstance(raw_row, dict):
            errors.add("pass_d_row_not_object", "Pass D rows must be objects.", {"pass_d_row_index": index})
            continue
        song_id = clean_string(raw_row.get("candidate_identity_key"))
        membership_id = clean_string(raw_row.get("v1_membership_id"))
        if not song_id:
            errors.add("pass_d_row_missing_candidate_identity_key", "Pass D row is missing `candidate_identity_key`.", {"pass_d_row_index": index})
            continue
        if not membership_id:
            errors.add("pass_d_row_missing_v1_membership_id", "Pass D row is missing `v1_membership_id`.", {"pass_d_row_index": index, "song_id": song_id})
            continue
        song_to_rows[song_id].append(raw_row)
        if membership_id in seen_memberships:
            errors.add("pass_d_duplicate_v1_membership_id", "Pass D contains a duplicate `v1_membership_id`.", {"v1_membership_id": membership_id})
        seen_memberships.add(membership_id)
        membership_to_row[membership_id] = raw_row

    return dict(song_to_rows), membership_to_row


def build_duplicate_review_index(doc: Any, errors: IssueBuckets) -> tuple[dict[str, list[dict[str, Any]]], Counter[str]]:
    if doc is None:
        return {}, Counter()
    groups = rows_from_doc(doc, "candidate_groups", "duplicate_review_groups_not_found", errors)
    groups_by_song: dict[str, list[dict[str, Any]]] = defaultdict(list)
    type_counts: Counter[str] = Counter()

    for index, raw_group in enumerate(groups):
        if not isinstance(raw_group, dict):
            errors.add("duplicate_review_group_not_object", "Duplicate-review candidate groups must be objects.", {"candidate_group_index": index})
            continue
        group_type = clean_string(raw_group.get("candidate_type")) or "unknown"
        type_counts[group_type] += 1
        song_ids = raw_group.get("song_ids")
        if not isinstance(song_ids, list):
            errors.add(
                "duplicate_review_group_song_ids_not_array",
                "Duplicate-review candidate groups must contain a `song_ids` array.",
                {"candidate_group_index": index, "candidate_group_id": raw_group.get("candidate_group_id")},
            )
            continue
        for song_id in sorted({clean_string(value) for value in song_ids if clean_string(value)}):
            groups_by_song[song_id].append(raw_group)

    for groups_for_song in groups_by_song.values():
        groups_for_song.sort(key=lambda group: clean_string(group.get("candidate_group_id")))
    return dict(groups_by_song), type_counts


def validate(args: argparse.Namespace) -> dict[str, Any]:
    errors = IssueBuckets()
    tags_doc = load_json(args.tags)
    allowed_doc = load_json(args.allowed)
    pass_d_doc = load_json(args.pass_d)
    duplicate_doc = load_json(args.duplicate_review) if args.duplicate_review else None

    allowed_by_dim = load_allowed_by_dimension(allowed_doc, errors)
    tag_to_dims: dict[str, set[str]] = defaultdict(set)
    for dim, tags in allowed_by_dim.items():
        for tag in tags:
            tag_to_dims[tag].add(dim)

    tag_rows = tag_rows_from_doc(tags_doc, errors)
    pass_d_rows = rows_from_doc(pass_d_doc, "rows", "pass_d_rows_not_found", errors)
    pass_d_by_song, pass_d_by_membership = build_pass_d_indexes(pass_d_rows, errors)
    duplicate_groups_by_song, duplicate_group_type_counts = build_duplicate_review_index(duplicate_doc, errors)

    song_row_counts: Counter[str] = Counter()
    tag_counter: Counter[str] = Counter()
    dimension_tag_counter: dict[str, Counter[str]] = {dim: Counter() for dim in (*CORE_DIMS, *OVERLAY_DIMS)}
    core_tag_count_dist: Counter[int] = Counter()
    combined_tag_count_dist: Counter[int] = Counter()
    review_code_counter: Counter[str] = Counter()
    output_song_ids: set[str] = set()
    overlay_membership_ids: set[str] = set()
    covered_families: set[str] = set()
    covered_archetypes: set[str] = set()
    rows_by_song: dict[str, dict[str, Any]] = {}

    overlay_count = 0
    empty_social_context_count = 0
    core_tag_total = 0
    combined_tag_total = 0
    duplicate_review_applicable_group_ids: set[str] = set()
    duplicate_review_applicable_song_ids: set[str] = set()
    duplicate_review_flagged_song_ids: set[str] = set()

    for row_index, raw_row in enumerate(tag_rows):
        if not isinstance(raw_row, dict):
            errors.add("tag_row_not_object", "Tag rows must be objects.", {"row_index": row_index})
            continue

        song_id = first_consistent_id(
            raw_row,
            SONG_ID_FIELDS,
            errors,
            "song_id_fields_disagree",
            "Song identity fields disagree within an output row.",
            {"row_index": row_index},
        )
        if not song_id:
            errors.add("tag_row_missing_song_id", "Each output song row must carry a Pass D song identity.", {"row_index": row_index})
        else:
            song_row_counts[song_id] += 1
            output_song_ids.add(song_id)
            rows_by_song.setdefault(song_id, raw_row)
            if song_id not in pass_d_by_song:
                errors.add("unresolved_song_id", "Output song ID does not resolve to a Pass D `candidate_identity_key`.", {"row_index": row_index, "song_id": song_id})

        for dim in (*CORE_DIMS, *OVERLAY_DIMS):
            if dim in raw_row:
                errors.add(
                    "dimension_at_song_row_top_level",
                    "Affinity dimensions must live inside `canonical_song_affinity_tags` or `membership_context_overlays`, not at song-row top level.",
                    {"row_index": row_index, "song_id": song_id, "dimension": dim},
                )

        core = raw_row.get("canonical_song_affinity_tags")
        row_core_tag_count = 0
        if not isinstance(core, dict):
            errors.add(
                "canonical_song_affinity_tags_not_object",
                "Each output song row must contain a `canonical_song_affinity_tags` object.",
                {"row_index": row_index, "song_id": song_id},
            )
            core = {}
        for dim in sorted(core):
            if dim in OVERLAY_DIMS:
                errors.add(
                    "overlay_dimension_in_core",
                    "Overlay dimensions must not appear in `canonical_song_affinity_tags`.",
                    {"row_index": row_index, "song_id": song_id, "dimension": dim},
                )
            elif dim not in CORE_DIMS:
                errors.add(
                    "unknown_core_dimension",
                    "`canonical_song_affinity_tags` contains a dimension outside the core contract.",
                    {"row_index": row_index, "song_id": song_id, "dimension": dim},
                )
        for dim in CORE_DIMS:
            tags = tags_in_bucket(core.get(dim), f"songs[{row_index}].canonical_song_affinity_tags.{dim}", errors)
            row_core_tag_count += len(tags)
            for tag in tags:
                validate_tag(
                    tag,
                    dim,
                    allowed_by_dim,
                    tag_to_dims,
                    errors,
                    {"row_index": row_index, "song_id": song_id, "dimension": dim, "tag": tag},
                )
                tag_counter[tag] += 1
                dimension_tag_counter[dim][tag] += 1

        overlays = raw_row.get("membership_context_overlays")
        row_overlay_tag_count = 0
        if not isinstance(overlays, list):
            errors.add(
                "membership_context_overlays_not_array",
                "Each output song row must contain a `membership_context_overlays` array.",
                {"row_index": row_index, "song_id": song_id},
            )
            overlays = []
        seen_row_overlay_memberships: set[str] = set()
        for overlay_index, raw_overlay in enumerate(overlays):
            overlay_count += 1
            overlay_path = f"songs[{row_index}].membership_context_overlays[{overlay_index}]"
            if not isinstance(raw_overlay, dict):
                errors.add(
                    "overlay_not_object",
                    "Membership context overlays must be objects.",
                    {"row_index": row_index, "song_id": song_id, "overlay_index": overlay_index},
                )
                continue

            membership_id = first_consistent_id(
                raw_overlay,
                OVERLAY_MEMBERSHIP_ID_FIELDS,
                errors,
                "overlay_membership_id_fields_disagree",
                "Overlay membership ID fields disagree within an overlay.",
                {"row_index": row_index, "song_id": song_id, "overlay_index": overlay_index},
            )
            if not membership_id:
                errors.add(
                    "overlay_missing_membership_id",
                    "Every overlay must carry a Pass D `v1_membership_id` value.",
                    {"row_index": row_index, "song_id": song_id, "overlay_index": overlay_index},
                )
            elif membership_id not in pass_d_by_membership:
                errors.add(
                    "unresolved_overlay_membership_id",
                    "Overlay membership ID does not resolve to a Pass D `v1_membership_id`.",
                    {"row_index": row_index, "song_id": song_id, "overlay_index": overlay_index, "membership_id": membership_id},
                )
            else:
                overlay_membership_ids.add(membership_id)
                pass_d_row = pass_d_by_membership[membership_id]
                expected_song_id = clean_string(pass_d_row.get("candidate_identity_key"))
                if song_id and expected_song_id and expected_song_id != song_id:
                    errors.add(
                        "overlay_membership_song_mismatch",
                        "Overlay membership ID belongs to a different Pass D song identity.",
                        {
                            "row_index": row_index,
                            "song_id": song_id,
                            "overlay_index": overlay_index,
                            "membership_id": membership_id,
                            "expected_song_id": expected_song_id,
                        },
                    )
                covered_families.add(clean_string(raw_overlay.get("family_number")) or clean_string(pass_d_row.get("primary_family")))
                covered_archetypes.add(clean_string(pass_d_row.get("archetype_id")))

            if membership_id:
                if membership_id in seen_row_overlay_memberships:
                    errors.add(
                        "duplicate_overlay_membership_id_within_song",
                        "A song row repeats the same overlay membership ID.",
                        {"row_index": row_index, "song_id": song_id, "overlay_index": overlay_index, "membership_id": membership_id},
                    )
                seen_row_overlay_memberships.add(membership_id)

            overlay_song_id = first_consistent_id(
                raw_overlay,
                OVERLAY_SONG_ID_FIELDS,
                errors,
                "overlay_song_id_fields_disagree",
                "Overlay song identity fields disagree within an overlay.",
                {"row_index": row_index, "song_id": song_id, "overlay_index": overlay_index},
            )
            if overlay_song_id and song_id and overlay_song_id != song_id:
                errors.add(
                    "overlay_song_id_mismatch",
                    "Overlay song identity does not match its parent song row.",
                    {"row_index": row_index, "song_id": song_id, "overlay_index": overlay_index, "overlay_song_id": overlay_song_id},
                )

            for dim in CORE_DIMS:
                if dim in raw_overlay:
                    errors.add(
                        "core_dimension_in_overlay",
                        "Core dimensions must not appear inside `membership_context_overlays`.",
                        {"row_index": row_index, "song_id": song_id, "overlay_index": overlay_index, "dimension": dim},
                    )
            for key in sorted(raw_overlay):
                if key in OVERLAY_DIMS or key in OVERLAY_METADATA_FIELDS or key in CORE_DIMS:
                    continue
                if looks_like_tag_bucket(raw_overlay.get(key)):
                    errors.add(
                        "unknown_overlay_dimension",
                        "`membership_context_overlays` contains a tag-bucket field outside the overlay contract.",
                        {"row_index": row_index, "song_id": song_id, "overlay_index": overlay_index, "dimension": key},
                    )
            social_tags = tags_in_bucket(raw_overlay.get("social_context"), f"{overlay_path}.social_context", errors)
            if not social_tags:
                empty_social_context_count += 1
            for dim in OVERLAY_DIMS:
                tags = social_tags if dim == "social_context" else tags_in_bucket(raw_overlay.get(dim), f"{overlay_path}.{dim}", errors)
                row_overlay_tag_count += len(tags)
                for tag in tags:
                    validate_tag(
                        tag,
                        dim,
                        allowed_by_dim,
                        tag_to_dims,
                        errors,
                        {
                            "row_index": row_index,
                            "song_id": song_id,
                            "overlay_index": overlay_index,
                            "membership_id": membership_id,
                            "dimension": dim,
                            "tag": tag,
                        },
                    )
                    tag_counter[tag] += 1
                    dimension_tag_counter[dim][tag] += 1

        core_tag_total += row_core_tag_count
        combined_tags = row_core_tag_count + row_overlay_tag_count
        combined_tag_total += combined_tags
        core_tag_count_dist[row_core_tag_count] += 1
        combined_tag_count_dist[combined_tags] += 1

        row_review_codes = review_codes_for_row(raw_row, row_index, song_id, errors)
        review_code_counter.update(row_review_codes)

    for song_id, count in sorted(song_row_counts.items()):
        if count > 1:
            errors.add("duplicate_song_row", "Each Pass D song identity may appear only once in sidecar output.", {"song_id": song_id, "occurrences": count})

    if duplicate_groups_by_song:
        for song_id in sorted(output_song_ids.intersection(duplicate_groups_by_song)):
            row = rows_by_song.get(song_id)
            if not row:
                continue
            groups = duplicate_groups_by_song[song_id]
            for group in groups:
                group_id = clean_string(group.get("candidate_group_id"))
                group_type = clean_string(group.get("candidate_type")) or "unknown"
                duplicate_review_applicable_song_ids.add(song_id)
                if group_id:
                    duplicate_review_applicable_group_ids.add(group_id)
                expected_codes = DUPLICATE_REVIEW_CODES_BY_TYPE.get(group_type, {"duplicate_context_unclear", "version_ambiguity"})
                if row_has_duplicate_review_flag(row, expected_codes):
                    duplicate_review_flagged_song_ids.add(song_id)
                else:
                    errors.add(
                        "missing_duplicate_context_review_flag",
                        "Output row intersects a duplicate/context review candidate group but is not review-flagged.",
                        {
                            "song_id": song_id,
                            "candidate_group_id": group_id,
                            "candidate_type": group_type,
                            "expected_any_reason_code": sorted(expected_codes),
                        },
                    )

    song_row_total = len(tag_rows)
    empty_social_rate = empty_social_context_count / overlay_count if overlay_count else 0.0
    pass_d_membership_ids_for_output_songs = {
        clean_string(row.get("v1_membership_id"))
        for song_id in output_song_ids
        for row in pass_d_by_song.get(song_id, [])
        if clean_string(row.get("v1_membership_id"))
    }
    missing_overlay_memberships = sorted(pass_d_membership_ids_for_output_songs - overlay_membership_ids)
    extra_overlay_memberships = sorted(overlay_membership_ids - set(pass_d_by_membership))

    metrics = {
        "validator": "validate_affinity_graphwide_sidecar_v0_1",
        "inputs": {
            "tags": str(args.tags),
            "allowed": str(args.allowed),
            "pass_d": str(args.pass_d),
            "duplicate_review": str(args.duplicate_review) if args.duplicate_review else None,
        },
        "pass_d_song_identity_count": len(pass_d_by_song),
        "pass_d_membership_count": len(pass_d_by_membership),
        "song_rows": song_row_total,
        "unique_output_song_ids": len(output_song_ids),
        "duplicate_song_row_count": sum(count - 1 for count in song_row_counts.values() if count > 1),
        "unresolved_song_id_count": errors.count("unresolved_song_id"),
        "membership_overlays": overlay_count,
        "unique_overlay_membership_ids": len(overlay_membership_ids),
        "unresolved_overlay_membership_id_count": errors.count("unresolved_overlay_membership_id"),
        "overlay_membership_song_mismatch_count": errors.count("overlay_membership_song_mismatch"),
        "pass_d_overlay_memberships_expected_for_output_songs": len(pass_d_membership_ids_for_output_songs),
        "pass_d_overlay_memberships_missing_from_output_count": len(missing_overlay_memberships),
        "pass_d_overlay_membership_coverage_rate": (
            len(overlay_membership_ids.intersection(pass_d_membership_ids_for_output_songs)) / len(pass_d_membership_ids_for_output_songs)
            if pass_d_membership_ids_for_output_songs
            else 0.0
        ),
        "extra_overlay_membership_ids_count": len(extra_overlay_memberships),
        "families_covered_count": len({value for value in covered_families if value}),
        "archetypes_covered_count": len({value for value in covered_archetypes if value}),
        "noncanonical_tag_count": errors.count("noncanonical_tag"),
        "misplaced_allowed_tag_count": errors.count("misplaced_allowed_tag"),
        "schema_boundary_violation_count": sum(
            errors.count(code)
            for code in (
                "dimension_at_song_row_top_level",
                "overlay_dimension_in_core",
                "unknown_core_dimension",
                "core_dimension_in_overlay",
                "unknown_overlay_dimension",
            )
        ),
        "unknown_review_reason_code_count": errors.count("unknown_review_reason_code"),
        "average_core_tag_count": round(core_tag_total / song_row_total, 4) if song_row_total else 0.0,
        "average_combined_tag_count": round(combined_tag_total / song_row_total, 4) if song_row_total else 0.0,
        "core_tag_count_distribution": {str(key): core_tag_count_dist[key] for key in sorted(core_tag_count_dist)},
        "combined_tag_count_distribution": {str(key): combined_tag_count_dist[key] for key in sorted(combined_tag_count_dist)},
        "safe_gateway_count": tag_counter.get("safe_gateway", 0),
        "context_dependent_count": tag_counter.get("context_dependent", 0),
        "empty_social_context_overlay_count": empty_social_context_count,
        "empty_social_context_overlay_rate": round(empty_social_rate, 6),
        "review_reason_code_counts": dict(sorted(review_code_counter.items())),
        "duplicate_review_provided": bool(args.duplicate_review),
        "duplicate_review_candidate_group_count": sum(duplicate_group_type_counts.values()),
        "duplicate_review_candidate_group_type_counts": dict(sorted(duplicate_group_type_counts.items())),
        "duplicate_review_applicable_group_count": len(duplicate_review_applicable_group_ids),
        "duplicate_review_applicable_song_count": len(duplicate_review_applicable_song_ids),
        "duplicate_review_flagged_song_count": len(duplicate_review_flagged_song_ids),
        "duplicate_review_missing_flag_count": errors.count("missing_duplicate_context_review_flag"),
        "tag_counts_by_dimension": {
            dim: dict(sorted(counter.items(), key=lambda item: (-item[1], item[0])))
            for dim, counter in sorted(dimension_tag_counter.items())
        },
        "top_tags": [{"tag": tag, "count": count} for tag, count in sorted(tag_counter.items(), key=lambda item: (-item[1], item[0]))[:50]],
        "hard_error_count": errors.total(),
    }

    return {
        "status": "fail" if errors.total() else "pass",
        "metrics": metrics,
        "errors": errors.as_list(),
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tags", required=True, help="Affinity sidecar output JSON to validate.")
    parser.add_argument("--allowed", required=True, help="Allowed canonical tags by dimension JSON.")
    parser.add_argument("--pass-d", required=True, help="Pass D graph_tagging_corpus_v1.json.")
    parser.add_argument("--duplicate-review", help="Optional duplicate/context review candidate JSON.")
    parser.add_argument("--metrics-out", help="Optional path to also write the validation JSON.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        result = validate(args)
    except (OSError, json.JSONDecodeError) as exc:
        result = {
            "status": "fail",
            "metrics": {"validator": "validate_affinity_graphwide_sidecar_v0_1", "hard_error_count": 1},
            "errors": [
                {
                    "code": "input_load_error",
                    "message": "Failed to load one or more validator inputs.",
                    "count": 1,
                    "samples": [{"error": str(exc)}],
                }
            ],
        }

    output = json.dumps(result, indent=2, sort_keys=True)
    print(output)
    if args.metrics_out:
        Path(args.metrics_out).write_text(output + "\n", encoding="utf-8")
    return 1 if result.get("errors") else 0


if __name__ == "__main__":
    sys.exit(main())
