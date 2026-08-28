# Entitlement Intelligence Data Model

Purpose: define a sustainable database-oriented model for a growing zoning and industrial-entitlement portfolio. The model supports countywide markets, municipalities, projects, parcels, actions, sources, meeting recordings, transcripts, evidence extracts, people, organizations, refresh runs, and gap tracking.

Recommended top-level hierarchy:

`Market > Jurisdiction > Case > Parcel / Action / Source / Evidence`

This keeps the market thesis readable while preserving enough granularity to support parcel-level underwriting and future database queries.

## Core Design Principles

- Store facts once, then connect them through relationship tables.
- Treat a case as the entitlement workstream, not as a parcel and not as a development project.
- Treat a parcel as a spatial/legal object that may appear in multiple cases over time.
- Treat a source as a document or webpage.
- Treat meeting recordings and transcripts as source-backed records that explain hearing discussion without replacing final action records.
- Treat transcript segments as timestamped, citeable evidence units.
- Treat evidence as a specific extracted claim from a source.
- Treat actions as official process events, such as Planning Commission recommendation or City Council final approval.
- Treat people and organizations as participants with roles in cases/actions.
- Treat gaps as first-class records so uncertainty can be managed, not buried in prose.

## Entity Relationship Diagram

```mermaid
erDiagram
  MARKET ||--o{ JURISDICTION : contains
  MARKET ||--o{ CASE : groups
  JURISDICTION ||--o{ CASE : controls
  CASE ||--o{ CASE_PARCEL : includes
  PARCEL ||--o{ CASE_PARCEL : appears_in
  CASE ||--o{ ACTION : has
  ACTION ||--o{ VOTE : records
  ACTION ||--o{ CONDITION : imposes
  CASE ||--o{ CASE_STATUS_HISTORY : tracks
  CASE ||--o{ GAP : has
  CASE ||--o{ EVIDENCE : supports
  SOURCE ||--o{ EVIDENCE : contains
  SOURCE ||--o{ SOURCE_FILE : stored_as
  SOURCE ||--o{ MEETING_RECORDING : preserves
  MEETING_RECORDING ||--o{ TRANSCRIPT : transcribed_as
  TRANSCRIPT ||--o{ TRANSCRIPT_SEGMENT : divided_into
  CASE ||--o{ TRANSCRIPT_SEGMENT : discussed_in
  ACTION ||--o{ TRANSCRIPT_SEGMENT : contextualized_by
  TRANSCRIPT_SEGMENT ||--o{ EVIDENCE : supports
  CASE ||--o{ CASE_PARTICIPANT : involves
  PERSON ||--o{ CASE_PARTICIPANT : participates
  ORGANIZATION ||--o{ CASE_PARTICIPANT : participates
  ORGANIZATION ||--o{ PERSON_AFFILIATION : employs
  PERSON ||--o{ PERSON_AFFILIATION : affiliated_with
  CASE ||--o{ REGIONAL_REVIEW : may_trigger
  CASE ||--o{ CURRENT_STATUS_OBSERVATION : observed_as
  MARKET ||--o{ REFRESH_RUN : refreshed_by
  JURISDICTION ||--o{ REFRESH_RUN_ITEM : checked_in
  REFRESH_RUN ||--o{ REFRESH_RUN_ITEM : includes

  MARKET {
    uuid id PK
    text name
    text slug
    text geography_note
    date research_start_date
    date research_end_date
  }

  JURISDICTION {
    uuid id PK
    uuid market_id FK
    text name
    text type
    text state
    text meeting_portal_url
    text zoning_code_url
    text gis_url
  }

  CASE {
    uuid id PK
    uuid market_id FK
    uuid jurisdiction_id FK
    text case_key
    text case_name
    text use_type
    text entitlement_stage
    text current_best_status
    date first_seen_date
    date last_verified_date
  }

  PARCEL {
    uuid id PK
    text parcel_number
    text county
    text state
    numeric acreage
    text geometry_ref
  }

  ACTION {
    uuid id PK
    uuid case_id FK
    text action_type
    text body
    date action_date
    text outcome
    text motion_text
    text ordinance_number
  }

  SOURCE {
    uuid id PK
    text source_type
    text publisher
    text title
    text url
    date source_date
    text reliability_tier
  }

  EVIDENCE {
    uuid id PK
    uuid case_id FK
    uuid source_id FK
    uuid transcript_segment_id FK
    text field_name
    text claim_value
    text evidence_note
    integer page_number
    text locator
    text confidence
  }

  SOURCE_FILE {
    uuid id PK
    uuid source_id FK
    text local_file_path
    text file_type
    text extracted_text_path
    text hash
  }

  MEETING_RECORDING {
    uuid id PK
    uuid source_id FK
    uuid jurisdiction_id FK
    text body
    date meeting_date
    text media_url
    text local_media_path
    text recording_status
  }

  TRANSCRIPT {
    uuid id PK
    uuid meeting_recording_id FK
    uuid source_file_id FK
    text transcript_path
    text transcript_status
    text transcript_method
  }

  TRANSCRIPT_SEGMENT {
    uuid id PK
    uuid transcript_id FK
    uuid case_id FK
    uuid action_id FK
    text segment_type
    integer start_seconds
    integer end_seconds
    text summary
  }

  CASE_STATUS_HISTORY {
    uuid id PK
    uuid case_id FK
    text status_type
    text status_value
    date status_date
    uuid source_id FK
  }

  CASE_PARCEL {
    uuid case_id FK
    uuid parcel_id FK
    text role
    numeric acreage_in_case
    text pre_zoning
    text post_zoning
  }

  VOTE {
    uuid id PK
    uuid action_id FK
    uuid person_id FK
    text vote
    text role_at_time
  }

  CONDITION {
    uuid id PK
    uuid case_id FK
    uuid action_id FK
    text condition_number
    text condition_text
    text condition_category
  }

  GAP {
    uuid id PK
    uuid case_id FK
    text gap_type
    text status
    boolean orr_required
  }

  PERSON {
    uuid id PK
    text full_name
    text normalized_name
  }

  ORGANIZATION {
    uuid id PK
    text name
    text normalized_name
    text organization_type
  }

  CASE_PARTICIPANT {
    uuid id PK
    uuid case_id FK
    uuid person_id FK
    uuid organization_id FK
    text participant_role
  }

  PERSON_AFFILIATION {
    uuid id PK
    uuid person_id FK
    uuid organization_id FK
    text title
  }

  REGIONAL_REVIEW {
    uuid id PK
    uuid case_id FK
    text review_program
    text review_number
    text review_status
  }

  CURRENT_STATUS_OBSERVATION {
    uuid id PK
    uuid case_id FK
    text observed_status
    date observed_date
    uuid source_id FK
  }

  REFRESH_RUN {
    uuid id PK
    uuid market_id FK
    timestamptz started_at
    timestamptz completed_at
    text run_type
    text status
  }

  REFRESH_RUN_ITEM {
    uuid id PK
    uuid refresh_run_id FK
    uuid jurisdiction_id FK
    text result
    integer sources_added
    integer cases_added
    integer transcripts_added
  }
```

