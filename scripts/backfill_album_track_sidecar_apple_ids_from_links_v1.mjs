#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

const repoRoot = process.cwd();
const currentRoot = path.join(repoRoot, "data/canonical_graph/current");
const outputManifestPath = path.join(currentRoot, "album_track_sidecar_apple_id_backfill_manifest.md");
const sidecarJsonPath = path.join(currentRoot, "album_track_sidecar.json");
const albumResolutionCsvPath = path.join(currentRoot, "album_track_sidecar_album_resolution.csv");
const tracksCsvPath = path.join(currentRoot, "album_track_sidecar_tracks.csv");

const linkInputSpecs = [
  "apple_music_link_pass_v1/apple_music_links_v1.jsonl",
  "apple_music_try_harder_pass_v1/apple_music_try_harder_links_v1.jsonl",
  "apple_music_residual_track_pass_v1/apple_music_residual_track_links_v1.jsonl",
  "apple_music_album_variant_pass_v1/apple_music_album_variant_links_v1.jsonl",
  "apple_music_offline_reconciliation_pass_v1/apple_music_offline_reconciliation_links_v1.jsonl",
  "apple_music_artist_album_resolver_pass_v1/apple_music_artist_album_resolver_links_v1.jsonl",
  "apple_music_high_confidence_album_pass_v1/apple_music_high_confidence_album_links_v1.jsonl",
  "apple_music_manual_album_review_pass_v1/apple_music_manual_album_review_links_v1.jsonl",
  "apple_music_semantic_album_hardening_pass_v1/apple_music_semantic_album_hardening_links_v1.jsonl",
  "apple_music_album_graph_decision_pass_v1/apple_music_album_graph_decision_links_v1.jsonl",
  "apple_music_song_source_album_reconciliation_pass_v1/apple_music_song_source_album_reconciliation_links_v1.jsonl",
  "apple_music_direct_song_hardening_pass_v1/apple_music_direct_song_hardening_links_v1.jsonl",
  "apple_music_direct_song_hardening_pass_v2/apple_music_direct_song_hardening_v2_links.jsonl",
  "apple_music_recording_hardening_pass_v1/apple_music_recording_hardening_links_v1.jsonl",
  "apple_music_graph_song_iterative_hardening_pass_v1/apple_music_graph_song_iterative_hardening_links_v1.jsonl",
  "apple_music_sidecar_track_album_bound_pass_v1/apple_music_sidecar_track_album_bound_links_v1.jsonl",
];

const sidecar = readJson(sidecarJsonPath);
const allLinks = linkInputSpecs.flatMap((relativePath) =>
  safeReadJsonl(path.join(currentRoot, relativePath)).map((link) => ({ ...link, __input_path: relativePath })),
);
const acceptedLinks = allLinks.filter(isAcceptedLink);
const albumLinksByRef = bestAcceptedLinksBySourceRef(
  acceptedLinks.filter((link) => link.source_type === "album_sidecar_album" && link.apple_resource_type === "album"),
);
const trackLinksByRef = bestAcceptedLinksBySourceRef(
  acceptedLinks.filter((link) => link.source_type === "album_sidecar_track" && link.apple_resource_type === "song"),
);

let albumIdsAddedToJson = 0;
let albumIdsAlreadyInJson = 0;
let trackIdsAddedToJson = 0;
let trackIdsAlreadyInJson = 0;
let trackUrlsAddedToJson = 0;
const albumLinkRefsUsed = new Set();
const trackLinkRefsUsed = new Set();
const albumIdConflicts = [];
const trackIdConflicts = [];

