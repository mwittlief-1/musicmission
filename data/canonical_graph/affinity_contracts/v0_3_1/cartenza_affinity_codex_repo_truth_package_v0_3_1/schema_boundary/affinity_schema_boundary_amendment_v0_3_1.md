# Cartenza Affinity Schema Boundary Amendment v0.3.1

## PM decision encoded

Affinity ontology v0.2.2 and sparse tagging rules v0.3 are approved as the current controlled tagging basis. Graph-wide tagging remains conditional on this schema-boundary amendment. Runtime ingestion remains not approved.

## Problem fixed

The sparse pilot proved the ontology and sparsity rules, but it also exposed a layer leak: social/use-case context can bleed into core song truth when the same song or composition appears under different graph surfaces.

The clearest pattern is a canonical song appearing as both an intrinsic music object and a contextual/shared-listening object. In that case, karaoke/family/holiday/worship/social behavior should not rewrite the core song profile.

## New boundary

### 1. Canonical song affinity tags

Stable, intrinsic song-level features. These describe the recording/song itself and should remain stable regardless of family, archetype, survey page, or mission surface.

Core dimensions:

```text
vocal_performance
emotion_theme
sonic_texture
rhythm_body
form_container
```

### 2. Membership / route-context overlays

Contextual use-case and routing behavior tied to a specific membership, family, archetype, role, survey surface, or mission surface.

Overlay dimensions:

```text
social_context
routing_caution
```

## Required output shape

```json
{
  "canonical_song_recording_id": "existing graph ID only",
  "canonical_song_affinity_tags": {
    "vocal_performance": {"primary": [], "secondary": []},
    "emotion_theme": {"primary": [], "secondary": []},
    "sonic_texture": {"primary": [], "secondary": []},
    "rhythm_body": {"primary": [], "secondary": []},
    "form_container": {"primary": [], "secondary": []}
  },
  "membership_context_overlays": [
    {
      "membership_id": "song_archetype_memberships.membership_id if available",
      "family_number": null,
      "archetype_id": "",
      "membership_roles": [],
      "social_context": {"primary": [], "secondary": []},
      "routing_caution": {"primary": [], "secondary": []},
      "overlay_notes": ""
    }
  ]
}
```

## Hard rules

1. Do not let family/archetype/mission context rewrite core song features.
2. `social_context` and `routing_caution` belong primarily in `membership_context_overlays`.
3. Core song tags describe the song itself, not how a mission uses it.
4. If the same composition/recording appears under multiple IDs or contexts, flag duplicate/context review.
5. A contextual surface may add overlay tags, but it may not create a different intrinsic profile.
6. Empty overlay dimensions are allowed and expected.
7. Empty core dimensions are allowed when a dimension is not route-bearing.
8. Alias leakage remains a hard fail.
9. Non-canonical tags remain a hard fail.

## Example: Bohemian Rhapsody pattern

Core song affinity should describe the record: theatrical/operatic delivery, suite-like or album-world structure, choral/guitar/studio architecture, and anthemic build.

Karaoke/shared-listening behavior belongs in `membership_context_overlays` for the context surface. It should not make the core song profile become `dancefloor + celebration` unless those tags are genuinely intrinsic to the song.

## Example: Family 17/context surfaces

Family/shared-listening songs may have strong `family_shared_context`, `holiday_context`, `karaoke_context`, `novelty_context`, or `worship_context` overlays. Those overlays do not imply that the song intrinsically has dancefloor, synthetic texture, romantic longing, or celebration core features.

## Approval status

```text
Affinity ontology v0.2.2: APPROVED
Sparse tagging rules v0.3: APPROVED
Schema boundary amendment v0.3.1: PREPARED FOR PM ACCEPTANCE
Graph-wide tagging: CONDITIONALLY READY AFTER PM ACCEPTS THIS AMENDMENT
Runtime ingestion: NOT APPROVED
```
