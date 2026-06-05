#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DIR = REPO_ROOT / "data/product_contracts/atlas_readout_v0_1"
PROMPTS_DIR = CONTRACT_DIR / "prompts"
SCHEMAS_DIR = CONTRACT_DIR / "schemas"
FIXTURES_DIR = CONTRACT_DIR / "fixtures"
PRICING_PATH = REPO_ROOT / "waymark-ai-tests/fixtures/pricing/openai_pricing_v0_3.json"

SYSTEM_PROMPT_PATH = PROMPTS_DIR / "system_prompt_v0_1.md"
FORMATS_PATH = PROMPTS_DIR / "formats_v0_1.json"
VARIANTS_PATH = PROMPTS_DIR / "variant_instructions_v0_1.json"
MATRIX_PATH = PROMPTS_DIR / "run_matrix_v0_1.json"
BRIEF_PATH = FIXTURES_DIR / "atlas_readout_evidence_brief_sample_v0_1.json"
OUTPUT_SCHEMA_PATH = SCHEMAS_DIR / "atlas_readout_output_v0_1.schema.json"
BRIEF_SCHEMA_PATH = SCHEMAS_DIR / "atlas_readout_evidence_brief_v0_1.schema.json"

DEFAULT_ENV_FILE = REPO_ROOT / "waymark-ai-tests/.env"
DEFAULT_OUT_ROOT = CONTRACT_DIR / "evaluations/prompt_test_v0_1"
OPENAI_RESPONSES_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com").rstrip("/") + "/v1/responses"

RAW_ID_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\bMIS_[A-Z0-9_]+\b",
        r"\bcluster_id\b",
        r"\bmission_id\b",
        r"\bcanonical\b",
        r"\bgraph internals?\b",
        r"\bOpenAI\b",
        r"\bApple payload\b",
        r"\bwaymark\b",
        r"\b[a-z_]+:[a-z0-9_]+\b",
    ]
]
FINAL_TRUTH_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\byou are a grunge fan\b",
        r"\byou are a grunge listener\b",
        r"\bwe know your taste\b",
        r"\bfinal taste\b",
        r"\bonly like guitar\b",
        r"\bdislike theatrical music permanently\b",
        r"\bangry lyrics\b",
    ]
]
TESTING_WORDS = ("test", "confirm", "refine", "probe", "clarify", "check", "boundary", "open")
MARKDOWN_PATTERNS = [re.compile(r"```"), re.compile(r"^\s{0,3}#{1,6}\s", re.MULTILINE)]
KNOWN_ABBREVIATIONS = ("R.E.M.", "U.S.", "v0.1")


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export ") :]
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            parsed = shlex.split(value)
            value = parsed[0] if parsed else ""
        os.environ.setdefault(key, value)


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


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def json_hash(payload: Any) -> str:
    return sha256_text(stable_json(payload))


def validate_with_schema(schema: dict[str, Any], document: Any) -> list[str]:
    try:
        from jsonschema import Draft202012Validator
    except ModuleNotFoundError as error:
        raise RuntimeError("jsonschema is required. Run with .venv/bin/python.") from error

    validator = Draft202012Validator(schema)
    return [
        f"{list(item.path)}: {item.message}"
        for item in sorted(validator.iter_errors(document), key=lambda err: list(err.path))
    ]


def build_user_prompt(format_template: str, variant_instruction: str, brief: dict[str, Any]) -> str:
    compact_brief = json.dumps(brief, ensure_ascii=False, separators=(",", ":"))
    return (
        format_template.replace("{{VARIANT_INSTRUCTION}}", variant_instruction)
        .replace("{{ATLAS_READOUT_EVIDENCE_BRIEF_JSON}}", compact_brief)
    )


def build_request(model_id: str, system_prompt: str, user_prompt: str, output_schema: dict[str, Any]) -> dict[str, Any]:
    return {
        "model": model_id,
        "input": [
            {
                "role": "system",
                "content": [{"type": "input_text", "text": system_prompt}],
            },
            {
                "role": "user",
                "content": [{"type": "input_text", "text": user_prompt}],
            },
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "atlas_readout_output_v0_1",
                "strict": True,
                "schema": output_schema,
            }
        },
        "max_output_tokens": int(os.environ.get("CARTENZA_ATLAS_READOUT_MAX_OUTPUT_TOKENS", "4000")),
        "store": False,
    }


