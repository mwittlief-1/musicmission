# Graph Hardening Pass D Freeze Manifest

Generated on 2026-05-26.

## Status

Pass D is frozen with PM-approved multi-memberships.

- Archetypes ready: 120 / 120
- Remaining effective gap: 0
- Active inventory rows: 11697
- Active Pass C rows: 4825
- Approved multi-memberships: 13
- Song tagging corpus rows: 7409
- Album sidecar seed rows: 2231
- Apple ID resolution queue rows: 7409
- Graph-linking node rows: 11309
- Unresolved rows excluded from v1: 804

## PM Decision

All 13 current-identity collisions from Pass C are approved as active multi-memberships in v1. They now live in both the existing archetype and the proposed archetype, with active effective credit in the approved archetype.

| Candidate | Existing membership | Approved added membership | Decision |
| --- | --- | --- | --- |
| Bobby Darin - Splish Splash | 001 Early Rock & Roll Foundations | 004 Teen Idol / Early Pop-Rock Radio | approved_active_multi_membership |
| Barbara Lynn - You'll Lose a Good Thing | 038 Southern Soul / Stax / Muscle Shoals | 006 Early Soul-Pop / R&B Crossover | approved_active_multi_membership |
| Nelly - Hot in Herre | 113 Party / Wedding / Karaoke / Bar Singalong Canon | 050 Pop-Rap / Mainstream Hip-Hop Crossover | approved_active_multi_membership |
| Will Smith - Men in Black | 106 Movie Soundtracks / 80s-90s-00s Soundtrack Memory | 050 Pop-Rap / Mainstream Hip-Hop Crossover | approved_active_multi_membership |
| Lauryn Hill - Ex-Factor | 043 Neo-Soul / Conscious R&B | 050 Pop-Rap / Mainstream Hip-Hop Crossover | approved_active_multi_membership |
| Doja Cat - Paint the Town Red | 093 TikTok / Streaming-Era Pop / Internet Pop | 050 Pop-Rap / Mainstream Hip-Hop Crossover | approved_active_multi_membership |
| J Dilla - Donuts | 120 Algorithmic Mood / Lo-Fi / Chill / Study Music | 051 Alternative / Experimental / Indie Rap | approved_active_multi_membership |
| Digable Planets - Rebirth of Slick (Cool Like Dat) | 046 Golden Age Hip-Hop / Conscious / Native Tongues | 051 Alternative / Experimental / Indie Rap | approved_active_multi_membership |
| Simple Minds - Don't You (Forget About Me) | 106 Movie Soundtracks / 80s-90s-00s Soundtrack Memory | 088 70s-80s Pop Sovereigns | approved_active_multi_membership |
| The Human League - Don't You Want Me | 058 Synthpop / New Romantic / 80s Electronic Pop | 088 70s-80s Pop Sovereigns | approved_active_multi_membership |
| Diana Ross - I'm Coming Out | 040 Disco / Dancefloor 70s | 088 70s-80s Pop Sovereigns | approved_active_multi_membership |
| Rihanna - Don't Stop the Music | 113 Party / Wedding / Karaoke / Bar Singalong Canon | 090 2000s Pop / Dance-Pop / Club-Pop | approved_active_multi_membership |
| Jason Mraz - I Won't Give Up | 113 Party / Wedding / Karaoke / Bar Singalong Canon | 092 Adult Pop / TV-Drama Anthem / Inspirational Pop | approved_active_multi_membership |

## Downstream Corpora

- `graph_tagging_corpus_v1`: song/recording rows ready for tagging.
- `apple_id_resolution_queue_v1`: song/recording rows ready for Apple ID matching.
- `album_sidecar_seed_albums_v1`: album rows ready for album sidecar planning.
- `atlas_archetype_profile_targets_v1`: final archetype readiness/profile targets.
- `graph_linking_node_set_v1`: identity-level graph nodes with active archetype memberships.

## Exclusions

Rows with `needs_resolution`, `exclude_or_quarantine`, or `risky_unresolved` status remain outside v1 downstream tagging/linking/resolution.
