# Waymark Alpha Intake Lineage Report

Date: 2026-05-25

Status: read-only diagnostic pass. No app implementation changes are proposed here as completed work.

Scope: TestFlight build 12 lineage from Apple Music payload through dynamic Survey pages, Survey completion, and support/export artifacts.

## Executive Summary

Build 12 has the core stabilization work in place: Survey pages are generated from the dynamic canonical provider, displayed pages are persisted, the active page is stable after a tap, later pages avoid previously displayed item IDs, and exact artist dislikes suppress downstream albums/songs by normalized artist key.

The remaining lineage gap is not whether the app can preserve a visible page. It can. The gap is that the app does not currently persist the full selection trace that explains why each tile beat nearby alternatives. The existing `survey_page_selection_audit` records visible tiles, source/objective mixes, rough candidate basis, Apple exposure presence, and graph refs, but intentionally excludes raw scoring internals and does not include selected-vs-excluded candidate reasons.

The likely causes of "slow adaptation" and page changes on refresh are:

- Page 1 intentionally admits at most four Apple payload signature artists, then fills the rest from deterministic canonical calibration buckets.
- Apple influence after Page 1 is weak in the main score, and song pages request a `payloadSignature` bucket that the current bucket classifier only emits for artist Page 1.
- Future pages are invalidated after a tap, but responses from invalidated future pages are not removed and may continue influencing regenerated pages.
- `prepareRequiredAlphaIntake(resetExistingResponses: true)` can reset persisted Survey state when the first-run Survey view is recreated before `survey_completed` is true.
- Recapturing an Apple Music payload clears all displayed pages.

## Current Lineage Map

```text
First-run SurveyView
  -> AppleMusicSignalProbeService.capture()
  -> AppleMusicSignalPayload
  -> SurveyStore.updateAppleMusicSignalPayload()
  -> PersistedSurveySession.apple_music_signal_payload
  -> AlphaAppleEvidenceIndex
  -> AlphaDynamicSurveyPageProvider.loadCandidates()
  -> AlphaSurveyRuntimeCandidate pool
  -> selectCandidates()
  -> SurveyGridPage
  -> PersistedSurveySession.displayed_pages
  -> SurveyResponse taps
  -> invalidateFutureDisplayedPages()
  -> subsequent generated pages
  -> Survey readout / Build My Atlas
  -> SurveyEvidenceExportBuilder
  -> survey_evidence_export
  -> mission_generation_digest_view
  -> candidate_pool
  -> mission_generation_request_packet
  -> support diagnostic package / manual diagnostic upload
```

Primary code refs:

- Apple capture trigger: `MusicAtlasController/Views/SurveyView.swift:167`
- Payload persistence and page reset: `MusicAtlasController/Services/SurveyStore.swift:260`
- Displayed page cache: `MusicAtlasController/Services/SurveyStore.swift:422`
- Future page invalidation: `MusicAtlasController/Services/SurveyStore.swift:445`
- Dynamic page provider: `MusicAtlasController/Services/AlphaDynamicSurveyPageProvider.swift:44`
- Candidate selection: `MusicAtlasController/Services/AlphaDynamicSurveyPageProvider.swift:122`
- Apple evidence index: `MusicAtlasController/Services/AlphaDynamicSurveyPageProvider.swift:1031`
- Survey evidence export: `MusicAtlasController/Services/SurveyStore.swift:598`
- Page selection audit: `MusicAtlasController/Services/SurveyStore.swift:791`
- Support diagnostic package: `MusicAtlasController/Models/AppModel.swift:1268`

## Apple Music Payload Fields That Influence Selection

`AppleMusicSignalPayload` carries more data than selection uses. The scorer only consumes a small normalized exposure subset.

| Payload field | Selection effect |
| --- | --- |
| `library_artists_sample[].name` | Adds `+0.95` to normalized artist exposure strength. |
| `library_albums_sample[].artist_name` | Adds `+0.45` to normalized artist exposure strength. |
| `library_albums_sample[].title` + `artist_name` | Adds `+0.95` to normalized album exposure strength keyed as `artist::album`. |
| `library_songs_sample[].artist_name` | Adds `+0.30 + play_boost` to normalized artist exposure strength. |
| `library_songs_sample[].title` + `artist_name` | Adds `+0.85 + play_boost` to normalized song exposure strength keyed as `artist::song`. |
| `library_songs_sample[].album_title` + `artist_name` | Adds `+0.35` to normalized album exposure strength. |
| `library_songs_sample[].play_count` | Defines `play_boost = min(0.55, play_count / 40.0)`. |
| `personal_recommendations[].albums[].artist_name` | Adds `+0.20` to normalized artist exposure strength. |
| `personal_recommendations[].albums[].title` + `artist_name` | Adds `+0.35` to normalized album exposure strength. |

