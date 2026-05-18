# Music Atlas Controller App Dev Kickoff Packet v0.2

## Purpose

This v0.2 packet replaces the v0.1 app-dev kickoff packet for the first SwiftUI/MusicKit implementation spike.

It resolves the v0.1 conflicts and turns the package into an executable app-development brief. The target is a private/personal MVP, not a public consumer launch.

## Primary PM decisions now locked

1. **Initial success bar is a spike, not a full mission player.** The first spike succeeds when the app can load the included 4-item sample mission, resolve at least 1 Apple Music track, play that resolved track on a physical iPhone, capture one reaction plus a note, and export valid JSON plus readable Markdown.
2. **`reconciliation_status` is top-level.** It belongs at the top level of `reaction_session.json`, defaulting to `not_reconciled`. It is not nested under `mission_summary`.
3. **Schemas are intentionally tighter.** Mission items must include item IDs, item type, artist/title or album metadata, resolution status, and unresolved/skipped handling. Reaction-session exports must include timestamps, resolution metadata, reaction values, notes, and per-item skipped/unresolved status.
4. **MusicKit spike must run on a physical iPhone.** Simulator-only success is not accepted because authorization, subscription/playback, device account state, DRM, storefront, and playback behavior must be tested on real hardware.
5. **The app does not update the Atlas.** v0.2 writes discovery-session outputs only. Atlas reconciliation remains a later manual/AI review process.

## Package contents

- `README_AppDev_Kickoff_Packet_v0_2.md`
- `Music_Atlas_Controller_Product_Brief_v0_2.md`
- `MVP_Scope_Release_Spine_v0_2.md`
- `User_Flow_v0_2.md`
- `Data_Contracts_v0_2.md`
- `MusicKit_Technical_Spike_Brief_v0_2.md`
- `Repo_Structure_Codex_Dispatch_v0_2.md`
- `Acceptance_Criteria_Test_Plan_v0_2.md`
- `App_Dev_Launch_Prompt_v0_2.md`
- `schema_mission_v0_2.json`
- `schema_reaction_session_v0_2.json`
- `sample_mission_love_tributaries_v0_2.json`
- `discovery_log_template_v0_2.md`
- `CHANGELOG_v0_1_to_v0_2.md`

## First implementation backlog

### 1. Repo setup

- Create/open the iOS repo locally.
- Add this packet under `docs/app_dev/kickoff_v0_2/`.
- Add `data/missions/sample_mission_love_tributaries_v0_2.json`.
- Add `Schemas/mission.schema.json` and `Schemas/reaction_session.schema.json` or equivalent app-bundled resources.
- Add a first `README.md` explaining the private-spike goal.

### 2. Data contracts and validation

- Implement Codable models for mission and reaction session.
- Implement local JSON validation or strict Codable validation with explicit error messages.
- Load the sample mission from bundled JSON.
- Fail visibly if mission item IDs, item type, artist/title, or resolution status are missing.

### 3. SwiftUI skeleton

- Create minimal SwiftUI app with tabs or navigation stack:
  - Mission List
  - Mission Detail
  - Resolver
  - Now Testing
  - Export Preview
- No graph UI in the spike.

### 4. MusicKit authorization

- Configure app identifier/capability and Info.plist purpose string.
- Request MusicKit authorization.
- Display status: not determined, denied, restricted, authorized.
- Block playback attempts unless authorized.

### 5. Catalog search/resolution

- Use MusicKit catalog search to resolve mission items against Apple Music.
- Store resolution metadata per item.
- Support statuses: unresolved, resolved, ambiguous, skipped, unavailable_region, unavailable_subscription, failed.
- Initial acceptance requires at least 1 resolved item.

### 6. Playback spike

- Play at least 1 resolved Apple Music catalog track on a physical iPhone.
- Display current playback attempt/result.
- Capture playback errors without crashing.

### 7. Reaction capture

- For the played item, capture a reaction value and a note.
- Required reaction values: hit, partial, ok_shelf, miss, slop, skipped, unresolved.
- Store timestamps.

### 8. Export

- Export `reaction_session.json` conforming to schema v0.2.
- Export readable Markdown using `discovery_log_template_v0_2.md` structure.
- Ensure top-level `reconciliation_status = not_reconciled`.

### 9. Physical-device acceptance test

- Run on a signed physical iPhone with Apple Music installed/configured.
- Complete the acceptance script in `Acceptance_Criteria_Test_Plan_v0_2.md`.
- Save exported JSON and Markdown to repo/sample-output or local Files share.

## Source notes for MusicKit assumptions

This package is written for implementation planning, not as legal/App Review advice. It uses the following Apple developer references as the current technical baseline:

- MusicKit overview: https://developer.apple.com/musickit/
- MusicKit framework docs: https://developer.apple.com/documentation/MusicKit/
- MusicKit automatic token generation: https://developer.apple.com/documentation/musickit/using-automatic-token-generation-for-apple-music-api
- Apple Music API overview: https://developer.apple.com/documentation/applemusicapi/
- NSAppleMusicUsageDescription: https://developer.apple.com/documentation/bundleresources/information-property-list/nsapplemusicusagedescription
- Requesting access to Apple Music library: https://developer.apple.com/documentation/storekit/requesting-access-to-apple-music-library
- SKCloudServiceController / capabilities: https://developer.apple.com/documentation/storekit/skcloudservicecontroller
- MusicCatalogSearchRequest: https://developer.apple.com/documentation/musickit/musiccatalogsearchrequest
- MusicCatalogResourceRequest: https://developer.apple.com/documentation/musickit/musiccatalogresourcerequest
- MusicPlayer: https://developer.apple.com/documentation/musickit/musicplayer
- Create a new library playlist: https://developer.apple.com/documentation/applemusicapi/create-a-new-library-playlist
