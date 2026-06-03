#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { createAppleMusicCatalogClient } from "./lib/appleMusicCatalogClient.mjs";

const repoRoot = process.cwd();
const currentRoot = path.join(repoRoot, "data/canonical_graph/current");
const outputRoot = path.join(currentRoot, "apple_music_sidecar_tracklist_authority_pass_v1");
const runVersion = "apple_music_sidecar_tracklist_authority_pass_v1";
const generatedAt = new Date().toISOString();

const sidecarJsonPath = path.join(currentRoot, "album_track_sidecar.json");
const albumResolutionCsvPath = path.join(currentRoot, "album_track_sidecar_album_resolution.csv");
const tracksCsvPath = path.join(currentRoot, "album_track_sidecar_tracks.csv");
const summaryPath = path.join(outputRoot, "apple_music_sidecar_tracklist_authority_summary.json");
const albumAuditPath = path.join(outputRoot, "apple_music_sidecar_tracklist_authority_album_audit_v1.csv");
const manifestPath = path.join(outputRoot, "apple_music_sidecar_tracklist_authority_manifest.md");
const checkpointPath = path.join(outputRoot, "apple_music_sidecar_tracklist_authority_pass_v1.checkpoint.json");

const args = parseArgs(process.argv.slice(2));
const client = createAppleMusicCatalogClient({
  storefront: args.storefront,
  maxRetries: args.maxRetries,
  retryBaseDelayMs: 1000,
  retryMaxDelayMs: 60000,
  timeoutMs: 60000,
});

fs.mkdirSync(outputRoot, { recursive: true });

const sidecar = readJson(sidecarJsonPath);
const albums = sidecar.albums ?? [];
const albumByKey = new Map(albums.map((album) => [album.candidate_identity_key, album]));
const checkpoint = args.resume ? safeReadJson(checkpointPath) : null;
const completedJobKeys = new Set(checkpoint?.completed_job_keys ?? []);
const outcomes = checkpoint?.outcomes ?? [];
const outcomeByJobKey = new Map(outcomes.map((outcome) => [outcome.job_key, outcome]));
const jobs = buildJobs();

let completed = 0;

console.error(JSON.stringify({
  run_version: runVersion,
  storefront: args.storefront,
  album_jobs: jobs.length,
  dry_run: args.dryRun,
  concurrency: args.concurrency,
}, null, 2));

await runPool(
  jobs.filter((job) => !completedJobKeys.has(job.job_key)),
  args.concurrency,
  async (job) => {
    const outcome = await rebuildJobSafely(job);
    if (!outcomeByJobKey.has(job.job_key)) outcomes.push(outcome);
    outcomeByJobKey.set(job.job_key, outcome);
    completedJobKeys.add(job.job_key);
    completed += 1;
    if (completed % args.checkpointEvery === 0) writeCheckpoint("partial");
    if (completed % args.progressEvery === 0 || completed === jobs.length) {
      console.error(`Apple tracklist authority pass: completed ${completed}/${jobs.length}`);
    }
  },
);

writeCheckpoint("complete");
if (!args.dryRun) applyOutcomesToSidecar();
writeFinalArtifacts();
if (!args.keepCheckpoint && fs.existsSync(checkpointPath)) fs.unlinkSync(checkpointPath);

function parseArgs(argv) {
  const parsed = {
    storefront: "us",
    concurrency: 8,
    maxRetries: 8,
    progressEvery: 50,
    checkpointEvery: 50,
    resume: true,
    keepCheckpoint: false,
    dryRun: false,
    limitAlbums: Number.NaN,
    sourceRefs: [],
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--storefront") parsed.storefront = argv[++index];
    else if (arg === "--concurrency") parsed.concurrency = Number(argv[++index]);
    else if (arg === "--max-retries") parsed.maxRetries = Number(argv[++index]);
    else if (arg === "--progress-every") parsed.progressEvery = Number(argv[++index]);
    else if (arg === "--checkpoint-every") parsed.checkpointEvery = Number(argv[++index]);
    else if (arg === "--no-resume") parsed.resume = false;
    else if (arg === "--keep-checkpoint") parsed.keepCheckpoint = true;
    else if (arg === "--dry-run") parsed.dryRun = true;
    else if (arg === "--limit-albums") parsed.limitAlbums = Number(argv[++index]);
    else if (arg === "--source-ref") parsed.sourceRefs.push(argv[++index]);
  }

  if (!parsed.storefront) parsed.storefront = "us";
  if (!Number.isFinite(parsed.concurrency) || parsed.concurrency < 1) parsed.concurrency = 1;
  if (parsed.concurrency > 12) parsed.concurrency = 12;
  if (!Number.isFinite(parsed.maxRetries) || parsed.maxRetries < 0) parsed.maxRetries = 3;
  if (!Number.isFinite(parsed.progressEvery) || parsed.progressEvery < 1) parsed.progressEvery = 50;
  if (!Number.isFinite(parsed.checkpointEvery) || parsed.checkpointEvery < 1) parsed.checkpointEvery = parsed.progressEvery;
  return parsed;
}

