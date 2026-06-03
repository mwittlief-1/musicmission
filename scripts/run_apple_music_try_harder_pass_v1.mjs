#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { createAppleMusicCatalogClient } from "./lib/appleMusicCatalogClient.mjs";

const repoRoot = process.cwd();
const currentRoot = path.join(repoRoot, "data/canonical_graph/current");
const priorPassRoot = path.join(currentRoot, "apple_music_link_pass_v1");
const outputRoot = path.join(currentRoot, "apple_music_try_harder_pass_v1");
const runVersion = "apple_music_try_harder_pass_v1";

const args = parseArgs(process.argv.slice(2));
const client = createAppleMusicCatalogClient({
  storefront: args.storefront,
  maxRetries: 8,
  retryBaseDelayMs: 1000,
  retryMaxDelayMs: 60000,
});

fs.mkdirSync(outputRoot, { recursive: true });

const linksPath = path.join(outputRoot, "apple_music_try_harder_links_v1.jsonl");
const deferredPath = path.join(outputRoot, "apple_music_try_harder_deferred_queue.csv");
const summaryPath = path.join(outputRoot, "apple_music_try_harder_summary.json");
const manifestPath = path.join(outputRoot, "apple_music_try_harder_manifest.md");
const checkpointPath = path.join(outputRoot, "apple_music_try_harder_pass_v1.checkpoint.json");

const sidecarTracks = readCsv(path.join(currentRoot, "album_track_sidecar_tracks.csv"));
const sidecarAlbums = readCsv(path.join(currentRoot, "album_track_sidecar_album_resolution.csv"));
const priorLinks = readJsonl(path.join(priorPassRoot, "apple_music_links_v1.jsonl"));
const priorReviews = readCsv(path.join(priorPassRoot, "apple_music_manual_review_queue.csv"));

const priorLinkKeys = new Set(priorLinks.map((link) => link.link_key));
const sidecarTracksByAlbum = groupBy(sidecarTracks, (row) => row.candidate_identity_key);
const sidecarAlbumsByKey = new Map(sidecarAlbums.map((row) => [row.candidate_identity_key, row]));
const priorTrackIdBySourceRef = new Map(
  priorLinks
    .filter((link) => link.source_type === "album_sidecar_track" && link.apple_resource_type === "song")
    .map((link) => [link.source_ref, link.apple_catalog_id]),
);

const checkpoint = args.resume ? readCheckpoint() : null;
const existingOutput = !checkpoint && args.mergeExistingOutput ? readExistingOutput() : null;
const completedAlbumSearchKeys = new Set(checkpoint?.completed_album_search_keys ?? []);
const completedTrackAlbumKeys = new Set(checkpoint?.completed_track_album_keys ?? []);
const links = checkpoint?.links ?? existingOutput?.links ?? [];
let deferred = checkpoint?.deferred ?? existingOutput?.deferred ?? [];
if (args.sourceRefs.length > 0) {
  const retryRefs = new Set(args.sourceRefs);
  deferred = deferred.filter((row) => !retryRefs.has(row.source_ref));
}
const linkKeys = new Set(links.map((link) => link.link_key));
const deferredKeys = new Set(deferred.map((row) => row.deferred_key));

const albumIdsBySourceRef = buildAlbumIdMap();
const albumSearchJobs = buildAlbumSearchJobs();
const trackAlbumJobs = buildTrackAlbumJobs();

console.error(JSON.stringify({
  run_version: runVersion,
  storefront: args.storefront,
  album_search_jobs: albumSearchJobs.length,
  track_album_jobs: trackAlbumJobs.length,
  dry_run: args.dryRun,
}, null, 2));

if (!args.skipAlbumSearch) {
  await runPool(albumSearchJobs.filter((job) => !completedAlbumSearchKeys.has(job.job_key)), args.concurrency, async (job, index) => {
    const outcome = await safelyTryResolveAlbumReview(job);
    recordAlbumSearchOutcome(job, outcome);
    completedAlbumSearchKeys.add(job.job_key);
    if ((index + 1) % args.checkpointEvery === 0) writeCheckpoint("partial");
    if ((index + 1) % args.progressEvery === 0) logProgress("album-search", index + 1, albumSearchJobs.length);
  });
}

const expandedTrackAlbumJobs = buildTrackAlbumJobs();
if (!args.skipTrackPass) {
  await runPool(expandedTrackAlbumJobs.filter((job) => !completedTrackAlbumKeys.has(job.job_key)), args.concurrency, async (job, index) => {
    const outcome = await safelyResolveAlbumTracks(job);
    recordAlbumTrackOutcome(job, outcome);
    completedTrackAlbumKeys.add(job.job_key);
    if ((index + 1) % args.checkpointEvery === 0) writeCheckpoint("partial");
    if ((index + 1) % args.progressEvery === 0) logProgress("track-pass", index + 1, expandedTrackAlbumJobs.length);
  });
}

if (!args.skipSidecarAlbumBridge) {
  bridgeSidecarAlbumLinksFromGraphAlbumLinks();
}

if (!args.skipGraphBridge) {
  bridgeGraphReviewsFromSidecarTracks();
}

writeCheckpoint("complete");
writeFinalArtifacts();
if (!args.keepCheckpoint && fs.existsSync(checkpointPath)) fs.unlinkSync(checkpointPath);

