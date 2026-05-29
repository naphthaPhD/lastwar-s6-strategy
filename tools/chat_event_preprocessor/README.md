# Chat Event Preprocessor

ゲーム内チャットのスクロール動画から、OpenAI API OCR に渡すべき「新規チャット行が出たフレーム」だけを抽出し、必要な crop 画像だけ OCR してゲームイベント JSON を作るツールです。

## 構成

- `chat_event_preprocessor.py`: mp4 から OCR 対象 crop を作る前処理
- `ocr_worker.py`: `cropped/*.png` を OpenAI Responses API で OCR し、`events.json` に追記
- `config.json`: 動画入力、ROI、差分閾値などの設定
- `prompt.txt`: OCR 用プロンプト
- `metadata.json`: 前処理ログ
- `events.json`: OCR 結果
- `ocr_errors.jsonl`: OCR 失敗ログ

## 必要なもの

- Python 3.10+
- ffmpeg
- OpenAI API key

ffmpeg は `ffmpeg -version` が通る状態にしてください。PATH にない場合は `config.json` の `ffmpeg_binary` に実行ファイルのフルパスを入れます。

## セットアップ

Windows:

```powershell
cd C:\Users\kitazaki\Documents\S6\tools\chat_event_preprocessor
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
$env:OPENAI_API_KEY="sk-..."
```

macOS / Linux:

```bash
cd tools/chat_event_preprocessor
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
export OPENAI_API_KEY="sk-..."
```

`.env.example` は環境変数名の見本です。このツール自体は `.env` を自動読み込みしないため、実行前にシェルの環境変数へ設定してください。

## 1. 前処理

`config.json` の `input_video` と `roi` を実動画に合わせて変更します。

```json
"input_video": "G:/マイドライブ/lastwar/S6/ScreenRecording_05-24-2026 21-40-38_1.mp4",
"roi": {
  "x": 120,
  "y": 300,
  "width": 900,
  "height": 1500,
  "relative": false
}
```

実行:

```powershell
.\.venv\Scripts\python .\chat_event_preprocessor.py --config config.json
```

macOS / Linux:

```bash
./.venv/bin/python chat_event_preprocessor.py --config config.json
```

出力:

```text
frames/
cropped/
diff/
metadata.json
```

`metadata.json` の例:

```json
[
  {
    "frame": "frame_0012.png",
    "timestamp_sec": 12,
    "new_content_detected": true,
    "crop_file": "crop_0012.png"
  }
]
```

## 2. OpenAI OCR

`metadata.json` のうち `new_content_detected: true` の `crop_file` だけを順番に処理します。既に `events.json` に成功記録がある crop は既定でスキップします。

実行:

```powershell
.\.venv\Scripts\python .\ocr_worker.py
```

macOS / Linux:

```bash
./.venv/bin/python ocr_worker.py
```

デフォルト:

- model: `gpt-5.4-mini`
- image detail: `low`
- max output tokens: `800`
- retries: `3`
- output: `events.json`

少量テスト:

```powershell
.\.venv\Scripts\python .\ocr_worker.py --limit 3
```

再OCR:

```powershell
.\.venv\Scripts\python .\ocr_worker.py --force
```

モデル変更:

```powershell
$env:OPENAI_OCR_MODEL="gpt-5.4-mini"
.\.venv\Scripts\python .\ocr_worker.py
```

## events.json

`events.json` は JSON 配列として保存され、成功した crop ごとに追記されます。

```json
[
  {
    "status": "ok",
    "frame": "frame_0012.png",
    "timestamp_sec": 12,
    "crop_file": "crop_0012.png",
    "model": "gpt-5.4-mini",
    "response_id": "resp_...",
    "metadata": {},
    "ocr_json": {
      "events": []
    }
  }
]
```

`ocr_json` には `response.output_text` を JSON として検証した結果を保存します。

## OCR失敗時

失敗した crop は `ocr_errors.jsonl` に1行JSONで記録します。失敗しても次の crop の処理は続行します。

## コスト削減の設計

- 前処理で新規行が出た crop のみ OCR
- OCR 済み crop は既定でスキップ
- `detail=low` を既定値に設定
- `max_output_tokens=800` で出力を抑制
- プロンプトは JSON only に限定

## ROI 設定

固定ピクセル指定:

```json
"roi": {
  "x": 120,
  "y": 300,
  "width": 520,
  "height": 650,
  "relative": false
}
```

画面サイズに対する比率指定:

```json
"roi": {
  "x": 0.05,
  "y": 0.25,
  "width": 0.90,
  "height": 0.55,
  "relative": true
}
```

## 主な調整項目

- `diff.threshold`: 平均差分量の閾値。高くすると保存数が減ります。
- `diff.min_changed_pixels_ratio`: 変化ピクセル比率の閾値。UIの小さな点滅を除外しやすくします。
- `dedupe.hamming_threshold`: 行画像ハッシュの近さ。大きくすると似た行を重複扱いしやすくなります。
- `dedupe.ignore_top_ratio` / `ignore_bottom_ratio`: チャット欄上端や下端の固定UIを行検出から除外します。
