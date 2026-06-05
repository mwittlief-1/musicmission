import fs from "node:fs";
import path from "node:path";
import { execFileSync, spawnSync } from "node:child_process";

const ROOT = process.cwd();
const GENERATED_AT = "2026-06-04";
const VERSION = "0.3";
const PACKAGE_ID = "AtlasExplainerPack_v0_3_ProfileLadders";
const SOURCE_DIR = path.join(ROOT, "data/atlas_explainer/AtlasExplainerPack_v0_2_3_RenderHardened");
const OUT_DIR = path.join(ROOT, "data/atlas_explainer", PACKAGE_ID);
const ZIP_PATH = `${OUT_DIR}.zip`;
const ACTIVE_INVENTORY_PATH = path.join(ROOT, "data/canonical_graph/current/canonical_graph_active_inventory.json");
const PROFILE_TARGETS_PATH = path.join(ROOT, "data/canonical_graph/current/atlas_archetype_profile_targets.json");
const APP_RESOURCE_PATH = path.join(ROOT, "MusicAtlasController/Resources/atlas_explainer_render_packs_v0_3.json");

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

const INTERNAL_QA_PATTERNS = [
  /do not cite/i,
  /wrong_context/i,
  /family_context_only/i,
  /source-audit/i,
  /source-deepening/i,
  /source deepening/i,
  /graph-defined road/i,
  /draft road/i,
  /until PM/i,
  /Atlas uses this draft road/i
];

const RECOGNITION_WEIGHT = {
  obvious: 4,
  medium: 3,
  deep: 2,
  low: 1,
  unknown: 0
};

const ROLE_WEIGHT = {
  anchor: 5,
  album_world: 4,
  bridge: 4,
  boundary_case: 3,
  deep_cut: 2,
  context: 1
};

const TYPE_WEIGHT = {
  song: 4,
  recording: 4,
  album: 3,
  artist_anchor: 2
};

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function writeJson(filePath, value) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, `${JSON.stringify(value, null, 2)}\n`);
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

function sentence(text) {
  return String(text || "")
    .replace(/\s+/gu, " ")
    .trim()
    .replace(/\.$/u, "");
}

function firstSentence(text, maxLength = 260) {
  const cleaned = sentence(text);
  const first = cleaned.split(/(?<=\.)\s+/u)[0]?.replace(/\.$/u, "") || cleaned;
  if (first.length <= maxLength) return first;
  return `${first.slice(0, maxLength).replace(/\s+\S*$/u, "")}...`;
}

function readableList(items) {
  const values = items.filter(Boolean);
  if (!values.length) return "";
  if (values.length === 1) return values[0];
  if (values.length === 2) return `${values[0]} and ${values[1]}`;
  return `${values.slice(0, -1).join(", ")}, and ${values.at(-1)}`;
}

function splitSentences(text) {
  const cleaned = sentence(text);
  if (!cleaned) return [];
  return cleaned
    .split(/(?<=[.!?])\s+/u)
    .map((value) => value.trim())
    .filter(Boolean);
}

function slugify(value) {
  return String(value || "")
    .toLowerCase()
    .normalize("NFKD")
    .replace(/[^\w\s-]/gu, "")
    .trim()
    .replace(/[\s_]+/gu, "-")
    .replace(/-+/gu, "-");
}

function versionedId(id) {
  return String(id || "")
    .replace(/_v0_2_3$/u, "_v0_3")
    .replace(/_v0_2_2$/u, "_v0_3")
    .replace(/_v0_2_1$/u, "_v0_3")
    .replace(/_v0_2$/u, "_v0_3");
}

function versionedFileName(name) {
  return name
    .replace("_v0_2_3", "_v0_3")
    .replace("_v0_2_2", "_v0_3")
    .replace("_v0_2_1", "_v0_3")
    .replace("_v0_2", "_v0_3");
}

function normalizeArtistKey(artist) {
  const normalized = String(artist || "")
    .toLowerCase()
    .replace(/&/gu, " and ")
    .replace(/\bgroup\b/gu, "")
    .replace(/^the\s+/u, "")
    .replace(/[^\p{L}\p{N}]+/gu, " ")
    .replace(/\s+/gu, " ")
    .trim();
  return normalized
    .replace(/\bsnoop doggy dogg\b/u, "snoop dogg")
    .replace(/\s+/gu, " ")
    .trim();
}

function artistMentionKeys(artist) {
  const raw = String(artist || "");
  const whole = normalizeArtistKey(raw);
  const pieces = raw
    .replace(/\b(?:feat|ft)(?:\.|uring)?\b/giu, "featuring")
    .split(/\s+featuring\.?\s+|,|\s+&\s+|\s+and\s+/giu)
    .map(normalizeArtistKey)
    .filter((value) => value.length > 2);
  return [...new Set([whole, ...pieces].filter(Boolean))];
}

function normalizeTitleKey(title) {
  return String(title || "")
    .toLowerCase()
    .normalize("NFKD")
    .replace(/[^\p{L}\p{N}]+/gu, " ")
    .replace(/\s+/gu, " ")
    .trim();
}

function candidateTypeToExampleType(type) {
  if (type === "artist_anchor") return "artist";
  if (type === "album") return "album";
  return "song_recording";
}

function displayLabel(row) {
  if (row.candidate_type === "artist_anchor") return row.artist_display_name || row.title;
  return `${row.title} - ${row.artist_display_name}`;
}

function proseLabel(row) {
  if (row.candidate_type === "artist_anchor") return row.artist_display_name || row.title;
  return `${row.title} by ${row.artist_display_name}`;
}

function sceneLabel(row) {
  if (row.candidate_type === "artist_anchor") return row.artist_display_name || row.title;
  const artist = row.artist_display_name || "";
  const possessive = artist.endsWith("s") ? `${artist}'` : `${artist}'s`;
  return `${possessive} ${row.title}`;
}

function exampleRef(row) {
  return row.candidate_identity_key;
}

function sourceGraphRef(row) {
  const slug = row.candidate_type === "artist_anchor"
    ? slugify(row.artist_display_name || row.title)
    : `${slugify(row.artist_display_name)}-${slugify(row.title)}`;
  if (row.candidate_type === "artist_anchor") return `artist:${slug}`;
  if (row.candidate_type === "album") return `album:${slug}`;
  return `song_recording:${slug}`;
}

function cleanForUserCopy(text) {
  return sentence(text)
    .replace(/\bsource[- ]audit\b/giu, "audit")
    .replace(/\bgraph-defined road\b/giu, "road")
    .replace(/\bdraft road\b/giu, "road");
}

function getListenCues(researchPack) {
  const cues = researchPack.explainer_content?.what_to_listen_for || [];
  return cues.filter(Boolean).map((cue) => sentence(cue)).filter(Boolean).slice(0, 6);
}

