#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_ROOT = REPO_ROOT / "data/canonical_graph"
DEFAULT_OUTPUT_ROOT = DEFAULT_INPUT_ROOT / "import_dry_run"
DEFAULT_EXPECTED_FAMILY_COUNT = 18

ROLE_ENUM = {
    "album_anchor",
    "anchor",
    "artist_anchor",
    "boundary",
    "bridge",
    "compilation_gateway",
    "contrast",
    "deepening",
    "false_nearby",
    "gateway",
    "live_gateway",
    "song_first",
}
RECOGNITION_ENUM = {"mass", "high", "medium", "low", "cult"}
SURVEY_ENUM = {"core", "standard", "edge", "suppress"}
ALBUM_OBJECT_TYPE_ENUM = {"studio_album", "live_album", "compilation", "soundtrack", "ep"}
ARTIST_SURVEY_STATUS_ENUM = {
    "artist_survey_worthy",
    "song_survey_first",
    "song_survey_only",
}

ARTIST_FIELDS = [
    "archetype_id",
    "artist_name",
    "proposed_artist_id",
    "existing_seed",
    "recognition_tier",
    "survey_tier",
    "roles",
    "archetype_membership_weight",
    "inclusion_reason",
    "object_specificity_note",
    "likely_canonical_albums",
    "likely_canonical_songs",
    "consolidation_warning",
]
ALBUM_FIELDS = [
    "archetype_id",
    "album_title",
    "artist_name",
    "proposed_album_id",
    "existing_seed",
    "release_year",
    "album_object_type",
    "recognition_tier",
    "survey_tier",
    "roles",
    "archetype_membership_weight",
    "inclusion_reason",
    "consolidation_warning",
]
SONG_FIELDS = [
    "archetype_id",
    "song_title",
    "artist_name",
    "proposed_song_id",
    "existing_seed",
    "release_year",
    "recognition_tier",
    "survey_tier",
    "roles",
    "archetype_membership_weight",
    "inclusion_reason",
    "artist_survey_status",
    "consolidation_warning",
]

RANK_RECOGNITION = {"mass": 5, "high": 4, "medium": 3, "low": 2, "cult": 1}
RANK_SURVEY = {"core": 4, "standard": 3, "edge": 2, "suppress": 1}
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def slugify(value: str) -> str:
    value = value.lower().replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return re.sub(r"-+", "-", value).strip("-")


def family_number_from_path(path: Path) -> int:
    match = re.search(r"family_(\d+)", str(path))
    if not match:
        raise ValueError(f"Cannot infer family number from {path}")
    return int(match.group(1))


def discover_family_files(input_root: Path) -> list[Path]:
    files = sorted(
        input_root.glob("family_*/normalized_family_*.json"),
        key=family_number_from_path,
    )
    if not files:
        raise FileNotFoundError(f"No normalized family files found under {input_root}")
    return files


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def validate_row(
    *,
    row: dict[str, Any],
    fields: list[str],
    id_field: str,
    kind: str,
    family_number: int,
    errors: list[str],
    warnings: list[str],
    strict_years: bool,
) -> None:
    row_id = row.get(id_field, "<missing>")
    prefix = f"family {family_number} {kind} {row_id}"
    for field in fields:
        if field not in row:
            errors.append(f"{prefix}: missing required field `{field}`")
    if not isinstance(row.get(id_field), str) or not SLUG_RE.match(str(row.get(id_field))):
        errors.append(f"{prefix}: `{id_field}` is not lowercase kebab-case")
    if row.get("recognition_tier") not in RECOGNITION_ENUM:
        errors.append(f"{prefix}: invalid recognition_tier `{row.get('recognition_tier')}`")
    if row.get("survey_tier") not in SURVEY_ENUM:
        errors.append(f"{prefix}: invalid survey_tier `{row.get('survey_tier')}`")
    roles = row.get("roles")
    if not isinstance(roles, list) or any(role not in ROLE_ENUM for role in roles):
        errors.append(f"{prefix}: roles must be a list of normalized role enum values")
    weight = row.get("archetype_membership_weight")
    if not isinstance(weight, (int, float)) or weight < 0 or weight > 1:
        errors.append(f"{prefix}: archetype_membership_weight must be 0.00-1.00")
    if kind == "album":
        if row.get("album_object_type") not in ALBUM_OBJECT_TYPE_ENUM:
            errors.append(f"{prefix}: invalid album_object_type `{row.get('album_object_type')}`")
        if not isinstance(row.get("release_year"), int):
            message = f"{prefix}: release_year is `{row.get('release_year')}`"
            (errors if strict_years else warnings).append(message)
    if kind == "song":
        if row.get("artist_survey_status") not in ARTIST_SURVEY_STATUS_ENUM:
            errors.append(
                f"{prefix}: invalid artist_survey_status `{row.get('artist_survey_status')}`"
            )
        if not isinstance(row.get("release_year"), int):
            message = f"{prefix}: release_year is `{row.get('release_year')}`"
            (errors if strict_years else warnings).append(message)


