# Handoff summary

## 2026-06-01 APACHE clarification and confirmation draft

## Context

Added the follow-up `(GcC)APACHE` chat clarification into the diplomacy OCR note and preserved a short English confirmation message for APACHE.

## Updated files

- `analysis/2026-06-01_gcc_apache_diplomacy_ocr.md`
- `analysis/latest_handoff.md`

## Key findings

1. Additional screenshots clarify the pact pairs as `GcC-KTVS`, `SHA-BAJ`, and `JDX-GoDs`.
2. APACHE separates a Wednesday movement/preparation plan from a Saturday plan.
3. The Saturday plan is described as `GoDs + JDX` entering #523.
4. The Wednesday movement appears to be related to `BAJ`.
5. APACHE's strategic intent is for #440 to enter #476 to stop enemy movement while #534/#511/#509 attack #523/#503/#480.
6. RevoLove's concern is that using a movement slot on Wednesday may be wasteful because Wednesday is an advance day; #440 internal movement may need to happen earlier.
7. A concise English confirmation draft was added so APACHE can verify the Japanese summary before it is shared.

## Recommended next actions

1. Send the confirmation draft to APACHE and ask for corrections.
2. Confirm exact date/time for the Wednesday and Saturday actions.
3. Confirm whether `KTV` and `KTVS` are the same alliance label.
4. Keep local file paths and personal-name-bearing paths out of shared Markdown/PDF outputs.

## 2026-06-01 GcC APACHE diplomacy OCR

## Context

OCR-read and summarized 10 screenshots from `(GcC)APACHE` chat about #440/#534 pact routing, #523 movement, #480/#476 operations, and critical fishery land.

## Updated files

- `analysis/2026-06-01_gcc_apache_diplomacy_ocr.md`
- `analysis/latest_handoff.md`

## Key findings

1. #440 `GcC` / `APACHE` is proposing movement toward #523 through pact coordination.
2. `APACHE` says `GoDs` and `IMp` will move toward #523, and asks #534-side alliances to pact with those two alliances to start moving to #523.
3. `4tH` is described as making pact with `GoDs` and entering #523 next Saturday.
4. `GcC` says it will pact with `KTV` on Friday, but also says `GcC` must pact with `SHA` Friday; this is unresolved and needs confirmation.
5. `APACHE` says the goal may be to enter #476 and defeat them.
6. #476 `SHA` fishery Lv.1 at `X:599 Y:978` is described as very important and should be defended.
7. `RevoLove` says `JDX` and `KTVS` plan to advance inside #480 on Wednesday; `APACHE` corrects that the plan is Saturday, not Wednesday.
8. `APACHE` warns that dropping land may leave it shielded until Wednesday, so wrong land selection can block the route.

## Current risks

1. Friday pact target is ambiguous: `KTV/KTVS`, `SHA`, or both.
2. Wednesday vs Saturday timing is inconsistent between #534 and #440 understanding.
3. `BAJ/baj` relationship to `SHA` pact is unclear from OCR.
4. Losing #476 `SHA` land at `599,978` may disrupt a later route or pact condition.

## Recommended next actions

1. Ask `APACHE` to clarify Friday pact target: `KTV/KTVS`, `SHA`, or both.
2. Confirm whether #480 movement is Wednesday while #523 entry is Saturday, or whether all movement should wait until Saturday.
3. Confirm `4tH -> GoDs -> #523` route with both 4tH and GoDs.
4. Assign defense responsibility for #476 `SHA` fishery `X:599 Y:978`.

## 2026-05-31 R4/R5 map colors from area color assignment

## Context

Expanded the R4/R5 review `map_review_v2` color rules using the production `#534` sheet `エリア色割当`. Production `#534` was read only and was not written to.

## Updated files

- `analysis/latest_handoff.md`

## External output

- Google Sheets: `https://docs.google.com/spreadsheets/d/1PEU2O5DWGpC_vuaSkTCl1y6AzQ1QXLdQlKOgAD2ifb4/edit`

## Key findings

1. Read `エリア色割当` from production `#534`.
2. Expanded #534 blue rules from the #534 column, including previously uncolored tags such as `MOE`, `SHA0`, `sg3`, `Trh`, `w6F`, `Skh`, `kOi`, `59U`, `noI`, `Dao`, `RGWC`, `f4j`, `moca`, `CROW`, and `Ryu1`.
3. Expanded #509/#440/#511 green rules from the corresponding ally columns.
4. Expanded #503/#480/#523/#476 red rules from the corresponding enemy columns.
5. Kept `破壊` cells with gray background.
6. Left the `中央` column out of automatic side coloring because it does not itself define a server side.
7. Sample readback confirmed newly covered tags such as `MOE`, `JL0`, and `EDFS` exist on `map_review_v2`.

## Recommended next actions

1. If central-map tags need side colors, review them manually and add them to `alliance_directory.csv` or a separate central-side rule.
2. Continue using `alliance_audit` to resolve uncolored or ambiguous tags.
3. Treat the map colors as review aids, not final attack authorization.

## 2026-05-31 R4/R5 map alliance color rules

## Context

Updated the R4/R5 review `map_review_v2` color rules so alliance-name colors are based on resolved server affiliation, not the area where the cell appears. Production `#534` was not written to.

## Updated files

- `analysis/latest_handoff.md`

## External output

- Google Sheets: `https://docs.google.com/spreadsheets/d/1PEU2O5DWGpC_vuaSkTCl1y6AzQ1QXLdQlKOgAD2ifb4/edit`

## Key findings

1. Added conditional formatting over `map_review_v2!A1:DU120`.
2. Confirmed #534 alliance names are blue: `4tH`, `89M`, `JDX`, `KTVS`, `SHA`, `nO9`.
3. Confirmed #509/#440/#511 alliance names are green: `2N7`, `BAJ`, `DaNG`, `FHX`, `GoDs`, `SsQ`, `SVa`, `VEX`, `tWD`.
4. Confirmed #503/#480/#476 alliance names are red: `476A`, `476B`, `476C`, `476H`, `476K`, `476M`, `476T`, `476X`, `476Z`, `476d`, `AAOA`, `BgNa`, `Digg`, `GX99`, `Lghs`, `RCON`, `TkTk`, `fzn`.
5. `破壊` cells have gray background.
6. Unresolved alliances are intentionally left uncolored to avoid false self/ally/enemy classification.
7. Sample readback found `SHA`, `FHX`, `476A`, and `破壊` cells in `map_review_v2`.

## Recommended next actions

1. Review unresolved alliance names in `alliance_audit` before adding more color rules.
2. Add #523-specific alliance tags once their resolved server is confirmed.
3. Keep `map_review_v2` as a review surface, not an operation-order surface.

## 2026-05-31 R4/R5 map refreshed from management table

## Context

Refreshed the R4/R5 review `map_review_v2` using the latest production `#534` map values. Production `全体マップたたき` already references `管理表たたき`, so the review map was updated by refreshing hidden `map_review_raw_v2` and pasting its current values into the visible copied map tab.

## Updated files

- `analysis/latest_handoff.md`

## External output

- Google Sheets: `https://docs.google.com/spreadsheets/d/1PEU2O5DWGpC_vuaSkTCl1y6AzQ1QXLdQlKOgAD2ifb4/edit`

## Key findings

1. Refreshed `map_review_raw_v2` with `IMPORTRANGE` from production `全体マップたたき!A1:DU120`.
2. Pasted the current values from `map_review_raw_v2` into visible `map_review_v2`.
3. Kept the copied production map formatting, merged cells, and column widths on `map_review_v2`.
4. Readback confirmed sampled #534, #476, and #509 ranges have current values and no `#REF!`.
5. Production `#534` was not modified.

