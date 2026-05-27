from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional

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


HARNESS_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = HARNESS_ROOT.parent
FIXTURES_ROOT = HARNESS_ROOT / "fixtures"
A3_INGESTION_DIR = REPO_ROOT / "data" / "atlas_schema" / "ingestion_proof" / "a3_gpt_5_5_3x3"
A3_NODE_INTERPRETATION_DIR = REPO_ROOT / "data" / "atlas_schema" / "node_interpretation_smoke" / "a3_v0_1_1"
A3_WWTSF_OUTPUT_DIR = REPO_ROOT / "data" / "atlas_schema" / "wwtsf_substrate_smoke" / "a3_v0_1_2"
A3_WWTSF_SHADOW_DIR = REPO_ROOT / "data" / "atlas_schema" / "wwtsf_substrate_smoke" / "a3_v0_1_3"
A3_WWTSF_CONSISTENCY_DIR = REPO_ROOT / "data" / "atlas_schema" / "wwtsf_substrate_smoke" / "a3_v0_1_4"
A3_WWTSF_REPAIR_DIR = REPO_ROOT / "data" / "atlas_schema" / "wwtsf_substrate_smoke" / "a3_v0_1_5"
A3_MISSION_OUTPUT_DIR = REPO_ROOT / "data" / "mission_generation" / "atlas_substrate_a3_v0_1_2"
PROFILES = ["01", "05", "06"]


CostEstimator = Callable[[str, Dict[str, Optional[int]], Dict[str, Any]], Dict[str, Any]]


def run_wwtsf_substrate(
    *,
    profiles: Iterable[str],
    config: OpenAIConfig,
    pricing: Dict[str, Any],
    estimate_cost_usd: CostEstimator,
    dry_run: bool,
) -> int:
    output_dir = A3_WWTSF_OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    schema = _load_json(FIXTURES_ROOT / "schemas" / "wwtsf_substrate_output_schema_v0_1_2.json")
    schema_out = output_dir / "wwtsf_substrate_smoke_output_schema_v0_1_2.json"
    write_json(schema_out, schema)

    results = []
    for profile in profiles:
        profile_id = _profile_id(profile)
        context_packet = _build_wwtsf_context(profile)
        rendered_prompt = _render_template(
            FIXTURES_ROOT / "prompt_templates" / "wwtsf_substrate_v0_1_2.md",
            {
                "{{PROFILE_ID}}": profile_id,
                "{{CONTEXT_PACKET_JSON}}": json.dumps(context_packet, indent=2, sort_keys=True),
                "{{OUTPUT_SCHEMA_JSON}}": json.dumps(schema, indent=2, sort_keys=True),
            },
        )
        run_result = _run_structured_generation(
            output_dir=output_dir,
            output_stem=f"wwtsf_substrate_profile_{profile}_A3",
            config=config,
            system_prompt=(
                "You generate Cartenza WWTSF substrate objects from bounded Atlas substrate. "
                "Return only JSON conforming to the provided schema. Do not create final user copy."
            ),
            user_prompt=rendered_prompt,
            output_schema=schema,
            schema_name="waymark_wwtsf_substrate_v0_1_2",
            dry_run=dry_run,
            pricing=pricing,
            estimate_cost_usd=estimate_cost_usd,
        )
        run_result["profile_id"] = profile_id
        run_result["profile"] = profile
        results.append(run_result)

    combined = {
        "schema_version": "waymark.wwtsf_substrate_smoke_output.v0.1.2",
        "generated_at": _now(),
        "model": config.model,
        "reasoning_effort": config.reasoning_effort,
        "profiles": [
            result.get("parsed_output")
            for result in results
            if isinstance(result.get("parsed_output"), dict)
        ],
    }
    write_json(output_dir / "wwtsf_substrate_smoke_output_v0_1_2.json", combined)
    manifest = _wwtsf_manifest(config, profiles, results, dry_run)
    write_json(output_dir / "wwtsf_substrate_smoke_manifest_v0_1_2.json", manifest)
    _write_combined_report(wwtsf_results=results, mission_results=[], dry_run=dry_run)
    print(f"WWTSF substrate output: {output_dir}")
    print(f"WWTSF substrate report: {output_dir / 'wwtsf_substrate_smoke_report_v0_1_2.md'}")
    return 0 if dry_run or all(result["validation_result"].get("valid") for result in results) else 1


def run_wwtsf_shadow_comparison(
    *,
    profiles: Iterable[str],
    config: OpenAIConfig,
    pricing: Dict[str, Any],
    estimate_cost_usd: CostEstimator,
    dry_run: bool,
) -> int:
    output_dir = A3_WWTSF_SHADOW_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    schema = _load_json(FIXTURES_ROOT / "schemas" / "wwtsf_substrate_output_schema_v0_1_2.json")
    write_json(output_dir / "wwtsf_substrate_shadow_output_schema_v0_1_3.json", schema)

    profile_list = list(profiles)
    results = []
    for profile in profile_list:
        profile_id = _profile_id(profile)
        context_packet = _build_wwtsf_context(profile)
        rendered_prompt = _render_template(
            FIXTURES_ROOT / "prompt_templates" / "wwtsf_substrate_v0_1_2.md",
            {
                "{{PROFILE_ID}}": profile_id,
                "{{CONTEXT_PACKET_JSON}}": json.dumps(context_packet, indent=2, sort_keys=True),
                "{{OUTPUT_SCHEMA_JSON}}": json.dumps(schema, indent=2, sort_keys=True),
            },
        )
        run_result = _run_structured_generation(
            output_dir=output_dir,
            output_stem=f"wwtsf_substrate_profile_{profile}_A3",
            config=config,
            system_prompt=(
                "You generate Cartenza WWTSF substrate objects from bounded Atlas substrate. "
                "Return only JSON conforming to the provided schema. Do not create final user copy."
            ),
            user_prompt=rendered_prompt,
            output_schema=schema,
            schema_name="waymark_wwtsf_substrate_v0_1_2",
            dry_run=dry_run,
            pricing=pricing,
            estimate_cost_usd=estimate_cost_usd,
        )
        run_result["profile_id"] = profile_id
        run_result["profile"] = profile
        results.append(run_result)

    comparisons = _compare_shadow_to_baseline(results, profile_list)
    combined = {
        "schema_version": "waymark.wwtsf_5_4_mini_shadow_comparison_output.v0.1.3",
        "generated_at": _now(),
        "shadow_model": config.model,
        "baseline_model": "gpt-5.5",
        "prompt_template": "wwtsf_substrate_v0_1_2",
        "output_schema": "wwtsf_substrate_output_schema_v0_1_2",
        "profiles": [
            result.get("parsed_output")
            for result in results
            if isinstance(result.get("parsed_output"), dict)
        ],
        "comparisons": comparisons,
    }
    write_json(output_dir / "wwtsf_5_4_mini_shadow_comparison_output_v0_1_3.json", combined)
    manifest = _wwtsf_shadow_manifest(config, profile_list, results, comparisons, dry_run)
    write_json(output_dir / "wwtsf_5_4_mini_shadow_comparison_manifest_v0_1_3.json", manifest)
    _write_wwtsf_shadow_report(results=results, comparisons=comparisons, dry_run=dry_run)
    print(f"WWTSF 5.4-mini shadow output: {output_dir}")
    print(f"WWTSF 5.4-mini shadow report: {output_dir / 'wwtsf_5_4_mini_shadow_comparison_report_v0_1_3.md'}")
    return 0 if dry_run or all(result["validation_result"].get("valid") for result in results) else 1


def run_wwtsf_consistency_guardrail_pass(
    *,
    profiles: Iterable[str],
    config: OpenAIConfig,
    pricing: Dict[str, Any],
    estimate_cost_usd: CostEstimator,
    dry_run: bool,
) -> int:
    output_dir = A3_WWTSF_CONSISTENCY_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    schema = _load_json(FIXTURES_ROOT / "schemas" / "wwtsf_substrate_output_schema_v0_1_2.json")
    write_json(output_dir / "wwtsf_consistency_output_schema_v0_1_4.json", schema)

    requested_profiles = list(profiles)
    ready_profiles, unavailable_requested = _ready_wwtsf_profiles(requested_profiles)
    additional_ready, additional_unavailable = _discover_additional_simulated_profile_status(ready_profiles)
    profile_list = ready_profiles + additional_ready

    results = []
    for profile in profile_list:
        profile_id = _profile_id(profile)
        context_packet = _build_wwtsf_context(profile)
        rendered_prompt = _render_template(
            FIXTURES_ROOT / "prompt_templates" / "wwtsf_substrate_v0_1_2.md",
            {
                "{{PROFILE_ID}}": profile_id,
                "{{CONTEXT_PACKET_JSON}}": json.dumps(context_packet, indent=2, sort_keys=True),
                "{{OUTPUT_SCHEMA_JSON}}": json.dumps(schema, indent=2, sort_keys=True),
            },
        )
        run_result = _run_structured_generation(
            output_dir=output_dir,
            output_stem=f"wwtsf_substrate_profile_{profile}_A3",
            config=config,
            system_prompt=(
                "You generate Cartenza WWTSF substrate objects from bounded Atlas substrate. "
                "Return only JSON conforming to the provided schema. Do not create final user copy."
            ),
            user_prompt=rendered_prompt,
            output_schema=schema,
            schema_name="waymark_wwtsf_substrate_v0_1_2",
            dry_run=dry_run,
            pricing=pricing,
            estimate_cost_usd=estimate_cost_usd,
        )
        run_result["profile_id"] = profile_id
        run_result["profile"] = profile
        run_result["guardrail_result"] = _evaluate_wwtsf_guardrails(profile, run_result.get("parsed_output"))
        write_json(output_dir / f"wwtsf_substrate_profile_{profile}_A3_guardrails.json", run_result["guardrail_result"])
        results.append(run_result)

    tag_fixture_result = _evaluate_tag_bearing_fixture()
    write_json(output_dir / "tag_bearing_fixture_guardrail_v0_1_4.json", tag_fixture_result)

    combined = {
        "schema_version": "waymark.wwtsf_mini_consistency_guardrail_output.v0.1.4",
        "generated_at": _now(),
        "model": config.model,
        "prompt_template": "wwtsf_substrate_v0_1_2",
        "output_schema": "wwtsf_substrate_output_schema_v0_1_2",
        "profiles": [
            result.get("parsed_output")
            for result in results
            if isinstance(result.get("parsed_output"), dict)
        ],
        "guardrail_results": [result["guardrail_result"] for result in results],
        "tag_bearing_fixture_guardrail": tag_fixture_result,
        "additional_profile_status": {
            "requested_unavailable": unavailable_requested,
            "additional_ready": additional_ready,
            "additional_unavailable": additional_unavailable,
        },
    }
    write_json(output_dir / "wwtsf_mini_consistency_guardrail_output_v0_1_4.json", combined)
    manifest = _wwtsf_consistency_manifest(
        config=config,
        profiles=profile_list,
        results=results,
        tag_fixture_result=tag_fixture_result,
        unavailable_requested=unavailable_requested,
        additional_ready=additional_ready,
        additional_unavailable=additional_unavailable,
        dry_run=dry_run,
    )
    write_json(output_dir / "wwtsf_mini_consistency_guardrail_manifest_v0_1_4.json", manifest)
    _write_wwtsf_consistency_report(
        results=results,
        tag_fixture_result=tag_fixture_result,
        unavailable_requested=unavailable_requested,
        additional_ready=additional_ready,
        additional_unavailable=additional_unavailable,
        dry_run=dry_run,
    )
    print(f"WWTSF mini consistency output: {output_dir}")
    print(f"WWTSF mini consistency report: {output_dir / 'wwtsf_mini_consistency_guardrail_report_v0_1_4.md'}")
    all_schema_valid = all(result["validation_result"].get("valid") for result in results)
    return 0 if dry_run or (all_schema_valid and results) else 1


