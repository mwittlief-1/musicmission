#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import shlex
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
INGESTION_DIR = REPO_ROOT / "data/atlas_schema/ingestion_proof/a3_gpt_5_5_3x3"
OUT_DIR = REPO_ROOT / "data/atlas_schema/node_interpretation_smoke/a3_v0_1_1"

MODEL_ID = os.environ.get("WAYMARK_LLM_MODEL", "gpt-5.5")
OPENAI_RESPONSES_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com").rstrip("/") + "/v1/responses"
GENERATED_AT = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

SLIM_PACKET_PATHS = [
    INGESTION_DIR / "slim_node_interpretation_input_profile_01_A3.json",
    INGESTION_DIR / "slim_node_interpretation_input_profile_05_A3.json",
    INGESTION_DIR / "slim_node_interpretation_input_profile_06_A3.json",
]

REQUEST_PATH = OUT_DIR / "a3_node_interpretation_smoke_request_v0_1_1.json"
OUTPUT_SCHEMA_PATH = OUT_DIR / "a3_node_interpretation_smoke_output_schema_v0_1_1.json"
RAW_RESPONSE_PATH = OUT_DIR / "a3_node_interpretation_smoke_raw_response_v0_1_1.json"
OUTPUT_PATH = OUT_DIR / "a3_node_interpretation_smoke_output_v0_1_1.json"
MANIFEST_PATH = OUT_DIR / "a3_node_interpretation_smoke_manifest_v0_1_1.json"
REPORT_PATH = OUT_DIR / "a3_node_interpretation_smoke_report_v0_1_1.md"

FORBIDDEN_INPUT_KEYS = {
    "pages",
    "scores",
    "raw_ranking_scores",
    "generator_visible_inputs",
    "adaptive_context",
    "page_generation_prompt_text",
    "deterministic_visible_evidence_summary",
    "debug_provenance",
    "possible_atlas_update_candidates",
    "full_raw_survey_payload",
    "hidden_profile_truth",
    "hidden_archetype_tiers",
    "hidden_corpus_reactions",
    "simulator_private_lookup_status",
    "profile_writer_output",
}


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
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            value = shlex.split(value)[0]
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


def stable_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def json_hash(payload: Any) -> str:
    return sha256_text(stable_json(payload))


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def schema_string_enum(values: list[str]) -> dict[str, Any]:
    return {"type": "string", "enum": values}


def string_array() -> dict[str, Any]:
    return {"type": "array", "items": {"type": "string"}}


def confidence_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["confidence_score", "confidence_band", "confidence_basis", "confidence_summary"],
        "properties": {
            "confidence_score": {"type": "number", "minimum": 0, "maximum": 1},
            "confidence_band": schema_string_enum(["low", "medium", "high"]),
            "confidence_basis": schema_string_enum(
                [
                    "survey_pattern",
                    "density_pattern",
                    "contradiction_pattern",
                    "object_scope",
                    "thin_evidence",
                    "mixed_evidence",
                ]
            ),
            "confidence_summary": {"type": "string"},
        },
    }


def review_requirement_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["required", "reason"],
        "properties": {
            "required": {"type": "boolean"},
            "reason": {"type": "string"},
        },
    }


def mission_hint_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["type", "risk_level", "objective", "suggested_probe_shape"],
        "properties": {
            "type": schema_string_enum(
                [
                    "artist_calibration",
                    "album_calibration",
                    "song_recording_calibration",
                    "frontier_probe",
                    "dead_end_check",
                    "contradiction_test",
                    "waypoint_bridge_test",
                    "region_density_test",
                ]
            ),
            "risk_level": schema_string_enum(["low", "medium", "high"]),
            "objective": {"type": "string"},
            "suggested_probe_shape": {"type": "string"},
        },
    }


def evidence_ref_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["signal_id", "reason"],
        "properties": {
            "signal_id": {"type": "string"},
            "reason": {"type": "string"},
        },
    }


