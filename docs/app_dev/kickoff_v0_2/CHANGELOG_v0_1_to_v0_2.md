# CHANGELOG v0.1 to v0.2

## Summary

v0.2 tightens the app-dev kickoff packet so it can be executed by Codex or an app-dev implementation chat without ambiguous success definitions.

## Changes

### Acceptance criteria conflict resolved

v0.1 had a conflict between a 4-track sample mission and a statement that v0.1 should resolve 8 of 10 tracks.

v0.2 decision:

- Sample mission has 4 items.
- Initial spike succeeds with 1 resolved Apple Music item.
- That item must play on a physical iPhone.
- One reaction and one note must be captured.
- JSON and Markdown must export.

### Session contract conflict resolved

v0.1 had `reconciliation_status` in inconsistent locations.

v0.2 decision:

- `reconciliation_status` is top-level on `reaction_session.json`.
- Default is `not_reconciled`.
- It is not nested under `mission_summary`.

### Schemas tightened

v0.2 schemas require:

- mission item IDs;
- item type;
- artist/title;
- timestamps;
- resolution status;
- resolved catalog metadata when resolved;
- reason when unresolved/skipped/unavailable/failed;
- reaction value;
- reaction timestamp;
- notes object and note text;
- top-level reconciliation status.

### MusicKit implementation requirements added

v0.2 explicitly requires:

- Apple Developer / App ID setup;
- MusicKit capability/service configuration;
- `NSAppleMusicUsageDescription`;
- Music authorization state handling;
- subscription/playback capability check;
- physical iPhone testing;
- storefront/region/unavailable-track handling.

### First implementation backlog added

v0.2 includes a concrete implementation backlog:

1. repo setup,
2. data contracts and validation,
3. SwiftUI skeleton,
4. MusicKit authorization,
5. catalog search/resolution,
6. playback spike,
7. reaction capture,
8. export,
9. physical-device acceptance test.

### Scope clarified

v0.2 confirms the spike does not include:

- graph visualization;
- Atlas auto-reconciliation;
- playlist creation;
- Spotify or other services;
- public product onboarding;
- resolving every mission item.
