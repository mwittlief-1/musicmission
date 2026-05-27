# Family 12 Lock Readiness

Judgment: soft-lock candidate after family-local importer review; not hard-locked yet.

| archetype_id | lock_after_gap_fill | remaining risk | needs another research pass? | consolidation/import action |
|---|---|---|---|---|
| 088 | maybe | Prince/Michael/Madonna/Whitney version and album-object handling spans pop, R&B, rock, and soundtrack contexts. | no full pass | Confirm album/song membership and do not flatten sovereign artists into one-hit prompts. |
| 089 | yes | Boy-band/girl-group songs can overstate artist-depth preference. | no | Prefer song-first survey prompts for group-monoculture rows. |
| 090 | maybe | Club/party pop can be confused with wedding or dancefloor context. | no | Use false_nearby and bridge roles for party-only signals. |
| 091 | maybe | Persona-pop album worlds overlap with indie/R&B/alternative families. | light targeted pass optional | Keep album_anchor rows and boundary roles. |
| 092 | yes | Inspirational and TV-drama anthems can become one-song dead ends. | no | Keep one-song inspirational rows edge-weighted and song_survey_only where needed. |
| 093 | maybe | Very recent TikTok/streaming hits are volatile. | light targeted pass optional | Recheck current recognition before hard lock. |

Lock recommendation: proceed to staging only after local schema validation and manual QA on the warnings above. No global import dry run was run for this family pass.
