# S6 Week 4 end #534 situation summary

## 1. Executive summary

2026-06-07時点、4週目終了後の戦況は「#476主導の敵圧が強く、#480/#503が便乗・側圧を加え、#534全体がジリ貧に入っている」状態である。管理表上は全面崩壊ではないが、都市損失、接続喪失、味方側の損耗が積み重なっており、#534全体としては戦線を広げる余力が落ちている。

- 全体マップでは critical 111件、high 167件。ただし `node_current_v2.csv` は古く、破壊済み都市数は最新ゲーム画面より過小。
- #534の破壊済み都市は、ゲーム画面確認で23件。旧管理表集計の8件は古い値として扱う。
- 敵保有ノード407件のうち #476 が240件、#480 が103件、#503 が62件。主敵は #476。
- #534前線に限定すると critical 2件、high 47件。即応対象は #534直接防衛edge 5件、直接攻撃edge 5件に圧縮できる。
- Week 5は、聖所攻防、前哨基地争奪、火曜祭壇、水曜/土曜破壊戦が重なるため、「全部守る」ではなく「接続と参加権を残す」方針へ切り替える。

## 2. Context

このまとめは、4週目終了時点で全体戦況と #534全体の状況をChatGPT・幹部向けに引き継ぐためのもの。JDX個別の評価ではなく、#534全体の防衛・接続・士気・Week5参加権を扱う。

主な参照元:

- `sample_output/sheet_migration/risk_map_v2.csv`
- `sample_output/sheet_migration/node_current_v2.csv`
- `sample_output/sheet_migration/current_enemy_nodes_v2.csv`
- `sample_output/sheet_migration/current_friendly_nodes_v2.csv`
- `sample_output/sheet_migration/server_534_frontline_risk_v2.csv`
- `sample_output/sheet_migration/top_critical_risks_534_v2.csv`
- `sample_output/sheet_migration/top_enemy_invasion_candidates_v2.csv`
- `sample_output/sheet_migration/top_server_534_attack_candidates_v2.csv`
- `analysis/2026-06-07_management_table_situation_analysis.md`
- `strategy/season6_strategy.md`
- `docs/season6_mechanics.md`

## 3. Key facts

### 全体戦況

| metric | value |
| --- | ---: |
| 全体 critical risk | 111 |
| 全体 high risk | 167 |
| 全体 mid risk | 806 |
| 全体 low risk | 1,084 |
| 敵保有ノード | 407 |
| 味方/自陣営保有ノード | 272 |
| 破壊済み都市 | 要再集計 |
| uncertain alert | 1,380 |
| unknown owner rows | 655 |
| type uncertain rows | 132 |

全体表は危険件数が多いが、uncertain/unknown系が多く混ざっている。幹部判断では、全体表をそのまま作戦対象にせず、前線・edge・Week5参加権に関わるものだけを抽出する。

### 破壊済み都市の分布

重要: この表は、#534のみゲーム画面確認値へ補正している。他エリアは旧 `node_current_v2.csv` 集計値であり、最新ゲーム画面または全体マップ再反映後に再集計する必要がある。

| area | destroyed cities |
| --- | ---: |
| #509 | 42 |
| #511 | 34 |
| #480 | 19 |
| #534 | 23 |
| #440 | 4 |
| #476 | 2 |

#534の損害は、旧管理表の8件ではなく、ゲーム画面確認の23件として扱う。これは接続と士気へ大きく響く数字であり、#534全体がジリ貧に入っている判断を強める。さらに味方陣営全体では #509/#511 の都市破壊も大きく、#534は単独で押し返すというより、#509/#440/#511との接続・前哨基地・聖所参加条件を残せるかが焦点になる。

### 敵保有ノードの主軸

| enemy server | enemy-owned nodes |
| --- | ---: |
| #476 | 240 |
| #480 | 103 |
| #503 | 62 |
| #299 | 2 |

敵の主軸は #476。#480/#503は便乗圧・側圧として扱う。#480/#503を主敵と同じ重さで扱うと、確認対象が広がりすぎて判断が鈍る。

### #534前線リスク

| scope | critical | high | mid | low |
| --- | ---: | ---: | ---: | ---: |
| 全体マップ | 111 | 167 | 806 | 1,084 |
| #534前線 | 2 | 47 | 56 | 75 |

#534前線の critical は #476 d-12 / d-14 の都市2件。high は47件あるが、その多くは #476/#480/#503 の都市・漁場・交易地が #534/味方線に近いという候補であり、人間確認前提である。

### #534破壊済み重要都市

| coord | group | risk_score |
| --- | --- | ---: |
| c-10 | frontline_core | 160 |
| c-8 | frontline_core | 160 |
| d-12 | frontline_core | 160 |
| d-14 | frontline_core | 160 |
| d-10 | frontline_adjacent | 145 |
| d-8 | frontline_adjacent | 145 |
| e-14 | frontline_adjacent | 145 |
| c-12 | other | 130 |

上記8件は旧管理表で確認できていた #534破壊済み重要都市であり、最新ゲーム画面の23件全体ではない。残り15件は、ゲーム画面または更新済み全体マップから座標を再抽出する必要がある。23件全体は奪還対象ではなく、接続喪失・防衛線再設計・士気説明の材料として扱う。

## 4. Timeline