def target_ref_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "source_digest_id",
            "target_node_ref",
            "target_role_assignment_id",
            "display_name",
            "object_type",
        ],
        "properties": {
            "source_digest_id": {"type": "string"},
            "target_node_ref": {"type": "string"},
            "target_role_assignment_id": {"type": "string"},
            "display_name": {"type": "string"},
            "object_type": schema_string_enum(
                [
                    "artist",
                    "album",
                    "song_recording",
                    "composition_placeholder",
                    "scene",
                    "era",
                    "genre_lane",
                    "taste_feature",
                    "user_defined_concept",
                    "mission_derived_concept",
                    "cluster",
                    "unknown",
                ]
            ),
        },
    }


def output_schema() -> dict[str, Any]:
    possible_candidate = {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "candidate_id",
            "profile_public_id",
            "target_ref",
            "candidate_type",
            "recommended_role",
            "recommended_action",
            "promotion_state",
            "confidence",
            "scope_limit",
            "reasoning_summary",
            "evidence_refs",
            "risks",
            "review_requirement",
            "mission_hint",
            "canonical_graph_mutation_allowed",
            "generated_hypothesis_only",
        ],
        "properties": {
            "candidate_id": {"type": "string"},
            "profile_public_id": {"type": "string"},
            "target_ref": target_ref_schema(),
            "candidate_type": schema_string_enum(
                [
                    "role_refinement",
                    "contradiction_cluster",
                    "frontier_hypothesis",
                    "dead_end_hypothesis",
                    "waypoint_hypothesis",
                    "region_hypothesis",
                    "landmark_reinforcement",
                    "scope_warning",
                    "review_requirement",
                ]
            ),
            "recommended_role": schema_string_enum(
                ["landmark", "region", "frontier", "dead_end", "waypoint", "unknown", "signal_only"]
            ),
            "recommended_action": schema_string_enum(
                [
                    "keep_existing_provisional_role",
                    "revise_to_frontier",
                    "revise_to_waypoint",
                    "revise_to_dead_end_hypothesis",
                    "revise_to_unknown",
                    "add_scope_warning",
                    "require_mission_test",
                    "merge_into_contradiction_cluster",
                    "block_promotion",
                ]
            ),
            "promotion_state": schema_string_enum(["proposed", "candidate", "blocked"]),
            "confidence": confidence_schema(),
            "scope_limit": {"type": "string"},
            "reasoning_summary": {"type": "string"},
            "evidence_refs": {"type": "array", "items": evidence_ref_schema()},
            "risks": string_array(),
            "review_requirement": review_requirement_schema(),
            "mission_hint": mission_hint_schema(),
            "canonical_graph_mutation_allowed": {"type": "boolean", "const": False},
            "generated_hypothesis_only": {"type": "boolean", "const": True},
        },
    }

    role_refinement = {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "target_role_assignment_id",
            "current_provisional_role",
            "recommended_role",
            "recommendation",
            "reason",
            "evidence_refs",
            "promotion_state",
        ],
        "properties": {
            "target_role_assignment_id": {"type": "string"},
            "current_provisional_role": schema_string_enum(
                ["landmark", "region", "frontier", "dead_end", "waypoint", "unknown", "signal_only"]
            ),
            "recommended_role": schema_string_enum(
                ["landmark", "region", "frontier", "dead_end", "waypoint", "unknown", "signal_only"]
            ),
            "recommendation": schema_string_enum(
                [
                    "keep",
                    "soften",
                    "escalate_review",
                    "downgrade_to_unknown",
                    "split_scope",
                    "mission_test_before_promotion",
                ]
            ),
            "reason": {"type": "string"},
            "evidence_refs": {"type": "array", "items": evidence_ref_schema()},
            "promotion_state": schema_string_enum(["proposed", "candidate", "blocked"]),
        },
    }

    contradiction = {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "cluster_id",
            "label",
            "explanation",
            "scope_limit",
            "evidence_refs",
            "review_requirement",
            "mission_hint",
        ],
        "properties": {
            "cluster_id": {"type": "string"},
            "label": {"type": "string"},
            "explanation": {"type": "string"},
            "scope_limit": {"type": "string"},
            "evidence_refs": {"type": "array", "items": evidence_ref_schema()},
            "review_requirement": review_requirement_schema(),
            "mission_hint": mission_hint_schema(),
        },
    }

    first_mission_hint = {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "hint_id",
            "type",
            "target_summary",
            "risk_level",
            "hypothesis",
            "success_signal",
            "failure_signal",
            "evidence_refs",
            "creates_mission_object",
        ],
        "properties": {
            "hint_id": {"type": "string"},
            "type": schema_string_enum(
                [
                    "artist_calibration",
                    "album_calibration",
                    "song_recording_calibration",
                    "frontier_probe",
                    "dead_end_check",
                    "contradiction_test",
                    "waypoint_bridge_test",
                    "region_density_test",
                ]
            ),
            "target_summary": {"type": "string"},
            "risk_level": schema_string_enum(["low", "medium", "high"]),
            "hypothesis": {"type": "string"},
            "success_signal": {"type": "string"},
            "failure_signal": {"type": "string"},
            "evidence_refs": {"type": "array", "items": evidence_ref_schema()},
            "creates_mission_object": {"type": "boolean", "const": False},
        },
    }

    profile = {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "profile_public_id",
            "source_digest_id",
            "interpretation_status",
            "packet_sufficiency",
            "possible_update_candidates",
            "role_refinement_recommendations",
            "contradiction_explanations",
            "wwtsf_ready_bullets",
            "first_mission_hint_candidates",
            "safety_checks",
        ],
        "properties": {
            "profile_public_id": {"type": "string"},
            "source_digest_id": {"type": "string"},
            "interpretation_status": schema_string_enum(["interpreted", "needs_more_evidence", "blocked"]),
            "packet_sufficiency": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "sufficient_for_structured_interpretation",
                    "raw_payload_needed",
                    "missing_context",
                    "summary",
                ],
                "properties": {
                    "sufficient_for_structured_interpretation": {"type": "boolean"},
                    "raw_payload_needed": {"type": "boolean", "const": False},
                    "missing_context": string_array(),
                    "summary": {"type": "string"},
                },
            },
            "possible_update_candidates": {"type": "array", "items": possible_candidate, "minItems": 2},
            "role_refinement_recommendations": {"type": "array", "items": role_refinement},
            "contradiction_explanations": {"type": "array", "items": contradiction},
            "wwtsf_ready_bullets": string_array(),
            "first_mission_hint_candidates": {"type": "array", "items": first_mission_hint},
            "safety_checks": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "no_promoted_truth",
                    "canonical_graph_mutation_allowed",
                    "used_only_slim_packet",
                    "final_wwtsf_copy_generated",
                    "final_missions_generated",
                    "family_archetype_labels_invented",
                    "apple_exposure_used_as_taste_truth",
                ],
                "properties": {
                    "no_promoted_truth": {"type": "boolean", "const": True},
                    "canonical_graph_mutation_allowed": {"type": "boolean", "const": False},
                    "used_only_slim_packet": {"type": "boolean", "const": True},
                    "final_wwtsf_copy_generated": {"type": "boolean", "const": False},
                    "final_missions_generated": {"type": "boolean", "const": False},
                    "family_archetype_labels_invented": {"type": "boolean", "const": False},
                    "apple_exposure_used_as_taste_truth": {"type": "boolean", "const": False},
                },
            },
        },
    }

    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema_version",
            "model_id",
            "generated_at",
            "source_packet_ids",
            "execution_policy",
            "profile_interpretations",
            "aggregate_review",
        ],
        "properties": {
            "schema_version": {"type": "string", "const": "waymark.a3_node_interpretation_smoke_output.v0.1.1"},
            "model_id": {"type": "string", "const": MODEL_ID},
            "generated_at": {"type": "string"},
            "source_packet_ids": string_array(),
            "execution_policy": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "input_scope",
                    "raw_survey_payload_allowed",
                    "profile_writer_output_allowed",
                    "canonical_graph_mutation_allowed",
                    "promoted_atlas_truth_allowed",
                    "final_wwtsf_copy_allowed",
                    "final_mission_generation_allowed",
                ],
                "properties": {
                    "input_scope": {"type": "string"},
                    "raw_survey_payload_allowed": {"type": "boolean", "const": False},
                    "profile_writer_output_allowed": {"type": "boolean", "const": False},
                    "canonical_graph_mutation_allowed": {"type": "boolean", "const": False},
                    "promoted_atlas_truth_allowed": {"type": "boolean", "const": False},
                    "final_wwtsf_copy_allowed": {"type": "boolean", "const": False},
                    "final_mission_generation_allowed": {"type": "boolean", "const": False},
                },
            },
            "profile_interpretations": {"type": "array", "items": profile, "minItems": 3, "maxItems": 3},
            "aggregate_review": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "all_profiles_interpreted_without_raw_payload",
                    "schema_compatible",
                    "uncertainty_preserved",
                    "dense_love_vs_isolated_love_handled",
                    "contradictions_create_review_recommendations",
                    "mission_hints_are_not_missions",
                    "wwtsf_bullets_are_not_final_copy",
                    "summary",
                ],
                "properties": {
                    "all_profiles_interpreted_without_raw_payload": {"type": "boolean"},
                    "schema_compatible": {"type": "boolean"},
                    "uncertainty_preserved": {"type": "boolean"},
                    "dense_love_vs_isolated_love_handled": {"type": "boolean"},
                    "contradictions_create_review_recommendations": {"type": "boolean"},
                    "mission_hints_are_not_missions": {"type": "boolean"},
                    "wwtsf_bullets_are_not_final_copy": {"type": "boolean"},
                    "summary": {"type": "string"},
                },
            },
        },
    }


