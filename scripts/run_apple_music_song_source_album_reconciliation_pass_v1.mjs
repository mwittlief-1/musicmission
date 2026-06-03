#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { createAppleMusicCatalogClient } from "./lib/appleMusicCatalogClient.mjs";

const repoRoot = process.cwd();
const currentRoot = path.join(repoRoot, "data/canonical_graph/current");
const outputRoot = path.join(currentRoot, "apple_music_song_source_album_reconciliation_pass_v1");
const runVersion = "apple_music_song_source_album_reconciliation_pass_v1";

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

const linksPath = path.join(outputRoot, "apple_music_song_source_album_reconciliation_links_v1.jsonl");
const deferredPath = path.join(outputRoot, "apple_music_song_source_album_reconciliation_deferred_queue.csv");
const summaryPath = path.join(outputRoot, "apple_music_song_source_album_reconciliation_summary.json");
const manifestPath = path.join(outputRoot, "apple_music_song_source_album_reconciliation_manifest.md");

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
  ["sidecar_track_album_bound_links", "apple_music_sidecar_track_album_bound_pass_v1/apple_music_sidecar_track_album_bound_links_v1.jsonl"],
  ["direct_song_hardening_v1_links", "apple_music_direct_song_hardening_pass_v1/apple_music_direct_song_hardening_links_v1.jsonl"],
  ["direct_song_hardening_v2_links", "apple_music_direct_song_hardening_pass_v2/apple_music_direct_song_hardening_v2_links.jsonl"],
  ["recording_hardening_links", "apple_music_recording_hardening_pass_v1/apple_music_recording_hardening_links_v1.jsonl"],
  ["graph_song_iterative_hardening_links", "apple_music_graph_song_iterative_hardening_pass_v1/apple_music_graph_song_iterative_hardening_links_v1.jsonl"],
];

const graphRows = readJson(path.join(currentRoot, "graph_linking_node_set.json")).rows;
const graphRowsByRef = new Map(graphRows.map((row) => [row.candidate_identity_key, row]));
const sidecarAlbumRows = readCsv(path.join(currentRoot, "album_track_sidecar_album_resolution.csv"));
const sidecarAlbumRowsByRef = new Map(sidecarAlbumRows.map((row) => [row.candidate_identity_key, row]));
const sidecarTrackRows = readCsv(path.join(currentRoot, "album_track_sidecar_tracks.csv"));
const firstPassReviews = readCsv(path.join(currentRoot, "apple_music_link_pass_v1/apple_music_manual_review_queue.csv"));
const replacementRows = safeReadJson(path.join(currentRoot, "apple_music_album_graph_decision_pass_v1/apple_music_album_graph_replacement_nodes_v1.json"))?.rows ?? [];
const replacementRowsByRef = new Map(replacementRows.map((row) => [row.candidate_identity_key, row]));

const existingLinks = linkInputSpecs.flatMap(([, relativePath]) => safeReadJsonl(path.join(currentRoot, relativePath)));
const existingGraphSongLinkKeys = new Set(
  existingLinks
    .filter((link) => isGraphSongLink(link) && isAcceptedLink(link))
    .map((link) => graphSourceKey(link.source_type, link.source_ref)),
);

const reviewRows = firstPassReviews
  .filter((row) => row.source_type === "graph_song" || row.source_type === "graph_recording")
  .filter((row) => !existingGraphSongLinkKeys.has(graphSourceKey(row.source_type, row.source_ref)));

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

for (const review of reviewRows) {
  const outcome = resolveReview(review);
  if (outcome.kind === "link") {
    const sourceKey = graphSourceKey(review.source_type, review.source_ref);
    if (outputGraphSourceKeys.has(sourceKey)) continue;
    const link = makeLink(review, outcome);
    links.push(link);
    outputGraphSourceKeys.add(sourceKey);
  } else {
    deferred.push(makeDeferred(review, outcome));
  }
}

writeFinalArtifacts();

