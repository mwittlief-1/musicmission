# Import Warnings

## Non-Enum Terms

- None detected in generated rows; role, recognition, survey, album type, and artist survey status fields use current importer enums.

## Source Alignment

- Packet 014 is controlling. F14.md is a null/status report with no aligned family mapping or row seeds.
- Treat every `existing_seed=false` row as gap-fill candidate data until an aligned row source or QA review promotes it.

## Merge / Alias / Version Risks

- Louis Armstrong: Jazz, standards, New Orleans, and pop-memory memberships should remain distinct.
- Dean Martin: Italian-American crooner persona and novelty/context rows overlap Family 17.
- Bing Crosby: Holiday rows overlap Family 17; do not treat all Crosby recognition as jazz appetite.
- Michael Buble: Modern crooner revival overlaps holiday/adult-pop context.
- Chet Baker: Standard composition and Baker vocal/trumpet recording need split handling.
- Stan Getz: Bossa nova and jazz gateway memberships should both be retained.
- Nina Simone: Jazz, soul, protest-song, and standards rows need cross-family membership review.
- Herb Alpert: Tijuana Brass, adult instrumental, and pop instrumental rows may split.
- Lang Lang: Classical-performance rows should not become a specialist classical canon dump.
- Max Richter: Film-score, modern classical, and ambient overlaps need context-aware memberships.
- Jackie Evancho: Talent-show/classical-crossover recognition should stay boundary until user confirms appetite.
- Dino: The Essential Dean Martin - Dean Martin: Compilation gateway; crooner standards and novelty/context rows overlap.
- Bing: His Legendary Years, 1931-1957 - Bing Crosby: Holiday-standard recognition should not merge with all standards rows.
- Call Me Irresponsible - Michael Buble: Adult-pop/crooner revival and holiday rows require cross-family review.
- Getz/Gilberto - Stan Getz and Joao Gilberto: Preserve bossa nova collaboration credits.
- Pastel Blues - Nina Simone: Jazz, soul, blues, and protest-song rows overlap.
- Classics in the Key of G - Kenny G: Classical-themed smooth-jazz object, not a classical-performance album.
- The Blue Notebooks - Max Richter: Modern classical/ambient/film-score overlap.
- Watermark - Enya: New age/pop recognition should remain bridge, not classical-crossover proof by itself.
- Fly Me to the Moon - Frank Sinatra: Standard composition has many recordings; preserve Sinatra recording.
- Someone to Watch Over Me - Ella Fitzgerald: Standard composition; recording-specific row.
- My Favorite Things - John Coltrane: Preserve Coltrane recording distinct from musical-theater composition.
- Round Midnight - Thelonious Monk: Standard with many recordings; do not title-merge.
- Nessun dorma - Luciano Pavarotti: Opera aria/composition must remain distinct from Pavarotti recording.
- Cello Suite No. 1: Prelude - Yo-Yo Ma: Composition vs recording distinction required.
- What a Wonderful World - Louis Armstrong: Pop standard and Louis Armstrong jazz identity both matter.
- That's Amore - Dean Martin: Crooner/context novelty overlap with Family 17.
- White Christmas - Bing Crosby: Holiday object overlaps Family 17; preserve Crosby recording.
- Feeling Good - Nina Simone: Also appears as modern crooner/adult-pop cover material.
- My Funny Valentine - Chet Baker: Standard composition has many recordings; preserve Baker row.
- The Girl from Ipanema - Stan Getz and Astrud Gilberto: Bossa nova, jazz, and lounge rows should remain distinct.
- Blue in Green - Miles Davis: Composition credit and recording-credit review needed.
- Lily Was Here - David A. Stewart featuring Candy Dulfer: Collaboration credit and soundtrack/adult-instrumental context need review.
- Soulful Strut - Young-Holt Unlimited: Instrumental soul-jazz/adult instrumental title may bridge Family 6.
- On the Nature of Daylight - Max Richter: Film-score and modern-classical contexts require split membership.
- La Campanella - Lang Lang: Composition and performer recording must not merge.
- Adagio for Strings - London Philharmonic Orchestra: Classical composition and film/trance uses need separate handling.

## Import Readiness Notes

- Largest remaining gap: The largest remaining gap is recording-level standard attribution: many songs need composition, definitive recording, and holiday/context split rules before hard lock.
- Duplicate object IDs across families should be interpreted as multi-membership unless a warning says the display names or source versions conflict.
