-- Entitlement Intelligence relational schema reference.
-- Designed for Postgres/Supabase-style storage. Adapt geometry_ref to PostGIS
-- geometry columns when parcel boundary data becomes available.

create extension if not exists pgcrypto;

create table markets (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  slug text not null unique,
  state text,
  geography_note text,
  research_start_date date,
  research_end_date date,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table jurisdictions (
  id uuid primary key default gen_random_uuid(),
  market_id uuid references markets(id),
  name text not null,
  jurisdiction_type text not null,
  state text,
  county text,
  meeting_portal_url text,
  zoning_code_url text,
  comprehensive_plan_url text,
  gis_url text,
  permit_portal_url text,
  orr_url text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table cases (
  id uuid primary key default gen_random_uuid(),
  market_id uuid not null references markets(id),
  jurisdiction_id uuid references jurisdictions(id),
  case_key text not null unique,
  case_name text not null,
  project_aliases text[],
  use_type text,
  submarket_or_corridor text,
  scale_summary text,
  entitlement_stage text,
  verified_outcome text,
  current_best_status text,
  first_seen_date date,
  last_verified_date date,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table parcels (
  id uuid primary key default gen_random_uuid(),
  parcel_number text not null,
  county text,
  state text,
  acreage numeric,
  owner_name_current text,
  geometry_ref text,
  gis_url text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(parcel_number, county, state)
);

create table case_parcels (
  case_id uuid not null references cases(id),
  parcel_id uuid not null references parcels(id),
  role text,
  acreage_in_case numeric,
  pre_zoning text,
  post_zoning text,
  pre_flum text,
  post_flum text,
  primary key (case_id, parcel_id)
);

create table sources (
  id uuid primary key default gen_random_uuid(),
  source_type text not null,
  publisher text,
  title text,
  url text,
  source_date date,
  retrieved_at timestamptz,
  reliability_tier text,
  local_file_path text,
  hash text,
  created_at timestamptz not null default now()
);

create table source_files (
  id uuid primary key default gen_random_uuid(),
  source_id uuid not null references sources(id),
  local_file_path text not null,
  file_type text,
  mime_type text,
  extracted_text_path text,
  hash text,
  created_at timestamptz not null default now()
);

create table meeting_recordings (
  id uuid primary key default gen_random_uuid(),
  source_id uuid references sources(id),
  jurisdiction_id uuid references jurisdictions(id),
  body text,
  meeting_date date,
  agenda_url text,
  media_url text,
  local_media_path text,
  recording_status text,
  retrieved_at timestamptz,
  duration_seconds integer,
  created_at timestamptz not null default now()
);

create table transcripts (
  id uuid primary key default gen_random_uuid(),
  meeting_recording_id uuid not null references meeting_recordings(id),
  source_file_id uuid references source_files(id),
  transcript_path text,
  transcript_status text not null,
  transcript_method text,
  language text,
  created_at timestamptz not null default now()
);

create table actions (
  id uuid primary key default gen_random_uuid(),
  case_id uuid not null references cases(id),
  jurisdiction_id uuid references jurisdictions(id),
  source_id uuid references sources(id),
  action_type text not null,
  body text,
  action_date date,
  outcome text,
  vote_summary text,
  motion_text text,
  ordinance_number text,
  resolution_number text,
  hearing_url text,
  created_at timestamptz not null default now()
);

create table case_status_history (
  id uuid primary key default gen_random_uuid(),
  case_id uuid not null references cases(id),
  status_type text not null,
  status_value text not null,
  status_date date,
  source_id uuid references sources(id),
  note text,
  created_at timestamptz not null default now()
);

create table conditions (
  id uuid primary key default gen_random_uuid(),
  case_id uuid not null references cases(id),
  action_id uuid references actions(id),
  condition_number text,
  condition_text text not null,
  condition_category text,
  responsible_party text,
  created_at timestamptz not null default now()
);

create table people (
  id uuid primary key default gen_random_uuid(),
  full_name text not null,
  normalized_name text,
  created_at timestamptz not null default now()
);

create table organizations (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  normalized_name text,
  organization_type text,
  created_at timestamptz not null default now()
);

create table person_affiliations (
  id uuid primary key default gen_random_uuid(),
  person_id uuid references people(id),
  organization_id uuid references organizations(id),
  title text,
  start_date date,
  end_date date,
  source_id uuid references sources(id)
);

create table case_participants (
  id uuid primary key default gen_random_uuid(),
  case_id uuid not null references cases(id),
  person_id uuid references people(id),
  organization_id uuid references organizations(id),
  participant_role text not null,
  source_id uuid references sources(id),
  confidence text
);

create table votes (
  id uuid primary key default gen_random_uuid(),
  action_id uuid not null references actions(id),
  person_id uuid references people(id),
  vote text not null,
  role_at_time text
);

create table transcript_segments (
  id uuid primary key default gen_random_uuid(),
  transcript_id uuid not null references transcripts(id),
  case_id uuid references cases(id),
  action_id uuid references actions(id),
  segment_type text,
  speaker_name text,
  speaker_role text,
  start_seconds integer,
  end_seconds integer,
  excerpt text,
  summary text,
  theme_tags text[],
  confidence text,
  created_at timestamptz not null default now()
);

create table evidence (
  id uuid primary key default gen_random_uuid(),
  case_id uuid not null references cases(id),
  source_id uuid not null references sources(id),
  action_id uuid references actions(id),
  transcript_segment_id uuid references transcript_segments(id),
  field_name text not null,
  claim_value text,
  evidence_note text,
  page_number integer,
  locator text,
  confidence text,
  extracted_at timestamptz not null default now()
);

create table regional_reviews (
  id uuid primary key default gen_random_uuid(),
  case_id uuid not null references cases(id),
  review_program text,
  review_number text,
  review_status text,
  review_date date,
  reviewing_body text,
  source_id uuid references sources(id)
);

create table current_status_observations (
  id uuid primary key default gen_random_uuid(),
  case_id uuid not null references cases(id),
  observed_status text not null,
  observed_date date,
  source_id uuid references sources(id),
  note text,
  created_at timestamptz not null default now()
);

create table refresh_runs (
  id uuid primary key default gen_random_uuid(),
  market_id uuid not null references markets(id),
  started_at timestamptz not null default now(),
  completed_at timestamptz,
  run_type text,
  cadence text,
  status text not null,
  summary text,
  next_scheduled_at timestamptz
);

create table refresh_run_items (
  id uuid primary key default gen_random_uuid(),
  refresh_run_id uuid not null references refresh_runs(id),
  jurisdiction_id uuid references jurisdictions(id),
  checked_from_date date,
  checked_through_date date,
  result text,
  sources_added integer not null default 0,
  cases_added integer not null default 0,
  cases_changed integer not null default 0,
  transcripts_added integer not null default 0,
  gaps_closed integer not null default 0,
  orr_candidates_added integer not null default 0,
  note text
);

create table gaps (
  id uuid primary key default gen_random_uuid(),
  case_id uuid not null references cases(id),
  gap_type text not null,
  gap_description text not null,
  priority integer,
  status text not null,
  next_action text,
  orr_required boolean not null default false,
  created_at timestamptz not null default now(),
  resolved_at timestamptz
);

create index idx_cases_market on cases(market_id);
create index idx_cases_jurisdiction on cases(jurisdiction_id);
create index idx_actions_case_date on actions(case_id, action_date);
create index idx_case_status_history_case on case_status_history(case_id, status_type, status_date);
create index idx_evidence_case_field on evidence(case_id, field_name);
create index idx_gaps_case_status on gaps(case_id, status);
create index idx_meeting_recordings_jurisdiction_date on meeting_recordings(jurisdiction_id, meeting_date);
create index idx_refresh_run_items_run on refresh_run_items(refresh_run_id);
create index idx_refresh_runs_market_started on refresh_runs(market_id, started_at);
create index idx_source_files_source on source_files(source_id);
create index idx_sources_url on sources(url);
create index idx_transcript_segments_case on transcript_segments(case_id, segment_type);
create index idx_transcripts_recording on transcripts(meeting_recording_id);
