#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
WAYMARK_AI_SRC = REPO_ROOT / "waymark-ai-tests" / "src"
if str(WAYMARK_AI_SRC) not in sys.path:
    sys.path.insert(0, str(WAYMARK_AI_SRC))

from waymark_ai_tests.openai_client import (  # noqa: E402
    build_request_payload,
    call_openai,
    config_from_env,
    extract_output_text,
    extract_usage,
    parse_json_from_text,
)
from waymark_ai_tests.schema_validator import validate_json  # noqa: E402
from waymark_ai_tests.score_output import score_mission_output  # noqa: E402


DEFAULT_PROFILE_ID = "public_profile_01_A3_Al1_S2"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "data" / "mission_generation" / "alpha_first_batch_route_ready_v0_1"
SURVEY_EXPORT_ROOT = REPO_ROOT / "data" / "survey_simulation" / "survey_evidence_export" / "samples"
MISSION_DIGEST_ROOT = (
    REPO_ROOT
    / "data"
    / "mission_generation"
    / "mission_generation_digest_view_alpha_v0_1"
    / "generated_from_survey_evidence_export"
)
CANDIDATE_POOL_PATH = REPO_ROOT / "data" / "alpha_consumable_layer" / "alpha_v0" / "sample_compact_candidate_pool_alpha_v0.json"
RICH_MISSION_SCHEMA_PATH = REPO_ROOT / "waymark-ai-tests" / "fixtures" / "schemas" / "mission_output_schema_v0_1.json"
PRICING_PATH = REPO_ROOT / "waymark-ai-tests" / "fixtures" / "pricing" / "openai_pricing_v0_3.json"

