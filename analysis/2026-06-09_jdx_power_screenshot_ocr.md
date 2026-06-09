# 2026-06-09 JDX power screenshot OCR

## 1. Executive summary

JDX戦力スクショの今回アップ分を確認し、`IMG_8159.PNG` から `IMG_8191.PNG` までの33枚をApple Vision OCRで読み取った。

Google Sheets `JDX戦力など` の `現在週` へ直接反映する更新候補は作成したが、OCR名寄せに不安定な候補が含まれるため、シート更新は未実行とした。更新前に `data/2026-06-09_jdx_power_sheet_update_plan.csv` の確認が必要。

## 2. Context

- 対象フォルダ: `/Users/mba2025/Library/CloudStorage/Dropbox-FIT/訓北﨑/lastwar/S6/JDX戦力スクショ/inbox`
- 対象画像: `IMG_8159.PNG` - `IMG_8191.PNG`
- 画像更新時刻: 2026-06-09 19:26-19:27
- 対象シート: Google Sheets `JDX戦力など` (`1mKbtxgBPMP4oOLH3bEBq8A_vX2L7gXHR7qh37DA5ZNs`)
- 対象タブ: `現在週`

## 3. Key facts

- 今回分33枚のうち、`IMG_8159.PNG` - `IMG_8179.PNG` は投票者ポップアップで、選択肢番号と総戦力が読める。
- `IMG_8180.PNG` - `IMG_8191.PNG` はコメント欄一覧で、一軍編成・一軍戦力・職業が読める。
- OCR抽出結果:
  - 投票者OCR候補: 90行
  - コメントOCR候補: 45行
  - シート名簿に寄せた更新候補: 73名
  - 既存シートとの差分候補: 72名
- Google Sheets `戦力分析` は、確認時点で `2026/06/09 19:38:02` に再計算済みだった。

## 4. Timeline

- 2026-06-09 19:26-19:27: Dropbox `JDX戦力スクショ/inbox` に `IMG_8159.PNG` - `IMG_8191.PNG` が追加された。
- 2026-06-09 19:38: Google Sheets `戦力分析` の再計算時刻を確認。
- 2026-06-09 19:39: Apple Vision OCRを33枚に対して実行。
- 2026-06-09 19:42: OCR CSVとシート更新候補CSVを作成。
- 2026-06-09 19:43以降: シート一括更新は安全性確認のため未実行。

## 5. Interpretation

今回画像は、一軍戦力アンケートの投票選択肢とコメント欄を合わせて、JDX現在週データをかなり広く更新できる材料である。

ただし、投票者ポップアップはスクロール重複があり、OCRで名前が欠けた行や、名前の読み違いをシート名簿へ強く寄せてしまう候補がある。特に総戦力は増減が大きい候補があり、実際の変動か名寄せ誤りかを人間確認した方が安全。

## 6. Risks

- OCR名寄せにより、別人の総戦力を誤って上書きするリスクがある。
- `IMG_8180.PNG` - `IMG_8191.PNG` のコメント欄は絵文字や多言語表記があり、編成種別が欠落・誤読されることがある。
- `いたちごっこR` のコメントはOCRが `★163.9指導者` と読んだが、画像文脈では `航空 63.9 指導者` と見るのが自然。手動確認が必要。
- 生OCRテキストは `tmp/jdx_power_ocr_20260609.txt` に残したが、一時ファイル扱いでcommitしない。

## 7. Recommended actions

1. `data/2026-06-09_jdx_power_sheet_update_plan.csv` を確認し、総戦力が大きく減る候補と名前OCRが弱い候補を先に見る。
2. 確認済み行だけ `現在週!C:G` に反映する。
3. 反映後に `戦力分析` の再計算時刻と集計値を確認する。
4. 反映完了後、今回分 `IMG_8159.PNG` - `IMG_8191.PNG` を `processed` または `処理済み` へ移動する。

## 8. Unknowns

- 総戦力が前回より下がっている候補が、実際の戦力変動かOCR/名寄せミスか。
- コメント欄でOCRが編成を読めなかった候補の正しい編成。
- 今回画像を即時シート反映してよいか、またはユーザー確認後に分割反映するか。

## 9. Files referenced

- `data/2026-06-09_jdx_power_vote_ocr.csv`
- `data/2026-06-09_jdx_power_comment_ocr.csv`
- `data/2026-06-09_jdx_power_sheet_update_plan.csv`
- `tmp/jdx_power_ocr_20260609.txt` (not for commit)
- Google Sheets `JDX戦力など` / `現在週`
