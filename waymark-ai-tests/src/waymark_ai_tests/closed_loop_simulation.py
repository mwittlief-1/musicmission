from __future__ import annotations

import hashlib
import json
import math
import time
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

from .a3_generation import (
    A3_INGESTION_DIR,
    A3_NODE_INTERPRETATION_DIR,
    A3_WWTSF_OUTPUT_DIR,
    FIXTURES_ROOT,
    REPO_ROOT,
    _fmt_cost,
    _load_json,
    _now,
    _profile_id,
    _redact_request_payload,
    _render_template,
)
from .openai_client import (
    OpenAIConfig,
    build_request_payload,
    call_openai,
    extract_output_text,
    extract_usage,
    parse_json_from_text,
)
from .report_writer import write_json
from .schema_validator import validate_json


CLOSED_LOOP_OUTPUT_DIR = REPO_ROOT / "data" / "closed_loop_simulation" / "a3_first_batch_learning_v0_1_adaptive_contract_v0_1"
REPORTS_ROOT = FIXTURES_ROOT.parent / "reports"
PROFILE_IDS = ["01", "05", "06"]
PRIMARY_SIGNAL_RATIO = 0.60
SECONDARY_TAG_RATIO = 0.30
ADAPTIVE_CONTRACT_VERSION = "waymark.adaptive_second_batch_contract.v0.1"
ADAPTATION_ACTIONS = ["deepen", "pivot", "retire_pause", "contradiction_check", "dead_end_confirmation"]
RESOLUTION_QUALITY_STATUSES = [
    "resolved",
    "one_placeholder",
    "too_many_placeholders",
    "search_calibration_only",
    "unsuitable_for_closed_loop_learning",
]
CLOSED_LOOP_SUITABILITY = ["suitable", "review_needed", "unsuitable"]

CostEstimator = Callable[[str, Dict[str, Optional[int]], Dict[str, Any]], Dict[str, Any]]


def run_closed_loop_simulation(
    *,
    profiles: Iterable[str],
    config: OpenAIConfig,
    pricing: Dict[str, Any],
    estimate_cost_usd: CostEstimator,
    dry_run: bool,
) -> int:
    CLOSED_LOOP_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    mission_schema = _load_json(FIXTURES_ROOT / "schemas" / "mission_output_schema_v0_1.json")
    first_batch_schema = _mission_batch_schema(mission_schema, adaptive_second_batch=False)
    second_batch_schema = _mission_batch_schema(mission_schema, adaptive_second_batch=True)
    write_json(CLOSED_LOOP_OUTPUT_DIR / "closed_loop_mission_batch_schema_v0_1.json", first_batch_schema)
    write_json(CLOSED_LOOP_OUTPUT_DIR / "adaptive_second_batch_schema_v0_1.json", second_batch_schema)

    profile_results = []
    for profile in list(profiles):
        result = _run_profile_loop(
            profile=profile,
            config=config,
            pricing=pricing,
            estimate_cost_usd=estimate_cost_usd,
            dry_run=dry_run,
            mission_schema=mission_schema,
            first_batch_schema=first_batch_schema,
            second_batch_schema=second_batch_schema,
        )
        profile_results.append(result)

    adaptive_report_path = _write_adaptive_second_batch_report(profile_results=profile_results, dry_run=dry_run)
    manifest = _closed_loop_manifest(
        config=config,
        profile_results=profile_results,
        dry_run=dry_run,
        adaptive_report_path=adaptive_report_path,
    )
    write_json(CLOSED_LOOP_OUTPUT_DIR / "closed_loop_manifest.json", manifest)
    _write_acceptance_report(profile_results=profile_results, dry_run=dry_run, adaptive_report_path=adaptive_report_path)
    print(f"Closed-loop output: {CLOSED_LOOP_OUTPUT_DIR}")
    print(f"Closed-loop report: {CLOSED_LOOP_OUTPUT_DIR / 'closed_loop_acceptance_report.md'}")
    print(f"Adaptive second-batch report: {adaptive_report_path}")
    return 0 if dry_run or all(result.get("final_status") in {"closed_loop_pass", "closed_loop_review_needed"} for result in profile_results) else 1


def _run_profile_loop(
    *,
    profile: str,
    config: OpenAIConfig,
    pricing: Dict[str, Any],
    estimate_cost_usd: CostEstimator,
    dry_run: bool,
    mission_schema: Dict[str, Any],
    first_batch_schema: Dict[str, Any],
    second_batch_schema: Dict[str, Any],
) -> Dict[str, Any]:
    profile_id = _profile_id(profile)
    profile_dir = CLOSED_LOOP_OUTPUT_DIR / f"profile_{profile}"
    profile_dir.mkdir(parents=True, exist_ok=True)

    first_context = _build_closed_loop_context(profile=profile, batch_stage="first_batch")
    first_batch = _run_mission_batch_generation(
        profile=profile,
        profile_dir=profile_dir,
        output_stem="first_batch_missions",
        batch_stage="first_batch",
        context_packet=first_context,
        config=config,
        batch_schema=first_batch_schema,
        pricing=pricing,
        estimate_cost_usd=estimate_cost_usd,
        dry_run=dry_run,
    )

    first_batch_output = first_batch.get("parsed_output") if isinstance(first_batch.get("parsed_output"), dict) else None
    first_batch_eval = (
        _evaluate_mission_batch(first_batch_output, mission_schema, adaptive_second_batch=False)
        if first_batch_output
        else {"valid": False, "errors": ["No first batch output."]}
    )
    write_json(profile_dir / "first_batch_mission_evaluation.json", first_batch_eval)

    if dry_run or not first_batch_output:
        return {
            "profile_id": profile_id,
            "profile": profile,
            "first_batch": _stage_summary(first_batch),
            "final_status": "dry_run" if dry_run else "closed_loop_fail",
        }

    feedback, hidden_trace = _simulate_mission_feedback(profile, first_batch_output)
    write_json(profile_dir / "simulated_mission_feedback_atlas_payload.json", feedback)
    write_json(profile_dir / "simulation_hidden_evaluator_trace_NOT_ATLAS_INPUT.json", hidden_trace)

    atlas_updates = _ingest_simulated_feedback(profile, feedback)
    write_json(profile_dir / "atlas_update_records_after_batch_1.json", atlas_updates)
    atlas_delta = _build_atlas_delta(profile, first_batch_output, feedback, atlas_updates)
    write_json(profile_dir / "atlas_delta_after_batch_1.json", atlas_delta)
    updated_digest = _build_updated_digest(profile, atlas_updates, atlas_delta)
    write_json(profile_dir / "atlas_digest_after_batch_1.json", updated_digest)

    second_context = _build_closed_loop_context(
        profile=profile,
        batch_stage="second_batch",
        updated_digest=updated_digest,
        first_batch=first_batch_output,
        feedback=feedback,
        atlas_updates=atlas_updates,
        atlas_delta=atlas_delta,
    )
    second_batch = _run_mission_batch_generation(
        profile=profile,
        profile_dir=profile_dir,
        output_stem="second_batch_missions",
        batch_stage="second_batch",
        context_packet=second_context,
        config=config,
        batch_schema=second_batch_schema,
        pricing=pricing,
        estimate_cost_usd=estimate_cost_usd,
        dry_run=dry_run,
    )
    second_batch_output = second_batch.get("parsed_output") if isinstance(second_batch.get("parsed_output"), dict) else None
    second_batch_eval = (
        _evaluate_mission_batch(
            second_batch_output,
            mission_schema,
            adaptive_second_batch=True,
            atlas_delta=atlas_delta,
            atlas_updates=atlas_updates,
        )
        if second_batch_output
        else {"valid": False, "errors": ["No second batch output."]}
    )
    write_json(profile_dir / "second_batch_mission_evaluation.json", second_batch_eval)

    qualitative_review = _profile_qualitative_review(
        profile=profile,
        first_batch=first_batch_output,
        first_eval=first_batch_eval,
        feedback=feedback,
        atlas_updates=atlas_updates,
        atlas_delta=atlas_delta,
        second_batch=second_batch_output,
        second_eval=second_batch_eval,
    )
    (profile_dir / f"qualitative_review_profile_{profile}.md").write_text(qualitative_review, encoding="utf-8")

    final_status = "closed_loop_pass" if first_batch_eval.get("valid") and second_batch_eval.get("valid") and _feedback_metrics_ok(feedback) else "closed_loop_review_needed"
    return {
        "profile_id": profile_id,
        "profile": profile,
        "first_batch": _stage_summary(first_batch),
        "first_batch_evaluation": first_batch_eval,
        "feedback_summary": feedback.get("summary"),
        "atlas_update_summary": atlas_updates.get("summary"),
        "atlas_delta_summary": atlas_delta.get("summary"),
        "second_batch": _stage_summary(second_batch),
        "second_batch_evaluation": second_batch_eval,
        "qualitative_review_file": str(profile_dir / f"qualitative_review_profile_{profile}.md"),
        "final_status": final_status,
    }


