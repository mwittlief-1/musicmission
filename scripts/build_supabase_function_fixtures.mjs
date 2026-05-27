#!/usr/bin/env node
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = dirname(dirname(fileURLToPath(import.meta.url)));
const packetDir = join(repoRoot, "data/alpha_packets/golden_alpha_packet_v0_1");
const fixtureDir = join(repoRoot, "supabase/functions/generate-first-mission-batch/fixtures");
const sourceFiles = [
  join(packetDir, "request/supabase_generate_first_mission_batch_request.json"),
  join(packetDir, "generation/mission_output_waymark_v0_1.reviewed_app_import_candidate.json"),
  join(packetDir, "generation/mission_output_waymark_v0_1.raw.json"),
  join(packetDir, "response/supabase_generate_first_mission_batch_response.json"),
];

if (sourceFiles.some((path) => !existsSync(path))) {
  const requiredFixtureFiles = [
    join(fixtureDir, "app_import_candidate/request.json"),
    join(fixtureDir, "app_import_candidate/expected_contract.json"),
    join(fixtureDir, "review_needed/request.json"),
    join(fixtureDir, "review_needed/expected_contract.json"),
    join(fixtureDir, "blocked/request.json"),
    join(fixtureDir, "blocked/expected_contract.json"),
    join(fixtureDir, "invalid_input/request.json"),
    join(fixtureDir, "invalid_input/expected_contract.json"),
  ];
  const missingFixture = requiredFixtureFiles.find((path) => !existsSync(path));
  if (missingFixture) {
    throw new Error(`missing fixture source packet and required existing fixture: ${missingFixture}`);
  }
  console.log("Golden packet source not found; keeping existing Supabase function fixtures.");
  process.exit(0);
}

const request = readJson(join(packetDir, "request/supabase_generate_first_mission_batch_request.json"));
const reviewedGeneration = readJson(
  join(packetDir, "generation/mission_output_waymark_v0_1.reviewed_app_import_candidate.json"),
);
const rawGeneration = readJson(join(packetDir, "generation/mission_output_waymark_v0_1.raw.json"));
const goldenResponse = readJson(join(packetDir, "response/supabase_generate_first_mission_batch_response.json"));
const enrichedRequest = enrichRequestRouteIdentity(request);
const reviewedGenerationWithRouteIdentity = enrichGenerationRouteIdentity(
  reviewedGeneration,
  enrichedRequest.candidate_pool,
);
const rawGenerationWithRouteIdentity = enrichGenerationRouteIdentity(rawGeneration, enrichedRequest.candidate_pool);
const goldenResponseWithRouteIdentity = enrichResponseRouteIdentity(goldenResponse, enrichedRequest.candidate_pool);

writeCase("app_import_candidate", {
  request: withReplay(enrichedRequest, reviewedGenerationWithRouteIdentity, "fixture_app_import_candidate"),
  expected_contract: {
    status: "app_import_candidate",
    app_missions_returned: true,
    mission_output_schema_version: reviewedGenerationWithRouteIdentity.schema_version,
    app_mission_schema_version: "mission.v0.2",
    source_fixture: "golden_alpha_packet_v0_1",
  },
  golden_response_reference: goldenResponseWithRouteIdentity,
});

writeCase("review_needed", {
  request: withReplay(enrichedRequest, rawGenerationWithRouteIdentity, "fixture_review_needed"),
  expected_contract: {
    status: "review_needed",
    app_missions_returned: true,
    alpha_import_policy: "return_app_valid_missions",
    reason: "source generation is schema-valid but review_config.ready_for_app_import is false; trusted Alpha policy may return app-valid missions with review flags",
    source_fixture: "golden_alpha_packet_v0_1",
  },
});

const blockedGeneration = structuredClone(reviewedGenerationWithRouteIdentity);
blockedGeneration.schema_version = "waymark.mission_output.v999";
writeCase("blocked", {
  request: withReplay(enrichedRequest, blockedGeneration, "fixture_blocked"),
  expected_contract: {
    status: "blocked",
    app_missions_returned: false,
    reason: "replay generation schema_version intentionally mismatches the Edge Function contract",
    source_fixture: "golden_alpha_packet_v0_1",
  },
});

writeCase("invalid_input", {
  request: {
    client_request_id: "fixture-invalid-input",
    requested_batch_size: 0,
    survey_evidence_export: null,
    mission_generation_digest_view: null,
  },
  expected_contract: {
    http_status: 400,
    error: "invalid_input",
    app_missions_returned: false,
  },
});