def run_wwtsf_mini_guarded_repair(
    *,
    profiles: Iterable[str],
    config: OpenAIConfig,
    pricing: Dict[str, Any],
    estimate_cost_usd: CostEstimator,
    dry_run: bool,
) -> int:
    output_dir = A3_WWTSF_REPAIR_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    schema = _load_json(FIXTURES_ROOT / "schemas" / "wwtsf_substrate_output_schema_v0_1_2.json")
    write_json(output_dir / "wwtsf_guarded_repair_output_schema_v0_1_5.json", schema)

    requested_profiles = list(profiles)
    ready_profiles, unavailable_requested = _ready_wwtsf_profiles(requested_profiles)
    results = []
    for profile in ready_profiles:
        first_result = _run_guarded_wwtsf_generation(
            profile=profile,
            config=config,
            output_dir=output_dir,
            output_stem=f"wwtsf_guarded_profile_{profile}_A3",
            schema=schema,
            dry_run=dry_run,
            pricing=pricing,
            estimate_cost_usd=estimate_cost_usd,
        )
        first_result["stage"] = "mini_first_pass"
        stage_results = [first_result]
        selected_result = first_result
        fallback_reason = None

        if not dry_run and first_result.get("guardrail_result", {}).get("overall_status") != "guardrail_pass":
            repair_result = _run_wwtsf_repair_generation(
                profile=profile,
                config=config,
                output_dir=output_dir,
                output_stem=f"wwtsf_repaired_profile_{profile}_A3",
                schema=schema,
                failed_result=first_result,
                dry_run=dry_run,
                pricing=pricing,
                estimate_cost_usd=estimate_cost_usd,
            )
            repair_result["stage"] = "mini_repair_pass"
            stage_results.append(repair_result)
            selected_result = repair_result
            if repair_result.get("guardrail_result", {}).get("overall_status") != "guardrail_pass":
                fallback_reason = "mini_repair_failed_guardrails"
                fallback_config = _fallback_config(config)
                fallback_result = _run_guarded_wwtsf_generation(
                    profile=profile,
                    config=fallback_config,
                    output_dir=output_dir,
                    output_stem=f"wwtsf_fallback_gpt_5_5_profile_{profile}_A3",
                    schema=schema,
                    dry_run=dry_run,
                    pricing=pricing,
                    estimate_cost_usd=estimate_cost_usd,
                )
                fallback_result["stage"] = "gpt_5_5_fallback"
                stage_results.append(fallback_result)
                selected_result = fallback_result

        final_result = {
            "profile": profile,
            "profile_id": _profile_id(profile),
            "stage_results": stage_results,
            "selected_stage": selected_result.get("stage"),
            "selected_model": selected_result.get("metadata", {}).get("model"),
            "selected_output_file": selected_result.get("output_file"),
            "selected_validation_result": selected_result.get("validation_result"),
            "selected_guardrail_result": selected_result.get("guardrail_result"),
            "fallback_reason": fallback_reason,
        }
        results.append(final_result)

    tag_fixture_result = _evaluate_tag_bearing_fixture()
    write_json(output_dir / "tag_bearing_fixture_guardrail_v0_1_5.json", tag_fixture_result)
    combined = {
        "schema_version": "waymark.wwtsf_mini_guarded_repair_output.v0.1.5",
        "generated_at": _now(),
        "mini_model": config.model,
        "fallback_model": "gpt-5.5",
        "prompt_template": "wwtsf_substrate_guarded_v0_1_5",
        "repair_prompt_template": "wwtsf_substrate_repair_v0_1_5",
        "output_schema": "wwtsf_substrate_output_schema_v0_1_2",
        "profiles": [
            _load_json(Path(result["selected_output_file"]))
            for result in results
            if result.get("selected_output_file") and Path(result["selected_output_file"]).exists()
        ],
        "profile_results": results,
        "tag_bearing_fixture_guardrail": tag_fixture_result,
        "requested_unavailable": unavailable_requested,
    }
    write_json(output_dir / "wwtsf_mini_guarded_repair_output_v0_1_5.json", combined)
    manifest = _wwtsf_guarded_repair_manifest(
        config=config,
        results=results,
        tag_fixture_result=tag_fixture_result,
        unavailable_requested=unavailable_requested,
        dry_run=dry_run,
    )
    write_json(output_dir / "wwtsf_mini_guarded_repair_manifest_v0_1_5.json", manifest)
    _write_wwtsf_guarded_repair_report(
        results=results,
        tag_fixture_result=tag_fixture_result,
        unavailable_requested=unavailable_requested,
        dry_run=dry_run,
    )
    print(f"WWTSF mini guarded repair output: {output_dir}")
    print(f"WWTSF mini guarded repair report: {output_dir / 'wwtsf_mini_guarded_repair_report_v0_1_5.md'}")
    final_pass = bool(results) and all(
        (result.get("selected_validation_result") or {}).get("valid")
        and (result.get("selected_guardrail_result") or {}).get("overall_status") == "guardrail_pass"
        for result in results
    )
    return 0 if dry_run or final_pass else 1


def run_a3_mission_generation(
    *,
    profiles: Iterable[str],
    config: OpenAIConfig,
    pricing: Dict[str, Any],
    estimate_cost_usd: CostEstimator,
    dry_run: bool,
) -> int:
    output_dir = A3_MISSION_OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    mission_schema = _load_json(FIXTURES_ROOT / "schemas" / "mission_output_schema_v0_1.json")
    scenarios = _select_scenarios(list(profiles))
    results = []
    for scenario in scenarios:
        profile = scenario["profile"]
        profile_id = _profile_id(profile)
        context_packet = _build_mission_context(profile, scenario)
        rendered_prompt = _render_template(
            FIXTURES_ROOT / "prompt_templates" / "a3_mission_generation_v0_1_2.md",
            {
                "{{PROFILE_ID}}": profile_id,
                "{{SCENARIO_ID}}": scenario["scenario_id"],
                "{{MISSION_ARCHETYPE}}": scenario["mission_archetype"],
                "{{SCENARIO_OBJECTIVE}}": scenario["objective"],
                "{{SCENARIO_CONSTRAINTS_JSON}}": json.dumps(scenario["constraints"], indent=2, sort_keys=True),
                "{{CONTEXT_PACKET_JSON}}": json.dumps(context_packet, indent=2, sort_keys=True),
                "{{OUTPUT_SCHEMA_JSON}}": json.dumps(mission_schema, indent=2, sort_keys=True),
            },
        )
        run_result = _run_structured_generation(
            output_dir=output_dir,
            output_stem=f"mission_{scenario['scenario_id']}",
            config=config,
            system_prompt=(
                "You generate Cartenza mission objects from bounded Atlas and WWTSF substrate. "
                "Return only JSON conforming to the provided mission schema."
            ),
            user_prompt=rendered_prompt,
            output_schema=mission_schema,
            schema_name="waymark_mission_output_v0_1",
            dry_run=dry_run,
            pricing=pricing,
            estimate_cost_usd=estimate_cost_usd,
        )
        run_result["profile_id"] = profile_id
        run_result["profile"] = profile
        run_result["scenario"] = scenario
        results.append(run_result)

    combined = {
        "schema_version": "waymark.a3_mission_generation_output.v0.1.2",
        "generated_at": _now(),
        "model": config.model,
        "scenarios": [
            {
                "scenario_id": result["scenario"]["scenario_id"],
                "profile_id": result["profile_id"],
                "output_file": result["output_file"],
                "validation_valid": result["validation_result"].get("valid"),
            }
            for result in results
        ],
    }
    write_json(output_dir / "a3_mission_generation_output_v0_1_2.json", combined)
    manifest = _mission_manifest(config, scenarios, results, dry_run)
    write_json(output_dir / "a3_mission_generation_manifest_v0_1_2.json", manifest)
    wwtsf_results = _load_wwtsf_result_summaries()
    _write_combined_report(wwtsf_results=wwtsf_results, mission_results=results, dry_run=dry_run)
    print(f"A3 mission generation output: {output_dir}")
    print(f"Combined A3 WWTSF/mission report: {A3_WWTSF_OUTPUT_DIR / 'wwtsf_substrate_smoke_report_v0_1_2.md'}")
    return 0 if dry_run or all(result["validation_result"].get("valid") for result in results) else 1


def _run_structured_generation(
    *,
    output_dir: Path,
    output_stem: str,
    config: OpenAIConfig,
    system_prompt: str,
    user_prompt: str,
    output_schema: Dict[str, Any],
    schema_name: str,
    dry_run: bool,
    pricing: Dict[str, Any],
    estimate_cost_usd: CostEstimator,
) -> Dict[str, Any]:
    request_payload = build_request_payload(config, system_prompt, user_prompt, output_schema, schema_name=schema_name)
    write_json(output_dir / f"{output_stem}_request.json", _redact_request_payload(request_payload))
    metadata = {
        "created_at": _now(),
        "model": config.model,
        "api_style": config.api_style,
        "reasoning_effort": config.reasoning_effort,
        "schema_name": schema_name,
        "run_type": "dry_run" if dry_run else "live_api",
    }
    if dry_run:
        write_json(output_dir / f"{output_stem}_metadata.json", metadata)
        return {
            "output_file": str(output_dir / f"{output_stem}.json"),
            "metadata": metadata,
            "validation_result": {"valid": False, "error_count": 0, "errors": ["dry_run"]},
            "metrics": {},
            "parsed_output": None,
            "raw_response": None,
        }

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

    write_json(output_dir / f"{output_stem}_raw_response.json", raw_response)
    if parsed_output is not None:
        write_json(output_dir / f"{output_stem}.json", parsed_output)
    validation_result = (
        validate_json(parsed_output, output_schema)
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
        "pricing_table_version": cost_estimate["pricing_table_version"],
        "pricing_table_date": cost_estimate["pricing_table_date"],
        "latency_seconds": elapsed_seconds,
    }
    metadata.update(metrics)
    metadata["valid"] = validation_result.get("valid")
    if parse_error:
        metadata["error"] = parse_error
    write_json(output_dir / f"{output_stem}_metadata.json", metadata)
    write_json(output_dir / f"{output_stem}_validation.json", validation_result)
    return {
        "output_file": str(output_dir / f"{output_stem}.json"),
        "metadata": metadata,
        "validation_result": validation_result,
        "metrics": metrics,
        "parsed_output": parsed_output,
        "raw_response": raw_response,
    }


def _run_guarded_wwtsf_generation(
    *,
    profile: str,
    config: OpenAIConfig,
    output_dir: Path,
    output_stem: str,
    schema: Dict[str, Any],
    dry_run: bool,
    pricing: Dict[str, Any],
    estimate_cost_usd: CostEstimator,
) -> Dict[str, Any]:
    profile_id = _profile_id(profile)
    context_packet = _build_wwtsf_context(profile)
    context_packet["generation_task"] = "wwtsf_substrate_guarded"
    context_packet["coverage_obligations"] = _coverage_obligations(profile)
    context_packet["coverage_obligation_rules"] = _coverage_obligation_rules()
    rendered_prompt = _render_template(
        FIXTURES_ROOT / "prompt_templates" / "wwtsf_substrate_guarded_v0_1_5.md",
        {
            "{{PROFILE_ID}}": profile_id,
            "{{CONTEXT_PACKET_JSON}}": json.dumps(context_packet, indent=2, sort_keys=True),
            "{{OUTPUT_SCHEMA_JSON}}": json.dumps(schema, indent=2, sort_keys=True),
        },
    )
    run_result = _run_structured_generation(
        output_dir=output_dir,
        output_stem=output_stem,
        config=config,
        system_prompt=(
            "You generate guarded Cartenza WWTSF substrate objects from bounded Atlas substrate. "
            "Preserve coverage obligations or explicitly mark omissions. Return only schema-valid JSON."
        ),
        user_prompt=rendered_prompt,
        output_schema=schema,
        schema_name="waymark_wwtsf_substrate_v0_1_2",
        dry_run=dry_run,
        pricing=pricing,
        estimate_cost_usd=estimate_cost_usd,
    )
    run_result["profile_id"] = profile_id
    run_result["profile"] = profile
    run_result["coverage_obligations"] = context_packet["coverage_obligations"]
    run_result["guardrail_result"] = _evaluate_wwtsf_guardrails(profile, run_result.get("parsed_output"))
    write_json(output_dir / f"{output_stem}_guardrails.json", run_result["guardrail_result"])
    return run_result


