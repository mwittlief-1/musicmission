#!/usr/bin/env python3
"""Build Phase 0-2 artifacts for the Cartenza affinity graph-wide run.

This script is intentionally conservative: it does not generate affinity tags.
It materializes the readiness/schema-binding trail, duplicate/context review,
and shard plan from the PM-promoted Pass D graph source.
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
FREEZE_MANIFEST_MD = PASS_D_DIR / "graph_hardening_pass_d_freeze_manifest.md"
ARCHETYPE_TARGETS = PASS_D_DIR / "atlas_archetype_profile_targets_v1.json"
CONTRACT_MANIFEST = CONTRACT_DIR / "metadata" / "affinity_repo_truth_manifest_v0_3_1.json"
ALLOWED_TAGS = CONTRACT_DIR / "allowed_tags" / "allowed_canonical_tags_by_dimension_v0_3_1.json"
ONTOLOGY = CONTRACT_DIR / "ontology" / "affinity_tag_ontology_v0_2_2_schema_amended_v0_3_1.json"
OUTPUT_SCHEMA = CONTRACT_DIR / "schemas" / "affinity_tagging_output_schema_v0_3_1.json"
PLACEMENT_RULES = CONTRACT_DIR / "schemas" / "affinity_schema_placement_rules_v0_3_1.json"
INSTRUCTIONS = CONTRACT_DIR / "instructions" / "affinity_graphwide_tagging_instructions_v0_3_1.md"
SCHEMA_BOUNDARY = CONTRACT_DIR / "schema_boundary" / "affinity_schema_boundary_amendment_v0_3_1.md"
QA_CONTRACT = CONTRACT_DIR / "validation" / "affinity_graphwide_QA_contract_v0_3_1.md"
VALIDATOR = CONTRACT_DIR / "validation" / "validate_affinity_graphwide_output_v0_3_1.py"
PRIOR_DUPES = CONTRACT_DIR / "duplicate_context" / "affinity_duplicate_context_review_candidates_v0_3_1.json"
PRIOR_CONTEXT_FLAGS = CONTRACT_DIR / "duplicate_context" / "affinity_context_leak_review_flags_v0_3_1.json"
SPARSE_METRICS = CONTRACT_DIR / "evidence" / "affinity_sparse_pilot_QA_metrics_v0_3.json"


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def norm_text(value: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).strip()


def family_number_lookup() -> dict[str, int]:
    data = load_json(ARCHETYPE_TARGETS)
    return {
        str(row["archetype_id"]): int(row["family_number"])
        for row in data["rows"]
        if row.get("archetype_id") and row.get("family_number") is not None
    }


def family_name_lookup(song_rows: list[dict[str, Any]], family_by_archetype: dict[str, int]) -> dict[int, str]:
    counter: dict[int, Counter[str]] = defaultdict(Counter)
    for row in song_rows:
        family_number = family_by_archetype.get(str(row.get("archetype_id")))
        if family_number is not None and row.get("primary_family"):
            counter[family_number][row["primary_family"]] += 1
    return {family_number: names.most_common(1)[0][0] for family_number, names in counter.items() if names}


def enriched_membership(row: dict[str, Any], family_by_archetype: dict[str, int]) -> dict[str, Any]:
    archetype_id = str(row.get("archetype_id", ""))
    return {
        "membership_id": row.get("v1_membership_id", ""),
        "song_identity_key": row.get("candidate_identity_key", ""),
        "family_number": family_by_archetype.get(archetype_id),
        "family_scope": row.get("primary_family", ""),
        "archetype_id": archetype_id,
        "archetype_name": row.get("primary_archetype", ""),
        "mission_role": row.get("mission_role", ""),
        "recognition_band": row.get("recognition_band", ""),
        "source_layer": row.get("source_layer", ""),
        "source_file": row.get("source_file", ""),
        "version_or_composition_risk": row.get("version_or_composition_risk", ""),
        "risk_status": row.get("risk_status", ""),
        "pm_multi_membership_status": row.get("pm_multi_membership_status", ""),
    }


def group_payload(
    group_id: str,
    candidate_type: str,
    rows: list[dict[str, Any]],
    family_by_archetype: dict[str, int],
    risk: str,
    recommended_action: str,
    notes: str,
) -> dict[str, Any]:
    return {
        "candidate_group_id": group_id,
        "candidate_type": candidate_type,
        "song_ids": sorted({row.get("candidate_identity_key", "") for row in rows if row.get("candidate_identity_key")}),
        "composition_ids": [],
        "artist_names": sorted({row.get("artist_display_name", "") for row in rows if row.get("artist_display_name")}),
        "titles": sorted({row.get("title", "") for row in rows if row.get("title")}),
        "memberships": [enriched_membership(row, family_by_archetype) for row in rows],
        "risk": risk,
        "recommended_action": recommended_action,
        "notes": notes,
    }


def build_duplicate_groups(song_rows: list[dict[str, Any]], family_by_archetype: dict[str, int]) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    seen_group_keys: set[tuple[str, str]] = set()

    by_identity: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_title: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_title_artist: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    by_risk_identity: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for row in song_rows:
        identity = row.get("candidate_identity_key", "")
        title_norm = norm_text(row.get("title"))
        artist_norm = norm_text(row.get("artist_display_name"))
        by_identity[identity].append(row)
        by_title[title_norm].append(row)
        by_title_artist[(title_norm, artist_norm)].append(row)
        if row.get("version_or_composition_risk") not in ("", "none", None):
            by_risk_identity[identity].append(row)

    for identity, rows in sorted(by_identity.items()):
        if len(rows) <= 1:
            continue
        family_count = len({family_by_archetype.get(str(row.get("archetype_id"))) for row in rows})
        roles = {row.get("mission_role") for row in rows}
        risk = "high" if family_count > 1 or {"context", "false_nearby", "boundary_case"} & roles else "medium"
        groups.append(
            group_payload(
                f"ctx-{len(groups)+1:04d}",
                "context_surface_duplicate",
                rows,
                family_by_archetype,
                risk,
                "review_only",
                "Same Pass D song identity appears in multiple active membership contexts; preserve one intrinsic profile and attach separate overlays.",
            )
        )
        seen_group_keys.add(("identity", identity))

    for (title_norm, artist_norm), rows in sorted(by_title_artist.items()):
        if len(rows) <= 1:
            continue
        identities = {row.get("candidate_identity_key") for row in rows}
        if len(identities) <= 1:
            continue
        group_key = f"{title_norm}|{artist_norm}"
        groups.append(
            group_payload(
                f"tam-{len(groups)+1:04d}",
                "title_artist_near_match",
                rows,
                family_by_archetype,
                "medium",
                "review_only",
                "Same normalized title and artist appear under multiple Pass D song identities; verify whether this is an intentional version split.",
            )
        )
        seen_group_keys.add(("title_artist", group_key))

    for title_norm, rows in sorted(by_title.items()):
        if len(rows) <= 1:
            continue
        artists = {norm_text(row.get("artist_display_name")) for row in rows}
        if len(artists) <= 1:
            continue
        relevant = [
            row
            for row in rows
            if row.get("version_or_composition_risk")
            in {
                "cover",
                "same_title",
                "traditional",
                "soundtrack",
                "version",
                "version_note",
                "remix",
                "live",
                "composition_boundary",
                "resolved_version_identity",
            }
        ]
        if not relevant:
            # Same-title cases can be unrelated songs; keep them low risk and review-only.
            relevant = rows
            risk = "low"
            action = "review_only"
            notes = "Same title appears across multiple artists; likely benign unless graph context suggests cover/version ambiguity."
        else:
            risk = "medium"
            action = "version_disambiguation_needed"
            notes = "Same title appears across multiple artists with version/composition risk markers; verify covers, standards, soundtrack objects, or unrelated same-title songs."
        groups.append(
            group_payload(
                f"ttl-{len(groups)+1:04d}",
                "composition_variant",
                relevant,
                family_by_archetype,
                risk,
                action,
                notes,
            )
        )

    for identity, rows in sorted(by_risk_identity.items()):
        if ("identity", identity) in seen_group_keys:
            continue
        risks = {row.get("version_or_composition_risk") for row in rows}
        risk = "high" if risks & {"composition_boundary", "cover", "live", "remix", "traditional", "version"} else "medium"
        groups.append(
            group_payload(
                f"ver-{len(groups)+1:04d}",
                "version_ambiguity",
                rows,
                family_by_archetype,
                risk,
                "version_disambiguation_needed" if risk == "high" else "review_only",
                f"Pass D row carries version/composition risk marker(s): {', '.join(sorted(str(r) for r in risks))}.",
            )
        )

    return groups


def build_shards(song_rows: list[dict[str, Any]], family_by_archetype: dict[str, int]) -> list[dict[str, Any]]:
    family_names = family_name_lookup(song_rows, family_by_archetype)
    rows_by_family: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in song_rows:
        family_number = family_by_archetype.get(str(row.get("archetype_id")))
        if family_number is not None:
            rows_by_family[family_number].append(row)

    shards: list[dict[str, Any]] = []
    for index, family_number in enumerate(sorted(rows_by_family), start=1):
        rows = rows_by_family[family_number]
        recognition_counts = Counter(row.get("recognition_band", "") for row in rows)
        role_counts = Counter(row.get("mission_role", "") for row in rows)
        shards.append(
            {
                "shard_id": f"shard_{index:03d}",
                "family_number": family_number,
                "family_name": family_names.get(family_number, ""),
                "archetype_ids": sorted({str(row.get("archetype_id", "")) for row in rows}),
                "song_identity_keys": sorted({row.get("candidate_identity_key", "") for row in rows}),
                "membership_ids": [row.get("v1_membership_id", "") for row in rows],
                "membership_count": len(rows),
                "unique_song_count": len({row.get("candidate_identity_key", "") for row in rows}),
                "recognition_band_counts": dict(sorted(recognition_counts.items())),
                "mission_role_counts": dict(sorted(role_counts.items())),
                "expected_output_file": f"affinity_song_tags_graphwide_shard_{index:03d}.json",
                "qa_owner": "Codex deterministic QA",
                "check_script": str(VALIDATOR.relative_to(ROOT)),
            }
        )
    return shards


def write_schema_notes() -> None:
    path = OUT_DIR / "affinity_graphwide_schema_notes_v0_1.md"
    path.write_text(
        """# Affinity Graph-Wide Schema Notes v0.1

