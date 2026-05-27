# Waymark Survey Completion to First Mission Batch Contract Alpha v0.1

Generated: 2026-05-22

Status: `OFFLINE_HANDOFF_READY_WITH_ROUTE_OBJECT_BLOCKER`

## Purpose

This contract defines the Mission Generation lane boundary for Alpha 1 after the 2026-05-22 product decisions.

First mission generation is triggered after required Survey completion. It is not bundled in the app, not generated locally in the app, and not allowed before visible Survey evidence exists.

## Trigger

The first-batch generation trigger is:

```text
privacy_terms_accepted
+ apple_identity_or_alpha_identity_ready
+ apple_music_authorization_attempted_or_recorded
+ onboarding_complete
+ required_alpha_survey_complete
+ survey_evidence_export_valid
-> generate_first_mission_batch
```

The app may show generation status language such as:

```text
building your Atlas
building your first missions
```

That language must remain provisional. It must not imply promoted Atlas truth.

## Allowed Inputs

The generation request may include:

- `client_request_id`
- `trusted_alpha_user_id` or `tester_alias`
- `requested_batch_size`
- `survey_evidence_export`
- `mission_generation_digest_view`
- `candidate_pool`
- `prompt_context`

For one-at-a-time ten-mission generation, `prompt_context` may include batch-memory fields:

- `already_selected_route_item_ids`
- `already_selected_candidate_ids`
- `already_selected_display_keys`
- `excluded_route_item_ids`
- `excluded_candidate_ids`

Allowed source material:

- Survey Evidence Export produced from user-visible Survey responses;
- MissionGenerationDigestView or AtlasDigestView derived from visible evidence;
- compact candidate pools from approved Alpha graph surfaces;
- anti-overfitting rules and candidate-role/risk metadata;
- app/storefront context needed for generation or MusicKit resolution planning.

## Prohibited Inputs

The request must not include:

- raw Survey construction logs;
- hidden simulator truth;
- fake profile labels;
- Profile Writer outputs;
- raw canonical graph rows;
- generator-private traces;
- promoted Atlas truth not present in the digest/read model;
- service-role keys, OpenAI keys, or other secrets.

## Generation Requirements

Default model:

```text
gpt-5.4-mini
```

Output must preserve:

- mission-as-experiment structure;
- source prompt and generation status;
- hypothesis and why-now;
- route logic;
- expected signal per item;
- feedback chips for the four primary reaction operations;
- conditional, mission-scoped possible Atlas update candidates;
- product status and app-import readiness;
- schema validation and audit metadata.

Generated missions must not:

- promote Atlas roles;
- mutate canonical graph;
- treat Apple exposure as taste truth;
- treat Survey taps as final verdicts;
- use unresolved/pseudo-playable route titles as app-ready mission items.
- use route items outside `candidate_pool.candidates`;
- use artist/title similarity as a substitute for exact `candidate_id` membership;
- repeat route item IDs, candidate IDs, or artist/title/type display identities inside a mission;
- repeat route items named in supplied batch-memory or exclusion fields.

## Status Semantics

The generation service and local harness should preserve these statuses:

| status | meaning | app behavior |
| --- | --- | --- |
| `generated` | A model output exists but has not cleared product/import review. | Do not import. |
| `product_review_needed` | Structurally useful, but needs review, repair, or resolution. | Do not import into normal Alpha path. |
| `blocked` | Schema, safety, resolution, or policy gate failed. | Do not import. |
| `app_import_candidate` | Product/import gates passed and app `mission.v0.2` payload is present. | Core may import through `MissionImportGate`. |
| `app_import_candidate_with_review_flags` | Alpha-only: Core/app validation passed, but review flags must be stored in diagnostics/audit. | Core may import only after trusted Alpha tolerance is implemented. |

Invariant:

```text
product_fail -> app_import_ready=false
```

## Backend Response Contract

