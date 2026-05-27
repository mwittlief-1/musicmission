# Lock Readiness

Judgment: staging-ready after targeted depth pass; not hard-locked.

Import-readiness score: 0.82

Rationale:
- Required artist, album, and song fields are present with normalized enum values and lowercase kebab-case IDs.
- The targeted pass added only structurally useful gaps and avoided a collector-only expansion.
- Every archetype now has enough surface for Page 1/Page 2 branching, with hardcore/noise depth kept survey-controlled.
- Remaining work is mostly consolidation: aliases, cover/source versions, cross-family memberships, and Page 2 thresholds.

## Archetype Lock Table

| archetype_id | archetype | lock_after_this_pass | remaining risk | consolidation scope |
|---|---|---|---|---|
| 053 | First-Wave Punk / 70s Punk | maybe | Cover/source and cross-membership handling for Wire/X/Germs edges. | Mostly consolidation; no broad expansion needed. |
| 054 | CBGB / Art-Punk / Downtown New York | maybe | No Wave aliasing and compilation gateway semantics. | Consolidation plus light Page 2 ordering. |
| 055 | Hardcore Punk / US 80s Hardcore | maybe | Hardcore/metal crossover and collector-only edge suppression. | Mostly consolidation and survey-tier QA. |
| 056 | Post-Punk / Dark Melodic / Gothic Roots | maybe | Post-punk/goth/dream-pop boundary with Families 10 and 11. | Consolidation and boundary tagging. |
| 057 | New Wave / MTV Pop-Rock | maybe | New wave vs classic rock/pop/context overlap. | Consolidation and Page 1 ordering. |
| 058 | Synthpop / New Romantic / 80s Electronic Pop | maybe | Synthpop vs Family 11 electronic and alias/version rows. | Consolidation and alias handling. |
| 059 | College Rock / Pre-Alternative 80s | maybe | College rock vs Family 10 alternative and Family 17 novelty false-nearby. | Consolidation and survey suppression QA. |
| 060 | Noise Rock / Post-Hardcore / Touch and Go Axis | maybe | Noise/post-hardcore depth can drift collector-only; cover/version risks with grunge. | Consolidation plus Page 2 thresholds. |

Lock recommendation: do not claim final lock. Family 8 can move into backend staging and internal survey simulation after this pass, but hard lock waits for alias/version consolidation and cross-family boundary QA.
