#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

const repoRoot = process.cwd();
const currentRoot = path.join(repoRoot, "data/canonical_graph/current");
const artistOutputRoot = path.join(currentRoot, "apple_music_artist_manual_resolution_pass_v1");
const generatedAt = new Date().toISOString();
const storefront = "us";

fs.mkdirSync(artistOutputRoot, { recursive: true });

const artistLinksPath = path.join(artistOutputRoot, "apple_music_artist_manual_resolution_links_v1.jsonl");
const artistStatusPath = path.join(artistOutputRoot, "apple_music_artist_manual_resolution_status_v1.json");
const artistStatusCsvPath = path.join(artistOutputRoot, "apple_music_artist_manual_resolution_status_v1.csv");
const artistSplitNodesPath = path.join(artistOutputRoot, "apple_music_artist_split_nodes_v1.json");
const artistSummaryPath = path.join(artistOutputRoot, "apple_music_artist_manual_resolution_summary.json");
const artistManifestPath = path.join(artistOutputRoot, "apple_music_artist_manual_resolution_manifest.md");

const albumReplacementJsonPath = path.join(currentRoot, "graph_album_replacement_links_v1.json");
const albumReplacementCsvPath = path.join(currentRoot, "graph_album_replacement_links_v1.csv");
const albumReplacementManifestPath = path.join(currentRoot, "graph_album_replacement_links_v1_manifest.md");

const manualArtistLinks = [
  link("artist_anchor|g i dle|g i dle", "1378887586", "user_provided_apple_artist_url", "verified", "high", "artist_alias_user_confirmed"),
  link("artist_anchor|afrika bambaataa and soulsonic force|afrika bambaataa and soulsonic force", "296025848", "user_provided_apple_artist_url", "verified", "high", "artist_alias_user_confirmed"),
  link("artist_anchor|banda ms|banda ms", "413048014", "user_provided_apple_artist_url", "verified", "high", "artist_alias_user_confirmed"),
  link("artist_anchor|bee gees early|bee gees early", "31937250", "user_provided_apple_artist_url", "verified", "high", "era_anchor_resolves_to_primary_artist"),
  link("artist_anchor|bill medley and jennifer warnes|bill medley and jennifer warnes", "1353760", "user_provided_component_artist_url", "candidate_verified", "medium", "component_artist_link_for_duet_anchor"),
  link("artist_anchor|hall and oates|hall and oates", "180586", "user_provided_apple_artist_url", "verified", "high", "artist_alias_user_confirmed"),
  link("artist_anchor|hildur gudnadottir|hildur gudnadottir", "306767183", "user_provided_apple_artist_url", "verified", "high", "artist_alias_user_confirmed"),
  link("artist_anchor|jackie brenston and his delta cats|jackie brenston and his delta cats", "3449346", "user_provided_apple_artist_url", "verified", "high", "leader_artist_link_for_group_anchor"),
  link("artist_anchor|jimmy darren|jimmy darren", "3224341", "user_provided_apple_artist_url", "verified", "high", "graph_alias_jimmy_to_james_darren_user_confirmed"),
  link("artist_anchor|kathy young and the innocents|kathy young and the innocents", "16749993", "user_provided_component_artist_url", "candidate_verified", "medium", "component_group_link_for_collaboration_anchor"),
  link("artist_anchor|kidz bop|kidz bop", "3628117", "user_provided_apple_artist_url", "verified", "high", "artist_alias_user_confirmed"),
  link("artist_anchor|la arrolladora banda el limon|la arrolladora banda el limon", "272094455", "user_provided_apple_artist_url", "verified", "high", "artist_alias_user_confirmed"),
  link("artist_anchor|mammoth wvh|mammoth wvh", "1808750544", "user_provided_apple_artist_url", "verified", "high", "artist_alias_user_confirmed"),
  link("artist_anchor|martha and the vandellas|martha and the vandellas", "13431501", "user_provided_apple_artist_url", "verified", "high", "artist_alias_user_confirmed"),
  link("artist_anchor|mos def yasiin bey|mos def yasiin bey", "92012", "user_provided_apple_artist_url", "verified", "high", "legacy_artist_name_resolves_to_mos_def"),
  link("artist_anchor|richard and mimi farina|richard and mimi farina", "258497764", "user_provided_apple_artist_url", "verified", "high", "artist_order_alias_user_confirmed"),
  link("artist_anchor|moody blues early|moody blues early", "133520", "user_provided_apple_artist_url", "verified", "high", "era_anchor_resolves_to_primary_artist"),
  link("artist_anchor|parliament|parliament", "79943", "manual_split_artist_node", "verified", "high", "split_from_parliament_funkadelic_composite"),
  link("artist_anchor|funkadelic|funkadelic", "32181103", "manual_split_artist_node", "verified", "high", "split_from_parliament_funkadelic_composite"),
  link("artist_anchor|soul stirrers|soul stirrers", "2133642", "manual_split_artist_node", "verified", "high", "split_from_sam_cooke_soul_stirrers_composite"),
];

