#!/usr/bin/env python3
"""Run Mission Enrichment v0.2 over the Build 45 six-mission packet."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from build_mission_enrichment_input_v0_2 import assemble_input
from prefilter_secondary_tags_v0_2 import DEFAULT_REGISTRY_PATH, load_registry
from validate_mission_enrichment_output_v0_2 import validate_contract, write_markdown_report


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[4]

DEFAULT_SOURCE_PACKET_ROOT = (
    REPO_ROOT / "build/share/cartenza_build45_mission_canonical_graph_packet_2026_06_03_v2/mission_review"
)
DEFAULT_MISSION_SNAPSHOT_PATH = DEFAULT_SOURCE_PACKET_ROOT / "reviewed_mission_catalog_snapshot_v0_1.json"
DEFAULT_AFFINITY_JOIN_PATH = DEFAULT_SOURCE_PACKET_ROOT / "mission_route_song_affinity_tags_v0_1.json"
DEFAULT_PRODUCT_SUMMARY_PATH = DEFAULT_SOURCE_PACKET_ROOT / "product_review_summary_v0_1.json"
DEFAULT_SURVEY_ATOMS_PATH = (
    REPO_ROOT
    / "data/exports/dev/product_review_friend_survey_mission_diagnostics_2026_06_03/derived/survey_response_atoms_flat.json"
)
DEFAULT_ATLAS_BRIEF_PATH = (
    REPO_ROOT / "data/product_contracts/atlas_readout_v0_1/fixtures/atlas_readout_evidence_brief_sample_v0_1.json"
)
DEFAULT_ENV_FILE = REPO_ROOT / "waymark-ai-tests/.env"
DEFAULT_OUTPUT_SCHEMA_PATH = PACKAGE_ROOT / "schemas/mission_enrichment_output_v0_2.schema.json"
DEFAULT_PROMPT_TEMPLATE_PATH = PACKAGE_ROOT / "prompts/mission_enrichment_prompt_v0_2.md"
DEFAULT_PRICING_PATH = REPO_ROOT / "waymark-ai-tests/fixtures/pricing/openai_pricing_v0_3.json"
RUNS_ROOT = PACKAGE_ROOT / "runs"

OPENAI_RESPONSES_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com").rstrip("/") + "/v1/responses"

MISSION_FOCUS_BY_ID = {
    "MIS_ALPHA_SURVEY_OPPORTUNITY_DEPTH_01": "90s alternative and grunge center",
    "MIS_ALPHA_SURVEY_OPPORTUNITY_DEPTH_02": "pre-grunge and source-code alternative",
    "MIS_ALPHA_SURVEY_OPPORTUNITY_BRIDGE_01": "whether the strong early lane bridges into adjacent territory",
    "MIS_ALPHA_SURVEY_OPPORTUNITY_BOUNDARY_01": "where the route becomes weaker, overfamiliar, or cleanly outside the lane",
    "MIS_ALPHA_SURVEY_OPPORTUNITY_CONTEXT_01": "whether the same source signal changes with context and neighboring songs",
    "MIS_ALPHA_SURVEY_OPPORTUNITY_GATEWAY_01": "a low-risk nearby frontier after the required Survey",
}

ALIGNMENT_BY_ROLE = {
    "anchor": "supports_confirmed_pattern",
    "probe": "tests_open_question",
    "stretch": "stretches_known_positive",
    "boundary": "tests_boundary",
    "contrast": "contrast_item",
    "control": "control_item",
    "bridge": "stretches_known_positive",
    "context": "context_dependence_check",
    "comparator": "contrast_item",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


def stable_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def schema_for_openai(schema: Any) -> Any:
    """Return the local contract schema with API-unsupported annotations removed."""

    if isinstance(schema, dict):
        cleaned = {}
        for key, value in schema.items():
            if key in {"$schema", "$id", "uniqueItems"}:
                continue
            if key == "title" and isinstance(value, str):
                continue
            cleaned[key] = schema_for_openai(value)
        if "const" in cleaned and "type" not in cleaned:
            const_value = cleaned["const"]
            if isinstance(const_value, str):
                cleaned["type"] = "string"
            elif isinstance(const_value, bool):
                cleaned["type"] = "boolean"
            elif isinstance(const_value, int):
                cleaned["type"] = "integer"
            elif isinstance(const_value, float):
                cleaned["type"] = "number"
            elif const_value is None:
                cleaned["type"] = "null"
        return cleaned
    if isinstance(schema, list):
        return [schema_for_openai(item) for item in schema]
    return schema


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


def env_first(*names: str) -> str | None:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


def model_from_env(default: str) -> str:
    return env_first("CARTENZA_OPENAI_MODEL", "WAYMARK_OPENAI_MODEL", "OPENAI_MODEL") or default


def max_output_tokens_from_env(default: int) -> int:
    value = env_first("CARTENZA_OPENAI_MAX_OUTPUT_TOKENS", "WAYMARK_OPENAI_MAX_OUTPUT_TOKENS")
    return int(value) if value else default


def temperature_from_env() -> float | None:
    value = env_first("CARTENZA_OPENAI_TEMPERATURE", "WAYMARK_OPENAI_TEMPERATURE")
    return float(value) if value else None


def timeout_from_env(default: int) -> int:
    value = env_first("CARTENZA_OPENAI_TIMEOUT_SECONDS", "WAYMARK_OPENAI_TIMEOUT_SECONDS")
    return int(value) if value else default


def build_user_atlas_context_brief(
    atlas_brief: dict[str, Any],
    product_summary: dict[str, Any],
    missing_affinity_items: list[Any],
) -> dict[str, Any]:
    missing_affinity_item_ids = [
        item.get("item_id", str(item)) if isinstance(item, dict) else str(item)
        for item in missing_affinity_items
    ]
    confirmed = [
        {
            "pattern_id": cluster["cluster_id"],
            "label": cluster["plain_label"],
            "confidence": cluster["confidence"],
            "evidence_type": "survey_readout_cluster",
        }
        for cluster in atlas_brief.get("strong_signal_clusters", [])
    ]

    open_questions = []
    known_boundaries = []
    for tension in atlas_brief.get("tensions_and_questions", []):
        label = tension.get("plain_label", "")
        entry = {
            "label": label,
            "confidence": "medium" if tension.get("question_id") in {"pixies_split_signal", "rem_context_check"} else "low",
            "evidence_type": "survey_tension",
        }
        if tension.get("question_id") == "decemberists_negative":
            entry["boundary_id"] = tension["question_id"]
            known_boundaries.append(entry)
        else:
            entry["question_id"] = tension.get("question_id", label.lower().replace(" ", "_"))
            open_questions.append(entry)

    survey = product_summary.get("survey", {}).get("summary", {})
    missions = product_summary.get("missions", {})
    catalog = missions.get("catalog", {})
    summary = [
        (
            f"Survey captured {survey.get('favorite_count', 0) + survey.get('like_count', 0)} positive, "
            f"{survey.get('fine_count', 0)} ok/waypoint, {survey.get('not_for_me_count', 0)} negative, "
            f"and {survey.get('dont_know_count', 0)} don't-know signal with no quarantined responses."
        ),
        "Treat these missions as tests of early evidence, not a settled taste verdict.",
    ]
    coverage = [
        (
            f"Build 45 packet captured {catalog.get('reviewed_mission_count', missions.get('mission_count', 0))} missions "
            f"and {catalog.get('route_item_count', missions.get('route_item_count', 0))} route items; "
            f"all playback-ready: {str(catalog.get('all_missions_playback_ready', False)).lower()}."
        ),
        (
            f"Exact survey song reuse count: {missions.get('exact_survey_song_reuse_count', 0)}; "
            f"repeated route candidates: {len(missions.get('repeated_route_candidates', []))}."
        ),
        (
            "Song-level affinity tags are available for 33 of 36 route items; missing sidecar rows are left empty "
            "rather than inferred."
        ),
        (
            "Supabase diagnostic upload captured mission IDs only; mission bodies and route items came from the local "
            "Build 45 share packet v2."
        ),
    ]
    if missing_affinity_item_ids:
        coverage.append("Missing affinity item IDs: " + ", ".join(missing_affinity_item_ids))

    return {
        "confirmed_positive_patterns": confirmed,
        "open_questions": open_questions,
        "known_boundaries": known_boundaries,
        "recent_learning_summary": summary,
        "coverage_notes": coverage,
    }


def known_artist_context_from_survey(survey_atoms: list[dict[str, Any]]) -> set[str]:
    states_with_context = {"favorite", "like", "fine", "not_for_me", "dont_know"}
    return {
        atom["title"]
        for atom in survey_atoms
        if atom.get("item_kind") == "artist" and atom.get("state") in states_with_context and atom.get("title")
    }


def affinity_index(affinity_join: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["item_id"]: item for item in affinity_join.get("route_items", [])}


def parse_affinity_tags(raw_tags: list[str]) -> list[dict[str, str]]:
    result = []
    for tag in raw_tags:
        if ":" not in tag:
            continue
        facet, _value = tag.split(":", 1)
        result.append({"tag": tag, "facet": facet})
    return result


def alignment_for_route(mission_type: str, route_role: str) -> str:
    if mission_type == "boundary_test" or route_role == "boundary":
        return "tests_boundary"
    if mission_type == "context_dependence_test" or route_role == "context":
        return "context_dependence_check"
    if mission_type == "gateway_test" and route_role in {"probe", "bridge"}:
        return "frontier_probe"
    return ALIGNMENT_BY_ROLE.get(route_role, "tests_open_question")


def canonical_song_id(item: dict[str, Any]) -> str:
    candidate_id = item.get("candidate_id", "")
    if candidate_id.startswith("canonical_song_recording:"):
        return candidate_id.split(":", 1)[1]
    dedupe_key = item.get("route_batch_dedupe_key", "")
    if dedupe_key.startswith("song_recording:"):
        return dedupe_key.split(":", 1)[1]
    return candidate_id or item["item_id"]


def mission_success_definition(mission: dict[str, Any]) -> str:
    minimum = mission.get("success_bar", {}).get("minimum_reactions_required", len(mission.get("items", [])))
    focus = MISSION_FOCUS_BY_ID.get(mission.get("mission_id", ""), mission.get("brief", "this route"))
    return (
        f"Collect at least {minimum} song reactions so Cartenza can tell whether {focus} is a durable center, "
        "a waypoint, a context split, or a boundary."
    )


def route_item_input(
    mission: dict[str, Any],
    item: dict[str, Any],
    affinity_by_item_id: dict[str, dict[str, Any]],
    known_artist_context: set[str],
) -> dict[str, Any]:
    affinity = affinity_by_item_id.get(item["item_id"], {})
    song_affinity_tags = parse_affinity_tags(affinity.get("affinity_tags", []))
    route_role = item.get("alpha_route_role") or item.get("role") or "probe"
    alignment = alignment_for_route(mission["mission_type"], route_role)
    user_alignment_hints = [{"tag": tag["tag"], "alignment": alignment} for tag in song_affinity_tags]
    context_relevant = mission["mission_type"] == "context_dependence_test" or route_role == "context"
    expected_test_signal = item.get("expected_test_signal")
    why_included = item.get("why_included", "")
    if expected_test_signal:
        why_included = f"{why_included} Expected signal: {expected_test_signal}"

    return {
        "item_id": item["item_id"],
        "canonical_song_recording_id": affinity.get("canonical_song_recording_id") or canonical_song_id(item),
        "sequence": item["sequence"],
        "title": item["title"],
        "artist": item["artist"],
        "year": item.get("year"),
        "route_role": route_role,
        "why_included": why_included,
        "song_affinity_tags": song_affinity_tags,
        "user_alignment_hints": user_alignment_hints,
        "prefiltered_secondary_tag_ids": [],
        "applicability_flags": {
            "has_vocals": True,
            "has_lyrics": True,
            "lyrics_language_known": True,
            "is_instrumental": False,
            "is_live_or_alt_version": False,
            "album_context_relevant": context_relevant,
            "long_form_context_relevant": context_relevant,
        },
        "artist_context_available": item["artist"] in known_artist_context,
    }


def mission_input_payload(
    mission: dict[str, Any],
    user_brief: dict[str, Any],
    affinity_by_item_id: dict[str, dict[str, Any]],
    known_artist_context: set[str],
    registry: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    source_payload = {
        "schema_version": "mission_enrichment_input_v0_2",
        "runtime_context": {
            "surface": "mission_card_and_feedback_chips",
            "mission_ordinal_for_user": 1,
            "max_secondary_tags_per_song": 6,
            "copy_mode": "external_alpha",
            "language_style": "clear_warm_music_literate",
            "avoid_founder_vocabulary": True,
        },
        "user_atlas_context_brief": user_brief,
        "mission_context": {
            "mission_id": mission["mission_id"],
            "mission_type": mission["mission_type"],
            "risk_level": mission["risk_level"],
            "mission_hypothesis": mission.get("hypothesis") or mission.get("brief", ""),
            "why_this_mission_now": mission["why_this_mission_now"],
            "success_definition": mission_success_definition(mission),
        },
        "route_items": [
            route_item_input(mission, item, affinity_by_item_id, known_artist_context)
            for item in sorted(mission.get("items", []), key=lambda candidate: candidate["sequence"])
        ],
        "allowed_secondary_reaction_tags": {},
        "copy_guardrails": [
            "Use early-signal language.",
            "Be specific but cautious.",
            "Mention missions as tests, not proof.",
            "Do not use raw canonical IDs.",
            "Do not say the user is a grunge listener.",
            "Do not make unsupported claims about lyrics unless grounded in supplied tags.",
            "Do not overgeneralize from one artist, album, or song.",
            "Do not mention Apple Music payload, graph internals, Supabase, or OpenAI.",
        ],
    }
    return assemble_input(source_payload, registry, refresh_prefilter=True)


def split_prompt(template: str, input_payload: dict[str, Any]) -> tuple[str, str, str]:
    marker = "Payload:\n\n```json\n{{MISSION_ENRICHMENT_INPUT_JSON}}\n```"
    input_json = json.dumps(input_payload, indent=2, ensure_ascii=False)
    rendered = template.replace("{{MISSION_ENRICHMENT_INPUT_JSON}}", input_json)
    if marker in template:
        system_prompt = template.split("Payload:", 1)[0].strip()
        user_prompt = "Payload:\n\n```json\n" + input_json + "\n```"
        return rendered, system_prompt, user_prompt
    return rendered, "You are enriching a deterministic Cartenza listening mission for app display.", rendered


def build_request(
    model: str,
    system_prompt: str,
    user_prompt: str,
    output_schema: dict[str, Any],
    max_output_tokens: int,
    temperature: float | None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": model,
        "input": [
            {"role": "system", "content": [{"type": "input_text", "text": system_prompt}]},
            {"role": "user", "content": [{"type": "input_text", "text": user_prompt}]},
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "mission_enrichment_output_v0_2",
                "strict": True,
                "schema": output_schema,
            }
        },
        "max_output_tokens": max_output_tokens,
        "store": False,
    }
    if temperature is not None:
        payload["temperature"] = temperature
    return payload


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


def call_with_retries(
    request_payload: dict[str, Any],
    api_key: str,
    timeout_seconds: int,
    max_attempts: int,
) -> tuple[dict[str, Any], int]:
    last_error: RuntimeError | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return post_openai(request_payload, api_key, timeout_seconds), attempt
        except RuntimeError as error:
            last_error = error
            text = str(error).lower()
            if any(term in text for term in ["insufficient_quota", "invalid_api_key", "model_not_found"]):
                raise
            if attempt < max_attempts and any(term in text for term in [" 429", " 500", " 502", " 503", " 504", "timed out"]):
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


def parse_model_json(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    return json.loads(stripped)


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


def estimate_cost(usage: dict[str, int | None], pricing: dict[str, float] | None) -> dict[str, float | None]:
    if pricing is None:
        return {"input_usd": None, "cached_input_usd": None, "output_usd": None, "total_usd": None}
    input_tokens = usage.get("input_tokens")
    output_tokens = usage.get("output_tokens")
    cached_input_tokens = usage.get("cached_input_tokens") or 0
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


def pricing_for_model(pricing_path: Path, model: str) -> dict[str, float] | None:
    if not pricing_path.exists():
        return None
    pricing = load_json(pricing_path).get("models", {})
    return pricing.get(model)


def mission_summary(output: dict[str, Any], input_payload: dict[str, Any], report: dict[str, Any]) -> dict[str, Any]:
    mission_copy = output.get("mission_copy", {})
    tags_by_item = {
        block.get("item_id"): [tag.get("tag_id") for tag in block.get("tags", [])]
        for block in output.get("secondary_reaction_tag_candidates", [])
    }
    return {
        "mission_id": output.get("mission_id"),
        "source_mission_title": input_payload["mission_context"]["mission_id"],
        "generated_title": mission_copy.get("title"),
        "generated_subtitle": mission_copy.get("subtitle"),
        "why_now": mission_copy.get("why_now"),
        "listen_for": mission_copy.get("listen_for", []),
        "validation_passed": report["passed"],
        "route_item_count": len(input_payload.get("route_items", [])),
        "missing_affinity_items": [
            item["item_id"] for item in input_payload.get("route_items", []) if not item.get("song_affinity_tags")
        ],
        "tag_ids_by_item": tags_by_item,
    }


def write_run_summary(run_dir: Path, summary: dict[str, Any]) -> None:
    write_json(run_dir / "batch_summary.json", summary)
    lines = [
        "# Build 45 Mission Enrichment Batch v0.2",
        "",
        f"Run ID: `{summary['run_id']}`",
        f"Mode: `{summary['mode']}`",
        f"Model: `{summary['model']}`",
        f"Started UTC: `{summary['started_at']}`",
        f"Completed UTC: `{summary['completed_at']}`",
        f"Validation passed: `{str(summary['all_validation_passed']).lower()}`",
        f"OpenAI calls attempted: `{summary['openai_calls_attempted']}`",
        f"OpenAI calls succeeded: `{summary['openai_calls_succeeded']}`",
        "",
        "## Data Findings",
        "",
    ]
    lines.extend([f"- {finding}" for finding in summary["data_findings"]])
    lines.extend(["", "## Mission Outputs", ""])
    for mission in summary["missions"]:
        lines.extend(
            [
                f"### {mission['mission_id']}",
                "",
                f"- Validation passed: `{str(mission['validation_passed']).lower()}`",
                f"- Title: {mission.get('generated_title')}",
                f"- Subtitle: {mission.get('generated_subtitle')}",
                f"- Why now: {mission.get('why_now')}",
                f"- Listen for: {'; '.join(mission.get('listen_for', []))}",
            ]
        )
        if mission.get("missing_affinity_items"):
            lines.append(f"- Missing affinity rows: {', '.join(mission['missing_affinity_items'])}")
        lines.append("")
    write_text(run_dir / "batch_summary.md", "\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mission-snapshot", default=DEFAULT_MISSION_SNAPSHOT_PATH, type=Path)
    parser.add_argument("--affinity-join", default=DEFAULT_AFFINITY_JOIN_PATH, type=Path)
    parser.add_argument("--product-summary", default=DEFAULT_PRODUCT_SUMMARY_PATH, type=Path)
    parser.add_argument("--survey-atoms", default=DEFAULT_SURVEY_ATOMS_PATH, type=Path)
    parser.add_argument("--atlas-brief", default=DEFAULT_ATLAS_BRIEF_PATH, type=Path)
    parser.add_argument("--registry", default=DEFAULT_REGISTRY_PATH, type=Path)
    parser.add_argument("--output-schema", default=DEFAULT_OUTPUT_SCHEMA_PATH, type=Path)
    parser.add_argument("--prompt-template", default=DEFAULT_PROMPT_TEMPLATE_PATH, type=Path)
    parser.add_argument("--pricing", default=DEFAULT_PRICING_PATH, type=Path)
    parser.add_argument("--env-file", default=DEFAULT_ENV_FILE, type=Path)
    parser.add_argument("--model", help="Override env-configured OpenAI model.")
    parser.add_argument("--run-dir", type=Path)
    parser.add_argument("--mission-id", action="append", dest="mission_ids", help="Run only the selected mission ID. Repeatable.")
    parser.add_argument("--continue-on-error", action="store_true", help="Continue selected batch when one mission fails.")
    parser.add_argument("--dry-run", action="store_true", help="Build inputs and prompts without calling OpenAI.")
    parser.add_argument("--timeout-seconds", type=int)
    parser.add_argument("--max-attempts", type=int, default=3)
    args = parser.parse_args()

    load_env_file(args.env_file)
    model = args.model or model_from_env("gpt-5.4-mini")
    max_output_tokens = max_output_tokens_from_env(12000)
    temperature = temperature_from_env()
    timeout_seconds = args.timeout_seconds or timeout_from_env(180)
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not args.dry_run and not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set; pass --dry-run to build inputs/prompts only.")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"build45_six_mission_enrichment_v0_2_{timestamp}"
    run_dir = args.run_dir or RUNS_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    registry_payload = load_json(args.registry)
    registry = load_registry(args.registry)
    output_schema = load_json(args.output_schema)
    openai_output_schema = schema_for_openai(output_schema)
    prompt_template = args.prompt_template.read_text(encoding="utf-8")
    mission_snapshot = load_json(args.mission_snapshot)
    affinity_join = load_json(args.affinity_join)
    product_summary = load_json(args.product_summary)
    atlas_brief = load_json(args.atlas_brief)
    survey_atoms = load_json(args.survey_atoms)

    missing_affinity_item_ids = affinity_join.get("missing_affinity_tag_items", [])
    user_brief = build_user_atlas_context_brief(atlas_brief, product_summary, missing_affinity_item_ids)
    known_artist_context = known_artist_context_from_survey(survey_atoms)
    affinity_by_item_id = affinity_index(affinity_join)
    pricing = pricing_for_model(args.pricing, model)
    mission_filter = set(args.mission_ids or [])
    indexed_missions = [
        (ordinal, mission)
        for ordinal, mission in enumerate(mission_snapshot["app_missions"], start=1)
        if not mission_filter or mission["mission_id"] in mission_filter
    ]
    if mission_filter:
        found = {mission["mission_id"] for _ordinal, mission in indexed_missions}
        missing = sorted(mission_filter - found)
        if missing:
            raise RuntimeError(f"Mission IDs not found in source snapshot: {', '.join(missing)}")

    write_json(
        run_dir / "source_manifest.json",
        {
            "run_id": run_id,
            "mission_snapshot": str(args.mission_snapshot),
            "mission_snapshot_sha256": stable_hash(mission_snapshot),
            "affinity_join": str(args.affinity_join),
            "affinity_join_sha256": stable_hash(affinity_join),
            "product_summary": str(args.product_summary),
            "product_summary_sha256": stable_hash(product_summary),
            "atlas_brief": str(args.atlas_brief),
            "atlas_brief_sha256": stable_hash(atlas_brief),
            "survey_atoms": str(args.survey_atoms),
            "survey_atoms_sha256": stable_hash(survey_atoms),
            "registry": str(args.registry),
            "registry_sha256": stable_hash(registry_payload),
            "model": model,
            "max_output_tokens": max_output_tokens,
            "temperature": temperature,
            "mode": "dry_run" if args.dry_run else "live_openai",
            "selected_mission_ids": sorted(mission_filter) if mission_filter else "all",
            "openai_schema_note": "Removed API-unsupported schema annotations/keywords for Structured Outputs; local validation uses the full v0.2 schema.",
        },
    )
    write_json(run_dir / "derived_user_atlas_context_brief.json", user_brief)

    started_at = datetime.now(timezone.utc).isoformat()
    mission_summaries: list[dict[str, Any]] = []
    model_logs: list[dict[str, Any]] = []
    calls_attempted = 0
    calls_succeeded = 0
    all_passed = True

    for ordinal, mission in indexed_missions:
        mission_id = mission["mission_id"]
        mission_dir = run_dir / "missions" / mission_id
        input_payload = mission_input_payload(mission, user_brief, affinity_by_item_id, known_artist_context, registry)
        input_payload["runtime_context"]["mission_ordinal_for_user"] = ordinal
        prompt, system_prompt, user_prompt = split_prompt(prompt_template, input_payload)
        request_payload = build_request(
            model=model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            output_schema=openai_output_schema,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
        )

        write_json(mission_dir / "input.json", input_payload)
        write_text(mission_dir / "prompt.md", prompt)
        write_json(mission_dir / "request_payload.json", request_payload)

        if args.dry_run:
            report = {
                "passed": False,
                "error_count": 0,
                "warning_count": 1,
                "errors": [],
                "warnings": ["Dry run only; no OpenAI output was validated."],
            }
            all_passed = False
            write_json(mission_dir / "validation_report.json", report)
            model_log = {
                "mission_id": mission_id,
                "mode": "dry_run",
                "model": model,
                "openai_call_attempted": False,
            }
            write_json(mission_dir / "cost_latency_model_log.json", model_log)
            model_logs.append(model_log)
            mission_summaries.append(
                {
                    "mission_id": mission_id,
                    "generated_title": None,
                    "generated_subtitle": None,
                    "why_now": None,
                    "listen_for": [],
                    "validation_passed": False,
                    "route_item_count": len(input_payload.get("route_items", [])),
                    "missing_affinity_items": [
                        item["item_id"] for item in input_payload.get("route_items", []) if not item.get("song_affinity_tags")
                    ],
                    "tag_ids_by_item": {},
                }
            )
            continue

        calls_attempted += 1
        call_started = time.time()
        try:
            raw_response, attempts = call_with_retries(request_payload, api_key, timeout_seconds, args.max_attempts)
            latency_ms = round((time.time() - call_started) * 1000)
            calls_succeeded += 1
            output_text = extract_output_text(raw_response)
            output_payload = parse_model_json(output_text)
            report_obj = validate_contract(input_payload, output_payload, registry_payload)
            report = report_obj.as_dict()
            all_passed = all_passed and report["passed"]
            usage = extract_usage(raw_response)
            cost = estimate_cost(usage, pricing)
            model_log = {
                "mission_id": mission_id,
                "mode": "live_openai",
                "model": model,
                "attempts": attempts,
                "latency_ms": latency_ms,
                "usage": usage,
                "estimated_cost_usd": cost,
            }

            write_json(mission_dir / "raw_api_response.json", raw_response)
            write_text(mission_dir / "raw_model_output.txt", output_text)
            write_json(mission_dir / "raw_model_output.json", output_payload)
            write_json(mission_dir / "validated_output.json", output_payload)
            write_json(mission_dir / "validation_report.json", report)
            write_markdown_report(report_obj, mission_dir / "validation_report.md")
            write_json(mission_dir / "cost_latency_model_log.json", model_log)
            model_logs.append(model_log)
            mission_summaries.append(mission_summary(output_payload, input_payload, report))
        except Exception as error:
            all_passed = False
            error_payload = {
                "mission_id": mission_id,
                "mode": "live_openai",
                "model": model,
                "error": str(error),
            }
            write_json(mission_dir / "api_error.json", error_payload)
            write_json(mission_dir / "cost_latency_model_log.json", error_payload)
            model_logs.append(error_payload)
            mission_summaries.append(
                {
                    "mission_id": mission_id,
                    "generated_title": None,
                    "generated_subtitle": None,
                    "why_now": None,
                    "listen_for": [],
                    "validation_passed": False,
                    "route_item_count": len(input_payload.get("route_items", [])),
                    "missing_affinity_items": [
                        item["item_id"] for item in input_payload.get("route_items", []) if not item.get("song_affinity_tags")
                    ],
                    "tag_ids_by_item": {},
                    "error": str(error),
                }
            )
            if not args.continue_on_error:
                break

    completed_at = datetime.now(timezone.utc).isoformat()
    totals = {
        "input_tokens": sum(log.get("usage", {}).get("input_tokens") or 0 for log in model_logs),
        "cached_input_tokens": sum(log.get("usage", {}).get("cached_input_tokens") or 0 for log in model_logs),
        "output_tokens": sum(log.get("usage", {}).get("output_tokens") or 0 for log in model_logs),
        "reasoning_output_tokens": sum(log.get("usage", {}).get("reasoning_output_tokens") or 0 for log in model_logs),
        "total_tokens": sum(log.get("usage", {}).get("total_tokens") or 0 for log in model_logs),
        "estimated_total_usd": round(
            sum(log.get("estimated_cost_usd", {}).get("total_usd") or 0 for log in model_logs),
            8,
        ),
    }
    summary = {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "mode": "dry_run" if args.dry_run else "live_openai",
        "model": model,
        "started_at": started_at,
        "completed_at": completed_at,
        "all_validation_passed": all_passed,
        "openai_calls_attempted": calls_attempted,
        "openai_calls_succeeded": calls_succeeded,
        "usage_totals": totals,
        "data_findings": [
            "The Supabase diagnostic packet captured mission IDs but not route bodies.",
            "The local Build 45 share packet v2 supplied six mission bodies and 36 route items.",
            "The affinity join supplied song-level tags for 33 of 36 route items.",
            "The missing affinity rows were left empty rather than inferred.",
        ],
        "missions": mission_summaries,
        "model_logs": model_logs,
    }
    write_run_summary(run_dir, summary)

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
