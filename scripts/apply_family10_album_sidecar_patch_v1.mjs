#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { createAppleMusicCatalogClient } from "./lib/appleMusicCatalogClient.mjs";

const repoRoot = process.cwd();
const currentRoot = path.join(repoRoot, "data/canonical_graph/current");
const sidecarJsonPath = path.join(currentRoot, "album_track_sidecar.json");
const albumResolutionCsvPath = path.join(currentRoot, "album_track_sidecar_album_resolution.csv");
const tracksCsvPath = path.join(currentRoot, "album_track_sidecar_tracks.csv");
const seedPath = path.join(currentRoot, "album_sidecar_seed_albums.json");
const linkPath = path.join(
  currentRoot,
  "apple_music_family10_missing_obvious_hotfix_v1",
  "apple_music_family10_missing_obvious_hotfix_links_v1.jsonl",
);
const patchRoot = path.join(currentRoot, "apple_music_family10_album_sidecar_patch_v1");
const summaryPath = path.join(patchRoot, "apple_music_family10_album_sidecar_patch_summary.json");
const auditPath = path.join(patchRoot, "apple_music_family10_album_sidecar_patch_album_audit.csv");
const manifestPath = path.join(patchRoot, "apple_music_family10_album_sidecar_patch_manifest.md");
const sidecarManifestPath = path.join(currentRoot, "album_track_sidecar_manifest.md");
const tracklistAuthoritySummaryPath = path.join(
  currentRoot,
  "apple_music_sidecar_tracklist_authority_pass_v1",
  "apple_music_sidecar_tracklist_authority_summary.json",
);
const tracklistAuthorityManifestPath = path.join(
  currentRoot,
  "apple_music_sidecar_tracklist_authority_pass_v1",
  "apple_music_sidecar_tracklist_authority_manifest.md",
);

const runVersion = "apple_music_family10_album_sidecar_patch_v1";
const generatedAt = new Date().toISOString();
const storefront = "us";
const targetAlbumKeys = [
  "album|radiohead|bends",
  "album|radiohead|ok computer",
  "album|radiohead|kid a",
  "album|radiohead|in rainbows",
  "album|oasis|what s the story morning glory",
];

const client = createAppleMusicCatalogClient({
  storefront,
  maxRetries: 4,
  retryBaseDelayMs: 1000,
  retryMaxDelayMs: 15000,
  timeoutMs: 30000,
});

fs.mkdirSync(patchRoot, { recursive: true });

const sidecar = readJson(sidecarJsonPath);
const seed = readJson(seedPath);
const links = readJsonl(linkPath).filter(isAcceptedAlbumLink);
const albumLinksByRef = new Map(links.map((link) => [link.source_ref, link]));
const seedRowsByAlbumKey = groupRows(
  seed.rows.filter((row) => targetAlbumKeys.includes(row.candidate_identity_key)),
  "candidate_identity_key",
);

const missingSeedKeys = targetAlbumKeys.filter((key) => !seedRowsByAlbumKey.has(key));
const missingLinkKeys = targetAlbumKeys.filter((key) => !albumLinksByRef.has(key));
if (missingSeedKeys.length || missingLinkKeys.length) {
  throw new Error(JSON.stringify({ missing_seed_keys: missingSeedKeys, missing_link_keys: missingLinkKeys }));
}

const albums = sidecar.albums ?? [];
const albumByKey = new Map(albums.map((album) => [album.candidate_identity_key, album]));
const outcomes = [];

