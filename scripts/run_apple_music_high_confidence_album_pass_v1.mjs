#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { createAppleMusicCatalogClient } from "./lib/appleMusicCatalogClient.mjs";

const repoRoot = process.cwd();
const currentRoot = path.join(repoRoot, "data/canonical_graph/current");
const outputRoot = path.join(currentRoot, "apple_music_high_confidence_album_pass_v1");
const runVersion = "apple_music_high_confidence_album_pass_v1";

const args = parseArgs(process.argv.slice(2));
const client = createAppleMusicCatalogClient({
  storefront: args.storefront,
  maxRetries: 8,
  retryBaseDelayMs: 1000,
  retryMaxDelayMs: 60000,
  timeoutMs: 60000,
});

fs.mkdirSync(outputRoot, { recursive: true });

const linksPath = path.join(outputRoot, "apple_music_high_confidence_album_links_v1.jsonl");
const deferredPath = path.join(outputRoot, "apple_music_high_confidence_album_deferred_queue.csv");
const summaryPath = path.join(outputRoot, "apple_music_high_confidence_album_summary.json");
const manifestPath = path.join(outputRoot, "apple_music_high_confidence_album_manifest.md");
const checkpointPath = path.join(outputRoot, "apple_music_high_confidence_album_pass_v1.checkpoint.json");

const graphRows = readJson(path.join(currentRoot, "graph_linking_node_set.json")).rows;
const sidecarTracks = readCsv(path.join(currentRoot, "album_track_sidecar_tracks.csv"));
const firstPassReviews = readCsv(path.join(currentRoot, "apple_music_link_pass_v1/apple_music_manual_review_queue.csv"));
const artistAlbumDeferred = readCsv(path.join(
  currentRoot,
  "apple_music_artist_album_resolver_pass_v1/apple_music_artist_album_resolver_deferred_queue.csv",
));

const existingLinks = [
  ...safeReadJsonl(path.join(currentRoot, "apple_music_link_pass_v1/apple_music_links_v1.jsonl")),
  ...safeReadJsonl(path.join(currentRoot, "apple_music_try_harder_pass_v1/apple_music_try_harder_links_v1.jsonl")),
  ...safeReadJsonl(path.join(currentRoot, "apple_music_residual_track_pass_v1/apple_music_residual_track_links_v1.jsonl")),
  ...safeReadJsonl(path.join(currentRoot, "apple_music_album_variant_pass_v1/apple_music_album_variant_links_v1.jsonl")),
  ...safeReadJsonl(path.join(currentRoot, "apple_music_offline_reconciliation_pass_v1/apple_music_offline_reconciliation_links_v1.jsonl")),
  ...safeReadJsonl(path.join(currentRoot, "apple_music_artist_album_resolver_pass_v1/apple_music_artist_album_resolver_links_v1.jsonl")),
];

const linkableStatuses = new Set(["verified", "candidate_verified"]);
const existingSourceResourceKeys = new Set(
  existingLinks
    .filter((link) => linkableStatuses.has(link.match_status))
    .map((link) => sourceResourceKey(link.source_type, link.source_ref, link.apple_resource_type)),
);
const existingSidecarTrackRefs = new Set(
  existingLinks
    .filter((link) => linkableStatuses.has(link.match_status))
    .filter((link) => link.source_type === "album_sidecar_track" && link.apple_resource_type === "song")
    .map((link) => link.source_ref),
);
const sidecarTracksByAlbum = groupBy(sidecarTracks, (row) => row.candidate_identity_key);
const firstPassAlbumReviewsByRef = new Map(
  firstPassReviews
    .filter((row) => row.source_type === "graph_album")
    .map((row) => [row.source_ref, row]),
);
const artistAlbumDeferredByRef = new Map(
  artistAlbumDeferred
    .filter((row) => row.source_ref)
    .map((row) => [row.source_ref, row]),
);

const checkpoint = args.resume ? readCheckpoint() : null;
const completedAlbumRefs = new Set(checkpoint?.completed_album_refs ?? []);
const links = checkpoint?.links ?? [];
const deferred = checkpoint?.deferred ?? [];
const outputLinkKeys = new Set(links.map((link) => link.link_key));
const outputSourceResourceKeys = new Set(
  links.map((link) => sourceResourceKey(link.source_type, link.source_ref, link.apple_resource_type)),
);
const deferredKeys = new Set(deferred.map((row) => row.deferred_key));

const albumCache = new Map();
const albumTracksCache = new Map();
const searchCache = new Map();

const albumJobs = buildAlbumJobs();

console.error(JSON.stringify({
  run_version: runVersion,
  storefront: args.storefront,
  album_jobs: albumJobs.length,
  dry_run: args.dryRun,
}, null, 2));

await runPool(albumJobs.filter((job) => !completedAlbumRefs.has(job.source_ref)), args.concurrency, async (job, index) => {
  const outcome = await safelyResolveAlbum(job);
  recordOutcome(job, outcome);
  completedAlbumRefs.add(job.source_ref);
  if ((index + 1) % args.checkpointEvery === 0) writeCheckpoint("partial");
  if ((index + 1) % args.progressEvery === 0) {
    console.error(`high-confidence-album: ${index + 1}/${albumJobs.length}, links=${links.length}, deferred=${deferred.length}`);
  }
});

writeCheckpoint("complete");
writeFinalArtifacts();
if (!args.keepCheckpoint && fs.existsSync(checkpointPath)) fs.unlinkSync(checkpointPath);

