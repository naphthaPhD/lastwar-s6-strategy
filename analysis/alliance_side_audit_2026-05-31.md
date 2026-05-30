# 連盟所属・敵味方判定監査 2026-05-31

これは作戦命令ではなく，R4/R5ブリーフィングに使われた連盟判定の監査表である。
`manual_server_override` と `manual_note` はCSV側で人間が追記するための空欄であり，自動適用しない。

## 1. Summary

- alliance_side_audit rows: 108
- risk_flag rows: 77
- unknown resolved_server rows: 70
- appears_as_enemy but maybe self/ally rows: 0
- side_check_required rows: 77

## 2. 最優先確認

| alliance | resolved_server | server_side | appearance_count | appears_as_enemy | appears_as_self_or_ally | appears_in_areas | risk_flag | review_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| JDX | 534 | self | 30 | FALSE | TRUE | #534; 中央 |  | ok |
| SHA | 534 | self | 46 | FALSE | TRUE | #509; #534; 中央 |  | ok |
| 4tH | 534 | self | 44 | FALSE | TRUE | #534; 中央 |  | ok |
| nO9 | 534 | self | 40 | FALSE | TRUE | #476; #480; #523; #534; 中央 |  | ok |

## 3. risk_flagあり

| alliance | resolved_server | server_side | appearance_count | appears_as_enemy | appears_as_self_or_ally | appears_in_areas | risk_flag | review_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 476A | 476 | enemy | 82 | TRUE | FALSE | #440; #476; #503; #509; #523; #534; 中央 | enemy_in_534_area | needs_review |
| 476B | 476 | enemy | 60 | TRUE | FALSE | #440; #476; #509; #511; #534; 中央 | enemy_in_534_area | needs_review |
| 476C | 476 | enemy | 62 | TRUE | FALSE | #476; #534; 中央 | enemy_in_534_area | needs_review |
| RCON | 480 | enemy | 45 | TRUE | FALSE | #480; #503; #509; #534; 中央 | enemy_in_534_area | needs_review |
| 476X | 476 | enemy | 54 | TRUE | FALSE | #476; #511; #523; #534; 中央 | enemy_in_534_area | needs_review |
| 59U | unknown | unknown | 1 | FALSE | FALSE | #534 | unknown_resolved_server | needs_review |
| 5DU | unknown | unknown | 9 | FALSE | FALSE | #511; #523 | unknown_resolved_server | needs_review |
| ALi | unknown | unknown | 1 | FALSE | FALSE | #523 | unknown_resolved_server | needs_review |
| ALj | unknown | unknown | 14 | FALSE | FALSE | #476; #511; 中央 | unknown_resolved_server | needs_review |
| ANH2 | unknown | unknown | 2 | FALSE | FALSE | #440 | unknown_resolved_server | needs_review |
| AoW | unknown | unknown | 11 | FALSE | FALSE | #509 | unknown_resolved_server | needs_review |
| BHE | unknown | unknown | 17 | FALSE | FALSE | #509; 中央 | unknown_resolved_server | needs_review |
| Bye | unknown | unknown | 14 | FALSE | FALSE | #480; #503; 中央 | unknown_resolved_server | needs_review |
| CDf8 | unknown | unknown | 15 | FALSE | FALSE | #480; #511; 中央 | unknown_resolved_server | needs_review |
| COZy | unknown | unknown | 6 | FALSE | FALSE | #480; #503; 中央 | unknown_resolved_server | needs_review |
| CROW | unknown | unknown | 5 | FALSE | FALSE | #534 | unknown_resolved_server | needs_review |
| DOLU | unknown | unknown | 11 | FALSE | FALSE | #440 | unknown_resolved_server | needs_review |
| Dao | unknown | unknown | 14 | FALSE | FALSE | #509; #534 | unknown_resolved_server | needs_review |
| EDFS | unknown | unknown | 16 | FALSE | FALSE | #511; #523; 中央 | unknown_resolved_server | needs_review |
| FarM | unknown | unknown | 10 | FALSE | FALSE | #503 | unknown_resolved_server | needs_review |
| GcC | unknown | unknown | 17 | FALSE | FALSE | #440; #476; #480; #503; #523; 中央 | unknown_resolved_server | needs_review |
| IMP | unknown | unknown | 3 | FALSE | FALSE | #480; 中央 | unknown_resolved_server | needs_review |
| IMp | unknown | unknown | 10 | FALSE | FALSE | #440; #511 | unknown_resolved_server | needs_review |
| IXM | unknown | unknown | 2 | FALSE | FALSE | #476 | unknown_resolved_server | needs_review |
| JL0 | unknown | unknown | 7 | FALSE | FALSE | #511; 中央 | unknown_resolved_server | needs_review |
| JL2 | unknown | unknown | 15 | FALSE | FALSE | #511; 中央 | unknown_resolved_server | needs_review |
| JLO | unknown | unknown | 12 | FALSE | FALSE | #511; #523; 中央 | unknown_resolved_server | needs_review |
| JlZ | unknown | unknown | 1 | FALSE | FALSE | 中央 | unknown_resolved_server | needs_review |
| K4TR | unknown | unknown | 15 | FALSE | FALSE | #511; #523; 中央 | unknown_resolved_server | needs_review |
| KOCH | unknown | unknown | 3 | FALSE | FALSE | #509 | unknown_resolved_server | needs_review |
| Kfk | unknown | unknown | 5 | FALSE | FALSE | #476; 中央 | unknown_resolved_server | needs_review |
| Lghs | 503 | enemy | 44 | TRUE | FALSE | #476; #480; #503; #509; #523; #534; 中央 | enemy_in_534_area | needs_review |
| MOE | unknown | unknown | 7 | FALSE | FALSE | #534; 中央 | unknown_resolved_server | needs_review |
| MOn | unknown | unknown | 15 | FALSE | FALSE | #509; 中央 | unknown_resolved_server | needs_review |
| MtG | unknown | unknown | 11 | FALSE | FALSE | #480; 中央 | unknown_resolved_server | needs_review |
| NBNH | unknown | unknown | 16 | FALSE | FALSE | #511; #523; 中央 | unknown_resolved_server | needs_review |
| OOEf | unknown | unknown | 2 | FALSE | FALSE | #511 | unknown_resolved_server | needs_review |
| OTT | unknown | unknown | 10 | FALSE | FALSE | #509 | unknown_resolved_server | needs_review |
| OWM | unknown | unknown | 12 | FALSE | FALSE | #509 | unknown_resolved_server | needs_review |
| PmP | unknown | unknown | 12 | FALSE | FALSE | #480; 中央 | unknown_resolved_server | needs_review |
| R6q | unknown | unknown | 13 | FALSE | FALSE | #476; #523 | unknown_resolved_server | needs_review |
| RGWC | unknown | unknown | 16 | FALSE | FALSE | #534 | unknown_resolved_server | needs_review |
| RING | unknown | unknown | 4 | FALSE | FALSE | #503 | unknown_resolved_server | needs_review |
| Ryu1 | unknown | unknown | 5 | FALSE | FALSE | #534 | unknown_resolved_server | needs_review |
| SHA0 | unknown | unknown | 6 | FALSE | FALSE | #534; 中央 | unknown_resolved_server | needs_review |
| SVh | unknown | unknown | 2 | FALSE | FALSE | #511 | unknown_resolved_server | needs_review |
| SVo | unknown | unknown | 1 | FALSE | FALSE | #511 | unknown_resolved_server | needs_review |
| Skh | unknown | unknown | 5 | FALSE | FALSE | #534 | unknown_resolved_server | needs_review |
| Stj | unknown | unknown | 12 | FALSE | FALSE | #503; #509; #511; 中央 | unknown_resolved_server | needs_review |
| TIKW | unknown | unknown | 16 | FALSE | FALSE | #480; #503; #509; 中央 | unknown_resolved_server | needs_review |
| TRh | unknown | unknown | 2 | FALSE | FALSE | #511 | unknown_resolved_server | needs_review |
| TaW | unknown | unknown | 16 | FALSE | FALSE | #440; #480; 中央 | unknown_resolved_server | needs_review |
| TrX | unknown | unknown | 15 | FALSE | FALSE | #440; #511; 中央 | unknown_resolved_server | needs_review |
| Trh | unknown | unknown | 5 | FALSE | FALSE | #534 | unknown_resolved_server | needs_review |
| UMN | unknown | unknown | 10 | FALSE | FALSE | #503; #509; 中央 | unknown_resolved_server | needs_review |
| UrE | unknown | unknown | 3 | FALSE | FALSE | #523 | unknown_resolved_server | needs_review |
| WUG | unknown | unknown | 18 | FALSE | FALSE | #511; #523; 中央 | unknown_resolved_server | needs_review |
| WbW | unknown | unknown | 18 | FALSE | FALSE | #480; #511; 中央 | unknown_resolved_server | needs_review |
| WoW3 | unknown | unknown | 7 | FALSE | FALSE | #440 | unknown_resolved_server | needs_review |
| YDR | unknown | unknown | 3 | FALSE | FALSE | #503 | unknown_resolved_server | needs_review |
| aTA | unknown | unknown | 4 | FALSE | FALSE | #440 | unknown_resolved_server | needs_review |
| eXt | unknown | unknown | 8 | FALSE | FALSE | #509 | unknown_resolved_server | needs_review |
| f4j | unknown | unknown | 16 | FALSE | FALSE | #534 | unknown_resolved_server | needs_review |
| fIrE | unknown | unknown | 16 | FALSE | FALSE | #476; #511; #523; 中央 | unknown_resolved_server | needs_review |
| fzn | 503 | enemy | 38 | TRUE | FALSE | #503; #509; #534; 中央 | enemy_in_534_area | needs_review |
| hMt | unknown | unknown | 3 | FALSE | FALSE | #503 | unknown_resolved_server | needs_review |
| hOe | unknown | unknown | 4 | FALSE | FALSE | #480; #503 | unknown_resolved_server | needs_review |
| kOi | unknown | unknown | 12 | FALSE | FALSE | #534 | unknown_resolved_server | needs_review |
| moca | unknown | unknown | 2 | FALSE | FALSE | #534 | unknown_resolved_server | needs_review |
| noI | unknown | unknown | 14 | FALSE | FALSE | #509; #534 | unknown_resolved_server | needs_review |
| nv8 | unknown | unknown | 2 | FALSE | FALSE | #440; #511 | unknown_resolved_server | needs_review |
| one | unknown | unknown | 18 | FALSE | FALSE | #480; #503; #509; #511; 中央 | unknown_resolved_server | needs_review |
| sbM | unknown | unknown | 13 | FALSE | FALSE | #511 | unknown_resolved_server | needs_review |
| sg3 | unknown | unknown | 5 | FALSE | FALSE | #534 | unknown_resolved_server | needs_review |
| u3o | unknown | unknown | 13 | FALSE | FALSE | #511; #523; 中央 | unknown_resolved_server | needs_review |
| w6F | unknown | unknown | 6 | FALSE | FALSE | #534 | unknown_resolved_server | needs_review |
| xjR | unknown | unknown | 12 | FALSE | FALSE | #503; #509; 中央 | unknown_resolved_server | needs_review |

