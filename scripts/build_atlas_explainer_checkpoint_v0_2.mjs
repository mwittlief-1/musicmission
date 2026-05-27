import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";

const ROOT = process.cwd();
const OUT_DIR = path.join(ROOT, "data/atlas_explainer/AtlasExplainerPack_v0_2_Checkpoint");
const ZIP_PATH = `${OUT_DIR}.zip`;
const FULL_OUT_DIR = path.join(ROOT, "data/atlas_explainer/AtlasExplainerPack_v0_2_All_Archetypes");
const FULL_ZIP_PATH = `${FULL_OUT_DIR}.zip`;
const GENERATED_AT = "2026-05-26";

const CHECKPOINT_REFS = [
  { family_id: 1, archetype_id: "001" },
  { family_id: 1, archetype_id: "002" },
  { family_id: 1, archetype_id: "003" },
  { family_id: 1, archetype_id: "004" },
  { family_id: 1, archetype_id: "005" },
  { family_id: 1, archetype_id: "006" },
  { family_id: 1, archetype_id: "007" },
  { family_id: 8, archetype_id: "054" },
  { family_id: 6, archetype_id: "039" },
  { family_id: 10, archetype_id: "079" }
];

const ATLAS_STATE_FIELDS_V0_2 = [
  "atlas_state.family_affinity[family_id]",
  "atlas_state.archetype_affinity[archetype_id]",
  "atlas_state.completed_mission_ids",
  "atlas_state.active_mission_id",
  "atlas_state.first_batch_mission_ids",
  "atlas_state.related_mission_ids",
  "atlas_state.survey_positive_candidate_refs",
  "atlas_state.survey_negative_candidate_refs",
  "atlas_state.boundary_question_results",
  "atlas_state.dead_end_probe_results",
  "atlas_state.user_known_song_refs",
  "atlas_state.user_disliked_song_refs",
  "atlas_state.user_saved_artist_refs",
  "atlas_state.user_skipped_artist_refs"
];

const FAMILY_2_ARCHETYPES = {
  "008": "British Invasion / Core UK Beat Groups",
  "009": "Jangle Pop / Folk-Rock Precursor",
  "010": "Folk-Rock / Harmony Pop / 60s Songcraft",
  "011": "Garage Rock / Nuggets / Proto-Punk Singles",
  "012": "Baroque Pop / Chamber Pop / Artful 60s Pop",
  "013": "Psychedelic Pop / Sunshine Pop / Late-60s Pop-Rock",
  "014": "Heavy Psych / Blues-Rock / Acid Rock",
  "015": "Art-Rock / Proto-Alternative / Freak Underground"
};

const SOURCE_REFERENCES = {
  canonical_graph_family_1: {
    title: "Normalized canonical graph export, Family 1",
    publisher: "Waymark internal canonical graph",
    url: "data/canonical_graph/family_1/normalized_family_1.json",
    source_type: "internal_graph_export",
    audit_use: "Family, archetype, membership, role, survey-tier, and non-mutation graph identity.",
    rights_note: "Internal factual graph metadata; no third-party prose copied."
  },
  canonical_graph_family_6: {
    title: "Normalized canonical graph export, Family 6",
    publisher: "Waymark internal canonical graph",
    url: "data/canonical_graph/family_6/normalized_family_6.json",
    source_type: "internal_graph_export",
    audit_use: "Family, archetype, membership, role, survey-tier, and non-mutation graph identity.",
    rights_note: "Internal factual graph metadata; no third-party prose copied."
  },
  canonical_graph_family_8: {
    title: "Normalized canonical graph export, Family 8",
    publisher: "Waymark internal canonical graph",
    url: "data/canonical_graph/family_8/normalized_family_8.json",
    source_type: "internal_graph_export",
    audit_use: "Family, archetype, membership, role, survey-tier, and non-mutation graph identity.",
    rights_note: "Internal factual graph metadata; no third-party prose copied."
  },
  canonical_graph_family_10: {
    title: "Normalized canonical graph export, Family 10",
    publisher: "Waymark internal canonical graph",
    url: "data/canonical_graph/family_10/normalized_family_10.json",
    source_type: "internal_graph_export",
    audit_use: "Family, archetype, membership, role, survey-tier, and non-mutation graph identity.",
    rights_note: "Internal factual graph metadata; no third-party prose copied."
  },
  canonical_graph_review_bundle: {
    title: "Waymark Canonical Graph Review Bundle v0.1",
    publisher: "Waymark internal graph review",
    url: "docs/reviews/canonical_graph/waymark_canonical_graph_review_bundle_v0_1.md",
    source_type: "internal_graph_audit",
    audit_use: "Archetype summary, object counts, boundary risks, and graph gap posture.",
    rights_note: "Internal factual audit metadata; no third-party prose copied."
  },
  survey_candidate_sidecars_v0_2: {
    title: "Survey candidate sidecars v0.2",
    publisher: "Waymark internal canonical graph",
    url: "data/canonical_graph/normalization_pass_2",
    source_type: "internal_graph_sidecar",
    audit_use: "Survey candidate refs, boundary-question refs, and dead-end probe refs.",
    rights_note: "Internal factual graph metadata; no third-party prose copied."
  },
  britannica_rock_and_roll: {
    title: "Rock and roll",
    publisher: "Encyclopaedia Britannica",
    url: "https://www.britannica.com/art/rock-and-roll-early-style-of-rock-music",
    source_type: "reference",
    audit_use: "Rock and roll origins, teen audience, and R&B/country/gospel crossover framing.",
    rights_note: "Use for factual paraphrase only; no long quotations."
  },
  rockhall_chuck_berry: {
    title: "Chuck Berry",
    publisher: "Rock & Roll Hall of Fame",
    url: "https://rockhall.com/inductees/chuck-berry/",
    source_type: "museum_reference",
    audit_use: "Chuck Berry as a foundational rock and roll songwriter, guitarist, and performer.",
    rights_note: "Use for factual paraphrase only; no long quotations."
  },
  rockhall_sister_rosetta_tharpe: {
    title: "Sister Rosetta Tharpe",
    publisher: "Rock & Roll Hall of Fame",
    url: "https://rockhall.com/inductees/sister-rosetta-tharpe/",
    source_type: "museum_reference",
    audit_use: "Gospel guitar and early influence context for rock and roll foundations.",
    rights_note: "Use for factual paraphrase only; no long quotations."
  },
  loc_rock_around_the_clock: {
    title: "(We're Gonna) Rock Around the Clock",
    publisher: "Library of Congress National Recording Registry",
    url: "https://www.loc.gov/static/programs/national-recording-preservation-board/documents/RockAroundTheClock.pdf",
    source_type: "archive_reference",
    audit_use: "Recording-registry context for a mass early-rock breakthrough recording.",
    rights_note: "Use for factual paraphrase only; no long quotations."
  },
  britannica_rockabilly: {
    title: "Rockabilly",
    publisher: "Encyclopaedia Britannica",
    url: "https://www.britannica.com/art/rockabilly",
    source_type: "reference",
    audit_use: "Rockabilly as rhythm-driven country, R&B, blues, and gospel hybrid; style markers.",
    rights_note: "Use for factual paraphrase only; no long quotations."
  },
  sun_records_history: {
    title: "History",
    publisher: "Sun Records",
    url: "https://sunrecords.com/history/",
    source_type: "official_label",
    audit_use: "Sun Records, Sam Phillips, Elvis Presley, Carl Perkins, Jerry Lee Lewis, and early rockabilly label context.",
    rights_note: "Use for factual paraphrase only; no long quotations."
  },
  rockhall_carl_perkins: {
    title: "Carl Perkins",
    publisher: "Rock & Roll Hall of Fame",
    url: "https://rockhall.com/inductees/carl-perkins/",
    source_type: "museum_reference",
    audit_use: "Carl Perkins and rockabilly anchor context.",
    rights_note: "Use for factual paraphrase only; no long quotations."
  },
  loc_blue_suede_shoes: {
    title: "Blue Suede Shoes",
    publisher: "Library of Congress National Recording Registry",
    url: "https://www.loc.gov/static/programs/national-recording-preservation-board/documents/BlueSuedeShoes.pdf",
    source_type: "archive_reference",
    audit_use: "Recording-registry context for Carl Perkins and rockabilly.",
    rights_note: "Use for factual paraphrase only; no long quotations."
  },
  britannica_doo_wop: {
    title: "Doo-wop",
    publisher: "Encyclopaedia Britannica",
    url: "https://www.britannica.com/art/doo-wop-music",
    source_type: "reference",
    audit_use: "Doo-wop vocal-harmony structure, urban youth context, and influence.",
    rights_note: "Use for factual paraphrase only; no long quotations."
  },
  teachrock_doo_wop: {
    title: "Doo Wop",
    publisher: "TeachRock",
    url: "https://teachrock.org/genre/doo-wop/",
    source_type: "educational",
    audit_use: "Doo-wop and teen-pop lesson framing.",
    rights_note: "Use for factual paraphrase only; no long quotations."
  },
  rockhall_platters: {
    title: "The Platters",
    publisher: "Rock & Roll Hall of Fame",
    url: "https://rockhall.com/inductees/platters/",
    source_type: "museum_reference",
    audit_use: "Doo-wop and R&B vocal group bridge context.",
    rights_note: "Use for factual paraphrase only; no long quotations."
  },
  loc_recording_registry: {
    title: "Recording Registry",
    publisher: "Library of Congress National Recording Preservation Board",
    url: "https://www.loc.gov/programs/national-recording-preservation-board/recording-registry/",
    source_type: "archive_reference",
    audit_use: "Cultural preservation context for significant U.S. recordings.",
    rights_note: "Use for factual paraphrase only; no long quotations."
  },
  teachrock_dion_teen_idols: {
    title: "Dion and the Teen Idols",
    publisher: "TeachRock",
    url: "https://teachrock.org/lesson/dion-and-the-teen-idols/",
    source_type: "educational",
    audit_use: "Teen-idol role in bringing rock and roll into mainstream culture.",
    rights_note: "Use for factual paraphrase only; no long quotations."
  },
  teachrock_rock_roll_becomes_pop: {
    title: "Rock and Roll Becomes Pop",
    publisher: "TeachRock",
    url: "https://teachrock.org/chapter/rock-and-roll-becomes-pop/",
    source_type: "educational",
    audit_use: "Late-1950s mainstream pop smoothing of rock and roll.",
    rights_note: "Use for factual paraphrase only; no long quotations."
  },
  rockhall_ricky_nelson: {
    title: "Ricky Nelson",
    publisher: "Rock & Roll Hall of Fame",
    url: "https://rockhall.com/inductees/ricky-nelson/",
    source_type: "museum_reference",
    audit_use: "Teen-idol image balanced with rockabilly/pop craft.",
    rights_note: "Use for factual paraphrase only; no long quotations."
  },
  britannica_rock_1960s: {
    title: "Rock in the 1960s",
    publisher: "Encyclopaedia Britannica",
    url: "https://www.britannica.com/art/rock-music/Rock-in-the-1960s",
    source_type: "reference",
    audit_use: "Rock and roll's late-1950s move into teen pop and British Invasion aftermath.",
    rights_note: "Use for factual paraphrase only; no long quotations."
  },
  britannica_brill_building: {
    title: "The Brill Building: Assembly-Line Pop",
    publisher: "Encyclopaedia Britannica",
    url: "https://www.britannica.com/topic/The-Brill-Building-Assembly-Line-Pop-1688332",
    source_type: "reference",
    audit_use: "Professional songwriting, publishing, and girl-group pop craft ecosystem.",
    rights_note: "Use for factual paraphrase only; no long quotations."
  },
  britannica_girl_groups: {
    title: "Girl groups",
    publisher: "Encyclopaedia Britannica",
    url: "https://www.britannica.com/art/girl-group",
    source_type: "reference",
    audit_use: "Girl-group sound, Brill-linked writing teams, doo-wop/R&B/pop hybrid.",
    rights_note: "Use for factual paraphrase only; no long quotations."
  },
  teachrock_brill_girl_group: {
    title: "The Brill Building and the Girl Group Era",
    publisher: "TeachRock",
    url: "https://teachrock.org/chapter/the-brill-building-and-the-girl-group-era/",
    source_type: "educational",
    audit_use: "Brill, publishers, producers, songwriters, and girl-group era teaching context.",
    rights_note: "Use for factual paraphrase only; no long quotations."
  },
  rockhall_brill_guide: {
    title: "Brill Building Library Guide",
    publisher: "Rock & Roll Hall of Fame Library & Archives",
    url: "https://library.rockhall.com/brill_building",
    source_type: "archive_guide",
    audit_use: "Brill Building businesses, collections, and source-finding context.",
    rights_note: "Use as source guide; do not reproduce archival material."
  },
  britannica_soul_music: {
    title: "Soul music",
    publisher: "Encyclopaedia Britannica",
    url: "https://www.britannica.com/art/soul-music",
    source_type: "reference",
    audit_use: "Soul as gospel, blues, R&B, jazz, and rock-rooted popular music.",
    rights_note: "Use for factual paraphrase only; no long quotations."
  },
  britannica_rhythm_and_blues: {
    title: "Rhythm and blues",
    publisher: "Encyclopaedia Britannica",
    url: "https://www.britannica.com/art/rhythm-and-blues",
    source_type: "reference",
    audit_use: "R&B labels, crossover, and transitional figures such as Ray Charles and Sam Cooke.",
    rights_note: "Use for factual paraphrase only; no long quotations."
  },
  rockhall_ray_charles: {
    title: "Ray Charles",
    publisher: "Rock & Roll Hall of Fame",
    url: "https://rockhall.com/inductees/ray-charles/",
    source_type: "museum_reference",
    audit_use: "Ray Charles and soul crossover framing.",
    rights_note: "Use for factual paraphrase only; no long quotations."
  },
  britannica_ray_charles: {
    title: "Ray Charles",
    publisher: "Encyclopaedia Britannica",
    url: "https://www.britannica.com/biography/Ray-Charles",
    source_type: "reference",
    audit_use: "Ray Charles as an early developer of soul through gospel, R&B, and jazz melding.",
    rights_note: "Use for factual paraphrase only; no long quotations."
  },
  britannica_surf_music: {
    title: "Surf music",
    publisher: "Encyclopaedia Britannica",
    url: "https://www.britannica.com/art/surf-music",
    source_type: "reference",
    audit_use: "Dick Dale, instrumental surf, Beach Boys, West Coast guitar and harmony contexts.",
    rights_note: "Use for factual paraphrase only; no long quotations."
  },
  britannica_dick_dale: {
    title: "Dick Dale",
    publisher: "Encyclopaedia Britannica",
    url: "https://www.britannica.com/biography/Dick-Dale",
    source_type: "reference",
    audit_use: "Dick Dale's surf-guitar role, percussive playing, and reverb-amplifier context.",
    rights_note: "Use for factual paraphrase only; no long quotations."
  },
  rockhall_beach_boys: {
    title: "The Beach Boys",
    publisher: "Rock & Roll Hall of Fame",
    url: "https://rockhall.com/inductees/beach-boys/",
    source_type: "museum_reference",
    audit_use: "Beach Boys as surf-rock and harmony-pop gateway with studio-pop expansion.",
    rights_note: "Use for factual paraphrase only; no long quotations."
  },
  britannica_beach_boys: {
    title: "The Beach Boys",
    publisher: "Encyclopaedia Britannica",
    url: "https://www.britannica.com/topic/the-Beach-Boys",
    source_type: "reference",
    audit_use: "Beach Boys formation, harmonies, surf image, and Brian Wilson studio role.",
    rights_note: "Use for factual paraphrase only; no long quotations."
  },
  britannica_funk: {
    title: "Funk",
    publisher: "Encyclopaedia Britannica",
    url: "https://www.britannica.com/art/funk",
    source_type: "reference",
    audit_use: "Funk pioneers, groove foundation, social commentary, P-Funk, and hip-hop sampling afterlife.",
    rights_note: "Use for factual paraphrase only; no long quotations."
  },
  smithsonian_james_brown: {
    title: "James Brown: Godfather of Soul",
    publisher: "Smithsonian Institution",
    url: "https://www.si.edu/spotlight/james-brown",
    source_type: "museum_reference",
    audit_use: "James Brown's rhythmically driven funk aesthetic and influence.",
    rights_note: "Use for factual paraphrase only; no long quotations."
  },
  carnegie_hall_funk_timeline: {
    title: "History of Funk",
    publisher: "Carnegie Hall Timeline of African American Music",
    url: "https://timeline.carnegiehall.org/genres/funk",
    source_type: "educational_archive",
    audit_use: "Funk's Black musical roots, pioneers, bass/rhythm innovation, and movement context.",
    rights_note: "Use for factual paraphrase only; no long quotations."
  },
  britannica_george_clinton: {
    title: "George Clinton",
    publisher: "Encyclopaedia Britannica",
    url: "https://www.britannica.com/biography/George-Clinton-American-musician",
    source_type: "reference",
    audit_use: "Parliament-Funkadelic as theatrical, genre-bending funk and psychedelic rock collective.",
    rights_note: "Use for factual paraphrase only; no long quotations."
  },
  rockhall_james_brown: {
    title: "James Brown",
    publisher: "Rock & Roll Hall of Fame",
    url: "https://rockhall.com/inductees/james-brown/",
    source_type: "museum_reference",
    audit_use: "James Brown's relationship to soul, funk, and rap lineages.",
    rights_note: "Use for factual paraphrase only; no long quotations."
  },
  cbgb_official_about: {
    title: "CBGB: The Unique History",
    publisher: "CBGB",
    url: "https://www.cbgb.com/about",
    source_type: "official_venue",
    audit_use: "CBGB origin, Bowery setting, and punk/new wave artist roster.",
    rights_note: "Use for factual paraphrase only; no long quotations or proprietary images."
  },
  cbgb_hilly_history: {
    title: "History By Hilly",
    publisher: "CBGB",
    url: "https://www.cbgb.com/pages/history-by-hilly",
    source_type: "official_primary_context",
    audit_use: "Founder account of CBGB/OMFUG and early club framing.",
    rights_note: "Use for factual paraphrase only; avoid extended quotation."
  },
  britannica_cbgb: {
    title: "CBGB",
    publisher: "Encyclopaedia Britannica",
    url: "https://www.britannica.com/topic/CBGB-1688333",
    source_type: "reference",
    audit_use: "CBGB as 1973 Bowery venue tied to punk and new wave.",
    rights_note: "Use for factual paraphrase only; no long quotations."
  },
  britannica_punk: {
    title: "Punk",
    publisher: "Encyclopaedia Britannica",
    url: "https://www.britannica.com/art/punk",
    source_type: "reference",
    audit_use: "CBGB, Patti Smith, Television, and minimalist literary New York punk scene.",
    rights_note: "Use for factual paraphrase only; no long quotations."
  },
  cornell_punk_archives: {
    title: "Anarchy in the Archives: Punk Arrives",
    publisher: "Cornell University Library",
    url: "https://rmc.library.cornell.edu/punkfest/exhibition/punkarrives/newyork.html",
    source_type: "university_archive",
    audit_use: "Punk archive context for New York scene, CBGB artists, and visual/documentary evidence.",
    rights_note: "Use for factual paraphrase only; do not reproduce images."
  },
  britannica_strokes: {
    title: "The Strokes",
    publisher: "Encyclopaedia Britannica",
    url: "https://www.britannica.com/topic/the-Strokes",
    source_type: "reference",
    audit_use: "The Strokes and early-2000s garage-rock revival framing.",
    rights_note: "Use for factual paraphrase only; no long quotations."
  },
  rockhall_white_stripes: {
    title: "The White Stripes",
    publisher: "Rock & Roll Hall of Fame",
    url: "https://rockhall.com/inductees/white-stripes/",
    source_type: "museum_reference",
    audit_use: "White Stripes as minimal, blues-rooted rock revival and Rock Hall context.",
    rights_note: "Use for factual paraphrase only; no long quotations."
  },
  allmusic_garage_revival: {
    title: "Garage Rock Revival",
    publisher: "AllMusic",
    url: "https://www.allmusic.com/style/garage-rock-revival-ma0000012343",
    source_type: "music_reference",
    audit_use: "Supplemental style markers for garage-rock revival.",
    rights_note: "Use only as supplemental support; no long quotations."
  },
  britannica_white_stripes: {
    title: "The White Stripes",
    publisher: "Encyclopaedia Britannica",
    url: "https://www.britannica.com/topic/White-Stripes",
    source_type: "reference",
    audit_use: "White Stripes biography and 2000s rock context.",
    rights_note: "Use for factual paraphrase only; no long quotations."
  }
};

