#!/usr/bin/env python3
"""Assemble or refresh MissionEnrichmentInput_v0_2 from a local fixture."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from prefilter_secondary_tags_v0_2 import DEFAULT_REGISTRY_PATH, load_registry, prefilter_secondary_tags


DEFAULT_GUARDRAILS = [
    "Do not change mission or song list.",
    "Use only allowed secondary tag IDs.",
    "Do not invent artists, songs, genres, user history, tags, or affinity facts.",
    "Do not use raw graph IDs in display copy.",
    "Do not expose raw affinity tags as chip labels.",
    "Do not claim final taste truth.",
    "Do not use founder-specific language.",
    "Do not assume rock, guitar music, vocals, lyrics, albums, English-language music, or advanced music knowledge.",
    "Treat all context as provisional."
]


def _registry_entry_for_input(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "tag_id": entry["tag_id"],
        "display_label": entry["display_label"],
        "valid_primary_reactions": entry["valid_primary_reactions"],
        "atlas_effect": entry["atlas_effect"],
        "allowed_facets": entry["allowed_facets"],
    }


def assemble_input(
    payload: dict[str, Any],
    registry: dict[str, dict[str, Any]],
    refresh_prefilter: bool = False,
) -> dict[str, Any]:
    payload.setdefault("schema_version", "mission_enrichment_input_v0_2")
    payload.setdefault(
        "runtime_context",
        {
            "surface": "mission_card_and_feedback_chips",
            "mission_ordinal_for_user": 1,
            "max_secondary_tags_per_song": 6,
            "copy_mode": "external_alpha",
            "language_style": "clear_warm_music_literate",
            "avoid_founder_vocabulary": True,
        },
    )
    payload.setdefault("copy_guardrails", DEFAULT_GUARDRAILS)

    mission_context = payload["mission_context"]
    user_brief = payload.get("user_atlas_context_brief", {})
    union_tag_ids: set[str] = set()

    for route_item in payload["route_items"]:
        if refresh_prefilter or not route_item.get("prefiltered_secondary_tag_ids"):
            route_item["prefiltered_secondary_tag_ids"] = prefilter_secondary_tags(
                route_item=route_item,
                registry=registry,
                mission_type=mission_context["mission_type"],
                risk_level=mission_context.get("risk_level", "low"),
                user_atlas_context_brief=user_brief,
            )
        union_tag_ids.update(route_item["prefiltered_secondary_tag_ids"])

    payload["allowed_secondary_reaction_tags"] = {
        tag_id: _registry_entry_for_input(registry[tag_id])
        for tag_id in sorted(union_tag_ids)
        if tag_id in registry
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Source mission enrichment input fixture.")
    parser.add_argument("--output", required=True, type=Path, help="Path for assembled input.")
    parser.add_argument("--registry", default=DEFAULT_REGISTRY_PATH, type=Path)
    parser.add_argument("--refresh-prefilter", action="store_true")
    args = parser.parse_args()

    registry = load_registry(args.registry)
    payload = json.loads(args.input.read_text())
    assembled = assemble_input(payload, registry, refresh_prefilter=args.refresh_prefilter)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(assembled, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
