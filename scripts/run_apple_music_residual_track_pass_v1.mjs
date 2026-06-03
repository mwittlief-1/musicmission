#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { createAppleMusicCatalogClient } from "./lib/appleMusicCatalogClient.mjs";

const repoRoot = process.cwd();
const currentRoot = path.join(repoRoot, "data/canonical_graph/current");
const outputRoot = path.join(currentRoot, "apple_music_residual_track_pass_v1");
const runVersion = "apple_music_residual_track_pass_v1";
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

const linksPath = path.join(outputRoot, "apple_music_residual_track_links_v1.jsonl");
const deferredPath = path.join(outputRoot, "apple_music_residual_track_deferred_queue.csv");
const summaryPath = path.join(outputRoot, "apple_music_residual_track_summary.json");
const manifestPath = path.join(outputRoot, "apple_music_residual_track_manifest.md");
const checkpointPath = path.join(outputRoot, "apple_music_residual_track_pass_v1.checkpoint.json");

const sidecarTracks = readCsv(path.join(currentRoot, "album_track_sidecar_tracks.csv"));
const tryHarderDeferred = readCsv(path.join(currentRoot, "apple_music_try_harder_pass_v1/apple_music_try_harder_deferred_queue.csv"));
const allLinks = [
  ...readJsonl(path.join(currentRoot, "apple_music_link_pass_v1/apple_music_links_v1.jsonl")),
  ...readJsonl(path.join(currentRoot, "apple_music_try_harder_pass_v1/apple_music_try_harder_links_v1.jsonl")),
  ...safeReadJsonl(path.join(currentRoot, "apple_music_offline_reconciliation_pass_v1/apple_music_offline_reconciliation_links_v1.jsonl")),
];

const sidecarTrackRowsBySourceRef = new Map(sidecarTracks.map((row) => [sidecarTrackSourceRef(row), row]));
const sidecarAlbumIdByRef = new Map(
  allLinks
    .filter((link) => link.source_type === "album_sidecar_album" && link.apple_resource_type === "album")
    .map((link) => [link.source_ref, link.apple_catalog_id]),
);
const existingTrackIdsBySourceRef = new Map(
  allLinks
    .filter((link) => link.source_type === "album_sidecar_track" && link.apple_resource_type === "song")
    .map((link) => [link.source_ref, link.apple_catalog_id]),
);

const checkpoint = args.resume ? readCheckpoint() : null;
const completedAlbumKeys = new Set(checkpoint?.completed_album_keys ?? []);
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

await runPool(albumJobs.filter((job) => !completedAlbumKeys.has(job.album_source_ref)), args.concurrency, async (job, index) => {
  const outcome = await safelyResolveAlbum(job);
  recordOutcome(job, outcome);
  completedAlbumKeys.add(job.album_source_ref);
  if ((index + 1) % args.checkpointEvery === 0) writeCheckpoint("partial");
  if ((index + 1) % args.progressEvery === 0) {
    console.error(`residual-track: ${index + 1}/${albumJobs.length}, links=${links.length}, deferred=${deferred.length}`);
  }
});

writeCheckpoint("complete");
writeFinalArtifacts();
if (!args.keepCheckpoint && fs.existsSync(checkpointPath)) fs.unlinkSync(checkpointPath);

