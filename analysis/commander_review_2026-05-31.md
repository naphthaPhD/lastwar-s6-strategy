# ???CSV???? 2026-05-31

?????????????????????????????
`confidence=medium` ?????????????????????????
`from_node_id` ??????????????????????????????????

## 1. #534??????

| metric | value | note |
| --- | --- | --- |
| battle_window_status | saturday_server_day | 2026-05-30T11:00+09:00 - 2026-05-31T10:59+09:00 |
| server_day | saturday | JST based server day |
| city_destroy_enabled | TRUE | city destroy candidates are time-sensitive |
| critical risk count | 55 | risk_map_v2 |
| high risk count | 193 | risk_map_v2 |
| current enemy nodes | 441 | current enemy-owned nodes |
| current friendly nodes | 262 | current self/ally-owned nodes |
| server_534 frontline risk count | 190 | owned frontline rows for review |
| enemy_invasion_candidates count | 49 | enemy-owned frontline candidates |
| server_534_attack_candidates count | 388 | enemy-owned attack-review candidates |
| unknown owner count | 646 | owned rows with current_alliance but unresolved owner_server |
| type uncertain count | 132 | node type needs review |
| safe time reference count | 1349 | safe_until_jst is reference only |

## 2. #534 Critical Risk

| rank | node_id | coord | current_alliance | owner_server | server_side | risk_score | risk_reason | recommended_action | confidence | memo_short |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | #534:c-10 | c-10 |  | none | destroyed | 160 | city +30; destroyed_flag +100; frontline_core +30 | 破壊済み確認 | high | 都市破壊ログ 2026/05/28 12:11:39 / #534 X:449 Y:249 Lv.2都市 / 攻撃側 #476[476C] / 防衛側 #53… |
| 2 | #534:c-8 | c-8 |  | none | destroyed | 160 | city +30; destroyed_flag +100; frontline_core +30 | 破壊済み確認 | high | 都市破壊ログ 2026/05/28 12:13:53 / #534 X:349 Y:249 Lv.2都市 / 攻撃側 #476[476C] / 防衛側 #53… |
| 3 | #534:d-12 | d-12 |  | none | destroyed | 160 | city +30; destroyed_flag +100; frontline_core +30 | 破壊済み確認 | high | 都市破壊ログ 2026/05/27 20:02:15 / #534 X:549 Y:349 Lv.3都市 / 攻撃側 #476[476B] / 防衛側 #53… |
| 4 | #534:d-14 | d-14 |  | none | destroyed | 160 | city +30; destroyed_flag +100; frontline_core +30 | 破壊済み確認 | high | 都市破壊ログ 2026/05/27 20:04:34 / #534 X:649 Y:349 Lv.3都市 / 攻撃側 #476[476B] / 防衛側 #53… |

## 3. ?????