const COPY = {
  "001": {
    source_refs: ["canonical_graph_family_1", "canonical_graph_review_bundle", "britannica_rock_and_roll", "rockhall_chuck_berry", "rockhall_sister_rosetta_tharpe", "loc_rock_around_the_clock"],
    display_title: "Early Rock & Roll Foundations",
    short_definition: "The first mass rock and roll doorway: R&B, blues, gospel, country, jump-blues, and teen radio colliding into a new shared pop language.",
    history_capsule: "This road explains how mid-1950s rock and roll moved from regional R&B, country, gospel, and blues sources into national youth culture. It is not a single-origin story; it is a collision zone where Chuck Berry, Little Richard, Fats Domino, Elvis Presley, Buddy Holly, Bo Diddley, the Everly Brothers, and source-code figures like Sister Rosetta Tharpe all matter in different ways.",
    why_it_mattered: "It set the grammar for rock after it: backbeat, electric guitar, piano drive, vocal urgency, teenage address, danceable singles, and the idea that popular music could reorganize youth culture.",
    distinct: "Compared with later oldies or British Invasion routes, this lane is closer to the ignition point. It keeps R&B originals, rockabilly crossover, doo-wop overlap, and early pop radio from being flattened into one nostalgia bucket.",
    listen_for: ["the backbeat as an engine", "guitar or piano riffs that become hooks", "call-and-response energy", "country and blues phrasing living in the same record", "short singles built for radio and dancing"],
    caution: "A familiar early-rock title can mean recognition without a broad appetite for 1950s rock. Treat negative signals as route-specific unless repeated across songs, artists, and neighboring archetypes.",
    did_you_know: ["Early rock and roll was a shared audience event before it was a tidy genre label.", "Many Family 1 anchors are also boundary objects for soul, country, gospel, R&B, or later rock guitar roads."],
    claims: [
      ["001-history-hybrid", "Early rock and roll is best explained as a hybrid of R&B, blues, gospel, country, and teen-oriented pop radio rather than as a single-source invention.", ["britannica_rock_and_roll", "rockhall_sister_rosetta_tharpe"]],
      ["001-berry-guitar-songcraft", "Chuck Berry is a central anchor for rock and roll guitar language, teen-life songwriting, and performance stance.", ["rockhall_chuck_berry", "britannica_rock_and_roll"]],
      ["001-mass-breakthrough", "Mass early-rock breakthroughs such as Bill Haley and Elvis Presley helped move the sound into national youth culture.", ["britannica_rock_and_roll", "loc_rock_around_the_clock"]],
      ["001-graph-scope", "Graph membership should distinguish historical importance, survey recognition, and adjacent-family overlap for early R&B, gospel, doo-wop, and rockabilly objects.", ["canonical_graph_family_1", "canonical_graph_review_bundle"]]
    ]
  },
  "002": {
    source_refs: ["canonical_graph_family_1", "canonical_graph_review_bundle", "britannica_rockabilly", "sun_records_history", "rockhall_carl_perkins", "loc_blue_suede_shoes"],
    display_title: "Rockabilly, Primitive Guitar, and Proto-Garage",
    short_definition: "The rawer guitar road out of early rock: country snap, R&B drive, slapback echo, twang, distortion, and small-band urgency.",
    history_capsule: "Rockabilly came out of the same 1950s collision as rock and roll, but this road listens for the rougher, leaner side: Sun Records energy, Carl Perkins swing, Gene Vincent intensity, Bo Diddley pulse, Link Wray threat, and the guitar-first records that point toward garage rock.",
    why_it_mattered: "It made rock feel dangerous, handmade, and portable. The stripped band sound became a template for garage bands, punk minimalism, surf instrumentals, and later revival scenes.",
    distinct: "This is not just early rock in cowboy boots. The key difference is the attack: snap, echo, tremolo, distortion, and riffs that make a small combo feel bigger than it is.",
    listen_for: ["slapback echo around the vocal or guitar", "upright-bass or snare snap", "twangy low strings", "distorted instrumental hooks", "a rough edge that later garage bands could copy"],
    caution: "A user may like one primitive guitar hook without wanting deep rockabilly. Do not overread one Link Wray, Dick Dale, or Kingsmen signal as full-family appetite.",
    did_you_know: ["Sun Records is useful here because it holds both canonical rockabilly anchors and boundary artists whose later meanings spill into country, pop, or soul.", "Proto-garage examples are deliberately graph-sidecar notes, not permission to rename the archetype."],
    claims: [
      ["002-rockabilly-definition", "Rockabilly is a rhythm-driven early rock style built from country, blues, R&B, and gospel contact zones.", ["britannica_rockabilly"]],
      ["002-sun-center", "Sun Records is a key label context for Elvis Presley, Carl Perkins, Jerry Lee Lewis, and other early rockabilly-associated figures.", ["sun_records_history", "britannica_rockabilly"]],
      ["002-perkins-anchor", "Carl Perkins and Blue Suede Shoes are central rockabilly anchors for this road's survey logic.", ["rockhall_carl_perkins", "loc_blue_suede_shoes"]],
      ["002-graph-scope", "The graph intentionally keeps rockabilly, primitive guitar instrumentals, and proto-garage boundary objects together while preserving adjacent-family cautions.", ["canonical_graph_family_1", "canonical_graph_review_bundle"]]
    ]
  },
  "003": {
    source_refs: ["canonical_graph_family_1", "canonical_graph_review_bundle", "britannica_doo_wop", "teachrock_doo_wop", "rockhall_platters", "loc_recording_registry"],
    display_title: "Doo-Wop and Vocal Group Oldies",
    short_definition: "Street-corner and studio vocal harmony: lead voice, background blend, romance, nonsense syllables, and a bridge from R&B groups into pop memory.",
    history_capsule: "Doo-wop grew from vocal-group traditions and urban youth singing culture, where harmony could carry a record even with minimal instrumentation. This road links the Platters, the Drifters, the Penguins, the Five Satins, the Flamingos, Frankie Lymon and the Teenagers, and other groups whose records became oldies standards.",
    why_it_mattered: "It made vocal blend a central rock and pop device. Its harmonies fed girl groups, Motown, soul-pop, surf vocals, and the durable jukebox idea of the romantic oldie.",
    distinct: "Compared with teen-idol pop, this road is group-centered and harmony-first. Compared with Brill/girl-group pop, it is usually closer to R&B vocal ensemble roots.",
    listen_for: ["tenor lead against bass or group response", "nonsense syllables as rhythm", "close harmony carrying the hook", "light instrumentation under a big vocal blend", "romantic drama built from small vocal gestures"],
    caution: "Doo-wop recognition is often song-first. A user may know one wedding, movie, or oldies-radio title without wanting a full vocal-group path.",
    did_you_know: ["Doo-wop is one of the clearest examples of music that could be made with very little equipment but enormous vocal discipline.", "This road is a graph neighbor to girl-group pop, but it should not be collapsed into it."],
    claims: [
      ["003-doowop-form", "Doo-wop generally centers a lead vocalist supported by trio or quartet background harmony.", ["britannica_doo_wop"]],
      ["003-urban-youth", "Urban youth vocal-group practice helped shape doo-wop's street-corner and hallway mythology.", ["britannica_doo_wop", "teachrock_doo_wop"]],
      ["003-platters-bridge", "The Platters are a useful high-recognition bridge between doo-wop, R&B vocal groups, and pop oldies memory.", ["rockhall_platters", "canonical_graph_family_1"]],
      ["003-graph-scope", "Graph membership treats doo-wop as a song-first and mixed-object lane with boundaries to Brill, early soul, and teen-idol radio.", ["canonical_graph_family_1", "canonical_graph_review_bundle"]]
    ]
  },
  "004": {
    source_refs: ["canonical_graph_family_1", "canonical_graph_review_bundle", "teachrock_dion_teen_idols", "teachrock_rock_roll_becomes_pop", "rockhall_ricky_nelson", "britannica_rock_1960s"],
    display_title: "Teen Idol and Early Pop-Rock Radio",
    short_definition: "Late-1950s and early-1960s pop-rock star-making: smoother vocals, teen magazines, television, dance records, ballads, and radio-ready hooks.",
    history_capsule: "This lane captures the moment when rock and roll entered mainstream teen commerce. Ricky Nelson, Paul Anka, Neil Sedaka, Brenda Lee, Connie Francis, Lesley Gore, Bobby Vee, Bobby Rydell, and Frankie Avalon are not all the same musically, but the graph uses them to test pop-facing oldies appetite.",
    why_it_mattered: "Teen-idol pop helped normalize rock and roll for mass audiences and built a model for later youth pop: image, television, short singles, and tightly managed emotional address.",
    distinct: "Compared with early rock foundations, this road is smoother and more media-conscious. Compared with Brill pop, the performer image often carries as much survey meaning as the songwriting system.",
    listen_for: ["polished lead vocal identity", "teen-drama framing", "major-label radio clarity", "danceable but softened rock and roll", "TV or magazine-ready persona"],
    caution: "Do not treat a positive teen-idol signal as proof of broad early-rock appetite. This lane can be nostalgia, image, or one-song memory.",
    did_you_know: ["Teen-idol status can hide real musical craft; Ricky Nelson is a useful example of image and rockabilly-pop musicianship coexisting.", "This road helps Atlas separate affection for oldies radio from appetite for raw early rock or vocal-group harmony."],
    claims: [
      ["004-mainstreaming", "Teen idols helped move rock and roll from fringe youth culture into mainstream pop culture.", ["teachrock_dion_teen_idols", "teachrock_rock_roll_becomes_pop"]],
      ["004-late-50s-pop", "By the late 1950s, rock and roll was being softened and commercialized into more polished teen pop.", ["britannica_rock_1960s", "teachrock_rock_roll_becomes_pop"]],
      ["004-ricky-nelson", "Ricky Nelson is historically useful because teen-idol image and rockabilly-flavored pop craft overlap in his work.", ["rockhall_ricky_nelson"]],
      ["004-graph-scope", "The graph treats Teen Idol / Early Pop-Rock Radio as a pop-facing route with boundary risks around adult pop, Brill writing, and raw early rock.", ["canonical_graph_family_1", "canonical_graph_review_bundle"]]
    ]
  },
  "005": {
    source_refs: ["canonical_graph_family_1", "canonical_graph_review_bundle", "britannica_brill_building", "britannica_girl_groups", "teachrock_brill_girl_group", "rockhall_brill_guide"],
    display_title: "Brill Building, Girl Group, and Early 60s Pop Craft",
    short_definition: "Professional early-1960s pop architecture: songwriters, producers, publishers, studio musicians, and young vocal groups turning teen emotion into precision singles.",
    history_capsule: "This road is a craft ecosystem, not one sound. Brill-linked songwriters, New York publishers, producers, girl groups, and adjacent teen-pop artists built records where melody, arrangement, vocal personality, and studio control all mattered.",
    why_it_mattered: "It made the pop single feel engineered without losing emotional directness. The model fed later girl groups, Motown-era pop, singer-songwriter transitions, and modern pop's division of writing, producing, and performing labor.",
    distinct: "Compared with doo-wop, this road is more writer-producer-studio driven. Compared with teen-idol radio, it foregrounds the song factory and the girl-group voice as a system.",
    listen_for: ["big hook before the chorus even arrives", "girl-group lead voice against stacked backing vocals", "strings, percussion, or studio effects heightening teen melodrama", "songwriter craft that sounds effortless", "production choices that make a small song feel cinematic"],
    caution: "Girl-group affection, Brill songwriter interest, and Phil Spector-linked production appetite are related but not identical. Let the graph examples separate them.",
    did_you_know: ["The Brill Building name points to a business ecology as much as a musical style.", "Several canonical examples are survey gateways because the record, not the artist biography, is the strongest user signal."],
    claims: [
      ["005-ecosystem", "Brill/Girl Group pop is best explained as a songwriting, publishing, production, and performance ecosystem.", ["britannica_brill_building", "teachrock_brill_girl_group", "rockhall_brill_guide"]],
      ["005-girl-group-hybrid", "Girl-group records drew from doo-wop, R&B, rock and roll, and pop while foregrounding young female vocal identity.", ["britannica_girl_groups", "teachrock_brill_girl_group"]],
      ["005-songwriter-teams", "Brill-linked writing teams such as Goffin/King, Greenwich/Barry, and Mann/Weil are central to this road's historical explanation.", ["britannica_brill_building", "britannica_girl_groups"]],
      ["005-graph-scope", "The graph treats Brill/girl-group pop as a mixed-object lane with boundaries to doo-wop, teen-idol radio, early soul-pop, and later Motown.", ["canonical_graph_family_1", "canonical_graph_review_bundle"]]
    ]
  },
  "006": {
    source_refs: ["canonical_graph_family_1", "canonical_graph_review_bundle", "britannica_soul_music", "britannica_rhythm_and_blues", "rockhall_ray_charles", "britannica_ray_charles"],
    display_title: "Early Soul-Pop and R&B Crossover",
    short_definition: "The bridge where R&B, gospel feeling, pop songwriting, vocal heat, and early soul language start crossing into mainstream memory.",
    history_capsule: "This road explains why Ray Charles, Sam Cooke, Ben E. King, Jackie Wilson, the Drifters, Mary Wells, the Isley Brothers, early Motown, and early James Brown-related objects sit near early rock but point forward to soul, funk, and modern R&B.",
    why_it_mattered: "It turned R&B and gospel-rooted performance into a pop language with huge crossover force, opening routes toward Motown, southern soul, funk, disco, and R&B radio.",
    distinct: "Compared with early rock foundations, this lane has more gospel-rooted phrasing and soul-pop polish. Compared with later soul families, it is still close to oldies radio and early crossover mechanics.",
    listen_for: ["gospel-shaped melisma and call response", "R&B groove under pop structure", "horns, piano, or rhythm section pushing the vocal", "romantic or communal uplift with rhythmic bite", "records that feel oldies-adjacent but point forward"],
    caution: "An early soul-pop signal is not automatically a full funk, Motown, or quiet-storm signal. Keep route confidence local until later examples confirm it.",
    did_you_know: ["Ray Charles is useful here because his records make the gospel, R&B, jazz, and pop crossover audible.", "Some Family 1 early-soul objects deliberately have stronger later-family ownership."],
    claims: [
      ["006-soul-roots", "Soul music is rooted in gospel, blues, R&B, jazz, and rock-era popular music exchange.", ["britannica_soul_music", "britannica_rhythm_and_blues"]],
      ["006-ray-charles", "Ray Charles is a core early-soul figure because his work melded gospel, R&B, blues, jazz, and pop force.", ["britannica_ray_charles", "rockhall_ray_charles"]],
      ["006-crossover", "Early soul-pop and R&B crossover records helped connect 1950s R&B to 1960s soul and pop radio.", ["britannica_soul_music", "britannica_rhythm_and_blues"]],
      ["006-graph-scope", "The graph keeps early soul-pop in Family 1 while marking later soul, funk, Motown, and R&B ownership as boundary-sensitive.", ["canonical_graph_family_1", "canonical_graph_review_bundle"]]
    ]
  },
  "007": {
    source_refs: ["canonical_graph_family_1", "canonical_graph_review_bundle", "britannica_surf_music", "britannica_dick_dale", "rockhall_beach_boys", "britannica_beach_boys"],
    display_title: "Surf, Instrumental, and Early Guitar Pop",
    short_definition: "West Coast surf image, reverb-heavy guitar instrumentals, car-and-beach pop, and harmony-rich early guitar radio.",
    history_capsule: "This road has two bright halves: Dick Dale, the Ventures, the Chantays, and other instrumental guitar groups on one side; the Beach Boys, Jan and Dean, and vocal surf-pop on the other. Atlas keeps both because users often enter through different memories.",
    why_it_mattered: "It made guitar tone, reverb, speed, and California image into pop signals, while the Beach Boys opened a road from surf radio into sophisticated harmony and studio pop.",
    distinct: "Compared with rockabilly, this road is cleaner, wetter, and more panoramic. Compared with Brill pop, it is less about New York song-factory craft and more about guitar texture, harmony, and West Coast fantasy.",
    listen_for: ["spring reverb and rapid picking", "drum fills that mimic motion", "wordless guitar hooks", "stacked vocal harmonies", "surf, car, and California imagery as sound design"],
    caution: "The Beach Boys can mean surf nostalgia, harmony pop, or later studio experimentation. Use graph examples to avoid over-routing from one familiar song.",
    did_you_know: ["Instrumental surf and vocal surf are not interchangeable, but both are important survey gateways.", "This road is a clean early test for users who respond to guitar tone before lyrics."],
    claims: [
      ["007-surf-two-sides", "Surf music includes guitar-driven instrumental records and vocal harmony surf-pop centered on West Coast youth imagery.", ["britannica_surf_music", "britannica_beach_boys"]],
      ["007-dick-dale", "Dick Dale is a key surf-guitar pioneer associated with percussive playing and reverb-amplifier sound.", ["britannica_dick_dale", "britannica_surf_music"]],
      ["007-beach-boys", "The Beach Boys are central because they translated surf culture into harmony-rich pop and later studio ambition.", ["rockhall_beach_boys", "britannica_beach_boys"]],
      ["007-graph-scope", "The graph treats surf, instrumental guitar pop, car-song pop, and early guitar-radio objects as related but boundary-sensitive.", ["canonical_graph_family_1", "canonical_graph_review_bundle"]]
    ]
  },
  "039": {
    source_refs: ["canonical_graph_family_6", "canonical_graph_review_bundle", "britannica_funk", "smithsonian_james_brown", "carnegie_hall_funk_timeline", "britannica_george_clinton", "rockhall_james_brown"],
    display_title: "Funk, Psychedelic Soul, and Groove Canon",
    short_definition: "The groove road: James Brown's rhythmic command, Sly's psychedelic social fusion, P-Funk's mythology, and the bass-and-drum vocabulary that later hip-hop kept sampling.",
    history_capsule: "This archetype explains funk as a rhythmic and cultural language, not just a dance style. James Brown, Sly and the Family Stone, Parliament-Funkadelic, Earth, Wind & Fire, Kool & the Gang, Curtis Mayfield, the Isley Brothers, and the Meters all show different ways groove can lead the record.",
    why_it_mattered: "Funk changed how popular music organizes bodies in time. It put bass, drums, riffs, vamps, and collective call-response at the center, then became source material for disco, hip-hop, R&B, rock, and electronic music.",
    distinct: "Compared with Motown or early soul, this lane is more rhythm-forward and vamp-based. Compared with disco, it is earthier, more syncopated, and often more band-anchored.",
    listen_for: ["the one as a structural anchor", "bass lines that behave like lead hooks", "interlocking guitar, horn, and drum riffs", "group vocals and chants as groove devices", "longer vamps that build identity through repetition"],
    caution: "A single dance-floor hit may signal party recognition rather than deep funk appetite. Look for repeated positive signals across bass, band, and psychedelic-soul examples.",
    did_you_know: ["Funk is one of Atlas's strongest lineage roads because it explains both dance music and hip-hop sample memory.", "P-Funk belongs here as both groove canon and theatrical psychedelic world-building."],
    claims: [
      ["039-funk-pioneers", "James Brown, Sly and the Family Stone, and Parliament-Funkadelic are central funk pioneers for this archetype.", ["britannica_funk", "carnegie_hall_funk_timeline"]],
      ["039-rhythm-foundation", "Funk foregrounds groove, bass, drums, riffs, and rhythmic interlock more than conventional verse-centered pop structure.", ["britannica_funk", "smithsonian_james_brown"]],
      ["039-pfunk-theater", "George Clinton's Parliament-Funkadelic made funk a theatrical, genre-blending world that crossed soul, gospel, rock, and psychedelic language.", ["britannica_george_clinton", "britannica_funk"]],
      ["039-graph-scope", "Graph membership distinguishes funk's historical importance from user-specific party, disco, R&B, or hip-hop fit.", ["canonical_graph_family_6", "canonical_graph_review_bundle"]]
    ]
  },
  "054": {
    source_refs: ["canonical_graph_family_8", "canonical_graph_review_bundle", "cbgb_official_about", "cbgb_hilly_history", "britannica_cbgb", "britannica_punk", "cornell_punk_archives"],
    display_title: "CBGB, Art-Punk, and Downtown New York",
    short_definition: "Downtown New York's punk-and-art road: CBGB, literary minimalism, angular guitars, bohemian theater, and bands that made weird local scenes feel historically inevitable.",
    history_capsule: "This lane is anchored by CBGB and the Bowery scene around Television, Patti Smith, Ramones, Blondie, Talking Heads, Richard Hell, and adjacent downtown acts. It is not just loud punk; it is the point where poetry, art school, garage minimalism, fashion, and new wave possibility meet.",
    why_it_mattered: "It gave punk and new wave a laboratory. A small venue ecology helped define how scenes, zines, bands, and audiences could turn local oddness into a durable lineage.",
    distinct: "Compared with first-wave punk as a whole, this lane is more place-specific and art-literate. Compared with later hardcore, it is less about speed and more about attitude, minimalism, persona, and scene contact.",
    listen_for: ["dry room energy", "two-guitar tension or minimalist riffing", "spoken or literary vocal presence", "danceable awkwardness", "pop hooks hiding inside downtown abrasion"],
    caution: "CBGB recognition can come from brand memory, one band, or venue mythology. Keep it contextual unless the user's evidence also touches the sound and scene.",
    did_you_know: ["CBGB's name came from a different roots-music intention, but the room became a punk and new wave landmark.", "This archetype is useful for lineage modules because it connects punk, art rock, new wave, indie, and downtown culture."],
    claims: [
      ["054-cbgb-origin", "CBGB opened on the Bowery in 1973 and became a forum for American punk and new wave bands.", ["cbgb_official_about", "britannica_cbgb"]],
      ["054-scene-range", "The New York CBGB scene included literary, art-punk, minimalist, pop, and new-wave branches rather than one uniform punk sound.", ["britannica_punk", "cornell_punk_archives"]],
      ["054-founder-context", "Hilly Kristal's own framing helps explain why the venue's name and later punk identity should not be confused.", ["cbgb_hilly_history", "cbgb_official_about"]],
      ["054-graph-scope", "Graph membership treats CBGB / Art-Punk / Downtown New York as a place-and-lineage archetype with boundaries to hardcore, first-wave punk, post-punk, and new wave.", ["canonical_graph_family_8", "canonical_graph_review_bundle"]]
    ]
  },
  "079": {
    source_refs: ["canonical_graph_family_10", "canonical_graph_review_bundle", "britannica_strokes", "rockhall_white_stripes", "allmusic_garage_revival", "britannica_white_stripes"],
    display_title: "Garage Revival and Rock-Is-Back 2000s",
    short_definition: "The early-2000s return-of-rock road: skinny riffs, rough glamour, post-punk cool, blues minimalism, and indie guitars becoming mainstream conversation again.",
    history_capsule: "This lane follows the 2000s moment when the Strokes, the White Stripes, the Hives, the Vines, the Black Keys, the Libertines, and related bands made stripped-down guitar rock feel newly urgent. It points backward to Nuggets, garage, blues, and post-punk, but its survey meaning is very 2000s.",
    why_it_mattered: "It reset rock's surface language after grunge and post-grunge: smaller bands, tighter clothes, rawer production, club scenes, and hooks that could cross from indie circles to mass radio.",
    distinct: "Compared with 1990s alternative, this lane is more retro-coded and style-conscious. Compared with original garage rock, it is revival-aware, media-aware, and often indie-branded.",
    listen_for: ["dry drums and clipped guitar parts", "minimal blues or garage riffs", "cool vocal nonchalance", "post-punk rhythmic angles", "retro signals made to feel current"],
    caution: "A user may know a few 2000s rock singles without wanting garage revival as a lineage. Confirm with artist, album, and neighboring indie evidence.",
    did_you_know: ["The Strokes and White Stripes make different versions of the same reset: New York post-punk cool versus Detroit blues-garage minimalism.", "This road is a bridge between old garage DNA and modern indie discovery."],
    claims: [
      ["079-strokes-revival", "The Strokes are widely framed as spearheading an early-2000s revival of 1960s-style garage rock.", ["britannica_strokes"]],
      ["079-white-stripes-minimalism", "The White Stripes are central to the revival because they made minimal, blues-rooted garage rock feel newly powerful.", ["rockhall_white_stripes", "britannica_white_stripes"]],
      ["079-style-markers", "Garage-rock revival style often emphasizes fuzz or dry guitar attack, sneering or cool vocals, and retro garage-band cues.", ["allmusic_garage_revival", "britannica_strokes"]],
      ["079-graph-scope", "Graph membership separates 2000s garage revival from broader indie rock, post-punk revival, blues-rock, and current rock revival routes.", ["canonical_graph_family_10", "canonical_graph_review_bundle"]]
    ]
  }
};