def _run_wwtsf_repair_generation(
    *,
    profile: str,
    config: OpenAIConfig,
    output_dir: Path,
    output_stem: str,
    schema: Dict[str, Any],
    failed_result: Dict[str, Any],
    dry_run: bool,
    pricing: Dict[str, Any],
    estimate_cost_usd: CostEstimator,
) -> Dict[str, Any]:
    profile_id = _profile_id(profile)
    repair_packet = _build_wwtsf_repair_packet(profile, failed_result)
    write_json(output_dir / f"{output_stem}_repair_packet.json", repair_packet)
    rendered_prompt = _render_template(
        FIXTURES_ROOT / "prompt_templates" / "wwtsf_substrate_repair_v0_1_5.md",
        {
            "{{PROFILE_ID}}": profile_id,
            "{{REPAIR_PACKET_JSON}}": json.dumps(repair_packet, indent=2, sort_keys=True),
            "{{OUTPUT_SCHEMA_JSON}}": json.dumps(schema, indent=2, sort_keys=True),
        },
    )
    run_result = _run_structured_generation(
        output_dir=output_dir,
        output_stem=output_stem,
        config=config,
        system_prompt=(
            "You repair Cartenza WWTSF substrate objects from bounded repair packets. "
            "Return one complete JSON object conforming to the provided schema."
        ),
        user_prompt=rendered_prompt,
        output_schema=schema,
        schema_name="waymark_wwtsf_substrate_v0_1_2",
        dry_run=dry_run,
        pricing=pricing,
        estimate_cost_usd=estimate_cost_usd,
    )
    run_result["profile_id"] = profile_id
    run_result["profile"] = profile
    run_result["coverage_obligations"] = repair_packet["coverage_obligations"]
    run_result["repair_packet_file"] = str(output_dir / f"{output_stem}_repair_packet.json")
    run_result["guardrail_result"] = _evaluate_wwtsf_guardrails(profile, run_result.get("parsed_output"))
    write_json(output_dir / f"{output_stem}_guardrails.json", run_result["guardrail_result"])
    return run_result


def _fallback_config(config: OpenAIConfig) -> OpenAIConfig:
    return OpenAIConfig(
        model="gpt-5.5",
        api_key=config.api_key,
        api_style=config.api_style,
        base_url=config.base_url,
        temperature=config.temperature,
        max_output_tokens=config.max_output_tokens,
        reasoning_effort=config.reasoning_effort or "medium",
        timeout_seconds=config.timeout_seconds,
    )


def _build_wwtsf_context(profile: str) -> Dict[str, Any]:
    digest_path = A3_INGESTION_DIR / f"atlas_digest_view_profile_{profile}_A3.json"
    node_path = A3_NODE_INTERPRETATION_DIR / f"node_interpretation_smoke_profile_{profile}_A3.json"
    bundle_path = A3_INGESTION_DIR / f"atlas_records_bundle_profile_{profile}_A3.json"
    _require_files([digest_path, node_path, bundle_path, A3_INGESTION_DIR / "role_assignment_policy_v0_1_1.md"])
    digest = _load_json(digest_path)
    node_interpretation = _load_json(node_path)
    return {
        "generation_task": "wwtsf_substrate",
        "profile_id": _profile_id(profile),
        "input_file_refs": {
            "atlas_digest_view": str(digest_path),
            "node_interpretation": str(node_path),
            "atlas_records_bundle": str(bundle_path),
            "role_assignment_policy": str(A3_INGESTION_DIR / "role_assignment_policy_v0_1_1.md"),
        },
        "exclusion_policy": _exclusion_policy(),
        "role_assignment_policy_notes": _load_text(A3_INGESTION_DIR / "role_assignment_policy_v0_1_1.md"),
        "atlas_digest_view": digest,
        "node_interpretation": node_interpretation,
        "anti_overfitting_rules": digest.get("anti_overfitting_rules", []),
        "selected_evidence_refs": _selected_evidence_refs(digest, node_interpretation),
    }


def _build_mission_context(profile: str, scenario: Dict[str, Any]) -> Dict[str, Any]:
    digest_path = A3_INGESTION_DIR / f"atlas_digest_view_profile_{profile}_A3.json"
    node_path = A3_NODE_INTERPRETATION_DIR / f"node_interpretation_smoke_profile_{profile}_A3.json"
    wwtsf_path = A3_WWTSF_OUTPUT_DIR / f"wwtsf_substrate_profile_{profile}_A3.json"
    _require_files([digest_path, node_path, wwtsf_path])
    digest = _load_json(digest_path)
    node_interpretation = _load_json(node_path)
    wwtsf = _load_json(wwtsf_path)
    return {
        "generation_task": "mission_generation",
        "profile_id": _profile_id(profile),
        "scenario": scenario,
        "input_file_refs": {
            "atlas_digest_view": str(digest_path),
            "node_interpretation": str(node_path),
            "wwtsf_substrate": str(wwtsf_path),
        },
        "exclusion_policy": _exclusion_policy(),
        "atlas_digest_view": digest,
        "node_interpretation": node_interpretation,
        "wwtsf_substrate": wwtsf,
        "anti_overfitting_rules": digest.get("anti_overfitting_rules", []),
        "selected_evidence_refs": wwtsf.get("evidence_refs", []),
    }


def _select_scenarios(profiles: List[str]) -> List[Dict[str, Any]]:
    scenarios: List[Dict[str, Any]] = []
    for profile in profiles:
        scenarios.append(
            {
                "scenario_id": f"first_mission_profile_{profile}_A3",
                "profile": profile,
                "mission_archetype": "Start Here / First Mission",
                "objective": "Create a first mission from provisional Atlas and WWTSF substrate.",
                "constraints": [
                    "Use first_mission_input_hints.",
                    "Preserve uncertainty.",
                    "Do not promote Atlas truth.",
                    "Use expected signals and feedback chips to collect evidence.",
                ],
            }
        )
        scenarios.append(
            {
                "scenario_id": f"waypoint_route_profile_{profile}_A3",
                "profile": profile,
                "mission_archetype": "Waypoint Route / Use-Case Route",
                "objective": "Test whether useful/contextual Waypoints can form routes without becoming canon.",
                "constraints": [
                    "Frame route as useful/contextual.",
                    "Do not turn Keep/OK evidence into Landmark evidence.",
                    "Use waypoint and bridge semantics.",
                ],
            }
        )
    scenarios.extend(
        [
            {
                "scenario_id": "dense_region_reinforcement_profile_05_A3",
                "profile": "05",
                "mission_archetype": "Nearby Road / Region Density Test",
                "objective": "Use the densest positive cluster to deepen known territory rather than treating every node as discovery.",
                "constraints": [
                    "Mostly safe route.",
                    "Include a few boundary probes.",
                    "Do not frame dense positives as raw frontier discovery.",
                ],
            },
            {
                "scenario_id": "isolated_love_frontier_profile_06_A3",
                "profile": "06",
                "mission_archetype": "Frontier Route",
                "objective": "Treat a strong sparse positive as promising but underexplored.",
                "constraints": [
                    "Do not create Landmark claims from isolated love.",
                    "Test nearby territory cautiously.",
                    "Preserve scope and confidence.",
                ],
            },
            {
                "scenario_id": "contradiction_scope_check_profile_01_A3",
                "profile": "01",
                "mission_archetype": "Correction Route / Dead End Check / Artist Calibration",
                "objective": "Turn contradictions into a scoped review mission rather than a collapsed verdict.",
                "constraints": [
                    "Test contradiction directly.",
                    "Keep object scope clear.",
                    "Avoid broad genre rejection.",
                    "Explain what each route item clarifies.",
                ],
            },
        ]
    )
    return [scenario for scenario in scenarios if scenario["profile"] in profiles]


def _selected_evidence_refs(digest: Dict[str, Any], node_interpretation: Dict[str, Any]) -> List[Dict[str, Any]]:
    refs: List[Dict[str, Any]] = []
    for signal in digest.get("signal_summaries", [])[:20]:
        refs.append(
            {
                "source_type": "signal",
                "source_record_id": signal.get("signal_id", ""),
                "summary": signal.get("summary") or signal.get("display_name") or str(signal)[:180],
            }
        )
    for candidate in node_interpretation.get("possible_update_candidates", [])[:12]:
        refs.append(
            {
                "source_type": "possible_update_candidate",
                "source_record_id": candidate.get("candidate_id", ""),
                "summary": candidate.get("reasoning_summary", ""),
            }
        )
    return refs


def _wwtsf_manifest(config: OpenAIConfig, profiles: Iterable[str], results: List[Dict[str, Any]], dry_run: bool) -> Dict[str, Any]:
    return {
        "schema_version": "waymark.wwtsf_substrate_smoke_manifest.v0.1.2",
        "generated_at": _now(),
        "generation_task": "wwtsf_substrate",
        "run_type": "dry_run" if dry_run else "live_api",
        "model": config.model,
        "reasoning_effort": config.reasoning_effort,
        "prompt_template": "wwtsf_substrate_v0_1_2",
        "output_schema": "wwtsf_substrate_output_schema_v0_1_2",
        "profiles": list(profiles),
        "input_roots": {
            "ingestion_proof": str(A3_INGESTION_DIR),
            "node_interpretation": str(A3_NODE_INTERPRETATION_DIR),
        },
        "exclusions": _exclusion_policy(),
        "profile_results": _manifest_results(results),
    }


def _mission_manifest(config: OpenAIConfig, scenarios: List[Dict[str, Any]], results: List[Dict[str, Any]], dry_run: bool) -> Dict[str, Any]:
    return {
        "schema_version": "waymark.a3_mission_generation_manifest.v0.1.2",
        "generated_at": _now(),
        "generation_task": "mission_generation",
        "run_type": "dry_run" if dry_run else "live_api",
        "model": config.model,
        "prompt_template": "a3_mission_generation_v0_1_2",
        "output_schema": "mission_output_schema_v0_1",
        "scenario_ids": [scenario["scenario_id"] for scenario in scenarios],
        "input_roots": {
            "ingestion_proof": str(A3_INGESTION_DIR),
            "node_interpretation": str(A3_NODE_INTERPRETATION_DIR),
            "wwtsf_substrate": str(A3_WWTSF_OUTPUT_DIR),
        },
        "exclusions": _exclusion_policy(),
        "scenario_results": _manifest_results(results),
    }


def _wwtsf_shadow_manifest(
    config: OpenAIConfig,
    profiles: List[str],
    results: List[Dict[str, Any]],
    comparisons: List[Dict[str, Any]],
    dry_run: bool,
) -> Dict[str, Any]:
    return {
        "schema_version": "waymark.wwtsf_5_4_mini_shadow_comparison_manifest.v0.1.3",
        "generated_at": _now(),
        "generation_task": "wwtsf_shadow_comparison",
        "run_type": "dry_run" if dry_run else "live_api",
        "shadow_model": config.model,
        "baseline_model": "gpt-5.5",
        "prompt_template": "wwtsf_substrate_v0_1_2",
        "output_schema": "wwtsf_substrate_output_schema_v0_1_2",
        "profiles": profiles,
        "baseline_root": str(A3_WWTSF_OUTPUT_DIR),
        "shadow_root": str(A3_WWTSF_SHADOW_DIR),
        "input_roots": {
            "ingestion_proof": str(A3_INGESTION_DIR),
            "node_interpretation": str(A3_NODE_INTERPRETATION_DIR),
        },
        "exclusions": _exclusion_policy(),
        "profile_results": _manifest_results(results),
        "comparisons": comparisons,
    }


def _wwtsf_consistency_manifest(
    *,
    config: OpenAIConfig,
    profiles: List[str],
    results: List[Dict[str, Any]],
    tag_fixture_result: Dict[str, Any],
    unavailable_requested: List[Dict[str, str]],
    additional_ready: List[str],
    additional_unavailable: List[Dict[str, str]],
    dry_run: bool,
) -> Dict[str, Any]:
    return {
        "schema_version": "waymark.wwtsf_mini_consistency_guardrail_manifest.v0.1.4",
        "generated_at": _now(),
        "generation_task": "wwtsf_mini_consistency_guardrail_pass",
        "run_type": "dry_run" if dry_run else "live_api",
        "model": config.model,
        "baseline_model": "gpt-5.5",
        "baseline_role": "review_baseline_and_adjudicator",
        "prompt_template": "wwtsf_substrate_v0_1_2",
        "output_schema": "wwtsf_substrate_output_schema_v0_1_2",
        "profiles": profiles,
        "baseline_root": str(A3_WWTSF_OUTPUT_DIR),
        "consistency_root": str(A3_WWTSF_CONSISTENCY_DIR),
        "input_roots": {
            "ingestion_proof": str(A3_INGESTION_DIR),
            "node_interpretation": str(A3_NODE_INTERPRETATION_DIR),
        },
        "exclusions": _exclusion_policy(),
        "profile_results": [
            {
                **entry,
                "guardrail_status": result.get("guardrail_result", {}).get("overall_status"),
                "mini_default_eligible": result.get("guardrail_result", {}).get("mini_default_eligible"),
            }
            for result, entry in zip(results, _manifest_results(results))
        ],
        "tag_bearing_fixture_guardrail": tag_fixture_result,
        "requested_unavailable": unavailable_requested,
        "additional_ready": additional_ready,
        "additional_unavailable": additional_unavailable,
    }


