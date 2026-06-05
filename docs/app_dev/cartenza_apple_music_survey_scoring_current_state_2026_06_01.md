# Cartenza Apple Music Survey Scoring Logic - 2026-06-01

## Purpose

This note is the cleaned Alpha contract for how Apple Music payload data should influence Survey page construction.

It is not an Atlas promotion policy, not a mission-generation policy, and not a canonical graph lock statement.

## Core Product Rules

Apple Music data is an exposure and familiarity prior only.

```text
apple_exposure_prior.taste_truth = false
```

Apple data may help Cartenza choose better Survey questions. It must not:

- create Atlas truth;
- create a Landmark, Region, Dead End, or Waypoint;
- mutate the canonical graph;
- imply preference without a visible user response;
- override quarantine, suppression, or Apple availability rules.

Survey responses write provisional evidence only. Atlas promotion remains owned by Atlas logic.

## Eligible Survey Universe

The Survey-eligible universe is the canonical graph, not a small hand-authored survey packet.

An object can be considered for Survey if all of these are true:

- it is a canonical `artist`, `album`, or `song_recording` object;
- it has a typed canonical ID;
- it has a usable Apple Music catalog resolution when playback/search specificity matters;
- it is not quarantined, suppressed, blocklisted, unresolved, or marked do-not-use;
- its object type is appropriate for the current page.

Rows without Apple IDs stay in the canonical graph for research, review, and future resolution. They must not feed Survey display, default mission playback, or automatic MusicKit resolution until resolved.

Compatibility note: app/resource names such as `survey_artist_candidates_v0_2.json`, `survey_album_candidates_v0_2.json`, and `survey_song_candidates_v0_2.json` may still exist as bundled priors or historical surfaces. They are not the product ceiling. Any canonical graph item with a valid Apple ID and no suppression flag is eligible in principle.

Operational rule: Survey tiles can come from any active canonical graph artist, album, or song when that object has an appropriate usable Apple Music catalog resolution for display/playback and is not quarantined, suppressed, blocklisted, or unresolved. Legacy `survey_*_candidates` resources must not be treated as a hard allowlist.

## Runtime Path

Current Alpha Survey flow:

```text
AppleMusicSignalProbeService
  -> AppleMusicSignalPayload
  -> SurveyStore.updateAppleMusicSignalPayload
  -> AlphaDynamicSurveyPageProvider.updateAppleMusicSignalPayload
  -> Apple exposure index
  -> page construction
  -> frozen displayed page history
  -> Survey Evidence Export
```

Compatibility note: `FixtureSurveyPageProvider` may still appear as a wrapper name in code/tests. Product behavior should be dynamic Survey construction, not static fixture pages.

## Apple Payload Sections

The scorer currently treats these sections as page-construction input:

```text
primary_signal_sources.recently_played_tracks.items
context_sources.replay_summary.items
```

Other captured sections are available for future scoring, but should not quietly become taste evidence:

```text
heavy_rotation
library_song_play_count
library_song_last_played
library_song_library_added
library_album_library_added
personal_recommendations
playlist_contexts
playlist_track_samples
observed_resource_annotations
catalog_hydration
excluded_or_diagnostic_sources
```

`catalog_hydration` can help resolution. It is not a preference signal by itself.

## Matching

For each Apple item, the scorer resolves to canonical objects in this order:

1. Match `catalog_id` / `apple_id` through `canonical_apple_music_catalog_index_v1.json`.
2. Use typed canonical object refs returned by the catalog index.
3. If no catalog match exists, use normalized display matching only as a fallback.
4. Never title-merge songs, covers, live versions, remixes, cast recordings, worship standards, or soundtrack objects.

Normalization for fallback matching:

```text
lowercase
diacritic-insensitive
ampersand -> "and"
remove punctuation
join alphanumeric tokens with hyphen
```

Fallback display matching is allowed to suggest a candidate. It must not override explicit version, quarantine, or do-not-merge policy.

## Uniform Apple Weighting

Apple rows now use uniform base weighting.

```text
base_source_weight = 1.0
recency_weight = disabled
rank_weight = disabled
replay_order_weight = disabled
```

Every matched Apple source row contributes one source event before object-specific rollup logic. A top Replay item and a lower Replay item have the same base weight.

Recently Played and Replay Summary both follow this rule.

