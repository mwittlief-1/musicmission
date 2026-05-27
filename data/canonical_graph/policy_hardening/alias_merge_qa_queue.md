# Alias and Merge QA Queue

Generated: 2026-05-20

This queue is a policy QA layer over the current dry-run warnings and merge review queue. It is not an automatic merge list.

## Safe Display-Name Normalization

These look like display/case/punctuation normalization issues. They can be normalized after confirming source rows refer to the same public entity or same recording.

| issue | examples | action |
|---|---|---|
| Ampersand vs `and` | `Martha & the Vandellas` / `Martha and the Vandellas`; `Simon & Garfunkel` / `Simon and Garfunkel` | Normalize display aliases to one canonical entity. |
| Case-only display drift | `Kool & The Gang` / `Kool & the Gang`; `Here Are The Sonics` / `Here Are the Sonics` | Normalize display text; keep source names as aliases. |
| Punctuation display drift | `The B-52's` / `The B-52s` | Human confirm, then normalize display alias and same recording rows. |
| Article and band-name drift | `Staple Singers` / `The Staple Singers` | Human confirm, then normalize if rows refer to the same artist identity. |

## Likely Same Artist / Entity

These are likely one public entity but need explicit alias records before import lock.

| issue | examples | action |
|---|---|---|
| Punctuation/name form alias | `Smokey Robinson & The Miracles` / `Smokey Robinson and the Miracles` | Create alias row. |
| Rap aliases | `2Pac` / Tupac; `Mos Def` / `Yasiin Bey`; `Jeezy` / Young Jeezy | Add alias table; do not infer from slug only. |
| Electronic project aliases | Larry Heard / `Mr. Fingers` / Fingers Inc.; Juan Atkins / `Model 500` / Cybotron | Human review because project alias can indicate different discographic identity. |
| Church-brand related entities | Hillsong Worship / Hillsong United / Hillsong church brands | Related but not automatically same; requires brand table. |

## Must Remain Separate

These should not merge even when names, members, or songs are related.

| issue | examples | action |
|---|---|---|
| Group vs solo | Diana Ross vs The Supremes; Michael Jackson vs Jackson 5; Beyonce vs Destiny's Child; Darius Rucker vs Hootie & the Blowfish | Keep separate canonical artists; optionally link through relationship table. |
| Different artists with similar names | Sleep vs Sleep Token; U.S. Wailers vs Bob Marley & The Wailers; Jimmie Rodgers pop singer vs country Jimmie Rodgers | Keep separate canonical IDs. |
| Different songs with same title | Fela Kuti `Zombie` vs The Cranberries `Zombie`; Korn `Blind` vs Hercules & Love Affair `Blind`; Mastodon `Oblivion` vs Grimes `Oblivion` | Keep separate composition IDs and recording IDs. |
| Cover/remake with distinct cultural function | Aerosmith `Walk This Way` vs Run-DMC/Aerosmith `Walk This Way`; Whitney Houston `I Will Always Love You` vs Dolly Parton original | Link only through composition after review; keep recordings separate. |

## Needs Human Review

| issue | examples | action |
|---|---|---|
| Group/alias ambiguity | The Crickets / Buddy Holly and the Crickets; Gene Vincent / Blue Caps | Decide canonical artist and alias/credit model. |
| Collaboration credits | `Luis Fonsi and Daddy Yankee`; `Waylon Jennings and Willie Nelson`; `Elevation Worship and Maverick City Music featuring Chandler Moore and Naomi Raine` | Preserve credited artist text; link individual canonical artists later. |
| Regional/language/remix variants | `Despacito`, `Bailando`, `Danza Kuduro`, `Love Nwantiti`, `AMG`, `Bebe Dame` | Require recording-level variant review. |
| Release-year conflict | Shania Twain `Man! I Feel Like a Woman!` 1997/1999 | Decide album-release vs single-release policy. |

## Composition-vs-Recording Review

| title | current issue | policy |
|---|---|---|
| `Hound Dog` | Big Mama Thornton and Elvis Presley recordings. | Preserve both recordings; link composition only after review. |
| `The Twist` | Hank Ballard and Chubby Checker recordings. | Preserve both recordings. |
| `Shake, Rattle and Roll` | Big Joe Turner and Bill Haley recordings. | Preserve both recordings. |
| `That's All Right` | Arthur Crudup and Elvis Presley recordings. | Preserve both recordings. |
| `Walk This Way` | Aerosmith original and Run-DMC/Aerosmith remake. | Preserve both recordings. |
| `Gloria` | Multiple different artists and possibly multiple compositions. | Manual composition review. |
| `House of the Rising Sun` | Traditional/revival object and The Animals recording. | Composition-first traditional-song model needed. |
| `God Only Knows` | The Beach Boys and for KING & COUNTRY same-title queue. | Review likely different compositions; do not merge by title. |
| `I'll Take You There` | Staple Singers display drift. | Likely display normalization plus recording identity check. |
| `Love Shack` | B-52's display drift. | Likely display normalization plus recording identity check. |
| `Zombie` | Fela Kuti and Cranberries same title. | Separate compositions and recordings. |

## Cast / Show / Soundtrack Review

| issue | examples | action |
|---|---|---|
| Cast credit variants | `We Don't Talk About Bruno`, `Defying Gravity`, `My Shot` | Model show/film, cast recording, performers, and recording separately. |
| Score vs soundtrack | `Black Panther`, `Guardians of the Galaxy`, `Star Wars`, `The Dark Knight` | Separate score album, curated soundtrack album, and pop-song recordings. |
| Fictional performer | `Man of Constant Sorrow - The Soggy Bottom Boys` | Preserve film-fictional credit; link traditional composition separately. |
| Theme authorship/performance | `James Bond Theme` | Manual composer/performance credit review. |

## Worship / Traditional Review

| issue | examples | action |
|---|---|---|
| Traditional/protest standards | `We Shall Overcome`, `House of the Rising Sun`, `This Land Is Your Land` | Composition-first model; performer rows only where survey-useful. |
| Worship standards | `Amazing Grace`, `Shout to the Lord`, `In Christ Alone`, `Build My Life`, `Way Maker` | Songbook composition plus recording variants. |
| Church brands | Hillsong, Bethel, Elevation, Maverick City, Passion | Keep brands and individual performers distinct. |
| Null/unstable years | Family 4 traditional/revival rows | Permit null only with explicit traditional/composition status. |
