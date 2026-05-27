#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

const repoRoot = process.cwd();
const base = path.join(repoRoot, "data/canonical_graph/depth_hardening_v0_2");
const passC = path.join(base, "pass_c");
const familyDir = path.join(passC, "families");

const normalizedInventoryPath = path.join(base, "graph_hardening_v0_2_normalized_inventory.json");
const auditPath = path.join(base, "graph_hardening_v0_2_mission_inventory_audit.json");
const auditRows = readJson(auditPath).rows;
const archetypeIdByName = new Map(
  auditRows.map((row) => [normalizeArchetypeName(row.archetype), row.archetype_id]),
);

const safeImportClasses = new Set([
  "core_graph_playable",
  "core_graph_album",
  "boundary_candidate",
  "false_nearby_candidate",
  "context_candidate",
]);

const allowedCandidateTypes = new Set(["song", "recording", "album"]);
const allowedRecognition = new Set(["obvious", "medium", "deep"]);
const allowedRoles = new Set([
  "anchor",
  "bridge",
  "contrast",
  "deep_cut",
  "boundary_case",
  "false_nearby",
  "album_world",
  "context",
]);
const allowedRiskStatus = new Set(["resolved", "resolved_with_version_note"]);

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function normKey(value) {
  return String(value ?? "")
    .toLowerCase()
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/&/g, "and")
    .replace(/[^a-z0-9]+/g, " ")
    .trim()
    .replace(/^the\s+/, "")
    .replace(/\s+/g, " ");
}

function normalizeArchetypeName(value) {
  return String(value ?? "")
    .replace(/^\d{3}\s*:\s*/, "")
    .toLowerCase()
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/&/g, "and")
    .replace(/[^a-z0-9]+/g, " ")
    .trim()
    .replace(/\s+/g, " ");
}

function identityKey(row) {
  return [row.candidate_type, normKey(row.artist_display_name), normKey(row.title)].join("|");
}

function asArray(value) {
  return Array.isArray(value) ? value : value == null ? [] : [value];
}

function loadPassCFiles() {
  if (!fs.existsSync(familyDir)) return [];
  return fs
    .readdirSync(familyDir)
    .filter((file) => /_pass_c_additions\.json$/.test(file))
    .sort((a, b) => a.localeCompare(b, undefined, { numeric: true }))
    .map((file) => path.join(familyDir, file));
}

function extractRows(document, sourceFile) {
  const candidates =
    document.additions ??
    document.candidate_additions ??
    document.pass_c_additions ??
    document.rows ??
    [];
  if (!Array.isArray(candidates)) {
    return [];
  }
  return candidates.map((row, index) => ({
    source_file: path.relative(repoRoot, sourceFile),
    source_index: String(index),
    ...row,
  }));
}

function normalizeRow(row) {
  const candidateType = String(row.candidate_type ?? "").toLowerCase();
  const rawMissionRole = String(row.mission_role ?? "").toLowerCase();
  const rawRecognitionBand = String(row.recognition_band ?? "").toLowerCase();
  const importClass = normalizeImportClass(String(row.import_class ?? "").toLowerCase(), candidateType);
  const riskStatus = normalizeRiskStatus(String(row.risk_status ?? "").toLowerCase());
  const title = String(row.title ?? "").trim();
  const artist = String(row.artist_display_name ?? "").trim();
  const primaryArchetype = String(row.primary_archetype ?? "").trim();
  const idFromArchetype = primaryArchetype.match(/^(\d{3})\s*:/)?.[1];
  const idFromName = archetypeIdByName.get(normalizeArchetypeName(primaryArchetype));
  const missionRole = normalizeMissionRole(rawMissionRole);
  const recognitionBand = normalizeRecognitionBand(rawRecognitionBand);

  const normalized = {
    source_file: row.source_file,
    source_index: row.source_index,
    archetype_id: String(row.archetype_id ?? row.primary_archetype_id ?? idFromArchetype ?? idFromName ?? "").padStart(3, "0"),
    candidate_type: candidateType,
    artist_display_name: artist,
    title,
    year: row.year ?? null,
    primary_family: String(row.primary_family ?? "").trim(),
    primary_archetype: primaryArchetype.replace(/^\d{3}\s*:\s*/, ""),
    secondary_archetypes: asArray(row.secondary_archetypes).map((value) => String(value).trim()).filter(Boolean),
    recognition_band: recognitionBand,
    mission_role: missionRole,
    import_class: importClass,
    version_or_composition_risk: String(row.version_or_composition_risk ?? "none").toLowerCase(),
    risk_status: riskStatus,
    confidence: String(row.confidence ?? "").toLowerCase(),
    effective_mission_credit: Number(row.effective_mission_credit ?? 1),
    why_it_belongs: String(row.why_it_belongs ?? "").trim(),
    notes: String(row.notes ?? "").trim(),
  };
  normalized.identity_key = identityKey(normalized);
  return normalized;
}

