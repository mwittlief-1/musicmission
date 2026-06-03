#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

const repoRoot = process.cwd();
const currentRoot = path.join(repoRoot, "data/canonical_graph/current");
const resourcesRoot = path.join(repoRoot, "MusicAtlasController/Resources");
const outputManifestPath = path.join(currentRoot, "app_full_graph_survey_resources_v1_manifest.md");

const generatedAt = new Date().toISOString();

const graphRows = rowsFrom(readJson(path.join(currentRoot, "graph_linking_node_set.json")));
const inventoryRows = rowsFrom(readJson(path.join(currentRoot, "canonical_graph_active_inventory.json")));
const archetypeRows = rowsFrom(readJson(path.join(currentRoot, "atlas_archetype_profile_targets.json")));
const catalogEntries = rowsFrom(readJson(path.join(resourcesRoot, "canonical_apple_music_catalog_index_v1.json")), "entries");

const existingArtists = readExistingArray("canonical_artists.json");
const existingAlbums = readExistingArray("canonical_albums.json");
const existingSongs = readExistingArray("canonical_song_recordings.json");

const archetypeByID = new Map(archetypeRows.map((row) => [String(row.archetype_id), row]));
const familyNameByID = buildFamilyNameByID();
const inventoryByKey = groupBy(inventoryRows.filter((row) => row.active_in_v1 !== false), (row) => row.candidate_identity_key);
const catalogBySourceRef = buildCatalogBySourceRef(catalogEntries);
const existingByKindAndID = {
  artist: new Map(existingArtists.map((row) => [row.canonical_artist_id, row])),
  album: new Map(existingAlbums.map((row) => [row.canonical_album_id, row])),
  song_recording: new Map(existingSongs.map((row) => [row.canonical_song_recording_id, row])),
};

const outputs = {
  artist: [],
  album: [],
  song_recording: [],
};
const canonicalRecords = {
  artist: new Map(),
  album: new Map(),
  song_recording: new Map(),
};
const surveyRowsByObject = {
  artist: [],
  album: [],
  song_recording: [],
};
const skipped = {
  no_catalog_entry: 0,
  unresolved_risk: 0,
  unsupported_type: 0,
  missing_identity: 0,
};
let inferredCanonicalIDs = 0;
let matchKeyCanonicalIDs = 0;

for (const graphRow of graphRows) {
  const objectType = objectTypeForGraphType(graphRow.candidate_type);
  if (!objectType) {
    skipped.unsupported_type += 1;
    continue;
  }

  const sourceRef = graphRow.candidate_identity_key;
  if (!sourceRef) {
    skipped.missing_identity += 1;
    continue;
  }

  const catalogEntry = catalogBySourceRef.get(sourceRef);
  if (!catalogEntry) {
    skipped.no_catalog_entry += 1;
    continue;
  }

  const memberships = inventoryByKey.get(sourceRef) ?? [];
  if (!isResolvedForAppSurvey(graphRow, memberships)) {
    skipped.unresolved_risk += 1;
    continue;
  }

  const canonicalMatchKey = canonicalIDFromMatchKeys(catalogEntry.match_keys);
  const canonicalID = canonicalMatchKey ?? inferredCanonicalID(objectType, graphRow);
  if (!canonicalID) {
    skipped.missing_identity += 1;
    continue;
  }
  if (canonicalMatchKey) {
    matchKeyCanonicalIDs += 1;
  } else {
    inferredCanonicalIDs += 1;
  }

  const metadata = buildCanonicalMetadata({
    objectType,
    canonicalID,
    graphRow,
    memberships,
    existing: existingByKindAndID[objectType].get(canonicalID),
  });
  canonicalRecords[objectType].set(canonicalID, metadata);

  for (const archetypeID of graphRow.archetype_ids ?? []) {
    const archetype = archetypeByID.get(String(archetypeID));
    const familyID = numberOrNull(archetype?.family_number);
    if (!familyID) {
      continue;
    }
    const membership = memberships.find((row) => String(row.archetype_id) === String(archetypeID));
    surveyRowsByObject[objectType].push(buildSurveyRow({
      objectType,
      canonicalID,
      graphRow,
      membership,
      archetypeID: String(archetypeID),
      familyID,
    }));
  }
}

