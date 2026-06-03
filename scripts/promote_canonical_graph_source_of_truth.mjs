#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

const repoRoot = process.cwd();
const canonicalRoot = path.join(repoRoot, "data/canonical_graph");
const passD = path.join(canonicalRoot, "depth_hardening_v0_2/pass_d");
const current = path.join(canonicalRoot, "current");
const promotedOn = "2026-05-26";

const passDManifest = readJson(path.join(passD, "graph_hardening_pass_d_freeze_manifest.json"));
const passDMetadata = passDManifest.metadata;
const albumTrackSidecar = readJson(path.join(passD, "album_track_sidecar_v1.json"));
const albumTrackSidecarMetadata = albumTrackSidecar.metadata;

if (passDMetadata.status !== "frozen") {
  throw new Error(`Pass D is not frozen; found status=${passDMetadata.status}`);
}
if (passDMetadata.archetypes_ready !== 120 || passDMetadata.remaining_effective_gap !== 0) {
  throw new Error("Pass D does not satisfy the 120/120 zero-gap source-of-truth gate.");
}
if (passDMetadata.pass_c_row_errors !== 0) {
  throw new Error("Pass D cannot be promoted while Pass C row errors remain.");
}

fs.mkdirSync(current, { recursive: true });

const artifactMap = [
  ["graph_hardening_v1_active_inventory.json", "canonical_graph_active_inventory.json"],
  ["graph_hardening_v1_active_inventory.csv", "canonical_graph_active_inventory.csv"],
  ["graph_tagging_corpus_v1.json", "graph_tagging_corpus.json"],
  ["graph_tagging_corpus_v1.csv", "graph_tagging_corpus.csv"],
  ["apple_id_resolution_queue_v1.json", "apple_id_resolution_queue.json"],
  ["apple_id_resolution_queue_v1.csv", "apple_id_resolution_queue.csv"],
  ["album_sidecar_seed_albums_v1.json", "album_sidecar_seed_albums.json"],
  ["album_sidecar_seed_albums_v1.csv", "album_sidecar_seed_albums.csv"],
  ["atlas_archetype_profile_targets_v1.json", "atlas_archetype_profile_targets.json"],
  ["atlas_archetype_profile_targets_v1.csv", "atlas_archetype_profile_targets.csv"],
  ["graph_linking_node_set_v1.json", "graph_linking_node_set.json"],
  ["graph_linking_node_set_v1.csv", "graph_linking_node_set.csv"],
  ["pm_multi_membership_decisions_v1.json", "pm_multi_membership_decisions.json"],
  ["pm_multi_membership_decisions_v1.csv", "pm_multi_membership_decisions.csv"],
  ["album_track_sidecar_v1.json", "album_track_sidecar.json"],
  ["album_track_sidecar_tracks_v1.csv", "album_track_sidecar_tracks.csv"],
  ["album_track_sidecar_album_resolution_v1.csv", "album_track_sidecar_album_resolution.csv"],
  ["album_track_sidecar_manual_apple_overrides_v1.json", "album_track_sidecar_manual_apple_overrides.json"],
  ["album_track_sidecar_manifest_v1.md", "album_track_sidecar_manifest.md"],
  ["graph_hardening_pass_d_freeze_manifest.json", "canonical_graph_freeze_manifest.json"],
  ["graph_hardening_pass_d_freeze_manifest.md", "canonical_graph_freeze_manifest.md"],
];

for (const [sourceName, targetName] of artifactMap) {
  fs.copyFileSync(path.join(passD, sourceName), path.join(current, targetName));
}

