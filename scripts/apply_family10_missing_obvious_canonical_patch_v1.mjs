#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

const repoRoot = process.cwd();
const canonicalRoot = path.join(repoRoot, "data/canonical_graph");
const passD = path.join(canonicalRoot, "depth_hardening_v0_2/pass_d");
const current = path.join(canonicalRoot, "current");
const resourcesRoot = path.join(repoRoot, "MusicAtlasController/Resources");
const normalizationPass2 = path.join(canonicalRoot, "normalization_pass_2");

const appliedOn = "2026-06-01";
const family10 = "Alternative, Indie, Grunge, Emo";
const archetypes = {
  "071": "Post-Grunge / Modern Rock Radio",
  "075": "Power-Pop Revival / Crunchy Alt-Pop",
  "078": "Blog Indie / Prestige Indie / 2000s Indie Rock",
};

const oasisHotfixId = "oasis_missing_obvious_hotfix_v1";
const oasisSourceLayer = "post_freeze_oasis_missing_obvious_hotfix";
const oasisSourceFile = "data/canonical_graph/current/oasis_missing_obvious_hotfix_v1.json";
const oasisPatchIntent =
  "Post-freeze missing-obvious correction for Oasis and (What's the Story) Morning Glory? coverage in Family 10.";

const appleLinkRunVersion = "apple_music_family10_missing_obvious_hotfix_v1";
const appleLinkDir = path.join(current, appleLinkRunVersion);
const appleLinkPath = path.join(appleLinkDir, "apple_music_family10_missing_obvious_hotfix_links_v1.jsonl");
const verifiedAt = "2026-06-01T00:00:00.000Z";

const oasisRows = [
  artist("075", "Oasis", "Oasis", null, "obvious", "bridge", "artist_anchor",
    "Missing-obvious Britpop/UK alternative anchor for melodic 90s guitar-pop, singalong recognition, and alt-pop boundary tests.",
    "Use as a Britpop bridge inside Family 10; do not collapse positive response into generic wedding/nostalgia singalong appetite."),
  album("075", "Oasis", "(What's the Story) Morning Glory?", 1995, "obvious", "album_world", "core_graph_album",
    "Core Oasis album-world object and a high-recognition Britpop gateway.",
    "Canonical studio album row; prefer original album object when linking even when Apple top songs surface remastered editions."),
  song("075", "Oasis", "Wonderwall", 1995, "obvious", "bridge", "core_graph_playable", "none",
    "Top Oasis song-recognition gateway and Britpop/alt-pop branch point.",
    "High singalong familiarity can be noisy; do not infer broad Oasis or Britpop affinity from this song alone."),
  song("075", "Oasis", "Champagne Supernova", 1995, "obvious", "bridge", "core_graph_playable", "none",
    "Apple top-songs rank #2 Oasis track and a useful album-world bridge from Wonderwall-level recognition into longer-form Oasis.",
    "Use as a stronger Oasis-depth check than a generic 90s nostalgia control."),
];

