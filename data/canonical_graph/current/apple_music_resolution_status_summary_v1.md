# Apple Music Resolution Status Summary v1

Date: 2026-05-29

Status: excellent enough for core app integration.

This note summarizes the Apple Music tagging and album sidecar work completed against the current canonical graph. It is intended as a posterity/handoff document, not as a new source ledger. The source ledgers remain the pass directories, JSONL link files, sidecar files, and app catalog index listed below.

## Product Posture

Apple Music is treated as a live resolver and playback/linking layer, not as Cartenza's canonical graph database.

Persisted Apple-related data in this pass is intentionally limited to catalog identifiers, storefront, catalog URLs where useful, source refs, match metadata, and Cartenza-side status/decision fields. We did not persist raw Apple payloads, artwork blobs, previews, lyrics, MusicKit playback content, Music User Tokens, or Apple music-video IDs.

## Where We Landed

| Area | Current status |
| --- | --- |
| Graph artist anchors | 1,895 Apple artist links are present for graph artist-anchor refs. Six graph artist refs are intentionally handled as special/split/do-not-present statuses rather than ordinary Apple artist links. |
| Graph albums | 2,112 graph album refs have Apple album links. 50 graph/sidecar album identities remain without Apple album IDs. |
| Graph songs/recordings | 7,049 graph song/recording refs are linked for app use: 6,671 graph songs and 378 graph recordings. The remaining identity-level graph gap is 200 rows: 179 songs and 21 recordings. |
| Album sidecar albums | 2,162 sidecar album identities exist. 2,112 have Apple album IDs and 50 do not. |
| Album sidecar tracks | 29,610 sidecar track rows exist after the Apple tracklist authority rebuild. 28,538 have Apple song IDs. 1,072 are missing Apple song IDs, all under albums that do not have Apple album IDs. |
| Replacement album links | 14 replacement album links were created for unavailable original graph albums. 13 are promotable into the album sidecar policy; 1 is a playlist fallback retained outside the album sidecar. |
| App resolver index | `MusicAtlasController/Resources/canonical_apple_music_catalog_index_v1.json` contains 9,160 compact app resolver entries and is wired before live MusicKit catalog search. |

## App Integration

The core app flow now has a bundled resolver index:

- `MusicAtlasController/Resources/canonical_apple_music_catalog_index_v1.json`
- `MusicAtlasController/Services/CanonicalAppleMusicCatalogIndex.swift`
- `MusicAtlasController/Services/MusicSearchService.swift`
- `scripts/build_app_apple_music_catalog_index_v1.mjs`
- `data/canonical_graph/current/app_apple_music_catalog_index_v1_manifest.md`

The current app index contains:

| Metric | Count |
| --- | ---: |
| Entries total | 9,160 |
| Graph song/recording entries | 7,049 |
| Graph album playable entries | 2,111 |
| Unique Apple song IDs | 8,657 |
| Sidecar track expansion entries | 0 |

The app index is deliberately compact. It includes graph song/recording refs and graph album playable seed refs. It does not bundle the full sidecar track expansion by default; the generator supports that later with `--include-sidecar-tracks` if we decide the runtime needs it.

The resolver order is now:

1. Check the bundled canonical Apple Music catalog index.
2. Return a cached `AppleMusicResolution` when a matching route/candidate key is present.
3. Fall back to live MusicKit catalog search only when the canonical index cannot resolve the item.

Validation performed:

- `node --check scripts/build_app_apple_music_catalog_index_v1.mjs`
- JSON parse/count check for `canonical_apple_music_catalog_index_v1.json`
- Entry-level scan confirming no persisted music-video resources or forbidden payload fields
- Targeted Xcode test: `MissionDecodingTests.testLiveResolverUsesCanonicalAppleMusicIndexBeforeCatalogSearch`

The full Xcode suite compiled and ran on an available `iPhone 17, OS 26.5` simulator, but one existing survey test failed outside this Apple Music integration slice: `SurveyTests.testArtistPageTwoDoesNotRepeatDislikedPriorObjects`.

## What We Tried

Resolution proceeded in layered passes rather than one brittle search pass:

- First-pass Apple Music link pass across artists, albums, songs, recordings, and sidecar inputs.
- Try-harder album/track matching using album-sidecar context.
- Residual track matching for album-sidecar rows.
- Album variant matching for remasters, artist-name-stripped titles, title-core matches, compilation variants, and tracklist-compatible alternates.
- Offline reconciliation of graph song/recording review rows against sidecar tracks that already had Apple IDs.
- Artist album resolver pass using known Apple artist IDs and artist album payloads transiently, especially for album ID resolution.
- High-confidence album pass using strong tracklist/title/edition evidence.
- Manual album review pass for user-approved high-confidence candidates.
- Semantic album hardening pass for obvious same-artist or semantically equivalent album matches that scripted fuzzy logic was too conservative to accept.
- Album graph decision pass for unavailable originals, replacement nodes, playlist fallbacks, and future-resolve decisions.
- Direct song hardening passes using stricter title, artist, year, participant, and collaboration heuristics.
- Recording hardening pass for residual recording rows.
- Song source album reconciliation and graph song iterative hardening using resolved album tracklists, sidecar-linked tracks, direct search, and replacement album context.
- Sidecar track album-bound pass for missing sidecar track IDs.
- Sidecar tracklist authority rebuild: for albums with accepted Apple album IDs, Apple Music catalog song relationships became the sidecar track-row authority.

## Important Decisions

- Apple Music album tracks are now the truth for sidecar tracks when the sidecar album has an accepted Apple album ID.
- Music-video relationship entries were dropped from the sidecar authority pass, and Apple music-video IDs are not persisted.
- Expanded editions are avoided when an original or acceptable remaster exists. Expanded editions can still appear only where they are the best available practical catalog anchor.
- Soundtrack album matching is allowed to ignore strict album-artist matching when the album identity and tracklist make the candidate clear.
- Original graph album nodes are preserved when an album is unavailable on Apple Music. Replacements are represented as additional linked nodes rather than silently mutating away the original target.
- Playlist fallbacks are allowed as explicit fallbacks, but they are not promoted as normal album-sidecar albums.
- Composite/special artist entities are not forced into weak Apple artist IDs. Examples include Disney, Broadway cast entities, Red Bird Records/The Red Bird Girls, Parliament/Funkadelic, and Sam Cooke and The Soul Stirrers.
- The Comsat Angels are marked as a do-not-present-for-now style entity because available Apple Music coverage appears insufficient for the current product flow.

## Remaining Gaps

### Artists

The six intentionally unresolved/special graph artist refs are:

- `artist_anchor|comsat angels|comsat angels`: do not present for now.
- `artist_anchor|disney|disney`: special entity, not a durable Apple artist resolver.
- `artist_anchor|original broadway cast of wicked|original broadway cast of wicked`: resolve through album/song context.
- `artist_anchor|parliament funkadelic|parliament funkadelic`: split into Parliament and Funkadelic anchors.
- `artist_anchor|red bird records|red bird girls`: historical label/scene entity, not a single Apple artist.
- `artist_anchor|sam cooke and the soul stirrers|sam cooke and the soul stirrers`: split into Sam Cooke and The Soul Stirrers anchors.

### Albums

There are 50 sidecar/graph album identities without Apple album IDs. Known patterns include:

- Apple Music licensing/catalog gaps.
- Historical albums not available as albums but partially represented by compilations or later collections.
- Albums where a playlist fallback is more honest than an album substitution.
- Original Broadway/cast-recording specificity issues where "original" versus year-specific productions matter.
- Cases where a graph replacement node is more product-honest than forcing the original target to a weak Apple match.

Two important examples already called out:

- `album|my bloody valentine|loveless`: known catalog/licensing gap; reject unrelated lookalike candidates.
- `album|link wray|link wray and the wraymen`: not available as the target album; needs a better replacement decision rather than a weak album match.

### Graph Songs And Recordings

The remaining graph song/recording gap is 200 identity rows: 179 songs and 21 recordings.

Patterns observed in the residual queue:

- Version/remix/live/dub ambiguity where a weak match would be worse than no match.
- Title collisions with incompatible artists.
- Compilation-only or unavailable source contexts.
- Older recordings where Apple surfaces a remaster, rerecording, compilation cut, or stereo/mono variant as the primary candidate.
- Collaboration and participant-credit cases where the expected artist is not the Apple primary artist.
- Broadway and soundtrack rows where the correct source album context matters more than search ranking.

