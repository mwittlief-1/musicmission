#!/usr/bin/env node
import { argv, env, exit } from "node:process";

const args = parseArgs(argv.slice(2));
const testerAlias = args["tester-alias"] ?? args.tester;
const since = args.since ?? new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
const jsonOutput = args.json === "true" || args.json === true;
const supabaseUrl = env.SUPABASE_URL;
const serviceKey = env.SUPABASE_SERVICE_ROLE_KEY;

if (!testerAlias || !supabaseUrl || !serviceKey) {
  console.error([
    "Usage:",
    "  SUPABASE_URL=... SUPABASE_SERVICE_ROLE_KEY=... node scripts/summarize_alpha_live_run.mjs --tester-alias <alias> [--since <iso>] [--json]",
    "",
    "This script reads trusted Alpha audit rows through Supabase REST using service-role credentials.",
  ].join("\n"));
  exit(2);
}

const [generationRuns, diagnostics, evidence] = await Promise.all([
  fetchRows("alpha_generation_runs", {
    select: [
      "id",
      "client_request_id",
      "tester_alias",
      "status",
      "app_import_status",
      "prompt_version",
      "model",
      "adapter_version",
      "input_packet_sha256",
      "app_missions",
      "validation",
      "token_usage",
      "latency_ms",
      "error_message",
      "created_at",
      "updated_at",
    ].join(","),
    tester_alias: `eq.${testerAlias}`,
    created_at: `gte.${since}`,
    order: "created_at.asc",
  }),
  fetchRows("alpha_client_diagnostic_artifacts", {
    select: [
      "id",
      "client_artifact_id",
      "tester_alias",
      "artifact_type",
      "survey_session_id",
      "client_request_id",
      "generation_run_id",
      "mission_id",
      "source_app_version",
      "source_app_build",
      "payload",
      "payload_sha256",
      "client_created_at",
      "received_at",
    ].join(","),
    tester_alias: `eq.${testerAlias}`,
    received_at: `gte.${since}`,
    order: "received_at.asc",
  }),
  fetchRows("alpha_evidence_artifacts", {
    select: [
      "id",
      "client_artifact_id",
      "tester_alias",
      "artifact_type",
      "upload_status",
      "upload_cadence",
      "source_app_version",
      "source_app_build",
      "payload_sha256",
      "client_created_at",
      "received_at",
    ].join(","),
    tester_alias: `eq.${testerAlias}`,
    received_at: `gte.${since}`,
    order: "received_at.asc",
  }),
]);

const summary = {
  tester_alias: testerAlias,
  since,
  generation_runs: generationRuns.map(summarizeGenerationRun),
  diagnostic_artifacts: diagnostics.map(summarizeDiagnostic),
  evidence_artifacts: evidence.map(summarizeEvidence),
  counts: {
    generation_runs: generationRuns.length,
    app_import_candidate: generationRuns.filter((run) => run.status === "app_import_candidate").length,
    review_needed: generationRuns.filter((run) => run.status === "review_needed").length,
    blocked: generationRuns.filter((run) => run.status === "blocked").length,
    failed: generationRuns.filter((run) => run.status === "failed").length,
    diagnostic_artifacts: diagnostics.length,
    evidence_artifacts: evidence.length,
  },
};

if (jsonOutput) {
  console.log(JSON.stringify(summary, null, 2));
} else {
  printMarkdown(summary);
}

function summarizeGenerationRun(run) {
  const validation = isObject(run.validation) ? run.validation : {};
  const alphaPolicy = isObject(validation.alpha_import_policy) ? validation.alpha_import_policy : {};
  const routeIdentity = isObject(validation.route_identity) ? validation.route_identity : {};
  const appMissions = Array.isArray(run.app_missions) ? run.app_missions : [];
  return {
    id: run.id,
    client_request_id: run.client_request_id,
    status: run.status,
    app_import_status: run.app_import_status,
    app_mission_count: appMissions.length,
    app_import_allowed_for_trusted_alpha: alphaPolicy.app_import_allowed_for_trusted_alpha ?? null,
    app_missions_returned: alphaPolicy.app_missions_returned ?? null,
    status_reason: alphaPolicy.status_reason ?? null,
    route_identity: {
      duplicate_route_item_ids: routeIdentity.duplicate_route_item_ids ?? [],
      duplicate_candidate_ids: routeIdentity.duplicate_candidate_ids ?? [],
      duplicate_display_identity_keys: routeIdentity.duplicate_display_identity_keys ?? [],
      non_candidate_ids: routeIdentity.non_candidate_ids ?? [],
    },
    model: run.model,
    prompt_version: run.prompt_version,
    adapter_version: run.adapter_version,
    input_packet_sha256: run.input_packet_sha256,
    token_usage: run.token_usage ?? null,
    latency_ms: run.latency_ms,
    error_message: run.error_message,
    created_at: run.created_at,
  };
}

