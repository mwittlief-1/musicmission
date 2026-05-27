# Canonical Graph / Atlas Support Dispatch - Live Generation Recovery - 2026-05-25

## Mission

Support the recovery by validating identity/display contracts and evidence boundaries. Do not expand scope unless a Core, Survey, Infrastructure, or Mission Generation blocker points here.

## Read First

- `docs/alpha_backlog/live_generation_recovery_dispatch_2026_05_25.md`
- `docs/infra/waymark_alpha_live_diagnostic_evidence_review_2026_05_25.md`
- `data/alpha_consumable_layer/alpha_v0/graph_to_atlas_music_object_ref_alpha_v0.md`
- `data/atlas_schema/alpha_hardening/atlas_live_smoke_diagnostic_contract_v0_1.json`

## P1 Tasks

- [x] CAT-LGR-001 Verify route identity fields.
  - Confirm the stable fields validators should use for item identity, candidate identity, display identity, and MusicKit search identity.
  - Document any mismatch between `candidate_id`, `canonical_entity_id`, `item_id`, and app route `item_id`.
  - Output: `data/alpha_consumable_layer/alpha_v0/alpha_route_identity_contract_alpha_v0.json`
  - Output: `data/alpha_consumable_layer/alpha_v0/alpha_route_identity_contract_alpha_v0.md`
  - Output: `data/atlas_schema/alpha_hardening/canonical_atlas_route_identity_contract_alpha_v0_1.md`
  - Output: `data/atlas_schema/alpha_hardening/canonical_atlas_route_identity_contract_alpha_v0_1.json`
  - Output update: `data/alpha_consumable_layer/alpha_v0/sample_compact_candidate_pool_alpha_v0.json`
  - Output update: `MusicAtlasController/Resources/alpha_compact_candidate_pool_alpha_v0.json`
  - Validator: `scripts/validate_alpha_consumable_layer_alpha_v0.mjs`
  - Validator: `scripts/validate_canonical_atlas_route_identity_contract.py`
  - Confirmed identities:
    - `candidate_id`: exact candidate-pool membership key.
    - `app_route_item_id`: deterministic app item ID seed for `route.items[].item_id`.
    - `route_candidate_key`: canonical playable route identity.
    - `route_batch_dedupe_key`: graph/candidate dedupe key.
    - `route_display_identity_key`: normalized route type + artist + title fallback and batch-repeat guard.
  - Mismatch note: `canonical_entity_id` identifies the canonical graph object only; it is not app item identity or candidate membership by itself.
  - Mismatch note: `route.items[].item_id` is app import identity; it is not proof of candidate-pool membership without `candidate_id`.

- [x] CAT-LGR-002 Verify display-name contract.
  - Identify app-facing display fields for artist, album, and song tiles.
  - Confirm internal slugs are never the preferred UI display value.
  - Output: `data/alpha_consumable_layer/alpha_v0/alpha_route_identity_contract_alpha_v0.md`
  - App-facing fields: `display_name`, `display_label`, `credited_artist`, `music_object_ref.display_name`, `music_object_ref.credited_artist_name`.
  - Internal-only fields: `candidate_id`, `canonical_entity_id`, `route_candidate_key`, `route_batch_dedupe_key`, `dedupe_group`, `source_membership_id`.

- [x] CAT-LGR-003 Verify candidate-pool provenance.
  - Confirm whether route items may ever come from digest strong regions without also being present in `candidate_pool.candidates`.
  - Current recovery assumption: no.
  - Decision: no. Route items must come from the supplied candidate pool; digest regions, Survey-visible tiles, Atlas hints, Apple exposure, model memory, and raw graph rows may explain selection but cannot create playable route items.
  - Output: `data/alpha_consumable_layer/alpha_v0/alpha_route_identity_contract_alpha_v0.json`
  - Output updates: `data/alpha_consumable_layer/alpha_v0/alpha1_first_mission_handoff_graph_contract_alpha_v0.json`
  - Output updates: `data/alpha_consumable_layer/alpha_v0/alpha1_first_mission_handoff_graph_contract_alpha_v0.md`

- [x] CAT-LGR-004 Verify Atlas evidence boundary.
  - Diagnostic artifacts remain support-only unless explicitly classified as Atlas-ingestable evidence.
  - Survey evidence remains provisional and append-only.
  - Mission generation results do not promote Atlas truth.
  - Output: `data/alpha_consumable_layer/alpha_v0/alpha_route_identity_contract_alpha_v0.json`
  - Output: `data/atlas_schema/alpha_hardening/canonical_atlas_route_identity_contract_alpha_v0_1.md`
  - Confirmed: route identity, generation results, diagnostics, and candidate-pool membership are operational references only and do not promote Atlas truth.

## Acceptance

- Core/Infrastructure have exact identity fields for duplicate/non-candidate validation.
- Survey/Core have exact display fields for user-facing grids.
- Mission Generation has a clear "candidate-pool-only" source rule.
- No recovery task accidentally promotes diagnostic or generated material into Atlas truth.

## Blockers To Raise

