from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .atlas_utils import dedupe_records, load_json, make_atlas_node, make_bundle, make_role_assignment, write_json
from .build_atlas_digest_view import build_atlas_digest_view
from .ingest_mission_review_output import ingest_mission_review_fixtures
from .ingest_survey_output import ingest_survey_fixtures
from .report_writer import write_report
from .validate_atlas_records import validate_records


HARNESS_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = HARNESS_ROOT.parent
FIXTURES_ROOT = HARNESS_ROOT / "fixtures"
ATLAS_SCHEMA_PATH = REPO_ROOT / "data" / "atlas_schema" / "atlas_schema_contract_v0_1.json"
MISSION_DIGEST_FIXTURE = REPO_ROOT / "waymark-ai-tests" / "fixtures" / "atlas_digests" / "generated_atlas_digest_view_v0_1.json"
MISSION_GENERATION_DIGEST_FIXTURE = REPO_ROOT / "waymark-ai-tests" / "fixtures" / "atlas_digests" / "mission_generation_digest_view_v0_1.json"


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run Cartenza Atlas ingestion and digest tests.")
    parser.add_argument("--survey-fixtures", type=Path, default=FIXTURES_ROOT / "survey_outputs" / "survey_outputs_v0_1.json")
    parser.add_argument("--mission-review-fixtures", type=Path, default=FIXTURES_ROOT / "mission_review_outputs" / "mission_review_outputs_v0_1.json")
    parser.add_argument("--canonical-refs", type=Path, default=FIXTURES_ROOT / "canonical_refs" / "music_object_refs_v0_1.json")
    parser.add_argument("--expected-summary", type=Path, default=FIXTURES_ROOT / "expected_atlas_records" / "expected_summary_v0_1.json")
    parser.add_argument("--output-root", type=Path, default=HARNESS_ROOT / "outputs")
    parser.add_argument("--reports-root", type=Path, default=HARNESS_ROOT / "reports")
    parser.add_argument("--schema", type=Path, default=ATLAS_SCHEMA_PATH)
    parser.add_argument("--no-export-mission-digest", action="store_true", help="Do not write generated digest fixtures into waymark-ai-tests.")
    parser.add_argument("--skip-mission-smoke", action="store_true", help="Skip mission-generation dry-run compatibility smoke test.")
    parser.add_argument("--mission-smoke-request", default="nirvana_to_current")
    parser.add_argument("--mission-smoke-context-mode", default="mission_generation_digest_view_plus_features_plus_candidates")
    args = parser.parse_args(argv)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    output_dir = args.output_root / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    canonical_refs_doc = load_json(args.canonical_refs)
    survey_doc = load_json(args.survey_fixtures)
    mission_review_doc = load_json(args.mission_review_fixtures)
    expected_summary = load_json(args.expected_summary)
    refs = canonical_refs_doc["refs"]

    survey_records = ingest_survey_fixtures(survey_doc["fixtures"], refs)
    mission_review_records = ingest_mission_review_fixtures(mission_review_doc["fixtures"], refs)
    records = dedupe_records(survey_records + mission_review_records)
    records = dedupe_records(records + _synthetic_region_seed(records, generated_at))
    user_id = _select_user_id(records)
    digest_record, expanded_digest, mission_generation_digest = build_atlas_digest_view(
        records=records,
        user_id=user_id,
        generated_at=generated_at,
    )

    validation_result = validate_records(
        records=records,
        digest_record=digest_record,
        expanded_digest=expanded_digest,
        schema_path=args.schema,
        expected_summary=expected_summary,
    )

    bundle = make_bundle(
        "atlas_ingestion_generated_records_v0_1",
        "Generated Atlas ingestion records from synthetic Survey and Mission Review fixtures.",
        records + [digest_record],
    )
    write_json(output_dir / "generated_atlas_records.json", bundle)
    write_json(output_dir / "survey_ingestion_records.json", make_bundle("survey_ingestion_records_v0_1", "Records generated from synthetic Survey fixtures.", survey_records))
    write_json(output_dir / "mission_review_ingestion_records.json", make_bundle("mission_review_ingestion_records_v0_1", "Records generated from synthetic Mission Review fixtures.", mission_review_records))
    write_json(output_dir / "atlas_digest_view.json", digest_record)
    write_json(output_dir / "atlas_digest_view_expanded.json", expanded_digest)
    write_json(output_dir / "mission_generation_digest_view.json", mission_generation_digest)
    write_json(output_dir / "validation_result.json", validation_result)

    if not args.no_export_mission_digest:
        write_json(MISSION_DIGEST_FIXTURE, expanded_digest)
        write_json(MISSION_GENERATION_DIGEST_FIXTURE, mission_generation_digest)

    mission_smoke = None
    if not args.skip_mission_smoke:
        mission_smoke = _run_mission_smoke(
            request_id=args.mission_smoke_request,
            context_mode=args.mission_smoke_context_mode,
            output_dir=output_dir / "mission_smoke_outputs",
        )

    report_path = write_report(
        reports_root=args.reports_root,
        timestamp=timestamp,
        records=records,
        digest_record=digest_record,
        expanded_digest=expanded_digest,
        mission_generation_digest=mission_generation_digest,
        validation_result=validation_result,
        output_dir=output_dir,
        mission_smoke=mission_smoke,
    )
    print(f"Atlas ingestion output: {output_dir}")
    print(f"Atlas ingestion report: {report_path}")
    if not args.no_export_mission_digest:
        print(f"Mission harness digest fixture: {MISSION_DIGEST_FIXTURE}")
        print(f"Mission generation digest fixture: {MISSION_GENERATION_DIGEST_FIXTURE}")
    if mission_smoke:
        print(f"Mission smoke output: {mission_smoke.get('output_dir')}")

    return 0 if validation_result["valid"] and (not mission_smoke or mission_smoke.get("ran")) else 1


