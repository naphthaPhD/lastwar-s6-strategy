# Handoff summary

## Date

2026-05-27

## Context

The pact situation changed: #503-side alliances can now attack #534. The user first asked for worst-case invasion forecasting, then for a map view that can show currently invadable alliances. The map merge/position problem remained difficult when trying to forcibly connect four areas into one custom layout, so the latest decision is to return to the exact same shape as `取得入力マップ`.

Latest side classification for this handoff:

- Allies: #534, #509
- Enemies: #476, #503

## Updated files

- `analysis/2026-05-27_503_476_worst_case_invasion_forecast.md`
- `analysis/2026-05-27_integrated_invasion_map_update.md`
- `analysis/latest_handoff.md`

## Updated Google Sheet

- Spreadsheet ID: `12uNW9XphH2zSX4h5BzjSd-OON9r5AckAuNCwQTbY79g`
- Existing forecast tab: `侵攻予測_20260527_最悪`
- Existing trial tab: `侵攻予測_20260527_統合`
- New recommended map tab: `侵攻予測_20260527_取得入力型`
- Source tab for the new map: `取得入力マップ`
- New map sheetId: `1280147971`

`侵攻予測_20260527_取得入力型` was created by directly duplicating `取得入力マップ`. It preserves the source tab's structure instead of trying to rebuild the map manually.

The user then asked for this tab to periodically reflect `取得入力マップ` like `塗り絵マップ`. A sync patch was added to the preserved Apps Script source tab:

- Source tab/range: `AppsScript_地点詳細!A1241:A1316`
- Copy source: `取得入力マップ!A6:DN92`
- Copy target: `侵攻予測_20260527_取得入力型!A6:DN92`
- Manual function: `copyLatestInputMapToInvasionMap`
- Trigger installer: `installInvasionMapSyncTrigger`
- Trigger interval: 5 minutes
- Stop function: `removeInvasionMapSyncTriggers`
- Last-sync cell: `侵攻予測_20260527_取得入力型!DL2`

Important: this is saved in the source tab only. The connector did not update the live Apps Script `Code.gs`. To activate the menu and time trigger, copy the block from `AppsScript_地点詳細!A1241:A1316` into the bound Apps Script project and add the three menu lines shown in the comments to the final `onOpen()`.

Troubleshooting note: the error `右側の入力欄が空です。 savePointFromDetail @ コード.gs:123` means the old point-entry menu/function ran. It is not the sync function. For this map sync, use `copyLatestInputMapToInvasionMap`; for periodic sync, run `installInvasionMapSyncTrigger` once.

Manual sync verification:

- At 2026-05-27 13:08 JST, `取得入力マップ!A6:DN92` was copied to `侵攻予測_20260527_取得入力型!A6:DN92` by Sheets API.
- `侵攻予測_20260527_取得入力型!DL2` now shows `5/27 13:08 手動反映済`.
- The prediction tab now has an added warning in `A4` that `入力欄を管理表たたきへ反映` is not the sync command.

Verified properties:

- Row count: `92`
- Column count: `118`
- Frozen rows: `5`
- Gridlines: hidden
- Sample merge retained: `A6:B6`
- Sample merge retained: `A49:B49`
- Sample merge retained: `L49:M50`
- Sample values retained: `A6=RGWC`, `A49=476K`, `L49=476C`

## Key findings

1. With #503 able to participate, #534 should treat #503 as a right-side convergence threat, not as secondary background pressure.
2. The most dangerous pattern remains #476C pressing upward/interior while #476B pushes rightward and creates later #503-side convergence.
3. `D-11`, `D-9`, and `E-7` remain the main denial points from the prior worst-case forecast.
4. The attempt to remove seams and force a single connected custom map created too much risk of merge and position drift.
5. The safest working map is now `侵攻予測_20260527_取得入力型`, because it is an exact duplicate of `取得入力マップ`.
6. `侵攻予測_20260527_統合` should be treated as a trial/reference tab, not the operational source of truth.
7. The new sync patch copies only the map body, so top notes and tactical formatting on the prediction tab can remain while the map body is refreshed.

## Current risks

1. #534 may over-defend visible cities and lose the denial line around `D-11 / D-9 / E-7`.
2. If #476B and #476C split roles, one can pull attention upward while the other opens the right-side route toward the #503 side.
3. If #503 pact access works immediately through connected territory, right-side pressure can accelerate faster than #534's recovery cycle.
4. Map-based command mistakes are likely if members continue using the older `統合` tab after the latest change.
5. Additional color rules on the new duplicated tab could conflict with inherited conditional formatting unless added carefully.
6. If the sync patch is run, the map body becomes copied values rather than live formulas; therefore the manual copy or 5-minute trigger should be treated as part of the operating procedure.
7. The patch is not live until it is reflected into `Code.gs`.
8. Running `savePointFromDetail` with empty right-side inputs is expected to fail; do not use it for map sync.

## Recommended next actions

1. Use `侵攻予測_20260527_取得入力型` as the current operational map.
2. Stop treating `侵攻予測_20260527_統合` as the correct map shape; keep it only as an experiment/history unless it is later deleted.
3. Add enemy/pact highlighting only on the duplicated tab, without changing row/column/merge structure.
4. Keep the #476B / #476C / #503 analysis focused on city destruction risk and route-opening risk, not full-map fixed defense.
5. Before the next city-fight window, confirm which #503-side pact alliances can actually use adjacency against #534.
6. Reflect `AppsScript_地点詳細!A1241:A1316` into live `Code.gs` if automatic sync is needed during the fight window.
7. After reflecting the script, run `copyLatestInputMapToInvasionMap` once to test, then run `installInvasionMapSyncTrigger` only if repeated refresh is needed.

## Questions for ChatGPT

1. Should the operational map now be standardized on `侵攻予測_20260527_取得入力型`?
2. Is `D-11 > D-9 > E-7` still the correct denial priority if #503 can join immediately?
3. What short R4/R5 order should be shared for the next city-fight window?
4. Which enemy/pact alliances should be highlighted first on the duplicated map?

## Notes

- This update intentionally stops trying to delete AO or remove map borders by restructuring cells.
- The new tab keeps the same shape as `取得入力マップ`, including the difficult merged cells.
- `侵攻予測_20260527_取得入力型!A1:A3` and `DL1:DL2` were updated with sync notes and last-sync status.
- Existing unrelated local changes remain outside this analysis.
