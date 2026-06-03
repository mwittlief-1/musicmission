# Alpha Mission Delivery Validation Report v0.2

Overall result: **PASS**

Approved app-import candidates: 10

App-import ready: 0

Schema errors: 0

Gate failures: 4

Gate failures include intentional rejected/deferred golden examples; approved app-import candidates have no blocking product-policy failures except the declared Apple Music resolution step.

## Fixture Results

| mission_id | mission_type | expected_class | computed_status | alpha_import_eligible | app_import_ready | top_blocking_reason |
| --- | --- | --- | --- | --- | --- | --- |
| `alpha-mission-v0-2-001-phase1g-public-profile-06-edge-heavy-200-context-dependence-test-mission-type-native-policy-v0-1` | `context_dependence_test` | approved_app_import_candidate | app_import_candidate | True | False | apple_music_resolution_remaining |
| `alpha-mission-v0-2-002-phase1g-public-profile-06-edge-heavy-200-context-dependence-test-diagnostic-biased-policy-v0-1` | `context_dependence_test` | approved_app_import_candidate | app_import_candidate | True | False | apple_music_resolution_remaining |
| `alpha-mission-v0-2-003-phase1g-public-profile-06-edge-heavy-200-boundary-test-experience-balanced-policy-v0-1` | `boundary_test` | approved_app_import_candidate | app_import_candidate | True | False | apple_music_resolution_remaining |
| `alpha-mission-v0-2-004-phase1g-public-profile-05-song-heavy-200-boundary-test-mission-type-native-policy-v0-1` | `boundary_test` | approved_app_import_candidate | app_import_candidate | True | False | apple_music_resolution_remaining |
| `alpha-mission-v0-2-005-phase1g-public-profile-06-edge-heavy-200-bridge-test-diagnostic-biased-policy-v0-1` | `bridge_test` | approved_app_import_candidate | app_import_candidate | True | False | apple_music_resolution_remaining |
| `alpha-mission-v0-2-006-phase1g-public-profile-06-song-heavy-200-bridge-test-experience-balanced-policy-v0-1` | `bridge_test` | approved_app_import_candidate | app_import_candidate | True | False | apple_music_resolution_remaining |
| `alpha-mission-v0-2-007-phase1g-public-profile-06-profile-weighted-balanced-200-archetype-depth-test-experience-balanced-policy-v0-1` | `archetype_depth_test` | approved_app_import_candidate | app_import_candidate | True | False | apple_music_resolution_remaining |
| `alpha-mission-v0-2-008-phase1g-public-profile-05-song-heavy-200-archetype-depth-test-mission-type-native-policy-v0-1` | `archetype_depth_test` | approved_app_import_candidate | app_import_candidate | True | False | apple_music_resolution_remaining |
| `alpha-mission-v0-2-009-phase1g-public-profile-06-song-heavy-200-context-dependence-test-mission-type-native-policy-v0-1` | `context_dependence_test` | approved_app_import_candidate | app_import_candidate | True | False | apple_music_resolution_remaining |
| `alpha-mission-v0-2-010-phase1g-public-profile-06-song-heavy-200-context-dependence-test-diagnostic-biased-policy-v0-1` | `context_dependence_test` | approved_app_import_candidate | app_import_candidate | True | False | apple_music_resolution_remaining |
| `alpha-mission-v0-2-011-phase1g-public-profile-06-profile-weighted-balanced-200-boundary-test-diagnostic-biased-policy-v0-1` | `boundary_test` | revise_needed | needs_revision | False | False | needs_revision |
| `alpha-mission-v0-2-012-phase1g-public-profile-06-edge-heavy-200-boundary-test-mission-type-native-policy-v0-1` | `boundary_test` | revise_needed | needs_revision | False | False | needs_revision |
| `alpha-mission-v0-2-013-phase1g-public-profile-06-edge-heavy-200-boundary-test-diagnostic-biased-policy-v0-1` | `boundary_test` | revise_needed | needs_revision | False | False | needs_revision |
| `alpha-mission-v0-2-014-phase1g-public-profile-06-song-heavy-200-boundary-test-mission-type-native-policy-v0-1` | `boundary_test` | revise_needed | needs_revision | False | False | needs_revision |
| `alpha-mission-v0-2-015-phase1g-public-profile-06-profile-weighted-balanced-200-boundary-test-mission-type-native-policy-v0-1` | `boundary_test` | revise_needed | needs_revision | False | False | needs_revision |
| `alpha-mission-v0-2-016-phase1g-public-profile-06-song-heavy-200-boundary-test-diagnostic-biased-policy-v0-1` | `boundary_test` | revise_needed | needs_revision | False | False | needs_revision |
| `alpha-mission-v0-2-017-phase1g-public-profile-06-song-heavy-200-artist-depth-test-mission-type-native-policy-v0-1` | `artist_depth_test` | rejected_product | rejected_product | False | False | mission_type_deferred_for_alpha_auto_import |
| `alpha-mission-v0-2-018-phase1g-public-profile-06-song-heavy-200-artist-depth-test-diagnostic-biased-policy-v0-1` | `artist_depth_test` | rejected_product | rejected_product | False | False | mission_type_deferred_for_alpha_auto_import |
| `alpha-mission-v0-2-019-phase1g-public-profile-05-song-heavy-200-album-container-test-mission-type-native-policy-v0-1` | `album_container_test` | rejected_product | rejected_product | False | False | mission_type_deferred_for_alpha_auto_import |
| `alpha-mission-v0-2-020-phase1g-public-profile-05-profile-weighted-balanced-200-album-container-test-mission-type-native-policy-v0-1` | `album_container_test` | rejected_product | rejected_product | False | False | mission_type_deferred_for_alpha_auto_import |
| `alpha-mission-v0-2-021-phase1g-public-profile-01-song-heavy-200-bridge-test-mission-type-native-policy-v0-1` | `bridge_test` | rejected_product | rejected_product | False | False | not_marked_as_import_candidate |
| `alpha-mission-v0-2-022-phase1g-public-profile-06-profile-weighted-balanced-200-context-dependence-test-mission-type-native-policy-v0-1` | `context_dependence_test` | rejected_product | app_import_blocked_unresolved | False | False | not_marked_as_import_candidate |

