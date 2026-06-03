import crypto from "node:crypto";
import fs from "node:fs";

const manifestPath =
  "data/alpha_consumable_layer/alpha_v0/alpha_graph_surface_manifest.json";
const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));

const failures = [];
const candidateRequiredFields = [
  "candidate_id",
  "canonical_entity_id",
  "object_type",
  "family_id",
  "archetype_ids",
  "survey_page_role",
  "survey_intent",
  "dedupe_group",
  "priority_score",
  "trigger_rule",
  "positive_inference",
  "negative_inference",
  "do_not_infer"
];
const alpha1FixedIntakePath =
  "data/alpha_consumable_layer/alpha_v0/alpha1_fixed_survey_intake_graph_support_alpha_v0.json";
const alpha1FirstMissionHandoffPath =
  "data/alpha_consumable_layer/alpha_v0/alpha1_first_mission_handoff_graph_contract_alpha_v0.json";
const tileLogMetadataContractPath =
  "data/alpha_consumable_layer/alpha_v0/tile_log_metadata_contract_alpha_v0.json";
const surveyRuntimeIngestionAlignmentPath =
  "data/alpha_consumable_layer/alpha_v0/survey_runtime_ingestion_alignment_alpha_v0.json";
const routeIdentityContractPath =
  "data/alpha_consumable_layer/alpha_v0/alpha_route_identity_contract_alpha_v0.json";
const candidateReviewRiskReportPath =
  "data/alpha_consumable_layer/alpha_v0/candidate_review_risk_report_alpha_v0.json";
const surveyPageSelectionAuditRefsPath =
  "data/alpha_consumable_layer/alpha_v0/survey_page_selection_audit_refs_alpha_v0.json";
const canonicalMissionItemUniversePath =
  "data/alpha_consumable_layer/alpha_v0/canonical_mission_item_universe_alpha_v0.json";
const appleMusicUnmatchedDoNotUsePath =
  "data/alpha_consumable_layer/alpha_v0/apple_music_unmatched_do_not_use_alpha_v0.json";
const appleMusicCatalogIndexPath =
  "MusicAtlasController/Resources/canonical_apple_music_catalog_index_v1.json";

function readJson(path) {
  return JSON.parse(fs.readFileSync(path, "utf8"));
}

function sha256(path) {
  return crypto.createHash("sha256").update(fs.readFileSync(path)).digest("hex");
}

function fail(message) {
  failures.push(message);
}

function normalizedIdentityPart(value) {
  return String(value || "")
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/&/g, " and ")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function routeDisplayIdentityKey(routeType, artist, displayName) {
  return [routeType, artist, displayName].map(normalizedIdentityPart).join(":");
}

function appleMusicCatalogLookup(index) {
  const canonicalSongIds = new Map();
  for (const entry of index.entries || []) {
    if (entry.item_type !== "track" || !entry.apple_catalog_id) continue;
    for (const key of entry.match_keys || []) {
      if (!key.startsWith("canonical_entity_id:")) continue;
      const canonicalId = key.slice("canonical_entity_id:".length);
      if (!canonicalSongIds.has(canonicalId)) canonicalSongIds.set(canonicalId, entry);
    }
  }
  return canonicalSongIds;
}

const allowedRefSources = new Set([
  "canonical_graph",
  "user_local",
  "external_catalog",
  "unresolved"
]);
const allowedObjectTypes = new Set([
  "artist",
  "album",
  "song_recording",
  "composition_placeholder"
]);
const allowedResolutionStates = new Set([
  "resolved",
  "needs_resolution",
  "intentionally_user_local"
]);
const allowedCompositionPolicyStatuses = new Set([
  "resolved",
  "needs_review",
  "not_applicable",
  "no_review_needed",
  "composition_first_required",
  "split_confirmed"
]);
const allowedFirstMissionBehaviors = new Set([
  "anchor",
  "bridge",
  "probe",
  "risky_probe",
  "waypoint",
  "trap"
]);
const blockedFirstMissionBehaviors = new Set(["exclude", "unknown"]);
const recordingVariantByContext = {
  original: "studio",
  album_version: "studio",
  single_version: "studio",
  source_version: "source",
  cover: "hit_cover",
  remake: "hit_cover",
  live: "live",
  radio_edit: "radio_edit",
  clean: "clean",
  explicit: "explicit",
  remix: "remix",
  cast_recording: "cast",
  film_version: "soundtrack_pop",
  traditional_arrangement: "traditional_arrangement"
};

function compositionPolicyStatusForVersion(version) {
  if (!version) return "not_applicable";
  if (version.review_status !== "approved" || version.survey_safe !== true) {
    return "needs_review";
  }
  const context = version.recording_context || "unknown";
  if (context === "original" || context === "album_version" || context === "single_version") {
    return "no_review_needed";
  }
  return "split_confirmed";
}

function buildCanonicalMusicObjectRef(row, recordingVersion) {
  const ref = {
    object_type: row.object_type,
    ref_source: "canonical_graph",
    canonical_artist_id: row.object_type === "artist" ? row.canonical_entity_id : null,
    canonical_album_id: row.object_type === "album" ? row.canonical_entity_id : null,
    canonical_song_recording_id:
      row.object_type === "song_recording" ? row.canonical_entity_id : null,
    composition_placeholder_id: null,
    user_music_object_id: null,
    external_catalog_refs: {},
    display_name: row.display_label,
    credited_artist_name: recordingVersion?.display_artist_credit || null,
    credit_context: "unknown",
    resolution_state: "resolved",
    composition_policy_status:
      row.object_type === "song_recording"
        ? compositionPolicyStatusForVersion(recordingVersion)
        : "not_applicable",
    recording_variant_type:
      row.object_type === "song_recording"
        ? recordingVariantByContext[recordingVersion?.recording_context] || "unknown"
        : null,
    canonical_membership_context: {
      family_numbers: [row.family_id],
      archetype_ids: row.archetype_ids || [],
      membership_role_notes: "Graph membership context only; not user taste."
    }
  };
  return ref;
}

