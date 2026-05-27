#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const passDRel = "data/canonical_graph/depth_hardening_v0_2/pass_d";
const seedRel = `${passDRel}/album_sidecar_seed_albums_v1.json`;
const sidecarRel = `${passDRel}/album_track_sidecar_v1.json`;
const tracksCsvRel = `${passDRel}/album_track_sidecar_tracks_v1.csv`;

const seedPath = path.join(repoRoot, seedRel);
const sidecarPath = path.join(repoRoot, sidecarRel);
const tracksCsvPath = path.join(repoRoot, tracksCsvRel);

const errors = [];
const warnings = [];

const seed = readJson(seedPath, seedRel);
const sidecar = readJson(sidecarPath, sidecarRel);

const seedRows = arrayOrEmpty(seed?.rows, "seed_rows_not_array", `${seedRel} rows must be an array`);
const sidecarAlbums = arrayOrEmpty(
  sidecar?.albums,
  "sidecar_albums_not_array",
  `${sidecarRel} albums must be an array`,
);
const seedMetadata = objectOrEmpty(seed?.metadata, "seed_metadata_not_object", `${seedRel} metadata must be an object`);
const sidecarMetadata = objectOrEmpty(
  sidecar?.metadata,
  "sidecar_metadata_not_object",
  `${sidecarRel} metadata must be an object`,
);

const seedRowsMissingIdentity = collector();
const seedRowsMissingMembershipId = collector();
const seedByIdentityKey = new Map();

for (const [index, row] of seedRows.entries()) {
  if (!isObject(row)) {
    seedRowsMissingIdentity.add({ index, reason: "row is not an object" });
    continue;
  }

  const key = cleanString(row.candidate_identity_key);
  if (!key) {
    seedRowsMissingIdentity.add({ index, v1_membership_id: row.v1_membership_id ?? null });
    continue;
  }

  if (!cleanString(row.v1_membership_id)) {
    seedRowsMissingMembershipId.add({ index, candidate_identity_key: key });
  }

  const entries = seedByIdentityKey.get(key) ?? [];
  entries.push({ index, row });
  seedByIdentityKey.set(key, entries);
}

const sidecarAlbumsMissingIdentity = collector();
const sidecarAlbumsNotObjects = collector();
const sidecarByIdentityKey = new Map();

for (const [index, album] of sidecarAlbums.entries()) {
  if (!isObject(album)) {
    sidecarAlbumsNotObjects.add({ index });
    continue;
  }

  const key = cleanString(album.candidate_identity_key);
  if (!key) {
    sidecarAlbumsMissingIdentity.add({ index, artist_display_name: album.artist_display_name ?? null, title: album.title ?? null });
    continue;
  }

  const entries = sidecarByIdentityKey.get(key) ?? [];
  entries.push({ index, album });
  sidecarByIdentityKey.set(key, entries);
}

if (seedRowsMissingIdentity.count > 0) {
  addCollectedIssue(
    errors,
    "seed_rows_missing_candidate_identity_key",
    "Seed rows must have candidate_identity_key before sidecar identity coverage can be validated.",
    seedRowsMissingIdentity,
  );
}

if (seedRowsMissingMembershipId.count > 0) {
  addCollectedIssue(
    errors,
    "seed_rows_missing_v1_membership_id",
    "Seed rows must have v1_membership_id so sidecar source_membership_ids can be validated.",
    seedRowsMissingMembershipId,
  );
}

if (sidecarAlbumsNotObjects.count > 0) {
  addCollectedIssue(errors, "sidecar_album_rows_not_objects", "Sidecar album rows must be objects.", sidecarAlbumsNotObjects);
}

if (sidecarAlbumsMissingIdentity.count > 0) {
  addCollectedIssue(
    errors,
    "sidecar_albums_missing_candidate_identity_key",
    "Every sidecar album must have candidate_identity_key.",
    sidecarAlbumsMissingIdentity,
  );
}

const seedIdentityKeys = [...seedByIdentityKey.keys()].sort();
const sidecarIdentityKeys = [...sidecarByIdentityKey.keys()].sort();
const missingSidecarKeys = seedIdentityKeys.filter((key) => !sidecarByIdentityKey.has(key));
const extraSidecarKeys = sidecarIdentityKeys.filter((key) => !seedByIdentityKey.has(key));
const duplicateSidecarKeys = sidecarIdentityKeys
  .map((key) => ({ key, occurrences: sidecarByIdentityKey.get(key)?.length ?? 0 }))
  .filter((entry) => entry.occurrences !== 1);

