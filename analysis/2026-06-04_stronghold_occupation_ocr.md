# 2026-06-04 拠点占領ログOCR

## 1. Executive summary

`ScreenRecording_06-04-2026 20-53-24_1.MP4` から、拠点占領系のチャットログをOCRし、座標付きイベントとして抽出した。

- OCR対象crop: 183件
- OCR成功: 183件
- OCR失敗: 0件
- 座標付き抽出イベント: 852件
- 機械的な重複除去後のイベント: 450件

## 2. Context

対象はゲーム内チャットに流れる「連盟Xが Lv.N 拠点/漁場などを占領しました」系のログである。動画末尾のスマホ操作画面2フレームは、ゲームログではないためOCR対象から除外した。

## 3. Key facts

出力先:

- `outputs/chat_event_preprocessor/20260604_205324/events.json`
- `outputs/chat_event_preprocessor/20260604_205324/stronghold_events_all.json`
- `outputs/chat_event_preprocessor/20260604_205324/stronghold_events_unique.json`
- `outputs/chat_event_preprocessor/20260604_205324/stronghold_events_unique.csv`
- `outputs/chat_event_preprocessor/20260604_205324/stronghold_summary.json`

サーバ別の重複除去後件数:

| server | unique events |
|---:|---:|
| 511 | 93 |
| 509 | 85 |
| 480 | 70 |
| 534 | 58 |
| 523 | 36 |
| 440 | 35 |
| 476 | 28 |
| 8061 | 22 |
| 503 | 18 |
| 459 | 3 |
| 522 | 1 |
| 806 | 1 |

主な施設種別:

| resource type | unique events |
|---|---:|
| 漁場 | 288 |
| 交易地 | 26 |
| 密林の村 | 21 |
| 湿地の村 | 18 |
| 密林の兵舎 | 10 |
| 密林の集会場 | 9 |
| 密林の集合場 | 8 |
| 湿地の兵舎 | 4 |

## 4. Timeline

この動画はOCRの前処理対象として扱い、詳細な時系列本文は `events.json` と `stronghold_events_all.json` に保存した。精査時は `stronghold_events_unique.csv` を開くと、座標・施設・Lv・連盟単位で確認しやすい。

## 5. Interpretation

この動画は、#511、#509、#480、#534 周辺の占領通知が多い。特に漁場の占領通知が大半を占めているため、拠点全般というより、漁場を中心に各連盟が広範囲で占領を進めている状況の証拠ログとして使える。

## 6. Risks

OCR結果には表記揺れが残る。例として、`漁場` が `魚場` になる、`兵舎` が `兵舍` になる、連盟名に `連盟` 接頭辞が残る、施設種別に余計な文字が混ざるケースがある。`stronghold_events_unique.csv` は機械的な重複除去結果であり、最終判断前には重要行の目視確認が必要である。

## 7. Recommended actions

1. まず `stronghold_events_unique.csv` を使い、#534、#511、#509、#480、#523、#476 の占領地点を確認する。
2. 重要な座標だけを正規化し、戦略判断用の `data/` または `logs/timeline/` に移す。
3. 連盟名と施設種別の揺れを正規化する小スクリプトを追加すると、次回以降の比較が楽になる。

## 8. Unknowns

- `8061` など、サーバ番号として不自然な値はOCR誤読の可能性がある。
- 一部の施設種別はOCRがチャット本文や装飾文字を混ぜている可能性がある。
- 同じ地点の再占領、別連盟による奪取、単なる重複表示の区別は、現時点では完全には分離していない。

## 9. Files referenced

- `ScreenRecording_06-04-2026 20-53-24_1.MP4`
- `outputs/chat_event_preprocessor/20260604_205324/metadata.json`
- `outputs/chat_event_preprocessor/20260604_205324/events.json`
- `outputs/chat_event_preprocessor/20260604_205324/stronghold_summary.json`
- `outputs/chat_event_preprocessor/20260604_205324/stronghold_events_unique.csv`
