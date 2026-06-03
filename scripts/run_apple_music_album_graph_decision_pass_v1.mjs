#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { createAppleMusicCatalogClient } from "./lib/appleMusicCatalogClient.mjs";

const repoRoot = process.cwd();
const currentRoot = path.join(repoRoot, "data/canonical_graph/current");
const outputRoot = path.join(currentRoot, "apple_music_album_graph_decision_pass_v1");
const runVersion = "apple_music_album_graph_decision_pass_v1";
const storefront = "us";

const client = createAppleMusicCatalogClient({
  storefront,
  maxRetries: 8,
  retryBaseDelayMs: 1000,
  retryMaxDelayMs: 60000,
  timeoutMs: 60000,
});

fs.mkdirSync(outputRoot, { recursive: true });

const linksPath = path.join(outputRoot, "apple_music_album_graph_decision_links_v1.jsonl");
const replacementNodesPath = path.join(outputRoot, "apple_music_album_graph_replacement_nodes_v1.json");
const decisionsPath = path.join(outputRoot, "apple_music_album_graph_decisions_v1.json");
const summaryPath = path.join(outputRoot, "apple_music_album_graph_decision_summary.json");
const manifestPath = path.join(outputRoot, "apple_music_album_graph_decision_manifest.md");

const graphRows = readJson(path.join(currentRoot, "graph_linking_node_set.json")).rows;
const graphAlbumsByRef = new Map(
  graphRows
    .filter((row) => row.candidate_type === "album")
    .map((row) => [row.candidate_identity_key, row]),
);
const existingLinks = [
  ...safeReadJsonl(path.join(currentRoot, "apple_music_link_pass_v1/apple_music_links_v1.jsonl")),
  ...safeReadJsonl(path.join(currentRoot, "apple_music_try_harder_pass_v1/apple_music_try_harder_links_v1.jsonl")),
  ...safeReadJsonl(path.join(currentRoot, "apple_music_residual_track_pass_v1/apple_music_residual_track_links_v1.jsonl")),
  ...safeReadJsonl(path.join(currentRoot, "apple_music_album_variant_pass_v1/apple_music_album_variant_links_v1.jsonl")),
  ...safeReadJsonl(path.join(currentRoot, "apple_music_offline_reconciliation_pass_v1/apple_music_offline_reconciliation_links_v1.jsonl")),
  ...safeReadJsonl(path.join(currentRoot, "apple_music_artist_album_resolver_pass_v1/apple_music_artist_album_resolver_links_v1.jsonl")),
  ...safeReadJsonl(path.join(currentRoot, "apple_music_high_confidence_album_pass_v1/apple_music_high_confidence_album_links_v1.jsonl")),
  ...safeReadJsonl(path.join(currentRoot, "apple_music_manual_album_review_pass_v1/apple_music_manual_album_review_links_v1.jsonl")),
  ...safeReadJsonl(path.join(currentRoot, "apple_music_semantic_album_hardening_pass_v1/apple_music_semantic_album_hardening_links_v1.jsonl")),
];

const existingSourceResourceKeys = new Set(
  existingLinks
    .filter((link) => ["verified", "candidate_verified"].includes(link.match_status))
    .map((link) => sourceResourceKey(link.source_type, link.source_ref, link.apple_resource_type)),
);
const outputSourceResourceKeys = new Set();
const outputLinkKeys = new Set();
const links = [];
const replacementNodes = [];
const decisionRows = [];

