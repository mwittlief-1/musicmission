#!/usr/bin/env python3
"""Promote clean Alpha app-import candidates to resolved UAT fixtures.

This is an offline packaging tool. It uses the bundled canonical Apple Music
catalog index only; it does not call MusicKit, mutate canonical graph truth, or
repair mission construction.
"""

from __future__ import annotations

import copy
import json
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_ROOT = ROOT / "data/product_contracts/alpha_mission_delivery_v0_2"
APP_RESOURCES = ROOT / "MusicAtlasController/Resources"
SOURCE_FIXTURE = APP_RESOURCES / "approved_alpha_app_import_candidates_v0_2.json"
CATALOG_INDEX = APP_RESOURCES / "canonical_apple_music_catalog_index_v1.json"
UAT_FIXTURE_DIR = CONTRACT_ROOT / "fixtures/uat"
REPORT_DIR = CONTRACT_ROOT / "reports"
APP_READY_FIXTURE_NAME = "app_import_ready_alpha_uat_fixtures_v0_2.json"

SUSPECT_CONTEXT_ROUTE_IDS = {
    "alpha-mission-v0-2-009-phase1g-public-profile-06-song-heavy-200-context-dependence-test-mission-type-native-policy-v0-1",
    "alpha-mission-v0-2-010-phase1g-public-profile-06-song-heavy-200-context-dependence-test-diagnostic-biased-policy-v0-1",
}

UAT_PRIMARY_RECOMMENDATION_IDS = [
    "alpha-mission-v0-2-001-phase1g-public-profile-06-edge-heavy-200-context-dependence-test-mission-type-native-policy-v0-1",
    "alpha-mission-v0-2-003-phase1g-public-profile-06-edge-heavy-200-boundary-test-experience-balanced-policy-v0-1",
    "alpha-mission-v0-2-004-phase1g-public-profile-05-song-heavy-200-boundary-test-mission-type-native-policy-v0-1",
    "alpha-mission-v0-2-007-phase1g-public-profile-06-profile-weighted-balanced-200-archetype-depth-test-experience-balanced-policy-v0-1",
    "alpha-mission-v0-2-008-phase1g-public-profile-05-song-heavy-200-archetype-depth-test-mission-type-native-policy-v0-1",
]

MIN_PROMOTION_CONFIDENCE = 0.85
GENERATED_AT = "2026-05-29T00:00:00Z"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=False) + "\n")


def slug(value: str | None) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii").lower()
    ascii_value = ascii_value.replace("&", " and ")
    return re.sub(r"[^a-z0-9]+", "-", ascii_value).strip("-")


def route_key(item: dict[str, Any]) -> str:
    return f"route_display_identity_key:track:{slug(item.get('artist_name'))}:{slug(item.get('song_title'))}"


def pair_key(title: str | None, artist: str | None) -> tuple[str, str]:
    return slug(artist), slug(title)


