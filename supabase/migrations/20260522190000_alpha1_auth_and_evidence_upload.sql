create table if not exists public.alpha_tester_profiles (
  user_id uuid primary key references auth.users (id) on delete cascade,
  tester_alias text unique,
  display_label text,
  terms_version_accepted text,
  terms_accepted_at timestamptz,
  onboarding_completed_at timestamptz,
  survey_completed_at timestamptz,
  first_generation_run_id uuid references public.alpha_generation_runs (id),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.alpha_tester_profiles enable row level security;

drop policy if exists "alpha testers can read own profile" on public.alpha_tester_profiles;
create policy "alpha testers can read own profile"
on public.alpha_tester_profiles
for select
to authenticated
using (auth.uid() = user_id);

drop policy if exists "alpha testers can insert own profile" on public.alpha_tester_profiles;
create policy "alpha testers can insert own profile"
on public.alpha_tester_profiles
for insert
to authenticated
with check (auth.uid() = user_id);

drop policy if exists "alpha testers can update own profile" on public.alpha_tester_profiles;
create policy "alpha testers can update own profile"
on public.alpha_tester_profiles
for update
to authenticated
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

alter table public.alpha_evidence_artifacts
  add column if not exists user_id uuid references auth.users (id) on delete set null,
  add column if not exists upload_status text not null default 'received'
    check (upload_status in ('received', 'accepted', 'replaced', 'blocked', 'deleted')),
  add column if not exists upload_cadence text
    check (upload_cadence in ('manual_share', 'after_saved_evidence', 'scheduled')),
  add column if not exists consent_terms_version text,
  add column if not exists consent_accepted_at timestamptz,
  add column if not exists source_app_version text,
  add column if not exists source_app_build text,
  add column if not exists client_artifact_sha256 text,
  add column if not exists payload_sha256 text,
  add column if not exists received_at timestamptz not null default now(),
  add column if not exists deleted_at timestamptz;

create index if not exists alpha_tester_profiles_tester_alias_idx
  on public.alpha_tester_profiles (tester_alias);

create index if not exists alpha_evidence_artifacts_user_id_idx
  on public.alpha_evidence_artifacts (user_id);

create index if not exists alpha_evidence_artifacts_payload_sha256_idx
  on public.alpha_evidence_artifacts (payload_sha256);

drop trigger if exists set_alpha_tester_profiles_updated_at on public.alpha_tester_profiles;
create trigger set_alpha_tester_profiles_updated_at
before update on public.alpha_tester_profiles
for each row
execute function public.set_updated_at();

comment on table public.alpha_tester_profiles is
  'Trusted Alpha user/session profile keyed by Supabase Auth user. Thin account layer only.';

comment on column public.alpha_evidence_artifacts.upload_status is
  'Evidence upload lifecycle. Records remain provisional evidence and do not promote Atlas truth.';

comment on column public.alpha_evidence_artifacts.consent_terms_version is
  'Terms/privacy version accepted before this evidence artifact was uploaded.';
