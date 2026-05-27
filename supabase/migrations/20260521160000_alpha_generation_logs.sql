create extension if not exists pgcrypto;

create table if not exists public.alpha_generation_runs (
  id uuid primary key default gen_random_uuid(),
  client_request_id text unique,
  tester_alias text,
  status text not null default 'received'
    check (status in ('received', 'generating', 'app_import_candidate', 'review_needed', 'blocked', 'failed')),
  app_import_status text not null default 'not_checked'
    check (app_import_status in ('not_checked', 'app_import_candidate', 'review_needed', 'blocked')),
  prompt_version text not null,
  model text not null,
  adapter_version text,
  mission_output_schema_version text not null,
  app_mission_schema_version text not null,
  input_packet_sha256 text,
  input_packet jsonb not null,
  openai_request jsonb,
  raw_openai_response jsonb,
  parsed_generation jsonb,
  app_missions jsonb,
  validation jsonb,
  token_usage jsonb,
  latency_ms integer,
  error_message text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists alpha_generation_runs_created_at_idx
  on public.alpha_generation_runs (created_at desc);

create index if not exists alpha_generation_runs_tester_alias_idx
  on public.alpha_generation_runs (tester_alias);

create table if not exists public.alpha_evidence_artifacts (
  id uuid primary key default gen_random_uuid(),
  client_artifact_id text unique,
  tester_alias text,
  artifact_type text not null
    check (artifact_type in (
      'survey_evidence_export',
      'mission_generation_digest_view',
      'reaction_session',
      'mission_review',
      'atlas_delta_candidate'
    )),
  schema_version text not null,
  payload jsonb not null,
  client_created_at timestamptz,
  created_at timestamptz not null default now()
);

create index if not exists alpha_evidence_artifacts_created_at_idx
  on public.alpha_evidence_artifacts (created_at desc);

create index if not exists alpha_evidence_artifacts_tester_alias_idx
  on public.alpha_evidence_artifacts (tester_alias);

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists set_alpha_generation_runs_updated_at on public.alpha_generation_runs;
create trigger set_alpha_generation_runs_updated_at
before update on public.alpha_generation_runs
for each row
execute function public.set_updated_at();

alter table public.alpha_generation_runs enable row level security;
alter table public.alpha_evidence_artifacts enable row level security;

comment on table public.alpha_generation_runs is
  'Trusted Alpha generation audit trail. Written by Supabase Edge Functions using service-role credentials.';

comment on table public.alpha_evidence_artifacts is
  'Trusted Alpha evidence artifacts for PM/Codex review. No direct anonymous client access by default.';