function validateMusicObjectRef(ref, label) {
  const required = [
    "object_type",
    "ref_source",
    "canonical_artist_id",
    "canonical_album_id",
    "canonical_song_recording_id",
    "composition_placeholder_id",
    "user_music_object_id",
    "external_catalog_refs",
    "display_name",
    "resolution_state",
    "composition_policy_status"
  ];
  for (const key of required) {
    if (!(key in ref)) fail(`${label} music_object_ref missing ${key}`);
  }
  if (!allowedObjectTypes.has(ref.object_type)) {
    fail(`${label} music_object_ref invalid object_type=${ref.object_type}`);
  }
  if (!allowedRefSources.has(ref.ref_source)) {
    fail(`${label} music_object_ref invalid ref_source=${ref.ref_source}`);
  }
  if (!allowedResolutionStates.has(ref.resolution_state)) {
    fail(`${label} music_object_ref invalid resolution_state=${ref.resolution_state}`);
  }
  if (!allowedCompositionPolicyStatuses.has(ref.composition_policy_status)) {
    fail(`${label} music_object_ref invalid composition_policy_status=${ref.composition_policy_status}`);
  }
  if (!ref.display_name || typeof ref.display_name !== "string") {
    fail(`${label} music_object_ref missing display_name`);
  }
  if (ref.ref_source === "canonical_graph") {
    if (ref.object_type === "artist" && !ref.canonical_artist_id) {
      fail(`${label} canonical artist ref missing canonical_artist_id`);
    }
    if (ref.object_type === "album" && !ref.canonical_album_id) {
      fail(`${label} canonical album ref missing canonical_album_id`);
    }
    if (ref.object_type === "song_recording" && !ref.canonical_song_recording_id) {
      fail(`${label} canonical song ref missing canonical_song_recording_id`);
    }
  }
  if (ref.object_type === "composition_placeholder" && !ref.composition_placeholder_id) {
    fail(`${label} composition placeholder ref missing composition_placeholder_id`);
  }
  if (ref.ref_source === "user_local") {
    if (!ref.user_music_object_id) fail(`${label} user_local ref missing user_music_object_id`);
    if (ref.resolution_state !== "intentionally_user_local") {
      fail(`${label} user_local ref must be intentionally_user_local`);
    }
  }
  if (ref.ref_source === "external_catalog") {
    if (!ref.external_catalog_refs || Object.keys(ref.external_catalog_refs).length === 0) {
      fail(`${label} external_catalog ref missing external_catalog_refs`);
    }
  }
  if (ref.ref_source === "unresolved" && ref.resolution_state !== "needs_resolution") {
    fail(`${label} unresolved ref must have resolution_state=needs_resolution`);
  }
  if (ref.canonical_membership_context) {
    const note = ref.canonical_membership_context.membership_role_notes || "";
    if (!note.includes("not user taste")) {
      fail(`${label} canonical_membership_context must state not user taste`);
    }
  }
}

function requireArrayIncludes(values, expected, label) {
  const actual = new Set(values || []);
  for (const value of expected) {
    if (!actual.has(value)) fail(`${label} missing ${value}`);
  }
}

for (const source of manifest.approved_source_files) {
  if (!fs.existsSync(source.file)) {
    fail(`missing approved source file: ${source.file}`);
    continue;
  }
  const actual = sha256(source.file);
  if (actual !== source.sha256) {
    fail(`sha256 mismatch for ${source.file}: expected ${source.sha256}, got ${actual}`);
  }
}

for (const source of manifest.alpha_overlay_files || []) {
  if (!fs.existsSync(source.file)) {
    fail(`missing alpha overlay file: ${source.file}`);
    continue;
  }
  const actual = sha256(source.file);
  if (actual !== source.sha256) {
    fail(`sha256 mismatch for ${source.file}: expected ${source.sha256}, got ${actual}`);
  }
}

for (const source of manifest.alpha_contract_files || []) {
  if (!fs.existsSync(source.file)) {
    fail(`missing alpha contract file: ${source.file}`);
    continue;
  }
  const actual = sha256(source.file);
  if (actual !== source.sha256) {
    fail(`sha256 mismatch for ${source.file}: expected ${source.sha256}, got ${actual}`);
  }
  if (source.file.endsWith(".json")) {
    readJson(source.file);
  }
}

const manifestContractFiles = new Set((manifest.alpha_contract_files || []).map((row) => row.file));
for (const requiredContract of [
  alpha1FixedIntakePath,
  alpha1FirstMissionHandoffPath,
  surveyRuntimeIngestionAlignmentPath,
  routeIdentityContractPath,
  candidateReviewRiskReportPath,
  surveyPageSelectionAuditRefsPath,
  canonicalMissionItemUniversePath,
  appleMusicUnmatchedDoNotUsePath,
  "data/alpha_consumable_layer/alpha_v0/alpha1_user_facing_graph_language_guardrails_alpha_v0.md"
]) {
  if (!manifestContractFiles.has(requiredContract)) {
    fail(`alpha manifest missing Alpha 1 contract file: ${requiredContract}`);
  }
}

for (const source of manifest.alpha_support_files || []) {
  if (!fs.existsSync(source.file)) {
    fail(`missing alpha support file: ${source.file}`);
    continue;
  }
  const actual = sha256(source.file);
  if (actual !== source.sha256) {
    fail(`sha256 mismatch for ${source.file}: expected ${source.sha256}, got ${actual}`);
  }
  if (source.file.endsWith(".json")) {
    readJson(source.file);
  }
}

const root = "data/canonical_graph/normalization_pass_2";
const quarantineRows = readJson(`${root}/canonical_quarantine_queue.json`);
const quarantinedIds = new Set();
const quarantinedTypedRefs = new Set();
for (const row of quarantineRows) {
  if (row.entity_ref) quarantinedTypedRefs.add(row.entity_ref);
  if (row.entity_type && row.canonical_entity_id) {
    quarantinedTypedRefs.add(`${row.entity_type}:${row.canonical_entity_id}`);
  }
  for (const key of [
    "entity_ref",
    "entity_id",
    "canonical_entity_id",
    "recording_id",
    "candidate_id"
  ]) {
    if (row[key]) quarantinedIds.add(String(row[key]).replace(/^[^:]+:/, ""));
  }
}

const blocklistPath =
  "data/alpha_consumable_layer/alpha_v0/alpha_candidate_blocklist_alpha_v0.json";
const alphaBlocklist = readJson(blocklistPath).blocklist || [];
const blockedCandidateIds = new Set(alphaBlocklist.map((row) => row.source_candidate_id));
const blockedTypedRefs = new Set(alphaBlocklist.map((row) => row.entity_ref));