const radioheadResourcePatch = {
  artists: [
    {
      canonical_artist_id: "radiohead",
      display_name: "Radiohead",
      family_numbers: [10],
      archetype_ids: ["078"],
      roles: ["anchor", "artist_anchor", "bridge"],
      existing_seed_any: false,
      source_row_count: 1,
      likely_canonical_albums: ["OK Computer", "Kid A", "In Rainbows", "The Bends"],
      likely_canonical_songs: [
        "Creep",
        "Fake Plastic Trees",
        "Paranoid Android",
        "Karma Police",
        "Everything in Its Right Place",
      ],
      best_recognition_tier: "mass",
      best_survey_tier: "core",
    },
  ],
  albums: [
    albumMetadata("radiohead-the-bends", "The Bends", "Radiohead", [10], ["071"], ["album_anchor", "bridge"], 1995, "mass", "core"),
    albumMetadata("radiohead-ok-computer", "OK Computer", "Radiohead", [10], ["078"], ["album_anchor", "anchor"], 1997, "mass", "core"),
    albumMetadata("radiohead-kid-a", "Kid A", "Radiohead", [10], ["078"], ["album_anchor", "boundary"], 2000, "high", "core"),
    albumMetadata("radiohead-in-rainbows", "In Rainbows", "Radiohead", [10], ["078"], ["album_anchor", "bridge"], 2007, "high", "standard"),
  ],
  songs: [
    songMetadata("radiohead-creep", "Creep", "Radiohead", [10], ["071"], ["song_first", "gateway", "bridge"], 1992, "mass", "core"),
    songMetadata("radiohead-fake-plastic-trees", "Fake Plastic Trees", "Radiohead", [10], ["071"], ["song_first", "bridge"], 1995, "mass", "core"),
    songMetadata("radiohead-paranoid-android", "Paranoid Android", "Radiohead", [10], ["078"], ["song_first", "boundary"], 1997, "mass", "core"),
    songMetadata("radiohead-karma-police", "Karma Police", "Radiohead", [10], ["078"], ["song_first", "gateway", "bridge"], 1997, "mass", "core"),
    songMetadata("radiohead-no-surprises", "No Surprises", "Radiohead", [10], ["078"], ["song_first", "bridge"], 1997, "high", "standard"),
    songMetadata("radiohead-everything-in-its-right-place", "Everything in Its Right Place", "Radiohead", [10], ["078"], ["boundary", "bridge"], 2000, "high", "standard"),
    songMetadata("radiohead-idioteque", "Idioteque", "Radiohead", [10], ["078"], ["boundary"], 2000, "high", "standard"),
    songMetadata("radiohead-weird-fishes-arpeggi", "Weird Fishes/Arpeggi", "Radiohead", [10], ["078"], ["deepening", "bridge"], 2007, "high", "standard"),
  ],
};

const oasisResourcePatch = {
  artists: [
    {
      canonical_artist_id: "oasis",
      display_name: "Oasis",
      family_numbers: [10],
      archetype_ids: ["075"],
      roles: ["anchor", "artist_anchor", "bridge"],
      existing_seed_any: false,
      source_row_count: 1,
      likely_canonical_albums: ["(What's the Story) Morning Glory?"],
      likely_canonical_songs: ["Wonderwall", "Champagne Supernova"],
      best_recognition_tier: "mass",
      best_survey_tier: "core",
    },
  ],
  albums: [
    albumMetadata("oasis-whats-the-story-morning-glory", "(What's the Story) Morning Glory?", "Oasis", [10], ["075"], ["album_anchor", "anchor", "bridge"], 1995, "mass", "core"),
  ],
  songs: [
    songMetadata("oasis-wonderwall", "Wonderwall", "Oasis", [10], ["075"], ["song_first", "gateway", "bridge"], 1995, "mass", "core"),
    songMetadata("oasis-champagne-supernova", "Champagne Supernova", "Oasis", [10], ["075"], ["song_first", "bridge", "deepening"], 1995, "mass", "core"),
  ],
};

