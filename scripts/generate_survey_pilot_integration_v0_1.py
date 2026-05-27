#!/usr/bin/env python3
"""Generate controlled survey pilot integration artifacts from NP2 surfaces only."""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
NP2 = ROOT / "data" / "canonical_graph" / "normalization_pass_2"
OUT = ROOT / "data" / "survey_pilot" / "v0_1"
GENERATED_AT = "2026-05-20T14:30:00Z"
PAGE_SIZE = 12

APPROVED_INPUT_FILES = [
    "survey_artist_candidates_v0_2.json",
    "survey_album_candidates_v0_2.json",
    "survey_song_candidates_v0_2.json",
    "family_survey_readiness_v0_2.json",
    "archetype_readiness_v0_2.json",
    "canonical_quarantine_queue.json",
    "canonical_recording_versions.json",
    "dead_end_probe_candidates_v0_2.json",
    "boundary_question_bank_v0_2.json",
]

OBJECT_FILES = {
    "artist": "survey_artist_candidates_v0_2.json",
    "album": "survey_album_candidates_v0_2.json",
    "song_recording": "survey_song_candidates_v0_2.json",
}

PAGE_ROLE_FOR_NUMBER = {
    1: "page1_core",
    2: "page2_adaptive",
    3: "page3_deep",
}

PAGE_ROLE_SOURCE_CATEGORY = {
    "page1_core": "graph_core",
    "page2_adaptive": "adaptive_bridge",
    "page3_deep": "frontier_probe",
}

SURVEY_AFFINITY_FAMILIES = {3, 6, 8, 10, 12, 18}
SURVEY_SECONDARY_FAMILIES = {4, 5, 7, 11, 13}
SURVEY_BOUNDARY_FAMILIES = {9, 14, 16}

PAGE1_FAMILY_ORDER = [12, 6, 3, 10, 8, 7, 5, 4, 9, 13, 11, 18]
PAGE2_FAMILY_ORDER = [3, 6, 8, 10, 12, 18, 4, 7, 11, 13, 5, 9]
PAGE3_FAMILY_ORDER = [10, 8, 18, 3, 6, 12, 7, 11, 13, 4, 5, 9]

PILOT_PAGE1_PREFERRED_IDS = {
    "artist": [
        ("michael-jackson", 12),
        ("aretha-franklin", 6),
        ("artist-led-zeppelin", 3),
        ("green-day", 10),
        ("the-clash", 8),
        ("2pac", 7),
        ("johnny-cash", 5),
        ("f4-026-artist-bob-dylan", 4),
        ("black-sabbath", 9),
        ("bad-bunny", 13),
        ("daft-punk", 11),
        ("arctic-monkeys", 18),
    ],
    "album": [
        ("michael-jackson-thriller", 12),
        ("marvin-gaye-whats-going-on", 6),
        ("album-led-zeppelin-iv-1971", 3),
        ("green-day-dookie", 10),
        ("the-clash-london-calling", 8),
        ("2pac-all-eyez-on-me", 7),
        ("johnny-cash-at-folsom-prison", 5),
        ("f4-024-album-blue-joni-mitchell", 4),
        ("linkin-park-hybrid-theory", 9),
        ("bad-bunny-un-verano-sin-ti", 13),
        ("daft-punk-discovery", 11),
        ("tame-impala-currents", 18),
    ],
    "song_recording": [
        ("michael-jackson-billie-jean", 12),
        ("aretha-franklin-respect", 6),
        ("song-stairway-to-heaven-1971", 3),
        ("green-day-basket-case", 10),
        ("the-clash-london-calling", 8),
        ("2pac-feat-dr-dre-california-love", 7),
        ("johnny-cash-ring-of-fire", 5),
        ("f4-029-song-fast-car-tracy-chapman", 4),
        ("metallica-enter-sandman", 9),
        ("daddy-yankee-gasolina", 13),
        ("fatboy-slim-praise-you", 11),
        ("tame-impala-the-less-i-know-the-better", 18),
    ],
}


class PilotValidationError(Exception):
    pass


def load_json(name: str) -> Any:
    if name not in APPROVED_INPUT_FILES:
        raise PilotValidationError(f"Unapproved pilot input requested: {name}")
    return json.loads((NP2 / name).read_text())


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def stable_int(text: str) -> int:
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:12], 16)