### Album Sidecar Tracks

All missing sidecar track Apple IDs now live under albums without Apple album IDs.

That means the surprising "tracks missing despite album resolved" gap has been closed. The sidecar track work remaining is album availability work first, track work second.

## Source Ledgers

Primary summary and handoff files:

- `data/canonical_graph/current/apple_music_link_pass_v1/apple_music_resolution_run_manifest.md`
- `data/canonical_graph/current/apple_music_try_harder_pass_v1/apple_music_try_harder_manifest.md`
- `data/canonical_graph/current/apple_music_residual_track_pass_v1/apple_music_residual_track_manifest.md`
- `data/canonical_graph/current/apple_music_album_variant_pass_v1/apple_music_album_variant_manifest.md`
- `data/canonical_graph/current/apple_music_offline_reconciliation_pass_v1/apple_music_offline_reconciliation_manifest.md`
- `data/canonical_graph/current/apple_music_artist_album_resolver_pass_v1/apple_music_artist_album_resolver_manifest.md`
- `data/canonical_graph/current/apple_music_high_confidence_album_pass_v1/apple_music_high_confidence_album_manifest.md`
- `data/canonical_graph/current/apple_music_manual_album_review_pass_v1/apple_music_manual_album_review_manifest.md`
- `data/canonical_graph/current/apple_music_semantic_album_hardening_pass_v1/apple_music_semantic_album_hardening_manifest.md`
- `data/canonical_graph/current/apple_music_album_graph_decision_pass_v1/apple_music_album_graph_decision_manifest.md`
- `data/canonical_graph/current/apple_music_song_source_album_reconciliation_pass_v1/apple_music_song_source_album_reconciliation_manifest.md`
- `data/canonical_graph/current/apple_music_direct_song_hardening_pass_v1/apple_music_direct_song_hardening_manifest.md`
- `data/canonical_graph/current/apple_music_direct_song_hardening_pass_v2/apple_music_direct_song_hardening_v2_manifest.md`
- `data/canonical_graph/current/apple_music_recording_hardening_pass_v1/apple_music_recording_hardening_manifest.md`
- `data/canonical_graph/current/apple_music_graph_song_iterative_hardening_pass_v1/apple_music_graph_song_iterative_hardening_manifest.md`
- `data/canonical_graph/current/apple_music_sidecar_track_album_bound_pass_v1/apple_music_sidecar_track_album_bound_manifest.md`
- `data/canonical_graph/current/apple_music_sidecar_tracklist_authority_pass_v1/apple_music_sidecar_tracklist_authority_manifest.md`
- `data/canonical_graph/current/apple_music_artist_manual_resolution_pass_v1/apple_music_artist_manual_resolution_manifest.md`
- `data/canonical_graph/current/album_track_sidecar_manifest.md`
- `data/canonical_graph/current/album_track_sidecar_apple_id_backfill_manifest.md`
- `data/canonical_graph/current/graph_album_replacement_links_v1_manifest.md`
- `data/canonical_graph/current/app_apple_music_catalog_index_v1_manifest.md`

Primary runtime/app integration files:

- `MusicAtlasController/Resources/canonical_apple_music_catalog_index_v1.json`
- `MusicAtlasController/Services/CanonicalAppleMusicCatalogIndex.swift`
- `MusicAtlasController/Services/MusicSearchService.swift`
- `scripts/build_app_apple_music_catalog_index_v1.mjs`

## Suggested Future Closure Path

1. Treat the current state as sufficient for alpha app flow.
2. Keep unresolved album originals in the graph, but tag them as Apple Music unavailable where confirmed.
3. Add replacement nodes only when the replacement is product-honest and Apple-resolvable.
4. Re-run the app catalog index generator after any accepted graph, album replacement, or sidecar changes.
5. Defer the final 200 graph song/recording rows until we have a manual review UI or a stronger album-context review workflow.
6. Do not broaden persistence beyond IDs, storefront, URLs, and match metadata without separate legal/product review.
