#!/usr/bin/env python3
"""Audit whether S6#534 full-map cells reflect 管理表たたき ownership."""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build


SPREADSHEET_ID = "1oK2tebQRs9RaSsrM-Oo9lynAjbt4loV82GjS8a3dPrQ"
DEFAULT_CREDENTIALS = "/Users/mba2025/.config/gptcodex/credentials-sub.json"

SHEET_MANAGEMENT = "管理表たたき"
SHEET_TEMPLATE = "マップ表示テンプレ"
SHEET_FULL_MAP = "全体マップ"
MAP_RANGE = "A1:DR135"

FULL_MAP_BLOCKS = [
    (6, 46, 1, 41, "#534"),
    (6, 46, 42, 81, "#509"),
    (6, 46, 82, 122, "#503"),
    (49, 89, 1, 41, "#476"),
    (49, 89, 82, 122, "#480"),
    (92, 132, 1, 41, "#523"),
    (92, 132, 42, 81, "#511"),
    (92, 132, 82, 122, "#440"),
]

UNOWNED = {"", "unknown", "未取得", "未登録", "中立", "中立/未登録"}


def get_values(service, spreadsheet_id: str, range_name: str) -> list[list[str]]:
    response = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=range_name)
        .execute()
    )
    return response.get("values", [])


def normalize_coord(value: str) -> str:
    text = str(value or "").strip()
    if "-" not in text:
        return ""
    left, right = text.split("-", 1)
    if len(left) != 1 or left.upper() not in "ABCDEFGHIJK":
        return ""
    try:
        number = int(right)
    except ValueError:
        return ""
    if number < 1 or number > 21:
        return ""
    return f"{left.upper()}-{number}"


def normalize_key(value: str) -> str:
    return str(value or "").strip().upper()


def area_for_cell(row_number: int, column_number: int) -> str:
    for start_row, end_row, start_column, end_column, area in FULL_MAP_BLOCKS:
        if start_row <= row_number <= end_row and start_column <= column_number <= end_column:
            return area
    return ""


def expected_display(row: dict[str, str]) -> str:
    owner = row.get("連盟", "").strip()
    node_type = row.get("種別", "").strip()
    status = row.get("状態", "").strip()
    memo = row.get("メモ", "").strip()
    if "破壊" in node_type or "破壊" in owner or "破壊" in status or ("破壊" in memo and not owner):
        return "破壊"
    if node_type == "交易地":
        return "交易地"
    return owner or row.get("座標", "").strip()


def is_owned(row: dict[str, str]) -> bool:
    owner = row.get("連盟", "").strip()
    if owner in UNOWNED:
        return False
    return bool(owner)


def build_management(rows: list[list[str]]) -> tuple[dict[str, dict[str, str]], Counter, dict[str, list[int]]]:
    headers = [str(value or "").strip() for value in rows[0]]
    result: dict[str, dict[str, str]] = {}
    duplicate_rows: dict[str, list[int]] = defaultdict(list)
    counters: Counter = Counter()
    for row_number, raw in enumerate(rows[2:], start=3):
        row = {header: raw[index] if index < len(raw) else "" for index, header in enumerate(headers)}
        key = normalize_key(row.get("位置キー", ""))
        if not key:
            area = row.get("エリア", "").strip()
            coord = normalize_coord(row.get("座標", ""))
            key = normalize_key(f"{area}:{coord}") if area and coord else ""
        if not key or ":" not in key:
            counters["no_key"] += 1
            continue
        row["_row_number"] = str(row_number)
        duplicate_rows[key].append(row_number)
        result[key] = row
        counters["management_keys"] += 1
        if is_owned(row):
            counters["owned_keys"] += 1
    return result, counters, duplicate_rows


def build_template_index(template_values: list[list[str]]) -> tuple[dict[str, tuple[int, int]], Counter]:
    result: dict[str, tuple[int, int]] = {}
    counters: Counter = Counter()
    for row_index, row in enumerate(template_values):
        row_number = row_index + 1
        for column_index, value in enumerate(row):
            column_number = column_index + 1
            coord = normalize_coord(value)
            if not coord:
                continue
            area = area_for_cell(row_number, column_number)
            if not area:
                counters["coordinates_outside_blocks"] += 1
                continue
            key = normalize_key(f"{area}:{coord}")
            result[key] = (row_number, column_number)
            counters["template_keys"] += 1
    return result, counters


def cell_value(values: list[list[str]], row_number: int, column_number: int) -> str:
    row_index = row_number - 1
    column_index = column_number - 1
    if row_index >= len(values) or column_index >= len(values[row_index]):
        return ""
    return str(values[row_index][column_index] or "").strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--credentials", default=DEFAULT_CREDENTIALS)
    parser.add_argument("--spreadsheet-id", default=SPREADSHEET_ID)
    parser.add_argument("--out", default="data/2026-06-06_s6_full_map_reflection_audit.csv")
    args = parser.parse_args()

    credentials = service_account.Credentials.from_service_account_file(
        args.credentials,
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
    )
    service = build("sheets", "v4", credentials=credentials, cache_discovery=False)

    management_rows = get_values(service, args.spreadsheet_id, f"{SHEET_MANAGEMENT}!A1:T")
    template_values = get_values(service, args.spreadsheet_id, f"{SHEET_TEMPLATE}!{MAP_RANGE}")
    full_map_values = get_values(service, args.spreadsheet_id, f"{SHEET_FULL_MAP}!{MAP_RANGE}")

    management, management_counters, duplicate_rows = build_management(management_rows)
    template_index, template_counters = build_template_index(template_values)

    findings = []
    counters = Counter()
    counters.update(management_counters)
    counters.update(template_counters)

    for key, row in sorted(management.items()):
        if not is_owned(row):
            continue
        expected = expected_display(row)
        map_position = template_index.get(key)
        if not map_position:
            findings.append({
                "issue": "owned_key_not_in_template",
                "key": key,
                "management_row": row.get("_row_number", ""),
                "type": row.get("種別", ""),
                "owner": row.get("連盟", ""),
                "expected": expected,
                "full_map": "",
                "map_row": "",
                "map_column": "",
                "memo": row.get("メモ", ""),
            })
            counters["owned_key_not_in_template"] += 1
            continue
        row_number, column_number = map_position
        actual = cell_value(full_map_values, row_number, column_number)
        if actual != expected:
            findings.append({
                "issue": "full_map_value_mismatch",
                "key": key,
                "management_row": row.get("_row_number", ""),
                "type": row.get("種別", ""),
                "owner": row.get("連盟", ""),
                "expected": expected,
                "full_map": actual,
                "map_row": row_number,
                "map_column": column_number,
                "memo": row.get("メモ", ""),
            })
            counters["full_map_value_mismatch"] += 1
        else:
            counters["owned_reflected"] += 1

    for key, rows in sorted(duplicate_rows.items()):
        if len(rows) <= 1:
            continue
        findings.append({
            "issue": "duplicate_management_key",
            "key": key,
            "management_row": ",".join(str(row) for row in rows),
            "type": "",
            "owner": "",
            "expected": "",
            "full_map": "",
            "map_row": "",
            "map_column": "",
            "memo": "Later row wins in Apps Script map generation.",
        })
        counters["duplicate_management_key"] += 1

    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "issue",
                "key",
                "management_row",
                "type",
                "owner",
                "expected",
                "full_map",
                "map_row",
                "map_column",
                "memo",
            ],
        )
        writer.writeheader()
        writer.writerows(findings)

    for key in sorted(counters):
        print(f"{key}: {counters[key]}")
    print(f"findings_csv: {output_path}")


if __name__ == "__main__":
    main()