const splitNodes = [
  splitNode("artist_anchor|parliament|parliament", "Parliament", "039", "Funk / Psychedelic Soul / Groove Canon", "artist_anchor|parliament funkadelic|parliament funkadelic", "manual_split_from_composite_artist_anchor", "79943"),
  splitNode("artist_anchor|funkadelic|funkadelic", "Funkadelic", "039", "Funk / Psychedelic Soul / Groove Canon", "artist_anchor|parliament funkadelic|parliament funkadelic", "manual_split_from_composite_artist_anchor", "32181103"),
  splitNode("artist_anchor|soul stirrers|soul stirrers", "The Soul Stirrers", "108", "Black Gospel / Gospel Soul", "artist_anchor|sam cooke and the soul stirrers|sam cooke and the soul stirrers", "manual_split_from_composite_artist_anchor", "2133642"),
];

const specialStatuses = [
  status("artist_anchor|disney|disney", "special_entity_no_apple_artist_resolver", "", "Disney is a family/soundtrack context entity in this graph, not a durable Apple artist anchor.", ["graph_context", "manual_resolver_review"], ["apple_music_auto_resolution"]),
  status("artist_anchor|original broadway cast of wicked|original broadway cast of wicked", "cast_entity_resolve_via_album_context", "", "Treat as cast-recording context; resolve playback through album/song links rather than an Apple artist anchor.", ["graph_context", "manual_resolver_review"], ["apple_music_auto_resolution"]),
  status("artist_anchor|parliament funkadelic|parliament funkadelic", "split_entity_replaced_by_distinct_artist_anchors", "artist_anchor|parliament|parliament;artist_anchor|funkadelic|funkadelic", "Composite P-Funk anchor split into distinct Parliament and Funkadelic artist nodes.", ["graph_context", "manual_resolver_review"], ["survey_display", "starter_atlas", "default_mission_generation", "apple_music_auto_resolution"]),
  status("artist_anchor|sam cooke and the soul stirrers|sam cooke and the soul stirrers", "split_entity_replaced_by_distinct_artist_anchors", "artist_anchor|sam cooke|sam cooke;artist_anchor|soul stirrers|soul stirrers", "Keep Sam Cooke and The Soul Stirrers as separate artist identities; Sam Cooke already has Apple artist 1195231.", ["graph_context", "manual_resolver_review"], ["survey_display", "starter_atlas", "default_mission_generation", "apple_music_auto_resolution"]),
  status("artist_anchor|red bird records|red bird girls", "historical_label_scene_special_entity", "", "Historical Red Bird girl-group context; active coverage is via Dixie Cups/Shangri-Las replacements, not an Apple artist.", ["graph_context", "manual_resolver_review"], ["apple_music_auto_resolution"]),
  status("artist_anchor|comsat angels|comsat angels", "do_not_present_for_now", "263285435", "Artist page exists, but usable Apple/Spotify catalog appears absent; keep for QA/manual resolver only.", ["qa_review", "manual_resolver_review"], ["survey_display", "starter_atlas", "default_mission_generation", "supabase_active_candidate", "openai_prompt_payload", "apple_music_auto_resolution"]),
];