def pick_best(values: list[str], rank: dict[str, int]) -> str:
    return max(values, key=lambda value: rank.get(value, 0))


def collect_entity(
    entities: dict[str, dict[str, Any]],
    *,
    entity_id: str,
    family_number: int,
    entity_type: str,
    row: dict[str, Any],
    name_field: str,
    extra_fields: dict[str, Any],
) -> None:
    entity = entities.setdefault(
        entity_id,
        {
            f"canonical_{entity_type}_id": entity_id,
            "display_name": row[name_field],
            "family_numbers": set(),
            "archetype_ids": set(),
            "recognition_tiers": [],
            "survey_tiers": [],
            "roles": set(),
            "existing_seed_any": False,
            "source_row_count": 0,
            "source_names": set(),
            **extra_fields,
        },
    )
    entity["family_numbers"].add(family_number)
    entity["archetype_ids"].add(row["archetype_id"])
    entity["recognition_tiers"].append(row["recognition_tier"])
    entity["survey_tiers"].append(row["survey_tier"])
    entity["roles"].update(row["roles"])
    entity["existing_seed_any"] = bool(entity["existing_seed_any"] or row["existing_seed"])
    entity["source_row_count"] += 1
    entity["source_names"].add(row[name_field])


def finalize_entities(
    entities: dict[str, dict[str, Any]],
    entity_type: str,
    conflict_fields: list[str],
) -> tuple[list[dict[str, Any]], list[str]]:
    conflicts: list[str] = []
    finalized: list[dict[str, Any]] = []
    for entity_id, entity in sorted(entities.items()):
        source_names = sorted(entity.pop("source_names"))
        if len(source_names) > 1:
            conflicts.append(
                f"{entity_type} `{entity_id}` has multiple display/source names: "
                + "; ".join(source_names)
            )
        for field in conflict_fields:
            values = entity.get(field)
            if isinstance(values, set) and len(values) > 1:
                conflicts.append(
                    f"{entity_type} `{entity_id}` has conflicting `{field}` values: "
                    + "; ".join(str(value) for value in sorted(values, key=str))
                )
        entity["family_numbers"] = sorted(entity["family_numbers"])
        entity["archetype_ids"] = sorted(entity["archetype_ids"])
        entity["roles"] = sorted(entity["roles"])
        entity["best_recognition_tier"] = pick_best(entity.pop("recognition_tiers"), RANK_RECOGNITION)
        entity["best_survey_tier"] = pick_best(entity.pop("survey_tiers"), RANK_SURVEY)
        for field, value in list(entity.items()):
            if isinstance(value, set):
                entity[field] = sorted(value, key=str)
        finalized.append(entity)
    return finalized, conflicts


def membership_id(family_number: int, object_type: str, object_id: str, archetype_id: str) -> str:
    return f"family-{family_number}-{object_type}-{archetype_id}-{object_id}"


