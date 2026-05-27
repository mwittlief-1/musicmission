# Graph Staging Contract

Generated: 2026-05-20

## Current Status

The canonical music graph is staging-import ready, not final-lock ready.

Current dry-run emission:

- 18 families imported
- 0 validation errors
- 9 validation warnings
- 1499 canonical artists
- 1207 canonical albums
- 1917 canonical song recordings
- 1612 artist memberships
- 1245 album memberships
- 1983 song memberships
- 24 composition/title review rows

Primary generated files:

- `data/canonical_graph/import_dry_run/canonical_artists.json`
- `data/canonical_graph/import_dry_run/canonical_albums.json`
- `data/canonical_graph/import_dry_run/canonical_song_recordings.json`
- `data/canonical_graph/import_dry_run/artist_archetype_memberships.json`
- `data/canonical_graph/import_dry_run/album_archetype_memberships.json`
- `data/canonical_graph/import_dry_run/song_archetype_memberships.json`
- `data/canonical_graph/import_dry_run/canonical_graph_manifest.json`
- `data/canonical_graph/import_dry_run/merge_review_queue.md`
- `data/canonical_graph/import_dry_run/composition_review_queue.json`

## Intended Use

Allowed for:

- Survey simulation candidate universe
- backend staging import tests
- internal survey flow tests
- Atlas prototype references
- first-mission candidate pool experiments

Not allowed for:

- final canonical lock
- automatic title merges
- automatic cover/source/live/remix merges
- treating family-local rows as unique canonical entities
- user-facing survey prompts without duplicate/alias suppression guardrails

## Core Rule

Import and product systems should reference canonical entities plus membership rows.

```text
canonical entity ID + object type + membership context
```

Do not import normalized family rows directly as unique product objects.

## Known QA Queues

The current graph still requires human or policy-mediated review for:

- display-name aliases
- group/solo splits
- credited versus canonical artist handling
- same-title songs
- covers and source recordings
- traditional songs and standards
- worship/hymn objects
- cast/show/soundtrack objects
- remix/edit/explicit/clean variants

## Atlas Reference Policy

Atlas records should reference canonical graph IDs when available.

However, user Atlas objects may exist outside the canonical graph. Atlas and Survey schemas must support:

- canonical graph objects
- user-local music objects
- external catalog objects
- unresolved imported objects
- composition placeholders

The canonical graph is Waymark's shared staging substrate, not a complete world catalog.
