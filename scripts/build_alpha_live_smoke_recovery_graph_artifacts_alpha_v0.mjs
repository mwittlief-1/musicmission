import fs from "node:fs";

const ROOT = "data/canonical_graph/normalization_pass_2";
const ALPHA = "data/alpha_consumable_layer/alpha_v0";
const CURRENT_GRAPH = "data/canonical_graph/current";
const APPLE_CATALOG_INDEX = "MusicAtlasController/Resources/canonical_apple_music_catalog_index_v1.json";

function readJson(path) {
  return JSON.parse(fs.readFileSync(path, "utf8"));
}

function writeJson(path, payload) {
  fs.writeFileSync(path, JSON.stringify(payload, null, 2) + "\n");
}

function writeMarkdown(path, lines) {
  fs.writeFileSync(path, lines.join("\n") + "\n");
}

const candidatePool = readJson(`${ALPHA}/sample_compact_candidate_pool_alpha_v0.json`);
const alphaBlocklist = readJson(`${ALPHA}/alpha_candidate_blocklist_alpha_v0.json`).blocklist || [];
const familyRecommendations = readJson(`${ALPHA}/family_inclusion_recommendation_alpha_v0.json`).families;
const familyById = new Map(familyRecommendations.map((row) => [row.family_id, row]));
const archetypeReadiness = readJson(`${ROOT}/archetype_readiness_v0_2.json`);
const archetypeById = new Map(archetypeReadiness.map((row) => [row.archetype_id, row]));
const recordingVersions = readJson(`${ROOT}/canonical_recording_versions.json`);
const recordingById = new Map(recordingVersions.map((row) => [row.recording_id, row]));
const appleCatalogIndex = readJson(APPLE_CATALOG_INDEX);
const currentGraphTaggingCorpus = readJson(`${CURRENT_GRAPH}/graph_tagging_corpus.json`).rows || [];
const currentGraphActiveInventory =
  readJson(`${CURRENT_GRAPH}/canonical_graph_active_inventory.json`).rows || [];

function appleMusicCatalogLookup(index) {
  const canonicalSongIds = new Map();
  const sourceRefs = new Set();
  const sourceRefEntries = new Map();
  const allSourceRefEntries = new Map();
  for (const entry of index.entries || []) {
    if (!entry.apple_catalog_id) continue;
    if (entry.source_ref && !allSourceRefEntries.has(entry.source_ref)) {
      allSourceRefEntries.set(entry.source_ref, entry);
    }
    for (const key of entry.match_keys || []) {
      if (key.startsWith("source_ref:")) {
        const sourceRef = key.slice("source_ref:".length);
        if (!allSourceRefEntries.has(sourceRef)) allSourceRefEntries.set(sourceRef, entry);
      }
    }
    if (entry.item_type !== "track") continue;
    if (entry.source_ref) {
      sourceRefs.add(entry.source_ref);
      if (!sourceRefEntries.has(entry.source_ref)) sourceRefEntries.set(entry.source_ref, entry);
    }
    for (const key of entry.match_keys || []) {
      if (key.startsWith("canonical_entity_id:")) {
        const canonicalId = key.slice("canonical_entity_id:".length);
        if (!canonicalSongIds.has(canonicalId)) canonicalSongIds.set(canonicalId, entry);
      }
      if (key.startsWith("source_ref:")) {
        const sourceRef = key.slice("source_ref:".length);
        sourceRefs.add(sourceRef);
        if (!sourceRefEntries.has(sourceRef)) sourceRefEntries.set(sourceRef, entry);
      }
    }
  }
  return { canonicalSongIds, sourceRefs, sourceRefEntries, allSourceRefEntries };
}

const appleMusicCatalog = appleMusicCatalogLookup(appleCatalogIndex);
const alphaBlocklistByEntityRef = new Map(alphaBlocklist.map((row) => [row.entity_ref, row]));

function normalizedSlug(value) {
  return String(value || "")
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/&/g, " and ")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function inventoryEntityRefs(row) {
  const artistTitleSlug = normalizedSlug(`${row.artist_display_name || ""} ${row.title || ""}`);
  if (row.candidate_type === "album") return [`album:${artistTitleSlug}`];
  if (row.candidate_type === "artist_anchor") {
    return [`artist:${normalizedSlug(row.artist_display_name || row.title)}`];
  }
  if (row.candidate_type === "song") return [`song:${artistTitleSlug}`, `song_recording:${artistTitleSlug}`];
  if (row.candidate_type === "recording") return [`recording:${artistTitleSlug}`, `song_recording:${artistTitleSlug}`];
  return [];
}

function inventoryBlocklistRow(row) {
  for (const ref of inventoryEntityRefs(row)) {
    const block = alphaBlocklistByEntityRef.get(ref);
    if (block) return block;
  }
  return null;
}

function graphSongSourceRefs(candidateIdentityKey) {
  const sourceRefs = new Set([candidateIdentityKey, `graph_song:${candidateIdentityKey}`]);
  if (String(candidateIdentityKey).startsWith("song|")) {
    const recordingKey = String(candidateIdentityKey).replace(/^song\|/, "recording|");
    sourceRefs.add(recordingKey);
    sourceRefs.add(`graph_recording:${recordingKey}`);
  }
  return sourceRefs;
}

