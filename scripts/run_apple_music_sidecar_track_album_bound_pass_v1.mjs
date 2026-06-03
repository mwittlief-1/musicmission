#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { createAppleMusicCatalogClient } from "./lib/appleMusicCatalogClient.mjs";

const repoRoot = process.cwd();
const currentRoot = path.join(repoRoot, "data/canonical_graph/current");
const outputRoot = path.join(currentRoot, "apple_music_sidecar_track_album_bound_pass_v1");
const runVersion = "apple_music_sidecar_track_album_bound_pass_v1";

const args = parseArgs(process.argv.slice(2));
const client = createAppleMusicCatalogClient({
  storefront: args.storefront,
  maxRetries: args.maxRetries,
  retryBaseDelayMs: 1000,
  retryMaxDelayMs: 60000,
  timeoutMs: 60000,
});

fs.mkdirSync(outputRoot, { recursive: true });

const linksPath = path.join(outputRoot, "apple_music_sidecar_track_album_bound_links_v1.jsonl");
const deferredPath = path.join(outputRoot, "apple_music_sidecar_track_album_bound_deferred_queue.csv");
const summaryPath = path.join(outputRoot, "apple_music_sidecar_track_album_bound_summary.json");
const manifestPath = path.join(outputRoot, "apple_music_sidecar_track_album_bound_manifest.md");
const checkpointPath = path.join(outputRoot, "apple_music_sidecar_track_album_bound_pass_v1.checkpoint.json");

const sidecarTrackRows = readCsv(path.join(currentRoot, "album_track_sidecar_tracks.csv"));
const existingLinks = linkInputSpecs().flatMap((relativePath) => safeReadJsonl(path.join(currentRoot, relativePath)));
const existingTrackLinks = new Set(
  existingLinks
    .filter((link) => link.source_type === "album_sidecar_track")
    .filter((link) => link.apple_resource_type === "song")
    .filter(isAcceptedLink)
    .map((link) => link.source_ref),
);

const checkpoint = args.resume ? safeReadJson(checkpointPath) : null;
const completedAlbumKeys = new Set(checkpoint?.completed_album_keys ?? []);
const links = checkpoint?.links ?? [];
const deferred = checkpoint?.deferred ?? [];
const linkKeys = new Set(links.map((link) => link.link_key));
const deferredKeys = new Set(deferred.map((row) => row.deferred_key));

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
  jobs.filter((job) => !completedAlbumKeys.has(job.job_key)),
  args.concurrency,
  async (job) => {
    const outcome = await resolveJobSafely(job);
    for (const link of outcome.links) addLink(link);
    for (const row of outcome.deferred) addDeferred(row);
    completedAlbumKeys.add(job.job_key);
    completed += 1;
    if (completed % args.checkpointEvery === 0) writeCheckpoint("partial");
    if (completed % args.progressEvery === 0 || completed === jobs.length) {
      console.error(`sidecar track album-bound pass: completed ${completed}/${jobs.length}, links=${links.length}, deferred=${deferred.length}`);
    }
  },
);

writeCheckpoint("complete");
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

function linkInputSpecs() {
  return [
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
  ];
}

function buildJobs() {
  const sourceFilter = args.sourceRefs.length ? new Set(args.sourceRefs) : null;
  const rowsByAlbum = groupBy(
    sidecarTrackRows.filter((row) => {
      if (!row.apple_collection_id || row.apple_track_id) return false;
      const sourceRef = sidecarTrackSourceRef(row);
      if (existingTrackLinks.has(sourceRef)) return false;
      return !sourceFilter || sourceFilter.has(row.candidate_identity_key);
    }),
    (row) => row.candidate_identity_key,
  );
  const jobs = [...rowsByAlbum.entries()]
    .map(([albumRef, rows]) => ({
      job_key: `album_bound_tracks:${albumRef}:${rows[0]?.apple_collection_id ?? ""}`,
      source_ref: albumRef,
      apple_album_id: rows[0]?.apple_collection_id ?? "",
      rows: rows.sort(compareSidecarTrackRows),
      all_album_rows: sidecarTrackRows
        .filter((row) => row.candidate_identity_key === albumRef)
        .sort(compareSidecarTrackRows),
    }))
    .filter((job) => job.apple_album_id)
    .sort((a, b) => a.job_key.localeCompare(b.job_key));

  return Number.isFinite(args.limitAlbums) ? jobs.slice(0, args.limitAlbums) : jobs;
}

