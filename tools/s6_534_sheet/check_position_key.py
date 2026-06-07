#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from google.oauth2 import service_account
from googleapiclient.discovery import build


SPREADSHEETS = {
    "src_12u": "12uNW9XphH2zSX4h5BzjSd-OON9r5AckAuNCwQTbY79g",
    "dst_1oK2": "1oK2tebQRs9RaSsrM-Oo9lynAjbt4loV82GjS8a3dPrQ",
}
DEFAULT_CREDENTIALS = "/Users/mba2025/.config/gptcodex/credentials-sub.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("key")
    parser.add_argument("--contains", action="store_true")
    parser.add_argument("--credentials", default=DEFAULT_CREDENTIALS)
    args = parser.parse_args()

    creds = service_account.Credentials.from_service_account_file(
        args.credentials,
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    service = build("sheets", "v4", credentials=creds, cache_discovery=False)
    output = {}
    for name, spreadsheet_id in SPREADSHEETS.items():
        values = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range="管理表たたき!A1:T2500",
        ).execute().get("values", [])
        rows = []
        for row_index, row in enumerate(values, start=1):
            padded = row + [""] * 20
            matched = padded[19].strip().upper() == args.key.upper()
            if args.contains:
                matched = args.key in " ".join(padded)
            if matched:
                rows.append({
                    "row": row_index,
                    "coord": padded[0],
                    "type": padded[2],
                    "owner": padded[3],
                    "acquired_at": padded[4],
                    "memo": padded[11],
                    "area": padded[18],
                    "key": padded[19],
                })
        output[name] = rows
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
