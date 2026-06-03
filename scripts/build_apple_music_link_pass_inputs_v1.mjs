#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

const repoRoot = process.cwd();
const currentDir = path.join(repoRoot, "data/canonical_graph/current");
const graphPath = path.join(currentDir, "graph_linking_node_set.json");
const albumResolutionPath = path.join(currentDir, "album_track_sidecar_album_resolution.csv");
const trackPath = path.join(currentDir, "album_track_sidecar_tracks.csv");
const outputDir = path.join(currentDir, "apple_music_link_pass_v1");
const outputPath = path.join(outputDir, "input_inventory.json");

const graph = readJson(graphPath);
const graphRows = Array.isArray(graph.rows) ? graph.rows : [];
const graphDedupe = dedupeRows(graphRows, stableRowKey);
const albumResolutionDedupe = dedupeRows(readCsv(albumResolutionPath), stableRowKey);
const trackDedupe = dedupeRows(readCsv(trackPath), stableRowKey);

const graphAlbumRows = graphDedupe.rows.filter((row) => row.candidate_type === "album");
const graphAlbumsByKey = groupBy(graphAlbumRows, (row) => row.candidate_identity_key);
const albumResolutionByKey = groupBy(albumResolutionDedupe.rows, (row) => row.candidate_identity_key);
const tracksByAlbumKey = groupBy(trackDedupe.rows, (row) => row.candidate_identity_key);

const albums = buildAlbumInventory(graphAlbumRows, albumResolutionByKey, tracksByAlbumKey);
const albumsNeedingAppleCollectionId = albums
  .filter((album) => album.apple_link_pass_reasons.includes("missing_apple_collection_id"))
  .map(toAlbumPlanRow);
const tracksNeedingAppleTrackId = buildTrackPlanRows(trackDedupe.rows, graphAlbumsByKey);
const duplicateIdentityKeys = {
  graph_album_nodes: duplicateGroupKeys(graphAlbumsByKey),
  album_resolution_rows: duplicateGroupKeys(albumResolutionByKey),
  track_rows_by_album_and_index: duplicateTrackKeys(trackDedupe.rows),
};

const inventory = {
  metadata: {
    id: "apple_music_link_pass_inputs_v1",
    generated_at: new Date().toISOString(),
    intent: "Offline inventory for a future Apple Music link pass. This script does not call Apple APIs and does not require credentials.",
    output_path: relativePath(outputPath),
  },
  source_files: {
    graph_linking_node_set: sourceSummary(graphPath, graphRows.length, graphDedupe),
    album_track_sidecar_album_resolution: sourceSummary(
      albumResolutionPath,
      albumResolutionDedupe.rawCount,
      albumResolutionDedupe,
    ),
    album_track_sidecar_tracks: sourceSummary(trackPath, trackDedupe.rawCount, trackDedupe),
  },
  summary: {
    graph_album_nodes: graphAlbumRows.length,
    album_resolution_rows: albumResolutionDedupe.rows.length,
    track_rows: trackDedupe.rows.length,
    albums_with_resolution_row: albums.filter((album) => album.has_album_resolution_row).length,
    albums_missing_resolution_row: albums.filter((album) => !album.has_album_resolution_row).length,
    resolved_albums: albums.filter((album) => album.resolution_status === "resolved").length,
    albums_with_apple_collection_id: albums.filter((album) => album.apple_collection_id).length,
    albums_needing_apple_collection_id: albumsNeedingAppleCollectionId.length,
    tracks_with_apple_track_id: trackDedupe.rows.filter((row) => hasValue(row.apple_track_id)).length,
    tracks_needing_apple_track_id: tracksNeedingAppleTrackId.length,
    duplicate_identity_key_groups: {
      graph_album_nodes: duplicateIdentityKeys.graph_album_nodes.length,
      album_resolution_rows: duplicateIdentityKeys.album_resolution_rows.length,
      track_rows_by_album_and_index: duplicateIdentityKeys.track_rows_by_album_and_index.length,
    },
  },
  input_plan: {
    album_lookup_basis:
      "Use these rows as offline planning input for a later credentialed Apple Music link pass; prefer exact artist/title/year matching and preserve candidate_identity_key.",
    track_lookup_basis:
      "Use resolved sidecar tracks missing apple_track_id as offline planning input; preserve sidecar_track_index, disc_number, track_number, and track_title.",
    albums_needing_apple_collection_id: albumsNeedingAppleCollectionId,
    tracks_needing_apple_track_id: tracksNeedingAppleTrackId,
  },
  duplicate_identity_keys: duplicateIdentityKeys,
};

fs.mkdirSync(outputDir, { recursive: true });
writeJson(outputPath, inventory);

