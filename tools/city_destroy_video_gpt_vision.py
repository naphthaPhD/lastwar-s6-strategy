#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import csv
import json
import mimetypes
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DEFAULT_OUT_DIR = ROOT / "tmp" / "city_destroy_gpt_vision"
DEFAULT_MODEL = os.environ.get("OPENAI_VISION_MODEL", os.environ.get("OPENAI_OCR_MODEL", "gpt-5.4-mini"))
KNOWN_SERVERS = ["#534", "#509", "#503", "#480", "#440", "#511", "#523", "#476"]
DEFAULT_SPREADSHEET = "1oK2tebQRs9RaSsrM-Oo9lynAjbt4loV82GjS8a3dPrQ"
DEFAULT_CREDENTIALS = Path("/Users/mba2025/.config/gptcodex/credentials-sub.json")


PROMPT = """You are reading Last War Season 6 in-game destruction history screenshots.

The screen is a scrolling list of city destruction history across eight server areas.
Each visible event usually has:
- timestamp, for example 2026-6-17 20:21:01
- attacker server and alliance, for example #476[476K]
- defender/target server and sometimes defender alliance, for example #534[5g3]
- target city level and coordinate, for example LV.1都市 #534(849,249)
- destruction reward text.

Extract every visible city destruction event. Do not invent hidden rows.
If an event is split across multiple visible lines, join the lines.
If characters are unclear, keep the best visible reading and add a note in uncertain.
Use the coordinate inside #server(x,y) as the target, not the attacker.

Color rule from the user:
- red text means the city was destroyed by an enemy
- blue text means the city was destroyed by an ally
If the text color is not visually clear, use "unknown".

Return JSON only:
{
  "events": [
    {
      "source_frame": "frame filename if shown in the prompt",
      "event_time": "YYYY-M-D HH:MM:SS",
      "actor_server": "#476",
      "actor_alliance": "476K",
      "target_server": "#534",
      "defender_alliance": "5g3",
      "level": "1",
      "target_type": "都市",
      "x": 849,
      "y": 249,
      "text_color": "red|blue|unknown",
      "destroyed_by": "enemy|ally|unknown",
      "raw_text": "",
      "uncertain": []
    }
  ],
  "screen_text": "",
  "notes": ""
}
"""


@dataclass(frozen=True)
class FrameRecord:
    frame: str
    path: str
    range_start_sec: float
    timestamp_sec: float
    sequence: int


def eprint(message: str) -> None:
    print(message, file=sys.stderr)


def parse_ranges(values: list[str]) -> list[tuple[float, float]]:
    if not values:
        return [(0.0, -1.0)]
    ranges: list[tuple[float, float]] = []
    for value in values:
        for part in value.split(","):
            part = part.strip()
            if not part:
                continue
            if "-" not in part:
                raise ValueError(f"range must be START-END seconds: {part}")
            start_text, end_text = part.split("-", 1)
            start = float(start_text)
            end = float(end_text)
            if start < 0 or end <= start:
                raise ValueError(f"invalid range: {part}")
            ranges.append((start, end))
    return ranges


def merge_ranges(ranges: list[tuple[float, float]], merge_gap: float) -> list[tuple[float, float]]:
    if not ranges:
        return []
    merged: list[tuple[float, float]] = []
    for start, end in sorted(ranges):
        if not merged or start > merged[-1][1] + merge_gap:
            merged.append((start, end))
        else:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
    return merged