function parseArgs(argv) {
  const parsed = {
    storefront: "us",
    concurrency: 6,
    progressEvery: 100,
    checkpointEvery: 100,
    resume: true,
    keepCheckpoint: false,
    dryRun: false,
    skipAlbumSearch: false,
    skipTrackPass: false,
    skipSidecarAlbumBridge: false,
    skipGraphBridge: false,
    limitAlbums: Number.NaN,
    limitAlbumSearch: Number.NaN,
    mergeExistingOutput: false,
    sourceRefs: [],
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--storefront") parsed.storefront = argv[++index];
    else if (arg === "--concurrency") parsed.concurrency = Number(argv[++index]);
    else if (arg === "--progress-every") parsed.progressEvery = Number(argv[++index]);
    else if (arg === "--checkpoint-every") parsed.checkpointEvery = Number(argv[++index]);
    else if (arg === "--no-resume") parsed.resume = false;
    else if (arg === "--keep-checkpoint") parsed.keepCheckpoint = true;
    else if (arg === "--dry-run") parsed.dryRun = true;
    else if (arg === "--skip-album-search") parsed.skipAlbumSearch = true;
    else if (arg === "--skip-track-pass") parsed.skipTrackPass = true;
    else if (arg === "--skip-sidecar-album-bridge") parsed.skipSidecarAlbumBridge = true;
    else if (arg === "--skip-graph-bridge") parsed.skipGraphBridge = true;
    else if (arg === "--limit-albums") parsed.limitAlbums = Number(argv[++index]);
    else if (arg === "--limit-album-search") parsed.limitAlbumSearch = Number(argv[++index]);
    else if (arg === "--merge-existing-output") parsed.mergeExistingOutput = true;
    else if (arg === "--source-ref") parsed.sourceRefs.push(argv[++index]);
  }

  if (!Number.isFinite(parsed.concurrency) || parsed.concurrency < 1) parsed.concurrency = 1;
  if (parsed.concurrency > 12) parsed.concurrency = 12;
  if (!Number.isFinite(parsed.progressEvery) || parsed.progressEvery < 1) parsed.progressEvery = 100;
  if (!Number.isFinite(parsed.checkpointEvery) || parsed.checkpointEvery < 1) parsed.checkpointEvery = parsed.progressEvery;
  return parsed;
}

function buildAlbumIdMap() {
  const map = new Map();
  for (const link of [...priorLinks, ...links]) {
    if (link.apple_resource_type !== "album") continue;
    if (link.source_type !== "graph_album" && link.source_type !== "album_sidecar_album") continue;
    if (!map.has(link.source_ref)) {
      map.set(link.source_ref, {
        apple_catalog_id: link.apple_catalog_id,
        source_basis: `${link.source_type}:${link.match_basis}`,
      });
    }
  }
  return map;
}

function buildAlbumSearchJobs() {
  const jobs = [];
  const albumReviews = priorReviews
    .filter((review) => review.source_type === "graph_album")
    .filter((review) => !albumIdsBySourceRef.has(review.source_ref));
  for (const review of albumReviews) {
    const sidecarRows = sidecarTracksByAlbum.get(review.source_ref) ?? [];
    jobs.push({
      job_key: `album_search:${review.source_ref}`,
      source_ref: review.source_ref,
      source_type: "graph_album",
      source_candidate_type: "album",
      artist_display_name: review.artist_display_name,
      title: review.title,
      year: review.year,
      sidecar_track_count: sidecarRows.length,
      sidecar_tracks: sidecarRows,
    });
  }
  const sorted = jobs.sort((a, b) => a.job_key.localeCompare(b.job_key));
  const filtered = filterJobsBySourceRef(sorted);
  return Number.isFinite(args.limitAlbumSearch) ? filtered.slice(0, args.limitAlbumSearch) : filtered;
}

function buildTrackAlbumJobs() {
  const jobs = [];
  for (const [sourceRef, albumLink] of albumIdsBySourceRef.entries()) {
    const tracks = sidecarTracksByAlbum.get(sourceRef) ?? [];
    if (!tracks.some((row) => !existingTrackIdForRow(row))) continue;
    jobs.push({
      job_key: `album_tracks:${sourceRef}:${albumLink.apple_catalog_id}`,
      source_ref: sourceRef,
      apple_album_id: albumLink.apple_catalog_id,
      album_link_basis: albumLink.source_basis,
      tracks,
    });
  }
  const sorted = jobs.sort((a, b) => a.job_key.localeCompare(b.job_key));
  const filtered = filterJobsBySourceRef(sorted);
  return Number.isFinite(args.limitAlbums) ? filtered.slice(0, args.limitAlbums) : filtered;
}

function filterJobsBySourceRef(jobs) {
  if (!args.sourceRefs.length) return jobs;
  const refs = new Set(args.sourceRefs);
  return jobs.filter((job) => refs.has(job.source_ref));
}

async function safelyTryResolveAlbumReview(job) {
  try {
    if (args.dryRun) return { kind: "deferred", reason: "dry_run_no_catalog_call" };
    return await tryResolveAlbumReview(job);
  } catch (error) {
    return { kind: "deferred", reason: "apple_album_try_harder_request_error", error_message: errorMessage(error) };
  }
}