function parseArgs(argv) {
  const parsed = {
    storefront: "us",
    concurrency: 4,
    progressEvery: 25,
    checkpointEvery: 25,
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
    else if (arg === "--progress-every") parsed.progressEvery = Number(argv[++index]);
    else if (arg === "--checkpoint-every") parsed.checkpointEvery = Number(argv[++index]);
    else if (arg === "--no-resume") parsed.resume = false;
    else if (arg === "--keep-checkpoint") parsed.keepCheckpoint = true;
    else if (arg === "--dry-run") parsed.dryRun = true;
    else if (arg === "--limit-albums") parsed.limitAlbums = Number(argv[++index]);
    else if (arg === "--source-ref") parsed.sourceRefs.push(argv[++index]);
  }
  if (!Number.isFinite(parsed.concurrency) || parsed.concurrency < 1) parsed.concurrency = 1;
  if (parsed.concurrency > 8) parsed.concurrency = 8;
  if (!Number.isFinite(parsed.progressEvery) || parsed.progressEvery < 1) parsed.progressEvery = 25;
  if (!Number.isFinite(parsed.checkpointEvery) || parsed.checkpointEvery < 1) parsed.checkpointEvery = parsed.progressEvery;
  return parsed;
}

function buildAlbumJobs() {
  const jobs = graphRows
    .filter((row) => row.candidate_type === "album")
    .filter((row) => !existingSourceResourceKeys.has(sourceResourceKey("graph_album", row.candidate_identity_key, "album")))
    .map((row) => {
      const firstPassReview = firstPassAlbumReviewsByRef.get(row.candidate_identity_key);
      const artistAlbumReview = artistAlbumDeferredByRef.get(row.candidate_identity_key);
      return {
        source_ref: row.candidate_identity_key,
        source_type: "graph_album",
        source_candidate_type: "album",
        artist_display_name: row.artist_display_name,
        title: row.title,
        year: row.year,
        archetype_ids: row.archetype_ids ?? [],
        archetypes: row.archetypes ?? [],
        sidecar_tracks: sidecarTracksByAlbum.get(row.candidate_identity_key) ?? [],
        first_pass_review_reason: firstPassReview?.review_reason ?? "",
        first_pass_best_score: firstPassReview?.best_score ?? "",
        prior_best_candidate_id: artistAlbumReview?.best_candidate_id ?? "",
        prior_best_candidate_title: artistAlbumReview?.best_candidate_title ?? "",
      };
    })
    .sort((a, b) => a.source_ref.localeCompare(b.source_ref));

  const filtered = args.sourceRefs.length
    ? jobs.filter((job) => args.sourceRefs.includes(job.source_ref))
    : jobs;
  return Number.isFinite(args.limitAlbums) ? filtered.slice(0, args.limitAlbums) : filtered;
}

async function safelyResolveAlbum(job) {
  try {
    if (args.dryRun) return { kind: "deferred", reason: "dry_run_no_catalog_call" };
    return await resolveAlbum(job);
  } catch (error) {
    return { kind: "deferred", reason: "high_confidence_album_request_error", error_message: errorMessage(error) };
  }
}

async function resolveAlbum(job) {
  const candidates = [];
  const seenIds = new Set();

  for (const seedId of seedAlbumIds(job)) {
    const item = await fetchAlbum(seedId);
    if (!item?.id || seenIds.has(item.id)) continue;
    seenIds.add(item.id);
    const tracks = await fetchAlbumTracks(item.id);
    candidates.push(scoreAlbumCandidate(job, item, tracks, 0, "prior_best_candidate_id"));
  }

  for (const term of buildSearchTerms(job)) {
    const searchResults = await searchAlbums(term);
    for (const [index, item] of searchResults.entries()) {
      if (!item?.id || seenIds.has(item.id)) continue;
      seenIds.add(item.id);
      if (!shouldScoreCandidate(job, item)) continue;
      const tracks = await fetchAlbumTracks(item.id);
      candidates.push(scoreAlbumCandidate(job, item, tracks, index + 1, term));
    }
  }

  candidates.sort(compareCandidatesForReview);
  const accepted = chooseCandidate(job, candidates);
  if (!accepted) {
    return {
      kind: "deferred",
      reason: "high_confidence_album_no_safe_match",
      candidate_count: candidates.length,
      best_score: candidates[0]?.score ?? "",
      best_candidate_id: candidates[0]?.item?.id ?? "",
      best_candidate_title: candidates[0]?.item?.attributes?.name ?? "",
      best_candidate_artist: candidates[0]?.item?.attributes?.artistName ?? "",
      best_candidate_basis: candidates[0]?.acceptanceBasis ?? "",
      best_track_overlap_ratio: candidates[0]?.trackOverlapRatio?.toFixed(3) ?? "",
      error_message: "",
    };
  }

  return {
    kind: "accepted",
    accepted,
    candidate_count: candidates.length,
    links: buildLinksForAcceptedAlbum(job, accepted, candidates.length),
  };
}

function seedAlbumIds(job) {
  return uniqueValues([
    ...curatedAlbumCandidateSeeds(job.source_ref),
    job.prior_best_candidate_id,
  ].filter((value) => /^\d+$/u.test(String(value ?? ""))));
}

function curatedAlbumCandidateSeeds(sourceRef) {
  const seeds = {
    "album|various artists|frozen": ["1440618177"],
    "album|various artists|aladdin": ["1440722016"],
    "album|various artists|pulp fiction": ["1469583186"],
    "album|original broadway cast of cabaret|cabaret": ["344579157"],
    "album|original london cast of les miserables|les miserables": ["286655561"],
    "album|original broadway cast of west side story|west side story": ["186302499"],
    "album|original broadway cast of a chorus line|a chorus line": ["1041504493"],
    "album|original broadway cast of fiddler on the roof|fiddler on the roof": ["401383466", "357911383"],
    "album|original broadway cast of guys and dolls|guys and dolls": ["1469581712"],
    "album|original broadway cast of into the woods|into the woods": ["219236910"],
    "album|kiss|alive": ["1853653621"],
  };
  return seeds[sourceRef] ?? [];
}

