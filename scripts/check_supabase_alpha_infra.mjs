#!/usr/bin/env node
import { existsSync, mkdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const repoRoot = dirname(dirname(fileURLToPath(import.meta.url)));
const reportPath = join(repoRoot, "supabase/alpha_infra_acceptance_report.md");
const results = [];

runStep("build fixtures", ["node", "scripts/build_supabase_function_fixtures.mjs"]);
runStep("fixture smoke", ["node", "scripts/smoke_supabase_generate_first_mission_batch.mjs"]);
runStep("edge function typecheck", [
  "npx",
  "-y",
  "-p",
  "typescript",
  "-p",
  "@types/deno",
  "tsc",
  "--noEmit",
  "--target",
  "ES2022",
  "--lib",
  "ES2022,DOM",
  "--strict",
  "supabase/functions/generate-first-mission-batch/index.ts",
]);
runStep("evidence upload function typecheck", [
  "npx",
  "-y",
  "-p",
  "typescript",
  "-p",
  "@types/deno",
  "tsc",
  "--noEmit",
  "--target",
  "ES2022",
  "--lib",
  "ES2022,DOM",
  "--strict",
  "supabase/functions/submit-alpha-evidence/index.ts",
]);
runStep("diagnostic upload function typecheck", [
  "npx",
  "-y",
  "-p",
  "typescript",
  "-p",
  "@types/deno",
  "tsc",
  "--noEmit",
  "--target",
  "ES2022",
  "--lib",
  "ES2022,DOM",
  "--strict",
  "supabase/functions/submit-alpha-diagnostic/index.ts",
]);

const supabaseVersion = commandOutput(["supabase", "--version"]);
const npxSupabaseVersion = commandOutput(["npx", "-y", "supabase", "--version"]);
const denoVersion = commandOutput(["deno", "--version"]);
const nodeVersion = commandOutput(["node", "--version"]);
const npxVersion = commandOutput(["npx", "--version"]);
const projectRef = process.env.SUPABASE_PROJECT_REF || "ewuffhezhgyskcfyzkvw";

const requiredFiles = [
  "supabase/config.toml",
  "supabase/functions/.env.example",
  "supabase/functions/generate-first-mission-batch/index.ts",
  "supabase/functions/submit-alpha-evidence/index.ts",
  "supabase/functions/submit-alpha-diagnostic/index.ts",
  "supabase/migrations/20260521160000_alpha_generation_logs.sql",
  "supabase/migrations/20260522190000_alpha1_auth_and_evidence_upload.sql",
  "supabase/migrations/20260524170000_alpha_client_diagnostics.sql",
  "supabase/migrations/20260525120000_alpha_client_state_snapshot_diagnostics.sql",
  "supabase/functions/generate-first-mission-batch/fixtures/app_import_candidate/request.json",
  "supabase/functions/generate-first-mission-batch/fixtures/review_needed/request.json",
  "supabase/functions/generate-first-mission-batch/fixtures/blocked/request.json",
  "supabase/functions/generate-first-mission-batch/fixtures/invalid_input/request.json",
  "supabase/functions/submit-alpha-evidence/fixtures/reaction_session/request.json",
  "supabase/functions/submit-alpha-evidence/fixtures/survey_evidence_export/request.json",
  "supabase/functions/submit-alpha-evidence/fixtures/invalid_consent/request.json",
  "supabase/functions/submit-alpha-diagnostic/fixtures/apple_music_signal_payload/request.json",
  "supabase/functions/submit-alpha-diagnostic/fixtures/client_state_snapshot/request.json",
  "supabase/functions/submit-alpha-diagnostic/fixtures/mission_import_result/request.json",
  "supabase/functions/submit-alpha-diagnostic/fixtures/invalid_consent/request.json",
  "scripts/summarize_alpha_live_run.mjs",
];

for (const file of requiredFiles) {
  if (!existsSync(join(repoRoot, file))) {
    results.push({ name: `required file ${file}`, ok: false, output: "missing" });
  }
}

const liveStatus = collectLiveStatus(projectRef);
const failed = results.filter((result) => !result.ok);
writeReport({
  supabaseVersion,
  npxSupabaseVersion,
  denoVersion,
  nodeVersion,
  npxVersion,
  liveStatus,
  failed,
});

if (failed.length > 0) {
  console.error(`SUPABASE_ALPHA_INFRA_CHECK_FAIL (${failed.length} failure(s))`);
  for (const result of failed) {
    console.error(`- ${result.name}`);
  }
  process.exit(1);
}

console.log("SUPABASE_ALPHA_INFRA_CHECK_PASS");
console.log(`Report: ${reportPath}`);

function runStep(name, command) {
  const result = spawnSync(command[0], command.slice(1), {
    cwd: repoRoot,
    encoding: "utf8",
    stdio: "pipe",
  });
  results.push({
    name,
    ok: result.status === 0,
    output: [result.stdout.trim(), result.stderr.trim()].filter(Boolean).join("\n"),
  });
}

function commandOutput(command) {
  const result = spawnSync(command[0], command.slice(1), {
    cwd: repoRoot,
    encoding: "utf8",
    stdio: "pipe",
  });
  if (result.status !== 0) {
    return null;
  }
  return result.stdout.trim() || result.stderr.trim();
}

function collectLiveStatus(projectRef) {
  const projects = commandOutput(["npx", "-y", "supabase", "projects", "list"]);
  const migrations = commandOutput(["npx", "-y", "supabase", "migration", "list", "--linked"]);
  const functions = commandOutput(["npx", "-y", "supabase", "functions", "list", "--project-ref", projectRef]);
  const secrets = commandOutput(["npx", "-y", "supabase", "secrets", "list", "--project-ref", projectRef]);

  const projectLine = projects
    ?.split("\n")
    .find((line) => line.includes(projectRef));
  const migrationIds = ["20260521160000", "20260522190000", "20260524170000", "20260525120000"];
  const blockers = [];

  if (!projects) {
    blockers.push("local Supabase CLI authentication for remote checks");
  }
  if (!secrets?.includes("OPENAI_API_KEY")) {
    blockers.push("OPENAI_API_KEY edge function secret");
  }
  if (!secrets?.includes("WAYMARK_ALPHA_REVIEW_NEEDED_APP_MISSION_POLICY")) {
    blockers.push("WAYMARK_ALPHA_REVIEW_NEEDED_APP_MISSION_POLICY edge function secret");
  }
  if (!secrets?.includes("WAYMARK_ALPHA_DIAGNOSTIC_TERMS_VERSION")) {
    blockers.push("WAYMARK_ALPHA_DIAGNOSTIC_TERMS_VERSION edge function secret");
  }
  blockers.push("authenticated app/JWT smoke path");
  blockers.push("Supabase Auth Apple provider end-to-end smoke");
  blockers.push("final privacy/retention/deletion policy before automatic evidence upload");

  return {
    projectRef,
    projectLinked: Boolean(projectLine?.includes("●")),
    projectAccessible: Boolean(projectLine),
    migrationsApplied: migrationIds.every((migrationId) => migrations?.includes(migrationId)),
    generationFunctionActive: Boolean(functions?.includes("generate-first-mission-batch") && functions.includes("ACTIVE")),
    evidenceFunctionActive: Boolean(functions?.includes("submit-alpha-evidence") && functions.includes("ACTIVE")),
    diagnosticFunctionActive: Boolean(functions?.includes("submit-alpha-diagnostic") && functions.includes("ACTIVE")),
    openaiSecretPresent: Boolean(secrets?.includes("OPENAI_API_KEY")),
    reviewNeededPolicySecretPresent: Boolean(secrets?.includes("WAYMARK_ALPHA_REVIEW_NEEDED_APP_MISSION_POLICY")),
    diagnosticTermsSecretPresent: Boolean(secrets?.includes("WAYMARK_ALPHA_DIAGNOSTIC_TERMS_VERSION")),
    secretsChecked: Boolean(secrets),
    blockers,
  };
}

function status(value, checked = true) {
  if (!checked) return "`not checked/unavailable`";
  return value ? "`yes`" : "`no`";
}

function writeReport({ supabaseVersion, npxSupabaseVersion, denoVersion, nodeVersion, npxVersion, liveStatus, failed }) {
  const body = [
    "# Supabase Alpha Infrastructure Acceptance Report",
    "",
    `Generated: ${new Date().toISOString()}`,
    "",
    "## Tooling",
    "",
    `- Supabase CLI: ${supabaseVersion ? `\`${supabaseVersion}\`` : "`not installed`"}`,
    `- Supabase CLI via npx: ${npxSupabaseVersion ? `\`${npxSupabaseVersion}\`` : "`not available`"}`,
    `- Deno CLI: ${denoVersion ? `\`${denoVersion.split("\n")[0]}\`` : "`not installed`"}`,
    `- Node: ${nodeVersion ? `\`${nodeVersion}\`` : "`not installed`"}`,
    `- npx: ${npxVersion ? `\`${npxVersion}\`` : "`not installed`"}`,
    "",
    "Supabase and Deno CLI absence does not block offline fixture/typecheck validation. Live link, migration, secrets, and deploy still require a real Supabase project and access token.",
    "",
    "## Local Checks",
    "",
    ...results.map((result) => `- ${result.ok ? "pass" : "fail"}: ${result.name}`),
    "",
    "## Live Supabase Status",
    "",
    `- Project ref: \`${liveStatus.projectRef}\``,
    `- Project accessible: ${status(liveStatus.projectAccessible, true)}`,
    `- Project linked: ${status(liveStatus.projectLinked, liveStatus.projectAccessible)}`,
    `- Required migrations applied: ${status(liveStatus.migrationsApplied, liveStatus.projectAccessible)}`,
    `- Edge Function secrets checked: ${status(liveStatus.secretsChecked, true)}`,
    `- \`OPENAI_API_KEY\` present: ${status(liveStatus.openaiSecretPresent, liveStatus.secretsChecked)}`,
    `- \`WAYMARK_ALPHA_REVIEW_NEEDED_APP_MISSION_POLICY\` present: ${status(liveStatus.reviewNeededPolicySecretPresent, liveStatus.secretsChecked)}`,
    `- \`WAYMARK_ALPHA_DIAGNOSTIC_TERMS_VERSION\` present: ${status(liveStatus.diagnosticTermsSecretPresent, liveStatus.secretsChecked)}`,
    `- \`generate-first-mission-batch\` deployed/active: ${status(liveStatus.generationFunctionActive, liveStatus.projectAccessible)}`,
    `- \`submit-alpha-evidence\` deployed/active: ${status(liveStatus.evidenceFunctionActive, liveStatus.projectAccessible)}`,
    `- \`submit-alpha-diagnostic\` deployed/active: ${status(liveStatus.diagnosticFunctionActive, liveStatus.projectAccessible)}`,
    "",
    "## Remaining Live Blockers",
    "",
    ...liveStatus.blockers.map((blocker) => `- ${blocker}`),
    "",
    "## Result",
    "",
    failed.length === 0 ? "`offline_acceptance_pass`" : "`offline_acceptance_fail`",
  ];

  mkdirSync(dirname(reportPath), { recursive: true });
  writeFileSync(reportPath, `${body.join("\n")}\n`);
}
