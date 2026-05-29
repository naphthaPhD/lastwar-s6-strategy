#!/usr/bin/env python3
"""
Extract likely-new chat content from a scrolling game chat video.

This script intentionally does not run OCR. It prepares a small set of
OCR-friendly crops so a later OpenAI API step can spend tokens only on frames
that are likely to contain newly appeared chat lines.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import cv2
import numpy as np


@dataclass(frozen=True)
class Roi:
    """Chat area definition. Values are pixels unless relative=True."""

    x: float
    y: float
    width: float
    height: float
    relative: bool = False


@dataclass(frozen=True)
class DiffConfig:
    """Thresholds for frame-to-frame change detection."""

    threshold: float
    min_changed_pixels_ratio: float
    save_debug_diff: bool


@dataclass(frozen=True)
class PreprocessConfig:
    """OCR-oriented image cleanup settings."""

    scale: float
    threshold_method: str
    adaptive_block_size: int
    adaptive_c: int


@dataclass(frozen=True)
class DedupeConfig:
    """Visual line de-duplication settings."""

    enabled: bool
    line_min_height: int
    line_padding: int
    hash_size: int
    hamming_threshold: int
    ignore_top_ratio: float
    ignore_bottom_ratio: float


@dataclass(frozen=True)
class AppConfig:
    """Fully parsed runtime configuration."""

    input_video: Path
    output_dir: Path
    ffmpeg_binary: str
    fps: int
    roi: Roi
    diff: DiffConfig
    preprocess: PreprocessConfig
    dedupe: DedupeConfig


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract OCR-ready crops for new chat events in a scrolling mp4."
    )
    parser.add_argument(
        "--config",
        default="config.json",
        help="Path to config JSON. Defaults to config.json.",
    )
    parser.add_argument(
        "--input",
        dest="input_video",
        help="Override input_video in config.",
    )
    parser.add_argument(
        "--output-dir",
        help="Override output_dir in config.",
    )
    parser.add_argument(
        "--keep-frames",
        action="store_true",
        help="Keep all extracted 1fps frames. Default is also to keep them because frames/ is a required output.",
    )
    return parser.parse_args()


def load_config(config_path: Path, args: argparse.Namespace) -> AppConfig:
    """Load JSON config and apply command-line overrides."""

    config_path = config_path.resolve()
    config_dir = config_path.parent

    # utf-8-sig keeps Windows PowerShell-created JSON files usable even when
    # they contain a UTF-8 BOM.
    with config_path.open("r", encoding="utf-8-sig") as f:
        raw = json.load(f)

    input_video = resolve_config_path(args.input_video or raw.get("input_video", "input.mp4"), config_dir)
    output_dir = resolve_config_path(args.output_dir or raw.get("output_dir", "."), config_dir)
    ffmpeg_binary = str(raw.get("ffmpeg_binary", "ffmpeg"))
    fps = int(raw.get("fps", 1))

    roi_raw = raw["roi"]
    roi = Roi(
        x=float(roi_raw["x"]),
        y=float(roi_raw["y"]),
        width=float(roi_raw["width"]),
        height=float(roi_raw["height"]),
        relative=bool(roi_raw.get("relative", False)),
    )

    diff_raw = raw.get("diff", {})
    diff = DiffConfig(
        threshold=float(diff_raw.get("threshold", 8.0)),
        min_changed_pixels_ratio=float(diff_raw.get("min_changed_pixels_ratio", 0.002)),
        save_debug_diff=bool(diff_raw.get("save_debug_diff", True)),
    )

    prep_raw = raw.get("preprocess", {})
    preprocess = PreprocessConfig(
        scale=float(prep_raw.get("scale", 2.0)),
        threshold_method=str(prep_raw.get("threshold_method", "otsu")),
        adaptive_block_size=int(prep_raw.get("adaptive_block_size", 31)),
        adaptive_c=int(prep_raw.get("adaptive_c", 7)),
    )

    dedupe_raw = raw.get("dedupe", {})
    dedupe = DedupeConfig(
        enabled=bool(dedupe_raw.get("enabled", True)),
        line_min_height=int(dedupe_raw.get("line_min_height", 12)),
        line_padding=int(dedupe_raw.get("line_padding", 4)),
        hash_size=int(dedupe_raw.get("hash_size", 16)),
        hamming_threshold=int(dedupe_raw.get("hamming_threshold", 6)),
        ignore_top_ratio=float(dedupe_raw.get("ignore_top_ratio", 0.0)),
        ignore_bottom_ratio=float(dedupe_raw.get("ignore_bottom_ratio", 0.0)),
    )

    return AppConfig(
        input_video=input_video,
        output_dir=output_dir,
        ffmpeg_binary=ffmpeg_binary,
        fps=fps,
        roi=roi,
        diff=diff,
        preprocess=preprocess,
        dedupe=dedupe,
    )


def resolve_config_path(value: str | Path, config_dir: Path) -> Path:
    """Resolve relative paths from the config file location."""

    path = Path(value)
    if path.is_absolute():
        return path
    return config_dir / path


def require_ffmpeg(ffmpeg_binary: str) -> None:
    """Fail early with a clear message if ffmpeg is not available."""

    # Accept either a command on PATH ("ffmpeg") or an explicit executable path.
    if Path(ffmpeg_binary).exists():
        return
    if shutil.which(ffmpeg_binary) is None:
        raise RuntimeError(
            f"ffmpeg was not found: {ffmpeg_binary}. Install ffmpeg or set ffmpeg_binary in config.json."
        )


def ensure_output_dirs(output_dir: Path) -> dict[str, Path]:
    """Create the required output folders."""

    paths = {
        "frames": output_dir / "frames",
        "cropped": output_dir / "cropped",
        "diff": output_dir / "diff",
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths


def extract_frames_with_ffmpeg(
    ffmpeg_binary: str, input_video: Path, frames_dir: Path, fps: int
) -> None:
    """Use ffmpeg to extract one image per second by default."""

    if not input_video.exists():
        raise FileNotFoundError(f"Input video does not exist: {input_video}")

    output_pattern = str(frames_dir / "frame_%04d.png")
    command = [
        ffmpeg_binary,
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(input_video),
        "-vf",
        f"fps={fps}",
        "-start_number",
        "0",
        output_pattern,
    ]
    subprocess.run(command, check=True)


def iter_frame_files(frames_dir: Path) -> Iterable[Path]:
    """Return extracted frame files in chronological order."""

    return sorted(frames_dir.glob("frame_*.png"))


def parse_frame_number(frame_path: Path) -> int:
    """Extract the numeric part from frame_0012.png."""

    return int(frame_path.stem.split("_")[-1])


def resolve_roi(roi: Roi, image_shape: tuple[int, int, int]) -> tuple[int, int, int, int]:
    """Convert configured ROI to safe pixel coordinates."""

    image_h, image_w = image_shape[:2]
    if roi.relative:
        x = int(round(roi.x * image_w))
        y = int(round(roi.y * image_h))
        width = int(round(roi.width * image_w))
        height = int(round(roi.height * image_h))
    else:
        x = int(round(roi.x))
        y = int(round(roi.y))
        width = int(round(roi.width))
        height = int(round(roi.height))

    x = max(0, min(x, image_w - 1))
    y = max(0, min(y, image_h - 1))
    width = max(1, min(width, image_w - x))
    height = max(1, min(height, image_h - y))
    return x, y, width, height


def crop_roi(frame: np.ndarray, roi: Roi) -> np.ndarray:
    """Crop the chat area from a full video frame."""

    x, y, width, height = resolve_roi(roi, frame.shape)
    return frame[y : y + height, x : x + width]


def preprocess_for_ocr(crop: np.ndarray, config: PreprocessConfig) -> np.ndarray:
    """Create an OCR-friendly grayscale, binarized, enlarged crop."""

    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)

    # A small blur stabilizes thresholding against compression noise.
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    method = config.threshold_method.lower()
    if method == "adaptive":
        block_size = config.adaptive_block_size
        if block_size % 2 == 0:
            block_size += 1
        binary = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            block_size,
            config.adaptive_c,
        )
    elif method == "simple":
        _, binary = cv2.threshold(gray, 160, 255, cv2.THRESH_BINARY)
    else:
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    if config.scale != 1.0:
        binary = cv2.resize(
            binary,
            None,
            fx=config.scale,
            fy=config.scale,
            interpolation=cv2.INTER_CUBIC,
        )
    return binary


def calculate_absdiff(
    previous_gray: np.ndarray | None, current_crop: np.ndarray, config: DiffConfig
) -> tuple[bool, float, float, np.ndarray | None, np.ndarray]:
    """Measure visual change from the previous ROI with cv2.absdiff."""

    current_gray = cv2.cvtColor(current_crop, cv2.COLOR_BGR2GRAY)
    if previous_gray is None:
        return True, 999.0, 1.0, None, current_gray

    if previous_gray.shape != current_gray.shape:
        previous_gray = cv2.resize(previous_gray, (current_gray.shape[1], current_gray.shape[0]))

    diff_image = cv2.absdiff(previous_gray, current_gray)
    mean_diff = float(np.mean(diff_image))
    changed_ratio = float(np.count_nonzero(diff_image > 25) / diff_image.size)
    is_changed = (
        mean_diff >= config.threshold
        and changed_ratio >= config.min_changed_pixels_ratio
    )
    return is_changed, mean_diff, changed_ratio, diff_image, current_gray


def line_segments(binary_image: np.ndarray, config: DedupeConfig) -> list[tuple[int, int]]:
    """Find likely text-line vertical ranges in a binarized crop."""

    height = binary_image.shape[0]
    start_y = int(height * config.ignore_top_ratio)
    end_y = int(height * (1.0 - config.ignore_bottom_ratio))
    work = binary_image[start_y:end_y, :]

    # Text may be dark-on-light after thresholding. Invert so text is foreground.
    foreground = 255 - work
    row_activity = np.count_nonzero(foreground > 0, axis=1)
    active_rows = row_activity > max(3, int(binary_image.shape[1] * 0.01))

    segments: list[tuple[int, int]] = []
    run_start: int | None = None
    for index, active in enumerate(active_rows):
        if active and run_start is None:
            run_start = index
        elif not active and run_start is not None:
            add_segment(segments, run_start + start_y, index + start_y, height, config)
            run_start = None

    if run_start is not None:
        add_segment(segments, run_start + start_y, len(active_rows) + start_y, height, config)

    return merge_close_segments(segments, max_gap=config.line_padding * 2)


def add_segment(
    segments: list[tuple[int, int]],
    start: int,
    end: int,
    image_height: int,
    config: DedupeConfig,
) -> None:
    """Append a padded segment if it is large enough to be a chat line."""

    if end - start < config.line_min_height:
        return
    padded_start = max(0, start - config.line_padding)
    padded_end = min(image_height, end + config.line_padding)
    segments.append((padded_start, padded_end))


def merge_close_segments(segments: list[tuple[int, int]], max_gap: int) -> list[tuple[int, int]]:
    """Merge nearby text ranges so one chat line does not split into fragments."""

    if not segments:
        return []
    merged = [segments[0]]
    for start, end in segments[1:]:
        prev_start, prev_end = merged[-1]
        if start - prev_end <= max_gap:
            merged[-1] = (prev_start, max(prev_end, end))
        else:
            merged.append((start, end))
    return merged


def average_hash(image: np.ndarray, hash_size: int) -> np.ndarray:
    """Create a compact visual fingerprint for a line image."""

    resized = cv2.resize(image, (hash_size, hash_size), interpolation=cv2.INTER_AREA)
    return resized > resized.mean()


def hamming_distance(hash_a: np.ndarray, hash_b: np.ndarray) -> int:
    """Count bit differences between two boolean image hashes."""

    return int(np.count_nonzero(hash_a != hash_b))


def detect_new_line_hashes(
    binary_crop: np.ndarray,
    seen_hashes: list[np.ndarray],
    config: DedupeConfig,
) -> tuple[int, list[dict[str, Any]]]:
    """Detect line images that have not appeared in earlier saved frames."""

    if not config.enabled:
        return 1, []

    new_lines: list[dict[str, Any]] = []
    segments = line_segments(binary_crop, config)
    for start_y, end_y in segments:
        line_image = binary_crop[start_y:end_y, :]
        line_hash = average_hash(line_image, config.hash_size)

        duplicate = any(
            hamming_distance(line_hash, existing) <= config.hamming_threshold
            for existing in seen_hashes
        )
        if duplicate:
            continue

        seen_hashes.append(line_hash)
        new_lines.append({"y_start": start_y, "y_end": end_y})

    return len(new_lines), new_lines


def write_image(path: Path, image: np.ndarray) -> None:
    """Write an image and fail loudly if OpenCV cannot encode it."""

    ok = cv2.imwrite(str(path), image)
    if not ok:
        raise RuntimeError(f"Failed to write image: {path}")


def build_metadata_record(
    frame_path: Path,
    crop_path: Path | None,
    diff_path: Path | None,
    timestamp_sec: int,
    new_content_detected: bool,
    mean_diff: float,
    changed_pixels_ratio: float,
    new_line_count: int,
    new_line_boxes: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build one log entry. This is the future OCR integration boundary."""

    record: dict[str, Any] = {
        "frame": frame_path.name,
        "timestamp_sec": timestamp_sec,
        "new_content_detected": new_content_detected,
        "crop_file": crop_path.name if crop_path else None,
        "mean_absdiff": round(mean_diff, 4),
        "changed_pixels_ratio": round(changed_pixels_ratio, 6),
        "new_line_count": new_line_count,
        "new_line_boxes": new_line_boxes,
    }
    if diff_path is not None:
        record["diff_file"] = diff_path.name
    return record


