# File Inventory - 2026-05-03

`/Users/mba2025/Documents/S6` の棚卸しメモ。GitHubはprivateかつドキュメント中心で運用する。

## GitHubに載せる中心ファイル

| パス | 役割 |
|---|---|
| `README.md` | プロジェクト入口。作業方針と素材の扱い |
| `docs/00_project_brief.md` | 現在の前提、未確定事項、意思決定基準 |
| `docs/season6_mechanics.md` | S6仕様の確認済み/仮説/要確認整理 |
| `docs/context_handoff.md` | 新しいチャットへ渡す引き継ぎ |
| `docs/previous_thread_summary.md` | 前回チャットの復元メモ |
| `docs/content_review_2026-05-03.md` | 2026-05-03時点のレビュー |
| `research/source_log.md` | 画像、外部情報、ローカル生成データの根拠ログ |
| `strategy/season6_strategy.md` | JDX/#534の戦略本体 |
| `strategy/action_plan.md` | 今後の実行タスク |
| `strategy/jdx_executive_brief_v2.md` | 幹部Discord向けの現行共有文 |
| `strategy/member_start_checklist.md` | 連盟員向けの開始前・開始直後チェックリスト |
| `strategy/week1_member_playbook.md` | Week 1メンバー向け指示 |
| `strategy/map_planning_notes.md` | Cpt Hedge地図とゲーム内配置を使った作戦メモ |
| `strategy/cpt_hedge_map_workflow.md` | Cpt Hedge地図を非公式作戦図として使うための運用手順 |
| `strategy/server_strategy_comparison_2026-05-03.md` | 戦力CSVから作成したサーバー別比較 |

## 旧版・補助ファイル

| パス | 扱い |
|---|---|
| `strategy/jdx_executive_brief.md` | 旧版。#509連携を強めに置いた初期案として残す。共有はv2を使う |
| `templates/screenshot_review_template.md` | 画像確認の記録テンプレート |

## ローカル管理素材

| パス/種類 | 扱い |
|---|---|
| `IMG_*.PNG` | 一次資料。移動せず、必要な事実だけ `research/source_log.md` へ転記 |
| `S6powerrank/IMG_*.PNG` | 戦力ランキング再集計用の画像群。ローカル/Drive管理 |
| `outputs/lastwar_s6_latest_*.csv` | 戦力ランキングCSV。`.gitignore` 対象 |
| `outputs/s6powerrank_*.csv` | `S6powerrank/` 画像から再集計した戦力ランキングCSV。`.gitignore` 対象 |
| `outputs/sheets/*.xlsx` | 戦力ランキングのExcel整理版。`.gitignore` 対象 |
| `outputs/lastwar_s6_latest_summary.md` | 戦力サマリー。必要な結論は `strategy/server_strategy_comparison_2026-05-03.md` に転記済み |
| `outputs/ocr_all_images_2026-05-03.txt` | OCR作業出力。ローカル参照用 |
| `map_exports/` | Cpt HedgeのJSONエクスポートや作業途中画像。作業用ローカル保存 |
| `build_lastwar_s6_latest_rankings.py` | CSV生成用ローカルスクリプト。GitHub docs-only方針では除外 |
| `tools/vision_ocr.swift` | OCR補助ローカルツール。GitHub docs-only方針では除外 |
| `node_modules/` | スプレッドシート作成時のローカル依存。GitHubには含めない |

## 現時点の注意

- READMEのファイル索引を通常の入口にする。
- `outputs/`、画像、ローカル抽出スクリプトはGitHubへ載せない前提。
- 戦力数値は新しい `outputs/s6powerrank_*.csv` を優先し、共有用の判断は `strategy/server_strategy_comparison_2026-05-03.md` を見る。
- 地図配置は `strategy/map_planning_notes.md` を正とする。
- 幹部Discord共有は `strategy/jdx_executive_brief_v2.md` を使う。