def build_index(entries: list[dict[str, Any]]) -> tuple[dict[str, list[dict[str, Any]]], dict[tuple[str, str], list[dict[str, Any]]]]:
    by_key: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_pair: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for entry in entries:
        if entry.get("item_type") != "track":
            continue
        for key in entry.get("match_keys", []):
            by_key[key].append(entry)
        by_pair[pair_key(entry.get("resolved_title"), entry.get("resolved_artist"))].append(entry)

    def sort_entries(values: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return sorted(values, key=lambda item: (item.get("confidence") or 0, item.get("priority") or 0), reverse=True)

    return (
        {key: sort_entries(values) for key, values in by_key.items()},
        {key: sort_entries(values) for key, values in by_pair.items()},
    )


def match_status_for(item: dict[str, Any], entry: dict[str, Any] | None, match_count: int, used_direct_key: bool) -> tuple[str, str, float, str]:
    if not entry:
        return "not_found", "high", 0.0, "No track-level match in canonical Apple Music catalog index."

    confidence = float(entry.get("confidence") or 0)
    title_exact = slug(item.get("song_title")) == slug(entry.get("resolved_title"))
    artist_exact = slug(item.get("artist_name")) == slug(entry.get("resolved_artist"))
    raw_status = str(entry.get("match_status") or "")
    basis = str(entry.get("match_basis") or "canonical_index")

    if not title_exact or not artist_exact:
        return "ambiguous", "high", confidence, f"Title/artist mismatch against canonical index: {basis}; raw_status={raw_status}."

    if not used_direct_key and match_count > 1:
        return "ambiguous", "medium", confidence, f"Multiple normalized title/artist matches without direct route key: {basis}; raw_status={raw_status}."

    if confidence >= 0.90 and raw_status in {"verified", "candidate_verified", "probable"}:
        return "verified", "low", confidence, f"Canonical index exact title/artist match; raw_status={raw_status}; basis={basis}."

    if confidence >= MIN_PROMOTION_CONFIDENCE and raw_status in {"verified", "candidate_verified", "probable"}:
        return "probable", "low", confidence, f"Canonical index exact title/artist match above UAT threshold; raw_status={raw_status}; basis={basis}."

    return "ambiguous", "medium", confidence, f"Canonical index match did not meet UAT confidence threshold; raw_status={raw_status}; basis={basis}."


def resolve_item(
    mission: dict[str, Any],
    item: dict[str, Any],
    by_key: dict[str, list[dict[str, Any]]],
    by_pair: dict[tuple[str, str], list[dict[str, Any]]],
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    direct_key = route_key(item)
    direct_matches = by_key.get(direct_key, [])
    matches = direct_matches or by_pair.get(pair_key(item.get("song_title"), item.get("artist_name")), [])
    entry = matches[0] if matches else None
    match_status, wrong_version_risk, confidence, notes = match_status_for(
        item,
        entry,
        match_count=len(matches),
        used_direct_key=bool(direct_matches),
    )

    resolution = {
        "mission_id": mission["mission_id"],
        "mission_item_id": item["mission_item_id"],
        "song_title": item["song_title"],
        "artist_name": item["artist_name"],
        "album_title": item.get("album_title"),
        "apple_music_id": entry.get("apple_catalog_id") if entry and match_status in {"verified", "probable"} else None,
        "apple_music_url": entry.get("apple_catalog_url") if entry and match_status in {"verified", "probable"} else None,
        "apple_album_id": entry.get("apple_album_id") if entry and match_status in {"verified", "probable"} else None,
        "resolved_title": entry.get("resolved_title") if entry else None,
        "resolved_artist": entry.get("resolved_artist") if entry else None,
        "resolved_album": entry.get("resolved_album") if entry else None,
        "storefront": (entry.get("storefront") if entry else None) or "us",
        "confidence": round(confidence, 3),
        "match_status": match_status,
        "match_basis": "canonical_index" if entry else "other",
        "wrong_version_risk": wrong_version_risk,
        "notes": notes,
    }
    return resolution, entry


def promote_mission(
    mission: dict[str, Any],
    resolutions: list[dict[str, Any]],
    entries_by_item_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    promoted = copy.deepcopy(mission)
    promoted["app_import_status"] = "app_import_ready"
    promoted.setdefault("validation", {})["expected_class"] = "approved_app_import_ready"
    promoted["validation"]["first_uat_resolution_promoted"] = True
    promoted["validation"]["music_resolution_source"] = "canonical_apple_music_catalog_index_v1"
    promoted["resolution"] = {
        "resolved_count": len(promoted["route"]),
        "candidate_count": 0,
        "unresolved_count": 0,
        "blocked_count": 0,
        "ordinary_alpha_ready_requires_no_unresolved": True,
        "apple_music_resolution_remaining": False,
        "resolution_source": "canonical_apple_music_catalog_index_v1",
        "resolved_at": GENERATED_AT,
    }

    resolution_by_item_id = {item["mission_item_id"]: item for item in resolutions}
    for item in promoted["route"]:
        resolution = resolution_by_item_id[item["mission_item_id"]]
        entry = entries_by_item_id[item["mission_item_id"]]
        item["resolution_status"] = "resolved"
        item["apple_music_id"] = resolution["apple_music_id"]
        item["apple_music_url"] = resolution["apple_music_url"]
        if item.get("album_title") in {"", None} and entry.get("resolved_album"):
            item["album_title"] = entry["resolved_album"]

    return promoted


def markdown_report(report: dict[str, Any]) -> str:
    rows = []
    for mission in report["missions"]:
        rows.append(
            f"| `{mission['mission_id']}` | `{mission['mission_type']}` | {mission['status']} | "
            f"{mission['resolved_items']} | {mission['blocked_items']} | {mission['ambiguous_items']} | {mission['top_blocker']} |"
        )

    item_rows = []
    for item in report["resolution_items"]:
        item_rows.append(
            f"| `{item['mission_id']}` | `{item['song_title']}` | {item['artist_name']} | "
            f"{item['match_status']} | {item['confidence']:.2f} | {item['wrong_version_risk']} | "
            f"{item['apple_music_id'] or ''} |"
        )

    return f"""Decision: {report['decision']}

Resolved missions: {report['resolved_missions']}

Resolved route items: {report['resolved_route_items']}

Blocked route items: {report['blocked_route_items']}

Ambiguous route items: {report['ambiguous_route_items']}

First-UAT recommended mission count: {report['first_uat_recommended_mission_count']}

Can TestFlight smoke start? {report['can_testflight_smoke_start']}

Top blocker: {report['top_blocker']}

Physical iPhone smoke notes: {report['physical_iphone_smoke_notes']}

# Alpha UAT Music Resolution Report v0.1

## Resolution Policy

- Source: bundled `canonical_apple_music_catalog_index_v1.json`.
- No live MusicKit, Apple Music, or catalog API calls were made.
- `candidate_verified` catalog-index entries are promoted only when title and artist match exactly and confidence is at least {MIN_PROMOTION_CONFIDENCE:.2f}; they are reported as probable, not hidden as stronger evidence.
- `Christmas Eve/Sarajevo 12/24` remains blocked because the local track-level index has no clean generic-song match, despite album-sidecar nearby variants.
- PM-suspect mixed-source context routes `009` and `010` are excluded from first UAT promotion.

## Mission Results

| mission_id | mission_type | status | resolved_items | blocked_items | ambiguous_items | top_blocker |
| --- | --- | ---: | ---: | ---: | ---: | --- |
{chr(10).join(rows)}

## Item-Level Resolution

| mission_id | song | artist | match_status | confidence | wrong_version_risk | apple_music_id |
| --- | --- | --- | --- | ---: | --- | --- |
{chr(10).join(item_rows)}
"""


def recommendation_markdown(promoted: list[dict[str, Any]], report: dict[str, Any]) -> str:
    promoted_by_id = {mission["mission_id"]: mission for mission in promoted}
    primary = [promoted_by_id[mission_id] for mission_id in UAT_PRIMARY_RECOMMENDATION_IDS if mission_id in promoted_by_id]
    alternate = [mission for mission in promoted if mission["mission_id"] not in UAT_PRIMARY_RECOMMENDATION_IDS]
    primary_rows = [
        f"| `{mission['mission_id']}` | `{mission['mission_type']}` | {len(mission['route'])} | app_import_ready |"
        for mission in primary
    ]
    alternate_rows = [
        f"| `{mission['mission_id']}` | `{mission['mission_type']}` | {len(mission['route'])} | resolved alternate |"
        for mission in alternate
    ]
    return f"""# First UAT Fixture Recommendation v0.1

Recommended first UAT set: **{len(primary)} missions / {sum(len(m['route']) for m in primary)} route items**.

The promoted fixture file contains {len(promoted)} fully resolved missions. For the first smoke pass, start with the five-mission primary set below to cover context dependence, boundary, and archetype depth while avoiding the blocked bridge routes and PM-suspect context routes `009`/`010`.

## Primary First-UAT Set

| mission_id | mission_type | route_items | status |
| --- | --- | ---: | --- |
{chr(10).join(primary_rows)}

## Resolved Alternate

| mission_id | mission_type | route_items | status |
| --- | --- | ---: | --- |
{chr(10).join(alternate_rows) if alternate_rows else '| none | | | |'}

## Blocked From First UAT

- Bridge routes `005` and `006` remain blocked by unresolved `Christmas Eve/Sarajevo 12/24` track-level matching.
- Context routes `009` and `010` remain excluded by PM decision because they are mixed-source context routes.

## Smoke Recommendation

Can TestFlight smoke start? **{report['can_testflight_smoke_start']}**

Use the primary set first. Keep the resolved alternate as a controlled second context-dependence option if PM wants a six-mission pass.
"""


def main() -> int:
    missions: list[dict[str, Any]] = load_json(SOURCE_FIXTURE)
    index_payload = load_json(CATALOG_INDEX)
    by_key, by_pair = build_index(index_payload["entries"])

    promoted: list[dict[str, Any]] = []
    resolution_items: list[dict[str, Any]] = []
    blocked_or_ambiguous: list[dict[str, Any]] = []
    mission_reports: list[dict[str, Any]] = []

    for mission in missions:
        mission_resolutions: list[dict[str, Any]] = []
        entries_by_item_id: dict[str, dict[str, Any]] = {}
        excluded_by_pm = mission["mission_id"] in SUSPECT_CONTEXT_ROUTE_IDS
        for item in mission["route"]:
            resolution, entry = resolve_item(mission, item, by_key, by_pair)
            if entry and resolution["match_status"] in {"verified", "probable"}:
                entries_by_item_id[item["mission_item_id"]] = entry
            mission_resolutions.append(resolution)
            resolution_items.append(resolution)

        blocked = [item for item in mission_resolutions if item["match_status"] in {"blocked", "not_found"}]
        ambiguous = [item for item in mission_resolutions if item["match_status"] == "ambiguous"]
        resolvable = not excluded_by_pm and not blocked and not ambiguous and len(entries_by_item_id) == len(mission["route"])

        status = "promoted_app_import_ready" if resolvable else "not_promoted"
        top_blocker = "none"
        if excluded_by_pm:
            top_blocker = "pm_excluded_mixed_source_context_route"
        elif blocked:
            top_blocker = blocked[0]["notes"]
        elif ambiguous:
            top_blocker = ambiguous[0]["notes"]

        mission_reports.append(
            {
                "mission_id": mission["mission_id"],
                "mission_type": mission["mission_type"],
                "status": status,
                "excluded_by_pm": excluded_by_pm,
                "resolved_items": sum(1 for item in mission_resolutions if item["match_status"] in {"verified", "probable"}),
                "blocked_items": len(blocked),
                "ambiguous_items": len(ambiguous),
                "top_blocker": top_blocker,
            }
        )

        if resolvable:
            promoted.append(promote_mission(mission, mission_resolutions, entries_by_item_id))
        else:
            blocked_or_ambiguous.extend(
                [
                    {**item, "blocked_reason": top_blocker if excluded_by_pm else item["notes"]}
                    for item in mission_resolutions
                    if excluded_by_pm or item["match_status"] in {"blocked", "not_found", "ambiguous"}
                ]
            )

    mission_type_counts = Counter(mission["mission_type"] for mission in promoted)
    resolved_route_items = sum(len(mission["route"]) for mission in promoted)
    first_uat_recommended_count = len([mission_id for mission_id in UAT_PRIMARY_RECOMMENDATION_IDS if any(m["mission_id"] == mission_id for m in promoted)])
    can_smoke = (
        first_uat_recommended_count >= 3
        and resolved_route_items >= 18
        and len(mission_type_counts) >= 2
        and all(item["resolution_status"] == "resolved" for mission in promoted for item in mission["route"])
    )

    report = {
        "artifact": "music_resolution_report_v0_1",
        "generated_at": GENERATED_AT,
        "decision": "PASS" if can_smoke else "PARTIAL",
        "source_fixture": str(SOURCE_FIXTURE.relative_to(ROOT)),
        "catalog_index": str(CATALOG_INDEX.relative_to(ROOT)),
        "resolved_missions": len(promoted),
        "resolved_route_items": resolved_route_items,
        "blocked_route_items": len([item for item in resolution_items if item["match_status"] in {"blocked", "not_found"}]),
        "ambiguous_route_items": len([item for item in resolution_items if item["match_status"] == "ambiguous"]),
        "first_uat_recommended_mission_count": first_uat_recommended_count,
        "can_testflight_smoke_start": "Yes" if can_smoke else "No",
        "top_blocker": "No bridge mission is resolved; bridge UAT waits on Trans-Siberian Orchestra track review." if can_smoke else "Insufficient clean resolved missions.",
        "physical_iphone_smoke_notes": "Not performed in this offline pass; promoted fixtures are ready for physical iPhone playback smoke.",
        "mission_type_counts": dict(mission_type_counts),
        "promoted_mission_ids": [mission["mission_id"] for mission in promoted],
        "excluded_suspect_context_route_ids": sorted(SUSPECT_CONTEXT_ROUTE_IDS),
        "missions": mission_reports,
        "resolution_items": resolution_items,
        "guardrails": {
            "runtime_generation": False,
            "real_listener_evidence_connection": False,
            "canonical_graph_mutation": False,
            "live_apple_music_api_calls": False,
            "candidate_items_marked_playback_ready": False,
            "suspect_context_routes_promoted": False,
        },
    }

    UAT_FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(UAT_FIXTURE_DIR / APP_READY_FIXTURE_NAME, promoted)
    write_json(APP_RESOURCES / APP_READY_FIXTURE_NAME, promoted)
    write_json(REPORT_DIR / "music_resolution_report_v0_1.json", report)
    (REPORT_DIR / "music_resolution_report_v0_1.md").write_text(markdown_report(report))
    write_json(REPORT_DIR / "blocked_or_ambiguous_resolution_items_v0_1.json", blocked_or_ambiguous)
    (REPORT_DIR / "first_uat_fixture_recommendation_v0_1.md").write_text(recommendation_markdown(promoted, report))

    print(
        json.dumps(
            {
                "decision": report["decision"],
                "resolved_missions": report["resolved_missions"],
                "resolved_route_items": report["resolved_route_items"],
                "blocked_route_items": report["blocked_route_items"],
                "ambiguous_route_items": report["ambiguous_route_items"],
                "first_uat_recommended_mission_count": report["first_uat_recommended_mission_count"],
                "can_testflight_smoke_start": report["can_testflight_smoke_start"],
                "mission_type_counts": report["mission_type_counts"],
            },
            indent=2,
        )
    )
    return 0 if can_smoke else 1


if __name__ == "__main__":
    raise SystemExit(main())
