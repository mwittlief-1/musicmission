# First UAT Fixture Recommendation v0.1

Recommended first UAT set: **5 missions / 30 route items**.

The promoted fixture file contains 6 fully resolved missions. For the first smoke pass, start with the five-mission primary set below to cover context dependence, boundary, and archetype depth while avoiding the blocked bridge routes and PM-suspect context routes `009`/`010`.

## Primary First-UAT Set

| mission_id | mission_type | route_items | status |
| --- | --- | ---: | --- |
| `alpha-mission-v0-2-001-phase1g-public-profile-06-edge-heavy-200-context-dependence-test-mission-type-native-policy-v0-1` | `context_dependence_test` | 6 | app_import_ready |
| `alpha-mission-v0-2-003-phase1g-public-profile-06-edge-heavy-200-boundary-test-experience-balanced-policy-v0-1` | `boundary_test` | 6 | app_import_ready |
| `alpha-mission-v0-2-004-phase1g-public-profile-05-song-heavy-200-boundary-test-mission-type-native-policy-v0-1` | `boundary_test` | 6 | app_import_ready |
| `alpha-mission-v0-2-007-phase1g-public-profile-06-profile-weighted-balanced-200-archetype-depth-test-experience-balanced-policy-v0-1` | `archetype_depth_test` | 6 | app_import_ready |
| `alpha-mission-v0-2-008-phase1g-public-profile-05-song-heavy-200-archetype-depth-test-mission-type-native-policy-v0-1` | `archetype_depth_test` | 6 | app_import_ready |

## Resolved Alternate

| mission_id | mission_type | route_items | status |
| --- | --- | ---: | --- |
| `alpha-mission-v0-2-002-phase1g-public-profile-06-edge-heavy-200-context-dependence-test-diagnostic-biased-policy-v0-1` | `context_dependence_test` | 6 | resolved alternate |

## Blocked From First UAT

- Bridge routes `005` and `006` remain blocked by unresolved `Christmas Eve/Sarajevo 12/24` track-level matching.
- Context routes `009` and `010` remain excluded by PM decision because they are mixed-source context routes.

## Smoke Recommendation

Can TestFlight smoke start? **Yes**

Use the primary set first. Keep the resolved alternate as a controlled second context-dependence option if PM wants a six-mission pass.
