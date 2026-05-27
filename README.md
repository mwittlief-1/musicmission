# Waymark / Cartenza Alpha

Private alpha repo for the Waymark/Cartenza iOS TestFlight app, MusicKit integration, mission generation, Atlas contracts, Supabase alpha backend, and supporting test harnesses.

Start with the current repo map before moving or adding files:

- `AGENTS.md`
- `docs/repo_map.md`
- `docs/repo_cleanup_inventory_2026_05_26.md`
- `data/README.md`

The original v0.2 app spike packet is still useful historical context:

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
MusicAtlasController.xcodeproj/  Xcode project for the iOS alpha
MusicAtlasController/            SwiftUI app source and bundled resources
MusicAtlasControllerTests/       XCTest sources and app fixtures
supabase/                       Supabase config, Edge Functions, and migrations
scripts/                        validation, generation, smoke, and import helpers
data/                           contracts, canonical material, fixtures, and generated evidence
docs/                           product/technical contracts, runbooks, reviews, and repo stewardship docs
waymark-ai-tests/               first-class mission-generation harness; generated outputs ignored
waymark-atlas-tests/            first-class Atlas ingestion harness; generated outputs ignored
build/                          local Xcode build output, ignored
data/exports/                   local app/device exports, ignored except .gitkeep
```

For the detailed policy, see `docs/repo_map.md`. For `data/` source-of-truth versus generated/archive decisions, see `data/README.md`.

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
