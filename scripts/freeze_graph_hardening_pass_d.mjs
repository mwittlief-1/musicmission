#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

const repoRoot = process.cwd();
const base = path.join(repoRoot, "data/canonical_graph/depth_hardening_v0_2");
const passC = path.join(base, "pass_c");
const passD = path.join(base, "pass_d");

const generatedOn = "2026-05-26";
const pmDecision = "all_current_identity_collisions_approved_as_multi_membership";

const normalizedInventory = readJson(path.join(base, "graph_hardening_v0_2_normalized_inventory.json")).rows;
const passCAdditions = readJson(path.join(passC, "graph_hardening_pass_c_compiled_additions.json")).rows;
const passCAudit = readJson(path.join(passC, "graph_hardening_pass_c_updated_inventory_audit.json")).rows;
const passCQA = readJson(path.join(passC, "qa/graph_hardening_pass_c_qa.json"));

fs.mkdirSync(passD, { recursive: true });
fs.mkdirSync(path.join(passD, "qa"), { recursive: true });

const archetypeNameById = new Map(passCAudit.map((row) => [row.archetype_id, row.archetype]));
const approvedCollisionKeys = new Set(
  passCQA.duplicate_rows.map((row) => multiMembershipKey(row)),
);

const activeBaselineRows = normalizedInventory
  .filter(isSafeActiveBaselineRow)
  .map((row) => normalizeActiveRow(row, {
    source_layer: row.source_layer,
    source_file: row.source_file,
    source_index: row.source_index ?? "",
    active_effective_credit: Number(row.effective_mission_credit ?? 0),
    pm_multi_membership_status: "not_applicable",
  }));

const activePassCRows = passCAdditions.map((row) => {
  const approvedCollision = approvedCollisionKeys.has(multiMembershipKey(row));
  return normalizeActiveRow(row, {
    source_layer: "pass_c_addition",
    source_file: row.source_file,
    source_index: row.source_index,
    active_effective_credit: 1,
    pm_multi_membership_status: approvedCollision ? "pm_approved_multi_membership" : "not_applicable",
    pass_c_zero_credit_before_pm_decision: row.accepted_effective_credit === 0,
  });
});

const activeInventory = [...activeBaselineRows, ...activePassCRows]
  .map((row, index) => ({
    v1_membership_id: `v1m_${String(index + 1).padStart(5, "0")}`,
    ...row,
  }));

const taggingCorpus = activeInventory
  .filter((row) =>
    ["song", "recording"].includes(row.candidate_type) &&
    ["core_graph_playable", "boundary_candidate", "false_nearby_candidate", "context_candidate"].includes(row.import_class) &&
    row.risk_status !== "risky_unresolved",
  )
  .map((row) => ({
    ...row,
    tagging_scope:
      row.import_class === "core_graph_playable"
        ? "primary_song_tagging"
        : row.import_class === "context_candidate"
          ? "context_song_tagging"
          : "boundary_contrast_tagging",
  }));

const appleIdResolutionQueue = taggingCorpus.map((row) => ({
  v1_membership_id: row.v1_membership_id,
  candidate_identity_key: row.candidate_identity_key,
  archetype_id: row.archetype_id,
  primary_archetype: row.primary_archetype,
  candidate_type: row.candidate_type,
  artist_display_name: row.artist_display_name,
  title: row.title,
  year: row.year,
  import_class: row.import_class,
  version_or_composition_risk: row.version_or_composition_risk,
  risk_status: row.risk_status,
  resolution_status: "ready_for_apple_id_resolution",
  version_notes: row.notes,
  pm_multi_membership_status: row.pm_multi_membership_status,
}));

const albumSidecarSeeds = activeInventory
  .filter((row) =>
    row.candidate_type === "album" &&
    ["core_graph_album", "boundary_candidate", "false_nearby_candidate", "context_candidate"].includes(row.import_class) &&
    row.risk_status !== "risky_unresolved",
  )
  .map((row) => ({
    ...row,
    sidecar_scope: row.import_class === "core_graph_album" ? "core_album_sidecar" : "context_boundary_album_sidecar",
  }));