def system_prompt() -> str:
    return (
        "You are Waymark's Atlas node interpretation smoke-test model. "
        "Return only strict JSON matching the supplied schema. Interpret Atlas substrate; do not write a prose taste profile."
    )


def developer_prompt() -> str:
    return "\n".join(
        [
            "Run A3_NODE_INTERPRETATION_SMOKE_V0_1_1.",
            "Use only the provided slim node-interpretation packets.",
            "Do not use raw A3 payloads, Profile Writer outputs, hidden fake-profile truth, hidden corpus reactions, or simulator-private lookup status.",
            "Treat AtlasNode as the thing only; role truth lives in AtlasRoleAssignment and possible update candidates.",
            "Return structured PossibleAtlasUpdateCandidate-style recommendations, role refinements, contradiction explanations, WWTSF-ready bullets, and first-mission hint candidates.",
            "Do not promote Atlas truth. Do not mutate canonical graph. Do not generate final WWTSF copy. Do not generate mission objects.",
            "Do not invent family or archetype labels when dictionary labels are unavailable; IDs may remain IDs.",
            "Apple evidence is exposure/import/familiarity context only, not taste truth.",
            "Dense-positive Loves, isolated Loves, and mixed-neighborhood Loves must be interpreted differently.",
            "Contradictions should create scope limits, review requirements, or mission-test hints, not overconfident claims.",
            "Keep outputs concise: 2-5 possible update candidates per profile, 2-5 role refinements, 0-4 contradiction explanations, 3-6 WWTSF-ready bullets, and 2-4 mission hints.",
            f"Set the top-level model_id field exactly to `{MODEL_ID}`.",
        ]
    )


