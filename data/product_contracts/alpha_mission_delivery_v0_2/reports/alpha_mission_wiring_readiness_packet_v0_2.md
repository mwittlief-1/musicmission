# Cartenza Alpha Mission Wiring Readiness Packet v0.2

Decision: PARTIAL

## What Was Completed

- Mission Construction Contract v0.2 for Alpha-safe mission types.
- App-import mission payload schema and TypeScript types.
- Route validator/product gates.
- Golden approved/revise/rejected fixture set.
- Backend endpoint contract draft.
- App wiring readiness/gap report.
- Deterministic validation report.

## What Was Changed

New offline contract artifacts were added under `data/product_contracts/alpha_mission_delivery_v0_2/` plus two scripts under `scripts/`.

## What Was Intentionally Not Changed

- No iOS runtime files were modified.
- No Supabase function was implemented.
- No Apple Music/API calls were made.
- No canonical graph truth was mutated.
- No production mission generation was added.

## Can App Wiring Start Now?

Yes, against the local app-import payload contract and golden fixtures for decoder/adapter, route-card, feedback, validation, and resolution work.

## Can TestFlight UAT Start Now?

No. TestFlight UAT remains blocked by playback resolution and app schema/model compatibility.

## Top Blockers

| blocker | severity | owner | proposed next action | blocks app wiring? | blocks TestFlight? |
| --- | --- | --- | --- | --- | --- |
| Apple Music IDs/resolution missing from golden app-import candidates | high | App/Backend | Resolve candidates or add staging adapter | yes | yes |
| App mission enum/schema mismatch | high | App | Add Alpha payload decoder/adapter | yes | yes |
| Existing app importer expects unresolved route items | medium | App/Product | Reconcile candidate vs unresolved semantics | yes | yes |
| Live backend generation not implemented | medium | Backend | Implement guarded endpoint after local fixture wiring | no | yes |
| Artist/album mission types deferred | low | PM/Construction | Write stricter contracts before broad automation | no | no |

## Mission Type Readiness

| mission_type | alpha_auto_allowed | manual_only | deferred | rationale |
| --- | --- | --- | --- | --- |
| `context_dependence_test` | yes | no | no | Alpha-active with contract gates |
| `boundary_test` | yes | no | no | Alpha-active with contract gates |
| `bridge_test` | yes | no | no | Alpha-active with contract gates |
| `archetype_depth_test` | yes | no | no | Alpha-active with contract gates |
| `gateway_test` | yes | no | no | Alpha-active with contract gates |
| `artist_depth_test` | no | yes | yes | Deferred from automatic Alpha import |
| `album_container_test` | no | yes | yes | Deferred from automatic Alpha import |
| `false_nearby_test` | no | yes | yes | Deferred from automatic Alpha import |
| `evidence_repair_test` | no | yes | yes | Deferred from automatic Alpha import |
| `exception_scope_test` | no | yes | yes | Deferred from automatic Alpha import |

## Fixture Results