const decisions = [
  unavailable("album|various artists|garden state", "context_only_soundtrack_excluded_from_alpha_playback", "Garden State is retained only as historical/context graph material and must not feed Alpha playback, app catalog index, default Mission Generation, or Apple auto-resolution."),
  direct("album|neil diamond|hot august night", "1443288776", "Hot August Night (40th Anniversary Deluxe Edition)", "user_confirmed_same_target_deluxe"),
  replace("album|various artists|matrix", "album|various artists|matrix reloaded the album music from the motion picture", "Various Artists", "The Matrix Reloaded: The Album (Music from the Motion Picture)", 2003, "328870607", "album", "original_unavailable_use_sequel_soundtrack_node", "Original The Matrix rock/industrial soundtrack is unavailable; prior score candidate is explicitly rejected."),
  replace("album|minor threat|complete discography", "album|minor threat|first two seven inches", "Minor Threat", "First Two Seven Inches", 1984, "784725777", "album", "original_unavailable_use_same_artist_replacement_node", "Use same-artist early Minor Threat release as graph replacement node."),
  replace("album|fats domino|this is fats domino", "album|fats domino|fats domino swings", "Fats Domino", "Fats Domino Swings", 1958, "1396311078", "album", "original_unavailable_use_same_artist_replacement_node", "Use Apple-available same-artist Fats Domino album."),
  unavailable("album|various artists|trainspotting", "no_good_alternative", "Original soundtrack unavailable and no acceptable Apple alternative found."),
  replace("album|monks|black monk time", "album|monks|early years 1964 1965", "The Monks", "The Early Years 1964 - 1965", 2009, "1790512830", "album", "original_unavailable_use_same_artist_replacement_node", "Use same-artist archival replacement node."),
  replace("album|various artists|now that s what i call christmas", "playlist|apple music|christmas", "Apple Music", "Christmas", 2026, "pl.0928edf01d5648948370b1404c7c6d0a", "playlist", "album_unavailable_use_playlist_context_node", "Technically a playlist, but manually approved as having the right seasonal material. Do not treat as album sidecar."),
  replace("album|jackie wilson|mr excitement", "album|jackie wilson|20 greatest hits remastered", "Jackie Wilson", "20 Greatest Hits (Remastered)", 1983, "111289716", "album", "original_unavailable_use_same_artist_compilation_node", "Use same-artist compilation replacement."),
  replace("album|peter paul and mary|if i had a hammer", "album|peter paul and mary|very best of peter paul and mary", "Peter, Paul and Mary", "The Very Best of Peter, Paul and Mary", 2005, "79029971", "album", "original_unavailable_use_same_artist_compilation_node", "Use same-artist compilation replacement."),
  replace("album|rossington collins band|anytime anyplace anywhere", "album|rossington collins band|20th century masters millennium collection best of rossington collins band", "Rossington Collins Band", "20th Century Masters - The Millennium Collection: The Best of Rossington Collins Band", 2003, "1443843596", "album", "original_unavailable_use_same_artist_compilation_node", "Use same-artist compilation replacement."),
  replace("album|major lance|monkey time", "album|major lance|very best of major lance", "Major Lance", "The Very Best of Major Lance", 2000, "158532661", "album", "original_unavailable_use_same_artist_compilation_node", "Use same-artist compilation replacement."),
  replace("album|mahalia jackson|world s greatest gospel singer", "album|mahalia jackson|gospels spirituals hymns", "Mahalia Jackson", "Gospels, Spirituals, & Hymns", 1991, "1032611117", "album", "original_unavailable_use_same_artist_replacement_node", "Use Apple-available Mahalia Jackson gospel collection."),
  unavailable("album|funkadelic|one nation under a groove", "future_resolve_license_dispute", "Original album appears affected by a licensing/catalog gap. Keep as future resolve; Funkadelic already has Maggot Brain graph coverage."),
  replace("album|oscar d leon|el oscar de la salsa", "album|oscar d leon|la salsa en las venas", "Oscar D'Leon", "La Salsa en las Venas", 1993, "1472779181", "album", "original_unavailable_use_same_artist_replacement_node", "Use same-artist salsa replacement album."),
  unavailable("album|revels|intoxica", "no_good_album_available", "No acceptable Apple album target found."),
  replace("album|eevee|seeds", "album|eevee|beat tape 12", "eevee", "beat tape 12", 2026, "1860043305", "album", "source_album_bandcamp_only_use_same_artist_replacement_node", "Seeds is only on Bandcamp; use Apple-available same-artist replacement node."),
  replace("album|sugarhill gang|sugarhill gang", "album|sugarhill gang|essentials sugarhill gang", "The Sugarhill Gang", "The Essentials: The Sugarhill Gang", 2002, "51958106", "album", "original_unavailable_use_same_artist_compilation_node", "Use same-artist essentials compilation replacement."),
  replace("album|bad brains|bad brains", "album|bad brains|i against i", "Bad Brains", "I Against I", 1986, "1469831735", "album", "original_unavailable_use_same_artist_replacement_node", "Use same-artist album replacement instead of Rock for Light."),
  unavailable("album|kathy young and the innocents|a thousand stars", "single_only_no_good_album", "A Thousand Stars was a single; no acceptable Apple album target found."),
];