def post_openai(request_payload: dict[str, Any], api_key: str, timeout_seconds: int) -> dict[str, Any]:
    body = json.dumps(request_payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        OPENAI_RESPONSES_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI API HTTP {error.code}: {detail}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"OpenAI API request failed: {error}") from error


def call_with_retries(request_payload: dict[str, Any], api_key: str, timeout_seconds: int) -> tuple[dict[str, Any], int]:
    last_error: RuntimeError | None = None
    for attempt in range(1, 4):
        try:
            return post_openai(request_payload, api_key, timeout_seconds), attempt
        except RuntimeError as error:
            last_error = error
            text = str(error).lower()
            if "insufficient_quota" in text or "invalid_request_error" in text:
                raise
            if attempt < 3 and any(code in text for code in [" 429", " 500", " 502", " 503", " 504", "timed out"]):
                time.sleep(2**attempt)
                continue
            raise
    raise last_error or RuntimeError("OpenAI request failed")


def extract_output_text(raw_response: dict[str, Any]) -> str:
    if isinstance(raw_response.get("output_text"), str):
        return raw_response["output_text"]
    chunks: list[str] = []
    for output_item in raw_response.get("output", []) or []:
        if not isinstance(output_item, dict):
            continue
        for content_item in output_item.get("content", []) or []:
            if (
                isinstance(content_item, dict)
                and content_item.get("type") in {"output_text", "text"}
                and isinstance(content_item.get("text"), str)
            ):
                chunks.append(content_item["text"])
    return "\n".join(chunks)


def extract_usage(raw_response: dict[str, Any]) -> dict[str, int | None]:
    usage = raw_response.get("usage")
    if not isinstance(usage, dict):
        return {
            "input_tokens": None,
            "cached_input_tokens": None,
            "output_tokens": None,
            "reasoning_output_tokens": None,
            "total_tokens": None,
        }
    input_tokens = usage.get("input_tokens", usage.get("prompt_tokens"))
    output_tokens = usage.get("output_tokens", usage.get("completion_tokens"))
    total_tokens = usage.get("total_tokens")
    input_details = usage.get("input_tokens_details") or usage.get("prompt_tokens_details") or {}
    output_details = usage.get("output_tokens_details") or usage.get("completion_tokens_details") or {}
    cached_input_tokens = input_details.get("cached_tokens") if isinstance(input_details, dict) else None
    reasoning_output_tokens = output_details.get("reasoning_tokens") if isinstance(output_details, dict) else None
    if total_tokens is None and isinstance(input_tokens, int) and isinstance(output_tokens, int):
        total_tokens = input_tokens + output_tokens
    return {
        "input_tokens": input_tokens if isinstance(input_tokens, int) else None,
        "cached_input_tokens": cached_input_tokens if isinstance(cached_input_tokens, int) else None,
        "output_tokens": output_tokens if isinstance(output_tokens, int) else None,
        "reasoning_output_tokens": reasoning_output_tokens if isinstance(reasoning_output_tokens, int) else None,
        "total_tokens": total_tokens if isinstance(total_tokens, int) else None,
    }


def estimate_cost(usage: dict[str, int | None], pricing: dict[str, float]) -> dict[str, float | None]:
    input_tokens = usage.get("input_tokens")
    cached_input_tokens = usage.get("cached_input_tokens") or 0
    output_tokens = usage.get("output_tokens")
    if not isinstance(input_tokens, int) or not isinstance(output_tokens, int):
        return {"input_usd": None, "cached_input_usd": None, "output_usd": None, "total_usd": None}
    billable_input_tokens = max(input_tokens - cached_input_tokens, 0)
    input_usd = billable_input_tokens * pricing["input_per_1m"] / 1_000_000
    cached_usd = cached_input_tokens * pricing["cached_input_per_1m"] / 1_000_000
    output_usd = output_tokens * pricing["output_per_1m"] / 1_000_000
    return {
        "input_usd": round(input_usd, 8),
        "cached_input_usd": round(cached_usd, 8),
        "output_usd": round(output_usd, 8),
        "total_usd": round(input_usd + cached_usd + output_usd, 8),
    }


