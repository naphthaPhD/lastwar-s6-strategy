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
- Last-sync cell: `侵攻予測_20260527_取得入力型!DK2`

Important: this is saved in the source tab only. The connector did not update the live Apps Script `Code.gs`. To activate the menu and time trigger, copy the block from `AppsScript_地点詳細!A1241:A1316` into the bound Apps Script project and add the three menu lines shown in the comments to the final `onOpen()`.

Troubleshooting note: the error `右側の入力欄が空です。 savePointFromDetail @ コード.gs:123` means the old point-entry menu/function ran. It is not the sync function. For this map sync, use `copyLatestInputMapToInvasionMap`; for periodic sync, run `installInvasionMapSyncTrigger` once.

Manual sync verification:

- At 2026-05-27 13:08 JST, `取得入力マップ!A6:DN92` was copied to `侵攻予測_20260527_取得入力型!A6:DN92` by Sheets API.
- `侵攻予測_20260527_取得入力型!DK2` now shows `5/27 13:08 手動反映済`.
- The prediction tab now has an added warning in `A4` that `入力欄を管理表たたきへ反映` is not the sync command.

Prediction-layer input added:

- Right-side panel: `侵攻予測_20260527_取得入力型!DO1:DY90`
- Scenario selector: `DP2`
- Layer table: `DO18:DY90`
- Auto key formula: `DT19`
- Game coordinate helper column: `DY18:DY90`
- Map coloring range: `A6:CC88`
- Current column count after adding the panel and deleting the old usage column: `131`
- Category colors: `敵主攻`, `破壊候補`, `防衛優先`, `捨て候補`, `再取得`, `反攻ルート`, `起点`, `要確認`
- Scenario choices: `全表示`, `最悪パターン`, `476B上押し`, `476C右押し`, `503合流`, `反攻ルート`, `防衛ライン`, `捨て/交換`, `要確認`

The layer table is intentionally separate from the map body. After copying `取得入力マップ` into the forecast tab, commanders can add or edit rows in `DO19:DY90`; rows with `ON=TRUE` are overlaid onto the map by conditional formatting. `DP2=全表示` shows all active rows, while selecting a scenario shows only that scenario.

At 2026-05-27 13:42 JST, the old `取得入力マップの使い方` column was deleted from the prediction tab only. This removed `CD` from `侵攻予測_20260527_取得入力型`; the source `取得入力マップ` was not changed. The saved Apps Script source patch in `AppsScript_地点詳細!A1253` was also updated from `DL2` to `DK2`.

At 2026-05-27 13:58 JST, the map display was adjusted for command readability:

- `A6:CC88` now uses white background as the base. The operational goal is no alliance-color background copy on this prediction tab.
- Enemy alliance names from `敵連盟_作業用!A2:A300` are red.
- #534-side alliance names, detected from `管理表たたき` area `#534`, are blue unless they are also in the enemy list.
- #509-side ally names, detected from `管理表たたき` area `#509`, are green unless they are also in the enemy list.
- Other names remain black.
- Enemy list matching has priority over #534/#509 area matching, so an enemy-held name inside a friendly server area still appears red.

Verification samples:

- `A6=RGWC`: blue #534-side text on white background.
- `CB6=MOn`: green #509-side text on white background.
- Enemy-list names such as 476-series entries appear red.

The right-side table was also extended with `DY18:DY90` as `ゲーム座標(自動)`. It uses the `DT` auto key to look up `管理表たたき!T:T`, reads the source/memo field in `管理表たたき!L:L`, and extracts strings like `#534 X:449 Y:49`, displayed as `#534 X449 Y49`. Blank coordinate cells mean the source/memo field does not currently contain a game-coordinate string for that key.

Seeded scenarios:

- `最悪パターン`: main enemy pressure on `#534:D-11`, `#534:D-9`, `#534:E-7`; city destruction candidates around `#534:c-12`, `#534:c-10`, `#534:c-8`, `#534:b-10`.
- `防衛ライン`: denial priority remains `D-11 > D-9 > E-7`.
- `捨て/交換`: `#534:c-8` is marked as both discard candidate and immediate recapture candidate.
- `反攻ルート`: `#534:C-11` is the starting candidate; `#534:D-9`, `#476:D-9`, and `#476:C-11` are marked as short-window connection-cut candidates.
- `476B上押し`, `476C右押し`, `503合流`: initial role-split and convergence hypotheses are included as editable rows.

Verified properties:

