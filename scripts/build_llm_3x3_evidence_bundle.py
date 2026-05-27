#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = REPO_ROOT / "data/survey_simulation"
SOURCE_DIR = SIM_DIR / "llm_profile_review" / "api_pilot_3x3"
REPORTS_DIR = SIM_DIR / "llm_profile_review" / "reports"
EVIDENCE_ROOT = SIM_DIR / "llm_profile_review" / "evidence_bundles"
DEFAULT_BUNDLE_ID = "gpt_5_5_3x3_2026_05_20"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def copy_artifact(
    source: Path,
    destination: Path,
    *,
    category: str,
    includes_hidden_data: bool,
    manifest_files: list[dict[str, Any]],
) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    manifest_files.append(
        {
            "category": category,
            "source_path": rel(source),
            "bundle_path": rel(destination),
            "bytes": destination.stat().st_size,
            "sha256": sha256_file(destination),
            "includes_hidden_data": includes_hidden_data,
        }
    )


def matching_file(directory: Path, prefix: str, profile_id: str, config_id: str) -> Path:
    path = directory / f"{prefix}_{profile_id}_{config_id}.json"
    if not path.exists():
        raise FileNotFoundError(path)
    return path


def copy_row_artifacts(
    *,
    row: dict[str, Any],
    bundle_dir: Path,
    manifest_files: list[dict[str, Any]],
) -> dict[str, Any]:
    profile_id = row["profile_public_id"]
    config_id = row["config_id"]

    copied: dict[str, str] = {}
    artifact_specs = [
        (
            Path(row["public_packet_path"]),
            bundle_dir / "public_blind" / "public_packets" / f"{profile_id}_{config_id}.json",
            "public_blind.public_packet",
            False,
            "public_packet",
        ),
        (
            matching_file(
                SOURCE_DIR / "executed_requests",
                "profile_writer_request",
                profile_id,
                config_id,
            ),
            bundle_dir / "public_blind" / "profile_writer_requests" / f"{profile_id}_{config_id}.json",
            "public_blind.profile_writer_request",
            False,
            "profile_writer_request",
        ),
        (
            Path(row["profile_writer_output_path"]),
            bundle_dir / "public_blind" / "raw_profile_writer_json" / f"{profile_id}_{config_id}.json",
            "public_blind.raw_profile_writer_json",
            False,
            "raw_profile_writer_json",
        ),
        (
            matching_file(
                SOURCE_DIR / "raw_api_responses",
                "profile_writer_raw_response",
                profile_id,
                config_id,
            ),
            bundle_dir / "public_blind" / "raw_profile_writer_api_responses" / f"{profile_id}_{config_id}.json",
            "public_blind.raw_profile_writer_api_response",
            False,
            "raw_profile_writer_api_response",
        ),
        (
            matching_file(
                SOURCE_DIR / "executed_requests",
                "evaluator_evidence_only_request",
                profile_id,
                config_id,
            ),
            bundle_dir / "public_review" / "evidence_only_evaluator_requests" / f"{profile_id}_{config_id}.json",
            "public_review.evidence_only_evaluator_request",
            False,
            "evidence_only_evaluator_request",
        ),
        (
            Path(row["evidence_output_path"]),
            bundle_dir / "public_review" / "evidence_only_evaluator_outputs" / f"{profile_id}_{config_id}.json",
            "public_review.evidence_only_evaluator_output",
            False,
            "evidence_only_evaluator_output",
        ),
        (
            matching_file(
                SOURCE_DIR / "raw_api_responses",
                "evaluator_evidence_only_raw_response",
                profile_id,
                config_id,
            ),
            bundle_dir / "public_review" / "evidence_only_evaluator_raw_responses" / f"{profile_id}_{config_id}.json",
            "public_review.evidence_only_evaluator_raw_response",
            False,
            "evidence_only_evaluator_raw_response",
        ),
        (
            Path(row["hidden_truth_path"]),
            bundle_dir / "simulator_private" / "hidden_truth_packets" / f"{profile_id}_{config_id}.json",
            "simulator_private.hidden_truth_packet",
            True,
            "hidden_truth_packet",
        ),
        (
            matching_file(
                SOURCE_DIR / "executed_requests",
                "evaluator_truth_scored_request",
                profile_id,
                config_id,
            ),
            bundle_dir / "simulator_private" / "truth_scored_evaluator_requests" / f"{profile_id}_{config_id}.json",
            "simulator_private.truth_scored_evaluator_request",
            True,
            "truth_scored_evaluator_request",
        ),
        (
            Path(row["truth_output_path"]),
            bundle_dir / "simulator_private" / "truth_scored_evaluator_outputs" / f"{profile_id}_{config_id}.json",
            "simulator_private.truth_scored_evaluator_output",
            True,
            "truth_scored_evaluator_output",
        ),
        (
            matching_file(
                SOURCE_DIR / "raw_api_responses",
                "evaluator_truth_scored_raw_response",
                profile_id,
                config_id,
            ),
            bundle_dir / "simulator_private" / "truth_scored_evaluator_raw_responses" / f"{profile_id}_{config_id}.json",
            "simulator_private.truth_scored_evaluator_raw_response",
            True,
            "truth_scored_evaluator_raw_response",
        ),
    ]

    for source, destination, category, includes_hidden_data, key in artifact_specs:
        source = REPO_ROOT / source if not source.is_absolute() else source
        copy_artifact(
            source,
            destination,
            category=category,
            includes_hidden_data=includes_hidden_data,
            manifest_files=manifest_files,
        )
        copied[key] = rel(destination)

    return copied