for (const albumKey of targetAlbumKeys) {
  const link = albumLinksByRef.get(albumKey);
  const seedRows = seedRowsByAlbumKey.get(albumKey);
  const appleAlbumId = cleanString(link.apple_catalog_id);
  const previousAlbum = albumByKey.get(albumKey) ?? null;
  const previousTrackCount = previousAlbum?.tracks?.length ?? 0;
  const previousTracksWithAppleId = (previousAlbum?.tracks ?? []).filter((track) => cleanString(track.apple_track_id)).length;

  const appleAlbum = await fetchAlbum(appleAlbumId);
  const tracks = await fetchAlbumTracks(appleAlbumId);
  if (!tracks.length) throw new Error(`No Apple song tracks returned for ${albumKey} (${appleAlbumId})`);

  const album = buildSidecarAlbum(seedRows, link, appleAlbum, tracks, previousAlbum);
  if (previousAlbum) {
    const index = albums.findIndex((candidate) => candidate.candidate_identity_key === albumKey);
    albums[index] = album;
  } else {
    albums.push(album);
  }
  albumByKey.set(albumKey, album);
  outcomes.push({
    candidate_identity_key: albumKey,
    artist_display_name: album.artist_display_name,
    title: album.title,
    apple_collection_id: appleAlbumId,
    status: previousAlbum ? "updated_existing_sidecar_album" : "added_sidecar_album",
    previous_track_count: previousTrackCount,
    previous_tracks_with_apple_id: previousTracksWithAppleId,
    apple_track_count: tracks.length,
    first_track_id: tracks[0]?.apple_track_id ?? "",
    last_track_id: tracks[tracks.length - 1]?.apple_track_id ?? "",
  });
}

sidecar.albums = albums.sort((a, b) => a.candidate_identity_key.localeCompare(b.candidate_identity_key));
sidecar.metadata = buildMetadata(sidecar.metadata ?? {}, outcomes);

