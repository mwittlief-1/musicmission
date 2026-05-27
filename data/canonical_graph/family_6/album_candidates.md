# Family 6 Album Candidates

Full importable album fields are in `normalized_family_6.json`. Packet 006 did not name album objects directly, so every album row is `existing_seed=false`.

| archetype_id | archetype_name | album_rows | album / artist candidates |
| --- | --- | ---: | --- |
| 037 | Motown / Detroit Soul Pop | 7 | `What's Going On` - Marvin Gaye; `Songs in the Key of Life` - Stevie Wonder; `Innervisions` - Stevie Wonder; `The Temptations Sing Smokey` - The Temptations; `Where Did Our Love Go` - The Supremes; `Going to a Go-Go` - Smokey Robinson & The Miracles; `Diana Ross Presents The Jackson 5` - Jackson 5 |
| 038 | Southern Soul / Stax / Muscle Shoals | 8 | `I Never Loved a Man the Way I Love You` - Aretha Franklin; `Lady Soul` - Aretha Franklin; `Otis Blue` - Otis Redding; `The Dictionary of Soul` - Otis Redding; `Hold On, I'm Comin'` - Sam & Dave; `The Exciting Wilson Pickett` - Wilson Pickett; `Hot Buttered Soul` - Isaac Hayes; `Call Me` - Al Green |
| 039 | Funk / Psychedelic Soul / Groove Canon | 8 | `Live at the Apollo` - James Brown; `Sex Machine` - James Brown; `Stand!` - Sly & the Family Stone; `There's a Riot Goin' On` - Sly & the Family Stone; `Maggot Brain` - Funkadelic; `Mothership Connection` - Parliament; `Super Fly` - Curtis Mayfield; `That's the Way of the World` - Earth, Wind & Fire |
| 040 | Disco / Dancefloor 70s | 9 | `Bad Girls` - Donna Summer; `I Remember Yesterday` - Donna Summer; `Saturday Night Fever` - Various Artists; `C'est Chic` - Chic; `Risque` - Chic; `We Are Family` - Sister Sledge; `Love Tracks` - Gloria Gaynor; `Diana` - Diana Ross; `Step II` - Sylvester |
| 041 | Quiet Storm / Smooth R&B / Adult Soul | 8 | `Let's Get It On` - Marvin Gaye; `A Quiet Storm` - Smokey Robinson; `Teddy` - Teddy Pendergrass; `Never Too Much` - Luther Vandross; `Rapture` - Anita Baker; `Diamond Life` - Sade; `Can't Get Enough` - Barry White; `Toni Braxton` - Toni Braxton |
| 042 | New Jack Swing / 80s-90s R&B Pop | 10 | `Control` - Janet Jackson; `Rhythm Nation 1814` - Janet Jackson; `Whitney Houston` - Whitney Houston; `Don't Be Cruel` - Bobby Brown; `Heart Break` - New Edition; `Cooleyhighharmony` - Boyz II Men; `CrazySexyCool` - TLC; `Diary of a Mad Band` - Jodeci; `My Way` - Usher; `One in a Million` - Aaliyah |
| 043 | Neo-Soul / Conscious R&B | 9 | `The Miseducation of Lauryn Hill` - Lauryn Hill; `Brown Sugar` - D'Angelo; `Voodoo` - D'Angelo; `Baduizm` - Erykah Badu; `Mama's Gun` - Erykah Badu; `Maxwell's Urban Hang Suite` - Maxwell; `Who Is Jill Scott? Words and Sounds Vol. 1` - Jill Scott; `Songs in A Minor` - Alicia Keys; `Acoustic Soul` - India.Arie |
| 044 | Modern R&B / Alt-R&B / Bedroom R&B | 12 | `Channel Orange` - Frank Ocean; `Blonde` - Frank Ocean; `Ctrl` - SZA; `SOS` - SZA; `House of Balloons` - The Weeknd; `Trilogy` - The Weeknd; `Kaleidoscope Dream` - Miguel; `A Seat at the Table` - Solange; `H.E.R.` - H.E.R.; `Over It` - Summer Walker; `Fuck the World` - Brent Faiyaz; `Take Me Apart` - Kelela |

## Object-Type Notes

| object_type | rows | import note |
| --- | ---: | --- |
| studio_album | 62 | Default album-world objects. |
| live_album | 2 | `Live at the Apollo`; `Sex Machine`. |
| compilation | 2 | `Trilogy`; `H.E.R.`. |
| soundtrack | 3 | `Super Fly`; `That's the Way of the World`; `Saturday Night Fever`; soundtrack-linked song rows also exist. |
| ep | 2 | `House of Balloons` is normalized to `ep` because the approved album enum has no mixtape type; `Fuck the World` is also represented as an EP. |
