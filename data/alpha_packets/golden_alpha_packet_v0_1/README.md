# Golden Alpha Packet v0.1

Generated: 2026-05-21T20:00:00Z

This packet is the first reproducible integration spine for trusted Alpha:

```text
Survey Evidence Export
-> MissionGenerationDigestView
-> candidate pool
-> Supabase generate-first-mission-batch request
-> Waymark mission output
-> reviewed app-import gate
-> mission.v0.2
```

## App Mission

- Mission ID: `MIS_NIRVANA_TO_CURRENT_ALPHA_GOLDEN`
- Title: `From Nirvana to Current Pulse`
- Items: `7`
- Schema: `mission.v0.2`

## Gate Status

- Source generation schema valid: `True`
- Source generation readiness: `product_pass_candidate`
- Model declared app import ready: `False`
- Score failures: `0`
- Score partials: `0`
- Manual app-import review override: `True`
- Packet app import status: `app_import_candidate`

The manual override exists only to create a complete app-import integration packet from a schema-valid,
zero-failure source generation. It is not evidence that autonomous generation is ready for external testers.

## Key Files

- `inputs/survey_evidence_export.json`
- `inputs/mission_generation_digest_view.json`
- `inputs/candidate_pool.json`
- `request/supabase_generate_first_mission_batch_request.json`
- `generation/mission_output_waymark_v0_1.raw.json`
- `generation/mission_output_waymark_v0_1.reviewed_app_import_candidate.json`
- `review/app_import_review_gate.json`
- `response/supabase_generate_first_mission_batch_response.json`
- `app_import/app_mission_v0_2.json`
- `app_import/app_mission_collection_v0_2.json`

## Validation

```sh
python3 scripts/validate_survey_evidence_export_v0_1.py --export data/alpha_packets/golden_alpha_packet_v0_1/inputs/survey_evidence_export.json
python3 scripts/validate_mission_json.py data/alpha_packets/golden_alpha_packet_v0_1/app_import/app_mission_v0_2.json
```