const sourceOfTruthManifest = {
  generated_on: promotedOn,
  status: "source_of_truth",
  source_version: "canonical_graph_v1",
  promoted_from: "data/canonical_graph/depth_hardening_v0_2/pass_d",
  pm_decision: passDMetadata.pm_decision,
  gates: {
    archetypes_ready: passDMetadata.archetypes_ready,
    remaining_effective_gap: passDMetadata.remaining_effective_gap,
    pass_c_row_errors: passDMetadata.pass_c_row_errors,
    unresolved_rows_excluded_from_v1: passDMetadata.unresolved_rows_excluded_from_v1,
  },
  counts: {
    active_inventory_rows: passDMetadata.active_inventory_rows,
    active_baseline_rows: passDMetadata.active_baseline_rows,
    active_pass_c_rows: passDMetadata.active_pass_c_rows,
    approved_multi_memberships: passDMetadata.approved_multi_memberships,
    tagging_corpus_rows: passDMetadata.tagging_corpus_rows,
    apple_id_resolution_queue_rows: passDMetadata.apple_id_resolution_queue_rows,
    album_sidecar_seed_rows: passDMetadata.album_sidecar_seed_rows,
    album_track_sidecar_album_rows: albumTrackSidecarMetadata.album_identity_rows_in_sidecar,
    album_track_sidecar_tracks: albumTrackSidecarMetadata.total_sidecar_tracks,
    album_track_sidecar_apple_resolved_albums: albumTrackSidecarMetadata.apple_resolved_album_identity_rows,
    album_track_sidecar_musicbrainz_resolved_albums: albumTrackSidecarMetadata.musicbrainz_resolved_album_identity_rows,
    graph_linking_node_rows: passDMetadata.graph_linking_node_rows,
  },
  post_freeze_availability_patch: passDMetadata.post_freeze_availability_patch ?? null,
  current_artifacts: {
    active_inventory: "data/canonical_graph/current/canonical_graph_active_inventory.json",
    active_inventory_csv: "data/canonical_graph/current/canonical_graph_active_inventory.csv",
    graph_tagging_corpus: "data/canonical_graph/current/graph_tagging_corpus.json",
    graph_tagging_corpus_csv: "data/canonical_graph/current/graph_tagging_corpus.csv",
    apple_id_resolution_queue: "data/canonical_graph/current/apple_id_resolution_queue.json",
    apple_id_resolution_queue_csv: "data/canonical_graph/current/apple_id_resolution_queue.csv",
    album_sidecar_seed_albums: "data/canonical_graph/current/album_sidecar_seed_albums.json",
    album_sidecar_seed_albums_csv: "data/canonical_graph/current/album_sidecar_seed_albums.csv",
    album_track_sidecar: "data/canonical_graph/current/album_track_sidecar.json",
    album_track_sidecar_tracks_csv: "data/canonical_graph/current/album_track_sidecar_tracks.csv",
    album_track_sidecar_album_resolution_csv: "data/canonical_graph/current/album_track_sidecar_album_resolution.csv",
    album_track_sidecar_manual_apple_overrides: "data/canonical_graph/current/album_track_sidecar_manual_apple_overrides.json",
    album_track_sidecar_manifest_md: "data/canonical_graph/current/album_track_sidecar_manifest.md",
    atlas_archetype_profile_targets: "data/canonical_graph/current/atlas_archetype_profile_targets.json",
    atlas_archetype_profile_targets_csv: "data/canonical_graph/current/atlas_archetype_profile_targets.csv",
    graph_linking_node_set: "data/canonical_graph/current/graph_linking_node_set.json",
    graph_linking_node_set_csv: "data/canonical_graph/current/graph_linking_node_set.csv",
    pm_multi_membership_decisions: "data/canonical_graph/current/pm_multi_membership_decisions.json",
    pm_multi_membership_decisions_csv: "data/canonical_graph/current/pm_multi_membership_decisions.csv",
    freeze_manifest: "data/canonical_graph/current/canonical_graph_freeze_manifest.json",
    freeze_manifest_md: "data/canonical_graph/current/canonical_graph_freeze_manifest.md",
  },
  legacy_inputs: {
    family_normalized_exports: "data/canonical_graph/family_*/normalized_family_*.json",
    prior_import_dry_run: "data/canonical_graph/import_dry_run/",
    pass_a_b_normalized_inventory: "data/canonical_graph/depth_hardening_v0_2/graph_hardening_v0_2_normalized_inventory.json",
    pass_c_compiled_additions: "data/canonical_graph/depth_hardening_v0_2/pass_c/graph_hardening_pass_c_compiled_additions.json",
    pass_d_freeze: "data/canonical_graph/depth_hardening_v0_2/pass_d/",
  },
  source_of_truth_policy: [
    "Use data/canonical_graph/current/* for downstream mission engine, tagging, linking, Atlas profile targets, and Apple ID resolution.",
    "Do not use depth_hardening_v0_1 totals or pre-hardening import_dry_run outputs as active source-of-truth inputs.",
    "Family normalized exports remain historical/source-material inputs, not the active mission-effective corpus.",
    "Rows in the v0.2 needs-resolution queue remain excluded until explicitly cleaned and re-promoted.",
  ],
};