def flatten_strings(payload: Any, *, include_internal: bool) -> list[str]:
    values: list[str] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            if not include_internal and key == "internal_quality_notes":
                continue
            values.extend(flatten_strings(value, include_internal=include_internal))
    elif isinstance(payload, list):
        for value in payload:
            values.extend(flatten_strings(value, include_internal=include_internal))
    elif isinstance(payload, str):
        values.append(payload)
    return values


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?", text))


def sentence_count(text: str) -> int:
    normalized = text
    for abbreviation in KNOWN_ABBREVIATIONS:
        normalized = normalized.replace(abbreviation, abbreviation.replace(".", ""))
    parts = [part.strip() for part in re.split(r"[.!?]+(?:\s+|$)", normalized) if part.strip()]
    return len(parts)


def all_body_fields(output: dict[str, Any]) -> list[tuple[str, str]]:
    fields: list[tuple[str, str]] = []
    for idx, card in enumerate(output.get("signal_cards", []) or []):
        if isinstance(card, dict) and isinstance(card.get("body"), str):
            fields.append((f"signal_cards[{idx}].body", card["body"]))
    summary = output.get("song_shape_summary")
    if isinstance(summary, dict) and isinstance(summary.get("body"), str):
        fields.append(("song_shape_summary.body", summary["body"]))
    for idx, card in enumerate(output.get("uncertainty_cards", []) or []):
        if isinstance(card, dict):
            if isinstance(card.get("body"), str):
                fields.append((f"uncertainty_cards[{idx}].body", card["body"]))
            if isinstance(card.get("why_it_matters"), str):
                fields.append((f"uncertainty_cards[{idx}].why_it_matters", card["why_it_matters"]))
    bridge = output.get("mission_bridge")
    if isinstance(bridge, dict) and isinstance(bridge.get("body"), str):
        fields.append(("mission_bridge.body", bridge["body"]))
    return fields


def allowed_example_set(brief: dict[str, Any]) -> set[str]:
    values: set[str] = set()
    for cluster in brief.get("strong_signal_clusters", []):
        values.update(cluster.get("supporting_examples", []) or [])
    for tag in brief.get("positive_song_affinity_rollup", {}).get("top_affinity_tags", []):
        values.update(tag.get("supporting_examples", []) or [])
    for tension in brief.get("tensions_and_questions", []):
        for field in ("plain_label", "evidence"):
            text = tension.get(field)
            if isinstance(text, str):
                values.add(text)
    return {normalize_example(value) for value in values}


def normalize_example(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("-", "\u2014").strip()).casefold()


