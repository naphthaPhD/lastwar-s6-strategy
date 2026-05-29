#!/usr/bin/env python3
"""
Run OpenAI OCR over preprocessed chat crops and append game-event JSON results.

Expected flow:
1. Run chat_event_preprocessor.py to create cropped/*.png and metadata.json.
2. Run this worker from tools/chat_event_preprocessor:
   python ocr_worker.py

The worker uses OPENAI_API_KEY from the environment and skips crops that already
have a successful record in events.json unless --force is supplied.
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from openai import OpenAI


DEFAULT_MODEL = "gpt-5.4-mini"
DEFAULT_MAX_OUTPUT_TOKENS = 800
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


@dataclass(frozen=True)
class CropJob:
    """One OCR job linked to one metadata row."""

    crop_path: Path
    metadata_record: dict[str, Any]


def eprint(message: str) -> None:
    """Print operational logs to stderr so stdout can stay machine-readable."""

    print(message, file=sys.stderr)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="OCR cropped chat images with the OpenAI Responses API."
    )
    parser.add_argument("--cropped-dir", type=Path, default=Path("cropped"))
    parser.add_argument("--metadata", type=Path, default=Path("metadata.json"))
    parser.add_argument("--prompt", type=Path, default=Path("prompt.txt"))
    parser.add_argument("--events", type=Path, default=Path("events.json"))
    parser.add_argument("--errors", type=Path, default=Path("ocr_errors.jsonl"))
    parser.add_argument(
        "--model",
        default=os.environ.get("OPENAI_OCR_MODEL", DEFAULT_MODEL),
        help="OpenAI model. Defaults to OPENAI_OCR_MODEL or gpt-5.4-mini.",
    )
    parser.add_argument(
        "--detail",
        choices=["low", "high", "auto"],
        default="low",
        help="Image detail. low is the default to reduce OCR cost.",
    )
    parser.add_argument("--max-output-tokens", type=int, default=DEFAULT_MAX_OUTPUT_TOKENS)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--retry-delay", type=float, default=2.0)
    parser.add_argument("--sleep", type=float, default=0.0)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--force", action="store_true", help="Reprocess successful crops.")
    return parser.parse_args()


def resolve_runtime_paths(args: argparse.Namespace) -> argparse.Namespace:
    """Resolve relative paths from this script directory, not the caller cwd."""

    base_dir = Path(__file__).resolve().parent
    for attr in ("cropped_dir", "metadata", "prompt", "events", "errors"):
        value = getattr(args, attr)
        if not value.is_absolute():
            setattr(args, attr, base_dir / value)
    return args


def load_json_array(path: Path) -> list[dict[str, Any]]:
    """Load a JSON array file. Missing files are treated as empty arrays."""

    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON array.")
    return data


def save_json_array(path: Path, records: list[dict[str, Any]]) -> None:
    """Atomically write a JSON array."""

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
        f.write("\n")
    tmp_path.replace(path)


def append_error(path: Path, record: dict[str, Any]) -> None:
    """Append one failure record as JSON Lines."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")))
        f.write("\n")


def load_prompt(path: Path) -> str:
    with path.open("r", encoding="utf-8-sig") as f:
        return f.read().strip()


def data_url(path: Path) -> str:
    """Encode an image as a data URL for Responses API image input."""

    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def metadata_jobs(metadata_path: Path, cropped_dir: Path) -> list[CropJob]:
    """Build OCR jobs from metadata.json, preserving frame order."""

    metadata = load_json_array(metadata_path)
    jobs: list[CropJob] = []
    for record in metadata:
        if not record.get("new_content_detected"):
            continue
        crop_name = record.get("crop_file")
        if not isinstance(crop_name, str):
            continue
        crop_path = cropped_dir / crop_name
        if crop_path.suffix.lower() not in IMAGE_EXTENSIONS:
            eprint(f"Skip unsupported image extension: {crop_path}")
            continue
        if not crop_path.exists():
            eprint(f"Skip missing crop linked from metadata: {crop_path}")
            continue
        jobs.append(CropJob(crop_path=crop_path, metadata_record=record))
    return sorted(jobs, key=lambda job: job.crop_path.name)


def successful_crop_files(events: list[dict[str, Any]]) -> set[str]:
    """Return crop_file values already OCRed successfully."""

    done: set[str] = set()
    for record in events:
        if record.get("status") == "ok" and isinstance(record.get("crop_file"), str):
            done.add(record["crop_file"])
    return done


