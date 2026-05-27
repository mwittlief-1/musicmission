#!/usr/bin/env node
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { dirname } from "node:path";

const repoRoot = dirname(dirname(fileURLToPath(import.meta.url)));
const fixtureRoot = join(repoRoot, "supabase/functions/generate-first-mission-batch/fixtures");
const evidenceFixtureRoot = join(repoRoot, "supabase/functions/submit-alpha-evidence/fixtures");
const diagnosticFixtureRoot = join(repoRoot, "supabase/functions/submit-alpha-diagnostic/fixtures");
const migrationPath = join(repoRoot, "supabase/migrations/20260521160000_alpha_generation_logs.sql");
const alpha1MigrationPath = join(repoRoot, "supabase/migrations/20260522190000_alpha1_auth_and_evidence_upload.sql");
const diagnosticsMigrationPath = join(repoRoot, "supabase/migrations/20260524170000_alpha_client_diagnostics.sql");
const envExamplePath = join(repoRoot, "supabase/functions/.env.example");
const configPath = join(repoRoot, "supabase/config.toml");

const requiredCases = [
  "app_import_candidate",
  "review_needed",
  "blocked",
  "duplicate_item_id",
  "non_candidate_item",
  "batch_memory_repeat",
  "invalid_input",
];
const errors = [];

for (const caseName of requiredCases) {
  const requestPath = join(fixtureRoot, caseName, "request.json");
  const expectedPath = join(fixtureRoot, caseName, "expected_contract.json");
  if (!existsSync(requestPath)) errors.push(`missing fixture request: ${requestPath}`);
  if (!existsSync(expectedPath)) errors.push(`missing expected contract: ${expectedPath}`);
}

if (errors.length === 0) {
  checkReplayCase("app_import_candidate", "app_import_candidate", true);
  checkReplayCase("review_needed", "review_needed", true);
  checkReplayCase("blocked", "blocked", false);
  checkReplayCase("duplicate_item_id", "blocked", false);
  checkReplayCase("non_candidate_item", "blocked", false);
  checkReplayCase("batch_memory_repeat", "blocked", false);
  checkInvalidInputCase();
  checkEvidenceUploadFixtures();
  checkDiagnosticUploadFixtures();
}

checkMigration();
checkEnvExample();
checkConfig();

if (errors.length > 0) {
  console.error("Supabase function smoke failed:");
  for (const error of errors) console.error(`- ${error}`);
  process.exit(1);
}

console.log("SUPABASE_FUNCTION_SMOKE_PASS");

function checkReplayCase(caseName, expectedStatus, expectsAppMissions) {
  const request = readFixture(caseName, "request");
  const expected = readFixture(caseName, "expected_contract");
  if (expected.status !== expectedStatus) {
    errors.push(`${caseName}: expected_contract.status must be ${expectedStatus}`);
  }
  if (expected.app_missions_returned !== expectsAppMissions) {
    errors.push(`${caseName}: expected_contract.app_missions_returned mismatch`);
  }
  if (!isObject(request.survey_evidence_export)) {
    errors.push(`${caseName}: request.survey_evidence_export must be object`);
  }
  if (!isObject(request.mission_generation_digest_view)) {
    errors.push(`${caseName}: request.mission_generation_digest_view must be object`);
  }
  checkCandidateRouteIdentityFields(caseName, request.candidate_pool);
  if (!isObject(request.replay_generation_output)) {
    errors.push(`${caseName}: replay_generation_output must be object`);
    return;
  }
  checkReplayRouteIdentityFields(caseName, request.replay_generation_output, request.candidate_pool);

  const replayStatus = deriveReplayStatus(request.replay_generation_output, request.candidate_pool, request.prompt_context);
  if (replayStatus !== expectedStatus) {
    errors.push(`${caseName}: derived replay status ${replayStatus} did not match ${expectedStatus}`);
  }
}

