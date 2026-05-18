# Music Atlas Controller Product Brief v0.2

## Product name

Working name: **Music Atlas Controller**

## Product purpose

Music Atlas Controller is a personal iOS listening tool for executing Music Atlas discovery missions. It is not the Atlas itself and it is not the public onboarding product. It is the player + feedback layer that turns a mission into listening, reactions, and exportable discovery evidence.

## Problem

The Atlas can generate high-quality discovery missions, but current listening feedback is captured manually through chat/voice notes. That is useful but inconsistent. The app should make the field loop fast:

1. Load a mission.
2. Resolve tracks/albums in Apple Music.
3. Play the mission.
4. Capture reactions and notes with minimal friction.
5. Export valid JSON and readable Markdown.

## MVP user

Matt only. This is a private spike for a single user with Apple Music.

## v0.2 product boundary

### In scope

- Load bundled/local mission JSON.
- Display mission hypothesis, items, and inflation warning.
- Resolve Apple Music catalog matches for mission items.
- Play at least one resolved track on a physical iPhone.
- Capture one or more per-item reactions and notes.
- Export reaction session as JSON and Markdown.

### Out of scope

- Atlas graph visualization.
- Automatic Atlas updates.
- Spotify, Pandora, YouTube Music, Last.fm, or web playback.
- Public onboarding/calibration flow.
- Multi-user accounts.
- Cloud sync.
- Recommendation generation inside the app.
- Perfect matching of all mission tracks.

## Strategic rule

The app writes **Discovery Log evidence**, not Atlas canon. Reconciliation into the Atlas happens later through a deliberate review pass.

## Initial success definition

The v0.2 spike succeeds when all of the following are true:

- The app loads the included 4-item sample mission.
- The app resolves at least 1 item to an Apple Music catalog item.
- The app plays that item on a physical iPhone.
- The app captures one reaction value and one note.
- The app exports schema-valid JSON.
- The app exports readable Markdown.
- The exported JSON has top-level `reconciliation_status: "not_reconciled"`.

## Product principle

Do the smallest thing that proves the feedback loop can exist on a real iPhone with Apple Music. Do not build the full Atlas UI yet.