def _wwtsf_guarded_repair_manifest(
    *,
    config: OpenAIConfig,
    results: List[Dict[str, Any]],
    tag_fixture_result: Dict[str, Any],
    unavailable_requested: List[Dict[str, str]],
    dry_run: bool,
) -> Dict[str, Any]:
    return {
        "schema_version": "waymark.wwtsf_mini_guarded_repair_manifest.v0.1.5",
        "generated_at": _now(),
        "generation_task": "wwtsf_mini_guarded_repair",
        "run_type": "dry_run" if dry_run else "live_api",
        "mini_model": config.model,
        "fallback_model": "gpt-5.5",
        "prompt_template": "wwtsf_substrate_guarded_v0_1_5",
        "repair_prompt_template": "wwtsf_substrate_repair_v0_1_5",
        "output_schema": "wwtsf_substrate_output_schema_v0_1_2",
        "output_root": str(A3_WWTSF_REPAIR_DIR),
        "input_roots": {
            "ingestion_proof": str(A3_INGESTION_DIR),
            "node_interpretation": str(A3_NODE_INTERPRETATION_DIR),
        },
        "exclusions": _exclusion_policy(),
        "profile_results": [
            {
                "profile_id": result.get("profile_id"),
                "selected_stage": result.get("selected_stage"),
                "selected_model": result.get("selected_model"),
                "selected_output_file": result.get("selected_output_file"),
                "selected_schema_valid": (result.get("selected_validation_result") or {}).get("valid"),
                "selected_guardrail_status": (result.get("selected_guardrail_result") or {}).get("overall_status"),
                "fallback_reason": result.get("fallback_reason"),
                "stage_results": [
                    {
                        "stage": stage.get("stage"),
                        "model": stage.get("metadata", {}).get("model"),
                        "valid": stage.get("validation_result", {}).get("valid"),
                        "guardrail_status": stage.get("guardrail_result", {}).get("overall_status"),
                        "output_file": stage.get("output_file"),
                        "input_tokens": stage.get("metrics", {}).get("input_tokens"),
                        "output_tokens": stage.get("metrics", {}).get("output_tokens"),
                        "estimated_total_cost_usd": stage.get("metrics", {}).get("estimated_total_cost_usd"),
                        "latency_seconds": stage.get("metrics", {}).get("latency_seconds"),
                    }
                    for stage in result.get("stage_results", [])
                ],
            }
            for result in results
        ],
        "tag_bearing_fixture_guardrail": tag_fixture_result,
        "requested_unavailable": unavailable_requested,
    }


def _manifest_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    manifest_results = []
    for result in results:
        manifest_results.append(
            {
                "profile_id": result.get("profile_id"),
                "scenario_id": (result.get("scenario") or {}).get("scenario_id"),
                "output_file": result.get("output_file"),
                "valid": result.get("validation_result", {}).get("valid"),
                "error_count": result.get("validation_result", {}).get("error_count"),
                "input_tokens": result.get("metrics", {}).get("input_tokens"),
                "output_tokens": result.get("metrics", {}).get("output_tokens"),
                "estimated_total_cost_usd": result.get("metrics", {}).get("estimated_total_cost_usd"),
                "latency_seconds": result.get("metrics", {}).get("latency_seconds"),
            }
        )
    return manifest_results


def _load_wwtsf_result_summaries() -> List[Dict[str, Any]]:
    results = []
    for profile in PROFILES:
        output_file = A3_WWTSF_OUTPUT_DIR / f"wwtsf_substrate_profile_{profile}_A3.json"
        validation_file = A3_WWTSF_OUTPUT_DIR / f"wwtsf_substrate_profile_{profile}_A3_validation.json"
        metadata_file = A3_WWTSF_OUTPUT_DIR / f"wwtsf_substrate_profile_{profile}_A3_metadata.json"
        if not output_file.exists():
            continue
        results.append(
            {
                "profile": profile,
                "profile_id": _profile_id(profile),
                "output_file": str(output_file),
                "parsed_output": _load_json(output_file),
                "validation_result": _load_json(validation_file) if validation_file.exists() else {"valid": None},
                "metadata": _load_json(metadata_file) if metadata_file.exists() else {},
                "metrics": _load_json(metadata_file) if metadata_file.exists() else {},
            }
        )
    return results


def _ready_wwtsf_profiles(profiles: List[str]) -> tuple[List[str], List[Dict[str, str]]]:
    ready = []
    unavailable = []
    for profile in profiles:
        missing = _missing_wwtsf_input_files(profile)
        if missing:
            unavailable.append({"profile": profile, "reason": "missing_wwtsf_input_files", "missing": "; ".join(missing)})
        else:
            ready.append(profile)
    return ready, unavailable


def _discover_additional_simulated_profile_status(existing_ready: List[str]) -> tuple[List[str], List[Dict[str, str]]]:
    fake_profile_dir = REPO_ROOT / "data" / "survey_simulation" / "fake_profiles"
    if not fake_profile_dir.exists():
        return [], [{"profile": "survey_simulation/fake_profiles", "reason": "fake_profile_directory_missing"}]
    ready = []
    unavailable = []
    seen = set(existing_ready)
    for path in sorted(fake_profile_dir.glob("fake_profile_*.json")):
        profile = path.stem.replace("fake_profile_", "")
        if profile in seen:
            continue
        missing = _missing_wwtsf_input_files(profile)
        if missing:
            unavailable.append(
                {
                    "profile": profile,
                    "source_file": str(path),
                    "reason": "not_ready_for_wwtsf_generation",
                    "missing": "; ".join(missing),
                }
            )
        else:
            ready.append(profile)
            seen.add(profile)
    return ready, unavailable


def _missing_wwtsf_input_files(profile: str) -> List[str]:
    paths = [
        A3_INGESTION_DIR / f"atlas_digest_view_profile_{profile}_A3.json",
        A3_NODE_INTERPRETATION_DIR / f"node_interpretation_smoke_profile_{profile}_A3.json",
        A3_INGESTION_DIR / f"atlas_records_bundle_profile_{profile}_A3.json",
        A3_INGESTION_DIR / "role_assignment_policy_v0_1_1.md",
    ]
    return [str(path) for path in paths if not path.exists()]


def _coverage_obligations(profile: str) -> Dict[str, Any]:
    digest = _load_json(A3_INGESTION_DIR / f"atlas_digest_view_profile_{profile}_A3.json")
    node = _load_json(A3_NODE_INTERPRETATION_DIR / f"node_interpretation_smoke_profile_{profile}_A3.json")
    baseline_path = A3_WWTSF_OUTPUT_DIR / f"wwtsf_substrate_profile_{profile}_A3.json"
    baseline = _load_json(baseline_path) if baseline_path.exists() else {}
    expected = _guardrail_expected_targets(digest, node, baseline)
    required_candidate_regions = _dedupe(expected["node_region_labels"] + expected["baseline_candidate_region_labels"])
    required_hint_types = expected["expected_hint_types"]
    minimum_hint_count = max(1, min(4, len(required_hint_types))) if required_hint_types else 1
    return {
        "profile_id": _profile_id(profile),
        "required_candidate_regions": required_candidate_regions,
        "required_frontier_labels": _dedupe(expected["node_frontier_labels"]),
        "required_waypoint_labels": _dedupe(expected["node_waypoint_labels"]),
        "required_contradiction_labels": _dedupe(expected["node_contradiction_labels"]),
        "required_mission_hint_types": required_hint_types,
        "minimum_hint_count": minimum_hint_count,
        "omission_policy": "Emit the required category, or add an explicit omitted_with_reason entry in the closest existing schema field.",
    }


def _coverage_obligation_rules() -> List[str]:
    return [
        "No silent drops: required categories must be emitted or explicitly omitted_with_reason.",
        "Candidate-region obligations belong in candidate_regions unless bounded evidence does not support that category.",
        "Mission-hint type obligations belong in first_mission_input_hints.",
        "Omission reasons must stay provisional and evidence-scoped.",
        "Omission reasons are review-needed and do not promote Atlas truth.",
    ]


def _build_wwtsf_repair_packet(profile: str, failed_result: Dict[str, Any]) -> Dict[str, Any]:
    failed_guardrail = failed_result.get("guardrail_result") or {}
    coverage = _coverage_obligations(profile)
    missing_requirements = _missing_requirements_from_guardrail(failed_guardrail, coverage)
    return {
        "generation_task": "wwtsf_substrate_targeted_repair",
        "profile_id": _profile_id(profile),
        "exclusion_policy": _exclusion_policy(),
        "coverage_obligations": coverage,
        "coverage_obligation_rules": _coverage_obligation_rules(),
        "failed_guardrail_report": failed_guardrail,
        "missing_requirements": missing_requirements,
        "original_mini_output": failed_result.get("parsed_output"),
        "relevant_source_snippets": _repair_relevant_source_snippets(profile, coverage, missing_requirements),
    }


def _missing_requirements_from_guardrail(guardrail: Dict[str, Any], coverage: Dict[str, Any]) -> Dict[str, Any]:
    missing: Dict[str, Any] = {}
    categories = guardrail.get("categories") or {}
    for category_id, category in categories.items():
        failed = [check for check in category.get("checks", []) if not check.get("passed")]
        if failed:
            missing[category_id] = failed
    if "candidate_region_preservation" in missing:
        missing["required_candidate_regions"] = coverage.get("required_candidate_regions", [])
    if "frontier_coverage" in missing:
        missing["required_frontier_labels"] = coverage.get("required_frontier_labels", [])
    if "contradiction_coverage" in missing:
        missing["required_contradiction_labels"] = coverage.get("required_contradiction_labels", [])
    if "mission_hint_completeness" in missing:
        missing["required_mission_hint_types"] = coverage.get("required_mission_hint_types", [])
        missing["minimum_hint_count"] = coverage.get("minimum_hint_count")
    return missing


def _repair_relevant_source_snippets(profile: str, coverage: Dict[str, Any], missing_requirements: Dict[str, Any]) -> Dict[str, Any]:
    digest = _load_json(A3_INGESTION_DIR / f"atlas_digest_view_profile_{profile}_A3.json")
    node = _load_json(A3_NODE_INTERPRETATION_DIR / f"node_interpretation_smoke_profile_{profile}_A3.json")
    required_labels = _dedupe(
        coverage.get("required_candidate_regions", [])
        + coverage.get("required_frontier_labels", [])
        + coverage.get("required_waypoint_labels", [])
        + coverage.get("required_contradiction_labels", [])
    )
    return {
        "input_file_refs": {
            "atlas_digest_view": str(A3_INGESTION_DIR / f"atlas_digest_view_profile_{profile}_A3.json"),
            "node_interpretation": str(A3_NODE_INTERPRETATION_DIR / f"node_interpretation_smoke_profile_{profile}_A3.json"),
            "role_assignment_policy": str(A3_INGESTION_DIR / "role_assignment_policy_v0_1_1.md"),
        },
        "candidate_pool_behavior_hints": _filter_relevant_items(digest.get("candidate_pool_behavior_hints", []), required_labels),
        "suggested_candidate_roles": _filter_relevant_items(digest.get("suggested_candidate_roles", []), required_labels),
        "contradiction_explanations": _filter_relevant_items(node.get("contradiction_explanations", []), required_labels),
        "first_mission_hint_candidates": node.get("first_mission_hint_candidates", []),
        "possible_update_candidates": _filter_relevant_items(node.get("possible_update_candidates", []), required_labels),
        "mission_relevant_constraints": digest.get("mission_relevant_constraints", []),
        "unresolved_questions": digest.get("unresolved_questions", []),
        "anti_overfitting_rules": digest.get("anti_overfitting_rules", []),
        "missing_requirements_summary": missing_requirements,
    }


