#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

const repoRoot = process.cwd();
const canonicalRoot = path.join(repoRoot, "data/canonical_graph");
const passD = path.join(canonicalRoot, "depth_hardening_v0_2/pass_d");
const current = path.join(canonicalRoot, "current");

const hotfixId = "radiohead_missing_obvious_hotfix_v1";
const appliedOn = "2026-05-31";
const hotfixSourceLayer = "post_freeze_missing_obvious_hotfix";
const hotfixSourceFile = "data/canonical_graph/current/radiohead_missing_obvious_hotfix_v1.json";

const patchIntent =
  "Post-freeze missing-obvious correction for Radiohead coverage in Family 10 while preserving recording/title specificity.";

const family10 = "Alternative, Indie, Grunge, Emo";
const archetypes = {
  "071": "Post-Grunge / Modern Rock Radio",
  "078": "Blog Indie / Prestige Indie / 2000s Indie Rock",
};

const rowDefinitions = [
  artist("078", "Radiohead", "Radiohead", null, "obvious", "bridge", "artist_anchor",
    "Missing-obvious alternative/art-rock survey anchor linking 90s modern-rock recognition, album-world listening, 2000s prestige indie, and electronic-rock boundary tests.",
    "Keep Radiohead distinct from Thom Yorke solo and The Smile. Do not infer broad Radiohead appetite from Creep alone."),
  album("071", "Radiohead", "The Bends", 1995, "obvious", "bridge", "core_graph_album",
    "90s guitar-song Radiohead gateway for modern-rock and alternative-radio branching.",
    "Useful as a route bridge from Creep/Fake Plastic Trees into later album-world Radiohead."),
  album("078", "Radiohead", "OK Computer", 1997, "obvious", "album_world", "core_graph_album",
    "Core album-world Radiohead anchor for art-rock, alternative canon, and prestige-indie lineage.",
    "Primary album-world object; keep album reaction separate from song-first Creep recognition."),
  album("078", "Radiohead", "Kid A", 2000, "obvious", "album_world", "core_graph_album",
    "Boundary-shifting album-world object for electronic-rock, abstraction tolerance, and post-OK Computer branching.",
    "Do not treat a Kid A positive as generic guitar-rock appetite."),
  album("078", "Radiohead", "In Rainbows", 2007, "obvious", "album_world", "core_graph_album",
    "Later Radiohead album-world gateway with warmer songcraft and art-rock accessibility.",
    "Useful contrast against both OK Computer architecture and Kid A abstraction."),
  song("071", "Radiohead", "Creep", 1992, "obvious", "bridge", "core_graph_playable", "same_title",
    "Mass-recognition Radiohead song-first gateway and modern-rock branch point.",
    "Same-title collision with TLC - Creep; distinct composition and recording. Do not merge by title. Do not infer broad Radiohead appetite from Creep alone."),
  song("071", "Radiohead", "Fake Plastic Trees", 1995, "obvious", "bridge", "core_graph_playable", "none",
    "High-recognition melodic bridge from The Bends into vulnerable alternative songcraft.",
    "Useful positive signal for Radiohead songcraft, but not sufficient evidence for Kid A-style abstraction."),
  song("078", "Radiohead", "Paranoid Android", 1997, "obvious", "boundary_case", "core_graph_playable", "none",
    "Canonical OK Computer suite and a strong test for art-rock structure tolerance.",
    "Long-form/sectional response should not be collapsed into generic 90s alternative appetite."),
  song("078", "Radiohead", "Karma Police", 1997, "obvious", "bridge", "core_graph_playable", "none",
    "Recognizable OK Computer song gateway with broad survey branching value.",
    "Keep as song-level bridge even when OK Computer is also an album-world object."),
  song("078", "Radiohead", "No Surprises", 1997, "obvious", "bridge", "core_graph_playable", "none",
    "Melodic OK Computer entry point that tests quiet dread, beauty, and soft-focus recognition.",
    "Do not over-infer appetite for the band's harsher or more abstract side."),
  song("078", "Radiohead", "Everything in Its Right Place", 2000, "obvious", "boundary_case", "core_graph_playable", "none",
    "Kid A entry point for electronic texture, repetition, and post-rock abstraction tolerance.",
    "Positive signal should branch toward electronic/post-rock boundary checks rather than ordinary modern-rock radio by default."),
  song("078", "Radiohead", "Idioteque", 2000, "obvious", "boundary_case", "boundary_candidate", "none",
    "Sharper Kid A boundary probe for electronic pulse, anxiety, and anti-guitar Radiohead.",
    "Use as a boundary/probe row; do not treat as a standard recommendation unless the route asks that question."),
  song("078", "Radiohead", "Weird Fishes/Arpeggi", 2007, "obvious", "deep_cut", "core_graph_playable", "none",
    "In Rainbows song-level bridge for later Radiohead warmth, motion, and fan-recognized album depth.",
    "More album-world than mass-radio; keep survey use adaptive rather than default Page 1 unless user signals fit."),
];

