# Import Warnings - Family 3

| warning_type | value | import_action |
| --- | --- | --- |
| source_role_shorthand | adult_pop; album_exception; album_exception_artist; album_first; album_world; art_glam; artist_anchor_album; boogie_anchor; boundary_test; bridge_album; critical_canon_album; cult_album; cult_anchor; cultural_furniture; depth; era_anchor; family_context; frontier; gateway_album; gateway_song; guitar_anchor; hard_rock; instrumental_anchor; jam_bridge; karaoke_anchor; live_album; mainstream_anchor; one_hit; one_hit_artist; popular_canon_album; proto_punk_bridge; radio_memory; regional_anchor; revival_anchor; scene_anchor; scene_anchor_album; singles_artist; smooth_pop; soft_anchor; soft_to_yacht; song_anchor; song_exception; soundtrack_anchor; specialist_anchor; studio_anchor; studio_pop; theatrical; wedding_anchor | Mapped to approved role enum; original shorthand not emitted in JSON roles. |
| source_recognition_shorthand | broad_anchor; cult_known; lane_anchor; mass_known; scene_known | Mapped to mass/high/medium/low/cult. |
| source_survey_shorthand | tier_0; tier_1; tier_2; tier_3 | Mapped to core/standard/edge/suppress. |
| source_album_type_shorthand | compilation_gateway | Mapped compilation_gateway to compilation; retained compilation_gateway as role. |
| row_repair | Line 95: malformed album row for Alive! had duplicate artist token 'Kiss'; removed before import. | Corrected in normalized candidate rows. |
| row_repair | Line 135: missing proposed_artist_id for Rush; generated artist-rush. | Corrected in normalized candidate rows. |
| row_repair | Line 349: missing proposed_artist_id for Chicago; generated artist-chicago. | Corrected in normalized candidate rows. |
| row_repair | Line 350: missing proposed_artist_id for Fleetwood Mac; generated artist-fleetwood-mac. | Corrected in normalized candidate rows. |
| row_repair | Line 351: missing proposed_artist_id for Eagles; generated artist-eagles. | Corrected in normalized candidate rows. |
| row_repair | Line 352: missing proposed_artist_id for America; generated artist-america. | Corrected in normalized candidate rows. |
| row_repair | Line 353: missing proposed_artist_id for Bread; generated artist-bread. | Corrected in normalized candidate rows. |
| row_repair | Line 354: missing proposed_artist_id for Carpenters; generated artist-carpenters. | Corrected in normalized candidate rows. |
| row_repair | Line 355: missing proposed_artist_id for Seals & Crofts; generated artist-seals-and-crofts. | Corrected in normalized candidate rows. |
| row_repair | Line 356: missing proposed_artist_id for Hall & Oates; generated artist-hall-and-oates. | Corrected in normalized candidate rows. |
| row_repair | Line 357: missing proposed_artist_id for The Doobie Brothers; generated artist-the-doobie-brothers. | Corrected in normalized candidate rows. |
| row_repair | Line 358: missing proposed_artist_id for Boz Scaggs; generated artist-boz-scaggs. | Corrected in normalized candidate rows. |
| row_repair | Line 407: missing proposed_artist_id for Kenny Loggins; generated artist-kenny-loggins. | Corrected in normalized candidate rows. |
| row_repair | Line 408: missing proposed_artist_id for Ambrosia; generated artist-ambrosia. | Corrected in normalized candidate rows. |
| row_repair | Line 409: missing proposed_artist_id for Pages; generated artist-pages. | Corrected in normalized candidate rows. |
| row_repair | Line 410: missing proposed_artist_id for Robbie Dupree; generated artist-robbie-dupree. | Corrected in normalized candidate rows. |
| duplicate_membership_expected | Same canonical objects appear across multiple archetypes, e.g. Pink Floyd, Rumours, Lowdown, A Night at the Opera. | Treat rows as archetype memberships, not duplicate object merges. |
| ambiguous_versions | Live vs studio versions and cover-adjacent later memories are not merged. | Requires downstream version-aware matching. |
| strict_yacht_boundary | Eagles, Fleetwood Mac, Hall & Oates, and Player are not promoted to strict yacht anchors by default. | Use consolidation_warning and false_nearby roles to avoid overclassification. |

## Second-Pass Cross-Check Warnings

- Reviewed `F3-2.md` and merged curated additions into `normalized_family_3.json`.
- Several source terms in the second-pass files used non-enum labels such as `broad_anchor`, `tier_2`, `gateway_song`, `album_exception`, `regional_known`, and `specialist_known`; accepted rows were normalized to the approved enum sets.
- Deferred rows remain editorial candidates only. Do not auto-import all second-pass collector/depth suggestions without a separate thresholding pass.
