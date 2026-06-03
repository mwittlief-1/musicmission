#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { createAppleMusicCatalogClient } from "./lib/appleMusicCatalogClient.mjs";

const repoRoot = process.cwd();
const currentRoot = path.join(repoRoot, "data/canonical_graph/current");

const args = parseArgs(process.argv.slice(2));
const reviewSet = reviewSetFor(args.reviewSet);
const outputRoot = path.join(currentRoot, reviewSet.output_dir);
const runVersion = reviewSet.run_version;
const client = createAppleMusicCatalogClient({
  storefront: args.storefront,
  maxRetries: 8,
  retryBaseDelayMs: 1000,
  retryMaxDelayMs: 60000,
  timeoutMs: 60000,
});

fs.mkdirSync(outputRoot, { recursive: true });

const linksPath = path.join(outputRoot, `${reviewSet.artifact_prefix}_links_v1.jsonl`);
const deferredPath = path.join(outputRoot, `${reviewSet.artifact_prefix}_deferred_queue.csv`);
const summaryPath = path.join(outputRoot, `${reviewSet.artifact_prefix}_summary.json`);
const manifestPath = path.join(outputRoot, `${reviewSet.artifact_prefix}_manifest.md`);

const approvedAlbums = reviewSet.approved_albums;
const heldOutAlbums = reviewSet.held_out_albums;

const graphRows = readJson(path.join(currentRoot, "graph_linking_node_set.json")).rows;
const graphAlbumsByRef = new Map(
  graphRows
    .filter((row) => row.candidate_type === "album")
    .map((row) => [row.candidate_identity_key, row]),
);
const sidecarTracks = readCsv(path.join(currentRoot, "album_track_sidecar_tracks.csv"));
const sidecarTracksByAlbum = groupBy(sidecarTracks, (row) => row.candidate_identity_key);
const existingLinks = [
  ...safeReadJsonl(path.join(currentRoot, "apple_music_link_pass_v1/apple_music_links_v1.jsonl")),
  ...safeReadJsonl(path.join(currentRoot, "apple_music_try_harder_pass_v1/apple_music_try_harder_links_v1.jsonl")),
  ...safeReadJsonl(path.join(currentRoot, "apple_music_residual_track_pass_v1/apple_music_residual_track_links_v1.jsonl")),
  ...safeReadJsonl(path.join(currentRoot, "apple_music_album_variant_pass_v1/apple_music_album_variant_links_v1.jsonl")),
  ...safeReadJsonl(path.join(currentRoot, "apple_music_offline_reconciliation_pass_v1/apple_music_offline_reconciliation_links_v1.jsonl")),
  ...safeReadJsonl(path.join(currentRoot, "apple_music_artist_album_resolver_pass_v1/apple_music_artist_album_resolver_links_v1.jsonl")),
  ...safeReadJsonl(path.join(currentRoot, "apple_music_high_confidence_album_pass_v1/apple_music_high_confidence_album_links_v1.jsonl")),
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
const outputLinkKeys = new Set();
const outputSourceResourceKeys = new Set();
const albumCache = new Map();
const albumTracksCache = new Map();
const links = [];
const deferred = [];

for (const review of approvedAlbums) {
  const sourceRow = graphAlbumsByRef.get(review.source_ref);
  if (!sourceRow) {
    deferred.push(deferredRow(review, "manual_album_review_source_ref_not_found"));
    continue;
  }

  const album = await fetchAlbum(review.apple_album_id);
  if (!album) {
    deferred.push(deferredRow(review, "manual_album_review_apple_album_not_found"));
    continue;
  }

  const sidecarRows = sidecarTracksByAlbum.get(review.source_ref) ?? [];
  const appleTracks = await fetchAlbumTracks(review.apple_album_id);
  const job = {
    ...review,
    artist_display_name: sourceRow.artist_display_name,
    title: sourceRow.title,
    year: sourceRow.year,
    sidecar_tracks: sidecarRows,
    album,
    apple_tracks: appleTracks,
    artist_optional_for_tracks: isArtistOptional(sourceRow),
  };

  for (const link of buildAlbumLinks(job)) addLink(link);
  for (const link of buildTrackLinks(job)) addLink(link);
}

writeFinalArtifacts();

function approved(sourceRef, appleAlbumId, manualReviewListIndex) {
  return {
    source_ref: sourceRef,
    apple_album_id: appleAlbumId,
    manual_review_list_index: manualReviewListIndex,
  };
}

function parseArgs(argv) {
  const parsed = { storefront: "us", reviewSet: "manual_album_review_v1" };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--storefront") parsed.storefront = argv[++index];
    else if (arg === "--review-set") parsed.reviewSet = argv[++index];
  }
  return parsed;
}