def build_import_model(
    family_docs: list[tuple[int, dict[str, Any]]],
    strict_years: bool,
) -> tuple[dict[str, Any], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    artist_entities: dict[str, dict[str, Any]] = {}
    album_entities: dict[str, dict[str, Any]] = {}
    song_entities: dict[str, dict[str, Any]] = {}
    artist_memberships: list[dict[str, Any]] = []
    album_memberships: list[dict[str, Any]] = []
    song_memberships: list[dict[str, Any]] = []

    for family_number, doc in family_docs:
        for row in doc.get("artists", []):
            validate_row(
                row=row,
                fields=ARTIST_FIELDS,
                id_field="proposed_artist_id",
                kind="artist",
                family_number=family_number,
                errors=errors,
                warnings=warnings,
                strict_years=strict_years,
            )
            artist_id = row["proposed_artist_id"]
            collect_entity(
                artist_entities,
                entity_id=artist_id,
                family_number=family_number,
                entity_type="artist",
                row=row,
                name_field="artist_name",
                extra_fields={
                    "likely_canonical_albums": set(row.get("likely_canonical_albums", [])),
                    "likely_canonical_songs": set(row.get("likely_canonical_songs", [])),
                },
            )
            artist_entities[artist_id]["likely_canonical_albums"].update(
                row.get("likely_canonical_albums", [])
            )
            artist_entities[artist_id]["likely_canonical_songs"].update(
                row.get("likely_canonical_songs", [])
            )
            artist_memberships.append(
                {
                    "membership_id": membership_id(
                        family_number, "artist", artist_id, row["archetype_id"]
                    ),
                    "canonical_artist_id": artist_id,
                    "family_number": family_number,
                    "archetype_id": row["archetype_id"],
                    "recognition_tier": row["recognition_tier"],
                    "survey_tier": row["survey_tier"],
                    "roles": row["roles"],
                    "archetype_membership_weight": row["archetype_membership_weight"],
                    "existing_seed": row["existing_seed"],
                    "object_specificity_note": row["object_specificity_note"],
                    "inclusion_reason": row["inclusion_reason"],
                    "consolidation_warning": row["consolidation_warning"],
                }
            )

        for row in doc.get("albums", []):
            validate_row(
                row=row,
                fields=ALBUM_FIELDS,
                id_field="proposed_album_id",
                kind="album",
                family_number=family_number,
                errors=errors,
                warnings=warnings,
                strict_years=strict_years,
            )
            album_id = row["proposed_album_id"]
            collect_entity(
                album_entities,
                entity_id=album_id,
                family_number=family_number,
                entity_type="album",
                row=row,
                name_field="album_title",
                extra_fields={
                    "album_title": row["album_title"],
                    "artist_names": {row["artist_name"]},
                    "release_years": {row.get("release_year")},
                    "album_object_types": {row.get("album_object_type")},
                },
            )
            album_entities[album_id]["artist_names"].add(row["artist_name"])
            album_entities[album_id]["release_years"].add(row.get("release_year"))
            album_entities[album_id]["album_object_types"].add(row.get("album_object_type"))
            album_memberships.append(
                {
                    "membership_id": membership_id(
                        family_number, "album", album_id, row["archetype_id"]
                    ),
                    "canonical_album_id": album_id,
                    "family_number": family_number,
                    "archetype_id": row["archetype_id"],
                    "recognition_tier": row["recognition_tier"],
                    "survey_tier": row["survey_tier"],
                    "roles": row["roles"],
                    "archetype_membership_weight": row["archetype_membership_weight"],
                    "existing_seed": row["existing_seed"],
                    "inclusion_reason": row["inclusion_reason"],
                    "consolidation_warning": row["consolidation_warning"],
                }
            )

        for row in doc.get("songs", []):
            validate_row(
                row=row,
                fields=SONG_FIELDS,
                id_field="proposed_song_id",
                kind="song",
                family_number=family_number,
                errors=errors,
                warnings=warnings,
                strict_years=strict_years,
            )
            song_id = row["proposed_song_id"]
            collect_entity(
                song_entities,
                entity_id=song_id,
                family_number=family_number,
                entity_type="song_recording",
                row=row,
                name_field="song_title",
                extra_fields={
                    "song_title": row["song_title"],
                    "artist_names": {row["artist_name"]},
                    "release_years": {row.get("release_year")},
                    "composition_key": slugify(row["song_title"]),
                },
            )
            song_entities[song_id]["artist_names"].add(row["artist_name"])
            song_entities[song_id]["release_years"].add(row.get("release_year"))
            song_memberships.append(
                {
                    "membership_id": membership_id(
                        family_number, "song", song_id, row["archetype_id"]
                    ),
                    "canonical_song_recording_id": song_id,
                    "family_number": family_number,
                    "archetype_id": row["archetype_id"],
                    "recognition_tier": row["recognition_tier"],
                    "survey_tier": row["survey_tier"],
                    "roles": row["roles"],
                    "archetype_membership_weight": row["archetype_membership_weight"],
                    "existing_seed": row["existing_seed"],
                    "artist_survey_status": row["artist_survey_status"],
                    "inclusion_reason": row["inclusion_reason"],
                    "consolidation_warning": row["consolidation_warning"],
                }
            )

    artists, artist_conflicts = finalize_entities(artist_entities, "artist", [])
    albums, album_conflicts = finalize_entities(
        album_entities, "album", ["artist_names", "release_years", "album_object_types"]
    )
    songs, song_conflicts = finalize_entities(
        song_entities, "song_recording", ["artist_names", "release_years"]
    )
    warnings.extend(artist_conflicts)
    warnings.extend(album_conflicts)
    warnings.extend(song_conflicts)

    model = {
        "canonical_artists": artists,
        "canonical_albums": albums,
        "canonical_song_recordings": songs,
        "artist_archetype_memberships": sorted(
            artist_memberships, key=lambda row: row["membership_id"]
        ),
        "album_archetype_memberships": sorted(
            album_memberships, key=lambda row: row["membership_id"]
        ),
        "song_archetype_memberships": sorted(
            song_memberships, key=lambda row: row["membership_id"]
        ),
    }
    return model, errors, warnings


def duplicate_count(rows: list[dict[str, Any]], field: str) -> int:
    counts = Counter(row[field] for row in rows)
    return sum(1 for count in counts.values() if count > 1)


def composition_review_queue(song_recordings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_composition: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in song_recordings:
        by_composition[row["composition_key"]].append(row)

    queue: list[dict[str, Any]] = []
    for composition_key, rows in sorted(by_composition.items()):
        artists = sorted({artist for row in rows for artist in row.get("artist_names", [])})
        ids = sorted(row["canonical_song_recording_id"] for row in rows)
        if len(ids) > 1 and len(artists) > 1:
            queue.append(
                {
                    "composition_key": composition_key,
                    "song_title": rows[0]["song_title"],
                    "artist_names": artists,
                    "canonical_song_recording_ids": ids,
                    "reason": "Same normalized song title appears across multiple artists; review composition versus recording split.",
                }
            )
    return queue


def collect_warning_snippets(input_root: Path) -> list[dict[str, str]]:
    patterns = re.compile(
        r"(do not merge|disambiguate|alias|distinct|traditional|manual|pending|split rules|version)",
        re.IGNORECASE,
    )
    snippets: list[dict[str, str]] = []
    for path in sorted(input_root.glob("family_*/import_warnings.md")):
        family_number = family_number_from_path(path)
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if patterns.search(line):
                snippets.append(
                    {
                        "family_number": str(family_number),
                        "source": str(path.relative_to(REPO_ROOT)),
                        "line": str(line_number),
                        "note": line.strip(),
                    }
                )
    return snippets


def write_report(
    output_root: Path,
    *,
    family_docs: list[tuple[int, dict[str, Any]]],
    model: dict[str, Any],
    errors: list[str],
    warnings: list[str],
    composition_queue: list[dict[str, Any]],
    warning_snippets: list[dict[str, str]],
    expected_family_count: int,
) -> None:
    remaining_family_count = max(expected_family_count - len(family_docs), 0)
    family_rows = []
    for family_number, doc in family_docs:
        family_rows.append(
            {
                "family_number": family_number,
                "family_name": doc.get("metadata", {}).get("family_name", ""),
                "artists": len(doc.get("artists", [])),
                "albums": len(doc.get("albums", [])),
                "songs": len(doc.get("songs", [])),
                "total": len(doc.get("artists", []))
                + len(doc.get("albums", []))
                + len(doc.get("songs", [])),
            }
        )

    lines = [
        "# Canonical Graph Import Dry Run",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "## Status",
        "",
        f"- Validation errors: {len(errors)}",
        f"- Validation warnings: {len(warnings)}",
        f"- Composition/title review rows: {len(composition_queue)}",
        f"- Imported family files: {len(family_docs)}",
        f"- Expected full corpus: {expected_family_count} families",
        f"- Families remaining: {remaining_family_count}",
        "",
        "## Family Inputs",
        "",
        "| family | scope | artists | albums | songs | total rows |",
        "|---:|---|---:|---:|---:|---:|",
    ]
    for row in family_rows:
        lines.append(
            f"| {row['family_number']} | {row['family_name']} | {row['artists']} | "
            f"{row['albums']} | {row['songs']} | {row['total']} |"
        )

    lines += [
        "",
        "## Emitted Tables",
        "",
        "| table | rows |",
        "|---|---:|",
        f"| canonical_artists.json | {len(model['canonical_artists'])} |",
        f"| canonical_albums.json | {len(model['canonical_albums'])} |",
        f"| canonical_song_recordings.json | {len(model['canonical_song_recordings'])} |",
        f"| artist_archetype_memberships.json | {len(model['artist_archetype_memberships'])} |",
        f"| album_archetype_memberships.json | {len(model['album_archetype_memberships'])} |",
        f"| song_archetype_memberships.json | {len(model['song_archetype_memberships'])} |",
        "",
        "## Duplicate Membership Signal",
        "",
        "| source rows | duplicate canonical IDs | note |",
        "|---|---:|---|",
        f"| artists | {duplicate_count(model['artist_archetype_memberships'], 'canonical_artist_id')} | Expected when one artist belongs to multiple archetypes/families. |",
        f"| albums | {duplicate_count(model['album_archetype_memberships'], 'canonical_album_id')} | Expected for shared album gateways. |",
        f"| songs | {duplicate_count(model['song_archetype_memberships'], 'canonical_song_recording_id')} | Expected for shared recordings; title collisions still require review. |",
        "",
        "## Warnings",
        "",
    ]
    if warnings:
        for warning in warnings[:200]:
            lines.append(f"- {warning}")
        if len(warnings) > 200:
            lines.append(f"- {len(warnings) - 200} additional warnings omitted from report; see manifest JSON.")
    else:
        lines.append("- None.")

    lines += ["", "## Errors", ""]
    if errors:
        for error in errors:
            lines.append(f"- {error}")
    else:
        lines.append("- None.")

    lines += [
        "",
        "## Next Dispatch Guidance",
        "",
        f"- Use the emitted canonical entity tables and membership tables as the import contract for the remaining {remaining_family_count} families.",
        "- Do not import family rows directly as unique entities; always route through canonical entity IDs plus membership rows.",
        "- Keep the composition review queue as a human QA queue, not an automatic merge list.",
    ]

    (output_root / "import_dry_run_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    queue_lines = [
        "# Merge Review Queue",
        "",
        "This queue is generated from title collisions and import-warning snippets. It is intentionally conservative.",
        "",
        "## Same-Title Song Recording Review",
        "",
        "| composition_key | song_title | artists | canonical_song_recording_ids | reason |",
        "|---|---|---|---|---|",
    ]
    for item in composition_queue:
        queue_lines.append(
            "| {composition_key} | {song_title} | {artists} | {ids} | {reason} |".format(
                composition_key=item["composition_key"],
                song_title=item["song_title"].replace("|", "\\|"),
                artists="; ".join(item["artist_names"]).replace("|", "\\|"),
                ids="; ".join(item["canonical_song_recording_ids"]),
                reason=item["reason"],
            )
        )
    queue_lines += [
        "",
        "## Warning Snippets",
        "",
        "| family | source | line | note |",
        "|---:|---|---:|---|",
    ]
    for item in warning_snippets:
        note = item["note"].replace("|", "\\|")
        queue_lines.append(
            f"| {item['family_number']} | `{item['source']}` | {item['line']} | "
            f"{note} |"
        )
    (output_root / "merge_review_queue.md").write_text(
        "\n".join(queue_lines) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate normalized canonical graph family files and emit dry-run import tables."
    )
    parser.add_argument(
        "--input-root",
        type=Path,
        default=DEFAULT_INPUT_ROOT,
        help="Directory containing family_*/normalized_family_*.json files.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Directory where dry-run import artifacts are written.",
    )
    parser.add_argument(
        "--strict-years",
        action="store_true",
        help="Treat missing album/song release_year values as validation errors instead of warnings.",
    )
    parser.add_argument(
        "--expected-family-count",
        type=int,
        default=DEFAULT_EXPECTED_FAMILY_COUNT,
        help="Expected number of total family packets in the finished corpus.",
    )
    args = parser.parse_args()

    family_files = discover_family_files(args.input_root)
    family_docs = [(family_number_from_path(path), load_json(path)) for path in family_files]
    model, errors, warnings = build_import_model(family_docs, args.strict_years)

    args.output_root.mkdir(parents=True, exist_ok=True)
    write_json(args.output_root / "canonical_artists.json", model["canonical_artists"])
    write_json(args.output_root / "canonical_albums.json", model["canonical_albums"])
    write_json(
        args.output_root / "canonical_song_recordings.json",
        model["canonical_song_recordings"],
    )
    write_json(
        args.output_root / "artist_archetype_memberships.json",
        model["artist_archetype_memberships"],
    )
    write_json(
        args.output_root / "album_archetype_memberships.json",
        model["album_archetype_memberships"],
    )
    write_json(
        args.output_root / "song_archetype_memberships.json",
        model["song_archetype_memberships"],
    )

    composition_queue = composition_review_queue(model["canonical_song_recordings"])
    warning_snippets = collect_warning_snippets(args.input_root)
    write_json(args.output_root / "composition_review_queue.json", composition_queue)
    write_json(args.output_root / "warning_snippets.json", warning_snippets)

    manifest = {
        "generated_date": date.today().isoformat(),
        "status": "blocked_by_errors" if errors else "dry_run_ready_with_warnings",
        "family_count": len(family_docs),
        "expected_family_count": args.expected_family_count,
        "remaining_family_count": max(args.expected_family_count - len(family_docs), 0),
        "family_numbers": [family_number for family_number, _ in family_docs],
        "input_files": [str(path.relative_to(REPO_ROOT)) for path in family_files],
        "validation_error_count": len(errors),
        "validation_warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "entity_counts": {
            "canonical_artists": len(model["canonical_artists"]),
            "canonical_albums": len(model["canonical_albums"]),
            "canonical_song_recordings": len(model["canonical_song_recordings"]),
        },
        "membership_counts": {
            "artist_archetype_memberships": len(model["artist_archetype_memberships"]),
            "album_archetype_memberships": len(model["album_archetype_memberships"]),
            "song_archetype_memberships": len(model["song_archetype_memberships"]),
        },
        "composition_review_count": len(composition_queue),
        "warning_snippet_count": len(warning_snippets),
    }
    write_json(args.output_root / "canonical_graph_manifest.json", manifest)

    write_report(
        args.output_root,
        family_docs=family_docs,
        model=model,
        errors=errors,
        warnings=warnings,
        composition_queue=composition_queue,
        warning_snippets=warning_snippets,
        expected_family_count=args.expected_family_count,
    )

    print(
        "canonical graph dry run: "
        f"{len(family_docs)} families, "
        f"{len(model['canonical_artists'])} artists, "
        f"{len(model['canonical_albums'])} albums, "
        f"{len(model['canonical_song_recordings'])} song recordings, "
        f"{len(errors)} errors, {len(warnings)} warnings"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