async function resolveJobSafely(job) {
  try {
    if (args.dryRun) {
      return {
        links: [],
        deferred: job.rows.map((row) => makeDeferred(row, job, "dry_run_no_catalog_call", { candidate_count: 0, best_score: 0 })),
      };
    }
    const appleTracks = await fetchAlbumTracks(job.apple_album_id);
    return resolveAlbumTracks(job, appleTracks);
  } catch (error) {
    return {
      links: [],
      deferred: job.rows.map((row) => makeDeferred(row, job, "apple_album_tracks_request_error", {
        candidate_count: 0,
        best_score: 0,
        error_message: errorMessage(error),
      })),
    };
  }
}

async function fetchAlbumTracks(albumId) {
  const tracks = [];
  let endpoint = `/v1/catalog/${encodeURIComponent(args.storefront)}/albums/${encodeURIComponent(albumId)}/tracks`;
  let query = {
    limit: 300,
    "fields[songs]": "name,artistName,durationInMillis,discNumber,trackNumber,url",
  };
  let guard = 0;

  while (endpoint && guard < 10) {
    const payload = await client.catalogGet(endpoint, query);
    for (const item of payload?.data ?? []) {
      if (item.type === "songs" && item.id) tracks.push(item);
    }
    endpoint = payload?.next ?? "";
    query = {};
    guard += 1;
  }

  return tracks;
}

function resolveAlbumTracks(job, appleItems) {
  const usableTracks = appleItems.map((item, index) => normalizeAppleTrack(item, index)).filter(Boolean);
  const usedAppleIds = new Set(
    job.all_album_rows
      .map((row) => row.apple_track_id)
      .filter(Boolean)
      .map(String),
  );
  const links = [];
  const deferred = [];

  for (const row of job.rows) {
    const scored = usableTracks
      .filter((track) => !usedAppleIds.has(track.apple_catalog_id))
      .map((track) => scoreTrackCandidate(row, track))
      .sort((a, b) => b.score - a.score);
    const best = scored[0];
    const second = scored[1];

    if (best && isTrackAutoAccept(best, second)) {
      usedAppleIds.add(best.track.apple_catalog_id);
      links.push(makeLink(row, job, best));
    } else {
      deferred.push(makeDeferred(row, job, "album_bound_track_no_safe_match", {
        candidate_count: scored.length,
        best_score: best?.score ?? 0,
        second_score: second?.score ?? "",
      }));
    }
  }

  return { links, deferred };
}

function normalizeAppleTrack(item, albumTrackIndex) {
  const attrs = item.attributes ?? {};
  if (!item.id || !attrs.name) return null;
  return {
    apple_catalog_id: String(item.id),
    album_track_index: albumTrackIndex,
    title_norm: normalize(attrs.name),
    title_core: normalizeTitleCore(attrs.name),
    title_loose: normalizeTitleLoose(attrs.name),
    artist_norm: normalize(attrs.artistName),
    disc_number: numberOrNull(attrs.discNumber),
    track_number: numberOrNull(attrs.trackNumber),
    duration_ms: numberOrNull(attrs.durationInMillis),
  };
}

function scoreTrackCandidate(row, track) {
  const expectedTitle = normalize(row.track_title);
  const expectedTitleCore = normalizeTitleCore(row.track_title);
  const expectedTitleLoose = normalizeTitleLoose(row.track_title);
  const expectedArtist = normalize(row.track_artist_name || row.artist_display_name);
  const expectedDisc = numberOrNull(row.disc_number);
  const expectedTrack = numberOrNull(row.track_number);
  const expectedDuration = numberOrNull(row.duration_ms);
  const positionExact = expectedDisc === track.disc_number && expectedTrack === track.track_number;
  const titleExact = expectedTitle && expectedTitle === track.title_norm;
  const titleCoreExact = expectedTitleCore && expectedTitleCore === track.title_core;
  const titleLooseExact = expectedTitleLoose && expectedTitleLoose === track.title_loose;
  const titleCompatible = Boolean(
    titleExact
    || titleCoreExact
    || titleLooseExact
    || containsUseful(track.title_core, expectedTitleCore)
    || containsUseful(expectedTitleCore, track.title_core),
  );
  const artistCompatible = !expectedArtist || compatibleNames(track.artist_norm, expectedArtist);
  const durationDelta = expectedDuration !== null && track.duration_ms !== null
    ? Math.abs(expectedDuration - track.duration_ms)
    : null;

  let score = 0;
  if (positionExact) score += 36;
  if (titleExact) score += 44;
  else if (titleCoreExact) score += 40;
  else if (titleLooseExact) score += 36;
  else if (titleCompatible) score += 24;
  if (artistCompatible) score += 12;
  if (durationDelta !== null && durationDelta <= 5000) score += 14;
  else if (durationDelta !== null && durationDelta <= 15000) score += 10;
  else if (durationDelta !== null && durationDelta <= 30000) score += 5;
  score -= Math.min(track.album_track_index, 5);

  const basis = [];
  if (positionExact) basis.push("position");
  if (titleExact) basis.push("title");
  else if (titleCoreExact) basis.push("title_core");
  else if (titleLooseExact) basis.push("title_loose");
  else if (titleCompatible) basis.push("title_compatible");
  if (artistCompatible) basis.push("artist");
  if (durationDelta !== null && durationDelta <= 15000) basis.push("duration");

  return {
    track,
    score,
    positionExact,
    titleExact,
    titleCoreExact,
    titleLooseExact,
    titleCompatible,
    artistCompatible,
    duration_delta_ms: durationDelta ?? "",
    title_match: titleExact ? "exact_normalized" : titleCoreExact ? "core_exact_normalized" : titleLooseExact ? "loose_exact_normalized" : titleCompatible ? "compatible_normalized" : "not_matched",
    artist_match: artistCompatible ? "compatible_normalized" : "not_matched",
    match_basis: `album_bound_sidecar_track_${basis.join("_")}_auto_match`,
    confidence: score >= 92 && (titleExact || titleCoreExact || titleLooseExact) ? "high" : "medium",
    warnings: durationDelta !== null && durationDelta > 30000 ? "duration_differs" : "",
  };
}