function reviewSetFor(name) {
  const reviewSets = {
    manual_album_review_v1: {
      run_version: "apple_music_manual_album_review_pass_v1",
      output_dir: "apple_music_manual_album_review_pass_v1",
      artifact_prefix: "apple_music_manual_album_review",
      approved_match_basis: "user_manual_album_review_approved",
      track_match_basis: "user_manual_album_review_track_auto_match",
      intent: "This pass records user-approved album IDs from the first 20-row manual review slice. Items 2, 9, and 18 from that slice are intentionally held out for more manual review.",
      approved_albums: [
        approved("album|beach boys|surfin u s a", "1443101236", 1),
        approved("album|andrae crouch|live in london", "305503778", 3),
        approved("album|rip chords|hey little cobra and other hot rod hits", "260254179", 4),
        approved("album|various artists|dirty dancing", "254938499", 5),
        approved("album|red krayola|parable of arable land", "379207819", 6),
        approved("album|fania all stars|live at the cheetah vol 1", "1481517285", 7),
        approved("album|duke ellington|ellington at newport", "902277483", 8),
        approved("album|various artists|forrest gump", "418556875", 10),
        approved("album|various artists|beauty and the beast", "1699102817", 11),
        approved("album|larry heard|sceneries not songs volume one", "1706159425", 12),
        approved("album|el p|fantastic damage", "1510478926", 13),
        approved("album|various artists|twilight", "294342468", 14),
        approved("album|various artists|crow", "322025243", 15),
        approved("album|wiggles|big red car", "1871095493", 16),
        approved("album|various artists|singles", "192995929", 17),
        approved("album|little river band|greatest hits", "1645806082", 19),
        approved("album|various artists|hercules", "1412858854", 20),
      ],
      held_out_albums: [
        "album|my bloody valentine|loveless",
        "album|original broadway cast of oklahoma|oklahoma",
        "album|link wray|link wray and the wraymen",
      ],
    },
    semantic_album_hardening_v1: {
      run_version: "apple_music_semantic_album_hardening_pass_v1",
      output_dir: "apple_music_semantic_album_hardening_pass_v1",
      artifact_prefix: "apple_music_semantic_album_hardening",
      approved_match_basis: "semantic_album_hardening_llm_assisted_approved",
      track_match_basis: "semantic_album_hardening_track_auto_match",
      intent: "This pass records an LLM-assisted semantic hardening slice over the remaining graph albums. It accepts same-artist or soundtrack/cast provenance matches whose Apple titles are semantically the same album, while holding out known wrong-band, missing-catalog, and weak compilation substitutes.",
      approved_albums: [
        approved("album|original broadway cast of oklahoma|oklahoma", "1383513675", "semantic_original_cast"),
        approved("album|various artists|moana", "1440634928", "semantic_soundtrack"),
        approved("album|chiffons|chiffons", "1466690187", "semantic_same_artist_compilation"),
        approved("album|platters|encore of golden hits", "1440777167", "semantic_same_artist_compilation"),
        approved("album|original broadway cast of gypsy|gypsy", "164925460", "semantic_original_cast"),
        approved("album|soft machine|volume two", "1442442602", "semantic_title_variant"),
        approved("album|jesus culture|your love never fails", "1440830801", "semantic_live_variant"),
        approved("album|various artists|tangled", "1440639057", "semantic_soundtrack_better_candidate"),
        approved("album|allman brothers band|at fillmore east", "1440833569", "semantic_live_variant"),
        approved("album|motorhead|no sleep til hammersmith", "1614257261", "semantic_live_variant"),
        approved("album|peter gabriel|passion", "987561472", "semantic_subtitle_variant"),
        approved("album|bsd u|late night bumps", "1828927475", "semantic_title_variant"),
        approved("album|gene vincent|bluejean bop", "1443088443", "semantic_title_variant"),
        approved("album|joff bush|bluey the album", "1539376375", "semantic_better_candidate"),
        approved("album|bing crosby|merry christmas", "1425234668", "semantic_retitled_album"),
        approved("album|moby grape|moby grape", "266203734", "semantic_bonus_track_variant"),
        approved("album|harptones|life is but a dream", "1491664837", "semantic_title_variant"),
        approved("album|paul anka|paul anka", "1625973434", "semantic_exact_title_artist"),
        approved("album|santo and johnny|santo and johnny", "1455434148", "semantic_exact_title_artist"),
        approved("album|ali farka toure and ry cooder|talking timbuktu", "1528519970", "semantic_collaboration_credit_variant"),
        approved("album|kruder and dorfmeister|kandd sessions", "1613602443", "semantic_dj_mix_variant"),
        approved("album|aretha franklin|amazing grace", "1628093959", "semantic_live_variant"),
        approved("album|patsy cline|showcase", "1485036494", "semantic_credit_variant"),
        approved("album|frank zappa|lumpy gravy", "1443184225", "semantic_project_credit_variant"),
        approved("album|yo yo ma|bach cello suites", "381515547", "semantic_remaster_variant"),
        approved("album|jethro tull|thick as a brick", "1006839794", "semantic_remix_variant"),
        approved("album|curtis mayfield|super fly", "1048472205", "semantic_better_candidate"),
        approved("album|various artists|saturday night fever", "1445668458", "semantic_soundtrack_better_candidate"),
        approved("album|buena vista social club|buena vista social club presents ibrahim ferrer", "1743961194", "semantic_credit_variant"),
        approved("album|maverick city music|maverick city vol 3 part 1", "1571839845", "semantic_title_variant"),
        approved("album|gene vincent|gene vincent and his blue caps", "1444084564", "semantic_better_candidate"),
        approved("album|ray stevens|ray stevens greatest hits", "277495713", "semantic_same_artist_compilation"),
        approved("album|various artists|romeo juliet", "1467520632", "semantic_soundtrack"),
        approved("album|paris sisters|paris sisters", "289487026", "semantic_same_artist_compilation"),
        approved("album|vicente fernandez|un azteca en el azteca", "1149209970", "semantic_better_candidate"),
      ],
      held_out_albums: [
        "album|my bloody valentine|loveless",
        "album|link wray|link wray and the wraymen",
        "album|garden state|garden state_wrong_artist_candidate",
        "album|various artists|matrix_score_not_soundtrack",
        "album|bad brains|bad brains_no_self_titled_apple_album_seen",
        "album|ll cool j|radio_no_album_candidate_seen",
        "album|ll cool j|bigger and deffer_wrong_artist_candidate",
      ],
    },
  };

  const reviewSet = reviewSets[name];
  if (!reviewSet) throw new Error(`Unknown review set: ${name}`);
  return reviewSet;
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

async function fetchAlbumTracks(albumId) {
  if (albumTracksCache.has(albumId)) return albumTracksCache.get(albumId);
  const tracks = [];
  let endpoint = `/v1/catalog/${encodeURIComponent(args.storefront)}/albums/${encodeURIComponent(albumId)}/tracks`;
  let query = {
    limit: 300,
    "fields[songs]": "name,artistName,durationInMillis,discNumber,trackNumber",
  };
  try {
    for (let page = 0; page < 10; page += 1) {
      const payload = await client.catalogGet(endpoint, query);
      for (const item of payload?.data ?? []) {
        if (item.type === "songs" && item.id) tracks.push(item);
      }
      if (!payload?.next) break;
      const next = new URL(payload.next, "https://api.music.apple.com");
      endpoint = next.pathname;
      query = Object.fromEntries(next.searchParams.entries());
    }
  } catch {
    tracks.length = 0;
  }
  albumTracksCache.set(albumId, tracks);
  return tracks;
}

function buildAlbumLinks(job) {
  const fields = {
    apple_catalog_id: job.apple_album_id,
    apple_resource_type: "album",
    match_status: "verified",
    match_basis: reviewSet.approved_match_basis,
    confidence: "high",
    result_rank: "",
    title_match: "manual_review_approved",
    artist_match: isArtistOptional(job) ? "not_required_manual_review" : "manual_review_approved",
    year_delta: yearDelta(job),
    warnings: "approved_by_user_manual_pass",
    manual_review_list_index: job.manual_review_list_index,
  };
  return [
    makeLink(job, "graph_album", "album", fields),
    makeLink(job, "album_sidecar_album", "album", fields),
  ];
}

function buildTrackLinks(job) {
  const normalizedAppleTracks = job.apple_tracks
    .map((item, index) => normalizeAppleTrack(item, index))
    .filter(Boolean);
  const output = [];
  const usedAppleIds = new Set();

  for (const row of job.sidecar_tracks.sort(compareTrackRows)) {
    const sourceRef = sidecarTrackSourceRef(row);
    if (existingSidecarTrackRefs.has(sourceRef)) continue;
    const scored = normalizedAppleTracks
      .filter((track) => !usedAppleIds.has(track.apple_catalog_id))
      .map((track) => scoreTrackCandidate(row, track, job.artist_optional_for_tracks))
      .sort((a, b) => b.score - a.score);
    const best = scored[0];
    const second = scored[1];
    if (!best || !isTrackAutoAccept(best, second, job.artist_optional_for_tracks)) continue;
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
      match_basis: reviewSet.track_match_basis,
      confidence: best.confidence,
      result_rank: best.track.album_track_index + 1,
      title_match: best.title_match,
      artist_match: best.artist_match,
      warnings: best.warnings,
      apple_album_id: job.apple_album_id,
      album_match_basis: reviewSet.approved_match_basis,
      track_score: best.score,
      duration_delta_ms: best.duration_delta_ms,
      manual_review_list_index: job.manual_review_list_index,
      verified_at: new Date().toISOString(),
      raw_payload_persisted: false,
    });
  }

  return output;
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
    manual_review_list_index: fields.manual_review_list_index,
    verified_at: new Date().toISOString(),
    raw_payload_persisted: false,
  };
}

