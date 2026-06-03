#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { createAppleMusicCatalogClient } from "./lib/appleMusicCatalogClient.mjs";

const repoRoot = process.cwd();
const currentRoot = path.join(repoRoot, "data/canonical_graph/current");
const outputRoot = path.join(currentRoot, "apple_music_graph_song_iterative_hardening_pass_v1");
const runVersion = "apple_music_graph_song_iterative_hardening_pass_v1";

const args = parseArgs(process.argv.slice(2));
const storefront = args.storefront;
const client = createAppleMusicCatalogClient({
  storefront,
  maxRetries: args.maxRetries,
  retryBaseDelayMs: 1000,
  retryMaxDelayMs: 60000,
  timeoutMs: 60000,
});

fs.mkdirSync(outputRoot, { recursive: true });

const linksPath = path.join(outputRoot, "apple_music_graph_song_iterative_hardening_links_v1.jsonl");
const deferredPath = path.join(outputRoot, "apple_music_graph_song_iterative_hardening_deferred_queue.csv");
const summaryPath = path.join(outputRoot, "apple_music_graph_song_iterative_hardening_summary.json");
const manifestPath = path.join(outputRoot, "apple_music_graph_song_iterative_hardening_manifest.md");

const linkInputSpecs = [
  ["first_pass_links", "apple_music_link_pass_v1/apple_music_links_v1.jsonl"],
  ["try_harder_links", "apple_music_try_harder_pass_v1/apple_music_try_harder_links_v1.jsonl"],
  ["residual_track_links", "apple_music_residual_track_pass_v1/apple_music_residual_track_links_v1.jsonl"],
  ["album_variant_links", "apple_music_album_variant_pass_v1/apple_music_album_variant_links_v1.jsonl"],
  ["offline_reconciliation_links", "apple_music_offline_reconciliation_pass_v1/apple_music_offline_reconciliation_links_v1.jsonl"],
  ["artist_album_resolver_links", "apple_music_artist_album_resolver_pass_v1/apple_music_artist_album_resolver_links_v1.jsonl"],
  ["high_confidence_album_links", "apple_music_high_confidence_album_pass_v1/apple_music_high_confidence_album_links_v1.jsonl"],
  ["manual_album_review_links", "apple_music_manual_album_review_pass_v1/apple_music_manual_album_review_links_v1.jsonl"],
  ["semantic_album_hardening_links", "apple_music_semantic_album_hardening_pass_v1/apple_music_semantic_album_hardening_links_v1.jsonl"],
  ["album_graph_decision_links", "apple_music_album_graph_decision_pass_v1/apple_music_album_graph_decision_links_v1.jsonl"],
  ["song_source_album_reconciliation_links", "apple_music_song_source_album_reconciliation_pass_v1/apple_music_song_source_album_reconciliation_links_v1.jsonl"],
  ["direct_song_hardening_v1_links", "apple_music_direct_song_hardening_pass_v1/apple_music_direct_song_hardening_links_v1.jsonl"],
  ["direct_song_hardening_v2_links", "apple_music_direct_song_hardening_pass_v2/apple_music_direct_song_hardening_v2_links.jsonl"],
  ["recording_hardening_links", "apple_music_recording_hardening_pass_v1/apple_music_recording_hardening_links_v1.jsonl"],
  ["sidecar_track_album_bound_links", "apple_music_sidecar_track_album_bound_pass_v1/apple_music_sidecar_track_album_bound_links_v1.jsonl"],
];

const graphRows = readJson(path.join(currentRoot, "graph_linking_node_set.json")).rows;
const graphRowsByRef = new Map(graphRows.map((row) => [row.candidate_identity_key, row]));
const sidecarAlbumRows = readCsv(path.join(currentRoot, "album_track_sidecar_album_resolution.csv"));
const sidecarAlbumRowsByRef = new Map(sidecarAlbumRows.map((row) => [row.candidate_identity_key, row]));
const sidecarTrackRows = readCsv(path.join(currentRoot, "album_track_sidecar_tracks.csv"));
const firstPassReviews = readCsv(path.join(currentRoot, "apple_music_link_pass_v1/apple_music_manual_review_queue.csv"));
const directSongV2DeferredRows = readCsv(path.join(currentRoot, "apple_music_direct_song_hardening_pass_v2/apple_music_direct_song_hardening_v2_deferred_queue.csv"));
const replacementRows = safeReadJson(path.join(currentRoot, "apple_music_album_graph_decision_pass_v1/apple_music_album_graph_replacement_nodes_v1.json"))?.rows ?? [];
const replacementRowsByRef = new Map(replacementRows.map((row) => [row.candidate_identity_key, row]));
const firstPassReviewByRef = new Map(firstPassReviews.map((row) => [graphSourceKey(row.source_type, row.source_ref), row]));
const v2DeferredByRef = new Map(directSongV2DeferredRows.map((row) => [graphSourceKey(row.source_type, row.source_ref), row]));

const existingLinks = linkInputSpecs.flatMap(([, relativePath]) => safeReadJsonl(path.join(currentRoot, relativePath)));
const existingGraphSongLinkKeys = new Set(
  existingLinks
    .filter((link) => isGraphSongLink(link) && isAcceptedLink(link))
    .map((link) => graphSourceKey(link.source_type, link.source_ref)),
);

const graphSongRows = graphRows.filter((row) => row.candidate_type === "song");
const allReviewRows = graphSongRows
  .filter((row) => !existingGraphSongLinkKeys.has(graphSourceKey("graph_song", row.candidate_identity_key)))
  .map((row) => graphSongJob(row));
const reviewRows = Number.isFinite(args.limitJobs) ? allReviewRows.slice(0, args.limitJobs) : allReviewRows;

const sidecarTrackLinkByRef = new Map();
for (const link of existingLinks) {
  if (link.source_type !== "album_sidecar_track" || link.apple_resource_type !== "song" || !isAcceptedLink(link)) continue;
  if (!sidecarTrackLinkByRef.has(link.source_ref)) sidecarTrackLinkByRef.set(link.source_ref, link);
}

const albumContextByAppleId = buildAlbumContextsByAppleId();
const bestAlbumContextBySourceRef = buildBestAlbumContextBySourceRef();
const sidecarCandidates = buildSidecarCandidates();
const albumFetchResults = await fetchResolvedAlbumTracks();
const albumTrackCandidates = buildAlbumTrackCandidates(albumFetchResults);
const allCandidates = [...sidecarCandidates, ...albumTrackCandidates];
const candidateIndex = buildCandidateIndex(allCandidates);

const links = [];
const deferred = [];
const outputGraphSourceKeys = new Set();
const albumStageDeferred = [];

for (const review of reviewRows) {
  const outcome = resolveAlbumBackedReview(review);
  if (outcome.kind === "link") {
    const sourceKey = graphSourceKey(review.source_type, review.source_ref);
    if (outputGraphSourceKeys.has(sourceKey)) continue;
    const link = makeLink(review, outcome);
    links.push(link);
    outputGraphSourceKeys.add(sourceKey);
  } else {
    albumStageDeferred.push({ review, outcome });
  }
}

const directSearchJobs = albumStageDeferred
  .map(({ review }) => review)
  .filter((review) => !outputGraphSourceKeys.has(graphSourceKey(review.source_type, review.source_ref)));
let directSearchProcessed = 0;

if (!args.skipSearch) {
  console.error(JSON.stringify({
    run_version: runVersion,
    storefront,
    direct_search_jobs: directSearchJobs.length,
    concurrency: args.searchConcurrency,
    dry_run: args.dryRun,
  }, null, 2));

  await runPool(directSearchJobs, args.searchConcurrency, async (review) => {
    const outcome = args.dryRun ? directSearchDefer("dry_run_no_catalog_call") : await resolveDirectSearchReview(review);
    const sourceKey = graphSourceKey(review.source_type, review.source_ref);
    if (outcome.kind === "link" && !outputGraphSourceKeys.has(sourceKey)) {
      links.push(makeDirectSearchLink(review, outcome));
      outputGraphSourceKeys.add(sourceKey);
    } else if (!outputGraphSourceKeys.has(sourceKey)) {
      deferred.push(makeDeferred(review, outcome));
    }

    directSearchProcessed += 1;
    if (directSearchProcessed % args.progressEvery === 0 || directSearchProcessed === directSearchJobs.length) {
      console.error(`graph song iterative hardening: direct search ${directSearchProcessed}/${directSearchJobs.length}, links=${links.length}, deferred=${deferred.length}`);
    }
  });
} else {
  for (const { review, outcome } of albumStageDeferred) {
    deferred.push(makeDeferred(review, outcome));
  }
}

