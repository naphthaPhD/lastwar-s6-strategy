# Base capture full OCR sheet update

## 1. Executive summary

Dropbox `拠点取得スクショ` 配下の全画像 234 枚を Apple Vision OCR で処理し、Google Sheets `管理表たたき` に 182 件を反映した。

更新対象は列 C:D:E:L で、種別、連盟、取得/破壊日時、OCR根拠メモを更新した。ユーザー訂正により `AL` は `ALj` として補正した。

## 2. Context

- 対象フォルダ: `/Users/mba2025/Library/CloudStorage/Dropbox-FIT/訓北﨑/lastwar/S6/拠点取得スクショ`
- 対象シート: Google Sheets `12uNW9XphH2zSX4h5BzjSd-OON9r5AckAuNCwQTbY79g` / `管理表たたき`
- 実行環境: Mac / Apple Vision OCR / Google Sheets API
- 実行スクリプト: `tools/base_capture_ocr_update.py`
- Apple Vision helper: `tools/vision_ocr.swift`

## 3. Key facts

- OCR対象画像: 234枚
- 抽出イベント: 721件
- 最新イベント候補: 534座標
- シート反映: 182件
- レビュー送り: 352件
- 書き込み後、5件をGoogle Sheetsから読み戻して C:D:E:L の反映一致を確認した。

## 4. Event breakdown

| Item | Count |
|---|---:|
| history_modal | 129 |
| timeline_chat | 592 |
| destroy | 129 |
| occupy | 333 |
| steal | 184 |
| first_occupy | 75 |

## 5. Sheet update breakdown

| Item | Count |
|---|---:|
| Total updates | 182 |
| 漁場 | 109 |
| 都市 | 73 |
| destroy | 48 |
| occupy | 66 |
| steal | 53 |
| first_occupy | 15 |
| owner changes | 19 |
| type changes | 0 |

## 6. Time handling

画面内時刻は `HH:MM` と `MM-DD HH:MM` の両方を認識した。時刻が表示されない行は、ファイル名番号順で直前の古い画像に見えていた時刻を補完した。

| Time source | Events | Updates |
|---|---:|---:|
| visible_datetime | 129 | 48 |
| visible_time | 314 | 129 |
| previous_image_visible_time | 276 | 5 |
| image_metadata_inferred | 2 | 0 |

`image_metadata_inferred` のイベントは最終更新には使っていない。

## 7. Review queue

| Reason | Count |
|---|---:|
| low_confidence_no_material_change | 155 |
| existing_newer | 138 |
| row_not_found | 57 |
| low_confidence_short_owner | 1 |
| type_mismatch | 1 |

`row_not_found` は管理表側に座標行が見つからないもの、`existing_newer` は既存シートの日時がOCR候補より新しいもの。`type_mismatch` は既存種別とOCR種別が異なるため更新を止めた。

## 8. Corrections

- `AL` は `ALj` として補正。
- `TKTK`/`TKTk` は `TkTk` として補正。
- `LO`/`L2` は `JL0`/`JL2` として補正。
- `GCC`/`Gcc` は `GcC` として補正。
- `SSQ`/`5sQ`/`5s0` は `SsQ` として補正。

## 9. Files referenced

- `data/2026-06-06_base_capture_full_ocr_events.csv`
- `data/2026-06-06_base_capture_full_ocr_sheet_updates.csv`
- `data/2026-06-06_base_capture_full_ocr_review.csv`
- `data/2026-06-06_base_capture_ocr_human_labels.csv`
- `inputs/ocr_alliance_corrections.json`
- `tools/base_capture_ocr_update.py`
- `tools/vision_ocr.swift`
