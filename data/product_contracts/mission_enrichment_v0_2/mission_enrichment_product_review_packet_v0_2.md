# Mission Enrichment Product Review Packet v0.2

Status: Provisionally alpha-locked companion spec.

Date: 2026-06-04.

Alpha lock update: CEO/Product provisionally accepted this v0.2 direction for alpha on 2026-06-04 after six Build 45 missions passed live OpenAI output validation. See `reports/mission_enrichment_alpha_provisional_lock_2026_06_04.md` and `runs/build45_six_mission_enrichment_v0_2_combined_validated_20260604T173100Z/combined_summary.md`.

Runtime-candidate update: the open Product questions from the first review draft have been resolved in the local schemas, registry, prefilter, prompt, fixtures, and validator. See `reports/mission_enrichment_runtime_candidate_report_v0_2.md` for validation results.

## Purpose

Mission Enrichment gives a deterministic Cartenza mission better user-facing language and a small set of diagnostic secondary reaction chips.

The mission already exists before enrichment runs. This layer should make the mission easier to understand, help the user know what to listen for, and make follow-up feedback more useful to Atlas.

It should not feel like a critic explaining music to the user. It should feel like Cartenza is setting up a listening test in clear, warm language.

## Product Doctrine

Mission selection remains deterministic. Enrichment is a copy and feedback-affordance layer only.

The model does not create taste truth. It translates already-known mission context, song affinity tags, and user alignment hints into concise display copy and ranked secondary chip candidates.

The same contract must work for:

- A low-information first mission.
- A mature mission after many prior reactions.
- Any random Jane Doe user.
- All canonical archetypes and broad music domains, including pop, hip-hop, R&B, country, folk, jazz, classical/crossover, electronic, dance, rock, metal, global music, and instrumental listening.

## Supersession

This v0.2 direction supersedes v0.1. The earlier rock-heavy examples are useful only as historical design input. They should not define runtime language, tag naming, or acceptance coverage.

Notable v0.2 changes:

- Primary reactions use `love`, `like`, `ok`, and `dislike`.
- Secondary tags are universal and genre-neutral.
- Founder-specific terms are removed.
- User-specific personalization comes from `user_alignment_hints`, not bespoke chip IDs.
- Model output should use display-safe labels and avoid raw graph identifiers.

## Call Boundary

Allowed:

- Write concise mission-card copy.
- Write short route-item setup copy.
- Rank secondary reaction tag candidates from the provided allowed set.
- Link selected tags to song affinity evidence and alignment hints.
- Prepare post-completion interpretation seeds as provisional copy helpers.

Not allowed:

- Select the mission.
- Add, remove, reorder, or replace route items.
- Change canonical song IDs, item IDs, route roles, mission IDs, or mission type.
- Invent artists, songs, genres, tags, graph facts, or user history.
- Mutate Atlas directly.
- Treat affinity similarity as listener preference truth.
- Use founder-specific vocabulary.
- Assume the user understands music theory or critic language.
- Assume rock, guitar music, vocals, lyrics, albums, English-language music, or any other domain as default.

## Primary Reactions

The v0.2 surface should use these primary reaction words:

| Primary reaction | Product meaning |
| --- | --- |
| `love` | Strong positive appetite signal. |
| `like` | Positive or promising signal. |
| `ok` | Weak non-failure, context, waypoint, or uncertainty signal. |
| `dislike` | Negative, boundary, blocker, or less-like-this signal. |

CEO direction for this packet: v0.2 copy and contracts use these words. A later app/backend integration slice may still need to decide whether older internal storage values are migrated or mapped behind the scenes.

## Core Data Flow

1. A deterministic mission builder selects the mission and route items.
2. A deterministic input assembler builds `MissionEnrichmentInput_v0_2`.
3. A deterministic `SecondaryTagOpportunity` prefilter narrows the universal tag registry to plausible tag IDs per song.
4. The model writes copy and ranks at most six secondary tag candidates per song.
5. A validator rejects invalid, unsafe, or contract-breaking output.
6. The app filters visible secondary chips after the user chooses a primary reaction.
7. Atlas learns only from the user's actual reaction event, not from the model output alone.