function buildSearchTerms(job) {
  const title = String(job.title ?? "").trim();
  const artist = String(job.artist_display_name ?? "").trim();
  const strippedTitle = stripArtistFromTitle(title, artist);
  const titleWithoutSubtitle = stripSubtitle(strippedTitle);
  const terms = [
    `${artist} ${title}`,
    `${artist} ${strippedTitle}`,
    `${stripFeaturing(artist)} ${title}`,
    `${title} ${artist}`,
    `${strippedTitle} ${artist}`,
    strippedTitle,
    titleWithoutSubtitle,
  ];

  if (looksLiveLike(job)) {
    terms.push(`${artist} ${strippedTitle} live`);
    terms.push(`${strippedTitle} live`);
  }

  if (isSoundtrackOrCastJob(job)) {
    terms.push(strippedTitle);
    terms.push(`${strippedTitle} soundtrack`);
    terms.push(`${strippedTitle} original soundtrack`);
    terms.push(`${strippedTitle} original motion picture soundtrack`);
    terms.push(`${strippedTitle} original cast recording`);
    terms.push(`${strippedTitle} original broadway cast recording`);
  }

  if (isCompilationLike(title)) {
    terms.push(`${artist} greatest hits`);
    terms.push(`${artist} best of`);
    terms.push(`${artist} collection`);
  }

  return uniqueValues(terms.map((term) => term.trim()).filter(Boolean));
}

async function fetchAlbum(albumId) {
  if (albumCache.has(albumId)) return albumCache.get(albumId);
  let item = null;
  try {
    const payload = await client.catalogGet(`/v1/catalog/${encodeURIComponent(args.storefront)}/albums/${encodeURIComponent(albumId)}`, {
      "fields[albums]": "name,artistName,releaseDate",
    });
    item = payload?.data?.[0] ?? null;
  } catch {
    item = null;
  }
  albumCache.set(albumId, item);
  return item;
}

async function searchAlbums(term) {
  if (searchCache.has(term)) return searchCache.get(term);
  let items = [];
  try {
    const payload = await client.catalogGet(`/v1/catalog/${encodeURIComponent(args.storefront)}/search`, {
      term,
      types: "albums",
      limit: 25,
      "fields[albums]": "name,artistName,releaseDate",
    });
    items = payload?.results?.albums?.data ?? [];
  } catch {
    items = [];
  }
  searchCache.set(term, items);
  return items;
}

async function fetchAlbumTracks(albumId) {
  if (albumTracksCache.has(albumId)) return albumTracksCache.get(albumId);
  const allTracks = [];
  let endpoint = `/v1/catalog/${encodeURIComponent(args.storefront)}/albums/${encodeURIComponent(albumId)}/tracks`;
  let query = {
    limit: 300,
    "fields[songs]": "name,artistName,durationInMillis,discNumber,trackNumber",
  };

  try {
    for (let page = 0; page < 10; page += 1) {
      const payload = await client.catalogGet(endpoint, query);
      for (const item of payload?.data ?? []) {
        if (item.type === "songs" && item.id) allTracks.push(item);
      }
      if (!payload?.next) break;
      const next = new URL(payload.next, "https://api.music.apple.com");
      endpoint = next.pathname;
      query = Object.fromEntries(next.searchParams.entries());
    }
  } catch {
    allTracks.length = 0;
  }

  albumTracksCache.set(albumId, allTracks);
  return allTracks;
}

function shouldScoreCandidate(job, item) {
  const attrs = item.attributes ?? {};
  const expectedTitleCore = normalizeTitleCore(job.title);
  const candidateTitleCore = normalizeTitleCore(attrs.name);
  if (containsUseful(candidateTitleCore, expectedTitleCore)) return true;
  if (containsUseful(expectedTitleCore, candidateTitleCore) && candidateTitleCore.length >= 5) return true;
  if (compatibleCensoredTitles(job.title, attrs.name)) return true;
  if (isSoundtrackOrCastJob(job)) return true;
  if (looksLiveLike(job) || looksLiveLike({ title: attrs.name, artist_display_name: attrs.artistName, archetype_ids: [] })) return true;
  return compatibleNames(normalize(attrs.artistName), normalize(job.artist_display_name));
}

function scoreAlbumCandidate(job, item, appleTracks, searchRank, searchTerm) {
  const attrs = item.attributes ?? {};
  const expectedTitle = normalize(job.title);
  const expectedTitleCore = normalizeTitleCore(job.title);
  const expectedTitleLoose = normalizeLooseTitle(job.title);
  const expectedArtistStrippedCore = normalizeTitleCore(stripArtistFromTitle(job.title, job.artist_display_name));
  const candidateTitle = normalize(attrs.name);
  const candidateTitleCore = normalizeTitleCore(attrs.name);
  const candidateTitleLoose = normalizeLooseTitle(attrs.name);
  const expectedArtist = normalize(job.artist_display_name);
  const candidateArtist = normalize(attrs.artistName);
  const candidateYear = yearFromReleaseDate(attrs.releaseDate);
  const expectedYear = Number(job.year);
  const yearDelta = Number.isFinite(expectedYear) && candidateYear !== null
    ? Math.abs(expectedYear - candidateYear)
    : 99;
  const titleExact = candidateTitle === expectedTitle;
  const titleCoreExact = expectedTitleCore && candidateTitleCore === expectedTitleCore;
  const titleLooseExact = expectedTitleLoose && candidateTitleLoose === expectedTitleLoose;
  const artistStrippedTitleMatch = expectedArtistStrippedCore && candidateTitleCore === expectedArtistStrippedCore;
  const titleContains = containsUseful(candidateTitleCore, expectedTitleCore)
    || containsUseful(expectedTitleCore, candidateTitleCore);
  const titleCompatible = titleExact
    || titleCoreExact
    || titleLooseExact
    || artistStrippedTitleMatch
    || titleContains
    || compatibleCensoredTitles(job.title, attrs.name);
  const soundtrackOrCast = isSoundtrackOrCastJob(job);
  const provenanceScore = provenancePoints(job, attrs);
  const curatedSeed = curatedAlbumCandidateSeeds(job.source_ref).includes(String(item.id));
  const artistCompatible = compatibleNames(candidateArtist, expectedArtist)
    || soundtrackOrCast
    || isVariousOrCast(attrs.artistName);
  const editionClass = classifyEdition(attrs.name);
  const overlap = tracklistOverlap(job.sidecar_tracks, appleTracks);
  const trackCountClose = job.sidecar_tracks.length > 0
    && appleTracks.length > 0
    && Math.abs(appleTracks.length - job.sidecar_tracks.length) <= 2;

  let score = 0;
  if (titleExact) score += 50;
  else if (titleCoreExact) score += 46;
  else if (titleLooseExact) score += 44;
  else if (artistStrippedTitleMatch) score += 38;
  else if (titleContains) score += 28;
  else if (compatibleCensoredTitles(job.title, attrs.name)) score += 32;
  if (artistCompatible) score += soundtrackOrCast && !compatibleNames(candidateArtist, expectedArtist) ? 16 : 24;
  score += provenanceScore;
  if (curatedSeed) score += 30;
  if (yearDelta === 0) score += 16;
  else if (yearDelta <= 1) score += 13;
  else if (yearDelta <= 3) score += 8;
  else if (yearDelta <= 20 && (editionClass === "remaster" || editionClass === "expanded")) score += 2;
  score += Math.round(overlap.ratio * 85);
  if (overlap.orderedAnchorMatches >= 2) score += 10;
  if (trackCountClose) score += 8;
  score += editionPreferencePoints(editionClass);
  score -= Math.min(Number(searchRank) || 0, 10);

  const candidate = {
    item,
    appleTracks,
    searchRank,
    searchTerm,
    score,
    titleExact,
    titleCoreExact,
    titleLooseExact,
    artistStrippedTitleMatch,
    titleContains,
    titleCompatible,
    artistCompatible,
    soundtrackOrCast,
    provenanceScore,
    curatedSeed,
    yearDelta,
    editionClass,
    trackOverlapRatio: overlap.ratio,
    trackOverlapCount: overlap.count,
    orderedAnchorMatches: overlap.orderedAnchorMatches,
    trackCountClose,
    acceptanceBasis: "",
  };
  candidate.acceptanceBasis = acceptanceBasis(job, candidate);
  return candidate;
}

