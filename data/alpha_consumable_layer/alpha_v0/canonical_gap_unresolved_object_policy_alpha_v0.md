# Canonical Gap and Unresolved Object Policy Alpha v0

Version: `alpha_v0`

Status: `frozen_for_alpha_consumable_layer`

This policy defines how downstream lanes represent music objects that are missing from the canonical graph, unresolved, externally sourced, user-local, or composition-first.

## Core Rule

Objects can exist in a user's Atlas without existing in the canonical database.

The canonical graph is a shared substrate, not the full world catalog. Missing graph coverage must not block user evidence capture.

## Allowed Reference Paths

Use Atlas-aligned `music_object_ref` paths:

| path | Use |
| --- | --- |
| `canonical_graph` | Approved canonical artist, album, or song recording from Alpha surfaces. |
| `user_local` | Object exists only in a user's library, notes, imports, or local Atlas. |
| `external_catalog` | Object is known through Apple Music or another catalog but not matched to the graph. |
| `unresolved` | Object is named or implied but cannot yet be resolved. |
| `composition_placeholder` | Composition/work identity matters before a concrete recording can be selected. |

Schema:

```text
data/alpha_consumable_layer/alpha_v0/atlas_music_object_ref_alpha_v0.schema.json
```

Guide:

```text
data/alpha_consumable_layer/alpha_v0/graph_to_atlas_music_object_ref_alpha_v0.md
```

## What Downstream Lanes May Do

Survey, Core, Mission, and Atlas may:

- preserve user evidence against `user_local`, `external_catalog`, `unresolved`, or `composition_placeholder` refs
- create provisional Signals and PossibleAtlasUpdateCandidates against non-canonical refs
- ask for resolver/manual review later
- keep user-visible display names when needed
- retain Apple catalog IDs as external refs

## What Downstream Lanes Must Not Do

Downstream lanes must not:

- mutate the canonical graph
- invent canonical IDs
- merge by title or display name
- treat Apple catalog identity as canonical truth
- treat graph family/archetype membership as user taste
- promote Atlas roles from graph metadata
- use composition placeholders as concrete playable recordings

## Default Handling

| situation | Alpha handling |
| --- | --- |
| user library object missing from graph | `ref_source=user_local` or `external_catalog` depending source. |
| Apple track not matched to graph | `ref_source=external_catalog`, `resolution_state=needs_resolution`. |
| user note names an uncertain object | `ref_source=unresolved`, `resolution_state=needs_resolution`. |
| same-title standard/work ambiguity | `object_type=composition_placeholder`, block default playback until concrete recording chosen. |
| graph candidate exists but is quarantined | do not use canonical ref for product surface; route to QA/manual review. |

## Promotion Boundary

Non-canonical refs may accumulate evidence in Atlas, but promotion semantics belong to Atlas. The graph lane supplies identity and safety metadata only.
