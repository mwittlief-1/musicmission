from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class BuiltPrompt:
    system_prompt: str
    user_prompt: str
    context_packet: Dict[str, Any]
    output_schema: Dict[str, Any]
    request_fixture: Dict[str, Any]
    candidate_pool: Optional[Dict[str, Any]]


CONTEXT_MODES = {
    "thin",
    "atlas_digest",
    "atlas_plus_features",
    "atlas_plus_features_plus_candidates",
    "generated_atlas_digest_view",
    "generated_atlas_digest_view_plus_features",
    "generated_atlas_digest_view_plus_features_plus_candidates",
    "mission_generation_digest_view",
    "mission_generation_digest_view_plus_features",
    "mission_generation_digest_view_plus_features_plus_candidates",
}
CONTEXT_MODE_ALIASES = {
    "thin_context": "thin",
    "atlas_digest_only": "atlas_digest",
}


def normalize_context_mode(context_mode: str) -> str:
    return CONTEXT_MODE_ALIASES.get(context_mode, context_mode)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_text(path: Path) -> str:
    with path.open("r", encoding="utf-8") as handle:
        return handle.read()


def find_request(fixtures_root: Path, request_id: str) -> Dict[str, Any]:
    requests_doc = load_json(fixtures_root / "mission_requests" / "requests_v0_1.json")
    for request in requests_doc["requests"]:
        if request["request_id"] == request_id:
            return request
    raise KeyError(f"Unknown request_id: {request_id}")


def load_requests_doc(fixtures_root: Path) -> Dict[str, Any]:
    return load_json(fixtures_root / "mission_requests" / "requests_v0_1.json")


def load_prompt_template(fixtures_root: Path, template_name: str) -> str:
    normalized = template_name if template_name.endswith(".md") else f"{template_name}.md"
    return load_text(fixtures_root / "prompt_templates" / normalized)


def load_output_schema(fixtures_root: Path) -> Dict[str, Any]:
    return load_json(fixtures_root / "schemas" / "mission_output_schema_v0_1.json")


