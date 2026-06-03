from __future__ import annotations

import argparse
import csv
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from urllib.request import urlopen


MAP_NODES_COLUMNS = [
    "node_id",
    "node_label",
    "node_type",
    "area",
    "map_x",
    "map_y",
    "level",
    "importance",
    "is_map_visible",
    "connectable",
    "movement_role",
    "permanent_status",
    "permanent_status_at_jst",
    "permanent_status_by",
    "permanent_status_source",
    "permanent_status_note",
]

OWNERSHIP_CURRENT_COLUMNS = [
    "node_id",
    "owner_server",
    "owner_alliance",
    "affiliation",
    "acquired_at_jst",
    "source",
    "confidence",
    "last_confirmed_at",
    "last_event_id",
    "status",
    "note",
]

DESTROYED_KEYWORDS = ("破壊", "destroyed", "ruined")

FISHERY_AXIS = [20, 99, 199, 299, 399, 499, 599, 699, 799, 899, 978]
CITY_AXIS = [49, 149, 249, 349, 449, 549, 649, 749, 849, 949]

TYPE_ALIASES = {
    "漁場": "漁場",
    "都市": "都市",
    "密林の村": "都市",
    "湿地の村": "都市",
    "密林の兵舎": "都市",
    "湿地の兵舎": "都市",
    "密林の集会場": "都市",
    "湿地の集会場": "都市",
    "交易地": "交易地",
    "祭壇": "祭壇",
    "祖霊神殿": "祖霊神殿",
    "ゲーム機": "ゲーム機",
}

TYPE_DEFAULTS = {
    "漁場": {"importance": "3", "connectable": "TRUE", "movement_role": "transit"},
    "都市": {"importance": "8", "connectable": "TRUE", "movement_role": "target_only"},
    "交易地": {"importance": "1", "connectable": "FALSE", "movement_role": "isolated"},
    "祭壇": {"importance": "9", "connectable": "FALSE", "movement_role": "isolated"},
    "祖霊神殿": {"importance": "10", "connectable": "FALSE", "movement_role": "isolated"},
    "ゲーム機": {"importance": "5", "connectable": "FALSE", "movement_role": "display_only"},
    "unknown": {"importance": "0", "connectable": "FALSE", "movement_role": "unknown"},
}

HEADER_ALIASES = {
    "node_label": ("座標(自動)", "座標", "node_label", "label"),
    "node_type": ("種別", "node_type", "type"),
    "owner_alliance": ("連盟", "owner_alliance", "owner", "alliance"),
    "acquired_at_jst": ("取得日時(Local Time)", "取得日時", "acquired_at_jst", "acquired_at"),
    "status": ("状態", "status"),
    "note": ("メモ", "note", "memo"),
    "area": ("エリア", "area"),
    "node_id": ("位置キー", "node_id", "id"),
}


@dataclass(frozen=True)
class LegacyRow:
    source_row: int
    node_id: str
    node_label: str
    raw_type: str
    owner_alliance: str
    acquired_at_jst: str
    legacy_status: str
    note: str
    area: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Migrate legacy 管理表たたき CSV into lightweight #534 MVP CSVs."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Legacy 管理表たたき CSV path or CSV export URL.",
    )
    parser.add_argument(
        "--output-dir",
        default="sample_output/sheet_migration",
        help="Output directory for map_nodes.csv and ownership_current.csv.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=90,
        help="Timeout when --input is an http(s) URL.",
    )
    return parser.parse_args()


def read_input_text(input_ref: str, timeout_seconds: float) -> str:
    if input_ref.startswith(("http://", "https://")):
        with urlopen(input_ref, timeout=timeout_seconds) as response:
            return response.read().decode("utf-8-sig")
    return Path(input_ref).read_text(encoding="utf-8-sig")


def pick(row: dict[str, str], *aliases: str) -> str:
    for alias in aliases:
        if alias in row and row[alias] is not None:
            value = str(row[alias]).strip()
            if value:
                return value
    return ""


def pick_alias(row: dict[str, str], field: str) -> str:
    return pick(row, *HEADER_ALIASES[field])


