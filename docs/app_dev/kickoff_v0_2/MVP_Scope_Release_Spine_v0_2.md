# MVP Scope / Release Spine v0.2

## Release name

**Music Atlas Controller v0.2 Spike**

## Release objective

Prove that a SwiftUI/MusicKit app can execute the minimum discovery loop on a physical iPhone:

> Load mission → resolve one Apple Music item → play it → capture reaction/note → export JSON + Markdown.

## Locked acceptance bar

The spike is accepted with **1 resolved and playable Apple Music track**, not 8/10 tracks. The sample mission has 4 items. The app may leave 3 unresolved, skipped, ambiguous, or unavailable as long as those states are represented correctly in the export.

## Functional spine

1. **Mission load**
   - Bundle or import `sample_mission_love_tributaries_v0_2.json`.
   - Validate required mission fields.
   - Display mission metadata and items.

2. **MusicKit authorization**
   - Request MusicKit authorization.
   - Show authorization status.
   - Block catalog search/playback if not authorized.

3. **Subscription/playback capability check**
   - Check whether playback is possible for the current user/device.
   - If unavailable, show clear failure reason and still allow mission viewing/export of failed state.

4. **Catalog search/resolution**
   - Resolve mission items using Apple Music catalog search.
   - Store selected catalog ID and metadata.
   - Mark unresolved/ambiguous/unavailable items explicitly.

5. **Playback spike**
   - Queue/play at least one resolved track on a physical iPhone.
   - Capture playback attempt, status, and error if any.

6. **Reaction capture**
   - Capture reaction value.
   - Capture a note.
   - Timestamp the reaction.

7. **Export**
   - Export JSON conforming to `schema_reaction_session_v0_2.json`.
   - Export readable Markdown using template structure.
   - Top-level `reconciliation_status` must be present and set to `not_reconciled` by default.

## Non-goals for this spike

- No playlist creation requirement.
- No station seeding requirement.
- No background playback requirement.
- No Apple Music library mutation requirement.
- No graph rendering.
- No Atlas reconciliation.
- No cloud storage.

## Definition of done

The implementation is done when the physical-device acceptance script passes and the exported JSON validates against the v0.2 reaction-session schema.
