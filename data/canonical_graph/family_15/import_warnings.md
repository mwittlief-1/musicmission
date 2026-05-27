# Import Warnings

## Non-Enum Terms

- None detected in generated rows; role, recognition, survey, album type, and artist survey status fields use current importer enums.

## Source Alignment

- Packet 015 is controlling. No aligned F15 supplemental report was present at baseline generation.
- Treat every `existing_seed=false` row as gap-fill candidate data until an aligned row source or QA review promotes it.

## Merge / Alias / Version Risks

- Claude-Michel Schonberg: Composer/show-first object; do not merge with cast recordings.
- Leonard Bernstein: Composer/conductor, Broadway, film, and classical rows overlap.
- Rodgers and Hammerstein: Songbook/show-first partnership should not split casually into individual artists.
- Benj Pasek and Justin Paul: Modern theater and screen-musical credits require show-first review.
- Howard Ashman: Lyricist/creative-partner rows bridge Disney and theater.
- Robert Lopez: Disney, Broadway, and comedy-adjacent credits need disambiguation.
- Kristen Anderson-Lopez: May merge in existing row as Anderson-Lopez and Robert Lopez partnership.
- Germaine Franco: Score and song soundtrack rows need separate handling.
- Bill Medley and Jennifer Warnes: Duet recording should remain separate from solo-artist catalog rows.
- Simon and Garfunkel: Soundtrack membership should not override folk-rock primary family.
- Adele: Bond soundtrack membership only; artist belongs primarily outside Family 15.
- Eminem: Soundtrack membership only; hip-hop primary family elsewhere.
- John Barry: Bond themes have composer/arranger/performance attribution complexity.
- Ludwig Goransson: Score and hip-hop/R&B soundtrack album rows should remain distinct.
- Trent Reznor and Atticus Ross: Industrial/rock artist identity and score-composer identity overlap.
- Les Miserables - Original London Cast of Les Miserables: Cast recording, stage show, and film soundtrack need separate IDs.
- West Side Story - Original Broadway Cast of West Side Story: Stage cast and film soundtrack rows should not merge.
- The Sound of Music - Original Broadway Cast of The Sound of Music: Stage, film, and family-context memberships overlap.
- O Brother, Where Art Thou? - Various Artists: Americana/roots soundtrack row overlaps country/folk families.
- Guardians of the Galaxy: Awesome Mix Vol. 1 - Various Artists: Compilation soundtrack made of older songs; do not merge with original release albums.
- Garden State - Various Artists: Indie soundtrack-compilation object, not a single artist discography.
- The Social Network - Trent Reznor and Atticus Ross: Score composer identity overlaps Nine Inch Nails/industrial-rock context.
- Black Panther - Ludwig Goransson: Score album distinct from Kendrick Lamar-curated soundtrack album.
- Being Alive - Dean Jones: Sondheim standard has many canonical recordings.
- I Will Always Love You - Whitney Houston: Preserve Whitney Houston recording distinct from Dolly Parton original.
- Main Title - John Williams: Title is generic; keep Star Wars soundtrack context.
- I Dreamed a Dream - Patti LuPone: Les Miserables standard has many cast and pop recordings.
- America - Original Broadway Cast of West Side Story: Stage, film, and Bernstein composition contexts overlap.
- Do-Re-Mi - Julie Andrews and The Sound of Music Cast: Family-context and musical-theater memberships both apply.
- We Don't Talk About Bruno - Carolina Gaitan, Mauro Castillo, Adassa, Rhenzy Feliz, Diane Guerrero, Stephanie Beatriz and Encanto Cast: Ensemble cast credit is version-specific and should not merge to one artist.
- Remember Me - Benjamin Bratt: Coco has multiple in-film versions; preserve recording context.
- Eye of the Tiger - Survivor: Rocky soundtrack membership overlaps mainstream rock and workout context.
- Lose Yourself - Eminem: Soundtrack membership only; primary hip-hop family elsewhere.
- Skyfall - Adele: Bond song row should not override Adele primary artist identity.
- Man of Constant Sorrow - The Soggy Bottom Boys: Film-fictional group and traditional/roots song attribution need review.
- Hooked on a Feeling - Blue Swede: Guardians soundtrack context is later than original release; preserve original recording year.
- James Bond Theme - John Barry Orchestra: Bond theme authorship and performance credits require manual review.

## Import Readiness Notes

- Largest remaining gap: The largest remaining gap is source-entity modeling: show, cast recording, film, soundtrack album, composer, and pop recording IDs need a policy pass before hard lock.
- Duplicate object IDs across families should be interpreted as multi-membership unless a warning says the display names or source versions conflict.