const graphLinkingNodeSet = buildGraphLinkingNodeSet(activeInventory);
const passDAudit = buildPassDAudit(passCAudit, activePassCRows);
const pmMultiMembershipDecisions = buildPMDecisionRows(passCQA.duplicate_rows, activePassCRows);

const summary = {
  generated_on: generatedOn,
  status: "frozen",
  pm_decision: pmDecision,
  archetypes_ready: passDAudit.filter((row) => row.pass_d_status === "mission_effective_ready").length,
  remaining_effective_gap: passDAudit.reduce((sum, row) => sum + row.effective_gap_after_pass_d, 0),
  active_inventory_rows: activeInventory.length,
  active_baseline_rows: activeBaselineRows.length,
  active_pass_c_rows: activePassCRows.length,
  approved_multi_memberships: pmMultiMembershipDecisions.length,
  tagging_corpus_rows: taggingCorpus.length,
  apple_id_resolution_queue_rows: appleIdResolutionQueue.length,
  album_sidecar_seed_rows: albumSidecarSeeds.length,
  graph_linking_node_rows: graphLinkingNodeSet.length,
  pass_c_row_errors: passCQA.row_errors.length,
  unresolved_rows_excluded_from_v1: normalizedInventory.filter((row) => row.risk_status === "risky_unresolved" || row.import_class === "needs_resolution").length,
};

writeJson("graph_hardening_pass_d_freeze_manifest.json", { metadata: summary, artifacts: artifactList() });
writeJson("graph_hardening_v1_active_inventory.json", { metadata: summary, rows: activeInventory });
writeCsv("graph_hardening_v1_active_inventory.csv", activeInventory);
writeJson("graph_tagging_corpus_v1.json", { metadata: summary, rows: taggingCorpus });
writeCsv("graph_tagging_corpus_v1.csv", taggingCorpus);
writeJson("apple_id_resolution_queue_v1.json", { metadata: summary, rows: appleIdResolutionQueue });
writeCsv("apple_id_resolution_queue_v1.csv", appleIdResolutionQueue);
writeJson("album_sidecar_seed_albums_v1.json", { metadata: summary, rows: albumSidecarSeeds });
writeCsv("album_sidecar_seed_albums_v1.csv", albumSidecarSeeds);
writeJson("graph_linking_node_set_v1.json", { metadata: summary, rows: graphLinkingNodeSet });
writeCsv("graph_linking_node_set_v1.csv", graphLinkingNodeSet);
writeJson("atlas_archetype_profile_targets_v1.json", { metadata: summary, rows: passDAudit });
writeCsv("atlas_archetype_profile_targets_v1.csv", passDAudit);
writeJson("pm_multi_membership_decisions_v1.json", { metadata: summary, rows: pmMultiMembershipDecisions });
writeCsv("pm_multi_membership_decisions_v1.csv", pmMultiMembershipDecisions);
writeMarkdown();

console.log(JSON.stringify(summary, null, 2));

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function writeJson(file, value) {
  fs.writeFileSync(path.join(passD, file), `${JSON.stringify(value, null, 2)}\n`);
}

function writeCsv(file, rows) {
  fs.writeFileSync(path.join(passD, file), toCsv(rows));
}

function isSafeActiveBaselineRow(row) {
  if (row.import_class === "needs_resolution" || row.import_class === "exclude_or_quarantine") return false;
  if (row.risk_status === "risky_unresolved") return false;
  return true;
}