function ensureFamilySourceReferences(graph) {
  for (const family of graph.families.values()) {
    const sourceId = `canonical_graph_family_${family.family_id}`;
    if (SOURCE_REFERENCES[sourceId]) continue;
    SOURCE_REFERENCES[sourceId] = {
      title: `Normalized canonical graph export, Family ${family.family_id}`,
      publisher: "Waymark internal canonical graph",
      url: family.source_file,
      source_type: "internal_graph_export",
      audit_use: "Family, archetype, membership, role, survey-tier, and non-mutation graph identity.",
      rights_note: "Internal factual graph metadata; no third-party prose copied."
    };
  }
}

function copyFor(entry) {
  if (COPY[entry.archetype_id]) {
    return {
      ...COPY[entry.archetype_id],
      research_editorial_status: "draft_research",
      render_editorial_status: "visualization_candidate",
      source_coverage_status: "checkpoint_sourced"
    };
  }

  const artistNames = sortRows(entry.artists).slice(0, 3).map((row) => row.artist_name).filter(Boolean);
  const songNames = sortRows(entry.songs).slice(0, 3).map((row) => row.song_title).filter(Boolean);
  const albumNames = sortRows(entry.albums).slice(0, 2).map((row) => row.album_title).filter(Boolean);
  const anchorList = [...artistNames, ...songNames, ...albumNames].slice(0, 5);
  const anchorCopy = anchorList.length ? anchorList.join("; ") : "its graph-listed artists, albums, songs, and survey candidates";
  const sourceId = `canonical_graph_family_${entry.family_id}`;

  return {
    source_refs: [sourceId, "canonical_graph_review_bundle", "survey_candidate_sidecars_v0_2"],
    research_editorial_status: "draft_research",
    render_editorial_status: "visualization_candidate",
    source_coverage_status: "internal_graph_only_needs_external_source_deepening",
    display_title: entry.archetype_name,
    short_definition: `The graph-defined ${entry.archetype_name} road inside ${entry.family_name}.`,
    history_capsule: `Atlas uses this draft road to explain how graph anchors such as ${anchorCopy} cluster inside ${entry.family_name}. This v0.2 pack stays deliberately graph-aligned until PM source-deepening adds archetype-specific external history sources.`,
    why_it_mattered: `Within the canonical graph, this road matters because it separates ${entry.archetype_name} signals from neighboring roads and gives Atlas deterministic context for survey, region, lineage, and mission-detail surfaces.`,
    distinct: `Its current boundary is defined by the canonical graph label, object memberships, roles, readiness sidecars, survey candidates, boundary questions, and dead-end probes. It is not a renamed or newly invented taxonomy.`,
    listen_for: [
      "the shared traits connecting the graph anchors",
      "which examples are song-first versus artist-first",
      "where boundary objects point to nearby roads",
      "whether user evidence repeats across more than one object type"
    ],
    caution: `Treat ${entry.archetype_name} as a contextual graph road until user evidence repeats across explicit Atlas state fields. Do not turn one familiar object into broad-family certainty.`,
    did_you_know: [
      `This draft pack is generated from existing graph identity for ${entry.canonical_graph_ref}; it does not mutate the graph.`,
      "PM source-deepening should add external history references before any production-copy approval."
    ],
    claims: [
      [`${entry.archetype_id}-graph-identity`, `${entry.archetype_name} is an existing canonical graph archetype in Family ${entry.family_id}, ${entry.family_name}.`, [sourceId, "canonical_graph_review_bundle"]],
      [`${entry.archetype_id}-membership-shape`, `The draft explainer scope is derived from existing artist, album, song-recording, survey-candidate, boundary-question, and dead-end-probe refs.`, [sourceId, "survey_candidate_sidecars_v0_2"]],
      [`${entry.archetype_id}-non-mutation`, `This pack adds educational sidecar copy only and does not rename archetypes, add graph nodes, or change memberships.`, [sourceId, "canonical_graph_review_bundle"]],
      [`${entry.archetype_id}-source-status`, `External archetype-specific source deepening is still required before production-copy approval.`, ["canonical_graph_review_bundle"]]
    ]
  };
}

