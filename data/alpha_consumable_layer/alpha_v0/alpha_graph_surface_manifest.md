# Alpha Graph Surface Manifest

Version: `alpha_v0`

Status: `frozen_alpha_consumable_surfaces_not_hard_lock`

This manifest freezes the approved Alpha graph surfaces for app/local Survey, starter Atlas references, default first Mission Generation candidate pools, and Supabase/OpenAI handoff checks. It does not hard-lock the canonical database.

## Controlling Contracts

- `data/product_contracts/app_local_candidate_pool_contract_alpha_v0.md`
- `data/product_contracts/graph_staging_contract.md`
- `data/product_contracts/cross_team_consistency_review.md`
- `docs/app_dev/alpha_product_decision_addendum_2026_05_22.md`

## Approved Source Files

| file | bytes | sha256 |
| --- | ---: | --- |
| `data/canonical_graph/normalization_pass_2/survey_artist_candidates_v0_2.json` | 2214388 | `4d65d3178ea2c303a35bc66af14b733806f9a122d6fc6dff73114b91e821356e` |
| `data/canonical_graph/normalization_pass_2/survey_album_candidates_v0_2.json` | 1927430 | `ccdc69380fcc0342cc63019515503d8b767778e93fef4b6779a26cbea042fcb3` |
| `data/canonical_graph/normalization_pass_2/survey_song_candidates_v0_2.json` | 3002522 | `26c90f4dbe3b5430b1fd32f79041bcd4213cc83ebb61ac01435dc17672cb7391` |
| `data/canonical_graph/normalization_pass_2/family_survey_readiness_v0_2.json` | 5190 | `d6e4d8973059f0148581257e2778e692a9fde43149dfd5905bcae98f38c21d18` |
| `data/canonical_graph/normalization_pass_2/archetype_readiness_v0_2.json` | 34425 | `23197f087b0b3c418ce0911c33c15964d2a355ff93eac50da9419b9323ef09f7` |
| `data/canonical_graph/normalization_pass_2/canonical_quarantine_queue.json` | 72798 | `b4bac88dcc6c706269b353609c9a52b54e56e65d78b94f0102fd7233c6ac5e6a` |
| `data/canonical_graph/normalization_pass_2/canonical_recording_versions.json` | 1100062 | `bf876dfa5e1e4663de4635ffb67179cd6be432d28db92180df3a57048d7c99a2` |
| `data/canonical_graph/normalization_pass_2/dead_end_probe_candidates_v0_2.json` | 475012 | `0398ea2d59e67251dee70138fbe8c538996a2429712a38045a9dc9dba1711418` |
| `data/canonical_graph/normalization_pass_2/boundary_question_bank_v0_2.json` | 366529 | `10b49e370a5f13053f263ffe1c0e2656f2a51d2096a1e75d700bd199759c5172` |

## Alpha Overlay Files

| file | rows | bytes | sha256 |
| --- | ---: | ---: | --- |
| `data/alpha_consumable_layer/alpha_v0/alpha_candidate_blocklist_alpha_v0.json` | 1 | 1368 | `2ecbb8000c9fee3b699fb03e6fef3af828b68064486d57db5429af711fd91c44` |

## Alpha Contract Files