Captured but not used for page selection:

- `authorization`, except indirectly: unauthorized capture returns empty signal arrays.
- `environment.storefront`, `can_play_catalog_content`, `has_cloud_library_enabled`, and device context.
- `raw_endpoints`, including recent played tracks/resources, recently added, and heavy rotation.
- `library_playlists_sample`.
- recommendation playlists/stations/counts/reasons/titles.
- IDs, URLs, artwork URLs, genres, dates, duration, track count, and most library metadata.
- payload `errors` and `notes`.

Important mismatch: `AppleMusicSignalProbeService.payloadNotes` still says the payload "is not used to generate Survey grids yet", but build 12 does use the persisted payload as Survey page-selection input.

Normalization is exact-key oriented: strings are case/diacritic folded, `&` becomes `and`, non-alphanumeric separators are removed, and tokens are joined with `-`. Apple names that do not match canonical display/artist metadata simply do not affect canonical candidates.

## Apple Boosting And Scoring

`AlphaAppleEvidenceIndex` clamps artist, album, and song strengths to `1.0`.

Candidate Apple direct strength:

- Artist: max exposure for candidate display key or canonical artist name keys.
- Album: max exact album key match, or strongest candidate artist exposure multiplied by `0.45`.
- Song: max exact song key match, or strongest candidate artist exposure multiplied by `0.30`.

Derived Apple score values:

- `strength = directStrength`
- `baseline = max(0.25, priorityScore / 100.0)`
- `overrepresentation = directStrength / baseline`, clamped to `1.0`
- `archetypeHypothesis = directStrength > 0 ? 0.40 + directStrength * 0.60 : 0`

Artist Page 1 score:

```text
0.22 * overrepresentation
+ 0.18 * apple.strength
+ 0.16 * expectedFamiliarity
+ 0.14 * max(response.positiveShared, apple.archetypeHypothesis)
+ 0.12 * junction
+ 0.08 * anchor
+ 0.05 * falseNearby
+ 0.05 * coverage
- genericSuperstarPenalty
```

All later pages:

```text
0.22 * response.posteriorRelevance
+ 0.18 * response.informationGain
+ 0.14 * response.disambiguation
+ 0.12 * max(response.bridgeValue, junction)
+ 0.10 * coverage
+ 0.08 * falseNearby
+ 0.06 * expectedFamiliarity
+ 0.04 * apple.strength
+ 0.04 * frontier
- response.penalty
- genericSuperstarPenalty
```

Selection is deterministic:

1. Filter ineligible candidates.
2. Filter prior visible IDs and answered IDs.
3. Score candidates.
4. Sort by score descending, then `priorityScore` descending, then display key ascending.
5. Fill target intent buckets, first with family/archetype quotas, then strict fallback, then relaxed fallback.
6. Return the 12-item grid limit.

Artist Page 1 has a special pre-pass: when Apple signals exist, it can add up to four `payloadSignature` artists before the target-bucket fill. This is why dense Apple payloads still show only a few directly Apple-derived tiles on Page 1.

## Why Page 1 Can Look Similar Across Builds Or Runs

Page 1 is designed to be partly adaptive and partly calibration-heavy.

- The grid is capped at 12 tiles.
- With usable Apple signals, only four Page 1 artists are targeted as `payloadSignature`.
- The remaining slots are canonical graph tests: archetype confirmation, junctions, false-nearby, mass-popular control, and coverage repair.
- Selection has no random seed. Same payload plus same candidate resources will produce the same page.
- If Apple access is unavailable or the samples do not exact-match canonical names, Page 1 falls back to deterministic canonical graph ordering.
- Candidate resources are bundled and static for the build. Build-to-build similarity is expected unless resource files, canonical metadata, blocklist, or scoring rules changed.
- The library samples are capped: artists 50, albums 50, songs 100 sorted by play count, playlists 50, recommendations 10. That is a useful but narrow snapshot.

## Page Immutability And Refresh Reshuffle Points

Displayed pages are immutable in the common forward path: `currentPage` returns an already persisted page from `displayedPages` instead of regenerating it.

