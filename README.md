# Last War Season 6 Strategy Project

ラストウォー Season 6 の戦略立案・情報整理・実行管理用プロジェクトです。

## 目的

- Season 6 の仕様・イベント・報酬・制約を確認する
- 同盟または個人の優先順位を決める
- 資源、英雄、部隊、建築、研究、課金/無課金判断を整理する
- 日次・週次で実行する作戦を明確にする
- スクリーンショットから得た情報を根拠付きで残す

## 使い方

1. `docs/00_project_brief.md` に前提条件を書く
2. `research/source_log.md` にスクリーンショットや外部情報の確認結果を記録する
3. `docs/season6_mechanics.md` に Season 6 の仕様を整理する
4. `strategy/season6_strategy.md` に方針をまとめる
5. `strategy/action_plan.md` で実行タスクを管理する

チャットの文脈が長くなった場合は、`docs/context_handoff.md` を新しいスレッドの再開用メモとして使います。

## 情報の扱い

ゲーム仕様は更新される可能性があります。未確認情報は「仮説」として扱い、根拠となる画像・日付・確認者を残します。

## 現在の素材

このフォルダ直下に `IMG_*.PNG` のスクリーンショットがあります。画像は移動せず、必要な内容を `research/source_log.md` に転記していきます。

戦力ランキングの生成物は `outputs/` にあります。元画像は `S6powerrank/` にあります。どちらも `.gitignore` 対象なので、GitHubへ共有する場合は必要な結論を `strategy/` または `docs/` のmdへ転記します。

## 地図作戦

Cpt HedgeのS6インタラクティブ地図は、公式情報源ではなく作戦図作成用として扱います。

- ゾーン対応、初期集合、#476警戒、#509候補線は `strategy/map_planning_notes.md`
- グリッド命名、色分け、JSON保存、Discord共有手順は `strategy/cpt_hedge_map_workflow.md`

地図のJSONエクスポートや作業途中画像は `map_exports/` にローカル保存し、GitHubには原則含めません。
