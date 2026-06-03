#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { createAppleMusicCatalogClient } from "./lib/appleMusicCatalogClient.mjs";

const repoRoot = process.cwd();
const currentRoot = path.join(repoRoot, "data/canonical_graph/current");
const outputRoot = path.join(currentRoot, "apple_music_direct_song_hardening_pass_v1");
const runVersion = "apple_music_direct_song_hardening_pass_v1";

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

const linksPath = path.join(outputRoot, "apple_music_direct_song_hardening_links_v1.jsonl");
const deferredPath = path.join(outputRoot, "apple_music_direct_song_hardening_deferred_queue.csv");
const summaryPath = path.join(outputRoot, "apple_music_direct_song_hardening_summary.json");
const manifestPath = path.join(outputRoot, "apple_music_direct_song_hardening_manifest.md");

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
];

const deferredRows = readCsv(path.join(
  currentRoot,
  "apple_music_song_source_album_reconciliation_pass_v1/apple_music_song_source_album_reconciliation_deferred_queue.csv",
));
const existingLinks = linkInputSpecs.flatMap(([, relativePath]) => safeReadJsonl(path.join(currentRoot, relativePath)));
const existingGraphSongLinkKeys = new Set(
  existingLinks
    .filter((link) => isGraphSongLink(link) && isAcceptedLink(link))
    .map((link) => graphSourceKey(link.source_type, link.source_ref)),
);

const jobs = deferredRows
  .filter((row) => selectedSourceTypes().has(row.source_type))
  .filter((row) => !existingGraphSongLinkKeys.has(graphSourceKey(row.source_type, row.source_ref)))
  .sort((a, b) => `${a.source_type}:${a.source_ref}`.localeCompare(`${b.source_type}:${b.source_ref}`));
const selectedJobs = Number.isFinite(args.limit) ? jobs.slice(0, args.limit) : jobs;
const links = [];
const deferred = [];
let processed = 0;

console.error(JSON.stringify({
  run_version: runVersion,
  storefront,
  source_scope: args.sourceScope,
  selected_jobs: selectedJobs.length,
  concurrency: args.concurrency,
  dry_run: args.dryRun,
}, null, 2));

await runPool(selectedJobs, args.concurrency, async (job) => {
  const outcome = args.dryRun ? dryRunOutcome() : await resolveJob(job);
  recordOutcome(job, outcome);
  processed += 1;
  if (processed % args.progressEvery === 0 || processed === selectedJobs.length) {
    console.error(`direct song hardening: ${processed}/${selectedJobs.length}, links=${links.length}, deferred=${deferred.length}`);
  }
});

writeFinalArtifacts();

function parseArgs(argv) {
  const parsed = {
    storefront: "us",
    sourceScope: "songs",
    concurrency: 8,
    maxRetries: 8,
    limit: Number.NaN,
    progressEvery: 100,
    dryRun: false,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--storefront") parsed.storefront = argv[++index];
    else if (arg === "--source-scope") parsed.sourceScope = argv[++index];
    else if (arg === "--concurrency") parsed.concurrency = Number(argv[++index]);
    else if (arg === "--max-retries") parsed.maxRetries = Number(argv[++index]);
    else if (arg === "--limit") parsed.limit = Number(argv[++index]);
    else if (arg === "--progress-every") parsed.progressEvery = Number(argv[++index]);
    else if (arg === "--dry-run") parsed.dryRun = true;
  }

  if (!["songs", "recordings", "all"].includes(parsed.sourceScope)) {
    throw new Error(`Unsupported --source-scope ${parsed.sourceScope}. Expected songs, recordings, or all.`);
  }
  if (!parsed.storefront) parsed.storefront = "us";
  if (!Number.isFinite(parsed.concurrency) || parsed.concurrency < 1) parsed.concurrency = 1;
  if (parsed.concurrency > 12) parsed.concurrency = 12;
  if (!Number.isFinite(parsed.maxRetries) || parsed.maxRetries < 0) parsed.maxRetries = 3;
  if (!Number.isFinite(parsed.progressEvery) || parsed.progressEvery < 1) parsed.progressEvery = 100;
  return parsed;
}

