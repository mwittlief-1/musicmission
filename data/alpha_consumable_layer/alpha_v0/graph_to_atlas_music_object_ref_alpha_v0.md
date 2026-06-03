# Graph to Atlas music_object_ref Adapter Alpha v0

Version: `alpha_v0`

Status: `frozen_for_alpha_consumable_layer`

Schema:

```text
data/alpha_consumable_layer/alpha_v0/atlas_music_object_ref_alpha_v0.schema.json
```

This adapter aligns graph-derived Alpha candidates to the Atlas `music_object_ref` union:

```text
canonical_graph | user_local | external_catalog | unresolved
artist | album | song_recording | composition_placeholder
```

The reference is identity and resolution context only. It is never user taste, never an Atlas role, and never a promotion decision.

## Core Rule

Graph metadata can be preserved as reference context:

- family number
- archetype IDs
- source membership ID
- candidate ID
- survey intent
- version/resolution policy

Graph metadata must not be interpreted as user-specific truth:

- not Landmark
- not Region
- not Frontier
- not Dead End
- not Waypoint
- not confidence
- not affinity
- not rejection

## Canonical Graph Path

Use this path for approved Alpha candidates from canonical graph surfaces.

### Artist

```json
{
  "object_type": "artist",
  "ref_source": "canonical_graph",
  "canonical_artist_id": "aretha-franklin",
  "canonical_album_id": null,
  "canonical_song_recording_id": null,
  "composition_placeholder_id": null,
  "user_music_object_id": null,
  "external_catalog_refs": {},
  "display_name": "Aretha Franklin",
  "credited_artist_name": null,
  "credit_context": "unknown",
  "resolution_state": "resolved",
  "composition_policy_status": "not_applicable",
  "recording_variant_type": null,
  "canonical_membership_context": {
    "family_numbers": [6],
    "archetype_ids": ["038"],
    "membership_role_notes": "Graph membership context only; not user taste."
  }
}
```

### Album

```json
{
  "object_type": "album",
  "ref_source": "canonical_graph",
  "canonical_artist_id": null,
  "canonical_album_id": "marvin-gaye-whats-going-on",
  "canonical_song_recording_id": null,
  "composition_placeholder_id": null,
  "user_music_object_id": null,
  "external_catalog_refs": {},
  "display_name": "What's Going On",
  "credited_artist_name": null,
  "credit_context": "unknown",
  "resolution_state": "resolved",
  "composition_policy_status": "not_applicable",
  "recording_variant_type": null,
  "canonical_membership_context": {
    "family_numbers": [6],
    "archetype_ids": ["037"],
    "membership_role_notes": "Graph membership context only; not user taste."
  }
}
```

### Song Recording

```json
{
  "object_type": "song_recording",
  "ref_source": "canonical_graph",
  "canonical_artist_id": null,
  "canonical_album_id": null,
  "canonical_song_recording_id": "michael-jackson-billie-jean",
  "composition_placeholder_id": null,
  "user_music_object_id": null,
  "external_catalog_refs": {},
  "display_name": "Billie Jean",
  "credited_artist_name": "Michael Jackson",
  "credit_context": "unknown",
  "resolution_state": "resolved",
  "composition_policy_status": "no_review_needed",
  "recording_variant_type": "studio",
  "canonical_membership_context": {
    "family_numbers": [12],
    "archetype_ids": ["088"],
    "membership_role_notes": "Graph membership context only; not user taste."
  }
}
```

## User-Local Path

Use this path when an object exists in one user's Atlas or library but not in the canonical graph.

```json
{
  "object_type": "song_recording",
  "ref_source": "user_local",
  "canonical_artist_id": null,
  "canonical_album_id": null,
  "canonical_song_recording_id": null,
  "composition_placeholder_id": null,
  "user_music_object_id": "user_music_object:local:abc123",
  "external_catalog_refs": {},
  "display_name": "Untitled local demo",
  "credited_artist_name": "Local Artist",
  "credit_context": "unknown",
  "resolution_state": "intentionally_user_local",
  "composition_policy_status": "not_applicable",
  "recording_variant_type": "unknown"
}
```

User-local objects may enter Atlas as user-specific references. They must not mutate the canonical graph.

## External Catalog Path

Use this path when Apple Music, another catalog, or import data identifies an object that has not yet been matched to the canonical graph.

```json
{
  "object_type": "song_recording",
  "ref_source": "external_catalog",
  "canonical_artist_id": null,
  "canonical_album_id": null,
  "canonical_song_recording_id": null,
  "composition_placeholder_id": null,
  "user_music_object_id": null,
  "external_catalog_refs": {
    "apple_music_song_id": "1234567890"
  },
  "display_name": "Catalog-only track",
  "credited_artist_name": "Catalog Artist",
  "credit_context": "unknown",
  "resolution_state": "needs_resolution",
  "composition_policy_status": "needs_review",
  "recording_variant_type": "unknown"
}
```

