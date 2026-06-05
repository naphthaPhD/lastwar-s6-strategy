# OCR Engine Comparison

## 1. Executive summary

Dropbox の漁場詳細スクリーンショット20枚で、Apple Vision、PaddleOCR、Tesseract を比較した。現時点では **Apple Vision を高速一次OCR、PaddleOCRを精度確認/照合、Tesseractを補助候補** とするのが良い。

ただし、この比較は正解ラベル付きの最終精度ではない。抽出できた項目数と代表行の目視確認に基づく一次評価である。

## 2. Context

- 対象: `Dropbox-FIT/訓北﨑/lastwar/S6/漁場スクショ/縦` と `漁場スクショ/ABC` から20枚
- 評価軸: サーバ番号、連盟タグ、種別、宣戦/保護時間、処理速度、レビュー要否
- 生データ: `tmp/ocr_engine_comparison_v3b/ocr_engine_comparison_raw.csv`
- 集計: `data/2026-06-06_ocr_engine_comparison_summary.csv`

## 3. Key facts

| Engine | Images | Avg sec | Server | Coordinate | Alliance | Kind | Time | Review rows |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Apple Vision | 20 | 0.836 | 20 | 0 | 20 | 20 | 20 | 0 |
| PaddleOCR | 20 | 4.476 | 20 | 0 | 20 | 20 | 20 | 0 |
| Tesseract | 20 | 2.711 | 19 | 0 | 20 | 11 | 20 | 9 |

`Coordinate` が0なのは、今回の漁場詳細スクショが `#509[eXt]漁場` のような表示で、X/Y座標を画面に出していないためである。

## 4. Interpretation

Apple Vision はサンドボックス外で実行すると正常に動き、今回の漁場詳細画面では非常に速い。`#509[OWM]漁場` や `2d 02:06:58` のような主要項目を読める。一方で、`K0CH` を `KOCH`、`SHA` を `SHA1`/`5HA` 風に読むなど、連盟タグの微妙な誤読はあり得る。

PaddleOCR は遅いが、今回の代表行では連盟タグの読みが安定していた。特に `K0CH`、`0WM`、`4tH`、`SHA` のような英数字混在タグでは、Apple VisionやTesseractより確認用として強い。

Tesseract は全体として読めるが、種別 `漁場` の取り落としが多く、レビュー必要行が9/20あった。単独の本命にはしづらい。

## 5. Recommended actions

1. 通常運用は Apple Vision で高速に候補抽出する。
2. 連盟タグ、特に `0/O`, `1/I/l`, `5/S`, `t/H` などが絡む行は PaddleOCR と照合する。
3. Tesseract は軽量な補助OCRまたは失敗時の追加材料に留める。
4. 次回は正解ラベル付きCSVを作り、タグ単位の真の正解率を計算する。

## 6. Unknowns

- 今回は漁場詳細スクショ中心であり、赤字占領ログ、動画crop、全体マップ、戦力表では結果が変わる可能性がある。
- Apple Vision は Codex サンドボックス内では `Foundation._GenericObjCError` で失敗したため、実行時は外側権限または通常Mac環境で動かす必要がある。
- 座標 `#534(X:...,Y:...)` の正解率は、座標表示があるログ系スクショで別途評価する必要がある。

## 7. Files referenced

- `tmp/ocr_engine_comparison_v3b/ocr_engine_comparison_raw.csv`
- `tmp/ocr_engine_comparison_v3b/ocr_engine_comparison.md`
- `data/2026-06-06_ocr_engine_comparison_summary.csv`
- `tools/ocr_engine_comparison.py`
- `tools/vision_ocr.swift`