def _filter_relevant_items(items: List[Dict[str, Any]], labels: List[str]) -> List[Dict[str, Any]]:
    if not labels:
        return items[:12]
    relevant = []
    for item in items:
        item_text = _json_text(item)
        if any(_label_present(label, item_text) for label in labels):
            relevant.append(item)
    return relevant[:20]


def _evaluate_wwtsf_guardrails(profile: str, output: Any) -> Dict[str, Any]:
    profile_id = _profile_id(profile)
    if not isinstance(output, dict):
        return {
            "profile_id": profile_id,
            "overall_status": "guardrail_fail",
            "mini_default_eligible": False,
            "failure_reason": "No parsed WWTSF output.",
            "categories": {},
        }

    digest = _load_json(A3_INGESTION_DIR / f"atlas_digest_view_profile_{profile}_A3.json")
    node = _load_json(A3_NODE_INTERPRETATION_DIR / f"node_interpretation_smoke_profile_{profile}_A3.json")
    baseline_path = A3_WWTSF_OUTPUT_DIR / f"wwtsf_substrate_profile_{profile}_A3.json"
    baseline = _load_json(baseline_path) if baseline_path.exists() else {}
    expected = _guardrail_expected_targets(digest, node, baseline)
    categories = {
        "candidate_region_preservation": _guardrail_candidate_region_preservation(output, expected),
        "frontier_coverage": _guardrail_frontier_coverage(output, expected),
        "contradiction_coverage": _guardrail_contradiction_coverage(output, expected),
        "mission_hint_completeness": _guardrail_mission_hint_completeness(output, expected),
        "scope_and_exclusion_integrity": _guardrail_scope_and_exclusion_integrity(output),
    }
    statuses = [category["status"] for category in categories.values()]
    explicit_omissions = _explicit_omissions(output)
    if all(status == "pass" for status in statuses):
        overall_status = "guardrail_review_needed" if explicit_omissions else "guardrail_pass"
    elif any(status == "fail" for status in statuses):
        overall_status = "guardrail_fail"
    else:
        overall_status = "guardrail_review_needed"
    return {
        "profile_id": profile_id,
        "overall_status": overall_status,
        "mini_default_eligible": overall_status == "guardrail_pass" and not explicit_omissions,
        "explicit_omissions": explicit_omissions,
        "expected_summary": {
            key: value
            for key, value in expected.items()
            if key.endswith("_labels") or key.endswith("_types") or key.endswith("_expected")
        },
        "output_counts": {
            "known_anchors": len(output.get("known_anchors", [])),
            "candidate_regions": len(output.get("candidate_regions", [])),
            "candidate_frontiers": len(output.get("candidate_frontiers", [])),
            "candidate_dead_end_hypotheses": len(output.get("candidate_dead_end_hypotheses", [])),
            "waypoint_notes": len(output.get("waypoint_notes", [])),
            "contradictions_or_review_needs": len(output.get("contradictions_or_review_needs", [])),
            "first_mission_input_hints": len(output.get("first_mission_input_hints", [])),
        },
        "categories": categories,
    }


def _guardrail_expected_targets(digest: Dict[str, Any], node: Dict[str, Any], baseline: Dict[str, Any]) -> Dict[str, Any]:
    digest_hints = digest.get("candidate_pool_behavior_hints", [])
    possible_candidates = node.get("possible_update_candidates", [])
    contradiction_explanations = node.get("contradiction_explanations", [])
    first_hints = node.get("first_mission_hint_candidates", [])
    node_hint_types = [
        hint.get("type")
        for hint in first_hints
        if isinstance(hint, dict) and hint.get("type")
    ]
    candidate_hint_types = [
        candidate.get("mission_hint", {}).get("type")
        for candidate in possible_candidates
        if isinstance(candidate.get("mission_hint"), dict) and candidate.get("mission_hint", {}).get("type")
    ]
    return {
        "landmark_labels": _labels_from_items([item for item in digest_hints if item.get("role") == "landmark"]),
        "digest_frontier_labels": _labels_from_items([item for item in digest_hints if item.get("role") == "frontier"]),
        "digest_waypoint_labels": _labels_from_items([item for item in digest_hints if item.get("role") == "waypoint"]),
        "digest_dead_end_labels": _labels_from_items([item for item in digest_hints if item.get("role") == "dead_end"]),
        "node_frontier_labels": _labels_from_items([item for item in possible_candidates if item.get("candidate_type") == "frontier_hypothesis"]),
        "node_region_labels": _labels_from_items(
            [
                item
                for item in possible_candidates
                if item.get("candidate_type") == "landmark_reinforcement"
                and (item.get("mission_hint") or {}).get("type") == "region_density_test"
            ]
        ),
        "node_contradiction_labels": _labels_from_items(contradiction_explanations)
        + _labels_from_items([item for item in possible_candidates if item.get("candidate_type") == "contradiction_cluster"]),
        "node_dead_end_labels": _labels_from_items([item for item in possible_candidates if item.get("candidate_type") == "dead_end_hypothesis"]),
        "node_waypoint_labels": _labels_from_items([item for item in possible_candidates if item.get("candidate_type") in {"waypoint_hypothesis", "scope_warning"}]),
        "baseline_candidate_region_labels": _labels_from_items(baseline.get("candidate_regions", [])),
        "baseline_frontier_labels": _labels_from_items(baseline.get("candidate_frontiers", [])),
        "baseline_hint_count": len(baseline.get("first_mission_input_hints", [])),
        "candidate_region_expected": bool(
            baseline.get("candidate_regions")
            or [
                item
                for item in possible_candidates
                if item.get("candidate_type") == "landmark_reinforcement"
                and (item.get("mission_hint") or {}).get("type") == "region_density_test"
            ]
        ),
        "expected_hint_types": sorted(set(value for value in node_hint_types + candidate_hint_types if value)),
    }


def _guardrail_candidate_region_preservation(output: Dict[str, Any], expected: Dict[str, Any]) -> Dict[str, Any]:
    anchor_region_items = output.get("known_anchors", []) + output.get("candidate_regions", [])
    anchor_region_text = _json_text(anchor_region_items + output.get("provisional_summary_bullets", []))
    omission_text = _json_text(output.get("contradictions_or_review_needs", []) + output.get("first_mission_input_hints", []))
    landmark_labels = expected["landmark_labels"]
    region_labels = expected["node_region_labels"] + expected["baseline_candidate_region_labels"]
    region_omitted_with_reason = _has_omission_reason(output, "candidate_regions") or any(_label_present(label, omission_text) and "omitted with reason" in _normalize_text(omission_text) for label in region_labels)
    checks = [
        _check("anchor_or_region_present", not landmark_labels or bool(anchor_region_items)),
        _check("candidate_pool_behavior_present", _items_have_key(anchor_region_items, "candidate_pool_behavior")),
        _check(
            "candidate_region_preserved_when_expected",
            not expected["candidate_region_expected"] or bool(output.get("candidate_regions")) or region_omitted_with_reason,
            {"explicit_omission": region_omitted_with_reason},
        ),
        _check(
            "region_or_dense_labels_mentioned",
            not region_labels or bool(_matched_labels(region_labels, anchor_region_text)) or region_omitted_with_reason,
            {"expected_labels": region_labels, "matched_labels": _matched_labels(region_labels, anchor_region_text)},
        ),
        _check(
            "landmark_label_recall_at_least_half",
            not landmark_labels or _label_recall(landmark_labels, anchor_region_text) >= 0.5,
            {"expected_labels": landmark_labels, "recall": _label_recall(landmark_labels, anchor_region_text)},
        ),
    ]
    return _guardrail_category("Candidate-region preservation", checks)


def _guardrail_frontier_coverage(output: Dict[str, Any], expected: Dict[str, Any]) -> Dict[str, Any]:
    frontier_items = output.get("candidate_frontiers", [])
    frontier_text = _json_text(frontier_items + output.get("first_mission_input_hints", []) + output.get("provisional_summary_bullets", []))
    node_frontier_labels = expected["node_frontier_labels"]
    digest_frontier_labels = expected["digest_frontier_labels"]
    minimum_count = max(1, min(len(digest_frontier_labels), max(1, len(node_frontier_labels)))) if digest_frontier_labels or node_frontier_labels else 0
    checks = [
        _check("frontiers_present_when_expected", minimum_count == 0 or len(frontier_items) >= minimum_count),
        _check("frontier_items_have_probe_behavior", _items_have_behavior(frontier_items, {"probe", "risky_probe", "bridge"})),
        _check(
            "node_frontier_labels_preserved",
            not node_frontier_labels or bool(_matched_labels(node_frontier_labels, frontier_text)),
            {"expected_labels": node_frontier_labels, "matched_labels": _matched_labels(node_frontier_labels, frontier_text)},
        ),
        _check("frontier_language_preserves_uncertainty", "frontier" in frontier_text and ("scope" in frontier_text or "provisional" in frontier_text or "test" in frontier_text)),
    ]
    return _guardrail_category("Frontier coverage", checks)