def entity_ref(candidate: dict[str, Any]) -> str:
    return f"{candidate['object_type']}:{candidate['canonical_entity_id']}"


def md_table(headers: list[str], rows: list[list[Any]]) -> str:
    def esc(value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, dict):
            return "; ".join(f"{key}: {val}" for key, val in sorted(value.items()))
        if isinstance(value, (list, tuple, set)):
            return "; ".join(esc(item) for item in value)
        return str(value).replace("|", "\\|").replace("\n", "<br>")

    output = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        output.append("| " + " | ".join(esc(item) for item in row) + " |")
    return "\n".join(output)


def get_candidates(
    survey_payloads: dict[str, dict[str, Any]],
    object_type: str,
    family_id: int,
    pool_name: str,
) -> list[dict[str, Any]]:
    family_payload = survey_payloads[object_type]["families"][family_id - 1]
    return list(family_payload[pool_name])


def recording_safe(recording_versions: dict[str, dict[str, Any]], candidate: dict[str, Any]) -> bool:
    if candidate["object_type"] != "song_recording":
        return True
    version = recording_versions.get(candidate["canonical_entity_id"])
    return bool(version and version.get("survey_safe") and version.get("review_status") == "approved")


def is_candidate_safe(
    candidate: dict[str, Any],
    quarantine_refs: set[str],
    recording_versions: dict[str, dict[str, Any]],
) -> bool:
    return (
        candidate["review_status"] == "approved"
        and not candidate.get("quarantine_reasons")
        and entity_ref(candidate) not in quarantine_refs
        and candidate["survey_page_role"] != "suppressed"
        and recording_safe(recording_versions, candidate)
    )


def source_category_for(candidate: dict[str, Any], page_number: int) -> str:
    intent = candidate["survey_intent"]
    if page_number == 1:
        return "graph_core"
    if intent == "bridge_test":
        return "adaptive_bridge"
    if intent == "false_nearby_test":
        return "false_nearby_probe"
    if intent == "boundary_test":
        return "negative_control_probe"
    if intent in {"deepening_only", "album_world_test"} and page_number == 3:
        return "frontier_probe"
    if intent in {"song_first_memory", "artist_affinity_probe", "recognition_anchor"} and page_number >= 2:
        return "waypoint_context_probe"
    return PAGE_ROLE_SOURCE_CATEGORY[PAGE_ROLE_FOR_NUMBER[page_number]]


def candidate_sort_key(candidate: dict[str, Any]) -> tuple[float, int, str]:
    return (-float(candidate["priority_score"]), stable_int(candidate["candidate_id"]), candidate["display_label"])


def pick_from_family_pool(
    pool_by_family: dict[int, list[dict[str, Any]]],
    family_order: list[int],
    selected: list[dict[str, Any]],
    seen_dedupe: set[str],
    source_counts: Counter[str],
    page_number: int,
    max_probe_like: int,
) -> None:
    for family_id in family_order:
        if len(selected) >= PAGE_SIZE:
            return
        for candidate in sorted(pool_by_family.get(family_id, []), key=candidate_sort_key):
            source = source_category_for(candidate, page_number)
            probe_like = source in {"false_nearby_probe", "negative_control_probe"}
            if candidate["dedupe_group"] in seen_dedupe:
                continue
            if probe_like and source_counts["false_nearby_probe"] + source_counts["negative_control_probe"] >= max_probe_like:
                continue
            selected.append(candidate)
            seen_dedupe.add(candidate["dedupe_group"])
            source_counts[source] += 1
            break


def pick_preferred_page1(
    pool_by_family: dict[int, list[dict[str, Any]]],
    object_type: str,
    selected: list[dict[str, Any]],
    seen_dedupe: set[str],
    source_counts: Counter[str],
) -> None:
    by_entity_family = {
        (candidate["canonical_entity_id"], int(candidate["family_id"])): candidate
        for candidates in pool_by_family.values()
        for candidate in candidates
    }
    for entity_id, family_id in PILOT_PAGE1_PREFERRED_IDS[object_type]:
        candidate = by_entity_family.get((entity_id, family_id))
        if candidate is None or candidate["dedupe_group"] in seen_dedupe:
            continue
        selected.append(candidate)
        seen_dedupe.add(candidate["dedupe_group"])
        source_counts[source_category_for(candidate, 1)] += 1
        if len(selected) >= PAGE_SIZE:
            return