function normalizeActiveRow(row, overrides) {
  const archetype = String(row.primary_archetype ?? archetypeNameById.get(row.archetype_id) ?? "").replace(/^\d{3}\s*:\s*/, "");
  const candidateIdentityKey = row.identity_key ?? identityKey(row);
  return {
    source_layer: overrides.source_layer,
    source_file: overrides.source_file,
    source_index: overrides.source_index,
    archetype_id: row.archetype_id,
    candidate_type: row.candidate_type,
    artist_display_name: row.artist_display_name,
    title: row.title,
    year: row.year,
    primary_family: row.primary_family,
    primary_archetype: archetype,
    secondary_archetypes: Array.isArray(row.secondary_archetypes) ? row.secondary_archetypes : [],
    recognition_band: row.recognition_band,
    mission_role: row.mission_role,
    import_class: row.import_class,
    version_or_composition_risk: row.version_or_composition_risk,
    risk_status: row.risk_status,
    confidence: row.confidence,
    why_it_belongs: row.why_it_belongs,
    notes: row.notes,
    candidate_identity_key: candidateIdentityKey,
    archetype_membership_key: `${candidateIdentityKey}@@${row.archetype_id}`,
    active_in_v1: true,
    active_effective_credit: overrides.active_effective_credit,
    pm_multi_membership_status: overrides.pm_multi_membership_status,
    pass_c_zero_credit_before_pm_decision: Boolean(overrides.pass_c_zero_credit_before_pm_decision),
  };
}

function identityKey(row) {
  return [row.candidate_type, normKey(row.artist_display_name), normKey(row.title)].join("|");
}

function normKey(value) {
  return String(value ?? "")
    .toLowerCase()
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/&/g, "and")
    .replace(/[^a-z0-9]+/g, " ")
    .trim()
    .replace(/^the\s+/, "")
    .replace(/\s+/g, " ");
}

function collisionKey(row) {
  return `${row.source_file}@@${row.source_index}@@${row.identity_key}@@${row.archetype_id}`;
}

function multiMembershipKey(row) {
  return `${row.source_file}@@${row.identity_key ?? row.candidate_identity_key}@@${row.archetype_id}`;
}

function classSplit(row) {
  if (row.import_class === "core_graph_playable" && ["song", "recording"].includes(row.candidate_type)) return "playable_songs";
  if (row.import_class === "core_graph_album") return "albums";
  if (row.import_class === "boundary_candidate") return "boundary";
  if (row.import_class === "false_nearby_candidate") return "false_nearby";
  if (row.import_class === "context_candidate") return "context_candidates";
  return null;
}

function buildPassDAudit(auditRows, passCRows) {
  const approvedCollisionRowsByArchetype = new Map();
  for (const row of passCRows) {
    if (row.pm_multi_membership_status !== "pm_approved_multi_membership") continue;
    const stats = approvedCollisionRowsByArchetype.get(row.archetype_id) ?? {
      total: 0,
      playable_songs: 0,
      albums: 0,
      boundary: 0,
      false_nearby: 0,
      context_candidates: 0,
    };
    stats.total += 1;
    const split = classSplit(row);
    if (split) stats[split] += 1;
    approvedCollisionRowsByArchetype.set(row.archetype_id, stats);
  }

  return auditRows.map((row) => {
    const approved = approvedCollisionRowsByArchetype.get(row.archetype_id) ?? {
      total: 0,
      playable_songs: 0,
      albums: 0,
      boundary: 0,
      false_nearby: 0,
      context_candidates: 0,
    };
    const effectiveMissionCountAfterPassD = row.effective_mission_count_after_pass_c + approved.total;
    const effectiveGapAfterPassD = Math.max(0, row.effective_target - effectiveMissionCountAfterPassD);
    return {
      archetype_id: row.archetype_id,
      family_number: row.family_number,
      archetype: row.archetype,
      high_traffic: row.high_traffic,
      effective_target: row.effective_target,
      effective_mission_count_before_pass_c: row.effective_mission_count,
      effective_mission_count_after_pass_c: row.effective_mission_count_after_pass_c,
      pm_approved_multi_membership_credit: approved.total,
      effective_mission_count_after_pass_d: effectiveMissionCountAfterPassD,
      effective_gap_after_pass_d: effectiveGapAfterPassD,
      playable_songs_after_pass_d: row.playable_songs_after_pass_c + approved.playable_songs,
      albums_after_pass_d: row.albums_after_pass_c + approved.albums,
      artist_anchors_after_pass_d: row.artist_anchors_after_pass_c,
      boundary_after_pass_d: row.boundary_after_pass_c + approved.boundary,
      false_nearby_after_pass_d: row.false_nearby_after_pass_c + approved.false_nearby,
      context_candidates_after_pass_d: row.context_candidates_after_pass_c + approved.context_candidates,
      risky_unresolved_after_pass_d: row.risky_unresolved_after_pass_c,
      pass_d_status: effectiveGapAfterPassD === 0 ? "mission_effective_ready" : "gap_remaining",
    };
  });
}