function parseArgs(argv) {
  const parsed = {
    storefront: "us",
    concurrency: 6,
    maxRetries: 8,
    limitAlbums: Number.NaN,
    progressEvery: 100,
    dryRun: false,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--storefront") parsed.storefront = argv[++index];
    else if (arg === "--concurrency") parsed.concurrency = Number(argv[++index]);
    else if (arg === "--max-retries") parsed.maxRetries = Number(argv[++index]);
    else if (arg === "--limit-albums") parsed.limitAlbums = Number(argv[++index]);
    else if (arg === "--progress-every") parsed.progressEvery = Number(argv[++index]);
    else if (arg === "--dry-run") parsed.dryRun = true;
  }

  if (!parsed.storefront) parsed.storefront = "us";
  if (!Number.isFinite(parsed.concurrency) || parsed.concurrency < 1) parsed.concurrency = 1;
  if (parsed.concurrency > 12) parsed.concurrency = 12;
  if (!Number.isFinite(parsed.maxRetries) || parsed.maxRetries < 0) parsed.maxRetries = 3;
  if (!Number.isFinite(parsed.progressEvery) || parsed.progressEvery < 1) parsed.progressEvery = 100;
  return parsed;
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

function resolveReview(review) {
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
    prior_review_reason: review.review_reason,
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
    "prior_review_reason",
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
      apple_catalog_requests: args.dryRun ? "none_dry_run" : "sparse_album_tracks_transient_only",
      persisted_catalog_fields: ["apple_catalog_id", "apple_resource_type", "storefront", "source refs", "match metadata"],
      excluded_persistent_fields: ["artwork", "previews", "lyrics", "raw_catalog_payload", "music_user_token", "apple_track_title", "apple_track_artist"],
    },
    inputs: Object.fromEntries(linkInputSpecs.map(([key, relativePath]) => [key, `data/canonical_graph/current/${relativePath}`])),
    counts: {
      first_pass_graph_song_recording_review_rows: firstPassReviews.filter((row) => row.source_type === "graph_song" || row.source_type === "graph_recording").length,
      preexisting_graph_song_recording_linked_sources: existingGraphSongLinkKeys.size,
      graph_song_recording_review_rows_considered: reviewRows.length,
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
      album_fetch_failures_by_status: countBy(albumFetchFailures, "status"),
    },
  };
}

function buildManifest(summary) {
  return `# Apple Music Song Source Album Reconciliation Pass v1

Generated: ${summary.generated_at}

Status: \`${summary.status}\`

Storefront: \`${summary.storefront}\`

## Policy

- Raw Apple payloads persisted: \`false\`
- Apple catalog requests are sparse and transient: \`${summary.policy.apple_catalog_requests}\`
- Durable output stores Apple catalog IDs, resource type, storefront, source refs, and compact matching metadata only.
- Apple track names/artists fetched for matching are not written to output artifacts.

## Intent

This pass reconciles unresolved first-pass graph song/recording rows against two album-backed sources:

1. Album sidecar tracks that already have Apple song IDs from any current pass.
2. Sparse track listings fetched transiently from already-resolved graph album and graph replacement album IDs.

## Counts

- Graph song/recording review rows considered: ${summary.counts.graph_song_recording_review_rows_considered}
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
  return unique([
    normalize(value),
    normalize(stripFeaturing(value)),
  ]).filter(Boolean);
}

function titleCoreKeys(value) {
  const exact = new Set(titleExactKeys(value));
  return unique([
    normalizeTitleCore(value),
    normalizeTitleCore(stripFeaturing(value)),
  ]).filter((key) => key && !exact.has(key));
}

function normalize(value) {
  return String(value ?? "")
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/['’]/g, "")
    .replace(/&/g, " and ")
    .replace(/[^a-z0-9]+/g, " ")
    .trim()
    .replace(/\bthe\b/g, "")
    .replace(/\s+/g, " ")
    .trim();
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