const recordingVersions = readJson(`${root}/canonical_recording_versions.json`);
const recordingById = new Map(recordingVersions.map((row) => [row.recording_id, row]));
const appleCatalogIndex = readJson(appleMusicCatalogIndexPath);
const appleMusicTrackByCanonicalSongId = appleMusicCatalogLookup(appleCatalogIndex);
const noAppleIdPayload = readJson(appleMusicUnmatchedDoNotUsePath);
const canonicalMissionItemUniverse = readJson(canonicalMissionItemUniversePath);
const noAppleIdSurveyIds = new Set(
  (noAppleIdPayload.active_survey_unmatched_rows || []).map((row) => row.candidate_id)
);
const noAppleIdCanonicalIds = new Set(
  (noAppleIdPayload.active_survey_unmatched_rows || []).map((row) => row.canonical_entity_id)
);
if (noAppleIdPayload.status !== "do_not_use_no_apple_id_status_applied") {
  fail(`apple music unmatched do-not-use status=${noAppleIdPayload.status}`);
}
if (noAppleIdPayload.policy?.canonical_rows_remain_in_graph !== true) {
  fail("apple music unmatched do-not-use policy must keep canonical rows in graph");
}
if (
  (noAppleIdPayload.grid_unmatched_rows || []).length !==
  noAppleIdPayload.summary?.canonical_grid_rows_do_not_use_no_apple_id
) {
  fail("apple music unmatched do-not-use grid_unmatched_rows count must match summary");
}
if (
  noAppleIdPayload.summary?.canonical_grid_rows_do_not_use_no_apple_id !==
  canonicalMissionItemUniverse.summary?.alpha_survey_unavailable_no_apple_id
) {
  fail("apple music unmatched grid no-Apple count must match canonical mission universe survey-unavailable count");
}
if (canonicalMissionItemUniverse.status !== "canonical_grid_available_for_mission_items_with_playback_gate") {
  fail(`canonical mission item universe status=${canonicalMissionItemUniverse.status}`);
}
if (canonicalMissionItemUniverse.policy?.canonical_grid_available_for_mission_items !== true) {
  fail("canonical mission item universe must mark the canonical grid available for mission items");
}
if (canonicalMissionItemUniverse.policy?.compact_candidate_pool_is_not_the_universe !== true) {
  fail("canonical mission item universe must state compact pool is not the universe");
}
if (canonicalMissionItemUniverse.policy?.playback_requires_apple_music_catalog_id !== true) {
  fail("canonical mission item universe must require Apple Music catalog IDs for playback");
}
if ((canonicalMissionItemUniverse.mission_items || []).length !== canonicalMissionItemUniverse.summary?.canonical_grid_items) {
  fail("canonical mission item universe item count must match summary");
}
const noAppleUniverseCount = (canonicalMissionItemUniverse.mission_items || []).filter(
  (row) => row.do_not_use_status === "do_not_use_no_apple_id"
).length;
const surveyEligibleUniverseCount = (canonicalMissionItemUniverse.mission_items || []).filter(
  (row) => row.alpha_survey_eligible === true
).length;
if (
  noAppleUniverseCount !==
  canonicalMissionItemUniverse.summary?.playback_candidate_rows_do_not_use_no_apple_id
) {
  fail("canonical mission item universe no-Apple count must match summary");
}
if (surveyEligibleUniverseCount !== canonicalMissionItemUniverse.summary?.alpha_survey_eligible_grid_items) {
  fail("canonical mission item universe survey-eligible count must match summary");
}
for (const row of canonicalMissionItemUniverse.mission_items || []) {
  const label = `canonical_mission_item_universe:${row.mission_item_id}`;
  if (row.survey_apple_music_catalog_id && row.alpha_mission_item_status !== "blocked_by_alpha_blocklist") {
    if (row.alpha_survey_eligible !== true) {
      fail(`${label} has Apple ID but is not survey eligible`);
    }
    if (row.alpha_survey_status !== "survey_eligible_apple_id_resolved") {
      fail(`${label} has Apple ID but invalid alpha_survey_status=${row.alpha_survey_status}`);
    }
  }
  if (!row.survey_apple_music_catalog_id && row.alpha_survey_eligible === true) {
    fail(`${label} is survey eligible without Apple ID`);
  }
}
if (
  canonicalMissionItemUniverse.summary?.playback_candidate_rows_do_not_use_no_apple_id !==
  noAppleIdPayload.summary?.active_graph_playback_rows_do_not_use_no_apple_id
) {
  fail("canonical mission item universe no-Apple count must match no-Apple queue");
}
const gardenStateMissionItem = (canonicalMissionItemUniverse.mission_items || []).find(
  (row) => row.candidate_identity_key === "album|various artists|garden state"
);
if (!gardenStateMissionItem) {
  fail("canonical mission item universe must retain Garden State for QA visibility");
} else if (gardenStateMissionItem.alpha_mission_item_status !== "blocked_by_alpha_blocklist") {
  fail("Garden State must be blocked_by_alpha_blocklist in canonical mission item universe");
} else if (gardenStateMissionItem.alpha_survey_eligible !== false) {
  fail("Garden State must not be survey eligible");
}
for (const row of noAppleIdPayload.active_survey_unmatched_rows || []) {
  const label = `apple_music_unmatched_do_not_use:${row.candidate_id}`;
  if (row.status !== "do_not_use_no_apple_id") fail(`${label} status must be do_not_use_no_apple_id`);
  if (row.alpha_playback_eligible !== false) fail(`${label} alpha_playback_eligible must be false`);
  requireArrayIncludes(
    row.blocked_surfaces || [],
    [
      "default_mission_generation",
      "supabase_active_candidate",
      "openai_prompt_payload",
      "app_playback",
      "apple_music_auto_resolution"
    ],
    label
  );
}

const refExamples = readJson(
  "data/alpha_consumable_layer/alpha_v0/atlas_music_object_ref_examples_alpha_v0.json"
);
for (const example of refExamples.examples || []) {
  validateMusicObjectRef(example.ref, `atlas_music_object_ref_examples:${example.name}`);
}

