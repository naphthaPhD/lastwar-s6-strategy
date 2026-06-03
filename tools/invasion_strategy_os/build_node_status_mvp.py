from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


DEFAULT_MAP_NODES = "sample_output/sheet_migration/map_nodes.csv"
DEFAULT_OWNERSHIP_CURRENT = "sample_output/sheet_migration/ownership_current.csv"
DEFAULT_PACTS = "sample_output/sheet_migration/pacts.csv"
DEFAULT_ALLIANCE_DIRECTORY = "sample_output/sheet_migration/alliance_directory.csv"
DEFAULT_OUTPUT = "sample_output/sheet_migration/node_status.json"
JST = ZoneInfo("Asia/Tokyo")


@dataclass(frozen=True)
class PactRecord:
    server: str
    alliance: str
    affiliation: str
    pact_status: str
    source: str
    active: bool
    parse_error: bool


@dataclass(frozen=True)
class AllianceDirectoryRecord:
    server: str
    alliance: str
    match_type: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build lightweight node_status.json from #534 MVP migration CSVs."
    )
    parser.add_argument("--map-nodes", default=DEFAULT_MAP_NODES, help="Input map_nodes.csv path.")
    parser.add_argument(
        "--ownership-current",
        default=DEFAULT_OWNERSHIP_CURRENT,
        help="Input ownership_current.csv path.",
    )
    parser.add_argument(
        "--pacts",
        default=DEFAULT_PACTS,
        help="Optional pacts.csv path for owner server and affiliation enrichment.",
    )
    parser.add_argument(
        "--alliance-directory",
        default=DEFAULT_ALLIANCE_DIRECTORY,
        help="Optional alliance_directory.csv path for owner server enrichment.",
    )
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Output node_status.json path.")
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return [{key: (value or "").strip() for key, value in row.items()} for row in csv.DictReader(fh)]


def parse_bool(value: str) -> bool:
    return str(value or "").strip().upper() == "TRUE"


def parse_number(value: str) -> int | float | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        number = float(text)
    except ValueError:
        return None
    return int(number) if number.is_integer() else number


def blank_to_none(value: str) -> str | None:
    text = str(value or "").strip()
    return text or None


def normalize_server(value: str) -> str:
    return str(value or "").strip().lstrip("#")


def format_server(value: str) -> str:
    server = normalize_server(value)
    return f"#{server}" if server else ""


def infer_server_from_alliance(owner_alliance: str) -> str:
    match = re.match(r"^(\d{3})", str(owner_alliance or "").strip())
    return match.group(1) if match else ""


def keyed(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        node_id = row.get("node_id", "")
        if node_id and node_id not in result:
            result[node_id] = row
    return result


def parse_jst_datetime(value: str, *, end_of_day: bool = False) -> tuple[datetime | None, bool]:
    text = str(value or "").strip()
    if not text:
        return None, False

    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y/%m/%d %H:%M:%S",
        "%Y/%m/%d %H:%M",
        "%Y-%m-%d",
        "%Y/%m/%d",
    ]
    for fmt in formats:
        try:
            parsed = datetime.strptime(text, fmt)
        except ValueError:
            continue
        if fmt in {"%Y-%m-%d", "%Y/%m/%d"}:
            if end_of_day:
                parsed = parsed.replace(hour=23, minute=59, second=59)
        return parsed.replace(tzinfo=JST), False

    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None, True
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=JST)
    return parsed.astimezone(JST), False


def pact_is_active(row: dict[str, str], now_jst: datetime) -> tuple[bool, bool]:
    valid_from, from_error = parse_jst_datetime(row.get("valid_from_jst", ""))
    valid_until, until_error = parse_jst_datetime(row.get("valid_until_jst", ""), end_of_day=True)
    if from_error or until_error:
        return False, True
    if valid_from and now_jst < valid_from:
        return False, False
    if valid_until and now_jst > valid_until:
        return False, False
    return True, False


