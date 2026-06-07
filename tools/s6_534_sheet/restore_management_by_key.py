#!/usr/bin/env python3
"""Restore S6 management rows from a source sheet by position key.

This intentionally matches rows by column T (位置キー), not by row number.
Only user-facing source fields C:E and L are written to the destination.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build


SOURCE_SPREADSHEET_ID = "12uNW9XphH2zSX4h5BzjSd-OON9r5AckAuNCwQTbY79g"
DESTINATION_SPREADSHEET_ID = "1oK2tebQRs9RaSsrM-Oo9lynAjbt4loV82GjS8a3dPrQ"
DEFAULT_CREDENTIALS = "/Users/mba2025/.config/gptcodex/credentials-sub.json"
SHEET_NAME = "管理表たたき"


def cell(row: list[str], index: int) -> str:
    return row[index] if index < len(row) else ""


def rows_by_key(rows: list[list[str]]) -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    for row_number, row in enumerate(rows[2:], start=3):
        key = cell(row, 19).strip().upper()
        if not key:
            continue
        result[key] = {
            "row_number": row_number,
            "values": [cell(row, i) for i in range(20)],
        }
    return result


def get_rows(service, spreadsheet_id: str) -> list[list[str]]:
    response = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=f"{SHEET_NAME}!A1:T2500")
        .execute()
    )
    return response.get("values", [])


def build_updates(source_rows: list[list[str]], destination_rows: list[list[str]]):
    source = rows_by_key(source_rows)
    destination = rows_by_key(destination_rows)
    counters: Counter[str] = Counter()
    updates: dict[str, list[list[str]]] = {}
    examples: list[dict[str, object]] = []

    for key, source_entry in sorted(source.items()):
        destination_entry = destination.get(key)
        if not destination_entry:
            counters["missing_key_in_destination"] += 1
            continue

        source_values = source_entry["values"]
        destination_values = destination_entry["values"]
        assert isinstance(source_values, list)
        assert isinstance(destination_values, list)
        destination_row = int(destination_entry["row_number"])

        source_type = str(source_values[2]).strip()
        source_owner = str(source_values[3]).strip()
        source_acquired_at = str(source_values[4]).strip()
        source_memo = str(source_values[11]).strip()

        destination_type = str(destination_values[2]).strip()
        destination_owner = str(destination_values[3]).strip()
        destination_acquired_at = str(destination_values[4]).strip()
        destination_memo = str(destination_values[11]).strip()

        should_update = False
        reasons: list[str] = []
        if source_type and source_type != destination_type:
            should_update = True
            reasons.append("type")
            counters["type_diff"] += 1
        if source_owner and source_owner != destination_owner:
            should_update = True
            reasons.append("owner")
            if destination_owner:
                counters["owner_diff"] += 1
            else:
                counters["blank_owner_restored"] += 1
        if source_acquired_at and source_acquired_at != destination_acquired_at:
            should_update = True
            reasons.append("acquired_at")
            counters["acquired_at_diff"] += 1
        if source_memo and source_memo != destination_memo:
            should_update = True
            reasons.append("memo")
            counters["memo_diff"] += 1

        if not should_update:
            counters["already_matching"] += 1
            continue

        updates[f"C{destination_row}:E{destination_row}"] = [
            [source_values[2], source_values[3], source_values[4]]
        ]
        updates[f"L{destination_row}:L{destination_row}"] = [[source_values[11]]]
        counters["rows_to_update"] += 1

        if len(examples) < 50:
            examples.append(
                {
                    "key": key,
                    "source_row": source_entry["row_number"],
                    "destination_row": destination_row,
                    "reasons": reasons,
                    "source_CDE": source_values[2:5],
                    "destination_CDE": destination_values[2:5],
                }
            )

    return updates, counters, examples


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--credentials", default=DEFAULT_CREDENTIALS)
    parser.add_argument("--source", default=SOURCE_SPREADSHEET_ID)
    parser.add_argument("--destination", default=DESTINATION_SPREADSHEET_ID)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--audit-out", default="/private/tmp/s6_restore_management_by_key_audit.json")
    args = parser.parse_args()

    credentials = service_account.Credentials.from_service_account_file(
        args.credentials,
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    service = build("sheets", "v4", credentials=credentials, cache_discovery=False)

    updates, counters, examples = build_updates(
        get_rows(service, args.source),
        get_rows(service, args.destination),
    )

    if args.apply and updates:
        items = list(updates.items())
        for start in range(0, len(items), 80):
            chunk = items[start : start + 80]
            service.spreadsheets().values().batchUpdate(
                spreadsheetId=args.destination,
                body={
                    "valueInputOption": "USER_ENTERED",
                    "data": [
                        {"range": f"{SHEET_NAME}!{range_name}", "values": values}
                        for range_name, values in chunk
                    ],
                },
            ).execute()
        counters["updated_ranges"] = len(updates)

    audit = {
        "mode": "apply" if args.apply else "dry_run",
        "source": args.source,
        "destination": args.destination,
        "updated_range_count": len(updates),
        "updated_row_count": len(updates) // 2,
        "counters": dict(counters),
        "examples": examples,
    }
    Path(args.audit_out).write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