function isTrackAutoAccept(best, second) {
  if (best.positionExact && (best.titleExact || best.titleCoreExact || best.titleLooseExact)) return true;
  if (best.positionExact && best.titleCompatible && best.duration_delta_ms !== "" && best.duration_delta_ms <= 15000) return true;
  if ((best.titleExact || best.titleCoreExact || best.titleLooseExact) && best.duration_delta_ms !== "" && best.duration_delta_ms <= 15000 && (!second || best.score - second.score >= 10)) return true;
  if ((best.titleExact || best.titleCoreExact || best.titleLooseExact) && best.duration_delta_ms !== "" && best.duration_delta_ms <= 30000 && best.score >= 45 && (!second || best.score - second.score >= 14)) return true;
  if ((best.titleExact || best.titleCoreExact || best.titleLooseExact) && best.artistCompatible && best.score >= 76 && (!second || best.score - second.score >= 10)) return true;
  if (best.score >= 88 && (!second || best.score - second.score >= 10) && (best.positionExact || best.artistCompatible)) return true;
  return false;
}

function makeLink(row, job, match) {
  const sourceRef = sidecarTrackSourceRef(row);
  const appleId = match.track.apple_catalog_id;
  return {
    link_key: `album_sidecar_track:${sourceRef}:apple_music:song:${appleId}:${args.storefront}`,
    run_version: runVersion,
    source_ref: sourceRef,
    source_type: "album_sidecar_track",
    source_candidate_type: "track",
    external_catalog: "apple_music",
    apple_catalog_id: appleId,
    apple_resource_type: "song",
    storefront: args.storefront,
    match_status: match.confidence === "high" ? "verified" : "candidate_verified",
    match_basis: match.match_basis,
    confidence: match.confidence,
    result_rank: match.track.album_track_index + 1,
    title_match: match.title_match,
    artist_match: match.artist_match,
    year_delta: "",
    warnings: match.warnings,
    apple_album_id: job.apple_album_id,
    album_match_basis: "album_bound_existing_sidecar_apple_album_id",
    track_score: match.score,
    duration_delta_ms: match.duration_delta_ms,
    verified_at: new Date().toISOString(),
    raw_payload_persisted: false,
  };
}

function makeDeferred(row, job, reason, extra = {}) {
  const sourceRef = sidecarTrackSourceRef(row);
  return {
    deferred_key: `album_sidecar_track:${sourceRef}:${reason}:${job.apple_album_id}`,
    run_version: runVersion,
    source_ref: sourceRef,
    source_type: "album_sidecar_track",
    source_candidate_type: "track",
    artist_display_name: row.track_artist_name || row.artist_display_name || "",
    title: row.track_title,
    year: row.album_year,
    storefront: args.storefront,
    deferred_reason: reason,
    candidate_count: extra.candidate_count ?? "",
    best_score: extra.best_score ?? "",
    second_score: extra.second_score ?? "",
    apple_album_id: job.apple_album_id,
    error_message: extra.error_message ?? "",
    raw_payload_persisted: false,
  };
}