for (const decision of decisions) {
  if (decision.action === "direct_link") {
    await validateAppleResource(decision);
    recordDirectDecision(decision);
  } else if (decision.action === "replacement_node") {
    await validateAppleResource(decision);
    recordReplacementDecision(decision);
  } else {
    recordUnavailableDecision(decision);
  }
}

writeFinalArtifacts();

function direct(sourceRef, appleCatalogId, selectedTitle, reason) {
  return {
    action: "direct_link",
    source_ref: sourceRef,
    apple_catalog_id: appleCatalogId,
    apple_resource_type: "album",
    selected_title: selectedTitle,
    decision_reason: reason,
  };
}

function replace(sourceRef, replacementRef, replacementArtist, replacementTitle, replacementYear, appleCatalogId, resourceType, reason, notes) {
  return {
    action: "replacement_node",
    source_ref: sourceRef,
    replacement_candidate_identity_key: replacementRef,
    replacement_artist_display_name: replacementArtist,
    replacement_title: replacementTitle,
    replacement_year: replacementYear,
    apple_catalog_id: appleCatalogId,
    apple_resource_type: resourceType,
    decision_reason: reason,
    notes,
  };
}

function unavailable(sourceRef, reason, notes) {
  return {
    action: "unresolvable",
    source_ref: sourceRef,
    apple_music_resolution_status: "apple_music_unresolvable",
    replacement_status: "no_replacement_selected",
    decision_reason: reason,
    notes,
  };
}

async function validateAppleResource(decision) {
  if (decision.apple_resource_type === "playlist") {
    decision.validation_status = "not_validated_playlist_context";
    return;
  }
  try {
    const payload = await client.catalogGet(`/v1/catalog/${encodeURIComponent(storefront)}/albums/${encodeURIComponent(decision.apple_catalog_id)}`, {
      "fields[albums]": "name,artistName,releaseDate",
    });
    decision.validation_status = payload?.data?.[0]?.id ? "validated_sparse_catalog_lookup" : "not_found";
  } catch {
    decision.validation_status = "validation_request_failed";
  }
}

function recordDirectDecision(decision) {
  const sourceRow = graphAlbumsByRef.get(decision.source_ref);
  if (!sourceRow) throw new Error(`Missing graph row ${decision.source_ref}`);
  const fields = {
    apple_catalog_id: decision.apple_catalog_id,
    apple_resource_type: decision.apple_resource_type,
    source_candidate_type: "album",
    match_status: "verified",
    match_basis: "user_album_graph_decision_direct_link",
    confidence: "high",
    title_match: "user_confirmed_same_target",
    artist_match: isVarious(sourceRow.artist_display_name) ? "not_required_user_confirmed" : "user_confirmed",
    warnings: decision.decision_reason,
  };
  addLink(makeLink(decision.source_ref, "graph_album", fields));
  addLink(makeLink(decision.source_ref, "album_sidecar_album", fields));
  decisionRows.push(decisionRow({
    ...decision,
    candidate_type: "album",
    artist_display_name: sourceRow.artist_display_name,
    title: sourceRow.title,
    year: sourceRow.year,
    apple_music_resolution_status: "resolved_direct",
    replacement_status: "not_applicable",
  }));
}

