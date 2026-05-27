# TestFlight Build 18 Upload Report

Date: 2026-05-26

## Build

- App version: `0.2`
- Build number: `18`
- Bundle ID: `com.vytisstudios.MusicAtlasController`
- Upload status: uploaded successfully; App Store Connect reported package processing.

## Fixes In This Build

- Fixed graph-native mission generation crash caused by `canonical_song_recordings.json` containing `release_years: [null]` for a small number of records.
- Updated `GraphSongRecord` decoding to tolerate missing/unknown release years by compacting nullable year arrays.
- Updated support diagnostic upload to fall back to the bundled Supabase anon key when no Supabase user session is available, so manual diagnostics can still upload when auth is part of the problem.
- Changed `Info.plist` version fields to use `$(MARKETING_VERSION)` and `$(CURRENT_PROJECT_VERSION)` so future build-number bumps flow into archives.

## Verification

- Passed targeted XCTest:
  - `MusicAtlasControllerTests/MissionDecodingTests/testGraphNativeStarterPackBuildsSixImportableEightSongMissions`
- Verified archive plist:
  - `CFBundleShortVersionString = 0.2`
  - `CFBundleVersion = 18`
- Archive succeeded:
  - `build/MusicAtlasController-0.2.18.xcarchive`
- TestFlight upload succeeded through `xcodebuild -exportArchive`.

## Notes

- This build does not reintroduce the OpenAI mission generation path. Starter Route Pack generation remains local and graph-native.
- Live Supabase diagnostic rows were not checked from this machine because neither Supabase service environment variables nor the Supabase CLI are available on PATH in the current shell.
