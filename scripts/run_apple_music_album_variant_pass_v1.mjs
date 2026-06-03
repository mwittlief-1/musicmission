#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { createAppleMusicCatalogClient } from "./lib/appleMusicCatalogClient.mjs";

const repoRoot = process.cwd();
const currentRoot = path.join(repoRoot, "data/canonical_graph/current");
const outputRoot = path.join(currentRoot, "apple_music_album_variant_pass_v1");
const runVersion = "apple_music_album_variant_pass_v1";
const storefront = "us";

const args = parseArgs(process.argv.slice(2));
const client = createAppleMusicCatalogClient({
  storefront,
  maxRetries: 8,
  retryBaseDelayMs: 1000,
  retryMaxDelayMs: 60000,
  timeoutMs: 60000,
});

fs.mkdirSync(outputRoot, { recursive: true });

const linksPath = path.join(outputRoot, "apple_music_album_variant_links_v1.jsonl");
const deferredPath = path.join(outputRoot, "apple_music_album_variant_deferred_queue.csv");
const summaryPath = path.join(outputRoot, "apple_music_album_variant_summary.json");
const manifestPath = path.join(outputRoot, "apple_music_album_variant_manifest.md");
const checkpointPath = path.join(outputRoot, "apple_music_album_variant_pass_v1.checkpoint.json");

const sidecarAlbums = readCsv(path.join(currentRoot, "album_track_sidecar_album_resolution.csv"));
const sidecarTracks = readCsv(path.join(currentRoot, "album_track_sidecar_tracks.csv"));
const firstPassReviews = readCsv(path.join(currentRoot, "apple_music_link_pass_v1/apple_music_manual_review_queue.csv"));
const existingLinks = [
  ...readJsonl(path.join(currentRoot, "apple_music_link_pass_v1/apple_music_links_v1.jsonl")),
  ...readJsonl(path.join(currentRoot, "apple_music_try_harder_pass_v1/apple_music_try_harder_links_v1.jsonl")),
  ...safeReadJsonl(path.join(currentRoot, "apple_music_residual_track_pass_v1/apple_music_residual_track_links_v1.jsonl")),
  ...safeReadJsonl(path.join(currentRoot, "apple_music_offline_reconciliation_pass_v1/apple_music_offline_reconciliation_links_v1.jsonl")),
];

const sidecarTracksByAlbum = groupBy(sidecarTracks, (row) => row.candidate_identity_key);
const existingSidecarAlbumRefs = new Set(
  existingLinks
    .filter((link) => link.source_type === "album_sidecar_album" && link.apple_resource_type === "album")
    .map((link) => link.source_ref),
);
const existingGraphAlbumRefs = new Set(
  existingLinks
    .filter((link) => link.source_type === "graph_album" && link.apple_resource_type === "album")
    .map((link) => link.source_ref),
);
const existingSidecarTrackRefs = new Set(
  existingLinks
    .filter((link) => link.source_type === "album_sidecar_track" && link.apple_resource_type === "song")
    .map((link) => link.source_ref),
);
const firstPassAlbumReviewsByRef = new Map(
  firstPassReviews
    .filter((row) => row.source_type === "graph_album")
    .map((row) => [row.source_ref, row]),
);

const checkpoint = args.resume ? readCheckpoint() : null;
const completedAlbumRefs = new Set(checkpoint?.completed_album_refs ?? []);
const links = checkpoint?.links ?? [];
const deferred = checkpoint?.deferred ?? [];
const linkKeys = new Set(links.map((link) => link.link_key));
const deferredKeys = new Set(deferred.map((row) => row.deferred_key));

const albumJobs = buildAlbumJobs();

console.error(JSON.stringify({
  run_version: runVersion,
  album_jobs: albumJobs.length,
  dry_run: args.dryRun,
}, null, 2));