async function tryResolveAlbumReview(job) {
  const searchTerms = uniqueValues([
    `${job.artist_display_name} ${job.title}`.trim(),
    `${stripFeaturing(job.artist_display_name)} ${job.title}`.trim(),
    `${job.title} ${job.artist_display_name}`.trim(),
  ]);
  const candidates = [];

  for (const term of searchTerms) {
    const payload = await client.catalogGet(`/v1/catalog/${encodeURIComponent(args.storefront)}/search`, {
      term,
      types: "albums",
      limit: 10,
      "fields[albums]": "name,artistName,releaseDate",
    });
    for (const [index, item] of (payload?.results?.albums?.data ?? []).entries()) {
      if (candidates.some((candidate) => candidate.item.id === item.id)) continue;
      const albumTracks = await fetchAlbumTracks(item.id);
      candidates.push(scoreAlbumCandidate(item, albumTracks, job, index + 1));
    }
  }

  candidates.sort((a, b) => b.score - a.score);
  const accepted = candidates.find((candidate) => (
    candidate.score >= 118
    && candidate.titleCompatible
    && (candidate.artistCompatible || candidate.trackOverlapRatio >= 0.7)
    && candidate.trackOverlapRatio >= 0.6
  )) ?? candidates.find((candidate) => (
    candidate.score >= 105
    && candidate.titleExact
    && candidate.artistCompatible
    && candidate.trackOverlapRatio >= 0.45
  ));

  if (!accepted) {
    return {
      kind: "deferred",
      reason: "album_try_harder_no_safe_tracklist_match",
      candidate_count: candidates.length,
      best_score: candidates[0]?.score ?? 0,
    };
  }

  albumIdsBySourceRef.set(job.source_ref, {
    apple_catalog_id: accepted.item.id,
    source_basis: "graph_album:album_try_harder_search_tracklist_auto_match",
  });

  return {
    kind: "link",
    apple_catalog_id: accepted.item.id,
    apple_resource_type: "album",
    match_status: accepted.trackOverlapRatio >= 0.7 ? "verified" : "candidate_verified",
    match_basis: "album_try_harder_search_tracklist_auto_match",
    confidence: accepted.trackOverlapRatio >= 0.7 ? "high" : "medium",
    result_rank: accepted.searchRank,
    title_match: accepted.titleExact ? "exact_normalized" : "compatible_normalized",
    artist_match: accepted.artistCompatible ? "compatible_normalized" : "tracklist_supported",
    year_delta: accepted.yearDelta,
    warnings: accepted.yearDelta > 3 ? "release_year_differs_tracklist_matched" : "",
    track_overlap_ratio: accepted.trackOverlapRatio.toFixed(3),
    track_overlap_count: accepted.trackOverlapCount,
    candidate_count: candidates.length,
  };
}

async function safelyResolveAlbumTracks(job) {
  try {
    if (args.dryRun) return { kind: "album_tracks", links: [], deferred: [] };
    const appleTracks = await fetchAlbumTracks(job.apple_album_id);
    return resolveAlbumTracks(job, appleTracks);
  } catch (error) {
    return {
      kind: "album_tracks",
      links: [],
      deferred: [{
        source_ref: job.source_ref,
        source_type: "album_sidecar_album",
        source_candidate_type: "album",
        reason: "apple_album_tracks_request_error",
        error_message: errorMessage(error),
      }],
    };
  }
}

async function fetchAlbumTracks(albumId) {
  const allTracks = [];
  let endpoint = `/v1/catalog/${encodeURIComponent(args.storefront)}/albums/${encodeURIComponent(albumId)}/tracks`;
  let query = {
    limit: 300,
    "fields[songs]": "name,artistName,durationInMillis,discNumber,trackNumber",
  };
  let guard = 0;

  while (endpoint && guard < 10) {
    const payload = await client.catalogGet(endpoint, query);
    for (const item of payload?.data ?? []) {
      if (item.type === "songs" && item.id) allTracks.push(item);
    }
    endpoint = payload?.next ?? "";
    query = {};
    guard += 1;
  }

  return allTracks;
}

function resolveAlbumTracks(job, appleTracks) {
  const matchedLinks = [];
  const deferredRows = [];
  const usableTracks = appleTracks
    .map((item, index) => normalizeAppleTrack(item, index))
    .filter(Boolean);
  const usedAppleIds = new Set(job.tracks.map(existingTrackIdForRow).filter(Boolean));
  const missingRows = job.tracks
    .filter((row) => !existingTrackIdForRow(row))
    .sort(compareSidecarTrackRows);

  for (const row of missingRows) {
    const sourceRef = sidecarTrackSourceRef(row);
    const scored = usableTracks
      .filter((track) => !usedAppleIds.has(track.apple_catalog_id))
      .map((track) => scoreTrackCandidate(row, track))
      .sort((a, b) => b.score - a.score);
    const best = scored[0];
    const second = scored[1];
    const accepted = best && isTrackAutoAccept(best, second);

    if (accepted) {
      usedAppleIds.add(best.track.apple_catalog_id);
      matchedLinks.push(makeLink({
        source_ref: sourceRef,
        source_type: "album_sidecar_track",
        source_candidate_type: "track",
        apple_catalog_id: best.track.apple_catalog_id,
        apple_resource_type: "song",
        match_status: best.confidence === "high" ? "verified" : "candidate_verified",
        match_basis: best.match_basis,
        confidence: best.confidence,
        result_rank: best.track.album_track_index + 1,
        title_match: best.title_match,
        artist_match: best.artist_match,
        year_delta: "",
        warnings: best.warnings,
        apple_album_id: job.apple_album_id,
        album_match_basis: job.album_link_basis,
        track_score: best.score,
        duration_delta_ms: best.duration_delta_ms,
      }));
    } else {
      deferredRows.push({
        source_ref: sourceRef,
        source_type: "album_sidecar_track",
        source_candidate_type: "track",
        artist_display_name: row.track_artist_name,
        title: row.track_title,
        year: row.album_year,
        reason: "album_track_try_harder_no_safe_match",
        candidate_count: scored.length,
        best_score: best?.score ?? 0,
        apple_album_id: job.apple_album_id,
        error_message: "",
      });
    }
  }

  return { kind: "album_tracks", links: matchedLinks, deferred: deferredRows };
}

