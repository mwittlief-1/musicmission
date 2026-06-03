# Canonical Mission Item Universe Alpha v0

Alpha contract version: `alpha_v0`

Generated: 2026-06-01T14:00:04.253Z

Status: `canonical_grid_available_for_mission_items_with_playback_gate`

The canonical grid is available as the mission-item universe. The compact candidate pool is a sample/slice for handoff tests, not the size of the graph.

Playback is a separate gate: playable song/recording items need an Apple Music catalog ID. No-ID rows remain in the graph but are blocked for playback until resolved.

## Summary

| metric | count |
| --- | ---: |
| canonical grid items | 11710 |
| playback candidate rows | 7417 |
| playback candidate rows with Apple ID | 7206 |
| playback candidate rows do_not_use_no_apple_id | 211 |
| Apple-ID resolved grid items | 11417 |
| Alpha survey-eligible grid items | 11417 |
| Alpha survey-unavailable no-Apple-ID rows | 291 |
| alpha blocklisted grid rows | 2 |
| alpha available mission items | 11497 |
| context/selection rows not playback | 4293 |

## By Candidate Type

| candidate_type | count |
| --- | ---: |
| song | 7018 |
| album | 2233 |
| artist_anchor | 2060 |
| recording | 399 |

## Policy

- The full canonical grid may be used as mission material.
- Any canonical grid item with an Apple Music catalog ID is eligible for Survey consideration unless blocklisted.
- The compact candidate pool is not the full mission universe.
- Apple Music catalog IDs gate playback, not canonical graph existence.
- `do_not_use_no_apple_id` blocks playback/default generation for that item until resolver work clears it.
- Graph metadata remains reference-only and never user taste.