function scoreCandidate(row, section = "general") {
  const recognition = RECOGNITION_WEIGHT[row.recognition_band] ?? 0;
  const role = ROLE_WEIGHT[row.mission_role] ?? 0;
  const type = TYPE_WEIGHT[row.candidate_type] ?? 0;
  const year = Number.isFinite(row.year) ? Math.max(0, 2200 - row.year) / 10000 : 0;
  const sectionBoost = section === "scene" && row.mission_role === "anchor" ? 2 : 0;
  const startBoost = section === "start_here" && row.candidate_type !== "artist_anchor" ? 1.5 : 0;
  const deepBoost = section === "go_deep" && row.recognition_band === "deep" ? 2 : 0;
  return recognition * 10 + role * 4 + type + sectionBoost + startBoost + deepBoost + year;
}

function sortedCandidates(candidates, section) {
  return [...candidates].sort((a, b) => {
    const scoreDelta = scoreCandidate(b, section) - scoreCandidate(a, section);
    if (scoreDelta) return scoreDelta;
    const yearA = Number.isFinite(a.year) ? a.year : 9999;
    const yearB = Number.isFinite(b.year) ? b.year : 9999;
    if (yearA !== yearB) return yearA - yearB;
    return displayLabel(a).localeCompare(displayLabel(b));
  });
}

function canUseCandidate(row, state, options = {}) {
  const exact = exampleRef(row);
  if (state.usedRefs.has(exact)) return false;
  if (state.usedDisplayLabels.has(displayLabel(row).toLowerCase())) return false;
  if (row.candidate_type !== "artist_anchor" && state.usedObjectTitles.has(normalizeTitleKey(row.title))) return false;
  if (options.skipSceneRefs && state.sceneRefs.has(exact)) return false;
  return artistMentionKeys(row.artist_display_name || row.title)
    .every((key) => (state.artistMentionCounts.get(key) || 0) < (options.artistCap ?? 2));
}

function markCandidate(row, state, { scene = false } = {}) {
  const exact = exampleRef(row);
  state.usedRefs.add(exact);
  state.usedDisplayLabels.add(displayLabel(row).toLowerCase());
  if (row.candidate_type !== "artist_anchor") state.usedObjectTitles.add(normalizeTitleKey(row.title));
  if (scene) state.sceneRefs.add(exact);
  for (const key of artistMentionKeys(row.artist_display_name || row.title)) {
    state.artistMentionCounts.set(key, (state.artistMentionCounts.get(key) || 0) + 1);
  }
}

function selectCandidates(pool, state, {
  section,
  target,
  recognitionBands,
  preferTypes = [],
  artistCap = 2,
  skipSceneRefs = false
}) {
  const preferred = sortedCandidates(pool.filter((row) => recognitionBands.includes(row.recognition_band)), section);
  const typeBoosted = [
    ...preferred.filter((row) => preferTypes.includes(row.candidate_type)),
    ...preferred.filter((row) => !preferTypes.includes(row.candidate_type))
  ];
  const selected = [];
  for (const row of typeBoosted) {
    if (selected.length >= target) break;
    if (!canUseCandidate(row, state, { artistCap, skipSceneRefs })) continue;
    selected.push(row);
    markCandidate(row, state);
  }
  return selected;
}

function fillCandidates(pool, state, selected, {
  section,
  target,
  artistCap = 2,
  skipSceneRefs = false
}) {
  for (const row of sortedCandidates(pool, section)) {
    if (selected.length >= target) break;
    if (!canUseCandidate(row, state, { artistCap, skipSceneRefs })) continue;
    selected.push(row);
    markCandidate(row, state);
  }
  if (selected.length >= Math.min(target, 2)) return selected;
  for (const row of sortedCandidates(pool, section)) {
    if (selected.length >= target) break;
    if (!canUseCandidate(row, state, { artistCap: 3, skipSceneRefs })) continue;
    selected.push(row);
    markCandidate(row, state);
  }
  return selected;
}

function seedSceneMentions(state, candidates, researchPack) {
  const seedText = [
    researchPack.explainer_content?.history_capsule,
    researchPack.explainer_content?.what_made_it_distinct,
    researchPack.explainer_content?.why_it_mattered
  ].map((value) => String(value || "").toLowerCase()).join(" ");
  const seenArtists = new Set();
  for (const row of candidates) {
    const artist = String(row.artist_display_name || row.title || "");
    const artistKey = artist.toLowerCase();
    if (!artistKey || seenArtists.has(artistKey) || !seedText.includes(artistKey)) continue;
    seenArtists.add(artistKey);
    for (const key of artistMentionKeys(artist)) {
      state.artistMentionCounts.set(key, (state.artistMentionCounts.get(key) || 0) + 1);
    }
  }
}

function buildSelection(candidates, researchPack) {
  const state = {
    usedRefs: new Set(),
    sceneRefs: new Set(),
    usedDisplayLabels: new Set(),
    usedObjectTitles: new Set(),
    artistMentionCounts: new Map()
  };

  const sceneAnchors = [];
  const scenePool = sortedCandidates(
    candidates.filter((row) => ["obvious", "medium"].includes(row.recognition_band)),
    "scene"
  );
  for (const row of scenePool) {
    if (sceneAnchors.length >= 4) break;
    if (!canUseCandidate(row, state, { artistCap: 1 })) continue;
    sceneAnchors.push(row);
    markCandidate(row, state, { scene: true });
  }
  if (sceneAnchors.length < 3) {
    for (const row of sortedCandidates(candidates, "scene")) {
      if (sceneAnchors.length >= 3) break;
      if (!canUseCandidate(row, state, { artistCap: 1 })) continue;
      sceneAnchors.push(row);
      markCandidate(row, state, { scene: true });
    }
  }
  seedSceneMentions(state, candidates, researchPack);

  const startHere = selectCandidates(candidates, state, {
    section: "start_here",
    target: 2,
    recognitionBands: ["obvious"],
    preferTypes: ["song", "recording", "album"],
    artistCap: 1,
    skipSceneRefs: true
  });
  fillCandidates(candidates, state, startHere, {
    section: "start_here",
    target: 2,
    artistCap: 1,
    skipSceneRefs: true
  });

  const nextLevel = selectCandidates(candidates, state, {
    section: "next_level",
    target: 3,
    recognitionBands: ["obvious", "medium"],
    preferTypes: ["song", "recording", "album", "artist_anchor"],
    artistCap: 1,
    skipSceneRefs: true
  });
  fillCandidates(candidates, state, nextLevel, {
    section: "next_level",
    target: 3,
    artistCap: 1,
    skipSceneRefs: true
  });

  const goDeep = selectCandidates(candidates, state, {
    section: "go_deep",
    target: 2,
    recognitionBands: ["deep"],
    preferTypes: ["song", "recording", "album", "artist_anchor"],
    artistCap: 1,
    skipSceneRefs: true
  });
  selectCandidates(candidates, state, {
    section: "go_deep",
    target: 3 - goDeep.length,
    recognitionBands: ["medium"],
    preferTypes: ["song", "recording", "album", "artist_anchor"],
    artistCap: 1,
    skipSceneRefs: true
  }).forEach((row) => goDeep.push(row));
  fillCandidates(candidates, state, goDeep, {
    section: "go_deep",
    target: 3,
    artistCap: 1,
    skipSceneRefs: true
  });

  return { sceneAnchors, startHere, nextLevel, goDeep, artistMentionCounts: state.artistMentionCounts };
}