writeFinalArtifacts();

function parseArgs(argv) {
  const parsed = {
    storefront: "us",
    concurrency: 6,
    searchConcurrency: 8,
    maxRetries: 8,
    limitAlbums: Number.NaN,
    limitJobs: Number.NaN,
    progressEvery: 100,
    skipSearch: false,
    dryRun: false,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--storefront") parsed.storefront = argv[++index];
    else if (arg === "--concurrency") parsed.concurrency = Number(argv[++index]);
    else if (arg === "--search-concurrency") parsed.searchConcurrency = Number(argv[++index]);
    else if (arg === "--max-retries") parsed.maxRetries = Number(argv[++index]);
    else if (arg === "--limit-albums") parsed.limitAlbums = Number(argv[++index]);
    else if (arg === "--limit-jobs") parsed.limitJobs = Number(argv[++index]);
    else if (arg === "--progress-every") parsed.progressEvery = Number(argv[++index]);
    else if (arg === "--skip-search") parsed.skipSearch = true;
    else if (arg === "--dry-run") parsed.dryRun = true;
  }

  if (!parsed.storefront) parsed.storefront = "us";
  if (!Number.isFinite(parsed.concurrency) || parsed.concurrency < 1) parsed.concurrency = 1;
  if (parsed.concurrency > 12) parsed.concurrency = 12;
  if (!Number.isFinite(parsed.searchConcurrency) || parsed.searchConcurrency < 1) parsed.searchConcurrency = parsed.concurrency;
  if (parsed.searchConcurrency > 12) parsed.searchConcurrency = 12;
  if (!Number.isFinite(parsed.maxRetries) || parsed.maxRetries < 0) parsed.maxRetries = 3;
  if (!Number.isFinite(parsed.progressEvery) || parsed.progressEvery < 1) parsed.progressEvery = 100;
  return parsed;
}

function graphSongJob(row) {
  const sourceKey = graphSourceKey("graph_song", row.candidate_identity_key);
  const firstPassReview = firstPassReviewByRef.get(sourceKey) ?? {};
  const v2Deferred = v2DeferredByRef.get(sourceKey) ?? {};
  return {
    source_ref: row.candidate_identity_key,
    source_type: "graph_song",
    source_candidate_type: "song",
    artist_display_name: row.artist_display_name ?? "",
    title: row.title ?? "",
    year: String(row.year ?? ""),
    archetype_ids: Array.isArray(row.archetype_ids) ? row.archetype_ids : [],
    archetypes: Array.isArray(row.archetypes) ? row.archetypes : [],
    import_classes: Array.isArray(row.import_classes) ? row.import_classes : [],
    review_reason: firstPassReview.review_reason ?? "",
    prior_review_reason: v2Deferred.prior_review_reason || firstPassReview.review_reason || "",
    prior_best_reject_reason: v2Deferred.best_reject_reason || v2Deferred.prior_best_reject_reason || "",
  };
}

function buildAlbumContextsByAppleId() {
  const contextByKey = new Map();
  for (const link of existingLinks) {
    if (!isAcceptedLink(link)) continue;
    if (link.apple_resource_type !== "album") continue;
    if (!["graph_album", "graph_replacement_album", "album_sidecar_album"].includes(link.source_type)) continue;

    const sourceRow = albumSourceRow(link);
    const context = {
      album_apple_catalog_id: String(link.apple_catalog_id),
      album_source_ref: link.source_ref,
      album_source_type: link.source_type,
      album_source_year: sourceYear(sourceRow),
      album_artist_norm: normalize(stripFeaturing(sourceRow?.artist_display_name ?? "")),
      album_match_basis: link.match_basis ?? "",
      album_match_status: link.match_status ?? "",
      album_confidence: link.confidence ?? "",
    };
    contextByKey.set(`${context.album_apple_catalog_id}|${context.album_source_type}|${context.album_source_ref}`, context);
  }

  const byAppleId = new Map();
  for (const context of [...contextByKey.values()].sort(compareAlbumContexts)) {
    if (!byAppleId.has(context.album_apple_catalog_id)) byAppleId.set(context.album_apple_catalog_id, []);
    byAppleId.get(context.album_apple_catalog_id).push(context);
  }
  return byAppleId;
}

function albumSourceRow(link) {
  if (link.source_type === "graph_album") return graphRowsByRef.get(link.source_ref);
  if (link.source_type === "graph_replacement_album") return replacementRowsByRef.get(link.source_ref);
  if (link.source_type === "album_sidecar_album") return sidecarAlbumRowsByRef.get(link.source_ref);
  return null;
}

function sourceYear(row) {
  return row?.year ? String(row.year) : row?.album_year ? String(row.album_year) : "";
}

function buildBestAlbumContextBySourceRef() {
  const bySourceRef = new Map();
  for (const contexts of albumContextByAppleId.values()) {
    for (const context of contexts) {
      const prior = bySourceRef.get(context.album_source_ref);
      if (!prior || compareAlbumContexts(context, prior) < 0) bySourceRef.set(context.album_source_ref, context);
    }
  }
  return bySourceRef;
}

function compareAlbumContexts(left, right) {
  const priorityDelta = albumContextPriority(right.album_source_type) - albumContextPriority(left.album_source_type);
  if (priorityDelta) return priorityDelta;
  return `${left.album_apple_catalog_id}|${left.album_source_ref}`.localeCompare(`${right.album_apple_catalog_id}|${right.album_source_ref}`);
}

function albumContextPriority(sourceType) {
  if (sourceType === "graph_album") return 40;
  if (sourceType === "graph_replacement_album") return 30;
  if (sourceType === "album_sidecar_album") return 20;
  return 0;
}

function buildSidecarCandidates() {
  const candidates = [];
  for (const row of sidecarTrackRows) {
    const sourceRef = sidecarTrackSourceRef(row);
    const link = sidecarTrackLinkByRef.get(sourceRef);
    if (!link) continue;

    const trackArtist = row.track_artist_name || row.artist_display_name || "";
    const albumContext = bestAlbumContextForSidecar(row.candidate_identity_key);
    candidates.push(makeCandidate({
      source_kind: "linked_sidecar_track",
      apple_catalog_id: link.apple_catalog_id,
      source_track_ref: sourceRef,
      album_source_ref: row.candidate_identity_key,
      album_source_type: "album_sidecar_album",
      album_source_year: String(row.album_year ?? ""),
      album_artist_name: row.artist_display_name ?? "",
      track_artist_name: trackArtist,
      track_title: row.track_title,
      album_apple_catalog_id: albumContext?.album_apple_catalog_id ?? row.apple_collection_id ?? "",
      album_match_basis: albumContext?.album_match_basis ?? "",
      track_match_basis: link.match_basis ?? "",
    }));
  }
  return candidates;
}

function bestAlbumContextForSidecar(sourceRef) {
  return bestAlbumContextBySourceRef.get(sourceRef) ?? null;
}

async function fetchResolvedAlbumTracks() {
  const albumIds = [...albumContextByAppleId.keys()].sort();
  const selectedAlbumIds = Number.isFinite(args.limitAlbums) ? albumIds.slice(0, args.limitAlbums) : albumIds;
  const results = [];
  let completed = 0;

  if (args.dryRun) {
    return selectedAlbumIds.map((albumId) => ({
      album_apple_catalog_id: albumId,
      tracks: [],
      status: "dry_run_no_catalog_call",
      error_message: "",
    }));
  }

  console.error(JSON.stringify({
    run_version: runVersion,
    storefront,
    resolved_album_ids_to_fetch: selectedAlbumIds.length,
    concurrency: args.concurrency,
  }, null, 2));

  await runPool(selectedAlbumIds, args.concurrency, async (albumId) => {
    const result = await fetchTracksForAlbum(albumId);
    results.push(result);
    completed += 1;
    if (completed % args.progressEvery === 0 || completed === selectedAlbumIds.length) {
      const failed = results.filter((row) => row.status !== "ok").length;
      const trackCount = results.reduce((sum, row) => sum + row.tracks.length, 0);
      console.error(`song source album pass: fetched ${completed}/${selectedAlbumIds.length} albums, tracks=${trackCount}, failed=${failed}`);
    }
  });

  return results.sort((a, b) => a.album_apple_catalog_id.localeCompare(b.album_apple_catalog_id));
}

