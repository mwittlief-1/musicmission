#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "data" / "alpha_packets" / "golden_alpha_packet_v0_1"

SURVEY_EXPORT = (
    REPO_ROOT
    / "data"
    / "survey_simulation"
    / "survey_evidence_export"
    / "samples"
    / "public_profile_01_A3_Al1_S2_survey_evidence_export.json"
)
MISSION_DIGEST = (
    REPO_ROOT
    / "waymark-atlas-tests"
    / "outputs"
    / "20260520T151906Z"
    / "mission_generation_digest_view.json"
)
CANDIDATE_POOL = (
    REPO_ROOT
    / "waymark-ai-tests"
    / "fixtures"
    / "candidate_pools"
    / "candidate_pool_nirvana_to_current.json"
)
GENERATION_RUN = (
    REPO_ROOT
    / "waymark-ai-tests"
    / "outputs"
    / "20260520T152256Z_001_nirvana_to_current_mission_generator_candidate_constrained_v0_1_mission_generation_digest_view_plus_features_plus_candidates_gpt-5_4-mini_run01"
)

GENERATED_AT = "2026-05-21T20:00:00Z"
CLIENT_REQUEST_ID = "golden-alpha-v0-1-nirvana-current"
TESTER_ALIAS = "trusted-alpha-golden"
RAW_MISSION_OUTPUT_FILENAME = "mission_output_cartenza_v0_1.raw.json"
REVIEWED_MISSION_OUTPUT_FILENAME = "mission_output_cartenza_v0_1.reviewed_app_import_candidate.json"


def main() -> int:
    require_inputs()
    reset_output_dir()

    survey_export = load_json(SURVEY_EXPORT)
    mission_digest = load_json(MISSION_DIGEST)
    candidate_pool = load_json(CANDIDATE_POOL)
    source_generation = load_json(GENERATION_RUN / "parsed_output.json")
    source_metadata = load_json(GENERATION_RUN / "metadata.json")
    source_validation = load_json(GENERATION_RUN / "validation_result.json")
    source_score = load_json(GENERATION_RUN / "score_report.json")

    reviewed_generation = reviewed_app_import_candidate(source_generation)
    app_mission = to_app_mission(reviewed_generation)
    supabase_request = build_supabase_request(survey_export, mission_digest, candidate_pool)
    supabase_response = build_supabase_response(
        reviewed_generation=reviewed_generation,
        app_mission=app_mission,
        source_metadata=source_metadata,
    )
    review_gate = build_review_gate(source_metadata, source_validation, source_score)
    write_json(OUT_DIR / "inputs" / "survey_evidence_export.json", survey_export)
    write_json(OUT_DIR / "inputs" / "mission_generation_digest_view.json", mission_digest)
    write_json(OUT_DIR / "inputs" / "candidate_pool.json", candidate_pool)
    write_json(OUT_DIR / "request" / "supabase_generate_first_mission_batch_request.json", supabase_request)
    write_json(OUT_DIR / "generation" / RAW_MISSION_OUTPUT_FILENAME, source_generation)
    write_json(OUT_DIR / "generation" / REVIEWED_MISSION_OUTPUT_FILENAME, reviewed_generation)
    write_json(OUT_DIR / "generation" / "source_metadata.json", source_metadata)
    write_json(OUT_DIR / "generation" / "source_validation_result.json", source_validation)
    write_json(OUT_DIR / "generation" / "source_score_report.json", source_score)
    write_json(OUT_DIR / "review" / "app_import_review_gate.json", review_gate)
    write_json(OUT_DIR / "app_import" / "app_mission_v0_2.json", app_mission)
    write_json(OUT_DIR / "app_import" / "app_mission_collection_v0_2.json", [app_mission])
    write_json(OUT_DIR / "response" / "supabase_generate_first_mission_batch_response.json", supabase_response)
    run_validations()

    manifest = build_manifest(
        source_metadata=source_metadata,
        source_validation=source_validation,
        source_score=source_score,
        review_gate=review_gate,
        app_mission=app_mission,
    )
    write_json(OUT_DIR / "manifest.json", manifest)
    write_text(OUT_DIR / "README.md", render_readme(manifest))

    print(f"Wrote {OUT_DIR}")
    return 0


