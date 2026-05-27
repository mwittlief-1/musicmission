# Closed-Loop Waymark First-Batch Simulation v0.1

- Generated at: `2026-05-21T17:52:05.764293Z`
- Run type: `live_api`
- Output root: `/Users/matt_wittlief_home/Documents/GitHub/musicmission/data/closed_loop_simulation/a3_first_batch_learning_v0_1_adaptive_contract_v0_1`
- Adaptive second-batch report: `/Users/matt_wittlief_home/Documents/GitHub/musicmission/waymark-ai-tests/reports/adaptive_second_batch_report_20260521T175205Z.md`
- Model for mission generation: `gpt-5.4-mini`
- Hidden simulator traces are evaluator-only and excluded from Atlas-facing payloads.

## Cost

- Estimated mission-generation cost: `$0.760868`

## Profile Summary

| Profile | First Batch | Signal Rate | Tag Rate | Atlas Signals | Second Batch | Status |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `profile_01_A3` | `True` | 0.611 | 0.273 | 18 | `True` | `closed_loop_pass` |
| `profile_05_A3` | `True` | 0.611 | 0.273 | 18 | `True` | `closed_loop_pass` |
| `profile_06_A3` | `True` | 0.611 | 0.273 | 18 | `True` | `closed_loop_pass` |

## Adaptive Second-Batch Summary

### profile_01_A3

- AtlasDelta actions: `{'deepen': 3, 'pivot': 1, 'retire_pause': 2}`
- Visibly adaptive missions: `6`
- Adaptation actions used: `{'deepen': 3, 'pivot': 1, 'retire_pause': 2}`
- Mission product status counts: `{'product_pass_candidate': 4, 'product_review_needed': 2}`

### profile_05_A3

- AtlasDelta actions: `{'retire_pause': 4, 'deepen': 1, 'pivot': 1}`
- Visibly adaptive missions: `6`
- Adaptation actions used: `{'deepen': 2, 'pivot': 3, 'retire_pause': 1}`
- Mission product status counts: `{'product_review_needed': 4, 'product_pass_candidate': 2}`

### profile_06_A3

- AtlasDelta actions: `{'deepen': 4, 'retire_pause': 1, 'dead_end_confirmation': 1}`
- Visibly adaptive missions: `6`
- Adaptation actions used: `{'deepen': 4, 'retire_pause': 1, 'contradiction_check': 1}`
- Mission product status counts: `{'product_pass_candidate': 6}`


## Acceptance Criteria Read

- Six first-batch missions per profile: checked in per-profile evaluations.
- Six second-batch missions per profile: checked in per-profile evaluations.
- Route items concrete or explicit candidate-search slots: checked in mission evaluations.
- Simulated feedback density: reported per profile.
- Hidden simulator truth excluded from Atlas-facing payload: enforced by separate artifact paths and payload construction.
- Atlas feedback ingested as Signals / PossibleAtlasUpdateCandidates / confidence deltas: written per profile.
- AtlasDelta generated after batch one and required by adaptive second-batch missions.
- Second-batch adaptivity evaluated separately from schema validity.
- No canonical graph mutation: `0` in update summaries.
- No automatic Atlas promotion: `0` in update summaries.

## Recommendation

`CLOSED_LOOP_REVIEW_READY`
