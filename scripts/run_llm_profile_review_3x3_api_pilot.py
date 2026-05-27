#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shlex
import sys
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = REPO_ROOT / "data/survey_simulation"
BACKTEST_DIR = SIM_DIR / "page_count_backtest"
REVIEW_DIR = SIM_DIR / "llm_profile_review"
MODEL_ID = os.environ.get("CARTENZA_LLM_MODEL") or os.environ.get("WAYMARK_LLM_MODEL", "gpt-5.5")
MODEL_SLUG = MODEL_ID.replace(".", "_").replace("-", "_")
OUT_DIR = REVIEW_DIR / ("api_pilot_3x3" if MODEL_ID == "gpt-5.5" else f"api_pilot_3x3_{MODEL_SLUG}")
PUBLIC_PACKET_DIR = OUT_DIR / "public_packets"
HIDDEN_TRUTH_DIR = OUT_DIR / "simulator_private" / "hidden_truth_packets"
REQUEST_DIR = OUT_DIR / "executed_requests"
RAW_DIR = OUT_DIR / "raw_api_responses"
PROFILE_DIR = OUT_DIR / "generated_taste_profiles"
EVALUATOR_DIR = OUT_DIR / "evaluator_scores"
REPORT_PATH = REVIEW_DIR / "reports" / (
    "api_pilot_3x3_execution_report.md"
    if MODEL_ID == "gpt-5.5"
    else f"api_pilot_3x3_{MODEL_SLUG}_execution_report.md"
)
METADATA_PATH = OUT_DIR / (
    "api_pilot_3x3_execution_metadata.json"
    if MODEL_ID == "gpt-5.5"
    else f"api_pilot_3x3_{MODEL_SLUG}_execution_metadata.json"
)
GENERATED_AT = "2026-05-20T12:00:00Z"
OPENAI_RESPONSES_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com").rstrip("/") + "/v1/responses"

PROFILES = [
    {
        "index": 1,
        "public_profile_id": "public_profile_01",
        "selection_role": "coherent_center_profile",
    },
    {
        "index": 5,
        "public_profile_id": "public_profile_05",
        "selection_role": "mixed_multi_center_profile",
    },
    {
        "index": 6,
        "public_profile_id": "public_profile_06",
        "selection_role": "context_heavy_profile",
    },
]
CONFIGS = [
    {"config_id": "A2_Al1_S1", "artist_pages": 2, "album_pages": 1, "song_pages": 1},
    {"config_id": "A3_Al1_S2", "artist_pages": 3, "album_pages": 1, "song_pages": 2},
    {"config_id": "A4_Al2_S3", "artist_pages": 4, "album_pages": 2, "song_pages": 3},
]
REACTIONS = ["love", "like", "ok", "dont_like", "dont_know_enough"]
REACTION_SCORE = {"love": 4, "like": 3, "ok": 2, "dont_like": 1, "dont_know_enough": None}
STAGE_NORMALIZATION = {"artists": "artist", "albums": "album", "songs": "song"}
EMPTY_APPLE_EVIDENCE = {
    "exact_signal_weight": 0.0,
    "exposure_score": 0.0,
    "recency_score": 0.0,
    "repetition_score": 0.0,
    "library_commitment_score": 0.0,
    "favorite_or_rating_score": 0.0,
    "playlist_context_score": 0.0,
    "album_completion_hint": 0.0,
    "artist_depth_hint": 0.0,
    "probable_affinity_score": 0.0,
    "signal_ids": [],
}