def require_inputs() -> None:
    missing = [
        path
        for path in [
            SURVEY_EXPORT,
            MISSION_DIGEST,
            CANDIDATE_POOL,
            GENERATION_RUN / "parsed_output.json",
            GENERATION_RUN / "metadata.json",
            GENERATION_RUN / "validation_result.json",
            GENERATION_RUN / "score_report.json",
        ]
        if not path.exists()
    ]
    if missing:
        raise SystemExit("Missing packet input(s):\n" + "\n".join(str(path) for path in missing))


def reset_output_dir() -> None:
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def reviewed_app_import_candidate(generation: dict[str, Any]) -> dict[str, Any]:
    reviewed = json.loads(json.dumps(generation))
    review_config = reviewed.setdefault("review_config", {})
    review_config["ready_for_app_import"] = True
    review_config["requires_human_review"] = True
    review_config["notes"] = (
        f"{review_config.get('notes', '').strip()} "
        "Golden Alpha packet review override: schema-valid product_pass_candidate output is marked app-import-ready "
        "for integration testing only. This does not imply Atlas promotion or public-quality autonomy."
    ).strip()
    review_config.setdefault("review_focus", [])
    if "golden packet adapter check" not in review_config["review_focus"]:
        review_config["review_focus"].append("golden packet adapter check")
    return reviewed


def build_supabase_request(
    survey_export: dict[str, Any],
    mission_digest: dict[str, Any],
    candidate_pool: dict[str, Any],
) -> dict[str, Any]:
    return {
        "client_request_id": CLIENT_REQUEST_ID,
        "tester_alias": TESTER_ALIAS,
        "requested_batch_size": 1,
        "survey_evidence_export": survey_export,
        "mission_generation_digest_view": mission_digest,
        "candidate_pool": candidate_pool,
        "prompt_context": {
            "alpha_scope": "first_batch",
            "storefront": "us",
            "generation_mode": "golden_packet_replay",
            "prompt_version": "mission_generator_candidate_constrained_v0_1",
            "target_model": "gpt-5.4-mini",
            "review_gate": "manual_app_import_override_for_integration_packet",
        },
    }


def build_supabase_response(
    *,
    reviewed_generation: dict[str, Any],
    app_mission: dict[str, Any],
    source_metadata: dict[str, Any],
) -> dict[str, Any]:
    return {
        "run_id": "00000000-0000-4000-8000-000000000101",
        "status": "app_import_candidate",
        "prompt_version": source_metadata.get("prompt_template", "mission_generator_candidate_constrained_v0_1"),
        "model": source_metadata.get("model", "gpt-5.4-mini"),
        "mission_output_schema_version": reviewed_generation.get("schema_version"),
        "app_mission_schema_version": app_mission.get("schema_version"),
        "generation": reviewed_generation,
        "app_missions": [app_mission],
        "validation": {
            "generation": {
                "valid": True,
                "source_validation_file": "generation/source_validation_result.json",
            },
            "app_mission": {
                "valid": True,
                "validation_command": "python3 scripts/validate_mission_json.py data/alpha_packets/golden_alpha_packet_v0_1/app_import/app_mission_v0_2.json",
                "validation_report": "validation/app_mission_v0_2_validation_report.md",
            },
        },
        "usage": {
            "input_tokens": source_metadata.get("input_tokens"),
            "cached_input_tokens": source_metadata.get("cached_input_tokens"),
            "output_tokens": source_metadata.get("output_tokens"),
            "total_tokens": source_metadata.get("total_tokens"),
            "estimated_total_cost_usd": source_metadata.get("estimated_total_cost_usd"),
        },
        "latency_ms": int(float(source_metadata.get("latency_seconds") or 0) * 1000),
    }


