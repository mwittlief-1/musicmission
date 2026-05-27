#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_DIR = REPO_ROOT / "data/survey_simulation/llm_profile_review"
PUBLIC_PACKET_CANDIDATES = (
    REVIEW_DIR
    / "public_packets"
    / "cartenza_survey_output_packet_public_profile_01_A2_Al1_S1.json",
    REVIEW_DIR
    / "public_packets"
    / "waymark_survey_output_packet_public_profile_01_A2_Al1_S1.json",
)
PUBLIC_PACKET_PATH = next((path for path in PUBLIC_PACKET_CANDIDATES if path.exists()), PUBLIC_PACKET_CANDIDATES[0])
HIDDEN_TRUTH_PATH = (
    REVIEW_DIR
    / "simulator_private"
    / "hidden_truth_packets"
    / "hidden_truth_public_profile_01_A2_Al1_S1.json"
)
MODEL_ID = os.environ.get("CARTENZA_LLM_MODEL") or os.environ.get("WAYMARK_LLM_MODEL", "gpt-5.5")
GENERATED_AT = "2026-05-20T12:00:00Z"
OPENAI_RESPONSES_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com").rstrip("/") + "/v1/responses"

OUTPUT_DIR = REVIEW_DIR / "api_pilot"
RAW_DIR = OUTPUT_DIR / "raw_api_responses"
REQUEST_DIR = OUTPUT_DIR / "executed_requests"
PROFILE_DIR = OUTPUT_DIR / "generated_taste_profiles"
EVALUATOR_DIR = OUTPUT_DIR / "evaluator_scores"
REPORT_PATH = REVIEW_DIR / "reports" / "api_pilot_execution_report.md"
METADATA_PATH = OUTPUT_DIR / "api_pilot_execution_metadata.json"
WRITER_OUTPUT_PATH = PROFILE_DIR / "profile_writer_public_profile_01_A2_Al1_S1.json"
EVIDENCE_EVALUATOR_OUTPUT_PATH = EVALUATOR_DIR / "evaluator_evidence_only_public_profile_01_A2_Al1_S1.json"
TRUTH_EVALUATOR_OUTPUT_PATH = EVALUATOR_DIR / "evaluator_truth_scored_public_profile_01_A2_Al1_S1.json"


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


def json_hash(payload: Any) -> str:
    return sha256_text(json.dumps(payload, sort_keys=True, separators=(",", ":")))


def strict_schema_request(template_path: Path, model_id: str) -> dict[str, Any]:
    request = load_json(template_path)
    request["model"] = model_id
    request.pop("temperature", None)
    text_format = request.get("text", {}).get("format", {})
    if text_format.get("type") != "json_schema" or text_format.get("strict") is not True:
        raise ValueError(f"{template_path} is not a strict Structured Outputs request")
    return request


def api_post(request_payload: dict[str, Any], api_key: str) -> dict[str, Any]:
    body = json.dumps(request_payload).encode("utf-8")
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
        with urllib.request.urlopen(request, timeout=900) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI API HTTP {error.code}: {detail}") from error


def extract_output_text(response: Any) -> str:
    if isinstance(response, dict) and isinstance(response.get("output_text"), str):
        return response["output_text"]
    if isinstance(response, dict):
        for item in response.get("output", []):
            for content in item.get("content", []):
                if isinstance(content, dict) and content.get("type") in {"output_text", "text"}:
                    text = content.get("text")
                    if isinstance(text, str):
                        return text
        for value in response.values():
            try:
                return extract_output_text(value)
            except ValueError:
                pass
    if isinstance(response, list):
        for item in response:
            try:
                return extract_output_text(item)
            except ValueError:
                pass
    raise ValueError("Could not find output text in API response")


def parse_structured_output(response: dict[str, Any]) -> dict[str, Any]:
    text = extract_output_text(response)
    return json.loads(text)