async function fetchTracksForAlbum(albumId) {
  const tracks = [];
  let endpoint = `/v1/catalog/${encodeURIComponent(storefront)}/albums/${encodeURIComponent(albumId)}/tracks`;
  let query = {
    limit: 100,
    "fields[songs]": "name,artistName,durationInMillis,discNumber,trackNumber",
  };

  try {
    while (endpoint) {
      const payload = await client.catalogGet(endpoint, query);
      for (const item of payload?.data ?? []) {
        if (item.type !== "songs" || !item.id) continue;
        tracks.push(item);
      }
      endpoint = payload?.next ?? "";
      query = {};
    }
    return { album_apple_catalog_id: albumId, tracks, status: "ok", error_message: "" };
  } catch (error) {
    return {
      album_apple_catalog_id: albumId,
      tracks: [],
      status: "request_failed",
      error_message: errorMessage(error),
    };
  }
}

function buildAlbumTrackCandidates(fetchResults) {
  const candidates = [];
  for (const result of fetchResults) {
    if (result.status !== "ok") continue;
    const contexts = albumContextByAppleId.get(result.album_apple_catalog_id) ?? [];
    if (!contexts.length) continue;

    for (const item of result.tracks) {
      const attrs = item.attributes ?? {};
      if (!attrs.name) continue;
      for (const context of contexts) {
        candidates.push(makeCandidate({
          source_kind: albumTrackSourceKind(context.album_source_type),
          apple_catalog_id: item.id,
          source_track_ref: "",
          album_source_ref: context.album_source_ref,
          album_source_type: context.album_source_type,
          album_source_year: context.album_source_year,
          album_artist_name: denormalizedAlbumArtist(context),
          track_artist_name: attrs.artistName ?? "",
          track_title: attrs.name,
          album_apple_catalog_id: result.album_apple_catalog_id,
          album_match_basis: context.album_match_basis,
          track_match_basis: "transient_resolved_album_track_sparse_lookup",
        }));
      }
    }
  }
  return candidates;
}

function albumTrackSourceKind(albumSourceType) {
  if (albumSourceType === "graph_album") return "resolved_graph_album_track";
  if (albumSourceType === "graph_replacement_album") return "resolved_graph_replacement_album_track";
  if (albumSourceType === "album_sidecar_album") return "resolved_sidecar_album_track";
  return "resolved_album_track";
}

function denormalizedAlbumArtist(context) {
  const row = context.album_source_type === "graph_album"
    ? graphRowsByRef.get(context.album_source_ref)
    : context.album_source_type === "graph_replacement_album"
      ? replacementRowsByRef.get(context.album_source_ref)
      : sidecarAlbumRowsByRef.get(context.album_source_ref);
  return row?.artist_display_name ?? "";
}

function makeCandidate(fields) {
  const exactTitleKeys = titleExactKeys(fields.track_title);
  const coreTitleKeys = titleCoreKeys(fields.track_title);
  const trackArtistNorm = normalize(stripFeaturing(fields.track_artist_name));
  const albumArtistNorm = normalize(stripFeaturing(fields.album_artist_name));

  return {
    ...fields,
    apple_catalog_id: String(fields.apple_catalog_id),
    album_apple_catalog_id: String(fields.album_apple_catalog_id ?? ""),
    album_source_year: String(fields.album_source_year ?? ""),
    exact_title_keys: exactTitleKeys,
    core_title_keys: coreTitleKeys,
    track_artist_norm: trackArtistNorm,
    album_artist_norm: albumArtistNorm,
    effective_artist_norm: trackArtistNorm || albumArtistNorm,
  };
}

function buildCandidateIndex(candidates) {
  const exactTitle = new Map();
  const coreTitle = new Map();
  for (const candidate of candidates) {
    for (const key of candidate.exact_title_keys) pushIndex(exactTitle, key, candidate);
    for (const key of candidate.core_title_keys) pushIndex(coreTitle, key, candidate);
  }
  return { exactTitle, coreTitle };
}

function resolveAlbumBackedReview(review) {
  const reviewContext = {
    title_exact_keys: titleExactKeys(review.title),
    title_core_keys: titleCoreKeys(review.title),
    artist_norm: normalize(stripFeaturing(review.artist_display_name)),
    year: String(review.year ?? ""),
  };
  const specs = [
    {
      title_mode: "exact",
      artist_mode: "exact",
      year_mode: "context_year",
      confidence: "high",
      title_match: "exact_normalized",
      artist_match: "exact_normalized",
      basis_suffix: "exact_title_artist_context_year",
      warnings: [],
    },
    {
      title_mode: "exact",
      artist_mode: "compatible",
      year_mode: "context_year",
      confidence: "medium",
      title_match: "exact_normalized",
      artist_match: "compatible_normalized",
      basis_suffix: "exact_title_compatible_artist_context_year",
      warnings: [],
    },
    {
      title_mode: "exact",
      artist_mode: "exact",
      year_mode: "unique_no_year",
      confidence: "medium",
      title_match: "exact_normalized",
      artist_match: "exact_normalized",
      basis_suffix: "exact_title_artist_unique_no_year",
      warnings: ["year_not_confirmed"],
    },
    {
      title_mode: "exact",
      artist_mode: "compatible",
      year_mode: "unique_no_year",
      confidence: "medium",
      title_match: "exact_normalized",
      artist_match: "compatible_normalized",
      basis_suffix: "exact_title_compatible_artist_unique_no_year",
      warnings: ["year_not_confirmed"],
    },
    {
      title_mode: "core",
      artist_mode: "exact",
      year_mode: "context_year",
      confidence: "medium",
      title_match: "core_exact_normalized",
      artist_match: "exact_normalized",
      basis_suffix: "core_title_artist_context_year",
      warnings: ["title_core_match"],
    },
    {
      title_mode: "core",
      artist_mode: "compatible",
      year_mode: "context_year",
      confidence: "medium",
      title_match: "core_exact_normalized",
      artist_match: "compatible_normalized",
      basis_suffix: "core_title_compatible_artist_context_year",
      warnings: ["title_core_match"],
    },
  ];

  let strongestAmbiguity = null;
  for (const spec of specs) {
    const result = candidatesForSpec(reviewContext, spec);
    if (result.unique.length === 1) {
      const candidate = chooseBestCandidate(result.unique[0].candidates, reviewContext);
      return {
        kind: "link",
        candidate,
        spec,
        candidate_apple_id_count: 1,
      };
    }
    if (result.unique.length > 1 && (!strongestAmbiguity || result.unique.length > strongestAmbiguity.candidate_apple_id_count)) {
      strongestAmbiguity = {
        kind: "deferred",
        reason: "song_source_album_ambiguous_track_match",
        candidate_apple_id_count: result.unique.length,
        candidate_count: result.candidate_count,
        strongest_basis_suffix: spec.basis_suffix,
      };
    }
  }

  return strongestAmbiguity ?? {
    kind: "deferred",
    reason: "song_source_album_no_unique_track_match",
    candidate_apple_id_count: 0,
    candidate_count: 0,
    strongest_basis_suffix: "",
  };
}

function candidatesForSpec(reviewContext, spec) {
  const titleKeys = spec.title_mode === "exact" ? reviewContext.title_exact_keys : reviewContext.title_core_keys;
  const sourceMap = spec.title_mode === "exact" ? candidateIndex.exactTitle : candidateIndex.coreTitle;
  const poolByCandidateKey = new Map();

  for (const titleKey of titleKeys) {
    for (const candidate of sourceMap.get(titleKey) ?? []) {
      if (!candidatePassesYear(candidate, reviewContext, spec)) continue;
      if (!candidatePassesArtist(candidate, reviewContext, spec)) continue;
      poolByCandidateKey.set(candidateKey(candidate), candidate);
    }
  }

  const byAppleId = new Map();
  for (const candidate of poolByCandidateKey.values()) {
    if (!byAppleId.has(candidate.apple_catalog_id)) byAppleId.set(candidate.apple_catalog_id, []);
    byAppleId.get(candidate.apple_catalog_id).push(candidate);
  }
  return {
    unique: [...byAppleId.entries()].map(([appleId, candidates]) => ({ appleId, candidates })),
    candidate_count: poolByCandidateKey.size,
  };
}