function recordReplacementDecision(decision) {
  const sourceRow = graphAlbumsByRef.get(decision.source_ref);
  if (!sourceRow) throw new Error(`Missing graph row ${decision.source_ref}`);
  replacementNodes.push({
    candidate_identity_key: decision.replacement_candidate_identity_key,
    candidate_type: decision.apple_resource_type === "playlist" ? "playlist_context" : "album",
    artist_display_name: decision.replacement_artist_display_name,
    title: decision.replacement_title,
    year: decision.replacement_year,
    source_ref_replaces: decision.source_ref,
    replacement_relationship: "apple_resolvable_replacement_for_unresolvable_graph_album",
    apple_catalog_id: decision.apple_catalog_id,
    apple_resource_type: decision.apple_resource_type,
    storefront,
    decision_reason: decision.decision_reason,
    notes: decision.notes,
    raw_payload_persisted: false,
  });
  const fields = {
    apple_catalog_id: decision.apple_catalog_id,
    apple_resource_type: decision.apple_resource_type,
    source_candidate_type: decision.apple_resource_type === "playlist" ? "playlist_context" : "album",
    match_status: decision.apple_resource_type === "playlist" ? "candidate_verified" : "verified",
    match_basis: decision.apple_resource_type === "playlist"
      ? "user_album_graph_decision_playlist_replacement_node"
      : "user_album_graph_decision_replacement_node",
    confidence: decision.apple_resource_type === "playlist" ? "medium" : "high",
    title_match: "replacement_node_user_confirmed",
    artist_match: isVarious(sourceRow.artist_display_name) ? "not_required_replacement_node" : "replacement_node_user_confirmed",
    warnings: decision.decision_reason,
    replaces_source_ref: decision.source_ref,
  };
  addLink(makeLink(decision.replacement_candidate_identity_key, "graph_replacement_album", fields));
  decisionRows.push(decisionRow({
    ...decision,
    candidate_type: "album",
    artist_display_name: sourceRow.artist_display_name,
    title: sourceRow.title,
    year: sourceRow.year,
    apple_music_resolution_status: "apple_music_unresolvable",
    replacement_status: "replacement_node_selected",
  }));
}

function recordUnavailableDecision(decision) {
  const sourceRow = graphAlbumsByRef.get(decision.source_ref);
  if (!sourceRow) throw new Error(`Missing graph row ${decision.source_ref}`);
  decisionRows.push(decisionRow({
    ...decision,
    candidate_type: "album",
    artist_display_name: sourceRow.artist_display_name,
    title: sourceRow.title,
    year: sourceRow.year,
  }));
}

function decisionRow(decision) {
  return {
    source_ref: decision.source_ref,
    candidate_type: decision.candidate_type,
    artist_display_name: decision.artist_display_name,
    title: decision.title,
    year: decision.year,
    action: decision.action,
    apple_music_resolution_status: decision.apple_music_resolution_status,
    replacement_status: decision.replacement_status,
    replacement_candidate_identity_key: decision.replacement_candidate_identity_key ?? "",
    replacement_artist_display_name: decision.replacement_artist_display_name ?? "",
    replacement_title: decision.replacement_title ?? "",
    replacement_year: decision.replacement_year ?? "",
    apple_catalog_id: decision.apple_catalog_id ?? "",
    apple_resource_type: decision.apple_resource_type ?? "",
    storefront,
    decision_reason: decision.decision_reason,
    validation_status: decision.validation_status ?? "",
    notes: decision.notes ?? "",
    reviewed_at: "2026-05-28",
    raw_payload_persisted: false,
  };
}

function makeLink(sourceRef, sourceType, fields) {
  return {
    link_key: `${sourceType}:${sourceRef}:apple_music:${fields.apple_resource_type}:${fields.apple_catalog_id}:${storefront}`,
    run_version: runVersion,
    source_ref: sourceRef,
    source_type: sourceType,
    source_candidate_type: fields.source_candidate_type,
    external_catalog: "apple_music",
    apple_catalog_id: fields.apple_catalog_id,
    apple_resource_type: fields.apple_resource_type,
    storefront,
    match_status: fields.match_status,
    match_basis: fields.match_basis,
    confidence: fields.confidence,
    title_match: fields.title_match,
    artist_match: fields.artist_match,
    warnings: fields.warnings,
    replaces_source_ref: fields.replaces_source_ref ?? "",
    verified_at: new Date().toISOString(),
    raw_payload_persisted: false,
  };
}

function addLink(link) {
  const sourceKey = sourceResourceKey(link.source_type, link.source_ref, link.apple_resource_type);
  if (existingSourceResourceKeys.has(sourceKey) || outputSourceResourceKeys.has(sourceKey) || outputLinkKeys.has(link.link_key)) return;
  links.push(link);
  outputSourceResourceKeys.add(sourceKey);
  outputLinkKeys.add(link.link_key);
}