function scoreAlbumCandidate(item, albumTracks, job, searchRank) {
  const attrs = item.attributes ?? {};
  const expectedTitle = normalize(job.title);
  const expectedTitleCore = normalizeTitleCore(job.title);
  const expectedArtist = normalize(job.artist_display_name);
  const candidateTitle = normalize(attrs.name);
  const candidateTitleCore = normalizeTitleCore(attrs.name);
  const candidateArtist = normalize(attrs.artistName);
  const expectedYear = Number(job.year);
  const candidateYear = Number(String(attrs.releaseDate ?? "").slice(0, 4));
  const yearDelta = Number.isFinite(expectedYear) && Number.isFinite(candidateYear)
    ? Math.abs(expectedYear - candidateYear)
    : 99;
  const titleExact = candidateTitle === expectedTitle;
  const titleCompatible = titleExact
    || candidateTitleCore === expectedTitleCore
    || containsUseful(candidateTitleCore, expectedTitleCore);
  const artistCompatible = compatibleNames(candidateArtist, expectedArtist);
  const overlap = tracklistOverlap(job.sidecar_tracks, albumTracks);

  let score = 0;
  if (titleExact) score += 45;
  else if (candidateTitleCore === expectedTitleCore) score += 40;
  else if (titleCompatible) score += 25;
  if (artistCompatible) score += 30;
  if (yearDelta === 0) score += 15;
  else if (yearDelta <= 1) score += 12;
  else if (yearDelta <= 3) score += 8;
  else if (!Number.isFinite(candidateYear)) score += 3;
  score += Math.round(overlap.ratio * 55);
  if (albumTracks.length && job.sidecar_track_count && Math.abs(albumTracks.length - job.sidecar_track_count) <= 2) score += 8;

  return {
    item,
    searchRank,
    score,
    titleExact,
    titleCompatible,
    artistCompatible,
    yearDelta,
    trackOverlapRatio: overlap.ratio,
    trackOverlapCount: overlap.count,
  };
}

function tracklistOverlap(sidecarRows, appleTracks) {
  if (!sidecarRows.length || !appleTracks.length) return { count: 0, ratio: 0 };
  const appleTitleCores = new Set(
    appleTracks
      .map((item) => normalizeTitleCore(item.attributes?.name))
      .filter(Boolean),
  );
  let count = 0;
  for (const row of sidecarRows) {
    const title = normalizeTitleCore(row.track_title);
    if (title && appleTitleCores.has(title)) count += 1;
  }
  return { count, ratio: count / Math.max(sidecarRows.length, 1) };
}

function normalizeAppleTrack(item, albumTrackIndex) {
  const attrs = item.attributes ?? {};
  if (!item.id || !attrs.name) return null;
  return {
    apple_catalog_id: item.id,
    album_track_index: albumTrackIndex,
    title: attrs.name,
    title_norm: normalize(attrs.name),
    title_core: normalizeTitleCore(attrs.name),
    artist_norm: normalize(attrs.artistName),
    disc_number: numberOrNull(attrs.discNumber),
    track_number: numberOrNull(attrs.trackNumber),
    duration_ms: numberOrNull(attrs.durationInMillis),
  };
}

function scoreTrackCandidate(row, track) {
  const expectedTitle = normalize(row.track_title);
  const expectedTitleCore = normalizeTitleCore(row.track_title);
  const expectedArtist = normalize(row.track_artist_name);
  const expectedDisc = numberOrNull(row.disc_number);
  const expectedTrack = numberOrNull(row.track_number);
  const expectedDuration = numberOrNull(row.duration_ms);
  const positionExact = expectedDisc === track.disc_number && expectedTrack === track.track_number;
  const titleExact = expectedTitle === track.title_norm;
  const titleCoreExact = expectedTitleCore && expectedTitleCore === track.title_core;
  const titleCompatible = titleExact || titleCoreExact || containsUseful(track.title_core, expectedTitleCore);
  const artistCompatible = compatibleNames(track.artist_norm, expectedArtist);
  const durationDelta = expectedDuration !== null && track.duration_ms !== null
    ? Math.abs(expectedDuration - track.duration_ms)
    : null;

  let score = 0;
  if (positionExact) score += 34;
  if (titleExact) score += 42;
  else if (titleCoreExact) score += 38;
  else if (titleCompatible) score += 24;
  if (artistCompatible) score += 14;
  if (durationDelta !== null && durationDelta <= 5000) score += 14;
  else if (durationDelta !== null && durationDelta <= 15000) score += 10;
  else if (durationDelta !== null && durationDelta <= 30000) score += 5;
  score -= Math.min(track.album_track_index, 5);

  const matchBasisParts = [];
  if (positionExact) matchBasisParts.push("position");
  if (titleExact) matchBasisParts.push("title");
  else if (titleCoreExact) matchBasisParts.push("title_core");
  if (artistCompatible) matchBasisParts.push("artist");
  if (durationDelta !== null && durationDelta <= 15000) matchBasisParts.push("duration");

  return {
    track,
    score,
    positionExact,
    titleExact,
    titleCoreExact,
    titleCompatible,
    artistCompatible,
    duration_delta_ms: durationDelta ?? "",
    title_match: titleExact ? "exact_normalized" : titleCoreExact ? "core_exact_normalized" : titleCompatible ? "compatible_normalized" : "not_matched",
    artist_match: artistCompatible ? "compatible_normalized" : "not_matched",
    match_basis: `album_track_try_harder_${matchBasisParts.join("_")}_auto_match`,
    confidence: score >= 92 && (titleExact || titleCoreExact) ? "high" : "medium",
    warnings: durationDelta !== null && durationDelta > 30000 ? "duration_differs" : "",
  };
}