MODEL = "gpt-5.4-mini"
PROMPT_VERSION = "alpha_first_batch_route_ready_v0_1"
ADAPTER_VERSION = "alpha_first_batch_route_ready_adapter_v0_1"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run live alpha first-batch mission generation with route-ready pool.")
    parser.add_argument("--profile-id", default=DEFAULT_PROFILE_ID)
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--max-output-tokens", type=int, default=12000)
    parser.add_argument("--timeout-seconds", type=int, default=180)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--dry-run", action="store_true", help="Write request artifacts without calling OpenAI.")
    args = parser.parse_args()

    load_env_file(REPO_ROOT / "waymark-ai-tests" / ".env")
    load_env_file(REPO_ROOT / ".env")

    run_id = now_compact()
    out_dir = args.output_root / args.profile_id / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    survey_export_path = SURVEY_EXPORT_ROOT / f"{args.profile_id}_survey_evidence_export.json"
    mission_digest_path = MISSION_DIGEST_ROOT / f"mission_generation_digest_view_{args.profile_id}.json"
    require_files([survey_export_path, mission_digest_path, CANDIDATE_POOL_PATH, RICH_MISSION_SCHEMA_PATH])

    survey_export = load_json(survey_export_path)
    mission_digest = load_json(mission_digest_path)
    raw_candidate_pool = load_json(CANDIDATE_POOL_PATH)
    candidate_pool = build_openai_candidate_pool(raw_candidate_pool)
    output_schema = load_json(RICH_MISSION_SCHEMA_PATH)
    request_fixture = build_request_fixture()
    prompt_context = build_prompt_context(args.profile_id)
    user_payload = {
        "prompt_version": PROMPT_VERSION,
        "requested_batch_size": 1,
        "survey_evidence_export": survey_export,
        "mission_generation_digest_view": mission_digest,
        "candidate_pool": candidate_pool,
        "prompt_context": prompt_context,
        "output_contract_notes": {
            "route_item_rule": (
                "Every route item must use a concrete candidate from candidate_pool.candidates. "
                "Digest and Survey examples are context only, not route-item sources, unless the exact object is also "
                "present in candidate_pool.candidates. Do not create pseudo-items or unresolved playable placeholders "
                "for this alpha smoke."
            ),
            "candidate_id_rule": "Copy the selected candidate_id exactly into each route item.",
            "candidate_membership_rule": (
                "Artist/title similarity is not enough. A route item is invalid unless route.items[].candidate_id "
                "exactly matches a row in candidate_pool.candidates."
            ),
            "batch_memory_rule": (
                "Respect prompt_context.already_selected_route_item_ids, already_selected_candidate_ids, "
                "already_selected_display_keys, excluded_route_item_ids, and excluded_candidate_ids. If the remaining "
                "candidate pool cannot satisfy the route, return review_config.ready_for_app_import=false with a "
                "blocked/retry reason instead of repeating an item."
            ),
            "release_year_rule": (
                "Candidate rows may omit release years. Use the widely accepted original release year only when "
                "unambiguous; add a review_state uncertainty flag named release_year_inferred_from_catalog_knowledge."
            ),
            "app_gate": (
                "Set review_config.ready_for_app_import true only if every route item is concrete, route-ready, "
                "selected from the candidate pool, has a MusicKit search hint, has structurally useful chips, and "
                "all possible Atlas updates satisfy recurrence/review guardrails."
            ),
            "trusted_alpha_review_tolerance": (
                "Do not set ready_for_app_import false solely because a route-ready risky, frontier, trap, "
                "dead-end, waypoint, or contradiction item correctly carries review flags. Those are Alpha "
                "diagnostics, not hard import blockers, when the mission is otherwise concrete and app-valid."
            ),
            "hard_import_blockers": [
                "rich schema invalid",
                "app mission adapter would fail",
                "route item missing from candidate_pool.candidates",
                "duplicate route item_id",
                "duplicate route candidate_id",
                "duplicate route artist/title/type identity",
                "route item repeated from prompt_context batch memory",
                "pseudo-playable route title",
                "unresolved candidate-search slot",
                "graph/candidate quarantine or unsafe review status",
                "hidden truth or raw graph leakage",
                "promoted Atlas truth or canonical graph mutation",
            ],
            "no_overclaiming": "All possible Atlas updates must stay conditional, review-gated, and scoped to future reactions.",
            "atlas_update_guardrails": [
                "Generated hypotheses are not evidence.",
                "Do not propose a new Landmark from first-batch mission generation.",
                "For every possible_atlas_update_candidate where atlas_role is not Signal only, every trigger condition must set minimum_occurrences to at least 2.",
                "For one-off first-batch evidence, prefer atlas_role Signal only with review_required=true.",
                "Trigger condition text must mention future reactions or recurrence, not a single immediate tap as sufficient proof.",
            ],
            "feedback_chip_guardrails": [
                "Every chip label must name an evidence dimension, not a simple like/dislike judgment.",
                "Do not use labels like good, bad, catchy, boring, interesting, not for me, recognized, classic reference, pop reference, or historical reference.",
                "Every signal_meaning must be at least four words and should include signal, evidence, Atlas, route, boundary, waypoint, recurrence, body, pressure, architecture, persona, or review where natural.",
                "Keep chips generic if needed, but make them structurally useful for Atlas evidence.",
            ],
            "primary_reaction_operations": ["love", "like", "keep", "not_for_me"],
        },
    }
    system_prompt = build_system_prompt()
    user_prompt = json.dumps(user_payload, indent=2, sort_keys=True)

    config = config_from_env(model=args.model, max_output_tokens=args.max_output_tokens, timeout_seconds=args.timeout_seconds)
    openai_request = build_request_payload(
        config=config,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        output_schema=output_schema,
        schema_name="waymark_mission_output_v0_1",
    )

    request_packet = {
        "client_request_id": f"alpha-first-batch-route-ready-{args.profile_id}-{run_id}",
        "tester_alias": "alpha_route_ready_smoke",
        "requested_batch_size": 1,
        "survey_evidence_export": survey_export,
        "mission_generation_digest_view": mission_digest,
        "candidate_pool": candidate_pool,
        "prompt_context": prompt_context,
    }
    write_json(out_dir / "inputs" / "survey_evidence_export.json", survey_export)
    write_json(out_dir / "inputs" / "mission_generation_digest_view.json", mission_digest)
    write_json(out_dir / "inputs" / "candidate_pool_raw_alpha_v0.json", raw_candidate_pool)
    write_json(out_dir / "inputs" / "candidate_pool_openai_flattened.json", candidate_pool)
    write_json(out_dir / "request" / "supabase_generate_first_mission_batch_request.json", request_packet)
    write_json(out_dir / "request" / "openai_request_payload.json", openai_request)

    if args.dry_run:
        write_json(out_dir / "manifest.json", build_manifest(out_dir, "dry_run", args.profile_id, None, None, None, None))
        print(f"DRY_RUN wrote {out_dir}")
        return 0

    started = time.perf_counter()
    raw_response = call_openai(config, openai_request)
    elapsed_seconds = round(time.perf_counter() - started, 3)
    output_text = extract_output_text(raw_response)
    parsed_output = parse_json_from_text(output_text)

    validation_result = validate_json(parsed_output, output_schema)
    score_report = score_mission_output(
        parsed_output=parsed_output,
        request_fixture=request_fixture,
        candidate_pool=candidate_pool,
        context_mode="mission_generation_digest_view_plus_alpha_v0_route_ready_candidates",
        prompt_template_name="mission_generator_candidate_constrained_alpha_first_batch_v0_1",
        schema_valid=bool(validation_result["valid"]),
    )
    usage = extract_usage(raw_response)
    cost_estimate = estimate_cost_usd(args.model, usage)
    product_status = derive_product_status(validation_result, score_report, parsed_output)
    model_ready = app_import_ready(parsed_output)
    app_import_ready_derived = product_status != "product_fail" and model_ready is True

    metadata = {
        "schema_version": "waymark.alpha_first_batch_route_ready_run_metadata.v0.1",
        "run_id": run_id,
        "created_at": now_iso(),
        "profile_id": args.profile_id,
        "model": args.model,
        "prompt_version": PROMPT_VERSION,
        "adapter_version": ADAPTER_VERSION,
        "run_type": "live_api",
        "context_mode": "mission_generation_digest_view_plus_alpha_v0_route_ready_candidates",
        "candidate_pool_path": rel(CANDIDATE_POOL_PATH),
        "candidate_count": len(candidate_pool["candidates"]),
        "route_ready_candidate_count": sum(1 for candidate in candidate_pool["candidates"] if candidate.get("playable_route_ready")),
        "input_tokens": usage["input_tokens"],
        "cached_input_tokens": usage["cached_input_tokens"],
        "output_tokens": usage["output_tokens"],
        "total_tokens": usage["total_tokens"],
        **cost_estimate,
        "latency_seconds": elapsed_seconds,
        "rich_mission_schema_valid": validation_result["valid"],
        "rich_mission_validation_error_count": validation_result["error_count"],
        "automated_score": score_report["automated_score"],
        "score_pass_count": score_report["pass_count"],
        "score_partial_count": score_report["partial_count"],
        "score_fail_count": score_report["fail_count"],
        "model_declared_app_import_ready": model_ready,
        "product_readiness_status": product_status,
        "app_import_ready": app_import_ready_derived,
        "app_import_ready_invariant": "forced_false_for_product_fail" if product_status == "product_fail" and model_ready else "ok",
    }

    write_json(out_dir / "generation" / "raw_openai_response.json", raw_response)
    write_text(out_dir / "generation" / "output_text.json", output_text)
    write_json(out_dir / "generation" / "mission_output_waymark_v0_1.parsed.json", parsed_output)
    write_json(out_dir / "validation" / "rich_mission_validation_result.json", validation_result)
    write_json(out_dir / "validation" / "score_report.json", score_report)
    write_json(out_dir / "metadata.json", metadata)

    app_mission_validation = {"valid": None, "error_count": None, "errors": ["not_run"]}
    app_missions: list[dict[str, Any]] = []
    if app_import_ready_derived:
        app_mission = to_app_mission(parsed_output)
        app_missions = [app_mission]
        write_json(out_dir / "app_import" / "app_mission_v0_2.json", app_mission)
        write_json(out_dir / "app_import" / "app_mission_collection_v0_2.json", app_missions)
        app_mission_validation = run_app_mission_validation(out_dir / "app_import" / "app_mission_v0_2.json", out_dir)

    response_packet = {
        "run_id": run_id,
        "status": "app_import_candidate" if app_missions and app_mission_validation.get("valid") else product_status,
        "prompt_version": PROMPT_VERSION,
        "model": args.model,
        "adapter_version": ADAPTER_VERSION,
        "mission_output_schema_version": parsed_output.get("schema_version"),
        "app_mission_schema_version": "mission.v0.2",
        "generation": parsed_output,
        "app_missions": app_missions if app_mission_validation.get("valid") else [],
        "validation": {
            "generation": validation_result,
            "automated_score": score_report,
            "app_mission": app_mission_validation,
        },
        "usage": usage,
        "estimated_cost": cost_estimate,
        "latency_ms": int(elapsed_seconds * 1000),
    }
    write_json(out_dir / "response" / "supabase_generate_first_mission_batch_response.json", response_packet)

    manifest = build_manifest(out_dir, response_packet["status"], args.profile_id, validation_result, score_report, app_mission_validation, metadata)
    write_json(out_dir / "manifest.json", manifest)
    write_text(out_dir / "README.md", render_readme(manifest, metadata))

    print(f"Wrote {out_dir}")
    print(json.dumps({"status": response_packet["status"], "rich_schema_valid": validation_result["valid"], "app_mission_valid": app_mission_validation.get("valid")}, indent=2))
    return 0