| file | bytes | sha256 |
| --- | ---: | --- |
| `data/alpha_consumable_layer/alpha_v0/atlas_music_object_ref_alpha_v0.schema.json` | 6248 | `42d65258ffa2998278d898fb5bd2dc2a196620c9ecd102b905427da05c80ac1e` |
| `data/alpha_consumable_layer/alpha_v0/graph_to_atlas_music_object_ref_alpha_v0.md` | 9241 | `7ebf7eae8e267f813f12ba9bc4ffcd397367659bbee92f4f1a147bd7309b9fbd` |
| `data/alpha_consumable_layer/alpha_v0/atlas_music_object_ref_examples_alpha_v0.json` | 5906 | `7605adaa13558faec79720f6b59040dcab952842060e43e60c9bd991d53d003c` |
| `data/alpha_consumable_layer/alpha_v0/candidate_role_risk_vocabulary_alpha_v0.json` | 7586 | `dfc84a5f516eccef5a5ac06b00ebf68e5ff828496076d5234377467ca6af2ba7` |
| `data/alpha_consumable_layer/alpha_v0/candidate_role_risk_vocabulary_alpha_v0.md` | 4261 | `1d9f844a26bd1fc957f74f7240f7f6183da18a8229900bb2e93bdc99993db3ad` |
| `data/alpha_consumable_layer/alpha_v0/resolver_version_policy_sidecar_alpha_v0.json` | 4081 | `9afa1efe95e0cd873cb532980fe77be718ca651fc65a16f9c2be2e540b2a817a` |
| `data/alpha_consumable_layer/alpha_v0/resolver_version_policy_sidecar_alpha_v0.md` | 3738 | `a85661db8fdb6db29168f2e1306603fb37a062db5c2b4ca56c27520c48983491` |
| `data/alpha_consumable_layer/alpha_v0/resolver_policy_machine_fields_alpha_v0.json` | 1373720 | `4a40f300b49164707a3038810ced12eeec3a71e0c7f5171451403b9b85f5e6f1` |
| `data/alpha_consumable_layer/alpha_v0/resolver_policy_machine_fields_alpha_v0.md` | 1315 | `29aacd0643cc4d5c7ea1cccfa40140ff85d1fdcd5284263dfef44bd12e1c62ea` |
| `data/alpha_consumable_layer/alpha_v0/tile_log_metadata_contract_alpha_v0.json` | 3405 | `ea4a4eecae172ab9246da49c30aec7368c26afed29bd0bf0e17b37f4de1feeed` |
| `data/alpha_consumable_layer/alpha_v0/tile_log_metadata_contract_alpha_v0.md` | 3697 | `97d54af5fdf873da9275198e5ac0aa59c78172d1cc12bcec3499036404fdd65b` |
| `data/alpha_consumable_layer/alpha_v0/survey_runtime_ingestion_alignment_alpha_v0.json` | 2950 | `8ba13312132a2dfd86dbe2f6a13e2d88fdad019857913dcbeb3909a8acc7e92c` |
| `data/alpha_consumable_layer/alpha_v0/survey_runtime_ingestion_alignment_alpha_v0.md` | 2715 | `9eb5bd43bdf4ce0485a1ff291c53622eafe5a73f2cfcaa8e71477ccc0aeb9d39` |
| `data/alpha_consumable_layer/alpha_v0/survey_page_selection_audit_refs_alpha_v0.json` | 13683173 | `ed27eb513208bb8442cd8341b7c7e1e3d37727e407e952ada498f357496db170` |
| `data/alpha_consumable_layer/alpha_v0/survey_page_selection_audit_refs_alpha_v0.md` | 1047 | `de1b14de7b28145f75e7b4119ed5d801f60d4206e89c82f34ffffd6d92ee1f2d` |
| `data/alpha_consumable_layer/alpha_v0/alpha_consumable_layer_guardrails_alpha_v0.md` | 6124 | `3f554087f20fe0ea4111994a129ab19587e730ae5e79767b146f020487ec2643` |
| `data/alpha_consumable_layer/alpha_v0/alpha1_fixed_survey_intake_graph_support_alpha_v0.json` | 7089 | `e7b53672628d40706450c119a741d57920b4a2e7b08d76270347121a6929d517` |
| `data/alpha_consumable_layer/alpha_v0/alpha1_fixed_survey_intake_graph_support_alpha_v0.md` | 6037 | `a803301c118257883cec5ae805a307e0c3e815baed19111f55569be2f0153223` |
| `data/alpha_consumable_layer/alpha_v0/family_inclusion_recommendation_alpha_v0.json` | 6462 | `51f99dce55f764c3a44cf224343f577cda0b5f5519dea87f3082b029512ea904` |
| `data/alpha_consumable_layer/alpha_v0/family_inclusion_recommendation_alpha_v0.md` | 3484 | `f72f396c776c7b78129d0fd3a0adac0ad86989b12969052789142e0af1df7642` |
| `data/alpha_consumable_layer/alpha_v0/caution_family_playbook_alpha_v0.md` | 3507 | `b77d2891d2737078b0f5a22e1ac0145eb93b826eca69d8ddbce03af21b893c1f` |
| `data/alpha_consumable_layer/alpha_v0/canonical_gap_unresolved_object_policy_alpha_v0.md` | 2906 | `1a88db4e97a0f2acee2ce7e294fd1350296e729af81198d709877d91357a799b` |
| `data/alpha_consumable_layer/alpha_v0/compact_candidate_pool_export_format_alpha_v0.md` | 4865 | `0ea212826b22c640ebb15aa85d56d2787343f189d9c73e87f5e021c1059e5fb3` |
| `data/alpha_consumable_layer/alpha_v0/route_ready_candidate_pool_report_alpha_v0.json` | 3865 | `6de8a823fe834105b9c277acec74d1c48eec249e2d7b7453045fee6a0e706a17` |
| `data/alpha_consumable_layer/alpha_v0/route_ready_candidate_pool_report_alpha_v0.md` | 2950 | `381c602b7ebfcde7758e5983dfced2575e7b0b2fa76a0802a8d5911dcca398ec` |
| `data/alpha_consumable_layer/alpha_v0/candidate_review_risk_report_alpha_v0.json` | 156669 | `da06895f94a066d5d6cdd9fc5209854cdaf167baa529cb487a44d064ccaafa1e` |
| `data/alpha_consumable_layer/alpha_v0/candidate_review_risk_report_alpha_v0.md` | 13943 | `a47cdaa6c6271e827e503fe64747f84eca5d2b556b7addb68b58b643bcc218aa` |
| `data/alpha_consumable_layer/alpha_v0/alpha1_first_mission_handoff_graph_contract_alpha_v0.json` | 6368 | `1e2d8068ed099e8571bb633b32f6474cb9f8d0490657232fe500540a83595aab` |
| `data/alpha_consumable_layer/alpha_v0/alpha1_first_mission_handoff_graph_contract_alpha_v0.md` | 7202 | `cf9173fa8e73367334f95e8057d16d91596d3123eb0cfa5405353eb1d0095667` |
| `data/alpha_consumable_layer/alpha_v0/alpha1_user_facing_graph_language_guardrails_alpha_v0.md` | 3314 | `5bda3d8902d3f0cec0f20ab518711ebb5ab0f105b95370d20f923dfc81d4ea60` |
| `data/alpha_consumable_layer/alpha_v0/qa_exception_ledger_alpha_v0.json` | 162277 | `a6ab8b973979672d670fe2d4c0458e47ccca69f3fe96f961cb0e726e4d9c581f` |
| `data/alpha_consumable_layer/alpha_v0/qa_exception_ledger_alpha_v0.md` | 2182 | `d24d42ce5d99e685c61066500795dd747c72d086ca23ba52ecd447aeace7cb9a` |
| `data/alpha_consumable_layer/alpha_v0/alpha_route_identity_contract_alpha_v0.json` | 6454 | `d7f161d801975029ea8c5cc33b9e8c2cb63890ce3408674a730fafcfdeb2e993` |
| `data/alpha_consumable_layer/alpha_v0/alpha_route_identity_contract_alpha_v0.md` | 4667 | `15c4e937aac7897a6910a9db826b1828c2bd27725e1a0370820a246014985f31` |

