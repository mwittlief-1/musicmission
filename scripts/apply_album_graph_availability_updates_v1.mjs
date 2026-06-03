#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

const repoRoot = process.cwd();
const canonicalRoot = path.join(repoRoot, "data/canonical_graph");
const passD = path.join(canonicalRoot, "depth_hardening_v0_2/pass_d");
const current = path.join(canonicalRoot, "current");

const patchSummary = {
  id: "album_graph_availability_updates_v1",
  applied_on: "2026-05-27",
  status: "applied",
  intent:
    "Post-freeze availability patch for Apple-resolvable album sidecar execution while preserving source-intent aliases in notes.",
  actions: [
    "replace_title_keep_role",
    "replace_active_album_preserve_historical_original",
    "demote_to_special_entity_no_album_sidecar",
    "bad_match_replace_with_swum_2018_album_anchor",
    "normalize_title_year_catalog_alias",
    "historical_unavailable_split_replacement",
    "correct_artist_keep_album",
  ],
};

const rowUpdates = [
  {
    membershipId: "v1m_00332",
    importAction: "replace_title_keep_role",
    fields: {
      artist_display_name: "Various Artists",
      title: "Essential Sun Rockabillies, Vol. 1",
      year: 2006,
      why_it_belongs: "Apple-resolvable Sun/Charly rockabilly compilation keeps the Sun Records gateway role for Page 2.",
      notes:
        "Availability replacement for source-intent title The Sun Rockabilly Years (1980); active Apple sidecar object is Essential Sun Rockabillies, Vol. 1.",
    },
  },
  {
    membershipId: "v1m_00336",
    importAction: "replace_title_keep_role",
    fields: {
      artist_display_name: "The Five Satins",
      title: "50 Best Hits (2023 Remastered)",
      year: 1965,
      notes:
        "Availability replacement for source-intent title Golden Hits; active Apple sidecar object is 50 Best Hits (2023 Remastered).",
    },
  },
  {
    membershipId: "v1m_00342",
    importAction: "replace_active_album_preserve_historical_original",
    fields: {
      artist_display_name: "Little Anthony and the Imperials",
      title: "The Greatest Hits of Little Anthony and the Imperials",
      year: 2005,
      why_it_belongs:
        "Concise Apple-resolvable Rhino compilation preserves the doo-wop-to-soul gateway role when the 1959 LP is not reliably Apple-US available.",
      notes:
        "Active Apple sidecar replacement; preserve We Are the Imperials Featuring Little Anthony (1959) as historical_original_album_alias/source intent.",
    },
  },
  {
    membershipId: "v1m_00365",
    importAction: "red_bird_split_replacement_dixie_cups",
    fields: {
      artist_display_name: "The Dixie Cups",
      title: "The Very Best of The Dixie Cups: Chapel of Love",
      year: 1999,
      why_it_belongs:
        "Apple-resolvable Dixie Cups best-of preserves the Red Bird / girl-group gateway while staying mission-playable.",
      notes:
        "Availability replacement for Chapel of Love source LP and part of The Red Bird Girls split replacement coverage.",
    },
  },
  {
    membershipId: "v1m_00368",
    importAction: "red_bird_split_replacement_shangri_las",
    fields: {
      artist_display_name: "The Shangri-Las",
      title: "20th Century Masters - The Millennium Collection: The Best of The Shangri-Las",
      year: 2002,
      why_it_belongs:
        "Apple-resolvable Shangri-Las best-of preserves the dramatic teen-pop side of the Red Bird / girl-group gateway.",
      notes:
        "Availability replacement for Leader of the Pack source LP/title and part of The Red Bird Girls split replacement coverage.",
    },
  },
  {
    membershipId: "v1m_00378",
    importAction: "historical_unavailable_split_replacement",
    fields: {
      candidate_type: "artist_anchor",
      artist_display_name: "Red Bird Records",
      title: "The Red Bird Girls",
      year: 1990,
      mission_role: "album_world",
      import_class: "artist_anchor",
      why_it_belongs:
        "Historical Red Bird / girl-group label-scene intent is retained as graph context; active album sidecar coverage is split through Dixie Cups and Shangri-Las Apple-resolvable objects.",
      notes:
        "Demoted from album sidecar: exact The Red Bird Girls compilation is not a stable US Apple target. Active split replacements: The Dixie Cups - The Very Best of The Dixie Cups: Chapel of Love; The Shangri-Las - 20th Century Masters - The Millennium Collection: The Best of The Shangri-Las.",
    },
  },
  {
    membershipId: "v1m_00403",
    importAction: "correct_artist_keep_album",
    fields: {
      artist_display_name: "Jan & Dean",
      title: "Ride the Wild Surf",
      year: 1964,
      notes:
        "Corrected active Apple attribution from Various Artists to Jan & Dean; keep surf / early guitar-pop bridge with soundtrack/movie-tie-in risk note.",
    },
  },
  {
    membershipId: "v1m_04437",
    importAction: "normalize_title_year_catalog_alias",
    fields: {
      artist_display_name: "Various Artists",
      title: "Children's Favorites, Vol. 1",
      year: 2008,
      notes:
        "Active Apple catalog normalization for Disney Children's Favorites source intent; preserve 1979 original-lineage alias.",
    },
  },
  {
    membershipId: "v1m_04585",
    importAction: "demote_to_special_entity_no_album_sidecar",
    fields: {
      candidate_type: "artist_anchor",
      artist_display_name: "Lo-fi Girl",
      title: "lofi hip hop radio",
      year: 2017,
      import_class: "artist_anchor",
      mission_role: "false_nearby",
      why_it_belongs:
        "Retains Lo-fi Girl / lofi hip hop radio as a special context entity for algorithmic mood routing without treating the livestream or playlist as an album.",
      notes:
        "Demoted from album sidecar: lofi hip hop radio is a playlist/channel/use-case object, not a concrete album.",
    },
  },
  {
    membershipId: "v1m_11685",
    importAction: "bad_match_replace_with_swum_2018_album_anchor",
    fields: {
      artist_display_name: "SwuM",
      title: "Swum",
      year: 2018,
      why_it_belongs:
        "SwuM - Swum adds a resolved album-world row for Algorithmic Mood / Lo-Fi / Chill / Study Music, useful when missions need a durable album context rather than a single-track surface.",
      notes:
        "Availability correction for bad source title Wishful Thinking; active Apple album anchor is SwuM - Swum (2018).",
    },
  },
];