- Week 3以降、火曜祭壇と水曜/土曜の都市破壊戦が本格化。
- 2026-05-27から2026-05-30にかけて、#534では c-8/c-10/d-8/d-10/d-12/d-14/e-14/c-12 の都市破壊ログが旧管理表に反映。
- 2026-06-07のユーザーゲーム画面確認では、#534破壊済み都市は23件。旧管理表の8件は過小として扱う。
- 4週目終了時点で、前哨基地配置・建設開始フェーズに入り、Week5以降の聖所攻防・前哨基地争奪へ移行する。
- Week5以降、敵陣営聖所攻防は第5-7週土曜13:00サーバー時間、1時間開催予定。
- JDXスケジュール画像ベースでは、前哨基地争奪は D-31/D-38/D-45 に発生する見込み。実際の開始/終了時刻はゲーム内カレンダー確認が必要。

## 5. Interpretation

4週目終了時点の全体像は、敵が強いだけでなく、戦場が「都市破壊」「前線漁場」「交易地」「前哨基地」「聖所参加条件」に分岐し始めた局面である。ここで全表を同じ重さで見ると、作戦担当も連盟員も疲弊する。

#534全体にとっての意味は3つある。

1. **#476主軸の圧を正面から全部受ける局面ではない。**
   #476は敵保有ノード240で突出しており、正面決戦は不利。#534は遅滞、防衛線縮小、#509/#440/#511連携の橋渡しに寄せる。これは前向きな攻勢転換ではなく、ジリ貧を止めるための損害限定策である。

2. **破壊済み都市は、取り返す対象ではなく接続再設計の前提である。**
   破壊済み都市は復旧しない前提で、残る漁場・拠点・盟約・前哨基地の接続を見直す。

3. **Week5は勢力値より参加権の週になる。**
   聖所攻防と前哨基地は、単体戦力だけでなく、隣接領土、前哨基地、盟約先が参加条件に関わる。守るべきものは「都市数」より「Week5-7に参加できる接続」である。

## 6. Risks

1. **全面防衛を掲げて士気が落ちるリスク。**
   管理表上は作戦対象を絞れるため、「全部守る」は避けるべき。

2. **unknown/uncertainを作戦命令に混ぜるリスク。**
   unknown owner 655件、uncertain alert 1,380件は整理課題であり、即応命令ではない。

3. **#480/#503の便乗圧を主敵化するリスク。**
   #480/#503は重要だが、主軸は #476。便乗勢力は接続・隣接・味方連携確認に限定する。

4. **Week5イベントの優先順位が曖昧になるリスク。**
   聖所攻防、前哨基地、火曜祭壇、水曜/土曜破壊戦が重なるため、集合優先順位を先に決める必要がある。

5. **#509/#511の損耗を見落とすリスク。**
   旧管理表では破壊済み都市は #509 42件、#511 34件。#534はゲーム画面確認で23件まで増えているため、味方側の接続弱体化と#534自身の損耗を両方見る必要がある。

## 7. Recommended actions

### 全体方針

1. **Week5は「勝ち切る」より「参加権と接続を残す」週として扱う。**
2. **主敵 #476、便乗 #480/#503、味方接続 #509/#440/#511 に分けて管理する。**
3. **全体risk_mapではなく、#534前線riskとedge候補だけを日次確認対象にする。**

### #534全体向け

1. **今日の確認対象は10件まで。**
   #534直接防衛edge 5件、#534直接攻撃edge 5件だけを見る。

2. **防衛優先は D-11 / D-13 / E-13 周辺。**
   SHA/JDXなど#534内の発射元・防衛元と、476B/476Cの隣接を確認する。

3. **破壊済み都市23件は「損失確定」として扱う。**
   取り返しや反撃感情ではなく、Week5接続再設計の前提にする。

4. **unknown系は即応判断から外す。**
   unknown attack 25件、unknown defense 23件、unknown owner 655件は地図確認キューに回す。

5. **幹部共有では次の言い方にする。**

   ```text
   4週目終了時点で、#534全体はジリ貧です。敵の主軸は#476です。
   #480/#503の便乗圧もありますが、全部を同じ重さでは見ません。
   Week5は、都市を全部守る週ではなく、聖所・前哨基地に参加できる接続を残し、これ以上の消耗を抑える週です。
   今日の確認対象は#534直接防衛5件・直接攻撃5件に絞ります。
   unknown系は地図確認キューに回し、作戦命令には使いません。
   ```

## 8. Unknowns

- Week5の前哨基地争奪戦の正確な開始/終了時刻。
- #534全体がWeek5聖所攻防でどの聖所/前哨基地/盟約ルートに参加できるか。
- #509/#511の都市破壊が、味方側の聖所/議事堂参加条件にどこまで影響するか。
- #534破壊済み都市23件の座標一覧。
- 管理表の2026-06-06/07 OCR更新とゲーム画面確認値が `全体マップ` に完全反映されているか。
- unknown owner 655件のうち、Week5参加権に関係するものが何件あるか。

## 9. Files referenced

- `sample_output/sheet_migration/risk_map_v2.csv`
- `sample_output/sheet_migration/node_current_v2.csv`
- `sample_output/sheet_migration/current_enemy_nodes_v2.csv`
- `sample_output/sheet_migration/current_friendly_nodes_v2.csv`
- `sample_output/sheet_migration/server_534_frontline_risk_v2.csv`
- `sample_output/sheet_migration/top_critical_risks_534_v2.csv`
- `sample_output/sheet_migration/top_enemy_invasion_candidates_v2.csv`
- `sample_output/sheet_migration/top_server_534_attack_candidates_v2.csv`
- `sample_output/sheet_migration/alerts_v2.csv`
- `sample_output/sheet_migration/unknown_owner_review_v2.csv`
- `sample_output/sheet_migration/type_uncertain_review_v2.csv`
- `analysis/2026-06-07_management_table_situation_analysis.md`
- `strategy/season6_strategy.md`
- `docs/season6_mechanics.md`
