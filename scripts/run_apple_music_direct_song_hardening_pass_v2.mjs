#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { createAppleMusicCatalogClient } from "./lib/appleMusicCatalogClient.mjs";

const repoRoot = process.cwd();
const currentRoot = path.join(repoRoot, "data/canonical_graph/current");
const outputRoot = path.join(currentRoot, "apple_music_direct_song_hardening_pass_v2");
const runVersion = "apple_music_direct_song_hardening_pass_v2";

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

const linksPath = path.join(outputRoot, "apple_music_direct_song_hardening_v2_links.jsonl");
const deferredPath = path.join(outputRoot, "apple_music_direct_song_hardening_v2_deferred_queue.csv");
const summaryPath = path.join(outputRoot, "apple_music_direct_song_hardening_v2_summary.json");
const manifestPath = path.join(outputRoot, "apple_music_direct_song_hardening_v2_manifest.md");

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
];

const sourceQueue = readCsv(path.join(
  currentRoot,
  "apple_music_direct_song_hardening_pass_v1/apple_music_direct_song_hardening_deferred_queue.csv",
));
const existingLinks = linkInputSpecs.flatMap(([, relativePath]) => safeReadJsonl(path.join(currentRoot, relativePath)));
const existingGraphSongLinkKeys = new Set(
  existingLinks
    .filter((link) => isGraphSongLink(link) && isAcceptedLink(link))
    .map((link) => graphSourceKey(link.source_type, link.source_ref)),
);

const jobs = sourceQueue
  .filter((row) => row.source_type === "graph_song")
  .filter((row) => !existingGraphSongLinkKeys.has(graphSourceKey(row.source_type, row.source_ref)))
  .sort((left, right) => left.source_ref.localeCompare(right.source_ref));
const selectedJobs = Number.isFinite(args.limit) ? jobs.slice(0, args.limit) : jobs;
const links = [];
const deferred = [];
let processed = 0;

console.error(JSON.stringify({
  run_version: runVersion,
  storefront,
  selected_jobs: selectedJobs.length,
  concurrency: args.concurrency,
  dry_run: args.dryRun,
}, null, 2));

await runPool(selectedJobs, args.concurrency, async (job) => {
  const outcome = args.dryRun ? dryRunOutcome() : await resolveJob(job);
  recordOutcome(job, outcome);
  processed += 1;
  if (processed % args.progressEvery === 0 || processed === selectedJobs.length) {
    console.error(`direct song hardening v2: ${processed}/${selectedJobs.length}, links=${links.length}, deferred=${deferred.length}`);
  }
});

writeFinalArtifacts();

function parseArgs(argv) {
  const parsed = {
    storefront: "us",
    concurrency: 8,
    maxRetries: 8,
    limit: Number.NaN,
    progressEvery: 50,
    dryRun: false,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--storefront") parsed.storefront = argv[++index];
    else if (arg === "--concurrency") parsed.concurrency = Number(argv[++index]);
    else if (arg === "--max-retries") parsed.maxRetries = Number(argv[++index]);
    else if (arg === "--limit") parsed.limit = Number(argv[++index]);
    else if (arg === "--progress-every") parsed.progressEvery = Number(argv[++index]);
    else if (arg === "--dry-run") parsed.dryRun = true;
  }

  if (!parsed.storefront) parsed.storefront = "us";
  if (!Number.isFinite(parsed.concurrency) || parsed.concurrency < 1) parsed.concurrency = 1;
  if (parsed.concurrency > 12) parsed.concurrency = 12;
  if (!Number.isFinite(parsed.maxRetries) || parsed.maxRetries < 0) parsed.maxRetries = 3;
  if (!Number.isFinite(parsed.progressEvery) || parsed.progressEvery < 1) parsed.progressEvery = 50;
  return parsed;
}