function parseArgs(argv) {
  const parsed = {
    concurrency: 3,
    progressEvery: 50,
    checkpointEvery: 50,
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
  if (parsed.concurrency > 6) parsed.concurrency = 6;
  return parsed;
}

function buildAlbumJobs() {
  const deferredRows = tryHarderDeferred
    .filter((row) => row.deferred_reason === "album_track_try_harder_no_safe_match")
    .map((row) => ({ deferred: row, track: sidecarTrackRowsBySourceRef.get(row.source_ref) }))
    .filter((pair) => pair.track)
    .filter((pair) => !existingTrackIdsBySourceRef.has(pair.deferred.source_ref));
  const byAlbum = groupBy(deferredRows, (pair) => pair.track.candidate_identity_key);
  const jobs = [];
  for (const [albumSourceRef, pairs] of byAlbum.entries()) {
    const appleAlbumId = sidecarAlbumIdByRef.get(albumSourceRef);
    if (!appleAlbumId) continue;
    jobs.push({
      album_source_ref: albumSourceRef,
      apple_album_id: appleAlbumId,
      deferred_pairs: pairs,
      all_album_tracks: sidecarTracks.filter((row) => row.candidate_identity_key === albumSourceRef),
    });
  }
  const sorted = jobs.sort((a, b) => a.album_source_ref.localeCompare(b.album_source_ref));
  return Number.isFinite(args.limitAlbums) ? sorted.slice(0, args.limitAlbums) : sorted;
}

async function safelyResolveAlbum(job) {
  try {
    if (args.dryRun) return { links: [], deferred: [] };
    const appleTracks = await fetchAlbumTracks(job.apple_album_id);
    return resolveAlbum(job, appleTracks);
  } catch (error) {
    return {
      links: [],
      deferred: job.deferred_pairs.map((pair) => makeDeferred(pair, "apple_album_tracks_request_error", {
        error_message: error instanceof Error ? error.message : String(error),
      })),
    };
  }
}

async function fetchAlbumTracks(albumId) {
  const payload = await client.catalogGet(`/v1/catalog/${encodeURIComponent(storefront)}/albums/${encodeURIComponent(albumId)}/tracks`, {
    limit: 300,
    "fields[songs]": "name,artistName,durationInMillis,discNumber,trackNumber",
  });
  return (payload?.data ?? [])
    .filter((item) => item.type === "songs" && item.id)
    .map((item, index) => normalizeAppleTrack(item, index))
    .filter(Boolean);
}

function resolveAlbum(job, appleTracks) {
  const usedAppleIds = new Set(
    job.all_album_tracks
      .map((row) => existingTrackIdsBySourceRef.get(sidecarTrackSourceRef(row)))
      .filter(Boolean),
  );
  const acceptedLinks = [];
  const deferredRows = [];

  for (const pair of job.deferred_pairs) {
    const scored = appleTracks
      .filter((track) => !usedAppleIds.has(track.apple_catalog_id))
      .map((track) => scoreTrack(pair.track, track))
      .sort((a, b) => b.score - a.score);
    const best = scored[0];
    const second = scored[1];
    if (best && isAcceptable(best, second)) {
      usedAppleIds.add(best.track.apple_catalog_id);
      acceptedLinks.push(makeLink(pair, best, job));
    } else {
      deferredRows.push(makeDeferred(pair, "residual_track_no_safe_match", {
        candidate_count: scored.length,
        best_score: best?.score ?? 0,
      }));
    }
  }

  return { links: acceptedLinks, deferred: deferredRows };
}

function normalizeAppleTrack(item, albumTrackIndex) {
  const attrs = item.attributes ?? {};
  if (!attrs.name) return null;
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

function scoreTrack(row, track) {
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
  else if (durationDelta !== null && durationDelta <= 30000) score += 5;
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
  };
}

function isAcceptable(best, second) {
  if (best.positionExact && best.artistCompatible && best.duration_delta_ms !== "" && best.duration_delta_ms <= 5000 && best.titleCompatible) return true;
  if (best.positionExact && best.artistCompatible && (best.titleExact || best.titleCoreExact)) return true;
  if ((best.titleExact || best.titleCoreExact) && best.artistCompatible && best.duration_delta_ms !== "" && best.duration_delta_ms <= 5000 && (!second || best.score - second.score >= 12)) return true;
  return false;
}

function makeLink(pair, best, job) {
  const sourceRef = pair.deferred.source_ref;
  return {
    link_key: `album_sidecar_track:${sourceRef}:apple_music:song:${best.track.apple_catalog_id}:${storefront}`,
    run_version: runVersion,
    source_ref: sourceRef,
    source_type: "album_sidecar_track",
    source_candidate_type: "track",
    external_catalog: "apple_music",
    apple_catalog_id: best.track.apple_catalog_id,
    apple_resource_type: "song",
    storefront,
    match_status: best.score >= 92 ? "verified" : "candidate_verified",
    match_basis: "residual_track_album_artist_fallback_auto_match",
    confidence: best.score >= 92 ? "high" : "medium",
    title_match: best.title_match,
    artist_match: best.artist_match,
    warnings: "",
    apple_album_id: job.apple_album_id,
    track_score: best.score,
    duration_delta_ms: best.duration_delta_ms,
    verified_at: new Date().toISOString(),
    raw_payload_persisted: false,
  };
}

function makeDeferred(pair, reason, extra = {}) {
  return {
    deferred_key: `album_sidecar_track:${pair.deferred.source_ref}:${reason}`,
    run_version: runVersion,
    source_ref: pair.deferred.source_ref,
    source_type: "album_sidecar_track",
    source_candidate_type: "track",
    artist_display_name: pair.track?.artist_display_name ?? "",
    title: pair.track?.track_title ?? "",
    year: pair.track?.album_year ?? "",
    storefront,
    deferred_reason: reason,
    candidate_count: extra.candidate_count ?? "",
    best_score: extra.best_score ?? "",
    error_message: extra.error_message ?? "",
    raw_payload_persisted: false,
  };
}

function recordOutcome(_job, outcome) {
  for (const link of outcome.links) {
    if (!linkKeys.has(link.link_key)) {
      links.push(link);
      linkKeys.add(link.link_key);
    }
  }
  for (const row of outcome.deferred) {
    if (!deferredKeys.has(row.deferred_key)) {
      deferred.push(row);
      deferredKeys.add(row.deferred_key);
    }
  }
}

function writeCheckpoint(status) {
  const value = {
    run_version: runVersion,
    status,
    storefront,
    generated_at: new Date().toISOString(),
    completed_album_keys: [...completedAlbumKeys].sort(),
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
      album_jobs_completed: completedAlbumKeys.size,
      new_links_total: sortedLinks.length,
      deferred_total: sortedDeferred.length,
      new_links_by_match_basis: countBy(sortedLinks, "match_basis"),
      deferred_by_reason: countBy(sortedDeferred, "deferred_reason"),
    },
  };
}

function buildManifest(summary) {
  return `# Apple Music Residual Track Pass v1

Generated: ${summary.generated_at}

Status: \`${summary.status}\`

Storefront: \`${summary.storefront}\`

## Policy

- Raw Apple payloads persisted: \`false\`
- Apple requests use sparse song fields for transient matching.
- Durable output stores Apple catalog IDs, resource type, storefront, source refs, match status, and matching metadata only.

## Counts

- Album jobs completed: ${summary.counts.album_jobs_completed}
- New links total: ${summary.counts.new_links_total}
- Deferred rows: ${summary.counts.deferred_total}

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
