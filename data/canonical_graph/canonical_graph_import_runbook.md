# Canonical Graph Import Runbook

Scope: reusable production path for the 18-family Waymark Canonical Music Graph.

## Current Source Of Truth

The active production graph source of truth is now:

```text
data/canonical_graph/current/
```

The promotion manifest is:

```text
data/canonical_graph/canonical_graph_source_of_truth_manifest.json
```

This current graph is `canonical_graph_v1`, promoted from `depth_hardening_v0_2/pass_d` on 2026-05-26. It is the active input for downstream mission engine work, graph tagging, Apple ID resolution, album sidecar planning, Atlas profile targets, and graph-linking.

Do not use `depth_hardening_v0_1` totals or the old `import_dry_run` outputs as active source-of-truth inputs. The family normalized exports remain lineage/source material and can be used for audits or future regeneration.

## Legacy Family Contract

Each family directory should contain:

- `gap_summary.md`
- `artist_candidates.md`
- `album_candidates.md`
- `song_candidates.md`
- `corrections_to_source_report.md`
- `lock_readiness.md`
- `normalized_family_<family_id>.json`
- `import_warnings.md`

The normalized JSON was the original family import source. Markdown files are review and traceability artifacts. After the v1 promotion, these family exports are lineage inputs rather than the active mission-effective corpus.

## Import Shape

Do not import each family row as a unique canonical object.

Use this two-layer model:

1. Canonical entities:
   - `canonical_artists`
   - `canonical_albums`
   - `canonical_song_recordings`
2. Archetype memberships:
   - `artist_archetype_memberships`
   - `album_archetype_memberships`
   - `song_archetype_memberships`

Repeated IDs across families or archetypes are expected. They mean one canonical entity has multiple memberships.

## Legacy Dry Run Command

```sh
python3 scripts/canonical_graph_import_dry_run.py
```

Outputs are written to:

```text
data/canonical_graph/import_dry_run/
```

Important outputs:

- `canonical_graph_manifest.json`
- `import_dry_run_report.md`
- `merge_review_queue.md`
- `canonical_artists.json`
- `canonical_albums.json`
- `canonical_song_recordings.json`
- `artist_archetype_memberships.json`
- `album_archetype_memberships.json`
- `song_archetype_memberships.json`

Use `--strict-years` only when traditional/ambiguous rows have been resolved. This dry-run path predates the v1 mission-effective graph and should not be treated as the active source of truth.

## Current Downstream Inputs

Use these stable paths:

- `data/canonical_graph/current/canonical_graph_active_inventory.json`
- `data/canonical_graph/current/graph_tagging_corpus.json`
- `data/canonical_graph/current/apple_id_resolution_queue.json`
- `data/canonical_graph/current/album_sidecar_seed_albums.json`
- `data/canonical_graph/current/album_track_sidecar.json`
- `data/canonical_graph/current/album_track_sidecar_tracks.csv`
- `data/canonical_graph/current/album_track_sidecar_album_resolution.csv`
- `data/canonical_graph/current/atlas_archetype_profile_targets.json`
- `data/canonical_graph/current/graph_linking_node_set.json`
- `data/canonical_graph/current/pm_multi_membership_decisions.json`

## Validation Rules

Required normalized enums:

- roles: `album_anchor`, `anchor`, `artist_anchor`, `boundary`, `bridge`, `compilation_gateway`, `contrast`, `deepening`, `false_nearby`, `gateway`, `live_gateway`, `song_first`
- recognition tiers: `mass`, `high`, `medium`, `low`, `cult`
- survey tiers: `core`, `standard`, `edge`, `suppress`
- album object types: `studio_album`, `live_album`, `compilation`, `soundtrack`, `ep`
- song artist survey status: `artist_survey_worthy`, `song_survey_first`, `song_survey_only`

IDs must be lowercase kebab-case.

## Per-Family Dispatch Pattern

For each remaining family:

1. Convert source reports into the eight family artifacts.
2. Preserve source rows as `existing_seed=true`.
3. Mark added gap-fill rows as `existing_seed=false`.
4. Normalize slugs and enums before writing JSON.
5. Flag, do not guess, ambiguous merge/version risks.
6. Run the dry-run script.
7. Inspect `import_dry_run_report.md` and `merge_review_queue.md`.
8. Update the global review with family counts, warnings, and lock posture.

## Current v1 Lock Bar

The current v1 source-of-truth lock is satisfied by `data/canonical_graph/current/`:

- 120 / 120 archetypes mission-effective ready.
- Remaining effective gap is 0.
- Pass C compiler row errors are 0.
- PM approved all 13 current-identity collisions as active multi-memberships.
- Rows with `needs_resolution`, `exclude_or_quarantine`, or `risky_unresolved` are excluded from v1.
- Stable downstream corpora exist for tagging, Apple ID resolution, album sidecar planning, Atlas profile targets, and graph-linking.

Legacy dry-run validation remains useful for lineage/debugging, but it is no longer the active lock gate.
