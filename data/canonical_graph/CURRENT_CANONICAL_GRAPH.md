# Current Canonical Graph Source Of Truth

Promoted on 2026-05-26.

Status: `source_of_truth`

The active canonical graph is now `canonical_graph_v1`, promoted from Pass D:

`data/canonical_graph/depth_hardening_v0_2/pass_d/`

## Gate

- Archetypes ready: 120 / 120
- Remaining effective gap: 0
- Pass C row errors: 0
- Active inventory rows: 11697
- Tagging corpus rows: 7409
- Apple ID resolution queue rows: 7409
- Album sidecar seed rows: 2231
- Graph-linking node rows: 11309
- Approved multi-memberships: 13
- Unresolved rows excluded from v1: 804

## Stable Current Paths

| Purpose | Path |
| --- | --- |
| Active graph inventory | `data/canonical_graph/current/canonical_graph_active_inventory.json` |
| Song tagging corpus | `data/canonical_graph/current/graph_tagging_corpus.json` |
| Apple ID resolution queue | `data/canonical_graph/current/apple_id_resolution_queue.json` |
| Album sidecar seed albums | `data/canonical_graph/current/album_sidecar_seed_albums.json` |
| Atlas archetype profile targets | `data/canonical_graph/current/atlas_archetype_profile_targets.json` |
| Graph-linking node set | `data/canonical_graph/current/graph_linking_node_set.json` |
| PM multi-membership decisions | `data/canonical_graph/current/pm_multi_membership_decisions.json` |
| Freeze manifest | `data/canonical_graph/current/canonical_graph_freeze_manifest.json` |

## Policy

- Downstream mission engine, tagging, linking, Atlas profile targets, and Apple ID resolution should consume `data/canonical_graph/current/*`.
- `depth_hardening_v0_1` remains historical draft expansion.
- `import_dry_run` remains pre-hardening dry-run output and is not active source of truth.
- `family_*/normalized_family_*.json` remains source material and audit lineage, not the active mission-effective corpus.
- The v0.2 needs-resolution queue remains excluded until a future cleaned promotion.