if (missingSidecarKeys.length > 0) {
  addIssue(errors, "missing_seed_candidate_identity_keys", "Every unique seed candidate_identity_key must appear in the sidecar exactly once.", {
    count: missingSidecarKeys.length,
    samples: missingSidecarKeys.slice(0, 20),
  });
}

if (extraSidecarKeys.length > 0) {
  addIssue(errors, "extra_sidecar_candidate_identity_keys", "Sidecar albums must come from the seed candidate_identity_key set.", {
    count: extraSidecarKeys.length,
    samples: extraSidecarKeys.slice(0, 20),
  });
}

if (duplicateSidecarKeys.length > 0) {
  addIssue(errors, "duplicate_sidecar_candidate_identity_keys", "Each sidecar candidate_identity_key must appear exactly once.", {
    count: duplicateSidecarKeys.length,
    samples: duplicateSidecarKeys.slice(0, 20),
  });
}

const albumMembershipCountMismatches = collector();
const albumMembershipIdMismatches = collector();
const albumArchetypeWarnings = collector();
const albumImportClassWarnings = collector();

for (const [key, entries] of sidecarByIdentityKey.entries()) {
  const seedEntries = seedByIdentityKey.get(key);
  if (!seedEntries || entries.length !== 1) continue;

  const album = entries[0].album;
  const expectedMembershipCount = seedEntries.length;
  if (album.membership_count !== expectedMembershipCount) {
    albumMembershipCountMismatches.add({
      candidate_identity_key: key,
      expected: expectedMembershipCount,
      actual: album.membership_count ?? null,
    });
  }

  const expectedMembershipIds = sortedUnique(seedEntries.map(({ row }) => row.v1_membership_id).filter(hasValue).map(String));
  const actualMembershipIds = Array.isArray(album.source_membership_ids)
    ? sortedUnique(album.source_membership_ids.filter(hasValue).map(String))
    : [];
  const membershipDiff = diffSets(expectedMembershipIds, actualMembershipIds);
  if (membershipDiff.missing.length > 0 || membershipDiff.extra.length > 0) {
    albumMembershipIdMismatches.add({
      candidate_identity_key: key,
      missing_source_membership_ids: membershipDiff.missing.slice(0, 10),
      extra_source_membership_ids: membershipDiff.extra.slice(0, 10),
    });
  }

  const expectedArchetypeIds = sortedUnique(seedEntries.map(({ row }) => row.archetype_id).filter(hasValue).map(String));
  const actualArchetypeIds = Array.isArray(album.archetype_ids) ? sortedUnique(album.archetype_ids.filter(hasValue).map(String)) : [];
  const archetypeDiff = diffSets(expectedArchetypeIds, actualArchetypeIds);
  if (archetypeDiff.missing.length > 0 || archetypeDiff.extra.length > 0) {
    albumArchetypeWarnings.add({
      candidate_identity_key: key,
      missing_archetype_ids: archetypeDiff.missing.slice(0, 10),
      extra_archetype_ids: archetypeDiff.extra.slice(0, 10),
    });
  }

  const expectedImportClasses = sortedUnique(seedEntries.map(({ row }) => row.import_class).filter(hasValue).map(String));
  const actualImportClasses = Array.isArray(album.import_classes) ? sortedUnique(album.import_classes.filter(hasValue).map(String)) : [];
  const importClassDiff = diffSets(expectedImportClasses, actualImportClasses);
  if (importClassDiff.missing.length > 0 || importClassDiff.extra.length > 0) {
    albumImportClassWarnings.add({
      candidate_identity_key: key,
      missing_import_classes: importClassDiff.missing.slice(0, 10),
      extra_import_classes: importClassDiff.extra.slice(0, 10),
    });
  }
}

addCollectedIssue(
  errors,
  "album_membership_count_mismatches",
  "Sidecar album membership_count must match the number of seed rows for the candidate_identity_key.",
  albumMembershipCountMismatches,
);
addCollectedIssue(
  errors,
  "album_source_membership_id_mismatches",
  "Sidecar source_membership_ids must match seed v1_membership_id values for the candidate_identity_key.",
  albumMembershipIdMismatches,
);
addCollectedIssue(
  warnings,
  "album_archetype_id_mismatches",
  "Sidecar archetype_ids differ from the seed rows for the candidate_identity_key.",
  albumArchetypeWarnings,
);
addCollectedIssue(
  warnings,
  "album_import_class_mismatches",
  "Sidecar import_classes differ from the seed rows for the candidate_identity_key.",
  albumImportClassWarnings,
);

