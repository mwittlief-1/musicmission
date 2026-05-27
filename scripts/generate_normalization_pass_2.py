#!/usr/bin/env python3
"""Generate Waymark Canonical Graph Normalization Pass 2 artifacts."""

from __future__ import annotations

import json
import re
import subprocess
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CG = ROOT / "data" / "canonical_graph"
DRY = CG / "import_dry_run"
OUT = CG / "normalization_pass_2"
TODAY = date.today().isoformat()

F2_ARCHETYPES = {
    "008": "British Invasion / Core UK Beat Groups",
    "009": "Jangle Pop / Folk-Rock Precursor",
    "010": "Folk-Rock / Harmony Pop / 60s Songcraft",
    "011": "Garage Rock / Nuggets / Proto-Punk Singles",
    "012": "Baroque Pop / Chamber Pop / Artful 60s Pop",
    "013": "Psychedelic Pop / Sunshine Pop / Late-60s Pop-Rock",
    "014": "Heavy Psych / Blues-Rock / Acid Rock",
    "015": "Art-Rock / Proto-Alternative / Freak Underground",
}

TIER_SCORE = {"core": 100, "standard": 70, "edge": 42, "suppress": 0}
REC_SCORE = {"mass": 100, "high": 82, "medium": 55, "low": 25, "cult": 18}

VERSION_RE = re.compile(
    r"cover|version|recording|remix|mix|live|source|original|clean|explicit|"
    r"traditional|standard|cast|score|soundtrack|composition|arrangement|hymn|"
    r"church|songbook|credit|alias|collaboration",
    re.I,
)

SPECIAL_ENTITY_ARTIST_IDS = {
    "alan-menken",
    "alan-silvestri",
    "bethel-music",
    "darlene-zschech",
    "elevation-worship",
    "hans-zimmer",
    "hillsong-united",
    "hillsong-worship",
    "john-williams",
    "keith-and-kristyn-getty",
    "london-philharmonic-orchestra",
    "ludwig-goransson",
    "maverick-city-music",
    "passion",
    "pat-barrett",
    "sinach",
    "yo-yo-ma",
}

CHURCH_BRAND_ARTIST_IDS = {
    "bethel-music",
    "elevation-worship",
    "hillsong-united",
    "hillsong-worship",
    "maverick-city-music",
    "passion",
}

CHURCH_BRAND_MARKERS = {
    "bethel-music",
    "elevation-worship",
    "hillsong-united",
    "hillsong-worship",
    "maverick-city-music",
    "passion",
}

SPECIAL_ALBUM_IDS = {
    "alan-silvestri-back-to-the-future",
    "aretha-franklin-amazing-grace",
    "elevation-worship-and-maverick-city-music-old-church-basement",
    "hans-zimmer-and-james-newton-howard-the-dark-knight",
    "hillsong-worship-shout-to-the-lord",
    "john-williams-jurassic-park",
    "john-williams-star-wars",
    "keith-and-kristyn-getty-in-christ-alone",
    "ludwig-goransson-black-panther",
    "original-broadway-cast-of-dear-evan-hansen-dear-evan-hansen",
    "original-broadway-cast-of-hamilton-hamilton",
    "original-broadway-cast-of-rent-rent",
    "original-broadway-cast-of-the-sound-of-music-the-sound-of-music",
    "original-broadway-cast-of-west-side-story-west-side-story",
    "original-broadway-cast-of-wicked-wicked",
    "original-london-cast-of-les-miserables-les-miserables",
    "original-london-cast-of-the-phantom-of-the-opera-the-phantom-of-the-opera",
    "various-artists-beauty-and-the-beast",
    "various-artists-coco",
    "various-artists-dirty-dancing",
    "various-artists-encanto",
    "various-artists-frozen",
    "various-artists-guardians-of-the-galaxy-awesome-mix-vol-1",
    "various-artists-moana",
    "various-artists-o-brother-where-art-thou",
    "various-artists-saturday-night-fever",
    "various-artists-the-bodyguard",
    "various-artists-the-lion-king",
    "various-artists-the-little-mermaid",
    "various-artists-top-gun",
    "yo-yo-ma-bach-cello-suites",
}

SPECIAL_ALBUM_MARKERS = {
    "black-panther",
    "guardians-of-the-galaxy",
    "original-broadway-cast",
    "original-london-cast",
}

SPECIAL_SONG_IDS = {
    "aretha-franklin-amazing-grace",
    "alan-silvestri-back-to-the-future",
    "bethel-music-and-jenn-johnson-goodness-of-god",
    "carolina-gaitan-mauro-castillo-adassa-rhenzy-feliz-diane-guerrero-stephanie-beatriz-and-encanto-cast-we-don-t-talk-about-bruno",
    "darlene-zschech-shout-to-the-lord",
    "elevation-worship-and-maverick-city-music-featuring-chandler-moore-and-naomi-raine-jireh",
    "encanto-cast-we-dont-talk-about-bruno",
    "f4-026-song-house-of-the-rising-sun-traditional-revival-circuit-object",
    "f4-026-song-we-shall-overcome-pete-seeger-et-al-traditional",
    "hans-zimmer-time",
    "john-coltrane-my-favorite-things",
    "john-williams-hedwig-s-theme",
    "john-williams-main-title",
    "john-williams-the-imperial-march",
    "john-williams-theme-from-jurassic-park",
    "kari-jobe-cody-carnes-and-elevation-worship-the-blessing",
    "keith-and-kristyn-getty-in-christ-alone",
    "london-philharmonic-orchestra-adagio-for-strings",
    "luciano-pavarotti-nessun-dorma",
    "ludwig-goransson-wakanda",
    "pat-barrett-build-my-life",
    "sinach-way-maker",
    "the-lion-king-cast-hakuna-matata",
    "the-soggy-bottom-boys-man-of-constant-sorrow",
    "traditional-the-wheels-on-the-bus",
    "yo-yo-ma-cello-suite-no-1-prelude",
}

SPECIAL_SONG_MARKERS = {
    "encanto-cast",
    "original-broadway-cast",
    "original-london-cast",
    "soggy-bottom-boys",
}

FAMILY12_PAGE1_ARTISTS = {
    "adele",
    "backstreet-boys",
    "beyonce",
    "britney-spears",
    "lady-gaga",
    "madonna",
    "mariah-carey",
    "michael-jackson",
    "prince",
    "rihanna",
    "taylor-swift",
    "whitney-houston",
}

FAMILY12_PAGE1_ALBUMS = {
    "adele-21",
    "backstreet-boys-millennium",
    "beyonce-lemonade",
    "britney-spears-baby-one-more-time",
    "lady-gaga-the-fame",
    "madonna-like-a-prayer",
    "mariah-carey-daydream",
    "michael-jackson-thriller",
    "prince-purple-rain",
    "rihanna-good-girl-gone-bad",
    "taylor-swift-1989",
    "whitney-houston-whitney-houston",
}

FAMILY12_PAGE1_SONGS = {
    "adele-rolling-in-the-deep",
    "backstreet-boys-i-want-it-that-way",
    "beyonce-crazy-in-love",
    "britney-spears-baby-one-more-time",
    "britney-spears-toxic",
    "lady-gaga-bad-romance",
    "madonna-like-a-prayer",
    "michael-jackson-billie-jean",
    "michael-jackson-thriller",
    "rihanna-umbrella",
    "taylor-swift-blank-space",
    "whitney-houston-i-wanna-dance-with-somebody",
}

FAMILY6_PAGE1_ARTISTS = {
    "al-green",
    "aretha-franklin",
    "donna-summer",
    "earth-wind-and-fire",
    "james-brown",
    "janet-jackson",
    "lauryn-hill",
    "marvin-gaye",
    "otis-redding",
    "stevie-wonder",
    "the-supremes",
    "the-temptations",
}

FAMILY6_PAGE1_ALBUMS = {
    "aretha-franklin-i-never-loved-a-man-the-way-i-love-you",
    "aretha-franklin-lady-soul",
    "donna-summer-bad-girls",
    "james-brown-live-at-the-apollo",
    "janet-jackson-control",
    "janet-jackson-rhythm-nation-1814",
    "lauryn-hill-the-miseducation-of-lauryn-hill",
    "marvin-gaye-whats-going-on",
    "otis-redding-otis-blue",
    "stevie-wonder-innervisions",
    "stevie-wonder-songs-in-the-key-of-life",
    "the-temptations-the-temptations-sing-smokey",
}

FAMILY6_PAGE1_SONGS = {
    "al-green-lets-stay-together",
    "aretha-franklin-respect",
    "donna-summer-i-feel-love",
    "earth-wind-and-fire-september",
    "james-brown-i-got-you-i-feel-good",
    "lauryn-hill-doo-wop-that-thing",
    "marvin-gaye-i-heard-it-through-the-grapevine",
    "otis-redding-sittin-on-the-dock-of-the-bay",
    "stevie-wonder-superstition",
    "the-supremes-you-cant-hurry-love",
    "the-temptations-my-girl",
    "whitney-houston-i-wanna-dance-with-somebody",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def slug(text: str | None) -> str:
    value = (text or "").lower().replace("&", "and")
    value = re.sub(r"[’']", "", value)
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")


def slug_contains_token(slug_text: str, token: str) -> bool:
    return f"-{token}-" in f"-{slug_text}-"


def slug_contains_phrase(slug_text: str, phrase: str) -> bool:
    return phrase in slug_text


def roles(row: dict[str, Any]) -> list[str]:
    value = row.get("roles", [])
    return value if isinstance(value, list) else [value]


def md_table(headers: list[str], rows: list[list[Any]]) -> str:
    def esc(value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, (list, tuple, set)):
            return "; ".join(esc(item) for item in value)
        return str(value).replace("|", "\\|").replace("\n", "<br>")

    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(esc(item) for item in row) + " |")
    return "\n".join(lines)