| pack_id | mission_type | expected_class | validator_status | app_import_candidate_or_ready | top_reason |
| --- | --- | --- | --- | --- | --- |
| `alpha-mission-v0-2-001-phase1g-public-profile-06-edge-heavy-200-context-dependence-test-mission-type-native-policy-v0-1` | `context_dependence_test` | approved_app_import_candidate | app_import_candidate | True | approved_for_app_fixture_import_after_music_resolution |
| `alpha-mission-v0-2-002-phase1g-public-profile-06-edge-heavy-200-context-dependence-test-diagnostic-biased-policy-v0-1` | `context_dependence_test` | approved_app_import_candidate | app_import_candidate | True | approved_for_app_fixture_import_after_music_resolution |
| `alpha-mission-v0-2-003-phase1g-public-profile-06-edge-heavy-200-boundary-test-experience-balanced-policy-v0-1` | `boundary_test` | approved_app_import_candidate | app_import_candidate | True | approved_for_app_fixture_import_after_music_resolution |
| `alpha-mission-v0-2-004-phase1g-public-profile-05-song-heavy-200-boundary-test-mission-type-native-policy-v0-1` | `boundary_test` | approved_app_import_candidate | app_import_candidate | True | approved_for_app_fixture_import_after_music_resolution |
| `alpha-mission-v0-2-005-phase1g-public-profile-06-edge-heavy-200-bridge-test-diagnostic-biased-policy-v0-1` | `bridge_test` | approved_app_import_candidate | app_import_candidate | True | approved_for_app_fixture_import_after_music_resolution |
| `alpha-mission-v0-2-006-phase1g-public-profile-06-song-heavy-200-bridge-test-experience-balanced-policy-v0-1` | `bridge_test` | approved_app_import_candidate | app_import_candidate | True | approved_for_app_fixture_import_after_music_resolution |
| `alpha-mission-v0-2-007-phase1g-public-profile-06-profile-weighted-balanced-200-archetype-depth-test-experience-balanced-policy-v0-1` | `archetype_depth_test` | approved_app_import_candidate | app_import_candidate | True | approved_for_app_fixture_import_after_music_resolution |
| `alpha-mission-v0-2-008-phase1g-public-profile-05-song-heavy-200-archetype-depth-test-mission-type-native-policy-v0-1` | `archetype_depth_test` | approved_app_import_candidate | app_import_candidate | True | approved_for_app_fixture_import_after_music_resolution |
| `alpha-mission-v0-2-009-phase1g-public-profile-06-song-heavy-200-context-dependence-test-mission-type-native-policy-v0-1` | `context_dependence_test` | approved_app_import_candidate | app_import_candidate | True | approved_for_app_fixture_import_after_music_resolution |
| `alpha-mission-v0-2-010-phase1g-public-profile-06-song-heavy-200-context-dependence-test-diagnostic-biased-policy-v0-1` | `context_dependence_test` | approved_app_import_candidate | app_import_candidate | True | approved_for_app_fixture_import_after_music_resolution |
| `alpha-mission-v0-2-011-phase1g-public-profile-06-profile-weighted-balanced-200-boundary-test-diagnostic-biased-policy-v0-1` | `boundary_test` | revise_needed | needs_revision | False | too_negative, weak_or_punitive_route_evidence |
| `alpha-mission-v0-2-012-phase1g-public-profile-06-edge-heavy-200-boundary-test-mission-type-native-policy-v0-1` | `boundary_test` | revise_needed | needs_revision | False | too_negative, weak_or_punitive_route_evidence |
| `alpha-mission-v0-2-013-phase1g-public-profile-06-edge-heavy-200-boundary-test-diagnostic-biased-policy-v0-1` | `boundary_test` | revise_needed | needs_revision | False | too_negative, weak_or_punitive_route_evidence |
| `alpha-mission-v0-2-014-phase1g-public-profile-06-song-heavy-200-boundary-test-mission-type-native-policy-v0-1` | `boundary_test` | revise_needed | needs_revision | False | too_negative, weak_or_punitive_route_evidence |
| `alpha-mission-v0-2-015-phase1g-public-profile-06-profile-weighted-balanced-200-boundary-test-mission-type-native-policy-v0-1` | `boundary_test` | revise_needed | needs_revision | False | too_negative, weak_or_punitive_route_evidence |
| `alpha-mission-v0-2-016-phase1g-public-profile-06-song-heavy-200-boundary-test-diagnostic-biased-policy-v0-1` | `boundary_test` | revise_needed | needs_revision | False | too_negative, weak_or_punitive_route_evidence |
| `alpha-mission-v0-2-017-phase1g-public-profile-06-song-heavy-200-artist-depth-test-mission-type-native-policy-v0-1` | `artist_depth_test` | rejected_product | rejected_product | False | mission_type_deferred_for_alpha_auto_import |
| `alpha-mission-v0-2-018-phase1g-public-profile-06-song-heavy-200-artist-depth-test-diagnostic-biased-policy-v0-1` | `artist_depth_test` | rejected_product | rejected_product | False | mission_type_deferred_for_alpha_auto_import |
| `alpha-mission-v0-2-019-phase1g-public-profile-05-song-heavy-200-album-container-test-mission-type-native-policy-v0-1` | `album_container_test` | rejected_product | rejected_product | False | mission_type_deferred_for_alpha_auto_import, too_negative |
| `alpha-mission-v0-2-020-phase1g-public-profile-05-profile-weighted-balanced-200-album-container-test-mission-type-native-policy-v0-1` | `album_container_test` | rejected_product | rejected_product | False | mission_type_deferred_for_alpha_auto_import, too_negative |
| `alpha-mission-v0-2-021-phase1g-public-profile-01-song-heavy-200-bridge-test-mission-type-native-policy-v0-1` | `bridge_test` | rejected_product | rejected_product | False | too_negative, weak_or_punitive_route_evidence |
| `alpha-mission-v0-2-022-phase1g-public-profile-06-profile-weighted-balanced-200-context-dependence-test-mission-type-native-policy-v0-1` | `context_dependence_test` | rejected_product | app_import_blocked_unresolved | False | unresolved_playback_item |

## Required Artifacts

1. Mission Construction Contract v0.2: `mission_construction_contract_v0_2.md` and `.json`
2. Mission payload JSON Schema: `app_import_mission_payload_v0_2.schema.json`
3. TypeScript types: `types/app_import_mission_payload_v0_2.ts`
4. Validator script: `scripts/validate_alpha_mission_delivery_v0_2.py`
5. Golden approved fixtures: `fixtures/golden/approved_app_import_candidates_v0_2.json`
6. Golden revise/reject fixtures: `fixtures/golden/revise_needed_v0_2.json`, `fixtures/golden/rejected_v0_2.json`
7. Validation report: `reports/alpha_mission_delivery_validation_report_v0_2.*`
8. App-import readiness report: `reports/app_wiring_readiness_report_v0_2.md`
9. Backend endpoint contract: `backend/generate_first_mission_batch_endpoint_contract_v0_2.md`
10. App-import status model: `app_import_readiness_status_model_v0_2.md`

## Commands

```bash
python3 scripts/build_alpha_mission_delivery_v0_2.py
python3 scripts/validate_alpha_mission_delivery_v0_2.py
```

## Recommended Next Codex Dispatch

Implement the app-side local fixture import adapter behind a dev/debug flag, reconcile candidate/unresolved MusicKit resolution semantics, and run a tiny route-card/playback smoke against the approved app-import candidates after Apple Music ID resolution.