const alpha1FixedIntake = readJson(alpha1FixedIntakePath);
if (alpha1FixedIntake.version !== "alpha_v0") {
  fail("alpha1 fixed Survey intake support must use version alpha_v0");
}
if (alpha1FixedIntake.status !== "approved_graph_support_for_alpha1_fixed_intake") {
  fail(`alpha1 fixed Survey intake support has unexpected status=${alpha1FixedIntake.status}`);
}
if (alpha1FixedIntake.graph_truth_rules?.graph_metadata_taste_truth !== false) {
  fail("alpha1 fixed Survey intake must mark graph_metadata_taste_truth=false");
}
if (alpha1FixedIntake.graph_truth_rules?.survey_response_creates_atlas_role !== false) {
  fail("alpha1 fixed Survey intake must not allow Survey response to create Atlas roles");
}
if (alpha1FixedIntake.graph_truth_rules?.survey_response_creates_landmark_region_or_dead_end !== false) {
  fail("alpha1 fixed Survey intake must not allow direct Landmark/Region/Dead End creation");
}
requireArrayIncludes(
  alpha1FixedIntake.family_rules?.context_only_blocked || [],
  [15, 17],
  "alpha1 fixed Survey intake context_only_blocked"
);
requireArrayIncludes(
  alpha1FixedIntake.candidate_row_requirements || [],
  [...candidateRequiredFields, "review_status"],
  "alpha1 fixed Survey intake candidate_row_requirements"
);
const fixedIntakeSurfaceToManifestKey = {
  artist: "artist",
  album: "album",
  song_recording: "song_recording"
};
for (const [surface, config] of Object.entries(
  alpha1FixedIntake.alpha1_required_intake?.object_surfaces || {}
)) {
  const manifestKey = fixedIntakeSurfaceToManifestKey[surface];
  const manifestCounts = manifest.candidate_surface_counts?.[manifestKey]?.totals || {};
  const available = (config.allowed_source_buckets || []).reduce(
    (sum, bucket) => sum + Number(manifestCounts[bucket] || 0),
    0
  );
  const declared = alpha1FixedIntake.active_candidate_availability?.[surface];
  if (!declared) {
    fail(`alpha1 fixed Survey intake missing active_candidate_availability for ${surface}`);
    continue;
  }
  if (Number(declared.available_for_alpha1_intake) !== available) {
    fail(
      `alpha1 fixed Survey intake ${surface} availability mismatch: declared ${declared.available_for_alpha1_intake}, manifest ${available}`
    );
  }
  if (available < Number(config.required_tiles || 0)) {
    fail(`alpha1 fixed Survey intake ${surface} has insufficient candidates`);
  }
  if (declared.capacity_status !== "pass") {
    fail(`alpha1 fixed Survey intake ${surface} capacity_status=${declared.capacity_status}`);
  }
  for (const bucket of config.allowed_source_buckets || []) {
    if (!["page1_core", "page2_adaptive"].includes(bucket)) {
      fail(`alpha1 fixed Survey intake ${surface} uses disallowed bucket=${bucket}`);
    }
  }
}

const alpha1FirstMissionHandoff = readJson(alpha1FirstMissionHandoffPath);
if (alpha1FirstMissionHandoff.version !== "alpha_v0") {
  fail("alpha1 first mission handoff must use version alpha_v0");
}
if (alpha1FirstMissionHandoff.graph_lane_ready_for_core_integration !== true) {
  fail("alpha1 first mission handoff must be marked ready for Core integration");
}
if (alpha1FirstMissionHandoff.mission_item_universe !== canonicalMissionItemUniversePath) {
  fail("alpha1 first mission handoff must reference the canonical mission item universe");
}
if (alpha1FirstMissionHandoff.compact_pool_is_full_mission_universe !== false) {
  fail("alpha1 first mission handoff must state compact pool is not the full mission universe");
}
requireArrayIncludes(
  alpha1FirstMissionHandoff.required_candidate_fields || [],
  [
    "candidate_id",
    "route_candidate_key",
    "route_batch_dedupe_key",
    "route_display_identity_key",
    "app_route_item_id",
    "candidate_role",
    "music_object_ref",
    "canonical_entity_id",
    "object_type",
    "canonical_object_type",
    "route_item_type",
    "playable_route_ready",
    "artist_level_candidate",
    "route_item",
    "candidate_pool_behavior",
    "credited_artist",
    "candidate_safety_state",
    "review_gate_status",
    "review_gate_action",
    "default_alpha_mission_eligible",
    "hard_block",
    "quarantine_status",
    "suppression_status",
    "resolver_risk_class",
    "review_risk_flags",
    "positive_inference",
    "negative_inference",
    "do_not_infer",
    "source_evidence_refs",
    "apple_music_catalog_status",
    "apple_music_catalog_id",
    "eligible_for_supabase",
    "eligible_for_openai"
  ],
  "alpha1 first mission handoff required_candidate_fields"
);
if (alpha1FirstMissionHandoff.route_identity_contract !== routeIdentityContractPath) {
  fail("alpha1 first mission handoff must reference the Alpha route identity contract");
}
if (alpha1FirstMissionHandoff.route_identity_policy?.route_items_must_come_from_candidate_pool !== true) {
  fail("alpha1 first mission handoff must require route items to come from the candidate pool");
}
if (
  alpha1FirstMissionHandoff.route_identity_policy
    ?.digest_or_strong_region_items_without_candidate_pool_membership_allowed !== false
) {
  fail("alpha1 first mission handoff must block non-candidate digest/strong-region route items");
}
if (alpha1FirstMissionHandoff.route_identity_policy?.display_string_identity_is_primary !== false) {
  fail("alpha1 first mission handoff must not use display strings as primary route identity");
}
for (const behavior of alpha1FirstMissionHandoff.allowed_candidate_pool_behaviors || []) {
  if (!allowedFirstMissionBehaviors.has(behavior)) {
    fail(`alpha1 first mission handoff has invalid allowed behavior=${behavior}`);
  }
  if (blockedFirstMissionBehaviors.has(behavior)) {
    fail(`alpha1 first mission handoff allowed behavior must not include blocked behavior=${behavior}`);
  }
}
requireArrayIncludes(
  alpha1FirstMissionHandoff.blocked_candidate_pool_behaviors || [],
  [...blockedFirstMissionBehaviors],
  "alpha1 first mission handoff blocked_candidate_pool_behaviors"
);
requireArrayIncludes(
  alpha1FirstMissionHandoff.blocked_default_first_mission_families || [],
  [15, 17],
  "alpha1 first mission handoff blocked_default_first_mission_families"
);
for (const familyId of alpha1FirstMissionHandoff.blocked_default_first_mission_families || []) {
  if ((alpha1FirstMissionHandoff.eligible_default_first_mission_families || []).includes(familyId)) {
    fail(`alpha1 first mission handoff family ${familyId} is both eligible and blocked`);
  }
}
requireArrayIncludes(
  alpha1FirstMissionHandoff.route_ready_requirements?.candidate_object_type || [],
  ["track"],
  "alpha1 first mission handoff route_ready_requirements.candidate_object_type"
);
if (alpha1FirstMissionHandoff.route_ready_requirements?.artist_level_route_candidates_allowed !== false) {
  fail("alpha1 first mission handoff must block artist-level route candidates");
}
if (alpha1FirstMissionHandoff.route_ready_requirements?.pseudo_playable_items_allowed !== false) {
  fail("alpha1 first mission handoff must block pseudo-playable route items");
}
if (alpha1FirstMissionHandoff.route_ready_requirements?.full_canonical_grid_available_for_mission_items !== true) {
  fail("alpha1 first mission handoff must keep full canonical grid available for mission items");
}
if (alpha1FirstMissionHandoff.route_ready_requirements?.compact_pool_is_sample_slice_not_universe !== true) {
  fail("alpha1 first mission handoff must state compact pool is a sample/slice");
}
if (alpha1FirstMissionHandoff.route_ready_requirements?.apple_music_catalog_id_required_for_default_playback !== true) {
  fail("alpha1 first mission handoff must require Apple Music catalog ID for default playback");
}
if (alpha1FirstMissionHandoff.review_gate_policy?.alpha_safe_with_review_flags_is_hard_block !== false) {
  fail("alpha1 first mission handoff must not hard-block alpha_safe_with_review_flags");
}
requireArrayIncludes(
  alpha1FirstMissionHandoff.graph_lane_non_claims || [],
  [
    "user_likes_candidate",
    "candidate_is_atlas_landmark",
    "candidate_is_confirmed_dead_end"
  ],
  "alpha1 first mission handoff graph_lane_non_claims"
);