function writeFinalArtifacts() {
  const sortedLinks = [...links].sort((a, b) => a.link_key.localeCompare(b.link_key));
  const sortedReplacementNodes = [...replacementNodes].sort((a, b) => a.candidate_identity_key.localeCompare(b.candidate_identity_key));
  const sortedDecisions = [...decisionRows].sort((a, b) => a.source_ref.localeCompare(b.source_ref));
  const summary = {
    run_version: runVersion,
    status: "complete",
    generated_at: new Date().toISOString(),
    storefront,
    policy: {
      preserve_original_graph_target_for_unresolvable_albums: true,
      replacement_model: "add_new_graph_node_with_relationship_to_original_target",
      raw_apple_payloads_persisted: false,
      persisted_catalog_fields: ["apple_catalog_id", "apple_resource_type", "storefront", "decision metadata"],
      excluded_persistent_fields: ["artwork", "previews", "lyrics", "raw_catalog_payload", "music_user_token"],
    },
    counts: {
      decisions_total: sortedDecisions.length,
      direct_link_decisions: sortedDecisions.filter((row) => row.action === "direct_link").length,
      replacement_node_decisions: sortedDecisions.filter((row) => row.action === "replacement_node").length,
      unresolvable_without_replacement_decisions: sortedDecisions.filter((row) => row.action === "unresolvable").length,
      replacement_nodes_total: sortedReplacementNodes.length,
      new_links_total: sortedLinks.length,
      new_links_by_source_type: countBy(sortedLinks, "source_type"),
      new_links_by_resource_type: countBy(sortedLinks, "apple_resource_type"),
      decisions_by_status: countBy(sortedDecisions, "apple_music_resolution_status"),
      replacement_status_counts: countBy(sortedDecisions, "replacement_status"),
    },
  };

  fs.writeFileSync(linksPath, `${sortedLinks.map((link) => JSON.stringify(link)).join("\n")}\n`);
  writeJson(replacementNodesPath, { metadata: summary, rows: sortedReplacementNodes });
  writeJson(decisionsPath, { metadata: summary, rows: sortedDecisions });
  writeJson(summaryPath, summary);
  fs.writeFileSync(manifestPath, buildManifest(summary));
  console.log(JSON.stringify(summary, null, 2));
}

function buildManifest(summary) {
  return `# Apple Music Album Graph Decision Pass v1

Generated: ${summary.generated_at}

Status: \`${summary.status}\`

Storefront: \`${summary.storefront}\`

## Intent

Record user-reviewed album availability decisions from the latest 20-row unmatched slice. This pass separates direct same-target Apple links from graph replacement nodes and from albums that should remain preserved but Apple-unresolvable.

## Policy

- Preserve original graph target for unresolvable albums: \`true\`
- Replacement model: \`${summary.policy.replacement_model}\`
- Raw Apple payloads persisted: \`false\`

## Counts

- Decisions: ${summary.counts.decisions_total}
- Direct links: ${summary.counts.direct_link_decisions}
- Replacement nodes staged: ${summary.counts.replacement_nodes_total}
- Unresolvable without replacement: ${summary.counts.unresolvable_without_replacement_decisions}
- New links: ${summary.counts.new_links_total}

## New Links By Source Type

${tableFromCounts(summary.counts.new_links_by_source_type)}

## Decisions By Status

${tableFromCounts(summary.counts.decisions_by_status)}
`;
}

function sourceResourceKey(sourceType, sourceRef, resourceType) {
  return `${sourceType}\t${sourceRef}\t${resourceType}`;
}

function isVarious(value) {
  return normalize(value) === "various artists";
}

function normalize(value) {
  return String(value ?? "")
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/gu, "")
    .toLowerCase()
    .replace(/&/gu, " and ")
    .replace(/[^a-z0-9]+/gu, " ")
    .trim()
    .replace(/^the\s+/u, "")
    .replace(/\s+/gu, " ");
}

function countBy(rows, key) {
  const counts = {};
  for (const row of rows) {
    const value = row[key] || "unknown";
    counts[value] = (counts[value] ?? 0) + 1;
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
  return String(value ?? "").replace(/\|/gu, "\\|");
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function writeJson(file, value) {
  fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`);
}

function readJsonl(file) {
  const text = fs.readFileSync(file, "utf8").trim();
  if (!text) return [];
  return text.split("\n").filter(Boolean).map((line) => JSON.parse(line));
}

function safeReadJsonl(file) {
  return fs.existsSync(file) ? readJsonl(file) : [];
}
