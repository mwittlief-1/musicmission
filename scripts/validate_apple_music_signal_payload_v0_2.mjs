#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const repoRoot = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const defaultPayloadPath = path.join(repoRoot, "MusicAtlasControllerTests/Fixtures/apple_music_signal_payload_v0_2_sample.json");
const schemaPath = path.join(repoRoot, "data/product_contracts/apple_music_signal_payload_v0_2.schema.json");
const payloadPath = process.argv[2] ? path.resolve(process.argv[2]) : defaultPayloadPath;

const payload = JSON.parse(fs.readFileSync(payloadPath, "utf8"));
const schema = JSON.parse(fs.readFileSync(schemaPath, "utf8"));
const failures = [];

function fail(message) {
  failures.push(message);
}

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function object(value, pointer) {
  if (!isObject(value)) {
    fail(`${pointer} must be an object`);
    return {};
  }
  return value;
}

function array(value, pointer) {
  if (!Array.isArray(value)) {
    fail(`${pointer} must be an array`);
    return [];
  }
  return value;
}

function sourceEntries() {
  const entries = [];
  for (const [groupName, group] of [
    ["primary_signal_sources", payload.primary_signal_sources],
    ["context_sources", payload.context_sources],
    ["observed_resource_annotations", payload.observed_resource_annotations]
  ]) {
    for (const [sectionName, section] of Object.entries(object(group, `/${groupName}`))) {
      entries.push({ groupName, sectionName, section, diagnostic: false, catalog: false });
    }
  }
  for (const [index, section] of array(payload.excluded_or_diagnostic_sources, "/excluded_or_diagnostic_sources").entries()) {
    entries.push({
      groupName: "excluded_or_diagnostic_sources",
      sectionName: section?.source_id ?? `diagnostic_${index}`,
      section,
      diagnostic: true,
      catalog: false
    });
  }
  entries.push({
    groupName: "catalog_hydration",
    sectionName: "catalog_hydration",
    section: {
      source_id: "catalog_hydration",
      cap: Number.MAX_SAFE_INTEGER,
      status: payload.catalog_hydration?.status,
      items: payload.catalog_hydration?.resources,
      errors: payload.catalog_hydration?.errors
    },
    diagnostic: false,
    catalog: true
  });
  return entries;
}

function hasStableIdentity(item) {
  return Boolean(
    item.source_item_id &&
      item.resource_type &&
      (
        item.apple_id ||
        item.catalog_id ||
        item.library_id ||
        item.persistent_id ||
        (item.display_name && (item.artist_name || item.album_title || item.playlist_name || item.resource_type === "artist"))
      )
  );
}

if (schema.properties?.schema_version?.const !== "apple_music_signal_payload.v0.2") {
  fail("schema must pin schema_version=apple_music_signal_payload.v0.2");
}
if (schema.properties?.probe_version?.const !== "apple_probe.v0.2") {
  fail("schema must pin probe_version=apple_probe.v0.2");
}

if (payload.schema_version !== "apple_music_signal_payload.v0.2") {
  fail("payload schema_version must be apple_music_signal_payload.v0.2");
}
if (payload.probe_version !== "apple_probe.v0.2") {
  fail("payload probe_version must be apple_probe.v0.2");
}
for (const key of [
  "payload_id",
  "captured_at",
  "storefront",
  "authorization",
  "primary_signal_sources",
  "context_sources",
  "observed_resource_annotations",
  "catalog_hydration",
  "excluded_or_diagnostic_sources"
]) {
  if (!Object.prototype.hasOwnProperty.call(payload, key)) {
    fail(`${key} is required`);
  }
}

const primary = object(payload.primary_signal_sources, "/primary_signal_sources");
for (const key of ["library_artists_sample", "library_albums_sample", "library_songs_sample"]) {
  if (Object.prototype.hasOwnProperty.call(primary, key)) {
    fail(`/primary_signal_sources/${key} is forbidden`);
  }
}