async function resolveJob(job) {
  const query = `${job.artist_display_name} ${job.title}`.trim();
  try {
    const payload = await client.catalogSearch({ term: query, types: "songs", limit: 10 });
    const items = payload?.results?.songs?.data ?? [];
    if (!items.length) return deferOutcome("direct_song_hardening_v2_no_results", { candidate_count: 0 });

    const scored = items
      .map((item, index) => scoreSongCandidate(job, item, index))
      .sort((left, right) => right.score - left.score || left.index - right.index);
    const accepted = scored.find((candidate) => candidate.accept_status === "accepted");
    if (accepted) {
      const runnerUp = scored.find((candidate) => candidate.item.id !== accepted.item.id);
      return linkOutcome(accepted, items.length, runnerUp);
    }

    const best = scored[0];
    return deferOutcome(best?.deferred_reason ?? "direct_song_hardening_v2_no_auto_match", {
      candidate_count: items.length,
      best_score: best?.score ?? "",
      best_result_rank: best ? best.index + 1 : "",
      best_reject_reason: best?.reject_reason ?? "",
    });
  } catch (error) {
    return deferOutcome("direct_song_hardening_v2_request_error", {
      candidate_count: "",
      best_score: "",
      best_result_rank: "",
      best_reject_reason: "",
      error_message: errorMessage(error),
    });
  }
}

function scoreSongCandidate(job, item, index) {
  const attrs = item.attributes ?? {};
  const expected = buildExpectedIdentity(job.title, job.artist_display_name, job.year);
  const candidate = buildCandidateIdentity(attrs.name ?? "", attrs.artistName ?? "", String(attrs.releaseDate ?? "").slice(0, 4));
  const title = titleEvidence(expected, candidate);
  const artist = artistEvidence(expected, candidate);
  const yearDelta = yearDeltaFor(job.year, attrs.releaseDate);
  const versionFlags = candidateVersionFlags(attrs.name ?? "", job.title);
  const contextFlags = candidateContextFlags(attrs, expected.artist.primary);
  const score = scoreFor({ title, artist, yearDelta, index, versionFlags, contextFlags });
  const acceptance = acceptanceFor({ title, artist, yearDelta, versionFlags, contextFlags, score });

  return {
    item,
    index,
    score,
    title_match: title.match,
    artist_match: artist.match,
    artist_evidence: artist.evidence,
    year_delta: yearDelta,
    version_flags: versionFlags,
    context_flags: contextFlags,
    accept_status: acceptance.accept_status,
    match_basis: acceptance.match_basis,
    confidence: acceptance.confidence,
    warnings: acceptance.warnings,
    deferred_reason: acceptance.deferred_reason,
    reject_reason: acceptance.reject_reason,
  };
}

function buildExpectedIdentity(title, artist, year) {
  return {
    title_variants: titleVariants(title),
    artist: artistIdentity(artist, ""),
    year: Number(year),
  };
}

function buildCandidateIdentity(title, artist, year) {
  return {
    title_variants: titleVariants(title),
    artist: artistIdentity(artist, title),
    year: Number(year),
  };
}

function titleEvidence(expected, candidate) {
  if (hasIntersection(expected.title_variants.exact, candidate.title_variants.exact)) {
    return { match: "exact_normalized", score: 58 };
  }
  if (hasIntersection(expected.title_variants.core, candidate.title_variants.core)) {
    return { match: "core_exact_normalized", score: 49 };
  }
  if (hasIntersection(expected.title_variants.compact, candidate.title_variants.compact)) {
    return { match: "compact_exact_normalized", score: 48 };
  }
  if (hasCompatibleTitle(expected.title_variants.core, candidate.title_variants.core)) {
    return { match: "compatible_normalized", score: 28 };
  }
  return { match: "not_matched", score: 0 };
}

function artistEvidence(expected, candidate) {
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

  if (expectedPrimary && candidatePrimary && artistNameCompatible(expectedPrimary, candidatePrimary)) {
    return { match: "exact_normalized", evidence: "primary_artist_exact", score: 34, coverage: 1 };
  }
  if (expectedPrimary && candidateNames.some((name) => artistNameCompatible(expectedPrimary, name))) {
    return {
      match: "compatible_normalized",
      evidence: "primary_artist_present_in_candidate_participants",
      score: 30,
      coverage: Math.max(expectedCoverage, compactCoverage),
      expected_participant_count: expectedNames.length,
      candidate_primary_matches_expected_primary: false,
    };
  }
  if (candidatePrimary && expectedNames.some((name) => artistNameCompatible(name, candidatePrimary))) {
    return {
      match: "compatible_normalized",
      evidence: "candidate_primary_present_in_expected_participants",
      score: 28,
      coverage: Math.max(expectedCoverage, compactCoverage),
      expected_participant_count: expectedNames.length,
      candidate_primary_matches_expected_primary: false,
    };
  }
  if (expectedNames.length > 1 && (expectedCoverage >= 0.5 || compactCoverage >= 0.5)) {
    return {
      match: "collaboration_participant_match",
      evidence: "multi_artist_participant_overlap",
      score: 26,
      coverage: Math.max(expectedCoverage, compactCoverage),
      expected_participant_count: expectedNames.length,
      candidate_primary_matches_expected_primary: false,
    };
  }
  if (hasCompatibleName(expectedNames, candidateNames) || hasIntersection(expectedCompact, candidateCompact)) {
    return {
      match: "compatible_normalized",
      evidence: "artist_alias_or_spacing_match",
      score: 23,
      coverage: Math.max(expectedCoverage, compactCoverage),
      expected_participant_count: expectedNames.length,
      candidate_primary_matches_expected_primary: false,
    };
  }
  return {
    match: "not_matched",
    evidence: "artist_not_matched",
    score: 0,
    coverage: 0,
    expected_participant_count: expectedNames.length,
    candidate_primary_matches_expected_primary: false,
  };
}

