#!/usr/bin/env python3
"""Merge only validated researched affinity batches into a partial sidecar."""

from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "review_packets/affinity_graphwide_v0_1"
BATCH_DIR = BASE / "research_batches"
MANIFEST = BATCH_DIR / "affinity_research_batch_manifest_v0_1.json"
ALLOWED = ROOT / "data/canonical_graph/affinity_contracts/v0_3_1/cartenza_affinity_codex_repo_truth_package_v0_3_1/allowed_tags/allowed_canonical_tags_by_dimension_v0_3_1.json"
VALIDATOR = ROOT / "scripts/validate_affinity_research_batch_v0_1.py"


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def batch_valid(input_file: Path, output_file: Path) -> bool:
    proc = subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            "--input",
            str(input_file),
            "--output",
            str(output_file),
            "--allowed",
            str(ALLOWED),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode == 0


def core_count(song: dict[str, Any]) -> int:
    dims = ["vocal_performance", "emotion_theme", "sonic_texture", "rhythm_body", "form_container"]
    count = 0
    core = song.get("canonical_song_affinity_tags", {})
    for dim in dims:
        bucket = core.get(dim, {})
        count += len(bucket.get("primary", []) or [])
        count += len(bucket.get("secondary", []) or [])
    return count


def progress_status(completed_song_count: int, total_song_count: int) -> str:
    if completed_song_count >= total_song_count:
        return "graphwide_research_complete_pending_pm_review"
    if completed_song_count >= 500:
        return "checkpoint_500_ready_for_semantic_review"
    if completed_song_count >= 150:
        return "checkpoint_150_accepted_research_in_progress"
    return "research_in_progress_before_checkpoint"


def main() -> int:
    manifest = load_json(MANIFEST)
    merged_songs = []
    completed = []
    skipped = []
    for batch in manifest["batches"]:
        input_path = ROOT / batch["input_file"]
        output_path = ROOT / batch["expected_output_file"]
        if not output_path.exists():
            skipped.append({"batch_id": batch["batch_id"], "reason": "missing"})
            continue
        if not batch_valid(input_path, output_path):
            skipped.append({"batch_id": batch["batch_id"], "reason": "validator_failed"})
            continue
        doc = load_json(output_path)
        merged_songs.extend(doc["songs"])
        completed.append(batch["batch_id"])

    counts = Counter(core_count(song) for song in merged_songs)
    duplicate_ids = [
        sid
        for sid, count in Counter(song["canonical_song_recording_id"] for song in merged_songs).items()
        if count > 1
    ]
    out = {
        "metadata": {
            "artifact_name": "affinity_researched_song_tags_partial_v0_1",
            "generated": str(date.today()),
            "status": progress_status(len(merged_songs), manifest["metadata"]["song_count"]),
            "runtime_ingestion_status": "not_approved",
            "derived_edge_construction_status": "not_approved",
            "completed_batch_count": len(completed),
            "completed_song_count": len(merged_songs),
            "remaining_batch_count": len(manifest["batches"]) - len(completed),
            "notes": "Contains only batches that passed the amended research-batch validator. This replaces heuristic rows only when graph-wide research is complete and PM approves sidecar use.",
        },
        "songs": merged_songs,
    }
    status = progress_status(len(merged_songs), manifest["metadata"]["song_count"])
    write_json(BASE / "affinity_researched_song_tags_partial_v0_1.json", out)
    write_json(
        BASE / "affinity_research_progress_metrics_v0_1.json",
        {
            "generated": str(date.today()),
            "progress_status": status,
            "next_checkpoint_song_count": 500,
            "next_checkpoint_status": "ready_for_review" if len(merged_songs) >= 500 else "pending",
            "review_field_contract_status": "amended_core_overlay_review_fields",
            "runtime_ingestion_status": "not_approved",
            "derived_edge_construction_status": "not_approved",
            "completed_batch_count": len(completed),
            "completed_song_count": len(merged_songs),
            "total_batch_count": len(manifest["batches"]),
            "total_song_count": manifest["metadata"]["song_count"],
            "remaining_batch_count": len(manifest["batches"]) - len(completed),
            "remaining_song_count": manifest["metadata"]["song_count"] - len(merged_songs),
            "core_tag_count_distribution": dict(sorted(counts.items())),
            "duplicate_song_ids": duplicate_ids,
            "completed_batch_ids": completed,
            "skipped": skipped[:50],
        },
    )
    return 1 if duplicate_ids else 0


if __name__ == "__main__":
    sys.exit(main())
