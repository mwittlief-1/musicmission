alter table public.alpha_client_diagnostic_artifacts
  drop constraint if exists alpha_client_diagnostic_artifacts_artifact_type_check;

alter table public.alpha_client_diagnostic_artifacts
  add constraint alpha_client_diagnostic_artifacts_artifact_type_check
  check (artifact_type in (
    'apple_music_signal_payload',
    'survey_page_selection_audit',
    'survey_evidence_export',
    'mission_generation_request_packet',
    'mission_generation_result',
    'mission_import_result',
    'mission_selection_audit',
    'client_state_snapshot',
    'client_error_event'
  ));

comment on constraint alpha_client_diagnostic_artifacts_artifact_type_check
  on public.alpha_client_diagnostic_artifacts is
  'Allowed trusted Alpha diagnostic artifact types, including deterministic mission selection audit packets.';