def summarize_writer_output(path: Path) -> dict[str, Any]:
    data = load_json(path)
    atlas_seed = data.get("atlas_seed", {})
    return {
        "status": data.get("assessment_status", {}).get("status"),
        "confidence": data.get("assessment_status", {}).get("confidence"),
        "headline": data.get("profile_summary", {}).get("headline"),
        "short_read": data.get("profile_summary", {}).get("short_read"),
        "total_visible_items": data.get("evidence_audit", {}).get("total_visible_items"),
        "landmark_count": len(atlas_seed.get("landmarks", [])),
        "region_count": len(atlas_seed.get("regions", [])),
        "frontier_count": len(atlas_seed.get("frontiers", [])),
        "dead_end_hypothesis_count": len(atlas_seed.get("dead_end_hypotheses", [])),
        "waypoint_count": len(atlas_seed.get("waypoints", [])),
    }


def summarize_evaluator_output(path: Path) -> dict[str, Any]:
    data = load_json(path)
    red_flags = data.get("red_flags", [])
    breakdown = data.get("score_breakdown", {})
    blindness = breakdown.get("blindness_and_forbidden_context", {})
    return {
        "overall_decision": data.get("overall_decision"),
        "overall_score_100": data.get("overall_score_100"),
        "suspected_leakage": blindness.get("suspected_leakage", False),
        "red_flag_count": len(red_flags),
        "blocking_red_flag_count": sum(1 for flag in red_flags if flag.get("severity") == "blocking"),
        "major_red_flag_count": sum(1 for flag in red_flags if flag.get("severity") == "major"),
        "minor_red_flag_count": sum(1 for flag in red_flags if flag.get("severity") == "minor"),
        "red_flag_categories": sorted({flag.get("category", "unknown") for flag in red_flags}),
    }