## 4. unknown resolved_server

| alliance | appearance_count | appears_in_briefing | appears_in_areas | sample_nodes | risk_flag |
| --- | --- | --- | --- | --- | --- |
| 59U | 1 | FALSE | #534 | #534:H-19 | unknown_resolved_server |
| 5DU | 9 | FALSE | #511; #523 | #511:D-3; #523:b-12; #523:c-14; #523:C-21; #523:F-19; #523:C-17; #523:C-19; #523:A-17 | unknown_resolved_server |
| ALi | 1 | FALSE | #523 | #523:J-21 | unknown_resolved_server |
| ALj | 14 | FALSE | #476; #511; 中央 | #476:G-15; #476:G-17; #476:h-18; #476:F-17; #476:g-20; #476:H-21; #511:I-1; #511:H-1 | unknown_resolved_server |
| ANH2 | 2 | FALSE | #440 | #440:B-19; #440:D-19 | unknown_resolved_server |
| AoW | 11 | FALSE | #509 | #509:b-14; #509:C-15; #509:K-9; #509:a-18; #509:B-19; #509:I-9; #509:b-18; #509:i-10 | unknown_resolved_server |
| BHE | 17 | FALSE | #509; 中央 | #509:h-4; #509:h-6; #509:F-3; #509:I-11; #509:h-8; #509:f-2; #509:f-6; #509:g-4 | unknown_resolved_server |
| Bye | 14 | FALSE | #480; #503; 中央 | #480:K-11; #503:A-5; #503:b-6; #503:b-8; #503:C-5; #503:B-5; #503:B-7; #503:B-9 | unknown_resolved_server |
| CDf8 | 15 | FALSE | #480; #511; 中央 | #480:d-16; #480:e-16; #480:D-5; #480:f-14; #480:B-17; #480:B-19; #480:G-15; #511:J-19 | unknown_resolved_server |
| COZy | 6 | FALSE | #480; #503; 中央 | #480:K-9; #480:j-20; #480:E-21; #503:A-9; #503:a-20; 中央:中央-10-17 | unknown_resolved_server |
| CROW | 5 | FALSE | #534 | #534:J-3; #534:j-4; #534:J-5; #534:j-6; #534:K-5 | unknown_resolved_server |
| DOLU | 11 | FALSE | #440 | #440:C-5; #440:C-7; #440:C-9; #440:b-12; #440:b-14; #440:C-11; #440:D-15; #440:C-13 | unknown_resolved_server |
| Dao | 14 | FALSE | #509; #534 | #509:H-1; #534:j-16; #534:i-6; #534:h-12; #534:i-10; #534:I-11; #534:I-13; #534:i-8 | unknown_resolved_server |
| EDFS | 16 | FALSE | #511; #523; 中央 | #511:F-3; #511:G-3; #523:C-5; #523:D-5; #523:G-19; #523:B-13; #523:B-9; #523:H-19 | unknown_resolved_server |
| FarM | 10 | FALSE | #503 | #503:h-8; #503:I-7; #503:I-9; #503:i-8; #503:J-9; #503:J-7; #503:K-5; #503:K-7 | unknown_resolved_server |
| GcC | 17 | FALSE | #440; #476; #480; #503; #523; 中央 | #440:e-14; #440:f-14; #440:j-10; #440:g-10; #476:j-14; #480:C-15; #480:a-10; #480:B-11 | unknown_resolved_server |
| IMP | 3 | FALSE | #480; 中央 | #480:A-11; #480:B-9; 中央:中央-17-16 | unknown_resolved_server |
| IMp | 10 | FALSE | #440; #511 | #440:I-15; #440:f-4; #440:e-4; #440:D-3; #440:E-1; #440:J-7; #440:G-1; #440:c-10 | unknown_resolved_server |
| IXM | 2 | FALSE | #476 | #476:K-13; #476:K-9 | unknown_resolved_server |
| JL0 | 7 | FALSE | #511; 中央 | #511:K-11; #511:c-12; #511:f-8; 中央:中央-17-8; 中央:中央-15-10; 中央:中央-18-10; 中央:中央-19-9 | unknown_resolved_server |
| JL2 | 15 | FALSE | #511; 中央 | #511:I-5; #511:F-5; #511:j-8; #511:G-5; #511:H-3; #511:j-6; #511:h-4; #511:i-6 | unknown_resolved_server |
| JLO | 12 | FALSE | #511; #523; 中央 | #511:D-13; #511:H-7; #511:H-9; #511:g-8; #511:c-8; #511:h-8; #523:J-19; #523:I-19 | unknown_resolved_server |
| JlZ | 1 | FALSE | 中央 | 中央:中央-20-8 | unknown_resolved_server |
| K4TR | 15 | FALSE | #511; #523; 中央 | #511:A-7; #511:B-5; #511:C-3; #511:A-11; #511:A-9; #523:A-11; #523:b-6; #523:E-19 | unknown_resolved_server |
| KOCH | 3 | FALSE | #509 | #509:h-2; #509:H-3; #509:K-1 | unknown_resolved_server |
| Kfk | 5 | FALSE | #476; 中央 | #476:I-19; #476:h-20; #476:I-21; 中央:中央-5-1; 中央:中央-5-2 | unknown_resolved_server |
| MOE | 7 | FALSE | #534; 中央 | #534:B-15; #534:b-16; #534:C-17; #534:D-17; 中央:中央-11-5; 中央:中央-14-5; 中央:中央-14-6 | unknown_resolved_server |
| MOn | 15 | FALSE | #509; 中央 | #509:F-15; #509:h-12; #509:h-14; #509:I-13; #509:h-10; #509:A-13; #509:g-10; #509:G-11 | unknown_resolved_server |
| MtG | 11 | FALSE | #480; 中央 | #480:K-15; #480:h-4; #480:I-1; #480:h-2; #480:F-1; #480:G-1; #480:j-16; 中央:中央-15-16 | unknown_resolved_server |
| NBNH | 16 | FALSE | #511; #523; 中央 | #511:I-3; #511:I-9; #523:g-18; #523:g-16; #523:G-17; #523:c-20; #523:I-17; #523:e-14 | unknown_resolved_server |
| OOEf | 2 | FALSE | #511 | #511:J-9; #511:K-9 | unknown_resolved_server |
| OTT | 10 | FALSE | #509 | #509:K-11; #509:K-13; #509:K-15; #509:G-17; #509:j-18; #509:i-18; #509:j-14; #509:j-16 | unknown_resolved_server |
| OWM | 12 | FALSE | #509 | #509:B-15; #509:b-16; #509:G-15; #509:i-6; #509:i-8; #509:J-3; #509:J-5; #509:j-6 | unknown_resolved_server |
| PmP | 12 | FALSE | #480; 中央 | #480:C-5; #480:D-1; #480:E-1; #480:e-4; #480:d-4; #480:D-3; 中央:中央-12-17; 中央:中央-17-19 | unknown_resolved_server |
| R6q | 13 | FALSE | #476; #523 | #476:C-15; #476:E-15; #476:D-21; #476:c-20; #476:C-17; #476:D-15; #476:D-17; #476:C-19 | unknown_resolved_server |
| RGWC | 16 | FALSE | #534 | #534:d-6; #534:F-7; #534:G-7; #534:H-5; #534:H-7; #534:e-8; #534:D-3; #534:h-10 | unknown_resolved_server |
| RING | 4 | FALSE | #503 | #503:J-11; #503:J-15; #503:J-13; #503:K-9 | unknown_resolved_server |
| Ryu1 | 5 | FALSE | #534 | #534:g-2; #534:H-1; #534:h-2; #534:H-3; #534:h-4 | unknown_resolved_server |
| SHA0 | 6 | FALSE | #534; 中央 | #534:A-9; #534:B-9; #534:b-8; 中央:中央-11-4; 中央:中央-12-4; 中央:中央-13-4 | unknown_resolved_server |
| SVh | 2 | FALSE | #511 | #511:C-7; #511:C-5 | unknown_resolved_server |
| SVo | 1 | FALSE | #511 | #511:K-17 | unknown_resolved_server |
| Skh | 5 | FALSE | #534 | #534:b-2; #534:B-1; #534:C-1; #534:D-1; #534:E-1 | unknown_resolved_server |
| Stj | 12 | FALSE | #503; #509; #511; 中央 | #503:f-14; #503:f-2; #503:B-19; #503:E-15; #503:I-1; #509:I-15; #509:I-17; #509:I-21 | unknown_resolved_server |
| TIKW | 16 | FALSE | #480; #503; #509; 中央 | #480:H-7; #480:C-19; #480:E-17; #480:F-17; #503:E-17; #503:i-2; #503:F-5; #503:b-16 | unknown_resolved_server |
| TRh | 2 | FALSE | #511 | #511:F-21; #511:E-21 | unknown_resolved_server |
| TaW | 16 | FALSE | #440; #480; 中央 | #440:d-16; #440:i-16; #440:E-17; #440:j-20; #440:F-13; #440:J-17; #440:J-13; #440:e-16 | unknown_resolved_server |
| TrX | 15 | FALSE | #440; #511; 中央 | #440:G-17; #440:F-5; #440:G-5; #440:h-18; #440:g-20; #440:D-1; #440:F-3; #440:H-17 | unknown_resolved_server |
| Trh | 5 | FALSE | #534 | #534:C-15; #534:b-14; #534:B-11; #534:A-11; #534:D-15 | unknown_resolved_server |
| UMN | 10 | FALSE | #503; #509; 中央 | #503:K-1; #503:I-13; #503:H-13; #503:j-2; #503:J-3; #509:H-19; #509:I-19; #509:K-21 | unknown_resolved_server |
| UrE | 3 | FALSE | #523 | #523:H-3; #523:K-1; #523:I-1 | unknown_resolved_server |
| WUG | 18 | FALSE | #511; #523; 中央 | #511:D-9; #511:D-7; #511:G-7; #523:h-12; #523:h-18; #523:g-12; #523:g-14; 中央:中央-12-5 | unknown_resolved_server |
| WbW | 18 | FALSE | #480; #511; 中央 | #480:D-13; #480:D-7; #480:C-7; #480:b-14; #480:d-6; #480:d-8; #480:h-14; #480:i-14 | unknown_resolved_server |
| WoW3 | 7 | FALSE | #440 | #440:b-10; #440:A-5; #440:A-7; #440:B-7; #440:A-9; #440:B-9; #440:A-3 | unknown_resolved_server |
| YDR | 3 | FALSE | #503 | #503:F-21; #503:H-21; #503:G-19 | unknown_resolved_server |
| aTA | 4 | FALSE | #440 | #440:H-7; #440:H-5; #440:h-4; #440:I-5 | unknown_resolved_server |
| eXt | 8 | FALSE | #509 | #509:D-1; #509:B-5; #509:E-1; #509:F-1; #509:f-4; #509:G-1; #509:g-2; #509:G-3 | unknown_resolved_server |
| f4j | 16 | FALSE | #534 | #534:i-12; #534:K-11; #534:i-14; #534:I-15; #534:i-16; #534:I-17; #534:j-10; #534:J-11 | unknown_resolved_server |
| fIrE | 16 | FALSE | #476; #511; #523; 中央 | #476:A-19; #511:E-7; #511:F-7; #511:c-2; #523:h-8; #523:i-10; #523:I-9; #523:g-8 | unknown_resolved_server |
| hMt | 3 | FALSE | #503 | #503:K-17; #503:I-17; #503:J-17 | unknown_resolved_server |
| hOe | 4 | FALSE | #480; #503 | #480:H-13; #480:I-13; #480:J-13; #503:A-13 | unknown_resolved_server |
| kOi | 12 | FALSE | #534 | #534:f-2; #534:E-5; #534:d-2; #534:e-2; #534:E-3; #534:F-1; #534:F-3; #534:f-4 | unknown_resolved_server |
| moca | 2 | FALSE | #534 | #534:K-1; #534:K-3 | unknown_resolved_server |
| noI | 14 | FALSE | #509; #534 | #509:I-1; #509:J-1; #534:F-21; #534:g-18; #534:G-19; #534:G-21; #534:h-16; #534:h-18 | unknown_resolved_server |
| nv8 | 2 | FALSE | #440; #511 | #440:A-1; #511:B-21 | unknown_resolved_server |
| one | 18 | FALSE | #480; #503; #509; #511; 中央 | #480:I-9; #480:H-9; #480:J-5; #480:J-9; #480:H-5; #503:b-12; #503:d-12; #503:e-2 | unknown_resolved_server |
| sbM | 13 | FALSE | #511 | #511:C-11; #511:e-16; #511:G-15; #511:F-15; #511:E-17; #511:F-17; #511:G-19; #511:d-16 | unknown_resolved_server |
| sg3 | 5 | FALSE | #534 | #534:c-18; #534:d-18; #534:D-19; #534:E-15; #534:E-17 | unknown_resolved_server |
| u3o | 13 | FALSE | #511; #523; 中央 | #511:B-7; #511:A-5; #511:B-3; #511:A-3; #523:f-4; #523:f-6; #523:E-17; #523:B-11 | unknown_resolved_server |
| w6F | 6 | FALSE | #534 | #534:b-20; #534:B-21; #534:B-19; #534:A-15; #534:A-17; #534:B-17 | unknown_resolved_server |
| xjR | 12 | FALSE | #503; #509; 中央 | #503:H-3; #503:i-12; #503:i-10; #503:I-11; #503:g-12; #509:H-21; #509:I-3; #509:J-15 | unknown_resolved_server |

## 5. 人間レビュー手順

1. `SHA` と `nO9` の所属サーバを最初に確認する。
2. 味方候補が `appears_as_enemy=TRUE` になっている行は，攻撃候補として扱わない。
3. 修正が必要な場合は，まず `alliance_side_audit_v2.csv` の `manual_server_override` と `manual_note` に記入する。
4. 自動適用はまだ行わず，`alliance_directory.csv` への反映は人間承認後に行う。

## 6. Files referenced

- `analysis/r4_r5_briefing_2026-05-31.md`
- `sample_output/sheet_migration/node_current_v2.csv`
- `sample_output/sheet_migration/alliance_directory.csv`
- `sample_output/sheet_migration/current_enemy_nodes_v2.csv`
- `sample_output/sheet_migration/current_friendly_nodes_v2.csv`
- `sample_output/sheet_migration/server_534_attack_edges_self_v2.csv`
- `sample_output/sheet_migration/server_534_attack_edges_ally_v2.csv`
- `sample_output/sheet_migration/enemy_invasion_edges_self_defense_v2.csv`
- `sample_output/sheet_migration/enemy_invasion_edges_ally_defense_v2.csv`
