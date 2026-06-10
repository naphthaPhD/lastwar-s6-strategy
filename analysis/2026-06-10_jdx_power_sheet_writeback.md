# 2026-06-10 JDX power sheet writeback

## 1. Executive summary

JDX戦力スクショ・コメント動画OCRの安全候補を、Google Sheets `JDX戦力など` の `現在週` タブへ反映した。

反映対象は `data/2026-06-10_jdx_power_sheet_update_plan.csv` のうち `changed=True` かつ `safe_to_apply=True` の行。77名・332セルを `現在週!C:G` に書き込んだ。低スコア名寄せの4名は保留した。

## 2. Context

- 対象シート: Google Sheets `JDX戦力など`
- Spreadsheet ID: `1mKbtxgBPMP4oOLH3bEBq8A_vX2L7gXHR7qh37DA5ZNs`
- 対象タブ: `現在週`
- 反映元: `data/2026-06-10_jdx_power_sheet_update_plan.csv`
- 対象画像: `IMG_8197.PNG` - `IMG_8221.PNG`
- 対象動画: `ScreenRecording_06-10-2026 20-24-22_1.MP4`

## 3. Key facts

- 反映行数: 77名
- 反映セル数: 332セル
- 反映範囲: `現在週!C:G`
- 空欄OCR値は上書きに使わず、既存値を保持した。
- 保留行:
  - `Revo Geruge`: `low_comment_match`
  - `BCCR`: `low_vote_match`
  - `もるせら`: `low_comment_match;partial_comment_parse`
  - `Fateの晩风`: `low_vote_match;partial_comment_parse`
- `戦力分析` は反映後 `2026/06/10 20:55:01` に再計算済み。

## 4. Timeline

- 2026-06-10 20:26: `IMG_8197.PNG` - `IMG_8221.PNG` がDropbox `inbox` に追加された。
- 2026-06-10 20:44: コメント欄動画がDropbox `inbox` に追加された。
- 2026-06-10 21時台: OCRと更新候補CSVを作成。
- 2026-06-10 21時台: ユーザー指示により、安全候補77名・332セルを `現在週!C:G` へ反映。

## 5. Interpretation

`現在週` は、2026-06-10投票者スクショ由来の総戦力・一軍帯と、コメント動画由来の一軍編成・一軍戦力・職業を反映した状態になった。

低スコア名寄せの4名は、誤上書き防止のため未反映。必要なら画像・動画で目視確認してから個別反映する。

## 6. Risks

- `large_total_delta` の候補は安全名寄せとして反映済みだが、実変動かどうかは最終判断前にスポットチェックした方がよい。
- コメント動画は2026-06-07投稿が中心のため、一軍情報の鮮度は総戦力スクショより古い可能性がある。
- 保留4名は、現時点では前回値のまま残っている。

## 7. Recommended actions

1. `戦力分析` の更新後集計を使って、JDXのWeek 5配分を検討する。
2. 保留4名を必要に応じて目視確認し、個別反映する。
3. 総戦力の大幅増減が作戦判断に影響するメンバーだけ、元画像でスポットチェックする。

## 8. Unknowns

- 保留4名の正しい最新値。
- `large_total_delta` が実変動か一時的な表示/名寄せ揺れか。

## 9. Files referenced

- `data/2026-06-10_jdx_power_sheet_update_plan.csv`
- `data/2026-06-10_jdx_power_vote_ocr.csv`
- `data/2026-06-10_jdx_power_comment_video_ocr.csv`
- Google Sheets `JDX戦力など` / `現在週`
