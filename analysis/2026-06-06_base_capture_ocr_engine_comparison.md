# 拠点取得スクショ OCRエンジン比較

## 1. Executive summary

Dropbox `拠点取得スクショ/inbox` の先頭20枚で、Apple Vision / PaddleOCR / Tesseract を比較した。

結論として、拠点取得スクショでは Apple Vision を第1候補にできる。20枚すべてでサーバー、座標、連盟タグ、種別、時刻を検出し、平均処理時間も 0.728 秒/枚だった。PaddleOCR も同じく20枚すべて検出したが、平均 4.196 秒/枚で遅い。Tesseract は座標と種別が弱く、この用途の主エンジンにはしにくい。

## 2. Context

- 対象日: 2026-06-06
- 対象フォルダ: `/Users/mba2025/Library/CloudStorage/Dropbox-FIT/訓北﨑/lastwar/S6/拠点取得スクショ/inbox`
- サンプル: `IMG_1290.PNG` から `IMG_1310.PNG` までの20枚。欠番 `IMG_1297.PNG` は存在しないため除外。
- 前半10枚は「都市一覧 / 陣営破壊履歴」モーダル、後半10枚はチャットの「タイムライン」取得ログだった。
- 評価値は正解ラベルとの厳密照合ではなく、抽出項目の検出可否である。

## 3. Key facts

| Scope | Engine | Images | Avg sec | Server | Coordinate | Alliance | Kind | Time | Review rows |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all 20 | Apple Vision | 20 | 0.728 | 20 | 20 | 20 | 20 | 20 | 0 |
| all 20 | PaddleOCR | 20 | 4.196 | 20 | 20 | 20 | 20 | 20 | 0 |
| all 20 | Tesseract | 20 | 0.989 | 12 | 2 | 19 | 3 | 10 | 18 |
| history modal 10 | Apple Vision | 10 | 0.756 | 10 | 10 | 10 | 10 | 10 | 0 |
| history modal 10 | PaddleOCR | 10 | 4.449 | 10 | 10 | 10 | 10 | 10 | 0 |
| history modal 10 | Tesseract | 10 | 0.577 | 10 | 0 | 9 | 0 | 0 | 10 |
| timeline chat 10 | Apple Vision | 10 | 0.700 | 10 | 10 | 10 | 10 | 10 | 0 |
| timeline chat 10 | PaddleOCR | 10 | 3.943 | 10 | 10 | 10 | 10 | 10 | 0 |
| timeline chat 10 | Tesseract | 10 | 1.400 | 2 | 2 | 10 | 3 | 10 | 8 |

## 4. Interpretation

Apple Vision は、履歴モーダルとタイムラインログの両方で実用的に使える。処理速度が PaddleOCR の約5.8倍速く、座標 `#509(449,49)` と `#476(X:699,Y:20)` の両形式を拾えた。

PaddleOCR は、Apple Vision と同水準に抽出できるため、タグや数字の確認用セカンドパスとして有効。例として `IMG_1290.PNG` では Apple Vision が `ALj` と読んだ箇所を、PaddleOCR は `AL` と読んだ。連盟タグの `0/O`、`1/I/l`、末尾欠落の確認にはPaddle側を併用する価値がある。

Tesseract は、日本語UIと小さい座標の混在に弱い。タイムラインの時刻や一部タグは拾えるが、座標・種別の抽出が不足するため、メイン処理には向かない。

## 5. Recommended actions

1. 拠点取得スクショは Apple Vision を主エンジンにする。
2. 連盟タグや座標がシート更新に直結する行は PaddleOCR で再確認する。
3. Tesseract はこの用途では保険扱いに留め、シート反映の判定には使わない。
4. 次は20枚に人間ラベルを付け、検出率ではなく正解率で `Apple単独` と `Apple+Paddle確認` を比較する。

## 6. Files referenced

- `data/2026-06-06_base_capture_ocr_engine_comparison_summary.csv`
- `tmp/ocr_engine_comparison_base_capture_v2/ocr_engine_comparison_raw.csv`
- `tmp/ocr_engine_comparison_base_capture_v2/ocr_engine_comparison.md`