let resolvedAlbumCount = 0;
let unresolvedAlbumCount = 0;
let appleResolvedAlbumCount = 0;
let musicBrainzResolvedAlbumCount = 0;
let totalTrackCount = 0;

const albumsMissingResolution = collector();
const albumsWithUnknownResolution = collector();
const resolvedAlbumsWithoutTracks = collector();
const unresolvedAlbumsWithTracks = collector();
const albumsTracksNotArray = collector();
const catalogTrackCountWarnings = collector();
const tracksNotObjects = collector();
const tracksMissingTitle = collector();
const tracksMissingStableId = collector();
const tracksMissingSource = collector();
const tracksMissingOrderFields = collector();
const tracksInvalidOrderFields = collector();
const tracksDuplicateOrder = collector();
const albumsOutOfTrackOrder = collector();

for (const [albumIndex, album] of sidecarAlbums.entries()) {
  if (!isObject(album)) continue;

  const albumKey = cleanString(album.candidate_identity_key) || `album_index_${albumIndex}`;
  const resolutionStatus = cleanString(album.resolution?.status);
  const selectedSource = cleanString(album.resolution?.selected_source);
  const catalogSource = cleanString(album.catalog_match?.source);
  const albumSource = selectedSource || catalogSource;

  if (!resolutionStatus) {
    albumsMissingResolution.add({ candidate_identity_key: albumKey });
  } else if (!["resolved", "unresolved"].includes(resolutionStatus)) {
    albumsWithUnknownResolution.add({ candidate_identity_key: albumKey, resolution_status: resolutionStatus });
  }

  const isResolved = resolutionStatus === "resolved";
  if (isResolved) {
    resolvedAlbumCount += 1;
    if (selectedSource === "apple_itunes_search_api") appleResolvedAlbumCount += 1;
    if (selectedSource === "musicbrainz_ws2") musicBrainzResolvedAlbumCount += 1;
  } else {
    unresolvedAlbumCount += 1;
  }

  if (!Array.isArray(album.tracks)) {
    albumsTracksNotArray.add({ candidate_identity_key: albumKey });
    if (isResolved) {
      resolvedAlbumsWithoutTracks.add({ candidate_identity_key: albumKey, track_count: 0 });
    }
    continue;
  }

  const tracks = album.tracks;
  totalTrackCount += tracks.length;

  if (isResolved && tracks.length === 0) {
    resolvedAlbumsWithoutTracks.add({ candidate_identity_key: albumKey, track_count: 0 });
  }
  if (!isResolved && tracks.length > 0) {
    unresolvedAlbumsWithTracks.add({ candidate_identity_key: albumKey, resolution_status: resolutionStatus || null, track_count: tracks.length });
  }

  const catalogTrackCount = album.catalog_match?.track_count;
  if (isResolved && Number.isInteger(catalogTrackCount) && catalogTrackCount >= 0 && catalogTrackCount !== tracks.length) {
    catalogTrackCountWarnings.add({
      candidate_identity_key: albumKey,
      catalog_track_count: catalogTrackCount,
      sidecar_track_count: tracks.length,
    });
  }

  let previousOrder = null;
  let albumOutOfOrderRecorded = false;
  const seenOrders = new Map();

  for (const [trackIndex, track] of tracks.entries()) {
    const trackLabel = { candidate_identity_key: albumKey, track_index: trackIndex + 1 };
    if (!isObject(track)) {
      tracksNotObjects.add(trackLabel);
      continue;
    }

    if (!cleanString(track.title)) {
      tracksMissingTitle.add({
        ...trackLabel,
        source: track.source ?? null,
        disc_number: track.disc_number ?? null,
        track_number: track.track_number ?? null,
      });
    }

    const trackSource = cleanString(track.source);
    const effectiveSource = trackSource || albumSource;
    if (!trackSource) {
      tracksMissingSource.add(trackLabel);
    }

    if (!hasStableTrackId(track, effectiveSource)) {
      tracksMissingStableId.add({
        ...trackLabel,
        source: effectiveSource || null,
        title: track.title ?? null,
      });
    }

    const discNumber = parseOrderField(track.disc_number);
    const trackNumber = parseOrderField(track.track_number);

    if (discNumber.status === "missing" || trackNumber.status === "missing") {
      tracksMissingOrderFields.add({
        ...trackLabel,
        disc_number: track.disc_number ?? null,
        track_number: track.track_number ?? null,
      });
      continue;
    }

    if (discNumber.status === "invalid" || trackNumber.status === "invalid") {
      tracksInvalidOrderFields.add({
        ...trackLabel,
        disc_number: track.disc_number ?? null,
        track_number: track.track_number ?? null,
      });
      continue;
    }

    const order = { disc_number: discNumber.value, track_number: trackNumber.value };
    const orderKey = `${order.disc_number}:${order.track_number}`;
    const firstIndexForOrder = seenOrders.get(orderKey);
    if (firstIndexForOrder !== undefined) {
      tracksDuplicateOrder.add({
        candidate_identity_key: albumKey,
        first_track_index: firstIndexForOrder,
        duplicate_track_index: trackIndex + 1,
        disc_number: order.disc_number,
        track_number: order.track_number,
      });
    } else {
      seenOrders.set(orderKey, trackIndex + 1);
    }

    if (previousOrder && compareTrackOrder(order, previousOrder) < 0 && !albumOutOfOrderRecorded) {
      albumsOutOfTrackOrder.add({
        candidate_identity_key: albumKey,
        previous_track_index: trackIndex,
        current_track_index: trackIndex + 1,
        previous_order: previousOrder,
        current_order: order,
      });
      albumOutOfOrderRecorded = true;
    }
    previousOrder = order;
  }
}

