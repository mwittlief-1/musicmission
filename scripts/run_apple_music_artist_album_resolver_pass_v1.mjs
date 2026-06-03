#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { createAppleMusicCatalogClient } from "./lib/appleMusicCatalogClient.mjs";

const repoRoot = process.cwd();
const currentRoot = path.join(repoRoot, "data/canonical_graph/current");
const outputRoot = path.join(currentRoot, "apple_music_artist_album_resolver_pass_v1");
const runVersion = "apple_music_artist_album_resolver_pass_v1";

const args = parseArgs(process.argv.slice(2));
const client = createAppleMusicCatalogClient({
  storefront: args.storefront,
  maxRetries: 8,
  retryBaseDelayMs: 1000,
  retryMaxDelayMs: 60000,
  timeoutMs: 60000,
});

fs.mkdirSync(outputRoot, { recursive: true });

const linksPath = path.join(outputRoot, "apple_music_artist_album_resolver_links_v1.jsonl");
const deferredPath = path.join(outputRoot, "apple_music_artist_album_resolver_deferred_queue.csv");
const summaryPath = path.join(outputRoot, "apple_music_artist_album_resolver_summary.json");
const manifestPath = path.join(outputRoot, "apple_music_artist_album_resolver_manifest.md");
const checkpointPath = path.join(outputRoot, "apple_music_artist_album_resolver_pass_v1.checkpoint.json");

const graphRows = readJson(path.join(currentRoot, "graph_linking_node_set.json")).rows;
const sidecarTracks = readCsv(path.join(currentRoot, "album_track_sidecar_tracks.csv"));
const firstPassReviews = readCsv(path.join(currentRoot, "apple_music_link_pass_v1/apple_music_manual_review_queue.csv"));
const existingLinks = [
  ...safeReadJsonl(path.join(currentRoot, "apple_music_link_pass_v1/apple_music_links_v1.jsonl")),
  ...safeReadJsonl(path.join(currentRoot, "apple_music_try_harder_pass_v1/apple_music_try_harder_links_v1.jsonl")),
  ...safeReadJsonl(path.join(currentRoot, "apple_music_residual_track_pass_v1/apple_music_residual_track_links_v1.jsonl")),
  ...safeReadJsonl(path.join(currentRoot, "apple_music_album_variant_pass_v1/apple_music_album_variant_links_v1.jsonl")),
  ...safeReadJsonl(path.join(currentRoot, "apple_music_offline_reconciliation_pass_v1/apple_music_offline_reconciliation_links_v1.jsonl")),
];

const linkableStatuses = new Set(["verified", "candidate_verified"]);
const existingLinkKeys = new Set(
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

const checkpoint = args.resume ? readCheckpoint() : null;
const completedAlbumRefs = new Set(checkpoint?.completed_album_refs ?? []);
const links = checkpoint?.links ?? [];
const deferred = checkpoint?.deferred ?? [];
const linkKeys = new Set(links.map((link) => link.link_key));
const deferredKeys = new Set(deferred.map((row) => row.deferred_key));
const artistSearchCache = new Map(checkpoint?.artist_search_cache ?? []);
const artistAlbumsCache = new Map();
const albumTracksCache = new Map();

const artistIdIndex = buildArtistIdIndex();
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
    console.error(`artist-album: ${index + 1}/${albumJobs.length}, links=${links.length}, deferred=${deferred.length}`);
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
  const missingAlbums = graphRows
    .filter((row) => row.candidate_type === "album")
    .filter((row) => !existingLinkKeys.has(sourceResourceKey("graph_album", row.candidate_identity_key, "album")))
    .map((row) => ({
      source_ref: row.candidate_identity_key,
      source_type: "graph_album",
      source_candidate_type: "album",
      artist_display_name: row.artist_display_name,
      title: row.title,
      year: row.year,
      archetype_ids: row.archetype_ids ?? [],
      sidecar_tracks: sidecarTracksByAlbum.get(row.candidate_identity_key) ?? [],
      first_pass_review_reason: firstPassAlbumReviewsByRef.get(row.candidate_identity_key)?.review_reason ?? "",
      first_pass_best_score: firstPassAlbumReviewsByRef.get(row.candidate_identity_key)?.best_score ?? "",
    }))
    .sort((a, b) => a.source_ref.localeCompare(b.source_ref));

  const filtered = args.sourceRefs.length
    ? missingAlbums.filter((job) => args.sourceRefs.includes(job.source_ref))
    : missingAlbums;
  return Number.isFinite(args.limitAlbums) ? filtered.slice(0, args.limitAlbums) : filtered;
}

