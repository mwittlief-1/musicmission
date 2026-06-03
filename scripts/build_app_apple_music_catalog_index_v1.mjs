#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

const repoRoot = process.cwd();
const currentRoot = path.join(repoRoot, "data/canonical_graph/current");
const resourcesRoot = path.join(repoRoot, "MusicAtlasController/Resources");
const outputPath = path.join(resourcesRoot, "canonical_apple_music_catalog_index_v1.json");
const manifestPath = path.join(currentRoot, "app_apple_music_catalog_index_v1_manifest.md");
const generatedAt = new Date().toISOString();
const runVersion = "canonical_apple_music_catalog_index_v1";
const args = parseArgs(process.argv.slice(2));

const graph = readJson(path.join(currentRoot, "graph_linking_node_set.json")).rows ?? [];
const sidecar = readJson(path.join(currentRoot, "album_track_sidecar.json"));
const appArtists = readJson(path.join(resourcesRoot, "canonical_artists.json"));
const appAlbums = readJson(path.join(resourcesRoot, "canonical_albums.json"));
const appSongs = readJson(path.join(resourcesRoot, "canonical_song_recordings.json"));
const compactPool = readJson(path.join(resourcesRoot, "alpha_compact_candidate_pool_alpha_v0.json"));
const alphaBlocklist = readJson(path.join(resourcesRoot, "alpha_candidate_blocklist_alpha_v0.json")).blocklist ?? [];

const graphBySourceRef = new Map(graph.map((row) => [row.candidate_identity_key, row]));
const appArtistIDsByName = buildAppArtistIDsByName(appArtists);
const appSongIDsByIdentity = buildAppIDsByIdentity(appSongs, "canonical_song_recording_id", "display_name");
const appAlbumIDsByIdentity = buildAppIDsByIdentity(appAlbums, "canonical_album_id", "display_name");
const compactPoolRefsByCanonicalID = buildCompactPoolRefs(compactPool);
const blockedCatalogRefs = buildBlockedCatalogRefs(alphaBlocklist);
const acceptedLinks = readAcceptedAppleLinks();
const bestGraphArtistLinks = bestLinksBySourceRef(acceptedLinks.filter((link) =>
  link.source_type === "graph_artist_anchor"
  && link.apple_resource_type === "artist"
));
const bestGraphLinks = bestLinksBySourceRef(acceptedLinks.filter((link) =>
  ["graph_song", "graph_recording"].includes(link.source_type)
  && link.apple_resource_type === "song"
));
const bestGraphAlbumLinks = bestLinksBySourceRef(acceptedLinks.filter((link) =>
  link.source_type === "graph_album"
  && link.apple_resource_type === "album"
));

const entries = [
  ...buildGraphArtistEntries(bestGraphArtistLinks),
  ...buildGraphTrackEntries(bestGraphLinks),
  ...buildGraphAlbumEntries(bestGraphAlbumLinks),
  ...buildSidecarAlbumPlayableEntries(bestGraphAlbumLinks),
  ...(args.includeSidecarTracks ? buildSidecarTrackEntries() : []),
]
  .filter((entry) => !isBlockedEntry(entry))
  .filter((entry) => entry.apple_catalog_id && entry.match_keys.length > 0)
  .sort((left, right) => {
    if (right.priority !== left.priority) return right.priority - left.priority;
    return left.entry_id.localeCompare(right.entry_id);
  });

const output = {
  artifact: runVersion,
  version: "v1",
  generated_at: generatedAt,
  source_policy: {
    raw_apple_payloads_persisted: false,
    persisted_apple_fields: ["apple_catalog_id", "storefront", "apple_catalog_url"],
    excluded_persistent_fields: ["artwork", "previews", "lyrics", "music_user_token", "raw_catalog_payload", "music_video_ids"],
    usage: "App-side Apple Music resolver index. Live MusicKit search remains a fallback only when no accepted canonical/sidecar ID matches."
  },
  counts: {
    entries_total: entries.length,
    artist_entries: entries.filter((entry) => entry.item_type === "artist").length,
    track_entries: entries.filter((entry) => entry.item_type === "track").length,
    album_entries: entries.filter((entry) => entry.item_type === "album").length,
    graph_artist_entries: entries.filter((entry) => entry.source_type === "graph_artist_anchor").length,
    graph_song_recording_entries: entries.filter((entry) => ["graph_song", "graph_recording"].includes(entry.source_type)).length,
    graph_album_entries: entries.filter((entry) => entry.source_type === "graph_album").length,
    sidecar_album_entries: entries.filter((entry) => entry.source_type === "album_sidecar_album").length,
    sidecar_track_entries: entries.filter((entry) => entry.source_type === "album_sidecar_track").length,
    unique_apple_catalog_ids: new Set(entries.map((entry) => String(entry.apple_catalog_id))).size,
  },
  entries,
};