function candidatePassesYear(candidate, reviewContext, spec) {
  if (spec.year_mode !== "context_year") return true;
  return Boolean(candidate.album_source_year && reviewContext.year && candidate.album_source_year === reviewContext.year);
}

function candidatePassesArtist(candidate, reviewContext, spec) {
  const artist = reviewContext.artist_norm;
  if (!artist) return false;
  if (spec.artist_mode === "exact") {
    return candidate.effective_artist_norm === artist || candidate.track_artist_norm === artist;
  }
  return (
    compatibleNames(candidate.effective_artist_norm, artist)
    || compatibleNames(candidate.track_artist_norm, artist)
    || compatibleNames(candidate.album_artist_norm, artist)
  );
}

function chooseBestCandidate(candidates, reviewContext) {
  return [...candidates].sort((left, right) => {
    const priorityDelta = candidatePriority(right, reviewContext) - candidatePriority(left, reviewContext);
    if (priorityDelta) return priorityDelta;
    return candidateKey(left).localeCompare(candidateKey(right));
  })[0];
}

function candidatePriority(candidate, reviewContext) {
  let priority = sourceKindPriority(candidate.source_kind);
  if (candidate.album_source_year && candidate.album_source_year === reviewContext.year) priority += 5;
  if (candidate.effective_artist_norm === reviewContext.artist_norm) priority += 3;
  return priority;
}

function sourceKindPriority(sourceKind) {
  if (sourceKind === "linked_sidecar_track") return 50;
  if (sourceKind === "resolved_graph_album_track") return 40;
  if (sourceKind === "resolved_graph_replacement_album_track") return 35;
  if (sourceKind === "resolved_sidecar_album_track") return 30;
  return 0;
}

async function resolveDirectSearchReview(review) {
  try {
    const items = await searchDirectCandidates(review);
    if (!items.length) return directSearchDefer("iterative_song_hardening_no_results", { candidate_count: 0 });

    const scored = items
      .map(({ item, searchBasis }, index) => scoreDirectSearchCandidate(review, item, index, searchBasis))
      .sort((left, right) => right.score - left.score || left.index - right.index);
    const accepted = scored.find((candidate) => candidate.accept_status === "accepted");
    if (accepted) {
      const runnerUp = scored.find((candidate) => candidate.item.id !== accepted.item.id);
      const ambiguityReason = directAcceptedAmbiguityReason(accepted, runnerUp);
      if (ambiguityReason) {
        return directSearchDefer("iterative_song_hardening_ambiguous_close_candidate", {
          candidate_count: items.length,
          best_score: accepted.score,
          best_result_rank: accepted.index + 1,
          best_reject_reason: ambiguityReason,
        });
      }
      return directSearchLink(accepted, items.length, runnerUp);
    }

    const best = scored[0];
    return directSearchDefer(best?.deferred_reason ?? "iterative_song_hardening_no_auto_match", {
      candidate_count: items.length,
      best_score: best?.score ?? "",
      best_result_rank: best ? best.index + 1 : "",
      best_reject_reason: best?.reject_reason ?? "",
    });
  } catch (error) {
    return directSearchDefer("iterative_song_hardening_request_error", {
      error_message: errorMessage(error),
    });
  }
}

async function searchDirectCandidates(review) {
  const title = review.title ?? "";
  const artist = review.artist_display_name ?? "";
  const titleSearch = titleSearchText(title);
  const soundtrack = isSoundtrackLenientReview(review);
  const terms = unique([
    `${artist} ${title}`.trim(),
    `${title} ${artist}`.trim(),
    titleSearch && titleSearch !== title ? `${artist} ${titleSearch}`.trim() : "",
    soundtrack ? `${titleSearch || title} soundtrack` : "",
    soundtrack ? `${titleSearch || title} original cast` : "",
    soundtrack ? titleSearch || title : "",
  ]).filter(Boolean);

  const byId = new Map();
  for (const [termIndex, term] of terms.entries()) {
    const payload = await client.catalogSearch({ term, types: "songs", limit: termIndex >= 3 ? 15 : 10 });
    for (const item of payload?.results?.songs?.data ?? []) {
      if (!item?.id || byId.has(item.id)) continue;
      byId.set(item.id, {
        item,
        searchBasis: termIndex === 0
          ? "artist_title"
          : termIndex === 1
            ? "title_artist"
            : termIndex === 2
              ? "artist_semantic_title"
              : "soundtrack_title_context",
      });
    }
  }
  return [...byId.values()];
}

function scoreDirectSearchCandidate(review, item, index, searchBasis) {
  const attrs = item.attributes ?? {};
  const expected = buildDirectExpectedIdentity(review);
  const candidate = buildDirectCandidateIdentity(attrs);
  const title = directTitleEvidence(expected, candidate);
  const artist = directArtistEvidence(expected, candidate);
  const yearDelta = yearDeltaFor(review.year, attrs.releaseDate);
  const versionFlags = candidateVersionFlags(attrs.name ?? "", review.title);
  const contextFlags = candidateContextFlags(attrs, expected, yearDelta);
  const soundtrackContext = directSoundtrackContextFor(review, attrs, expected);
  const score = directScoreFor({ title, artist, yearDelta, index, versionFlags, contextFlags, soundtrackContext, searchBasis });
  const acceptance = directAcceptanceFor({
    review,
    title,
    artist,
    yearDelta,
    versionFlags,
    contextFlags,
    soundtrackContext,
    score,
    searchBasis,
  });

  return {
    item,
    index,
    search_basis: searchBasis,
    score,
    title_match: title.match,
    artist_match: artist.match,
    artist_evidence: artist.evidence,
    artist_coverage: artist.coverage,
    year_delta: yearDelta,
    version_flags: versionFlags,
    context_flags: contextFlags,
    soundtrack_context: soundtrackContext,
    accept_status: acceptance.accept_status,
    match_basis: acceptance.match_basis,
    confidence: acceptance.confidence,
    warnings: acceptance.warnings,
    deferred_reason: acceptance.deferred_reason,
    reject_reason: acceptance.reject_reason,
  };
}

function buildDirectExpectedIdentity(review) {
  return {
    raw_title: String(review.title ?? ""),
    raw_artist: String(review.artist_display_name ?? ""),
    title_variants: titleVariants(review.title),
    artist: artistIdentity(review.artist_display_name, review.title),
    year: Number(review.year),
    soundtrack_lenient: isSoundtrackLenientReview(review),
  };
}

function buildDirectCandidateIdentity(attrs) {
  return {
    title_variants: titleVariants(attrs.name ?? ""),
    album_variants: titleVariants(attrs.albumName ?? ""),
    artist: artistIdentity(attrs.artistName ?? "", attrs.name ?? ""),
    year: Number(String(attrs.releaseDate ?? "").slice(0, 4)),
  };
}

function directTitleEvidence(expected, candidate) {
  if (hasIntersection(expected.title_variants.exact, candidate.title_variants.exact)) {
    return { match: "exact_normalized", score: 58 };
  }
  if (hasIntersection(expected.title_variants.core, candidate.title_variants.core)) {
    return { match: "core_exact_normalized", score: 50 };
  }
  if (hasIntersection(expected.title_variants.compact, candidate.title_variants.compact)) {
    return { match: "compact_exact_normalized", score: 48 };
  }
  if (hasCompatibleTitle(expected.title_variants.semantic, candidate.title_variants.semantic)) {
    return { match: "compatible_normalized", score: 34 };
  }
  return { match: "not_matched", score: 0 };
}

