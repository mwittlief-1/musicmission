# Waymark App/Local Candidate Pool Contract Alpha v0

Version: `alpha_v0`

Frozen on: 2026-05-21

Status: `APPROVED_FOR_LOCAL_FIRST_MISSION_GENERATION_WITH_GUARDRAILS`

Artifact path:

```text
data/product_contracts/app_local_candidate_pool_contract_alpha_v0.md
```

Alpha consumable-layer companion artifacts:

```text
data/alpha_consumable_layer/alpha_v0/alpha_graph_surface_manifest.json
data/alpha_consumable_layer/alpha_v0/alpha_graph_surface_manifest.md
data/alpha_consumable_layer/alpha_v0/alpha_candidate_blocklist_alpha_v0.json
data/alpha_consumable_layer/alpha_v0/atlas_music_object_ref_alpha_v0.schema.json
data/alpha_consumable_layer/alpha_v0/graph_to_atlas_music_object_ref_alpha_v0.md
data/alpha_consumable_layer/alpha_v0/atlas_music_object_ref_examples_alpha_v0.json
data/alpha_consumable_layer/alpha_v0/candidate_role_risk_vocabulary_alpha_v0.json
data/alpha_consumable_layer/alpha_v0/resolver_version_policy_sidecar_alpha_v0.json
data/alpha_consumable_layer/alpha_v0/tile_log_metadata_contract_alpha_v0.json
data/alpha_consumable_layer/alpha_v0/alpha_consumable_layer_guardrails_alpha_v0.md
data/alpha_consumable_layer/alpha_v0/alpha1_fixed_survey_intake_graph_support_alpha_v0.json
data/alpha_consumable_layer/alpha_v0/alpha1_fixed_survey_intake_graph_support_alpha_v0.md
data/alpha_consumable_layer/alpha_v0/alpha1_first_mission_handoff_graph_contract_alpha_v0.json
data/alpha_consumable_layer/alpha_v0/alpha1_first_mission_handoff_graph_contract_alpha_v0.md
data/alpha_consumable_layer/alpha_v0/alpha1_user_facing_graph_language_guardrails_alpha_v0.md
data/alpha_consumable_layer/alpha_v0/alpha_route_identity_contract_alpha_v0.json
data/alpha_consumable_layer/alpha_v0/alpha_route_identity_contract_alpha_v0.md
data/alpha_consumable_layer/alpha_v0/canonical_mission_item_universe_alpha_v0.json
data/alpha_consumable_layer/alpha_v0/canonical_mission_item_universe_alpha_v0.md
data/alpha_consumable_layer/alpha_v0/apple_music_unmatched_do_not_use_alpha_v0.json
data/alpha_consumable_layer/alpha_v0/apple_music_unmatched_do_not_use_alpha_v0.md
```

This contract freezes the app/local candidate pool boundary for first mission generation in trusted Alpha. It does not approve raw canonical graph use, full canonical import, hard lock, or unguarded Atlas promotion.

## 1. Contract Purpose

The app/local candidate pool is the safe handoff layer between:

```text
Survey evidence + repaired canonical graph candidate surfaces
-> first mission generation
-> mission review / provisional Atlas evidence
```

Its job is to give first mission generation enough concrete music objects, roles, reasons, and guardrails to build credible listening missions without leaking unsafe graph rows, hidden simulation data, unresolved version risk, or premature Atlas truth.

The candidate pool is not the canonical graph. It is not the Atlas. It is not a final recommendation engine. It is an Alpha-safe packet of eligible candidates and constraints.

Current mission-item rule:

```text
the full canonical grid is available as mission material.
the compact pool is a sample/slice for handoff tests, not the universe.
playback route items must require an Apple Music catalog ID for each playable track.
any canonical grid item with an Apple Music catalog ID is eligible for Survey consideration unless blocklisted.
artist-level candidates may inform context, but must not become pseudo-playable route items.
album candidates are held as graph/reference context unless a future album-route contract explicitly enables them.
```

The playback-ready `alpha_v0` sample now resolves `MGN-I004` by exporting `track` candidates with credited artist, Apple Music catalog IDs, MusicKit search hints, candidate role, risk class, review status, and reference-safe `music_object_ref` values. It does not cap the canonical mission universe.

Survey availability rule:

```text
canonical graph + Apple Music catalog ID = available for Survey consideration
```

The curated `survey_*_candidates_v0_2.json` files are approved/default Alpha surfaces. They are not the outer limit of what Survey may draw from when a canonical graph item has an Apple ID and is not blocklisted.

Live generation recovery route identity rule:

```text
Mission route items must copy candidate_id from the supplied candidate pool.
Mission route item_id should copy app_route_item_id.
route_candidate_key and route_batch_dedupe_key are the preferred non-display duplicate/batch-repeat keys.
Digest regions, Survey-visible tiles, Atlas hints, Apple exposure, and model memory may explain selection but must not create non-candidate route items.
```

## Alpha 1 First-Run Intake Alignment

Product has approved the Alpha 1 first-run Survey shape:

```text
4 artist screens
2 album screens
4 song screens
12 tiles per screen
```

The graph lane supports that fixed intake through:

```text
data/alpha_consumable_layer/alpha_v0/alpha1_fixed_survey_intake_graph_support_alpha_v0.json
data/alpha_consumable_layer/alpha_v0/alpha1_fixed_survey_intake_graph_support_alpha_v0.md
```

The graph contract version remains `alpha_v0`. This is an Alpha 1 alignment layer over the already frozen surfaces, not a hard-lock of the canonical database.

## 2. Source Artifacts Allowed

The local first-mission candidate pool may be built only from these repaired Normalization Pass 2 files:

```text
data/canonical_graph/normalization_pass_2/survey_artist_candidates_v0_2.json
data/canonical_graph/normalization_pass_2/survey_album_candidates_v0_2.json
data/canonical_graph/normalization_pass_2/survey_song_candidates_v0_2.json
data/canonical_graph/normalization_pass_2/family_survey_readiness_v0_2.json
data/canonical_graph/normalization_pass_2/archetype_readiness_v0_2.json
data/canonical_graph/normalization_pass_2/canonical_quarantine_queue.json
data/canonical_graph/normalization_pass_2/canonical_recording_versions.json
data/canonical_graph/normalization_pass_2/dead_end_probe_candidates_v0_2.json
data/canonical_graph/normalization_pass_2/boundary_question_bank_v0_2.json
MusicAtlasController/Resources/canonical_apple_music_catalog_index_v1.json
```

Do not build the local first-mission pool directly from:

- raw family rows
- raw canonical entity tables
- raw Apple Music payloads
- merge review queues
- composition review queues
- suppressed/quarantined buckets
- hidden simulation truth

## 2A. Apple Music ID Gate

Canonical songs may remain in the graph even when they do not yet have an Apple Music catalog ID. For Alpha app playback and playback-route selection, those rows are `do_not_use_no_apple_id`.

The canonical mission universe is:

```text
data/alpha_consumable_layer/alpha_v0/canonical_mission_item_universe_alpha_v0.json
```

The derived queue is:

```text
data/alpha_consumable_layer/alpha_v0/apple_music_unmatched_do_not_use_alpha_v0.json
```

Rows in that queue must not feed:

- Survey display
- playback route selection
- Supabase active candidate import
- OpenAI prompt payloads
- app playback
- Apple Music auto-resolution

Manual resolver work may clear the status by adding a verified Apple Music catalog entry to:

```text
MusicAtlasController/Resources/canonical_apple_music_catalog_index_v1.json
```

## 3. Included Families

First mission generation may use candidates from `survey_ready` families only.

Included families:

| family_id | family_name | Alpha use |
| --- | --- | --- |
| 1 | Early Rock, Oldies, Doo-Wop, Pre-Beatles Pop | eligible |
| 2 | Beatles, British Invasion, 60s Pop-Rock | eligible |
| 3 | Classic Rock, Album Rock, Progressive Rock | eligible |
| 4 | Singer-Songwriter, Folk, Americana, Adult Songcraft | eligible |
| 5 | Country | eligible |
| 6 | Soul, Funk, Disco, R&B Foundations | eligible |
| 7 | Hip-Hop | eligible |
| 8 | Punk, Hardcore, Post-Punk, New Wave | eligible |
| 9 | Metal and Heavy Music | eligible |
| 10 | Alternative, Indie, Grunge, Emo | eligible |
| 11 | Electronic, Dance, Club, Industrial, Experimental Pop | eligible with MusicKit/version caution |
| 12 | Pop Monoculture and Persona Pop | eligible |
| 13 | Latin, Caribbean, Global Pop | eligible with language/remix/collaboration caution |
| 14 | Jazz, Standards, Vocal, Classical-Adjacent | eligible with work/recording caution |
| 16 | Christian, Worship, Gospel | eligible with worship-standard/church-brand caution |
| 18 | Modern Rock, Current Discovery, Internet-Native Scenes | eligible |

Excluded from default first mission generation:

