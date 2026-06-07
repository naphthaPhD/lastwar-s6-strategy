#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter

from google.oauth2 import service_account
from googleapiclient.discovery import build


SPREADSHEET_ID = "12uNW9XphH2zSX4h5BzjSd-OON9r5AckAuNCwQTbY79g"
DEFAULT_CREDENTIALS = "/Users/mba2025/.config/gptcodex/credentials-sub.json"


def main() -> int:
    creds = service_account.Credentials.from_service_account_file(
        DEFAULT_CREDENTIALS,
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    service = build("sheets", "v4", credentials=creds, cache_discovery=False)
    values = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="管理表たたき!A1:T2500",
    ).execute().get("values", [])
    rows = []
    for row_number, row in enumerate(values[1:], start=2):
        padded = row + [""] * 20
        if padded[2] == "都市" and padded[3] == "破壊":
            rows.append({
                "row": row_number,
                "key": padded[19],
                "area": padded[18],
                "coord": padded[0],
                "time": padded[4],
                "memo": padded[11],
            })
    output = {
        "total": len(rows),
        "by_area": dict(Counter(row["area"] for row in rows)),
        "rows_534": [row for row in rows if row["area"] == "#534"],
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