function addLink(link) {
  const sourceKey = sourceResourceKey(link.source_type, link.source_ref, link.apple_resource_type);
  if (existingSourceResourceKeys.has(sourceKey) || outputSourceResourceKeys.has(sourceKey) || outputLinkKeys.has(link.link_key)) return;
  links.push(link);
  outputLinkKeys.add(link.link_key);
  outputSourceResourceKeys.add(sourceKey);
}

function deferredRow(review, reason) {
  return {
    deferred_key: `graph_album:${review.source_ref}:${reason}`,
    run_version: runVersion,
    source_ref: review.source_ref,
    source_type: "graph_album",
    source_candidate_type: "album",
    apple_album_id: review.apple_album_id,
    storefront: args.storefront,
    deferred_reason: reason,
    manual_review_list_index: review.manual_review_list_index,
    raw_payload_persisted: false,
  };
}

function yearDelta(job) {
  const expected = Number(job.year);
  const actual = Number(String(job.album?.attributes?.releaseDate ?? "").slice(0, 4));
  if (!Number.isFinite(expected) || !Number.isFinite(actual)) return "";
  return Math.abs(expected - actual);
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

function isArtistOptional(row) {
  const text = normalize(`${row.artist_display_name ?? ""} ${row.title ?? ""} ${(row.archetypes ?? []).join(" ")}`);
  return text.includes("various artists")
    || text.includes("soundtrack")
    || text.includes("cast")
    || text.includes("disney")
    || text.includes("movie soundtracks");
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
    .replace(/\s+/gu, " ")
    .trim();
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
    const value = row[key] || "unknown";
    counts[value] = (counts[value] ?? 0) + 1;
  }
  return counts;
}

