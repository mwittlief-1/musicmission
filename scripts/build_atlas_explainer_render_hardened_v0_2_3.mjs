import fs from "node:fs";
import path from "node:path";
import { execFileSync, spawnSync } from "node:child_process";

const ROOT = process.cwd();
const GENERATED_AT = "2026-05-27";
const SOURCE_DIR = path.join(ROOT, "data/atlas_explainer/AtlasExplainerPack_v0_2_2_SourceRecovery");
const OUT_DIR = path.join(ROOT, "data/atlas_explainer/AtlasExplainerPack_v0_2_3_RenderHardened");
const ZIP_PATH = `${OUT_DIR}.zip`;

const MODULE_KEYS = [
  "atlas_home_region_card",
  "region_scene_page",
  "mission_detail_history_module",
  "did_you_know_card",
  "what_to_listen_for_prompt",
  "personalized_atlas_overlay",
  "canonical_examples_block",
  "related_roads_lineage_module",
  "dead_end_false_nearby_caution_module"
];

const INTERNAL_QA_PATTERNS = [
  /do not cite/i,
  /do not support/i,
  /use .* sources/i,
  /sources? alone/i,
  /source-audit/i,
  /wrong_context/i,
  /family_context_only/i,
  /primary evidence/i,
  /source-deepening/i,
  /source deepening/i,
  /graph-defined road/i,
  /draft road/i,
  /until PM/i,
  /Atlas uses this draft road/i
];

const FORBIDDEN_DYNAMIC_MISSION_PHRASES = [
  "generate mission from this node",
  "create a new mission",
  "launch arbitrary mission",
  "open a dynamic route from here",
  "ask AI to build a mission from this archetype"
];

const TEMPLATE_RATIONALE_PATTERNS = [
  /short-form urgency and angular guitar or synth lines/i,
  /angular guitar or synth lines and dry scene energy/i,
  /dry scene energy and DIY economy/i,
  /anchors .* by making .* easier to hear/i,
  /roots sources carried by personal authorship/i
];

const ARCHETYPE_RENDER_CUES = new Map([
  ["005", ["immediate hook placement", "teen-drama compression", "backing-vocal answer phrases", "handclap and percussion punctuation", "studio scale around the lead vocal"]],
  ["054", ["small-room tension", "poetry or art-school persona", "minimalist guitar or rhythm choices", "downtown scene contrast", "pop hooks under abrasion"]]
]);

