#!/usr/bin/env python3
"""Rebuild the S6 full map from the destination management sheet.

The logic mirrors tools/s6_534_sheet/Code.gs closely enough for API repair:
template coordinates are resolved to management rows by position key, then the
visible map value, text color, bold state, white background, and note are written.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build


DESTINATION_SPREADSHEET_ID = "1oK2tebQRs9RaSsrM-Oo9lynAjbt4loV82GjS8a3dPrQ"
DEFAULT_CREDENTIALS = "/Users/mba2025/.config/gptcodex/credentials-sub.json"
MANAGEMENT_SHEET = "管理表たたき"
MAP_TEMPLATE_SHEET = "マップ表示テンプレ"
FULL_MAP_SHEET = "全体マップ"
PACT_SHEET = "連盟盟約状況"
FULL_MAP_RANGE = "A1:DR135"
BACKGROUND = "#ffffff"
COLORS = {
    "self": "#2563eb",
    "ally": "#16a34a",
    "enemy": "#dc2626",
    "trade": "#020617",
    "destroyed": "#6b7280",
    "unowned": "#000000",
}
SELF_SERVERS = {"#534"}
ALLY_SERVERS = {"#509", "#440", "#511"}
ENEMY_SERVERS = {"#503", "#480", "#523", "#476"}
OWNER_OVERRIDES = {
    "self": {"4tH", "59U", "89M", "CROW", "Dao", "JDX", "KTVS", "MOE", "RGWC", "Ryu1", "SHA", "SHA0", "SKh", "Skh", "Trh", "f4j", "kOi", "moca", "nO9", "noI", "sg3", "w6F"},
    "ally": {"0TT", "2N7", "ANH2", "AoW", "BAJ", "BHE", "CZX", "DOLU", "DaNG", "FHX", "GcC", "GoDs", "IMP", "IMp", "JL2", "JLO", "KOCH", "MOn", "OOEf", "OTT", "OWM", "SVa", "SVh", "SVo", "SsQ", "TRh", "TaW", "TrX", "VEX", "WoW3", "aTA", "eXt", "nv8", "sbM", "tWD"},
    "enemy": {"299", "476A", "476B", "476C", "476H", "476K", "476M", "476T", "476X", "476Z", "476d", "5DU", "AAOA", "ALi", "ALj", "ASp", "BgNa", "Bye", "CDF8", "CDf8", "COZy", "Digg", "EDFS", "FarM", "GX99", "IXM", "JL0", "K4TR", "Kfk", "Lghs", "MtG", "NBNH", "PmP", "R6q", "RCON", "RING", "Stj", "TIKW", "TkTk", "UMN", "UrE", "WUG", "WbW", "YDR", "fIrE", "fzn", "hMt", "hOe", "one", "pSs", "u3o", "xjR"},
}
BLOCKS = [
    (6, 46, 1, 41, "#534"),
    (6, 46, 42, 81, "#509"),
    (6, 46, 82, 122, "#503"),
    (49, 89, 1, 41, "#476"),
    (49, 89, 82, 122, "#480"),
    (92, 132, 1, 41, "#523"),
    (92, 132, 42, 81, "#511"),
    (92, 132, 82, 122, "#440"),
]


def cell(row: list[str], index: int) -> str:
    return row[index] if index < len(row) else ""


def get_values(service, spreadsheet_id: str, range_name: str) -> list[list[str]]:
    response = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name,
    ).execute()
    return response.get("values", [])


def pad_grid(rows: list[list[str]], row_count: int, column_count: int) -> list[list[str]]:
    padded = []
    for index in range(row_count):
        row = rows[index] if index < len(rows) else []
        padded.append([cell(row, column) for column in range(column_count)])
    return padded


def build_management(rows: list[list[str]]) -> dict[str, dict[str, object]]:
    headers = [str(value).strip() for value in rows[0]] if rows else []
    indexes = {
        "coord": headers.index("座標") if "座標" in headers else 0,
        "type": headers.index("種別") if "種別" in headers else 2,
        "owner": headers.index("連盟") if "連盟" in headers else 3,
        "acquired": headers.index("取得日時(Local Time)") if "取得日時(Local Time)" in headers else 4,
        "protect": headers.index("保護切れ日時(JST)") if "保護切れ日時(JST)" in headers else 5,
        "remaining": headers.index("保護残り") if "保護残り" in headers else 6,
        "status": headers.index("状態") if "状態" in headers else 9,
        "next": headers.index("次応戦枠") if "次応戦枠" in headers else 10,
        "memo": headers.index("メモ") if "メモ" in headers else 11,
        "area": headers.index("エリア") if "エリア" in headers else 18,
        "key": headers.index("位置キー") if "位置キー" in headers else 19,
    }
    result = {}
    for row_number, row in enumerate(rows[1:], start=2):
        area = str(cell(row, indexes["area"])).strip()
        coord = str(cell(row, indexes["coord"])).strip()
        key = str(cell(row, indexes["key"])).strip() or (f"{area}:{coord}" if area and coord else "")
        if ":" not in key:
            continue
        result[key.upper()] = {
            "row": row_number,
            "key": key.upper(),
            "type": str(cell(row, indexes["type"])).strip(),
            "owner": str(cell(row, indexes["owner"])).strip(),
            "acquired": str(cell(row, indexes["acquired"])).strip(),
            "protect": str(cell(row, indexes["protect"])).strip(),
            "status": str(cell(row, indexes["status"])).strip(),
            "memo": str(cell(row, indexes["memo"])).strip(),
        }
    return result


def area_for_cell(row_number: int, column_number: int) -> str:
    for start_row, end_row, start_col, end_col, area in BLOCKS:
        if start_row <= row_number <= end_row and start_col <= column_number <= end_col:
            return area
    return ""


def normalize_coordinate(value: str) -> str:
    text = str(value).strip()
    if len(text) < 3 or "-" not in text:
        return ""
    letter, number = text.split("-", 1)
    if letter.upper() not in list("ABCDEFGHIJK"):
        return ""
    return text if number.isdigit() and 1 <= int(number) <= 21 else ""


def normalize_server(value: str) -> str:
    text = str(value or "").strip()
    for server in ["534", "509", "440", "511", "503", "480", "523", "476"]:
        if server in text:
            return f"#{server}"
    return ""


def build_alliance_server_map(rows: list[list[str]]) -> dict[str, str]:
    result = {}
    for row in rows[1:]:
        for alliance_index, server_index in [(0, 1), (2, 3)]:
            alliance = str(cell(row, alliance_index)).strip()
            server = normalize_server(cell(row, server_index))
            if alliance and server and alliance not in result:
                result[alliance] = server
    return result


def is_destroyed(node: dict[str, object]) -> bool:
    return any("破壊" in str(node.get(field, "")) for field in ["type", "owner", "status"])


def is_unowned(owner: str) -> bool:
    return owner in {"", "unknown", "未取得", "未登録", "中立", "中立/未登録"}


def relation_for(node: dict[str, object], area: str, alliance_server_map: dict[str, str]) -> str:
    if is_destroyed(node):
        return "destroyed"
    if str(node.get("type", "")) == "交易地":
        return "trade"
    owner = str(node.get("owner", "")).strip()
    if is_unowned(owner):
        return "unowned"
    for relation, owners in OWNER_OVERRIDES.items():
        if owner in owners:
            return relation
    server = normalize_server(owner) or alliance_server_map.get(owner) or normalize_server(area)
    if server in SELF_SERVERS:
        return "self"
    if server in ALLY_SERVERS:
        return "ally"
    if server in ENEMY_SERVERS:
        return "enemy"
    return "unowned"


def display_value(node: dict[str, object], fallback: str) -> str:
    if is_destroyed(node):
        return "破壊"
    if str(node.get("type", "")) == "交易地":
        return "交易地"
    return str(node.get("owner", "")).strip() or fallback


def build_note(node: dict[str, object], key: str) -> str:
    lines = [
        key,
        f"種別: {node.get('type', '')}",
        f"所有連盟: {node.get('owner', '')}",
        f"取得日時: {node.get('acquired', '')}",
        f"保護切れ: {node.get('protect', '')}",
        f"状態: {node.get('status', '')}",
        f"管理表行: {node.get('row', '')}",
    ]
    if node.get("memo"):
        lines.append(f"メモ: {node.get('memo')}")
    return "\n".join(lines)


def hex_color(value: str) -> dict[str, float]:
    text = value.lstrip("#")
    return {
        "red": int(text[0:2], 16) / 255,
        "green": int(text[2:4], 16) / 255,
        "blue": int(text[4:6], 16) / 255,
    }


def cell_data(value: str, color: str, note: str = "") -> dict[str, object]:
    data = {
        "userEnteredFormat": {
            "backgroundColor": hex_color(BACKGROUND),
            "textFormat": {
                "foregroundColor": hex_color(color),
                "bold": True,
            },
        },
    }
    if value:
        data["userEnteredValue"] = {"stringValue": value}
    if note:
        data["note"] = note
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--credentials", default=DEFAULT_CREDENTIALS)
    parser.add_argument("--spreadsheet", default=DESTINATION_SPREADSHEET_ID)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--audit-out", default="/private/tmp/s6_rebuild_full_map_audit.json")
    args = parser.parse_args()

    credentials = service_account.Credentials.from_service_account_file(
        args.credentials,
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    service = build("sheets", "v4", credentials=credentials, cache_discovery=False)

    template = pad_grid(get_values(service, args.spreadsheet, f"{MAP_TEMPLATE_SHEET}!{FULL_MAP_RANGE}"), 135, 122)
    management = build_management(get_values(service, args.spreadsheet, f"{MANAGEMENT_SHEET}!A1:T2500"))
    alliance_server_map = build_alliance_server_map(get_values(service, args.spreadsheet, f"{PACT_SHEET}!A1:D500"))
    metadata = service.spreadsheets().get(spreadsheetId=args.spreadsheet).execute()
    full_map_sheet = next(
        sheet
        for sheet in metadata["sheets"]
        if sheet["properties"]["title"] == FULL_MAP_SHEET
    )
    full_map_sheet_id = full_map_sheet["properties"]["sheetId"]
    conditional_format_count = len(full_map_sheet.get("conditionalFormats", []))

    counts: Counter[str] = Counter()
    rows: list[dict[str, object]] = []
    examples = []
    for row_index, template_row in enumerate(template):
        row_values = []
        for column_index, template_value in enumerate(template_row):
            row_number = row_index + 1
            column_number = column_index + 1
            value = template_value
            relation = "unowned"
            note = ""
            coordinate = normalize_coordinate(template_value)
            area = area_for_cell(row_number, column_number) if coordinate else ""
            if coordinate and area:
                key = f"{area}:{coordinate}".upper()
                node = management.get(key)
                if node:
                    value = display_value(node, coordinate)
                    relation = relation_for(node, area, alliance_server_map)
                    note = build_note(node, key)
                    counts[relation] += 1
                    if len(examples) < 20:
                        examples.append({"cell": f"R{row_number}C{column_number}", "key": key, "value": value, "relation": relation})
                else:
                    counts["missing"] += 1
            row_values.append(cell_data(str(value), COLORS.get(relation, "#000000"), note))
        rows.append({"values": row_values})

    summary_note = (
        f"全体マップ更新: {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}\n"
        f"青(#534): {counts['self']}\n"
        f"緑(#509/#440/#511): {counts['ally']}\n"
        f"赤(#503/#480/#523/#476): {counts['enemy']}\n"
        f"黒(交易地): {counts['trade']}\n"
        f"灰(破壊): {counts['destroyed']}\n"
        f"未取得/未判定: {counts['unowned']}\n"
        f"管理表未一致: {counts['missing']}"
    )
    rows[0]["values"][0]["note"] = summary_note

    requests = [
        {
            "deleteConditionalFormatRule": {
                "sheetId": full_map_sheet_id,
                "index": index,
            }
        }
        for index in range(conditional_format_count - 1, -1, -1)
    ]
    for start in range(0, len(rows), 15):
        requests.append({
            "updateCells": {
                "range": {
                    "sheetId": full_map_sheet_id,
                    "startRowIndex": start,
                    "endRowIndex": min(start + 15, len(rows)),
                    "startColumnIndex": 0,
                    "endColumnIndex": 122,
                },
                "rows": rows[start:start + 15],
                "fields": "userEnteredValue,userEnteredFormat.backgroundColor,userEnteredFormat.textFormat.foregroundColor,userEnteredFormat.textFormat.bold,note",
            }
        })

    if args.apply:
        for start in range(0, len(requests), 20):
            service.spreadsheets().batchUpdate(
                spreadsheetId=args.spreadsheet,
                body={"requests": requests[start:start + 20]},
            ).execute()

    audit = {
        "mode": "apply" if args.apply else "dry_run",
        "spreadsheet": args.spreadsheet,
        "request_count": len(requests),
        "deleted_conditional_format_rules": conditional_format_count if args.apply else 0,
        "counts": dict(counts),
        "examples": examples,
    }
    Path(args.audit_out).write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
