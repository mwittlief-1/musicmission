#!/usr/bin/env node

import crypto from "node:crypto";
import fs from "node:fs";
import https from "node:https";
import path from "node:path";

const repoRoot = process.cwd();
const currentRoot = path.join(repoRoot, "data/canonical_graph/current");
const outputRoot = path.join(currentRoot, "apple_music_link_pass_v1");
const envPathDefault = path.join(process.env.HOME ?? "", ".config/cartenza/apple-music/catalog-resolver.env");
const runVersion = "apple_music_link_pass_v1";

const args = parseArgs(process.argv.slice(2));
const env = loadResolverEnv(args.envPath);
const storefront = args.storefront ?? env.APPLE_MUSIC_STOREFRONT ?? "us";
const developerToken = makeDeveloperToken(env);

fs.mkdirSync(outputRoot, { recursive: true });

const checkpointPath = path.join(outputRoot, "apple_music_link_pass_v1.checkpoint.json");
const linksPath = path.join(outputRoot, "apple_music_links_v1.jsonl");
const reviewPath = path.join(outputRoot, "apple_music_manual_review_queue.csv");
const summaryPath = path.join(outputRoot, "apple_music_links_summary.json");
const manifestPath = path.join(outputRoot, "apple_music_resolution_run_manifest.md");

const graphNodes = readJson(path.join(currentRoot, "graph_linking_node_set.json")).rows;
const sidecarAlbumRows = readCsv(path.join(currentRoot, "album_track_sidecar_album_resolution.csv"));
const sidecarTrackRows = readCsv(path.join(currentRoot, "album_track_sidecar_tracks.csv"));

const sidecarAlbumByIdentityKey = new Map(
  sidecarAlbumRows
    .filter((row) => row.apple_collection_id)
    .map((row) => [row.candidate_identity_key, row]),
);
const sidecarTrackIndex = buildSidecarTrackIndex(sidecarTrackRows);

const seededLinks = buildSeedLinks();
const graphJobs = buildGraphJobs();
const selectedJobs = applyArgsToJobs(graphJobs);
const checkpoint = args.resume ? readCheckpoint() : null;
const completedJobKeys = new Set(checkpoint?.completed_job_keys ?? []);
const links = checkpoint?.links ?? [];
const reviews = checkpoint?.reviews ?? [];
const seededLinkKeys = new Set(seededLinks.map((link) => link.link_key));
const linkKeys = new Set(links.map((link) => link.link_key));
const reviewKeys = new Set(reviews.map((review) => review.review_key));

for (const link of seededLinks) {
  if (!linkKeys.has(link.link_key)) {
    links.push(link);
    linkKeys.add(link.link_key);
  }
}

let processed = 0;
const runnableJobs = selectedJobs.filter((job) => !completedJobKeys.has(job.job_key));
console.error(JSON.stringify({
  run_version: runVersion,
  mode: args.mode,
  storefront,
  dry_run: args.dryRun,
  total_graph_jobs: graphJobs.length,
  selected_jobs: selectedJobs.length,
  runnable_jobs: runnableJobs.length,
  seeded_links: seededLinks.length,
}, null, 2));

await runPool(runnableJobs, args.concurrency, async (job) => {
  const outcome = await safelyResolveJob(job);
  recordOutcome(job, outcome);
  completedJobKeys.add(job.job_key);
  processed += 1;

  if (processed % args.checkpointEvery === 0) writeCheckpoint("partial");
  if (processed % args.progressEvery === 0 || processed === runnableJobs.length) {
    const summary = buildSummary("partial");
    console.error(`apple link pass: ${processed}/${runnableJobs.length} runnable, links=${summary.counts.links_total}, review=${summary.counts.review_total}`);
  }
});

writeCheckpoint("complete");
writeFinalArtifacts();
if (!args.keepCheckpoint && fs.existsSync(checkpointPath)) fs.unlinkSync(checkpointPath);