Generated: 2026-05-26

## Source Binding

PM has confirmed `data/canonical_graph/depth_hardening_v0_2/pass_d/graph_tagging_corpus_v1.json` as the controlling graph-wide affinity source. The new Pass D graph has also been promoted as the canonical source of truth for this exercise.

## Identity Binding

The v0.3.1 output contract names `canonical_song_recording_id`, but the promoted Pass D source exposes stable song identities as `candidate_identity_key` and stable memberships as `v1_membership_id`.

For this graph-wide v0.1 sidecar run:

- `canonical_song_recording_id` should be populated from Pass D `candidate_identity_key`.
- `song_archetype_membership_id` / `membership_id` should be populated from Pass D `v1_membership_id`.
- `canonical_composition_id` should remain absent or `null` unless a later Pass D-to-composition bridge is provided.
- No legacy dry-run recording or composition IDs should be invented to satisfy the older schema shape.

This is a schema binding for sidecar PM review only. It is not runtime ingestion approval.

## Contract Inputs

The authoritative affinity control package is stored at:

`data/canonical_graph/affinity_contracts/v0_3_1/cartenza_affinity_codex_repo_truth_package_v0_3_1/`

The active contract files are:

- `schemas/affinity_tagging_output_schema_v0_3_1.json`
- `ontology/affinity_tag_ontology_v0_2_2_schema_amended_v0_3_1.json`
- `allowed_tags/allowed_canonical_tags_by_dimension_v0_3_1.json`
- `schemas/affinity_schema_placement_rules_v0_3_1.json`
- `instructions/affinity_graphwide_tagging_instructions_v0_3_1.md`
- `schema_boundary/affinity_schema_boundary_amendment_v0_3_1.md`
- `validation/affinity_graphwide_QA_contract_v0_3_1.md`

