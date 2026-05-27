# Family 1 Corrections to Source Report

| issue_type | existing_report_area | correction |
|---|---|---|
| source package mismatch | iCloud Drive | No Family 1 zip was found at the iCloud root; used `waymark_family_1_latest_corpus_for_codex_2026-05-19.md` because it identifies itself as the latest consolidation corpus. |
| schema drift | Song roles | Replaced non-schema roles such as `bridge_song`, `slowdance_anchor`, `summer_anchor`, `party_anchor`, `instrumental`, `novelty_anchor`, and `atmosphere` with normalized enum values. |
| recognition drift | all archetypes | Expanded `MK/BA/LA/SK/CK` and `mass_known/broad_anchor/lane_anchor/scene_known/cult_known` into `mass/high/medium/low/cult`. |
| artist ID drift | Part B 004/005/006 rows | Generated missing artist IDs from artist names where the table omitted the Artist ID column. |
| song row malformed | Fats Domino - Blueberry Hill | Generated `fats-domino-blueberry-hill` and filled 1956 for the missing year/id row. |
| artist merge risk | Rick Nelson / Ricky Nelson | Use `ricky-nelson`; keep `rick-nelson` only as an alias if encountered. |
| artist split risk | Johnny Burnette solo vs Rock and Roll Trio | Keep trio rows in 002 distinct from solo Burnette rows in 004. |
| artist split risk | The Tornados vs The Tornadoes | Keep `the-tornados` for `Telstar` and `the-tornadoes` for `Bustin' Surfboards`. |
| artist disambiguation | The Wailers | Disambiguate Pacific Northwest Wailers from Bob Marley and the Wailers before hard lock. |
| artist alias risk | Link Wray / Wraymen / Ray Men | Normalize backing-band credits without creating duplicate Link Wray canonical artist entities. |
| artist alias risk | The Crickets / Buddy Holly and the Crickets | Decide whether Crickets rows are aliases, memberships, or distinct band records before hard lock. |
| artist credit risk | Jackie Brenston / Ike Turner | Keep `Rocket 88` as Jackie Brenston and His Delta Cats while retaining Ike Turner/Kings of Rhythm credit aliases. |
| song duplicate risk | Hound Dog | Preserve Big Mama Thornton and Elvis Presley as separate recordings. |
| song duplicate risk | The Twist | Preserve Hank Ballard original and Chubby Checker version as separate recordings. |
| song duplicate risk | Shake, Rattle and Roll | Preserve Big Joe Turner and Bill Haley versions as separate recordings. |
| song duplicate risk | Sh-Boom / Love Potion No. 9 / Louie Louie | Define source/cover split rules before any title-based merge or composition matching. |
| canonical object correction | 005 | Added label/anthology gateways for Spector, Red Bird, and broader girl-group discovery. |
| parse normalization | source table | Generated missing song ID `fats-domino-blueberry-hill` and release_year `1956` for Part B row `Blueberry Hill` by `Fats Domino` in archetype 001. |
| parse normalization | source table | Generated missing artist ID `bobby-vee` for Part B row `Bobby Vee` in archetype 004. |
| parse normalization | source table | Generated missing artist ID `frankie-avalon` for Part B row `Frankie Avalon` in archetype 004. |
| parse normalization | source table | Generated missing artist ID `bobby-rydell` for Part B row `Bobby Rydell` in archetype 004. |
| parse normalization | source table | Generated missing artist ID `fabian` for Part B row `Fabian` in archetype 004. |
| parse normalization | source table | Generated missing artist ID `connie-francis` for Part B row `Connie Francis` in archetype 004. |
| parse normalization | source table | Generated missing artist ID `brenda-lee` for Part B row `Brenda Lee` in archetype 004. |
| parse normalization | source table | Generated missing artist ID `bobby-darin` for Part B row `Bobby Darin` in archetype 004. |
| parse normalization | source table | Generated missing artist ID `gene-pitney` for Part B row `Gene Pitney` in archetype 004. |
| parse normalization | source table | Generated missing artist ID `johnny-tillotson` for Part B row `Johnny Tillotson` in archetype 004. |
| parse normalization | source table | Generated missing artist ID `brian-hyland` for Part B row `Brian Hyland` in archetype 004. |
| parse normalization | source table | Generated missing artist ID `jimmy-clanton` for Part B row `Jimmy Clanton` in archetype 004. |
| parse normalization | source table | Generated missing artist ID `tommy-roe` for Part B row `Tommy Roe` in archetype 004. |
| parse normalization | source table | Generated missing artist ID `shelley-fabares` for Part B row `Shelley Fabares` in archetype 004. |
| parse normalization | source table | Generated missing artist ID `lesley-gore` for Part B row `Lesley Gore` in archetype 004. |
| parse normalization | source table | Generated missing artist ID `annette-funicello` for Part B row `Annette Funicello` in archetype 004. |
| parse normalization | source table | Generated missing artist ID `chris-montez` for Part B row `Chris Montez` in archetype 004. |
| parse normalization | source table | Generated missing artist ID `jimmy-jones` for Part B row `Jimmy Jones` in archetype 004. |
| parse normalization | source table | Generated missing artist ID `mark-dinning` for Part B row `Mark Dinning` in archetype 004. |
| parse normalization | source table | Generated missing artist ID `ray-peterson` for Part B row `Ray Peterson` in archetype 004. |
| parse normalization | source table | Generated missing artist ID `the-cascades` for Part B row `The Cascades` in archetype 004. |
| parse normalization | source table | Generated missing artist ID `the-teddy-bears` for Part B row `The Teddy Bears` in archetype 004. |
| parse normalization | source table | Generated missing artist ID `the-fleetwoods` for Part B row `The Fleetwoods` in archetype 004. |
| parse normalization | source table | Generated missing artist ID `the-orlons` for Part B row `The Orlons` in archetype 005. |
| parse normalization | source table | Generated missing artist ID `major-lance` for Part B row `Major Lance` in archetype 006. |
| parse normalization | source table | Generated missing artist ID `gene-chandler` for Part B row `Gene Chandler` in archetype 006. |
| parse normalization | source table | Generated missing artist ID `dee-clark` for Part B row `Dee Clark` in archetype 006. |
| parse normalization | source table | Generated missing artist ID `betty-everett` for Part B row `Betty Everett` in archetype 006. |
| parse normalization | source table | Generated missing artist ID `jerry-butler` for Part B row `Jerry Butler` in archetype 006. |
| parse normalization | source table | Generated missing artist ID `the-righteous-brothers` for Part B row `The Righteous Brothers` in archetype 006. |
| parse normalization | source table | Generated missing artist ID `etta-james` for Part B row `Etta James` in archetype 006. |
| parse normalization | source table | Generated missing artist ID `little-willie-john` for Part B row `Little Willie John` in archetype 006. |
| parse normalization | source table | Generated missing artist ID `barrett-strong` for Part B row `Barrett Strong` in archetype 006. |
| parse normalization | source table | Generated missing artist ID `chubby-checker` for Part B row `Chubby Checker` in archetype 006. |
