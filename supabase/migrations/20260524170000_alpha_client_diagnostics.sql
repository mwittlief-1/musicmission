create table if not exists public.alpha_client_diagnostic_artifacts (
  id uuid primary key default gen_random_uuid(),
  client_artifact_id text unique not null,
  tester_alias text,
  user_id uuid references auth.users (id) on delete set null,
  artifact_type text not null
    check (artifact_type in (
      'apple_music_signal_payload',
      'survey_page_selection_audit',
      'survey_evidence_export',
      'mission_generation_request_packet',
      'mission_generation_result',
      'mission_import_result',
      'client_state_snapshot',
      'client_error_event'
    )),
  schema_version text not null,
  survey_session_id text,
  client_request_id text,
  generation_run_id uuid references public.alpha_generation_runs (id) on delete set null,
  mission_id text,
  source_app_version text,
  source_app_build text,
  redaction_level text not null default 'support_diagnostic'
    check (redaction_level in ('support_diagnostic', 'pm_summary', 'redacted')),
  upload_cadence text not null default 'manual_share'
    check (upload_cadence in ('manual_share', 'after_saved_evidence', 'scheduled')),
  consent_terms_version text,
  consent_accepted_at timestamptz,
  payload jsonb not null,
  payload_sha256 text not null,
  client_created_at timestamptz,
  received_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  deleted_at timestamptz
);

create index if not exists alpha_client_diagnostic_artifacts_created_at_idx
  on public.alpha_client_diagnostic_artifacts (created_at desc);

create index if not exists alpha_client_diagnostic_artifacts_tester_alias_idx
  on public.alpha_client_diagnostic_artifacts (tester_alias);

create index if not exists alpha_client_diagnostic_artifacts_user_id_idx
  on public.alpha_client_diagnostic_artifacts (user_id);

create index if not exists alpha_client_diagnostic_artifacts_artifact_type_idx
  on public.alpha_client_diagnostic_artifacts (artifact_type);

create index if not exists alpha_client_diagnostic_artifacts_survey_session_id_idx
  on public.alpha_client_diagnostic_artifacts (survey_session_id);

create index if not exists alpha_client_diagnostic_artifacts_client_request_id_idx
  on public.alpha_client_diagnostic_artifacts (client_request_id);

create index if not exists alpha_client_diagnostic_artifacts_generation_run_id_idx
  on public.alpha_client_diagnostic_artifacts (generation_run_id);

create index if not exists alpha_client_diagnostic_artifacts_payload_sha256_idx
  on public.alpha_client_diagnostic_artifacts (payload_sha256);

drop trigger if exists set_alpha_client_diagnostic_artifacts_updated_at
  on public.alpha_client_diagnostic_artifacts;
create trigger set_alpha_client_diagnostic_artifacts_updated_at
before update on public.alpha_client_diagnostic_artifacts
for each row
execute function public.set_updated_at();

alter table public.alpha_client_diagnostic_artifacts enable row level security;

comment on table public.alpha_client_diagnostic_artifacts is
  'Trusted Alpha PM/support diagnostic artifacts linking Apple Music, Survey, generation, and app import behavior. Written by Edge Functions with service-role credentials.';

comment on column public.alpha_client_diagnostic_artifacts.redaction_level is
  'Support visibility marker. Diagnostic artifacts are not user-facing product state and do not promote Atlas truth.';

comment on column public.alpha_client_diagnostic_artifacts.payload is
  'Diagnostic payload. Must not include auth tokens, service-role keys, Apple identity tokens, or hidden simulator truth.';