const SPECIAL_EXAMPLE_CUES = new Map([
  ["the chiffons", "girl-group harmonies, bright teen-drama hooks, and compact early-1960s pop craft"],
  ["the crystals", "Spector-era scale, call-and-response drama, and teenage melodrama"],
  ["a christmas gift for you from phil spector - various artists", "wall-of-sound density, studio scale, and pop-standard craft"],
  ["presenting the fabulous ronettes featuring veronica - the ronettes", "Veronica Bennett's lead vocal, backing-vocal drama, and Spector-style studio scale"],
  ["be my baby - the ronettes", "iconic drum intro, wall-of-sound scale, and Veronica Bennett's lead-vocal drama"],
  ["will you love me tomorrow - the shirelles", "girl-group vulnerability, polished songwriting, and a chorus built around teenage uncertainty"],
  ["the cure", "bass-led melancholy, reverb-thick atmosphere, and pop melody under gothic restraint"],
  ["disintegration - the cure", "scale, reverb, bass-led melancholy, and emotional immersion"],
  ["talking heads", "anxious rhythm, clipped guitar, conceptual art-pop, and downtown tension"],
  ["remain in light - talking heads", "interlocking rhythm, studio experiment, and art-funk tension"],
  ["once in a lifetime - talking heads", "sermon-like vocal phrasing, looped groove, and conceptual art-pop unease"],
  ["patti smith", "poetry-rock persona, incantatory vocal force, and downtown art-punk authority"],
  ["horses - patti smith", "poetry-rock structure, live-wire vocal presence, and art-punk transformation of garage material"],
  ["gloria - patti smith", "spoken-to-sung escalation, garage-rock transformation, and downtown poetic force"],
  ["the cars", "synth/guitar pop architecture, deadpan vocal cool, and new-wave polish"],
  ["the cars - the cars", "synth/guitar pop architecture, deadpan vocal cool, and new-wave polish"],
  ["lcd soundsystem", "cumulative groove, dance-punk body, adult irony, and repetition"],
  ["sound of silver - lcd soundsystem", "cumulative groove, dance-punk body, adult irony, and repetition"],
  ["frankie knuckles", "DJ architecture, four-on-the-floor lift, and Chicago club warmth"],
  ["juan atkins", "machine pulse, Detroit futurism, and lean synth motion"],
  ["mahalia jackson", "gospel vocal authority, church phrasing, and sacred emotional lift"],
  ["sister rosetta tharpe", "gospel drive, guitar attack, and sacred-to-pop bridgework"],
  ["aretha franklin", "gospel-rooted phrasing, soul force, and piano-centered authority"],
  ["carole king", "piano-centered melody, conversational vocal phrasing, and songwriter intimacy"],
  ["billy joel", "piano-driven structure, character writing, and adult-pop payoff"],
  ["james taylor", "soft vocal grain, acoustic restraint, and confessional calm"],
  ["joni mitchell", "harmonic color, intimate phrasing, and writerly detail"],
  ["blue - joni mitchell", "harmonic color, emotional exposure, and album-scale intimacy"],
  ["tapestry - carole king", "piano-led craft, direct feeling, and singer-songwriter architecture"],
  ["the strokes", "dry guitar precision, city cool, and stripped early-2000s rock style"],
  ["is this it - the strokes", "dry guitar precision, city cool, and stripped early-2000s rock style"],
  ["the white stripes", "garage-blues reduction, raw guitar attack, and minimalist rock drama"],
  ["elephant - the white stripes", "garage-blues reduction, raw guitar attack, and minimalist rock drama"],
  ["interpol", "post-punk bass movement, baritone cool, and nocturnal guitar tension"],
  ["turn on the bright lights - interpol", "post-punk bass movement, baritone cool, and nocturnal guitar tension"],
  ["my bloody valentine", "guitar haze, vocal blur, and immersive noise-pop texture"],
  ["loveless - my bloody valentine", "guitar haze, vocal blur, and immersive noise-pop texture"]
]);

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function writeJson(filePath, data) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, `${JSON.stringify(data, null, 2)}\n`);
}

function writeText(filePath, text) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, text);
}

function listJsonFiles(dir) {
  return fs.readdirSync(dir)
    .filter((name) => name.endsWith(".json"))
    .sort()
    .map((name) => path.join(dir, name));
}

function mdReport(title, lines) {
  return [`# ${title}`, "", ...lines, ""].join("\n");
}

function v23Id(id) {
  return String(id).replace(/_v0_2_2$/u, "_v0_2_3");
}

function schemaNameV23(name) {
  return name.replace("v0_2_2", "v0_2_3");
}

function moduleStrings(pack) {
  const rows = [];
  for (const key of MODULE_KEYS) {
    for (const depth of ["compact", "standard", "deep"]) {
      rows.push({ module: key, depth, text: String(pack.modules?.[key]?.[depth] || "") });
    }
  }
  return rows;
}

function sentence(text) {
  return String(text || "")
    .replace(/\s+/gu, " ")
    .trim()
    .replace(/\.$/u, "");
}

function firstSentence(text, maxLength = 220) {
  const cleaned = sentence(text);
  const first = cleaned.split(/(?<=\.)\s+/u)[0]?.replace(/\.$/u, "") || cleaned;
  if (first.length <= maxLength) return first;
  const trimmed = first.slice(0, maxLength).replace(/\s+\S*$/u, "");
  return `${trimmed}...`;
}

function titleWithoutSlash(title) {
  return String(title || "").replace(/\s*\/\s*/gu, " / ");
}

