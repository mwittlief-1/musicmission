#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

const repoRoot = process.cwd();
const currentRoot = path.join(repoRoot, "data/canonical_graph/current");
const outputRoot = path.join(currentRoot, "apple_music_offline_reconciliation_pass_v1");
const runVersion = "apple_music_offline_reconciliation_pass_v1";
const storefront = "us";

fs.mkdirSync(outputRoot, { recursive: true });

const linksPath = path.join(outputRoot, "apple_music_offline_reconciliation_links_v1.jsonl");
const deferredPath = path.join(outputRoot, "apple_music_offline_reconciliation_deferred_queue.csv");
const summaryPath = path.join(outputRoot, "apple_music_offline_reconciliation_summary.json");
const manifestPath = path.join(outputRoot, "apple_music_offline_reconciliation_manifest.md");

const sidecarTracks = readCsv(path.join(currentRoot, "album_track_sidecar_tracks.csv"));
const firstPassLinks = readJsonl(path.join(currentRoot, "apple_music_link_pass_v1/apple_music_links_v1.jsonl"));
const tryHarderLinks = readJsonl(path.join(currentRoot, "apple_music_try_harder_pass_v1/apple_music_try_harder_links_v1.jsonl"));
const firstPassReviews = readCsv(path.join(currentRoot, "apple_music_link_pass_v1/apple_music_manual_review_queue.csv"));
const existingLinks = [...firstPassLinks, ...tryHarderLinks];
existingLinks.push(...safeReadJsonl(path.join(currentRoot, "apple_music_residual_track_pass_v1/apple_music_residual_track_links_v1.jsonl")));
existingLinks.push(...safeReadJsonl(path.join(currentRoot, "apple_music_album_variant_pass_v1/apple_music_album_variant_links_v1.jsonl")));
const existingGraphSongLinkKeys = new Set(
  existingLinks
    .filter((link) => (link.source_type === "graph_song" || link.source_type === "graph_recording") && link.apple_resource_type === "song")
    .map((link) => graphSourceKey(link.source_type, link.source_ref)),
);

const sidecarTrackIdBySourceRef = new Map(
  existingLinks
    .filter((link) => link.source_type === "album_sidecar_track" && link.apple_resource_type === "song")
    .map((link) => [link.source_ref, link]),
);

const sidecarCandidates = buildSidecarCandidates();
const sidecarByTitleArtistYear = groupBy(sidecarCandidates, (candidate) => [
  candidate.track_title_norm,
  candidate.effective_artist_norm,
  candidate.album_year,
].join("|"));
const sidecarByTitleYear = groupBy(sidecarCandidates, (candidate) => [
  candidate.track_title_norm,
  candidate.album_year,
].join("|"));

const reviewRows = firstPassReviews
  .filter((row) => row.source_type === "graph_song" || row.source_type === "graph_recording")
  .filter((row) => !existingGraphSongLinkKeys.has(graphSourceKey(row.source_type, row.source_ref)));

const links = [];
const deferred = [];

for (const review of reviewRows) {
  const outcome = resolveReviewFromSidecar(review);
  if (outcome.kind === "link") links.push(makeLink(review, outcome));
  else deferred.push(makeDeferred(review, outcome));
}

writeFinalArtifacts();

function buildSidecarCandidates() {
  const candidates = [];
  for (const row of sidecarTracks) {
    const sourceRef = sidecarTrackSourceRef(row);
    const link = sidecarTrackIdBySourceRef.get(sourceRef);
    if (!link) continue;
    candidates.push({
      row,
      sidecar_track_source_ref: sourceRef,
      apple_catalog_id: link.apple_catalog_id,
      album_source_ref: row.candidate_identity_key,
      album_artist_norm: normalize(row.artist_display_name),
      track_artist_norm: normalize(row.track_artist_name),
      effective_artist_norm: normalize(row.track_artist_name || row.artist_display_name),
      track_title_norm: normalize(row.track_title),
      track_title_core: normalizeTitleCore(row.track_title),
      album_year: String(row.album_year ?? ""),
      match_source_basis: link.match_basis,
    });
  }
  return candidates;
}

function resolveReviewFromSidecar(review) {
  const titleNorm = normalize(review.title);
  const artistNorm = normalize(stripFeaturing(review.artist_display_name));
  const year = String(review.year ?? "");

  const exactArtistYear = uniqueByAppleId(
    sidecarByTitleArtistYear.get([titleNorm, artistNorm, year].join("|")) ?? [],
  );
  if (exactArtistYear.length === 1) {
    return linkOutcome(exactArtistYear[0], {
      match_basis: "offline_sidecar_exact_title_effective_artist_year",
      confidence: "high",
      title_match: "exact_normalized",
      artist_match: "exact_normalized",
      year_delta: "0",
      warnings: "",
    });
  }

  const compatibleArtistYear = uniqueByAppleId(
    (sidecarByTitleYear.get([titleNorm, year].join("|")) ?? [])
      .filter((candidate) => (
        compatibleNames(candidate.effective_artist_norm, artistNorm)
        || compatibleNames(candidate.track_artist_norm, artistNorm)
        || compatibleNames(candidate.album_artist_norm, artistNorm)
      )),
  );
  if (compatibleArtistYear.length === 1) {
    return linkOutcome(compatibleArtistYear[0], {
      match_basis: "offline_sidecar_exact_title_compatible_artist_year",
      confidence: "medium",
      title_match: "exact_normalized",
      artist_match: "compatible_normalized",
      year_delta: "0",
      warnings: review.review_reason === "apple_song_search_needs_review_version_risk"
        ? "version_risk_resolved_by_album_sidecar_context"
        : "",
    });
  }

  const ambiguousCount = Math.max(exactArtistYear.length, compatibleArtistYear.length);
  return {
    kind: "deferred",
    reason: ambiguousCount > 1
      ? "offline_sidecar_ambiguous_track_match"
      : "offline_sidecar_no_unique_track_match",
    candidate_count: ambiguousCount,
  };
}

