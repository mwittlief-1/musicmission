# Mission Enrichment Runtime Candidate Report v0.2

Date: 2026-06-04

Status: Historical runtime-candidate report. Superseded for current approval status by `mission_enrichment_alpha_provisional_lock_2026_06_04.md`.

Current status note: CEO/Product provisionally locked Mission Enrichment v0.2 for alpha on 2026-06-04 after six Build 45 live OpenAI outputs passed validation. This report preserves the earlier runtime-candidate evidence from the pre-lock slice.

## Summary

This slice converts the Mission Enrichment v0.2 product direction into a local contract package with machine-readable schemas, registry JSON, deterministic prefilter logic, a prompt template, validator tooling, fixtures, tests, and a dry-run prompt runner.

Mission selection remains out of scope. The package assumes a deterministic mission already exists before Mission Enrichment runs.

## Files Created

- `schemas/mission_enrichment_input_v0_2.schema.json`
- `schemas/mission_enrichment_output_v0_2.schema.json`
- `schemas/secondary_reaction_tag_registry_v0_2.schema.json`
- `registry/secondary_reaction_tag_registry_v0_2.json`
- `prompts/mission_enrichment_prompt_v0_2.md`
- `scripts/build_mission_enrichment_input_v0_2.py`
- `scripts/prefilter_secondary_tags_v0_2.py`
- `scripts/validate_mission_enrichment_output_v0_2.py`
- `scripts/run_mission_enrichment_prompt_test_v0_2.py`
- `tests/fixture_contract_tests_v0_2.py`
- `types/index.ts`
- `fixtures/positive/*.json`
- `fixtures/negative/*.json`
- `runs/20260604T162934Z/*`

Existing package docs were updated to reflect the runtime-candidate scope.

## Product Decisions Encoded

- Primary reactions are `love`, `like`, `ok`, and `dislike`.
- Mission `ok` is treated as weak explicit evidence: waypoint, context, uncertainty, or weak non-failure.
- Default max secondary tags per route item is six.
- `display_label` must exactly match the approved registry label.
- `LESS_LIKE_THIS` is `dislike` only.
- Route item applicability flags are required.
- Added `DID_NOT_HOLD_ATTENTION`.
- Added `WRONG_VERSION_OR_RECORDING`.
- `RIGHT_ARTIST_WRONG_TRACK` is gated by artist context.
- `NEEDS_MORE_CONTEXT` is gated by album/context/long-form applicability.
- Founder-specific and rock-assumptive tags remain excluded.

## Registry

The machine-readable registry contains the v0.2 approved draft IDs plus the two added runtime-candidate tags. Deliberately excluded:

- `SLOP_SIGNAL`
- `TOO_HEAVY`
- `TOO_POLISHED`
- `RIFF_WORKED`

## Prefilter Summary

`scripts/prefilter_secondary_tags_v0_2.py` deterministically narrows the registry to 8-14 candidate IDs per route item.

Inputs used:

- Route item affinity facets.
- User alignment hints.
- Mission type.
- Route role.
- Risk level.
- Applicability flags.
- Optional `artist_context_available`.
- Compact user Atlas brief.

Fixture prefilter counts:

- Build 45-style fixture: `[14, 14]`
- Pop-forward fixture: `[14]`
- Hip-hop/R&B fixture: `[14]`
- Country/folk fixture: `[14]`
- Jazz/classical/instrumental fixture: `[14]`
- Electronic/dance fixture: `[14]`
- Low-information first mission fixture: `[11]`
- Mature mission #40 fixture: `[14]`
- Boundary-test fixture: `[14]`
- Context-dependence fixture: `[14]`

## Validator Summary

`scripts/validate_mission_enrichment_output_v0_2.py` validates:

- JSON schema conformance.
- Mission ID preservation.
- Route item coverage and order.
- Known and prefiltered tag IDs only.
- Max six tags per item.
- Sequential tag ranks.
- Exact registry display labels.
- Exact registry Atlas effects.
- Valid primary reaction subsets.
- Linked song affinity tags and alignment hints from input only.
- `LESS_LIKE_THIS` dislike-only.
- Artist/context/voice/lyrics applicability gates.
- Raw graph ID and raw affinity tag display-copy leaks.
- Founder-specific and final-taste copy patterns.

Known limitation: the validator can catch explicit unsupported IDs/tags and banned copy patterns, but it cannot fully prove that every natural-language music fact is non-invented. Product review and prompt tests still need to inspect generated copy.

## Fixtures

Positive inputs:

- `build45_like_runtime_candidate_input.json`
- `pop_forward_first_mission_input.json`
- `hiphop_rnb_forward_input.json`
- `country_folk_forward_input.json`
- `jazz_classical_instrumental_input.json`
- `electronic_dance_forward_input.json`
- `low_information_first_mission_input.json`
- `mature_mission_40_input.json`
- `boundary_test_mixed_signal_input.json`
- `context_dependence_mission_input.json`

Positive output:

- `build45_like_runtime_candidate_output.json`

Negative outputs:

- `changed_route_item_id_output.json`
- `changed_route_order_output.json`
- `display_label_mismatch_output.json`
- `duplicate_route_item_output.json`
- `founder_specific_banned_language_output.json`
- `instrumental_with_lyrics_tag_output.json`
- `less_like_this_after_ok_output.json`
- `missing_route_item_output.json`
- `mission_id_mismatch_output.json`
- `needs_more_context_without_applicable_context_output.json`
- `raw_affinity_tag_in_display_copy_output.json`
- `right_artist_wrong_track_without_artist_context_output.json`
- `tag_not_prefiltered_output.json`
- `too_many_tags_output.json`
- `unknown_tag_id_output.json`
- `voice_chip_on_non_vocal_track_output.json`

## Test Commands

Fixture/schema/product-rule tests:

```sh
.venv/bin/python data/product_contracts/mission_enrichment_v0_2/tests/fixture_contract_tests_v0_2.py
```

Result:

```text
Ran 4 tests in 0.220s
OK
```

Dry prompt run:

```sh
.venv/bin/python data/product_contracts/mission_enrichment_v0_2/scripts/run_mission_enrichment_prompt_test_v0_2.py --dry-run
```

Result:

```text
passed=true
error_count=0
warning_count=0
model=gpt-5.4-mini
mode=dry_run
```

Dry-run artifacts:

- `runs/20260604T162934Z/input.json`
- `runs/20260604T162934Z/prompt.md`
- `runs/20260604T162934Z/raw_model_output.json`
- `runs/20260604T162934Z/validated_output.json`
- `runs/20260604T162934Z/validation_report.json`
- `runs/20260604T162934Z/validation_report.md`
- `runs/20260604T162934Z/cost_latency_model_log.json`

## OpenAI Execution

No live OpenAI completion was executed in this slice. The run used dry mode and wrote a validator-ready placeholder output.

The prompt runner preserves the runtime target model name `gpt-5.4-mini` in its model log and does not silently substitute another model.

## Remaining Risks

- Product has not yet reviewed the generated fixture copy and registry tone as a runtime candidate.
- The minimum 24-output live prompt matrix was not run.
- No live `gpt-5.4-mini` output has been validated yet in this environment.
- The fixtures are synthetic and intentionally small; they do not prove full six-song production route behavior.
- `artist_context_available` is an optional route-item flag added for deterministic gating; app/backend integration should decide the canonical source of that fact.
- Validator language scans are guardrails, not a complete natural-language fact checker.

## Recommendation

This package is ready for Product review and a controlled live prompt-test pass.

It is not yet ready for full app/backend integration. Proceed to integration only after Product approves the registry/copy behavior and at least one real `gpt-5.4-mini` output passes the validator with externally plausible copy.