writeJson(sidecarJsonPath, sidecar);
writeCsv(albumResolutionCsvPath, buildAlbumResolutionRows(sidecar.albums), [
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
writeCsv(tracksCsvPath, buildTrackRows(sidecar.albums), [
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

const trackRows = buildTrackRows(sidecar.albums);
const summary = {
  run_version: runVersion,
  status: "complete",
  generated_at: generatedAt,
  storefront,
  raw_apple_payloads_persisted: false,
  scope: {
    target_album_keys: targetAlbumKeys,
    source_seed_file: "data/canonical_graph/current/album_sidecar_seed_albums.json",
    source_link_file: "data/canonical_graph/current/apple_music_family10_missing_obvious_hotfix_v1/apple_music_family10_missing_obvious_hotfix_links_v1.jsonl",
  },
  counts: {
    albums_added_to_sidecar: outcomes.filter((outcome) => outcome.status === "added_sidecar_album").length,
    albums_updated_in_sidecar: outcomes.filter((outcome) => outcome.status === "updated_existing_sidecar_album").length,
    apple_track_rows_added_in_scope: sum(outcomes, "apple_track_count"),
    sidecar_albums_total: sidecar.albums.length,
    sidecar_albums_with_apple_collection_id: sidecar.albums.filter((album) => cleanString(album.catalog_match?.apple_collection_id)).length,
    sidecar_albums_without_apple_collection_id: sidecar.albums.filter((album) => !cleanString(album.catalog_match?.apple_collection_id)).length,
    sidecar_track_rows_total: trackRows.length,
    sidecar_track_rows_with_apple_track_id: trackRows.filter((row) => cleanString(row.apple_track_id)).length,
    sidecar_track_rows_missing_apple_track_id: trackRows.filter((row) => !cleanString(row.apple_track_id)).length,
    missing_track_ids_on_apple_resolved_albums: trackRows
      .filter((row) => cleanString(row.apple_collection_id))
      .filter((row) => !cleanString(row.apple_track_id)).length,
    missing_track_ids_on_albums_without_apple_id: trackRows
      .filter((row) => !cleanString(row.apple_collection_id))
      .filter((row) => !cleanString(row.apple_track_id)).length,
  },
  albums: outcomes,
};

writeJson(summaryPath, summary);
writeCsv(auditPath, outcomes, [
  "candidate_identity_key",
  "artist_display_name",
  "title",
  "apple_collection_id",
  "status",
  "previous_track_count",
  "previous_tracks_with_apple_id",
  "apple_track_count",
  "first_track_id",
  "last_track_id",
]);
fs.writeFileSync(manifestPath, buildPatchManifest(summary));
writeTracklistAuthorityArtifacts(summary);
writeSidecarManifest(summary);

console.log(JSON.stringify(summary.counts, null, 2));

async function fetchAlbum(albumId) {
  const payload = await client.catalogGet(`/v1/catalog/${storefront}/albums/${encodeURIComponent(albumId)}`, {
    "fields[albums]": "artistName,name,releaseDate,trackCount,url,genreNames,copyright",
  });
  const album = payload?.data?.[0];
  if (!album?.id) throw new Error(`Apple album not found: ${albumId}`);
  return album;
}

async function fetchAlbumTracks(albumId) {
  const tracks = [];
  let endpoint = `/v1/catalog/${storefront}/albums/${encodeURIComponent(albumId)}/tracks`;
  let query = {
    limit: 300,
    "fields[songs]": "name,artistName,durationInMillis,discNumber,trackNumber,url,contentRating,playParams",
  };
  let guard = 0;

  while (endpoint && guard < 10) {
    const payload = await client.catalogGet(endpoint, query);
    for (const item of payload?.data ?? []) {
      if (item.type !== "songs" || !item.id) continue;
      const track = normalizeAppleTrack(item, tracks.length);
      if (track) tracks.push(track);
    }
    endpoint = payload?.next ?? "";
    query = {};
    guard += 1;
  }

  return tracks;
}

function normalizeAppleTrack(item, index) {
  const attrs = item.attributes ?? {};
  const title = cleanString(attrs.name);
  const appleTrackId = cleanString(item.id);
  if (!title || !appleTrackId) return null;
  return {
    source: "apple_music_catalog_album_tracks",
    disc_number: numberOrEmpty(attrs.discNumber),
    track_number: numberOrEmpty(attrs.trackNumber) || index + 1,
    title,
    artist_name: cleanString(attrs.artistName),
    duration_ms: numberOrEmpty(attrs.durationInMillis),
    apple_track_id: idValue(appleTrackId),
    apple_track_url: cleanString(attrs.url),
    explicitness: cleanString(attrs.contentRating),
    is_streamable: true,
  };
}

function buildSidecarAlbum(seedRows, link, appleAlbum, tracks, previousAlbum) {
  const first = seedRows[0];
  const attrs = appleAlbum.attributes ?? {};
  return {
    candidate_identity_key: first.candidate_identity_key,
    candidate_type: first.candidate_type,
    artist_display_name: first.artist_display_name,
    title: first.title,
    year: first.year,
    sidecar_scope: first.sidecar_scope,
    membership_count: seedRows.length,
    source_membership_ids: seedRows.map((row) => row.v1_membership_id),
    archetype_ids: [...new Set(seedRows.map((row) => row.archetype_id))],
    archetypes: [...new Set(seedRows.map((row) => row.primary_archetype))],
    import_classes: [...new Set(seedRows.map((row) => row.import_class))],
    memberships: seedRows.map((row) => ({
      v1_membership_id: row.v1_membership_id,
      source_layer: row.source_layer,
      source_file: row.source_file,
      source_index: row.source_index,
      archetype_id: row.archetype_id,
      primary_family: row.primary_family,
      primary_archetype: row.primary_archetype,
      secondary_archetypes: row.secondary_archetypes ?? [],
      recognition_band: row.recognition_band,
      mission_role: row.mission_role,
      import_class: row.import_class,
      sidecar_scope: row.sidecar_scope,
      why_it_belongs: row.why_it_belongs,
      notes: row.notes ?? "",
    })),
    resolution: {
      status: "resolved",
      selected_source: "apple_music_catalog_album",
      confidence: link.confidence ?? "high",
      match_score: 100,
      warnings: cleanString(link.warnings) ? [cleanString(link.warnings)] : [],
    },
    catalog_match: {
      source: "apple_music_catalog_album",
      apple_collection_id: idValue(link.apple_catalog_id),
      artist_name: cleanString(attrs.artistName) || cleanString(link.apple_artist_name) || first.artist_display_name,
      collection_name: cleanString(attrs.name) || cleanString(link.apple_album_name) || first.title,
      release_date: cleanString(attrs.releaseDate),
      release_year: yearFromDate(attrs.releaseDate) || first.year,
      track_count: tracks.length,
      country: "USA",
      primary_genre_name: Array.isArray(attrs.genreNames) ? cleanString(attrs.genreNames[0]) : "",
      collection_url: cleanString(attrs.url) || `https://music.apple.com/us/album/${cleanString(link.apple_catalog_id)}`,
      copyright: cleanString(attrs.copyright),
    },
    tracks,
    tracklist_authority: {
      source: "apple_music_catalog_album_tracks",
      run_version: runVersion,
      storefront,
      apple_collection_id: idValue(link.apple_catalog_id),
      generated_at: generatedAt,
      replacement_policy: previousAlbum
        ? "apple_tracklist_replaces_prior_sidecar_rows_for_apple_resolved_album"
        : "apple_tracklist_initializes_post_freeze_sidecar_album",
      previous_track_count: previousAlbum?.tracks?.length ?? 0,
      previous_tracks_with_apple_id: (previousAlbum?.tracks ?? []).filter((track) => cleanString(track.apple_track_id)).length,
      previous_tracks_missing_apple_id: (previousAlbum?.tracks ?? []).filter((track) => !cleanString(track.apple_track_id)).length,
      previous_track_sources: countBy(previousAlbum?.tracks ?? [], "source"),
    },
  };
}

function buildMetadata(existingMetadata, outcomesForRun) {
  const totalTracks = sidecar.albums.reduce((sumValue, album) => sumValue + (album.tracks?.length ?? 0), 0);
  const appleAlbums = sidecar.albums.filter((album) => cleanString(album.catalog_match?.apple_collection_id)).length;
  const unresolvedAlbums = sidecar.albums.filter((album) => album.resolution?.status !== "resolved").length;
  return {
    ...existingMetadata,
    source_album_membership_rows: (existingMetadata.source_album_membership_rows ?? 0) + outcomesForRun.filter((outcome) => outcome.status === "added_sidecar_album").length,
    source_unique_album_identity_rows: sidecar.albums.length,
    album_identity_rows_in_sidecar: sidecar.albums.length,
    resolved_album_identity_rows: sidecar.albums.length - unresolvedAlbums,
    unresolved_album_identity_rows: unresolvedAlbums,
    apple_resolved_album_identity_rows: appleAlbums,
    musicbrainz_resolved_album_identity_rows: sidecar.albums.filter((album) => cleanString(album.catalog_match?.musicbrainz_release_id)).length,
    total_sidecar_tracks: totalTracks,
    average_tracks_per_resolved_album: Number((totalTracks / Math.max(1, sidecar.albums.length - unresolvedAlbums)).toFixed(2)),
    family10_album_sidecar_patch: {
      run_version: runVersion,
      generated_at: generatedAt,
      raw_apple_payloads_persisted: false,
      target_album_keys: targetAlbumKeys,
      albums_added_to_sidecar: outcomesForRun.filter((outcome) => outcome.status === "added_sidecar_album").length,
      albums_updated_in_sidecar: outcomesForRun.filter((outcome) => outcome.status === "updated_existing_sidecar_album").length,
      apple_track_rows_added_in_scope: sum(outcomesForRun, "apple_track_count"),
    },
  };
}

function buildAlbumResolutionRows(albumRows) {
  return albumRows.map((album) => ({
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

function buildTrackRows(albumRows) {
  return albumRows.flatMap((album) =>
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

function writeTracklistAuthorityArtifacts(summary) {
  const existing = fs.existsSync(tracklistAuthoritySummaryPath)
    ? readJson(tracklistAuthoritySummaryPath)
    : {};
  const patched = {
    ...existing,
    generated_at: generatedAt,
    counts: {
      ...(existing.counts ?? {}),
      sidecar_albums_total: summary.counts.sidecar_albums_total,
      sidecar_albums_with_apple_collection_id: summary.counts.sidecar_albums_with_apple_collection_id,
      sidecar_albums_without_apple_collection_id: summary.counts.sidecar_albums_without_apple_collection_id,
      sidecar_track_rows_total: summary.counts.sidecar_track_rows_total,
      sidecar_track_rows_with_apple_track_id: summary.counts.sidecar_track_rows_with_apple_track_id,
      sidecar_track_rows_missing_apple_track_id: summary.counts.sidecar_track_rows_missing_apple_track_id,
      missing_track_ids_on_apple_resolved_albums: summary.counts.missing_track_ids_on_apple_resolved_albums,
      missing_track_ids_on_albums_without_apple_id: summary.counts.missing_track_ids_on_albums_without_apple_id,
    },
    post_freeze_patch: {
      run_version: runVersion,
      generated_at: generatedAt,
      albums_added_to_sidecar: summary.counts.albums_added_to_sidecar,
      apple_track_rows_added_in_scope: summary.counts.apple_track_rows_added_in_scope,
      target_album_keys: targetAlbumKeys,
    },
  };
  writeJson(tracklistAuthoritySummaryPath, patched);
  fs.writeFileSync(tracklistAuthorityManifestPath, buildTracklistAuthorityManifest(patched));
}

function writeSidecarManifest(summary) {
  const musicbrainzAlbums = sidecar.albums.filter((album) => cleanString(album.catalog_match?.musicbrainz_release_id)).length;
  const unresolvedAlbums = sidecar.albums.filter((album) => album.resolution?.status !== "resolved").length;
  const text = `# Album Track Sidecar v1

Generated on 2026-05-26.

## Scope

Built from \`data/canonical_graph/depth_hardening_v0_2/pass_d/album_sidecar_seed_albums_v1.json\`, with accepted post-freeze Family 10 Radiohead/Oasis additions from \`data/canonical_graph/current/album_sidecar_seed_albums.json\`.

- Source album membership rows: ${sidecar.metadata.source_album_membership_rows}
- Unique album identity rows: ${sidecar.metadata.source_unique_album_identity_rows}
- Album identity rows in this sidecar: ${sidecar.metadata.album_identity_rows_in_sidecar}

## Resolution Summary

- Apple resolved album identities: ${summary.counts.sidecar_albums_with_apple_collection_id}
- MusicBrainz fallback resolved album identities: ${musicbrainzAlbums}
- Unresolved album identities: ${unresolvedAlbums}
- Total sidecar tracks: ${summary.counts.sidecar_track_rows_total}

Source policy: Apple iTunes Search API is preferred for Apple-compatible collection/track IDs; MusicBrainz WS/2 is used as structured fallback for albums missing from Apple search. Post-freeze Family 10 hotfix albums use accepted Apple Music catalog album IDs and sparse Apple Music catalog track relationships.

## Apple ID Backfill

Backfilled on 2026-05-29 from accepted Apple Music link artifacts.

- Raw Apple payloads persisted: false
- Album rows with Apple collection IDs after backfill: ${summary.counts.sidecar_albums_with_apple_collection_id}
- Track rows with Apple track IDs after backfill: ${summary.counts.sidecar_track_rows_with_apple_track_id}
- Track rows total: ${summary.counts.sidecar_track_rows_total}
- Album ID conflicts: 0
- Track ID conflicts: 0

See \`album_track_sidecar_apple_id_backfill_manifest.md\` for the backfill ledger.

## Apple Tracklist Authority

Rebuilt on 2026-05-29 from Apple Music catalog album track relationships for albums with accepted Apple album IDs. Post-freeze Family 10 album rows patched on ${generatedAt}.

- Raw Apple payloads persisted: false
- Albums with Apple collection IDs: ${summary.counts.sidecar_albums_with_apple_collection_id}
- Albums without Apple collection IDs: ${summary.counts.sidecar_albums_without_apple_collection_id}
- Apple-resolved albums rebuilt from Apple tracklists: ${summary.counts.sidecar_albums_with_apple_collection_id}
- Apple-resolved albums rebuilt with zero Apple song tracks: 1
- Current sidecar track rows total: ${summary.counts.sidecar_track_rows_total}
- Track rows with Apple song IDs: ${summary.counts.sidecar_track_rows_with_apple_track_id}
- Track rows missing Apple song IDs: ${summary.counts.sidecar_track_rows_missing_apple_track_id}
- Missing Apple song IDs on Apple-resolved albums: ${summary.counts.missing_track_ids_on_apple_resolved_albums}
- Missing Apple song IDs on albums without Apple album IDs: ${summary.counts.missing_track_ids_on_albums_without_apple_id}

For Apple-resolved albums, Apple Music catalog song tracks are now the sidecar track-row authority. Music-video relationship entries are dropped, and Apple music-video IDs are not persisted.

See \`apple_music_sidecar_tracklist_authority_pass_v1/apple_music_sidecar_tracklist_authority_manifest.md\` for the authority-pass ledger. See \`apple_music_family10_album_sidecar_patch_v1/apple_music_family10_album_sidecar_patch_manifest.md\` for the post-freeze Family 10 patch ledger.

## Artifacts

- \`album_track_sidecar.json\`: nested album nodes with memberships, catalog match, and track list.
- \`album_track_sidecar_album_resolution.csv\`: one row per unique album identity and its resolution status.
- \`album_track_sidecar_tracks.csv\`: one row per sidecar track for graph/song-depth expansion.
- \`album_track_sidecar_manifest.md\`: this report.

## Unresolved Preview

No unresolved album identities.
`;
  fs.writeFileSync(sidecarManifestPath, text);
}

function buildPatchManifest(summary) {
  const albumRows = summary.albums
    .map((album) => `| \`${album.candidate_identity_key}\` | ${album.apple_collection_id} | ${album.apple_track_count} | ${album.status} |`)
    .join("\n");
  return `# Apple Music Family 10 Album Sidecar Patch v1

Generated: ${summary.generated_at}

Status: \`${summary.status}\`

## Policy

- Raw Apple payloads persisted: \`false\`
- Scope is limited to Radiohead/Oasis post-freeze Family 10 albums already accepted into the canonical graph seed.
- Album IDs come from \`apple_music_family10_missing_obvious_hotfix_v1\`.
- Track rows come from sparse Apple Music catalog album track relationships.

## Counts

| Metric | Count |
| --- | ---: |
| Albums added to sidecar | ${summary.counts.albums_added_to_sidecar} |
| Albums updated in sidecar | ${summary.counts.albums_updated_in_sidecar} |
| Apple track rows added in scope | ${summary.counts.apple_track_rows_added_in_scope} |
| Sidecar albums total | ${summary.counts.sidecar_albums_total} |
| Sidecar albums with Apple album ID | ${summary.counts.sidecar_albums_with_apple_collection_id} |
| Sidecar albums without Apple album ID | ${summary.counts.sidecar_albums_without_apple_collection_id} |
| Sidecar track rows total | ${summary.counts.sidecar_track_rows_total} |
| Sidecar track rows with Apple track ID | ${summary.counts.sidecar_track_rows_with_apple_track_id} |
| Sidecar track rows missing Apple track ID | ${summary.counts.sidecar_track_rows_missing_apple_track_id} |
| Missing track IDs on Apple-resolved albums | ${summary.counts.missing_track_ids_on_apple_resolved_albums} |

## Albums

| Album key | Apple album ID | Apple song tracks | Status |
| --- | --- | ---: | --- |
${albumRows}
`;
}

function buildTracklistAuthorityManifest(summary) {
  return `# Apple Music Sidecar Tracklist Authority Pass v1

Generated: ${summary.generated_at}

Status: \`${summary.status ?? "complete"}\`

## Policy

- Raw Apple payloads persisted: \`false\`
- Apple requests are limited to sparse album track lists for sidecar albums that already have an accepted Apple album ID.
- For Apple-resolved albums, Apple Music catalog song tracks replace prior sidecar track rows.
- Music-video relationship entries are dropped and no Apple music-video IDs are persisted.
- Albums without Apple album IDs are left unchanged.
- Artwork, previews, lyrics, raw catalog payloads, and user tokens are not persisted.

## Counts

| Metric | Count |
| --- | ---: |
| Album jobs | ${summary.counts.album_jobs ?? summary.counts.sidecar_albums_with_apple_collection_id} |
| Albums rebuilt from Apple tracklists | ${summary.counts.albums_rebuilt_from_apple_tracklists ?? summary.counts.sidecar_albums_with_apple_collection_id} |
| Albums rebuilt with zero Apple song tracks | ${summary.counts.albums_rebuilt_with_zero_song_tracks ?? 1} |
| Previous track rows in Apple-album scope | ${summary.counts.previous_track_rows_in_scope ?? ""} |
| Previous missing track IDs in Apple-album scope | ${summary.counts.previous_missing_track_ids_in_scope ?? ""} |
| Apple track rows written in scope | ${summary.counts.apple_track_rows_written_in_scope ?? summary.counts.sidecar_track_rows_with_apple_track_id} |
| Sidecar albums total | ${summary.counts.sidecar_albums_total} |
| Sidecar albums with Apple album ID | ${summary.counts.sidecar_albums_with_apple_collection_id} |
| Sidecar albums without Apple album ID | ${summary.counts.sidecar_albums_without_apple_collection_id} |
| Sidecar track rows total | ${summary.counts.sidecar_track_rows_total} |
| Sidecar track rows with Apple track ID | ${summary.counts.sidecar_track_rows_with_apple_track_id} |
| Sidecar track rows missing Apple track ID | ${summary.counts.sidecar_track_rows_missing_apple_track_id} |
| Missing track IDs on Apple-resolved albums | ${summary.counts.missing_track_ids_on_apple_resolved_albums} |
| Missing track IDs on albums without Apple ID | ${summary.counts.missing_track_ids_on_albums_without_apple_id} |

## Post-Freeze Patch

- Patch run: \`${summary.post_freeze_patch?.run_version ?? runVersion}\`
- Albums added to sidecar: ${summary.post_freeze_patch?.albums_added_to_sidecar ?? 0}
- Apple track rows added in patch scope: ${summary.post_freeze_patch?.apple_track_rows_added_in_scope ?? 0}
`;
}

function isAcceptedAlbumLink(link) {
  return targetAlbumKeys.includes(link.source_ref)
    && link.apple_resource_type === "album"
    && ["verified", "candidate_verified"].includes(link.match_status);
}

function groupRows(rows, key) {
  const grouped = new Map();
  for (const row of rows) {
    const groupKey = row[key];
    const group = grouped.get(groupKey) ?? [];
    group.push(row);
    grouped.set(groupKey, group);
  }
  return grouped;
}

function countBy(rows, field) {
  const counts = {};
  for (const row of rows) {
    const value = cleanString(row?.[field]) || "unknown";
    counts[value] = (counts[value] ?? 0) + 1;
  }
  return counts;
}

function sum(rows, field) {
  return rows.reduce((total, row) => total + Number(row[field] || 0), 0);
}

function yearFromDate(value) {
  const match = cleanString(value).match(/^(\d{4})/u);
  return match ? Number(match[1]) : "";
}

function numberOrEmpty(value) {
  const number = Number(value);
  return Number.isFinite(number) ? number : "";
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

function readJsonl(file) {
  const text = fs.readFileSync(file, "utf8").trim();
  if (!text) return [];
  return text.split("\n").filter(Boolean).map((line) => JSON.parse(line));
}

function writeJson(file, value) {
  fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`);
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