writeJson(outputPath, output);
writeManifest(output);
console.log(JSON.stringify(output.counts, null, 2));

function buildGraphArtistEntries(linkMap) {
  const output = [];
  for (const link of linkMap.values()) {
    const graphRow = graphBySourceRef.get(link.source_ref);
    if (!graphRow) continue;
    const artist = graphRow.artist_display_name || graphRow.title || artistNameFromAnchorRef(link.source_ref);
    if (!artist) continue;
    const appArtistIDs = appArtistIDsByName.get(normalizedIdentityPart(artist)) ?? [];
    const matchKeys = commonMatchKeys({
      itemType: "artist",
      sourceType: link.source_type,
      sourceRef: link.source_ref,
      artist,
      title: artist,
      canonicalObjectType: "artist",
      canonicalIDs: appArtistIDs,
    });

    output.push(compactEntry({
      entryID: `${link.source_type}:${link.source_ref}`,
      sourceType: link.source_type,
      sourceRef: link.source_ref,
      itemType: "artist",
      appleResourceType: "artist",
      appleCatalogID: link.apple_catalog_id,
      appleAlbumID: "",
      appleCatalogURL: appleArtistURL(link.apple_catalog_id),
      storefront: link.storefront ?? "us",
      resolvedTitle: artist,
      resolvedArtist: artist,
      resolvedAlbum: "",
      confidence: confidenceScore(link),
      matchStatus: link.match_status,
      matchBasis: link.match_basis,
      matchKeys,
      priority: priorityForLink(link, 820),
    }));
  }
  return output;
}

function buildGraphTrackEntries(linkMap) {
  const output = [];
  for (const link of linkMap.values()) {
    const graphRow = graphBySourceRef.get(link.source_ref);
    if (!graphRow) continue;
    const artist = graphRow.artist_display_name ?? "";
    const title = graphRow.title ?? "";
    const appSongIDs = appSongIDsByIdentity.get(identityKey(artist, title)) ?? [];
    const matchKeys = commonMatchKeys({
      itemType: "track",
      sourceType: link.source_type,
      sourceRef: link.source_ref,
      artist,
      title,
      canonicalObjectType: "song_recording",
      canonicalIDs: appSongIDs,
    });

    output.push(compactEntry({
      entryID: `${link.source_type}:${link.source_ref}`,
      sourceType: link.source_type,
      sourceRef: link.source_ref,
      itemType: "track",
      appleCatalogID: link.apple_catalog_id,
      appleAlbumID: link.album_apple_catalog_id ?? link.apple_album_id ?? "",
      appleCatalogURL: appleSongURL(link.apple_catalog_id, link.album_apple_catalog_id ?? link.apple_album_id),
      storefront: link.storefront ?? "us",
      resolvedTitle: title,
      resolvedArtist: artist,
      resolvedAlbum: "",
      confidence: confidenceScore(link),
      matchStatus: link.match_status,
      matchBasis: link.match_basis,
      matchKeys,
      priority: priorityForLink(link, 900),
    }));
  }
  return output;
}

