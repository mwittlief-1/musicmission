# Import Warnings

## Non-Enum Terms

- None detected in generated rows; role, recognition, survey, album type, and artist survey status fields use current importer enums.

## Source Alignment

- Packet 016 is controlling. F16.md is misaligned; it describes dream-pop/shoegaze rather than Christian, worship, or gospel material, so it was not used as seed evidence.
- Treat every `existing_seed=false` row as gap-fill candidate data until an aligned row source or QA review promotes it.

## Merge / Alias / Version Risks

- Sister Rosetta Tharpe: Gospel, early rock and roll, and blues memberships should remain linked but distinct.
- Mary Mary: Gospel, R&B, and pop-crossover rows overlap.
- Skillet: Christian-market and mainstream hard-rock identities should not be merged into worship appetite.
- Keith and Kristyn Getty: Modern hymn/songbook object should be treated standard-first.
- Maverick City Music: Collective, church-brand, and featured-vocal rows require credit review.
- Passion: Conference/live worship brand needs distinct entity handling.
- Old Church Basement - Elevation Worship and Maverick City Music: Collaboration album should not merge church-band brands.
- Awake - Skillet: Hard-rock crossover row, not worship appetite by default.
- In Christ Alone - Keith and Kristyn Getty: Modern hymn/songbook row; many church versions exist.
- Maverick City Vol. 3 Part 1 - Maverick City Music: Collective and featured-vocal credits need review.
- People - Hillsong United: Hillsong Worship, Hillsong United, and church-brand rows should remain distinct.
- Amazing Grace - Aretha Franklin: Composition vs Aretha live recording must remain distinct.
- Soon and Very Soon - Andrae Crouch: Gospel standard has many church and choir versions.
- Shackles (Praise You) - Mary Mary: Gospel/R&B/pop-crossover rows overlap.
- Break Every Chain - Tasha Cobbs Leonard: Worship standard and live gospel recording should remain distinct.
- God's Not Dead (Like a Lion) - Newsboys: Newsboys cover/version should not merge with original Daniel Bashta worship song.
- Monster - Skillet: Mainstream hard-rock recognition can be a false nearby for worship/CCM appetite.
- Shout to the Lord - Darlene Zschech: Church-songbook standard with many Hillsong and congregation versions.
- Oceans (Where Feet May Fail) - Hillsong United: Hillsong United and Hillsong Worship brand split needed.
- In Christ Alone - Keith and Kristyn Getty: Modern hymn should be standard-first and version-aware.
- Goodness of God - Bethel Music and Jenn Johnson: Bethel brand and Jenn Johnson performance credit require review.
- Jireh - Elevation Worship and Maverick City Music featuring Chandler Moore and Naomi Raine: Collaboration and featured-vocal credits need manual handling.
- The Blessing - Kari Jobe, Cody Carnes and Elevation Worship: Artist, songwriter, and church-brand credits overlap.
- Build My Life - Pat Barrett: Modern worship standard with many artist and church versions.
- Great Are You Lord - All Sons & Daughters: Worship standard should not be forced into one artist-only object.

## Import Readiness Notes

- Largest remaining gap: The largest remaining gap is worship standard/version policy: live, church-brand, songwriter, and congregational versions need explicit import split rules.
- Duplicate object IDs across families should be interpreted as multi-membership unless a warning says the display names or source versions conflict.