addCollectedIssue(errors, "albums_missing_resolution_status", "Every sidecar album must have resolution.status.", albumsMissingResolution);
addCollectedIssue(
  warnings,
  "albums_with_unknown_resolution_status",
  "Album resolution.status should be resolved or unresolved.",
  albumsWithUnknownResolution,
);
addCollectedIssue(
  errors,
  "album_tracks_not_array",
  "Every sidecar album must have a tracks array.",
  albumsTracksNotArray,
);
addCollectedIssue(
  errors,
  "resolved_albums_without_tracks",
  "Every resolved album must have at least one track.",
  resolvedAlbumsWithoutTracks,
);
addCollectedIssue(
  warnings,
  "unresolved_albums_with_tracks",
  "Unresolved albums are expected to have no tracks.",
  unresolvedAlbumsWithTracks,
);
addCollectedIssue(
  warnings,
  "catalog_track_count_mismatches",
  "Resolved album catalog_match.track_count differs from the number of sidecar tracks.",
  catalogTrackCountWarnings,
);
addCollectedIssue(errors, "tracks_not_objects", "Every sidecar track must be an object.", tracksNotObjects);
addCollectedIssue(errors, "tracks_missing_title", "Every sidecar track must have a non-empty title.", tracksMissingTitle);
addCollectedIssue(
  errors,
  "tracks_missing_stable_source_id",
  "Tracks must have a stable source id for the selected source when one is available.",
  tracksMissingStableId,
);
addCollectedIssue(warnings, "tracks_missing_source_field", "Tracks should carry their source field explicitly.", tracksMissingSource);
addCollectedIssue(
  errors,
  "tracks_missing_order_fields",
  "Every sidecar track must have disc_number and track_number order fields.",
  tracksMissingOrderFields,
);
addCollectedIssue(
  errors,
  "tracks_invalid_order_fields",
  "Track disc_number and track_number must be positive integers.",
  tracksInvalidOrderFields,
);
addCollectedIssue(
  errors,
  "tracks_duplicate_order_fields",
  "Track disc_number and track_number pairs must be unique within an album.",
  tracksDuplicateOrder,
);
addCollectedIssue(
  errors,
  "albums_out_of_track_order",
  "Tracks must be ordered by disc_number, then track_number within each album.",
  albumsOutOfTrackOrder,
);