def load_pilot_module() -> Any:
    path = REPO_ROOT / "scripts" / "build_llm_profile_review_pilot.py"
    spec = importlib.util.spec_from_file_location("llm_profile_review_pilot", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import pilot module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


pilot = load_pilot_module()


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


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def json_hash(payload: Any) -> str:
    return sha256_text(json.dumps(payload, sort_keys=True, separators=(",", ":")))


def stable_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def fingerprint(payload: Any) -> str:
    return sha256_text(stable_json(payload))


def canonical_ref_key(ref: dict[str, Any]) -> tuple[str, str]:
    object_type = ref["object_type"]
    if object_type == "artist":
        return object_type, ref["canonical_artist_id"]
    if object_type == "album":
        return object_type, ref["canonical_album_id"]
    if object_type == "song_recording":
        return object_type, ref["canonical_song_recording_id"]
    raise ValueError(f"Unsupported object_type: {object_type}")


def evidence_ref(stage: str, page: dict[str, Any], tile: dict[str, Any], response: dict[str, Any]) -> str:
    display = tile["music_object_ref"]["display_name"].replace(":", " -")
    return f"{page['page_id']}:{stage}:{tile['position']:02d}:{display}:{response['reaction']}"


def normalized_apple_evidence(tile: dict[str, Any]) -> dict[str, Any]:
    source = dict(EMPTY_APPLE_EVIDENCE)
    apple_evidence = tile.get("apple_evidence") or {}
    for key in source:
        if key in apple_evidence:
            source[key] = apple_evidence[key]
    return source


def tile_packet(stage: str, page: dict[str, Any], tile: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
    page_stage = STAGE_NORMALIZATION.get(page["stage"], stage)
    graph_context = tile.get("graph_context") or {
        "family_numbers": [],
        "archetype_ids": [],
        "roles": [],
        "best_recognition_tier": "unknown",
        "best_survey_tier": "unknown",
    }
    return {
        "evidence_ref": evidence_ref(page_stage, page, tile, response),
        "position": tile["position"],
        "tile_id": tile["tile_id"],
        "response_id": response["response_id"],
        "music_object_ref": tile["music_object_ref"],
        "reaction": response["reaction"],
        "atlas_signal_interpretation": response["atlas_signal_interpretation"],
        "app_ui_candidate": response["app_ui_candidate"],
        "page_intent": tile["page_intent"],
        "candidate_basis": tile.get("candidate_basis", []),
        "graph_context": graph_context,
        "apple_evidence_summary": normalized_apple_evidence(tile),
        "scores": tile.get("scores", {}),
        "response_evidence_refs": tile.get("response_evidence_refs", []),
        "shown_unselected_tags": response.get("shown_unselected_tags", []),
        "observed_selected_tags": response.get("observed_selected_tags", []),
        "suppression_warnings": tile.get("suppression_warnings", []),
    }


def selected_pages(path: dict[str, Any], config: dict[str, Any]) -> list[tuple[str, dict[str, Any], dict[str, Any]]]:
    selected: list[tuple[str, dict[str, Any], dict[str, Any]]] = []
    for stage, count in [
        ("artist", config["artist_pages"]),
        ("album", config["album_pages"]),
        ("song", config["song_pages"]),
    ]:
        pages = path["pages_by_stage"][stage][:count]
        recordings = path["recorded_responses_by_stage"][stage][:count]
        for page, recorded in zip(pages, recordings):
            selected.append((stage, page, recorded))
    return selected


def build_pages(path: dict[str, Any], config: dict[str, Any]) -> list[dict[str, Any]]:
    pages = []
    for stage, page, recorded in selected_pages(path, config):
        responses_by_tile = {item["tile_id"]: item for item in recorded["responses"]}
        tiles = [tile_packet(stage, page, tile, responses_by_tile[tile["tile_id"]]) for tile in page["tiles"]]
        pages.append(
            {
                "page_id": page["page_id"],
                "stage": STAGE_NORMALIZATION.get(page["stage"], stage),
                "page_number": page["page_number"],
                "page_mode": page["page_mode"],
                "tile_count": page["tile_count"],
                "generator_visible_inputs": page.get("generator_visible_inputs", {}),
                "adaptive_context": page.get("adaptive_context"),
                "tiles": tiles,
            }
        )
    return pages


def response_counts_by_stage(pages: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    counts = {stage: {reaction: 0 for reaction in REACTIONS} for stage in ["artist", "album", "song"]}
    for page in pages:
        stage_counts = counts[page["stage"]]
        for tile in page["tiles"]:
            stage_counts[tile["reaction"]] += 1
    return counts


def cluster_summary(pages: list[dict[str, Any]]) -> dict[str, Any]:
    buckets = {
        "positive_clusters": [],
        "negative_clusters": [],
        "ok_waypoint_clusters": [],
        "unknown_clusters": [],
    }
    grouped: dict[str, Counter[str]] = {key: Counter() for key in buckets}
    evidence_refs: dict[tuple[str, str], list[str]] = defaultdict(list)
    for page in pages:
        for tile in page["tiles"]:
            reaction = tile["reaction"]
            if reaction in {"love", "like"}:
                bucket = "positive_clusters"
            elif reaction == "dont_like":
                bucket = "negative_clusters"
            elif reaction == "ok":
                bucket = "ok_waypoint_clusters"
            else:
                bucket = "unknown_clusters"
            labels = [f"archetype:{item}" for item in tile["graph_context"]["archetype_ids"]]
            labels.extend(f"family:{item}" for item in tile["graph_context"]["family_numbers"])
            if not labels:
                labels = ["unclustered"]
            for label in labels:
                grouped[bucket][label] += 1
                evidence_refs[(bucket, label)].append(tile["evidence_ref"])
    for bucket, counter in grouped.items():
        for label, count in counter.most_common(10):
            buckets[bucket].append(
                {
                    "label": label,
                    "visible_response_count": count,
                    "evidence_refs": evidence_refs[(bucket, label)][:10],
                }
            )
    return buckets


def apple_payload_summary(apple_payload: dict[str, Any], pages: list[dict[str, Any]]) -> dict[str, Any]:
    payload_signature_refs = []
    for page in pages:
        for tile in page["tiles"]:
            if tile["page_intent"] == "payload_signature_artist":
                payload_signature_refs.append(
                    {
                        "display_name": tile["music_object_ref"]["display_name"],
                        "music_object_ref": tile["music_object_ref"],
                        "payload_overrepresentation_score": tile["scores"].get("payload_overrepresentation_score", 0.0),
                        "apple_evidence_strength": tile["scores"].get("apple_evidence_strength", 0.0),
                        "evidence_ref": tile["evidence_ref"],
                    }
                )
    top_signals = []
    for signal in apple_payload.get("signals", [])[:12]:
        top_signals.append(
            {
                "signal_id": signal["signal_id"],
                "signal_type": signal["signal_type"],
                "music_object_ref": signal["music_object_ref"],
                "normalized_weight": signal.get("normalized_weight", 0.0),
                "recency_days": signal.get("recency_days"),
                "play_count_90d": signal.get("play_count_90d"),
                "library_added_at": signal.get("library_added_at"),
            }
        )
    return {
        "apple_payload_id": apple_payload["apple_payload_id"],
        "signal_count": len(apple_payload.get("signals", [])),
        "top_visible_signals": top_signals,
        "apple_overrepresented_artists": payload_signature_refs,
        "optional_future_fields": {
            "playlist_context": apple_payload.get(
                "playlist_context",
                {"playlist_name": None, "playlist_kind": "unknown"},
            ),
            "track_level_signals": apple_payload.get("track_level_signals", []),
            "album_level_signals": apple_payload.get("album_level_signals", []),
            "skip_or_completion_hints": apple_payload.get("skip_or_completion_hints", []),
            "loved_or_favorite_hints": apple_payload.get("loved_or_favorite_hints", []),
        },
    }


def visible_summary(pages: list[dict[str, Any]]) -> dict[str, Any]:
    summary = cluster_summary(pages)
    summary["multi_archetype_junctions_seen"] = [
        {
            "display_name": tile["music_object_ref"]["display_name"],
            "reaction": tile["reaction"],
            "evidence_ref": tile["evidence_ref"],
            "archetype_ids": tile["graph_context"]["archetype_ids"],
        }
        for page in pages
        for tile in page["tiles"]
        if tile["page_intent"] == "multi_archetype_junction"
    ]
    summary["false_nearby_tests_seen"] = [
        {
            "display_name": tile["music_object_ref"]["display_name"],
            "reaction": tile["reaction"],
            "evidence_ref": tile["evidence_ref"],
            "page_intent": tile["page_intent"],
        }
        for page in pages
        for tile in page["tiles"]
        if "false" in tile["page_intent"] or "boundary" in tile["page_intent"]
    ]
    return summary


def build_public_packet(
    profile_public_id: str,
    config: dict[str, Any],
    path: dict[str, Any],
    apple_payload: dict[str, Any],
    selection_role: str,
) -> dict[str, Any]:
    pages = build_pages(path, config)
    packet = {
        "schema_version": "waymark.profile_writer_input.v0.1",
        "purpose": "Blind Profile Writer input",
        "profile_public_id": profile_public_id,
        "apple_payload_id": apple_payload["apple_payload_id"],
        "run_id": f"llm_profile_review_{profile_public_id}_{config['config_id']}",
        "created_at": GENERATED_AT,
        "input_fingerprint": "",
        "page_count_config": {
            **config,
            "tile_count": (config["artist_pages"] + config["album_pages"] + config["song_pages"]) * 12,
        },
        "blindness_contract": {
            "hidden_inputs_used_for_generation": False,
            "public_packet_contains_hidden_truth": False,
            "forbidden_context_absent": [
                "hidden_profile_label",
                "hidden_archetype_tiers",
                "unshown_hidden_reactions",
                "hidden_reason_tags",
                "hidden_lookup_status",
            ],
        },
        "allowed_context": {
            "canonical_graph_metadata_included": [
                "family_numbers",
                "archetype_ids",
                "roles",
                "best_recognition_tier",
                "best_survey_tier",
            ],
            "page_metadata_included": [
                "page_intent",
                "candidate_basis",
                "scores",
                "generator_visible_inputs",
            ],
            "survey_responses_included": [
                "reaction",
                "atlas_signal_interpretation",
                "app_ui_candidate",
                "observed_selected_tags",
                "shown_unselected_tags",
            ],
        },
        "reaction_scale": {
            reaction: {
                "numeric_score_for_backtests": REACTION_SCORE[reaction],
                "profile_writer_guidance": {
                    "love": "strong positive, but scope remains unknown unless reinforced",
                    "like": "qualified positive or partial positive",
                    "ok": "waypoint, context, or familiarity signal rather than landmark evidence",
                    "dont_like": "negative signal with careful scope control",
                    "dont_know_enough": "familiarity failure, not taste failure",
                }[reaction],
            }
            for reaction in REACTIONS
        },
        "observed_response_counts_by_stage": response_counts_by_stage(pages),
        "apple_payload_summary": apple_payload_summary(apple_payload, pages),
        "deterministic_visible_evidence_summary": visible_summary(pages),
        "canonical_graph_dictionary": {
            "dictionary_available": False,
            "families": [],
            "archetypes": [],
            "instruction": "Do not invent human-readable meanings for family numbers or archetype IDs.",
        },
        "pages": pages,
    }
    packet["input_fingerprint"] = fingerprint({**packet, "input_fingerprint": ""})
    return packet


def hidden_truth_packet(
    public_packet: dict[str, Any],
    hidden_corpus: dict[str, Any],
    fake_profile: dict[str, Any],
) -> dict[str, Any]:
    observed_keys = {
        canonical_ref_key(tile["music_object_ref"])
        for page in public_packet["pages"]
        for tile in page["tiles"]
    }
    heldout = []
    for item in hidden_corpus["reactions"]:
        ref = item["music_object_ref"]
        key = canonical_ref_key(ref)
        if key in observed_keys:
            continue
        heldout.append(
            {
                "music_object_ref": ref,
                "reaction": item["reaction"],
                "familiarity_band": item.get("familiarity_band"),
                "confidence": item.get("confidence"),
            }
        )
    by_type: dict[str, Counter[str]] = defaultdict(Counter)
    by_archetype: dict[str, Counter[str]] = defaultdict(Counter)
    for item in heldout:
        by_type[item["music_object_ref"]["object_type"]][item["reaction"]] += 1
    for item in fake_profile.get("primary_archetype_affinities", []):
        by_archetype[item["archetype_id"]]["primary_affinity_weight_x100"] = int(round(item["weight"] * 100))
    for item in fake_profile.get("secondary_archetype_affinities", []):
        by_archetype[item["archetype_id"]]["secondary_affinity_weight_x100"] = int(round(item["weight"] * 100))
    return {
        "schema_version": "waymark.simulator_private_hidden_truth_packet.v0.1",
        "profile_public_id": public_packet["profile_public_id"],
        "page_count_config_id": public_packet["page_count_config"]["config_id"],
        "simulation_only": True,
        "not_allowed_for_profile_writer": True,
        "hidden_profile_truth": {
            "display_label": fake_profile.get("display_label"),
            "summary": fake_profile.get("summary"),
            "context_lane": fake_profile.get("context_lane"),
            "false_nearby_lane": fake_profile.get("false_nearby_lane"),
            "primary_archetype_affinities": fake_profile.get("primary_archetype_affinities", []),
            "secondary_archetype_affinities": fake_profile.get("secondary_archetype_affinities", []),
            "hidden_anti_affinities": fake_profile.get("hidden_anti_affinities", []),
        },
        "observed_survey_key_count": len(observed_keys),
        "heldout_populated_reaction_count": len(heldout),
        "heldout_reaction_distribution_by_object_type": {
            object_type: {reaction: counter.get(reaction, 0) for reaction in REACTIONS}
            for object_type, counter in sorted(by_type.items())
        },
        "hidden_profile_archetype_weight_summary": {
            archetype_id: dict(counter)
            for archetype_id, counter in sorted(by_archetype.items())
        },
        "heldout_reaction_examples": heldout[:80],
        "private_field_redactions": [
            "reason_tags removed",
            "hidden lookup status removed",
            "private corpus identifier removed",
        ],
    }


def response_request(
    system_prompt: str,
    developer_prompt: str,
    user_payload: dict[str, Any],
    output_schema: dict[str, Any],
    schema_name: str,
) -> dict[str, Any]:
    return {
        "model": MODEL_ID,
        "input": [
            {"role": "system", "content": [{"type": "input_text", "text": system_prompt}]},
            {"role": "developer", "content": [{"type": "input_text", "text": developer_prompt}]},
            {"role": "user", "content": [{"type": "input_text", "text": json.dumps(user_payload, indent=2)}]},
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


def output_is_schema_valid(schema_path: Path, document_path: Path) -> bool:
    return document_path.exists() and not validate_json_schema(schema_path, document_path)


def replace_placeholder(payload: Any, writer_output: dict[str, Any]) -> Any:
    if isinstance(payload, dict):
        if payload == {"replace_with": "waymark.profile_writer_output.v0.1 JSON"}:
            return writer_output
        return {key: replace_placeholder(value, writer_output) for key, value in payload.items()}
    if isinstance(payload, list):
        return [replace_placeholder(item, writer_output) for item in payload]
    return payload


def request_contains_forbidden_writer_context(request_payload: dict[str, Any]) -> bool:
    text = json.dumps(request_payload)
    forbidden = [
        "hidden_profile_truth",
        "optional_hidden_truth_packet_for_simulation_only",
        "primary_archetype_affinities",
        "secondary_archetype_affinities",
        "hidden_anti_affinities",
        "fake_profile_",
        "hidden_corpus_",
        "display_label",
        "Classic Suburban Dad",
        "R&B / Hip-Hop Listener",
        "Theater / Family Context User",
    ]
    return any(item in text for item in forbidden)


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


def prompt_schema_hashes() -> dict[str, Any]:
    prompt_paths = {
        "profile_writer_system": REVIEW_DIR / "prompts" / "profile_writer_system.md",
        "profile_writer_developer": REVIEW_DIR / "prompts" / "profile_writer_developer.md",
        "profile_evaluator_system": REVIEW_DIR / "prompts" / "profile_evaluator_system.md",
        "profile_evaluator_developer": REVIEW_DIR / "prompts" / "profile_evaluator_developer.md",
    }
    schema_paths = {
        "profile_writer_output": REVIEW_DIR / "schemas" / "profile_writer_output.schema.json",
        "profile_evaluator_output": REVIEW_DIR / "schemas" / "profile_evaluator_output.schema.json",
    }
    return {
        "prompt_hashes": {name: sha256_file(path) for name, path in prompt_paths.items()},
        "schema_hashes": {name: sha256_file(path) for name, path in schema_paths.items()},
    }


def writer_request(public_packet: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "task": "Generate a provisional Cartenza taste profile from the visible survey output packet. Return only schema-valid JSON.",
        "visible_survey_output_packet": public_packet,
    }
    return response_request(
        pilot.PROFILE_WRITER_SYSTEM,
        pilot.PROFILE_WRITER_DEVELOPER,
        payload,
        load_json(REVIEW_DIR / "schemas" / "profile_writer_output.schema.json"),
        "waymark_profile_writer_output_v0_1",
    )


def evaluator_request(
    public_packet: dict[str, Any],
    writer_output: dict[str, Any],
    mode: str,
    hidden_truth: dict[str, Any] | None,
) -> dict[str, Any]:
    payload = {
        "task": f"Evaluate the Profile Writer output in {mode} mode. Return only schema-valid JSON.",
        "evaluation_mode": mode,
        "visible_survey_output_packet": public_packet,
        "profile_writer_output": {"replace_with": "waymark.profile_writer_output.v0.1 JSON"},
        "optional_hidden_truth_packet_for_simulation_only": hidden_truth,
        "optional_backtest_results": None,
    }
    request = response_request(
        pilot.PROFILE_EVALUATOR_SYSTEM,
        pilot.PROFILE_EVALUATOR_DEVELOPER,
        payload,
        load_json(REVIEW_DIR / "schemas" / "profile_evaluator_output.schema.json"),
        "waymark_profile_evaluator_output_v0_1",
    )
    return inject_writer_output(request, writer_output)


def row_id(profile_public_id: str, config_id: str) -> str:
    return f"{profile_public_id}_{config_id}"


def artifact_paths(profile_public_id: str, config_id: str) -> dict[str, Path]:
    stem = row_id(profile_public_id, config_id)
    return {
        "public_packet": PUBLIC_PACKET_DIR / f"cartenza_survey_output_packet_{stem}.json",
        "hidden_truth": HIDDEN_TRUTH_DIR / f"hidden_truth_{stem}.json",
        "writer_request": REQUEST_DIR / f"profile_writer_request_{stem}.json",
        "writer_raw": RAW_DIR / f"profile_writer_raw_response_{stem}.json",
        "writer_output": PROFILE_DIR / f"profile_writer_{stem}.json",
        "evidence_request": REQUEST_DIR / f"evaluator_evidence_only_request_{stem}.json",
        "evidence_raw": RAW_DIR / f"evaluator_evidence_only_raw_response_{stem}.json",
        "evidence_output": EVALUATOR_DIR / f"evaluator_evidence_only_{stem}.json",
        "truth_request": REQUEST_DIR / f"evaluator_truth_scored_request_{stem}.json",
        "truth_raw": RAW_DIR / f"evaluator_truth_scored_raw_response_{stem}.json",
        "truth_output": EVALUATOR_DIR / f"evaluator_truth_scored_{stem}.json",
    }


def build_packets() -> list[dict[str, Any]]:
    rows = []
    for profile in PROFILES:
        index = profile["index"]
        profile_public_id = profile["public_profile_id"]
        path = load_json(BACKTEST_DIR / "max_depth_paths" / f"{profile_public_id}.json")
        apple_payload = load_json(SIM_DIR / "apple_payloads" / f"apple_payload_{index:02d}.json")
        hidden_corpus = load_json(SIM_DIR / "hidden_reaction_corpora" / f"hidden_corpus_{index:02d}.json")
        fake_profile = load_json(SIM_DIR / "fake_profiles" / f"fake_profile_{index:02d}.json")
        for config in CONFIGS:
            paths = artifact_paths(profile_public_id, config["config_id"])
            public_packet = build_public_packet(
                profile_public_id,
                config,
                path,
                apple_payload,
                profile["selection_role"],
            )
            hidden_truth = hidden_truth_packet(public_packet, hidden_corpus, fake_profile)
            write_json(paths["public_packet"], public_packet)
            write_json(paths["hidden_truth"], hidden_truth)
            rows.append(
                {
                    "profile_public_id": profile_public_id,
                    "selection_role": profile["selection_role"],
                    "config_id": config["config_id"],
                    "tile_count": public_packet["page_count_config"]["tile_count"],
                    "public_packet_path": str(paths["public_packet"].relative_to(REPO_ROOT)),
                    "hidden_truth_path": str(paths["hidden_truth"].relative_to(REPO_ROOT)),
                    "public_packet_sha256": sha256_file(paths["public_packet"]),
                    "public_packet_input_fingerprint": public_packet["input_fingerprint"],
                    "hidden_truth_sha256": sha256_file(paths["hidden_truth"]),
                }
            )
    return rows


def flag_counts(evaluations: list[dict[str, Any]]) -> dict[str, Any]:
    genre = 0
    counterevidence = 0
    secondary_lane = 0
    blocking = 0
    leakage = 0
    for item in evaluations:
        leakage_block = item.get("score_breakdown", {}).get("blindness_and_forbidden_context", {})
        if leakage_block.get("suspected_leakage") or leakage_block.get("leakage_examples"):
            leakage += 1
        for flag in item.get("red_flags", []):
            text = json.dumps(flag).casefold()
            if flag.get("severity") == "blocking":
                blocking += 1
            if "genre" in text or "stylistic" in text or "human-readable" in text:
                genre += 1
            if "counterevidence" in text or "contextual caveat" in text:
                counterevidence += 1
        truth = item.get("score_breakdown", {}).get("simulation_truth_alignment", {})
        for missed in truth.get("missed_truth_signals", []):
            text = missed.casefold()
            if "secondary" in text or "underdevelop" in text or "folded" in text:
                secondary_lane += 1
    return {
        "hidden_context_leakage_count": leakage,
        "blocking_red_flag_count": blocking,
        "genre_shorthand_issue_count": genre,
        "direct_contextual_counterevidence_issue_count": counterevidence,
        "secondary_lane_underdevelopment_count": secondary_lane,
    }


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def aggregate(rows: list[dict[str, Any]], evaluations: list[dict[str, Any]]) -> dict[str, Any]:
    evidence_scores = [
        item["overall_score_100"]
        for item in evaluations
        if item.get("evaluation_mode") == "evidence_only"
    ]
    truth_scores = [
        item["overall_score_100"]
        for item in evaluations
        if item.get("evaluation_mode") == "truth_scored_simulation"
    ]
    all_scores = evidence_scores + truth_scores
    counts = flag_counts(evaluations)
    gate = {
        "average_evaluator_score_threshold": mean(all_scores) >= 85,
        "zero_hidden_context_leakage": counts["hidden_context_leakage_count"] == 0,
        "no_blocking_red_flags": counts["blocking_red_flag_count"] == 0,
        "genre_shorthand_issues_tracked": True,
        "counterevidence_issues_measured": True,
        "secondary_lane_underdevelopment_tracked": True,
    }
    return {
        "profile_count": len({row["profile_public_id"] for row in rows}),
        "config_count": len({row["config_id"] for row in rows}),
        "packet_count": len(rows),
        "scores": {
            "average_all_evaluators": round(mean(all_scores), 2),
            "average_evidence_only": round(mean(evidence_scores), 2),
            "average_truth_scored": round(mean(truth_scores), 2),
            "minimum_all_evaluators": min(all_scores) if all_scores else None,
            "maximum_all_evaluators": max(all_scores) if all_scores else None,
        },
        "issue_counts": counts,
        "gate": gate,
        "gate_passed": all(gate.values()),
    }


def render_report(metadata: dict[str, Any]) -> str:
    agg = metadata.get("aggregate", {})
    lines = [
        "# 3x3 API Pilot Execution Report",
        "",
        f"Generated: {GENERATED_AT}",
        "",
        f"- Status: `{metadata['status']}`",
        f"- Model ID: `{metadata['model_id']}`",
        f"- Profile Writer calls: `{metadata['call_counts']['profile_writer']}`",
        f"- Evidence-only Evaluator calls: `{metadata['call_counts']['evaluator_evidence_only']}`",
        f"- Truth-scored Evaluator calls: `{metadata['call_counts']['evaluator_truth_scored']}`",
        "",
        "## Scope",
        "",
        "- Profiles: coherent-center, mixed/multi-center, context-heavy",
        "- Configs: `A2_Al1_S1`, `A3_Al1_S2`, `A4_Al2_S3`",
        "- Full 180-call batch: not run",
        "",
        "## Aggregate Scores",
        "",
    ]
    if agg:
        scores = agg["scores"]
        lines.extend(
            [
                f"- Average all evaluators: `{scores['average_all_evaluators']}`",
                f"- Average evidence-only: `{scores['average_evidence_only']}`",
                f"- Average truth-scored: `{scores['average_truth_scored']}`",
                f"- Min / max evaluator score: `{scores['minimum_all_evaluators']}` / `{scores['maximum_all_evaluators']}`",
                "",
                "## Gate",
                "",
            ]
        )
        for key, value in agg["gate"].items():
            lines.append(f"- {key}: `{value}`")
        lines.extend(
            [
                f"- Gate passed: `{agg['gate_passed']}`",
                "",
                "## Tracked Issues",
                "",
            ]
        )
        for key, value in agg["issue_counts"].items():
            lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## Rows",
            "",
            "| Profile | Role | Config | Writer | Evidence Evaluator | Truth Evaluator |",
            "|---|---|---|---:|---:|---:|",
        ]
    )
    for row in metadata.get("rows", []):
        lines.append(
            f"| `{row['profile_public_id']}` | `{row['selection_role']}` | `{row['config_id']}` | "
            f"{row.get('profile_writer_status', 'n/a')} | {row.get('evidence_score', 'n/a')} | {row.get('truth_score', 'n/a')} |"
        )
    if metadata.get("error"):
        lines.extend(["", "## Error", "", f"```text\n{metadata['error']}\n```"])
    lines.append("")
    return "\n".join(lines)


def run() -> int:
    load_env_file(REPO_ROOT / "waymark-ai-tests" / ".env")
    api_key = os.environ.get("OPENAI_API_KEY")
    rows = build_packets()
    previous_metadata = load_json(METADATA_PATH) if METADATA_PATH.exists() else {}
    previous_rows = {
        (row.get("profile_public_id"), row.get("config_id")): row
        for row in previous_metadata.get("rows", [])
    }
    for row in rows:
        row.update(previous_rows.get((row["profile_public_id"], row["config_id"]), {}))
    metadata: dict[str, Any] = {
        "schema_version": "waymark.llm_profile_review_api_pilot_3x3_execution.v0.1",
        "generated_at": GENERATED_AT,
        "status": "running",
        "model_id": MODEL_ID,
        "openai_responses_url": OPENAI_RESPONSES_URL,
        "scope": {
            "profiles": PROFILES,
            "configs": CONFIGS,
            "full_180_call_batch_run": False,
        },
        "hashes": prompt_schema_hashes(),
        "call_counts": previous_metadata.get("call_counts", {
            "profile_writer": 0,
            "evaluator_evidence_only": 0,
            "evaluator_truth_scored": 0,
        }),
        "rows": rows,
        "aggregate": {},
        "error": None,
    }
    if not api_key:
        metadata["status"] = "blocked"
        metadata["error"] = "OPENAI_API_KEY is not set; no API calls were made."
        write_json(METADATA_PATH, metadata)
        write_text(REPORT_PATH, render_report(metadata))
        print("BLOCKED: OPENAI_API_KEY is not set", file=sys.stderr)
        return 2

    evaluations = []
    try:
        for index, row in enumerate(rows, start=1):
            stem = row_id(row["profile_public_id"], row["config_id"])
            paths = artifact_paths(row["profile_public_id"], row["config_id"])
            public_packet = load_json(paths["public_packet"])
            hidden_truth = load_json(paths["hidden_truth"])

            writer_schema = REVIEW_DIR / "schemas" / "profile_writer_output.schema.json"
            evaluator_schema = REVIEW_DIR / "schemas" / "profile_evaluator_output.schema.json"

            if output_is_schema_valid(writer_schema, paths["writer_output"]):
                writer_output = load_json(paths["writer_output"])
                row["profile_writer_status"] = "passed"
                row["profile_writer_output_path"] = str(paths["writer_output"].relative_to(REPO_ROOT))
            else:
                request = writer_request(public_packet)
                if request_contains_forbidden_writer_context(request):
                    raise RuntimeError(f"Profile Writer request contains forbidden hidden/private context for {stem}")
                write_json(paths["writer_request"], request)
                row["profile_writer_request_sha256"] = json_hash(request)
                raw = api_post(request, api_key)
                metadata["call_counts"]["profile_writer"] += 1
                write_json(paths["writer_raw"], raw)
                writer_output = parse_structured_output(raw)
                write_json(paths["writer_output"], writer_output)
                writer_errors = validate_json_schema(writer_schema, paths["writer_output"])
                row["profile_writer_status"] = "passed" if not writer_errors else "failed"
                row["profile_writer_output_path"] = str(paths["writer_output"].relative_to(REPO_ROOT))
                if writer_errors:
                    raise RuntimeError(f"Profile Writer schema validation failed for {stem}: {writer_errors}")

            if output_is_schema_valid(evaluator_schema, paths["evidence_output"]):
                evidence_output = load_json(paths["evidence_output"])
            else:
                evidence_request = evaluator_request(public_packet, writer_output, "evidence_only", None)
                if "hidden_profile_truth" in json.dumps(evidence_request):
                    raise RuntimeError(f"Evidence-only Evaluator request contains hidden truth for {stem}")
                if "waymark.profile_writer_output.v0.1 JSON" in json.dumps(evidence_request):
                    raise RuntimeError(f"Evidence-only Evaluator request still contains placeholder for {stem}")
                write_json(paths["evidence_request"], evidence_request)
                row["evidence_request_sha256"] = json_hash(evidence_request)
                raw = api_post(evidence_request, api_key)
                metadata["call_counts"]["evaluator_evidence_only"] += 1
                write_json(paths["evidence_raw"], raw)
                evidence_output = parse_structured_output(raw)
                write_json(paths["evidence_output"], evidence_output)
                evidence_errors = validate_json_schema(evaluator_schema, paths["evidence_output"])
                if evidence_errors:
                    raise RuntimeError(f"Evidence-only Evaluator schema validation failed for {stem}: {evidence_errors}")
            row["evidence_score"] = evidence_output["overall_score_100"]
            row["evidence_decision"] = evidence_output["overall_decision"]
            row["evidence_output_path"] = str(paths["evidence_output"].relative_to(REPO_ROOT))
            evaluations.append(evidence_output)

            if output_is_schema_valid(evaluator_schema, paths["truth_output"]):
                truth_output = load_json(paths["truth_output"])
            else:
                truth_request = evaluator_request(public_packet, writer_output, "truth_scored_simulation", hidden_truth)
                if "hidden_profile_truth" not in json.dumps(truth_request):
                    raise RuntimeError(f"Truth-scored Evaluator request lacks hidden truth for {stem}")
                if "waymark.profile_writer_output.v0.1 JSON" in json.dumps(truth_request):
                    raise RuntimeError(f"Truth-scored Evaluator request still contains placeholder for {stem}")
                write_json(paths["truth_request"], truth_request)
                row["truth_request_sha256"] = json_hash(truth_request)
                raw = api_post(truth_request, api_key)
                metadata["call_counts"]["evaluator_truth_scored"] += 1
                write_json(paths["truth_raw"], raw)
                truth_output = parse_structured_output(raw)
                write_json(paths["truth_output"], truth_output)
                truth_errors = validate_json_schema(evaluator_schema, paths["truth_output"])
                if truth_errors:
                    raise RuntimeError(f"Truth-scored Evaluator schema validation failed for {stem}: {truth_errors}")
            row["truth_score"] = truth_output["overall_score_100"]
            row["truth_decision"] = truth_output["overall_decision"]
            row["truth_output_path"] = str(paths["truth_output"].relative_to(REPO_ROOT))
            evaluations.append(truth_output)

            metadata["rows"] = rows
            metadata["aggregate"] = aggregate(rows, evaluations)
            write_json(METADATA_PATH, metadata)
            write_text(REPORT_PATH, render_report(metadata))
            print(f"Completed {index}/9: {stem}")
            time.sleep(0.25)

        metadata["status"] = "completed"
        metadata["aggregate"] = aggregate(rows, evaluations)
        write_json(METADATA_PATH, metadata)
        write_text(REPORT_PATH, render_report(metadata))
        print(f"Completed 3x3 API pilot at {OUT_DIR.relative_to(REPO_ROOT)}")
        return 0
    except Exception as error:
        metadata["status"] = "failed"
        metadata["error"] = str(error)
        metadata["aggregate"] = aggregate(rows, evaluations) if evaluations else {}
        write_json(METADATA_PATH, metadata)
        write_text(REPORT_PATH, render_report(metadata))
        print(f"FAILED: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(run())