def load_candidate_pool(fixtures_root: Path, request_fixture: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    file_name = request_fixture.get("candidate_pool_file")
    if not file_name:
        return None
    return load_json(fixtures_root / "candidate_pools" / file_name)


def build_context_packet(
    fixtures_root: Path,
    request_id: str,
    context_mode: str,
) -> Dict[str, Any]:
    context_mode = normalize_context_mode(context_mode)
    if context_mode not in CONTEXT_MODES:
        raise ValueError(f"Unknown context mode {context_mode}. Expected one of {sorted(CONTEXT_MODES)}")

    request_fixture = find_request(fixtures_root, request_id)
    thin_atlas = load_json(fixtures_root / "atlas_digests" / "matt_atlas_digest_thin.json")
    full_atlas = load_json(fixtures_root / "atlas_digests" / "matt_atlas_digest_v0_1.json")
    generated_atlas_path = fixtures_root / "atlas_digests" / "generated_atlas_digest_view_v0_1.json"
    generated_atlas = load_json(generated_atlas_path) if generated_atlas_path.exists() else None
    mission_generation_digest_path = fixtures_root / "atlas_digests" / "mission_generation_digest_view_v0_1.json"
    mission_generation_digest = load_json(mission_generation_digest_path) if mission_generation_digest_path.exists() else None

    packet: Dict[str, Any] = {
        "harness_version": "0.1",
        "product_frame": {
            "product_name": "Waymark",
            "mission_is_not_playlist": True,
            "mission_definition": (
                "A mission is a structured listening route designed to test a taste hypothesis, "
                "collect evidence, preserve uncertainty, and produce conditional possible Atlas update candidates."
            ),
            "primary_reaction_operations": ["love", "like", "keep", "not_for_me"],
            "generation_contract": [
                "Use bounded context only.",
                "Do not promote Waypoints into Landmarks.",
                "Do not convert one-object exceptions into broad genre appetite.",
                "Use Dead Ends as learning instruments, not as punishment.",
                "Prefer route logic and expected evidence over recommendation prose.",
                "Preserve uncertainty explicitly.",
            ],
        },
        "mission_request": request_fixture,
        "context_mode": context_mode,
        "atlas_digest": _select_atlas_digest(context_mode, thin_atlas, full_atlas, generated_atlas, mission_generation_digest),
    }

    if context_mode in {
        "atlas_plus_features",
        "atlas_plus_features_plus_candidates",
        "generated_atlas_digest_view_plus_features",
        "generated_atlas_digest_view_plus_features_plus_candidates",
        "mission_generation_digest_view_plus_features",
        "mission_generation_digest_view_plus_features_plus_candidates",
    }:
        packet["taste_feature_registry"] = load_json(
            fixtures_root / "feature_registry" / "taste_feature_registry_seed_v0_1.json"
        )

    if context_mode in {
        "atlas_plus_features_plus_candidates",
        "generated_atlas_digest_view_plus_features_plus_candidates",
        "mission_generation_digest_view_plus_features_plus_candidates",
    }:
        candidate_pool = load_candidate_pool(fixtures_root, request_fixture)
        if candidate_pool is not None:
            packet["candidate_pool"] = candidate_pool
        else:
            packet["candidate_pool"] = {
                "pool_id": "none",
                "candidates": [],
                "notes": "No candidate pool fixture was supplied for this request.",
            }

    return packet


def _select_atlas_digest(
    context_mode: str,
    thin_atlas: Dict[str, Any],
    full_atlas: Dict[str, Any],
    generated_atlas: Optional[Dict[str, Any]],
    mission_generation_digest: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    if context_mode == "thin":
        return thin_atlas
    if context_mode.startswith("mission_generation_digest_view"):
        if mission_generation_digest is None:
            raise FileNotFoundError(
                "mission_generation_digest_view context requires "
                "fixtures/atlas_digests/mission_generation_digest_view_v0_1.json. "
                "Run waymark-atlas-tests/src/run_atlas_ingestion_tests.py first."
            )
        return mission_generation_digest
    if context_mode.startswith("generated_atlas_digest_view"):
        if generated_atlas is None:
            raise FileNotFoundError(
                "generated_atlas_digest_view context requires "
                "fixtures/atlas_digests/generated_atlas_digest_view_v0_1.json. "
                "Run waymark-atlas-tests/src/run_atlas_ingestion_tests.py first."
            )
        return generated_atlas
    return full_atlas


def build_prompt(
    fixtures_root: Path,
    request_id: str,
    template_name: str,
    context_mode: str,
) -> BuiltPrompt:
    context_mode = normalize_context_mode(context_mode)
    context_packet = build_context_packet(fixtures_root, request_id, context_mode)
    output_schema = load_output_schema(fixtures_root)
    request_fixture = context_packet["mission_request"]
    candidate_pool = context_packet.get("candidate_pool")

    template = load_prompt_template(fixtures_root, template_name)
    rendered = template
    replacements = {
        "{{SOURCE_PROMPT}}": request_fixture["prompt"],
        "{{REQUEST_ID}}": request_fixture["request_id"],
        "{{CONTEXT_MODE}}": context_mode,
        "{{CONTEXT_PACKET_JSON}}": json.dumps(context_packet, indent=2, sort_keys=True),
        "{{MISSION_OUTPUT_SCHEMA_JSON}}": json.dumps(output_schema, indent=2, sort_keys=True),
    }
    for placeholder, value in replacements.items():
        rendered = rendered.replace(placeholder, value)

    system_prompt = (
        "You generate Waymark mission objects for a bounded API test harness. "
        "Return only JSON that conforms to the provided schema. "
        "A mission is not a playlist: every item must have a route function, expected signal, "
        "and reaction-specific feedback chips for love, like, keep, and not_for_me."
    )
    return BuiltPrompt(
        system_prompt=system_prompt,
        user_prompt=rendered,
        context_packet=context_packet,
        output_schema=output_schema,
        request_fixture=request_fixture,
        candidate_pool=candidate_pool if isinstance(candidate_pool, dict) else None,
    )


def candidate_ids(candidate_pool: Optional[Dict[str, Any]]) -> List[str]:
    if not candidate_pool:
        return []
    return [candidate["candidate_id"] for candidate in candidate_pool.get("candidates", [])]
