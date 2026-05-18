# App Dev Launch Prompt v0.2

Use this prompt to start the implementation chat or Codex session.

```text
We are building Music Atlas Controller, a private SwiftUI/MusicKit iOS spike.

Use the attached v0.2 kickoff packet as controlling context.

Primary goal:
Build the smallest working iOS app that proves the discovery-mission feedback loop on a physical iPhone.

Locked success bar:
- Load sample_mission_love_tributaries_v0_2.json.
- Display the 4 mission items.
- Request/display MusicKit authorization status.
- Resolve at least 1 Apple Music catalog track.
- Play that resolved track on a physical iPhone.
- Capture one reaction value plus one non-empty note.
- Export reaction_session.json conforming to schema_reaction_session_v0_2.json.
- Export readable Markdown.
- Top-level reconciliation_status must exist and default to not_reconciled.

Important constraints:
- Do not build graph visualization.
- Do not auto-update the Atlas.
- Do not support Spotify/Pandora/YouTube Music.
- Do not require resolving all mission tracks.
- Do not implement playlist creation in this spike.
- Physical iPhone playback is required for acceptance.

First implementation backlog:
1. repo setup,
2. data contracts and validation,
3. SwiftUI skeleton,
4. MusicKit authorization,
5. catalog search/resolution,
6. playback spike,
7. reaction capture,
8. export,
9. physical-device acceptance test.

Start by inspecting the repo and proposing the exact file changes. Then implement in small reviewable steps.
```
