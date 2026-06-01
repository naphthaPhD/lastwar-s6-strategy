# Last War S6 漁場保護管理システム

## 1. Executive summary

漁場ごとの保護切れ時刻、応戦枠、ワンパン候補、放棄後タイマーを管理する Google Sheets + Apps Script パッケージを追加した。主目的は「次にどの漁場がいつ開くか」を一覧化し、ヘカテ個人の記憶に依存しない防御壁運用へ寄せること。

## 2. Context

入力仕様は、交戦日を水曜・土曜、応戦枠を `15:00-16:00`, `23:00-24:00`, `07:00-08:00`、15時枠を安全期間として扱う前提。A列は `木曜7時 -> 土曜23時`、B列は `水曜23時 -> 日曜7時` の保護ローテーションを基本にする。

## 3. Key facts

- Apps Script 本体を `tools/fishery_protection_sheet/Code.gs` に保存した。
- 導入手順と運用方針を `tools/fishery_protection_sheet/README.md` に保存した。
- ゲームルールの整理を `rules/fishery_protection_timer_rules.md` に保存した。
- `漁場一覧`, `イベント一覧`, `シミュレーター`, `カレンダー` の4シートを作成・更新する設計。
- `NEXT_PROTECTION_END`, `ABANDON_PROTECTION_END`, `CAN_ABANDON` のカスタム関数も用意した。
- `ワンパン必要` は手動判断を上書きしない。空欄または `自動:` で始まる値だけ自動更新する。

## 4. Timeline

| 日時 | 内容 |
|---|---|
| 2026-06-01 | 漁場保護管理システムの仕様整理、Apps Script、テンプレート、引き継ぎを追加 |

## 5. Interpretation

このシステムは、ワンパンの実行判断を自動化するものではない。23時開放は `自動:候補`、7時開放は `自動:7時要判断` として、実行者が状況判断できる表示に留める。7時側を危険として放置するヘカテ方式にも対応する。

## 6. Risks

1. 放棄後保護の実ゲーム挙動は、実画面で追加確認が必要。
2. Apps Script のタイムゾーンが `Asia/Tokyo` でないと、日時表示がずれる可能性がある。
3. 実ゲーム画面の保護終了表示と表計算が食い違う場合は、画面表示を優先する必要がある。

## 7. Recommended actions

1. 新規またはレビュー用 Google Sheet に `Code.gs` を貼り付け、`setupFisheryProtectionWorkbook()` を実行する。
2. `漁場一覧` に現在の全対象漁場を入力する。
3. 実画面の保護終了表示と計算結果を数件突き合わせる。
4. 放棄を1件テストできるタイミングで、放棄後保護終了が Apps Script の仮定と一致するか確認する。

## 8. Unknowns

- 放棄後保護が「次の応戦枠基準」で確定か。
- 7時枠をどの条件で保護パン対象に戻すか。
- 実運用シートを新規作成するか、既存レビューシートに追加するか。

## 9. Files referenced

- `tools/fishery_protection_sheet/Code.gs`
- `tools/fishery_protection_sheet/README.md`
- `rules/fishery_protection_timer_rules.md`
- `data/fishery_protection_sheet_template.csv`