function graphSongHasAppleMusic(candidateIdentityKey) {
  for (const ref of graphSongSourceRefs(candidateIdentityKey)) {
    if (appleMusicCatalog.sourceRefs.has(ref)) return true;
  }
  return false;
}

function graphInventorySourceRefs(row) {
  const sourceRefs = new Set([row.candidate_identity_key]);
  if (row.candidate_type === "artist_anchor") {
    sourceRefs.add(`graph_artist_anchor:${row.candidate_identity_key}`);
  }
  if (row.candidate_type === "album") {
    sourceRefs.add(`graph_album:${row.candidate_identity_key}`);
  }
  if (row.candidate_type === "song") {
    sourceRefs.add(`graph_song:${row.candidate_identity_key}`);
    const recordingKey = String(row.candidate_identity_key).replace(/^song\|/, "recording|");
    sourceRefs.add(recordingKey);
    sourceRefs.add(`graph_recording:${recordingKey}`);
  }
  if (row.candidate_type === "recording") {
    sourceRefs.add(`graph_recording:${row.candidate_identity_key}`);
    const songKey = String(row.candidate_identity_key).replace(/^recording\|/, "song|");
    sourceRefs.add(songKey);
    sourceRefs.add(`graph_song:${songKey}`);
  }
  return sourceRefs;
}

function graphInventoryAppleEntry(row) {
  for (const ref of graphInventorySourceRefs(row)) {
    const entry = appleMusicCatalog.sourceRefEntries.get(ref);
    if (entry) return entry;
  }
  return null;
}

function graphInventoryAnyAppleEntry(row) {
  for (const ref of graphInventorySourceRefs(row)) {
    const entry = appleMusicCatalog.allSourceRefEntries.get(ref);
    if (entry) return entry;
  }
  return null;
}

function isPlaybackCandidateType(type) {
  return type === "song" || type === "recording";
}

function surveySongAppleMusicStatus(row) {
  const entry = appleMusicCatalog.canonicalSongIds.get(row.canonical_entity_id);
  if (!entry) {
    return {
      apple_music_catalog_status: "unmatched_no_apple_id",
      apple_music_catalog_id: null,
      apple_music_catalog_url: null,
      apple_music_catalog_match_status: null,
      apple_music_catalog_match_basis: null,
      apple_music_storefront: null,
      alpha_playback_eligible: false,
      do_not_use_status: "do_not_use_no_apple_id"
    };
  }
  return {
    apple_music_catalog_status: "resolved",
    apple_music_catalog_id: entry.apple_catalog_id,
    apple_music_catalog_url: entry.apple_catalog_url || null,
    apple_music_catalog_match_status: entry.match_status || null,
    apple_music_catalog_match_basis: entry.match_basis || null,
    apple_music_storefront: entry.storefront || "us",
    alpha_playback_eligible: true,
    do_not_use_status: null
  };
}

function countBy(rows, keyFn) {
  const counts = {};
  for (const row of rows) {
    const key = keyFn(row);
    counts[key] = (counts[key] || 0) + 1;
  }
  return counts;
}

const routeCandidates = Object.entries(candidatePool.pools || {}).flatMap(([poolName, rows]) =>
  rows.map((row) => ({ ...row, pool_name: poolName }))
);

const routeRows = routeCandidates.map((row) => ({
  candidate_id: row.candidate_id,
  route_candidate_key: row.route_candidate_key,
  route_batch_dedupe_key: row.route_batch_dedupe_key,
  route_display_identity_key: row.route_display_identity_key,
  app_route_item_id: row.app_route_item_id,
  pool_name: row.pool_name,
  object_type: row.object_type,
  canonical_object_type: row.canonical_object_type,
  canonical_entity_id: row.canonical_entity_id,
  display_name: row.display_name,
  credited_artist: row.credited_artist,
  candidate_role: row.candidate_role,
  candidate_pool_behavior: row.candidate_pool_behavior,
  risk_class: row.risk_class,
  candidate_safety_state: row.candidate_safety_state,
  review_gate_status: row.review_gate_status,
  review_gate_action: row.review_gate_action,
  default_alpha_mission_eligible: row.default_alpha_mission_eligible,
  hard_block: row.hard_block,
  blocked_reason: row.blocked_reason,
  quarantine_status: row.quarantine_status,
  suppression_status: row.suppression_status,
  resolver_risk_class: row.resolver_risk_class,
  review_risk_flags: row.review_risk_flags || [],
  review_status: row.review_status,
  manual_review_required: row.manual_review_required,
  context_only: row.context_only,
  family_id: row.family_id,
  archetype_ids: row.archetype_ids,
  source_file: row.source_file,
  source_membership_id: row.source_membership_id,
  music_kit_search_hint: row.music_kit_search_hint,
  apple_music_resolution_policy: row.apple_music_resolution_policy,
  apple_music_catalog_status: row.apple_music_catalog_status || null,
  apple_music_catalog_id: row.apple_music_catalog_id || null,
  apple_music_catalog_url: row.apple_music_catalog_url || null,
  apple_music_catalog_match_status: row.apple_music_catalog_match_status || null,
  apple_music_catalog_match_basis: row.apple_music_catalog_match_basis || null,
  version_risk_note: row.version_risk_note,
  source_evidence_refs: row.source_evidence_refs || []
}));

const hardBlockedRows = routeRows.filter((row) => row.hard_block || !row.default_alpha_mission_eligible);