const artistSummary = {
  run_version: "apple_music_artist_manual_resolution_pass_v1",
  status: "complete",
  generated_at: generatedAt,
  storefront,
  policy: {
    raw_apple_payloads_persisted: false,
    persisted_catalog_fields: ["apple_catalog_id", "apple_resource_type", "storefront", "match/status metadata"],
    excluded_persistent_fields: ["artwork", "previews", "lyrics", "raw_catalog_payload", "music_user_token"],
  },
  counts: {
    accepted_artist_links: manualArtistLinks.length,
    split_nodes: splitNodes.length,
    special_status_rows: specialStatuses.length,
    accepted_links_by_confidence: countBy(manualArtistLinks, "confidence"),
    statuses_by_resolution_status: countBy(specialStatuses, "resolution_status"),
  },
};

fs.writeFileSync(artistLinksPath, manualArtistLinks.map((row) => JSON.stringify(row)).join("\n") + "\n");
writeJson(artistStatusPath, {
  metadata: artistSummary,
  rows: specialStatuses,
});
writeCsv(artistStatusCsvPath, specialStatuses, [
  "source_ref",
  "resolution_status",
  "replacement_refs",
  "apple_catalog_id",
  "allowed_surfaces",
  "blocked_surfaces",
  "notes",
  "raw_payload_persisted",
]);
writeJson(artistSplitNodesPath, {
  metadata: artistSummary,
  rows: splitNodes,
});
writeJson(artistSummaryPath, artistSummary);
fs.writeFileSync(artistManifestPath, buildArtistManifest(artistSummary));

const albumReplacementRows = buildAlbumReplacementRows();
writeJson(albumReplacementJsonPath, {
  metadata: {
    id: "graph_album_replacement_links_v1",
    status: "active_replacement_link_ledger",
    generated_at: generatedAt,
    source_decision_pass: "data/canonical_graph/current/apple_music_album_graph_decision_pass_v1",
    replacement_model: "preserve_original_graph_target_and_link_apple_resolvable_replacement",
    raw_apple_payloads_persisted: false,
  },
  rows: albumReplacementRows,
});
writeCsv(albumReplacementCsvPath, albumReplacementRows, [
  "source_ref",
  "replacement_candidate_identity_key",
  "replacement_relationship",
  "replacement_artist_display_name",
  "replacement_title",
  "replacement_year",
  "apple_catalog_id",
  "apple_resource_type",
  "storefront",
  "sidecar_policy",
  "decision_reason",
  "notes",
  "raw_payload_persisted",
]);
fs.writeFileSync(albumReplacementManifestPath, buildAlbumReplacementManifest(albumReplacementRows));

console.log(JSON.stringify({
  artist_manual_links: manualArtistLinks.length,
  artist_split_nodes: splitNodes.length,
  artist_special_status_rows: specialStatuses.length,
  album_replacement_links: albumReplacementRows.length,
  album_replacements_for_sidecar: albumReplacementRows.filter((row) => row.sidecar_policy === "promote_album_sidecar").length,
  playlist_fallbacks: albumReplacementRows.filter((row) => row.sidecar_policy === "playlist_fallback_no_album_sidecar").length,
}, null, 2));

function link(sourceRef, appleCatalogId, matchBasis, matchStatus, confidence, warning) {
  return {
    link_key: `graph_artist_anchor:${sourceRef}:apple_music:artist:${appleCatalogId}:${storefront}`,
    run_version: "apple_music_artist_manual_resolution_pass_v1",
    source_ref: sourceRef,
    source_type: "graph_artist_anchor",
    source_candidate_type: "artist_anchor",
    external_catalog: "apple_music",
    apple_catalog_id: appleCatalogId,
    apple_resource_type: "artist",
    storefront,
    match_status: matchStatus,
    match_basis: matchBasis,
    confidence,
    result_rank: "",
    title_match: "not_applicable",
    artist_match: "user_or_manual_confirmed",
    year_delta: "",
    warnings: warning,
    verified_at: generatedAt,
    raw_payload_persisted: false,
  };
}