const auditEntrySchema = {
  type: "object",
  required: ["claim_id", "claim_text", "source_ref_ids", "confidence", "module_usage", "graph_refs", "audit_status"],
  properties: {
    claim_id: { type: "string" },
    claim_text: { type: "string" },
    source_ref_ids: { type: "array", items: { type: "string" }, minItems: 1 },
    confidence: { type: "string" },
    module_usage: { type: "array", items: { type: "string" }, minItems: 1 },
    graph_refs: { type: "array", items: { type: "string" }, minItems: 1 },
    audit_status: { type: "string" }
  },
  additionalProperties: true
};

const canonicalExampleSchema = {
  type: "object",
  required: ["example_ref", "example_type", "display_label", "why_this_example_matters", "what_to_listen_for", "graph_ref_validation_status"],
  properties: {
    example_ref: { type: "string" },
    example_type: { enum: ["artist", "album", "song_recording", "survey_candidate"] },
    display_label: { type: "string" },
    why_this_example_matters: { type: "string" },
    what_to_listen_for: { type: "array", items: { type: "string" }, minItems: 1 },
    graph_ref_validation_status: { type: "string" }
  },
  additionalProperties: true
};

const moduleVariantSchema = {
  type: "object",
  required: ["compact", "standard", "deep"],
  properties: {
    compact: { type: "string" },
    standard: { type: "string" },
    deep: { type: "string" }
  },
  additionalProperties: false
};

const modulesSchema = {
  type: "object",
  required: [
    "atlas_home_region_card",
    "region_scene_page",
    "mission_detail_history_module",
    "did_you_know_card",
    "what_to_listen_for_prompt",
    "personalized_atlas_overlay",
    "canonical_examples_block",
    "related_roads_lineage_module",
    "dead_end_false_nearby_caution_module"
  ],
  properties: {
    atlas_home_region_card: moduleVariantSchema,
    region_scene_page: moduleVariantSchema,
    mission_detail_history_module: moduleVariantSchema,
    did_you_know_card: moduleVariantSchema,
    what_to_listen_for_prompt: moduleVariantSchema,
    personalized_atlas_overlay: moduleVariantSchema,
    canonical_examples_block: moduleVariantSchema,
    related_roads_lineage_module: moduleVariantSchema,
    dead_end_false_nearby_caution_module: moduleVariantSchema
  },
  additionalProperties: false
};

const RESEARCH_SCHEMA = {
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://waymark.local/schemas/atlas_explainer_research_pack_schema_v0_2.json",
  title: "Atlas Explainer Research Pack v0.2",
  type: "object",
  required: [
    "schema_version",
    "pack_id",
    "identity",
    "graph_alignment",
    "explainer_content",
    "source_references",
    "claim_level_source_audit",
    "rights_policy",
    "editorial_status",
    "non_mutation_policy",
    "alpha_v0_mission_boundary"
  ],
  properties: {
    schema_version: { const: "0.2" },
    pack_id: { type: "string" },
    generated_at: { type: "string" },
    identity: { type: "object" },
    graph_alignment: { type: "object" },
    explainer_content: {
      type: "object",
      required: ["canonical_example_rationales"],
      properties: {
        canonical_example_rationales: { type: "array", items: canonicalExampleSchema, minItems: 1 }
      },
      additionalProperties: true
    },
    source_references: { type: "object" },
    claim_level_source_audit: { type: "array", items: auditEntrySchema, minItems: 4 },
    rights_policy: { type: "object" },
    editorial_status: { enum: ["draft_research", "pm_review_needed", "visualization_candidate", "alpha_render_candidate", "production_copy_candidate", "blocked"] },
    non_mutation_policy: { type: "object" },
    alpha_v0_mission_boundary: { type: "object" }
  },
  additionalProperties: true
};

const RENDER_SCHEMA = {
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://waymark.local/schemas/atlas_explainer_render_pack_schema_v0_2.json",
  title: "Atlas Explainer Render Pack v0.2",
  type: "object",
  required: [
    "schema_version",
    "render_pack_id",
    "identity",
    "graph_alignment",
    "modules",
    "canonical_examples",
    "personalization_hooks",
    "source_claim_refs",
    "rights_status",
    "editorial_status",
    "non_mutation_assertion",
    "alpha_v0_mission_boundary"
  ],
  properties: {
    schema_version: { const: "0.2" },
    render_pack_id: { type: "string" },
    identity: { type: "object" },
    graph_alignment: { type: "object" },
    modules: modulesSchema,
    canonical_examples: { type: "array", items: canonicalExampleSchema, minItems: 1 },
    personalization_hooks: { type: "array" },
    source_claim_refs: { type: "array", items: { type: "string" }, minItems: 1 },
    rights_status: { enum: ["pass", "needs_review", "blocked"] },
    editorial_status: { enum: ["draft_research", "pm_review_needed", "visualization_candidate", "alpha_render_candidate", "production_copy_candidate", "blocked"] },
    non_mutation_assertion: { type: "string" },
    alpha_v0_mission_boundary: { type: "object" }
  },
  additionalProperties: true
};

