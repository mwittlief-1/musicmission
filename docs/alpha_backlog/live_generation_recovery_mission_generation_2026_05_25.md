# Mission Generation Dispatch - Live Generation Recovery - 2026-05-25

## Mission

Harden the generation contract so OpenAI returns app-importable, candidate-constrained, diverse Alpha missions.

## Read First

- `docs/alpha_backlog/live_generation_recovery_dispatch_2026_05_25.md`
- `docs/infra/waymark_alpha_live_diagnostic_evidence_review_2026_05_25.md`
- `data/product_contracts/mission_generation_alpha_handoff_v0_1.md`
- `data/product_contracts/survey_completion_first_batch_generation_contract_alpha_v0_1.md`

## P0 Tasks

- [x] MGN-LGR-001 Tighten candidate-pool-only contract.
  - Output route items must come only from `candidate_pool.candidates`.
  - Digest/strong-region items are context, not a route-item source unless included in the candidate pool.
  - If no valid candidate fits, output a blocked/retry reason rather than inventing a route item.
  - Output: `data/mission_generation/live_generation_recovery_2026_05_25/mission_generation_route_identity_recovery_contract_v0_1.md`
  - Updated: `data/product_contracts/mission_generation_alpha_handoff_v0_1.md`, `data/product_contracts/survey_completion_first_batch_generation_contract_alpha_v0_1.md`, `waymark-ai-tests/fixtures/prompt_templates/mission_generator_candidate_constrained_v0_1.md`

- [x] MGN-LGR-002 Tighten uniqueness rules.
  - No duplicate route item IDs within a mission.
  - No duplicate title/artist/display identity within a mission.
  - Prefer no repeated route item across the 10-mission Alpha batch.
  - Added evaluator checks: `route_item_ids_unique`, `route_candidate_ids_unique`, `route_display_identity_unique`.
  - Supabase route identity validation blocks duplicate item IDs, duplicate candidate IDs, duplicate display identities, and exact candidate-pool misses.

- [x] MGN-LGR-003 Define batch-memory request field.
  - Propose the exact field shape for already-used route items, for example `excluded_item_ids` or `already_selected_route_item_ids`.
  - Specify whether the field lives in `prompt_context`, top-level request, or candidate-pool contract.
  - Keep it backward-compatible for one-mission calls.
  - Contract field placement: `prompt_context`.
  - Field shape:
    - `already_selected_route_item_ids: string[]`
    - `already_selected_candidate_ids: string[]`
    - `already_selected_display_keys: string[]`
    - `excluded_route_item_ids: string[]`
    - `excluded_candidate_ids: string[]`
  - Backward compatibility: omitted arrays mean one-mission behavior; supplied arrays become hard exclusions.

- [x] MGN-LGR-004 Add failure fixtures.
  - Duplicate route item fixture.
  - Non-candidate route item fixture.
  - Cross-batch repeat fixture if contract supports batch memory.
  - Expected result should be blocked or retry, not app import.
  - Existing duplicate fixture: `supabase/functions/generate-first-mission-batch/fixtures/duplicate_item_id/`
  - Added non-candidate fixture: `supabase/functions/generate-first-mission-batch/fixtures/non_candidate_item/`
  - Added batch-memory repeat fixture: `supabase/functions/generate-first-mission-batch/fixtures/batch_memory_repeat/`

- [x] MGN-LGR-005 Review prompt wording.
  - Ensure model instructions do not invite using familiar examples from broader digest context.
  - Explicitly require candidate IDs and concrete MusicKit-searchable route items.
  - Preserve Alpha language: evidence handoff, not promoted Atlas verdict.
  - Updated prompt language in the offline runner, reusable candidate-constrained template, and Supabase generation request packet.
  - Prompts now state that Survey/Atlas/digest/strong-region examples are context only and not playable route item sources.

## Acceptance

- The prompt/contract makes candidate-pool-only behavior unambiguous.
- Fixtures prove duplicate and non-candidate outputs fail validation.
- Batch-memory contract is ready for Core/Infrastructure implementation.
- Mission Generation can explain whether a bad output is prompt drift, validator gap, or candidate-pool construction issue.

## Blockers To Raise

| issue id | blocker | owner lane | needed for | current workaround | status |
| --- | --- | --- | --- | --- | --- |
| `MGN-LGR-I001` | Deploy the hardened `generate-first-mission-batch` route identity validator to live Supabase. | Supabase Infrastructure | Live Alpha run must block duplicate, non-candidate, and batch-memory-repeat route items before app import. | Local function, replay fixtures, and smoke test pass. | open |
| `MGN-LGR-I002` | Populate `prompt_context` batch-memory arrays during the live ten-mission generation loop. | Core / Supabase orchestration | Prevent repeated route items across the 10-mission Alpha batch. | Contract fields are defined and local validator blocks repeats when arrays are supplied. | open |

## Completion Note

- status: `mission_contract_hardened_local; live import fix depends on Supabase deploy and Core/Supabase batch-memory handoff`
- files changed:
  - `data/mission_generation/live_generation_recovery_2026_05_25/mission_generation_route_identity_recovery_contract_v0_1.md`
  - `data/product_contracts/mission_generation_alpha_handoff_v0_1.md`
  - `data/product_contracts/survey_completion_first_batch_generation_contract_alpha_v0_1.md`
  - `waymark-ai-tests/fixtures/prompt_templates/mission_generator_candidate_constrained_v0_1.md`
  - `waymark-ai-tests/src/waymark_ai_tests/score_output.py`
  - `scripts/run_alpha_first_batch_generation_v0_1.py`
  - `scripts/smoke_supabase_generate_first_mission_batch.mjs`
  - `supabase/functions/generate-first-mission-batch/index.ts`
  - `supabase/functions/generate-first-mission-batch/fixtures/non_candidate_item/`
  - `supabase/functions/generate-first-mission-batch/fixtures/batch_memory_repeat/`
- commands/tests run:
  - `python3 -m compileall -q waymark-ai-tests/src scripts/run_alpha_first_batch_generation_v0_1.py`
  - `python3 -m json.tool` on new Supabase fixture JSON files
  - `node scripts/smoke_supabase_generate_first_mission_batch.mjs`
  - scorer smoke snippet proving non-candidate and duplicate route outputs fail the tightened evaluator checks
  - `npx -y -p typescript tsc --noEmit --target ES2022 --lib ES2022,DOM --strict supabase/functions/generate-first-mission-batch/index.ts`
  - `git diff --check` on touched files
- live deploy or build number: not deployed by Mission lane
- remaining blockers: `MGN-LGR-I001`, `MGN-LGR-I002`
- handoff needed from: Supabase Infrastructure deploy; Core/Supabase orchestration batch-memory wiring