def read_pacts(path: Path, now_jst: datetime) -> tuple[list[PactRecord], int]:
    if not path.exists():
        return [], 0

    records: list[PactRecord] = []
    parse_error_count = 0
    for row in read_csv(path):
        server = normalize_server(row.get("server", ""))
        alliance = row.get("alliance", "").strip()
        if not server and not alliance:
            continue

        active, parse_error = pact_is_active(row, now_jst)
        parse_error_count += 1 if parse_error else 0
        records.append(
            PactRecord(
                server=server,
                alliance=alliance,
                affiliation=row.get("affiliation", "unknown") or "unknown",
                pact_status=row.get("pact_status", "unknown") or "unknown",
                source=row.get("source", "") or "unknown",
                active=active,
                parse_error=parse_error,
            )
        )
    return records, parse_error_count


def read_alliance_directory(
    path: Path,
) -> tuple[dict[str, AllianceDirectoryRecord], dict[str, AllianceDirectoryRecord]]:
    if not path.exists():
        return {}, {}

    by_alliance: dict[str, AllianceDirectoryRecord] = {}
    by_alias: dict[str, AllianceDirectoryRecord] = {}
    for row in read_csv(path):
        server = normalize_server(row.get("server", ""))
        alliance = row.get("alliance", "").strip()
        if not server or not alliance:
            continue

        by_alliance.setdefault(
            alliance,
            AllianceDirectoryRecord(server=server, alliance=alliance, match_type="alliance"),
        )
        for alias in row.get("alliance_alias", "").split(","):
            alias = alias.strip()
            if not alias:
                continue
            by_alias.setdefault(
                alias,
                AllianceDirectoryRecord(server=server, alliance=alliance, match_type="alias"),
            )
    return by_alliance, by_alias


def lookup_alliance_directory(
    owner_alliance: str,
    by_alliance: dict[str, AllianceDirectoryRecord],
    by_alias: dict[str, AllianceDirectoryRecord],
) -> tuple[str, str]:
    if not owner_alliance:
        return "", "none"
    if owner_alliance in by_alliance:
        return by_alliance[owner_alliance].server, "alliance"
    if owner_alliance in by_alias:
        return by_alias[owner_alliance].server, "alias"
    return "", "none"


def resolve_owner_server(
    owner_server: str,
    owner_alliance: str,
    directory_by_alliance: dict[str, AllianceDirectoryRecord],
    directory_by_alias: dict[str, AllianceDirectoryRecord],
) -> tuple[str, str, str]:
    if owner_server:
        return owner_server, "ownership_current", "none"

    inferred_server = infer_server_from_alliance(owner_alliance)
    if inferred_server:
        return format_server(inferred_server), "numeric_prefix", "none"

    directory_server, directory_match_type = lookup_alliance_directory(
        owner_alliance,
        directory_by_alliance,
        directory_by_alias,
    )
    if directory_server:
        source = "alliance_directory" if directory_match_type == "alliance" else "alliance_alias"
        return format_server(directory_server), source, directory_match_type

    return "", "unknown", directory_match_type


def choose_pact(candidates: list[PactRecord]) -> tuple[PactRecord | None, list[str]]:
    if not candidates:
        return None, []

    warnings: list[str] = []
    for candidate in candidates:
        if candidate.active:
            return candidate, warnings

    if any(candidate.parse_error for candidate in candidates):
        warnings.append("pact_time_parse_error")
    else:
        warnings.append("pact_expired")
    return None, warnings


def build_pact_indexes(
    records: list[PactRecord],
) -> tuple[dict[str, list[PactRecord]], dict[str, list[PactRecord]], dict[str, list[PactRecord]]]:
    by_alliance: dict[str, list[PactRecord]] = {}
    by_server: dict[str, list[PactRecord]] = {}
    by_server_any: dict[str, list[PactRecord]] = {}
    for record in records:
        if record.server:
            by_server_any.setdefault(record.server, []).append(record)
        if record.alliance:
            by_alliance.setdefault(record.alliance, []).append(record)
        elif record.server:
            by_server.setdefault(record.server, []).append(record)
    return by_alliance, by_server, by_server_any


