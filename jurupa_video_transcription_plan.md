# Jurupa Valley Council Video Transcription Plan

## Goal

Use City Council meeting videos to add decision-making context to the Jurupa IOS / Trucking / M-H eligibility memo.

The transcript pass should answer:

1. What did staff say was required for approval?
2. What did applicants argue?
3. What did Council members say they were worried about?
4. What public opposition or support appeared?
5. Which capital/site-readiness issues drove the decision?
6. Did Council treat M-H + CUP as sufficient, or only as a threshold condition?

## Source Platform

Jurupa Valley uses Swagit/Granicus for meeting videos:

- Archive: `https://jurupavalleyca.new.swagit.com/views/96`
- Known FC Pallets video: `https://jurupavalleyca.new.swagit.com/videos/350142`
- Known I-15 denial video: `https://jurupavalleyca.new.swagit.com/videos/375852`

The FC Pallets video page exposes:

- HLS playlist URL: `https://archive-stream.granicus.com/OnDemand/_definst_/mp4:swagitVideo/jurupavalleyca/923097c4-61be-42c0-b126-e9aae66492eb.mp4/playlist.m3u8`
- Agenda PDF URL: `https://swagit-attachments.granicus.com/uploads/video/agenda_file/350142/7-17_JurupaCC.pdf`
- Video index item 15.G: FC Pallets / MA21108.

The page did not expose a ready-made transcript in HTML. The workflow should therefore use media extraction plus speech-to-text, unless a hidden caption endpoint is later found.

## Priority Order

### Tier 1: Most Relevant To IOS / Trucking Feasibility

1. July 17, 2025 City Council - FC Pallets / MA21108.
2. February 19, 2026 City Council - I-15 RV/self-storage denial / MA20269.
3. February 5, 2026 City Council - I-15 RV/self-storage initial approval package / MA20269.
4. August 6, 2026 City Council - Bus dispatch / MA25123 / ZCA25006.
5. August 6, 2026 City Council - Citywide Freight Analysis Plan and Mobility Element Update.

### Tier 2: Policy Regime-Break Context

6. December 2, 2021 City Council - ZCA21007 Truck Intensive Use Ordinance final action.
7. October 7, 2021 Joint City Council / Planning Commission study session - truck-intensive use policy.
8. January 21, 2021 City Council - truck-intensive moratorium initiation.

### Tier 3: Large Logistics Approval Context

9. January 18, 2024 City Council - Rubidoux Commerce Park final action.
10. July 15, 2021 City Council - Aqua Mansa Road Development approval.
11. September 21, 2023 City Council - The District at Jurupa Valley Specific Plan.
12. September 5, 2024 City Council - Rio Vista Specific Plan.

## Extraction Workflow

### Step 1: Resolve Video URLs

For each target date:

1. Search the Swagit archive page for the date and body.
2. Open the video page.
3. Save:
   - video URL
   - agenda URL
   - packet URL if available
   - video duration
   - relevant agenda item number
   - video index item ID if present
   - HLS `.m3u8` playlist URL

Output:

- Update `jurupa_video_transcription_targets.csv`.

### Step 2: Map Agenda Item To Timestamp

For each video page:

1. Parse the video index headings.
2. Identify the exact item:
   - FC Pallets: `15.G`
   - I-15 RV/self-storage: `MA20269`
   - Bus dispatch: `MA25123 / ZCA25006`
   - Truck ordinance: `ZCA21007`
3. Extract chapter start time if available through Swagit data attributes.
4. If timestamps are not in the HTML, use the video index in the browser and record the playback start time manually.
5. Clip from item start to next agenda item start, plus 60 seconds before/after.

Output:

- `jurupa_video_clip_manifest.csv`

Suggested fields:

- `target_id`
- `meeting_date`
- `video_url`
- `agenda_item`
- `item_start`
- `item_end`
- `clip_file`
- `method`
- `confidence`

### Step 3: Download Audio

Preferred command pattern:

```powershell
ffmpeg -y -i "<m3u8_url>" -vn -ac 1 -ar 16000 "<output.wav>"
```

If clipping is available:

```powershell
ffmpeg -y -ss HH:MM:SS -to HH:MM:SS -i "<m3u8_url>" -vn -ac 1 -ar 16000 "<clip.wav>"
```

If ffmpeg is not installed:

1. Use the Swagit download endpoint if it provides an MP4.
2. Use browser download manually.
3. Use a bundled media library only if it can preserve audio quality and timestamps.

Output folder:

- `video_transcripts/audio/`

### Step 4: Transcribe

Options:

1. Local Whisper/faster-whisper if installed.
2. OpenAI speech-to-text API if credentials are available.
3. Manual browser captions only if captions are available.

Target output format:

- `.txt` readable transcript
- `.srt` or `.vtt` timestamped transcript where possible
- `.json` segment transcript with start/end times

Output folder:

- `video_transcripts/transcripts/`

### Step 5: Code The Transcript

For each transcript, create a coded summary row:

- `target_id`
- `speaker`
- `speaker_role`
- `timestamp`
- `topic`
- `quote_or_paraphrase`
- `decision_factor`
- `capital_implication`
- `entitlement_implication`
- `support_or_opposition`
- `confidence`
- `source_video_url`

Decision-factor categories:

- zoning eligibility
- M-H / CUP threshold
- fire access / fire safety
- right-of-way truck parking
- traffic / circulation
- truck routes
- paving / dust / stormwater
- screening / buffering
- code violations / unpermitted use
- CEQA / environmental
- compatibility with residential/sensitive receptors
- economic development / jobs
- public opposition
- applicant credibility / operating history
- conditions of approval
- legal risk

Output:

- `jurupa_video_decision_context.csv`

### Step 6: Update The Memo

Add a new section to `Jurupa_Valley_City_Council_IOS_Trucking_Memo.html`:

`Council Deliberation Context`

Include:

- short narrative findings
- most important paraphrased comments
- limited short direct quotes where useful
- timestamped video citations
- decision-factor table

Do not overquote transcripts. Use short excerpts only, with timestamps.

## First Transcript To Run

Start with FC Pallets because:

- it is closest to IOS/truck-storage
- video URL is known
- agenda index item is known: 15.G
- applicant is identified: Francisco Cortez
- entitlement package is exactly the M-H/CUP path we need to understand
- reported outcome is denial

Questions to answer from FC Pallets transcript:

1. What findings could Council not make?
2. How much of the issue was zoning versus operations?
3. What site work or compliance work was described?
4. Did fire access/safety dominate?
5. Did right-of-way truck/trailer parking dominate?
6. Did Council indicate M-H + CUP is enough in principle but not for this applicant/site?
7. Did the applicant offer capital improvements or conditions?
8. Was denial framed as permanent, or could a cleaner re-application work?

## Expected Deliverables After Transcription

1. `jurupa_video_transcription_targets.csv` - target list.
2. `jurupa_video_clip_manifest.csv` - clip/timestamp list.
3. `jurupa_video_decision_context.csv` - coded transcript evidence.
4. Transcript files under `video_transcripts/transcripts/`.
5. Updated standalone memo with Council deliberation context.

## Practical Caveats

- Meeting videos are long. Do not transcribe whole meetings unless item timestamps cannot be isolated.
- If a target item was on consent and not discussed, mark it as `no substantive discussion`.
- If the item was continued, capture why and who requested the continuation.
- The goal is not a perfect legal transcript. The goal is underwriting-grade decision context tied to timestamps.
