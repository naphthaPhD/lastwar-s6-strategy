# #534 Sheet V2 integration plan

## 1. Executive summary

`#534` Google Sheets V2 is not a separate new system. Treat it as a lightweight, staged version of the existing `管理表たたき` workflow.

The simplest durable design is:

1. Keep legacy tabs read-only.
2. Use `node_current_v2` as the normalized current-state table.
3. Derive `alerts_v2` and `risk_map_v2` from `node_current_v2`.
4. Keep `dashboard_v2` as a view layer only.
5. Generate JSON and heavy scoring from Python, not volatile spreadsheet formulas.

This keeps Google Sheets useful as the input and review surface while moving expensive judgment, JSON generation, and map/risk analysis into the existing `tools/invasion_strategy_os/` pipeline.

## 2. Context

Target spreadsheet: `#534`

Spreadsheet ID: `12uNW9XphH2zSX4h5BzjSd-OON9r5AckAuNCwQTbY79g`

Existing read-only source tabs:

- `管理表たたき`
- `拠点履歴_座標`
- `拠点履歴_イベント`
- `連盟協定`
- `連盟安全時間`
- `安全時間履歴`
- `RAW_OCR_LOG`
- `読取ログ`

Current V2 tabs already created in Google Sheets:

- `node_current_v2`
- `alerts_v2`
- `risk_map_v2`
- `dashboard_v2`

Existing local MVP artifacts:

- `sample_output/sheet_migration/map_nodes.csv`
- `sample_output/sheet_migration/ownership_current.csv`
- `sample_output/sheet_migration/pacts.csv`
- `sample_output/sheet_migration/alliance_directory.csv`
- `sample_output/sheet_migration/node_status.json`

Existing local MVP scripts:

- `tools/invasion_strategy_os/migrate_534_sheet_mvp.py`
- `tools/invasion_strategy_os/build_node_status_mvp.py`
- `tools/invasion_strategy_os/report_unmatched_owners_mvp.py`
- `tools/invasion_strategy_os/suggest_alliance_directory_from_power.py`

## 3. Key facts

- `管理表たたき` remains the operational source during migration.
- `Alliance Power` is dictionary evidence for alliance-to-server lookup only. It is not current ownership evidence.
- `pacts.csv` is for pact and attack-policy interpretation. It is not the alliance tag directory.
- `alliance_directory.csv` is the alliance tag to server directory.
- V2 should avoid heavy `NOW()`, array formulas, full-column formulas, and live dashboard logic where Python can precompute static snapshots.

## 4. Simplified data flow

```text
Legacy Google Sheets tabs
  -> local CSV extraction
  -> map_nodes.csv + ownership_current.csv
  -> alliance_directory.csv + pacts.csv enrichment
  -> node_status.json
  -> node_current_v2.csv
  -> alerts_v2.csv + risk_map_v2.csv
  -> dashboard_v2 view + map/JSON outputs
```

For now, Google Sheets write-back should stay manual or explicitly approved. The safe implementation target is local CSV/JSON generation first.

## 5. Sheet roles

### node_current_v2

Purpose: one row per node, sheet-friendly current-state table.

This should be the V2 equivalent of `node_status.json`, not another independent manual source.

Required columns:

```text
node_id
area
coord
node_type_raw
node_type_norm
x
y
current_alliance
status_raw
status_norm
captured_at_jst
safe_until_jst
protection_status
last_event_at
last_event_owner
event_count
confidence
memo
```

Recommended extra derived columns for Python and dashboard use:

```text
owner_server
owner_server_source
server_side
enemy_flag
destroyed_flag
warning_flags
source_row
updated_at_jst
```

### alerts_v2

Purpose: human review queue only.

Keep it small. For MVP, use one row per node with the highest-priority alert, plus a `reason` or `warning_flags` column for secondary reasons.

Priority order:

```text
destroyed_city
enemy_owned
safe_time_missing
uncertain
type_uncertain
abandon_detected
```

Recommended columns:

```text
alert_type
severity
node_id
coord
node_type_norm
current_alliance
server_side
status_norm
protection_status
safe_until_jst
reason
review_status
memo
```

### risk_map_v2

Purpose: risk visualization and JSON input.

This should be generated from `node_current_v2`, not hand-maintained.

Columns:

```text
node_id
coord
node_type_norm
current_alliance
status_norm
protection_status
safe_until_jst
frontline_group
server_side
enemy_flag
destroyed_flag
strategic_value
risk_score
risk_level
risk_note
```

### dashboard_v2

Purpose: commander dashboard.