## Input Contract

`MissionEnrichmentInput_v0_2` should contain only the compact evidence needed for one mission. It should not include full Atlas history or unrelated graph data.

Required top-level sections:

| Field | Purpose |
| --- | --- |
| `schema_version` | Constant: `mission_enrichment_input_v0_2`. |
| `runtime_context` | Surface, copy mode, max tags per song, language style, and safety flags. |
| `user_atlas_context_brief` | Compact provisional listener context. |
| `mission_context` | Deterministic mission metadata and hypothesis. |
| `route_items` | Fixed route item list with song metadata, affinity tags, and alignment hints. |
| `allowed_secondary_reaction_tags` | Approved tag objects or the prefiltered subset for this call. |
| `copy_guardrails` | Explicit copy and safety rules. |

### Runtime Context

Recommended fields:

| Field | Notes |
| --- | --- |
| `surface` | Example: `mission_card_and_feedback_chips`. |
| `mission_ordinal_for_user` | Integer, useful for tone and caution level. |
| `max_secondary_tags_per_song` | Product default: 6. |
| `copy_mode` | Example: `external_alpha`. |
| `language_style` | Example: `clear_warm_music_literate`. |
| `avoid_founder_vocabulary` | Must be true for this surface. |

Model selection should remain deployment configuration, not a hard requirement of the product contract.

### User Atlas Context Brief

Use generic, non-founder fields:

| Field | Purpose |
| --- | --- |
| `confirmed_positive_patterns` | Provisional patterns with labels, confidence, and evidence type. |
| `open_questions` | Unresolved questions this mission may clarify. |
| `known_boundaries` | Provisional boundaries or weakened patterns. |
| `recent_learning_summary` | Short recent-learning notes for mature journeys. |
| `coverage_notes` | Fatigue, repetition, or coverage guidance. |

This section should be small. Mission #40 should not send the whole listener history; it should send a brief synthesis.

### Mission Context

Recommended fields:

| Field | Notes |
| --- | --- |
| `mission_id` | Must be preserved in output. |
| `mission_type` | Controlled mission type label. |
| `risk_level` | Low, medium, or high. |
| `mission_hypothesis` | Internal/provisional hypothesis. |
| `why_this_mission_now` | Deterministic rationale. |
| `success_definition` | What useful learning would look like. |

Mission types may include:

- `archetype_depth_test`
- `artist_depth_test`
- `album_container_test`
- `bridge_test`
- `boundary_test`
- `context_dependence_test`
- `contrast_test`
- `frontier_test`
- `gateway_test`
- `recovery_test`
- `user_requested`

### Route Items

Each route item should include:

| Field | Purpose |
| --- | --- |
| `item_id` | Must be preserved in output. |
| `canonical_song_recording_id` | Stable song identity; not for display copy. |
| `sequence` | Route order; must not change. |
| `title` | Display title. |
| `artist` | Display artist. |
| `year` | Optional display/support fact when available. |
| `route_role` | Controlled role such as anchor, probe, stretch, boundary, contrast, or control. |
| `why_included` | Deterministic inclusion rationale. |
| `song_affinity_tags` | Five to eight highest-value tags for this song. |
| `user_alignment_hints` | How each relevant tag relates to the user's provisional Atlas. |
| `prefiltered_secondary_tag_ids` | Eight to fourteen plausible universal tags for this song. |

### User Alignment Hints

Approved alignment labels should be generic:

- `matches_known_positive`
- `matches_known_negative`
- `supports_confirmed_pattern`
- `stretches_known_positive`
- `tests_boundary`
- `tests_open_question`
- `frontier_probe`
- `contrast_item`
- `control_item`
- `recovery_item`
- `overexposure_check`
- `novelty_check`
- `context_dependence_check`

These hints let the same song affinity tag produce different chip options for different users.

Example:

```json
{
  "tag": "vocal_performance:detached_delivery",
  "alignment": "tests_boundary"
}
```

The model can then rank tags such as `VOICE_DID_NOT_WORK`, `TOO_DETACHED`, `INTERESTING_NOT_MINE`, or `RIGHT_MOOD_WRONG_MOMENT` if they are in the prefiltered allowed set.