async function safelyResolveAlbum(job) {
  try {
    if (args.dryRun) return { kind: "deferred", reason: "dry_run_no_catalog_call" };
    return await resolveAlbum(job);
  } catch (error) {
    return { kind: "deferred", reason: "artist_album_resolver_request_error", error_message: errorMessage(error) };
  }
}

async function resolveAlbum(job) {
  const artist = await resolveArtist(job.artist_display_name);
  if (!artist) {
    return { kind: "deferred", reason: "artist_album_resolver_no_artist_id" };
  }

  const artistAlbums = await fetchArtistAlbums(artist.apple_artist_id);
  if (!artistAlbums.ok) {
    return {
      kind: "deferred",
      reason: "artist_album_resolver_artist_albums_request_error",
      apple_artist_id: artist.apple_artist_id,
      artist_id_source: artist.artist_id_source,
      error_message: artistAlbums.error_message,
    };
  }

  const candidates = [];
  for (const item of artistAlbums.albums) {
    const preliminary = scoreAlbumPreliminary(job, item, artist);
    if (!shouldFetchTracksForCandidate(preliminary, job)) continue;
    const appleTracks = await fetchAlbumTracks(item.id);
    candidates.push(scoreAlbumCandidate(job, item, artist, appleTracks, preliminary));
  }

  const accepted = chooseCandidate(job, candidates);
  if (!accepted) {
    return {
      kind: "deferred",
      reason: "artist_album_resolver_no_safe_album_match",
      apple_artist_id: artist.apple_artist_id,
      artist_id_source: artist.artist_id_source,
      candidate_count: candidates.length,
      best_score: candidates[0]?.score ?? "",
      best_candidate_id: candidates[0]?.item?.id ?? "",
      best_candidate_title: candidates[0]?.item?.attributes?.name ?? "",
      best_candidate_variant: candidates[0]?.edition_class ?? "",
    };
  }

  return {
    kind: "accepted",
    accepted,
    candidate_count: candidates.length,
    links: buildLinksForAcceptedAlbum(job, accepted, candidates.length),
  };
}

function buildArtistIdIndex() {
  const index = new Map();
  const artistRows = graphRows.filter((row) => row.candidate_type === "artist_anchor");
  const existingArtistLinksBySourceRef = new Map(
    existingLinks
      .filter((link) => linkableStatuses.has(link.match_status))
      .filter((link) => link.source_type === "graph_artist_anchor" && link.apple_resource_type === "artist")
      .map((link) => [link.source_ref, link]),
  );

  for (const row of artistRows) {
    const link = existingArtistLinksBySourceRef.get(row.candidate_identity_key);
    if (!link) continue;
    addArtistAlias(index, row.artist_display_name, {
      apple_artist_id: link.apple_catalog_id,
      apple_artist_name: row.artist_display_name,
      artist_id_source: "existing_graph_artist_link",
      artist_link_source_ref: row.candidate_identity_key,
      artist_link_match_basis: link.match_basis,
    });
    addArtistAlias(index, row.title, {
      apple_artist_id: link.apple_catalog_id,
      apple_artist_name: row.artist_display_name,
      artist_id_source: "existing_graph_artist_link",
      artist_link_source_ref: row.candidate_identity_key,
      artist_link_match_basis: link.match_basis,
    });
  }

  for (const override of manualArtistOverrides()) {
    for (const alias of override.aliases) {
      addArtistAlias(index, alias, {
        apple_artist_id: override.apple_artist_id,
        apple_artist_name: override.apple_artist_name,
        artist_id_source: "manual_artist_override",
        artist_link_source_ref: override.source_ref,
        artist_link_match_basis: "manual_apple_music_artist_url_review",
      });
    }
  }

  return index;
}