def validate_output(output: dict[str, Any], output_schema: dict[str, Any], brief: dict[str, Any]) -> dict[str, Any]:
    fail_reasons: list[str] = []
    warnings: list[str] = []
    schema_errors = validate_with_schema(output_schema, output)
    if schema_errors:
        fail_reasons.extend([f"schema: {error}" for error in schema_errors])

    opening = output.get("opening_read")
    if isinstance(opening, str):
        count = word_count(opening)
        if count < 70 or count > 120:
            fail_reasons.append(f"opening_read_word_count={count}")
    else:
        fail_reasons.append("opening_read_missing")

    for field_name, body in all_body_fields(output):
        count = sentence_count(body)
        if count < 1 or count > 3:
            fail_reasons.append(f"{field_name}_sentence_count={count}")

    user_text = "\n".join(flatten_strings(output, include_internal=False))
    all_text = "\n".join(flatten_strings(output, include_internal=True))
    for pattern in MARKDOWN_PATTERNS:
        if pattern.search(all_text):
            fail_reasons.append(f"markdown_detected:{pattern.pattern}")
            break
    for pattern in RAW_ID_PATTERNS:
        if pattern.search(user_text):
            fail_reasons.append(f"user_facing_raw_or_internal_term:{pattern.pattern}")
    for pattern in FINAL_TRUTH_PATTERNS:
        if pattern.search(user_text):
            fail_reasons.append(f"forbidden_or_final_truth_claim:{pattern.pattern}")
    for sentence in re.split(r"(?<=[.!?])\s+", user_text):
        if re.search(r"\bfinal map\b", sentence, flags=re.IGNORECASE) and not re.search(
            r"\bnot\s+(?:a\s+|the\s+)?final map\b",
            sentence,
            flags=re.IGNORECASE,
        ):
            fail_reasons.append("final_map_claim")

    if re.search(r"\bWipers\b", user_text, flags=re.IGNORECASE):
        for sentence in re.split(r"(?<=[.!?])\s+", user_text):
            if re.search(r"\bWipers\b", sentence, flags=re.IGNORECASE) and re.search(
                r"\b(reject|rejected|dislike|not for me|dead end)\b",
                sentence,
                flags=re.IGNORECASE,
            ):
                fail_reasons.append("wipers_unknown_framed_as_rejection")
    for sentence in re.split(r"(?<=[.!?])\s+", user_text):
        if not re.search(r"\bDecemberists\b", sentence, flags=re.IGNORECASE):
            continue
        if re.search(r"\b(permanent|forever|never|dead end)\b", sentence, flags=re.IGNORECASE) and not re.search(
            r"\bnot\s+(?:a\s+)?(?:permanent|dead end)\b",
            sentence,
            flags=re.IGNORECASE,
        ):
            fail_reasons.append("decemberists_negative_framed_too_permanently")

    bridge = output.get("mission_bridge", {})
    bridge_text = "\n".join(flatten_strings(bridge, include_internal=True))
    if not any(word in bridge_text.casefold() for word in TESTING_WORDS):
        warnings.append("mission_bridge_lacks_testing_language")

    allowed = allowed_example_set(brief)
    for card_idx, card in enumerate(output.get("signal_cards", []) or []):
        examples = card.get("evidence_examples", []) if isinstance(card, dict) else []
        for example in examples:
            if isinstance(example, str) and normalize_example(example) not in allowed:
                warnings.append(f"signal_cards[{card_idx}].evidence_examples may be unsupported: {example}")

    return {
        "schema_valid": not schema_errors,
        "auto_fail": bool(fail_reasons),
        "fail_reasons": fail_reasons,
        "warnings": warnings,
    }


def parse_structured_output(raw_response: dict[str, Any]) -> dict[str, Any]:
    text = extract_output_text(raw_response)
    return json.loads(text)


def build_result_wrapper(
    *,
    run: dict[str, Any],
    model_id: str,
    input_sha256: str,
    prompt_sha256: str,
    output: dict[str, Any],
    validation: dict[str, Any],
    usage: dict[str, int | None],
    cost: dict[str, float | None],
    latency_seconds: float,
    attempt_count: int,
) -> dict[str, Any]:
    gate_decision = "fail" if validation["auto_fail"] else ("review" if validation["warnings"] else "pass")
    return {
        "schema_version": "cartenza.atlas_readout_prompt_test_result.v0.1",
        "run_id": run["run_id"],
        "model_id": model_id,
        "prompt_format_id": run["format_id"],
        "variant_id": run["variant_id"],
        "input_sha256": input_sha256,
        "prompt_sha256": prompt_sha256,
        "output": output,
        "automated_validation": validation,
        "telemetry": {
            "latency_seconds": round(latency_seconds, 3),
            "attempt_count": attempt_count,
            "usage": usage,
            "cost_estimate_usd": cost,
        },
        "rubric_score_status": "not_scored",
        "rubric_scores": {
            "evidence_faithfulness": None,
            "specificity": None,
            "cartenza_voice": None,
            "humility": None,
            "affinity_usefulness": None,
            "mission_bridge_quality": None,
            "ui_readiness": None,
            "brevity": None,
            "false_claim_risk": None,
            "overall_alpha_readiness": None,
        },
        "gate_decision": gate_decision,
    }