await runPool(albumJobs.filter((job) => !completedAlbumRefs.has(job.source_ref)), args.concurrency, async (job, index) => {
  const outcome = await safelyResolveAlbum(job);
  recordOutcome(job, outcome);
  completedAlbumRefs.add(job.source_ref);
  if ((index + 1) % args.checkpointEvery === 0) writeCheckpoint("partial");
  if ((index + 1) % args.progressEvery === 0) {
    console.error(`album-variant: ${index + 1}/${albumJobs.length}, links=${links.length}, deferred=${deferred.length}`);
  }
});

writeCheckpoint("complete");
writeFinalArtifacts();
if (!args.keepCheckpoint && fs.existsSync(checkpointPath)) fs.unlinkSync(checkpointPath);

function parseArgs(argv) {
  const parsed = {
    concurrency: 2,
    progressEvery: 25,
    checkpointEvery: 25,
    resume: true,
    keepCheckpoint: false,
    dryRun: false,
    limitAlbums: Number.NaN,
  };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--concurrency") parsed.concurrency = Number(argv[++index]);
    else if (arg === "--progress-every") parsed.progressEvery = Number(argv[++index]);
    else if (arg === "--checkpoint-every") parsed.checkpointEvery = Number(argv[++index]);
    else if (arg === "--no-resume") parsed.resume = false;
    else if (arg === "--keep-checkpoint") parsed.keepCheckpoint = true;
    else if (arg === "--dry-run") parsed.dryRun = true;
    else if (arg === "--limit-albums") parsed.limitAlbums = Number(argv[++index]);
  }
  if (!Number.isFinite(parsed.concurrency) || parsed.concurrency < 1) parsed.concurrency = 1;
  if (parsed.concurrency > 4) parsed.concurrency = 4;
  return parsed;
}

function buildAlbumJobs() {
  const jobs = sidecarAlbums
    .filter((album) => !existingSidecarAlbumRefs.has(album.candidate_identity_key))
    .map((album) => ({
      source_ref: album.candidate_identity_key,
      artist_display_name: album.artist_display_name,
      title: album.title,
      year: album.year,
      sidecar_track_count: Number(album.track_count) || (sidecarTracksByAlbum.get(album.candidate_identity_key)?.length ?? 0),
      sidecar_tracks: sidecarTracksByAlbum.get(album.candidate_identity_key) ?? [],
      first_pass_review_reason: firstPassAlbumReviewsByRef.get(album.candidate_identity_key)?.review_reason ?? "",
      first_pass_best_score: firstPassAlbumReviewsByRef.get(album.candidate_identity_key)?.best_score ?? "",
    }))
    .filter((job) => job.sidecar_tracks.length > 0)
    .sort((a, b) => a.source_ref.localeCompare(b.source_ref));
  return Number.isFinite(args.limitAlbums) ? jobs.slice(0, args.limitAlbums) : jobs;
}

async function safelyResolveAlbum(job) {
  try {
    if (args.dryRun) return { accepted: null, candidates: 0, links: [], deferred_reason: "dry_run_no_catalog_call" };
    return await resolveAlbum(job);
  } catch (error) {
    return {
      accepted: null,
      candidates: 0,
      links: [],
      deferred_reason: "album_variant_request_error",
      error_message: error instanceof Error ? error.message : String(error),
    };
  }
}

async function resolveAlbum(job) {
  const candidates = [];
  for (const term of buildSearchTerms(job)) {
    const payload = await client.catalogGet(`/v1/catalog/${encodeURIComponent(storefront)}/search`, {
      term,
      types: "albums",
      limit: 15,
      "fields[albums]": "name,artistName,releaseDate",
    });
    for (const [index, item] of (payload?.results?.albums?.data ?? []).entries()) {
      if (!item?.id || candidates.some((candidate) => candidate.item.id === item.id)) continue;
      const tracks = await fetchAlbumTracks(item.id);
      candidates.push(scoreAlbumCandidate(item, tracks, job, index + 1, term));
    }
  }

  candidates.sort((a, b) => b.score - a.score);
  const accepted = chooseCandidate(candidates);
  if (!accepted) {
    return {
      accepted: null,
      candidates: candidates.length,
      links: [],
      deferred_reason: "album_variant_no_safe_match",
      best_score: candidates[0]?.score ?? 0,
    };
  }

  return {
    accepted,
    candidates: candidates.length,
    links: buildLinksForAcceptedAlbum(job, accepted, candidates.length),
  };
}