outputs.artist = sortCanonicalRows([...canonicalRecords.artist.values()], "canonical_artist_id");
outputs.album = sortCanonicalRows([...canonicalRecords.album.values()], "canonical_album_id");
outputs.song_recording = sortCanonicalRows([...canonicalRecords.song_recording.values()], "canonical_song_recording_id");

writeJson(path.join(resourcesRoot, "canonical_artists.json"), outputs.artist);
writeJson(path.join(resourcesRoot, "canonical_albums.json"), outputs.album);
writeJson(path.join(resourcesRoot, "canonical_song_recordings.json"), outputs.song_recording);

const artistSurface = buildSurveySurface("artist", surveyRowsByObject.artist);
const albumSurface = buildSurveySurface("album", surveyRowsByObject.album);
const songSurface = buildSurveySurface("song_recording", surveyRowsByObject.song_recording);

writeJson(path.join(resourcesRoot, "survey_artist_candidates_v0_2.json"), artistSurface);
writeJson(path.join(resourcesRoot, "survey_album_candidates_v0_2.json"), albumSurface);
writeJson(path.join(resourcesRoot, "survey_song_candidates_v0_2.json"), songSurface);

const summary = {
  generated_at: generatedAt,
  source_graph: "data/canonical_graph/current/graph_linking_node_set.json",
  source_inventory: "data/canonical_graph/current/canonical_graph_active_inventory.json",
  catalog_index: "MusicAtlasController/Resources/canonical_apple_music_catalog_index_v1.json",
  canonical_counts: {
    artists: outputs.artist.length,
    albums: outputs.album.length,
    song_recordings: outputs.song_recording.length,
  },
  survey_membership_counts: {
    artists: countSurfaceRows(artistSurface),
    albums: countSurfaceRows(albumSurface),
    song_recordings: countSurfaceRows(songSurface),
  },
  canonical_id_sources: {
    from_catalog_match_key: matchKeyCanonicalIDs,
    inferred_from_graph_identity: inferredCanonicalIDs,
  },
  skipped,
};

writeManifest(summary);
console.log(JSON.stringify(summary, null, 2));

function buildCatalogBySourceRef(entries) {
  const byRef = new Map();
  for (const entry of entries) {
    const refs = new Set([entry.source_ref]);
    for (const key of entry.match_keys ?? []) {
      if (String(key).startsWith("source_ref:")) {
        refs.add(String(key).slice("source_ref:".length));
      }
    }
    for (const ref of refs) {
      const prior = byRef.get(ref);
      if (!prior || priority(entry) > priority(prior)) {
        byRef.set(ref, entry);
      }
    }
  }
  return byRef;
}

function buildCanonicalMetadata({ objectType, canonicalID, graphRow, memberships, existing }) {
  const archetypeIDs = uniqueSorted([
    ...(graphRow.archetype_ids ?? []),
    ...memberships.map((row) => row.archetype_id),
    ...(existing?.archetype_ids ?? []),
  ].map(String));
  const familyNumbers = uniqueNumbers([
    ...archetypeIDs.map((id) => archetypeByID.get(id)?.family_number),
    ...(existing?.family_numbers ?? []),
  ]);
  const roles = uniqueSorted([
    ...(existing?.roles ?? []),
    ...memberships.flatMap((row) => [row.mission_role, row.import_class, row.candidate_type]),
    ...(graphRow.import_classes ?? []),
  ].filter(Boolean).map(String));
  const years = uniqueNumbers([
    graphRow.year,
    ...memberships.map((row) => row.year),
    ...(existing?.release_years ?? []),
  ]);
  const recognitionTier = existing?.best_recognition_tier ?? bestRecognitionTier(memberships);
  const surveyTier = existing?.best_survey_tier ?? surveyTierForRecognition(recognitionTier);
  const artistNames = artistNamesFor(graphRow, existing, objectType);
  const displayName = existing?.display_name ?? displayNameFor(graphRow, objectType);

  if (objectType === "artist") {
    return {
      canonical_artist_id: canonicalID,
      display_name: displayName,
      family_numbers: familyNumbers,
      archetype_ids: archetypeIDs,
      roles,
      existing_seed_any: Boolean(existing?.existing_seed_any),
      source_row_count: Math.max(1, memberships.length || graphRow.membership_count || 1),
      likely_canonical_albums: existing?.likely_canonical_albums ?? [],
      likely_canonical_songs: existing?.likely_canonical_songs ?? [],
      best_recognition_tier: recognitionTier,
      best_survey_tier: surveyTier,
    };
  }

  if (objectType === "album") {
    return {
      canonical_album_id: canonicalID,
      display_name: displayName,
      family_numbers: familyNumbers,
      archetype_ids: archetypeIDs,
      roles,
      existing_seed_any: Boolean(existing?.existing_seed_any),
      source_row_count: Math.max(1, memberships.length || graphRow.membership_count || 1),
      album_title: graphRow.title ?? existing?.album_title ?? displayName,
      artist_names: artistNames,
      release_years: years,
      album_object_types: existing?.album_object_types ?? uniqueSorted(memberships.map((row) => row.import_class).filter(Boolean)),
      best_recognition_tier: recognitionTier,
      best_survey_tier: surveyTier,
    };
  }

  return {
    canonical_song_recording_id: canonicalID,
    display_name: displayName,
    family_numbers: familyNumbers,
    archetype_ids: archetypeIDs,
    roles,
    existing_seed_any: Boolean(existing?.existing_seed_any),
    source_row_count: Math.max(1, memberships.length || graphRow.membership_count || 1),
    song_title: graphRow.title ?? existing?.song_title ?? displayName,
    artist_names: artistNames,
    release_years: years,
    composition_key: existing?.composition_key ?? slug(graphRow.title ?? displayName),
    best_recognition_tier: recognitionTier,
    best_survey_tier: surveyTier,
  };
}