function normalizeRecognitionBand(value) {
  if (["obvious", "medium", "deep"].includes(value)) return value;
  if (["mass", "high"].includes(value)) return "obvious";
  if (["low", "cult"].includes(value)) return "deep";
  return value;
}

function normalizeMissionRole(value) {
  if (allowedRoles.has(value)) return value;
  if (["album_anchor", "compilation_gateway", "live_gateway"].includes(value)) return "album_world";
  if (value === "boundary") return "boundary_case";
  if (value === "deepening") return "deep_cut";
  if (["gateway", "song_first"].includes(value)) return "bridge";
  return value;
}

function normalizeImportClass(value, candidateType) {
  if (safeImportClasses.has(value)) return value;
  if (value === "playable_recording" || value === "core_playable") return "core_graph_playable";
  if (value === "album_world" || value === "album_anchor") return "core_graph_album";
  if (value === "boundary") return "boundary_candidate";
  if (value === "false_nearby") return "false_nearby_candidate";
  if (value === "context") return "context_candidate";
  if (!value && candidateType === "album") return "core_graph_album";
  if (!value && (candidateType === "song" || candidateType === "recording")) return "core_graph_playable";
  return value;
}

function normalizeRiskStatus(value) {
  if (allowedRiskStatus.has(value)) return value;
  if (["accepted_clean", "clean", "safe", "resolved_clean"].includes(value)) return "resolved";
  if (["accepted_with_note", "version_note", "resolved_version_note"].includes(value)) {
    return "resolved_with_version_note";
  }
  return value;
}

function validateRow(row) {
  const errors = [];
  if (!/^\d{3}$/.test(row.archetype_id)) errors.push("missing_or_invalid_archetype_id");
  if (!allowedCandidateTypes.has(row.candidate_type)) errors.push("invalid_candidate_type");
  if (!row.artist_display_name) errors.push("missing_artist_display_name");
  if (!row.title) errors.push("missing_title");
  if (row.year == null || row.year === "" || Number(row.year) <= 0) errors.push("missing_or_invalid_year");
  if (!row.primary_family) errors.push("missing_primary_family");
  if (!row.primary_archetype) errors.push("missing_primary_archetype");
  if (!allowedRecognition.has(row.recognition_band)) errors.push("invalid_recognition_band");
  if (!allowedRoles.has(row.mission_role)) errors.push("invalid_mission_role");
  if (!safeImportClasses.has(row.import_class)) errors.push("invalid_or_unsafe_import_class");
  if (!allowedRiskStatus.has(row.risk_status)) errors.push("invalid_or_unresolved_risk_status");
  if (row.effective_mission_credit !== 1) errors.push("invalid_effective_credit");
  if (!row.why_it_belongs) errors.push("missing_why_it_belongs");
  return errors;
}

const normalizedInventory = readJson(normalizedInventoryPath).rows;
const baselineAudit = readJson(auditPath).rows;
const existingByIdentity = new Map();
const existingByIdentityAndArchetype = new Set();

for (const row of normalizedInventory) {
  existingByIdentity.set(row.identity_key, row);
  existingByIdentityAndArchetype.add(`${row.identity_key}@@${row.archetype_id}`);
}

const sourceFiles = loadPassCFiles();
const passCRows = [];
const fileSummaries = [];

for (const file of sourceFiles) {
  const document = readJson(file);
  const rows = extractRows(document, file).map(normalizeRow);
  passCRows.push(...rows);
  fileSummaries.push({
    file: path.relative(repoRoot, file),
    row_count: rows.length,
  });
}

const seenPassCIdentities = new Map();
const rowErrors = [];
const acceptedRows = [];
const duplicateRows = [];

