# Alpha v0 Candidate Pool Route Readiness Report

Generated: 2026-05-23

Status: `route_ready_candidate_pool_live_generation_passed`

## Purpose

Mission Generation previously blocked on `MGN-I004` because the `alpha_v0` candidate pool exposed only artist-level route candidates. Canonical Music Graph / Candidate Pool has now provided a route-ready pool with concrete track and album candidates.

Input candidate pool:

```text
data/alpha_consumable_layer/alpha_v0/sample_compact_candidate_pool_alpha_v0.json
```

Canonical resolution report:

```text
data/alpha_consumable_layer/alpha_v0/route_ready_candidate_pool_report_alpha_v0.json
```

Core app-import target:

```text
MusicAtlasController/Services/MissionLoader.swift
```

## Candidate Pool Summary

| pool | count | object types | mission role |
| --- | ---: | --- | --- |
| `anchors` | 12 | `track: 12` | anchor |
| `bridges` | 12 | `track: 12` | bridge |
| `probes` | 12 | `track: 3`, `album: 9` | probe |
| `boundary_probes` | 12 | `track: 12` | boundary/probe |
| `dead_end_checks` | 12 | `track: 11`, `album: 1` | trap/check |
| `waypoints` | 12 | `album: 12` | waypoint/context |

Total candidates reviewed: `72`

Route-ready track/album candidates found: `72`

Artist-level route candidates found: `0`

## Checks

| check | status | note |
| --- | --- | --- |
| Candidate pool loads | pass | JSON loads and has expected pool groups. |
| Candidate records are reviewed/eligible | pass | Sample rows carry `review_status=approved`, `eligible_for_supabase=true`, and `eligible_for_openai=true`. |
| Hidden taste truth excluded | pass | Pool states `graph_metadata_taste_truth=false` and `atlas_promotion_created=false`. |
| Route-level track/album objects available | pass | Populated candidate records are concrete `track` or `album` route items. |
| Waypoint route candidates available | pass | `waypoints` contains 12 album candidates. |
| Dead-end check candidates available | pass | `dead_end_checks` contains 12 candidates. |
| Core app-import candidate-pool boundary | pass | Pool now has concrete route items, and Mission Generation produced a rich-schema-valid `app_import_candidate` that maps to Core `mission.v0.2`. |

## Interpretation

`MGN-I004` is resolved for Candidate Pool and Mission Generation.

The rerun path now passes:

```text
MissionGenerationDigestView
+ route-ready alpha_v0 candidate pool
-> first-batch generation
-> rich mission schema validation
-> Core mission.v0.2 mapping validation
-> status=app_import_candidate
```

Latest passing live run:

```text
data/mission_generation/alpha_first_batch_route_ready_v0_1/public_profile_01_A3_Al1_S2/20260523T225550Z/
```

Run summary:

| field | value |
| --- | --- |
| model | `gpt-5.4-mini` |
| product status | `app_import_candidate` |
| rich mission schema valid | `true` |
| automated score | `1.0` |
| score pass / partial / fail | `24 / 0 / 0` |
| Core mission.v0.2 valid | `true` |
| estimated cost | `$0.178239` |
| latency | `37.821s` |

Generated mission:

```text
Start Here: Familiar Anchors, Nearby Roads
```

Selected route items are concrete route-ready candidates from the alpha pool:

- Led Zeppelin — `Stairway to Heaven`
- Pink Floyd — `Money`
- Dolly Parton — `Jolene`
- Al Green — `Let's Stay Together`
- Kraftwerk — `Autobahn`

## Remaining Boundaries

MusicKit catalog resolution is still required before playback.

The graph candidate pool does not create Atlas promotion.

Mission Generation must not fabricate mission objects from Atlas role summaries alone. It should use the route-ready candidate pool for concrete route items and the Atlas/MissionGenerationDigestView for user-specific interpretation context.

The current passing app-import candidate uses existing `A3_Al1_S2` fixtures. A true new-user Alpha 1 proof should rerun the same path once the fixed `A4_Al2_S4` Survey Evidence Export is available from Survey.

## Resolved Issue

```text
MGN-I004
```

Resolution evidence:

```text
data/alpha_consumable_layer/alpha_v0/route_ready_candidate_pool_report_alpha_v0.json
node scripts/validate_alpha_consumable_layer_alpha_v0.mjs
python3 scripts/run_alpha_first_batch_generation_v0_1.py --model gpt-5.4-mini --timeout-seconds 240
```