## Alpha Support Files

| file | bytes | sha256 |
| --- | ---: | --- |
| `scripts/validate_alpha_consumable_layer_alpha_v0.mjs` | 39552 | `a67eca7f271ed343fb533a8d8296354a3a5e9113015b6db15654e7be7ba33306` |
| `scripts/build_alpha_compact_candidate_pool_alpha_v0.mjs` | 20672 | `ac92943478467fe5be19629fee46469d453b44770f42c3f47c50e640bd44b137` |
| `data/alpha_consumable_layer/alpha_v0/sample_compact_candidate_pool_alpha_v0.json` | 512243 | `d1f1d2a9eb291f1fcef4a17ee614dbb5b5f8ef19c041ce088494b4a7f920fdcd` |
| `scripts/build_alpha_live_smoke_recovery_graph_artifacts_alpha_v0.mjs` | 15585 | `ed468822d7f45c142cf1c50d1e781760a81ba340a5930c45ca78a2c153d59703` |

## Live Generation Recovery

Source: `docs/alpha_backlog/live_generation_recovery_dispatch_2026_05_25.md`

Status: `canonical_route_identity_contract_complete`

Route identity contract: `data/alpha_consumable_layer/alpha_v0/alpha_route_identity_contract_alpha_v0.json`

Route-ready candidate count: 72