function buildSearchTerms(job) {
  const strippedTitle = stripArtistFromTitle(job.title, job.artist_display_name);
  const terms = [
    `${job.artist_display_name} ${job.title}`,
    `${job.artist_display_name} ${strippedTitle}`,
    `${strippedTitle} ${job.artist_display_name}`,
    job.title,
  ];
  if (isCompilationLike(job.title)) {
    terms.push(`${job.artist_display_name} greatest hits`);
    terms.push(`${job.artist_display_name} best of`);
    terms.push(`${job.artist_display_name} collection`);
  }
  if (isVariousOrCast(job.artist_display_name)) {
    terms.push(strippedTitle);
  }
  return uniqueValues(terms.map((term) => term.trim()).filter(Boolean));
}

async function fetchAlbumTracks(albumId) {
  const payload = await client.catalogGet(`/v1/catalog/${encodeURIComponent(storefront)}/albums/${encodeURIComponent(albumId)}/tracks`, {
    limit: 300,
    "fields[songs]": "name,artistName,durationInMillis,discNumber,trackNumber",
  });
  return (payload?.data ?? []).filter((item) => item.type === "songs" && item.id);
}

function scoreAlbumCandidate(item, appleTracks, job, searchRank, searchTerm) {
  const attrs = item.attributes ?? {};
  const expectedTitle = normalize(job.title);
  const expectedTitleCore = normalizeTitleCore(job.title);
  const expectedTitleArtistStripped = normalizeTitleCore(stripArtistFromTitle(job.title, job.artist_display_name));
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
  const titleCoreExact = candidateTitleCore === expectedTitleCore;
  const artistStrippedTitleMatch = expectedTitleArtistStripped && candidateTitleCore === expectedTitleArtistStripped;
  const titleCompatible = titleExact
    || titleCoreExact
    || artistStrippedTitleMatch
    || containsUseful(candidateTitleCore, expectedTitleCore);
  const artistCompatible = compatibleNames(candidateArtist, expectedArtist)
    || isVariousOrCast(job.artist_display_name)
    || isVariousOrCast(attrs.artistName);
  const overlap = tracklistOverlap(job.sidecar_tracks, appleTracks);
  const compilationMode = isCompilationLike(job.title) || isCompilationLike(attrs.name) || isVariousOrCast(job.artist_display_name);
  const strongTracklist = overlap.ratio >= 0.78 && overlap.count >= Math.min(8, Math.max(3, job.sidecar_tracks.length));
  const mediumTracklist = overlap.ratio >= 0.65 && overlap.count >= Math.min(6, Math.max(3, job.sidecar_tracks.length));

  let score = 0;
  if (titleExact) score += 42;
  else if (titleCoreExact) score += 38;
  else if (artistStrippedTitleMatch) score += 36;
  else if (titleCompatible) score += 22;
  if (artistCompatible) score += 24;
  if (yearDelta === 0) score += 12;
  else if (yearDelta <= 1) score += 10;
  else if (yearDelta <= 3) score += 5;
  score += Math.round(overlap.ratio * 70);
  if (Math.abs(appleTracks.length - job.sidecar_tracks.length) <= 2) score += 8;
  if (compilationMode && strongTracklist) score += 12;

  return {
    item,
    searchRank,
    searchTerm,
    score,
    titleExact,
    titleCoreExact,
    artistStrippedTitleMatch,
    titleCompatible,
    artistCompatible,
    compilationMode,
    strongTracklist,
    mediumTracklist,
    yearDelta,
    trackOverlapRatio: overlap.ratio,
    trackOverlapCount: overlap.count,
    orderedAnchorMatches: overlap.orderedAnchorMatches,
    appleTracks,
  };
}

