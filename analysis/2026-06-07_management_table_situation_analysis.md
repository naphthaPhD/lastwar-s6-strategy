# 管理表から見る #534/JDX 現状整理 2026-06-07

## 1. Executive summary

管理表上の結論は、「全面崩壊」ではなく「前線の限られた線に危険が圧縮されている」である。

- 全体マップでは critical 111件、high 167件だが、#534前線表に限定すると critical 2件、high 47件まで下がる。
- 敵保有ノード407件のうち #476 が240件、#480 が103件、#503 が62件。主敵は #476 で、#480/#503 が便乗圧を足している構図。
- #534単独で直接確認できる実行候補は、防衛edge 5件、攻撃edge 5件に絞れる。
- unknown edge 48件、unknown owner 655件、uncertain alert 1,380件は、即応判断ではなく地図確認・データ整理タスクとして分離するべき。

士気維持のため、当面の作戦説明は「全部守る」ではなく「10件だけ見る」に切り替えるのがよい。

## 2. Context

対象は、`sample_output/sheet_migration/` の管理表出力を中心にした #534/JDX の現状確認。

主に参照したファイル:

- `sample_output/sheet_migration/risk_map_v2.csv`
- `sample_output/sheet_migration/server_534_frontline_risk_v2.csv`
- `sample_output/sheet_migration/current_enemy_nodes_v2.csv`
- `sample_output/sheet_migration/current_friendly_nodes_v2.csv`
- `sample_output/sheet_migration/top_enemy_invasion_candidates_v2.csv`
- `sample_output/sheet_migration/top_server_534_attack_candidates_v2.csv`
- `sample_output/sheet_migration/server_534_attack_edges_self_v2.csv`
- `sample_output/sheet_migration/enemy_invasion_edges_self_defense_v2.csv`
- `analysis/r4_r5_briefing_2026-05-31.md`
- `analysis/commander_review_2026-05-31.md`

## 3. Key facts

### 全体リスク

| scope | critical | high | mid | low |
| --- | ---: | ---: | ---: | ---: |
| 全体マップ | 111 | 167 | 806 | 1,084 |
| #534前線 | 2 | 47 | 56 | 75 |

全体マップの件数をそのまま作戦担当が背負うと、心理的にも運用的にも重すぎる。実務では #534前線とedge候補に絞る。

### 敵保有ノード

| server | enemy nodes |
| --- | ---: |
| #476 | 240 |
| #480 | 103 |
| #503 | 62 |
| #299 | 2 |

#476 が敵保有ノードの約6割を占める。#480/#503 の侵攻は事実だが、主敵と便乗勢力を同じ重さで扱うと判断不能になる。

### #534直接edge

| category | count | interpretation |
| --- | ---: | --- |
| #534 direct defense edges | 5 | 今日の主確認対象 |
| #534 direct attack edges | 5 | 発射元・協定確認後に検討 |
| ally attack edges | 3 | #509/#440/#511との連携確認 |
| ally defense edges | 5 | 味方側の防衛可否確認 |
| unknown attack edges | 25 | 命令ではなく地図確認キュー |
| unknown defense edges | 23 | 命令ではなく地図確認キュー |

## 4. Timeline

- 2026-05-27から2026-05-30にかけて、#534の c-10, c-8, d-12, d-14, d-10, d-8, e-14, c-12 などの都市破壊ログが管理表に反映されている。
- 2026-05-31時点の R4/R5 briefing では、#534直接防衛edge 5件、#534単独攻撃edge 5件、味方連携攻撃edge 3件、味方防衛edge 5件、地図確認待ち攻撃25件・防衛23件として整理されていた。
- 2026-06-06/07のOCR更新により、破壊ログや管理表更新候補が追加されている可能性がある。

## 5. Interpretation

現在の「やる気が削られる」感覚は、データ上も妥当である。敵が強いだけでなく、#480/#503などの便乗圧も加わっており、画面上は複数方向から押されているように見える。

ただし、管理表を分解すると、作戦判断に使うべき対象はかなり絞れる。全体の critical/high 件数、unknown owner、uncertain alert を同時に見ると絶望感が出るが、これは「即応判断」と「データ整理」が混ざっているため。