def validate_json_schema(schema_path: Path, document_path: Path) -> list[str]:
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ModuleNotFoundError as error:
        raise RuntimeError("jsonschema is required for output validation") from error
    schema = load_json(schema_path)
    document = load_json(document_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [
        f"{list(item.path)}: {item.message}"
        for item in sorted(validator.iter_errors(document), key=lambda err: list(err.path))
    ]


def prompt_schema_packet_hashes() -> dict[str, Any]:
    prompt_paths = {
        "profile_writer_system": REVIEW_DIR / "prompts" / "profile_writer_system.md",
        "profile_writer_developer": REVIEW_DIR / "prompts" / "profile_writer_developer.md",
        "profile_evaluator_system": REVIEW_DIR / "prompts" / "profile_evaluator_system.md",
        "profile_evaluator_developer": REVIEW_DIR / "prompts" / "profile_evaluator_developer.md",
    }
    schema_paths = {
        "profile_writer_input": REVIEW_DIR / "schemas" / "profile_writer_input.schema.json",
        "profile_writer_output": REVIEW_DIR / "schemas" / "profile_writer_output.schema.json",
        "profile_evaluator_output": REVIEW_DIR / "schemas" / "profile_evaluator_output.schema.json",
    }
    return {
        "prompt_hashes": {name: sha256_file(path) for name, path in prompt_paths.items()},
        "schema_hashes": {name: sha256_file(path) for name, path in schema_paths.items()},
        "packet_hashes": {
            "public_packet_file_sha256": sha256_file(PUBLIC_PACKET_PATH),
            "public_packet_input_fingerprint": load_json(PUBLIC_PACKET_PATH).get("input_fingerprint"),
            "hidden_truth_file_sha256": sha256_file(HIDDEN_TRUTH_PATH),
        },
    }


def replace_placeholder(payload: Any, writer_output: dict[str, Any]) -> Any:
    if isinstance(payload, dict):
        if payload == {"replace_with": "waymark.profile_writer_output.v0.1 JSON"}:
            return writer_output
        return {key: replace_placeholder(value, writer_output) for key, value in payload.items()}
    if isinstance(payload, list):
        return [replace_placeholder(item, writer_output) for item in payload]
    return payload


def inject_writer_output(request_payload: dict[str, Any], writer_output: dict[str, Any]) -> dict[str, Any]:
    request_payload = replace_placeholder(request_payload, writer_output)
    for message in request_payload.get("input", []):
        for content in message.get("content", []):
            text = content.get("text")
            if not isinstance(text, str) or "waymark.profile_writer_output.v0.1 JSON" not in text:
                continue
            parsed = json.loads(text)
            parsed = replace_placeholder(parsed, writer_output)
            content["text"] = json.dumps(parsed, indent=2)
    return request_payload


def request_contains_forbidden_writer_context(request_payload: dict[str, Any]) -> bool:
    text = json.dumps(request_payload)
    forbidden = [
        "hidden_profile_truth",
        "optional_hidden_truth_packet_for_simulation_only",
        "primary_archetype_affinities",
        "secondary_archetype_affinities",
        "hidden_anti_affinities",
        "Classic Suburban Dad",
        "fake_profile_",
        "hidden_corpus_",
        "display_label",
    ]
    return any(item in text for item in forbidden)


def render_report(metadata: dict[str, Any]) -> str:
    lines = [
        "# API Pilot Execution Report",
        "",
        f"Generated: {GENERATED_AT}",
        "",
        f"- Status: `{metadata['status']}`",
        f"- Model ID: `{metadata['model_id']}`",
        f"- Profile Writer call count: `{metadata['call_counts']['profile_writer']}`",
        f"- Evidence-only Evaluator call count: `{metadata['call_counts']['evaluator_evidence_only']}`",
        f"- Truth-scored Evaluator call count: `{metadata['call_counts']['evaluator_truth_scored']}`",
        "",
        "## Hashes",
        "",
        f"- Public packet file SHA256: `{metadata['hashes']['packet_hashes']['public_packet_file_sha256']}`",
        f"- Public packet input fingerprint: `{metadata['hashes']['packet_hashes']['public_packet_input_fingerprint']}`",
        f"- Profile Writer output schema SHA256: `{metadata['hashes']['schema_hashes']['profile_writer_output']}`",
        f"- Evaluator output schema SHA256: `{metadata['hashes']['schema_hashes']['profile_evaluator_output']}`",
        f"- Profile Writer system prompt SHA256: `{metadata['hashes']['prompt_hashes']['profile_writer_system']}`",
        f"- Profile Writer developer prompt SHA256: `{metadata['hashes']['prompt_hashes']['profile_writer_developer']}`",
        f"- Evaluator system prompt SHA256: `{metadata['hashes']['prompt_hashes']['profile_evaluator_system']}`",
        f"- Evaluator developer prompt SHA256: `{metadata['hashes']['prompt_hashes']['profile_evaluator_developer']}`",
        "",
        "## Response Paths",
        "",
    ]
    for label, path in metadata.get("response_paths", {}).items():
        lines.append(f"- {label}: `{path}`")
    lines.extend(["", "## Validation", ""])
    for name, status in metadata.get("validation_status", {}).items():
        lines.append(f"- {name}: `{status}`")
    if metadata.get("error"):
        lines.extend(["", "## Error", "", f"```text\n{metadata['error']}\n```"])
    lines.append("")
    return "\n".join(lines)


def blocked_metadata(reason: str) -> dict[str, Any]:
    metadata = {
        "schema_version": "waymark.llm_profile_review_api_pilot_execution.v0.1",
        "generated_at": GENERATED_AT,
        "status": "blocked",
        "block_reason": reason,
        "model_id": MODEL_ID,
        "openai_responses_url": OPENAI_RESPONSES_URL,
        "hashes": prompt_schema_packet_hashes(),
        "call_counts": {
            "profile_writer": 0,
            "evaluator_evidence_only": 0,
            "evaluator_truth_scored": 0,
        },
        "response_paths": {},
        "validation_status": {
            "profile_writer_output": "not_run",
            "evaluator_evidence_only_output": "not_run",
            "evaluator_truth_scored_output": "not_run",
            "blind_boundary": "not_run",
        },
        "error": reason,
    }
    write_json(METADATA_PATH, metadata)
    write_text(REPORT_PATH, render_report(metadata))
    return metadata


def main() -> int:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        blocked_metadata("OPENAI_API_KEY is not set in the environment; no API calls were made.")
        print("BLOCKED: OPENAI_API_KEY is not set; no API calls were made.", file=sys.stderr)
        return 2

    metadata = {
        "schema_version": "waymark.llm_profile_review_api_pilot_execution.v0.1",
        "generated_at": GENERATED_AT,
        "status": "running",
        "model_id": MODEL_ID,
        "openai_responses_url": OPENAI_RESPONSES_URL,
        "hashes": prompt_schema_packet_hashes(),
        "call_counts": {
            "profile_writer": 0,
            "evaluator_evidence_only": 0,
            "evaluator_truth_scored": 0,
        },
        "response_paths": {},
        "validation_status": {},
        "error": None,
    }
    try:
        reuse_writer = (
            (
                os.environ.get("CARTENZA_REUSE_PROFILE_WRITER_OUTPUT")
                or os.environ.get("WAYMARK_REUSE_PROFILE_WRITER_OUTPUT")
            )
            == "1"
            and WRITER_OUTPUT_PATH.exists()
        )
        metadata["hashes"]["executed_request_hashes"] = {}
        if reuse_writer:
            writer_output = load_json(WRITER_OUTPUT_PATH)
            writer_errors = validate_json_schema(
                REVIEW_DIR / "schemas" / "profile_writer_output.schema.json",
                WRITER_OUTPUT_PATH,
            )
            if writer_errors:
                raise RuntimeError(f"Existing Profile Writer output failed schema validation: {writer_errors}")
            previous_metadata = load_json(METADATA_PATH) if METADATA_PATH.exists() else {}
            metadata["call_counts"]["profile_writer"] = previous_metadata.get("call_counts", {}).get("profile_writer", 0)
            metadata["response_paths"]["profile_writer_output"] = str(WRITER_OUTPUT_PATH.relative_to(REPO_ROOT))
            metadata["validation_status"]["profile_writer_output"] = "passed"
            metadata["profile_writer_reused"] = True
        else:
            writer_request = strict_schema_request(
                REVIEW_DIR / "api_requests" / "profile_writer_reference_request.json",
                MODEL_ID,
            )
            if request_contains_forbidden_writer_context(writer_request):
                raise RuntimeError("Profile Writer request contains forbidden hidden/private context")
            write_json(REQUEST_DIR / "profile_writer_request.json", writer_request)
            metadata["hashes"]["executed_request_hashes"]["profile_writer"] = json_hash(writer_request)
            writer_raw = api_post(writer_request, api_key)
            metadata["call_counts"]["profile_writer"] += 1
            write_json(RAW_DIR / "profile_writer_raw_response.json", writer_raw)
            writer_output = parse_structured_output(writer_raw)
            write_json(WRITER_OUTPUT_PATH, writer_output)
            metadata["response_paths"]["profile_writer_output"] = str(WRITER_OUTPUT_PATH.relative_to(REPO_ROOT))
            writer_errors = validate_json_schema(
                REVIEW_DIR / "schemas" / "profile_writer_output.schema.json",
                WRITER_OUTPUT_PATH,
            )
            metadata["validation_status"]["profile_writer_output"] = "passed" if not writer_errors else writer_errors
            if writer_errors:
                raise RuntimeError(f"Profile Writer output failed schema validation: {writer_errors}")
            metadata["profile_writer_reused"] = False

        evidence_request = strict_schema_request(
            REVIEW_DIR / "api_requests" / "evaluator_evidence_only_reference_request.json",
            MODEL_ID,
        )
        evidence_request = inject_writer_output(evidence_request, writer_output)
        if "hidden_profile_truth" in json.dumps(evidence_request):
            raise RuntimeError("Evidence-only Evaluator request contains hidden truth")
        if "waymark.profile_writer_output.v0.1 JSON" in json.dumps(evidence_request):
            raise RuntimeError("Evidence-only Evaluator request still contains Profile Writer placeholder")
        write_json(REQUEST_DIR / "evaluator_evidence_only_request.json", evidence_request)
        metadata["hashes"]["executed_request_hashes"]["evaluator_evidence_only"] = json_hash(evidence_request)
        evidence_raw = api_post(evidence_request, api_key)
        metadata["call_counts"]["evaluator_evidence_only"] += 1
        write_json(RAW_DIR / "evaluator_evidence_only_raw_response.json", evidence_raw)
        evidence_output = parse_structured_output(evidence_raw)
        write_json(EVIDENCE_EVALUATOR_OUTPUT_PATH, evidence_output)
        metadata["response_paths"]["evaluator_evidence_only_output"] = str(EVIDENCE_EVALUATOR_OUTPUT_PATH.relative_to(REPO_ROOT))
        evidence_errors = validate_json_schema(
            REVIEW_DIR / "schemas" / "profile_evaluator_output.schema.json",
            EVIDENCE_EVALUATOR_OUTPUT_PATH,
        )
        metadata["validation_status"]["evaluator_evidence_only_output"] = "passed" if not evidence_errors else evidence_errors
        if evidence_errors:
            raise RuntimeError(f"Evidence-only Evaluator output failed schema validation: {evidence_errors}")

        truth_request = strict_schema_request(
            REVIEW_DIR
            / "simulator_private"
            / "api_requests"
            / "evaluator_truth_scored_reference_request.json",
            MODEL_ID,
        )
        truth_request = inject_writer_output(truth_request, writer_output)
        if "hidden_profile_truth" not in json.dumps(truth_request):
            raise RuntimeError("Truth-scored Evaluator request lacks simulator-private hidden truth")
        if "waymark.profile_writer_output.v0.1 JSON" in json.dumps(truth_request):
            raise RuntimeError("Truth-scored Evaluator request still contains Profile Writer placeholder")
        write_json(REQUEST_DIR / "evaluator_truth_scored_request.json", truth_request)
        metadata["hashes"]["executed_request_hashes"]["evaluator_truth_scored"] = json_hash(truth_request)
        truth_raw = api_post(truth_request, api_key)
        metadata["call_counts"]["evaluator_truth_scored"] += 1
        write_json(RAW_DIR / "evaluator_truth_scored_raw_response.json", truth_raw)
        truth_output = parse_structured_output(truth_raw)
        write_json(TRUTH_EVALUATOR_OUTPUT_PATH, truth_output)
        metadata["response_paths"]["evaluator_truth_scored_output"] = str(TRUTH_EVALUATOR_OUTPUT_PATH.relative_to(REPO_ROOT))
        truth_errors = validate_json_schema(
            REVIEW_DIR / "schemas" / "profile_evaluator_output.schema.json",
            TRUTH_EVALUATOR_OUTPUT_PATH,
        )
        metadata["validation_status"]["evaluator_truth_scored_output"] = "passed" if not truth_errors else truth_errors
        if truth_errors:
            raise RuntimeError(f"Truth-scored Evaluator output failed schema validation: {truth_errors}")

        metadata["validation_status"]["blind_boundary"] = "passed"
        metadata["status"] = "completed"
        write_json(METADATA_PATH, metadata)
        write_text(REPORT_PATH, render_report(metadata))
        print(f"Completed API pilot at {OUTPUT_DIR.relative_to(REPO_ROOT)}")
        return 0
    except Exception as error:
        metadata["status"] = "failed"
        metadata["error"] = str(error)
        write_json(METADATA_PATH, metadata)
        write_text(REPORT_PATH, render_report(metadata))
        print(f"FAILED: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