Unique route_candidate_key values: 72

Unique route_batch_dedupe_key values: 72

Unique app_route_item_id values: 72

Unique route_display_identity_key values: 72

Candidate-pool-only route item rule: `true`

Digest or strong-region non-candidate route items allowed: `false`

## Live Alpha Smoke Recovery

Source: `docs/alpha_backlog/alpha_live_smoke_recovery_2026_05_24.md`

Status: `canonical_graph_recovery_tasks_complete`

Candidate review-risk report: `data/alpha_consumable_layer/alpha_v0/candidate_review_risk_report_alpha_v0.json`

Survey page-selection audit refs: `data/alpha_consumable_layer/alpha_v0/survey_page_selection_audit_refs_alpha_v0.json`

Route candidates default Alpha eligible: 72

Route candidates hard-blocked: 0

Survey audit ref count: 4228

## Survey Runtime Ingestion Alignment

Source: `data/alpha_consumable_layer/alpha_v0/survey_runtime_ingestion_alignment_alpha_v0.json`

Status: `aligned_with_survey_runtime_page_history`

Atlas-ingestable path: `survey_evidence_export.atlas_ingestable.evidence_atoms`

Must ignore path: `survey_evidence_export.construction_only_excluded`

Same-session displayed page history required: `true`

Apple exposure prior taste truth: `false`

Evidence strength hint policy: `survey_metadata_only_not_atlas_confidence`

dont_know mapping: `familiarity_uncertainty`

## Alpha 1 Fixed Survey Intake

Source: `data/alpha_consumable_layer/alpha_v0/alpha1_fixed_survey_intake_graph_support_alpha_v0.json`

Status: `capacity_pass_guardrails_enforced`

| surface | required pages | required tiles |
| --- | ---: | ---: |
| artist | 4 | 48 |
| album | 2 | 24 |
| song_recording | 4 | 48 |

Allowed buckets for fixed Alpha 1 intake: `page1_core`, `page2_adaptive`. Context-only families remain blocked.

## Alpha 1 First Mission Handoff

Source: `data/alpha_consumable_layer/alpha_v0/alpha1_first_mission_handoff_graph_contract_alpha_v0.json`

Status: `ready_for_core_app_integration_with_guardrails`

Route readiness: `route_ready_track_album_candidates`

Route-ready candidate count: 72

Track candidates: 50

Album candidates: 22

Artist-level route candidates: `false`

Resolves blocker: `MGN-I004`

Graph metadata taste truth: `false`

Atlas promotion created by graph handoff: `false`

## music_object_ref Alignment

Schema: `data/alpha_consumable_layer/alpha_v0/atlas_music_object_ref_alpha_v0.schema.json`

Adapter: `data/alpha_consumable_layer/alpha_v0/graph_to_atlas_music_object_ref_alpha_v0.md`

Examples: `data/alpha_consumable_layer/alpha_v0/atlas_music_object_ref_examples_alpha_v0.json`

Ref sources: `canonical_graph`, `user_local`, `external_catalog`, `unresolved`

Object types: `artist`, `album`, `song_recording`, `composition_placeholder`

Reference-only: `true`; taste truth: `false`; Atlas role truth: `false`; promotion from ref only: `false`.

## Included Families