今の局面は、勝ち筋を広く探すよりも、次の3つを分けるべきである。

1. 今日見る防衛線: D-11 / D-13 / E-13周辺。
2. 連携確認に回す候補: #509/#440/#511の味方edge。
3. 見ないと決めるもの: unknown edge、unknown owner、未確定安全時間、重要度の低い外縁。

## 6. Risks

1. **全部守ろうとして幹部・主力が折れるリスク。**
   管理表の全件を作戦対象にすると、人間側の処理能力を超える。

2. **unknown edgeを命令に混ぜて混乱するリスク。**
   unknown edge は地図確認キューであり、直接命令に使うべきではない。

3. **便乗勢力を主敵と同じ重さで扱うリスク。**
   #480/#503の圧はあるが、主軸は #476。便乗組は接続・隣接確認に絞る。

4. **破壊済み都市を奪還目標として見てしまうリスク。**
   旧管理表では #534破壊済み都市8件だったが、2026-06-07のゲーム画面確認では23件。最新は23件を確認済み損失として扱い、接続喪失と士気説明の材料にする。

## 7. Recommended actions

1. **今日のR4/R5確認は10件だけに絞る。**
   #534直接防衛edge 5件、#534直接攻撃edge 5件だけを確認対象にする。

2. **防衛優先は D-11 / D-13 / E-13 周辺。**
   SHA/JDXの発射元・防衛元と、476B/476Cの隣接を重点確認する。

3. **unknown系は「見ない棚」に置く。**
   unknown attack 25件、unknown defense 23件、unknown owner 655件、uncertain alert 1,380件は、今日の作戦判断から外す。

4. **幹部共有文は「全部守らない」を明文化する。**
   例:

   ```text
   現状、敵の圧は強いですが、管理表上の即応対象は絞れます。
   今日見るのは #534直接防衛5件・直接攻撃5件のみです。
   unknown edgeや所有者未確認は地図確認キューに回し、作戦命令には使いません。
   全部守るのではなく、D-11 / D-13 / E-13周辺だけを重点確認します。
   ```

5. **士気維持のため、作戦の言葉を小さくする。**
   「勝つ」「取り返す」より、「10件だけ見る」「残す」「損害を増やさない」に寄せる。

## 8. Unknowns

- 管理表出力は 2026-05-31 生成系と 2026-06-06/07 OCR更新が混在している可能性があり、最新ゲーム内地図との差分確認が必要。
- edge候補は confidence=medium が中心で、地図・協定・安全時間の人間確認前提。
- city_destroy_enabled が FALSE の時間帯では、都市破壊候補は実行対象ではない。
- unknown owner 655件のうち、作戦に関係するものだけを別途抽出する必要がある。

## 9. Files referenced

- `sample_output/sheet_migration/risk_map_v2.csv`
- `sample_output/sheet_migration/server_534_frontline_risk_v2.csv`
- `sample_output/sheet_migration/current_enemy_nodes_v2.csv`
- `sample_output/sheet_migration/current_friendly_nodes_v2.csv`
- `sample_output/sheet_migration/top_enemy_invasion_candidates_v2.csv`
- `sample_output/sheet_migration/top_server_534_attack_candidates_v2.csv`
- `sample_output/sheet_migration/server_534_attack_edges_self_v2.csv`
- `sample_output/sheet_migration/server_534_attack_edges_ally_v2.csv`
- `sample_output/sheet_migration/server_534_attack_edges_unknown_v2.csv`
- `sample_output/sheet_migration/enemy_invasion_edges_self_defense_v2.csv`
- `sample_output/sheet_migration/enemy_invasion_edges_ally_defense_v2.csv`
- `sample_output/sheet_migration/enemy_invasion_edges_unknown_v2.csv`
- `sample_output/sheet_migration/alerts_v2.csv`
- `sample_output/sheet_migration/unknown_owner_review_v2.csv`
- `sample_output/sheet_migration/type_uncertain_review_v2.csv`
- `analysis/r4_r5_briefing_2026-05-31.md`
- `analysis/commander_review_2026-05-31.md`