def apply_pacts(
    owner_server: str,
    owner_alliance: str,
    affiliation: str,
    by_alliance: dict[str, list[PactRecord]],
    by_server: dict[str, list[PactRecord]],
) -> tuple[str, str, str, str, str, list[str]]:
    if not owner_alliance:
        return owner_server, affiliation, "unknown", "", "", []

    normalized_owner_server = normalize_server(owner_server)
    pact, pact_warnings = choose_pact(by_server.get(normalized_owner_server, []))
    if pact:
        return owner_server, pact.affiliation, pact.pact_status, pact.source, "server", pact_warnings
    if pact_warnings:
        return owner_server, affiliation, "unknown", "", "", pact_warnings

    pact, pact_warnings = choose_pact(by_alliance.get(owner_alliance, []))
    if pact:
        updated_server = owner_server or format_server(pact.server)
        return updated_server, pact.affiliation, pact.pact_status, pact.source, "alliance", pact_warnings
    if pact_warnings:
        return owner_server, affiliation, "unknown", "", "", pact_warnings

    return owner_server, affiliation, "unknown", "", "", []


def final_status(map_row: dict[str, str] | None, ownership_row: dict[str, str] | None) -> str:
    permanent_status = (map_row or {}).get("permanent_status", "") or "unknown"
    ownership_status = (ownership_row or {}).get("status", "") or "unknown"
    if permanent_status == "destroyed" or ownership_status == "destroyed":
        return "destroyed"
    if ownership_row:
        return ownership_status or "unknown"
    return "unknown"


def warnings_for(
    status: str,
    permanent_status: str,
    owner_server: str,
    owner_alliance: str,
    affiliation: str,
) -> list[str]:
    warnings: list[str] = []
    if permanent_status == "destroyed" or status == "destroyed":
        warnings.append("destroyed_node")
    if not owner_alliance:
        warnings.append("missing_owner_alliance")
    if owner_alliance and not owner_server:
        warnings.append("missing_owner_server")
    if affiliation == "unknown":
        warnings.append("unknown_affiliation")
    return warnings


def build_node(
    node_id: str,
    map_row: dict[str, str] | None,
    ownership_row: dict[str, str] | None,
    pact_by_alliance: dict[str, list[PactRecord]],
    pact_by_server: dict[str, list[PactRecord]],
    pact_by_server_any: dict[str, list[PactRecord]],
    directory_by_alliance: dict[str, AllianceDirectoryRecord],
    directory_by_alias: dict[str, AllianceDirectoryRecord],
) -> tuple[dict[str, object], str, str]:
    map_row = map_row or {}
    ownership_row = ownership_row or {}

    permanent_status_value = map_row.get("permanent_status", "") or "unknown"
    status = final_status(map_row, ownership_row)
    owner_server = ownership_row.get("owner_server", "")
    owner_alliance = ownership_row.get("owner_alliance", "")
    affiliation = ownership_row.get("affiliation", "") or "unknown"
    owner_server, owner_server_source, directory_match_type = resolve_owner_server(
        owner_server,
        owner_alliance,
        directory_by_alliance,
        directory_by_alias,
    )
    owner_server, affiliation, pact_status, pact_source, pact_match_type, pact_warnings = apply_pacts(
        owner_server,
        owner_alliance,
        affiliation,
        pact_by_alliance,
        pact_by_server,
    )
    last_event_id = ownership_row.get("last_event_id", "")
    acquired_at_jst = ownership_row.get("acquired_at_jst", "")

    warnings = warnings_for(status, permanent_status_value, owner_server, owner_alliance, affiliation)
    warnings = list(dict.fromkeys([*warnings, *pact_warnings]))

    return {
        "node_id": node_id,
        "node_label": map_row.get("node_label", ""),
        "node_type": map_row.get("node_type", "unknown") or "unknown",
        "area": map_row.get("area", ""),
        "map_x": parse_number(map_row.get("map_x", "")),
        "map_y": parse_number(map_row.get("map_y", "")),
        "level": parse_number(map_row.get("level", "")),
        "importance": parse_number(map_row.get("importance", "")),
        "is_map_visible": parse_bool(map_row.get("is_map_visible", "")),
        "connectable": parse_bool(map_row.get("connectable", "")),
        "movement_role": map_row.get("movement_role", "unknown") or "unknown",
        "owner_server": owner_server,
        "owner_server_source": owner_server_source,
        "owner_alliance": owner_alliance,
        "affiliation": affiliation,
        "pact_status": pact_status,
        "pact_source": pact_source,
        "status": status,
        "acquired_at_jst": acquired_at_jst,
        "confidence": ownership_row.get("confidence", "unknown") or "unknown",
        "last_confirmed_at": ownership_row.get("last_confirmed_at", ""),
        "last_event_id": last_event_id,
        "permanent_status": {
            "status": permanent_status_value,
            "at_jst": blank_to_none(map_row.get("permanent_status_at_jst", "")),
            "by": blank_to_none(map_row.get("permanent_status_by", "")),
            "source": blank_to_none(map_row.get("permanent_status_source", "")),
            "note": blank_to_none(map_row.get("permanent_status_note", "")),
        },
        "history_summary": {
            "last_event_id": last_event_id,
            "last_capture_at_jst": acquired_at_jst,
            "last_capture_by": owner_alliance,
            "capture_count": 0,
            "recent_events": [],
        },
        "warnings": warnings,
    }, pact_match_type, directory_match_type


