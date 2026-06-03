Decision: PASS

Resolved missions: 6

Resolved route items: 36

Blocked route items: 2

Ambiguous route items: 0

First-UAT recommended mission count: 5

Can TestFlight smoke start? Yes

Top blocker: No bridge mission is resolved; bridge UAT waits on Trans-Siberian Orchestra track review.

Physical iPhone smoke notes: Not performed in this offline pass; promoted fixtures are ready for physical iPhone playback smoke.

# Alpha UAT Music Resolution Report v0.1

## Resolution Policy

- Source: bundled `canonical_apple_music_catalog_index_v1.json`.
- No live MusicKit, Apple Music, or catalog API calls were made.
- `candidate_verified` catalog-index entries are promoted only when title and artist match exactly and confidence is at least 0.85; they are reported as probable, not hidden as stronger evidence.
- `Christmas Eve/Sarajevo 12/24` remains blocked because the local track-level index has no clean generic-song match, despite album-sidecar nearby variants.
- PM-suspect mixed-source context routes `009` and `010` are excluded from first UAT promotion.

## Mission Results

| mission_id | mission_type | status | resolved_items | blocked_items | ambiguous_items | top_blocker |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `alpha-mission-v0-2-001-phase1g-public-profile-06-edge-heavy-200-context-dependence-test-mission-type-native-policy-v0-1` | `context_dependence_test` | promoted_app_import_ready | 6 | 0 | 0 | none |
| `alpha-mission-v0-2-002-phase1g-public-profile-06-edge-heavy-200-context-dependence-test-diagnostic-biased-policy-v0-1` | `context_dependence_test` | promoted_app_import_ready | 6 | 0 | 0 | none |
| `alpha-mission-v0-2-003-phase1g-public-profile-06-edge-heavy-200-boundary-test-experience-balanced-policy-v0-1` | `boundary_test` | promoted_app_import_ready | 6 | 0 | 0 | none |
| `alpha-mission-v0-2-004-phase1g-public-profile-05-song-heavy-200-boundary-test-mission-type-native-policy-v0-1` | `boundary_test` | promoted_app_import_ready | 6 | 0 | 0 | none |
| `alpha-mission-v0-2-005-phase1g-public-profile-06-edge-heavy-200-bridge-test-diagnostic-biased-policy-v0-1` | `bridge_test` | not_promoted | 5 | 1 | 0 | No track-level match in canonical Apple Music catalog index. |
| `alpha-mission-v0-2-006-phase1g-public-profile-06-song-heavy-200-bridge-test-experience-balanced-policy-v0-1` | `bridge_test` | not_promoted | 5 | 1 | 0 | No track-level match in canonical Apple Music catalog index. |
| `alpha-mission-v0-2-007-phase1g-public-profile-06-profile-weighted-balanced-200-archetype-depth-test-experience-balanced-policy-v0-1` | `archetype_depth_test` | promoted_app_import_ready | 6 | 0 | 0 | none |
| `alpha-mission-v0-2-008-phase1g-public-profile-05-song-heavy-200-archetype-depth-test-mission-type-native-policy-v0-1` | `archetype_depth_test` | promoted_app_import_ready | 6 | 0 | 0 | none |
| `alpha-mission-v0-2-009-phase1g-public-profile-06-song-heavy-200-context-dependence-test-mission-type-native-policy-v0-1` | `context_dependence_test` | not_promoted | 6 | 0 | 0 | pm_excluded_mixed_source_context_route |
| `alpha-mission-v0-2-010-phase1g-public-profile-06-song-heavy-200-context-dependence-test-diagnostic-biased-policy-v0-1` | `context_dependence_test` | not_promoted | 6 | 0 | 0 | pm_excluded_mixed_source_context_route |

## Item-Level Resolution