function manualArtistOverrides() {
  return [
    manualArtist("1378887586", "(G)I-DLE", ["(G)I-DLE", "G I-DLE", "g i dle"]),
    manualArtist("296025848", "Afrika Bambaataa & The Soul Sonic Force", ["Afrika Bambaataa & Soulsonic Force", "Afrika Bambaataa and Soulsonic Force"]),
    manualArtist("413048014", "Banda MS de Sergio Lizarraga", ["Banda MS", "Banda MS de Sergio Lizarraga"]),
    manualArtist("31937250", "Bee Gees", ["Bee Gees", "Bee Gees (early)"]),
    manualArtist("1353760", "Bill Medley", ["Bill Medley and Jennifer Warnes"]),
    manualArtist("263285435", "The Comsat Angels", ["The Comsat Angels", "Comsat Angels"]),
    manualArtist("180586", "Daryl Hall & John Oates", ["Hall & Oates", "Hall and Oates", "Daryl Hall & John Oates"]),
    manualArtist("306767183", "Hildur Gudnadottir", ["Hildur Gudnadottir", "Hildur Guðnadóttir"]),
    manualArtist("3449346", "Jackie Brenston", ["Jackie Brenston and His Delta Cats", "Jackie Brenston"]),
    manualArtist("3224341", "James Darren", ["Jimmy Darren", "James Darren"]),
    manualArtist("16749993", "Kathy Young & The Innocents", ["Kathy Young & The Innocents", "Kathy Young and The Innocents"]),
    manualArtist("3628117", "KIDZ BOP Kids", ["Kidz Bop", "KIDZ BOP Kids"]),
    manualArtist("272094455", "La Arrolladora Banda El Limon de Rene Camacho", ["La Arrolladora Banda El Limon", "La Arrolladora Banda El Limón de René Camacho"]),
    manualArtist("1808750544", "Mammoth", ["Mammoth WVH", "Mammoth"]),
    manualArtist("13431501", "Martha Reeves & The Vandellas", ["Martha and the Vandellas", "Martha Reeves & The Vandellas"]),
    manualArtist("92012", "Mos Def", ["Mos Def / Yasiin Bey", "Mos Def", "Yasiin Bey"]),
    manualArtist("258497764", "Mimi and Richard Farina", ["Richard and Mimi Farina", "Mimi and Richard Fariña"]),
    manualArtist("2133642", "The Soul Stirrers", ["Sam Cooke and The Soul Stirrers", "The Soul Stirrers"]),
    manualArtist("133520", "The Moody Blues", ["The Moody Blues", "The Moody Blues (early)"]),
  ];
}

function manualArtist(appleArtistId, appleArtistName, aliases) {
  return {
    apple_artist_id: appleArtistId,
    apple_artist_name: appleArtistName,
    aliases,
    source_ref: `manual_artist_override:${normalize(aliases[0])}`,
  };
}

function addArtistAlias(index, alias, value) {
  const key = normalize(alias);
  if (key && !index.has(key)) index.set(key, value);
}

async function resolveArtist(artistDisplayName) {
  const normalizedArtist = normalize(artistDisplayName);
  if (artistIdIndex.has(normalizedArtist)) return artistIdIndex.get(normalizedArtist);
  if (artistSearchCache.has(normalizedArtist)) return artistSearchCache.get(normalizedArtist);

  const result = await searchArtist(artistDisplayName);
  artistSearchCache.set(normalizedArtist, result);
  return result;
}

async function searchArtist(artistDisplayName) {
  const expected = normalize(artistDisplayName);
  const payload = await client.catalogSearch({
    term: artistDisplayName,
    types: "artists",
    limit: 5,
    "fields[artists]": "name,url",
  });
  const scored = (payload?.results?.artists?.data ?? [])
    .map((item, index) => {
      const candidate = normalize(item.attributes?.name);
      let score = 0;
      if (candidate === expected) score += 100;
      else if (compatibleNames(candidate, expected)) score += 75;
      score -= index;
      return { item, score };
    })
    .sort((a, b) => b.score - a.score);

  const best = scored[0];
  if (!best || best.score < 74) return null;
  return {
    apple_artist_id: best.item.id,
    apple_artist_name: best.item.attributes?.name ?? artistDisplayName,
    artist_id_source: "apple_artist_search_ephemeral",
    artist_link_source_ref: "",
    artist_link_match_basis: "artist_search_exact_or_compatible_normalized",
  };
}