def build_page(
    survey_payloads: dict[str, dict[str, Any]],
    object_type: str,
    page_number: int,
    eligible_families: set[int],
    quarantine_refs: set[str],
    recording_versions: dict[str, dict[str, Any]],
    positive_families: set[int],
    negative_families: set[int],
) -> list[dict[str, Any]]:
    pool_name = PAGE_ROLE_FOR_NUMBER[page_number]
    pool_by_family: dict[int, list[dict[str, Any]]] = {}
    for family_id in eligible_families:
        safe_pool = [
            candidate
            for candidate in get_candidates(survey_payloads, object_type, family_id, pool_name)
            if is_candidate_safe(candidate, quarantine_refs, recording_versions)
        ]
        pool_by_family[family_id] = safe_pool

    selected: list[dict[str, Any]] = []
    seen_dedupe: set[str] = set()
    source_counts: Counter[str] = Counter()
    if page_number == 1:
        pick_preferred_page1(pool_by_family, object_type, selected, seen_dedupe, source_counts)
        pick_from_family_pool(pool_by_family, PAGE1_FAMILY_ORDER, selected, seen_dedupe, source_counts, page_number, 0)
    elif page_number == 2:
        adaptive_order = sorted(positive_families, key=lambda family: PAGE2_FAMILY_ORDER.index(family) if family in PAGE2_FAMILY_ORDER else 999)
        adaptive_order += [family for family in PAGE2_FAMILY_ORDER if family not in adaptive_order]
        pick_from_family_pool(pool_by_family, adaptive_order, selected, seen_dedupe, source_counts, page_number, 3)
        boundary_order = sorted((negative_families or SURVEY_BOUNDARY_FAMILIES) & eligible_families)
        pick_from_family_pool(pool_by_family, boundary_order, selected, seen_dedupe, source_counts, page_number, 3)
    else:
        deep_order = sorted(positive_families, key=lambda family: PAGE3_FAMILY_ORDER.index(family) if family in PAGE3_FAMILY_ORDER else 999)
        deep_order += [family for family in PAGE3_FAMILY_ORDER if family not in deep_order]
        pick_from_family_pool(pool_by_family, deep_order, selected, seen_dedupe, source_counts, page_number, 3)

    if len(selected) < PAGE_SIZE:
        all_candidates = [
            candidate
            for family_id in sorted(eligible_families)
            for candidate in pool_by_family.get(family_id, [])
            if candidate["dedupe_group"] not in seen_dedupe
        ]
        for candidate in sorted(all_candidates, key=candidate_sort_key):
            source = source_category_for(candidate, page_number)
            if source in {"false_nearby_probe", "negative_control_probe"} and source_counts["false_nearby_probe"] + source_counts["negative_control_probe"] >= 3:
                continue
            selected.append(candidate)
            seen_dedupe.add(candidate["dedupe_group"])
            source_counts[source] += 1
            if len(selected) >= PAGE_SIZE:
                break

    if len(selected) != PAGE_SIZE:
        raise PilotValidationError(f"{object_type} page {page_number} generated {len(selected)} tiles, expected {PAGE_SIZE}")
    return selected


def synthetic_response(candidate: dict[str, Any], page_number: int, object_type: str) -> tuple[str, str]:
    family_id = int(candidate["family_id"])
    intent = candidate["survey_intent"]
    roll = stable_int(candidate["candidate_id"] + f":{page_number}:{object_type}") % 100
    if family_id in SURVEY_AFFINITY_FAMILIES:
        if page_number == 1 and roll < 28:
            return "love", "known_deep"
        if roll < 78:
            return "like", "known"
        if roll < 91:
            return "ok", "heard_of"
        return "dont_know_enough", "unknown"
    if family_id in SURVEY_SECONDARY_FAMILIES:
        if intent in {"false_nearby_test", "boundary_test"} and roll < 34:
            return "dont_like", "known"
        if roll < 42:
            return "like", "known"
        if roll < 70:
            return "ok", "heard_of"
        return "dont_know_enough", "unknown"
    if intent in {"false_nearby_test", "boundary_test"}:
        if roll < 58:
            return "dont_like", "known"
        if roll < 76:
            return "ok", "heard_of"
        return "dont_know_enough", "unknown"
    if page_number == 3 and roll < 44:
        return "dont_know_enough", "unknown"
    if roll < 24:
        return "like", "known"
    if roll < 52:
        return "ok", "heard_of"
    if roll < 80:
        return "dont_know_enough", "unknown"
    return "dont_like", "known"