function chooseCandidate(candidates) {
  for (const candidate of candidates) {
    if (
      candidate.trackOverlapRatio >= 0.7
      && candidate.trackOverlapCount >= 5
      && candidate.yearDelta <= 3
      && (candidate.titleCompatible || candidate.compilationMode)
      && (candidate.artistCompatible || candidate.trackOverlapRatio >= 0.82)
      && candidate.orderedAnchorMatches >= 2
    ) return candidate;
  }
  for (const candidate of candidates) {
    if (
      candidate.trackOverlapRatio >= 0.58
      && candidate.trackOverlapCount >= 4
      && candidate.yearDelta <= 1
      && (candidate.titleCoreExact || candidate.artistStrippedTitleMatch)
      && candidate.artistCompatible
    ) return candidate;
  }
  return null;
}

function buildLinksForAcceptedAlbum(job, accepted, candidateCount) {
  const output = [];
  const albumFields = {
    apple_catalog_id: accepted.item.id,
    apple_resource_type: "album",
    match_status: accepted.trackOverlapRatio >= 0.78 ? "verified" : "candidate_verified",
    match_basis: accepted.compilationMode && !accepted.titleCompatible
      ? "album_variant_compilation_tracklist_auto_match"
      : accepted.artistStrippedTitleMatch
        ? "album_variant_artist_name_stripped_title_auto_match"
        : "album_variant_remaster_or_title_core_tracklist_auto_match",
    confidence: accepted.trackOverlapRatio >= 0.78 ? "high" : "medium",
    title_match: accepted.titleExact ? "exact_normalized" : accepted.artistStrippedTitleMatch ? "artist_name_stripped_exact" : accepted.titleCoreExact ? "core_exact_normalized" : accepted.titleCompatible ? "compatible_normalized" : "tracklist_supported",
    artist_match: accepted.artistCompatible ? "compatible_normalized" : "tracklist_supported",
    year_delta: accepted.yearDelta,
    warnings: accepted.compilationMode ? "compilation_or_variant_title_accepted_by_tracklist" : "",
    result_rank: accepted.searchRank,
    track_overlap_ratio: accepted.trackOverlapRatio.toFixed(3),
    track_overlap_count: accepted.trackOverlapCount,
    ordered_anchor_matches: accepted.orderedAnchorMatches,
    candidate_count: candidateCount,
  };
  output.push(makeLink(job, "graph_album", "album", albumFields));
  output.push(makeLink(job, "album_sidecar_album", "album", albumFields));

  const trackLinks = resolveAcceptedAlbumTracks(job, accepted);
  output.push(...trackLinks);
  return output;
}

function resolveAcceptedAlbumTracks(job, accepted) {
  const normalizedAppleTracks = accepted.appleTracks
    .map((item, index) => normalizeAppleTrack(item, index))
    .filter(Boolean);
  const usedAppleIds = new Set();
  const output = [];
  for (const row of job.sidecar_tracks.sort(compareTrackRows)) {
    const sourceRef = sidecarTrackSourceRef(row);
    if (existingSidecarTrackRefs.has(sourceRef)) continue;
    const scored = normalizedAppleTracks
      .filter((track) => !usedAppleIds.has(track.apple_catalog_id))
      .map((track) => scoreTrackCandidate(row, track))
      .sort((a, b) => b.score - a.score);
    const best = scored[0];
    const second = scored[1];
    if (!best || !isTrackAutoAccept(best, second)) continue;
    usedAppleIds.add(best.track.apple_catalog_id);
    output.push({
      link_key: `album_sidecar_track:${sourceRef}:apple_music:song:${best.track.apple_catalog_id}:${storefront}`,
      run_version: runVersion,
      source_ref: sourceRef,
      source_type: "album_sidecar_track",
      source_candidate_type: "track",
      external_catalog: "apple_music",
      apple_catalog_id: best.track.apple_catalog_id,
      apple_resource_type: "song",
      storefront,
      match_status: best.confidence === "high" ? "verified" : "candidate_verified",
      match_basis: "album_variant_track_auto_match",
      confidence: best.confidence,
      title_match: best.title_match,
      artist_match: best.artist_match,
      warnings: best.warnings,
      apple_album_id: accepted.item.id,
      album_match_basis: "album_variant_album_auto_match",
      track_score: best.score,
      duration_delta_ms: best.duration_delta_ms,
      verified_at: new Date().toISOString(),
      raw_payload_persisted: false,
    });
  }
  return output;
}