def build_system_prompt() -> str:
    return " ".join(
        [
            "You generate one Waymark trusted Alpha first-batch listening mission.",
            "Use only the supplied Survey evidence export, MissionGenerationDigestView, and route-ready candidate pool.",
            "Digest, Atlas, Survey, and strong-region examples are context only; route items must still come from candidate_pool.candidates.",
            "A mission is a structured listening experiment, not a playlist.",
            "The mission should be credible as a first Alpha route for a new user: safe enough, varied enough, and instrumented to learn.",
            "Do not use raw hidden profile truth, Profile Writer outputs, or canonical graph mutation.",
            "Do not promote provisional evidence into Atlas truth.",
            "Generated mission hypotheses are not learned user evidence.",
            "All non-Signal possible Atlas role changes require at least two future occurrences and human review.",
            "Feedback chip labels and meanings must be structurally useful evidence dimensions, not generic sentiment words.",
            "Route items must come from candidate_pool.candidates and must copy candidate_id exactly.",
            "Every route item must use a unique item_id, unique candidate_id, and unique artist/title/type identity.",
            "Respect prompt_context batch memory fields and do not repeat prior selected or excluded route items.",
            "Return only JSON matching the provided schema.",
        ]
    )


def build_prompt_context(profile_id: str) -> dict[str, Any]:
    return {
        "alpha_scope": "first_batch",
        "generation_mode": "live_route_ready_alpha_v0_smoke",
        "profile_id": profile_id,
        "storefront": "us",
        "target_model": MODEL,
        "prompt_version": PROMPT_VERSION,
        "batch_mission_index": 1,
        "batch_mission_total": 10,
        "attempt_index": 1,
        "max_generation_attempts": 14,
        "batch_seed": "alpha_v0_route_ready_replay_seed",
        "already_selected_route_item_ids": [],
        "already_selected_candidate_ids": [],
        "already_selected_display_keys": [],
        "excluded_route_item_ids": [],
        "excluded_candidate_ids": [],
        "prior_imported_mission_ids": [],
        "prior_imported_candidate_ids": [],
        "prior_attempt_summaries": [],
        "prior_review_needed_reasons": [],
        "mission_portfolio_slot": {
            "slot_id": "first_batch_start_here_safe_nearby_intro",
            "functional_role": "Safe / anchor plus nearby-road first mission",
            "required_balance": [
                "at least two safe anchors or recognition controls",
                "at least one bridge item",
                "at least one probe",
                "at most one trap or dead-end check",
                "no artist-level route items",
            ],
        },
    }