function buildSurveyRow({ objectType, canonicalID, graphRow, membership, archetypeID, familyID }) {
  const recognitionTier = bestRecognitionTier(membership ? [membership] : []);
  const pageRole = pageRoleForRecognition(recognitionTier);
  const intent = surveyIntentFor(objectType, membership, graphRow);
  return {
    candidate_id: `survey-fullgraph-f${familyID}-${objectType}-${canonicalID}-${archetypeID}`,
    canonical_entity_id: canonicalID,
    display_label: displayNameFor(graphRow, objectType),
    object_type: objectType,
    family_id: familyID,
    archetype_ids: [archetypeID],
    survey_page_role: pageRole,
    survey_intent: intent,
    trigger_rule: "generated_from_current_canonical_graph_with_apple_catalog_resolution",
    do_not_infer: guardrailsFor(intent, objectType),
    positive_inference: [`possible affinity for ${displayNameFor(graphRow, objectType)} in this graph context`],
    negative_inference: [`possible rejection or low appetite for ${displayNameFor(graphRow, objectType)} in this narrow context`],
    dedupe_group: `${objectType}:${canonicalID}`,
    priority_score: priorityScoreFor(recognitionTier, intent),
    review_status: "approved",
    quarantine_reasons: [],
    source_membership_id: membership?.v1_membership_id ?? `${graphRow.candidate_identity_key}@@${archetypeID}`,
  };
}

function buildSurveySurface(objectType, rows) {
  const familyMap = new Map();
  for (const row of rows) {
    const family = familyMap.get(row.family_id) ?? {
      family_id: row.family_id,
      family_name: familyNameFor(row.family_id),
      object_type: objectType,
      suppressed_quarantined_counts: {},
      page1_core: [],
      page2_adaptive: [],
      page3_deep: [],
    };
    family[row.survey_page_role].push(row);
    familyMap.set(row.family_id, family);
  }

  const families = [...familyMap.values()].sort((left, right) => left.family_id - right.family_id);
  for (const family of families) {
    for (const bucket of ["page1_core", "page2_adaptive", "page3_deep"]) {
      family[bucket] = dedupeRows(family[bucket]).sort(sortSurveyRows);
    }
  }

  return {
    generated_date: generatedAt.slice(0, 10),
    object_type: objectType,
    page_model: "alpha_v0_2_full_current_canonical_graph_apple_resolved",
    families,
  };
}

function isResolvedForAppSurvey(graphRow, memberships) {
  const graphRisks = graphRow.risk_statuses ?? [];
  if (graphRisks.includes("unresolved")) {
    return false;
  }
  for (const membership of memberships) {
    if (membership.active_in_v1 === false) {
      return false;
    }
    if (String(membership.risk_status ?? "").toLowerCase() === "unresolved") {
      return false;
    }
  }
  return true;
}

