# Cartenza Alpha Local Fixture Wiring Readiness v0.1

Decision: PASS

Can local fixture app wiring continue? Yes.

Can MusicKit resolution begin? Yes, through local fixture candidate staging.

Can TestFlight UAT begin? No. All approved local fixtures are still `app_import_candidate` and every route item is `candidate`, not `resolved`.

## What Changed

- Added an app-side `AlphaAppImportMissionPayloadV0_2` decoder/adapter.
- Added bundled local debug fixture resource `approved_alpha_app_import_candidates_v0_2.json`.
- Added local debug import from approved Alpha fixtures into reviewed mission assignments.
- Preserved Alpha mission types instead of collapsing them to legacy mission names.
- Added candidate/blocked resolution states for MusicKit resolution staging.
- Rendered mission type, brief, why-this-mission-now, risk, route role, route resolution status, expected signal, and why-in-route in mission detail.
- Added tests for approved fixture decode/import, revise/rejected filtering, mission type preservation, route order, role preservation, feedback mapping, candidate playback blocking, and mocked fully resolved playback readiness.

## Files Changed

- `MusicAtlasController/Models/AlphaAppImportMissionPayload.swift`
- `MusicAtlasController/Models/Mission.swift`
- `MusicAtlasController/Models/AppModel.swift`
- `MusicAtlasController/Services/MissionLoader.swift`
- `MusicAtlasController/Views/MissionListView.swift`
- `MusicAtlasController/Views/MissionDetailView.swift`
- `MusicAtlasController/Resources/approved_alpha_app_import_candidates_v0_2.json`
- `MusicAtlasControllerTests/MissionDecodingTests.swift`
- `MusicAtlasController.xcodeproj/project.pbxproj`

## Commands Run

```bash
plutil -lint MusicAtlasController.xcodeproj/project.pbxproj
python3 -m json.tool MusicAtlasController/Resources/approved_alpha_app_import_candidates_v0_2.json >/dev/null
xcodebuild test -project MusicAtlasController.xcodeproj -scheme MusicAtlasController -destination 'platform=iOS Simulator,name=iPhone 17,OS=26.5' -only-testing:MusicAtlasControllerTests/MissionDecodingTests
xcodebuild test -project MusicAtlasController.xcodeproj -scheme MusicAtlasController -destination 'platform=iOS Simulator,name=iPhone 17,OS=26.5'
```

## Test Results

- Project file lint: PASS.
- Approved fixture JSON parse: PASS.
- Targeted `MissionDecodingTests`: PASS, 24 tests.
- Full XCTest suite: PASS on iPhone 17 simulator, 74 tests.

Simulator evidence:

- Targeted result bundle: `~/Library/Developer/Xcode/DerivedData/MusicAtlasController-bfnmfzbsjxhgjggtptzlveersahw/Logs/Test/Test-MusicAtlasController-2026.05.29_11-32-29--0500.xcresult`
- Full suite result bundle: `~/Library/Developer/Xcode/DerivedData/MusicAtlasController-bfnmfzbsjxhgjggtptzlveersahw/Logs/Test/Test-MusicAtlasController-2026.05.29_11-34-07--0500.xcresult`

Screenshots were not captured in this slice; the proof is decoder/import/render model coverage plus successful simulator XCTest execution.

## Fixture Import Results

| mission_id | mission_type | decoded | shown_in_debug_import | route_count | candidate_items | resolved_items | blocked_reason |
| --- | --- | --- | --- | ---: | ---: | ---: | --- |
| `alpha-mission-v0-2-001-phase1g-public-profile-06-edge-heavy-200-context-dependence-test-mission-type-native-policy-v0-1` | `context_dependence_test` | yes | yes | 6 | 6 | 0 | music_resolution_pending |
| `alpha-mission-v0-2-002-phase1g-public-profile-06-edge-heavy-200-context-dependence-test-diagnostic-biased-policy-v0-1` | `context_dependence_test` | yes | yes | 6 | 6 | 0 | music_resolution_pending |
| `alpha-mission-v0-2-003-phase1g-public-profile-06-edge-heavy-200-boundary-test-experience-balanced-policy-v0-1` | `boundary_test` | yes | yes | 6 | 6 | 0 | music_resolution_pending |
| `alpha-mission-v0-2-004-phase1g-public-profile-05-song-heavy-200-boundary-test-mission-type-native-policy-v0-1` | `boundary_test` | yes | yes | 6 | 6 | 0 | music_resolution_pending |
| `alpha-mission-v0-2-005-phase1g-public-profile-06-edge-heavy-200-bridge-test-diagnostic-biased-policy-v0-1` | `bridge_test` | yes | yes | 6 | 6 | 0 | music_resolution_pending |
| `alpha-mission-v0-2-006-phase1g-public-profile-06-song-heavy-200-bridge-test-experience-balanced-policy-v0-1` | `bridge_test` | yes | yes | 6 | 6 | 0 | music_resolution_pending |
| `alpha-mission-v0-2-007-phase1g-public-profile-06-profile-weighted-balanced-200-archetype-depth-test-experience-balanced-policy-v0-1` | `archetype_depth_test` | yes | yes | 6 | 6 | 0 | music_resolution_pending |
| `alpha-mission-v0-2-008-phase1g-public-profile-05-song-heavy-200-archetype-depth-test-mission-type-native-policy-v0-1` | `archetype_depth_test` | yes | yes | 6 | 6 | 0 | music_resolution_pending |
| `alpha-mission-v0-2-009-phase1g-public-profile-06-song-heavy-200-context-dependence-test-mission-type-native-policy-v0-1` | `context_dependence_test` | yes | yes | 6 | 6 | 0 | music_resolution_pending |
| `alpha-mission-v0-2-010-phase1g-public-profile-06-song-heavy-200-context-dependence-test-diagnostic-biased-policy-v0-1` | `context_dependence_test` | yes | yes | 6 | 6 | 0 | music_resolution_pending |