## Recommended next actions

1. Use `map_review_v2` as the current visual map snapshot for R4/R5 review.
2. Repeat the same refresh process after future `管理表たたき` updates.
3. If live auto-refresh is required later, copy the dependency tabs or move map rendering to a script-generated view.

## 2026-05-31 R4/R5 full-copy map refresh

## Context

Rebuilt the R4/R5 review `map_review_v2` by copying the production `#534` `全体マップたたき` tab first, then replacing broken formulas with current imported values. This preserves the original map layout, formatting, column widths, and merged-cell structure much better than the previous manual reconstruction.

## Updated files

- `analysis/latest_handoff.md`

## External output

- Google Sheets: `https://docs.google.com/spreadsheets/d/1PEU2O5DWGpC_vuaSkTCl1y6AzQ1QXLdQlKOgAD2ifb4/edit`

## Key findings

1. Renamed the previous manual `map_review_v2` to `map_review_v2_old_manual` and hid it.
2. Copied production `全体マップたたき` into the review spreadsheet as the new visible `map_review_v2`.
3. The copied formulas initially showed `#REF!` because the review spreadsheet does not contain production-side dependency tabs such as `管理表たたき`.
4. Fixed the visible map by pasting current values from hidden `map_review_raw_v2` into the copied tab, while keeping copied formatting and merged cells.
5. Readback confirmed visible values for #534, #476, and #509 sections without `#REF!` in sampled ranges.
6. Production `#534` was not modified.

## Recommended next actions

1. Use this full-copy `map_review_v2` as the visual map surface for R4/R5.
2. Refresh by repeating the same pattern: import current values into hidden raw tab, then paste values onto the copied visible tab.
3. Avoid adding live formulas from production dependency tabs into the review spreadsheet unless those dependency tabs are intentionally copied too.

## 2026-05-31 R4/R5 merged map view refresh

## Context

Refined the R4/R5 review Google Spreadsheet map. The visible `map_review_v2` tab now uses a value snapshot from production `#534` `全体マップたたき`, with merged area headers and compact map formatting. Production `#534` was read only and was not written to.

## Updated files

- `analysis/latest_handoff.md`

## External output

- Google Sheets: `https://docs.google.com/spreadsheets/d/1PEU2O5DWGpC_vuaSkTCl1y6AzQ1QXLdQlKOgAD2ifb4/edit`

## Key findings

1. Confirmed `全体マップたたき` formulas read from `管理表たたき`, so the refreshed review map reflects the user's latest management-table updates.
2. Created hidden helper tab `map_review_raw_v2` to import the current production map.
3. Rebuilt visible `map_review_v2` as a value-snapshot map and merged the main area headers for #534/#509/#503, #476/central/#480, and #523/#511/#440 layout.
4. Updated compact row/column sizing, borders, header formatting, and README notes.
5. Production `#534` was not modified.

## Recommended next actions

1. Use `map_review_v2` as the R4/R5 visual map surface.
2. If the production `管理表たたき` changes again, refresh the value snapshot from `map_review_raw_v2`.
3. Keep action decisions tied to `briefing`, `edge` tabs, and `alliance_audit`; use the map as visual confirmation.

## 2026-05-31 GitHub account transition summary

## Context

Summarized the GitHub account transition work for this repository. The account switch is intended to be repo-local to this S6 checkout and should not affect other local projects.

## Updated files

- `analysis/2026-05-31_github_account_transition_summary.md`
- `analysis/latest_handoff.md`

## Key findings

1. The repository now points to `https://naphthaPhD@github.com/naphthaPhD/lastwar-s6-strategy.git`.
2. Repo-local Git identity is `naphthaPhD <naphthaPhD@users.noreply.github.com>`.
3. `credential.useHttpPath=true` is set locally so credentials can be separated by repository path.
4. The public repository remains read-only for other users unless collaborators are explicitly added.
5. Raw personal login email should not be used as public commit metadata.

## Current risks

1. HTTPS push still depends on Git Credential Manager selecting or prompting for the `naphthaPhD` account.
2. If the wrong GitHub account appears during authentication, the push should be cancelled.
3. Existing unrelated local changes under `sample_output/` and `tools/invasion_strategy_os/` were not included in this summary commit.

## Recommended next actions

1. Push `main` only after confirming authentication uses `naphthaPhD`.
2. Keep GitHub collaborators empty unless write access is intentionally granted.
3. Consider branch protection for `main` after the initial push.

## 2026-05-31 R4/R5 review map tab

## Context

Added a map view to the separate R4/R5 review Google Spreadsheet. The tab reuses the production `#534` spreadsheet's `全体マップたたき` layout by read-only `IMPORTRANGE`; production `#534` was not written to.

## Updated files

- `analysis/latest_handoff.md`

## External output

- Google Sheets: `https://docs.google.com/spreadsheets/d/1PEU2O5DWGpC_vuaSkTCl1y6AzQ1QXLdQlKOgAD2ifb4/edit`

## Key findings

1. Added review tab: `map_review_v2`.
2. `map_review_v2` imports `全体マップたたき!A1:DU120` from production `#534` for display only.
3. The imported map expanded successfully on readback.
4. Added simple visual formatting: compact map cells, frozen note rows, and conditional colors for confirmed self/ally candidates, known enemy candidates, and destroyed cells.
5. Updated `README` to note that `map_review_v2` is a read-only review map and does not write to production `#534`.

## Recommended next actions

1. Use `map_review_v2` as the meeting map surface alongside `briefing`.
2. Keep actual correction work in CSV/alliance audit first; do not edit production map from the review sheet.
3. If more precision is needed, replace the live `IMPORTRANGE` view with a generated overlay from `node_current_v2.csv` and `risk_map_v2.csv`.

## 2026-05-31 SHA/nO9 refreshed R4/R5 review Google Sheet

## Context

Updated the separate R4/R5 review Google Spreadsheet after the `SHA` and `nO9` manual overrides. This update targeted only the review spreadsheet, not the production `#534` spreadsheet.

## Updated files

- `analysis/latest_handoff.md`

## External output

- Google Sheets: `https://docs.google.com/spreadsheets/d/1PEU2O5DWGpC_vuaSkTCl1y6AzQ1QXLdQlKOgAD2ifb4/edit`

## Key findings

1. Updated tabs: `README`, `briefing`, `self_defense_edges`, `self_attack_edges`, `ally_coordination`, `map_check_queue`, `critical_534`, `dashboard`, `alliance_audit`.
2. `briefing` now shows #534 self attack edges `5` and #534 self defense edges `5`.
3. `alliance_audit` includes all `108` alliance audit rows with the requested review columns.
4. `SHA`, `nO9`, `JDX`, and `4tH` all read back as `server=534`, `server_side=self`, `risk_flag` blank, `review_status=ok`.
5. Production `#534` was not written to; full `node_current_v2`, full `risk_map_v2`, `alerts_v2`, and `safe_time_reference_review_v2` were not added to the review sheet.

## Recommended next actions

1. Use the refreshed Google Sheet for R4/R5 meeting review after SHA/nO9 correction.
2. Treat `map_check_queue` as confirmation work and `confidence=medium` rows as human-review items.
3. Keep `alliance_audit` as the next data-quality review surface before issuing action language.

## 2026-05-31 SHA/nO9 manual side override

## Context

