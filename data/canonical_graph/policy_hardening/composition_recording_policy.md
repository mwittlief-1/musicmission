# Composition vs Recording Policy

Generated: 2026-05-20

## Principle

The current graph imports song rows as recording objects. Same title is never enough to merge. A composition layer is needed for standards, covers, traditional songs, worship songs, show tunes, and songs with culturally distinct hit recordings.

Staging import can proceed with recording IDs plus a review queue. Final lock requires explicit composition/recording rules for every high-risk case.

## Required Future Model

| layer | purpose |
|---|---|
| `composition_id` | Stable song/work identity when multiple recordings share authorship or tradition. |
| `canonical_song_recording_id` | Specific recording/version used in survey or atlas. |
| `recording_variant_type` | source, hit_cover, live, radio_edit, remix, clean, explicit, cast, soundtrack_pop, traditional_arrangement. |
| `credited_artist_name` | Exact artist/performer/cast credit. |
| `canonical_artist_credits` | Linked artist entities and credit roles. |
| `composition_policy_status` | no_review_needed, review_needed, composition_first_required, split_confirmed. |

## Same-Title Songs

Same-title rows enter `composition-vs-recording review`, not automatic merge.

Examples from current queue:

- `Gloria`: Patti Smith, The Cadillacs, The Shadows of Knight, Them.
- `Zombie`: Fela Kuti and The Cranberries.
- `God Only Knows`: The Beach Boys and for KING & COUNTRY.
- `Love Shack`: The B-52's / The B-52s display normalization issue.

Policy:

- If same title but different composition, keep separate composition IDs.
- If same composition but different recording, link recordings under one composition ID.
- If same recording with display-name drift, normalize display alias and keep one recording.

## Covers and Source Versions

Covers remain separate recording objects. Source versions should be preserved even when the later cover is more famous.

Current required splits:

- `Hound Dog`: Big Mama Thornton source recording vs Elvis Presley hit recording.
- `The Twist`: Hank Ballard & The Midnighters vs Chubby Checker.
- `Shake, Rattle and Roll`: Big Joe Turner vs Bill Haley & His Comets.
- `That's All Right`: Arthur "Big Boy" Crudup vs Elvis Presley.
- `Walk This Way`: Aerosmith original vs Run-DMC/Aerosmith version.

Policy:

- Store separate canonical song recording IDs.
- Add a shared `composition_id` only after authorship/source review.
- Preserve source-version rows even if survey prominence belongs to the hit version.

## Live Versions

Live versions remain distinct when user recognition, canonical status, or survey usefulness depends on the live recording.

Policy:

- Live album gateways are valid canonical objects.
- Live song recordings should have `recording_variant_type=live`.
- Do not merge live and studio rows unless the graph explicitly decides the distinction is irrelevant for survey flow.

Examples:

- `At Folsom Prison`
- `Live at the Apollo`
- `Frampton Comes Alive!`
- `Tyrone` live warning in Family 6.

## Radio Edits, Remixes, Clean and Explicit Versions

Staging schema currently stores warnings, not version rows. Production import needs variant handling.

Policy:

- Radio edits and album versions may share composition but can be distinct recordings.
- Remixes remain distinct if arrangement, credited artists, or user recognition differs.
- Clean and explicit versions remain distinct survey objects only when the difference matters for availability, recognition, or content policy.

Examples:

- `WAP` explicit/clean versions.
- Chief Keef `I Don't Like` original vs Kanye remix.
- Global-pop remix/language variants such as `Despacito`, `Bailando`, `Danza Kuduro`, and `Love Nwantiti`.
- Club tracks where title can mean original mix, radio edit, remix, DJ-set version, or viral clip.

## Standards and Traditional Songs

Standards and traditional songs require composition-first modeling when no single artist owns the user's taste signal.

Examples:

- `House of the Rising Sun`: traditional/revival object vs The Animals recording.
- `We Shall Overcome`: movement/traditional/protest standard.
- `Turn! Turn! Turn!`: Byrds recording and Pete Seeger authorship context.
- Jazz standards such as `My Favorite Things` and `Round Midnight`.

Policy:

- Create a composition or standard object when the song is bigger than one recording.
- Link definitive recordings as recording objects.
- Allow survey to ask either composition-level or recording-level questions depending on context.

## Hymns and Worship Standards

Worship standards often function as songbook compositions with many live/church versions.

Examples:

- `Amazing Grace`
- `Shout to the Lord`
- `In Christ Alone`
- `Build My Life`
- `Break Every Chain`
- `Way Maker`

Policy:

- Use composition-first handling for church-songbook standards.
- Preserve important artist/live recordings separately.
- Do not merge church brands, songwriters, and congregational versions into one artist row.

## Show Tunes and Cast Recordings

Show tunes need show/work, composition, cast recording, and performer context.

Examples:

- `We Don't Talk About Bruno`: Encanto cast credit variants.
- `My Favorite Things`: musical-theater composition vs John Coltrane jazz recording.
- `Defying Gravity`: show tune, cast recording, and performer-specific recording.

Policy:

- Treat the show/film as context, not as the sole artist.
- Preserve cast recording credits exactly.
- Link individual performers only through credit roles unless the recording is marketed as a solo artist recording.

## Soundtrack Pop Recordings

Soundtrack pop recordings are recording objects attached to soundtrack context.

Examples:

- Whitney Houston `I Will Always Love You` vs Dolly Parton original.
- Celine Dion `My Heart Will Go On`.
- Prince and The Revolution `Purple Rain`.

Policy:

- Keep soundtrack pop recordings distinct from source compositions and original artist versions.
- Soundtrack membership can be separate from artist-family membership.

## Queue Example Decisions

| title | policy disposition |
|---|---|
| `Hound Dog` | Same composition/source lineage likely; recordings must remain separate. |
| `The Twist` | Same composition/lineage likely; Hank Ballard and Chubby Checker recordings remain separate. |
| `Shake, Rattle and Roll` | Source/hit cover split; do not title-merge. |
| `That's All Right` | Source/hit cover split; do not title-merge. |
| `Walk This Way` | Aerosmith original and Run-DMC/Aerosmith remake remain separate recordings. |
| `Gloria` | Multi-composition/multi-recording review; do not merge by title. |
| `House of the Rising Sun` | Traditional composition object needed; The Animals recording remains distinct. |
| `We Shall Overcome` | Composition/movement standard object needed; performer rows require caution. |
| `God Only Knows` | Review: likely different compositions across Beach Boys and for KING & COUNTRY unless confirmed otherwise. |
| `We Don't Talk About Bruno` | Cast/show recording credit review; likely display-credit normalization plus cast entity modeling. |
| `I'll Take You There` | Likely display-name normalization for Staple Singers / The Staple Singers, then same recording review. |
| `Love Shack` | Likely display-name normalization for B-52's / B-52s, then same recording review. |
| `Zombie` | Different compositions/recordings; Fela Kuti and The Cranberries remain separate. |