def build_summary(
    *,
    metadata: dict[str, Any],
    row_summaries: list[dict[str, Any]],
    bundle_dir: Path,
    zip_path: Path,
) -> str:
    aggregate = metadata.get("aggregate", {})
    scores = aggregate.get("scores", {})
    issues = aggregate.get("issue_counts", {})
    gate = aggregate.get("gate", {})

    rows = "\n".join(
        "| {profile} | {role} | {config} | {tiles} | {writer_confidence} | {evidence_score} | {truth_score} | {headline} |".format(
            profile=row["profile_public_id"],
            role=row["selection_role"],
            config=row["config_id"],
            tiles=row["tile_count"],
            writer_confidence=row["writer_summary"].get("confidence"),
            evidence_score=row["evidence_only_summary"].get("overall_score_100"),
            truth_score=row["truth_scored_summary"].get("overall_score_100"),
            headline=(row["writer_summary"].get("headline") or "").replace("|", "/"),
        )
        for row in row_summaries
    )

    return f"""# GPT-5.5 3x3 Evidence Bundle

Generated: {datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")}

## Purpose

This bundle preserves the input and output evidence from the completed 3x3 `gpt-5.5` Profile Writer / Evaluator pilot. It is intended for review before increasing API limits or running a broader qualitative matrix.

## Boundary Contract

- `public_blind/` contains artifacts that are safe for the blind Profile Writer evidence path: public packets, executed Profile Writer requests, raw Profile Writer JSON, and Profile Writer raw API responses.
- `public_review/` contains evidence-only evaluator material derived from visible/public evidence only.
- `simulator_private/` contains hidden truth packets and truth-scored evaluator material. Do not feed this folder into Profile Writer, Survey Builder, predictor inputs, or user-visible transcripts.
- No new API calls were made while building this bundle.

## Bundle Location

- Directory: `{rel(bundle_dir)}`
- Zip archive: `{rel(zip_path)}`

## Run Summary

- Source run: `{rel(SOURCE_DIR)}`
- Model ID: `{metadata.get("model_id")}`
- Status: `{metadata.get("status")}`
- Profile Writer calls: `{metadata.get("call_counts", {}).get("profile_writer")}`
- Evidence-only Evaluator calls: `{metadata.get("call_counts", {}).get("evaluator_evidence_only")}`
- Truth-scored Evaluator calls: `{metadata.get("call_counts", {}).get("evaluator_truth_scored")}`
- Full 180-call batch run: `{metadata.get("scope", {}).get("full_180_call_batch_run")}`

## Aggregate Scores

- Average all evaluators: `{scores.get("average_all_evaluators")}`
- Average evidence-only: `{scores.get("average_evidence_only")}`
- Average truth-scored: `{scores.get("average_truth_scored")}`
- Min evaluator score: `{scores.get("minimum_all_evaluators")}`
- Max evaluator score: `{scores.get("maximum_all_evaluators")}`

## Tracked Issues

- Hidden-context leakage count: `{issues.get("hidden_context_leakage_count")}`
- Blocking red flag count: `{issues.get("blocking_red_flag_count")}`
- Genre shorthand issue count: `{issues.get("genre_shorthand_issue_count")}`
- Direct/contextual counterevidence issue count: `{issues.get("direct_contextual_counterevidence_issue_count")}`
- Secondary-lane underdevelopment count: `{issues.get("secondary_lane_underdevelopment_count")}`

## Gate Status

- Average evaluator score threshold: `{gate.get("average_evaluator_score_threshold")}`
- Zero hidden-context leakage: `{gate.get("zero_hidden_context_leakage")}`
- No blocking red flags: `{gate.get("no_blocking_red_flags")}`
- Genre shorthand issues tracked: `{gate.get("genre_shorthand_issues_tracked")}`
- Counterevidence issues measured: `{gate.get("counterevidence_issues_measured")}`
- Secondary lane underdevelopment tracked: `{gate.get("secondary_lane_underdevelopment_tracked")}`
- Overall 3x3 gate passed: `{aggregate.get("gate_passed")}`

## Row Index

| Profile | Selection role | Config | Tiles | Writer confidence | Evidence score | Truth score | Writer headline |
|---|---|---:|---:|---|---:|---:|---|
{rows}

## File Index

- Manifest: `{rel(bundle_dir / "manifest.json")}`
- Row summary: `{rel(bundle_dir / "row_summary.json")}`
- Raw Profile Writer JSON folder: `{rel(bundle_dir / "public_blind" / "raw_profile_writer_json")}`
- Public packets folder: `{rel(bundle_dir / "public_blind" / "public_packets")}`
- Evidence-only evaluator outputs: `{rel(bundle_dir / "public_review" / "evidence_only_evaluator_outputs")}`
- Simulator-private truth-scored outputs: `{rel(bundle_dir / "simulator_private" / "truth_scored_evaluator_outputs")}`
"""


def create_zip(bundle_dir: Path, zip_path: Path) -> None:
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(bundle_dir.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(bundle_dir.parent))


