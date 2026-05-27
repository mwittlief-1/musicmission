# Family 6 Song Candidates

Full importable song fields are in `normalized_family_6.json`. Packet 006 did not name song objects directly, so every song row is `existing_seed=false`.

| archetype_id | archetype_name | song_rows | high-yield song candidates |
| --- | --- | ---: | --- |
| 037 | Motown / Detroit Soul Pop | 15 | `My Girl`; `Ain't No Mountain High Enough`; `I Heard It Through the Grapevine`; `Superstition`; `Signed, Sealed, Delivered (I'm Yours)`; `Where Did Our Love Go`; `You Can't Hurry Love`; `Stop! In the Name of Love`; `Reach Out I'll Be There`; `I Can't Help Myself`; `The Tears of a Clown`; `I Want You Back`; `ABC`; `Dancing in the Street`; `My Guy` |
| 038 | Southern Soul / Stax / Muscle Shoals | 15 | `Respect`; `Chain of Fools`; `Think`; `(Sittin' On) The Dock of the Bay`; `Try a Little Tenderness`; `Soul Man`; `Hold On, I'm Comin'`; `In the Midnight Hour`; `Land of 1000 Dances`; `Green Onions`; `I'll Take You There`; `Let's Stay Together`; `Tired of Being Alone`; `Theme from Shaft`; `When a Man Loves a Woman` |
| 039 | Funk / Psychedelic Soul / Groove Canon | 17 | `Papa's Got a Brand New Bag`; `I Got You (I Feel Good)`; `Cold Sweat`; `Get Up (I Feel Like Being a) Sex Machine`; `Dance to the Music`; `Everyday People`; `Family Affair`; `Maggot Brain`; `Give Up the Funk`; `Flash Light`; `September`; `Shining Star`; `Jungle Boogie`; `Brick House`; `Superfly`; `Cissy Strut`; `Super Freak` |
| 040 | Disco / Dancefloor 70s | 18 | `I Feel Love`; `Last Dance`; `Hot Stuff`; `Le Freak`; `Good Times`; `Stayin' Alive`; `Night Fever`; `I Will Survive`; `We Are Family`; `He's the Greatest Dancer`; `That's the Way (I Like It)`; `Get Down Tonight`; `Y.M.C.A.`; `Disco Inferno`; `You Make Me Feel (Mighty Real)`; `Turn the Beat Around`; `Young Hearts Run Free`; `Don't Leave Me This Way` |
| 041 | Quiet Storm / Smooth R&B / Adult Soul | 15 | `Quiet Storm`; `Let's Get It On`; `Sexual Healing`; `Close the Door`; `Turn Off the Lights`; `Never Too Much`; `Here and Now`; `Sweet Love`; `Caught Up in the Rapture`; `Smooth Operator`; `No Ordinary Love`; `Can't Get Enough of Your Love, Babe`; `Killing Me Softly with His Song`; `Lovin' You`; `Un-Break My Heart` |
| 042 | New Jack Swing / 80s-90s R&B Pop | 20 | `Nasty`; `Control`; `Rhythm Nation`; `I Wanna Dance with Somebody`; `How Will I Know`; `My Prerogative`; `Every Little Step`; `If It Isn't Love`; `Poison`; `End of the Road`; `I'll Make Love to You`; `No Scrubs`; `Creep`; `Forever My Lady`; `Freek'n You`; `Real Love`; `Weak`; `Hold On`; `One in a Million`; `No Diggity` |
| 043 | Neo-Soul / Conscious R&B | 16 | `Doo Wop (That Thing)`; `Ex-Factor`; `Brown Sugar`; `Untitled (How Does It Feel)`; `On & On`; `Tyrone`; `Fortunate`; `Ascension (Don't Ever Wonder)`; `A Long Walk`; `Golden`; `Fallin'`; `If I Ain't Got You`; `Video`; `Love`; `You Got Me`; `Charlene` |
| 044 | Modern R&B / Alt-R&B / Bedroom R&B | 23 | `Novacane`; `Thinkin Bout You`; `Pyramids`; `Pink + White`; `Wicked Games`; `House of Balloons / Glass Table Girls`; `The Hills`; `Earned It`; `Love Galore`; `The Weekend`; `Good Days`; `Kill Bill`; `Adorn`; `Coffee`; `Cranes in the Sky`; `Losing You`; `Focus`; `Girls Need Love`; `Playing Games`; `Clouded`; `Two Weeks`; `LMK`; `Exchange` |

## Version-Specific Rows

| row | handling |
| --- | --- |
| `Ain't No Mountain High Enough` | Marvin Gaye & Tammi Terrell recording is distinct from Diana Ross solo version. |
| `Respect` | Aretha Franklin recording is distinct from Otis Redding original. |
| `I Heard It Through the Grapevine` | Marvin Gaye recording is distinct from Gladys Knight & the Pips version. |
| `Tyrone` | Live-version row uses `live_gateway` role and `erykah-badu-tyrone-live` ID. |
| `Don't Leave Me This Way` | Thelma Houston recording is distinct from Harold Melvin & the Blue Notes version. |
| `You Got Me`, `Love Galore`, `No Diggity` | Featured-artist credits should be preserved during import. |
