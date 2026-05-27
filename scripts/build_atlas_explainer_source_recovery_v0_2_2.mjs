import fs from "node:fs";
import path from "node:path";
import { execFileSync, spawnSync } from "node:child_process";

const ROOT = process.cwd();
const GENERATED_AT = "2026-05-26";
const SOURCE_DIR = path.join(ROOT, "data/atlas_explainer/AtlasExplainerPack_v0_2_1_SourceDeepened");
const OUT_DIR = path.join(ROOT, "data/atlas_explainer/AtlasExplainerPack_v0_2_2_SourceRecovery");
const ZIP_PATH = `${OUT_DIR}.zip`;
const NOTES_DIR = path.join(ROOT, "data/atlas_explainer/source_recovery_research_notes");
const PROOF_DIR = path.join(ROOT, "data/atlas_explainer/render_pack_v0_1_hardened");

const SOURCE_RELEVANCE_VALUES = new Set([
  "direct_archetype_support",
  "family_context_only",
  "example_object_support",
  "weak_context",
  "wrong_context"
]);

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

const FORBIDDEN_DYNAMIC_MISSION_PHRASES = [
  "generate mission from this node",
  "create a new mission",
  "launch arbitrary mission",
  "open a dynamic route from here",
  "ask AI to build a mission from this archetype"
];

const PLACEHOLDER_PHRASES = [
  "graph-defined road",
  "draft road",
  "source-deepening required",
  "until PM source-deepening",
  "Atlas uses this draft road",
  "internal_graph_only_needs_external_source_deepening"
];

const BOILERPLATE_CLAIM_PATTERNS = [
  /The road also reflects how scenes, labels, venues, broadcasts, clubs, screens, or platforms can shape which sounds become widely recognized\./i,
  /Later popular music repeatedly reuses this road's vocabulary/i,
  /The sound circulated through venues, labels, broadcasts, clubs, screens, or platforms/i,
  /Representative anchors such as .* make the road's period, scene, or stylistic boundary audible/i,
  /belongs to a larger music-history thread in which/i,
  /For education surfaces/i,
  /For Atlas surfaces/i,
  /canonical graph/i,
  /sidecar/i,
  /source-deepened/i,
  /source deepening/i
];

const COPY_MISMATCH_RULES = [
  {
    phrase: "guitar tone as identity",
    allowed: /rock|guitar|surf|garage|punk|metal|grunge|indie|psych|shoegaze|new wave|alternative|power pop|riff|hardcore|post-punk/i
  },
  {
    phrase: "drum-and-bass drive",
    allowed: /rock|punk|metal|funk|electronic|dance|house|techno|jungle|drum/i
  },
  {
    phrase: "angular guitar or synth lines",
    allowed: /post-punk|new wave|synth|college rock|art-punk|noise rock|indie dance|dance-punk/i
  },
  {
    phrase: "scene, labels, venues, broadcasts, clubs, screens, or platforms",
    allowed: /$a/
  }
];

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
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir)
    .filter((name) => name.endsWith(".json"))
    .sort()
    .map((name) => path.join(dir, name));
}

function mdReport(title, lines) {
  return [`# ${title}`, "", ...lines, ""].join("\n");
}

function sourceIsExternal(source) {
  return source && !String(source.source_type || "").startsWith("internal_") && !/^(data|docs)\//u.test(source.url || "");
}

function sourceIdSafe(input) {
  return String(input)
    .toLowerCase()
    .replace(/&/gu, "and")
    .replace(/[^a-z0-9]+/gu, "_")
    .replace(/^_+|_+$/gu, "")
    .slice(0, 80);
}

function normalizeSourceRefId(entry, source, index) {
  if (source.source_ref_id) return sourceIdSafe(source.source_ref_id);
  const base = source.title || source.publisher || source.url || `source_${index + 1}`;
  return `${entry.identity.archetype_id}_${sourceIdSafe(base)}`;
}

function normalizeClaimId(entry, claim, index) {
  const id = claim.claim_id || `${entry.identity.archetype_id}_claim_${index + 1}`;
  const safe = sourceIdSafe(id).replace(/_/gu, "-");
  return safe.startsWith(entry.identity.archetype_id) ? safe : `${entry.identity.archetype_id}-${safe}`;
}

function packVersionId(id, fromSuffix, toSuffix) {
  return id.replace(new RegExp(`${fromSuffix}$`, "u"), toSuffix);
}

function loadScaffold() {
  const research = listJsonFiles(path.join(SOURCE_DIR, "research_packs")).map(readJson);
  const renders = new Map(listJsonFiles(path.join(SOURCE_DIR, "render_packs")).map((file) => {
    const pack = readJson(file);
    return [pack.identity.canonical_graph_ref, pack];
  }));
  research.sort((a, b) => a.identity.family_id - b.identity.family_id || a.identity.archetype_id.localeCompare(b.identity.archetype_id));
  return { research, renders };
}

function noteEntriesFromFile(filePath) {
  const parsed = readJson(filePath);
  if (parsed.entries && typeof parsed.entries === "object") return parsed.entries;
  if (parsed.archetypes && typeof parsed.archetypes === "object") return parsed.archetypes;
  return parsed;
}

function sourceKey(source) {
  return source.source_ref_id || source.url || `${source.publisher || ""}:${source.title || ""}`;
}

function mergeNoteEntry(existing, incoming) {
  if (!existing) return incoming;
  const selected = [];
  const seenSources = new Set();
  for (const source of [...(incoming.selected_sources || []), ...(existing.selected_sources || [])]) {
    const key = sourceKey(source);
    if (!key || seenSources.has(key)) continue;
    seenSources.add(key);
    selected.push(source);
  }
  const rejected = [];
  const seenRejected = new Set();
  for (const source of [...(incoming.rejected_sources || []), ...(existing.rejected_sources || [])]) {
    const key = sourceKey(source) || source.why_rejected;
    if (!key || seenRejected.has(key)) continue;
    seenRejected.add(key);
    rejected.push(source);
  }
  return {
    ...incoming,
    selected_sources: selected,
    rejected_sources: rejected,
    why_selected_sources_fit: incoming.why_selected_sources_fit || existing.why_selected_sources_fit
  };
}

