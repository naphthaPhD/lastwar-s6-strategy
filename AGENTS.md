# AGENTS.md

## 目的

このリポジトリは、ゲーム内シーズン戦略、チャットログ整理、OCR結果、時系列ログ、連盟分析、ルール整理、作戦判断材料を管理するためのものである。

基本ワークフローは以下とする。

1. Windows PC上のCodexで画像処理、OCR、ログ整理、分析、Markdown/JSON/CSV/TSV生成を行う。
2. 成果物をこのリポジトリに保存する。
3. 作業区切りごとにGitHubへcommit/pushする。
4. ChatGPTがGitHub上の成果物を確認し、戦況解釈、要約、作戦方針、共有文案、次のCodex指示を作成する。

このリポジトリは、CodexとChatGPTの間の引き継ぎ台帳として使う。

## 既存の正本

以下の既存ファイルは、このプロジェクトの正本として扱う。

- `docs/season6_mechanics.md`: Season 6 の仕様、確認済み事実、仮説、要確認事項。
- `strategy/season6_strategy.md`: #534/JDX の戦略本体。
- `strategy/action_plan.md`: 実行タスク、日次/週次チェック、未確認事項。
- `research/source_log.md`: スクリーンショット、Discord、公式情報、外部情報、ローカル生成データの根拠ログ。
- `analysis/latest_handoff.md`: ChatGPTが最初に読む最新引き継ぎ。

## 基本方針

- ChatGPTと人間が読みやすい形式で保存する。
- 主要形式は Markdown, JSON, CSV, TSV とする。
- PDFや画像だけに依存しない。
- 一時ファイルや不要な中間生成物はcommitしない。
- 作業結果は、後から差分確認できる単位でcommitする。
- `git add .` は原則禁止。必ず対象ファイルを確認してから個別にaddする。
- 大量スクリーンショットやcrop画像は原則commitしない。
- 重要な根拠画像のみ `screenshots/selected/` に保存する。
- 作業区切りごとに `analysis/latest_handoff.md` を更新する。
- 判断に迷うファイルはcommitしない。

## 推奨ファイル形式

- `.md`: 人間向けの分析、作戦方針、ルール整理、ブリーフィング、引き継ぎ文書。
- `.json`: OCR結果、チャットログ、イベントログ、時系列データ、構造化情報。
- `.csv` / `.tsv`: ランキング、座標、連盟情報、集計表、比較表。
- `.py`: OCR前処理、JSON整形、CSV生成、レポート生成などの処理スクリプト。
- `.txt`: 一時的なメモやプロンプト下書き。ただし最終成果物は原則 `.md` に整理する。
- `.pdf`: 最終確認用・参照用。分析の主形式にはしない。

## ディレクトリ構成

以下の構成を基本とする。存在しない場合は作成する。

```text
.
├─ README.md
├─ AGENTS.md
├─ analysis/
│  ├─ latest_handoff.md
│  └─ YYYY-MM-DD_topic_analysis.md
├─ logs/
│  ├─ timeline/
│  ├─ chat/
│  └─ decisions/
├─ rules/
├─ data/
├─ prompts/
├─ tools/
└─ screenshots/
   └─ selected/
```

### `analysis/`

戦況分析、連盟比較、作戦案、リスク評価、次回行動方針を保存する。

例:

```text
analysis/2026-05-26_534_altar_preparation.md
analysis/2026-05-26_476_pressure_analysis.md
analysis/2026-05-26_534_next_actions.md
analysis/latest_handoff.md
```

### `logs/timeline/`

時系列ログを保存する。

例:

```text
logs/timeline/2026-05-26_timeline.md
```

### `logs/chat/`

チャットログ、OCR後の発言記録、構造化した会話データを保存する。

例:

```text
logs/chat/2026-05-26_chat_events.json
```

### `logs/decisions/`

撤退基準、外交判断、連盟内方針、作戦決定ログを保存する。

例:

```text
logs/decisions/2026-05-26_retreat_criteria.md
```

### `rules/`