def process_frames(config: AppConfig, paths: dict[str, Path]) -> list[dict[str, Any]]:
    """Crop, diff, de-dupe, preprocess, and save useful frames."""

    metadata: list[dict[str, Any]] = []
    previous_gray: np.ndarray | None = None
    seen_hashes: list[np.ndarray] = []

    for frame_path in iter_frame_files(paths["frames"]):
        frame_number = parse_frame_number(frame_path)
        timestamp_sec = int(round(frame_number / config.fps))

        frame = cv2.imread(str(frame_path))
        if frame is None:
            raise RuntimeError(f"OpenCV could not read frame: {frame_path}")

        crop = crop_roi(frame, config.roi)
        changed, mean_diff, changed_ratio, diff_image, previous_gray_next = calculate_absdiff(
            previous_gray, crop, config.diff
        )
        previous_gray = previous_gray_next

        processed: np.ndarray | None = None
        new_line_count = 0
        new_line_boxes: list[dict[str, Any]] = []
        if changed:
            processed = preprocess_for_ocr(crop, config.preprocess)
            new_line_count, new_line_boxes = detect_new_line_hashes(
                processed, seen_hashes, config.dedupe
            )
        new_content_detected = changed and new_line_count > 0

        crop_path: Path | None = None
        diff_path: Path | None = None
        if new_content_detected:
            crop_path = paths["cropped"] / f"crop_{frame_number:04d}.png"
            if processed is None:
                raise RuntimeError("Internal error: processed crop is missing.")
            write_image(crop_path, processed)

            if config.diff.save_debug_diff and diff_image is not None:
                diff_path = paths["diff"] / f"diff_{frame_number:04d}.png"
                write_image(diff_path, diff_image)

        metadata.append(
            build_metadata_record(
                frame_path=frame_path,
                crop_path=crop_path,
                diff_path=diff_path,
                timestamp_sec=timestamp_sec,
                new_content_detected=new_content_detected,
                mean_diff=mean_diff,
                changed_pixels_ratio=changed_ratio,
                new_line_count=new_line_count if new_content_detected else 0,
                new_line_boxes=new_line_boxes if new_content_detected else [],
            )
        )

    return metadata


def save_metadata(output_dir: Path, metadata: list[dict[str, Any]]) -> None:
    """Write metadata.json as UTF-8 JSON."""

    metadata_path = output_dir / "metadata.json"
    with metadata_path.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main() -> int:
    args = parse_args()
    config = load_config(Path(args.config), args)

    require_ffmpeg(config.ffmpeg_binary)
    paths = ensure_output_dirs(config.output_dir)
    extract_frames_with_ffmpeg(
        config.ffmpeg_binary, config.input_video, paths["frames"], config.fps
    )
    metadata = process_frames(config, paths)
    save_metadata(config.output_dir, metadata)

    saved = sum(1 for record in metadata if record["new_content_detected"])
    print(
        json.dumps(
            {
                "frames_scanned": len(metadata),
                "crops_saved": saved,
                "metadata": str(config.output_dir / "metadata.json"),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
