# Music Atlas Controller Implementation Plan v0.2

Date: 2026-05-16

## Review Request

This document is intended for independent PM/architecture review before deeper implementation continues.

Please review whether the plan below is faithful to the v0.2 kickoff packet, especially:

- the acceptance bar;
- the data model and export shape;
- how much can proceed while Apple Developer enrollment is pending;
- whether the proposed service boundaries are appropriate for a small private iOS spike;
- whether any requirement should be clarified before MusicKit catalog search, playback, or export work begins.

## PM Review Decisions

Status: accepted with minor clarifications.

The following decisions control the next implementation slice:

- Do not require `device_context.is_physical_device = true` in the JSON schema generally. Development/stub exports may set it to `false`; physical-device acceptance exports must set it to `true` and are validated by manual acceptance.
- Keep the v0.2 reaction enum as `hit`, `partial`, `ok_shelf`, `miss`, `slop`, `skipped`, `unresolved`.
- Treat future labels such as `more_like_this`, `dont_generalize`, and `too_soft` as reaction tags later, not v0.2 primary reactions.
- Store development/stub exports under `data/exports/dev/`.
- Store physical-device acceptance exports under `data/exports/acceptance/`.
- Stub/dev exports must clearly mark resolver/playback as stubbed or simulated and do not count as acceptance evidence.
- In-memory session state is acceptable for v0.2.
- Manual resolution is not required for v0.2 acceptance. The first pass may accept the top catalog result if the displayed metadata looks correct, but it must store candidate count, resolved metadata, confidence, storefront if available, resolver method, and failure/ambiguity status where applicable.

## Executive Summary

Music Atlas Controller is a private SwiftUI/MusicKit iOS spike. Its job is not to build the full Music Atlas. Its job is to prove one end-to-end discovery loop:

```text
Load sample mission -> resolve at least 1 Apple Music item -> play it on physical iPhone -> capture reaction/note -> export JSON + Markdown
```

The current repo now contains:

- the v0.2 kickoff packet under `docs/app_dev/kickoff_v0_2/`;
- canonical mission and schema JSON under `data/`;
- validation scripts under `scripts/`;
- a starter SwiftUI iOS project under `MusicAtlasController/`;
- bundled mission/schema resources inside the app target;
- starter mission, resolver, testing, export, and MusicKit authorization screens.

The Apple Developer account is pending. That blocks final MusicKit App ID/capability setup and physical-device acceptance, but it does not block local app architecture, UI state, mission loading, resolver state modeling, reaction capture, export generation, or validation utilities.

## Locked Scope

### v0.2 Acceptance Bar

The v0.2 spike succeeds when the app can:

1. Load `sample_mission_love_tributaries_v0_2.json`.
2. Display all 4 mission items.
3. Request and display Apple Music authorization status.
4. Resolve at least 1 mission item to an Apple Music catalog item.
5. Play that resolved item on a physical iPhone.
6. Capture one reaction value and one non-empty note.
7. Export JSON conforming to `schema_reaction_session_v0_2.json`.
8. Export readable Markdown.
9. Include top-level `reconciliation_status: "not_reconciled"` in JSON.

### Explicit Non-Goals

- Full graph visualization.
- Atlas canon updates.
- Spotify support.
- Cloud sync.
- Public onboarding.
- Social sharing.
- Playlist creation.
- Polished production UI.
- AI inference inside the app.

## Current Architecture

```text
MusicAtlasControllerApp
  |
  v
AppModel
  |-- MissionLoader
  |-- MusicAuthorizationService
  |-- future: MusicSearchService
  |-- future: MusicPlaybackService
  |-- future: SessionStore
  |-- future: SessionExporter
  |
  v
SwiftUI Views
  |-- MissionListView
  |-- MissionDetailView
  |-- ResolverStatusView
  |-- NowTestingView
  |-- ExportPreviewView
```

### Model Layer

The model layer mirrors the v0.2 JSON contracts closely:

- `Mission`
- `MissionItem`
- `AppleMusicResolution`
- `ReactionSession`
- `ItemResult`
- `PlaybackRecord`
- `ReactionRecord`
- `DeviceContext`
- `MusicContext`
- `ExportRecord`

The current implementation uses Swift `Codable` with snake_case coding keys. Dates decode as ISO-8601. This keeps app code aligned with the JSON schemas and avoids a second internal domain language too early.

### State Layer

`AppModel` is the single starter state object injected through the SwiftUI environment. That is intentionally simple for v0.2.

