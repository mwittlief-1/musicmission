# Candidate Role and Risk Vocabulary Alpha v0

Version: `alpha_v0`

Status: `frozen_for_alpha_consumable_layer`

This vocabulary defines the operational roles and risk classes allowed in app/local first mission candidate pools. These values guide Survey, Mission Generation, Supabase storage, and OpenAI prompt payloads. They do not create Atlas roles.

## Candidate Roles

| role | Use | OpenAI handling |
| --- | --- | --- |
| `anchor` | Safe route start or comparison point from strong survey evidence or `page1_core` recognition. | Use as a reference point, not a promoted Atlas Landmark. |
| `bridge` | Connects an anchor into an adjacent lane. | Explain the relationship being tested and keep inference scoped. |
| `probe` | Tests promising but uncertain territory. | Frame as experiment, not recommendation certainty. |
| `boundary_probe` | Tests a taste boundary or false-nearby edge. | Use sparingly; never treat negative response as final Dead End proof. |
| `dead_end_check` | Controlled trap/boundary item from dead-end probe candidates. | Never frame as standard recommendation. |
| `waypoint` | Useful support item, comfort object, or weak-positive bridge. | Do not promote to Atlas Waypoint without Atlas logic. |
| `palate_cleanser` | Low-risk spacing item inside a mission. | Avoid filler with no signal value. |
| `manual_review_only` | Useful but blocked until human review resolves risk. | Do not send to automatic OpenAI mission generation. |

## Candidate Pool Behavior Alignment

Atlas/Candidate Pool Builder behavior terms map to local Alpha mission roles this way:

| candidate_pool_behavior | local mission roles | Notes |
| --- | --- | --- |
| `anchor` | `anchor` | Operational anchor only; does not create an Atlas Landmark. |
| `bridge` | `bridge` | Connective test between known evidence and nearby territory. |
| `probe` | `probe` | Promising but uncertain test. |
| `risky_probe` | `boundary_probe` | False-nearby or boundary test; sparse and intentional. |
| `waypoint` | `waypoint`, `palate_cleanser` | Useful support/context candidate; does not create an Atlas Waypoint. |
| `trap` | `dead_end_check` | Dead-end check or negative-control probe; does not create an Atlas Dead End. |
| `exclude` | `manual_review_only` | Blocked from automatic Survey, Mission Generation, Supabase active rows, and OpenAI prompts. |
| `unknown` | none in final local pool | Upstream unresolved state only; must be mapped before OpenAI. |

## Risk Classes

| risk_class | Meaning | Supabase | OpenAI |
| --- | --- | --- | --- |
| `low` | Approved, survey-safe, unquarantined, clear identity, low version ambiguity. | allowed | allowed |
| `medium` | Approved and survey-safe, but requires careful inference or context caution. | allowed | allowed |
| `high` | Approved but sharp, irritating, overfit-prone, or boundary-heavy if used casually. | allowed | allowed only as `probe`, `boundary_probe`, or `dead_end_check` |
| `manual_review` | Potentially useful, but blocked until resolver/version/special-entity review. | blocked for active candidate rows | blocked |
| `blocked` | Suppressed, quarantined, context-only, unresolved, unsafe, or raw-graph-only. | blocked | blocked |

## Familiarity Assumptions

Allowed values:

- `known`
- `likely_known`
- `unknown`
- `likely_unknown`

These are assumptions for mission design, not user truth. User response and playback evidence must overwrite or qualify them.

## Source Mix Values

Allowed values:

- `apple_payload`
- `graph_core`
- `adaptive_bridge`
- `false_nearby_probe`
- `frontier_probe`
- `waypoint_context_probe`
- `negative_control_probe`
- `manual_concierge`

`apple_payload` means Apple helped bias selection or ordering. It does not mean Apple proved taste.

## Survey Page Roles

Allowed into Alpha candidate pools:

- `page1_core`
- `page2_adaptive`
- `page3_deep`

Blocked:

- `suppressed`
- `quarantined`
- `suppressed_quarantined`

## Atlas Boundary

Candidate roles are operational route-design hints. They are not Atlas roles.

Specifically:

- `anchor` does not create a Landmark.
- `waypoint` does not create a Waypoint.
- `boundary_probe` does not create a boundary truth.
- `dead_end_check` does not create a Dead End.
- Survey responses write provisional evidence only.