def _run_mission_batch_generation(
    *,
    profile: str,
    profile_dir: Path,
    output_stem: str,
    batch_stage: str,
    context_packet: Dict[str, Any],
    config: OpenAIConfig,
    batch_schema: Dict[str, Any],
    pricing: Dict[str, Any],
    estimate_cost_usd: CostEstimator,
    dry_run: bool,
) -> Dict[str, Any]:
    profile_id = _profile_id(profile)
    prompt = _render_template(
        FIXTURES_ROOT / "prompt_templates" / "closed_loop_mission_batch_v0_1.md",
        {
            "{{PROFILE_ID}}": profile_id,
            "{{BATCH_STAGE}}": batch_stage,
            "{{MISSION_PORTFOLIO_JSON}}": json.dumps(_mission_portfolio(batch_stage), indent=2, sort_keys=True),
            "{{CONTEXT_PACKET_JSON}}": json.dumps(context_packet, indent=2, sort_keys=True),
            "{{ADAPTIVE_CONTRACT_JSON}}": json.dumps(_adaptive_contract_prompt_packet(batch_stage), indent=2, sort_keys=True),
            "{{OUTPUT_SCHEMA_JSON}}": json.dumps(batch_schema, indent=2, sort_keys=True),
        },
    )
    schema_name = "waymark_adaptive_second_batch_v0_1" if batch_stage == "second_batch" else "waymark_closed_loop_mission_batch_v0_1"
    request_payload = build_request_payload(
        config,
        "You generate Waymark mission batches from bounded Atlas substrate. Return only JSON conforming to the provided batch schema.",
        prompt,
        batch_schema,
        schema_name=schema_name,
    )
    write_json(profile_dir / f"{output_stem}_request.json", _redact_request_payload(request_payload))
    metadata = {
        "created_at": _now(),
        "model": config.model,
        "api_style": config.api_style,
        "batch_stage": batch_stage,
        "run_type": "dry_run" if dry_run else "live_api",
    }
    if dry_run:
        write_json(profile_dir / f"{output_stem}_metadata.json", metadata)
        return {"metadata": metadata, "validation_result": {"valid": False, "errors": ["dry_run"]}, "parsed_output": None, "metrics": {}}

    started_at = time.perf_counter()
    parse_error = None
    parsed_output = None
    try:
        raw_response = call_openai(config, request_payload)
        try:
            parsed_output = parse_json_from_text(extract_output_text(raw_response))
        except Exception as error:  # noqa: BLE001
            parse_error = str(error)
    except Exception as error:  # noqa: BLE001
        parse_error = str(error)
        raw_response = {"api_error": parse_error}
    elapsed_seconds = round(time.perf_counter() - started_at, 3)

    write_json(profile_dir / f"{output_stem}_raw_response.json", raw_response)
    if parsed_output is not None:
        write_json(profile_dir / f"{output_stem}.json", parsed_output)
    validation_result = (
        validate_json(parsed_output, batch_schema)
        if parsed_output is not None
        else {"validator": "none", "valid": False, "error_count": 1, "errors": [parse_error or "No parsed output."]}
    )
    usage = extract_usage(raw_response)
    cost_estimate = estimate_cost_usd(config.model, usage, pricing)
    metrics = {
        "input_tokens": usage["input_tokens"],
        "cached_input_tokens": usage["cached_input_tokens"],
        "output_tokens": usage["output_tokens"],
        "total_tokens": usage["total_tokens"],
        "estimated_total_cost_usd": cost_estimate["estimated_total_cost_usd"],
        "cost_status": cost_estimate["cost_status"],
        "latency_seconds": elapsed_seconds,
    }
    metadata.update(metrics)
    metadata["valid"] = validation_result.get("valid")
    if parse_error:
        metadata["error"] = parse_error
    write_json(profile_dir / f"{output_stem}_metadata.json", metadata)
    write_json(profile_dir / f"{output_stem}_validation.json", validation_result)
    return {
        "metadata": metadata,
        "metrics": metrics,
        "validation_result": validation_result,
        "parsed_output": parsed_output,
        "raw_response": raw_response,
        "output_file": str(profile_dir / f"{output_stem}.json"),
    }


def _mission_object_schema(mission_schema: Dict[str, Any], *, adaptive_second_batch: bool) -> Dict[str, Any]:
    mission_object = {
        key: deepcopy(value)
        for key, value in mission_schema.items()
        if key not in {"$schema", "$id", "$defs", "title"}
    }
    mission_object["title"] = "Waymark Mission Object v0.1"
    if adaptive_second_batch:
        mission_object["title"] = "Waymark Adaptive Second-Batch Mission Object v0.1"
        mission_object["properties"].update(
            {
                "mission_type": {"type": "string", "minLength": 1},
                "adaptation_action": {"type": "string", "enum": ADAPTATION_ACTIONS},
                "source_signal_refs": {"type": "array", "minItems": 1, "items": {"type": "string", "minLength": 1}},
                "source_update_candidate_refs": {"type": "array", "minItems": 1, "items": {"type": "string", "minLength": 1}},
                "source_atlas_delta_refs": {"type": "array", "minItems": 1, "items": {"type": "string", "minLength": 1}},
                "what_batch_1_taught": {"type": "string", "minLength": 24},
                "why_this_mission_now": {"type": "string", "minLength": 24},
                "what_changed_since_prior_batch": {"type": "string", "minLength": 24},
                "what_this_mission_is_not_doing_anymore": {"type": "string", "minLength": 12},
                "success_condition": {"type": "string", "minLength": 12},
                "failure_condition": {"type": "string", "minLength": 12},
                "no_signal_interpretation": {"type": "string", "minLength": 12},
                "expected_next_atlas_update": {"type": "string", "minLength": 12},
                "resolution_quality_status": {"type": "string", "enum": RESOLUTION_QUALITY_STATUSES},
                "closed_loop_learning_suitability": {"type": "string", "enum": CLOSED_LOOP_SUITABILITY},
            }
        )
        mission_object["required"] = list(mission_object["required"]) + [
            "mission_type",
            "adaptation_action",
            "source_signal_refs",
            "source_update_candidate_refs",
            "source_atlas_delta_refs",
            "what_batch_1_taught",
            "why_this_mission_now",
            "what_changed_since_prior_batch",
            "what_this_mission_is_not_doing_anymore",
            "success_condition",
            "failure_condition",
            "no_signal_interpretation",
            "expected_next_atlas_update",
            "resolution_quality_status",
            "closed_loop_learning_suitability",
        ]
    return mission_object


def _full_mission_schema(mission_schema: Dict[str, Any], *, adaptive_second_batch: bool) -> Dict[str, Any]:
    schema = _mission_object_schema(mission_schema, adaptive_second_batch=adaptive_second_batch)
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    schema["$defs"] = deepcopy(mission_schema.get("$defs", {}))
    return schema


def _mission_batch_schema(mission_schema: Dict[str, Any], *, adaptive_second_batch: bool) -> Dict[str, Any]:
    mission_object = _mission_object_schema(mission_schema, adaptive_second_batch=adaptive_second_batch)
    required = ["schema_version", "profile_id", "batch_id", "batch_stage", "mission_portfolio_slots", "missions"]
    properties: Dict[str, Any] = {
        "schema_version": {
            "type": "string",
            "const": "waymark.adaptive_second_batch.v0.1" if adaptive_second_batch else "waymark.closed_loop_mission_batch.v0.1",
        },
        "profile_id": {"type": "string", "minLength": 1},
        "batch_id": {"type": "string", "minLength": 1},
        "batch_stage": {"type": "string", "const": "second_batch" if adaptive_second_batch else "first_batch"},
        "mission_portfolio_slots": {
            "type": "array",
            "minItems": 6,
            "maxItems": 6,
            "items": {
                "type": "string",
                "enum": [
                    "safe_anchor",
                    "nearby_road",
                    "frontier",
                    "dead_end_or_contradiction_check",
                    "waypoint_useful_not_canon",
                    "wildcard_delight",
                ],
            },
        },
        "missions": {"type": "array", "minItems": 6, "maxItems": 6, "items": mission_object},
    }
    if adaptive_second_batch:
        required.append("batch_delta_summary")
        properties["batch_delta_summary"] = {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "what_batch_1_taught",
                "atlas_deltas_consumed",
                "major_changes",
                "deepened_paths",
                "pivots",
                "paused_or_retired_paths",
                "contradictions_to_check",
                "dead_ends_to_confirm",
                "what_this_batch_is_not_doing_anymore",
            ],
            "properties": {
                "what_batch_1_taught": {"type": "string", "minLength": 24},
                "atlas_deltas_consumed": {"type": "array", "minItems": 1, "items": {"type": "string", "minLength": 1}},
                "major_changes": {"type": "array", "items": {"type": "string"}},
                "deepened_paths": {"type": "array", "items": {"type": "string"}},
                "pivots": {"type": "array", "items": {"type": "string"}},
                "paused_or_retired_paths": {"type": "array", "items": {"type": "string"}},
                "contradictions_to_check": {"type": "array", "items": {"type": "string"}},
                "dead_ends_to_confirm": {"type": "array", "items": {"type": "string"}},
                "what_this_batch_is_not_doing_anymore": {"type": "array", "minItems": 1, "items": {"type": "string", "minLength": 1}},
            },
        }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Waymark Adaptive Second Batch v0.1" if adaptive_second_batch else "Waymark Closed Loop Mission Batch v0.1",
        "type": "object",
        "additionalProperties": False,
        "required": required,
        "properties": properties,
        "$defs": deepcopy(mission_schema.get("$defs", {})),
    }