| family_id | family_name | Reason |
| --- | --- | --- |
| 15 | Soundtrack, Theater, Musicals, Family Context | `context_only`; special entity handling not safe for default first missions |
| 17 | Nostalgia, Novelty, Context, Shared Listening | `context_only`; use-case/context lane, not default taste-canon lane |

Family 15 or 17 may appear only in a deliberately scoped concierge/context mission and must not be included in automatic first mission generation.

## 4. Included Archetypes

### Anchor-Eligible Archetypes

An archetype is anchor-eligible for Alpha first mission generation when:

```text
readiness == survey_ready
fast_survey_allowed == true
```

As of `alpha_v0`, that includes 100 archetypes:

| archetype_id | family_id | archetype_name |
| --- | --- | --- |
| 001 | 1 | Early Rock & Roll Foundations |
| 002 | 1 | Rockabilly / Primitive Guitar / Proto-Garage |
| 003 | 1 | Doo-Wop / Vocal Group Oldies |
| 004 | 1 | Teen Idol / Early Pop-Rock Radio |
| 005 | 1 | Brill Building / Girl Group / Early 60s Pop Craft |
| 006 | 1 | Early Soul-Pop / R&B Crossover |
| 007 | 1 | Surf / Instrumental / Early Guitar Pop |
| 008 | 2 | British Invasion / Core UK Beat Groups |
| 010 | 2 | Folk-Rock / Harmony Pop / 60s Songcraft |
| 012 | 2 | Baroque Pop / Chamber Pop / Artful 60s Pop |
| 013 | 2 | Psychedelic Pop / Sunshine Pop / Late-60s Pop-Rock |
| 014 | 2 | Heavy Psych / Blues-Rock / Acid Rock |
| 016 | 3 | Classic Rock / Album-Rock Spine |
| 017 | 3 | Hard Rock / Riff Rock / Proto-Metal |
| 018 | 3 | Progressive Rock / Art-Prog Canon |
| 019 | 3 | Southern Rock / Roots Jam Rock |
| 020 | 3 | Glam Rock / Theatrical Seventies Rock |
| 022 | 3 | Soft Rock / AM Gold / Adult Pop |
| 023 | 3 | Yacht Rock / Smooth Studio Pop |
| 024 | 4 | Classic singer-songwriter |
| 025 | 4 | Piano pop and adult songcraft |
| 026 | 4 | Folk revival and protest folk |
| 027 | 4 | Country-folk and Americana roots |
| 029 | 4 | Adult alternative and coffeehouse songcraft |
| 030 | 4 | Modern indie folk and folk-pop |
| 031 | 5 | Classic Country / Honky-Tonk / Nashville Foundations |
| 032 | 5 | Outlaw Country / Cosmic Country |
| 033 | 5 | Country-Pop / Crossover Country |
| 034 | 5 | 90s Country Radio / Hat Acts / New Traditionalists |
| 035 | 5 | Modern Country Radio / Bro-Country / Arena Country |
| 037 | 6 | Motown / Detroit Soul Pop |
| 038 | 6 | Southern Soul / Stax / Muscle Shoals |
| 039 | 6 | Funk / Psychedelic Soul / Groove Canon |
| 040 | 6 | Disco / Dancefloor 70s |
| 041 | 6 | Quiet Storm / Smooth R&B / Adult Soul |
| 042 | 6 | New Jack Swing / 80s-90s R&B Pop |
| 043 | 6 | Neo-Soul / Conscious R&B |
| 044 | 6 | Modern R&B / Alt-R&B / Bedroom R&B |
| 045 | 7 | Old-School Hip-Hop / Electro-Rap Foundations |
| 046 | 7 | Golden Age Hip-Hop / Conscious / Native Tongues |
| 047 | 7 | Gangsta Rap / West Coast / G-Funk |
| 048 | 7 | East Coast 90s / Boom Bap / Street Canon |
| 049 | 7 | Southern Hip-Hop / Crunk / Trap Foundations |
| 050 | 7 | Pop-Rap / Mainstream Hip-Hop Crossover |
| 051 | 7 | Alternative / Experimental / Indie Rap |
| 052 | 7 | Modern Trap / Streaming-Era Rap |
| 053 | 8 | First-Wave Punk / 70s Punk |
| 054 | 8 | CBGB / Art-Punk / Downtown New York |
| 056 | 8 | Post-Punk / Dark Melodic / Gothic Roots |
| 057 | 8 | New Wave / MTV Pop-Rock |
| 058 | 8 | Synthpop / New Romantic / 80s Electronic Pop |
| 059 | 8 | College Rock / Pre-Alternative 80s |
| 061 | 9 | Traditional Heavy Metal / NWOBHM |
| 062 | 9 | Thrash Metal / Speed Metal |
| 063 | 9 | Glam Metal / Hair Metal / Pop Metal |
| 064 | 9 | Doom / Stoner / Desert Heavy |
| 065 | 9 | Industrial Metal / Machine Rock |
| 066 | 9 | Alt-Metal / Nu-Metal / Rap-Metal |
| 067 | 9 | Metalcore / Emo-Heavy / Modern Active Rock |
| 068 | 9 | Extreme Metal Gateway / Black-Death-Sludge |
| 069 | 10 | 1980s Alternative Source-Code / Pre-Grunge |
| 071 | 10 | Post-Grunge / Modern Rock Radio |
| 072 | 10 | 90s Indie / Lo-Fi / Slacker / Matador Axis |
| 073 | 10 | Shoegaze / Dream Pop / Noise Haze |
| 074 | 10 | Female 90s Alt / Riot Grrrl / Guitar Voices |
| 075 | 10 | Power-Pop Revival / Crunchy Alt-Pop |
| 076 | 10 | Pop-Punk / Skate Punk / 90s-00s Punk Pop |
| 077 | 10 | Emo / Mall Emo / Post-Hardcore Pop |
| 078 | 10 | Blog Indie / Prestige Indie / 2000s Indie Rock |
| 079 | 10 | Garage Revival / Rock-Is-Back 2000s |
| 080 | 10 | Post-Punk Revival / Dark Indie Rock |
| 081 | 11 | House / Chicago / Dance Club Foundations |
| 083 | 11 | EDM / Festival Dance / Big Room / Mainstream Electronic |
| 084 | 11 | Trip-Hop / Downtempo / Nocturnal Electronic |
| 087 | 11 | Experimental Electronic / IDM / Art-Electronic |
| 088 | 12 | 70s-80s Pop Sovereigns |
| 089 | 12 | 90s Pop / Teen Pop / TRL Monoculture |
| 090 | 12 | 2000s Pop / Dance-Pop / Club-Pop |
| 091 | 12 | 2010s Persona Pop / Architectural Pop |
| 092 | 12 | Adult Pop / TV-Drama Anthem / Inspirational Pop |
| 093 | 12 | TikTok / Streaming-Era Pop / Internet Pop |
| 094 | 13 | Reggaeton / Urbano / Latin Pop Crossover |
| 095 | 13 | Regional Mexican / Corridos / Musica Mexicana |
| 096 | 13 | Salsa / Latin Dance / Tropical Pop |
| 097 | 13 | Afrobeats / African Pop Crossover |
| 098 | 13 | K-Pop / J-Pop / Asian Pop Crossover |
| 099 | 13 | Global Folk / World Fusion / Diaspora Roots |
| 100 | 14 | Vocal Standards / Crooners / Great American Songbook |
| 101 | 14 | Jazz Foundations / Bebop / Hard Bop Gateway |
| 102 | 14 | Smooth Jazz / Jazz-Pop / Adult Instrumental |
| 103 | 14 | Classical Crossover / Instrumental Popular Canon |
| 108 | 16 | Black Gospel / Gospel Soul |
| 109 | 16 | CCM / Christian Pop-Rock / Worship Radio |
| 110 | 16 | Worship / Praise / Church Songbook |
| 115 | 18 | Current Rock Revival / Post-Punk New Wave 2020s |
| 116 | 18 | Modern Indie Singer-Songwriter / Sad-Prestige Indie |
| 117 | 18 | Modern Psych / Groove Indie / Tame-MGMT-Arctic Axis |
| 118 | 18 | Heavy Modern Alternative / Active Rock Survival |
| 119 | 18 | Hyperpop / Synthetic Edge-Pop / Internet Maximalism |
| 120 | 18 | Algorithmic Mood / Lo-Fi / Chill / Study Music |