async function fetchArtistAlbums(artistId) {
  if (artistAlbumsCache.has(artistId)) return artistAlbumsCache.get(artistId);

  let endpoint = `/v1/catalog/${encodeURIComponent(args.storefront)}/artists/${encodeURIComponent(artistId)}/albums`;
  let query = { limit: 100, "fields[albums]": "name,artistName,releaseDate,url" };
  const albums = [];
  const seenIds = new Set();

  for (let page = 0; page < 20; page += 1) {
    let payload;
    try {
      payload = await client.catalogGet(endpoint, query);
    } catch (error) {
      const result = { ok: false, error_message: errorMessage(error), albums };
      artistAlbumsCache.set(artistId, result);
      return result;
    }

    for (const item of payload?.data ?? []) {
      if (item?.id && !seenIds.has(item.id)) {
        seenIds.add(item.id);
        albums.push(item);
      }
    }

    if (!payload?.next) break;
    const next = new URL(payload.next, "https://api.music.apple.com");
    endpoint = next.pathname;
    query = Object.fromEntries(next.searchParams.entries());
  }

  const result = { ok: true, error_message: "", albums };
  artistAlbumsCache.set(artistId, result);
  return result;
}

async function fetchAlbumTracks(albumId) {
  if (albumTracksCache.has(albumId)) return albumTracksCache.get(albumId);
  let tracks = [];
  try {
    const payload = await client.catalogGet(`/v1/catalog/${encodeURIComponent(args.storefront)}/albums/${encodeURIComponent(albumId)}/tracks`, {
      limit: 300,
      "fields[songs]": "name,artistName,durationInMillis,discNumber,trackNumber",
    });
    tracks = (payload?.data ?? []).filter((item) => item.type === "songs" && item.id);
  } catch {
    tracks = [];
  }
  albumTracksCache.set(albumId, tracks);
  return tracks;
}

function scoreAlbumPreliminary(job, item, artist) {
  const attrs = item.attributes ?? {};
  const expectedTitle = normalize(job.title);
  const expectedTitleCore = normalizeTitleCore(job.title);
  const candidateTitle = normalize(attrs.name);
  const candidateTitleCore = normalizeTitleCore(attrs.name);
  const expectedArtist = normalize(job.artist_display_name);
  const candidateArtist = normalize(attrs.artistName);
  const candidateYear = yearFromReleaseDate(attrs.releaseDate);
  const expectedYear = Number(job.year);
  const yearDelta = Number.isFinite(expectedYear) && candidateYear !== null
    ? Math.abs(expectedYear - candidateYear)
    : 99;
  const titleExact = candidateTitle === expectedTitle;
  const titleCoreExact = expectedTitleCore && candidateTitleCore === expectedTitleCore;
  const titleContains = containsUseful(candidateTitleCore, expectedTitleCore)
    && !looksLikeNumberedSeriesCandidate(expectedTitleCore, candidateTitleCore);
  const artistCompatible = compatibleNames(candidateArtist, expectedArtist)
    || compatibleNames(candidateArtist, normalize(artist.apple_artist_name));
  const editionClass = classifyEdition(attrs.name);

  let preliminaryScore = 0;
  if (titleExact) preliminaryScore += 45;
  else if (titleCoreExact) preliminaryScore += 42;
  else if (titleContains) preliminaryScore += 24;
  if (artistCompatible) preliminaryScore += 20;
  if (yearDelta === 0) preliminaryScore += 16;
  else if (yearDelta <= 1) preliminaryScore += 12;
  else if (yearDelta <= 3) preliminaryScore += 7;
  else if (yearDelta <= 10 && editionClass === "remaster") preliminaryScore += 2;
  preliminaryScore += editionPreferencePoints(editionClass);

  return {
    item,
    artist,
    preliminaryScore,
    titleExact,
    titleCoreExact,
    titleContains,
    artistCompatible,
    yearDelta,
    editionClass,
  };
}

function shouldFetchTracksForCandidate(candidate, job) {
  if (candidate.titleExact || candidate.titleCoreExact || candidate.titleContains) return true;
  if (candidate.yearDelta <= 3 && candidate.artistCompatible) return true;
  return job.sidecar_tracks.length > 0 && candidate.preliminaryScore >= 30;
}