## App Compatibility Results

| area | current state | change made | remaining gap | blocks local wiring? | blocks TestFlight? |
| --- | --- | --- | --- | --- | --- |
| mission model/types | legacy mission types plus existing `false_nearby_test` | added Alpha mission type cases and display labels | deferred types remain blocked from normal import | no | no |
| app-import payload | app expected legacy `mission.v0.2` shape | added Alpha payload decoder and adapter to app `Mission` | live backend still needs to emit or adapt to this contract | no | yes |
| local fixture import | paste/import path existed for reviewed/generated legacy missions | added debug-only bundled approved fixture import | not a production endpoint | no | no |
| route item model | had song/artist/expected signal but no Alpha route role | added optional Alpha route role/resolution/source trace fields | schema export compatibility for candidate status should be hardened later | no | yes |
| route card rendering | showed title/artist/why and debug resolution | now shows type, brief, why-now, risk, role, resolution status, expected signal | UI polish and dedicated debug validation screen still open | no | no |
| reaction mapping | app primary reactions map to four operations | documented/tested Love, Like, Ok/Keep, Dislike, Skip mapping | Wrong version/unavailable are not primary reaction buttons yet | no | no |
| MusicKit resolution | unresolved items were resolved in-app | candidate items now enter the same staging path and remain non-playback-ready | must resolve all candidate items to Apple IDs/URLs before UAT | no | yes |
| persistence/export | reviewed assignments and session state already persist | local fixture assignments persist as `local_alpha_fixture` | reaction-session schema should be extended before exporting candidate-state sessions | no | yes |

## Playback Readiness

| mission_id | total_items | resolved_items | candidate_items | unresolved_items | playback_ready | top_blocker |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| `alpha-mission-v0-2-001-phase1g-public-profile-06-edge-heavy-200-context-dependence-test-mission-type-native-policy-v0-1` | 6 | 0 | 6 | 0 | no | music_resolution_pending |
| `alpha-mission-v0-2-002-phase1g-public-profile-06-edge-heavy-200-context-dependence-test-diagnostic-biased-policy-v0-1` | 6 | 0 | 6 | 0 | no | music_resolution_pending |
| `alpha-mission-v0-2-003-phase1g-public-profile-06-edge-heavy-200-boundary-test-experience-balanced-policy-v0-1` | 6 | 0 | 6 | 0 | no | music_resolution_pending |
| `alpha-mission-v0-2-004-phase1g-public-profile-05-song-heavy-200-boundary-test-mission-type-native-policy-v0-1` | 6 | 0 | 6 | 0 | no | music_resolution_pending |
| `alpha-mission-v0-2-005-phase1g-public-profile-06-edge-heavy-200-bridge-test-diagnostic-biased-policy-v0-1` | 6 | 0 | 6 | 0 | no | music_resolution_pending |
| `alpha-mission-v0-2-006-phase1g-public-profile-06-song-heavy-200-bridge-test-experience-balanced-policy-v0-1` | 6 | 0 | 6 | 0 | no | music_resolution_pending |
| `alpha-mission-v0-2-007-phase1g-public-profile-06-profile-weighted-balanced-200-archetype-depth-test-experience-balanced-policy-v0-1` | 6 | 0 | 6 | 0 | no | music_resolution_pending |
| `alpha-mission-v0-2-008-phase1g-public-profile-05-song-heavy-200-archetype-depth-test-mission-type-native-policy-v0-1` | 6 | 0 | 6 | 0 | no | music_resolution_pending |
| `alpha-mission-v0-2-009-phase1g-public-profile-06-song-heavy-200-context-dependence-test-mission-type-native-policy-v0-1` | 6 | 0 | 6 | 0 | no | music_resolution_pending |
| `alpha-mission-v0-2-010-phase1g-public-profile-06-song-heavy-200-context-dependence-test-diagnostic-biased-policy-v0-1` | 6 | 0 | 6 | 0 | no | music_resolution_pending |

## Known Blockers

1. Apple Music IDs/URLs are absent in the approved fixtures, so none are `app_import_ready`.
2. Wrong-version and unavailable issue operations exist in the Alpha mapping, but the current primary reaction UI does not expose them as first-class buttons.
3. Candidate-state session export/schema compatibility should be hardened before exporting unresolved fixture sessions as evidence.
4. The local fixture import button is debug-only; live backend generation/import remains out of scope.

## Recommended Next Dispatch

Run the approved local fixtures through the MusicKit resolution path on a physical iPhone, attach Apple Music IDs/URLs where confidence is high, mark unresolvable items as blocked, and produce at least one fully resolved `app_import_ready` fixture for TestFlight playback smoke.

## Explicit Confirmations

- No live mission generation was implemented.
- No canonical graph truth was mutated.
- Revise/rejected fixtures are not imported into ordinary mission UI.
- Candidate items do not masquerade as playable.
- New mission types are preserved.
- TestFlight readiness is not claimed.
