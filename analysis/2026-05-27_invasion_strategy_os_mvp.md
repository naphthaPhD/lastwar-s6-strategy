# LastWar invasion strategy OS MVP

## 1. Executive summary

Built a first MVP for a strategy-support graph system that reads board state data, generates a `networkx` graph, extracts CHOKE candidates, and writes `pyvis` HTML plus JSON output. This is a decision-support tool, not gameplay automation.

## 2. Context

Date: 2026-05-27

Purpose: provide a repeatable daily workflow for current-board visualization, connection analysis, collapse-risk review, CHOKE extraction, and isolated-node detection.

Input target: Google Sheets or CSV export. The MVP has a replaceable source layer so the live board sheet can be wired by spreadsheet id and gid.

## 3. Key facts

- Added the MVP under `tools/invasion_strategy_os/`.
- Added CSV and Google Sheets CSV-export loading.
- Added `config.google_history_534.json` for the first #534-only live test.
- Added `config.google_full_map.json` for the current full-map live test.
- Added node and edge structures with `id`, `name`, `type`, `owner`, `protect_until`, `x`, `y`, `importance`, `from`, `to`, and `weight`.
- Added JST protection-timer handling.
- Added graph analysis for connected components, articulation points, shortest path, degree centrality, and betweenness centrality.
- The current full-map output reads the management-table sheet, includes the central area, and contains 2,166 nodes with 5,412 coordinate-rule tactical edges.
- Central area typing follows the Cpt Hedgehog Season 6 reference-map pattern plus the commander adjustment: 208 central fishery nodes are connected by 636 adjacent central-fishery edges, 188 central altar nodes are isolated, and the 2x2 center is represented by one large isolated `祖霊神殿` node.
- The outer area placement is clockwise from the upper-left: `#534`, `#509`, `#503`, `#480`, `#440`, `#511`, `#523`, `#476`.
- Trade-post nodes are displayed but intentionally left unconnected.
- Fishery nodes are displayed larger than city nodes, while central-area fishery nodes are displayed smaller than outer fisheries.
- The HTML map can toggle labels between coordinates and alliance names at the same node-center position. In alliance-name mode, trade posts are always labeled `交易地`.
- The HTML map can reset moved nodes to the generated layout with `位置リセット`.
- The HTML map can highlight tactical edges: selecting a fishery highlights all connected edges, `境界強調` highlights #534-side fishery to enemy-side fishery edges plus enemy-side fishery to unowned fishery edges, `境界+内側` extends that view to the #534-side self-to-self fishery edges touching #534/enemy boundary fisheries, `ルート選択` highlights all equal-length shortest-route edges between two selected nodes, and `強調解除` / `ルート解除` clear edge highlighting.
- Default generated-map edges are fixed at width `1`, including outer-to-central edges; only interactive highlights use thicker lines.
- The HTML map can refresh from the latest `管理表たたき` sheet with `マップ最新化` when the local interactive server is running.
- Strategic colors are based on ownership from `管理表たたき`: #534-side owners blue, #509/#440/#511-side owners green, enemy-side owners red, and unowned nodes white. Owners with server-number prefixes such as `476B` are classified by that prefix even when they occupy another area.
- Edge rules are tactical and coordinate-based, not pure distance: fisheries connect to adjacent fisheries in 8 directions unless the diagonal crosses a city/trade-post cell, cities connect only to their four surrounding fisheries, destroyed cities are isolated, outer-area fisheries connect to nearby central fisheries with a small coordinate tolerance, city-city edges are blocked, trade posts remain isolated and are never treated as cities, and altar/temple nodes are isolated.
- Fishery nodes use circle styling and smaller in-node label text so alliance-name labels fit better; central fishery node size is reduced to 14.
- The full-map HTML applies display-only gaps between area blocks and includes a fixed legend for strategic colors, gray destroyed-city nodes, and red/yellow protection borders. The current display gap is 90, reducing inter-area and outer-to-central edge spans compared with the earlier 180 gap.
- The full-map view has a fixed click information panel using management-table fields, so alliance/status/protection data is easier to inspect.
- Added an initial local interactive-map server prototype for search, sheet refresh, and local manual owner/status/memo overrides.

