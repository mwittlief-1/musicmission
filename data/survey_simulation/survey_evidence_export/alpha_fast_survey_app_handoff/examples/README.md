# Alpha Survey Slate Render Examples v0.1

These examples are app-renderable pre-response slate packets. They contain visible tile identity, graph provenance, Apple exposure priors where applicable, response controls, and planned evidence-export linkage. They do not contain captured user reactions, hidden simulator truth, raw candidate scores, hidden reason tags, or lookup state.

| mode | run | page mode | tiles | Apple applied | packet |
| --- | --- | --- | ---: | --- | --- |
| `graph_only` | `RUN_001_GRAPH_SEED` | `generic_graph_seed` | 12 | `False` | `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/examples/graph_only_artist_page_001_alpha_survey_slate_packet.json` |
| `apple_biased` | `RUN_002_APPLE_BIASED` | `apple_biased_seed` | 12 | `True` | `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/examples/apple_biased_artist_page_001_alpha_survey_slate_packet.json` |

## Completed-Response Packet Examples

These examples use public visible survey packets and include captured simulated responses for schema and evidence-export integration checks. They are not pre-response render fixtures.

| profile | config | packet |
| --- | --- | --- |
| `public_profile_05` | `A3_Al1_S2` | `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/examples/public_profile_05_A3_Al1_S2_alpha_survey_page_packet.json` |
| `public_profile_06` | `A3_Al1_S2` | `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/examples/public_profile_06_A3_Al1_S2_alpha_survey_page_packet.json` |

## Live Smoke Recovery Diagnostic Fixture

This fixture is construction-only diagnostic coverage for the quarantine reason taxonomy. It is not a user-facing Survey packet and Atlas must ignore its `construction_only_excluded` rows.

| fixture | purpose | packet |
| --- | --- | --- |
| `live_three_quarantine_cases` | Exercises `missing_displayed_page`, `missing_tile_or_ref`, and `apple_only_unmatched_object` quarantine reasons. | `data/survey_simulation/survey_evidence_export/alpha_fast_survey_app_handoff/examples/live_three_quarantine_cases_survey_evidence_export.json` |
