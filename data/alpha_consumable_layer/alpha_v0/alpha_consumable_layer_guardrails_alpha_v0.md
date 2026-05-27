# Alpha Consumable Layer Guardrails Alpha v0

Version: `alpha_v0`

Status: `frozen_for_alpha_consumable_layer`

This file states the hard boundaries for using graph-derived music objects in Alpha app surfaces, Survey, starter Atlas references, default first Mission Generation, Supabase, and OpenAI.

## Product Posture

Build the Alpha consumable layer, not a hard-locked canonical database.

The consumable layer is a safe, versioned view over the repaired graph surfaces. It exists to ask useful questions and seed careful missions. It is not final canon and does not own user-specific truth.

## Allowed Uses

The approved Alpha graph surfaces may feed:

- controlled Survey candidate display
- app/local candidate pools for first Mission Generation
- Supabase candidate storage for passing rows
- compact OpenAI prompt payloads for mission generation
- starter Atlas references as provisional evidence inputs
- manual/concierge review packets

For Alpha 1 first-run intake, controlled Survey display means exactly:

```text
4 artist screens
2 album screens
4 song screens
12 tiles per screen
```

Graph-side support for that fixed shape is defined in:

```text
data/alpha_consumable_layer/alpha_v0/alpha1_fixed_survey_intake_graph_support_alpha_v0.json
data/alpha_consumable_layer/alpha_v0/alpha1_fixed_survey_intake_graph_support_alpha_v0.md
```

All product-facing candidates should carry an Atlas-aligned `music_object_ref` using:

```text
data/alpha_consumable_layer/alpha_v0/atlas_music_object_ref_alpha_v0.schema.json
data/alpha_consumable_layer/alpha_v0/graph_to_atlas_music_object_ref_alpha_v0.md
```

`music_object_ref` is reference-only. It is not user taste and does not create Atlas roles.

Survey Evidence Export ingestion must consume only:

```text
survey_evidence_export.atlas_ingestable.evidence_atoms
```

and must ignore:

```text
survey_evidence_export.construction_only_excluded
```

Survey owns live page selection and same-session displayed page history. Canonical owns stable candidate surfaces and typed refs.

## Blocked Uses

Raw graph rows must not feed:

- Survey surfaces
- starter Atlas creation
- default Mission Generation
- app-visible candidate grids
- Supabase active candidate tables
- OpenAI prompt payloads
- MusicKit auto-resolution

Hard blocks:

- no full canonical import
- no hard lock
- no title-only merges
- no unguarded Atlas promotion
- no direct Dead End creation from graph rows
- no context-only families in default first missions
- no quarantined or suppressed rows in user-facing product surfaces
- no graph metadata treated as user taste
- no candidate role treated as Atlas role
- no post-Survey "building your Atlas" language treated as promoted Atlas truth
- no `construction_only_excluded` Survey rows treated as Atlas-ingestable evidence
- no Survey response without same-session displayed page history treated as evidence

## Quarantine / Suppression Enforcement

A row is blocked if:

- it appears in `canonical_quarantine_queue.json`
- source bucket is `suppressed_quarantined`
- `review_status != approved`
- `quarantine_reasons` is non-empty
- recording sidecar has `survey_safe == false`
- recording sidecar has `review_status == quarantined`
- recording sidecar has `review_status == needs_review`
- row belongs only to `context_only` family/archetype
- row requires manual review and no human override exists
- row appears in `alpha_candidate_blocklist_alpha_v0.json`

Blocked rows may remain visible to QA. They must not appear in Survey, app surfaces, default Mission Generation, starter Atlas, MusicKit auto-resolution, Supabase active candidate tables, or OpenAI prompt payloads.

## Approved Surface Boundary

Approved Alpha graph surfaces:

- `survey_artist_candidates_v0_2.json`
- `survey_album_candidates_v0_2.json`
- `survey_song_candidates_v0_2.json`
- `family_survey_readiness_v0_2.json`
- `archetype_readiness_v0_2.json`
- `canonical_quarantine_queue.json`
- `canonical_recording_versions.json`
- `dead_end_probe_candidates_v0_2.json`
- `boundary_question_bank_v0_2.json`

These are versioned in:

```text
data/alpha_consumable_layer/alpha_v0/alpha_graph_surface_manifest.json
data/alpha_consumable_layer/alpha_v0/alpha_graph_surface_manifest.md
data/alpha_consumable_layer/alpha_v0/alpha_candidate_blocklist_alpha_v0.json
data/alpha_consumable_layer/alpha_v0/atlas_music_object_ref_alpha_v0.schema.json
data/alpha_consumable_layer/alpha_v0/graph_to_atlas_music_object_ref_alpha_v0.md
```

## Mission Generation Boundary

Mission Generation may consume:

- compact local candidate pools
- observed/provisional survey evidence
- candidate role/risk vocabulary
- inference guardrails
- version-risk notes

The Alpha 1 graph handoff is defined in:

```text
data/alpha_consumable_layer/alpha_v0/alpha1_first_mission_handoff_graph_contract_alpha_v0.json
data/alpha_consumable_layer/alpha_v0/alpha1_first_mission_handoff_graph_contract_alpha_v0.md
```

Mission Generation must not consume:

- raw canonical graph rows
- raw family files
- hidden simulation truth
- raw Apple payloads
- quarantined rows
- suppressed rows
- manual-review-only rows in default generation
- graph claims framed as promoted Atlas truth

## Atlas Boundary

This lane blocks only on Atlas for:

- final `music_object_ref` union details
- Atlas promotion semantics
- confidence/promotion state rules
- how non-canonical user-local/external/unresolved objects coexist with canonical refs

This lane does not need to block on Atlas for:

- freezing approved Alpha graph surfaces
- candidate role/risk vocabulary
- quarantine/suppression enforcement
- tile-log metadata
- MusicKit version-risk notes
- local candidate pool checks

## Safe-Send Rule

Before sending to Supabase or OpenAI, a candidate must be:

```text
from approved alpha_v0 source
approved
active
not quarantined
not suppressed
deduped within route/page
version-checked
role-tagged
risk-tagged
guardrail-tagged
source_contract_version == alpha_v0
```

If any condition fails:

```text
do_not_send_to_supabase = true
do_not_send_to_openai = true
do_not_show_in_app = true
manual_review_required = true
```