validateCount(seedMetadata, "album_sidecar_seed_rows", seedRows.length, "seed_metadata_count_mismatch");
validateCount(sidecarMetadata, "source_album_membership_rows", seedRows.length, "sidecar_metadata_count_mismatch");
validateCount(sidecarMetadata, "source_unique_album_identity_rows", seedByIdentityKey.size, "sidecar_metadata_count_mismatch");
validateCount(sidecarMetadata, "album_identity_rows_in_sidecar", sidecarAlbums.length, "sidecar_metadata_count_mismatch");
validateCount(sidecarMetadata, "resolved_album_identity_rows", resolvedAlbumCount, "sidecar_metadata_count_mismatch");
validateCount(sidecarMetadata, "unresolved_album_identity_rows", unresolvedAlbumCount, "sidecar_metadata_count_mismatch");
validateCount(sidecarMetadata, "apple_resolved_album_identity_rows", appleResolvedAlbumCount, "sidecar_metadata_count_mismatch");
validateCount(sidecarMetadata, "musicbrainz_resolved_album_identity_rows", musicBrainzResolvedAlbumCount, "sidecar_metadata_count_mismatch");
validateCount(sidecarMetadata, "total_sidecar_tracks", totalTrackCount, "sidecar_metadata_count_mismatch");

if (sidecarMetadata.album_identity_rows_in_sidecar !== seedByIdentityKey.size) {
  addIssue(
    errors,
    "sidecar_metadata_seed_coverage_mismatch",
    "Sidecar metadata album_identity_rows_in_sidecar must match the unique seed candidate_identity_key count.",
    {
      field: "album_identity_rows_in_sidecar",
      expected: seedByIdentityKey.size,
      actual: sidecarMetadata.album_identity_rows_in_sidecar ?? null,
    },
  );
}

const expectedAverageTracksPerResolvedAlbum =
  resolvedAlbumCount === 0 ? 0 : Number((totalTrackCount / resolvedAlbumCount).toFixed(2));
if (
  typeof sidecarMetadata.average_tracks_per_resolved_album === "number" &&
  Math.abs(sidecarMetadata.average_tracks_per_resolved_album - expectedAverageTracksPerResolvedAlbum) > 0.001
) {
  addIssue(warnings, "sidecar_average_tracks_mismatch", "average_tracks_per_resolved_album differs from computed tracks/resolved albums.", {
    field: "average_tracks_per_resolved_album",
    expected: expectedAverageTracksPerResolvedAlbum,
    actual: sidecarMetadata.average_tracks_per_resolved_album,
  });
}

if (sidecarMetadata.version !== undefined && sidecarMetadata.version !== "album_track_sidecar_v1") {
  addIssue(errors, "sidecar_version_mismatch", "Sidecar metadata.version must be album_track_sidecar_v1.", {
    expected: "album_track_sidecar_v1",
    actual: sidecarMetadata.version,
  });
}

if (sidecarMetadata.source_seed_file !== undefined && sidecarMetadata.source_seed_file !== seedRel) {
  addIssue(warnings, "sidecar_source_seed_file_mismatch", "Sidecar metadata.source_seed_file should point at the seed JSON path.", {
    expected: seedRel,
    actual: sidecarMetadata.source_seed_file,
  });
}

let csvTrackRows = null;
let csvExists = false;
if (fs.existsSync(tracksCsvPath)) {
  csvExists = true;
  const csvResult = countCsvDataRows(tracksCsvPath);
  csvTrackRows = csvResult.dataRows;
  if (csvResult.error) {
    addIssue(errors, "csv_track_rows_unreadable", "Track CSV could not be counted reliably.", {
      path: tracksCsvRel,
      error: csvResult.error,
    });
  } else if (csvResult.dataRows !== totalTrackCount) {
    addIssue(errors, "csv_track_row_count_mismatch", "CSV track data row count must match the JSON sidecar total track count.", {
      path: tracksCsvRel,
      csv_track_rows: csvResult.dataRows,
      json_total_tracks: totalTrackCount,
    });
  }
}

const summary = {
  validator: "validate_album_track_sidecar_v1",
  ok: errors.length === 0,
  files: {
    seed: seedRel,
    sidecar: sidecarRel,
    tracks_csv: csvExists ? tracksCsvRel : null,
  },
  counts: {
    seed_membership_rows: seedRows.length,
    seed_unique_candidate_identity_keys: seedByIdentityKey.size,
    sidecar_album_rows: sidecarAlbums.length,
    sidecar_unique_candidate_identity_keys: sidecarByIdentityKey.size,
    resolved_album_rows: resolvedAlbumCount,
    unresolved_album_rows: unresolvedAlbumCount,
    apple_resolved_album_rows: appleResolvedAlbumCount,
    musicbrainz_resolved_album_rows: musicBrainzResolvedAlbumCount,
    json_total_tracks: totalTrackCount,
    csv_track_rows: csvTrackRows,
  },
  error_count: sumIssueCounts(errors),
  warning_count: sumIssueCounts(warnings),
  errors,
  warnings,
};

