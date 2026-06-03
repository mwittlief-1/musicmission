#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

const repoRoot = process.cwd();
const packetRoot = path.join(repoRoot, "review_packets/affinity_graphwide_v0_1");
const currentRoot = path.join(repoRoot, "data/canonical_graph/current");
const affinityPath = path.join(packetRoot, "affinity_song_tags_graphwide_v0_1.json");
const patchPath = path.join(currentRoot, "affinity_family10_missing_obvious_hotfix_v1.json");
const runVersion = "affinity_family10_missing_obvious_hotfix_v1";
const generatedAt = "2026-06-01";

const songs = [
  song({
    id: "song|radiohead|creep",
    title: "Creep",
    artist: "Radiohead",
    year: 1992,
    membershipId: "v1m_11703",
    archetypeId: "071",
    archetypeName: "Post-Grunge / Modern Rock Radio",
    roles: ["bridge"],
    recognition: "obvious",
    tags: {
      vocal_performance: primary("ragged_voice"),
      emotion_theme: primary("alienation"),
      sonic_texture: primary("distorted_guitar"),
      rhythm_body: primary("explosive_chorus"),
      form_container: primary("anthem"),
    },
    social: { primary: ["karaoke_context"], secondary: ["nostalgia_context"] },
    caution: { primary: ["safe_gateway"], secondary: ["overfamiliar_anchor"] },
    evidence: [
      "Uses quiet/loud guitar contrast and a distorted chorus lift rather than smooth pop-rock polish.",
      "Lyric and vocal stance center outsider alienation and self-loathing rather than romantic resolution.",
      "Mass familiarity makes it useful as a Radiohead gateway but noisy as broad Radiohead affinity evidence.",
    ],
    overlayNotes: "Use as a high-recognition Radiohead gateway, but do not infer broad Radiohead or art-rock appetite from Creep alone; same-title TLC collision remains a distinct recording identity.",
    taggingNotes: "Post-freeze Family 10 hotfix tag assignment; keep context saturation in overlay rather than core tags.",
  }),
  song({
    id: "song|radiohead|fake plastic trees",
    title: "Fake Plastic Trees",
    artist: "Radiohead",
    year: 1995,
    membershipId: "v1m_11704",
    archetypeId: "071",
    archetypeName: "Post-Grunge / Modern Rock Radio",
    roles: ["bridge"],
    recognition: "obvious",
    tags: {
      vocal_performance: primary("intimate_voice"),
      emotion_theme: primary("alienation"),
      sonic_texture: primary("acoustic_intimate", ["guitar_forward"]),
      rhythm_body: primary("slow_burn"),
      form_container: primary("narrative_song"),
    },
    social: emptyBucket(),
    caution: { primary: ["safe_gateway"], secondary: ["requires_framing"] },
    evidence: [
      "Begins from exposed acoustic guitar and intimate vocal pressure before widening into a band build.",
      "The song's affect is alienated and fragile rather than rebellious or celebratory.",
      "It tests Radiohead songcraft and dynamic patience more than Kid A-style electronic abstraction.",
    ],
    overlayNotes: "Use as a bridge from modern-rock Radiohead into more delicate songcraft routes; frame separately from electronic or art-rock Radiohead probes.",
  }),
  song({
    id: "song|radiohead|paranoid android",
    title: "Paranoid Android",
    artist: "Radiohead",
    year: 1997,
    membershipId: "v1m_11705",
    archetypeId: "078",
    archetypeName: "Blog Indie / Prestige Indie / 2000s Indie Rock",
    roles: ["boundary_case"],
    recognition: "obvious",
    tags: {
      vocal_performance: primary("detached_cool"),
      emotion_theme: primary("alienation", ["dread"]),
      sonic_texture: primary("studio_architecture", ["distorted_guitar"]),
      rhythm_body: primary("anthemic_build"),
      form_container: primary("concept_piece"),
    },
    social: emptyBucket(),
    caution: { primary: ["requires_framing"], secondary: ["high_whiplash"] },
    evidence: [
      "Sectional structure moves through contrasting parts rather than a standard verse/chorus single container.",
      "The recording combines studio architecture, guitar abrasion, and shifting dynamics.",
      "Affinity signal should test tolerance for long-form art-rock construction, not generic 1990s alternative radio.",
    ],
    overlayNotes: "Use as a boundary-case route item when testing long-form Radiohead architecture; sequence with framing because abrupt sectional changes can create whiplash.",
  }),
  song({
    id: "song|radiohead|karma police",
    title: "Karma Police",
    artist: "Radiohead",
    year: 1997,
    membershipId: "v1m_11706",
    archetypeId: "078",
    archetypeName: "Blog Indie / Prestige Indie / 2000s Indie Rock",
    roles: ["bridge"],
    recognition: "obvious",
    tags: {
      vocal_performance: primary("detached_cool"),
      emotion_theme: primary("alienation"),
      sonic_texture: primary("piano_led", ["studio_architecture"]),
      rhythm_body: primary("slow_burn"),
      form_container: primary("anthem"),
    },
    social: { primary: [], secondary: ["nostalgia_context"] },
    caution: { primary: ["safe_gateway"], secondary: ["overfamiliar_anchor"] },
    evidence: [
      "Piano-led arrangement and gradual studio build distinguish it from straight guitar-rock.",
      "Detached delivery and social unease point toward alienation rather than open catharsis.",
      "Recognition is high, so it works best as a bridge into OK Computer context rather than a terminal taste verdict.",
    ],
    overlayNotes: "Use as a recognizable OK Computer bridge; avoid making it the only evidence for the listener's response to Radiohead album-world material.",
  }),
  song({
    id: "song|radiohead|no surprises",
    title: "No Surprises",
    artist: "Radiohead",
    year: 1997,
    membershipId: "v1m_11707",
    archetypeId: "078",
    archetypeName: "Blog Indie / Prestige Indie / 2000s Indie Rock",
    roles: ["bridge"],
    recognition: "obvious",
    tags: {
      vocal_performance: primary("intimate_voice"),
      emotion_theme: primary("dread"),
      sonic_texture: primary("polished_studio"),
      rhythm_body: primary("ballad_pacing"),
      form_container: primary("single_craft"),
    },
    social: { primary: [], secondary: ["nostalgia_context"] },
    caution: { primary: ["safe_gateway"], secondary: ["overfamiliar_anchor"] },
    evidence: [
      "Gentle, polished surface contrasts with bleak emotional content.",
      "Ballad pacing and compact single craft make it a softer OK Computer entry point.",
      "The core signal is quiet dread and resignation, not upbeat nostalgia.",
    ],
    overlayNotes: "Use as a low-abrasion Radiohead bridge; keep nostalgia and familiarity separate from the darker intrinsic affect.",
  }),
  song({
    id: "song|radiohead|everything in its right place",
    title: "Everything in Its Right Place",
    artist: "Radiohead",
    year: 2000,
    membershipId: "v1m_11708",
    archetypeId: "078",
    archetypeName: "Blog Indie / Prestige Indie / 2000s Indie Rock",
    roles: ["boundary_case"],
    recognition: "obvious",
    tags: {
      vocal_performance: primary("processed_vocal"),
      emotion_theme: primary("alienation"),
      sonic_texture: primary("synthetic_texture", ["dark_atmosphere"]),
      rhythm_body: primary("minimal_pulse"),
      form_container: primary("concept_piece"),
    },
    social: emptyBucket(),
    caution: { primary: ["requires_framing"], secondary: ["context_dependent"] },
    evidence: [
      "Processed vocal fragments and synthetic keyboard texture are central to the recording identity.",
      "Minimal pulse and atmosphere test tolerance for abstraction rather than guitar-rock drive.",
      "Positive response should branch toward electronic/art-rock boundary checks before ordinary alt-rock recommendations.",
    ],
    overlayNotes: "Use as a Kid A boundary probe; frame the electronic and processed-vocal shift so it is not mistaken for standard modern-rock affinity.",
  }),
  song({
    id: "song|radiohead|idioteque",
    title: "Idioteque",
    artist: "Radiohead",
    year: 2000,
    membershipId: "v1m_11709",
    archetypeId: "078",
    archetypeName: "Blog Indie / Prestige Indie / 2000s Indie Rock",
    roles: ["boundary_case"],
    recognition: "obvious",
    tags: {
      vocal_performance: primary("processed_vocal"),
      emotion_theme: primary("dread"),
      sonic_texture: primary("synthetic_texture"),
      rhythm_body: primary("minimal_pulse", ["dancefloor"]),
      form_container: primary("club_track"),
    },
    social: emptyBucket(),
    caution: { primary: ["requires_framing"], secondary: ["high_whiplash", "context_dependent"] },
    evidence: [
      "Beat-driven electronic construction puts the track closer to a tense club form than guitar-rock single craft.",
      "Vocal processing, synthetic texture, and apocalyptic affect are core to the listener signal.",
      "It is a boundary probe for electronic/post-rock tolerance inside a Radiohead route.",
    ],
    overlayNotes: "Use as a high-whiplash boundary probe; do not route from this directly into generic electronic affinity without additional listener evidence.",
  }),
  song({
    id: "song|radiohead|weird fishes arpeggi",
    title: "Weird Fishes/Arpeggi",
    artist: "Radiohead",
    year: 2007,
    membershipId: "v1m_11710",
    archetypeId: "078",
    archetypeName: "Blog Indie / Prestige Indie / 2000s Indie Rock",
    roles: ["deep_cut"],
    recognition: "obvious",
    tags: {
      vocal_performance: primary("intimate_voice"),
      emotion_theme: primary("spiritual_yearning"),
      sonic_texture: primary("guitar_forward"),
      rhythm_body: primary("driving_eighths"),
      form_container: primary("album_world"),
    },
    social: emptyBucket(),
    caution: { primary: ["requires_framing"], secondary: [] },
    evidence: [
      "Interlocking guitar motion and patient drive define the song's feel more than a single chorus payoff.",
      "The affect is yearning and submerged rather than blunt alienation or rebellion.",
      "Best treated as an album-world Radiohead signal rather than a mass-radio control.",
    ],
    overlayNotes: "Use as a deeper In Rainbows/album-world check after the listener has shown tolerance for Radiohead pacing and atmosphere.",
  }),
  song({
    id: "song|oasis|wonderwall",
    title: "Wonderwall",
    artist: "Oasis",
    year: 1995,
    membershipId: "v1m_11713",
    archetypeId: "075",
    archetypeName: "Power-Pop Revival / Crunchy Alt-Pop",
    roles: ["bridge"],
    recognition: "obvious",
    tags: {
      vocal_performance: primary("plainspoken_voice"),
      emotion_theme: primary("romantic_longing"),
      sonic_texture: primary("acoustic_intimate"),
      rhythm_body: primary("anthemic_build"),
      form_container: primary("anthem"),
    },
    social: { primary: ["karaoke_context"], secondary: ["nostalgia_context"] },
    caution: { primary: ["overfamiliar_anchor"], secondary: ["safe_gateway", "context_dependent"] },
    evidence: [
      "Acoustic strum, plainspoken vocal stance, and broad chorus shape make the track an anthem rather than a deep Britpop diagnostic by itself.",
      "Romantic longing is explicit in the song's function, but singalong context can dominate reactions.",
      "Use as a noisy gateway because familiarity can outscore true Oasis or Britpop affinity.",
    ],
    overlayNotes: "Use as a noisy Oasis/Britpop gateway; context and ubiquity should not be treated as broad artist or scene affinity without follow-up.",
  }),
  song({
    id: "song|oasis|champagne supernova",
    title: "Champagne Supernova",
    artist: "Oasis",
    year: 1995,
    membershipId: "v1m_11714",
    archetypeId: "075",
    archetypeName: "Power-Pop Revival / Crunchy Alt-Pop",
    roles: ["bridge"],
    recognition: "obvious",
    tags: {
      vocal_performance: primary("plainspoken_voice"),
      emotion_theme: primary("nostalgia"),
      sonic_texture: primary("guitar_forward"),
      rhythm_body: primary("slow_burn"),
      form_container: primary("anthem"),
    },
    social: { primary: [], secondary: ["nostalgia_context"] },
    caution: { primary: ["safe_gateway"], secondary: ["overfamiliar_anchor"] },
    evidence: [
      "Longer slow-burn build and guitar-forward atmosphere make it a better Oasis-depth check than a simple singalong control.",
      "The affect leans nostalgic and expansive rather than narrowly romantic.",
      "It remains high-recognition, so route interpretation should still separate familiarity from Britpop affinity.",
    ],
    overlayNotes: "Use as a stronger Oasis-depth bridge than Wonderwall, while preserving caution around nostalgia and overfamiliarity.",
  }),
];

