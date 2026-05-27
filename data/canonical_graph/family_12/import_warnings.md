# Family 12 Import Warnings

## Schema Drift Normalized

| area | warning |
|---|---|
| role enums | Candidate rows use only normalized role enums from the family 1-4 examples. |
| tier enums | Recognition and survey tiers are normalized to mass/high/medium/low/cult and core/standard/edge/suppress. |

## Duplicate / Membership Semantics

| object class | duplicate canonical IDs across archetypes | import handling |
|---|---:|---|
| artists | 0 | Treat duplicate proposed artist IDs as one canonical artist with multiple archetype memberships. |
| albums | 0 | Treat duplicate proposed album IDs as one canonical album with multiple memberships. |
| songs | 0 | Treat duplicate proposed song IDs as one recording unless a warning says versions must split. |

## High-Risk Cases

| risk | handling |
|---|---|
| `beyonce` solo vs group-era credits | Do not merge Destiny-era recordings into solo Beyonce without explicit alias/member handling. |
| `mariah-carey` Christmas rows | Family 17 should own seasonal Mariah Christmas context; Family 12 rows describe general pop/vocal-pop appetite. |
| `purple-rain` album type | Stored as soundtrack album object here because it is a pop-sovereign album gateway; Family 15 may also claim soundtrack membership. |
| `the-weeknd` / `doja-cat` / `ice-spice` | These are boundary rows; primary genre appetite may belong to R&B/rap or internet-native families. |
| Current hits from 2023-2024 | Recheck recognition tier before hard lock because streaming-era monoculture can move quickly. |