function sectionIntent(section) {
  if (section === "start_here") return "additional obvious or high-access anchors after the scene description";
  if (section === "next_level") return "obvious stragglers and medium-recognition examples that widen the road";
  return "medium and deep examples that show boundary, lineage, or texture";
}

function sectionTitle(section) {
  if (section === "start_here") return "Start Here";
  if (section === "next_level") return "Next Level";
  return "Go Deep";
}

function sectionLead(section) {
  if (section === "start_here") return "Start here with";
  if (section === "next_level") return "Next level opens";
  return "Go deep with";
}

function cueForType(type) {
  if (type === "artist_anchor") return "recurring sound choices";
  if (type === "album") return "album-scale arc";
  return "recording-level arrangement";
}

function cueForRole(role) {
  switch (role) {
  case "anchor":
    return "central vocabulary";
  case "album_world":
    return "long-form worldbuilding";
  case "bridge":
    return "crossover pressure";
  case "boundary_case":
    return "edge-of-road tension";
  case "deep_cut":
    return "deep-scene texture";
  case "context":
    return "context-setting sound";
  default:
    return "historical placement";
  }
}

function listenerCuePhrase(cue) {
  const cleaned = sentence(cue).replace(/\?$/u, "");
  if (!cleaned) return "";
  if (/^Track the branch/i.test(cleaned)) {
    return "branching scene vocabulary";
  }
  if (/^Preserve the distinction/i.test(cleaned)) {
    return "";
  }
  if (/^The first 10 seconds/i.test(cleaned)) {
    return "instant scene-setting";
  }
  if (/^Teen-drama compression/i.test(cleaned)) {
    return "teen-drama compression";
  }
  if (/^Hook placement/i.test(cleaned)) {
    return "early title-hook return";
  }
  if (/^Backing-vocal architecture/i.test(cleaned)) {
    return "answer-phrase backing vocals";
  }
  if (/^Production as scale/i.test(cleaned)) {
    return "production scale";
  }
  if (/^Craft handoff/i.test(cleaned)) {
    return "performer/writer craft handoff";
  }
  if (/^What is the band subtracting from classic rock/i.test(cleaned)) {
    return "subtracted classic-rock weight";
  }
  if (/^Where does the art enter/i.test(cleaned)) {
    return "art-pressure in performance";
  }
  if (/^Is the track pop-readable/i.test(cleaned)) {
    return "pop/punk/art boundary";
  }
  if (/^Does the weirdness create/i.test(cleaned)) {
    return "weirdness as tension";
  }
  if (/^What is /i.test(cleaned)) {
    return cleaned.replace(/^What is /iu, "what ").replace(/:/u, "");
  }
  if (/^Where /i.test(cleaned)) return cleaned.charAt(0).toLowerCase() + cleaned.slice(1).replace(/:/u, "");
  if (/^How /i.test(cleaned)) return cleaned.charAt(0).toLowerCase() + cleaned.slice(1).replace(/:/u, "");
  if (/^Does /i.test(cleaned)) return cleaned.replace(/^Does /iu, "whether ").replace(/:/u, "");
  if (/^Is /i.test(cleaned)) return cleaned.replace(/^Is /iu, "whether ").replace(/:/u, "");
  return cleaned;
}

function objectNoun(row) {
  if (row.candidate_type === "artist_anchor") return "name";
  if (row.candidate_type === "album") return "release";
  return "recording";
}

function placementPhrase(row, section) {
  switch (row.mission_role) {
  case "anchor":
    return "sets a broad reference point for the profile";
  case "album_world":
    return "shows the profile at long-form scale";
  case "bridge":
    if (section === "start_here" && row.recognition_band === "medium") return "adds a second doorway into the road from a neighboring sound";
    if (section === "next_level") return "shows the road continuing into an adjacent lane";
    if (section === "go_deep") return "keeps a through-line back to the landmarks while moving outward";
    return "connects the central landmarks to a neighboring sound";
  case "boundary_case":
    if (section === "go_deep") return "tests one outer edge of the profile without leaving the road";
    return "marks one edge of the profile without leaving the road";
  case "deep_cut":
    if (section === "next_level") return "moves just outside the best-known canon while staying legible";
    return "shows how the road works outside the best-known canon";
  default:
    return "adds another historically placed reference point";
  }
}

function sectionPlacement(section) {
  if (section === "start_here") return "It is meant to make the road easy to enter after the headline landmarks.";
  if (section === "next_level") return "It widens the profile beyond the easiest landmarks.";
  return "It belongs on the outer shelf, where texture and edge matter more than instant recognition.";
}

function itemCopy(row, section, researchPack) {
  const lead = row.year
    ? `From ${row.year}, this ${objectNoun(row)} ${placementPhrase(row, section)}.`
    : `This ${objectNoun(row)} ${placementPhrase(row, section)}.`;
  return `${lead} ${sectionPlacement(section)}`;
}

function tagSignature(tags) {
  return tags.join("|").toLowerCase();
}

function rotatePick(pool, start, count) {
  const selected = [];
  for (let index = 0; index < pool.length && selected.length < count; index += 1) {
    const value = pool[(start + index) % pool.length];
    if (value && !selected.includes(value)) selected.push(value);
  }
  return selected;
}

function listeningCues(row, researchPack, section, usedCueSignatures) {
  const cues = getListenCues(researchPack);
  const offset = section === "start_here" ? 0 : section === "next_level" ? 1 : 2;
  const pool = [...new Set([
    ...cues.map(listenerCuePhrase).filter((cue) => cue.length <= 64),
    cueForType(row.candidate_type),
    cueForRole(row.mission_role)
  ].filter(Boolean))];
  const count = Math.min(3, Math.max(1, pool.length));
  for (let shift = 0; shift < Math.max(pool.length, 1); shift += 1) {
    const selected = rotatePick(pool, offset + shift, count);
    const signature = tagSignature(selected);
    if (!usedCueSignatures || !usedCueSignatures.has(signature)) {
      usedCueSignatures?.add(signature);
      return selected;
    }
  }
  const fallback = [...rotatePick(pool, offset, count), cueForRole(row.mission_role), cueForType(row.candidate_type)]
    .filter(Boolean);
  const selected = [...new Set(fallback)].slice(0, 4);
  usedCueSignatures?.add(tagSignature(selected));
  return selected;
}

