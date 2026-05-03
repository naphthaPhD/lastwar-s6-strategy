# Context Handoff

このファイルは、チャットの文脈が長くなりすぎた場合に新しいスレッドで作業を再開するための引き継ぎメモです。

## 再開時に最初に伝えること

新しいチャットでは、以下を貼るか、このファイルを読むよう依頼する。

```text
/Users/mba2025/Documents/S6 は、ラストウォー Season 6 の戦略立案プロジェクトです。
まず README.md と docs/context_handoff.md を読み、現在の構成を把握してください。
スクリーンショット IMG_*.PNG は一次資料なので移動せず、確認結果を research/source_log.md に記録してください。
Season 6 の仕様は docs/season6_mechanics.md、方針は strategy/season6_strategy.md、実行タスクは strategy/action_plan.md に整理してください。
```

## 現在のプロジェクト構成

| パス | 役割 |
|---|---|
| `README.md` | プロジェクトの入口 |
| `docs/00_project_brief.md` | 目的、前提、意思決定基準 |
| `docs/season6_mechanics.md` | Season 6 の仕様整理 |
| `docs/file_inventory_2026-05-03.md` | フォルダ内ファイルの棚卸しとGitHubへ載せる/載せない整理 |
| `docs/previous_thread_summary.md` | 前回チャット「シャドウジャングル情報を収集」の復元メモ |
| `docs/content_review_2026-05-03.md` | 2026-05-03時点の内容確認メモ |
| `research/source_log.md` | スクリーンショットや外部情報の根拠ログ |
| `strategy/season6_strategy.md` | 戦略方針 |
| `strategy/action_plan.md` | タスク、日次チェック、週次チェック |
| `strategy/server_strategy_comparison_2026-05-03.md` | 戦力CSVから作成したサーバー別戦略比較 |
| `strategy/jdx_executive_brief.md` | 幹部Discord共有用の要約 |
| `strategy/jdx_executive_brief_v2.md` | 公式Wiki貼り付け情報反映後の幹部Discord共有用要約 |
| `strategy/week1_member_playbook.md` | S6開始後1週目の連盟メンバー向け行動指示 |
| `strategy/map_planning_notes.md` | Cpt Hedge S6地図を使ったゾーン対応、初期集合、ルート計画メモ |
| `outputs/lastwar_s6_latest_*.csv` | 戦力ランキングCSV。`.gitignore` 対象でGitHubには通常含めない |
| `outputs/lastwar_s6_latest_summary.md` | 最新戦力サマリー。`.gitignore` 対象 |
| `templates/screenshot_review_template.md` | 画像確認用テンプレート |

## 作業方針

- 会話だけに重要情報を残さない
- 判断の根拠は、画像ファイル名・確認日・状態と一緒に記録する
- 未確認情報は「仮説」または「要確認」として扱う
- ゲーム仕様は変わる可能性があるため、最新性が必要な情報は確認日を残す
- 長くなった議論は、結論だけを該当ファイルへ反映する

## 2026-05-03 追加コンテキスト

このスレッドでは、Chromeで開かれていたDiscord画面と `https://lastwarblog.com/season6/` を参照して、Season 6情報を追加整理した。

- Discord #534側 `#s6` と公式Discord `#🐊シーズン6-シャドウジャングル` を画面走査済み。
- 公式Discord側は、2026-03-26頃から2026-05-03午前までの投稿を中心に確認。
- 画像添付のみの詳細は全文取得できていないため、職業スキル、前哨基地詳細、軍功画像表は必要に応じて再確認する。
- 重要な追加確認: 敵陣営都市は破壊扱い、破壊済み都市は修復不可・中立化・隣接喪失、都市破壊には自戦域または盟約連盟の隣接が必要。
- 重要な追加確認: 中央エリア漁場は拠点ボス討伐に集結が必要なため、1週目は占領不可、2週目以降が実質開始という公式Discord補足あり。
- 重要な追加確認: 陣営科学の盟約解放は先行3-68では1週目終盤。寄付量が多ければ前倒し可能性あり。

### 2026-05-03 公式Wiki貼り付け追加