Manually confirmed `SHA` and `nO9` as #534-side alliances and regenerated local V2 CSV/Markdown outputs. Google Sheets write-back was not performed.

## Updated files

- `sample_output/sheet_migration/alliance_directory.csv`
- `tools/invasion_strategy_os/build_sheet_v2_outputs.py`
- `tools/invasion_strategy_os/build_alliance_side_audit.py`
- `sample_output/sheet_migration/node_current_v2.csv`
- `sample_output/sheet_migration/risk_map_v2.csv`
- `sample_output/sheet_migration/current_enemy_nodes_v2.csv`
- `sample_output/sheet_migration/current_friendly_nodes_v2.csv`
- `sample_output/sheet_migration/*edge*_v2.csv`
- `analysis/commander_review_2026-05-31.md`
- `analysis/r4_r5_briefing_2026-05-31.md`
- `sample_output/sheet_migration/alliance_side_audit_v2.csv`
- `analysis/alliance_side_audit_2026-05-31.md`
- `analysis/latest_handoff.md`

## Key findings

1. `SHA` classification is now `server=534`, `side=self`, `risk=none`.
2. `nO9` classification is now `server=534`, `side=self`, `risk=none`.
3. `JDX` and `4tH` remain `server=534`, `side=self`, `risk=none`.
4. `current_enemy_nodes=401`, `current_friendly_nodes=302`.
5. Attack edge split: self `5`, ally `3`, unknown `25`.
6. Defense edge split: self `5`, ally `5`, unknown `23`.
7. `side_check_required rows=77`.

## Recommended next actions

1. Re-review the refreshed R4/R5 briefing before sharing any order language.
2. Treat `side_check_required` rows as data-quality review work before further candidate expansion.
3. Do not write refreshed outputs into production `#534` until human approval.

## 2026-05-31 Alliance side audit

## Context

Prioritized alliance ownership and side-classification audit before generating or expanding any further R4/R5 attack candidates. This audit is needed because alliances such as `SHA` and `nO9` may be #534-side or allied, while current generated outputs classify them as enemy.

## Updated files

- `tools/invasion_strategy_os/build_alliance_side_audit.py`
- `sample_output/sheet_migration/alliance_side_audit_v2.csv`
- `analysis/alliance_side_audit_2026-05-31.md`
- `analysis/latest_handoff.md`

## Key findings

1. `alliance_side_audit_v2.csv` has `108` alliance rows.
2. `risk_flag` rows: `79`.
3. `unknown resolved_server` rows: `70`.
4. `appears_as_enemy but maybe self/ally` rows: `2`.
5. `SHA` classification: `server=503`, `server_side=enemy`, risk `enemy_in_534_area; enemy_but_known_self_or_ally_candidate`.
6. `nO9` classification: `server=476`, `server_side=enemy`, risk `enemy_in_534_area; enemy_but_known_self_or_ally_candidate`.
7. `JDX` and `4tH` both resolve to `server=534`, `server_side=self`, with no risk flag.

## Recommended next actions

1. Treat R4/R5 attack candidates as unconfirmed until `SHA` and `nO9` are manually reviewed.
2. Use `manual_server_override` and `manual_note` in `alliance_side_audit_v2.csv` for human correction notes only; do not auto-apply them yet.
3. After review, update `alliance_directory.csv` by human-approved changes, then regenerate V2 outputs.

## 2026-05-31 R4/R5 Google Sheets review export

## Context

Wrote the R4/R5 review material to a separate Google Spreadsheet, not the production `#534` spreadsheet. The target spreadsheet is `#534_R4R5レビュー_2026-05-31`.

## Updated files

- `analysis/latest_handoff.md`

## External output

- Google Sheets: `https://docs.google.com/spreadsheets/d/1PEU2O5DWGpC_vuaSkTCl1y6AzQ1QXLdQlKOgAD2ifb4/edit`

## Key findings

1. Created/updated tabs: `README`, `briefing`, `self_defense_edges`, `self_attack_edges`, `ally_coordination`, `map_check_queue`, `critical_534`, `dashboard`.
2. The sheet includes only commander-review material: no `node_current_v2`, no `risk_map_v2`, no `alerts_v2`, and no `safe_time_reference_review_v2`.
3. Production `#534` was not written to.

## Recommended next actions

1. Use the Google Sheet as the first R4/R5 meeting view.
2. Keep detailed review in `analysis/commander_review_2026-05-31.md` and the classified CSVs.
3. Treat `map_check_queue` rows as confirmation work, not orders.

## 2026-05-31 R4/R5 one-page briefing

## Context

Created a one-page R4/R5 briefing from the commander review, classified edge CSVs, and commander dashboard. This is a meeting-start summary, not an operation order. Google Sheets write-back was not performed.

## Updated files

- `analysis/r4_r5_briefing_2026-05-31.md`
- `tools/invasion_strategy_os/build_r4_r5_briefing.py`
- `analysis/latest_handoff.md`

## Key findings

1. The briefing summarizes #534 destroyed critical cities `4`, #534 self attack edges `7`, #534 defense edges `7`, ally attack edges `11`, ally defense edges `11`, and map-check queues `21/21`.
2. The displayed tables are capped for meeting use: #534 defense max 7, #534 attack max 7, ally attack max 5, ally defense max 5.
3. `city_destroy_enabled=TRUE` in the current commander dashboard snapshot.

## Recommended next actions

1. Use `analysis/r4_r5_briefing_2026-05-31.md` as the first R4/R5 view.
2. Use `analysis/commander_review_2026-05-31.md` and classified CSVs only for drill-down review.
3. Treat all `edge_unknown` rows as map-confirmation queues, not orders.

## 2026-05-31 Edge execution classification

## Context

Split concrete edge candidates into execution classes for R4/R5 review. This is still a triage layer, not an operation order. Google Sheets write-back was not performed.

## Updated files

- `tools/invasion_strategy_os/build_sheet_v2_outputs.py`
- `sample_output/sheet_migration/server_534_attack_edges_self_v2.csv`
- `sample_output/sheet_migration/server_534_attack_edges_ally_v2.csv`
- `sample_output/sheet_migration/server_534_attack_edges_unknown_v2.csv`
- `sample_output/sheet_migration/enemy_invasion_edges_self_defense_v2.csv`
- `sample_output/sheet_migration/enemy_invasion_edges_ally_defense_v2.csv`
- `sample_output/sheet_migration/enemy_invasion_edges_unknown_v2.csv`
- `analysis/commander_review_2026-05-31.md`
- `analysis/latest_handoff.md`

## Key findings

1. #534 attack edges split into self action `7`, ally coordination `11`, and map-check required `21`.
2. Enemy invasion defense edges split into #534 defense `7`, ally defense `11`, and map-check required `21`.
3. Classified CSVs add `execution_class`, `recommended_owner`, `review_priority`, and `human_check`.
4. `analysis/commander_review_2026-05-31.md` now has six edge-classification sections, each capped at 10 displayed rows.

## Recommended next actions

1. Review `server_534_attack_edges_self_v2.csv` first for #534-only candidate actions.
2. Use ally-classified files only as coordination candidates with #509/#440/#511.
3. Treat all unknown-classified rows as map-confirmation work, not executable orders.

## 2026-05-31 Concrete attack and defense edges

## Context

Added concrete adjacent-edge CSVs using `sample_output/state.json` connections plus `node_current_v2.csv` side classification. These are map-confirmation candidate lists, not orders. Google Sheets write-back was not performed.

## Updated files

