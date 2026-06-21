# City destruction video GPT Vision workflow

都市破壊履歴のスクロール動画を、高密度フレーム抽出して OpenAI GPT Vision / Responses API に投げ、8サーバ別の破壊履歴CSVへ集計するための補助ツール。

## 目的

- Apple Vision の1fps OCRで落ちた都市破壊履歴を、GPT Visionで再確認する。
- 全動画をそのままAPIへ投げず、該当スクロール区間だけを高密度抽出する。
- 出力はCSV/JSONまで。Googleスプレッドシートへの反映は別判断で行う。

## 1. 該当区間の自動提案

既存の Apple Vision raw OCR がある場合、対象サーバが見えている秒数範囲を提案できる。

```bash
./.venv/bin/python tools/city_destroy_video_gpt_vision.py suggest-ranges \
  --server '#534' \
  --out tmp/city_destroy_gpt_vision_20260621/suggest_534.json
```

出力の `prepare_args` を次の `prepare --range` に渡す。

## 2. 高密度フレーム抽出

例: #534 の提案区間だけを 3fps で抽出する。

```bash
./.venv/bin/python tools/city_destroy_video_gpt_vision.py prepare \
  --video '/Users/mba2025/Library/CloudStorage/Dropbox-FIT/訓北﨑/lastwar/S6/拠点取得スクショ/review/ScreenRecording_06-21-2026 19-25-47_1.MP4' \
  --out-dir tmp/city_destroy_gpt_vision_20260621 \
  --range '20.500-31.500,49.500-66.500,76.500-109.500,139.500-162.500,167.500-180.500,189.500-224.500,233.500-261.500,271.500-300.500,304.500-312.500,318.500-352.500,357.500-368.500' \
  --fps 3 \
  --scale-width 1800
```

既定では履歴本文周辺だけを crop する。

## 3. GPT Vision OCR

実行前に `OPENAI_API_KEY` を設定する。

```bash
export OPENAI_API_KEY='sk-...'
export OPENAI_VISION_MODEL='gpt-5.4-mini'

./.venv/bin/python tools/city_destroy_video_gpt_vision.py ocr \
  --metadata tmp/city_destroy_gpt_vision_20260621/metadata.json \
  --out-dir tmp/city_destroy_gpt_vision_20260621 \
  --detail high \
  --batch-size 2 \
  --sleep 0.2
```

少量テスト:

```bash
./.venv/bin/python tools/city_destroy_video_gpt_vision.py ocr \
  --metadata tmp/city_destroy_gpt_vision_20260621/metadata.json \
  --out-dir tmp/city_destroy_gpt_vision_20260621 \
  --limit 3 \
  --batch-size 1
```

`--batch-size 2` は今回の動画で動作確認済み。`--batch-size 3` はAPI側の一時エラー/サイズ相性が出たため、長時間処理では2を推奨する。

## 4. 集計

GPT Vision OCR結果を重複排除し、8サーバ別に集計する。

```bash
./.venv/bin/python tools/city_destroy_video_gpt_vision.py aggregate \
  --events tmp/city_destroy_gpt_vision_20260621/gpt_vision_events.json \
  --run-date 2026-06-21_high_density \
  --compare-sheet
```

主な出力:

- `data/2026-06-21_high_density_city_destroy_gpt_vision_raw_events.csv`
- `data/2026-06-21_high_density_city_destroy_gpt_vision_deduped_events.csv`
- `data/2026-06-21_high_density_city_destroy_gpt_vision_summary.csv`
- `data/2026-06-21_high_density_city_destroy_gpt_vision_sheet_missing.csv`

## 色の解釈

- 赤字: 敵が破壊
- 青字: 味方が破壊
- 管理表の所有連盟としては、どちらも `破壊` にする。

## 注意

- このツールはGoogleスプレッドシートを直接更新しない。
- `sheet_missing.csv` を確認してから、既存のシート更新スクリプトまたは手動処理で反映する。
- まず `--limit 3` でAPI応答とJSON形式を確認する。
