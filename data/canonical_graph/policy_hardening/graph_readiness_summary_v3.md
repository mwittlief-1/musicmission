# Graph Readiness Summary v3

Generated: 2026-05-20

## Current State

The canonical graph corpus is backend staging ready.

Dry-run status:

- 18 families imported.
- 0 validation errors.
- 9 validation warnings.
- 1499 canonical artists emitted.
- 1207 canonical albums emitted.
- 1917 canonical song recordings emitted.
- 1612 artist memberships emitted.
- 1245 album memberships emitted.
- 1983 song memberships emitted.
- 24 composition/title review rows generated.

The corpus is not final-lock ready.

## What Is Staging-Ready

- Required family output files exist for all 18 families.
- Normalized JSON parses for all families.
- Artist, album, and song row schemas validate.
- Simplified enums are import-safe for staging.
- Canonical entity tables and membership tables are emitted.
- Duplicate memberships are expected and represented separately from canonical entities.
- Merge review and warning queues exist.
- The current graph can support backend import contract tests.

## What Is Not Final-Lock Ready

- Alias/split table is not complete.
- Composition vs recording model is not implemented.
- Same-title songs still need human QA.
- Group/solo and credited/canonical artist rules are not encoded in data.
- Cast/show/soundtrack/composer/fictional-performer modeling is not final.
- Worship, hymn, standard, and traditional-song modeling is not final.
- Family 8 targeted depth pass is complete, but alias/version and cross-family boundary QA remain.
- Fast-moving current/internet-native scenes need freshness review policy.
- Several generated families have no aligned row-level seed source and need source-specific second passes before lock.

## Highest-Risk Import Areas

| risk area | examples | why it matters |
|---|---|---|
| Composition vs recording | `Hound Dog`, `The Twist`, `Walk This Way`, `House of the Rising Sun`, `We Shall Overcome` | Title merges would corrupt taste signals. |
| Alias and group/solo splits | 2Pac/Tupac, Mos Def/Yasiin Bey, Diana Ross/Supremes, Beyonce/Destiny's Child | Bad merges collapse distinct survey meanings. |
| Display-name drift | Kool & The Gang, Martha & the Vandellas, Simon & Garfunkel, B-52's | Safe to normalize only after entity confirmation. |
| Cast/show/soundtrack objects | `We Don't Talk About Bruno`, `Hamilton`, `Frozen`, `Black Panther`, `James Bond Theme` | Show, cast, composer, soundtrack, and recording are different graph objects. |
| Worship and standards | `Amazing Grace`, `Shout to the Lord`, `In Christ Alone`, `My Favorite Things`, `Nessun dorma` | Composition-first handling is often required. |
| Remix/edit/explicit variants | `WAP`, `I Don't Like`, club mixes, global-pop remixes | Version differences can be survey-relevant. |
| Current-scene volatility | hyperpop, modern active rock, lo-fi/study, TikTok pop | Requires refresh/suppress cadence. |

## Five Highest-Leverage Next Actions

1. Implement alias and identity sidecar tables.
   Include display aliases, project aliases, group/solo relationships, credited artist names, and canonical artist IDs.

2. Implement composition/recording policy fields.
   Add `composition_id`, `recording_variant_type`, `composition_policy_status`, and a queue status for the current merge-review rows.

3. Resolve the top same-title and cover/source cases.
   Start with `Hound Dog`, `The Twist`, `Shake, Rattle and Roll`, `That's All Right`, `Walk This Way`, `Gloria`, `House of the Rising Sun`, `We Shall Overcome`, `God Only Knows`, `We Don't Talk About Bruno`, `I'll Take You There`, `Love Shack`, and `Zombie`.

4. Run Family 8 consolidation and Page 2 threshold QA.
   Family 8 is no longer underbuilt, but it remains boundary-sensitive against Families 9, 10, 11, 17, and 18.

5. Add entity-context modeling for soundtrack, cast, worship, and standards.
   This should cover show/film, cast recording, composer, score album, curated soundtrack, church brand, songwriter, and traditional composition contexts.

## Backend Staging Tests

Ready: yes.

Recommended backend tests:

- Import canonical entity tables and membership tables into staging.
- Verify duplicate memberships do not create duplicate canonical entities.
- Verify warning and merge-review queues remain attached to imported rows.
- Verify null years are accepted only when traditional/composition status is present or warning-routed.
- Verify UI/API can fetch one canonical object with multiple family/archetype memberships.

## User-Facing Survey Tests

Ready: limited internal tests only.

Use the corpus for internal survey simulation, not broad user-facing tests. The graph can ask useful questions, but unresolved alias and composition cases can still produce confusing or duplicated prompts.

Minimum before broader user-facing survey tests:

- suppress or manually resolve high-risk duplicate prompts;
- block automatic title merges;
- apply Family 8 boundary/suppression QA;
- add display alias normalization for safe cases;
- keep standards/worship/cast rows behind manual-review flags.

## Final Canonical Lock

Ready: no.

Final lock is blocked until:

- duplicate handling is explicit;
- alias handling is explicit;
- composition/recording policy is implemented;
- cast/show/soundtrack/church/traditional entity modeling is explicit;
- Family 8 boundary and version risks are resolved after the targeted depth pass;
- each family has an explicit lock judgment after QA.

## Bottom Line

Proceed with backend staging import tests. Do not present this as a final canonical graph. The graph has a working schema and import path; the next pass should convert warnings into structured identity, alias, composition, and entity-context policies.