def build_request_fixture() -> dict[str, Any]:
    return {
        "request_id": "alpha_v0_first_batch_route_ready",
        "prompt": "Build a trusted Alpha first mission for this new user from the MissionGenerationDigestView and route-ready alpha_v0 candidate pool.",
        "expected_archetypes": ["Start Here / First Mission", "First Mission", "Safe / Anchor Route", "Nearby Road"],
        "expected_route_item_count": {"min": 5, "max": 8},
        "main_risks": [
            "Generic playlist instead of evidence route.",
            "Using route items outside the route-ready pool.",
            "Copying familiar digest examples without exact candidate IDs.",
            "Repeating route items inside a mission or across the batch.",
            "Treating provisional survey evidence as final Atlas truth.",
            "Marking app import ready while unresolved candidate-search placeholders remain.",
        ],
        "constraints": {
            "allow_duplicate_songs": False,
            "candidate_constrained_allowed": True,
            "required_warning_terms": ["provisional", "Atlas"],
            "avoid_artist_terms": [],
            "waypoint_terms": [],
        },
    }


def build_openai_candidate_pool(raw_pool: dict[str, Any]) -> dict[str, Any]:
    candidates = []
    for pool_name, raw_candidates in (raw_pool.get("pools") or {}).items():
        for raw in raw_candidates:
            if not raw.get("eligible_for_openai") or not raw.get("playable_route_ready"):
                continue
            route_item = raw.get("route_item") or {}
            object_type = raw.get("route_item_type") or raw.get("object_type") or route_item.get("route_item_type")
            title = raw.get("display_name") or route_item.get("display_name") or raw.get("display_label") or ""
            artist = raw.get("credited_artist") or route_item.get("credited_artist") or ""
            music_hint = raw.get("music_kit_search_hint") or route_item.get("music_kit_search_hint") or ""
            candidates.append(
                {
                    "candidate_id": raw["candidate_id"],
                    "artist": artist,
                    "title": title,
                    "album": title if object_type == "album" else "",
                    "year": raw.get("release_year") or raw.get("year"),
                    "object_type": object_type,
                    "canonical_object_type": raw.get("canonical_object_type"),
                    "canonical_entity_id": raw.get("canonical_entity_id"),
                    "known_to_user": normalize_familiarity(raw.get("familiarity_assumption")),
                    "candidate_reason": raw.get("why_selected", ""),
                    "expected_signal": raw.get("expected_signal", ""),
                    "risk_class": normalize_risk_class(raw.get("risk_class"), raw.get("mission_candidate_role")),
                    "source_risk_class": raw.get("risk_class"),
                    "selection_role": normalize_selection_role(raw.get("mission_candidate_role")),
                    "candidate_role": raw.get("candidate_role"),
                    "mission_candidate_role": raw.get("mission_candidate_role"),
                    "candidate_pool_behavior": raw.get("candidate_pool_behavior"),
                    "expected_feature_hints": raw.get("positive_inference", [])[:4],
                    "negative_inference": raw.get("negative_inference", []),
                    "do_not_infer": raw.get("do_not_infer", []),
                    "music_kit_search_hint": {
                        "search_query": music_hint,
                        "artist": artist,
                        "title": title,
                        "album": title if object_type == "album" else "",
                        "preferred_version_notes": raw.get("apple_music_resolution_policy", ""),
                        "avoid_versions": raw.get("version_risk_note", ""),
                        "resolution_status_placeholder": "unresolved",
                    },
                    "music_object_ref": raw.get("music_object_ref"),
                    "route_item": route_item,
                    "source_pool": pool_name,
                    "source_evidence_refs": raw.get("source_evidence_refs", []),
                    "source_evidence_summary": raw.get("source_evidence_summary", ""),
                    "review_status": raw.get("review_status"),
                    "playable_route_ready": raw.get("playable_route_ready"),
                    "eligible_for_openai": raw.get("eligible_for_openai"),
                    "notes_warnings": " ".join(str(value) for value in raw.get("do_not_infer", [])[:3]),
                }
            )
    return {
        "pool_id": "alpha_v0_route_ready_candidate_pool",
        "schema_version": raw_pool.get("schema_version", "alpha_v0"),
        "candidate_policy": (
            "Use only these route-ready candidates. Do not use artist-level rows. Trap rows are allowed only as explicit "
            "bounded checks, and positive trap reactions must mean unexpected exception, cultural furniture, or reassess-dead-end."
        ),
        "mission_request": build_request_fixture(),
        "mission_portfolio_slot": build_prompt_context("profile")["mission_portfolio_slot"],
        "candidate_count": len(candidates),
        "candidates": candidates,
        "source_summary": {
            "source_path": rel(CANDIDATE_POOL_PATH),
            "source_pool_counts": {name: len(items) for name, items in (raw_pool.get("pools") or {}).items()},
            "release_years_supplied_by_pool": sum(1 for candidate in candidates if candidate.get("year")),
            "release_year_gap_note": "The alpha_v0 route-ready pool does not currently supply release_year on candidate rows.",
        },
    }