function selectedSourceTypes() {
  if (args.sourceScope === "songs") return new Set(["graph_song"]);
  if (args.sourceScope === "recordings") return new Set(["graph_recording"]);
  return new Set(["graph_song", "graph_recording"]);
}

async function resolveJob(job) {
  const query = `${job.artist_display_name} ${job.title}`.trim();
  try {
    const payload = await client.catalogSearch({ term: query, types: "songs", limit: 10 });
    const items = payload?.results?.songs?.data ?? [];
    if (!items.length) return deferOutcome("direct_song_search_no_results", { candidate_count: 0 });

    const scored = items
      .map((item, index) => scoreSongCandidate(job, item, index))
      .sort((left, right) => bSort(right, left));
    const accepted = scored.find((candidate) => candidate.accept_status === "accepted");
    if (accepted) return linkOutcome(accepted, items.length);

    const best = scored[0];
    return deferOutcome(best?.deferred_reason ?? "direct_song_search_no_auto_match", {
      candidate_count: items.length,
      best_score: best?.score ?? "",
      best_result_rank: best ? best.index + 1 : "",
      best_reject_reason: best?.reject_reason ?? "",
    });
  } catch (error) {
    return deferOutcome("direct_song_search_request_error", {
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
  const expected = comparisonFields(job.title, job.artist_display_name, job.year);
  const candidate = comparisonFields(attrs.name ?? "", attrs.artistName ?? "", String(attrs.releaseDate ?? "").slice(0, 4));
  const versionFlags = candidateVersionFlags(attrs.name ?? "", job.title);
  const titleMatch = titleMatchKind(expected, candidate);
  const artistMatch = artistMatchKind(expected.artist_norm, candidate.artist_norm);
  const yearDelta = yearDeltaFor(job.year, attrs.releaseDate);
  const score = scoreFor({ titleMatch, artistMatch, yearDelta, index, versionFlags });
  const acceptance = acceptanceFor({ titleMatch, artistMatch, yearDelta, versionFlags, score });

  return {
    item,
    index,
    score,
    title_match: titleMatch,
    artist_match: artistMatch,
    year_delta: yearDelta,
    version_flags: versionFlags,
    accept_status: acceptance.accept_status,
    match_basis: acceptance.match_basis,
    confidence: acceptance.confidence,
    warnings: acceptance.warnings,
    deferred_reason: acceptance.deferred_reason,
    reject_reason: acceptance.reject_reason,
  };
}

function comparisonFields(title, artist, year) {
  return {
    title_norm: normalize(title),
    title_core: normalizeTitleCore(title),
    title_without_feature: normalize(removeFeaturedTitleText(title)),
    title_core_without_feature: normalizeTitleCore(removeFeaturedTitleText(title)),
    artist_norm: normalize(stripFeaturing(artist)),
    year: Number(year),
  };
}

function titleMatchKind(expected, candidate) {
  const expectedExact = unique([expected.title_norm, expected.title_without_feature]).filter(Boolean);
  const candidateExact = unique([candidate.title_norm, candidate.title_without_feature]).filter(Boolean);
  if (expectedExact.some((value) => candidateExact.includes(value))) return "exact_normalized";

  const expectedCore = unique([expected.title_core, expected.title_core_without_feature]).filter(Boolean);
  const candidateCore = unique([candidate.title_core, candidate.title_core_without_feature]).filter(Boolean);
  if (expectedCore.some((value) => candidateCore.includes(value))) return "core_exact_normalized";

  if (expectedCore.some((left) => candidateCore.some((right) => compatibleNames(left, right)))) {
    return "compatible_normalized";
  }
  return "not_matched";
}

function artistMatchKind(expectedArtist, candidateArtist) {
  if (!expectedArtist || !candidateArtist) return "not_matched";
  if (expectedArtist === candidateArtist) return "exact_normalized";
  if (compatibleNames(expectedArtist, candidateArtist)) return "compatible_normalized";
  return "not_matched";
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

function scoreFor({ titleMatch, artistMatch, yearDelta, index, versionFlags }) {
  let score = 0;
  if (titleMatch === "exact_normalized") score += 58;
  else if (titleMatch === "core_exact_normalized") score += 48;
  else if (titleMatch === "compatible_normalized") score += 24;

  if (artistMatch === "exact_normalized") score += 32;
  else if (artistMatch === "compatible_normalized") score += 22;

  if (yearDelta === 0) score += 12;
  else if (yearDelta !== "" && yearDelta <= 2) score += 8;
  else if (yearDelta !== "" && yearDelta <= 10) score += 4;

  score += Math.max(0, 8 - index);
  score -= versionFlags.length ? 20 : 0;
  return score;
}

function acceptanceFor({ titleMatch, artistMatch, yearDelta, versionFlags, score }) {
  if (versionFlags.length) {
    return {
      accept_status: "deferred",
      deferred_reason: "direct_song_search_version_term_needs_review",
      reject_reason: `version_term:${versionFlags.join(";")}`,
    };
  }

  const exactTitle = titleMatch === "exact_normalized";
  const coreTitle = titleMatch === "core_exact_normalized";
  const exactArtist = artistMatch === "exact_normalized";
  const compatibleArtist = artistMatch === "compatible_normalized";
  const yearTight = yearDelta !== "" && yearDelta <= 2;
  const yearKnown = yearDelta !== "";

  if (exactTitle && exactArtist) {
    return {
      accept_status: "accepted",
      match_basis: "direct_song_hardening_exact_title_artist_auto_match",
      confidence: "high",
      warnings: yearKnown && yearDelta > 10 ? "release_year_differs_likely_compilation" : yearKnown && yearDelta > 0 ? "release_year_differs" : "",
    };
  }
  if (coreTitle && exactArtist) {
    return {
      accept_status: "accepted",
      match_basis: yearTight
        ? "direct_song_hardening_core_title_artist_year_auto_match"
        : "direct_song_hardening_core_title_artist_auto_match",
      confidence: yearTight ? "high" : "medium",
      warnings: compact(["title_core_match", yearKnown && yearDelta > 10 ? "release_year_differs_likely_compilation" : yearKnown && yearDelta > 0 ? "release_year_differs" : ""]).join(";"),
    };
  }
  if (exactTitle && compatibleArtist && yearTight) {
    return {
      accept_status: "accepted",
      match_basis: "direct_song_hardening_exact_title_compatible_artist_year_auto_match",
      confidence: "medium",
      warnings: "compatible_artist_match",
    };
  }
  if (coreTitle && compatibleArtist && yearTight && score >= 76) {
    return {
      accept_status: "accepted",
      match_basis: "direct_song_hardening_core_title_compatible_artist_year_auto_match",
      confidence: "medium",
      warnings: "title_core_match;compatible_artist_match",
    };
  }

  return {
    accept_status: "deferred",
    deferred_reason: "direct_song_search_no_auto_match",
    reject_reason: compact([titleMatch === "not_matched" ? "title_not_matched" : "", artistMatch === "not_matched" ? "artist_not_matched" : "", !yearTight && compatibleArtist ? "compatible_artist_without_tight_year" : ""]).join(";"),
  };
}

function linkOutcome(candidate, candidateCount) {
  return {
    kind: "link",
    candidate,
    candidate_count: candidateCount,
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
  if (outcome.kind === "link") {
    links.push(makeLink(job, outcome));
    return;
  }
  deferred.push(makeDeferred(job, outcome));
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
    title_match: candidate.title_match,
    artist_match: candidate.artist_match,
    year_delta: candidate.year_delta,
    warnings: candidate.warnings,
    prior_review_reason: job.prior_review_reason,
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
    error_message: outcome.error_message,
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
    "best_score",
    "best_result_rank",
    "best_reject_reason",
    "prior_review_reason",
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
    source_scope: args.sourceScope,
    policy: {
      raw_apple_payloads_persisted: false,
      apple_catalog_requests: args.dryRun ? "none_dry_run" : "song_search_transient_only",
      persisted_catalog_fields: ["apple_catalog_id", "apple_resource_type", "storefront", "source refs", "match metadata"],
      excluded_persistent_fields: ["artwork", "previews", "lyrics", "raw_catalog_payload", "music_user_token", "apple_track_title", "apple_track_artist", "apple_album_name"],
    },
    inputs: {
      deferred_queue: "data/canonical_graph/current/apple_music_song_source_album_reconciliation_pass_v1/apple_music_song_source_album_reconciliation_deferred_queue.csv",
      link_inputs: Object.fromEntries(linkInputSpecs.map(([key, relativePath]) => [key, `data/canonical_graph/current/${relativePath}`])),
    },
    counts: {
      jobs_considered: selectedJobs.length,
      new_links_total: sortedLinks.length,
      deferred_total: sortedDeferred.length,
      new_links_by_source_type: countBy(sortedLinks, "source_type"),
      new_links_by_confidence: countBy(sortedLinks, "confidence"),
      new_links_by_match_basis: countBy(sortedLinks, "match_basis"),
      new_links_by_prior_review_reason: countBy(sortedLinks, "prior_review_reason"),
      deferred_by_reason: countBy(sortedDeferred, "deferred_reason"),
      deferred_by_best_reject_reason: countBy(sortedDeferred, "best_reject_reason"),
    },
  };
}

function buildManifest(summary) {
  return `# Apple Music Direct Song Hardening Pass v1

Generated: ${summary.generated_at}

Status: \`${summary.status}\`

Storefront: \`${summary.storefront}\`

Source scope: \`${summary.source_scope}\`

## Policy

- Raw Apple payloads persisted: \`false\`
- Apple catalog requests are transient song searches only.
- Durable output stores Apple catalog IDs, resource type, storefront, source refs, and compact matching metadata only.
- Apple track names, album names, artist names from search responses, artwork, previews, lyrics, and Music User Tokens are not persisted.

## Acceptance Rule

This pass encodes the review calibration that medium/high direct song candidates are acceptable when the identity evidence is title/artist strong:

- exact normalized title + exact normalized artist
- edition-stripped core title + exact normalized artist
- exact/core title + compatible artist only with tight release-year support

Obvious mix/live/cover/demo/karaoke/instrumental/remix version terms stay deferred.

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

function isGraphSongLink(link) {
  return (link.source_type === "graph_song" || link.source_type === "graph_recording") && link.apple_resource_type === "song";
}

function isAcceptedLink(link) {
  return ["verified", "candidate_verified"].includes(link.match_status);
}

function graphSourceKey(sourceType, sourceRef) {
  return `${sourceType}:${sourceRef}`;
}

function bSort(right, left) {
  const scoreDelta = right.score - left.score;
  if (scoreDelta) return scoreDelta;
  return left.index - right.index;
}

function yearDeltaFor(expectedYear, releaseDate) {
  const expected = Number(expectedYear);
  const candidate = Number(String(releaseDate ?? "").slice(0, 4));
  if (!Number.isFinite(expected) || !Number.isFinite(candidate)) return "";
  return Math.abs(expected - candidate);
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

function normalizeTitleCore(value) {
  return normalize(removeFeaturedTitleText(value))
    .replace(/\b(remaster(ed)?|mono|stereo|single|album|version|edit|deluxe|expanded|anniversary|bonus|track|explicit|clean|radio)\b/g, " ")
    .replace(/\b(19|20)\d{2}\b/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function stripFeaturing(value) {
  return String(value ?? "").replace(/\b(feat\.?|ft\.?|featuring)\b.*$/iu, "").trim();
}

function removeFeaturedTitleText(value) {
  return String(value ?? "")
    .replace(/\s*[\[(][^\])]*(feat\.?|ft\.?|featuring)[^\])]*[\])]\s*/giu, " ")
    .replace(/\b(feat\.?|ft\.?|featuring)\b.*$/iu, "")
    .trim();
}

function compatibleNames(candidate, expected) {
  if (!candidate || !expected) return false;
  return candidate === expected || candidate.includes(expected) || expected.includes(candidate);
}

function compact(values) {
  return values.filter((value) => value !== undefined && value !== null && value !== "");
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