祭壇、都市、漁場、拠点、極秘任務などのルール整理を保存する。既に正本へ統合できる内容は、最終的に `docs/season6_mechanics.md` へ反映する。

例:

```text
rules/altar_rules.md
rules/city_rules.md
rules/fishery_rules.md
```

### `data/`

CSV、TSV、JSONなどの分析用データを保存する。

例:

```text
data/2026-05-26_events.json
data/2026-05-26_alliance_rankings.csv
data/2026-05-26_base_positions.tsv
```

### `prompts/`

Codex、OCR、ChatGPT分析用プロンプトを保存する。

例:

```text
prompts/codex_ocr_prompt.md
prompts/strategy_analysis_prompt.md
prompts/briefing_prompt.md
```

### `tools/`

Pythonなどの処理スクリプトを保存する。現行の `.gitignore` では広範なローカル補助スクリプトを除外しているため、commitする場合は必要なスクリプトを明示的に選び、必要なら `.gitignore` のallowlistも同時に更新する。

例:

```text
tools/normalize_events.py
tools/ocr_result_to_json.py
tools/make_timeline.py
```

### `screenshots/selected/`

分析上必要な証拠画像のみ保存する。大量のraw画像やcrop画像は保存しない。

## 分析ファイルの標準構成

分析Markdownを作成する場合、原則として以下の構成にする。

```md
# タイトル

## 1. Executive summary

結論を短く書く。

## 2. Context

前提、対象日時、対象サーバ、対象連盟、参照データを整理する。

## 3. Key facts

確認できた事実を箇条書きで整理する。

## 4. Timeline

重要イベントを時系列で整理する。

## 5. Interpretation

#534視点での意味、相手の意図、現在のリスクを解釈する。

## 6. Risks

今後起こり得るリスクを整理する。

## 7. Recommended actions

推奨行動を優先順位付きで示す。

## 8. Unknowns

未確認事項、追加確認が必要な点を書く。

## 9. Files referenced

参照したファイルを列挙する。
```

## ChatGPT引き継ぎファイル

作業の区切りごとに、必ず以下を更新する。

```text
analysis/latest_handoff.md
```

`latest_handoff.md` の標準形式は以下。

```md
# Handoff summary

## Date

YYYY-MM-DD

## Context

今回の分析対象、前提、参照したログや画像の概要。

## Updated files

- analysis/...
- data/...
- logs/timeline/...
- rules/...

## Key findings

1. ...
2. ...
3. ...

## Current risks

1. ...
2. ...
3. ...

## Recommended next actions

1. ...
2. ...
3. ...

## Questions for ChatGPT

1. この判断でよいか。
2. 幹部向け共有文にするならどう書くか。
3. 次の作戦判断に必要な追加データは何か。

## Notes

補足事項、未確認事項、注意点。
```

ChatGPT側では、この `latest_handoff.md` を最初に確認する。

## Git commit / push 運用

作業が一区切りついたら、GitHubへ反映する。

一区切りとは以下を指す。

- 分析レポートを作成または更新した。
- 時系列ログを更新した。
- OCR結果をJSON化した。
- CSV/TSVを作成・更新した。
- ルール整理を更新した。
- 作戦判断メモを作成した。
- ChatGPT引き継ぎファイルを更新した。
- 処理スクリプトを作成・更新した。

## push前の確認手順

必ず以下を実行する。

```bash
git status
git branch --show-current
git diff --stat
git diff --name-only
```

そのうえで、commit対象を選別する。

原則として `git add .` は使わない。

```bash
git add analysis/latest_handoff.md
git add analysis/YYYY-MM-DD_topic_analysis.md
git add data/YYYY-MM-DD_events.json
git add logs/timeline/YYYY-MM-DD_timeline.md
```

commit前に必ず確認する。

```bash
git status
git diff --cached --stat
git diff --cached --check
```

問題なければcommitする。

```bash
git commit -m "Update strategy analysis and handoff"
git push
```

## commit message 方針

commit message は内容が分かるように簡潔に書く。

例:

