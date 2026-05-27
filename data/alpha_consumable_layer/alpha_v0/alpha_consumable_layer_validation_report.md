# Alpha Consumable Layer Validation Report

Generated: 2026-05-25

Command:

```text
node scripts/validate_alpha_consumable_layer_alpha_v0.mjs
```

Result:

```text
ALPHA_CONSUMABLE_LAYER_VALIDATION_PASS
manifest=data/alpha_consumable_layer/alpha_v0/alpha_graph_surface_manifest.json
approved_source_files=9
anchor_eligible_archetypes=100
```

Validation coverage:

- approved source file existence
- approved source file SHA-256 checksums
- active candidate `review_status == approved`
- active candidate `quarantine_reasons == []`
- active candidate page role matches source bucket
- active candidate inference guardrails are non-empty
- song recording candidates have approved, survey-safe recording-version sidecar rows
- active graph candidates can be adapted into Atlas-aligned `music_object_ref` values
- `music_object_ref` examples cover canonical, user-local, external catalog, unresolved, and composition-placeholder paths
- canonical membership context explicitly says graph metadata is not user taste
- candidate required fields are present across active Alpha buckets
- duplicate canonical IDs and duplicate dedupe groups are blocked within active family/object/page buckets
- compact candidate pool sample preserves `alpha_v0`, `music_object_ref`, role/risk fields, and no duplicate dedupe groups
- compact candidate pool sample blocks duplicate route display identities across the route-ready export
- Alpha 1 fixed Survey intake capacity covers 4 artist pages, 2 album pages, and 4 song pages without using raw/suppressed/quarantined rows
- Alpha 1 first mission handoff contract preserves allowed candidate behaviors and blocks context-only families from default first missions
- compact candidate pool sample is route-ready for `MGN-I004`: 72 candidates, 50 tracks, 22 albums, 0 artist route candidates
- `waypoints` and `dead_end_checks` pools are non-empty and contain concrete route items
- route-ready candidates preserve `credited_artist`, `music_kit_search_hint`, `route_item`, `source_evidence_refs`, and Atlas reference-only semantics
- route-ready candidates preserve `candidate_id`, `app_route_item_id`, `route_candidate_key`, `route_batch_dedupe_key`, and `route_display_identity_key` for live generation/import validation
- route-ready candidates preserve candidate safety/review-gate metadata for live-smoke import tolerance
- candidate review-risk report confirms 72 default-eligible route candidates and 0 hard-blocked candidates
- Survey page-selection audit refs cover active Alpha Survey surfaces without raw graph rows or hidden simulator truth
- Survey runtime alignment requires ingestion from `survey_evidence_export.atlas_ingestable.evidence_atoms` only
- `construction_only_excluded` rows are explicitly non-ingestable
- `apple_exposure_prior` is not taste truth, `evidence_strength_hint` is not Atlas confidence, and `dont_know` maps to `familiarity_uncertainty`
- canonical quarantine collisions are blocked or alpha-blocklisted
- suppressed/quarantined source bucket rows are not treated as active Alpha candidates
- Alpha contract, overlay, and support file checksums match the manifest

Alpha overlay note:

- `album:robin-s-show-me-love` is blocked by `alpha_candidate_blocklist_alpha_v0.json` because the same canonical ID is quarantined as `song_recording:robin-s-show-me-love` for mix/edit resolution risk.
- The repaired graph source file is not mutated; the Alpha consumable layer excludes that candidate from Survey display, starter Atlas, default Mission Generation, Supabase active candidate rows, OpenAI prompt payloads, and Apple Music auto-resolution.
