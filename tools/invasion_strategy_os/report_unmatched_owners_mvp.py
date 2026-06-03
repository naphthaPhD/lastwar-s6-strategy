from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_OWNERSHIP_CURRENT = "sample_output/sheet_migration/ownership_current.csv"
DEFAULT_NODE_STATUS = "sample_output/sheet_migration/node_status.json"
DEFAULT_PACTS = "sample_output/sheet_migration/pacts.csv"
DEFAULT_ALLIANCE_DIRECTORY = "sample_output/sheet_migration/alliance_directory.csv"
DEFAULT_UNMATCHED_OUTPUT = "sample_output/sheet_migration/unmatched_owners.csv"
DEFAULT_CANDIDATES_OUTPUT = "sample_output/sheet_migration/pacts_candidates.csv"
ALLY_ALLIANCES = {"JDX", "Sq", "SsQ", "God", "GoDs"}
ENEMY_SERVERS = {"503", "476", "480", "523"}
SAMPLE_LIMIT = 8


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Report unmatched owner alliances for #534 MVP pact enrichment."
    )
    parser.add_argument(
        "--ownership-current",
        default=DEFAULT_OWNERSHIP_CURRENT,
        help="Input ownership_current.csv path.",
    )
    parser.add_argument(
        "--node-status",
        default=DEFAULT_NODE_STATUS,
        help="Input node_status.json path.",
    )
    parser.add_argument(
        "--pacts",
        default=DEFAULT_PACTS,
        help="Optional pacts.csv path. Read only, not modified.",
    )
    parser.add_argument(
        "--alliance-directory",
        default=DEFAULT_ALLIANCE_DIRECTORY,
        help="Optional alliance_directory.csv path. Read only, not modified.",
    )
    parser.add_argument(
        "--unmatched-output",
        default=DEFAULT_UNMATCHED_OUTPUT,
        help="Output unmatched_owners.csv path.",
    )
    parser.add_argument(
        "--candidates-output",
        default=DEFAULT_CANDIDATES_OUTPUT,
        help="Output pacts_candidates.csv path.",
    )
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return [{key: (value or "").strip() for key, value in row.items()} for row in csv.DictReader(fh)]


def read_node_status(path: Path) -> dict[str, dict[str, Any]]:
    with path.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)
    return payload.get("nodes", {})


def infer_server(owner_alliance: str) -> str:
    match = re.match(r"^(\d{3})", str(owner_alliance or "").strip())
    return match.group(1) if match else ""


def normalize_server(value: str) -> str:
    return str(value or "").strip().lstrip("#")


def read_alliance_directory(path: Path) -> tuple[dict[str, str], dict[str, str]]:
    by_alliance: dict[str, str] = {}
    by_alias: dict[str, str] = {}
    for row in read_csv(path):
        server = normalize_server(row.get("server", ""))
        alliance = row.get("alliance", "").strip()
        if not server or not alliance:
            continue
        by_alliance.setdefault(alliance, server)
        for alias in row.get("alliance_alias", "").split(","):
            alias = alias.strip()
            if alias:
                by_alias.setdefault(alias, server)
    return by_alliance, by_alias


def directory_match(
    owner_alliance: str,
    by_alliance: dict[str, str],
    by_alias: dict[str, str],
) -> tuple[str, str]:
    if owner_alliance in by_alliance:
        return by_alliance[owner_alliance], "alliance"
    if owner_alliance in by_alias:
        return by_alias[owner_alliance], "alias"
    return "", "none"


def node_needs_review(node: dict[str, Any]) -> bool:
    warnings = set(node.get("warnings", []))
    owner_alliance = str(node.get("owner_alliance", "") or "").strip()
    owner_server = str(node.get("owner_server", "") or "").strip()
    return (
        node.get("affiliation") == "unknown"
        or "unknown_affiliation" in warnings
        or bool(owner_alliance and not owner_server)
        or node.get("pact_status") == "unknown"
    )


