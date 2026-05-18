# Music Atlas Controller

Private SwiftUI/MusicKit spike for running Music Atlas discovery missions.

The controlling product and implementation packet is v0.2:

- `docs/app_dev/kickoff_v0_2/`
- `docs/app_dev/IMPLEMENTATION_PLAN_v0_2.md`

## Locked v0.2 Success Bar

The first spike succeeds when the app can:

1. Load `sample_mission_love_tributaries_v0_2.json`.
2. Display all 4 mission items.
3. Request and display Apple Music authorization status.
4. Resolve at least 1 mission item to an Apple Music catalog item.
5. Play that resolved item on a physical iPhone.
6. Capture one reaction value and one non-empty note.
7. Export JSON conforming to `schema_reaction_session_v0_2.json`.
8. Export readable Markdown.
9. Include top-level `reconciliation_status: "not_reconciled"` in JSON.

The spike does not require resolving all sample items, creating playlists, updating the Atlas, Spotify support, cloud sync, or public-product polish.

## Repo Layout

```text
MusicAtlasController.xcodeproj/  Xcode project for the iOS spike
MusicAtlasController/            SwiftUI app source and bundled resources
docs/app_dev/kickoff_v0_2/   v0.2 PM packet and implementation brief
data/missions/               sample mission JSON
data/schemas/                JSON schemas for missions and reaction sessions
data/exports/dev/            development/stub exports, ignored except .gitkeep
data/exports/acceptance/     physical-device acceptance exports, ignored except .gitkeep
scripts/                     validation helpers
tests/                       test notes and future automated test space
```

## Validate The Sample Mission

Install the script dependency:

```sh
python3 -m pip install -r scripts/requirements.txt
```

Validate the included sample mission:

```sh
python3 scripts/validate_mission_json.py
```

Validate a reaction-session export:

```sh
python3 scripts/validate_session_json.py data/exports/reaction_session_YYYYMMDD_HHMMSS.json
```

## Next Implementation Step

Open `MusicAtlasController.xcodeproj` in Xcode, select a real Apple Developer team, enable MusicKit for the App ID, and run the starter app on a physical iPhone. The first implementation slice after launch is MusicKit catalog search/resolution.