def build_response_request(
    prompt: str,
    image_path: Path,
    model: str,
    detail: str,
    max_output_tokens: int,
) -> dict[str, Any]:
    """Build a minimal Responses API request."""

    return {
        "model": model,
        "input": [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {
                        "type": "input_image",
                        "image_url": data_url(image_path),
                        "detail": detail,
                    },
                ],
            }
        ],
        "text": {"format": {"type": "json_object"}},
        "max_output_tokens": max_output_tokens,
    }


def call_openai_with_retry(
    client: OpenAI,
    payload: dict[str, Any],
    retries: int,
    retry_delay: float,
) -> Any:
    """Call Responses API with exponential backoff."""

    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            return client.responses.create(**payload)
        except Exception as exc:  # SDK exceptions differ by version.
            last_error = exc
            if attempt >= retries:
                break
            delay = retry_delay * (2 ** (attempt - 1))
            eprint(f"OCR retry {attempt}/{retries - 1} after error: {exc}")
            time.sleep(delay)
    assert last_error is not None
    raise last_error


def parse_output_json(output_text: str) -> dict[str, Any]:
    """Validate model output as a JSON object with an events array."""

    parsed = json.loads(output_text)
    if not isinstance(parsed, dict):
        raise ValueError("OCR output JSON root is not an object.")
    events = parsed.get("events")
    if not isinstance(events, list):
        raise ValueError("OCR output JSON does not contain an events array.")
    return parsed


def build_success_record(
    job: CropJob,
    response: Any,
    ocr_json: dict[str, Any],
    model: str,
    elapsed_sec: float,
) -> dict[str, Any]:
    """Create the append record saved to events.json."""

    return {
        "status": "ok",
        "frame": job.metadata_record.get("frame"),
        "timestamp_sec": job.metadata_record.get("timestamp_sec"),
        "crop_file": job.crop_path.name,
        "model": model,
        "response_id": getattr(response, "id", None),
        "elapsed_sec": round(elapsed_sec, 3),
        "metadata": job.metadata_record,
        "ocr_json": ocr_json,
    }


def build_failure_record(
    job: CropJob,
    model: str,
    error: Exception,
    elapsed_sec: float,
) -> dict[str, Any]:
    """Create a compact failure log record."""

    return {
        "status": "error",
        "frame": job.metadata_record.get("frame"),
        "timestamp_sec": job.metadata_record.get("timestamp_sec"),
        "crop_file": job.crop_path.name,
        "model": model,
        "elapsed_sec": round(elapsed_sec, 3),
        "error": str(error),
    }


def main() -> int:
    args = resolve_runtime_paths(parse_args())

    if not os.environ.get("OPENAI_API_KEY"):
        eprint("OPENAI_API_KEY is not set. See .env.example.")
        return 2

    prompt = load_prompt(args.prompt)
    jobs = metadata_jobs(args.metadata, args.cropped_dir)
    existing_events = load_json_array(args.events)
    already_done = successful_crop_files(existing_events)

    if not args.force:
        jobs = [job for job in jobs if job.crop_path.name not in already_done]
    if args.limit is not None:
        jobs = jobs[: args.limit]

    if not jobs:
        eprint("No OCR jobs to run.")
        return 0

    client = OpenAI()
    records = existing_events
    ok_count = 0
    error_count = 0

    for index, job in enumerate(jobs, start=1):
        eprint(f"[{index}/{len(jobs)}] OCR {job.crop_path.name}")
        payload = build_response_request(
            prompt=prompt,
            image_path=job.crop_path,
            model=args.model,
            detail=args.detail,
            max_output_tokens=args.max_output_tokens,
        )

        started = time.time()
        try:
            response = call_openai_with_retry(
                client=client,
                payload=payload,
                retries=args.retries,
                retry_delay=args.retry_delay,
            )
            output_text = response.output_text
            ocr_json = parse_output_json(output_text)
            records.append(
                build_success_record(
                    job=job,
                    response=response,
                    ocr_json=ocr_json,
                    model=args.model,
                    elapsed_sec=time.time() - started,
                )
            )
            save_json_array(args.events, records)
            ok_count += 1
        except Exception as exc:
            error_record = build_failure_record(
                job=job,
                model=args.model,
                error=exc,
                elapsed_sec=time.time() - started,
            )
            append_error(args.errors, error_record)
            eprint(f"OCR failed for {job.crop_path.name}: {exc}")
            error_count += 1

        if args.sleep and index < len(jobs):
            time.sleep(args.sleep)

    print(
        json.dumps(
            {
                "jobs": len(jobs),
                "ok": ok_count,
                "errors": error_count,
                "events": str(args.events),
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
    )
    return 1 if error_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