for (const [index, row] of passCRows.entries()) {
  const errors = validateRow(row);
  const existingSameArchetype = existingByIdentityAndArchetype.has(`${row.identity_key}@@${row.archetype_id}`);
  const existingAny = existingByIdentity.has(row.identity_key);
  const priorIndex = seenPassCIdentities.get(`${row.identity_key}@@${row.archetype_id}`);

  if (existingSameArchetype) errors.push("duplicate_existing_same_archetype");
  if (priorIndex != null) errors.push("duplicate_pass_c_same_archetype");

  if (errors.length > 0) {
    rowErrors.push({
      index,
      source_file: row.source_file,
      source_index: row.source_index,
      identity_key: row.identity_key,
      archetype_id: row.archetype_id,
      errors,
    });
    continue;
  }

  if (existingAny) {
    duplicateRows.push({
      index,
      source_file: row.source_file,
      identity_key: row.identity_key,
      archetype_id: row.archetype_id,
      existing_archetype_id: existingByIdentity.get(row.identity_key)?.archetype_id,
      handling: "counts_only_if_PM_accepts_new_multi_membership",
    });
  }

  seenPassCIdentities.set(`${row.identity_key}@@${row.archetype_id}`, index);
  acceptedRows.push({
    ...row,
    current_graph_identity_collision: existingAny,
    accepted_effective_credit: existingAny ? 0 : 1,
  });
}

const additionsByArchetype = new Map();
const additionStatsByArchetype = new Map();
for (const row of acceptedRows) {
  additionsByArchetype.set(
    row.archetype_id,
    (additionsByArchetype.get(row.archetype_id) ?? 0) + row.accepted_effective_credit,
  );
  const stats = additionStatsByArchetype.get(row.archetype_id) ?? {
    accepted_rows: 0,
    zero_credit_identity_collisions: 0,
    playable_songs: 0,
    albums: 0,
    boundary: 0,
    false_nearby: 0,
    context_candidates: 0,
  };
  stats.accepted_rows += 1;
  if (row.accepted_effective_credit === 0) {
    stats.zero_credit_identity_collisions += 1;
  }
  if (row.accepted_effective_credit > 0) {
    if (row.import_class === "core_graph_playable" && ["song", "recording"].includes(row.candidate_type)) {
      stats.playable_songs += row.accepted_effective_credit;
    } else if (row.import_class === "core_graph_album") {
      stats.albums += row.accepted_effective_credit;
    } else if (row.import_class === "boundary_candidate") {
      stats.boundary += row.accepted_effective_credit;
    } else if (row.import_class === "false_nearby_candidate") {
      stats.false_nearby += row.accepted_effective_credit;
    } else if (row.import_class === "context_candidate") {
      stats.context_candidates += row.accepted_effective_credit;
    }
  }
  additionStatsByArchetype.set(row.archetype_id, stats);
}

const updatedAudit = baselineAudit.map((row) => {
  const passCCredit = additionsByArchetype.get(row.archetype_id) ?? 0;
  const passCStats = additionStatsByArchetype.get(row.archetype_id) ?? {
    accepted_rows: 0,
    zero_credit_identity_collisions: 0,
    playable_songs: 0,
    albums: 0,
    boundary: 0,
    false_nearby: 0,
    context_candidates: 0,
  };
  const effectiveMissionCountAfterPassC = row.effective_mission_count + passCCredit;
  const effectiveGapAfterPassC = Math.max(0, row.effective_target - effectiveMissionCountAfterPassC);
  return {
    ...row,
    pass_c_accepted_effective_additions: passCCredit,
    pass_c_accepted_rows: passCStats.accepted_rows,
    pass_c_zero_credit_identity_collisions: passCStats.zero_credit_identity_collisions,
    pass_c_playable_songs: passCStats.playable_songs,
    pass_c_albums: passCStats.albums,
    pass_c_boundary: passCStats.boundary,
    pass_c_false_nearby: passCStats.false_nearby,
    pass_c_context_candidates: passCStats.context_candidates,
    playable_songs_after_pass_c: row.playable_songs + passCStats.playable_songs,
    albums_after_pass_c: row.albums + passCStats.albums,
    artist_anchors_after_pass_c: row.artist_anchors,
    boundary_after_pass_c: row.boundary + passCStats.boundary,
    false_nearby_after_pass_c: row.false_nearby + passCStats.false_nearby,
    context_candidates_after_pass_c: row.context_candidates + passCStats.context_candidates,
    risky_unresolved_after_pass_c: row.risky_unresolved,
    effective_mission_count_after_pass_c: effectiveMissionCountAfterPassC,
    effective_gap_after_pass_c: effectiveGapAfterPassC,
    pass_c_status:
      effectiveGapAfterPassC === 0
        ? "mission_effective_ready"
        : row.high_traffic
          ? "high_traffic_gap"
          : "effective_gap",
  };
});

