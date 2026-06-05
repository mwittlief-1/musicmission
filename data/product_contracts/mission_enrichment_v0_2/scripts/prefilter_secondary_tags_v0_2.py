#!/usr/bin/env python3
"""Deterministic SecondaryTagOpportunity prefilter for Mission Enrichment v0.2."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY_PATH = PACKAGE_ROOT / "registry" / "secondary_reaction_tag_registry_v0_2.json"

POSITIVE_BY_FACET = {
    "form_container": ["HOOK_WORKED", "BUILD_WORKED"],
    "melody_harmony": ["MELODY_WORKED", "HOOK_WORKED"],
    "rhythm_body": ["GROOVE_WORKED", "BEAT_WORKED", "ENERGY_WORKED"],
    "production": ["PRODUCTION_WORKED", "SOUND_WORKED"],
    "sonic_texture": ["SOUND_WORKED", "PRODUCTION_WORKED"],
    "vocal_performance": ["VOICE_WORKED", "PERFORMANCE_WORKED"],
    "instrumental_performance": ["PERFORMANCE_WORKED"],
    "lyrics_language": ["LYRICS_WORKED"],
    "narrative_theme": ["STORY_WORKED", "LYRICS_WORKED"],
    "emotion_theme": ["MOOD_WORKED"],
    "atmosphere": ["MOOD_WORKED"],
    "energy_profile": ["ENERGY_WORKED"],
    "dynamic_shape": ["BUILD_WORKED", "ARRANGEMENT_WORKED"],
    "arrangement": ["ARRANGEMENT_WORKED", "BUILD_WORKED"],
    "activity_context": ["CONTEXT_DEPENDENT"],
    "social_context": ["CONTEXT_DEPENDENT"],
    "context_rule": ["CONTEXT_DEPENDENT", "MOOD_DEPENDENT"],
}

NEGATIVE_BY_FACET = {
    "form_container": ["NO_CLEAR_HOOK", "TOO_REPETITIVE", "TOO_PREDICTABLE", "DID_NOT_HOLD_ATTENTION"],
    "melody_harmony": ["NO_CLEAR_HOOK", "TOO_PREDICTABLE", "TOO_ABSTRACT"],
    "rhythm_body": ["BEAT_DID_NOT_WORK", "TOO_BUSY", "TOO_LOW_ENERGY", "DID_NOT_HOLD_ATTENTION"],
    "production": ["PRODUCTION_DID_NOT_WORK", "TOO_SMOOTH", "TOO_ROUGH", "TOO_BUSY"],
    "sonic_texture": ["TOO_INTENSE", "TOO_SMOOTH", "TOO_ROUGH", "RIGHT_SOUND_WRONG_SONG"],
    "vocal_performance": ["VOICE_DID_NOT_WORK", "TOO_DRAMATIC", "TOO_DETACHED", "TOO_SMOOTH", "TOO_ROUGH"],
    "instrumental_performance": ["DID_NOT_HOLD_ATTENTION"],
    "lyrics_language": ["LYRICS_DID_NOT_WORK", "TOO_ABSTRACT"],
    "narrative_theme": ["LYRICS_DID_NOT_WORK", "TOO_DRAMATIC"],
    "emotion_theme": ["TOO_INTENSE", "TOO_DETACHED", "RIGHT_MOOD_WRONG_MOMENT"],
    "atmosphere": ["RIGHT_MOOD_WRONG_MOMENT", "TOO_DETACHED", "TOO_INTENSE"],
    "energy_profile": ["TOO_INTENSE", "TOO_LOW_ENERGY"],
    "dynamic_shape": ["TOO_SPARSE", "DID_NOT_HOLD_ATTENTION", "TOO_BUSY"],
    "arrangement": ["TOO_BUSY", "TOO_SPARSE", "DID_NOT_HOLD_ATTENTION"],
    "activity_context": ["CONTEXT_DEPENDENT", "NOT_TODAY_MAYBE_LATER"],
    "social_context": ["CONTEXT_DEPENDENT"],
    "context_rule": ["CONTEXT_DEPENDENT", "NOT_TODAY_MAYBE_LATER", "NEEDS_MORE_CONTEXT"],
}

UNCERTAINTY_FOR_TEST_ROLES = [
    "GOOD_NOT_CORE",
    "KEEP_AS_WAYPOINT",
    "UNSURE_BUT_CURIOUS",
    "NEEDS_ANOTHER_LISTEN",
    "INTERESTING_NOT_MINE",
]

SAFE_BACKFILL = [
    "SURPRISED_ME",
    "WOULD_TRY_MORE_NEARBY",
    "GOOD_NOT_CORE",
    "KEEP_AS_WAYPOINT",
    "UNSURE_BUT_CURIOUS",
    "NEEDS_ANOTHER_LISTEN",
    "INTERESTING_NOT_MINE",
    "GOOD_NOT_FOR_ME",
    "DID_NOT_HOLD_ATTENTION",
    "NOT_MY_LANE",
]

TEST_ROLES = {"probe", "stretch", "boundary", "contrast", "bridge", "context", "comparator"}
CONTEXT_MISSION_TYPES = {"album_container_test", "context_dependence_test"}
BOUNDARY_ALIGNMENTS = {"tests_boundary", "matches_known_negative", "contrast_item"}

VOICE_TAGS = {"VOICE_WORKED", "VOICE_DID_NOT_WORK"}
LYRIC_STORY_TAGS = {"LYRICS_WORKED", "LYRICS_DID_NOT_WORK", "STORY_WORKED"}
CONTEXT_TAGS = {"NEEDS_MORE_CONTEXT"}
ARTIST_CONTEXT_TAGS = {"RIGHT_ARTIST_WRONG_TRACK"}


def load_registry(path: Path = DEFAULT_REGISTRY_PATH) -> dict[str, dict[str, Any]]:
    data = json.loads(path.read_text())
    return data["tags"]


def _add_many(result: list[str], candidates: list[str], registry: dict[str, Any]) -> None:
    for tag_id in candidates:
        if tag_id in registry and tag_id not in result:
            result.append(tag_id)


def _facets(route_item: dict[str, Any]) -> set[str]:
    return {entry["facet"] for entry in route_item.get("song_affinity_tags", [])}


def _alignment_values(route_item: dict[str, Any]) -> set[str]:
    return {entry["alignment"] for entry in route_item.get("user_alignment_hints", [])}


def _has_artist_context(
    route_item: dict[str, Any],
    mission_type: str,
    user_atlas_context_brief: dict[str, Any] | None = None,
) -> bool:
    if route_item.get("artist_context_available") is True:
        return True
    if mission_type == "artist_depth_test":
        return True
    brief = user_atlas_context_brief or {}
    for section in ("confirmed_positive_patterns", "open_questions", "known_boundaries"):
        for entry in brief.get(section, []):
            if "artist" in entry.get("label", "").lower():
                return True
    return False


def _has_context_gate(route_item: dict[str, Any], mission_type: str, facets: set[str]) -> bool:
    flags = route_item.get("applicability_flags", {})
    return (
        mission_type in CONTEXT_MISSION_TYPES
        or flags.get("album_context_relevant") is True
        or flags.get("long_form_context_relevant") is True
        or "context_rule" in facets
        or "activity_context" in facets
        or "social_context" in facets
    )


def _applicable(
    tag_id: str,
    route_item: dict[str, Any],
    mission_type: str,
    facets: set[str],
    user_atlas_context_brief: dict[str, Any] | None,
) -> bool:
    flags = route_item.get("applicability_flags", {})
    if flags.get("is_instrumental") is True and tag_id in (VOICE_TAGS | LYRIC_STORY_TAGS):
        return False
    if flags.get("has_vocals") is False and tag_id in VOICE_TAGS:
        return False
    if flags.get("has_lyrics") is False and tag_id in LYRIC_STORY_TAGS:
        return False
    if flags.get("lyrics_language_known") is False and tag_id in LYRIC_STORY_TAGS:
        return False
    if tag_id in CONTEXT_TAGS and not _has_context_gate(route_item, mission_type, facets):
        return False
    if tag_id in ARTIST_CONTEXT_TAGS and not _has_artist_context(route_item, mission_type, user_atlas_context_brief):
        return False
    return True


def filter_applicability(
    tag_ids: list[str],
    route_item: dict[str, Any],
    registry: dict[str, Any],
    mission_type: str,
    user_atlas_context_brief: dict[str, Any] | None = None,
) -> list[str]:
    facets = _facets(route_item)
    filtered: list[str] = []
    for tag_id in tag_ids:
        if tag_id not in registry or tag_id in filtered:
            continue
        if _applicable(tag_id, route_item, mission_type, facets, user_atlas_context_brief):
            filtered.append(tag_id)
    return filtered


def prefilter_secondary_tags(
    route_item: dict[str, Any],
    registry: dict[str, Any],
    mission_type: str,
    risk_level: str = "low",
    user_atlas_context_brief: dict[str, Any] | None = None,
) -> list[str]:
    """Return 8-14 deterministic tag IDs for one route item."""

    result: list[str] = []
    facets = _facets(route_item)
    alignments = _alignment_values(route_item)
    route_role = route_item.get("route_role", "probe")
    flags = route_item.get("applicability_flags", {})

    for facet in sorted(facets):
        _add_many(result, POSITIVE_BY_FACET.get(facet, []), registry)

    _add_many(result, ["SURPRISED_ME", "WOULD_TRY_MORE_NEARBY"], registry)

    if route_role in TEST_ROLES or mission_type in CONTEXT_MISSION_TYPES:
        _add_many(result, UNCERTAINTY_FOR_TEST_ROLES, registry)

    if "sonic_texture" in facets or "production" in facets or "arrangement" in facets:
        _add_many(result, ["RIGHT_SOUND_WRONG_SONG"], registry)

    if _has_artist_context(route_item, mission_type, user_atlas_context_brief):
        _add_many(result, ["RIGHT_ARTIST_WRONG_TRACK"], registry)

    if _has_context_gate(route_item, mission_type, facets):
        _add_many(result, ["NEEDS_MORE_CONTEXT", "CONTEXT_DEPENDENT"], registry)

    if "emotion_theme" in facets or "atmosphere" in facets or "context_rule" in facets:
        _add_many(result, ["MOOD_DEPENDENT", "RIGHT_MOOD_WRONG_MOMENT"], registry)

    if flags.get("is_live_or_alt_version") is True:
        _add_many(result, ["WRONG_VERSION_OR_RECORDING"], registry)

    boundary_context = bool(alignments & BOUNDARY_ALIGNMENTS) or route_role in {"boundary", "contrast"} or risk_level == "high"
    if boundary_context:
        for facet in sorted(facets):
            _add_many(result, NEGATIVE_BY_FACET.get(facet, []), registry)
        _add_many(result, ["GOOD_NOT_FOR_ME", "NOT_MY_LANE", "LESS_LIKE_THIS"], registry)

    result = filter_applicability(result, route_item, registry, mission_type, user_atlas_context_brief)

    for tag_id in SAFE_BACKFILL:
        if len(result) >= 8:
            break
        result = filter_applicability(result + [tag_id], route_item, registry, mission_type, user_atlas_context_brief)

    return result[:14]


def prefilter_payload(payload: dict[str, Any], registry: dict[str, Any]) -> dict[str, Any]:
    mission_context = payload["mission_context"]
    brief = payload.get("user_atlas_context_brief", {})
    for route_item in payload["route_items"]:
        route_item["prefiltered_secondary_tag_ids"] = prefilter_secondary_tags(
            route_item=route_item,
            registry=registry,
            mission_type=mission_context["mission_type"],
            risk_level=mission_context.get("risk_level", "low"),
            user_atlas_context_brief=brief,
        )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Mission enrichment input JSON to update.")
    parser.add_argument("--output", required=True, type=Path, help="Path for the updated input JSON.")
    parser.add_argument("--registry", default=DEFAULT_REGISTRY_PATH, type=Path)
    args = parser.parse_args()

    payload = json.loads(args.input.read_text())
    registry = load_registry(args.registry)
    updated = prefilter_payload(payload, registry)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(updated, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
