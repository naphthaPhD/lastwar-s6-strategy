from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from datetime import datetime, time, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


DEFAULT_NODE_STATUS = "sample_output/sheet_migration/node_status.json"
DEFAULT_STATE_JSON = "sample_output/state.json"
DEFAULT_ALLIANCE_DIRECTORY = "sample_output/sheet_migration/alliance_directory.csv"
DEFAULT_PACTS = "sample_output/sheet_migration/pacts.csv"
DEFAULT_OUTPUT_DIR = "sample_output/sheet_migration"
DEFAULT_COMMANDER_REVIEW = "analysis/commander_review_2026-05-31.md"
JST = ZoneInfo("Asia/Tokyo")

SELF_SERVER = "534"
ALLY_SERVERS = {"509", "440", "511"}
FRONTLINE_CORE = {"D-11", "D-13", "E-11", "E-13", "d-12", "d-14", "c-8", "c-10"}
FRONTLINE_ADJACENT_PREFIXES = {"D", "E", "d", "e"}

NODE_CURRENT_COLUMNS = [
    "node_id",
    "area",
    "coord",
    "node_type_raw",
    "node_type_norm",
    "x",
    "y",
    "current_alliance",
    "owner_server",
    "owner_server_source",
    "server_side",
    "pact_status",
    "pact_source",
    "status_raw",
    "status_norm",
    "captured_at_jst",
    "safe_until_jst",
    "protection_status",
    "last_event_at",
    "last_event_owner",
    "event_count",
    "confidence",
    "enemy_flag",
    "destroyed_flag",
    "warning_flags",
    "source_row",
    "updated_at_jst",
    "memo",
]

ALERT_COLUMNS = [
    "alert_type",
    "severity",
    "node_id",
    "coord",
    "node_type_norm",
    "current_alliance",
    "server_side",
    "status_norm",
    "protection_status",
    "safe_until_jst",
    "reason",
    "review_status",
    "memo",
]

RISK_COLUMNS = [
    "node_id",
    "coord",
    "node_type_norm",
    "current_alliance",
    "status_norm",
    "protection_status",
    "safe_until_jst",
    "frontline_group",
    "server_side",
    "enemy_flag",
    "destroyed_flag",
    "strategic_value",
    "risk_score",
    "risk_level",
    "risk_note",
]

DECISION_COLUMNS = [
    "node_id",
    "area",
    "coord",
    "node_type_norm",
    "current_alliance",
    "owner_server",
    "owner_server_source",
    "server_side",
    "pact_status",
    "status_norm",
    "frontline_group",
    "enemy_flag",
    "destroyed_flag",
    "strategic_value",
    "risk_score",
    "risk_level",
    "risk_note",
    "confidence",
    "memo",
]

COMMANDER_DASHBOARD_COLUMNS = [
    "metric",
    "value",
    "note",
]

TOP_CRITICAL_COLUMNS = [
    "rank",
    "node_id",
    "coord",
    "node_type_norm",
    "current_alliance",
    "owner_server",
    "server_side",
    "frontline_group",
    "risk_score",
    "risk_level",
    "risk_reason",
    "recommended_action",
    "confidence",
    "memo_short",
]

TOP_ENEMY_INVASION_COLUMNS = [
    "rank",
    "from_node_id",
    "from_coord",
    "from_alliance",
    "from_server",
    "to_node_id",
    "to_coord",
    "to_alliance",
    "to_server",
    "target_type",
    "candidate_reason",
    "priority",
    "recommended_action",
    "confidence",
]

TOP_ATTACK_COLUMNS = [
    "rank",
    "from_node_id",
    "from_coord",
    "from_alliance",
    "to_node_id",
    "to_coord",
    "to_alliance",
    "to_server",
    "target_type",
    "attack_reason",
    "priority",
    "recommended_action",
    "city_destroy_window",
    "confidence",
]

ENEMY_INVASION_EDGE_COLUMNS = [
    "enemy_from_node",
    "enemy_from_coord",
    "enemy_from_alliance",
    "enemy_from_server",
    "friendly_to_node",
    "friendly_to_coord",
    "friendly_to_alliance",
    "friendly_to_server",
    "edge_type",
    "risk_reason",
    "recommended_action",
    "confidence",
]

ATTACK_EDGE_COLUMNS = [
    "friendly_from_node",
    "friendly_from_coord",
    "friendly_from_alliance",
    "friendly_from_server",
    "enemy_to_node",
    "enemy_to_coord",
    "enemy_to_alliance",
    "enemy_to_server",
    "edge_type",
    "attack_reason",
    "recommended_action",
    "confidence",
]

EDGE_CLASSIFICATION_COLUMNS = [
    "execution_class",
    "recommended_owner",
    "review_priority",
    "human_check",
]

CLASSIFIED_ENEMY_INVASION_EDGE_COLUMNS = ENEMY_INVASION_EDGE_COLUMNS + EDGE_CLASSIFICATION_COLUMNS
CLASSIFIED_ATTACK_EDGE_COLUMNS = ATTACK_EDGE_COLUMNS + EDGE_CLASSIFICATION_COLUMNS

TOP_LIMIT = 30
EDGE_REVIEW_LIMIT = 10
CITY_DESTROY_WINDOWS = [
    {"label": "wednesday_server_day", "weekday": 2, "start": "11:00", "end": "10:59"},
    {"label": "saturday_server_day", "weekday": 5, "start": "11:00", "end": "10:59"},
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate #534 Sheet V2 CSVs from node_status.json."
    )
    parser.add_argument("--node-status", default=DEFAULT_NODE_STATUS, help="Input node_status.json.")
    parser.add_argument("--state-json", default=DEFAULT_STATE_JSON, help="Input state.json for graph adjacency.")
    parser.add_argument(
        "--alliance-directory",
        default=DEFAULT_ALLIANCE_DIRECTORY,
        help="Input alliance_directory.csv for owner_server fallback.",
    )
    parser.add_argument("--pacts", default=DEFAULT_PACTS, help="Input pacts.csv, read only.")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="Directory for V2 CSV outputs.")
    parser.add_argument(
        "--commander-review",
        default=DEFAULT_COMMANDER_REVIEW,
        help="Markdown review file to update with edge classification sections.",
    )
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return [{key: (value or "").strip() for key, value in row.items()} for row in csv.DictReader(fh)]


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def load_node_status(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)
    nodes = payload.get("nodes")
    if not isinstance(nodes, dict):
        raise ValueError(f"{path} does not contain a nodes object")
    return payload


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def build_adjacency(state: dict[str, Any]) -> dict[str, set[str]]:
    adjacency: dict[str, set[str]] = {}
    for edge in state.get("connections", []) or []:
        if not isinstance(edge, dict):
            continue
        source = str(edge.get("source", "") or "")
        target = str(edge.get("target", "") or "")
        if not source or not target:
            continue
        adjacency.setdefault(source, set()).add(target)
        adjacency.setdefault(target, set()).add(source)
    return adjacency


