# Acceptance Criteria and Test Plan v0.2

## Locked success bar

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

## Non-acceptance definitions

The spike does **not** require:

- resolving all 4 sample items;
- resolving 8 of 10 items;
- creating a playlist;
- mutating the Apple Music library;
- updating the Atlas;
- supporting Spotify or other services;
- running without a physical iPhone;
- polished UI.

## Manual test script

### Preconditions

- Physical iPhone available.
- Apple Music app installed/configured.
- Device signed into Apple ID.
- Active Apple Music subscription or playable catalog access.
- App signed with Apple Developer team and MusicKit setup completed.
- Network available.

### Test 1 — Mission load

1. Install app on physical iPhone.
2. Launch app.
3. Confirm Mission List shows `Love Tributaries — v0.2 Spike Sample`.
4. Open mission.
5. Confirm 4 items appear with artist/title and unresolved resolution status.

Pass if all 4 items display and no required-field validation errors appear.

### Test 2 — Authorization

1. Tap authorization action if required.
2. Respond to system prompt.
3. Confirm app displays final authorization status.

Pass if app reaches `authorized`, or if denied/restricted is displayed clearly and playback is blocked. Full spike acceptance requires authorized state.

### Test 3 — Resolution

1. Tap `Resolve Mission` or resolve one item.
2. Confirm at least one item becomes `resolved` with Apple Music catalog metadata.
3. Confirm unresolved/ambiguous/unavailable items are marked with explicit status/reason.

Pass if at least one item is resolved.

### Test 4 — Playback

1. Select resolved item.
2. Tap play.
3. Confirm audible playback on physical iPhone.
4. Confirm app records playback status.

Pass if at least one item audibly plays and playback status is stored.

### Test 5 — Reaction capture

1. Select a reaction value.
2. Enter a non-empty note.
3. Save reaction.
4. Confirm reaction appears in session state.

Pass if reaction value, note, and timestamp are stored.

### Test 6 — Export JSON

1. Tap export.
2. Save/share JSON.
3. Validate JSON against schema.
4. Confirm top-level `reconciliation_status` equals `not_reconciled`.

Pass if schema-valid.

### Test 7 — Export Markdown

1. Save/share Markdown.
2. Open Markdown.
3. Confirm it is readable and includes mission title, item played, reaction, note, resolution status, and reconciliation status.

Pass if readable without JSON parsing.

## Acceptance evidence to keep

- Screenshot or note of authorization status.
- The exported JSON file.
- The exported Markdown file.
- Note of physical device model / iOS version.
- Note of Apple Music storefront/region if available.
- Any MusicKit errors encountered.