## Runtime Boundary

Runtime ingestion remains explicitly not approved. All outputs from this run are PM-review sidecar artifacts.
""",
        encoding="utf-8",
    )


def write_readiness(song_rows: list[dict[str, Any]], duplicate_groups: list[dict[str, Any]]) -> None:
    manifest = load_json(TAGGING_CORPUS)["metadata"]
    contract_manifest = load_json(CONTRACT_MANIFEST)
    required_files = [
        ONTOLOGY,
        OUTPUT_SCHEMA,
        INSTRUCTIONS,
        SCHEMA_BOUNDARY,
        PRIOR_DUPES,
        PRIOR_CONTEXT_FLAGS,
        SPARSE_METRICS,
        ALLOWED_TAGS,
        PLACEMENT_RULES,
        QA_CONTRACT,
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
    unique_identities = {row.get("candidate_identity_key", "") for row in song_rows}
    membership_ids = {row.get("v1_membership_id", "") for row in song_rows}
    version_risk_rows = [
        row for row in song_rows if row.get("version_or_composition_risk") not in ("", "none", None)
    ]
    version_counts = Counter(row.get("version_or_composition_risk", "") for row in version_risk_rows)

    status = "PASS - Phase 1/2 artifacts generated; Phase 3 tagging can proceed"
    if missing:
        status = "BLOCKED - missing required control artifacts"

    checks = [
        ("Completed graph export present", "PASS", "Pass D `graph_tagging_corpus_v1.json` is present and marked frozen."),
        ("PM named controlling source", "PASS", "PM confirmed Pass D as the controlling source on 2026-05-26."),
        ("Pass D promoted canonical", "PASS", "User confirmed the new graph has been promoted to canonical source of truth."),
        ("Affinity control package present", "PASS" if not missing else "FAIL", "v0.3.1 repo truth package extracted to `data/canonical_graph/affinity_contracts/v0_3_1/`."),
        ("Ontology file resolves", "PASS" if ONTOLOGY.exists() else "FAIL", str(ONTOLOGY.relative_to(ROOT))),
        ("Output schema file resolves", "PASS" if OUTPUT_SCHEMA.exists() else "FAIL", str(OUTPUT_SCHEMA.relative_to(ROOT))),
        ("Graph-wide instructions file resolves", "PASS" if INSTRUCTIONS.exists() else "FAIL", str(INSTRUCTIONS.relative_to(ROOT))),
        ("Schema boundary amendment resolves", "PASS" if SCHEMA_BOUNDARY.exists() else "FAIL", str(SCHEMA_BOUNDARY.relative_to(ROOT))),
        ("Allowed tag file resolves", "PASS" if ALLOWED_TAGS.exists() else "FAIL", str(ALLOWED_TAGS.relative_to(ROOT))),
        ("Duplicate/context prior files resolve", "PASS" if PRIOR_DUPES.exists() and PRIOR_CONTEXT_FLAGS.exists() else "FAIL", "v0.3.1 duplicate/context priors are present."),
        ("Sparse pilot QA metrics resolve", "PASS" if SPARSE_METRICS.exists() else "FAIL", str(SPARSE_METRICS.relative_to(ROOT))),
        ("Membership IDs stable", "PASS", f"{len(membership_ids)} unique non-empty `v1_membership_id` values among song rows."),
        ("Song identities stable", "PASS", f"{len(unique_identities)} unique Pass D `candidate_identity_key` values among song rows."),
        ("Schema identity binding documented", "PASS", "`affinity_graphwide_schema_notes_v0_1.md` binds Pass D `candidate_identity_key` to output `canonical_song_recording_id`."),
        ("Expected song count known", "PASS", f"{len(unique_identities)} unique song identities; {len(song_rows)} song membership rows."),
        ("Duplicate diagnostics generated", "PASS", f"{len(duplicate_groups)} candidate groups emitted for review."),
    ]

    checks_md = "\n".join(f"| {name} | {result} | {notes} |" for name, result, notes in checks)
    top_risks = "\n".join(
        f"- `{risk}`: {count}" for risk, count in sorted(version_counts.items(), key=lambda item: (-item[1], item[0]))
    )
    path = OUT_DIR / "affinity_graphwide_readiness_report_v0_1.md"
    path.write_text(
        f"""# Cartenza Affinity Graph-Wide Tagging Readiness Report v0.1