for (const album of sidecar.albums ?? []) {
  const albumLink = albumLinksByRef.get(album.candidate_identity_key);
  if (albumLink) {
    albumLinkRefsUsed.add(album.candidate_identity_key);
    const existingAlbumId = cleanString(album.catalog_match?.apple_collection_id);
    const linkAlbumId = cleanString(albumLink.apple_catalog_id);
    if (existingAlbumId && existingAlbumId !== linkAlbumId) {
      albumIdConflicts.push({
        candidate_identity_key: album.candidate_identity_key,
        existing_apple_collection_id: existingAlbumId,
        link_apple_catalog_id: linkAlbumId,
      });
    } else if (existingAlbumId) {
      albumIdsAlreadyInJson += 1;
    } else if (linkAlbumId) {
      if (!album.catalog_match) album.catalog_match = {};
      album.catalog_match.apple_collection_id = idValue(linkAlbumId);
      albumIdsAddedToJson += 1;
    }
  }

  for (const track of album.tracks ?? []) {
    const sourceRef = sidecarTrackSourceRef(album, track);
    const trackLink = trackLinksByRef.get(sourceRef);
    if (!trackLink) continue;

    trackLinkRefsUsed.add(sourceRef);
    const existingTrackId = cleanString(track.apple_track_id);
    const linkTrackId = cleanString(trackLink.apple_catalog_id);
    if (existingTrackId && existingTrackId !== linkTrackId) {
      trackIdConflicts.push({
        source_ref: sourceRef,
        existing_apple_track_id: existingTrackId,
        link_apple_catalog_id: linkTrackId,
      });
      continue;
    }

    if (existingTrackId) {
      trackIdsAlreadyInJson += 1;
    } else if (linkTrackId) {
      track.apple_track_id = idValue(linkTrackId);
      trackIdsAddedToJson += 1;
    }

    const albumId = cleanString(album.catalog_match?.apple_collection_id)
      || cleanString(trackLink.apple_album_id)
      || cleanString(trackLink.album_apple_catalog_id);
    if (!track.apple_track_url && albumId && linkTrackId) {
      track.apple_track_url = `https://music.apple.com/us/album/${albumId}?i=${linkTrackId}`;
      trackUrlsAddedToJson += 1;
    }
  }
}

sidecar.metadata = {
  ...(sidecar.metadata ?? {}),
  apple_link_backfill: {
    run_version: "album_track_sidecar_apple_id_backfill_v1",
    generated_at: new Date().toISOString(),
    raw_apple_payloads_persisted: false,
    source_link_files: linkInputSpecs.map((relativePath) => `data/canonical_graph/current/${relativePath}`),
    album_sidecar_album_links_considered: albumLinksByRef.size,
    album_sidecar_album_links_used: albumLinkRefsUsed.size,
    album_apple_collection_ids_added_to_sidecar: albumIdsAddedToJson,
    album_apple_collection_ids_already_present: albumIdsAlreadyInJson,
    album_id_conflicts: albumIdConflicts.length,
    album_sidecar_track_links_considered: trackLinksByRef.size,
    album_sidecar_track_links_used: trackLinkRefsUsed.size,
    track_apple_ids_added_to_sidecar: trackIdsAddedToJson,
    track_apple_ids_already_present: trackIdsAlreadyInJson,
    track_urls_derived_and_added: trackUrlsAddedToJson,
    track_id_conflicts: trackIdConflicts.length,
  },
};

const albumResolutionRows = buildAlbumResolutionRows(sidecar.albums ?? []);
const trackRows = buildTrackRows(sidecar.albums ?? []);
writeJson(sidecarJsonPath, sidecar);
writeCsv(albumResolutionCsvPath, albumResolutionRows, [
  "candidate_identity_key",
  "artist_display_name",
  "title",
  "year",
  "membership_count",
  "archetype_ids",
  "import_classes",
  "resolution_status",
  "selected_source",
  "confidence",
  "match_score",
  "track_count",
  "catalog_artist_name",
  "catalog_collection_name",
  "catalog_release_date",
  "apple_collection_id",
  "musicbrainz_release_group_id",
  "musicbrainz_release_id",
  "catalog_url",
  "warnings",
]);
writeCsv(tracksCsvPath, trackRows, [
  "candidate_identity_key",
  "artist_display_name",
  "album_title",
  "album_year",
  "membership_count",
  "archetype_ids",
  "selected_source",
  "apple_collection_id",
  "musicbrainz_release_id",
  "sidecar_track_index",
  "disc_number",
  "track_number",
  "track_title",
  "track_artist_name",
  "duration_ms",
  "apple_track_id",
  "musicbrainz_recording_id",
  "track_url",
  "is_streamable",
]);
writeManifest({
  albumResolutionRows,
  trackRows,
  albumLinkRefsUsed,
  trackLinkRefsUsed,
  albumIdConflicts,
  trackIdConflicts,
});

