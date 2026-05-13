# File Inventory - 2026-05-03

`/Users/mba2025/Documents/S6` の棚卸しメモ。GitHubはprivateかつドキュメント中心で運用する。

## GitHubに載せる中心ファイル

| パス | 役割 |
|---|---|
| `README.md` | プロジェクト入口。作業方針と素材の扱い |
| `docs/00_project_brief.md` | 現在の前提、未確定事項、意思決定基準 |
| `docs/season6_mechanics.md` | S6仕様の確認済み/仮説/要確認整理 |
| `docs/english_discord_season6_delta_2026-05-13.md` | 公式英語版Discord `#season-6` の差分抽出。日本語版で未記録/弱かったStaff・Mod・Advisor回答と要確認の観測を分離 |
| `docs/japanese_discord_season6_delta_2026-05-13.md` | 公式日本語Discord `#🐊シーズン6-シャドウジャングル` HTML全件走査の差分抽出。盟約更新後挙動、巨大花未適用観測、最新日本語ログの補強を分離 |
| `docs/context_handoff.md` | 新しいチャットへ渡す引き継ぎ |
| `docs/previous_thread_summary.md` | 前回チャットの復元メモ |
| `docs/shadow_jungle_info_previous_thread.md` | 前回チャット復元メモからJDX方針を除いた情報抽出版 |
| `docs/content_review_2026-05-03.md` | 2026-05-03時点のレビュー |
| `research/source_log.md` | 画像、外部情報、ローカル生成データの根拠ログ |
| `strategy/season6_strategy.md` | JDX/#534の戦略本体 |
| `strategy/hero_power_growth_by_spend.md` | 無課金・微課金・廃課金別の英雄戦力育成方針 |
| `strategy/action_plan.md` | 今後の実行タスク |
| `strategy/jdx_executive_brief_v2.md` | 幹部Discord向けの現行共有文 |
| `strategy/member_start_checklist.md` | 連盟員向けの開始前・開始直後チェックリスト |
| `strategy/week1_member_playbook.md` | Week 1メンバー向け指示 |
| `strategy/509_week2_proposal_2026-05-12.md` | #509大統領・作戦担当へ送るWeek 2中央入口/#503方面提案文 |
| `strategy/map_planning_notes.md` | Cpt Hedge地図とゲーム内配置を使った作戦メモ |
| `strategy/base_occupation_plan_2026-05-12.md` | 7日目までの占領予定図を使った拠点取得・担当境界・中央入口・防衛ライン・戦力比較反映の判断メモ |
| `strategy/476_invasion_map_assessment_2026-05-07.md` | #476の中央侵攻/#534妨害ルート評価 |
| `strategy/cpt_hedge_map_workflow.md` | Cpt Hedge地図を非公式作戦図として使うための運用手順 |
| `strategy/server_strategy_comparison_2026-05-10.md` | ODS版OCRから作成した最新サーバー別比較 |

## 旧版・補助ファイル

| パス | 扱い |
|---|---|
| `strategy/archive/jdx_executive_brief.md` | 旧版。#509連携を強めに置いた初期案として退避。共有はv2を使う |
| `strategy/server_strategy_comparison_2026-05-03.md` | 旧戦力スナップショット。現行判断は2026-05-10版を使う |
| `templates/screenshot_review_template.md` | 画像確認の記録テンプレート |

## ローカル管理素材

| パス/種類 | 扱い |
|---|---|
| `IMG_*.PNG` | 一次資料。移動せず、必要な事実だけ `research/source_log.md` へ転記 |
| `S6powerrank/IMG_*.PNG` | 戦力ランキング再集計用の画像群。ローカル/Drive管理 |
| `outputs/lastwar_s6_latest_*.csv` | 戦力ランキングCSV。`.gitignore` 対象 |
| `outputs/s6powerrank_*.csv` | `S6powerrank/` 画像から再集計した戦力ランキングCSV。`.gitignore` 対象 |
| `outputs/sheets/*.xlsx` | 戦力ランキングのExcel整理版。`.gitignore` 対象 |
| `outputs/lastwar_s6_latest_summary.md` | 旧戦力サマリー。現行判断は2026-05-10 ODS版へ更新済み |
| `outputs/ocr_all_images_2026-05-03.txt` | OCR作業出力。ローカル参照用 |
| `map_exports/` | Cpt HedgeのJSONエクスポートや作業途中画像。作業用ローカル保存 |
| `build_lastwar_s6_latest_rankings.py` | CSV生成用ローカルスクリプト。GitHub docs-only方針では除外 |
| `tools/vision_ocr.swift` | OCR補助ローカルツール。GitHub docs-only方針では除外 |
| `node_modules/` | スプレッドシート作成時のローカル依存。GitHubには含めない |

## 現時点の注意

- READMEのファイル索引を通常の入口にする。
- `outputs/`、画像、ローカル抽出スクリプトはGitHubへ載せない前提。
- 戦力数値は2026-05-10 ODS版の `outputs/s6powerrank_*_ods_2026-05-10.csv` を優先し、共有用の判断は `strategy/server_strategy_comparison_2026-05-10.md` を見る。
- 地図配置は `strategy/map_planning_notes.md` を正とする。
- 幹部Discord共有は `strategy/jdx_executive_brief_v2.md` を使う。
