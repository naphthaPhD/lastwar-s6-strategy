# Handoff summary

## Date

2026-05-27

## Context

Built the first MVP of a LastWar invasion strategy OS for current-board visualization and connection analysis. The goal is strategic decision support: read map state from Google Sheets or CSV, generate a graph, extract CHOKE candidates, and output HTML plus JSON for review.

This does not automate gameplay. It is a repeatable analysis and visualization pipeline connected to the live Google Sheets operational map.

The current live output reads `管理表たたき` from spreadsheet `＃534`, expands it to the full outer map using the Google Sheets full-map layout, and excludes the central area for now.

## Updated files

- `.gitignore`
- `analysis/2026-05-27_invasion_strategy_os_mvp.md`
- `analysis/latest_handoff.md`
- `tools/invasion_strategy_os/invasion_strategy_os.py`
- `tools/invasion_strategy_os/config.example.json`
- `tools/invasion_strategy_os/config.google_history_534.json`
- `tools/invasion_strategy_os/config.google_full_map.json`
- `tools/invasion_strategy_os/README.md`
- `tools/invasion_strategy_os/requirements.txt`
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
7. The Google Sheets full-map output currently contains all 8 outer areas from `管理表たたき`: 1,768 nodes, 6,436 provisional distance edges, 81 connected components, and 0 CHOKE nodes under the current distance-edge model.
8. The 81 components are expected in this model: 80 `交易地` nodes are intentionally isolated, and the remaining connected component is the outer-ring map.
9. Lowercase coordinate letters are normalized to `都市`; uppercase coordinate letters are normalized to `漁場`; the central area is excluded.
10. The full-map HTML uses smaller nodes and labels to create more visible spacing between cities and fisheries.
11. Clicking a node now opens a fixed information panel with management-table fields, instead of relying on the small browser hover tooltip.
12. The outer area placement is now clockwise from the upper-left: `#534`, `#509`, `#503`, `#480`, `#440`, `#511`, `#523`, `#476`.

## Current risks

1. `管理表たたき` does not expose explicit adjacency. The current live graph derives provisional distance edges from coordinates, so CHOKE results must not be treated as confirmed game adjacency.
2. CHOKE candidates are graph evidence, not automatic orders; game rules, protection windows, pact state, and attack eligibility must still be checked.
3. Diagonal adjacency and pact-assisted adjacency need explicit modeling rules before live operational use.
4. The 3x3 area offsets are derived from the Google Sheets full-map layout. If the sheet layout changes, `config.google_full_map.json` should be updated.

## Recommended next actions

1. Add a live node export tab to the operational Google Sheet with `id`, `name`, `type`, `owner`, `protect_until`, `x`, `y`, `importance`, and `adjacent`.
2. Add a live edge export tab only if adjacency is not stored in the node table.
3. Review `sample_output/state.json` first, then use `sample_output/map.html` for commander sharing.
4. For the current #534-only live test, run `.\.venv\Scripts\python.exe tools\invasion_strategy_os\invasion_strategy_os.py --config tools\invasion_strategy_os\config.google_history_534.json`.
5. For the current full outer-map live test, run `.\.venv\Scripts\python.exe tools\invasion_strategy_os\invasion_strategy_os.py --config tools\invasion_strategy_os\config.google_full_map.json`.

## Questions for ChatGPT

1. Should canonical node ids be grid ids, game coordinates, or combined ids?
2. Should diagonal adjacency be treated as normal, weighted, or scenario-dependent?
3. Should pact access be modeled as graph edges, temporary scenario edges, or a separate layer?
4. Which node types should count as major nodes for CHOKE scoring in Week 3?

## Notes

- Dependencies were installed into the existing local `.venv` for verification.
- The generated HTML is UTF-8 and uses local vis-network assets in `sample_output/lib/`.
- The in-app browser successfully rendered the live full outer-map Google Sheets output at `http://127.0.0.1:8000/sample_output/map.html`.
- The `tools/invasion_strategy_os/` directory was explicitly allowlisted in `.gitignore`; existing unrelated local `tools/` files remain ignored.
- Existing unrelated local changes were not touched.