const affinity = readJson(affinityPath);
const byId = new Map(affinity.songs.map((entry, index) => [entry.canonical_song_recording_id, index]));
let added = 0;
let replaced = 0;
for (const entry of songs) {
  const index = byId.get(entry.canonical_song_recording_id);
  if (index === undefined) {
    affinity.songs.push(entry);
    added += 1;
  } else {
    affinity.songs[index] = entry;
    replaced += 1;
  }
}

affinity.metadata = {
  ...affinity.metadata,
  completed_song_count: affinity.songs.length,
  total_song_count: affinity.songs.length,
  completed_batch_count: Math.ceil(affinity.songs.length / 25),
  post_freeze_hotfixes: [
    ...(affinity.metadata.post_freeze_hotfixes ?? []).filter((entry) => entry.run_version !== runVersion),
    {
      run_version: runVersion,
      generated_at: generatedAt,
      songs_added: added,
      songs_replaced: replaced,
      target_song_ids: songs.map((entry) => entry.canonical_song_recording_id),
      policy: "Approved post-freeze Radiohead/Oasis canonical graph songs receive v0.3.1 canonical affinity tags without runtime listener inference.",
    },
  ],
};

writeJson(affinityPath, affinity);
writeJson(patchPath, {
  artifact_name: runVersion,
  generated_at: generatedAt,
  status: "applied",
  ontology_version: affinity.metadata.ontology_version,
  schema_version: affinity.metadata.schema_version,
  songs,
});