function writeFinalArtifacts() {
  const sortedLinks = [...links].sort((a, b) => a.link_key.localeCompare(b.link_key));
  const sortedDeferred = [...deferred].sort((a, b) => a.deferred_key.localeCompare(b.deferred_key));
  const summary = {
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
      approved_album_count: approvedAlbums.length,
      held_out_for_manual_check: heldOutAlbums,
      graph_linking_node_set: "data/canonical_graph/current/graph_linking_node_set.json",
      album_track_sidecar_tracks: "data/canonical_graph/current/album_track_sidecar_tracks.csv",
    },
    counts: {
      new_links_total: sortedLinks.length,
      deferred_total: sortedDeferred.length,
      new_links_by_source_type: countBy(sortedLinks, "source_type"),
      new_links_by_resource_type: countBy(sortedLinks, "apple_resource_type"),
      new_links_by_match_basis: countBy(sortedLinks, "match_basis"),
      deferred_by_reason: countBy(sortedDeferred, "deferred_reason"),
    },
  };

  fs.writeFileSync(linksPath, `${sortedLinks.map((link) => JSON.stringify(link)).join("\n")}\n`);
  writeCsv(deferredPath, sortedDeferred, [
    "deferred_key",
    "run_version",
    "source_ref",
    "source_type",
    "source_candidate_type",
    "apple_album_id",
    "storefront",
    "deferred_reason",
    "manual_review_list_index",
    "raw_payload_persisted",
  ]);
  fs.writeFileSync(summaryPath, `${JSON.stringify(summary, null, 2)}\n`);
  fs.writeFileSync(manifestPath, buildManifest(summary));
  console.log(JSON.stringify(summary, null, 2));
}

function buildManifest(summary) {
  return `# Apple Music Manual Album Review Pass v1

Generated: ${summary.generated_at}

Status: \`${summary.status}\`

Storefront: \`${summary.storefront}\`

## Policy

- Raw Apple payloads persisted: \`false\`
- Apple album and album track payloads are used only as transient validation and sidecar-track candidate pools.
- Durable output stores Apple catalog IDs, resource type, storefront, source refs, manual review provenance, and compact matching metadata only.

## Intent

${reviewSet.intent}

## Counts

- Approved albums: ${summary.inputs.approved_album_count}
- New links total: ${summary.counts.new_links_total}
- Deferred rows: ${summary.counts.deferred_total}

## New Links By Source Type

${tableFromCounts(summary.counts.new_links_by_source_type)}

## New Links By Match Basis

${tableFromCounts(summary.counts.new_links_by_match_basis)}
`;
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
