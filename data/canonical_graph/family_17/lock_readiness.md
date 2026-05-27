# Family 17 Lock Readiness

Judgment: soft-lock candidate after family-local importer review; not hard-locked yet.

| archetype_id | lock_after_gap_fill | remaining risk | needs another research pass? | consolidation/import action |
|---|---|---|---|---|
| 111 | yes | Novelty rows can overstate actual genre appetite if weighted like normal anchors. | no | Keep mostly edge/song-first and suppress dated-risk rows. |
| 112 | maybe | Holiday objects require seasonal flags and duplicate handling with standards/crooners. | light targeted pass optional | Use seasonal context and do not merge with general artist appetite. |
| 113 | yes | Party/karaoke familiarity can be mistaken for rock/pop/country/disco taste. | no | Apply false_nearby and context-first survey logic. |
| 114 | maybe | Kids/family songs often need composition or soundtrack ownership. | light targeted pass optional | Coordinate with Family 15 and composition handling before hard lock. |

Lock recommendation: proceed to staging only after local schema validation and manual QA on the warnings above. No global import dry run was run for this family pass.
