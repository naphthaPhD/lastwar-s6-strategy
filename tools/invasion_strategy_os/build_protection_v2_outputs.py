from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


BASE_DIR = Path("sample_output/sheet_migration")
NODE_CURRENT = BASE_DIR / "node_current_v2.csv"
STATE_JSON = Path("sample_output/state.json")

BLUE_ALLIANCES = {
    "4tH",
    "59U",
    "89M",
    "CROW",
    "Dao",
    "JDX",
    "KTVS",
    "MOE",
    "RGWC",
    "Ryu1",
    "SHA",
    "SHA0",
    "Skh",
    "Trh",
    "f4j",
    "kOi",
    "moca",
    "nO9",
    "noI",
    "sg3",
    "w6F",
}
GREEN_ALLIANCES = {
    "2N7",
    "AoW",
    "BAJ",
    "BHE",
    "CZX",
    "DaNG",
    "FHX",
    "GcC",
    "GoDs",
    "IMP",
    "JL0",
    "JlZ",
    "KOCH",
    "MOn",
    "OOEf",
    "OTT",
    "OWM",
    "SVa",
    "SVo",
    "SsQ",
    "TaW",
    "TrX",
    "VEX",
    "WoW3",
    "eXt",
    "sbM",
    "tWD",
}
RED_ALLIANCES = {
    "476A",
    "476B",
    "476C",
    "476H",
    "476K",
    "476M",
    "476T",
    "476X",
    "476Z",
    "476d",
    "AAOA",
    "ALj",
    "BgNa",
    "Bye",
    "CDf8",
    "Digg",
    "EDFS",
    "GX99",
    "IXM",
    "K4TR",
    "Kfk",
    "Lghs",
    "MtG",
    "R6q",
    "RCON",
    "Stj",
    "TIKW",
    "TkTk",
    "UMN",
    "WUG",
    "fzn",
    "one",
    "xjR",
}