def parse_datetime(value: Any) -> datetime:
    text = str(value or "").strip()
    if not text:
        return datetime.now(JST)
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return datetime.now(JST)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=JST)
    return parsed.astimezone(JST)


def parse_hhmm(value: str) -> time:
    hour, minute = value.split(":", 1)
    return time(int(hour), int(minute), tzinfo=JST)


def active_city_destroy_window(now_jst: datetime) -> tuple[bool, dict[str, str]]:
    for window in CITY_DESTROY_WINDOWS:
        base_date = now_jst.date()
        days_since = (now_jst.weekday() - int(window["weekday"])) % 7
        start_date = base_date - timedelta(days=days_since)
        start_at = datetime.combine(start_date, parse_hhmm(window["start"]))
        end_at = datetime.combine(start_date, parse_hhmm(window["end"]))
        if end_at <= start_at:
            end_at += timedelta(days=1)
        if start_at <= now_jst <= end_at:
            return True, {
                "label": window["label"],
                "server_day": str(window["label"]).replace("_server_day", ""),
                "start_at_jst": start_at.isoformat(timespec="minutes"),
                "end_at_jst": end_at.isoformat(timespec="minutes"),
            }
    return False, {
        "label": "outside_city_destroy_window",
        "server_day": "none",
        "start_at_jst": "",
        "end_at_jst": "",
    }


