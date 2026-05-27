# Family 17 Import Warnings

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
| Holiday Mariah / general Mariah | Keep Family 17 seasonal rows separate from Family 12 pop-vocal rows. |
| `mr-brightside`, `dont-stop-believin`, `livin-on-a-prayer` | Context familiarity should not by itself infer indie rock or arena rock appetite. |
| Line-dance songs | `cha-cha-slide`, `cupid-shuffle`, and `ymca` should operate as event/context waypoints. |
| Disney spillover | `let-it-go`, `we-dont-talk-about-bruno`, and related soundtrack rows may be primarily owned by Family 15. |
| Traditional/kids repertoire | Composition-level objects need non-artist canonical handling where performer is not meaningful. |
| Suppress row | `ahab-the-arab` is retained for duplicate/historical handling but set to suppress due dated stereotype risk. |