ユーザーが公式Wiki本文と画像を順次貼り付けたため、以下は公式Wiki由来の一次情報として扱う。

- `show/245`: S6基本概要。8戦域が4対4の2陣営に分かれ、敵領地占領・都市破壊・祭壇・陣営科学・背水の陣・同陣営連携・英雄覚醒が中核。
- `show/267`: 陣営と盟約。第1週は自戦域内移設のみ、第2週以降は高級移設や連盟遠征集結地点で他戦域移設が可能。同陣営1連盟のみ盟約可能。
- 勲功・釣り・陣営テクノロジー: 勲功は累計値で消費しても総勲功は減らない。魚は陣営科学と連盟スキルの燃料。陣営科学はシーズン限定で陣営全体に効果。
- イベントスケジュール画像: WK1-2は殲滅・漁場・都市争奪、WK3以降は祭壇、WK5-7は聖所攻防、WK8は集計。
- 都市破壊: 水曜・土曜の宣戦日中心。敵陣営都市は自動で破壊指令となり、破壊後は修復不可・連地効果なし。破壊時は都市勢力値の50%を獲得。
- 英雄覚醒: S6ではキンバリー、DVA、テスラが順次対象。条件は星5、専用武装Lv20、S6到達。覚醒は最大5星。
- 祭壇: 毎週火曜サーバー時間12:00から1時間。隣接不要。1連盟3祭壇まで。排他祭壇あり。占領後R4以上が大河氏族の贈り物を1回召喚可能。
- 釣りの日: 通常餌は来訪者・勲功商店、ゴールド餌は職業スキル。タイミングは魚種やエネルギーではなく重さに影響。
- Day 1攻略画像: 初日はウイルス耐性、胞子工場、真菌研究所、漁場2つ、釣り開始、魚寄付を優先。
- 前哨基地: 大統領のみ配置可能。配置後移動不可。建設後は本戦域全連盟に領土リンク効果。破壊されると再配置不可。

### 2026-05-03 Cpt Hedge S6地図確認

`https://cpt-hedge.com/maps/season-6/interactive` を確認し、S6地図を作戦検討に使えることを確認。

- 地図は3000x3000座標で、外周A-Hと中央Iに分かれる。
- ユーザー添付のゲーム内シーズンマップ画像で、#534=A、#509=H、#503=G、#476=B、中央#8061=I、#480=F、#523=C、#511=D、#440=Eとして扱えることを確認。
- 密林陣営は#440/#509/#511/#534、湿地陣営は#476/#480/#503/#523。
- #440は右下E。全体方針待ちだが、#534からは遠いため初期防衛を#440頼みにしすぎない。
- Cpt Hedge側はグリッド作成、連盟色分け、進軍ルート番号、JSONエクスポート/インポートに対応。
- 詳細は `strategy/map_planning_notes.md`。

### 2026-05-03 戦力データ

ローカルの `outputs/` に戦力CSVと要約がある。`outputs/` は `.gitignore` 対象なので、GitHubへ共有する場合は必要な結論をmdへ転記する。

- `outputs/lastwar_s6_latest_summary.md`
- `outputs/lastwar_s6_latest_server_power_summary.csv`
- `outputs/lastwar_s6_latest_alliance_rankings_by_server.csv`
- `outputs/lastwar_s6_latest_commander_highlights_by_server.csv`
- `outputs/lastwar_s6_latest_rankings_combined.csv`

戦力分析のmdは `strategy/server_strategy_comparison_2026-05-03.md`。

## 次の具体作業

1. `IMG_*.PNG` を順に確認する
2. イベント名、期限、報酬、必要条件、交換アイテムを `research/source_log.md` に記録する
3. Season 6 固有のルールを `docs/season6_mechanics.md` に転記する
4. 戦略判断が必要な項目を `strategy/season6_strategy.md` にまとめる
5. 実行すべき作業を `strategy/action_plan.md` に落とす

## コンテキスト上限対策

- 画像を大量に一度に解析しない。10枚程度ずつ処理する
- 解析が終わった区切りで、必ず Markdown に要点を保存する
- 新しいスレッドでは、このファイルと README を読めば再開できる状態を保つ