function makeLink(job, sourceType, candidateType, fields) {
  return {
    link_key: `${sourceType}:${job.source_ref}:apple_music:${fields.apple_resource_type}:${fields.apple_catalog_id}:${storefront}`,
    run_version: runVersion,
    source_ref: job.source_ref,
    source_type: sourceType,
    source_candidate_type: candidateType,
    external_catalog: "apple_music",
    apple_catalog_id: fields.apple_catalog_id,
    apple_resource_type: fields.apple_resource_type,
    storefront,
    match_status: fields.match_status,
    match_basis: fields.match_basis,
    confidence: fields.confidence,
    result_rank: fields.result_rank,
    title_match: fields.title_match,
    artist_match: fields.artist_match,
    year_delta: fields.year_delta,
    warnings: fields.warnings,
    track_overlap_ratio: fields.track_overlap_ratio,
    track_overlap_count: fields.track_overlap_count,
    ordered_anchor_matches: fields.ordered_anchor_matches,
    candidate_count: fields.candidate_count,
    prior_review_reason: job.first_pass_review_reason,
    prior_best_score: job.first_pass_best_score,
    verified_at: new Date().toISOString(),
    raw_payload_persisted: false,
  };
}

function recordOutcome(job, outcome) {
  if (outcome.accepted) {
    for (const link of outcome.links) {
      if (!linkKeys.has(link.link_key)) {
        links.push(link);
        linkKeys.add(link.link_key);
      }
    }
    return;
  }
  const deferredRow = {
    deferred_key: `album_sidecar_album:${job.source_ref}:${outcome.deferred_reason}`,
    run_version: runVersion,
    source_ref: job.source_ref,
    source_type: "album_sidecar_album",
    source_candidate_type: "album",
    artist_display_name: job.artist_display_name,
    title: job.title,
    year: job.year,
    storefront,
    deferred_reason: outcome.deferred_reason,
    candidate_count: outcome.candidates ?? "",
    best_score: outcome.best_score ?? "",
    error_message: outcome.error_message ?? "",
    raw_payload_persisted: false,
  };
  if (!deferredKeys.has(deferredRow.deferred_key)) {
    deferred.push(deferredRow);
    deferredKeys.add(deferredRow.deferred_key);
  }
}

function tracklistOverlap(sidecarRows, appleTracks) {
  if (!sidecarRows.length || !appleTracks.length) return { count: 0, ratio: 0, orderedAnchorMatches: 0 };
  const appleTitleCores = new Set(appleTracks.map((item) => normalizeTitleCore(item.attributes?.name)).filter(Boolean));
  let count = 0;
  for (const row of sidecarRows) {
    const title = normalizeTitleCore(row.track_title);
    if (title && appleTitleCores.has(title)) count += 1;
  }
  const anchors = anchorRows(sidecarRows);
  let orderedAnchorMatches = 0;
  for (const row of anchors) {
    const appleAtPosition = appleTracks.find((item) => (
      Number(item.attributes?.discNumber) === Number(row.disc_number)
      && Number(item.attributes?.trackNumber) === Number(row.track_number)
    ));
    if (appleAtPosition && normalizeTitleCore(appleAtPosition.attributes?.name) === normalizeTitleCore(row.track_title)) {
      orderedAnchorMatches += 1;
    }
  }
  return { count, ratio: count / Math.max(sidecarRows.length, 1), orderedAnchorMatches };
}