const tileLogMetadataContract = readJson(tileLogMetadataContractPath);
requireArrayIncludes(
  tileLogMetadataContract.displayed_tile_required_fields || [],
  ["survey_session_id", "shown_page_id", "shown_page_history_ref", "apple_exposure_prior"],
  "tile log displayed_tile_required_fields"
);
if (
  tileLogMetadataContract.evidence_export_ingestion?.atlas_ingestable_path !==
  "survey_evidence_export.atlas_ingestable.evidence_atoms"
) {
  fail("tile log contract must point Atlas ingestion at atlas_ingestable.evidence_atoms");
}
if (
  tileLogMetadataContract.evidence_export_ingestion?.must_ignore_path !==
  "survey_evidence_export.construction_only_excluded"
) {
  fail("tile log contract must require construction_only_excluded to be ignored");
}
if (tileLogMetadataContract.evidence_export_ingestion?.same_session_display_history_required !== true) {
  fail("tile log contract must require same-session displayed page history");
}
if (tileLogMetadataContract.response_semantics?.apple_exposure_prior_taste_truth !== false) {
  fail("tile log contract must mark apple_exposure_prior_taste_truth=false");
}
if (
  !String(tileLogMetadataContract.response_semantics?.dont_know || "").includes(
    "familiarity_uncertainty"
  )
) {
  fail("tile log contract must map dont_know to familiarity_uncertainty");
}

const surveyRuntimeIngestionAlignment = readJson(surveyRuntimeIngestionAlignmentPath);
if (
  surveyRuntimeIngestionAlignment.ingestion_rule?.atlas_ingestable_path !==
  "survey_evidence_export.atlas_ingestable.evidence_atoms"
) {
  fail("survey runtime alignment must consume atlas_ingestable.evidence_atoms");
}
if (
  surveyRuntimeIngestionAlignment.ingestion_rule?.must_ignore_path !==
  "survey_evidence_export.construction_only_excluded"
) {
  fail("survey runtime alignment must ignore construction_only_excluded");
}
if (surveyRuntimeIngestionAlignment.ingestion_rule?.same_session_display_history_required !== true) {
  fail("survey runtime alignment must require same-session displayed page history");
}
if (surveyRuntimeIngestionAlignment.semantics?.apple_exposure_prior_taste_truth !== false) {
  fail("survey runtime alignment must mark apple_exposure_prior_taste_truth=false");
}
if (surveyRuntimeIngestionAlignment.semantics?.dont_know_mapping !== "familiarity_uncertainty") {
  fail("survey runtime alignment must map dont_know to familiarity_uncertainty");
}
requireArrayIncludes(
  surveyRuntimeIngestionAlignment.music_object_ref_policy?.visible_survey_object_types || [],
  ["artist", "album", "song_recording"],
  "survey runtime alignment visible_survey_object_types"
);

const routeIdentityContract = readJson(routeIdentityContractPath);
if (routeIdentityContract.version !== "alpha_v0") {
  fail("route identity contract must use version alpha_v0");
}
if (routeIdentityContract.hard_rules?.route_items_must_come_from_candidate_pool !== true) {
  fail("route identity contract must require candidate-pool route items");
}
if (routeIdentityContract.hard_rules?.digest_or_strong_region_items_without_candidate_pool_membership_allowed !== false) {
  fail("route identity contract must block digest/strong-region non-candidate route items");
}
if (routeIdentityContract.hard_rules?.display_string_identity_is_primary !== false) {
  fail("route identity contract must not use display identity as primary identity");
}
for (const field of [
  "candidate_id",
  "route_candidate_key",
  "route_batch_dedupe_key",
  "app_route_item_id",
  "dedupe_group",
  "route_display_identity_key"
]) {
  if (!routeIdentityContract.candidate_identity_fields?.[field]) {
    fail(`route identity contract missing candidate_identity_fields.${field}`);
  }
}
for (const batchBlocker of [
  "same app_route_item_id repeated across the 10-mission batch",
  "same candidate_id repeated across the 10-mission batch",
  "same route_candidate_key repeated across the 10-mission batch",
  "same route_batch_dedupe_key repeated across the 10-mission batch",
  "same route_display_identity_key repeated across the 10-mission batch when stronger keys differ or are missing"
]) {
  if (!(routeIdentityContract.validation_policy?.batch_blockers || []).includes(batchBlocker)) {
    fail(`route identity contract missing batch blocker: ${batchBlocker}`);
  }
}

