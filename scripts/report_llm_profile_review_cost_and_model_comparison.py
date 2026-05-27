#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_DIR = REPO_ROOT / "data/survey_simulation/llm_profile_review"
PILOT_55_DIR = REVIEW_DIR / "api_pilot_3x3"
PILOT_MINI_DIR = REVIEW_DIR / "api_pilot_3x3_gpt_5_4_mini"
REPORT_PATH = REVIEW_DIR / "reports/token_cost_and_5_4_mini_3x3_comparison.md"
JSON_PATH = REVIEW_DIR / "reports/token_cost_and_5_4_mini_3x3_comparison.json"
GENERATED_AT = "2026-05-20T12:00:00Z"
FULL_MATRIX_MULTIPLIER = 20

PRICING = {
    "gpt-5.5": {
        "input": 5.00,
        "cached_input": 0.50,
        "output": 30.00,
    },
    "gpt-5.4-mini": {
        "input": 0.75,
        "cached_input": 0.075,
        "output": 4.50,
    },
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


def write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


def usage_from_raw(raw_dir: Path) -> dict[str, Any]:
    total = {"input_tokens": 0, "cached_input_tokens": 0, "uncached_input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "calls": 0}
    by_call_type: dict[str, dict[str, int]] = defaultdict(
        lambda: {"input_tokens": 0, "cached_input_tokens": 0, "uncached_input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "calls": 0}
    )
    max_input_tokens = 0
    models = set()
    for path in sorted(raw_dir.glob("*.json")):
        payload = load_json(path)
        usage = payload.get("usage", {})
        input_tokens = int(usage.get("input_tokens", 0))
        cached_tokens = int(usage.get("input_tokens_details", {}).get("cached_tokens", 0))
        output_tokens = int(usage.get("output_tokens", 0))
        total_tokens = int(usage.get("total_tokens", input_tokens + output_tokens))
        uncached_tokens = input_tokens - cached_tokens
        call_type = path.name.split("_raw_response_", 1)[0]
        models.add(payload.get("model", "unknown"))
        max_input_tokens = max(max_input_tokens, input_tokens)
        for target in [total, by_call_type[call_type]]:
            target["input_tokens"] += input_tokens
            target["cached_input_tokens"] += cached_tokens
            target["uncached_input_tokens"] += uncached_tokens
            target["output_tokens"] += output_tokens
            target["total_tokens"] += total_tokens
            target["calls"] += 1
    return {
        "models": sorted(models),
        "total": total,
        "by_call_type": dict(sorted(by_call_type.items())),
        "max_input_tokens_single_call": max_input_tokens,
    }


def cost_for_usage(usage: dict[str, int], rates: dict[str, float], batch: bool = False) -> float:
    multiplier = 0.5 if batch else 1.0
    return (
        (usage["uncached_input_tokens"] / 1_000_000.0) * rates["input"] * multiplier
        + (usage["cached_input_tokens"] / 1_000_000.0) * rates["cached_input"] * multiplier
        + (usage["output_tokens"] / 1_000_000.0) * rates["output"] * multiplier
    )


def cost_table(usage: dict[str, int]) -> list[dict[str, Any]]:
    rows = []
    for model, rates in PRICING.items():
        for mode, batch in [("standard", False), ("batch", True)]:
            pilot_cost = cost_for_usage(usage, rates, batch=batch)
            rows.append(
                {
                    "model": model,
                    "mode": mode,
                    "pilot_3x3_cost_usd": round(pilot_cost, 4),
                    "projected_full_matrix_cost_usd": round(pilot_cost * FULL_MATRIX_MULTIPLIER, 4),
                }
            )
    return rows


def decision_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        for key in ["evidence_decision", "truth_decision"]:
            value = row.get(key)
            if value:
                counts[value] = counts.get(value, 0) + 1
    return counts


def model_quality(metadata_path: Path) -> dict[str, Any]:
    if not metadata_path.exists():
        return {"status": "missing"}
    metadata = load_json(metadata_path)
    rows = metadata.get("rows", [])
    aggregate = metadata.get("aggregate", {})
    completed_rows = [row for row in rows if row.get("truth_score") is not None]
    return {
        "status": metadata.get("status"),
        "model_id": metadata.get("model_id"),
        "call_counts": metadata.get("call_counts", {}),
        "completed_rows": len(completed_rows),
        "aggregate": aggregate,
        "decision_counts": decision_counts(completed_rows),
        "error": metadata.get("error"),
    }


def render_money(value: float | int | None) -> str:
    if value is None:
        return "n/a"
    return f"${float(value):,.2f}"


def render_report(payload: dict[str, Any]) -> str:
    usage = payload["usage_from_gpt_5_5_3x3"]["total"]
    lines = [
        "# Token Cost Estimate and GPT-5.4 Mini 3x3 Comparison",
        "",
        f"Generated: {GENERATED_AT}",
        "",
        "## Scope",
        "",
        "- Full 180-config qualitative matrix was not run.",
        "- Cost projection uses actual completed 3x3 `gpt-5.5` Responses API usage.",
        f"- Full-matrix projection is exactly `{FULL_MATRIX_MULTIPLIER}x` the 3x3 pilot, per authorization.",
        "- `gpt-5.4-mini` quality comparison attempted the same 3x3 prompts, packets, and schemas, but was blocked by API quota before any successful call.",
        "",
        "## Actual 3x3 Token Usage",
        "",
        f"- Calls: `{usage['calls']}`",
        f"- Input tokens: `{usage['input_tokens']:,}`",
        f"- Cached input tokens: `{usage['cached_input_tokens']:,}`",
        f"- Uncached input tokens: `{usage['uncached_input_tokens']:,}`",
        f"- Output tokens: `{usage['output_tokens']:,}`",
        f"- Total tokens: `{usage['total_tokens']:,}`",
        f"- Max single-call input tokens: `{payload['usage_from_gpt_5_5_3x3']['max_input_tokens_single_call']:,}`",
        "",
        "By call type:",
        "",
        "| Call type | Calls | Input | Cached input | Output | Total |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for call_type, item in payload["usage_from_gpt_5_5_3x3"]["by_call_type"].items():
        lines.append(
            f"| `{call_type}` | {item['calls']} | {item['input_tokens']:,} | {item['cached_input_tokens']:,} | {item['output_tokens']:,} | {item['total_tokens']:,} |"
        )

    lines.extend(
        [
            "",
            "## Cost Estimate",
            "",
            "| Model | Mode | 3x3 estimate | Full matrix estimate |",
            "|---|---|---:|---:|",
        ]
    )
    for row in payload["cost_estimates"]:
        lines.append(
            f"| `{row['model']}` | `{row['mode']}` | {render_money(row['pilot_3x3_cost_usd'])} | {render_money(row['projected_full_matrix_cost_usd'])} |"
        )

    quality_55 = payload["quality"]["gpt-5.5"]
    quality_mini = payload["quality"]["gpt-5.4-mini"]
    lines.extend(
        [
            "",
            "## Model Quality Comparison",
            "",
            "| Metric | gpt-5.5 | gpt-5.4-mini |",
            "|---|---:|---:|",
            f"| Schema pass rate | 27/27 | {'n/a' if quality_mini['completed_rows'] == 0 else 'see metadata'} |",
            f"| Average evidence-only evaluator score | {quality_55['aggregate']['scores']['average_evidence_only']} | n/a |",
            f"| Average truth-scored evaluator score | {quality_55['aggregate']['scores']['average_truth_scored']} | n/a |",
            f"| Leakage count | {quality_55['aggregate']['issue_counts']['hidden_context_leakage_count']} | n/a |",
            f"| Blocking red flags | {quality_55['aggregate']['issue_counts']['blocking_red_flag_count']} | n/a |",
            f"| Genre shorthand issue count | {quality_55['aggregate']['issue_counts']['genre_shorthand_issue_count']} | n/a |",
            f"| Direct/contextual counterevidence issue count | {quality_55['aggregate']['issue_counts']['direct_contextual_counterevidence_issue_count']} | n/a |",
            f"| Secondary-lane underdevelopment count | {quality_55['aggregate']['issue_counts']['secondary_lane_underdevelopment_count']} | n/a |",
            "",
            "Mini comparison status:",
            "",
            f"- Status: `{quality_mini['status']}`",
            f"- Completed rows: `{quality_mini['completed_rows']}`",
            f"- Call counts: `{quality_mini['call_counts']}`",
            f"- Error: `{quality_mini['error']}`",
            "",
            "## Decision",
            "",
            "Do not authorize the full matrix yet.",
            "",
            "Reason: cost estimation is complete, but the requested `gpt-5.4-mini` quality comparison did not run because the API returned `insufficient_quota` before any successful mini call. The full matrix should wait until the mini comparison can complete or the team explicitly decides to proceed with `gpt-5.5` only.",
            "",
            "## Pricing Assumptions",
            "",
            "- Prices use OpenAI API pricing checked on 2026-05-20.",
            "- `gpt-5.5`: $5.00 / 1M input, $0.50 / 1M cached input, $30.00 / 1M output.",
            "- `gpt-5.4-mini`: $0.75 / 1M input, $0.075 / 1M cached input, $4.50 / 1M output.",
            "- Batch estimates apply the published 50% Batch API discount to the same token charges.",
            "- This estimate uses the actual `gpt-5.5` token footprint for both model projections; actual mini usage may differ if/when the mini pilot runs.",
            "",
            "Sources: OpenAI API pricing page, including GPT-5.5/GPT-5.4-mini rates and Batch API 50% discount: https://openai.com/api/pricing/",
            "",
        ]
    )
    return "\n".join(lines)


def build() -> None:
    usage_55 = usage_from_raw(PILOT_55_DIR / "raw_api_responses")
    quality_55 = model_quality(PILOT_55_DIR / "api_pilot_3x3_execution_metadata.json")
    quality_mini = model_quality(PILOT_MINI_DIR / "api_pilot_3x3_gpt_5_4_mini_execution_metadata.json")
    payload = {
        "schema_version": "waymark.llm_profile_review_cost_and_model_comparison.v0.1",
        "generated_at": GENERATED_AT,
        "full_matrix_multiplier": FULL_MATRIX_MULTIPLIER,
        "pricing_source": "https://openai.com/api/pricing/",
        "pricing_per_1m_tokens_usd": PRICING,
        "usage_from_gpt_5_5_3x3": usage_55,
        "cost_estimates": cost_table(usage_55["total"]),
        "quality": {
            "gpt-5.5": quality_55,
            "gpt-5.4-mini": quality_mini,
        },
        "decision": {
            "full_matrix_authorized": False,
            "reason": "gpt-5.4-mini comparison blocked by insufficient_quota before any successful mini call",
        },
    }
    write_json(JSON_PATH, payload)
    write_text(REPORT_PATH, render_report(payload))


def main() -> int:
    build()
    print(f"Generated cost/model comparison report at {REPORT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