def _guardrail_contradiction_coverage(output: Dict[str, Any], expected: Dict[str, Any]) -> Dict[str, Any]:
    contradiction_items = output.get("contradictions_or_review_needs", [])
    contradiction_text = _json_text(contradiction_items)
    required_labels = expected["node_contradiction_labels"]
    checks = [
        _check("contradictions_present_when_expected", not required_labels or len(contradiction_items) >= max(1, len(set(required_labels)) // 2)),
        _check(
            "required_contradiction_labels_preserved",
            not required_labels or bool(_matched_labels(required_labels, contradiction_text)),
            {"expected_labels": required_labels, "matched_labels": _matched_labels(required_labels, contradiction_text)},
        ),
        _check("contradictions_have_mission_test_hints", _items_have_key(contradiction_items, "mission_test_hint")),
        _check("contradictions_have_review_rationale", _items_have_key(contradiction_items, "why_it_needs_review")),
    ]
    return _guardrail_category("Contradiction coverage", checks)


def _guardrail_mission_hint_completeness(output: Dict[str, Any], expected: Dict[str, Any]) -> Dict[str, Any]:
    hints = output.get("first_mission_input_hints", [])
    hint_text = _json_text(hints)
    expected_types = expected["expected_hint_types"]
    type_checks = {
        "contradiction_test": "contradiction" in hint_text or "correction" in hint_text,
        "frontier_probe": "frontier" in hint_text,
        "waypoint_bridge_test": "waypoint" in hint_text or "bridge" in hint_text,
        "dead_end_check": "dead" in hint_text or "trap" in hint_text,
        "region_density_test": "density" in hint_text or "region" in hint_text,
        "artist_calibration": "artist" in hint_text or "calibration" in hint_text,
    }
    missing_types = [
        hint_type
        for hint_type in expected_types
        if not type_checks.get(hint_type, hint_type.replace("_", " ") in hint_text)
        and not _has_omission_reason(output, hint_type)
    ]
    minimum_hint_count = max(1, min(4, len(expected_types))) if expected_types else 1
    checks = [
        _check("minimum_hint_count_met", len(hints) >= minimum_hint_count, {"minimum": minimum_hint_count, "actual": len(hints)}),
        _check("expected_hint_types_covered", not missing_types, {"expected_types": expected_types, "missing_types": missing_types}),
        _check("hints_have_prompt_seed", _items_have_key(hints, "prompt_seed")),
        _check("hints_have_objective", _items_have_key(hints, "objective")),
        _check("hints_have_caution_notes", _items_have_non_empty_list(hints, "caution_notes")),
    ]
    return _guardrail_category("Mission-hint completeness", checks)


def _guardrail_scope_and_exclusion_integrity(output: Dict[str, Any]) -> Dict[str, Any]:
    exclusions = output.get("exclusion_confirmations") or {}
    text = _json_text(output)
    checks = [
        _check("not_final_user_copy_true", output.get("not_final_user_copy") is True),
        _check("exclusions_all_false", bool(exclusions) and all(value is False for value in exclusions.values())),
        _check("scope_limits_present", len(output.get("scope_limits", [])) >= 3),
        _check("confidence_warnings_present", len(output.get("confidence_warnings", [])) >= 2),
        _check("no_canonical_mutation_language", "canonical graph mutation allowed\": true" not in text),
    ]
    return _guardrail_category("Scope and exclusion integrity", checks)


def _has_omission_reason(output: Dict[str, Any], category_or_label: str) -> bool:
    omission_text = _normalize_text(_json_text(output.get("contradictions_or_review_needs", []) + output.get("first_mission_input_hints", [])))
    needle = _normalize_text(category_or_label)
    return "omitted with reason" in omission_text and (not needle or needle in omission_text)


def _explicit_omissions(output: Dict[str, Any]) -> List[str]:
    omissions = []
    for item in output.get("contradictions_or_review_needs", []):
        if isinstance(item, dict) and "omitted_with_reason" in _json_text(item):
            omissions.append(item.get("label") or item.get("mission_test_hint") or "omitted_with_reason")
    for hint in output.get("first_mission_input_hints", []):
        if isinstance(hint, dict) and "omitted_with_reason" in _json_text(hint):
            omissions.append(hint.get("prompt_seed") or hint.get("hint_id") or "omitted_with_reason")
    return omissions


def _evaluate_tag_bearing_fixture() -> Dict[str, Any]:
    path = A3_INGESTION_DIR / "tag_bearing_signal_sample_v0_1_1.json"
    if not path.exists():
        return {
            "fixture": str(path),
            "status": "not_available",
            "mini_default_eligible": False,
            "checks": [_check("fixture_exists", False)],
        }
    fixture = _load_json(path)
    records = fixture.get("records", []) if isinstance(fixture, dict) else []
    signal_records = [record for record in records if isinstance(record, dict) and record.get("record_type") == "signal"]
    checks = [
        _check("fixture_exists", True),
        _check("has_signal_record", bool(signal_records)),
        _check("selected_tags_preserved", any(record.get("observed_user_tags") for record in signal_records)),
        _check("shown_unselected_tags_preserved", any(record.get("shown_unselected_tags") for record in signal_records)),
        _check(
            "signal_strength_separate_from_interpretation_confidence",
            any(record.get("signal_strength") != record.get("interpretation_confidence") for record in signal_records),
        ),
        _check(
            "apple_exposure_not_taste_truth",
            any((record.get("apple_exposure_context") or {}).get("context_type") == "exposure_import_familiarity_not_taste_truth" for record in signal_records),
        ),
        _check("no_direct_update_candidates_from_tag_fixture", all(not record.get("derived_update_candidate_ids") for record in signal_records)),
    ]
    category = _guardrail_category("Tag-bearing fixture preservation", checks)
    return {
        "fixture": str(path),
        "schema_version": fixture.get("schema_version") if isinstance(fixture, dict) else None,
        "example_name": fixture.get("example_name") if isinstance(fixture, dict) else None,
        "status": category["status"],
        "mini_default_eligible": category["status"] == "pass",
        "checks": checks,
    }


def _guardrail_category(name: str, checks: List[Dict[str, Any]]) -> Dict[str, Any]:
    passed = sum(1 for check in checks if check["passed"])
    if passed == len(checks):
        status = "pass"
    elif passed == 0 or any(not check["passed"] and check["name"] in {"candidate_region_preserved_when_expected", "expected_hint_types_covered", "required_contradiction_labels_preserved"} for check in checks):
        status = "fail"
    else:
        status = "review_needed"
    return {
        "name": name,
        "status": status,
        "passed_checks": passed,
        "total_checks": len(checks),
        "checks": checks,
    }


def _check(name: str, passed: bool, detail: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    result = {"name": name, "passed": bool(passed)}
    if detail is not None:
        result["detail"] = detail
    return result


def _labels_from_items(items: List[Dict[str, Any]]) -> List[str]:
    labels = []
    for item in items:
        label = _label_from_item(item)
        if label:
            labels.extend(_split_label_terms(label))
    return _dedupe(labels)


def _label_from_item(item: Dict[str, Any]) -> str:
    if not isinstance(item, dict):
        return ""
    for key in ("label", "name", "display_name", "target_summary", "prompt_seed"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    target_ref = item.get("target_ref")
    if isinstance(target_ref, dict):
        value = target_ref.get("display_name") or target_ref.get("target_node_ref")
        if isinstance(value, str) and value.strip():
            return value.strip()
    music_ref = item.get("music_object_ref")
    if isinstance(music_ref, dict):
        value = music_ref.get("display_name") or music_ref.get("credited_artist_name")
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _split_label_terms(label: str) -> List[str]:
    parts = [label]
    if "/" in label:
        parts.extend(part.strip() for part in label.split("/") if part.strip())
    return [part for part in parts if len(_normalize_text(part)) >= 3]


def _matched_labels(labels: List[str], haystack: str) -> List[str]:
    return [label for label in _dedupe(labels) if _label_present(label, haystack)]


def _label_recall(labels: List[str], haystack: str) -> float:
    deduped = _dedupe(labels)
    if not deduped:
        return 1.0
    return len(_matched_labels(deduped, haystack)) / len(deduped)


def _label_present(label: str, haystack: str) -> bool:
    norm_label = _normalize_text(label)
    norm_haystack = _normalize_text(haystack)
    if not norm_label:
        return False
    return norm_label in norm_haystack


def _normalize_text(value: Any) -> str:
    return "".join(char.lower() if char.isalnum() else " " for char in str(value)).strip()


def _dedupe(values: List[str]) -> List[str]:
    seen = set()
    deduped = []
    for value in values:
        key = _normalize_text(value)
        if key and key not in seen:
            seen.add(key)
            deduped.append(value)
    return deduped


def _items_have_key(items: List[Dict[str, Any]], key: str) -> bool:
    return bool(items) and all(isinstance(item, dict) and bool(item.get(key)) for item in items)


def _items_have_non_empty_list(items: List[Dict[str, Any]], key: str) -> bool:
    return bool(items) and all(isinstance(item, dict) and bool(item.get(key)) and isinstance(item.get(key), list) for item in items)


def _items_have_behavior(items: List[Dict[str, Any]], allowed: set[str]) -> bool:
    return bool(items) and all(isinstance(item, dict) and item.get("candidate_pool_behavior") in allowed for item in items)


def _compare_shadow_to_baseline(results: List[Dict[str, Any]], profiles: List[str]) -> List[Dict[str, Any]]:
    comparisons = []
    shadow_by_profile = {result.get("profile"): result for result in results}
    for profile in profiles:
        baseline_path = A3_WWTSF_OUTPUT_DIR / f"wwtsf_substrate_profile_{profile}_A3.json"
        shadow_result = shadow_by_profile.get(profile, {})
        shadow = shadow_result.get("parsed_output")
        baseline = _load_json(baseline_path) if baseline_path.exists() else None
        profile_id = _profile_id(profile)
        if not isinstance(shadow, dict) or not isinstance(baseline, dict):
            comparisons.append(
                {
                    "profile_id": profile_id,
                    "baseline_available": isinstance(baseline, dict),
                    "shadow_available": isinstance(shadow, dict),
                    "category_scores": {},
                    "overall_status": "not_comparable",
                    "notes": ["Missing baseline or shadow output."],
                }
            )
            continue
        category_scores = {
            "scope_discipline": _score_scope_discipline(shadow, baseline),
            "contradiction_handling": _score_count_based_category(shadow, baseline, "contradictions_or_review_needs"),
            "dense_positive_vs_isolated_frontier_logic": _score_dense_frontier_logic(shadow, baseline, profile),
            "dead_end_caution": _score_dead_end_caution(shadow, baseline),
            "waypoint_usefulness": _score_waypoint_usefulness(shadow, baseline),
            "first_mission_hint_quality": _score_first_mission_hints(shadow, baseline),
        }
        total = sum(score["score"] for score in category_scores.values())
        max_total = 3 * len(category_scores)
        if any(score["score"] <= 1 for score in category_scores.values()):
            overall = "review_needed"
        elif total >= max_total - 2:
            overall = "shadow_pass_candidate"
        else:
            overall = "usable_with_review"
        comparisons.append(
            {
                "profile_id": profile_id,
                "baseline_available": True,
                "shadow_available": True,
                "category_scores": category_scores,
                "total_score": total,
                "max_score": max_total,
                "overall_status": overall,
                "notes": _shadow_notes(shadow, baseline, profile),
            }
        )
    return comparisons


def _score_scope_discipline(shadow: Dict[str, Any], baseline: Dict[str, Any]) -> Dict[str, Any]:
    checks = [
        shadow.get("not_final_user_copy") is True,
        all(value is False for value in (shadow.get("exclusion_confirmations") or {}).values()),
        len(shadow.get("scope_limits", [])) >= max(1, min(len(baseline.get("scope_limits", [])), 3)),
        len(shadow.get("confidence_warnings", [])) >= 1,
    ]
    return _score_from_checks(checks, "Maintains provisional/copy/exclusion/scope discipline.")


def _score_count_based_category(shadow: Dict[str, Any], baseline: Dict[str, Any], key: str) -> Dict[str, Any]:
    shadow_count = len(shadow.get(key, []))
    baseline_count = len(baseline.get(key, []))
    if baseline_count == 0:
        score = 3 if shadow_count == 0 else 2
    elif shadow_count >= baseline_count:
        score = 3
    elif shadow_count >= max(1, baseline_count - 2):
        score = 2
    elif shadow_count > 0:
        score = 1
    else:
        score = 0
    return {
        "score": score,
        "shadow_count": shadow_count,
        "baseline_count": baseline_count,
        "detail": f"`{key}` count shadow={shadow_count}, baseline={baseline_count}.",
    }


def _score_dense_frontier_logic(shadow: Dict[str, Any], baseline: Dict[str, Any], profile: str) -> Dict[str, Any]:
    text = _json_text(shadow)
    checks = [
        len(shadow.get("known_anchors", [])) + len(shadow.get("candidate_regions", [])) >= 1,
        len(shadow.get("candidate_frontiers", [])) >= 1,
        "frontier" in text,
    ]
    if profile == "05":
        checks.extend(["dense" in text or len(shadow.get("candidate_regions", [])) >= 1, "isolated" in text or "single" in text])
    if profile == "06":
        checks.extend(["isolated" in text or "sparse" in text, len(shadow.get("candidate_frontiers", [])) >= len(shadow.get("known_anchors", []))])
    return _score_from_checks(checks, "Distinguishes dense positive evidence from isolated frontier opportunities.")


def _score_dead_end_caution(shadow: Dict[str, Any], baseline: Dict[str, Any]) -> Dict[str, Any]:
    dead_ends = shadow.get("candidate_dead_end_hypotheses", [])
    text = _json_text({"dead_ends": dead_ends, "warnings": shadow.get("confidence_warnings", []), "scope_limits": shadow.get("scope_limits", [])})
    checks = [
        len(dead_ends) >= min(len(baseline.get("candidate_dead_end_hypotheses", [])), 1),
        any(item.get("review_needed") is True for item in dead_ends) if dead_ends else False,
        "hypothesis" in text or "scoped" in text or "scope" in text,
    ]
    return _score_from_checks(checks, "Treats Dead Ends as scoped hypotheses rather than final exclusions.")


def _score_waypoint_usefulness(shadow: Dict[str, Any], baseline: Dict[str, Any]) -> Dict[str, Any]:
    waypoints = shadow.get("waypoint_notes", [])
    text = _json_text(waypoints)
    checks = [
        len(waypoints) >= min(len(baseline.get("waypoint_notes", [])), 1),
        "waypoint" in text or "useful" in text or "context" in text,
        "landmark" not in text or "not landmark" in text or "not canon" in text or "canon" in text,
    ]
    return _score_from_checks(checks, "Keeps Waypoints useful/contextual without canon inflation.")


def _score_first_mission_hints(shadow: Dict[str, Any], baseline: Dict[str, Any]) -> Dict[str, Any]:
    hints = shadow.get("first_mission_input_hints", [])
    text = _json_text(hints)
    checks = [
        len(hints) >= min(len(baseline.get("first_mission_input_hints", [])), 1),
        all((hint.get("prompt_seed") and hint.get("objective")) for hint in hints),
        "caution" in text or "scope" in text or "uncertain" in text or "review" in text,
    ]
    return _score_from_checks(checks, "Provides mission-usable hint seeds with caution notes.")


def _score_from_checks(checks: List[bool], detail: str) -> Dict[str, Any]:
    passed = sum(1 for value in checks if value)
    if passed == len(checks):
        score = 3
    elif passed >= max(1, len(checks) - 1):
        score = 2
    elif passed:
        score = 1
    else:
        score = 0
    return {
        "score": score,
        "passed_checks": passed,
        "total_checks": len(checks),
        "detail": detail,
    }


def _shadow_notes(shadow: Dict[str, Any], baseline: Dict[str, Any], profile: str) -> List[str]:
    notes = []
    if len(shadow.get("first_mission_input_hints", [])) < len(baseline.get("first_mission_input_hints", [])):
        notes.append("Shadow has fewer first mission hints than baseline.")
    if profile == "06" and len(shadow.get("known_anchors", [])) > len(shadow.get("candidate_frontiers", [])):
        notes.append("Profile 06 should bias toward frontier logic over anchor inflation.")
    if not notes:
        notes.append("No deterministic shadow-comparison caveat detected.")
    return notes


def _write_wwtsf_guarded_repair_report(
    *,
    results: List[Dict[str, Any]],
    tag_fixture_result: Dict[str, Any],
    unavailable_requested: List[Dict[str, str]],
    dry_run: bool,
) -> None:
    A3_WWTSF_REPAIR_DIR.mkdir(parents=True, exist_ok=True)
    path = A3_WWTSF_REPAIR_DIR / "wwtsf_mini_guarded_repair_report_v0_1_5.md"
    all_final_pass = bool(results) and all(
        (result.get("selected_validation_result") or {}).get("valid")
        and (result.get("selected_guardrail_result") or {}).get("overall_status") == "guardrail_pass"
        for result in results
    )
    fallback_used = any(result.get("selected_stage") == "gpt_5_5_fallback" for result in results)
    repair_used = any(any(stage.get("stage") == "mini_repair_pass" for stage in result.get("stage_results", [])) for result in results)
    total_cost = sum(
        (stage.get("metrics", {}) or {}).get("estimated_total_cost_usd") or 0
        for result in results
        for stage in result.get("stage_results", [])
    )
    total_input = sum(
        (stage.get("metrics", {}) or {}).get("input_tokens") or 0
        for result in results
        for stage in result.get("stage_results", [])
    )
    total_output = sum(
        (stage.get("metrics", {}) or {}).get("output_tokens") or 0
        for result in results
        for stage in result.get("stage_results", [])
    )
    total_latency = sum(
        (stage.get("metrics", {}) or {}).get("latency_seconds") or 0
        for result in results
        for stage in result.get("stage_results", [])
    )
    if all_final_pass and not fallback_used and repair_used:
        recommendation = "ACCEPT_GPT_5_4_MINI_GUARDED_REPAIR_PATH"
    elif all_final_pass and fallback_used:
        recommendation = "ACCEPT_WITH_GPT_5_5_FALLBACK_REQUIRED"
    elif all_final_pass:
        recommendation = "ACCEPT_GPT_5_4_MINI_GUARDED_FIRST_PASS"
    else:
        recommendation = "REJECT_AND_REPAIR_GUARDRAIL_LOOP"

    lines = [
        "# A3 WWTSF Mini Guarded Repair v0.1.5",
        "",
        f"- Generated at: `{_now()}`",
        f"- Run type: `{'dry_run' if dry_run else 'live_api'}`",
        f"- Output dir: `{A3_WWTSF_REPAIR_DIR}`",
        "- Mini model: `gpt-5.4-mini`",
        "- Fallback model: `gpt-5.5`",
        "- First-pass prompt: `wwtsf_substrate_guarded_v0_1_5`",
        "- Repair prompt: `wwtsf_substrate_repair_v0_1_5`",
        "- Output schema: `wwtsf_substrate_output_schema_v0_1_2`",
        "",
        "## Policy",
        "",
        "- GPT-5.4-mini unguarded default remains rejected.",
        "- GPT-5.4-mini guarded candidate remains viable only if functional coverage passes.",
        "- GPT-5.5 remains baseline/default unless mini first pass or mini repair clears guardrails.",
        "- Raw A3 payloads, Profile Writer outputs, hidden truth, promoted Atlas truth, and canonical graph mutation are excluded.",
        "",
        "## Token / Cost Summary",
        "",
        f"- Total input tokens across stages: `{total_input}`",
        f"- Total output tokens across stages: `{total_output}`",
        f"- Estimated total cost across stages: `{_fmt_cost(total_cost)}`",
        f"- Total latency across stages: `{round(total_latency, 3)}s`",
        "",
        "## Per-Profile Results",
        "",
        "| Profile | First Pass | Repair | Fallback | Selected Stage | Selected Model | Final Guardrail | Final Valid |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for result in results:
        stage_by_name = {stage.get("stage"): stage for stage in result.get("stage_results", [])}
        lines.append(
            "| "
            f"`{result.get('profile_id')}` | "
            f"`{_stage_status(stage_by_name.get('mini_first_pass'))}` | "
            f"`{_stage_status(stage_by_name.get('mini_repair_pass'))}` | "
            f"`{_stage_status(stage_by_name.get('gpt_5_5_fallback'))}` | "
            f"`{result.get('selected_stage')}` | "
            f"`{result.get('selected_model')}` | "
            f"`{(result.get('selected_guardrail_result') or {}).get('overall_status')}` | "
            f"`{(result.get('selected_validation_result') or {}).get('valid')}` |"
        )
    lines.extend(["", "## Failure / Repair Details", ""])
    for result in results:
        lines.append(f"### {result.get('profile_id')}")
        for stage in result.get("stage_results", []):
            guardrail = stage.get("guardrail_result") or {}
            lines.append(f"- `{stage.get('stage')}` / `{stage.get('metadata', {}).get('model')}`: `{guardrail.get('overall_status')}`")
            for category_id, category in (guardrail.get("categories") or {}).items():
                if category.get("status") != "pass":
                    failed = [check for check in category.get("checks", []) if not check.get("passed")]
                    failed_names = ", ".join(check.get("name", "") for check in failed)
                    lines.append(f"  - `{category_id}`: `{category.get('status')}` ({failed_names})")
            omissions = guardrail.get("explicit_omissions") or []
            if omissions:
                lines.append(f"  - Explicit omissions: `{'; '.join(str(value) for value in omissions)}`")
        lines.append("")
    lines.extend(
        [
            "## Tag-Bearing Fixture Guardrail",
            "",
            f"- Fixture: `{tag_fixture_result.get('fixture')}`",
            f"- Status: `{tag_fixture_result.get('status')}`",
        ]
    )
    for check in tag_fixture_result.get("checks", []):
        lines.append(f"- `{check.get('name')}`: `{check.get('passed')}`")
    lines.extend(
        [
            "",
            "## Requested Unavailable Profiles",
            "",
            f"- Count: `{len(unavailable_requested)}`",
        ]
    )
    for item in unavailable_requested:
        lines.append(f"- `{item.get('profile')}`: `{item.get('reason')}`")
    lines.extend(["", "## Recommendation", "", f"`{recommendation}`"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _stage_status(stage: Optional[Dict[str, Any]]) -> str:
    if not stage:
        return "not_run"
    guardrail = stage.get("guardrail_result") or {}
    valid = stage.get("validation_result", {}).get("valid")
    return f"{guardrail.get('overall_status')} / valid={valid}"


def _write_wwtsf_consistency_report(
    *,
    results: List[Dict[str, Any]],
    tag_fixture_result: Dict[str, Any],
    unavailable_requested: List[Dict[str, str]],
    additional_ready: List[str],
    additional_unavailable: List[Dict[str, str]],
    dry_run: bool,
) -> None:
    A3_WWTSF_CONSISTENCY_DIR.mkdir(parents=True, exist_ok=True)
    path = A3_WWTSF_CONSISTENCY_DIR / "wwtsf_mini_consistency_guardrail_report_v0_1_4.md"
    total_cost = sum((result.get("metrics", {}) or {}).get("estimated_total_cost_usd") or 0 for result in results)
    total_input = sum((result.get("metrics", {}) or {}).get("input_tokens") or 0 for result in results)
    total_output = sum((result.get("metrics", {}) or {}).get("output_tokens") or 0 for result in results)
    total_latency = sum((result.get("metrics", {}) or {}).get("latency_seconds") or 0 for result in results)
    all_schema_valid = all(result.get("validation_result", {}).get("valid") for result in results)
    all_guardrails_pass = bool(results) and all(result.get("guardrail_result", {}).get("overall_status") == "guardrail_pass" for result in results)
    tag_pass = tag_fixture_result.get("status") == "pass"
    recommendation = "KEEP_GPT_5_5_AS_WWTSF_REVIEW_BASELINE"
    if all_schema_valid and all_guardrails_pass and tag_pass:
        recommendation = "ACCEPT_GPT_5_4_MINI_AS_WWTSF_DEFAULT_CANDIDATE_PENDING_HUMAN_REVIEW"
    elif all_schema_valid:
        recommendation = "KEEP_GPT_5_5_AS_WWTSF_BASELINE_UNTIL_MINI_PASSES_FUNCTIONAL_GUARDRAILS"

    lines = [
        "# WWTSF Mini Consistency + Guardrail Pass v0.1.4",
        "",
        f"- Generated at: `{_now()}`",
        f"- Run type: `{'dry_run' if dry_run else 'live_api'}`",
        f"- Output dir: `{A3_WWTSF_CONSISTENCY_DIR}`",
        "- Model under test: `gpt-5.4-mini`",
        "- Baseline/review model: `gpt-5.5`",
        "- Prompt: `wwtsf_substrate_v0_1_2`",
        "- Schema: `wwtsf_substrate_output_schema_v0_1_2`",
        "",
        "## Acceptance Target",
        "",
        "GPT-5.4-mini can become default for WWTSF substrate only if it preserves functional coverage, not merely schema validity. GPT-5.5 remains the review/baseline model until mini passes this broader gate.",
        "",
        "## Input / Exclusion Confirmation",
        "",
        "- Same AtlasDigestView inputs as v0.1.3: `true`",
        "- Same node interpretation inputs as v0.1.3: `true`",
        "- Same role assignment policy notes as v0.1.3: `true`",
        "- Raw A3 payloads used: `false`",
        "- Profile Writer outputs used: `false`",
        "- Hidden fake-profile truth used: `false`",
        "- Canonical graph mutation allowed: `false`",
        "",
        "## Token / Cost Summary",
        "",
        f"- Total input tokens: `{total_input}`",
        f"- Total output tokens: `{total_output}`",
        f"- Estimated cost: `{_fmt_cost(total_cost)}`",
        f"- Total latency: `{round(total_latency, 3)}s`",
        "",
        "## Per-Profile Guardrail Status",
        "",
        "| Profile | Schema Valid | Candidate/Region | Frontier | Contradiction | Hints | Scope | Overall | Cost |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | ---: |",
    ]
    for result in results:
        guardrail = result.get("guardrail_result", {})
        categories = guardrail.get("categories", {})
        lines.append(
            "| "
            f"`{result.get('profile_id')}` | "
            f"`{result.get('validation_result', {}).get('valid')}` | "
            f"`{_guardrail_status(categories, 'candidate_region_preservation')}` | "
            f"`{_guardrail_status(categories, 'frontier_coverage')}` | "
            f"`{_guardrail_status(categories, 'contradiction_coverage')}` | "
            f"`{_guardrail_status(categories, 'mission_hint_completeness')}` | "
            f"`{_guardrail_status(categories, 'scope_and_exclusion_integrity')}` | "
            f"`{guardrail.get('overall_status')}` | "
            f"{_fmt_cost((result.get('metrics') or {}).get('estimated_total_cost_usd'))} |"
        )
    lines.extend(
        [
            "",
            "## Guardrail Details",
            "",
        ]
    )
    for result in results:
        guardrail = result.get("guardrail_result", {})
        lines.append(f"### {result.get('profile_id')}")
        lines.append(f"- Overall: `{guardrail.get('overall_status')}`")
        for category_id, category in guardrail.get("categories", {}).items():
            lines.append(f"- `{category_id}`: `{category.get('status')}` ({category.get('passed_checks')}/{category.get('total_checks')})")
            failed = [check for check in category.get("checks", []) if not check.get("passed")]
            for check in failed:
                detail = check.get("detail")
                lines.append(f"  - Failed `{check.get('name')}`{': ' + json.dumps(detail, sort_keys=True) if detail else ''}")
        lines.append("")
    lines.extend(
        [
            "## Additional Simulated Profile Readiness",
            "",
            f"- Additional ready profiles run: `{', '.join(additional_ready) if additional_ready else 'none'}`",
            f"- Requested unavailable profiles: `{len(unavailable_requested)}`",
            f"- Additional simulated profiles unavailable: `{len(additional_unavailable)}`",
            "",
        ]
    )
    for item in unavailable_requested + additional_unavailable[:12]:
        lines.append(f"- `{item.get('profile')}`: `{item.get('reason')}`")
    if len(additional_unavailable) > 12:
        lines.append(f"- Additional unavailable profiles omitted from report body: `{len(additional_unavailable) - 12}`")
    lines.extend(
        [
            "",
            "## Tag-Bearing Fixture Guardrail",
            "",
            f"- Fixture: `{tag_fixture_result.get('fixture')}`",
            f"- Status: `{tag_fixture_result.get('status')}`",
        ]
    )
    for check in tag_fixture_result.get("checks", []):
        lines.append(f"- `{check.get('name')}`: `{check.get('passed')}`")
    lines.extend(
        [
            "",
            "## Recommendation",
            "",
            f"`{recommendation}`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _guardrail_status(categories: Dict[str, Any], key: str) -> str:
    return str((categories.get(key) or {}).get("status", "missing"))


def _write_wwtsf_shadow_report(
    *,
    results: List[Dict[str, Any]],
    comparisons: List[Dict[str, Any]],
    dry_run: bool,
) -> None:
    A3_WWTSF_SHADOW_DIR.mkdir(parents=True, exist_ok=True)
    path = A3_WWTSF_SHADOW_DIR / "wwtsf_5_4_mini_shadow_comparison_report_v0_1_3.md"
    total_cost = sum((result.get("metrics", {}) or {}).get("estimated_total_cost_usd") or 0 for result in results)
    total_input = sum((result.get("metrics", {}) or {}).get("input_tokens") or 0 for result in results)
    total_output = sum((result.get("metrics", {}) or {}).get("output_tokens") or 0 for result in results)
    total_latency = sum((result.get("metrics", {}) or {}).get("latency_seconds") or 0 for result in results)
    all_valid = all(result.get("validation_result", {}).get("valid") for result in results)
    all_pass_or_usable = all(comp.get("overall_status") in {"shadow_pass_candidate", "usable_with_review"} for comp in comparisons)
    recommendation = "KEEP_GPT_5_5_BASELINE_FOR_WWTSF"
    if all_valid and all(comp.get("overall_status") == "shadow_pass_candidate" for comp in comparisons):
        recommendation = "ACCEPT_GPT_5_4_MINI_AS_WWTSF_CANDIDATE_WITH_HUMAN_REVIEW"
    elif all_valid and all_pass_or_usable:
        recommendation = "ACCEPT_GPT_5_4_MINI_WITH_REPAIR_OR_REVIEW_BEFORE_DEFAULT"

    lines = [
        "# A3 WWTSF 5.4-Mini Shadow Comparison v0.1.3",
        "",
        f"- Generated at: `{_now()}`",
        f"- Run type: `{'dry_run' if dry_run else 'live_api'}`",
        f"- Shadow output dir: `{A3_WWTSF_SHADOW_DIR}`",
        f"- Baseline output dir: `{A3_WWTSF_OUTPUT_DIR}`",
        "- Baseline model: `gpt-5.5`",
        "- Shadow model: `gpt-5.4-mini`",
        "- Prompt: `wwtsf_substrate_v0_1_2`",
        "- Schema: `wwtsf_substrate_output_schema_v0_1_2`",
        "",
        "## Input / Exclusion Confirmation",
        "",
        "- Same AtlasDigestView inputs as v0.1.2: `true`",
        "- Same node interpretation inputs as v0.1.2: `true`",
        "- Same role assignment policy notes as v0.1.2: `true`",
        "- Raw A3 payloads used: `false`",
        "- Profile Writer outputs used: `false`",
        "- Hidden fake-profile truth used: `false`",
        "- Canonical graph mutation allowed: `false`",
        "",
        "## Token / Cost Summary",
        "",
        f"- Shadow total input tokens: `{total_input}`",
        f"- Shadow total output tokens: `{total_output}`",
        f"- Shadow estimated cost: `{_fmt_cost(total_cost)}`",
        f"- Shadow total latency: `{round(total_latency, 3)}s`",
        "",
        "## Per-Profile Status",
        "",
        "| Profile | Schema Valid | Scope | Contradiction | Dense/Frontier | Dead End | Waypoint | First Mission Hints | Status | Cost |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |",
    ]
    results_by_profile = {result.get("profile_id"): result for result in results}
    for comparison in comparisons:
        profile_id = comparison["profile_id"]
        result = results_by_profile.get(profile_id, {})
        scores = comparison.get("category_scores", {})
        lines.append(
            "| "
            f"`{profile_id}` | "
            f"`{result.get('validation_result', {}).get('valid')}` | "
            f"{_category_score(scores, 'scope_discipline')} | "
            f"{_category_score(scores, 'contradiction_handling')} | "
            f"{_category_score(scores, 'dense_positive_vs_isolated_frontier_logic')} | "
            f"{_category_score(scores, 'dead_end_caution')} | "
            f"{_category_score(scores, 'waypoint_usefulness')} | "
            f"{_category_score(scores, 'first_mission_hint_quality')} | "
            f"`{comparison.get('overall_status')}` | "
            f"{_fmt_cost((result.get('metrics') or {}).get('estimated_total_cost_usd'))} |"
        )
    lines.extend(
        [
            "",
            "## Comparison Notes",
            "",
        ]
    )
    for comparison in comparisons:
        lines.append(f"### {comparison['profile_id']}")
        for category, score in comparison.get("category_scores", {}).items():
            lines.append(f"- `{category}`: `{score.get('score')}/3` - {score.get('detail')}")
        for note in comparison.get("notes", []):
            lines.append(f"- Note: {note}")
        lines.append("")
    lines.extend(
        [
            "## Mission Generation Repair Brief",
            "",
            f"- Repair brief: `{A3_MISSION_OUTPUT_DIR / 'mission_generation_repair_brief_v0_1_3.md'}`",
            "- Mission-side finding: schema-valid route placeholders such as `Disney-associated theatrical/film song probe` are development planning slots, not beta-ready playable route items.",
            "- Required repair: every route item must be either a concrete Apple Music-searchable object or an explicit unresolved candidate-search slot.",
            "- Import rule: unresolved candidate-search slots and generic placeholder route titles must force `app_import_ready = false`.",
            "- Model policy: keep mission generation on `gpt-5.4-mini`; do not use `gpt-5.5` for missions until candidate object selection is cleaned up.",
            "",
            "## Recommendation",
            "",
            f"`{recommendation}`",
            "",
            "Do not switch WWTSF default model on this run alone. Use this shadow comparison to decide whether a broader 5.4-mini consistency pass is warranted.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _category_score(scores: Dict[str, Any], key: str) -> str:
    score = scores.get(key, {}).get("score")
    return "" if score is None else str(score)


def _json_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True).lower()


def _write_combined_report(*, wwtsf_results: List[Dict[str, Any]], mission_results: List[Dict[str, Any]], dry_run: bool) -> None:
    A3_WWTSF_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = A3_WWTSF_OUTPUT_DIR / "wwtsf_substrate_smoke_report_v0_1_2.md"
    lines = [
        "# A3 WWTSF Substrate + Mission Dev Run v0.1.2",
        "",
        f"- Generated at: `{_now()}`",
        f"- Run type: `{'dry_run' if dry_run else 'live_api'}`",
        f"- WWTSF output dir: `{A3_WWTSF_OUTPUT_DIR}`",
        f"- Mission output dir: `{A3_MISSION_OUTPUT_DIR}`",
        "",
        "## Exclusion Confirmations",
        "",
        "- Raw A3 payloads used: `false`",
        "- Profile Writer outputs used: `false`",
        "- Hidden fake-profile truth used: `false`",
        "- Canonical graph mutation allowed: `false`",
        "- Promoted Atlas truth assumed: `false`",
        "",
        "## WWTSF Substrate Status",
        "",
        "| Profile | Schema Valid | Input Tokens | Output Tokens | Est. Cost | Output |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for result in wwtsf_results:
        lines.append(
            "| "
            f"`{result.get('profile_id')}` | "
            f"`{result.get('validation_result', {}).get('valid')}` | "
            f"{_fmt_num(result.get('metrics', {}).get('input_tokens'))} | "
            f"{_fmt_num(result.get('metrics', {}).get('output_tokens'))} | "
            f"{_fmt_cost(result.get('metrics', {}).get('estimated_total_cost_usd'))} | "
            f"`{result.get('output_file')}` |"
        )
    lines.extend(
        [
            "",
            "## Mission Scenario Status",
            "",
            "| Scenario | Profile | Schema Valid | Input Tokens | Output Tokens | Est. Cost | Output |",
            "| --- | --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for result in mission_results:
        scenario = result.get("scenario") or {}
        lines.append(
            "| "
            f"`{scenario.get('scenario_id')}` | "
            f"`{result.get('profile_id')}` | "
            f"`{result.get('validation_result', {}).get('valid')}` | "
            f"{_fmt_num(result.get('metrics', {}).get('input_tokens'))} | "
            f"{_fmt_num(result.get('metrics', {}).get('output_tokens'))} | "
            f"{_fmt_cost(result.get('metrics', {}).get('estimated_total_cost_usd'))} | "
            f"`{result.get('output_file')}` |"
        )
    lines.extend(_quality_notes(wwtsf_results, mission_results))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _quality_notes(wwtsf_results: List[Dict[str, Any]], mission_results: List[Dict[str, Any]]) -> List[str]:
    wwtsf_valid = sum(1 for result in wwtsf_results if result.get("validation_result", {}).get("valid"))
    mission_valid = sum(1 for result in mission_results if result.get("validation_result", {}).get("valid"))
    decision = "ACCEPT_WITH_REPAIR_BEFORE_BETA_PIPELINE"
    if wwtsf_results and mission_results and wwtsf_valid == len(wwtsf_results) and mission_valid == len(mission_results):
        decision = "ACCEPT_END_TO_END_ATLAS_TO_GENERATION_PROOF"
    elif not wwtsf_results or wwtsf_valid < len(wwtsf_results):
        decision = "REJECT_AND_REPAIR_WWTSF_OR_MISSION_HANDOFF"
    return [
        "",
        "## Quality Notes",
        "",
        "- WWTSF substrate consumes AtlasDigestView and node interpretation outputs only.",
        "- Mission generation consumes AtlasDigestView, node interpretation output, and WWTSF substrate.",
        "- Strict schema validation is recorded per output.",
        "- The report does not judge MusicKit resolution quality; search hints remain placeholders.",
        "",
        "## Recommended Decision",
        "",
        f"`{decision}`",
    ]


def _exclusion_policy() -> Dict[str, bool]:
    return {
        "raw_a3_payload_used": False,
        "profile_writer_output_used": False,
        "hidden_truth_used": False,
        "canonical_graph_mutation_allowed": False,
        "promoted_atlas_truth_assumed": False,
    }


def _require_files(paths: Iterable[Path]) -> None:
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required A3 input files: " + ", ".join(missing))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _render_template(path: Path, replacements: Dict[str, str]) -> str:
    rendered = path.read_text(encoding="utf-8")
    for key, value in replacements.items():
        rendered = rendered.replace(key, value)
    return rendered


def _redact_request_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    return json.loads(json.dumps(payload))


def _profile_id(profile: str) -> str:
    return f"profile_{profile}_A3"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _fmt_num(value: Any) -> str:
    return "" if value is None else str(value)


def _fmt_cost(value: Any) -> str:
    return "" if value is None else f"${float(value):.6f}"