- `tools/invasion_strategy_os/build_sheet_v2_outputs.py`
- `sample_output/sheet_migration/top_enemy_invasion_edges_v2.csv`
- `sample_output/sheet_migration/top_server_534_attack_edges_v2.csv`
- `analysis/latest_handoff.md`

## Key findings

1. `top_enemy_invasion_edges_v2.csv` maps enemy candidate nodes to adjacent self/ally defense nodes where the state graph has a connection.
2. `top_server_534_attack_edges_v2.csv` maps #534 attack targets to adjacent self/ally source nodes, preferring self sources over ally sources.
3. If no adjacent self/ally source is found in `state.json`, the row is emitted with blank source/target fields and `recommended_action=地図確認`.
4. Current output check: `enemy_invasion_edges rows=39`, `server_534_attack_edges rows=39`, enemy defense blanks `21`, attack source blanks `21`, self-source attack edges `7`, ally-source attack edges `11`.
5. Current generated snapshot has `city_destroy_enabled=TRUE`, so city target rows remain `都市破壊候補`.

## Recommended next actions

1. Review `edge_unknown` rows on the map before using them in commander discussion.
2. For attack edges, prioritize `self_to_enemy_adjacent` rows before `ally_to_enemy_adjacent` rows.
3. If too many #476 rows remain `edge_unknown`, inspect whether cross-area adjacency is missing from `state.json` or excluded by current map rules.

## 2026-05-31 Commander review practical cleanup

## Context

Refined commander-facing outputs so R4/R5 starts with #534-relevant risk instead of global destroyed-city noise. Destroyed nodes are no longer shown as `server_side=unknown`; they are separated as destroyed. Google Sheets write-back was not performed.

## Updated files

- `tools/invasion_strategy_os/build_sheet_v2_outputs.py`
- `sample_output/sheet_migration/top_critical_risks_global_v2.csv`
- `sample_output/sheet_migration/top_critical_risks_534_v2.csv`
- `sample_output/sheet_migration/top_server_534_attack_targets_v2.csv`
- `sample_output/sheet_migration/commander_dashboard_v2.csv`
- `analysis/commander_review_2026-05-31.md`
- `analysis/latest_handoff.md`

## Key findings

1. Critical risk is now split into global and #534-specific files. The review report shows #534 Critical Risk first, then global Critical Risk later.
2. Destroyed rows use `owner_server=none` and `server_side=destroyed`, so they are not treated as unknown owners.
3. Enemy invasion `recommended_action` now separates `防衛確認`, `隣接確認`, and other review actions instead of making every row `協定影響確認`.
4. #534 attack output is now treated as attack targets via `top_server_534_attack_targets_v2.csv`; blank `from_node_id` means launch source is not assigned.
5. Battle-window summary is included in `commander_dashboard_v2.csv`; current generated snapshot has `city_destroy_enabled=TRUE`.

## Output check

```text
top_critical_risks_534_v2 rows=4
top_critical_risks_global_v2 rows=30
top_enemy_invasion_candidates_v2 rows=30
top_server_534_attack_targets_v2 rows=30
unknown_owner_review_v2 rows excluding destroyed=646
recommended_action: 攻撃候補=11, 破壊済み確認=34, 都市破壊候補=19, 防衛確認=9, 隣接確認=21
city_destroy_enabled=TRUE
```

## Recommended next actions

1. Review `top_critical_risks_534_v2.csv` and `analysis/commander_review_2026-05-31.md` before sharing with R4/R5.
2. Treat `top_server_534_attack_targets_v2.csv` as target selection only; launch/source nodes still require map confirmation.
3. Improve `unknown_owner_review_v2.csv` next to raise confidence in side judgment.

## 2026-05-31 Commander CSV review report

## Context

Generated a human-review Markdown report from the commander-facing V2 CSVs. This is not an operation order. It is a review aid for checking auto-generated triage rows before any R4/R5 decision.

## Updated files

- `analysis/commander_review_2026-05-31.md`
- `analysis/latest_handoff.md`

## Key findings

1. The report includes the commander dashboard summary, top 30 critical risks, top 30 enemy invasion candidates, and top 30 #534 attack candidates.
2. It automatically extracts review warnings: `confidence=medium`, blank `from_node_id`, unresolved owner server, `recommended_action` breakdown, and duplicate coordinates.
3. Current extracted counts are `confidence=medium: 60`, `from_node_id blank: 30`, unresolved owner server in critical top rows: 30, and duplicate coordinate groups: 20.

## Recommended next actions

1. Review `analysis/commander_review_2026-05-31.md` before sharing any order text.
2. Treat blank `from_node_id` rows as requiring map confirmation of launch/source nodes.
3. Use duplicate coordinate groups to identify places appearing in multiple commander lists.

## 2026-05-31 Commander CSV readability

## Context

Commander-facing V2 CSVs were reshaped so R4/R5 can read each row as: which node, who owns it, why it matters, and what to do next. This is a presentation/readability change, not a scoring-accuracy expansion. Google Sheets write-back was not performed.

## Updated files

- `tools/invasion_strategy_os/build_sheet_v2_outputs.py`
- `sample_output/sheet_migration/commander_dashboard_v2.csv`
- `sample_output/sheet_migration/top_critical_risks_v2.csv`
- `sample_output/sheet_migration/top_enemy_invasion_candidates_v2.csv`
- `sample_output/sheet_migration/top_server_534_attack_candidates_v2.csv`
- `analysis/2026-05-31_534_sheet_v2_integration_plan.md`
- `analysis/latest_handoff.md`

## Key findings

1. `top_critical_risks_v2.csv` now has rank, node identity, owner/server fields, `risk_reason`, `recommended_action`, `confidence`, and `memo_short`.
2. `top_enemy_invasion_candidates_v2.csv` now uses `from_*` fields for the enemy-held candidate and `to_*` fields for the #534/allied defensive review target.
3. `top_server_534_attack_candidates_v2.csv` now uses `to_*` fields for the enemy-held target and includes `attack_reason`, `priority`, and `recommended_action`.
4. `commander_dashboard_v2.csv` now includes critical/high risk, current enemy/friendly counts, frontline risk, candidate counts, unknown owner, type uncertain, and safe-time reference counts.

## Output check

```text
top_critical_risks_v2 rows=30
top_enemy_invasion_candidates_v2 rows=30
top_server_534_attack_candidates_v2 rows=30
recommended_action: 協定影響確認=30, 攻撃候補=11, 破壊済み確認=30, 都市破壊候補=19
confidence: high=30, medium=60
unknown owner count=646
```

## Recommended next actions

1. Have R4/R5 review the four commander files first.
2. Treat blank `from_node_id` in #534 attack candidates as "specific launch point not assigned yet."
3. Improve `unknown_owner_review_v2.csv` next to increase trust in server-side judgments.

## 2026-05-31 V2 operation-layer split

## Context

`alerts_v2.csv` has 1931 rows and is too large for commanders. V2 outputs are now split into commander, staff, and data-maintenance layers. Google Sheets write-back was not performed.

## Updated files

- `tools/invasion_strategy_os/build_sheet_v2_outputs.py`
- `sample_output/sheet_migration/commander_dashboard_v2.csv`
- `sample_output/sheet_migration/top_critical_risks_v2.csv`
- `sample_output/sheet_migration/top_enemy_invasion_candidates_v2.csv`
- `sample_output/sheet_migration/top_server_534_attack_candidates_v2.csv`
- `sample_output/sheet_migration/unknown_owner_review_v2.csv`
- `sample_output/sheet_migration/type_uncertain_review_v2.csv`
- `sample_output/sheet_migration/safe_time_reference_review_v2.csv`
- `analysis/2026-05-31_534_sheet_v2_integration_plan.md`
- `analysis/latest_handoff.md`