| mission_id | song | artist | match_status | confidence | wrong_version_risk | apple_music_id |
| --- | --- | --- | --- | ---: | --- | --- |
| `alpha-mission-v0-2-001-phase1g-public-profile-06-edge-heavy-200-context-dependence-test-mission-type-native-policy-v0-1` | `Bohemian Rhapsody` | Queen | verified | 0.95 | low | 1440650711 |
| `alpha-mission-v0-2-001-phase1g-public-profile-06-edge-heavy-200-context-dependence-test-mission-type-native-policy-v0-1` | `Just What I Needed` | The Cars | verified | 0.95 | low | 1088527515 |
| `alpha-mission-v0-2-001-phase1g-public-profile-06-edge-heavy-200-context-dependence-test-mission-type-native-policy-v0-1` | `Smooth Operator` | Sade | verified | 0.95 | low | 1524651263 |
| `alpha-mission-v0-2-001-phase1g-public-profile-06-edge-heavy-200-context-dependence-test-mission-type-native-policy-v0-1` | `Lose Yourself` | Eminem | verified | 0.95 | low | 1440903439 |
| `alpha-mission-v0-2-001-phase1g-public-profile-06-edge-heavy-200-context-dependence-test-mission-type-native-policy-v0-1` | `Man! I Feel Like a Woman!` | Shania Twain | probable | 0.86 | low | 1445668856 |
| `alpha-mission-v0-2-001-phase1g-public-profile-06-edge-heavy-200-context-dependence-test-mission-type-native-policy-v0-1` | `Fight the Power` | Public Enemy | verified | 0.95 | low | 1440838444 |
| `alpha-mission-v0-2-002-phase1g-public-profile-06-edge-heavy-200-context-dependence-test-diagnostic-biased-policy-v0-1` | `Bohemian Rhapsody` | Queen | verified | 0.95 | low | 1440650711 |
| `alpha-mission-v0-2-002-phase1g-public-profile-06-edge-heavy-200-context-dependence-test-diagnostic-biased-policy-v0-1` | `Just What I Needed` | The Cars | verified | 0.95 | low | 1088527515 |
| `alpha-mission-v0-2-002-phase1g-public-profile-06-edge-heavy-200-context-dependence-test-diagnostic-biased-policy-v0-1` | `Smooth Operator` | Sade | verified | 0.95 | low | 1524651263 |
| `alpha-mission-v0-2-002-phase1g-public-profile-06-edge-heavy-200-context-dependence-test-diagnostic-biased-policy-v0-1` | `Livin' on a Prayer` | Bon Jovi | verified | 0.95 | low | 1422955211 |
| `alpha-mission-v0-2-002-phase1g-public-profile-06-edge-heavy-200-context-dependence-test-diagnostic-biased-policy-v0-1` | `Man! I Feel Like a Woman!` | Shania Twain | probable | 0.86 | low | 1445668856 |
| `alpha-mission-v0-2-002-phase1g-public-profile-06-edge-heavy-200-context-dependence-test-diagnostic-biased-policy-v0-1` | `Fight the Power` | Public Enemy | verified | 0.95 | low | 1440838444 |
| `alpha-mission-v0-2-003-phase1g-public-profile-06-edge-heavy-200-boundary-test-experience-balanced-policy-v0-1` | `Livin' on a Prayer` | Bon Jovi | verified | 0.95 | low | 1422955211 |
| `alpha-mission-v0-2-003-phase1g-public-profile-06-edge-heavy-200-boundary-test-experience-balanced-policy-v0-1` | `Lose Yourself` | Eminem | verified | 0.95 | low | 1440903439 |
| `alpha-mission-v0-2-003-phase1g-public-profile-06-edge-heavy-200-boundary-test-experience-balanced-policy-v0-1` | `Fight the Power` | Public Enemy | verified | 0.95 | low | 1440838444 |
| `alpha-mission-v0-2-003-phase1g-public-profile-06-edge-heavy-200-boundary-test-experience-balanced-policy-v0-1` | `Smooth Operator` | Sade | verified | 0.95 | low | 1524651263 |
| `alpha-mission-v0-2-003-phase1g-public-profile-06-edge-heavy-200-boundary-test-experience-balanced-policy-v0-1` | `How Will I Know` | Whitney Houston | verified | 0.95 | low | 1784790781 |
| `alpha-mission-v0-2-003-phase1g-public-profile-06-edge-heavy-200-boundary-test-experience-balanced-policy-v0-1` | `Sexual Healing` | Marvin Gaye | verified | 0.95 | low | 158539332 |
| `alpha-mission-v0-2-004-phase1g-public-profile-05-song-heavy-200-boundary-test-mission-type-native-policy-v0-1` | `DNA.` | Kendrick Lamar | verified | 0.95 | low | 1440881357 |
| `alpha-mission-v0-2-004-phase1g-public-profile-05-song-heavy-200-boundary-test-mission-type-native-policy-v0-1` | `Respect` | Aretha Franklin | verified | 0.95 | low | 937107838 |
| `alpha-mission-v0-2-004-phase1g-public-profile-05-song-heavy-200-boundary-test-mission-type-native-policy-v0-1` | `Closer` | Nine Inch Nails | verified | 0.95 | low | 1440837621 |
| `alpha-mission-v0-2-004-phase1g-public-profile-05-song-heavy-200-boundary-test-mission-type-native-policy-v0-1` | `Celebration` | Kool & The Gang | verified | 0.95 | low | 1431062029 |
| `alpha-mission-v0-2-004-phase1g-public-profile-05-song-heavy-200-boundary-test-mission-type-native-policy-v0-1` | `m.A.A.d city` | Kendrick Lamar feat. MC Eiht | verified | 0.95 | low | 1471263912 |
| `alpha-mission-v0-2-004-phase1g-public-profile-05-song-heavy-200-boundary-test-mission-type-native-policy-v0-1` | `Public Image` | Public Image Ltd | verified | 0.95 | low | 1809861697 |
| `alpha-mission-v0-2-005-phase1g-public-profile-06-edge-heavy-200-bridge-test-diagnostic-biased-policy-v0-1` | `Man! I Feel Like a Woman!` | Shania Twain | probable | 0.86 | low | 1445668856 |
| `alpha-mission-v0-2-005-phase1g-public-profile-06-edge-heavy-200-bridge-test-diagnostic-biased-policy-v0-1` | `Fight the Power` | Public Enemy | verified | 0.95 | low | 1440838444 |
| `alpha-mission-v0-2-005-phase1g-public-profile-06-edge-heavy-200-bridge-test-diagnostic-biased-policy-v0-1` | `Christmas Eve/Sarajevo 12/24` | Trans-Siberian Orchestra | not_found | 0.00 | high |  |
| `alpha-mission-v0-2-005-phase1g-public-profile-06-edge-heavy-200-bridge-test-diagnostic-biased-policy-v0-1` | `Alice's Restaurant Massacree` | Arlo Guthrie | verified | 0.95 | low | 41229186 |
| `alpha-mission-v0-2-005-phase1g-public-profile-06-edge-heavy-200-bridge-test-diagnostic-biased-policy-v0-1` | `Smooth Operator` | Sade | verified | 0.95 | low | 1524651263 |
| `alpha-mission-v0-2-005-phase1g-public-profile-06-edge-heavy-200-bridge-test-diagnostic-biased-policy-v0-1` | `Why` | Frankie Avalon | verified | 0.95 | low | 1423249862 |
| `alpha-mission-v0-2-006-phase1g-public-profile-06-song-heavy-200-bridge-test-experience-balanced-policy-v0-1` | `Bohemian Rhapsody` | Queen | verified | 0.95 | low | 1440650711 |
| `alpha-mission-v0-2-006-phase1g-public-profile-06-song-heavy-200-bridge-test-experience-balanced-policy-v0-1` | `Smooth Operator` | Sade | verified | 0.95 | low | 1524651263 |
| `alpha-mission-v0-2-006-phase1g-public-profile-06-song-heavy-200-bridge-test-experience-balanced-policy-v0-1` | `Fight the Power` | Public Enemy | verified | 0.95 | low | 1440838444 |
| `alpha-mission-v0-2-006-phase1g-public-profile-06-song-heavy-200-bridge-test-experience-balanced-policy-v0-1` | `Lose Yourself` | Eminem | verified | 0.95 | low | 1440903439 |
| `alpha-mission-v0-2-006-phase1g-public-profile-06-song-heavy-200-bridge-test-experience-balanced-policy-v0-1` | `Christmas Eve/Sarajevo 12/24` | Trans-Siberian Orchestra | not_found | 0.00 | high |  |
| `alpha-mission-v0-2-006-phase1g-public-profile-06-song-heavy-200-bridge-test-experience-balanced-policy-v0-1` | `Man! I Feel Like a Woman!` | Shania Twain | probable | 0.86 | low | 1445668856 |
| `alpha-mission-v0-2-007-phase1g-public-profile-06-profile-weighted-balanced-200-archetype-depth-test-experience-balanced-policy-v0-1` | `Bohemian Rhapsody` | Queen | verified | 0.95 | low | 1440650711 |
| `alpha-mission-v0-2-007-phase1g-public-profile-06-profile-weighted-balanced-200-archetype-depth-test-experience-balanced-policy-v0-1` | `Lose Yourself` | Eminem | verified | 0.95 | low | 1440903439 |
| `alpha-mission-v0-2-007-phase1g-public-profile-06-profile-weighted-balanced-200-archetype-depth-test-experience-balanced-policy-v0-1` | `Fight the Power` | Public Enemy | verified | 0.95 | low | 1440838444 |
| `alpha-mission-v0-2-007-phase1g-public-profile-06-profile-weighted-balanced-200-archetype-depth-test-experience-balanced-policy-v0-1` | `Livin' on a Prayer` | Bon Jovi | verified | 0.95 | low | 1422955211 |
| `alpha-mission-v0-2-007-phase1g-public-profile-06-profile-weighted-balanced-200-archetype-depth-test-experience-balanced-policy-v0-1` | `Only Shallow` | My Bloody Valentine | verified | 0.95 | low | 1589230439 |
| `alpha-mission-v0-2-007-phase1g-public-profile-06-profile-weighted-balanced-200-archetype-depth-test-experience-balanced-policy-v0-1` | `Not Strong Enough` | boygenius | verified | 0.95 | low | 1666138718 |
| `alpha-mission-v0-2-008-phase1g-public-profile-05-song-heavy-200-archetype-depth-test-mission-type-native-policy-v0-1` | `DNA.` | Kendrick Lamar | verified | 0.95 | low | 1440881357 |
| `alpha-mission-v0-2-008-phase1g-public-profile-05-song-heavy-200-archetype-depth-test-mission-type-native-policy-v0-1` | `Public Image` | Public Image Ltd | verified | 0.95 | low | 1809861697 |
| `alpha-mission-v0-2-008-phase1g-public-profile-05-song-heavy-200-archetype-depth-test-mission-type-native-policy-v0-1` | `Fight the Power` | Public Enemy | verified | 0.95 | low | 1440838444 |
| `alpha-mission-v0-2-008-phase1g-public-profile-05-song-heavy-200-archetype-depth-test-mission-type-native-policy-v0-1` | `Not Strong Enough` | boygenius | verified | 0.95 | low | 1666138718 |
| `alpha-mission-v0-2-008-phase1g-public-profile-05-song-heavy-200-archetype-depth-test-mission-type-native-policy-v0-1` | `B.O.B.` | OutKast | verified | 0.95 | low | 255837382 |
| `alpha-mission-v0-2-008-phase1g-public-profile-05-song-heavy-200-archetype-depth-test-mission-type-native-policy-v0-1` | `Money (That's What I Want)` | Barrett Strong | verified | 0.95 | low | 1445297290 |
| `alpha-mission-v0-2-009-phase1g-public-profile-06-song-heavy-200-context-dependence-test-mission-type-native-policy-v0-1` | `Fight the Power` | Public Enemy | verified | 0.95 | low | 1440838444 |
| `alpha-mission-v0-2-009-phase1g-public-profile-06-song-heavy-200-context-dependence-test-mission-type-native-policy-v0-1` | `Bohemian Rhapsody` | Queen | verified | 0.95 | low | 1440650711 |
| `alpha-mission-v0-2-009-phase1g-public-profile-06-song-heavy-200-context-dependence-test-mission-type-native-policy-v0-1` | `Lose Yourself` | Eminem | verified | 0.95 | low | 1440903439 |
| `alpha-mission-v0-2-009-phase1g-public-profile-06-song-heavy-200-context-dependence-test-mission-type-native-policy-v0-1` | `Livin' on a Prayer` | Bon Jovi | verified | 0.95 | low | 1422955211 |
| `alpha-mission-v0-2-009-phase1g-public-profile-06-song-heavy-200-context-dependence-test-mission-type-native-policy-v0-1` | `Man! I Feel Like a Woman!` | Shania Twain | probable | 0.86 | low | 1445668856 |
| `alpha-mission-v0-2-009-phase1g-public-profile-06-song-heavy-200-context-dependence-test-mission-type-native-policy-v0-1` | `Under the Milky Way` | The Church | verified | 0.95 | low | 303081981 |
| `alpha-mission-v0-2-010-phase1g-public-profile-06-song-heavy-200-context-dependence-test-diagnostic-biased-policy-v0-1` | `Fight the Power` | Public Enemy | verified | 0.95 | low | 1440838444 |
| `alpha-mission-v0-2-010-phase1g-public-profile-06-song-heavy-200-context-dependence-test-diagnostic-biased-policy-v0-1` | `Bohemian Rhapsody` | Queen | verified | 0.95 | low | 1440650711 |
| `alpha-mission-v0-2-010-phase1g-public-profile-06-song-heavy-200-context-dependence-test-diagnostic-biased-policy-v0-1` | `Livin' on a Prayer` | Bon Jovi | verified | 0.95 | low | 1422955211 |
| `alpha-mission-v0-2-010-phase1g-public-profile-06-song-heavy-200-context-dependence-test-diagnostic-biased-policy-v0-1` | `Fun, Fun, Fun` | The Beach Boys | verified | 0.95 | low | 728254965 |
| `alpha-mission-v0-2-010-phase1g-public-profile-06-song-heavy-200-context-dependence-test-diagnostic-biased-policy-v0-1` | `Smooth Operator` | Sade | verified | 0.95 | low | 1524651263 |
| `alpha-mission-v0-2-010-phase1g-public-profile-06-song-heavy-200-context-dependence-test-diagnostic-biased-policy-v0-1` | `I Wanna Dance with Somebody` | Whitney Houston | probable | 0.86 | low | 840431935 |
