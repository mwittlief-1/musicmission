# Mission Construction Contract v0.2

Scope: convert approved mission opportunity blobs into offline Alpha mission packs that can become app-import candidates after playback resolution.

This contract keeps mission opportunity selection and mission construction separate. It does not generate production missions and does not mutate canonical graph truth.

## Universal Alpha Route Rules

- Default route size: 5-6 songs.
- A 3-song short mission is allowed only when intentionally marked short.
- Ordinary Alpha missions may not include unresolved/search-placeholder tracks.
- Every route item must include concrete music object refs sufficient for Apple Music resolution or pre-resolved playback metadata.
- Every mission needs a one-sentence explanation, hypothesis, route rationale, expected signal per item, risk level, and completion criteria.
- Every mission must produce enough evidence to answer what it taught us.

## Negative Budget

- Max 1 high-risk negative candidate by default.
- Max 2 only for boundary/correction-style missions.
- Never allow a route where the anchor fails the thesis and multiple probes are high risk.
- Never allow 3+ negative-risk items in a 6-song first-run Alpha mission.
- Diagnostic routes must not feel punitive.

## Source Purity

One coherent source opportunity is preferred. Mixed opportunities require `multi_source_route=true` and a clear explanation.

## Mission Type Readiness

| mission_type | alpha_auto_allowed | manual_only | deferred | rationale | Alpha constraint |
| --- | --- | --- | --- | --- | --- |
| `context_dependence_test` | yes | no | no | Clarify whether the listener responds to the music itself, the surrounding context, or both. | max negative risk 1 |
| `boundary_test` | yes | no | no | Find the edge between a known positive area and a nearby uncertain or mixed area without making the route punitive. | max negative risk 2 |
| `bridge_test` | yes | no | no | Test whether a known positive source area can carry into an under-tested target through a plausible path. | max negative risk 1 |
| `archetype_depth_test` | yes | no | no | Test whether the listener likes deeper or less obvious material inside an already promising archetype. | max negative risk 1 |
| `gateway_test` | yes | no | no | Use a low-risk entry point to introduce an under-tested family or archetype. | max negative risk 1 |
| `artist_depth_test` | no | yes | yes | Deferred for Alpha auto-import; requires stricter artist-specific construction before automation. | blocked from automatic Alpha import |
| `album_container_test` | no | yes | yes | Deferred for Alpha auto-import; requires stricter album-container construction before automation. | blocked from automatic Alpha import |
| `false_nearby_test` | no | yes | yes | Deferred for Alpha auto-import except manual review because the negative-risk profile is high. | blocked from automatic Alpha import |
| `evidence_repair_test` | no | yes | yes | Deferred for Alpha auto-import until repair-specific route policy exists. | blocked from automatic Alpha import |
| `exception_scope_test` | no | yes | yes | Deferred for Alpha auto-import until scope-isolation policy exists. | blocked from automatic Alpha import |

The machine-readable form is in `mission_construction_contract_v0_2.json`.