function chooseCandidate(job, candidates) {
  const accepted = candidates
    .map((candidate) => ({ candidate, basis: acceptanceBasis(job, candidate) }))
    .filter(({ basis }) => basis)
    .sort((a, b) => compareAcceptedCandidates(a.candidate, b.candidate));

  if (!accepted.length) return null;
  const [best, second] = accepted;
  if (best.candidate.curatedSeed) return acceptedCandidate(best.candidate, best.basis);
  if (second && best.candidate.score - second.candidate.score < 8) {
    if (best.candidate.trackOverlapRatio >= 0.85 && best.candidate.trackOverlapCount >= 8 && best.candidate.provenanceScore >= 15) {
      return acceptedCandidate(best.candidate, best.basis);
    }
    const bestTitleStrong = best.candidate.titleExact || best.candidate.titleCoreExact || best.candidate.titleLooseExact;
    const secondTitleStrong = second.candidate.titleExact || second.candidate.titleCoreExact || second.candidate.titleLooseExact;
    if (!bestTitleStrong || secondTitleStrong) return null;
  }

  return acceptedCandidate(best.candidate, best.basis);
}

function acceptanceBasis(job, candidate) {
  const hasSidecar = job.sidecar_tracks.length > 0;
  const minUsefulCount = Math.min(8, Math.max(3, Math.ceil(job.sidecar_tracks.length * 0.45)));
  const titleStrong = candidate.titleExact || candidate.titleCoreExact || candidate.titleLooseExact;
  const titleVariant = titleStrong
    || candidate.titleContains
    || candidate.artistStrippedTitleMatch
    || compatibleCensoredTitles(job.title, candidate.item.attributes?.name);
  const tracklistStrong = candidate.trackOverlapRatio >= 0.7
    && candidate.trackOverlapCount >= Math.min(8, Math.max(4, Math.ceil(job.sidecar_tracks.length * 0.5)));
  const tracklistVeryStrong = candidate.trackOverlapRatio >= 0.82
    && candidate.trackOverlapCount >= Math.min(10, Math.max(5, Math.ceil(job.sidecar_tracks.length * 0.6)));
  const orderedSupport = candidate.orderedAnchorMatches >= 2 || candidate.trackCountClose;
  const yearAcceptable = candidate.yearDelta <= 3
    || candidate.yearDelta === 99
    || ((candidate.editionClass === "remaster" || candidate.editionClass === "expanded") && candidate.trackOverlapCount >= minUsefulCount);

  if (candidate.editionClass === "single") return "";
  if (hasOriginalCastIntent(job) && candidate.yearDelta > 5 && candidate.provenanceScore < 20 && !candidate.curatedSeed) return "";

  if (candidate.curatedSeed && titleVariant && candidate.trackOverlapRatio >= 0.65 && candidate.trackOverlapCount >= 4) {
    return "high_confidence_curated_seed_tracklist_auto_match";
  }

  if (
    candidate.curatedSeed
    && candidate.soundtrackOrCast
    && titleVariant
    && candidate.yearDelta <= 3
    && candidate.provenanceScore >= 20
    && candidate.trackOverlapCount === 0
  ) {
    return "high_confidence_curated_seed_title_year_auto_match";
  }

  if (hasSidecar && titleStrong && candidate.artistCompatible && candidate.trackOverlapRatio >= 0.42 && candidate.trackOverlapCount >= 3) {
    return "high_confidence_title_tracklist_auto_match";
  }

  if (hasSidecar && titleVariant && candidate.artistCompatible && tracklistStrong && orderedSupport && yearAcceptable) {
    if (compatibleCensoredTitles(job.title, candidate.item.attributes?.name)) {
      return "high_confidence_censored_title_tracklist_auto_match";
    }
    if (candidate.editionClass === "expanded" || candidate.editionClass === "remaster") {
      return "high_confidence_edition_variant_tracklist_auto_match";
    }
    return "high_confidence_title_variant_tracklist_auto_match";
  }

  if (hasSidecar && candidate.soundtrackOrCast && titleVariant && candidate.trackOverlapRatio >= 0.55 && candidate.trackOverlapCount >= 4 && orderedSupport) {
    return "high_confidence_soundtrack_title_tracklist_auto_match";
  }

  if (hasSidecar && candidate.soundtrackOrCast && titleVariant && candidate.provenanceScore >= 20 && candidate.trackOverlapRatio >= 0.72 && candidate.trackOverlapCount >= 8) {
    return "high_confidence_soundtrack_provenance_tracklist_auto_match";
  }

  if (hasSidecar && candidate.artistCompatible && tracklistVeryStrong && orderedSupport && candidate.yearDelta <= 20) {
    return "high_confidence_alternate_title_tracklist_auto_match";
  }

  if (!hasSidecar && titleStrong && candidate.artistCompatible && candidate.yearDelta <= 1) {
    return "high_confidence_title_year_auto_match";
  }

  return "";
}

