#!/usr/bin/env python3
from __future__ import annotations

import json

from google.oauth2 import service_account
from googleapiclient.discovery import build


SPREADSHEETS = {
    "12u": "12uNW9XphH2zSX4h5BzjSd-OON9r5AckAuNCwQTbY79g",
    "1oK2": "1oK2tebQRs9RaSsrM-Oo9lynAjbt4loV82GjS8a3dPrQ",
}
DEFAULT_CREDENTIALS = "/Users/mba2025/.config/gptcodex/credentials-sub.json"
KEY = "#534:H-19"
VALUES = [
    ["漁場", "59U", ""],
]
MEMO = (
    "手動修正 2026/06/07 / #534:H-19 / "
    "誤混入修正: #534:C-7 OCR (#534 X:299 Y:199, 476C) がH-19へ重複反映されていたため復元 / "
    "根拠: data/2026-06-01_fishery_vertical_screenshot_import.csv IMG_1563.PNG #534[59U] H-19"
)


def main() -> int:
    creds = service_account.Credentials.from_service_account_file(
        DEFAULT_CREDENTIALS,
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    service = build("sheets", "v4", credentials=creds, cache_discovery=False)
    changed = {}
    for name, spreadsheet_id in SPREADSHEETS.items():
        values = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range="管理表たたき!A1:T2500",
        ).execute().get("values", [])
        row_number = None
        for index, row in enumerate(values, start=1):
            padded = row + [""] * 20
            if padded[19].strip().upper() == KEY:
                row_number = index
                break
        if not row_number:
            raise RuntimeError(f"{name}: key not found {KEY}")
        body = {
            "valueInputOption": "USER_ENTERED",
            "data": [
                {"range": f"管理表たたき!C{row_number}:E{row_number}", "values": VALUES},
                {"range": f"管理表たたき!L{row_number}:L{row_number}", "values": [[MEMO]]},
            ],
        }
        service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
        changed[name] = {"row": row_number, "key": KEY, "owner": "59U"}
    print(json.dumps(changed, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