## Workflow / Data Lineage Diagram

```mermaid
flowchart TD
  A[Define Market and Jurisdictions] --> B[Discover Source Portals]
  B --> C[Build Initial Case Universe]
  C --> D[Download Source Packets]
  D --> E[Pull Meeting Media]
  E --> F[Transcribe Relevant Agenda Items]
  F --> G[Extract Searchable Text]
  G --> H[Extract Evidence Claims and Transcript Themes]
  H --> I[Create Cases, Actions, Parcels, Sources, Transcripts]
  I --> J[Code Gap Matrix]
  J --> K[Update Memo and Workbook]
  J --> L{Gaps Material?}
  L -->|No| M[Publish Market Packet]
  L -->|Yes| N[Prepare Targeted ORR List]
  N --> O[ORR Escalation Phase]
  O --> D
  M --> P[Scheduled Refresh Run]
  P --> B
```

## Evidence Confidence Ladder

```mermaid
flowchart LR
  A[Market / Broker Signal] --> B[Legal Notice]
  B --> C[Regional Review / DRI]
  C --> D[Staff Report]
  D --> E[Planning Commission Recommendation]
  E --> F[Final Governing Body Minutes]
  F --> G[Meeting Transcript with Timestamps]
  G --> H[Signed Ordinance / Resolution]
  H --> I[Permit / LDP / Site Plan / CO]
```

Higher on the ladder does not erase lower evidence. It changes the claim type that can be made.

For example:

- Broker listing can support `market signal`.
- Legal notice can support `hearing noticed`.
- DRI can support `regional review complete`.
- Transcript segments can support `discussion theme`, `public concern`, `applicant representation`, or `condition negotiation`.
- Council minutes can support `final local approval verified`.
- Permit/CO can support `construction/occupancy status`.

## Recommended Tables

### markets

One row per investment/research geography.

Key fields:

- `id`
- `name`
- `slug`
- `state`
- `geography_note`
- `research_start_date`
- `research_end_date`
- `created_at`
- `updated_at`

### jurisdictions

One row per city, county, town, regional body, or authority.

Key fields:

- `id`
- `market_id`
- `name`
- `jurisdiction_type`
- `state`
- `county`
- `meeting_portal_url`
- `zoning_code_url`
- `comprehensive_plan_url`
- `gis_url`
- `permit_portal_url`
- `orr_url`

