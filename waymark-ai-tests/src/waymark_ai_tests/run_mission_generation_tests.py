from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .a3_generation import PROFILES as A3_PROFILES
from .a3_generation import (
    run_a3_mission_generation,
    run_wwtsf_consistency_guardrail_pass,
    run_wwtsf_mini_guarded_repair,
    run_wwtsf_shadow_comparison,
    run_wwtsf_substrate,
)
from .closed_loop_simulation import run_closed_loop_simulation
from .openai_client import (
    build_request_payload,
    call_openai,
    config_from_env,
    extract_output_text,
    extract_usage,
    parse_json_from_text,
)
from .prompt_builder import build_prompt, load_requests_doc, normalize_context_mode
from .report_writer import (
    write_context_matrix_report,
    write_json,
    write_model_matrix_report,
    write_run_report,
    write_summary_report,
)
from .schema_validator import validate_json
from .score_output import PRIMARY_REACTIONS, score_mission_output


HARNESS_ROOT = Path(__file__).resolve().parents[2]
FIXTURES_ROOT = HARNESS_ROOT / "fixtures"
DEFAULT_MODEL_MATRIX = ["gpt-5.4-nano", "gpt-5.4-mini", "gpt-5.4", "gpt-5.5"]
LEGACY_MODEL_MATRIX = ["gpt-4.1"]


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run Cartenza mission-generation API tests.")
    parser.add_argument("--generation-task", choices=["mission_generation", "wwtsf_substrate", "wwtsf_shadow_comparison", "wwtsf_consistency_guardrail_pass", "wwtsf_mini_guarded_repair", "closed_loop_simulation"], default="mission_generation", help="Generation task mode. Default keeps the existing mission-generation harness behavior.")
    parser.add_argument("--a3-dev-run", action="store_true", help="Run the A3 mission-generation dev scenarios using AtlasDigestView, node interpretation, and WWTSF substrate.")
    parser.add_argument("--profiles", default=",".join(A3_PROFILES), help="A3 profiles to run, comma-separated, for WWTSF or A3 mission dev modes.")
    parser.add_argument("--request", action="append", help="Request id to run. Can be repeated or comma-separated.")
    parser.add_argument("--suite", help="Suite id from requests_v0_1.json, for example suggested_first_five or all.")
    parser.add_argument("--prompt-template", action="append", default=[], help="Prompt template name without .md. Can be repeated or comma-separated.")
    parser.add_argument("--context-mode", action="append", default=[], help="thin, atlas_digest, atlas_plus_features, or atlas_plus_features_plus_candidates. Can be repeated or comma-separated.")
    parser.add_argument("--model", help="OpenAI model. Defaults to CARTENZA_OPENAI_MODEL, WAYMARK_OPENAI_MODEL, OPENAI_MODEL, or gpt-4.1. Can be comma-separated.")
    parser.add_argument("--models", action="append", default=[], help="Model matrix to run. Can be repeated or comma-separated.")
    parser.add_argument("--api-style", choices=["responses", "chat_completions"], help="OpenAI API style. Defaults to responses.")
    parser.add_argument("--temperature", type=float, help="Optional sampling temperature.")
    parser.add_argument("--max-output-tokens", type=int, help="Optional maximum output token budget.")
    parser.add_argument("--reasoning-effort", help="Optional reasoning effort for models that support it.")
    parser.add_argument("--timeout-seconds", type=int, help="OpenAI request timeout per model call. Defaults to CARTENZA_OPENAI_TIMEOUT_SECONDS, WAYMARK_OPENAI_TIMEOUT_SECONDS, or 120.")
    parser.add_argument("--runs", type=int, default=1, help="Number of repeated runs per matrix cell.")
    parser.add_argument("--output-root", type=Path, default=HARNESS_ROOT / "outputs")
    parser.add_argument("--reports-root", type=Path, default=HARNESS_ROOT / "reports")
    parser.add_argument("--dry-run", action="store_true", help="Build and save request payloads without calling OpenAI or scoring output.")
    parser.add_argument("--mock", action="store_true", help="Use a local deterministic schema-valid mock output for smoke tests.")
    parser.add_argument("--model-matrix-report", action="store_true", help="Write reports/model_matrix_<timestamp>.md in addition to the suite summary.")
    parser.add_argument("--context-matrix-report", action="store_true", help="Write reports/context_matrix_<timestamp>.md in addition to the suite summary.")
    parser.add_argument("--list", choices=["requests", "suites", "prompts", "context_modes", "models"], help="List available harness fixtures and exit.")
    args = parser.parse_args(argv)

    _load_env_file(HARNESS_ROOT / ".env")
    _load_env_file(Path.cwd() / ".env")

    if args.list:
        return _list_fixture(args.list)

    if args.generation_task == "wwtsf_substrate":
        pricing = _load_pricing()
        config = config_from_env(
            model=args.model or "gpt-5.5",
            api_style=args.api_style,
            temperature=args.temperature,
            max_output_tokens=args.max_output_tokens,
            reasoning_effort=args.reasoning_effort or "medium",
            timeout_seconds=args.timeout_seconds,
        )
        return run_wwtsf_substrate(
            profiles=_split_many([args.profiles]),
            config=config,
            pricing=pricing,
            estimate_cost_usd=_estimate_cost_usd,
            dry_run=args.dry_run,
        )

    if args.generation_task == "wwtsf_shadow_comparison":
        pricing = _load_pricing()
        config = config_from_env(
            model=args.model or "gpt-5.4-mini",
            api_style=args.api_style,
            temperature=args.temperature,
            max_output_tokens=args.max_output_tokens,
            reasoning_effort=args.reasoning_effort,
            timeout_seconds=args.timeout_seconds,
        )
        return run_wwtsf_shadow_comparison(
            profiles=_split_many([args.profiles]),
            config=config,
            pricing=pricing,
            estimate_cost_usd=_estimate_cost_usd,
            dry_run=args.dry_run,
        )

    if args.generation_task == "wwtsf_consistency_guardrail_pass":
        pricing = _load_pricing()
        config = config_from_env(
            model=args.model or "gpt-5.4-mini",
            api_style=args.api_style,
            temperature=args.temperature,
            max_output_tokens=args.max_output_tokens,
            reasoning_effort=args.reasoning_effort,
            timeout_seconds=args.timeout_seconds,
        )
        return run_wwtsf_consistency_guardrail_pass(
            profiles=_split_many([args.profiles]),
            config=config,
            pricing=pricing,
            estimate_cost_usd=_estimate_cost_usd,
            dry_run=args.dry_run,
        )

    if args.generation_task == "wwtsf_mini_guarded_repair":
        pricing = _load_pricing()
        config = config_from_env(
            model=args.model or "gpt-5.4-mini",
            api_style=args.api_style,
            temperature=args.temperature,
            max_output_tokens=args.max_output_tokens,
            reasoning_effort=args.reasoning_effort,
            timeout_seconds=args.timeout_seconds,
        )
        return run_wwtsf_mini_guarded_repair(
            profiles=_split_many([args.profiles]),
            config=config,
            pricing=pricing,
            estimate_cost_usd=_estimate_cost_usd,
            dry_run=args.dry_run,
        )

    if args.generation_task == "closed_loop_simulation":
        pricing = _load_pricing()
        config = config_from_env(
            model=args.model or "gpt-5.4-mini",
            api_style=args.api_style,
            temperature=args.temperature,
            max_output_tokens=args.max_output_tokens,
            reasoning_effort=args.reasoning_effort,
            timeout_seconds=args.timeout_seconds,
        )
        return run_closed_loop_simulation(
            profiles=_split_many([args.profiles]),
            config=config,
            pricing=pricing,
            estimate_cost_usd=_estimate_cost_usd,
            dry_run=args.dry_run,
        )

    if args.a3_dev_run:
        pricing = _load_pricing()
        config = config_from_env(
            model=args.model or "gpt-5.4-mini",
            api_style=args.api_style,
            temperature=args.temperature,
            max_output_tokens=args.max_output_tokens,
            reasoning_effort=args.reasoning_effort,
            timeout_seconds=args.timeout_seconds,
        )
        return run_a3_mission_generation(
            profiles=_split_many([args.profiles]),
            config=config,
            pricing=pricing,
            estimate_cost_usd=_estimate_cost_usd,
            dry_run=args.dry_run,
        )

    requests_doc = load_requests_doc(FIXTURES_ROOT)
    request_ids = _select_request_ids(args, requests_doc)
    prompt_templates = _split_many(args.prompt_template) or [
        "mission_generator_compact_v0_1",
    ]
    context_modes = [normalize_context_mode(mode) for mode in (_split_many(args.context_mode) or ["atlas_plus_features_plus_candidates"])]
    models = _select_models(args)
    pricing = _load_pricing()

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_results: List[Dict[str, Any]] = []
    sequence = 0

    for request_id in request_ids:
        for prompt_template in prompt_templates:
            for context_mode in context_modes:
                for model in models:
                    config = config_from_env(
                        model=model,
                        api_style=args.api_style,
                        temperature=args.temperature,
                        max_output_tokens=args.max_output_tokens,
                        reasoning_effort=args.reasoning_effort,
                        timeout_seconds=args.timeout_seconds,
                    )
                    for run_index in range(1, args.runs + 1):
                        sequence += 1
                        result = _run_one(
                            request_id=request_id,
                            prompt_template=prompt_template,
                            context_mode=context_mode,
                            run_index=run_index,
                            sequence=sequence,
                            timestamp=timestamp,
                            config=config,
                            output_root=args.output_root,
                            dry_run=args.dry_run,
                            mock=args.mock,
                            pricing=pricing,
                        )
                        if result is not None:
                            run_results.append(result)

    if run_results:
        summary_path = write_summary_report(args.reports_root, timestamp, run_results)
        print(f"Summary report: {summary_path}")
        if args.model_matrix_report or len(models) > 1:
            matrix_path = write_model_matrix_report(args.reports_root, timestamp, run_results)
            print(f"Model matrix report: {matrix_path}")
        if args.context_matrix_report or (len(context_modes) > 1 and len(models) == 1):
            context_matrix_path = write_context_matrix_report(args.reports_root, timestamp, run_results)
            print(f"Context matrix report: {context_matrix_path}")
    elif args.dry_run:
        print(f"Dry run complete. Request payloads were written under {args.output_root}.")
    return 0


