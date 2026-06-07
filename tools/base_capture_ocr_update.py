from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from google.auth import default
from google.oauth2 import service_account
from googleapiclient.discovery import build


ROOT = Path(__file__).resolve().parents[1]
SPREADSHEET_ID = "12uNW9XphH2zSX4h5BzjSd-OON9r5AckAuNCwQTbY79g"
SHEET = "管理表たたき"
IMAGE_DIR = Path("/Users/mba2025/Library/CloudStorage/Dropbox-FIT/訓北﨑/lastwar/S6/拠点取得スクショ")
OUT_DIR = ROOT / "tmp" / "base_capture_full_ocr"
DATA_DIR = ROOT / "data"
VISION_SCRIPT = ROOT / "tools" / "vision_ocr.swift"
CORRECTIONS_PATH = ROOT / "inputs" / "ocr_alliance_corrections.json"
DEFAULT_CREDENTIALS = Path("/Users/mba2025/.config/gptcodex/credentials-sub.json")


@dataclass
class Event:
    image: str
    image_path: str
    screen_type: str
    event_time: datetime
    actor_server: str
    actor_alliance: str
    opponent_alliance: str
    target_server: str
    x: int
    y: int
    level: str
    terrain: str
    kind_raw: str
    kind_sheet: str
    action: str
    owner_for_sheet: str
    confidence: str
    time_source: str
    source_text: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="OCR Dropbox base-capture screenshots and update 管理表たたき.")
    parser.add_argument("--image-dir", type=Path, default=IMAGE_DIR)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    parser.add_argument("--run-date", default="2026-06-06")
    parser.add_argument("--credentials", type=Path, default=DEFAULT_CREDENTIALS)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--trust-type-mismatch", action="store_true")
    parser.add_argument("--apply", action="store_true")
    return parser.parse_args()


def load_corrections() -> dict[str, str]:
    if not CORRECTIONS_PATH.exists():
        return {}
    return json.loads(CORRECTIONS_PATH.read_text(encoding="utf-8"))


def correct_tag(tag: str, corrections: dict[str, str]) -> str:
    tag = normalize_chars(tag).strip()
    tag = tag.strip("[](){}:：,，.。!！| ")
    return corrections.get(tag, tag)


def normalize_chars(text: str) -> str:
    replacements = {
        "＃": "#",
        "【": "[",
        "】": "]",
        "［": "[",
        "］": "]",
        "（": "(",
        "）": ")",
        "「": "",
        "」": "",
        "：": ":",
        "，": ",",
        "×": "x",
        "０": "0",
        "１": "1",
        "２": "2",
        "３": "3",
        "４": "4",
        "５": "5",
        "６": "6",
        "７": "7",
        "８": "8",
        "９": "9",
    }
    for before, after in replacements.items():
        text = text.replace(before, after)
    return text


def clean_vision_lines(output: str) -> list[str]:
    lines: list[str] = []
    for line in output.splitlines():
        line = normalize_chars(line.strip())
        if not line or line.startswith("====="):
            continue
        parts = line.split(maxsplit=5)
        if len(parts) >= 6:
            try:
                [float(part) for part in parts[:5]]
            except ValueError:
                pass
            else:
                line = parts[5]
        if line:
            lines.append(line)
    return lines


def run_apple_vision(image: Path, out_dir: Path) -> str:
    cache = out_dir / "apple_vision_raw" / f"{image.stem}.txt"
    cache.parent.mkdir(parents=True, exist_ok=True)
    if cache.exists():
        return cache.read_text(encoding="utf-8")
    module_cache = ROOT / "tmp" / "swift_module_cache"
    module_cache.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        ["swift", "-module-cache-path", str(module_cache), str(VISION_SCRIPT), str(image)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=90,
    )
    text = proc.stdout
    meaningful_stderr = "\n".join(
        line
        for line in proc.stderr.splitlines()
        if "DVTFilePathFSEvents" not in line and "DVTDeveloperPaths" not in line
    ).strip()
    if meaningful_stderr:
        text += "\n" + meaningful_stderr
    cache.write_text(text, encoding="utf-8")
    return text


def image_date(image: Path, event_hhmm: str | None = None) -> datetime:
    stamp = getattr(image.stat(), "st_birthtime", image.stat().st_mtime)
    captured = datetime.fromtimestamp(stamp)
    if not event_hhmm:
        return captured
    hour, minute = [int(part) for part in event_hhmm.split(":")[:2]]
    candidate = captured.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if candidate > captured + timedelta(hours=1):
        candidate -= timedelta(days=1)
    return candidate