| rank | from_coord | from_alliance | from_server | to_coord | to_alliance | to_server | candidate_reason | priority | recommended_action | confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | d-12 | 476B | 476 |  | #534/ally line | 534/509/440/511 | city +30; enemy_flag +40; frontline_core +30 | critical | 防衛確認 | medium |
| 2 | d-14 | 476B | 476 |  | #534/ally line | 534/509/440/511 | city +30; enemy_flag +40; frontline_core +30 | critical | 防衛確認 | medium |
| 3 | d-14 | BgNa | 480 |  | #534/ally line | 534/509/440/511 | city +30; enemy_flag +40; frontline_core +30 | critical | 防衛確認 | medium |
| 4 | d-10 | 476B | 476 |  | #534/ally line | 534/509/440/511 | city +30; enemy_flag +40; frontline_adjacent +15 | high | 隣接確認 | medium |
| 5 | d-2 | 476K | 476 |  | #534/ally line | 534/509/440/511 | city +30; enemy_flag +40; frontline_adjacent +15 | high | 隣接確認 | medium |
| 6 | d-6 | 476M | 476 |  | #534/ally line | 534/509/440/511 | city +30; enemy_flag +40; frontline_adjacent +15 | high | 隣接確認 | medium |
| 7 | e-14 | 476d | 476 |  | #534/ally line | 534/509/440/511 | city +30; enemy_flag +40; frontline_adjacent +15 | high | 隣接確認 | medium |
| 8 | e-18 | 476Z | 476 |  | #534/ally line | 534/509/440/511 | city +30; enemy_flag +40; frontline_adjacent +15 | high | 隣接確認 | medium |
| 9 | e-18 | AAOA | 480 |  | #534/ally line | 534/509/440/511 | city +30; enemy_flag +40; frontline_adjacent +15 | high | 隣接確認 | medium |
| 10 | e-6 | TkTk | 480 |  | #534/ally line | 534/509/440/511 | city +30; enemy_flag +40; frontline_adjacent +15 | high | 隣接確認 | medium |
| 11 | e-8 | BgNa | 480 |  | #534/ally line | 534/509/440/511 | city +30; enemy_flag +40; frontline_adjacent +15 | high | 隣接確認 | medium |
| 12 | d-10 | Lghs | 503 |  | #534/ally line | 534/509/440/511 | city +30; enemy_flag +40; frontline_adjacent +15 | high | 隣接確認 | medium |
| 13 | e-8 | Lghs | 503 |  | #534/ally line | 534/509/440/511 | city +30; enemy_flag +40; frontline_adjacent +15 | high | 隣接確認 | medium |
| 14 | d-10 | SHA | 503 |  | #534/ally line | 534/509/440/511 | city +30; enemy_flag +40; frontline_adjacent +15 | high | 隣接確認 | medium |
| 15 | d-4 | nO9 | 476 |  | #534/ally line | 534/509/440/511 | city +30; enemy_flag +40; frontline_adjacent +15 | high | 隣接確認 | medium |
| 16 | e-14 | SHA | 503 |  | #534/ally line | 534/509/440/511 | city +30; enemy_flag +40; frontline_adjacent +15 | high | 隣接確認 | medium |
| 17 | e-4 | nO9 | 476 |  | #534/ally line | 534/509/440/511 | city +30; enemy_flag +40; frontline_adjacent +15 | high | 隣接確認 | medium |
| 18 | e-6 | SHA | 503 |  | #534/ally line | 534/509/440/511 | city +30; enemy_flag +40; frontline_adjacent +15 | high | 隣接確認 | medium |
| 19 | D-11 | 476A | 476 |  | #534/ally line | 534/509/440/511 | fishery +10; enemy_flag +40; frontline_core +30 | high | 防衛確認 | medium |
| 20 | D-13 | 476A | 476 |  | #534/ally line | 534/509/440/511 | fishery +10; enemy_flag +40; frontline_core +30 | high | 防衛確認 | medium |
| 21 | D-11 | 476C | 476 |  | #534/ally line | 534/509/440/511 | fishery +10; enemy_flag +40; frontline_core +30 | high | 防衛確認 | medium |
| 22 | D-13 | 476B | 476 |  | #534/ally line | 534/509/440/511 | fishery +10; enemy_flag +40; frontline_core +30 | high | 防衛確認 | medium |
| 23 | E-11 | SHA | 503 |  | #534/ally line | 534/509/440/511 | fishery +10; enemy_flag +40; frontline_core +30 | high | 防衛確認 | medium |
| 24 | E-13 | 476C | 476 |  | #534/ally line | 534/509/440/511 | fishery +10; enemy_flag +40; frontline_core +30 | high | 防衛確認 | medium |
| 25 | d-2 | GX99 | 503 |  | #534/ally line | 534/509/440/511 | trade +20; enemy_flag +40; frontline_adjacent +15 | high | 隣接確認 | medium |
| 26 | d-20 | 476A | 476 |  | #534/ally line | 534/509/440/511 | trade +20; enemy_flag +40; frontline_adjacent +15 | high | 隣接確認 | medium |
| 27 | e-20 | 476B | 476 |  | #534/ally line | 534/509/440/511 | trade +20; enemy_flag +40; frontline_adjacent +15 | high | 隣接確認 | medium |
| 28 | e-2 | AAOA | 480 |  | #534/ally line | 534/509/440/511 | trade +20; enemy_flag +40; frontline_adjacent +15 | high | 隣接確認 | medium |
| 29 | d-20 | 476X | 476 |  | #534/ally line | 534/509/440/511 | trade +20; enemy_flag +40; frontline_adjacent +15 | high | 隣接確認 | medium |
| 30 | D-3 | 476K | 476 |  | #534/ally line | 534/509/440/511 | fishery +10; enemy_flag +40; frontline_adjacent +15 | high | 隣接確認 | medium |

## 4. #534??????