const candidateFiles = [
  `${root}/survey_artist_candidates_v0_2.json`,
  `${root}/survey_album_candidates_v0_2.json`,
  `${root}/survey_song_candidates_v0_2.json`
];

for (const file of candidateFiles) {
  const data = readJson(file);
  for (const family of Object.values(data.families)) {
    for (const bucket of ["page1_core", "page2_adaptive", "page3_deep"]) {
      const rows = family[bucket] || [];
      const seenCanonicalIds = new Map();
      const seenDedupeGroups = new Map();
      for (const row of rows) {
        const label = `${file}:${bucket}:${row.candidate_id}`;
        const typedRef = `${row.object_type}:${row.canonical_entity_id}`;
        const alphaBlocked =
          blockedCandidateIds.has(row.candidate_id) || blockedTypedRefs.has(typedRef);
        if (alphaBlocked) continue;
        for (const field of candidateRequiredFields) {
          if (!(field in row)) fail(`${label} missing required candidate field ${field}`);
        }
        if (seenCanonicalIds.has(row.canonical_entity_id)) {
          fail(`${label} duplicates canonical_entity_id with ${seenCanonicalIds.get(row.canonical_entity_id)}`);
        }
        seenCanonicalIds.set(row.canonical_entity_id, row.candidate_id);
        if (seenDedupeGroups.has(row.dedupe_group)) {
          fail(`${label} duplicates dedupe_group with ${seenDedupeGroups.get(row.dedupe_group)}`);
        }
        seenDedupeGroups.set(row.dedupe_group, row.candidate_id);
        if (row.review_status !== "approved") {
          fail(`${label} has review_status=${row.review_status}`);
        }
        if (Array.isArray(row.quarantine_reasons) && row.quarantine_reasons.length > 0) {
          fail(`${label} has quarantine_reasons=${row.quarantine_reasons.join(",")}`);
        }
        if (quarantinedTypedRefs.has(typedRef)) {
          fail(`${label} matches typed canonical_quarantine_queue`);
        }
        if (quarantinedIds.has(row.canonical_entity_id)) {
          fail(`${label} has canonical_entity_id collision with canonical_quarantine_queue but is not alpha-blocklisted`);
        }
        if (row.survey_page_role !== bucket) {
          fail(`${label} has survey_page_role=${row.survey_page_role}, expected ${bucket}`);
        }
        if (!Array.isArray(row.positive_inference) || row.positive_inference.length === 0) {
          fail(`${label} missing positive_inference`);
        }
        if (!Array.isArray(row.negative_inference) || row.negative_inference.length === 0) {
          fail(`${label} missing negative_inference`);
        }
        if (!Array.isArray(row.do_not_infer) || row.do_not_infer.length === 0) {
          fail(`${label} missing do_not_infer`);
        }
        if (row.object_type === "song_recording") {
          const version = recordingById.get(row.canonical_entity_id);
          if (!version) {
            fail(`${label} missing recording-version sidecar row`);
          } else {
            if (version.review_status !== "approved") {
              fail(`${label} recording sidecar review_status=${version.review_status}`);
            }
            if (version.survey_safe !== true) {
              fail(`${label} recording sidecar survey_safe=${version.survey_safe}`);
            }
            if (version.apple_music_resolution_policy === "manual_review_required") {
              fail(`${label} recording sidecar requires manual MusicKit review`);
            }
          }
        }
        const version =
          row.object_type === "song_recording"
            ? recordingById.get(row.canonical_entity_id)
            : null;
        validateMusicObjectRef(buildCanonicalMusicObjectRef(row, version), label);
      }
    }
    const suppressed = family.suppressed_quarantined || [];
    for (const row of suppressed) {
      if (row.survey_page_role === "page1_core" || row.survey_page_role === "page2_adaptive") {
        fail(`${file}:suppressed_quarantined:${row.candidate_id} has active survey_page_role=${row.survey_page_role}`);
      }
    }
  }
}