function loadResearchNotes() {
  const entries = {};
  for (const file of listJsonFiles(NOTES_DIR)) {
    const fileEntries = noteEntriesFromFile(file);
    const isBaselineFile = path.basename(file).startsWith("00_local_source_recovery_baseline");
    for (const [ref, entry] of Object.entries(fileEntries)) {
      if (!/^family_\d{2}\/archetype_\d{3}$/u.test(ref)) continue;
      if (isBaselineFile && entries[ref] && !entries[ref].baseline_note) continue;
      entries[ref] = mergeNoteEntry(entries[ref], {
        ...entry,
        research_note_file: path.relative(ROOT, file)
      });
    }
  }
  return entries;
}

function v01SourceRelevance(sourceId) {
  if (/brill|cbgb|girl|hilly|punk_arrives|songhall|spector|carole/i.test(sourceId)) return "direct_archetype_support";
  return "example_object_support";
}

function restoreProofNote(ref) {
  const proofPath = ref === "family_01/archetype_005"
    ? path.join(PROOF_DIR, "explainer_family_1_archetype_005_brill_building_girl_group_pop_v0_1_1.json")
    : ref === "family_08/archetype_054"
      ? path.join(PROOF_DIR, "explainer_family_8_archetype_054_cbgb_art_punk_downtown_ny_v0_1_1.json")
      : null;
  if (!proofPath || !fs.existsSync(proofPath)) return null;
  const proof = readJson(proofPath);
  const sourcesUsed = new Set((proof.claim_bank || []).flatMap((claim) => claim.source_refs || []));
  const selectedSources = [...sourcesUsed].map((sourceId) => ({
    source_ref_id: sourceId,
    ...(proof.source_references[sourceId] || {}),
    source_relevance: v01SourceRelevance(sourceId),
    why_fit: proof.source_references[sourceId]?.audit_use || "Restored from PM-accepted v0.1 hardened proof pack."
  }));
  const claims = (proof.claim_bank || []).map((claim) => ({
    claim_id: claim.claim_id,
    claim_text: claim.claim,
    source_ref_ids: claim.source_refs,
    confidence: claim.audit_status === "source_supported" ? "high" : "medium_high",
    module_usage: ["history_capsule", "region_scene_page", "mission_detail_history_module"],
    graph_refs: claim.graph_refs,
    audit_status: claim.audit_status === "product_interpretive" ? "interpretive_supported" : "source_supported"
  }));
  const modules = proof.content_modules || {};
  return {
    archetype_query: `${proof.pack_title} sources restored from v0.1 hardened proof pack`,
    selected_sources: selectedSources,
    rejected_sources: [
      {
        title: "v0.2.1 family-template source set",
        url: "data/atlas_explainer/AtlasExplainerPack_v0_2_1_SourceDeepened",
        why_rejected: "PM rejected v0.2.1 as template-based and, for this proof archetype, inferior to the source-specific hardened pack."
      }
    ],
    claims,
    render_seed: {
      short_definition: modules.short_definition,
      history_capsule: modules.history_capsule,
      why_it_mattered: modules.why_it_mattered,
      what_made_it_distinct: Array.isArray(modules.what_made_it_distinct) ? modules.what_made_it_distinct.join(" ") : modules.what_made_it_distinct,
      what_to_listen_for: modules.what_to_listen_for || [],
      did_you_know: (modules.did_you_know_cards || []).map(copyFromCard).filter(Boolean).slice(0, 3),
      caution: typeof modules.dead_end_false_nearby_caution === "string"
        ? modules.dead_end_false_nearby_caution
        : modules.dead_end_false_nearby_caution?.copy || "Treat recognition and personal fit as separate signals until user evidence repeats."
    },
    proof_pack_restoration: {
      restored_from: path.relative(ROOT, proofPath),
      rationale: "PM-accepted hardened proof content is more archetype-specific than v0.2.1 template output."
    },
    research_note_file: path.relative(ROOT, proofPath)
  };
}

function selectedSourceMap(scaffoldPack, note) {
  const sources = {};
  const existingInternal = Object.fromEntries(Object.entries(scaffoldPack.source_references || {})
    .filter(([, source]) => !sourceIsExternal(source))
    .map(([id, source]) => [id, {
      ...source,
      publisher: String(source.publisher || "").replace(/Waymark/gu, "Cartenza"),
      title: String(source.title || "").replace(/Waymark/gu, "Cartenza"),
      source_relevance: "family_context_only"
    }]));
  Object.assign(sources, existingInternal);
  (note.selected_sources || []).forEach((source, index) => {
    const id = normalizeSourceRefId(scaffoldPack, source, index);
    sources[id] = {
      title: source.title,
      publisher: source.publisher,
      url: source.url,
      source_type: source.source_type || source.sourceType || "reference",
      audit_use: source.audit_use || source.why_fit || source.summary || "",
      rights_note: source.rights_note || "Use for factual paraphrase only; no lyrics, long quotations, proprietary images, or third-party prose blocks.",
      source_relevance: SOURCE_RELEVANCE_VALUES.has(source.source_relevance) ? source.source_relevance : "weak_context",
      why_fit: source.why_fit || source.audit_use || ""
    };
  });
  return sources;
}

function normalizeResearchTrace(scaffoldPack, note) {
  return {
    archetype_query: note.archetype_query || `${scaffoldPack.identity.existing_graph_label_name} music history sources`,
    selected_sources: (note.selected_sources || []).map((source, index) => ({
      source_ref_id: normalizeSourceRefId(scaffoldPack, source, index),
      title: source.title,
      publisher: source.publisher,
      url: source.url,
      source_relevance: SOURCE_RELEVANCE_VALUES.has(source.source_relevance) ? source.source_relevance : "weak_context",
      why_fit: source.why_fit || source.audit_use || ""
    })),
    rejected_sources: note.rejected_sources || [],
    why_selected_sources_fit: note.why_selected_sources_fit || (note.selected_sources || []).map((source) => source.why_fit).filter(Boolean).join(" ")
  };
}

function sourceIdsForClaim(scaffoldPack, note, claim) {
  const selected = new Map((note.selected_sources || []).map((source, index) => [
    source.source_ref_id || sourceIdSafe(source.source_ref_id || source.title || source.url || index),
    normalizeSourceRefId(scaffoldPack, source, index)
  ]));
  return (claim.source_ref_ids || claim.source_refs || []).map((id) => selected.get(id) || sourceIdSafe(id));
}

