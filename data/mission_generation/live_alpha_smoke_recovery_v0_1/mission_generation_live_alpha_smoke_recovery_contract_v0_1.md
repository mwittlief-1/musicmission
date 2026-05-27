# Waymark Mission Generation Live Alpha Smoke Recovery Contract v0.1

Generated: 2026-05-24

Status: `MISSION_POLICY_READY_INFRA_CORE_IMPLEMENTATION_NEEDED`

## Purpose

This note converts the live Alpha smoke findings into Mission Generation policy for first-batch generation.

The live path is real, but Alpha cannot freeze after one structurally valid `review_needed` response. Mission Generation should distinguish hard import blockers from review notes that are acceptable for trusted internal Alpha when Core validation and audit capture still pass.

## Trusted Alpha Status Semantics

| status | app missions allowed | meaning |
| --- | --- | --- |
| `blocked` | no | Generation failed schema, safety, resolution, hidden-truth, candidate, or app-import validation. Never import. |
| `review_needed` | no | A mission may be useful, but it is not app-importable without repair or human review. Continue attempts when possible. |
| `app_import_candidate` | yes | Mission clears Mission Generation, adapter, and Core app import gates without extra review flags. |
| `app_import_candidate_with_review_flags` | yes, Alpha only | Mission clears adapter and Core app import gates, but carries product review notes that must be stored in diagnostics/audit. |

`app_import_candidate_with_review_flags` is an Alpha-only response status. It is not a relaxation of mission validity. It exists so a trusted tester can keep moving when the model produces an app-valid mission with bounded review notes.

## Hard Blockers

Return `blocked` and do not include app missions when any of these are true:

- rich mission schema invalid;
- app `mission.v0.2` adaptation invalid;
- Core `MissionImportGate` would fail;
- any playable route item is a pseudo-item, unresolved candidate-search title, artist-only placeholder, or missing concrete artist/title;
- selected route item is not from the supplied candidate pool in candidate-constrained mode;
- selected candidate has graph/candidate quarantine, blocked review status, or missing route-ready eligibility;
- route requires manual MusicKit/version resolution before listening;
- hidden simulator truth, raw graph rows, raw Survey construction logs, Profile Writer output, or generator-private traces appear in mission-facing output;
- generated mission implies promoted Atlas truth or canonical graph mutation;
- `product_fail -> app_import_ready=true` or equivalent contradictory readiness appears.

## Alpha-Tolerable Review Flags

These can be imported only when the app mission validates and review flags are preserved in backend/client diagnostics:

- risky/frontier/trap/contradiction items correctly set `review_state.needs_human_review=true`;
- `review_config.requires_human_review=true` because the route should be inspected later, while `review_config.ready_for_app_import=true` because the mission is playable and bounded;
- release year is inferred from public catalog knowledge and marked with an uncertainty flag;
- Dead End or trap items are explicit bounded checks and positive trap chips use exception/reassess/cultural-furniture semantics;
- possible Atlas updates are conditional, mission-scoped, recurrence-gated, and review-required;
- the mission has product-review notes but no hard blocker.

Mission Generation prompt rule:

```text
Do not set review_config.ready_for_app_import=false solely because a valid route contains risky, frontier, trap, dead-end, waypoint, or contradiction review flags. Those flags are expected Alpha diagnostics. Set ready_for_app_import=false only for hard blockers or genuinely unresolved product questions that make the mission unsuitable for listening.
```

## Response Contract Recommendation

For trusted Alpha, backend responses should use:

```json
{
  "status": "app_import_candidate_with_review_flags",
  "app_import_status": "app_import_candidate_with_review_flags",
  "app_missions": [{ "...": "valid mission.v0.2 object" }],
  "validation": {
    "generation": { "valid": true },
    "app_mission": { "valid": true },
    "alpha_review_flags": ["..."]
  }
}
```

Core should still import only through `MissionImportGate`. Supabase should still persist raw status, review flags, validation, run ID, and adapter metadata. Normal tester UI should not expose raw run IDs, schemas, or review errors.

## 10-Mission Attempt Semantics

Alpha first-batch generation targets ten imported missions, not ten generation calls.

Recommended default:

```text
target_imported_missions = 10
max_generation_attempts = 14
```

Generation should continue after isolated `review_needed` or `app_import_candidate_with_review_flags` responses until one of these occurs:

- ten missions are imported;
- a hard `blocked` or `failed` condition indicates the request/context is unusable;
- the configured max-attempt ceiling is reached;
- auth, network, or privacy/account policy blocks the run.

Each one-at-a-time generation call should receive enough context to avoid near-duplicate missions:

- `batch_mission_index`;
- `batch_mission_total`;
- `attempt_index`;
- `max_generation_attempts`;
- `batch_seed`;
- `mission_portfolio_slot`;
- `mission_archetype`;
- `mission_objective`;
- `diversity_directive`;
- `prior_imported_mission_ids`;
- `prior_imported_candidate_ids`;
- `prior_attempt_summaries`;
- `prior_review_needed_reasons`.

## First-Batch Portfolio Coverage

Across the ten imported missions, the batch should cover at least:

- two safe/anchor or known-territory missions;
- two nearby-road or bridge missions;
- two frontier probes;
- one contradiction or dead-end check;
- one waypoint/useful-not-canon route;
- one wildcard/delight route;
- one flexible slot chosen from the strongest available Atlas/candidate signal.

One mission may satisfy multiple coverage labels, but the batch should not collapse into ten variants of the same safe route.

## Current Non-Dependent Prompt Repair

Mission Generation can immediately update prompt/evaluator guidance to reduce false review gates:

- route-ready candidates with expected item-level review flags may still be app-import candidates;
- app-import readiness should be blocked by concrete hard blockers, not by the mere presence of risk labels;
- missing route-ready candidate metadata remains a hard blocker;
- pseudo-playable route titles remain a hard blocker;
- Alpha review flags must be auditable, not hidden inside prose.

## Remaining Cross-Lane Implementation

Mission Generation defines the policy here. Supabase/Core own live response semantics, app import behavior, and diagnostic persistence.

No new generated or prebuilt missions should be bundled into the app.