## Negative Fixture Results

| fixture | expected_fail | did_fail | reason |
| --- | --- | --- | --- |
| `constructor_input_hidden_reaction_labels_v0_2.json` | True | True | ['route', 0]: Additional properties are not allowed ('hidden_oracle_reaction' was unexpected) |
| `pack_final_mission_copy_v0_2.json` | True | True | []: Additional properties are not allowed ('final_mission_copy' was unexpected) |
| `pack_missing_source_opportunity_refs_v0_2.json` | True | True | missing_source_opportunity_refs |
| `pack_production_generation_true_v0_2.json` | True | True | ['runtime_flags', 'production_mission_generation_allowed']: False was expected |
| `pack_song_missing_why_in_route_v0_2.json` | True | True | ['route', 0, 'why_in_route']: '' should be non-empty |
| `pack_unresolved_app_ready_v0_2.json` | True | True | app_import_ready_missing_apple_music_ref, app_import_ready_requires_all_route_items_resolved |
| `same_seed_determinism_mismatch_v0_2.json` | True | True | determinism_mismatch |
| `selector_output_hidden_reaction_labels_v0_2.json` | True | True | hidden_oracle_or_final_copy_leakage |

## Guardrail Summary

- Runtime selector wiring remains false.
- Real listener evidence connection remains false.
- Production mission generation remains false.
- Final mission construction remains false.
- Canonical graph mutation remains false.
- Hidden oracle reactions are not present in app-import payload fixtures.
- Ordinary app-import-ready missions with unresolved route items are blocked.