## Key findings

1. R4/R5 should start with `commander_dashboard_v2.csv`, `top_critical_risks_v2.csv`, `top_enemy_invasion_candidates_v2.csv`, and `top_server_534_attack_candidates_v2.csv`.
2. Staff-level detailed files remain: enemy/friendly nodes, frontline risk, invasion candidates, attack candidates, and `risk_map_v2.csv`.
3. Data-maintenance review files are separated: unknown owner, type uncertain, and safe-time reference review.
4. `alerts_v2.csv` is explicitly a back-office review queue, not commander-facing output.
5. Current new-layer counts are `commander_dashboard_v2 rows=10`, top critical/enemy invasion/#534 attack rows are all 30, unknown owner review is 646, type uncertain review is 132, and safe-time reference review is 1349.

## Current risks

1. `unknown_owner_review_v2.csv` remains the highest-value cleanup queue because server-side accuracy depends on owner-server resolution.
2. Top candidate files are triage lists and still need human map/context review before orders.

## Recommended next actions

1. Use the four commander files as the first R4/R5 review package.
2. Work through `unknown_owner_review_v2.csv` to improve `alliance_directory.csv`.
3. Keep `alerts_v2.csv` out of commander sharing unless filtered.

## 2026-05-31 Sheet V2 policy change

## Context

Protection update time, protection expiry time, and abandonment time are no longer complete-restoration targets. The V2 flow now prioritizes current decision support from `node_status.json`: owner-server resolution, current-alliance accuracy, server-side judgment, frontline judgment, and pact-aware invasion candidates.

## Updated files

- `tools/invasion_strategy_os/build_sheet_v2_outputs.py`
- `sample_output/sheet_migration/node_current_v2.csv`
- `sample_output/sheet_migration/alerts_v2.csv`
- `sample_output/sheet_migration/risk_map_v2.csv`
- `sample_output/sheet_migration/current_enemy_nodes_v2.csv`
- `sample_output/sheet_migration/current_friendly_nodes_v2.csv`
- `sample_output/sheet_migration/server_534_frontline_risk_v2.csv`
- `sample_output/sheet_migration/enemy_invasion_candidates_v2.csv`
- `sample_output/sheet_migration/server_534_attack_candidates_v2.csv`
- `analysis/2026-05-31_534_sheet_v2_integration_plan.md`
- `analysis/latest_handoff.md`

## Key findings

1. `safe_until_jst` remains in CSVs as reference information, but `safe_time_missing` and `protection_expired` are removed from the primary `risk_score`.
2. `alerts_v2` is now focused on current review needs: destroyed cities, enemy-owned nodes, uncertain side/alliance judgment, and uncertain types.
3. Added current-decision outputs for enemy-owned nodes, friendly-owned nodes, #534 frontline risk, enemy invasion candidates, and #534 attack candidates.
4. Current counts are `node_current_v2 rows=2168`, `alerts_v2 rows=1931`, `risk_map_v2 rows=2168`, `critical count=55`, `high count=193`, `mid count=848`, `low count=1072`.
5. Current decision-output counts are `current_enemy_nodes_v2=441`, `current_friendly_nodes_v2=262`, `server_534_frontline_risk_v2=190`, `enemy_invasion_candidates_v2=49`, and `server_534_attack_candidates_v2=388`.

## Current risks

1. Enemy and friendly outputs are only as reliable as `owner_server` and `current_alliance` resolution.
2. Invasion and attack candidate CSVs are current triage lists, not full route/adjacency proofs.
3. Google Sheets write-back is still intentionally not performed.

## Recommended next actions

1. Improve `alliance_directory.csv` to reduce `owner_server=unknown`.
2. Use the enemy/friendly/current frontline CSVs as the first commander review queue.
3. Add pact-aware adjacency or route logic only after current ownership accuracy improves.

## 2026-05-31 Sheet V2 CSV generator

## Context

`node_current_v2`, `alerts_v2`, and `risk_map_v2` are now generated locally from `sample_output/sheet_migration/node_status.json`. Google Sheets remains a review/display surface; no automatic write-back was performed.

## Updated files

- `tools/invasion_strategy_os/build_sheet_v2_outputs.py`
- `sample_output/sheet_migration/node_current_v2.csv`
- `sample_output/sheet_migration/alerts_v2.csv`
- `sample_output/sheet_migration/risk_map_v2.csv`
- `analysis/2026-05-31_534_sheet_v2_integration_plan.md`
- `analysis/latest_handoff.md`

## Key findings

1. `server_side` is fixed as `534=self`, `509/440/511=ally`, all other resolved owner servers as `enemy`, and missing owner server as `unknown`.
2. `alerts_v2` is generated from `node_current_v2`; it is not a manual input table.
3. `risk_map_v2` is generated from `node_current_v2` using the risk rules in `analysis/2026-05-31_534_sheet_v2_integration_plan.md`.
4. Current output counts are `node_current_v2 rows=2168`, `alerts_v2 rows=2168`, `risk_map_v2 rows=2168`, `critical count=81`, `high count=429`, `mid count=680`, `low count=978`.
5. The current `node_status.json` snapshot does not include `safe_until_jst`, so many owned nodes are intentionally flagged as `safe_time_missing`.

## Current risks

1. `alerts_v2` currently contains all 2168 nodes because safe-time and unknown-owner data is incomplete in `node_status.json`.
2. `safe_time_missing` should be treated as a data-completeness review queue, not direct in-game proof.
3. The generated CSVs should be reviewed before any paste or API write into Google Sheets.

## Recommended next actions

1. Review the generated CSVs locally.
2. Decide whether `node_status.json` should be extended with `safe_until_jst` before importing V2 sheets.
3. After human approval, paste or write the CSVs into the corresponding Google Sheets tabs.

## 2026-05-31 #534 Sheet V2 integration plan

## Context

Google Spreadsheet `#534` already has `node_current_v2`, `alerts_v2`, `risk_map_v2`, and `dashboard_v2` tabs. The new direction is to integrate these tabs into the existing lightweight migration flow instead of creating a separate system.

## Updated files

- `analysis/2026-05-31_534_sheet_v2_integration_plan.md`
- `analysis/latest_handoff.md`

## Key findings

1. Keep legacy tabs such as `管理表たたき`, history tabs, OCR logs, pact tabs, and safe-time tabs read-only during migration.
2. Treat `node_current_v2` as the sheet-facing normalized form of `node_status.json`.
3. Generate `alerts_v2` and `risk_map_v2` from `node_current_v2` / `node_status.json`; do not hand-maintain them as independent sources.
4. Keep `dashboard_v2` as a view layer only, so it does not become another source of truth.
5. For V2 risk scoring, use `server_side`: `534=self`, `509/440/511=ally`, any other resolved server as `enemy`, unresolved owner server as `unknown`.

## Current risks

1. Applying `enemy = all non-ally` before resolving `owner_server` can overclassify unknown owners.
2. Heavy spreadsheet formulas, especially volatile time formulas or full-column array formulas, may recreate the current performance issue.
3. Manual edits in `node_current_v2` can diverge from `管理表たたき` unless a clear override policy is added.

## Recommended next actions

1. Add a local generator that writes `node_current_v2.csv`, `alerts_v2.csv`, and `risk_map_v2.csv` from `node_status.json`.
2. Validate row counts and alert/risk counts locally before any Google Sheets write-back.
3. Only after human approval, paste or write the generated V2 CSVs into Google Sheets.