const surveyRows = [
  surveyRow("artist", "radiohead", "Radiohead", ["078"], "page2_adaptive", "bridge_test", 100, "family-10-artist-078-radiohead",
    ["Keep Radiohead distinct from Thom Yorke solo and The Smile.", "Do not infer broad Radiohead appetite from Creep alone."]),
  surveyRow("artist", "oasis", "Oasis", ["075"], "page2_adaptive", "bridge_test", 98, "family-10-artist-075-oasis",
    ["Britpop bridge inside Family 10.", "Do not collapse into generic wedding/nostalgia singalong appetite."]),

  surveyRow("album", "radiohead-the-bends", "The Bends", ["071"], "page2_adaptive", "album_world_test", 96, "family-10-album-071-radiohead-the-bends"),
  surveyRow("album", "radiohead-ok-computer", "OK Computer", ["078"], "page2_adaptive", "album_world_test", 100, "family-10-album-078-radiohead-ok-computer"),
  surveyRow("album", "radiohead-kid-a", "Kid A", ["078"], "page2_adaptive", "boundary_test", 96, "family-10-album-078-radiohead-kid-a",
    ["Do not infer generic guitar-rock appetite from Kid A response."]),
  surveyRow("album", "radiohead-in-rainbows", "In Rainbows", ["078"], "page3_deep", "album_world_test", 92, "family-10-album-078-radiohead-in-rainbows"),
  surveyRow("album", "oasis-whats-the-story-morning-glory", "(What's the Story) Morning Glory?", ["075"], "page2_adaptive", "album_world_test", 98, "family-10-album-075-oasis-whats-the-story-morning-glory"),

  surveyRow("song_recording", "radiohead-creep", "Creep", ["071"], "page2_adaptive", "song_first_memory", 100, "family-10-song-071-radiohead-creep",
    ["Same-title collision with TLC - Creep; distinct composition and recording.", "Do not infer broad Radiohead appetite from Creep alone."]),
  surveyRow("song_recording", "radiohead-fake-plastic-trees", "Fake Plastic Trees", ["071"], "page2_adaptive", "song_first_memory", 98, "family-10-song-071-radiohead-fake-plastic-trees"),
  surveyRow("song_recording", "radiohead-paranoid-android", "Paranoid Android", ["078"], "page2_adaptive", "boundary_test", 98, "family-10-song-078-radiohead-paranoid-android",
    ["Long-form/sectional response should not be collapsed into generic 90s alternative appetite."]),
  surveyRow("song_recording", "radiohead-karma-police", "Karma Police", ["078"], "page2_adaptive", "song_first_memory", 98, "family-10-song-078-radiohead-karma-police"),
  surveyRow("song_recording", "radiohead-no-surprises", "No Surprises", ["078"], "page2_adaptive", "song_first_memory", 94, "family-10-song-078-radiohead-no-surprises"),
  surveyRow("song_recording", "radiohead-everything-in-its-right-place", "Everything in Its Right Place", ["078"], "page3_deep", "boundary_test", 92, "family-10-song-078-radiohead-everything-in-its-right-place"),
  surveyRow("song_recording", "radiohead-idioteque", "Idioteque", ["078"], "page3_deep", "boundary_test", 90, "family-10-song-078-radiohead-idioteque"),
  surveyRow("song_recording", "radiohead-weird-fishes-arpeggi", "Weird Fishes/Arpeggi", ["078"], "page3_deep", "song_first_memory", 90, "family-10-song-078-radiohead-weird-fishes-arpeggi"),
  surveyRow("song_recording", "oasis-wonderwall", "Wonderwall", ["075"], "page2_adaptive", "song_first_memory", 100, "family-10-song-075-oasis-wonderwall",
    ["High singalong familiarity can be noisy; do not infer broad Oasis or Britpop affinity from this song alone."]),
  surveyRow("song_recording", "oasis-champagne-supernova", "Champagne Supernova", ["075"], "page2_adaptive", "song_first_memory", 98, "family-10-song-075-oasis-champagne-supernova"),
];

const appleLinks = [
  artistLink("Radiohead", "artist_anchor|radiohead|radiohead", "657515", 1, "apple_artist_search_top_exact_normalized"),
  artistLink("Oasis", "artist_anchor|oasis|oasis", "512633", 1, "apple_artist_search_top_exact_normalized"),
  albumLink("Radiohead", "The Bends", "album|radiohead|bends", "1097862703", 1),
  albumLink("Radiohead", "OK Computer", "album|radiohead|ok computer", "1097861387", 1),
  albumLink("Radiohead", "Kid A", "album|radiohead|kid a", "1097862870", 1),
  albumLink("Radiohead", "In Rainbows", "album|radiohead|in rainbows", "1109714933", 1),
  albumLink("Oasis", "(What's the Story) Morning Glory?", "album|oasis|what s the story morning glory", "1517447039", 3, "apple_album_search_title_artist_original_album_preferred"),
  songLink("Radiohead", "Creep", "song|radiohead|creep", "1097862231", "1097862062", 1),
  songLink("Radiohead", "Fake Plastic Trees", "song|radiohead|fake plastic trees", "1097862845", "1097862703", 1),
  songLink("Radiohead", "Paranoid Android", "song|radiohead|paranoid android", "1097861770", "1097861387", 1),
  songLink("Radiohead", "Karma Police", "song|radiohead|karma police", "1097861836", "1097861387", 1),
  songLink("Radiohead", "No Surprises", "song|radiohead|no surprises", "1097861842", "1097861387", 1),
  songLink("Radiohead", "Everything in Its Right Place", "song|radiohead|everything in its right place", "1097863108", "1097862870", 1),
  songLink("Radiohead", "Idioteque", "song|radiohead|idioteque", "1097863262", "1097862870", 1),
  songLink("Radiohead", "Weird Fishes/Arpeggi", "song|radiohead|weird fishes arpeggi", "1109715168", "1109714933", 1),
  songLink("Oasis", "Wonderwall", "song|oasis|wonderwall", "1517447333", "1517447039", 1, "apple_song_search_original_album_track_preferred"),
  songLink("Oasis", "Champagne Supernova", "song|oasis|champagne supernova", "1517447869", "1517447039", 1, "apple_song_search_original_album_track_preferred"),
];