```text
Update altar preparation analysis
Add 534 timeline for 2026-05-26
Update alliance ranking data
Add OCR event normalization script
Update latest handoff for ChatGPT review
```

日本語でもよい。

```text
祭壇準備分析を更新
534視点の時系列ログを追加
連盟ランキングデータを更新
ChatGPT引き継ぎメモを更新
```

## push後の報告形式

push後、Codexは必ず以下の形式で報告する。

```md
## Push completed

- Branch:
- Commit:
- Commit message:
- Main files:
- Summary:
- Notes:
```

## commitしてよいもの

原則として以下はcommit対象としてよい。

```text
README.md
AGENTS.md
analysis/*.md
logs/timeline/*.md
logs/chat/*.json
logs/decisions/*.md
rules/*.md
data/*.json
data/*.csv
data/*.tsv
prompts/*.md
tools/*.py
screenshots/selected/*
```

ただし、`tools/` は現行 `.gitignore` で広く除外している。commitする場合は、用途が説明できるものだけを個別に選び、allowlist化する。

## commitしないもの

以下は原則としてcommitしない。

```text
.venv/
venv/
node_modules/
__pycache__/
*.pyc
.DS_Store
Thumbs.db
*.log
tmp/
temp/
cache/
debug/
output_tmp/
intermediate/
cropped/
crop/
ocr_tmp/
ocr_debug/
failed_ocr/
raw_ocr/
screenshots/raw/
screenshots/cropped/
screenshots/tmp/
```

大量画像、crop画像、OCR途中ファイル、重複画像はcommitしない。必要な証拠画像だけ `screenshots/selected/` に移してcommitする。

## `.gitignore` 標準設定

`.gitignore` に以下が含まれているか確認する。なければ追加する。

```gitignore
# OS
.DS_Store
Thumbs.db

# Python
__pycache__/
*.pyc
.venv/
venv/

# Node
node_modules/

# Logs and temporary files
*.log
tmp/
temp/
cache/
debug/
output_tmp/
intermediate/

# OCR temporary outputs
cropped/
crop/
ocr_tmp/
ocr_debug/
failed_ocr/
raw_ocr/

# Bulk screenshots
screenshots/raw/
screenshots/cropped/
screenshots/tmp/

# Allow selected screenshots
!screenshots/
!screenshots/selected/
!screenshots/selected/**

# Local environment
.env
.env.local
```

## Codex作業開始時の標準手順

Codexは作業開始時に以下を確認する。

```bash
git status
git branch --show-current
```

必要なら以下も確認する。

```bash
git pull
```

ただし、未commit変更がある場合は、勝手にpullして競合させない。まず現在の変更を確認し、必要ならユーザーに報告する。

## Codex作業終了時の標準手順

Codexは作業終了時に以下を実行する。

1. 成果物をMarkdown/JSON/CSV/TSVとして保存する。
2. `analysis/latest_handoff.md` を更新する。
3. `git status` を確認する。
4. `git diff --stat` と `git diff --name-only` を確認する。
5. commit対象を選別する。
6. 必要ファイルだけ `git add` する。
7. `git diff --cached --stat` と `git diff --cached --check` を確認する。
8. commitする。
9. pushする。
10. push完了報告を出す。

## ChatGPTに確認してもらう前提の出力

ChatGPTに確認してもらう分析結果は、必ず以下のいずれかで保存する。

```text
analysis/latest_handoff.md
analysis/YYYY-MM-DD_topic_analysis.md
data/YYYY-MM-DD_topic_events.json
logs/timeline/YYYY-MM-DD_timeline.md
```

ChatGPTに渡すべき情報は、`latest_handoff.md` に集約する。

## 重要な注意

- GitHubは作業成果物の共有場所であり、未整理ファイルの物置ではない。
- Codexは作業のたびに、何を保存し、何を保存しないか判断する。
- 判断に迷うファイルはcommitしない。
- 大量ファイルを追加する前に必ず確認する。
- 分析の根拠が画像だけの場合は、可能な限りOCR結果や要約をMarkdown/JSONとして残す。
- ChatGPTが読む前提で、ファイル名と見出しを明確にする。