const reviewRiskReport = {
  artifact: "candidate_review_risk_report",
  version: "alpha_v0",
  alpha_contract_version: "alpha_v0",
  generated_at: new Date().toISOString(),
  status: hardBlockedRows.length ? "route_candidate_review_risk_has_blocks" : "route_candidate_review_risk_clear",
  purpose:
    "Expose playback-ready candidate safety metadata so Mission Generation/Supabase can store review flags without false hard review gates.",
  source_candidate_pool: `${ALPHA}/sample_compact_candidate_pool_alpha_v0.json`,
  summary: {
    total_route_candidates: routeRows.length,
    default_alpha_mission_eligible: routeRows.filter((row) => row.default_alpha_mission_eligible).length,
    hard_blocked: hardBlockedRows.length,
    track_candidates: routeRows.filter((row) => row.object_type === "track").length,
    album_candidates: routeRows.filter((row) => row.object_type === "album").length,
    artist_candidates: routeRows.filter((row) => row.object_type === "artist").length,
    waypoints: routeRows.filter((row) => row.pool_name === "waypoints").length,
    dead_end_checks: routeRows.filter((row) => row.pool_name === "dead_end_checks").length
  },
  counts: {
    by_pool: countBy(routeRows, (row) => row.pool_name),
    by_object_type: countBy(routeRows, (row) => row.object_type),
    by_risk_class: countBy(routeRows, (row) => row.risk_class),
    by_candidate_safety_state: countBy(routeRows, (row) => row.candidate_safety_state),
    by_review_gate_action: countBy(routeRows, (row) => row.review_gate_action),
    by_resolver_risk_class: countBy(routeRows, (row) => row.resolver_risk_class)
  },
  gate_policy: {
    hard_block_generation_when: [
      "hard_block == true",
      "default_alpha_mission_eligible != true",
      "review_status != approved",
      "quarantine_status != clear",
      "suppression_status != active",
      "manual_review_required == true",
      "context_only == true",
      "object_type != track",
      "apple_music_catalog_status != resolved",
      "apple_music_catalog_id is missing"
    ],
    do_not_hard_block_generation_when: [
      "candidate_safety_state == alpha_safe_with_review_flags",
      "risk_class == medium",
      "risk_class == high with candidate_role in [risky_probe, trap]",
      "review_risk_flags is non-empty"
    ],
    alpha_recommendation:
      "Store review_risk_flags/audit metadata and continue generation attempts; app import still requires valid mission.v0.2."
  },
  route_candidates: routeRows
};

writeJson(`${ALPHA}/candidate_review_risk_report_alpha_v0.json`, reviewRiskReport);

writeMarkdown(`${ALPHA}/candidate_review_risk_report_alpha_v0.md`, [
  "# Candidate Review-Risk Report Alpha v0",
  "",
  "Alpha contract version: `alpha_v0`",
  "",
  `Generated: ${reviewRiskReport.generated_at}`,
  "",
  `Status: \`${reviewRiskReport.status}\``,
  "",
  "Purpose: expose playback-ready candidate safety metadata so Mission Generation/Supabase can store review flags without false hard review gates.",
  "",
  "## Summary",
  "",
  "| metric | count |",
  "| --- | ---: |",
  `| total route candidates | ${reviewRiskReport.summary.total_route_candidates} |`,
  `| default Alpha mission eligible | ${reviewRiskReport.summary.default_alpha_mission_eligible} |`,
  `| hard blocked | ${reviewRiskReport.summary.hard_blocked} |`,
  `| track candidates | ${reviewRiskReport.summary.track_candidates} |`,
  `| album candidates | ${reviewRiskReport.summary.album_candidates} |`,
  `| artist candidates | ${reviewRiskReport.summary.artist_candidates} |`,
  `| waypoints | ${reviewRiskReport.summary.waypoints} |`,
  `| dead-end checks | ${reviewRiskReport.summary.dead_end_checks} |`,
  "",
  "## Gate Policy",
  "",
  "Do not hard-block generation merely because a candidate has review flags. Use the flags for audit/review posture while continuing attempts toward the Alpha target.",
  "",
  "Hard-block only when a candidate is actually blocked, quarantined, suppressed, manual-review-only, context-only, not playback-ready, or not approved.",
  "",
  "## Review Actions",
  "",
  "| action | count |",
  "| --- | ---: |",
  ...Object.entries(reviewRiskReport.counts.by_review_gate_action).map(([key, value]) => `| ${key} | ${value} |`),
  "",
  "## Risk Classes",
  "",
  "| risk_class | count |",
  "| --- | ---: |",
  ...Object.entries(reviewRiskReport.counts.by_risk_class).map(([key, value]) => `| ${key} | ${value} |`),
  "",
  "## Candidate Rows",
  "",
  "| pool | object | display | role | risk | safety | action | flags |",
  "| --- | --- | --- | --- | --- | --- | --- | --- |",
  ...routeRows.map((row) =>
    `| ${row.pool_name} | ${row.object_type} | ${row.credited_artist} - ${row.display_name} | ${row.candidate_role} | ${row.risk_class} | ${row.candidate_safety_state} | ${row.review_gate_action} | ${(row.review_risk_flags || []).join(", ")} |`
  )
]);