console.log(JSON.stringify(summary, null, 2));
process.exitCode = errors.length > 0 ? 1 : 0;

function readJson(filePath, displayPath) {
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf8"));
  } catch (error) {
    addIssue(errors, "json_read_failed", "Required JSON file could not be read or parsed.", {
      path: displayPath,
      error: error.message,
    });
    return null;
  }
}

function validateCount(metadata, field, expected, code) {
  if (metadata[field] !== expected) {
    addIssue(errors, code, `Metadata field ${field} must match the computed count.`, {
      field,
      expected,
      actual: metadata[field] ?? null,
    });
  }
}

function arrayOrEmpty(value, code, message) {
  if (Array.isArray(value)) return value;
  addIssue(errors, code, message);
  return [];
}

function objectOrEmpty(value, code, message) {
  if (isObject(value)) return value;
  addIssue(errors, code, message);
  return {};
}

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function cleanString(value) {
  return typeof value === "string" ? value.trim() : "";
}

function hasValue(value) {
  return value !== null && value !== undefined && String(value).trim() !== "";
}

function sortedUnique(values) {
  return [...new Set(values)].sort();
}

function diffSets(expected, actual) {
  const expectedSet = new Set(expected);
  const actualSet = new Set(actual);
  return {
    missing: expected.filter((value) => !actualSet.has(value)),
    extra: actual.filter((value) => !expectedSet.has(value)),
  };
}

function hasStableTrackId(track, source) {
  if (source === "apple_itunes_search_api") {
    return hasValue(track.apple_track_id);
  }

  if (source === "musicbrainz_ws2") {
    return hasValue(track.musicbrainz_recording_id) || hasValue(track.musicbrainz_track_id);
  }

  return (
    hasValue(track.apple_track_id) ||
    hasValue(track.musicbrainz_recording_id) ||
    hasValue(track.musicbrainz_track_id)
  );
}

function parseOrderField(value) {
  if (value === null || value === undefined || value === "") {
    return { status: "missing", value: null };
  }

  if (typeof value === "number") {
    return Number.isInteger(value) && value > 0 ? { status: "ok", value } : { status: "invalid", value: null };
  }

  if (typeof value === "string" && /^[1-9]\d*$/.test(value.trim())) {
    return { status: "ok", value: Number(value.trim()) };
  }

  return { status: "invalid", value: null };
}

function compareTrackOrder(left, right) {
  if (left.disc_number !== right.disc_number) return left.disc_number - right.disc_number;
  return left.track_number - right.track_number;
}

function countCsvDataRows(filePath) {
  try {
    const text = fs.readFileSync(filePath, "utf8");
    const recordCount = countCsvRecords(text);
    return { dataRows: Math.max(0, recordCount - 1), error: null };
  } catch (error) {
    return { dataRows: null, error: error.message };
  }
}

function countCsvRecords(text) {
  let inQuotes = false;
  let recordCount = 0;
  let hasRecordContent = false;

  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];

    if (inQuotes) {
      if (char === '"' && text[index + 1] === '"') {
        index += 1;
      } else if (char === '"') {
        inQuotes = false;
      }
      hasRecordContent = true;
      continue;
    }

    if (char === '"') {
      inQuotes = true;
      hasRecordContent = true;
      continue;
    }

    if (char === "\r" || char === "\n") {
      if (char === "\r" && text[index + 1] === "\n") index += 1;
      if (hasRecordContent) {
        recordCount += 1;
        hasRecordContent = false;
      }
      continue;
    }

    hasRecordContent = true;
  }

  if (inQuotes) {
    throw new Error("unterminated quoted CSV field");
  }

  if (hasRecordContent) recordCount += 1;
  return recordCount;
}

function collector(limit = 20) {
  return {
    count: 0,
    samples: [],
    add(sample) {
      this.count += 1;
      if (this.samples.length < limit) this.samples.push(sample);
    },
  };
}

function addCollectedIssue(target, code, message, collection) {
  if (collection.count === 0) return;
  addIssue(target, code, message, {
    count: collection.count,
    samples: collection.samples,
  });
}

function addIssue(target, code, message, details = {}) {
  target.push({
    code,
    message,
    ...details,
  });
}

function sumIssueCounts(issues) {
  return issues.reduce((sum, issue) => sum + (Number.isInteger(issue.count) ? issue.count : 1), 0);
}
