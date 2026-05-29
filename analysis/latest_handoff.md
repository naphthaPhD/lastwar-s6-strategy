# Handoff summary

## Date

2026-05-30

## Context

Built and iterated the first MVP of a LastWar Season 6 invasion strategy OS for current-board visualization and connection analysis. The tool reads the operational Google Sheet through CSV export, generates a graph, extracts CHOKE candidates, and outputs HTML plus JSON for review.

This does not automate gameplay. It is a repeatable analysis and visualization pipeline for commander review.

Latest update adds local Excel alliance-strength integration and the first simulation layer. The current full-map generation reads `s6powerrank_8server_power_2026-05-10_en.xlsx` sheet `Alliance Power`, attaches matching alliance ranking power to map nodes, exports a derived JSON ranking cache, and writes invasion/threat candidate lists to `sample_output/state.json`.

## Updated files

- `.gitignore`
- `analysis/2026-05-27_invasion_strategy_os_mvp.md`
- `analysis/latest_handoff.md`
- `tools/invasion_strategy_os/invasion_strategy_os.py`
- `tools/invasion_strategy_os/simulation.py`
- `tools/invasion_strategy_os/config.example.json`
- `tools/invasion_strategy_os/config.google_history_534.json`
- `tools/invasion_strategy_os/config.google_full_map.json`
- `tools/invasion_strategy_os/README.md`
- `tools/invasion_strategy_os/interactive_app.html`
- `tools/invasion_strategy_os/interactive_server.py`
- `tools/invasion_strategy_os/requirements.txt`
- `data/alliance_power_rankings_2026-05-10.json`
- `tools/invasion_strategy_os/sample_nodes.csv`
- `tools/invasion_strategy_os/sample_edges.csv`
- `sample_output/map.html`
- `sample_output/state.json`

## Key findings