function directArtistEvidence(expected, candidate) {
  const expectedPrimary = expected.artist.primary;
  const candidatePrimary = candidate.artist.primary;
  const expectedNames = expected.artist.names;
  const candidateNames = candidate.artist.names;
  const expectedCompact = expected.artist.compactNames;
  const candidateCompact = candidate.artist.compactNames;
  const overlap = expectedNames.filter((name) => candidateNames.some((candidateName) => artistNameCompatible(name, candidateName))).length;
  const compactOverlap = overlapCount(expectedCompact, candidateCompact);
  const expectedCoverage = expectedNames.length ? overlap / expectedNames.length : 0;
  const compactCoverage = expectedCompact.length ? compactOverlap / expectedCompact.length : 0;
  const coverage = Math.max(expectedCoverage, compactCoverage);

  if (expectedPrimary && candidatePrimary && compact(expectedPrimary) === compact(candidatePrimary)) {
    return { match: "exact_normalized", evidence: "primary_artist_exact", score: 34, coverage: 1, expected_participant_count: expectedNames.length };
  }
  if (expectedPrimary && candidateNames.some((name) => artistNameCompatible(expectedPrimary, name))) {
    return { match: "compatible_normalized", evidence: "primary_artist_present_in_candidate_participants", score: 30, coverage, expected_participant_count: expectedNames.length };
  }
  if (candidatePrimary && expectedNames.some((name) => artistNameCompatible(name, candidatePrimary))) {
    return { match: "compatible_normalized", evidence: "candidate_primary_present_in_expected_participants", score: 28, coverage, expected_participant_count: expectedNames.length };
  }
  if (expectedNames.length > 1 && coverage >= 0.5) {
    return { match: "collaboration_participant_match", evidence: "multi_artist_participant_overlap", score: 27, coverage, expected_participant_count: expectedNames.length };
  }
  return { match: "not_matched", evidence: "artist_not_matched", score: 0, coverage: 0, expected_participant_count: expectedNames.length };
}

function directSoundtrackContextFor(review, attrs, expected) {
  const album = normalize(attrs.albumName ?? "");
  const artist = normalize(attrs.artistName ?? "");
  const title = normalize(attrs.name ?? "");
  const combined = `${album} ${artist} ${title}`;
  if (/\b(original motion picture soundtrack|motion picture soundtrack|soundtrack|original broadway cast|original cast|cast recording|film score|score)\b/u.test(combined)) {
    return "soundtrack_or_cast";
  }
  if (expected.soundtrack_lenient) return "graph_soundtrack_archetype";
  return "";
}

function directScoreFor({ title, artist, yearDelta, index, versionFlags, contextFlags, soundtrackContext, searchBasis }) {
  let score = title.score + artist.score;
  if (yearDelta === 0) score += 12;
  else if (yearDelta !== "" && yearDelta <= 2) score += 9;
  else if (yearDelta !== "" && yearDelta <= 10) score += 4;
  else if (yearDelta !== "" && yearDelta > 10) score -= 3;
  if (soundtrackContext) score += 7;
  if (searchBasis === "title_artist") score += 1;
  if (searchBasis === "artist_semantic_title") score -= 1;
  if (searchBasis === "soundtrack_title_context") score -= 6;
  score += Math.max(0, 8 - index);
  score -= blockingVersionFlags(versionFlags).length ? 30 : 0;
  score -= contextFlags.length ? 35 : 0;
  return score;
}

function directAcceptanceFor({ review, title, artist, yearDelta, versionFlags, contextFlags, soundtrackContext, score, searchBasis }) {
  const blockingVersions = blockingVersionFlags(versionFlags);
  if (blockingVersions.length) {
    return {
      accept_status: "deferred",
      deferred_reason: "iterative_song_hardening_version_term_needs_review",
      reject_reason: `version_term:${blockingVersions.join(";")}`,
    };
  }
  if (contextFlags.length) {
    return {
      accept_status: "deferred",
      deferred_reason: "iterative_song_hardening_context_term_needs_review",
      reject_reason: `context_term:${contextFlags.join(";")}`,
    };
  }

  const strongTitle = ["exact_normalized", "core_exact_normalized", "compact_exact_normalized"].includes(title.match);
  const compatibleTitle = title.match === "compatible_normalized";
  const exactArtist = artist.match === "exact_normalized";
  const participantArtist = artist.match === "collaboration_participant_match" || artist.evidence.includes("participants");
  const yearTight = yearDelta !== "" && yearDelta <= 2;
  const yearKnown = yearDelta !== "";
  const soundtrackAllowed = isSoundtrackLenientReview(review) && soundtrackContext && !isFalseNearbyCandidate(review);
  const singleArtistFeaturedOnly = artist.evidence === "primary_artist_present_in_candidate_participants"
    && artist.expected_participant_count <= 1;

  if (strongTitle && exactArtist && score >= 78) {
    return {
      accept_status: "accepted",
      match_basis: `iterative_song_hardening_${basisTitle(title.match)}_primary_artist_exact_auto_match`,
      confidence: title.match === "exact_normalized" && searchBasis !== "soundtrack_title_context" ? "high" : "medium",
      warnings: warningString([yearWarning(yearKnown, yearDelta), liveWarning(versionFlags, yearTight), soundtrackContext]),
    };
  }

  if (strongTitle && participantArtist && !singleArtistFeaturedOnly && artist.coverage >= 0.5 && score >= 80) {
    return {
      accept_status: "accepted",
      match_basis: `iterative_song_hardening_${basisTitle(title.match)}_participant_overlap_auto_match`,
      confidence: yearTight || soundtrackAllowed ? "high" : "medium",
      warnings: warningString(["participant_artist_match", yearWarning(yearKnown, yearDelta), liveWarning(versionFlags, yearTight), soundtrackContext]),
    };
  }

  if (strongTitle && singleArtistFeaturedOnly && yearTight && score >= 80) {
    return {
      accept_status: "accepted",
      match_basis: `iterative_song_hardening_${basisTitle(title.match)}_single_artist_featured_with_tight_year_auto_match`,
      confidence: "medium",
      warnings: warningString(["single_artist_appears_as_featured_credit", yearWarning(yearKnown, yearDelta), liveWarning(versionFlags, yearTight), soundtrackContext]),
    };
  }

  if (compatibleTitle && (exactArtist || participantArtist) && (yearTight || soundtrackContext) && score >= 80) {
    if (singleArtistFeaturedOnly && !yearTight) {
      return {
        accept_status: "deferred",
        deferred_reason: "iterative_song_hardening_no_auto_match",
        reject_reason: "single_artist_only_featured_without_tight_year",
      };
    }
    return {
      accept_status: "accepted",
      match_basis: "iterative_song_hardening_compatible_title_context_auto_match",
      confidence: "medium",
      warnings: warningString(["compatible_title_match", exactArtist ? "" : "participant_artist_match", yearWarning(yearKnown, yearDelta), soundtrackContext]),
    };
  }

  if (soundtrackAllowed && strongTitle && yearTight && score >= 66) {
    return {
      accept_status: "accepted",
      match_basis: `iterative_song_hardening_${basisTitle(title.match)}_soundtrack_cast_context_auto_match`,
      confidence: "medium",
      warnings: warningString(["artist_relaxed_for_soundtrack_context", yearWarning(yearKnown, yearDelta), soundtrackContext]),
    };
  }

  return {
    accept_status: "deferred",
    deferred_reason: "iterative_song_hardening_no_auto_match",
    reject_reason: !strongTitle && !compatibleTitle
      ? "title_not_matched"
        : artist.match === "not_matched" && !(soundtrackAllowed && yearTight)
        ? "artist_not_matched"
        : singleArtistFeaturedOnly
          ? "single_artist_only_featured_without_tight_year"
          : "identity_evidence_below_threshold",
  };
}

function directAcceptedAmbiguityReason(accepted, runnerUp) {
  const delta = runnerUp ? accepted.score - runnerUp.score : Number.POSITIVE_INFINITY;
  if (delta <= 0) return "accepted_candidate_not_above_runner_up";
  if (accepted.title_match === "compatible_normalized" && delta <= 2) return "compatible_title_close_runner_up";
  if (accepted.index + 1 >= 10 && delta <= 2) return "low_rank_close_runner_up";
  if (accepted.warnings?.includes("release_year_differs_likely_compilation") && delta <= 2) {
    return "compilation_candidate_close_runner_up";
  }
  return "";
}