- Row count: `92`
- Column count before prediction panel: `118`
- Column count after prediction panel and old usage column deletion: `131`
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
8. The right-side prediction layer now turns the tab into a paint-map workflow: add a coordinate row, select a scenario and category, set `ON=TRUE`, and the map highlights that point.
9. For command use, scenario switching is now simpler than creating separate tabs for every hypothesis.
10. The old `取得入力マップの使い方` column has been removed from the prediction tab to reduce clutter.
11. The map body now prioritizes white background plus text-color classification: red enemy, blue #534, green #509 ally, black other.
12. Game-coordinate display is available in `DY`, but only where `管理表たたき` already has a coordinate string in the memo/source field.

## Current risks

1. #534 may over-defend visible cities and lose the denial line around `D-11 / D-9 / E-7`.
2. If #476B and #476C split roles, one can pull attention upward while the other opens the right-side route toward the #503 side.
3. If #503 pact access works immediately through connected territory, right-side pressure can accelerate faster than #534's recovery cycle.
4. Map-based command mistakes are likely if members continue using the older `統合` tab after the latest change.
5. Additional color rules on the new duplicated tab could conflict with inherited conditional formatting unless added carefully.
6. If the sync patch is run, the map body becomes copied values rather than live formulas; therefore the manual copy or 5-minute trigger should be treated as part of the operating procedure.
7. The patch is not live until it is reflected into `Code.gs`.
8. Running `savePointFromDetail` with empty right-side inputs is expected to fail; do not use it for map sync.
9. Prediction rows are hypotheses, not confirmed rules. If fishery ownership, city break eligibility, or pact access changes, the right-side table must be updated before using the colors operationally.
10. The counterattack route layer should be treated as a short-window disruption plan; fixed occupation against #476/#503 pressure is still high-risk.
11. Because the map body background is intentionally white, prediction category background colors on `A6:CC88` are effectively secondary. Use `DP2` and the right-side table for category interpretation unless the white rule is later relaxed.
12. Coordinate blanks in `DY` are data gaps, not formula failure, when the corresponding `管理表たたき` memo/source field has no `#... X... Y...` text.

## Recommended next actions

1. Use `侵攻予測_20260527_取得入力型` as the current operational map.
2. Stop treating `侵攻予測_20260527_統合` as the correct map shape; keep it only as an experiment/history unless it is later deleted.
3. Add enemy/pact highlighting only on the duplicated tab, without changing row/column/merge structure.
4. Keep the #476B / #476C / #503 analysis focused on city destruction risk and route-opening risk, not full-map fixed defense.
5. Before the next city-fight window, confirm which #503-side pact alliances can actually use adjacency against #534.
6. Reflect `AppsScript_地点詳細!A1241:A1316` into live `Code.gs` if automatic sync is needed during the fight window.
7. After reflecting the script, run `copyLatestInputMapToInvasionMap` once to test, then run `installInvasionMapSyncTrigger` only if repeated refresh is needed.
8. Use `DP2=最悪パターン` to brief likely enemy break points, `DP2=防衛ライン` for minimum defense, `DP2=捨て/交換` for abandon/recapture, and `DP2=反攻ルート` for attack planning.
9. Add new rows under `DO19:DY90` whenever 476B/476C/503 captures a fishery or gains a new city-destruction adjacency.
10. Add missing game coordinates to `管理表たたき` memo/source fields in `#534 X449 Y49` or `#534 X:449 Y:49` style if `DY` should show them.

## Questions for ChatGPT

1. Should the operational map now be standardized on `侵攻予測_20260527_取得入力型`?
2. Is `D-11 > D-9 > E-7` still the correct denial priority if #503 can join immediately?
3. What short R4/R5 order should be shared for the next city-fight window?
4. Which enemy/pact alliances should be highlighted first on the duplicated map?
5. Are the seeded counterattack route candidates too aggressive given the current power gap, or useful as disruption-only options?
6. Should the command map keep white background only, or should prediction-category background colors be restored for specific scenarios?

## Notes

- This update intentionally stops trying to delete AO or remove map borders by restructuring cells.
- The new tab keeps the same shape as `取得入力マップ`, including the difficult merged cells.
- `侵攻予測_20260527_取得入力型!A1:A3` and `DK1:DK2` were updated with sync notes and last-sync status.
- `侵攻予測_20260527_取得入力型!DO:DY` is now the operator-facing prediction input area; the map body should still be treated as copied/current-state terrain.
- The map body is now a white-background command view with text colors: red enemy, blue #534, green #509 ally, black other.
- Existing unrelated local changes remain outside this analysis.