function anchorRows(rows) {
  const sorted = [...rows].sort(compareTrackRows);
  return uniqueValues([
    sorted[0],
    sorted[Math.floor(sorted.length / 2)],
    sorted[sorted.length - 1],
  ].filter(Boolean));
}

function normalizeAppleTrack(item, albumTrackIndex) {
  const attrs = item.attributes ?? {};
  if (!item.id || !attrs.name) return null;
  return {
    apple_catalog_id: item.id,
    album_track_index: albumTrackIndex,
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
  const expectedArtist = normalize(row.track_artist_name || row.artist_display_name);
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
  score -= Math.min(track.album_track_index, 5);
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
    confidence: score >= 92 && (titleExact || titleCoreExact) ? "high" : "medium",
    warnings: "",
  };
}

function isTrackAutoAccept(best, second) {
  if (best.positionExact && best.artistCompatible && (best.titleExact || best.titleCoreExact)) return true;
  if (best.positionExact && best.titleCompatible && best.duration_delta_ms !== "" && best.duration_delta_ms <= 5000) return true;
  if ((best.titleExact || best.titleCoreExact) && best.artistCompatible && best.duration_delta_ms !== "" && best.duration_delta_ms <= 5000 && (!second || best.score - second.score >= 12)) return true;
  return false;
}

function writeCheckpoint(status) {
  const value = {
    run_version: runVersion,
    status,
    storefront,
    generated_at: new Date().toISOString(),
    completed_album_refs: [...completedAlbumRefs].sort(),
    links,
    deferred,
  };
  const tempPath = `${checkpointPath}.tmp`;
  fs.writeFileSync(tempPath, `${JSON.stringify(value, null, 2)}\n`);
  fs.renameSync(tempPath, checkpointPath);
}

function readCheckpoint() {
  if (!fs.existsSync(checkpointPath)) return null;
  const loaded = readJson(checkpointPath);
  if (loaded.run_version !== runVersion) throw new Error(`Checkpoint ${checkpointPath} has wrong run_version.`);
  return loaded;
}

function writeFinalArtifacts() {
  const sortedLinks = [...links].sort((a, b) => a.link_key.localeCompare(b.link_key));
  const sortedDeferred = [...deferred].sort((a, b) => a.deferred_key.localeCompare(b.deferred_key));
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
    "error_message",
    "raw_payload_persisted",
  ]);
  fs.writeFileSync(summaryPath, `${JSON.stringify(summary, null, 2)}\n`);
  fs.writeFileSync(manifestPath, buildManifest(summary));
  console.log(JSON.stringify(summary, null, 2));
}

function buildSummary(sortedLinks, sortedDeferred) {
  return {
    run_version: runVersion,
    status: "complete",
    generated_at: new Date().toISOString(),
    storefront,
    policy: {
      raw_apple_payloads_persisted: false,
      persisted_catalog_fields: ["apple_catalog_id", "apple_resource_type", "storefront", "match metadata"],
      excluded_persistent_fields: ["artwork", "previews", "lyrics", "raw_catalog_payload", "music_user_token"],
    },
    counts: {
      album_jobs_completed: completedAlbumRefs.size,
      new_links_total: sortedLinks.length,
      deferred_total: sortedDeferred.length,
      new_links_by_source_type: countBy(sortedLinks, "source_type"),
      new_links_by_resource_type: countBy(sortedLinks, "apple_resource_type"),
      new_links_by_match_basis: countBy(sortedLinks, "match_basis"),
      deferred_by_reason: countBy(sortedDeferred, "deferred_reason"),
    },
  };
}

