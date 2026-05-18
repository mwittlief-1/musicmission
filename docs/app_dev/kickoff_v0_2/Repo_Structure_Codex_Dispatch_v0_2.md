# Repo Structure + Codex Dispatch v0.2

## Recommended repo structure

```text
music-atlas-controller/
  README.md
  docs/
    app_dev/
      kickoff_v0_2/
        README_AppDev_Kickoff_Packet_v0_2.md
        Music_Atlas_Controller_Product_Brief_v0_2.md
        MVP_Scope_Release_Spine_v0_2.md
        User_Flow_v0_2.md
        Data_Contracts_v0_2.md
        MusicKit_Technical_Spike_Brief_v0_2.md
        Repo_Structure_Codex_Dispatch_v0_2.md
        Acceptance_Criteria_Test_Plan_v0_2.md
        App_Dev_Launch_Prompt_v0_2.md
        CHANGELOG_v0_1_to_v0_2.md
    discovery_log/
      README.md
  data/
    missions/
      sample_mission_love_tributaries_v0_2.json
    schemas/
      schema_mission_v0_2.json
      schema_reaction_session_v0_2.json
    exports/
      .gitkeep
  MusicAtlasController/
    MusicAtlasControllerApp.swift
    Models/
    Services/
    Views/
    Resources/
      sample_mission_love_tributaries_v0_2.json
      schema_mission_v0_2.json
      schema_reaction_session_v0_2.json
  tests/
    README.md
```

## First implementation backlog

### 1. Repo setup

- Place v0.2 packet under `docs/app_dev/kickoff_v0_2/`.
- Place schemas and sample mission under `data/`.
- Initialize SwiftUI iOS project if not already present.
- Add resources to the app target.

### 2. Data contracts and validation

- Create `Mission`, `MissionItem`, `AppleMusicResolution`, `ReactionSession`, `ItemResult`, `Reaction` Codable models.
- Load sample mission.
- Fail gracefully on missing required fields.
- Add minimal validation tests for the sample mission.

### 3. SwiftUI skeleton

- Mission list.
- Mission detail.
- Resolver status view.
- Now Testing/player view.
- Export preview.

### 4. MusicKit authorization

- Add Info.plist `NSAppleMusicUsageDescription`.
- Add MusicKit capability/configuration.
- Implement `MusicAuthorization` request/status UI.

### 5. Catalog search/resolution

- Search using mission item title/artist.
- Store first strong match or present choices for ambiguity.
- Record status and metadata.

### 6. Playback spike

- Queue/play one resolved item.
- Capture playback status/error.
- Require physical iPhone acceptance.

### 7. Reaction capture

- Render reaction buttons.
- Require a note for acceptance-test export.
- Timestamp reaction.

### 8. Export

- Generate JSON matching schema.
- Generate Markdown discovery log.
- Save/share files.

### 9. Physical-device acceptance test

- Run acceptance script.
- Save sample export files.
- Document results.

## Codex implementation dispatch

```text
You are working in the Music Atlas Controller iOS repo.

Use docs/app_dev/kickoff_v0_2 as controlling context. Build only the v0.2 SwiftUI/MusicKit spike.

Goal:
Create a minimal iOS app that loads sample_mission_love_tributaries_v0_2.json, validates/decodes it, requests MusicKit authorization, resolves at least one Apple Music catalog track, plays that track on a physical iPhone, captures one reaction plus one note, and exports both JSON and Markdown.

Important PM decisions:
- Initial success requires 1 resolved/playable track, not 8/10 tracks.
- Sample mission has 4 items.
- reconciliation_status is top-level on reaction_session.json and defaults to not_reconciled.
- The app does not update the Atlas.
- The spike is Apple Music/MusicKit only.
- Physical iPhone playback is required for acceptance.

Implementation order:
1. Create/confirm repo structure.
2. Add models and data loading for mission JSON.
3. Add strict validation/error display.
4. Build SwiftUI skeleton.
5. Add MusicKit authorization and status UI.
6. Add catalog search/resolution service.
7. Add playback service.
8. Add reaction capture UI.
9. Add export service for JSON + Markdown.
10. Add basic tests or validation utilities where feasible.

Do not build graph visualization, Spotify support, cloud sync, public onboarding, or automatic Atlas reconciliation.

Before making code changes, inspect the repo and summarize the planned file changes. Then implement in small, reviewable steps.
```