function makeLink(review, outcome) {
  const candidate = outcome.candidate;
  const warnings = [...outcome.spec.warnings];
  if (review.review_reason === "apple_song_search_needs_review_version_risk") {
    warnings.push("prior_version_risk_resolved_by_album_source_context");
  }

  return {
    link_key: `${review.source_type}:${review.source_ref}:apple_music:song:${candidate.apple_catalog_id}:${storefront}`,
    run_version: runVersion,
    source_ref: review.source_ref,
    source_type: review.source_type,
    source_candidate_type: review.source_candidate_type,
    external_catalog: "apple_music",
    apple_catalog_id: candidate.apple_catalog_id,
    apple_resource_type: "song",
    storefront,
    match_status: outcome.spec.confidence === "high" ? "verified" : "candidate_verified",
    match_basis: `song_source_album_${candidate.source_kind}_${outcome.spec.basis_suffix}`,
    confidence: outcome.spec.confidence,
    title_match: outcome.spec.title_match,
    artist_match: outcome.spec.artist_match,
    year_delta: outcome.spec.year_mode === "context_year" ? "0" : "",
    warnings: unique(warnings).join(";"),
    candidate_source_kind: candidate.source_kind,
    sidecar_track_source_ref: candidate.source_track_ref,
    album_source_type: candidate.album_source_type,
    album_source_ref: candidate.album_source_ref,
    album_apple_catalog_id: candidate.album_apple_catalog_id,
    album_match_basis: candidate.album_match_basis,
    track_match_basis: candidate.track_match_basis,
    prior_review_reason: review.review_reason,
    verified_at: new Date().toISOString(),
    raw_payload_persisted: false,
  };
}

function makeDirectSearchLink(review, outcome) {
  const candidate = outcome.candidate;
  return {
    link_key: `${review.source_type}:${review.source_ref}:apple_music:song:${candidate.item.id}:${storefront}`,
    run_version: runVersion,
    source_ref: review.source_ref,
    source_type: review.source_type,
    source_candidate_type: review.source_candidate_type,
    external_catalog: "apple_music",
    apple_catalog_id: candidate.item.id,
    apple_resource_type: "song",
    storefront,
    match_status: candidate.confidence === "high" ? "verified" : "candidate_verified",
    match_basis: candidate.match_basis,
    confidence: candidate.confidence,
    result_rank: candidate.index + 1,
    search_basis: candidate.search_basis,
    score: candidate.score,
    score_delta_to_runner_up: outcome.score_delta_to_runner_up,
    title_match: candidate.title_match,
    artist_match: candidate.artist_match,
    artist_evidence: candidate.artist_evidence,
    artist_coverage: candidate.artist_coverage,
    year_delta: candidate.year_delta,
    warnings: candidate.warnings,
    candidate_source_kind: "direct_catalog_song_search",
    prior_review_reason: review.prior_review_reason,
    prior_best_reject_reason: review.prior_best_reject_reason,
    candidate_count: outcome.candidate_count,
    verified_at: new Date().toISOString(),
    raw_payload_persisted: false,
  };
}

function directSearchLink(candidate, candidateCount, runnerUp) {
  return {
    kind: "link",
    candidate,
    candidate_count: candidateCount,
    score_delta_to_runner_up: runnerUp ? candidate.score - runnerUp.score : "",
  };
}

function directSearchDefer(reason, fields = {}) {
  return {
    kind: "deferred",
    reason,
    candidate_count: fields.candidate_count ?? "",
    candidate_apple_id_count: fields.candidate_apple_id_count ?? "",
    strongest_basis_suffix: fields.strongest_basis_suffix ?? "",
    best_score: fields.best_score ?? "",
    best_result_rank: fields.best_result_rank ?? "",
    best_reject_reason: fields.best_reject_reason ?? "",
    error_message: fields.error_message ?? "",
  };
}

function makeDeferred(review, outcome) {
  return {
    deferred_key: `${review.source_type}:${review.source_ref}:${outcome.reason}`,
    run_version: runVersion,
    source_ref: review.source_ref,
    source_type: review.source_type,
    source_candidate_type: review.source_candidate_type,
    artist_display_name: review.artist_display_name,
    title: review.title,
    year: review.year,
    storefront,
    deferred_reason: outcome.reason,
    candidate_count: outcome.candidate_count ?? "",
    candidate_apple_id_count: outcome.candidate_apple_id_count ?? "",
    strongest_basis_suffix: outcome.strongest_basis_suffix ?? "",
    best_score: outcome.best_score ?? "",
    best_result_rank: outcome.best_result_rank ?? "",
    best_reject_reason: outcome.best_reject_reason ?? "",
    prior_review_reason: review.prior_review_reason || review.review_reason,
    prior_best_reject_reason: review.prior_best_reject_reason ?? "",
    error_message: outcome.error_message ?? "",
    raw_payload_persisted: false,
  };
}

function writeFinalArtifacts() {
  const sortedLinks = [...links].sort((a, b) => a.link_key.localeCompare(b.link_key));
  const sortedDeferred = [...deferred].sort((a, b) => a.deferred_key.localeCompare(b.deferred_key));
  const summary = buildSummary(sortedLinks, sortedDeferred);

  fs.writeFileSync(linksPath, sortedLinks.length ? `${sortedLinks.map((link) => JSON.stringify(link)).join("\n")}\n` : "");
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
    "candidate_apple_id_count",
    "strongest_basis_suffix",
    "best_score",
    "best_result_rank",
    "best_reject_reason",
    "prior_review_reason",
    "prior_best_reject_reason",
    "error_message",
    "raw_payload_persisted",
  ]);
  fs.writeFileSync(summaryPath, `${JSON.stringify(summary, null, 2)}\n`);
  fs.writeFileSync(manifestPath, buildManifest(summary));
  console.log(JSON.stringify(summary, null, 2));
}

function buildSummary(sortedLinks, sortedDeferred) {
  const albumFetchFailures = albumFetchResults.filter((row) => row.status !== "ok");
  return {
    run_version: runVersion,
    status: "complete",
    generated_at: new Date().toISOString(),
    storefront,
    policy: {
      raw_apple_payloads_persisted: false,
      apple_catalog_requests: args.dryRun ? "none_dry_run" : "sparse_album_tracks_and_song_search_transient_only",
      persisted_catalog_fields: ["apple_catalog_id", "apple_resource_type", "storefront", "source refs", "match metadata"],
      excluded_persistent_fields: ["artwork", "previews", "lyrics", "raw_catalog_payload", "music_user_token", "apple_track_title", "apple_track_artist", "apple_album_name"],
    },
    inputs: Object.fromEntries(linkInputSpecs.map(([key, relativePath]) => [key, `data/canonical_graph/current/${relativePath}`])),
    counts: {
      graph_song_total: graphSongRows.length,
      preexisting_graph_song_recording_linked_sources: existingGraphSongLinkKeys.size,
      unresolved_graph_song_rows_before_pass: allReviewRows.length,
      graph_song_rows_considered: reviewRows.length,
      sidecar_track_candidates_with_apple_ids: sidecarCandidates.length,
      resolved_album_contexts: [...albumContextByAppleId.values()].reduce((sum, rows) => sum + rows.length, 0),
      resolved_album_ids_fetched: albumFetchResults.length,
      resolved_album_fetch_failures: albumFetchFailures.length,
      transient_resolved_album_track_candidates: albumTrackCandidates.length,
      all_track_candidates: allCandidates.length,
      new_links_total: sortedLinks.length,
      deferred_total: sortedDeferred.length,
      projected_review_rows_remaining_after_pass: sortedDeferred.length,
      new_links_by_source_type: countBy(sortedLinks, "source_type"),
      new_links_by_candidate_source_kind: countBy(sortedLinks, "candidate_source_kind"),
      new_links_by_match_basis: countBy(sortedLinks, "match_basis"),
      new_links_by_confidence: countBy(sortedLinks, "confidence"),
      new_links_by_prior_review_reason: countBy(sortedLinks, "prior_review_reason"),
      deferred_by_reason: countBy(sortedDeferred, "deferred_reason"),
      deferred_by_best_reject_reason: countBy(sortedDeferred, "best_reject_reason"),
      album_fetch_failures_by_status: countBy(albumFetchFailures, "status"),
    },
  };
}

