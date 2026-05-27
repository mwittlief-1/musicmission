# Canonical Identity Policy

Generated: 2026-05-20

## Principle

Canonical identity is not the same as display credit. The graph should store stable canonical entities while preserving the exact credited artist text that made the row meaningful to the listener.

Import rule: create canonical entity rows, then membership rows. Do not create new artist entities just because the same artist appears in more than one family or archetype.

## Artist Aliases

| rule | policy |
|---|---|
| Display punctuation/case differs only | Normalize to one canonical artist ID and preserve display names as aliases. |
| Stage name vs legal name | Use the public music identity as canonical unless survey recognition depends on the alternate name. |
| Producer/project alias | Do not merge automatically. Create alias review records for cases like Larry Heard / Mr. Fingers / Fingers Inc. and Juan Atkins / Model 500 / Cybotron. |
| Name changes | Preserve current and historical display aliases; canonical ID should use the identity most useful for user recognition unless the identities are musically distinct. |

Safe display normalization examples from dry run:

- `Kool & The Gang` / `Kool & the Gang`
- `Martha & the Vandellas` / `Martha and the Vandellas`
- `Simon & Garfunkel` / `Simon and Garfunkel`
- `Smokey Robinson & The Miracles` / `Smokey Robinson and the Miracles`

## Group vs Solo Artist

Group and solo entities remain separate unless the row is explicitly a solo artist alias.

Examples:

- `Diana Ross` is not automatically `The Supremes`.
- `Michael Jackson` is not automatically `Jackson 5`.
- `Smokey Robinson` is not automatically `Smokey Robinson and the Miracles`.
- `Beyonce` solo rows do not absorb Destiny's Child recordings.
- `Darius Rucker` solo catalog does not merge with Hootie & the Blowfish.

Membership rows may connect the same person to multiple graph identities later, but surveys should not collapse group and solo taste signals.

## Credited Artist vs Canonical Artist

Every song and album row should preserve:

- `credited_artist_name`: exact row/display credit.
- `canonical_artist_id`: stable artist entity when applicable.
- `credit_context`: solo, group, duet, featured, cast, church brand, producer project, fictional performer, Various Artists.

The current graph stores artist names directly in object rows. For staging, that is acceptable. For production, credit context needs a sidecar table before automatic merging.

## Duet and Collaboration Artist IDs

Duets and collaborations should generally be recording credits, not new canonical artist entities, unless the collaboration has a durable public identity.

Rules:

- Use one canonical song recording ID for the credited recording.
- Link each participating canonical artist through a future credit table.
- Do not merge the collaboration into either solo artist.
- Only create a collaboration artist entity when the collaboration is a stable act.

Examples:

- `Waylon Jennings and Willie Nelson` on `Mammas Don't Let Your Babies Grow Up to Be Cowboys` remains a collaboration recording credit.
- `Run-DMC` with Aerosmith on `Walk This Way` remains distinct from Aerosmith's original recording.
- `Luis Fonsi and Daddy Yankee` on `Despacito` remains a collaboration recording credit.

## Featured Artists

Featured artists should not change canonical ownership of the primary artist row by default.

Rules:

- Preserve featured credit text.
- Store featured artists in recording credits.
- Do not duplicate the same recording under both primary and featured artist IDs.
- If the feature is the user-recognition reason, add a warning or credit prominence flag.

Examples:

- `David Guetta featuring Sia - Titanium`
- `Wizkid featuring Tems - Essence`
- `God's Property featuring Kirk Franklin - Stomp`
- `Cardi B feat. Megan Thee Stallion - WAP`

## Cast Recordings

Cast recordings are recording credits, not conventional band entities.

Rules:

- Create or preserve a cast-recording credit entity where needed.
- Do not merge a cast recording into the composer, show, film, or individual performer.
- If multiple cast versions exist, each recording version needs separate handling.

Examples:

- `Original Broadway Cast of Hamilton`
- `Original Broadway Cast of Wicked`
- `Encanto Cast`
- `Carolina Gaitan, Mauro Castillo, Adassa, Rhenzy Feliz, Diane Guerrero, Stephanie Beatriz and Encanto Cast`

## Church and Worship Brands

Church/worship brands are not automatically interchangeable with songwriters, individual worship leaders, or parent churches.

Rules:

- Keep `Hillsong Worship`, `Hillsong United`, and related brands distinct unless an alias table explicitly links them.
- Keep `Elevation Worship`, `Maverick City Music`, `Bethel Music`, `Passion`, and individual featured vocalists as separate credit contexts.
- Worship standards need composition-first review when many church versions exist.

Examples:

- `People - Hillsong United`
- `Jireh - Elevation Worship and Maverick City Music featuring Chandler Moore and Naomi Raine`
- `Build My Life - Pat Barrett`
- `Shout to the Lord - Darlene Zschech`

## Producer-Led and Various Artists Albums

Producer-led albums and Various Artists albums can be canonical album objects.

Rules:

- `Various Artists` is an album credit context, not a canonical artist preference signal by itself.
- Producer-led soundtrack or compilation albums should keep producer/composer/curator roles separate.
- Compilation gateway albums should not merge into original release albums.

Examples:

- `Saturday Night Fever - Various Artists`
- `Guardians of the Galaxy: Awesome Mix Vol. 1 - Various Artists`
- `Black Panther - Ludwig Goransson` is distinct from Kendrick Lamar-curated soundtrack context.

## Soundtrack, Cast, Composer Entities

Production import should support separate entity types or context tags:

- film/show entity;
- soundtrack album;
- score album;
- cast recording;
- pop single from soundtrack;
- composer;
- performer;
- fictional performer.

Do not force these into one artist model. The graph can ask better questions if `Hamilton`, Lin-Manuel Miranda, Original Broadway Cast, and `My Shot` remain linked but distinct.