const graphSummary = patchGraphArtifacts();
patchFamily10Normalized();
writeAcceptedAppleLinks();
patchAppResources();

console.log(JSON.stringify({
  ok: true,
  graph_patch: graphSummary,
  apple_links: appleLinks.length,
  app_resource_rows_added: {
    artists: radioheadResourcePatch.artists.length + oasisResourcePatch.artists.length,
    albums: radioheadResourcePatch.albums.length + oasisResourcePatch.albums.length,
    songs: radioheadResourcePatch.songs.length + oasisResourcePatch.songs.length,
    survey_rows: surveyRows.length,
  },
}, null, 2));

function patchGraphArtifacts() {
  const activeInventoryPath = path.join(passD, "graph_hardening_v1_active_inventory.json");
  const activeInventory = readJson(activeInventoryPath);
  const passDManifestPath = path.join(passD, "graph_hardening_pass_d_freeze_manifest.json");
  const passDManifest = readJson(passDManifestPath);
  const profileTargetsPath = path.join(passD, "atlas_archetype_profile_targets_v1.json");
  const oasisKeys = new Set(oasisRows.map((row) => identityKey(row)));
  const previousRows = activeInventory.rows.filter((row) => oasisKeys.has(row.candidate_identity_key));
  const previousIdsByKey = new Map(previousRows.map((row) => [row.candidate_identity_key, row.v1_membership_id]));
  const previousDelta = buildProfileTargetDelta(previousRows);
  const baseRows = activeInventory.rows.filter((row) => !oasisKeys.has(row.candidate_identity_key));
  const nextIdStart = nextMembershipNumber(baseRows);
  const addedRows = oasisRows.map((definition, index) => {
    const key = identityKey(definition);
    const id = previousIdsByKey.get(key) ?? `v1m_${String(nextIdStart + index).padStart(5, "0")}`;
    return normalizeOasisRow(definition, id, index);
  });

  const activeRows = [...baseRows, ...addedRows].sort(compareMembershipId);
  const taggingCorpus = buildTaggingCorpus(activeRows);
  const appleIdResolutionQueue = buildAppleIdResolutionQueue(taggingCorpus);
  const albumSeeds = buildAlbumSidecarSeeds(activeRows);
  const graphLinkingRows = buildGraphLinkingNodeSet(activeRows);
  const profileDelta = buildProfileTargetDelta(addedRows);
  const profileTargets = patchProfileTargets(
    readJson(profileTargetsPath).rows,
    previousDelta,
    profileDelta,
  );
  const patchSummary = {
    id: oasisHotfixId,
    applied_on: appliedOn,
    status: "applied",
    intent: oasisPatchIntent,
    row_count: addedRows.length,
    artist_anchor_rows: addedRows.filter((row) => row.candidate_type === "artist_anchor").length,
    album_rows: addedRows.filter((row) => row.candidate_type === "album").length,
    song_rows: addedRows.filter((row) => row.candidate_type === "song").length,
    profile_target_delta: profileDelta,
    actions: [
      "add_missing_obvious_artist_anchor",
      "add_album_world_row",
      "add_top_song_gateway_rows",
      "preserve_britpop_vs_generic_nostalgia_guardrail",
    ],
  };

  const nextMetadata = patchMetadata(passDManifest.metadata, {
    active_inventory_rows: activeRows.length,
    tagging_corpus_rows: taggingCorpus.length,
    apple_id_resolution_queue_rows: appleIdResolutionQueue.length,
    album_sidecar_seed_rows: albumSeeds.length,
    graph_linking_node_rows: graphLinkingRows.length,
  }, patchSummary);

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
    artifacts: [...new Set([...(passDManifest.artifacts ?? []), "oasis_missing_obvious_hotfix_v1.json"])],
  });
  writeJson(path.join(passD, "oasis_missing_obvious_hotfix_v1.json"), {
    metadata: patchSummary,
    rows: addedRows,
  });
  writeFreezeMarkdown(path.join(passD, "graph_hardening_pass_d_freeze_manifest.md"), patchSummary, nextMetadata);
  promotePatchedArtifacts(nextMetadata, patchSummary);

  return {
    id: oasisHotfixId,
    added_rows: addedRows.length,
    active_inventory_rows: activeRows.length,
    tagging_corpus_rows: taggingCorpus.length,
    apple_id_resolution_queue_rows: appleIdResolutionQueue.length,
    album_sidecar_seed_rows: albumSeeds.length,
    graph_linking_node_rows: graphLinkingRows.length,
  };
}