const activeInventoryPath = path.join(passD, "graph_hardening_v1_active_inventory.json");
const activeInventory = readJson(activeInventoryPath);
const passDManifestPath = path.join(passD, "graph_hardening_pass_d_freeze_manifest.json");
const passDManifest = readJson(passDManifestPath);
const previousHotfix = passDManifest.metadata.post_freeze_radiohead_hotfix;
const previousRows = activeInventory.rows.filter((row) => row.source_layer === hotfixSourceLayer);
const previousIdsByKey = new Map(previousRows.map((row) => [row.candidate_identity_key, row.v1_membership_id]));
const previousDelta = previousHotfix?.profile_target_delta ?? {};
const hotfixKeys = new Set(rowDefinitions.map((row) => identityKey(row)));

const baseRows = activeInventory.rows.filter((row) =>
  row.source_layer !== hotfixSourceLayer && !hotfixKeys.has(row.candidate_identity_key),
);
const nextIdStart = nextMembershipNumber(baseRows);
const addedRows = rowDefinitions.map((definition, index) => {
  const key = identityKey(definition);
  const id = previousIdsByKey.get(key) ?? `v1m_${String(nextIdStart + index).padStart(5, "0")}`;
  return normalizeHotfixRow(definition, id, index);
});

const activeRows = [...baseRows, ...addedRows].sort(compareMembershipId);
const taggingCorpus = buildTaggingCorpus(activeRows);
const appleIdResolutionQueue = buildAppleIdResolutionQueue(taggingCorpus);
const albumSeeds = buildAlbumSidecarSeeds(activeRows);
const graphLinkingRows = buildGraphLinkingNodeSet(activeRows);
const profileDelta = buildProfileTargetDelta(addedRows);
const profileTargets = patchProfileTargets(
  readJson(path.join(passD, "atlas_archetype_profile_targets_v1.json")).rows,
  previousDelta,
  profileDelta,
);

const patchSummary = {
  id: hotfixId,
  applied_on: appliedOn,
  status: "applied",
  intent: patchIntent,
  row_count: addedRows.length,
  artist_anchor_rows: addedRows.filter((row) => row.candidate_type === "artist_anchor").length,
  album_rows: addedRows.filter((row) => row.candidate_type === "album").length,
  song_rows: addedRows.filter((row) => row.candidate_type === "song").length,
  profile_target_delta: profileDelta,
  actions: [
    "add_missing_obvious_artist_anchor",
    "add_album_world_rows",
    "add_song_gateway_rows",
    "preserve_creep_same_title_do_not_merge",
  ],
};

const nextMetadata = patchMetadata(passDManifest.metadata, {
  active_inventory_rows: activeRows.length,
  tagging_corpus_rows: taggingCorpus.length,
  apple_id_resolution_queue_rows: appleIdResolutionQueue.length,
  album_sidecar_seed_rows: albumSeeds.length,
  graph_linking_node_rows: graphLinkingRows.length,
});