function musicObjectRefForSurveyCandidate(row) {
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
    resolution_state: "resolved",
    composition_policy_status: "not_applicable"
  };
  if (row.object_type === "song_recording") {
    const version = recordingById.get(row.canonical_entity_id);
    ref.credited_artist_name = version?.display_artist_credit || null;
    ref.composition_policy_status =
      version?.review_status === "approved" && version?.survey_safe === true
        ? "no_review_needed"
        : "needs_review";
  }
  return ref;
}

function sourceMixHint(row, bucket) {
  if (row.survey_intent === "false_nearby_test") return "false_nearby_probe";
  if (row.survey_intent === "boundary_test") return "negative_control_probe";
  if (row.survey_intent === "bridge_test" || bucket === "page2_adaptive") return "adaptive_bridge";
  if (row.survey_intent === "deepening_only" || bucket === "page3_deep") return "frontier_probe";
  if (row.survey_intent === "song_first_memory" || row.survey_intent === "album_world_test") {
    return "waypoint_context_probe";
  }
  return "graph_core";
}

const auditRefs = [];
const activeSurveySongRows = [];
for (const [objectType, file] of [
  ["artist", "survey_artist_candidates_v0_2.json"],
  ["album", "survey_album_candidates_v0_2.json"],
  ["song_recording", "survey_song_candidates_v0_2.json"]
]) {
  const data = readJson(`${ROOT}/${file}`);
  for (const family of Object.values(data.families || {})) {
    for (const bucket of ["page1_core", "page2_adaptive", "page3_deep"]) {
      for (const row of family[bucket] || []) {
        if (row.object_type !== objectType) continue;
        if (row.object_type === "song_recording") activeSurveySongRows.push({ ...row, source_file: file, source_bucket: bucket });
        const familyInfo = familyById.get(row.family_id) || {};
        const appleStatus =
          row.object_type === "song_recording" ? surveySongAppleMusicStatus(row) : null;
        const archetypes = (row.archetype_ids || []).map((id) => {
          const info = archetypeById.get(id) || {};
          return {
            archetype_id: id,
            diagnostic_label: info.archetype_name || null,
            readiness: info.readiness || null,
            fast_survey_allowed: info.fast_survey_allowed ?? null
          };
        });
        auditRefs.push({
          audit_ref_id: `audit:${row.candidate_id}`,
          candidate_id: row.candidate_id,
          canonical_entity_ref: `${row.object_type}:${row.canonical_entity_id}`,
          canonical_entity_id: row.canonical_entity_id,
          object_type: row.object_type,
          display_label: row.display_label,
          music_object_ref: musicObjectRefForSurveyCandidate(row),
          dedupe_group: row.dedupe_group,
          approved_surface_ref: {
            source_contract_version: "alpha_v0",
            source_file: file,
            source_bucket: bucket,
            survey_page_role: row.survey_page_role,
            source_membership_id: row.source_membership_id || null
          },
          candidate_basis: {
            survey_intent: row.survey_intent,
            trigger_rule: row.trigger_rule,
            priority_score: row.priority_score,
            source_mix_hint: sourceMixHint(row, bucket)
          },
          family: {
            family_id: row.family_id,
            diagnostic_label: familyInfo.family_name || family.family_name || null,
            caution_flags: familyInfo.caution_flags || [],
            default_first_mission_allowed: familyInfo.default_first_mission_allowed ?? null,
            graph_metadata_taste_truth: false
          },
          archetypes,
          graph_provenance_summary:
            `Approved ${bucket} ${row.object_type} candidate from ${file}; diagnostic refs only; graph metadata is not user taste.`,
          safety: {
            review_status: row.review_status,
            approved_surface: row.review_status === "approved",
            quarantine_clear: Array.isArray(row.quarantine_reasons) && row.quarantine_reasons.length === 0,
            suppressed: false,
            hidden_simulator_truth: false,
            raw_graph_row_exposed: false,
            apple_music_catalog_status: appleStatus?.apple_music_catalog_status || "not_applicable",
            apple_music_catalog_id: appleStatus?.apple_music_catalog_id || null,
            alpha_playback_eligible: appleStatus?.alpha_playback_eligible ?? null,
            do_not_use_status: appleStatus?.do_not_use_status || null
          },
          inference_context: {
            positive_inference: row.positive_inference || [],
            negative_inference: row.negative_inference || [],
            do_not_infer: row.do_not_infer || []
          },
          public_label_policy: "diagnostic_label_not_user_facing_without_product_approval"
        });
      }
    }
  }
}

const auditPayload = {
  artifact: "survey_page_selection_audit_refs",
  version: "alpha_v0",
  alpha_contract_version: "alpha_v0",
  generated_at: new Date().toISOString(),
  status: "ready_for_live_smoke_page_selection_audit",
  purpose:
    "Stable Canonical refs/diagnostic labels for Survey/Core page-selection audit without exposing raw graph rows or hidden simulator truth.",
  source_files: [
    `${ROOT}/survey_artist_candidates_v0_2.json`,
    `${ROOT}/survey_album_candidates_v0_2.json`,
    `${ROOT}/survey_song_candidates_v0_2.json`
  ],
  summary: {
    total_audit_refs: auditRefs.length,
    by_object_type: countBy(auditRefs, (row) => row.object_type),
    by_surface_bucket: countBy(auditRefs, (row) => row.approved_surface_ref.source_bucket),
    caution_flagged_refs: auditRefs.filter((row) => row.family.caution_flags.length > 0).length
  },
  fields_safe_for_client_diagnostic_upload: [
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
    "safety",
    "inference_context"
  ],
  blocked_from_normal_tester_ui: [
    "family.diagnostic_label",
    "archetypes.diagnostic_label",
    "candidate_basis",
    "graph_provenance_summary",
    "inference_context"
  ],
  audit_refs: auditRefs
};