TARGET_COLUMNS = [
    "ライン",
    "対象種別",
    "座標",
    "拠点ID",
    "現所有連盟",
    "所有サーバ",
    "色区分",
    "敵味方判定",
    "現在状態",
    "目標開放",
    "必要な実行時間帯",
    "対象判定",
    "除外理由",
    "確認状態",
    "メモ",
]
SOURCE_COLUMNS = [
    "候補連盟",
    "サーバ",
    "色区分",
    "候補座標",
    "拠点ID",
    "隣接先候補数",
    "盟約確認",
    "当日取得上限",
    "使用可否",
    "除外理由",
    "確認状態",
    "メモ",
]
CANDIDATE_COLUMNS = [
    "優先度",
    "対象ライン",
    "対象座標",
    "対象拠点ID",
    "対象連盟",
    "目標開放",
    "実行時間帯",
    "候補連盟",
    "候補サーバ",
    "候補座標",
    "候補拠点ID",
    "隣接確認",
    "盟約確認",
    "取得上限確認",
    "安全時間影響",
    "候補判定",
    "理由",
    "メモ",
]
NOTICE_COLUMNS = [
    "実行日",
    "実行時間帯",
    "担当連盟",
    "担当者",
    "対象ライン",
    "対象座標",
    "目的",
    "やること",
    "注意",
    "実行後報告",
    "確認状態",
    "結果",
    "スクショ/リンク",
    "メモ",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return [{key: (value or "").strip() for key, value in row.items()} for row in csv.DictReader(fh)]


def write_csv(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def color_side(row: dict[str, str]) -> str:
    alliance = row.get("current_alliance", "")
    server = row.get("owner_server", "")
    if alliance in BLUE_ALLIANCES or server == "534":
        return "blue"
    if alliance in GREEN_ALLIANCES or server in {"509", "440", "511"}:
        return "green"
    if alliance in RED_ALLIANCES or server in {"503", "480", "523", "476"}:
        return "red"
    if row.get("status_norm") == "destroyed":
        return "destroyed"
    return "unknown"


def target_judgement(row: dict[str, str]) -> tuple[str, str]:
    side = color_side(row)
    if row.get("status_norm") != "owned":
        return "除外", "所有中ではない"
    if side == "blue":
        return "候補", "青文字連盟所有"
    if side == "green":
        return "除外", "緑文字連盟は今回は運用対象外"
    if side == "red":
        return "除外", "敵候補のため保護パン対象外"
    if not row.get("current_alliance"):
        return "要確認", "所有連盟不明"
    return "要確認", "連盟所属未解決"


def line_of(coord: str) -> str:
    return coord[0]


def target_release(line: str) -> str:
    return "次回交戦日 7:00" if line == "A" else "次回交戦日 23:00"


def execution_window(line: str) -> str:
    return "23:00〜翌6:59" if line == "A" else "11:00〜14:59 / 16:00〜22:59"


def priority(line: str) -> str:
    return "高" if line == "A" else "中"


def full_coord(row: dict[str, str]) -> str:
    return f"{row.get('area', '')} {row.get('coord', '')}".strip()


def build_adjacency(state: dict[str, Any]) -> dict[str, set[str]]:
    adjacency: dict[str, set[str]] = defaultdict(set)
    for edge in state.get("connections", []):
        source = edge.get("source", "")
        target = edge.get("target", "")
        if source and target:
            adjacency[source].add(target)
            adjacency[target].add(source)
    return adjacency


def build_outputs() -> dict[str, Any]:
    rows = read_csv(NODE_CURRENT)
    by_id = {row["node_id"]: row for row in rows}
    state = json.loads(STATE_JSON.read_text(encoding="utf-8"))
    adjacency = build_adjacency(state)

    ab_rows = [
        row
        for row in rows
        if row.get("node_type_norm") == "fishery" and re.match(r"^[AB]-\d+$", row.get("coord", ""))
    ]
    ab_rows.sort(key=lambda row: (row.get("area", ""), line_of(row["coord"]), int(row["coord"].split("-")[1])))

    target_rows: list[dict[str, str]] = []
    for row in ab_rows:
        judgement, reason = target_judgement(row)
        line = line_of(row["coord"])
        target_rows.append(
            {
                "ライン": line,
                "対象種別": "漁場",
                "座標": full_coord(row),
                "拠点ID": row["node_id"],
                "現所有連盟": row.get("current_alliance", ""),
                "所有サーバ": row.get("owner_server", "") or "unknown",
                "色区分": color_side(row),
                "敵味方判定": row.get("server_side", ""),
                "現在状態": row.get("status_norm", ""),
                "目標開放": target_release(line),
                "必要な実行時間帯": execution_window(line),
                "対象判定": judgement,
                "除外理由": "" if judgement == "候補" else reason,
                "確認状態": "未確認" if judgement == "候補" else ("要確認" if judgement == "要確認" else "除外"),
                "メモ": reason,
            }
        )

    blue_targets = [row for row in ab_rows if target_judgement(row)[0] == "候補"]
    candidate_rows: list[dict[str, str]] = []
    source_pool: dict[str, dict[str, str]] = {}
    for target in blue_targets:
        line = line_of(target["coord"])
        found = False
        for node_id in sorted(adjacency.get(target["node_id"], [])):
            source = by_id.get(node_id)
            if not source:
                continue
            if source.get("status_norm") != "owned":
                continue
            if color_side(source) != "blue":
                continue
            if not source.get("current_alliance"):
                continue
            if source["node_id"] == target["node_id"]:
                continue
            if source.get("current_alliance") == target.get("current_alliance"):
                continue
            found = True
            area_note = "同一エリア" if source.get("area") == target.get("area") else "別エリア"
            candidate_rows.append(
                {
                    "優先度": priority(line),
                    "対象ライン": line,
                    "対象座標": full_coord(target),
                    "対象拠点ID": target["node_id"],
                    "対象連盟": target.get("current_alliance", ""),
                    "目標開放": target_release(line),
                    "実行時間帯": execution_window(line),
                    "候補連盟": source.get("current_alliance", ""),
                    "候補サーバ": source.get("owner_server", "") or "534候補",
                    "候補座標": full_coord(source),
                    "候補拠点ID": source["node_id"],
                    "隣接確認": "隣接あり",
                    "盟約確認": "要確認",
                    "取得上限確認": "要確認",
                    "安全時間影響": "15:00〜16:00除外" if line == "B" else "なし",
                    "候補判定": "候補",
                    "理由": f"青文字連盟の隣接拠点（{area_note}）",
                    "メモ": "同一連盟は除外済み。盟約と取得上限は実行前確認。",
                }
            )
            source_pool[source["node_id"]] = source
        if not found:
            candidate_rows.append(
                {
                    "優先度": priority(line),
                    "対象ライン": line,
                    "対象座標": full_coord(target),
                    "対象拠点ID": target["node_id"],
                    "対象連盟": target.get("current_alliance", ""),
                    "目標開放": target_release(line),
                    "実行時間帯": execution_window(line),
                    "候補連盟": "",
                    "候補サーバ": "",
                    "候補座標": "",
                    "候補拠点ID": "",
                    "隣接確認": "隣接候補なし",
                    "盟約確認": "",
                    "取得上限確認": "",
                    "安全時間影響": "15:00〜16:00除外" if line == "B" else "なし",
                    "候補判定": "地図確認",
                    "理由": "青文字の隣接候補が見つからない",
                    "メモ": "map_review_v2で手動確認",
                }
            )

    source_rows: list[dict[str, str]] = []
    for source in sorted(source_pool.values(), key=lambda row: (row.get("current_alliance", ""), row.get("area", ""), row.get("coord", ""))):
        adjacent_count = sum(1 for row in candidate_rows if row.get("候補拠点ID") == source["node_id"])
        source_rows.append(
            {
                "候補連盟": source.get("current_alliance", ""),
                "サーバ": source.get("owner_server", "") or "534候補",
                "色区分": "青",
                "候補座標": full_coord(source),
                "拠点ID": source["node_id"],
                "隣接先候補数": str(adjacent_count),
                "盟約確認": "要確認",
                "当日取得上限": "要確認",
                "使用可否": "要確認",
                "除外理由": "",
                "確認状態": "未確認",
                "メモ": "青文字の隣接候補。担当者と上限を確認。",
            }
        )

    notice_rows = build_notice_rows(blue_targets, candidate_rows)
    return {
        "target_rows": target_rows,
        "source_rows": source_rows,
        "candidate_rows": candidate_rows,
        "notice_rows": notice_rows,
        "summary": {
            "protection_targets_v2 rows": len(target_rows),
            "blue target rows": len(blue_targets),
            "protection_source_pool_v2 rows": len(source_rows),
            "protection_candidates_v2 rows": len(candidate_rows),
            "protection_notice_v2 action rows": len(blue_targets),
            "target side counts": dict(Counter(row["色区分"] for row in target_rows)),
            "candidate judgement counts": dict(Counter(row["候補判定"] for row in candidate_rows)),
            "notice status counts": dict(
                Counter(row["確認状態"] for row in notice_rows if row["対象ライン"] in {"A", "B"})
            ),
        },
    }


def build_notice_rows(blue_targets: list[dict[str, str]], candidate_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    assignment_count: Counter[str] = Counter()
    notice_rows: list[dict[str, str]] = []
    for target in sorted(blue_targets, key=lambda row: (line_of(row["coord"]), row.get("area", ""), int(row["coord"].split("-")[1]))):
        line = line_of(target["coord"])
        candidates = [
            row
            for row in candidate_rows
            if row.get("対象拠点ID") == target["node_id"] and row.get("候補判定") == "候補"
        ]

        def candidate_key(row: dict[str, str]) -> tuple[int, int, int, str, str]:
            source_area = row["候補座標"].split()[0] if row.get("候補座標") else ""
            same_area = 0 if source_area == target.get("area", "") else 1
            area_534 = 0 if row.get("候補座標", "").startswith("#534 ") else 1
            return (same_area, area_534, assignment_count[row["候補連盟"]], row["候補連盟"], row["候補座標"])

        chosen = sorted(candidates, key=candidate_key)[0] if candidates else None
        if chosen:
            assignment_count[chosen["候補連盟"]] += 1
            assignee = chosen["候補連盟"]
            status = "候補"
            memo = f"候補元: {chosen['候補座標']} / 盟約・取得上限は要確認"
        else:
            assignee = ""
            status = "地図確認"
            memo = "青文字の隣接候補なし。手動で発射元確認。"

        notice_rows.append(
            {
                "実行日": "次回交戦日",
                "実行時間帯": execution_window(line),
                "担当連盟": assignee,
                "担当者": "",
                "対象ライン": line,
                "対象座標": full_coord(target),
                "目的": f"{target_release(line)} 開放に寄せる",
                "やること": "対象漁場をワンパンし、占領しきらず防衛成功で保護を付ける",
                "注意": "取得しない。盟約相手に攻撃しない。取得上限を確認。"
                + (" 15:00〜16:00は実行しない。" if line == "B" else ""),
                "実行後報告": "対象座標・実行時刻・結果スクショを報告",
                "確認状態": status,
                "結果": "",
                "スクショ/リンク": "",
                "メモ": memo,
            }
        )

    notice_rows.extend(
        [
            {"目的": "【保護パン依頼】"},
            {"実行日": "目的", "目的": "Aラインは次回交戦日7:00開放、Bラインは次回交戦日23:00開放に寄せます。"},
            {"実行日": "実行時間", "目的": "Aライン：23:00〜翌6:59 / Bライン：11:00〜14:59 または 16:00〜22:59"},
            {"実行日": "禁止時間", "目的": "15:00〜16:00は安全時間のため実行しないでください。"},
            {"実行日": "注意", "目的": "取得しない。盟約相手に攻撃しない。取得上限に達している人は担当しない。"},
        ]
    )
    return [{column: row.get(column, "") for column in NOTICE_COLUMNS} for row in notice_rows]


def main() -> None:
    outputs = build_outputs()
    write_csv(BASE_DIR / "protection_targets_v2.csv", TARGET_COLUMNS, outputs["target_rows"])
    write_csv(BASE_DIR / "protection_source_pool_v2.csv", SOURCE_COLUMNS, outputs["source_rows"])
    write_csv(BASE_DIR / "protection_candidates_v2.csv", CANDIDATE_COLUMNS, outputs["candidate_rows"])
    write_csv(BASE_DIR / "protection_notice_v2.csv", NOTICE_COLUMNS, outputs["notice_rows"])

    for key, value in outputs["summary"].items():
        print(f"{key}={value}")


if __name__ == "__main__":
    main()
