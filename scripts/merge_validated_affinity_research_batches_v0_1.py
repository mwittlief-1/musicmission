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
DUPLICATE_REVIEW = BASE / "affinity_duplicate_context_review_graphwide_v0_1.json"
SHARD_MANIFEST = BASE / "affinity_graphwide_shard_manifest_v0_1.json"

DUPLICATE_REVIEW_CODES_BY_TYPE = {
    "context_surface_duplicate": {"duplicate_context_unclear", "context_leak_risk"},
    "composition_variant": {
        "duplicate_context_unclear",
        "recording_identity_unclear",
        "version_ambiguity",
    },
    "version_ambiguity": {"recording_identity_unclear", "version_ambiguity"},
}


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


def duplicate_groups_by_song() -> dict[str, list[dict[str, Any]]]:
    if not DUPLICATE_REVIEW.exists():
        return {}
    data = load_json(DUPLICATE_REVIEW)
    out: dict[str, list[dict[str, Any]]] = {}
    for group in data.get("candidate_groups", []):
        if not isinstance(group, dict):
            continue
        for song_id in group.get("song_ids", []):
            if isinstance(song_id, str) and song_id:
                out.setdefault(song_id, []).append(group)
    for groups in out.values():
        groups.sort(key=lambda item: str(item.get("candidate_group_id", "")))
    return out


def enrich_duplicate_context_review(songs: list[dict[str, Any]]) -> int:
    """Attach deterministic duplicate/context flags without changing tags."""

    by_song = duplicate_groups_by_song()
    flagged = 0
    for song in songs:
        song_id = song.get("canonical_song_recording_id")
        groups = by_song.get(song_id, [])
        if not groups:
            continue

        reason_codes: set[str] = set()
        candidate_types: set[str] = set()
        candidate_group_ids: list[str] = []
        risks: set[str] = set()
        recommended_actions: set[str] = set()
        notes: list[str] = []
        for group in groups:
            group_type = str(group.get("candidate_type", "") or "unknown")
            candidate_types.add(group_type)
            group_id = str(group.get("candidate_group_id", "") or "")
            if group_id:
                candidate_group_ids.append(group_id)
            risk = str(group.get("risk", "") or "")
            if risk:
                risks.add(risk)
            action = str(group.get("recommended_action", "") or "")
            if action:
                recommended_actions.add(action)
            note = str(group.get("notes", "") or "")
            if note:
                notes.append(note)
            reason_codes.update(
                DUPLICATE_REVIEW_CODES_BY_TYPE.get(
                    group_type,
                    {"duplicate_context_unclear", "version_ambiguity"},
                )
            )

        song["duplicate_context_review"] = {
            "needed": True,
            "reason_codes": sorted(reason_codes),
            "candidate_types": sorted(candidate_types),
            "candidate_group_ids": candidate_group_ids,
            "risk": sorted(risks),
            "recommended_actions": sorted(recommended_actions),
            "notes": " ".join(dict.fromkeys(notes)),
        }

        review = song.setdefault("review", {})
        existing_codes = review.get("review_reason_codes", []) or []
        review["review_reason_codes"] = sorted(set(existing_codes) | reason_codes)
        review["identity_review_needed"] = bool(
            review.get("identity_review_needed")
            or {"recording_identity_unclear", "version_ambiguity"} & reason_codes
        )
        review["core_tag_review_needed"] = bool(review.get("core_tag_review_needed"))
        review["overlay_review_needed"] = bool(
            review.get("overlay_review_needed")
            or {"duplicate_context_unclear", "context_leak_risk"} & reason_codes
        )
        review["duplicate_context_review_needed"] = True
        review["context_leak_review_needed"] = bool("context_leak_risk" in reason_codes)
        review["review_reason"] = "; ".join(review["review_reason_codes"])
        review.pop("tag_review_needed", None)
        flagged += 1
    return flagged


def enrich_membership_overlay_metadata(
    songs: list[dict[str, Any]],
    membership_context: dict[str, dict[str, Any]],
) -> None:
    for song in songs:
        song.setdefault("canonical_composition_id", "")
        for overlay in song.get("membership_context_overlays", []):
            if not isinstance(overlay, dict):
                continue
            membership_id = overlay.get("membership_id", "")
            ctx = membership_context.get(membership_id, {})
            overlay.setdefault("song_archetype_membership_id", membership_id)
            overlay.setdefault("family_id", f"family_{ctx.get('family_number')}" if ctx.get("family_number") is not None else "")
            overlay.setdefault("family_number", ctx.get("family_number"))
            overlay.setdefault("family_scope", ctx.get("family_scope", ""))
            overlay.setdefault("archetype_id", ctx.get("archetype_id", ""))
            overlay.setdefault("archetype_name", ctx.get("archetype_name", ""))
            overlay.setdefault("membership_roles", ctx.get("membership_roles", []))
            overlay.setdefault("recognition_tier", ctx.get("recognition_tier", ""))
            overlay.setdefault("survey_tier", ctx.get("survey_tier", ""))


