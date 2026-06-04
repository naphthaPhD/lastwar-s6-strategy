#!/usr/bin/env python3
"""
Extract red zombie-spawn event rows from a Last War screen recording.

The script uses OpenCV only. It samples an MP4 at a fixed FPS, detects red text
inside a configurable ROI, crops each detected red notification row, and writes
metadata compatible with tools/chat_event_preprocessor/ocr_worker.py.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np


@dataclass(frozen=True)
class Roi:
    x: int
    y: int
    width: int
    height: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract red zombie event row crops.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--fps", type=float, default=1.0)
    parser.add_argument("--roi-x", type=int, default=320)
    parser.add_argument("--roi-y", type=int, default=520)
    parser.add_argument("--roi-width", type=int, default=1760)
    parser.add_argument("--roi-height", type=int, default=2100)
    parser.add_argument("--min-red-pixels-per-line", type=int, default=70)
    parser.add_argument("--merge-y-gap", type=int, default=130)
    parser.add_argument("--min-box-area", type=int, default=5000)
    parser.add_argument("--padding-x", type=int, default=45)
    parser.add_argument("--padding-y", type=int, default=35)
    parser.add_argument(
        "--page-crops",
        action="store_true",
        help="Save one red-only ROI image per sampled frame instead of row crops.",
    )
    return parser.parse_args()


def clamp_roi(roi: Roi, frame: np.ndarray) -> Roi:
    h, w = frame.shape[:2]
    x = max(0, min(roi.x, w - 1))
    y = max(0, min(roi.y, h - 1))
    width = max(1, min(roi.width, w - x))
    height = max(1, min(roi.height, h - y))
    return Roi(x=x, y=y, width=width, height=height)


def red_mask(bgr: np.ndarray) -> np.ndarray:
    """Return a mask for red/pink UI text."""

    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    lower1 = np.array([0, 45, 120], dtype=np.uint8)
    upper1 = np.array([12, 255, 255], dtype=np.uint8)
    lower2 = np.array([165, 45, 120], dtype=np.uint8)
    upper2 = np.array([179, 255, 255], dtype=np.uint8)
    mask = cv2.inRange(hsv, lower1, upper1) | cv2.inRange(hsv, lower2, upper2)

    # Remove isolated pixels, then bridge characters on the same text row.
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    mask = cv2.dilate(mask, np.ones((5, 9), np.uint8), iterations=1)
    return mask


def merge_runs(runs: list[tuple[int, int]], max_gap: int) -> list[tuple[int, int]]:
    if not runs:
        return []
    merged = [runs[0]]
    for start, end in runs[1:]:
        prev_start, prev_end = merged[-1]
        if start - prev_end <= max_gap:
            merged[-1] = (prev_start, max(prev_end, end))
        else:
            merged.append((start, end))
    return merged


def y_runs(mask: np.ndarray, min_pixels: int, merge_gap: int) -> list[tuple[int, int]]:
    counts = np.count_nonzero(mask, axis=1)
    active = counts >= min_pixels
    runs: list[tuple[int, int]] = []
    start: int | None = None
    for y, is_active in enumerate(active):
        if is_active and start is None:
            start = y
        elif not is_active and start is not None:
            runs.append((start, y - 1))
            start = None
    if start is not None:
        runs.append((start, len(active) - 1))
    return merge_runs(runs, merge_gap)


def crop_boxes(
    frame: np.ndarray,
    roi: Roi,
    min_red_pixels_per_line: int,
    merge_y_gap: int,
    min_box_area: int,
    padding_x: int,
    padding_y: int,
) -> list[tuple[int, int, int, int, np.ndarray]]:
    region = frame[roi.y : roi.y + roi.height, roi.x : roi.x + roi.width]
    mask = red_mask(region)
    boxes: list[tuple[int, int, int, int, np.ndarray]] = []
    for y1, y2 in y_runs(mask, min_red_pixels_per_line, merge_y_gap):
        band = mask[y1 : y2 + 1, :]
        xs = np.where(np.count_nonzero(band, axis=0) > 0)[0]
        if xs.size == 0:
            continue
        x1 = int(xs.min())
        x2 = int(xs.max())
        gx1 = max(0, roi.x + x1 - padding_x)
        gy1 = max(0, roi.y + y1 - padding_y)
        gx2 = min(frame.shape[1], roi.x + x2 + padding_x)
        gy2 = min(frame.shape[0], roi.y + y2 + padding_y)
        if (gx2 - gx1) * (gy2 - gy1) < min_box_area:
            continue
        mask_crop = mask[max(0, y1 - padding_y) : min(mask.shape[0], y2 + padding_y),
                         max(0, x1 - padding_x) : min(mask.shape[1], x2 + padding_x)]
        boxes.append((gx1, gy1, gx2, gy2, mask_crop))
    return boxes


def crop_fingerprint(mask_crop: np.ndarray) -> str:
    resized = cv2.resize(mask_crop, (96, 32), interpolation=cv2.INTER_AREA)
    _, binary = cv2.threshold(resized, 8, 255, cv2.THRESH_BINARY)
    return hashlib.sha1(binary.tobytes()).hexdigest()


def ocr_friendly_crop(frame_crop: np.ndarray) -> np.ndarray:
    """Keep red text, convert it to black, and place it on white background."""

    mask = red_mask(frame_crop)
    result = np.full(frame_crop.shape[:2], 255, dtype=np.uint8)
    result[mask > 0] = 0
    result = cv2.dilate(result, np.ones((2, 2), np.uint8), iterations=1)
    return cv2.resize(result, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)


def ocr_friendly_red_page(region: np.ndarray) -> tuple[np.ndarray, int]:
    mask = red_mask(region)
    red_pixels = int(np.count_nonzero(mask))
    result = np.full(region.shape[:2], 255, dtype=np.uint8)
    result[mask > 0] = 0
    result = cv2.dilate(result, np.ones((2, 2), np.uint8), iterations=1)
    return cv2.resize(result, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC), red_pixels


def main() -> None:
    args = parse_args()
    out = args.output_dir
    crops_dir = out / "cropped"
    red_debug_dir = out / "red_debug"
    crops_dir.mkdir(parents=True, exist_ok=True)
    red_debug_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(args.input))
    if not cap.isOpened():
        raise FileNotFoundError(f"Cannot open video: {args.input}")
    native_fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / native_fps if native_fps else 0.0
    step = 1.0 / args.fps

    roi = Roi(args.roi_x, args.roi_y, args.roi_width, args.roi_height)
    metadata: list[dict[str, Any]] = []
    seen: set[str] = set()
    crop_index = 0
    timestamp = 0.0
    while timestamp <= duration + 0.001:
        cap.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)
        ok, frame = cap.read()
        if not ok:
            timestamp += step
            continue
        actual_roi = clamp_roi(roi, frame)
        if args.page_crops:
            region = frame[
                actual_roi.y : actual_roi.y + actual_roi.height,
                actual_roi.x : actual_roi.x + actual_roi.width,
            ]
            page, red_pixels = ocr_friendly_red_page(region)
            if red_pixels < args.min_box_area:
                timestamp += step
                continue
            crop_name = f"red_page_{crop_index:04d}.png"
            debug_name = f"debug_page_{crop_index:04d}.png"
            cv2.imwrite(str(crops_dir / crop_name), page)
            cv2.imwrite(str(red_debug_dir / debug_name), region)
            metadata.append(
                {
                    "frame": f"t_{int(round(timestamp)):04d}",
                    "timestamp_sec": int(round(timestamp)),
                    "new_content_detected": True,
                    "crop_file": crop_name,
                    "debug_file": debug_name,
                    "red_box": actual_roi.__dict__,
                    "red_pixels": red_pixels,
                }
            )
            crop_index += 1
            timestamp += step
            continue
        boxes = crop_boxes(
            frame,
            actual_roi,
            args.min_red_pixels_per_line,
            args.merge_y_gap,
            args.min_box_area,
            args.padding_x,
            args.padding_y,
        )
        for box_i, (x1, y1, x2, y2, mask_crop) in enumerate(boxes):
            fingerprint = crop_fingerprint(mask_crop)
            # Exact same row in consecutive static frames is common. Avoid broad
            # fuzzy de-dupe because a single digit can matter for this analysis.
            if fingerprint in seen:
                continue
            seen.add(fingerprint)
            crop = frame[y1:y2, x1:x2]
            crop_name = f"red_{crop_index:04d}.png"
            debug_name = f"debug_{crop_index:04d}.png"
            cv2.imwrite(str(crops_dir / crop_name), ocr_friendly_crop(crop))
            cv2.imwrite(str(red_debug_dir / debug_name), crop)
            metadata.append(
                {
                    "frame": f"t_{int(round(timestamp)):04d}_{box_i:02d}",
                    "timestamp_sec": int(round(timestamp)),
                    "new_content_detected": True,
                    "crop_file": crop_name,
                    "debug_file": debug_name,
                    "red_box": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
                    "fingerprint": fingerprint,
                }
            )
            crop_index += 1
        timestamp += step

    with (out / "metadata.json").open("w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
        f.write("\n")
    with (out / "config.json").open("w", encoding="utf-8") as f:
        json.dump(
            {
                "input_video": str(args.input),
                "fps": args.fps,
                "roi": roi.__dict__,
                "duration_sec": duration,
                "crops_saved": len(metadata),
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
        f.write("\n")
    print(json.dumps({"duration_sec": duration, "crops_saved": len(metadata)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
