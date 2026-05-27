from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class OpenAIConfig:
    model: str
    api_key: str
    api_style: str = "responses"
    base_url: str = "https://api.openai.com/v1"
    temperature: Optional[float] = None
    max_output_tokens: Optional[int] = 12000
    reasoning_effort: Optional[str] = None
    timeout_seconds: int = 120


def config_from_env(
    model: Optional[str] = None,
    api_style: Optional[str] = None,
    temperature: Optional[float] = None,
    max_output_tokens: Optional[int] = None,
    reasoning_effort: Optional[str] = None,
    timeout_seconds: Optional[int] = None,
) -> OpenAIConfig:
    api_key = os.environ.get("OPENAI_API_KEY", "")
    configured_model = model or os.environ.get("WAYMARK_OPENAI_MODEL") or os.environ.get("OPENAI_MODEL") or "gpt-4.1"
    configured_style = api_style or os.environ.get("WAYMARK_OPENAI_API_STYLE", "responses")
    configured_base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")

    env_temperature = os.environ.get("WAYMARK_OPENAI_TEMPERATURE")
    if temperature is None and env_temperature:
        temperature = float(env_temperature)

    env_max_output = os.environ.get("WAYMARK_OPENAI_MAX_OUTPUT_TOKENS")
    if max_output_tokens is None and env_max_output:
        max_output_tokens = int(env_max_output)

    env_reasoning = os.environ.get("WAYMARK_OPENAI_REASONING_EFFORT")
    if reasoning_effort is None and env_reasoning:
        reasoning_effort = env_reasoning

    env_timeout = os.environ.get("WAYMARK_OPENAI_TIMEOUT_SECONDS")
    if timeout_seconds is None and env_timeout:
        timeout_seconds = int(env_timeout)

    return OpenAIConfig(
        model=configured_model,
        api_key=api_key,
        api_style=configured_style,
        base_url=configured_base_url,
        temperature=temperature,
        max_output_tokens=max_output_tokens if max_output_tokens is not None else 12000,
        reasoning_effort=reasoning_effort,
        timeout_seconds=timeout_seconds if timeout_seconds is not None else 120,
    )


def build_request_payload(
    config: OpenAIConfig,
    system_prompt: str,
    user_prompt: str,
    output_schema: Dict[str, Any],
    schema_name: str = "waymark_mission_output_v0_1",
) -> Dict[str, Any]:
    if config.api_style == "chat_completions":
        payload: Dict[str, Any] = {
            "model": config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": schema_name,
                    "strict": True,
                    "schema": output_schema,
                },
            },
        }
        if config.temperature is not None:
            payload["temperature"] = config.temperature
        if config.max_output_tokens is not None:
            payload["max_tokens"] = config.max_output_tokens
        return payload

    payload = {
        "model": config.model,
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
                "name": schema_name,
                "strict": True,
                "schema": output_schema,
            }
        },
    }
    if config.temperature is not None:
        payload["temperature"] = config.temperature
    if config.max_output_tokens is not None:
        payload["max_output_tokens"] = config.max_output_tokens
    if config.reasoning_effort:
        payload["reasoning"] = {"effort": config.reasoning_effort}
    return payload


def call_openai(config: OpenAIConfig, payload: Dict[str, Any]) -> Dict[str, Any]:
    if not config.api_key:
        raise RuntimeError("OPENAI_API_KEY is not set. Use --mock or --dry-run for offline harness checks.")

    endpoint = "chat/completions" if config.api_style == "chat_completions" else "responses"
    url = f"{config.base_url}/{endpoint}"

    try:
        return _post_openai_json(url, config.api_key, payload, config.timeout_seconds)
    except RuntimeError as error:
        if "temperature" in payload and _looks_like_unsupported_parameter_error(str(error), "temperature"):
            retry_payload = json.loads(json.dumps(payload))
            retry_payload.pop("temperature", None)
            return _post_openai_json(url, config.api_key, retry_payload, config.timeout_seconds)
        raise


def _post_openai_json(url: str, api_key: str, payload: Dict[str, Any], timeout_seconds: int) -> Dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
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
        error_body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI API error {error.code}: {error_body}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"OpenAI API request failed: {error}") from error


def _looks_like_unsupported_parameter_error(error_text: str, parameter_name: str) -> bool:
    lowered = error_text.lower()
    parameter = parameter_name.lower()
    return parameter in lowered and any(term in lowered for term in ["unsupported", "not support", "unknown parameter", "invalid parameter"])


def extract_output_text(raw_response: Dict[str, Any]) -> str:
    if isinstance(raw_response.get("output_text"), str):
        return raw_response["output_text"]

    choices = raw_response.get("choices")
    if isinstance(choices, list) and choices:
        message = choices[0].get("message", {})
        content = message.get("content")
        if isinstance(content, str):
            return content

    chunks = []
    for output_item in raw_response.get("output", []) or []:
        for content_item in output_item.get("content", []) or []:
            if content_item.get("type") in {"output_text", "text"} and isinstance(content_item.get("text"), str):
                chunks.append(content_item["text"])
    return "\n".join(chunks)


def extract_usage(raw_response: Dict[str, Any]) -> Dict[str, Optional[int]]:
    usage = raw_response.get("usage") if isinstance(raw_response, dict) else None
    if not isinstance(usage, dict):
        return {
            "input_tokens": None,
            "cached_input_tokens": None,
            "output_tokens": None,
            "total_tokens": None,
        }

    input_tokens = usage.get("input_tokens", usage.get("prompt_tokens"))
    output_tokens = usage.get("output_tokens", usage.get("completion_tokens"))
    total_tokens = usage.get("total_tokens")
    if total_tokens is None and isinstance(input_tokens, int) and isinstance(output_tokens, int):
        total_tokens = input_tokens + output_tokens

    input_details = usage.get("input_tokens_details")
    if not isinstance(input_details, dict):
        input_details = usage.get("prompt_tokens_details")
    cached_input_tokens = input_details.get("cached_tokens") if isinstance(input_details, dict) else None

    return {
        "input_tokens": input_tokens if isinstance(input_tokens, int) else None,
        "cached_input_tokens": cached_input_tokens if isinstance(cached_input_tokens, int) else None,
        "output_tokens": output_tokens if isinstance(output_tokens, int) else None,
        "total_tokens": total_tokens if isinstance(total_tokens, int) else None,
    }


def parse_json_from_text(text: str) -> Dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()

    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        parsed = json.loads(stripped[start : end + 1])

    if not isinstance(parsed, dict):
        raise ValueError("Model output JSON was not an object.")
    return parsed
