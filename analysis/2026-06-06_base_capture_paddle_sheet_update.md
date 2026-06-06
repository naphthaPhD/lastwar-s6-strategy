# 2026-06-06 Base Capture PaddleOCR Sheet Update

## 1. Executive summary

Dropbox/Drive synced `拠点取得スクショ` の追加画像 121 枚を PaddleOCR で解析し、Google Sheets `管理表たたき` の C:D:E:L を 198 行更新した。

## 2. Context

- 対象日: 2026-06-06
- 対象シート: `12uNW9XphH2zSX4h5BzjSd-OON9r5AckAuNCwQTbY79g` / `管理表たたき`
- 対象画像: `IMG_0552.PNG` から `IMG_0908.PNG` のうち 121 枚
- 入力フォルダ: Google Drive sync temp `拠点取得スクショ`
- OCR: Apple Vision がこの画像群で失敗したため、PaddleOCR のキャッシュ済みモデルで処理

## 3. Key facts

- 処理画像数: 121
- 抽出イベント数: 384
- latest target 候補: 350
- シート更新: 198 行
- レビュー送り: 152 件
- 更新列: C `拠点種別`, D `連盟`, E `取得時間`, L `メモ`
- 代表行の読み戻し確認:
  - `C1953:E1953` = `漁場 / MOn / 2026/05/24 9:36`
  - `L1953` = `IMG_0879.PNG` 由来メモ
  - `C1947:E1947` = `漁場 / PmP / 2026/05/24 12:15`
  - `L1947` = `IMG_0908.PNG` 由来メモ

## 4. Timeline

- 2026-05-22 14:10 から 2026-05-24 12:15 までの占領/奪取ログを抽出。
- 画像内に時刻が見えない行は、直前の古い画像で見えていた時刻を補完として使用した。

## 5. Interpretation

今回の追加分は、既存の Apple Vision OCR では読めなかった画像群の補完更新である。中央 `#8061` の高レベル漁場と、#440/#476/#480/#503/#509/#511/#523/#534 の漁場・交易地・都市更新が混在している。

## 6. Risks

- レビュー送り 152 件は未反映。内訳は `existing_newer` 130、`type_mismatch` 11、`row_not_found` 10、`low_confidence_owner_no_letter` 1。
- `previous_image_visible_time` で補完した行は、画像に時刻が直接写っている行より信頼度を一段下げて扱う。
- Google Sheets の読み戻し確認で `C718:E718` は API timeout したが、同じ行の `L718` は反映済みとして返った。

## 7. Recommended actions

1. `data/2026-06-06_base_capture_paddle_review.csv` の `row_not_found` と `type_mismatch` を確認する。
2. 取得時間補完行を必要に応じて手動スポットチェックする。
3. `管理表たたき` を正として、必要なら S6#534 の全体マップ更新スクリプトを再実行する。

## 8. Unknowns

- Google Drive temp 経由で見えている 121 枚が、Dropbox 側の最新投入分すべてかはローカル sync 状態に依存する。
- `全体マップ` 側の反映は、管理表更新後に別途 Apps Script refresh が必要。

## 9. Files referenced

- `data/2026-06-06_base_capture_paddle_events.csv`
- `data/2026-06-06_base_capture_paddle_sheet_updates.csv`
- `data/2026-06-06_base_capture_paddle_review.csv`
- `data/2026-06-06_base_capture_paddle_ranges.json`
- `inputs/ocr_alliance_corrections.json`
- `tools/base_capture_paddle_update.py`
