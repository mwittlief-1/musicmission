# Family 008 Depth Recommendation

Generated: 2026-05-20

## Status

Completed: a targeted punk/post-punk/new-wave expansion pass was applied on 2026-05-20.

Family 8 should no longer be treated as only a staging baseline. It is now strong enough for backend staging and internal survey simulation. It should still not be hard-locked.

Do not run an open-ended full music-history pass. Remaining work should focus on consolidation: aliases, cover/source versions, cross-family boundaries, and Page 2 thresholds.

## Current Status

| criterion | status |
|---|---|
| Schema compliance | Pass |
| Dry-run import | Pass |
| Required files | Present |
| Staging import | Ready |
| Hard lock | Not ready |
| Breadth | Adequate after targeted pass |
| Duplicate/version risk handling | Partial |
| Family 10/11 boundary handling | Needs QA |

## Why A Targeted Pass Is Better

Family 8 sits between several high-confusion zones:

- Family 10 Alternative/Indie/Grunge/Emo;
- Family 11 Electronic/Dance/Synthpop;
- Family 9 Metal/Heavy Music;
- Family 17 party/novelty/context rows for MTV-era normal-user memory.

The updated Family 8 coverage now supports first-wave punk, CBGB/art-punk, hardcore, post-punk/gothic, MTV new wave, synthpop, college rock, and post-hardcore/noise branching. It still needs weighting, false-nearby controls, and consolidation QA.

## Targeted Expansion Goals

Do:

- strengthen normal-user anchors without making punk collector-only;
- add bridge/contrast rows where the survey needs to distinguish punk, post-punk, new wave, synthpop, college rock, and alternative;
- identify rows that should remain Family 10 or Family 11 instead of Family 8;
- preserve song-first objects where one track is more survey-useful than the artist;
- flag covers, live versions, and display-name risks.

Do not:

- chase rare hardcore singles;
- inflate every sub-archetype to equal size;
- merge synthpop into electronic just because synths are present;
- merge college rock into 90s alternative just because later influence is obvious;
- over-promote one novelty/MTV song into artist-level importance.

## Superseded Dispatch Prompt

This prompt was the basis for the completed targeted pass. Do not rerun it as broad expansion unless survey testing shows a specific gap:

```text
We are hardening Family 8 of the Waymark Canonical Music Graph.

Family 8: Punk, Hardcore, Post-Punk, New Wave

Archetypes:
- 053 First-Wave Punk / 70s Punk
- 054 CBGB / Art-Punk / Downtown New York
- 055 Hardcore Punk / US 80s Hardcore
- 056 Post-Punk / Dark Melodic / Gothic Roots
- 057 New Wave / MTV Pop-Rock
- 058 Synthpop / New Romantic / 80s Electronic Pop
- 059 College Rock / Pre-Alternative 80s
- 060 Noise Rock / Post-Hardcore / Touch and Go Axis

Inputs:
- data/canonical_graph/family_8/normalized_family_8.json
- data/canonical_graph/family_8/import_warnings.md
- data/canonical_graph/policy_hardening/schema_policy_review.md
- data/canonical_graph/policy_hardening/canonical_identity_policy.md
- data/canonical_graph/policy_hardening/composition_recording_policy.md
- data/canonical_graph/import_dry_run/merge_review_queue.md

Task:
Run a targeted depth pass, not a broad music-history essay. Keep the graph survey-first.

Output:
- recommended adds, suppressions, and reweights;
- bridge/contrast/false-nearby notes against Families 9, 10, 11, and 17;
- version/cover/alias warnings;
- updated lock-readiness judgment;
- do not claim hard lock.

Constraints:
- Do not title-merge songs automatically.
- Do not merge covers automatically.
- Do not collapse artist/album/song objects.
- Preserve normal-user recognition alongside canon.
- Song-first and one-hit objects are valid, but do not over-promote one song into artist-level importance.
```

## Next Deliverable

The next pass should produce either:

- structured alias/version decisions for Family 8 warnings;
- suppress/reweight recommendations after Page 1/Page 2 survey simulation;
- boundary decisions against Families 9, 10, 11, 17, and 18.

Hard lock remains blocked until alias/version policy and cross-family boundaries are explicit.