function buildGraphAlbumEntries(linkMap) {
  const output = [];
  for (const link of linkMap.values()) {
    const graphRow = graphBySourceRef.get(link.source_ref);
    if (!graphRow) continue;
    const artist = graphRow.artist_display_name ?? "";
    const title = graphRow.title ?? "";
    const sidecarAlbum = sidecarAlbumByAppleID(link.apple_catalog_id);
    const firstTrack = firstPlayableTrack(sidecarAlbum);
    if (!firstTrack?.apple_track_id) continue;
    const appAlbumIDs = appAlbumIDsByIdentity.get(identityKey(artist, title)) ?? [];
    const matchKeys = commonMatchKeys({
      itemType: "album",
      sourceType: link.source_type,
      sourceRef: link.source_ref,
      artist,
      title,
      canonicalObjectType: "album",
      canonicalIDs: appAlbumIDs,
    });

    output.push(compactEntry({
      entryID: `graph_album_playable:${link.source_ref}`,
      sourceType: "graph_album",
      sourceRef: link.source_ref,
      itemType: "album",
      appleCatalogID: firstTrack.apple_track_id,
      appleAlbumID: link.apple_catalog_id,
      appleCatalogURL: firstTrack.apple_track_url ?? appleSongURL(firstTrack.apple_track_id, link.apple_catalog_id),
      storefront: link.storefront ?? "us",
      resolvedTitle: "",
      resolvedArtist: artist,
      resolvedAlbum: title,
      confidence: confidenceScore(link),
      matchStatus: link.match_status,
      matchBasis: `${link.match_basis}:first_song_track_for_album_playback`,
      matchKeys,
      priority: priorityForLink(link, 760),
    }));
  }
  return output;
}

function buildSidecarAlbumPlayableEntries(graphAlbumLinks) {
  const graphAlbumSourceRefs = new Set([...graphAlbumLinks.keys()]);
  const output = [];
  for (const album of sidecar.albums ?? []) {
    if (graphAlbumSourceRefs.has(album.candidate_identity_key)) continue;
    const appleAlbumID = clean(album.catalog_match?.apple_collection_id);
    if (!appleAlbumID) continue;
    const firstTrack = firstPlayableTrack(album);
    if (!firstTrack?.apple_track_id) continue;
    const artist = album.artist_display_name ?? "";
    const title = album.title ?? "";
    const appAlbumIDs = appAlbumIDsByIdentity.get(identityKey(artist, title)) ?? [];
    const matchKeys = commonMatchKeys({
      itemType: "album",
      sourceType: "album_sidecar_album",
      sourceRef: album.candidate_identity_key,
      artist,
      title,
      canonicalObjectType: "album",
      canonicalIDs: appAlbumIDs,
    });

    output.push(compactEntry({
      entryID: `album_sidecar_album_playable:${album.candidate_identity_key}`,
      sourceType: "album_sidecar_album",
      sourceRef: album.candidate_identity_key,
      itemType: "album",
      appleCatalogID: firstTrack.apple_track_id,
      appleAlbumID,
      appleCatalogURL: firstTrack.apple_track_url ?? appleSongURL(firstTrack.apple_track_id, appleAlbumID),
      storefront: "us",
      resolvedTitle: "",
      resolvedArtist: artist,
      resolvedAlbum: title,
      confidence: 0.88,
      matchStatus: "candidate_verified",
      matchBasis: "apple_tracklist_authority_first_song_track_for_album_playback",
      matchKeys,
      priority: 680,
    }));
  }
  return output;
}

function buildSidecarTrackEntries() {
  const output = [];
  for (const album of sidecar.albums ?? []) {
    const appleAlbumID = clean(album.catalog_match?.apple_collection_id);
    if (!appleAlbumID) continue;
    for (const track of album.tracks ?? []) {
      if (!track.apple_track_id) continue;
      const artist = track.artist_name || album.artist_display_name || "";
      const title = track.title ?? "";
      const sourceRef = sidecarTrackSourceRef(album, track);
      const matchKeys = commonMatchKeys({
        itemType: "track",
        sourceType: "album_sidecar_track",
        sourceRef,
        artist,
        title,
        canonicalObjectType: "song_recording",
        canonicalIDs: [],
      });

      output.push(compactEntry({
        entryID: `album_sidecar_track:${sourceRef}`,
        sourceType: "album_sidecar_track",
        sourceRef,
        itemType: "track",
        appleCatalogID: track.apple_track_id,
        appleAlbumID,
        appleCatalogURL: track.apple_track_url ?? appleSongURL(track.apple_track_id, appleAlbumID),
        storefront: "us",
        resolvedTitle: "",
        resolvedArtist: "",
        resolvedAlbum: "",
        confidence: 0.78,
        matchStatus: "candidate_verified",
        matchBasis: "apple_tracklist_authority_sidecar_song_track",
        matchKeys,
        priority: 420,
      }));
    }
  }
  return output;
}