def parse_datetime(value: str, image: Path) -> datetime:
    value = re.sub(r"\s+", " ", normalize_chars(value)).strip()
    match = re.search(r"(20\d{2})[-/](\d{1,2})[-/](\d{1,2})\s+(\d{1,2}):(\d{2})(?::(\d{2}))?", value)
    if match:
        year, month, day, hour, minute, second = match.groups()
        dt = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second or 0))
        captured = image_date(image)
        if abs((captured - dt).days) > 180:
            dt = dt.replace(year=captured.year)
        return dt
    match = re.search(r"\b(\d{1,2})[-/](\d{1,2})\s+(\d{1,2}):(\d{2})\b", value)
    if match:
        month, day, hour, minute = match.groups()
        captured = image_date(image)
        return datetime(captured.year, int(month), int(day), int(hour), int(minute), 0)
    match = re.search(r"\b(\d{1,2}):(\d{2})\b", value)
    if match:
        return image_date(image, f"{match.group(1)}:{match.group(2)}")
    return image_date(image)


def image_sort_key(image: Path) -> tuple[int, str, str]:
    match = re.search(r"(\d+)", image.stem)
    number = int(match.group(1)) if match else -1
    return (number, image.name, str(image.parent))


def visible_timeline_times(lines: list[str]) -> list[str]:
    times: list[str] = []
    for line in lines:
        normalized = normalize_chars(line).strip()
        match = re.fullmatch(r"(?:\d{1,2}[-/]\d{1,2}\s+)?\d{1,2}:\d{2}", normalized)
        if match:
            times.append(match.group(0))
    return times


def build_previous_visible_time_map(image_lines: dict[Path, list[str]]) -> dict[Path, str]:
    fallback: dict[Path, str] = {}
    previous_hhmm = ""
    previous_date: datetime | None = None
    for image in sorted(image_lines, key=image_sort_key):
        captured = image_date(image)
        if previous_hhmm and previous_date and abs((captured.date() - previous_date.date()).days) <= 1:
            fallback[image] = previous_hhmm
        times = visible_timeline_times(image_lines[image])
        if times:
            previous_hhmm = times[-1]
            previous_date = captured
    return fallback


def is_inferred_time(event: Event) -> bool:
    return event.time_source in {"image_metadata_inferred", "previous_image_visible_time"}


def kind_for_sheet(kind: str) -> str:
    if "漁場" in kind:
        return "漁場"
    if "交易地" in kind:
        return "交易地"
    if "祭壇" in kind:
        return "祭壇"
    if any(word in kind for word in ["都市", "村", "兵舎", "集会場"]):
        return "都市"
    return kind or "要確認"


def parse_history_events(lines: list[str], image: Path, corrections: dict[str, str]) -> list[Event]:
    text = " ".join(lines)
    text = re.sub(r"\s+", " ", normalize_chars(text))
    pattern = re.compile(
        r"#(?P<actor_server>\d{3,4})\s*\[\s*(?P<actor>[A-Za-z0-9_-]{1,10})\s*\]?"
        r"\s*が\s*#(?P<target_server>\d{3,4})(?:\s*\[\s*(?P<opp>[A-Za-z0-9_-]{1,10})\s*\])?"
        r"\s*領有中の\s*L[vV]\.?\s*(?P<level>\d+)\s*(?P<kind>都市|漁場|交易地|密林の兵舎|湿地の兵舎|密林の集会場|湿地の集会場|密林の村|湿地の村)"
        r"\s*#(?P=target_server)\s*\(\s*(?P<x>\d{1,4})\s*,\s*(?P<y>\d{1,4})\s*\)"
        r".{0,80}?(?P<dt>20\d{2}[-/]\d{1,2}[-/]\d{1,2}\s+\d{1,2}:\d{2}:\d{2})",
    )
    events: list[Event] = []
    for match in pattern.finditer(text):
        kind_raw = match.group("kind")
        actor = correct_tag(match.group("actor"), corrections)
        opp = correct_tag(match.group("opp") or "", corrections) if match.group("opp") else ""
        events.append(
            Event(
                image=image.name,
                image_path=str(image),
                screen_type="history_modal",
                event_time=parse_datetime(match.group("dt"), image),
                actor_server=f"#{match.group('actor_server')}",
                actor_alliance=actor,
                opponent_alliance=opp,
                target_server=f"#{match.group('target_server')}",
                x=int(match.group("x")),
                y=int(match.group("y")),
                level=match.group("level"),
                terrain="",
                kind_raw=kind_raw,
                kind_sheet=kind_for_sheet(kind_raw),
                action="destroy",
                owner_for_sheet="破壊",
                confidence="medium",
                time_source="visible_datetime",
                source_text=match.group(0),
            )
        )
    return events