## Questions for ChatGPT

1. Is the `server_side` rule sufficient for the first commander dashboard?
2. Should `node_current_v2` allow manual override columns, or should all overrides stay in the old source tabs for now?
3. Which dashboard block should be shown first to R4/R5: critical risks, destroyed cities, or safe-time missing nodes?

## 2026-05-30 Sheet refresh timeout hardening

## Context

`マップ最新化` 押下時に `ERROR: The read operation timed out` が出た。更新API自体には到達していたが、Google Sheets CSV読み込みの30秒タイムアウトで失敗していた。

## Updated files

- `tools/invasion_strategy_os/invasion_strategy_os.py`
- `tools/invasion_strategy_os/interactive_server.py`
- `tools/invasion_strategy_os/config.google_full_map.json`
- `sample_output/map.html`
- `analysis/latest_handoff.md`

## Key findings

1. `interactive_server.py` が起動していれば、`マップ最新化` は `invasion_strategy_os.py --config config.google_full_map.json` を実行し、管理表たたきの安全期間も再取得・再計算する。
2. Google Sheets CSV取得は `timeout_seconds=90`, `retries=3`, `retry_delay_seconds=3` に変更した。
3. サーバー側の更新処理待ち時間を600秒に伸ばした。
4. 静的HTML側のエラー文を、サーバー未起動だけでなくGoogle Sheets読み込み失敗も示す内容に変更した。

## Notes

- ボタン更新で反映される安全期間は、Google Sheetsから再取得できた場合の最新値。Google側がタイムアウトした場合は、更新前の `map.html/state.json` のままになる。

## 2026-05-30 Server-based color assignment update

## Context

ノード色を現在位置のエリアではなく、所有連盟の所属サーバーで固定する方針に寄せた。#534 は青、#509/#440/#511 は緑、#503/#480/#523/#476 は赤。

## Updated files

- `tools/invasion_strategy_os/invasion_strategy_os.py`
- `sample_output/state.json`
- `sample_output/briefing_input.json`
- `sample_output/map.html`
- `analysis/latest_handoff.md`

## Key findings

1. 所有者名のサーバー接頭辞、またはExcel戦力表の所属サーバーが取れる場合は、それを最優先して色を決めるようにした。
2. 戦力表にない連盟だけ、従来どおり出現エリアから所属サーバーを推定する。
3. 例: `nO9`/`JDX`/`sbM` は他エリアにいても #534所属なので青、`BAJ`/`TaW`/`GcC` は #440所属なので緑、`fzn`/`Stj`/`Lghs` は #503所属なので赤。

## Notes

- Google Sheets再取得ではなく、既存ローカル `state.json` を元に再生成した。シート最新値は次回の `マップ最新化` で反映する。

## 2026-05-30 Enemy color inference update

## Context

敵サーバーは #503/#480/#523/#476 であるため、敵エリア由来の所有連盟が同数判定で ally 側に寄って赤くならないケースを補正した。

## Updated files

- `tools/invasion_strategy_os/invasion_strategy_os.py`
- `sample_output/state.json`
- `sample_output/briefing_input.json`
- `sample_output/map.html`
- `analysis/latest_handoff.md`

## Key findings

1. 所有連盟の所属推定で、出現数が同数の場合は `self > enemy > ally` の優先順にした。
2. #534側に明確に多く出る所有者は従来通り self、#509/#440/#511側に明確に多く出る所有者は ally のまま。
3. 例として `fzn` は #503 と #509 が同数だったため、以前は ally 側へ寄っていたが、今回 enemy に補正された。

## Notes

- Google Sheets再取得ではなく、既存ローカル `state.json` を元に再生成した。シート最新値は次回の `マップ最新化` で反映する。

## 2026-05-30 #534 attack forecast and server-day battle window update

## Context

Phase3の汎用TOPボタンを前面から外し、#534連盟向けの実用ボタンを中心にした。あわせて、ゲームサーバー時間がJSTより11時間遅い前提に合わせ、水曜/土曜の戦闘日をJST 11:00から翌日10:59として扱うようにした。

## Updated files

- `tools/invasion_strategy_os/config.google_full_map.json`
- `tools/invasion_strategy_os/simulation.py`
- `tools/invasion_strategy_os/invasion_strategy_os.py`
- `sample_output/state.json`
- `sample_output/briefing_input.json`
- `sample_output/map.html`
- `analysis/latest_handoff.md`

## Key findings

1. UIから `Phase3防衛TOP` などの汎用TOPボタンを外し、`#534連盟侵攻リスク`、`#534連盟攻撃予測`、`#534連盟協定込みリスク` を中心にした。
2. `server_534_attack_options` を追加し、#534所属連盟の漁場から攻撃可能な敵/未取得拠点を抽出するようにした。
3. 水曜/土曜サーバー日中だけ、#534所属連盟の漁場に隣接する敵都市を都市破壊候補として `server_534_attack_options` に含める。
4. 戦闘時間はJST基準で `水曜11:00-木曜10:59`、`土曜11:00-日曜10:59` として判定する。

## Notes

- 通常の接続グラフ自体は常時の都市通行エッジとしては扱わない。都市破壊可能時間だけ、攻撃候補として都市隣接を出す。
- Google Sheets の再取得はタイムアウトしたため、この更新の `sample_output` は既存ローカル `state.json` を元に新しいシミュレーション/UIを再生成した。シート最新値の取り込みは次回 `マップ最新化` または再生成時に行う。

## 2026-05-30 Pact-aware invasion prediction update

## Context

LastWar S6 strategy OS に `連盟協定` シートを読み込む協定込み侵攻予測を追加した。通常の地図エッジは変更せず、協定は Phase3 ルールエンジン上の「敵が一段先に使える可能性があるアクセス」として評価する。

## Updated files

- `tools/invasion_strategy_os/config.google_full_map.json`
- `tools/invasion_strategy_os/invasion_strategy_os.py`
- `tools/invasion_strategy_os/simulation.py`
- `sample_output/state.json`
- `sample_output/briefing_input.json`
- `sample_output/map.html`
- `analysis/latest_handoff.md`

## Key findings

1. `連盟協定` の有効協定を `state.json.pacts` に圧縮して出力するようにした。
2. Phase3 に `pact_threat_options` を追加し、敵連盟が協定先の漁場から味方/未取得側へ接続し得る候補を抽出するようにした。
3. UI に `協定込み敵侵攻予測` ボタンを追加し、候補エッジを赤系で強調できるようにした。
4. `briefing_input.json` に `top_pact_threats` を追加し、将来の GPT ブリーフィングで協定込みリスクだけを渡せるようにした。

## Notes

- 2026-05-30 の再生成では有効協定18件、協定込み敵侵攻候補19件、ブリーフィング上位10件を確認。
- 協定は一段先の投影のみ。協定の連鎖はまだ評価していない。
- 安全期間は協定行の `安全期間（現地時間）` に `15:00-16:00` のような時刻範囲がある場合だけ、スコアを弱める。

## 2026-05-30 #534 alliance-group invasion risk update

## Context

味方グループ全体の侵攻リスクとは別に、#534所属連盟の保有拠点を対象にした侵攻リスク表示を追加した。対象は JDX 単独ではなく、`self` 判定される #534連盟全体。

## Updated files

- `tools/invasion_strategy_os/invasion_strategy_os.py`
- `tools/invasion_strategy_os/simulation.py`
- `sample_output/state.json`
- `sample_output/briefing_input.json`
- `sample_output/map.html`
- `analysis/latest_handoff.md`