def normalize_server(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    match = re.search(r"(\d{3})", text)
    return match.group(1) if match else ""


def compact_lookup_value(value: Any) -> str:
    return re.sub(r"\s+", "", str(value or "").strip())


def exact_lookup_key(value: Any) -> str:
    return f"EXACT:{compact_lookup_value(value)}"


def normalized_lookup_key(value: Any) -> str:
    return f"NORM:{compact_lookup_value(value).upper()}"


def read_alliance_directory(path: Path) -> dict[str, tuple[str, str]]:
    directory: dict[str, tuple[str, str]] = {}
    directory_priority: dict[str, int] = {}
    normalized: dict[str, tuple[str, str, str]] = {}
    normalized_priority: dict[str, int] = {}
    ambiguous_normalized: set[str] = set()

    source_priority = {
        "manual_override": 100,
        "alliance_directory": 80,
        "alliance_alias": 70,
    }

    def add_entry(value: str, server: str, source: str) -> None:
        compact = compact_lookup_value(value)
        if not server or not compact:
            return
        priority = source_priority.get(source, 50)
        exact_key = exact_lookup_key(compact)
        if priority >= directory_priority.get(exact_key, -1):
            directory[exact_key] = (server, source)
            directory_priority[exact_key] = priority
        norm_key = normalized_lookup_key(compact)
        existing = normalized.get(norm_key)
        if existing and existing[2] != compact:
            if priority > normalized_priority.get(norm_key, -1):
                normalized[norm_key] = (server, source, compact)
                normalized_priority[norm_key] = priority
                ambiguous_normalized.discard(norm_key)
            elif priority == normalized_priority.get(norm_key, -1):
                ambiguous_normalized.add(norm_key)
        elif norm_key not in ambiguous_normalized:
            normalized[norm_key] = (server, source, compact)
            normalized_priority[norm_key] = priority

    for row in read_csv(path):
        server = normalize_server(row.get("server", ""))
        alliance = row.get("alliance", "").strip()
        row_source = row.get("source", "").strip()
        alliance_source = "manual_override" if row_source == "manual_override" else "alliance_directory"
        alias_source = "manual_override" if row_source == "manual_override" else "alliance_alias"
        add_entry(alliance, server, alliance_source)
        for alias in re.split(r"[,;/\s]+", row.get("alliance_alias", "")):
            add_entry(alias.strip(), server, alias_source)
    for key, (server, source, _value) in normalized.items():
        if key not in ambiguous_normalized:
            directory.setdefault(key, (server, source))
    return directory


def node_type_norm(raw: Any) -> str:
    text = str(raw or "").strip()
    if text == "漁場":
        return "fishery"
    if text in {"都市", "密林の村", "密林の兵舎", "密林の集会場"}:
        return "city"
    if text == "交易地":
        return "trade"
    return "unknown"


def status_norm(raw: Any, owner_alliance: str) -> str:
    text = str(raw or "").strip()
    if text == "destroyed" or text == "破壊":
        return "destroyed"
    if text in {"active", "保護中", "保護切れ"}:
        return "owned" if owner_alliance else "neutral_or_unknown"
    if text in {"要確認", "uncertain", "owned_uncertain"}:
        return "owned_uncertain"
    return "neutral_or_unknown"


def first_value(node: dict[str, Any], names: list[str]) -> str:
    for name in names:
        value = node.get(name)
        if value not in (None, ""):
            return str(value)
    return ""


def resolve_owner_server(
    node: dict[str, Any],
    directory: dict[str, tuple[str, str]],
) -> tuple[str, str]:
    owner_alliance = str(node.get("owner_alliance", "") or "").strip()
    if owner_alliance:
        manual_match = directory.get(exact_lookup_key(owner_alliance)) or directory.get(normalized_lookup_key(owner_alliance))
        if manual_match and manual_match[1] == "manual_override":
            return manual_match

    owner_server = normalize_server(node.get("owner_server", ""))
    owner_source = str(node.get("owner_server_source", "") or "unknown")
    if owner_server:
        return owner_server, owner_source

    if owner_alliance:
        match = re.match(r"^#?(\d{3})", owner_alliance)
        if match:
            return match.group(1), "numeric_prefix"
        directory_match = directory.get(exact_lookup_key(owner_alliance)) or directory.get(normalized_lookup_key(owner_alliance))
        if directory_match:
            return directory_match

    return "", "unknown"


def server_side(owner_server: str, current_alliance: str) -> str:
    server = normalize_server(owner_server)
    if not server:
        return "unknown"
    if server == SELF_SERVER:
        return "self"
    if server in ALLY_SERVERS:
        return "ally"
    return "enemy"


def protection_status(row: dict[str, Any]) -> str:
    if row["status_norm"] == "destroyed":
        return "destroyed"
    if row["status_norm"] == "neutral_or_unknown":
        return "neutral_or_unknown"
    if row["safe_until_jst"]:
        return "safe_time_known"
    return "safe_time_missing"


def extract_memo(node: dict[str, Any]) -> str:
    permanent = node.get("permanent_status")
    if isinstance(permanent, dict):
        note = permanent.get("note")
        if note:
            return str(note)
    return first_value(node, ["memo", "note"])


def build_node_current_rows(
    nodes: dict[str, dict[str, Any]],
    directory: dict[str, tuple[str, str]],
    updated_at_jst: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, (node_id, node) in enumerate(nodes.items(), start=1):
        current_alliance = str(node.get("owner_alliance", "") or "").strip()
        owner_server, owner_server_source = resolve_owner_server(node, directory)
        raw_status = str(node.get("status", "") or "")
        normalized_status = status_norm(raw_status, current_alliance)
        side = server_side(owner_server, current_alliance)
        if normalized_status == "destroyed":
            owner_server = "none"
            owner_server_source = "destroyed"
            side = "destroyed"
        warnings = node.get("warnings", [])
        if not isinstance(warnings, list):
            warnings = []

        row = {
            "node_id": node_id,
            "area": node.get("area", ""),
            "coord": node.get("node_label", "") or node_id.split(":", 1)[-1],
            "node_type_raw": node.get("node_type", ""),
            "node_type_norm": node_type_norm(node.get("node_type", "")),
            "x": node.get("map_x", ""),
            "y": node.get("map_y", ""),
            "current_alliance": current_alliance,
            "owner_server": owner_server,
            "owner_server_source": owner_server_source,
            "server_side": side,
            "pact_status": node.get("pact_status", "") or "unknown",
            "pact_source": node.get("pact_source", ""),
            "status_raw": raw_status,
            "status_norm": normalized_status,
            "captured_at_jst": node.get("acquired_at_jst", ""),
            "safe_until_jst": first_value(
                node,
                ["safe_until_jst", "protect_until", "protect_until_jst", "protection_until_jst"],
            ),
            "last_event_at": "",
            "last_event_owner": "",
            "event_count": 0,
            "confidence": node.get("confidence", "unknown") or "unknown",
            "enemy_flag": "",
            "destroyed_flag": "TRUE" if normalized_status == "destroyed" else "FALSE",
            "warning_flags": ";".join(str(warning) for warning in warnings if warning),
            "source_row": index,
            "updated_at_jst": updated_at_jst,
            "memo": extract_memo(node),
        }

        history = node.get("history_summary")
        if isinstance(history, dict):
            row["last_event_at"] = history.get("last_capture_at_jst", "") or ""
            row["last_event_owner"] = history.get("last_capture_by", "") or ""
            row["event_count"] = history.get("capture_count", 0) or 0

        row["protection_status"] = protection_status(row)
        row["enemy_flag"] = "TRUE" if row["server_side"] == "enemy" else "FALSE"
        rows.append(row)
    return rows


def alert_for(row: dict[str, Any]) -> tuple[str, str, str] | None:
    warning_flags = set(str(row.get("warning_flags", "")).split(";")) if row.get("warning_flags") else set()

    if row["node_type_norm"] == "city" and row["destroyed_flag"] == "TRUE":
        return "destroyed_city", "critical", "city is destroyed"
    if row["server_side"] == "enemy" and row["status_norm"] in {"owned", "owned_uncertain"}:
        return "enemy_owned", "high", "resolved owner server is enemy"
    if row["status_norm"] == "owned_uncertain" or "unknown_affiliation" in warning_flags:
        return "uncertain", "mid", "owner server, current alliance, or side judgment needs review"
    if row["node_type_norm"] == "unknown":
        return "type_uncertain", "low", "node type is not mapped"
    if row["status_norm"] == "neutral_or_unknown" and row["last_event_owner"]:
        return "abandon_detected", "high", "history owner exists but current state is neutral or unknown"
    return None


def build_alert_rows(node_current_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in node_current_rows:
        alert = alert_for(row)
        if not alert:
            continue
        alert_type, severity, reason = alert
        rows.append(
            {
                "alert_type": alert_type,
                "severity": severity,
                "node_id": row["node_id"],
                "coord": row["coord"],
                "node_type_norm": row["node_type_norm"],
                "current_alliance": row["current_alliance"],
                "server_side": row["server_side"],
                "status_norm": row["status_norm"],
                "protection_status": row["protection_status"],
                "safe_until_jst": row["safe_until_jst"],
                "reason": reason,
                "review_status": "open",
                "memo": row["memo"],
            }
        )
    return rows


def frontline_group(coord: str) -> str:
    text = str(coord or "").strip()
    if text in FRONTLINE_CORE:
        return "frontline_core"
    if text[:1] in FRONTLINE_ADJACENT_PREFIXES:
        return "frontline_adjacent"
    return "other"


def type_score(node_type: str) -> int:
    if node_type == "city":
        return 30
    if node_type == "trade":
        return 20
    if node_type == "fishery":
        return 10
    return 0


def risk_level(score: int) -> str:
    if score >= 90:
        return "critical"
    if score >= 60:
        return "high"
    if score >= 30:
        return "mid"
    return "low"


def build_risk_rows(node_current_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in node_current_rows:
        score = 0
        notes: list[str] = []

        base_score = type_score(row["node_type_norm"])
        if base_score:
            score += base_score
            notes.append(f"{row['node_type_norm']} +{base_score}")

        if row["enemy_flag"] == "TRUE":
            score += 40
            notes.append("enemy_flag +40")
        if row["destroyed_flag"] == "TRUE":
            score += 100
            notes.append("destroyed_flag +100")

        group = frontline_group(row["coord"])
        if group == "frontline_core":
            score += 30
            notes.append("frontline_core +30")
        elif group == "frontline_adjacent":
            score += 15
            notes.append("frontline_adjacent +15")

        rows.append(
            {
                "node_id": row["node_id"],
                "coord": row["coord"],
                "node_type_norm": row["node_type_norm"],
                "current_alliance": row["current_alliance"],
                "status_norm": row["status_norm"],
                "protection_status": row["protection_status"],
                "safe_until_jst": row["safe_until_jst"],
                "frontline_group": group,
                "server_side": row["server_side"],
                "enemy_flag": row["enemy_flag"],
                "destroyed_flag": row["destroyed_flag"],
                "strategic_value": base_score,
                "risk_score": score,
                "risk_level": risk_level(score),
                "risk_note": "; ".join(notes),
            }
        )
    return rows


def merge_decision_rows(
    node_current_rows: list[dict[str, Any]],
    risk_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    risk_by_id = {row["node_id"]: row for row in risk_rows}
    rows: list[dict[str, Any]] = []
    for node_row in node_current_rows:
        risk_row = risk_by_id[node_row["node_id"]]
        rows.append(
            {
                "node_id": node_row["node_id"],
                "area": node_row["area"],
                "coord": node_row["coord"],
                "node_type_norm": node_row["node_type_norm"],
                "current_alliance": node_row["current_alliance"],
                "owner_server": node_row["owner_server"],
                "owner_server_source": node_row["owner_server_source"],
                "server_side": node_row["server_side"],
                "pact_status": node_row["pact_status"],
                "status_norm": node_row["status_norm"],
                "frontline_group": risk_row["frontline_group"],
                "enemy_flag": node_row["enemy_flag"],
                "destroyed_flag": node_row["destroyed_flag"],
                "strategic_value": risk_row["strategic_value"],
                "risk_score": risk_row["risk_score"],
                "risk_level": risk_row["risk_level"],
                "risk_note": risk_row["risk_note"],
                "confidence": node_row["confidence"],
                "memo": node_row["memo"],
            }
        )
    return rows


def sort_decision_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        rows,
        key=lambda row: (
            -int(row.get("risk_score") or 0),
            str(row.get("area") or ""),
            str(row.get("coord") or ""),
            str(row.get("node_id") or ""),
        ),
    )


def memo_short(value: Any, limit: int = 80) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def critical_action(row: dict[str, Any]) -> str:
    if row["destroyed_flag"] == "TRUE":
        return "破壊済み確認"
    if row["server_side"] == "enemy" and row["frontline_group"] != "other":
        return "奪還候補"
    if row["server_side"] == "enemy":
        return "敵支配確認"
    if row["server_side"] in {"self", "ally"} and row["frontline_group"] != "other":
        return "防衛候補"
    if row["server_side"] == "unknown" and row["current_alliance"]:
        return "所有者確認"
    return "監視継続"


def pact_related(row: dict[str, Any]) -> bool:
    return str(row.get("pact_status", "") or "") not in {"", "unknown", "attack_allowed"}


def enemy_invasion_action(row: dict[str, Any]) -> str:
    if pact_related(row):
        return "協定影響確認"
    if row["frontline_group"] == "frontline_core":
        return "防衛確認"
    if row["frontline_group"] == "frontline_adjacent":
        return "隣接確認"
    if row.get("to_server_side") == "self":
        return "防衛優先"
    if row.get("to_server_side") == "ally":
        return "味方連携確認"
    if not row.get("from_node_id") or not row.get("to_node_id"):
        return "地図確認"
    return "次回攻撃候補として監視"


def attack_action(row: dict[str, Any], city_destroy_enabled: bool) -> str:
    if row["node_type_norm"] == "city":
        return "都市破壊候補" if city_destroy_enabled else "都市破壊候補（時間外）"
    if row["frontline_group"] != "other":
        return "攻撃候補"
    if row["confidence"] in {"low", "unknown", ""}:
        return "偵察候補"
    return "奪還候補"


def priority(row: dict[str, Any]) -> str:
    if row["risk_level"] == "critical":
        return "critical"
    if row["risk_level"] == "high":
        return "high"
    if row["risk_level"] == "mid":
        return "mid"
    return "low"


def format_top_critical(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    formatted: list[dict[str, Any]] = []
    for rank, row in enumerate(rows[:TOP_LIMIT], start=1):
        formatted.append(
            {
                "rank": rank,
                "node_id": row["node_id"],
                "coord": row["coord"],
                "node_type_norm": row["node_type_norm"],
                "current_alliance": row["current_alliance"],
                "owner_server": row["owner_server"],
                "server_side": row["server_side"],
                "frontline_group": row["frontline_group"],
                "risk_score": row["risk_score"],
                "risk_level": row["risk_level"],
                "risk_reason": row["risk_note"],
                "recommended_action": critical_action(row),
                "confidence": row["confidence"],
                "memo_short": memo_short(row["memo"]),
            }
        )
    return formatted


def format_top_enemy_invasion(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    formatted: list[dict[str, Any]] = []
    for rank, row in enumerate(rows[:TOP_LIMIT], start=1):
        action_input = {**row, "from_node_id": row["node_id"], "to_node_id": "", "to_server_side": "ally"}
        formatted.append(
            {
                "rank": rank,
                "from_node_id": row["node_id"],
                "from_coord": row["coord"],
                "from_alliance": row["current_alliance"],
                "from_server": row["owner_server"],
                "to_node_id": "",
                "to_coord": "",
                "to_alliance": "#534/ally line",
                "to_server": "534/509/440/511",
                "target_type": row["node_type_norm"],
                "candidate_reason": row["risk_note"],
                "priority": priority(row),
                "recommended_action": enemy_invasion_action(action_input),
                "confidence": row["confidence"],
            }
        )
    return formatted


def format_top_attack(
    rows: list[dict[str, Any]],
    city_destroy_enabled: bool,
    city_destroy_window: str,
) -> list[dict[str, Any]]:
    formatted: list[dict[str, Any]] = []
    for rank, row in enumerate(rows[:TOP_LIMIT], start=1):
        formatted.append(
            {
                "rank": rank,
                "from_node_id": "",
                "from_coord": "",
                "from_alliance": "#534/ally attack group",
                "to_node_id": row["node_id"],
                "to_coord": row["coord"],
                "to_alliance": row["current_alliance"],
                "to_server": row["owner_server"],
                "target_type": row["node_type_norm"],
                "attack_reason": row["risk_note"],
                "priority": priority(row),
                "recommended_action": attack_action(row, city_destroy_enabled),
                "city_destroy_window": city_destroy_window if row["node_type_norm"] == "city" else "",
                "confidence": row["confidence"],
            }
        )
    return formatted


def edge_action_for_invasion(enemy_row: dict[str, Any], friendly_row: dict[str, Any] | None) -> str:
    if friendly_row is None:
        return "地図確認"
    group = frontline_group(str(enemy_row.get("from_coord", "") or ""))
    if group == "frontline_core":
        return "防衛確認"
    if group == "frontline_adjacent":
        return "隣接確認"
    if friendly_row.get("server_side") == "self":
        return "#534防衛優先"
    if friendly_row.get("server_side") == "ally":
        return "味方連携確認"
    return "監視継続"


def build_enemy_invasion_edges(
    top_enemy_rows: list[dict[str, Any]],
    node_current_by_id: dict[str, dict[str, Any]],
    adjacency: dict[str, set[str]],
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for enemy_row in top_enemy_rows:
        enemy_node_id = enemy_row.get("from_node_id", "")
        neighbors = [
            node_current_by_id[node_id]
            for node_id in sorted(adjacency.get(enemy_node_id, set()))
            if node_id in node_current_by_id and node_current_by_id[node_id].get("server_side") in {"self", "ally"}
        ]
        if not neighbors:
            output.append(
                {
                    "enemy_from_node": enemy_node_id,
                    "enemy_from_coord": enemy_row.get("from_coord", ""),
                    "enemy_from_alliance": enemy_row.get("from_alliance", ""),
                    "enemy_from_server": enemy_row.get("from_server", ""),
                    "friendly_to_node": "",
                    "friendly_to_coord": "",
                    "friendly_to_alliance": "",
                    "friendly_to_server": "",
                    "edge_type": "edge_unknown",
                    "risk_reason": enemy_row.get("candidate_reason", ""),
                    "recommended_action": "地図確認",
                    "confidence": enemy_row.get("confidence", ""),
                }
            )
            continue
        for friendly in sorted(neighbors, key=lambda row: (0 if row["server_side"] == "self" else 1, row["node_id"])):
            output.append(
                {
                    "enemy_from_node": enemy_node_id,
                    "enemy_from_coord": enemy_row.get("from_coord", ""),
                    "enemy_from_alliance": enemy_row.get("from_alliance", ""),
                    "enemy_from_server": enemy_row.get("from_server", ""),
                    "friendly_to_node": friendly.get("node_id", ""),
                    "friendly_to_coord": friendly.get("coord", ""),
                    "friendly_to_alliance": friendly.get("current_alliance", ""),
                    "friendly_to_server": friendly.get("owner_server", ""),
                    "edge_type": f"enemy_to_{friendly.get('server_side', 'unknown')}_adjacent",
                    "risk_reason": enemy_row.get("candidate_reason", ""),
                    "recommended_action": edge_action_for_invasion(enemy_row, friendly),
                    "confidence": enemy_row.get("confidence", ""),
                }
            )
    return output


def attack_edge_action(target_row: dict[str, Any], source_row: dict[str, Any] | None, city_destroy_enabled: bool) -> str:
    if source_row is None:
        return "地図確認"
    if target_row.get("target_type") == "city":
        return "都市破壊候補" if city_destroy_enabled else "都市破壊候補（時間外）"
    if source_row.get("server_side") == "self":
        return "攻撃候補"
    if source_row.get("server_side") == "ally":
        return "味方連携確認"
    return "監視継続"


def build_attack_edges(
    top_attack_rows: list[dict[str, Any]],
    node_current_by_id: dict[str, dict[str, Any]],
    adjacency: dict[str, set[str]],
    city_destroy_enabled: bool,
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for target_row in top_attack_rows:
        target_node_id = target_row.get("to_node_id", "")
        adjacent_sources = [
            node_current_by_id[node_id]
            for node_id in sorted(adjacency.get(target_node_id, set()))
            if node_id in node_current_by_id and node_current_by_id[node_id].get("server_side") in {"self", "ally"}
        ]
        self_sources = [row for row in adjacent_sources if row["server_side"] == "self"]
        ally_sources = [row for row in adjacent_sources if row["server_side"] == "ally"]
        selected_sources = self_sources or ally_sources
        if not selected_sources:
            output.append(
                {
                    "friendly_from_node": "",
                    "friendly_from_coord": "",
                    "friendly_from_alliance": "",
                    "friendly_from_server": "",
                    "enemy_to_node": target_node_id,
                    "enemy_to_coord": target_row.get("to_coord", ""),
                    "enemy_to_alliance": target_row.get("to_alliance", ""),
                    "enemy_to_server": target_row.get("to_server", ""),
                    "edge_type": "edge_unknown",
                    "attack_reason": target_row.get("attack_reason", ""),
                    "recommended_action": "地図確認",
                    "confidence": target_row.get("confidence", ""),
                }
            )
            continue
        for source in sorted(selected_sources, key=lambda row: (0 if row["server_side"] == "self" else 1, row["node_id"])):
            output.append(
                {
                    "friendly_from_node": source.get("node_id", ""),
                    "friendly_from_coord": source.get("coord", ""),
                    "friendly_from_alliance": source.get("current_alliance", ""),
                    "friendly_from_server": source.get("owner_server", ""),
                    "enemy_to_node": target_node_id,
                    "enemy_to_coord": target_row.get("to_coord", ""),
                    "enemy_to_alliance": target_row.get("to_alliance", ""),
                    "enemy_to_server": target_row.get("to_server", ""),
                    "edge_type": f"{source.get('server_side', 'unknown')}_to_enemy_adjacent",
                    "attack_reason": target_row.get("attack_reason", ""),
                    "recommended_action": attack_edge_action(target_row, source, city_destroy_enabled),
                    "confidence": target_row.get("confidence", ""),
                }
            )
    return output


def priority_from_reason(reason: str) -> str:
    score = sum(int(value) for value in re.findall(r"\+(\d+)", reason or ""))
    if score >= 90:
        return "critical"
    if score >= 60:
        return "high"
    if score >= 30:
        return "mid"
    return "low"


def attack_human_check(row: dict[str, Any]) -> str:
    action = str(row.get("recommended_action", "") or "")
    if row.get("edge_type") == "edge_unknown":
        return "発射元拠点確認; 地図確認"
    checks = ["発射元拠点確認"]
    if "都市破壊" in action:
        checks.append("都市破壊時間確認")
    if row.get("edge_type") == "ally_to_enemy_adjacent":
        checks.append("味方連携確認")
    checks.append("協定確認")
    return "; ".join(checks)


def invasion_human_check(row: dict[str, Any]) -> str:
    if not row.get("friendly_to_node"):
        return "防衛先確認; 地図確認"
    if str(row.get("friendly_to_server", "")) == SELF_SERVER:
        return "防衛ライン確認"
    return "味方連携確認; 防衛ライン確認"


def classify_attack_edges(
    attack_edges: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    output = {
        "server_534_attack_edges_self_v2.csv": [],
        "server_534_attack_edges_ally_v2.csv": [],
        "server_534_attack_edges_unknown_v2.csv": [],
    }
    for row in attack_edges:
        edge_type = str(row.get("edge_type", "") or "")
        classified = {
            **row,
            "review_priority": priority_from_reason(str(row.get("attack_reason", "") or "")),
            "human_check": attack_human_check(row),
        }
        if edge_type == "self_to_enemy_adjacent":
            classified["execution_class"] = "self_action"
            classified["recommended_owner"] = "#534"
            output["server_534_attack_edges_self_v2.csv"].append(classified)
        elif edge_type == "ally_to_enemy_adjacent":
            classified["execution_class"] = "ally_coordination"
            classified["recommended_owner"] = "#509/#440/#511"
            output["server_534_attack_edges_ally_v2.csv"].append(classified)
        else:
            classified["execution_class"] = "map_check_required"
            classified["recommended_owner"] = "R4/R5確認"
            output["server_534_attack_edges_unknown_v2.csv"].append(classified)
    return output


def classify_enemy_invasion_edges(
    enemy_invasion_edges: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    output = {
        "enemy_invasion_edges_self_defense_v2.csv": [],
        "enemy_invasion_edges_ally_defense_v2.csv": [],
        "enemy_invasion_edges_unknown_v2.csv": [],
    }
    for row in enemy_invasion_edges:
        friendly_server = str(row.get("friendly_to_server", "") or "")
        classified = {
            **row,
            "review_priority": priority_from_reason(str(row.get("risk_reason", "") or "")),
            "human_check": invasion_human_check(row),
        }
        if friendly_server == SELF_SERVER:
            classified["execution_class"] = "self_action"
            classified["recommended_owner"] = "#534"
            output["enemy_invasion_edges_self_defense_v2.csv"].append(classified)
        elif friendly_server in ALLY_SERVERS:
            classified["execution_class"] = "ally_coordination"
            classified["recommended_owner"] = "#509/#440/#511"
            output["enemy_invasion_edges_ally_defense_v2.csv"].append(classified)
        else:
            classified["execution_class"] = "map_check_required"
            classified["recommended_owner"] = "R4/R5確認"
            output["enemy_invasion_edges_unknown_v2.csv"].append(classified)
    return output


def markdown_escape(value: Any) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows[:EDGE_REVIEW_LIMIT]:
        lines.append("| " + " | ".join(markdown_escape(row.get(column, "")) for column in columns) + " |")
    if not rows:
        lines.append("| " + " | ".join("" for _ in columns) + " |")
    return "\n".join(lines)


def update_commander_review_edges(
    path: Path,
    classified_attack_edges: dict[str, list[dict[str, Any]]],
    classified_invasion_edges: dict[str, list[dict[str, Any]]],
) -> None:
    begin = "<!-- EDGE_CLASSIFICATION_BEGIN -->"
    end = "<!-- EDGE_CLASSIFICATION_END -->"
    attack_columns = [
        "friendly_from_coord",
        "friendly_from_alliance",
        "friendly_from_server",
        "enemy_to_coord",
        "enemy_to_alliance",
        "enemy_to_server",
        "review_priority",
        "recommended_action",
        "human_check",
        "confidence",
    ]
    invasion_columns = [
        "enemy_from_coord",
        "enemy_from_alliance",
        "enemy_from_server",
        "friendly_to_coord",
        "friendly_to_alliance",
        "friendly_to_server",
        "review_priority",
        "recommended_action",
        "human_check",
        "confidence",
    ]
    sections = [
        (
            "#534単独攻撃edge",
            classified_attack_edges["server_534_attack_edges_self_v2.csv"],
            attack_columns,
        ),
        (
            "味方連携攻撃edge",
            classified_attack_edges["server_534_attack_edges_ally_v2.csv"],
            attack_columns,
        ),
        (
            "地図確認が必要な攻撃候補",
            classified_attack_edges["server_534_attack_edges_unknown_v2.csv"],
            attack_columns,
        ),
        (
            "#534防衛edge",
            classified_invasion_edges["enemy_invasion_edges_self_defense_v2.csv"],
            invasion_columns,
        ),
        (
            "味方防衛edge",
            classified_invasion_edges["enemy_invasion_edges_ally_defense_v2.csv"],
            invasion_columns,
        ),
        (
            "地図確認が必要な敵侵攻候補",
            classified_invasion_edges["enemy_invasion_edges_unknown_v2.csv"],
            invasion_columns,
        ),
    ]
    block_lines = [
        begin,
        "",
        "## Edge候補の実行可能性分類",
        "",
        "これは作戦命令ではなく，edge候補の分類である。各セクションは最大10件まで表示する。",
    ]
    for title, rows, columns in sections:
        block_lines.extend(["", f"## {title}", "", markdown_table(rows, columns)])
    block_lines.extend(["", end, ""])
    block = "\n".join(block_lines)

    if path.exists():
        current = path.read_text(encoding="utf-8")
        pattern = re.compile(rf"\n?{re.escape(begin)}.*?{re.escape(end)}\n?", re.DOTALL)
        if pattern.search(current):
            updated = pattern.sub("\n\n" + block, current).rstrip() + "\n"
        else:
            updated = current.rstrip() + "\n\n" + block
    else:
        updated = "# 司令官CSVレビュー 2026-05-31\n\n" + block
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(updated, encoding="utf-8")


def build_decision_outputs(
    node_current_rows: list[dict[str, Any]],
    risk_rows: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    decision_rows = merge_decision_rows(node_current_rows, risk_rows)

    active_owned = {
        "owned",
        "owned_uncertain",
    }
    enemy_rows = [
        row
        for row in decision_rows
        if row["server_side"] == "enemy" and row["status_norm"] in active_owned
    ]
    friendly_rows = [
        row
        for row in decision_rows
        if row["server_side"] in {"self", "ally"} and row["status_norm"] in active_owned
    ]
    frontline_rows = [
        row
        for row in decision_rows
        if row["frontline_group"] != "other" and row["status_norm"] in active_owned
    ]
    enemy_invasion_rows = [
        row
        for row in decision_rows
        if row["server_side"] == "enemy"
        and row["status_norm"] in active_owned
        and row["frontline_group"] != "other"
    ]
    attack_rows = [
        row
        for row in decision_rows
        if row["server_side"] == "enemy"
        and row["status_norm"] in active_owned
        and row["node_type_norm"] in {"city", "fishery", "trade"}
    ]

    return {
        "current_enemy_nodes_v2.csv": sort_decision_rows(enemy_rows),
        "current_friendly_nodes_v2.csv": sort_decision_rows(friendly_rows),
        "server_534_frontline_risk_v2.csv": sort_decision_rows(frontline_rows),
        "enemy_invasion_candidates_v2.csv": sort_decision_rows(enemy_invasion_rows),
        "server_534_attack_candidates_v2.csv": sort_decision_rows(attack_rows),
    }


def build_commander_outputs(
    node_current_rows: list[dict[str, Any]],
    risk_rows: list[dict[str, Any]],
    decision_outputs: dict[str, list[dict[str, Any]]],
    review_outputs: dict[str, list[dict[str, Any]]],
    city_destroy_enabled: bool,
    city_destroy_window: dict[str, str],
) -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    risk_by_id = {row["node_id"]: row for row in risk_rows}
    level_counts = Counter(row["risk_level"] for row in risk_rows)
    unknown_owner_rows = [
        row
        for row in node_current_rows
        if row["owner_server"] == "" and row["current_alliance"] and row["status_norm"] in {"owned", "owned_uncertain"}
    ]
    destroyed_city_rows = [
        row
        for row in node_current_rows
        if row["node_type_norm"] == "city" and row["destroyed_flag"] == "TRUE"
    ]

    dashboard_rows = [
        {
            "metric": "battle_window_status",
            "value": city_destroy_window["label"],
            "note": f"{city_destroy_window['start_at_jst']} - {city_destroy_window['end_at_jst']}".strip(" -"),
        },
        {"metric": "server_day", "value": city_destroy_window["server_day"], "note": "JST based server day"},
        {
            "metric": "city_destroy_enabled",
            "value": str(city_destroy_enabled).upper(),
            "note": "city destroy candidates are time-sensitive",
        },
        {"metric": "critical risk count", "value": level_counts.get("critical", 0), "note": "risk_map_v2"},
        {"metric": "high risk count", "value": level_counts.get("high", 0), "note": "risk_map_v2"},
        {
            "metric": "current enemy nodes",
            "value": len(decision_outputs["current_enemy_nodes_v2.csv"]),
            "note": "current enemy-owned nodes",
        },
        {
            "metric": "current friendly nodes",
            "value": len(decision_outputs["current_friendly_nodes_v2.csv"]),
            "note": "current self/ally-owned nodes",
        },
        {
            "metric": "server_534 frontline risk count",
            "value": len(decision_outputs["server_534_frontline_risk_v2.csv"]),
            "note": "owned frontline rows for review",
        },
        {
            "metric": "enemy_invasion_candidates count",
            "value": len(decision_outputs["enemy_invasion_candidates_v2.csv"]),
            "note": "enemy-owned frontline candidates",
        },
        {
            "metric": "server_534_attack_candidates count",
            "value": len(decision_outputs["server_534_attack_candidates_v2.csv"]),
            "note": "enemy-owned attack-review candidates",
        },
        {
            "metric": "unknown owner count",
            "value": len(unknown_owner_rows),
            "note": "owned rows with current_alliance but unresolved owner_server",
        },
        {
            "metric": "type uncertain count",
            "value": len(review_outputs["type_uncertain_review_v2.csv"]),
            "note": "node type needs review",
        },
        {
            "metric": "safe time reference count",
            "value": len(review_outputs["safe_time_reference_review_v2.csv"]),
            "note": "safe_until_jst is reference only",
        },
        {"metric": "destroyed city count", "value": len(destroyed_city_rows), "note": "city rows only"},
    ]

    critical_rows = [
        row
        for row in merge_decision_rows(node_current_rows, risk_rows)
        if risk_by_id[row["node_id"]]["risk_level"] == "critical"
    ]
    critical_global_rows = sort_decision_rows(critical_rows)
    critical_534_rows = [
        row
        for row in critical_global_rows
        if row["area"] == "#534" or row["owner_server"] == SELF_SERVER or row["server_side"] == "self"
    ]
    city_destroy_window_label = (
        f"{city_destroy_window['label']} {city_destroy_window['start_at_jst']} - {city_destroy_window['end_at_jst']}"
        if city_destroy_enabled
        else "outside_city_destroy_window"
    )
    commander_outputs = {
        "top_critical_risks_global_v2.csv": format_top_critical(critical_global_rows),
        "top_critical_risks_534_v2.csv": format_top_critical(critical_534_rows),
        "top_enemy_invasion_candidates_v2.csv": format_top_enemy_invasion(
            decision_outputs["enemy_invasion_candidates_v2.csv"]
        ),
        "top_server_534_attack_targets_v2.csv": format_top_attack(
            decision_outputs["server_534_attack_candidates_v2.csv"],
            city_destroy_enabled,
            city_destroy_window_label,
        ),
    }
    return dashboard_rows, commander_outputs


def build_review_outputs(
    node_current_rows: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    unknown_owner_rows = [
        row
        for row in node_current_rows
        if row["owner_server"] == "" and row["current_alliance"] and row["status_norm"] in {"owned", "owned_uncertain"}
    ]
    type_uncertain_rows = [
        row
        for row in node_current_rows
        if row["node_type_norm"] == "unknown"
    ]
    safe_time_rows = [
        row
        for row in node_current_rows
        if row["status_norm"] in {"owned", "owned_uncertain"} and row["protection_status"] in {"safe_time_known", "safe_time_missing"}
    ]
    return {
        "unknown_owner_review_v2.csv": unknown_owner_rows,
        "type_uncertain_review_v2.csv": type_uncertain_rows,
        "safe_time_reference_review_v2.csv": safe_time_rows,
    }


def print_summary(
    node_current_rows: list[dict[str, Any]],
    alert_rows: list[dict[str, Any]],
    risk_rows: list[dict[str, Any]],
    decision_outputs: dict[str, list[dict[str, Any]]],
    dashboard_rows: list[dict[str, Any]],
    commander_outputs: dict[str, list[dict[str, Any]]],
    review_outputs: dict[str, list[dict[str, Any]]],
    city_destroy_enabled: bool,
    enemy_invasion_edges: list[dict[str, Any]],
    attack_edges: list[dict[str, Any]],
    classified_attack_edges: dict[str, list[dict[str, Any]]],
    classified_invasion_edges: dict[str, list[dict[str, Any]]],
) -> None:
    level_counts = Counter(row["risk_level"] for row in risk_rows)
    print(f"node_current_v2 rows={len(node_current_rows)}")
    print(f"alerts_v2 rows={len(alert_rows)}")
    print(f"risk_map_v2 rows={len(risk_rows)}")
    print(f"critical count={level_counts.get('critical', 0)}")
    print(f"high count={level_counts.get('high', 0)}")
    print(f"mid count={level_counts.get('mid', 0)}")
    print(f"low count={level_counts.get('low', 0)}")
    for name, rows in decision_outputs.items():
        print(f"{name} rows={len(rows)}")
    print(f"commander_dashboard_v2 rows={len(dashboard_rows)}")
    for name, rows in commander_outputs.items():
        print(f"{name} rows={len(rows)}")
    for name, rows in review_outputs.items():
        print(f"{name} rows={len(rows)}")
    recommended_actions = Counter(
        str(row.get("recommended_action", ""))
        for rows in commander_outputs.values()
        for row in rows
        if row.get("recommended_action")
    )
    confidences = Counter(
        str(row.get("confidence", ""))
        for rows in commander_outputs.values()
        for row in rows
        if row.get("confidence")
    )
    print("recommended_action breakdown")
    for action, count in sorted(recommended_actions.items()):
        print(f"{action}={count}")
    print("confidence breakdown")
    for confidence, count in sorted(confidences.items()):
        print(f"{confidence}={count}")
    print(f"unknown owner count={len(review_outputs['unknown_owner_review_v2.csv'])}")
    print(f"city_destroy_enabled={str(city_destroy_enabled).upper()}")
    print(f"enemy_invasion_edges rows={len(enemy_invasion_edges)}")
    print(f"server_534_attack_edges rows={len(attack_edges)}")
    print(
        "enemy_invasion_edges with friendly_to_node blank="
        f"{sum(1 for row in enemy_invasion_edges if not row.get('friendly_to_node'))}"
    )
    print(
        "server_534_attack_edges with friendly_from_node blank="
        f"{sum(1 for row in attack_edges if not row.get('friendly_from_node'))}"
    )
    print(
        "self-source attack edges count="
        f"{sum(1 for row in attack_edges if str(row.get('edge_type', '')).startswith('self_'))}"
    )
    print(
        "ally-source attack edges count="
        f"{sum(1 for row in attack_edges if str(row.get('edge_type', '')).startswith('ally_'))}"
    )
    print(f"self attack edges count={len(classified_attack_edges['server_534_attack_edges_self_v2.csv'])}")
    print(f"ally attack edges count={len(classified_attack_edges['server_534_attack_edges_ally_v2.csv'])}")
    print(f"unknown attack edges count={len(classified_attack_edges['server_534_attack_edges_unknown_v2.csv'])}")
    print(f"self defense edges count={len(classified_invasion_edges['enemy_invasion_edges_self_defense_v2.csv'])}")
    print(f"ally defense edges count={len(classified_invasion_edges['enemy_invasion_edges_ally_defense_v2.csv'])}")
    print(f"unknown defense edges count={len(classified_invasion_edges['enemy_invasion_edges_unknown_v2.csv'])}")


def main() -> None:
    args = parse_args()
    node_status_path = Path(args.node_status)
    state_json_path = Path(args.state_json)
    alliance_directory_path = Path(args.alliance_directory)
    pacts_path = Path(args.pacts)
    output_dir = Path(args.output_dir)
    commander_review_path = Path(args.commander_review)

    payload = load_node_status(node_status_path)
    state = load_state(state_json_path)
    nodes = payload["nodes"]
    directory = read_alliance_directory(alliance_directory_path)
    read_csv(pacts_path)

    updated_at_jst = str(payload.get("generated_at_jst") or datetime.now(JST).isoformat(timespec="seconds"))
    generated_at_jst = parse_datetime(updated_at_jst)
    city_destroy_enabled, city_destroy_window = active_city_destroy_window(generated_at_jst)
    node_current_rows = build_node_current_rows(nodes, directory, updated_at_jst)
    node_current_by_id = {row["node_id"]: row for row in node_current_rows}
    adjacency = build_adjacency(state)
    alert_rows = build_alert_rows(node_current_rows)
    risk_rows = build_risk_rows(node_current_rows)
    decision_outputs = build_decision_outputs(node_current_rows, risk_rows)
    review_outputs = build_review_outputs(node_current_rows)
    dashboard_rows, commander_outputs = build_commander_outputs(
        node_current_rows,
        risk_rows,
        decision_outputs,
        review_outputs,
        city_destroy_enabled,
        city_destroy_window,
    )

    write_csv(output_dir / "node_current_v2.csv", NODE_CURRENT_COLUMNS, node_current_rows)
    write_csv(output_dir / "alerts_v2.csv", ALERT_COLUMNS, alert_rows)
    write_csv(output_dir / "risk_map_v2.csv", RISK_COLUMNS, risk_rows)
    for filename, rows in decision_outputs.items():
        write_csv(output_dir / filename, DECISION_COLUMNS, rows)
    write_csv(output_dir / "commander_dashboard_v2.csv", COMMANDER_DASHBOARD_COLUMNS, dashboard_rows)
    commander_columns = {
        "top_critical_risks_global_v2.csv": TOP_CRITICAL_COLUMNS,
        "top_critical_risks_534_v2.csv": TOP_CRITICAL_COLUMNS,
        "top_enemy_invasion_candidates_v2.csv": TOP_ENEMY_INVASION_COLUMNS,
        "top_server_534_attack_targets_v2.csv": TOP_ATTACK_COLUMNS,
    }
    for filename, rows in commander_outputs.items():
        write_csv(output_dir / filename, commander_columns[filename], rows)
    write_csv(output_dir / "top_critical_risks_v2.csv", TOP_CRITICAL_COLUMNS, commander_outputs["top_critical_risks_534_v2.csv"])
    write_csv(
        output_dir / "top_server_534_attack_candidates_v2.csv",
        TOP_ATTACK_COLUMNS,
        commander_outputs["top_server_534_attack_targets_v2.csv"],
    )
    for filename, rows in review_outputs.items():
        write_csv(output_dir / filename, NODE_CURRENT_COLUMNS, rows)
    enemy_invasion_edges = build_enemy_invasion_edges(
        commander_outputs["top_enemy_invasion_candidates_v2.csv"],
        node_current_by_id,
        adjacency,
    )
    attack_edges = build_attack_edges(
        commander_outputs["top_server_534_attack_targets_v2.csv"],
        node_current_by_id,
        adjacency,
        city_destroy_enabled,
    )
    write_csv(output_dir / "top_enemy_invasion_edges_v2.csv", ENEMY_INVASION_EDGE_COLUMNS, enemy_invasion_edges)
    write_csv(output_dir / "top_server_534_attack_edges_v2.csv", ATTACK_EDGE_COLUMNS, attack_edges)
    classified_attack_edges = classify_attack_edges(attack_edges)
    classified_invasion_edges = classify_enemy_invasion_edges(enemy_invasion_edges)
    for filename, rows in classified_attack_edges.items():
        write_csv(output_dir / filename, CLASSIFIED_ATTACK_EDGE_COLUMNS, rows)
    for filename, rows in classified_invasion_edges.items():
        write_csv(output_dir / filename, CLASSIFIED_ENEMY_INVASION_EDGE_COLUMNS, rows)
    update_commander_review_edges(commander_review_path, classified_attack_edges, classified_invasion_edges)
    print_summary(
        node_current_rows,
        alert_rows,
        risk_rows,
        decision_outputs,
        dashboard_rows,
        commander_outputs,
        review_outputs,
        city_destroy_enabled,
        enemy_invasion_edges,
        attack_edges,
        classified_attack_edges,
        classified_invasion_edges,
    )


if __name__ == "__main__":
    main()
