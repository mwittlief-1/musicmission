import fs from "node:fs";

const ROOT = "data/canonical_graph/normalization_pass_2";
const ALPHA = "data/alpha_consumable_layer/alpha_v0";

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
const familyRecommendations = readJson(`${ALPHA}/family_inclusion_recommendation_alpha_v0.json`).families;
const familyById = new Map(familyRecommendations.map((row) => [row.family_id, row]));
const archetypeReadiness = readJson(`${ROOT}/archetype_readiness_v0_2.json`);
const archetypeById = new Map(archetypeReadiness.map((row) => [row.archetype_id, row]));
const recordingVersions = readJson(`${ROOT}/canonical_recording_versions.json`);
const recordingById = new Map(recordingVersions.map((row) => [row.recording_id, row]));

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
    "Expose route-ready candidate safety metadata so Mission Generation/Supabase can store review flags without false hard review gates.",
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
      "object_type not in [track, album]"
    ],
    do_not_hard_block_generation_when: [
      "candidate_safety_state == alpha_safe_with_review_flags",
      "risk_class == medium",
      "risk_class == high with candidate_role in [risky_probe, trap]",
      "resolver_risk_class == album_search_selection",
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
  "Purpose: expose route-ready candidate safety metadata so Mission Generation/Supabase can store review flags without false hard review gates.",
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
  "Hard-block only when a candidate is actually blocked, quarantined, suppressed, manual-review-only, context-only, non-route-ready, or not approved.",
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
        const familyInfo = familyById.get(row.family_id) || {};
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
            raw_graph_row_exposed: false
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