const samplePool = readJson(
  "data/alpha_consumable_layer/alpha_v0/sample_compact_candidate_pool_alpha_v0.json"
);
if (samplePool.graph_metadata_taste_truth !== false) {
  fail("sample compact candidate pool must mark graph_metadata_taste_truth=false");
}
if (samplePool.atlas_promotion_created !== false) {
  fail("sample compact candidate pool must mark atlas_promotion_created=false");
}
if (samplePool.compact_pool_is_full_mission_universe !== false) {
  fail("sample compact candidate pool must state it is not the full mission universe");
}
if (samplePool.mission_item_universe !== canonicalMissionItemUniversePath) {
  fail("sample compact candidate pool must reference canonical mission item universe");
}
if (samplePool.route_readiness_status !== "route_ready_canonical_song_candidates") {
  fail("sample compact candidate pool must be playback-ready canonical song candidates");
}
if (samplePool.resolves_blocker !== "MGN-I004") {
  fail("sample compact candidate pool must declare resolves_blocker=MGN-I004");
}
if (samplePool.artist_level_candidates_in_route_pools !== false) {
  fail("sample compact candidate pool must not use artist-level route candidates");
}
const sampleSeen = new Set();
const sampleDisplayIdentitySeen = new Map();
const sampleRouteCandidateKeys = new Set();
const sampleRouteBatchDedupeKeys = new Set();
const sampleAppRouteItemIds = new Set();
let routeReadySampleCount = 0;
const sampleObjectTypeCounts = {};
for (const [poolName, rows] of Object.entries(samplePool.pools || {})) {
  if ((poolName === "waypoints" || poolName === "dead_end_checks") && rows.length === 0) {
    fail(`sample compact candidate pool ${poolName} must not be empty`);
  }
  for (const row of rows) {
    const label = `sample_compact_candidate_pool:${poolName}:${row.candidate_id}`;
    for (const field of [
      "route_candidate_key",
      "route_batch_dedupe_key",
      "route_display_identity_key",
      "app_route_item_id"
    ]) {
      if (typeof row[field] !== "string" || row[field].trim().length === 0) {
        fail(`${label} missing ${field}`);
      }
    }
    if (row.source_contract_version !== "alpha_v0") {
      fail(`${label} source_contract_version is not alpha_v0`);
    }
    if (row.eligible_for_openai !== true || row.eligible_for_supabase !== true) {
      fail(`${label} is not eligible for OpenAI/Supabase`);
    }
    if (row.candidate_pool_behavior === "unknown") {
      fail(`${label} candidate_pool_behavior must not be unknown in compact pool`);
    }
    if (!allowedFirstMissionBehaviors.has(row.candidate_pool_behavior)) {
      fail(`${label} invalid candidate_pool_behavior=${row.candidate_pool_behavior}`);
    }
    if (blockedFirstMissionBehaviors.has(row.candidate_pool_behavior)) {
      fail(`${label} uses blocked candidate_pool_behavior=${row.candidate_pool_behavior}`);
    }
    if (row.candidate_role !== row.candidate_pool_behavior) {
      fail(`${label} candidate_role must match candidate_pool_behavior`);
    }
    if (row.object_type !== "track") {
      fail(`${label} object_type must be playback-ready track, got ${row.object_type}`);
    }
    if (noAppleIdSurveyIds.has(row.candidate_id) || noAppleIdCanonicalIds.has(row.canonical_entity_id)) {
      fail(`${label} is marked do_not_use_no_apple_id`);
    }
    const appleEntry = appleMusicTrackByCanonicalSongId.get(row.canonical_entity_id);
    if (!appleEntry) {
      fail(`${label} missing Apple Music catalog index entry`);
    }
    if (row.apple_music_catalog_status !== "resolved") {
      fail(`${label} apple_music_catalog_status must be resolved`);
    }
    if (!row.apple_music_catalog_id) {
      fail(`${label} missing apple_music_catalog_id`);
    }
    if (appleEntry && row.apple_music_catalog_id !== appleEntry.apple_catalog_id) {
      fail(`${label} apple_music_catalog_id does not match catalog index`);
    }
    const expectedRoutePrefix = `route:${row.object_type}:${row.canonical_object_type}:`;
    if (!String(row.route_candidate_key || "").startsWith(expectedRoutePrefix)) {
      fail(`${label} route_candidate_key must start with ${expectedRoutePrefix}`);
    }
    if (row.route_batch_dedupe_key !== row.dedupe_group) {
      fail(`${label} route_batch_dedupe_key must match dedupe_group`);
    }
    if (!/^ITEM_ALPHA_[A-Z0-9_]+_[A-F0-9]{8}$/.test(row.app_route_item_id || "")) {
      fail(`${label} app_route_item_id must be an app-safe ITEM_ALPHA id`);
    }
    if (sampleRouteCandidateKeys.has(row.route_candidate_key)) {
      fail(`${label} duplicates route_candidate_key ${row.route_candidate_key}`);
    }
    sampleRouteCandidateKeys.add(row.route_candidate_key);
    if (sampleRouteBatchDedupeKeys.has(row.route_batch_dedupe_key)) {
      fail(`${label} duplicates route_batch_dedupe_key ${row.route_batch_dedupe_key}`);
    }
    sampleRouteBatchDedupeKeys.add(row.route_batch_dedupe_key);
    if (sampleAppRouteItemIds.has(row.app_route_item_id)) {
      fail(`${label} duplicates app_route_item_id ${row.app_route_item_id}`);
    }
    sampleAppRouteItemIds.add(row.app_route_item_id);
    if (row.route_item_type !== row.object_type) {
      fail(`${label} route_item_type must match object_type`);
    }
    if (row.playable_route_ready !== true) {
      fail(`${label} must mark playable_route_ready=true`);
    }
    if (row.artist_level_candidate !== false) {
      fail(`${label} must mark artist_level_candidate=false`);
    }
    if (!["alpha_safe_default", "alpha_safe_with_review_flags"].includes(row.candidate_safety_state)) {
      fail(`${label} invalid candidate_safety_state=${row.candidate_safety_state}`);
    }
    if (row.review_gate_status !== "eligible_for_default_alpha_generation") {
      fail(`${label} invalid review_gate_status=${row.review_gate_status}`);
    }
    if (!["generate_allowed", "generate_allowed_store_review_flags"].includes(row.review_gate_action)) {
      fail(`${label} invalid review_gate_action=${row.review_gate_action}`);
    }
    if (row.default_alpha_mission_eligible !== true) {
      fail(`${label} must mark default_alpha_mission_eligible=true`);
    }
    if (row.hard_block !== false) {
      fail(`${label} must mark hard_block=false`);
    }
    if (row.quarantine_status !== "clear") {
      fail(`${label} quarantine_status must be clear`);
    }
    if (row.suppression_status !== "active") {
      fail(`${label} suppression_status must be active`);
    }
    if (row.manual_review_required !== false) {
      fail(`${label} manual_review_required must be false`);
    }
    if (row.context_only !== false) {
      fail(`${label} context_only must be false`);
    }
    if (!Array.isArray(row.review_risk_flags)) {
      fail(`${label} review_risk_flags must be an array`);
    }
    if (!row.credited_artist || typeof row.credited_artist !== "string") {
      fail(`${label} missing credited_artist`);
    }
    if (!row.music_kit_search_hint || typeof row.music_kit_search_hint !== "string") {
      fail(`${label} missing music_kit_search_hint`);
    }
    if (!Array.isArray(row.source_evidence_refs) || row.source_evidence_refs.length === 0) {
      fail(`${label} missing source_evidence_refs`);
    }
    if (!row.route_item || row.route_item.route_item_type !== row.object_type) {
      fail(`${label} missing matching route_item`);
    }
    if (row.route_item?.apple_music_catalog_id !== row.apple_music_catalog_id) {
      fail(`${label} route_item.apple_music_catalog_id must match candidate`);
    }
    if (row.route_item?.apple_music_catalog_status !== "resolved") {
      fail(`${label} route_item.apple_music_catalog_status must be resolved`);
    }
    if (row.route_item?.item_id !== row.app_route_item_id) {
      fail(`${label} route_item.item_id must match app_route_item_id`);
    }
    if (row.route_item?.candidate_id !== row.candidate_id) {
      fail(`${label} route_item.candidate_id must match candidate_id`);
    }
    if (row.route_item?.route_candidate_key !== row.route_candidate_key) {
      fail(`${label} route_item.route_candidate_key must match route_candidate_key`);
    }
    if (row.route_item?.route_batch_dedupe_key !== row.route_batch_dedupe_key) {
      fail(`${label} route_item.route_batch_dedupe_key must match route_batch_dedupe_key`);
    }
    if (row.route_item?.route_display_identity_key !== row.route_display_identity_key) {
      fail(`${label} route_item.route_display_identity_key must match route_display_identity_key`);
    }
    if (row.object_type === "track" && row.music_object_ref.object_type !== "song_recording") {
      fail(`${label} track route item must reference a canonical song_recording`);
    }
    if (row.object_type === "album") fail(`${label} album route items are blocked in early Alpha default pool`);
    if (sampleSeen.has(row.dedupe_group)) {
      fail(`${label} duplicates sample dedupe_group ${row.dedupe_group}`);
    }
    sampleSeen.add(row.dedupe_group);
    const displayIdentityKey = routeDisplayIdentityKey(
      row.object_type,
      row.credited_artist,
      row.display_label || row.display_name
    );
    if (row.route_display_identity_key !== displayIdentityKey) {
      fail(`${label} route_display_identity_key must match normalized display identity ${displayIdentityKey}`);
    }
    if (sampleDisplayIdentitySeen.has(displayIdentityKey)) {
      fail(
        `${label} duplicates sample display identity ${displayIdentityKey} with ${sampleDisplayIdentitySeen.get(displayIdentityKey)}`
      );
    }
    sampleDisplayIdentitySeen.set(displayIdentityKey, row.candidate_id);
    sampleObjectTypeCounts[row.object_type] = (sampleObjectTypeCounts[row.object_type] || 0) + 1;
    if (row.playable_route_ready && ["track", "album"].includes(row.object_type)) {
      routeReadySampleCount += 1;
    }
    validateMusicObjectRef(row.music_object_ref, label);
  }
}
if (routeReadySampleCount === 0) {
  fail("sample compact candidate pool has no playback-ready canonical song candidates");
}
if (sampleObjectTypeCounts.artist) {
  fail("sample compact candidate pool must not contain artist route candidates");
}
if (samplePool.route_ready_candidate_count !== routeReadySampleCount) {
  fail(
    `sample compact candidate pool route_ready_candidate_count mismatch: declared ${samplePool.route_ready_candidate_count}, counted ${routeReadySampleCount}`
  );
}

