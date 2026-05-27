# Closed-Loop Waymark First-Batch Simulation v0.1

- Generated at: `2026-05-21T15:52:43.555303Z`
- Run type: `live_api`
- Output root: `/Users/matt_wittlief_home/Documents/GitHub/musicmission/data/closed_loop_simulation/a3_first_batch_learning_v0_1`
- Model for mission generation: `gpt-5.4-mini`
- Hidden simulator traces are evaluator-only and excluded from Atlas-facing payloads.

## Cost

- Estimated mission-generation cost: `$0.760101`

## Profile Summary

| Profile | First Batch | Signal Rate | Tag Rate | Atlas Signals | Second Batch | Status |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `profile_01_A3` | `True` | 0.611 | 0.273 | 18 | `True` | `closed_loop_pass` |
| `profile_05_A3` | `True` | 0.611 | 0.273 | 18 | `True` | `closed_loop_pass` |
| `profile_06_A3` | `True` | 0.611 | 0.273 | 18 | `True` | `closed_loop_pass` |

## Acceptance Criteria Read

- Six first-batch missions per profile: checked in per-profile evaluations.
- Six second-batch missions per profile: checked in per-profile evaluations.
- Route items concrete or explicit candidate-search slots: checked in mission evaluations.
- Simulated feedback density: reported per profile.
- Hidden simulator truth excluded from Atlas-facing payload: enforced by separate artifact paths and payload construction.
- Atlas feedback ingested as Signals / PossibleAtlasUpdateCandidates / confidence deltas: written per profile.
- No canonical graph mutation: `0` in update summaries.
- No automatic Atlas promotion: `0` in update summaries.

## Recommendation

`CLOSED_LOOP_REVIEW_READY`
