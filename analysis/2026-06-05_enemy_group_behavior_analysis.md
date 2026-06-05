# Enemy group behavior analysis

## 1. Executive summary

2026-06-05時点の管理表CSV、侵攻候補CSV、協定チャットOCR、占領ログOCRを合わせると、敵側の押し込みは「単純な戦力差」だけでは説明しきれない。主圧力は#476系、横圧力は#480/#503系、協定・移動路設計は#440 GcC/APACHE周辺に見える。

敵側は「絶対に負けない」と考えているというより、局所的な損失が出ても、前線を広げ、pactで移動路を作り、こちらの確認・翻訳・協定調整の遅さを突けば、全体では押し切れると見ている可能性が高い。

#534/JDX側の対策は、全拠点防衛ではなく、守る場所を絞り、敵の移動路と判断速度を遅らせることに寄せるべきである。

## 2. Context

- 対象日時: 2026-06-05時点のローカル管理表・OCR成果物。
- 対象視点: #534/JDX。
- 主な参照データ:
  - `sample_output/sheet_migration/current_enemy_nodes_v2.csv`
  - `sample_output/sheet_migration/enemy_invasion_candidates_v2.csv`
  - `sample_output/sheet_migration/alliance_side_audit_v2.csv`
  - `analysis/2026-06-01_gcc_apache_diplomacy_ocr.md`
  - `analysis/2026-06-04_stronghold_occupation_ocr.md`

この分析は、現在の管理表反映とOCRレビュー結果を使った作戦判断メモであり、最終確定の外交記録ではない。

## 3. Key facts

### 3.1 Enemy-owned nodes

`current_enemy_nodes_v2.csv` の敵所有ノードは407件。

| owner server | enemy nodes |
|---:|---:|
| 476 | 240 |
| 480 | 103 |
| 503 | 62 |
| 299 | 2 |

敵所有ノードの上位連盟は以下。

| alliance | enemy nodes |
|---|---:|
| 476A | 38 |
| 476B | 30 |
| 476C | 30 |
| 476H | 29 |
| 476d | 27 |
| 476X | 27 |
| GX99 | 24 |
| 476Z | 22 |
| BgNa | 22 |
| Lghs | 22 |
| AAOA | 22 |
| RCON | 21 |
| TkTk | 20 |

### 3.2 High-risk enemy nodes

`current_enemy_nodes_v2.csv` で `critical` または `high` の敵ノードは151件。

| owner server | high or critical enemy nodes |
|---:|---:|
| 476 | 88 |
| 480 | 34 |
| 503 | 28 |
| 299 | 1 |

高リスク以上の上位連盟は、476A、476B、Lghs、RCON、476d、476C、GX99など。つまり、#476系が主圧力で、#480/#503系が別方向から補助的に圧を作っている。

### 3.3 Enemy invasion candidates

`enemy_invasion_candidates_v2.csv` の侵攻候補は41件。

| owner server | invasion candidates |
|---:|---:|
| 476 | 19 |
| 480 | 11 |
| 503 | 10 |
| 299 | 1 |

候補の出現エリアは、#509が12件、#476が8件、#503が8件、#534が5件、#480が5件、#511が2件、#523が1件。

#534周辺では以下が高リスクとして出ている。

| node | type | alliance | server | risk |
|---|---|---|---:|---|
| #534:D-11 | fishery | 476C | 476 | high |
| #534:D-13 | fishery | 476B | 476 | high |
| #534:E-13 | fishery | 476C | 476 | high |
| #534:D-7 | fishery | 476B | 476 | high |
| #534:E-7 | fishery | 476C | 476 | high |
| #534:a-12 | trade | 476X | 476 | high |
| #534:a-16 | trade | fzn | 503 | high |
| #534:a-18 | trade | 476A | 476 | high |
| #534:a-2 | trade | Lghs | 503 | high |
| #534:a-8 | trade | RCON | 480 | high |

## 4. Enemy group characteristics

### 4.1 #476 group: main pressure

#476系は敵所有ノード240件、高リスク以上88件、侵攻候補19件で最多である。476A、476B、476C、476d、476X、476H、476Zなど複数連盟が広く現れており、単一連盟の突撃ではなく、複数連盟で前線密度を作っている。

#534に対しては、D-11、D-13、E-13などの漁場・接続点へ既に食い込みがある。#509側にも D-11/D-13 の476A食い込みがあり、#534単独ではなく味方側の横線も同時に圧迫されている。

特徴は、主力を一点だけに置くよりも、複数連盟で面を押してこちらの確認負荷を増やすことにある。こちらが全件確認しようとすると、判断が遅れて相手の前進を許す。

### 4.2 #480 group: lateral pressure

#480系は敵所有ノード103件、高リスク以上34件、侵攻候補11件。RCON、AAOA、TkTk、BgNaなどが目立つ。

#480系は#480内に閉じているだけではなく、#503、#509、#534周辺にも現れる。これは単独の正面突破というより、#476の主圧力とは別方向から横圧力をかけ、#534/#509側の防衛判断を分散させる役割に見える。

### 4.3 #503 group: connection and trade pressure

#503系は敵所有ノード62件、高リスク以上28件、侵攻候補10件。LghsとGX99が目立つ。