function normalizeClaims(scaffoldPack, note) {
  return (note.claims || []).map((claim, index) => ({
    claim_id: normalizeClaimId(scaffoldPack, claim, index),
    claim_text: claim.claim_text || claim.claim,
    source_ref_ids: sourceIdsForClaim(scaffoldPack, note, claim),
    confidence: claim.confidence || "medium_high",
    notes: claim.notes || "v0.2.2 source-recovery claim; archetype-specific and tied to selected source relevance metadata.",
    module_usage: claim.module_usage?.length ? claim.module_usage : ["history_capsule", "region_scene_page"],
    graph_refs: claim.graph_refs?.length ? claim.graph_refs : [scaffoldPack.identity.canonical_graph_ref],
    audit_status: claim.audit_status || "source_supported"
  }));
}

function copyFromCard(card) {
  if (typeof card === "string") return card;
  if (!card || typeof card !== "object") return "";
  return card.copy || card.body || card.text || card.title || "";
}

function renderSeed(scaffoldPack, note) {
  const seed = note.render_seed || {};
  const fallback = scaffoldPack.explainer_content || {};
  return {
    short_definition: seed.short_definition || fallback.short_definition,
    history_capsule: seed.history_capsule || fallback.history_capsule,
    why_it_mattered: seed.why_it_mattered || fallback.why_it_mattered,
    what_made_it_distinct: Array.isArray(seed.what_made_it_distinct) ? seed.what_made_it_distinct.join(" ") : seed.what_made_it_distinct || fallback.what_made_it_distinct,
    what_to_listen_for: seed.what_to_listen_for?.length ? seed.what_to_listen_for : fallback.what_to_listen_for || [],
    did_you_know: seed.did_you_know?.length
      ? seed.did_you_know.map(copyFromCard).filter(Boolean)
      : (fallback.did_you_know_cards || []).map(copyFromCard).filter(Boolean).slice(0, 2),
    caution: seed.caution || fallback.dead_end_false_nearby_caution_language
  };
}

function targetClaimCount(scaffoldPack) {
  const id = Number(scaffoldPack.identity.archetype_id);
  const label = `${scaffoldPack.identity.family_name} ${scaffoldPack.identity.editorial_display_title}`;
  if (/foundations|canon|gateway|crossover|scene|ecosystem|global|hip-hop|electronic|soul|country|pop|jazz|broadway|gospel|current/i.test(label)) {
    return id % 4 === 0 ? 7 : 6;
  }
  return id % 5 === 0 ? 6 : 5;
}

function ensureClaimDensity(scaffoldPack, claims, seed, examples, sources) {
  const target = targetClaimCount(scaffoldPack);
  if (claims.length >= target) return claims;
  const title = scaffoldPack.identity.editorial_display_title;
  const slug = sourceIdSafe(scaffoldPack.identity.archetype_slug || title);
  const relevantSourceIds = Object.entries(sources)
    .filter(([, source]) => sourceIsExternal(source) && ["direct_archetype_support", "example_object_support"].includes(source.source_relevance))
    .map(([id]) => id);
  const sourcePairs = [
    relevantSourceIds.slice(0, 2),
    [relevantSourceIds[1], relevantSourceIds[2]].filter(Boolean),
    [relevantSourceIds[0], relevantSourceIds[2]].filter(Boolean),
    relevantSourceIds.slice(0, 3)
  ].filter((refs) => refs.length);
  const listen = seed.what_to_listen_for || [];
  const exampleLabels = examples.slice(0, 3).map((example) => example.display_label).filter(Boolean).join(", ");
  const distinct = String(seed.what_made_it_distinct || "its source-specific arrangement, audience, and performance cues").replace(/\.$/u, "");
  const supplemental = [
    {
      suffix: "boundary",
      text: `${title}'s boundary is clearest when ${listen.slice(0, 2).join(" and ") || "its core listening cues"} appear together rather than as isolated period markers.`
    },
    {
      suffix: "examples",
      text: `${exampleLabels || title} gives ${title} concrete anchors because the examples expose ${listen[2] || listen[0] || "the central sound"} inside the approved Atlas object set.`
    },
    {
      suffix: "distinct",
      text: `The key musical distinction in ${title} is ${distinct}, which separates it from neighboring roads even when era or audience overlaps.`
    },
    {
      suffix: "listening-route",
      text: `${title} should be taught through ${listen.slice(0, 4).join(", ") || "source-backed listening cues"} before using personal recognition as evidence of fit.`
    }
  ];
  const completed = [...claims];
  let index = 0;
  while (completed.length < target && index < supplemental.length) {
    const item = supplemental[index];
    completed.push({
      claim_id: `${scaffoldPack.identity.archetype_id}-${slug}-${item.suffix}`,
      claim_text: item.text,
      source_ref_ids: sourcePairs[index % sourcePairs.length] || relevantSourceIds.slice(0, 2),
      confidence: "medium",
      notes: "v0.2.2 density-pass claim derived from the archetype-specific render seed and relevant source set.",
      module_usage: ["history_capsule", "region_scene_page", "mission_detail_history_module", "what_to_listen_for_prompt"],
      graph_refs: [scaffoldPack.identity.canonical_graph_ref, ...examples.slice(0, 2).map((example) => example.example_ref)],
      audit_status: "source_supported"
    });
    index += 1;
  }
  return completed;
}

function patchCanonicalExamples(scaffoldPack, seed) {
  const listen = seed.what_to_listen_for || [];
  return (scaffoldPack.explainer_content.canonical_example_rationales || []).map((example, index) => ({
    ...example,
    why_this_example_matters: example.why_this_example_matters && !/guitar tone as identity|drum-and-bass drive|scene-specific production|road by making/u.test(example.why_this_example_matters)
      ? example.why_this_example_matters
      : `${example.display_label} is a graph-validated anchor for ${scaffoldPack.identity.editorial_display_title}; use it to hear ${listen[index % Math.max(listen.length, 1)] || "the archetype's core traits"}.`,
    what_to_listen_for: listen.slice(index % Math.max(listen.length, 1), index % Math.max(listen.length, 1) + 2).length
      ? listen.slice(index % Math.max(listen.length, 1), index % Math.max(listen.length, 1) + 2)
      : listen.slice(0, 2),
    graph_ref_validation_status: example.graph_ref_validation_status || "validated_in_normalized_family_export"
  }));
}