function scoreAlbumCandidate(job, item, artist, appleTracks, preliminary) {
  const overlap = tracklistOverlap(job.sidecar_tracks, appleTracks);
  let score = preliminary.preliminaryScore + Math.round(overlap.ratio * 70);
  if (overlap.orderedAnchorMatches >= 2) score += 8;
  if (job.sidecar_tracks.length && Math.abs(appleTracks.length - job.sidecar_tracks.length) <= 2) score += 5;

  return {
    ...preliminary,
    item,
    artist,
    appleTracks,
    score,
    trackOverlapRatio: overlap.ratio,
    trackOverlapCount: overlap.count,
    orderedAnchorMatches: overlap.orderedAnchorMatches,
  };
}

function chooseCandidate(job, candidates) {
  const usable = candidates
    .filter((candidate) => (
      candidate.titleExact
      || candidate.titleCoreExact
      || candidate.titleContains
      || isCensoredTitleTracklistMatch(job, candidate)
      || isStrongAlternateTitleTracklistMatch(candidate)
    ))
    .sort((a, b) => b.score - a.score);

  if (!usable.length) return null;

  const titleMatched = usable.filter((candidate) => candidate.titleExact || candidate.titleCoreExact);
  const preferredTitleCandidate = choosePreferredEdition(titleMatched);
  if (preferredTitleCandidate && isSafeTitleCandidate(job, preferredTitleCandidate)) {
    return acceptedCandidate(preferredTitleCandidate, "artist_album_list_title_year_auto_match");
  }

  const containedTitleCandidates = usable.filter((candidate) => candidate.titleContains);
  const preferredContainedCandidate = choosePreferredEdition(containedTitleCandidates);
  if (preferredContainedCandidate && isSafeContainedTitleCandidate(preferredContainedCandidate)) {
    return acceptedCandidate(preferredContainedCandidate, "artist_album_list_title_containment_auto_match");
  }

  const censoredTitleCandidates = usable.filter((candidate) => isCensoredTitleTracklistMatch(job, candidate));
  const preferredCensoredCandidate = choosePreferredEdition(censoredTitleCandidates);
  if (preferredCensoredCandidate) {
    return acceptedCandidate(preferredCensoredCandidate, "artist_album_list_censored_title_tracklist_auto_match");
  }

  const alternateTitleCandidates = usable.filter((candidate) => isStrongAlternateTitleTracklistMatch(candidate));
  const preferredAlternateCandidate = choosePreferredEdition(alternateTitleCandidates);
  if (preferredAlternateCandidate && preferredAlternateCandidate.editionClass !== "expanded") {
    return acceptedCandidate(preferredAlternateCandidate, "artist_album_list_tracklist_auto_match");
  }

  return null;
}

function choosePreferredEdition(candidates) {
  if (!candidates.length) return null;
  const sorted = [...candidates].sort((a, b) => {
    const sameCoreA = a.titleExact || a.titleCoreExact ? 0 : 1;
    const sameCoreB = b.titleExact || b.titleCoreExact ? 0 : 1;
    return sameCoreA - sameCoreB
      || editionRank(a.editionClass) - editionRank(b.editionClass)
      || a.yearDelta - b.yearDelta
      || b.score - a.score;
  });
  return sorted[0];
}

function isSafeTitleCandidate(job, candidate) {
  if (candidate.yearDelta > 3) return false;
  if (candidate.editionClass === "single") return false;
  if (candidate.editionClass === "expanded") {
    return job.sidecar_tracks.length <= 3
      || candidate.trackOverlapRatio >= 0.4
      || candidate.trackOverlapCount >= 4;
  }
  return true;
}

function isSafeContainedTitleCandidate(candidate) {
  if (candidate.yearDelta > 3) return false;
  if (candidate.editionClass === "single") return false;
  return candidate.trackOverlapRatio >= 0.4 && candidate.trackOverlapCount >= 4;
}

function isCensoredTitleTracklistMatch(job, candidate) {
  if (candidate.yearDelta > 3) return false;
  if (candidate.editionClass === "single") return false;
  if (candidate.trackOverlapRatio < 0.78 || candidate.trackOverlapCount < 5 || candidate.orderedAnchorMatches < 2) return false;
  return hasExplicitWord(job.title) || hasCensoredMarker(candidate.item.attributes?.name);
}