## Key findings

1. Phase3 に `server_534_risk_watchlist` を追加し、#534所属連盟の保有拠点のみの侵攻リスクを抽出できるようにした。
2. UI に `#534連盟侵攻リスク` と `#534連盟協定込みリスク` ボタンを追加した。
3. `briefing_input.json` に `server_534_risk_watchlist` と `top_server_534_pact_threats` を追加した。

## Notes

- 2026-05-30 の再生成では `server_534_risk_watchlist` は30件。
- `server_534_enemy_threat_options` は30件。
- `server_534_pact_threat_options` は0件。現時点の協定データでは、協定経由だけで #534所属連盟の保有拠点へ新しく届く候補は出ていない。
- UI の `#534連盟協定込みリスク` は、空になりやすい純粋な協定経由候補ではなく、`server_534_pact_aware_risk_watchlist` を表示する。これは #534所属連盟の通常侵攻リスクに協定経由アクセス要素を加味した一覧。

## Date

2026-05-30

## Context

Dropbox のS6ゲーム内ルールスクショフォルダから、ゲーム内の前哨基地争奪戦ルール/戦場情報スクショ5枚と、友好連盟/盟約スクショ2枚をS6リポジトリへ取り込んだ。

今回の目的は、GitHub上でChatGPTが参照できる形で、前哨基地争奪戦と盟約の最新ゲーム内表示を証拠画像として残し、既存のルール整理を補強すること。

## Updated files

- `screenshots/selected/game_rules_2026-05-30/game_rules_2026-05-30_095829.png`
- `screenshots/selected/game_rules_2026-05-30/game_rules_2026-05-30_095846.png`
- `screenshots/selected/game_rules_2026-05-30/game_rules_2026-05-30_095855.png`
- `screenshots/selected/game_rules_2026-05-30/game_rules_2026-05-30_095905.png`
- `screenshots/selected/game_rules_2026-05-30/game_rules_2026-05-30_095922.png`
- `screenshots/selected/game_rules_2026-05-30/game_rules_2026-05-30_img7957.png`
- `screenshots/selected/game_rules_2026-05-30/game_rules_2026-05-30_img7958.png`
- `research/source_log.md`
- `docs/season6_mechanics.md`
- `analysis/latest_handoff.md`

## Key findings

1. 2026-05-30時点のゲーム内表示では、前哨基地争奪戦の戦場情報タブに #440/#476/#509/#480/#511/#503/#534/#523 が表示され、見えている範囲では前哨基地枠は未配置だった。
2. 戦場情報タブには `間もなく 戦闘開始` と約 `11d 14:01` のカウントダウンが表示されていた。スクショ時点からは2026-06-11 0時前後の可能性があるが、サーバー時間とイベントカレンダーで再確認が必要。
3. 前哨基地建設ルールは、既存記録どおり「大統領が配置」「配置後は位置変更不可」「該当戦域の連盟が建設」「建設完了後は本戦域全連盟の領土扱い」「建設貢献1位が領主」。
4. ポイント報酬は、前哨基地/大砲台での撃破、汚染地域での撃破/戦死、前哨基地駐留、基地耐久削り、ランダム移設誘発、訓練/治療短縮が得点源として表示されていた。
5. #534 `[JDX]` と #509 `[FHX]` の友好連盟/盟約成功画面を確認。盟約締結後は双方に72時間の締結クールダウンが入り、その間は新規盟約を締結できない。水曜と土曜も締結不可。
6. 盟約は「双方の領土が常に隣接している」ことが条件として表示され、条件を満たせなくなると友好関係は自動解除される。

## Current risks

1. カウントダウンから推測した開始日時は確定扱いにしない。ゲーム内イベントカレンダーとサーバー時間で絶対日時に変換する必要がある。
2. 画像では表示範囲外の下部情報や詳細報酬が一部未確認。追加スクショがあれば追記する。
3. 配置権、他戦域による建設貢献、所有条件は既存メモでも未確定要素が残るため、実際の配置/建設画面で確認する。
4. 盟約切替や中央#8061支援は、72時間CD、水曜/土曜不可、隣接維持を無視すると計画が破綻する。

## Recommended next actions

1. 前哨基地争奪戦のイベントカレンダー画面をスクショし、開始/終了時刻をサーバー時間とJSTで記録する。
2. #534向けに、前哨基地候補地、建設貢献担当、駐留/大砲台担当、ランダム移設誘発狙いの攻撃班を分けた作戦メモを作る。
3. #534-JDX と #509-FHX の中央#8061隣接を、盟約維持条件として地図/管理表に明示する。
4. 追加のルール画像が出たら、同じ `screenshots/selected/game_rules_2026-05-30/` または日付別フォルダに入れ、`research/source_log.md` と `docs/season6_mechanics.md` を更新する。

## Questions for ChatGPT

1. 前哨基地配置候補を#534単独防衛、#509連携、#476遅滞、聖所/議事堂参加権のどの軸で優先すべきか。
2. 個人ポイント400kを狙う場合、駐留、撃破、ランダム移設誘発、訓練/治療短縮のどれを主軸にするべきか。
3. 72時間CDを前提に、JDX-FHX盟約をいつ維持し、いつ切り替えるべきか。
4. 前哨基地戦の集合指示文を幹部向け/一般連盟員向けに分けるなら、どの注意点を先に出すべきか。

## Notes

- 元画像は Dropbox 側に残し、GitHubには選別済み画像のみ追加した。
- 既存の未追跡ファイル `jdx_run_note_latest.md` と `s6powerrank_8server_power_2026-05-10_en.xlsx` は今回の作業対象外。

## 2026-05-31 R4/R5 review map bottom fix

## Context

R4/R5 review spreadsheet `#534_R4R5レビュー_2026-05-31` の `map_review_v2` で、下部に `#REF!` が残っていた。原因は `map_review_raw_v2` の `IMPORTRANGE` が `全体マップたたき!A1:DU120` までで止まっていた一方、コピー元の全体マップは135行構成だったこと。

## Updated files

- `analysis/latest_handoff.md`

## Key findings

1. `map_review_v2!A121:DU135` に古い参照式由来の `#REF!` が残っていた。
2. `map_review_raw_v2` の取り込み範囲を `全体マップたたき!A1:DU135` に拡張した。
3. `map_review_raw_v2` から `map_review_v2` へ `A1:DU135` を値貼り直しした。
4. 連盟名色分けと破壊セル背景グレーの条件付き書式を `A1:DU135` まで拡張した。

## Notes

- 本番 `#534` スプレッドシートには書き込んでいない。
- 更新対象はレビュー用スプレッドシートのみ。
- 下部サンプル `A121:H135`, `AP121:AW135`, `CE121:CL135` で `#REF!` が消えていることを確認済み。

## 2026-05-31 R4/R5 review sheet manual tab

## Context

R4/R5 review spreadsheet `#534_R4R5レビュー_2026-05-31` を当面は本番 `#534` と分けて運用するため、レビュー用シート内に `manual` タブを追加した。

## Updated files

- `analysis/latest_handoff.md`

## External output

- Google Sheets: `https://docs.google.com/spreadsheets/d/1PEU2O5DWGpC_vuaSkTCl1y6AzQ1QXLdQlKOgAD2ifb4/edit`

## Key findings