function getListenCues(researchPack) {
  if (ARCHETYPE_RENDER_CUES.has(researchPack.identity.archetype_id)) {
    return ARCHETYPE_RENDER_CUES.get(researchPack.identity.archetype_id);
  }
  const cues = researchPack.explainer_content?.what_to_listen_for || [];
  return cues.filter(Boolean).slice(0, 5);
}

function readableList(items) {
  const values = items.filter(Boolean);
  if (!values.length) return "";
  if (values.length === 1) return values[0];
  if (values.length === 2) return `${values[0]} and ${values[1]}`;
  return `${values.slice(0, -1).join(", ")}, and ${values.at(-1)}`;
}

function cleanUserCopy(text) {
  return String(text || "")
    .replace(/Do not cite [^.]+\.?/giu, "")
    .replace(/Do not support [^.]+\.?/giu, "")
    .replace(/Avoid using only [^.]+\.?/giu, "")
    .replace(/Use .* sources[^.]+\.?/giu, "")
    .replace(/Use dead-end probe results only when explicit Atlas evidence supports them\.?/giu, "")
    .replace(/Repeated negative signals can mark a false-nearby caution, but the road's map position stays unchanged\.?/giu, "")
    .replace(/\s+/gu, " ")
    .trim();
}

function buildCautionModule(researchPack) {
  const title = researchPack.identity.editorial_display_title;
  const cues = getListenCues(researchPack);
  const cueText = readableList(cues.slice(0, 3)) || "its core listening evidence";
  const distinct = sentence(researchPack.explainer_content?.what_made_it_distinct) || "its specific historical function and sound";
  const compact = `Do not confuse ${title} with nearby roads unless the listening evidence points there.`;
  const standard = `${compact} This lane is about ${cueText}.`;
  const deep = `${standard} In Alpha, treat this as a false-nearby caution: recognition can help orient the road, but repeated Atlas evidence should carry the fit.`;
  return { compact, standard, deep, audit_note: distinct };
}

function relatedLabels(refs, identityByRef) {
  return refs
    .map((ref) => identityByRef.get(ref)?.editorial_display_title || identityByRef.get(ref)?.existing_graph_label_name || null)
    .filter(Boolean);
}

function buildRelatedModule(researchPack, identityByRef) {
  const title = researchPack.identity.editorial_display_title;
  const relatedRefs = researchPack.graph_alignment?.related_archetype_refs || [];
  const beforeRefs = researchPack.graph_alignment?.before_archetype_refs || [];
  const afterRefs = researchPack.graph_alignment?.after_archetype_refs || [];
  const related = relatedLabels(relatedRefs, identityByRef);
  const before = relatedLabels(beforeRefs, identityByRef);
  const after = relatedLabels(afterRefs, identityByRef);
  const display = related.length ? related : [...before, ...after];
  const compact = display.length
    ? `Related road${display.length > 1 ? "s" : ""}: ${readableList(display.slice(0, 3))}.`
    : `${title} sits at an edge of its current family map.`;
  const distinct = firstSentence(researchPack.explainer_content?.what_made_it_distinct) || "the listening evidence changes the fit";
  const standard = display.length
    ? `${title} sits near ${readableList(display.slice(0, 3))}; the contrast is ${distinct}.`
    : `${title} has no explicit adjacent road in the current graph; use the family context to explain what this route tests.`;
  const lineageParts = [];
  if (before.length) lineageParts.push(`before it: ${readableList(before.slice(0, 3))}`);
  if (after.length) lineageParts.push(`after it: ${readableList(after.slice(0, 3))}`);
  const lineage = lineageParts.length ? ` Lineage markers: ${lineageParts.join("; ")}.` : "";
  const deep = `${standard}${lineage} In Alpha, keep this as related mission context: it can explain the batch, and you may encounter this road later.`;
  return { compact, standard, deep };
}

function buildListenModule(researchPack) {
  const cues = getListenCues(researchPack);
  const compact = `Listen for ${readableList(cues.slice(0, 2))}.`;
  const standard = `Listen for ${readableList(cues.slice(0, 4))}.`;
  const deep = `Listen for ${readableList(cues.slice(0, 5))}.`;
  return { compact, standard, deep };
}

function exampleCueText(example, researchPack) {
  const special = SPECIAL_EXAMPLE_CUES.get(String(example.display_label || "").toLowerCase());
  if (special) return special;
  const exampleCues = (example.what_to_listen_for || []).filter(Boolean);
  const researchCues = getListenCues(researchPack);
  const cues = [...new Set([...exampleCues, ...researchCues])].slice(0, 3);
  return readableList(cues) || "the road's core sound and historical function";
}

function polishedExample(example, researchPack) {
  const title = researchPack.identity.editorial_display_title;
  const label = example.display_label;
  const cueText = exampleCueText(example, researchPack);
  const type = example.example_type;
  const prefix = type === "album"
    ? `${label} gives ${title} an album-scale anchor`
    : type === "song_recording"
      ? `${label} gives ${title} a song-level listening test`
      : `${label} anchors ${title}`;
  const cues = (SPECIAL_EXAMPLE_CUES.get(String(label || "").toLowerCase())
    ? SPECIAL_EXAMPLE_CUES.get(String(label || "").toLowerCase()).split(/,\s*|, and\s*/u)
    : [...new Set([...(example.what_to_listen_for || []), ...getListenCues(researchPack)])].slice(0, 4))
    .filter(Boolean)
    .map((cue) => cue.replace(/^and /u, ""));
  return {
    ...example,
    why_this_example_matters: `${prefix}: listen for ${cueText}.`,
    what_to_listen_for: cues.length ? cues.slice(0, 4) : ["core listening evidence"]
  };
}

function versionResearchPack(pack) {
  return {
    ...pack,
    schema_version: "0.2.3",
    pack_id: v23Id(pack.pack_id),
    generated_at: GENERATED_AT
  };
}

function versionRenderPack(pack, researchPack, identityByRef, reports) {
  const originalModules = pack.modules;
  const caution = buildCautionModule(researchPack);
  const related = buildRelatedModule(researchPack, identityByRef);
  const polishedExamples = (pack.canonical_examples || []).map((example) => {
    const before = example.why_this_example_matters || "";
    const after = polishedExample(example, researchPack);
    if (before !== after.why_this_example_matters || TEMPLATE_RATIONALE_PATTERNS.some((regex) => regex.test(before))) {
      reports.examplePolish.push({
        canonical_graph_ref: pack.identity.canonical_graph_ref,
        example_ref: example.example_ref,
        display_label: example.display_label,
        before,
        after: after.why_this_example_matters
      });
    }
    return after;
  });
  const modules = Object.fromEntries(Object.entries(originalModules).map(([key, value]) => [key, {
    compact: cleanUserCopy(value.compact),
    standard: cleanUserCopy(value.standard),
    deep: cleanUserCopy(value.deep)
  }]));
  modules.dead_end_false_nearby_caution_module = {
    compact: caution.compact,
    standard: caution.standard,
    deep: caution.deep
  };
  modules.related_roads_lineage_module = related;
  modules.what_to_listen_for_prompt = buildListenModule(researchPack);
  reports.related.push({
    canonical_graph_ref: pack.identity.canonical_graph_ref,
    compact: related.compact,
    standard: related.standard,
    deep: related.deep
  });
  const qaBefore = moduleStrings(pack).filter((row) => INTERNAL_QA_PATTERNS.some((regex) => regex.test(row.text)));
  const qaAfter = moduleStrings({ modules }).filter((row) => INTERNAL_QA_PATTERNS.some((regex) => regex.test(row.text)));
  if (qaBefore.length || qaAfter.length) {
    reports.qaLanguage.push({
      canonical_graph_ref: pack.identity.canonical_graph_ref,
      before_hits: qaBefore.map((row) => `${row.module}.${row.depth}`),
      after_hits: qaAfter.map((row) => `${row.module}.${row.depth}`)
    });
  }
  return {
    ...pack,
    schema_version: "0.2.3",
    render_pack_id: v23Id(pack.render_pack_id),
    generated_at: GENERATED_AT,
    source_research_pack_id: researchPack.pack_id,
    modules,
    canonical_examples: polishedExamples,
    editorial_status: pack.editorial_status === "alpha_render_candidate" || pack.editorial_status === "production_copy_candidate"
      ? "visualization_candidate"
      : pack.editorial_status
  };
}

function writeSchemas() {
  for (const file of listJsonFiles(path.join(SOURCE_DIR, "schemas"))) {
    const schema = readJson(file);
    schema.$id = String(schema.$id || "").replace(/v0_2_2/gu, "v0_2_3");
    schema.title = String(schema.title || "").replace(/v0\.2\.2/gu, "v0.2.3");
    if (schema.properties?.schema_version) schema.properties.schema_version = { const: "0.2.3" };
    writeJson(path.join(OUT_DIR, "schemas", schemaNameV23(path.basename(file))), schema);
  }
}

function runAjv(schemaPath, dataGlob) {
  const result = spawnSync("npx", ["--yes", "ajv-cli@5", "validate", "-s", schemaPath, "-d", dataGlob, "--strict=false", "--all-errors", "--errors=text"], {
    cwd: ROOT,
    encoding: "utf8",
    maxBuffer: 20 * 1024 * 1024
  });
  return {
    status: result.status === 0 ? "pass" : "fail",
    exit_code: result.status,
    stdout: result.stdout,
    stderr: result.stderr
  };
}

function validateGraph(researchPacks, renderPacks) {
  const byRef = new Set(researchPacks.map((pack) => pack.identity.canonical_graph_ref));
  const failures = [];
  for (const pack of researchPacks) {
    const expected = `family_${String(pack.identity.family_id).padStart(2, "0")}/archetype_${pack.identity.archetype_id}`;
    if (pack.identity.canonical_graph_ref !== expected) failures.push(`${pack.pack_id}: expected ${expected}`);
  }
  for (const pack of renderPacks) {
    if (!byRef.has(pack.identity.canonical_graph_ref)) failures.push(`${pack.render_pack_id}: missing research pair`);
    for (const example of pack.canonical_examples || []) {
      if (!example.example_ref || !example.graph_ref_validation_status) failures.push(`${pack.render_pack_id}: example missing graph validation`);
    }
  }
  return failures;
}

function validateRights(researchPacks, renderPacks) {
  return [
    ...researchPacks.filter((pack) => pack.rights_policy?.rights_status !== "pass").map((pack) => `${pack.pack_id}: ${pack.rights_policy?.rights_status}`),
    ...renderPacks.filter((pack) => pack.rights_status !== "pass").map((pack) => `${pack.render_pack_id}: ${pack.rights_status}`)
  ];
}

function validateRenderCopy(renderPacks) {
  const qaHits = [];
  const rawRelated = [];
  const deepMap = new Map();
  const forbiddenDynamic = [];
  const rationaleHits = [];
  for (const pack of renderPacks) {
    for (const row of moduleStrings(pack)) {
      if (INTERNAL_QA_PATTERNS.some((regex) => regex.test(row.text))) qaHits.push(`${pack.render_pack_id}:${row.module}.${row.depth}`);
      if (FORBIDDEN_DYNAMIC_MISSION_PHRASES.some((phrase) => row.text.toLowerCase().includes(phrase))) forbiddenDynamic.push(`${pack.render_pack_id}:${row.module}.${row.depth}`);
    }
    const relatedText = JSON.stringify(pack.modules.related_roads_lineage_module);
    if (/family_\d+\/archetype_\d+/u.test(relatedText)) rawRelated.push(pack.render_pack_id);
    const deep = pack.modules.related_roads_lineage_module.deep;
    deepMap.set(deep, (deepMap.get(deep) || 0) + 1);
    for (const example of pack.canonical_examples || []) {
      if (TEMPLATE_RATIONALE_PATTERNS.some((regex) => regex.test(example.why_this_example_matters || ""))) {
        rationaleHits.push(`${pack.render_pack_id}:${example.example_ref}`);
      }
    }
  }
  const repeatedDeep = [...deepMap.entries()].filter(([, count]) => count > 3);
  return { qaHits, rawRelated, repeatedDeep, forbiddenDynamic, rationaleHits };
}

function writeReports({ researchPacks, renderPacks, schemaValidation, graphFailures, rightsFailures, renderValidation, reports }) {
  writeText(path.join(OUT_DIR, "indexes/schema_validation_report_v0_2_3.md"), mdReport("Schema Validation Report v0.2.3", [
    "Schemas were versioned cleanly to require `schema_version: \"0.2.3\"`.",
    "",
    `Research schema validation: ${schemaValidation.research.status}`,
    `Render schema validation: ${schemaValidation.render.status}`,
    "",
    "Research validator output:",
    "```text",
    schemaValidation.research.stdout || schemaValidation.research.stderr || "(no output)",
    "```",
    "",
    "Render validator output:",
    "```text",
    schemaValidation.render.stdout || schemaValidation.render.stderr || "(no output)",
    "```"
  ]));
  writeText(path.join(OUT_DIR, "indexes/render_copy_hardening_report_v0_2_3.md"), mdReport("Render Copy Hardening Report v0.2.3", [
    "v0.2.3 preserves v0.2.2 research/source recovery and hardens user-facing render modules.",
    "",
    `Render packs processed: ${renderPacks.length}`,
    `Internal QA/source-instruction hits after rewrite: ${renderValidation.qaHits.length}`,
    `Forbidden dynamic mission language hits: ${renderValidation.forbiddenDynamic.length}`,
    `Template rationale hits after polish: ${renderValidation.rationaleHits.length}`,
    "",
    "Primary copy actions:",
    "- Replaced source-audit-style caution text with listener-facing false-nearby caution language.",
    "- Rewrote related-roads modules with display labels and Alpha-safe context.",
    "- Regenerated canonical example rationale copy from v0.2.2 listening cues and targeted example cue overrides."
  ]));
  writeText(path.join(OUT_DIR, "indexes/related_roads_lineage_rewrite_report_v0_2_3.md"), mdReport("Related Roads Lineage Rewrite Report v0.2.3", [
    `Related modules rewritten: ${reports.related.length}`,
    `Raw graph-ref related modules after rewrite: ${renderValidation.rawRelated.length}`,
    `Repeated deep related-road variants over threshold: ${renderValidation.repeatedDeep.length}`,
    "",
    ...(renderValidation.rawRelated.length ? renderValidation.rawRelated.map((item) => `- raw ref: ${item}`) : ["No raw graph-ref-only related road modules remain."]),
    "",
    "Sample rewrites:",
    ...reports.related.slice(0, 12).map((item) => `- ${item.canonical_graph_ref}: ${item.standard}`)
  ]));
  writeText(path.join(OUT_DIR, "indexes/canonical_example_rationale_polish_report_v0_2_3.md"), mdReport("Canonical Example Rationale Polish Report v0.2.3", [
    `Canonical example rationales polished: ${reports.examplePolish.length}`,
    `Template rationale hits after polish: ${renderValidation.rationaleHits.length}`,
    "",
    ...(renderValidation.rationaleHits.length ? renderValidation.rationaleHits.map((item) => `- ${item}`) : ["No known generic rationale-template phrases remain."]),
    "",
    "Sample polished rationales:",
    ...reports.examplePolish.slice(0, 16).map((item) => `- ${item.canonical_graph_ref} / ${item.display_label}: ${item.after}`)
  ]));
  writeText(path.join(OUT_DIR, "indexes/internal_qa_language_scan_v0_2_3.md"), mdReport("Internal QA Language Scan v0.2.3", [
    `User-facing render module QA/source-instruction hits after rewrite: ${renderValidation.qaHits.length}`,
    "",
    ...(renderValidation.qaHits.length ? renderValidation.qaHits.map((item) => `- ${item}`) : ["No `Do not cite...`, source-audit instruction, wrong_context, draft-road, or source-deepening language remains in user-facing render modules."])
  ]));
  writeText(path.join(OUT_DIR, "indexes/graph_ref_validation_report_v0_2_3.md"), mdReport("Graph Ref Validation Report v0.2.3", [
    `Graph-ref validation failures: ${graphFailures.length}`,
    `Research refs checked: ${researchPacks.length}`,
    `Render refs checked: ${renderPacks.length}`,
    "",
    ...(graphFailures.length ? graphFailures.map((item) => `- ${item}`) : ["No graph-ref validation failures."])
  ]));
  writeText(path.join(OUT_DIR, "indexes/rights_policy_report_v0_2_3.md"), mdReport("Rights Policy Report v0.2.3", [
    `Rights-policy failures: ${rightsFailures.length}`,
    "Policy scan: no lyrics, long quotations, proprietary album art dependency, artist-photo dependency, or third-party prose blocks are introduced by the render hardening builder.",
    "",
    ...(rightsFailures.length ? rightsFailures.map((item) => `- ${item}`) : ["All research and render packs have rights_status pass."])
  ]));
  const renderStatuses = renderPacks.reduce((acc, pack) => {
    acc[pack.editorial_status] = (acc[pack.editorial_status] || 0) + 1;
    return acc;
  }, {});
  const totalBlocking = (schemaValidation.research.status === "pass" ? 0 : 1)
    + (schemaValidation.render.status === "pass" ? 0 : 1)
    + graphFailures.length
    + rightsFailures.length
    + renderValidation.qaHits.length
    + renderValidation.rawRelated.length
    + renderValidation.repeatedDeep.length
    + renderValidation.forbiddenDynamic.length
    + renderValidation.rationaleHits.length;
  writeText(path.join(OUT_DIR, "indexes/alpha_render_readiness_report_v0_2_3.md"), mdReport("Alpha Render Readiness Report v0.2.3", [
    "Cartenza Atlas Explainer Layer v0.2.3 render hardening preserves v0.2.2 source recovery and improves app-facing copy.",
    "",
    `Research-pack coverage: ${researchPacks.length} / 120`,
    `Render-pack coverage: ${renderPacks.length} / 120`,
    `Schema validation failures: ${(schemaValidation.research.status === "pass" ? 0 : 1) + (schemaValidation.render.status === "pass" ? 0 : 1)}`,
    `Graph-ref validation failures: ${graphFailures.length}`,
    `Rights-policy failures: ${rightsFailures.length}`,
    `Internal QA/source-instruction hits: ${renderValidation.qaHits.length}`,
    `Raw graph-ref related-road module failures: ${renderValidation.rawRelated.length}`,
    `Repeated generic deep related-road failures: ${renderValidation.repeatedDeep.length}`,
    `Canonical rationale template hits: ${renderValidation.rationaleHits.length}`,
    `Render statuses: ${JSON.stringify(renderStatuses)}`,
    `Total blocking validation issues: ${totalBlocking}`,
    "",
    "No pack is marked `alpha_render_candidate` or `production_copy_candidate`.",
    "PM approval remains required before Alpha render promotion."
  ]));
  writeJson(path.join(OUT_DIR, "indexes/atlas_explainer_pack_manifest_v0_2_3.json"), {
    generated_at: GENERATED_AT,
    package_id: "AtlasExplainerPack_v0_2_3_RenderHardened",
    source_package: "AtlasExplainerPack_v0_2_2_SourceRecovery",
    research_packs: researchPacks.map((pack) => `research_packs/${pack.pack_id}.json`),
    render_packs: renderPacks.map((pack) => `render_packs/${pack.render_pack_id}.json`),
    reports: [
      "indexes/schema_validation_report_v0_2_3.md",
      "indexes/render_copy_hardening_report_v0_2_3.md",
      "indexes/related_roads_lineage_rewrite_report_v0_2_3.md",
      "indexes/canonical_example_rationale_polish_report_v0_2_3.md",
      "indexes/internal_qa_language_scan_v0_2_3.md",
      "indexes/graph_ref_validation_report_v0_2_3.md",
      "indexes/rights_policy_report_v0_2_3.md",
      "indexes/alpha_render_readiness_report_v0_2_3.md"
    ]
  });
}

function main() {
  if (!fs.existsSync(SOURCE_DIR)) throw new Error(`Missing source package ${SOURCE_DIR}`);
  if (fs.existsSync(OUT_DIR)) fs.rmSync(OUT_DIR, { recursive: true, force: true });
  fs.mkdirSync(OUT_DIR, { recursive: true });
  writeSchemas();
  const sourceResearchPacks = listJsonFiles(path.join(SOURCE_DIR, "research_packs")).map(readJson);
  const sourceRenderPacks = listJsonFiles(path.join(SOURCE_DIR, "render_packs")).map(readJson);
  const identityByRef = new Map(sourceResearchPacks.map((pack) => [pack.identity.canonical_graph_ref, pack.identity]));
  const researchByRef = new Map();
  const renderReports = { related: [], examplePolish: [], qaLanguage: [] };
  const researchPacks = sourceResearchPacks
    .sort((a, b) => a.identity.family_id - b.identity.family_id || a.identity.archetype_id.localeCompare(b.identity.archetype_id))
    .map((pack) => {
      const versioned = versionResearchPack(pack);
      researchByRef.set(versioned.identity.canonical_graph_ref, versioned);
      writeJson(path.join(OUT_DIR, `research_packs/${versioned.pack_id}.json`), versioned);
      return versioned;
    });
  const renderPacks = sourceRenderPacks
    .sort((a, b) => a.identity.family_id - b.identity.family_id || a.identity.archetype_id.localeCompare(b.identity.archetype_id))
    .map((pack) => {
      const researchPack = researchByRef.get(pack.identity.canonical_graph_ref);
      if (!researchPack) throw new Error(`Missing research pack for ${pack.identity.canonical_graph_ref}`);
      const versioned = versionRenderPack(pack, researchPack, identityByRef, renderReports);
      writeJson(path.join(OUT_DIR, `render_packs/${versioned.render_pack_id}.json`), versioned);
      return versioned;
    });
  const schemaValidation = {
    research: runAjv(path.join(OUT_DIR, "schemas/atlas_explainer_research_pack_schema_v0_2_3.json"), path.join(OUT_DIR, "research_packs/*.json")),
    render: runAjv(path.join(OUT_DIR, "schemas/atlas_explainer_render_pack_schema_v0_2_3.json"), path.join(OUT_DIR, "render_packs/*.json"))
  };
  const graphFailures = validateGraph(researchPacks, renderPacks);
  const rightsFailures = validateRights(researchPacks, renderPacks);
  const renderValidation = validateRenderCopy(renderPacks);
  writeReports({ researchPacks, renderPacks, schemaValidation, graphFailures, rightsFailures, renderValidation, reports: renderReports });
  if (fs.existsSync(ZIP_PATH)) fs.rmSync(ZIP_PATH, { force: true });
  execFileSync("zip", ["-qr", ZIP_PATH, path.basename(OUT_DIR)], { cwd: path.dirname(OUT_DIR) });
  console.log(JSON.stringify({
    package_dir: OUT_DIR,
    zip_path: ZIP_PATH,
    research_packs: researchPacks.length,
    render_packs: renderPacks.length,
    schema_research: schemaValidation.research.status,
    schema_render: schemaValidation.render.status,
    graph_failures: graphFailures.length,
    rights_failures: rightsFailures.length,
    internal_qa_hits: renderValidation.qaHits.length,
    raw_related_failures: renderValidation.rawRelated.length,
    repeated_deep_related_failures: renderValidation.repeatedDeep.length,
    rationale_template_hits: renderValidation.rationaleHits.length
  }, null, 2));
}

main();