function scoreFor({ title, artist, yearDelta, index, versionFlags, contextFlags }) {
  let score = title.score + artist.score;
  if (yearDelta === 0) score += 12;
  else if (yearDelta !== "" && yearDelta <= 2) score += 8;
  else if (yearDelta !== "" && yearDelta <= 10) score += 4;
  score += Math.max(0, 8 - index);
  score -= versionFlags.length ? 25 : 0;
  score -= contextFlags.length ? 35 : 0;
  return score;
}

function acceptanceFor({ title, artist, yearDelta, versionFlags, contextFlags, score }) {
  if (versionFlags.length) {
    return {
      accept_status: "deferred",
      deferred_reason: "direct_song_hardening_v2_version_term_needs_review",
      reject_reason: `version_term:${versionFlags.join(";")}`,
    };
  }
  if (contextFlags.length) {
    return {
      accept_status: "deferred",
      deferred_reason: "direct_song_hardening_v2_context_term_needs_review",
      reject_reason: `context_term:${contextFlags.join(";")}`,
    };
  }

  const strongTitle = ["exact_normalized", "core_exact_normalized", "compact_exact_normalized"].includes(title.match);
  const exactOrPrimaryArtist = artist.match === "exact_normalized"
    || artist.evidence === "primary_artist_present_in_candidate_participants"
    || artist.evidence === "candidate_primary_present_in_expected_participants";
  const collaborationArtist = artist.match === "collaboration_participant_match" && artist.coverage >= 0.5;
  const compatibleArtist = artist.match === "compatible_normalized";
  const yearTight = yearDelta !== "" && yearDelta <= 2;
  const yearKnown = yearDelta !== "";
  const singleArtistAsFeaturedOnly = artist.evidence === "primary_artist_present_in_candidate_participants"
    && artist.expected_participant_count <= 1;

  if (strongTitle && exactOrPrimaryArtist && !singleArtistAsFeaturedOnly && score >= 74) {
    return {
      accept_status: "accepted",
      match_basis: `direct_song_hardening_v2_${basisTitle(title.match)}_${basisArtist(artist.evidence)}_auto_match`,
      confidence: title.match === "exact_normalized" && artist.match === "exact_normalized" ? "high" : "medium",
      warnings: yearWarning(yearKnown, yearDelta),
    };
  }

  if (strongTitle && singleArtistAsFeaturedOnly && yearTight && score >= 78) {
    return {
      accept_status: "accepted",
      match_basis: `direct_song_hardening_v2_${basisTitle(title.match)}_single_artist_featured_with_tight_year_auto_match`,
      confidence: "medium",
      warnings: "single_artist_appears_as_featured_credit",
    };
  }

  if (strongTitle && collaborationArtist && score >= 76) {
    return {
      accept_status: "accepted",
      match_basis: `direct_song_hardening_v2_${basisTitle(title.match)}_collaboration_participant_auto_match`,
      confidence: yearTight ? "high" : "medium",
      warnings: compactValues(["collaboration_participant_match", yearWarning(yearKnown, yearDelta)]).join(";"),
    };
  }

  if (strongTitle && compatibleArtist && yearTight && score >= 72) {
    return {
      accept_status: "accepted",
      match_basis: `direct_song_hardening_v2_${basisTitle(title.match)}_compatible_artist_year_auto_match`,
      confidence: "medium",
      warnings: "compatible_artist_match",
    };
  }

  if (!strongTitle) {
    return {
      accept_status: "deferred",
      deferred_reason: "direct_song_hardening_v2_no_auto_match",
      reject_reason: title.match === "not_matched" ? "title_not_matched" : "title_not_strong_enough",
    };
  }
  if (artist.match === "not_matched") {
    return {
      accept_status: "deferred",
      deferred_reason: "direct_song_hardening_v2_no_auto_match",
      reject_reason: "artist_not_matched",
    };
  }
  return {
    accept_status: "deferred",
    deferred_reason: "direct_song_hardening_v2_no_auto_match",
    reject_reason: singleArtistAsFeaturedOnly ? "single_artist_only_featured_without_tight_year" : "identity_evidence_below_threshold",
  };
}

