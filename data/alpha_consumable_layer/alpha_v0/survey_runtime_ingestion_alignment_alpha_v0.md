# Survey Runtime Ingestion Alignment Alpha v0

Version: `alpha_v0`

Status: `aligned_with_survey_runtime_page_history`

Survey now acts first. The app Survey runtime selects and freezes shown pages using Apple exposure priors plus Canonical candidate surfaces. Canonical owns the input graph surfaces and stable metadata, not live page selection.

## Ownership Boundary

Survey owns:

- live page selection
- shown page freezing
- `survey_session_id` persistence
- displayed page history persistence
- Apple exposure prior capture
- Survey Evidence Export assembly

Canonical Graph owns:

- stable candidate surfaces
- typed canonical IDs
- `music_object_ref` identity metadata
- quarantine and suppression rules
- version and resolver policy sidecars
- reference-only graph metadata

Atlas owns:

- Signal ingestion
- AtlasNode creation/update
- provisional AtlasRoleAssignment
- PossibleAtlasUpdateCandidate
- AtlasDigestView

## Ingestion Rule

Atlas and Canonical-adjacent ingestion should consume only:

```text
survey_evidence_export.atlas_ingestable.evidence_atoms
```

They must ignore:

```text
survey_evidence_export.construction_only_excluded
```

Any response not backed by the same session's displayed page history is non-ingestable and belongs in construction/quarantine handling.

## Semantics

- `apple_exposure_prior.taste_truth` is always `false`.
- `evidence_strength_hint` is Survey metadata only, not Atlas confidence.
- `dont_know` maps to `familiarity_uncertainty`, not negative taste.
- `selected_tags` are visible Signal evidence.
- `shown_unselected_tags` are weak/non-selected context.
- `music_object_ref.object_type` is typed as `artist`, `album`, or `song_recording` for Survey evidence.
- Graph meanings remain refs/IDs only unless Canonical provides approved visible labels/descriptions.

## Blocked Ingestion

Do not ingest these into Atlas Signals:

- `construction_only_excluded`
- responses without same-session displayed page history
- unshown responses
- unresolved responses
- raw Apple payloads
- raw graph rows
- promoted Atlas role claims
- final Atlas confidence claims

## Recommended Atlas Pipeline

```text
Survey Evidence Export
-> Signal
-> AtlasNode
-> provisional AtlasRoleAssignment
-> PossibleAtlasUpdateCandidate
-> AtlasDigestView
```

## Public Label Policy

Current Alpha default:

```text
Canonical may provide IDs and internal labels as metadata. UI/Atlas must not present family/archetype labels as user-facing meaning unless Product requests and Canonical approves a public-label contract.
```

Dependency trigger:

```text
If Atlas or UI needs human-readable graph meaning, create a public family/archetype label policy task before surfacing labels.
```