### Conditional Probe Archetypes

These archetypes are not anchor-eligible. They may be used only as triggered probes, bridges, boundaries, or deepening candidates when an approved candidate row exists and the mission has a clear reason to test that edge:

| archetype_id | family_id | readiness | archetype_name |
| --- | --- | --- | --- |
| 011 | 2 | adaptive_only | Garage Rock / Nuggets / Proto-Punk Singles |
| 015 | 2 | adaptive_only | Art-Rock / Proto-Alternative / Freak Underground |
| 021 | 3 | adaptive_only | Power Pop / Melodic Guitar Pop |
| 028 | 4 | adaptive_only | Alt-country and No Depression |
| 036 | 5 | adaptive_only | Red Dirt / Americana Country / Texas Country |
| 055 | 8 | adaptive_only | Hardcore Punk / US 80s Hardcore |
| 060 | 8 | adaptive_only | Noise Rock / Post-Hardcore / Touch and Go Axis |
| 070 | 10 | adaptive_only | Grunge / Seattle / 90s Alt Center |
| 082 | 11 | adaptive_only | Techno / Detroit / Minimal Electronic |
| 085 | 11 | adaptive_only | Indie Dance / Dance-Punk / Electroclash |
| 086 | 11 | adaptive_only | Synthwave / Chillwave / Bedroom Electronic |
| 009 | 2 | deep_only | Jangle Pop / Folk-Rock Precursor |

