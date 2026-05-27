# Family Lock Triage

Generated: 2026-05-20

All 18 families are staging-import ready because the dry run imports every family with 0 validation errors. No family is hard-lock ready yet because alias handling, duplicate handling, composition/recording policy, and final breadth review are not all explicit.

| family | staging_import_ready | hard_lock_ready | risk | biggest blocker | next QA action | next expansion action |
|---:|---|---|---|---|---|---|
| 1 | yes | no | medium | Source-version split rules and early artist aliases. | Resolve `Hound Dog`, `The Twist`, `Shake, Rattle and Roll`, `That's All Right`, Crickets/Buddy Holly, Gene Vincent/Blue Caps. | None broad; only targeted source-version fixes. |
| 2 | yes | no | medium | British Invasion covers and cross-family ownership. | Review `Gloria`, `House of the Rising Sun`, garage/proto-punk bridges. | No broad expansion; tune boundary rows. |
| 3 | yes | no | medium | Duplicate-membership semantics and Page 2 bloat. | Confirm canonical entity plus membership import behavior for repeated album-rock/prog objects. | No broad expansion; threshold and suppress. |
| 4 | yes | no | high | Traditional/protest standards and null/unstable years. | Composition-first review for `We Shall Overcome`, `House of the Rising Sun`, `Turn! Turn! Turn!`. | No broad expansion; attribution cleanup. |
| 5 | yes | no | medium | No aligned row-level source seeds and country edge coverage. | Review country cover/source rows such as `Wagon Wheel`, `Tennessee Whiskey`, `Act Naturally`, `Me and Bobby McGee`. | Targeted pass for western swing, bluegrass, country gospel, Bakersfield, Tejano-country. |
| 6 | yes | no | medium | Motown group/solo, disco-era, and R&B version splits. | Alias policy for solo/group rows; version policy for `Respect`, `Ain't No Mountain High Enough`, `I Heard It Through the Grapevine`. | None broad; targeted quiet-storm/new-jack calibration if needed. |
| 7 | yes | no | high | Explicit/clean/remix/collaboration version policy. | Resolve alias rows and explicit/clean cases, especially `WAP`, `Walk This Way`, `Killing Me Softly`, `I Don't Like`. | No broad expansion; version and credit QA. |
| 8 | yes | no | medium | Targeted depth pass complete; alias/version consolidation and cross-family boundary QA remain. | Review `Gloria`, `Tainted Love`, `D-7`, `Lake of Fire`, `Pepper`, Yazoo/Yaz, Love and Rockets/Bauhaus, and Family 9/10/11 boundaries. | No broad expansion; only survey-driven reweights or suppressions. |
| 9 | yes | no | medium | Extreme/deep metal coverage and cover-version gateways. | Review `Sleep` vs `Sleep Token`, `Hurt`, `Cum On Feel the Noize`. | Targeted extreme-metal/deep-gateway review. |
| 10 | yes | no | medium | Boundary with Families 8, 9, 11, and 18. | Cross-family membership QA for college rock, shoegaze, emo, blog indie, garage revival. | No broad expansion; suppress collector-only tails. |
| 11 | yes | no | high | Club alias/mix/edit specificity and missing regional club scenes. | Alias and mix/edit review for Mr. Fingers, Model 500, Cybotron, Inner City. | Targeted industrial, ambient, D&B, garage, trance, regional club pass. |
| 12 | yes | no | medium | Persona-pop recency and solo/group credits. | Beyonce/Destiny-era and feature-credit handling. | No broad expansion; recency/threshold pass. |
| 13 | yes | no | high | Uneven regional coverage and language/remix variants. | Review `Despacito`, `Bailando`, `Danza Kuduro`, `Love Nwantiti`, `7 Seconds`. | Targeted South Asian, MENA, Brazilian, reggae/dancehall, non-Afrobeats Africa pass. |
| 14 | yes | no | high | Standards need composition/recording split. | Composition-first policy for `My Favorite Things`, `Nessun dorma`, `Round Midnight`, `The Girl from Ipanema`. | No broad expansion until standards policy exists. |
| 15 | yes | no | high | Show/film/cast/composer entity model. | Resolve `We Don't Talk About Bruno`, `Remember Me`, `James Bond Theme`, score vs soundtrack rows. | No broad expansion until source-entity model exists. |
| 16 | yes | no | high | Worship standard/version policy. | Resolve church brand, songwriter, live, and congregational version handling. | No broad expansion until worship-songbook model exists. |
| 17 | yes | no | high | Traditional/kids/holiday repertoire often lacks meaningful performer ownership. | Composition-first QA for holiday, kids, novelty, karaoke, wedding, and party standards. | No broad expansion; policy first. |
| 18 | yes | no | medium | Recency volatility and internet-native shelf stability. | Add freshness cadence and suppress/expire policy for current scenes. | Targeted refresh cycle, not broad expansion. |
