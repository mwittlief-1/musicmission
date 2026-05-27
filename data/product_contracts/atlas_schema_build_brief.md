# Atlas Schema Build Brief

Generated: 2026-05-20

Working title:

```text
Atlas Schema Contract v0.1: User Interpretation Layer
```

## Purpose

Define the missing middle contract that lets Survey, Mission Generation, Candidate Pool Builder, Mission Review, and Atlas visualization speak the same language.

This is not the canonical music graph schema. It is the user-specific interpretation schema above the canonical graph.

## Core Boundary

```text
Canonical graph = music-object substrate
Atlas schema = user-specific interpretation layer
```

Survey, Mission Generation, and Mission Review must not mutate the canonical graph.

They create or update:

- Signals
- provisional Atlas state
- role assignments
- update candidates
- user-specific taste feature state

## Music Object Reference Union

Atlas must support objects that do not exist in the canonical graph.

Use a typed music reference rather than a single string:

```json
{
  "object_type": "artist | album | song_recording | composition_placeholder",
  "ref_source": "canonical_graph | user_local | external_catalog | unresolved",
  "canonical_artist_id": null,
  "canonical_album_id": null,
  "canonical_song_recording_id": null,
  "composition_placeholder_id": null,
  "user_music_object_id": null,
  "external_catalog_refs": {},
  "display_name": "",
  "resolution_state": "resolved | needs_resolution | intentionally_user_local",
  "composition_policy_status": "resolved | needs_review | not_applicable"
}
```

## Required Persistent Objects

### AtlasNode

Represents the thing.

Can represent:

- artist
- album
- song recording
- composition placeholder
- scene
- era
- genre/lane
- taste feature when renderable
- user-defined concept
- mission-derived concept

`AtlasNode` should not own authoritative role truth.

### AtlasRoleAssignment

Represents how a node functions for a user in a scope.

Authoritative role values for v0.1:

- `landmark`
- `region`
- `frontier`
- `dead_end`
- `waypoint`
- `unknown`
- `signal_only`

Do not include `road` and `lineage` as ordinary roles in v0.1.

### Road

A grouping or route structure used by Atlas and Mission Generation.

It may connect landmarks, waypoints, frontiers, and dead ends, but it should not blur with `AtlasRoleAssignment`.

### Lineage

An edge/network view over canonical and Atlas nodes.

Represent through edges, not role assignment.

### TasteFeature

Global feature registry.

Examples:

- `body_force`
- `hooks_under_pressure`
- `album_world`
- `hard_persona_pop`
- `fake_hard`
- `no_blood`
- `waypoint_not_landmark`

### UserTasteFeatureState

User-specific state for a global Taste Feature.

Example:

`body_force` may be globally defined, but for one user it may be high-confidence and tied to Nirvana, Local H, and Muse.

### Signal

Durable evidence ledger.

Sources include:

- survey
- mission
- open_road
- import
- note
- review
- playback

Split:

- `signal_strength`
- `interpretation_confidence`

A skip is a real event but weak taste evidence. A specific note can be low-volume but high interpretive value.

### UserVocabularyTerm

Stores user language that can later become chip or Atlas copy.

### PossibleAtlasUpdateCandidate

Mission Review and Survey should produce possible updates before promotion.

This prevents generated hypotheses from becoming accidental Atlas state.

## Lifecycle Fields

Use distinct fields:

```text
status: active | suppressed | archived | provisional
review_state: unreviewed | needs_review | reviewed | rejected
promotion_state: proposed | candidate | promoted | demoted | blocked
```

## Confidence Fields

Use a shared confidence shape:

```text
confidence_score: 0.0-1.0
confidence_band: low | medium | high
confidence_basis: enum + short summary
```

## Required Write Paths

### Survey Event -> Provisional Atlas State

Survey creates:

- Signal
- possible UserVocabularyTerm
- provisional AtlasNode if needed
- provisional AtlasRoleAssignment candidate
- possible Atlas update candidate

Survey should not create promoted Landmarks, Regions, Frontiers, Dead Ends, or Waypoints without evidence thresholds/review.

### Mission Review Event -> Evidence-Backed Update Candidate

Mission Review creates:

- Signal
- candidate role changes
- confidence delta
- recurrence requirement
- review requirement
- promote/demote/block recommendation

Mission Review should not auto-promote unless a later policy explicitly allows it.

## Digest Views

Mission Generation should not consume raw Atlas tables directly.

Define an Atlas Digest View containing:

- relevant Landmarks
- relevant Regions
- relevant Frontiers
- relevant Dead Ends
- relevant Waypoints
- user Taste Feature states
- user vocabulary terms
- anti-overfitting rules
- recent signals
- unresolved questions
- mission-relevant constraints
- suggested candidate roles

Candidate Pool Builder should consume `AtlasRoleAssignment` and digest views, not raw `AtlasNode`.

## Example Records Required In Schema Contract

The full v0.1 contract should include examples for:

- Landmark
- Region
- Frontier
- Dead End
- Waypoint
- Signal
- Taste Feature
- UserTasteFeatureState
- Survey-seeded Atlas update
- Mission-review possible Atlas update
- canonical music-object reference
- non-canonical user-local music-object reference

## Acceptance Criteria

Atlas Schema v0.1 is sufficient when it can support:

1. Survey creates starter Atlas state without final verdicts.
2. Mission Generation consumes an Atlas Digest.
3. Candidate Pool Builder can query anchors, bridges, probes, risky probes, waypoints, and traps.
4. Mission Review records Signals and possible updates without overpromotion.
5. Atlas UI can render basic Landmark, Region, Frontier, Dead End, and Waypoint cards.
6. Evidence remains auditable back to survey, mission, note, reaction, tag, skip, playback, import, or review signal.