const manualOverrideUpdates = [
  {
    oldKey: "album|various artists|sun rockabilly years",
    next: override("album|various artists|essential sun rockabillies vol 1", 156819935, "https://music.apple.com/us/album/essential-sun-rockabillies-vol-1/156819935", "medium", "replace_title_keep_role", "Active Apple-resolvable Sun/Charly comp. Preserve The Sun Rockabilly Years as source-intent/historical alias."),
  },
  {
    oldKey: "album|five satins|golden hits",
    next: override("album|five satins|50 best hits 2023 remastered", 1715543363, "https://music.apple.com/us/album/50-best-hits-2023-remastered/1715543363", "medium", "replace_title_keep_role", "Active Apple availability replacement. Preserve Golden Hits as source-intent alias."),
  },
  {
    oldKey: "album|little anthony and the imperials|we are the imperials featuring little anthony",
    next: override("album|little anthony and the imperials|greatest hits of little anthony and the imperials", 80004926, "https://music.apple.com/us/album/the-greatest-hits-of-little-anthony-and-the-imperials/80004926", "medium", "replace_active_album_preserve_historical_original", "Use concise Apple-resolvable Rhino compilation as active sidecar object. Preserve 1959 LP as historical_original_album_alias."),
  },
  {
    oldKey: null,
    next: override("album|dixie cups|very best of the dixie cups chapel of love", 1881889298, "https://music.apple.com/us/album/the-very-best-of-the-dixie-cups-chapel-of-love/1881889298", "medium", "historical_unavailable_split_replacement", "Red Bird Girls split replacement: Dixie Cups Apple-resolvable best-of."),
  },
  {
    oldKey: null,
    next: override("album|shangri las|20th century masters the millennium collection the best of the shangri las", 1444000328, "https://music.apple.com/us/album/20th-century-masters-the-millennium-collection-the/1444000328", "medium", "historical_unavailable_split_replacement", "Red Bird Girls split replacement: Shangri-Las Apple-resolvable best-of."),
  },
  {
    oldKey: "album|various artists|ride the wild surf",
    next: override("album|jan and dean|ride the wild surf", 715562999, "https://music.apple.com/us/album/ride-the-wild-surf/715562999", "high", "correct_artist_keep_album", "Correct active Apple attribution to Jan & Dean; keep soundtrack/movie-tie-in risk note."),
  },
  {
    oldKey: "album|various artists|disney children s favorites",
    next: override("album|various artists|children s favorites vol 1", 1440798564, "https://music.apple.com/us/album/childrens-favorites-vol-1/1440798564", "medium", "normalize_title_year_catalog_alias", "Accepted active Apple object. Preserve 1979 original-lineage alias/source intent."),
  },
  {
    oldKey: "album|swum|wishful thinking",
    next: override("album|swum|swum", 1754636804, "https://music.apple.com/us/album/swum/1754636804", "medium", "bad_match_replace_with_swum_2018_album_anchor", "Replace bad Wishful Thinking album row with SwuM - Swum (2018) Apple album anchor."),
  },
];