def build_review_gate(
    source_metadata: dict[str, Any],
    source_validation: dict[str, Any],
    source_score: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "waymark.alpha_app_import_review_gate.v0.1",
        "reviewed_at": GENERATED_AT,
        "source_generation_status": {
            "validation_valid": source_validation.get("valid"),
            "validation_error_count": source_validation.get("error_count"),
            "product_readiness_status": source_metadata.get("product_readiness_status"),
            "model_declared_app_import_ready": source_metadata.get("model_declared_app_import_ready"),
            "score_fail_count": source_score.get("fail_count"),
            "score_partial_count": source_score.get("partial_count"),
            "score_pass_count": source_score.get("pass_count"),
        },
        "override": {
            "applied": True,
            "target_status": "app_import_candidate",
            "reason": (
                "Golden integration packet needs a complete app-import artifact. The source output is schema-valid "
                "with zero automated product failures, but the model left ready_for_app_import false pending human review."
            ),
            "limits": [
                "Does not prove autonomous mission generation is ready.",
                "Does not promote Atlas roles.",
                "Does not bypass physical-device MusicKit QA.",
            ],
        },
        "required_followup": [
            "Replace this override with the final Supabase product review gate.",
            "Rerun after Survey, Atlas, and Canonical Graph lanes deliver frozen Alpha contracts.",
            "Run MusicKit resolution QA against every route item before external testers.",
        ],
    }


def build_manifest(
    *,
    source_metadata: dict[str, Any],
    source_validation: dict[str, Any],
    source_score: dict[str, Any],
    review_gate: dict[str, Any],
    app_mission: dict[str, Any],
) -> dict[str, Any]:
    files = sorted(path for path in OUT_DIR.rglob("*") if path.is_file())
    return {
        "schema_version": "waymark.alpha_golden_packet_manifest.v0.1",
        "packet_id": "golden_alpha_packet_v0_1",
        "generated_at": GENERATED_AT,
        "purpose": "Golden end-to-end Alpha integration packet from Survey evidence through app-importable mission.v0.2.",
        "source_paths": {
            "survey_evidence_export": rel(SURVEY_EXPORT),
            "mission_generation_digest_view": rel(MISSION_DIGEST),
            "candidate_pool": rel(CANDIDATE_POOL),
            "generation_run": rel(GENERATION_RUN),
        },
        "status": {
            "source_generation_schema_valid": source_validation.get("valid"),
            "source_generation_product_readiness": source_metadata.get("product_readiness_status"),
            "source_generation_model_declared_app_import_ready": source_metadata.get("model_declared_app_import_ready"),
            "source_generation_score_fail_count": source_score.get("fail_count"),
            "source_generation_score_partial_count": source_score.get("partial_count"),
            "manual_app_import_review_override_applied": review_gate["override"]["applied"],
            "packet_app_import_status": "app_import_candidate",
        },
        "app_mission": {
            "mission_id": app_mission["mission_id"],
            "mission_title": app_mission["mission_title"],
            "item_count": len(app_mission["items"]),
            "schema_version": app_mission["schema_version"],
        },
        "validation_commands": [
            "python3 scripts/validate_survey_evidence_export_v0_1.py --export data/alpha_packets/golden_alpha_packet_v0_1/inputs/survey_evidence_export.json",
            "python3 scripts/validate_mission_json.py data/alpha_packets/golden_alpha_packet_v0_1/app_import/app_mission_v0_2.json",
        ],
        "files": [
            {
                "path": rel(path),
                "sha256": sha256(path),
            }
            for path in files
        ],
    }


def run_validations() -> None:
    validation_dir = OUT_DIR / "validation"
    validation_dir.mkdir(parents=True, exist_ok=True)
    python = validation_python()

    run_checked(
        [
            str(python),
            "scripts/validate_survey_evidence_export_v0_1.py",
            "--export",
            rel(OUT_DIR / "inputs" / "survey_evidence_export.json"),
            "--report",
            rel(validation_dir / "survey_evidence_export_validation_report.md"),
        ],
    )
    mission_result = run_checked(
        [
            str(python),
            "scripts/validate_mission_json.py",
            rel(OUT_DIR / "app_import" / "app_mission_v0_2.json"),
        ],
    )
    write_validation_report(
        validation_dir / "app_mission_v0_2_validation_report.md",
        title="App Mission v0.2 Validation Report",
        target=OUT_DIR / "app_import" / "app_mission_v0_2.json",
        command=[str(python), "scripts/validate_mission_json.py", rel(OUT_DIR / "app_import" / "app_mission_v0_2.json")],
        result=mission_result,
    )