function addLink(link) {
  if (linkKeys.has(link.link_key)) return;
  links.push(link);
  linkKeys.add(link.link_key);
}

function addDeferred(row) {
  if (deferredKeys.has(row.deferred_key)) return;
  deferred.push(row);
  deferredKeys.add(row.deferred_key);
}

function writeCheckpoint(status) {
  writeJson(checkpointPath, {
    run_version: runVersion,
    status,
    generated_at: new Date().toISOString(),
    completed_album_keys: [...completedAlbumKeys].sort(),
    links,
    deferred,
  });
}

function writeFinalArtifacts() {
  const sortedLinks = links.sort((a, b) => a.link_key.localeCompare(b.link_key));
  const sortedDeferred = deferred.sort((a, b) => a.deferred_key.localeCompare(b.deferred_key));
  fs.writeFileSync(linksPath, sortedLinks.map((link) => JSON.stringify(link)).join("\n") + (sortedLinks.length ? "\n" : ""));
  writeCsv(deferredPath, sortedDeferred, [
    "deferred_key",
    "run_version",
    "source_ref",
    "source_type",
    "source_candidate_type",
    "artist_display_name",
    "title",
    "year",
    "storefront",
    "deferred_reason",
    "candidate_count",
    "best_score",
    "second_score",
    "apple_album_id",
    "error_message",
    "raw_payload_persisted",
  ]);

  const summary = {
    run_version: runVersion,
    status: "complete",
    generated_at: new Date().toISOString(),
    storefront: args.storefront,
    policy: {
      raw_apple_payloads_persisted: false,
      apple_catalog_requests: args.dryRun ? "none_dry_run" : "album_tracks_sparse_transient_only",
      persisted_catalog_fields: ["apple_catalog_id", "apple_resource_type", "storefront", "match metadata"],
      excluded_persistent_fields: ["artwork", "previews", "lyrics", "raw_catalog_payload", "music_user_token", "apple_track_title", "apple_track_artist", "apple_album_name"],
    },
    counts: {
      album_jobs: jobs.length,
      track_rows_missing_ids_in_scope: jobs.reduce((sum, job) => sum + job.rows.length, 0),
      links_total: sortedLinks.length,
      deferred_total: sortedDeferred.length,
      links_by_confidence: countBy(sortedLinks, "confidence"),
      deferred_by_reason: countBy(sortedDeferred, "deferred_reason"),
    },
  };
  writeJson(summaryPath, summary);
  fs.writeFileSync(manifestPath, buildManifest(summary));
  console.log(JSON.stringify(summary.counts, null, 2));
}

function buildManifest(summary) {
  return `# Apple Music Sidecar Track Album-Bound Pass v1

Generated: ${summary.generated_at}

Status: \`${summary.status}\`

## Policy

- Raw Apple payloads persisted: \`false\`
- Apple requests are limited to sparse track lists for sidecar albums that already have an Apple album ID.
- Output persists Apple song IDs and match evidence only; fetched Apple track titles/artists/album names are not written.

## Counts

| Metric | Count |
| --- | ---: |
| Album jobs | ${summary.counts.album_jobs} |
| Missing sidecar track rows in scope | ${summary.counts.track_rows_missing_ids_in_scope} |
| Track links accepted | ${summary.counts.links_total} |
| Deferred rows | ${summary.counts.deferred_total} |

## Deferred By Reason

${tableFromCounts(summary.counts.deferred_by_reason)}
`;
}