function isTrackAutoAccept(best, second) {
  if (best.positionExact && (best.titleExact || best.titleCoreExact)) return true;
  if (best.positionExact && best.titleCompatible && best.duration_delta_ms !== "" && best.duration_delta_ms <= 15000) return true;
  if ((best.titleExact || best.titleCoreExact) && best.artistCompatible && best.score >= 78 && (!second || best.score - second.score >= 12)) return true;
  if (best.score >= 88 && (!second || best.score - second.score >= 10) && (best.positionExact || best.artistCompatible)) return true;
  return false;
}

function bridgeGraphReviewsFromSidecarTracks() {
  const sidecarTrackLinks = new Map();
  for (const link of priorLinks) {
    if (link.source_type === "album_sidecar_track" && link.apple_resource_type === "song") {
      sidecarTrackLinks.set(link.source_ref, link.apple_catalog_id);
    }
  }
  for (const link of links) {
    if (link.source_type === "album_sidecar_track" && link.apple_resource_type === "song") {
      sidecarTrackLinks.set(link.source_ref, link.apple_catalog_id);
    }
  }

  const rowsWithIds = [];
  for (const row of sidecarTracks) {
    const sourceRef = sidecarTrackSourceRef(row);
    const appleId = existingTrackIdForRow(row) || sidecarTrackLinks.get(sourceRef);
    if (!appleId) continue;
    rowsWithIds.push({ row, sourceRef, appleId });
  }

  const byExactYear = groupBy(rowsWithIds, ({ row }) => trackLookupKey(row.track_artist_name, row.track_title, row.album_year));
  const byNoYear = groupBy(rowsWithIds, ({ row }) => trackLookupKey(row.track_artist_name, row.track_title, ""));

  const graphReviews = priorReviews.filter((review) => (
    (review.source_type === "graph_song" || review.source_type === "graph_recording")
    && !priorLinkKeys.has(linkKeyFor(review.source_type, review.source_ref, "song", ""))
  ));

  for (const review of graphReviews) {
    const exactRows = uniqueRowsByAppleId(byExactYear.get(trackLookupKey(review.artist_display_name, review.title, review.year)) ?? []);
    const noYearRows = uniqueRowsByAppleId(byNoYear.get(trackLookupKey(review.artist_display_name, review.title, "")) ?? []);
    const picked = exactRows.length === 1
      ? { hit: exactRows[0], basis: "graph_review_try_harder_sidecar_track_exact_artist_title_year", confidence: "high", yearDelta: "0", warning: "" }
      : noYearRows.length === 1
        ? { hit: noYearRows[0], basis: "graph_review_try_harder_sidecar_track_unique_artist_title", confidence: "medium", yearDelta: "", warning: "year_not_confirmed" }
        : null;

    if (!picked) continue;
    const link = makeLink({
      source_ref: review.source_ref,
      source_type: review.source_type,
      source_candidate_type: review.source_candidate_type,
      apple_catalog_id: picked.hit.appleId,
      apple_resource_type: "song",
      match_status: picked.confidence === "high" ? "verified" : "candidate_verified",
      match_basis: picked.basis,
      confidence: picked.confidence,
      result_rank: "",
      title_match: "exact_normalized",
      artist_match: "exact_normalized",
      year_delta: picked.yearDelta,
      warnings: picked.warning,
      sidecar_track_source_ref: picked.hit.sourceRef,
    });
    addLink(link);
  }
}

function bridgeSidecarAlbumLinksFromGraphAlbumLinks() {
  const graphAlbumLinks = [...priorLinks, ...links]
    .filter((link) => link.source_type === "graph_album")
    .filter((link) => link.apple_resource_type === "album")
    .filter((link) => sidecarAlbumsByKey.has(link.source_ref));
  const sourceRefFilter = args.sourceRefs.length ? new Set(args.sourceRefs) : null;

  for (const link of graphAlbumLinks) {
    if (sourceRefFilter && !sourceRefFilter.has(link.source_ref)) continue;
    addLink(makeLink({
      source_ref: link.source_ref,
      source_type: "album_sidecar_album",
      source_candidate_type: "album",
      apple_catalog_id: link.apple_catalog_id,
      apple_resource_type: "album",
      match_status: link.match_status,
      match_basis: `album_sidecar_inherited_${link.source_type}_${link.match_basis}`,
      confidence: link.confidence,
      result_rank: link.result_rank,
      title_match: link.title_match,
      artist_match: link.artist_match,
      year_delta: link.year_delta,
      warnings: link.warnings,
      track_overlap_ratio: link.track_overlap_ratio,
      track_overlap_count: link.track_overlap_count,
      candidate_count: link.candidate_count,
    }));
  }
}