console.log(JSON.stringify(inventory.summary, null, 2));
console.error(`wrote ${relativePath(outputPath)}`);

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function writeJson(file, value) {
  fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`);
}

function readCsv(file) {
  const text = fs.readFileSync(file, "utf8");
  const records = parseCsv(text);
  if (records.length === 0) return [];
  const [headers, ...rows] = records;
  return rows
    .filter((row) => row.some((value) => value !== ""))
    .map((row) => Object.fromEntries(headers.map((header, index) => [header, row[index] ?? ""])));
}

function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let inQuotes = false;

  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];
    const next = text[index + 1];

    if (inQuotes) {
      if (char === '"' && next === '"') {
        field += '"';
        index += 1;
      } else if (char === '"') {
        inQuotes = false;
      } else {
        field += char;
      }
      continue;
    }

    if (char === '"') {
      inQuotes = true;
    } else if (char === ",") {
      row.push(field);
      field = "";
    } else if (char === "\n") {
      row.push(field);
      rows.push(row);
      row = [];
      field = "";
    } else if (char !== "\r") {
      field += char;
    }
  }

  if (field !== "" || row.length > 0) {
    row.push(field);
    rows.push(row);
  }

  return rows;
}

function dedupeRows(rows, keyForRow) {
  const seen = new Set();
  const deduped = [];
  let duplicateCount = 0;

  for (const row of rows) {
    const key = keyForRow(row);
    if (seen.has(key)) {
      duplicateCount += 1;
      continue;
    }
    seen.add(key);
    deduped.push(row);
  }

  return {
    rawCount: rows.length,
    duplicateCount,
    rows: deduped,
  };
}

function stableRowKey(row) {
  if (row === null || typeof row !== "object" || Array.isArray(row)) return JSON.stringify(row);
  return JSON.stringify(
    Object.keys(row)
      .sort()
      .reduce((accumulator, key) => {
        accumulator[key] = row[key];
        return accumulator;
      }, {}),
  );
}

function groupBy(rows, keyForRow) {
  const grouped = new Map();
  for (const row of rows) {
    const key = keyForRow(row) || "";
    if (!grouped.has(key)) grouped.set(key, []);
    grouped.get(key).push(row);
  }
  return grouped;
}

function buildAlbumInventory(graphAlbums, albumResolutionByKey, tracksByAlbumKey) {
  return graphAlbums
    .map((graphAlbum) => {
      const resolutionRows = albumResolutionByKey.get(graphAlbum.candidate_identity_key) ?? [];
      const resolution = pickResolutionRow(resolutionRows);
      const tracks = tracksByAlbumKey.get(graphAlbum.candidate_identity_key) ?? [];
      const appleLinkPassReasons = [];

      if (resolutionRows.length === 0) appleLinkPassReasons.push("missing_album_resolution_row");
      if (!hasValue(resolution?.apple_collection_id)) appleLinkPassReasons.push("missing_apple_collection_id");
      if (tracks.some((track) => !hasValue(track.apple_track_id))) appleLinkPassReasons.push("tracks_missing_apple_track_id");

      return {
        candidate_identity_key: graphAlbum.candidate_identity_key,
        artist_display_name: graphAlbum.artist_display_name,
        title: graphAlbum.title,
        year: graphAlbum.year,
        membership_count: graphAlbum.membership_count,
        archetype_ids: graphAlbum.archetype_ids ?? [],
        import_classes: graphAlbum.import_classes ?? [],
        has_album_resolution_row: resolutionRows.length > 0,
        album_resolution_row_count: resolutionRows.length,
        resolution_status: resolution?.resolution_status ?? "missing",
        selected_source: resolution?.selected_source ?? "",
        confidence: resolution?.confidence ?? "",
        track_count_reported: numberOrNull(resolution?.track_count),
        sidecar_track_rows: tracks.length,
        apple_collection_id: resolution?.apple_collection_id ?? "",
        musicbrainz_release_id: resolution?.musicbrainz_release_id ?? "",
        catalog_url: resolution?.catalog_url ?? "",
        apple_link_pass_reasons: appleLinkPassReasons,
      };
    })
    .sort(compareByIdentityKey);
}

function pickResolutionRow(rows) {
  if (rows.length === 0) return null;
  return [...rows].sort((left, right) => {
    const leftHasApple = hasValue(left.apple_collection_id) ? 0 : 1;
    const rightHasApple = hasValue(right.apple_collection_id) ? 0 : 1;
    if (leftHasApple !== rightHasApple) return leftHasApple - rightHasApple;
    return stableRowKey(left).localeCompare(stableRowKey(right));
  })[0];
}

function buildTrackPlanRows(trackRows, graphAlbumsByKey) {
  return trackRows
    .filter((row) => !hasValue(row.apple_track_id))
    .map((row) => {
      const graphAlbum = graphAlbumsByKey.get(row.candidate_identity_key)?.[0] ?? {};
      return {
        candidate_identity_key: row.candidate_identity_key,
        artist_display_name: row.artist_display_name || graphAlbum.artist_display_name || "",
        album_title: row.album_title || graphAlbum.title || "",
        album_year: row.album_year || stringifyValue(graphAlbum.year),
        archetype_ids: splitList(row.archetype_ids || graphAlbum.archetype_ids),
        selected_source: row.selected_source,
        apple_collection_id: row.apple_collection_id,
        musicbrainz_release_id: row.musicbrainz_release_id,
        sidecar_track_index: numberOrNull(row.sidecar_track_index),
        disc_number: numberOrNull(row.disc_number),
        track_number: numberOrNull(row.track_number),
        track_title: row.track_title,
        track_artist_name: row.track_artist_name,
        duration_ms: numberOrNull(row.duration_ms),
        track_url: row.track_url,
        is_streamable: parseBoolean(row.is_streamable),
      };
    })
    .sort(compareTrackPlanRows);
}

function toAlbumPlanRow(album) {
  return {
    candidate_identity_key: album.candidate_identity_key,
    artist_display_name: album.artist_display_name,
    title: album.title,
    year: album.year,
    membership_count: album.membership_count,
    archetype_ids: album.archetype_ids,
    import_classes: album.import_classes,
    resolution_status: album.resolution_status,
    selected_source: album.selected_source,
    confidence: album.confidence,
    track_count_reported: album.track_count_reported,
    sidecar_track_rows: album.sidecar_track_rows,
    musicbrainz_release_id: album.musicbrainz_release_id,
    catalog_url: album.catalog_url,
    apple_link_pass_reasons: album.apple_link_pass_reasons,
  };
}

function sourceSummary(file, rawRows, dedupe) {
  return {
    path: relativePath(file),
    raw_rows: rawRows,
    unique_rows: dedupe.rows.length,
    duplicate_source_rows_removed: dedupe.duplicateCount,
  };
}

function duplicateGroupKeys(grouped) {
  return [...grouped.entries()]
    .filter(([, rows]) => rows.length > 1)
    .map(([candidateIdentityKey, rows]) => ({
      candidate_identity_key: candidateIdentityKey,
      row_count: rows.length,
    }))
    .sort((left, right) => left.candidate_identity_key.localeCompare(right.candidate_identity_key));
}

function duplicateTrackKeys(rows) {
  const grouped = new Map();
  const partsByKey = new Map();

  for (const row of rows) {
    const parts = [
      row.candidate_identity_key,
      row.sidecar_track_index,
      row.disc_number,
      row.track_number,
      row.track_title,
    ];
    const key = JSON.stringify(parts);
    if (!grouped.has(key)) grouped.set(key, []);
    grouped.get(key).push(row);
    partsByKey.set(key, parts);
  }

  return [...grouped.entries()]
    .filter(([, duplicateRows]) => duplicateRows.length > 1)
    .map(([key, duplicateRows]) => {
      const [candidateIdentityKey, sidecarTrackIndex, discNumber, trackNumber, trackTitle] = partsByKey.get(key);
      return {
        candidate_identity_key: candidateIdentityKey,
        sidecar_track_index: numberOrNull(sidecarTrackIndex),
        disc_number: numberOrNull(discNumber),
        track_number: numberOrNull(trackNumber),
        track_title: trackTitle,
        row_count: duplicateRows.length,
      };
    })
    .sort((left, right) => {
      const albumOrder = left.candidate_identity_key.localeCompare(right.candidate_identity_key);
      if (albumOrder !== 0) return albumOrder;
      return (left.sidecar_track_index ?? 0) - (right.sidecar_track_index ?? 0);
    });
}

function compareByIdentityKey(left, right) {
  return left.candidate_identity_key.localeCompare(right.candidate_identity_key);
}

function compareTrackPlanRows(left, right) {
  const albumOrder = left.candidate_identity_key.localeCompare(right.candidate_identity_key);
  if (albumOrder !== 0) return albumOrder;
  return (left.sidecar_track_index ?? 0) - (right.sidecar_track_index ?? 0);
}

function hasValue(value) {
  return value !== undefined && value !== null && String(value).trim() !== "";
}

function numberOrNull(value) {
  if (!hasValue(value)) return null;
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function parseBoolean(value) {
  if (String(value).toLowerCase() === "true") return true;
  if (String(value).toLowerCase() === "false") return false;
  return null;
}

function splitList(value) {
  if (Array.isArray(value)) return value.map(stringifyValue).filter(Boolean);
  if (!hasValue(value)) return [];
  return String(value)
    .split(/[|;]/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function stringifyValue(value) {
  return value === undefined || value === null ? "" : String(value);
}

function relativePath(file) {
  return path.relative(repoRoot, file);
}
