# Survey Simulator Build Brief

Generated: 2026-05-20

Source input:

- `/Users/matt_wittlief_home/Downloads/waymark_survey_simulation_harness_spec_v0_1.md`

## Purpose

Build a repeatable harness that tests whether the staging canonical graph plus Apple Music-style seed signals can generate an adaptive onboarding Survey that learns useful taste evidence quickly.

The harness should answer:

- Can the graph produce a reasonable Page 1?
- Does Apple bias improve relevance without overfitting stale or misleading signals?
- Does Page 2 adapt meaningfully after Page 1?
- How much Survey input is enough?
- Can held-out hidden reactions be predicted better after more evidence?
- Does the resulting starter Atlas / first mission language feel like Waymark?

## Non-Negotiable Boundaries

- The Survey Builder sees only observable inputs:
  - simulated Apple payload
  - canonical graph data
  - prior visible survey responses
- The Survey Builder must never see:
  - hidden archetype weights
  - hidden anti-affinities
  - full hidden reaction corpus
  - hidden reason tags
  - fake profile label
- Survey writes should become Signals or provisional update candidates, not promoted Atlas state.
- The canonical graph is read-only.

## Page Model

Use 12 tiles per page.

Object-stage flow:

```text
Artists -> Albums -> Songs
```

Initial variants:

| variant | artist pages | album pages | song pages | total tiles |
|---|---:|---:|---:|---:|
| 2/1/1 | 2 | 1 | 1 | 48 |
| 2/1/2 | 2 | 1 | 2 | 60 |
| 3/1/1 | 3 | 1 | 1 | 60 |
| 3/2/3 | 3 | 2 | 3 | 96 |

Page 1 modes:

- `generic_graph_seed`
- `apple_biased_seed`

Do not add declared-goal Page 1 mode in v0.1.

## Fake Profile Requirements

Create at least ten fake users:

1. Classic Suburban Dad
2. Pop / Radio Generalist
3. Alt Formation User
4. Country-Pop Listener
5. R&B / Hip-Hop Listener
6. Theater / Family Context User
7. Indie / Prestige Listener
8. Metal / Heavy User
9. Modern Pop + TikTok User
10. Low-Library Streaming User

Each should include:

- 2 primary archetype affinities
- 2 secondary archetype affinities
- 1 context / nostalgia / family lane
- 1 false-nearby lane
- hidden anti-affinities
- sparse hidden reaction corpus
- simulated Apple payload

## Reaction Normalization

Simulator-facing reactions:

- `love`
- `like`
- `ok`
- `dont_know_enough`
- `dont_like`

These need a map to app/UI and Atlas Signal terms.

Current likely mapping:

| simulator | app/UI candidate | Atlas signal interpretation |
|---|---|---|
| `love` | `favorite` | strong positive |
| `like` | `like` | positive |
| `ok` | `fine` | weak positive / familiarity |
| `dont_know_enough` | `dontKnow` | unknown / insufficient familiarity |
| `dont_like` | `notForMe` | negative, scope carefully |

The final UI labels can change later; the simulator should use stable internal enums.

## Hidden Data Separation

The spec's hidden reaction corpus includes `reason_tags`.

Implementation rule:

- Hidden `reason_tags` may be used for evaluation and profile design.
- Hidden `reason_tags` must not be exported into visible survey transcript.
- Hidden `reason_tags` must not be available to Survey Builder or predictor.
- If the simulated UI supports visible chips, store those separately as observed `selected_tags` and `shown_unselected_tags`.

## ID and Music Reference Policy

Do not use vague IDs such as `artist_fleetwood-mac` as canonical IDs.

Use a typed reference:

```json
{
  "object_type": "artist",
  "ref_source": "canonical_graph",
  "canonical_artist_id": "fleetwood-mac",
  "display_name": "Fleetwood Mac",
  "resolution_state": "resolved"
}
```

For simulator-local or unresolved Apple objects:

```json
{
  "object_type": "song_recording",
  "ref_source": "external_catalog",
  "external_catalog_refs": {
    "apple_music_id": "..."
  },
  "display_name": "...",
  "resolution_state": "needs_resolution"
}
```

For v0.1, the candidate universe can be restricted to canonical graph objects, but payload and Atlas schemas should not assume every real user object is canonical.

## Required Outputs

Recommended directory:

```text
data/survey_simulation/
  README.md
  fake_profiles/
  apple_payloads/
  hidden_reaction_corpora/
  runs/
  reports/
```

Per run:

- `survey_run.json`
- `survey_transcript.md`
- `page_generation_log.json`
- `recorded_responses.json`
- `apple_payload_used.json`
- `hidden_lookup_coverage_report.md`

Reports:

- `apple_seed_simulation_report.md`
- `mixed_profile_simulation_report.md`
- `page_count_comparison_report.md`
- `prediction_backtest_report.md`
- `product_feel_report.md`
- `simulation_acceptance_report.md`

## Acceptance Criteria

The v0.1 harness succeeds when:

- fake profiles have hidden mixed archetype seeds;
- each profile has a simulated Apple payload;
- each profile has a sparse hidden artist/album/song reaction corpus;
- missing hidden responses become `dont_know_enough`;
- Page 1 can run from graph-only and Apple-biased modes;
- Page 2 adapts from Page 1 responses;
- artist, album, and song stages all run;
- page-count variants run successfully;
- transcripts and logs are exported;
- held-out prediction backtest runs;
- product-feel generation emits starter Atlas summaries and sample mission briefs as proposals only;
- Apple residue does not dominate Page 1.

## Suggested First Implementation Slice

1. Build validators for fake profiles, Apple payloads, and hidden corpora.
2. Load canonical graph emitted tables read-only.
3. Generate graph-only Artist Page 1.
4. Generate Apple-biased Artist Page 1.
5. Simulate responses with hidden corpus lookup.
6. Export run transcript and hidden coverage report.
7. Add Page 2 adaptation.
8. Add album and song stages.
9. Add page-count comparison.
10. Add prediction backtest and product-feel reports.