Planned state decomposition:

- `MissionState`: loaded mission, load errors, selected item.
- `AuthorizationState`: MusicKit authorization status.
- `ResolutionState`: per-item resolution records and catalog candidates.
- `PlaybackState`: queued/current item, playback status, playback errors.
- `ReactionState`: selected reaction, note text, timestamps.
- `ExportState`: generated JSON, Markdown, validation status, share/save result.

Recommendation: keep one `AppModel` facade for the views, but move behavior into small services/stores as each slice lands. Avoid introducing a full architecture framework for the spike.

### Service Layer

Services should be small and swappable:

- `MissionLoader`: loads bundled mission JSON.
- `MusicAuthorizationService`: wraps `MusicAuthorization`.
- `MusicSearchService`: searches Apple Music catalog and converts results into `AppleMusicResolution`.
- `MusicPlaybackService`: queues/plays one resolved catalog track through MusicKit.
- `ReactionStore`: holds reaction records for the current session.
- `SessionExporter`: creates schema-shaped reaction-session JSON and Markdown.
- `DeviceContextProvider`: supplies device model, OS version, app version, and physical-device flag.

Use protocols only where they unlock immediate testing or simulator fallback. For example, `MusicSearchServing` and `MusicPlaybackServing` are useful because MusicKit/device behavior is gated by account/capability setup. Do not protocol-wrap every small helper by default.

## Development Approach

### Principle 1: Build The Contracted Loop, Not The Product

Every implementation slice should map back to the locked v0.2 acceptance bar. If a feature does not help load, resolve, play, react, or export, defer it.

### Principle 2: Keep MusicKit Behind A Thin Boundary

MusicKit is the riskiest integration because it depends on signing, account state, storefront, subscription, and physical device behavior. The app should isolate MusicKit calls behind services so the rest of the UI/session/export work can proceed with stub or simulated data.

### Principle 3: Export Is The Source Of Value

The app is useful when it produces a clean discovery log. Export shape should be treated as a first-class acceptance artifact, not an afterthought after playback works.

### Principle 4: Prefer Strict Codable Validation In-App

The repo already validates JSON schemas through Python scripts. In-app validation should start with strict `Codable` decoding and domain checks:

- mission has at least 1 item;
- sample mission has 4 items;
- item IDs are present;
- resolution status is present;
- acceptance export has at least 1 resolved item;
- acceptance export has at least 1 played or playing item;
- acceptance export has at least 1 non-empty reaction note;
- `reconciliation_status` is `not_reconciled`.

Full JSON Schema validation inside Swift can be added later only if needed.

## Implementation Phases

### Phase 0: Repo Baseline - Done

Completed:

- Imported v0.2 kickoff packet.
- Added canonical data files and schema files.
- Added Python validation scripts.
- Added starter Xcode project and SwiftUI app.
- Added mission models and mission loader.
- Added starter views.
- Added MusicKit authorization service shell.
- Added `NSAppleMusicUsageDescription`.
- Verified sample mission schema validation.
- Verified sample mission decodes through Swift model.

### Phase 1: Mission UI And Local State

Goal: make the starter app pleasant and deterministic before MusicKit.

Tasks:

- Add selected mission item state.
- Let Mission Detail navigate into a single item view.
- Show item metadata, `why_included`, expected signal, resolution status, and notes.
- Add visible validation error states for mission load failures.
- Add a development-only "reload sample mission" action.

Acceptance:

- Simulator can load and browse all 4 mission items.
- Missing or invalid bundled mission produces a visible error.

### Phase 2: Resolver State Without Network Dependency

Goal: model resolution state before relying on live Apple Music search.

Tasks:

- Add `MusicSearchService` protocol.
- Add `StubMusicSearchService` for local development.
- Add `ResolverStore` or equivalent state in `AppModel`.
- Add per-item actions:
  - resolve;
  - mark skipped;
  - mark unavailable region;
  - mark unavailable subscription;
  - reset to unresolved.
- Store resolution metadata in the schema-compatible `AppleMusicResolution` shape.

Acceptance:

- In Simulator, one item can move from `unresolved` to `resolved` using stub data.
- Other items can remain unresolved/skipped with explicit reasons.

### Phase 3: Reaction And Session State

Goal: capture the acceptance-test reaction before real playback is complete.

Tasks:

- Add `ReactionStore`.
- Add reaction picker/buttons using schema enum:
  - `hit`;
  - `partial`;
  - `ok_shelf`;
  - `miss`;
  - `slop`;
  - `skipped`;
  - `unresolved`.
