# User Flow v0.2

## Primary flow

### 1. Launch

- App opens to Mission List.
- Sample mission appears: `Love Tributaries — v0.2 Spike Sample`.

### 2. Mission detail

User sees:

- mission title
- hypothesis
- recommended format
- inflation warning
- item list with title/artist/item type
- current resolution status for each item

Primary actions:

- Authorize Apple Music
- Resolve items
- Start playable item

### 3. Music authorization

If status is not determined:

- User taps `Authorize Apple Music`.
- App calls MusicKit authorization flow.

If denied/restricted:

- App displays status and blocks playback.
- App still allows viewing mission and exporting a failed/incomplete session.

If authorized:

- App enables catalog resolution.

### 4. Resolve items

User taps `Resolve Mission`.

App behavior:

- Search Apple Music catalog per mission item.
- If one strong match exists, mark resolved.
- If multiple plausible matches exist, mark ambiguous and present choices.
- If no match, mark unresolved.
- If track appears unavailable in region/subscription, mark unavailable status.

Initial acceptance requires only one resolved item.

### 5. Now Testing / playback

User selects or starts first resolved item.

App shows:

- item title
- artist
- album if available
- catalog ID
- playback status
- reaction controls
- note field

User taps play. The track must play on a physical iPhone for acceptance.

### 6. Reaction capture

User selects one reaction value:

- hit
- partial
- ok_shelf
- miss
- slop
- skipped
- unresolved

User enters a short note. For the acceptance test, the note must be non-empty.

### 7. Export

User taps `Export Session`.

App produces:

- `reaction_session_<timestamp>.json`
- `discovery_log_<timestamp>.md`

The JSON must validate against `schema_reaction_session_v0_2.json`. The Markdown must be readable without parsing JSON.

## Error states that must be visible

- Apple Music authorization denied/restricted.
- No Apple Music subscription or playback capability unavailable.
- Track unresolved.
- Track ambiguous.
- Track unavailable in storefront/region.
- Playback failed.
- Export validation failed.

## UX constraint

This is a spike. Prefer visible debug/status rows over polished design. The app should make failure modes legible.
