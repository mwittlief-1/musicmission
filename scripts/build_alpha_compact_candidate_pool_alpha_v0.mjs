import crypto from "node:crypto";
import fs from "node:fs";

const ROOT = "data/canonical_graph/normalization_pass_2";
const IMPORT_DRY_RUN = "data/canonical_graph/import_dry_run";
const ALPHA = "data/alpha_consumable_layer/alpha_v0";

const args = new Map();
for (let i = 2; i < process.argv.length; i += 1) {
  const arg = process.argv[i];
  if (arg.startsWith("--")) {
    args.set(arg.slice(2), process.argv[i + 1] && !process.argv[i + 1].startsWith("--") ? process.argv[++i] : true);
  }
}

const output = args.get("output") || `${ALPHA}/sample_compact_candidate_pool_alpha_v0.json`;
const maxPerPool = Number(args.get("max-per-pool") || 12);
const familyFilter = args.get("family")
  ? new Set(String(args.get("family")).split(",").map((value) => Number(value.trim())))
  : null;

function readJson(path) {
  return JSON.parse(fs.readFileSync(path, "utf8"));
}

const familyRecommendations = readJson(`${ALPHA}/family_inclusion_recommendation_alpha_v0.json`).families;
const eligibleFamilies = new Set(
  familyRecommendations
    .filter((row) => row.default_first_mission_allowed)
    .map((row) => row.family_id)
);
const familyCautions = new Map(
  familyRecommendations.map((row) => [row.family_id, row.caution_flags || []])
);

const blocklist = readJson(`${ALPHA}/alpha_candidate_blocklist_alpha_v0.json`).blocklist || [];
const blockedCandidateIds = new Set(blocklist.map((row) => row.source_candidate_id));
const blockedTypedRefs = new Set(blocklist.map((row) => row.entity_ref));

const recordingVersions = readJson(`${ROOT}/canonical_recording_versions.json`);
const recordingById = new Map(recordingVersions.map((row) => [row.recording_id, row]));
const canonicalAlbums = readJson(`${IMPORT_DRY_RUN}/canonical_albums.json`);
const albumById = new Map(canonicalAlbums.map((row) => [row.canonical_album_id, row]));
const canonicalSongs = readJson(`${IMPORT_DRY_RUN}/canonical_song_recordings.json`);
const songById = new Map(canonicalSongs.map((row) => [row.canonical_song_recording_id, row]));
const deadEndProbes = readJson(`${ROOT}/dead_end_probe_candidates_v0_2.json`);
const deadEndProbeByTypedRef = new Map(
  deadEndProbes.map((row) => [`${row.entity_type}:${row.entity_id}`, row])
);

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
  if (version.review_status !== "approved" || version.survey_safe !== true) return "needs_review";
  const context = version.recording_context || "unknown";
  if (context === "original" || context === "album_version" || context === "single_version") {
    return "no_review_needed";
  }
  return "split_confirmed";
}

function musicObjectRef(row) {
  const version =
    row.object_type === "song_recording" ? recordingById.get(row.canonical_entity_id) : null;
  return {
    object_type: row.object_type,
    ref_source: "canonical_graph",
    canonical_artist_id: null,
    canonical_album_id: row.object_type === "album" ? row.canonical_entity_id : null,
    canonical_song_recording_id:
      row.object_type === "song_recording" ? row.canonical_entity_id : null,
    composition_placeholder_id: null,
    user_music_object_id: null,
    external_catalog_refs: {},
    display_name: row.display_label,
    credited_artist_name: creditedArtist(row),
    credit_context: "route_candidate",
    resolution_state: "resolved",
    composition_policy_status:
      row.object_type === "song_recording"
        ? compositionPolicyStatusForVersion(version)
        : "not_applicable",
    recording_variant_type:
      row.object_type === "song_recording"
        ? recordingVariantByContext[version?.recording_context] || "unknown"
        : null,
    canonical_membership_context: {
      family_numbers: [row.family_id],
      archetype_ids: row.archetype_ids || [],
      membership_role_notes: "Graph membership context only; not user taste."
    }
  };
}

