# Handoff summary

## Date

2026-05-27

## Context

The pact situation changed: #503-side alliances can now attack #534. The user asked for a worst-case forecast of how #534 holdings could change, and then asked for an integrated map based on `取得入力マップ`.

This handoff uses the live Google Sheet and the previous #476B/#476C route analysis. Two prediction/support tabs were added to the spreadsheet.

## Updated files

- `analysis/2026-05-27_503_476_worst_case_invasion_forecast.md`
- `analysis/2026-05-27_integrated_invasion_map_update.md`
- `analysis/latest_handoff.md`

## Updated Google Sheet

- Spreadsheet ID: `12uNW9XphH2zSX4h5BzjSd-OON9r5AckAuNCwQTbY79g`
- Added tab: `侵攻予測_20260527_最悪`
- Added tab: `侵攻予測_20260527_統合`
- Integrated map range: `侵攻予測_20260527_統合!A12:BT92`
- Integrated map formula: `={'取得入力マップ'!A6:BT45;'取得入力マップ'!A49:BT89}`
- Pact input range for purple display: `侵攻予測_20260527_統合!O2:Y9`

## Key findings

1. With #503 able to participate, #534 should treat #503 as a right-side convergence threat, not as secondary background pressure.
2. The most dangerous pattern is #476C pressing upward/interior from `A-7 / B-7 / C-7 / C-9`, while #476B pushes rightward from `C-11 / D-7`.
3. `D-11` is the highest-priority denial point. If it falls, `c-12(JDX)` and `d-12(JDX)` become a two-sided JDX problem.
4. `D-9` is the second denial point because it creates the right-turn route toward `d-10(SHA)` and the later #503-side corridor.
5. `E-7` is the third denial point because it lets the attack move beyond the D-line into deeper SHA/4tH territory.
6. The integrated map now displays alliance names from `取得入力マップ` without the four-area boundary headers, so #534/#509/#476/中央 can be scanned as one map.
7. Current invadable/potentially invadable alliance classes are: existing #534 invaders `476B`, `476C`; #476-side boundary alliances `476K`, `476H`, `476A`, `476C`, `IXM`, `476d`, `476B`; and manually entered pact partners in `O2:Y9`.

## Current risks

1. #534 may over-defend visible cities and lose `D-11 / D-9 / E-7`.
2. If `D-11` and `D-9` both fall, the C-line stops being the real front; D/E become the new contested belt.
3. #503 can amplify a rightward route once a shared/pact-enabled connection is usable.
4. City destruction remains less reversible than fishing-ground exchange; `c-12`, `c-10`, `c-8`, and `b-10` should be watched but not at the cost of losing the denial points.
5. Pact partners are not yet available as structured data in the sheet, so the purple class depends on manual entry into `O2:Y9`.

## Recommended next actions

1. Assign one watch group to #476C upper/interior pressure.
2. Assign one watch group to #476B/#503 right-side pressure.
3. Make `D-11`, `D-9`, and `E-7` the map callouts for immediate denial.
4. Use `侵攻予測_20260527_最悪` for the route forecast and `侵攻予測_20260527_統合` for current invadable alliance monitoring.
5. Before the next 2026-05-27 response window, enter confirmed pact partners of the red/orange alliances into `侵攻予測_20260527_統合!O2:Y9`.
6. Confirm in game whether #503 can use pact territory as attack adjacency immediately, and whether empty-owner city rows can be destroyed.

## Questions for ChatGPT

1. Is `D-11 > D-9 > E-7` the correct denial priority under the new pact situation?
2. Should #534 intentionally abandon some city defense to preserve D/E-line denial?
3. What should the short R4/R5 instruction be for the 23:00 JST window?
4. Does the integrated map's three-class filter cover today's command needs, or should pact partners be split by source alliance?
5. The user wrote `478エリア`; current implementation treats this as `#476エリア`. Please confirm whether this interpretation is acceptable.

## Notes

- The new prediction tab is a forecast layer, not a confirmed future state.
- The tab uses colors for current enemy footholds, first denial points, city destruction candidates, and #503-side convergence route.
- The integrated tab is a monitoring layer: red = existing #534 invader, orange = #476-side boundary alliance, purple = manually entered pact partner.
- Existing unrelated local changes remain outside this analysis.