writeJson(path.join(passD, "graph_hardening_v1_active_inventory.json"), { metadata: nextMetadata, rows: activeRows });
writeCsv(path.join(passD, "graph_hardening_v1_active_inventory.csv"), activeRows);
writeJson(path.join(passD, "graph_tagging_corpus_v1.json"), { metadata: nextMetadata, rows: taggingCorpus });
writeCsv(path.join(passD, "graph_tagging_corpus_v1.csv"), taggingCorpus);
writeJson(path.join(passD, "apple_id_resolution_queue_v1.json"), { metadata: nextMetadata, rows: appleIdResolutionQueue });
writeCsv(path.join(passD, "apple_id_resolution_queue_v1.csv"), appleIdResolutionQueue);
writeJson(path.join(passD, "album_sidecar_seed_albums_v1.json"), { metadata: nextMetadata, rows: albumSeeds });
writeCsv(path.join(passD, "album_sidecar_seed_albums_v1.csv"), albumSeeds);
writeJson(path.join(passD, "graph_linking_node_set_v1.json"), { metadata: nextMetadata, rows: graphLinkingRows });
writeCsv(path.join(passD, "graph_linking_node_set_v1.csv"), graphLinkingRows);
writeJson(path.join(passD, "atlas_archetype_profile_targets_v1.json"), { metadata: nextMetadata, rows: profileTargets });
writeCsv(path.join(passD, "atlas_archetype_profile_targets_v1.csv"), profileTargets);
writeJson(passDManifestPath, {
  ...passDManifest,
  metadata: nextMetadata,
  artifacts: [...new Set([...(passDManifest.artifacts ?? []), "radiohead_missing_obvious_hotfix_v1.json"])],
});
writeJson(path.join(passD, "radiohead_missing_obvious_hotfix_v1.json"), {
  metadata: patchSummary,
  rows: addedRows,
});
writeFreezeMarkdown(path.join(passD, "graph_hardening_pass_d_freeze_manifest.md"), nextMetadata);
patchFamily10Normalized();
promotePatchedArtifacts(nextMetadata);

console.log(JSON.stringify({
  ok: true,
  patch: hotfixId,
  added_rows: addedRows.length,
  active_inventory_rows: activeRows.length,
  tagging_corpus_rows: taggingCorpus.length,
  apple_id_resolution_queue_rows: appleIdResolutionQueue.length,
  album_sidecar_seed_rows: albumSeeds.length,
  graph_linking_node_rows: graphLinkingRows.length,
}, null, 2));

function artist(archetypeId, artistName, title, year, recognitionBand, missionRole, importClass, whyItBelongs, notes) {
  return baseRow(archetypeId, "artist_anchor", artistName, title, year, recognitionBand, missionRole, importClass, "none", whyItBelongs, notes);
}

function album(archetypeId, artistName, title, year, recognitionBand, missionRole, importClass, whyItBelongs, notes) {
  return baseRow(archetypeId, "album", artistName, title, year, recognitionBand, missionRole, importClass, "none", whyItBelongs, notes);
}

function song(archetypeId, artistName, title, year, recognitionBand, missionRole, importClass, versionRisk, whyItBelongs, notes) {
  return baseRow(archetypeId, "song", artistName, title, year, recognitionBand, missionRole, importClass, versionRisk, whyItBelongs, notes);
}

function baseRow(archetypeId, candidateType, artistName, title, year, recognitionBand, missionRole, importClass, versionRisk, whyItBelongs, notes) {
  return {
    archetype_id: archetypeId,
    candidate_type: candidateType,
    artist_display_name: artistName,
    title,
    year,
    primary_family: family10,
    primary_archetype: archetypes[archetypeId],
    secondary_archetypes: [],
    recognition_band: recognitionBand,
    mission_role: missionRole,
    import_class: importClass,
    version_or_composition_risk: versionRisk,
    risk_status: "resolved",
    confidence: "high",
    why_it_belongs: whyItBelongs,
    notes,
  };
}