for (const key of [
  "heavy_rotation",
  "recently_played_tracks",
  "library_song_play_count",
  "library_song_last_played",
  "library_song_library_added",
  "library_album_library_added",
  "personal_recommendations"
]) {
  if (!Object.prototype.hasOwnProperty.call(primary, key)) {
    fail(`/primary_signal_sources/${key} is required`);
  }
}

let usefulCapturedSources = 0;
for (const { groupName, sectionName, section, diagnostic, catalog } of sourceEntries()) {
  const source = object(section, `/${groupName}/${sectionName}`);
  const sourceID = source.source_id ?? sectionName;
  const items = array(source.items, `/${groupName}/${sectionName}/items`);
  const errors = array(source.errors, `/${groupName}/${sectionName}/errors`);

  if (!["captured", "empty", "unavailable", "error", "not_requested"].includes(source.status)) {
    fail(`/${groupName}/${sectionName}/status is invalid`);
  }
  if (Number.isInteger(source.cap) && items.length > source.cap) {
    fail(`/${groupName}/${sectionName}/items exceeds cap ${source.cap}`);
  }
  if (diagnostic && source.excluded_from_survey_evidence !== true) {
    fail(`/${groupName}/${sectionName}/excluded_from_survey_evidence must be true`);
  }
  if (diagnostic && typeof source.diagnostic_reason !== "string") {
    fail(`/${groupName}/${sectionName}/diagnostic_reason is required`);
  }
  if (groupName === "primary_signal_sources" && source.status === "captured" && items.length > 0) {
    usefulCapturedSources += 1;
  }

  for (const [index, error] of errors.entries()) {
    if (typeof error.source !== "string" || error.source.length === 0) {
      fail(`/${groupName}/${sectionName}/errors/${index}/source is required`);
    }
    if (typeof error.code !== "string" || error.code.length === 0) {
      fail(`/${groupName}/${sectionName}/errors/${index}/code is required`);
    }
    if (typeof error.message !== "string" || error.message.length === 0) {
      fail(`/${groupName}/${sectionName}/errors/${index}/message is required`);
    }
  }

  for (const [index, item] of items.entries()) {
    if (!hasStableIdentity(item)) {
      fail(`/${groupName}/${sectionName}/items/${index} needs stable identity fields`);
    }
    if (!item.evidence_basis) {
      fail(`/${groupName}/${sectionName}/items/${index}/evidence_basis is required`);
    }
    if (!item.source_confidence) {
      fail(`/${groupName}/${sectionName}/items/${index}/source_confidence is required`);
    }
    if (item.evidence_basis === "diagnostic_excluded" && !diagnostic) {
      fail(`/${groupName}/${sectionName}/items/${index} uses diagnostic_excluded outside diagnostics`);
    }
    if (diagnostic && item.evidence_basis !== "diagnostic_excluded") {
      fail(`/${groupName}/${sectionName}/items/${index} must use diagnostic_excluded`);
    }
    if (item.evidence_basis === "catalog_identity" && !catalog) {
      fail(`/${groupName}/${sectionName}/items/${index} uses catalog_identity outside catalog_hydration`);
    }
    if (catalog && item.evidence_basis !== "catalog_identity") {
      fail(`/${groupName}/${sectionName}/items/${index} must use catalog_identity`);
    }
  }
}

if (usefulCapturedSources < 1) {
  fail("at least one useful primary source must be captured with items before Survey continues");
}

const authErrors = array(payload.authorization?.errors, "/authorization/errors");
for (const [index, error] of authErrors.entries()) {
  if (typeof error.source !== "string" || typeof error.code !== "string" || typeof error.message !== "string") {
    fail(`/authorization/errors/${index} must be source-scoped`);
  }
}

if (failures.length > 0) {
  console.error(`Apple Music Signal Payload v0.2 validation failed for ${path.relative(repoRoot, payloadPath)}`);
  for (const failure of failures) {
    console.error(`- ${failure}`);
  }
  process.exit(1);
}

console.log(`Apple Music Signal Payload v0.2 validation passed: ${path.relative(repoRoot, payloadPath)}`);