console.log(JSON.stringify({
  status: "complete",
  raw_apple_payloads_persisted: false,
  album_sidecar_album_links_considered: albumLinksByRef.size,
  album_sidecar_album_links_used: albumLinkRefsUsed.size,
  album_apple_collection_ids_added_to_sidecar: albumIdsAddedToJson,
  album_apple_collection_ids_already_present: albumIdsAlreadyInJson,
  album_id_conflicts: albumIdConflicts.length,
  album_rows_with_apple_collection_id: albumResolutionRows.filter((row) => row.apple_collection_id).length,
  album_sidecar_track_links_considered: trackLinksByRef.size,
  album_sidecar_track_links_used: trackLinkRefsUsed.size,
  track_apple_ids_added_to_sidecar: trackIdsAddedToJson,
  track_apple_ids_already_present: trackIdsAlreadyInJson,
  track_urls_derived_and_added: trackUrlsAddedToJson,
  track_id_conflicts: trackIdConflicts.length,
  track_rows_with_apple_track_id: trackRows.filter((row) => row.apple_track_id).length,
  track_rows_total: trackRows.length,
}, null, 2));

function buildAlbumResolutionRows(albums) {
  return albums.map((album) => ({
    candidate_identity_key: album.candidate_identity_key,
    artist_display_name: album.artist_display_name,
    title: album.title,
    year: album.year,
    membership_count: album.membership_count,
    archetype_ids: album.archetype_ids,
    import_classes: album.import_classes,
    resolution_status: album.resolution?.status ?? "",
    selected_source: album.resolution?.selected_source ?? "",
    confidence: album.resolution?.confidence ?? "",
    match_score: album.resolution?.match_score ?? album.resolution?.best_candidate_match_score ?? "",
    track_count: album.tracks?.length ?? 0,
    catalog_artist_name: album.catalog_match?.artist_name ?? "",
    catalog_collection_name: album.catalog_match?.collection_name ?? "",
    catalog_release_date: album.catalog_match?.release_date ?? "",
    apple_collection_id: album.catalog_match?.apple_collection_id ?? "",
    musicbrainz_release_group_id: album.catalog_match?.musicbrainz_release_group_id ?? "",
    musicbrainz_release_id: album.catalog_match?.musicbrainz_release_id ?? "",
    catalog_url: album.catalog_match?.collection_url ?? "",
    warnings: album.resolution?.warnings ?? [],
  }));
}

function buildTrackRows(albums) {
  return albums.flatMap((album) =>
    (album.tracks ?? []).map((track, index) => ({
      candidate_identity_key: album.candidate_identity_key,
      artist_display_name: album.artist_display_name,
      album_title: album.title,
      album_year: album.year,
      membership_count: album.membership_count,
      archetype_ids: album.archetype_ids,
      selected_source: album.resolution?.selected_source ?? "",
      apple_collection_id: album.catalog_match?.apple_collection_id ?? "",
      musicbrainz_release_id: album.catalog_match?.musicbrainz_release_id ?? "",
      sidecar_track_index: index + 1,
      disc_number: track.disc_number ?? "",
      track_number: track.track_number ?? "",
      track_title: track.title,
      track_artist_name: track.artist_name ?? "",
      duration_ms: track.duration_ms ?? "",
      apple_track_id: track.apple_track_id ?? "",
      musicbrainz_recording_id: track.musicbrainz_recording_id ?? "",
      track_url: track.apple_track_url ?? "",
      is_streamable: track.is_streamable,
    })),
  );
}