function buildJobs() {
  const sourceFilter = args.sourceRefs.length ? new Set(args.sourceRefs) : null;
  const selected = albums
    .filter((album) => cleanString(album.catalog_match?.apple_collection_id))
    .filter((album) => !sourceFilter || sourceFilter.has(album.candidate_identity_key))
    .map((album) => ({
      job_key: `apple_tracklist:${album.candidate_identity_key}:${cleanString(album.catalog_match?.apple_collection_id)}`,
      source_ref: album.candidate_identity_key,
      apple_album_id: cleanString(album.catalog_match?.apple_collection_id),
      old_track_count: album.tracks?.length ?? 0,
      old_tracks_with_apple_id: (album.tracks ?? []).filter((track) => cleanString(track.apple_track_id)).length,
      old_tracks_missing_apple_id: (album.tracks ?? []).filter((track) => !cleanString(track.apple_track_id)).length,
      old_track_sources: countBy(album.tracks ?? [], "source"),
    }))
    .sort((a, b) => a.job_key.localeCompare(b.job_key));

  return Number.isFinite(args.limitAlbums) ? selected.slice(0, args.limitAlbums) : selected;
}

async function rebuildJobSafely(job) {
  try {
    if (args.dryRun) {
      return {
        ...job,
        status: "dry_run",
        apple_track_count: 0,
        tracks: [],
        error_message: "",
      };
    }

    const tracks = await fetchAlbumTracks(job.apple_album_id);
    if (!tracks.length) {
      return {
        ...job,
        status: "rebuilt_empty_apple_song_tracklist",
        apple_track_count: 0,
        tracks: [],
        error_message: "",
      };
    }

    return {
      ...job,
      status: "rebuilt_from_apple_song_tracklist",
      apple_track_count: tracks.length,
      tracks,
      error_message: "",
    };
  } catch (error) {
    return {
      ...job,
      status: "apple_album_tracks_request_error",
      apple_track_count: 0,
      tracks: [],
      error_message: errorMessage(error),
    };
  }
}

async function fetchAlbumTracks(albumId) {
  const tracks = [];
  let endpoint = `/v1/catalog/${encodeURIComponent(args.storefront)}/albums/${encodeURIComponent(albumId)}/tracks`;
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
  if (!title) return null;
  const appleTrackId = cleanString(item.id);
  const url = cleanString(attrs.url)
    || `https://music.apple.com/${args.storefront}/album/${appleTrackId}`;

  return {
    source: "apple_music_catalog_album_tracks",
    disc_number: numberOrEmpty(attrs.discNumber),
    track_number: numberOrEmpty(attrs.trackNumber) || index + 1,
    title,
    artist_name: cleanString(attrs.artistName),
    duration_ms: numberOrEmpty(attrs.durationInMillis),
    apple_track_id: idValue(appleTrackId),
    apple_track_url: url,
    explicitness: cleanString(attrs.contentRating),
    is_streamable: true,
  };
}