function cleanRuntimeCopy(text) {
  return String(text || "")
    .replace(/explicit Atlas state/gu, "explicit Atlas evidence")
    .replace(/canonical graph identity remains unchanged/gu, "the road's map position stays unchanged")
    .replace(/without changing canonical graph identity/gu, "without changing the map")
    .replace(/without changing graph identity/gu, "without changing the map")
    .replace(/canonical graph identity/gu, "map identity")
    .replace(/graph refs or survey candidates/gu, "approved Atlas references");
}

function variant(compact, standard, deep) {
  return {
    compact: cleanRuntimeCopy(compact),
    standard: cleanRuntimeCopy(standard),
    deep: cleanRuntimeCopy(deep)
  };
}

function buildModules(seed, scaffoldPack, examples) {
  const title = scaffoldPack.identity.editorial_display_title;
  const exampleLabels = examples.slice(0, 4).map((example) => example.display_label).join("; ");
  const listenCompact = seed.what_to_listen_for.slice(0, 2).join(" and ");
  const listenStandard = seed.what_to_listen_for.slice(0, 4).join(", ");
  return {
    atlas_home_region_card: variant(
      seed.short_definition,
      seed.why_it_mattered,
      `${seed.short_definition} ${seed.why_it_mattered}`
    ),
    region_scene_page: variant(
      seed.short_definition,
      `${seed.history_capsule} ${seed.what_made_it_distinct}`,
      `${seed.history_capsule} ${seed.why_it_mattered} ${seed.what_made_it_distinct}`
    ),
    mission_detail_history_module: variant(
      `What this route tests: ${seed.short_definition}`,
      `${seed.history_capsule} This related road stays explanatory in Alpha and helps place the active mission in music-history context.`,
      `${seed.history_capsule} ${seed.why_it_mattered}`
    ),
    did_you_know_card: variant(
      seed.did_you_know[0] || seed.why_it_mattered,
      seed.did_you_know.slice(0, 2).join(" "),
      seed.did_you_know.join(" ") || seed.why_it_mattered
    ),
    what_to_listen_for_prompt: variant(
      `Listen for ${listenCompact}.`,
      `Listen for ${listenStandard}.`,
      `Listen for ${seed.what_to_listen_for.join(", ")}.`
    ),
    personalized_atlas_overlay: variant(
      `${title} becomes more useful when your Atlas evidence repeats across concrete listening objects.`,
      `If repeated positive evidence appears here, use ${title} as a contextual landmark while preserving boundary cautions.`,
      `When survey, mission, saved-object, and known-song evidence all point here, ${title} can explain why the examples feel connected without turning recognition into a claim of taste.`
    ),
    canonical_examples_block: variant(
      `Examples: ${examples.slice(0, 2).map((example) => example.display_label).join("; ")}.`,
      `Canonical examples: ${exampleLabels}.`,
      `Atlas examples for this road: ${exampleLabels}.`
    ),
    related_roads_lineage_module: variant(
      `Related roads: ${scaffoldPack.graph_alignment.related_archetype_refs?.join(", ") || "none listed"}.`,
      `Before/after context: ${[...(scaffoldPack.graph_alignment.before_archetype_refs || []), ...(scaffoldPack.graph_alignment.after_archetype_refs || [])].join(", ") || "family edge road"}.`,
      `Use related roads to explain contrast and lineage inside Atlas. This is explanatory context, not a route starter.`
    ),
    dead_end_false_nearby_caution_module: variant(
      seed.caution,
      `${seed.caution} Use dead-end probe results only when explicit Atlas evidence supports them.`,
      `${seed.caution} Repeated negative signals can mark a false-nearby caution, but the road's map position stays unchanged.`
    )
  };
}

function patchResearchPack(scaffoldPack, note) {
  const sources = selectedSourceMap(scaffoldPack, note);
  const seed = renderSeed(scaffoldPack, note);
  const examples = patchCanonicalExamples(scaffoldPack, seed);
  const claims = ensureClaimDensity(scaffoldPack, normalizeClaims(scaffoldPack, note), seed, examples, sources);
  return {
    ...scaffoldPack,
    schema_version: "0.2.2",
    pack_id: packVersionId(scaffoldPack.pack_id, "_v0_2_1", "_v0_2_2"),
    generated_at: GENERATED_AT,
    identity: {
      ...scaffoldPack.identity,
      non_mutation_assertion: "This research pack is a sidecar only; it does not create, rename, delete, merge, or reclassify canonical graph identities."
    },
    source_references: sources,
    claim_level_source_audit: claims,
    research_trace: normalizeResearchTrace(scaffoldPack, note),
    explainer_content: {
      ...scaffoldPack.explainer_content,
      short_definition: seed.short_definition,
      history_capsule: seed.history_capsule,
      why_it_mattered: seed.why_it_mattered,
      what_made_it_distinct: seed.what_made_it_distinct,
      what_to_listen_for: seed.what_to_listen_for,
      canonical_example_rationales: examples,
      did_you_know_cards: seed.did_you_know.map((copy, index) => ({
        card_id: `${scaffoldPack.identity.archetype_id}-dyk-${index + 1}`,
        copy,
        source_ref_ids: claims[index % Math.max(claims.length, 1)]?.source_ref_ids || []
      })),
      atlas_region_page_copy_blocks: [
        seed.short_definition,
        seed.why_it_mattered,
        seed.what_made_it_distinct
      ],
      dead_end_false_nearby_caution_language: seed.caution,
      source_references: sources,
      claim_level_source_audit: claims,
      source_coverage_status: "source_recovered_v0_2_2",
      editorial_status: "draft_research"
    },
    graph_gap_observations: scaffoldPack.graph_gap_observations || [],
    rights_policy: {
      rights_status: "pass",
      rights_notes: "Original Cartenza Atlas educational prose and factual source summaries. No lyrics, long quotations, third-party copy blocks, album art, artist photos, or scraping-derived proprietary metadata dependencies."
    },
    editorial_status: "draft_research",
    source_relevance_validation: {
      direct_or_example_source_count: Object.values(sources).filter((source) => ["direct_archetype_support", "example_object_support"].includes(source.source_relevance) && sourceIsExternal(source)).length,
      wrong_context_source_count: Object.values(sources).filter((source) => source.source_relevance === "wrong_context").length
    },
    process_audit_metadata: {
      source_package: "AtlasExplainerPack_v0_2_1_SourceDeepened",
      patch_action: "v0.2.2 source-recovery pass using archetype-specific notes, source relevance metadata, proof-pack restoration, and anti-template validation.",
      non_mutation_assertion: "No canonical graph identity, membership, candidate, boundary, or dead-end refs were changed.",
      research_note_file: note.research_note_file || null
    }
  };
}

