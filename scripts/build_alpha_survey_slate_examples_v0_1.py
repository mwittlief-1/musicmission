#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from build_alpha_survey_page_packet_v0_1 import (
    GRAPH_SURFACE_DIR,
    REPO_ROOT,
    RESPONSE_STATES,
    apple_exposure_prior,
    graph_refs,
    load_approved_surface_index,
    music_object_ref,
    sha256_file,
    surface_ref_for_tile,
    utc_now,
    write_json,
)


SIM_DIR = REPO_ROOT / "data/survey_simulation"
HANDOFF_DIR = SIM_DIR / "survey_evidence_export/alpha_fast_survey_app_handoff"
DEFAULT_OUTPUT_DIR = HANDOFF_DIR / "examples"

EXAMPLES = [
    {
        "mode": "graph_only",
        "run_path": SIM_DIR / "runs/run_001_graph_seed/survey_run.json",
        "output_name": "graph_only_artist_page_001_alpha_survey_slate_packet.json",
        "profile_public_id": "render_example_graph_only",
        "apple_payload_id": "none",
    },
    {
        "mode": "apple_biased",
        "run_path": SIM_DIR / "runs/run_002_apple_biased/survey_run.json",
        "output_name": "apple_biased_artist_page_001_alpha_survey_slate_packet.json",
        "profile_public_id": "render_example_apple_biased",
        "apple_payload_id": "apple_payload_example",
    },
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "untitled"


def normalize_stage(stage: str) -> str:
    return {
        "artists": "artist",
        "artist": "artist",
        "albums": "album",
        "album": "album",
        "songs": "song",
        "song": "song",
    }.get(stage, stage)


def approved_artist_candidates() -> list[dict[str, Any]]:
    data = load_json(GRAPH_SURFACE_DIR / "survey_artist_candidates_v0_2.json")
    candidates = []
    for family in data.get("families", []):
        for bucket in ["page1_core", "page2_adaptive", "page3_deep"]:
            for candidate in family.get(bucket, []):
                if candidate.get("review_status") == "approved":
                    candidates.append(candidate)
    return candidates


def replacement_tile(
    *,
    source_tile: dict[str, Any],
    approved_candidates: list[dict[str, Any]],
    used_entity_ids: set[str],
) -> dict[str, Any]:
    source_family = (source_tile.get("graph_context", {}).get("family_numbers") or [None])[0]
    candidate = None
    for row in approved_candidates:
        if row["canonical_entity_id"] in used_entity_ids:
            continue
        if source_family is not None and row.get("family_id") == source_family:
            candidate = row
            break
    if candidate is None:
        for row in approved_candidates:
            if row["canonical_entity_id"] not in used_entity_ids:
                candidate = row
                break
    if candidate is None:
        raise ValueError("No approved replacement candidate available")
    return {
        "tile_id": source_tile["tile_id"],
        "position": source_tile["position"],
        "music_object_ref": {
            "object_type": "artist",
            "ref_source": "canonical_graph",
            "canonical_artist_id": candidate["canonical_entity_id"],
            "display_name": candidate["display_label"],
            "resolution_state": "resolved",
        },
        "page_intent": candidate["survey_intent"],
        "candidate_basis": [
            "approved_canonical_graph_surface",
            candidate["survey_page_role"],
            "replacement_for_unapproved_render_example_tile",
        ],
        "graph_context": {
            "family_numbers": [candidate["family_id"]],
            "archetype_ids": list(candidate.get("archetype_ids", [])),
            "roles": [],
            "best_recognition_tier": "unknown",
            "best_survey_tier": "unknown",
        },
        "apple_evidence": {},
    }


def tile_to_render_tile(
    *,
    run_id: str,
    page: dict[str, Any],
    tile: dict[str, Any],
    surface_index: dict[tuple[str, str], list[dict[str, Any]]],
    approved_candidates: list[dict[str, Any]],
    used_entity_ids: set[str],
) -> dict[str, Any]:
    entity_id = tile["music_object_ref"].get("canonical_artist_id")
    surface_ref = surface_ref_for_tile(
        {
            **tile,
            "apple_evidence_summary": tile.get("apple_evidence", {}),
        },
        surface_index,
    )
    if surface_ref["review_status"] != "approved":
        tile = replacement_tile(
            source_tile=tile,
            approved_candidates=approved_candidates,
            used_entity_ids=used_entity_ids,
        )
        entity_id = tile["music_object_ref"].get("canonical_artist_id")

    if entity_id:
        used_entity_ids.add(entity_id)

    display_name = tile["music_object_ref"]["display_name"]
    response_id = f"{run_id.lower()}:{page['page_id']}:resp_{tile['position']:02d}"
    evidence_ref = (
        f"{page['page_id']}:{normalize_stage(page['stage'])}:{tile['position']:02d}:"
        f"{slug(display_name)}:unanswered"
    )
    normalized_tile = {
        **tile,
        "response_id": response_id,
        "evidence_ref": evidence_ref,
        "apple_evidence_summary": tile.get("apple_evidence", {}),
    }
    surface_ref = surface_ref_for_tile(normalized_tile, surface_index)
    if surface_ref["review_status"] != "approved":
        raise ValueError(f"{run_id} {display_name} is not backed by an approved graph surface")

    return {
        "render_tile_id": f"{page['page_id']}_tile_{tile['position']:02d}",
        "display_order": tile["position"],
        "response_id": response_id,
        "evidence_ref": evidence_ref,
        "music_object_ref": music_object_ref(tile["music_object_ref"]),
        "display": {
            "primary_text": display_name,
            "secondary_text": tile["music_object_ref"].get("artist_display_name"),
            "object_type": tile["music_object_ref"]["object_type"],
        },
        "page_intent": tile["page_intent"],
        "candidate_basis": list(tile.get("candidate_basis", [])),
        "approved_graph_surface_ref": surface_ref,
        "graph_refs": graph_refs(tile.get("graph_context", {})),
        "apple_exposure_prior": apple_exposure_prior(tile.get("apple_evidence", {})),
        "response_capture": {
            "allowed_states": [item["state"] for item in RESPONSE_STATES],
            "selected_tags": [],
            "selected_tags_semantics": "visible_signal_evidence",
            "shown_unselected_tags": [],
            "shown_unselected_tags_semantics": "weak_non_selected_context",
            "note": None,
            "captured_state": None,
            "normalized_operation": None,
        },
        "evidence_export_linkage": {
            "evidence_atom_id": f"survey_response:{response_id}",
            "response_id": response_id,
            "evidence_ref": evidence_ref,
            "supporting_visible_response_refs": [],
        },
    }


def build_example(example: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    run_path = example["run_path"].resolve()
    run = load_json(run_path)
    surface_index = load_approved_surface_index()
    approved_candidates = approved_artist_candidates()
    used_entity_ids: set[str] = set()
    source_page = run["pages"][0]
    stage = normalize_stage(source_page["stage"])
    tiles = [
        tile_to_render_tile(
            run_id=run["run_id"],
            page=source_page,
            tile=tile,
            surface_index=surface_index,
            approved_candidates=approved_candidates,
            used_entity_ids=used_entity_ids,
        )
        for tile in source_page["tiles"]
    ]
    packet = {
        "schema_version": "waymark.alpha_survey_page_packet.v0.1",
        "packet_id": f"alpha_survey_slate_packet:{example['mode']}:{run['run_id'].lower()}:{source_page['page_id']}",
        "created_at": utc_now(),
        "source": {
            "profile_public_id": example["profile_public_id"],
            "apple_payload_id": example["apple_payload_id"],
            "survey_run_id": run["run_id"],
            "source_packet_schema_version": run["schema_version"],
            "source_packet_path": str(run_path.relative_to(REPO_ROOT)),
            "source_public_packet_sha256": sha256_file(run_path),
            "source_input_fingerprint": run["run_id"].lower(),
        },
        "page_count_recommendation": {
            "config_id": f"{example['mode']}_artist_page_001_render_example",
            "artist_pages": 1 if stage == "artist" else 0,
            "album_pages": 1 if stage == "album" else 0,
            "song_pages": 1 if stage == "song" else 0,
            "tile_count": len(tiles),
            "alpha_status": "render_example_not_onboarding_recommendation",
            "qualification": "single-page render fixture only; not an onboarding-length recommendation",
        },
        "response_state_contract": RESPONSE_STATES,
        "tag_and_note_contract": {
            "selected_tags": {
                "type": "array",
                "required": True,
                "empty_allowed": True,
                "signal_semantics": "visible_signal_evidence",
            },
            "shown_unselected_tags": {
                "type": "array",
                "required": True,
                "empty_allowed": True,
                "signal_semantics": "weak_non_selected_context",
            },
            "note": {
                "type": "string_or_null",
                "required": True,
                "empty_allowed": True,
            },
        },
        "private_data_boundary": {
            "private_simulator_truth_excluded": True,
            "hidden_corpus_reactions_excluded": True,
            "hidden_reason_tags_excluded": True,
            "lookup_state_excluded": True,
            "raw_candidate_scores_excluded": True,
            "generation_prompts_excluded": True,
            "profile_writer_prose_excluded": True,
        },
        "evidence_export_compatibility": {
            "target_schema_version": "waymark.survey_evidence_export.v0.1",
            "target_atlas_flow": [
                "Survey Evidence Export",
                "Signal",
                "AtlasNode",
                "provisional AtlasRoleAssignment",
                "PossibleAtlasUpdateCandidate",
                "AtlasDigestView",
            ],
            "one_atom_per_visible_response": True,
            "apple_exports_as_exposure_prior": True,
            "apple_taste_truth_required_value": False,
            "construction_only_excluded_outside_atlas_ingestion": True,
        },
        "blocking_dependencies": [
            "Atlas ingestion semantics",
            "App decision on whether Survey appears in this TestFlight build",
            "Final Canonical family/label policy",
        ],
        "pages": [
            {
                "page_id": source_page["page_id"],
                "stage": stage,
                "page_number": source_page["page_number"],
                "tile_count": len(tiles),
                "rendering": {
                    "layout": "grid",
                    "columns": "app_defined",
                    "requires_ordered_tiles": True,
                },
                "tiles": tiles,
            }
        ],
    }
    output_path = output_dir / example["output_name"]
    write_json(output_path, packet)
    return {
        "mode": example["mode"],
        "path": str(output_path.relative_to(REPO_ROOT)),
        "run_id": run["run_id"],
        "page_mode": source_page.get("page_mode"),
        "tile_count": len(tiles),
        "apple_payload_applied": source_page.get("generator_visible_inputs", {}).get("apple_payload_applied"),
    }


def render_readme(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Alpha Survey Slate Render Examples v0.1",
        "",
        "These examples are app-renderable pre-response slate packets. They contain visible tile identity, graph provenance, Apple exposure priors where applicable, response controls, and planned evidence-export linkage. They do not contain captured user reactions, hidden simulator truth, raw candidate scores, hidden reason tags, or lookup state.",
        "",
        "| mode | run | page mode | tiles | Apple applied | packet |",
        "| --- | --- | --- | ---: | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| `{row['mode']}` | `{row['run_id']}` | `{row['page_mode']}` | {row['tile_count']} | "
            f"`{row['apple_payload_applied']}` | `{row['path']}` |"
        )
    lines.extend(
        [
            "",
            "## Completed-Response Packet Examples",
            "",
            "These examples use public visible survey packets and include captured simulated responses for schema and evidence-export integration checks. They are not pre-response render fixtures.",
            "",
            "| profile | config | packet |",
            "| --- | --- | --- |",
            "| `public_profile_05` | `A3_Al1_S2` | `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/examples/public_profile_05_A3_Al1_S2_alpha_survey_page_packet.json` |",
            "| `public_profile_06` | `A3_Al1_S2` | `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/examples/public_profile_06_A3_Al1_S2_alpha_survey_page_packet.json` |",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build graph-only and Apple-biased Alpha Survey slate examples.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    output_dir = args.output_dir.resolve()
    rows = [build_example(example, output_dir) for example in EXAMPLES]
    readme_path = output_dir / "README.md"
    write_text(readme_path, render_readme(rows))
    print(readme_path.relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