def smoke_user_payload(packets: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "waymark.a3_node_interpretation_smoke_input.v0.1.1",
        "generated_at": GENERATED_AT,
        "expected_output_metadata": {
            "schema_version": "waymark.a3_node_interpretation_smoke_output.v0.1.1",
            "model_id": MODEL_ID,
        },
        "input_scope": "one_pass_across_three_slim_packets_only",
        "source_packet_ids": [packet["profile_public_id"] for packet in packets],
        "acceptance_criteria": [
            "Interpret all three slim packets without raw payload.",
            "Return records schema-compatible or trivially mappable to PossibleAtlasUpdateCandidate / AtlasDigestView extensions.",
            "Preserve uncertainty and scope limits.",
            "Treat dense-positive Loves differently from isolated or mixed-neighborhood Loves.",
            "Turn contradictions into review/test recommendations.",
            "Keep mission hints as hypotheses, not mission objects.",
            "Keep WWTSF bullets as source material, not final user-facing copy.",
        ],
        "slim_node_interpretation_packets": packets,
    }


def response_request(packets: list[dict[str, Any]], schema: dict[str, Any]) -> dict[str, Any]:
    return {
        "model": MODEL_ID,
        "input": [
            {"role": "system", "content": [{"type": "input_text", "text": system_prompt()}]},
            {"role": "developer", "content": [{"type": "input_text", "text": developer_prompt()}]},
            {"role": "user", "content": [{"type": "input_text", "text": json.dumps(smoke_user_payload(packets), indent=2)}]},
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "a3_node_interpretation_smoke_output_v0_1_1",
                "strict": True,
                "schema": schema,
            }
        },
    }


