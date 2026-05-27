# Corrections To Source Report - Family 3

| source_issue | correction |
| --- | --- |
| Non-enum recognition tiers | Mapped mass_known->mass, broad_anchor->high, lane_anchor->medium, scene_known->low, cult_known->cult. |
| Non-enum survey tiers | Mapped tier_0->core, tier_1->standard, tier_2/tier_3->edge. |
| Album object type compilation_gateway | Normalized album_object_type to compilation while preserving compilation_gateway role. |
| Underscore IDs | Converted all proposed IDs to lowercase kebab-case slugs. |
| Missing proposed_artist_id values | Generated IDs for Rush, Chicago, Fleetwood Mac in 022, Eagles in 022, America, Bread, Carpenters, Seals & Crofts, Hall & Oates, The Doobie Brothers in 022, Kenny Loggins, Ambrosia, Pages, and Robbie Dupree. |
| Malformed Alive! album row | Removed extra artist token after album_alive_1975 and imported release_year=1975, album_object_type=live_album. |
| Non-ASCII album title in source | Rendered Pronounced Leh-nerd Skin-nerd in ASCII for import stability; slug remains album-pronounced-leh-nerd-skin-nerd-1973. |
| Distinct live/public versions | Kept I Want You to Want Me (live), Show Me the Way (live), and live-gateway albums distinct; no studio/live merges inferred. |