console.log(JSON.stringify({
  status: "complete",
  songs_added: added,
  songs_replaced: replaced,
  total_song_count: affinity.songs.length,
  patch_file: path.relative(repoRoot, patchPath),
}, null, 2));

function song(config) {
  return {
    canonical_song_recording_id: config.id,
    song_title: config.title,
    artist_names: [config.artist],
    release_years: [config.year],
    research_evidence: config.evidence.map((source) => ({
      source_type: "general_music_knowledge",
      source,
      supports: "affinity_tag_assignment",
    })),
    canonical_song_affinity_tags: config.tags,
    membership_context_overlays: [
      {
        membership_id: config.membershipId,
        social_context: config.social,
        routing_caution: config.caution,
        overlay_notes: config.overlayNotes,
        song_archetype_membership_id: config.membershipId,
        family_id: "family_10",
        family_number: 10,
        family_scope: "Alternative, Indie, Grunge, Emo",
        archetype_id: config.archetypeId,
        archetype_name: config.archetypeName,
        membership_roles: config.roles,
        recognition_tier: config.recognition,
        survey_tier: "",
      },
    ],
    review: {
      identity_review_needed: false,
      core_tag_review_needed: false,
      overlay_review_needed: false,
      review_reason_codes: [],
      review_reason: "",
      duplicate_context_review_needed: false,
      context_leak_review_needed: false,
    },
    tagging_notes: config.taggingNotes ?? "Post-freeze Family 10 hotfix tag assignment from approved canonical graph rows.",
    source_confidence: "high",
    canonical_composition_id: "",
    duplicate_context_review: {
      needed: false,
      reason_codes: [],
      candidate_types: [],
      candidate_group_ids: [],
      risk: [],
      recommended_actions: [],
      notes: "",
    },
  };
}

function primary(tag, secondary = []) {
  return { primary: [tag], secondary };
}

function emptyBucket() {
  return { primary: [], secondary: [] };
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function writeJson(file, value) {
  fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`);
}