function linkOutcome(candidate, fields) {
  return {
    kind: "link",
    candidate,
    ...fields,
  };
}

function makeLink(review, outcome) {
  return {
    link_key: `${review.source_type}:${review.source_ref}:apple_music:song:${outcome.candidate.apple_catalog_id}:${storefront}`,
    run_version: runVersion,
    source_ref: review.source_ref,
    source_type: review.source_type,
    source_candidate_type: review.source_candidate_type,
    external_catalog: "apple_music",
    apple_catalog_id: outcome.candidate.apple_catalog_id,
    apple_resource_type: "song",
    storefront,
    match_status: outcome.confidence === "high" ? "verified" : "candidate_verified",
    match_basis: outcome.match_basis,
    confidence: outcome.confidence,
    title_match: outcome.title_match,
    artist_match: outcome.artist_match,
    year_delta: outcome.year_delta,
    warnings: outcome.warnings,
    sidecar_track_source_ref: outcome.candidate.sidecar_track_source_ref,
    album_source_ref: outcome.candidate.album_source_ref,
    sidecar_track_match_basis: outcome.candidate.match_source_basis,
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
    prior_review_reason: review.review_reason,
    raw_payload_persisted: false,
  };
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
    storefront,
    policy: {
      raw_apple_payloads_persisted: false,
      persisted_catalog_fields: ["apple_catalog_id", "apple_resource_type", "storefront", "match metadata"],
      excluded_persistent_fields: ["artwork", "previews", "lyrics", "raw_catalog_payload", "music_user_token"],
    },
    inputs: {
      first_pass_links: "data/canonical_graph/current/apple_music_link_pass_v1/apple_music_links_v1.jsonl",
      try_harder_links: "data/canonical_graph/current/apple_music_try_harder_pass_v1/apple_music_try_harder_links_v1.jsonl",
      residual_track_links: "data/canonical_graph/current/apple_music_residual_track_pass_v1/apple_music_residual_track_links_v1.jsonl",
      album_variant_links: "data/canonical_graph/current/apple_music_album_variant_pass_v1/apple_music_album_variant_links_v1.jsonl",
      first_pass_review_queue: "data/canonical_graph/current/apple_music_link_pass_v1/apple_music_manual_review_queue.csv",
      album_track_sidecar_tracks: "data/canonical_graph/current/album_track_sidecar_tracks.csv",
    },
    counts: {
      sidecar_track_candidates_with_apple_ids: sidecarCandidates.length,
      graph_song_recording_review_rows_considered: reviewRows.length,
      new_links_total: sortedLinks.length,
      deferred_total: sortedDeferred.length,
      new_links_by_source_type: countBy(sortedLinks, "source_type"),
      new_links_by_match_basis: countBy(sortedLinks, "match_basis"),
      deferred_by_reason: countBy(sortedDeferred, "deferred_reason"),
      links_by_prior_review_reason: countBy(sortedLinks, "prior_review_reason"),
    },
  };
}

function buildManifest(summary) {
  return `# Apple Music Offline Reconciliation Pass v1

Generated: ${summary.generated_at}

Status: \`${summary.status}\`

Storefront: \`${summary.storefront}\`

## Policy

- Raw Apple payloads persisted: \`false\`
- No Apple API calls are made by this pass.
- Durable output stores Apple catalog IDs, resource type, storefront, source refs, match status, and matching metadata only.

## Intent

This pass reconciles first-pass graph song/recording review rows against album-sidecar tracks that already received Apple song IDs in prior passes.

## Counts

- Sidecar track candidates with Apple IDs: ${summary.counts.sidecar_track_candidates_with_apple_ids}
- Graph song/recording review rows considered: ${summary.counts.graph_song_recording_review_rows_considered}
- New links total: ${summary.counts.new_links_total}
- Deferred rows: ${summary.counts.deferred_total}

## New Links By Match Basis

${tableFromCounts(summary.counts.new_links_by_match_basis)}

## Links By Prior Review Reason

${tableFromCounts(summary.counts.links_by_prior_review_reason)}

## Deferred By Reason

${tableFromCounts(summary.counts.deferred_by_reason)}
`;
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

function graphSourceKey(sourceType, sourceRef) {
  return `${sourceType}:${sourceRef}`;
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

function uniqueByAppleId(candidates) {
  const byAppleId = new Map();
  for (const candidate of candidates) {
    byAppleId.set(candidate.apple_catalog_id, candidate);
  }
  return [...byAppleId.values()];
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