function applyOutcomesToSidecar() {
  const rebuiltOutcomes = outcomes.filter(isAppliedRebuildStatus);
  for (const outcome of rebuiltOutcomes) {
    const album = albumByKey.get(outcome.source_ref);
    if (!album) continue;

    const previousTrackCount = album.tracks?.length ?? 0;
    const previousTracksWithAppleId = (album.tracks ?? []).filter((track) => cleanString(track.apple_track_id)).length;
    const previousTracksMissingAppleId = previousTrackCount - previousTracksWithAppleId;
    const previousTrackSources = countBy(album.tracks ?? [], "source");

    album.tracks = outcome.tracks;
    album.tracklist_authority = {
      source: "apple_music_catalog_album_tracks",
      run_version: runVersion,
      storefront: args.storefront,
      apple_collection_id: idValue(outcome.apple_album_id),
      generated_at: generatedAt,
      replacement_policy: "apple_tracklist_replaces_prior_sidecar_rows_for_apple_resolved_album",
      previous_track_count: previousTrackCount,
      previous_tracks_with_apple_id: previousTracksWithAppleId,
      previous_tracks_missing_apple_id: previousTracksMissingAppleId,
      previous_track_sources: previousTrackSources,
    };
    if (!album.catalog_match) album.catalog_match = {};
    album.catalog_match.track_count = outcome.tracks.length;
  }

  sidecar.metadata = {
    ...(sidecar.metadata ?? {}),
    apple_tracklist_authority: {
      run_version: runVersion,
      generated_at: generatedAt,
      storefront: args.storefront,
      raw_apple_payloads_persisted: false,
      replacement_policy: "For albums with an accepted Apple album ID, Apple Music catalog song tracks are the sidecar track-row authority; music-video relationship entries are dropped.",
      persisted_catalog_fields: [
        "apple_track_id",
        "apple_track_url",
        "disc_number",
        "track_number",
        "title",
        "artist_name",
        "duration_ms",
        "explicitness",
        "is_streamable",
      ],
      excluded_persistent_fields: [
        "artwork",
        "previews",
        "lyrics",
        "raw_catalog_payload",
        "music_user_token",
      ],
    },
  };

  writeJson(sidecarJsonPath, sidecar);
  writeCsv(albumResolutionCsvPath, buildAlbumResolutionRows(albums), [
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
  writeCsv(tracksCsvPath, buildTrackRows(albums), [
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

function writeCheckpoint(status) {
  writeJson(checkpointPath, {
    run_version: runVersion,
    status,
    generated_at: new Date().toISOString(),
    completed_job_keys: [...completedJobKeys].sort(),
    outcomes,
  });
}

function writeFinalArtifacts() {
  const auditRows = [...outcomes]
    .sort((a, b) => a.job_key.localeCompare(b.job_key))
    .map((outcome) => ({
      candidate_identity_key: outcome.source_ref,
      apple_collection_id: outcome.apple_album_id,
      status: outcome.status,
      old_track_count: outcome.old_track_count,
      old_tracks_with_apple_id: outcome.old_tracks_with_apple_id,
      old_tracks_missing_apple_id: outcome.old_tracks_missing_apple_id,
      apple_track_count: outcome.apple_track_count,
      track_count_delta: (outcome.apple_track_count || 0) - (outcome.old_track_count || 0),
      old_track_sources: JSON.stringify(outcome.old_track_sources ?? {}),
      error_message: outcome.error_message ?? "",
    }));
  writeCsv(albumAuditPath, auditRows, [
    "candidate_identity_key",
    "apple_collection_id",
    "status",
    "old_track_count",
    "old_tracks_with_apple_id",
    "old_tracks_missing_apple_id",
    "apple_track_count",
    "track_count_delta",
    "old_track_sources",
    "error_message",
  ]);

  const trackRows = buildTrackRows(albums);
  const summary = {
    run_version: runVersion,
    status: "complete",
    generated_at: generatedAt,
    storefront: args.storefront,
    dry_run: args.dryRun,
    policy: {
      raw_apple_payloads_persisted: false,
      apple_catalog_requests: args.dryRun ? "none_dry_run" : "album_tracks_sparse_transient_only",
      replacement_policy: "Apple Music catalog song tracks replace prior sidecar track rows for albums with accepted Apple album IDs; music-video relationship entries are dropped.",
      persisted_catalog_fields: [
        "apple_track_id",
        "apple_track_url",
        "disc_number",
        "track_number",
        "title",
        "artist_name",
        "duration_ms",
        "explicitness",
        "is_streamable",
      ],
      excluded_persistent_fields: [
        "artwork",
        "previews",
        "lyrics",
        "raw_catalog_payload",
        "music_user_token",
      ],
    },
    counts: {
      album_jobs: jobs.length,
      albums_rebuilt_from_apple_tracklists: auditRows.filter((row) => isAppliedRebuildStatus(row)).length,
      albums_rebuilt_with_zero_song_tracks: auditRows.filter((row) => row.status === "rebuilt_empty_apple_song_tracklist").length,
      albums_not_rebuilt_by_reason: countBy(auditRows.filter((row) => !isAppliedRebuildStatus(row)), "status"),
      previous_track_rows_in_scope: sum(auditRows, "old_track_count"),
      previous_missing_track_ids_in_scope: sum(auditRows, "old_tracks_missing_apple_id"),
      apple_track_rows_written_in_scope: sum(auditRows.filter(isAppliedRebuildStatus), "apple_track_count"),
      sidecar_albums_total: albums.length,
      sidecar_albums_with_apple_collection_id: albums.filter((album) => cleanString(album.catalog_match?.apple_collection_id)).length,
      sidecar_albums_without_apple_collection_id: albums.filter((album) => !cleanString(album.catalog_match?.apple_collection_id)).length,
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
  };

  writeJson(summaryPath, summary);
  fs.writeFileSync(manifestPath, buildManifest(summary));
  console.log(JSON.stringify(summary.counts, null, 2));
}

function buildManifest(summary) {
  return `# Apple Music Sidecar Tracklist Authority Pass v1

Generated: ${summary.generated_at}

Status: \`${summary.status}\`

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
| Album jobs | ${summary.counts.album_jobs} |
| Albums rebuilt from Apple tracklists | ${summary.counts.albums_rebuilt_from_apple_tracklists} |
| Albums rebuilt with zero Apple song tracks | ${summary.counts.albums_rebuilt_with_zero_song_tracks} |
| Previous track rows in Apple-album scope | ${summary.counts.previous_track_rows_in_scope} |
| Previous missing track IDs in Apple-album scope | ${summary.counts.previous_missing_track_ids_in_scope} |
| Apple track rows written in scope | ${summary.counts.apple_track_rows_written_in_scope} |
| Sidecar albums total | ${summary.counts.sidecar_albums_total} |
| Sidecar albums with Apple album ID | ${summary.counts.sidecar_albums_with_apple_collection_id} |
| Sidecar albums without Apple album ID | ${summary.counts.sidecar_albums_without_apple_collection_id} |
| Sidecar track rows total | ${summary.counts.sidecar_track_rows_total} |
| Sidecar track rows with Apple track ID | ${summary.counts.sidecar_track_rows_with_apple_track_id} |
| Sidecar track rows missing Apple track ID | ${summary.counts.sidecar_track_rows_missing_apple_track_id} |
| Missing track IDs on Apple-resolved albums | ${summary.counts.missing_track_ids_on_apple_resolved_albums} |
| Missing track IDs on albums without Apple ID | ${summary.counts.missing_track_ids_on_albums_without_apple_id} |
`;
}

function isAppliedRebuildStatus(outcome) {
  return [
    "rebuilt_from_apple_song_tracklist",
    "rebuilt_empty_apple_song_tracklist",
  ].includes(outcome.status);
}

async function runPool(items, concurrency, worker) {
  let nextIndex = 0;
  const workers = Array.from({ length: Math.min(concurrency, items.length) }, async () => {
    while (nextIndex < items.length) {
      const item = items[nextIndex];
      nextIndex += 1;
      await worker(item);
    }
  });
  await Promise.all(workers);
}

function countBy(rows, field) {
  const counts = {};
  for (const row of rows) {
    const key = cleanString(row[field]) || "(blank)";
    counts[key] = (counts[key] ?? 0) + 1;
  }
  return counts;
}

function sum(rows, field) {
  return rows.reduce((total, row) => total + (Number(row[field]) || 0), 0);
}

function idValue(value) {
  const text = cleanString(value);
  const numeric = Number(text);
  if (/^\d+$/u.test(text) && Number.isSafeInteger(numeric)) return numeric;
  return text;
}

function numberOrEmpty(value) {
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric : "";
}

function cleanString(value) {
  if (value === undefined || value === null) return "";
  return String(value).trim();
}

function errorMessage(error) {
  if (error instanceof Error) return error.message;
  return String(error);
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function safeReadJson(file) {
  if (!fs.existsSync(file)) return null;
  return readJson(file);
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