const manualOverrideRemovals = new Set([
  "album|lo fi girl|lofi hip hop radio",
  "album|various artists|red bird girls",
]);

const activeInventoryPath = path.join(passD, "graph_hardening_v1_active_inventory.json");
const activeInventory = readJson(activeInventoryPath);
const activeRows = activeInventory.rows;
const appliedRows = [];

for (const update of rowUpdates) {
  const row = activeRows.find((candidate) => candidate.v1_membership_id === update.membershipId);
  if (!row) throw new Error(`Missing active inventory row ${update.membershipId}`);
  Object.assign(row, update.fields);
  row.candidate_identity_key = identityKey(row);
  row.archetype_membership_key = `${row.candidate_identity_key}@@${row.archetype_id}`;
  row.active_in_v1 = true;
  row.active_effective_credit = Number(row.active_effective_credit ?? 1);
  row.pm_multi_membership_status = row.pm_multi_membership_status || "not_applicable";
  row.pass_c_zero_credit_before_pm_decision = Boolean(row.pass_c_zero_credit_before_pm_decision);
  appliedRows.push({
    v1_membership_id: row.v1_membership_id,
    import_action: update.importAction,
    candidate_identity_key: row.candidate_identity_key,
    candidate_type: row.candidate_type,
    artist_display_name: row.artist_display_name,
    title: row.title,
    year: row.year,
  });
}

const albumSeeds = buildAlbumSidecarSeeds(activeRows);
const graphLinkingRows = buildGraphLinkingNodeSet(activeRows);
const profileTargets = patchProfileTargets(readJson(path.join(passD, "atlas_archetype_profile_targets_v1.json")).rows);
const passDManifest = readJson(path.join(passD, "graph_hardening_pass_d_freeze_manifest.json"));
const nextMetadata = patchMetadata(passDManifest.metadata, {
  active_inventory_rows: activeRows.length,
  album_sidecar_seed_rows: albumSeeds.length,
  graph_linking_node_rows: graphLinkingRows.length,
});

writeJson(path.join(passD, "graph_hardening_v1_active_inventory.json"), { metadata: nextMetadata, rows: activeRows });
writeCsv(path.join(passD, "graph_hardening_v1_active_inventory.csv"), activeRows);
writeJson(path.join(passD, "album_sidecar_seed_albums_v1.json"), { metadata: nextMetadata, rows: albumSeeds });
writeCsv(path.join(passD, "album_sidecar_seed_albums_v1.csv"), albumSeeds);
writeJson(path.join(passD, "graph_linking_node_set_v1.json"), { metadata: nextMetadata, rows: graphLinkingRows });
writeCsv(path.join(passD, "graph_linking_node_set_v1.csv"), graphLinkingRows);
writeJson(path.join(passD, "atlas_archetype_profile_targets_v1.json"), { metadata: nextMetadata, rows: profileTargets });
writeCsv(path.join(passD, "atlas_archetype_profile_targets_v1.csv"), profileTargets);
writeJson(path.join(passD, "graph_hardening_pass_d_freeze_manifest.json"), {
  ...passDManifest,
  metadata: nextMetadata,
});
writeJson(path.join(passD, "album_graph_availability_updates_v1.json"), {
  metadata: patchSummary,
  rows: appliedRows,
});
writeFreezeMarkdown(path.join(passD, "graph_hardening_pass_d_freeze_manifest.md"), nextMetadata);

