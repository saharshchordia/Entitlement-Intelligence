# Municipal Entitlement Hardening Playbook

Purpose: give an AI-assisted analyst a repeatable process for turning an initial industrial-zoning market scan into a source-backed entitlement packet for any county, municipality, or corridor.

This playbook is written as executable research instructions. An AI agent should follow it in order, produce the named artifacts, and preserve evidence provenance for every claim.

## Operating Standard

The work product must distinguish:

- Regional review signal, such as DRI, ARC, MPO, state clearinghouse, or regional commission review.
- Local entitlement action, such as planning commission recommendation, council/commission final vote, ordinance, resolution, variance, conditional use, annexation, site plan, LDP, permit, or development agreement.
- Current development status, such as proposed, pending, approved/not started, under construction, delivered, active, inactive, withdrawn, denied, or unknown.

Never treat a DRI completion, market article, broker listing, construction announcement, or legal notice as final local entitlement approval unless a local action record also supports it.

## Required Inputs

Before execution, collect:

- Market name and geography.
- Jurisdictions in scope.
- Target use types, such as industrial, logistics, warehouse, manufacturing, truck terminal, quarry, data center, cold storage, or flex.
- Date window.
- Existing packet folder, if any.
- Whether open-record requests are allowed.
- Output folder name.

Default hierarchy:

`Market > Jurisdiction > Case > Parcel > Action > Evidence > Source`

## Folder Convention

For a market packet, use:

```text
{market-slug}-Industrial-Intelligence/
  {market-slug}_industrial_entitlement_findings.csv
  {market-slug}_gap_matrix.csv
  {market-slug}_industrial_key_players.csv
  {market-slug}_source_audit.csv
  {Market_Title}_Industrial_Entitlement_Landscape.html
  build_workbook.mjs

meeting-intelligence/
  meeting_ledger.csv
  source-packets/{market-slug}/
    {jurisdiction-slug}/
      extracted_text/
      meeting-media/
  transcripts/{market-slug}/
    {jurisdiction-slug}/
      full/
      excerpts/
  refresh-logs/{market-slug}/

outputs/{market-slug}-industrial-intelligence/
  {Market_Title}_Industrial_Entitlement_Landscape.xlsx
  Executive_Summary.png
  Recent_Cases.png
  Gap_Matrix.png
  Key_Players.png
  Source_Audit.png
```

If the market contains multiple municipalities, create one subfolder per jurisdiction under `source-packets/{market-slug}/`.

## Workflow

### Phase 1: Define the Search Universe

1. Create a jurisdiction inventory.
2. For each jurisdiction, identify:
   - governing body
   - planning commission or zoning board
   - agenda/minute portal
   - legal notice publication source
   - zoning code
   - comprehensive plan / FLUM / character area map
   - GIS / parcel source
   - permit or LDP portal
   - public-records boundary
3. Create a search-key list:
   - project name
   - developer/applicant
   - landowner
   - zoning counsel
   - parcel number
   - road name
   - interchange/corridor
   - case number
   - ordinance/resolution number
   - requested zoning district
   - use type
   - DRI or regional-review number

Output: jurisdiction inventory notes and initial source-audit rows.

### Phase 2: Build the Initial Case Universe

Search the following source classes in this order:

1. Official local agendas, minutes, and packets.
2. Official regional-review records.
3. Official zoning maps, FLUM maps, GIS viewers, and parcel records.
4. Official permit, LDP, site-plan, or development-services portals.
5. Legal notices.
6. Developer, contractor, broker, and economic-development pages.
7. Trade press and local reporting.
8. Market reports and listing databases.

For every possible case, capture:

- case title
- jurisdiction
- project location
- applicant/developer
- landowner
- use
- scale
- case numbers
- hearing dates
- record URLs
- source type
- confidence level

Output: preliminary findings CSV.

### Phase 3: Pull Local Action Records

For each case, search the local portal by:

- exact case number
- applicant name
- landowner name
- parcel number
- road name
- ordinance number
- requested zoning district
- use phrase
- meeting month

Download or locally save:

- agendas
- agenda packets
- staff reports
- planning commission minutes
- council/commission minutes
- planning commission audio/video recordings
- city council / county commission audio/video recordings
- meeting livestream archive pages
- meeting transcript files generated from recordings
- case-specific transcript excerpts with timestamps
- ordinances
- resolutions
- conditions
- site plans
- LDP or permit pages, where public
- legal notices

Convert PDFs, HTML records, and meeting media into searchable text files. Keep source files and extracted text together.