| rank | from_coord | from_alliance | to_coord | to_alliance | to_server | attack_reason | priority | recommended_action | city_destroy_window | confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 |  | #534/ally attack group | d-12 | 476B | 476 | city +30; enemy_flag +40; frontline_core +30 | critical | 都市破壊候補 | saturday_server_day 2026-05-30T11:00+09:00 - 2026-05-31T10:59+09:00 | medium |
| 2 |  | #534/ally attack group | d-14 | 476B | 476 | city +30; enemy_flag +40; frontline_core +30 | critical | 都市破壊候補 | saturday_server_day 2026-05-30T11:00+09:00 - 2026-05-31T10:59+09:00 | medium |
| 3 |  | #534/ally attack group | d-14 | BgNa | 480 | city +30; enemy_flag +40; frontline_core +30 | critical | 都市破壊候補 | saturday_server_day 2026-05-30T11:00+09:00 - 2026-05-31T10:59+09:00 | medium |
| 4 |  | #534/ally attack group | d-10 | 476B | 476 | city +30; enemy_flag +40; frontline_adjacent +15 | high | 都市破壊候補 | saturday_server_day 2026-05-30T11:00+09:00 - 2026-05-31T10:59+09:00 | medium |
| 5 |  | #534/ally attack group | d-2 | 476K | 476 | city +30; enemy_flag +40; frontline_adjacent +15 | high | 都市破壊候補 | saturday_server_day 2026-05-30T11:00+09:00 - 2026-05-31T10:59+09:00 | medium |
| 6 |  | #534/ally attack group | d-6 | 476M | 476 | city +30; enemy_flag +40; frontline_adjacent +15 | high | 都市破壊候補 | saturday_server_day 2026-05-30T11:00+09:00 - 2026-05-31T10:59+09:00 | medium |
| 7 |  | #534/ally attack group | e-14 | 476d | 476 | city +30; enemy_flag +40; frontline_adjacent +15 | high | 都市破壊候補 | saturday_server_day 2026-05-30T11:00+09:00 - 2026-05-31T10:59+09:00 | medium |
| 8 |  | #534/ally attack group | e-18 | 476Z | 476 | city +30; enemy_flag +40; frontline_adjacent +15 | high | 都市破壊候補 | saturday_server_day 2026-05-30T11:00+09:00 - 2026-05-31T10:59+09:00 | medium |
| 9 |  | #534/ally attack group | e-18 | AAOA | 480 | city +30; enemy_flag +40; frontline_adjacent +15 | high | 都市破壊候補 | saturday_server_day 2026-05-30T11:00+09:00 - 2026-05-31T10:59+09:00 | medium |
| 10 |  | #534/ally attack group | e-6 | TkTk | 480 | city +30; enemy_flag +40; frontline_adjacent +15 | high | 都市破壊候補 | saturday_server_day 2026-05-30T11:00+09:00 - 2026-05-31T10:59+09:00 | medium |
| 11 |  | #534/ally attack group | e-8 | BgNa | 480 | city +30; enemy_flag +40; frontline_adjacent +15 | high | 都市破壊候補 | saturday_server_day 2026-05-30T11:00+09:00 - 2026-05-31T10:59+09:00 | medium |
| 12 |  | #534/ally attack group | d-10 | Lghs | 503 | city +30; enemy_flag +40; frontline_adjacent +15 | high | 都市破壊候補 | saturday_server_day 2026-05-30T11:00+09:00 - 2026-05-31T10:59+09:00 | medium |
| 13 |  | #534/ally attack group | e-8 | Lghs | 503 | city +30; enemy_flag +40; frontline_adjacent +15 | high | 都市破壊候補 | saturday_server_day 2026-05-30T11:00+09:00 - 2026-05-31T10:59+09:00 | medium |
| 14 |  | #534/ally attack group | d-10 | SHA | 503 | city +30; enemy_flag +40; frontline_adjacent +15 | high | 都市破壊候補 | saturday_server_day 2026-05-30T11:00+09:00 - 2026-05-31T10:59+09:00 | medium |
| 15 |  | #534/ally attack group | d-4 | nO9 | 476 | city +30; enemy_flag +40; frontline_adjacent +15 | high | 都市破壊候補 | saturday_server_day 2026-05-30T11:00+09:00 - 2026-05-31T10:59+09:00 | medium |
| 16 |  | #534/ally attack group | e-14 | SHA | 503 | city +30; enemy_flag +40; frontline_adjacent +15 | high | 都市破壊候補 | saturday_server_day 2026-05-30T11:00+09:00 - 2026-05-31T10:59+09:00 | medium |
| 17 |  | #534/ally attack group | e-4 | nO9 | 476 | city +30; enemy_flag +40; frontline_adjacent +15 | high | 都市破壊候補 | saturday_server_day 2026-05-30T11:00+09:00 - 2026-05-31T10:59+09:00 | medium |
| 18 |  | #534/ally attack group | e-6 | SHA | 503 | city +30; enemy_flag +40; frontline_adjacent +15 | high | 都市破壊候補 | saturday_server_day 2026-05-30T11:00+09:00 - 2026-05-31T10:59+09:00 | medium |
| 19 |  | #534/ally attack group | D-11 | 476A | 476 | fishery +10; enemy_flag +40; frontline_core +30 | high | 攻撃候補 |  | medium |
| 20 |  | #534/ally attack group | D-13 | 476A | 476 | fishery +10; enemy_flag +40; frontline_core +30 | high | 攻撃候補 |  | medium |
| 21 |  | #534/ally attack group | D-11 | 476C | 476 | fishery +10; enemy_flag +40; frontline_core +30 | high | 攻撃候補 |  | medium |
| 22 |  | #534/ally attack group | D-13 | 476B | 476 | fishery +10; enemy_flag +40; frontline_core +30 | high | 攻撃候補 |  | medium |
| 23 |  | #534/ally attack group | E-11 | SHA | 503 | fishery +10; enemy_flag +40; frontline_core +30 | high | 攻撃候補 |  | medium |
| 24 |  | #534/ally attack group | E-13 | 476C | 476 | fishery +10; enemy_flag +40; frontline_core +30 | high | 攻撃候補 |  | medium |
| 25 |  | #534/ally attack group | d-2 | GX99 | 503 | trade +20; enemy_flag +40; frontline_adjacent +15 | high | 攻撃候補 |  | medium |
| 26 |  | #534/ally attack group | d-20 | 476A | 476 | trade +20; enemy_flag +40; frontline_adjacent +15 | high | 攻撃候補 |  | medium |
| 27 |  | #534/ally attack group | e-20 | 476B | 476 | trade +20; enemy_flag +40; frontline_adjacent +15 | high | 攻撃候補 |  | medium |
| 28 |  | #534/ally attack group | e-2 | AAOA | 480 | trade +20; enemy_flag +40; frontline_adjacent +15 | high | 攻撃候補 |  | medium |
| 29 |  | #534/ally attack group | d-20 | 476X | 476 | trade +20; enemy_flag +40; frontline_adjacent +15 | high | 攻撃候補 |  | medium |
| 30 |  | #534/ally attack group | a-10 | 476M | 476 | city +30; enemy_flag +40 | high | 都市破壊候補 | saturday_server_day 2026-05-30T11:00+09:00 - 2026-05-31T10:59+09:00 | medium |