function normalizeHotfixRow(definition, membershipId, index) {
  const candidateIdentityKey = identityKey(definition);
  return {
    v1_membership_id: membershipId,
    source_layer: hotfixSourceLayer,
    source_file: hotfixSourceFile,
    source_index: `radiohead-hotfix-${String(index + 1).padStart(3, "0")}`,
    ...definition,
    candidate_identity_key: candidateIdentityKey,
    archetype_membership_key: `${candidateIdentityKey}@@${definition.archetype_id}`,
    active_in_v1: true,
    active_effective_credit: definition.candidate_type === "artist_anchor" ? 0 : 1,
    pm_multi_membership_status: "not_applicable",
    pass_c_zero_credit_before_pm_decision: false,
  };
}

function buildTaggingCorpus(rows) {
  return rows
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
}

function buildAppleIdResolutionQueue(taggingRows) {
  return taggingRows.map((row) => ({
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

function buildProfileTargetDelta(rows) {
  const delta = {};
  for (const row of rows) {
    const stats = delta[row.archetype_id] ?? {
      effective_mission_count_after_pass_d: 0,
      playable_songs_after_pass_d: 0,
      albums_after_pass_d: 0,
      artist_anchors_after_pass_d: 0,
      boundary_after_pass_d: 0,
      false_nearby_after_pass_d: 0,
      context_candidates_after_pass_d: 0,
    };
    stats.effective_mission_count_after_pass_d += Number(row.active_effective_credit ?? 0);
    if (row.import_class === "core_graph_playable" && ["song", "recording"].includes(row.candidate_type)) {
      stats.playable_songs_after_pass_d += 1;
    } else if (row.import_class === "core_graph_album") {
      stats.albums_after_pass_d += 1;
    } else if (row.import_class === "boundary_candidate") {
      stats.boundary_after_pass_d += 1;
    } else if (row.import_class === "false_nearby_candidate") {
      stats.false_nearby_after_pass_d += 1;
    } else if (row.import_class === "context_candidate") {
      stats.context_candidates_after_pass_d += 1;
    }
    if (row.candidate_type === "artist_anchor") stats.artist_anchors_after_pass_d += 1;
    delta[row.archetype_id] = stats;
  }
  return delta;
}

function patchProfileTargets(rows, previousDelta, nextDelta) {
  const fields = [
    "effective_mission_count_after_pass_d",
    "playable_songs_after_pass_d",
    "albums_after_pass_d",
    "artist_anchors_after_pass_d",
    "boundary_after_pass_d",
    "false_nearby_after_pass_d",
    "context_candidates_after_pass_d",
  ];

  return rows.map((row) => {
    const next = { ...row };
    for (const field of fields) {
      next[field] = Number(next[field] ?? 0) - Number(previousDelta[row.archetype_id]?.[field] ?? 0) + Number(nextDelta[row.archetype_id]?.[field] ?? 0);
    }
    next.effective_gap_after_pass_d = Math.max(0, Number(next.effective_target ?? 0) - Number(next.effective_mission_count_after_pass_d ?? 0));
    next.pass_d_status = next.effective_gap_after_pass_d === 0 ? "mission_effective_ready" : "gap_remaining";
    return next;
  });
}

function patchMetadata(metadata, counts) {
  return {
    ...metadata,
    ...counts,
    post_freeze_radiohead_hotfix: patchSummary,
  };
}

function patchFamily10Normalized() {
  const file = path.join(canonicalRoot, "family_10/normalized_family_10.json");
  const document = readJson(file);

  document.artists = [
    ...document.artists.filter((row) => row.proposed_artist_id !== "radiohead"),
    {
      archetype_id: "078",
      artist_name: "Radiohead",
      proposed_artist_id: "radiohead",
      existing_seed: false,
      recognition_tier: "mass",
      survey_tier: "core",
      roles: ["anchor", "artist_anchor", "bridge"],
      archetype_membership_weight: 0.98,
      inclusion_reason: "Missing-obvious alternative/art-rock anchor connecting 90s modern rock, album-world canon, 2000s prestige indie, and electronic-rock boundary tests.",
      object_specificity_note: "artist_level",
      likely_canonical_albums: ["OK Computer", "Kid A", "In Rainbows", "The Bends"],
      likely_canonical_songs: ["Creep", "Fake Plastic Trees", "Paranoid Android", "Karma Police", "Everything in Its Right Place"],
      consolidation_warning: "Keep Radiohead distinct from Thom Yorke solo and The Smile. Do not infer broad Radiohead appetite from Creep alone.",
    },
  ];

  const albumRows = [
    normalizedAlbum("071", "The Bends", 1995, "mass", "core", ["album_anchor", "bridge"], 0.91,
      "90s guitar-song Radiohead album bridge for modern-rock and alternative-radio branching.",
      "Added as missing-obvious; keep album-world reaction separate from later Radiohead abstraction."),
    normalizedAlbum("078", "OK Computer", 1997, "mass", "core", ["album_anchor", "anchor"], 0.98,
      "Core Radiohead album-world anchor for art-rock, alternative canon, and prestige-indie lineage.",
      "Primary album-world object; do not collapse into single-song Creep recognition."),
    normalizedAlbum("078", "Kid A", 2000, "high", "core", ["album_anchor", "boundary"], 0.96,
      "Boundary-shifting album-world object for electronic-rock, abstraction tolerance, and post-OK Computer branching.",
      "Do not infer generic guitar-rock appetite from Kid A response."),
    normalizedAlbum("078", "In Rainbows", 2007, "high", "standard", ["album_anchor", "bridge"], 0.92,
      "Later Radiohead album-world gateway with warmer songcraft and art-rock accessibility.",
      "Useful contrast against OK Computer architecture and Kid A abstraction."),
  ];
  document.albums = [
    ...document.albums.filter((row) => row.artist_name !== "Radiohead"),
    ...albumRows,
  ];

  const songRows = [
    normalizedSong("071", "Creep", 1992, "mass", "core", ["song_first", "gateway", "bridge"], 0.93,
      "Mass-recognition Radiohead song-first gateway and modern-rock branch point.",
      "artist_survey_worthy",
      "Same-title collision with TLC - Creep; distinct composition and recording. Do not merge by title. Do not infer broad Radiohead appetite from Creep alone."),
    normalizedSong("071", "Fake Plastic Trees", 1995, "mass", "core", ["song_first", "bridge"], 0.9,
      "High-recognition melodic bridge from The Bends into vulnerable alternative songcraft.",
      "artist_survey_worthy",
      "Useful positive signal for songcraft, but not sufficient evidence for Kid A-style abstraction."),
    normalizedSong("078", "Paranoid Android", 1997, "mass", "core", ["song_first", "boundary"], 0.95,
      "Canonical OK Computer suite and a strong test for art-rock structure tolerance.",
      "artist_survey_worthy",
      "Long-form/sectional response should not be collapsed into generic 90s alternative appetite."),
    normalizedSong("078", "Karma Police", 1997, "mass", "core", ["song_first", "gateway", "bridge"], 0.94,
      "Recognizable OK Computer song gateway with broad survey branching value.",
      "artist_survey_worthy",
      "Keep as song-level bridge even when OK Computer is also an album-world object."),
    normalizedSong("078", "No Surprises", 1997, "high", "standard", ["song_first", "bridge"], 0.88,
      "Melodic OK Computer entry point that tests quiet dread, beauty, and soft-focus recognition.",
      "artist_survey_worthy",
      "Do not over-infer appetite for the band's harsher or more abstract side."),
    normalizedSong("078", "Everything in Its Right Place", 2000, "high", "standard", ["boundary", "bridge"], 0.89,
      "Kid A entry point for electronic texture, repetition, and post-rock abstraction tolerance.",
      "artist_survey_worthy",
      "Positive signal should branch toward electronic/post-rock boundary checks rather than ordinary modern-rock radio by default."),
    normalizedSong("078", "Idioteque", 2000, "high", "standard", ["boundary"], 0.86,
      "Sharper Kid A boundary probe for electronic pulse, anxiety, and anti-guitar Radiohead.",
      "artist_survey_worthy",
      "Use as a boundary/probe row; do not treat as a standard recommendation unless the route asks that question."),
    normalizedSong("078", "Weird Fishes/Arpeggi", 2007, "high", "standard", ["deepening", "bridge"], 0.84,
      "In Rainbows song-level bridge for later Radiohead warmth, motion, and fan-recognized album depth.",
      "artist_survey_worthy",
      "More album-world than mass-radio; keep survey use adaptive rather than default Page 1 unless user signals fit."),
  ];
  document.songs = [
    ...document.songs.filter((row) => row.artist_name !== "Radiohead"),
    ...songRows,
  ];

  refreshFamily10Metadata(document);
  writeJson(file, document);
}

function normalizedAlbum(archetypeId, albumTitle, year, recognitionTier, surveyTier, roles, weight, reason, warning) {
  return {
    archetype_id: archetypeId,
    album_title: albumTitle,
    artist_name: "Radiohead",
    proposed_album_id: `radiohead-${slug(albumTitle)}`,
    existing_seed: false,
    release_year: year,
    album_object_type: "studio_album",
    recognition_tier: recognitionTier,
    survey_tier: surveyTier,
    roles,
    archetype_membership_weight: weight,
    inclusion_reason: reason,
    consolidation_warning: warning,
  };
}

function normalizedSong(archetypeId, songTitle, year, recognitionTier, surveyTier, roles, weight, reason, artistSurveyStatus, warning) {
  return {
    archetype_id: archetypeId,
    song_title: songTitle,
    artist_name: "Radiohead",
    proposed_song_id: `radiohead-${slug(songTitle)}`,
    existing_seed: false,
    release_year: year,
    recognition_tier: recognitionTier,
    survey_tier: surveyTier,
    roles,
    archetype_membership_weight: weight,
    inclusion_reason: reason,
    artist_survey_status: artistSurveyStatus,
    consolidation_warning: warning,
  };
}

function refreshFamily10Metadata(document) {
  const artists = document.artists ?? [];
  const albums = document.albums ?? [];
  const songs = document.songs ?? [];
  const allRows = [...artists, ...albums, ...songs];
  const existingSeed = allRows.filter((row) => row.existing_seed === true).length;
  document.metadata.row_counts = {
    artists: artists.length,
    albums: albums.length,
    songs: songs.length,
    total: allRows.length,
    existing_seed: existingSeed,
    added_missing_obvious: allRows.length - existingSeed,
  };

  document.metadata.archetype_counts = Object.entries(document.metadata.archetypes).map(([archetypeId, archetypeName]) => ({
    archetype_id: archetypeId,
    archetype_name: archetypeName,
    artists: artists.filter((row) => row.archetype_id === archetypeId).length,
    albums: albums.filter((row) => row.archetype_id === archetypeId).length,
    songs: songs.filter((row) => row.archetype_id === archetypeId).length,
  }));
}

function promotePatchedArtifacts(metadata) {
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
    ["graph_hardening_pass_d_freeze_manifest.json", "canonical_graph_freeze_manifest.json"],
    ["graph_hardening_pass_d_freeze_manifest.md", "canonical_graph_freeze_manifest.md"],
    ["radiohead_missing_obvious_hotfix_v1.json", "radiohead_missing_obvious_hotfix_v1.json"],
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
      tagging_corpus_rows: metadata.tagging_corpus_rows,
      apple_id_resolution_queue_rows: metadata.apple_id_resolution_queue_rows,
      album_sidecar_seed_rows: metadata.album_sidecar_seed_rows,
      graph_linking_node_rows: metadata.graph_linking_node_rows,
    };
    manifest.post_freeze_radiohead_hotfix = patchSummary;
    manifest.current_artifacts = {
      ...manifest.current_artifacts,
      radiohead_missing_obvious_hotfix: "data/canonical_graph/current/radiohead_missing_obvious_hotfix_v1.json",
    };
    writeJson(file, manifest);
  }

  updateCurrentMarkdown(path.join(canonicalRoot, "CURRENT_CANONICAL_GRAPH.md"), metadata);
  updateCurrentMarkdown(path.join(current, "README.md"), metadata);
}

function writeFreezeMarkdown(file, metadata) {
  let text = fs.readFileSync(file, "utf8");
  text = updateGateCounts(text, metadata);

  if (!text.includes("## Post-Freeze Radiohead Missing-Obvious Hotfix")) {
    text += `
## Post-Freeze Radiohead Missing-Obvious Hotfix

- Patch: \`${patchSummary.id}\`
- Applied on: ${patchSummary.applied_on}
- Intent: ${patchSummary.intent}
- Added rows: ${patchSummary.row_count}
- Active inventory rows after patch: ${metadata.active_inventory_rows}
- Song tagging corpus rows after patch: ${metadata.tagging_corpus_rows}
- Apple ID resolution queue rows after patch: ${metadata.apple_id_resolution_queue_rows}
- Album sidecar seed rows after patch: ${metadata.album_sidecar_seed_rows}
- Graph-linking node rows after patch: ${metadata.graph_linking_node_rows}
`;
  }
  fs.writeFileSync(file, text);
}

function updateCurrentMarkdown(file, metadata) {
  let text = fs.readFileSync(file, "utf8");
  text = updateGateCounts(text, metadata);

  if (!text.includes("## Post-Freeze Radiohead Missing-Obvious Hotfix")) {
    text += `
## Post-Freeze Radiohead Missing-Obvious Hotfix

- Patch: \`${patchSummary.id}\`
- Applied on: ${patchSummary.applied_on}
- Intent: ${patchSummary.intent}
- Added rows: ${patchSummary.row_count}
- Title/recording guardrail: Radiohead - Creep remains distinct from TLC - Creep and must not be title-merged.
`;
  }
  fs.writeFileSync(file, text);
}

function updateGateCounts(text, metadata) {
  return text
    .replace(/- Active inventory rows: \d+/, `- Active inventory rows: ${metadata.active_inventory_rows}`)
    .replace(/- Song tagging corpus rows: \d+/, `- Song tagging corpus rows: ${metadata.tagging_corpus_rows}`)
    .replace(/- Tagging corpus rows: \d+/, `- Tagging corpus rows: ${metadata.tagging_corpus_rows}`)
    .replace(/- Apple ID resolution queue rows: \d+/, `- Apple ID resolution queue rows: ${metadata.apple_id_resolution_queue_rows}`)
    .replace(/- Album sidecar seed rows: \d+/, `- Album sidecar seed rows: ${metadata.album_sidecar_seed_rows}`)
    .replace(/- Graph-linking node rows: \d+/, `- Graph-linking node rows: ${metadata.graph_linking_node_rows}`);
}

function nextMembershipNumber(rows) {
  const ids = rows
    .map((row) => String(row.v1_membership_id ?? "").match(/^v1m_(\d+)$/))
    .filter(Boolean)
    .map((match) => Number(match[1]));
  return Math.max(...ids) + 1;
}

function compareMembershipId(a, b) {
  return membershipNumber(a.v1_membership_id) - membershipNumber(b.v1_membership_id);
}

function membershipNumber(value) {
  const match = String(value ?? "").match(/^v1m_(\d+)$/);
  return match ? Number(match[1]) : Number.MAX_SAFE_INTEGER;
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

function slug(value) {
  return normKey(value).replace(/\s+/g, "-");
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function writeJson(file, value) {
  fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`);
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
