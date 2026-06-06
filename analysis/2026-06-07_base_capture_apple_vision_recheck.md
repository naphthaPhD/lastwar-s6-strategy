# 2026-06-07 Base Capture Apple Vision Recheck

## 1. Executive summary

先ほどの `拠点取得スクショ` 121 枚を Apple Vision で再解析し、PaddleOCR反映後の `管理表たたき` に対して追加/修正候補 95 行を反映した。

## 2. Context

- 対象画像: Google Drive sync temp `拠点取得スクショ` の 121 枚
- 対象シート: `12uNW9XphH2zSX4h5BzjSd-OON9r5AckAuNCwQTbY79g` / `管理表たたき`
- OCR engine: Apple Vision
- 実行条件: Codex sandbox内では Apple Vision が `Foundation._GenericObjCError 0` で失敗するため、外側権限で実行した。

## 3. Key facts

- 処理画像数: 121
- OCRイベント数: 364
- latest target 候補: 331
- PaddleOCR反映済みシートに対する追加/修正: 95 行
- レビュー送り: 180 件
- 変更なし: 56 件
- シート更新列: C:D:E:L
- Google Sheets writeback: 95 rows / 380 cells

## 4. Timeline

- 2026-05-22 18:18 から 2026-05-24 12:52 までの追加/修正候補を反映。
- 画像内に時刻がないイベントは、直前の古い画像で見えていた時刻を補完として使用した。

## 5. Interpretation

Apple VisionはPaddleOCRより総イベント数は少ないが、PaddleOCRで落ちた後続イベントや一部の座標更新を拾えていた。今回の再解析で、Paddle反映後に残っていた古い所有者/時刻を 95 行修正した。

## 6. Risks

- レビュー送り 180 件は未反映。内訳は `existing_newer` 119、`type_mismatch` 51、`row_not_found` 10。
- `previous_image_visible_time` 補完の更新が 45 件あるため、直接表示時刻より信頼度は一段低い。
- Apple Visionの補正辞書に `GODs -> GoDs`、`w6F -> W6f` を追加した。

## 7. Recommended actions

1. `data/2026-06-07_base_capture_apple_vision_review.csv` の `type_mismatch` と `row_not_found` を確認する。
2. `全体マップ` 側に反映する場合は、S6#534 Apps Script の `全体マップ更新` を実行する。
3. 今後の同種作業では Apple Vision を外側権限で優先実行し、失敗時のみPaddleOCRへfallbackする。

## 8. Unknowns

- Dropbox本体フォルダは `.DS_Store` のみで、画像実体はGoogle Drive temp側にあった。同期元の状態確認は未実施。
- `type_mismatch` 51 件は手動確認待ち。

## 9. Files referenced

- `data/2026-06-07_base_capture_apple_vision_events.csv`
- `data/2026-06-07_base_capture_apple_vision_sheet_updates.csv`
- `data/2026-06-07_base_capture_apple_vision_review.csv`
- `data/2026-06-07_base_capture_apple_vision_noop.csv`
- `data/2026-06-07_base_capture_apple_vision_ranges.json`
- `data/2026-06-07_base_capture_apple_vision_summary.json`
- `inputs/ocr_alliance_corrections.json`
