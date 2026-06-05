#!/usr/bin/env python3
"""Render or run a local Mission Enrichment prompt-test candidate."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from build_mission_enrichment_input_v0_2 import assemble_input
from prefilter_secondary_tags_v0_2 import DEFAULT_REGISTRY_PATH, load_registry
from validate_mission_enrichment_output_v0_2 import validate_contract, write_markdown_report


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_PATH = PACKAGE_ROOT / "fixtures" / "positive" / "build45_like_runtime_candidate_input.json"
PROMPT_TEMPLATE_PATH = PACKAGE_ROOT / "prompts" / "mission_enrichment_prompt_v0_2.md"
RUNS_ROOT = PACKAGE_ROOT / "runs"


def render_prompt(template: str, input_payload: dict[str, Any]) -> str:
    return template.replace("{{MISSION_ENRICHMENT_INPUT_JSON}}", json.dumps(input_payload, indent=2))


def _first_or_empty(values: list[str]) -> list[str]:
    return values[:1] if values else []


def build_placeholder_output(input_payload: dict[str, Any]) -> dict[str, Any]:
    allowed = input_payload["allowed_secondary_reaction_tags"]
    route_items = sorted(input_payload["route_items"], key=lambda item: item["sequence"])
    mission = input_payload["mission_context"]

    route_item_copy = []
    secondary_blocks = []
    used_song_tags: set[str] = set()
    used_alignments: set[str] = set()

    for route_item in route_items:
        route_item_copy.append(
            {
                "item_id": route_item["item_id"],
                "pre_play_line": f"Use this track to check one part of the mission question.",
                "why_this_song": route_item["why_included"],
                "listen_for": [
                    "Whether the main feel pulls you in.",
                    "Whether the details support or distract from the song."
                ]
            }
        )
        song_tags = [entry["tag"] for entry in route_item["song_affinity_tags"]]
        alignments = [entry["alignment"] for entry in route_item["user_alignment_hints"]]
        tags = []
        for rank, tag_id in enumerate(route_item["prefiltered_secondary_tag_ids"][:6], start=1):
            registry_entry = allowed[tag_id]
            linked_song_tags = _first_or_empty(song_tags)
            linked_alignments = _first_or_empty(alignments)
            used_song_tags.update(linked_song_tags)
            used_alignments.update(linked_alignments)
            tags.append(
                {
                    "tag_id": tag_id,
                    "rank": rank,
                    "display_label": registry_entry["display_label"],
                    "valid_primary_reactions": registry_entry["valid_primary_reactions"],
                    "why_this_tag_is_relevant": "This chip is included because it gives Atlas a focused way to interpret the primary reaction.",
                    "linked_song_affinity_tags": linked_song_tags,
                    "linked_user_alignment_hints": linked_alignments,
                    "atlas_effect": registry_entry["atlas_effect"],
                    "atlas_signal_target": {
                        "target_type": "mission_hypothesis",
                        "target_labels": ["current mission question"]
                    }
                }
            )
        secondary_blocks.append({"item_id": route_item["item_id"], "tags": tags})

    return {
        "schema_version": "mission_enrichment_output_v0_2",
        "mission_id": mission["mission_id"],
        "mission_copy": {
            "title": "Check This Route",
            "subtitle": "A short test to clarify one part of your map.",
            "short_description": "This mission uses a fixed route to test whether the current pattern holds when you listen all the way through.",
            "why_now": mission["why_this_mission_now"],
            "listen_for": [
                "Which songs feel immediately useful.",
                "Which details help or get in the way."
            ],
            "mission_hypothesis_user_facing": "If several songs land, this area may deserve more testing. If they split, Cartenza can refine the edge."
        },
        "route_item_copy": route_item_copy,
        "secondary_reaction_tag_candidates": secondary_blocks,
        "post_completion_interpretation_seeds": [
            {
                "condition": "mostly_positive",
                "readout_seed": "This route produced a useful positive signal.",
                "atlas_inference_hint": "Strengthen supported patterns, but keep the result provisional."
            },
            {
                "condition": "mixed",
                "readout_seed": "The route split in a useful way.",
                "atlas_inference_hint": "Separate song, context, and trait-level signals."
            },
            {
                "condition": "mostly_negative",
                "readout_seed": "This route may mark a boundary.",
                "atlas_inference_hint": "Weaken nearby assumptions without overgeneralizing."
            }
        ],
        "internal_quality_notes": {
            "used_song_affinity_tags": sorted(used_song_tags),
            "used_alignment_hints": sorted(used_alignments),
            "avoided_overclaims": ["No final taste claim made."],
            "risk_flags": []
        }
    }


def maybe_live_openai_completion(prompt: str, model: str) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    if "OPENAI_API_KEY" not in os.environ:
        return None, {"mode": "dry_run", "reason": "OPENAI_API_KEY is not set", "model": model}
    try:
        from openai import OpenAI
    except Exception as exc:  # pragma: no cover - depends on local environment.
        return None, {"mode": "dry_run", "reason": f"openai package unavailable: {exc}", "model": model}

    try:  # pragma: no cover - live model execution is environment dependent.
        client = OpenAI()
        response = client.responses.create(model=model, input=prompt)
        text = getattr(response, "output_text", None)
        if not text:
            return None, {"mode": "dry_run", "reason": "OpenAI response did not expose output_text", "model": model}
        return json.loads(text), {"mode": "live", "model": model}
    except Exception as exc:
        return None, {"mode": "dry_run", "reason": f"live OpenAI call failed: {exc}", "model": model}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=DEFAULT_INPUT_PATH, type=Path)
    parser.add_argument("--registry", default=DEFAULT_REGISTRY_PATH, type=Path)
    parser.add_argument("--model", default="gpt-5.4-mini")
    parser.add_argument("--dry-run", action="store_true", help="Do not attempt a live OpenAI call.")
    parser.add_argument("--run-dir", type=Path)
    args = parser.parse_args()

    registry_payload = json.loads(args.registry.read_text())
    registry = registry_payload["tags"]
    source_input = json.loads(args.input.read_text())
    input_payload = assemble_input(source_input, registry, refresh_prefilter=False)
    prompt = render_prompt(PROMPT_TEMPLATE_PATH.read_text(), input_payload)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = args.run_dir or RUNS_ROOT / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    model_log = {"mode": "dry_run", "reason": "dry-run flag set", "model": args.model}
    output_payload = None
    if not args.dry_run:
        output_payload, model_log = maybe_live_openai_completion(prompt, args.model)
    if output_payload is None:
        output_payload = build_placeholder_output(input_payload)

    report = validate_contract(input_payload, output_payload, registry_payload)

    (run_dir / "input.json").write_text(json.dumps(input_payload, indent=2) + "\n")
    (run_dir / "prompt.md").write_text(prompt)
    (run_dir / "raw_model_output.json").write_text(json.dumps(output_payload, indent=2) + "\n")
    (run_dir / "validated_output.json").write_text(json.dumps(output_payload, indent=2) + "\n")
    (run_dir / "validation_report.json").write_text(json.dumps(report.as_dict(), indent=2) + "\n")
    write_markdown_report(report, run_dir / "validation_report.md")
    (run_dir / "cost_latency_model_log.json").write_text(json.dumps(model_log, indent=2) + "\n")

    print(json.dumps({"run_dir": str(run_dir), **report.as_dict(), "model_log": model_log}, indent=2))
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