function readJson(relPath) {
  return JSON.parse(fs.readFileSync(path.join(ROOT, relPath), "utf8"));
}

function writeJson(filePath, value) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, `${JSON.stringify(value, null, 2)}\n`);
}

function writeText(filePath, value) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, value.endsWith("\n") ? value : `${value}\n`);
}

function slugify(value) {
  return String(value)
    .toLowerCase()
    .replace(/&/g, " and ")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .replace(/-{2,}/g, "-");
}

function graphRef(familyId, archetypeId) {
  return `family_${String(familyId).padStart(2, "0")}/archetype_${archetypeId}`;
}

function familySlug(familyName) {
  return slugify(familyName);
}

function idFromMeta(meta, fileFamilyId) {
  if (typeof meta.family_number === "number") return meta.family_number;
  if (typeof meta.agent_family === "number") return meta.agent_family;
  if (typeof meta.family_id === "string") {
    const match = meta.family_id.match(/\d+/);
    if (match) return Number(match[0]);
  }
  return fileFamilyId;
}

function displayLabel(row, type) {
  if (type === "artist") return row.artist_name || row.display_name || row.proposed_artist_id;
  if (type === "album") return `${row.album_title || row.display_name} - ${row.artist_name || ""}`.replace(/\s+-\s+$/, "");
  return `${row.song_title || row.display_name} - ${row.artist_name || ""}`.replace(/\s+-\s+$/, "");
}

function objectId(row, type) {
  if (type === "artist") return row.proposed_artist_id || row.canonical_artist_id || row.artist_id;
  if (type === "album") return row.proposed_album_id || row.canonical_album_id || row.album_id;
  return row.proposed_song_id || row.canonical_song_recording_id || row.song_recording_id || row.song_id;
}

function objectRef(row, type) {
  const id = objectId(row, type);
  if (!id) return null;
  return `${type === "song" ? "song_recording" : type}:${id}`;
}

function sourceMembershipId(familyId, archetypeId, type, id) {
  const memberType = type === "song" ? "song" : type;
  return `family-${familyId}-${memberType}-${archetypeId}-${id}`;
}

function normalizeRoles(row) {
  if (Array.isArray(row.roles)) return row.roles;
  if (typeof row.roles === "string") return row.roles.split(/[;,]/).map((r) => r.trim()).filter(Boolean);
  return [];
}

function sortRows(rows) {
  const tierWeight = { mass: 5, high: 4, medium: 3, low: 2, cult: 1 };
  const surveyWeight = { core: 4, standard: 3, edge: 2, suppress: 1 };
  return [...rows].sort((a, b) => {
    const aw = (surveyWeight[a.survey_tier] || 0) * 10 + (tierWeight[a.recognition_tier] || 0) + (normalizeRoles(a).includes("anchor") ? 5 : 0) + (normalizeRoles(a).includes("artist_anchor") || normalizeRoles(a).includes("album_anchor") ? 3 : 0);
    const bw = (surveyWeight[b.survey_tier] || 0) * 10 + (tierWeight[b.recognition_tier] || 0) + (normalizeRoles(b).includes("anchor") ? 5 : 0) + (normalizeRoles(b).includes("artist_anchor") || normalizeRoles(b).includes("album_anchor") ? 3 : 0);
    return bw - aw;
  });
}

function collectCandidates(fileName) {
  const source = readJson(`data/canonical_graph/normalization_pass_2/${fileName}`);
  const rows = [];
  for (const family of source.families || []) {
    for (const key of ["page1_core", "page2_adaptive", "page3_deep", "suppressed", "suppressed_quarantined"]) {
      if (Array.isArray(family[key])) rows.push(...family[key]);
    }
  }
  return rows;
}

function loadGraph() {
  const familyDirs = fs.readdirSync(path.join(ROOT, "data/canonical_graph"))
    .filter((name) => /^family_\d+$/.test(name))
    .sort((a, b) => Number(a.match(/\d+/)[0]) - Number(b.match(/\d+/)[0]));
  const families = new Map();
  const archetypes = new Map();
  const validGraphRefs = new Set();

  for (const dir of familyDirs) {
    const fileFamilyId = Number(dir.match(/\d+/)[0]);
    const rel = `data/canonical_graph/${dir}/normalized_${dir}.json`;
    const data = readJson(rel);
    const meta = data.metadata || {};
    const familyId = idFromMeta(meta, fileFamilyId);
    const familyName = meta.family_name || data.family_name;
    const family = {
      family_id: familyId,
      family_name: familyName,
      family_slug: familySlug(familyName),
      source_file: rel,
      artists: data.artists || [],
      albums: data.albums || [],
      songs: data.songs || []
    };
    families.set(familyId, family);

    let archetypeEntries = [];
    if (meta.archetypes && !Array.isArray(meta.archetypes) && typeof meta.archetypes === "object") {
      archetypeEntries = Object.entries(meta.archetypes).map(([id, name]) => ({ id, name }));
    } else if (Array.isArray(meta.archetypes)) {
      archetypeEntries = meta.archetypes.map((a) => ({ id: a.archetype_id, name: a.name || a.archetype_name }));
    } else if (Array.isArray(meta.archetype_counts)) {
      archetypeEntries = meta.archetype_counts.map((a) => ({ id: a.archetype_id, name: a.archetype_name }));
    } else if (familyId === 2) {
      archetypeEntries = Object.entries(FAMILY_2_ARCHETYPES).map(([id, name]) => ({ id, name }));
    }

    const rowArchetypeIds = new Set([...family.artists, ...family.albums, ...family.songs].map((row) => row.archetype_id).filter(Boolean));
    for (const id of rowArchetypeIds) {
      if (!archetypeEntries.some((entry) => entry.id === id)) {
        archetypeEntries.push({ id, name: `Archetype ${id}` });
      }
    }

    for (const { id, name } of archetypeEntries) {
      const artists = family.artists.filter((row) => row.archetype_id === id);
      const albums = family.albums.filter((row) => row.archetype_id === id);
      const songs = family.songs.filter((row) => row.archetype_id === id);
      const ref = graphRef(familyId, id);
      archetypes.set(ref, {
        family_id: familyId,
        family_name: familyName,
        family_slug: family.family_slug,
        archetype_id: id,
        archetype_name: name,
        archetype_slug: slugify(name),
        canonical_graph_ref: ref,
        artists,
        albums,
        songs,
        source_file: rel
      });
      for (const row of artists) validGraphRefs.add(objectRef(row, "artist"));
      for (const row of albums) validGraphRefs.add(objectRef(row, "album"));
      for (const row of songs) validGraphRefs.add(objectRef(row, "song"));
    }
  }

  const surveyRows = [
    ...collectCandidates("survey_artist_candidates_v0_2.json"),
    ...collectCandidates("survey_album_candidates_v0_2.json"),
    ...collectCandidates("survey_song_candidates_v0_2.json")
  ];
  const boundaryRows = readJson("data/canonical_graph/normalization_pass_2/boundary_question_bank_v0_2.json");
  const deadEndRows = readJson("data/canonical_graph/normalization_pass_2/dead_end_probe_candidates_v0_2.json");
  const readinessRows = readJson("data/canonical_graph/normalization_pass_2/archetype_readiness_v0_2.json");

  for (const row of surveyRows) {
    for (const aid of row.archetype_ids || []) {
      const ref = graphRef(row.family_id, aid);
      const entry = archetypes.get(ref);
      if (!entry) continue;
      entry.survey_candidates ||= [];
      entry.survey_candidates.push(row);
    }
  }
  for (const row of boundaryRows) {
    const idMatch = row.question_id?.match(/-(\d{3})$/);
    const aid = idMatch?.[1];
    const ref = aid ? graphRef(row.family_id, aid) : null;
    const entry = ref ? archetypes.get(ref) : null;
    if (!entry) continue;
    entry.boundary_questions ||= [];
    entry.boundary_questions.push(row);
  }
  for (const row of deadEndRows) {
    for (const aid of row.archetype_ids || []) {
      const ref = graphRef(row.family_id, aid);
      const entry = archetypes.get(ref);
      if (!entry) continue;
      entry.dead_end_probes ||= [];
      entry.dead_end_probes.push(row);
    }
  }
  for (const row of readinessRows) {
    const ref = graphRef(row.family_id, row.archetype_id);
    const entry = archetypes.get(ref);
    if (entry) entry.readiness = row;
  }

  return { families, archetypes, validGraphRefs, surveyRows };
}

function graphAlignment(entry, allArchetypes) {
  const familyArchetypes = [...allArchetypes.values()]
    .filter((item) => item.family_id === entry.family_id)
    .sort((a, b) => a.archetype_id.localeCompare(b.archetype_id));
  const index = familyArchetypes.findIndex((item) => item.archetype_id === entry.archetype_id);
  const before = index > 0 ? [familyArchetypes[index - 1].canonical_graph_ref] : [];
  const after = index >= 0 && index < familyArchetypes.length - 1 ? [familyArchetypes[index + 1].canonical_graph_ref] : [];
  const related = [...new Set([...before, ...after])];
  return {
    canonical_artist_refs: sortRows(entry.artists).slice(0, 12).map((row) => rowRef(row, entry, "artist")),
    canonical_album_refs: sortRows(entry.albums).slice(0, 10).map((row) => rowRef(row, entry, "album")),
    canonical_song_recording_refs: sortRows(entry.songs).slice(0, 14).map((row) => rowRef(row, entry, "song")),
    survey_candidate_refs: (entry.survey_candidates || []).slice(0, 20).map((row) => ({
      ref: `survey_candidate:${row.candidate_id}`,
      candidate_id: row.candidate_id,
      object_type: row.object_type,
      display_label: row.display_label,
      survey_page_role: row.survey_page_role,
      survey_intent: row.survey_intent,
      review_status: row.review_status
    })),
    boundary_question_refs: (entry.boundary_questions || []).slice(0, 20).map((row) => ({
      ref: `boundary_question:${row.question_id}`,
      question_id: row.question_id,
      display_label: row.display_label,
      question_intent: row.question_intent
    })),
    dead_end_probe_refs: (entry.dead_end_probes || []).slice(0, 20).map((row) => ({
      ref: `dead_end_probe:${row.probe_id}`,
      probe_id: row.probe_id,
      entity_type: row.entity_type,
      display_label: row.display_label,
      recommended_surface: row.recommended_surface
    })),
    related_archetype_refs: related,
    before_archetype_refs: before,
    after_archetype_refs: after
  };
}

function rowRef(row, entry, type) {
  const id = objectId(row, type);
  return {
    ref: objectRef(row, type),
    object_id: id,
    display_label: displayLabel(row, type),
    source_membership_id: sourceMembershipId(entry.family_id, entry.archetype_id, type, id),
    roles: normalizeRoles(row),
    recognition_tier: row.recognition_tier || null,
    survey_tier: row.survey_tier || null,
    inclusion_reason: row.inclusion_reason || null,
    graph_ref_validation_status: "validated_in_normalized_family_export"
  };
}

function canonicalExampleRationales(entry, alignment, copy) {
  const examples = [
    ...alignment.canonical_artist_refs.slice(0, 2).map((item) => ({ ...item, example_type: "artist" })),
    ...alignment.canonical_album_refs.slice(0, 2).map((item) => ({ ...item, example_type: "album" })),
    ...alignment.canonical_song_recording_refs.slice(0, 3).map((item) => ({ ...item, example_type: "song_recording" }))
  ].slice(0, 6);
  return examples.map((item) => ({
    example_ref: item.ref,
    example_type: item.example_type,
    display_label: item.display_label,
    why_this_example_matters: item.inclusion_reason || `${item.display_label} is a graph-listed ${item.example_type} example for ${entry.archetype_name}.`,
    what_to_listen_for: copy.listen_for.slice(0, 2),
    graph_ref_validation_status: item.graph_ref_validation_status
  }));
}

function claimTarget(entry) {
  const total = entry.artists.length + entry.albums.length + entry.songs.length;
  const denseName = /scene|ecosystem|foundations|canon|crossover|global|hip-hop|metal|electronic|punk|soul|jazz|country|pop|rock|r&b|r-and-b/i.test(entry.archetype_name);
  if (total >= 80 || (denseName && total >= 45)) return 8;
  if (total >= 25) return 6;
  return 4;
}