function isStrongAlternateTitleTracklistMatch(candidate) {
  if (candidate.yearDelta > 1) return false;
  if (candidate.editionClass === "single" || candidate.editionClass === "expanded") return false;
  return candidate.trackOverlapRatio >= 0.82
    && candidate.trackOverlapCount >= 8
    && candidate.orderedAnchorMatches >= 2;
}

function acceptedCandidate(candidate, matchBasis) {
  return {
    ...candidate,
    match_basis: matchBasis,
    confidence: candidate.editionClass === "expanded" ? "medium" : candidate.trackOverlapRatio >= 0.78 ? "high" : "medium",
  };
}

function buildLinksForAcceptedAlbum(job, accepted, candidateCount) {
  const albumFields = {
    apple_catalog_id: accepted.item.id,
    apple_resource_type: "album",
    match_status: accepted.confidence === "high" ? "verified" : "candidate_verified",
    match_basis: accepted.match_basis,
    confidence: accepted.confidence,
    result_rank: "",
    title_match: accepted.titleExact ? "exact_normalized" : accepted.titleCoreExact ? "core_exact_normalized" : accepted.titleContains ? "contains_normalized" : "tracklist_supported",
    artist_match: accepted.artistCompatible ? "compatible_normalized" : "artist_id_scoped",
    year_delta: accepted.yearDelta,
    warnings: warningForAcceptedAlbum(accepted),
    apple_artist_id: accepted.artist.apple_artist_id,
    apple_artist_name: accepted.artist.apple_artist_name,
    artist_id_source: accepted.artist.artist_id_source,
    artist_link_source_ref: accepted.artist.artist_link_source_ref,
    artist_link_match_basis: accepted.artist.artist_link_match_basis,
    artist_album_candidate_count: candidateCount,
    edition_class: accepted.editionClass,
    track_overlap_ratio: accepted.trackOverlapRatio.toFixed(3),
    track_overlap_count: accepted.trackOverlapCount,
    ordered_anchor_matches: accepted.orderedAnchorMatches,
  };

  const output = [];
  output.push(makeLink(job, "graph_album", "album", albumFields));
  output.push(makeLink(job, "album_sidecar_album", "album", albumFields));
  output.push(...resolveAcceptedAlbumTracks(job, accepted));
  return output;
}

function warningForAcceptedAlbum(accepted) {
  const warnings = [];
  if (accepted.editionClass === "expanded") warnings.push("expanded_or_deluxe_accepted_only_after_same_title_preference");
  if (accepted.editionClass === "remaster") warnings.push("remaster_accepted");
  if (accepted.match_basis === "artist_album_list_tracklist_auto_match") warnings.push("alternate_album_title_accepted_by_strong_tracklist");
  return warnings.join(";");
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
    apple_artist_id: fields.apple_artist_id,
    apple_artist_name: fields.apple_artist_name,
    artist_id_source: fields.artist_id_source,
    artist_link_source_ref: fields.artist_link_source_ref,
    artist_link_match_basis: fields.artist_link_match_basis,
    artist_album_candidate_count: fields.artist_album_candidate_count,
    edition_class: fields.edition_class,
    track_overlap_ratio: fields.track_overlap_ratio,
    track_overlap_count: fields.track_overlap_count,
    ordered_anchor_matches: fields.ordered_anchor_matches,
    prior_review_reason: job.first_pass_review_reason,
    prior_best_score: job.first_pass_best_score,
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
      .map((track) => scoreTrackCandidate(row, track))
      .sort((a, b) => b.score - a.score);
    const best = scored[0];
    const second = scored[1];
    if (!best || !isTrackAutoAccept(best, second)) continue;
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
      match_basis: "artist_album_resolver_track_auto_match",
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
      if (!linkKeys.has(link.link_key)) {
        links.push(link);
        linkKeys.add(link.link_key);
      }
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
    apple_artist_id: outcome.apple_artist_id ?? "",
    artist_id_source: outcome.artist_id_source ?? "",
    candidate_count: outcome.candidate_count ?? "",
    best_score: outcome.best_score ?? "",
    best_candidate_id: outcome.best_candidate_id ?? "",
    best_candidate_title: outcome.best_candidate_title ?? "",
    best_candidate_variant: outcome.best_candidate_variant ?? "",
    error_message: outcome.error_message ?? "",
    prior_review_reason: job.first_pass_review_reason,
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
    storefront: args.storefront,
    generated_at: new Date().toISOString(),
    completed_album_refs: [...completedAlbumRefs].sort(),
    artist_search_cache: [...artistSearchCache.entries()],
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
    "apple_artist_id",
    "artist_id_source",
    "candidate_count",
    "best_score",
    "best_candidate_id",
    "best_candidate_title",
    "best_candidate_variant",
    "error_message",
    "prior_review_reason",
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
      ],
    },
    counts: {
      album_jobs_completed: completedAlbumRefs.size,
      new_links_total: sortedLinks.length,
      deferred_total: sortedDeferred.length,
      new_links_by_source_type: countBy(sortedLinks, "source_type"),
      new_links_by_resource_type: countBy(sortedLinks, "apple_resource_type"),
      new_links_by_match_basis: countBy(sortedLinks, "match_basis"),
      new_links_by_edition_class: countBy(sortedLinks.filter((link) => link.apple_resource_type === "album"), "edition_class"),
      deferred_by_reason: countBy(sortedDeferred, "deferred_reason"),
    },
  };
}