def progress_status(completed_song_count: int, total_song_count: int) -> str:
    if completed_song_count >= total_song_count:
        return "graphwide_research_complete_pending_pm_review"
    if completed_song_count >= 5000:
        return "internal_checkpoint_5000_research_in_progress"
    if completed_song_count >= 2500:
        return "internal_checkpoint_2500_research_in_progress"
    if completed_song_count >= 1000:
        return "internal_checkpoint_1000_research_in_progress"
    if completed_song_count >= 500:
        return "checkpoint_500_approved_research_in_progress"
    if completed_song_count >= 150:
        return "checkpoint_150_accepted_research_in_progress"
    return "research_in_progress_before_checkpoint"


def next_checkpoint(completed_song_count: int, total_song_count: int) -> int:
    for target in (1000, 2500, 5000):
        if completed_song_count < target:
            return target
    return total_song_count


def final_metadata(completed_count: int, total_count: int, flagged_count: int) -> dict[str, Any]:
    return {
        "artifact_name": "affinity_song_tags_graphwide_v0_1",
        "generated": str(date.today()),
        "status": progress_status(completed_count, total_count),
        "ontology_version": "v0.2.2_schema_amended_v0.3.1",
        "schema_version": "v0.3.1_amended_research_contract",
        "source_graph": "data/canonical_graph/depth_hardening_v0_2/pass_d/graph_tagging_corpus_v1.json",
        "source_graph_promoted_canonical": True,
        "runtime_ingestion_status": "not_approved",
        "derived_edge_construction_status": "not_approved",
        "review_field_contract_status": "amended_core_overlay_review_fields",
        "research_method": "per-song evidence-backed research batches",
        "completed_batch_count": completed_count // 25 if completed_count else 0,
        "completed_song_count": completed_count,
        "total_song_count": total_count,
        "duplicate_context_review_flagged_song_count": flagged_count,
        "notes": "PM-review sidecar only. Runtime ingestion and derived edge construction remain blocked pending PM approval.",
    }


def write_final_outputs(songs: list[dict[str, Any]], metadata: dict[str, Any]) -> None:
    write_json(BASE / "affinity_song_tags_graphwide_v0_1.json", {"metadata": metadata, "songs": songs})
    if not SHARD_MANIFEST.exists():
        return
    shard_manifest = load_json(SHARD_MANIFEST)
    songs_by_id = {song["canonical_song_recording_id"]: song for song in songs}
    for shard in shard_manifest.get("shards", []):
        shard_songs = [
            songs_by_id[song_id]
            for song_id in shard.get("song_identity_keys", [])
            if song_id in songs_by_id
        ]
        write_json(
            BASE / shard["expected_output_file"],
            {
                "metadata": {
                    **metadata,
                    "shard_id": shard.get("shard_id"),
                    "family_number": shard.get("family_number"),
                    "family_name": shard.get("family_name"),
                },
                "songs": shard_songs,
            },
        )


def main() -> int:
    manifest = load_json(MANIFEST)
    merged_songs = []
    completed = []
    skipped = []
    membership_context: dict[str, dict[str, Any]] = {}
    for batch in manifest["batches"]:
        input_path = ROOT / batch["input_file"]
        output_path = ROOT / batch["expected_output_file"]
        input_doc = load_json(input_path)
        for song in input_doc.get("songs", []):
            for membership in song.get("memberships", []):
                membership_id = membership.get("membership_id", "")
                if membership_id:
                    membership_context[membership_id] = membership
        if not output_path.exists():
            skipped.append({"batch_id": batch["batch_id"], "reason": "missing"})
            continue
        if not batch_valid(input_path, output_path):
            skipped.append({"batch_id": batch["batch_id"], "reason": "validator_failed"})
            continue
        doc = load_json(output_path)
        merged_songs.extend(doc["songs"])
        completed.append(batch["batch_id"])

    enrich_membership_overlay_metadata(merged_songs, membership_context)
    duplicate_flagged_count = enrich_duplicate_context_review(merged_songs)
    counts = Counter(core_count(song) for song in merged_songs)
    duplicate_ids = [
        sid
        for sid, count in Counter(song["canonical_song_recording_id"] for song in merged_songs).items()
        if count > 1
    ]
    metadata = final_metadata(
        len(merged_songs),
        manifest["metadata"]["song_count"],
        duplicate_flagged_count,
    )
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
            "duplicate_context_review_flagged_song_count": duplicate_flagged_count,
            "notes": "Contains only batches that passed the amended research-batch validator, with deterministic duplicate/context review flags joined from the graphwide review file. This replaces heuristic rows only when graph-wide research is complete and PM approves sidecar use.",
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
            "next_checkpoint_song_count": next_checkpoint(len(merged_songs), manifest["metadata"]["song_count"]),
            "next_checkpoint_status": "pending",
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
            "duplicate_context_review_flagged_song_count": duplicate_flagged_count,
            "completed_batch_ids": completed,
            "skipped": skipped[:50],
        },
    )
    if len(merged_songs) == manifest["metadata"]["song_count"] and not skipped:
        write_final_outputs(merged_songs, metadata)
    return 1 if duplicate_ids else 0


if __name__ == "__main__":
    sys.exit(main())
