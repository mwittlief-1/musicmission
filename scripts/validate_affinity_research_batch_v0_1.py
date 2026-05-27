#!/usr/bin/env python3
"""Validate a researched affinity batch output."""

from __future__ import annotations

import argparse
import json
import sys
from json import JSONDecodeError
from collections import Counter
from pathlib import Path
from typing import Any


CORE_DIMS = ["vocal_performance", "emotion_theme", "sonic_texture", "rhythm_body", "form_container"]
OVERLAY_DIMS = ["social_context", "routing_caution"]
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
ALLOWED_BATCH_STATUSES = {
    "researched_complete",
    "researched_complete_with_review_flags",
    "blocked_needs_research_repair",
}
CORE_REVIEW_CODES = {
    "tag_definition_ambiguous",
    "missing_tag_candidate",
    "over_tagged",
    "under_tagged",
    "context_leak_risk",
    "schema_boundary_risk",
}
OVERLAY_REVIEW_CODES = {
    "social_context_unclear",
    "routing_caution_unclear",
    "duplicate_context_unclear",
    "context_leak_risk",
    "schema_boundary_risk",
}


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def tags(bucket: Any) -> list[str]:
    if not isinstance(bucket, dict):
        return []
    out = []
    for slot in ("primary", "secondary"):
        values = bucket.get(slot, [])
        if isinstance(values, list):
            out.extend(value for value in values if isinstance(value, str) and value)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--allowed", required=True, type=Path)
    args = ap.parse_args()

    try:
        input_doc = load_json(args.input)
        output_doc = load_json(args.output)
        allowed = load_json(args.allowed)["allowed_tags_by_dimension"]
    except (OSError, JSONDecodeError) as exc:
        print(
            json.dumps(
                {
                    "status": "fail",
                    "error_count": 1,
                    "errors": [f"could not load required JSON: {exc}"],
                    "metrics": {},
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 1
    allowed_sets = {dim: set(values) for dim, values in allowed.items()}

    metadata = output_doc.get("metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}
        errors = ["metadata must be object"]
    else:
        errors = []
    status = metadata.get("status")
    if status not in ALLOWED_BATCH_STATUSES:
        errors.append(
            f"metadata.status must be one of {sorted(ALLOWED_BATCH_STATUSES)}, got {status!r}"
        )

    expected_songs = {song["canonical_song_recording_id"]: song for song in input_doc.get("songs", [])}
    expected_memberships = {
        song["canonical_song_recording_id"]: {m["membership_id"] for m in song.get("memberships", [])}
        for song in input_doc.get("songs", [])
    }
    output_songs = output_doc.get("songs", [])
    metrics = Counter()

    if len(output_songs) != len(expected_songs):
        errors.append(f"song count mismatch: expected {len(expected_songs)}, got {len(output_songs)}")

    seen = set()
    for song in output_songs:
        sid = song.get("canonical_song_recording_id", "")
        if sid not in expected_songs:
            errors.append(f"unexpected song id: {sid}")
            continue
        if sid in seen:
            errors.append(f"duplicate song id: {sid}")
        seen.add(sid)
        evidence = song.get("research_evidence", [])
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{sid}: missing research_evidence")
        else:
            metrics["songs_with_evidence"] += 1

        core = song.get("canonical_song_affinity_tags", {})
        if not isinstance(core, dict):
            errors.append(f"{sid}: canonical_song_affinity_tags must be object")
            core = {}
        for dim in core:
            if dim not in CORE_DIMS:
                errors.append(f"{sid}: forbidden core dimension {dim}")
        core_count = 0
        for dim in CORE_DIMS:
            bucket = core.get(dim, {"primary": [], "secondary": []})
            for tag in tags(bucket):
                core_count += 1
                if tag not in allowed_sets.get(dim, set()):
                    errors.append(f"{sid}: noncanonical/misplaced core tag {tag} in {dim}")
        if core_count > 6:
            errors.append(f"{sid}: too many core tags ({core_count})")
        if core_count < 4:
            errors.append(f"{sid}: too few core tags ({core_count})")
        metrics[f"core_tag_count_{core_count}"] += 1

        overlays = song.get("membership_context_overlays", [])
        if not isinstance(overlays, list):
            errors.append(f"{sid}: membership_context_overlays must be array")
            overlays = []
        output_memberships = {overlay.get("membership_id") for overlay in overlays}
        if output_memberships != expected_memberships[sid]:
            errors.append(f"{sid}: overlay membership set mismatch")
        for overlay in overlays:
            mid = overlay.get("membership_id", "")
            for dim in overlay:
                if dim in CORE_DIMS:
                    errors.append(f"{sid}/{mid}: core dimension leaked into overlay: {dim}")
            for dim in OVERLAY_DIMS:
                for tag in tags(overlay.get(dim, {})):
                    if tag not in allowed_sets.get(dim, set()):
                        errors.append(f"{sid}/{mid}: noncanonical/misplaced overlay tag {tag} in {dim}")

        review = song.get("review", {})
        if isinstance(review, dict):
            if "tag_review_needed" in review:
                errors.append(f"{sid}: deprecated review field tag_review_needed")
            for required in ("identity_review_needed", "core_tag_review_needed", "overlay_review_needed"):
                if not isinstance(review.get(required), bool):
                    errors.append(f"{sid}: review.{required} must be boolean")
            review_codes = review.get("review_reason_codes", []) or []
            for code in review_codes:
                if code not in REVIEW_CODES:
                    errors.append(f"{sid}: unknown review code {code}")
            if any(code in CORE_REVIEW_CODES for code in review_codes) and not review.get("core_tag_review_needed"):
                errors.append(f"{sid}: core review code present but core_tag_review_needed is false")
            if any(code in OVERLAY_REVIEW_CODES for code in review_codes) and not review.get("overlay_review_needed"):
                errors.append(f"{sid}: overlay review code present but overlay_review_needed is false")
        else:
            errors.append(f"{sid}: review must be object")

    missing = set(expected_songs) - seen
    for sid in sorted(missing):
        errors.append(f"missing song id: {sid}")

    result = {
        "status": "pass" if not errors else "fail",
        "error_count": len(errors),
        "errors": errors[:200],
        "metrics": dict(metrics),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