def normalize_familiarity(value: Any) -> str:
    text = str(value or "").lower()
    if text in {"deeply_known", "familiar", "title_known", "unknown"}:
        return text
    if "likely_known" in text:
        return "familiar"
    return "unknown"


def normalize_selection_role(value: Any) -> str:
    text = str(value or "").lower()
    if text in {"anchor", "bridge", "probe", "trap", "checkpoint", "cooldown"}:
        return text
    if text == "risky_probe":
        return "probe"
    if text == "waypoint":
        return "checkpoint"
    return "probe"


def normalize_risk_class(value: Any, role: Any) -> str:
    role_text = str(role or "").lower()
    if role_text == "trap":
        return "trap"
    if role_text == "risky_probe":
        return "risky"
    text = str(value or "").lower()
    if text == "high":
        return "risky"
    if text == "medium":
        return "medium"
    return "safe"


def to_app_mission(generation: dict[str, Any]) -> dict[str, Any]:
    items = [to_app_item(item, index) for index, item in enumerate(generation["route"]["items"], start=1)]
    mission_type = "false_nearby_test" if any(item.get("risk_class") in {"trap", "dead_end_check"} for item in generation["route"]["items"]) else "album_test" if any(item["item_type"] == "album" for item in items) else "track_probe"
    return without_none(
        {
            "schema_version": "mission.v0.2",
            "mission_id": app_id("MIS", f"{generation['mission_id']}_alpha_route_ready"),
            "mission_title": generation["title"],
            "mission_version": "v0.1",
            "created_at": now_iso(),
            "mission_type": mission_type,
            "recommended_format": "play_items_in_order",
            "hypothesis": generation["hypothesis"],
            "inflation_warning": (
                "Alpha generated mission. Treat all route logic and Atlas implications as provisional until reviewed "
                "after real listening evidence."
            ),
            "success_bar": {
                "minimum_items_to_resolve": min(3, len(items)),
                "minimum_items_to_play": min(3, len(items)),
                "minimum_reactions_required": min(3, len(items)),
                "requires_physical_iphone": True,
                "notes": "Route-ready alpha_v0 candidate pool smoke; MusicKit resolution still must run on device.",
            },
            "run_instructions": {
                "listen_in_order": True,
                "shuffle_allowed": False,
                "raw_text": generation["route"].get("route_summary", ""),
            },
            "post_run_inference_rules": [
                {
                    "trigger": "After completion, review primary reactions, chip selections, skips, notes, and resolver state.",
                    "inference": "Create Signals and possible Atlas updates only through the Alpha review path.",
                }
            ],
            "items": items,
        }
    )