function routeItemType(row) {
  if (row.object_type === "song_recording") return "track";
  if (row.object_type === "album") return "album";
  return "unsupported";
}

function creditedArtist(row) {
  if (row.object_type === "song_recording") {
    const version = recordingById.get(row.canonical_entity_id);
    const canonical = songById.get(row.canonical_entity_id);
    return version?.display_artist_credit || canonical?.artist_names?.join(", ") || null;
  }
  if (row.object_type === "album") {
    const canonical = albumById.get(row.canonical_entity_id);
    return canonical?.artist_names?.join(", ") || null;
  }
  return null;
}

function appleMusicResolutionPolicy(row) {
  if (row.object_type === "song_recording") {
    return (
      recordingById.get(row.canonical_entity_id)?.apple_music_resolution_policy ||
      "manual_review_required"
    );
  }
  return "search_selection_required";
}

function versionRiskNote(row) {
  if (row.object_type === "album") return "album_search_selection_required";
  const version = recordingById.get(row.canonical_entity_id);
  if (!version) return "missing_recording_version_sidecar";
  if (version.apple_music_resolution_policy === "manual_review_required") {
    return "manual_review_required";
  }
  return "exact_recording_required";
}

function musicKitSearchHint(row) {
  const artist = creditedArtist(row);
  if (row.object_type === "album") {
    return artist ? `${artist} ${row.display_label} album` : `${row.display_label} album`;
  }
  return artist ? `${artist} ${row.display_label}` : row.display_label;
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

function appSafeSlug(value) {
  return String(value || "")
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toUpperCase()
    .replace(/[^A-Z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "");
}

function shortHash(value) {
  return crypto.createHash("sha1").update(String(value)).digest("hex").slice(0, 8).toUpperCase();
}

function routeCandidateKey(routeType, canonicalObjectType, canonicalEntityId) {
  return `route:${routeType}:${canonicalObjectType}:${canonicalEntityId}`;
}

function routeBatchDedupeKey(row, routeType) {
  return row.dedupe_group || `${routeType}:${row.object_type}:${row.canonical_entity_id}`;
}

function routeDisplayIdentityKey(routeType, artist, displayName) {
  return [routeType, artist, displayName].map(normalizedIdentityPart).join(":");
}

function appRouteItemId(routeType, canonicalObjectType, canonicalEntityId) {
  const key = routeCandidateKey(routeType, canonicalObjectType, canonicalEntityId);
  const slug = appSafeSlug(`${routeType}_${canonicalEntityId}`).slice(0, 43);
  return `ITEM_ALPHA_${slug}_${shortHash(key)}`;
}

function sourceFileFor(type) {
  if (type === "album") return "survey_album_candidates_v0_2.json";
  return "survey_song_candidates_v0_2.json";
}

function allowed(row) {
  if (!["album", "song_recording"].includes(row.object_type)) return false;
  if (!eligibleFamilies.has(row.family_id)) return false;
  if (familyFilter && !familyFilter.has(row.family_id)) return false;
  if (row.review_status !== "approved") return false;
  if (row.quarantine_reasons?.length) return false;
  const typedRef = `${row.object_type}:${row.canonical_entity_id}`;
  if (blockedCandidateIds.has(row.candidate_id) || blockedTypedRefs.has(typedRef)) return false;
  if (row.object_type === "song_recording") {
    const version = recordingById.get(row.canonical_entity_id);
    if (!version || version.review_status !== "approved" || version.survey_safe !== true) return false;
    if (version.apple_music_resolution_policy === "manual_review_required") return false;
  }
  if (row.object_type === "album" && !albumById.has(row.canonical_entity_id)) return false;
  return routeItemType(row) !== "unsupported";
}

function riskFor(row, candidateRole) {
  const cautions = familyCautions.get(row.family_id) || [];
  if (candidateRole === "trap" || candidateRole === "risky_probe") return "high";
  if (cautions.length) return "medium";
  return "low";
}

function reviewMetadata(row, candidateRole, riskClass) {
  const cautionFlags = familyCautions.get(row.family_id) || [];
  const reviewRiskFlags = [];
  if (cautionFlags.length) reviewRiskFlags.push(...cautionFlags);
  if (candidateRole === "risky_probe") reviewRiskFlags.push("boundary_probe_use_with_care");
  if (candidateRole === "trap") reviewRiskFlags.push("dead_end_check_store_as_probe_not_conclusion");
  if (row.object_type === "album") reviewRiskFlags.push("album_search_selection_required");
  if (row.object_type === "song_recording") reviewRiskFlags.push(versionRiskNote(row));

  const needsReviewFlags =
    riskClass !== "low" || reviewRiskFlags.includes("album_search_selection_required");

  return {
    candidate_safety_state: needsReviewFlags
      ? "alpha_safe_with_review_flags"
      : "alpha_safe_default",
    review_gate_status: "eligible_for_default_alpha_generation",
    review_gate_action: needsReviewFlags
      ? "generate_allowed_store_review_flags"
      : "generate_allowed",
    default_alpha_mission_eligible: true,
    hard_block: false,
    blocked_reason: null,
    quarantine_status: "clear",
    suppression_status: "active",
    resolver_risk_class: row.object_type === "album" ? "album_search_selection" : versionRiskNote(row),
    review_risk_flags: [...new Set(reviewRiskFlags)],
    context_only: false,
    manual_review_required: false,
    trusted_alpha_import_note:
      "Candidate may feed generation; app import still requires valid mission.v0.2 and stored review/audit flags."
  };
}

function familiarityFor(row, bucket, candidateRole) {
  if (candidateRole === "waypoint") return "likely_known_or_contextual";
  if (bucket === "page1_core") return "likely_known";
  return "unknown";
}

function sourceEvidenceRefs(row) {
  const refs = [
    { ref_type: "survey_candidate", ref_id: row.candidate_id },
    { ref_type: "source_membership", ref_id: row.source_membership_id || null }
  ].filter((ref) => ref.ref_id);
  const probe = deadEndProbeByTypedRef.get(`${row.object_type}:${row.canonical_entity_id}`);
  if (probe) refs.push({ ref_type: "dead_end_probe", ref_id: probe.probe_id });
  return refs;
}

function sourceEvidenceSummary(row, candidateRole) {
  if (candidateRole === "trap") {
    return "Derived from approved false-nearby/dead-end probe material; requires user signal before any Atlas Dead End.";
  }
  if (candidateRole === "risky_probe") {
    return "Derived from approved boundary material; useful for testing route edges without treating failure as conclusion.";
  }
  return `Derived from approved ${row.survey_page_role} ${row.object_type} candidate surface.`;
}

function toCandidate(row, bucket, candidateRole, poolName) {
  const risk = riskFor(row, candidateRole);
  const review = reviewMetadata(row, candidateRole, risk);
  const ref = musicObjectRef(row);
  const routeType = routeItemType(row);
  const artist = creditedArtist(row);
  const searchHint = musicKitSearchHint(row);
  const routeKey = routeCandidateKey(routeType, row.object_type, row.canonical_entity_id);
  const batchDedupeKey = routeBatchDedupeKey(row, routeType);
  const displayIdentityKey = routeDisplayIdentityKey(routeType, artist, row.display_label);
  const stableItemId = appRouteItemId(routeType, row.object_type, row.canonical_entity_id);
  return {
    candidate_id: row.candidate_id,
    route_candidate_key: routeKey,
    route_batch_dedupe_key: batchDedupeKey,
    route_display_identity_key: displayIdentityKey,
    app_route_item_id: stableItemId,
    candidate_role: candidateRole,
    mission_candidate_role: candidateRole,
    candidate_pool_behavior: candidateRole,
    route_item_type: routeType,
    playable_route_ready: true,
    artist_level_candidate: false,
    object_type: routeType,
    canonical_object_type: row.object_type,
    canonical_entity_id: row.canonical_entity_id,
    music_object_ref: ref,
    display_name: row.display_label,
    display_label: row.display_label,
    credited_artist: artist,
    family_id: row.family_id,
    archetype_ids: row.archetype_ids || [],
    survey_page_role: row.survey_page_role,
    survey_intent: row.survey_intent,
    dedupe_group: row.dedupe_group,
    priority_score: row.priority_score,
    trigger_rule: row.trigger_rule,
    why_selected: `${candidateRole} route-ready ${routeType} from ${bucket} ${row.object_type} surface`,
    expected_signal: `tests ${row.survey_intent} response without creating Atlas truth`,
    risk_class: risk,
    candidate_safety_state: review.candidate_safety_state,
    review_gate_status: review.review_gate_status,
    review_gate_action: review.review_gate_action,
    default_alpha_mission_eligible: review.default_alpha_mission_eligible,
    hard_block: review.hard_block,
    blocked_reason: review.blocked_reason,
    quarantine_status: review.quarantine_status,
    suppression_status: review.suppression_status,
    resolver_risk_class: review.resolver_risk_class,
    review_risk_flags: review.review_risk_flags,
    context_only: review.context_only,
    manual_review_required: review.manual_review_required,
    trusted_alpha_import_note: review.trusted_alpha_import_note,
    familiarity_assumption: familiarityFor(row, bucket, candidateRole),
    positive_inference: row.positive_inference,
    negative_inference: row.negative_inference,
    do_not_infer: row.do_not_infer,
    music_kit_search_hint: searchHint,
    music_kit_resolution_status: "search_required",
    apple_music_resolution_policy: appleMusicResolutionPolicy(row),
    version_risk_note: versionRiskNote(row),
    route_item: {
      item_id: stableItemId,
      candidate_id: row.candidate_id,
      route_candidate_key: routeKey,
      route_batch_dedupe_key: batchDedupeKey,
      route_display_identity_key: displayIdentityKey,
      route_item_type: routeType,
      display_name: row.display_label,
      credited_artist: artist,
      canonical_entity_id: row.canonical_entity_id,
      canonical_object_type: row.object_type,
      music_object_ref: ref,
      music_kit_search_hint: searchHint,
      apple_music_resolution_policy: appleMusicResolutionPolicy(row),
      version_risk_note: versionRiskNote(row)
    },
    source_file: sourceFileFor(row.object_type),
    source_contract_version: "alpha_v0",
    source_membership_id: row.source_membership_id,
    source_evidence_refs: sourceEvidenceRefs(row),
    source_evidence_summary: sourceEvidenceSummary(row, candidateRole),
    atlas_role_refs: [],
    atlas_role_ref_status: "none_graph_metadata_reference_only",
    review_status: row.review_status,
    eligible_for_supabase: true,
    eligible_for_openai: true,
    source_pool: poolName
  };
}

function loadRows() {
  const rows = [];
  for (const [objectType, file] of [
    ["album", "survey_album_candidates_v0_2.json"],
    ["song_recording", "survey_song_candidates_v0_2.json"]
  ]) {
    const data = readJson(`${ROOT}/${file}`);
    for (const family of Object.values(data.families)) {
      for (const bucket of ["page1_core", "page2_adaptive", "page3_deep"]) {
        for (const row of family[bucket] || []) {
          if (row.object_type !== objectType) continue;
          if (!allowed(row)) continue;
          rows.push({ row, bucket });
        }
      }
    }
  }
  return rows;
}

function sortRows(rows, typePreference) {
  const typeRank = new Map(typePreference.map((type, index) => [type, index]));
  return [...rows].sort((a, b) => {
    const typeDelta =
      (typeRank.get(a.row.object_type) ?? 99) - (typeRank.get(b.row.object_type) ?? 99);
    if (typeDelta !== 0) return typeDelta;
    const priorityDelta = Number(b.row.priority_score || 0) - Number(a.row.priority_score || 0);
    if (priorityDelta !== 0) return priorityDelta;
    return a.row.candidate_id.localeCompare(b.row.candidate_id);
  });
}

function roundRobinByFamily(rows) {
  const grouped = new Map();
  for (const item of rows) {
    const group = grouped.get(item.row.family_id) || [];
    group.push(item);
    grouped.set(item.row.family_id, group);
  }
  const families = [...grouped.keys()].sort((a, b) => a - b);
  const result = [];
  let pulled = true;
  while (pulled) {
    pulled = false;
    for (const familyId of families) {
      const group = grouped.get(familyId);
      if (group?.length) {
        result.push(group.shift());
        pulled = true;
      }
    }
  }
  return result;
}

function routeSelectionKeys(row) {
  const routeType = routeItemType(row);
  return [
    routeBatchDedupeKey(row, routeType),
    routeCandidateKey(routeType, row.object_type, row.canonical_entity_id),
    routeDisplayIdentityKey(routeType, creditedArtist(row), row.display_label)
  ].filter(Boolean);
}

function selectPool(allRows, definition, seenRouteIdentityKeys) {
  const candidates = allRows.filter(({ row, bucket }) => definition.filter(row, bucket));
  const sorted = roundRobinByFamily(sortRows(candidates, definition.typePreference));
  const selected = [];
  for (const item of sorted) {
    const routeKeys = routeSelectionKeys(item.row);
    if (routeKeys.some((key) => seenRouteIdentityKeys.has(key))) continue;
    selected.push(toCandidate(item.row, item.bucket, definition.candidateRole, definition.poolName));
    for (const key of routeKeys) seenRouteIdentityKeys.add(key);
    if (selected.length >= maxPerPool) break;
  }
  return selected;
}

const allRows = loadRows();
const seenRouteIdentityKeys = new Set();

const poolDefinitions = [
  {
    poolName: "anchors",
    candidateRole: "anchor",
    typePreference: ["song_recording", "album"],
    filter: (row, bucket) =>
      bucket === "page1_core" &&
      ["recognition_anchor", "song_first_memory", "album_world_test"].includes(row.survey_intent)
  },
  {
    poolName: "bridges",
    candidateRole: "bridge",
    typePreference: ["song_recording", "album"],
    filter: (row, bucket) =>
      row.survey_intent === "bridge_test" ||
      (bucket === "page2_adaptive" && !["boundary_test", "false_nearby_test"].includes(row.survey_intent))
  },
  {
    poolName: "probes",
    candidateRole: "probe",
    typePreference: ["album", "song_recording"],
    filter: (row, bucket) =>
      bucket === "page3_deep" &&
      !["boundary_test", "false_nearby_test", "do_not_survey"].includes(row.survey_intent)
  },
  {
    poolName: "boundary_probes",
    candidateRole: "risky_probe",
    typePreference: ["song_recording", "album"],
    filter: (row) => row.survey_intent === "boundary_test"
  },
  {
    poolName: "dead_end_checks",
    candidateRole: "trap",
    typePreference: ["song_recording", "album"],
    filter: (row) => row.survey_intent === "false_nearby_test"
  },
  {
    poolName: "waypoints",
    candidateRole: "waypoint",
    typePreference: ["album", "song_recording"],
    filter: (row, bucket) =>
      bucket !== "page1_core" &&
      ["song_first_memory", "album_world_test"].includes(row.survey_intent)
  }
];

const pools = {};
for (const definition of poolDefinitions) {
  pools[definition.poolName] = selectPool(allRows, definition, seenRouteIdentityKeys);
}

const routeReadyCount = Object.values(pools)
  .flat()
  .filter((row) => row.playable_route_ready && ["track", "album"].includes(row.object_type)).length;

const payload = {
  artifact: "compact_candidate_pool",
  version: "alpha_v0",
  generated_at: new Date().toISOString(),
  source_contract: "data/product_contracts/app_local_candidate_pool_contract_alpha_v0.md",
  source_surfaces: [
    `${ROOT}/survey_album_candidates_v0_2.json`,
    `${ROOT}/survey_song_candidates_v0_2.json`
  ],
  note: "Route-ready graph-only sample/export helper output. User-specific Survey/Atlas evidence should further select and rank this pool.",
  route_readiness_status: "route_ready_track_album_candidates",
  resolves_blocker: "MGN-I004",
  graph_metadata_taste_truth: false,
  atlas_promotion_created: false,
  artist_level_candidates_in_route_pools: false,
  resolver_step_required_before_playback: true,
  route_ready_object_types: ["track", "album"],
  route_ready_candidate_count: routeReadyCount,
  max_per_pool: maxPerPool,
  pools
};

fs.writeFileSync(output, JSON.stringify(payload, null, 2) + "\n");
console.log(output);