function acceptedCandidate(candidate, matchBasis) {
  return {
    ...candidate,
    match_basis: matchBasis,
    confidence: candidate.trackOverlapRatio >= 0.78 || candidate.titleExact || candidate.titleCoreExact ? "high" : "medium",
  };
}

function buildLinksForAcceptedAlbum(job, accepted, candidateCount) {
  const albumFields = {
    apple_catalog_id: accepted.item.id,
    apple_resource_type: "album",
    match_status: accepted.confidence === "high" ? "verified" : "candidate_verified",
    match_basis: accepted.match_basis,
    confidence: accepted.confidence,
    result_rank: accepted.searchRank,
    title_match: titleMatchLabel(accepted),
    artist_match: accepted.artistCompatible ? "compatible_or_not_required" : "tracklist_supported",
    year_delta: accepted.yearDelta,
    warnings: warningForAcceptedAlbum(accepted),
    edition_class: accepted.editionClass,
    track_overlap_ratio: accepted.trackOverlapRatio.toFixed(3),
    track_overlap_count: accepted.trackOverlapCount,
    ordered_anchor_matches: accepted.orderedAnchorMatches,
    candidate_count: candidateCount,
    search_term: accepted.searchTerm,
  };

  const output = [];
  output.push(...makeAlbumLinks(job, albumFields));
  output.push(...resolveAcceptedAlbumTracks(job, accepted));
  return output;
}

function makeAlbumLinks(job, fields) {
  const rows = [];
  for (const [sourceType, candidateType] of [["graph_album", "album"], ["album_sidecar_album", "album"]]) {
    const key = sourceResourceKey(sourceType, job.source_ref, fields.apple_resource_type);
    if (existingSourceResourceKeys.has(key) || outputSourceResourceKeys.has(key)) continue;
    rows.push(makeLink(job, sourceType, candidateType, fields));
  }
  return rows;
}

function warningForAcceptedAlbum(accepted) {
  const warnings = [];
  if (accepted.editionClass === "expanded") warnings.push("expanded_or_deluxe_accepted_after_high_confidence_evidence");
  if (accepted.editionClass === "remaster") warnings.push("remaster_accepted");
  if (accepted.yearDelta > 3 && accepted.yearDelta !== 99) warnings.push("release_year_differs");
  if (accepted.match_basis === "high_confidence_alternate_title_tracklist_auto_match") warnings.push("alternate_album_title_accepted_by_strong_tracklist");
  if (accepted.match_basis === "high_confidence_soundtrack_title_tracklist_auto_match") warnings.push("soundtrack_or_cast_artist_match_not_required");
  return warnings.join(";");
}

function titleMatchLabel(accepted) {
  if (accepted.titleExact) return "exact_normalized";
  if (accepted.titleCoreExact) return "core_exact_normalized";
  if (accepted.titleLooseExact) return "loose_exact_normalized";
  if (accepted.artistStrippedTitleMatch) return "artist_name_stripped_exact";
  if (accepted.titleContains) return "contains_normalized";
  return "tracklist_supported";
}

function makeLink(job, sourceType, sourceCandidateType, fields) {
  return {
    link_key: `${sourceType}:${job.source_ref}:apple_music:${fields.apple_resource_type}:${fields.apple_catalog_id}:${args.storefront}`,
    run_version: runVersion,
    source_ref: job.source_ref,
    source_type: sourceType,
    source_candidate_type: sourceCandidateType,
    external_catalog: "apple_music",
    apple_catalog_id: fields.apple_catalog_id,
    apple_resource_type: fields.apple_resource_type,
    storefront: args.storefront,
    match_status: fields.match_status,
    match_basis: fields.match_basis,
    confidence: fields.confidence,
    result_rank: fields.result_rank,
    title_match: fields.title_match,
    artist_match: fields.artist_match,
    year_delta: fields.year_delta,
    warnings: fields.warnings,
    edition_class: fields.edition_class,
    track_overlap_ratio: fields.track_overlap_ratio,
    track_overlap_count: fields.track_overlap_count,
    ordered_anchor_matches: fields.ordered_anchor_matches,
    candidate_count: fields.candidate_count,
    search_term: fields.search_term,
    prior_review_reason: job.first_pass_review_reason,
    prior_best_score: job.first_pass_best_score,
    prior_best_candidate_id: job.prior_best_candidate_id,
    prior_best_candidate_title: job.prior_best_candidate_title,
    verified_at: new Date().toISOString(),
    raw_payload_persisted: false,
  };
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
      .map((track) => scoreTrackCandidate(row, track, accepted.soundtrackOrCast))
      .sort((a, b) => b.score - a.score);
    const best = scored[0];
    const second = scored[1];
    if (!best || !isTrackAutoAccept(best, second, accepted.soundtrackOrCast)) continue;
    usedAppleIds.add(best.track.apple_catalog_id);
    output.push({
      link_key: `album_sidecar_track:${sourceRef}:apple_music:song:${best.track.apple_catalog_id}:${args.storefront}`,
      run_version: runVersion,
      source_ref: sourceRef,
      source_type: "album_sidecar_track",
      source_candidate_type: "track",
      external_catalog: "apple_music",
      apple_catalog_id: best.track.apple_catalog_id,
      apple_resource_type: "song",
      storefront: args.storefront,
      match_status: best.confidence === "high" ? "verified" : "candidate_verified",
      match_basis: "high_confidence_album_track_auto_match",
      confidence: best.confidence,
      title_match: best.title_match,
      artist_match: best.artist_match,
      warnings: best.warnings,
      apple_album_id: accepted.item.id,
      album_match_basis: accepted.match_basis,
      track_score: best.score,
      duration_delta_ms: best.duration_delta_ms,
      verified_at: new Date().toISOString(),
      raw_payload_persisted: false,
    });
  }
  return output;
}