writeJson(`${ALPHA}/survey_page_selection_audit_refs_alpha_v0.json`, auditPayload);

writeMarkdown(`${ALPHA}/survey_page_selection_audit_refs_alpha_v0.md`, [
  "# Survey Page Selection Audit Refs Alpha v0",
  "",
  "Alpha contract version: `alpha_v0`",
  "",
  `Generated: ${auditPayload.generated_at}`,
  "",
  `Status: \`${auditPayload.status}\``,
  "",
  "Purpose: stable Canonical refs/diagnostic labels for Survey/Core page-selection audit without exposing raw graph rows or hidden simulator truth.",
  "",
  "## Summary",
  "",
  "| metric | count |",
  "| --- | ---: |",
  `| total audit refs | ${auditPayload.summary.total_audit_refs} |`,
  `| caution-flagged refs | ${auditPayload.summary.caution_flagged_refs} |`,
  "",
  "## By Object Type",
  "",
  "| object_type | count |",
  "| --- | ---: |",
  ...Object.entries(auditPayload.summary.by_object_type).map(([key, value]) => `| ${key} | ${value} |`),
  "",
  "## By Surface Bucket",
  "",
  "| bucket | count |",
  "| --- | ---: |",
  ...Object.entries(auditPayload.summary.by_surface_bucket).map(([key, value]) => `| ${key} | ${value} |`),
  "",
  "## Usage Rule",
  "",
  "Core/Survey may attach `audit_ref_id`, `candidate_id`, `canonical_entity_ref`, `approved_surface_ref`, `candidate_basis`, family/archetype diagnostic refs, caution flags, and provenance summary to diagnostic artifacts.",
  "",
  "These refs are for PM/debug audit, not normal tester UI copy. They are graph references only and do not create user taste or Atlas role truth."
]);

const activeGraphSongs = currentGraphTaggingCorpus.filter(
  (row) => row.active_in_v1 === true && row.candidate_type === "song"
);
const activeCanonicalGridRows = currentGraphActiveInventory.filter((row) => row.active_in_v1 === true);
const activeGraphPlaybackRows = activeCanonicalGridRows.filter((row) =>
  isPlaybackCandidateType(row.candidate_type)
);
const missionUniverseRows = activeCanonicalGridRows.map((row) => {
  const appleEntry = isPlaybackCandidateType(row.candidate_type)
    ? graphInventoryAppleEntry(row)
    : null;
  const surveyAppleEntry = graphInventoryAnyAppleEntry(row);
  const blocklistRow = inventoryBlocklistRow(row);
  const playbackReady = Boolean(appleEntry);
  const surveyAppleResolved = Boolean(surveyAppleEntry);
  const playbackStatus = isPlaybackCandidateType(row.candidate_type)
    ? playbackReady
      ? "apple_music_catalog_resolved"
      : "do_not_use_no_apple_id"
    : "non_playback_context_object";
  const alphaMissionItemStatus = blocklistRow
    ? "blocked_by_alpha_blocklist"
    : playbackStatus === "do_not_use_no_apple_id"
      ? "do_not_use_no_apple_id"
      : "available";
  const alphaSurveyStatus = blocklistRow
    ? "blocked_by_alpha_blocklist"
    : surveyAppleResolved
      ? "survey_eligible_apple_id_resolved"
      : "survey_unavailable_no_apple_id";
  return {
    mission_item_id: `canonical-grid:${row.v1_membership_id}`,
    mission_item_universe: "canonical_grid",
    canonical_grid_member: true,
    mission_item_available: alphaMissionItemStatus === "available",
    alpha_mission_item_status: alphaMissionItemStatus,
    graph_metadata_taste_truth: false,
    atlas_promotion_created: false,
    candidate_type: row.candidate_type,
    candidate_identity_key: row.candidate_identity_key,
    archetype_membership_key: row.archetype_membership_key,
    display_label: row.title,
    credited_artist: row.artist_display_name,
    release_year: row.year,
    family_name: row.primary_family,
    archetype_id: row.archetype_id,
    archetype_name: row.primary_archetype,
    secondary_archetypes: row.secondary_archetypes || [],
    recognition_band: row.recognition_band,
    mission_role: row.mission_role,
    import_class: row.import_class,
    version_or_composition_risk: row.version_or_composition_risk,
    risk_status: row.risk_status,
    confidence: row.confidence,
    source_file: row.source_file,
    source_membership_id: row.v1_membership_id,
    default_alpha_playback_status: playbackStatus,
    default_alpha_playback_eligible: playbackReady,
    alpha_survey_status: alphaSurveyStatus,
    alpha_survey_eligible: alphaSurveyStatus === "survey_eligible_apple_id_resolved",
    apple_music_catalog_id: appleEntry?.apple_catalog_id || null,
    apple_music_catalog_url: appleEntry?.apple_catalog_url || null,
    apple_music_catalog_match_status: appleEntry?.match_status || null,
    apple_music_catalog_match_basis: appleEntry?.match_basis || null,
    survey_apple_music_catalog_id: surveyAppleEntry?.apple_catalog_id || null,
    survey_apple_music_item_type: surveyAppleEntry?.item_type || null,
    survey_apple_music_catalog_url: surveyAppleEntry?.apple_catalog_url || null,
    survey_apple_music_catalog_match_status: surveyAppleEntry?.match_status || null,
    survey_apple_music_catalog_match_basis: surveyAppleEntry?.match_basis || null,
    allowed_mission_use:
      blocklistRow
        ? "blocked_by_alpha_blocklist"
        : playbackStatus === "apple_music_catalog_resolved"
        ? "available_as_playback_item"
        : playbackStatus === "non_playback_context_object"
          ? "available_as_context_or_selection_item_not_playback"
          : "blocked_for_playback_until_apple_id_resolved",
    do_not_use_status: blocklistRow
      ? "blocked_by_alpha_blocklist"
      : playbackStatus === "do_not_use_no_apple_id"
        ? "do_not_use_no_apple_id"
        : null,
    blocklist_ref: blocklistRow?.block_id || null,
    blocklist_reason: blocklistRow?.reason || null,
    blocked_surfaces: blocklistRow?.blocked_surfaces || []
  };
});