def forbidden_key_paths(payload: Any, path: tuple[str, ...] = ()) -> list[str]:
    paths: list[str] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            key_text = str(key)
            if key_text in FORBIDDEN_INPUT_KEYS:
                paths.append(".".join((*path, key_text)))
            paths.extend(forbidden_key_paths(value, (*path, key_text)))
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            paths.extend(forbidden_key_paths(value, (*path, str(index))))
    return paths


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
    return json.loads(extract_output_text(response))


def validate_output(output: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if output.get("schema_version") != "waymark.a3_node_interpretation_smoke_output.v0.1.1":
        errors.append("Unexpected schema_version.")
    profiles = output.get("profile_interpretations")
    if not isinstance(profiles, list) or len(profiles) != 3:
        errors.append("Expected exactly three profile_interpretations.")
        return errors

    for profile in profiles:
        profile_id = profile.get("profile_public_id", "<unknown>")
        safety = profile.get("safety_checks") or {}
        if safety.get("no_promoted_truth") is not True:
            errors.append(f"{profile_id}: no_promoted_truth is not true.")
        if safety.get("canonical_graph_mutation_allowed") is not False:
            errors.append(f"{profile_id}: canonical_graph_mutation_allowed is not false.")
        if safety.get("used_only_slim_packet") is not True:
            errors.append(f"{profile_id}: used_only_slim_packet is not true.")
        if safety.get("final_wwtsf_copy_generated") is not False:
            errors.append(f"{profile_id}: final_wwtsf_copy_generated is not false.")
        if safety.get("final_missions_generated") is not False:
            errors.append(f"{profile_id}: final_missions_generated is not false.")
        if (profile.get("packet_sufficiency") or {}).get("raw_payload_needed") is not False:
            errors.append(f"{profile_id}: raw_payload_needed is not false.")
        for candidate in profile.get("possible_update_candidates", []):
            if candidate.get("promotion_state") not in {"proposed", "candidate", "blocked"}:
                errors.append(f"{profile_id}: invalid candidate promotion_state.")
            if candidate.get("canonical_graph_mutation_allowed") is not False:
                errors.append(f"{profile_id}: candidate allows canonical graph mutation.")
            if candidate.get("generated_hypothesis_only") is not True:
                errors.append(f"{profile_id}: candidate is not marked generated_hypothesis_only.")
        for hint in profile.get("first_mission_hint_candidates", []):
            if hint.get("creates_mission_object") is not False:
                errors.append(f"{profile_id}: mission hint creates a mission object.")
    return errors


def write_profile_splits(output: dict[str, Any]) -> list[str]:
    paths = []
    for profile in output.get("profile_interpretations", []):
        profile_id = profile["profile_public_id"]
        profile_num = profile_id.rsplit("_", 1)[-1]
        path = OUT_DIR / f"node_interpretation_smoke_profile_{profile_num}_A3.json"
        write_json(path, profile)
        paths.append(rel(path))
    return paths


def render_report(metadata: dict[str, Any]) -> str:
    lines = [
        "# A3 Node Interpretation Smoke v0.1.1",
        "",
        f"- Status: `{metadata['status']}`",
        f"- Model: `{metadata['model_id']}`",
        f"- Generated at: `{metadata['generated_at']}`",
        f"- Input scope: `{metadata['input_scope']}`",
        f"- Raw payload used: `{metadata['raw_payload_used']}`",
        f"- Profile Writer output used: `{metadata['profile_writer_output_used']}`",
        f"- Request: `{metadata['artifacts']['request']}`",
        f"- Output schema: `{metadata['artifacts']['output_schema']}`",
    ]
    if metadata.get("artifacts", {}).get("output"):
        lines.append(f"- Structured output: `{metadata['artifacts']['output']}`")
    if metadata.get("validation_errors"):
        lines.extend(["", "## Validation Errors", ""])
        lines.extend(f"- {error}" for error in metadata["validation_errors"])
    if metadata.get("error"):
        lines.extend(["", "## Error", "", f"```text\n{metadata['error']}\n```"])
    if metadata.get("summary"):
        lines.extend(["", "## Summary", "", metadata["summary"]])
    profile_outputs = metadata.get("artifacts", {}).get("profile_outputs") or []
    if profile_outputs:
        lines.extend(["", "## Profile Outputs", ""])
        lines.extend(f"- `{path}`" for path in profile_outputs)
    lines.append("")
    return "\n".join(lines)


def run() -> int:
    load_env_file(REPO_ROOT / "waymark-ai-tests" / ".env")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    packets = [load_json(path) for path in SLIM_PACKET_PATHS]
    schema = output_schema()
    request = response_request(packets, schema)
    request_key_violations = forbidden_key_paths(smoke_user_payload(packets))

    write_json(OUTPUT_SCHEMA_PATH, schema)
    write_json(REQUEST_PATH, request)

    metadata: dict[str, Any] = {
        "schema_version": "waymark.a3_node_interpretation_smoke_manifest.v0.1.1",
        "generated_at": GENERATED_AT,
        "status": "running",
        "model_id": MODEL_ID,
        "openai_responses_url": OPENAI_RESPONSES_URL,
        "input_scope": "slim_node_interpretation_packets_only",
        "source_slim_packets": [rel(path) for path in SLIM_PACKET_PATHS],
        "source_packet_ids": [packet["profile_public_id"] for packet in packets],
        "request_sha256": json_hash(request),
        "output_schema_sha256": json_hash(schema),
        "raw_payload_used": False,
        "profile_writer_output_used": False,
        "forbidden_input_key_violations": request_key_violations,
        "validation_errors": [],
        "artifacts": {
            "request": rel(REQUEST_PATH),
            "output_schema": rel(OUTPUT_SCHEMA_PATH),
            "raw_response": rel(RAW_RESPONSE_PATH),
            "output": rel(OUTPUT_PATH),
            "profile_outputs": [],
        },
        "error": None,
        "summary": None,
    }

    if request_key_violations:
        metadata["status"] = "blocked"
        metadata["error"] = "Slim smoke input contains forbidden raw/debug/construction keys."
        write_json(MANIFEST_PATH, metadata)
        write_text(REPORT_PATH, render_report(metadata))
        print("BLOCKED: forbidden input keys found", file=sys.stderr)
        return 2

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        metadata["status"] = "blocked"
        metadata["error"] = "OPENAI_API_KEY is not set; no API calls were made."
        write_json(MANIFEST_PATH, metadata)
        write_text(REPORT_PATH, render_report(metadata))
        print("BLOCKED: OPENAI_API_KEY is not set", file=sys.stderr)
        return 2

    try:
        raw_response = api_post(request, api_key)
        write_json(RAW_RESPONSE_PATH, raw_response)
        output = parse_structured_output(raw_response)
        write_json(OUTPUT_PATH, output)
        profile_outputs = write_profile_splits(output)
        validation_errors = validate_output(output)
        metadata["validation_errors"] = validation_errors
        metadata["artifacts"]["profile_outputs"] = profile_outputs
        metadata["output_sha256"] = json_hash(output)
        metadata["status"] = "completed" if not validation_errors else "completed_with_validation_errors"
        aggregate = output.get("aggregate_review") or {}
        metadata["summary"] = aggregate.get("summary")
        write_json(MANIFEST_PATH, metadata)
        write_text(REPORT_PATH, render_report(metadata))
        print(f"Completed A3 node interpretation smoke at {rel(OUT_DIR)}")
        return 0 if not validation_errors else 1
    except Exception as error:
        metadata["status"] = "failed"
        metadata["error"] = str(error)
        write_json(MANIFEST_PATH, metadata)
        write_text(REPORT_PATH, render_report(metadata))
        print(f"FAILED: {error}", file=sys.stderr)
        time.sleep(0.1)
        return 1


if __name__ == "__main__":
    raise SystemExit(run())
