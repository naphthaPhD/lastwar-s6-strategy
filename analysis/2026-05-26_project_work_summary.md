# S6 Project Work Summary

## 1. Executive Summary

このリポジトリでは、Last War Season 6 の仕様確認、#534/JDX の作戦設計、戦力ランキング整理、Google Sheets 連携、スクリーンショット処理、GitHub/ChatGPT 引き継ぎ運用を進めてきた。

現時点の中心方針は、#534/JDX 単独で #476 を正面から押し返すより、南側は遅滞・防衛、中央入口は #509/#440 連携、重要ルールは `docs/season6_mechanics.md` に集約し、作戦判断は `strategy/` と `analysis/` に残すことである。

## 2. Repository Operation

- `AGENTS.md` を追加し、Codex と ChatGPT の引き継ぎ台帳としての運用ルールを明文化した。
- `analysis/latest_handoff.md` を ChatGPT が最初に読む入口として整備した。
- `analysis/`, `logs/timeline/`, `logs/chat/`, `logs/decisions/`, `rules/`, `data/`, `prompts/`, `screenshots/selected/` を追加した。
- `.gitignore` を更新し、大量画像、OCR中間物、cache、env、ローカル生成物、広範な `tools/` 配下を原則除外する方針にした。
- GitHub へ載せるものは Markdown/JSON/CSV/TSV 中心とし、未整理のスクリーンショットや生成物はローカル/Drive 管理に寄せた。

## 3. Mechanics And Rule Research

- Season 6 の主要仕様を `docs/season6_mechanics.md` に集約してきた。
- 公式英語Discord `#season-6` と日本語Discord `#シーズン6-シャドウジャングル` のHTMLログ差分を調査し、`docs/english_discord_season6_delta_2026-05-13.md` と `docs/japanese_discord_season6_delta_2026-05-13.md` に整理した。
- 都市、Stronghold、Fishing Ground、祭壇、交易地、盟約、前哨基地、保護期間、安全時間、バリア解除条件などの実務ルールを確認・仮説化した。
- 2026-05-20 メンテ終了メールの内容を反映し、漁場初期上限6、陣営激突報酬上方修正、R3権限変更、賞金首/軍事演習関連の変更を整理した。
- 追加ルールとして faction clash と altar conquest 関連の情報を `docs/season6_mechanics.md` に統合した。

## 4. Strategy And Planning

- `docs/00_project_brief.md` に、#534/JDX の前提、陣営配置、意思決定基準、未確定事項を整理した。
- `strategy/season6_strategy.md` を JDX/#534 の戦略本体として更新してきた。
- `strategy/action_plan.md` に、日次/週次タスク、未確認事項、戦闘前に確認すべき項目を集約した。
- `strategy/member_start_checklist.md` と `strategy/week1_member_playbook.md` に、連盟員向けの行動指示を作成した。
- `strategy/hero_power_growth_by_spend.md` に、課金帯別の英雄戦力育成方針を整理した。
- `strategy/jdx_executive_brief_v2.md` を、幹部Discord共有用の現行要約として整備した。

## 5. Map And Alliance Operations

- Cpt Hedge 地図は公式情報源ではなく、作戦図作成用として扱う方針にした。
- `strategy/map_planning_notes.md` に、ゾーン対応、初期集合、#476警戒、#509候補線を整理した。
- `strategy/base_occupation_plan_2026-05-12.md` に、7日目までの占領予定、担当境界、中央入口、防衛ラインの見立てを整理した。
- `strategy/476_invasion_map_assessment_2026-05-07.md` で、#476の中央侵攻/#534妨害ルートを評価した。
- `strategy/534_defense_line_abc_2026-05-14.md` で、#476侵攻に備える #534 A/B/C 防衛ラインと接触漁場案を整理した。
- `strategy/534_ooda_sunzi_frame.md` で、OODAループと孫子を #534 の遅滞・中央妨害・限定反撃へ落とし込んだ。
- 2026-05-25 時点の live Google Sheet 地図分析では、ローカルブックではなく live sheet を正とし、#476 を主圧力、#534 は防衛・遅滞と中央入口警戒を優先する読みを出した。

