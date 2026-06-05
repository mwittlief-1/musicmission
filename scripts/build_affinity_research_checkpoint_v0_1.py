#!/usr/bin/env python3
"""Build a deterministic QA checkpoint for researched affinity batches."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "review_packets/affinity_graphwide_v0_1"
BATCH_DIR = BASE / "research_batches"
MANIFEST = BATCH_DIR / "affinity_research_batch_manifest_v0_1.json"
ALLOWED = ROOT / "data/canonical_graph/affinity_contracts/v0_3_1/cartenza_affinity_codex_repo_truth_package_v0_3_1/allowed_tags/allowed_canonical_tags_by_dimension_v0_3_1.json"
VALIDATOR = ROOT / "scripts/validate_affinity_research_batch_v0_1.py"
SENTINELS = BATCH_DIR / "reports/sentinel_research_corrections_v0_1.json"

CORE_DIMS = ["vocal_performance", "emotion_theme", "sonic_texture", "rhythm_body", "form_container"]
OVERLAY_DIMS = ["social_context", "routing_caution"]


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def bucket_tags(bucket: Any) -> list[str]:
    if not isinstance(bucket, dict):
        return []
    out: list[str] = []
    for slot in ("primary", "secondary"):
        values = bucket.get(slot, [])
        if isinstance(values, list):
            out.extend(v for v in values if isinstance(v, str) and v)
    return out


def core_tags(song: dict[str, Any]) -> dict[str, list[str]]:
    tags = song.get("canonical_song_affinity_tags", {})
    return {dim: bucket_tags(tags.get(dim, {})) for dim in CORE_DIMS}


def core_tag_count(song: dict[str, Any]) -> int:
    return sum(len(values) for values in core_tags(song).values())


def validate_batch(input_path: Path, output_path: Path) -> tuple[bool, dict[str, Any]]:
    proc = subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            "--input",
            str(input_path),
            "--output",
            str(output_path),
            "--allowed",
            str(ALLOWED),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        payload = {"status": "fail", "errors": [proc.stdout[-2000:], proc.stderr[-2000:]]}
    return proc.returncode == 0, payload


def collect_membership_context(manifest: dict[str, Any], batch_ids: set[str]) -> dict[str, dict[str, Any]]:
    memberships: dict[str, dict[str, Any]] = {}
    for batch in manifest["batches"]:
        if batch["batch_id"] not in batch_ids:
            continue
        input_doc = load_json(ROOT / batch["input_file"])
        for song in input_doc.get("songs", []):
            for membership in song.get("memberships", []):
                memberships[membership["membership_id"]] = {
                    "song_id": song["canonical_song_recording_id"],
                    "family_number": membership.get("family_number"),
                    "family_scope": membership.get("family_scope", ""),
                    "archetype_id": membership.get("archetype_id", ""),
                    "archetype_name": membership.get("archetype_name", ""),
                    "risk_status": membership.get("risk_status", ""),
                }
    return memberships


def compare_sentinels(songs_by_id: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    if not SENTINELS.exists():
        return []
    sentinel_doc = load_json(SENTINELS)
    checks = []
    for expected in sentinel_doc.get("songs", []):
        sid = expected["canonical_song_recording_id"]
        actual = songs_by_id.get(sid)
        if not actual:
            checks.append({"canonical_song_recording_id": sid, "status": "not_in_checkpoint"})
            continue
        expected_core = core_tags(expected)
        actual_core = core_tags(actual)
        actual_count = core_tag_count(actual)
        missing = {
            dim: sorted(set(expected_core[dim]) - set(actual_core[dim]))
            for dim in CORE_DIMS
            if set(expected_core[dim]) - set(actual_core[dim])
        }
        extra = {
            dim: sorted(set(actual_core[dim]) - set(expected_core[dim]))
            for dim in CORE_DIMS
            if set(actual_core[dim]) - set(expected_core[dim])
        }
        uncovered_dimensions = [
            dim
            for dim in CORE_DIMS
            if expected_core[dim] and not (set(expected_core[dim]) & set(actual_core[dim]))
        ]
        density_ok = 4 <= actual_count <= 6
        contract_compatible = not extra and not uncovered_dimensions and density_ok
        checks.append(
            {
                "canonical_song_recording_id": sid,
                "song_title": actual.get("song_title", expected.get("song_title", "")),
                "status": (
                    "matches_sentinel_core"
                    if not missing and not extra
                    else "contract_compatible_sentinel_core"
                    if contract_compatible
                    else "differs_from_sentinel_guidance"
                ),
                "core_tag_count": actual_count,
                "uncovered_expected_dimensions": uncovered_dimensions,
                "missing_expected_core_tags": missing,
                "additional_researched_core_tags": extra,
            }
        )
    return checks


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target-song-count", type=int, default=500)
    args = ap.parse_args()

    manifest = load_json(MANIFEST)
    completed_batches: list[dict[str, Any]] = []
    failed_batches: list[dict[str, Any]] = []
    songs: list[dict[str, Any]] = []

    for batch in manifest["batches"]:
        output_path = ROOT / batch["expected_output_file"]
        if not output_path.exists():
            continue
        input_path = ROOT / batch["input_file"]
        ok, validation = validate_batch(input_path, output_path)
        if not ok:
            failed_batches.append({"batch_id": batch["batch_id"], "validation": validation})
            continue
        doc = load_json(output_path)
        completed_batches.append(batch)
        songs.extend(doc.get("songs", []))
        if len(songs) >= args.target_song_count:
            break

    songs = songs[: args.target_song_count]
    songs_by_id = {song["canonical_song_recording_id"]: song for song in songs}
    batch_ids = {batch["batch_id"] for batch in completed_batches}
    memberships = collect_membership_context(manifest, batch_ids)

    core_distribution = Counter(core_tag_count(song) for song in songs)
    core_by_dimension: dict[str, Counter[str]] = {dim: Counter() for dim in CORE_DIMS}
    overlay_by_dimension: dict[str, Counter[str]] = {dim: Counter() for dim in OVERLAY_DIMS}
    top_tags = Counter()
    family_metrics: dict[str, dict[str, Any]] = {}
    safe_gateway_song_ids = set()
    context_dependent_song_ids = set()
    review_flags = Counter()
    review_codes = Counter()
    duplicate_context_song_ids = set()

    def family_bucket(ctx: dict[str, Any]) -> dict[str, Any]:
        key = str(ctx.get("family_number"))
        if key not in family_metrics:
            family_metrics[key] = {
                "family_number": ctx.get("family_number"),
                "family_scope": ctx.get("family_scope", ""),
                "song_count": 0,
                "membership_count": 0,
                "core_tags": Counter(),
                "social_context_tags": Counter(),
                "routing_caution_tags": Counter(),
            }
        return family_metrics[key]

    family_song_ids: dict[str, set[str]] = defaultdict(set)
    for song in songs:
        sid = song["canonical_song_recording_id"]
        for dim, values in core_tags(song).items():
            core_by_dimension[dim].update(values)
            top_tags.update(values)
        review = song.get("review", {})
        for field in ("identity_review_needed", "core_tag_review_needed", "overlay_review_needed"):
            if review.get(field):
                review_flags[field] += 1
        codes = review.get("review_reason_codes", []) or []
        review_codes.update(codes)
        if {"duplicate_context_unclear", "context_leak_risk", "version_ambiguity"} & set(codes):
            duplicate_context_song_ids.add(sid)
        for overlay in song.get("membership_context_overlays", []):
            ctx = memberships.get(overlay.get("membership_id", ""), {})
            if ctx:
                bucket = family_bucket(ctx)
                family_song_ids[str(ctx.get("family_number"))].add(sid)
                bucket["membership_count"] += 1
                for values in core_tags(song).values():
                    bucket["core_tags"].update(values)
            for dim in OVERLAY_DIMS:
                values = bucket_tags(overlay.get(dim, {}))
                overlay_by_dimension[dim].update(values)
                top_tags.update(values)
                if ctx:
                    bucket = family_bucket(ctx)
                    bucket[f"{dim}_tags"].update(values)
                if dim == "routing_caution":
                    if "safe_gateway" in values:
                        safe_gateway_song_ids.add(sid)
                    if "context_dependent" in values:
                        context_dependent_song_ids.add(sid)

    for key, ids in family_song_ids.items():
        family_metrics[key]["song_count"] = len(ids)

    serial_family_metrics = []
    for key in sorted(family_metrics, key=lambda x: (x == "None", int(x) if x.isdigit() else 999)):
        item = family_metrics[key]
        serial_family_metrics.append(
            {
                "family_number": item["family_number"],
                "family_scope": item["family_scope"],
                "song_count": item["song_count"],
                "membership_count": item["membership_count"],
                "top_core_tags": item["core_tags"].most_common(12),
                "top_social_context_tags": item["social_context_tags"].most_common(8),
                "top_routing_caution_tags": item["routing_caution_tags"].most_common(8),
            }
        )

    sentinel_checks = compare_sentinels(songs_by_id)
    average_core = round(sum(core_tag_count(song) for song in songs) / len(songs), 3) if songs else 0
    checkpoint_ready = len(songs) >= args.target_song_count and not failed_batches
    progress_label = (
        f"checkpoint_{args.target_song_count:04d}_ready_for_semantic_review"
        if checkpoint_ready
        else f"checkpoint_{args.target_song_count:04d}_pending"
    )
    metrics = {
        "generated": str(date.today()),
        "artifact_name": f"affinity_research_checkpoint_{args.target_song_count:04d}_QA_metrics_v0_1",
        "progress_status": progress_label,
        "target_song_count": args.target_song_count,
        "checkpoint_song_count": len(songs),
        "completed_batch_ids_included": [batch["batch_id"] for batch in completed_batches],
        "failed_batch_count": len(failed_batches),
        "failed_batches": failed_batches[:10],
        "runtime_ingestion_status": "not_approved",
        "derived_edge_construction_status": "not_approved",
        "review_field_contract_status": "amended_core_overlay_review_fields",
        "average_core_tags_per_song": average_core,
        "core_tag_count_distribution": dict(sorted(core_distribution.items())),
        "top_repeated_tags": top_tags.most_common(40),
        "tag_distribution_by_dimension": {
            "core": {dim: core_by_dimension[dim].most_common() for dim in CORE_DIMS},
            "overlay": {dim: overlay_by_dimension[dim].most_common() for dim in OVERLAY_DIMS},
        },
        "tag_distribution_by_family": serial_family_metrics,
        "safe_gateway": {
            "unique_song_count": len(safe_gateway_song_ids),
            "rate": round(len(safe_gateway_song_ids) / len(songs), 4) if songs else 0,
        },
        "context_dependent": {
            "unique_song_count": len(context_dependent_song_ids),
            "rate": round(len(context_dependent_song_ids) / len(songs), 4) if songs else 0,
        },
        "review_flag_rates": {
            field: {
                "count": review_flags[field],
                "rate": round(review_flags[field] / len(songs), 4) if songs else 0,
            }
            for field in ("identity_review_needed", "core_tag_review_needed", "overlay_review_needed")
        },
        "review_reason_code_counts": review_codes.most_common(),
        "duplicate_context_handling": {
            "song_count_with_duplicate_or_version_review": len(duplicate_context_song_ids),
            "song_ids": sorted(duplicate_context_song_ids)[:100],
        },
        "manual_sentinel_spot_checks": sentinel_checks,
    }

    metrics_path = BASE / f"affinity_research_checkpoint_{args.target_song_count:04d}_QA_metrics_v0_1.json"
    report_path = BASE / f"affinity_research_checkpoint_{args.target_song_count:04d}_QA_report_v0_1.md"
    write_json(metrics_path, metrics)

    lines = [
        f"# Affinity Research Checkpoint {args.target_song_count} QA Report v0.1",
        "",
        f"Generated: {date.today()}",
        "",
        "## Status",
        "",
        f"- Progress status: `{metrics['progress_status']}`",
        f"- Songs included: {len(songs)} / {args.target_song_count}",
        f"- Included batches: {', '.join(metrics['completed_batch_ids_included'])}",
        "- Runtime ingestion: NOT APPROVED",
        "- Derived edge construction: NOT APPROVED",
        "- Review field contract: amended to `core_tag_review_needed` and `overlay_review_needed`",
        "",
        "## Core Tag QA",
        "",
        f"- Average core tags per song: {average_core}",
        f"- Core tag count distribution: {dict(sorted(core_distribution.items()))}",
        "",
        "## Overlay Caution QA",
        "",
        f"- `safe_gateway` unique songs: {metrics['safe_gateway']['unique_song_count']} ({metrics['safe_gateway']['rate']})",
        f"- `context_dependent` unique songs: {metrics['context_dependent']['unique_song_count']} ({metrics['context_dependent']['rate']})",
        "",
        "## Review Flags",
        "",
    ]
    for field, payload in metrics["review_flag_rates"].items():
        lines.append(f"- `{field}`: {payload['count']} ({payload['rate']})")
    lines.extend(
        [
            "",
            "## Family Distribution",
            "",
        ]
    )
    for family in metrics["tag_distribution_by_family"]:
        lines.append(
            f"- Family {family['family_number']} ({family['family_scope']}): "
            f"{family['song_count']} songs, {family['membership_count']} memberships"
        )
        core_preview = ", ".join(f"`{tag}` {count}" for tag, count in family["top_core_tags"][:5])
        route_preview = ", ".join(f"`{tag}` {count}" for tag, count in family["top_routing_caution_tags"][:5])
        if core_preview:
            lines.append(f"  Core: {core_preview}")
        if route_preview:
            lines.append(f"  Routing: {route_preview}")
    lines.extend(
        [
            "",
            "## Top Repeated Tags",
            "",
        ]
    )
    for tag, count in metrics["top_repeated_tags"][:25]:
        lines.append(f"- `{tag}`: {count}")
    lines.extend(
        [
            "",
            "## Manual Sentinel Spot Checks",
            "",
        ]
    )
    for check in sentinel_checks:
        lines.append(
            f"- {check.get('song_title', check['canonical_song_recording_id'])}: `{check['status']}`"
        )
        missing = check.get("missing_expected_core_tags") or {}
        extra = check.get("additional_researched_core_tags") or {}
        if missing:
            lines.append(f"  Missing sentinel core tags: `{missing}`")
        if extra:
            lines.append(f"  Additional researched core tags: `{extra}`")
    lines.extend(
        [
            "",
            "## Duplicate/Context Handling",
            "",
            f"- Songs with duplicate/version/context review codes: {metrics['duplicate_context_handling']['song_count_with_duplicate_or_version_review']}",
        ]
    )
    for sid in metrics["duplicate_context_handling"]["song_ids"][:25]:
        lines.append(f"- `{sid}`")
    lines.extend(
        [
            "",
            "## Checkpoint Review Notes",
            "",
        ]
    )
    if metrics["safe_gateway"]["rate"] > 0.35:
        lines.append(
            f"- `safe_gateway` usage is high at {metrics['safe_gateway']['rate']}; review whether workers are still using it too broadly."
        )
    if metrics["context_dependent"]["rate"] > 0.25:
        lines.append(
            f"- `context_dependent` usage is at {metrics['context_dependent']['rate']}; review whether this remains specific enough."
        )
    sentinel_diff_count = sum(
        1 for check in sentinel_checks if check.get("status") == "differs_from_sentinel_guidance"
    )
    if sentinel_diff_count:
        lines.append(
            f"- {sentinel_diff_count} sentinel rows differ from strict sentinel guidance; review before full graph continuation."
        )
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- Metrics: `{metrics_path.relative_to(ROOT)}`",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"metrics": str(metrics_path), "report": str(report_path), "status": metrics["progress_status"]}, indent=2))
    return 0 if checkpoint_ready else 1


if __name__ == "__main__":
    sys.exit(main())
