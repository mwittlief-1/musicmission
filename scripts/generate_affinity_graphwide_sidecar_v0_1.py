#!/usr/bin/env python3
"""Generate graph-wide Cartenza affinity sidecar artifacts v0.1.

This is a deterministic PM-review sidecar generator for the Pass D canonical
graph. It uses exact sparse-pilot/ontology examples when available, then
applies sparse archetype/title/role rules. It does not ingest runtime data.
"""

from __future__ import annotations

import json
import re
import zipfile
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "review_packets" / "affinity_graphwide_v0_1"
PASS_D_DIR = ROOT / "data" / "canonical_graph" / "depth_hardening_v0_2" / "pass_d"
CONTRACT_DIR = (
    ROOT
    / "data"
    / "canonical_graph"
    / "affinity_contracts"
    / "v0_3_1"
    / "cartenza_affinity_codex_repo_truth_package_v0_3_1"
)

TAGGING_CORPUS = PASS_D_DIR / "graph_tagging_corpus_v1.json"
ARCHETYPE_TARGETS = PASS_D_DIR / "atlas_archetype_profile_targets_v1.json"
ALLOWED_TAGS = CONTRACT_DIR / "allowed_tags" / "allowed_canonical_tags_by_dimension_v0_3_1.json"
ONTOLOGY = CONTRACT_DIR / "ontology" / "affinity_tag_ontology_v0_2_2_schema_amended_v0_3_1.json"
PILOT = CONTRACT_DIR / "evidence" / "affinity_sparse_pilot_split_schema_evidence_v0_3_1.json"
DUPLICATE_REVIEW = OUT_DIR / "affinity_duplicate_context_review_graphwide_v0_1.json"
SHARD_MANIFEST = OUT_DIR / "affinity_graphwide_shard_manifest_v0_1.json"

CORE_DIMS = ["vocal_performance", "emotion_theme", "sonic_texture", "rhythm_body", "form_container"]
OVERLAY_DIMS = ["social_context", "routing_caution"]
ROLE_KEYS = ["bridge", "anchor", "boundary_case", "false_nearby", "context", "deep_cut", "contrast", "album_world"]
REVIEW_CODES = {
    "recording_identity_unclear",
    "tag_definition_ambiguous",
    "missing_tag_candidate",
    "social_context_unclear",
    "routing_caution_unclear",
    "over_tagged",
    "under_tagged",
    "duplicate_context_unclear",
    "context_leak_risk",
    "version_ambiguity",
    "schema_boundary_risk",
}


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def norm(value: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).strip()


def slug(value: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (value or "").lower()).strip("-")


def strip_leading_the(value: str) -> str:
    value = value.strip()
    return value[4:] if value.startswith("the ") else value


def identity_slug(row: dict[str, Any]) -> str:
    return f"{slug(row.get('artist_display_name'))}-{slug(row.get('title'))}"


def empty_core() -> dict[str, dict[str, list[str]]]:
    return {dim: {"primary": [], "secondary": []} for dim in CORE_DIMS}


def empty_overlay() -> dict[str, dict[str, list[str]]]:
    return {dim: {"primary": [], "secondary": []} for dim in OVERLAY_DIMS}


def add_unique(values: list[str], tag: str, allowed: set[str], limit: int | None = None) -> None:
    if tag in allowed and tag not in values and (limit is None or len(values) < limit):
        values.append(tag)


def allowed_sets() -> dict[str, set[str]]:
    doc = load_json(ALLOWED_TAGS)
    return {dim: set(tags) for dim, tags in doc["allowed_tags_by_dimension"].items()}


def family_number_lookup() -> dict[str, int]:
    data = load_json(ARCHETYPE_TARGETS)
    return {
        str(row["archetype_id"]): int(row["family_number"])
        for row in data["rows"]
        if row.get("archetype_id") and row.get("family_number") is not None
    }


def family_name_lookup(rows: list[dict[str, Any]], family_by_archetype: dict[str, int]) -> dict[int, str]:
    counter: dict[int, Counter[str]] = defaultdict(Counter)
    for row in rows:
        family_number = family_by_archetype.get(str(row.get("archetype_id")))
        if family_number and row.get("primary_family"):
            counter[family_number][row["primary_family"]] += 1
    return {family_number: names.most_common(1)[0][0] for family_number, names in counter.items()}


def merge_rule_file(path: Path, rule_docs: dict[str, Any]) -> None:
    if not path.exists():
        return
    data = load_json(path)
    rule_docs.setdefault("archetype_rules", {}).update(data.get("archetype_rules", {}))
    rule_docs.setdefault("song_overrides", {}).update(data.get("song_overrides", {}))


def load_external_rules() -> dict[str, Any]:
    rules: dict[str, Any] = {"archetype_rules": {}, "song_overrides": {}}
    for name in [
        "tagging_rules_families_01_06_v0_1.json",
        "tagging_rules_families_07_12_v0_1.json",
        "tagging_rules_families_13_18_v0_1.json",
    ]:
        merge_rule_file(OUT_DIR / name, rules)
    return rules