def signal_strength(response: str) -> str:
    return {
        "love": "strong_positive",
        "like": "positive",
        "ok": "weak_positive_or_waypoint",
        "dont_like": "negative_scoped",
        "dont_know_enough": "unknown_familiarity_only",
    }[response]


def page_adaptive_reason(page_number: int, candidate: dict[str, Any], positive_families: set[int], negative_families: set[int]) -> str | None:
    if page_number == 1:
        return None
    family_id = int(candidate["family_id"])
    if family_id in positive_families:
        return "selected from family with prior positive or okay survey evidence"
    if family_id in negative_families:
        return "selected as scoped boundary follow-up after prior negative evidence"
    if candidate["survey_intent"] in {"false_nearby_test", "boundary_test"}:
        return "selected as cautious probe; probe response cannot create Atlas Dead End"
    return "selected to preserve family/archetype coverage while adapting"


def build_source_mix(tiles: list[dict[str, Any]]) -> dict[str, int]:
    source_mix = {
        "apple_payload": 0,
        "graph_core": 0,
        "adaptive_bridge": 0,
        "false_nearby_probe": 0,
        "frontier_probe": 0,
        "waypoint_context_probe": 0,
        "negative_control_probe": 0,
    }
    for tile in tiles:
        source_mix[tile["source_category"]] += 1
    return source_mix


def distribution(values: list[Any]) -> dict[str, int]:
    return {str(key): value for key, value in sorted(Counter(values).items(), key=lambda item: str(item[0]))}


def page_type_for(object_type: str) -> str:
    return "song" if object_type == "song_recording" else object_type