const summary = {
  generated_on: "2026-05-26",
  source_files: fileSummaries,
  raw_pass_c_rows: passCRows.length,
  accepted_rows: acceptedRows.length,
  row_error_count: rowErrors.length,
  current_identity_collision_count: duplicateRows.length,
  accepted_effective_credit: acceptedRows.reduce((sum, row) => sum + row.accepted_effective_credit, 0),
  ready_before: baselineAudit.filter((row) => row.effective_gap === 0).length,
  ready_after: updatedAudit.filter((row) => row.effective_gap_after_pass_c === 0).length,
  total_gap_before: baselineAudit.reduce((sum, row) => sum + row.effective_gap, 0),
  total_gap_after: updatedAudit.reduce((sum, row) => sum + row.effective_gap_after_pass_c, 0),
};

fs.mkdirSync(path.join(passC, "qa"), { recursive: true });
fs.writeFileSync(
  path.join(passC, "graph_hardening_pass_c_compiled_additions.json"),
  JSON.stringify({ metadata: summary, rows: acceptedRows }, null, 2),
);
fs.writeFileSync(
  path.join(passC, "graph_hardening_pass_c_updated_inventory_audit.json"),
  JSON.stringify({ metadata: summary, rows: updatedAudit }, null, 2),
);
fs.writeFileSync(
  path.join(passC, "graph_hardening_pass_c_updated_inventory_audit.csv"),
  toCsv(updatedAudit),
);
fs.writeFileSync(
  path.join(passC, "qa/graph_hardening_pass_c_qa.json"),
  JSON.stringify({ metadata: summary, row_errors: rowErrors, duplicate_rows: duplicateRows }, null, 2),
);

const auditMarkdown = [
  "| Archetype | Effective Before | Pass C Credit | Effective After | Target | Remaining Gap | Status |",
  "| --------- | ---------------: | ------------: | --------------: | -----: | ------------: | ------ |",
  ...updatedAudit.map((row) =>
    [
      row.archetype,
      row.effective_mission_count,
      row.pass_c_accepted_effective_additions,
      row.effective_mission_count_after_pass_c,
      row.effective_target,
      row.effective_gap_after_pass_c,
      row.pass_c_status,
    ].join(" | "),
  ).map((line) => `| ${line} |`),
];
fs.writeFileSync(
  path.join(passC, "graph_hardening_pass_c_updated_inventory_audit.md"),
  `${auditMarkdown.join("\n")}\n`,
);

console.log(JSON.stringify(summary, null, 2));

function toCsv(rows) {
  if (rows.length === 0) return "";
  const columns = [
    "archetype_id",
    "family_number",
    "archetype",
    "high_traffic",
    "total_count",
    "playable_songs",
    "albums",
    "artist_anchors",
    "boundary",
    "false_nearby",
    "context_candidates",
    "risky_unresolved",
    "effective_mission_count",
    "effective_target",
    "effective_gap",
    "pass_c_accepted_rows",
    "pass_c_accepted_effective_additions",
    "pass_c_zero_credit_identity_collisions",
    "pass_c_playable_songs",
    "pass_c_albums",
    "pass_c_boundary",
    "pass_c_false_nearby",
    "pass_c_context_candidates",
    "playable_songs_after_pass_c",
    "albums_after_pass_c",
    "artist_anchors_after_pass_c",
    "boundary_after_pass_c",
    "false_nearby_after_pass_c",
    "context_candidates_after_pass_c",
    "risky_unresolved_after_pass_c",
    "effective_mission_count_after_pass_c",
    "effective_gap_after_pass_c",
    "pass_c_status",
  ];
  const lines = [
    columns.join(","),
    ...rows.map((row) =>
      columns
        .map((column) => csvCell(row[column]))
        .join(","),
    ),
  ];
  return `${lines.join("\n")}\n`;
}

function csvCell(value) {
  const text = Array.isArray(value) ? value.join("; ") : String(value ?? "");
  return /[",\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
}