| issue id | blocker | owner lane | needed for | current workaround | status |
| --- | --- | --- | --- | --- | --- |
| `CAT-LGR-I001` | Core bundled candidate resource contains `app_route_item_id`, `route_candidate_key`, `route_batch_dedupe_key`, and `route_display_identity_key`, but the current `AlphaRouteCandidate` decoder/dictionary does not preserve those fields into live `candidate_pool.candidates`. | Core Waymark Build | Mission Generation/Supabase need exact non-display route keys and deterministic app item IDs in the live request payload. | Supabase can still enforce `candidate_id` membership and reconstructed display identity. Strong route-key validation remains partial until Core passes these fields through. | open |

## Completion Note

- status: `canonical_route_identity_contract_complete`
- files changed:
  - `data/alpha_consumable_layer/alpha_v0/alpha_route_identity_contract_alpha_v0.json`
  - `data/alpha_consumable_layer/alpha_v0/alpha_route_identity_contract_alpha_v0.md`
  - `data/atlas_schema/alpha_hardening/canonical_atlas_route_identity_contract_alpha_v0_1.md`
  - `data/atlas_schema/alpha_hardening/canonical_atlas_route_identity_contract_alpha_v0_1.json`
  - `data/atlas_schema/alpha_hardening/atlas_contract_index_v0_1.md`
  - `data/alpha_consumable_layer/alpha_v0/sample_compact_candidate_pool_alpha_v0.json`
  - `MusicAtlasController/Resources/alpha_compact_candidate_pool_alpha_v0.json`
  - `data/alpha_consumable_layer/alpha_v0/route_ready_candidate_pool_report_alpha_v0.json`
  - `data/alpha_consumable_layer/alpha_v0/route_ready_candidate_pool_report_alpha_v0.md`
  - `data/alpha_consumable_layer/alpha_v0/candidate_review_risk_report_alpha_v0.json`
  - `data/alpha_consumable_layer/alpha_v0/candidate_review_risk_report_alpha_v0.md`
  - `data/alpha_consumable_layer/alpha_v0/compact_candidate_pool_export_format_alpha_v0.md`
  - `data/alpha_consumable_layer/alpha_v0/alpha1_first_mission_handoff_graph_contract_alpha_v0.json`
  - `data/alpha_consumable_layer/alpha_v0/alpha1_first_mission_handoff_graph_contract_alpha_v0.md`
  - `data/alpha_consumable_layer/alpha_v0/alpha_graph_surface_manifest.json`
  - `data/alpha_consumable_layer/alpha_v0/alpha_graph_surface_manifest.md`
  - `data/alpha_consumable_layer/alpha_v0/alpha_consumable_layer_validation_report.md`
  - `scripts/build_alpha_compact_candidate_pool_alpha_v0.mjs`
  - `scripts/validate_alpha_consumable_layer_alpha_v0.mjs`
  - `scripts/validate_canonical_atlas_route_identity_contract.py`
  - `docs/alpha_backlog/live_generation_recovery_canonical_atlas_support_2026_05_25.md`
- commands/tests run:
  - `node scripts/build_alpha_compact_candidate_pool_alpha_v0.mjs`
  - `node scripts/build_alpha_live_smoke_recovery_graph_artifacts_alpha_v0.mjs`
  - `node scripts/validate_alpha_consumable_layer_alpha_v0.mjs` -> `ALPHA_CONSUMABLE_LAYER_VALIDATION_PASS`
  - `python3 scripts/validate_canonical_atlas_route_identity_contract.py` -> `ROUTE_IDENTITY_CONTRACT_VALIDATION_PASS`
  - `python3 scripts/validate_atlas_alpha_contracts.py` -> `Atlas Alpha validation passed`
  - `python3 -m py_compile scripts/validate_canonical_atlas_route_identity_contract.py`
  - JSON syntax checks for `alpha_graph_surface_manifest.json`, `alpha_route_identity_contract_alpha_v0.json`, `canonical_atlas_route_identity_contract_alpha_v0_1.json`, and `route_ready_candidate_pool_report_alpha_v0.json`
  - candidate-pool uniqueness check: `candidate_id`, `dedupe_group`, `route_candidate_key`, `route_batch_dedupe_key`, `app_route_item_id`, and `route_display_identity_key` are all `72/72`
  - duplicate repair check: current pool has exactly one `track:alicia-keys:fallin` route display identity after the builder skipped the second `Fallin'` candidate row.
  - bundled resource parity check: `MusicAtlasController/Resources/alpha_compact_candidate_pool_alpha_v0.json` matches `data/alpha_consumable_layer/alpha_v0/sample_compact_candidate_pool_alpha_v0.json`.
- live deploy or build number: n/a for Canonical lane; no live Supabase deploy performed here.
- remaining blockers:
  - `CAT-LGR-I001` Core passthrough for new route identity fields.
  - Live Supabase deployment remains owned by Infrastructure.
- handoff needed from:
  - Core Waymark Build: pass new route identity fields from the bundled Alpha resource into live `candidate_pool.candidates`.
  - Mission Generation: copy `candidate_id`, `app_route_item_id`, `route_candidate_key`, `route_batch_dedupe_key`, and `route_display_identity_key` from candidate pool rows into route items when schema allows.
  - Supabase / Infrastructure: enforce candidate-pool membership plus item/candidate/route-key/display-key batch dedupe in live validation.
