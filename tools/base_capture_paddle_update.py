from __future__ import annotations

import argparse
import csv
import json
import os
import re
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from base_capture_ocr.paddle_runtime import create_paddle_ocr, predict_texts
from base_capture_ocr_update import (
    DATA_DIR,
    ROOT,
    Event,
    add_state_coord_index,
    build_previous_visible_time_map,
    build_sheet_indexes,
    correct_tag,
    event_to_row,
    image_sort_key,
    load_corrections,
    normalize_chars,
    parse_sheet_datetime,
    parse_timeline_events,
    write_csv,
)


DEFAULT_IMAGE_DIR = Path("/Users/mba2025/Library/CloudStorage/GoogleDrive-ktzkstsh@gmail.com/.tmp/2584/拠点取得スクショ")
DEFAULT_OUT_DIR = ROOT / "tmp" / "base_capture_paddle_ocr"
DEFAULT_SHEET_CSV = ROOT / "tmp" / "management_table.csv"
RUN_DATE = "2026-06-06"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="OCR base capture screenshots with PaddleOCR and prepare sheet updates.")
    parser.add_argument("--image-dir", type=Path, default=DEFAULT_IMAGE_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--sheet-csv", type=Path, default=DEFAULT_SHEET_CSV)
    parser.add_argument("--limit", type=int, default=0)
    return parser.parse_args()


def read_sheet_csv(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return [row for row in csv.reader(fh)]


def paddle_lines(ocr: Any, image: Path, out_dir: Path) -> list[str]:
    cache = out_dir / "paddle_raw" / f"{image.stem}.txt"
    cache.parent.mkdir(parents=True, exist_ok=True)
    if cache.exists():
        return [line for line in cache.read_text(encoding="utf-8").splitlines() if line.strip()]
    texts = predict_texts(ocr, image)
    lines = [normalize_chars(item.text.strip()) for item in texts if item.text.strip()]
    cache.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return lines


def visible_timeline_times_paddle(lines: list[str]) -> list[str]:
    times: list[str] = []
    for line in lines:
        normalized = normalize_chars(line).strip()
        if re.fullmatch(r"(?:\d{1,2}[-/]\d{1,2}\s+)?\d{1,2}:\d{2}", normalized):
            times.append(normalized)
    return times


def build_previous_visible_time_map_from_lines(image_lines: dict[Path, list[str]]) -> dict[Path, str]:
    fallback: dict[Path, str] = {}
    previous_hhmm = ""
    for image in sorted(image_lines, key=image_sort_key):
        if previous_hhmm:
            fallback[image] = previous_hhmm
        times = visible_timeline_times_paddle(image_lines[image])
        if times:
            previous_hhmm = times[-1]
    return fallback


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
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

    os.environ.setdefault("HOME", str(ROOT / "tmp" / "paddle_home"))
    os.environ.setdefault("PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK", "True")
    ocr = create_paddle_ocr()
    corrections = load_corrections()

    started = time.perf_counter()
    image_lines: dict[Path, list[str]] = {}
    for index, image in enumerate(images, start=1):
        lines = paddle_lines(ocr, image, args.out_dir)
        image_lines[image] = lines
        print(f"[{index}/{len(images)}] {image.name}: paddle_lines={len(lines)}")

    fallback_hhmm_by_image = build_previous_visible_time_map_from_lines(image_lines)
    all_events: list[Event] = []
    for index, image in enumerate(images, start=1):
        events = parse_timeline_events(image_lines[image], image, corrections, fallback_hhmm_by_image.get(image, ""))
        all_events.extend(events)
        print(f"[{index}/{len(images)}] {image.name}: events={len(events)} total={len(all_events)} fallback_time={fallback_hhmm_by_image.get(image, '')}")

    event_rows = []
    for event in all_events:
        row = asdict(event)
        row["event_time"] = event.event_time.strftime("%Y/%m/%d %H:%M:%S")
        event_rows.append(row)
    write_csv(DATA_DIR / f"{RUN_DATE}_base_capture_paddle_events.csv", event_rows)

    latest: dict[tuple[str, int, int], Event] = {}
    for event in all_events:
        key = (event.target_server, event.x, event.y)
        if key not in latest or event.event_time > latest[key].event_time:
            latest[key] = event

    values = read_sheet_csv(args.sheet_csv)
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
        if not re.search(r"[A-Za-z]", event.owner_for_sheet):
            review_rows.append(
                {
                    "reason": "low_confidence_owner_no_letter",
                    "target_server": key[0],
                    "x": key[1],
                    "y": key[2],
                    "sheet_row": row_index,
                    "existing_owner": existing_owner,
                    "owner_for_sheet": event.owner_for_sheet,
                    "event_time": event.event_time.strftime("%Y/%m/%d %H:%M:%S"),
                    "image": event.image,
                    "source_text": event.source_text,
                }
            )
            continue
        if existing_type and existing_type != event.kind_sheet:
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
                    "existing_owner": existing_owner,
                    "owner_for_sheet": event.owner_for_sheet,
                    "image": event.image,
                    "source_text": event.source_text,
                }
            )
            continue
        update = event_to_row(event)
        ranges[f"C{row_index}:E{row_index}"] = [[update["type"], update["owner"], update["acquired_at"]]]
        ranges[f"L{row_index}:L{row_index}"] = [[update["memo"].replace("Dropbox赤字OCR", "Dropbox PaddleOCR")]]
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

    write_csv(DATA_DIR / f"{RUN_DATE}_base_capture_paddle_sheet_updates.csv", update_rows)
    write_csv(DATA_DIR / f"{RUN_DATE}_base_capture_paddle_review.csv", review_rows)
    (DATA_DIR / f"{RUN_DATE}_base_capture_paddle_ranges.json").write_text(
        json.dumps(ranges, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"images={len(images)} events={len(all_events)} latest_targets={len(latest)} updates={len(update_rows)} review={len(review_rows)} seconds={time.perf_counter()-started:.1f}")
    print(DATA_DIR / f"{RUN_DATE}_base_capture_paddle_events.csv")
    print(DATA_DIR / f"{RUN_DATE}_base_capture_paddle_sheet_updates.csv")
    print(DATA_DIR / f"{RUN_DATE}_base_capture_paddle_review.csv")
    print(DATA_DIR / f"{RUN_DATE}_base_capture_paddle_ranges.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