function patchFamily10Normalized() {
  const file = path.join(canonicalRoot, "family_10/normalized_family_10.json");
  const document = readJson(file);

  document.artists = [
    ...document.artists.filter((row) => row.proposed_artist_id !== "oasis"),
    {
      archetype_id: "075",
      artist_name: "Oasis",
      proposed_artist_id: "oasis",
      existing_seed: false,
      recognition_tier: "mass",
      survey_tier: "core",
      roles: ["anchor", "artist_anchor", "bridge"],
      archetype_membership_weight: 0.9,
      inclusion_reason: "Missing-obvious Britpop/UK alternative anchor connecting melodic 90s guitar-pop, mass song recognition, and alt-pop boundary tests.",
      object_specificity_note: "artist_level",
      likely_canonical_albums: ["(What's the Story) Morning Glory?"],
      likely_canonical_songs: ["Wonderwall", "Champagne Supernova"],
      consolidation_warning: "Use as a Britpop bridge inside Family 10; do not collapse into generic wedding/nostalgia singalong appetite.",
    },
  ];

  document.albums = [
    ...document.albums.filter((row) => row.proposed_album_id !== "oasis-whats-the-story-morning-glory"),
    {
      archetype_id: "075",
      album_title: "(What's the Story) Morning Glory?",
      artist_name: "Oasis",
      proposed_album_id: "oasis-whats-the-story-morning-glory",
      existing_seed: false,
      release_year: 1995,
      album_object_type: "studio_album",
      recognition_tier: "mass",
      survey_tier: "core",
      roles: ["album_anchor", "anchor", "bridge"],
      archetype_membership_weight: 0.9,
      inclusion_reason: "Core Oasis album-world object and high-recognition Britpop gateway.",
      consolidation_warning: "Prefer original album object when linking; keep remastered/deluxe Apple variants explicit if used.",
    },
  ];

  document.songs = [
    ...document.songs.filter((row) => !["oasis-wonderwall", "oasis-champagne-supernova"].includes(row.proposed_song_id)),
    {
      archetype_id: "075",
      song_title: "Wonderwall",
      artist_name: "Oasis",
      proposed_song_id: "oasis-wonderwall",
      existing_seed: false,
      release_year: 1995,
      recognition_tier: "mass",
      survey_tier: "core",
      roles: ["song_first", "gateway", "bridge"],
      archetype_membership_weight: 0.9,
      inclusion_reason: "Top Oasis song-recognition gateway and Britpop/alt-pop branch point.",
      artist_survey_status: "artist_survey_worthy",
      consolidation_warning: "High singalong familiarity can be noisy; do not infer broad Oasis or Britpop affinity from this song alone.",
    },
    {
      archetype_id: "075",
      song_title: "Champagne Supernova",
      artist_name: "Oasis",
      proposed_song_id: "oasis-champagne-supernova",
      existing_seed: false,
      release_year: 1995,
      recognition_tier: "mass",
      survey_tier: "core",
      roles: ["song_first", "bridge", "deepening"],
      archetype_membership_weight: 0.88,
      inclusion_reason: "Apple top-songs rank #2 Oasis track and useful album-depth bridge beyond Wonderwall.",
      artist_survey_status: "artist_survey_worthy",
      consolidation_warning: "Use as a stronger Oasis-depth check than a generic 90s nostalgia control.",
    },
  ];

  refreshFamily10Metadata(document);
  writeJson(file, document);
}