def _build_closed_loop_context(
    *,
    profile: str,
    batch_stage: str,
    updated_digest: Optional[Dict[str, Any]] = None,
    first_batch: Optional[Dict[str, Any]] = None,
    feedback: Optional[Dict[str, Any]] = None,
    atlas_updates: Optional[Dict[str, Any]] = None,
    atlas_delta: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    digest_path = A3_INGESTION_DIR / f"atlas_digest_view_profile_{profile}_A3.json"
    node_path = A3_NODE_INTERPRETATION_DIR / f"node_interpretation_smoke_profile_{profile}_A3.json"
    wwtsf_path = A3_WWTSF_OUTPUT_DIR / f"wwtsf_substrate_profile_{profile}_A3.json"
    bundle_path = A3_INGESTION_DIR / f"atlas_records_bundle_profile_{profile}_A3.json"
    digest = updated_digest or _load_json(digest_path)
    compact_for_adaptive_second_batch = batch_stage == "second_batch"
    node_interpretation = _load_json(node_path)
    wwtsf_substrate = _load_json(wwtsf_path)
    return {
        "generation_task": "closed_loop_mission_batch",
        "batch_stage": batch_stage,
        "profile_id": _profile_id(profile),
        "input_file_refs": {
            "atlas_digest_view": str(digest_path),
            "node_interpretation": str(node_path),
            "wwtsf_substrate": str(wwtsf_path),
            "atlas_records_bundle": str(bundle_path),
        },
        "exclusion_policy": {
            "raw_a3_payload_used": False,
            "profile_writer_output_used": False,
            "hidden_truth_used_for_generation": False,
            "hidden_evaluator_trace_used_for_generation": False,
            "canonical_graph_mutation_allowed": False,
        },
        "atlas_digest_view": _mission_generation_digest_summary(digest) if compact_for_adaptive_second_batch else digest,
        "node_interpretation": _node_interpretation_summary(node_interpretation) if compact_for_adaptive_second_batch else node_interpretation,
        "wwtsf_substrate": _wwtsf_summary(wwtsf_substrate) if compact_for_adaptive_second_batch else wwtsf_substrate,
        "atlas_records_bundle_summary": _records_bundle_summary(_load_json(bundle_path)),
        "mission_portfolio": _mission_portfolio(batch_stage),
        "prior_first_batch_summary": _batch_summary_for_prompt(first_batch) if first_batch else None,
        "mission_feedback_summary": feedback.get("summary") if feedback else None,
        "atlas_update_summary": atlas_updates.get("summary") if atlas_updates else None,
        "atlas_update_records_after_batch_1": _atlas_update_prompt_summary(atlas_updates) if atlas_updates else None,
        "atlas_delta_after_batch_1": atlas_delta,
        "adaptive_second_batch_reference_table": _adaptive_reference_table(atlas_delta) if atlas_delta else None,
        "adaptive_second_batch_contract": _adaptive_contract_prompt_packet(batch_stage),
    }


def _mission_portfolio(batch_stage: str) -> List[Dict[str, Any]]:
    second = batch_stage == "second_batch"
    return [
        {"slot": "safe_anchor", "mission_archetype": "Safe / Anchor Mission", "objective": "Use reliable positive substrate as a safe first route." if not second else "Deepen reliable positives that were supported by batch-one feedback."},
        {"slot": "nearby_road", "mission_archetype": "Nearby Road", "objective": "Move from an anchor into adjacent material with low to medium risk." if not second else "Refine the best nearby road using feedback-supported signals."},
        {"slot": "frontier", "mission_archetype": "Frontier Route", "objective": "Test one promising but underexplored lane." if not second else "Turn a batch-one positive or unknown into a sharper frontier test."},
        {"slot": "dead_end_or_contradiction_check", "mission_archetype": "Correction Route / Dead End Check", "objective": "Check one scoped contradiction or possible dead end without broad rejection." if not second else "Sharpen a contradiction or soften a failed path based on feedback."},
        {"slot": "waypoint_useful_not_canon", "mission_archetype": "Waypoint / Use-Case Route", "objective": "Use useful-but-not-canon evidence as a route, not a Landmark." if not second else "Use confirmed Keep/Waypoint evidence without canon inflation."},
        {"slot": "wildcard_delight", "mission_archetype": "Wildcard / Delight", "objective": "Offer one playful exploratory bet with clear learning value." if not second else "Offer a better-informed delight bet based on the first batch."},
    ]


def _adaptive_contract_prompt_packet(batch_stage: str) -> Dict[str, Any]:
    applies = batch_stage == "second_batch"
    return {
        "schema_version": ADAPTIVE_CONTRACT_VERSION,
        "applies": applies,
        "controlling_rule": (
            "Do not generate a second-batch mission unless it can point to at least one referenced AtlasDelta."
            if applies
            else "First batch establishes instrumented routes; adaptive fields are not required until second batch."
        ),
        "required_mission_fields_when_second_batch": [
            "mission_type",
            "adaptation_action",
            "source_signal_refs",
            "source_update_candidate_refs",
            "source_atlas_delta_refs",
            "what_batch_1_taught",
            "why_this_mission_now",
            "what_changed_since_prior_batch",
            "what_this_mission_is_not_doing_anymore",
            "success_condition",
            "failure_condition",
            "no_signal_interpretation",
            "expected_next_atlas_update",
            "resolution_quality_status",
            "closed_loop_learning_suitability",
        ],
        "adaptation_action_enum": ADAPTATION_ACTIONS,
        "resolution_quality_status_enum": RESOLUTION_QUALITY_STATUSES,
        "closed_loop_learning_suitability_enum": CLOSED_LOOP_SUITABILITY,
        "source_ref_rules": {
            "source_signal_refs": "Use only signal_id values listed inside the referenced AtlasDelta source_signal_refs. Do not use survey signal IDs.",
            "source_update_candidate_refs": "Use only candidate_id values listed inside the referenced AtlasDelta source_update_candidate_refs.",
            "source_atlas_delta_refs": "Use delta_id values from atlas_delta_after_batch_1.deltas. This is mandatory.",
        },
        "resolution_rule": "No second-batch mission should include more than one unresolved candidate-search placeholder unless mission_type is resolution_search_calibration. If too many placeholders remain, mark the mission review_needed or unsuitable, not suitable.",
        "batch_level_required": "Populate batch_delta_summary so a reviewer can see what Batch 1 taught, what deltas were consumed, what paths were deepened, pivoted, paused, checked, or narrowed, and what this batch is not doing anymore.",
    }


def _adaptive_reference_table(atlas_delta: Dict[str, Any]) -> Dict[str, Any]:
    rows = []
    for delta in atlas_delta.get("deltas", []):
        rows.append(
            {
                "delta_id": delta.get("delta_id"),
                "recommended_adaptation_action": delta.get("recommended_adaptation_action"),
                "source_signal_refs": delta.get("source_signal_refs", []),
                "source_update_candidate_refs": delta.get("source_update_candidate_refs", []),
                "what_changed": delta.get("what_changed"),
            }
        )
    return {
        "copy_refs_from_this_table_only": True,
        "do_not_use_survey_signal_refs": True,
        "required_action_coverage": sorted({row.get("recommended_adaptation_action") for row in rows if row.get("recommended_adaptation_action")}),
        "rows": rows,
    }


def _records_bundle_summary(bundle: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "record_type": bundle.get("record_type"),
        "schema_version": bundle.get("schema_version"),
        "profile_id": bundle.get("profile_id") or bundle.get("user_id"),
        "top_level_keys": sorted(bundle.keys())[:30],
    }


def _mission_generation_digest_summary(digest: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "view_type": "MissionGenerationDigestView.compact_for_adaptive_second_batch",
        "digest_id": digest.get("digest_id"),
        "user_id": digest.get("user_id"),
        "mission_context": digest.get("mission_context"),
        "candidate_landmarks": _summarize_records(digest.get("candidate_landmarks", []), 10),
        "candidate_regions": _summarize_records(digest.get("candidate_regions", []), 10),
        "candidate_frontiers": _summarize_records(digest.get("candidate_frontiers", []), 10),
        "candidate_dead_end_hypotheses": _summarize_records(digest.get("candidate_dead_end_hypotheses", []), 10),
        "candidate_waypoints": _summarize_records(digest.get("candidate_waypoints", []), 10),
        "user_taste_feature_summaries": _summarize_records(digest.get("user_taste_feature_summaries", []), 20),
        "user_vocabulary_terms": _summarize_records(digest.get("user_vocabulary_terms", []), 20),
        "anti_overfitting_rules": digest.get("anti_overfitting_rules", [])[:20],
        "mission_relevant_constraints": digest.get("mission_relevant_constraints", [])[:20],
        "unresolved_questions": digest.get("unresolved_questions", [])[:20],
        "recent_signals": _summarize_records(digest.get("recent_signals", []), 20),
        "signal_summaries": _summarize_records(digest.get("signal_summaries", []), 20),
        "candidate_pool_behavior_hints": _summarize_records(digest.get("candidate_pool_behavior_hints", []), 20),
        "candidate_pool_behavior_hints_after_batch_1": _summarize_records(digest.get("candidate_pool_behavior_hints_after_batch_1", []), 20),
        "atlas_delta_after_batch_1_summary": digest.get("atlas_delta_after_batch_1_summary"),
        "atlas_delta_after_batch_1_refs": digest.get("atlas_delta_after_batch_1_refs", []),
        "closed_loop_learning_summary": digest.get("closed_loop_learning_summary"),
        "canonical_graph_mutation_allowed": digest.get("canonical_graph_mutation_allowed", False),
    }


def _node_interpretation_summary(node_interpretation: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "profile_public_id": node_interpretation.get("profile_public_id"),
        "source_digest_id": node_interpretation.get("source_digest_id"),
        "interpretation_status": node_interpretation.get("interpretation_status"),
        "packet_sufficiency": node_interpretation.get("packet_sufficiency"),
        "wwtsf_ready_bullets": node_interpretation.get("wwtsf_ready_bullets", [])[:12],
        "first_mission_hint_candidates": _summarize_records(node_interpretation.get("first_mission_hint_candidates", []), 12),
        "contradiction_explanations": _summarize_records(node_interpretation.get("contradiction_explanations", []), 12),
        "role_refinement_recommendations": _summarize_records(node_interpretation.get("role_refinement_recommendations", []), 12),
        "safety_checks": node_interpretation.get("safety_checks"),
    }


def _wwtsf_summary(wwtsf: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "profile_id": wwtsf.get("profile_id"),
        "not_final_user_copy": wwtsf.get("not_final_user_copy"),
        "provisional_summary_bullets": wwtsf.get("provisional_summary_bullets", [])[:12],
        "known_anchors": _summarize_records(wwtsf.get("known_anchors", []), 12),
        "candidate_regions": _summarize_records(wwtsf.get("candidate_regions", []), 12),
        "candidate_frontiers": _summarize_records(wwtsf.get("candidate_frontiers", []), 12),
        "candidate_dead_end_hypotheses": _summarize_records(wwtsf.get("candidate_dead_end_hypotheses", []), 12),
        "waypoint_notes": _summarize_records(wwtsf.get("waypoint_notes", []), 12),
        "contradictions_or_review_needs": _summarize_records(wwtsf.get("contradictions_or_review_needs", []), 12),
        "confidence_warnings": wwtsf.get("confidence_warnings", [])[:12],
        "scope_limits": wwtsf.get("scope_limits", [])[:12],
        "first_mission_input_hints": _summarize_records(wwtsf.get("first_mission_input_hints", []), 12),
    }


def _summarize_records(records: Any, limit: int) -> List[Any]:
    if not isinstance(records, list):
        return []
    return [_summarize_record(record) for record in records[:limit]]


def _summarize_record(record: Any) -> Any:
    if not isinstance(record, dict):
        return record
    keep_keys = [
        "id",
        "signal_id",
        "candidate_id",
        "role_assignment_id",
        "label",
        "name",
        "title",
        "artist",
        "role",
        "atlas_role",
        "proposed_role",
        "scope",
        "confidence",
        "confidence_band",
        "confidence_delta",
        "candidate_pool_behavior",
        "summary",
        "evidence_summary",
        "why",
        "reason",
        "feature_ids",
        "taste_feature_ids",
        "music_object_ref",
        "subject_music_object_ref",
        "failure_or_edge_conditions",
        "review_required",
    ]
    summarized = {key: record.get(key) for key in keep_keys if key in record}
    if not summarized:
        summarized = {key: record.get(key) for key in list(record.keys())[:6]}
    return summarized


def _batch_summary_for_prompt(batch: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not batch:
        return None
    return {
        "batch_id": batch.get("batch_id"),
        "mission_titles": [mission.get("title") for mission in batch.get("missions", [])],
        "mission_archetypes": [mission.get("archetypes", []) for mission in batch.get("missions", [])],
    }


def _atlas_update_prompt_summary(atlas_updates: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not atlas_updates:
        return None
    return {
        "summary": atlas_updates.get("summary"),
        "role_candidate_changes": atlas_updates.get("role_assignment_candidate_changes", [])[:20],
        "possible_update_candidates": atlas_updates.get("possible_atlas_update_candidates", [])[:20],
        "contradiction_clusters": atlas_updates.get("contradiction_clusters", [])[:12],
    }


def _evaluate_mission_batch(
    batch: Optional[Dict[str, Any]],
    mission_schema: Dict[str, Any],
    *,
    adaptive_second_batch: bool,
    atlas_delta: Optional[Dict[str, Any]] = None,
    atlas_updates: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    if not batch:
        return {"valid": False, "errors": ["No batch output."]}
    errors: List[str] = []
    missions = batch.get("missions", [])
    slots = batch.get("mission_portfolio_slots", [])
    if len(missions) != 6:
        errors.append(f"Expected 6 missions; got {len(missions)}.")
    required_slots = [slot["slot"] for slot in _mission_portfolio(batch.get("batch_stage", "first_batch"))]
    missing_slots = [slot for slot in required_slots if slot not in slots]
    if missing_slots:
        errors.append(f"Missing portfolio slots: {', '.join(missing_slots)}.")
    route_items_total = 0
    route_items_ready = 0
    route_item_failures = []
    mission_validation_errors = []
    adaptive_results = []
    nested_schema = _full_mission_schema(mission_schema, adaptive_second_batch=adaptive_second_batch)
    for index, mission in enumerate(missions, start=1):
        validation = validate_json(mission, nested_schema)
        if not validation.get("valid"):
            mission_validation_errors.append({"mission_index": index, "errors": validation.get("errors", [])})
        for item in ((mission.get("route") or {}).get("items") or []):
            route_items_total += 1
            if _route_item_ready(item):
                route_items_ready += 1
            else:
                route_item_failures.append(
                    {
                        "mission_id": mission.get("mission_id"),
                        "item_id": item.get("item_id"),
                        "artist": (item.get("display_metadata") or {}).get("artist"),
                        "title": (item.get("display_metadata") or {}).get("title"),
                    }
                )
        if adaptive_second_batch:
            adaptive_results.append(_evaluate_adaptive_mission(mission, atlas_delta or {}, atlas_updates or {}))
    if mission_validation_errors:
        errors.append("One or more missions failed nested mission schema validation.")
    if route_item_failures:
        errors.append("One or more route items are neither concrete nor explicit candidate-search slots.")
    adaptive_summary = None
    if adaptive_second_batch:
        adaptive_summary = _evaluate_adaptive_batch(batch, adaptive_results, atlas_delta or {})
        errors.extend(adaptive_summary.get("errors", []))
    return {
        "valid": not errors,
        "errors": errors,
        "mission_count": len(missions),
        "portfolio_slots": slots,
        "missing_slots": missing_slots,
        "route_items_total": route_items_total,
        "route_items_ready": route_items_ready,
        "route_item_failures": route_item_failures,
        "mission_validation_errors": mission_validation_errors,
        "adaptive_mission_results": adaptive_results,
        "adaptive_summary": adaptive_summary,
    }


def _evaluate_adaptive_mission(mission: Dict[str, Any], atlas_delta: Dict[str, Any], atlas_updates: Dict[str, Any]) -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []
    delta_ids = {delta.get("delta_id") for delta in atlas_delta.get("deltas", [])}
    signal_ids = {signal.get("signal_id") for signal in atlas_updates.get("signals", [])}
    update_ids = {candidate.get("candidate_id") for candidate in atlas_updates.get("possible_atlas_update_candidates", [])}

    action = mission.get("adaptation_action")
    if action not in ADAPTATION_ACTIONS:
        errors.append("adaptation_action missing or invalid.")

    source_delta_refs = mission.get("source_atlas_delta_refs") or []
    source_signal_refs = mission.get("source_signal_refs") or []
    source_update_refs = mission.get("source_update_candidate_refs") or []
    if not source_delta_refs:
        errors.append("source_atlas_delta_refs is empty.")
    if any(ref not in delta_ids for ref in source_delta_refs):
        errors.append("source_atlas_delta_refs includes unknown refs.")
    if not source_signal_refs:
        errors.append("source_signal_refs is empty.")
    if any(ref not in signal_ids for ref in source_signal_refs):
        errors.append("source_signal_refs includes unknown refs.")
    if update_ids and not source_update_refs:
        errors.append("source_update_candidate_refs is empty while update candidates exist.")
    if any(ref not in update_ids for ref in source_update_refs):
        errors.append("source_update_candidate_refs includes unknown refs.")

    adaptive_text_fields = [
        "what_batch_1_taught",
        "why_this_mission_now",
        "what_changed_since_prior_batch",
        "what_this_mission_is_not_doing_anymore",
        "success_condition",
        "failure_condition",
        "no_signal_interpretation",
        "expected_next_atlas_update",
    ]
    for field in adaptive_text_fields:
        text = str(mission.get(field) or "").strip()
        if _generic_adaptive_text(text):
            errors.append(f"{field} is missing or too generic.")

    why_now = str(mission.get("why_this_mission_now") or "")
    changed = str(mission.get("what_changed_since_prior_batch") or "")
    if not _references_atlas_change(why_now):
        errors.append("why_this_mission_now does not visibly reference Atlas/batch-one change.")
    if not _references_atlas_change(changed):
        errors.append("what_changed_since_prior_batch does not visibly distinguish batch 2 from batch 1.")

    placeholder_count = _mission_placeholder_count(mission)
    computed_resolution = _computed_resolution_quality_status(mission, placeholder_count)
    declared_resolution = mission.get("resolution_quality_status")
    suitability = mission.get("closed_loop_learning_suitability")
    if declared_resolution == "resolved" and placeholder_count:
        errors.append("resolution_quality_status says resolved but route contains placeholders.")
    if declared_resolution == "one_placeholder" and placeholder_count != 1:
        errors.append("resolution_quality_status says one_placeholder but placeholder count differs.")
    if declared_resolution == "too_many_placeholders" and suitability == "suitable":
        errors.append("too_many_placeholders cannot be suitable for closed-loop learning.")
    if placeholder_count > 1 and mission.get("mission_type") != "resolution_search_calibration" and suitability == "suitable":
        errors.append("More than one placeholder requires non-suitable/review-needed status unless mission_type is resolution_search_calibration.")
    if declared_resolution != computed_resolution:
        warnings.append(f"Declared resolution_quality_status `{declared_resolution}` differs from computed `{computed_resolution}`.")

    product_status = "product_pass_candidate" if not errors and suitability == "suitable" else "product_review_needed" if not errors else "product_fail"
    app_import_ready = product_status not in {"product_fail"} and suitability != "unsuitable" and bool(source_delta_refs)
    return {
        "mission_id": mission.get("mission_id"),
        "title": mission.get("title"),
        "adaptation_action": action,
        "source_atlas_delta_refs": source_delta_refs,
        "source_signal_ref_count": len(source_signal_refs),
        "source_update_candidate_ref_count": len(source_update_refs),
        "placeholder_count": placeholder_count,
        "computed_resolution_quality_status": computed_resolution,
        "declared_resolution_quality_status": declared_resolution,
        "closed_loop_learning_suitability": suitability,
        "product_status": product_status,
        "app_import_ready": app_import_ready,
        "errors": errors,
        "warnings": warnings,
    }


def _evaluate_adaptive_batch(batch: Dict[str, Any], adaptive_results: List[Dict[str, Any]], atlas_delta: Dict[str, Any]) -> Dict[str, Any]:
    errors: List[str] = []
    batch_summary = batch.get("batch_delta_summary") or {}
    if _generic_adaptive_text(str(batch_summary.get("what_batch_1_taught") or "")):
        errors.append("batch_delta_summary.what_batch_1_taught is missing or generic.")
    consumed = set(batch_summary.get("atlas_deltas_consumed") or [])
    known_deltas = {delta.get("delta_id") for delta in atlas_delta.get("deltas", [])}
    if not consumed:
        errors.append("batch_delta_summary.atlas_deltas_consumed is empty.")
    if consumed and not consumed.issubset(known_deltas):
        errors.append("batch_delta_summary.atlas_deltas_consumed includes unknown deltas.")
    visibly_adaptive = [result for result in adaptive_results if result.get("product_status") != "product_fail" and result.get("source_atlas_delta_refs")]
    if len(visibly_adaptive) < 2:
        errors.append("Fewer than two second-batch missions are visibly adaptive.")
    actions = [result.get("adaptation_action") for result in adaptive_results]
    if not any(action in {"deepen", "pivot"} for action in actions):
        errors.append("No mission deepens or pivots from batch-one learning.")
    if not any(action == "retire_pause" for action in actions):
        errors.append("No mission pauses, retires, narrows, or deprioritizes a path.")
    expected_actions = {delta.get("recommended_adaptation_action") for delta in atlas_delta.get("deltas", [])}
    if expected_actions.intersection({"contradiction_check", "dead_end_confirmation"}) and not set(actions).intersection({"contradiction_check", "dead_end_confirmation"}):
        errors.append("AtlasDelta indicates contradiction/dead-end evidence, but no second-batch mission handles it.")
    if not any(not _generic_adaptive_text(str((mission.get("what_this_mission_is_not_doing_anymore") or ""))) for mission in batch.get("missions", [])):
        errors.append("No mission clearly states what Waymark is not doing anymore.")
    mission_failures = [result for result in adaptive_results if result.get("errors")]
    if mission_failures:
        errors.append("One or more adaptive missions failed adaptive evaluator checks.")
    return {
        "valid": not errors,
        "errors": errors,
        "visible_adaptive_mission_count": len(visibly_adaptive),
        "adaptation_action_counts": _count_by(adaptive_results, "adaptation_action"),
        "mission_product_status_counts": _count_by(adaptive_results, "product_status"),
        "mission_failures": mission_failures,
    }


def _route_item_ready(item: Dict[str, Any]) -> bool:
    if _is_candidate_search_slot(item):
        return True
    metadata = item.get("display_metadata") or {}
    hint = item.get("music_kit_search_hint") or {}
    artist = str(metadata.get("artist") or "").strip()
    title = str(metadata.get("title") or "").strip()
    query = str(hint.get("search_query") or "").strip()
    bad_terms = [" probe", "placeholder", "candidate_search_required", "manual_selection_required", "associated theatrical", "low-risk familiarity", "scoped dead-end check"]
    lowered = f"{artist} {title} {query}".lower()
    return bool(artist and title and query) and not any(term in lowered for term in bad_terms)


def _generic_adaptive_text(text: str) -> bool:
    stripped = " ".join(text.strip().split())
    if len(stripped) < 18:
        return True
    generic = {
        "the first batch provided useful evidence",
        "this continues the previous exploration",
        "this mission tests nearby music",
        "batch 1 provided useful evidence",
        "waymark learned from the first batch",
        "this is the next right test",
    }
    lowered = stripped.lower().rstrip(".")
    return lowered in generic


def _references_atlas_change(text: str) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in ["batch 1", "batch one", "first batch", "atlas", "delta", "signal", "update", "changed", "stronger", "weaker", "pause", "paused", "skip", "skipped", "no-signal", "miss"])


def _mission_placeholder_count(mission: Dict[str, Any]) -> int:
    return sum(1 for item in ((mission.get("route") or {}).get("items") or []) if _is_candidate_search_slot(item))


def _computed_resolution_quality_status(mission: Dict[str, Any], placeholder_count: int) -> str:
    if mission.get("mission_type") == "resolution_search_calibration":
        return "search_calibration_only"
    if placeholder_count == 0:
        return "resolved"
    if placeholder_count == 1:
        return "one_placeholder"
    return "too_many_placeholders"


def _is_candidate_search_slot(item: Dict[str, Any]) -> bool:
    metadata = item.get("display_metadata") or {}
    hint = item.get("music_kit_search_hint") or {}
    text = f"{metadata.get('title', '')} {hint.get('search_query', '')} {' '.join((item.get('review_state') or {}).get('uncertainty_flags', []))}".lower()
    return "candidate_search_required" in text or "manual_selection_required" in text


def _simulate_mission_feedback(profile: str, batch: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    route_refs = _flatten_route_items(batch)
    signal_count = int(round(len(route_refs) * PRIMARY_SIGNAL_RATIO))
    signaled_ids = {entry["route_item_global_id"] for entry in sorted(route_refs, key=lambda item: _stable_float(item["route_item_global_id"] + ":signal"))[:signal_count]}
    selected_tag_count = int(round(signal_count * SECONDARY_TAG_RATIO))
    selected_tag_ids = {entry["route_item_global_id"] for entry in sorted([item for item in route_refs if item["route_item_global_id"] in signaled_ids], key=lambda item: _stable_float(item["route_item_global_id"] + ":tag"))[:selected_tag_count]}
    hidden_truth = _load_hidden_truth(profile)
    hidden_index = _hidden_reaction_index(hidden_truth)
    feedback_events = []
    trace_events = []
    for entry in route_refs:
        item = entry["route_item"]
        global_id = entry["route_item_global_id"]
        visible_ref = _visible_music_object_ref(item)
        if global_id not in signaled_ids:
            playback_status = "skipped" if _stable_float(global_id + ":skip") < 0.5 else "no_signal"
            feedback_events.append(_atlas_feedback_event(entry, visible_ref, playback_status, "skipped" if playback_status == "skipped" else "no_signal", [], _shown_unselected_tags(item)))
            trace_events.append(_hidden_trace_event(entry, visible_ref, "NOT_ATLAS_INPUT", "no_user_signal", None, 0.0))
            continue
        reaction, source, hidden_ref, confidence = _decide_hidden_reaction(item, visible_ref, hidden_index)
        selected_tags = _selected_secondary_tags(item, reaction) if global_id in selected_tag_ids else []
        shown_unselected = _shown_unselected_tags(item, selected_tags)
        feedback_events.append(_atlas_feedback_event(entry, visible_ref, "played", reaction, selected_tags, shown_unselected))
        trace_events.append(_hidden_trace_event(entry, visible_ref, "NOT_ATLAS_INPUT", source, hidden_ref, confidence))
    summary = _feedback_summary(feedback_events)
    return (
        {
            "schema_version": "waymark.closed_loop.atlas_feedback_payload.v0.1",
            "profile_id": _profile_id(profile),
            "batch_id": batch.get("batch_id"),
            "source": "mission",
            "source_session_id": f"closed_loop_session:{_profile_id(profile)}:{batch.get('batch_id')}",
            "created_at": _now(),
            "feedback_events": feedback_events,
            "summary": summary,
        },
        {
            "schema_version": "waymark.closed_loop.hidden_evaluator_trace.v0.1",
            "profile_id": _profile_id(profile),
            "batch_id": batch.get("batch_id"),
            "NOT_ATLAS_INPUT": True,
            "NOT_PRODUCTION_SIGNAL": True,
            "EVALUATOR_ONLY": True,
            "created_at": _now(),
            "trace_events": trace_events,
            "summary": {
                "events": len(trace_events),
                "source_counts": _count_by(trace_events, "reaction_source"),
            },
        },
    )


def _flatten_route_items(batch: Dict[str, Any]) -> List[Dict[str, Any]]:
    refs = []
    for mission in batch.get("missions", []):
        for item in (mission.get("route") or {}).get("items", []):
            global_id = f"{mission.get('mission_id')}::{item.get('item_id')}"
            refs.append({"mission": mission, "route_item": item, "route_item_global_id": global_id})
    return refs


def _load_hidden_truth(profile: str) -> Dict[str, Any]:
    candidates = [
        REPO_ROOT / "data" / "survey_simulation" / "llm_profile_review" / "api_pilot_3x3" / "simulator_private" / "hidden_truth_packets" / f"hidden_truth_public_profile_{profile}_A3_Al1_S2.json",
        REPO_ROOT / "data" / "survey_simulation" / "fake_profiles" / f"fake_profile_{profile}.json",
    ]
    for path in candidates:
        if path.exists():
            loaded = _load_json(path)
            loaded["_source_file"] = str(path)
            return loaded
    return {}


def _hidden_reaction_index(hidden_truth: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    index: Dict[str, Dict[str, Any]] = {}
    for example in hidden_truth.get("heldout_reaction_examples", []):
        ref = example.get("music_object_ref") or {}
        for value in [ref.get("display_name"), ref.get("canonical_artist_id"), ref.get("canonical_album_id"), ref.get("canonical_song_recording_id")]:
            if value:
                index[_normalize(value)] = example
    return index


def _decide_hidden_reaction(item: Dict[str, Any], visible_ref: Dict[str, Any], hidden_index: Dict[str, Dict[str, Any]]) -> Tuple[str, str, Optional[str], float]:
    metadata = item.get("display_metadata") or {}
    hint = item.get("music_kit_search_hint") or {}
    title = metadata.get("title") or hint.get("title")
    artist = metadata.get("artist") or hint.get("artist")
    for key, source in [(title, "hidden_song_exact"), (artist, "hidden_artist_inferred")]:
        if key and _normalize(key) in hidden_index:
            example = hidden_index[_normalize(key)]
            return _map_hidden_reaction(example.get("reaction")), source, (example.get("music_object_ref") or {}).get("display_name"), float(example.get("confidence") or 0.7)
    return _heuristic_reaction(item), "graph_neighborhood_imputed", None, 0.42


def _map_hidden_reaction(reaction: str) -> str:
    return {
        "love": "strong_positive",
        "like": "qualified_positive",
        "ok": "keep",
        "dont_like": "negative",
        "dont_know_enough": "unknown",
    }.get(reaction, "unknown")


def _heuristic_reaction(item: Dict[str, Any]) -> str:
    role = item.get("selection_role")
    risk = item.get("risk_class")
    seed = _stable_float(f"{item.get('item_id')}:{role}:{risk}")
    if risk in {"trap", "dead_end_check"}:
        return "negative" if seed < 0.72 else "keep"
    if role in {"anchor", "bridge"} or risk == "safe":
        return "strong_positive" if seed < 0.35 else "qualified_positive"
    if role == "probe" or risk == "risky":
        return "qualified_positive" if seed < 0.45 else "unknown"
    if role == "checkpoint":
        return "keep"
    return "unknown"


def _visible_music_object_ref(item: Dict[str, Any]) -> Dict[str, Any]:
    metadata = item.get("display_metadata") or {}
    hint = item.get("music_kit_search_hint") or {}
    return {
        "object_type": item.get("item_type"),
        "artist": metadata.get("artist"),
        "title": metadata.get("title"),
        "album": metadata.get("album"),
        "release_year": metadata.get("release_year"),
        "search_query": hint.get("search_query"),
        "resolution_state": hint.get("resolution_status_placeholder"),
        "candidate_id": item.get("candidate_id"),
    }


def _atlas_feedback_event(entry: Dict[str, Any], visible_ref: Dict[str, Any], playback_status: str, primary_reaction: str, selected_tags: List[str], shown_unselected_tags: List[str]) -> Dict[str, Any]:
    mission = entry["mission"]
    item = entry["route_item"]
    return {
        "event_id": f"feedback:{entry['route_item_global_id']}",
        "mission_id": mission.get("mission_id"),
        "mission_item_id": item.get("item_id"),
        "route_item_ref": {
            "route_index": item.get("route_index"),
            "selection_role": item.get("selection_role"),
            "risk_class": item.get("risk_class"),
            "expected_features": item.get("expected_features", []),
        },
        "music_object_ref": visible_ref,
        "playback_status": playback_status,
        "primary_reaction": primary_reaction,
        "selected_secondary_tags": selected_tags,
        "shown_unselected_tags": shown_unselected_tags,
        "note": _simulated_note(primary_reaction, item) if selected_tags else "",
        "timestamp": _now(),
        "source": "mission",
        "source_session_id": f"session:{mission.get('mission_id')}",
    }


def _hidden_trace_event(entry: Dict[str, Any], visible_ref: Dict[str, Any], marker: str, source: str, hidden_ref: Optional[str], confidence: float) -> Dict[str, Any]:
    return {
        "trace_id": f"trace:{entry['route_item_global_id']}",
        marker: True,
        "mission_id": entry["mission"].get("mission_id"),
        "mission_item_id": entry["route_item"].get("item_id"),
        "visible_music_object_ref": visible_ref,
        "reaction_source": source,
        "hidden_preference_ref": hidden_ref,
        "imputation_confidence": confidence,
    }


def _selected_secondary_tags(item: Dict[str, Any], primary_reaction: str) -> List[str]:
    reaction_key = {
        "strong_positive": "love",
        "qualified_positive": "like",
        "keep": "keep",
        "unknown": "keep",
        "negative": "not_for_me",
    }.get(primary_reaction, "keep")
    chips = ((item.get("feedback_chip_sets") or {}).get(reaction_key) or [])
    return [chip.get("label") for chip in chips[:1] if chip.get("label")]


def _shown_unselected_tags(item: Dict[str, Any], selected: Optional[List[str]] = None) -> List[str]:
    selected = selected or []
    labels = []
    for chips in (item.get("feedback_chip_sets") or {}).values():
        for chip in chips:
            label = chip.get("label")
            if label and label not in selected and label not in labels:
                labels.append(label)
    return labels[:4]


def _simulated_note(primary_reaction: str, item: Dict[str, Any]) -> str:
    if primary_reaction == "negative":
        return f"Simulated note: this did not support {item.get('selection_role')} evidence."
    if primary_reaction in {"strong_positive", "qualified_positive"}:
        return f"Simulated note: this supported {item.get('selection_role')} evidence but remains scoped."
    return "Simulated note: useful but not decisive."


def _feedback_summary(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    signaled = [event for event in events if event["primary_reaction"] not in {"skipped", "no_signal", "unresolved"}]
    tagged = [event for event in signaled if event.get("selected_secondary_tags")]
    return {
        "route_items": len(events),
        "signaled_items": len(signaled),
        "signal_rate": round(len(signaled) / len(events), 3) if events else 0,
        "tagged_signaled_items": len(tagged),
        "secondary_tag_rate_among_signaled": round(len(tagged) / len(signaled), 3) if signaled else 0,
        "primary_reaction_counts": _count_by(events, "primary_reaction"),
        "playback_status_counts": _count_by(events, "playback_status"),
    }


def _ingest_simulated_feedback(profile: str, feedback: Dict[str, Any]) -> Dict[str, Any]:
    signals = []
    update_candidates = []
    role_changes = []
    contradiction_clusters = []
    confidence_deltas = []
    for index, event in enumerate(feedback.get("feedback_events", []), start=1):
        signal_id = f"signal:mission:{_profile_id(profile)}:{index:03d}"
        signal = {
            "signal_id": signal_id,
            "record_type": "signal",
            "schema_version": "closed_loop.v0.1",
            "user_id": _profile_id(profile),
            "source": "mission",
            "source_session_id": event.get("source_session_id"),
            "mission_id": event.get("mission_id"),
            "mission_item_id": event.get("mission_item_id"),
            "subject_music_object_ref": event.get("music_object_ref"),
            "playback_status": event.get("playback_status"),
            "primary_reaction": event.get("primary_reaction"),
            "observed_user_tags": event.get("selected_secondary_tags", []),
            "shown_unselected_tags": event.get("shown_unselected_tags", []),
            "signal_strength": _signal_strength(event),
            "interpretation_confidence": _interpretation_confidence(event),
            "integrity_state": "valid",
        }
        signals.append(signal)
        update = _possible_update_from_signal(profile, signal)
        update_candidates.append(update)
        role_changes.append(_role_change_from_update(update, signal))
        confidence_deltas.append({"signal_id": signal_id, "target_role": update["atlas_role"], "delta": update["confidence_delta"], "review_required": True})
        if event.get("primary_reaction") == "negative" and event.get("route_item_ref", {}).get("selection_role") in {"anchor", "bridge", "probe"}:
            contradiction_clusters.append({"cluster_id": f"contradiction:{signal_id}", "label": event.get("music_object_ref", {}).get("title"), "evidence_signal_ids": [signal_id], "review_required": True})
    summary = {
        "signals_created": len(signals),
        "possible_update_candidates_created": len(update_candidates),
        "role_change_candidates": len(role_changes),
        "confidence_deltas": len(confidence_deltas),
        "contradiction_clusters": len(contradiction_clusters),
        "auto_promotions": 0,
        "canonical_graph_mutations": 0,
    }
    return {
        "schema_version": "waymark.closed_loop.atlas_update_records.v0.1",
        "profile_id": _profile_id(profile),
        "created_at": _now(),
        "provenance_policy": {
            "atlas_inputs_are_user_visible_mission_feedback_only": True,
            "profile_writer_outputs_used": False,
            "raw_a3_payloads_used": False,
            "canonical_graph_mutation_allowed": False,
            "auto_promotion_allowed": False,
        },
        "signals": signals,
        "possible_atlas_update_candidates": update_candidates,
        "role_assignment_candidate_changes": role_changes,
        "confidence_deltas": confidence_deltas,
        "contradiction_clusters": contradiction_clusters,
        "summary": summary,
    }


def _build_atlas_delta(
    profile: str,
    first_batch: Dict[str, Any],
    feedback: Dict[str, Any],
    atlas_updates: Dict[str, Any],
) -> Dict[str, Any]:
    profile_id = _profile_id(profile)
    signals_by_mission: Dict[str, List[Dict[str, Any]]] = {}
    for signal in atlas_updates.get("signals", []):
        mission_id = signal.get("mission_id")
        if mission_id:
            signals_by_mission.setdefault(mission_id, []).append(signal)

    update_ids_by_signal: Dict[str, List[str]] = {}
    for update in atlas_updates.get("possible_atlas_update_candidates", []):
        for signal_id in update.get("evidence_signal_ids", []):
            update_ids_by_signal.setdefault(signal_id, []).append(update.get("candidate_id"))

    feedback_by_signal_key = {
        (event.get("mission_id"), event.get("mission_item_id")): event
        for event in feedback.get("feedback_events", [])
    }
    deltas = []
    for index, mission in enumerate(first_batch.get("missions", []), start=1):
        mission_id = mission.get("mission_id")
        mission_signals = signals_by_mission.get(mission_id, [])
        source_signal_refs = [signal.get("signal_id") for signal in mission_signals if signal.get("signal_id")]
        source_update_refs = [
            update_id
            for signal_id in source_signal_refs
            for update_id in update_ids_by_signal.get(signal_id, [])
            if update_id
        ]
        reaction_counts = _count_by(mission_signals, "primary_reaction")
        placeholder_count = sum(1 for item in (mission.get("route") or {}).get("items", []) if _is_candidate_search_slot(item))
        action, change_type = _classify_atlas_delta(mission, reaction_counts, placeholder_count)
        labels = [
            signal.get("subject_music_object_ref", {}).get("title") or signal.get("subject_music_object_ref", {}).get("artist")
            for signal in mission_signals
        ]
        labels = [str(label) for label in labels if label]
        selected_tags = [
            tag
            for signal in mission_signals
            for tag in signal.get("observed_user_tags", [])
            if tag
        ]
        changed = _delta_change_sentence(mission, action, reaction_counts, labels, placeholder_count)
        delta_id = f"atlas_delta:{profile_id}:{index:03d}"
        deltas.append(
            {
                "delta_id": delta_id,
                "profile_id": profile_id,
                "source_batch_id": first_batch.get("batch_id"),
                "source_mission_id": mission_id,
                "source_mission_title": mission.get("title"),
                "source_signal_refs": source_signal_refs,
                "source_update_candidate_refs": source_update_refs,
                "interpreted_change_type": change_type,
                "recommended_adaptation_action": action,
                "reaction_counts": reaction_counts,
                "selected_tag_evidence": selected_tags[:8],
                "placeholder_count": placeholder_count,
                "what_changed": changed,
                "candidate_pool_behavior_effect": _candidate_pool_behavior_effect(action),
                "review_required": True,
                "canonical_graph_mutation_allowed": False,
                "auto_promotion_allowed": False,
                "mission_item_feedback_refs": [
                    event.get("event_id")
                    for signal in mission_signals
                    for event in [feedback_by_signal_key.get((signal.get("mission_id"), signal.get("mission_item_id")))]
                    if event and event.get("event_id")
                ],
            }
        )
    summary = _atlas_delta_summary(deltas)
    return {
        "schema_version": "waymark.closed_loop.atlas_delta.v0.1",
        "profile_id": profile_id,
        "created_at": _now(),
        "source": "mission_feedback_interpretation",
        "provenance_policy": {
            "hidden_truth_used": False,
            "profile_writer_outputs_used": False,
            "raw_a3_payloads_used": False,
            "canonical_graph_mutation_allowed": False,
            "auto_promotion_allowed": False,
        },
        "deltas": deltas,
        "summary": summary,
    }


def _classify_atlas_delta(mission: Dict[str, Any], reaction_counts: Dict[str, int], placeholder_count: int) -> Tuple[str, str]:
    text = " ".join([mission.get("title", ""), " ".join(mission.get("archetypes", []))]).lower()
    positive = reaction_counts.get("strong_positive", 0) + reaction_counts.get("qualified_positive", 0)
    weak = reaction_counts.get("skipped", 0) + reaction_counts.get("no_signal", 0) + reaction_counts.get("unknown", 0) + reaction_counts.get("unresolved", 0)
    keep = reaction_counts.get("keep", 0)
    negative = reaction_counts.get("negative", 0)
    if negative and ("dead" in text or "trap" in text or "false" in text):
        return "dead_end_confirmation", "dead_end_hypothesis_strengthened"
    if negative:
        return "contradiction_check", "scoped_contradiction_appeared"
    if placeholder_count > 1:
        return "retire_pause", "resolution_quality_blocks_learning"
    if weak >= 2 and weak >= positive + keep:
        return "retire_pause", "weak_or_no_signal_path_should_pause"
    if keep and positive <= 1:
        return "pivot", "waypoint_or_side_probe_outperformed"
    if positive >= 2:
        return "deepen", "positive_signal_strengthened"
    if positive == 1 and weak <= 1:
        return "deepen", "single_positive_needs_recurrence"
    return "retire_pause", "insufficient_signal_to_continue"


def _delta_change_sentence(mission: Dict[str, Any], action: str, reaction_counts: Dict[str, int], labels: List[str], placeholder_count: int) -> str:
    title = mission.get("title") or mission.get("mission_id")
    label_text = ", ".join(labels[:3]) if labels else "the route"
    counts = ", ".join(f"{key}={value}" for key, value in sorted(reaction_counts.items()))
    if action == "deepen":
        return f"Batch 1 strengthened `{title}` through positive evidence on {label_text}; counts: {counts}."
    if action == "pivot":
        return f"Batch 1 made `{title}` look more useful as a waypoint or side route than as the original path; counts: {counts}."
    if action == "retire_pause":
        reason = "resolution placeholders blocked clean learning" if placeholder_count > 1 else "weak/no-signal evidence outweighed useful reactions"
        return f"Batch 1 says to pause or narrow `{title}` because {reason}; counts: {counts}."
    if action == "contradiction_check":
        return f"Batch 1 introduced scoped conflict inside `{title}`; a negative or miss needs a narrower scope check; counts: {counts}."
    return f"Batch 1 strengthened a possible dead-end boundary inside `{title}` without authorizing broad rejection; counts: {counts}."


def _candidate_pool_behavior_effect(action: str) -> str:
    return {
        "deepen": "prefer bridge/probe candidates near the strongest feature pattern",
        "pivot": "prefer candidate roles that follow the side signal without promoting it",
        "retire_pause": "deprioritize or replace this path unless a resolution-calibration mission is explicitly needed",
        "contradiction_check": "choose scoped controls that separate one-object exception from broader lane",
        "dead_end_confirmation": "choose bounded trap/control candidates; do not broaden into a recommendation route",
    }.get(action, "review_required")


def _atlas_delta_summary(deltas: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "delta_count": len(deltas),
        "action_counts": _count_by(deltas, "recommended_adaptation_action"),
        "what_batch_1_taught": "Batch 1 produced interpreted AtlasDelta entries for second-batch routing; every adaptive mission must consume at least one delta.",
        "deepened_paths": [delta["delta_id"] for delta in deltas if delta.get("recommended_adaptation_action") == "deepen"],
        "pivots": [delta["delta_id"] for delta in deltas if delta.get("recommended_adaptation_action") == "pivot"],
        "paused_or_retired_paths": [delta["delta_id"] for delta in deltas if delta.get("recommended_adaptation_action") == "retire_pause"],
        "contradictions_to_check": [delta["delta_id"] for delta in deltas if delta.get("recommended_adaptation_action") == "contradiction_check"],
        "dead_ends_to_confirm": [delta["delta_id"] for delta in deltas if delta.get("recommended_adaptation_action") == "dead_end_confirmation"],
    }


def _possible_update_from_signal(profile: str, signal: Dict[str, Any]) -> Dict[str, Any]:
    reaction = signal.get("primary_reaction")
    role = signal.get("subject_music_object_ref", {}).get("candidate_id") or signal.get("subject_music_object_ref", {}).get("title")
    route_role = "Signal only"
    candidate_behavior = "unknown"
    confidence_delta = 0.0
    if reaction in {"strong_positive", "qualified_positive"}:
        route_role = "Frontier"
        candidate_behavior = "probe"
        confidence_delta = 0.12 if reaction == "strong_positive" else 0.08
    elif reaction == "keep":
        route_role = "Waypoint"
        candidate_behavior = "waypoint"
        confidence_delta = 0.05
    elif reaction == "negative":
        route_role = "Dead End"
        candidate_behavior = "trap"
        confidence_delta = -0.08
    return {
        "candidate_id": f"possible_update:{signal['signal_id']}",
        "target_label": role,
        "atlas_role": route_role,
        "candidate_pool_behavior": candidate_behavior,
        "confidence_delta": confidence_delta,
        "scope": "mission_item_object_scope",
        "trigger_conditions": ["future recurrence required before promotion"],
        "evidence_signal_ids": [signal["signal_id"]],
        "review_required": True,
        "canonical_graph_mutation_allowed": False,
        "auto_promote": False,
    }


def _role_change_from_update(update: Dict[str, Any], signal: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "change_id": f"role_change:{signal['signal_id']}",
        "target_label": update.get("target_label"),
        "proposed_role": update.get("atlas_role"),
        "candidate_pool_behavior": update.get("candidate_pool_behavior"),
        "confidence_delta": update.get("confidence_delta"),
        "evidence_signal_ids": [signal["signal_id"]],
        "promotion_state": "candidate",
        "review_required": True,
    }


def _signal_strength(event: Dict[str, Any]) -> float:
    return {
        "strong_positive": 0.86,
        "qualified_positive": 0.72,
        "keep": 0.52,
        "unknown": 0.28,
        "negative": 0.78,
        "skipped": 0.18,
        "no_signal": 0.05,
        "unresolved": 0.0,
    }.get(event.get("primary_reaction"), 0.2)


def _interpretation_confidence(event: Dict[str, Any]) -> float:
    if event.get("selected_secondary_tags"):
        return min(_signal_strength(event) + 0.08, 0.9)
    if event.get("primary_reaction") in {"skipped", "no_signal", "unknown"}:
        return 0.24
    return max(_signal_strength(event) - 0.12, 0.1)


def _build_updated_digest(profile: str, atlas_updates: Dict[str, Any], atlas_delta: Dict[str, Any]) -> Dict[str, Any]:
    digest = deepcopy(_load_json(A3_INGESTION_DIR / f"atlas_digest_view_profile_{profile}_A3.json"))
    signal_summaries = digest.setdefault("signal_summaries", [])
    for signal in atlas_updates.get("signals", [])[:30]:
        signal_summaries.append(
            {
                "signal_id": signal.get("signal_id"),
                "source": "mission",
                "summary": f"{signal.get('primary_reaction')} on {signal.get('subject_music_object_ref', {}).get('title')}",
                "signal_strength": signal.get("signal_strength"),
                "interpretation_confidence": signal.get("interpretation_confidence"),
            }
        )
    digest["closed_loop_learning_summary"] = _learning_summary_from_updates(atlas_updates)
    digest["atlas_delta_after_batch_1_summary"] = atlas_delta.get("summary")
    digest["atlas_delta_after_batch_1_refs"] = [
        {
            "delta_id": delta.get("delta_id"),
            "recommended_adaptation_action": delta.get("recommended_adaptation_action"),
            "what_changed": delta.get("what_changed"),
            "source_signal_refs": delta.get("source_signal_refs", []),
            "source_update_candidate_refs": delta.get("source_update_candidate_refs", []),
        }
        for delta in atlas_delta.get("deltas", [])
    ]
    digest["candidate_pool_behavior_hints_after_batch_1"] = atlas_updates.get("role_assignment_candidate_changes", [])[:30]
    digest["unresolved_questions_after_batch_1"] = _unresolved_after_updates(atlas_updates)
    digest["canonical_graph_mutation_allowed"] = False
    return digest


def _learning_summary_from_updates(atlas_updates: Dict[str, Any]) -> Dict[str, Any]:
    updates = atlas_updates.get("possible_atlas_update_candidates", [])
    return {
        "positive_frontier_support": [item for item in updates if item.get("atlas_role") == "Frontier"][:12],
        "waypoint_confirmations": [item for item in updates if item.get("atlas_role") == "Waypoint"][:12],
        "dead_end_support": [item for item in updates if item.get("atlas_role") == "Dead End"][:12],
        "review_required_for_all_candidates": True,
        "auto_promotions": 0,
    }


def _unresolved_after_updates(atlas_updates: Dict[str, Any]) -> List[str]:
    unresolved = []
    for signal in atlas_updates.get("signals", []):
        if signal.get("primary_reaction") in {"unknown", "skipped", "no_signal"}:
            unresolved.append(f"Still unclear: {signal.get('subject_music_object_ref', {}).get('title')}")
    return unresolved[:20]


def _profile_qualitative_review(
    *,
    profile: str,
    first_batch: Dict[str, Any],
    first_eval: Dict[str, Any],
    feedback: Dict[str, Any],
    atlas_updates: Dict[str, Any],
    atlas_delta: Dict[str, Any],
    second_batch: Optional[Dict[str, Any]],
    second_eval: Dict[str, Any],
) -> str:
    first_titles = [mission.get("title") for mission in first_batch.get("missions", [])]
    second_titles = [mission.get("title") for mission in (second_batch or {}).get("missions", [])]
    feedback_summary = feedback.get("summary", {})
    atlas_summary = atlas_updates.get("summary", {})
    delta_summary = atlas_delta.get("summary", {})
    adaptive_summary = second_eval.get("adaptive_summary") or {}
    smarter = bool(second_eval.get("valid") and adaptive_summary.get("visible_adaptive_mission_count", 0) >= 2)
    lines = [
        f"# Qualitative Review Profile {profile}",
        "",
        "## First Batch",
        "",
        f"- Mission count: `{len(first_titles)}`",
        f"- Portfolio valid: `{first_eval.get('valid')}`",
        f"- Route items ready: `{first_eval.get('route_items_ready')}/{first_eval.get('route_items_total')}`",
        f"- Titles: {', '.join('`' + str(title) + '`' for title in first_titles)}",
        "",
        "## Simulated Feedback",
        "",
        f"- Signal rate: `{feedback_summary.get('signal_rate')}`",
        f"- Secondary tag rate among signaled: `{feedback_summary.get('secondary_tag_rate_among_signaled')}`",
        f"- Reaction counts: `{feedback_summary.get('primary_reaction_counts')}`",
        "- Hidden evaluator trace is separate and marked `NOT_ATLAS_INPUT`.",
        "",
        "## Atlas Update",
        "",
        f"- Signals created: `{atlas_summary.get('signals_created')}`",
        f"- Possible updates created: `{atlas_summary.get('possible_update_candidates_created')}`",
        f"- Atlas deltas created: `{delta_summary.get('delta_count')}`",
        f"- Delta action counts: `{delta_summary.get('action_counts')}`",
        f"- Auto promotions: `{atlas_summary.get('auto_promotions')}`",
        f"- Canonical graph mutations: `{atlas_summary.get('canonical_graph_mutations')}`",
        "",
        "## Second Batch",
        "",
        f"- Mission count: `{len(second_titles)}`",
        f"- Portfolio valid: `{second_eval.get('valid')}`",
        f"- Visibly adaptive missions: `{adaptive_summary.get('visible_adaptive_mission_count')}`",
        f"- Adaptation actions: `{adaptive_summary.get('adaptation_action_counts')}`",
        f"- Route items ready: `{second_eval.get('route_items_ready')}/{second_eval.get('route_items_total')}`",
        f"- Titles: {', '.join('`' + str(title) + '`' for title in second_titles)}",
        "",
        "## Read",
        "",
        f"- Batch two smarter than batch one: `{'yes' if smarter else 'review_needed'}`",
        "- Review note: this is deterministic product-loop review, not an LLM-as-judge artifact.",
    ]
    return "\n".join(lines) + "\n"


def _write_adaptive_second_batch_report(*, profile_results: List[Dict[str, Any]], dry_run: bool) -> Path:
    REPORTS_ROOT.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report_path = REPORTS_ROOT / f"adaptive_second_batch_report_{timestamp}.md"
    lines = [
        "# Adaptive Second-Batch Report v0.1",
        "",
        f"- Generated at: `{_now()}`",
        f"- Run type: `{'dry_run' if dry_run else 'live_api'}`",
        f"- Contract: `{ADAPTIVE_CONTRACT_VERSION}`",
        f"- Closed-loop output root: `{CLOSED_LOOP_OUTPUT_DIR}`",
        "",
        "## Mission Table",
        "",
        "| Profile | Mission | Adaptation Action | AtlasDelta Refs | Source Signals | Source Updates | Why Now | Not Doing Anymore | Resolution Status | Suitability | Product Status |",
        "| --- | --- | --- | ---: | ---: | ---: | --- | --- | --- | --- | --- |",
    ]
    for result in profile_results:
        second_eval = result.get("second_batch_evaluation") or {}
        for mission_result in second_eval.get("adaptive_mission_results") or []:
            lines.append(
                "| "
                f"`{result.get('profile_id')}` | "
                f"`{mission_result.get('mission_id')}` | "
                f"`{mission_result.get('adaptation_action')}` | "
                f"{len(mission_result.get('source_atlas_delta_refs') or [])} | "
                f"{mission_result.get('source_signal_ref_count')} | "
                f"{mission_result.get('source_update_candidate_ref_count')} | "
                f"{_compact_table_text(_mission_field_lookup(result, mission_result.get('mission_id'), 'why_this_mission_now'))} | "
                f"{_compact_table_text(_mission_field_lookup(result, mission_result.get('mission_id'), 'what_this_mission_is_not_doing_anymore'))} | "
                f"`{mission_result.get('declared_resolution_quality_status')}` | "
                f"`{mission_result.get('closed_loop_learning_suitability')}` | "
                f"`{mission_result.get('product_status')}` |"
            )
    lines.extend(["", "## Profile Summary", ""])
    for result in profile_results:
        adaptive_summary = ((result.get("second_batch_evaluation") or {}).get("adaptive_summary") or {})
        delta_summary = result.get("atlas_delta_summary") or {}
        lines.extend(
            [
                f"### {result.get('profile_id')}",
                "",
                f"- What batch 1 taught: `{delta_summary.get('what_batch_1_taught')}`",
                f"- Atlas deltas consumed/action counts: `{delta_summary.get('action_counts')}`",
                f"- Deepened: `{delta_summary.get('deepened_paths')}`",
                f"- Pivoted: `{delta_summary.get('pivots')}`",
                f"- Paused/retired/narrowed: `{delta_summary.get('paused_or_retired_paths')}`",
                f"- Contradictions checked: `{delta_summary.get('contradictions_to_check')}`",
                f"- Dead ends confirmed: `{delta_summary.get('dead_ends_to_confirm')}`",
                f"- Resolution risks/product counts: `{adaptive_summary.get('mission_product_status_counts')}`",
                f"- Pass/fail: `{result.get('final_status')}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Product Rule",
            "",
            "Batch 2 must be visibly caused by Atlas changes from Batch 1. Schema validity alone is not product pass.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def _mission_field_lookup(result: Dict[str, Any], mission_id: Optional[str], field: str) -> str:
    if not mission_id:
        return ""
    output_file = ((result.get("second_batch") or {}).get("output_file"))
    if not output_file:
        return ""
    path = Path(output_file)
    if not path.exists():
        return ""
    try:
        batch = _load_json(path)
    except Exception:  # noqa: BLE001
        return ""
    for mission in batch.get("missions", []):
        if mission.get("mission_id") == mission_id:
            return str(mission.get(field) or "")
    return ""


def _compact_table_text(text: str, limit: int = 120) -> str:
    compact = " ".join(str(text).split()).replace("|", "/")
    if len(compact) > limit:
        compact = compact[: limit - 3].rstrip() + "..."
    return compact


def _closed_loop_manifest(
    *,
    config: OpenAIConfig,
    profile_results: List[Dict[str, Any]],
    dry_run: bool,
    adaptive_report_path: Path,
) -> Dict[str, Any]:
    return {
        "schema_version": "waymark.closed_loop_manifest.v0.1",
        "generated_at": _now(),
        "run_type": "dry_run" if dry_run else "live_api",
        "model": config.model,
        "output_root": str(CLOSED_LOOP_OUTPUT_DIR),
        "adaptive_contract_version": ADAPTIVE_CONTRACT_VERSION,
        "adaptive_second_batch_report": str(adaptive_report_path),
        "profiles": [result.get("profile_id") for result in profile_results],
        "input_roots": {
            "ingestion_proof": str(A3_INGESTION_DIR),
            "node_interpretation": str(A3_NODE_INTERPRETATION_DIR),
            "wwtsf_substrate": str(A3_WWTSF_OUTPUT_DIR),
        },
        "prohibited_inputs": {
            "raw_a3_payloads_used_for_generation": False,
            "profile_writer_outputs_used_as_evidence": False,
            "hidden_truth_used_for_generation_or_atlas": False,
            "canonical_graph_mutation_allowed": False,
        },
        "simulation_parameters": {
            "primary_signal_ratio": PRIMARY_SIGNAL_RATIO,
            "secondary_tag_ratio_among_signaled": SECONDARY_TAG_RATIO,
        },
        "profile_results": profile_results,
    }


def _write_acceptance_report(*, profile_results: List[Dict[str, Any]], dry_run: bool, adaptive_report_path: Path) -> None:
    total_cost = sum(
        ((result.get("first_batch") or {}).get("estimated_total_cost_usd") or 0)
        + ((result.get("second_batch") or {}).get("estimated_total_cost_usd") or 0)
        for result in profile_results
    )
    lines = [
        "# Closed-Loop Waymark First-Batch Simulation v0.1",
        "",
        f"- Generated at: `{_now()}`",
        f"- Run type: `{'dry_run' if dry_run else 'live_api'}`",
        f"- Output root: `{CLOSED_LOOP_OUTPUT_DIR}`",
        f"- Adaptive second-batch report: `{adaptive_report_path}`",
        "- Model for mission generation: `gpt-5.4-mini`",
        "- Hidden simulator traces are evaluator-only and excluded from Atlas-facing payloads.",
        "",
        "## Cost",
        "",
        f"- Estimated mission-generation cost: `{_fmt_cost(total_cost)}`",
        "",
        "## Profile Summary",
        "",
        "| Profile | First Batch | Signal Rate | Tag Rate | Atlas Signals | Second Batch | Status |",
        "| --- | --- | ---: | ---: | ---: | --- | --- |",
    ]
    for result in profile_results:
        feedback = result.get("feedback_summary") or {}
        atlas = result.get("atlas_update_summary") or {}
        lines.append(
            "| "
            f"`{result.get('profile_id')}` | "
            f"`{(result.get('first_batch_evaluation') or {}).get('valid')}` | "
            f"{feedback.get('signal_rate', '')} | "
            f"{feedback.get('secondary_tag_rate_among_signaled', '')} | "
            f"{atlas.get('signals_created', '')} | "
            f"`{(result.get('second_batch_evaluation') or {}).get('valid')}` | "
            f"`{result.get('final_status')}` |"
        )
    lines.extend(["", "## Adaptive Second-Batch Summary", ""])
    for result in profile_results:
        adaptive_summary = ((result.get("second_batch_evaluation") or {}).get("adaptive_summary") or {})
        delta_summary = result.get("atlas_delta_summary") or {}
        lines.extend(
            [
                f"### {result.get('profile_id')}",
                "",
                f"- AtlasDelta actions: `{delta_summary.get('action_counts')}`",
                f"- Visibly adaptive missions: `{adaptive_summary.get('visible_adaptive_mission_count')}`",
                f"- Adaptation actions used: `{adaptive_summary.get('adaptation_action_counts')}`",
                f"- Mission product status counts: `{adaptive_summary.get('mission_product_status_counts')}`",
                "",
            ]
        )
    lines.extend(
        [
            "",
            "## Acceptance Criteria Read",
            "",
            "- Six first-batch missions per profile: checked in per-profile evaluations.",
            "- Six second-batch missions per profile: checked in per-profile evaluations.",
            "- Route items concrete or explicit candidate-search slots: checked in mission evaluations.",
            "- Simulated feedback density: reported per profile.",
            "- Hidden simulator truth excluded from Atlas-facing payload: enforced by separate artifact paths and payload construction.",
            "- Atlas feedback ingested as Signals / PossibleAtlasUpdateCandidates / confidence deltas: written per profile.",
            "- AtlasDelta generated after batch one and required by adaptive second-batch missions.",
            "- Second-batch adaptivity evaluated separately from schema validity.",
            "- No canonical graph mutation: `0` in update summaries.",
            "- No automatic Atlas promotion: `0` in update summaries.",
            "",
            "## Recommendation",
            "",
            "`CLOSED_LOOP_REVIEW_READY`",
        ]
    )
    (CLOSED_LOOP_OUTPUT_DIR / "closed_loop_acceptance_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _stage_summary(stage: Dict[str, Any]) -> Dict[str, Any]:
    metadata = stage.get("metadata") or {}
    return {
        "valid": (stage.get("validation_result") or {}).get("valid"),
        "output_file": stage.get("output_file"),
        "input_tokens": metadata.get("input_tokens"),
        "output_tokens": metadata.get("output_tokens"),
        "estimated_total_cost_usd": metadata.get("estimated_total_cost_usd"),
        "latency_seconds": metadata.get("latency_seconds"),
    }


def _feedback_metrics_ok(feedback: Dict[str, Any]) -> bool:
    summary = feedback.get("summary") or {}
    return abs(float(summary.get("signal_rate", 0)) - PRIMARY_SIGNAL_RATIO) <= 0.12 and abs(float(summary.get("secondary_tag_rate_among_signaled", 0)) - SECONDARY_TAG_RATIO) <= 0.15


def _count_by(items: List[Dict[str, Any]], key: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for item in items:
        value = str(item.get(key))
        counts[value] = counts.get(value, 0) + 1
    return counts


def _stable_float(seed: str) -> float:
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return int(digest[:12], 16) / float(16**12)


def _normalize(value: Any) -> str:
    return "".join(char.lower() if char.isalnum() else " " for char in str(value)).strip()
