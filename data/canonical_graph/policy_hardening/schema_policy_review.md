# Schema Policy Review

Generated: 2026-05-20

## Judgment

The current simplified enum schema is sufficient for staging import. It validates cleanly, keeps artist/album/song rows distinct, and supports the importer contract of canonical entities plus archetype membership rows.

It is not sufficient for final canonical lock. Several research concepts were intentionally collapsed into broad enums or free-text warnings. That was the right staging tradeoff, but production import needs those concepts preserved as structured metadata before user-facing survey logic depends on them.

## Current Schema Fitness

| area | staging verdict | final-lock concern |
|---|---|---|
| `recognition_tier` | Sufficient as a broad exposure signal. | It does not distinguish canon recognition, radio recognition, meme recognition, regional recognition, soundtrack recognition, or platform-recency recognition. |
| `survey_tier` | Sufficient for first-pass row inclusion. | It mixes row priority with survey placement; Page 1/Page 2 decisions need more policy. |
| `roles` | Sufficient for compact staging import. | It mixes object function, survey function, membership function, and warning semantics. |
| `album_object_type` | Sufficient for core object separation. | It needs eventual extensions or companion metadata for cast album, score album, curated soundtrack, anthology, DJ mix, mixtape, and holiday compilation. |
| `artist_survey_status` | Sufficient for song rows. | It should eventually split artist survey worthiness from song-first display strategy. |
| `consolidation_warning` | Useful staging escape valve. | Too much final-lock policy currently lives in free text. |

## Collapsed Research Concepts

The current schema collapses these richer concepts:

| collapsed concept | currently represented by | preserve as |
|---|---|---|
| Canon recognition vs normal-user recognition | `recognition_tier` | `recognition_basis` tag: canon, radio, streaming, soundtrack, meme, regional, scene, collector |
| Page placement vs object importance | `survey_tier` | `survey_surface_priority`, `atlas_depth_priority` |
| Artist-level importance vs song-first importance | `roles`, `artist_survey_status` | `object_specificity`, `survey_display_mode` |
| Bridge vs boundary vs false-nearby | `roles` | Keep role, add `boundary_target_family_ids` and `false_nearby_reason` |
| Compilation/live/cast/soundtrack gateway behavior | `album_object_type`, `roles` | `gateway_object_context`, `recording_context` |
| Covers/source/live/remix/clean-explicit | `consolidation_warning` | `recording_variant_type`, `composition_id`, `source_recording_id` |
| Alias/project/group/solo distinctions | slug plus warning | `canonical_artist_id`, `credited_artist_name`, `alias_group_id`, `artist_entity_type` |
| Traditional/standard/show/worship ownership | warning text | `composition_model_required`, `composition_origin_type` |
| Recency volatility | warnings and family notes | `freshness_policy`, `review_after_date`, `volatility_tier` |

## Separation Of Core Fields

`recognition_tier`, `survey_tier`, and `roles` are separated enough for staging import:

- `recognition_tier` answers: how likely is a normal listener to recognize this object?
- `survey_tier` answers: how much should this row participate in surveys now?
- `roles` answers: why is this row useful inside an archetype?

They are not separated enough for production survey tuning. A mass-recognition object can be a bad artist survey row, a great song survey row, and a poor atlas anchor. Examples include one-hit novelty songs, soundtrack singles, explicit-only hip-hop rows, and worship standards where the composition matters more than one artist.

## Role Split Recommendation

Split `roles` before final lock into four related fields. Keep the current `roles` array as backward-compatible staging input until the split is implemented.

| proposed field | examples | purpose |
|---|---|---|
| `object_role` | artist_anchor, album_anchor, song_first, live_gateway, compilation_gateway | What kind of graph object is this? |
| `survey_role` | page1_anchor, page2_depth, contrast_probe, suppress_candidate | How should it behave in survey flow? |
| `membership_role` | core_member, bridge_member, boundary_member, false_nearby | How does it relate to an archetype/family? |
| `warning_flags` | cover_version, alias_review, composition_review, explicit_clean_split, cast_entity_review | What QA rule must run before lock? |

## Preserve Before Production Import

These additions should be implemented as metadata or sidecar tables before user-facing survey tests:

- `artist_aliases`: canonical artist, display alias, credit alias, group/solo relation, project alias.
- `recording_variants`: original, hit cover, source version, live, radio edit, remix, clean, explicit, cast recording.
- `composition_review_queue`: composition key, candidate recordings, recommended composition policy.
- `entity_context`: show, film, church brand, fictional performer, producer project, Various Artists.
- `review_flags`: structured flags copied from `consolidation_warning`.

## Staging Decision

Use the simplified enum schema for backend staging tests. Do not use it alone for final canonical lock or final user-facing survey weighting.