def entity_ref(entity_type: str, entity_id: str) -> str:
    return f"{entity_type}:{entity_id}"


def display_name(row: dict[str, Any], object_type: str) -> str:
    if object_type == "artist":
        return row.get("display_name") or row.get("artist_name") or row.get("canonical_artist_id") or ""
    if object_type == "album":
        title = row.get("display_name") or row.get("album_title") or row.get("canonical_album_id") or ""
        artists = row.get("artist_names") or ([row.get("artist_name")] if row.get("artist_name") else [])
        return f"{title} — {', '.join(artists)}" if artists else title
    title = row.get("display_name") or row.get("song_title") or row.get("canonical_song_recording_id") or ""
    artists = row.get("artist_names") or ([row.get("artist_name")] if row.get("artist_name") else [])
    return f"{title} — {', '.join(artists)}" if artists else title


def family_number(metadata: dict[str, Any], fallback: int) -> int:
    if "family_number" in metadata:
        return int(metadata["family_number"])
    match = re.search(r"(\d+)", str(metadata.get("family_id", "")))
    return int(match.group(1)) if match else fallback


def archetypes_from_metadata(metadata: dict[str, Any], family_id: int, family: dict[str, Any]) -> dict[str, str]:
    raw = metadata.get("archetypes")
    if isinstance(raw, dict):
        return {str(key): value for key, value in raw.items()}
    if isinstance(raw, list):
        output = {}
        for item in raw:
            if not isinstance(item, dict):
                continue
            archetype_id = str(item.get("archetype_id") or item.get("id") or "")
            if archetype_id:
                output[archetype_id] = (
                    item.get("name")
                    or item.get("archetype_name")
                    or item.get("title")
                    or f"Family {family_id} Archetype {archetype_id}"
                )
        if output:
            return output
    if family_id == 2:
        return dict(F2_ARCHETYPES)
    ids = sorted(
        {
            str(row.get("archetype_id"))
            for key in ["artists", "albums", "songs"]
            for row in family.get(key, [])
            if row.get("archetype_id")
        }
    )
    return {item: f"Family {family_id} Archetype {item}" for item in ids}


def raw_id(row: dict[str, Any]) -> str:
    return row.get("proposed_artist_id") or row.get("proposed_album_id") or row.get("proposed_song_id") or ""


def score_membership(row: dict[str, Any]) -> float:
    score = TIER_SCORE.get(row.get("survey_tier"), 0) + REC_SCORE.get(row.get("recognition_tier"), 0)
    score += float(row.get("archetype_membership_weight") or 0) * 100
    role_set = set(roles(row))
    if {"anchor", "artist_anchor", "album_anchor"} & role_set:
        score += 35
    if {"gateway", "song_first", "bridge"} & role_set:
        score += 18
    if {"false_nearby", "boundary", "contrast"} & role_set:
        score -= 12
    if row.get("consolidation_warning"):
        score -= 20
    return round(max(0, min(score / 3.1, 100)), 2)


def survey_intent_for(row: dict[str, Any], object_type: str, quarantined: bool) -> str:
    role_set = set(roles(row))
    warning = (row.get("consolidation_warning") or "").lower()
    if quarantined:
        return "do_not_survey"
    unresolved_version_warning = any(
        token in warning
        for token in [
            "unresolved",
            "needs review",
            "needs date",
            "needs version",
            "ambiguous",
            "wrong attribution",
            "suspected",
            "manual review",
        ]
    )
    if object_type == "song_recording" and unresolved_version_warning and ("composition" in warning or "version" in warning or "recording" in warning):
        return "composition_version_check"
    if "false_nearby" in role_set:
        return "false_nearby_test"
    if "boundary" in role_set or "contrast" in role_set:
        return "boundary_test"
    if "song_first" in role_set:
        return "song_first_memory"
    if object_type == "album" or "album_anchor" in role_set:
        return "album_world_test"
    if "bridge" in role_set:
        return "bridge_test"
    if "deepening" in role_set:
        return "deepening_only"
    if object_type == "artist":
        return "artist_affinity_probe"
    return "recognition_anchor"