def _select_user_id(records: List[Dict[str, Any]]) -> str:
    for record in records:
        if record.get("user_id"):
            return record["user_id"]
    return "user_matt_atlas_harness"


def _synthetic_region_seed(records: List[Dict[str, Any]], generated_at: str) -> List[Dict[str, Any]]:
    signal_ids = {record.get("signal_id") for record in records if record.get("record_type") == "signal"}
    evidence_signal_ids = [
        signal_id
        for signal_id in [
            "signal:survey_event:nirvana_favorite",
            "signal:survey_event:body_fake_hard_note",
            "signal:mission_review_event:current_rock_probe_like",
        ]
        if signal_id in signal_ids
    ]
    if len(evidence_signal_ids) < 2:
        return []
    user_id = _select_user_id(records)
    atlas_node_id = "atlas_node:body_first_guitar_pressure_region"
    role_assignment_id = "role:body_first_guitar_pressure_region:region"
    return [
        make_atlas_node(
            atlas_node_id=atlas_node_id,
            user_id=user_id,
            node_type="genre_lane",
            display_name="Body-first guitar pressure",
            subtitle="Provisional Region candidate from clustered evidence",
            music_object_ref=None,
            origin="review",
            render_summary="A provisional Region candidate grouping body, pressure, and anti-fake-hard evidence without claiming final truth.",
            evidence_signal_ids=evidence_signal_ids,
            confidence_score=0.61,
            confidence_basis="mixed",
            confidence_summary="Multiple synthetic evidence sources point toward a useful Region candidate, but it remains review-gated.",
            created_at=generated_at,
            review_state="needs_review",
        ),
        make_role_assignment(
            role_assignment_id=role_assignment_id,
            user_id=user_id,
            atlas_node_id=atlas_node_id,
            role="region",
            candidate_pool_behavior="bridge",
            assignment_summary="Use as a bridge Region for candidate-pool grouping; not a final promoted taste Region.",
            evidence_signal_ids=evidence_signal_ids,
            confidence_score=0.61,
            confidence_basis="mixed",
            confidence_summary="Region assignment is provisional and exists to test digest routing over grouped evidence.",
            created_at=generated_at,
            review_state="needs_review",
        ),
    ]


def _run_mission_smoke(*, request_id: str, context_mode: str, output_dir: Path) -> Dict[str, Any]:
    script = REPO_ROOT / "waymark-ai-tests" / "src" / "run_mission_generation_tests.py"
    if not script.exists():
        return {
            "ran": False,
            "request_id": request_id,
            "context_mode": context_mode,
            "dry_run_payload_written": False,
            "output_dir": str(output_dir),
            "notes": "Mission harness script not found.",
        }
    command = [
        sys.executable,
        str(script),
        "--request",
        request_id,
        "--prompt-template",
        "mission_generator_candidate_constrained_v0_1",
        "--context-mode",
        context_mode,
        "--model",
        "gpt-5.4-mini",
        "--dry-run",
        "--output-root",
        str(output_dir),
    ]
    result = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    payloads = list(output_dir.glob("*/request_payload.json"))
    return {
        "ran": result.returncode == 0,
        "request_id": request_id,
        "context_mode": context_mode,
        "dry_run_payload_written": bool(payloads),
        "output_dir": str(output_dir),
        "notes": (result.stdout or result.stderr).strip(),
    }