1. `manual` タブを追加し、見る順番、注意事項、定期再生成手順、マップ更新、データ整備、禁止事項を記載した。
2. 定期運用手順は、ローカルCSV/Markdown生成を先に行い、レビュー用Google Sheetだけを更新する流れにした。
3. READMEにも `manual` 追加と、レビュー用シートには全量 `node_current_v2` / `risk_map_v2` / `alerts_v2` を入れない方針を追記した。

## Recommended next actions

1. 定期再生成時は `manual` の手順に従い、まずローカルCSV/Markdownを更新する。
2. 本番 `#534` には自動書込せず、レビュー用シートだけを更新する。
3. 将来、更新頻度が上がる場合はレビュー用Google Sheet更新処理だけをスクリプト化する。

## 2026-05-31 R4/R5 review sheet Japanese cell labels

## Context

Review spreadsheet tab names can remain English, but R4/R5-facing cell labels should be readable in Japanese.

## Updated files

- `analysis/latest_handoff.md`

## External output

- Google Sheets: `https://docs.google.com/spreadsheets/d/1PEU2O5DWGpC_vuaSkTCl1y6AzQ1QXLdQlKOgAD2ifb4/edit`

## Key findings

1. Kept tab names in English.
2. Changed visible header cells in `manual`, `briefing`, `dashboard`, `self_defense_edges`, `self_attack_edges`, `ally_coordination`, `map_check_queue`, `critical_534`, and `alliance_audit` to Japanese labels.
3. Left CSV filenames and some machine-oriented values as-is where they help trace the generated source files.
4. Added README notes that visible cells are Japanese while sheet names remain English.

## Notes

- This was applied only to the review spreadsheet.
- Production `#534` was not written to.

## 2026-05-31 V2 pipeline rerun after management table update

## Context

Ran the local Python V2 generation sequence against the current production `#534` `管理表たたき` CSV export. This was a local regeneration only; Google Sheets review tabs were not refreshed in this step.

## Updated files

- `sample_output/sheet_migration/map_nodes.csv`
- `sample_output/sheet_migration/ownership_current.csv`
- `sample_output/sheet_migration/node_status.json`
- `sample_output/sheet_migration/unmatched_owners.csv`
- `sample_output/sheet_migration/pacts_candidates.csv`
- `sample_output/sheet_migration/*_v2.csv`
- `analysis/commander_review_2026-05-31.md`
- `analysis/alliance_side_audit_2026-05-31.md`
- `analysis/r4_r5_briefing_2026-05-31.md`
- `analysis/latest_handoff.md`

## Commands run

```powershell
.\.venv\Scripts\python.exe tools\invasion_strategy_os\migrate_534_sheet_mvp.py --input "<#534 管理表たたき CSV export URL>"
.\.venv\Scripts\python.exe tools\invasion_strategy_os\build_node_status_mvp.py
.\.venv\Scripts\python.exe tools\invasion_strategy_os\report_unmatched_owners_mvp.py
.\.venv\Scripts\python.exe tools\invasion_strategy_os\build_sheet_v2_outputs.py
.\.venv\Scripts\python.exe tools\invasion_strategy_os\build_alliance_side_audit.py
.\.venv\Scripts\python.exe tools\invasion_strategy_os\build_r4_r5_briefing.py
```

## Key findings

1. `map_nodes_rows=2168`, `ownership_current_rows=2168`, duplicate node IDs `0`.
2. `destroyed_count=109`, up from the earlier 52-row snapshot.
3. `node_current_v2 rows=2168`, `alerts_v2 rows=1926`, `risk_map_v2 rows=2168`.
4. Risk counts are `critical=111`, `high=167`, `mid=806`, `low=1084`.
5. Commander outputs: `top_critical_risks_534_v2 rows=8`, `top_enemy_invasion_candidates_v2 rows=30`, `top_server_534_attack_targets_v2 rows=30`.
6. Edge classification: self attack `5`, ally attack `3`, unknown attack `25`; self defense `5`, ally defense `5`, unknown defense `23`.
7. `city_destroy_enabled=FALSE`, so city destruction candidates should be treated as outside the active window.
8. Alliance audit still resolves `SHA`, `nO9`, `JDX`, and `4tH` as `server:534, side:self, risk:none`.

## Notes

- The first CSV export run required network access outside the sandbox.
- Review Google Sheet refresh is still a separate step.
- Production `#534` was read only and was not written to.

## 2026-05-31 protection notice sheet scaffold

## Context

Added protection-operation tabs to the R4/R5 review spreadsheet. The intent is not GPT export, but a sheet structure Codex can use to reason about A/B line fishery protection punches and a concise notice table that can be shared with the actual executors.

## Updated files

- `analysis/latest_handoff.md`

## External output

- Google Sheets: `https://docs.google.com/spreadsheets/d/1PEU2O5DWGpC_vuaSkTCl1y6AzQ1QXLdQlKOgAD2ifb4/edit`

## Added tabs

- `protection_rules_v2`
- `protection_targets_v2`
- `protection_source_pool_v2`
- `protection_candidates_v2`
- `protection_notice_v2`
- `protection_result_log_v2`

## Key findings

1. Tab names remain English, but visible cells are Japanese.
2. `protection_notice_v2` is the main executor-facing sheet. It includes A-line and B-line template rows plus a copyable notice text block.
3. `protection_rules_v2` records the fixed assumptions: A-line aims for next battle-day 7:00 release, B-line aims for next battle-day 23:00 release, and 15:00-16:00 JST is a no-action safe time.
4. `protection_targets_v2`, `protection_source_pool_v2`, and `protection_candidates_v2` are staff-side planning tables.
5. `protection_result_log_v2` is for execution time, result, protection display, and screenshot/link logging.

## Notes

- Production `#534` was not written to.
- The next step is to populate `protection_targets_v2` from the current A/B uppercase fishery rows, then derive candidate punch sources.

## 2026-05-31 protection plan calculated from current management table

## Context

Calculated A/B uppercase fishery protection-punch targets from the current `管理表たたき`-derived `node_current_v2.csv` and `state.json` adjacency. Updated the R4/R5 review spreadsheet, not production `#534`.

## Updated files

- `tools/invasion_strategy_os/build_protection_v2_outputs.py`
- `sample_output/sheet_migration/protection_targets_v2.csv`
- `sample_output/sheet_migration/protection_source_pool_v2.csv`
- `sample_output/sheet_migration/protection_candidates_v2.csv`
- `sample_output/sheet_migration/protection_notice_v2.csv`
- `analysis/latest_handoff.md`

## External output

- Google Sheets: `https://docs.google.com/spreadsheets/d/1PEU2O5DWGpC_vuaSkTCl1y6AzQ1QXLdQlKOgAD2ifb4/edit`

## Key findings

1. A/B uppercase fishery rows checked: `176`.
2. Blue-owned protection targets: `23` total, split into A-line `12` and B-line `11`.
3. Source pool: `39` adjacent blue-owned candidate source nodes.
4. Candidate edges: `59` target/source adjacent combinations.
5. `protection_notice_v2` was updated with 23 executor-facing rows.
6. `protection_targets_v2` was updated with the 23 blue-owned A/B fishery targets.
7. `protection_candidates_v2` and `protection_source_pool_v2` currently show summary rows; full detail is in the local CSVs.

## Assumptions

- Blue alliances are treated as #534 operation candidates based on the review map color assignment.
- Green alliances are excluded as overseas/ally operation targets for this workflow.
- Red alliances are excluded as enemy candidates.
- Same-alliance punch sources are excluded.
- Pact/盟約 and same-day acquisition limit remain human checks, not automatic approvals.

## Notes

- The generated notice is a candidate execution notice, not an order.
- Production `#534` was not written to.
