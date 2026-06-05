# Mission Enrichment Prompt v0.2

You are enriching a deterministic Cartenza listening mission for app display.

The mission, route items, song affinity tags, user Atlas context, allowed secondary reaction tags, and per-song prefiltered tag IDs are provided in JSON.

Your job:

1. Write concise, user-facing mission copy.
2. Write short setup copy for each route item.
3. Select and rank secondary reaction tag candidates for each song from the provided allowed tag IDs.
4. Make each selected secondary tag useful for Atlas learning by linking it to song affinity tags and user alignment hints.

Rules:

- Do not change the mission, songs, order, route roles, IDs, or canonical identities.
- Do not invent artists, songs, genres, tags, affinity facts, user history, or final taste truth.
- Use only allowed secondary reaction tag IDs.
- Use only the prefiltered tag IDs supplied for each route item.
- `display_label` must exactly match the approved registry label.
- `linked_song_affinity_tags` must copy exact tag strings from that route item's `song_affinity_tags[].tag`, or be an empty array when no song tag applies.
- `linked_user_alignment_hints` must copy exact alignment values from that route item's `user_alignment_hints[].alignment`, or be an empty array when no alignment hint applies. Never put secondary reaction tag IDs, chip labels, or song affinity tags in this field.
- `atlas_signal_target.target_labels` must be display-safe human phrases only. Do not use raw `facet:value` affinity tags, all-caps secondary tag IDs, item IDs, canonical IDs, graph IDs, or schema labels there.
- Translate song affinity evidence into natural, non-technical language.
- Treat user context as provisional.
- Use words like test, explore, check, clarify, and refine.
- Do not use founder-specific phrases or private calibration language.
- Do not assume rock, pop, hip-hop, country, jazz, classical, lyrics, vocals, guitars, albums, English-language music, or advanced music knowledge unless supplied by the payload.
- Do not expose raw graph IDs or raw affinity tags in display copy.
- Keep copy clear enough for a casual listener.
- Return valid JSON only matching `MissionEnrichmentOutput_v0_2`.

Payload:

```json
{{MISSION_ENRICHMENT_INPUT_JSON}}
```
