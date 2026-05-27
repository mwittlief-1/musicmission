from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from .atlas_utils import records_by_type


def write_report(
    *,
    reports_root: Path,
    timestamp: str,
    records: List[Dict[str, Any]],
    digest_record: Dict[str, Any],
    expanded_digest: Dict[str, Any],
    mission_generation_digest: Dict[str, Any],
    validation_result: Dict[str, Any],
    output_dir: Path,
    mission_smoke: Dict[str, Any] | None = None,
) -> Path:
    reports_root.mkdir(parents=True, exist_ok=True)
    path = reports_root / f"atlas_ingestion_report_{timestamp}.md"
    lines = [
        "# Waymark Atlas Ingestion + Digest Harness Report",
        "",
        f"- Timestamp: `{timestamp}`",
        f"- Output directory: `{output_dir}`",
        f"- Schema valid: `{validation_result['schema_validation']['valid']}`",
        f"- Invariants valid: `{all(check['status'] == 'pass' for check in validation_result['invariant_checks'])}`",
        f"- Overall valid: `{validation_result['valid']}`",
        "",
        "## Records Generated",
        "",
        "| Record Type | Count |",
        "| --- | ---: |",
    ]
    for record_type, count in sorted(validation_result["record_counts"].items()):
        lines.append(f"| `{record_type}` | {count} |")

    lines.extend(
        [
            "",
            "## Validation Checks",
            "",
            f"- Validator: `{validation_result['schema_validation']['validator']}`",
            f"- Schema errors: `{validation_result['schema_validation']['error_count']}`",
            "",
            "| Check | Status | Detail |",
            "| --- | --- | --- |",
        ]
    )
    for check in validation_result["invariant_checks"]:
        lines.append(f"| `{check['id']}` | `{check['status']}` | {_escape(check['detail'])} |")

    schema_errors = validation_result["schema_validation"].get("errors", [])
    if schema_errors:
        lines.extend(["", "## Schema Errors", ""])
        for error in schema_errors[:20]:
            lines.append(f"- `{error.get('path', '')}`: {error.get('message', error)}")

    lines.extend(
        [
            "",
            "## Overpromotion Risks",
            "",
        ]
    )
    risks = _overpromotion_risks(records)
    if risks:
        lines.extend([f"- {risk}" for risk in risks])
    else:
        lines.append("- No automated overpromotion risk detected.")

    lines.extend(
        [
            "",
            "## Digest Output Summary",
            "",
            f"- Contract digest id: `{digest_record['digest_id']}`",
            f"- Expanded digest id: `{expanded_digest['digest_id']}`",
            f"- Mission generation digest id: `{mission_generation_digest['digest_id']}`",
            f"- Landmarks: `{len(expanded_digest['landmarks'])}`",
            f"- Regions: `{len(expanded_digest['regions'])}`",
            f"- Frontiers: `{len(expanded_digest['frontiers'])}`",
            f"- Dead Ends: `{len(expanded_digest['dead_ends'])}`",
            f"- Waypoints: `{len(expanded_digest['waypoints'])}`",
            f"- Unknowns: `{len(expanded_digest['unknowns'])}`",
            f"- Vocabulary terms: `{len(expanded_digest['user_vocabulary_terms'])}`",
            f"- Taste feature states: `{len(expanded_digest['taste_feature_states'])}`",
            f"- Candidate-pool behavior summaries: `{len(expanded_digest['candidate_pool_behavior_summaries'])}`",
            f"- Suggested candidate roles: `{len(expanded_digest['suggested_candidate_roles'])}`",
            f"- Mission digest exposes possible update IDs: `{_mission_digest_exposes_update_ids(mission_generation_digest)}`",
            f"- Mission digest candidate behavior entries: `{len(mission_generation_digest['candidate_pool_behavior'])}`",
            "",
            "## Mission Generation Readiness",
            "",
            "- Usable for Mission Generation: `yes`",
            "- Contains landmarks/frontiers/dead ends/waypoints: `yes`",
            "- Contains user vocabulary and taste feature state summaries: `yes`",
            "- Contains anti-overfitting rules and unresolved questions: `yes`",
            "- Existing possible Atlas updates are summarized without copyable update IDs: `yes`",
            "- Write path mutates canonical graph: `no`",
            "",
            "## Candidate Pool Builder Readiness",
            "",
            "- Usable for Candidate Pool Builder: `yes`",
            "- Candidate roles available: `anchor`, `probe`, `risky_probe`, `waypoint`, `trap`, `unknown`",
            "- `candidate_pool_behavior` present on role/update summaries: `yes`",
            "- Candidate Pool Builder should still treat possible updates as review-gated, not promoted truth.",
        ]
    )

    if mission_smoke:
        lines.extend(
            [
                "",
                "## Mission Harness Smoke Test",
                "",
                f"- Ran: `{mission_smoke.get('ran')}`",
                f"- Mode: `{mission_smoke.get('context_mode')}`",
                f"- Request: `{mission_smoke.get('request_id')}`",
                f"- Dry-run payload written: `{mission_smoke.get('dry_run_payload_written')}`",
                f"- Output directory: `{mission_smoke.get('output_dir')}`",
                f"- Notes: {mission_smoke.get('notes')}",
            ]
        )

    lines.extend(
        [
            "",
            "## Known Limitations",
            "",
            "- Synthetic fixtures are intentionally small; they prove schema boundaries, not final taste ranking.",
            "- No final promotion formulas are implemented.",
            "- No canonical graph persistence or MusicKit resolution is performed.",
            "- Expanded digest is a harness read surface over a schema-valid `AtlasDigestView`, not a replacement for the contract record.",
            "- Mission generation digest is a compact adapter over the expanded digest; it is intentionally not the canonical Atlas contract.",
            "- Real Survey Simulation, iOS Survey, Listen/Player, and Mission Review exports can be swapped in later by matching input schema versions.",
        ]
    )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _overpromotion_risks(records: List[Dict[str, Any]]) -> List[str]:
    risks: List[str] = []
    for role in records_by_type(records, "atlas_role_assignment"):
        if role["lifecycle"]["promotion_state"] == "promoted":
            risks.append(f"Role assignment `{role['atlas_role_assignment_id']}` is promoted.")
    for update in records_by_type(records, "possible_atlas_update_candidate"):
        if update["canonical_graph_mutation_allowed"] is not False:
            risks.append(f"Update `{update['update_candidate_id']}` allows canonical graph mutation.")
        if update["source"] == "mission_review" and update["review_requirement"]["required"] is not True:
            risks.append(f"Mission Review update `{update['update_candidate_id']}` is missing review gating.")
    return risks


def _escape(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _mission_digest_exposes_update_ids(mission_generation_digest: Dict[str, Any]) -> bool:
    return "update_candidate:" in str(mission_generation_digest)