def _run_one(
    request_id: str,
    prompt_template: str,
    context_mode: str,
    run_index: int,
    sequence: int,
    timestamp: str,
    config: Any,
    output_root: Path,
    dry_run: bool,
    mock: bool,
    pricing: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    context_mode = normalize_context_mode(context_mode)
    built = build_prompt(FIXTURES_ROOT, request_id, prompt_template, context_mode)
    request_payload = build_request_payload(config, built.system_prompt, built.user_prompt, built.output_schema)

    safe_model = _safe_name(config.model)
    run_dir = output_root / f"{timestamp}_{sequence:03d}_{request_id}_{prompt_template}_{context_mode}_{safe_model}_run{run_index:02d}"
    run_dir.mkdir(parents=True, exist_ok=True)
    run_type = "dry_run" if dry_run else "mock" if mock else "live_api"
    created_timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    metadata = {
        "request_id": request_id,
        "prompt_template": prompt_template,
        "context_mode": context_mode,
        "model": config.model,
        "run_index": run_index,
        "api_mode": "dry_run" if dry_run else config.api_style,
        "run_type": run_type,
        "created_at": created_timestamp,
        "suite_timestamp": timestamp,
    }
    write_json(run_dir / "metadata.json", metadata)
    write_json(run_dir / "context_packet.json", built.context_packet)
    write_json(run_dir / "request_payload.json", _redact_request_payload(request_payload))

    if dry_run:
        return None

    parse_error = None
    parsed_output: Optional[Dict[str, Any]] = None
    started_at = time.perf_counter()
    if mock:
        parsed_output = _mock_output(built.request_fixture, built.candidate_pool)
        raw_response: Dict[str, Any] = {"mock": True, "output_text": json.dumps(parsed_output)}
    else:
        try:
            raw_response = call_openai(config, request_payload)
            try:
                parsed_output = parse_json_from_text(extract_output_text(raw_response))
            except Exception as error:  # noqa: BLE001 - we want parse failures in the report.
                parse_error = str(error)
        except Exception as error:  # noqa: BLE001 - API failures should still produce harness artifacts.
            parse_error = str(error)
            raw_response = {"api_error": parse_error}
    elapsed_seconds = round(time.perf_counter() - started_at, 3)

    write_json(run_dir / "raw_model_output.json", raw_response)
    if parsed_output is not None:
        write_json(run_dir / "parsed_output.json", parsed_output)

    validation_result = (
        validate_json(parsed_output, built.output_schema)
        if parsed_output is not None
        else {"validator": "none", "valid": False, "error_count": 1, "errors": [parse_error or "No parsed output."]}
    )
    write_json(run_dir / "validation_result.json", validation_result)

    score_report = score_mission_output(
        parsed_output=parsed_output,
        request_fixture=built.request_fixture,
        candidate_pool=built.candidate_pool,
        context_mode=context_mode,
        prompt_template_name=prompt_template,
        schema_valid=bool(validation_result["valid"]),
        parse_error=parse_error,
    )
    usage = extract_usage(raw_response)
    cost_estimate = _estimate_cost_usd(config.model, usage, pricing)
    model_declared_app_import_ready = _app_import_ready(parsed_output)
    metrics = {
        "input_tokens": usage["input_tokens"],
        "cached_input_tokens": usage["cached_input_tokens"],
        "output_tokens": usage["output_tokens"],
        "total_tokens": usage["total_tokens"],
        "estimated_input_cost_usd": cost_estimate["estimated_input_cost_usd"],
        "estimated_cached_input_cost_usd": cost_estimate["estimated_cached_input_cost_usd"],
        "estimated_output_cost_usd": cost_estimate["estimated_output_cost_usd"],
        "estimated_total_cost_usd": cost_estimate["estimated_total_cost_usd"],
        "estimated_cost_usd": cost_estimate["estimated_total_cost_usd"],
        "cost_status": cost_estimate["cost_status"],
        "cost_calculation_version": cost_estimate["cost_calculation_version"],
        "pricing_table_version": cost_estimate["pricing_table_version"],
        "pricing_table_date": cost_estimate["pricing_table_date"],
        "pricing_source": cost_estimate["pricing_source"],
        "cost_estimate_source": cost_estimate["pricing_source"],
        "latency_seconds": elapsed_seconds,
    }
    product_readiness_status = _derive_product_readiness_status(
        run_type=run_type,
        validation_result=validation_result,
        score_report=score_report,
        parsed_output=parsed_output,
    )
    app_import_ready = _derived_app_import_ready(model_declared_app_import_ready, product_readiness_status)
    metadata.update(metrics)
    metadata["product_readiness_status"] = product_readiness_status
    metadata["app_import_ready"] = app_import_ready
    metadata["model_declared_app_import_ready"] = model_declared_app_import_ready
    metadata["app_import_ready_invariant"] = (
        "forced_false_for_product_fail"
        if product_readiness_status == "product_fail" and model_declared_app_import_ready is True
        else "ok"
    )
    write_json(run_dir / "metadata.json", metadata)
    write_json(run_dir / "metrics.json", metrics)
    write_json(run_dir / "score_report.json", score_report)
    report_path = write_run_report(run_dir, metadata, validation_result, score_report)
    print(f"Run report: {report_path}")
    return {
        "metadata": metadata,
        "validation_result": validation_result,
        "score_report": score_report,
        "metrics": metrics,
        "product_readiness_status": product_readiness_status,
        "run_dir": str(run_dir),
        "report_path": str(report_path),
    }


def _select_request_ids(args: argparse.Namespace, requests_doc: Dict[str, Any]) -> List[str]:
    if args.suite:
        if args.suite == "all":
            return [request["request_id"] for request in requests_doc["requests"]]
        suites = requests_doc.get("suites", {})
        if args.suite not in suites:
            raise SystemExit(f"Unknown suite {args.suite}. Available suites: {', '.join(sorted(suites))}")
        return list(suites[args.suite])
    request_ids = _split_many(args.request or [])
    return request_ids or ["nirvana_to_current"]


def _select_models(args: argparse.Namespace) -> List[str]:
    requested_models = _split_many(args.models)
    if not requested_models and args.model:
        requested_models = _split_many([args.model])
    if not requested_models:
        requested_models = [config_from_env().model]
    seen = set()
    models = []
    for model in requested_models:
        if model not in seen:
            models.append(model)
            seen.add(model)
    return models


def _split_many(values: Iterable[str]) -> List[str]:
    result: List[str] = []
    for value in values:
        for part in value.split(","):
            stripped = part.strip()
            if stripped:
                result.append(stripped)
    return result


def _list_fixture(kind: str) -> int:
    requests_doc = load_requests_doc(FIXTURES_ROOT)
    if kind == "requests":
        for request in requests_doc["requests"]:
            print(f"{request['request_id']}: {request['prompt']}")
    elif kind == "suites":
        for suite_id, request_ids in requests_doc.get("suites", {}).items():
            print(f"{suite_id}: {', '.join(request_ids)}")
        print("all: every request fixture")
    elif kind == "prompts":
        for path in sorted((FIXTURES_ROOT / "prompt_templates").glob("*.md")):
            print(path.stem)
    elif kind == "context_modes":
        for mode in [
            "thin",
            "thin_context",
            "atlas_digest",
            "atlas_digest_only",
            "atlas_plus_features",
            "atlas_plus_features_plus_candidates",
            "generated_atlas_digest_view",
            "generated_atlas_digest_view_plus_features",
            "generated_atlas_digest_view_plus_features_plus_candidates",
            "mission_generation_digest_view",
            "mission_generation_digest_view_plus_features",
            "mission_generation_digest_view_plus_features_plus_candidates",
        ]:
            print(mode)
    elif kind == "models":
        for model in DEFAULT_MODEL_MATRIX + LEGACY_MODEL_MATRIX:
            print(model)
    return 0


def _load_pricing() -> Dict[str, Any]:
    raw_name, raw = _env_pair("CARTENZA_MODEL_PRICING_JSON", "WAYMARK_MODEL_PRICING_JSON")
    if raw:
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as error:
            raise SystemExit(f"{raw_name} is invalid JSON: {error}") from error
        return {
            "source": f"env:{raw_name}",
            "models": parsed.get("models", parsed) if isinstance(parsed, dict) else {},
            "pricing_table_version": parsed.get("pricing_table_version") if isinstance(parsed, dict) else None,
            "pricing_table_date": parsed.get("pricing_table_date") if isinstance(parsed, dict) else None,
        }

    _, pricing_file = _env_pair("CARTENZA_MODEL_PRICING_FILE", "WAYMARK_MODEL_PRICING_FILE")
    paths = [Path(pricing_file)] if pricing_file else [
        FIXTURES_ROOT / "pricing" / "openai_pricing_v0_3.json",
        HARNESS_ROOT / "model_pricing.json",
    ]
    for path in paths:
        if path.exists():
            parsed = json.loads(path.read_text(encoding="utf-8"))
            return {
                "source": str(path),
                "models": parsed.get("models", parsed) if isinstance(parsed, dict) else {},
                "pricing_table_version": parsed.get("pricing_table_version") if isinstance(parsed, dict) else None,
                "pricing_table_date": parsed.get("pricing_table_date") if isinstance(parsed, dict) else None,
            }

    return {
        "source": "not_configured",
        "models": {},
        "pricing_table_version": None,
        "pricing_table_date": None,
    }


def _env_pair(*names: str) -> tuple[str | None, str | None]:
    for name in names:
        value = os.environ.get(name)
        if value:
            return name, value
    return None, None


def _estimate_cost_usd(model: str, usage: Dict[str, Optional[int]], pricing: Dict[str, Any]) -> Dict[str, Any]:
    base_result = {
        "estimated_input_cost_usd": None,
        "estimated_cached_input_cost_usd": None,
        "estimated_output_cost_usd": None,
        "estimated_total_cost_usd": None,
        "cost_status": "not_calculated",
        "cost_calculation_version": "waymark_cost_v0_3",
        "pricing_table_version": pricing.get("pricing_table_version"),
        "pricing_table_date": pricing.get("pricing_table_date"),
        "pricing_source": pricing.get("source", "not_configured"),
    }
    input_tokens = usage.get("input_tokens")
    cached_input_tokens = usage.get("cached_input_tokens")
    output_tokens = usage.get("output_tokens")
    if input_tokens is None or output_tokens is None:
        return {**base_result, "cost_status": "usage_unavailable"}

    model_prices = pricing.get("models", {}).get(model) or pricing.get("models", {}).get("*")
    if not isinstance(model_prices, dict):
        return {**base_result, "cost_status": "pricing_missing"}

    input_price = model_prices.get("input_per_1m", model_prices.get("input_per_million"))
    cached_input_price = model_prices.get("cached_input_per_1m", model_prices.get("cached_input_per_million"))
    output_price = model_prices.get("output_per_1m", model_prices.get("output_per_million"))
    if input_price is None or output_price is None:
        return {**base_result, "cost_status": "pricing_missing"}

    cached_tokens = max(0, cached_input_tokens or 0)
    uncached_tokens = max(0, input_tokens - cached_tokens)
    if cached_tokens and cached_input_price is None:
        return {**base_result, "cost_status": "cached_pricing_missing"}

    input_cost = (uncached_tokens / 1_000_000) * float(input_price)
    cached_cost = (cached_tokens / 1_000_000) * float(cached_input_price or 0)
    output_cost = (output_tokens / 1_000_000) * float(output_price)
    total_cost = input_cost + cached_cost + output_cost
    return {
        **base_result,
        "estimated_input_cost_usd": round(input_cost, 6),
        "estimated_cached_input_cost_usd": round(cached_cost, 6),
        "estimated_output_cost_usd": round(output_cost, 6),
        "estimated_total_cost_usd": round(total_cost, 6),
        "cost_status": "estimated",
    }


def _app_import_ready(parsed_output: Optional[Dict[str, Any]]) -> Optional[bool]:
    if not isinstance(parsed_output, dict):
        return None
    review_config = parsed_output.get("review_config", {})
    if not isinstance(review_config, dict):
        return None
    return bool(review_config.get("ready_for_app_import"))


def _derived_app_import_ready(model_declared_app_import_ready: Optional[bool], product_readiness_status: str) -> Optional[bool]:
    if product_readiness_status == "product_fail":
        return False
    return model_declared_app_import_ready


def _derive_product_readiness_status(
    run_type: str,
    validation_result: Dict[str, Any],
    score_report: Dict[str, Any],
    parsed_output: Optional[Dict[str, Any]],
) -> str:
    if run_type == "mock":
        return "mock_only"
    if not validation_result.get("valid") or parsed_output is None:
        return "product_fail"
    if score_report.get("fail_count", 0) > 0:
        return "product_fail"
    if score_report.get("partial_count", 0) > 0:
        return "product_review_needed"
    review_config = parsed_output.get("review_config", {}) if isinstance(parsed_output, dict) else {}
    if isinstance(review_config, dict) and review_config.get("ready_for_app_import") is True:
        return "app_import_candidate"
    return "product_pass_candidate"


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


def _redact_request_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    redacted = json.loads(json.dumps(payload))
    return redacted


def _safe_name(value: str) -> str:
    return "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in value)


def _mock_output(request_fixture: Dict[str, Any], candidate_pool: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    candidates = list((candidate_pool or {}).get("candidates", []))
    expected_count = request_fixture.get("expected_route_item_count", {})
    count = max(expected_count.get("min", 4), 4)
    count = min(count, expected_count.get("max", count), len(candidates) if candidates else count)
    selected = candidates[:count] if candidates else []
    if not selected:
        selected = [
            {
                "candidate_id": f"MOCK_{index}",
                "artist": "Mock Artist",
                "title": f"Mock Track {index}",
                "album": "Mock Album",
                "year": 2026,
                "known_to_user": "unknown",
                "risk_class": "medium",
                "expected_feature_hints": ["emotional_conviction"],
                "music_kit_search_hint": {
                    "search_query": f"Mock Artist Mock Track {index}",
                    "preferred_version_notes": "Use canonical studio version.",
                    "avoid_versions": "Avoid live versions.",
                },
            }
            for index in range(1, count + 1)
        ]

    items = []
    for index, candidate in enumerate(selected, start=1):
        item_features = candidate.get("expected_feature_hints", [])[:3] or ["emotional_conviction"]
        risk_class = candidate.get("risk_class", "medium")
        is_trap = risk_class in {"trap", "dead_end_check"}
        selection_role = "anchor" if index == 1 else "trap" if is_trap else "probe"
        expected_positive_signal = (
            "Unexpected positive reaction would mean a bounded exception, cultural furniture value, or a need to reassess the dead end."
            if is_trap
            else "Pressure, conviction, or architecture appears in the user's own vocabulary."
        )
        items.append(
            {
                "route_index": index,
                "item_id": f"ITEM_{index:02d}",
                "candidate_id": candidate.get("candidate_id", ""),
                "item_type": candidate.get("item_type", "track"),
                "display_metadata": {
                    "artist": candidate.get("artist", "Unknown Artist"),
                    "title": candidate.get("title", "Unknown Title"),
                    "album": candidate.get("album", ""),
                    "release_year": candidate.get("year", 2026),
                },
                "selection_role": selection_role,
                "risk_class": risk_class,
                "familiarity_assumption": candidate.get("known_to_user", "unknown"),
                "why_selected": candidate.get("candidate_reason", "Mock route item generated for harness smoke testing."),
                "route_function": "Test whether this candidate produces evidence for the requested mission rather than playlist approval.",
                "item_hypothesis": "If this lands, it should reveal a bounded feature signal rather than a broad genre claim.",
                "expected_positive_signal": expected_positive_signal,
                "expected_negative_signal": "The item feels like a false-nearby recommendation with no body or bite.",
                "expected_features": item_features,
                "feedback_chip_sets": {
                    reaction: _mock_chips(reaction, item_features, is_trap=is_trap)
                    for reaction in PRIMARY_REACTIONS
                },
                "music_kit_search_hint": {
                    "search_query": candidate.get("music_kit_search_hint", {}).get(
                        "search_query",
                        f"{candidate.get('artist', '')} {candidate.get('title', '')}",
                    ),
                    "artist": candidate.get("artist", ""),
                    "title": candidate.get("title", ""),
                    "album": candidate.get("album", ""),
                    "preferred_version_notes": candidate.get("music_kit_search_hint", {}).get("preferred_version_notes", "Use canonical studio version."),
                    "avoid_versions": candidate.get("music_kit_search_hint", {}).get("avoid_versions", "Avoid live, karaoke, tribute, and remaster-only mismatches."),
                    "resolution_status_placeholder": "unresolved",
                },
                "review_state": {
                    "needs_human_review": True,
                    "review_notes": "Mock output only. Do not judge model quality from this run.",
                    "uncertainty_flags": ["mock_output"],
                },
            }
        )

    return {
        "schema_version": "waymark.mission_output.v0.1",
        "mission_id": f"MIS_TEST_{request_fixture['request_id'].upper()}",
        "source_prompt": request_fixture["prompt"],
        "title": f"Mock Mission: {request_fixture['request_id']}",
        "archetypes": request_fixture.get("expected_archetypes", ["Frontier Route"])[:2],
        "brief": "Local mock output for harness smoke testing.",
        "hypothesis": "A bounded route can test the prompt while preserving uncertainty and avoiding overgeneralization.",
        "why_now": "The request asks for a specific Cartenza mission-generation test.",
        "risk_model": {
            "overall_risk": "medium",
            "known_traps_acknowledged": request_fixture.get("main_risks", [])[:4],
            "uncertainty_notes": ["Mock output cannot prove generation quality."],
            "candidate_policy": "Use candidate fixture rows when present.",
        },
        "route": {
            "route_summary": "Mock route assembled from candidate fixture order.",
            "intended_item_count": len(items),
            "items": items,
        },
        "completion_criteria": {
            "min_items_to_play": min(3, len(items)),
            "min_primary_reactions": min(3, len(items)),
            "primary_reaction_policy": "Primary reactions are counted once per route item and are separate from optional chip selections.",
            "min_chip_selections_for_summary": 0,
            "chip_selection_policy": "Chip selections refine signal meaning but do not substitute for primary reactions.",
            "completion_logic": "Collect primary reactions first, then optional chips, then review evidence manually.",
        },
        "review_config": {
            "requires_human_review": True,
            "ready_for_app_import": False,
            "default_item_review_needed_for": ["risky", "trap", "dead_end_check", "frontier_unknown"],
            "frontier_or_trap_review_policy": "Risky, trap, dead-end, and unknown frontier items default to review-needed before any Atlas change.",
            "review_focus": ["schema smoke test", "fixture wiring", "candidate constraint behavior"],
            "notes": "Generated by --mock.",
        },
        "completion_summary_inputs": [
            {
                "input_id": "summary_signal_pattern",
                "prompt": "Which expected signals actually appeared?",
                "source": "route_item_primary_reactions",
            },
            {
                "input_id": "summary_chip_pattern",
                "prompt": "Which chip selections explain the primary reactions?",
                "source": "chip_selections",
            }
        ],
        "possible_atlas_update_candidates": [
            {
                "candidate_id": "atlas_mock_no_update",
                "trigger_conditions": [
                    {
                        "condition_id": "mock_future_reaction_gate",
                        "future_reaction_operations": ["love", "like"],
                        "required_signal": "A real future reaction repeats the same bounded signal.",
                        "minimum_occurrences": 2,
                        "condition_text": "Only if future primary reactions and chip selections repeat the signal after real listening evidence exists."
                    }
                ],
                "atlas_role": "Signal only",
                "confidence": "low",
                "rationale": "Mock runs must not update Atlas canon.",
                "review_required": True,
            }
        ],
    }


def _mock_chips(reaction: str, features: List[str], is_trap: bool = False) -> List[Dict[str, Any]]:
    label_by_reaction = {
        "love": ["body confirms", "opens route"],
        "like": ["feature works", "needs recurrence"],
        "keep": ["useful waypoint", "context shelf"],
        "not_for_me": ["false-nearby", "no blood"],
    }
    if is_trap:
        label_by_reaction = {
            "love": ["unexpected exception", "reassess dead end"],
            "like": ["cultural furniture", "bounded exception"],
            "keep": ["boundary useful", "context shelf"],
            "not_for_me": ["dead end holds", "false-nearby"],
        }
    labels = label_by_reaction[reaction]
    return [
        {
            "chip_id": f"CHIP_{reaction.upper()}_{index}",
            "label": label,
            "reaction_operation": reaction,
            "chip_type": _mock_chip_type(reaction, index, is_trap),
            "signal_meaning": _mock_chip_meaning(reaction, label, is_trap),
            "mapped_canonical_feature_id": features[min(index - 1, len(features) - 1)] if features else "",
            "atlas_effect_hint": _mock_atlas_effect_hint(reaction, is_trap),
            "weight_hint": "low" if is_trap and reaction in {"love", "like"} else "medium",
            "uses_user_vocabulary": True,
        }
        for index, label in enumerate(labels, start=1)
    ]


def _mock_chip_type(reaction: str, index: int, is_trap: bool) -> str:
    if not is_trap:
        return "feature_signal" if index == 1 else "route_signal"
    if reaction == "love":
        return "unexpected_exception_signal" if index == 1 else "reassess_dead_end_signal"
    if reaction == "like":
        return "cultural_furniture_signal" if index == 1 else "unexpected_exception_signal"
    if reaction == "keep":
        return "boundary_signal"
    return "dead_end_signal"


def _mock_chip_meaning(reaction: str, label: str, is_trap: bool) -> str:
    if not is_trap:
        return f"Mock signal for {reaction}: {label}."
    if reaction in {"love", "like"}:
        return f"Positive trap response means {label}; treat as conditional evidence, not forced negative interpretation."
    return f"Trap response means {label}; use it to refine the boundary."


def _mock_atlas_effect_hint(reaction: str, is_trap: bool) -> str:
    if is_trap and reaction in {"love", "like"}:
        return "Record as possible unexpected exception / cultural furniture / reassess dead end; require future recurrence before Atlas change."
    return "Record as bounded signal only."


if __name__ == "__main__":
    sys.exit(main())