They are not globally immutable. A previously displayed page can be removed and later regenerated through these paths:

| Path | What changes |
| --- | --- |
| `updateAppleMusicSignalPayload` | Sets the new payload and clears all `displayedPages`. Any subsequent page access regenerates from the new Apple index. |
| `prepareRequiredAlphaIntake(resetExistingResponses: true)` | Clears responses, freeform signals, displayed pages, and Apple payload, then starts at connect Apple Music. |
| Tapping/changing a tile | Calls `invalidateFutureDisplayedPages`; pages after the tile's source page are removed and regenerated on next access. |
| Direct provider calls without displayed history | Recompute pages from current responses and deterministic fallback. App UI uses the store cache, but tests/support code can bypass it. |

High-risk refresh issue: `SurveyView(isFirstRunIntake: true)` calls `prepareRequiredAlphaIntake()` in `.task`, and the default is `resetExistingResponses: true`. The in-memory `hasPreparedRequiredAlphaIntake` flag only protects the current `SurveyStore` instance. If the first-run Survey view is recreated before `survey_completed` is true, the app can clear persisted in-progress Survey state and produce a fresh Page 1.

## Tap Adaptation Latency

Positive and negative taps affect future pages immediately in the store:

- `setState`, `toggleNuance`, and `updateNote` update `responses`.
- Each calls `invalidateFutureDisplayedPages(afterRespondingTo:)`.
- If the item belongs to Page N, pages after Page N are removed.
- The current page is not removed, so it does not reshuffle after a tap.
- The next page generated after navigation uses the updated responses.

Response scoring uses overlap with existing response items:

- Family overlap contributes `0.30`.
- Archetype overlap contributes `0.45`.
- Artist-name overlap contributes `0.30`.
- Favorites add overlap `+0.24`, likes add `+0.16`.
- `fine`, `notForMe`, and `dontKnow` feed disambiguation/negative/unknown paths.
- Exact same artist overlap can add a `0.35` exact-artist match boost to positive response relevance.

Observability and behavior gap: future page invalidation removes `displayedPages`, but it does not remove responses from those invalidated pages. Those now-non-visible responses remain in `responses`, still feed `responseRelevance`, and may alter regenerated future pages. Later export will quarantine responses that no longer resolve to visible pages, but page selection can already have been influenced by them.

## Artist Dislike Suppression

Artist dislikes suppress downstream albums and songs through `isBlockedByRejectedArtist`.

Current behavior:

- Only non-artist candidates are blocked.
- The rejected set is built from responses where `itemKind == .artist` and `state == .notForMe`.
- For each rejected artist response, the code adds the candidate's normalized canonical `artistNames` and display key.
- Album/song candidates are blocked when their normalized `artistNames` intersects that rejected set.

Known limits:

- Suppression is exact normalized artist-key matching, not broad graph propagation.
- It depends on canonical album/song metadata having the relevant `artist_names`.
- It does not suppress artist candidates themselves beyond answered/prior-visible ID exclusion.
- It does not use aliases, featured-artist variants, remixer/producer credits, or raw Apple IDs.
- It does not currently suppress downstream content from disliked album/song responses, only disliked artist responses.

## Survey Completion And Export Lineage

When the tester reaches readout and taps `Build My Atlas`, `RootView.completeSurvey` marks `survey_completed`, sets generation status, and starts first mission generation.

Generation request construction uses `SurveyEvidenceExportBuilder`:

- `survey_evidence_export`: user-visible Survey responses only, with visible page context, graph refs, Apple exposure prior flags, quarantined responses, and evidence semantics.
- `mission_generation_digest_view`: compact generation-only digest of positive, fine, negative, unknown, and freeform signals.
- `candidate_pool`: approved route-ready candidate pool, with policy that visible Survey tiles are evidence refs rather than the mission route pool.
- `mission_generation_request_packet`: emitted as support diagnostic before Supabase generation.

Support diagnostics can package:

- `apple_music_signal_payload`
- `survey_page_selection_audit`
- `survey_evidence_export`
- mission generation request/result/import artifacts
- client error events

The current support package is good enough to reconstruct what was shown and what was exported. It is not enough to reconstruct the full candidate ranking and exclusion path.

## Specific Observability Gaps

1. No persistent selection trace per generated page.

The app does not persist the score vector, rank, intent bucket, quota pass, fallback pass, family/archetype counts, or exclusion reason for selected and near-miss candidates.