function writeAcceptedAppleLinks() {
  fs.mkdirSync(appleLinkDir, { recursive: true });
  fs.writeFileSync(appleLinkPath, `${appleLinks.map((link) => JSON.stringify(link)).join("\n")}\n`);
  writeJson(path.join(appleLinkDir, "apple_music_family10_missing_obvious_hotfix_summary.json"), {
    run_version: appleLinkRunVersion,
    generated_at: verifiedAt,
    raw_payload_persisted: false,
    persisted_catalog_fields: ["apple_catalog_id", "apple_resource_type", "storefront", "source refs", "match metadata"],
    excluded_persistent_fields: ["artwork", "previews", "lyrics", "raw_catalog_payload", "music_user_token"],
    links_total: appleLinks.length,
    graph_artist_links: appleLinks.filter((link) => link.source_type === "graph_artist_anchor").length,
    graph_album_links: appleLinks.filter((link) => link.source_type === "graph_album").length,
    graph_song_links: appleLinks.filter((link) => link.source_type === "graph_song").length,
    notes: [
      "Radiohead artist link resolves Replay raw artist ref 657515.",
      "Oasis top-two tracks follow Apple artist top-songs ordering: Wonderwall, Champagne Supernova.",
      "Oasis graph links prefer original album track IDs when available to avoid remastered/deluxe ambiguity.",
    ],
  });
}

function patchAppResources() {
  patchCanonicalMetadataResource(
    path.join(resourcesRoot, "canonical_artists.json"),
    "canonical_artist_id",
    [...radioheadResourcePatch.artists, ...oasisResourcePatch.artists],
  );
  patchCanonicalMetadataResource(
    path.join(resourcesRoot, "canonical_albums.json"),
    "canonical_album_id",
    [...radioheadResourcePatch.albums, ...oasisResourcePatch.albums],
  );
  patchCanonicalMetadataResource(
    path.join(resourcesRoot, "canonical_song_recordings.json"),
    "canonical_song_recording_id",
    [...radioheadResourcePatch.songs, ...oasisResourcePatch.songs],
  );

  for (const root of [resourcesRoot, normalizationPass2]) {
    patchSurveySurface(path.join(root, "survey_artist_candidates_v0_2.json"), "artist");
    patchSurveySurface(path.join(root, "survey_album_candidates_v0_2.json"), "album");
    patchSurveySurface(path.join(root, "survey_song_candidates_v0_2.json"), "song_recording");
  }
}

function patchCanonicalMetadataResource(file, idField, additions) {
  const rows = readJson(file);
  const ids = new Set(additions.map((row) => row[idField]));
  const nextRows = [
    ...rows.filter((row) => !ids.has(row[idField])),
    ...additions,
  ].sort((a, b) => String(a[idField]).localeCompare(String(b[idField])));
  writeJson(file, nextRows);
}

function patchSurveySurface(file, objectType) {
  const payload = readJson(file);
  const family = payload.families.find((row) => row.family_id === 10);
  if (!family) throw new Error(`Family 10 missing in ${file}`);
  const rows = surveyRows.filter((row) => row.object_type === objectType);
  const ids = new Set(rows.map((row) => row.canonical_entity_id));
  for (const bucket of ["page1_core", "page2_adaptive", "page3_deep"]) {
    family[bucket] = family[bucket].filter((row) => !ids.has(row.canonical_entity_id));
  }
  for (const row of rows) {
    family[row.survey_page_role].push(row);
  }
  for (const bucket of ["page1_core", "page2_adaptive", "page3_deep"]) {
    family[bucket].sort((a, b) => {
      if (Number(b.priority_score) !== Number(a.priority_score)) {
        return Number(b.priority_score) - Number(a.priority_score);
      }
      return a.display_label.localeCompare(b.display_label);
    });
  }
  writeJson(file, payload);
}

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

function normalizeOasisRow(definition, membershipId, index) {
  const candidateIdentityKey = identityKey(definition);
  return {
    v1_membership_id: membershipId,
    source_layer: oasisSourceLayer,
    source_file: oasisSourceFile,
    source_index: `oasis-hotfix-${String(index + 1).padStart(3, "0")}`,
    ...definition,
    candidate_identity_key: candidateIdentityKey,
    archetype_membership_key: `${candidateIdentityKey}@@${definition.archetype_id}`,
    active_in_v1: true,
    active_effective_credit: definition.candidate_type === "artist_anchor" ? 0 : 1,
    pm_multi_membership_status: "not_applicable",
    pass_c_zero_credit_before_pm_decision: false,
  };
}