function titleVariants(value) {
  const withoutFeature = removeFeaturedTitleText(value);
  const withoutVersion = removeVersionDescriptors(withoutFeature);
  const exact = unique([
    normalize(value),
    normalize(withoutFeature),
  ]).filter(Boolean);
  const core = unique([
    normalizeTitleCore(value),
    normalizeTitleCore(withoutFeature),
    normalizeTitleCore(withoutVersion),
  ]).filter(Boolean);
  const compactVariants = unique([...exact, ...core].map(compact)).filter(Boolean);
  return { exact, core, compact: compactVariants };
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
    .split(/\s*(?:,|&|\band\b|\bfeat\.?\b|\bft\.?\b|\bfeaturing\b|\+)\s*/giu)
    .map((part) => normalize(part))
    .filter(Boolean);
}

function extractFeaturedArtists(title) {
  const text = String(title ?? "");
  const matches = [];
  for (const match of text.matchAll(/(?:feat\.?|ft\.?|featuring)\s+([^\])]+)/giu)) {
    matches.push(...splitArtistNames(match[1]));
  }
  return matches;
}

function candidateVersionFlags(candidateTitle, expectedTitle) {
  const candidate = normalize(candidateTitle);
  const expected = normalize(expectedTitle);
  const flags = [];
  const disallowed = [
    "live",
    "club mix",
    "remix",
    "dub",
    "karaoke",
    "tribute",
    "cover",
    "demo",
    "instrumental",
    "sped up",
    "slowed",
    "nightcore",
  ];
  for (const term of disallowed) {
    if (candidate.includes(term) && !expected.includes(term)) flags.push(term.replace(/\s+/g, "_"));
  }
  return unique(flags);
}

function candidateContextFlags(attrs, expectedPrimary) {
  const expected = normalize(expectedPrimary);
  const title = normalize(attrs.name ?? "");
  const artist = normalize(attrs.artistName ?? "");
  const album = normalize(attrs.albumName ?? "");
  const combined = `${title} ${artist} ${album}`;
  const flags = [];
  const disallowed = [
    "tribute",
    "karaoke",
    "lullaby",
    "lullabies",
    "rendition",
    "renditions",
    "cover",
    "made famous",
    "style of",
    "originally performed",
  ];
  for (const term of disallowed) {
    if (combined.includes(term) && !expected.includes(term)) flags.push(term.replace(/\s+/g, "_"));
  }
  if (album.includes(" live") && !expected.includes(" live")) flags.push("album_live");
  if (expected && (artist.includes(`${expected} jr`) || artist.includes(`${expected} junior`))) {
    flags.push("artist_suffix_jr");
  }
  return unique(flags);
}

function removeFeaturedTitleText(value) {
  return String(value ?? "")
    .replace(/\s*[\[(][^\])]*(feat\.?|ft\.?|featuring)[^\])]*[\])]\s*/giu, " ")
    .replace(/\b(feat\.?|ft\.?|featuring)\b.*$/iu, "")
    .trim();
}

function removeVersionDescriptors(value) {
  return String(value ?? "")
    .replace(/\s*[\[(](?:\\d{4}\\s+)?(?:re)?master(?:ed)?[^)\]]*[\])]/giu, " ")
    .replace(/\s*[\[(](?:single|album|radio|mono|stereo|clean|explicit)\\s+(?:version|edit)?[^)\]]*[\])]/giu, " ")
    .replace(/\s*[\[(](?:version|edit|bonus track)[^)\]]*[\])]/giu, " ")
    .trim();
}