def parse_legacy_rows(text: str) -> list[LegacyRow]:
    raw_rows = list(csv.reader(text.splitlines()))
    if not raw_rows:
        return []

    header = [cell.strip() for cell in raw_rows[0]]
    has_named_header = any(name in header for aliases in HEADER_ALIASES.values() for name in aliases)
    rows: list[LegacyRow] = []

    if has_named_header:
        for source_row, row in enumerate(csv.DictReader(text.splitlines()), start=2):
            legacy = LegacyRow(
                source_row=source_row,
                node_id=pick_alias(row, "node_id"),
                node_label=pick_alias(row, "node_label"),
                raw_type=pick_alias(row, "node_type"),
                owner_alliance=pick_alias(row, "owner_alliance"),
                acquired_at_jst=pick_alias(row, "acquired_at_jst"),
                legacy_status=pick_alias(row, "status"),
                note=pick_alias(row, "note"),
                area=normalize_area(pick_alias(row, "area")),
            )
            if should_keep(legacy):
                rows.append(fill_missing_node_id(legacy))
        return rows

    for source_row, row in enumerate(raw_rows, start=1):
        padded = row + [""] * max(0, 20 - len(row))
        legacy = LegacyRow(
            source_row=source_row,
            node_id=padded[19].strip(),
            node_label=(padded[1].strip() or padded[0].strip()),
            raw_type=padded[2].strip(),
            owner_alliance=padded[3].strip(),
            acquired_at_jst=padded[4].strip(),
            legacy_status=padded[7].strip(),
            note=padded[11].strip(),
            area=normalize_area(padded[18].strip()),
        )
        if should_keep(legacy):
            rows.append(fill_missing_node_id(legacy))
    return rows


def should_keep(row: LegacyRow) -> bool:
    if row.source_row <= 2 and row.node_label in {"座標", "座標(自動)", "例: B-19 / b-20"}:
        return False
    if row.source_row <= 2 and (row.node_label == "自動" or "から選択" in row.raw_type):
        return False
    return bool(row.node_label or row.node_id)


def fill_missing_node_id(row: LegacyRow) -> LegacyRow:
    if row.node_id:
        return row
    if not row.area or not row.node_label:
        return row
    if row.area in {"中央", "#8061", "8061"} or row.node_label.startswith("中央-"):
        node_id = f"中央:{row.node_label}"
    else:
        node_id = f"{row.area}:{row.node_label}"
    return LegacyRow(**{**row.__dict__, "node_id": node_id})