function objectTypeForGraphType(type) {
  switch (type) {
    case "artist_anchor":
      return "artist";
    case "album":
      return "album";
    case "song":
    case "recording":
      return "song_recording";
    default:
      return null;
  }
}

function canonicalIDFromMatchKeys(matchKeys = []) {
  const key = matchKeys.find((value) => String(value).startsWith("canonical_entity_id:"));
  return key ? String(key).slice("canonical_entity_id:".length) : null;
}

function inferredCanonicalID(objectType, graphRow) {
  const artist = slug(graphRow.artist_display_name);
  const title = slug(graphRow.title);
  if (objectType === "artist") {
    return slug(graphRow.artist_display_name || graphRow.title);
  }
  if (!artist && !title) {
    return null;
  }
  return artist ? `${artist}-${title}` : title;
}

function displayNameFor(graphRow, objectType) {
  if (objectType === "artist") {
    return graphRow.artist_display_name || graphRow.title || "Unknown Artist";
  }
  return graphRow.title || graphRow.artist_display_name || "Unknown";
}

function artistNamesFor(graphRow, existing, objectType) {
  if (objectType === "artist") {
    return [displayNameFor(graphRow, objectType)];
  }
  const names = existing?.artist_names ?? [graphRow.artist_display_name].filter(Boolean);
  return uniqueSorted(names.map(String));
}

function bestRecognitionTier(memberships) {
  const tiers = memberships.map((row) => row.recognition_band).filter(Boolean);
  if (tiers.includes("obvious")) return "high";
  if (tiers.includes("medium")) return "medium";
  if (tiers.includes("deep")) return "cult";
  return "medium";
}

function surveyTierForRecognition(recognitionTier) {
  switch (recognitionTier) {
    case "mass":
    case "high":
      return "core";
    case "medium":
      return "standard";
    default:
      return "edge";
  }
}

function pageRoleForRecognition(recognitionTier) {
  switch (recognitionTier) {
    case "mass":
    case "high":
      return "page1_core";
    case "medium":
      return "page2_adaptive";
    default:
      return "page3_deep";
  }
}

function surveyIntentFor(objectType, membership, graphRow) {
  const values = [
    membership?.mission_role,
    membership?.import_class,
    ...(graphRow.import_classes ?? []),
  ].filter(Boolean).map((value) => String(value));
  if (values.some((value) => value.includes("false"))) return "false_nearby_test";
  if (values.some((value) => value.includes("boundary") || value.includes("contrast"))) return "boundary_test";
  if (objectType === "album" || values.some((value) => value.includes("album"))) return "album_world_test";
  if (objectType === "song_recording") return "song_first_memory";
  if (values.some((value) => value.includes("bridge"))) return "bridge_test";
  return "artist_affinity_probe";
}

function guardrailsFor(intent, objectType) {
  const output = [
    "do not infer broad genre appetite from one tap",
    "do not infer canonical graph mutation from survey response",
  ];
  if (intent === "song_first_memory") {
    output.push("do not over-promote the artist from one song-first response");
  }
  if (intent === "album_world_test") {
    output.push("do not infer favorite-artist status without artist/song evidence");
  }
  if (intent === "boundary_test" || intent === "false_nearby_test") {
    output.push("do not create a dead-end conclusion without repeated user signal");
  }
  if (objectType !== "artist") {
    output.push("keep object-level response distinct from artist-level response");
  }
  return output;
}

function priorityScoreFor(recognitionTier, intent) {
  const base = {
    mass: 100,
    high: 94,
    medium: 76,
    cult: 58,
    low: 42,
  }[recognitionTier] ?? 70;
  const bonus = intent === "bridge_test" ? 2 : intent === "boundary_test" || intent === "false_nearby_test" ? -4 : 0;
  return Math.max(1, Math.min(100, base + bonus));
}

function familyNameFor(familyID) {
  return familyNameByID.get(Number(familyID)) ?? `Family ${familyID}`;
}

function buildFamilyNameByID() {
  const output = new Map();
  for (const row of inventoryRows) {
    const archetype = archetypeByID.get(String(row.archetype_id));
    const familyID = numberOrNull(archetype?.family_number);
    if (familyID && row.primary_family && !output.has(familyID)) {
      output.set(familyID, row.primary_family);
    }
  }
  for (const row of archetypeRows) {
    const familyID = numberOrNull(row.family_number);
    const name = row.family_name ?? row.primary_family;
    if (familyID && name && !output.has(familyID)) {
      output.set(familyID, name);
    }
  }
  return output;
}