def reason_for_node(node: dict[str, Any]) -> str:
    warnings = set(node.get("warnings", []))
    owner_alliance = str(node.get("owner_alliance", "") or "").strip()
    owner_server = str(node.get("owner_server", "") or "").strip()
    if "pact_time_parse_error" in warnings:
        return "parse_error"
    if "pact_expired" in warnings:
        return "pact_expired"
    if not owner_alliance:
        return "owner_alliance_empty"
    if node.get("affiliation") == "unknown" or node.get("pact_status") == "unknown":
        return "missing_from_pacts"
    if not owner_server:
        return "owner_server_missing"
    return "unknown"


def choose_reason(reasons: Counter[str]) -> str:
    priority = [
        "parse_error",
        "pact_expired",
        "owner_alliance_empty",
        "missing_from_pacts",
        "owner_server_missing",
        "unknown",
    ]
    for reason in priority:
        if reasons.get(reason):
            return reason
    return "unknown"


def compact_counts(counter: Counter[str]) -> str:
    return json.dumps(dict(counter.most_common()), ensure_ascii=False, separators=(",", ":"))


def current_affiliation(counter: Counter[str]) -> str:
    if not counter:
        return "unknown"
    return counter.most_common(1)[0][0] or "unknown"


def suggested_affiliation(owner_alliance: str, inferred_server: str, directory_server: str) -> tuple[str, str]:
    if owner_alliance in ALLY_ALLIANCES:
        return "ally", "high"
    if owner_alliance in ENEMY_SERVERS or inferred_server in ENEMY_SERVERS or directory_server in ENEMY_SERVERS:
        return "enemy", "medium"
    return "unknown", "low"


def existing_pact_keys(pacts_path: Path) -> set[tuple[str, str]]:
    keys: set[tuple[str, str]] = set()
    for row in read_csv(pacts_path):
        keys.add((normalize_server(row.get("server", "")), row.get("alliance", "")))
    return keys


def collect_groups(
    nodes: dict[str, dict[str, Any]],
    directory_by_alliance: dict[str, str],
    directory_by_alias: dict[str, str],
) -> tuple[dict[str, dict[str, Any]], int]:
    groups: dict[str, dict[str, Any]] = {}
    blank_owner_node_count = 0

    for node_id, node in nodes.items():
        if not node_needs_review(node):
            continue

        owner_alliance = str(node.get("owner_alliance", "") or "").strip()
        if not owner_alliance:
            blank_owner_node_count += 1
        directory_server, directory_match_type = directory_match(
            owner_alliance,
            directory_by_alliance,
            directory_by_alias,
        )
        key = owner_alliance
        group = groups.setdefault(
            key,
            {
                "owner_alliance": owner_alliance,
                "inferred_server": infer_server(owner_alliance),
                "directory_server": directory_server,
                "directory_match_type": directory_match_type,
                "node_count": 0,
                "area_counts": Counter(),
                "node_type_counts": Counter(),
                "sample_node_ids": [],
                "sample_node_labels": [],
                "affiliations": Counter(),
                "reasons": Counter(),
            },
        )
        if not group["directory_server"] and directory_server:
            group["directory_server"] = directory_server
            group["directory_match_type"] = directory_match_type
        group["node_count"] += 1
        group["area_counts"].update([str(node.get("area", "") or "")])
        group["node_type_counts"].update([str(node.get("node_type", "unknown") or "unknown")])
        group["affiliations"].update([str(node.get("affiliation", "unknown") or "unknown")])
        group["reasons"].update([reason_for_node(node)])
        if len(group["sample_node_ids"]) < SAMPLE_LIMIT:
            group["sample_node_ids"].append(node_id)
        if len(group["sample_node_labels"]) < SAMPLE_LIMIT:
            group["sample_node_labels"].append(str(node.get("node_label", "") or ""))

    return groups, blank_owner_node_count


