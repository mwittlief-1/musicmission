# Corrections To Source Report

| Source issue | Correction / import treatment |
|---|---|
| Standalone `F9.md` is not Family 9 under the dispatch map. | Not used. Packet 009 in the families 005-018 dispatch file is the controlling source; report notes the F9.md Afrobeats proxy mismatch. |
| Packet 009 names artist seeds but not album or song rows. | Artist rows for Packet 009 names are `existing_seed=true`; instantiated albums and songs are `existing_seed=false` curated missing-obvious additions. |
| Source names include diacritics and curly apostrophe forms: Motorhead (source umlaut form), Motley Crue (source umlaut form), Guns N' Roses. | Normalized display and IDs to ASCII `Motorhead`, `Motley Crue`, and `Guns N' Roses` for import stability; retain warning for display-title enrichment if desired. |
| Hard-rock and pop-metal names appear beside true-metal names. | Bon Jovi, Def Leppard, Guns N' Roses, Whitesnake, Europe, Deep Purple, Van Halen, and similar rows are boundary/false-nearby where appropriate. |
| Queens of the Stone Age is a desert/heavy-rock gateway rather than a pure metal anchor. | Kept in 064 as source seed with gateway, bridge, boundary, and false_nearby roles. |
| Nine Inch Nails and Rage Against the Machine have strong alternative/industrial/rap-rock ownership. | Included because Packet 009 names them, but normalized as gateway/bridge/boundary rather than pure metal anchors. |
| Linkin Park and Limp Bizkit can signal nu-metal openness without broader heavy affinity. | Rows retain high/mass recognition while using boundary or false_nearby roles where needed. |
| `Aenima` uses ASCII display instead of the official ligature title. | Import as `tool-aenima`; display-title enrichment can restore the official typography later. |
| Self-titled artist/album/song collisions are common in metal. | Warnings flag Black Sabbath, Metallica, Korn, System of a Down, Rage Against the Machine, Slipknot, Skid Row, Whitesnake, and other title collisions. |