### cases

One row per entitlement/development workstream.

Key fields:

- `id`
- `market_id`
- `jurisdiction_id`
- `case_key`
- `case_name`
- `project_aliases`
- `use_type`
- `submarket_or_corridor`
- `scale_summary`
- `entitlement_stage`
- `verified_outcome`
- `current_best_status`
- `first_seen_date`
- `last_verified_date`

### parcels

One row per parcel identifier.

Key fields:

- `id`
- `parcel_number`
- `county`
- `state`
- `acreage`
- `owner_name_current`
- `geometry_ref`
- `gis_url`

### case_parcels

Many-to-many join between cases and parcels.

Key fields:

- `case_id`
- `parcel_id`
- `role`
- `acreage_in_case`
- `pre_zoning`
- `post_zoning`
- `pre_flum`
- `post_flum`

### actions

One row per public process event.

Key fields:

- `id`
- `case_id`
- `jurisdiction_id`
- `action_type`
- `body`
- `action_date`
- `outcome`
- `vote_summary`
- `motion_text`
- `ordinance_number`
- `resolution_number`
- `hearing_url`

Action types:

- `legal_notice`
- `staff_report`
- `planning_commission`
- `city_council`
- `county_commission`
- `annexation`
- `rezoning`
- `conditional_use`
- `variance`
- `site_plan`
- `ldp`
- `building_permit`
- `certificate_of_occupancy`
- `development_agreement`
- `withdrawal`
- `denial`

### votes

Optional detail table for votes.

Key fields:

- `id`
- `action_id`
- `person_id`
- `vote`
- `role_at_time`

### conditions

One row per approval condition.

Key fields:

- `id`
- `case_id`
- `action_id`
- `condition_number`
- `condition_text`
- `condition_category`
- `responsible_party`

Condition categories:

- `traffic`
- `access`
- `buffer`
- `landscape`
- `stormwater`
- `environmental`
- `utility`
- `site_plan`
- `operations`
- `hours`
- `lighting`
- `noise`
- `plat`
- `development_agreement`

### sources

One row per unique document/page/source.

Key fields:

- `id`
- `source_type`
- `publisher`
- `title`
- `url`
- `source_date`
- `retrieved_at`
- `reliability_tier`
- `local_file_path`
- `hash`

Source types:

- `agenda`
- `agenda_packet`
- `staff_report`
- `minutes`
- `ordinance`
- `resolution`
- `legal_notice`
- `meeting_archive_page`
- `meeting_audio`
- `meeting_video`
- `transcript`
- `regional_review`
- `permit_record`
- `gis_record`
- `developer_page`
- `broker_listing`
- `trade_press`

### source_files

One row per locally stored source artifact or derivative.

Use this when one source has multiple file representations, such as a downloaded PDF, rendered page images, extracted text, OCR output, or archived HTML.

Key fields:

- `id`
- `source_id`
- `local_file_path`
- `file_type`
- `mime_type`
- `extracted_text_path`
- `hash`
- `created_at`

### meeting_recordings

One row per public meeting audio/video recording or archive entry.

Use this table for planning commission, city council, county commission, zoning board, development authority, or other hearing bodies where case discussion may appear.

Key fields:

- `id`
- `source_id`
- `jurisdiction_id`
- `body`
- `meeting_date`
- `agenda_url`
- `media_url`
- `local_media_path`
- `recording_status`
- `retrieved_at`
- `duration_seconds`

Recording statuses:

- `downloaded`
- `url_preserved`
- `stream_only`
- `unavailable`
- `broken_link`
- `orr_needed`

### transcripts

One row per transcript generated from or attached to a meeting recording.

Key fields:

- `id`
- `meeting_recording_id`
- `source_file_id`
- `transcript_path`
- `transcript_status`
- `transcript_method`
- `language`
- `created_at`

Transcript statuses:

- `complete`
- `partial_case_segments_only`
- `failed_audio_quality`
- `media_unavailable`
- `needs_review`

### transcript_segments

One row per timestamped discussion segment that matters to a case.

Use this as the bridge between raw transcript text and entitlement intelligence. A single meeting transcript may generate many case-linked segments.

Key fields:

- `id`
- `transcript_id`
- `case_id`
- `action_id`
- `segment_type`
- `speaker_name`
- `speaker_role`
- `start_seconds`
- `end_seconds`
- `excerpt`
- `summary`
- `theme_tags`
- `confidence`

Segment types:

- `staff_presentation`
- `applicant_presentation`
- `public_comment_support`
- `public_comment_opposition`
- `official_discussion`
- `condition_negotiation`
- `motion`
- `vote`

