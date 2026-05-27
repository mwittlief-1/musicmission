# Family 1 Lock Readiness

Judgment: soft-lock candidate after importer dry-run; not hard-locked yet.

Family 1 is broad enough and schema-normalized, but hard lock depends on importer behavior for canonical entities plus archetype memberships, recording-specific cover/source splits, and alias handling.

| archetype_id | lock_after_gap_fill | remaining risk | needs another research pass? | consolidation/import action |
|---|---|---|---|---|
| 001 | maybe | Source-version vs mass-version handling; roots additions must not overwhelm normal-user survey. | no full pass | Confirm version-aware recording entities and Page 1 thresholding. |
| 002 | maybe | Could become too collector-rockabilly if Page 3 additions are over-promoted. | no | Keep low-recognition rows edge/suppressed unless user taps point there. |
| 003 | yes | Main risk is compilation normalization and avoiding artist-survey bloat for song-only acts. | no | Import with song-first survey defaults and compilation gateway support. |
| 004 | yes | Adult-pop boundary can sprawl into non-rock crooner territory if not capped. | no | Keep crooner/adult-pop rows as contrast/boundary objects. |
| 005 | maybe | Motown-girl material overlaps 006 and later Motown/soul families. | light targeted pass optional | Use membership rows, not duplicate canonical entities. |
| 006 | maybe | Boundary with later classic soul, Motown, Stax, blues-soul, and funk families. | light targeted pass optional | Keep early-period rows and bridge later-family ownership. |
| 007 | yes | Pure surf vs hot-rod/frat/instrumental pop needs clear survey thresholds. | no | Preserve song-first instrumental logic and keep album surface modest. |

Lock recommendation: proceed to staging import; require manual QA on duplicate membership, aliases, and source/covers before final canonical lock.