def to_app_item(item: dict[str, Any], sequence: int) -> dict[str, Any]:
    metadata = item["display_metadata"]
    search_hint = item.get("music_kit_search_hint", {})
    review_state = item.get("review_state", {})
    expected_test_signal = " ".join(
        part
        for part in [
            f"Positive: {item.get('expected_positive_signal', '')}".strip(),
            f"Negative: {item.get('expected_negative_signal', '')}".strip(),
        ]
        if part and not part.endswith(":")
    )
    notes = " ".join(
        part
        for part in [
            f"candidate_id={item.get('candidate_id')}" if item.get("candidate_id") else "",
            "Human review requested." if review_state.get("needs_human_review") else "",
            review_state.get("review_notes", ""),
        ]
        if part
    )
    return without_none(
        {
            "item_id": app_id("ITEM", item["item_id"]),
            "sequence": sequence,
            "item_type": "album" if item.get("item_type") == "album" else "track",
            "artist": metadata["artist"],
            "title": metadata["title"],
            "album": metadata.get("album") or None,
            "year": metadata.get("release_year"),
            "why_included": item.get("why_selected") or item.get("route_function"),
            "expected_test_signal": expected_test_signal,
            "player_card": {
                "flip_side": {
                    "song_hypothesis": item.get("item_hypothesis", ""),
                    "detail": item.get("route_function", ""),
                }
            },
            "feedback_chip_sets": {
                "hit": to_app_chips(item, "love"),
                "partial": to_app_chips(item, "like"),
                "ok_shelf": to_app_chips(item, "keep"),
                "miss": to_app_chips(item, "not_for_me"),
            },
            "apple_music_resolution": {
                "status": "unresolved",
                "reason": search_hint.get("search_query", "alpha_route_ready_requires_music_kit_resolution"),
                "resolver": "not_attempted",
            },
            "notes": notes or None,
        }
    )