def validation_python() -> Path:
    venv_python = REPO_ROOT / ".venv" / "bin" / "python"
    if venv_python.exists():
        return venv_python
    return Path(sys.executable)


def run_checked(command: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(
            "Validation command failed:\n"
            + " ".join(command)
            + "\n\nSTDOUT:\n"
            + result.stdout
            + "\nSTDERR:\n"
            + result.stderr
        )
    return result


def write_validation_report(
    path: Path,
    *,
    title: str,
    target: Path,
    command: list[str],
    result: subprocess.CompletedProcess[str],
) -> None:
    body = [
        f"# {title}",
        "",
        f"- Target: `{rel(target)}`",
        "- Status: `passed`",
        "",
        "## Command",
        "",
        "```sh",
        " ".join(command),
        "```",
        "",
        "## Output",
        "",
        "```text",
        (result.stdout or "").strip(),
        "```",
        "",
    ]
    write_text(path, "\n".join(body))


def to_app_mission(generation: dict[str, Any]) -> dict[str, Any]:
    raw_items = generation["route"]["items"]
    items = [to_app_item(item, index) for index, item in enumerate(raw_items, start=1)]
    return without_none(
        {
            "schema_version": "mission.v0.2",
            "mission_id": app_id("MIS", f"{generation['mission_id']}_alpha_golden"),
            "mission_title": generation["title"],
            "mission_version": "v0.1",
            "created_at": GENERATED_AT,
            "mission_type": "album_test" if any(item["item_type"] == "album" for item in items) else "track_probe",
            "recommended_format": "play_items_in_order",
            "hypothesis": generation["hypothesis"],
            "inflation_warning": (
                "Golden Alpha generated mission. Treat route logic and all Atlas implications as provisional "
                "until reviewed after real listening evidence."
            ),
            "success_bar": {
                "minimum_items_to_resolve": min(3, len(items)),
                "minimum_items_to_play": min(3, len(items)),
                "minimum_reactions_required": min(3, len(items)),
                "requires_physical_iphone": True,
                "notes": "Golden Alpha app-import packet for Survey -> Supabase -> mission.v0.2 integration testing.",
            },
            "run_instructions": {
                "listen_in_order": True,
                "shuffle_allowed": False,
                "raw_text": generation["route"].get("route_summary"),
            },
            "post_run_inference_rules": [
                {
                    "trigger": "After the mission, review primary reactions, chips, notes, skips, and resolver state.",
                    "inference": "Create Signals and possible Atlas updates only through the Alpha review path.",
                }
            ],
            "items": items,
        }
    )


def to_app_item(item: dict[str, Any], sequence: int) -> dict[str, Any]:
    metadata = item["display_metadata"]
    search_hint = item.get("music_kit_search_hint", {})
    review_state = item.get("review_state", {})
    expected_test_signal = " ".join(
        part
        for part in [
            f"Positive: {item.get('expected_positive_signal', '')}".strip(),
            f"Negative: {item.get('expected_negative_signal', '')}".strip(),
        ]
        if part and not part.endswith(":")
    )
    notes = " ".join(
        part
        for part in [
            "Human review requested." if review_state.get("needs_human_review") else "",
            review_state.get("review_notes", ""),
        ]
        if part
    )
    return without_none(
        {
            "item_id": app_id("ITEM", item["item_id"]),
            "sequence": sequence,
            "item_type": "album" if item.get("item_type") == "album" else "track",
            "artist": metadata["artist"],
            "title": metadata["title"],
            "album": metadata.get("album") or None,
            "year": metadata.get("release_year"),
            "why_included": item.get("why_selected") or item.get("route_function"),
            "expected_test_signal": expected_test_signal,
            "player_card": {
                "flip_side": {
                    "song_hypothesis": item.get("item_hypothesis", ""),
                    "detail": item.get("route_function", ""),
                }
            },
            "feedback_chip_sets": {
                "hit": to_app_chips(item, "love"),
                "partial": to_app_chips(item, "like"),
                "ok_shelf": to_app_chips(item, "keep"),
                "miss": to_app_chips(item, "not_for_me"),
            },
            "apple_music_resolution": {
                "status": "unresolved",
                "reason": search_hint.get("search_query", "generated_alpha_requires_music_kit_resolution"),
                "resolver": "not_attempted",
            },
            "notes": notes or None,
        }
    )


def to_app_chips(item: dict[str, Any], operation: str) -> list[dict[str, Any]]:
    chips = item.get("feedback_chip_sets", {}).get(operation, [])
    return [
        without_none(
            {
                "tag_id": app_id("TAG", chip["chip_id"]),
                "label": chip["label"],
                "description": chip.get("signal_meaning") or chip.get("atlas_effect_hint"),
            }
        )
        for chip in chips
    ]


def app_id(prefix: str, value: Any) -> str:
    raw = str(value).upper()
    slug = re.sub(r"[^A-Z0-9]+", "_", raw).strip("_")
    if slug.startswith(f"{prefix}_"):
        return slug
    return f"{prefix}_{slug}"


def without_none(value: dict[str, Any]) -> dict[str, Any]:
    return {key: child for key, child in value.items() if child is not None}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def render_readme(manifest: dict[str, Any]) -> str:
    app_mission = manifest["app_mission"]
    status = manifest["status"]
    return f"""# Golden Alpha Packet v0.1

Generated: {manifest["generated_at"]}

This packet is the first reproducible integration spine for trusted Alpha:

```text
Survey Evidence Export
-> MissionGenerationDigestView
-> candidate pool
-> Supabase generate-first-mission-batch request
-> Cartenza mission output
-> reviewed app-import gate
-> mission.v0.2
```

## App Mission

- Mission ID: `{app_mission["mission_id"]}`
- Title: `{app_mission["mission_title"]}`
- Items: `{app_mission["item_count"]}`
- Schema: `{app_mission["schema_version"]}`

## Gate Status

- Source generation schema valid: `{status["source_generation_schema_valid"]}`
- Source generation readiness: `{status["source_generation_product_readiness"]}`
- Model declared app import ready: `{status["source_generation_model_declared_app_import_ready"]}`
- Score failures: `{status["source_generation_score_fail_count"]}`
- Score partials: `{status["source_generation_score_partial_count"]}`
- Manual app-import review override: `{status["manual_app_import_review_override_applied"]}`
- Packet app import status: `{status["packet_app_import_status"]}`

The manual override exists only to create a complete app-import integration packet from a schema-valid,
zero-failure source generation. It is not evidence that autonomous generation is ready for external testers.

## Key Files

- `inputs/survey_evidence_export.json`
- `inputs/mission_generation_digest_view.json`
- `inputs/candidate_pool.json`
- `request/supabase_generate_first_mission_batch_request.json`
- `generation/{RAW_MISSION_OUTPUT_FILENAME}`
- `generation/{REVIEWED_MISSION_OUTPUT_FILENAME}`
- `review/app_import_review_gate.json`
- `response/supabase_generate_first_mission_batch_response.json`
- `app_import/app_mission_v0_2.json`
- `app_import/app_mission_collection_v0_2.json`

## Validation

```sh
python3 scripts/validate_survey_evidence_export_v0_1.py --export data/alpha_packets/golden_alpha_packet_v0_1/inputs/survey_evidence_export.json
python3 scripts/validate_mission_json.py data/alpha_packets/golden_alpha_packet_v0_1/app_import/app_mission_v0_2.json
```
"""


if __name__ == "__main__":
    raise SystemExit(main())