function recordOutcome(job, outcome) {
  if (outcome.kind === "accepted") {
    for (const link of outcome.links) {
      const sourceKey = sourceResourceKey(link.source_type, link.source_ref, link.apple_resource_type);
      if (outputLinkKeys.has(link.link_key) || existingSourceResourceKeys.has(sourceKey) || outputSourceResourceKeys.has(sourceKey)) continue;
      links.push(link);
      outputLinkKeys.add(link.link_key);
      outputSourceResourceKeys.add(sourceKey);
    }
    return;
  }

  const row = {
    deferred_key: `graph_album:${job.source_ref}:${outcome.reason}`,
    run_version: runVersion,
    source_ref: job.source_ref,
    source_type: "graph_album",
    source_candidate_type: "album",
    artist_display_name: job.artist_display_name,
    title: job.title,
    year: job.year,
    storefront: args.storefront,
    deferred_reason: outcome.reason,
    candidate_count: outcome.candidate_count ?? "",
    best_score: outcome.best_score ?? "",
    best_candidate_id: outcome.best_candidate_id ?? "",
    best_candidate_title: outcome.best_candidate_title ?? "",
    best_candidate_artist: outcome.best_candidate_artist ?? "",
    best_candidate_basis: outcome.best_candidate_basis ?? "",
    best_track_overlap_ratio: outcome.best_track_overlap_ratio ?? "",
    error_message: outcome.error_message ?? "",
    prior_review_reason: job.first_pass_review_reason,
    prior_best_candidate_id: job.prior_best_candidate_id,
    raw_payload_persisted: false,
  };
  if (!deferredKeys.has(row.deferred_key)) {
    deferred.push(row);
    deferredKeys.add(row.deferred_key);
  }
}

function tracklistOverlap(sidecarRows, appleTracks) {
  if (!sidecarRows.length || !appleTracks.length) return { count: 0, ratio: 0, orderedAnchorMatches: 0 };
  const appleTitleCores = new Set(appleTracks.map((item) => normalizeTitleCore(item.attributes?.name)).filter(Boolean));
  const appleTitleLoose = new Set(appleTracks.map((item) => normalizeLooseTitle(item.attributes?.name)).filter(Boolean));
  let count = 0;
  for (const row of sidecarRows) {
    const titleCore = normalizeTitleCore(row.track_title);
    const titleLoose = normalizeLooseTitle(row.track_title);
    if ((titleCore && appleTitleCores.has(titleCore)) || (titleLoose && appleTitleLoose.has(titleLoose))) count += 1;
  }

  const anchors = anchorRows(sidecarRows);
  let orderedAnchorMatches = 0;
  for (const row of anchors) {
    const appleAtPosition = appleTracks.find((item) => (
      Number(item.attributes?.discNumber) === Number(row.disc_number)
      && Number(item.attributes?.trackNumber) === Number(row.track_number)
    ));
    if (!appleAtPosition) continue;
    const appleCore = normalizeTitleCore(appleAtPosition.attributes?.name);
    const appleLoose = normalizeLooseTitle(appleAtPosition.attributes?.name);
    const expectedCore = normalizeTitleCore(row.track_title);
    const expectedLoose = normalizeLooseTitle(row.track_title);
    if ((appleCore && appleCore === expectedCore) || (appleLoose && appleLoose === expectedLoose)) {
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
    title_loose: normalizeLooseTitle(attrs.name),
    artist_norm: normalize(attrs.artistName),
    disc_number: numberOrNull(attrs.discNumber),
    track_number: numberOrNull(attrs.trackNumber),
    duration_ms: numberOrNull(attrs.durationInMillis),
  };
}

function scoreTrackCandidate(row, track, artistOptional) {
  const expectedTitle = normalize(row.track_title);
  const expectedTitleCore = normalizeTitleCore(row.track_title);
  const expectedTitleLoose = normalizeLooseTitle(row.track_title);
  const expectedArtist = normalize(row.track_artist_name || row.artist_display_name);
  const expectedDisc = numberOrNull(row.disc_number);
  const expectedTrack = numberOrNull(row.track_number);
  const expectedDuration = numberOrNull(row.duration_ms);
  const positionExact = expectedDisc === track.disc_number && expectedTrack === track.track_number;
  const titleExact = expectedTitle === track.title_norm;
  const titleCoreExact = expectedTitleCore && expectedTitleCore === track.title_core;
  const titleLooseExact = expectedTitleLoose && expectedTitleLoose === track.title_loose;
  const titleCompatible = titleExact || titleCoreExact || titleLooseExact || containsUseful(track.title_core, expectedTitleCore);
  const artistCompatible = artistOptional || compatibleNames(track.artist_norm, expectedArtist);
  const durationDelta = expectedDuration !== null && track.duration_ms !== null
    ? Math.abs(expectedDuration - track.duration_ms)
    : null;
  let score = 0;
  if (positionExact) score += 34;
  if (titleExact) score += 42;
  else if (titleCoreExact) score += 38;
  else if (titleLooseExact) score += 36;
  else if (titleCompatible) score += 24;
  if (artistCompatible) score += artistOptional ? 8 : 14;
  if (durationDelta !== null && durationDelta <= 5000) score += 14;
  else if (durationDelta !== null && durationDelta <= 15000) score += 10;
  score -= Math.min(track.album_track_index, 5);
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
    artist_match: artistCompatible ? (artistOptional ? "not_required" : "compatible_normalized") : "not_matched",
    confidence: score >= 86 && (titleExact || titleCoreExact || titleLooseExact) ? "high" : "medium",
    warnings: "",
  };
}