function albumMetadata(canonicalID, displayName, artistName, familyNumbers, archetypeIDs, roles, year, recognitionTier, surveyTier) {
  return {
    canonical_album_id: canonicalID,
    display_name: displayName,
    family_numbers: familyNumbers,
    archetype_ids: archetypeIDs,
    roles,
    existing_seed_any: false,
    source_row_count: 1,
    album_title: displayName,
    artist_names: [artistName],
    release_years: [year],
    album_object_types: ["studio_album"],
    best_recognition_tier: recognitionTier,
    best_survey_tier: surveyTier,
  };
}

function songMetadata(canonicalID, displayName, artistName, familyNumbers, archetypeIDs, roles, year, recognitionTier, surveyTier) {
  return {
    canonical_song_recording_id: canonicalID,
    display_name: displayName,
    family_numbers: familyNumbers,
    archetype_ids: archetypeIDs,
    roles,
    existing_seed_any: false,
    source_row_count: 1,
    song_title: displayName,
    artist_names: [artistName],
    release_years: [year],
    composition_key: slug(displayName),
    best_recognition_tier: recognitionTier,
    best_survey_tier: surveyTier,
  };
}

function surveyRow(objectType, canonicalID, displayLabel, archetypeIDs, pageRole, intent, priorityScore, sourceMembershipID, extraDoNotInfer = []) {
  const kindSegment = objectType === "song_recording" ? "song_recording" : objectType;
  const familyName = family10;
  const positiveType = objectType === "album"
    ? "possible album-world appetite beyond single recognition"
    : objectType === "song_recording"
      ? "possible song-first memory or cultural-furniture recognition"
      : `possible affinity for ${canonicalID} in this family/archetype context`;
  const negativeType = `possible rejection or low appetite for ${canonicalID} in this narrow context`;
  return {
    candidate_id: `survey-f10-${kindSegment}-${canonicalID}-${archetypeIDs[0]}`,
    canonical_entity_id: canonicalID,
    display_label: displayLabel,
    object_type: objectType,
    family_id: 10,
    archetype_ids: archetypeIDs,
    survey_page_role: pageRole,
    survey_intent: intent,
    trigger_rule: "post_freeze_missing_obvious_hotfix",
    do_not_infer: [
      "do not infer broad genre appetite from one tap",
      "do not infer canonical graph mutation from survey response",
      ...extraDoNotInfer,
      "do not infer adjacent archetypes without follow-up evidence",
    ],
    positive_inference: [
      `possible affinity for ${canonicalID} in this family/archetype context`,
      positiveType,
      `possible openness to the ${archetypes[archetypeIDs[0]]} lane`,
    ],
    negative_inference: [negativeType],
    dedupe_group: `${objectType}:${canonicalID}`,
    priority_score: priorityScore,
    review_status: "approved",
    quarantine_reasons: [],
    source_membership_id: sourceMembershipID,
  };
}

function artistLink(artistName, sourceRef, appleCatalogId, resultRank, matchBasis) {
  return compactAppleLink({
    sourceType: "graph_artist_anchor",
    sourceCandidateType: "artist_anchor",
    sourceRef,
    appleCatalogId,
    appleResourceType: "artist",
    matchBasis,
    resultRank,
    titleMatch: "not_applicable",
    artistMatch: "exact_normalized",
    warnings: "",
    extra: {
      apple_artist_name: artistName,
    },
  });
}

function albumLink(artistName, albumTitle, sourceRef, appleCatalogId, resultRank, matchBasis = "apple_album_search_title_artist_year_auto_match") {
  return compactAppleLink({
    sourceType: "graph_album",
    sourceCandidateType: "album",
    sourceRef,
    appleCatalogId,
    appleResourceType: "album",
    matchBasis,
    resultRank,
    titleMatch: "exact_normalized",
    artistMatch: "exact_normalized",
    warnings: resultRank === 1 ? "" : "original_album_preferred_over_deluxe_or_remastered_variant",
    extra: {
      apple_artist_name: artistName,
      apple_album_name: albumTitle,
    },
  });
}