function buildPMDecisionRows(duplicateRows, passCRows) {
  const rowByCollisionKey = new Map(passCRows.map((row) => [multiMembershipKey(row), row]));
  return duplicateRows.map((row) => {
    const activeRow = rowByCollisionKey.get(multiMembershipKey(row));
    return {
      identity_key: row.identity_key,
      candidate_type: activeRow?.candidate_type ?? row.identity_key.split("|")[0],
      artist_display_name: activeRow?.artist_display_name ?? "",
      title: activeRow?.title ?? "",
      year: activeRow?.year ?? "",
      existing_archetype_id: row.existing_archetype_id,
      existing_archetype: archetypeNameById.get(row.existing_archetype_id) ?? "",
      approved_archetype_id: row.archetype_id,
      approved_archetype: archetypeNameById.get(row.archetype_id) ?? "",
      source_file: row.source_file,
      decision: "approved_active_multi_membership",
      active_effective_credit: 1,
      notes: "PM decision: all 13 current-identity collisions should live in both archetypes.",
    };
  });
}

function buildGraphLinkingNodeSet(rows) {
  const nodes = new Map();
  for (const row of rows) {
    const node = nodes.get(row.candidate_identity_key) ?? {
      candidate_identity_key: row.candidate_identity_key,
      candidate_type: row.candidate_type,
      artist_display_name: row.artist_display_name,
      title: row.title,
      year: row.year,
      membership_count: 0,
      active_effective_credit_total: 0,
      archetype_ids: new Set(),
      archetypes: new Set(),
      import_classes: new Set(),
      source_layers: new Set(),
      pm_multi_membership_statuses: new Set(),
      version_or_composition_risks: new Set(),
      risk_statuses: new Set(),
    };
    node.membership_count += 1;
    node.active_effective_credit_total += row.active_effective_credit;
    node.archetype_ids.add(row.archetype_id);
    node.archetypes.add(row.primary_archetype);
    node.import_classes.add(row.import_class);
    node.source_layers.add(row.source_layer);
    node.pm_multi_membership_statuses.add(row.pm_multi_membership_status);
    node.version_or_composition_risks.add(row.version_or_composition_risk);
    node.risk_statuses.add(row.risk_status);
    nodes.set(row.candidate_identity_key, node);
  }

  return [...nodes.values()].map((node) => ({
    candidate_identity_key: node.candidate_identity_key,
    candidate_type: node.candidate_type,
    artist_display_name: node.artist_display_name,
    title: node.title,
    year: node.year,
    membership_count: node.membership_count,
    active_effective_credit_total: node.active_effective_credit_total,
    archetype_ids: [...node.archetype_ids].sort(),
    archetypes: [...node.archetypes].sort(),
    import_classes: [...node.import_classes].sort(),
    source_layers: [...node.source_layers].sort(),
    pm_multi_membership_statuses: [...node.pm_multi_membership_statuses].sort(),
    version_or_composition_risks: [...node.version_or_composition_risks].sort(),
    risk_statuses: [...node.risk_statuses].sort(),
  })).sort((a, b) => a.candidate_identity_key.localeCompare(b.candidate_identity_key));
}

