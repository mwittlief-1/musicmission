#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

const repoRoot = process.cwd();
const passD = path.join(repoRoot, "data/canonical_graph/depth_hardening_v0_2/pass_d");
const seedPath = path.join(passD, "album_sidecar_seed_albums_v1.json");

const generatedOn = "2026-05-26";
const sidecarVersion = "album_track_sidecar_v1";
const userAgent = "WaymarkMusicMission/0.1 (https://github.com/; album-sidecar-build)";
let lastAppleRequestAt = 0;
let appleGate = Promise.resolve();
let appleCircuitOpenUntil = 0;
let lastMusicBrainzRequestAt = 0;
let musicBrainzGate = Promise.resolve();

const args = parseArgs(process.argv.slice(2));
const seed = readJson(seedPath);
const albumNodes = buildAlbumNodes(seed.rows);

if (args.normalizeExisting) {
  const existing = readJson(path.join(passD, "album_track_sidecar_v1.json"));
  const normalizedAlbums = existing.albums.map(normalizeAlbumTrackOrder);
  writeFinalArtifacts(normalizedAlbums);
  process.exit(0);
}

const existingSidecar = args.resume ? readExistingSidecar() : null;
const existingByIdentityKey = new Map(
  (existingSidecar?.albums ?? []).map((album) => [album.candidate_identity_key, album]),
);

const results = [];
const selectedAlbumNodes = selectAlbumNodesForRun(albumNodes, existingByIdentityKey);
let completed = 0;

await runPool(selectedAlbumNodes, args.concurrency, async (album) => {
  const cached = existingByIdentityKey.get(album.candidate_identity_key);
  if (cached && cached.resolution?.status === "resolved" && Array.isArray(cached.tracks) && cached.tracks.length > 0) {
    results.push(rehydrateExistingAlbum(album, cached));
  } else {
    if (args.retryUnresolved) {
      console.error(`album sidecar retry: ${completed + 1}/${selectedAlbumNodes.length} ${album.artist_display_name} — ${album.title}`);
    }
    results.push(await resolveAlbum(album));
  }

  completed += 1;
  if (completed % args.checkpointEvery === 0) {
    writePartialCheckpoint(results);
  }
  if (completed % args.progressEvery === 0 || completed === selectedAlbumNodes.length) {
    console.error(`album sidecar fetch: ${completed}/${selectedAlbumNodes.length}`);
  }
});

writeFinalArtifacts(results);
removePartialCheckpoint();

function parseArgs(argv) {
  const parsed = {
    limit: Number.NaN,
    concurrency: 8,
    progressEvery: 25,
    checkpointEvery: 25,
    resume: true,
    appleOnly: false,
    normalizeExisting: false,
    aggressive: false,
    retryUnresolved: false,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--limit") parsed.limit = Number(argv[++index]);
    if (arg === "--concurrency") parsed.concurrency = Number(argv[++index]);
    if (arg === "--progress-every") parsed.progressEvery = Number(argv[++index]);
    if (arg === "--checkpoint-every") parsed.checkpointEvery = Number(argv[++index]);
    if (arg === "--no-resume") parsed.resume = false;
    if (arg === "--apple-only") parsed.appleOnly = true;
    if (arg === "--normalize-existing") parsed.normalizeExisting = true;
    if (arg === "--aggressive") parsed.aggressive = true;
    if (arg === "--retry-unresolved") parsed.retryUnresolved = true;
  }

  if (!Number.isFinite(parsed.concurrency) || parsed.concurrency < 1) parsed.concurrency = 1;
  if (!Number.isFinite(parsed.progressEvery) || parsed.progressEvery < 1) parsed.progressEvery = 25;
  if (!Number.isFinite(parsed.checkpointEvery) || parsed.checkpointEvery < 1) parsed.checkpointEvery = parsed.progressEvery;
  return parsed;
}