console.log(`Wrote Supabase function fixtures to ${fixtureDir}`);

function withReplay(baseRequest, replayGeneration, clientRequestID) {
  return {
    ...baseRequest,
    client_request_id: clientRequestID,
    prompt_context: {
      ...(baseRequest.prompt_context ?? {}),
      generation_mode: "fixture_replay",
      fixture_source: "golden_alpha_packet_v0_1",
    },
    replay_generation_output: replayGeneration,
  };
}

function enrichRequestRouteIdentity(baseRequest) {
  const enrichedRequest = structuredClone(baseRequest);
  enrichedRequest.candidate_pool = enrichCandidatePool(enrichedRequest.candidate_pool);
  return enrichedRequest;
}

function enrichCandidatePool(value) {
  if (Array.isArray(value)) {
    return value.map((child) => enrichCandidatePool(child));
  }
  if (!isObject(value)) {
    return value;
  }

  const cloned = Object.fromEntries(
    Object.entries(value).map(([key, child]) => [key, enrichCandidatePool(child)]),
  );
  if (!cleanString(cloned.candidate_id)) {
    return cloned;
  }

  const identity = routeIdentityFor(cloned);
  cloned.app_route_item_id = firstNonEmptyString(cloned.app_route_item_id, identity.app_route_item_id);
  cloned.route_candidate_key = firstNonEmptyString(cloned.route_candidate_key, identity.route_candidate_key);
  cloned.route_batch_dedupe_key = firstNonEmptyString(cloned.route_batch_dedupe_key, identity.route_batch_dedupe_key);
  cloned.route_display_identity_key = firstNonEmptyString(
    cloned.route_display_identity_key,
    identity.route_display_identity_key,
  );
  return cloned;
}

function enrichGenerationRouteIdentity(generation, candidatePool) {
  const enrichedGeneration = structuredClone(generation);
  if (!isObject(enrichedGeneration.route) || !Array.isArray(enrichedGeneration.route.items)) {
    return enrichedGeneration;
  }

  const candidateMetadata = candidateMetadataFromPool(candidatePool);
  enrichedGeneration.route.items = enrichedGeneration.route.items.map((item) => {
    if (!isObject(item)) {
      return item;
    }

    const candidateID = cleanString(item.candidate_id);
    const candidate = candidateID ? candidateMetadata.get(candidateID) : undefined;
    const identity = routeIdentityFor(item, candidate);
    return {
      ...item,
      route_candidate_key: firstNonEmptyString(
        item.route_candidate_key,
        candidate?.route_candidate_key,
        identity.route_candidate_key,
      ),
      route_batch_dedupe_key: firstNonEmptyString(
        item.route_batch_dedupe_key,
        candidate?.route_batch_dedupe_key,
        identity.route_batch_dedupe_key,
      ),
      route_display_identity_key: firstNonEmptyString(
        item.route_display_identity_key,
        candidate?.route_display_identity_key,
        identity.route_display_identity_key,
      ),
    };
  });
  return enrichedGeneration;
}

function enrichResponseRouteIdentity(response, candidatePool) {
  const enrichedResponse = structuredClone(response);
  if (isObject(enrichedResponse.generation)) {
    enrichedResponse.generation = enrichGenerationRouteIdentity(enrichedResponse.generation, candidatePool);
  }

  if (!Array.isArray(enrichedResponse.app_missions)) {
    return enrichedResponse;
  }

  const candidateMetadata = candidateMetadataFromPool(candidatePool);
  const routeItemsByCandidateID = routeItemsByCandidate(enrichedResponse.generation);
  enrichedResponse.app_missions = enrichedResponse.app_missions.map((mission) => {
    if (!isObject(mission) || !Array.isArray(mission.items)) {
      return mission;
    }
    return {
      ...mission,
      items: mission.items.map((item) => enrichAppMissionItemRouteIdentity(item, candidateMetadata, routeItemsByCandidateID)),
    };
  });
  return enrichedResponse;
}

