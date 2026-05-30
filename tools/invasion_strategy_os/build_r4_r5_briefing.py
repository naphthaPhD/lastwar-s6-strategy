from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


BASE_DIR = Path("sample_output/sheet_migration")
COMMANDER_REVIEW = Path("analysis/commander_review_2026-05-31.md")
OUTPUT_PATH = Path("analysis/r4_r5_briefing_2026-05-31.md")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return [{key: (value or "").strip() for key, value in row.items()} for row in csv.DictReader(fh)]


def dashboard_value(rows: list[dict[str, str]], metric: str) -> str:
    for row in rows:
        if row.get("metric") == metric:
            return row.get("value", "")
    return ""


def count_section_rows(path: Path, start_marker: str, end_marker: str) -> int:
    text = path.read_text(encoding="utf-8")
    start = text.find(start_marker)
    if start < 0:
        return 0
    end = text.find(end_marker, start)
    section = text[start:] if end < 0 else text[start:end]
    count = 0
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if "---" in stripped or "rank" in stripped:
            continue
        count += 1
    return count


def md_escape(value: Any) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def md_table(rows: list[dict[str, str]], columns: list[str], limit: int) -> str:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows[:limit]:
        lines.append("| " + " | ".join(md_escape(row.get(column, "")) for column in columns) + " |")
    if not rows:
        lines.append("| " + " | ".join("" for _ in columns) + " |")
    return "\n".join(lines)


def build_briefing() -> dict[str, int | bool]:
    dashboard = read_csv(BASE_DIR / "commander_dashboard_v2.csv")
    self_attack = read_csv(BASE_DIR / "server_534_attack_edges_self_v2.csv")
    ally_attack = read_csv(BASE_DIR / "server_534_attack_edges_ally_v2.csv")
    unknown_attack = read_csv(BASE_DIR / "server_534_attack_edges_unknown_v2.csv")
    self_defense = read_csv(BASE_DIR / "enemy_invasion_edges_self_defense_v2.csv")
    ally_defense = read_csv(BASE_DIR / "enemy_invasion_edges_ally_defense_v2.csv")
    unknown_defense = read_csv(BASE_DIR / "enemy_invasion_edges_unknown_v2.csv")

    destroyed_534_critical = count_section_rows(COMMANDER_REVIEW, "## 2.", "## 3.")
    city_destroy_enabled = dashboard_value(dashboard, "city_destroy_enabled")

    defense_columns = [
        "enemy_from_coord",
        "enemy_from_alliance",
        "enemy_from_server",
        "friendly_to_coord",
        "friendly_to_alliance",
        "recommended_action",
        "human_check",
    ]
    attack_columns = [
        "friendly_from_coord",
        "friendly_from_alliance",
        "enemy_to_coord",
        "enemy_to_alliance",
        "enemy_to_server",
        "recommended_action",
        "human_check",
    ]
    ally_attack_columns = [
        "friendly_from_coord",
        "friendly_from_alliance",
        "friendly_from_server",
        "enemy_to_coord",
        "enemy_to_alliance",
        "enemy_to_server",
        "recommended_action",
        "human_check",
    ]
    ally_defense_columns = [
        "enemy_from_coord",
        "enemy_from_alliance",
        "enemy_from_server",
        "friendly_to_coord",
        "friendly_to_alliance",
        "friendly_to_server",
        "recommended_action",
        "human_check",
    ]

    self_defense_display = self_defense[:7]
    self_attack_display = self_attack[:7]
    ally_attack_display = ally_attack[:5]
    ally_defense_display = ally_defense[:5]

    lines = [
        "# R4/R5 1枚ブリーフィング 2026-05-31",
        "",
        "## 1. 現状サマリー",
        "",
        f"- #534破壊済み重要都市：{destroyed_534_critical}件",
        f"- #534単独攻撃edge：{len(self_attack)}件",
        f"- #534防衛edge：{len(self_defense)}件",
        f"- 味方連携攻撃edge：{len(ally_attack)}件",
        f"- 味方防衛edge：{len(ally_defense)}件",
        f"- 地図確認待ち：攻撃{len(unknown_attack)}件，防衛{len(unknown_defense)}件",
        f"- city_destroy_enabled：{city_destroy_enabled}",
        "",
        "## 2. まず確認すべき#534防衛ライン",
        "",
        md_table(self_defense_display, defense_columns, 7),
        "",
        "## 3. #534単独で検討できる攻撃候補",
        "",
        md_table(self_attack_display, attack_columns, 7),
        "",
        "## 4. 味方連携が必要な候補",
        "",
        "### ally attack edges",
        "",
        md_table(ally_attack_display, ally_attack_columns, 5),
        "",
        "### ally defense edges",
        "",
        md_table(ally_defense_display, ally_defense_columns, 5),
        "",
        "## 5. 地図確認待ち",
        "",
        f"- unknown attack edges count：{len(unknown_attack)}",
        f"- unknown defense edges count：{len(unknown_defense)}",
        "",
        "## 6. 注意書き",
        "",
        "- これは作戦命令ではなく，自動生成された候補の整理である。",
        "- confidence=medium の候補は，地図・協定・チャット状況の人間確認が必要。",
        "- 都市破壊候補は，city_destroy_enabled が TRUE の時間帯のみ有効。",
        "- edge_unknown は命令に使わず，地図確認キューとして扱う。",
    ]
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return {
        "exists": OUTPUT_PATH.exists(),
        "self_defense_rows_displayed": len(self_defense_display),
        "self_attack_rows_displayed": len(self_attack_display),
        "ally_attack_rows_displayed": len(ally_attack_display),
        "ally_defense_rows_displayed": len(ally_defense_display),
        "unknown_attack_count": len(unknown_attack),
        "unknown_defense_count": len(unknown_defense),
    }


def main() -> None:
    result = build_briefing()
    print(f"r4_r5_briefing exists={str(result['exists']).upper()}")
    print(f"self defense rows displayed={result['self_defense_rows_displayed']}")
    print(f"self attack rows displayed={result['self_attack_rows_displayed']}")
    ally_sections_displayed = (
        int(result["ally_attack_rows_displayed"]) > 0
        and int(result["ally_defense_rows_displayed"]) > 0
    )
    print(f"ally sections displayed={str(ally_sections_displayed).upper()}")
    unknown_counts_displayed = (
        int(result["unknown_attack_count"]) >= 0
        and int(result["unknown_defense_count"]) >= 0
    )
    print(f"unknown counts displayed={str(unknown_counts_displayed).upper()}")


if __name__ == "__main__":
    main()