const candidateReviewRiskReport = readJson(candidateReviewRiskReportPath);
if (candidateReviewRiskReport.status !== "route_candidate_review_risk_clear") {
  fail(`candidate review-risk report status=${candidateReviewRiskReport.status}`);
}
if (candidateReviewRiskReport.summary?.total_route_candidates !== routeReadySampleCount) {
  fail("candidate review-risk report total_route_candidates must match playback-ready sample count");
}
if (candidateReviewRiskReport.summary?.hard_blocked !== 0) {
  fail("candidate review-risk report must have hard_blocked=0");
}
if (candidateReviewRiskReport.summary?.default_alpha_mission_eligible !== routeReadySampleCount) {
  fail("candidate review-risk report must mark every route candidate default Alpha mission eligible");
}
if (candidateReviewRiskReport.gate_policy?.do_not_hard_block_generation_when?.length === 0) {
  fail("candidate review-risk report missing do_not_hard_block_generation_when policy");
}
for (const row of candidateReviewRiskReport.route_candidates || []) {
  const label = `candidate_review_risk_report:${row.candidate_id}`;
  for (const field of [
    "route_candidate_key",
    "route_batch_dedupe_key",
    "route_display_identity_key",
    "app_route_item_id"
  ]) {
    if (typeof row[field] !== "string" || row[field].trim().length === 0) {
      fail(`${label} missing ${field}`);
    }
  }
  if (row.default_alpha_mission_eligible !== true) fail(`${label} is not default Alpha mission eligible`);
  if (row.hard_block !== false) fail(`${label} must not be hard-blocked`);
  if (row.quarantine_status !== "clear") fail(`${label} quarantine_status must be clear`);
  if (row.suppression_status !== "active") fail(`${label} suppression_status must be active`);
  if (row.object_type !== "track") fail(`${label} object_type must be track`);
}

const surveyPageSelectionAuditRefs = readJson(surveyPageSelectionAuditRefsPath);
if (surveyPageSelectionAuditRefs.status !== "ready_for_live_smoke_page_selection_audit") {
  fail(`survey page-selection audit refs status=${surveyPageSelectionAuditRefs.status}`);
}
if ((surveyPageSelectionAuditRefs.audit_refs || []).length === 0) {
  fail("survey page-selection audit refs must not be empty");
}
for (const row of surveyPageSelectionAuditRefs.audit_refs || []) {
  const label = `survey_page_selection_audit_refs:${row.candidate_id}`;
  for (const field of [
    "audit_ref_id",
    "candidate_id",
    "canonical_entity_ref",
    "object_type",
    "display_label",
    "music_object_ref",
    "dedupe_group",
    "approved_surface_ref",
    "candidate_basis",
    "family",
    "archetypes",
    "graph_provenance_summary",
    "safety"
  ]) {
    if (!(field in row)) fail(`${label} missing ${field}`);
  }
  if (row.safety?.raw_graph_row_exposed !== false) fail(`${label} must not expose raw graph rows`);
  if (row.safety?.hidden_simulator_truth !== false) fail(`${label} must not expose hidden simulator truth`);
  if (
    row.object_type === "song_recording" &&
    row.safety?.apple_music_catalog_status === "unmatched_no_apple_id" &&
    row.safety?.do_not_use_status !== "do_not_use_no_apple_id"
  ) {
    fail(`${label} unmatched song audit ref missing do_not_use_no_apple_id`);
  }
  if (row.family?.graph_metadata_taste_truth !== false) fail(`${label} family graph metadata must not be taste truth`);
  if (!row.approved_surface_ref?.source_file || !row.approved_surface_ref?.source_bucket) {
    fail(`${label} missing approved surface source file/bucket`);
  }
  if (!row.candidate_basis?.survey_intent || !row.candidate_basis?.trigger_rule) {
    fail(`${label} missing candidate basis survey_intent/trigger_rule`);
  }
  validateMusicObjectRef(row.music_object_ref, label);
}

if (failures.length > 0) {
  console.error("ALPHA_CONSUMABLE_LAYER_VALIDATION_FAIL");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("ALPHA_CONSUMABLE_LAYER_VALIDATION_PASS");
console.log(`manifest=${manifestPath}`);
console.log(`approved_source_files=${manifest.approved_source_files.length}`);
console.log(`anchor_eligible_archetypes=${manifest.anchor_eligible_archetype_count}`);