function recordAlbumSearchOutcome(job, outcome) {
  if (outcome.kind === "link") {
    addLink(makeLink({
      source_ref: job.source_ref,
      source_type: job.source_type,
      source_candidate_type: job.source_candidate_type,
      apple_catalog_id: outcome.apple_catalog_id,
      apple_resource_type: outcome.apple_resource_type,
      match_status: outcome.match_status,
      match_basis: outcome.match_basis,
      confidence: outcome.confidence,
      result_rank: outcome.result_rank,
      title_match: outcome.title_match,
      artist_match: outcome.artist_match,
      year_delta: outcome.year_delta,
      warnings: outcome.warnings,
      track_overlap_ratio: outcome.track_overlap_ratio,
      track_overlap_count: outcome.track_overlap_count,
      candidate_count: outcome.candidate_count,
    }));
    addLink(makeLink({
      source_ref: job.source_ref,
      source_type: "album_sidecar_album",
      source_candidate_type: "album",
      apple_catalog_id: outcome.apple_catalog_id,
      apple_resource_type: "album",
      match_status: outcome.match_status,
      match_basis: "album_sidecar_try_harder_inherited_graph_album_tracklist_match",
      confidence: outcome.confidence,
      result_rank: outcome.result_rank,
      title_match: outcome.title_match,
      artist_match: outcome.artist_match,
      year_delta: outcome.year_delta,
      warnings: outcome.warnings,
      track_overlap_ratio: outcome.track_overlap_ratio,
      track_overlap_count: outcome.track_overlap_count,
      candidate_count: outcome.candidate_count,
    }));
  } else {
    addDeferred({
      source_ref: job.source_ref,
      source_type: job.source_type,
      source_candidate_type: job.source_candidate_type,
      artist_display_name: job.artist_display_name,
      title: job.title,
      year: job.year,
      reason: outcome.reason,
      candidate_count: outcome.candidate_count ?? "",
      best_score: outcome.best_score ?? "",
      apple_album_id: "",
      error_message: outcome.error_message ?? "",
    });
  }
}

function recordAlbumTrackOutcome(_job, outcome) {
  for (const link of outcome.links ?? []) addLink(link);
  for (const row of outcome.deferred ?? []) addDeferred(row);
}

function makeLink(fields) {
  const appleId = fields.apple_catalog_id;
  return {
    link_key: linkKeyFor(fields.source_type, fields.source_ref, fields.apple_resource_type, appleId),
    run_version: runVersion,
    source_ref: fields.source_ref,
    source_type: fields.source_type,
    source_candidate_type: fields.source_candidate_type,
    external_catalog: "apple_music",
    apple_catalog_id: appleId,
    apple_resource_type: fields.apple_resource_type,
    storefront: args.storefront,
    match_status: fields.match_status,
    match_basis: fields.match_basis,
    confidence: fields.confidence,
    result_rank: fields.result_rank ?? "",
    title_match: fields.title_match ?? "",
    artist_match: fields.artist_match ?? "",
    year_delta: fields.year_delta ?? "",
    warnings: fields.warnings ?? "",
    apple_album_id: fields.apple_album_id ?? "",
    album_match_basis: fields.album_match_basis ?? "",
    sidecar_track_source_ref: fields.sidecar_track_source_ref ?? "",
    track_overlap_ratio: fields.track_overlap_ratio ?? "",
    track_overlap_count: fields.track_overlap_count ?? "",
    candidate_count: fields.candidate_count ?? "",
    track_score: fields.track_score ?? "",
    duration_delta_ms: fields.duration_delta_ms ?? "",
    verified_at: new Date().toISOString(),
    raw_payload_persisted: false,
  };
}

function addLink(link) {
  if (priorLinkKeys.has(link.link_key) || linkKeys.has(link.link_key)) return;
  links.push(link);
  linkKeys.add(link.link_key);
}

function addDeferred(row) {
  const deferred = {
    deferred_key: `${row.source_type}:${row.source_ref}:${row.reason}:${row.apple_album_id ?? ""}`,
    run_version: runVersion,
    source_ref: row.source_ref,
    source_type: row.source_type,
    source_candidate_type: row.source_candidate_type,
    artist_display_name: row.artist_display_name ?? "",
    title: row.title ?? "",
    year: row.year ?? "",
    storefront: args.storefront,
    deferred_reason: row.reason,
    candidate_count: row.candidate_count ?? "",
    best_score: row.best_score ?? "",
    apple_album_id: row.apple_album_id ?? "",
    error_message: row.error_message ?? "",
    raw_payload_persisted: false,
  };
  if (deferredKeys.has(deferred.deferred_key)) return;
  deferredRowsPush(deferred);
}

function deferredRowsPush(row) {
  deferred.push(row);
  deferredKeys.add(row.deferred_key);
}