## 4. Timeline

- Created `tools/invasion_strategy_os/invasion_strategy_os.py`.
- Created sample CSV inputs for smoke testing only.
- Added `tools/invasion_strategy_os/README.md` and `requirements.txt`.
- Generated `sample_output/map.html` and `sample_output/state.json`.
- Updated `.gitignore` to allowlist only this durable tool directory under `tools/`.
- Switched full-map input to the management-table sheet for more direct ownership/type/status data.
- Adjusted central-area type classification and edge derivation from the Cpt Hedgehog Season 6 reference map.
- Added generated-HTML edge highlighting for selected fisheries and #534-side versus enemy fishery borders.
- Added a generated-map refresh button backed by the local interactive server refresh API.
- Added generated-map shortest-route highlighting with two-click route selection.

## 5. Interpretation

This MVP should be used as a bridge between the current Google Sheets operational map and later GPT/API analysis. The immediate value is not tactical automation; it is a repeatable way to convert the current map into graph evidence that commanders can review.

The current full-map output is now useful for visual review across the outer 8 areas and the central area. The CHOKE result is still provisional because explicit game-rule adjacency is not yet modeled.

Central-area altar ownership should not be treated as movement adjacency. The current graph therefore displays central altar/temple nodes while excluding them from edge derivation.

## 6. Risks

- The management-table sheet does not expose explicit adjacency. The current live graph derives provisional distance edges from coordinates, so CHOKE results must not be treated as confirmed game adjacency.
- CHOKE candidates are graph evidence, not automatic orders; game rules, protection windows, alliance pact state, and actual attack eligibility must still be checked.
- Diagonal adjacency and pact-assisted adjacency need explicit modeling rules before live operational use.
- The 3x3 area offsets and central reference typing are derived from external map references. If those references change, the config and central typing helper should be updated.

## 7. Recommended actions

1. Add or export a live adjacency table from the operational Google Sheet.
2. Run the MVP after each meaningful map update and review `critical_nodes` in `sample_output/state.json`.
3. Compare CHOKE candidates against the commander map before issuing any R4/R5 order.
4. Continue adjusting the full-map visual density as commander review reveals crowded areas.
5. Test the local interactive prototype before deciding whether manual overrides should write back to Google Sheets.

## 8. Unknowns

- Whether diagonal adjacency should be represented as normal edges, lower-weight edges, or rule-dependent edges.
- Whether pact territory should be modeled as direct edges or as a scenario layer.
- Whether trade-post nodes should remain isolated in every scenario or only in the default tactical layer.
- Whether central altar subtypes need to be preserved separately or can remain grouped as `祭壇` for graph analysis.

## 9. Files referenced

- `.gitignore`
- `C:/Users/kitazaki/FIT Dropbox/訓北﨑/lastwar/S6/IMG_1219.PNG` (visual reference only; not committed)
- `C:/Users/kitazaki/FIT Dropbox/訓北﨑/lastwar/S6/IMG_1220.PNG` (visual reference only; not committed)
- `tools/invasion_strategy_os/invasion_strategy_os.py`
- `tools/invasion_strategy_os/config.example.json`
- `tools/invasion_strategy_os/config.google_history_534.json`
- `tools/invasion_strategy_os/config.google_full_map.json`
- `tools/invasion_strategy_os/README.md`
- `tools/invasion_strategy_os/interactive_app.html`
- `tools/invasion_strategy_os/interactive_server.py`
- `tools/invasion_strategy_os/requirements.txt`
- `tools/invasion_strategy_os/sample_nodes.csv`
- `tools/invasion_strategy_os/sample_edges.csv`
- `sample_output/map.html`
- `sample_output/state.json`