def ordered_node_ids(map_rows: list[dict[str, str]], ownership_by_id: dict[str, dict[str, str]]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for row in map_rows:
        node_id = row.get("node_id", "")
        if node_id and node_id not in seen:
            ordered.append(node_id)
            seen.add(node_id)
    for node_id in sorted(set(ownership_by_id) - seen):
        ordered.append(node_id)
    return ordered


def build_status(
    map_nodes_path: Path,
    ownership_current_path: Path,
    pacts_path: Path,
    alliance_directory_path: Path,
) -> tuple[dict[str, object], dict[str, int]]:
    map_rows = read_csv(map_nodes_path)
    ownership_rows = read_csv(ownership_current_path)
    map_by_id = keyed(map_rows)
    ownership_by_id = keyed(ownership_rows)
    ids = ordered_node_ids(map_rows, ownership_by_id)
    now_jst = datetime.now(JST)
    pacts, pact_time_parse_error_count = read_pacts(pacts_path, now_jst)
    pact_by_alliance, pact_by_server, pact_by_server_any = build_pact_indexes(pacts)
    directory_by_alliance, directory_by_alias = read_alliance_directory(alliance_directory_path)

    nodes: dict[str, dict[str, object]] = {}
    pact_match_counts = Counter()
    directory_match_counts = Counter()
    owner_server_source_counts = Counter()
    before_warning_counts = Counter()
    for node_id in ids:
        map_row = map_by_id.get(node_id)
        ownership_row = ownership_by_id.get(node_id) or {}
        before_status = final_status(map_row, ownership_row)
        before_permanent = (map_row or {}).get("permanent_status", "") or "unknown"
        before_owner_server = ownership_row.get("owner_server", "")
        before_owner_alliance = ownership_row.get("owner_alliance", "")
        before_affiliation = ownership_row.get("affiliation", "") or "unknown"
        before_warning_counts.update(
            warnings_for(
                before_status,
                before_permanent,
                before_owner_server,
                before_owner_alliance,
                before_affiliation,
            )
        )
        node, match_type, directory_match_type = build_node(
            node_id,
            map_row,
            ownership_row,
            pact_by_alliance,
            pact_by_server,
            pact_by_server_any,
            directory_by_alliance,
            directory_by_alias,
        )
        nodes[node_id] = node
        if match_type:
            pact_match_counts[match_type] += 1
        if directory_match_type != "none":
            directory_match_counts[directory_match_type] += 1
        owner_server_source_counts[str(node.get("owner_server_source", "unknown"))] += 1

    warning_counts = Counter(
        warning
        for node in nodes.values()
        for warning in node.get("warnings", [])
    )
    summary = {
        "node_count": len(nodes),
        "active_count": sum(1 for node in nodes.values() if node.get("status") == "active"),
        "destroyed_count": sum(1 for node in nodes.values() if node.get("status") == "destroyed"),
        "unknown_owner_count": warning_counts.get("missing_owner_alliance", 0),
    }
    map_ids = set(map_by_id)
    ownership_ids = set(ownership_by_id)
    inspection = {
        "node_count": len(nodes),
        "destroyed_count": summary["destroyed_count"],
        "unknown_owner_count": summary["unknown_owner_count"],
        "missing_owner_server_count": warning_counts.get("missing_owner_server", 0),
        "unknown_affiliation_count": warning_counts.get("unknown_affiliation", 0),
        "unknown_affiliation_before": before_warning_counts.get("unknown_affiliation", 0),
        "unknown_affiliation_after": warning_counts.get("unknown_affiliation", 0),
        "missing_owner_server_before": before_warning_counts.get("missing_owner_server", 0),
        "missing_owner_server_after": warning_counts.get("missing_owner_server", 0),
        "directory_matched_by_alliance_count": directory_match_counts.get("alliance", 0),
        "directory_matched_by_alias_count": directory_match_counts.get("alias", 0),
        "numeric_prefix_server_count": owner_server_source_counts.get("numeric_prefix", 0),
        "directory_unmatched_owner_count": sum(
            1
            for node in nodes.values()
            if node.get("owner_alliance") and node.get("owner_server_source") == "unknown"
        ),
        "pact_matched_after_directory_count": pact_match_counts.get("server", 0),
        "pact_matched_by_alliance_count": pact_match_counts.get("alliance", 0),
        "pact_matched_by_server_count": pact_match_counts.get("server", 0),
        "pact_unmatched_owner_count": sum(
            1
            for node in nodes.values()
            if node.get("owner_alliance") and not node.get("pact_source")
        ),
        "pact_time_parse_error_count": pact_time_parse_error_count,
        "map_nodes_only_count": len(map_ids - ownership_ids),
        "ownership_only_count": len(ownership_ids - map_ids),
        "node_id_mismatch_count": len(map_ids.symmetric_difference(ownership_ids)),
    }

    payload = {
        "generated_at_jst": now_jst.isoformat(timespec="seconds"),
        "source": {
            "map_nodes": str(map_nodes_path).replace("\\", "/"),
            "ownership_current": str(ownership_current_path).replace("\\", "/"),
            "pacts": str(pacts_path).replace("\\", "/") if pacts_path.exists() else "",
            "alliance_directory": str(alliance_directory_path).replace("\\", "/")
            if alliance_directory_path.exists()
            else "",
        },
        "summary": summary,
        "nodes": nodes,
    }
    return payload, inspection


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def print_inspection(inspection: dict[str, int], output_path: Path, payload: dict[str, object]) -> None:
    print("Node status MVP inspection")
    print(f"output={output_path}")
    for key in [
        "node_count",
        "destroyed_count",
        "unknown_owner_count",
        "unknown_affiliation_before",
        "unknown_affiliation_after",
        "missing_owner_server_before",
        "missing_owner_server_after",
        "directory_matched_by_alliance_count",
        "directory_matched_by_alias_count",
        "numeric_prefix_server_count",
        "directory_unmatched_owner_count",
        "pact_matched_after_directory_count",
        "pact_matched_by_alliance_count",
        "pact_matched_by_server_count",
        "pact_unmatched_owner_count",
        "pact_time_parse_error_count",
        "missing_owner_server_count",
        "unknown_affiliation_count",
        "map_nodes_only_count",
        "ownership_only_count",
        "node_id_mismatch_count",
    ]:
        print(f"{key}={inspection[key]}")
    warning_counts = Counter(
        warning
        for node in payload["nodes"].values()
        for warning in node.get("warnings", [])
    )
    print(f"warning_counts={dict(sorted(warning_counts.items()))}")


def main() -> int:
    args = parse_args()
    map_nodes_path = Path(args.map_nodes)
    ownership_current_path = Path(args.ownership_current)
    pacts_path = Path(args.pacts)
    alliance_directory_path = Path(args.alliance_directory)
    output_path = Path(args.output)

    payload, inspection = build_status(
        map_nodes_path,
        ownership_current_path,
        pacts_path,
        alliance_directory_path,
    )
    write_json(output_path, payload)
    print_inspection(inspection, output_path, payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