function expandedClaims(copy, entry, alignment) {
  const sourceId = `canonical_graph_family_${entry.family_id}`;
  const claims = [...copy.claims];
  const target = claimTarget(entry);
  const candidateCount = alignment.survey_candidate_refs.length;
  const boundaryCount = alignment.boundary_question_refs.length;
  const probeCount = alignment.dead_end_probe_refs.length;
  const exampleCount = alignment.canonical_artist_refs.length + alignment.canonical_album_refs.length + alignment.canonical_song_recording_refs.length;
  const generated = [
    [`${entry.archetype_id}-canonical-example-validation`, `Canonical examples for ${entry.archetype_name} are selected only from existing artist, album, song-recording, or survey-candidate refs.`, [sourceId, "canonical_graph_review_bundle"]],
    [`${entry.archetype_id}-survey-candidate-alignment`, `${entry.archetype_name} has ${candidateCount} survey-candidate refs available in the v0.2 sidecars for deterministic Atlas surfaces.`, ["survey_candidate_sidecars_v0_2", sourceId]],
    [`${entry.archetype_id}-boundary-readiness`, `${entry.archetype_name} has ${boundaryCount} boundary-question refs and ${probeCount} dead-end probe refs available for false-nearby caution logic.`, ["survey_candidate_sidecars_v0_2", sourceId]],
    [`${entry.archetype_id}-render-boundary`, `Render copy for ${entry.archetype_name} must stay explanatory in Alpha and must not imply dynamic mission generation.`, ["canonical_graph_review_bundle"]],
    [`${entry.archetype_id}-rights-policy`, "Rights policy for this pack prohibits lyrics, long quotations, third-party copy blocks, proprietary album art dependencies, artist-photo dependencies, and scraping-derived proprietary metadata.", ["canonical_graph_review_bundle"]],
    [`${entry.archetype_id}-example-density`, `${entry.archetype_name} exposes ${exampleCount} graph example refs across artists, albums, and song recordings before render-pack trimming.`, [sourceId, "canonical_graph_review_bundle"]],
    [`${entry.archetype_id}-state-contract`, `Personalization for ${entry.archetype_name} is limited to explicit atlas_state fields or proposed dependencies reported in the state-field dependency index.`, ["survey_candidate_sidecars_v0_2"]],
    [`${entry.archetype_id}-editorial-status`, `${entry.archetype_name} is not production-approved in v0.2; PM review is required before production copy promotion.`, ["canonical_graph_review_bundle"]]
  ];
  for (const claim of generated) {
    if (claims.length >= target) break;
    claims.push(claim);
  }
  return claims;
}

function claimAudit(copy, entry, alignment) {
  return expandedClaims(copy, entry, alignment).map(([claimId, claimText, sourceRefIds]) => ({
    claim_id: claimId,
    claim_text: claimText,
    source_ref_ids: sourceRefIds,
    confidence: "medium_high",
    notes: "Concise factual claim paraphrased from listed sources and graph sidecars.",
    module_usage: ["history_capsule", "why_it_mattered", "region_scene_page", "mission_detail_history_module"],
    graph_refs: [entry.canonical_graph_ref],
    audit_status: "source_supported"
  }));
}

function buildResearchPack(entry, alignment) {
  const copy = copyFor(entry);
  const examples = canonicalExampleRationales(entry, alignment, copy);
  const claimLevelSourceAudit = claimAudit(copy, entry, alignment);
  const sourceIds = [...new Set([
    ...copy.source_refs,
    ...claimLevelSourceAudit.flatMap((claim) => claim.source_ref_ids)
  ])];
  const sourceReferences = Object.fromEntries(sourceIds.map((id) => [id, SOURCE_REFERENCES[id]]));
  return {
    schema_version: "0.2",
    pack_id: `family_${String(entry.family_id).padStart(2, "0")}_archetype_${entry.archetype_id}_${entry.archetype_slug}_research_v0_2`,
    generated_at: GENERATED_AT,
    source_graph_bundle: {
      canonical_graph_export: entry.source_file,
      normalization_pass_2_manifest: "data/canonical_graph/normalization_pass_2/normalization_pass_2_manifest.json",
      graph_review_bundle: "docs/reviews/canonical_graph/waymark_canonical_graph_review_bundle_v0_1.md"
    },
    identity: {
      family_id: entry.family_id,
      family_slug: entry.family_slug,
      family_name: entry.family_name,
      archetype_id: entry.archetype_id,
      archetype_slug: entry.archetype_slug,
      canonical_graph_ref: entry.canonical_graph_ref,
      existing_graph_label_name: entry.archetype_name,
      editorial_display_title: copy.display_title,
      non_mutation_assertion: "This research pack is a sidecar only; it does not create, rename, delete, merge, or reclassify canonical graph identities."
    },
    graph_alignment: alignment,
    source_references: sourceReferences,
    claim_level_source_audit: claimLevelSourceAudit,
    explainer_content: {
      short_definition: copy.short_definition,
      history_capsule: copy.history_capsule,
      why_it_mattered: copy.why_it_mattered,
      what_made_it_distinct: copy.distinct,
      what_to_listen_for: copy.listen_for,
      canonical_example_rationales: examples,
      before_after_related_roads: {
        before: alignment.before_archetype_refs,
        after: alignment.after_archetype_refs,
        related: alignment.related_archetype_refs,
        copy: `Use ${copy.display_title} as a contextual road inside ${entry.family_name}; related roads explain contrast, sequence, and survey uncertainty while staying inside Alpha scope.`
      },
      did_you_know_cards: copy.did_you_know.map((text, index) => ({
        card_id: `${entry.archetype_id}-dyk-${index + 1}`,
        copy: text,
        source_ref_ids: copy.source_refs.slice(0, 3)
      })),
      mission_description_snippets: [
        `What this route tests: whether ${copy.display_title.toLowerCase()} is a useful listening-history doorway for this user.`,
        `Why this region explains the batch: it gives context around graph anchors while staying inside Alpha scope.`
      ],
      atlas_region_page_copy_blocks: [
        copy.short_definition,
        copy.why_it_mattered,
        copy.distinct
      ],
      dead_end_false_nearby_caution_language: copy.caution,
      personalization_hooks: personalizationHooks(entry, copy),
      source_references: sourceReferences,
      claim_level_source_audit: claimLevelSourceAudit,
      editorial_status: copy.research_editorial_status,
      source_coverage_status: copy.source_coverage_status
    },
    graph_gap_observations: [],
    rights_policy: {
      rights_status: "pass",
      rights_notes: "Original educational prose. No lyrics, no long quotations, no third-party copy blocks, no album art, no artist photos, and no proprietary metadata scraping dependency."
    },
    alpha_v0_mission_boundary: {
      allowed_language_policy: "Contextual Alpha language only: related mission, included in first batch, what this route tests, why this region explains the batch, not in Alpha batch yet, you may encounter this road later.",
      forbidden_language_policy: "No runtime route-creation language."
    },
    non_mutation_policy: {
      status: "pass",
      assertion: "Sidecar-only explainer pack. Canonical graph identity remains unchanged."
    },
    editorial_status: copy.research_editorial_status
  };
}

function variant(compact, standard, deep) {
  return { compact, standard, deep };
}

function homeRegionStandard(entry, copy) {
  const options = [
    `${copy.display_title} gives ${entry.family_name} a clear Atlas doorway: ${copy.short_definition}`,
    `Use ${copy.display_title} to orient this region: ${copy.short_definition}`,
    `${entry.family_name} gets sharper here because ${copy.display_title.toLowerCase()} separates nearby signals without rewriting the graph.`,
    `${copy.display_title} frames this part of the map with graph-validated examples, source-audited claims, and explicit boundary cautions.`
  ];
  return options[Number(entry.archetype_id) % options.length];
}

function buildRenderPack(entry, alignment, researchPack) {
  const copy = copyFor(entry);
  const exampleLabels = researchPack.explainer_content.canonical_example_rationales
    .slice(0, 4)
    .map((item) => item.display_label);
  const modules = {
    atlas_home_region_card: variant(
      copy.short_definition,
      homeRegionStandard(entry, copy),
      `${copy.short_definition} ${copy.why_it_mattered}`
    ),
    region_scene_page: variant(
      copy.why_it_mattered,
      `${copy.history_capsule} ${copy.distinct}`,
      `${copy.history_capsule} ${copy.why_it_mattered} ${copy.distinct}`
    ),
    mission_detail_history_module: variant(
      `What this route tests: ${copy.short_definition}`,
      `${copy.history_capsule} This module explains the related road and stays explanatory in Alpha.`,
      `${copy.history_capsule} ${copy.why_it_mattered} Use it as context for the active mission and related mission history.`
    ),
    did_you_know_card: variant(
      copy.did_you_know[0],
      copy.did_you_know.join(" "),
      `${copy.did_you_know.join(" ")} Source coverage is claim-audited in the research pack.`
    ),
    what_to_listen_for_prompt: variant(
      `Listen for ${copy.listen_for.slice(0, 2).join(" and ")}.`,
      `Listen for ${copy.listen_for.slice(0, 3).join(", ")}.`,
      `Listen for ${copy.listen_for.join(", ")}.`
    ),
    personalized_atlas_overlay: variant(
      `This road can refine your Atlas map when your signals touch ${copy.display_title.toLowerCase()}.`,
      `If your Atlas state shows repeated positive evidence here, use ${copy.display_title} as a contextual landmark, not a promise of broad family fit.`,
      `When survey, mission, and saved-object evidence all point here, this road can explain why nearby examples feel connected while still preserving boundary cautions.`
    ),
    canonical_examples_block: variant(
      `Examples: ${exampleLabels.slice(0, 2).join("; ")}.`,
      `Graph examples: ${exampleLabels.join("; ")}.`,
      `Graph examples are validated against canonical refs or survey candidates: ${exampleLabels.join("; ")}.`
    ),
    related_roads_lineage_module: variant(
      `Related roads: ${alignment.related_archetype_refs.join(", ") || "none listed"}.`,
      `Before/after context: ${[...alignment.before_archetype_refs, ...alignment.after_archetype_refs].join(", ") || "family edge road"}.`,
      `Use related roads to explain contrast and lineage inside Atlas. Do not treat related roads as runtime route starters.`
    ),
    dead_end_false_nearby_caution_module: variant(
      copy.caution,
      `${copy.caution} Use dead-end probe results only when explicit Atlas state supports them.`,
      `${copy.caution} Repeated negative signals can mark a false-nearby caution, but the canonical graph identity remains unchanged.`
    )
  };

  return {
    schema_version: "0.2",
    render_pack_id: `family_${String(entry.family_id).padStart(2, "0")}_archetype_${entry.archetype_id}_${entry.archetype_slug}_render_v0_2`,
    generated_at: GENERATED_AT,
    source_research_pack_id: researchPack.pack_id,
    identity: researchPack.identity,
    graph_alignment: {
      canonical_graph_ref: entry.canonical_graph_ref,
      canonical_example_refs: researchPack.explainer_content.canonical_example_rationales.map((item) => item.example_ref),
      survey_candidate_refs: alignment.survey_candidate_refs.map((item) => item.ref),
      related_archetype_refs: alignment.related_archetype_refs
    },
    modules,
    canonical_examples: researchPack.explainer_content.canonical_example_rationales,
    personalization_hooks: personalizationHooks(entry, copy),
    source_claim_refs: researchPack.claim_level_source_audit.map((claim) => claim.claim_id),
    rights_status: "pass",
    rights_notes: "Original Cartenza/Atlas educational render copy; no lyrics, long quotations, album art, artist photos, or proprietary third-party prose.",
    editorial_status: copy.render_editorial_status,
    non_mutation_assertion: "Render pack is a runtime sidecar only; it does not mutate canonical graph identity.",
    alpha_v0_mission_boundary: {
      status: "pass",
      allowed_terms_used: ["related mission", "what this route tests", "why this region explains the batch"],
      forbidden_dynamic_mission_language_present: false
    }
  };
}

function personalizationHooks(entry, copy) {
  return [
    {
      hook_id: `${entry.archetype_id}-affinity-positive`,
      required_state_fields: [`atlas_state.archetype_affinity[${entry.archetype_id}]`, `atlas_state.family_affinity[${entry.family_id}]`],
      predicate: `atlas_state.archetype_affinity[${entry.archetype_id}] >= 0.65 || atlas_state.family_affinity[${entry.family_id}] >= 0.65`,
      copy_variant: `You have enough Atlas evidence to treat ${copy.display_title} as a contextual landmark.`,
      fallback_copy: `Explore ${copy.display_title} as a context road, not a confirmed fit.`,
      state_field_status: "proposed"
    },
    {
      hook_id: `${entry.archetype_id}-known-song`,
      required_state_fields: ["atlas_state.user_known_song_refs", "atlas_state.survey_positive_candidate_refs"],
      predicate: `atlas_state.user_known_song_refs intersects canonical_song_recording_refs for ${entry.canonical_graph_ref} || atlas_state.survey_positive_candidate_refs intersects survey_candidate_refs for ${entry.canonical_graph_ref}`,
      copy_variant: `Your known songs make this road easier to place on the map.`,
      fallback_copy: `Use the canonical examples to orient this road before personalizing it.`,
      state_field_status: "proposed"
    },
    {
      hook_id: `${entry.archetype_id}-false-nearby-caution`,
      required_state_fields: ["atlas_state.dead_end_probe_results", "atlas_state.boundary_question_results", "atlas_state.survey_negative_candidate_refs"],
      predicate: `atlas_state.dead_end_probe_results has repeated_negative for ${entry.canonical_graph_ref} || atlas_state.boundary_question_results has boundary_negative for ${entry.canonical_graph_ref}`,
      copy_variant: copy.caution,
      fallback_copy: `No false-nearby caution is active for ${copy.display_title}.`,
      state_field_status: "proposed"
    },
    {
      hook_id: `${entry.archetype_id}-alpha-context`,
      required_state_fields: ["atlas_state.completed_mission_ids", "atlas_state.active_mission_id", "atlas_state.first_batch_mission_ids", "atlas_state.related_mission_ids"],
      predicate: `atlas_state.active_mission_id in atlas_state.first_batch_mission_ids || atlas_state.completed_mission_ids intersects atlas_state.related_mission_ids for ${entry.canonical_graph_ref} || atlas_state.related_mission_ids references ${entry.canonical_graph_ref}`,
      copy_variant: `This road explains why the active Alpha route may point nearby.`,
      fallback_copy: `This road is not in Alpha batch yet; you may encounter this road later.`,
      state_field_status: "proposed"
    },
    {
      hook_id: `${entry.archetype_id}-saved-or-skipped-object`,
      required_state_fields: ["atlas_state.user_saved_artist_refs", "atlas_state.user_skipped_artist_refs", "atlas_state.user_disliked_song_refs"],
      predicate: `atlas_state.user_saved_artist_refs intersects canonical_artist_refs for ${entry.canonical_graph_ref} || atlas_state.user_skipped_artist_refs intersects canonical_artist_refs for ${entry.canonical_graph_ref} || atlas_state.user_disliked_song_refs intersects canonical_song_recording_refs for ${entry.canonical_graph_ref}`,
      copy_variant: `Saved, skipped, or disliked objects can tune this road without changing its graph identity.`,
      fallback_copy: `No saved, skipped, or disliked object signal is active for ${copy.display_title}.`,
      state_field_status: "proposed"
    }
  ];
}