1. The MVP can read CSV or Google Sheets CSV-export sources through a replaceable source layer.
2. The internal graph uses explicit Node and Edge structures matching the requested fields.
3. `networkx` analysis covers connected components, articulation points, shortest path, degree centrality, and betweenness centrality.
4. CHOKE candidates are extracted from articulation points and scored by importance, graph degree, betweenness, major-node split, and major-node isolation.
5. `sample_output/map.html` is generated with `pyvis`, owner-based node colors, importance-based size, edge display, click/hover node details, and protection-status border coloring.
6. HTML generation uses local vis-network assets under `sample_output/lib/`, avoiding the inline-script black-screen issue seen in the in-app browser.
7. The current full-map output contains the 8 outer areas plus central area: 2,166 nodes, 5,412 coordinate-rule tactical edges, and 0 CHOKE nodes under the current coordinate-edge model.
8. Central area typing now follows the Cpt Hedgehog Season 6 reference-map pattern plus the commander adjustment: 397 central nodes, 208 central fishery nodes, 188 central altar nodes, and one large `祖霊神殿` node replacing the 2x2 center.
9. Central fishery nodes are connected by distance edges; central altar/temple nodes are displayed but isolated. Verification after regeneration: 1,764 central fishery-related edges, 0 central altar edges, and 0 `祖霊神殿` edges.
10. Trade-post nodes are displayed but intentionally left unconnected.
11. Lowercase coordinate letters are normalized to city nodes; uppercase coordinate letters are normalized to fishery nodes.
12. The outer area placement is clockwise from the upper-left: `#534`, `#509`, `#503`, `#480`, `#440`, `#511`, `#523`, `#476`.
13. Fishery nodes are displayed larger than city nodes, but central-area fishery nodes are displayed smaller than outer fisheries to reduce central clutter.
14. The HTML map has a label toggle: coordinate labels by default, or alliance-name labels at the same node-center position. In alliance-name mode, trade posts are always labeled `交易地`.
15. Node colors are strategic colors from `管理表たたき` ownership: #534-side owners are blue, #509/#440/#511-side owners are green, enemy-side owners are red, and unowned nodes are white. Owners with server-number prefixes such as `476B` are classified by that prefix even when they occupy another area.
16. Edge rules are now tactical and coordinate-based: fisheries connect to adjacent fisheries in 8 directions unless the diagonal crosses a city/trade-post cell, cities connect only to their four surrounding fisheries, destroyed cities are isolated, trade posts remain isolated and are never treated as cities, and altar/temple nodes are isolated. Outer-area fisheries also connect to nearby central fisheries using the same adjacency intent with a small coordinate tolerance. Verification after regeneration: 5,624 edges, 2,740 fishery-fishery edges, 2,884 fishery-city edges, 0 destroyed-node edges, 0 city-city edges, 0 trade-post edges, and 0 altar/temple edges.
17. The HTML map has a `位置リセット` button that returns moved nodes to the generated layout.
18. Clicking a node opens a fixed information panel with management-table fields.
19. Fishery nodes now use circle styling and smaller in-node label text so alliance-name mode is easier to read; central fishery node size is reduced to 14.
20. The HTML map applies display-only gaps between the 3x3 area blocks; graph coordinates and edge derivation remain unchanged. The current display gap is 90, reducing inter-area and outer-to-central edge spans compared with the earlier 180 gap.
21. The HTML map includes a fixed legend explaining strategic colors, gray destroyed-city nodes, and red/yellow protection borders.
22. Added a first local interactive-map server skeleton for a cpt-hedge-style workflow: browser rendering from `state.json`, sheet refresh endpoint, and local manual overrides in `data/invasion_strategy_overrides.json`.
23. Added edge-highlight controls to the generated HTML map: selecting a fishery highlights its connected edges in cyan, `境界強調` highlights friendly-side (#534/#509/#440/#511 group) fishery to enemy-side fishery edges in orange and enemy-side fishery to unowned fishery edges in amber, `境界+内側` / `境界+内側+内側` / `境界+内側+内側+内側` additionally highlight edges from friendly/enemy boundary friendly-side fisheries into friendly-side or unowned fisheries for 1/2/3 interior steps in rose red, and `強調解除` resets edge styling. Current live data contains 82 self-enemy fishery boundary edges, 279 ally-enemy fishery boundary edges, 464 enemy-unowned fishery boundary edges, 166 boundary friendly fishery nodes, 322 one-step interior edges, 553 two-step interior edges, and 717 three-step interior edges. Example: `#534:D-13` is enemy, `#534:D-15` is self, `#534:D-17` is unowned, and `#534:D-15 -- #534:D-17` is included from the 1-step interior view onward.
24. Added a generated-map `マップ最新化` button. It calls the local `/api/refresh` endpoint, regenerates from the latest `管理表たたき` Google Sheet through `config.google_full_map.json`, and reloads the map. The interactive server now permits local CORS fallback from `127.0.0.1:8000` to `127.0.0.1:8010`.
25. Added generated-map shortest-route highlighting. `ルート選択` puts the map into two-click route mode; the first selected node is the start, the second selected node is the target, and all equal-length shortest-route fishery edges are shown with thick purple edges. Cities are excluded as transit nodes; if the selected target is a city, the route is drawn to the nearest fishery adjacent to that city. Route mode clears the normal yellow adjacent-edge selection highlight. `ルート解除` clears route/edge highlighting.
26. Default generated-map edge width is fixed at `1`, including outer-to-central edges; thicker lines are reserved for interactive highlights.
27. Local Excel alliance power integration is now wired through `config.google_full_map.json`. The parser reads `Alliance Power` rows from `s6powerrank_8server_power_2026-05-10_en.xlsx`; regenerated output matched JDX at 26.39B overall rank 13, 476A at 33.94B rank 1, 476B at 27.55B rank 8, FHX at 31.95B rank 2, and BAJ at 30.09B rank 3.
28. Node click details in `sample_output/map.html` now include alliance power, overall rank/server, and alliance name when the owner tag matches the ranking workbook.
29. `sample_output/state.json` now includes `alliance_power_rankings` with 287 alliance records and node-level `alliance_power` payloads for matched owners.
30. Added an initial `invasion_simulation` JSON block. It produces top-30 lists for `friendly_pressure_options`, `enemy_threat_options`, `friendly_expansion_options`, and `enemy_expansion_options` from fishery-to-fishery tactical edges, scored by alliance ranking power plus target importance.
31. Current regenerated simulation counts: 357 friendly/enemy fishery boundary edges, 165 boundary friendly fishery nodes, 109 one-step interior edges, 198 two-step interior edges, and 263 three-step interior edges under the current graph and owner data.
32. Added generated-map simulation highlight buttons: `敵侵攻予測`, `味方侵攻候補`, `敵未取得拡張`, and `味方未取得拡張`. These rank fishery-to-fishery candidates in-browser using alliance power plus target importance and highlight the top 30 edges.
33. Split route selection into two modes. `戦力無視ルート` keeps the current fishery-only shortest route behavior and ignores enemy power. `始点より低戦力通過` still avoids city transit, but permits transit through enemy fisheries only when that enemy alliance power is lower than the alliance power of the selected start node.
34. Added separate simulation score models: `attack_score_options`, `interdiction_score_options`, and `risk_avoidance_options`. Attack favors enemy boundary fisheries near enemy cities while penalizing stronger enemy pockets; interdiction favors enemy cities destroyable from adjacent friendly fisheries; risk avoidance flags high-power or dense enemy boundary areas.
35. Added generated-map `遮断候補` and `危険回避` buttons to highlight the corresponding score-model candidates.
36. Phase 3 separates the strategic rule engine into `tools/invasion_strategy_os/simulation.py`. `invasion_strategy_os.py` now builds the sheet/map/graph state, writes the same state shape used by `sample_output/state.json`, and delegates `invasion_simulation` scoring to the separated module.
37. The Phase 3 rule engine writes JSON score reasons and factor breakdowns for protection expiry, battle windows, capture-limit pressure, enemy adjacency, city-destruction reach, central connection value, and counterattack risk. GPT is not used in this engine.

## Current risks

1. The operational sheet does not expose explicit adjacency. The current live graph derives provisional distance edges from coordinates, so CHOKE results must not be treated as confirmed game adjacency.
2. CHOKE candidates are graph evidence, not automatic orders; game rules, protection windows, pact state, and attack eligibility must still be checked.
3. Diagonal adjacency and pact-assisted adjacency need explicit modeling rules before live operational use.
4. The 3x3 area offsets and central reference typing are derived from the Google Sheets full-map layout plus the Cpt Hedgehog Season 6 reference map. If either reference changes, update `config.google_full_map.json` and the central typing helper.
5. Alliance ranking power is a coarse proxy only. It does not account for live attendance, capture caps, protection windows, march timing, rally availability, or tactical city-destruction sequencing.
6. Current game-rule modeling covers map connectivity rules plus an initial Phase 3 scoring layer for protection expiry, battle windows, capture-limit pressure, enemy adjacency, city-destruction reach, central connection value, and counterattack risk. Capture-limit usage is still a proxy based on currently owned city/fishery nodes, and live player attendance, rally timing, and explicit current pact target are not solved yet.
7. Excel power file remains fixed-name input: `s6powerrank_8server_power_2026-05-10_en.xlsx`. Replacing that file and regenerating updates the derived cache and map output.

## Recommended next actions

1. Add a live node export tab to the operational Google Sheet with `id`, `name`, `type`, `owner`, `protect_until`, `x`, `y`, `importance`, and `adjacent`.
2. Add a live edge export tab only if adjacency is not stored in the node table.
3. Review `sample_output/state.json` first, then use `sample_output/map.html` for commander sharing.
4. For the current #534-only live test, run `.\.venv\Scripts\python.exe tools\invasion_strategy_os\invasion_strategy_os.py --config tools\invasion_strategy_os\config.google_history_534.json`.
5. For the current full-map live test, run `.\.venv\Scripts\python.exe tools\invasion_strategy_os\invasion_strategy_os.py --config tools\invasion_strategy_os\config.google_full_map.json`.
6. For refresh buttons and the local interactive prototype, run `.\.venv\Scripts\python.exe tools\invasion_strategy_os\interactive_server.py --port 8010`; then open either `http://127.0.0.1:8010/` or the generated map at `http://127.0.0.1:8010/sample_output/map.html`.
7. Review `sample_output/state.json` under `invasion_simulation.enemy_threat_options` and `friendly_pressure_options` as a first queue for commander review, then confirm protection/cap/pact constraints manually before treating any candidate as an order.

## Questions for ChatGPT

1. Should canonical node ids be grid ids, game coordinates, or combined ids?
2. Should diagonal adjacency be treated as normal, weighted, or scenario-dependent?
3. Should pact access be modeled as graph edges, temporary scenario edges, or a separate layer?
4. Which node types should count as major nodes for CHOKE scoring in Week 3?
5. Which Excel-derived fields beyond alliance ranking power should affect route/threat scoring?
6. Should pact state be represented as a config scenario, a sheet column, or a temporary graph layer?

## Notes

- Dependencies were installed into the existing local `.venv` for verification.
- The generated HTML is UTF-8 and uses local vis-network assets in `sample_output/lib/`.
- The in-app browser successfully rendered the regenerated full-map output at `http://127.0.0.1:8000/sample_output/map.html`.
- The in-app browser visually verified the new `境界強調` and `強調解除` buttons on the generated `sample_output/map.html`.
- The in-app browser visually verified `マップ最新化`: it called the local refresh API, regenerated from Google Sheets, and reloaded `sample_output/map.html` with a cache-busting URL.
- The in-app browser verified the generated route toolbar: `ルート選択` is visible and changes to `始点選択中`; node click handling changed to route mode for the first selected node.
- The latest generation succeeded with the current Google Sheet plus local Excel ranking workbook. Browser visual verification was attempted, but `127.0.0.1:8000` was not serving at that moment; JSON and generated HTML contents were verified directly instead.
- Latest route/simulation button update was regenerated and verified by generated HTML text checks. Browser file navigation was blocked by the browser security policy, so visual browser verification was not completed in this turn.
- Latest score-model update regenerated successfully after one Google Sheets CSV timeout retry. Verification found 30 attack candidates, 25 interdiction candidates, and 30 risk-avoidance candidates in `sample_output/state.json`.
- Visual reference screenshots supplied by the user for tactical map geometry: `C:/Users/kitazaki/FIT Dropbox/訓北﨑/lastwar/S6/IMG_1219.PNG` and `C:/Users/kitazaki/FIT Dropbox/訓北﨑/lastwar/S6/IMG_1220.PNG`. These were used as reference only and were not committed.
- The `tools/invasion_strategy_os/` directory is explicitly allowlisted in `.gitignore`; existing unrelated local `tools/` files remain ignored.
- Existing unrelated local changes were not touched.