function isTrackAutoAccept(best, second, artistOptional) {
  if (best.positionExact && (best.titleExact || best.titleCoreExact || best.titleLooseExact)) return true;
  if (best.positionExact && best.titleCompatible && best.duration_delta_ms !== "" && best.duration_delta_ms <= 15000) return true;
  if ((best.titleExact || best.titleCoreExact || best.titleLooseExact) && best.artistCompatible && best.score >= (artistOptional ? 76 : 82) && (!second || best.score - second.score >= 10)) return true;
  return false;
}

function compareCandidatesForReview(a, b) {
  return b.score - a.score
    || b.trackOverlapRatio - a.trackOverlapRatio
    || b.trackOverlapCount - a.trackOverlapCount
    || editionRank(a.editionClass) - editionRank(b.editionClass)
    || a.yearDelta - b.yearDelta;
}

function compareAcceptedCandidates(a, b) {
  return Number(b.curatedSeed) - Number(a.curatedSeed)
    || b.provenanceScore - a.provenanceScore
    || b.score - a.score
    || b.trackOverlapRatio - a.trackOverlapRatio
    || b.trackOverlapCount - a.trackOverlapCount
    || a.yearDelta - b.yearDelta
    || editionRank(a.editionClass) - editionRank(b.editionClass);
}

function writeCheckpoint(status) {
  const value = {
    run_version: runVersion,
    status,
    storefront: args.storefront,
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
    "best_candidate_id",
    "best_candidate_title",
    "best_candidate_artist",
    "best_candidate_basis",
    "best_track_overlap_ratio",
    "error_message",
    "prior_review_reason",
    "prior_best_candidate_id",
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
    storefront: args.storefront,
    policy: {
      raw_apple_payloads_persisted: false,
      persisted_catalog_fields: ["apple_catalog_id", "apple_resource_type", "storefront", "match metadata"],
      excluded_persistent_fields: ["artwork", "previews", "lyrics", "raw_catalog_payload", "music_user_token"],
    },
    inputs: {
      graph_linking_node_set: "data/canonical_graph/current/graph_linking_node_set.json",
      album_track_sidecar_tracks: "data/canonical_graph/current/album_track_sidecar_tracks.csv",
      existing_link_passes: [
        "apple_music_link_pass_v1",
        "apple_music_try_harder_pass_v1",
        "apple_music_residual_track_pass_v1",
        "apple_music_album_variant_pass_v1",
        "apple_music_offline_reconciliation_pass_v1",
        "apple_music_artist_album_resolver_pass_v1",
      ],
    },
    counts: {
      album_jobs_completed: completedAlbumRefs.size,
      new_links_total: sortedLinks.length,
      deferred_total: sortedDeferred.length,
      new_links_by_source_type: countBy(sortedLinks, "source_type"),
      new_links_by_resource_type: countBy(sortedLinks, "apple_resource_type"),
      new_links_by_match_basis: countBy(sortedLinks, "match_basis"),
      album_links_by_edition_class: countBy(sortedLinks.filter((link) => link.apple_resource_type === "album"), "edition_class"),
      deferred_by_reason: countBy(sortedDeferred, "deferred_reason"),
    },
  };
}

function buildManifest(summary) {
  return `# Apple Music High Confidence Album Pass v1

Generated: ${summary.generated_at}

Status: \`${summary.status}\`

Storefront: \`${summary.storefront}\`

## Policy

- Raw Apple payloads persisted: \`false\`
- Apple album and album track payloads are used only as transient candidate pools.
- Durable output stores Apple catalog IDs, resource type, storefront, source refs, match status, and compact matching metadata only.

## Intent

This pass targets graph albums still missing Apple album IDs after the conservative search, variant, offline, and artist-album passes. It deliberately accepts high-confidence remaster, expanded, censored-title, live-title, and alternate-title matches when title normalization and/or tracklist evidence is strong. For soundtrack, cast, and Various Artists-style album containers, album artist name mismatch is not treated as a blocker when title and tracklist evidence are strong.

## Counts

- Album jobs completed: ${summary.counts.album_jobs_completed}
- New links total: ${summary.counts.new_links_total}
- Deferred rows: ${summary.counts.deferred_total}

## New Links By Source Type

${tableFromCounts(summary.counts.new_links_by_source_type)}

## New Links By Match Basis

${tableFromCounts(summary.counts.new_links_by_match_basis)}

## Album Links By Edition Class

${tableFromCounts(summary.counts.album_links_by_edition_class)}

## Deferred By Reason

${tableFromCounts(summary.counts.deferred_by_reason)}
`;
}