def suggest_ranges(args: argparse.Namespace) -> int:
    raw_dir = args.raw_dir
    if not raw_dir.exists():
        eprint(f"raw OCR directory not found: {raw_dir}")
        return 1
    servers = [normalize_server(value) for value in args.server]
    servers = [server for server in servers if server]
    patterns = [re.compile(re.escape(server).replace("\\#", r"[#＃]")) for server in servers]
    hits: list[dict[str, Any]] = []
    ranges: list[tuple[float, float]] = []
    for path in sorted(raw_dir.glob("frame_*.txt")):
        match = re.search(r"(\d+)$", path.stem)
        if not match:
            continue
        frame_number = int(match.group(1))
        timestamp = args.frame_zero_sec + (frame_number - args.first_frame_number) / args.source_fps
        text = path.read_text(encoding="utf-8", errors="ignore")
        if patterns:
            found = any(pattern.search(text) for pattern in patterns)
        else:
            found = any(server in text or server.replace("#", "＃") in text for server in KNOWN_SERVERS)
        if not found:
            continue
        start = max(0.0, timestamp - args.pad)
        end = timestamp + args.pad
        ranges.append((start, end))
        hits.append({"frame": path.name, "timestamp_sec": round(timestamp, 3), "path": str(path)})
    merged = merge_ranges(ranges, args.merge_gap)
    result = {
        "raw_dir": str(raw_dir),
        "servers": servers or KNOWN_SERVERS,
        "hits": len(hits),
        "ranges": [[round(start, 3), round(end, 3)] for start, end in merged],
        "prepare_args": ",".join(f"{start:.3f}-{end:.3f}" for start, end in merged),
    }
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps({**result, "hit_frames": hits}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def ensure_ffmpeg(binary: str) -> None:
    try:
        subprocess.run([binary, "-version"], capture_output=True, text=True, check=True, timeout=10)
    except Exception as exc:
        raise RuntimeError(f"ffmpeg is not available: {binary}") from exc


def ffprobe_duration(video: Path, ffprobe: str = "ffprobe") -> float | None:
    try:
        proc = subprocess.run(
            [
                ffprobe,
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(video),
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=20,
        )
        return float(proc.stdout.strip())
    except Exception:
        return None


def crop_filter(crop_rel: str | None) -> str:
    if not crop_rel:
        return ""
    parts = [float(p.strip()) for p in crop_rel.split(",")]
    if len(parts) != 4:
        raise ValueError("--crop-rel must be x,y,width,height")
    x, y, w, h = parts
    if not all(0 <= p <= 1 for p in parts) or w <= 0 or h <= 0 or x + w > 1 or y + h > 1:
        raise ValueError("--crop-rel values must be fractions within the image")
    return f"crop=iw*{w}:ih*{h}:iw*{x}:ih*{y}"


def prepare_frames(args: argparse.Namespace) -> int:
    ensure_ffmpeg(args.ffmpeg)
    video = args.video.resolve()
    if not video.exists():
        eprint(f"video not found: {video}")
        return 1

    ranges = parse_ranges(args.range)
    if ranges == [(0.0, -1.0)]:
        duration = ffprobe_duration(video, args.ffprobe)
        if duration is None:
            eprint("Could not determine video duration; pass --range START-END.")
            return 1
        ranges = [(0.0, duration)]

    frames_dir = args.out_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    metadata: list[FrameRecord] = []
    global_sequence = 1
    filters = []
    crop = crop_filter(args.crop_rel)
    if crop:
        filters.append(crop)
    filters.append(f"fps={args.fps}")
    if args.scale_width:
        filters.append(f"scale={args.scale_width}:-1")
    vf = ",".join(filters)

    for range_index, (start, end) in enumerate(ranges, start=1):
        pattern = frames_dir / f"range{range_index:02d}_frame_%06d.png"
        cmd = [
            args.ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            f"{start:.3f}",
            "-to",
            f"{end:.3f}",
            "-i",
            str(video),
            "-vf",
            vf,
            "-vsync",
            "0",
            str(pattern),
        ]
        eprint(" ".join(cmd))
        subprocess.run(cmd, check=True)
        range_frames = sorted(frames_dir.glob(f"range{range_index:02d}_frame_*.png"))
        for local_index, path in enumerate(range_frames, start=1):
            timestamp = start + (local_index - 1) / args.fps
            metadata.append(
                FrameRecord(
                    frame=path.name,
                    path=str(path.resolve()),
                    range_start_sec=start,
                    timestamp_sec=round(timestamp, 3),
                    sequence=global_sequence,
                )
            )
            global_sequence += 1

    metadata_path = args.out_dir / "metadata.json"
    metadata_path.write_text(
        json.dumps([record.__dict__ for record in metadata], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "video": str(video),
                "frames": len(metadata),
                "fps": args.fps,
                "ranges": ranges,
                "frames_dir": str(frames_dir),
                "metadata": str(metadata_path),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def data_url(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def post_response(api_key: str, base_url: str, payload: dict[str, Any], timeout: int) -> dict[str, Any]:
    request = urllib.request.Request(
        base_url.rstrip("/") + "/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI API HTTP {exc.code}: {detail}") from exc


def output_text(response: dict[str, Any]) -> str:
    if isinstance(response.get("output_text"), str):
        return response["output_text"]
    chunks: list[str] = []
    for item in response.get("output", []) or []:
        for content in item.get("content", []) or []:
            if isinstance(content, dict) and content.get("type") in {"output_text", "text"}:
                text = content.get("text")
                if isinstance(text, str):
                    chunks.append(text)
    return "\n".join(chunks).strip()


def parse_jsonish(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", cleaned, flags=re.DOTALL | re.IGNORECASE)
    if fence:
        cleaned = fence.group(1).strip()
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        return {"events": [], "parse_error": "model output was not valid JSON", "raw_output": text}
    if not isinstance(parsed, dict):
        return {"events": [], "parse_error": "model output root was not an object", "raw_output": text}
    if not isinstance(parsed.get("events"), list):
        parsed["events"] = []
    return parsed


def load_metadata(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON array")
    return [record for record in data if isinstance(record, dict)]


def ocr_frames(args: argparse.Namespace) -> int:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        eprint("OPENAI_API_KEY is not set. Prepare frames can run without it; OCR cannot.")
        return 2

    metadata = load_metadata(args.metadata)
    out_dir = args.out_dir / "responses"
    out_dir.mkdir(parents=True, exist_ok=True)
    events_path = args.out_dir / "gpt_vision_events.json"
    existing = json.loads(events_path.read_text(encoding="utf-8")) if events_path.exists() else []
    done = {record.get("frame") for record in existing if record.get("status") == "ok"}
    records = existing
    ok = 0
    errors = 0

    jobs: list[dict[str, Any]] = []
    for record in metadata:
        frame = record.get("frame")
        path = Path(str(record.get("path", "")))
        if not frame or not path.exists():
            eprint(f"skip missing frame in metadata: {record}")
            continue
        if frame in done and not args.force:
            continue
        jobs.append(record)
    if args.limit:
        jobs = jobs[: args.limit]

    batch_size = max(1, args.batch_size)
    batches = [jobs[index : index + batch_size] for index in range(0, len(jobs), batch_size)]

    for index, batch in enumerate(batches, start=1):
        batch_frames = [str(record.get("frame")) for record in batch]
        eprint(f"[{index}/{len(batches)}] GPT Vision OCR {', '.join(batch_frames)}")
        prompt = args.prompt or (
            PROMPT
            + "\n\nWhen multiple images are provided, each event must include source_frame exactly matching the frame filename printed before that image."
        )
        content: list[dict[str, Any]] = [{"type": "input_text", "text": prompt}]
        for record in batch:
            path = Path(str(record.get("path", "")))
            content.append({"type": "input_text", "text": f"source_frame: {record.get('frame')}"})
            content.append({"type": "input_image", "image_url": data_url(path), "detail": args.detail})
        payload: dict[str, Any] = {
            "model": args.model,
            "input": [
                {
                    "role": "user",
                    "content": content,
                }
            ],
            "text": {"format": {"type": "json_object"}},
            "max_output_tokens": args.max_output_tokens,
        }
        started = time.time()
        try:
            response = post_response(
                api_key=api_key,
                base_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
                payload=payload,
                timeout=args.timeout,
            )
            text = output_text(response)
            parsed = parse_jsonish(text)
            batch_stem = Path(batch_frames[0]).stem if len(batch_frames) == 1 else f"{Path(batch_frames[0]).stem}_batch{len(batch_frames)}"
            response_path = out_dir / f"{batch_stem}.response.json"
            parsed_path = out_dir / f"{batch_stem}.json"
            response_path.write_text(json.dumps(response, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            parsed_path.write_text(json.dumps(parsed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            records.append(
                {
                    "status": "ok",
                    "frame": batch_frames[0],
                    "frames": batch_frames,
                    "image_path": str(Path(str(batch[0].get("path", "")))),
                    "image_paths": [str(record.get("path", "")) for record in batch],
                    "timestamp_sec": batch[0].get("timestamp_sec"),
                    "timestamps_sec": [record.get("timestamp_sec") for record in batch],
                    "sequence": batch[0].get("sequence"),
                    "sequences": [record.get("sequence") for record in batch],
                    "model": args.model,
                    "elapsed_sec": round(time.time() - started, 3),
                    "response_id": response.get("id"),
                    "parsed_json": str(parsed_path),
                    "events": parsed.get("events", []),
                    "parse_error": parsed.get("parse_error", ""),
                    "notes": parsed.get("notes", ""),
                }
            )
            ok += 1
        except Exception as exc:
            records.append(
                {
                    "status": "error",
                    "frame": batch_frames[0] if batch_frames else "",
                    "frames": batch_frames,
                    "image_paths": [str(record.get("path", "")) for record in batch],
                    "timestamp_sec": batch[0].get("timestamp_sec") if batch else "",
                    "timestamps_sec": [record.get("timestamp_sec") for record in batch],
                    "sequence": batch[0].get("sequence") if batch else "",
                    "sequences": [record.get("sequence") for record in batch],
                    "model": args.model,
                    "elapsed_sec": round(time.time() - started, 3),
                    "error": str(exc),
                }
            )
            errors += 1
            eprint(f"failed {', '.join(batch_frames)}: {exc}")
        events_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if args.sleep and index < len(batches):
            time.sleep(args.sleep)

    print(
        json.dumps(
            {"jobs": len(jobs), "batches": len(batches), "ok": ok, "errors": errors, "events": str(events_path)},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 1 if errors else 0


def normalize_server(value: Any) -> str:
    text = str(value or "").strip()
    match = re.search(r"(\d{3})", text)
    return f"#{match.group(1)}" if match else ""


def to_int(value: Any) -> int | None:
    if isinstance(value, int):
        return value
    match = re.search(r"\d+", str(value or ""))
    return int(match.group(0)) if match else None


def target_from_raw_text(raw_text: str) -> tuple[str, int, int] | None:
    normalized = raw_text.replace("＃", "#").replace("（", "(").replace("）", ")").replace("，", ",")
    matches = list(re.finditer(r"#\s*(\d{3})\s*\(\s*(\d{1,4})\s*,\s*(\d{1,4})\s*\)", normalized))
    if not matches:
        return None
    # The destruction target is the coordinate-bearing #server(x,y) reference.
    match = matches[-1]
    return f"#{match.group(1)}", int(match.group(2)), int(match.group(3))


def xy_to_coord(x: int, y: int) -> str:
    if (x - 49) % 100 != 0 or (y - 49) % 100 != 0:
        return ""
    col = (x - 49) // 100
    row = (y - 49) // 100
    if not (0 <= col <= 10 and 0 <= row <= 10):
        return ""
    return f"{chr(ord('a') + row)}-{(col + 1) * 2}"


def load_gpt_records(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON array")
    return [record for record in data if isinstance(record, dict)]


def flatten_events(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for record in records:
        if record.get("status") != "ok":
            continue
        for event in record.get("events", []) or []:
            if not isinstance(event, dict):
                continue
            raw_text = str(event.get("raw_text") or "")
            raw_target = target_from_raw_text(raw_text)
            if raw_target:
                server, x, y = raw_target
            else:
                server = normalize_server(event.get("target_server"))
                x = to_int(event.get("x"))
                y = to_int(event.get("y"))
            if server not in KNOWN_SERVERS or x is None or y is None:
                continue
            target_type = str(event.get("target_type") or "")
            if target_type and "都市" not in target_type:
                continue
            rows.append(
                {
                    "target_server": server,
                    "coord": xy_to_coord(x, y),
                    "x": x,
                    "y": y,
                    "event_time": str(event.get("event_time") or ""),
                    "actor_server": normalize_server(event.get("actor_server")),
                    "actor_alliance": str(event.get("actor_alliance") or ""),
                    "defender_alliance": str(event.get("defender_alliance") or ""),
                    "level": str(event.get("level") or ""),
                    "text_color": str(event.get("text_color") or "unknown"),
                    "destroyed_by": str(event.get("destroyed_by") or "unknown"),
                    "frame": str(event.get("source_frame") or record.get("frame", "")),
                    "timestamp_sec": record.get("timestamp_sec", ""),
                    "raw_text": raw_text,
                }
            )
    return rows


def dedupe_events(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key: dict[tuple[str, int, int], dict[str, Any]] = {}
    for row in rows:
        key = (row["target_server"], int(row["x"]), int(row["y"]))
        current = by_key.get(key)
        if current is None:
            by_key[key] = row
            continue
        current_time = str(current.get("event_time") or "")
        new_time = str(row.get("event_time") or "")
        if new_time and (not current_time or new_time < current_time):
            by_key[key] = row
    return sorted(by_key.values(), key=lambda r: (r["target_server"], int(r["y"]), int(r["x"])))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = []
        for row in rows:
            for key in row:
                if key not in fieldnames:
                    fieldnames.append(key)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_sheet_city_rows(credentials: Path, spreadsheet: str) -> dict[tuple[str, str], dict[str, Any]]:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = service_account.Credentials.from_service_account_file(str(credentials), scopes=scopes)
    svc = build("sheets", "v4", credentials=creds, cache_discovery=False)
    values = (
        svc.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet, range="管理表たたき!A1:T2500", valueRenderOption="FORMATTED_VALUE")
        .execute()
        .get("values", [])
    )
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    for index, row in enumerate(values[1:], start=2):
        padded = row + [""] * 20
        server = padded[18].strip()
        coord = padded[0].strip().lower()
        if server in KNOWN_SERVERS and padded[2].strip() == "都市" and coord:
            rows[(server, coord)] = {
                "row": index,
                "owner": padded[3].strip(),
                "acquired_at": padded[4].strip(),
                "memo": padded[11].strip(),
            }
    return rows


def aggregate(args: argparse.Namespace) -> int:
    records = load_gpt_records(args.events)
    raw_rows = flatten_events(records)
    deduped = dedupe_events(raw_rows)
    prefix = args.run_date
    raw_path = args.data_dir / f"{prefix}_city_destroy_gpt_vision_raw_events.csv"
    events_path = args.data_dir / f"{prefix}_city_destroy_gpt_vision_deduped_events.csv"
    summary_path = args.data_dir / f"{prefix}_city_destroy_gpt_vision_summary.csv"
    missing_path = args.data_dir / f"{prefix}_city_destroy_gpt_vision_sheet_missing.csv"
    outside_path = args.data_dir / f"{prefix}_city_destroy_gpt_vision_not_in_sheet.csv"

    write_csv(raw_path, raw_rows)
    write_csv(events_path, deduped)

    sheet_rows: dict[tuple[str, str], dict[str, Any]] = {}
    if args.compare_sheet:
        sheet_rows = read_sheet_city_rows(args.credentials, args.spreadsheet)

    summary: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    outside: list[dict[str, Any]] = []
    for server in KNOWN_SERVERS:
        video_keys = {(row["target_server"], row["coord"]) for row in deduped if row["target_server"] == server and row["coord"]}
        destroyed = 0
        city_count = 0
        if sheet_rows:
            server_sheet = {key: value for key, value in sheet_rows.items() if key[0] == server}
            city_count = len(server_sheet)
            destroyed = sum(1 for value in server_sheet.values() if value["owner"] == "破壊")
            for key in sorted(video_keys):
                sheet = sheet_rows.get(key)
                source = next(row for row in deduped if (row["target_server"], row["coord"]) == key)
                if not sheet:
                    outside.append({"server": key[0], "coord": key[1], "frame": source["frame"], "raw_text": source["raw_text"]})
                elif sheet["owner"] != "破壊":
                    missing.append({**source, "sheet_row": sheet["row"], "current_owner": sheet["owner"], "current_acquired_at": sheet["acquired_at"]})
        summary.append(
            {
                "server": server,
                "gpt_video_destroy_unique_coords": len(video_keys),
                "sheet_city_rows": city_count if sheet_rows else "",
                "sheet_destroyed": destroyed if sheet_rows else "",
                "video_destroy_not_marked_in_sheet": sum(1 for row in missing if row["target_server"] == server) if sheet_rows else "",
                "video_destroy_not_in_city_rows": sum(1 for row in outside if row["server"] == server) if sheet_rows else "",
            }
        )

    write_csv(summary_path, summary)
    if args.compare_sheet:
        write_csv(missing_path, missing)
        write_csv(outside_path, outside)
    print(
        json.dumps(
            {
                "raw_events": len(raw_rows),
                "deduped_events": len(deduped),
                "summary": str(summary_path),
                "events": str(events_path),
                "missing": str(missing_path) if args.compare_sheet else "",
                "outside": str(outside_path) if args.compare_sheet else "",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="High-density GPT Vision OCR for S6 city-destruction history videos.")
    sub = parser.add_subparsers(dest="command", required=True)

    suggest = sub.add_parser("suggest-ranges", help="Suggest dense-extraction ranges from existing Apple Vision raw OCR.")
    suggest.add_argument("--raw-dir", type=Path, default=ROOT / "tmp" / "city_destroy_video_20260621_vision" / "apple_vision_raw")
    suggest.add_argument("--server", action="append", default=[], help="Target server to search, e.g. #534. Repeatable.")
    suggest.add_argument("--source-fps", type=float, default=1.0, help="FPS used for the existing raw OCR frames.")
    suggest.add_argument("--first-frame-number", type=int, default=1, help="First extracted frame number, usually 1 for frame_0001.")
    suggest.add_argument("--frame-zero-sec", type=float, default=0.0, help="Timestamp for first-frame-number.")
    suggest.add_argument("--pad", type=float, default=1.5)
    suggest.add_argument("--merge-gap", type=float, default=2.0)
    suggest.add_argument("--out", type=Path, default=None)
    suggest.set_defaults(func=suggest_ranges)

    prepare = sub.add_parser("prepare", help="Extract high-density frames from selected video ranges.")
    prepare.add_argument("--video", type=Path, required=True)
    prepare.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    prepare.add_argument("--range", action="append", default=[], help="Seconds range START-END. Repeatable or comma-separated.")
    prepare.add_argument("--fps", type=float, default=3.0)
    prepare.add_argument("--scale-width", type=int, default=1800)
    prepare.add_argument("--crop-rel", default="0.20,0.16,0.62,0.70", help="Relative crop x,y,w,h. Use empty string to disable.")
    prepare.add_argument("--ffmpeg", default="ffmpeg")
    prepare.add_argument("--ffprobe", default="ffprobe")
    prepare.set_defaults(func=prepare_frames)

    ocr = sub.add_parser("ocr", help="Send prepared frames to OpenAI Responses API.")
    ocr.add_argument("--metadata", type=Path, default=DEFAULT_OUT_DIR / "metadata.json")
    ocr.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    ocr.add_argument("--model", default=DEFAULT_MODEL)
    ocr.add_argument("--detail", choices=["low", "high", "auto"], default="high")
    ocr.add_argument("--max-output-tokens", type=int, default=2400)
    ocr.add_argument("--timeout", type=int, default=180)
    ocr.add_argument("--sleep", type=float, default=0.0)
    ocr.add_argument("--limit", type=int, default=0)
    ocr.add_argument("--batch-size", type=int, default=1)
    ocr.add_argument("--force", action="store_true")
    ocr.add_argument("--prompt", default="")
    ocr.set_defaults(func=ocr_frames)

    agg = sub.add_parser("aggregate", help="Aggregate GPT Vision OCR records into CSV summaries.")
    agg.add_argument("--events", type=Path, default=DEFAULT_OUT_DIR / "gpt_vision_events.json")
    agg.add_argument("--data-dir", type=Path, default=DATA_DIR)
    agg.add_argument("--run-date", default="2026-06-21")
    agg.add_argument("--compare-sheet", action="store_true")
    agg.add_argument("--spreadsheet", default=DEFAULT_SPREADSHEET)
    agg.add_argument("--credentials", type=Path, default=DEFAULT_CREDENTIALS)
    agg.set_defaults(func=aggregate)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except Exception as exc:
        eprint(f"error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
