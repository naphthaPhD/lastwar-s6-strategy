# Last War Season 6 Strategy Project

ラストウォー Season 6 の戦略立案・情報整理・実行管理用プロジェクトです。

## 目的

- Season 6 の仕様・イベント・報酬・制約を確認する
- 同盟または個人の優先順位を決める
- 資源、英雄、部隊、建築、研究、課金/無課金判断を整理する
- 日次・週次で実行する作戦を明確にする
- スクリーンショットから得た情報を根拠付きで残す

## 使い方

1. `strategy/member_start_checklist.md` で、連盟員へ最初に貼る内容を確認する
2. `strategy/week1_member_playbook.md` で、Week 1全体のメンバー向け方針を確認する
3. `strategy/season6_strategy.md` で、JDX/#534全体の戦略方針を確認する
4. `strategy/hero_power_growth_by_spend.md` で、課金帯別の英雄戦力育成方針を確認する
5. `docs/season6_mechanics.md` で、仕様・仮説・要確認事項を確認する
6. `strategy/action_plan.md` で、今後の実行タスクを管理する

チャットの文脈が長くなった場合は、`docs/context_handoff.md` を新しいスレッドの再開用メモとして使います。

## Discord添付用PDF/PNG

GitHub Actions の `Build Discord Assets` で、リポジトリ内のMarkdownとExcelファイルをDiscord添付用のPDF/PNGに変換できます。

1. GitHubの `Actions` タブを開く
2. `Build Discord Assets` を選ぶ
3. `Run workflow` を押す
4. 完了した実行履歴を開く
5. 実行結果ページの `Artifacts` から `discord-assets` をダウンロードする
6. ダウンロードしたZIPを展開し、必要なPDFまたはPNGをDiscordへ手動で添付する

手元で同じ変換を行う場合は、Pandoc、Google ChromeまたはChromium、Poppler、LibreOfficeを入れた上で次を実行します。

```sh
bash scripts/build_discord_assets.sh
```

生成先は `outputs/discord_assets/` です。Excelは事前に印刷範囲、用紙方向、改ページを整えておくとPDF/PNGが見やすくなります。

GitHub Actionsで作ったPDF/PNGはリポジトリのファイル一覧には追加されません。Actionsの実行結果に保存される一時成果物として扱います。

注意: `outputs/` は `.gitignore` 対象なので、GitHub Actionsで変換したいExcelは `strategy/`、`docs/`、`sheets/` などGit管理対象の場所に置きます。

## ファイル索引

### まず読む

| パス | 用途 |
|---|---|
| `strategy/member_start_checklist.md` | S6開始前・開始直後に連盟員へ貼る短縮チェックリスト |
| `strategy/week1_member_playbook.md` | Week 1全体の連盟員向け行動指示 |
| `strategy/season6_strategy.md` | JDX/#534の戦略本体 |
| `strategy/hero_power_growth_by_spend.md` | 無課金・微課金・廃課金別の英雄戦力育成方針 |
| `strategy/action_plan.md` | 実行タスク、日次/週次チェック |

### 幹部向け

| パス | 用途 |
|---|---|
| `strategy/jdx_executive_brief_v2.md` | 幹部Discord共有用の現行要約 |
| `strategy/server_strategy_comparison_2026-05-10.md` | ODS版OCRに基づく最新サーバー別戦力比較と戦略評価 |
| `strategy/509_week2_proposal_2026-05-12.md` | #509大統領・作戦担当へ送るWeek 2中央入口/#503方面提案文 |
| `strategy/map_planning_notes.md` | Cpt Hedge地図のゾーン対応、初期集合、警戒線 |
| `strategy/base_occupation_plan_2026-05-12.md` | 7日目までの占領予定図を使った拠点取得・担当境界・中央入口・防衛ライン・戦力比較反映の判断メモ |
| `strategy/476_invasion_map_assessment_2026-05-07.md` | #476の中央侵攻/#534妨害ルート評価 |
| `strategy/cpt_hedge_map_workflow.md` | Cpt Hedge地図のグリッド命名、色分け、JSON保存、共有手順 |

### 仕様・根拠確認

| パス | 用途 |
|---|---|
| `docs/season6_mechanics.md` | S6仕様の確認済み/仮説/要確認整理 |
| `research/source_log.md` | 画像、Discord、公式Wiki、外部サイト、ローカル生成データの根拠ログ |
| `docs/previous_thread_summary.md` | 前回チャットと追加走査の要約 |
| `docs/shadow_jungle_info_previous_thread.md` | 前回チャット要約からJDX方針を除いた情報抽出版 |
| `docs/context_handoff.md` | 新しいチャットへ渡す引き継ぎ |

### 管理・補助

| パス | 用途 |
|---|---|
| `docs/00_project_brief.md` | プロジェクトの前提、未確定事項、意思決定基準 |
| `docs/file_inventory_2026-05-03.md` | ファイル棚卸しとGitHubへ載せる/載せない整理 |
| `docs/content_review_2026-05-03.md` | 2026-05-03時点の内容レビュー |
| `templates/screenshot_review_template.md` | 画像確認用テンプレート |

### 旧版

| パス | 扱い |
|---|---|
| `strategy/archive/jdx_executive_brief.md` | 旧版。#509連携を強めに置いた初期案として退避。共有には `strategy/jdx_executive_brief_v2.md` を使う |
| `strategy/server_strategy_comparison_2026-05-03.md` | 旧戦力スナップショット。現行判断は `strategy/server_strategy_comparison_2026-05-10.md` を使う |

## 情報の扱い

ゲーム仕様は更新される可能性があります。未確認情報は「仮説」として扱い、根拠となる画像・日付・確認者を残します。

## 現在の素材

このフォルダ直下に `IMG_*.PNG` のスクリーンショットがあります。画像は移動せず、必要な内容を `research/source_log.md` に転記していきます。

戦力ランキングの生成物は `outputs/` にあります。元画像は `S6powerrank/` にあります。どちらも `.gitignore` 対象なので、GitHubへ共有する場合は必要な結論を `strategy/` または `docs/` のmdへ転記します。現行の戦力比較は `strategy/server_strategy_comparison_2026-05-10.md` を参照します。

## 地図作戦

Cpt HedgeのS6インタラクティブ地図は、公式情報源ではなく作戦図作成用として扱います。

- ゾーン対応、初期集合、#476警戒、#509候補線は `strategy/map_planning_notes.md`
- 7日目までの占領予定図からの拠点取得・担当境界・中央入口・防衛ライン・戦力比較反映は `strategy/base_occupation_plan_2026-05-12.md`
- #476の中央侵攻/#534妨害ルート評価は `strategy/476_invasion_map_assessment_2026-05-07.md`
- グリッド命名、色分け、JSON保存、Discord共有手順は `strategy/cpt_hedge_map_workflow.md`

地図のJSONエクスポートや作業途中画像は `map_exports/` にローカル保存し、GitHubには原則含めません。