The Supabase `generate-first-mission-batch` response shape is the current backend handoff target.

Required response fields:

- `run_id`
- `status`
- `prompt_version`
- `model`
- `adapter_version`
- `mission_output_schema_version`
- `app_mission_schema_version`
- `input_packet_sha256`
- `generation`
- `app_missions`
- `validation`
- `usage`
- `latency_ms`

Current hard response rule:

```text
app_missions must be non-empty only when status = app_import_candidate.
```

The app imports only `mission.v0.2` objects from `app_missions`, and only through Core's app-import gate.

Trusted Alpha recovery update:

```text
app_missions may also be non-empty when status = app_import_candidate_with_review_flags,
but only if app mission validation passes and alpha review flags are preserved in diagnostics/audit.
```

`review_needed`, `blocked`, and `failed` responses must still not be imported.

## App-Import Gate Compatibility

Current Core import requirements:

- `schema_version = mission.v0.2`;
- `mission_id` matches `MIS_[A-Z0-9_]+`;
- each route item has unique `ITEM_[A-Z0-9_]+`;
- each route item copies an exact candidate ID from the supplied route-ready candidate pool;
- no two route items share the same candidate ID or artist/title/type display identity;
- each route item is concrete enough to carry artist/title;
- each route item enters the app with `apple_music_resolution.status = unresolved`;
- each route item has `expected_test_signal`;
- each route item has `player_card.flip_side.song_hypothesis`;
- each route item has feedback chips for hit, partial, ok-shelf, and miss.

Mission Generation readiness policy:

```text
Route-ready risky/frontier/trap/waypoint review flags do not automatically make a mission non-importable for trusted Alpha. Hard blockers still do.
```

Hard blockers include:

- route item missing from `candidate_pool.candidates`;
- missing or non-pool `route.items[].candidate_id`;
- duplicate route item ID;
- duplicate route candidate ID;
- duplicate artist/title/type display identity;
- route item repeated from supplied first-batch memory/exclusion fields;
- pseudo-playable route title or unresolved candidate-search slot in an app-import candidate.

## Current Offline Fixture Status

Validated import-pipeline fixture:

```text
data/alpha_packets/golden_alpha_packet_v0_1/
```

This packet validates the Survey -> generation response -> app `mission.v0.2` import path, but it is not the final post-brand Alpha first batch because:

- it uses the older `candidate_pool_nirvana_to_current.json`;
- it applies a manual app-import review override;
- it predates the post-brand requirement that first missions are generated after required Survey completion.

Current `alpha_v0` candidate-pool retry:

```text
data/alpha_consumable_layer/alpha_v0/sample_compact_candidate_pool_alpha_v0.json
```

The retry now clears the Mission Generation gate: the route-ready pool contains concrete track/album candidates, and a live `gpt-5.4-mini` run using `MissionGenerationDigestView + alpha_v0 route-ready candidate pool` produced an `app_import_candidate` without a manual override.

Detailed readiness report:

```text
data/mission_generation/alpha_first_batch_readiness_v0_1/alpha_v0_candidate_pool_route_readiness_report.md
```

Passing generated artifact:

```text
data/mission_generation/alpha_first_batch_route_ready_v0_1/public_profile_01_A3_Al1_S2/20260523T225550Z/
```

## Minimum Needed To Clear Alpha First-Batch Import

Mission Generation can produce an Alpha first-batch import artifact when:

1. Candidate Pool Builder provides approved track/album route-item candidates with MusicKit search hints and candidate roles.
2. The generated rich mission passes schema validation and the product evaluator.
3. The rich mission adapts cleanly into Core `mission.v0.2`.

The safe output status remains:

```text
product_review_needed
```

unless all gates pass, in which case the safe output status is:

```text
app_import_candidate
```

For trusted Alpha recovery only, the service may return:

```text
app_import_candidate_with_review_flags
```

when the app mission validates and review flags are stored for PM/support inspection.
