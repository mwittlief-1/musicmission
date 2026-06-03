# App Wiring Readiness Report v0.2

## Current App Observations

- Current runtime mission model is `MusicAtlasController/Models/Mission.swift`.
- Current app `MissionType` enum is legacy-shaped: `track_probe`, `album_test`, `station_seed`, `playlist_bleed`, `false_nearby_test`.
- New Alpha mission types (`context_dependence_test`, `boundary_test`, `bridge_test`, `archetype_depth_test`, `gateway_test`) are not currently first-class app mission enum cases.
- Current app schema `schema_mission_v0_2.json` is not the same as this app-import payload contract.
- Current app `MissionLoader` validation expects imported route items to enter unresolved so MusicKit resolution evidence is captured in-app.
- The new product contract hard-blocks ordinary app-import-ready missions with unresolved route items. This is a real mismatch to reconcile.
- Current reaction model has stable operations: `strong_positive`, `qualified_positive`, `keep_waypoint`, and `negative`.

## Shortest Safe Wiring Path

1. Add an app-side adapter or separate decoder for `AlphaAppImportMissionPayloadV0_2`.
2. Map Alpha mission types into app display/navigation without collapsing product semantics.
3. Decide whether `resolution_status=candidate` should be imported as a pre-resolution staging state before the existing unresolved MusicKit pass.
4. Resolve or attach Apple Music IDs before promoting any fixture to `app_import_ready`.
5. Keep local golden fixtures behind a dev/debug import path until endpoint generation is trusted.

## Can App Wiring Start?

Yes, for local fixture import, route-card rendering, feedback model mapping, validation UI, and MusicKit resolution adapter work.

## Can TestFlight UAT Start?

No. Playback-ready UAT remains blocked by Apple Music resolution and app model/schema compatibility.
