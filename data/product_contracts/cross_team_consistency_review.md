# Cross-Team Consistency Review

Generated: 2026-05-20

Inputs reviewed:

- Canonical graph staging outputs under `data/canonical_graph/`
- Mission-team Atlas schema requirements from the product thread
- CEO note that user Atlas objects may not exist in the canonical graph
- Survey simulation spec: `/Users/matt_wittlief_home/Downloads/waymark_survey_simulation_harness_spec_v0_1.md`

## Bottom Line

The Survey, Mission, Atlas, and Canonical Graph directions are aligned.

The shared architecture should be:

```text
Canonical graph = shared music-object substrate
Survey simulator = evidence-gathering test harness
Atlas schema = user-specific interpretation layer
Mission generation = hypothesis/probe generator
Mission review = evidence-backed update proposal layer
```

No team is asking for the canonical graph to be mutated by Survey, Mission Generation, or Mission Review. That is the right boundary.

## Confirmed Shared Principles

- The graph asks good questions; user taps decide what is true.
- Apple Music payloads are a bias layer, not taste truth.
- Survey outputs create provisional evidence and seed state, not final Atlas truth.
- Mission Generation creates hypotheses, not promoted Atlas facts.
- Mission Review creates evidence and possible updates, not automatic promotions.
- Atlas state must remain auditable back to Signals.
- Candidate Pool Builder should consume Atlas role assignments, not raw music nodes.
- Canonical graph references should be used when available, but the Atlas must support user-local, imported, unresolved, and external music objects.

## Inconsistencies / Contract Risks

| issue | source | risk | recommended resolution |
|---|---|---|---|
| Canonical ID examples use prefixes like `artist_fleetwood-mac`, `album_rumours`, `song_dreams`. | Survey spec examples | Current canonical graph IDs are lowercase kebab canonical IDs without these generic prefixes. | Use typed `music_object_ref` fields. Keep simulator-local IDs separate from canonical IDs. |
| Survey reaction labels differ from current app/test labels. | Survey spec vs Swift tests | Simulator could drift from app state names. | Define a reaction normalization map between simulator labels and app/UI labels. |
| `dont_know_enough` is used for missing hidden-corpus entries. | Survey spec | This is valid in simulation, but production cannot know "missing from hidden corpus." | Preserve `hidden_lookup_status` only in simulator-private evaluation logs. Production-facing transcript should record user-visible `dont_know` / familiarity state. |
| Hidden `reason_tags` appear in `SurveyResponse`. | Survey spec | If exported to the visible transcript, this leaks fake-user ground truth to the Survey Builder or predictor. | Split hidden evaluation tags from observed user-selected tags. Only observed tags may enter Survey transcript, Atlas Signals, or predictor input. |
| `Canonical graph = candidate universe` conflicts with CEO note if read as product-wide truth. | Survey spec and CEO note | Could exclude non-canonical user library objects from Atlas design. | Scope this to simulator v0.1 candidate generation. Atlas v0.1 must support non-canonical refs. |
| `AtlasNode.atlas_roles` duplicates `AtlasRoleAssignment`. | Mission input | Role truth could be stored in two places. | Treat node roles on `AtlasNode` as optional denormalized summary only; `AtlasRoleAssignment` is authoritative. |
| `road` and `lineage` were initially listed as Atlas roles. | Mission input | Blurs role assignment with graph structures/views. | Model Road as a grouping/route structure and Lineage as edge/network view for v0.1. |
| `confidence`, `status`, `review_state`, and `promotion_state` appear in many places. | Mission input | Fields can collapse into ambiguous "truthiness." | Define shared confidence and lifecycle enums in Atlas schema contract. |
| Survey product-feel test emits starter Atlas and sample missions. | Survey spec | Could be mistaken for real Atlas writes. | Treat output as proposed seed Atlas state and sample mission briefs only. |

## Required Normalization Decisions Before Implementation

1. Define one `music_object_ref` union used by Survey, Atlas, Mission, and Candidate Pool Builder.
2. Define reaction enum mappings between simulator, app UI, Atlas Signals, and mission review.
3. Split simulator-private hidden data from visible survey transcript data.
4. Define confidence fields:
   - `confidence_score`
   - `confidence_band`
   - `confidence_basis`
5. Define lifecycle fields:
   - `status`
   - `review_state`
   - `promotion_state`
6. Define how non-canonical Apple/import objects are represented and resolved.

## Implementation Guidance

The next implementation work should split into two separate tracks:

- Survey Simulation Harness: read-only canonical graph consumer plus fake-user hidden evaluation data.
- Atlas Schema Contract v0.1: user interpretation schema with typed canonical and non-canonical music references.

The integration point between them is:

```text
Survey response/event -> Signal -> provisional Atlas update candidate
```

Do not let the simulator write promoted Atlas state directly.