Reliability tiers:

- `official_final_action`
- `official_staff_packet`
- `official_regional_review`
- `official_map_or_gis`
- `legal_notice`
- `developer_or_contractor`
- `trade_press`
- `market_listing`
- `secondary_reporting`

### evidence

One row per extracted claim.

Key fields:

- `id`
- `case_id`
- `source_id`
- `action_id`
- `transcript_segment_id`
- `field_name`
- `claim_value`
- `evidence_note`
- `page_number`
- `locator`
- `confidence`
- `extracted_at`

Field examples:

- `original_zoning`
- `requested_zoning`
- `final_zoning`
- `flum`
- `character_area`
- `acreage`
- `square_feet`
- `applicant`
- `landowner`
- `staff_recommendation`
- `planning_commission_action`
- `final_action`
- `conditions`
- `current_status`

### case_status_history

One row per coded status change or verification state for a case.

Use this for durable status history instead of overwriting the case every time a new source is found. The `cases.current_best_status` field should hold the latest rollup for reporting, while this table preserves the underlying sequence.

Key fields:

- `id`
- `case_id`
- `status_type`
- `status_value`
- `status_date`
- `source_id`
- `note`
- `created_at`

Status types:

- `entitlement`
- `development`
- `gap_resolution`
- `research_quality`

### refresh_runs

One row per scheduled or ad hoc refresh of a market packet.

Key fields:

- `id`
- `market_id`
- `started_at`
- `completed_at`
- `run_type`
- `cadence`
- `status`
- `summary`
- `next_scheduled_at`

Run types:

- `scheduled_monthly`
- `scheduled_quarterly`
- `weekly_hearing_window`
- `ad_hoc_signal`
- `orr_follow_up`

### refresh_run_items

One row per jurisdiction checked during a refresh run.

Key fields:

- `id`
- `refresh_run_id`
- `jurisdiction_id`
- `checked_from_date`
- `checked_through_date`
- `result`
- `sources_added`
- `cases_added`
- `cases_changed`
- `transcripts_added`
- `gaps_closed`
- `orr_candidates_added`
- `note`

### participants

Use `people`, `organizations`, and `case_participants` rather than storing names only in case rows.

Case participant fields:

- `case_id`
- `person_id`
- `organization_id`
- `participant_role`
- `source_id`
- `confidence`

Roles:

- `applicant`
- `developer`
- `landowner`
- `zoning_counsel`
- `civil_engineer`
- `traffic_engineer`
- `staff_presenter`
- `planning_commissioner`
- `council_member`
- `county_commissioner`
- `public_speaker_support`
- `public_speaker_opposition`
- `broker`
- `contractor`
- `utility_provider`

### gaps

One row per open verification need.

Key fields:

- `id`
- `case_id`
- `gap_type`
- `gap_description`
- `priority`
- `status`
- `next_action`
- `orr_required`
- `created_at`
- `resolved_at`

Gap types:

- `original_zoning`
- `flum_character`
- `staff_report`
- `planning_commission_action`
- `final_action`
- `conditions`
- `site_plan`
- `permit`
- `certificate_of_occupancy`
- `development_agreement`
- `utility`
- `traffic`
- `current_status`
- `source_quality`

## Stable Case ID Convention

Use:

```text
{MARKET}-{YEAR}-{JURISDICTION}-{SHORTNAME}
```

Examples:

- `JC-2024-COMMERCE-TAYLOR`
- `FB-2025-4627`
- `JC-2026-ORCHID`

IDs should remain stable even if project names change.

## Query Examples The Model Should Support

- Show all final local approvals for M-1 or LI industrial uses in a market.
- Show all DRI-complete cases without final local action.
- Show all cases involving truck terminals, truck stops, or diesel fueling.
- Show all conditions involving road improvements or buffers.
- Show all projects where original zoning was agricultural and final zoning was industrial.
- Show all active gaps requiring ORR escalation.
- Show all cases where a specific developer, counsel, or landowner appears.
- Show all approvals in a given municipality during a date window.

## Migration Path From Current CSVs

Current CSV to database mapping:

- findings CSV -> `cases`, `case_status_history`, selected `evidence`
- gap matrix CSV -> `gaps`
- key players CSV -> `people`, `organizations`, `case_participants`
- source audit CSV -> `sources`
- meeting ledger CSV -> `actions`, `sources`, `source_files`, `meeting_recordings`
- extracted text files -> `source_files`, optionally searchable document store
- transcript files -> `transcripts`, `transcript_segments`, selected `evidence`
- refresh logs -> `refresh_runs`, `refresh_run_items`, `case_status_history`

Do not throw away CSVs immediately. Keep them as export/reporting artifacts generated from the database once the database exists.