function parseArgs(argv) {
  const parsed = {
    envPath: envPathDefault,
    storefront: null,
    mode: "all",
    limit: Number.NaN,
    concurrency: 6,
    progressEvery: 100,
    checkpointEvery: 100,
    resume: true,
    keepCheckpoint: false,
    dryRun: false,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--env") parsed.envPath = argv[++index];
    else if (arg === "--storefront") parsed.storefront = argv[++index];
    else if (arg === "--mode") parsed.mode = argv[++index];
    else if (arg === "--limit") parsed.limit = Number(argv[++index]);
    else if (arg === "--concurrency") parsed.concurrency = Number(argv[++index]);
    else if (arg === "--progress-every") parsed.progressEvery = Number(argv[++index]);
    else if (arg === "--checkpoint-every") parsed.checkpointEvery = Number(argv[++index]);
    else if (arg === "--no-resume") parsed.resume = false;
    else if (arg === "--keep-checkpoint") parsed.keepCheckpoint = true;
    else if (arg === "--dry-run") parsed.dryRun = true;
  }

  const allowedModes = new Set(["all", "seed", "artists", "albums", "songs", "recordings", "graph"]);
  if (!allowedModes.has(parsed.mode)) {
    throw new Error(`Unsupported --mode ${parsed.mode}. Expected one of ${[...allowedModes].join(", ")}`);
  }
  if (!Number.isFinite(parsed.concurrency) || parsed.concurrency < 1) parsed.concurrency = 1;
  if (parsed.concurrency > 12) parsed.concurrency = 12;
  if (!Number.isFinite(parsed.progressEvery) || parsed.progressEvery < 1) parsed.progressEvery = 100;
  if (!Number.isFinite(parsed.checkpointEvery) || parsed.checkpointEvery < 1) parsed.checkpointEvery = parsed.progressEvery;
  return parsed;
}

function loadResolverEnv(envPath) {
  const text = fs.readFileSync(envPath, "utf8");
  const loaded = {};
  for (const rawLine of text.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line.startsWith("#")) continue;
    const index = line.indexOf("=");
    if (index === -1) continue;
    loaded[line.slice(0, index)] = line.slice(index + 1);
  }

  for (const key of ["APPLE_MUSIC_TEAM_ID", "APPLE_MUSIC_KEY_ID", "APPLE_MUSIC_PRIVATE_KEY_PATH"]) {
    if (!loaded[key]) throw new Error(`${key} is required in ${envPath}`);
    if (loaded[key].includes("REPLACE_WITH") && key !== "APPLE_MUSIC_PRIVATE_KEY_PATH") {
      throw new Error(`${key} still contains a placeholder in ${envPath}`);
    }
  }
  if (!fs.existsSync(loaded.APPLE_MUSIC_PRIVATE_KEY_PATH)) {
    throw new Error(`APPLE_MUSIC_PRIVATE_KEY_PATH does not exist: ${loaded.APPLE_MUSIC_PRIVATE_KEY_PATH}`);
  }
  return loaded;
}

function makeDeveloperToken(loadedEnv) {
  const privateKey = fs.readFileSync(loadedEnv.APPLE_MUSIC_PRIVATE_KEY_PATH, "utf8");
  if (!privateKey.includes("BEGIN PRIVATE KEY") || privateKey.includes("PASTE_PRIVATE_KEY_BODY_HERE")) {
    throw new Error("Apple Music private key file is missing PEM markers or still contains placeholder text.");
  }

  const now = Math.floor(Date.now() / 1000);
  const tokenTtlSeconds = 6 * 60 * 60;
  const header = { alg: "ES256", kid: loadedEnv.APPLE_MUSIC_KEY_ID };
  const payload = { iss: loadedEnv.APPLE_MUSIC_TEAM_ID, iat: now, exp: now + tokenTtlSeconds };
  const signingInput = `${base64UrlJson(header)}.${base64UrlJson(payload)}`;
  const signer = crypto.createSign("SHA256");
  signer.update(signingInput);
  signer.end();
  return `${signingInput}.${derSignatureToJose(signer.sign(privateKey))}`;
}

function base64UrlJson(value) {
  return base64Url(Buffer.from(JSON.stringify(value)));
}

