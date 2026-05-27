# Supabase Adapter Reconciliation v0.1

Generated: 2026-05-22

## Purpose

This note reconciles the Supabase Edge Function adapter with the golden Alpha packet builder.

Controlling artifacts:

- `supabase/functions/generate-first-mission-batch/index.ts`
- `scripts/build_alpha_golden_packet_v0_1.py`
- `data/alpha_packets/golden_alpha_packet_v0_1/`

## Shared Contract

Both adapters map rich mission-generation output into app `mission.v0.2`.

Shared app mission fields:

- `schema_version`
- `mission_id`
- `mission_title`
- `mission_version`
- `created_at`
- `mission_type`
- `recommended_format`
- `hypothesis`
- `inflation_warning`
- `success_bar`
- `run_instructions`
- `post_run_inference_rules`
- `items`

Shared item fields:

- `item_id`
- `sequence`
- `item_type`
- `artist`
- `title`
- `album`
- `year`
- `why_included`
- `expected_test_signal`
- `player_card.flip_side`
- `feedback_chip_sets.hit`
- `feedback_chip_sets.partial`
- `feedback_chip_sets.ok_shelf`
- `feedback_chip_sets.miss`
- `apple_music_resolution.status = unresolved`
- `apple_music_resolution.resolver = not_attempted`
- `notes`

## Intentional Differences

The golden packet is a fixed fixture. The Edge Function is a live adapter.

Allowed differences:

- `created_at`
  - Golden packet uses a fixed timestamp for reproducibility.
  - Edge Function uses request-time timestamp.
- mission provenance text
  - Golden packet notes say `Golden Alpha`.
  - Edge Function notes say generated through Supabase/OpenAI.
- `run_id`
  - Golden packet uses a stable fake UUID.
  - Edge Function uses `crypto.randomUUID()`.
- token/latency usage
  - Golden packet copies source harness metadata.
  - Edge Function logs live OpenAI response usage or replay zeroes.

Not allowed:

- returning app missions when status is `review_needed`, `blocked`, or `failed`
- app mission IDs that fail Core import gate
- pre-resolved Apple Music evidence in imported mission payloads
- missing expected signal, player card, or four feedback chip sets
- hidden simulator truth in request, response, or logs

Trusted Alpha recovery exception:

- `app_import_candidate_with_review_flags` may return app missions only after Supabase/Core implement the Alpha-only tolerance path.
- That status requires both rich generation validation and app `mission.v0.2` validation to pass.
- Review flags must be persisted in the audit envelope and client diagnostics.
- `review_needed` remains non-importing; use it for missions that are schema-valid but not safe enough for app import.

## Fixture Replay

The Edge Function supports local replay only when:

```text
WAYMARK_ALPHA_REPLAY_MODE=true
```

Replay requests may include:

```json
{
  "replay_generation_output": {}
}
```

If replay mode is not enabled, requests containing `replay_generation_output` return:

```text
replay_mode_disabled
```

This keeps local smoke tests deterministic without creating a production bypass.

## Audit Envelope

The function logs:

- `client_request_id`
- `tester_alias`
- `status`
- `app_import_status`
- `prompt_version`
- `model`
- `adapter_version`
- `mission_output_schema_version`
- `app_mission_schema_version`
- `input_packet_sha256`
- `input_packet`
- `openai_request`
- `raw_openai_response`
- `parsed_generation`
- `app_missions`
- `validation`
- `token_usage`
- `latency_ms`
- `error_message`

For trusted Alpha recovery, the audit envelope should additionally preserve:

- `alpha_review_flags`
- `alpha_import_tolerance_policy_version`
- `mission_generation_attempt_index`
- `mission_generation_max_attempts`
- `prior_imported_mission_ids`
- `prior_imported_candidate_ids`
- `prior_review_needed_reasons`

Live persistence requires `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` in the Edge Function environment. These secrets are never app-safe.