const unmatchedGraphSongs = activeGraphPlaybackRows
  .filter((row) => !graphInventoryAppleEntry(row))
  .map((row) => ({
    status: "do_not_use_no_apple_id",
    object_type: row.candidate_type,
    candidate_identity_key: row.candidate_identity_key,
    display_label: row.title,
    credited_artist: row.artist_display_name,
    family_name: row.primary_family,
    archetype_id: row.archetype_id,
    archetype_name: row.primary_archetype,
    source_file: row.source_file,
    source_membership_id: row.v1_membership_id,
    import_class: row.import_class,
    risk_status: row.risk_status,
    blocked_surfaces: [
      "default_mission_generation",
      "supabase_active_candidate",
      "openai_prompt_payload",
      "app_playback",
      "apple_music_auto_resolution"
    ],
    allowed_surfaces: [
      "canonical_graph",
      "qa_review",
      "manual_resolver_review"
    ],
    reason: "no_apple_music_catalog_id"
  }));

const missionUniversePayload = {
  artifact: "canonical_mission_item_universe",
  version: "alpha_v0",
  alpha_contract_version: "alpha_v0",
  generated_at: new Date().toISOString(),
  status: "canonical_grid_available_for_mission_items_with_playback_gate",
  source_graph_inventory: `${CURRENT_GRAPH}/canonical_graph_active_inventory.json`,
  source_catalog_index: APPLE_CATALOG_INDEX,
  policy: {
    canonical_grid_available_for_mission_items: true,
    compact_candidate_pool_is_not_the_universe: true,
    playback_requires_apple_music_catalog_id: true,
    no_apple_id_status: "do_not_use_no_apple_id",
    graph_metadata_taste_truth: false,
    atlas_promotion_created: false
  },
  summary: {
    canonical_grid_items: activeCanonicalGridRows.length,
    by_candidate_type: countBy(activeCanonicalGridRows, (row) => row.candidate_type),
    playback_candidate_rows: activeGraphPlaybackRows.length,
    playback_candidate_rows_with_apple_id:
      activeGraphPlaybackRows.length - unmatchedGraphSongs.length,
    playback_candidate_rows_do_not_use_no_apple_id: unmatchedGraphSongs.length,
    apple_id_resolved_grid_items: missionUniverseRows.filter((row) => row.survey_apple_music_catalog_id).length,
    alpha_survey_eligible_grid_items: missionUniverseRows.filter((row) => row.alpha_survey_eligible).length,
    alpha_survey_unavailable_no_apple_id: missionUniverseRows.filter(
      (row) => row.alpha_survey_status === "survey_unavailable_no_apple_id"
    ).length,
    alpha_blocklisted_grid_rows: missionUniverseRows.filter(
      (row) => row.alpha_mission_item_status === "blocked_by_alpha_blocklist"
    ).length,
    alpha_available_mission_items: missionUniverseRows.filter((row) => row.mission_item_available).length,
    context_or_selection_rows_not_playback: activeCanonicalGridRows.length - activeGraphPlaybackRows.length
  },
  mission_items: missionUniverseRows
};

writeJson(`${ALPHA}/canonical_mission_item_universe_alpha_v0.json`, missionUniversePayload);