function dedupeRows(rows) {
  const seen = new Set();
  const output = [];
  for (const row of rows) {
    const key = `${row.canonical_entity_id}@@${row.archetype_ids.join(",")}`;
    if (seen.has(key)) continue;
    seen.add(key);
    output.push(row);
  }
  return output;
}

function sortSurveyRows(left, right) {
  if (right.priority_score !== left.priority_score) return right.priority_score - left.priority_score;
  if (left.display_label !== right.display_label) return left.display_label.localeCompare(right.display_label);
  return left.candidate_id.localeCompare(right.candidate_id);
}

function sortCanonicalRows(rows, key) {
  return rows.sort((left, right) => {
    if (left.display_name !== right.display_name) return String(left.display_name).localeCompare(String(right.display_name));
    return String(left[key]).localeCompare(String(right[key]));
  });
}

function countSurfaceRows(surface) {
  return surface.families.reduce((sum, family) => (
    sum + family.page1_core.length + family.page2_adaptive.length + family.page3_deep.length
  ), 0);
}

function slug(value) {
  return String(value ?? "")
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/&/g, " and ")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function uniqueSorted(values) {
  return [...new Set(values.filter((value) => value !== undefined && value !== null && String(value).trim() !== ""))]
    .map(String)
    .sort((left, right) => left.localeCompare(right));
}

function uniqueNumbers(values) {
  return [...new Set(values.map(numberOrNull).filter(Boolean))]
    .sort((left, right) => left - right);
}

function numberOrNull(value) {
  const numeric = Number(value);
  return Number.isFinite(numeric) && numeric > 0 ? numeric : null;
}

function priority(entry) {
  return Number(entry?.priority ?? 0);
}

function groupBy(values, keyFn) {
  const output = new Map();
  for (const value of values) {
    const key = keyFn(value);
    if (!key) continue;
    const group = output.get(key) ?? [];
    group.push(value);
    output.set(key, group);
  }
  return output;
}

function rowsFrom(payload, key = "rows") {
  if (Array.isArray(payload)) return payload;
  return payload?.[key] ?? [];
}

function readExistingArray(file) {
  const target = path.join(resourcesRoot, file);
  if (!fs.existsSync(target)) return [];
  return readJson(target);
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function writeJson(file, value) {
  fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`);
}

function writeManifest(summary) {
  const text = `# App Full Graph Survey Resources v1

Generated: ${summary.generated_at}

Status: complete

## Source

- Source graph: \`${summary.source_graph}\`
- Source inventory: \`${summary.source_inventory}\`
- Apple catalog gate: \`${summary.catalog_index}\`

## Canonical App Resource Counts

| Resource | Count |
| --- | ---: |
| canonical_artists.json | ${summary.canonical_counts.artists} |
| canonical_albums.json | ${summary.canonical_counts.albums} |
| canonical_song_recordings.json | ${summary.canonical_counts.song_recordings} |

## Survey Membership Counts

| Surface | Count |
| --- | ---: |
| survey_artist_candidates_v0_2.json | ${summary.survey_membership_counts.artists} |
| survey_album_candidates_v0_2.json | ${summary.survey_membership_counts.albums} |
| survey_song_candidates_v0_2.json | ${summary.survey_membership_counts.song_recordings} |

## Canonical ID Sources

| Source | Count |
| --- | ---: |
| Catalog match key | ${summary.canonical_id_sources.from_catalog_match_key} |
| Inferred from graph identity | ${summary.canonical_id_sources.inferred_from_graph_identity} |

## Skipped Graph Objects

| Reason | Count |
| --- | ---: |
| No Apple catalog entry | ${summary.skipped.no_catalog_entry} |
| Unresolved risk | ${summary.skipped.unresolved_risk} |
| Unsupported type | ${summary.skipped.unsupported_type} |
| Missing identity | ${summary.skipped.missing_identity} |

## Policy

Survey display resources are no longer capped by the legacy reduced survey candidate projection.
Any active current canonical graph artist, album, song, or recording may enter the app Survey resources when it has usable Apple catalog coverage and is not unresolved or blocklisted at runtime.
`;
  fs.writeFileSync(outputManifestPath, text);
}