def to_app_chips(item: dict[str, Any], operation: str) -> list[dict[str, Any]]:
    chips = item.get("feedback_chip_sets", {}).get(operation, [])
    return [
        without_none(
            {
                "tag_id": app_id("TAG", chip["chip_id"]),
                "label": chip["label"],
                "description": chip.get("signal_meaning") or chip.get("atlas_effect_hint"),
            }
        )
        for chip in chips
    ]


def run_app_mission_validation(app_mission_path: Path, out_dir: Path) -> dict[str, Any]:
    python = validation_python()
    command = [str(python), "scripts/validate_mission_json.py", rel(app_mission_path)]
    result = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    report = {
        "validator": "scripts/validate_mission_json.py",
        "valid": result.returncode == 0,
        "error_count": 0 if result.returncode == 0 else 1,
        "errors": [] if result.returncode == 0 else [(result.stderr or result.stdout).strip()],
        "stdout": result.stdout,
        "stderr": result.stderr,
        "command": command,
    }
    write_json(out_dir / "validation" / "app_mission_v0_2_validation_result.json", report)
    lines = [
        "# App Mission v0.2 Validation Report",
        "",
        f"- Target: `{rel(app_mission_path)}`",
        f"- Status: `{'passed' if report['valid'] else 'failed'}`",
        "",
        "## Command",
        "",
        "```sh",
        " ".join(command),
        "```",
        "",
        "## Output",
        "",
        "```text",
        (result.stdout or result.stderr or "").strip(),
        "```",
        "",
    ]
    write_text(out_dir / "validation" / "app_mission_v0_2_validation_report.md", "\n".join(lines))
    return report


def derive_product_status(validation_result: dict[str, Any], score_report: dict[str, Any], parsed_output: dict[str, Any]) -> str:
    if not validation_result.get("valid"):
        return "product_fail"
    if score_report.get("fail_count", 0) > 0:
        return "product_fail"
    if score_report.get("partial_count", 0) > 0:
        return "product_review_needed"
    if app_import_ready(parsed_output):
        return "app_import_candidate"
    return "product_pass_candidate"


def app_import_ready(parsed_output: dict[str, Any] | None) -> bool | None:
    if not isinstance(parsed_output, dict):
        return None
    review_config = parsed_output.get("review_config")
    if not isinstance(review_config, dict):
        return None
    return bool(review_config.get("ready_for_app_import"))


def estimate_cost_usd(model: str, usage: dict[str, Any]) -> dict[str, Any]:
    default = {
        "estimated_input_cost_usd": None,
        "estimated_cached_input_cost_usd": None,
        "estimated_output_cost_usd": None,
        "estimated_total_cost_usd": None,
        "cost_status": "pricing_missing",
        "cost_calculation_version": "alpha_first_batch_route_ready_cost_v0_1",
        "pricing_table_version": None,
        "pricing_table_date": None,
        "pricing_source": rel(PRICING_PATH),
    }
    if not PRICING_PATH.exists():
        return default
    pricing = load_json(PRICING_PATH)
    default["pricing_table_version"] = pricing.get("pricing_table_version")
    default["pricing_table_date"] = pricing.get("pricing_table_date")
    rates = (pricing.get("models") or {}).get(model)
    if not isinstance(rates, dict):
        return default
    input_tokens = usage.get("input_tokens")
    cached_tokens = usage.get("cached_input_tokens") or 0
    output_tokens = usage.get("output_tokens")
    if not isinstance(input_tokens, int) or not isinstance(output_tokens, int):
        return {**default, "cost_status": "usage_missing"}
    billable_input = max(0, input_tokens - cached_tokens)
    input_cost = billable_input * float(rates.get("input_per_1m", 0)) / 1_000_000
    cached_cost = cached_tokens * float(rates.get("cached_input_per_1m", rates.get("input_per_1m", 0))) / 1_000_000
    output_cost = output_tokens * float(rates.get("output_per_1m", 0)) / 1_000_000
    total_cost = input_cost + cached_cost + output_cost
    return {
        **default,
        "estimated_input_cost_usd": round(input_cost, 6),
        "estimated_cached_input_cost_usd": round(cached_cost, 6),
        "estimated_output_cost_usd": round(output_cost, 6),
        "estimated_total_cost_usd": round(total_cost, 6),
        "cost_status": "estimated",
    }


