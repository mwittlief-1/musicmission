from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")


def write_run_report(
    run_dir: Path,
    metadata: Dict[str, Any],
    validation_result: Dict[str, Any],
    score_report: Dict[str, Any],
) -> Path:
    run_type = metadata.get("run_type", metadata.get("api_mode", "unknown"))
    lines = [
        "# Waymark Mission Generation Run Report",
        "",
        f"- Request: `{metadata['request_id']}`",
        f"- Prompt template: `{metadata['prompt_template']}`",
        f"- Context mode: `{metadata['context_mode']}`",
        f"- Model: `{metadata['model']}`",
        f"- Run index: `{metadata['run_index']}`",
        f"- API mode: `{metadata['api_mode']}`",
        f"- Run type: `{run_type}`",
        f"- Created: `{metadata.get('created_at', '')}`",
        f"- Product readiness: `{metadata.get('product_readiness_status', 'unknown')}`",
        f"- App import ready: `{metadata.get('app_import_ready')}`",
        f"- Tokens: input `{_fmt(metadata.get('input_tokens'))}` / cached input `{_fmt(metadata.get('cached_input_tokens'))}` / output `{_fmt(metadata.get('output_tokens'))}` / total `{_fmt(metadata.get('total_tokens'))}`",
        f"- Estimated cost: input `{_fmt_cost(metadata.get('estimated_input_cost_usd'))}` / cached input `{_fmt_cost(metadata.get('estimated_cached_input_cost_usd'))}` / output `{_fmt_cost(metadata.get('estimated_output_cost_usd'))}` / total `{_fmt_cost(metadata.get('estimated_total_cost_usd'))}`",
        f"- Cost status: `{metadata.get('cost_status', 'unknown')}`",
        f"- Pricing table: `{metadata.get('pricing_table_version')}` dated `{metadata.get('pricing_table_date')}`",
        f"- Latency seconds: `{_fmt(metadata.get('latency_seconds'))}`",
        f"- Output directory: `{run_dir}`",
        "",
        "> Cost estimates are for model-comparison and planning. Dashboard reconciliation may differ due to cached tokens, service tier, retries, failed calls, or account-level aggregation.",
        "",
    ]
    if run_type == "mock":
        lines.extend(
            [
                "> Mock runs are schema/harness validation only and must not be interpreted as model-quality or product-quality evidence.",
                "",
            ]
        )

    lines.extend(
        [
            "## Validation",
            "",
            f"- Validator: `{validation_result.get('validator')}`",
            f"- Valid: `{validation_result.get('valid')}`",
            f"- Error count: `{validation_result.get('error_count')}`",
        ]
    )
    for error in validation_result.get("errors", [])[:20]:
        lines.append(f"- {error}")

    lines.extend(
        [
            "",
            "## Automated Checks",
            "",
            f"- Automated score: `{score_report['automated_score']}`",
            f"- Pass / partial / fail: `{score_report['pass_count']} / {score_report['partial_count']} / {score_report['fail_count']}`",
            "",
            "| Check | Status | Detail |",
            "| --- | --- | --- |",
        ]
    )
    for check in score_report["checks"]:
        detail = str(check["detail"]).replace("\n", " ")
        lines.append(f"| `{check['check_id']}` | {check['status']} | {detail} |")

    lines.extend(
        [
            "",
            "## Human Rubric",
            "",
            "Score these manually from 0-3 after reading `parsed_output.json` and listening-risk context.",
            "",
            "| Category | Score | Notes |",
            "| --- | --- | --- |",
        ]
    )
    for rubric in score_report["human_rubric"]:
        lines.append(f"| {rubric['category']} |  |  |")

    report_path = run_dir / "report.md"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def write_summary_report(reports_dir: Path, timestamp: str, run_results: List[Dict[str, Any]]) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    path = reports_dir / f"summary_{timestamp}.md"
    lines = [
        "# Waymark Mission Generation Suite Summary",
        "",
        f"- Runs: `{len(run_results)}`",
        "",
    ]
    if any(result["metadata"].get("run_type") == "mock" for result in run_results):
        lines.extend(
            [
                "> Mock runs are schema/harness validation only and must not be interpreted as model-quality or product-quality evidence.",
                "",
            ]
        )

    lines.extend(
        [
            "## Results",
            "",
            "> Cost estimates are for model-comparison and planning. Dashboard reconciliation may differ due to cached tokens, service tier, retries, failed calls, or account-level aggregation.",
            "",
            "| Request | Prompt | Context | Model | Run Type | Schema Valid | Product Status | App Import | Score | P/P/F | Input Tokens | Cached Input | Output Tokens | Est. Cost | Latency | Run Report |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for result in run_results:
        metadata = result["metadata"]
        score = result["score_report"]
        validation = result["validation_result"]
        lines.append(
            "| "
            f"`{metadata['request_id']}` | "
            f"`{metadata['prompt_template']}` | "
            f"`{metadata['context_mode']}` | "
            f"`{metadata['model']}` | "
            f"`{metadata.get('run_type', '')}` | "
            f"`{validation.get('valid')}` | "
            f"`{metadata.get('product_readiness_status', '')}` | "
            f"`{metadata.get('app_import_ready')}` | "
            f"{score['automated_score']} | "
            f"{score['pass_count']}/{score['partial_count']}/{score['fail_count']} | "
            f"{_fmt(metadata.get('input_tokens'))} | "
            f"{_fmt(metadata.get('cached_input_tokens'))} | "
            f"{_fmt(metadata.get('output_tokens'))} | "
            f"{_fmt_cost(metadata.get('estimated_total_cost_usd'))} | "
            f"{_fmt(metadata.get('latency_seconds'))} | "
            f"{result.get('report_path', '')} |"
        )

    lines.extend(["", "## Comparisons", ""])
    for dimension in ["prompt_template", "context_mode", "model"]:
        lines.append(f"### By {dimension}")
        grouped = _group_average(run_results, dimension)
        if not grouped:
            lines.append("")
            continue
        lines.extend(["", "| Value | Runs | Avg Score | Avg Fails |", "| --- | ---: | ---: | ---: |"])
        for value, stats in grouped:
            lines.append(f"| `{value}` | {stats['runs']} | {stats['avg_score']} | {stats['avg_fails']} |")
        lines.append("")

    failures = _aggregate_failures(run_results)
    lines.extend(
        [
            "## Failure Modes To Inspect",
            "",
            "| Check | Failures | Partials |",
            "| --- | ---: | ---: |",
        ]
    )
    for check_id, counts in failures:
        lines.append(f"| `{check_id}` | {counts['fail']} | {counts['partial']} |")

    lines.extend(
        [
            "",
            "## Next Iteration Notes",
            "",
            "- Compare candidate-constrained runs against unconstrained runs for route specificity and hallucination control.",
            "- Inspect low-scoring chip sets for structurally useless language or missing signal meaning.",
            "- If schema conformance fails repeatedly, simplify the schema before changing product requirements.",
            "- If Atlas misuse appears, tighten anti-overfitting rules in the digest and prompt template.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_model_matrix_report(reports_dir: Path, timestamp: str, run_results: List[Dict[str, Any]]) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    path = reports_dir / f"model_matrix_{timestamp}.md"
    live_results = [result for result in run_results if result["metadata"].get("run_type") == "live_api"]
    model_rows = _model_rankings(live_results)
    recommended_model = model_rows[0][0] if model_rows else "n/a"
    recommendation_basis = "live API runs" if model_rows else "no live API runs"

    lines = [
        "# Waymark Mission Generation Model Matrix",
        "",
        "> Mock runs are schema/harness validation only and must not be interpreted as model-quality or product-quality evidence.",
        "",
        "## Executive Summary",
        "",
        f"- Runs analyzed: `{len(run_results)}`",
        f"- Live API runs: `{len(live_results)}`",
        f"- Current recommendation: `{recommended_model}` based on {recommendation_basis}.",
        "- Cost estimates are for model-comparison and planning. Dashboard reconciliation may differ due to cached tokens, service tier, retries, failed calls, or account-level aggregation.",
        "",
        "## Models Tested",
        "",
    ]
    for model in sorted({result["metadata"]["model"] for result in run_results}):
        lines.append(f"- `{model}`")

    lines.extend(["", "## Requests Tested", ""])
    for request_id in sorted({result["metadata"]["request_id"] for result in run_results}):
        lines.append(f"- `{request_id}`")

    lines.extend(
        [
            "",
            "## Cost / Token / Latency",
            "",
            "| Model | Runs | Pass | Review | Fail | Input Tokens | Cached Input | Output Tokens | Total Tokens | Est. Cost | Avg Cost | Avg Latency | Avg Output Tokens | Notes |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for model, stats in _model_cost_latency_rows(run_results):
        lines.append(
            f"| `{model}` | {stats['runs']} | {stats['pass']} | {stats['review']} | {stats['fail']} | "
            f"{_fmt(stats['input_tokens'])} | {_fmt(stats['cached_input_tokens'])} | {_fmt(stats['output_tokens'])} | "
            f"{_fmt(stats['total_tokens'])} | {_fmt_cost(stats['estimated_total_cost_usd'])} | {_fmt_cost(stats['avg_cost'])} | "
            f"{_fmt(stats['avg_latency'])} | {_fmt(stats['avg_output_tokens'])} | {stats['notes']} |"
        )

    lines.extend(
        [
            "",
            "## Automated Score By Request",
            "",
            "| Request | Model | Auto Score | Pass / Partial / Fail | Schema Valid | Product Status | App Import | Input Tokens | Output Tokens | Est. Cost | Latency | Notes |",
            "| --- | --- | ---: | --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for result in sorted(run_results, key=lambda item: (item["metadata"]["request_id"], item["metadata"]["model"], item["metadata"]["run_index"])):
        metadata = result["metadata"]
        score = result["score_report"]
        lines.append(
            f"| `{metadata['request_id']}` | `{metadata['model']}` | {score['automated_score']} | "
            f"{score['pass_count']} / {score['partial_count']} / {score['fail_count']} | "
            f"`{result['validation_result'].get('valid')}` | `{metadata.get('product_readiness_status', '')}` | `{metadata.get('app_import_ready')}` | "
            f"{_fmt(metadata.get('input_tokens'))} | {_fmt(metadata.get('output_tokens'))} | {_fmt_cost(metadata.get('estimated_total_cost_usd'))} | "
            f"{_fmt(metadata.get('latency_seconds'))} | {_top_failure_note(score)} |"
        )

    lines.extend(
        [
            "",
            "## Product Readiness",
            "",
            "| Request | Model | Run | Schema Valid | Product Status | App Import Ready | Report |",
            "| --- | --- | ---: | --- | --- | --- | --- |",
        ]
    )
    for result in sorted(run_results, key=lambda item: (item["metadata"]["request_id"], item["metadata"]["model"], item["metadata"]["run_index"])):
        metadata = result["metadata"]
        validation = result["validation_result"]
        lines.append(
            f"| `{metadata['request_id']}` | `{metadata['model']}` | {metadata['run_index']} | "
            f"`{validation.get('valid')}` | `{metadata.get('product_readiness_status', '')}` | `{metadata.get('app_import_ready')}` | {result.get('report_path', '')} |"
        )

    lines.extend(
        [
            "",
            "## Repeated Failure Modes By Model",
            "",
            "| Model | Check | Fails | Partials |",
            "| --- | --- | ---: | ---: |",
        ]
    )
    failure_rows = _failure_modes_by_model(run_results)
    if failure_rows:
        for model, check_id, counts in failure_rows:
            lines.append(f"| `{model}` | `{check_id}` | {counts['fail']} | {counts['partial']} |")
    else:
        lines.append("| none | none | 0 | 0 |")

    lines.extend(["", "## Strongest Output Per Request", "", "| Request | Model | Score | Status | Report |", "| --- | --- | ---: | --- | --- |"])
    for request_id, result in _best_by_request(run_results):
        metadata = result["metadata"]
        score = result["score_report"]
        lines.append(
            f"| `{request_id}` | `{metadata['model']}` | {score['automated_score']} | "
            f"`{metadata.get('product_readiness_status', '')}` | {result.get('report_path', '')} |"
        )

    lines.extend(["", "## Weakest Output Per Request", "", "| Request | Model | Score | Status | Report |", "| --- | --- | ---: | --- | --- |"])
    for request_id, result in _worst_by_request(run_results):
        metadata = result["metadata"]
        score = result["score_report"]
        lines.append(
            f"| `{request_id}` | `{metadata['model']}` | {score['automated_score']} | "
            f"`{metadata.get('product_readiness_status', '')}` | {result.get('report_path', '')} |"
        )

    lines.extend(
        [
            "",
            "## Recommendation For Next Model",
            "",
            f"- Start the next live pass with `{recommended_model}` unless manual review contradicts the automated report." if model_rows else "- No model-quality recommendation yet because this report has no live API runs.",
            "- Prefer the cheapest model that has no product failures on the sensitive requests and does not regress trap semantics, Atlas caution, or route shape.",
            "- Draft routing hypothesis: `gpt-5.4-mini` for default full mission generation, `gpt-5.4-nano` for cheap/simple substeps, `gpt-5.4` for hard fallback, `gpt-5.5` for quality ceiling, and `gpt-4.1` as legacy baseline only.",
            "",
            "## Recommendation For Next Prompt / Schema Changes",
            "",
            "- Inspect any repeated `possible_atlas_updates_are_conditional`, `candidate_role_discipline`, and `mission_route_shape` failures first.",
            "- If failures concentrate in one request, fix the fixture or prompt instructions before broadening the model matrix.",
            "- If a smaller model is close but brittle, test a two-step route-then-chip prompt before discarding it.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_context_matrix_report(reports_dir: Path, timestamp: str, run_results: List[Dict[str, Any]]) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    path = reports_dir / f"context_matrix_{timestamp}.md"
    live_results = [result for result in run_results if result["metadata"].get("run_type") == "live_api"]
    best_context = _best_context(live_results or run_results)
    candidate_answer = _candidate_pool_answer(run_results)

    lines = [
        "# Waymark Mission Generation Context Matrix",
        "",
        "> Mock runs are schema/harness validation only and must not be interpreted as model-quality or product-quality evidence.",
        "",
        "## Executive Summary",
        "",
        f"- Runs analyzed: `{len(run_results)}`",
        f"- Live API runs: `{len(live_results)}`",
        f"- Model: `{_single_value(run_results, 'model')}`",
        f"- Current minimum viable default context: `{best_context}`",
        f"- Candidate-pool read: {candidate_answer}",
        "- Cost estimates are for model-comparison and planning. Dashboard reconciliation may differ due to cached tokens, service tier, retries, failed calls, or account-level aggregation.",
        "",
    ]
    if _all_runs_not_evaluable(run_results):
        lines.extend(
            [
                "> All runs in this matrix are API/schema failures, so this report must not be used to infer context quality.",
                "",
            ]
        )
    lines.extend(
        [
            "## Context Summary",
            "",
            "| Context | Runs | Pass | Review | Fail | Avg Score | Avg Cost | Avg Latency | Avg Input Tokens | Avg Output Tokens | Overgeneralization | Candidate Choice | Chip Usefulness | Atlas Caution |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |",
        ]
    )
    for context, stats in _context_summary_rows(run_results):
        lines.append(
            f"| `{context}` | {stats['runs']} | {stats['pass']} | {stats['review']} | {stats['fail']} | "
            f"{stats['avg_score']} | {_fmt_cost(stats['avg_cost'])} | {_fmt(stats['avg_latency'])} | "
            f"{_fmt(stats['avg_input_tokens'])} | {_fmt(stats['avg_output_tokens'])} | "
            f"{stats['overgeneralization']} | {stats['candidate_choice']} | {stats['chip_usefulness']} | {stats['atlas_caution']} |"
        )

    lines.extend(
        [
            "",
            "## Run Details",
            "",
            "| Request | Context | Schema Valid | Product Status | App Import | Auto Score | Human Review Needed | Overgeneralization | Candidate Choice | Chip Usefulness | Atlas Caution | Input Tokens | Output Tokens | Est. Cost | Latency | Notes |",
            "| --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for result in sorted(run_results, key=lambda item: (item["metadata"]["request_id"], _context_sort_key(item["metadata"]["context_mode"]))):
        metadata = result["metadata"]
        score = result["score_report"]
        validation = result["validation_result"]
        categories = _context_failure_categories(score)
        lines.append(
            f"| `{metadata['request_id']}` | `{metadata['context_mode']}` | `{validation.get('valid')}` | "
            f"`{metadata.get('product_readiness_status')}` | `{metadata.get('app_import_ready')}` | {score['automated_score']} | "
            f"{_human_review_needed(metadata)} | {categories['overgeneralization']} | {categories['candidate_choice']} | "
            f"{categories['chip_usefulness']} | {categories['atlas_caution']} | {_fmt(metadata.get('input_tokens'))} | "
            f"{_fmt(metadata.get('output_tokens'))} | {_fmt_cost(metadata.get('estimated_total_cost_usd'))} | "
            f"{_fmt(metadata.get('latency_seconds'))} | {_top_failure_note(score)} |"
        )

    lines.extend(
        [
            "",
            "## Minimum Viable Context By Mission Type",
            "",
            "| Mission Type | Requests Used | Minimum Viable Context | Recommendation |",
            "| --- | --- | --- | --- |",
        ]
    )
    for mission_type, request_ids in _mission_type_requests().items():
        context, note = _minimum_context_for_requests(run_results, request_ids)
        requests_label = ", ".join(f"`{request_id}`" for request_id in request_ids) if request_ids else "not tested"
        lines.append(f"| {mission_type} | {requests_label} | `{context}` | {note} |")

    lines.extend(
        [
            "",
            "## Compression / Removal Candidates",
            "",
        ]
    )
    lines.extend(_compression_notes(run_results))

    lines.extend(
        [
            "",
            "## Next Test",
            "",
            "- Rerun the weakest passing context for each route type 3 times to separate one-off luck from stable sufficiency.",
            "- If non-candidate contexts fail by hallucinating or choosing poor route items, keep candidate pools as mandatory for that route class.",
            "- If `atlas_plus_features` matches full-context quality, compress candidate pools to smaller role-labeled shortlists before retesting.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _group_average(run_results: List[Dict[str, Any]], metadata_key: str) -> List[Any]:
    buckets: Dict[str, List[Dict[str, Any]]] = {}
    for result in run_results:
        value = result["metadata"][metadata_key]
        buckets.setdefault(value, []).append(result)
    rows = []
    for value, results in buckets.items():
        avg_score = sum(result["score_report"]["automated_score"] for result in results) / len(results)
        avg_fails = sum(result["score_report"]["fail_count"] for result in results) / len(results)
        rows.append(
            (
                value,
                {
                    "runs": len(results),
                    "avg_score": round(avg_score, 3),
                    "avg_fails": round(avg_fails, 2),
                },
            )
        )
    rows.sort(key=lambda row: row[1]["avg_score"], reverse=True)
    return rows


def _aggregate_failures(run_results: List[Dict[str, Any]]) -> List[Any]:
    counts: Dict[str, Dict[str, int]] = {}
    for result in run_results:
        for check in result["score_report"]["checks"]:
            item = counts.setdefault(check["check_id"], {"fail": 0, "partial": 0})
            if check["status"] == "fail":
                item["fail"] += 1
            elif check["status"] == "partial":
                item["partial"] += 1
    rows = [(check_id, value) for check_id, value in counts.items() if value["fail"] or value["partial"]]
    rows.sort(key=lambda row: (row[1]["fail"], row[1]["partial"]), reverse=True)
    return rows


def _context_summary_rows(run_results: List[Dict[str, Any]]) -> List[Tuple[str, Dict[str, Any]]]:
    buckets: Dict[str, List[Dict[str, Any]]] = {}
    for result in run_results:
        buckets.setdefault(result["metadata"]["context_mode"], []).append(result)

    rows = []
    for context, results in buckets.items():
        scores = [result["score_report"]["automated_score"] for result in results]
        costs = [result["metadata"].get("estimated_total_cost_usd") for result in results if isinstance(result["metadata"].get("estimated_total_cost_usd"), (int, float))]
        latencies = [result["metadata"].get("latency_seconds") for result in results if isinstance(result["metadata"].get("latency_seconds"), (int, float))]
        input_tokens = [result["metadata"].get("input_tokens") for result in results if isinstance(result["metadata"].get("input_tokens"), int)]
        output_tokens = [result["metadata"].get("output_tokens") for result in results if isinstance(result["metadata"].get("output_tokens"), int)]
        category_rows = [_context_failure_categories(result["score_report"]) for result in results]
        rows.append(
            (
                context,
                {
                    "runs": len(results),
                    "pass": sum(1 for result in results if result["metadata"].get("product_readiness_status") in {"app_import_candidate", "product_pass_candidate"}),
                    "review": sum(1 for result in results if result["metadata"].get("product_readiness_status") == "product_review_needed"),
                    "fail": sum(1 for result in results if result["metadata"].get("product_readiness_status") == "product_fail"),
                    "avg_score": round(sum(scores) / len(scores), 3) if scores else None,
                    "avg_cost": round(sum(costs) / len(costs), 6) if costs else None,
                    "avg_latency": round(sum(latencies) / len(latencies), 3) if latencies else None,
                    "avg_input_tokens": round(sum(input_tokens) / len(input_tokens), 1) if input_tokens else None,
                    "avg_output_tokens": round(sum(output_tokens) / len(output_tokens), 1) if output_tokens else None,
                    "overgeneralization": _summarize_category(category_rows, "overgeneralization"),
                    "candidate_choice": _summarize_category(category_rows, "candidate_choice"),
                    "chip_usefulness": _summarize_category(category_rows, "chip_usefulness"),
                    "atlas_caution": _summarize_category(category_rows, "atlas_caution"),
                },
            )
        )
    rows.sort(key=lambda row: _context_sort_key(row[0]))
    return rows


def _context_failure_categories(score_report: Dict[str, Any]) -> Dict[str, str]:
    checks = {check["check_id"]: check["status"] for check in score_report.get("checks", [])}
    if checks.get("valid_json") == "fail" or checks.get("schema_conformance") == "fail":
        return {
            "overgeneralization": "not_evaluable",
            "candidate_choice": "not_evaluable",
            "chip_usefulness": "not_evaluable",
            "atlas_caution": "not_evaluable",
        }
    groups = {
        "overgeneralization": [
            "known_dead_end_warnings_present",
            "false_nearby_traps_not_promoted",
            "waypoint_landmark_distinction",
            "generated_hypothesis_is_not_evidence",
        ],
        "candidate_choice": [
            "candidate_constrained_uses_pool",
            "candidate_role_discipline",
            "no_duplicate_songs_unless_allowed",
            "route_item_count_expected",
            "expected_archetype_present",
            "risk_ratio_constraints",
            "year_constraints",
        ],
        "chip_usefulness": [
            "all_items_have_four_chip_sets",
            "each_chip_set_has_two_chips",
            "feedback_chips_not_generic",
            "trap_positive_chips_have_exception_semantics",
        ],
        "atlas_caution": [
            "possible_atlas_updates_are_conditional",
            "generated_hypothesis_is_not_evidence",
            "waypoint_landmark_distinction",
            "risky_trap_frontier_items_need_review",
        ],
    }
    return {category: _aggregate_status([checks.get(check_id, "pass") for check_id in check_ids]) for category, check_ids in groups.items()}


def _aggregate_status(statuses: List[str]) -> str:
    if any(status == "fail" for status in statuses):
        return "fail"
    if any(status == "partial" for status in statuses):
        return "partial"
    return "pass"


def _summarize_category(category_rows: List[Dict[str, str]], key: str) -> str:
    not_evaluable = sum(1 for row in category_rows if row[key] == "not_evaluable")
    fail = sum(1 for row in category_rows if row[key] == "fail")
    partial = sum(1 for row in category_rows if row[key] == "partial")
    if not_evaluable:
        return f"{not_evaluable} not evaluable"
    if fail or partial:
        return f"{fail} fail / {partial} partial"
    return "pass"


def _best_context(run_results: List[Dict[str, Any]]) -> str:
    if _all_runs_not_evaluable(run_results):
        return "none_api_failure"
    rows = _context_summary_rows(run_results)
    viable = [
        (context, stats)
        for context, stats in rows
        if stats["fail"] == 0 and stats["pass"] >= max(1, stats["runs"] - stats["review"])
    ]
    if viable:
        return viable[0][0]
    if not rows or all(stats["fail"] > 0 and stats["pass"] == 0 and stats["review"] == 0 for _, stats in rows):
        return "n/a"
    ranked = sorted(rows, key=lambda row: (row[1]["fail"], -row[1]["pass"], -(row[1]["avg_score"] or 0), row[1]["avg_cost"] or 999999))
    return ranked[0][0]


def _minimum_context_for_requests(run_results: List[Dict[str, Any]], request_ids: List[str]) -> Tuple[str, str]:
    if not request_ids:
        return "not_tested", "No simple album-route fixture was included in this v0.4 matrix."
    by_context: Dict[str, List[Dict[str, Any]]] = {}
    for result in run_results:
        if result["metadata"]["request_id"] in request_ids:
            by_context.setdefault(result["metadata"]["context_mode"], []).append(result)
    for context in _context_order():
        results = by_context.get(context, [])
        if len(results) != len(request_ids):
            continue
        if all(result["metadata"].get("product_readiness_status") in {"app_import_candidate", "product_pass_candidate"} for result in results):
            return context, "Viable without product-review flags in this run."
        if all(result["metadata"].get("product_readiness_status") != "product_fail" for result in results):
            return context, "Viable only with review; rerun before adopting as default."
    return "none", "No tested context cleared the product bar."


def _mission_type_requests() -> Dict[str, List[str]]:
    return {
        "Simple album routes": [],
        "Bridge routes": ["nirvana_to_current"],
        "Frontier routes": ["lithuanian_artists_frontier"],
        "Dead-end checks": ["muse_boundary_check"],
        "Open-prompt missions": ["taylor_persona_pop", "modern_safe_risky"],
    }


def _candidate_pool_answer(run_results: List[Dict[str, Any]]) -> str:
    if _all_runs_not_evaluable(run_results):
        return "not evaluable because all live calls failed before model output was produced."
    full = [result for result in run_results if result["metadata"].get("context_mode") == "atlas_plus_features_plus_candidates"]
    no_pool = [result for result in run_results if result["metadata"].get("context_mode") == "atlas_plus_features"]
    if not full or not no_pool:
        return "not enough paired context data yet."
    full_fail = sum(1 for result in full if result["metadata"].get("product_readiness_status") == "product_fail")
    no_pool_fail = sum(1 for result in no_pool if result["metadata"].get("product_readiness_status") == "product_fail")
    if full_fail < no_pool_fail:
        return "candidate pools appear materially helpful and may be essential for at least some route classes."
    if full_fail == 0 and no_pool_fail == 0:
        return "candidate pools may not be universally required, but compare candidate-choice and overgeneralization columns before removing them."
    return "candidate-pool necessity is inconclusive from this run."


def _compression_notes(run_results: List[Dict[str, Any]]) -> List[str]:
    if _all_runs_not_evaluable(run_results):
        return ["- No context-compression conclusion is possible from this run because all calls failed before model output was produced."]
    notes = []
    for request_id in sorted({result["metadata"]["request_id"] for result in run_results}):
        request_results = {
            result["metadata"]["context_mode"]: result
            for result in run_results
            if result["metadata"]["request_id"] == request_id
        }
        viable = [
            context
            for context in _context_order()
            if context in request_results and request_results[context]["metadata"].get("product_readiness_status") in {"app_import_candidate", "product_pass_candidate"}
        ]
        if not viable:
            notes.append(f"- `{request_id}`: no context cleared the no-review product bar; keep full context and inspect failures.")
            continue
        minimum = viable[0]
        if minimum == "thin":
            notes.append(f"- `{request_id}`: thin context cleared this run; Atlas details, registry, and candidates are compression candidates, but rerun for stability.")
        elif minimum == "atlas_digest":
            notes.append(f"- `{request_id}`: full Atlas digest was enough; feature registry and candidate pool may be removable for this route class.")
        elif minimum == "atlas_plus_features":
            notes.append(f"- `{request_id}`: candidate pool may be removable, but keep Atlas digest plus feature registry.")
        else:
            notes.append(f"- `{request_id}`: full candidate-constrained context is still the safest packet.")
    if "listen_to_in_utero" not in {result["metadata"]["request_id"] for result in run_results}:
        notes.append("- Simple album-route guidance is not covered by this matrix; run `listen_to_in_utero` before compressing album-route context.")
    return notes


def _human_review_needed(metadata: Dict[str, Any]) -> str:
    return "no" if metadata.get("product_readiness_status") == "app_import_candidate" else "yes"


def _single_value(run_results: List[Dict[str, Any]], metadata_key: str) -> str:
    values = sorted({str(result["metadata"].get(metadata_key, "")) for result in run_results})
    return values[0] if len(values) == 1 else ", ".join(values)


def _all_runs_not_evaluable(run_results: List[Dict[str, Any]]) -> bool:
    if not run_results:
        return False
    for result in run_results:
        checks = {check["check_id"]: check["status"] for check in result["score_report"].get("checks", [])}
        if checks.get("valid_json") != "fail" and checks.get("schema_conformance") != "fail":
            return False
    return True


def _context_order() -> List[str]:
    return ["thin", "atlas_digest", "atlas_plus_features", "atlas_plus_features_plus_candidates"]


def _context_sort_key(context: str) -> int:
    try:
        return _context_order().index(context)
    except ValueError:
        return len(_context_order())


def _model_cost_latency_rows(run_results: List[Dict[str, Any]]) -> List[Tuple[str, Dict[str, Any]]]:
    buckets: Dict[str, List[Dict[str, Any]]] = {}
    for result in run_results:
        buckets.setdefault(result["metadata"]["model"], []).append(result)

    rows = []
    for model, results in buckets.items():
        metadata_rows = [result["metadata"] for result in results]
        latency_values = [row.get("latency_seconds") for row in metadata_rows if isinstance(row.get("latency_seconds"), (int, float))]
        cost_values = [row.get("estimated_total_cost_usd") for row in metadata_rows if isinstance(row.get("estimated_total_cost_usd"), (int, float))]
        output_values = [row.get("output_tokens") for row in metadata_rows if isinstance(row.get("output_tokens"), int)]
        pass_count = sum(
            1
            for row in metadata_rows
            if row.get("product_readiness_status") in {"app_import_candidate", "product_pass_candidate"}
        )
        review_count = sum(1 for row in metadata_rows if row.get("product_readiness_status") == "product_review_needed")
        fail_count = sum(1 for row in metadata_rows if row.get("product_readiness_status") == "product_fail")
        cost_statuses = sorted({str(row.get("cost_status", "unknown")) for row in metadata_rows})
        rows.append(
            (
                model,
                {
                    "runs": len(results),
                    "pass": pass_count,
                    "review": review_count,
                    "fail": fail_count,
                    "input_tokens": _sum_known(row.get("input_tokens") for row in metadata_rows),
                    "cached_input_tokens": _sum_known(row.get("cached_input_tokens") for row in metadata_rows),
                    "output_tokens": _sum_known(row.get("output_tokens") for row in metadata_rows),
                    "total_tokens": _sum_known(row.get("total_tokens") for row in metadata_rows),
                    "estimated_total_cost_usd": _sum_known(row.get("estimated_total_cost_usd") for row in metadata_rows),
                    "avg_cost": round(sum(cost_values) / len(cost_values), 6) if cost_values else None,
                    "avg_latency": round(sum(latency_values) / len(latency_values), 3) if latency_values else None,
                    "avg_output_tokens": round(sum(output_values) / len(output_values), 1) if output_values else None,
                    "notes": ", ".join(cost_statuses),
                },
            )
        )
    rows.sort(key=lambda row: row[0])
    return rows


def _model_rankings(run_results: List[Dict[str, Any]]) -> List[Tuple[str, Dict[str, Any]]]:
    buckets: Dict[str, List[Dict[str, Any]]] = {}
    for result in run_results:
        buckets.setdefault(result["metadata"]["model"], []).append(result)
    rows = []
    for model, results in buckets.items():
        scores = [result["score_report"]["automated_score"] for result in results]
        fail_count = sum(result["score_report"]["fail_count"] for result in results)
        product_fail_count = sum(1 for result in results if result["metadata"].get("product_readiness_status") == "product_fail")
        latencies = [result["metadata"].get("latency_seconds") for result in results if isinstance(result["metadata"].get("latency_seconds"), (int, float))]
        costs = [result["metadata"].get("estimated_total_cost_usd") for result in results if isinstance(result["metadata"].get("estimated_total_cost_usd"), (int, float))]
        rows.append(
            (
                model,
                {
                    "avg_score": sum(scores) / len(scores),
                    "fail_count": fail_count,
                    "product_fail_count": product_fail_count,
                    "avg_latency": sum(latencies) / len(latencies) if latencies else 999999,
                    "avg_cost": sum(costs) / len(costs) if costs else 999999,
                },
            )
        )
    rows.sort(key=lambda row: (row[1]["product_fail_count"], row[1]["fail_count"], -row[1]["avg_score"], row[1]["avg_cost"], row[1]["avg_latency"]))
    return rows


def _failure_modes_by_model(run_results: List[Dict[str, Any]]) -> List[Tuple[str, str, Dict[str, int]]]:
    counts: Dict[Tuple[str, str], Dict[str, int]] = {}
    for result in run_results:
        model = result["metadata"]["model"]
        for check in result["score_report"]["checks"]:
            if check["status"] not in {"fail", "partial"}:
                continue
            item = counts.setdefault((model, check["check_id"]), {"fail": 0, "partial": 0})
            item[check["status"]] += 1
    rows = [(model, check_id, counts_value) for (model, check_id), counts_value in counts.items()]
    rows.sort(key=lambda row: (row[0], row[2]["fail"], row[2]["partial"]), reverse=True)
    return rows


def _best_by_request(run_results: List[Dict[str, Any]]) -> List[Tuple[str, Dict[str, Any]]]:
    buckets = _by_request(run_results)
    rows = []
    for request_id, results in buckets.items():
        rows.append((request_id, sorted(results, key=_result_quality_key, reverse=True)[0]))
    rows.sort(key=lambda row: row[0])
    return rows


def _worst_by_request(run_results: List[Dict[str, Any]]) -> List[Tuple[str, Dict[str, Any]]]:
    buckets = _by_request(run_results)
    rows = []
    for request_id, results in buckets.items():
        rows.append((request_id, sorted(results, key=_result_quality_key)[0]))
    rows.sort(key=lambda row: row[0])
    return rows


def _by_request(run_results: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    buckets: Dict[str, List[Dict[str, Any]]] = {}
    for result in run_results:
        buckets.setdefault(result["metadata"]["request_id"], []).append(result)
    return buckets


def _result_quality_key(result: Dict[str, Any]) -> Tuple[float, int, int]:
    score = result["score_report"]
    product_status = result["metadata"].get("product_readiness_status")
    status_rank = {
        "app_import_candidate": 4,
        "product_pass_candidate": 3,
        "product_review_needed": 2,
        "schema_valid": 1,
        "mock_only": 0,
        "product_fail": -1,
    }.get(product_status, 0)
    return (score["automated_score"], status_rank, -score["fail_count"])


def _top_failure_note(score_report: Dict[str, Any]) -> str:
    for status in ["fail", "partial"]:
        for check in score_report.get("checks", []):
            if check.get("status") == status:
                return f"{status}: `{check.get('check_id')}`"
    return "OK"


def _sum_known(values: Any) -> Any:
    known = [value for value in values if isinstance(value, (int, float))]
    if not known:
        return None
    total = sum(known)
    return round(total, 6) if isinstance(total, float) else total


def _fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    return str(value)


def _fmt_cost(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"${float(value):.6f}"