For each planning or governing-body meeting tied to a case:

1. Locate the meeting page, agenda item, video/audio archive, and minute file.
2. Download or locally preserve the media file when allowed; otherwise save the stable archive URL and metadata.
3. Transcribe the relevant meeting or agenda-item segment.
4. Capture timestamps for staff presentation, applicant presentation, public comment, official discussion, motion, vote, and condition negotiation.
5. Link transcript excerpts back to the case, action, source, and meeting body.
6. Extract qualitative themes from the conversation, including opposition/support, operations, truck traffic, road access, buffers, hours, lighting, utility capacity, environmental issues, and negotiated conditions.

Do not let a transcript replace the official action record. Use the transcript to explain the discussion, context, objections, and condition formation; use minutes, ordinances, or resolutions to verify the final legal action.

Output: source packets and extracted text.

### Phase 4: Extract Evidence

For each case, extract these fields:

- original zoning
- requested zoning
- final zoning
- FLUM / character area
- annexation status
- parcel IDs
- acreage
- proposed square footage
- use type
- planning staff recommendation
- planning commission action
- final governing-body action
- vote count
- motion language
- staff presentation themes from meeting transcript
- applicant presentation themes from meeting transcript
- public comment themes from meeting transcript
- elected/appointed official discussion themes from meeting transcript
- condition negotiation from meeting transcript
- timestamped transcript citations
- ordinance/resolution number
- conditions
- development agreement terms
- public opposition/support themes
- utility references
- traffic/access references
- environmental constraints
- current development status
- remaining gaps

Preferred evidence phrases:

- `current zoning`
- `existing zoning`
- `requested zoning`
- `future land use`
- `character area`
- `staff recommends`
- `Planning Commission recommends`
- `motion`
- `approved`
- `denied`
- `tabled`
- `withdrawn`
- `conditions`
- `development agreement`
- `land disturbance permit`
- `site plan`
- `certificate of occupancy`
- `public hearing`
- `discussion`
- `concern`
- `traffic`
- `buffer`
- `motion by`
- `seconded by`
- `all in favor`
- `opposed`

Output: case evidence extracts and updated gap matrix.

### Phase 5: Code Status

Use these status values:

- `Final local approval verified`
- `Planning Commission recommendation verified / final action open`
- `Staff report found / hearing action open`
- `DRI complete / local action open`
- `Legal notice only / hearing action open`
- `Approved/not started`
- `Under construction`
- `Delivered`
- `Denied`
- `Withdrawn / inactive`
- `Tabled / no later action found`
- `Public-record open`
- `Open-records request needed`
- `Transcript complete`
- `Transcript unavailable / public media not found`
- `Refresh pending`
- `Refresh complete / no change`
- `Refresh complete / packet updated`

Rules:

- A final governing-body vote with matching case/use/parcel is enough for final local approval.
- Draft ordinance language is not enough unless minutes or signed ordinance show approval.
- Planning Commission recommendation is not final entitlement unless that body has final authority.
- Legal notice is useful for case discovery and hearing scope, but not final action.
- Permit/CO status can remain open if the public portal does not expose it.
- Meeting transcripts support conversation analysis but do not override minutes, ordinances, or signed action records.
- If official minutes conflict with a transcript, preserve both and flag the discrepancy as a gap.

### Phase 6: Gap Matrix

Create one row per case with these columns:

```text
case_id
case_name
jurisdiction
original_zoning_verified
flum_character_verified
local_staff_report_found
planning_commission_action_found
boc_city_final_action_found
ordinance_conditions_found
current_development_status_verified
current_best_status
meeting_recording_status
transcript_status
transcript_themes
evidence_closing_note
last_refresh_date
next_refresh_date
refresh_status
next_gap_to_close
```

Every `No`, `Partial`, or `Open` value must have a matching `next_gap_to_close`.

### Phase 7: Memo Update

The HTML or written memo must include:

- executive investment read
- jurisdiction map
- entitlement framework
- consolidated case table
- player map
- acquisition rules
- evidence method
- open items
- source package

The case table must state:

- month/date
- lead group
- pre-development zoning
- entitlement change
- meeting signal
- current status
- evidence status
- acquisition signal

### Phase 8: Workbook Update

Workbook must include:

- `Executive Summary`
- `Recent Cases`
- `Gap Matrix`
- `Key Players`
- `Source Audit`

Run a formula/error scan for:

```text
#REF!
#DIV/0!
#VALUE!
#NAME?
#N/A
```

