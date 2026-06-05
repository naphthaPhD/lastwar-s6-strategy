# 拠点取得スクショ OCR正解ラベル

## 1. Executive summary

Dropbox `拠点取得スクショ/inbox` のOCR比較サンプル20枚に、人間ラベルを付与した。

このラベルは、Apple Vision / PaddleOCR / Tesseract の「検出できたか」ではなく「正しく読めたか」を評価するための正本として使う。

## 2. Context

- 対象画像: `IMG_1290.PNG` から `IMG_1310.PNG` までの20枚。欠番 `IMG_1297.PNG` は除外。
- 正解ラベル: `data/2026-06-06_base_capture_ocr_human_labels.csv`
- 前半10枚: `都市一覧 / 陣営破壊履歴` モーダルの先頭表示イベント。
- 後半10枚: チャット `タイムライン` 内で、画面内に時刻見出しが見えている最初のイベント。

## 3. Key facts

1. 履歴モーダル10枚は、攻撃側サーバー、攻撃側連盟、対象サーバー、座標、都市Lv、時刻をラベル化した。
2. タイムライン10枚は、連盟タグ、相手連盟、対象サーバー、座標、Lv、地形、種別、行動種別をラベル化した。
3. `IMG_1305.PNG` はOCRが `JDXI` と読みやすいが、目視ラベルは `JDX`。
4. `IMG_1307.PNG` と `IMG_1309.PNG` は、画面上端に前時刻グループの続きが見えているため、時刻見出しが表示されている最初のイベントを評価対象にした。

## 4. Label rule

履歴モーダルは、スクショ内の一番上の破壊履歴行を評価対象にする。

タイムラインは、時刻見出しが画面内に表示されている最初のイベントを評価対象にする。上端に途中から見えている前時刻グループのイベントは、時刻判定が曖昧になるため除外する。

## 5. Recommended next actions

1. `tmp/ocr_engine_comparison_base_capture_v2/ocr_engine_comparison_raw.csv` とこのラベルCSVを照合し、エンジン別の真の正解率を計算する。
2. 評価軸は、連盟タグ、対象サーバー、座標、種別、時刻を分けて計算する。
3. `IMG_1307.PNG` と `IMG_1309.PNG` のような時刻グループ境界ケースを、実運用でどう扱うか別途ルール化する。

## 6. Files referenced

- `data/2026-06-06_base_capture_ocr_human_labels.csv`
- `tmp/ocr_engine_comparison_base_capture_v2/ocr_engine_comparison_raw.csv`