function ladderItem(row, section, researchPack, usedCueSignatures) {
  return {
    example_ref: exampleRef(row),
    example_type: candidateTypeToExampleType(row.candidate_type),
    display_label: displayLabel(row),
    artist_display_name: row.artist_display_name || row.title,
    title: row.title,
    year: row.year ?? null,
    recognition_band: row.recognition_band,
    mission_role: row.mission_role,
    import_class: row.import_class,
    current_graph_candidate_identity_key: row.candidate_identity_key,
    current_graph_membership_id: row.v1_membership_id,
    legacy_display_ref: sourceGraphRef(row),
    ladder_section: section,
    current_graph_why_it_belongs: row.why_it_belongs || "",
    why_this_example_matters: itemCopy(row, section, researchPack),
    what_to_listen_for: listeningCues(row, researchPack, section, usedCueSignatures),
    graph_ref_validation_status: "validated_in_current_canonical_graph_active_inventory_v1"
  };
}

function sceneAnchorItem(row) {
  return {
    example_ref: exampleRef(row),
    example_type: candidateTypeToExampleType(row.candidate_type),
    display_label: displayLabel(row),
    artist_display_name: row.artist_display_name || row.title,
    title: row.title,
    year: row.year ?? null,
    recognition_band: row.recognition_band,
    mission_role: row.mission_role,
    current_graph_candidate_identity_key: row.candidate_identity_key,
    current_graph_membership_id: row.v1_membership_id,
    legacy_display_ref: sourceGraphRef(row),
    graph_ref_validation_status: "validated_in_current_canonical_graph_active_inventory_v1"
  };
}

function buildSceneDescription(researchPack, originalRenderPack, selection) {
  const title = researchPack.identity.editorial_display_title;
  const history = firstSentence(researchPack.explainer_content?.history_capsule)
    || firstSentence(originalRenderPack.modules.region_scene_page?.standard)
    || `${title} is a graph-backed Cartenza Atlas road`;
  const distinct = firstSentence(researchPack.explainer_content?.what_made_it_distinct)
    || firstSentence(researchPack.explainer_content?.why_it_mattered)
    || "its sound is best understood through the specific examples attached to the road";
  const anchors = selection.sceneAnchors.map(sceneLabel);
  const anchorSentence = anchors.length
    ? `${readableList(anchors)} give the scene its high-recognition landmarks.`
    : "The ladder below uses the current graph to orient the scene before opening deeper examples.";
  return {
    compact: `${history}.`,
    standard: `${history}. ${anchorSentence}`,
    deep: `${history}. ${distinct}. ${anchorSentence} From there, the examples move from quick recognition toward medium and deeper scene signals.`
  };
}

function buildExamplesBlock(selection) {
  const labels = {
    start_here: selection.startHere.map(displayLabel),
    next_level: selection.nextLevel.map(displayLabel),
    go_deep: selection.goDeep.map(displayLabel)
  };
  const compactParts = [
    labels.start_here.length ? `Start Here: ${readableList(labels.start_here)}` : null,
    labels.next_level.length ? `Next Level: ${readableList(labels.next_level.slice(0, 2))}` : null,
    labels.go_deep.length ? `Go Deep: ${readableList(labels.go_deep.slice(0, 2))}` : null
  ].filter(Boolean);
  return {
    compact: compactParts.join(". ") + ".",
    standard: [
      labels.start_here.length ? `Start Here: ${readableList(labels.start_here)}.` : null,
      labels.next_level.length ? `Next Level: ${readableList(labels.next_level)}.` : null,
      labels.go_deep.length ? `Go Deep: ${readableList(labels.go_deep)}.` : null
    ].filter(Boolean).join(" "),
    deep: [
      labels.start_here.length ? `Start Here uses quick landmarks: ${readableList(labels.start_here)}.` : null,
      labels.next_level.length ? `Next Level widens the road with ${readableList(labels.next_level)}.` : null,
      labels.go_deep.length ? `Go Deep opens boundary and lineage texture through ${readableList(labels.go_deep)}.` : null
    ].filter(Boolean).join(" ")
  };
}

function buildExampleLadder(researchPack, selection) {
  const usedCueSignatures = new Set();
  const item = (row, section) => {
    return ladderItem(row, section, researchPack, usedCueSignatures);
  };
  return {
    framework_version: "0.3",
    source_graph_artifact: "data/canonical_graph/current/canonical_graph_active_inventory.json",
    selection_policy: {
      scene_description_uses_high_recognition_examples: true,
      exact_scene_objects_reused_as_cards: false,
      artist_repeat_soft_cap_across_scene_and_cards: 2,
      artist_repeat_selection_policy: "Prefer one use per artist across scene and ladder; relax only when a road is too thin to fill Start Here, Next Level, or Go Deep.",
      start_here: sectionIntent("start_here"),
      next_level: sectionIntent("next_level"),
      go_deep: sectionIntent("go_deep")
    },
    scene_anchor_examples: selection.sceneAnchors.map(sceneAnchorItem),
    sections: {
      start_here: {
        title: sectionTitle("start_here"),
        intent: sectionIntent("start_here"),
        items: selection.startHere.map((row) => item(row, "start_here"))
      },
      next_level: {
        title: sectionTitle("next_level"),
        intent: sectionIntent("next_level"),
        items: selection.nextLevel.map((row) => item(row, "next_level"))
      },
      go_deep: {
        title: sectionTitle("go_deep"),
        intent: sectionIntent("go_deep"),
        items: selection.goDeep.map((row) => item(row, "go_deep"))
      }
    }
  };
}

function allLadderItems(ladder) {
  return [
    ...ladder.sections.start_here.items,
    ...ladder.sections.next_level.items,
    ...ladder.sections.go_deep.items
  ];
}

function updateSchema(schema, kind) {
  const next = JSON.parse(JSON.stringify(schema));
  next.$id = String(next.$id || "").replace(/v0_2_3/gu, "v0_3");
  next.title = String(next.title || "").replace(/v0\.2\.3/gu, "v0.3");
  if (next.properties?.schema_version) next.properties.schema_version = { const: VERSION };
  if (kind === "render") {
    next.required = [...new Set([...(next.required || []), "example_ladder"])];
    next.properties.example_ladder = {
      type: "object",
      required: ["framework_version", "source_graph_artifact", "selection_policy", "scene_anchor_examples", "sections"],
      properties: {
        framework_version: { const: VERSION },
        source_graph_artifact: { type: "string" },
        selection_policy: { type: "object", additionalProperties: true },
        scene_anchor_examples: {
          type: "array",
          items: { type: "object", additionalProperties: true }
        },
        sections: {
          type: "object",
          required: ["start_here", "next_level", "go_deep"],
          properties: {
            start_here: ladderSectionSchema(),
            next_level: ladderSectionSchema(),
            go_deep: ladderSectionSchema()
          },
          additionalProperties: false
        }
      },
      additionalProperties: true
    };
  }
  return next;
}