## Output Contract

`MissionEnrichmentOutput_v0_2` should return JSON only.

Required top-level sections:

| Field | Purpose |
| --- | --- |
| `schema_version` | Constant: `mission_enrichment_output_v0_2`. |
| `mission_id` | Must match input. |
| `mission_copy` | Concise app-facing mission card copy. |
| `route_item_copy` | One copy block per route item. |
| `secondary_reaction_tag_candidates` | Ranked candidate tags per route item. |
| `post_completion_interpretation_seeds` | Provisional readout seeds for outcome types. |
| `internal_quality_notes` | Non-rendered quality/debug notes. |

### Mission Copy

Recommended fields:

| Field | Limit |
| --- | --- |
| `title` | Short app title, ideally under 8 words. |
| `subtitle` | One compact setup line. |
| `short_description` | One short paragraph. |
| `why_now` | One short paragraph or sentence. |
| `listen_for` | Two to four short bullets. |
| `mission_hypothesis_user_facing` | Provisional, test-oriented explanation. |

Tone should be clear, warm, and specific. Use words like `test`, `explore`, `check`, `clarify`, and `refine`. Avoid final-identity language.

### Route Item Copy

Each route item should include:

| Field | Purpose |
| --- | --- |
| `item_id` | Must match input. |
| `pre_play_line` | Short setup before listening. |
| `why_this_song` | App-ready rationale without internal IDs. |
| `listen_for` | One to three brief cues. |

### Secondary Reaction Tag Candidates

Each route item should return at most six tags total. Do not generate separate chip sets for each primary reaction.

Each selected tag should include:

| Field | Purpose |
| --- | --- |
| `tag_id` | Must be from allowed IDs. |
| `rank` | 1-based rank for this route item. |
| `display_label` | Must match approved label unless a later registry permits variants. |
| `valid_primary_reactions` | Subset of `love`, `like`, `ok`, `dislike`. |
| `why_this_tag_is_relevant` | Non-rendered rationale. |
| `linked_song_affinity_tags` | Evidence tags that made the chip relevant. |
| `linked_user_alignment_hints` | Alignment hints that made the chip user-specific. |
| `atlas_effect` | Registry-approved learning effect. |
| `atlas_signal_target` | Display-safe target type and labels. |

Allowed `atlas_signal_target.target_type` values:

- `affinity_tag`
- `pattern`
- `region`
- `mission_hypothesis`
- `boundary`
- `frontier`
- `context_rule`

Prefer display-safe labels in model output. Raw graph IDs should remain in deterministic app/backend context, not user-facing copy.

## Secondary Tag Opportunity Prefilter

The model should not receive the full tag registry for every song. A deterministic prefilter should narrow the registry to eight to fourteen plausible tag IDs per song, using:

- Route item affinity tags.
- User alignment hints.
- Mission type.
- Route role.
- Risk level.
- Coverage or overexposure notes.

The model then ranks the best candidates down to the product maximum, default six.

Prefilter principles:

- Always include at least one positive/confirming candidate when positive reactions are valid.
- Always include at least one uncertainty or split-signal candidate for probes, stretches, frontiers, and boundary tests.
- Include negative/boundary candidates only when song affinity tags or alignment hints support them.
- Avoid over-indexing on one facet, such as only voice or only beat, unless the mission is explicitly facet-specific.
- Do not expose raw affinity tags as chip labels.

## Atlas Event Boundary

The model output does not update Atlas by itself. Atlas should update only after the user reacts.

A later runtime event should store enough context to interpret the reaction:

```json
{
  "event_type": "mission_route_item_reaction",
  "mission_id": "",
  "item_id": "",
  "canonical_song_recording_id": "",
  "primary_reaction": "love | like | ok | dislike",
  "secondary_tag_ids": [],
  "song_affinity_tags": [],
  "user_alignment_hints_at_time_of_reaction": [],
  "mission_hypothesis": "",
  "route_role": "anchor | probe | stretch | boundary | contrast | control",
  "atlas_effect_candidates": []
}
```

Example interpretations:

- `love` plus `SOUND_WORKED` can strengthen the linked sound or production affinity tags.
- `dislike` plus `TOO_INTENSE` can mark intensity as a boundary without rejecting the whole region.
- `like` plus `RIGHT_SOUND_WRONG_SONG` can preserve an affinity signal while weakening the specific object fit.
- `ok` plus `RESPECT_MORE_THAN_WANT` can keep an item as a waypoint rather than a landmark.

## Validator Requirements

A later validator should reject output when:

- JSON is invalid.
- `schema_version` is wrong.
- `mission_id` does not match input.
- Any route item is missing or duplicated.
- Song order, item IDs, canonical song IDs, or route roles are changed.
- Any tag ID is unknown or not allowed for that route item.
- A route item has more than six secondary tag candidates.
- A tag uses unsupported primary reactions.
- Display copy exposes raw graph IDs or raw affinity tags.
- Copy invents artists, songs, genres, history, or unsupported facts.
- Copy makes final taste claims.
- Copy uses founder-specific language or banned calibration words.
- Copy assumes a genre, instrument, vocal presence, lyric language, album context, or music knowledge that was not supplied.

## Copy Guardrails

Preferred:

- "This route checks..."
- "This is a test of..."
- "If these land..."
- "If these split..."
- "Cartenza can refine..."
- "This may clarify..."

Avoid:

- "You are a..."
- "You love..."
- "Cartenza knows..."
- "Your true taste..."
- "Final map..."
- "Objectively..."
- "Obviously..."
- Founder-specific phrases and private calibration terms.
- Raw tags such as `sonic_texture:distorted_guitar`.

## Acceptance Coverage

The implementation-readiness slice should pass Product review and later prompt/validator checks against:

1. Existing Build 45-style rock-heavy sample.
2. Pop-forward user.
3. Hip-hop/R&B-forward user.
4. Country/folk-forward user.
5. Jazz/classical/instrumental user.
6. Electronic/dance-forward user.
7. Low-information first-mission user.
8. Mature mission #40 user with confirmed positives and known boundaries.
9. Boundary-test mission with mixed or negative prior evidence.
10. Context-dependence mission where timing or setting may matter.

Acceptance bar:

- Copy is concise, user-facing, and more helpful than deterministic placeholder copy.
- Secondary tags are reaction-, song-, and user-context-specific.
- Tags map cleanly to Atlas learning effects.
- The same schema works across mission ordinal, user type, and archetype.
- The model remains inside the deterministic mission boundary.

## Runtime Candidate Decisions Encoded

- Default max secondary chips per song is six.
- `display_label` must exactly equal the registry label in v0.2.
- `RIGHT_ARTIST_WRONG_TRACK` is gated by known artist context or explicit artist-level evidence.
- `NEEDS_MORE_CONTEXT` is gated by album-container, context-dependence, long-form, or context applicability evidence.
- `LESS_LIKE_THIS` is `dislike` only.
- Mission `ok` is weak explicit evidence for waypoint, context, uncertainty, or weak non-failure.
- Route-item applicability flags are required before schema hardening.
- Build 45 runtime compatibility preserves `gateway_test` and route roles `bridge`, `context`, and `comparator`.

## Provisional Alpha Lock

Product/CEO provisionally locked v0.2 for alpha on 2026-06-04 with the following scope:

- The v0.2 input/output schemas, registry, deterministic prefilter, prompt guardrails, validator, and Build 45 compatibility extensions are accepted as the alpha contract baseline.
- The combined Build 45 six-mission live OpenAI packet is accepted as provisional alpha output evidence.
- v0.1 remains superseded.
- Missing Build 45 affinity sidecar rows stay explicit gaps; the alpha behavior is to leave those per-song affinity arrays empty rather than infer tags.

Open integration follow-ups remain:

1. Decide the deployed OpenAI model and runtime secret/config path.
2. Wire the app/backend execution path without changing deterministic mission selection.
3. Decide whether `artist_context_available` is the runtime hook for artist-context gating.
4. Capture mission bodies and route items in future Supabase diagnostics so Product review does not rely on local share packets.
5. Backfill or consciously accept the three missing Build 45 affinity rows before treating those songs as fully sidecar-covered.