- Require non-empty note for acceptance export.
- Timestamp reaction saves.
- Tie reaction records to mission item IDs.

Acceptance:

- User can select a resolved/stubbed item, choose a reaction, enter a note, and save it.
- State persists for the current app session.

### Phase 4: Export Generation

Goal: generate valid `reaction_session.v0.2` JSON and readable Markdown before physical-device playback is available.

Tasks:

- Add `SessionExporter`.
- Add `DeviceContextProvider`.
- Add `MarkdownDiscoveryLogRenderer`.
- Generate filenames matching the v0.2 convention.
- Add Export Preview screen showing JSON and Markdown.
- Add save/share support if available without overcomplicating the spike.
- Add local export validation script examples in docs.

Acceptance:

- Stub-resolved/stub-played local session can export schema-valid JSON.
- Markdown includes mission title, item played/tested, reaction, note, resolution status, playback status, and reconciliation status.

### Phase 5: MusicKit Authorization And Capability Display

Goal: make account/device readiness explicit.

Tasks:

- Finalize `MusicAuthorizationService`.
- Display authorization status.
- Add playback capability status once the correct Apple APIs are available in Xcode.
- Add clear UI messaging for:
  - not determined;
  - denied;
  - restricted;
  - authorized;
  - no subscription/playback capability;
  - unknown/gated by signing.

Acceptance:

- On Simulator or unsigned state, app remains usable for non-MusicKit development.
- On real device after account approval, authorization can be requested and shown.

### Phase 6: Real Catalog Search

Goal: replace stub search with MusicKit catalog search.

Tasks:

- Implement `MusicSearchService` with MusicKit.
- Query by artist/title/album.
- Capture candidate count.
- Store storefront if available.
- Store catalog ID, resolved title, resolved artist, resolved album, confidence, resolver, and resolved timestamp.
- Show ambiguous choices if multiple credible results appear.

Acceptance:

- On real device, at least one sample item resolves to an Apple Music catalog item.
- Failed, ambiguous, unavailable, or skipped states have explicit reasons.

### Phase 7: Real Playback

Goal: play one resolved track on physical iPhone.

Tasks:

- Implement `MusicPlaybackService`.
- Queue/play a selected resolved catalog song.
- Record playback attempt timestamp.
- Record playing/played/failed status.
- Capture errors without crashing.
- Connect playback status to export.

Acceptance:

- At least one resolved item audibly plays on physical iPhone.
- Playback status is represented in `item_results`.

### Phase 8: Physical-Device Acceptance Evidence

Goal: preserve proof that the spike passed.

Tasks:

- Run the v0.2 manual acceptance script.
- Save exported JSON and Markdown.
- Note device model, iOS version, storefront/region, and MusicKit errors if any.
- Optionally promote a sanitized sample export into repo documentation.

Acceptance:

- Exported JSON validates against `schema_reaction_session_v0_2.json`.
- Exported Markdown is readable without parsing JSON.

## Pending Apple Developer Account Strategy

While Apple Developer enrollment is pending:

- continue Simulator/local UI work;
- use stubs for catalog resolution;
- use stubs for playback status;
- implement export generation and validation;
- avoid spending time on provisioning profile issues;
- keep real MusicKit calls isolated and guarded.

After account approval:

- set the real Apple Developer team in Xcode;
- confirm bundle identifier;
- enable MusicKit service for the App ID;
- ensure provisioning profile includes MusicKit;
- run on physical iPhone;
- replace/stress-test stubs with live MusicKit services.

## Export Evidence Rules

Acceptance exports:

- Must come from a physical iPhone.
- Must include `device_context.is_physical_device = true`.
- Must include top-level `reconciliation_status = "not_reconciled"`.
- Must validate against `schema_reaction_session_v0_2.json`.
- Must include at least one resolved item, one played item, one reaction, and one non-empty note.
- Belong under `data/exports/acceptance/` if preserved in the repo.

Development/stub exports:

- Are allowed.
- Belong under `data/exports/dev/`.
- Must clearly mark resolver/playback as stubbed or simulated.
- Do not count as acceptance evidence.

## Testing Strategy

### Existing Script Tests

```sh
python3 scripts/validate_mission_json.py
python3 scripts/validate_session_json.py data/exports/reaction_session_YYYYMMDD_HHMMSS.json
```

### Local Swift Checks