function commonMatchKeys({
  itemType,
  sourceType,
  sourceRef,
  artist,
  title,
  canonicalObjectType,
  canonicalIDs,
}) {
  const routeType = itemType === "album" ? "album" : itemType === "artist" ? "artist" : "track";
  const keys = [
    `source_ref:${sourceRef}`,
    `source_ref:${sourceType}:${sourceRef}`,
    `route_display_identity_key:${routeIdentity(routeType, artist, title)}`,
    `normalized_identity:${routeIdentity(routeType, artist, title)}`,
  ];
  for (const canonicalID of canonicalIDs) {
    keys.push(`canonical_entity_id:${canonicalID}`);
    keys.push(`route_candidate_key:route:${routeType}:${canonicalObjectType}:${canonicalID}`);
    keys.push(`route_batch_dedupe_key:${canonicalObjectType}:${canonicalID}`);
    const compactRefs = compactPoolRefsByCanonicalID.get(canonicalID) ?? [];
    for (const ref of compactRefs) {
      keys.push(...ref.matchKeys);
    }
  }
  return [...new Set(keys.filter(Boolean))].sort();
}

function compactEntry({
  entryID,
  sourceType,
  sourceRef,
  itemType,
  appleResourceType,
  appleCatalogID,
  appleAlbumID,
  appleCatalogURL,
  storefront,
  resolvedTitle,
  resolvedArtist,
  resolvedAlbum,
  confidence,
  matchStatus,
  matchBasis,
  matchKeys,
  priority,
}) {
  return {
    entry_id: entryID,
    source_type: sourceType,
    source_ref: sourceRef,
    item_type: itemType,
    apple_catalog_id: String(appleCatalogID),
    apple_resource_type: appleResourceType || "song",
    apple_album_id: clean(appleAlbumID),
    apple_catalog_url: clean(appleCatalogURL),
    storefront: storefront || "us",
    resolved_title: clean(resolvedTitle),
    resolved_artist: clean(resolvedArtist),
    resolved_album: clean(resolvedAlbum),
    confidence,
    match_status: matchStatus || "candidate_verified",
    match_basis: matchBasis || "",
    priority,
    match_keys: [...new Set(matchKeys)].sort(),
  };
}

function buildBlockedCatalogRefs(blocklist) {
  const canonicalIDs = new Set();
  const typedRefs = new Set();
  const sourceRefs = new Set();

  for (const row of blocklist ?? []) {
    if (row.canonical_entity_id) canonicalIDs.add(String(row.canonical_entity_id));
    if (row.entity_ref) typedRefs.add(String(row.entity_ref));
    const sourceRef = legacySourceRefFromBlocklistRow(row);
    if (sourceRef) sourceRefs.add(sourceRef);
  }

  return { canonicalIDs, typedRefs, sourceRefs };
}

function legacySourceRefFromBlocklistRow(row) {
  if (!row || !row.object_type || !row.canonical_entity_id) return "";
  const parts = String(row.canonical_entity_id).split("-");
  if (parts.length < 2) return "";
  const title = parts.pop();
  const artist = parts.join(" ");
  return `${row.object_type}|${artist}|${title}`;
}

function isBlockedEntry(entry) {
  if (blockedCatalogRefs.sourceRefs.has(entry.source_ref)) return true;
  for (const canonicalID of blockedCatalogRefs.canonicalIDs) {
    if ((entry.match_keys ?? []).includes(`canonical_entity_id:${canonicalID}`)) return true;
  }
  for (const typedRef of blockedCatalogRefs.typedRefs) {
    const [type, canonicalID] = typedRef.split(":");
    if (!type || !canonicalID) continue;
    if ((entry.match_keys ?? []).includes(`route_batch_dedupe_key:${type}:${canonicalID}`)) return true;
    if ((entry.match_keys ?? []).includes(`route_candidate_key:route:${entry.item_type}:${type}:${canonicalID}`)) {
      return true;
    }
  }
  return false;
}