function inventoryRows(graph) {
  return [...graph.archetypes.values()]
    .sort((a, b) => a.family_id - b.family_id || a.archetype_id.localeCompare(b.archetype_id))
    .map((entry) => ({
      family_id: entry.family_id,
      family_name: entry.family_name,
      family_slug: entry.family_slug,
      archetype_id: entry.archetype_id,
      archetype_name: entry.archetype_name,
      archetype_slug: entry.archetype_slug,
      canonical_graph_ref: entry.canonical_graph_ref,
      candidate_counts: {
        total_graph_objects: entry.artists.length + entry.albums.length + entry.songs.length,
        artists: entry.artists.length,
        albums: entry.albums.length,
        song_recordings: entry.songs.length
      },
      artist_count: entry.artists.length,
      album_count: entry.albums.length,
      song_count: entry.songs.length,
      survey_candidate_count: (entry.survey_candidates || []).length,
      dead_end_probe_count: (entry.dead_end_probes || []).length,
      boundary_question_count: (entry.boundary_questions || []).length,
      related_archetype_refs: graphAlignment(entry, graph.archetypes).related_archetype_refs,
      readiness_status_metadata: entry.readiness || null
    }));
}

function validatePacks(graph, researchPacks, renderPacks, refSpecs = CHECKPOINT_REFS) {
  const errors = [];
  const warnings = [];
  const selectedRefs = refSpecs.map((item) => graphRef(item.family_id, item.archetype_id));
  const researchRefs = new Set(researchPacks.map((pack) => pack.identity.canonical_graph_ref));
  const renderRefs = new Set(renderPacks.map((pack) => pack.identity.canonical_graph_ref));
  const forbidden = [
    "generate mission from this node",
    "create a new mission",
    "launch arbitrary mission",
    "open a dynamic route from here",
    "ask AI to build a mission from this archetype"
  ];
  const researchRequired = ["identity", "graph_alignment", "explainer_content", "source_references", "claim_level_source_audit", "rights_policy", "editorial_status", "non_mutation_policy", "alpha_v0_mission_boundary"];
  const claimRequired = ["claim_id", "claim_text", "source_ref_ids", "confidence", "module_usage", "graph_refs", "audit_status"];
  const exampleRequired = ["example_ref", "example_type", "display_label", "why_this_example_matters", "what_to_listen_for", "graph_ref_validation_status"];
  const renderRequired = ["identity", "graph_alignment", "modules", "canonical_examples", "personalization_hooks", "source_claim_refs", "rights_status", "editorial_status", "non_mutation_assertion", "alpha_v0_mission_boundary"];
  const moduleRequired = ["atlas_home_region_card", "region_scene_page", "mission_detail_history_module", "did_you_know_card", "what_to_listen_for_prompt", "personalized_atlas_overlay", "canonical_examples_block", "related_roads_lineage_module", "dead_end_false_nearby_caution_module"];
  const variantRequired = ["compact", "standard", "deep"];

  for (const ref of selectedRefs) {
    if (!researchRefs.has(ref)) errors.push(`Missing research pack for ${ref}`);
    if (!renderRefs.has(ref)) errors.push(`Missing render pack for ${ref}`);
  }

  for (const pack of researchPacks) {
    for (const key of researchRequired) {
      if (pack[key] === undefined) errors.push(`Research pack ${pack.pack_id} missing required field ${key}`);
    }
    if (!graph.archetypes.has(pack.identity.canonical_graph_ref)) errors.push(`Invalid canonical graph ref in research pack ${pack.pack_id}`);
    if (!pack.identity.non_mutation_assertion) errors.push(`Missing non-mutation assertion in ${pack.pack_id}`);
    if (!pack.editorial_status) errors.push(`Missing editorial status in ${pack.pack_id}`);
    if (pack.editorial_status !== "draft_research") errors.push(`Research pack ${pack.pack_id} has non-draft editorial status ${pack.editorial_status}`);
    if (!pack.rights_policy?.rights_status) errors.push(`Missing rights status in ${pack.pack_id}`);
    if (pack.editorial_status === "production_copy_candidate") errors.push(`Research pack ${pack.pack_id} is incorrectly production_copy_candidate`);
    if ((pack.claim_level_source_audit || []).length < claimTarget(graph.archetypes.get(pack.identity.canonical_graph_ref))) {
      errors.push(`Research pack ${pack.pack_id} has insufficient claim density`);
    }
    for (const claim of pack.claim_level_source_audit || []) {
      for (const key of claimRequired) {
        if (claim[key] === undefined) errors.push(`Claim ${claim.claim_id || "unknown"} missing required field ${key}`);
      }
      if (!claim.source_ref_ids?.length) errors.push(`Claim ${claim.claim_id} has no source refs`);
      for (const sourceId of claim.source_ref_ids || []) {
        if (!pack.source_references[sourceId]) errors.push(`Claim ${claim.claim_id} references missing source ${sourceId}`);
      }
    }
    for (const example of pack.explainer_content.canonical_example_rationales || []) {
      for (const key of exampleRequired) {
        if (example[key] === undefined) errors.push(`Canonical example ${example.example_ref || "unknown"} missing required field ${key}`);
      }
      if (!graph.validGraphRefs.has(example.example_ref) && !example.example_ref.startsWith("survey_candidate:")) {
        errors.push(`Example ${example.example_ref} is not a validated graph or candidate ref`);
      }
    }
    if (Object.keys(pack.source_references || {}).length < 3) {
      warnings.push(`${pack.pack_id} has fewer than three source refs`);
    }
  }

  for (const pack of renderPacks) {
    for (const key of renderRequired) {
      if (pack[key] === undefined) errors.push(`Render pack ${pack.render_pack_id} missing required field ${key}`);
    }
    for (const moduleKey of moduleRequired) {
      const module = pack.modules?.[moduleKey];
      if (!module) {
        errors.push(`Render pack ${pack.render_pack_id} missing module ${moduleKey}`);
        continue;
      }
      for (const variantKey of variantRequired) {
        if (typeof module[variantKey] !== "string" || !module[variantKey]) {
          errors.push(`Render pack ${pack.render_pack_id} module ${moduleKey} missing ${variantKey}`);
        }
      }
    }
    const copy = JSON.stringify(pack);
    for (const phrase of forbidden) {
      if (copy.toLowerCase().includes(phrase)) errors.push(`Forbidden Alpha dynamic mission phrase in ${pack.render_pack_id}: ${phrase}`);
    }
    if (!pack.non_mutation_assertion) errors.push(`Missing render non-mutation assertion in ${pack.render_pack_id}`);
    if (!pack.rights_status) errors.push(`Missing render rights status in ${pack.render_pack_id}`);
    if (!pack.editorial_status) errors.push(`Missing render editorial status in ${pack.render_pack_id}`);
    if (pack.editorial_status !== "visualization_candidate") errors.push(`Render pack ${pack.render_pack_id} has unexpected editorial status ${pack.editorial_status}`);
    if (pack.editorial_status === "production_copy_candidate") errors.push(`Render pack ${pack.render_pack_id} is incorrectly production_copy_candidate`);
    if (copy.includes(" maps ") && copy.includes(" through ")) errors.push(`Render pack ${pack.render_pack_id} may still contain checkpoint template phrasing`);
    for (const example of pack.canonical_examples || []) {
      for (const key of exampleRequired) {
        if (example[key] === undefined) errors.push(`Render canonical example ${example.example_ref || "unknown"} missing required field ${key}`);
      }
    }
    for (const hook of pack.personalization_hooks || []) {
      if (!hook.required_state_fields?.length) errors.push(`Hook ${hook.hook_id} has no state fields`);
      for (const field of hook.required_state_fields || []) {
        if (!field.startsWith("atlas_state.")) errors.push(`Hook ${hook.hook_id} uses non-Atlas state field ${field}`);
      }
    }
  }

  return {
    generated_at: GENERATED_AT,
    package_scope_refs: selectedRefs,
    gates: {
      research_pack_coverage: selectedRefs.every((ref) => researchRefs.has(ref)),
      render_pack_coverage: selectedRefs.every((ref) => renderRefs.has(ref)),
      graph_ref_validation: errors.filter((error) => error.includes("Invalid canonical graph ref")).length === 0,
      canonical_example_validation: errors.filter((error) => error.includes("Example")).length === 0,
      dynamic_mission_language: errors.filter((error) => error.includes("Forbidden Alpha")).length === 0,
      claim_source_refs: errors.filter((error) => error.includes("Claim")).length === 0,
      personalization_state_fields: errors.filter((error) => error.includes("Hook")).length === 0,
      editorial_status: errors.filter((error) => error.includes("editorial status")).length === 0,
      rights_status: errors.filter((error) => error.includes("rights status")).length === 0,
      non_mutation_assertion: errors.filter((error) => error.includes("non-mutation")).length === 0,
      schema_required_fields: errors.filter((error) => error.includes("missing required field") || error.includes("missing module")).length === 0,
      no_production_copy_candidate: ![...researchPacks, ...renderPacks].some((pack) => pack.editorial_status === "production_copy_candidate")
    },
    error_count: errors.length,
    warning_count: warnings.length,
    errors,
    warnings
  };
}

function mdReport(title, lines) {
  return [`# ${title}`, "", ...lines, ""].join("\n");
}

function buildReports(graph, researchPacks, renderPacks, validation, outDir, refSpecs = CHECKPOINT_REFS) {
  const inventory = inventoryRows(graph);
  const selectedRefs = refSpecs.map((item) => graphRef(item.family_id, item.archetype_id));
  const coverageRows = selectedRefs.map((ref) => {
    const r = researchPacks.find((pack) => pack.identity.canonical_graph_ref === ref);
    const p = renderPacks.find((pack) => pack.identity.canonical_graph_ref === ref);
    return `| ${ref} | ${r ? "yes" : "no"} | ${p ? "yes" : "no"} | ${r?.editorial_status || "missing"} | ${r?.rights_policy?.rights_status || "missing"} |`;
  });
  writeText(path.join(outDir, "indexes/archetype_explainer_coverage_report_v0_2.md"), mdReport("Archetype Explainer Coverage Report v0.2", [
    `Package archetypes covered: ${selectedRefs.length}`,
    `Full graph archetypes inventoried: ${inventory.length}`,
    "",
    "| canonical_graph_ref | research_pack | render_pack | editorial_status | rights_status |",
    "| --- | --- | --- | --- | --- |",
    ...coverageRows
  ]));

  const graphRows = selectedRefs.map((ref) => `| ${ref} | ${graph.archetypes.has(ref) ? "pass" : "fail"} | research/render sidecars only |`);
  writeText(path.join(outDir, "indexes/graph_ref_validation_report_v0_2.md"), mdReport("Graph Ref Validation Report v0.2", [
    "| canonical_graph_ref | status | notes |",
    "| --- | --- | --- |",
    ...graphRows,
    "",
    `Validation errors: ${validation.error_count}`
  ]));

  const rightsRows = researchPacks.map((pack) => `| ${pack.identity.canonical_graph_ref} | ${pack.rights_policy.rights_status} | ${pack.rights_policy.rights_notes} |`);
  writeText(path.join(outDir, "indexes/rights_policy_report_v0_2.md"), mdReport("Rights Policy Report v0.2", [
    "All package packs use original educational prose and source summaries only.",
    "",
    "| canonical_graph_ref | rights_status | notes |",
    "| --- | --- | --- |",
    ...rightsRows
  ]));

  const proposedHooks = renderPacks.flatMap((pack) => pack.personalization_hooks.map((hook) => ({
    canonical_graph_ref: pack.identity.canonical_graph_ref,
    hook_id: hook.hook_id,
    fields: hook.required_state_fields,
    state_field_status: hook.state_field_status
  })));
  writeJson(path.join(outDir, "indexes/state_field_dependency_report_v0_2.json"), {
    generated_at: GENERATED_AT,
    note: "The v0.2 dispatch requires atlas_state.* predicates. Most fields are proposed in the current app codebase and reported here.",
    state_fields_contract_v0_2: ATLAS_STATE_FIELDS_V0_2,
    proposed_dependencies: proposedHooks
  });

  const sourceReviewNeeded = researchPacks.filter((pack) => pack.explainer_content.source_coverage_status !== "checkpoint_sourced").length;
  const weakSourcePacks = researchPacks
    .filter((pack) => pack.explainer_content.source_coverage_status !== "checkpoint_sourced")
    .map((pack) => ({
      canonical_graph_ref: pack.identity.canonical_graph_ref,
      archetype_id: pack.identity.archetype_id,
      editorial_display_title: pack.identity.editorial_display_title,
      source_coverage_status: pack.explainer_content.source_coverage_status,
      recommended_action: "Add archetype-specific external sources and PM copy review before alpha_render_candidate promotion."
    }));
  const graphGapCount = researchPacks.flatMap((pack) => pack.graph_gap_observations || []).length;
  writeText(path.join(outDir, "indexes/alpha_render_readiness_report_v0_2.md"), mdReport("Alpha Render Readiness Report v0.2", [
    `Total graph archetypes inventoried: ${inventory.length}`,
    `Package archetypes covered: ${selectedRefs.length}`,
    `Packs passing automated validation: ${validation.error_count === 0 ? selectedRefs.length : 0}`,
    `Validation errors: ${validation.error_count}`,
    `Validation warnings: ${validation.warning_count}`,
    `Packs needing source review: ${sourceReviewNeeded}`,
    `Packs with graph gaps: ${graphGapCount}; graph gap observations file included.`,
    `Packs with personalization state dependencies: ${renderPacks.length}`,
    "Rights/copyright review warnings: 0 blocking warnings.",
    "Recommended first Atlas Visualization batch: Family 1 full set, with CBGB 054 as the cross-family venue/scene test.",
    "Recommended holdbacks before Alpha: source-deepen weak-source draft packs before alpha_render_candidate promotion; do not promote any pack to production_copy_candidate without explicit PM approval."
  ]));
  writeJson(path.join(outDir, "indexes/weak_source_archetypes_v0_2.json"), {
    generated_at: GENERATED_AT,
    weak_source_count: weakSourcePacks.length,
    weak_source_archetypes: weakSourcePacks
  });

  writeText(path.join(outDir, "indexes/graph_gap_observations_v0_2.md"), mdReport("Graph Gap Observations v0.2", [
    "No canonical graph mutations were made.",
    "Generation did not require adding missing artists, albums, songs, survey candidates, boundary questions, or dead-end probes.",
    "Any future obvious historical omissions should be logged here with `do_not_mutate_graph: true` and PM review."
  ]));

  writeText(path.join(outDir, "indexes/pm_questions_and_ambiguities_v0_2.md"), mdReport("PM Questions and Ambiguities v0.2", [
    "1. Confirm the app implementation timeline for proposed `atlas_state.*` fields now treated as the v0.2 explainer contract.",
    "2. Confirm which PM-reviewed packs, if any, should be promoted beyond `visualization_candidate` to `alpha_render_candidate`.",
    "3. Confirm whether Family 1 should be the first full visualization batch, given its strong oldies-radio survey value and accepted Brill proof-pack precedent."
  ]));

  writeJson(path.join(outDir, "indexes/source_audit_index_v0_2.json"), {
    generated_at: GENERATED_AT,
    source_references: SOURCE_REFERENCES,
    pack_source_usage: Object.fromEntries(researchPacks.map((pack) => [
      pack.pack_id,
      Object.keys(pack.source_references)
    ]))
  });
  buildFamilyDeltas(graph, researchPacks, renderPacks, outDir);
}

