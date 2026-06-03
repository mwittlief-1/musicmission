# Cartenza Alpha Autonomous Lane Backlog

Generated: 2026-05-21

This folder is the shared working backlog for the TestFlight Alpha lanes.

Tell every lane:

```text
Use docs/alpha_backlog/README.md as the master index. Open your lane file, complete any non-dependent tasks you can, edit checkboxes/statuses as you finish, and add issue rows when you hit a dependency owned by another lane.
```

## Broadcast Note

You can send this to every lane:

```text
Please read docs/alpha_backlog/alpha_live_smoke_recovery_2026_05_24.md first, then use the Alpha autonomous backlog at docs/alpha_backlog/README.md. Open your lane file, complete every non-dependent task you can, mark checkboxes as you go, and add a row to Raised Issues only when you hit a concrete dependency owned by another lane. New work is under "Live Alpha Smoke Recovery Tasks." Do not wait for me unless the backlog says the task is blocked or a product/account decision is required.
```

## Global Rule

The TestFlight app should not ship with prebuilt missions as user content.

Prebuilt missions are allowed only as test fixtures, debug fixtures, contract examples, golden packets, or harness artifacts. Production TestFlight user missions must arrive after install through a reviewed assignment/import path.

## Lane Files

| lane | file | current instruction |
| --- | --- | --- |
| Core Cartenza Build | `docs/alpha_backlog/core_waymark_build.md` | Build the missionless TestFlight runtime, mission assignment/import boundary, and Atlas-ingestion-ready evidence exports. |
| Canonical Music Graph | `docs/alpha_backlog/canonical_music_graph.md` | Freeze Alpha-safe graph surfaces, resolver policy, candidate-role metadata, and Atlas `music_object_ref` alignment. |
| Survey Simulator | `docs/alpha_backlog/survey_simulator.md` | Produce app-renderable survey packets and validated Survey Evidence Export into Atlas Schema v0.1. |
| Atlas Schema | `docs/alpha_backlog/atlas_schema.md` | Harden the first-pass contract into ingestion/read-model validators and unblock the other lanes. |
| Mission Generation / Closed-Loop Learning | `docs/alpha_backlog/mission_generation_closed_loop.md` | Produce reviewed first/adaptive mission-generation contracts, evaluator gates, and app-import handoff semantics without promoting Atlas truth. |
| Supabase / Infrastructure | `docs/alpha_backlog/supabase_infrastructure.md` | Stand up the thin backend for generation logs, OpenAI calls, mission adaptation, and future evidence upload. |

## Current Audit

Latest audit:

```text
docs/alpha_backlog/backlog_audit_2026_05_22.md
```

Latest live-smoke recovery packet:

```text
docs/alpha_backlog/alpha_live_smoke_recovery_2026_05_24.md
```

Latest live-generation recovery dispatch:

```text
docs/alpha_backlog/live_generation_recovery_dispatch_2026_05_25.md
```

Latest Apple Music raw signal payload alignment dispatch:

```text
docs/alpha_backlog/apple_music_signal_payload_v0_2_alignment_dispatch_2026_05_25.md
```

Latest Alpha follow-up dispatch packet:

```text
docs/alpha_backlog/alpha_followup_dispatch_packet_2026_05_25.md
```

Latest physical-device Build 14 feedback triage:

```text
docs/app_dev/testflight_build_14_feedback_triage_2026_05_25.md
```

Core return integration gate:

```text
docs/alpha_backlog/core_return_integration_acceptance_2026_05_24.md
```

## Status Convention

Use checkboxes for work state:

- `[ ]` not started
- `[x]` complete
- `[~]` in progress
- `[!]` issue raised or blocked

When a lane changes `[ ]` to `[x]`, it should add the artifact path or a short note on the next indented line.

Example:

```text
- [x] CWB-001 Add MissionProvider protocol.
  - Output: MusicAtlasController/Services/MissionProvider.swift
```

## Dependency Rule

Keep building until one of these is true:

- the task requires a missing contract field from another lane
- the task would force a product policy decision not yet made
- the task would risk promoted Atlas truth, raw graph leakage, hidden simulator leakage, or bundled mission content
- the task requires account credentials, Apple/Supabase project access, or external service configuration the lane does not have

When blocked, add a row to the lane's "Raised Issues" table using this shape:

| issue id | blocker | owner lane | needed for | current workaround | status |
| --- | --- | --- | --- | --- | --- |
| `CWB-I001` | Need final Survey page packet schema. | Survey Simulator | In-app survey renderer | Keep renderer behind fixture protocol. | open |

## Shared Source Contracts

Use these as current controlling inputs:

Waymark-named alpha briefs are historical contract artifacts. Cartenza is the current product name; do not rename those filenames without publishing replacement Cartenza contracts.