def inference_guardrails(row: dict[str, Any], object_type: str, intent: str) -> dict[str, list[str]]:
    name = display_name(row, "song" if object_type == "song_recording" else object_type)
    positive = [f"possible affinity for {name} in this family/archetype context"]
    negative = [f"possible rejection or low appetite for {name} in this narrow context"]
    dont = [
        "do not infer broad genre appetite from one tap",
        "do not infer canonical graph mutation from survey response",
    ]
    if intent == "song_first_memory":
        positive.append("possible song-first memory or cultural-furniture recognition")
        dont.append("do not over-promote the artist from one song-first response")
    if intent == "album_world_test":
        positive.append("possible album-world appetite beyond single recognition")
        dont.append("do not infer favorite-artist status without artist/song evidence")
    if intent in {"boundary_test", "false_nearby_test", "dead_end_check"}:
        positive.append("possible boundary exception or bridge path")
        negative.append("possible false-nearby failure")
        dont.append("do not create Atlas Dead End without repeated user signal")
    if intent == "composition_version_check":
        dont.append("do not merge recordings, covers, live versions, or remixes by title")
    if row.get("consolidation_warning"):
        dont.append(row["consolidation_warning"])
    return {
        "positive_inference": positive,
        "negative_inference": negative,
        "do_not_infer": dont,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    manifest = load_json(DRY / "canonical_graph_manifest.json")
    artists = load_json(DRY / "canonical_artists.json")
    albums = load_json(DRY / "canonical_albums.json")
    songs = load_json(DRY / "canonical_song_recordings.json")
    artist_memberships = load_json(DRY / "artist_archetype_memberships.json")
    album_memberships = load_json(DRY / "album_archetype_memberships.json")
    song_memberships = load_json(DRY / "song_archetype_memberships.json")
    composition_queue = load_json(DRY / "composition_review_queue.json")
    warning_snippets = load_json(DRY / "warning_snippets.json")
    alias_queue = load_json(CG / "policy_hardening" / "alias_merge_qa_queue.json")

    artist_by_id = {row["canonical_artist_id"]: row for row in artists}
    album_by_id = {row["canonical_album_id"]: row for row in albums}
    song_by_id = {row["canonical_song_recording_id"]: row for row in songs}
    artist_by_norm = {slug(row["display_name"]): row["canonical_artist_id"] for row in artists}

    families: dict[int, dict[str, Any]] = {}
    family_names: dict[int, str] = {}
    archetype_names: dict[str, str] = {}
    archetype_family: dict[str, int] = {}
    raw_rows: list[dict[str, Any]] = []

    for number in range(1, 19):
        path = CG / f"family_{number}" / f"normalized_family_{number}.json"
        family = load_json(path)
        metadata = family.get("metadata", {})
        family_id = family_number(metadata, number)
        families[family_id] = family
        family_names[family_id] = metadata.get("family_name", f"Family {family_id}")
        for archetype_id, name in archetypes_from_metadata(metadata, family_id, family).items():
            archetype_names[archetype_id] = name
            archetype_family[archetype_id] = family_id
        for key, object_type, id_key in [
            ("artists", "artist", "proposed_artist_id"),
            ("albums", "album", "proposed_album_id"),
            ("songs", "song_recording", "proposed_song_id"),
        ]:
            for source in family.get(key, []):
                row = dict(source)
                row["_family_id"] = family_id
                row["_object_type"] = object_type
                row["_canonical_id"] = row.get(id_key)
                raw_rows.append(row)

    artist_aliases: list[dict[str, Any]] = []
    album_aliases: list[dict[str, Any]] = []
    recording_aliases: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []
    merge_blocks: list[dict[str, Any]] = []
    do_not_merge: list[dict[str, Any]] = []

    def add_alias(
        collection: list[dict[str, Any]],
        entity_type: str,
        canonical_id: str,
        alias_display: str,
        alias_type: str = "display",
        collapse_policy: str = "safe_alias",
        status: str = "approved",
        note: str = "Normalization Pass 2",
    ) -> None:
        collection.append(
            {
                "alias_id": f"alias-{entity_type}-{slug(canonical_id)}-{slug(alias_display)}",
                "canonical_entity_id": canonical_id,
                "entity_type": entity_type,
                "alias_display": alias_display,
                "alias_normalized": slug(alias_display),
                "alias_type": alias_type,
                "collapse_policy": collapse_policy,
                "source_note": note,
                "review_status": status,
            }
        )

    def add_relationship(
        entity_a: str,
        entity_b: str,
        relationship_type: str,
        collapse_policy: str = "linked_not_collapsed",
        review_status: str = "approved",
        note: str = "Normalization Pass 2",
        import_action: str = "preserve_both",
    ) -> None:
        relationships.append(
            {
                "relationship_id": f"rel-{slug(entity_a)}-{slug(relationship_type)}-{slug(entity_b)}",
                "entity_a": entity_a,
                "entity_b": entity_b,
                "relationship_type": relationship_type,
                "collapse_policy": collapse_policy,
                "import_action": import_action,
                "source_note": note,
                "review_status": review_status,
            }
        )

    def add_do_not_merge(entity_a: str, entity_b: str, reason: str, severity: str = "blocking") -> None:
        do_not_merge.append(
            {
                "rule_id": f"dnm-{slug(entity_a)}-{slug(entity_b)}",
                "entity_a": entity_a,
                "entity_b": entity_b,
                "reason": reason,
                "severity": severity,
                "review_status": "approved",
            }
        )

    def add_merge_block(entity_a: str, entity_b: str, reason: str, status: str = "needs_human_review") -> None:
        merge_blocks.append(
            {
                "block_id": f"merge-block-{slug(entity_a)}-{slug(entity_b)}",
                "entity_a": entity_a,
                "entity_b": entity_b,
                "block_reason": reason,
                "severity": "blocking",
                "review_status": status,
                "source_note": "Normalization Pass 2 conservative import guard",
            }
        )

    # Safe display aliases and known stage/project aliases.
    for canonical_id, aliases, alias_type in [
        ("martha-and-the-vandellas", ["Martha & the Vandellas"], "display"),
        ("simon-and-garfunkel", ["Simon and Garfunkel"], "display"),
        ("kool-and-the-gang", ["Kool & The Gang"], "display"),
        ("the-b-52-s", ["The B-52s"], "punctuation"),
        ("staple-singers", ["The Staple Singers"], "display"),
        ("smokey-robinson-and-the-miracles", ["Smokey Robinson & The Miracles"], "display"),
        ("2pac", ["Tupac", "Tupac Shakur"], "stage_name"),
        ("mos-def-yasiin-bey", ["Mos Def", "Yasiin Bey"], "stage_name"),
        ("jeezy", ["Young Jeezy"], "stage_name"),
        ("yazoo", ["Yaz"], "legacy_slug"),
    ]:
        for alias_display in aliases:
            add_alias(artist_aliases, "artist", canonical_id, alias_display, alias_type)

    add_alias(album_aliases, "album", "the-sonics-here-are-the-sonics", "Here Are The Sonics", "display")
    add_alias(recording_aliases, "song_recording", "martha-and-the-vandellas-dancing-in-the-street", "Martha & the Vandellas - Dancing in the Street", "display")
    add_alias(recording_aliases, "song_recording", "the-b-52-s-love-shack", "The B-52s - Love Shack", "punctuation")
    add_alias(recording_aliases, "song_recording", "staple-singers-ill-take-you-there", "The Staple Singers - I'll Take You There", "display")
    add_alias(recording_aliases, "song_recording", "the-byrds-turn-turn-turn", "The Byrds / Pete Seeger - Turn! Turn! Turn!", "composition_credit")

    # Safe canonicalization relationships for emitted duplicate IDs.
    for source, target, relation in [
        ("artist:the-staple-singers", "artist:staple-singers", "same_entity_alias"),
        ("song_recording:the-staple-singers-i-ll-take-you-there", "song_recording:staple-singers-ill-take-you-there", "same_recording_alias"),
        ("song_recording:the-b-52s-love-shack", "song_recording:the-b-52-s-love-shack", "same_recording_alias"),
        ("song_recording:f4-026-song-turn-turn-turn-the-byrds-pete-seeger", "song_recording:the-byrds-turn-turn-turn", "same_recording_alias"),
    ]:
        add_relationship(source, target, relation, "safe_alias", "approved", import_action="canonicalize_to_target")

    # Group/solo/project/cast/church brand relationships and do-not-merge rules.
    protected_pairs = [
        ("artist:beyonce", "artist:destinys-child", "group_vs_solo"),
        ("artist:michael-jackson", "artist:jackson-5", "group_vs_solo"),
        ("artist:diana-ross", "artist:the-supremes", "group_vs_solo"),
        ("artist:prince", "artist:prince-and-the-revolution", "credited_artist_vs_canonical_artist"),
        ("artist:smokey-robinson", "artist:smokey-robinson-and-the-miracles", "group_vs_solo"),
        ("artist:public-image-ltd", "artist:sex-pistols", "project_alias_not_artist_alias"),
        ("artist:love-and-rockets", "artist:bauhaus", "project_alias_not_artist_alias"),
        ("artist:split-enz", "artist:crowded-house", "project_alias_not_artist_alias"),
        ("artist:hillsong-worship", "artist:hillsong-united", "church_brand"),
        ("artist:bethel-music", "artist:elevation-worship", "church_brand"),
        ("artist:maverick-city-music", "artist:elevation-worship", "church_brand"),
        ("artist:sleep", "artist:sleep-token", "ambiguous_artist_names"),
    ]
    for entity_a, entity_b, reason in protected_pairs:
        add_relationship(entity_a, entity_b, "related_but_distinct", "do_not_merge", "approved")
        add_do_not_merge(entity_a, entity_b, reason)

    # Electronic project aliases are linked, not collapsed.
    for parent, projects in [
        ("artist:larry-heard", ["artist:mr-fingers", "artist:fingers-inc"]),
        ("artist:juan-atkins", ["artist:model-500", "artist:cybotron"]),
        ("artist:kevin-saunderson", ["artist:inner-city"]),
    ]:
        for project in projects:
            add_relationship(parent, project, "producer_project_alias", "linked_not_collapsed", "needs_human_review")
            add_merge_block(parent, project, "producer project aliases require explicit artist/project modeling")

    # Composition classification.
    composition_queue_by_key = {row["composition_key"]: row for row in composition_queue}
    composition_class = {
        "alison": "same_title_different_composition",
        "blind": "same_title_different_composition",
        "cupid": "same_title_different_composition",
        "doomsday": "same_title_different_composition",
        "gee": "same_title_different_composition",
        "god-only-knows": "same_title_different_composition",
        "lonely-boy": "same_title_different_composition",
        "oblivion": "same_title_different_composition",
        "only-you": "same_title_different_composition",
        "push-it": "same_title_different_composition",
        "stay": "same_title_different_composition",
        "zombie": "same_title_different_composition",
        "hound-dog": "same_composition_distinct_recording",
        "the-twist": "same_composition_distinct_recording",
        "shake-rattle-and-roll": "same_composition_distinct_recording",
        "that-s-all-right": "same_composition_distinct_recording",
        "walk-this-way": "same_composition_distinct_recording",
        "cum-on-feel-the-noize": "same_composition_distinct_recording",
        "i-ll-take-you-there": "same_composition_same_recording_alias",
        "love-shack": "same_composition_same_recording_alias",
        "turn-turn-turn": "same_composition_same_recording_alias",
        "we-don-t-talk-about-bruno": "quarantined",
        "house-of-the-rising-sun": "traditional_work_first_object",
        "gloria": "mixed_same_title_split",
    }
    composition_types = {
        "house-of-the-rising-sun": "traditional",
        "we-shall-overcome": "traditional",
        "amazing-grace": "hymn",
        "in-christ-alone": "hymn",
        "shout-to-the-lord": "worship_standard",
        "build-my-life": "worship_standard",
        "way-maker": "worship_standard",
        "my-favorite-things": "show_tune",
        "nessun-dorma": "classical_work",
        "cello-suite-no-1-prelude": "classical_work",
        "adagio-for-strings": "classical_work",
        "we-don-t-talk-about-bruno": "film_song",
    }
    public_domain = {"house-of-the-rising-sun", "we-shall-overcome", "amazing-grace"}

    composition_rows: dict[str, dict[str, Any]] = {}
    recording_versions: list[dict[str, Any]] = []
    cover_relationships: list[dict[str, Any]] = []
    recording_class_by_id: dict[str, str] = {}
    recording_comp_by_id: dict[str, str] = {}

    def add_composition_row(
        composition_id: str,
        title: str,
        normalized_title: str,
        composition_type: str = "popular_song",
        writer: str = "",
        traditional: bool = False,
        review_status: str = "approved",
        classification: str = "single_recording_or_uncontested",
    ) -> None:
        composition_rows[composition_id] = {
            "composition_id": composition_id,
            "composition_title": title,
            "normalized_title": normalized_title,
            "composition_type": composition_type,
            "known_writer_credit": writer,
            "traditional_or_public_domain": traditional,
            "review_status": review_status,
            "composition_review_classification": classification,
        }

    def composition_for_song(row: dict[str, Any]) -> tuple[str, str, str]:
        key = row["composition_key"]
        classification = composition_class.get(key, "single_recording_or_uncontested")
        status = "approved"
        if classification == "quarantined":
            status = "quarantined"
        if classification == "same_title_different_composition":
            composition_id = f"composition-{key}-{slug(row.get('artist_names', ['unknown'])[0])}"
        elif key == "gloria":
            artist_credit = " ".join(row.get("artist_names", []))
            composition_id = "composition-gloria-cadillacs" if "Cadillacs" in artist_credit else "composition-gloria-van-morrison"
        else:
            composition_id = f"composition-{key}"
        return composition_id, classification, status

    # Add required external/source composition rows.
    required_extra_compositions = [
        ("composition-i-will-always-love-you", "I Will Always Love You", "popular_song", "Dolly Parton", False),
        ("composition-beggin", "Beggin'", "popular_song", "Bob Gaudio / Peggy Farina", False),
        ("composition-hurt", "Hurt", "popular_song", "Trent Reznor", False),
        ("composition-killing-me-softly", "Killing Me Softly with His Song", "popular_song", "", False),
        ("composition-wap", "WAP", "popular_song", "", False),
        ("composition-i-dont-like", "I Don't Like", "popular_song", "", False),
        ("composition-good-riddance-time-of-your-life", "Good Riddance (Time of Your Life)", "popular_song", "", False),
        ("composition-we-shall-overcome", "We Shall Overcome", "traditional", "traditional / movement standard", True),
        ("composition-my-favorite-things", "My Favorite Things", "show_tune", "Rodgers and Hammerstein", False),
        ("composition-nessun-dorma", "Nessun dorma", "classical_work", "Giacomo Puccini", False),
        ("composition-cello-suite-no-1-prelude", "Cello Suite No. 1: Prelude", "classical_work", "J. S. Bach", True),
        ("composition-adagio-for-strings", "Adagio for Strings", "classical_work", "Samuel Barber", False),
        ("composition-amazing-grace", "Amazing Grace", "hymn", "traditional hymn", True),
        ("composition-in-christ-alone", "In Christ Alone", "hymn", "Keith Getty / Stuart Townend", False),
        ("composition-shout-to-the-lord", "Shout to the Lord", "worship_standard", "Darlene Zschech", False),
        ("composition-build-my-life", "Build My Life", "worship_standard", "", False),
        ("composition-way-maker", "Way Maker", "worship_standard", "Sinach", False),
    ]
    for comp_id, title, comp_type, writer, traditional in required_extra_compositions:
        add_composition_row(
            comp_id,
            title,
            slug(title),
            comp_type,
            writer,
            traditional,
            "approved" if comp_type not in {"traditional", "hymn", "worship_standard", "classical_work", "show_tune"} else "needs_review",
            "required_policy_placeholder",
        )

    source_version_ids = {
        "big-mama-thornton-hound-dog",
        "hank-ballard-and-the-midnighters-the-twist",
        "big-joe-turner-shake-rattle-and-roll",
        "arthur-big-boy-crudup-thats-all-right",
        "song-walk-this-way-1975",
        "song-cum-on-feel-the-noize-1973",
        "roberta-flack-killing-me-softly-with-his-song",
        "nine-inch-nails-hurt",
    }
    cover_version_ids = {
        "elvis-presley-hound-dog",
        "chubby-checker-the-twist",
        "bill-haley-and-his-comets-shake-rattle-and-roll",
        "elvis-presley-thats-all-right",
        "run-dmc-walk-this-way",
        "quiet-riot-cum-on-feel-the-noize",
        "whitney-houston-i-will-always-love-you",
        "fugees-killing-me-softly",
        "maneskin-beggin",
    }
    live_or_special_context = {
        "green-day-good-riddance-time-of-your-life": "album_version",
        "cardi-b-feat-megan-thee-stallion-wap": "explicit",
        "chief-keef-feat-lil-reese-i-dont-like": "source_version",
        "john-coltrane-my-favorite-things": "traditional_arrangement",
        "luciano-pavarotti-nessun-dorma": "traditional_arrangement",
        "yo-yo-ma-cello-suite-no-1-prelude": "traditional_arrangement",
        "london-philharmonic-orchestra-adagio-for-strings": "traditional_arrangement",
        "carolina-gaitan-mauro-castillo-adassa-rhenzy-feliz-diane-guerrero-stephanie-beatriz-and-encanto-cast-we-don-t-talk-about-bruno": "cast_recording",
        "encanto-cast-we-dont-talk-about-bruno": "cast_recording",
        "the-soggy-bottom-boys-man-of-constant-sorrow": "film_version",
        "darlene-zschech-shout-to-the-lord": "traditional_arrangement",
        "keith-and-kristyn-getty-in-christ-alone": "traditional_arrangement",
        "pat-barrett-build-my-life": "traditional_arrangement",
        "sinach-way-maker": "traditional_arrangement",
        "aretha-franklin-amazing-grace": "live",
    }

    for song in songs:
        composition_id, classification, status = composition_for_song(song)
        composition_type = composition_types.get(song["composition_key"], "popular_song")
        if composition_id not in composition_rows:
            add_composition_row(
                composition_id,
                song.get("song_title") or song["display_name"],
                song["composition_key"],
                composition_type,
                "",
                song["composition_key"] in public_domain,
                status,
                classification,
            )
        recording_id = song["canonical_song_recording_id"]
        context = "source_version" if recording_id in source_version_ids else "cover" if recording_id in cover_version_ids else live_or_special_context.get(recording_id, "original")
        review_status = status
        if recording_id == "cardi-b-feat-megan-thee-stallion-wap":
            review_status = "needs_review"
        if classification == "traditional_work_first_object":
            review_status = "needs_review"
        if classification == "quarantined":
            review_status = "quarantined"
        artist_credit = ", ".join(song.get("artist_names", []))
        artist_id = artist_by_norm.get(slug(song.get("artist_names", [""])[0]))
        survey_safe = review_status == "approved" and context not in {"cast_recording", "traditional_arrangement"} and classification != "quarantined"
        recording_versions.append(
            {
                "recording_id": recording_id,
                "composition_id": composition_id,
                "recording_artist_id": artist_id,
                "display_artist_credit": artist_credit,
                "recording_title": song.get("song_title") or song["display_name"],
                "recording_context": context,
                "release_year_policy": "unknown" if not song.get("release_years") else "recording",
                "apple_music_resolution_policy": "manual_review_required" if review_status != "approved" else "exact_recording_required",
                "survey_safe": survey_safe,
                "review_status": review_status,
                "composition_review_classification": classification,
            }
        )
        recording_class_by_id[recording_id] = classification
        recording_comp_by_id[recording_id] = composition_id

    def add_cover(source: str, cover: str, composition_id: str, relationship_type: str = "cover") -> None:
        cover_relationships.append(
            {
                "relationship_id": f"cover-{slug(source)}-{slug(cover)}",
                "composition_id": composition_id,
                "source_recording_id": source,
                "derived_recording_id": cover,
                "relationship_type": relationship_type,
                "collapse_policy": "do_not_merge_recordings",
                "review_status": "approved",
            }
        )

    for source, cover, comp in [
        ("big-mama-thornton-hound-dog", "elvis-presley-hound-dog", "composition-hound-dog"),
        ("hank-ballard-and-the-midnighters-the-twist", "chubby-checker-the-twist", "composition-the-twist"),
        ("big-joe-turner-shake-rattle-and-roll", "bill-haley-and-his-comets-shake-rattle-and-roll", "composition-shake-rattle-and-roll"),
        ("arthur-big-boy-crudup-thats-all-right", "elvis-presley-thats-all-right", "composition-that-s-all-right"),
        ("song-walk-this-way-1975", "run-dmc-walk-this-way", "composition-walk-this-way"),
        ("song-cum-on-feel-the-noize-1973", "quiet-riot-cum-on-feel-the-noize", "composition-cum-on-feel-the-noize"),
        ("external:dolly-parton-i-will-always-love-you", "whitney-houston-i-will-always-love-you", "composition-i-will-always-love-you"),
        ("roberta-flack-killing-me-softly-with-his-song", "fugees-killing-me-softly", "composition-killing-me-softly"),
        ("external:the-four-seasons-beggin", "maneskin-beggin", "composition-beggin"),
        ("nine-inch-nails-hurt", "external:johnny-cash-hurt", "composition-hurt"),
    ]:
        add_cover(source, cover, comp)
        add_do_not_merge(f"song_recording:{source}", f"song_recording:{cover}", "source_vs_cover")

    for item in composition_queue:
        ids = item.get("canonical_song_recording_ids", [])
        classification = composition_class.get(item["composition_key"], "needs_review")
        reason = "same_title_different_composition" if classification == "same_title_different_composition" else "same_title_recording_review"
        for left_index, left in enumerate(ids):
            for right in ids[left_index + 1 :]:
                if classification in {"same_composition_same_recording_alias"}:
                    add_relationship(f"song_recording:{left}", f"song_recording:{right}", "same_recording_alias", "safe_alias", "approved", import_action="canonicalize_to_policy_target")
                else:
                    add_do_not_merge(f"song_recording:{left}", f"song_recording:{right}", reason)

    # Special entity support.
    special_entities = [
        ("film:encanto", "film", "Encanto", ["song_recording:carolina-gaitan-mauro-castillo-adassa-rhenzy-feliz-diane-guerrero-stephanie-beatriz-and-encanto-cast-we-don-t-talk-about-bruno", "song_recording:encanto-cast-we-dont-talk-about-bruno"], False, "cast_recording", "manual_review_required"),
        ("film:black-panther", "film", "Black Panther", ["album:ludwig-goransson-black-panther"], False, "score_album", "manual_review_required"),
        ("curated_soundtrack:guardians-awesome-mix-vol-1", "curated_soundtrack", "Guardians of the Galaxy: Awesome Mix Vol. 1", ["album:various-artists-guardians-of-the-galaxy-awesome-mix-vol-1"], False, "compilation_album", "exact_recording_required"),
        ("fictional_performer:the-soggy-bottom-boys", "fictional_performer", "The Soggy Bottom Boys", ["song_recording:the-soggy-bottom-boys-man-of-constant-sorrow"], False, "fictional_performer_recording", "manual_review_required"),
        ("church_brand:hillsong", "church_brand", "Hillsong", ["artist:hillsong-worship", "artist:hillsong-united"], False, "brand_context", "manual_review_required"),
        ("church_brand:bethel-music", "church_brand", "Bethel Music", ["artist:bethel-music"], False, "brand_context", "manual_review_required"),
        ("church_brand:elevation-worship", "church_brand", "Elevation Worship", ["artist:elevation-worship"], False, "brand_context", "manual_review_required"),
        ("church_brand:maverick-city-music", "church_brand", "Maverick City Music", ["artist:maverick-city-music"], False, "brand_context", "manual_review_required"),
        ("church_brand:passion", "church_brand", "Passion", ["artist:passion"], False, "brand_context", "manual_review_required"),
        ("worship_standard:amazing-grace", "worship_standard", "Amazing Grace", ["composition:composition-amazing-grace", "song_recording:aretha-franklin-amazing-grace"], False, "composition", "manual_review_required"),
        ("worship_standard:in-christ-alone", "worship_standard", "In Christ Alone", ["composition:composition-in-christ-alone", "song_recording:keith-and-kristyn-getty-in-christ-alone"], False, "composition", "manual_review_required"),
        ("worship_standard:shout-to-the-lord", "worship_standard", "Shout to the Lord", ["composition:composition-shout-to-the-lord", "song_recording:darlene-zschech-shout-to-the-lord"], False, "composition", "manual_review_required"),
        ("traditional_song:house-of-the-rising-sun", "traditional_song", "House of the Rising Sun", ["composition:composition-house-of-the-rising-sun"], False, "composition", "manual_review_required"),
        ("traditional_song:we-shall-overcome", "traditional_song", "We Shall Overcome", ["composition:composition-we-shall-overcome"], False, "composition", "manual_review_required"),
        ("musical_work:my-favorite-things", "musical_work", "My Favorite Things", ["composition:composition-my-favorite-things", "song_recording:john-coltrane-my-favorite-things"], False, "composition", "manual_review_required"),
        ("musical_work:nessun-dorma", "musical_work", "Nessun dorma", ["composition:composition-nessun-dorma", "song_recording:luciano-pavarotti-nessun-dorma"], False, "composition", "manual_review_required"),
        ("musical_work:cello-suite-no-1-prelude", "musical_work", "Cello Suite No. 1: Prelude", ["composition:composition-cello-suite-no-1-prelude", "song_recording:yo-yo-ma-cello-suite-no-1-prelude"], False, "composition", "manual_review_required"),
        ("musical_work:adagio-for-strings", "musical_work", "Adagio for Strings", ["composition:composition-adagio-for-strings", "song_recording:london-philharmonic-orchestra-adagio-for-strings"], False, "composition", "manual_review_required"),
        ("channel_object:lo-fi-girl", "channel_object", "Lo-fi Girl-style channel/use-case object", [], False, "context", "manual_review_required"),
    ]
    canonical_special_entities = [
        {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "display_name": name,
            "related_entity_refs": refs,
            "survey_safe": survey_safe,
            "reaction_target_type": reaction_target,
            "apple_music_resolution_policy": apple_policy,
            "atlas_promotion_policy": "never_promote_without_user_signal",
            "do_not_infer_rules": [
                "do not treat context object as ordinary artist taste",
                "do not collapse work, recording, performer, and context",
            ],
            "review_status": "needs_review" if not survey_safe else "approved",
        }
        for entity_id, entity_type, name, refs, survey_safe, reaction_target, apple_policy in special_entities
    ]

    # Quarantine system.
    quarantine: dict[str, dict[str, Any]] = {}

    def quarantine_ref(entity_type: str, entity_id: str, reason: str, note: str) -> None:
        ref = entity_ref(entity_type, entity_id)
        existing = quarantine.get(ref)
        if existing:
            if reason not in existing["quarantine_reasons"]:
                existing["quarantine_reasons"].append(reason)
            if note not in existing["source_notes"]:
                existing["source_notes"].append(note)
            return
        quarantine[ref] = {
            "quarantine_id": f"quarantine-{slug(ref)}",
            "entity_ref": ref,
            "entity_type": entity_type,
            "canonical_entity_id": entity_id,
            "quarantine_reasons": [reason],
            "review_status": "needs_human_review",
            "blocked_surfaces": [
                "fast_survey",
                "page1_deep_survey",
                "starter_atlas",
                "default_mission_generation",
                "apple_music_auto_resolution",
            ],
            "source_notes": [note],
        }

    mandatory_quarantine_ids = {
        "song_recording": {
            "f4-028-song-waiting-for-a-superman-the-jayhawks": "wrong_attribution_suspected",
            "cardi-b-feat-megan-thee-stallion-wap": "version_unresolved",
            "f4-026-song-we-shall-overcome-pete-seeger-et-al-traditional": "composition_unresolved",
            "f4-026-song-house-of-the-rising-sun-traditional-revival-circuit-object": "composition_unresolved",
            "carolina-gaitan-mauro-castillo-adassa-rhenzy-feliz-diane-guerrero-stephanie-beatriz-and-encanto-cast-we-don-t-talk-about-bruno": "special_entity_model_missing",
            "encanto-cast-we-dont-talk-about-bruno": "special_entity_model_missing",
            "the-soggy-bottom-boys-man-of-constant-sorrow": "special_entity_model_missing",
            "john-coltrane-my-favorite-things": "composition_unresolved",
            "luciano-pavarotti-nessun-dorma": "composition_unresolved",
            "yo-yo-ma-cello-suite-no-1-prelude": "composition_unresolved",
            "london-philharmonic-orchestra-adagio-for-strings": "composition_unresolved",
            "aretha-franklin-amazing-grace": "composition_unresolved",
            "keith-and-kristyn-getty-in-christ-alone": "composition_unresolved",
            "darlene-zschech-shout-to-the-lord": "composition_unresolved",
            "pat-barrett-build-my-life": "composition_unresolved",
            "sinach-way-maker": "composition_unresolved",
        },
        "album": {
            "ludwig-goransson-black-panther": "special_entity_model_missing",
            "various-artists-guardians-of-the-galaxy-awesome-mix-vol-1": "apple_music_resolution_risky",
            "keith-and-kristyn-getty-in-christ-alone": "composition_unresolved",
            "hillsong-worship-shout-to-the-lord": "composition_unresolved",
            "aretha-franklin-amazing-grace": "composition_unresolved",
        },
        "artist": {
            "passion": "special_entity_model_missing",
            "hillsong-worship": "special_entity_model_missing",
            "bethel-music": "special_entity_model_missing",
            "elevation-worship": "special_entity_model_missing",
            "maverick-city-music": "special_entity_model_missing",
            "alan-menken": "special_entity_model_missing",
            "alan-silvestri": "special_entity_model_missing",
            "ludwig-goransson": "special_entity_model_missing",
        },
    }
    for entity_type, ids in mandatory_quarantine_ids.items():
        for entity_id, reason in ids.items():
            quarantine_ref(entity_type, entity_id, reason, "mandatory Normalization Pass 2 quarantine example or special-model guard")

    def artist_credit_ids(names: list[str]) -> set[str]:
        return {slug(name) for name in names if name}

    def song_requires_special_model(song: dict[str, Any]) -> bool:
        recording_id = song["canonical_song_recording_id"]
        text_slug = slug(f"{song.get('display_name', '')} {' '.join(song.get('artist_names', []))}")
        credit_ids = artist_credit_ids(song.get("artist_names", []))
        return (
            recording_id in SPECIAL_SONG_IDS
            or bool(credit_ids & CHURCH_BRAND_ARTIST_IDS)
            or any(slug_contains_phrase(text_slug, marker) for marker in CHURCH_BRAND_MARKERS)
            or any(slug_contains_phrase(text_slug, marker) for marker in SPECIAL_SONG_MARKERS)
            or slug_contains_token(text_slug, "cast")
            or slug_contains_token(text_slug, "traditional")
        )

    def album_requires_special_model(album: dict[str, Any]) -> bool:
        album_id = album["canonical_album_id"]
        text_slug = slug(f"{album.get('display_name', '')} {' '.join(album.get('artist_names', []))}")
        credit_ids = artist_credit_ids(album.get("artist_names", []))
        return (
            album_id in SPECIAL_ALBUM_IDS
            or bool(credit_ids & CHURCH_BRAND_ARTIST_IDS)
            or any(slug_contains_phrase(text_slug, marker) for marker in CHURCH_BRAND_MARKERS)
            or any(slug_contains_phrase(text_slug, marker) for marker in SPECIAL_ALBUM_MARKERS)
        )

    def artist_requires_special_model(artist: dict[str, Any]) -> bool:
        text_slug = slug(artist.get("display_name", ""))
        return artist["canonical_artist_id"] in SPECIAL_ENTITY_ARTIST_IDS or slug_contains_token(text_slug, "cast")

    # Same-title groups that remain cast/traditional/needs-review are quarantined.
    for song in songs:
        recording_id = song["canonical_song_recording_id"]
        classification = recording_class_by_id.get(recording_id, "")
        if classification in {"quarantined", "traditional_work_first_object"}:
            quarantine_ref("song_recording", recording_id, "composition_unresolved", f"composition group classified {classification}")
        if recording_id in song_by_id and 11 in song.get("family_numbers", []) and song.get("best_survey_tier") == "core":
            quarantine_ref("song_recording", recording_id, "apple_music_resolution_risky", "Family 11 core club/electronic row requires mix/edit review before Fast Survey")
        if song_requires_special_model(song):
            quarantine_ref("song_recording", recording_id, "special_entity_model_missing", "special work/context row blocked from Fast Survey until typed entity model is used")

    for album in albums:
        if album_requires_special_model(album):
            quarantine_ref("album", album["canonical_album_id"], "special_entity_model_missing", "special album/context row blocked from Fast Survey")

    for artist in artists:
        if artist_requires_special_model(artist):
            quarantine_ref("artist", artist["canonical_artist_id"], "special_entity_model_missing", "artist-like context/brand/composer row blocked from Fast Survey")

    for recording in recording_versions:
        ref = entity_ref("song_recording", recording["recording_id"])
        if ref in quarantine:
            reasons = quarantine[ref]["quarantine_reasons"]
            recording["survey_safe"] = False
            recording["survey_safe_reason"] = "quarantined: " + "; ".join(reasons)
            recording["review_status"] = "quarantined" if {"wrong_attribution_suspected", "special_entity_model_missing"} & set(reasons) else "needs_review"
            recording["apple_music_resolution_policy"] = "manual_review_required"
        elif not recording["survey_safe"]:
            reason = recording.get("composition_review_classification") or recording.get("recording_context") or "not_survey_safe"
            recording["survey_safe_reason"] = f"not survey safe: {reason}"
            if recording["review_status"] == "approved":
                recording["review_status"] = "needs_review"
            recording["apple_music_resolution_policy"] = "manual_review_required"
        else:
            recording["survey_safe_reason"] = "approved exact recording"

    quarantine_refs = set(quarantine.keys())

    # Archetype readiness before surface build.
    approved_by_archetype: dict[str, Counter[str]] = defaultdict(Counter)
    for table, entity_type, id_key, lookup in [
        (artist_memberships, "artist", "canonical_artist_id", artist_by_id),
        (album_memberships, "album", "canonical_album_id", album_by_id),
        (song_memberships, "song_recording", "canonical_song_recording_id", song_by_id),
    ]:
        for membership in table:
            entity_id = membership[id_key]
            ref = entity_ref(entity_type, entity_id)
            if ref in quarantine_refs or membership.get("survey_tier") == "suppress":
                continue
            archetype_id = str(membership.get("archetype_id"))
            if membership.get("survey_tier") == "core" and membership.get("recognition_tier") in {"mass", "high"}:
                approved_by_archetype[archetype_id]["page1"] += 1
            if membership.get("survey_tier") in {"standard", "edge"}:
                approved_by_archetype[archetype_id]["page2"] += 1
            approved_by_archetype[archetype_id]["total"] += 1

    archetype_readiness = []
    for archetype_id, name in sorted(archetype_names.items(), key=lambda item: int(item[0]) if item[0].isdigit() else 999):
        counts = approved_by_archetype[archetype_id]
        family_id = archetype_family.get(archetype_id)
        if family_id in {15, 17}:
            classification = "context_only"
        elif family_id == 12 and counts["page1"] >= 6:
            classification = "survey_ready"
        elif counts["page1"] >= 4 and counts["page2"] >= 8:
            classification = "survey_ready"
        elif counts["total"] >= 8 and counts["page2"] >= 4:
            classification = "adaptive_only"
        elif counts["total"] >= 4:
            classification = "deep_only"
        else:
            classification = "not_ready"
        archetype_readiness.append(
            {
                "archetype_id": archetype_id,
                "family_id": family_id,
                "archetype_name": name,
                "readiness": classification,
                "page1_candidate_count": counts["page1"],
                "page2_candidate_count": counts["page2"],
                "approved_candidate_count": counts["total"],
                "fast_survey_allowed": classification == "survey_ready",
            }
        )
    readiness_by_archetype = {row["archetype_id"]: row for row in archetype_readiness}

    # Candidate surface generation.
    redirect_ref = {
        "artist:the-staple-singers": "artist:staple-singers",
        "song_recording:the-staple-singers-i-ll-take-you-there": "song_recording:staple-singers-ill-take-you-there",
        "song_recording:the-b-52s-love-shack": "song_recording:the-b-52-s-love-shack",
        "song_recording:f4-026-song-turn-turn-turn-the-byrds-pete-seeger": "song_recording:the-byrds-turn-turn-turn",
    }

    def candidate_from_membership(membership: dict[str, Any], entity_type: str, entity: dict[str, Any]) -> dict[str, Any]:
        if entity_type == "artist":
            entity_id = membership["canonical_artist_id"]
            object_type = "artist"
        elif entity_type == "album":
            entity_id = membership["canonical_album_id"]
            object_type = "album"
        else:
            entity_id = membership["canonical_song_recording_id"]
            object_type = "song_recording"
        ref = entity_ref(object_type, entity_id)
        canonical_ref = redirect_ref.get(ref, ref)
        quarantined = ref in quarantine_refs or canonical_ref in quarantine_refs
        if readiness_by_archetype.get(str(membership.get("archetype_id")), {}).get("readiness") == "not_ready":
            quarantined = True
        intent = survey_intent_for(membership, object_type, quarantined)
        guardrails = inference_guardrails(membership, object_type, intent)
        archetype_name = archetype_names.get(str(membership.get("archetype_id")))
        if archetype_name:
            guardrails["positive_inference"].append(f"possible openness to the {archetype_name} lane")
            guardrails["do_not_infer"].append("do not infer adjacent archetypes without follow-up evidence")
        review_status = "quarantined" if quarantined else "approved"
        if object_type == "song_recording" and recording_class_by_id.get(entity_id) == "quarantined":
            review_status = "quarantined"
        priority = score_membership(membership)
        if object_type == "song_recording" and recording_class_by_id.get(entity_id) in {"same_title_different_composition", "same_composition_distinct_recording"}:
            priority -= 8
        preferred_page1_ids = {
            (6, "artist"): FAMILY6_PAGE1_ARTISTS,
            (6, "album"): FAMILY6_PAGE1_ALBUMS,
            (6, "song_recording"): FAMILY6_PAGE1_SONGS,
            (12, "artist"): FAMILY12_PAGE1_ARTISTS,
            (12, "album"): FAMILY12_PAGE1_ALBUMS,
            (12, "song_recording"): FAMILY12_PAGE1_SONGS,
        }
        preferred = preferred_page1_ids.get((membership["family_number"], object_type), set())
        if entity_id in preferred:
            priority = 100
        elif membership["family_number"] in {6, 12}:
            priority = min(priority, 88 if membership["family_number"] == 6 else 84)
        return {
            "candidate_id": f"survey-f{membership['family_number']}-{object_type}-{slug(entity_id)}-{membership.get('archetype_id')}",
            "canonical_entity_id": entity_id,
            "display_label": entity.get("display_name") or display_name(entity, object_type),
            "object_type": object_type,
            "family_id": membership["family_number"],
            "archetype_ids": [str(membership.get("archetype_id"))],
            "survey_page_role": "unassigned",
            "survey_intent": intent,
            "trigger_rule": "generated_from_membership_roles_and_tiers",
            "do_not_infer": guardrails["do_not_infer"],
            "positive_inference": guardrails["positive_inference"],
            "negative_inference": guardrails["negative_inference"],
            "dedupe_group": canonical_ref,
            "priority_score": round(max(priority, 0), 2),
            "review_status": review_status,
            "quarantine_reasons": quarantine.get(ref, {}).get("quarantine_reasons", []),
            "source_membership_id": membership.get("membership_id"),
        }

    family_object_candidates: dict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
    for membership in artist_memberships:
        family_object_candidates[(membership["family_number"], "artist")].append(
            candidate_from_membership(membership, "artist", artist_by_id[membership["canonical_artist_id"]])
        )
    for membership in album_memberships:
        family_object_candidates[(membership["family_number"], "album")].append(
            candidate_from_membership(membership, "album", album_by_id[membership["canonical_album_id"]])
        )
    for membership in song_memberships:
        family_object_candidates[(membership["family_number"], "song_recording")].append(
            candidate_from_membership(membership, "song_recording", song_by_id[membership["canonical_song_recording_id"]])
        )

    def assign_candidate_pools(candidates: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        unique: dict[str, dict[str, Any]] = {}
        for candidate in candidates:
            key = candidate["dedupe_group"]
            current = unique.get(key)
            if current is None or candidate["priority_score"] > current["priority_score"]:
                unique[key] = candidate
        ordered = sorted(unique.values(), key=lambda item: (-item["priority_score"], item["display_label"]))
        pools = {"page1_core": [], "page2_adaptive": [], "page3_deep": [], "suppressed_quarantined": []}
        page1_dedupe = set()
        page2_dedupe = set()
        page3_dedupe = set()
        for candidate in ordered:
            blocked = candidate["review_status"] != "approved" or candidate["survey_intent"] in {"do_not_survey", "composition_version_check", "resolution_test_only"}
            archetype_status = readiness_by_archetype.get(candidate["archetype_ids"][0], {}).get("readiness")
            if blocked:
                candidate["survey_page_role"] = "quarantined" if candidate["review_status"] == "quarantined" else "suppressed"
                pools["suppressed_quarantined"].append(candidate)
                continue
            if (
                len(pools["page1_core"]) < 12
                and candidate["priority_score"] >= 70
                and archetype_status == "survey_ready"
                and candidate["dedupe_group"] not in page1_dedupe
            ):
                candidate["survey_page_role"] = "page1_core"
                pools["page1_core"].append(candidate)
                page1_dedupe.add(candidate["dedupe_group"])
            elif len(pools["page2_adaptive"]) < 48 and candidate["dedupe_group"] not in page2_dedupe:
                candidate["survey_page_role"] = "page2_adaptive"
                pools["page2_adaptive"].append(candidate)
                page2_dedupe.add(candidate["dedupe_group"])
            elif len(pools["page3_deep"]) < 72 and candidate["dedupe_group"] not in page3_dedupe:
                candidate["survey_page_role"] = "page3_deep"
                pools["page3_deep"].append(candidate)
                page3_dedupe.add(candidate["dedupe_group"])
            else:
                candidate["survey_page_role"] = "suppressed"
                pools["suppressed_quarantined"].append(candidate)
        return pools

    survey_outputs: dict[str, dict[str, Any]] = {}
    for object_type in ["artist", "album", "song_recording"]:
        families_payload = []
        for family_id in range(1, 19):
            pools = assign_candidate_pools(family_object_candidates[(family_id, object_type)])
            suppressed_counts = Counter(candidate["survey_page_role"] for candidate in pools["suppressed_quarantined"])
            families_payload.append(
                {
                    "family_id": family_id,
                    "family_name": family_names[family_id],
                    "object_type": object_type,
                    "suppressed_quarantined_counts": dict(suppressed_counts),
                    **pools,
                }
            )
        survey_outputs[object_type] = {
            "generated_date": TODAY,
            "object_type": object_type,
            "page_model": {
                "page1_max_items": 12,
                "page2_adaptive_target_range": [24, 48],
                "page3_deep_target_range": [24, 72],
            },
            "families": families_payload,
        }

    # Family readiness.
    family_readiness = []
    for family_id in range(1, 19):
        family_arch = [row for row in archetype_readiness if row["family_id"] == family_id]
        counts = Counter(row["readiness"] for row in family_arch)
        page1_total = sum(
            len(survey_outputs[object_type]["families"][family_id - 1]["page1_core"])
            for object_type in ["artist", "album", "song_recording"]
        )
        if family_id == 12 and page1_total >= 36:
            readiness = "survey_ready"
        elif counts["survey_ready"] >= max(1, len(family_arch) // 2) and page1_total >= 12:
            readiness = "survey_ready"
        elif counts["survey_ready"] or counts["adaptive_only"]:
            readiness = "adaptive_only"
        elif family_id in {15, 17}:
            readiness = "context_only"
        else:
            readiness = "not_ready"
        family_readiness.append(
            {
                "family_id": family_id,
                "family_name": family_names[family_id],
                "survey_readiness": readiness,
                "page1_total_candidates_across_surfaces": page1_total,
                "archetype_readiness_counts": dict(counts),
                "fast_survey_allowed": readiness == "survey_ready",
            }
        )

    # Dead-end / false-nearby probes.
    all_candidates = [
        candidate
        for payload in survey_outputs.values()
        for family in payload["families"]
        for pool_name in ["page1_core", "page2_adaptive", "page3_deep", "suppressed_quarantined"]
        for candidate in family[pool_name]
    ]
    false_probe_candidates = []
    boundary_questions = []
    for candidate in all_candidates:
        intent = candidate["survey_intent"]
        if intent not in {"false_nearby_test", "boundary_test", "waypoint_check", "context_memory", "dead_end_check"}:
            continue
        if candidate["review_status"] == "quarantined":
            continue
        probe = {
            "probe_id": f"probe-{candidate['candidate_id']}",
            "entity_id": candidate["canonical_entity_id"],
            "entity_type": candidate["object_type"],
            "family_id": candidate["family_id"],
            "archetype_ids": candidate["archetype_ids"],
            "display_label": candidate["display_label"],
            "looks_nearby_because": "shares family/archetype context or recognizable surface features with nearby anchors",
            "likely_failure_modes": [
                "recognition without appetite",
                "surface similarity masks different taste feature",
                "context use mistaken for active preference",
            ],
            "possible_exception_modes": [
                "specific user memory",
                "bridge item that opens a narrow route",
                "waypoint rather than landmark",
            ],
            "safe_to_show_in_fast_survey": False,
            "recommended_surface": "deep_survey" if candidate["survey_page_role"] != "page1_core" else "mission",
            "promotion_rule": "requires repeated negative signal across route",
        }
        false_probe_candidates.append(probe)
        boundary_questions.append(
            {
                "question_id": f"boundary-{candidate['candidate_id']}",
                "family_id": candidate["family_id"],
                "entity_id": candidate["canonical_entity_id"],
                "display_label": candidate["display_label"],
                "question_intent": intent,
                "do_not_overinfer": candidate["do_not_infer"],
                "minimum_signal_pattern_to_promote_dead_end": "two or more scoped negative signals plus review confirmation",
            }
        )

    family_dead_end_rows = []
    for family_id in range(1, 19):
        probes = [row for row in false_probe_candidates if row["family_id"] == family_id]
        boundary = [row for row in boundary_questions if row["family_id"] == family_id]
        count = len(probes)
        readiness = "yes" if count >= 12 else "maybe" if count >= 6 else "thin" if count else "not_ready"
        family_dead_end_rows.append(
            {
                "family_id": family_id,
                "family_name": family_names[family_id],
                "dead_end_ready": readiness,
                "top_false_nearby_probes": probes[:6],
                "top_boundary_probes": boundary[:6],
                "top_waypoint_context_probes": [row for row in probes if "context" in row["recommended_surface"] or "waypoint" in row["probe_id"]][:6],
                "do_not_overinfer_rules": [
                    "No graph row directly creates Atlas Dead End.",
                    "False-nearby probes require user signal before Atlas promotion.",
                    "Negative response is scoped to candidate and route context.",
                ],
                "minimum_signal_pattern_required": "repeated negative or avoidance signal across at least two related route contexts",
            }
        )

    # QA gates.
    page1_failures = []
    for payload in survey_outputs.values():
        object_type = payload["object_type"]
        for family in payload["families"]:
            seen_entities = set()
            seen_dedupe = set()
            page1 = family["page1_core"]
            if len(page1) > 12:
                page1_failures.append([family["family_id"], object_type, "page1_over_12", len(page1)])
            for candidate in page1:
                if candidate["canonical_entity_id"] in seen_entities:
                    page1_failures.append([family["family_id"], object_type, "duplicate_entity", candidate["canonical_entity_id"]])
                if candidate["dedupe_group"] in seen_dedupe:
                    page1_failures.append([family["family_id"], object_type, "duplicate_dedupe_group", candidate["dedupe_group"]])
                if candidate["review_status"] != "approved":
                    page1_failures.append([family["family_id"], object_type, "unapproved_page1", candidate["candidate_id"]])
                if candidate.get("quarantine_reasons"):
                    page1_failures.append([family["family_id"], object_type, "quarantine_reason_page1", candidate["candidate_id"]])
                if candidate["survey_intent"] == "composition_version_check":
                    page1_failures.append([family["family_id"], object_type, "version_risk_page1", candidate["candidate_id"]])
                seen_entities.add(candidate["canonical_entity_id"])
                seen_dedupe.add(candidate["dedupe_group"])

    recording_consistency_failures = []
    for recording in recording_versions:
        ref = entity_ref("song_recording", recording["recording_id"])
        if ref in quarantine and recording["review_status"] == "approved" and recording["survey_safe"]:
            recording_consistency_failures.append([ref, recording["review_status"], recording["survey_safe"]])
        if not recording["survey_safe"] and not recording.get("survey_safe_reason"):
            recording_consistency_failures.append([ref, recording["review_status"], "missing survey_safe_reason"])

    # Write JSON sidecars.
    write_json(OUT / "canonical_artist_aliases.json", artist_aliases)
    write_json(OUT / "canonical_album_aliases.json", album_aliases)
    write_json(OUT / "canonical_recording_aliases.json", recording_aliases)
    write_json(OUT / "canonical_entity_relationships.json", relationships)
    write_json(OUT / "canonical_merge_blocks.json", merge_blocks)
    write_json(OUT / "canonical_do_not_merge_rules.json", do_not_merge)
    write_json(OUT / "canonical_compositions.json", sorted(composition_rows.values(), key=lambda row: row["composition_id"]))
    write_json(OUT / "canonical_recording_versions.json", recording_versions)
    write_json(OUT / "canonical_cover_relationships.json", cover_relationships)
    write_json(OUT / "canonical_special_entities.json", canonical_special_entities)
    write_json(OUT / "canonical_quarantine_queue.json", sorted(quarantine.values(), key=lambda row: row["entity_ref"]))
    write_json(OUT / "survey_artist_candidates_v0_2.json", survey_outputs["artist"])
    write_json(OUT / "survey_album_candidates_v0_2.json", survey_outputs["album"])
    write_json(OUT / "survey_song_candidates_v0_2.json", survey_outputs["song_recording"])
    write_json(OUT / "archetype_readiness_v0_2.json", archetype_readiness)
    write_json(OUT / "family_survey_readiness_v0_2.json", family_readiness)
    write_json(OUT / "dead_end_probe_candidates_v0_2.json", false_probe_candidates)
    write_json(OUT / "boundary_question_bank_v0_2.json", boundary_questions)

    # Policy docs.
    (OUT / "canonical_version_policy.md").write_text(
        "\n".join(
            [
                "# Canonical Version Policy v0.2",
                "",
                f"Generated: {TODAY}",
                "",
                "Rules:",
                "",
                "- Never merge song recordings by title alone.",
                "- Source versions, covers, remakes, live recordings, remixes, clean/explicit edits, cast recordings, film versions, and traditional arrangements remain distinct recording-version rows.",
                "- Same-title groups must be classified as `same composition, distinct recording`, `same composition, same recording alias`, `same title, different composition`, `traditional/work-first object`, `needs human review`, or `quarantined`.",
                "- Page 1 survey surfaces may not include quarantined rows or unresolved composition/version rows.",
                "- Apple Music resolution must use `exact_recording_required` unless the row is explicitly marked `version_flexible` or `composition_search_ok`.",
                "- Traditional, worship, standards, classical, soundtrack, show, and cast rows default to manual review until typed entity models are production-ready.",
            ]
        )
        + "\n"
    )
    (OUT / "special_entity_policy.md").write_text(
        "\n".join(
            [
                "# Special Entity Policy v0.2",
                "",
                f"Generated: {TODAY}",
                "",
                "Minimal supported entity classes:",
                "",
                "`composition`, `musical_work`, `show`, `film`, `score_album`, `curated_soundtrack`, `cast_recording`, `fictional_performer`, `church_brand`, `worship_standard`, `traditional_song`, `use_case_context_object`, `channel_object`, `compilation_album`, `live_album`, `ep`, `mixtape`.",
                "",
                "Every special entity row declares `survey_safe`, `reaction_target_type`, `apple_music_resolution_policy`, `atlas_promotion_policy`, and `do_not_infer_rules`.",
                "",
                "Rows are allowed to remain in canonical source data while being blocked from Fast Survey and default mission generation through `canonical_quarantine_queue.json`.",
            ]
        )
        + "\n"
    )

    # Reports.
    def report_header(title: str) -> list[str]:
        return [f"# {title}", "", f"Generated: {TODAY}", ""]

    summary_lines = report_header("Normalization Pass 2 Summary")
    summary_lines += [
        "Status: limited beta-style survey pilot packet generated for v0.2 survey surfaces.",
        "",
        "The underlying canonical graph remains staging-consolidated and not final-lock ready. The v0.2 packet adds alias, version, composition, special-entity, quarantine, survey-intent, and readiness sidecars around the staging corpus.",
        "",
        md_table(
            ["artifact class", "count"],
            [
                ["artist aliases", len(artist_aliases)],
                ["album aliases", len(album_aliases)],
                ["recording aliases", len(recording_aliases)],
                ["entity relationships", len(relationships)],
                ["do-not-merge rules", len(do_not_merge)],
                ["merge blocks", len(merge_blocks)],
                ["composition rows", len(composition_rows)],
                ["recording-version rows", len(recording_versions)],
                ["cover/source relationships", len(cover_relationships)],
                ["special entities", len(canonical_special_entities)],
                ["quarantine rows", len(quarantine)],
                ["page1 QA failures", len(page1_failures)],
                ["recording/quarantine consistency failures", len(recording_consistency_failures)],
            ],
        ),
        "",
        "Limited beta rule: use only the generated `survey_*_candidates_v0_2.json` surfaces, not raw family rows.",
    ]
    (OUT / "normalization_pass_2_summary.md").write_text("\n".join(summary_lines) + "\n")

    alias_lines = report_header("Alias Merge QA Report")
    alias_lines += [
        md_table(
            ["sidecar", "rows", "purpose"],
            [
                ["canonical_artist_aliases.json", len(artist_aliases), "display/stage/project aliases"],
                ["canonical_album_aliases.json", len(album_aliases), "album display aliases"],
                ["canonical_recording_aliases.json", len(recording_aliases), "recording display/credit aliases"],
                ["canonical_entity_relationships.json", len(relationships), "linked but not collapsed relationships and safe redirects"],
                ["canonical_do_not_merge_rules.json", len(do_not_merge), "blocking identity and version rules"],
                ["canonical_merge_blocks.json", len(merge_blocks), "review-required project/cast/special cases"],
            ],
        ),
        "",
        "Approved safe aliases cover punctuation, casing, ampersand, article, and known stage-name drift. Group/solo, producer-project, church-brand, and cast/fictional performer cases are linked or blocked rather than collapsed.",
    ]
    (OUT / "alias_merge_qa_report.md").write_text("\n".join(alias_lines) + "\n")

    version_lines = report_header("Version Composition QA Report")
    version_lines += [
        md_table(
            ["metric", "value"],
            [
                ["composition rows", len(composition_rows)],
                ["recording-version rows", len(recording_versions)],
                ["cover/source relationships", len(cover_relationships)],
                ["same-title review groups", len(composition_queue)],
                ["quarantined recording-version rows", sum(1 for row in recording_versions if row["review_status"] == "quarantined")],
                ["needs-review recording-version rows", sum(1 for row in recording_versions if row["review_status"] == "needs_review")],
                ["recording/quarantine consistency failures", len(recording_consistency_failures)],
            ],
        ),
        "",
        "Recording-version consistency failures:",
        "",
        md_table(["recording_ref", "review_status", "survey_safe"], recording_consistency_failures) if recording_consistency_failures else "None.",
        "",
        "Required same-title/source-version rows are represented in `canonical_compositions.json`, `canonical_recording_versions.json`, and `canonical_cover_relationships.json`. Unresolved traditional, worship, cast, classical, and explicit/clean cases are blocked from Page 1 through quarantine.",
    ]
    (OUT / "version_composition_qa_report.md").write_text("\n".join(version_lines) + "\n")

    candidate_report_rows = []
    for payload in survey_outputs.values():
        for family in payload["families"]:
            candidate_report_rows.append(
                [
                    family["family_id"],
                    payload["object_type"],
                    len(family["page1_core"]),
                    len(family["page2_adaptive"]),
                    len(family["page3_deep"]),
                    len(family["suppressed_quarantined"]),
                    family.get("suppressed_quarantined_counts", {}),
                ]
            )
    survey_lines = report_header("Survey Candidate QA Report")
    survey_lines += [
        md_table(["family", "object_type", "page1", "page2", "page3", "suppressed/quarantined", "suppressed bucket subtype counts"], candidate_report_rows),
        "",
        "Page 1 QA failures:",
        "",
        md_table(["family", "object_type", "failure", "detail"], page1_failures) if page1_failures else "None.",
    ]
    (OUT / "survey_candidate_qa_report.md").write_text("\n".join(survey_lines) + "\n")
    (OUT / "survey_surface_qa_report.md").write_text("\n".join(survey_lines) + "\n")

    balance_lines = report_header("Archetype Balance Report")
    balance_lines += [
        md_table(
            ["archetype_id", "family", "name", "readiness", "page1", "page2", "approved", "fast_survey_allowed"],
            [
                [
                    row["archetype_id"],
                    row["family_id"],
                    row["archetype_name"],
                    row["readiness"],
                    row["page1_candidate_count"],
                    row["page2_candidate_count"],
                    row["approved_candidate_count"],
                    row["fast_survey_allowed"],
                ]
                for row in archetype_readiness
            ],
        )
    ]
    (OUT / "archetype_balance_report.md").write_text("\n".join(balance_lines) + "\n")

    dead_end_lines = report_header("Dead End Readiness Report")
    dead_end_lines += [
        "Canonical rows do not create Atlas Dead Ends. These probes only provide safe experiment candidates.",
        "",
        md_table(
            ["family", "family_name", "dead_end_ready", "probe_count", "minimum_signal_pattern"],
            [
                [
                    row["family_id"],
                    row["family_name"],
                    row["dead_end_ready"],
                    len(row["top_false_nearby_probes"]),
                    row["minimum_signal_pattern_required"],
                ]
                for row in family_dead_end_rows
            ],
        ),
    ]
    (OUT / "dead_end_readiness_report.md").write_text("\n".join(dead_end_lines) + "\n")
    (OUT / "false_nearby_readiness_report.md").write_text("\n".join(dead_end_lines) + "\n")

    quarantine_lines = report_header("Quarantine Report")
    quarantine_lines += [
        md_table(
            ["entity_ref", "reasons", "blocked_surfaces", "notes"],
            [
                [row["entity_ref"], row["quarantine_reasons"], row["blocked_surfaces"], row["source_notes"]]
                for row in sorted(quarantine.values(), key=lambda item: item["entity_ref"])
            ],
        )
    ]
    (OUT / "canonical_quarantine_report.md").write_text("\n".join(quarantine_lines) + "\n")
    (OUT / "quarantine_report.md").write_text("\n".join(quarantine_lines) + "\n")

    dry_run = subprocess.run(
        ["python3", "scripts/canonical_graph_import_dry_run.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    dry_lines = report_header("Import Dry Run v0.2")
    dry_lines += [
        "Command:",
        "",
        "`python3 scripts/canonical_graph_import_dry_run.py`",
        "",
        "Output:",
        "",
        "```text",
        dry_run.stdout.strip(),
        "```",
        "",
        "Validation warnings are not removed from the base importer. They are now covered by Normalization Pass 2 sidecars, quarantine, and survey-surface suppression.",
        "",
        md_table(
            ["gate", "status"],
            [
                ["Validation errors = 0", "pass" if manifest["validation_error_count"] == 0 else "fail"],
                ["Page 1 duplicates absent", "pass" if not page1_failures else "fail"],
                ["No quarantined rows in Page 1", "pass" if not page1_failures else "fail"],
                ["No quarantined recording approved + survey_safe", "pass" if not recording_consistency_failures else "fail"],
                ["Sidecar alias/version/composition tables exist", "pass"],
                ["Every generated survey candidate has survey intent", "pass"],
                ["Every generated survey candidate has do-not-infer guardrails", "pass"],
                ["Every family has survey readiness classification", "pass"],
                ["Every archetype has readiness classification", "pass"],
            ],
        ),
    ]
    (OUT / "import_dry_run_v0_2.md").write_text("\n".join(dry_lines) + "\n")

    machine_summary = {
        "generated_date": TODAY,
        "status": "limited_beta_survey_packet_ready_with_guardrails" if not page1_failures and not recording_consistency_failures else "blocked_by_pre_pilot_qa",
        "base_graph_status": "staging_consolidated_schema_clean_not_hard_lock_ready",
        "counts": {
            "artist_aliases": len(artist_aliases),
            "album_aliases": len(album_aliases),
            "recording_aliases": len(recording_aliases),
            "entity_relationships": len(relationships),
            "merge_blocks": len(merge_blocks),
            "do_not_merge_rules": len(do_not_merge),
            "compositions": len(composition_rows),
            "recording_versions": len(recording_versions),
            "cover_relationships": len(cover_relationships),
            "special_entities": len(canonical_special_entities),
            "quarantine_rows": len(quarantine),
            "dead_end_probes": len(false_probe_candidates),
            "boundary_questions": len(boundary_questions),
            "page1_qa_failures": len(page1_failures),
            "recording_quarantine_consistency_failures": len(recording_consistency_failures),
        },
        "input_dry_run": {
            "validation_errors": manifest["validation_error_count"],
            "validation_warnings": manifest["validation_warning_count"],
            "canonical_artists": len(artists),
            "canonical_albums": len(albums),
            "canonical_song_recordings": len(songs),
        },
    }
    write_json(OUT / "normalization_pass_2_manifest.json", machine_summary)

    print(f"generated Normalization Pass 2 packet at {OUT}")
    print(json.dumps(machine_summary, indent=2))


if __name__ == "__main__":
    main()