patchManualAppleOverrides(path.join(passD, "album_track_sidecar_manual_apple_overrides_v1.json"));
promotePatchedArtifacts(nextMetadata);

console.log(JSON.stringify({
  ok: true,
  patch: patchSummary.id,
  updated_rows: appliedRows.length,
  active_inventory_rows: activeRows.length,
  album_sidecar_seed_rows: albumSeeds.length,
  graph_linking_node_rows: graphLinkingRows.length,
}, null, 2));

function override(candidate_identity_key, apple_collection_id, apple_url, confidence, import_action, notes) {
  return {
    candidate_identity_key,
    status: "apply",
    apple_collection_id,
    apple_url,
    country: "US",
    confidence,
    import_action,
    notes,
  };
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function writeJson(file, value) {
  fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`);
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

function buildAlbumSidecarSeeds(rows) {
  return rows
    .filter((row) =>
      row.candidate_type === "album" &&
      ["core_graph_album", "boundary_candidate", "false_nearby_candidate", "context_candidate"].includes(row.import_class) &&
      row.risk_status !== "risky_unresolved",
    )
    .map((row) => ({
      ...row,
      sidecar_scope: row.import_class === "core_graph_album" ? "core_album_sidecar" : "context_boundary_album_sidecar",
    }));
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
    node.active_effective_credit_total += Number(row.active_effective_credit ?? 0);
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

function patchProfileTargets(rows) {
  return rows.map((row) => {
    if (row.archetype_id === "005") {
      return {
        ...row,
        albums_after_pass_d: Number(row.albums_after_pass_d) - 1,
        artist_anchors_after_pass_d: Number(row.artist_anchors_after_pass_d) + 1,
      };
    }
    if (row.archetype_id === "120") {
      return {
        ...row,
        albums_after_pass_d: Number(row.albums_after_pass_d) - 1,
        artist_anchors_after_pass_d: Number(row.artist_anchors_after_pass_d) + 1,
      };
    }
    return row;
  });
}

function patchMetadata(metadata, counts) {
  return {
    ...metadata,
    ...counts,
    post_freeze_availability_patch: patchSummary,
  };
}

function patchManualAppleOverrides(file) {
  const document = readJson(file);
  const updatesByOldKey = new Map(manualOverrideUpdates.filter((entry) => entry.oldKey).map((entry) => [entry.oldKey, entry.next]));
  const additions = manualOverrideUpdates.filter((entry) => !entry.oldKey).map((entry) => entry.next);
  const nextKeys = new Set(manualOverrideUpdates.map((entry) => entry.next.candidate_identity_key));
  const seenNextKeys = new Set();
  const overrides = [];

  for (const row of document.overrides ?? []) {
    if (manualOverrideRemovals.has(row.candidate_identity_key)) continue;
    const replacement = updatesByOldKey.get(row.candidate_identity_key);
    if (replacement) {
      overrides.push(replacement);
      seenNextKeys.add(replacement.candidate_identity_key);
      continue;
    }
    if (nextKeys.has(row.candidate_identity_key)) continue;
    overrides.push(row);
  }

  for (const addition of additions) {
    if (seenNextKeys.has(addition.candidate_identity_key)) continue;
    overrides.push(addition);
    seenNextKeys.add(addition.candidate_identity_key);
  }

  writeJson(file, {
    metadata: {
      ...document.metadata,
      post_freeze_availability_patch: patchSummary,
    },
    overrides,
  });
}

function promotePatchedArtifacts(metadata) {
  const artifactMap = [
    ["graph_hardening_v1_active_inventory.json", "canonical_graph_active_inventory.json"],
    ["graph_hardening_v1_active_inventory.csv", "canonical_graph_active_inventory.csv"],
    ["album_sidecar_seed_albums_v1.json", "album_sidecar_seed_albums.json"],
    ["album_sidecar_seed_albums_v1.csv", "album_sidecar_seed_albums.csv"],
    ["atlas_archetype_profile_targets_v1.json", "atlas_archetype_profile_targets.json"],
    ["atlas_archetype_profile_targets_v1.csv", "atlas_archetype_profile_targets.csv"],
    ["graph_linking_node_set_v1.json", "graph_linking_node_set.json"],
    ["graph_linking_node_set_v1.csv", "graph_linking_node_set.csv"],
    ["graph_hardening_pass_d_freeze_manifest.json", "canonical_graph_freeze_manifest.json"],
    ["graph_hardening_pass_d_freeze_manifest.md", "canonical_graph_freeze_manifest.md"],
    ["album_graph_availability_updates_v1.json", "album_graph_availability_updates_v1.json"],
  ];

  for (const [sourceName, targetName] of artifactMap) {
    fs.copyFileSync(path.join(passD, sourceName), path.join(current, targetName));
  }

  for (const file of [
    path.join(current, "canonical_graph_source_of_truth_manifest.json"),
    path.join(canonicalRoot, "canonical_graph_source_of_truth_manifest.json"),
  ]) {
    const manifest = readJson(file);
    manifest.counts = {
      ...manifest.counts,
      active_inventory_rows: metadata.active_inventory_rows,
      album_sidecar_seed_rows: metadata.album_sidecar_seed_rows,
      graph_linking_node_rows: metadata.graph_linking_node_rows,
    };
    manifest.post_freeze_availability_patch = patchSummary;
    writeJson(file, manifest);
  }

  updateCurrentMarkdown(path.join(canonicalRoot, "CURRENT_CANONICAL_GRAPH.md"), metadata);
  updateCurrentMarkdown(path.join(current, "README.md"), metadata);
}

function writeFreezeMarkdown(file, metadata) {
  let text = fs.readFileSync(file, "utf8");
  text = text
    .replace(/- Active inventory rows: \d+/, `- Active inventory rows: ${metadata.active_inventory_rows}`)
    .replace(/- Album sidecar seed rows: \d+/, `- Album sidecar seed rows: ${metadata.album_sidecar_seed_rows}`)
    .replace(/- Graph-linking node rows: \d+/, `- Graph-linking node rows: ${metadata.graph_linking_node_rows}`);

  if (!text.includes("## Post-Freeze Availability Patch")) {
    text += `
## Post-Freeze Availability Patch

- Patch: \`${patchSummary.id}\`
- Applied on: ${patchSummary.applied_on}
- Updated rows: ${appliedRows.length}
- Album sidecar seed rows after patch: ${metadata.album_sidecar_seed_rows}
`;
  }
  fs.writeFileSync(file, text);
}

function updateCurrentMarkdown(file, metadata) {
  let text = fs.readFileSync(file, "utf8");
  text = text
    .replace(/- Active inventory rows: \d+/, `- Active inventory rows: ${metadata.active_inventory_rows}`)
    .replace(/- Album sidecar seed rows: \d+/, `- Album sidecar seed rows: ${metadata.album_sidecar_seed_rows}`)
    .replace(/- Graph-linking node rows: \d+/, `- Graph-linking node rows: ${metadata.graph_linking_node_rows}`);

  if (!text.includes("## Post-Freeze Availability Patch")) {
    text += `
## Post-Freeze Availability Patch

- Patch: \`${patchSummary.id}\`
- Applied on: ${patchSummary.applied_on}
- Intent: ${patchSummary.intent}
`;
  }
  fs.writeFileSync(file, text);
}

function writeCsv(file, rows) {
  fs.writeFileSync(file, toCsv(rows));
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