def windows(lines: list[str], size: int = 3) -> list[tuple[int, str]]:
    result = []
    for index in range(len(lines)):
        result.append((index, " ".join(lines[index : index + size])))
    return result


def parse_timeline_events(lines: list[str], image: Path, corrections: dict[str, str], fallback_hhmm: str = "") -> list[Event]:
    events: list[Event] = []
    current_time_by_index: dict[int, str] = {}
    current_time: str | None = None
    for index, line in enumerate(lines):
        line = normalize_chars(line)
        time_match = re.fullmatch(r"(?:\d{1,2}[-/]\d{1,2}\s+)?\d{1,2}:\d{2}", line.strip())
        if time_match:
            current_time = line.strip()
        current_time_by_index[index] = current_time or ""

    patterns = [
        (
            "steal",
            re.compile(
                r"連盟\s*(?P<actor>[A-Za-z0-9_-]{1,10})\s*は\s*連盟\s*(?P<opp>[A-Za-z0-9_-]{1,10})\s*の\s*"
                r"L[vV]\.?\s*(?P<level>\d+)\s*(?P<terrain>密林の|湿地の)?\s*(?P<kind>漁場|兵舎|集会場|村|交易地|祭壇)"
                r".{0,20}?#(?P<server>\d{3,4})\s*\(\s*X\s*:\s*(?P<x>\d{1,4})\s*,\s*Y\s*:\s*(?P<y>\d{1,4})\s*\).{0,30}?奪\s*い?"
            ),
        ),
        (
            "occupy",
            re.compile(
                r"連盟\s*(?P<actor>[A-Za-z0-9_-]{1,10})\s*が\s*L[vV]\.?\s*(?P<level>\d+)\s*"
                r"(?P<terrain>密林の|湿地の)?\s*(?P<kind>漁場|兵舎|集会場|村|交易地|祭壇)"
                r".{0,20}?#(?P<server>\d{3,4})\s*\(\s*X\s*:\s*(?P<x>\d{1,4})\s*,\s*Y\s*:\s*(?P<y>\d{1,4})\s*\).{0,50}?占\s*領"
            ),
        ),
    ]
    seen: set[tuple[str, str, str, str, str]] = set()
    for index, chunk in windows([normalize_chars(line) for line in lines], size=4):
        chunk = re.sub(r"\s+", " ", chunk)
        hhmm = current_time_by_index.get(index, "")
        for action, pattern in patterns:
            for match in pattern.finditer(chunk):
                actor = correct_tag(match.group("actor"), corrections)
                opp = correct_tag(match.groupdict().get("opp") or "", corrections)
                server = f"#{match.group('server')}"
                x = match.group("x")
                y = match.group("y")
                key = (image.name, action, actor, server, x, y)
                if key in seen:
                    continue
                seen.add(key)
                terrain = (match.group("terrain") or "").replace("の", "")
                kind_raw = (match.group("terrain") or "") + match.group("kind")
                tail = chunk[match.start() : match.end() + 40]
                action_name = "first_occupy" if action == "occupy" and "最初" in tail else action
                events.append(
                    Event(
                        image=image.name,
                        image_path=str(image),
                        screen_type="timeline_chat",
                        event_time=parse_datetime(hhmm or fallback_hhmm, image) if (hhmm or fallback_hhmm) else image_date(image),
                        actor_server="",
                        actor_alliance=actor,
                        opponent_alliance=opp,
                        target_server=server,
                        x=int(x),
                        y=int(y),
                        level=match.group("level"),
                        terrain=terrain,
                        kind_raw=kind_raw,
                        kind_sheet=kind_for_sheet(kind_raw),
                        action=action_name,
                        owner_for_sheet=actor,
                        confidence="medium" if hhmm else "low",
                        time_source="visible_time" if hhmm else ("previous_image_visible_time" if fallback_hhmm else "image_metadata_inferred"),
                        source_text=match.group(0),
                    )
                )
    return events