def normalize_area(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    if text in {"中央", "#8061", "8061"}:
        return "中央"
    if text.startswith("#"):
        return text
    if text.isdigit():
        return f"#{text}"
    return text


def normalize_node_type(raw_type: str) -> str:
    text = str(raw_type or "").strip()
    return TYPE_ALIASES.get(text, "unknown")


def has_destroyed_marker(*values: str) -> bool:
    text = " ".join(str(value or "") for value in values).lower()
    return any(keyword.lower() in text for keyword in DESTROYED_KEYWORDS)


def local_coord_xy(label: str) -> tuple[str, str]:
    text = str(label or "").strip()
    if text.startswith("中央-"):
        parts = text.split("-")
        if len(parts) == 3 and parts[1].isdigit() and parts[2].isdigit():
            row = int(parts[1])
            col = int(parts[2])
            if 1 <= row <= 20 and 1 <= col <= 20:
                return str(24 + (col - 1) * 50), str(974 - (row - 1) * 50)
        return "", ""

    if "-" not in text:
        return "", ""
    letter, number_text = text.split("-", 1)
    if len(letter) != 1 or not number_text.isdigit():
        return "", ""
    number = int(number_text)
    if letter.isupper():
        row_index = ord(letter) - ord("A")
        col_index = (number - 1) // 2
        if 0 <= row_index < len(FISHERY_AXIS) and 0 <= col_index < len(FISHERY_AXIS):
            return str(FISHERY_AXIS[col_index]), str(FISHERY_AXIS[row_index])
    if letter.islower():
        row_index = ord(letter) - ord("a")
        col_index = (number - 2) // 2
        if 0 <= row_index < len(CITY_AXIS) and 0 <= col_index < len(CITY_AXIS):
            return str(CITY_AXIS[col_index]), str(CITY_AXIS[row_index])
    return "", ""


def owner_server(owner_alliance: str) -> str:
    text = str(owner_alliance or "").strip()
    if text == "破壊":
        return ""
    digits = ""
    for char in text:
        if char.isdigit():
            digits += char
            continue
        break
    return f"#{digits}" if len(digits) >= 3 else ""


def build_rows(legacy_rows: list[LegacyRow]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    map_nodes: list[dict[str, str]] = []
    ownership_current: list[dict[str, str]] = []

    for legacy in legacy_rows:
        node_type = normalize_node_type(legacy.raw_type)
        defaults = TYPE_DEFAULTS[node_type]
        permanent_status = (
            "destroyed"
            if has_destroyed_marker(legacy.owner_alliance, legacy.legacy_status, legacy.note)
            else "active"
        )
        map_x, map_y = local_coord_xy(legacy.node_label)
        permanent_note = legacy.note if permanent_status == "destroyed" else ""

        map_nodes.append(
            {
                "node_id": legacy.node_id,
                "node_label": legacy.node_label,
                "node_type": node_type,
                "area": legacy.area,
                "map_x": map_x,
                "map_y": map_y,
                "level": "",
                "importance": defaults["importance"],
                "is_map_visible": "TRUE",
                "connectable": defaults["connectable"],
                "movement_role": defaults["movement_role"],
                "permanent_status": permanent_status,
                "permanent_status_at_jst": legacy.acquired_at_jst if permanent_status == "destroyed" else "",
                "permanent_status_by": "",
                "permanent_status_source": "legacy_management_table" if permanent_status == "destroyed" else "",
                "permanent_status_note": permanent_note,
            }
        )

        if permanent_status == "destroyed":
            current_status = "destroyed"
            confidence = "high"
        elif legacy.owner_alliance:
            current_status = "active"
            confidence = "medium"
        else:
            current_status = "unknown"
            confidence = "low"

        ownership_current.append(
            {
                "node_id": legacy.node_id,
                "owner_server": owner_server(legacy.owner_alliance),
                "owner_alliance": "" if permanent_status == "destroyed" else legacy.owner_alliance,
                "affiliation": "unknown",
                "acquired_at_jst": legacy.acquired_at_jst,
                "source": "legacy_management_table",
                "confidence": confidence,
                "last_confirmed_at": legacy.acquired_at_jst,
                "last_event_id": "",
                "status": current_status,
                "note": legacy.note,
            }
        )

    return map_nodes, ownership_current


def write_csv(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def duplicate_values(rows: list[dict[str, str]], field: str) -> list[str]:
    counts = Counter(row.get(field, "") for row in rows if row.get(field, ""))
    return sorted(value for value, count in counts.items() if count > 1)


def print_inspection(map_nodes: list[dict[str, str]], ownership_current: list[dict[str, str]], output_dir: Path) -> None:
    map_duplicates = duplicate_values(map_nodes, "node_id")
    ownership_duplicates = duplicate_values(ownership_current, "node_id")
    blank_map_ids = sum(1 for row in map_nodes if not row.get("node_id"))
    blank_ownership_ids = sum(1 for row in ownership_current if not row.get("node_id"))

    print("MVP sheet migration inspection")
    print(f"output_dir={output_dir}")
    print(f"map_nodes_rows={len(map_nodes)}")
    print(f"ownership_current_rows={len(ownership_current)}")
    print(f"map_nodes_blank_node_id={blank_map_ids}")
    print(f"ownership_current_blank_node_id={blank_ownership_ids}")
    print(f"map_nodes_duplicate_node_id_count={len(map_duplicates)}")
    print(f"ownership_current_duplicate_node_id_count={len(ownership_duplicates)}")
    if map_duplicates:
        print(f"map_nodes_duplicate_node_id_sample={map_duplicates[:20]}")
    if ownership_duplicates:
        print(f"ownership_current_duplicate_node_id_sample={ownership_duplicates[:20]}")
    print(f"map_nodes_type_counts={dict(sorted(Counter(row['node_type'] for row in map_nodes).items()))}")
    print(f"map_nodes_permanent_status_counts={dict(sorted(Counter(row['permanent_status'] for row in map_nodes).items()))}")
    print(f"ownership_status_counts={dict(sorted(Counter(row['status'] for row in ownership_current).items()))}")
    print("wrote=map_nodes.csv")
    print("wrote=ownership_current.csv")


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    text = read_input_text(args.input, args.timeout_seconds)
    legacy_rows = parse_legacy_rows(text)
    map_nodes, ownership_current = build_rows(legacy_rows)

    write_csv(output_dir / "map_nodes.csv", MAP_NODES_COLUMNS, map_nodes)
    write_csv(output_dir / "ownership_current.csv", OWNERSHIP_CURRENT_COLUMNS, ownership_current)
    print_inspection(map_nodes, ownership_current, output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