def build_manifest(
    out_dir: Path,
    status: str,
    profile_id: str,
    validation_result: dict[str, Any] | None,
    score_report: dict[str, Any] | None,
    app_mission_validation: dict[str, Any] | None,
    metadata: dict[str, Any] | None,
) -> dict[str, Any]:
    files = sorted(path for path in out_dir.rglob("*") if path.is_file())
    return {
        "schema_version": "waymark.alpha_first_batch_route_ready_manifest.v0.1",
        "generated_at": now_iso(),
        "profile_id": profile_id,
        "status": status,
        "model": MODEL if metadata is None else metadata.get("model"),
        "prompt_version": PROMPT_VERSION,
        "source_paths": {
            "survey_evidence_export": f"data/survey_simulation/survey_evidence_export/samples/{profile_id}_survey_evidence_export.json",
            "mission_generation_digest_view": f"data/mission_generation/mission_generation_digest_view_alpha_v0_1/generated_from_survey_evidence_export/mission_generation_digest_view_{profile_id}.json",
            "candidate_pool": rel(CANDIDATE_POOL_PATH),
        },
        "validation": {
            "rich_mission_schema_valid": None if validation_result is None else validation_result.get("valid"),
            "rich_mission_error_count": None if validation_result is None else validation_result.get("error_count"),
            "score_fail_count": None if score_report is None else score_report.get("fail_count"),
            "score_partial_count": None if score_report is None else score_report.get("partial_count"),
            "app_mission_valid": None if app_mission_validation is None else app_mission_validation.get("valid"),
        },
        "metadata": metadata or {},
        "files": [{"path": rel(path), "sha256": sha256(path)} for path in files],
    }


def render_readme(manifest: dict[str, Any], metadata: dict[str, Any]) -> str:
    return f"""# Alpha First-Batch Route-Ready Generation v0.1

Generated: `{manifest["generated_at"]}`

This packet reruns Mission Generation with:

```text
Survey Evidence Export
-> MissionGenerationDigestView
-> alpha_v0 route-ready candidate pool
-> Waymark rich mission output
-> optional Core mission.v0.2 app import artifact
```

## Status

- Status: `{manifest["status"]}`
- Profile: `{manifest["profile_id"]}`
- Model: `{metadata.get("model")}`
- Rich mission schema valid: `{manifest["validation"]["rich_mission_schema_valid"]}`
- Score fail / partial: `{manifest["validation"]["score_fail_count"]}` / `{manifest["validation"]["score_partial_count"]}`
- Model declared app-import ready: `{metadata.get("model_declared_app_import_ready")}`
- Derived app-import ready: `{metadata.get("app_import_ready")}`
- App mission valid: `{manifest["validation"]["app_mission_valid"]}`
- Estimated cost: `${metadata.get("estimated_total_cost_usd")}`
- Latency seconds: `{metadata.get("latency_seconds")}`

## Key Files

- `request/supabase_generate_first_mission_batch_request.json`
- `request/openai_request_payload.json`
- `generation/raw_openai_response.json`
- `generation/mission_output_waymark_v0_1.parsed.json`
- `validation/rich_mission_validation_result.json`
- `validation/score_report.json`
- `response/supabase_generate_first_mission_batch_response.json`

If status is `app_import_candidate`, the packet also includes:

- `app_import/app_mission_v0_2.json`
- `app_import/app_mission_collection_v0_2.json`
- `validation/app_mission_v0_2_validation_report.md`
"""


def load_env_file(path: Path) -> None:
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


def require_files(paths: list[Path]) -> None:
    missing = [path for path in paths if not path.exists()]
    if missing:
        raise SystemExit("Missing required file(s):\n" + "\n".join(str(path) for path in missing))


def validation_python() -> Path:
    venv = REPO_ROOT / ".venv" / "bin" / "python"
    return venv if venv.exists() else Path(sys.executable)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def now_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def app_id(prefix: str, value: Any) -> str:
    raw = str(value).upper()
    slug = re.sub(r"[^A-Z0-9]+", "_", raw).strip("_")
    if slug.startswith(f"{prefix}_"):
        return slug
    return f"{prefix}_{slug}"


def without_none(value: dict[str, Any]) -> dict[str, Any]:
    return {key: child for key, child in value.items() if child is not None}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
