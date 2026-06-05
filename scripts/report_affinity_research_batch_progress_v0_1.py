#!/usr/bin/env python3
"""Report progress for researched affinity batches."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = ROOT / "review_packets/affinity_graphwide_v0_1/research_batches"
MANIFEST = BATCH_DIR / "affinity_research_batch_manifest_v0_1.json"
ALLOWED = ROOT / "data/canonical_graph/affinity_contracts/v0_3_1/cartenza_affinity_codex_repo_truth_package_v0_3_1/allowed_tags/allowed_canonical_tags_by_dimension_v0_3_1.json"
VALIDATOR = ROOT / "scripts/validate_affinity_research_batch_v0_1.py"
CHECKPOINT_TARGETS = [500, 1000, 2500, 5000]


def next_checkpoint(researched_song_count: int, total_song_count: int) -> int:
    for target in CHECKPOINT_TARGETS:
        if researched_song_count < target:
            return target
    return total_song_count


def progress_label(researched_song_count: int, total_song_count: int) -> str:
    if researched_song_count >= total_song_count:
        return "graphwide_research_complete_pending_pm_review"
    if researched_song_count >= 5000:
        return "internal_checkpoint_5000_research_in_progress"
    if researched_song_count >= 2500:
        return "internal_checkpoint_2500_research_in_progress"
    if researched_song_count >= 1000:
        return "internal_checkpoint_1000_research_in_progress"
    if researched_song_count >= 500:
        return "checkpoint_500_approved_research_in_progress"
    if researched_song_count >= 150:
        return "checkpoint_150_accepted_research_in_progress"
    return "research_in_progress_before_checkpoint"


def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    manifest = load_json(MANIFEST)
    completed = []
    failed = []
    missing = []
    for batch in manifest["batches"]:
        input_path = ROOT / batch["input_file"]
        output_path = ROOT / batch["expected_output_file"]
        if not output_path.exists():
            missing.append(batch["batch_id"])
            continue
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
            text=True,
            capture_output=True,
            check=False,
        )
        if proc.returncode == 0:
            completed.append(batch["batch_id"])
        else:
            failed.append({"batch_id": batch["batch_id"], "validator_output": proc.stdout[-4000:]})

    total = len(manifest["batches"])
    researched_song_count = sum(
        batch.get("song_count", manifest["metadata"]["batch_size"])
        for batch in manifest["batches"]
        if batch["batch_id"] in completed
    )
    total_song_count = manifest["metadata"]["song_count"]
    progress_status = progress_label(researched_song_count, total_song_count)
    checkpoint_target = next_checkpoint(researched_song_count, total_song_count)

    result = {
        "progress_status": progress_status,
        "next_checkpoint_song_count": checkpoint_target,
        "next_checkpoint_status": "ready_for_internal_QA" if researched_song_count >= checkpoint_target else "pending",
        "review_field_contract_status": "amended_core_overlay_review_fields",
        "runtime_ingestion_status": "not_approved",
        "derived_edge_construction_status": "not_approved",
        "total_batches": total,
        "completed_valid_batches": len(completed),
        "failed_batches": len(failed),
        "missing_batches": len(missing),
        "researched_song_count": researched_song_count,
        "completed_batch_ids": completed[:50],
        "failed": failed[:10],
        "next_missing_batch_ids": missing[:20],
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