Render worksheet previews if the tooling supports it.

### Phase 9: Open-Records Escalation

Use this only after public sources are exhausted.

Trigger an ORR escalation when a case is strategically important and any of these remain unverified:

- signed final ordinance or resolution
- final site plan
- LDP approval
- building permit
- certificate of occupancy
- executed development agreement
- utility capacity letter
- traffic study
- conditions exhibit
- staff report not posted publicly
- audio/video replacement for unusable public media
- missing meeting audio/video for a hearing where minutes are too sparse to understand discussion
- missing transcript or recording segment needed to verify condition negotiation

ORR package should include:

- jurisdiction
- case name
- case numbers
- parcel IDs
- hearing dates
- specific records requested
- reason for request
- source links already reviewed
- desired date range

Do not ask broadly for "all records" unless the narrow search path fails.

### Phase 10: Refresh Cadence

After initial delivery, refresh the market packet on a regular cadence.

Recommended cadence:

- Monthly for active entitlement markets.
- Quarterly for stable markets with no recent cases.
- Weekly during known hearing windows for high-priority jurisdictions or strategic sites.
- Ad hoc when a broker/developer signal, legal notice, DRI filing, or agenda post identifies a new case.

Refresh steps:

1. Re-run source discovery for each jurisdiction portal.
2. Check new agendas, agenda packets, minutes, ordinances, resolutions, legal notices, permits, and meeting media since the last refresh date.
3. Pull down new city council, county commission, planning commission, zoning board, and development authority meeting recordings where relevant.
4. Transcribe new relevant agenda items and attach timestamped excerpts to existing or new cases.
5. Create new case rows for newly discovered matters.
6. Update action rows for newly posted votes, minutes, ordinances, or conditions.
7. Update current-status observations from permits, site plans, COs, construction sources, developer pages, broker pages, and GIS where public.
8. Re-code gaps and close any resolved items.
9. Emit a refresh log that states refresh date, jurisdictions checked, sources added, cases added, cases changed, transcripts added, gaps closed, new ORR candidates, and no-change jurisdictions.

Never overwrite prior evidence during refresh. Add new sources, actions, transcript segments, evidence rows, and status-history rows, then update the reporting rollups.

## AI Execution Prompt Template

Use this prompt when assigning the workflow to an AI agent:

```text
Run a municipal entitlement hardening pass for {market} / {jurisdiction}. Use official public records first, then regional-review records, legal notices, developer/contractor sources, market reports, and listing databases. Pull down relevant planning commission and city/county governing-body meeting recordings, transcribe the portions discussing target cases, and extract timestamped discussion themes. Do not treat DRI completion, legal notices, broker listings, press, or transcript discussion as final local approval unless local minutes, signed ordinances, resolutions, or equivalent official action records verify it.

Create or update:
- findings CSV
- gap matrix CSV
- source audit CSV
- key players CSV
- meeting ledger rows
- meeting recording and transcript inventory
- timestamped transcript excerpts
- HTML memo
- workbook and rendered previews

For every case, code original zoning, FLUM/character area, staff report, planning commission action, final governing-body action, ordinance/conditions, current development status, meeting discussion themes, timestamped transcript citations, evidence closing note, and remaining gap. Stop short of open-record requests unless asked to run the escalation phase; if public records are exhausted, prepare a targeted ORR list.

Preserve downloaded source packets and extracted text under meeting-intelligence/source-packets/{market-slug}/{jurisdiction-slug}/.
Preserve meeting media, transcript files, and transcript excerpts under meeting-intelligence/source-packets/{market-slug}/{jurisdiction-slug}/meeting-media/ and meeting-intelligence/transcripts/{market-slug}/{jurisdiction-slug}/.
For refresh runs, check all source portals since {last-refresh-date}, append new evidence rather than overwriting old evidence, and produce a refresh log.
```

## Quality Gate

Before final delivery, confirm:

- Each case has a unique stable ID.
- Every verified claim points to a source.
- DRI and local entitlement are separated.
- Legal notices are not over-coded as approvals.
- Final action is tied to the correct jurisdiction.
- Conditions are captured.
- Current status is separately coded.
- Relevant meeting recordings are pulled or logged as unavailable.
- Relevant meeting discussions are transcribed with timestamps.
- Residual gaps are explicit.
- Refresh date and next refresh date are recorded.
- Source packets are stored locally.
- Workbook builds without spreadsheet errors.
- Memo language does not overstate certainty.