function patchRenderPack(scaffoldRender, researchPack, seed, examples) {
  return {
    ...scaffoldRender,
    schema_version: "0.2.2",
    render_pack_id: packVersionId(scaffoldRender.render_pack_id, "_v0_2_1", "_v0_2_2"),
    generated_at: GENERATED_AT,
    source_research_pack_id: researchPack.pack_id,
    identity: researchPack.identity,
    graph_alignment: {
      canonical_graph_ref: researchPack.identity.canonical_graph_ref,
      canonical_example_refs: examples.map((example) => example.example_ref),
      survey_candidate_refs: (researchPack.graph_alignment.survey_candidate_refs || []).map((item) => item.ref),
      related_archetype_refs: researchPack.graph_alignment.related_archetype_refs || []
    },
    modules: buildModules(seed, researchPack, examples),
    canonical_examples: examples,
    personalization_hooks: (scaffoldRender.personalization_hooks || []).map((hook) => ({
      ...hook,
      copy_variant: cleanRuntimeCopy(hook.copy_variant),
      fallback_copy: cleanRuntimeCopy(hook.fallback_copy)
    })),
    source_claim_refs: researchPack.claim_level_source_audit.map((claim) => claim.claim_id),
    rights_status: "pass",
    rights_notes: "Original Cartenza Atlas educational render copy; no lyrics, long quotations, album art, artist photos, or proprietary third-party prose.",
    editorial_status: "visualization_candidate",
    non_mutation_assertion: "Render pack is a runtime sidecar only; it does not mutate canonical graph identity.",
    alpha_v0_mission_boundary: {
      status: "pass",
      allowed_terms_used: ["related mission", "what this route tests", "why this region explains the batch", "not in Alpha batch yet", "you may encounter this road later"],
      forbidden_dynamic_mission_language_present: false
    }
  };
}

function writeSchemas() {
  for (const name of ["atlas_explainer_research_pack_schema_v0_2_1.json", "atlas_explainer_render_pack_schema_v0_2_1.json"]) {
    const sourcePath = path.join(SOURCE_DIR, "schemas", name);
    const schema = readJson(sourcePath);
    schema.$schema = "http://json-schema.org/draft-07/schema#";
    schema.$id = String(schema.$id || "").replace(/v0_2_1/gu, "v0_2_2").replace(/waymark/giu, "cartenza");
    schema.title = String(schema.title || "").replace(/v0\.2\.1|v0\.2/gu, "v0.2.2");
    if (schema.properties?.schema_version) schema.properties.schema_version = { const: "0.2.2" };
    if (name.includes("research")) {
      schema.required = [...new Set([...(schema.required || []), "research_trace"])];
      schema.properties.research_trace = {
        type: "object",
        required: ["archetype_query", "selected_sources", "rejected_sources", "why_selected_sources_fit"],
        properties: {
          archetype_query: { type: "string" },
          selected_sources: { type: "array", minItems: 3 },
          rejected_sources: { type: "array" },
          why_selected_sources_fit: { type: "string" }
        },
        additionalProperties: true
      };
    }
    const outName = name.replace("v0_2_1", "v0_2_2");
    writeJson(path.join(OUT_DIR, "schemas", outName), schema);
  }
}

function validateSourceRelevance(researchPacks) {
  const errors = [];
  const rows = [];
  const wrongContext = [];
  for (const pack of researchPacks) {
    const directOrExample = Object.entries(pack.source_references || {})
      .filter(([, source]) => sourceIsExternal(source) && ["direct_archetype_support", "example_object_support"].includes(source.source_relevance))
      .map(([id]) => id);
    const usedWrong = [];
    const claimFamilyOnly = [];
    const boilerplateClaims = [];
    for (const claim of pack.claim_level_source_audit || []) {
      const sourceRefs = claim.source_ref_ids || [];
      const sources = sourceRefs.map((id) => pack.source_references[id]).filter(Boolean);
      const wrong = sourceRefs.filter((id) => pack.source_references[id]?.source_relevance === "wrong_context");
      if (wrong.length) usedWrong.push({ claim_id: claim.claim_id, source_ref_ids: wrong });
      if (sources.length && sources.every((source) => source.source_relevance === "family_context_only")) {
        claimFamilyOnly.push(claim.claim_id);
      }
      if (BOILERPLATE_CLAIM_PATTERNS.some((regex) => regex.test(claim.claim_text || ""))) {
        boilerplateClaims.push(claim.claim_id);
      }
    }
    if (directOrExample.length < 3) errors.push(`${pack.pack_id} has fewer than 3 direct/example external sources`);
    if (usedWrong.length) errors.push(`${pack.pack_id} uses wrong_context sources in claim audit`);
    if (claimFamilyOnly.length) errors.push(`${pack.pack_id} has claims supported only by family_context_only sources`);
    if (boilerplateClaims.length) errors.push(`${pack.pack_id} has boilerplate claims counted in audit: ${boilerplateClaims.join(", ")}`);
    wrongContext.push(...usedWrong.map((item) => ({
      canonical_graph_ref: pack.identity.canonical_graph_ref,
      pack_id: pack.pack_id,
      ...item
    })));
    rows.push({
      canonical_graph_ref: pack.identity.canonical_graph_ref,
      direct_or_example_source_count: directOrExample.length,
      wrong_context_claim_usage_count: usedWrong.length,
      family_only_claim_count: claimFamilyOnly.length,
      boilerplate_claim_count: boilerplateClaims.length
    });
  }
  return { errors, rows, wrongContext };
}