function summarizeDiagnostic(artifact) {
  const payload = isObject(artifact.payload) ? artifact.payload : {};
  const rootState = isObject(payload.root_state) ? payload.root_state : {};
  return {
    id: artifact.id,
    client_artifact_id: artifact.client_artifact_id,
    artifact_type: artifact.artifact_type,
    survey_session_id: artifact.survey_session_id,
    client_request_id: artifact.client_request_id,
    generation_run_id: artifact.generation_run_id,
    mission_id: artifact.mission_id,
    app: [artifact.source_app_version, artifact.source_app_build].filter(Boolean).join(" build "),
    local_import_status: payload.local_import_status ?? null,
    local_validation_errors: payload.local_validation_errors ?? null,
    computed_root_stage: rootState.computed_root_stage ?? payload.computed_root_stage ?? null,
    generation_status: rootState.generation_status ?? null,
    reviewed_mission_count: rootState.reviewed_mission_count ?? null,
    payload_sha256: artifact.payload_sha256,
    received_at: artifact.received_at,
  };
}

function summarizeEvidence(artifact) {
  return {
    id: artifact.id,
    client_artifact_id: artifact.client_artifact_id,
    artifact_type: artifact.artifact_type,
    upload_status: artifact.upload_status,
    upload_cadence: artifact.upload_cadence,
    app: [artifact.source_app_version, artifact.source_app_build].filter(Boolean).join(" build "),
    payload_sha256: artifact.payload_sha256,
    received_at: artifact.received_at,
  };
}

function printMarkdown(summary) {
  console.log(`# Alpha Live Run Summary`);
  console.log("");
  console.log(`- tester_alias: \`${summary.tester_alias}\``);
  console.log(`- since: \`${summary.since}\``);
  console.log(`- generation runs: ${summary.counts.generation_runs}`);
  console.log(`- review_needed: ${summary.counts.review_needed}`);
  console.log(`- app_import_candidate: ${summary.counts.app_import_candidate}`);
  console.log(`- blocked/failed: ${summary.counts.blocked}/${summary.counts.failed}`);
  console.log(`- diagnostic artifacts: ${summary.counts.diagnostic_artifacts}`);
  console.log(`- evidence artifacts: ${summary.counts.evidence_artifacts}`);
  console.log("");

  console.log("## Generation Runs");
  for (const run of summary.generation_runs) {
    const routeIssues = [
      ...(run.route_identity.duplicate_route_item_ids ?? []).map((value) => `duplicate item ${value}`),
      ...(run.route_identity.duplicate_candidate_ids ?? []).map((value) => `duplicate candidate ${value}`),
      ...(run.route_identity.non_candidate_ids ?? []).map((value) => `non-candidate ${value}`),
    ];
    console.log(
      `- ${run.created_at}: \`${run.status}\` / \`${run.app_import_status}\`; app_missions=${run.app_mission_count}; run=${run.id}; request=${run.client_request_id}; reason=${run.status_reason ?? "n/a"}${routeIssues.length > 0 ? `; route=${routeIssues.join(", ")}` : ""}`,
    );
  }
  if (summary.generation_runs.length === 0) console.log("- none");
  console.log("");

  console.log("## Diagnostic Artifacts");
  for (const artifact of summary.diagnostic_artifacts) {
    const details = [
      artifact.local_import_status ? `local_import=${artifact.local_import_status}` : null,
      artifact.computed_root_stage ? `root=${artifact.computed_root_stage}` : null,
      artifact.generation_status ? `generation=${artifact.generation_status}` : null,
      Number.isInteger(artifact.reviewed_mission_count) ? `missions=${artifact.reviewed_mission_count}` : null,
      Array.isArray(artifact.local_validation_errors) && artifact.local_validation_errors.length > 0
        ? `errors=${artifact.local_validation_errors.join(" | ")}`
        : null,
    ].filter(Boolean).join("; ");
    console.log(
      `- ${artifact.received_at}: \`${artifact.artifact_type}\`; request=${artifact.client_request_id ?? "n/a"}; run=${artifact.generation_run_id ?? "n/a"}; mission=${artifact.mission_id ?? "n/a"}${details ? `; ${details}` : ""}`,
    );
  }
  if (summary.diagnostic_artifacts.length === 0) console.log("- none");
  console.log("");

  console.log("## Evidence Artifacts");
  for (const artifact of summary.evidence_artifacts) {
    console.log(
      `- ${artifact.received_at}: \`${artifact.artifact_type}\`; status=${artifact.upload_status}; cadence=${artifact.upload_cadence ?? "n/a"}`,
    );
  }
  if (summary.evidence_artifacts.length === 0) console.log("- none");
}

async function fetchRows(table, filters) {
  const url = new URL(`${supabaseUrl.replace(/\/$/, "")}/rest/v1/${table}`);
  for (const [key, value] of Object.entries(filters)) {
    url.searchParams.set(key, value);
  }

  const response = await fetch(url, {
    headers: {
      apikey: serviceKey,
      Authorization: `Bearer ${serviceKey}`,
      Accept: "application/json",
    },
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`${table} query failed: ${response.status} ${body}`);
  }

  return await response.json();
}

function parseArgs(rawArgs) {
  const parsed = {};
  for (let index = 0; index < rawArgs.length; index += 1) {
    const arg = rawArgs[index];
    if (!arg.startsWith("--")) continue;
    const key = arg.slice(2);
    const next = rawArgs[index + 1];
    if (!next || next.startsWith("--")) {
      parsed[key] = true;
    } else {
      parsed[key] = next;
      index += 1;
    }
  }
  return parsed;
}

function isObject(value) {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