function linkKeyFor(sourceType, sourceRef, resourceType, appleId) {
  return `${sourceType}:${sourceRef}:apple_music:${resourceType}:${appleId}:${args.storefront}`;
}

function existingTrackIdForRow(row) {
  return row.apple_track_id || priorTrackIdBySourceRef.get(sidecarTrackSourceRef(row)) || "";
}

function sidecarTrackSourceRef(row) {
  return [
    row.candidate_identity_key,
    row.disc_number || "",
    row.track_number || "",
    normalize(row.track_artist_name),
    normalize(row.track_title),
  ].join("@@");
}

function compareSidecarTrackRows(a, b) {
  return (Number(a.disc_number) || 0) - (Number(b.disc_number) || 0)
    || (Number(a.track_number) || 0) - (Number(b.track_number) || 0)
    || (Number(a.sidecar_track_index) || 0) - (Number(b.sidecar_track_index) || 0);
}

function uniqueRowsByAppleId(rows) {
  const byId = new Map();
  for (const row of rows) {
    if (!byId.has(row.appleId)) byId.set(row.appleId, row);
  }
  return [...byId.values()];
}

function readCheckpoint() {
  if (!fs.existsSync(checkpointPath)) return null;
  const loaded = readJson(checkpointPath);
  if (loaded.run_version !== runVersion || loaded.storefront !== args.storefront) {
    throw new Error(`Checkpoint ${checkpointPath} does not match run_version/storefront.`);
  }
  return loaded;
}

function readExistingOutput() {
  return {
    links: fs.existsSync(linksPath) ? readJsonl(linksPath) : [],
    deferred: fs.existsSync(deferredPath) ? readCsv(deferredPath) : [],
    summary: fs.existsSync(summaryPath) ? readJson(summaryPath) : null,
  };
}

function writeCheckpoint(status) {
  const value = {
    run_version: runVersion,
    status,
    storefront: args.storefront,
    generated_at: new Date().toISOString(),
    completed_album_search_keys: [...completedAlbumSearchKeys].sort(),
    completed_track_album_keys: [...completedTrackAlbumKeys].sort(),
    links: sortLinks(links),
    deferred: sortDeferred(deferred),
  };
  const tempPath = `${checkpointPath}.tmp`;
  fs.writeFileSync(tempPath, `${JSON.stringify(value, null, 2)}\n`);
  fs.renameSync(tempPath, checkpointPath);
}

function writeFinalArtifacts() {
  const sortedLinks = sortLinks(links);
  const sortedDeferred = sortDeferred(deferred);
  const summary = buildSummary(sortedLinks, sortedDeferred);
  fs.writeFileSync(linksPath, `${sortedLinks.map((link) => JSON.stringify(link)).join("\n")}\n`);
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
    "apple_album_id",
    "error_message",
    "raw_payload_persisted",
  ]);
  fs.writeFileSync(summaryPath, `${JSON.stringify(summary, null, 2)}\n`);
  fs.writeFileSync(manifestPath, buildManifest(summary));
  console.log(JSON.stringify(summary, null, 2));
}

function buildSummary(sortedLinks, sortedDeferred) {
  const existingCounts = existingOutput?.summary?.counts ?? {};
  const cumulativeAlbumSearchJobs = Math.max(
    existingCounts.album_search_jobs_completed_cumulative ?? existingCounts.album_search_jobs_completed ?? 0,
    completedAlbumSearchKeys.size,
  );
  const cumulativeAlbumTrackJobs = Math.max(
    existingCounts.album_track_jobs_completed_cumulative ?? existingCounts.album_track_jobs_completed ?? 0,
    completedTrackAlbumKeys.size,
  );

  return {
    run_version: runVersion,
    status: "complete",
    generated_at: new Date().toISOString(),
    storefront: args.storefront,
    policy: {
      raw_apple_payloads_persisted: false,
      persisted_catalog_fields: ["apple_catalog_id", "apple_resource_type", "storefront", "match metadata"],
      excluded_persistent_fields: ["artwork", "previews", "lyrics", "raw_catalog_payload", "music_user_token"],
    },
    inputs: {
      prior_links: "data/canonical_graph/current/apple_music_link_pass_v1/apple_music_links_v1.jsonl",
      prior_review_queue: "data/canonical_graph/current/apple_music_link_pass_v1/apple_music_manual_review_queue.csv",
      album_track_sidecar_tracks: "data/canonical_graph/current/album_track_sidecar_tracks.csv",
    },
    counts: {
      prior_links_total: priorLinks.length,
      new_links_total: sortedLinks.length,
      deferred_total: sortedDeferred.length,
      album_search_jobs_completed_current_invocation: completedAlbumSearchKeys.size,
      album_track_jobs_completed_current_invocation: completedTrackAlbumKeys.size,
      album_search_jobs_completed_cumulative: cumulativeAlbumSearchJobs,
      album_track_jobs_completed_cumulative: cumulativeAlbumTrackJobs,
      new_links_by_source_type: countBy(sortedLinks, "source_type"),
      new_links_by_resource_type: countBy(sortedLinks, "apple_resource_type"),
      new_links_by_match_basis: countBy(sortedLinks, "match_basis"),
      deferred_by_reason: countBy(sortedDeferred, "deferred_reason"),
    },
  };
}