writeJson(path.join(current, "canonical_graph_source_of_truth_manifest.json"), sourceOfTruthManifest);
writeJson(path.join(canonicalRoot, "canonical_graph_source_of_truth_manifest.json"), sourceOfTruthManifest);
writeMarkdown(sourceOfTruthManifest);

console.log(JSON.stringify(sourceOfTruthManifest, null, 2));

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function writeJson(file, value) {
  fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`);
}

function writeMarkdown(manifest) {
  const md = `# Current Canonical Graph Source Of Truth

Promoted on ${promotedOn}.

Status: \`${manifest.status}\`

The active canonical graph is now \`${manifest.source_version}\`, promoted from Pass D:

\`data/canonical_graph/depth_hardening_v0_2/pass_d/\`

## Gate

- Archetypes ready: ${manifest.gates.archetypes_ready} / 120
- Remaining effective gap: ${manifest.gates.remaining_effective_gap}
- Pass C row errors: ${manifest.gates.pass_c_row_errors}
- Active inventory rows: ${manifest.counts.active_inventory_rows}
- Tagging corpus rows: ${manifest.counts.tagging_corpus_rows}
- Apple ID resolution queue rows: ${manifest.counts.apple_id_resolution_queue_rows}
- Album sidecar seed rows: ${manifest.counts.album_sidecar_seed_rows}
- Graph-linking node rows: ${manifest.counts.graph_linking_node_rows}
- Approved multi-memberships: ${manifest.counts.approved_multi_memberships}
- Unresolved rows excluded from v1: ${manifest.gates.unresolved_rows_excluded_from_v1}

## Stable Current Paths

| Purpose | Path |
| --- | --- |
| Active graph inventory | \`${manifest.current_artifacts.active_inventory}\` |
| Song tagging corpus | \`${manifest.current_artifacts.graph_tagging_corpus}\` |
| Apple ID resolution queue | \`${manifest.current_artifacts.apple_id_resolution_queue}\` |
| Album sidecar seed albums | \`${manifest.current_artifacts.album_sidecar_seed_albums}\` |
| Album track sidecar | \`${manifest.current_artifacts.album_track_sidecar}\` |
| Album track sidecar tracks CSV | \`${manifest.current_artifacts.album_track_sidecar_tracks_csv}\` |
| Atlas archetype profile targets | \`${manifest.current_artifacts.atlas_archetype_profile_targets}\` |
| Graph-linking node set | \`${manifest.current_artifacts.graph_linking_node_set}\` |
| PM multi-membership decisions | \`${manifest.current_artifacts.pm_multi_membership_decisions}\` |
| Freeze manifest | \`${manifest.current_artifacts.freeze_manifest}\` |

## Policy

- Downstream mission engine, tagging, linking, Atlas profile targets, and Apple ID resolution should consume \`data/canonical_graph/current/*\`.
- Album sidecar planning and album-world missions should consume \`data/canonical_graph/current/album_track_sidecar.json\` and paired sidecar CSVs.
- \`depth_hardening_v0_1\` remains historical draft expansion.
- \`import_dry_run\` remains pre-hardening dry-run output and is not active source of truth.
- \`family_*/normalized_family_*.json\` remains source material and audit lineage, not the active mission-effective corpus.
- The v0.2 needs-resolution queue remains excluded until a future cleaned promotion.
`;
  fs.writeFileSync(path.join(canonicalRoot, "CURRENT_CANONICAL_GRAPH.md"), md);
  fs.writeFileSync(path.join(current, "README.md"), md);
}