def render_report(metadata: dict[str, Any], results: list[dict[str, Any]]) -> str:
    total_cost = sum(
        result.get("telemetry", {}).get("cost_estimate_usd", {}).get("total_usd") or 0
        for result in results
    )
    total_input = sum(result.get("telemetry", {}).get("usage", {}).get("input_tokens") or 0 for result in results)
    total_output = sum(result.get("telemetry", {}).get("usage", {}).get("output_tokens") or 0 for result in results)
    total_cached = sum(result.get("telemetry", {}).get("usage", {}).get("cached_input_tokens") or 0 for result in results)
    failed = [result for result in results if result.get("automated_validation", {}).get("auto_fail")]
    warning_count = sum(len(result.get("automated_validation", {}).get("warnings", [])) for result in results)

    lines = [
        "# Atlas Readout Prompt Test v0.1 Report",
        "",
        f"Generated at: `{metadata['generated_at']}`",
        f"Model: `{metadata['model_id']}`",
        f"Runs completed: `{len(results)}`",
        f"Auto-fail count: `{len(failed)}`",
        f"Warning count: `{warning_count}`",
        f"Total input tokens: `{total_input}`",
        f"Total cached input tokens: `{total_cached}`",
        f"Total output tokens: `{total_output}`",
        f"Estimated total cost: `${total_cost:.6f}`",
        "",
        "Cost uses standard processing rates from the local pricing table, verified against OpenAI pricing on 2026-06-03: input $0.75/1M, cached input $0.075/1M, output $4.50/1M.",
        "",
        "## Per-Run Telemetry",
        "",
        "| Run | Format | Variant | Latency s | Input | Cached | Output | Total tokens | Cost USD | Gate | Notes |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for result in results:
        usage = result["telemetry"]["usage"]
        cost = result["telemetry"]["cost_estimate_usd"]
        validation = result["automated_validation"]
        notes = []
        if validation["fail_reasons"]:
            notes.append(f"{len(validation['fail_reasons'])} fail")
        if validation["warnings"]:
            notes.append(f"{len(validation['warnings'])} warn")
        lines.append(
            "| {run} | {fmt} | {var} | {lat:.3f} | {inp} | {cached} | {out} | {total} | ${cost:.6f} | {gate} | {notes} |".format(
                run=result["run_id"],
                fmt=result["prompt_format_id"],
                var=result["variant_id"],
                lat=result["telemetry"]["latency_seconds"],
                inp=usage.get("input_tokens") or 0,
                cached=usage.get("cached_input_tokens") or 0,
                out=usage.get("output_tokens") or 0,
                total=usage.get("total_tokens") or 0,
                cost=cost.get("total_usd") or 0,
                gate=result["gate_decision"],
                notes=", ".join(notes) if notes else "-",
            )
        )
    lines.extend(["", "## Output Titles", ""])
    for result in results:
        output = result.get("output", {})
        lines.append(
            f"- `{result['run_id']}`: {output.get('readout_title', '')} / {output.get('readout_subtitle', '')}"
        )
    if failed:
        lines.extend(["", "## Auto-Fail Details", ""])
        for result in failed:
            lines.append(f"### {result['run_id']}")
            for reason in result["automated_validation"]["fail_reasons"]:
                lines.append(f"- {reason}")
            lines.append("")
    warning_results = [result for result in results if result["automated_validation"]["warnings"]]
    if warning_results:
        lines.extend(["", "## Warning Details", ""])
        for result in warning_results:
            lines.append(f"### {result['run_id']}")
            for warning in result["automated_validation"]["warnings"]:
                lines.append(f"- {warning}")
            lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Cartenza Atlas readout 25-prompt OpenAI test.")
    parser.add_argument("--env-file", type=Path, default=DEFAULT_ENV_FILE)
    parser.add_argument("--out-root", type=Path, default=DEFAULT_OUT_ROOT)
    parser.add_argument("--run-id", help="Optional single run id, e.g. A01, for smoke testing.")
    parser.add_argument("--timeout-seconds", type=int, default=180)
    args = parser.parse_args()

    load_env_file(args.env_file)
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("BLOCKED: OPENAI_API_KEY is not set after loading env file.", file=sys.stderr)
        return 2

    system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    formats = {item["format_id"]: item for item in load_json(FORMATS_PATH)["formats"]}
    variants = {item["variant_id"]: item for item in load_json(VARIANTS_PATH)["variants"]}
    matrix = load_json(MATRIX_PATH)
    runs = matrix["runs"]
    if args.run_id:
        runs = [run for run in runs if run["run_id"] == args.run_id]
        if not runs:
            print(f"Unknown run id: {args.run_id}", file=sys.stderr)
            return 2

    model_id = matrix["model_id"]
    pricing_table = load_json(PRICING_PATH)
    pricing = pricing_table["models"][model_id]
    brief = load_json(BRIEF_PATH)
    brief_schema = load_json(BRIEF_SCHEMA_PATH)
    output_schema = load_json(OUTPUT_SCHEMA_PATH)
    brief_errors = validate_with_schema(brief_schema, brief)
    if brief_errors:
        print(f"Evidence brief failed schema validation: {brief_errors}", file=sys.stderr)
        return 1

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = args.out_root / timestamp
    request_dir = out_dir / "executed_requests"
    raw_dir = out_dir / "raw_api_responses"
    output_dir = out_dir / "structured_outputs"
    result_dir = out_dir / "result_wrappers"

    metadata = {
        "schema_version": "cartenza.atlas_readout_prompt_test_execution.v0.1",
        "generated_at": timestamp,
        "model_id": model_id,
        "responses_url": OPENAI_RESPONSES_URL,
        "input_sha256": sha256_file(BRIEF_PATH),
        "brief_schema_sha256": sha256_file(BRIEF_SCHEMA_PATH),
        "output_schema_sha256": sha256_file(OUTPUT_SCHEMA_PATH),
        "system_prompt_sha256": sha256_file(SYSTEM_PROMPT_PATH),
        "formats_sha256": sha256_file(FORMATS_PATH),
        "variants_sha256": sha256_file(VARIANTS_PATH),
        "matrix_sha256": sha256_file(MATRIX_PATH),
        "pricing_source": str(PRICING_PATH.relative_to(REPO_ROOT)),
        "pricing_table_version": pricing_table.get("pricing_table_version"),
        "pricing_table_date": pricing_table.get("pricing_table_date"),
    }

    results: list[dict[str, Any]] = []
    write_json(out_dir / "execution_metadata.json", metadata)
    for index, run in enumerate(runs, start=1):
        run_id = run["run_id"]
        prompt_format = formats[run["format_id"]]
        variant = variants[run["variant_id"]]
        user_prompt = build_user_prompt(prompt_format["user_prompt_template"], variant["instruction"], brief)
        prompt_sha256 = sha256_text(system_prompt + "\n\n" + user_prompt)
        request_payload = build_request(model_id, system_prompt, user_prompt, output_schema)
        write_json(request_dir / f"{run_id}.json", request_payload)

        print(f"[{index}/{len(runs)}] {run_id} {prompt_format['label']} / {variant['label']}...", flush=True)
        started = time.monotonic()
        try:
            raw_response, attempt_count = call_with_retries(request_payload, api_key, args.timeout_seconds)
            latency = time.monotonic() - started
            write_json(raw_dir / f"{run_id}.json", raw_response)
            output = parse_structured_output(raw_response)
            write_json(output_dir / f"{run_id}.json", output)
            usage = extract_usage(raw_response)
            cost = estimate_cost(usage, pricing)
            validation = validate_output(output, output_schema, brief)
            result = build_result_wrapper(
                run=run,
                model_id=model_id,
                input_sha256=metadata["input_sha256"],
                prompt_sha256=prompt_sha256,
                output=output,
                validation=validation,
                usage=usage,
                cost=cost,
                latency_seconds=latency,
                attempt_count=attempt_count,
            )
            write_json(result_dir / f"{run_id}.json", result)
            results.append(result)
            print(
                f"  ok latency={latency:.3f}s input={usage.get('input_tokens')} output={usage.get('output_tokens')} cost=${cost.get('total_usd')}",
                flush=True,
            )
        except Exception as error:
            latency = time.monotonic() - started
            error_payload = {
                "run": run,
                "error": str(error),
                "latency_seconds": round(latency, 3),
            }
            write_json(out_dir / "errors" / f"{run_id}.json", error_payload)
            print(f"  failed after {latency:.3f}s: {error}", file=sys.stderr, flush=True)
            if "insufficient_quota" in str(error).lower():
                break
            return 1

    write_json(out_dir / "aggregate_results.json", results)
    write_text(out_dir / "report.md", render_report(metadata, results))
    print(f"Report: {out_dir / 'report.md'}")
    return 0 if len(results) == len(runs) else 1


if __name__ == "__main__":
    raise SystemExit(main())