Apple catalog presence is exposure/resolution context only. It is not taste proof.

## Unresolved Path

Use this path when a user, import, survey note, or mission review references an object that cannot yet be resolved.

```json
{
  "object_type": "artist",
  "ref_source": "unresolved",
  "canonical_artist_id": null,
  "canonical_album_id": null,
  "canonical_song_recording_id": null,
  "composition_placeholder_id": null,
  "user_music_object_id": null,
  "external_catalog_refs": {},
  "display_name": "Unknown artist from user note",
  "credited_artist_name": null,
  "credit_context": "unknown",
  "resolution_state": "needs_resolution",
  "composition_policy_status": "not_applicable",
  "recording_variant_type": null
}
```

Unresolved objects can preserve evidence. They must not be collapsed into canonical rows by title or display name.

## Composition-Placeholder Path

Use this path when the product needs composition-first handling before a recording can be safely chosen.

```json
{
  "object_type": "composition_placeholder",
  "ref_source": "unresolved",
  "canonical_artist_id": null,
  "canonical_album_id": null,
  "canonical_song_recording_id": null,
  "composition_placeholder_id": "composition_placeholder:house-of-the-rising-sun",
  "user_music_object_id": null,
  "external_catalog_refs": {},
  "display_name": "House of the Rising Sun",
  "credited_artist_name": null,
  "credit_context": "unknown",
  "resolution_state": "needs_resolution",
  "composition_policy_status": "composition_first_required",
  "recording_variant_type": "traditional_arrangement"
}
```

Composition placeholders are allowed for Atlas evidence and review. They are not default first-mission route items unless a human or resolver policy chooses a specific recording.

## Candidate Adapter Rules

For Alpha graph candidates:

| candidate object_type | music_object_ref mapping |
| --- | --- |
| `artist` | `ref_source=canonical_graph`, `canonical_artist_id=canonical_entity_id` |
| `album` | `ref_source=canonical_graph`, `canonical_album_id=canonical_entity_id` |
| `song_recording` | `ref_source=canonical_graph`, `canonical_song_recording_id=canonical_entity_id` |

For Survey Evidence Export atoms, the visible Survey `music_object_ref.object_type` remains typed as:

- `artist`
- `album`
- `song_recording`

Playback-ready Mission candidate pools may expose app route `object_type = track|album`, but their nested `music_object_ref.object_type` must still point back to `song_recording` or `album`.

Always include:

- `display_name`
- `resolution_state`
- `composition_policy_status`
- `canonical_membership_context.family_numbers`
- `canonical_membership_context.archetype_ids`
- `canonical_membership_context.membership_role_notes`

For song recordings, enrich when available from `canonical_recording_versions.json`:

- `credited_artist_name`
- `recording_variant_type`
- `composition_policy_status`

## Recording Variant Mapping

| recording_context | recording_variant_type |
| --- | --- |
| `original` | `studio` |
| `album_version` | `studio` |
| `single_version` | `studio` |
| `source_version` | `source` |
| `cover` | `hit_cover` |
| `remake` | `hit_cover` |
| `live` | `live` |
| `radio_edit` | `radio_edit` |
| `clean` | `clean` |
| `explicit` | `explicit` |
| `remix` | `remix` |
| `cast_recording` | `cast` |
| `film_version` | `soundtrack_pop` |
| `traditional_arrangement` | `traditional_arrangement` |

## Composition Policy Mapping

| recording sidecar state | composition_policy_status |
| --- | --- |
| approved, survey-safe, uncontested recording | `no_review_needed` |
| approved, split/source/cover/live/remix version explicitly classified | `split_confirmed` |
| manual review required | `needs_review` |
| composition-first row | `composition_first_required` |
| not a song recording | `not_applicable` |

## Blocked Interpretations

The following are invalid uses of `music_object_ref`:

- treating graph family membership as user affinity
- treating `survey_intent` as Atlas role
- treating `mission_candidate_role` as Atlas role
- treating `evidence_strength_hint` as Atlas confidence
- treating `apple_exposure_prior` as taste proof
- treating `dont_know` as negative taste
- ingesting `construction_only_excluded` Survey rows as Atlas Signals
- promoting a Landmark, Region, Frontier, Dead End, or Waypoint from graph metadata
- merging unresolved/external/user-local refs into canonical IDs without resolver review
- using a composition placeholder as if it were a concrete recording