Conditional probe archetypes must not be used as first mission anchors unless a Product Owner explicitly approves a focused mission.

### Excluded Context Archetypes

These are excluded from automatic first mission generation:

| archetype_id | family_id | readiness | archetype_name |
| --- | --- | --- | --- |
| 104 | 15 | context_only | Broadway / Modern Musical Theater |
| 105 | 15 | context_only | Disney / Family Soundtrack / Animated Musical Canon |
| 106 | 15 | context_only | Movie Soundtracks / 80s-90s-00s Soundtrack Memory |
| 107 | 15 | context_only | Film Score / Epic Score / Ambient Cinematic |
| 111 | 17 | context_only | Novelty / Comedy / Weird Pop |
| 112 | 17 | context_only | Holiday / Christmas / Seasonal Canon |
| 113 | 17 | context_only | Party / Wedding / Karaoke / Bar Singalong Canon |
| 114 | 17 | context_only | Kids / Family / Household Context Music |

## 5. Candidate Pool Shape

The app/local candidate pool should contain candidate records grouped by intended mission use:

| local pool | Allowed source rows | First mission use |
| --- | --- | --- |
| `anchors` | approved `page1_core`, strong positive survey evidence, anchor-eligible archetype | safe start points and comparison anchors |
| `bridges` | approved `page2_adaptive` or `page3_deep`, positive or mixed evidence, clear adjacent archetype | route connective tissue |
| `probes` | approved `page2_adaptive` or `page3_deep`, uncertain or unexplored branch | test promising territory |
| `boundary_probes` | boundary question bank or approved candidate with `boundary_test` / `false_nearby_test` | test edges without overclaiming |
| `dead_end_checks` | dead-end probe file only | cautious negative/control checks, never standard recommendations |
| `waypoints` | approved candidate with `waypoint_check`, `context_waypoint`, or weak positive evidence | useful filler or bridge, not promoted truth |
| `manual_review` | approved source but version/special-entity concern remains | local review only, not automatic OpenAI prompt payload |
| `excluded` | suppressed, quarantined, context-only, unresolved version, or unsafe source | not eligible |

First mission generation should receive a compact, local candidate pool rather than the whole graph.

Recommended Alpha size per user profile:

| pool | Suggested count |
| --- | --- |
| anchors | 8-24 |
| bridges | 8-24 |
| probes | 8-24 |
| boundary_probes | 2-8 |
| dead_end_checks | 0-4 |
| waypoints | 4-12 |

Do not send hundreds of candidates to OpenAI for a first mission. The model should design missions from a curated local pool, not rediscover the graph.

## 6. Candidate Fields Required by Mission Generation

Every candidate sent to mission generation must include these fields.

### Source Identity

```json
{
  "candidate_id": "survey-f12-song_recording-michael-jackson-billie-jean-088",
  "music_object_ref": {
    "object_type": "song_recording",
    "ref_source": "canonical_graph",
    "canonical_artist_id": null,
    "canonical_album_id": null,
    "canonical_song_recording_id": "michael-jackson-billie-jean",
    "composition_placeholder_id": null,
    "user_music_object_id": null,
    "external_catalog_refs": {},
    "display_name": "Billie Jean",
    "resolution_state": "resolved",
    "composition_policy_status": "no_review_needed"
  },
  "canonical_entity_id": "michael-jackson-billie-jean",
  "object_type": "artist|album|song_recording|composition|context",
  "display_label": "Billie Jean",
  "family_id": 12,
  "archetype_ids": ["088"],
  "source_file": "survey_song_candidates_v0_2.json",
  "source_contract_version": "alpha_v0",
  "source_membership_id": "family-12-song-088-michael-jackson-billie-jean"
}
```

Required fields:

- `candidate_id`
- `music_object_ref`
- `canonical_entity_id`
- `object_type`
- `display_label`
- `family_id`
- `archetype_ids`
- `source_file`
- `source_contract_version`
- `source_membership_id`

### Survey and Selection Context