function readAcceptedAppleLinks() {
  const relativePaths = [
    "apple_music_link_pass_v1/apple_music_links_v1.jsonl",
    "apple_music_try_harder_pass_v1/apple_music_try_harder_links_v1.jsonl",
    "apple_music_residual_track_pass_v1/apple_music_residual_track_links_v1.jsonl",
    "apple_music_album_variant_pass_v1/apple_music_album_variant_links_v1.jsonl",
    "apple_music_offline_reconciliation_pass_v1/apple_music_offline_reconciliation_links_v1.jsonl",
    "apple_music_artist_album_resolver_pass_v1/apple_music_artist_album_resolver_links_v1.jsonl",
    "apple_music_high_confidence_album_pass_v1/apple_music_high_confidence_album_links_v1.jsonl",
    "apple_music_manual_album_review_pass_v1/apple_music_manual_album_review_links_v1.jsonl",
    "apple_music_semantic_album_hardening_pass_v1/apple_music_semantic_album_hardening_links_v1.jsonl",
    "apple_music_album_graph_decision_pass_v1/apple_music_album_graph_decision_links_v1.jsonl",
    "apple_music_song_source_album_reconciliation_pass_v1/apple_music_song_source_album_reconciliation_links_v1.jsonl",
    "apple_music_direct_song_hardening_pass_v1/apple_music_direct_song_hardening_links_v1.jsonl",
    "apple_music_direct_song_hardening_pass_v2/apple_music_direct_song_hardening_v2_links.jsonl",
    "apple_music_recording_hardening_pass_v1/apple_music_recording_hardening_links_v1.jsonl",
    "apple_music_graph_song_iterative_hardening_pass_v1/apple_music_graph_song_iterative_hardening_links_v1.jsonl",
    "apple_music_family10_missing_obvious_hotfix_v1/apple_music_family10_missing_obvious_hotfix_links_v1.jsonl",
  ];
  return relativePaths
    .flatMap((relativePath) => safeReadJsonl(path.join(currentRoot, relativePath)))
    .filter((link) => ["verified", "candidate_verified"].includes(link.match_status));
}

function parseArgs(argv) {
  const parsed = {
    includeSidecarTracks: false,
  };
  for (const arg of argv) {
    if (arg === "--include-sidecar-tracks") parsed.includeSidecarTracks = true;
  }
  return parsed;
}

function bestLinksBySourceRef(links) {
  const byRef = new Map();
  for (const link of links) {
    const prior = byRef.get(link.source_ref);
    if (!prior || priorityForLink(link, 0) > priorityForLink(prior, 0)) {
      byRef.set(link.source_ref, link);
    }
  }
  return byRef;
}

function priorityForLink(link, base) {
  let score = base;
  if (link.match_status === "verified") score += 100;
  if (link.confidence === "high") score += 40;
  if (link.confidence === "medium") score += 20;
  if (link.source_type === "graph_artist_anchor") score += 25;
  if (link.source_type === "graph_song" || link.source_type === "graph_recording") score += 30;
  if (link.source_type === "graph_album") score += 10;
  if (String(link.run_version ?? "").includes("manual")) score += 8;
  return score;
}

function confidenceScore(link) {
  if (link.confidence === "high") return 0.95;
  if (link.confidence === "medium") return 0.86;
  return link.match_status === "verified" ? 0.90 : 0.78;
}

function buildAppIDsByIdentity(rows, idField, titleField) {
  const byIdentity = new Map();
  for (const row of rows) {
    const id = row[idField];
    const title = row[titleField];
    const artists = row.artist_names?.length ? row.artist_names : [""];
    if (!id || !title) continue;
    for (const artist of artists) {
      const key = identityKey(artist, title);
      const ids = byIdentity.get(key) ?? [];
      ids.push(id);
      byIdentity.set(key, ids);
    }
  }
  return byIdentity;
}

function buildAppArtistIDsByName(rows) {
  const byName = new Map();
  for (const row of rows) {
    const id = row.canonical_artist_id;
    const name = row.display_name;
    if (!id || !name) continue;
    const key = normalizedIdentityPart(name);
    const ids = byName.get(key) ?? [];
    ids.push(id);
    byName.set(key, ids);
  }
  return byName;
}