function checkInvalidInputCase() {
  const request = readFixture("invalid_input", "request");
  const expected = readFixture("invalid_input", "expected_contract");
  if (expected.error !== "invalid_input") {
    errors.push("invalid_input: expected_contract.error must be invalid_input");
  }
  if (isObject(request.survey_evidence_export)) {
    errors.push("invalid_input: fixture should not include valid survey_evidence_export");
  }
}

function checkCandidateRouteIdentityFields(caseName, candidatePool) {
  const candidates = Array.isArray(candidatePool?.candidates) ? candidatePool.candidates : [];
  for (const [index, candidate] of candidates.entries()) {
    for (const field of routeIdentityFields()) {
      if (!cleanString(candidate?.[field])) {
        errors.push(`${caseName}: candidate_pool.candidates[${index}].${field} must be non-empty`);
      }
    }
  }
}

function checkReplayRouteIdentityFields(caseName, generation, candidatePool) {
  const candidateIDs = candidateIDsFromPool(candidatePool);
  const items = isObject(generation.route) && Array.isArray(generation.route.items)
    ? generation.route.items.filter(isObject)
    : [];
  for (const [index, item] of items.entries()) {
    const candidateID = cleanString(item.candidate_id);
    if (!candidateID || !candidateIDs.has(candidateID)) continue;
    for (const field of ["route_candidate_key", "route_batch_dedupe_key", "route_display_identity_key"]) {
      if (!cleanString(item[field])) {
        errors.push(`${caseName}: replay_generation_output.route.items[${index}].${field} must be non-empty`);
      }
    }
  }
}

function routeIdentityFields() {
  return ["app_route_item_id", "route_candidate_key", "route_batch_dedupe_key", "route_display_identity_key"];
}

function deriveReplayStatus(generation, candidatePool = {}, promptContext = {}) {
  if (generation.schema_version !== "waymark.mission_output.v0.1") {
    return "blocked";
  }
  if (!isObject(generation.route) || !Array.isArray(generation.route.items) || generation.route.items.length === 0) {
    return "blocked";
  }
  if (!isObject(generation.review_config)) {
    return "blocked";
  }
  if (!routeIdentityIsValid(generation, candidatePool, promptContext)) {
    return "blocked";
  }
  return generation.review_config.ready_for_app_import === true ? "app_import_candidate" : "review_needed";
}

function routeIdentityIsValid(generation, candidatePool, promptContext = {}) {
  const items = isObject(generation.route) && Array.isArray(generation.route.items)
    ? generation.route.items.filter(isObject)
    : [];
  const candidateIDs = candidateIDsFromPool(candidatePool);
  const blockedRouteItemIDs = stringsFromPromptContext(promptContext, [
    "already_selected_route_item_ids",
    "excluded_route_item_ids",
  ]);
  const blockedCandidateIDs = stringsFromPromptContext(promptContext, [
    "already_selected_candidate_ids",
    "excluded_candidate_ids",
    "prior_imported_candidate_ids",
  ]);
  const blockedDisplayKeys = stringsFromPromptContext(promptContext, [
    "already_selected_display_keys",
    "excluded_display_keys",
  ]);
  const routeItemIDs = items.map((item) => cleanString(item.item_id)).filter(Boolean);
  const routeCandidateIDs = items.map((item) => cleanString(item.candidate_id)).filter(Boolean);
  const candidateMetadata = candidateMetadataFromPool(candidatePool);
  const displayKeys = items.map((item) => routeDisplayIdentityKey(item, candidateMetadata)).filter(Boolean);

  if (hasDuplicates(routeItemIDs) || hasDuplicates(routeCandidateIDs) || hasDuplicates(displayKeys)) {
    return false;
  }
  if (routeCandidateIDs.length !== items.length) {
    return false;
  }
  if (candidateIDs.size > 0 && routeCandidateIDs.some((candidateID) => !candidateIDs.has(candidateID))) {
    return false;
  }
  if (routeItemIDs.some((itemID) => blockedRouteItemIDs.has(itemID))) {
    return false;
  }
  if (routeCandidateIDs.some((candidateID) => blockedCandidateIDs.has(candidateID))) {
    return false;
  }
  if (displayKeys.some((displayKey) => blockedDisplayKeys.has(displayKey))) {
    return false;
  }
  return true;
}

