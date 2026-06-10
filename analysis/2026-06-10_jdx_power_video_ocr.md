# 2026-06-10 JDX power screenshot and comment video OCR

## 1. Executive summary

JDX戦力スクショの今回アップ分を確認し、静止画 `IMG_8197.PNG` - `IMG_8221.PNG` とコメント欄動画 `ScreenRecording_06-10-2026 20-24-22_1.MP4` をApple Vision OCRで読み取った。

Google Sheets `JDX戦力など` / `現在週` への更新候補CSVは作成済み。今回の書き戻しは未実行。

## 2. Context

- 対象フォルダ: `/Users/mba2025/Library/CloudStorage/Dropbox-FIT/訓北﨑/lastwar/S6/JDX戦力スクショ/inbox`
- 投票者静止画: `IMG_8197.PNG` - `IMG_8221.PNG`
- コメント欄動画: `ScreenRecording_06-10-2026 20-24-22_1.MP4`
- 動画長: 約62.6秒
- 動画フレーム抽出: 2秒ごと、31フレーム
- 対象シート: Google Sheets `JDX戦力など`
- 対象タブ: `現在週`

## 3. Key facts

- 静止画OCR候補: 107行
- 静止画OCRから名簿へ寄った総戦力候補: 77名
- 動画コメントOCR候補: 147行
- 動画コメントOCRから名簿へ寄った一軍情報候補: 69名
- シート更新候補: 82名
- 差分候補: 81名
- `safe_to_apply=True` の差分候補: 77名
- フラグ付き候補: 18名

## 4. Timeline

- 2026-06-10 20:26: `IMG_8197.PNG` - `IMG_8221.PNG` がDropbox `inbox` に追加された。
- 2026-06-10 20:44: コメント欄動画 `ScreenRecording_06-10-2026 20-24-22_1.MP4` がDropbox `inbox` に追加された。
- 2026-06-10 21時台: 動画を2秒ごとに31フレームへ分割し、静止画と合わせてApple Vision OCRを実行。
- 2026-06-10 21時台: OCR結果を `現在週` の指揮官名簿へ名寄せし、更新候補CSVを作成。

## 5. Interpretation

静止画は投票者ポップアップで、選択肢番号と総戦力を読み取れる。動画はコメント欄のスクロールで、一軍編成・一軍戦力・職業の補完に使える。

今回の動画コメントは、投稿日時が主に2026-06-07のコメント欄で、前回取り込んだ一軍情報と重なる内容が多い。一方、今回の投票者静止画は2026-06-10に追加された総戦力の新しい値として扱える可能性が高い。

## 6. Risks

- 投票者ポップアップはスクロール重複と名前OCR揺れがあり、低スコア名寄せ候補は手動確認が必要。
- コメント動画はフレーム間重複が多く、OCRが職業や編成を部分欠落させることがある。
- `large_total_delta` は実際の戦力変動かOCR/名寄せ誤りか判断が必要。
- `partial_comment_parse` はコメント本文が読めているが、編成・戦力・職業のいずれかが欠けている候補。

## 7. Recommended actions

1. `data/2026-06-10_jdx_power_sheet_update_plan.csv` を確認する。
2. `safe_to_apply=True` の行だけ先に反映する。
3. `flags` に `low_vote_match` または `low_comment_match` がある行は、画像または動画で確認してから反映する。
4. 反映後に `戦力分析` の再計算時刻と集計値を確認する。

## 8. Unknowns

- 総戦力の大幅増減が実変動か、投票者ポップアップの名寄せ誤りか。
- コメント動画で `partial_comment_parse` になった候補の正確な編成・職業。
- 今回の更新を全候補一括で反映するか、安全候補だけ反映するか。

## 9. Files referenced

- `data/2026-06-10_jdx_power_vote_ocr.csv`
- `data/2026-06-10_jdx_power_comment_video_ocr.csv`
- `data/2026-06-10_jdx_power_sheet_update_plan.csv`
- `tmp/jdx_power_ocr_20260610.txt` (not for commit)
- `tmp/jdx_20260610_video_frames/` (not for commit)