writeMarkdown(`${ALPHA}/canonical_mission_item_universe_alpha_v0.md`, [
  "# Canonical Mission Item Universe Alpha v0",
  "",
  "Alpha contract version: `alpha_v0`",
  "",
  `Generated: ${missionUniversePayload.generated_at}`,
  "",
  `Status: \`${missionUniversePayload.status}\``,
  "",
  "The canonical grid is available as the mission-item universe. The compact candidate pool is a sample/slice for handoff tests, not the size of the graph.",
  "",
  "Playback is a separate gate: playable song/recording items need an Apple Music catalog ID. No-ID rows remain in the graph but are blocked for playback until resolved.",
  "",
  "## Summary",
  "",
  "| metric | count |",
  "| --- | ---: |",
  `| canonical grid items | ${missionUniversePayload.summary.canonical_grid_items} |`,
  `| playback candidate rows | ${missionUniversePayload.summary.playback_candidate_rows} |`,
  `| playback candidate rows with Apple ID | ${missionUniversePayload.summary.playback_candidate_rows_with_apple_id} |`,
  `| playback candidate rows do_not_use_no_apple_id | ${missionUniversePayload.summary.playback_candidate_rows_do_not_use_no_apple_id} |`,
  `| Apple-ID resolved grid items | ${missionUniversePayload.summary.apple_id_resolved_grid_items} |`,
  `| Alpha survey-eligible grid items | ${missionUniversePayload.summary.alpha_survey_eligible_grid_items} |`,
  `| Alpha survey-unavailable no-Apple-ID rows | ${missionUniversePayload.summary.alpha_survey_unavailable_no_apple_id} |`,
  `| alpha blocklisted grid rows | ${missionUniversePayload.summary.alpha_blocklisted_grid_rows} |`,
  `| alpha available mission items | ${missionUniversePayload.summary.alpha_available_mission_items} |`,
  `| context/selection rows not playback | ${missionUniversePayload.summary.context_or_selection_rows_not_playback} |`,
  "",
  "## By Candidate Type",
  "",
  "| candidate_type | count |",
  "| --- | ---: |",
  ...Object.entries(missionUniversePayload.summary.by_candidate_type).map(
    ([key, value]) => `| ${key} | ${value} |`
  ),
  "",
  "## Policy",
  "",
  "- The full canonical grid may be used as mission material.",
  "- Any canonical grid item with an Apple Music catalog ID is eligible for Survey consideration unless blocklisted.",
  "- The compact candidate pool is not the full mission universe.",
  "- Apple Music catalog IDs gate playback, not canonical graph existence.",
  "- `do_not_use_no_apple_id` blocks playback/default generation for that item until resolver work clears it.",
  "- Graph metadata remains reference-only and never user taste."
]);

const unmatchedSurveySongs = activeSurveySongRows
  .map((row) => ({ row, apple_status: surveySongAppleMusicStatus(row) }))
  .filter(({ apple_status }) => apple_status.apple_music_catalog_status !== "resolved")
  .map(({ row, apple_status }) => ({
    status: "do_not_use_no_apple_id",
    object_type: "song_recording",
    candidate_id: row.candidate_id,
    canonical_entity_id: row.canonical_entity_id,
    display_label: row.display_label,
    family_id: row.family_id,
    archetype_ids: row.archetype_ids || [],
    survey_page_role: row.survey_page_role,
    survey_intent: row.survey_intent,
    dedupe_group: row.dedupe_group,
    source_file: row.source_file,
    source_bucket: row.source_bucket,
    source_membership_id: row.source_membership_id || null,
    review_status: row.review_status,
    apple_music_catalog_status: apple_status.apple_music_catalog_status,
    apple_music_catalog_id: apple_status.apple_music_catalog_id,
    alpha_playback_eligible: false,
    blocked_surfaces: [
      "default_mission_generation",
      "supabase_active_candidate",
      "openai_prompt_payload",
      "app_playback",
      "apple_music_auto_resolution"
    ],
    allowed_surfaces: [
      "canonical_graph",
      "survey_source_qa",
      "manual_resolver_review"
    ],
    reason: "no_apple_music_catalog_id"
  }));

const noAppleIdPayload = {
  artifact: "apple_music_unmatched_do_not_use",
  version: "alpha_v0",
  alpha_contract_version: "alpha_v0",
  generated_at: new Date().toISOString(),
  status: "do_not_use_no_apple_id_status_applied",
  source_catalog_index: APPLE_CATALOG_INDEX,
  source_graph_corpus: `${CURRENT_GRAPH}/graph_tagging_corpus.json`,
  source_survey_surface: `${ROOT}/survey_song_candidates_v0_2.json`,
  policy: {
    canonical_rows_remain_in_graph: true,
    no_apple_id_status: "do_not_use_no_apple_id",
    product_use_rule:
      "Rows without an Apple Music catalog ID may remain in the canonical mission universe for QA/resolver visibility but must not feed Survey display, Alpha playback, playback-route selection, Supabase active playback candidates, OpenAI playback payloads, or Apple Music auto-resolution.",
    resolver_rule:
      "Manual resolver work may clear this status by adding a verified Apple Music catalog entry to the app catalog index."
  },
  summary: {
    canonical_grid_rows: activeCanonicalGridRows.length,
    canonical_grid_rows_with_apple_id: missionUniverseRows.filter((row) => row.survey_apple_music_catalog_id).length,
    canonical_grid_rows_do_not_use_no_apple_id: missionUniverseRows.filter(
      (row) => row.alpha_survey_status === "survey_unavailable_no_apple_id"
    ).length,
    active_graph_song_rows: activeGraphSongs.length,
    active_graph_song_rows_with_apple_id: activeGraphSongs.filter((row) =>
      graphSongHasAppleMusic(row.candidate_identity_key)
    ).length,
    active_graph_song_rows_do_not_use_no_apple_id: activeGraphSongs.filter(
      (row) => !graphSongHasAppleMusic(row.candidate_identity_key)
    ).length,
    active_graph_recording_rows: activeGraphPlaybackRows.filter((row) => row.candidate_type === "recording").length,
    active_graph_playback_rows: activeGraphPlaybackRows.length,
    active_graph_playback_rows_with_apple_id:
      activeGraphPlaybackRows.length - unmatchedGraphSongs.length,
    active_graph_playback_rows_do_not_use_no_apple_id: unmatchedGraphSongs.length,
    active_survey_song_candidates: activeSurveySongRows.length,
    active_survey_song_candidates_with_apple_id:
      activeSurveySongRows.length - unmatchedSurveySongs.length,
    active_survey_song_candidates_do_not_use_no_apple_id: unmatchedSurveySongs.length
  },
  grid_unmatched_rows: missionUniverseRows
    .filter((row) => row.alpha_survey_status === "survey_unavailable_no_apple_id")
    .map((row) => ({
      status: "do_not_use_no_apple_id",
      mission_item_id: row.mission_item_id,
      candidate_type: row.candidate_type,
      candidate_identity_key: row.candidate_identity_key,
      display_label: row.display_label,
      credited_artist: row.credited_artist,
      family_name: row.family_name,
      archetype_id: row.archetype_id,
      archetype_name: row.archetype_name,
      source_file: row.source_file,
      source_membership_id: row.source_membership_id,
      blocked_surfaces: [
        "survey_display",
        "app_playback",
        "playback_route_selection",
        "supabase_active_candidate",
        "openai_prompt_payload",
        "apple_music_auto_resolution"
      ],
      allowed_surfaces: ["canonical_graph", "qa_review", "manual_resolver_review"],
      reason: "no_apple_music_catalog_id"
    })),
  graph_unmatched_rows: unmatchedGraphSongs,
  active_survey_unmatched_rows: unmatchedSurveySongs
};