function buildManifest(summary) {
  return `# Apple Music Graph Song Iterative Hardening Pass v1

Generated: ${summary.generated_at}

Status: \`${summary.status}\`

Storefront: \`${summary.storefront}\`

## Policy

- Raw Apple payloads persisted: \`false\`
- Apple catalog requests are sparse and transient: \`${summary.policy.apple_catalog_requests}\`
- Durable output stores Apple catalog IDs, resource type, storefront, source refs, and compact matching metadata only.
- Apple track names/artists/albums fetched for matching are not written to output artifacts.

## Intent

This pass targets currently unresolved \`graph_song\` rows after the prior Apple Music song passes.

It runs two stages:

1. Album sidecar tracks that already have Apple song IDs from any current pass.
2. Sparse track listings fetched transiently from already-resolved graph album and graph replacement album IDs.
3. Direct Apple Music song search with stronger title normalization, artist alias handling, compilation tolerance, and soundtrack/cast/score leniency.

## Counts

- Graph song rows before pass: ${summary.counts.unresolved_graph_song_rows_before_pass}
- Graph song rows considered: ${summary.counts.graph_song_rows_considered}
- Sidecar track candidates with Apple IDs: ${summary.counts.sidecar_track_candidates_with_apple_ids}
- Resolved album contexts: ${summary.counts.resolved_album_contexts}
- Resolved album IDs fetched: ${summary.counts.resolved_album_ids_fetched}
- Transient resolved-album track candidates: ${summary.counts.transient_resolved_album_track_candidates}
- New links total: ${summary.counts.new_links_total}
- Deferred rows: ${summary.counts.deferred_total}

## New Links By Candidate Source

${tableFromCounts(summary.counts.new_links_by_candidate_source_kind)}

## New Links By Match Basis

${tableFromCounts(summary.counts.new_links_by_match_basis)}

## Deferred By Reason

${tableFromCounts(summary.counts.deferred_by_reason)}
`;
}

function isGraphSongLink(link) {
  return (link.source_type === "graph_song" || link.source_type === "graph_recording") && link.apple_resource_type === "song";
}

function isAcceptedLink(link) {
  return ["verified", "candidate_verified"].includes(link.match_status);
}

function graphSourceKey(sourceType, sourceRef) {
  return `${sourceType}:${sourceRef}`;
}

function sourceTrackDisplayRef(candidate) {
  return candidate.source_track_ref || `${candidate.album_source_type}:${candidate.album_source_ref}:${candidate.apple_catalog_id}`;
}

function candidateKey(candidate) {
  return [
    candidate.source_kind,
    candidate.album_source_type,
    candidate.album_source_ref,
    candidate.album_apple_catalog_id,
    sourceTrackDisplayRef(candidate),
    candidate.apple_catalog_id,
  ].join("|");
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

function titleExactKeys(value) {
  return titleVariants(value).exact;
}

function titleCoreKeys(value) {
  return titleVariants(value).core;
}

function titleVariants(value) {
  const withoutFeature = removeFeaturedTitleText(value);
  const withoutVersion = removeVersionDescriptors(withoutFeature);
  const themeVariants = themeTitleVariants(withoutVersion);
  const semanticVariants = semanticTitleVariants(withoutVersion);
  const exact = unique([
    normalize(value),
    normalize(withoutFeature),
    normalize(withoutVersion),
    ...themeVariants.map(normalize),
  ]).filter(Boolean);
  const core = unique([
    normalizeTitleCore(value),
    normalizeTitleCore(withoutFeature),
    normalizeTitleCore(withoutVersion),
    ...themeVariants.map(normalizeTitleCore),
    ...semanticVariants.map(normalizeTitleCore),
  ]).filter(Boolean);
  const semantic = unique([...exact, ...core, ...semanticVariants.map(normalizeTitleCore)]).filter(Boolean);
  const compactVariants = unique([...exact, ...core, ...semantic].map(compact)).filter(Boolean);
  return { exact, core, semantic, compact: compactVariants };
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

function normalizeTitleCore(value) {
  return normalize(removeVersionDescriptors(removeFeaturedTitleText(value)))
    .replace(/\b(remaster(ed)?|mono|stereo|single|album|version|edit|deluxe|expanded|anniversary|bonus|track|explicit|clean|radio|soundtrack)\b/g, " ")
    .replace(/\b(19|20)\d{2}\b/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function stripFeaturing(value) {
  return removeFeaturedTitleText(value);
}

function compatibleNames(candidate, expected) {
  if (!candidate || !expected) return false;
  return candidate === expected || candidate.includes(expected) || expected.includes(candidate);
}

function hasIntersection(left, right) {
  const rightSet = new Set(right);
  return left.some((value) => rightSet.has(value));
}

function hasCompatibleTitle(left, right) {
  return left.some((leftValue) => right.some((rightValue) => compatibleTitleValues(leftValue, rightValue)));
}

function compatibleTitleValues(left, right) {
  if (!left || !right) return false;
  if (left === right) return true;
  if (left.length < 5 || right.length < 5) return false;
  const leftTokens = tokenSet(left);
  const rightTokens = tokenSet(right);
  if (leftTokens.length < 2 && rightTokens.length < 2) return false;
  const shorter = leftTokens.length <= rightTokens.length ? leftTokens : rightTokens;
  const longer = leftTokens.length <= rightTokens.length ? rightTokens : leftTokens;
  if (shorter.length < 2) return false;
  return shorter.every((token) => longer.includes(token));
}

function artistIdentity(artistName, title) {
  const names = unique([
    ...splitArtistNames(artistName),
    ...extractFeaturedArtists(title),
  ]).filter(Boolean);
  return {
    primary: names[0] ?? "",
    names,
    compactNames: unique(names.map(compact)).filter(Boolean),
  };
}

function splitArtistNames(value) {
  return String(value ?? "")
    .replace(/\s+x\s+/giu, " and ")
    .replace(/\s+with\s+/giu, " and ")
    .replace(/\s+vs\.?\s+/giu, " and ")
    .replace(/\s+presents\s+/giu, " and ")
    .split(/\s*(?:,|&|\band\b|\bfeat\.?\b|\bft\.?\b|\bfeaturing\b|\+)\s*/giu)
    .flatMap((part) => roleCreditVariants(part))
    .flatMap((part) => artistAliasVariants(part))
    .map((part) => normalize(part))
    .filter(Boolean);
}

function roleCreditVariants(value) {
  const text = String(value ?? "").trim();
  const match = text.match(/^(.+?)\s+as\s+(.+)$/iu);
  if (!match) return [text];
  return [match[1], match[2]];
}

function artistAliasVariants(value) {
  const base = String(value ?? "").trim();
  const normalized = normalize(base);
  const variants = [base];
  if (normalized.endsWith(" orchestra")) variants.push(normalized.replace(/\s+orchestra$/u, ""));
  if (normalized.endsWith(" band")) variants.push(normalized.replace(/\s+band$/u, ""));
  if (normalized === "ceelo green") variants.push("cee lo green");
  if (normalized === "cee lo green") variants.push("ceelo green");
  if (normalized === "run dmc") variants.push("run d m c");
  if (normalized === "john barry orchestra") variants.push("john barry");
  if (normalized.includes("cookie monster")) variants.push("cookie monster", "sesame street");
  if (normalized.includes("ernie")) variants.push("ernie", "sesame street");
  return variants;
}

function extractFeaturedArtists(title) {
  const text = String(title ?? "");
  const matches = [];
  for (const match of text.matchAll(/(?:feat\.?|ft\.?|featuring)\s+([^\])]+)/giu)) {
    matches.push(...splitArtistNames(match[1]));
  }
  return matches;
}

function artistNameCompatible(left, right) {
  if (!left || !right) return false;
  if (left === right || compact(left) === compact(right)) return true;
  const leftTokens = tokenSet(left);
  const rightTokens = tokenSet(right);
  if (!leftTokens.length || !rightTokens.length) return false;
  if (leftTokens.length === 1) {
    return leftTokens[0].length >= 4 && rightTokens.includes(leftTokens[0]);
  }
  return leftTokens.every((token) => rightTokens.includes(token));
}

function overlapCount(left, right) {
  const rightSet = new Set(right);
  return left.filter((value) => rightSet.has(value)).length;
}

function tokenSet(value) {
  return normalize(value).split(/\s+/gu).filter(Boolean);
}

function compact(value) {
  return String(value ?? "").replace(/[^a-z0-9]+/gu, "");
}

function titleSearchText(value) {
  const variants = semanticTitleVariants(value).map((variant) => variant.trim()).filter(Boolean);
  return variants[0] ?? String(value ?? "");
}

function semanticTitleVariants(value) {
  const text = String(value ?? "").trim();
  const variants = [];
  variants.push(text.replace(/\s*[\[(][^\])]+[\])]\s*/gu, " ").trim());
  variants.push(text.replace(/\s+part\s+(one|two|three|i|ii|iii|1|2|3)\b/giu, " part $1").trim());
  if (/^(.+?)\s*[:\-]\s+.+$/u.test(text)) variants.push(text.replace(/^(.+?)\s*[:\-]\s+.+$/u, "$1").trim());
  return unique(variants).filter((variant) => variant && variant !== text);
}