function buildManifest(summary) {
  return `# Apple Music Try Harder Pass v1

Generated: ${summary.generated_at}

Status: \`${summary.status}\`

Storefront: \`${summary.storefront}\`

## Policy

- Raw Apple payloads persisted: \`false\`
- Durable output stores Apple catalog IDs, resource type, storefront, source refs, match status, and scoring metadata only.
- Artwork, previews, lyrics, MusicKit content, raw catalog responses, and Music User Tokens are not persisted.

## Intent

This pass avoids manual review by using safer additional context:

- album-scoped Apple Music track relationships for sidecar track IDs
- tracklist overlap for album rows that the first pass deferred
- sidecar-derived Apple track IDs to bridge deferred graph song/recording rows

## Counts

- Prior links total: ${summary.counts.prior_links_total}
- New links total: ${summary.counts.new_links_total}
- Deferred rows: ${summary.counts.deferred_total}
- Album search jobs completed cumulative: ${summary.counts.album_search_jobs_completed_cumulative}
- Album track jobs completed cumulative: ${summary.counts.album_track_jobs_completed_cumulative}
- Album search jobs completed current invocation: ${summary.counts.album_search_jobs_completed_current_invocation}
- Album track jobs completed current invocation: ${summary.counts.album_track_jobs_completed_current_invocation}

## New Links By Source Type

${tableFromCounts(summary.counts.new_links_by_source_type)}

## New Links By Match Basis

${tableFromCounts(summary.counts.new_links_by_match_basis)}

## Deferred By Reason

${tableFromCounts(summary.counts.deferred_by_reason)}
`;
}

function logProgress(label, processed, total) {
  const summary = buildSummary(sortLinks(links), sortDeferred(deferred));
  console.error(`${label}: ${processed}/${total}, new_links=${summary.counts.new_links_total}, deferred=${summary.counts.deferred_total}`);
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function readJsonl(file) {
  const text = fs.readFileSync(file, "utf8").trim();
  if (!text) return [];
  return text.split("\n").filter(Boolean).map((line) => JSON.parse(line));
}

function readCsv(file) {
  const text = fs.readFileSync(file, "utf8");
  const records = parseCsv(text);
  if (!records.length) return [];
  const [headers, ...rows] = records;
  return rows
    .filter((row) => row.some((value) => value !== ""))
    .map((row) => Object.fromEntries(headers.map((header, index) => [header, row[index] ?? ""])));
}

function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;

  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];
    const next = text[index + 1];
    if (quoted) {
      if (char === "\"" && next === "\"") {
        field += "\"";
        index += 1;
      } else if (char === "\"") {
        quoted = false;
      } else {
        field += char;
      }
    } else if (char === "\"") {
      quoted = true;
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
  if (field || row.length) {
    row.push(field);
    rows.push(row);
  }
  return rows;
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
  if (/[",\n\r]/.test(text)) return `"${text.replace(/"/g, "\"\"")}"`;
  return text;
}

function groupBy(rows, keyForRow) {
  const map = new Map();
  for (const row of rows) {
    const key = keyForRow(row) ?? "";
    if (!map.has(key)) map.set(key, []);
    map.get(key).push(row);
  }
  return map;
}

function countBy(rows, key) {
  const counts = {};
  for (const row of rows) {
    const countKey = row[key] || "unknown";
    counts[countKey] = (counts[countKey] ?? 0) + 1;
  }
  return counts;
}

function sortLinks(values) {
  return [...values].sort((a, b) => a.link_key.localeCompare(b.link_key));
}

function sortDeferred(values) {
  return [...values].sort((a, b) => a.deferred_key.localeCompare(b.deferred_key));
}

async function runPool(items, concurrency, worker) {
  let nextIndex = 0;
  const workers = Array.from({ length: Math.min(concurrency, items.length) }, async () => {
    while (nextIndex < items.length) {
      const index = nextIndex;
      nextIndex += 1;
      await worker(items[index], index);
    }
  });
  await Promise.all(workers);
}

function normalize(value) {
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

function normalizeTitleCore(value) {
  return normalize(value)
    .replace(/\b(remaster(ed)?|mono|stereo|single|album|version|edit|deluxe|expanded|anniversary|bonus|track|explicit|clean)\b/g, " ")
    .replace(/\b(19|20)\d{2}\b/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function stripFeaturing(value) {
  return String(value ?? "").replace(/\b(feat\.?|ft\.?|featuring)\b.*$/iu, "").trim();
}

function compatibleNames(candidate, expected) {
  if (!candidate || !expected) return false;
  return candidate === expected || candidate.includes(expected) || expected.includes(candidate);
}

function containsUseful(candidate, expected) {
  if (!candidate || !expected || expected.length < 4) return false;
  return candidate.includes(expected) || expected.includes(candidate);
}

function numberOrNull(value) {
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function uniqueValues(values) {
  return [...new Set(values.filter(Boolean))];
}

function trackLookupKey(artist, title, year) {
  return `${normalize(artist)}|${normalize(title)}|${String(year ?? "")}`;
}

function tableFromCounts(counts) {
  const rows = Object.entries(counts)
    .sort((a, b) => b[1] - a[1])
    .map(([key, count]) => `| ${escapeMd(key)} | ${count} |`);
  return ["| key | count |", "| --- | ---: |", ...rows].join("\n");
}

function escapeMd(value) {
  return String(value ?? "").replace(/\|/g, "\\|");
}

function errorMessage(error) {
  return error instanceof Error ? error.message : String(error);
}