Until full Xcode build/test is available, use:

```sh
swiftc -parse-as-library -typecheck MusicAtlasController/MusicAtlasControllerApp.swift MusicAtlasController/Models/*.swift MusicAtlasController/Services/*.swift MusicAtlasController/Views/*.swift
```

### Future XCTest Coverage

Add tests for:

- mission decoding;
- invalid mission handling;
- resolution state transitions;
- reaction note requirement;
- export JSON encoding;
- Markdown rendering.

### Manual Acceptance

Use `docs/app_dev/kickoff_v0_2/Acceptance_Criteria_Test_Plan_v0_2.md`.

## Risk Register

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Apple Developer account pending | Blocks final MusicKit capability and device acceptance | Continue non-MusicKit slices with stubs |
| MusicKit catalog matching messy | Could resolve wrong track/remaster | Store candidate count, metadata, confidence, and allow manual choice |
| Subscription/storefront differences | Track may resolve but not play | Track unavailable statuses and storefront context |
| Simulator differs from device | False confidence | Physical iPhone required for acceptance |
| Export drifts from schema | Discovery logs lose value | Keep scripts and schema-shaped models central |
| UI grows beyond spike | Slows learning | Defer graph/product polish until acceptance loop passes |

## Proposed File Ownership

```text
MusicAtlasController/
  Models/
    Mission.swift
    ReactionSession.swift
  Services/
    MissionLoader.swift
    MusicAuthorizationService.swift
    MusicSearchService.swift        # next
    MusicPlaybackService.swift      # later
    ReactionStore.swift             # next
    SessionExporter.swift           # next
  Views/
    MissionListView.swift
    MissionDetailView.swift
    ResolverStatusView.swift
    NowTestingView.swift
    ExportPreviewView.swift
  Resources/
    sample_mission_love_tributaries_v0_2.json
    schema_mission_v0_2.json
    schema_reaction_session_v0_2.json
```

## Proposed Next Code Slice

If this plan is accepted, the next implementation slice should be:

1. Add selected item and resolver state.
2. Add stub resolver that can mark one sample item as resolved.
3. Add reaction capture tied to the selected item.
4. Add session export generation for stubbed local data.
5. Validate the generated JSON against `schema_reaction_session_v0_2.json`.

This creates a full local loop before live MusicKit is available.

## Review Questions

These are not blockers for the next local-code slice, but they are worth PM review:

1. Should the exported JSON schema require `device_context.is_physical_device = true` for acceptance exports, or should physical-device proof remain a manual acceptance criterion?
2. Should the v0.2 reaction enum stay as `hit`, `partial`, `ok_shelf`, `miss`, `slop`, `skipped`, `unresolved`, or should it restore earlier labels like `good`, `more_like_this`, and `dont_generalize`?
3. Should local stub-resolved exports be allowed in `data/exports/`, or should only real physical-device acceptance exports be preserved?
4. Should the app persist session state between launches in v0.2, or is in-memory state acceptable until playback works?
5. Should manual resolution be required for v0.2, or can the first acceptance pass rely on accepting the top catalog result?

## Product Backlog

### Feedback taxonomy alignment

Primary reaction labels such as `hit`, `partial`, `ok_shelf`/shelf, and `miss` should remain functionally stable and user-calibrated. The user-facing words may eventually become configurable aliases, but the app should avoid making primary reactions song-specific unless that is an explicit product decision.

Secondary feedback tags should be treated as contextual qualifiers. They may depend on the user, mission, song, selected primary reaction, or some combination of those factors. Examples include `more_like_this`, `dont_generalize`, `too_soft`, `wrong_version`, `bad_match`, `needs_replay`, and mission-specific signal tags.

Open questions before implementation:

1. Should exported primary reaction values remain canonical while UI labels become user-customizable aliases?
2. Is shelf functionally the same as `ok_shelf`, or should a future schema rename the canonical value?
3. Should secondary tag options depend on selected primary reaction, mission signal, specific song, or all three?
4. Should secondary tags be authored in mission packages, generated by the app, learned from user preferences, or edited during mission review?
5. Should resolver/problem tags such as `wrong_version` and `bad_match` live in the same tag system, or remain separate resolution issue flags?
6. Should secondary tags be optional during playback and finalized on a later Mission Review screen?

## Recommendation

Proceed with the local loop first: resolver state, reaction capture, export generation, and schema validation. Defer live catalog search and playback until the Apple Developer account and MusicKit App ID setup are ready.