function checkMigration() {
  const migration = readFileSync(migrationPath, "utf8");
  for (const column of ["adapter_version", "input_packet_sha256", "openai_request", "raw_openai_response"]) {
    if (!migration.includes(column)) {
      errors.push(`migration missing audit column: ${column}`);
    }
  }

  const alpha1Migration = readFileSync(alpha1MigrationPath, "utf8");
  for (const token of [
    "alpha_tester_profiles",
    "user_id",
    "upload_status",
    "consent_terms_version",
    "payload_sha256",
    "client_artifact_sha256",
  ]) {
    if (!alpha1Migration.includes(token)) {
      errors.push(`alpha1 migration missing auth/evidence token: ${token}`);
    }
  }

  const diagnosticsMigration = readFileSync(diagnosticsMigrationPath, "utf8");
  for (const token of [
    "alpha_client_diagnostic_artifacts",
    "apple_music_signal_payload",
    "client_state_snapshot",
    "survey_page_selection_audit",
    "mission_generation_request_packet",
    "mission_import_result",
    "generation_run_id",
    "payload_sha256",
  ]) {
    if (!diagnosticsMigration.includes(token)) {
      errors.push(`diagnostics migration missing token: ${token}`);
    }
  }
}

function checkEnvExample() {
  const envExample = readFileSync(envExamplePath, "utf8");
  for (const key of [
    "OPENAI_API_KEY",
    "WAYMARK_OPENAI_MODEL",
    "WAYMARK_APP_MISSION_ADAPTER_VERSION",
    "WAYMARK_ALPHA_REPLAY_MODE",
    "WAYMARK_ALPHA_EVIDENCE_TERMS_VERSION",
    "WAYMARK_ALPHA_REVIEW_NEEDED_APP_MISSION_POLICY",
    "WAYMARK_ALPHA_DIAGNOSTIC_TERMS_VERSION",
    "SUPABASE_URL",
    "SUPABASE_SERVICE_ROLE_KEY",
  ]) {
    if (!envExample.includes(`${key}=`)) {
      errors.push(`.env.example missing key: ${key}`);
    }
  }
}

function checkConfig() {
  const config = readFileSync(configPath, "utf8");
  for (const functionName of ["generate-first-mission-batch", "submit-alpha-evidence", "submit-alpha-diagnostic"]) {
    if (!config.includes(`[functions.${functionName}]`)) {
      errors.push(`supabase/config.toml missing function config: ${functionName}`);
    }
  }
}

function checkDiagnosticUploadFixtures() {
  for (const caseName of ["apple_music_signal_payload", "mission_import_result", "client_state_snapshot", "invalid_consent"]) {
    const requestPath = join(diagnosticFixtureRoot, caseName, "request.json");
    const expectedPath = join(diagnosticFixtureRoot, caseName, "expected_contract.json");
    if (!existsSync(requestPath)) errors.push(`missing diagnostic fixture request: ${requestPath}`);
    if (!existsSync(expectedPath)) errors.push(`missing diagnostic expected contract: ${expectedPath}`);
  }

  const validCases = ["apple_music_signal_payload", "mission_import_result", "client_state_snapshot"];
  for (const caseName of validCases) {
    const request = readDiagnosticFixture(caseName, "request");
    if (!isObject(request.consent) || request.consent.diagnostic_upload_allowed !== true) {
      errors.push(`${caseName}: consent.diagnostic_upload_allowed must be true`);
    }
    if (!isObject(request.payload)) {
      errors.push(`${caseName}: payload must be object`);
    }
  }

  const invalidConsent = readDiagnosticFixture("invalid_consent", "request");
  if (isObject(invalidConsent.consent) && invalidConsent.consent.diagnostic_upload_allowed === true) {
    errors.push("diagnostic invalid_consent: fixture should not permit diagnostic upload");
  }
}