2. No raw Apple-to-canonical match trace.

A tester cannot tell whether "I listen to Artist X" failed because the payload lacked Artist X, the sample cap missed Artist X, normalization did not match, or no canonical candidate exists.

3. Apple exposure prior is booleanized too early in diagnostics.

`apple_exposure_prior.present_on_visible_tile` says whether `strength >= 0.10`, but not the strength, matched field path, contribution source, normalized key, or direct vs artist-fallback match.

4. Future invalidation lacks audit events.

The audit does not record "Page 3 was previously generated, then removed because Page 1 item Y changed at time T."

5. Invalidated future responses remain in scoring inputs.

The export can quarantine them later, but the selector can already have used them as hidden input.

6. Page 1 Apple quota and deterministic canonical fill are not visible to testers/support.

The product behavior is intentional, but without a quota trace it feels like Apple Music is being ignored.

7. Song page target mix names a bucket the classifier does not emit for songs.

`targetMix` for songs includes `payloadSignature`, but `intentBucket` returns `payloadSignature` only inside artist Page 1 logic. Direct Apple song/album candidates can still appear via fallback, but not through the named target bucket.

8. Bundled canonical audit refs are not attached by the app page audit.

`data/alpha_consumable_layer/alpha_v0/survey_page_selection_audit_refs_alpha_v0.json` contains stable `audit_ref_id`, `candidate_id`, approved surface refs, family/archetype diagnostics, safety, and inference context. The app currently emits rough graph refs derived from item IDs, not those richer audit refs.

## Likely Causes To Investigate First

1. First-run Survey reset on app refresh.

If a tester refreshes/relaunches before completion, `prepareRequiredAlphaIntake()` can clear persisted displayed pages and Apple payload because it defaults to full reset.

2. Apple payload recapture clears displayed pages.

Any call to `updateAppleMusicSignalPayload` clears all page history. This is correct for a new payload, but it needs an explicit "restart Survey" concept or a diagnostic event.

3. Slow adaptation from weak post-Page-1 Apple weighting.

After artist Page 1, Apple strength is only `0.04` of the generic score. Most later adaptation comes from response overlap and canonical graph structure, not direct Apple exposure.

4. Hidden influence from invalidated future responses.

If a tester goes backward after visiting later pages, later page responses may remain in `responses` while their pages are removed from `displayedPages`.

5. Exact-name matching misses expected Apple influences.

No raw endpoint JSON, Apple IDs, genre names, dates, or playlist evidence enter the scorer. Apple exposure that is visible to the tester may be invisible to the app if it does not exact-match canonical display/artist keys in the capped sample arrays.

## Recommended Instrumentation

Add a support-only `survey_page_selection_trace` artifact, or extend `survey_page_selection_audit` to include a `selection_trace` block under each page.

Minimum page-level fields:

- `selection_algorithm_version`
- `candidate_resource_versions`
- `apple_payload_hash`
- `apple_payload_captured_at`
- `apple_index_summary`: normalized artist/album/song key counts and top matched keys
- `page_generation_event_id`
- `page_generation_reason`: first_generate, apple_payload_updated, future_invalidated, required_intake_reset, restored_from_cache
- `input_response_ids`
- `visible_history_before_page`
- `invalidated_page_history_refs`

Minimum selected-tile fields:

- `position`
- `survey_item_id`
- `audit_ref_id`
- `candidate_id` or `approved_surface_refs`
- `canonical_entity_ref`
- `display_label`
- `normalized_display_key`
- `dedupe_group`
- `family_ids`
- `archetype_ids`
- `survey_page_roles`
- `survey_intents`
- `priority_score`
- `recognition_tier`
- `survey_tier`
- `intent_bucket`
- `target_bucket`
- `selection_pass`: apple_prepass, target_strict, fallback_strict, fallback_relaxed
- `rank_before_quota`
- `final_score`
- score components: `apple_strength`, `apple_overrepresentation`, `apple_archetype_hypothesis`, `expected_familiarity`, `positive_shared`, `negative_shared`, `ok_shared`, `unknown_shared`, `posterior_relevance`, `information_gain`, `disambiguation`, `bridge_value`, `coverage_gap`, `junction`, `anchor`, `false_nearby`, `frontier`, `penalty`, `generic_superstar_penalty`
- `apple_match_trace`: payload paths, raw labels, normalized keys, contribution weights, direct/fallback match kind
- `quota_state_before_add` and `quota_state_after_add`