## 5. ???? Critical Risk

| rank | node_id | coord | current_alliance | owner_server | server_side | risk_score | risk_reason | recommended_action | confidence | memo_short |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | #480:d-12 | d-12 |  | none | destroyed | 160 | city +30; destroyed_flag +100; frontline_core +30 | 破壊済み確認 | high | 都市破壊ログ 2026/05/27 20:23:21 / #480 X:549 Y:349 Lv.3都市 / 攻撃側 #440[GcC] / 防衛側 #480… |
| 2 | #509:c-10 | c-10 |  | none | destroyed | 160 | city +30; destroyed_flag +100; frontline_core +30 | 破壊済み確認 | high | 都市破壊ログ 2026/05/28 12:22:48 / #509 X:449 Y:249 Lv.2都市 / 攻撃側 #503[Lghs] / 防衛側 #50… |
| 3 | #509:d-12 | d-12 |  | none | destroyed | 160 | city +30; destroyed_flag +100; frontline_core +30 | 破壊済み確認 | high | 都市破壊ログ 2026/05/27 20:04:04 / #509 X:549 Y:349 Lv.3都市 / 攻撃側 #476[476A] / 防衛側 #50… |
| 4 | #511:d-14 | d-14 |  | none | destroyed | 160 | city +30; destroyed_flag +100; frontline_core +30 | 破壊済み確認 | high | 都市破壊ログ 2026/05/28 12:35:01 / #511 X:649 Y:349 Lv.3都市 / 攻撃側 #480[WbW] / 防衛側 #511… |
| 5 | #534:c-10 | c-10 |  | none | destroyed | 160 | city +30; destroyed_flag +100; frontline_core +30 | 破壊済み確認 | high | 都市破壊ログ 2026/05/28 12:11:39 / #534 X:449 Y:249 Lv.2都市 / 攻撃側 #476[476C] / 防衛側 #53… |
| 6 | #534:c-8 | c-8 |  | none | destroyed | 160 | city +30; destroyed_flag +100; frontline_core +30 | 破壊済み確認 | high | 都市破壊ログ 2026/05/28 12:13:53 / #534 X:349 Y:249 Lv.2都市 / 攻撃側 #476[476C] / 防衛側 #53… |
| 7 | #534:d-12 | d-12 |  | none | destroyed | 160 | city +30; destroyed_flag +100; frontline_core +30 | 破壊済み確認 | high | 都市破壊ログ 2026/05/27 20:02:15 / #534 X:549 Y:349 Lv.3都市 / 攻撃側 #476[476B] / 防衛側 #53… |
| 8 | #534:d-14 | d-14 |  | none | destroyed | 160 | city +30; destroyed_flag +100; frontline_core +30 | 破壊済み確認 | high | 都市破壊ログ 2026/05/27 20:04:34 / #534 X:649 Y:349 Lv.3都市 / 攻撃側 #476[476B] / 防衛側 #53… |
| 9 | #480:d-10 | d-10 |  | none | destroyed | 145 | city +30; destroyed_flag +100; frontline_adjacent +15 | 破壊済み確認 | high | 都市破壊ログ 2026/05/27 20:12:18 / #480 X:449 Y:349 Lv.3都市 / 攻撃側 #440[GcC] / 防衛側 #480… |
| 10 | #509:d-10 | d-10 |  | none | destroyed | 145 | city +30; destroyed_flag +100; frontline_adjacent +15 | 破壊済み確認 | high | 都市破壊ログ 2026/05/27 20:17:55 / #509 X:449 Y:349 Lv.3都市 / 攻撃側 #476[476A] / 防衛側 #50… |
| 11 | #509:e-16 | e-16 |  | none | destroyed | 145 | city +30; destroyed_flag +100; frontline_adjacent +15 | 破壊済み確認 | high | 都市破壊ログ 2026/05/28 12:20:43 / #509 X:749 Y:449 Lv.2都市 / 攻撃側 #503[Lghs] / 防衛側 #50… |
| 12 | #511:e-14 | e-14 |  | none | destroyed | 145 | city +30; destroyed_flag +100; frontline_adjacent +15 | 破壊済み確認 | high | 都市破壊ログ 2026/05/28 12:25:14 / #511 X:649 Y:449 Lv.3都市 / 攻撃側 #480[BgNa] / 防衛側 #51… |
| 13 | #511:e-4 | e-4 |  | none | destroyed | 145 | city +30; destroyed_flag +100; frontline_adjacent +15 | 破壊済み確認 | high | 都市破壊ログ 2026/05/28 12:19:34 / #511 X:149 Y:449 Lv.1都市 / 攻撃側 #523[EDFS] / 防衛側 #51… |
| 14 | #511:e-8 | e-8 |  | none | destroyed | 145 | city +30; destroyed_flag +100; frontline_adjacent +15 | 破壊済み確認 | high | 都市破壊ログ 2026/05/27 20:23:12 / #511 X:349 Y:449 Lv.3都市 / 攻撃側 #523[WUG] / 防衛側 #511… |
| 15 | #476:g-2 | g-2 |  | none | destroyed | 130 | city +30; destroyed_flag +100 | 破壊済み確認 | high | 都市破壊ログ 2026/05/28 13:24:45 / #476 X:49 Y:649 Lv.1都市 / 攻撃側 #534[89M] / 防衛側 #476 … |
| 16 | #476:i-2 | i-2 |  | none | destroyed | 130 | city +30; destroyed_flag +100 | 破壊済み確認 | high | 都市破壊ログ 2026/05/27 20:02:38 / #476 X:49 Y:849 Lv.1都市 / 攻撃側 #534[nO9] / 防衛側 #476[… |
| 17 | #480:b-6 | b-6 |  | none | destroyed | 130 | city +30; destroyed_flag +100 | 破壊済み確認 | high | 都市破壊ログ 2026/05/28 04:37:22 / #480 X:249 Y:149 Lv.1都市 / 攻撃側 #440[GoDs] / 防衛側 #48… |
| 18 | #480:b-8 | b-8 |  | none | destroyed | 130 | city +30; destroyed_flag +100 | 破壊済み確認 | high | 都市破壊ログ 2026/05/28 12:01:52 / #480 X:349 Y:149 Lv.1都市 / 攻撃側 #440[GoDs] / 防衛側 #48… |
| 19 | #480:c-14 | c-14 |  | none | destroyed | 130 | city +30; destroyed_flag +100 | 破壊済み確認 | high | 都市破壊ログ 2026/05/28 12:20:01 / #480 X:649 Y:249 Lv.2都市 / 攻撃側 #509[SsQ] / 防衛側 #480… |
| 20 | #480:c-16 | c-16 |  | none | destroyed | 130 | city +30; destroyed_flag +100 | 破壊済み確認 | high | 都市破壊ログ 2026/05/28 12:17:50 / #480 X:749 Y:249 Lv.2都市 / 攻撃側 #509[SsQ] / 防衛側 #480… |
| 21 | #480:c-6 | c-6 |  | none | destroyed | 130 | city +30; destroyed_flag +100 | 破壊済み確認 | high | 都市破壊ログ 2026/05/28 12:11:30 / #480 X:249 Y:249 Lv.2都市 / 攻撃側 #440[BAJ] / 防衛側 #480… |
| 22 | #509:a-10 | a-10 |  | none | destroyed | 130 | city +30; destroyed_flag +100 | 破壊済み確認 | high | 都市破壊ログ 2026/05/28 00:52:11 / #509 X:449 Y:49 Lv.1都市 / 攻撃側 #476[ALj] / 防衛側 #509 … |
| 23 | #509:a-12 | a-12 |  | none | destroyed | 130 | city +30; destroyed_flag +100 | 破壊済み確認 | high | 都市破壊ログ 2026/05/28 03:09:40 / #509 X:549 Y:49 Lv.1都市 / 攻撃側 #476[476K] / 防衛側 #509… |
| 24 | #509:a-14 | a-14 |  | none | destroyed | 130 | city +30; destroyed_flag +100 | 破壊済み確認 | high | 都市破壊ログ 2026/05/28 03:04:40 / #509 X:649 Y:49 Lv.1都市 / 攻撃側 #476[476K] / 防衛側 #509… |
| 25 | #509:a-4 | a-4 |  | none | destroyed | 130 | city +30; destroyed_flag +100 | 破壊済み確認 | high | 都市破壊ログ 2026/05/28 00:17:43 / #509 X:149 Y:49 Lv.1都市 / 攻撃側 #476[476Z] / 防衛側 #509… |
| 26 | #509:a-6 | a-6 |  | none | destroyed | 130 | city +30; destroyed_flag +100 | 破壊済み確認 | high | 都市破壊ログ 2026/05/28 00:11:44 / #509 X:249 Y:49 Lv.1都市 / 攻撃側 #476[476Z] / 防衛側 #509… |
| 27 | #509:a-8 | a-8 |  | none | destroyed | 130 | city +30; destroyed_flag +100 | 破壊済み確認 | high | 都市破壊ログ 2026/05/28 00:35:38 / #509 X:349 Y:49 Lv.1都市 / 攻撃側 #476[ALj] / 防衛側 #509 … |
| 28 | #509:c-18 | c-18 |  | none | destroyed | 130 | city +30; destroyed_flag +100 | 破壊済み確認 | high | 都市破壊ログ 2026/05/28 12:19:52 / #509 X:849 Y:249 Lv.1都市 / 攻撃側 #480[RCON] / 防衛側 #50… |
| 29 | #509:f-16 | f-16 |  | none | destroyed | 130 | city +30; destroyed_flag +100 | 破壊済み確認 | high | 都市破壊ログ 2026/05/28 12:01:56 / #509 X:749 Y:549 Lv.2都市 / 攻撃側 #503[GX99] / 防衛側 #50… |
| 30 | #509:f-18 | f-18 |  | none | destroyed | 130 | city +30; destroyed_flag +100 | 破壊済み確認 | high | 都市破壊ログ 2026/05/28 12:02:34 / #509 X:849 Y:549 Lv.1都市 / 攻撃側 #503[Bye] / 防衛側 #509… |