function songLink(artistName, songTitle, sourceRef, appleCatalogId, albumAppleCatalogId, resultRank, matchBasis = "apple_song_search_title_artist_album_context_auto_match") {
  return compactAppleLink({
    sourceType: "graph_song",
    sourceCandidateType: "song",
    sourceRef,
    appleCatalogId,
    appleResourceType: "song",
    matchBasis,
    resultRank,
    titleMatch: "exact_normalized",
    artistMatch: "exact_normalized",
    warnings: "",
    extra: {
      apple_artist_name: artistName,
      apple_track_name: songTitle,
      album_apple_catalog_id: albumAppleCatalogId,
      apple_album_id: albumAppleCatalogId,
    },
  });
}

function compactAppleLink({
  sourceType,
  sourceCandidateType,
  sourceRef,
  appleCatalogId,
  appleResourceType,
  matchBasis,
  resultRank,
  titleMatch,
  artistMatch,
  warnings,
  extra = {},
}) {
  return {
    link_key: `${sourceType}:${sourceRef}:apple_music:${appleResourceType}:${appleCatalogId}:us`,
    run_version: appleLinkRunVersion,
    source_ref: sourceRef,
    source_type: sourceType,
    source_candidate_type: sourceCandidateType,
    external_catalog: "apple_music",
    apple_catalog_id: String(appleCatalogId),
    apple_resource_type: appleResourceType,
    storefront: "us",
    match_status: "verified",
    match_basis: matchBasis,
    confidence: "high",
    result_rank: resultRank,
    title_match: titleMatch,
    artist_match: artistMatch,
    year_delta: 0,
    warnings,
    verified_at: verifiedAt,
    raw_payload_persisted: false,
    ...extra,
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

function patchMetadata(metadata, counts, patchSummary) {
  return {
    ...metadata,
    ...counts,
    post_freeze_oasis_hotfix: patchSummary,
  };
}

function promotePatchedArtifacts(metadata, patchSummary) {
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
    ["oasis_missing_obvious_hotfix_v1.json", "oasis_missing_obvious_hotfix_v1.json"],
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
    manifest.post_freeze_oasis_hotfix = patchSummary;
    manifest.current_artifacts = {
      ...manifest.current_artifacts,
      oasis_missing_obvious_hotfix: "data/canonical_graph/current/oasis_missing_obvious_hotfix_v1.json",
      apple_music_family10_missing_obvious_hotfix_links: "data/canonical_graph/current/apple_music_family10_missing_obvious_hotfix_v1/apple_music_family10_missing_obvious_hotfix_links_v1.jsonl",
    };
    writeJson(file, manifest);
  }

  updateCurrentMarkdown(path.join(canonicalRoot, "CURRENT_CANONICAL_GRAPH.md"), patchSummary, metadata);
  updateCurrentMarkdown(path.join(current, "README.md"), patchSummary, metadata);
}

function writeFreezeMarkdown(file, patchSummary, metadata) {
  let text = fs.readFileSync(file, "utf8");
  text = updateGateCounts(text, metadata);

  if (!text.includes("## Post-Freeze Oasis Missing-Obvious Hotfix")) {
    text += `
## Post-Freeze Oasis Missing-Obvious Hotfix

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

function updateCurrentMarkdown(file, patchSummary, metadata) {
  let text = fs.readFileSync(file, "utf8");
  text = updateGateCounts(text, metadata);

  if (!text.includes("## Post-Freeze Oasis Missing-Obvious Hotfix")) {
    text += `
## Post-Freeze Oasis Missing-Obvious Hotfix

- Patch: \`${patchSummary.id}\`
- Applied on: ${patchSummary.applied_on}
- Intent: ${patchSummary.intent}
- Added rows: ${patchSummary.row_count}
- Apple links: \`data/canonical_graph/current/apple_music_family10_missing_obvious_hotfix_v1/apple_music_family10_missing_obvious_hotfix_links_v1.jsonl\`
- Guardrail: Oasis rows are Britpop/alt-pop bridge material, not generic wedding/nostalgia controls.
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