function sidecarTrackSourceRef(row) {
  return [
    row.candidate_identity_key,
    row.disc_number || "",
    row.track_number || "",
    normalizeLegacySourceRefSegment(row.track_artist_name),
    normalizeLegacySourceRefSegment(row.track_title),
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

function normalize(value) {
  return normalizeComparableSegment(value);
}

function normalizeComparableSegment(value) {
  return normalizeLegacySourceRefSegment(value)
    .replace(/\bf k\b/gu, "fuck")
    .replace(/\bf u c k\b/gu, "fuck")
    .replace(/\bn z\b/gu, "niggaz")
    .replace(/\bn a\b/gu, "nigga")
    .replace(/\s+/g, " ")
    .trim();
}

function normalizeTitleCore(value) {
  return normalize(value)
    .replace(/\b(remaster(ed)?|mono|stereo|single|album|version|edit|deluxe|expanded|anniversary|bonus|tracks?|explicit|clean|edition|reissue|original|collector|complete|legacy|motion|picture|score|soundtrack|recording|cast|broadway|live|with|vol|volume|mix|master)\b/gu, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function normalizeTitleLoose(value) {
  return normalize(
    String(value ?? "")
      .replace(/\[[^\]]*\]/gu, " ")
      .replace(/\([^)]*\)/gu, " ")
      .replace(/\bfeat(?:uring)?\b.*$/giu, " ")
      .replace(/\bwith\b.*$/giu, " "),
  )
    .replace(/\b(remaster(ed)?|mono|stereo|lp|single|album|version|edit|deluxe|expanded|anniversary|bonus|tracks?|explicit|clean|edition|reissue|original|collector|complete|legacy|motion|picture|score|soundtrack|recording|cast|broadway|live|vol|volume|mix|master)\b/gu, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function containsUseful(left, right) {
  if (!left || !right) return false;
  if (right.length < 5 || left.length < 5) return false;
  return left.includes(right) || right.includes(left);
}

function compatibleNames(left, right) {
  if (!left || !right) return false;
  return left === right || left.includes(right) || right.includes(left);
}

function compareSidecarTrackRows(a, b) {
  return (Number(a.disc_number) || 0) - (Number(b.disc_number) || 0)
    || (Number(a.track_number) || 0) - (Number(b.track_number) || 0)
    || (Number(a.sidecar_track_index) || 0) - (Number(b.sidecar_track_index) || 0);
}

function numberOrNull(value) {
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function isAcceptedLink(link) {
  return ["verified", "candidate_verified"].includes(link.match_status);
}

async function runPool(items, concurrency, worker) {
  let index = 0;
  const runners = Array.from({ length: Math.min(concurrency, items.length) }, async () => {
    while (index < items.length) {
      const currentIndex = index;
      index += 1;
      await worker(items[currentIndex], currentIndex);
    }
  });
  await Promise.all(runners);
}

function groupBy(values, keyFn) {
  const map = new Map();
  for (const value of values) {
    const key = keyFn(value);
    if (!map.has(key)) map.set(key, []);
    map.get(key).push(value);
  }
  return map;
}

function countBy(values, key) {
  const counts = {};
  for (const value of values) {
    const item = value[key] || "";
    counts[item] = (counts[item] ?? 0) + 1;
  }
  return counts;
}

function tableFromCounts(counts) {
  const entries = Object.entries(counts).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
  if (!entries.length) return "_None._";
  return ["| Value | Count |", "| --- | ---: |", ...entries.map(([key, count]) => `| \`${key || "(blank)"}\` | ${count} |`)].join("\n");
}

function readCsv(file) {
  if (!fs.existsSync(file)) return [];
  const text = fs.readFileSync(file, "utf8").trim();
  if (!text) return [];
  const [headerLine, ...lines] = splitCsvLines(text);
  const headers = parseCsvLine(headerLine);
  return lines.map((line) => {
    const values = parseCsvLine(line);
    return Object.fromEntries(headers.map((header, index) => [header, values[index] ?? ""]));
  });
}

function writeCsv(file, rows, headers) {
  const lines = [headers.join(",")];
  for (const row of rows) {
    lines.push(headers.map((header) => csvCell(row[header] ?? "")).join(","));
  }
  fs.writeFileSync(file, `${lines.join("\n")}\n`);
}

function splitCsvLines(text) {
  const lines = [];
  let current = "";
  let inQuotes = false;
  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];
    const next = text[index + 1];
    if (char === "\"" && inQuotes && next === "\"") {
      current += "\"";
      index += 1;
    } else if (char === "\"") {
      inQuotes = !inQuotes;
      current += char;
    } else if (char === "\n" && !inQuotes) {
      lines.push(current.replace(/\r$/u, ""));
      current = "";
    } else {
      current += char;
    }
  }
  if (current) lines.push(current.replace(/\r$/u, ""));
  return lines;
}

function parseCsvLine(line) {
  const values = [];
  let current = "";
  let inQuotes = false;
  for (let index = 0; index < line.length; index += 1) {
    const char = line[index];
    const next = line[index + 1];
    if (char === "\"" && inQuotes && next === "\"") {
      current += "\"";
      index += 1;
    } else if (char === "\"") {
      inQuotes = !inQuotes;
    } else if (char === "," && !inQuotes) {
      values.push(current);
      current = "";
    } else {
      current += char;
    }
  }
  values.push(current);
  return values;
}

function csvCell(value) {
  const text = String(value ?? "");
  if (/[",\n\r]/u.test(text)) return `"${text.replace(/"/g, "\"\"")}"`;
  return text;
}

function safeReadJson(file) {
  if (!fs.existsSync(file)) return null;
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

function errorMessage(error) {
  return error instanceof Error ? error.message : String(error);
}