## 6. Diplomacy And Coordination

- `strategy/509_week2_proposal_2026-05-12.md` に、#509大統領/作戦担当へ送る Week 2 中央入口・#503方面提案を作成した。
- `strategy/509_534_voice_meeting_2026-05-17.md` に、#509/#534 音声会議の要約を作成した。
- `strategy/jdx_todo_2026-05-18.md` に、中央 #8061 囲い込み、#503 進路妨害、安全時間変更後の調整、476外交の扱いを即応タスクとして整理した。
- KTVS/VEX/4th の暫定盟約・切替予定を、戦略本体、防衛線、#509提案、action plan に反映した。

## 7. Power Ranking And OCR Work

- 2026-05-03 版と 2026-05-10 版の戦力ランキングを比較し、現行判断は `strategy/server_strategy_comparison_2026-05-10.md` に寄せた。
- #476 は Top9/Top6/Top3 の圧力が最大で、#509 は味方側の実働主力候補、#534 は単独正面戦より遅滞・連携・中央入口確保が重要という読みを整理した。
- ローカルOCRは混在文字、装飾フォント、UI桁の影響で誤認識が多いため、スクリーンショットランキングは ChatGPT で一次OCRし、Codex は検証・正規化・Google Sheets 反映を担う分業に切り替えた。
- `tools/openai_vision_ocr.py` など、より高精度なOCR/vision処理の検討も行ったが、実運用では ChatGPT Excel を working truth とする場面があった。

## 8. Google Sheets And Automation

- S6 の Google Sheets 作業では、Drive検索ではなく明示された `spreadsheet_id` に直接ルーティングする運用を採用した。
- JDX questionnaire handover では、現行名簿、未回答、移籍/一軍関連タブを対象に、重複整理やタブ更新の順序を確認した。
- S6 ranking sheet では、ChatGPT生成Excelとローカル検証結果を突き合わせ、対象タブへ反映した。
- Google Sheets の重さについて、`onSelectionChange` による自動詳細更新が主な遅延要因と判断し、保存されていたソースタブ上で自動更新を抑えるパッチ案を作った。ただし live `Code.gs` へ直接反映したとは扱わない。
- 2026-05-25 の JDX戦力スクショ更新では、Drive同期フォルダの `IMG_1055.PNG` から `IMG_1084.PNG` までを処理し、JDX戦力などシートの現在週 D:G を中心に、明確に名簿照合できた値だけを更新した。Google Sheets API 上では 18 行・69 セル更新、戦力分析再計算も確認した。

## 9. Environment And Tooling

- Windows 環境向けの引き継ぎとして `docs/windows_environment_handoff_2026-05-24.md` を追加した。
- `.venv`, `.tessdata`, `node_modules`, `outputs/`, `S6powerrank/`, `map_exports/` などを原則ローカル管理にした。
- Discord添付用のPDF/PNG生成は GitHub Actions の `Build Discord Assets` を使う方針にした。

## 10. Current Open Items

- #440 全体方針、#509 正式連携、#534内の役割分担は未確定のまま。
- 防衛ライン、中央入口、JDX担当範囲は、実際の所有者・保護明け・取得/宣戦ボタン・安全時間の実画面確認が必要。
- 祭壇の当日占領数制限、Lv違い同日取得、20人超/1,000M条件、排他関係は初回実画面で再確認する。
- 盟約領土を使った敵都市破壊、中央FG斜め隣接、保護明け表示バグ疑い、Stronghold所有者切替時のバリアリスクは要検証。
- JDX戦力スクショ更新は、今後も ChatGPT/vision OCR と Codex の Sheets 反映を分けて運用する。

## 11. Files To Read First

1. `analysis/latest_handoff.md`
2. `docs/00_project_brief.md`
3. `strategy/action_plan.md`
4. `docs/season6_mechanics.md`
5. `strategy/season6_strategy.md`
6. `strategy/server_strategy_comparison_2026-05-10.md`
7. `strategy/jdx_executive_brief_v2.md`
8. `research/source_log.md`