## 6. ???????

- `confidence=medium`: 60?
- `from_node_id` ??? #534??????: 30?
- #534 Critical Risk ? `owner_server` ???: 0?
- ???? Critical Risk ? `owner_server` ???: 0?
- `unknown_owner_review_v2.csv`: 646??destroyed?????
- `type_uncertain_review_v2.csv`: 132?
- `safe_time_reference_review_v2.csv`: 1349?
- `city_destroy_enabled`: TRUE
- `recommended_action` ???:
- `攻撃候補`: 11?
- `破壊済み確認`: 34?
- `都市破壊候補`: 19?
- `防衛確認`: 9?
- `隣接確認`: 21?
- ??coord????????:
- `d-10`: 8? (enemy_invasion#4:from_coord, enemy_invasion#12:from_coord, enemy_invasion#14:from_coord, server_534_attack_target#4:to_coord, server_534_attack_target#12:to_coord, server_534_attack_target#14:to_coord, critical_global#9:coord, critical_global#10:coord)
- `d-14`: 7? (critical_534#4:coord, enemy_invasion#2:from_coord, enemy_invasion#3:from_coord, server_534_attack_target#2:to_coord, server_534_attack_target#3:to_coord, critical_global#4:coord, critical_global#8:coord)
- `d-12`: 6? (critical_534#3:coord, enemy_invasion#1:from_coord, server_534_attack_target#1:to_coord, critical_global#1:coord, critical_global#3:coord, critical_global#7:coord)
- `e-14`: 5? (enemy_invasion#7:from_coord, enemy_invasion#16:from_coord, server_534_attack_target#7:to_coord, server_534_attack_target#16:to_coord, critical_global#12:coord)
- `e-8`: 5? (enemy_invasion#11:from_coord, enemy_invasion#13:from_coord, server_534_attack_target#11:to_coord, server_534_attack_target#13:to_coord, critical_global#14:coord)
- `D-11`: 4? (enemy_invasion#19:from_coord, enemy_invasion#21:from_coord, server_534_attack_target#19:to_coord, server_534_attack_target#21:to_coord)
- `D-13`: 4? (enemy_invasion#20:from_coord, enemy_invasion#22:from_coord, server_534_attack_target#20:to_coord, server_534_attack_target#22:to_coord)
- `d-2`: 4? (enemy_invasion#5:from_coord, enemy_invasion#25:from_coord, server_534_attack_target#5:to_coord, server_534_attack_target#25:to_coord)
- `d-20`: 4? (enemy_invasion#26:from_coord, enemy_invasion#29:from_coord, server_534_attack_target#26:to_coord, server_534_attack_target#29:to_coord)
- `e-18`: 4? (enemy_invasion#8:from_coord, enemy_invasion#9:from_coord, server_534_attack_target#8:to_coord, server_534_attack_target#9:to_coord)
- `e-6`: 4? (enemy_invasion#10:from_coord, enemy_invasion#18:from_coord, server_534_attack_target#10:to_coord, server_534_attack_target#18:to_coord)
- `c-10`: 3? (critical_534#1:coord, critical_global#2:coord, critical_global#5:coord)
- `e-4`: 3? (enemy_invasion#17:from_coord, server_534_attack_target#17:to_coord, critical_global#13:coord)
- `E-11`: 2? (enemy_invasion#23:from_coord, server_534_attack_target#23:to_coord)
- `E-13`: 2? (enemy_invasion#24:from_coord, server_534_attack_target#24:to_coord)
- `a-10`: 2? (server_534_attack_target#30:to_coord, critical_global#22:coord)
- `c-8`: 2? (critical_534#2:coord, critical_global#6:coord)
- `d-4`: 2? (enemy_invasion#15:from_coord, server_534_attack_target#15:to_coord)
- `d-6`: 2? (enemy_invasion#6:from_coord, server_534_attack_target#6:to_coord)
- `e-2`: 2? (enemy_invasion#28:from_coord, server_534_attack_target#28:to_coord)
- `e-20`: 2? (enemy_invasion#27:from_coord, server_534_attack_target#27:to_coord)

### ??????????????

- ????????????
- ?????????????????????
- ????????????????????
- `from_node_id` ?????????????????????
- `confidence=medium` ????????????????




<!-- EDGE_CLASSIFICATION_BEGIN -->

## Edge候補の実行可能性分類

これは作戦命令ではなく，edge候補の分類である。各セクションは最大10件まで表示する。

## #534単独攻撃edge

| friendly_from_coord | friendly_from_alliance | friendly_from_server | enemy_to_coord | enemy_to_alliance | enemy_to_server | review_priority | recommended_action | human_check | confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D-9 | SHA | 534 | D-11 | 476C | 476 | high | 攻撃候補 | 発射元拠点確認; 協定確認 | medium |
| E-11 | SHA | 534 | D-11 | 476C | 476 | high | 攻撃候補 | 発射元拠点確認; 協定確認 | medium |
| C-13 | JDX | 534 | D-13 | 476B | 476 | high | 攻撃候補 | 発射元拠点確認; 協定確認 | medium |
| c-14 | JDX | 534 | D-13 | 476B | 476 | high | 攻撃候補 | 発射元拠点確認; 協定確認 | medium |
| E-11 | SHA | 534 | E-13 | 476C | 476 | high | 攻撃候補 | 発射元拠点確認; 協定確認 | medium |

## 味方連携攻撃edge

| friendly_from_coord | friendly_from_alliance | friendly_from_server | enemy_to_coord | enemy_to_alliance | enemy_to_server | review_priority | recommended_action | human_check | confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E-11 | FHX | 509 | D-11 | 476A | 476 | high | 味方連携確認 | 発射元拠点確認; 味方連携確認; 協定確認 | medium |
| E-13 | FHX | 509 | D-13 | 476A | 476 | high | 味方連携確認 | 発射元拠点確認; 味方連携確認; 協定確認 | medium |
| d-14 | FHX | 509 | D-13 | 476A | 476 | high | 味方連携確認 | 発射元拠点確認; 味方連携確認; 協定確認 | medium |

## 地図確認が必要な攻撃候補

| friendly_from_coord | friendly_from_alliance | friendly_from_server | enemy_to_coord | enemy_to_alliance | enemy_to_server | review_priority | recommended_action | human_check | confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  | d-12 | 476B | 476 | critical | 地図確認 | 発射元拠点確認; 地図確認 | medium |
|  |  |  | d-14 | 476B | 476 | critical | 地図確認 | 発射元拠点確認; 地図確認 | medium |
|  |  |  | d-10 | 476B | 476 | high | 地図確認 | 発射元拠点確認; 地図確認 | medium |
|  |  |  | d-2 | 476K | 476 | high | 地図確認 | 発射元拠点確認; 地図確認 | medium |
|  |  |  | d-6 | 476M | 476 | high | 地図確認 | 発射元拠点確認; 地図確認 | medium |
|  |  |  | e-14 | 476d | 476 | high | 地図確認 | 発射元拠点確認; 地図確認 | medium |
|  |  |  | e-18 | 476Z | 476 | high | 地図確認 | 発射元拠点確認; 地図確認 | medium |
|  |  |  | e-18 | AAOA | 480 | high | 地図確認 | 発射元拠点確認; 地図確認 | medium |
|  |  |  | d-10 | Lghs | 503 | high | 地図確認 | 発射元拠点確認; 地図確認 | medium |
|  |  |  | e-8 | Lghs | 503 | high | 地図確認 | 発射元拠点確認; 地図確認 | medium |

## #534防衛edge

| enemy_from_coord | enemy_from_alliance | enemy_from_server | friendly_to_coord | friendly_to_alliance | friendly_to_server | review_priority | recommended_action | human_check | confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D-11 | 476C | 476 | D-9 | SHA | 534 | high | 防衛確認 | 防衛ライン確認 | medium |
| D-11 | 476C | 476 | E-11 | SHA | 534 | high | 防衛確認 | 防衛ライン確認 | medium |
| D-13 | 476B | 476 | C-13 | JDX | 534 | high | 防衛確認 | 防衛ライン確認 | medium |
| D-13 | 476B | 476 | c-14 | JDX | 534 | high | 防衛確認 | 防衛ライン確認 | medium |
| E-13 | 476C | 476 | E-11 | SHA | 534 | high | 防衛確認 | 防衛ライン確認 | medium |

## 味方防衛edge

| enemy_from_coord | enemy_from_alliance | enemy_from_server | friendly_to_coord | friendly_to_alliance | friendly_to_server | review_priority | recommended_action | human_check | confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D-11 | 476A | 476 | E-11 | FHX | 509 | high | 防衛確認 | 味方連携確認; 防衛ライン確認 | medium |
| D-13 | 476A | 476 | E-13 | FHX | 509 | high | 防衛確認 | 味方連携確認; 防衛ライン確認 | medium |
| D-13 | 476A | 476 | d-14 | FHX | 509 | high | 防衛確認 | 味方連携確認; 防衛ライン確認 | medium |
| D-17 | AAOA | 480 | D-15 | SsQ | 509 | high | 隣接確認 | 味方連携確認; 防衛ライン確認 | medium |
| E-5 | RCON | 480 | E-7 | BAJ | 440 | high | 隣接確認 | 味方連携確認; 防衛ライン確認 | medium |

## 地図確認が必要な敵侵攻候補

| enemy_from_coord | enemy_from_alliance | enemy_from_server | friendly_to_coord | friendly_to_alliance | friendly_to_server | review_priority | recommended_action | human_check | confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| d-12 | 476B | 476 |  |  |  | critical | 地図確認 | 防衛先確認; 地図確認 | medium |
| d-14 | 476B | 476 |  |  |  | critical | 地図確認 | 防衛先確認; 地図確認 | medium |
| d-10 | 476B | 476 |  |  |  | high | 地図確認 | 防衛先確認; 地図確認 | medium |
| d-2 | 476K | 476 |  |  |  | high | 地図確認 | 防衛先確認; 地図確認 | medium |
| d-6 | 476M | 476 |  |  |  | high | 地図確認 | 防衛先確認; 地図確認 | medium |
| e-14 | 476d | 476 |  |  |  | high | 地図確認 | 防衛先確認; 地図確認 | medium |
| e-18 | 476Z | 476 |  |  |  | high | 地図確認 | 防衛先確認; 地図確認 | medium |
| e-18 | AAOA | 480 |  |  |  | high | 地図確認 | 防衛先確認; 地図確認 | medium |
| d-10 | Lghs | 503 |  |  |  | high | 地図確認 | 防衛先確認; 地図確認 | medium |
| e-8 | Lghs | 503 |  |  |  | high | 地図確認 | 防衛先確認; 地図確認 | medium |

<!-- EDGE_CLASSIFICATION_END -->