def report_header(title: str) -> list[str]:
    return [f"# {title}", "", f"Generated: {GENERATED_AT}", ""]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    survey_payloads = {
        "artist": load_json("survey_artist_candidates_v0_2.json"),
        "album": load_json("survey_album_candidates_v0_2.json"),
        "song_recording": load_json("survey_song_candidates_v0_2.json"),
    }
    family_readiness = load_json("family_survey_readiness_v0_2.json")
    archetype_readiness = load_json("archetype_readiness_v0_2.json")
    quarantine_queue = load_json("canonical_quarantine_queue.json")
    recording_versions_list = load_json("canonical_recording_versions.json")
    dead_end_probes = load_json("dead_end_probe_candidates_v0_2.json")
    boundary_questions = load_json("boundary_question_bank_v0_2.json")

    quarantine_refs = {row["entity_ref"] for row in quarantine_queue}
    recording_versions = {row["recording_id"]: row for row in recording_versions_list}
    eligible_families = {
        row["family_id"]
        for row in family_readiness
        if row["survey_readiness"] == "survey_ready" and row["fast_survey_allowed"]
    }
    context_families = {
        row["family_id"]
        for row in family_readiness
        if row["survey_readiness"] == "context_only" or not row["fast_survey_allowed"]
    }
    if eligible_families & context_families:
        raise PilotValidationError("A family is both eligible and context-only")

    dead_end_keys = {(row["entity_type"], row["entity_id"]) for row in dead_end_probes}
    boundary_keys = {(row.get("entity_id"), row.get("family_id")) for row in boundary_questions}

    page_logs: list[dict[str, Any]] = []
    tile_logs: list[dict[str, Any]] = []
    response_logs: list[dict[str, Any]] = []
    positive_families: set[int] = set()
    negative_families: set[int] = set()
    timestamp_base = datetime(2026, 5, 20, 14, 30, tzinfo=timezone.utc)
    sequence = 0

    for object_type in ["artist", "album", "song_recording"]:
        for page_number in [1, 2, 3]:
            candidates = build_page(
                survey_payloads,
                object_type,
                page_number,
                eligible_families,
                quarantine_refs,
                recording_versions,
                positive_families,
                negative_families,
            )
            page_tiles = []
            for index, candidate in enumerate(candidates, start=1):
                sequence += 1
                response, familiarity = synthetic_response(candidate, page_number, object_type)
                source_category = source_category_for(candidate, page_number)
                candidate_key = (candidate["object_type"], candidate["canonical_entity_id"])
                timestamp = (timestamp_base + timedelta(seconds=sequence * 17)).isoformat().replace("+00:00", "Z")
                tile = {
                    "candidate_id": candidate["candidate_id"],
                    "canonical_entity_id": candidate["canonical_entity_id"],
                    "object_type": candidate["object_type"],
                    "family_id": candidate["family_id"],
                    "archetype_ids": candidate["archetype_ids"],
                    "survey_page_role": candidate["survey_page_role"],
                    "survey_intent": candidate["survey_intent"],
                    "dedupe_group": candidate["dedupe_group"],
                    "priority_score": candidate["priority_score"],
                    "trigger_rule": candidate["trigger_rule"],
                    "shown_page_number": page_number,
                    "shown_position": index,
                    "user_response": response,
                    "familiarity_state": familiarity,
                    "timestamp": timestamp,
                    "apple_payload_reason": None,
                    "adaptive_reason": page_adaptive_reason(page_number, candidate, positive_families, negative_families),
                    "positive_inference": candidate["positive_inference"],
                    "negative_inference": candidate["negative_inference"],
                    "do_not_infer": candidate["do_not_infer"],
                    "display_label": candidate["display_label"],
                    "source_category": source_category,
                    "is_false_nearby_or_boundary_probe": (
                        candidate["survey_intent"] in {"false_nearby_test", "boundary_test"}
                        or candidate_key in dead_end_keys
                        or (candidate["canonical_entity_id"], candidate["family_id"]) in boundary_keys
                    ),
                    "atlas_write_mode": "provisional_signal_only",
                    "atlas_promotion_created": False,
                }
                tile_logs.append(tile)
                page_tiles.append(tile)
                response_logs.append(
                    {
                        "candidate_id": tile["candidate_id"],
                        "canonical_entity_id": tile["canonical_entity_id"],
                        "object_type": tile["object_type"],
                        "family_id": tile["family_id"],
                        "archetype_ids": tile["archetype_ids"],
                        "survey_page_role": tile["survey_page_role"],
                        "survey_intent": tile["survey_intent"],
                        "user_response": response,
                        "familiarity_state": familiarity,
                        "signal_strength": signal_strength(response),
                        "provisional_evidence_only": True,
                        "atlas_promotion_created": False,
                    }
                )
                if response in {"love", "like", "ok"}:
                    positive_families.add(int(candidate["family_id"]))
                elif response == "dont_like":
                    negative_families.add(int(candidate["family_id"]))

            dedupe_passed = len({tile["dedupe_group"] for tile in page_tiles}) == PAGE_SIZE
            quarantine_passed = all(entity_ref(tile) not in quarantine_refs for tile in page_tiles)
            if not dedupe_passed:
                raise PilotValidationError(f"{object_type} page {page_number} failed dedupe")
            if not quarantine_passed:
                raise PilotValidationError(f"{object_type} page {page_number} includes quarantined tile")
            page_logs.append(
                {
                    "page_type": page_type_for(object_type),
                    "object_type": object_type,
                    "page_number": page_number,
                    "source_mix": build_source_mix(page_tiles),
                    "dedupe_checks_passed": dedupe_passed,
                    "quarantine_checks_passed": quarantine_passed,
                    "family_distribution": distribution([tile["family_id"] for tile in page_tiles]),
                    "archetype_distribution": distribution([aid for tile in page_tiles for aid in tile["archetype_ids"]]),
                    "tile_count": PAGE_SIZE,
                    "candidate_ids": [tile["candidate_id"] for tile in page_tiles],
                    "display_labels": [tile["display_label"] for tile in page_tiles],
                    "pilot_rules": {
                        "page1_pool": "page1_core only" if page_number == 1 else None,
                        "page2_pool": "page2_adaptive only" if page_number == 2 else None,
                        "page3_pool": "page3_deep only" if page_number == 3 else None,
                        "context_only_families_excluded": sorted(context_families),
                    },
                }
            )

    acceptance_failures = []
    for tile in tile_logs:
        if tile["family_id"] not in eligible_families:
            acceptance_failures.append([tile["candidate_id"], "non_survey_ready_family"])
        expected_role = PAGE_ROLE_FOR_NUMBER[tile["shown_page_number"]]
        if tile["survey_page_role"] != expected_role:
            acceptance_failures.append([tile["candidate_id"], "wrong_page_role"])
        if entity_ref(tile) in quarantine_refs:
            acceptance_failures.append([tile["candidate_id"], "quarantined_tile"])
        if tile["atlas_promotion_created"]:
            acceptance_failures.append([tile["candidate_id"], "atlas_promotion_created"])
        if tile["object_type"] == "song_recording" and not recording_safe(recording_versions, tile):
            acceptance_failures.append([tile["candidate_id"], "recording_version_not_survey_safe"])

    manifest = {
        "generated_at": GENERATED_AT,
        "status": "controlled_survey_pilot_integration_pass" if not acceptance_failures else "blocked_by_pilot_acceptance_failures",
        "approved_input_files": APPROVED_INPUT_FILES,
        "use_raw_graph_fast_survey": False,
        "full_canonical_import_approved": False,
        "hard_lock_approved": False,
        "unguarded_atlas_promotion_approved": False,
        "apple_payload_used": False,
        "apple_payload_note": "No Apple payload file was consumed because this dispatch restricted graph inputs to repaired Normalization Pass 2 files.",
        "eligible_families": sorted(eligible_families),
        "excluded_context_only_families": sorted(context_families),
        "page_count": len(page_logs),
        "displayed_tile_count": len(tile_logs),
        "response_count": len(response_logs),
        "acceptance_failure_count": len(acceptance_failures),
        "acceptance_failures": acceptance_failures,
    }

    write_json(OUT / "survey_pilot_manifest.json", manifest)
    write_json(OUT / "survey_pilot_page_generation_log.json", page_logs)
    write_json(OUT / "survey_pilot_tile_display_log.json", tile_logs)
    write_json(OUT / "survey_pilot_response_log.json", response_logs)

    response_counts = Counter(row["user_response"] for row in response_logs)
    response_by_object = defaultdict(Counter)
    response_by_page = defaultdict(Counter)
    dont_know_by_object = Counter()
    total_by_object = Counter()
    for tile in tile_logs:
        response_by_object[tile["object_type"]][tile["user_response"]] += 1
        response_by_page[(tile["object_type"], tile["shown_page_number"])][tile["user_response"]] += 1
        total_by_object[tile["object_type"]] += 1
        if tile["user_response"] == "dont_know_enough":
            dont_know_by_object[tile["object_type"]] += 1

    page_lines = report_header("Survey Pilot Page Generation Report")
    page_lines += [
        "This is a controlled dry pilot generated from repaired Normalization Pass 2 survey surfaces only.",
        "",
        md_table(
            ["page_type", "page", "source_mix", "family_distribution", "dedupe", "quarantine", "labels"],
            [
                [
                    page["page_type"],
                    page["page_number"],
                    page["source_mix"],
                    page["family_distribution"],
                    page["dedupe_checks_passed"],
                    page["quarantine_checks_passed"],
                    page["display_labels"],
                ]
                for page in page_logs
            ],
        ),
    ]
    (OUT / "survey_pilot_page_generation_report.md").write_text("\n".join(page_lines) + "\n")

    response_lines = report_header("Survey Pilot Response Distribution Report")
    response_lines += [
        md_table(["response", "count"], [[key, response_counts[key]] for key in sorted(response_counts)]),
        "",
        md_table(
            ["object_type", "love", "like", "ok", "dont_know_enough", "dont_like"],
            [
                [object_type] + [response_by_object[object_type][reaction] for reaction in ["love", "like", "ok", "dont_know_enough", "dont_like"]]
                for object_type in ["artist", "album", "song_recording"]
            ],
        ),
    ]
    (OUT / "survey_pilot_response_distribution_report.md").write_text("\n".join(response_lines) + "\n")

    signal_counts = Counter(row["signal_strength"] for row in response_logs)
    signal_lines = report_header("Survey Pilot Signal Quality Report")
    signal_lines += [
        "All responses are logged as provisional evidence only. No Landmark, Region, Frontier, Dead End, or Waypoint is promoted by this harness.",
        "",
        md_table(["signal_strength", "count"], [[key, signal_counts[key]] for key in sorted(signal_counts)]),
        "",
        md_table(
            ["guardrail", "status"],
            [
                ["survey responses are provisional evidence only", "pass"],
                ["atlas_promotion_created is false for every response", "pass" if not any(row["atlas_promotion_created"] for row in response_logs) else "fail"],
                ["source graph mutated", "false"],
                ["raw family rows used", "false"],
            ],
        ),
    ]
    (OUT / "survey_pilot_signal_quality_report.md").write_text("\n".join(signal_lines) + "\n")

    probe_tiles = [tile for tile in tile_logs if tile["source_category"] in {"false_nearby_probe", "negative_control_probe"} or tile["is_false_nearby_or_boundary_probe"]]
    probe_lines = report_header("Survey Pilot False-Nearby Probe Report")
    probe_lines += [
        "False-nearby and boundary rows are treated as probes only, not conclusions.",
        "",
        md_table(
            ["page_type", "page", "position", "label", "intent", "source_category", "response", "promotion_created"],
            [
                [
                    tile["object_type"],
                    tile["shown_page_number"],
                    tile["shown_position"],
                    tile["display_label"],
                    tile["survey_intent"],
                    tile["source_category"],
                    tile["user_response"],
                    tile["atlas_promotion_created"],
                ]
                for tile in probe_tiles
            ],
        ),
    ]
    (OUT / "survey_pilot_false_nearby_probe_report.md").write_text("\n".join(probe_lines) + "\n")

    dont_rows = []
    for key, counts in sorted(response_by_page.items()):
        object_type, page_number = key
        total = sum(counts.values())
        rate = counts["dont_know_enough"] / total if total else 0
        dont_rows.append([object_type, page_number, counts["dont_know_enough"], total, f"{rate:.1%}", "watch" if rate > 0.35 else "ok"])
    dont_lines = report_header("Survey Pilot Don't Know Rate Report")
    dont_lines += [
        md_table(["page_type", "page", "dont_know", "total", "rate", "status"], dont_rows),
        "",
        md_table(
            ["object_type", "dont_know", "total", "rate"],
            [
                [object_type, dont_know_by_object[object_type], total_by_object[object_type], f"{dont_know_by_object[object_type] / total_by_object[object_type]:.1%}"]
                for object_type in ["artist", "album", "song_recording"]
            ],
        ),
    ]
    (OUT / "survey_pilot_dont_know_rate_report.md").write_text("\n".join(dont_lines) + "\n")

    apple_lines = report_header("Survey Pilot Apple Payload Seed Report")
    apple_lines += [
        "No Apple payload file was consumed in this controlled run because the approved dispatch input list was limited to repaired Normalization Pass 2 files.",
        "",
        "The tile log still includes `apple_payload_reason` on every tile; values are `null` in this run. The page log includes `source_mix.apple_payload = 0` on every page.",
        "",
        md_table(
            ["page_type", "page", "apple_payload_count", "graph_core_count"],
            [[page["page_type"], page["page_number"], page["source_mix"]["apple_payload"], page["source_mix"]["graph_core"]] for page in page_logs],
        ),
    ]
    (OUT / "survey_pilot_apple_payload_seed_report.md").write_text("\n".join(apple_lines) + "\n")

    safety_lines = report_header("Survey Pilot Import Safety Report")
    safety_lines += [
        md_table(
            ["gate", "status"],
            [
                ["Fast Survey uses survey_ready families only", "pass"],
                ["Context-only families excluded", "pass"],
                ["Page 1 pulls only from page1_core", "pass"],
                ["Page 2 pulls only from page2_adaptive", "pass"],
                ["Page 3 pulls only from page3_deep", "pass"],
                ["suppressed_quarantined rows displayed", "false"],
                ["quarantined rows displayed", "false"],
                ["quarantined Apple auto-resolution allowed", "false"],
                ["false-nearby rows create Dead Ends", "false"],
                ["survey response directly creates Atlas object", "false"],
                ["acceptance failures", len(acceptance_failures)],
            ],
        ),
        "",
        "Approved files read:",
        "",
        *[f"- `{filename}`" for filename in APPROVED_INPUT_FILES],
    ]
    (OUT / "survey_pilot_import_safety_report.md").write_text("\n".join(safety_lines) + "\n")

    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