Minimum excluded-candidate fields:

- Top 25 by score per page after initial filtering.
- `candidate_id`, `canonical_entity_ref`, `display_label`, `intent_bucket`, `score`.
- `excluded_reason`: prior_visible_item_id, answered_item_id, duplicate_display_key, family_quota, archetype_quota, rejected_artist_block, deep_only_without_signal, blocklist, not_top_after_quota, grid_full.

Also add event diagnostics:

- `survey_page_cache_event`: page persisted/restored/cleared/regenerated.
- `survey_response_scope_event`: future page responses deleted, retained, or quarantined after invalidation.
- `apple_payload_index_event`: exact summary of payload fields that entered the evidence index.

## Implementation Tickets

### Survey Lane

`SURV-LIN-001` Add support-safe selection trace persistence.

Persist a page-generation trace alongside each displayed page. Include selected candidates, top excluded candidates, score components, bucket/quota pass, Apple match trace, and resource/version hashes. Acceptance: support can explain why every tile appeared and why higher-scoring visible alternatives were excluded.

`SURV-LIN-002` Make required Alpha intake preparation resumptive.

Change first-run preparation so app relaunch or first-run view recreation does not clear an in-progress Survey unless the user/support explicitly starts a new intake. Acceptance: closing/reopening during Page 2 restores the same Apple payload, Page 1, Page 2, responses, and session ID.

`SURV-LIN-003` Scope or purge responses from invalidated future pages.

When an earlier-page response invalidates future pages, either remove responses tied to those invalidated pages or mark them excluded from page-selection input until their page is visible again. Acceptance: no non-visible quarantined future response can affect regenerated page selection.

`SURV-LIN-004` Align song/album Apple bucket logic.

Either emit `payloadSignature` for direct Apple song/album candidates or change song page target mix to target `payloadAdjacent`/`objectSpecific` explicitly. Acceptance: direct Apple song/album matches have an auditable targeted path, not only fallback ranking.

`SURV-LIN-005` Add refresh/invalidation regression tests.

Cover app relaunch before Survey completion, Apple recapture, backward navigation after future pages have responses, current-page tap stability, and page regeneration event logs.

### Core Lane

`CORE-LIN-001` Include selection trace in support diagnostics.

Package `apple_music_signal_payload`, `survey_page_selection_trace`, `survey_page_selection_audit`, `survey_evidence_export`, generation request/result, import result, and client errors with shared `survey_session_id`, app build, and payload hashes.

`CORE-LIN-002` Add local page cache event diagnostics.

Record when displayed pages are created, restored, invalidated, or cleared, including reason and source response/item. Acceptance: a tester's "refresh changed my page" report has a local event trail.

`CORE-LIN-003` Freeze Apple payload after Page 1 unless tester restarts intake.

If a payload is already tied to displayed pages, recapture should either be blocked, create a new session, or require an explicit restart. Acceptance: no silent page history wipe from Apple recapture.

`CORE-LIN-004` Show support-safe Apple summary in diagnostics, not normal UI.

Expose counts, payload timestamp, sample caps, and unmatched Apple names in support diagnostics. Keep raw JSON out of normal tester UI.

### Canonical Lane

`CMG-LIN-001` Attach stable audit refs to app candidates.

Bundle or derive `audit_ref_id`, `candidate_id`, approved surface refs, family/archetype diagnostic refs, dedupe group, safety, and inference context from `survey_page_selection_audit_refs_alpha_v0`. Acceptance: every app tile can be joined to canonical audit refs without parsing item IDs.

`CMG-LIN-002` Add alias/credit normalization for suppression.

Expand canonical artist metadata used by albums/songs with aliases, featured credits, and normalized display variants where support-safe. Acceptance: disliked artists suppress obvious album/song variants beyond one exact display key.

`CMG-LIN-003` Produce Apple-to-canonical match diagnostics.

Generate a support-only report of Apple payload names/keys that matched canonical candidates, matched canonical metadata only, or remained unmatched. Acceptance: support can explain why a tester's visible Apple Music artist did or did not influence a page.

`CMG-LIN-004` Version the selection-resource bundle.

Emit candidate resource version/hash, canonical metadata version/hash, blocklist version/hash, and audit-ref version/hash in each selection trace. Acceptance: build-to-build page differences can be attributed to resource changes vs scoring changes vs Apple payload changes.