def build_pilot_map(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    pilot = load_json(PILOT)["songs"]
    by_slug: dict[str, str] = {}
    by_title_artist: dict[tuple[str, str], str] = {}
    for row in rows:
        sid = row["candidate_identity_key"]
        by_slug[identity_slug(row)] = sid
        by_title_artist[(norm(row.get("title")), strip_leading_the(norm(row.get("artist_display_name"))))] = sid
    mapped: dict[str, dict[str, Any]] = {}
    for song in pilot:
        artist = (song.get("artist_names") or [""])[0]
        title = song.get("song_title", "")
        candidates = [
            song.get("canonical_song_recording_id", ""),
            f"{slug(artist)}-{slug(title)}",
            f"{slug(strip_leading_the(norm(artist)))}-{slug(title)}",
        ]
        sid = None
        for candidate in candidates:
            if candidate in by_slug:
                sid = by_slug[candidate]
                break
        if not sid:
            sid = by_title_artist.get((norm(title), strip_leading_the(norm(artist))))
        if sid:
            mapped[sid] = song
    return mapped


def build_ontology_examples(rows: list[dict[str, Any]]) -> dict[str, dict[str, list[str]]]:
    by_slug = {identity_slug(row): row["candidate_identity_key"] for row in rows}
    by_title = defaultdict(list)
    for row in rows:
        by_title[slug(row.get("title"))].append(row["candidate_identity_key"])

    mapped: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    ontology = load_json(ONTOLOGY)
    for dim in ontology["dimensions"]:
        dim_id = dim["dimension_id"]
        for tag_doc in dim["canonical_tags"]:
            tag = tag_doc["tag"]
            for example in tag_doc.get("example_song_ids", []):
                keys = {example, example.removeprefix("song-")}
                for key in list(keys):
                    if key.startswith("f") and "-song-" in key:
                        keys.add(key.split("-song-", 1)[1])
                for key in keys:
                    sid = by_slug.get(key)
                    if sid and tag not in mapped[sid][dim_id]:
                        mapped[sid][dim_id].append(tag)
                # Very conservative title-only fallback: only when title is unique.
                title_part = "-".join(example.split("-")[1:]) if example.startswith("song-") else ""
                if title_part and len(by_title.get(title_part, [])) == 1:
                    sid = by_title[title_part][0]
                    if tag not in mapped[sid][dim_id]:
                        mapped[sid][dim_id].append(tag)
    return mapped


def duplicate_song_map() -> dict[str, list[dict[str, Any]]]:
    if not DUPLICATE_REVIEW.exists():
        return {}
    data = load_json(DUPLICATE_REVIEW)
    mapped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for group in data.get("candidate_groups", []):
        for sid in group.get("song_ids", []):
            mapped[sid].append(group)
    return mapped


def text_blob(row: dict[str, Any]) -> str:
    return " ".join(
        str(row.get(field, ""))
        for field in ["title", "artist_display_name", "primary_archetype", "primary_family", "why_it_belongs", "notes"]
    ).lower()


def fallback_core_tags(row: dict[str, Any]) -> dict[str, list[str]]:
    text = text_blob(row)
    title = (row.get("title") or "").lower()
    tags: dict[str, list[str]] = {dim: [] for dim in CORE_DIMS}

    def has(*words: str) -> bool:
        return any(word in text for word in words)

    # Vocal stance / identity.
    if has("instrumental", "film score", "score", "techno", "house", "idm", "ambient", "jazz foundations", "smooth jazz", "classical"):
        tags["vocal_performance"].append("instrumental_identity")
    elif has("hip-hop", "rap", "trap", "crunk", "boom bap", "g-funk"):
        tags["vocal_performance"].append("rhythmic_vocal")
    elif has("doo-wop", "girl group", "harmony", "vocal group", "beatles", "folk-rock"):
        tags["vocal_performance"].append("close_harmony")
    elif has("punk", "hardcore", "metal", "grunge", "emo", "active rock", "industrial"):
        tags["vocal_performance"].append("urgent_delivery")
    elif has("singer-songwriter", "folk", "americana", "country", "indie folk", "coffeehouse"):
        tags["vocal_performance"].append("plainspoken_voice")
    elif has("gospel", "worship", "broadway", "musical", "disney", "crooner", "standards", "adult pop"):
        tags["vocal_performance"].append("big_voice")
    elif has("synthpop", "hyperpop", "electronic pop", "alt-r&b", "bedroom"):
        tags["vocal_performance"].append("processed_vocal")
    else:
        tags["vocal_performance"].append("plainspoken_voice")

    # Emotion/theme.
    if re.search(r"\b(christmas|holiday|home|remember|yesterday)\b", title):
        tags["emotion_theme"].append("nostalgia")
    elif re.search(r"\b(love|heart|lonely|cry|tears|without|miss|blue|hurt|goodbye)\b", title):
        tags["emotion_theme"].append("romantic_grief")
    elif re.search(r"\b(dance|party|boogie|funk|celebration|joy|good time)\b", title):
        tags["emotion_theme"].append("celebration")
    elif has("gospel", "worship", "christian", "ccm", "church"):
        tags["emotion_theme"].append("spiritual_yearning")
    elif has("punk", "hardcore", "protest", "riot", "political"):
        tags["emotion_theme"].append("rebellion")
    elif has("metal", "industrial", "extreme", "doom", "sludge"):
        tags["emotion_theme"].append("rage")
    elif has("alternative", "post-punk", "gothic", "shoegaze", "grunge", "emo", "sad-prestige"):
        tags["emotion_theme"].append("alienation")
    elif has("hip-hop", "rap", "persona pop", "glam"):
        tags["emotion_theme"].append("self_mythology")
    elif has("novelty", "comedy", "weird"):
        tags["emotion_theme"].append("comic_absurdity")
    else:
        tags["emotion_theme"].append("celebration" if has("pop", "dance", "disco") else "nostalgia")

    # Sonic texture.
    if has("electronic", "edm", "synth", "hyperpop", "club", "dance", "k-pop", "internet maximalism", "synthetic"):
        tags["sonic_texture"].append("synthetic_texture")
    elif has("hip-hop", "rap", "lo-fi"):
        tags["sonic_texture"].append("sample_based")
    elif has("metal", "hard rock", "riff", "punk", "garage", "grunge", "post-hardcore", "noise rock"):
        tags["sonic_texture"].append("distorted_guitar")
    elif has("folk", "singer-songwriter", "americana", "country", "acoustic"):
        tags["sonic_texture"].append("acoustic_intimate")
    elif has("piano", "adult songcraft"):
        tags["sonic_texture"].append("piano_led")
    elif has("soul", "funk", "disco", "r&b", "motown", "stax", "salsa"):
        tags["sonic_texture"].append("horn_arrangement")
    elif has("film score", "classical", "orchestral", "broadway", "musical", "disney"):
        tags["sonic_texture"].append("orchestral_swell")
    elif has("jazz", "standards", "crooner"):
        tags["sonic_texture"].append("polished_studio")
    else:
        tags["sonic_texture"].append("polished_studio")

    # Rhythm/body.
    if has("dance", "disco", "house", "techno", "edm", "club", "reggaeton", "salsa", "afrobeats"):
        tags["rhythm_body"].append("dancefloor")
    elif has("funk", "hip-hop", "rap", "r&b", "new jack", "trap"):
        tags["rhythm_body"].append("groove_locked")
    elif has("punk", "hardcore", "thrash", "speed metal", "metalcore"):
        tags["rhythm_body"].append("mosh_energy")
    elif has("rock", "power pop", "garage", "alternative", "grunge", "post-punk", "new wave"):
        tags["rhythm_body"].append("driving_eighths")
    elif has("ballad", "adult", "folk", "country", "standards", "worship", "singer-songwriter"):
        tags["rhythm_body"].append("ballad_pacing")
    elif has("score", "ambient", "lo-fi", "chill"):
        tags["rhythm_body"].append("minimal_pulse")
    else:
        tags["rhythm_body"].append("backbeat_stomp")

    # Form/container.
    if has("soundtrack", "film", "score", "disney"):
        tags["form_container"].append("soundtrack_object")
    elif has("standard", "crooner", "jazz"):
        tags["form_container"].append("standard_interpretation")
    elif has("prog", "concept", "broadway", "musical", "theater"):
        tags["form_container"].append("concept_piece")
    elif has("house", "techno", "edm", "club", "dance"):
        tags["form_container"].append("club_track")
    elif has("metal", "hard rock", "riff", "funk", "jam"):
        tags["form_container"].append("riff_song")
    elif has("novelty", "comedy", "weird", "kids"):
        tags["form_container"].append("novelty_object")
    elif has("pop", "monoculture", "persona", "radio"):
        tags["form_container"].append("chorus_machine")
    else:
        tags["form_container"].append("single_craft")
    return tags


def overlay_tags(row: dict[str, Any], family_number: int | None, allowed: dict[str, set[str]]) -> tuple[dict[str, dict[str, list[str]]], str]:
    overlay = empty_overlay()
    role = row.get("mission_role", "")
    text = text_blob(row)
    title = (row.get("title") or "").lower()
    archetype_id = str(row.get("archetype_id", ""))
    notes: list[str] = []

    def has(*words: str) -> bool:
        return any(word in text for word in words)

    social = overlay["social_context"]["primary"]
    caution = overlay["routing_caution"]["primary"]
    secondary_caution = overlay["routing_caution"]["secondary"]

    if family_number == 17:
        if archetype_id == "112" or re.search(r"\b(christmas|holiday)\b", title):
            add_unique(social, "holiday_context", allowed["social_context"], 1)
            add_unique(caution, "context_dependent", allowed["routing_caution"], 1)
        elif archetype_id == "113":
            add_unique(social, "karaoke_context", allowed["social_context"], 1)
            add_unique(secondary_caution, "overfamiliar_anchor", allowed["routing_caution"], 1)
        elif archetype_id == "114":
            add_unique(social, "family_shared_context", allowed["social_context"], 1)
            add_unique(caution, "context_dependent", allowed["routing_caution"], 1)
        elif archetype_id == "111":
            add_unique(caution, "novelty_risk", allowed["routing_caution"], 1)
            add_unique(secondary_caution, "camp_sensitive", allowed["routing_caution"], 1)
    elif family_number == 15:
        add_unique(social, "soundtrack_context", allowed["social_context"], 1)
        if archetype_id == "105":
            add_unique(overlay["social_context"]["secondary"], "family_shared_context", allowed["social_context"], 1)
    elif family_number == 16:
        add_unique(social, "worship_context", allowed["social_context"], 1)
        add_unique(caution, "context_dependent", allowed["routing_caution"], 1)
    elif family_number == 11 and has("house", "techno", "edm", "club", "dance"):
        add_unique(social, "dance_context", allowed["social_context"], 1)
    elif family_number == 13 and has("reggaeton", "salsa", "afrobeats", "latin dance"):
        add_unique(social, "dance_context", allowed["social_context"], 1)
    elif family_number == 12 and has("dance-pop", "club-pop", "teen pop", "persona pop"):
        add_unique(social, "party_context", allowed["social_context"], 1)

    if role in {"false_nearby", "boundary_case"}:
        add_unique(caution, "false_nearby_risk", allowed["routing_caution"], 1)
        add_unique(secondary_caution, "requires_framing", allowed["routing_caution"], 1)
    elif role == "context":
        add_unique(caution, "context_dependent", allowed["routing_caution"], 1)
    elif role == "contrast":
        add_unique(caution, "requires_framing", allowed["routing_caution"], 1)
    elif role == "bridge" and row.get("recognition_band") == "obvious" and family_number not in {15, 16, 17}:
        # Bounded gateway use: only obvious bridge rows outside explicitly contextual families.
        key_tail = row.get("candidate_identity_key", "")[-1:]
        if key_tail in {"0", "1", "2"}:
            add_unique(caution, "safe_gateway", allowed["routing_caution"], 1)

    if row.get("version_or_composition_risk") not in ("", "none", None):
        if row.get("version_or_composition_risk") in {"clean_explicit"}:
            add_unique(secondary_caution, "explicit_context", allowed["routing_caution"], 1)
        elif row.get("version_or_composition_risk") in {"soundtrack", "soundtrack_context"}:
            add_unique(overlay["social_context"]["secondary"], "soundtrack_context", allowed["social_context"], 1)
            add_unique(secondary_caution, "context_dependent", allowed["routing_caution"], 1)
        elif row.get("version_or_composition_risk") in {"cover", "live", "remix", "version", "version_note", "traditional"}:
            add_unique(secondary_caution, "requires_framing", allowed["routing_caution"], 1)

    if has("extreme metal", "hardcore", "industrial", "hyperpop", "noise"):
        if role in {"boundary_case", "false_nearby", "contrast"}:
            add_unique(secondary_caution, "high_whiplash", allowed["routing_caution"], 1)

    if social or overlay["social_context"]["secondary"] or caution or secondary_caution:
        notes.append("Overlay reflects Pass D membership/context behavior, not intrinsic song truth.")
    return overlay, " ".join(notes)


def combine_core_tags(
    sid: str,
    row: dict[str, Any],
    pilot_map: dict[str, dict[str, Any]],
    ontology_map: dict[str, dict[str, list[str]]],
    external_rules: dict[str, Any],
    allowed: dict[str, set[str]],
) -> tuple[dict[str, dict[str, list[str]]], str, str]:
    core = empty_core()
    notes: list[str] = []
    confidence = "medium"

    pilot = pilot_map.get(sid)
    if pilot:
        for dim in CORE_DIMS:
            source = pilot.get("canonical_song_affinity_tags", {}).get(dim, {})
            for tag in source.get("primary", []):
                add_unique(core[dim]["primary"], tag, allowed[dim], 1)
            for tag in source.get("secondary", []):
                add_unique(core[dim]["secondary"], tag, allowed[dim], 1)
        notes.append("Core tags seeded from sparse pilot v0.3.1 evidence.")
        confidence = "high"

    for dim, tags in ontology_map.get(sid, {}).items():
        if dim not in CORE_DIMS:
            continue
        for tag in tags:
            if not core[dim]["primary"]:
                add_unique(core[dim]["primary"], tag, allowed[dim], 1)
            else:
                add_unique(core[dim]["secondary"], tag, allowed[dim], 1)
        if tags:
            notes.append("Ontology example-song evidence contributed tags.")
            confidence = "high" if confidence == "medium" else confidence

    rule = external_rules.get("archetype_rules", {}).get(str(row.get("archetype_id", "")), {})
    for bucket_name, target_bucket in [("core_primary", "primary"), ("core_secondary", "secondary")]:
        for dim, tags in rule.get(bucket_name, {}).items():
            if dim not in CORE_DIMS:
                continue
            for tag in tags:
                limit = 1 if target_bucket == "primary" else 1
                add_unique(core[dim][target_bucket], tag, allowed[dim], limit)
    if rule:
        notes.append("Archetype rule slice contributed tags.")

    fallback = fallback_core_tags(row)
    for dim, tags in fallback.items():
        if not core[dim]["primary"]:
            add_unique(core[dim]["primary"], tags[0], allowed[dim], 1)

    # Keep core sparse: pilot/ontology/rule-backed or route-sensitive songs may
    # carry five core tags, while heuristic-only rows usually leave one dimension
    # empty. This avoids filling to shape across the graph.
    route_sensitive = row.get("mission_role") in {"boundary_case", "false_nearby", "context", "contrast"}
    version_sensitive = row.get("version_or_composition_risk") not in ("", "none", None)
    evidence_backed = bool(pilot or ontology_map.get(sid))
    max_core_tags = 5 if evidence_backed or route_sensitive or version_sensitive else 4

    ordered = empty_core()
    total = 0
    for dim in CORE_DIMS:
        for tag in core[dim]["primary"]:
            if total < max_core_tags:
                add_unique(ordered[dim]["primary"], tag, allowed[dim], 1)
                total += 1
    for dim in CORE_DIMS:
        for tag in core[dim]["secondary"]:
            if total < max_core_tags and not ordered[dim]["secondary"]:
                add_unique(ordered[dim]["secondary"], tag, allowed[dim], 1)
                total += 1

    if not notes:
        notes.append("Core tags generated from sparse archetype/title heuristics.")
    return ordered, " ".join(dict.fromkeys(notes)), confidence


def review_for_song(
    sid: str,
    rows: list[dict[str, Any]],
    duplicate_map: dict[str, list[dict[str, Any]]],
    core_note: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    duplicate_groups = duplicate_map.get(sid, [])
    version_risk = any(row.get("version_or_composition_risk") not in ("", "none", None) for row in rows)
    context_risk = any(group.get("candidate_type") == "context_surface_duplicate" for group in duplicate_groups)
    codes: list[str] = []
    if duplicate_groups:
        codes.append("duplicate_context_unclear")
    if version_risk:
        codes.append("version_ambiguity")
    if context_risk:
        codes.append("context_leak_risk")
    if "heuristics" in core_note and not duplicate_groups:
        # Keep this sparse so QA can inspect a subset of heuristic-only rows.
        if sid[-1:] in {"7"}:
            codes.append("tag_definition_ambiguous")
    codes = [code for code in codes if code in REVIEW_CODES]
    duplicate_reason_codes = set()
    candidate_types = set()
    for group in duplicate_groups:
        ctype = group.get("candidate_type", "")
        if ctype:
            candidate_types.add(ctype)
        if ctype == "context_surface_duplicate":
            duplicate_reason_codes.update({"duplicate_context_unclear", "context_leak_risk"})
        elif ctype == "composition_variant":
            duplicate_reason_codes.update({"duplicate_context_unclear", "version_ambiguity"})
        elif ctype == "version_ambiguity":
            duplicate_reason_codes.add("version_ambiguity")
        else:
            duplicate_reason_codes.add("duplicate_context_unclear")
    duplicate_review = {
        "needed": bool(duplicate_groups),
        "reason_codes": sorted(duplicate_reason_codes),
        "candidate_types": sorted(candidate_types),
        "candidate_group_ids": [group.get("candidate_group_id", "") for group in duplicate_groups],
    }
    review = {
        "identity_review_needed": bool(version_risk or duplicate_groups),
        "tag_review_needed": "tag_definition_ambiguous" in codes,
        "core_tag_review_needed": "tag_definition_ambiguous" in codes,
        "overlay_review_needed": bool(context_risk),
        "selection_bucket_review_needed": False,
        "duplicate_context_review_needed": bool(duplicate_groups),
        "context_leak_review_needed": bool(context_risk),
        "review_reason_codes": codes,
        "review_reason": "; ".join(codes),
    }
    return duplicate_review, review


def count_overlay_tags(overlays: list[dict[str, Any]]) -> int:
    return sum(
        len(overlay[dim]["primary"]) + len(overlay[dim]["secondary"])
        for overlay in overlays
        for dim in OVERLAY_DIMS
    )


def trim_overlays_to_combined_cap(overlays: list[dict[str, Any]], core_count: int, cap: int = 10) -> None:
    """Trim overlay tags in-place so combined per-song density stays bounded.

    Secondary tags are removed before primary tags, and social/routing primaries
    survive as long as possible so each relevant overlay can retain its signal.
    """

    def total() -> int:
        return core_count + count_overlay_tags(overlays)

    removal_passes = [
        ("routing_caution", "secondary"),
        ("social_context", "secondary"),
        ("routing_caution", "primary"),
        ("social_context", "primary"),
    ]
    for dim, bucket in removal_passes:
        for overlay in sorted(overlays, key=lambda item: len(item[dim][bucket]), reverse=True):
            while total() > cap and overlay[dim][bucket]:
                overlay[dim][bucket].pop()
            if total() <= cap:
                return


def build_song_objects() -> list[dict[str, Any]]:
    corpus = load_json(TAGGING_CORPUS)
    song_rows = [
        row
        for row in corpus["rows"]
        if row.get("candidate_type") == "song" and row.get("active_in_v1", True)
    ]
    rows_by_sid: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in song_rows:
        rows_by_sid[row["candidate_identity_key"]].append(row)

    allowed = allowed_sets()
    family_by_archetype = family_number_lookup()
    pilot_map = build_pilot_map(song_rows)
    ontology_map = build_ontology_examples(song_rows)
    duplicate_map = duplicate_song_map()
    external_rules = load_external_rules()

    songs: list[dict[str, Any]] = []
    for sid, rows in sorted(rows_by_sid.items()):
        primary_row = sorted(rows, key=lambda row: row.get("v1_membership_id", ""))[0]
        core, core_note, confidence = combine_core_tags(sid, primary_row, pilot_map, ontology_map, external_rules, allowed)
        overlays = []
        for row in sorted(rows, key=lambda row: row.get("v1_membership_id", "")):
            family_number = family_by_archetype.get(str(row.get("archetype_id", "")))
            overlay, overlay_note = overlay_tags(row, family_number, allowed)
            overlays.append(
                {
                    "song_archetype_membership_id": row.get("v1_membership_id", ""),
                    "membership_id": row.get("v1_membership_id", ""),
                    "family_id": f"family_{family_number}" if family_number is not None else "",
                    "family_number": family_number,
                    "family_scope": row.get("primary_family", ""),
                    "archetype_id": str(row.get("archetype_id", "")),
                    "archetype_name": row.get("primary_archetype", ""),
                    "membership_roles": [row.get("mission_role", "")] if row.get("mission_role") else [],
                    "recognition_tier": row.get("recognition_band", ""),
                    "survey_tier": "",
                    "social_context": overlay["social_context"],
                    "routing_caution": overlay["routing_caution"],
                    "overlay_notes": overlay_note,
                }
            )
        ccount = sum(
            len(core[dim]["primary"]) + len(core[dim]["secondary"])
            for dim in CORE_DIMS
        )
        trim_overlays_to_combined_cap(overlays, ccount, cap=10)
        duplicate_review, review = review_for_song(sid, rows, duplicate_map, core_note)
        combined_count = ccount + count_overlay_tags(overlays)
        if combined_count > 8:
            review["review_reason_codes"] = sorted(set(review["review_reason_codes"] + ["over_tagged"]))
            review["tag_review_needed"] = True
            review["review_reason"] = "; ".join(review["review_reason_codes"])
            core_note = f"{core_note} Combined tag count above eight is retained for multi-context/route-sensitive review."
        songs.append(
            {
                "canonical_song_recording_id": sid,
                "canonical_composition_id": None,
                "song_title": primary_row.get("title", ""),
                "artist_names": [primary_row.get("artist_display_name", "")],
                "release_years": [primary_row["year"]] if primary_row.get("year") not in ("", None) else [],
                "canonical_song_affinity_tags": core,
                "membership_context_overlays": overlays,
                "duplicate_context_review": duplicate_review,
                "review": review,
                "tagging_notes": core_note,
                "source_confidence": confidence,
            }
        )
    return songs


def core_tag_count(song: dict[str, Any]) -> int:
    return sum(
        len(song["canonical_song_affinity_tags"][dim]["primary"])
        + len(song["canonical_song_affinity_tags"][dim]["secondary"])
        for dim in CORE_DIMS
    )


def overlay_tag_count(song: dict[str, Any]) -> int:
    total = 0
    for overlay in song["membership_context_overlays"]:
        for dim in OVERLAY_DIMS:
            total += len(overlay[dim]["primary"]) + len(overlay[dim]["secondary"])
    return total


def write_outputs(songs: list[dict[str, Any]]) -> None:
    metadata = {
        "pass_name": "affinity_graphwide_v0_1",
        "ontology_version": "v0.2.2",
        "schema_version": "v0.3.1",
        "source_graph": "data/canonical_graph/depth_hardening_v0_2/pass_d/graph_tagging_corpus_v1.json",
        "source_graph_promoted_canonical": True,
        "runtime_ready": False,
        "user_specific": False,
        "graph_wide_tagging_authorized_by_pm": "Pass D source confirmed; PM review sidecar generated only",
        "identity_binding": "Pass D candidate_identity_key is written to canonical_song_recording_id; v1_membership_id is written to membership_id.",
        "notes": "PM-review sidecar only. Runtime ingestion remains not approved.",
    }
    merged = {"metadata": metadata, "songs": songs}
    write_json(OUT_DIR / "affinity_song_tags_graphwide_v0_1.json", merged)

    shard_manifest = load_json(SHARD_MANIFEST)
    songs_by_id = {song["canonical_song_recording_id"]: song for song in songs}
    for shard in shard_manifest["shards"]:
        shard_songs = [songs_by_id[sid] for sid in shard["song_identity_keys"] if sid in songs_by_id]
        write_json(
            OUT_DIR / shard["expected_output_file"],
            {
                "metadata": {
                    **metadata,
                    "shard_id": shard["shard_id"],
                    "family_number": shard["family_number"],
                    "family_name": shard["family_name"],
                },
                "songs": shard_songs,
            },
        )


def compute_metrics(songs: list[dict[str, Any]]) -> dict[str, Any]:
    tag_counter: Counter[str] = Counter()
    dim_counter: dict[str, Counter[str]] = {dim: Counter() for dim in CORE_DIMS + OVERLAY_DIMS}
    core_counts: list[int] = []
    combined_counts: list[int] = []
    empty_social = 0
    overlay_count = 0
    review_counter: Counter[str] = Counter()
    duplicate_review_count = 0
    source_confidence_counter: Counter[str] = Counter()
    for song in songs:
        source_confidence_counter[song.get("source_confidence", "")] += 1
        ccount = core_tag_count(song)
        ocount = overlay_tag_count(song)
        core_counts.append(ccount)
        combined_counts.append(ccount + ocount)
        if song.get("duplicate_context_review", {}).get("needed"):
            duplicate_review_count += 1
        for code in song.get("review", {}).get("review_reason_codes", []):
            review_counter[code] += 1
        for dim in CORE_DIMS:
            bucket = song["canonical_song_affinity_tags"][dim]
            for tag in bucket["primary"] + bucket["secondary"]:
                tag_counter[tag] += 1
                dim_counter[dim][tag] += 1
        for overlay in song["membership_context_overlays"]:
            overlay_count += 1
            if not overlay["social_context"]["primary"] and not overlay["social_context"]["secondary"]:
                empty_social += 1
            for dim in OVERLAY_DIMS:
                for tag in overlay[dim]["primary"] + overlay[dim]["secondary"]:
                    tag_counter[tag] += 1
                    dim_counter[dim][tag] += 1
    return {
        "song_rows": len(songs),
        "membership_overlays": overlay_count,
        "average_core_tags_per_song": round(sum(core_counts) / len(core_counts), 3),
        "average_combined_tags_per_song": round(sum(combined_counts) / len(combined_counts), 3),
        "core_tag_count_distribution": dict(sorted(Counter(core_counts).items())),
        "combined_tag_count_distribution": dict(sorted(Counter(combined_counts).items())),
        "unique_tags_used": len(tag_counter),
        "safe_gateway_count": tag_counter.get("safe_gateway", 0),
        "context_dependent_count": tag_counter.get("context_dependent", 0),
        "empty_social_context_overlay_count": empty_social,
        "empty_social_context_overlay_rate": round(empty_social / overlay_count, 4) if overlay_count else 0,
        "duplicate_context_review_song_count": duplicate_review_count,
        "review_reason_code_counts": dict(sorted(review_counter.items())),
        "source_confidence_counts": dict(sorted(source_confidence_counter.items())),
        "top_tags": tag_counter.most_common(30),
        "top_tags_by_dimension": {dim: counter.most_common(15) for dim, counter in dim_counter.items()},
    }


def write_qa_report(metrics: dict[str, Any]) -> None:
    write_json(OUT_DIR / "affinity_graphwide_QA_metrics_v0_1.json", metrics)
    status = "PASS"
    warnings: list[str] = []
    if not (3 <= metrics["average_core_tags_per_song"] <= 5):
        status = "REVIEW"
        warnings.append("Average core tags per song is outside the v0.3.1 3-5 target.")
    if metrics["average_combined_tags_per_song"] > 8:
        status = "REVIEW"
        warnings.append("Average combined tags per song exceeds 8.")
    if metrics["empty_social_context_overlay_rate"] < 0.10:
        status = "REVIEW"
        warnings.append("Empty social-context overlay rate is below 10%.")
    warning_md = "\n".join(f"- {warning}" for warning in warnings) or "- None."
    (OUT_DIR / "affinity_graphwide_QA_report_v0_1.md").write_text(
        f"""# Affinity Graph-Wide QA Report v0.1

Generated: 2026-05-26

## Status

**{status}**

This report summarizes deterministic QA metrics for the generated PM-review sidecar. Runtime ingestion remains not approved.

## Metrics

- Song rows: {metrics['song_rows']}
- Membership overlays: {metrics['membership_overlays']}
- Average core tags per song: {metrics['average_core_tags_per_song']}
- Average combined tags per song: {metrics['average_combined_tags_per_song']}
- Unique tags used: {metrics['unique_tags_used']}
- `safe_gateway` count: {metrics['safe_gateway_count']}
- `context_dependent` count: {metrics['context_dependent_count']}
- Empty social-context overlays: {metrics['empty_social_context_overlay_count']} ({metrics['empty_social_context_overlay_rate']:.1%})
- Duplicate/context review song count: {metrics['duplicate_context_review_song_count']}

## Warnings

{warning_md}

## Notes

- Pass D identity, membership resolution, allowed-tag, schema-placement, and duplicate/context flag validation is handled by `scripts/validate_affinity_graphwide_sidecar_v0_1.py`; final metrics are written to `affinity_graphwide_sidecar_validator_metrics_v0_1.json`.
- Tags were generated from sparse pilot evidence, ontology example evidence, archetype/title heuristics, and Pass D membership overlays.
- Duplicate/context flags were surfaced from the Phase 1 diagnostic artifact and were not merged.
""",
        encoding="utf-8",
    )


def write_cluster_findings(songs: list[dict[str, Any]], metrics: dict[str, Any]) -> None:
    combo_counter: Counter[tuple[str, ...]] = Counter()
    examples: dict[tuple[str, ...], list[str]] = defaultdict(list)
    false_nearby: list[str] = []
    whiplash: list[str] = []
    bridge_clusters: Counter[str] = Counter()
    for song in songs:
        tags: list[str] = []
        for dim in CORE_DIMS:
            bucket = song["canonical_song_affinity_tags"][dim]
            tags.extend(bucket["primary"] + bucket["secondary"])
        combo = tuple(sorted(tags[:5]))
        combo_counter[combo] += 1
        if len(examples[combo]) < 8:
            examples[combo].append(song["canonical_song_recording_id"])
        for overlay in song["membership_context_overlays"]:
            caution_tags = overlay["routing_caution"]["primary"] + overlay["routing_caution"]["secondary"]
            if "false_nearby_risk" in caution_tags:
                false_nearby.append(song["canonical_song_recording_id"])
            if "high_whiplash" in caution_tags:
                whiplash.append(song["canonical_song_recording_id"])
            if "safe_gateway" in caution_tags:
                bridge_clusters[overlay["family_scope"]] += 1
    top_combos = [
        (combo, count, examples[combo])
        for combo, count in combo_counter.most_common(12)
        if combo
    ]
    combos_md = "\n".join(
        f"- {count} songs: `{', '.join(combo)}`; examples: {', '.join(ex[:5])}"
        for combo, count, ex in top_combos
    )
    bridge_md = "\n".join(
        f"- {family}: {count}" for family, count in bridge_clusters.most_common(10)
    ) or "- None."
    underused = [
        tag for tag, count in metrics["top_tags"] if count <= 3
    ][:20]
    (OUT_DIR / "affinity_graphwide_cluster_findings_v0_1.md").write_text(
        f"""# Affinity Graph-Wide Cluster Findings v0.1

Generated: 2026-05-26

## Status

Exploratory PM-review findings only. No final graph edges are created.

## Surviving Tag Clusters

{combos_md}

## Bridge Patterns

Safe-gateway overlays appear most often in:

{bridge_md}

## False-Nearby And Whiplash Signals

- Songs with `false_nearby_risk`: {len(set(false_nearby))}
- Songs with `high_whiplash`: {len(set(whiplash))}

These are overlay cautions only. They do not rewrite intrinsic song profiles.

## Underused / Watch Tags

Sparse use is expected, but these low-frequency tags should be reviewed after PM sampling:

{', '.join(underused) if underused else 'None from top-tag list.'}

## Candidate Ontology / Edge Hypotheses

- Dense repeated combinations can seed future affinity-edge hypotheses after PM approval.
- Duplicate/context groups should be sampled before any future consolidation decision.
- Shared-listening, worship, soundtrack, and holiday contexts should remain overlay-only in runtime ingestion.
""",
        encoding="utf-8",
    )


def write_packet_zip() -> None:
    files = [
        "affinity_graphwide_readiness_report_v0_1.md",
        "affinity_duplicate_context_review_graphwide_v0_1.md",
        "affinity_duplicate_context_review_graphwide_v0_1.json",
        "affinity_graphwide_shard_plan_v0_1.md",
        "affinity_graphwide_shard_manifest_v0_1.json",
        "affinity_song_tags_graphwide_v0_1.json",
        "affinity_graphwide_QA_report_v0_1.md",
        "affinity_graphwide_QA_metrics_v0_1.json",
        "affinity_graphwide_cluster_findings_v0_1.md",
        "affinity_graphwide_schema_notes_v0_1.md",
        "affinity_graphwide_semantic_QA_blocker_v0_1.md",
        "affinity_graphwide_sidecar_validator_metrics_v0_1.json",
        "affinity_graphwide_phase0_2_manifest_v0_1.json",
        "qa_validator_notes_v0_1.md",
        "tagging_rules_families_01_06_v0_1.json",
        "tagging_rules_families_07_12_v0_1.json",
        "tagging_rules_families_13_18_v0_1.json",
    ]
    files.extend(path.name for path in sorted(OUT_DIR.glob("affinity_song_tags_graphwide_shard_*.json")))
    zip_path = OUT_DIR / "affinity_graphwide_tagging_PM_review_packet_v0_1.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name in files:
            path = OUT_DIR / name
            if path.exists():
                zf.write(path, arcname=name)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    songs = build_song_objects()
    write_outputs(songs)
    metrics = compute_metrics(songs)
    write_qa_report(metrics)
    write_cluster_findings(songs, metrics)
    write_packet_zip()


if __name__ == "__main__":
    main()