function base64Url(value) {
  return Buffer.from(value)
    .toString("base64")
    .replace(/=/g, "")
    .replace(/\+/g, "-")
    .replace(/\//g, "_");
}

function derSignatureToJose(signatureDer) {
  const paramBytes = 32;
  const signature = Buffer.from(signatureDer);
  let offset = 0;
  if (signature[offset++] !== 0x30) throw new Error("Invalid DER signature sequence.");
  let sequenceLength = signature[offset++];
  if (sequenceLength & 0x80) {
    const lengthBytes = sequenceLength & 0x7f;
    sequenceLength = 0;
    for (let index = 0; index < lengthBytes; index += 1) {
      sequenceLength = (sequenceLength << 8) | signature[offset++];
    }
  }
  if (signature[offset++] !== 0x02) throw new Error("Invalid DER signature integer r.");
  let rLength = signature[offset++];
  let r = signature.slice(offset, offset + rLength);
  offset += rLength;
  if (signature[offset++] !== 0x02) throw new Error("Invalid DER signature integer s.");
  let sLength = signature[offset++];
  let s = signature.slice(offset, offset + sLength);

  if (r.length > paramBytes) r = r.slice(r.length - paramBytes);
  if (s.length > paramBytes) s = s.slice(s.length - paramBytes);
  if (r.length < paramBytes) r = Buffer.concat([Buffer.alloc(paramBytes - r.length), r]);
  if (s.length < paramBytes) s = Buffer.concat([Buffer.alloc(paramBytes - s.length), s]);
  return base64Url(Buffer.concat([r, s]));
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function readCsv(file) {
  const text = fs.readFileSync(file, "utf8");
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
  if (field.length > 0 || row.length > 0) {
    row.push(field);
    rows.push(row);
  }

  const [headers, ...dataRows] = rows;
  return dataRows
    .filter((dataRow) => dataRow.length === headers.length)
    .map((dataRow) => Object.fromEntries(headers.map((header, index) => [header, dataRow[index]])));
}

function writeCsv(file, rows, headers) {
  const lines = [headers.join(",")];
  for (const row of rows) {
    lines.push(headers.map((header) => csvCell(row[header] ?? "")).join(","));
  }
  fs.writeFileSync(file, `${lines.join("\n")}\n`);
}

function csvCell(value) {
  const string = Array.isArray(value) ? value.join(";") : String(value ?? "");
  if (/[",\n\r]/.test(string)) return `"${string.replace(/"/g, "\"\"")}"`;
  return string;
}

function buildSidecarTrackIndex(rows) {
  const byExactYear = new Map();
  const byNoYear = new Map();
  const appleRows = rows.filter((row) => row.apple_track_id);
  for (const row of appleRows) {
    pushIndex(byExactYear, trackIndexKey(row.track_artist_name, row.track_title, row.album_year), row);
    pushIndex(byNoYear, trackIndexKey(row.track_artist_name, row.track_title, ""), row);
  }
  return { byExactYear, byNoYear, appleRows };
}

function pushIndex(map, key, row) {
  const bucket = map.get(key) ?? [];
  bucket.push(row);
  map.set(key, bucket);
}

function buildSeedLinks() {
  const seedLinks = [];
  for (const row of sidecarAlbumRows) {
    if (!row.apple_collection_id) continue;
    seedLinks.push(makeLink({
      source_ref: row.candidate_identity_key,
      source_type: "album_sidecar_album",
      source_candidate_type: "album",
      apple_catalog_id: row.apple_collection_id,
      apple_resource_type: "album",
      match_status: "verified",
      match_basis: "existing_sidecar_apple_collection_id_catalog_validation",
      confidence: "high",
      rank: "",
      title_match: "not_persisted",
      artist_match: "not_persisted",
      year_delta: "",
      warnings: "",
    }));
  }

  const seenTrackRefs = new Set();
  for (const row of sidecarTrackRows) {
    if (!row.apple_track_id) continue;
    const sourceRef = [
      row.candidate_identity_key,
      row.disc_number || "",
      row.track_number || "",
      normalize(row.track_artist_name),
      normalize(row.track_title),
    ].join("@@");
    if (seenTrackRefs.has(sourceRef)) continue;
    seenTrackRefs.add(sourceRef);
    seedLinks.push(makeLink({
      source_ref: sourceRef,
      source_type: "album_sidecar_track",
      source_candidate_type: "track",
      apple_catalog_id: row.apple_track_id,
      apple_resource_type: "song",
      match_status: "verified",
      match_basis: "existing_sidecar_apple_track_id_catalog_validation",
      confidence: "high",
      rank: "",
      title_match: "not_persisted",
      artist_match: "not_persisted",
      year_delta: "",
      warnings: "",
    }));
  }
  return seedLinks.sort((a, b) => a.link_key.localeCompare(b.link_key));
}

function buildGraphJobs() {
  return graphNodes
    .map((node) => {
      const sourceType = `graph_${node.candidate_type}`;
      return {
        job_key: `${sourceType}:${node.candidate_identity_key}`,
        source_ref: node.candidate_identity_key,
        source_type: sourceType,
        candidate_type: node.candidate_type,
        artist_display_name: node.artist_display_name ?? "",
        title: node.title ?? "",
        year: node.year ? String(node.year) : "",
        import_classes: node.import_classes ?? [],
        risk_statuses: node.risk_statuses ?? [],
        version_or_composition_risks: node.version_or_composition_risks ?? [],
        archetype_ids: node.archetype_ids ?? [],
      };
    })
    .sort((a, b) => a.job_key.localeCompare(b.job_key));
}

function applyArgsToJobs(jobs) {
  let selected = jobs;
  if (args.mode === "seed") selected = [];
  if (args.mode === "artists") selected = jobs.filter((job) => job.candidate_type === "artist_anchor");
  if (args.mode === "albums") selected = jobs.filter((job) => job.candidate_type === "album");
  if (args.mode === "songs") selected = jobs.filter((job) => job.candidate_type === "song");
  if (args.mode === "recordings") selected = jobs.filter((job) => job.candidate_type === "recording");
  if (args.mode === "graph") selected = jobs;
  if (Number.isFinite(args.limit)) selected = selected.slice(0, args.limit);
  return selected;
}

function readCheckpoint() {
  if (!fs.existsSync(checkpointPath)) return null;
  const loaded = readJson(checkpointPath);
  if (loaded.run_version !== runVersion || loaded.storefront !== storefront) {
    throw new Error(`Checkpoint ${checkpointPath} does not match run_version/storefront.`);
  }
  return loaded;
}

function writeCheckpoint(status) {
  const checkpointValue = {
    run_version: runVersion,
    status,
    storefront,
    generated_at: new Date().toISOString(),
    completed_job_keys: [...completedJobKeys].sort(),
    links: sortLinks(links),
    reviews: sortReviews(reviews),
  };
  const tempPath = `${checkpointPath}.tmp`;
  fs.writeFileSync(tempPath, `${JSON.stringify(checkpointValue, null, 2)}\n`);
  fs.renameSync(tempPath, checkpointPath);
}

async function resolveJob(job) {
  const seeded = seededGraphOutcome(job);
  if (seeded) return seeded;
  if (args.dryRun) return manualReview("dry_run_no_catalog_call", { candidate_count: 0 });

  if (job.candidate_type === "artist_anchor") return resolveArtist(job);
  if (job.candidate_type === "album") return resolveAlbum(job);
  if (job.candidate_type === "song" || job.candidate_type === "recording") return resolveSong(job);
  return manualReview(`unsupported_candidate_type_${job.candidate_type}`, { candidate_count: 0 });
}

async function safelyResolveJob(job) {
  try {
    return await resolveJob(job);
  } catch (error) {
    return manualReview("apple_catalog_request_error", {
      error_message: error instanceof Error ? error.message : String(error),
    });
  }
}

function seededGraphOutcome(job) {
  if (job.candidate_type === "album") {
    const album = sidecarAlbumByIdentityKey.get(job.source_ref);
    if (!album) return null;
    return {
      kind: "link",
      apple_catalog_id: album.apple_collection_id,
      apple_resource_type: "album",
      match_status: "verified",
      match_basis: "graph_album_matched_existing_sidecar_apple_collection_id",
      confidence: "high",
      rank: "",
      title_match: "not_persisted",
      artist_match: "not_persisted",
      year_delta: "",
      warnings: "",
    };
  }

  if (job.candidate_type === "song" || job.candidate_type === "recording") {
    const exactYearRows = sidecarTrackIndex.byExactYear.get(trackIndexKey(job.artist_display_name, job.title, job.year)) ?? [];
    const exactYearIds = uniqueAppleTrackIds(exactYearRows);
    if (exactYearIds.length === 1) {
      return {
        kind: "link",
        apple_catalog_id: exactYearIds[0],
        apple_resource_type: "song",
        match_status: "verified",
        match_basis: "graph_song_matched_unique_sidecar_track_artist_title_year",
        confidence: "high",
        rank: "",
        title_match: "exact_normalized",
        artist_match: "exact_or_compatible_normalized",
        year_delta: "0",
        warnings: "",
      };
    }
    if (exactYearIds.length > 1) {
      return manualReview("sidecar_track_artist_title_year_ambiguous", { candidate_count: exactYearIds.length });
    }

    const noYearRows = sidecarTrackIndex.byNoYear.get(trackIndexKey(job.artist_display_name, job.title, "")) ?? [];
    const noYearIds = uniqueAppleTrackIds(noYearRows);
    if (noYearIds.length === 1) {
      return {
        kind: "link",
        apple_catalog_id: noYearIds[0],
        apple_resource_type: "song",
        match_status: "candidate_verified",
        match_basis: "graph_song_matched_unique_sidecar_track_artist_title_without_year",
        confidence: "medium",
        rank: "",
        title_match: "exact_normalized",
        artist_match: "exact_or_compatible_normalized",
        year_delta: "",
        warnings: "year_not_confirmed",
      };
    }
    if (noYearIds.length > 1) {
      return manualReview("sidecar_track_artist_title_ambiguous", { candidate_count: noYearIds.length });
    }
  }

  return null;
}

function uniqueAppleTrackIds(rows) {
  return [...new Set(rows.map((row) => row.apple_track_id).filter(Boolean))];
}

async function resolveArtist(job) {
  const query = job.artist_display_name;
  const items = await searchCatalog("artists", query, 5);
  if (!items.length) return manualReview("apple_artist_search_no_results", { candidate_count: 0 });

  const expectedArtist = normalize(job.artist_display_name);
  const bestIndex = items.findIndex((item) => normalize(item.attributes?.name) === expectedArtist);
  if (bestIndex === 0) {
    return linkFromItem(items[0], "artist", "apple_artist_search_top_exact_normalized", "high", bestIndex, {
      title_match: "not_applicable",
      artist_match: "exact_normalized",
    });
  }
  if (bestIndex > 0) {
    return linkFromItem(items[bestIndex], "artist", "apple_artist_search_exact_normalized_in_top5", "medium", bestIndex, {
      title_match: "not_applicable",
      artist_match: "exact_normalized",
      warnings: "not_top_result",
    });
  }
  return manualReview("apple_artist_search_no_exact_normalized_result", { candidate_count: items.length });
}

async function resolveAlbum(job) {
  const query = `${job.artist_display_name} ${job.title}`.trim();
  const items = await searchCatalog("albums", query, 10);
  if (!items.length) return manualReview("apple_album_search_no_results", { candidate_count: 0 });

  const scored = items.map((item, index) => scoreTitledItem(item, job, index));
  const accepted = scored.find((candidate) => candidate.score >= 92 && candidate.titleExact && candidate.artistCompatible && candidate.yearDelta <= 1)
    ?? scored.find((candidate) => candidate.score >= 88 && candidate.titleExact && candidate.artistCompatible);

  if (!accepted) {
    return manualReview("apple_album_search_no_auto_match", { candidate_count: items.length, best_score: scored[0]?.score ?? 0 });
  }
  return linkFromItem(accepted.item, "album", accepted.yearDelta <= 1 ? "apple_album_search_title_artist_year_auto_match" : "apple_album_search_title_artist_auto_match", accepted.yearDelta <= 1 ? "high" : "medium", accepted.index, {
    title_match: accepted.titleExact ? "exact_normalized" : "compatible_normalized",
    artist_match: accepted.artistCompatible ? "compatible_normalized" : "not_matched",
    year_delta: accepted.yearDelta,
    warnings: accepted.yearDelta > 1 ? "year_not_confirmed" : "",
  });
}

async function resolveSong(job) {
  const query = `${job.artist_display_name} ${job.title}`.trim();
  const items = await searchCatalog("songs", query, 10);
  if (!items.length) return manualReview("apple_song_search_no_results", { candidate_count: 0 });

  const scored = items.map((item, index) => scoreTitledItem(item, job, index));
  const hasVersionRisk = (job.version_or_composition_risks ?? []).some((risk) => risk && risk !== "none");
  const accepted = scored.find((candidate) => candidate.score >= 94 && candidate.titleExact && candidate.artistCompatible && candidate.yearDelta <= 1)
    ?? (!hasVersionRisk ? scored.find((candidate) => candidate.score >= 90 && candidate.titleExact && candidate.artistCompatible) : null);

  if (!accepted) {
    return manualReview(hasVersionRisk ? "apple_song_search_needs_review_version_risk" : "apple_song_search_no_auto_match", {
      candidate_count: items.length,
      best_score: scored[0]?.score ?? 0,
    });
  }
  return linkFromItem(accepted.item, "song", accepted.yearDelta <= 1 ? "apple_song_search_title_artist_year_auto_match" : "apple_song_search_title_artist_auto_match", accepted.yearDelta <= 1 ? "high" : "medium", accepted.index, {
    title_match: accepted.titleExact ? "exact_normalized" : "compatible_normalized",
    artist_match: accepted.artistCompatible ? "compatible_normalized" : "not_matched",
    year_delta: accepted.yearDelta,
    warnings: accepted.yearDelta > 1 ? "year_not_confirmed" : "",
  });
}

async function searchCatalog(type, term, limit) {
  const pathName = `/v1/catalog/${encodeURIComponent(storefront)}/search?term=${encodeURIComponent(term)}&types=${encodeURIComponent(type)}&limit=${limit}`;
  const payload = await appleGet(pathName);
  return payload?.results?.[type]?.data ?? [];
}

async function appleGet(pathName, attempt = 1) {
  const response = await requestJson(pathName);
  if (response.status === 200) return response.payload;
  if ((response.status === 429 || response.status >= 500) && attempt <= 5) {
    const retryAfterMs = Number(response.headers["retry-after"]) > 0
      ? Number(response.headers["retry-after"]) * 1000
      : 500 * (2 ** (attempt - 1));
    await sleep(retryAfterMs + Math.floor(Math.random() * 250));
    return appleGet(pathName, attempt + 1);
  }
  throw new Error(`Apple Music request failed status=${response.status} path=${pathName}`);
}

function requestJson(pathName) {
  return new Promise((resolve, reject) => {
    const request = https.request({
      hostname: "api.music.apple.com",
      path: pathName,
      method: "GET",
      headers: {
        Authorization: `Bearer ${developerToken}`,
      },
    }, (response) => {
      let body = "";
      response.setEncoding("utf8");
      response.on("data", (chunk) => {
        body += chunk;
      });
      response.on("end", () => {
        let payload = null;
        try {
          payload = body ? JSON.parse(body) : null;
        } catch {
          payload = null;
        }
        resolve({ status: response.statusCode ?? 0, headers: response.headers, payload });
      });
    });
    request.on("error", reject);
    request.end();
  });
}

function scoreTitledItem(item, job, index) {
  const attrs = item.attributes ?? {};
  const expectedTitle = normalize(job.title);
  const expectedArtist = normalize(job.artist_display_name);
  const candidateTitle = normalize(attrs.name);
  const candidateArtist = normalize(attrs.artistName);
  const expectedYear = Number(job.year);
  const candidateYear = Number(String(attrs.releaseDate ?? "").slice(0, 4));
  const titleExact = candidateTitle === expectedTitle;
  const artistCompatible = candidateArtist === expectedArtist
    || candidateArtist.includes(expectedArtist)
    || expectedArtist.includes(candidateArtist);
  const yearDelta = Number.isFinite(expectedYear) && Number.isFinite(candidateYear)
    ? Math.abs(expectedYear - candidateYear)
    : 99;

  let score = 0;
  if (titleExact) score += 50;
  else if (candidateTitle.includes(expectedTitle) || expectedTitle.includes(candidateTitle)) score += 38;
  if (artistCompatible) score += 35;
  if (yearDelta === 0) score += 15;
  else if (yearDelta <= 1) score += 12;
  else if (yearDelta <= 3) score += 7;
  else if (!Number.isFinite(expectedYear) || !Number.isFinite(candidateYear)) score += 4;
  score -= Math.min(index, 5);

  return { item, index, score, titleExact, artistCompatible, yearDelta };
}

function linkFromItem(item, resourceType, basis, confidence, index, extra = {}) {
  return {
    kind: "link",
    apple_catalog_id: item.id,
    apple_resource_type: resourceType,
    match_status: confidence === "high" ? "verified" : "candidate_verified",
    match_basis: basis,
    confidence,
    rank: index + 1,
    title_match: extra.title_match ?? "",
    artist_match: extra.artist_match ?? "",
    year_delta: extra.year_delta ?? "",
    warnings: extra.warnings ?? "",
  };
}

function manualReview(reason, extra = {}) {
  return {
    kind: "review",
    review_reason: reason,
    candidate_count: extra.candidate_count ?? "",
    best_score: extra.best_score ?? "",
    error_message: extra.error_message ?? "",
  };
}

function recordOutcome(job, outcome) {
  if (outcome.kind === "link") {
    const link = makeLink({
      source_ref: job.source_ref,
      source_type: job.source_type,
      source_candidate_type: job.candidate_type,
      apple_catalog_id: outcome.apple_catalog_id,
      apple_resource_type: outcome.apple_resource_type,
      match_status: outcome.match_status,
      match_basis: outcome.match_basis,
      confidence: outcome.confidence,
      rank: outcome.rank,
      title_match: outcome.title_match,
      artist_match: outcome.artist_match,
      year_delta: outcome.year_delta,
      warnings: outcome.warnings,
    });
    if (!linkKeys.has(link.link_key)) {
      links.push(link);
      linkKeys.add(link.link_key);
    }
    return;
  }

  const review = makeReview(job, outcome);
  if (!reviewKeys.has(review.review_key)) {
    reviews.push(review);
    reviewKeys.add(review.review_key);
  }
}

function makeLink(fields) {
  const sourceRef = fields.source_ref;
  const appleId = fields.apple_catalog_id;
  return {
    link_key: `${fields.source_type}:${sourceRef}:apple_music:${fields.apple_resource_type}:${appleId}:${storefront}`,
    run_version: runVersion,
    source_ref: sourceRef,
    source_type: fields.source_type,
    source_candidate_type: fields.source_candidate_type,
    external_catalog: "apple_music",
    apple_catalog_id: appleId,
    apple_resource_type: fields.apple_resource_type,
    storefront,
    match_status: fields.match_status,
    match_basis: fields.match_basis,
    confidence: fields.confidence,
    result_rank: fields.rank,
    title_match: fields.title_match,
    artist_match: fields.artist_match,
    year_delta: fields.year_delta,
    warnings: fields.warnings,
    verified_at: new Date().toISOString(),
    raw_payload_persisted: false,
  };
}

function makeReview(job, outcome) {
  return {
    review_key: `${job.source_type}:${job.source_ref}:${outcome.review_reason}`,
    run_version: runVersion,
    source_ref: job.source_ref,
    source_type: job.source_type,
    source_candidate_type: job.candidate_type,
    artist_display_name: job.artist_display_name,
    title: job.title,
    year: job.year,
    storefront,
    review_reason: outcome.review_reason,
    candidate_count: outcome.candidate_count,
    best_score: outcome.best_score,
    error_message: outcome.error_message,
    raw_payload_persisted: false,
  };
}

function writeFinalArtifacts() {
  const sortedLinks = sortLinks(links);
  const sortedReviews = sortReviews(reviews);
  fs.writeFileSync(linksPath, `${sortedLinks.map((link) => JSON.stringify(link)).join("\n")}\n`);
  writeCsv(reviewPath, sortedReviews, [
    "review_key",
    "run_version",
    "source_ref",
    "source_type",
    "source_candidate_type",
    "artist_display_name",
    "title",
    "year",
    "storefront",
    "review_reason",
    "candidate_count",
    "best_score",
    "error_message",
    "raw_payload_persisted",
  ]);

  const summary = buildSummary("complete");
  fs.writeFileSync(summaryPath, `${JSON.stringify(summary, null, 2)}\n`);
  fs.writeFileSync(manifestPath, buildManifest(summary, sortedReviews));
  console.log(JSON.stringify(summary, null, 2));
}

function buildSummary(status) {
  const sortedLinks = sortLinks(links);
  const sortedReviews = sortReviews(reviews);
  return {
    run_version: runVersion,
    status,
    generated_at: new Date().toISOString(),
    storefront,
    policy: {
      raw_apple_payloads_persisted: false,
      persisted_catalog_fields: ["apple_catalog_id", "apple_resource_type", "storefront", "match metadata"],
      excluded_persistent_fields: ["artwork", "previews", "lyrics", "raw_catalog_payload", "music_user_token"],
    },
    inputs: {
      graph_linking_node_set: "data/canonical_graph/current/graph_linking_node_set.json",
      album_track_sidecar_album_resolution: "data/canonical_graph/current/album_track_sidecar_album_resolution.csv",
      album_track_sidecar_tracks: "data/canonical_graph/current/album_track_sidecar_tracks.csv",
    },
    counts: {
      graph_nodes_total: graphJobs.length,
      graph_jobs_selected_current_invocation: selectedJobs.length,
      graph_jobs_completed_cumulative: completedJobKeys.size,
      graph_jobs_remaining: Math.max(graphJobs.length - completedJobKeys.size, 0),
      sidecar_seed_links: seededLinks.length,
      links_total: sortedLinks.length,
      review_total: sortedReviews.length,
      links_by_source_type: countBy(sortedLinks, "source_type"),
      links_by_resource_type: countBy(sortedLinks, "apple_resource_type"),
      links_by_match_basis: countBy(sortedLinks, "match_basis"),
      reviews_by_reason: countBy(sortedReviews, "review_reason"),
    },
  };
}

function buildManifest(summary, sortedReviews) {
  const reviewPreview = sortedReviews.slice(0, 20).map((review) => (
    `| ${review.source_candidate_type} | ${escapeMd(review.artist_display_name)} | ${escapeMd(review.title)} | ${review.year} | ${review.review_reason} |`
  ));
  return `# Apple Music Link Pass v1

Generated: ${summary.generated_at}

Status: \`${summary.status}\`

Storefront: \`${storefront}\`

## Policy

- Raw Apple payloads persisted: \`false\`
- Durable output stores Apple catalog IDs, resource type, storefront, source refs, match status, and scoring metadata only.
- Artwork, previews, lyrics, MusicKit content, raw catalog responses, and Music User Tokens are not persisted.

## Inputs

- \`${summary.inputs.graph_linking_node_set}\`
- \`${summary.inputs.album_track_sidecar_album_resolution}\`
- \`${summary.inputs.album_track_sidecar_tracks}\`

## Counts

- Graph nodes total: ${summary.counts.graph_nodes_total}
- Graph jobs completed cumulative: ${summary.counts.graph_jobs_completed_cumulative}
- Graph jobs remaining: ${summary.counts.graph_jobs_remaining}
- Sidecar seed links: ${summary.counts.sidecar_seed_links}
- Links total: ${summary.counts.links_total}
- Manual review rows: ${summary.counts.review_total}

## Links By Source Type

${tableFromCounts(summary.counts.links_by_source_type)}

## Links By Match Basis

${tableFromCounts(summary.counts.links_by_match_basis)}

## Reviews By Reason

${tableFromCounts(summary.counts.reviews_by_reason)}

## Manual Review Preview

| type | artist | title | year | reason |
| --- | --- | --- | --- | --- |
${reviewPreview.length ? reviewPreview.join("\n") : "|  |  |  |  | none |"}
`;
}

function tableFromCounts(counts) {
  const rows = Object.entries(counts)
    .sort((a, b) => b[1] - a[1])
    .map(([key, count]) => `| ${escapeMd(key)} | ${count} |`);
  return ["| key | count |", "| --- | ---: |", ...rows].join("\n");
}

function sortLinks(values) {
  return [...values].sort((a, b) => a.link_key.localeCompare(b.link_key));
}

function sortReviews(values) {
  return [...values].sort((a, b) => a.review_key.localeCompare(b.review_key));
}

function countBy(values, key) {
  const counts = {};
  for (const value of values) {
    const countKey = value[key] || "unknown";
    counts[countKey] = (counts[countKey] ?? 0) + 1;
  }
  return counts;
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

function trackIndexKey(artist, title, year) {
  return `${normalize(artist)}|${normalize(title)}|${String(year ?? "")}`;
}

function escapeMd(value) {
  return String(value ?? "").replace(/\|/g, "\\|");
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