function buildManifest(summary) {
  return `# Apple Music Artist Album Resolver Pass v1

Generated: ${summary.generated_at}

Status: \`${summary.status}\`

Storefront: \`${summary.storefront}\`

## Policy

- Raw Apple payloads persisted: \`false\`
- Apple artist album and album track payloads are used only as transient candidate pools.
- Durable output stores Apple catalog IDs, resource type, storefront, source refs, match status, and matching metadata only.

## Intent

This pass targets graph albums still missing Apple album IDs after prior album search and album-variant passes. It scopes candidate albums by resolved Apple artist IDs, prefers original-like albums over remasters, and prefers remasters over expanded/deluxe editions when a same-title candidate exists.

## Counts

- Album jobs completed: ${summary.counts.album_jobs_completed}
- New links total: ${summary.counts.new_links_total}
- Deferred rows: ${summary.counts.deferred_total}

## New Links By Source Type

${tableFromCounts(summary.counts.new_links_by_source_type)}

## New Links By Match Basis

${tableFromCounts(summary.counts.new_links_by_match_basis)}

## Album Links By Edition Class

${tableFromCounts(summary.counts.new_links_by_edition_class)}

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

function classifyEdition(value) {
  const text = String(value ?? "").toLowerCase();
  if (/\bsingle\b/.test(text)) return "single";
  if (/\bep\b/.test(text)) return "ep";
  if (/\b(super deluxe|deluxe|expanded|bonus tracks?|anniversary|collector|legacy edition|complete recordings)\b/.test(text)) return "expanded";
  if (/\b(remaster(ed)?|remastered)\b/.test(text)) return "remaster";
  return "original_like";
}

function editionPreferencePoints(editionClass) {
  if (editionClass === "original_like") return 8;
  if (editionClass === "remaster") return 5;
  if (editionClass === "expanded") return -8;
  if (editionClass === "ep") return -6;
  return -20;
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
    .replace(/\b(remaster(ed)?|remastered|mono|stereo|single|album|version|edit|deluxe|expanded|anniversary|bonus|track|explicit|clean|edition|reissue|original|collector|complete|legacy|motion|picture|score|soundtrack)\b/g, " ")
    .replace(/\b(19|20)\d{2}\b/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function compatibleNames(candidate, expected) {
  if (!candidate || !expected) return false;
  return candidate === expected || candidate.includes(expected) || expected.includes(candidate);
}

function containsUseful(candidate, expected) {
  if (!candidate || !expected || expected.length < 6) return false;
  return candidate.includes(expected) || expected.includes(candidate);
}

function looksLikeNumberedSeriesCandidate(expectedTitleCore, candidateTitleCore) {
  if (!expectedTitleCore || !candidateTitleCore) return false;
  return new RegExp(`^${escapeRegex(expectedTitleCore)}\\s+\\d+$`).test(candidateTitleCore);
}

function hasExplicitWord(value) {
  return /\b(fuck|fucking|pussy|shit|bitch)\b/i.test(String(value ?? ""));
}

function hasCensoredMarker(value) {
  return /\*{2,}/.test(String(value ?? ""));
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

function escapeRegex(value) {
  return String(value).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function escapeMd(value) {
  return String(value ?? "").replace(/\|/g, "\\|");
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