- `docs/alpha_lane_dispatch_packet_v0_1.md`
- `docs/alpha_testflight_infrastructure_plan_v0_1.md`
- `docs/app_dev/alpha_product_decision_addendum_2026_05_22.md`
- `docs/app_dev/brand_ui_review_playbook_v0_1.md`
- `docs/app_dev/mockups/alpha_orientation_flow_v0_1/README.md`
- `docs/app_dev/mockups/alpha_orientation_flow_v0_1/IMPLEMENTATION_HANDOFF.md`
- `docs/app_dev/core_live_auth_generation_dispatch_2026_05_22.md`
- `docs/infra/alpha_client_diagnostic_audit_trail_v0_1.md`
- `data/atlas_schema/atlas_schema_contract_v0_1.md`
- `data/atlas_schema/atlas_schema_contract_v0_1.json`
- `data/atlas_schema/atlas_delta_v0_1.md`
- `data/product_contracts/app_local_candidate_pool_contract_alpha_v0.md`
- `data/product_contracts/alpha_briefs/Waymark App and MusicKit Execution PM Alpha Brief v0.1.md`
- `data/product_contracts/alpha_briefs/Waymark Canonical Graph PM Alpha Brief v0.1.md`
- `data/product_contracts/alpha_briefs/waymark_survey_intelligence_pm_alpha_brief_v0_1.md`
- `data/product_contracts/alpha_briefs/Waymark Atlas PM Alpha Brief v0.1.md`
- `data/product_contracts/alpha_briefs/Waymark Mission Generation and Closed-Loop Learning PM Alpha Brief v0.1.md`
- `data/product_contracts/mission_generation_alpha_handoff_v0_1.md`
- `data/product_contracts/survey_completion_first_batch_generation_contract_alpha_v0_1.md`

## Cross-Lane Non-Negotiables

- Survey output is evidence, not final Atlas truth.
- Canonical Graph is substrate, not user taste.
- Atlas role truth lives in `AtlasRoleAssignment`, not `AtlasNode`.
- `Signal` is the durable evidence ledger.
- `PossibleAtlasUpdateCandidate` is a proposal, not an automatic promotion.
- `AtlasDigestView` is the read surface for Mission Generation, Candidate Pool Builder, WWTSF, and app-facing summaries.
- `AtlasDelta` is deterministic change substrate, not final copy.
- Apple Music data is exposure/resolution context, not taste truth.
- Hidden simulator truth, hidden reason tags, evaluator-only output, and generator-private payloads do not enter user-facing or Atlas-ingestable artifacts.
- Quarantined graph rows do not display in Survey, feed default mission generation, or auto-resolve through Apple Music.

## Current Cross-Lane Dependency Register

| dependency | owner | consumers | current status | build guidance |
| --- | --- | --- | --- | --- |
| Final Survey app packet schema | Survey Simulator | Core Cartenza, Atlas | frozen v0.1 | Core can build renderer against `waymark.alpha_survey_page_packet.v0.1`; Atlas should ingest only Survey Evidence Export v0.1. |
| Final app decision: Survey visible in first TestFlight | Product/Core | Core, Survey | decided_yes | Survey is required first-run intake after onboarding. |
| Supabase project ref and secrets | Product/Infrastructure | Core, Infrastructure | live_backend_ready | Project `ewuffhezhgyskcfyzkvw` is linked, functions are active, secrets are set, live generation/evidence smokes pass. Core should now wire app auth/function calls. |
| Promotion/demotion thresholds | Atlas/Product | All lanes | open | Build only provisional/candidate flows now. |
| Correction/superseding atom policy | Atlas | Survey, Core | open | Preserve append-only evidence and raise issue if amendment is needed. |
| Release/privacy copy and deletion policy | Release/Product | Core, Atlas, Infra | required | Privacy/terms gate is required before Survey/upload; copy still needed. |
| Final brand/app name/icon | Design/Release | Core | name_decided | App name is Cartenza; icon candidates still needed. |
| Approved Alpha orientation wireframes | Product/Design | Core | approved_2026_05_22 | Core/UI can implement from `docs/app_dev/mockups/alpha_orientation_flow_v0_1/IMPLEMENTATION_HANDOFF.md`; copy/legal/upload/icon blockers still apply. |
| App-facing "What Cartenza learned" placement | Product/Core/Atlas | Core, Atlas | open | Build `AtlasDelta` substrate and hide from UI until decided. |
| First-run Sign in with Apple + Apple Music | Product/Core/Infra | Core, Infra | core_live_auth_needed | Present as one guided step; implement as separate Supabase Auth and MusicKit capabilities. Current app is local-only for Apple ID; Core should use `docs/app_dev/core_live_auth_generation_dispatch_2026_05_22.md`. |
| Fixed Alpha Survey length | Product/Survey/Core | Survey, Core, Atlas | decided | 4 artist pages, 2 album pages, 4 song pages. |
| First mission batch after Survey | Product/Infra/Mission Generation | Core, Infra, Mission Generation, Atlas | backend_live_smoke_passed | No bundled missions; generate one batch after Survey completion. Backend live smoke returns `app_import_candidate`; Core must call it with the real Supabase session after Survey. |
| Evidence upload posture | Product/Infra/Release | Core, Infra, Atlas | decided_direction | Prefer Supabase upload/sync if safe; keep manual Share Evidence fallback. |
| Alpha visual mode/orientation | Product/Design/Core | Core | decided | Dark mode only; portrait-only. |
| Live Alpha import tolerance for `review_needed` | Product/Mission Generation/Infra/Core | Core, Infra, Mission Generation, Release QA | recommended_for_alpha | Trusted Alpha should not hard-stop after one structurally valid `review_needed` response. Import only app-valid missions, store review flags/audit rows, and continue generation attempts toward 10 missions. |
| Client-side audit trail | Core/Infra/Survey/Atlas | PM, Core, Survey, Mission Generation, Release QA | required_next | Add consent-gated diagnostic artifacts for Apple signal, Survey page selection, Survey export, mission request/result, app import result, and client errors. |
| Survey quarantine explanation | Survey/Core/Atlas | PM, Release QA, Mission Generation | required_next | Any quarantined Survey response should report a reason tied to displayed-page/session state so live runs can be reconstructed. |

## Update Cadence

Each lane should leave the file in a state another lane can read:

- completed tasks checked
- new artifacts listed
- blockers in the issue table
- assumptions called out near the task
- no silent contract drift
