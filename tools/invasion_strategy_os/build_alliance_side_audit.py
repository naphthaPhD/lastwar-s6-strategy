from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


OUTPUT_CSV = Path("sample_output/sheet_migration/alliance_side_audit_v2.csv")
OUTPUT_MD = Path("analysis/alliance_side_audit_2026-05-31.md")
BRIEFING_MD = Path("analysis/r4_r5_briefing_2026-05-31.md")
BASE_DIR = Path("sample_output/sheet_migration")

SELF_SERVER = "534"
ALLY_SERVERS = {"509", "440", "511"}
KNOWN_SELF_OR_ALLY = {
    "JDX",
    "4tH",
    "SHA",
    "nO9",
    "KTVS",
    "MOE",
    "89M",
    "Dao",
    "w6F",
    "sg3",
    "kOi",
    "f4j",
    "SsQ",
    "FHX",
    "BAJ",
    "GoDs",
    "VEX",
}
KNOWN_ENEMY = {
    "476A",
    "476B",
    "476C",
    "476d",
    "476K",
    "476M",
    "476X",
    "476Z",
    "ALj",
    "BgNa",
    "TkTk",
    "AAOA",
    "Lghs",
    "GX99",
    "Stj",
    "fzn",
    "WUG",
    "EDFS",
    "K4TR",
    "NBNH",
}
AUDIT_COLUMNS = [
    "alliance",
    "resolved_server",
    "server_side",
    "source",
    "appearance_count",
    "appears_in_briefing",
    "appears_as_enemy",
    "appears_as_self_or_ally",
    "appears_in_areas",
    "sample_nodes",
    "risk_flag",
    "review_status",
    "manual_server_override",
    "manual_note",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return [{key: (value or "").strip() for key, value in row.items()} for row in csv.DictReader(fh)]


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=AUDIT_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def bool_text(value: bool) -> str:
    return "TRUE" if value else "FALSE"


def add_audit(audits: dict[str, dict[str, Any]], alliance: str) -> dict[str, Any] | None:
    alliance = (alliance or "").strip()
    if not alliance:
        return None
    if alliance not in audits:
        audits[alliance] = {
            "alliance": alliance,
            "appearance_count": 0,
            "appears_in_briefing": False,
            "appears_as_enemy": False,
            "appears_as_self_or_ally": False,
            "areas": set(),
            "sample_nodes": [],
            "servers": set(),
            "sources": set(),
        }
    return audits[alliance]


def add_occurrence(
    audits: dict[str, dict[str, Any]],
    alliance: str,
    *,
    server: str = "",
    side: str = "",
    area: str = "",
    node_id: str = "",
    source: str = "",
) -> None:
    audit = add_audit(audits, alliance)
    if audit is None:
        return
    audit["appearance_count"] += 1
    if server:
        audit["servers"].add(str(server))
    if side == "enemy":
        audit["appears_as_enemy"] = True
    if side in {"self", "ally"}:
        audit["appears_as_self_or_ally"] = True
    if area:
        audit["areas"].add(area)
    if node_id and node_id not in audit["sample_nodes"]:
        audit["sample_nodes"].append(node_id)
    if source:
        audit["sources"].add(source)


def server_side(server: str) -> str:
    if server == SELF_SERVER:
        return "self"
    if server in ALLY_SERVERS:
        return "ally"
    if server in {"", "unknown"} or server.startswith("multiple:"):
        return "unknown"
    return "enemy"


def node_area(node_id: str) -> str:
    match = re.match(r"^(#[^:]+):", node_id or "")
    return match.group(1) if match else ""


def exact_tag_in_text(tag: str, text: str) -> bool:
    return bool(re.search(rf"(?<![A-Za-z0-9]){re.escape(tag)}(?![A-Za-z0-9])", text))


def directory_lookup(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    lookup: dict[str, dict[str, str]] = {}
    for row in rows:
        server = row.get("server", "")
        source = f"alliance_directory:{row.get('source', '') or 'unknown'}"
        for key in [row.get("alliance", "")] + [alias.strip() for alias in row.get("alliance_alias", "").split(",")]:
            if key:
                lookup.setdefault(key, {"server": server, "source": source})
    return lookup


def collect_audits() -> list[dict[str, Any]]:
    audits: dict[str, dict[str, Any]] = {}
    briefing_text = BRIEFING_MD.read_text(encoding="utf-8") if BRIEFING_MD.exists() else ""
    directory = directory_lookup(read_csv(BASE_DIR / "alliance_directory.csv"))

    for alliance in sorted(KNOWN_SELF_OR_ALLY | KNOWN_ENEMY | set(directory)):
        audit = add_audit(audits, alliance)
        if audit is not None and alliance in directory:
            audit["servers"].add(directory[alliance]["server"])
            audit["sources"].add(directory[alliance]["source"])

    for row in read_csv(BASE_DIR / "node_current_v2.csv"):
        alliance = row.get("current_alliance", "")
        side = row.get("server_side", "")
        server = row.get("owner_server", "")
        source = row.get("owner_server_source", "")
        add_occurrence(
            audits,
            alliance,
            server=server,
            side=side,
            area=row.get("area", ""),
            node_id=row.get("node_id", ""),
            source=f"node_current:{source or 'unknown'}",
        )

    for filename, side in [
        ("current_enemy_nodes_v2.csv", "enemy"),
        ("current_friendly_nodes_v2.csv", "self_or_ally"),
    ]:
        for row in read_csv(BASE_DIR / filename):
            actual_side = "ally" if side == "self_or_ally" else "enemy"
            add_occurrence(
                audits,
                row.get("current_alliance", ""),
                server=row.get("owner_server", ""),
                side=actual_side if row.get("server_side", "") != "self" else "self",
                area=row.get("area", ""),
                node_id=row.get("node_id", ""),
                source=filename,
            )

    edge_specs = [
        ("server_534_attack_edges_self_v2.csv", "friendly_from_alliance", "friendly_from_server", "friendly_from_node", "self"),
        ("server_534_attack_edges_self_v2.csv", "enemy_to_alliance", "enemy_to_server", "enemy_to_node", "enemy"),
        ("server_534_attack_edges_ally_v2.csv", "friendly_from_alliance", "friendly_from_server", "friendly_from_node", "ally"),
        ("server_534_attack_edges_ally_v2.csv", "enemy_to_alliance", "enemy_to_server", "enemy_to_node", "enemy"),
        ("enemy_invasion_edges_self_defense_v2.csv", "enemy_from_alliance", "enemy_from_server", "enemy_from_node", "enemy"),
        ("enemy_invasion_edges_self_defense_v2.csv", "friendly_to_alliance", "friendly_to_server", "friendly_to_node", "self"),
        ("enemy_invasion_edges_ally_defense_v2.csv", "enemy_from_alliance", "enemy_from_server", "enemy_from_node", "enemy"),
        ("enemy_invasion_edges_ally_defense_v2.csv", "friendly_to_alliance", "friendly_to_server", "friendly_to_node", "ally"),
    ]
    for filename, alliance_col, server_col, node_col, side in edge_specs:
        for row in read_csv(BASE_DIR / filename):
            node_id = row.get(node_col, "")
            add_occurrence(
                audits,
                row.get(alliance_col, ""),
                server=row.get(server_col, ""),
                side=side,
                area=node_area(node_id),
                node_id=node_id,
                source=f"edge:{filename}:{alliance_col}",
            )

    for alliance, audit in audits.items():
        if exact_tag_in_text(alliance, briefing_text):
            audit["appears_in_briefing"] = True

    rows: list[dict[str, Any]] = []
    for alliance, audit in audits.items():
        servers = {server for server in audit["servers"] if server}
        if len(servers) == 1:
            resolved_server = next(iter(servers))
        elif len(servers) > 1:
            resolved_server = "multiple:" + "|".join(sorted(servers))
        else:
            resolved_server = "unknown"
        side = server_side(resolved_server)
        areas = sorted(audit["areas"])
        reasons = []
        if audit["appears_as_enemy"] and "#534" in areas:
            reasons.append("enemy_in_534_area")
        if audit["appears_as_enemy"] and alliance in KNOWN_SELF_OR_ALLY:
            reasons.append("enemy_but_known_self_or_ally_candidate")
        if resolved_server == "unknown":
            reasons.append("unknown_resolved_server")
        if resolved_server.startswith("multiple:"):
            reasons.append("multiple_server_inference")
        review_status = "needs_review" if reasons else "ok"
        rows.append(
            {
                "alliance": alliance,
                "resolved_server": resolved_server,
                "server_side": side,
                "source": "; ".join(sorted(audit["sources"])),
                "appearance_count": audit["appearance_count"],
                "appears_in_briefing": bool_text(audit["appears_in_briefing"]),
                "appears_as_enemy": bool_text(audit["appears_as_enemy"]),
                "appears_as_self_or_ally": bool_text(audit["appears_as_self_or_ally"]),
                "appears_in_areas": "; ".join(areas),
                "sample_nodes": "; ".join(audit["sample_nodes"][:8]),
                "risk_flag": "; ".join(reasons),
                "review_status": review_status,
                "manual_server_override": "",
                "manual_note": "",
            }
        )

    rows.sort(key=lambda row: (0 if row["risk_flag"] else 1, 0 if row["appears_in_briefing"] == "TRUE" else 1, row["alliance"]))
    return rows


def markdown_table(rows: list[dict[str, Any]], columns: list[str], limit: int | None = None) -> str:
    selected = rows if limit is None else rows[:limit]
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in selected:
        lines.append("| " + " | ".join(str(row.get(col, "")).replace("|", "\\|") for col in columns) + " |")
    return "\n".join(lines)


def write_markdown(rows: list[dict[str, Any]]) -> None:
    risk_rows = [row for row in rows if row["risk_flag"]]
    unknown_rows = [row for row in rows if row["resolved_server"] == "unknown"]
    maybe_self_ally_rows = [
        row for row in rows if row["appears_as_enemy"] == "TRUE" and row["alliance"] in KNOWN_SELF_OR_ALLY
    ]
    focus = [row for row in rows if row["alliance"] in {"SHA", "nO9", "JDX", "4tH"}]
    columns = [
        "alliance",
        "resolved_server",
        "server_side",
        "appearance_count",
        "appears_as_enemy",
        "appears_as_self_or_ally",
        "appears_in_areas",
        "risk_flag",
        "review_status",
    ]
    lines = [
        "# 連盟所属・敵味方判定監査 2026-05-31",
        "",
        "これは作戦命令ではなく，R4/R5ブリーフィングに使われた連盟判定の監査表である。",
        "`manual_server_override` と `manual_note` はCSV側で人間が追記するための空欄であり，自動適用しない。",
        "",
        "## 1. Summary",
        "",
        f"- alliance_side_audit rows: {len(rows)}",
        f"- risk_flag rows: {len(risk_rows)}",
        f"- unknown resolved_server rows: {len(unknown_rows)}",
        f"- appears_as_enemy but maybe self/ally rows: {len(maybe_self_ally_rows)}",
        f"- side_check_required rows: {sum(1 for row in rows if row['review_status'] == 'needs_review')}",
        "",
        "## 2. 最優先確認",
        "",
        markdown_table(focus, columns),
        "",
        "## 3. risk_flagあり",
        "",
        markdown_table(risk_rows, columns, limit=80),
        "",
        "## 4. unknown resolved_server",
        "",
        markdown_table(unknown_rows, ["alliance", "appearance_count", "appears_in_briefing", "appears_in_areas", "sample_nodes", "risk_flag"], limit=80),
        "",
        "## 5. 人間レビュー手順",
        "",
        "1. `SHA` と `nO9` の所属サーバを最初に確認する。",
        "2. 味方候補が `appears_as_enemy=TRUE` になっている行は，攻撃候補として扱わない。",
        "3. 修正が必要な場合は，まず `alliance_side_audit_v2.csv` の `manual_server_override` と `manual_note` に記入する。",
        "4. 自動適用はまだ行わず，`alliance_directory.csv` への反映は人間承認後に行う。",
        "",
        "## 6. Files referenced",
        "",
        "- `analysis/r4_r5_briefing_2026-05-31.md`",
        "- `sample_output/sheet_migration/node_current_v2.csv`",
        "- `sample_output/sheet_migration/alliance_directory.csv`",
        "- `sample_output/sheet_migration/current_enemy_nodes_v2.csv`",
        "- `sample_output/sheet_migration/current_friendly_nodes_v2.csv`",
        "- `sample_output/sheet_migration/server_534_attack_edges_self_v2.csv`",
        "- `sample_output/sheet_migration/server_534_attack_edges_ally_v2.csv`",
        "- `sample_output/sheet_migration/enemy_invasion_edges_self_defense_v2.csv`",
        "- `sample_output/sheet_migration/enemy_invasion_edges_ally_defense_v2.csv`",
    ]
    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows = collect_audits()
    write_csv(OUTPUT_CSV, rows)
    write_markdown(rows)
    by_alliance = {row["alliance"]: row for row in rows}
    risk_rows = [row for row in rows if row["risk_flag"]]
    unknown_rows = [row for row in rows if row["resolved_server"] == "unknown"]
    maybe_self_ally_rows = [
        row for row in rows if row["appears_as_enemy"] == "TRUE" and row["alliance"] in KNOWN_SELF_OR_ALLY
    ]
    print(f"alliance_side_audit rows={len(rows)}")
    print(f"risk_flag rows={len(risk_rows)}")
    print(f"unknown resolved_server rows={len(unknown_rows)}")
    print(f"appears_as_enemy but maybe self/ally rows={len(maybe_self_ally_rows)}")
    print(f"side_check_required rows={sum(1 for row in rows if row['review_status'] == 'needs_review')}")
    for alliance in ["SHA", "nO9", "JDX", "4tH"]:
        row = by_alliance.get(alliance, {})
        print(
            f"{alliance} classification="
            f"server:{row.get('resolved_server', 'missing')},"
            f"side:{row.get('server_side', 'missing')},"
            f"risk:{row.get('risk_flag', '') or 'none'}"
        )


if __name__ == "__main__":
    main()