function enrichAppMissionItemRouteIdentity(item, candidateMetadata, routeItemsByCandidateID) {
  if (!isObject(item)) {
    return item;
  }

  const candidateID = cleanString(item.candidate_id);
  const candidate = candidateID ? candidateMetadata.get(candidateID) : undefined;
  const routeItem = candidateID ? routeItemsByCandidateID.get(candidateID) : undefined;
  const identity = routeIdentityFor({ ...(routeItem ?? {}), ...item }, candidate);
  return {
    ...item,
    route_candidate_key: firstNonEmptyString(
      item.route_candidate_key,
      routeItem?.route_candidate_key,
      candidate?.route_candidate_key,
      identity.route_candidate_key,
    ),
    route_batch_dedupe_key: firstNonEmptyString(
      item.route_batch_dedupe_key,
      routeItem?.route_batch_dedupe_key,
      candidate?.route_batch_dedupe_key,
      identity.route_batch_dedupe_key,
    ),
    route_display_identity_key: firstNonEmptyString(
      item.route_display_identity_key,
      routeItem?.route_display_identity_key,
      candidate?.route_display_identity_key,
      identity.route_display_identity_key,
    ),
  };
}

function routeItemsByCandidate(generation) {
  const items = isObject(generation?.route) && Array.isArray(generation.route.items) ? generation.route.items : [];
  const byCandidateID = new Map();
  for (const item of items) {
    if (!isObject(item)) {
      continue;
    }
    const candidateID = cleanString(item.candidate_id);
    if (candidateID) {
      byCandidateID.set(candidateID, item);
    }
  }
  return byCandidateID;
}

function candidateMetadataFromPool(value, metadata = new Map()) {
  if (Array.isArray(value)) {
    for (const child of value) candidateMetadataFromPool(child, metadata);
    return metadata;
  }
  if (!isObject(value)) {
    return metadata;
  }

  const candidateID = cleanString(value.candidate_id);
  if (candidateID) {
    metadata.set(candidateID, value);
  }
  for (const child of Object.values(value)) candidateMetadataFromPool(child, metadata);
  return metadata;
}

function routeIdentityFor(value, fallback = {}) {
  const itemType = identitySlug(firstNonEmptyString(value.item_type, fallback?.item_type, "track")) ?? "track";
  const artistSlug = identitySlug(firstNonEmptyString(
    value.artist,
    value.display_metadata?.artist,
    value.music_kit_search_hint?.artist,
    fallback?.artist,
    fallback?.display_metadata?.artist,
    fallback?.music_kit_search_hint?.artist,
  )) ?? "unknown-artist";
  const candidateID = firstNonEmptyString(value.candidate_id, fallback?.candidate_id);
  const titleSlug = identitySlug(firstNonEmptyString(
    value.title,
    value.display_metadata?.title,
    value.music_kit_search_hint?.title,
    fallback?.title,
    fallback?.display_metadata?.title,
    fallback?.music_kit_search_hint?.title,
  )) ?? identitySlug(candidateID) ?? "unknown-title";
  const keyStem = `${artistSlug}-${titleSlug}`;

  return {
    app_route_item_id: [
      "ITEM_ALPHA",
      appIDToken(itemType),
      appIDToken(artistSlug),
      appIDToken(titleSlug),
      appIDToken(candidateID ?? keyStem),
    ].join("_"),
    route_candidate_key: `route:${itemType}:${keyStem}`,
    route_batch_dedupe_key: `${itemType}:${keyStem}`,
    route_display_identity_key: `${itemType}:${artistSlug}:${titleSlug}`,
  };
}

function firstNonEmptyString(...values) {
  for (const value of values) {
    const text = cleanString(value);
    if (text) {
      return text;
    }
  }
  return null;
}

function cleanString(value) {
  return typeof value === "string" && value.trim().length > 0 ? value.trim() : null;
}

function identitySlug(value) {
  const text = cleanString(value);
  if (!text) {
    return null;
  }
  const normalized = text
    .toLowerCase()
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return normalized.length > 0 ? normalized : null;
}

function appIDToken(value) {
  const text = cleanString(value);
  if (!text) {
    return "UNKNOWN";
  }
  const token = text
    .toUpperCase()
    .replace(/[^A-Z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "");
  return token.length > 0 ? token : "UNKNOWN";
}

function isObject(value) {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function writeCase(caseName, files) {
  const outDir = join(fixtureDir, caseName);
  mkdirSync(outDir, { recursive: true });
  for (const [filename, value] of Object.entries(files)) {
    writeJson(join(outDir, `${filename}.json`), value);
  }
}

function readJson(path) {
  return JSON.parse(readFileSync(path, "utf8"));
}

function writeJson(path, value) {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, `${JSON.stringify(value, null, 2)}\n`);
}
