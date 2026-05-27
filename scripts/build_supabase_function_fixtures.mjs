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

writeCase("app_import_candidate", {
  request: withReplay(request, reviewedGeneration, "fixture_app_import_candidate"),
  expected_contract: {
    status: "app_import_candidate",
    app_missions_returned: true,
    mission_output_schema_version: reviewedGeneration.schema_version,
    app_mission_schema_version: "mission.v0.2",
    source_fixture: "golden_alpha_packet_v0_1",
  },
  golden_response_reference: goldenResponse,
});

writeCase("review_needed", {
  request: withReplay(request, rawGeneration, "fixture_review_needed"),
  expected_contract: {
    status: "review_needed",
    app_missions_returned: true,
    alpha_import_policy: "return_app_valid_missions",
    reason: "source generation is schema-valid but review_config.ready_for_app_import is false; trusted Alpha policy may return app-valid missions with review flags",
    source_fixture: "golden_alpha_packet_v0_1",
  },
});

const blockedGeneration = structuredClone(reviewedGeneration);
blockedGeneration.schema_version = "waymark.mission_output.v999";
writeCase("blocked", {
  request: withReplay(request, blockedGeneration, "fixture_blocked"),
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