function splitNode(candidateIdentityKey, displayName, archetypeId, archetype, sourceRefReplaces, relationship, appleCatalogId) {
  return {
    candidate_identity_key: candidateIdentityKey,
    candidate_type: "artist_anchor",
    artist_display_name: displayName,
    title: displayName,
    year: null,
    archetype_ids: [archetypeId],
    archetypes: [archetype],
    source_ref_replaces: sourceRefReplaces,
    replacement_relationship: relationship,
    apple_catalog_id: appleCatalogId,
    apple_resource_type: "artist",
    storefront,
    raw_payload_persisted: false,
  };
}

function status(sourceRef, resolutionStatus, replacementRefs, notes, allowedSurfaces, blockedSurfaces) {
  return {
    source_ref: sourceRef,
    resolution_status: resolutionStatus,
    replacement_refs: replacementRefs,
    apple_catalog_id: /^\d/u.test(replacementRefs) ? replacementRefs : "",
    allowed_surfaces: allowedSurfaces,
    blocked_surfaces: blockedSurfaces,
    notes,
    raw_payload_persisted: false,
  };
}

function buildAlbumReplacementRows() {
  const replacementPath = path.join(currentRoot, "apple_music_album_graph_decision_pass_v1/apple_music_album_graph_replacement_nodes_v1.json");
  const rows = readJson(replacementPath).rows ?? [];
  return rows.map((row) => ({
    source_ref: row.source_ref_replaces,
    replacement_candidate_identity_key: row.candidate_identity_key,
    replacement_relationship: row.replacement_relationship,
    replacement_artist_display_name: row.artist_display_name,
    replacement_title: row.title,
    replacement_year: row.year,
    apple_catalog_id: row.apple_catalog_id,
    apple_resource_type: row.apple_resource_type,
    storefront: row.storefront,
    sidecar_policy: row.apple_resource_type === "album" ? "promote_album_sidecar" : "playlist_fallback_no_album_sidecar",
    decision_reason: row.decision_reason,
    notes: row.notes,
    raw_payload_persisted: false,
  }));
}

function buildArtistManifest(summary) {
  return `# Apple Music Artist Manual Resolution Pass v1

Generated: ${summary.generated_at}

Status: \`${summary.status}\`

## Counts

| Metric | Count |
| --- | ---: |
| Accepted artist links | ${summary.counts.accepted_artist_links} |
| Split artist nodes | ${summary.counts.split_nodes} |
| Special/status rows | ${summary.counts.special_status_rows} |

## Policy

- Raw Apple payloads persisted: \`false\`
- Stored fields are Apple artist IDs, storefront, source refs, split/status metadata, and match evidence only.
`;
}

function buildAlbumReplacementManifest(rows) {
  return `# Graph Album Replacement Links v1

Generated: ${generatedAt}

Status: \`active_replacement_link_ledger\`

| Metric | Count |
| --- | ---: |
| Replacement links | ${rows.length} |
| Album replacements promoted to sidecar policy | ${rows.filter((row) => row.sidecar_policy === "promote_album_sidecar").length} |
| Playlist fallbacks retained outside album sidecar | ${rows.filter((row) => row.sidecar_policy === "playlist_fallback_no_album_sidecar").length} |

Original graph album nodes are preserved. Replacement rows link Apple-resolvable substitutes to those original targets.
`;
}

function countBy(values, key) {
  const counts = {};
  for (const value of values) {
    const item = Array.isArray(value[key]) ? value[key].join(";") : String(value[key] ?? "");
    counts[item] = (counts[item] ?? 0) + 1;
  }
  return counts;
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function writeJson(file, value) {
  fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`);
}

function writeCsv(file, rows, headers) {
  const lines = [headers.join(",")];
  for (const row of rows) lines.push(headers.map((header) => csvCell(row[header])).join(","));
  fs.writeFileSync(file, `${lines.join("\n")}\n`);
}

function csvCell(value) {
  const text = Array.isArray(value) ? value.join(";") : String(value ?? "");
  if (/[",\n\r]/u.test(text)) return `"${text.replace(/"/g, "\"\"")}"`;
  return text;
}