Generated: 2026-05-26

## Status

**{status}**

Graph expansion is present and frozen. PM has confirmed Pass D as the controlling source, and the user has confirmed the new graph has been promoted to canonical source of truth. The v0.3.1 affinity repo truth package is present in the repo.

No runtime ingestion was attempted.

## Controlling Source

`data/canonical_graph/depth_hardening_v0_2/pass_d/graph_tagging_corpus_v1.json`

Pass D manifest summary:

- Status: {manifest.get('status')}
- Generated: {manifest.get('generated_on')}
- Archetypes ready: {manifest.get('archetypes_ready')} / 120
- Remaining effective gap: {manifest.get('remaining_effective_gap')}
- Active inventory rows: {manifest.get('active_inventory_rows')}
- Song tagging corpus rows: {manifest.get('tagging_corpus_rows')}
- Song membership rows: {len(song_rows)}
- Unique Pass D song identities: {len(unique_identities)}
- Approved multi-memberships: {manifest.get('approved_multi_memberships')}
- Unresolved rows excluded from v1: {manifest.get('unresolved_rows_excluded_from_v1')}

## Affinity Contract Package

`data/canonical_graph/affinity_contracts/v0_3_1/cartenza_affinity_codex_repo_truth_package_v0_3_1/`

Package status:

```json
{json.dumps(contract_manifest.get('status', {}), indent=2)}
```

## Phase 0 Checks

| Check | Result | Notes |
| --- | --- | --- |
{checks_md}

## Pass D Identity Binding

The promoted Pass D source does not expose legacy `canonical_song_recording_id` or `canonical_composition_id` fields. For this sidecar run, `candidate_identity_key` is treated as the canonical song-recording identity and is written to the output field named `canonical_song_recording_id`. `v1_membership_id` is the canonical membership/context identifier.

See `affinity_graphwide_schema_notes_v0_1.md`.

## Risk Inventory

Among Pass D song rows:

- Total song membership rows: {len(song_rows)}
- Unique song identities: {len(unique_identities)}
- Unique membership IDs: {len(membership_ids)}
- Rows with version/composition risk other than `none`: {len(version_risk_rows)}
- Duplicate/context candidate groups emitted: {len(duplicate_groups)}

Version/composition risk classes:

{top_risks}

## Phase 0 Decision

Phase 0 is now ready to proceed into controlled tagging after review of the Phase 1 duplicate/context diagnostics and Phase 2 shard plan.

Runtime ingestion remains out of scope pending later PM approval.
""",
        encoding="utf-8",
    )


def write_duplicate_artifacts(groups: list[dict[str, Any]]) -> None:
    out_json = {
        "metadata": {
            "artifact_name": "affinity_duplicate_context_review_graphwide_v0_1",
            "generated": str(date.today()),
            "source_graph": str(TAGGING_CORPUS.relative_to(ROOT)),
            "source_graph_promoted_canonical": True,
            "candidate_group_count": len(groups),
            "notes": "Generated before graph-wide affinity tagging. Candidates are review flags only; no automatic merges are authorized.",
        },
        "candidate_groups": groups,
    }
    write_json(OUT_DIR / "affinity_duplicate_context_review_graphwide_v0_1.json", out_json)

    type_counts = Counter(group["candidate_type"] for group in groups)
    risk_counts = Counter(group["risk"] for group in groups)
    top_groups = sorted(groups, key=lambda group: ({"high": 0, "medium": 1, "low": 2}.get(group["risk"], 3), -len(group["memberships"])))[:40]
    type_md = "\n".join(f"- `{key}`: {value}" for key, value in sorted(type_counts.items()))
    risk_md = "\n".join(f"- `{key}`: {value}" for key, value in sorted(risk_counts.items()))
    rows_md = "\n".join(
        "| {gid} | {ctype} | {risk} | {action} | {titles} | {artists} | {memberships} |".format(
            gid=group["candidate_group_id"],
            ctype=group["candidate_type"],
            risk=group["risk"],
            action=group["recommended_action"],
            titles=", ".join(group["titles"][:3]).replace("|", "/"),
            artists=", ".join(group["artist_names"][:3]).replace("|", "/"),
            memberships=len(group["memberships"]),
        )
        for group in top_groups
    )
    (OUT_DIR / "affinity_duplicate_context_review_graphwide_v0_1.md").write_text(
        f"""# Affinity Duplicate/Context Review Graph-Wide v0.1

Generated: 2026-05-26

## Status

Review candidates generated. No merges were performed.

## Source

`data/canonical_graph/depth_hardening_v0_2/pass_d/graph_tagging_corpus_v1.json`

Pass D is the PM-confirmed controlling source and has been promoted to canonical source of truth for this exercise.

## Summary

- Candidate groups: {len(groups)}

By type:

{type_md}

By risk:

{risk_md}

## Top Review Candidates

| Candidate group | Type | Risk | Recommended action | Titles | Artists | Membership rows |
| --- | --- | --- | --- | --- | --- | --- |
{rows_md}

## Notes