writeJson(`${ALPHA}/apple_music_unmatched_do_not_use_alpha_v0.json`, noAppleIdPayload);

writeMarkdown(`${ALPHA}/apple_music_unmatched_do_not_use_alpha_v0.md`, [
  "# Apple Music Unmatched Do-Not-Use Alpha v0",
  "",
  "Alpha contract version: `alpha_v0`",
  "",
  `Generated: ${noAppleIdPayload.generated_at}`,
  "",
  `Status: \`${noAppleIdPayload.status}\``,
  "",
  "Canonical graph rows stay in the graph. For Alpha playback and default Mission Generation, any song without an Apple Music catalog ID is marked `do_not_use_no_apple_id` until resolver work clears it.",
  "",
  "## Summary",
  "",
  "| metric | count |",
  "| --- | ---: |",
  `| canonical grid rows | ${noAppleIdPayload.summary.canonical_grid_rows} |`,
  `| canonical grid rows with Apple ID | ${noAppleIdPayload.summary.canonical_grid_rows_with_apple_id} |`,
  `| canonical grid rows do_not_use_no_apple_id | ${noAppleIdPayload.summary.canonical_grid_rows_do_not_use_no_apple_id} |`,
  `| active graph song rows | ${noAppleIdPayload.summary.active_graph_song_rows} |`,
  `| active graph song rows with Apple ID | ${noAppleIdPayload.summary.active_graph_song_rows_with_apple_id} |`,
  `| active graph song rows do_not_use_no_apple_id | ${noAppleIdPayload.summary.active_graph_song_rows_do_not_use_no_apple_id} |`,
  `| active graph recording rows | ${noAppleIdPayload.summary.active_graph_recording_rows} |`,
  `| active graph playback rows | ${noAppleIdPayload.summary.active_graph_playback_rows} |`,
  `| active graph playback rows with Apple ID | ${noAppleIdPayload.summary.active_graph_playback_rows_with_apple_id} |`,
  `| active graph playback rows do_not_use_no_apple_id | ${noAppleIdPayload.summary.active_graph_playback_rows_do_not_use_no_apple_id} |`,
  `| active survey song candidates | ${noAppleIdPayload.summary.active_survey_song_candidates} |`,
  `| active survey song candidates with Apple ID | ${noAppleIdPayload.summary.active_survey_song_candidates_with_apple_id} |`,
  `| active survey song candidates do_not_use_no_apple_id | ${noAppleIdPayload.summary.active_survey_song_candidates_do_not_use_no_apple_id} |`,
  "",
  "## Product Rule",
  "",
  noAppleIdPayload.policy.product_use_rule,
  "",
  "The full canonical grid remains the mission-item universe; this file only gates unresolved playback rows.",
  "",
  "## Blocked Surfaces",
  "",
  "- default Mission Generation",
  "- Supabase active candidates",
  "- OpenAI prompt payloads",
  "- app playback",
  "- Apple Music auto-resolution",
  "",
  "## First Survey-Surface Examples",
  "",
  "| candidate_id | family | display | bucket |",
  "| --- | ---: | --- | --- |",
  ...unmatchedSurveySongs
    .slice(0, 30)
    .map((row) => `| ${row.candidate_id} | ${row.family_id} | ${row.display_label} | ${row.source_bucket} |`),
  "",
  "## First Graphwide Examples",
  "",
  "| candidate_identity_key | display | family |",
  "| --- | --- | --- |",
  ...unmatchedGraphSongs
    .slice(0, 30)
    .map((row) => `| ${row.candidate_identity_key} | ${row.credited_artist} - ${row.display_label} | ${row.family_name} |`)
]);