def build_bundle(bundle_id: str, force: bool) -> Path:
    if not SOURCE_DIR.exists():
        raise FileNotFoundError(SOURCE_DIR)

    bundle_dir = EVIDENCE_ROOT / bundle_id
    if bundle_dir.exists():
        if not force:
            raise FileExistsError(f"Bundle already exists: {bundle_dir}")
        shutil.rmtree(bundle_dir)
    bundle_dir.mkdir(parents=True)

    metadata = load_json(SOURCE_DIR / "api_pilot_3x3_execution_metadata.json")
    manifest_files: list[dict[str, Any]] = []

    metadata_dest = bundle_dir / "metadata" / "api_pilot_3x3_execution_metadata.json"
    copy_artifact(
        SOURCE_DIR / "api_pilot_3x3_execution_metadata.json",
        metadata_dest,
        category="metadata.execution_metadata",
        includes_hidden_data=False,
        manifest_files=manifest_files,
    )
    report_path = REPORTS_DIR / "api_pilot_3x3_execution_report.md"
    if report_path.exists():
        copy_artifact(
            report_path,
            bundle_dir / "metadata" / "api_pilot_3x3_execution_report.md",
            category="metadata.execution_report",
            includes_hidden_data=False,
            manifest_files=manifest_files,
        )

    row_summaries: list[dict[str, Any]] = []
    for row in metadata.get("rows", []):
        copied = copy_row_artifacts(row=row, bundle_dir=bundle_dir, manifest_files=manifest_files)
        writer_summary = summarize_writer_output(REPO_ROOT / copied["raw_profile_writer_json"])
        evidence_summary = summarize_evaluator_output(REPO_ROOT / copied["evidence_only_evaluator_output"])
        truth_summary = summarize_evaluator_output(REPO_ROOT / copied["truth_scored_evaluator_output"])
        row_summaries.append(
            {
                "profile_public_id": row["profile_public_id"],
                "selection_role": row["selection_role"],
                "config_id": row["config_id"],
                "tile_count": row["tile_count"],
                "public_packet_sha256": row["public_packet_sha256"],
                "public_packet_input_fingerprint": row["public_packet_input_fingerprint"],
                "profile_writer_status": row["profile_writer_status"],
                "profile_writer_request_sha256": row["profile_writer_request_sha256"],
                "evidence_request_sha256": row["evidence_request_sha256"],
                "truth_request_sha256": row["truth_request_sha256"],
                "writer_summary": writer_summary,
                "evidence_only_summary": evidence_summary,
                "truth_scored_summary": truth_summary,
                "bundle_paths": copied,
            }
        )

    row_summary_path = bundle_dir / "row_summary.json"
    write_json(row_summary_path, row_summaries)
    manifest_files.append(
        {
            "category": "metadata.row_summary",
            "source_path": None,
            "bundle_path": rel(row_summary_path),
            "bytes": row_summary_path.stat().st_size,
            "sha256": sha256_file(row_summary_path),
            "includes_hidden_data": True,
        }
    )

    manifest_path = bundle_dir / "manifest.json"
    manifest = {
        "schema_version": "waymark.llm_profile_review_evidence_bundle.v0.1",
        "bundle_id": bundle_id,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source_run": rel(SOURCE_DIR),
        "model_id": metadata.get("model_id"),
        "status": metadata.get("status"),
        "call_counts": metadata.get("call_counts"),
        "scope": metadata.get("scope"),
        "aggregate": metadata.get("aggregate"),
        "boundary_contract": {
            "public_blind_contains_hidden_data": False,
            "public_review_contains_hidden_data": False,
            "simulator_private_contains_hidden_data": True,
            "profile_writer_must_not_receive_simulator_private": True,
        },
        "files": manifest_files,
    }
    write_json(manifest_path, manifest)

    zip_path = EVIDENCE_ROOT / f"{bundle_id}.zip"
    summary = build_summary(metadata=metadata, row_summaries=row_summaries, bundle_dir=bundle_dir, zip_path=zip_path)
    readme_path = bundle_dir / "README.md"
    readme_path.write_text(summary, encoding="utf-8")

    for generated_path, category, includes_hidden_data in [
        (manifest_path, "metadata.manifest", True),
        (readme_path, "metadata.readme", True),
    ]:
        existing = next((item for item in manifest_files if item["bundle_path"] == rel(generated_path)), None)
        if existing:
            existing.update(
                {
                    "bytes": generated_path.stat().st_size,
                    "sha256": sha256_file(generated_path),
                    "includes_hidden_data": includes_hidden_data,
                }
            )
        else:
            manifest_files.append(
                {
                    "category": category,
                    "source_path": None,
                    "bundle_path": rel(generated_path),
                    "bytes": generated_path.stat().st_size,
                    "sha256": sha256_file(generated_path),
                    "includes_hidden_data": includes_hidden_data,
                }
            )

    write_json(manifest_path, manifest)
    create_zip(bundle_dir, zip_path)

    zip_manifest_path = EVIDENCE_ROOT / f"{bundle_id}.zip.sha256.json"
    write_json(
        zip_manifest_path,
        {
            "zip_path": rel(zip_path),
            "bytes": zip_path.stat().st_size,
            "sha256": sha256_file(zip_path),
        },
    )
    print(rel(bundle_dir))
    print(rel(zip_path))
    return bundle_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an evidence bundle for the completed GPT-5.5 3x3 pilot.")
    parser.add_argument("--bundle-id", default=DEFAULT_BUNDLE_ID)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    build_bundle(args.bundle_id, args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