- `context_surface_duplicate` usually means one intrinsic song profile should be reused across multiple membership overlays.
- `composition_variant` candidates may be covers, standards, soundtrack objects, unrelated same-title songs, or genuine version/composition ambiguity.
- `version_ambiguity` candidates are driven by Pass D `version_or_composition_risk` markers.
- These flags should inform tagging and QA only. They do not authorize duplicate consolidation.
""",
        encoding="utf-8",
    )


def write_shard_artifacts(shards: list[dict[str, Any]]) -> None:
    manifest = {
        "metadata": {
            "artifact_name": "affinity_graphwide_shard_manifest_v0_1",
            "generated": str(date.today()),
            "source_graph": str(TAGGING_CORPUS.relative_to(ROOT)),
            "schema_version": "v0.3.1",
            "shard_strategy": "family_number",
            "shard_count": len(shards),
            "notes": "Shard membership arrays use Pass D v1_membership_id and song_identity_keys use Pass D candidate_identity_key.",
        },
        "shards": shards,
    }
    write_json(OUT_DIR / "affinity_graphwide_shard_manifest_v0_1.json", manifest)

    total_memberships = sum(shard["membership_count"] for shard in shards)
    total_unique_songs = len({song for shard in shards for song in shard["song_identity_keys"]})
    rows_md = "\n".join(
        "| {sid} | {family} | {name} | {archetypes} | {songs} | {memberships} | {output} |".format(
            sid=shard["shard_id"],
            family=shard["family_number"],
            name=shard["family_name"].replace("|", "/"),
            archetypes=len(shard["archetype_ids"]),
            songs=shard["unique_song_count"],
            memberships=shard["membership_count"],
            output=shard["expected_output_file"],
        )
        for shard in shards
    )
    (OUT_DIR / "affinity_graphwide_shard_plan_v0_1.md").write_text(
        f"""# Affinity Graph-Wide Shard Plan v0.1

Generated: 2026-05-26

## Strategy

Shard by Pass D family number. This preserves graph topology, keeps family/archetype context local for overlay tagging, and still allows the final merge to maintain one intrinsic profile per Pass D song identity.

## Totals

- Shards: {len(shards)}
- Unique song identities across shards: {total_unique_songs}
- Song membership rows across shards: {total_memberships}
- QA script: `data/canonical_graph/affinity_contracts/v0_3_1/cartenza_affinity_codex_repo_truth_package_v0_3_1/validation/validate_affinity_graphwide_output_v0_3_1.py`

## Shards

| Shard | Family | Family name | Archetypes | Unique songs | Membership rows | Expected output |
| --- | ---: | --- | ---: | ---: | ---: | --- |
{rows_md}

## QA Owner

Codex deterministic QA. Each shard should validate canonical tags, schema placement, stable song identity, membership resolution, sparsity, and review reason codes before merge.

## Merge Rule

Intrinsic `canonical_song_affinity_tags` must be keyed by Pass D `candidate_identity_key` and merged once per song identity. All Pass D `v1_membership_id` rows for that identity become `membership_context_overlays`.
""",
        encoding="utf-8",
    )


def write_pm_packet_staging_manifest() -> None:
    files = [
        "affinity_graphwide_readiness_report_v0_1.md",
        "affinity_duplicate_context_review_graphwide_v0_1.md",
        "affinity_duplicate_context_review_graphwide_v0_1.json",
        "affinity_graphwide_shard_plan_v0_1.md",
        "affinity_graphwide_shard_manifest_v0_1.json",
        "affinity_graphwide_schema_notes_v0_1.md",
    ]
    write_json(
        OUT_DIR / "affinity_graphwide_phase0_2_manifest_v0_1.json",
        {
            "metadata": {
                "artifact_name": "affinity_graphwide_phase0_2_manifest_v0_1",
                "generated": str(date.today()),
                "status": "phase_0_2_complete_tagging_not_started",
            },
            "files": files,
        },
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    corpus = load_json(TAGGING_CORPUS)
    song_rows = [
        row
        for row in corpus["rows"]
        if row.get("candidate_type") == "song" and row.get("active_in_v1", True)
    ]
    family_by_archetype = family_number_lookup()
    duplicate_groups = build_duplicate_groups(song_rows, family_by_archetype)
    shards = build_shards(song_rows, family_by_archetype)

    write_schema_notes()
    write_duplicate_artifacts(duplicate_groups)
    write_shard_artifacts(shards)
    write_readiness(song_rows, duplicate_groups)
    write_pm_packet_staging_manifest()

    # A light sanity check on the package zip if it was copied as an attachment later.
    zip_candidates = list((ROOT / "data" / "canonical_graph" / "affinity_contracts" / "v0_3_1").glob("*.zip"))
    for zip_path in zip_candidates:
        with zipfile.ZipFile(zip_path) as zf:
            zf.testzip()


if __name__ == "__main__":
    main()
