import argparse
import csv
import html
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
DEPS = ROOT / ".transcription_deps"
if str(DEPS) not in sys.path:
    sys.path.insert(0, str(DEPS))

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"
BASE = "https://jurupavalleyca.new.swagit.com"


def get_url(url: str) -> str:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="replace")


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


def seconds_to_hms(seconds: int) -> str:
    seconds = max(0, int(seconds))
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def parse_video_page(video_url: str):
    text = get_url(video_url)
    video_id = video_url.rstrip("/").split("/")[-1]
    meta_dir = ROOT / "video_transcripts" / "metadata"
    meta_dir.mkdir(parents=True, exist_ok=True)
    page_path = meta_dir / f"swagit_{video_id}.html"
    page_path.write_text(text, encoding="utf-8")

    m3u8_match = re.search(r'src:\s*"([^"]+playlist\.m3u8)"', text)
    if not m3u8_match:
        raise RuntimeError(f"No HLS playlist found for {video_url}")
    playlist = html.unescape(m3u8_match.group(1))

    agenda_match = re.search(r'src="(https://swagit-attachments\.granicus\.com/uploads/video/agenda_file/[^"]+)"', text)
    agenda_url = html.unescape(agenda_match.group(1)) if agenda_match else f"{video_url}/agenda"

    rows = []
    for match in re.finditer(
        r'<span class="playerControl"[^>]*data-id="(?P<data_id>\d+)"[^>]*data-ts="(?P<start>\d+)"[^>]*data-end-ts="(?P<end>\d+)"[^>]*data-title="(?P<title>[^"]*)"',
        text,
    ):
        title = html.unescape(match.group("title")).strip()
        title = re.sub(r"\s+", " ", title)
        rows.append(
            {
                "data_id": match.group("data_id"),
                "start": int(match.group("start")),
                "end": int(match.group("end")),
                "title": title,
            }
        )
    return {"video_id": video_id, "page_path": str(page_path), "playlist": playlist, "agenda_url": agenda_url, "items": rows}


def load_cases(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def find_item(items, pattern):
    rx = re.compile(pattern, re.I)
    hits = [item for item in items if rx.search(item["title"])]
    return hits[0] if hits else None


def write_index(case, parsed):
    out = ROOT / "video_transcripts" / "metadata" / f"{case['case_id']}_video_index.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["data_id", "start", "end", "title"])
        writer.writeheader()
        writer.writerows(parsed["items"])
    return out


def clip_case(case, parsed, item, overwrite=False):
    import imageio_ffmpeg

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    audio_dir = ROOT / "video_transcripts" / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    start = max(0, item["start"] - int(case.get("buffer_before_seconds") or 10))
    end = item["end"] + int(case.get("buffer_after_seconds") or 10)
    duration = end - start
    base = f"{case['case_id']}_{slugify(case['case_name'])}_{case['meeting_date']}"
    wav = audio_dir / f"{base}_16k.wav"
    mp3 = audio_dir / f"{base}.mp3"
    if wav.exists() and mp3.exists() and not overwrite:
        return wav, mp3, start, end
    headers = f"Referer: {case['video_url']}\r\nUser-Agent: {USER_AGENT}\r\n"
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-headers",
            headers,
            "-ss",
            str(start),
            "-i",
            parsed["playlist"],
            "-t",
            str(duration),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            str(wav),
        ],
        check=True,
    )
    subprocess.run([ffmpeg, "-y", "-i", str(wav), "-codec:a", "libmp3lame", "-b:a", "64k", str(mp3)], check=True)
    return wav, mp3, start, end


def ts(sec, comma=True):
    ms = int(round((sec - int(sec)) * 1000))
    s = int(sec)
    h = s // 3600
    m = (s % 3600) // 60
    ss = s % 60
    sep = "," if comma else "."
    return f"{h:02d}:{m:02d}:{ss:02d}{sep}{ms:03d}"


