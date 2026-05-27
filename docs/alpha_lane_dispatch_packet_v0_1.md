# Alpha Lane Dispatch Packet v0.1

Generated: 2026-05-21

Purpose: instructions for the Core Waymark Build, Canonical Music Graph, and Survey Simulator lanes after inventory completion and Atlas Schema first-pass completion.

For editable lane checklists, use:

```text
docs/alpha_backlog/README.md
```

## Global Correction

The TestFlight app should not ship with prebuilt missions as user content.

Allowed:

- test fixtures in tests, docs, harnesses, and CI
- golden packet artifacts for contract validation
- debug-only sample missions that cannot appear in production TestFlight UX
- mission JSON delivered after install through a reviewed assignment/import path

Not allowed:

- production TestFlight app bundle as the mission source of truth
- personal mission packs in app resources for external testers
- first-run UX that implies Waymark already knows the user's missions before onboarding, assignment, or server/harness delivery

The golden Alpha packet is an integration fixture, not seed content.

## Shared Build Latitude

Each lane should keep building until it hits a dependency that truly requires another lane's completed contract. Atlas Schema v0.1 is now available as a provisional integration contract, so lanes should build against it instead of waiting for final Atlas product policy.

All lanes should preserve these boundaries:

- Survey gathers evidence; it does not create promoted Atlas truth.
- Canonical Graph supplies safe music-object substrate; it does not decide user taste.
- Core Waymark executes product flows and captures evidence; it does not generate missions locally.
- Mission artifacts are app-importable only after concrete route-item and product-review gates.
- Apple Music data is exposure/resolution context, not taste truth.
- Hidden simulator truth and evaluator-only fields never enter user-visible or Atlas-ingestable payloads.

## Atlas First-Pass Contract Now Available

Use these as provisional Alpha integration inputs:

- `data/atlas_schema/atlas_schema_contract_v0_1.md`
- `data/atlas_schema/atlas_schema_contract_v0_1.json`
- `data/atlas_schema/atlas_delta_v0_1.md`
- `data/atlas_schema/ingestion_proof/survey_evidence_export_v0_1/README.md`
- `data/atlas_schema/ingestion_proof/survey_to_atlas_digest_v0_1/README.md`
- `data/atlas_schema/ingestion_proof/a3_gpt_5_5_3x3/a3_ingestion_acceptance_report.md`

Accepted first-pass interfaces:

- typed `music_object_ref` supports `canonical_graph`, `user_local`, `external_catalog`, and `unresolved` refs
- supported object types are `artist`, `album`, `song_recording`, and `composition_placeholder`
- `AtlasNode` represents the thing and must not carry authoritative role truth
- `AtlasRoleAssignment` is authoritative for `landmark`, `region`, `frontier`, `dead_end`, `waypoint`, `unknown`, and `signal_only`
- persistent lifecycle fields are separate: `status`, `review_state`, and `promotion_state`
- `Signal` is the durable evidence ledger for survey, mission, open-road, import, note, review, and playback evidence
- `PossibleAtlasUpdateCandidate` stores proposed changes before they become Atlas state
- `AtlasDigestView` is the read surface for Mission Generation, Candidate Pool Builder, WWTSF substrate, evidence audit, and correction
- `AtlasDelta` summarizes what changed between Atlas states and is source material, not final truth or final copy

Do not wait for final promotion thresholds to build ingestion, export, digest, candidate-pool, or app-read paths. Promotion/demotion automation remains reviewed/manual until a separate policy is accepted.

## Dispatch: Core Waymark Build

Tell Core Waymark:

You own the TestFlight iOS runtime and evidence instrument. Pivot the app from "bundled mission library" to "missionless shell plus reviewed mission assignment/import."

Build everything you can against Atlas Schema v0.1:

- Remove or production-gate bundled user mission packs from the TestFlight flow.
- Keep sample missions only as tests/debug fixtures, not production Resources for users.
- Add a real empty state: no assigned missions yet, connect Apple Music, complete survey or wait for assigned route.
- Introduce a `MissionProvider` boundary that can support remote Supabase assignment, manual JSON import, and debug fixtures behind build flags.
- Accept only `app_import_candidate` mission JSON with stable `mission_id`, `item_id`, concrete route items, expected signals, player-card copy, reaction chip sets, and search hints.
- Keep mission generation out of the app.
- Preserve local persistence for assigned missions, sessions, playback records, reactions, chips, notes, resolution metadata, and exports.
- Keep physical-device MusicKit QA as the release gate.
- Hide diagnostics/export/resolver tools from the normal Alpha path while keeping them reachable for support.
- Add reset/recover behavior for local Alpha data.
- Keep reaction operations stable even if labels change.
- Continue hardening skip/no-signal, auto-advance, seek, wrong-version, unavailable-track, and export flows.
- Map app playback, reaction, chip, skip, note, resolution, and review evidence toward Atlas `Signal` source types.
- Preserve enough IDs for future `Signal -> AtlasDigestView -> AtlasDelta` ingestion: `mission_id`, `item_id`, playback event IDs, reaction operation, selected/shown-unselected chips, notes, MusicKit resolution, device context, and export IDs.
- Treat local app exports as Atlas-ingestion candidates, not direct Atlas writes.

You may proceed independently on:

- mission source abstraction
- empty-state and first-run shell
- production/debug resource split
- Supabase client stub or local import adapter
- evidence export hardening
- physical-device QA checklist
- TestFlight packaging readiness

Stop or flag dependency when you need:

- final Survey Output Contract if Survey is shown in-app
- final Release/Trust/Privacy copy for tester-facing privacy and support language
- final in-app decision for whether `AtlasDelta.user_facing_summary_inputs` appears in TestFlight
- final retention/deletion policy for Signals, notes, Apple exposure context, model packets, and exported evidence

Acceptance bar:

- A TestFlight user can install the app with no bundled missions, connect Apple Music, receive/import a reviewed mission after install, play it, react, persist state, export evidence, and never see provisional evidence represented as final Atlas truth.

## Dispatch: Canonical Music Graph

Tell Canonical Graph:

You own the safe music-object substrate. Keep building the Alpha consumable layer, not a full hard-locked canonical database.

Build everything you can against Atlas Schema v0.1:

- Freeze and version the approved Alpha graph surfaces used by Survey and Candidate Pool Builder.
- Preserve `survey_artist_candidates_v0_2.json`, `survey_album_candidates_v0_2.json`, `survey_song_candidates_v0_2.json`, readiness files, quarantine files, recording-version policy, boundary bank, and dead-end probe files as the only approved source layer.
- Produce a compact Alpha manifest that states included/excluded families, caution families, context-only families, and suppressed/quarantined rows.
- Add or harden machine-readable resolver policy fields for songs, albums, covers, live versions, remasters, clean/explicit variants, worship standards, theater/cast recordings, traditional/classical works, and soundtrack/context objects.
- Provide candidate role/risk vocabulary for anchors, bridges, probes, boundary probes, dead-end checks, waypoints, manual-review items, and excluded items.
- Export required tile-log metadata for Survey and app telemetry.
- Keep raw graph tables out of Fast Survey, starter Atlas, default mission generation, and app surfaces.
- Keep false-nearby and dead-end rows as probes only.
- Keep quarantine as a hard block for survey display and Apple Music auto-resolution.
- Align graph refs to Atlas `music_object_ref` requirements, including canonical artist, album, song recording, unresolved, external catalog, user-local, and composition-placeholder pathways.
- Provide graph metadata in a form Atlas can preserve without treating family/archetype membership as user-specific taste truth.

You may proceed independently on:

- Alpha graph surface manifest
- resolver/version policy sidecars
- candidate-pool input contract improvements
- QA ledgers and suppression/quarantine reporting
- duplicate/dedupe group enforcement
- family inclusion recommendations for trusted Alpha
- Graph-to-Survey metadata completeness checks

Stop or flag dependency when you need:

- Survey final page-count and reaction-label decisions
- App/MusicKit final resolver telemetry fields if they differ from current resolution metadata
- service-level referential integrity checks for canonical IDs if Atlas importer requirements exceed current graph artifacts
- final promotion semantics for when repeated evidence can create promoted Regions, Landmarks, Frontiers, Dead Ends, or Waypoints

Acceptance bar:

- Downstream lanes can consume Alpha graph surfaces without touching raw rows, quarantined objects, hidden simulator data, or graph metadata that looks like promoted user taste.

## Dispatch: Survey Simulator

Tell Survey Simulator:

You own evidence-gathering intelligence and Survey Evidence Export. Keep moving toward an app-renderable, production-facing survey contract while preserving simulator/private separation.

Build everything you can against Atlas Schema v0.1:

- Finalize the Alpha Survey Output Contract for app rendering and persistence.
- Produce app-renderable survey page packets from approved Canonical Graph surfaces only.
- Keep 12-tile page assumptions unless the product decision changes.
- Preserve five response states and stable internal normalization, including `dont_know_enough` as familiarity uncertainty and `ok` as waypoint/context evidence.
- Define selected tags, shown-unselected tags, optional notes, and freeform evidence rules.
- Keep Apple payload seeding as exposure prior with source-mix caps and audit logs.
- Generate Survey Evidence Export v0.1 or compatible successor from visible user responses only.
- Keep hidden fake-profile truth, hidden reason tags, lookup state, evaluator outputs, and construction-only logs out of Atlas-ingestable payloads.
- Provide validators for private-field leakage, append-only semantics, response-ref closure, typed refs, and Apple-as-exposure.
- Produce several app-ready survey slate examples and corresponding validated evidence exports.
- Target the proven Survey Evidence Export flow: `Survey Evidence Export -> Signal -> AtlasNode -> provisional AtlasRoleAssignment -> PossibleAtlasUpdateCandidate -> AtlasDigestView`.
- Preserve `evidence_strength_hint` as Survey-side basis metadata only; Atlas owns confidence.
- Preserve selected tags as user-visible Signal evidence and shown-unselected tags as weak/non-selected context.

You may proceed independently on:

- app survey packet schema
- survey page builder outputs
- reaction normalization map draft
- Apple exposure prior summary shape
- export validator coverage
- sample Alpha slates
- survey-feel QA prompts for trusted testers

Stop or flag dependency when you need:

- App final UI decision on whether Survey appears in this TestFlight build
- Canonical final family inclusion changes or graph label visibility decisions
- final Atlas correction/superseding atom policy if Survey needs to amend exported evidence after first export
- final promotion thresholds if Survey is asked to create anything beyond provisional Signals and update candidates

Acceptance bar:

- Survey can produce a validated, append-only evidence export from app-renderable pages, and nothing in the Survey output can be mistaken for a completed Atlas or mission assignment.

## Immediate Cross-Lane Ask

Ask each completed lane to return:

- files changed or produced
- contract version they consider frozen for Alpha
- guardrails enforced in code versus documented only
- dependencies they hit and exactly which lane owns each dependency
- "ready for Core app integration" status: yes, no, or yes with listed caveats