function buildCompactPoolRefs(pool) {
  const byCanonicalID = new Map();
  for (const rows of Object.values(pool.pools ?? {})) {
    for (const row of rows ?? []) {
      const canonicalID = row.canonical_entity_id;
      if (!canonicalID) continue;
      const matchKeys = [
        row.candidate_id ? `candidate_id:${row.candidate_id}` : "",
        row.app_route_item_id ? `candidate_id:${row.app_route_item_id}` : "",
        row.route_candidate_key ? `route_candidate_key:${row.route_candidate_key}` : "",
        row.route_batch_dedupe_key ? `route_batch_dedupe_key:${row.route_batch_dedupe_key}` : "",
        row.route_display_identity_key ? `route_display_identity_key:${row.route_display_identity_key}` : "",
      ].filter(Boolean);
      const refs = byCanonicalID.get(canonicalID) ?? [];
      refs.push({ matchKeys });
      byCanonicalID.set(canonicalID, refs);
    }
  }
  return byCanonicalID;
}

function sidecarAlbumByAppleID(appleAlbumID) {
  const target = clean(appleAlbumID);
  return (sidecar.albums ?? []).find((album) => clean(album.catalog_match?.apple_collection_id) === target);
}

function firstPlayableTrack(album) {
  return (album?.tracks ?? []).find((track) => clean(track.apple_track_id));
}

function sidecarTrackSourceRef(album, track) {
  return [
    album.candidate_identity_key,
    track.disc_number ?? "",
    track.track_number ?? "",
    normalizeLegacySourceRefSegment(track.artist_name),
    normalizeLegacySourceRefSegment(track.title),
  ].join("@@");
}

function identityKey(artist, title) {
  return `${normalizedIdentityPart(artist)}::${normalizedIdentityPart(title)}`;
}

function routeIdentity(routeType, artist, title) {
  return [routeType, artist, title].map(normalizedIdentityPart).join(":");
}

function appleArtistURL(artistID) {
  return `https://music.apple.com/us/artist/${artistID}`;
}

function appleSongURL(songID, albumID) {
  if (albumID) return `https://music.apple.com/us/album/${albumID}?i=${songID}`;
  return `https://music.apple.com/us/song/${songID}`;
}

function artistNameFromAnchorRef(sourceRef) {
  const parts = String(sourceRef ?? "").split("|");
  return parts.length >= 2 ? parts[1] : "";
}

function normalizedIdentityPart(value) {
  return String(value ?? "")
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/&/g, " and ")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
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

function clean(value) {
  if (value === undefined || value === null) return "";
  return String(value).trim();
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function safeReadJsonl(file) {
  if (!fs.existsSync(file)) return [];
  const text = fs.readFileSync(file, "utf8").trim();
  if (!text) return [];
  return text.split("\n").filter(Boolean).map((line) => JSON.parse(line));
}

function writeJson(file, value) {
  fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`);
}

function writeManifest(payload) {
  const text = `# App Apple Music Catalog Index v1

Generated: ${payload.generated_at}

Status: \`complete\`

## Policy

- Raw Apple payloads persisted: \`false\`
- Music video IDs persisted: \`false\`
- Artwork, previews, lyrics, raw Apple payloads, and user tokens are not included.
- The app resolver uses this file before MusicKit catalog search.
- Full sidecar track expansion is intentionally excluded unless \`--include-sidecar-tracks\` is passed.

## Counts

| Metric | Count |
| --- | ---: |
| Entries total | ${payload.counts.entries_total} |
| Artist entries | ${payload.counts.artist_entries} |
| Track entries | ${payload.counts.track_entries} |
| Album entries | ${payload.counts.album_entries} |
| Graph artist entries | ${payload.counts.graph_artist_entries} |
| Graph song/recording entries | ${payload.counts.graph_song_recording_entries} |
| Graph album entries | ${payload.counts.graph_album_entries} |
| Sidecar album entries | ${payload.counts.sidecar_album_entries} |
| Sidecar track entries | ${payload.counts.sidecar_track_entries} |
| Unique Apple catalog IDs | ${payload.counts.unique_apple_catalog_ids} |

## App Artifact

- \`MusicAtlasController/Resources/canonical_apple_music_catalog_index_v1.json\`
`;
  fs.writeFileSync(manifestPath, text);
}