function writeManifest(summary) {
  const albumRowsWithApple = summary.albumResolutionRows.filter((row) => row.apple_collection_id).length;
  const trackRowsWithApple = summary.trackRows.filter((row) => row.apple_track_id).length;
  const text = `# Album Track Sidecar Apple ID Backfill v1

Generated: ${sidecar.metadata.apple_link_backfill.generated_at}

Status: \`complete\`

## Policy

- Raw Apple payloads persisted: \`false\`
- No Apple catalog requests were made.
- Source data is accepted Apple link JSONL output only.
- Durable updates are Apple collection IDs, Apple track IDs, and derived Apple Music track URLs for existing sidecar rows.

## Counts

| Metric | Count |
| --- | ---: |
| Album sidecar album links considered | ${albumLinksByRef.size} |
| Album sidecar album links used | ${summary.albumLinkRefsUsed.size} |
| Album Apple collection IDs added to sidecar | ${albumIdsAddedToJson} |
| Album Apple collection IDs already present | ${albumIdsAlreadyInJson} |
| Album ID conflicts | ${summary.albumIdConflicts.length} |
| Album rows with Apple collection ID after backfill | ${albumRowsWithApple} |
| Album sidecar track links considered | ${trackLinksByRef.size} |
| Album sidecar track links used | ${summary.trackLinkRefsUsed.size} |
| Track Apple IDs added to sidecar | ${trackIdsAddedToJson} |
| Track Apple IDs already present | ${trackIdsAlreadyInJson} |
| Track URLs derived and added | ${trackUrlsAddedToJson} |
| Track ID conflicts | ${summary.trackIdConflicts.length} |
| Track rows with Apple track ID after backfill | ${trackRowsWithApple} |
| Total track rows | ${summary.trackRows.length} |
`;
  fs.writeFileSync(outputManifestPath, text);
}

function bestAcceptedLinksBySourceRef(links) {
  const byRef = new Map();
  for (const link of links) {
    const prior = byRef.get(link.source_ref);
    if (!prior || linkPriority(link) > linkPriority(prior)) byRef.set(link.source_ref, link);
  }
  return byRef;
}

function linkPriority(link) {
  let score = 0;
  if (link.match_status === "verified") score += 1000;
  if (link.confidence === "high") score += 100;
  if (link.confidence === "medium") score += 50;
  if (link.run_version?.includes("manual")) score += 10;
  return score;
}

function isAcceptedLink(link) {
  return ["verified", "candidate_verified"].includes(link.match_status);
}

function sidecarTrackSourceRef(album, track) {
  return [
    album.candidate_identity_key,
    track.disc_number ?? "",
    track.track_number ?? "",
    normalizeLegacySourceRefSegment(track.artist_name),
    normalizeLegacySourceRefSegment(track.title),
  ].join("@@");
}

function normalizeLegacySourceRefSegment(value) {
  return String(value ?? "")
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/&/g, " and ")
    .replace(/[^a-z0-9]+/g, " ")
    .trim()
    .replace(/\bthe\b/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

function idValue(value) {
  const text = cleanString(value);
  const numeric = Number(text);
  if (/^\d+$/u.test(text) && Number.isSafeInteger(numeric)) return numeric;
  return text;
}

function cleanString(value) {
  if (value === undefined || value === null) return "";
  return String(value).trim();
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function writeJson(file, value) {
  fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`);
}

function safeReadJsonl(file) {
  if (!fs.existsSync(file)) return [];
  const text = fs.readFileSync(file, "utf8").trim();
  if (!text) return [];
  return text.split("\n").filter(Boolean).map((line) => JSON.parse(line));
}

function writeCsv(file, rows, headers) {
  const lines = [headers.join(",")];
  for (const row of rows) {
    lines.push(headers.map((header) => csvCell(row[header] ?? "")).join(","));
  }
  fs.writeFileSync(file, `${lines.join("\n")}\n`);
}

function csvCell(value) {
  const text = Array.isArray(value) ? value.join(";") : String(value ?? "");
  if (/[",\n\r]/u.test(text)) return `"${text.replace(/"/g, "\"\"")}"`;
  return text;
}