function themeTitleVariants(value) {
  const text = String(value ?? "");
  const variants = [];
  const fromMatch = text.match(/^theme from (.+)$/iu);
  if (fromMatch) variants.push(`${fromMatch[1]} theme`, `${fromMatch[1]} main theme`, `main title ${fromMatch[1]}`);
  const mainTitleMatch = text.match(/^main title from (.+)$/iu);
  if (mainTitleMatch) variants.push(`main title ${mainTitleMatch[1]}`, `${mainTitleMatch[1]} main title`);
  return variants;
}

function removeFeaturedTitleText(value) {
  return String(value ?? "")
    .replace(/\s*[\[(][^\])]*(feat\.?|ft\.?|featuring)[^\])]*[\])]\s*/giu, " ")
    .replace(/\b(feat\.?|ft\.?|featuring)\b.*$/iu, "")
    .trim();
}

function removeVersionDescriptors(value) {
  return String(value ?? "")
    .replace(/\s*[\[(](?:\d{4}\s+)?(?:re)?master(?:ed)?[^)\]]*[\])]/giu, " ")
    .replace(/\s*[\[(](?:single|album|radio|mono|stereo|clean|explicit|soundtrack)\s+(?:version|edit)?[^)\]]*[\])]/giu, " ")
    .replace(/\s*[\[(](?:version|edit|bonus track)[^)\]]*[\])]/giu, " ")
    .trim();
}

function candidateVersionFlags(candidateTitle, expectedTitle) {
  const candidate = normalize(candidateTitle);
  const expected = normalize(expectedTitle);
  const flags = [];
  const terms = ["live", "en vivo", "morning evening", "morning and evening", "club mix", "dj mix", "mix", "mixed", "remix", "rework", "dub", "radio edit", "club rub", "disco trip", "extended version", "spanish version", "new vocal", "urban assault vehicle", "karaoke", "tribute", "cover", "demo", "instrumental", "a cappella", "acappella", "acapella", "acoustic", "interview", "sped up", "slowed", "nightcore", "arr", "arranged", "re recorded", "rerecorded", "home tape"];
  for (const term of terms) {
    if (candidate.includes(term) && !expected.includes(term)) flags.push(term.replace(/\s+/g, "_"));
  }
  if (expected.includes("remix") && !candidate.includes("remix") && !candidate.includes("mix")) {
    flags.push("expected_remix_missing");
  }
  return unique(flags);
}

function blockingVersionFlags(flags) {
  return flags;
}

function candidateContextFlags(attrs, expected, yearDelta) {
  const expectedPrimary = normalize(expected.artist.primary);
  const expectedText = normalize(`${expected.raw_artist} ${expected.raw_title}`);
  const expectedCastLike = expected.soundtrack_lenient || /\b(cast|chorus|disney|broadway|london|motion picture|soundtrack)\b/u.test(expectedText);
  const expectedScoreLike = expected.soundtrack_lenient || /\b(theme|main title|score|from|soundtrack)\b/u.test(expectedText);
  const title = normalize(attrs.name ?? "");
  const artist = normalize(attrs.artistName ?? "");
  const album = normalize(attrs.albumName ?? "");
  const combined = `${title} ${artist} ${album}`;
  const flags = [];
  const disallowed = ["tribute", "karaoke", "lullaby", "lullabies", "rendition", "renditions", "cover", "made famous", "style of", "originally performed", "en vivo", "morning evening", "morning and evening", "dj mix", "remix", "remixes", "rework", "radio edit", "club rub", "disco trip", "extended version", "spanish version", "new vocal", "urban assault vehicle", "a cappella", "acappella", "acapella", "acoustic", "interview", "re recorded", "rerecorded", "home tape"];
  for (const term of disallowed) {
    if (combined.includes(term) && !expectedText.includes(term)) flags.push(term.replace(/\s+/g, "_"));
  }
  if (/\blive\b/u.test(album) && !/\blive\b/u.test(expectedText)) flags.push("album_live");
  if (expectedPrimary && (artist.includes(`${expectedPrimary} jr`) || artist.includes(`${expectedPrimary} junior`))) flags.push("artist_suffix_jr");
  if (/\b(original broadway cast|original cast recording|broadway cast)\b/u.test(album) && !expectedCastLike && !expectedScoreLike) {
    flags.push("unexpected_cast_context");
  }
  const participantCount = splitArtistNames(attrs.artistName ?? "").length;
  if (
    participantCount >= 4
    && yearDelta !== ""
    && yearDelta > 10
    && !isCompilationLike(album)
    && !expectedCastLike
    && !expectedScoreLike
  ) {
    flags.push("later_reperformance_context");
  }
  return unique(flags);
}

function isCompilationLike(albumNorm) {
  return /\b(best|greatest|essential|collection|anthology|complete|singles|hits|remaster|remastered|legacy|playlist|profile|profiles|ultimate|retrospective|box|classics)\b/u.test(albumNorm);
}

function isSoundtrackLenientReview(review) {
  const ids = new Set(review.archetype_ids ?? []);
  if (["104", "105", "106", "107", "114"].some((id) => ids.has(id))) return true;
  const text = normalize(`${(review.archetypes ?? []).join(" ")} ${review.artist_display_name} ${review.title}`);
  return /\b(soundtrack|score|film|movie|disney|broadway|cast|musical|theme|main title)\b/u.test(text);
}

function isFalseNearbyCandidate(review) {
  return (review.import_classes ?? []).includes("false_nearby_candidate");
}

function liveWarning(flags, yearTight) {
  if (!flags.includes("live")) return "";
  return yearTight ? "live_recording_context" : "live_recording_context_year_not_tight";
}

function warningString(values) {
  return unique(values.filter(Boolean)).join(";");
}

function basisTitle(match) {
  if (match === "exact_normalized") return "exact_title";
  if (match === "core_exact_normalized") return "core_title";
  if (match === "compact_exact_normalized") return "compact_title";
  return "compatible_title";
}

function yearDeltaFor(expectedYear, releaseDate) {
  const expected = Number(expectedYear);
  const candidate = Number(String(releaseDate ?? "").slice(0, 4));
  if (!Number.isFinite(expected) || !Number.isFinite(candidate)) return "";
  return Math.abs(expected - candidate);
}

function yearWarning(yearKnown, yearDelta) {
  if (!yearKnown || yearDelta === 0) return "";
  if (yearDelta > 10) return "release_year_differs_likely_compilation";
  return "release_year_differs";
}

function normalize(value) {
  return String(value ?? "")
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/['’`´]/g, "")
    .replace(/\*/g, "")
    .replace(/&/g, " and ")
    .replace(/[^a-z0-9]+/g, " ")
    .trim()
    .replace(/\bthe\b/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

function pushIndex(map, key, value) {
  if (!key) return;
  if (!map.has(key)) map.set(key, []);
  map.get(key).push(value);
}

function unique(values) {
  return [...new Set(values)];
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

function errorMessage(error) {
  if (error instanceof Error) return error.message;
  return String(error ?? "unknown_error");
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function safeReadJson(file) {
  return fs.existsSync(file) ? readJson(file) : null;
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
