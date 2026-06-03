# Current Canonical Graph Source Of Truth

Promoted on 2026-05-26.

Status: `source_of_truth`

The active canonical graph is now `canonical_graph_v1`, promoted from Pass D:

`data/canonical_graph/depth_hardening_v0_2/pass_d/`

## Gate

- Archetypes ready: 120 / 120
- Remaining effective gap: 0
- Pass C row errors: 0
- Active inventory rows: 11714
- Tagging corpus rows: 7419
- Apple ID resolution queue rows: 7419
- Album sidecar seed rows: 2234
- Graph-linking node rows: 11326
- Approved multi-memberships: 13
- Unresolved rows excluded from v1: 804

## Stable Current Paths

| Purpose | Path |
| --- | --- |
| Active graph inventory | `data/canonical_graph/current/canonical_graph_active_inventory.json` |
| Song tagging corpus | `data/canonical_graph/current/graph_tagging_corpus.json` |
| Apple ID resolution queue | `data/canonical_graph/current/apple_id_resolution_queue.json` |
| Album sidecar seed albums | `data/canonical_graph/current/album_sidecar_seed_albums.json` |
| Album track sidecar | `data/canonical_graph/current/album_track_sidecar.json` |
| Album track sidecar tracks CSV | `data/canonical_graph/current/album_track_sidecar_tracks.csv` |
| Atlas archetype profile targets | `data/canonical_graph/current/atlas_archetype_profile_targets.json` |
| Graph-linking node set | `data/canonical_graph/current/graph_linking_node_set.json` |
| PM multi-membership decisions | `data/canonical_graph/current/pm_multi_membership_decisions.json` |
| Freeze manifest | `data/canonical_graph/current/canonical_graph_freeze_manifest.json` |

## Policy

- Downstream mission engine, tagging, linking, Atlas profile targets, and Apple ID resolution should consume `data/canonical_graph/current/*`.
- Album sidecar planning and album-world missions should consume `data/canonical_graph/current/album_track_sidecar.json` and paired sidecar CSVs.
- `depth_hardening_v0_1` remains historical draft expansion.
- `import_dry_run` remains pre-hardening dry-run output and is not active source of truth.
- `family_*/normalized_family_*.json` remains source material and audit lineage, not the active mission-effective corpus.
- The v0.2 needs-resolution queue remains excluded until a future cleaned promotion.

## Post-Freeze Radiohead Missing-Obvious Hotfix

- Patch: `radiohead_missing_obvious_hotfix_v1`
- Applied on: 2026-05-31
- Intent: Post-freeze missing-obvious correction for Radiohead coverage in Family 10 while preserving recording/title specificity.
- Added rows: 13
- Title/recording guardrail: Radiohead - Creep remains distinct from TLC - Creep and must not be title-merged.

## Post-Freeze Oasis Missing-Obvious Hotfix

- Patch: `oasis_missing_obvious_hotfix_v1`
- Applied on: 2026-06-01
- Intent: Post-freeze missing-obvious correction for Oasis and (What's the Story) Morning Glory? coverage in Family 10.
- Added rows: 4
- Apple links: `data/canonical_graph/current/apple_music_family10_missing_obvious_hotfix_v1/apple_music_family10_missing_obvious_hotfix_links_v1.jsonl`
- Guardrail: Oasis rows are Britpop/alt-pop bridge material, not generic wedding/nostalgia controls.