function artifactList() {
  return [
    "graph_hardening_v1_active_inventory.json",
    "graph_hardening_v1_active_inventory.csv",
    "graph_tagging_corpus_v1.json",
    "graph_tagging_corpus_v1.csv",
    "apple_id_resolution_queue_v1.json",
    "apple_id_resolution_queue_v1.csv",
    "album_sidecar_seed_albums_v1.json",
    "album_sidecar_seed_albums_v1.csv",
    "graph_linking_node_set_v1.json",
    "graph_linking_node_set_v1.csv",
    "atlas_archetype_profile_targets_v1.json",
    "atlas_archetype_profile_targets_v1.csv",
    "pm_multi_membership_decisions_v1.json",
    "pm_multi_membership_decisions_v1.csv",
    "graph_hardening_pass_d_freeze_manifest.json",
    "graph_hardening_pass_d_freeze_manifest.md",
  ];
}

function writeMarkdown() {
  const decisionRows = pmMultiMembershipDecisions
    .map((row) =>
      `| ${row.artist_display_name} - ${row.title} | ${row.existing_archetype_id} ${row.existing_archetype} | ${row.approved_archetype_id} ${row.approved_archetype} | ${row.decision} |`,
    )
    .join("\n");

  const markdown = `# Graph Hardening Pass D Freeze Manifest

Generated on ${generatedOn}.

## Status

Pass D is frozen with PM-approved multi-memberships.

- Archetypes ready: ${summary.archetypes_ready} / 120
- Remaining effective gap: ${summary.remaining_effective_gap}
- Active inventory rows: ${summary.active_inventory_rows}
- Active Pass C rows: ${summary.active_pass_c_rows}
- Approved multi-memberships: ${summary.approved_multi_memberships}
- Song tagging corpus rows: ${summary.tagging_corpus_rows}
- Album sidecar seed rows: ${summary.album_sidecar_seed_rows}
- Apple ID resolution queue rows: ${summary.apple_id_resolution_queue_rows}
- Graph-linking node rows: ${summary.graph_linking_node_rows}
- Unresolved rows excluded from v1: ${summary.unresolved_rows_excluded_from_v1}

## PM Decision

All 13 current-identity collisions from Pass C are approved as active multi-memberships in v1. They now live in both the existing archetype and the proposed archetype, with active effective credit in the approved archetype.

| Candidate | Existing membership | Approved added membership | Decision |
| --- | --- | --- | --- |
${decisionRows}

## Downstream Corpora

- \`graph_tagging_corpus_v1\`: song/recording rows ready for tagging.
- \`apple_id_resolution_queue_v1\`: song/recording rows ready for Apple ID matching.
- \`album_sidecar_seed_albums_v1\`: album rows ready for album sidecar planning.
- \`atlas_archetype_profile_targets_v1\`: final archetype readiness/profile targets.
- \`graph_linking_node_set_v1\`: identity-level graph nodes with active archetype memberships.

## Exclusions

Rows with \`needs_resolution\`, \`exclude_or_quarantine\`, or \`risky_unresolved\` status remain outside v1 downstream tagging/linking/resolution.
`;
  fs.writeFileSync(path.join(passD, "graph_hardening_pass_d_freeze_manifest.md"), markdown);
}

function toCsv(rows) {
  if (rows.length === 0) return "";
  const columns = [...rows.reduce((set, row) => {
    Object.keys(row).forEach((key) => set.add(key));
    return set;
  }, new Set())];
  const lines = [
    columns.join(","),
    ...rows.map((row) => columns.map((column) => csvCell(row[column])).join(",")),
  ];
  return `${lines.join("\n")}\n`;
}

function csvCell(value) {
  const text = Array.isArray(value) ? value.join("; ") : String(value ?? "");
  return /[",\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
}