function sourceResourceKey(sourceType, sourceRef, resourceType) {
  return `${sourceType}\t${sourceRef}\t${resourceType}`;
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

function isSoundtrackOrCastJob(job) {
  const artist = normalize(job.artist_display_name);
  const title = normalize(job.title);
  const archetypeIds = new Set((job.archetype_ids ?? []).map(String));
  return isVariousOrCast(job.artist_display_name)
    || archetypeIds.has("104")
    || archetypeIds.has("105")
    || archetypeIds.has("106")
    || /\b(soundtrack|score|cast|disney)\b/u.test(`${artist} ${title}`);
}

function isVariousOrCast(value) {
  const text = normalize(value);
  return text === "various artists"
    || /\boriginal\b.*\bcast\b/u.test(text)
    || /\bcast\b/u.test(text)
    || /\bsoundtrack\b/u.test(text);
}

function hasOriginalCastIntent(job) {
  return /\boriginal\b.*\b(broadway|london)\b.*\bcast\b/iu.test(String(job.artist_display_name ?? ""));
}

function provenancePoints(job, attrs) {
  const candidateText = normalize(`${attrs.name ?? ""} ${attrs.artistName ?? ""}`);
  const titleText = normalize(attrs.name);
  const artistText = normalize(job.artist_display_name);
  let score = 0;

  if (/\boriginal broadway cast\b/iu.test(String(job.artist_display_name ?? ""))) {
    if (/\boriginal broadway cast\b/u.test(candidateText)) score += 35;
    if (/\bbroadway cast recording\b/u.test(candidateText)) score += 20;
    if (/\b(new|revival|2022|spanish|london theatre orchestra)\b/u.test(candidateText)) score -= 35;
  }

  if (/\boriginal london cast\b/iu.test(String(job.artist_display_name ?? ""))) {
    if (/\boriginal\b/u.test(candidateText) && /\blondon cast\b/u.test(candidateText)) score += 40;
    if (/\b1985\b/u.test(candidateText)) score += 20;
    if (/\bbroadway cast\b/u.test(candidateText)) score -= 30;
  }

  if (/\bvarious artists\b/u.test(artistText) || /soundtrack/iu.test(String(job.title ?? "")) || isSoundtrackOrCastJob(job)) {
    if (/\boriginal motion picture soundtrack\b/u.test(candidateText)) score += 22;
    else if (/\boriginal soundtrack\b/u.test(candidateText)) score += 14;
    if (titleText && containsUseful(titleText, normalizeTitleCore(job.title))) score += 5;
  }

  return score;
}

function looksLiveLike(job) {
  return /\b(live|at|in concert|carnegie|apollo|fillmore|folsom|newport|budokan|cheetah|terlingua|azteca)\b/iu.test(String(job.title ?? ""));
}

function isCompilationLike(value) {
  return /\b(best of|greatest hits|collection|anthology|complete|singles|golden hits|vault)\b/iu.test(String(value ?? ""));
}

function stripArtistFromTitle(title, artist) {
  const normalizedArtist = normalize(artist);
  const normalizedTitle = normalize(title);
  if (!normalizedArtist || !normalizedTitle.includes(normalizedArtist)) return title;
  const artistWords = normalizedArtist.split(" ").filter(Boolean);
  return String(title ?? "")
    .split(/\s+/u)
    .filter((word) => !artistWords.includes(normalize(word)))
    .join(" ")
    .replace(/\s+/gu, " ")
    .trim() || title;
}

function stripSubtitle(value) {
  return String(value ?? "").split(/\s[-:]\s/u)[0].trim();
}

function stripFeaturing(value) {
  return String(value ?? "")
    .replace(/\s+(feat\.?|ft\.?|featuring)\s+.*$/iu, "")
    .trim();
}

function classifyEdition(value) {
  const text = String(value ?? "").toLowerCase();
  if (/\bsingle\b/u.test(text)) return "single";
  if (/\bep\b/u.test(text)) return "ep";
  if (/\b(super deluxe|deluxe|expanded|bonus tracks?|anniversary|collector|legacy edition|complete recordings|complete|40th anniversary)\b/u.test(text)) return "expanded";
  if (/\b(remaster(ed)?|remastered|stereo mix|mono mix|mix\/master)\b/u.test(text)) return "remaster";
  return "original_like";
}

function editionPreferencePoints(editionClass) {
  if (editionClass === "original_like") return 8;
  if (editionClass === "remaster") return 4;
  if (editionClass === "expanded") return -3;
  if (editionClass === "ep") return -7;
  return -25;
}

function editionRank(editionClass) {
  if (editionClass === "original_like") return 0;
  if (editionClass === "remaster") return 1;
  if (editionClass === "expanded") return 2;
  if (editionClass === "ep") return 3;
  return 4;
}

function yearFromReleaseDate(value) {
  const year = Number(String(value ?? "").slice(0, 4));
  return Number.isFinite(year) ? year : null;
}

function normalize(value) {
  return String(value ?? "")
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/gu, "")
    .toLowerCase()
    .replace(/&/gu, " and ")
    .replace(/\+/gu, " plus ")
    .replace(/[@$]/gu, " ")
    .replace(/[^a-z0-9]+/gu, " ")
    .trim()
    .replace(/\bthe\b/gu, "")
    .replace(/\s+/gu, " ")
    .trim();
}

function normalizeTitleCore(value) {
  return normalize(value)
    .replace(/\b(remaster(ed)?|remastered|mono|stereo|single|album|version|edit|deluxe|expanded|anniversary|bonus|tracks?|explicit|clean|edition|reissue|original|collector|complete|legacy|motion|picture|score|soundtrack|recording|cast|broadway|live|with|vol|volume|mix|master)\b/gu, " ")
    .replace(/\b(19|20)\d{2}\b/gu, " ")
    .replace(/\s+/gu, " ")
    .trim();
}

function normalizeLooseTitle(value) {
  return normalizeTitleCore(value)
    .replace(/\bf k\b/gu, "fuck")
    .replace(/\bf ck\b/gu, "fuck")
    .replace(/\bs t\b/gu, "shit")
    .replace(/\bu s a\b/gu, "usa")
    .replace(/\byoure\b/gu, "you re")
    .replace(/\bwhos\b/gu, "who s")
    .replace(/\bmacdougal\b/gu, "mac dougal")
    .replace(/\s+/gu, " ")
    .trim();
}

function compatibleCensoredTitles(expected, candidate) {
  const expectedLoose = normalizeLooseTitle(expected);
  const candidateLoose = normalizeLooseTitle(candidate);
  if (!expectedLoose || !candidateLoose) return false;
  if (expectedLoose === candidateLoose) return true;
  const expectedHasExplicit = /\b(fuck|fucking|shit|bitch|pussy)\b/iu.test(String(expected ?? ""));
  const candidateHasCensor = /\*{1,}/u.test(String(candidate ?? ""));
  return expectedHasExplicit && candidateHasCensor && containsUseful(candidateLoose, expectedLoose);
}

function compatibleNames(candidate, expected) {
  if (!candidate || !expected) return false;
  return candidate === expected || candidate.includes(expected) || expected.includes(candidate);
}

function containsUseful(candidate, expected) {
  if (!candidate || !expected || expected.length < 5 || candidate.length < 5) return false;
  return candidate.includes(expected) || expected.includes(candidate);
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
  return String(value ?? "").replace(/\|/gu, "\\|");
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
  if (/[",\n\r]/u.test(text)) return `"${text.replace(/"/gu, "\"\"")}"`;
  return text;
}

function errorMessage(error) {
  return error instanceof Error ? error.message : String(error);
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
