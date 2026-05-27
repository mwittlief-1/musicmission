# Family 6 Gap Summary

Controlling source: Packet 006 from `/Users/matt_wittlief_home/Library/Mobile Documents/com~apple~CloudDocs/waymark_pass_one_dispatches_families_005_018.md`.

`F6.md` was not used as authority because it says Family 6 was unspecified. `F10.md` and `F7.md` were used only as salvage context for the disco and modern/alt-R&B edges noted below.

Source seed rows normalized: 63 artist rows.

Added missing-obvious/boundary rows: 44 artist rows, 71 album rows, 139 song rows.

| archetype_id | archetype_name | artists | albums | songs | source_seed_artists | added_artists | added_albums | added_songs | gap_note |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 037 | Motown / Detroit Soul Pop | 11 | 7 | 15 | 9 | 2 | 7 | 15 | Strong Motown spine from Packet 006; added Marvelettes and Mary Wells as obvious early-Motown survey gaps. |
| 038 | Southern Soul / Stax / Muscle Shoals | 12 | 8 | 15 | 8 | 4 | 8 | 15 | Strong Stax/Atlantic/Hi coverage; added Percy Sledge, Etta James, Solomon Burke, and Ann Peebles for ballad, blues-soul, and Memphis depth. |
| 039 | Funk / Psychedelic Soul / Groove Canon | 13 | 8 | 17 | 7 | 6 | 8 | 17 | Strong James Brown, Sly, P-Funk, EWF center; added Meters, Ohio Players, War, Rick James, Isley Brothers, and Prince boundary control. |
| 040 | Disco / Dancefloor 70s | 13 | 9 | 18 | 5 | 8 | 9 | 18 | Broad disco/dancefloor coverage; F10 salvage supports Sylvester/Sister Sledge and later disco-continuum warnings, while Packet 006 remains authoritative. |
| 041 | Quiet Storm / Smooth R&B / Adult Soul | 13 | 8 | 15 | 7 | 6 | 8 | 15 | Quiet storm treated as a real lane, not a soft appendix; added Barry White, Roberta Flack, Minnie Riperton, Stylistics, Peabo Bryson, Toni Braxton. |
| 042 | New Jack Swing / 80s-90s R&B Pop | 15 | 10 | 20 | 10 | 5 | 10 | 20 | Broad normal-user R&B-pop coverage; added Keith Sweat, SWV, En Vogue, Bell Biv DeVoe, and Aaliyah. |
| 043 | Neo-Soul / Conscious R&B | 13 | 9 | 16 | 7 | 6 | 9 | 16 | Album-world neo-soul core is strong; added India.Arie, Musiq Soulchild, Raphael Saadiq, Bilal, Angie Stone, and Anthony Hamilton. |
| 044 | Modern R&B / Alt-R&B / Bedroom R&B | 17 | 12 | 23 | 10 | 7 | 12 | 23 | Strong Packet 006 modern R&B seed spine; F7 salvage supports FKA twigs, Kelela, Tinashe, PARTYNEXTDOOR, Bryson Tiller, 6LACK, Daniel Caesar as non-seed additions. |

## Production Notes

- The normalized JSON is the import source of truth.
- Artist seed flags are intentionally narrow: only artist objects explicitly named in Packet 006 are `existing_seed=true`.
- All album and song rows are `existing_seed=false` because Packet 006 did not name album/song objects directly.
- Version-specific and credit-specific rows were preserved where survey behavior differs: Diana Ross solo versus Supremes, Bee Gees disco-era, live `Tyrone`, soundtrack and compilation rows, featured-artist rows, and Weeknd mixtape-era objects.
- R. Kelly was not added despite high 1990s R&B recognition; see `import_warnings.md` for policy review note.