function ladderSectionSchema() {
  return {
    type: "object",
    required: ["title", "intent", "items"],
    properties: {
      title: { type: "string" },
      intent: { type: "string" },
      items: {
        type: "array",
        items: {
          type: "object",
          required: [
            "example_ref",
            "example_type",
            "display_label",
            "artist_display_name",
            "title",
            "recognition_band",
            "mission_role",
            "current_graph_candidate_identity_key",
            "ladder_section",
            "why_this_example_matters",
            "what_to_listen_for",
            "graph_ref_validation_status"
          ],
          properties: {
            example_ref: { type: "string" },
            example_type: { enum: ["artist", "album", "song_recording", "survey_candidate"] },
            display_label: { type: "string" },
            artist_display_name: { type: "string" },
            title: { type: "string" },
            recognition_band: { type: "string" },
            mission_role: { type: "string" },
            current_graph_candidate_identity_key: { type: "string" },
            ladder_section: { type: "string" },
            why_this_example_matters: { type: "string" },
            what_to_listen_for: { type: "array", minItems: 1, items: { type: "string" } },
            graph_ref_validation_status: { type: "string" }
          },
          additionalProperties: true
        }
      }
    },
    additionalProperties: true
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

function polishDidYouKnowVariants(variants) {
  return {
    compact: polishDidYouKnowCopy(variants?.compact, 1),
    standard: polishDidYouKnowCopy(variants?.standard, 2),
    deep: polishDidYouKnowCopy(variants?.deep, 3)
  };
}

function polishDidYouKnowCopy(text, maxSentences) {
  const raw = String(text || "").replace(/\s+/gu, " ").trim();
  if (!raw) return "";
  const sentences = raw
    .split(/(?<=[.!?])\s+/u)
    .map((value) => value.trim())
    .filter(Boolean);
  const chosen = (sentences.length ? sentences : [raw]).slice(0, maxSentences);
  return chosen.join("\n\n");
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

function deferFalseNearbyHooks(hooks) {
  return (hooks || []).map((hook) => {
    const hookId = String(hook.hook_id || "");
    const predicate = String(hook.predicate || "");
    if (!/false-nearby|dead_end_probe|boundary_question/iu.test(`${hookId} ${predicate}`)) return hook;
    return {
      ...hook,
      copy_variant: "",
      fallback_copy: "",
      state_field_status: hook.state_field_status || "proposed",
      deferred_in_v0_3: true,
      defer_reason: "False-nearby caution copy is intentionally deferred in v0.3 pending PM language polish."
    };
  });
}

function userFacingStrings(pack) {
  const rows = moduleStrings(pack);
  for (const [index, example] of (pack.canonical_examples || []).entries()) {
    rows.push({ module: "canonical_examples", depth: `${index}.display_label`, text: String(example.display_label || "") });
    rows.push({ module: "canonical_examples", depth: `${index}.why_this_example_matters`, text: String(example.why_this_example_matters || "") });
    for (const [cueIndex, cue] of (example.what_to_listen_for || []).entries()) {
      rows.push({ module: "canonical_examples", depth: `${index}.what_to_listen_for.${cueIndex}`, text: String(cue || "") });
    }
  }
  for (const depth of ["compact", "standard", "deep"]) {
    rows.push({ module: "example_ladder.scene_description", depth, text: String(pack.example_ladder?.scene_description?.[depth] || "") });
  }
  for (const section of ["start_here", "next_level", "go_deep"]) {
    const sectionBlock = pack.example_ladder?.sections?.[section];
    rows.push({ module: `example_ladder.${section}`, depth: "title", text: String(sectionBlock?.title || "") });
    rows.push({ module: `example_ladder.${section}`, depth: "intent", text: String(sectionBlock?.intent || "") });
    for (const [index, item] of (sectionBlock?.items || []).entries()) {
      rows.push({ module: `example_ladder.${section}`, depth: `${index}.display_label`, text: String(item.display_label || "") });
      rows.push({ module: `example_ladder.${section}`, depth: `${index}.why_this_example_matters`, text: String(item.why_this_example_matters || "") });
      for (const [cueIndex, cue] of (item.what_to_listen_for || []).entries()) {
        rows.push({ module: `example_ladder.${section}`, depth: `${index}.what_to_listen_for.${cueIndex}`, text: String(cue || "") });
      }
    }
  }
  for (const [index, hook] of (pack.personalization_hooks || []).entries()) {
    rows.push({ module: "personalization_hooks", depth: `${index}.copy_variant`, text: String(hook.copy_variant || "") });
    rows.push({ module: "personalization_hooks", depth: `${index}.fallback_copy`, text: String(hook.fallback_copy || "") });
  }
  return rows;
}

function validatePackage({ renderPacks, inventoryKeys }) {
  const failures = [];
  const repeatWarnings = [];
  const sceneReuseFailures = [];
  const displayReuseFailures = [];
  const titleReuseFailures = [];
  const emptySectionWarnings = [];
  const qaHits = [];
  const forbiddenDynamicHits = [];
  const duplicateTagFailures = [];
  const tagCopyOverlapWarnings = [];
  const exactExampleRefs = new Set();
  for (const pack of renderPacks) {
    const ladder = pack.example_ladder;
    const sceneRefs = new Set(ladder.scene_anchor_examples.map((item) => item.example_ref));
    const cardItems = allLadderItems(ladder);
    if (!cardItems.length) failures.push(`${pack.render_pack_id}: no ladder card items`);
    for (const section of ["start_here", "next_level", "go_deep"]) {
      if (!ladder.sections[section].items.length) {
        emptySectionWarnings.push(`${pack.identity.canonical_graph_ref}: ${section}`);
      }
    }
    const mentionCounts = new Map();
    const displayLabels = new Set();
    const objectTitles = new Set();
    const tagSignatures = new Set();
    for (const item of [...ladder.scene_anchor_examples, ...cardItems]) {
      for (const key of artistMentionKeys(item.artist_display_name)) {
        mentionCounts.set(key, (mentionCounts.get(key) || 0) + 1);
      }
      const display = String(item.display_label || "").toLowerCase();
      if (displayLabels.has(display)) displayReuseFailures.push(`${pack.identity.canonical_graph_ref}: ${item.display_label}`);
      displayLabels.add(display);
      if (item.example_type !== "artist") {
        const titleKey = normalizeTitleKey(item.title);
        if (objectTitles.has(titleKey)) titleReuseFailures.push(`${pack.identity.canonical_graph_ref}: ${item.title}`);
        objectTitles.add(titleKey);
      }
      if (!inventoryKeys.has(item.current_graph_candidate_identity_key)) {
        failures.push(`${pack.render_pack_id}: missing active inventory key ${item.current_graph_candidate_identity_key}`);
      }
      exactExampleRefs.add(item.example_ref);
    }
    for (const item of cardItems) {
      const tags = item.what_to_listen_for || [];
      const signature = tagSignature(tags);
      if (tagSignatures.has(signature)) {
        duplicateTagFailures.push(`${pack.identity.canonical_graph_ref}: ${item.display_label} repeats tags ${tags.join(", ")}`);
      }
      tagSignatures.add(signature);
      const body = String(item.why_this_example_matters || "").toLowerCase();
      for (const tag of tags) {
        const lowerTag = String(tag || "").toLowerCase();
        if (lowerTag.length >= 4 && body.includes(lowerTag)) {
          tagCopyOverlapWarnings.push(`${pack.identity.canonical_graph_ref}: ${item.display_label} repeats tag in body: ${tag}`);
        }
      }
    }
    for (const item of cardItems) {
      if (sceneRefs.has(item.example_ref)) {
        sceneReuseFailures.push(`${pack.identity.canonical_graph_ref}: ${item.example_ref}`);
      }
    }
    for (const [artist, count] of mentionCounts.entries()) {
      if (count > 2) repeatWarnings.push(`${pack.identity.canonical_graph_ref}: ${artist} mentioned ${count} times`);
    }
    for (const row of userFacingStrings(pack)) {
      if (!row.text) continue;
      if (INTERNAL_QA_PATTERNS.some((regex) => regex.test(row.text))) qaHits.push(`${pack.render_pack_id}:${row.module}.${row.depth}`);
      if (FORBIDDEN_DYNAMIC_MISSION_PHRASES.some((phrase) => row.text.toLowerCase().includes(phrase))) {
        forbiddenDynamicHits.push(`${pack.render_pack_id}:${row.module}.${row.depth}`);
      }
    }
  }
  return {
    failures,
    repeatWarnings,
    sceneReuseFailures,
    displayReuseFailures,
    titleReuseFailures,
    emptySectionWarnings,
    qaHits,
    forbiddenDynamicHits,
    duplicateTagFailures,
    tagCopyOverlapWarnings,
    exactExampleRefs
  };
}

function writeReports({ researchPacks, renderPacks, schemaValidation, packageValidation, profileTargets, inventoryRows }) {
  const statusCounts = renderPacks.reduce((acc, pack) => {
    acc[pack.editorial_status] = (acc[pack.editorial_status] || 0) + 1;
    return acc;
  }, {});
  const ladderCounts = renderPacks.map((pack) => ({
    ref: pack.identity.canonical_graph_ref,
    title: pack.identity.editorial_display_title,
    scene: pack.example_ladder.scene_anchor_examples.length,
    start_here: pack.example_ladder.sections.start_here.items.length,
    next_level: pack.example_ladder.sections.next_level.items.length,
    go_deep: pack.example_ladder.sections.go_deep.items.length
  }));
  const thin = ladderCounts.filter((row) => row.start_here < 1 || row.next_level < 2 || row.go_deep < 2);
  const sourceSummary = profileTargets.reduce((acc, row) => {
    if (row.high_traffic) acc.high_traffic += 1;
    return acc;
  }, { high_traffic: 0 });

  writeText(path.join(OUT_DIR, "indexes/schema_validation_report_v0_3.md"), mdReport("Schema Validation Report v0.3", [
    "Schemas were versioned to require `schema_version: \"0.3\"`.",
    "The render schema now requires `example_ladder` while retaining the v0.2.3 render module structure.",
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

  writeText(path.join(OUT_DIR, "indexes/example_ladder_framework_report_v0_3.md"), mdReport("Example Ladder Framework Report v0.3", [
    "v0.3 replaces the flat canonical example copy with a structured scene-plus-ladder framework.",
    "",
    "Framework:",
    "- Scene description: history plus high-recognition graph landmarks.",
    "- Start Here: additional obvious or high-access anchors.",
    "- Next Level: obvious stragglers and strong medium examples.",
    "- Go Deep: medium and deep examples for boundary, lineage, and texture.",
    "",
    `Render packs processed: ${renderPacks.length}`,
    `Research packs preserved/versioned: ${researchPacks.length}`,
    `Current active graph inventory rows used as source pool: ${inventoryRows.length}`,
    `High-traffic archetypes in profile targets: ${sourceSummary.high_traffic}`,
    `Exact selected example refs across all ladders/scenes: ${packageValidation.exactExampleRefs.size}`,
    "",
    "CBGB 054 check:",
    ...renderPacks.filter((pack) => pack.identity.archetype_id === "054").flatMap((pack) => [
      `- Scene anchors: ${readableList(pack.example_ladder.scene_anchor_examples.map((item) => item.display_label))}`,
      `- Start Here: ${readableList(pack.example_ladder.sections.start_here.items.map((item) => item.display_label))}`,
      `- Next Level: ${readableList(pack.example_ladder.sections.next_level.items.map((item) => item.display_label))}`,
      `- Go Deep: ${readableList(pack.example_ladder.sections.go_deep.items.map((item) => item.display_label))}`
    ])
  ]));

  writeText(path.join(OUT_DIR, "indexes/current_graph_example_selection_report_v0_3.md"), mdReport("Current Graph Example Selection Report v0.3", [
    "All v0.3 ladder selections are drawn from `data/canonical_graph/current/canonical_graph_active_inventory.json`.",
    "The older v0.2.3 canonical example arrays are not used as the selection source.",
    "",
    `Graph-key validation failures: ${packageValidation.failures.length}`,
    `Scene object reused as card failures: ${packageValidation.sceneReuseFailures.length}`,
    `Display-label duplicate failures: ${packageValidation.displayReuseFailures.length}`,
    `Object-title duplicate failures: ${packageValidation.titleReuseFailures.length}`,
    `Artist repeat warnings over soft cap: ${packageValidation.repeatWarnings.length}`,
    `Duplicate example-card tag-set failures: ${packageValidation.duplicateTagFailures.length}`,
    `Tag/body exact-overlap warnings: ${packageValidation.tagCopyOverlapWarnings.length}`,
    `Thin ladder section warnings: ${packageValidation.emptySectionWarnings.length}`,
    "",
    ...(packageValidation.failures.length ? packageValidation.failures.map((item) => `- failure: ${item}`) : ["No selected example is missing from the active inventory."]),
    "",
    ...(packageValidation.sceneReuseFailures.length ? packageValidation.sceneReuseFailures.map((item) => `- scene/card duplicate: ${item}`) : ["No exact scene anchor object is reused as a ladder card."]),
    "",
    ...(packageValidation.displayReuseFailures.length ? packageValidation.displayReuseFailures.map((item) => `- display duplicate: ${item}`) : ["No scene/card ladder display labels are repeated within a profile."]),
    "",
    ...(packageValidation.titleReuseFailures.length ? packageValidation.titleReuseFailures.map((item) => `- title duplicate: ${item}`) : ["No scene/card ladder object titles are repeated within a profile."]),
    "",
    ...(packageValidation.repeatWarnings.length ? packageValidation.repeatWarnings.slice(0, 80).map((item) => `- repeat warning: ${item}`) : ["No profile exceeds the artist repeat soft cap across scene anchors and ladder cards."]),
    "",
    ...(packageValidation.duplicateTagFailures.length ? packageValidation.duplicateTagFailures.map((item) => `- duplicate tag set: ${item}`) : ["No two ladder cards in a profile share the exact same tag set."]),
    "",
    ...(packageValidation.tagCopyOverlapWarnings.length ? packageValidation.tagCopyOverlapWarnings.slice(0, 80).map((item) => `- tag/body overlap warning: ${item}`) : ["No exact tag strings are repeated inside the example-card body copy."]),
    "",
    ...(thin.length ? thin.map((row) => `- thin ladder: ${row.ref} ${row.title} scene=${row.scene} start=${row.start_here} next=${row.next_level} deep=${row.go_deep}`) : ["No thin ladder warnings."])
  ]));

  writeText(path.join(OUT_DIR, "indexes/render_copy_policy_report_v0_3.md"), mdReport("Render Copy Policy Report v0.3", [
    "User-facing render copy remains deterministic and sidecar-backed.",
    "False-nearby caution modules are deferred in v0.3 render copy by setting compact/standard/deep to empty strings.",
    "False-nearby personalization hook copy/fallback strings are also blanked; research/audit metadata is preserved for future state-tied use.",
    "",
    `Internal QA/source-instruction hits: ${packageValidation.qaHits.length}`,
    `Forbidden dynamic mission language hits: ${packageValidation.forbiddenDynamicHits.length}`,
    "",
    ...(packageValidation.qaHits.length ? packageValidation.qaHits.map((item) => `- QA hit: ${item}`) : ["No internal QA/source-instruction language was found in user-facing modules."]),
    "",
    ...(packageValidation.forbiddenDynamicHits.length ? packageValidation.forbiddenDynamicHits.map((item) => `- dynamic mission hit: ${item}`) : ["No forbidden dynamic mission-generation language was found."])
  ]));

  writeText(path.join(OUT_DIR, "indexes/alpha_render_readiness_report_v0_3.md"), mdReport("Alpha Render Readiness Report v0.3", [
    "Cartenza Atlas Explainer Pack v0.3 is a profile-ladder hardening pass over v0.2.3.",
    "",
    `Research-pack coverage: ${researchPacks.length} / 120`,
    `Render-pack coverage: ${renderPacks.length} / 120`,
    `Schema validation failures: ${(schemaValidation.research.status === "pass" ? 0 : 1) + (schemaValidation.render.status === "pass" ? 0 : 1)}`,
    `Current graph example validation failures: ${packageValidation.failures.length}`,
    `Scene/card exact duplicate failures: ${packageValidation.sceneReuseFailures.length}`,
    `Display-label duplicate failures: ${packageValidation.displayReuseFailures.length}`,
    `Object-title duplicate failures: ${packageValidation.titleReuseFailures.length}`,
    `Artist repeat soft-cap warnings: ${packageValidation.repeatWarnings.length}`,
    `Duplicate example-card tag-set failures: ${packageValidation.duplicateTagFailures.length}`,
    `Tag/body exact-overlap warnings: ${packageValidation.tagCopyOverlapWarnings.length}`,
    `Thin ladder warnings: ${packageValidation.emptySectionWarnings.length}`,
    `Internal QA/source-instruction hits: ${packageValidation.qaHits.length}`,
    `Forbidden dynamic mission language hits: ${packageValidation.forbiddenDynamicHits.length}`,
    `Render statuses: ${JSON.stringify(statusCounts)}`,
    "",
    "No pack is marked `alpha_render_candidate` or `production_copy_candidate`.",
    "PM approval remains required before Alpha render promotion."
  ]));

  writeJson(path.join(OUT_DIR, "indexes/atlas_explainer_pack_manifest_v0_3.json"), {
    generated_at: GENERATED_AT,
    package_id: PACKAGE_ID,
    schema_version: VERSION,
    source_package: "AtlasExplainerPack_v0_2_3_RenderHardened",
    current_graph_source: "data/canonical_graph/current/canonical_graph_active_inventory.json",
    research_pack_count: researchPacks.length,
    render_pack_count: renderPacks.length,
    research_packs: researchPacks.map((pack) => `research_packs/${pack.pack_id}.json`),
    render_packs: renderPacks.map((pack) => `render_packs/${pack.render_pack_id}.json`),
    reports: [
      "indexes/schema_validation_report_v0_3.md",
      "indexes/example_ladder_framework_report_v0_3.md",
      "indexes/current_graph_example_selection_report_v0_3.md",
      "indexes/render_copy_policy_report_v0_3.md",
      "indexes/alpha_render_readiness_report_v0_3.md"
    ]
  });
}

function loadCompatibilityRefsByArchetype() {
  const refsByArchetype = new Map();
  if (fs.existsSync(APP_RESOURCE_PATH)) {
    const bundle = readJson(APP_RESOURCE_PATH);
    for (const pack of bundle.packs || []) {
      refsByArchetype.set(pack.identity.archetype_id, pack.graph_alignment?.canonical_example_refs || []);
    }
    return refsByArchetype;
  }

  for (const file of listJsonFiles(path.join(SOURCE_DIR, "render_packs"))) {
    const pack = readJson(file);
    refsByArchetype.set(pack.identity.archetype_id, pack.graph_alignment?.canonical_example_refs || []);
  }
  return refsByArchetype;
}

function writeAppResource(renderPacks, compatibilityRefsByArchetype) {
  const bundledPacks = renderPacks.map((pack) => {
    const next = JSON.parse(JSON.stringify(pack));
    const compatibilityRefs = compatibilityRefsByArchetype.get(pack.identity.archetype_id) || [];
    next.graph_alignment.canonical_example_refs = [
      ...new Set([
        ...next.graph_alignment.canonical_example_refs,
        ...compatibilityRefs
      ])
    ];
    return next;
  });
  writeJson(APP_RESOURCE_PATH, {
    artifact: "atlas_explainer_render_pack_bundle",
    schema_version: VERSION,
    source_package: PACKAGE_ID,
    generated_from: "data/atlas_explainer/AtlasExplainerPack_v0_3_ProfileLadders/render_packs",
    generated_at: GENERATED_AT,
    pack_count: bundledPacks.length,
    packs: bundledPacks,
    compatibility_graph_refs_source: "MusicAtlasController/Resources/atlas_explainer_render_packs_v0_2_3.json"
  });
}

function main() {
  fs.rmSync(OUT_DIR, { recursive: true, force: true });
  fs.mkdirSync(path.join(OUT_DIR, "research_packs"), { recursive: true });
  fs.mkdirSync(path.join(OUT_DIR, "render_packs"), { recursive: true });
  fs.mkdirSync(path.join(OUT_DIR, "schemas"), { recursive: true });
  fs.mkdirSync(path.join(OUT_DIR, "indexes"), { recursive: true });

  const inventory = readJson(ACTIVE_INVENTORY_PATH);
  const compatibilityRefsByArchetype = loadCompatibilityRefsByArchetype();
  const profileTargets = readJson(PROFILE_TARGETS_PATH).rows;
  const inventoryRows = inventory.rows.filter((row) => row.active_in_v1 && ["artist_anchor", "album", "song", "recording"].includes(row.candidate_type));
  const inventoryKeys = new Set(inventoryRows.map((row) => row.candidate_identity_key));
  const rowsByArchetype = new Map();
  for (const row of inventoryRows) {
    const key = String(row.archetype_id).padStart(3, "0");
    const rows = rowsByArchetype.get(key) || [];
    rows.push(row);
    rowsByArchetype.set(key, rows);
  }

  const sourceResearchFiles = listJsonFiles(path.join(SOURCE_DIR, "research_packs"));
  const sourceRenderFiles = listJsonFiles(path.join(SOURCE_DIR, "render_packs"));
  const researchById = new Map();
  const renderById = new Map();
  for (const file of sourceResearchFiles) {
    const pack = readJson(file);
    researchById.set(pack.identity.archetype_id, { file, pack });
  }
  for (const file of sourceRenderFiles) {
    const pack = readJson(file);
    renderById.set(pack.identity.archetype_id, { file, pack });
  }

  for (const schemaFile of listJsonFiles(path.join(SOURCE_DIR, "schemas"))) {
    const kind = path.basename(schemaFile).includes("render") ? "render" : "research";
    const schema = updateSchema(readJson(schemaFile), kind);
    writeJson(path.join(OUT_DIR, "schemas", versionedFileName(path.basename(schemaFile))), schema);
  }

  const researchPacks = [];
  const renderPacks = [];
  const archetypeIds = [...renderById.keys()].sort();
  for (const archetypeId of archetypeIds) {
    const researchPack = JSON.parse(JSON.stringify(researchById.get(archetypeId).pack));
    const renderPack = JSON.parse(JSON.stringify(renderById.get(archetypeId).pack));
    const candidates = rowsByArchetype.get(archetypeId) || [];
    const selection = buildSelection(candidates, researchPack);
    const sceneDescription = buildSceneDescription(researchPack, renderPack, selection);
    const exampleLadder = buildExampleLadder(researchPack, selection);
    const ladderItems = allLadderItems(exampleLadder);
    const examplesBlock = buildExamplesBlock(selection);

    researchPack.schema_version = VERSION;
    researchPack.pack_id = versionedId(researchPack.pack_id);
    researchPack.generated_at = GENERATED_AT;
    researchPack.current_graph_profile_ladder_trace = {
      source_graph_artifact: "data/canonical_graph/current/canonical_graph_active_inventory.json",
      active_inventory_candidates_for_archetype: candidates.length,
      scene_anchor_refs: selection.sceneAnchors.map(exampleRef),
      ladder_example_refs: ladderItems.map((item) => item.example_ref),
      non_mutation_assertion: "v0.3 profile ladders select render examples from current graph rows only; they do not mutate canonical graph identity, membership, refs, or recognition bands."
    };

    renderPack.schema_version = VERSION;
    renderPack.render_pack_id = versionedId(renderPack.render_pack_id);
    renderPack.generated_at = GENERATED_AT;
    renderPack.source_research_pack_id = researchPack.pack_id;
    renderPack.modules = {
      ...renderPack.modules,
      region_scene_page: sceneDescription,
      did_you_know_card: polishDidYouKnowVariants(renderPack.modules.did_you_know_card),
      canonical_examples_block: examplesBlock,
      dead_end_false_nearby_caution_module: {
        compact: "",
        standard: "",
        deep: ""
      }
    };
    renderPack.example_ladder = {
      ...exampleLadder,
      scene_description: sceneDescription
    };
    renderPack.canonical_examples = ladderItems;
    renderPack.personalization_hooks = deferFalseNearbyHooks(renderPack.personalization_hooks);
    renderPack.graph_alignment = {
      ...renderPack.graph_alignment,
      canonical_example_refs: ladderItems.map((item) => item.example_ref),
      current_graph_candidate_identity_keys: candidates.map((row) => row.candidate_identity_key),
      current_graph_candidate_counts: candidates.reduce((acc, row) => {
        acc[row.candidate_type] = (acc[row.candidate_type] || 0) + 1;
        return acc;
      }, {}),
      current_graph_recognition_counts: candidates.reduce((acc, row) => {
        acc[row.recognition_band] = (acc[row.recognition_band] || 0) + 1;
        return acc;
      }, {})
    };
    if (["alpha_render_candidate", "production_copy_candidate"].includes(renderPack.editorial_status)) {
      renderPack.editorial_status = "visualization_candidate";
    }

    researchPacks.push(researchPack);
    renderPacks.push(renderPack);
    writeJson(path.join(OUT_DIR, "research_packs", `${researchPack.pack_id}.json`), researchPack);
    writeJson(path.join(OUT_DIR, "render_packs", `${renderPack.render_pack_id}.json`), renderPack);
  }

  const schemaValidation = {
    research: runAjv(
      path.join(OUT_DIR, "schemas/atlas_explainer_research_pack_schema_v0_3.json"),
      path.join(OUT_DIR, "research_packs/*.json")
    ),
    render: runAjv(
      path.join(OUT_DIR, "schemas/atlas_explainer_render_pack_schema_v0_3.json"),
      path.join(OUT_DIR, "render_packs/*.json")
    )
  };
  const packageValidation = validatePackage({ renderPacks, inventoryKeys });
  writeReports({ researchPacks, renderPacks, schemaValidation, packageValidation, profileTargets, inventoryRows });
  writeAppResource(renderPacks, compatibilityRefsByArchetype);

  if (fs.existsSync(ZIP_PATH)) fs.rmSync(ZIP_PATH, { force: true });
  execFileSync("zip", ["-qr", ZIP_PATH, path.relative(ROOT, OUT_DIR)], { cwd: ROOT });
  console.log(JSON.stringify({
    package_id: PACKAGE_ID,
    out_dir: OUT_DIR,
    zip_path: ZIP_PATH,
    research_packs: researchPacks.length,
    render_packs: renderPacks.length,
    schema_validation: {
      research: schemaValidation.research.status,
      render: schemaValidation.render.status
    },
    graph_validation_failures: packageValidation.failures.length,
    scene_card_duplicate_failures: packageValidation.sceneReuseFailures.length,
    display_duplicate_failures: packageValidation.displayReuseFailures.length,
    title_duplicate_failures: packageValidation.titleReuseFailures.length,
    artist_repeat_warnings: packageValidation.repeatWarnings.length,
    thin_ladder_warnings: packageValidation.emptySectionWarnings.length,
    duplicate_tag_failures: packageValidation.duplicateTagFailures.length,
    tag_copy_overlap_warnings: packageValidation.tagCopyOverlapWarnings.length,
    qa_hits: packageValidation.qaHits.length,
    forbidden_dynamic_hits: packageValidation.forbiddenDynamicHits.length,
    app_resource_path: APP_RESOURCE_PATH
  }, null, 2));
}

main();