def build_unmatched_rows(groups: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for group in groups.values():
        rows.append(
            {
                "owner_alliance": group["owner_alliance"],
                "inferred_server": group["inferred_server"],
                "directory_server": group["directory_server"],
                "directory_match_type": group["directory_match_type"],
                "node_count": str(group["node_count"]),
                "area_counts": compact_counts(group["area_counts"]),
                "node_type_counts": compact_counts(group["node_type_counts"]),
                "sample_node_ids": ";".join(group["sample_node_ids"]),
                "sample_node_labels": ";".join(group["sample_node_labels"]),
                "current_affiliation": current_affiliation(group["affiliations"]),
                "reason": choose_reason(group["reasons"]),
            }
        )
    return sorted(rows, key=lambda row: (-int(row["node_count"]), row["owner_alliance"]))


def build_candidate_rows(
    groups: dict[str, dict[str, Any]],
    pact_keys: set[tuple[str, str]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for group in groups.values():
        owner_alliance = group["owner_alliance"]
        if not owner_alliance:
            continue

        inferred_server = group["inferred_server"]
        directory_server = group["directory_server"]
        candidate_server = inferred_server or directory_server
        suggestion, confidence = suggested_affiliation(owner_alliance, inferred_server, directory_server)
        if (candidate_server, owner_alliance) in pact_keys:
            note = "already in pacts.csv but still unmatched"
        else:
            note = ""
        rows.append(
            {
                "server": candidate_server,
                "alliance": owner_alliance,
                "directory_server": directory_server,
                "directory_match_type": group["directory_match_type"],
                "suggested_affiliation": suggestion,
                "pact_status": "attack_allowed" if suggestion != "unknown" else "unknown",
                "confidence": confidence,
                "reason": choose_reason(group["reasons"]),
                "node_count": str(group["node_count"]),
                "note": note,
            }
        )
    return sorted(rows, key=lambda row: (-int(row["node_count"]), row["alliance"]))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def print_inspection(
    unmatched_rows: list[dict[str, str]],
    candidate_rows: list[dict[str, str]],
    blank_owner_node_count: int,
) -> None:
    unmatched_node_count = sum(int(row["node_count"]) for row in unmatched_rows)
    owner_rows = [row for row in unmatched_rows if row["owner_alliance"]]

    print("Unmatched owners MVP inspection")
    print(f"unmatched_owner_alliance_count={len(owner_rows)}")
    print(f"unmatched_node_count={unmatched_node_count}")
    print(f"blank_owner_alliance_node_count={blank_owner_node_count}")
    print(f"pacts_candidate_count={len(candidate_rows)}")
    print("top_20_unmatched_owners")
    for row in owner_rows[:20]:
        candidate = next((c for c in candidate_rows if c["alliance"] == row["owner_alliance"]), {})
        print(
            f"{row['owner_alliance']}\t"
            f"nodes={row['node_count']}\t"
            f"inferred_server={row['inferred_server']}\t"
            f"directory_server={row['directory_server']}\t"
            f"directory_match_type={row['directory_match_type']}\t"
            f"suggested={candidate.get('suggested_affiliation', 'unknown')}\t"
            f"reason={row['reason']}"
        )


def main() -> int:
    args = parse_args()
    ownership_current_path = Path(args.ownership_current)
    node_status_path = Path(args.node_status)
    pacts_path = Path(args.pacts)
    alliance_directory_path = Path(args.alliance_directory)
    unmatched_output_path = Path(args.unmatched_output)
    candidates_output_path = Path(args.candidates_output)

    read_csv(ownership_current_path)
    directory_by_alliance, directory_by_alias = read_alliance_directory(alliance_directory_path)
    nodes = read_node_status(node_status_path)
    groups, blank_owner_node_count = collect_groups(nodes, directory_by_alliance, directory_by_alias)
    unmatched_rows = build_unmatched_rows(groups)
    candidate_rows = build_candidate_rows(groups, existing_pact_keys(pacts_path))

    write_csv(
        unmatched_output_path,
        unmatched_rows,
        [
            "owner_alliance",
            "inferred_server",
            "directory_server",
            "directory_match_type",
            "node_count",
            "area_counts",
            "node_type_counts",
            "sample_node_ids",
            "sample_node_labels",
            "current_affiliation",
            "reason",
        ],
    )
    write_csv(
        candidates_output_path,
        candidate_rows,
        [
            "server",
            "alliance",
            "directory_server",
            "directory_match_type",
            "suggested_affiliation",
            "pact_status",
            "confidence",
            "reason",
            "node_count",
            "note",
        ],
    )
    print_inspection(unmatched_rows, candidate_rows, blank_owner_node_count)
    print(f"unmatched_output={unmatched_output_path}")
    print(f"candidates_output={candidates_output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
