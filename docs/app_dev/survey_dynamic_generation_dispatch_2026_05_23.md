# Survey Dynamic Generation Dispatch

Date: 2026-05-23

Status: Core blocked from further survey-candidate heuristics until Survey/Canonical Graph returns a live page generation contract or app-ready generator artifact.

## Problem

TestFlight currently proves the wrong Survey behavior.

The iOS app still renders the legacy fixture provider for first-run Survey. That provider contains static, hand-authored tiles and local app-side adaptive pools. It does not build Page 1 from the tester's Apple Music exposure, and Page 2+ does not use prior page responses through the Survey simulation/canonical graph logic.

Observed tester failure:

- Page 1 showed stale fixture artists.
- The tester marked Nirvana, Wipers, and Sonic Youth negatively.
- Page 2 still contained the same territory instead of pivoting from the prior responses.
- This made the app feel like it was ignoring Apple Music and ignoring Survey answers.

This is not acceptable to patch with app-side taste guesses.

## Product Boundary

Core must not invent fallback candidates.

If Apple Music produces too little signal, fallback Survey seeding must come from approved Canonical Graph survey surfaces, especially high-recognition or famous `page1_core` candidates. The app should not carry local hand-picked artist pools as production Survey logic.

Apple Music is an exposure prior, not taste truth.

Page N+1 must learn from Page N. Dedupe is necessary, but dedupe alone is not adaptation.

## Controlling Inputs

- `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/waymark_alpha_survey_output_contract_v0_1.md`
- `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/alpha_survey_page_packet_v0_1.schema.json`
- `data/canonical_graph/normalization_pass_2/survey_artist_candidates_v0_2.json`
- `data/canonical_graph/normalization_pass_2/survey_album_candidates_v0_2.json`
- `data/canonical_graph/normalization_pass_2/survey_song_candidates_v0_2.json`
- `docs/alpha_backlog/survey_simulator.md`
- `docs/alpha_backlog/canonical_music_graph.md`

## Required Survey-Lane Behavior

Build or expose a generator that produces app-renderable Survey page packets from:

- sanitized Apple Music exposure payload
- prior visible Survey responses
- prior visible tile history
- approved Canonical Graph survey candidate surfaces
- requested Alpha intake shape: 4 artist pages, 2 album pages, 4 song pages

Page 1 behavior:

- Match Apple Music exposure to approved Canonical Graph candidates where possible.
- Use Apple Music as `exposure_prior` with `taste_truth=false`.
- If Apple Music is thin, sparse, or unmatched, fill from approved Canonical Graph `page1_core` candidates.
- Prefer famous/high-recognition calibration candidates for fallback, not app-authored guesses.

Page 2+ behavior:

- Use prior responses as routing evidence, not final taste truth.
- Positive responses should trigger scoped confirmation, nearby road, bridge, and frontier probes.
- Negative responses should trigger scoped boundary checks, contrast probes, and possible dead-end validation.
- `ok` responses should trigger waypoint/context probes.
- `dont_know_enough` responses should trigger familiarity/recognition calibration, not negative inference.
- Exclude already visible objects by canonical id, display key, and `dedupe_group`.
- Avoid repeating the same narrow family/archetype after a negative unless the generator is explicitly testing a boundary with a different candidate role.

Album and song pages:

- Follow the same adaptive rules.
- Use album/song pages to test artist-wide versus object-specific taste.
- Do not reuse visible Survey songs as mission route content unless downstream Mission Generation explicitly passes the visible-repeat guardrail.

## Required Output

Return app-renderable packets compatible with `waymark.alpha_survey_page_packet.v0.1`.

Each tile must include:

- display text
- typed `music_object_ref`
- `approved_graph_surface_ref`
- `graph_refs` as refs/IDs only
- `apple_exposure_prior` when applicable, with `taste_truth=false`
- `candidate_basis`
- `page_intent`
- response capture contract for the five Alpha states
- evidence export linkage fields

No app-facing packet may include:

- hidden simulator truth
- hidden reason tags
- raw scoring
- generation prompts
- adaptive construction debug
- promoted Atlas truth

## Acceptance Test Required

Add a test case for the exact observed failure:

1. Apple Music payload is present but incomplete.
2. Page 1 contains Nirvana, Wipers, and Sonic Youth through Apple/canonical matching or canonical fallback.
3. User marks those three as `dont_like`.
4. Page 2 must not repeat those objects.
5. Page 2 must adapt away from direct repetition and toward scoped contrast, boundary, bridge, or unfamiliarity probes from approved Canonical Graph candidates.
6. The app-rendered packet remains valid against `alpha_survey_page_packet_v0_1.schema.json`.
7. Generated Survey Evidence Export remains valid and treats all Apple exposure as `taste_truth=false`.

## Core-App Follow-Up After Survey Output Exists

Once Survey/Canonical Graph provides the live generator or service contract, Core should:

- Replace the Release first-run `FixtureSurveyPageProvider`.
- Keep fixtures debug-only.
- Capture sanitized Apple Music exposure before Survey Page 1.
- Request each page from the Survey-owned generator/service with prior responses and visible tile history.
- Render returned page packets without changing candidate ranking.
- Persist response and visible-tile history for Survey Evidence Export.
- Preserve the five response states and existing Alpha Survey Evidence Export contract.

## Current Core Guardrail

Core should not make another TestFlight survey build claiming Apple Music/dynamic Survey behavior until the Release path no longer uses the legacy fixture provider.