Keep this as formulas, pivots, charts, or imported summary values over `node_current_v2`, `alerts_v2`, and `risk_map_v2`. Do not make it a source table.

Minimum dashboard blocks:

- total nodes
- protected nodes
- expired protection nodes
- missing safe time nodes
- destroyed nodes
- frontline core list
- frontline adjacent count
- enemy-owned count
- destroyed city list
- critical risk list

## 6. Normalization rules

### node_type_norm

```text
漁場 -> fishery
都市 -> city
密林の村 -> city
密林の兵舎 -> city
密林の集会場 -> city
交易地 -> trade
その他 -> unknown
```

### status_norm

```text
破壊 -> destroyed
保護中 -> owned
保護切れ -> owned
要確認 -> owned_uncertain
blank -> neutral_or_unknown
```

### server_side

Use `owner_server` after resolving it from `ownership_current`, numeric owner prefix, `alliance_directory`, or alias lookup.

```text
534 -> self
509, 440, 511 -> ally
any other resolved server -> enemy
blank owner_server -> unknown
blank current_alliance -> neutral_or_unknown
```

This satisfies the new V2 rule that every non-#534/#509/#440/#511 resolved server is enemy, while still avoiding false enemy classification when the owner server is not known.

## 7. Risk scoring

Base type score:

```text
city +30
trade +20
fishery +10
```

State score:

```text
enemy_flag +40
destroyed_flag +100
protection_expired +20
safe_time_missing +15
```

Frontline score:

```text
frontline_core +30
frontline_adjacent +15
```

Risk level:

```text
>= 90 critical
>= 60 high
>= 30 mid
< 30 low
```

## 8. Frontline rule

Core coordinates:

```text
D-11
D-13
E-11
E-13
d-12
d-14
c-8
c-10
```

Adjacent groups:

```text
D*
E*
d*
e*
```

Implementation note: keep `frontline_group` as one of:

```text
frontline_core
frontline_adjacent
other
```

## 9. Implementation sequence

1. Add a local generator that reads `node_status.json` and writes:
   - `sample_output/sheet_migration/node_current_v2.csv`
   - `sample_output/sheet_migration/alerts_v2.csv`
   - `sample_output/sheet_migration/risk_map_v2.csv`
2. Validate counts locally.
3. Compare generated `node_current_v2.csv` against the live `node_current_v2` sheet columns.
4. Only after human approval, write or paste the generated CSV into Google Sheets.
5. Keep `dashboard_v2` as a lightweight view over these generated tables.
6. Later, add JSON exports:
   - `nodes.json`
   - `node_current.json`
   - `events.json`
   - `pacts.json`
   - `risk_map.json`

## 10. Risks

- If `enemy = all non-ally` is applied before resolving `owner_server`, unknown owners may be overclassified as enemies.
- If `dashboard_v2` uses volatile full-column formulas, the sheet will become slow again.
- If `node_current_v2` is manually edited independently from `管理表たたき`, reconciliation will become unclear.
- `safe_until_jst` and `protection_status` should be snapshot values for analysis, not constantly recalculated dashboard formulas.

## 11. Recommended actions

1. Treat `node_current_v2` as the sheet-facing form of `node_status.json`.
2. Generate `alerts_v2` and `risk_map_v2` from Python first.
3. Do not write to Google Sheets until the generated CSV columns and counts are checked.
4. Adopt the simplified `server_side` rule for V2 risk scoring.
5. Keep the existing map output files untouched until the V2 CSV pipeline is verified.

## 12. Unknowns

- Whether `node_current_v2` should be fully generated or allow manual override columns.
- Whether `last_event_at`, `last_event_owner`, and `event_count` should come from `拠点履歴_イベント` immediately or remain blank in the first V2 snapshot.
- Whether dashboard charts should be native Google Sheets charts or generated HTML.
- Whether Google Sheets write-back will be done by Apps Script, Sheets API, or manual CSV paste.

## 13. Files referenced

- `sample_output/sheet_migration/map_nodes.csv`
- `sample_output/sheet_migration/ownership_current.csv`
- `sample_output/sheet_migration/pacts.csv`
- `sample_output/sheet_migration/alliance_directory.csv`
- `sample_output/sheet_migration/node_status.json`
- `tools/invasion_strategy_os/migrate_534_sheet_mvp.py`
- `tools/invasion_strategy_os/build_node_status_mvp.py`
- `tools/invasion_strategy_os/report_unmatched_owners_mvp.py`
- `tools/invasion_strategy_os/suggest_alliance_directory_from_power.py`