| family_id | family_name |
| --- | --- |
| 1 | Early Rock, Oldies, Doo-Wop, Pre-Beatles Pop |
| 2 | Beatles, British Invasion, 60s Pop-Rock |
| 3 | Classic Rock, Album Rock, Progressive Rock |
| 4 | Singer-Songwriter, Folk, Americana, Adult Songcraft |
| 5 | Country |
| 6 | Soul, Funk, Disco, R&B Foundations |
| 7 | Hip-Hop |
| 8 | Punk, Hardcore, Post-Punk, New Wave |
| 9 | Metal and Heavy Music |
| 10 | Alternative, Indie, Grunge, Emo |
| 11 | Electronic, Dance, Club, Industrial, Experimental Pop |
| 12 | Pop Monoculture and Persona Pop |
| 13 | Latin, Caribbean, Global Pop |
| 14 | Jazz, Standards, Vocal, Classical-Adjacent |
| 16 | Christian, Worship, Gospel |
| 18 | Modern Rock, Current Discovery, Internet-Native Scenes |

## Excluded Families

| family_id | family_name | reason |
| --- | --- | --- |
| 15 | Soundtrack, Theater, Musicals, Family Context | context_only; fast_survey_allowed=false |
| 17 | Nostalgia, Novelty, Context, Shared Listening | context_only; fast_survey_allowed=false |

## Archetype Readiness

| readiness | count |
| --- | ---: |
| survey_ready | 100 |
| deep_only | 1 |
| adaptive_only | 11 |
| context_only | 8 |

Anchor-eligible archetypes: 100

Conditional probe/deep archetypes: 12

Context-only archetypes: 8

## Candidate Surface Counts

### artist

| bucket | count |
| --- | ---: |
| page1_core | 192 |
| page2_adaptive | 765 |
| page3_deep | 507 |
| suppressed_quarantined | 105 |

### album

| bucket | count |
| --- | ---: |
| page1_core | 192 |
| page2_adaptive | 679 |
| page3_deep | 319 |
| suppressed_quarantined | 42 |

### song_recording

| bucket | count |
| --- | ---: |
| page1_core | 192 |
| page2_adaptive | 780 |
| page3_deep | 602 |
| suppressed_quarantined | 375 |

## Version and Quarantine Counts

Quarantine queue rows: 107

Alpha blocklist rows: 1

Recording-version rows: 1917

### Apple Music resolution policy

| value | count |
| --- | ---: |
| exact_recording_required | 1857 |
| manual_review_required | 60 |

### Recording review status

| value | count |
| --- | ---: |
| approved | 1857 |
| quarantined | 38 |
| needs_review | 22 |

### Recording survey safety

| value | count |
| --- | ---: |
| true | 1857 |
| false | 60 |

## Forbidden Source Classes

- raw_family_rows
- raw_canonical_entity_tables
- merge_review_queue
- composition_review_queue
- hidden_simulation_truth
- raw_apple_music_payloads
- suppressed_quarantined_candidate_rows

## Alpha Use Rules

- page1: page1_core only
- page2: page2_adaptive only
- page3: page3_deep only
- raw_graph_rows: blocked
- quarantined_rows: blocked from survey, starter Atlas, default Mission Gen, app surfaces, Apple auto-resolution, OpenAI prompt payloads
- context_only_families: blocked from default first mission generation
- survey_response_semantics: provisional evidence only
- atlas_promotion_semantics: blocked until Atlas promotion logic owns decision
- alpha_candidate_blocklist: blocked from survey display, starter Atlas, default Mission Gen, Supabase active rows, OpenAI prompt payloads, and Apple auto-resolution
- music_object_ref: required for app/local candidate and tile payloads; reference-only, never user taste
- qa_exception_ledger: preserve warnings/manual-review rows as QA context; blocked rows do not feed product surfaces
- compact_candidate_pool: use helper output as curated candidate material only; user Survey/Atlas evidence must select/rank before Mission Generation

## Safe Send Gate

- supabase: only passing active candidate-pool rows with alpha_v0 contract version
- openai: only compact curated candidate pools, no raw graph, no hidden truth, no quarantined rows