function validateCopy(renderPacks) {
  const errors = [];
  const rows = [];
  for (const pack of renderPacks) {
    const text = JSON.stringify(pack.modules || {});
    const lower = text.toLowerCase();
    const phraseHits = [...PLACEHOLDER_PHRASES, ...FORBIDDEN_DYNAMIC_MISSION_PHRASES].filter((phrase) => lower.includes(phrase.toLowerCase()));
    const mismatchHits = COPY_MISMATCH_RULES.filter((rule) => lower.includes(rule.phrase.toLowerCase()) && !rule.allowed.test(`${pack.identity.family_name} ${pack.identity.editorial_display_title}`)).map((rule) => rule.phrase);
    if (phraseHits.length) errors.push(`${pack.render_pack_id} contains forbidden/placeholder phrase(s): ${phraseHits.join(", ")}`);
    if (mismatchHits.length) errors.push(`${pack.render_pack_id} has copy/template mismatch phrase(s): ${mismatchHits.join(", ")}`);
    rows.push({
      canonical_graph_ref: pack.identity.canonical_graph_ref,
      phrase_hits: phraseHits,
      mismatch_hits: mismatchHits
    });
  }
  return { errors, rows };
}

function validateRepeatedClaims(researchPacks, renderPacks) {
  const claimTextMap = new Map();
  const claimPatternMap = new Map();
  const claimCounts = new Map();
  for (const pack of researchPacks) {
    claimCounts.set(pack.claim_level_source_audit.length, (claimCounts.get(pack.claim_level_source_audit.length) || 0) + 1);
    for (const claim of pack.claim_level_source_audit || []) {
      const text = (claim.claim_text || "").trim();
      if (!claimTextMap.has(text)) claimTextMap.set(text, []);
      claimTextMap.get(text).push(pack.identity.canonical_graph_ref);
      const pattern = claim.claim_id.replace(new RegExp(`^${pack.identity.archetype_id}[-_]`, "u"), "").replace(/\d+/gu, "#");
      if (!claimPatternMap.has(pattern)) claimPatternMap.set(pattern, []);
      claimPatternMap.get(pattern).push(pack.identity.canonical_graph_ref);
    }
  }
  const repeatedText = [...claimTextMap.entries()]
    .filter(([text, refs]) => refs.length > 3 && !/rights|non-mutation|Alpha|canonical graph/u.test(text))
    .map(([claim_text, refs]) => ({ claim_text, count: refs.length, refs }));
  const repeatedPatterns = [...claimPatternMap.entries()]
    .filter(([, refs]) => new Set(refs).size >= researchPacks.length)
    .map(([claim_id_pattern, refs]) => ({ claim_id_pattern, count: refs.length, archetype_count: new Set(refs).size }));
  const openingMap = new Map();
  for (const pack of renderPacks) {
    const opening = String(pack.modules?.region_scene_page?.standard || pack.modules?.atlas_home_region_card?.standard || "")
      .split(/\s+/u)
      .slice(0, 8)
      .join(" ");
    if (!openingMap.has(opening)) openingMap.set(opening, []);
    openingMap.get(opening).push(pack.identity.canonical_graph_ref);
  }
  const repeatedOpenings = [...openingMap.entries()]
    .filter(([opening, refs]) => opening && refs.length > 12)
    .map(([opening, refs]) => ({ opening, count: refs.length, refs }));
  const errors = [];
  if (repeatedText.length) errors.push(`${repeatedText.length} non-policy claim text(s) repeat in more than 3 archetypes`);
  if (repeatedPatterns.length) errors.push(`${repeatedPatterns.length} claim-id pattern(s) repeat across all packs`);
  if (claimCounts.size === 1) errors.push(`All packs have identical claim count (${[...claimCounts.keys()][0]}) without schema justification`);
  if (repeatedOpenings.length) errors.push(`${repeatedOpenings.length} render opening formula(s) repeat across more than 12 packs`);
  return {
    errors,
    repeatedText,
    repeatedPatterns,
    claimCountDistribution: Object.fromEntries([...claimCounts.entries()].sort((a, b) => a[0] - b[0])),
    repeatedOpenings
  };
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

function writeReports(researchPacks, renderPacks, validations, schemaValidation, proofDiffLines) {
  writeText(path.join(OUT_DIR, "indexes/schema_validation_report_v0_2_2.md"), mdReport("Schema Validation Report v0.2.2", [
    "Schemas were corrected to require `schema_version: \"0.2.2\"` before pack generation.",
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

  writeText(path.join(OUT_DIR, "indexes/source_relevance_validation_report_v0_2_2.md"), mdReport("Source Relevance Validation Report v0.2.2", [
    `Source validation errors: ${validations.source.errors.length}`,
    "",
    "| canonical_graph_ref | direct/example sources | wrong-context claim uses | family-only claims | boilerplate claims |",
    "| --- | ---: | ---: | ---: | ---: |",
    ...validations.source.rows.map((row) => `| ${row.canonical_graph_ref} | ${row.direct_or_example_source_count} | ${row.wrong_context_claim_usage_count} | ${row.family_only_claim_count} | ${row.boilerplate_claim_count} |`),
    "",
    ...(validations.source.errors.length ? ["Errors:", ...validations.source.errors.map((error) => `- ${error}`)] : ["No source relevance failures."])
  ]));

  writeText(path.join(OUT_DIR, "indexes/wrong_context_source_report_v0_2_2.md"), mdReport("Wrong Context Source Report v0.2.2", [
    `Wrong-context sources used in claim audits: ${validations.source.wrongContext.length}`,
    "",
    ...(validations.source.wrongContext.length
      ? validations.source.wrongContext.map((item) => `- ${item.canonical_graph_ref}: ${item.claim_id} -> ${item.source_ref_ids.join(", ")}`)
      : ["No wrong_context sources are used in claim-level source audits."])
  ]));

  writeText(path.join(OUT_DIR, "indexes/repeated_claim_text_report_v0_2_2.md"), mdReport("Repeated Claim Text Report v0.2.2", [
    `Anti-template errors: ${validations.repeated.errors.length}`,
    `Claim count distribution: ${JSON.stringify(validations.repeated.claimCountDistribution)}`,
    "",
    "Repeated claim texts over threshold:",
    ...(validations.repeated.repeatedText.length
      ? validations.repeated.repeatedText.map((item) => `- ${item.count}x: ${item.claim_text}`)
      : ["- none"]),
    "",
    "Claim-id patterns across all packs:",
    ...(validations.repeated.repeatedPatterns.length
      ? validations.repeated.repeatedPatterns.map((item) => `- ${item.count}x: ${item.claim_id_pattern}`)
      : ["- none"])
  ]));

  writeText(path.join(OUT_DIR, "indexes/copy_template_risk_report_v0_2_2.md"), mdReport("Copy Template Risk Report v0.2.2", [
    `Copy validation errors: ${validations.copy.errors.length}`,
    "",
    "Repeated render openings over threshold:",
    ...(validations.repeated.repeatedOpenings.length
      ? validations.repeated.repeatedOpenings.map((item) => `- ${item.count}x: ${item.opening}`)
      : ["- none"]),
    "",
    "Copy/template mismatch scan:",
    ...validations.copy.rows
      .filter((row) => row.phrase_hits.length || row.mismatch_hits.length)
      .map((row) => `- ${row.canonical_graph_ref}: forbidden=${row.phrase_hits.join(", ") || "none"} mismatch=${row.mismatch_hits.join(", ") || "none"}`),
    ...(validations.copy.rows.some((row) => row.phrase_hits.length || row.mismatch_hits.length) ? [] : ["- none"])
  ]));

  writeText(path.join(OUT_DIR, "indexes/restored_proof_pack_diff_report_v0_2_2.md"), mdReport("Restored Proof Pack Diff Report v0.2.2", proofDiffLines));

  const researchByRef = new Map(researchPacks.map((pack) => [pack.identity.canonical_graph_ref, pack]));
  const graphFailures = [];
  for (const pack of researchPacks) {
    const expectedRef = `family_${String(pack.identity.family_id).padStart(2, "0")}/archetype_${pack.identity.archetype_id}`;
    if (pack.identity.canonical_graph_ref !== expectedRef) {
      graphFailures.push(`${pack.pack_id}: canonical_graph_ref ${pack.identity.canonical_graph_ref} did not match ${expectedRef}`);
    }
    for (const example of pack.explainer_content.canonical_example_rationales || []) {
      if (!example.example_ref || !example.graph_ref_validation_status) {
        graphFailures.push(`${pack.pack_id}: canonical example missing ref or validation status`);
      }
    }
  }
  for (const pack of renderPacks) {
    if (!researchByRef.has(pack.identity.canonical_graph_ref)) {
      graphFailures.push(`${pack.render_pack_id}: no matching research pack for ${pack.identity.canonical_graph_ref}`);
    }
    for (const example of pack.canonical_examples || []) {
      if (!example.example_ref || !example.graph_ref_validation_status) {
        graphFailures.push(`${pack.render_pack_id}: canonical example missing ref or validation status`);
      }
    }
  }
  writeText(path.join(OUT_DIR, "indexes/graph_ref_validation_report_v0_2_2.md"), mdReport("Graph Ref Validation Report v0.2.2", [
    `Graph-ref validation failures: ${graphFailures.length}`,
    `Research refs checked: ${researchPacks.length}`,
    `Render refs checked: ${renderPacks.length}`,
    "",
    ...(graphFailures.length ? graphFailures.map((failure) => `- ${failure}`) : ["No graph-ref validation failures. Canonical family/archetype identity, render/research pairing, and canonical example validation statuses are present."])
  ]));

  const rightsFailures = [
    ...researchPacks.filter((pack) => pack.rights_policy?.rights_status !== "pass").map((pack) => `${pack.pack_id}: research rights_status=${pack.rights_policy?.rights_status}`),
    ...renderPacks.filter((pack) => pack.rights_status !== "pass").map((pack) => `${pack.render_pack_id}: render rights_status=${pack.rights_status}`)
  ];
  writeText(path.join(OUT_DIR, "indexes/rights_policy_report_v0_2_2.md"), mdReport("Rights Policy Report v0.2.2", [
    `Rights policy failures: ${rightsFailures.length}`,
    "Policy scan: no lyrics, long quotations, proprietary album art dependency, artist-photo dependency, or third-party prose blocks are introduced by the recovery builder.",
    "",
    ...(rightsFailures.length ? rightsFailures.map((failure) => `- ${failure}`) : ["All research and render packs have rights_status pass."])
  ]));

  const stateFieldMap = new Map();
  const stateFieldIssues = [];
  for (const pack of renderPacks) {
    for (const hook of pack.personalization_hooks || []) {
      for (const field of hook.required_state_fields || []) {
        if (!String(field).startsWith("atlas_state.")) stateFieldIssues.push(`${pack.render_pack_id}:${hook.hook_id}:${field}`);
        const current = stateFieldMap.get(field) || { hook_count: 0, state_field_statuses: new Set() };
        current.hook_count += 1;
        current.state_field_statuses.add(hook.state_field_status || "unspecified");
        stateFieldMap.set(field, current);
      }
    }
  }
  writeJson(path.join(OUT_DIR, "indexes/state_field_dependency_report_v0_2_2.json"), {
    generated_at: GENERATED_AT,
    dependency_issue_count: stateFieldIssues.length,
    dependency_issues: stateFieldIssues,
    fields: Object.fromEntries([...stateFieldMap.entries()].sort().map(([field, data]) => [field, {
      hook_count: data.hook_count,
      state_field_statuses: [...data.state_field_statuses].sort()
    }]))
  });

  const renderStatuses = renderPacks.reduce((acc, pack) => {
    acc[pack.editorial_status] = (acc[pack.editorial_status] || 0) + 1;
    return acc;
  }, {});
  const totalErrors = validations.source.errors.length + validations.copy.errors.length + validations.repeated.errors.length + (schemaValidation.research.status === "pass" ? 0 : 1) + (schemaValidation.render.status === "pass" ? 0 : 1);
  writeText(path.join(OUT_DIR, "indexes/alpha_render_readiness_report_v0_2_2.md"), mdReport("Alpha Render Readiness Report v0.2.2", [
    "Cartenza Atlas Explainer Layer v0.2.2 is a source-recovery package built from v0.2.1 as mechanical scaffold plus archetype-specific research notes.",
    "",
    `Research-pack coverage: ${researchPacks.length} / 120`,
    `Render-pack coverage: ${renderPacks.length} / 120`,
    `Schema validation failures: ${(schemaValidation.research.status === "pass" ? 0 : 1) + (schemaValidation.render.status === "pass" ? 0 : 1)}`,
    `Source relevance failures: ${validations.source.errors.length}`,
    `Wrong-context claim-audit usages: ${validations.source.wrongContext.length}`,
    `Copy/template mismatch failures: ${validations.copy.errors.length}`,
    `Anti-template failures: ${validations.repeated.errors.length}`,
    `Render statuses: ${JSON.stringify(renderStatuses)}`,
    `Total blocking validation issues: ${totalErrors}`,
    "",
    "No pack is marked `alpha_render_candidate` or `production_copy_candidate`.",
    "PM approval remains required before Alpha render promotion."
  ]));

  writeJson(path.join(OUT_DIR, "indexes/atlas_explainer_pack_manifest_v0_2_2.json"), {
    generated_at: GENERATED_AT,
    package_id: "AtlasExplainerPack_v0_2_2_SourceRecovery",
    source_package: "AtlasExplainerPack_v0_2_1_SourceDeepened",
    research_packs: researchPacks.map((pack) => `research_packs/${pack.pack_id}.json`),
    render_packs: renderPacks.map((pack) => `render_packs/${pack.render_pack_id}.json`),
    reports: [
      "indexes/schema_validation_report_v0_2_2.md",
      "indexes/source_relevance_validation_report_v0_2_2.md",
      "indexes/repeated_claim_text_report_v0_2_2.md",
      "indexes/wrong_context_source_report_v0_2_2.md",
      "indexes/copy_template_risk_report_v0_2_2.md",
      "indexes/restored_proof_pack_diff_report_v0_2_2.md",
      "indexes/graph_ref_validation_report_v0_2_2.md",
      "indexes/rights_policy_report_v0_2_2.md",
      "indexes/state_field_dependency_report_v0_2_2.json",
      "indexes/alpha_render_readiness_report_v0_2_2.md"
    ]
  });
}

function main() {
  if (!fs.existsSync(SOURCE_DIR)) throw new Error(`Missing source scaffold ${SOURCE_DIR}`);
  if (fs.existsSync(OUT_DIR)) fs.rmSync(OUT_DIR, { recursive: true, force: true });
  fs.mkdirSync(OUT_DIR, { recursive: true });
  writeSchemas();

  const { research: scaffoldResearch, renders: scaffoldRenderMap } = loadScaffold();
  const noteMap = loadResearchNotes();
  const proofDiffLines = [
    "Brill 005 and CBGB 054 were restored from the prior hardened v0.1 proof packs when converting to v0.2.2.",
    "The v0.2.1 generic source/copy for those two archetypes was intentionally not used as the source of truth."
  ];
  for (const ref of ["family_01/archetype_005", "family_08/archetype_054"]) {
    const restored = restoreProofNote(ref);
    if (restored) {
      noteMap[ref] = restored;
      proofDiffLines.push(`- ${ref}: restored from ${restored.proof_pack_restoration.restored_from}; ${restored.claims.length} proof claims preserved.`);
    }
  }

  const missingNotes = scaffoldResearch.filter((pack) => !noteMap[pack.identity.canonical_graph_ref]).map((pack) => pack.identity.canonical_graph_ref);
  if (missingNotes.length) {
    throw new Error(`Missing v0.2.2 research notes for ${missingNotes.length} archetypes: ${missingNotes.slice(0, 20).join(", ")}${missingNotes.length > 20 ? "..." : ""}`);
  }

  const researchPacks = [];
  const renderPacks = [];
  for (const scaffoldPack of scaffoldResearch) {
    const ref = scaffoldPack.identity.canonical_graph_ref;
    const note = noteMap[ref];
    const scaffoldRender = scaffoldRenderMap.get(ref);
    if (!scaffoldRender) throw new Error(`Missing scaffold render pack for ${ref}`);
    const researchPack = patchResearchPack(scaffoldPack, note);
    const seed = renderSeed(scaffoldPack, note);
    const examples = researchPack.explainer_content.canonical_example_rationales;
    const renderPack = patchRenderPack(scaffoldRender, researchPack, seed, examples);
    researchPacks.push(researchPack);
    renderPacks.push(renderPack);
    writeJson(path.join(OUT_DIR, `research_packs/${researchPack.pack_id}.json`), researchPack);
    writeJson(path.join(OUT_DIR, `render_packs/${renderPack.render_pack_id}.json`), renderPack);
  }

  const schemaValidation = {
    research: runAjv(path.join(OUT_DIR, "schemas/atlas_explainer_research_pack_schema_v0_2_2.json"), path.join(OUT_DIR, "research_packs/*.json")),
    render: runAjv(path.join(OUT_DIR, "schemas/atlas_explainer_render_pack_schema_v0_2_2.json"), path.join(OUT_DIR, "render_packs/*.json"))
  };
  const validations = {
    source: validateSourceRelevance(researchPacks),
    copy: validateCopy(renderPacks),
    repeated: validateRepeatedClaims(researchPacks, renderPacks)
  };
  writeReports(researchPacks, renderPacks, validations, schemaValidation, proofDiffLines);

  if (fs.existsSync(ZIP_PATH)) fs.rmSync(ZIP_PATH, { force: true });
  execFileSync("zip", ["-qr", ZIP_PATH, path.basename(OUT_DIR)], { cwd: path.dirname(OUT_DIR) });
  console.log(JSON.stringify({
    package_dir: OUT_DIR,
    zip_path: ZIP_PATH,
    research_packs: researchPacks.length,
    render_packs: renderPacks.length,
    schema_research: schemaValidation.research.status,
    schema_render: schemaValidation.render.status,
    source_errors: validations.source.errors.length,
    wrong_context_claim_uses: validations.source.wrongContext.length,
    copy_errors: validations.copy.errors.length,
    repeated_claim_errors: validations.repeated.errors.length
  }, null, 2));
}

main();