def transcribe_case(case, wav, item, clip_start, clip_end, overwrite=False):
    from faster_whisper import WhisperModel

    outdir = ROOT / "video_transcripts" / "transcripts"
    outdir.mkdir(parents=True, exist_ok=True)
    base_name = f"{case['case_id']}_{slugify(case['case_name'])}_{case['meeting_date']}_raw_transcript"
    base = outdir / base_name
    txt = base.with_suffix(".txt")
    srt = base.with_suffix(".srt")
    js = base.with_suffix(".json")
    if txt.exists() and srt.exists() and js.exists() and not overwrite:
        return txt, srt, js

    model_name = "base.en"
    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    started = time.time()
    segments, info = model.transcribe(str(wav), language="en", beam_size=5, vad_filter=True, word_timestamps=False)
    segs = []
    for i, seg in enumerate(segments, start=1):
        segs.append({"id": i, "start": float(seg.start), "end": float(seg.end), "text": seg.text.strip()})
        if i % 50 == 0:
            print(f"{case['case_id']}: {i} segments, {round(time.time() - started, 1)}s")

    header = f"{case['case_name']} - Jurupa Valley City Council - {case['meeting_date']} - {case.get('agenda_item','')}\n"
    note = "Machine transcript generated with faster-whisper base.en. Review against source video before quotation.\n"
    clip_note = f"Clip video time: {seconds_to_hms(clip_start)} to {seconds_to_hms(clip_end)} approx.; transcript timestamps are relative to clip start.\n\n"
    with txt.open("w", encoding="utf-8") as f:
        f.write(header)
        f.write(note)
        f.write(clip_note)
        for rec in segs:
            f.write(f"[{ts(rec['start'], comma=False)} - {ts(rec['end'], comma=False)}] {rec['text']}\n")
    with srt.open("w", encoding="utf-8") as f:
        for rec in segs:
            f.write(f"{rec['id']}\n{ts(rec['start'])} --> {ts(rec['end'])}\n{rec['text']}\n\n")
    meta = {
        "case_id": case["case_id"],
        "case_name": case["case_name"],
        "source_video_url": case["video_url"],
        "agenda_item": item["title"],
        "model": model_name,
        "language": info.language,
        "language_probability": info.language_probability,
        "duration": info.duration,
        "note": "Machine transcript; timestamps are relative to audio clip start.",
    }
    with js.open("w", encoding="utf-8") as f:
        json.dump({"metadata": meta, "segments": segs}, f, indent=2)
    return txt, srt, js


def run(args):
    cases = load_cases(ROOT / "jurupa_transcript_case_list.csv")
    selected = {x.strip() for x in args.case_id.split(",")} if args.case_id else None
    manifest_rows = []
    for case in cases:
        if selected and case["case_id"] not in selected:
            continue
        print(f"== {case['case_id']} {case['case_name']}")
        parsed = parse_video_page(case["video_url"])
        index_path = write_index(case, parsed)
        item = find_item(parsed["items"], case["item_pattern"])
        if not item:
            print(f"  no matching item for pattern: {case['item_pattern']}")
            manifest_rows.append({**case, "status": "item_not_found", "video_id": parsed["video_id"], "video_index_csv": str(index_path)})
            continue
        wav = mp3 = txt = srt = js = ""
        clip_start = max(0, item["start"] - int(case.get("buffer_before_seconds") or 10))
        clip_end = item["end"] + int(case.get("buffer_after_seconds") or 10)
        if args.clip or args.transcribe:
            wav, mp3, clip_start, clip_end = clip_case(case, parsed, item, overwrite=args.overwrite)
        if args.transcribe:
            txt, srt, js = transcribe_case(case, wav, item, clip_start, clip_end, overwrite=args.overwrite)
        manifest_rows.append(
            {
                **case,
                "status": "transcribed" if args.transcribe else "indexed",
                "video_id": parsed["video_id"],
                "agenda_url": parsed["agenda_url"],
                "hls_playlist": parsed["playlist"],
                "matched_item_title": item["title"],
                "item_start_video_ts": seconds_to_hms(item["start"]),
                "item_end_video_ts": seconds_to_hms(item["end"]),
                "clip_start_video_ts": seconds_to_hms(clip_start),
                "clip_end_video_ts": seconds_to_hms(clip_end),
                "video_index_csv": str(index_path.relative_to(ROOT)),
                "audio_mp3": str(mp3.relative_to(ROOT)) if mp3 else "",
                "audio_wav": str(wav.relative_to(ROOT)) if wav else "",
                "raw_transcript_txt": str(txt.relative_to(ROOT)) if txt else "",
                "raw_transcript_srt": str(srt.relative_to(ROOT)) if srt else "",
                "raw_transcript_json": str(js.relative_to(ROOT)) if js else "",
            }
        )
    out = ROOT / "video_transcripts" / "metadata" / "jurupa_video_clip_manifest.csv"
    fields = sorted({str(k) for row in manifest_rows for k in row.keys() if k is not None})
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(manifest_rows)
    print(f"wrote {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-id", default="")
    parser.add_argument("--clip", action="store_true")
    parser.add_argument("--transcribe", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    run(parser.parse_args())