function normalizeTitleCore(value) {
  return normalize(removeVersionDescriptors(removeFeaturedTitleText(value)))
    .replace(/\b(remaster(ed)?|mono|stereo|single|album|version|edit|deluxe|expanded|anniversary|bonus|track|explicit|clean|radio)\b/g, " ")
    .replace(/\b(19|20)\d{2}\b/g, " ")
    .replace(/\s+/g, " ")
    .trim();
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

function basisTitle(match) {
  if (match === "exact_normalized") return "exact_title";
  if (match === "core_exact_normalized") return "core_title";
  if (match === "compact_exact_normalized") return "compact_title";
  return "compatible_title";
}

function basisArtist(evidence) {
  return evidence.replace(/[^a-z0-9]+/gu, "_").replace(/^_+|_+$/gu, "");
}

function yearWarning(yearKnown, yearDelta) {
  if (!yearKnown || yearDelta === 0) return "";
  if (yearDelta > 10) return "release_year_differs_likely_compilation";
  return "release_year_differs";
}

function graphSourceKey(sourceType, sourceRef) {
  return `${sourceType}:${sourceRef}`;
}

function isGraphSongLink(link) {
  return (link.source_type === "graph_song" || link.source_type === "graph_recording") && link.apple_resource_type === "song";
}

function isAcceptedLink(link) {
  return ["verified", "candidate_verified"].includes(link.match_status);
}

function yearDeltaFor(expectedYear, releaseDate) {
  const expected = Number(expectedYear);
  const candidate = Number(String(releaseDate ?? "").slice(0, 4));
  if (!Number.isFinite(expected) || !Number.isFinite(candidate)) return "";
  return Math.abs(expected - candidate);
}

function hasIntersection(left, right) {
  const rightSet = new Set(right);
  return left.some((value) => rightSet.has(value));
}

function overlapCount(left, right) {
  const rightSet = new Set(right);
  return left.filter((value) => rightSet.has(value)).length;
}

function hasCompatibleTitle(left, right) {
  return left.some((leftValue) => right.some((rightValue) => compatibleNames(leftValue, rightValue)));
}

function hasCompatibleName(left, right) {
  return left.some((leftValue) => right.some((rightValue) => artistNameCompatible(leftValue, rightValue)));
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

function tokenSet(value) {
  return normalize(value).split(/\s+/gu).filter(Boolean);
}

function compatibleNames(candidate, expected) {
  if (!candidate || !expected) return false;
  return candidate === expected || candidate.includes(expected) || expected.includes(candidate);
}

function compact(value) {
  return String(value ?? "").replace(/[^a-z0-9]+/gu, "");
}

function compactValues(values) {
  return values.filter((value) => value !== undefined && value !== null && value !== "");
}

function unique(values) {
  return [...new Set(values)];
}

function linkOutcome(candidate, candidateCount, runnerUp) {
  return {
    kind: "link",
    candidate,
    candidate_count: candidateCount,
    score_delta_to_runner_up: runnerUp ? candidate.score - runnerUp.score : "",
  };
}

function deferOutcome(reason, fields = {}) {
  return {
    kind: "deferred",
    deferred_reason: reason,
    candidate_count: fields.candidate_count ?? "",
    best_score: fields.best_score ?? "",
    best_result_rank: fields.best_result_rank ?? "",
    best_reject_reason: fields.best_reject_reason ?? "",
    error_message: fields.error_message ?? "",
  };
}

function dryRunOutcome() {
  return deferOutcome("dry_run_no_catalog_call", { candidate_count: 0 });
}

function recordOutcome(job, outcome) {
  if (outcome.kind === "link") links.push(makeLink(job, outcome));
  else deferred.push(makeDeferred(job, outcome));
}

function makeLink(job, outcome) {
  const candidate = outcome.candidate;
  return {
    link_key: `${job.source_type}:${job.source_ref}:apple_music:song:${candidate.item.id}:${storefront}`,
    run_version: runVersion,
    source_ref: job.source_ref,
    source_type: job.source_type,
    source_candidate_type: job.source_candidate_type,
    external_catalog: "apple_music",
    apple_catalog_id: candidate.item.id,
    apple_resource_type: "song",
    storefront,
    match_status: candidate.confidence === "high" ? "verified" : "candidate_verified",
    match_basis: candidate.match_basis,
    confidence: candidate.confidence,
    result_rank: candidate.index + 1,
    score: candidate.score,
    score_delta_to_runner_up: outcome.score_delta_to_runner_up,
    title_match: candidate.title_match,
    artist_match: candidate.artist_match,
    artist_evidence: candidate.artist_evidence,
    year_delta: candidate.year_delta,
    warnings: candidate.warnings,
    prior_review_reason: job.prior_review_reason,
    prior_best_reject_reason: job.best_reject_reason,
    candidate_count: outcome.candidate_count,
    verified_at: new Date().toISOString(),
    raw_payload_persisted: false,
  };
}

function makeDeferred(job, outcome) {
  return {
    deferred_key: `${job.source_type}:${job.source_ref}:${outcome.deferred_reason}`,
    run_version: runVersion,
    source_ref: job.source_ref,
    source_type: job.source_type,
    source_candidate_type: job.source_candidate_type,
    artist_display_name: job.artist_display_name,
    title: job.title,
    year: job.year,
    storefront,
    deferred_reason: outcome.deferred_reason,
    candidate_count: outcome.candidate_count,
    best_score: outcome.best_score,
    best_result_rank: outcome.best_result_rank,
    best_reject_reason: outcome.best_reject_reason,
    prior_review_reason: job.prior_review_reason,
    prior_best_reject_reason: job.best_reject_reason,
    error_message: outcome.error_message,
    raw_payload_persisted: false,
  };
}

function writeFinalArtifacts() {
  const sortedLinks = [...links].sort((left, right) => left.link_key.localeCompare(right.link_key));
  const sortedDeferred = [...deferred].sort((left, right) => left.deferred_key.localeCompare(right.deferred_key));
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
  return {
    run_version: runVersion,
    status: "complete",
    generated_at: new Date().toISOString(),
    storefront,
    policy: {
      raw_apple_payloads_persisted: false,
      apple_catalog_requests: args.dryRun ? "none_dry_run" : "song_search_transient_only",
      persisted_catalog_fields: ["apple_catalog_id", "apple_resource_type", "storefront", "source refs", "match metadata"],
      excluded_persistent_fields: ["artwork", "previews", "lyrics", "raw_catalog_payload", "music_user_token", "apple_track_title", "apple_track_artist", "apple_album_name"],
    },
    inputs: {
      source_queue: "data/canonical_graph/current/apple_music_direct_song_hardening_pass_v1/apple_music_direct_song_hardening_deferred_queue.csv",
      link_inputs: Object.fromEntries(linkInputSpecs.map(([key, relativePath]) => [key, `data/canonical_graph/current/${relativePath}`])),
    },
    counts: {
      jobs_considered: selectedJobs.length,
      new_links_total: sortedLinks.length,
      deferred_total: sortedDeferred.length,
      new_links_by_confidence: countBy(sortedLinks, "confidence"),
      new_links_by_match_basis: countBy(sortedLinks, "match_basis"),
      new_links_by_artist_evidence: countBy(sortedLinks, "artist_evidence"),
      new_links_by_prior_best_reject_reason: countBy(sortedLinks, "prior_best_reject_reason"),
      deferred_by_reason: countBy(sortedDeferred, "deferred_reason"),
      deferred_by_best_reject_reason: countBy(sortedDeferred, "best_reject_reason"),
    },
  };
}

function buildManifest(summary) {
  return `# Apple Music Direct Song Hardening Pass v2

Generated: ${summary.generated_at}

Status: \`${summary.status}\`

Storefront: \`${summary.storefront}\`

## Policy

- Raw Apple payloads persisted: \`false\`
- Apple catalog requests are transient song searches only.
- Durable output stores Apple catalog IDs, resource type, storefront, source refs, and compact match metadata only.
- Apple track names, album names, artist names from search responses, artwork, previews, lyrics, and Music User Tokens are not persisted.

## Acceptance Rule

This pass targets residual graph songs deferred by v1. It adds:

- multi-artist, featured-artist, and compact artist normalization
- title compacting for punctuation/stylization/censored-text differences
- collaboration participant matching when title identity is strong

It still defers obvious live/remix/dub/karaoke/cover/demo/instrumental version traps unless the graph title itself requests that version.

## Counts

- Jobs considered: ${summary.counts.jobs_considered}
- New links total: ${summary.counts.new_links_total}
- Deferred rows: ${summary.counts.deferred_total}

## New Links By Match Basis

${tableFromCounts(summary.counts.new_links_by_match_basis)}

## Deferred By Reason

${tableFromCounts(summary.counts.deferred_by_reason)}
`;
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
    .sort((left, right) => right[1] - left[1])
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