def parse_events(raw_output: str, image: Path, corrections: dict[str, str], fallback_hhmm: str = "") -> list[Event]:
    lines = clean_vision_lines(raw_output)
    return parse_history_events(lines, image, corrections) + parse_timeline_events(lines, image, corrections, fallback_hhmm)


def service(credentials_path: Path | None = None) -> Any:
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    if credentials_path and credentials_path.exists():
        creds = service_account.Credentials.from_service_account_file(str(credentials_path), scopes=scopes)
    else:
        creds, _ = default(scopes=scopes)
    return build("sheets", "v4", credentials=creds)


def read_sheet_values(svc: Any) -> list[list[str]]:
    result = (
        svc.spreadsheets()
        .values()
        .get(spreadsheetId=SPREADSHEET_ID, range=f"{SHEET}!A1:T2500", valueRenderOption="FORMATTED_VALUE")
        .execute()
    )
    return result.get("values", [])


def parse_sheet_datetime(value: str) -> datetime | None:
    if not value:
        return None
    value = value.strip()
    for fmt in ("%Y/%m/%d %H:%M", "%Y/%m/%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass
    return None


def build_sheet_indexes(values: list[list[str]]) -> tuple[dict[str, int], dict[tuple[str, int, int], int]]:
    key_to_row: dict[str, int] = {}
    coord_to_row: dict[tuple[str, int, int], int] = {}
    memo_pattern = re.compile(r"(#\d{3,4}|中央)\s*X\s*:\s*(\d{1,4})\s*Y\s*:\s*(\d{1,4})", re.IGNORECASE)
    for row_index, row in enumerate(values, start=1):
        padded = row + [""] * (20 - len(row))
        area = padded[18].strip()
        key = padded[19].strip()
        memo = normalize_chars(padded[11])
        if key:
            key_to_row[key] = row_index
            key_coord = key_to_xy(key)
            if key_coord:
                coord_to_row[key_coord] = row_index
        for match in memo_pattern.finditer(memo):
            coord_to_row[(match.group(1), int(match.group(2)), int(match.group(3)))] = row_index
        if area and memo:
            for match in re.finditer(r"X\s*:\s*(\d{1,4})\s*Y\s*:\s*(\d{1,4})", memo, re.IGNORECASE):
                coord_to_row[(area, int(match.group(1)), int(match.group(2)))] = row_index
    return key_to_row, coord_to_row


def key_to_xy(key: str) -> tuple[str, int, int] | None:
    match = re.fullmatch(r"(#\d{3,4}|中央):([A-Ka-k]|中央-\d+)-(\d{1,2})", key.strip())
    if not match:
        return None
    area, row_part, column_text = match.groups()
    column = int(column_text)
    if area == "中央":
        # The center map uses custom key labels that are already represented in
        # memo/state data; do not guess their screen coordinates from the key.
        return None
    if len(row_part) != 1:
        return None
    row_index = ord(row_part.lower()) - ord("a") + 1
    if row_part.islower():
        x = column * 50 - 51
        y = row_index * 100 - 51
    else:
        x = 20 if column == 1 else 978 if column == 21 else column * 50 - 51
        y = 20 if row_index == 1 else 978 if row_index == 11 else row_index * 100 - 101
    if x < 0 or y < 0:
        return None
    return area, x, y


def add_state_coord_index(coord_to_row: dict[tuple[str, int, int], int], key_to_row: dict[str, int]) -> None:
    state_path = ROOT / "sample_output" / "state.json"
    if not state_path.exists():
        return
    state = json.loads(state_path.read_text(encoding="utf-8"))
    memo_pattern = re.compile(r"(#\d{3,4}|中央)\s*X\s*:\s*(\d{1,4})\s*Y\s*:\s*(\d{1,4})", re.IGNORECASE)
    for node in state.get("nodes", []):
        row_index = key_to_row.get(str(node.get("id", "")))
        if not row_index:
            continue
        memo = normalize_chars(str(node.get("memo", "")))
        for match in memo_pattern.finditer(memo):
            coord_to_row[(match.group(1), int(match.group(2)), int(match.group(3)))] = row_index


def event_to_row(event: Event) -> dict[str, Any]:
    memo = (
        f"Dropbox赤字OCR {event.image} / {event.target_server} X:{event.x} Y:{event.y} "
        f"Lv.{event.level} {event.kind_raw} / "
    )
    if event.action == "destroy":
        memo += f"攻撃側 {event.actor_server}[{event.actor_alliance}]"
        if event.opponent_alliance:
            memo += f" / 防衛側 {event.target_server}[{event.opponent_alliance}]"
        memo += " / 破壊済み・復活なし"
    elif event.action in {"steal", "first_occupy", "occupy"}:
        before = event.opponent_alliance or "中立/未登録"
        arrow = " -> "
        memo += f"{before}{arrow}{event.actor_alliance}"
        if event.action == "steal":
            memo += " / 奪取"
        if event.action == "first_occupy":
            memo += " / 最初の連盟"
    if event.time_source == "previous_image_visible_time":
        memo += " / 時刻は直前の古い画像ファイルで見えた時刻から補完"
    elif event.time_source == "image_metadata_inferred":
        memo += " / 時刻は画像メタデータから推定"
    memo += f" / raw:{event.source_text[:180]}"
    return {
        "type": event.kind_sheet,
        "owner": event.owner_for_sheet,
        "acquired_at": event.event_time.strftime("%Y/%m/%d %H:%M"),
        "memo": memo,
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    corrections = load_corrections()
    images = sorted(
        (
            path
            for ext in ("*.png", "*.PNG", "*.jpg", "*.JPG", "*.jpeg", "*.JPEG")
            for path in args.image_dir.rglob(ext)
        ),
        key=image_sort_key,
    )
    if args.limit:
        images = images[: args.limit]

    image_lines: dict[Path, list[str]] = {}
    raw_outputs: dict[Path, str] = {}
    started = time.perf_counter()
    for index, image in enumerate(images, start=1):
        raw = run_apple_vision(image, args.out_dir)
        raw_outputs[image] = raw
        image_lines[image] = clean_vision_lines(raw)
        print(f"[{index}/{len(images)}] {image.name}: ocr_lines={len(image_lines[image])}")

    fallback_hhmm_by_image = build_previous_visible_time_map(image_lines)
    all_events: list[Event] = []
    for index, image in enumerate(images, start=1):
        events = parse_events(raw_outputs[image], image, corrections, fallback_hhmm_by_image.get(image, ""))
        all_events.extend(events)
        print(f"[{index}/{len(images)}] {image.name}: events={len(events)} total={len(all_events)} fallback_time={fallback_hhmm_by_image.get(image, '')}")

    event_rows = [
        {
            "image": event.image,
            "screen_type": event.screen_type,
            "event_time": event.event_time.strftime("%Y/%m/%d %H:%M:%S"),
            "actor_server": event.actor_server,
            "actor_alliance": event.actor_alliance,
            "opponent_alliance": event.opponent_alliance,
            "target_server": event.target_server,
            "x": event.x,
            "y": event.y,
            "level": event.level,
            "terrain": event.terrain,
            "kind_raw": event.kind_raw,
            "kind_sheet": event.kind_sheet,
            "action": event.action,
            "owner_for_sheet": event.owner_for_sheet,
            "confidence": event.confidence,
            "time_source": event.time_source,
            "source_text": event.source_text,
        }
        for event in all_events
    ]
    write_csv(args.data_dir / f"{args.run_date}_base_capture_full_ocr_events.csv", event_rows)

    latest: dict[tuple[str, int, int], Event] = {}
    for event in all_events:
        key = (event.target_server, event.x, event.y)
        current = latest.get(key)
        if current and is_inferred_time(event) and not is_inferred_time(current):
            if event.owner_for_sheet == current.owner_for_sheet and event.kind_sheet == current.kind_sheet:
                continue
        if key not in latest or event.event_time > latest[key].event_time:
            latest[key] = event

    svc = service(args.credentials)
    values = read_sheet_values(svc)
    key_to_row, coord_to_row = build_sheet_indexes(values)
    add_state_coord_index(coord_to_row, key_to_row)

    update_rows: list[dict[str, Any]] = []
    review_rows: list[dict[str, Any]] = []
    ranges: dict[str, list[list[str]]] = {}
    for key, event in sorted(latest.items(), key=lambda item: item[1].event_time):
        row_index = coord_to_row.get(key)
        if not row_index:
            review_rows.append(
                {
                    "reason": "row_not_found",
                    "target_server": key[0],
                    "x": key[1],
                    "y": key[2],
                    "image": event.image,
                    "event_time": event.event_time.strftime("%Y/%m/%d %H:%M:%S"),
                    "owner_for_sheet": event.owner_for_sheet,
                    "kind_sheet": event.kind_sheet,
                    "source_text": event.source_text,
                }
            )
            continue
        row = values[row_index - 1] + [""] * 20
        existing_dt = parse_sheet_datetime(row[4])
        existing_type = row[2]
        existing_owner = row[3]
        if is_inferred_time(event) and len(event.owner_for_sheet) < 2:
            review_rows.append(
                {
                    "reason": "low_confidence_short_owner",
                    "target_server": key[0],
                    "x": key[1],
                    "y": key[2],
                    "sheet_row": row_index,
                    "event_time": event.event_time.strftime("%Y/%m/%d %H:%M:%S"),
                    "owner_for_sheet": event.owner_for_sheet,
                    "image": event.image,
                    "source_text": event.source_text,
                }
            )
            continue
        if (
            is_inferred_time(event)
            and existing_dt
            and existing_type == event.kind_sheet
            and existing_owner == event.owner_for_sheet
        ):
            review_rows.append(
                {
                    "reason": "low_confidence_no_material_change",
                    "target_server": key[0],
                    "x": key[1],
                    "y": key[2],
                    "sheet_row": row_index,
                    "existing_at": row[4],
                    "event_time": event.event_time.strftime("%Y/%m/%d %H:%M:%S"),
                    "existing_owner": existing_owner,
                    "owner_for_sheet": event.owner_for_sheet,
                    "image": event.image,
                    "source_text": event.source_text,
                }
            )
            continue
        if existing_type and kind_for_sheet(existing_type) != event.kind_sheet and not args.trust_type_mismatch:
            review_rows.append(
                {
                    "reason": "type_mismatch",
                    "target_server": key[0],
                    "x": key[1],
                    "y": key[2],
                    "sheet_row": row_index,
                    "existing_type": existing_type,
                    "event_type": event.kind_sheet,
                    "existing_owner": existing_owner,
                    "owner_for_sheet": event.owner_for_sheet,
                    "event_time": event.event_time.strftime("%Y/%m/%d %H:%M:%S"),
                    "image": event.image,
                    "source_text": event.source_text,
                }
            )
            continue
        if existing_dt and existing_dt > event.event_time:
            review_rows.append(
                {
                    "reason": "existing_newer",
                    "target_server": key[0],
                    "x": key[1],
                    "y": key[2],
                    "sheet_row": row_index,
                    "existing_at": row[4],
                    "event_time": event.event_time.strftime("%Y/%m/%d %H:%M:%S"),
                    "existing_owner": row[3],
                    "owner_for_sheet": event.owner_for_sheet,
                    "image": event.image,
                    "source_text": event.source_text,
                }
            )
            continue
        update = event_to_row(event)
        ranges[f"C{row_index}:E{row_index}"] = [[update["type"], update["owner"], update["acquired_at"]]]
        ranges[f"L{row_index}:L{row_index}"] = [[update["memo"]]]
        update_rows.append(
            {
                "sheet_row": row_index,
                "position_key": row[19],
                "target_server": key[0],
                "x": key[1],
                "y": key[2],
                "previous_type": existing_type,
                "previous_owner": existing_owner,
                "previous_acquired_at": row[4],
                "new_type": update["type"],
                "new_owner": update["owner"],
                "new_acquired_at": update["acquired_at"],
                "image": event.image,
                "action": event.action,
                "time_source": event.time_source,
                "source_text": event.source_text,
            }
        )

    write_csv(args.data_dir / f"{args.run_date}_base_capture_full_ocr_sheet_updates.csv", update_rows)
    write_csv(args.data_dir / f"{args.run_date}_base_capture_full_ocr_review.csv", review_rows)

    if args.apply and ranges:
        body = {"valueInputOption": "USER_ENTERED", "data": [{"range": f"{SHEET}!{rng}", "values": data} for rng, data in ranges.items()]}
        result = svc.spreadsheets().values().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
        print(f"applied={result}")
    print(f"images={len(images)} events={len(all_events)} latest_targets={len(latest)} updates={len(update_rows)} review={len(review_rows)} seconds={time.perf_counter()-started:.1f}")
    print(args.data_dir / f"{args.run_date}_base_capture_full_ocr_events.csv")
    print(args.data_dir / f"{args.run_date}_base_capture_full_ocr_sheet_updates.csv")
    print(args.data_dir / f"{args.run_date}_base_capture_full_ocr_review.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