function selectAlbumNodesForRun(nodes, existingByKey) {
  if (!args.retryUnresolved) {
    return Number.isFinite(args.limit) ? nodes.slice(0, args.limit) : nodes;
  }

  const unresolvedNodes = nodes.filter((node) => {
    const cached = existingByKey.get(node.candidate_identity_key);
    return cached && cached.resolution?.status !== "resolved";
  });
  const selected = Number.isFinite(args.limit) ? unresolvedNodes.slice(0, args.limit) : unresolvedNodes;
  const selectedKeys = new Set(selected.map((node) => node.candidate_identity_key));

  for (const node of nodes) {
    if (selectedKeys.has(node.candidate_identity_key)) continue;
    const cached = existingByKey.get(node.candidate_identity_key);
    if (cached) results.push(rehydrateExistingAlbum(node, cached));
  }

  return selected;
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function readExistingSidecar() {
  const sidecarPath = path.join(passD, "album_track_sidecar_v1.json");
  const partialPath = path.join(passD, "album_track_sidecar_v1.partial.json");
  const candidates = [sidecarPath, partialPath]
    .filter((file) => fs.existsSync(file))
    .map((file) => ({ file, sidecar: readJson(file) }))
    .sort((a, b) => (b.sidecar.albums?.length ?? 0) - (a.sidecar.albums?.length ?? 0));
  return candidates[0]?.sidecar ?? null;
}

function writeJson(file, value) {
  fs.writeFileSync(path.join(passD, file), `${JSON.stringify(value, null, 2)}\n`);
}

function writePartialCheckpoint(albums) {
  const sortedAlbums = [...albums]
    .map(normalizeAlbumTrackOrder)
    .sort((a, b) => a.candidate_identity_key.localeCompare(b.candidate_identity_key));
  const partial = buildArtifacts(sortedAlbums).sidecar;
  partial.metadata.status = "partial";
  partial.metadata.partial_checkpoint = true;
  partial.metadata.completed_album_identity_rows = sortedAlbums.length;
  const finalPath = path.join(passD, "album_track_sidecar_v1.partial.json");
  const tempPath = `${finalPath}.tmp`;
  fs.writeFileSync(tempPath, `${JSON.stringify(partial, null, 2)}\n`);
  fs.renameSync(tempPath, finalPath);
}

function writeFinalArtifacts(albums) {
  const normalizedAlbums = albums
    .map(normalizeAlbumTrackOrder)
    .sort((a, b) => a.candidate_identity_key.localeCompare(b.candidate_identity_key));
  const artifacts = buildArtifacts(normalizedAlbums);
  writeJson("album_track_sidecar_v1.json", artifacts.sidecar);
  writeCsv("album_track_sidecar_album_resolution_v1.csv", artifacts.albumResolutionRows);
  writeCsv("album_track_sidecar_tracks_v1.csv", artifacts.trackRows);
  writeMarkdown(artifacts.summary, artifacts.unresolvedRows);
  console.log(JSON.stringify(artifacts.summary, null, 2));
}

function removePartialCheckpoint() {
  const partialPath = path.join(passD, "album_track_sidecar_v1.partial.json");
  if (fs.existsSync(partialPath)) fs.unlinkSync(partialPath);
}

function buildAlbumNodes(rows) {
  const byIdentity = new Map();
  for (const row of rows) {
    const node = byIdentity.get(row.candidate_identity_key) ?? {
      candidate_identity_key: row.candidate_identity_key,
      candidate_type: row.candidate_type,
      artist_display_name: row.artist_display_name,
      title: row.title,
      year: row.year,
      sidecar_scope: row.sidecar_scope,
      membership_count: 0,
      source_membership_ids: [],
      archetype_ids: new Set(),
      archetypes: new Set(),
      import_classes: new Set(),
      memberships: [],
    };

    node.membership_count += 1;
    node.source_membership_ids.push(row.v1_membership_id);
    node.archetype_ids.add(row.archetype_id);
    node.archetypes.add(row.primary_archetype);
    node.import_classes.add(row.import_class);
    node.memberships.push({
      v1_membership_id: row.v1_membership_id,
      source_layer: row.source_layer,
      source_file: row.source_file,
      source_index: row.source_index,
      archetype_id: row.archetype_id,
      primary_family: row.primary_family,
      primary_archetype: row.primary_archetype,
      secondary_archetypes: row.secondary_archetypes,
      recognition_band: row.recognition_band,
      mission_role: row.mission_role,
      import_class: row.import_class,
      sidecar_scope: row.sidecar_scope,
      why_it_belongs: row.why_it_belongs,
      notes: row.notes,
    });

    byIdentity.set(row.candidate_identity_key, node);
  }

  return [...byIdentity.values()]
    .map((node) => ({
      ...node,
      source_membership_ids: [...node.source_membership_ids].sort(),
      archetype_ids: [...node.archetype_ids].sort(),
      archetypes: [...node.archetypes].sort(),
      import_classes: [...node.import_classes].sort(),
      memberships: node.memberships.sort((a, b) => a.v1_membership_id.localeCompare(b.v1_membership_id)),
    }))
    .sort((a, b) => a.candidate_identity_key.localeCompare(b.candidate_identity_key));
}

async function resolveAlbum(album) {
  if (args.retryUnresolved && isManualReviewFastSkip(album)) {
    return {
      ...album,
      ...unresolvedResult("manual_review_fast_skip_ambiguous_album", {
        match_score: 0,
        title: album.title,
        "artist-credit": [{ name: album.artist_display_name }],
      }),
    };
  }

  const appleResult = await safelyResolveCatalog(album, "apple", () => resolveWithApple(album));
  if (appleResult.resolution.status === "resolved" && !isSuspiciousAppleResult(appleResult)) {
    return { ...album, ...appleResult };
  }

  if (args.appleOnly && appleResult.resolution.status === "resolved") return { ...album, ...appleResult };

  const musicBrainzResult = await safelyResolveCatalog(album, "musicbrainz", () => resolveWithMusicBrainz(album));
  if (musicBrainzResult.resolution.status === "resolved") return { ...album, ...musicBrainzResult };

  if (appleResult.resolution.status === "resolved") return { ...album, ...appleResult };

  return {
    ...album,
    resolution: {
      status: "unresolved",
      selected_source: null,
      confidence: "none",
      warnings: [
        ...appleResult.resolution.warnings.map((warning) => `apple:${warning}`),
        ...musicBrainzResult.resolution.warnings.map((warning) => `musicbrainz:${warning}`),
      ],
    },
    catalog_match: null,
    tracks: [],
  };
}

async function safelyResolveCatalog(album, source, resolver) {
  try {
    return await resolver();
  } catch (error) {
    if (source === "apple") {
      appleCircuitOpenUntil = Date.now() + 60000;
    }
    return unresolvedResult(`${source}_fetch_error:${String(error.message ?? error).slice(0, 120)}`, {
      match_score: 0,
      title: album.title,
      "artist-credit": [{ name: album.artist_display_name }],
    });
  }
}

function rehydrateExistingAlbum(album, cached) {
  return {
    ...album,
    resolution: cached.resolution,
    catalog_match: cached.catalog_match,
    tracks: cached.tracks,
  };
}

async function resolveWithApple(album) {
  if (Date.now() < appleCircuitOpenUntil) {
    if (args.aggressive) {
      await sleep(appleCircuitOpenUntil - Date.now());
    } else {
      return unresolvedResult("apple_circuit_open_after_throttle", {
        match_score: 0,
        collectionName: album.title,
        artistName: album.artist_display_name,
      });
    }
  }

  if (Date.now() < appleCircuitOpenUntil) {
    return unresolvedResult("apple_circuit_open_after_throttle", {
      match_score: 0,
      collectionName: album.title,
      artistName: album.artist_display_name,
    });
  }

  const candidateByCollectionId = new Map();
  for (const term of appleSearchTerms(album)) {
    const searchUrl = new URL("https://itunes.apple.com/search");
    searchUrl.searchParams.set("term", term);
    searchUrl.searchParams.set("entity", "album");
    searchUrl.searchParams.set("media", "music");
    searchUrl.searchParams.set("country", "US");
    searchUrl.searchParams.set("limit", args.aggressive ? "25" : "15");

    const search = await fetchJson(searchUrl, { source: "apple" });
    for (const candidate of search.results ?? []) {
      if (candidate.wrapperType !== "collection" || candidate.collectionType !== "Album") continue;
      const scored = scoreAppleAlbum(album, candidate);
      const existing = candidateByCollectionId.get(candidate.collectionId);
      if (!existing || scored.match_score > existing.match_score) {
        candidateByCollectionId.set(candidate.collectionId, scored);
      }
    }

    if (!args.aggressive && candidateByCollectionId.size > 0) break;
    if (args.aggressive && [...candidateByCollectionId.values()].some((candidate) => candidate.match_score >= 90)) break;
  }

  const candidates = [...candidateByCollectionId.values()].sort((a, b) => b.match_score - a.match_score);

  const best = candidates[0];
  if (!best || !isAcceptableAppleMatch(album, best)) {
    return unresolvedResult("no_confident_album_match", best);
  }

  const lookupUrl = new URL("https://itunes.apple.com/lookup");
  lookupUrl.searchParams.set("id", String(best.collectionId));
  lookupUrl.searchParams.set("entity", "song");
  lookupUrl.searchParams.set("country", "US");

  const lookup = await fetchJson(lookupUrl, { source: "apple" });
  const collection = (lookup.results ?? []).find((result) => result.wrapperType === "collection") ?? best;
  const tracks = (lookup.results ?? [])
    .filter((result) => result.wrapperType === "track" && result.kind === "song")
    .sort((a, b) => (a.discNumber - b.discNumber) || (a.trackNumber - b.trackNumber))
    .map((track) => ({
      source: "apple_itunes_search_api",
      disc_number: track.discNumber ?? null,
      track_number: track.trackNumber ?? null,
      title: track.trackName ?? "",
      artist_name: track.artistName ?? "",
      duration_ms: track.trackTimeMillis ?? null,
      apple_track_id: track.trackId ?? null,
      apple_track_url: track.trackViewUrl ?? null,
      explicitness: track.trackExplicitness ?? "",
      is_streamable: Boolean(track.isStreamable),
    }));

  if (tracks.length === 0) {
    return unresolvedResult("matched_album_but_no_tracks", best);
  }

  const warnings = appleTracklistWarnings(album, collection, tracks);

  return {
    resolution: {
      status: "resolved",
      selected_source: "apple_itunes_search_api",
      confidence: appleConfidence(best.match_score),
      match_score: best.match_score,
      warnings,
    },
    catalog_match: {
      source: "apple_itunes_search_api",
      apple_artist_id: collection.artistId ?? best.artistId ?? null,
      apple_collection_id: collection.collectionId ?? best.collectionId ?? null,
      artist_name: collection.artistName ?? best.artistName ?? "",
      collection_name: collection.collectionName ?? best.collectionName ?? "",
      release_date: dateOnly(collection.releaseDate ?? best.releaseDate),
      release_year: yearFromDate(collection.releaseDate ?? best.releaseDate),
      track_count: collection.trackCount ?? tracks.length,
      country: collection.country ?? "USA",
      primary_genre_name: collection.primaryGenreName ?? "",
      collection_url: collection.collectionViewUrl ?? best.collectionViewUrl ?? null,
      artwork_url_100: collection.artworkUrl100 ?? best.artworkUrl100 ?? null,
      copyright: collection.copyright ?? best.copyright ?? "",
    },
    tracks,
  };
}

async function resolveWithMusicBrainz(album) {
  const candidates = [];
  for (const query of musicBrainzReleaseGroupQueries(album)) {
    await musicBrainzDelay();

    const searchUrl = new URL("https://musicbrainz.org/ws/2/release-group/");
    searchUrl.searchParams.set("query", query);
    searchUrl.searchParams.set("fmt", "json");
    searchUrl.searchParams.set("limit", args.aggressive ? "15" : "5");

    const search = await fetchJson(searchUrl, { source: "musicbrainz" });
    candidates.push(
      ...(search["release-groups"] ?? []).map((candidate) => scoreMusicBrainzReleaseGroup(album, candidate)),
    );
    if (candidates.some((candidate) => candidate.match_score >= (args.aggressive ? 84 : 72))) break;
  }

  candidates.sort((a, b) => b.match_score - a.match_score);

  const best = candidates[0];
  const bestIsAcceptable = args.aggressive ? isAcceptableMusicBrainzMatch(album, best) : (best?.match_score ?? 0) >= 72;
  if (!best || !bestIsAcceptable) {
    if (args.aggressive) {
      return await resolveWithMusicBrainzReleaseSearch(album, best);
    }
    return unresolvedResult("no_confident_release_group_match", best);
  }

  await musicBrainzDelay();

  const releasesUrl = new URL("https://musicbrainz.org/ws/2/release/");
  releasesUrl.searchParams.set("release-group", best.id);
  releasesUrl.searchParams.set("inc", "media+recordings");
  releasesUrl.searchParams.set("fmt", "json");
  releasesUrl.searchParams.set("limit", args.aggressive ? "25" : "10");

  const releases = await fetchJson(releasesUrl, { source: "musicbrainz" });
  const selectedRelease = chooseMusicBrainzRelease(releases.releases ?? [], album);
  const release = selectedRelease?.release ?? null;
  if (!release) {
    if (args.aggressive) {
      return await resolveWithMusicBrainzReleaseSearch(album, best);
    }
    return unresolvedResult("matched_release_group_but_no_release_tracks", best);
  }

  const tracks = flattenMusicBrainzTracks(release);
  if (tracks.length === 0) {
    return unresolvedResult("matched_release_but_no_tracks", best);
  }

  return {
    resolution: {
      status: "resolved",
      selected_source: "musicbrainz_ws2",
      confidence: musicBrainzConfidence(Math.min(best.match_score, selectedRelease.score + 60)),
      match_score: best.match_score,
      selected_release_score: selectedRelease.score,
      warnings: selectedRelease.warnings,
    },
    catalog_match: {
      source: "musicbrainz_ws2",
      musicbrainz_release_group_id: best.id,
      musicbrainz_release_id: release.id,
      artist_name: artistCreditName(best["artist-credit"]),
      collection_name: release.title ?? best.title ?? "",
      release_date: release.date ?? best["first-release-date"] ?? "",
      release_year: yearFromDate(release.date ?? best["first-release-date"]),
      track_count: tracks.length,
      country: release.country ?? "",
      primary_genre_name: "",
      collection_url: `https://musicbrainz.org/release/${release.id}`,
      artwork_url_100: null,
      copyright: "",
      release_status: release.status ?? "",
      release_format: (release.media ?? []).map((medium) => medium.format).filter(Boolean).join("; "),
    },
    tracks,
  };
}

async function resolveWithMusicBrainzReleaseSearch(album, bestReleaseGroupCandidate) {
  const releaseCandidates = [];
  for (const query of musicBrainzReleaseQueries(album)) {
    await musicBrainzDelay();

    const searchUrl = new URL("https://musicbrainz.org/ws/2/release/");
    searchUrl.searchParams.set("query", query);
    searchUrl.searchParams.set("fmt", "json");
    searchUrl.searchParams.set("limit", "15");

    const search = await fetchJson(searchUrl, { source: "musicbrainz" });
    releaseCandidates.push(
      ...(search.releases ?? []).map((candidate) => scoreMusicBrainzReleaseSearchCandidate(album, candidate)),
    );
    if (releaseCandidates.some((candidate) => candidate.match_score >= 84)) break;
  }

  releaseCandidates.sort((a, b) => b.match_score - a.match_score);
  const best = releaseCandidates[0];
  if (!best || !isAcceptableMusicBrainzMatch(album, best)) {
    return unresolvedResult("no_confident_release_group_match", bestReleaseGroupCandidate ?? best);
  }

  await musicBrainzDelay();

  const releaseUrl = new URL(`https://musicbrainz.org/ws/2/release/${best.id}`);
  releaseUrl.searchParams.set("inc", "media+recordings");
  releaseUrl.searchParams.set("fmt", "json");

  const release = await fetchJson(releaseUrl, { source: "musicbrainz" });
  const tracks = flattenMusicBrainzTracks(release);
  if (tracks.length === 0) {
    return unresolvedResult("matched_release_but_no_tracks", best);
  }

  return {
    resolution: {
      status: "resolved",
      selected_source: "musicbrainz_ws2",
      confidence: musicBrainzConfidence(best.match_score),
      match_score: best.match_score,
      selected_release_score: best.match_score,
      warnings: ["resolved_by_aggressive_release_search"],
    },
    catalog_match: {
      source: "musicbrainz_ws2",
      musicbrainz_release_group_id: best["release-group"]?.id ?? "",
      musicbrainz_release_id: release.id,
      artist_name: artistCreditName(best["artist-credit"]),
      collection_name: release.title ?? best.title ?? "",
      release_date: release.date ?? best.date ?? "",
      release_year: yearFromDate(release.date ?? best.date),
      track_count: tracks.length,
      country: release.country ?? best.country ?? "",
      primary_genre_name: "",
      collection_url: `https://musicbrainz.org/release/${release.id}`,
      artwork_url_100: null,
      copyright: "",
      release_status: release.status ?? best.status ?? "",
      release_format: (release.media ?? []).map((medium) => medium.format).filter(Boolean).join("; "),
    },
    tracks,
  };
}

function unresolvedResult(reason, bestCandidate) {
  return {
    resolution: {
      status: "unresolved",
      selected_source: null,
      confidence: "none",
      warnings: [reason],
      best_candidate_match_score: bestCandidate?.match_score ?? 0,
      best_candidate_name: bestCandidate?.collectionName ?? bestCandidate?.title ?? "",
      best_candidate_artist: bestCandidate?.artistName ?? artistCreditName(bestCandidate?.["artist-credit"]) ?? "",
    },
    catalog_match: null,
    tracks: [],
  };
}

function scoreAppleAlbum(album, candidate) {
  const targetTitle = normKey(album.title);
  const targetArtist = normKey(album.artist_display_name);
  const candidateTitle = normKey(candidate.collectionName);
  const candidateArtist = normKey(candidate.artistName);
  const candidateYear = yearFromDate(candidate.releaseDate);
  const targetYear = Number(album.year);
  const titleQuality = titleMatchQuality(album.title, candidate.collectionName);
  const yearDistance = releaseYearDistance(album, candidateYear);

  let score = 0;
  if (titleQuality.exact) score += 50;
  else if (titleQuality.compactExact) score += 46;
  else if (normalizedTitleContains(album.title, candidate.collectionName)) score += 34;
  else score += tokenOverlapScore(targetTitle, candidateTitle, 26);

  score += nameMatchScore(album.artist_display_name, candidate.artistName, 34, 24, 20);

  if (Number.isFinite(targetYear) && Number.isFinite(candidateYear)) {
    if (yearDistance === 0) score += 10;
    else if (yearDistance <= 1) score += 7;
    else if (yearDistance <= 3) score += 2;
    else if (yearDistance >= 15) score -= 10;
  }

  if ((candidate.trackCount ?? 0) > 0) score += 3;
  if (hasEditionNoise(candidate.collectionName) && !hasEditionNoise(album.title)) score -= 8;
  if ((titleQuality.exact || titleQuality.compactExact) && Number.isFinite(yearDistance) && yearDistance <= 1) {
    score += 12;
  }
  if (
    isCastOrSoundtrackSeed(album) &&
    candidateHasCastOrSoundtrackSignals(candidate) &&
    (titleQuality.overlapRatio >= 0.45 || castSeedTitleCompatible(album, candidate.collectionName))
  ) {
    score += 14;
  }
  if (isVariousArtistSeed(album) && (titleQuality.exact || titleQuality.compactExact) && Number.isFinite(yearDistance) && yearDistance <= 2) {
    score += 10;
  }

  return {
    ...candidate,
    match_score: Math.max(0, Math.round(score)),
  };
}

function isAcceptableAppleMatch(album, candidate) {
  if ((candidate.trackCount ?? 0) <= 0) return false;
  if (candidateHasWrongCastLocale(candidate, album)) return false;

  const titleQuality = titleMatchQuality(album.title, candidate.collectionName);
  const distance = releaseYearDistance(album, yearFromDate(candidate.releaseDate));
  const titleStrong = titleQuality.exact || titleQuality.compactExact || titleQuality.overlapRatio >= 0.68;
  const yearUsable = !Number.isFinite(distance) || distance <= 3;
  const artistOk = artistCompatible(album, candidate.artistName) || candidateArtistNamedBySeed(album, candidate.artistName);
  const castOrVariousOk =
    candidateHasCastOrSoundtrackSignals(candidate) &&
    (
      (isCastOrSoundtrackSeed(album) && (titleQuality.overlapRatio >= 0.55 || castSeedTitleCompatible(album, candidate.collectionName))) ||
      (isVariousArtistSeed(album) && (titleQuality.overlapRatio >= 0.55 || normalizedTitleContains(album.title, candidate.collectionName)))
    );

  if (!titleStrong || !yearUsable) return false;
  if ((candidate.match_score ?? 0) >= 74 && (artistOk || castOrVariousOk)) return true;

  if (
    (titleQuality.exact || titleQuality.compactExact) &&
    Number.isFinite(distance) &&
    distance <= 1 &&
    (artistOk || castOrVariousOk)
  ) {
    return true;
  }

  return (
    castOrVariousOk &&
    (!Number.isFinite(distance) || distance <= 3)
  );
}

function scoreMusicBrainzReleaseGroup(album, candidate) {
  const targetTitle = normKey(album.title);
  const targetArtist = normKey(album.artist_display_name);
  const candidateTitle = normKey(candidate.title);
  const candidateArtist = normKey(artistCreditName(candidate["artist-credit"]));
  const candidateYear = yearFromDate(candidate["first-release-date"]);
  const targetYear = Number(album.year);
  const titleQuality = titleMatchQuality(album.title, candidate.title);
  const yearDistance = releaseYearDistance(album, candidateYear);

  let score = Math.min(100, Number(candidate.score ?? 0)) * 0.4;
  if (titleQuality.exact) score += 34;
  else if (titleQuality.compactExact) score += 30;
  else if (normalizedTitleContains(album.title, candidate.title)) score += 22;
  else score += tokenOverlapScore(targetTitle, candidateTitle, 20);

  score += nameMatchScore(album.artist_display_name, artistCreditName(candidate["artist-credit"]), 22, 14, 14);

  if (candidate["primary-type"] === "Album") score += 5;
  if (candidate["secondary-types"]?.includes("Soundtrack")) score += 4;

  if (Number.isFinite(targetYear) && Number.isFinite(candidateYear)) {
    if (yearDistance === 0) score += 8;
    else if (yearDistance <= 1) score += 5;
    else if (yearDistance <= 3) score += 2;
    else if (yearDistance >= 15) score -= 8;
  }

  if (hasEditionNoise(candidate.title) && !hasEditionNoise(album.title)) score -= 6;
  if ((titleQuality.exact || titleQuality.compactExact) && Number.isFinite(yearDistance) && yearDistance <= 1) {
    score += 8;
  }
  if (
    isCastOrSoundtrackSeed(album) &&
    candidateHasCastOrSoundtrackSignals(candidate) &&
    (titleQuality.overlapRatio >= 0.45 || castSeedTitleCompatible(album, candidate.title))
  ) {
    score += 12;
  }

  return {
    ...candidate,
    match_score: Math.max(0, Math.round(score)),
  };
}

function scoreMusicBrainzReleaseSearchCandidate(album, candidate) {
  const targetTitle = normKey(album.title);
  const candidateTitle = normKey(candidate.title);
  const candidateArtistName = artistCreditName(candidate["artist-credit"]);
  const candidateYear = yearFromDate(candidate.date);
  const titleQuality = titleMatchQuality(album.title, candidate.title);
  const yearDistance = releaseYearDistance(album, candidateYear);
  const releaseGroup = candidate["release-group"] ?? {};

  let score = Math.min(100, Number(candidate.score ?? 0)) * 0.35;
  if (titleQuality.exact) score += 34;
  else if (titleQuality.compactExact) score += 30;
  else if (normalizedTitleContains(album.title, candidate.title)) score += 22;
  else score += tokenOverlapScore(targetTitle, candidateTitle, 20);

  score += nameMatchScore(album.artist_display_name, candidateArtistName, 22, 14, 14);

  if (releaseGroup["primary-type"] === "Album") score += 5;
  if (releaseGroup["secondary-types"]?.includes("Soundtrack")) score += 5;
  if (candidate.status === "Official") score += 5;
  if (candidate.country === "US") score += 4;
  if (candidate.country === "XW") score += 3;
  if ((candidate.media ?? []).some((medium) => medium.format === "Digital Media")) score += 3;
  if ((candidate.media ?? []).some((medium) => medium.format === "CD")) score += 2;

  if (Number.isFinite(yearDistance)) {
    if (yearDistance === 0) score += 8;
    else if (yearDistance <= 1) score += 5;
    else if (yearDistance <= 3) score += 2;
    else if (yearDistance >= 15) score -= 10;
  }

  if (hasEditionNoise(candidate.title) && !hasEditionNoise(album.title)) score -= 8;
  if ((titleQuality.exact || titleQuality.compactExact) && Number.isFinite(yearDistance) && yearDistance <= 1) {
    score += 8;
  }
  if (
    isCastOrSoundtrackSeed(album) &&
    candidateHasCastOrSoundtrackSignals(candidate) &&
    (titleQuality.overlapRatio >= 0.45 || castSeedTitleCompatible(album, candidate.title))
  ) {
    score += 12;
  }

  return {
    ...candidate,
    match_score: Math.max(0, Math.round(score)),
  };
}

function isAcceptableMusicBrainzMatch(album, candidate) {
  if (!candidate || (candidate.match_score ?? 0) < 72) return false;
  if (candidateHasWrongCastLocale(candidate, album)) return false;

  const titleQuality = titleMatchQuality(album.title, candidate.title);
  const candidateArtistName = artistCreditName(candidate["artist-credit"]);
  const artistScore = nameMatchScore(album.artist_display_name, candidateArtistName, 22, 14, 14);
  const candidateYear = yearFromDate(candidate["first-release-date"] ?? candidate.date);
  const distance = releaseYearDistance(album, candidateYear);
  const castTitleStrong =
    isCastOrSoundtrackSeed(album) &&
    candidateHasCastOrSoundtrackSignals(candidate) &&
    castSeedTitleCompatible(album, candidate.title);
  const titleStrong = titleQuality.exact || titleQuality.compactExact || titleQuality.overlapRatio >= 0.68 || castTitleStrong;
  const yearUsable = !Number.isFinite(distance) || distance <= 3;

  if (!titleStrong || !yearUsable) return false;
  if (artistScore >= 10 || artistCompatible(album, candidateArtistName) || candidateArtistNamedBySeed(album, candidateArtistName)) {
    return true;
  }
  if (
    isVariousArtistSeed(album) &&
    (titleQuality.exact || titleQuality.compactExact) &&
    candidateHasCastOrSoundtrackSignals(candidate)
  ) {
    return true;
  }
  if (isCastOrSoundtrackSeed(album) && candidateHasCastOrSoundtrackSignals(candidate)) return true;
  return false;
}

function chooseMusicBrainzRelease(releases, album) {
  const targetTitle = normKey(album.title);
  const targetYear = Number(album.year);
  const castKind = castSeedKind(album);

  return releases
    .filter((release) => flattenMusicBrainzTracks(release).length > 0)
    .filter((release) => !candidateHasWrongCastLocale(release, album))
    .map((release) => {
      const releaseTitle = normKey(release.title);
      const releaseYear = yearFromDate(release.date);
      const warnings = [];
      let score = 0;
      if (releaseTitle === targetTitle) score += 24;
      else if (normalizedTitleContains(album.title, release.title)) score += 6;
      else score += tokenOverlapScore(targetTitle, releaseTitle, 8);
      if (release.status === "Official") score += 10;
      if (release.country === "US") score += 8;
      if (release.country === "XW") score += 6;
      if (castKind === "broadway" && ["US", "XW"].includes(release.country)) score += 8;
      if (castKind === "london" && ["GB", "XW"].includes(release.country)) score += 8;
      if ((release.media ?? []).some((medium) => medium.format === "Digital Media")) score += 5;
      if ((release.media ?? []).some((medium) => medium.format === "CD")) score += 3;
      if (release.date) score += 2;
      if (castKind && releaseHasCastKind(release, castKind)) score += 34;
      else if (castKind && releaseHasCastSignals(release) && castSeedTitleCompatible(album, release.title)) score += 12;
      if (castKind && containsNonLatinScript(release.title) && !containsNonLatinScript(album.title)) {
        score -= 36;
        warnings.push("selected_release_title_non_latin_for_latin_seed");
      }
      if (castKind === "broadway" && release.country && !["US", "XW", "CA"].includes(release.country)) score -= 10;
      if (castKind === "london" && release.country && !["GB", "XW", "US"].includes(release.country)) score -= 10;
      if (hasEditionNoise(release.title) && !hasEditionNoise(album.title)) {
        score -= 18;
        warnings.push("selected_release_title_contains_edition_noise");
      }
      if (Number.isFinite(targetYear) && Number.isFinite(releaseYear)) {
        const distance = Math.abs(targetYear - releaseYear);
        if (distance === 0) score += 4;
        else if (distance <= 1) score += 2;
        else if (distance >= 10) {
          score -= 24;
          warnings.push("selected_release_year_far_from_seed_year");
        } else if (distance >= 5) {
          score -= 12;
          warnings.push("selected_release_year_drift_from_seed_year");
        }
      }
      return { release, score, warnings };
    })
    .sort((a, b) => b.score - a.score)[0] ?? null;
}

function flattenMusicBrainzTracks(release) {
  return (release.media ?? [])
    .flatMap((medium) =>
      (medium.tracks ?? []).map((track, index) => ({
        source: "musicbrainz_ws2",
        disc_number: medium.position ?? null,
        track_number: index + 1,
        title: track.title ?? track.recording?.title ?? "",
        artist_name: "",
        duration_ms: track.length ?? track.recording?.length ?? null,
        musicbrainz_track_id: track.id ?? null,
        musicbrainz_recording_id: track.recording?.id ?? null,
        explicitness: "",
        is_streamable: false,
      })),
    )
    .sort((a, b) => (a.disc_number - b.disc_number) || (a.track_number - b.track_number));
}

function normalizeAlbumTrackOrder(album) {
  if (album.resolution?.selected_source !== "musicbrainz_ws2") return album;

  const countersByDisc = new Map();
  const tracks = (album.tracks ?? []).map((track) => {
    const discNumber = Number(track.disc_number) > 0 ? Number(track.disc_number) : 1;
    const nextTrackNumber = (countersByDisc.get(discNumber) ?? 0) + 1;
    countersByDisc.set(discNumber, nextTrackNumber);
    return {
      ...track,
      disc_number: discNumber,
      track_number: nextTrackNumber,
    };
  });

  return {
    ...album,
    tracks,
  };
}

function isSuspiciousAppleResult(result) {
  const warnings = result.resolution?.warnings ?? [];
  return warnings.some((warning) =>
    [
      "collection_title_contains_edition_noise",
      "duplicate_base_track_titles_possible_expanded_package",
      "track_titles_contain_version_or_bonus_noise",
    ].includes(warning),
  );
}

function appleTracklistWarnings(album, collection, tracks) {
  const warnings = [];
  if (tracks.length < (collection.trackCount ?? 0)) {
    warnings.push("lookup_track_count_below_catalog_track_count");
  }
  if (hasEditionNoise(collection.collectionName) && !hasEditionNoise(album.title)) {
    warnings.push("collection_title_contains_edition_noise");
  }
  if (duplicateBaseTrackRatio(tracks.map((track) => track.title)) >= 0.18) {
    warnings.push("duplicate_base_track_titles_possible_expanded_package");
  }
  if (tracks.filter((track) => hasTrackVersionNoise(track.title)).length >= 3) {
    warnings.push("track_titles_contain_version_or_bonus_noise");
  }
  if (tracks.length >= 24 && !warnings.includes("duplicate_base_track_titles_possible_expanded_package")) {
    warnings.push("large_track_count_review_recommended");
  }
  return warnings;
}

async function musicBrainzDelay() {
  let releaseGate;
  const previousGate = musicBrainzGate;
  musicBrainzGate = new Promise((resolve) => {
    releaseGate = resolve;
  });

  await previousGate;
  const elapsed = Date.now() - lastMusicBrainzRequestAt;
  const wait = Math.max(0, 1100 - elapsed);
  if (wait > 0) await sleep(wait);
  lastMusicBrainzRequestAt = Date.now();
  releaseGate();
}

async function fetchJson(url, options = {}) {
  const maxAttempts = options.source === "apple" ? 2 : 4;
  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    try {
      if (options.source === "apple") await appleDelay();
      const response = await fetch(url, {
        headers: {
          "User-Agent": userAgent,
          "Accept": "application/json",
        },
        signal: AbortSignal.timeout(options.source === "musicbrainz" ? 30000 : 20000),
      });

      if (response.status === 403 || response.status === 429 || response.status >= 500) {
        if (attempt === maxAttempts) {
          throw new Error(`${options.source ?? "fetch"} ${response.status} ${response.statusText}`);
        }
        await sleep((response.status === 403 ? 2500 : 750) * attempt * attempt);
        continue;
      }

      if (!response.ok) {
        throw new Error(`${options.source ?? "fetch"} ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      if (attempt === maxAttempts) throw error;
      await sleep(500 * attempt * attempt);
    }
  }
  return {};
}

async function appleDelay() {
  let releaseGate;
  const previousGate = appleGate;
  appleGate = new Promise((resolve) => {
    releaseGate = resolve;
  });

  await previousGate;
  const elapsed = Date.now() - lastAppleRequestAt;
  const wait = Math.max(0, (args.aggressive ? 650 : 300) - elapsed);
  if (wait > 0) await sleep(wait);
  lastAppleRequestAt = Date.now();
  releaseGate();
}

async function runPool(items, concurrency, worker) {
  let nextIndex = 0;
  const workers = Array.from({ length: Math.min(concurrency, items.length) }, async () => {
    while (nextIndex < items.length) {
      const item = items[nextIndex];
      nextIndex += 1;
      await worker(item);
    }
  });
  await Promise.all(workers);
}

function buildArtifacts(albums) {
  const resolved = albums.filter((album) => album.resolution.status === "resolved");
  const unresolved = albums.filter((album) => album.resolution.status !== "resolved");
  const totalTracks = albums.reduce((sum, album) => sum + album.tracks.length, 0);
  const appleResolved = resolved.filter((album) => album.resolution.selected_source === "apple_itunes_search_api").length;
  const musicBrainzResolved = resolved.filter((album) => album.resolution.selected_source === "musicbrainz_ws2").length;

  const summary = {
    generated_on: generatedOn,
    version: sidecarVersion,
    source_seed_file: "data/canonical_graph/depth_hardening_v0_2/pass_d/album_sidecar_seed_albums_v1.json",
    source_album_membership_rows: seed.rows.length,
    source_unique_album_identity_rows: albumNodes.length,
    album_identity_rows_in_sidecar: albums.length,
    resolved_album_identity_rows: resolved.length,
    unresolved_album_identity_rows: unresolved.length,
    apple_resolved_album_identity_rows: appleResolved,
    musicbrainz_resolved_album_identity_rows: musicBrainzResolved,
    total_sidecar_tracks: totalTracks,
    average_tracks_per_resolved_album: resolved.length === 0 ? 0 : Number((totalTracks / resolved.length).toFixed(2)),
    source_policy: "Apple iTunes Search API is preferred for Apple-compatible collection/track IDs; MusicBrainz WS/2 is used as structured fallback for albums missing from Apple search.",
  };

  const sidecar = {
    metadata: summary,
    albums,
  };

  const albumResolutionRows = albums.map((album) => ({
    candidate_identity_key: album.candidate_identity_key,
    artist_display_name: album.artist_display_name,
    title: album.title,
    year: album.year,
    membership_count: album.membership_count,
    archetype_ids: album.archetype_ids,
    import_classes: album.import_classes,
    resolution_status: album.resolution.status,
    selected_source: album.resolution.selected_source ?? "",
    confidence: album.resolution.confidence ?? "",
    match_score: album.resolution.match_score ?? album.resolution.best_candidate_match_score ?? "",
    track_count: album.tracks.length,
    catalog_artist_name: album.catalog_match?.artist_name ?? "",
    catalog_collection_name: album.catalog_match?.collection_name ?? "",
    catalog_release_date: album.catalog_match?.release_date ?? "",
    apple_collection_id: album.catalog_match?.apple_collection_id ?? "",
    musicbrainz_release_group_id: album.catalog_match?.musicbrainz_release_group_id ?? "",
    musicbrainz_release_id: album.catalog_match?.musicbrainz_release_id ?? "",
    catalog_url: album.catalog_match?.collection_url ?? "",
    warnings: album.resolution.warnings ?? [],
  }));

  const trackRows = albums.flatMap((album) =>
    album.tracks.map((track, index) => ({
      candidate_identity_key: album.candidate_identity_key,
      artist_display_name: album.artist_display_name,
      album_title: album.title,
      album_year: album.year,
      membership_count: album.membership_count,
      archetype_ids: album.archetype_ids,
      selected_source: album.resolution.selected_source,
      apple_collection_id: album.catalog_match?.apple_collection_id ?? "",
      musicbrainz_release_id: album.catalog_match?.musicbrainz_release_id ?? "",
      sidecar_track_index: index + 1,
      disc_number: track.disc_number ?? "",
      track_number: track.track_number ?? "",
      track_title: track.title,
      track_artist_name: track.artist_name ?? "",
      duration_ms: track.duration_ms ?? "",
      apple_track_id: track.apple_track_id ?? "",
      musicbrainz_recording_id: track.musicbrainz_recording_id ?? "",
      track_url: track.apple_track_url ?? "",
      is_streamable: track.is_streamable,
    })),
  );

  return {
    summary,
    sidecar,
    albumResolutionRows,
    trackRows,
    unresolvedRows: albumResolutionRows.filter((row) => row.resolution_status !== "resolved"),
  };
}

function writeMarkdown(summary, unresolvedRows) {
  const bySource = [
    `- Apple resolved album identities: ${summary.apple_resolved_album_identity_rows}`,
    `- MusicBrainz fallback resolved album identities: ${summary.musicbrainz_resolved_album_identity_rows}`,
    `- Unresolved album identities: ${summary.unresolved_album_identity_rows}`,
    `- Total sidecar tracks: ${summary.total_sidecar_tracks}`,
  ].join("\n");

  const unresolvedPreview = unresolvedRows
    .slice(0, 30)
    .map((row) => `| ${row.artist_display_name} | ${row.title} | ${row.year} | ${row.warnings} |`)
    .join("\n");

  const markdown = `# Album Track Sidecar v1

Generated on ${summary.generated_on}.

## Scope

Built from \`${summary.source_seed_file}\`.

- Source album membership rows: ${summary.source_album_membership_rows}
- Unique album identity rows: ${summary.source_unique_album_identity_rows}
- Album identity rows in this sidecar: ${summary.album_identity_rows_in_sidecar}

## Resolution Summary

${bySource}

Source policy: ${summary.source_policy}

## Artifacts

- \`album_track_sidecar_v1.json\`: nested album nodes with memberships, catalog match, and track list.
- \`album_track_sidecar_album_resolution_v1.csv\`: one row per unique album identity and its resolution status.
- \`album_track_sidecar_tracks_v1.csv\`: one row per sidecar track for graph/song-depth expansion.
- \`album_track_sidecar_manifest_v1.md\`: this report.

## Unresolved Preview

${unresolvedRows.length === 0 ? "No unresolved album identities." : "| Artist | Album | Year | Warnings |\n| --- | --- | --- | --- |\n" + unresolvedPreview}
`;

  fs.writeFileSync(path.join(passD, "album_track_sidecar_manifest_v1.md"), markdown);
}

function writeCsv(file, rows) {
  fs.writeFileSync(path.join(passD, file), toCsv(rows));
}

function toCsv(rows) {
  if (rows.length === 0) return "";
  const columns = [...rows.reduce((set, row) => {
    Object.keys(row).forEach((key) => set.add(key));
    return set;
  }, new Set())];
  const lines = [
    columns.join(","),
    ...rows.map((row) => columns.map((column) => csvCell(row[column])).join(",")),
  ];
  return `${lines.join("\n")}\n`;
}

function csvCell(value) {
  const text = Array.isArray(value) ? value.join("; ") : String(value ?? "");
  return /[",\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
}

function artistCreditName(artistCredit) {
  if (!Array.isArray(artistCredit)) return "";
  return artistCredit
    .map((credit) => `${credit.name ?? ""}${credit.joinphrase ?? ""}`)
    .join("")
    .trim();
}

function appleSearchTerms(album) {
  if (!args.aggressive) return [`${album.artist_display_name} ${album.title}`.trim()];

  const titleVariants = albumTitleSearchVariants(album);
  const artistVariants = searchArtistVariants(album.artist_display_name);
  const castTerms = castOrSoundtrackSearchTerms(album);
  const terms = [];

  terms.push(`${album.artist_display_name} ${album.title}`);
  terms.push(`${album.title} ${album.artist_display_name}`);
  terms.push(...castTerms);
  if (Number.isFinite(Number(album.year))) terms.push(`${album.title} ${album.year}`);

  for (const title of titleVariants.slice(0, 6)) {
    terms.push(title);
    for (const artist of artistVariants.slice(0, 4)) {
      terms.push(`${artist} ${title}`);
      terms.push(`${title} ${artist}`);
    }
  }

  return uniqueStrings(terms).slice(0, 12);
}

function musicBrainzReleaseGroupQueries(album) {
  const titleVariants = args.aggressive ? albumTitleSearchVariants(album) : [album.title];
  const artistVariants = args.aggressive ? searchArtistVariants(album.artist_display_name) : musicBrainzArtistSearchVariants(album.artist_display_name);
  const castTerms = castOrSoundtrackSearchTerms(album);
  const queries = [];

  for (const term of castTerms) {
    queries.push(term);
    queries.push(`releasegroup:${queryPhrase(term)}`);
  }

  for (const title of titleVariants.slice(0, args.aggressive ? 6 : 1)) {
    for (const artist of artistVariants.slice(0, args.aggressive ? 5 : 3)) {
      queries.push(`releasegroup:${queryPhrase(title)} AND artist:${queryPhrase(artist)}`);
    }
  }

  if (args.aggressive) {
    for (const title of titleVariants.slice(0, 6)) {
      for (const artist of artistVariants.slice(0, 4)) {
        queries.push(`${title} ${artist} ${album.year ?? ""}`.trim());
      }
      queries.push(`releasegroup:${queryPhrase(title)}`);
      queries.push(`${title} ${album.year ?? ""}`.trim());
    }
  }

  return uniqueStrings(queries).slice(0, args.aggressive ? 14 : 6);
}

function musicBrainzReleaseQueries(album) {
  const titleVariants = albumTitleSearchVariants(album);
  const artistVariants = searchArtistVariants(album.artist_display_name);
  const castTerms = castOrSoundtrackSearchTerms(album);
  const queries = [];

  for (const term of castTerms) {
    queries.push(term);
    queries.push(`release:${queryPhrase(term)}`);
  }

  for (const title of titleVariants.slice(0, 6)) {
    for (const artist of artistVariants.slice(0, 5)) {
      queries.push(`release:${queryPhrase(title)} AND artist:${queryPhrase(artist)}`);
      queries.push(`${title} ${artist} ${album.year ?? ""}`.trim());
    }
    queries.push(`release:${queryPhrase(title)}`);
    if (Number.isFinite(Number(album.year))) queries.push(`${title} ${album.year}`);
  }

  return uniqueStrings(queries).slice(0, 14);
}

function musicBrainzArtistSearchVariants(value) {
  const text = String(value ?? "").trim();
  const variants = [
    text,
    text.replace(/(\d)\s+([A-Za-z])/g, "$1$2"),
    text.replace(/([A-Za-z])\s+(\d)/g, "$1$2"),
    text.replace(/\band\b/gi, "&"),
    text.replace(/&/g, "and"),
    text.replace(/\band\b/gi, "with"),
    text.replace(/\bPublic Image Ltd\b/i, "Public Image Limited"),
    text.replace(/\bPublic Image Ltd\b/i, "PiL"),
    text.replace(/\bRun-DMC\b/i, "Run-D.M.C."),
  ].filter(Boolean);
  return [...new Set(variants)];
}

function searchArtistVariants(value) {
  const text = String(value ?? "").trim();
  const variants = [
    ...musicBrainzArtistSearchVariants(text),
    text.replace(/^The\s+/i, ""),
    /^The\s+/i.test(text) ? text : `The ${text}`,
  ];

  const collaborationSplit = text.split(/\s+(?:and|with|&|\/|\+)\s+/i).map((part) => part.trim()).filter(Boolean);
  if (collaborationSplit.length > 1) {
    variants.push(...collaborationSplit);
    variants.push(collaborationSplit.join(" & "));
    variants.push(collaborationSplit.join(" with "));
  }

  variants.push(
    text.replace(/\b4\.40\b/g, "y 4.40"),
    text.replace(/\bHikaru Utada\b/i, "Utada Hikaru"),
    text.replace(/\bUtada Hikaru\b/i, "Hikaru Utada"),
  );

  return uniqueStrings(variants).filter(Boolean);
}

function albumTitleSearchVariants(album) {
  return uniqueStrings([
    ...searchTitleVariants(album.title),
    ...searchTitleVariants(seedTitleWithoutLeadingArtist(album)),
  ]);
}

function seedTitleWithoutLeadingArtist(album) {
  const title = String(album.title ?? "").trim();
  const artist = String(album.artist_display_name ?? "").trim();
  if (!title || !artist) return "";

  const direct = new RegExp(`^${escapeRegex(artist)}(?:'s|s)?\\s+`, "i");
  const stripped = title.replace(direct, "").trim();
  if (stripped !== title) return stripped;

  const titleTokens = normKey(title).split(" ").filter(Boolean);
  const artistTokens = normKey(artist).split(" ").filter(Boolean);
  const possessiveArtistTokens = [...artistTokens];
  if (possessiveArtistTokens.length > 0) {
    possessiveArtistTokens[possessiveArtistTokens.length - 1] = `${possessiveArtistTokens[possessiveArtistTokens.length - 1]}s`;
  }
  const startsWithArtist = artistTokens.every((token, index) => titleTokens[index] === token);
  const startsWithPossessiveArtist = possessiveArtistTokens.every((token, index) => titleTokens[index] === token);
  if (!startsWithArtist && !startsWithPossessiveArtist) return "";
  return titleTokens.slice(artistTokens.length).join(" ");
}

function searchTitleVariants(value) {
  const text = String(value ?? "").trim();
  const norm = normKey(text);
  const compact = compactKey(text);
  const stripped = text
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[\u2019\u2018`\u00b4]/g, "'")
    .replace(/[\u2022\u00b7]/g, ".")
    .replace(/[\u2010\u2011\u2012\u2013\u2014\u2015]/g, "-")
    .replace(/\s+/g, " ")
    .trim();

  const variants = [
    text,
    stripped,
    norm,
    compact,
    stripped.replace(/[.]/g, ""),
    stripped.replace(/[.]/g, " "),
    stripped.replace(/[\u2019\u2018'`\u00b4]/g, ""),
    stripped.replace(/&/g, "and"),
    stripped.replace(/\band\b/gi, "&"),
    stripped.replace(/\bYoure\b/i, "You're"),
    stripped.replace(/\bMans\b/i, "Man's"),
    spacedLetters(compact),
  ];

  const acronym = compact.match(/^[a-z0-9]{2,6}$/i) ? compact.split("").join(".") : "";
  if (acronym) {
    variants.push(acronym);
    variants.push(acronym.replace(/\./g, "\u2022"));
  }

  return uniqueStrings(variants)
    .map((variant) => variant.trim())
    .filter((variant) => variant.length > 0);
}

function castOrSoundtrackSearchTerms(album) {
  if (!isCastOrSoundtrackSeed(album)) return [];

  const artist = String(album.artist_display_name ?? "");
  const title = String(album.title ?? "").trim();
  const castArtistMatch = artist.match(/^Original\s+(?:Broadway|London|West End|Cast)?\s*Cast\s+(?:of|Recording\s+of)\s+(.+)$/i);
  const showFromArtist = castArtistMatch?.[1]?.trim() ?? "";
  const showTitle = showFromArtist && showFromArtist.length < 80 ? showFromArtist : title;
  const year = Number.isFinite(Number(album.year)) ? ` ${album.year}` : "";

  return uniqueStrings([
    `${showTitle} Original Broadway Cast Recording${year}`,
    `${showTitle} Original London Cast Recording${year}`,
    `${showTitle} Original Cast Recording${year}`,
    `${showTitle} Cast Recording${year}`,
    `${showTitle} soundtrack${year}`,
    `${title} Original Broadway Cast Recording${year}`,
    `${title} soundtrack${year}`,
  ]);
}

function queryPhrase(value) {
  return `"${String(value ?? "").replace(/\\/g, "\\\\").replace(/"/g, '\\"')}"`;
}

function escapeRegex(value) {
  return String(value ?? "").replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function dateOnly(value) {
  return String(value ?? "").slice(0, 10);
}

function yearFromDate(value) {
  const match = String(value ?? "").match(/^(\d{4})/);
  return match ? Number(match[1]) : Number.NaN;
}

function hasEditionNoise(value) {
  return /\b(deluxe|expanded|anniversary|remaster|remastered|special edition|bonus track|collector|legacy edition|super deluxe|instrumental|instrumentals|acapella|a cappella|karaoke|commentary|single)\b/i.test(String(value ?? ""));
}

function hasTrackVersionNoise(value) {
  return /\b(mono|stereo|demo|alternate|alternative|take \d+|version|mix|remix|remaster|remastered|bonus|live|instrumental|acapella|a cappella|karaoke)\b/i.test(String(value ?? ""));
}

function duplicateBaseTrackRatio(titles) {
  if (titles.length === 0) return 0;
  const counts = new Map();
  for (const title of titles) {
    const baseTitle = normKey(String(title ?? "").replace(/\s*[\[(].*?[\])]\s*/g, " "));
    if (!baseTitle) continue;
    counts.set(baseTitle, (counts.get(baseTitle) ?? 0) + 1);
  }
  const duplicateCount = [...counts.values()].reduce((sum, count) => sum + Math.max(0, count - 1), 0);
  return duplicateCount / titles.length;
}

function nameMatchScore(targetRaw, candidateRaw, exactPoints, containsPoints, overlapMax) {
  const target = normKey(targetRaw);
  const candidate = normKey(candidateRaw);
  if (target && candidate) {
    if (candidate === target) return exactPoints;
    if (candidate.includes(target) || target.includes(candidate)) return containsPoints;
    return tokenOverlapScore(target, candidate, overlapMax);
  }

  const rawTarget = rawComparableKey(targetRaw);
  const rawCandidate = rawComparableKey(candidateRaw);
  if (rawTarget && rawCandidate && rawTarget === rawCandidate) return exactPoints;
  return 0;
}

function artistCompatible(album, candidateArtistRaw) {
  const artistScore = nameMatchScore(album.artist_display_name, candidateArtistRaw, 22, 14, 14);
  if (artistScore >= 8) return true;

  const targetTokens = artistTokens(album.artist_display_name);
  const candidateTokens = artistTokens(candidateArtistRaw);
  if (targetTokens.length === 0 || candidateTokens.length === 0) return false;
  const candidateSet = new Set(candidateTokens);
  const overlap = targetTokens.filter((token) => candidateSet.has(token)).length;
  return overlap >= 2 && overlap / Math.max(targetTokens.length, candidateTokens.length) >= 0.5;
}

function candidateArtistNamedBySeed(album, candidateArtistRaw) {
  const candidateTokens = artistTokens(candidateArtistRaw);
  if (candidateTokens.length === 0 || candidateTokens.length > 4) return false;
  const seedTokens = new Set(artistTokens(`${album.artist_display_name ?? ""} ${album.title ?? ""}`));
  if (seedTokens.size === 0) return false;
  return candidateTokens.filter((token) => seedTokens.has(token)).length === candidateTokens.length;
}

function artistTokens(value) {
  return normKey(value)
    .split(" ")
    .filter((token) => token.length > 2 && !["and", "the", "with", "feat", "featuring", "various", "artists"].includes(token));
}

function rawComparableKey(value) {
  return String(value ?? "")
    .toLowerCase()
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

function titleMatchQuality(targetRaw, candidateRaw) {
  const target = normKey(targetRaw);
  const candidate = normKey(candidateRaw);
  const targetCompact = compactKey(targetRaw);
  const candidateCompact = compactKey(candidateRaw);
  const overlapRatio = tokenOverlapRatio(target, candidate);
  return {
    exact: Boolean(target && candidate && target === candidate),
    compactExact: Boolean(targetCompact && candidateCompact && targetCompact === candidateCompact),
    overlapRatio,
  };
}

function normalizedTitleContains(targetRaw, candidateRaw) {
  const target = normKey(targetRaw);
  const candidate = normKey(candidateRaw);
  if (!target || !candidate) return false;
  if (target === candidate) return true;

  const targetTokens = target.split(" ").filter(Boolean);
  const candidateTokens = candidate.split(" ").filter(Boolean);
  if (targetTokens.length === 1 || candidateTokens.length === 1) {
    return candidateTokens.includes(target) || targetTokens.includes(candidate);
  }

  return containsTokenPhrase(candidateTokens, targetTokens) || containsTokenPhrase(targetTokens, candidateTokens);
}

function castSeedTitleCompatible(album, candidateRaw) {
  const target = normKey(album.title);
  const candidate = normKey(candidateRaw);
  if (!target || !candidate) return false;
  if (target === candidate) return true;

  const targetTokens = target.split(" ").filter(Boolean);
  const candidateTokens = candidate.split(" ").filter(Boolean);
  if (targetTokens.length === 1) {
    if (candidateTokens[0] !== targetTokens[0]) return false;
    const next = candidateTokens[1] ?? "";
    return ["original", "broadway", "london", "cast", "musical", "the"].includes(next);
  }

  return containsTokenPhrase(candidateTokens, targetTokens);
}

function containsTokenPhrase(haystackTokens, needleTokens) {
  if (needleTokens.length === 0 || needleTokens.length > haystackTokens.length) return false;
  for (let index = 0; index <= haystackTokens.length - needleTokens.length; index += 1) {
    if (needleTokens.every((token, offset) => haystackTokens[index + offset] === token)) return true;
  }
  return false;
}

function releaseYearDistance(album, candidateYear) {
  const targetYear = Number(album.year);
  if (!Number.isFinite(targetYear) || !Number.isFinite(candidateYear)) return Number.NaN;
  return Math.abs(targetYear - candidateYear);
}

function compactKey(value) {
  return String(value ?? "")
    .toLowerCase()
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/&/g, "and")
    .replace(/\+/g, "and")
    .replace(/\b(feat|featuring|ft)\b\.?/g, "")
    .replace(/[^a-z0-9]+/g, "")
    .trim();
}

function normKey(value) {
  return String(value ?? "")
    .toLowerCase()
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/&/g, "and")
    .replace(/\+/g, " and ")
    .replace(/([a-z])([0-9])/g, "$1 $2")
    .replace(/([0-9])([a-z])/g, "$1 $2")
    .replace(/\b(feat|featuring|ft)\b\.?/g, " ")
    .replace(/[^a-z0-9]+/g, " ")
    .trim()
    .replace(/^the\s+/, "")
    .replace(/\s+/g, " ");
}

function tokenOverlapRatio(a, b) {
  const left = new Set(String(a ?? "").split(" ").filter(Boolean));
  const right = new Set(String(b ?? "").split(" ").filter(Boolean));
  if (left.size === 0 || right.size === 0) return 0;
  const overlap = [...left].filter((token) => right.has(token)).length;
  return overlap / Math.max(left.size, right.size);
}

function tokenOverlapScore(a, b, maximum) {
  const left = new Set(a.split(" ").filter(Boolean));
  const right = new Set(b.split(" ").filter(Boolean));
  if (left.size === 0 || right.size === 0) return 0;
  const overlap = [...left].filter((token) => right.has(token)).length;
  return Math.round(maximum * (overlap / Math.max(left.size, right.size)));
}

function isCastOrSoundtrackSeed(album) {
  const text = `${album.artist_display_name ?? ""} ${album.title ?? ""} ${(album.archetypes ?? []).join(" ")}`;
  return /\b(original\s+(broadway|london|west end)?\s*cast|cast recording|soundtrack|motion picture|musical|various artists)\b/i.test(text);
}

function isVariousArtistSeed(album) {
  return /\b(various artists|soundtrack|original cast|original broadway cast|original london cast)\b/i.test(
    `${album.artist_display_name ?? ""} ${album.title ?? ""}`,
  );
}

function isGenericTitleOnlySeed(album) {
  const title = normKey(album.title);
  return /^(hair|cats|six|chicago|company|rent|wicked|hamilton|frozen|encanto|grease|cabaret|carousel|oklahoma)$/.test(title);
}

function isManualReviewFastSkip(album) {
  const title = normKey(album.title);
  const artist = normKey(album.artist_display_name);
  if (/\b(golden hits|greatest hits|best of)\b/.test(title)) return true;
  if (artist === "lo fi girl" && title.includes("lofi hip hop radio")) return true;
  return false;
}

function castSeedKind(album) {
  const artist = normKey(album.artist_display_name);
  if (artist.includes("original broadway cast")) return "broadway";
  if (artist.includes("original london cast") || artist.includes("original west end cast")) return "london";
  return "";
}

function releaseHasCastKind(release, kind) {
  const text = normKey([
    release.title,
    artistCreditName(release["artist-credit"]),
    release.disambiguation,
    ...(release.media ?? []).map((medium) => medium.title),
  ].filter(Boolean).join(" "));
  if (!text.includes("cast")) return false;
  if (kind === "broadway") return text.includes("broadway");
  if (kind === "london") return text.includes("london") || text.includes("west end");
  return false;
}

function releaseHasCastSignals(release) {
  const text = normKey([
    release.title,
    artistCreditName(release["artist-credit"]),
    release.disambiguation,
    ...(release.media ?? []).map((medium) => medium.title),
  ].filter(Boolean).join(" "));
  return /\b(original|cast|broadway|london|west end|musical)\b/.test(text);
}

function candidateHasCastOrSoundtrackSignals(candidate) {
  const text = [
    candidate.collectionName,
    candidate.artistName,
    candidate.primaryGenreName,
    candidate.copyright,
    candidate.title,
    artistCreditName(candidate["artist-credit"]),
    candidate["primary-type"],
    ...(candidate["secondary-types"] ?? []),
    candidate["release-group"]?.title,
    candidate["release-group"]?.["primary-type"],
    ...(candidate["release-group"]?.["secondary-types"] ?? []),
  ].filter(Boolean).join(" ");
  return /\b(cast|soundtrack|broadway|london|west end|musical|motion picture|film|stage|theatre|theater|various artists)\b/i.test(text);
}

function candidateHasWrongCastLocale(candidate, album) {
  const kind = castSeedKind(album);
  if (!kind) return false;

  const text = normKey([
    candidate.collectionName,
    candidate.artistName,
    candidate.title,
    candidate.disambiguation,
    artistCreditName(candidate["artist-credit"]),
    candidate["release-group"]?.title,
    candidate["release-group"]?.disambiguation,
  ].filter(Boolean).join(" "));

  if (containsNonLatinScript(candidate.collectionName ?? candidate.title ?? "") && !containsNonLatinScript(album.title)) return true;

  const hasRequiredKind = kind === "broadway"
    ? text.includes("broadway")
    : text.includes("london") || text.includes("west end");
  if (hasRequiredKind) return false;

  if (kind === "broadway") {
    return /\b(japanese|japan|london|west end|german|deutsch|dutch|spanish|italian|french|paris|mexican|australian|vienna|wien|swedish|korean|revival|tour|movie|film)\b/.test(text);
  }
  return /\b(japanese|japan|broadway|german|deutsch|dutch|spanish|italian|french|paris|mexican|australian|vienna|wien|swedish|korean|revival|tour|movie|film)\b/.test(text);
}

function containsNonLatinScript(value) {
  const stripped = String(value ?? "")
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "");
  return /[^\x00-\x7F]/.test(stripped);
}

function uniqueStrings(values) {
  const seen = new Set();
  const result = [];
  for (const value of values) {
    const text = String(value ?? "").replace(/\s+/g, " ").trim();
    if (!text) continue;
    const key = rawComparableKey(text);
    if (seen.has(key)) continue;
    seen.add(key);
    result.push(text);
  }
  return result;
}

function spacedLetters(value) {
  const text = String(value ?? "").replace(/[^a-z0-9]/gi, "");
  if (text.length < 2 || text.length > 16) return "";
  return text.split("").join(" ");
}

function appleConfidence(score) {
  if (score >= 94) return "high";
  if (score >= 82) return "medium";
  return "low";
}

function musicBrainzConfidence(score) {
  if (score >= 92) return "high";
  if (score >= 80) return "medium";
  return "low";
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