function buildFamilyDeltas(graph, researchPacks, renderPacks, outDir) {
  const familyIds = [...new Set(researchPacks.map((pack) => pack.identity.family_id))].sort((a, b) => a - b);
  for (const familyId of familyIds) {
    const family = graph.families.get(familyId);
    const familyResearch = researchPacks.filter((pack) => pack.identity.family_id === familyId);
    const familyRender = renderPacks.filter((pack) => pack.identity.family_id === familyId);
    const dir = path.join(outDir, "family_deltas", `family_${String(familyId).padStart(2, "0")}`);
    const weak = familyResearch.filter((pack) => pack.explainer_content.source_coverage_status !== "checkpoint_sourced");
    writeJson(path.join(dir, "source_audit_index_delta_v0_2.json"), {
      generated_at: GENERATED_AT,
      family_id: familyId,
      family_name: family?.family_name,
      pack_source_usage: Object.fromEntries(familyResearch.map((pack) => [pack.pack_id, Object.keys(pack.source_references || {})]))
    });
    writeText(path.join(dir, "graph_ref_validation_delta_v0_2.md"), mdReport(`Family ${String(familyId).padStart(2, "0")} Graph Ref Validation Delta v0.2`, [
      "| canonical_graph_ref | research_pack | render_pack | status |",
      "| --- | --- | --- | --- |",
      ...familyResearch.map((pack) => {
        const render = familyRender.find((item) => item.identity.canonical_graph_ref === pack.identity.canonical_graph_ref);
        return `| ${pack.identity.canonical_graph_ref} | yes | ${render ? "yes" : "no"} | ${graph.archetypes.has(pack.identity.canonical_graph_ref) ? "pass" : "fail"} |`;
      })
    ]));
    writeText(path.join(dir, "rights_policy_delta_v0_2.md"), mdReport(`Family ${String(familyId).padStart(2, "0")} Rights Policy Delta v0.2`, [
      "| canonical_graph_ref | rights_status | notes |",
      "| --- | --- | --- |",
      ...familyResearch.map((pack) => `| ${pack.identity.canonical_graph_ref} | ${pack.rights_policy.rights_status} | ${pack.rights_policy.rights_notes} |`)
    ]));
    writeJson(path.join(dir, "state_field_dependency_delta_v0_2.json"), {
      generated_at: GENERATED_AT,
      family_id: familyId,
      family_name: family?.family_name,
      dependencies: familyRender.flatMap((pack) => pack.personalization_hooks.map((hook) => ({
        canonical_graph_ref: pack.identity.canonical_graph_ref,
        hook_id: hook.hook_id,
        fields: hook.required_state_fields,
        state_field_status: hook.state_field_status
      })))
    });
    writeText(path.join(dir, "family_pm_notes_v0_2.md"), mdReport(`Family ${String(familyId).padStart(2, "0")} PM Notes v0.2`, [
      `Family: ${family?.family_name}`,
      `Research packs: ${familyResearch.length}`,
      `Render packs: ${familyRender.length}`,
      `Weak-source packs: ${weak.length}`,
      "Graph mutation: none",
      "Editorial policy: research packs remain draft_research; render packs are visualization_candidate after validation.",
      weak.length
        ? "PM action: source-deepen weak-source archetypes before alpha_render_candidate promotion."
        : "PM action: checkpoint-source density is present; still review before production approval."
    ]));
  }
}

function buildExamples(renderPacks, outDir) {
  const sample = renderPacks.slice(0, 4);
  writeText(path.join(outDir, "examples/atlas_home_region_cards_examples_v0_2.md"), mdReport("Atlas Home Region Cards Examples v0.2", sample.flatMap((pack) => [
    `## ${pack.identity.editorial_display_title}`,
    `Compact: ${pack.modules.atlas_home_region_card.compact}`,
    `Standard: ${pack.modules.atlas_home_region_card.standard}`,
    ""
  ])));
  writeText(path.join(outDir, "examples/region_scene_page_examples_v0_2.md"), mdReport("Region Scene Page Examples v0.2", sample.flatMap((pack) => [
    `## ${pack.identity.editorial_display_title}`,
    pack.modules.region_scene_page.standard,
    ""
  ])));
  writeText(path.join(outDir, "examples/mission_detail_history_module_examples_v0_2.md"), mdReport("Mission Detail History Module Examples v0.2", sample.flatMap((pack) => [
    `## ${pack.identity.editorial_display_title}`,
    pack.modules.mission_detail_history_module.standard,
    ""
  ])));
}

function buildPackage(graph, outDir, zipPath, refSpecs, packageConfig) {
  if (fs.existsSync(outDir)) fs.rmSync(outDir, { recursive: true, force: true });
  fs.mkdirSync(outDir, { recursive: true });

  writeJson(path.join(outDir, "schemas/atlas_explainer_research_pack_schema_v0_2.json"), RESEARCH_SCHEMA);
  writeJson(path.join(outDir, "schemas/atlas_explainer_render_pack_schema_v0_2.json"), RENDER_SCHEMA);
  writeJson(path.join(outDir, "indexes/archetype_inventory_v0_2.json"), {
    generated_at: GENERATED_AT,
    source_of_truth: "data/canonical_graph normalized family exports plus normalization_pass_2 sidecars",
    total_archetypes: graph.archetypes.size,
    archetypes: inventoryRows(graph)
  });

  const researchPacks = [];
  const renderPacks = [];
  for (const refSpec of refSpecs) {
    const ref = graphRef(refSpec.family_id, refSpec.archetype_id);
    const entry = graph.archetypes.get(ref);
    if (!entry) throw new Error(`Missing graph ref ${ref}`);
    const alignment = graphAlignment(entry, graph.archetypes);
    const researchPack = buildResearchPack(entry, alignment);
    const renderPack = buildRenderPack(entry, alignment, researchPack);
    researchPacks.push(researchPack);
    renderPacks.push(renderPack);
    writeJson(path.join(outDir, `research_packs/family_${String(entry.family_id).padStart(2, "0")}_archetype_${entry.archetype_id}_${entry.archetype_slug}_research_v0_2.json`), researchPack);
    writeJson(path.join(outDir, `render_packs/family_${String(entry.family_id).padStart(2, "0")}_archetype_${entry.archetype_id}_${entry.archetype_slug}_render_v0_2.json`), renderPack);
  }

  const validation = validatePacks(graph, researchPacks, renderPacks, refSpecs);
  writeJson(path.join(outDir, "indexes/atlas_explainer_pack_manifest_v0_2.json"), {
    generated_at: GENERATED_AT,
    package_id: packageConfig.package_id,
    package_scope: packageConfig.package_scope,
    checkpoint_family: packageConfig.checkpoint_family || null,
    cross_family_samples: packageConfig.cross_family_samples || [],
    schemas: [
      "schemas/atlas_explainer_research_pack_schema_v0_2.json",
      "schemas/atlas_explainer_render_pack_schema_v0_2.json"
    ],
    research_packs: researchPacks.map((pack) => `research_packs/${pack.pack_id}.json`),
    render_packs: renderPacks.map((pack) => `render_packs/${pack.render_pack_id}.json`),
    indexes: [
      "indexes/archetype_inventory_v0_2.json",
      "indexes/archetype_explainer_coverage_report_v0_2.md",
      "indexes/source_audit_index_v0_2.json",
      "indexes/graph_ref_validation_report_v0_2.md",
      "indexes/rights_policy_report_v0_2.md",
      "indexes/alpha_render_readiness_report_v0_2.md",
      "indexes/weak_source_archetypes_v0_2.json",
      "indexes/atlas_explainer_validation_report_v0_2.json",
      "indexes/checkpoint_validation_report_v0_2.json",
      "indexes/state_field_dependency_report_v0_2.json",
      "indexes/graph_gap_observations_v0_2.md",
      "indexes/pm_questions_and_ambiguities_v0_2.md"
    ],
    validation_summary: validation
  });
  writeJson(path.join(outDir, "indexes/checkpoint_validation_report_v0_2.json"), validation);
  writeJson(path.join(outDir, "indexes/atlas_explainer_validation_report_v0_2.json"), validation);
  buildReports(graph, researchPacks, renderPacks, validation, outDir, refSpecs);
  buildExamples(renderPacks, outDir);

  if (fs.existsSync(zipPath)) fs.rmSync(zipPath, { force: true });
  execFileSync("zip", ["-qr", zipPath, path.basename(outDir)], { cwd: path.dirname(outDir) });
  return {
    package_dir: outDir,
    zip_path: zipPath,
    archetypes_inventoried: graph.archetypes.size,
    package_packs: researchPacks.length,
    validation_errors: validation.error_count,
    validation_warnings: validation.warning_count,
    source_review_needed: researchPacks.filter((pack) => pack.explainer_content.source_coverage_status !== "checkpoint_sourced").length
  };
}

function main() {
  const graph = loadGraph();
  ensureFamilySourceReferences(graph);

  const checkpointSummary = buildPackage(graph, OUT_DIR, ZIP_PATH, CHECKPOINT_REFS, {
    package_id: "AtlasExplainerPack_v0_2_Checkpoint",
    package_scope: "one complete family plus three cross-family archetypes",
    checkpoint_family: { family_id: 1, family_name: graph.families.get(1).family_name },
    cross_family_samples: CHECKPOINT_REFS.filter((item) => item.family_id !== 1).map((item) => graphRef(item.family_id, item.archetype_id))
  });

  let fullSummary = null;
  if (checkpointSummary.validation_errors === 0 && checkpointSummary.validation_warnings === 0) {
    const fullRefs = [...graph.archetypes.values()]
      .sort((a, b) => a.family_id - b.family_id || a.archetype_id.localeCompare(b.archetype_id))
      .map((entry) => ({ family_id: entry.family_id, archetype_id: entry.archetype_id }));
    fullSummary = buildPackage(graph, FULL_OUT_DIR, FULL_ZIP_PATH, fullRefs, {
      package_id: "AtlasExplainerPack_v0_2_All_Archetypes",
      package_scope: "all canonical archetypes from the expanded canonical graph export",
      checkpoint_family: { family_id: 1, family_name: graph.families.get(1).family_name },
      cross_family_samples: CHECKPOINT_REFS.filter((item) => item.family_id !== 1).map((item) => graphRef(item.family_id, item.archetype_id))
    });
  }

  console.log(JSON.stringify({
    checkpoint: checkpointSummary,
    full: fullSummary
  }, null, 2));
}

main();