function checkEvidenceUploadFixtures() {
  for (const caseName of ["reaction_session", "survey_evidence_export", "invalid_consent"]) {
    const requestPath = join(evidenceFixtureRoot, caseName, "request.json");
    const expectedPath = join(evidenceFixtureRoot, caseName, "expected_contract.json");
    if (!existsSync(requestPath)) errors.push(`missing evidence fixture request: ${requestPath}`);
    if (!existsSync(expectedPath)) errors.push(`missing evidence expected contract: ${expectedPath}`);
  }

  const validCases = ["reaction_session", "survey_evidence_export"];
  for (const caseName of validCases) {
    const request = readEvidenceFixture(caseName, "request");
    if (!isObject(request.consent) || request.consent.evidence_upload_allowed !== true) {
      errors.push(`${caseName}: consent.evidence_upload_allowed must be true`);
    }
    if (!isObject(request.payload)) {
      errors.push(`${caseName}: payload must be object`);
    }
  }

  const invalidConsent = readEvidenceFixture("invalid_consent", "request");
  if (isObject(invalidConsent.consent) && invalidConsent.consent.evidence_upload_allowed === true) {
    errors.push("invalid_consent: fixture should not permit evidence upload");
  }
}

function readFixture(caseName, filename) {
  return JSON.parse(readFileSync(join(fixtureRoot, caseName, `${filename}.json`), "utf8"));
}

function readEvidenceFixture(caseName, filename) {
  return JSON.parse(readFileSync(join(evidenceFixtureRoot, caseName, `${filename}.json`), "utf8"));
}

function readDiagnosticFixture(caseName, filename) {
  return JSON.parse(readFileSync(join(diagnosticFixtureRoot, caseName, `${filename}.json`), "utf8"));
}

function isObject(value) {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function candidateIDsFromPool(value, ids = new Set()) {
  if (Array.isArray(value)) {
    for (const child of value) candidateIDsFromPool(child, ids);
    return ids;
  }
  if (!isObject(value)) return ids;
  const candidateID = cleanString(value.candidate_id);
  if (candidateID) ids.add(candidateID);
  for (const child of Object.values(value)) candidateIDsFromPool(child, ids);
  return ids;
}

function candidateMetadataFromPool(value, metadata = new Map()) {
  if (Array.isArray(value)) {
    for (const child of value) candidateMetadataFromPool(child, metadata);
    return metadata;
  }
  if (!isObject(value)) return metadata;
  const candidateID = cleanString(value.candidate_id);
  if (candidateID) metadata.set(candidateID, value);
  for (const child of Object.values(value)) candidateMetadataFromPool(child, metadata);
  return metadata;
}

function stringsFromPromptContext(promptContext, fieldNames) {
  const values = new Set();
  if (!isObject(promptContext)) return values;
  for (const fieldName of fieldNames) {
    const rawValues = promptContext[fieldName];
    if (!Array.isArray(rawValues)) continue;
    for (const rawValue of rawValues) {
      const value = cleanString(rawValue);
      if (value) values.add(value);
    }
  }
  return values;
}

function routeDisplayIdentityKey(item, candidateMetadata = new Map()) {
  const explicitKey = cleanString(item.route_display_identity_key);
  if (explicitKey) return explicitKey;

  const candidateID = cleanString(item.candidate_id);
  const candidateKey = candidateID ? cleanString(candidateMetadata.get(candidateID)?.route_display_identity_key) : null;
  if (candidateKey) return candidateKey;

  const metadata = isObject(item.display_metadata) ? item.display_metadata : {};
  const searchHint = isObject(item.music_kit_search_hint) ? item.music_kit_search_hint : {};
  const artist = identityPart(metadata.artist ?? searchHint.artist);
  const title = identityPart(metadata.title ?? searchHint.title);
  const itemType = identityPart(item.item_type);
  return artist && title && itemType ? `${itemType}:${artist}:${title}` : null;
}

function hasDuplicates(values) {
  return new Set(values).size !== values.length;
}

function cleanString(value) {
  return typeof value === "string" && value.trim().length > 0 ? value.trim() : null;
}

function identityPart(value) {
  if (typeof value !== "string") return null;
  const normalized = value
    .toLowerCase()
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
  return normalized.length > 0 ? normalized : null;
}