function buildManifest(summary) {
  return `# Apple Music Album Variant Pass v1

Generated: ${summary.generated_at}

Status: \`${summary.status}\`

Storefront: \`${summary.storefront}\`

## Policy

- Raw Apple payloads persisted: \`false\`
- Apple requests use sparse album and song fields for transient matching.
- Durable output stores Apple catalog IDs, resource type, storefront, source refs, match status, and matching metadata only.

## Intent

This pass targets albums still missing Apple album IDs after the earlier passes, with specific handling for remastered editions, compilation title mismatches, and source titles that include the artist name.

## Counts

- Album jobs completed: ${summary.counts.album_jobs_completed}
- New links total: ${summary.counts.new_links_total}
- Deferred rows: ${summary.counts.deferred_total}

## New Links By Source Type

${tableFromCounts(summary.counts.new_links_by_source_type)}

## New Links By Match Basis

${tableFromCounts(summary.counts.new_links_by_match_basis)}

## Deferred By Reason

${tableFromCounts(summary.counts.deferred_by_reason)}
`;
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function readJsonl(file) {
  const text = fs.readFileSync(file, "utf8").trim();
  if (!text) return [];
  return text.split("\n").filter(Boolean).map((line) => JSON.parse(line));
}

function safeReadJsonl(file) {
  return fs.existsSync(file) ? readJsonl(file) : [];
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

function sidecarTrackSourceRef(row) {
  return [
    row.candidate_identity_key,
    row.disc_number || "",
    row.track_number || "",
    normalize(row.track_artist_name),
    normalize(row.track_title),
  ].join("@@");
}

function compareTrackRows(a, b) {
  return (Number(a.disc_number) || 0) - (Number(b.disc_number) || 0)
    || (Number(a.track_number) || 0) - (Number(b.track_number) || 0)
    || (Number(a.sidecar_track_index) || 0) - (Number(b.sidecar_track_index) || 0);
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
    .replace(/\b(remaster(ed)?|remastered|mono|stereo|single|album|version|edit|deluxe|expanded|anniversary|bonus|track|explicit|clean|edition|reissue|original)\b/g, " ")
    .replace(/\b(19|20)\d{2}\b/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function stripArtistFromTitle(title, artist) {
  const normalizedArtist = normalize(artist);
  const words = normalizedArtist.split(" ").filter(Boolean);
  let normalizedTitle = normalize(title);
  if (normalizedArtist && normalizedTitle.startsWith(normalizedArtist)) {
    normalizedTitle = normalizedTitle.slice(normalizedArtist.length).trim();
  }
  if (words.length > 1) {
    normalizedTitle = normalizedTitle
      .split(" ")
      .filter((word) => !words.includes(word))
      .join(" ")
      .trim();
  }
  return normalizedTitle || title;
}

function compatibleNames(candidate, expected) {
  if (!candidate || !expected) return false;
  return candidate === expected || candidate.includes(expected) || expected.includes(candidate);
}

function containsUseful(candidate, expected) {
  if (!candidate || !expected || expected.length < 4) return false;
  return candidate.includes(expected) || expected.includes(candidate);
}

function isCompilationLike(value) {
  return /\b(greatest|best|hits|singles|collection|anthology|essential|ultimate|gold|complete|selected|favorites|favourites|retrospective|chronicle|legend|definitive|discography)\b/i.test(String(value ?? ""));
}

function isVariousOrCast(value) {
  return /\b(various artists|original .* cast|soundtrack|motion picture|broadway cast|london cast)\b/i.test(String(value ?? ""));
}

function numberOrNull(value) {
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function uniqueValues(values) {
  return [...new Set(values)];
}

function groupBy(rows, keyForRow) {
  const map = new Map();
  for (const row of rows) {
    const key = keyForRow(row);
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

function tableFromCounts(counts) {
  const rows = Object.entries(counts)
    .sort((a, b) => b[1] - a[1])
    .map(([key, count]) => `| ${escapeMd(key)} | ${count} |`);
  return ["| key | count |", "| --- | ---: |", ...rows].join("\n");
}

function escapeMd(value) {
  return String(value ?? "").replace(/\|/g, "\\|");
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
