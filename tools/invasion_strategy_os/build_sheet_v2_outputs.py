from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


DEFAULT_NODE_STATUS = "sample_output/sheet_migration/node_status.json"
DEFAULT_ALLIANCE_DIRECTORY = "sample_output/sheet_migration/alliance_directory.csv"
DEFAULT_PACTS = "sample_output/sheet_migration/pacts.csv"
DEFAULT_OUTPUT_DIR = "sample_output/sheet_migration"
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
    "confidence",
]

TOP_LIMIT = 30


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate #534 Sheet V2 CSVs from node_status.json."
    )
    parser.add_argument("--node-status", default=DEFAULT_NODE_STATUS, help="Input node_status.json.")
    parser.add_argument(
        "--alliance-directory",
        default=DEFAULT_ALLIANCE_DIRECTORY,
        help="Input alliance_directory.csv for owner_server fallback.",
    )
    parser.add_argument("--pacts", default=DEFAULT_PACTS, help="Input pacts.csv, read only.")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="Directory for V2 CSV outputs.")
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


def normalize_server(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    match = re.search(r"(\d{3})", text)
    return match.group(1) if match else ""


def read_alliance_directory(path: Path) -> dict[str, tuple[str, str]]:
    directory: dict[str, tuple[str, str]] = {}
    for row in read_csv(path):
        server = normalize_server(row.get("server", ""))
        alliance = row.get("alliance", "").strip()
        if server and alliance:
            directory.setdefault(alliance.casefold(), (server, "alliance_directory"))
        for alias in re.split(r"[,;/\s]+", row.get("alliance_alias", "")):
            alias = alias.strip()
            if server and alias:
                directory.setdefault(alias.casefold(), (server, "alliance_alias"))
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
    owner_server = normalize_server(node.get("owner_server", ""))
    owner_source = str(node.get("owner_server_source", "") or "unknown")
    if owner_server:
        return owner_server, owner_source

    owner_alliance = str(node.get("owner_alliance", "") or "").strip()
    if owner_alliance:
        match = re.match(r"^#?(\d{3})", owner_alliance)
        if match:
            return match.group(1), "numeric_prefix"
        directory_match = directory.get(owner_alliance.casefold())
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
            "server_side": server_side(owner_server, current_alliance),
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


def enemy_invasion_action(row: dict[str, Any]) -> str:
    if row["pact_status"] and row["pact_status"] != "unknown":
        return "協定影響確認"
    if row["frontline_group"] != "other":
        return "防衛ライン確認"
    return "次回攻撃候補として監視"


def attack_action(row: dict[str, Any]) -> str:
    if row["node_type_norm"] == "city":
        return "都市破壊候補"
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
                "recommended_action": enemy_invasion_action(row),
                "confidence": row["confidence"],
            }
        )
    return formatted


def format_top_attack(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
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
                "recommended_action": attack_action(row),
                "confidence": row["confidence"],
            }
        )
    return formatted


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
    commander_outputs = {
        "top_critical_risks_v2.csv": format_top_critical(sort_decision_rows(critical_rows)),
        "top_enemy_invasion_candidates_v2.csv": format_top_enemy_invasion(
            decision_outputs["enemy_invasion_candidates_v2.csv"]
        ),
        "top_server_534_attack_candidates_v2.csv": format_top_attack(
            decision_outputs["server_534_attack_candidates_v2.csv"]
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


def main() -> None:
    args = parse_args()
    node_status_path = Path(args.node_status)
    alliance_directory_path = Path(args.alliance_directory)
    pacts_path = Path(args.pacts)
    output_dir = Path(args.output_dir)

    payload = load_node_status(node_status_path)
    nodes = payload["nodes"]
    directory = read_alliance_directory(alliance_directory_path)
    read_csv(pacts_path)

    updated_at_jst = str(payload.get("generated_at_jst") or datetime.now(JST).isoformat(timespec="seconds"))
    node_current_rows = build_node_current_rows(nodes, directory, updated_at_jst)
    alert_rows = build_alert_rows(node_current_rows)
    risk_rows = build_risk_rows(node_current_rows)
    decision_outputs = build_decision_outputs(node_current_rows, risk_rows)
    review_outputs = build_review_outputs(node_current_rows)
    dashboard_rows, commander_outputs = build_commander_outputs(
        node_current_rows,
        risk_rows,
        decision_outputs,
        review_outputs,
    )

    write_csv(output_dir / "node_current_v2.csv", NODE_CURRENT_COLUMNS, node_current_rows)
    write_csv(output_dir / "alerts_v2.csv", ALERT_COLUMNS, alert_rows)
    write_csv(output_dir / "risk_map_v2.csv", RISK_COLUMNS, risk_rows)
    for filename, rows in decision_outputs.items():
        write_csv(output_dir / filename, DECISION_COLUMNS, rows)
    write_csv(output_dir / "commander_dashboard_v2.csv", COMMANDER_DASHBOARD_COLUMNS, dashboard_rows)
    commander_columns = {
        "top_critical_risks_v2.csv": TOP_CRITICAL_COLUMNS,
        "top_enemy_invasion_candidates_v2.csv": TOP_ENEMY_INVASION_COLUMNS,
        "top_server_534_attack_candidates_v2.csv": TOP_ATTACK_COLUMNS,
    }
    for filename, rows in commander_outputs.items():
        write_csv(output_dir / filename, commander_columns[filename], rows)
    for filename, rows in review_outputs.items():
        write_csv(output_dir / filename, NODE_CURRENT_COLUMNS, rows)
    print_summary(
        node_current_rows,
        alert_rows,
        risk_rows,
        decision_outputs,
        dashboard_rows,
        commander_outputs,
        review_outputs,
    )


if __name__ == "__main__":
    main()
