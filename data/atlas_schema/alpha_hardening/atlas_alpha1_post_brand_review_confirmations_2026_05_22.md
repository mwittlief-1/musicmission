# Atlas Alpha 1 Post-Brand Review Confirmations

Generated: 2026-05-22

Controlling decision source: `docs/app_dev/alpha_product_decision_addendum_2026_05_22.md`

## Summary

Product has decided that Alpha 1 includes a required first-run Survey intake, a post-Survey generation status surface, and a preferred path toward Supabase evidence upload after accepted privacy/terms.

Atlas can support the target Alpha 1 flow with the current schema boundary:

```text
Survey Evidence Export
-> Signal
-> AtlasNode when needed
-> provisional AtlasRoleAssignment
-> PossibleAtlasUpdateCandidate
-> AtlasDigestView
-> MissionGenerationDigestView
-> first mission batch generation
```

The support is conditional on the same hard rules already accepted:

- Survey output is evidence, not final Atlas truth.
- `AtlasNode` carries no role truth.
- `AtlasRoleAssignment` carries user-specific role truth.
- Survey-created roles remain `proposed`, `candidate`, or `blocked`; never `promoted`.
- Apple exposure remains exposure/familiarity context, not taste truth.
- `dont_know_enough` remains familiarity uncertainty, not negative evidence.
- Canonical graph mutation remains disallowed.

## ATL-015: Fixed Survey Intake Ingestion Profile

### Required Alpha 1 Intake Shape

Atlas expects the Alpha 1 Survey Evidence Export to declare and satisfy:

```json
{
  "page_count_config": {
    "artist_pages": 4,
    "album_pages": 2,
    "song_pages": 4,
    "config_id": "A4_Al2_S4"
  }
}
```

The export must contain one Atlas-ingestable evidence atom per visible completed tile response. Page counts are validated by distinct `page_context.page_id` values grouped by `page_context.stage`.

### Atlas Ingestion Expectations

For a fixed 4/2/4 intake export, Atlas ingestion must produce:

- `Signal` records for every visible evidence atom;
- `AtlasNode` records only as renderable/reasonable things;
- provisional/candidate `AtlasRoleAssignment` records only when policy allows;
- `PossibleAtlasUpdateCandidate` records for candidate roles, contradictions, review needs, recurrence requirements, and scope warnings;
- `AtlasDigestView` sufficient for WWTSF, Mission Generation, Candidate Pool Builder, evidence audit, and future correction;
- `MissionGenerationDigestView` sufficient for first mission batch generation without raw Survey payload.

### Current Fixture Status

Available normalized Survey Evidence Export samples currently validate and ingest for:

- `public_profile_01_A3_Al1_S2`
- `public_profile_05_A3_Al1_S2`
- `public_profile_06_A3_Al1_S2`

Those are useful proof fixtures, but they are not the required Alpha 1 fixed intake shape. They contain 3 artist pages, 1 album page, and 2 song pages.

Concrete dependency raised: `ATL-I001`. Atlas needs a Survey-owned `A4_Al2_S4` Survey Evidence Export fixture to run the full fixed-intake ingestion proof.

### Validation Gate

Atlas added a fixed-intake validator:

```bash
python3 scripts/validate_atlas_alpha1_intake_profile.py \
  --survey-export path/to/A4_Al2_S4_survey_evidence_export.json
```

The validator checks:

- `page_count_config.artist_pages = 4`;
- `page_count_config.album_pages = 2`;
- `page_count_config.song_pages = 4`;
- distinct visible evidence page counts match 4/2/4;
- evidence atoms exist;
- hidden/private construction fields are not present in Atlas-ingestable evidence;
- Apple exposure does not claim taste truth;
- `dont_know_enough` is not normalized as negative evidence;
- refs used by Atlas-ingestable evidence resolve inside the visible export.

## ATL-016: "Building Your Atlas" Wording Guardrails

Product may use "building your Atlas" on the post-Survey waiting/status surface if the surrounding copy preserves provisionality.

### Safe Status Copy

Safe phrases:

- "Building your Atlas"
- "Reading your Survey evidence"
- "Finding a careful first route"
- "Preparing your first mission batch"
- "Checking uncertainty before we recommend anything"

Recommended status sequence:

```text
Building your Atlas
Reading your Survey evidence
Looking for useful anchors, frontiers, and open questions
Preparing your first mission batch
```

This is safe because the word "Atlas" names the user's working map, not promoted truth.

### Required Caveats

The status/waiting surface should not say or imply:

- confirmed Landmarks;
- permanent Regions;
- final taste profile;
- Apple Music-proven taste;
- genre-level dislikes from sparse evidence;
- automatic promotion from Survey evidence.

Forbidden phrases:

- "We found your true taste."
- "Your Landmarks are confirmed."
- "Your permanent Atlas is ready."
- "We know exactly what you love."
- "Apple Music proved your taste."

### Product Boundary

The generation status surface may promise:

- Waymark is processing evidence;
- Waymark is creating a provisional starter map;
- Waymark is preparing first missions to test uncertainty.

It must not promise:

- final Atlas truth;
- durable role promotion;
- complete taste understanding.

## ATL-017: Uploaded App Evidence Policy

Product prefers automatic or scheduled Supabase evidence upload if engineering can support it safely. Atlas confirms this is compatible with the schema if the upload path remains append-only, auditable, provisional, and consent-gated.

### Upload Preconditions

Do not upload evidence until:

- privacy/terms acknowledgement has been accepted in-app;
- the app has a stable authenticated user identity;
- Supabase project access is configured without service-role keys in the app;
- upload payloads exclude hidden simulator/evaluator/debug data.

### Uploadable Evidence Classes

Uploadable after consent:

- Survey Evidence Export or equivalent visible Survey evidence atoms;
- mission reaction Signals;
- playback and skip/no-signal events;
- selected tags;
- shown-unselected tags as weak context;
- user notes;
- resolver/import context;
- correction/superseding atoms;
- app-generated evidence exports for PM audit.

Derived outputs may be uploaded or regenerated server-side:

- `AtlasDigestView`;
- `MissionGenerationDigestView`;
- `PossibleAtlasUpdateCandidate`;
- `AtlasDelta`.

### Upload Rules

- Uploads are append-only.
- Corrections append superseding/correction atoms; they do not mutate prior evidence.
- Uploaded evidence remains provisional Alpha evidence.
- No upload path may promote Atlas roles by itself.
- No upload path may mutate canonical graph.
- Apple exposure remains context only.
- User deletion/reset must suppress or delete source evidence and regenerate derived Atlas read models.

### Privacy / Deletion Support

Atlas already inventories the relevant data classes in `data/atlas_schema/alpha_hardening/atlas_alpha_hardening_contracts_v0_1.md`.

The upload policy supports privacy/terms copy by keeping:

- source evidence traceable;
- derived state regenerable;
- user notes identifiable as sensitive user-authored data;
- Apple exposure separate from taste truth;
- model packets separate from raw Survey construction/debug payloads.

Final privacy/terms language remains a Release/Product dependency, but the Atlas data policy is compatible with either manual Share Evidence fallback or consented scheduled Supabase upload.

## Updated Readiness

Atlas is ready for Core/Supabase integration with caveats:

- fixed 4/2/4 Survey Evidence Export fixture is still needed from Survey for full proof;
- live Supabase/account access is not required for this policy confirmation;
- final privacy/terms copy is not required to define the data policy, but it is required before enabling upload;
- no automatic promotion is authorized.