侵攻候補では #503:d-10、#503:e-8 のcity、#503:d-2 のtrade、#534:a-2 のLghsなどが出ている。#503系は接続点、交易地、漁場を押さえながら、前線を横に広げる役として見るべきである。

### 4.4 Pact operation group: GcC/APACHE pattern

2026-06-01のGcC/APACHE外交OCRでは、APACHEが GoDs、IMp、SHA、BAJ、KTVS、4tH などのpactを使い、#523/#476方面へ移動路を作る構想を示している。

重要なのは、pactを「友好確認」ではなく「移動可能範囲を作る道具」として扱っている点である。GoDs/IMpとのpactを通じて#523へ進む話、SHA/BAJやKTVSとのpact調整、金曜・土曜といった曜日指定が出ているため、敵側または周辺勢力は曜日単位で侵攻・移動計画を分けている可能性がある。

この系統は直接の戦闘力だけでなく、協定、土地選択、シールド期間、移動タイミングを組み合わせている。言語差・確認待ち・協定未整理は、こちら側の弱点として突かれやすい。

## 5. Timeline interpretation

現時点の時系列データは完全ではない。`ownership_current.csv` は一部 `owner_server` が未解決で、6/4占領OCRも未正規化のレビューキューである。そのため、ここでは厳密な時系列確定ではなく、傾向として扱う。

- 管理表反映では、#476系が最も広く敵所有ノードを保持している。
- 侵攻候補では、#476系が#534/#509に直接食い込み、#480/#503系が別方向から横圧力を作っている。
- GcC/APACHEの協定OCRでは、pactを使った#523/#476方面の移動構想が示されている。
- 6/4占領OCRでは、#511、#509、#480、#534、#523、#440、#476など広範囲で占領通知が出ており、戦線全体の更新頻度が高い。ただしOCR揺れがあるため、個別連盟の断定には追加正規化が必要である。

## 6. Interpretation: why they are pushing in

敵の強さは、廃課金者がいることだけではない。より重要なのは、次の4点である。

1. 主攻勢の密度が高い。#476系が複数連盟で面を作っている。
2. 横展開がある。#480/#503系が別方向から防衛判断を分散させる。
3. pactを戦術化している。協定を移動路、曜日計画、土地確保と結びつけている。
4. こちらの遅さを突いている。確認、翻訳、協定調整、全件防衛判断に時間がかかるほど相手が有利になる。

「強すぎて負けることはない」というより、敵は「広げても全体では押し切れる」と見ている可能性が高い。局所的に失敗しても、全体の前線が進めばよいという発想であれば、多少雑な侵攻でも成立する。

一方で弱点もある。広げすぎた前線は防衛密度が落ちる。pact依存の移動路は、協定不成立、時間遅延、土地放棄、シールド期間の読み違いに弱い。こちらは正面から全て止めるのではなく、敵の運用速度を落とすことを狙うべきである。

## 7. Recommended actions

### 7.1 Defend only selected points

全拠点防衛を前提にしない。#534:D-11、#534:D-13、#534:E-13 のような食い込み点、中央入口、味方高戦力が即応できる点を優先する。

### 7.2 Put pact checks into the command tab

GoDs、IMp、SHA、BAJ、KTVS、4tH、GcC/APACHE周辺は、外交ログとして読むだけではなく、司令タブ上で `pact確認待ち`、`移動路リスク`、`曜日計画あり` として表示する。

### 7.3 Delay the enemy route, not every enemy node

#523/#476/#480方面の接続候補、交易地、漁場を「敵の移動路」として見る。守れない場所でも、放棄タイミング、再取得、ワンパン、偵察で敵の時間を削る。

### 7.4 Attack overextended lateral pressure

#480/#503系の横展開は、敵が広げすぎた場合の反撃候補にする。ただし、反撃は敵が薄い時だけに限定し、#476主攻勢への防衛火力を削らない。

### 7.5 Shorten decision language

多言語・多連盟で動くため、長い説明をやめる。司令タブには以下のような短文指示を出せる形にする。

```text
DEFEND #534:D-13 now. Need strong players. Hold until 22:00 JST.
DELAY #523 route. Scout first. Do not overcommit.
PACT CHECK: GoDs / IMp / SHA / BAJ. Confirm OK / NO / ETA.
ABANDON low-value node. Save troops for #534:D-11 and #534:E-13.
COUNTER only if #480/#503 line is weak.
```

## 8. Unknowns

- `alliance_side_audit_v2.csv` には unknown owner が多く、未解決連盟は敵味方を断定しない。
- 6/4占領OCRは未正規化のレビューキューであり、連盟名・サーバ番号・施設種別にOCR揺れが残る。
- GcC/APACHE外交OCRは会話スクショ解釈であり、実際にどのpactが成立したかは別確認が必要である。
- `owner_server=299` など少数の不自然な値はOCRまたは管理表解決の誤りである可能性がある。

## 9. Files referenced

- `sample_output/sheet_migration/current_enemy_nodes_v2.csv`
- `sample_output/sheet_migration/enemy_invasion_candidates_v2.csv`
- `sample_output/sheet_migration/alliance_side_audit_v2.csv`
- `sample_output/sheet_migration/ownership_current.csv`
- `analysis/2026-06-01_gcc_apache_diplomacy_ocr.md`
- `analysis/2026-06-04_stronghold_occupation_ocr.md`