```json
{
  "survey_page_role": "page1_core|page2_adaptive|page3_deep",
  "survey_intent": "recognition_anchor|song_first_memory|artist_affinity_probe|album_world_test|era_scene_probe|bridge_test|boundary_test|false_nearby_test|dead_end_check|waypoint_check|context_memory|cultural_furniture_check|composition_version_check|resolution_test_only|deepening_only|do_not_survey",
  "dedupe_group": "song_recording:michael-jackson-billie-jean",
  "priority_score": 100,
  "trigger_rule": "generated_from_membership_roles_and_tiers"
}
```

Required fields:

- `survey_page_role`
- `survey_intent`
- `dedupe_group`
- `priority_score`
- `trigger_rule`

Allowed mission input values for `survey_page_role`:

- `page1_core`
- `page2_adaptive`
- `page3_deep`

Blocked values:

- `suppressed`
- `quarantined`
- `suppressed_quarantined`

### Mission Use

The local pool builder must derive these mission fields before sending candidates to mission generation:

```json
{
  "mission_candidate_role": "anchor|bridge|probe|boundary_probe|dead_end_check|waypoint|palate_cleanser|manual_review_only",
  "why_selected": "Strong positive survey signal on pop-sovereign groove architecture; useful anchor for testing polished dance-pop versus rock-body force.",
  "risk_class": "low|medium|high|manual_review",
  "familiarity_assumption": "known|likely_known|unknown|likely_unknown",
  "expected_signal": "tests whether this is active appetite, cultural memory, waypoint value, or boundary",
  "candidate_pool_reason": "selected from approved page1_core positive survey response"
}
```

Required fields:

- `mission_candidate_role`
- `why_selected`
- `risk_class`
- `familiarity_assumption`
- `expected_signal`
- `candidate_pool_reason`

Mission generation should treat `mission_candidate_role` as operational guidance, not user truth.

`music_object_ref` is also operational identity and resolution context only. It must not be treated as user taste, Atlas role truth, confidence, or promotion state.

### Inference Guardrails

```json
{
  "positive_inference": [
    "possible appetite for polished groove-pop with menace and architecture"
  ],
  "negative_inference": [
    "may reject highly polished 80s pop architecture"
  ],
  "do_not_infer": [
    "do not infer generic 80s pop appetite",
    "do not infer canonical graph mutation from survey response"
  ]
}
```

Required fields:

- `positive_inference`
- `negative_inference`
- `do_not_infer`

All three must be non-empty arrays before sending to OpenAI.

### Safety State

```json
{
  "review_status": "approved",
  "quarantine_reasons": [],
  "suppression_state": "active",
  "quarantine_checked": true,
  "dedupe_checked": true,
  "eligible_for_openai": true,
  "eligible_for_supabase": true
}
```

Required fields:

- `review_status`
- `quarantine_reasons`
- `suppression_state`
- `quarantine_checked`
- `dedupe_checked`
- `eligible_for_openai`
- `eligible_for_supabase`

Any non-empty `quarantine_reasons` fails the candidate.

### MusicKit / Resolver Fields

For `song_recording` candidates, enrich from `canonical_recording_versions.json` when available:

```json
{
  "recording_id": "michael-jackson-billie-jean",
  "composition_id": "comp-billie-jean",
  "recording_context": "original|source_version|cover|remake|live|radio_edit|album_version|single_version|clean|explicit|remix|cast_recording|film_version|traditional_arrangement",
  "apple_music_resolution_policy": "exact_recording_required|version_flexible|composition_search_ok|manual_review_required",
  "survey_safe": true,
  "recording_review_status": "approved",
  "music_kit_search_hint": "Michael Jackson Billie Jean",
  "version_risk_note": "exact recording required"
}
```

Required for `song_recording`:

- `recording_id`
- `apple_music_resolution_policy`
- `survey_safe`
- `recording_review_status`
- `music_kit_search_hint`
- `version_risk_note`

Required when present in sidecar:

- `composition_id`
- `recording_context`

For `artist` and `album`, include:

```json
{
  "music_kit_search_hint": "artist or album display label plus credited artist when known",
  "version_risk_note": "not_applicable|album_version_sensitive|compilation_gateway|manual_review_required"
}
```

## 7. Quarantine and Suppression Rules

A candidate fails Alpha local-pool eligibility if any of the following are true:

- source row is in `suppressed_quarantined`
- `review_status != approved`
- `quarantine_reasons` is non-empty
- `canonical_entity_id` appears in `canonical_quarantine_queue.json`
- family has `fast_survey_allowed == false`
- family has `survey_readiness == context_only`
- archetype has `readiness == context_only`
- candidate has `survey_intent == do_not_survey`
- candidate has `survey_intent == resolution_test_only` and no resolver-specific mission is being run
- song recording has `survey_safe == false`
- recording version sidecar has `review_status == quarantined` or `needs_review`
- MusicKit policy is `manual_review_required` and no human has approved the specific mission use
- candidate lacks non-empty `positive_inference`, `negative_inference`, or `do_not_infer`
- candidate would duplicate another candidate by `canonical_entity_id` or `dedupe_group` inside the same mission route

Suppressed rows may remain in local QA tooling. They must not be sent to OpenAI or inserted into Supabase mission tables as active candidates.

Quarantined rows may remain in review queues. They must not feed:

- Fast Survey
- default first mission generation
- starter Atlas
- automatic MusicKit resolution
- OpenAI mission prompt payloads
- Supabase active mission candidate tables

## 8. MusicKit Version-Risk Notes

Default rule:

```text
song_recording -> exact_recording_required
```

Version risk must be visible before mission generation, not discovered after route creation.

### Safe Enough for Automatic Resolver Attempt

Allowed when:

- `review_status == approved`
- `survey_safe == true`
- `apple_music_resolution_policy == exact_recording_required`
- `recording_context` is ordinary original, album version, single version, or version-flexible approved row
- no quarantine queue entry exists

Even here, the resolver should prefer exact artist plus title plus year/context where available.

### Manual Review Required

Manual review is required before sending to automatic first mission generation when:

- `apple_music_resolution_policy == manual_review_required`
- candidate involves traditional/work-first material
- candidate involves worship standards or church-brand ambiguity
- candidate involves cast recordings, show tunes, film songs, fictional performers, or soundtrack context
- candidate involves classical works, arias, movements, or composition-first rows
- candidate involves known remix/edit/live/source/cover ambiguity not already resolved
- candidate involves explicit/clean variants where lyrical content matters to the route
- candidate involves electronic mix/edit/remix specificity
- candidate involves Latin/global remix, language, or collaboration specificity that changes the listening object

### Never Auto-Resolve

Never attempt automatic MusicKit resolution when:

- row is quarantined
- row is suppressed
- row is context-only
- row is `needs_review`
- row has unresolved composition/recording policy
- row is known wrong-attribution or suspected wrong-attribution
- row is a dead-end probe without a specific mission reason

## 9. Supabase Payload Boundary

Supabase may store local first-mission candidate records that pass this contract.

Minimum Supabase-safe candidate record:

```json
{
  "candidate_id": "",
  "canonical_entity_id": "",
  "object_type": "",
  "display_label": "",
  "family_id": 0,
  "archetype_ids": [],
  "survey_page_role": "",
  "survey_intent": "",
  "mission_candidate_role": "",
  "dedupe_group": "",
  "priority_score": 0,
  "why_selected": "",
  "expected_signal": "",
  "risk_class": "",
  "familiarity_assumption": "",
  "positive_inference": [],
  "negative_inference": [],
  "do_not_infer": [],
  "music_kit_search_hint": "",
  "apple_music_resolution_policy": "",
  "version_risk_note": "",
  "source_file": "",
  "source_contract_version": "alpha_v0",
  "review_status": "approved",
  "eligible_for_supabase": true
}
```

Supabase payload must not include:

- hidden simulator truth
- raw Apple Music private library payload
- Apple Music auth tokens
- full canonical graph row dumps
- quarantine queue internals beyond pass/fail reason needed for QA
- unreviewed personal notes unless user-consented product logging permits them

## 10. OpenAI Prompt Payload Boundary

OpenAI mission generation may receive only compact candidate records and observed/provisional user evidence.

OpenAI-safe payload may include:

- candidate identity fields
- object type and display label
- family and archetype context
- mission candidate role
- survey intent
- positive/negative/do-not-infer guardrails
- why selected
- expected signal
- risk class
- familiarity assumption
- version-risk note
- MusicKit search hint only when needed for route concreteness

OpenAI payload must not include:

- raw canonical graph tables
- hidden simulator truth
- direct claims that a user has a Landmark, Region, Frontier, Dead End, or Waypoint
- raw Apple payloads or private library dumps
- unresolved/quarantined candidate records
- false-nearby probes framed as recommendations

Preferred language for uncertain candidates:

```text
This candidate is a probe to test X, not a conclusion that the user likes Y.
```

## 11. False-Nearby and Dead-End Probe Handling

False-nearby and boundary candidates are allowed only as probes.

Rules:

- They must have `mission_candidate_role` of `boundary_probe` or `dead_end_check`.
- They must include `looks_nearby_because` or equivalent `why_selected`.
- They must include likely failure modes when available.
- They must not be described as recommendations.
- They must not create Atlas Dead Ends.
- They should appear sparingly in first missions.
- They should be avoided when the first mission needs to build trust rather than test a risky edge.

Promotion rule:

```text
requires repeated negative signal across route plus Atlas promotion logic
```

## 12. Pass/Fail Checklist: Safe to Send to Supabase/OpenAI

A local candidate pool passes only if every check below passes.

### Source and Scope

| Check | Pass condition |
| --- | --- |
| Approved source files only | Candidate came from the approved v0.2 files listed in this contract |
| Raw graph blocked | No raw family row or raw canonical entity row is sent |
| Family eligible | `family_id` is one of 1-14, 16, 18 |
| Context families excluded | No Family 15 or 17 candidate is present unless explicitly concierge/context-only and excluded from default generation |
| Archetype eligible | Anchor candidates use `survey_ready` archetypes; conditional archetypes are probe-only |

### Candidate Safety

| Check | Pass condition |
| --- | --- |
| Review approved | `review_status == approved` |
| No quarantine | `quarantine_reasons == []` and no matching quarantine queue entry |
| Not suppressed | Candidate is not from `suppressed_quarantined` |
| Dedupe passed | No duplicate `canonical_entity_id` or `dedupe_group` in the same mission route |
| Intent present | `survey_intent` is present and not `do_not_survey` |
| Guardrails present | `positive_inference`, `negative_inference`, and `do_not_infer` are non-empty |
| Mission role present | `mission_candidate_role` is present and allowed |

### MusicKit and Version Safety

| Check | Pass condition |
| --- | --- |
| Recording sidecar checked | Song recordings are checked against `canonical_recording_versions.json` |
| Survey safe | `survey_safe == true` for song recordings |
| Version approved | recording review status is `approved` |
| Resolver policy present | `apple_music_resolution_policy` is present |
| Manual review honored | `manual_review_required` candidates are not sent automatically |
| Quarantine blocks resolver | Quarantined rows are never auto-resolved |

### Supabase Safety

| Check | Pass condition |
| --- | --- |
| Typed object fields present | Candidate has `object_type`, `canonical_entity_id`, and `dedupe_group` |
| Contract version present | `source_contract_version == alpha_v0` |
| No hidden truth | No hidden simulator, evaluator-only, or fake-profile truth fields are included |
| No raw Apple private data | No auth token, private library dump, or unfiltered Apple payload is included |
| Provisional semantics | Candidate is not stored as promoted Atlas state |

### OpenAI Safety

| Check | Pass condition |
| --- | --- |
| Compact prompt payload | OpenAI receives curated local pool, not whole graph |
| Candidate role clear | Each item says whether it is anchor, bridge, probe, boundary, dead-end check, or waypoint |
| Probe language safe | False-nearby/dead-end rows are framed as probes, not conclusions |
| No Atlas overclaiming | Payload does not say the user has a confirmed Landmark, Region, Frontier, Dead End, or Waypoint |
| Do-not-infer included | Each candidate carries explicit inference limits |

If any check fails:

```text
candidate_pool_status = fail
do_not_send_to_openai = true
do_not_insert_as_active_supabase_candidate = true
route_generation_blocked_until_repaired = true
```

## 13. Alpha v0 Decision

The app/local candidate pool contract is frozen for first mission generation under this status:

```text
APP_LOCAL_CANDIDATE_POOL_ALPHA_V0_FROZEN
SAFE_FOR_LOCAL_FIRST_MISSION_GENERATION_WITH_GUARDRAILS
SAFE_TO_SEND_PASSING_CANDIDATES_TO_SUPABASE
SAFE_TO_SEND_PASSING_COMPACT_CANDIDATE_POOLS_TO_OPENAI
NOT_SAFE_FOR_RAW_GRAPH_FAST_SURVEY
NOT_SAFE_FOR_FULL_CANONICAL_IMPORT
NOT_SAFE_FOR_HARD_LOCK
NOT_SAFE_FOR_UNGUARDED_ATLAS_PROMOTION
```

The next review gate should inspect actual generated local candidate pools, not the raw graph:

```text
FIRST_MISSION_LOCAL_CANDIDATE_POOL_REVIEW
```

Focus:

- Are anchors recognizably useful?
- Are probes purposeful rather than random?
- Are false-nearby checks sparse and defensible?
- Are version-risk rows blocked or manually reviewed?
- Is the OpenAI prompt packet compact enough to guide mission design?
- Does the Supabase payload preserve evidence without promoting Atlas truth?