When ranking "top artists" from Apple input, use the Apple payload scoring output after canonical resolution and song/album-to-artist rollup. Do not substitute recognition tier, canonical priority, old survey-surface priority, or generic popularity for the Apple-derived artist score.

## Object Specificity

Uniform source weighting does not mean every graph effect is identical. Cartenza still distinguishes direct object evidence from rollups:

```text
direct song match -> song evidence
direct album match -> album evidence
direct artist match -> artist evidence
song match -> light album/artist rollup
album match -> light artist rollup
artist match -> artist exposure only
```

Rollups are weaker because they are less specific. A play of one song should not become a broad artist or genre claim.

## Page Construction Principles

All Survey pages are 12-tile pages.

Page 1 should prioritize:

- recognizable canonical anchors;
- clear object identity;
- Apple-exposed objects when they ask useful questions;
- broad branching power;
- safe MusicKit resolution;
- no duplicate canonical IDs or dedupe groups;
- no unresolved version/composition rows.

Page 2 and later should prioritize:

- visible prior responses;
- adaptive branching;
- bridge and boundary tests;
- false-nearby probes used carefully;
- album-world vs song-first distinction;
- frontier probes where the user has opened the door.

Apple exposure can help select what to ask, but visible user responses should dominate adaptive pages.

## Boundary And False-Nearby Use

Canonical graph rows may carry roles such as:

```text
bridge
boundary
false_nearby
context
deep_cut
anchor
```

These roles are survey-question roles, not Atlas conclusions.

False-nearby and boundary rows can appear as probes only when the page is intentionally asking that question. A negative response to a false-nearby probe does not directly create an Atlas Dead End.

## Evidence Export

Survey Evidence Export should include only responses attached to frozen, displayed page history.

For displayed tiles, export may include:

```text
candidate_id
canonical_entity_id
music_object_ref
object_type
family_id
archetype_ids
survey_page_role
survey_intent
dedupe_group
shown_page_number
shown_position
user_response
familiarity / don't-know state
selected_tags
shown_unselected_tags
apple_exposure_prior
positive_inference
negative_inference
do_not_infer
```

Apple prior fields must remain scoped:

```text
apple_exposure_prior.taste_truth = false
apple_exposure_prior.exposure_or_familiarity_only = true
```

Unshown, unresolved, or construction-only responses should be quarantined under construction-only export sections and ignored by Atlas ingestion.

## Debug Trace

User-ingestable evidence should not include raw score internals.

A developer/support trace may record scoring details for debugging:

```text
candidate_id
canonical_id
matched Apple source refs
match path
direct_strength
rollup_strength
family/archetype contribution
bucket
selection reason
exclusion reason
```

That trace is construction-only. It is not Atlas-ingestable evidence.

## Guardrails

No Survey page should include:

- quarantined rows;
- suppressed rows;
- rows without usable Apple IDs when playback/search is required;
- unresolved version or composition rows;
- Garden State soundtrack rows or any other known no-Apple-ID excluded object;
- duplicate canonical IDs;
- duplicate dedupe groups;
- raw graph rows that bypass suppression policy;
- false-nearby rows as ordinary recommendations.

## Current Refinement Direction

The next Survey refinement should use the canonical graph plus Apple IDs as the playable/question universe, with these signals layered in order:

1. hard eligibility: object type, Apple ID, quarantine/suppression/blocklist;
2. canonical graph roles and archetype memberships;
3. Apple exposure/familiarity prior using uniform source-row weighting;
4. visible Survey response history;
5. affinity tags for adaptive branching, bridges, boundaries, and Page 2/3 specificity.

The useful recent affinity query shape is:

```text
driving_eighths
distorted_guitar
anthem
guitar_forward
urgent_delivery
```

Exact five-tag intersections may be sparse. Four-of-five matches are useful for adaptive Page 2/3 probes, especially when missing-tag differences help Cartenza ask a sharper question.

## Acceptance Standard

The Survey logic is in-bounds when:

- Apple data improves question selection without becoming taste truth;
- the full Apple-resolved canonical graph can feed Survey eligibility;
- no no-Apple-ID or quarantined object reaches Survey display;
- Page 1 remains normal-user recognizable;
- Page 2/3 ask better adaptive questions rather than merely deeper ones;
- song, album, and artist objects stay distinct;
- evidence export includes only visible, frozen page responses;
- Atlas receives provisional evidence, not conclusions.
