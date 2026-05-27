# Handoff summary

## Date

2026-05-27

## Context

Built the first MVP of a LastWar invasion strategy OS for current-board visualization and connection analysis. The goal is strategic decision support: read map state from Google Sheets or CSV, generate a graph, extract CHOKE candidates, and output HTML plus JSON for review.

This does not automate gameplay. It is a repeatable analysis and visualization pipeline that can later be connected to the live Google Sheets operational map.

Previous tactical map work remains in Google Sheets; this update adds a local Python tool that can consume exported node/edge state once the sheet has stable export ranges. A first live test now reads `拠点履歴_座標` from spreadsheet `＃534` and filters it to the `#534` area.

## Updated files

- `.gitignore`
- `analysis/2026-05-27_invasion_strategy_os_mvp.md`
- `analysis/latest_handoff.md`
- `tools/invasion_strategy_os/invasion_strategy_os.py`
- `tools/invasion_strategy_os/config.example.json`
- `tools/invasion_strategy_os/config.google_history_534.json`
- `tools/invasion_strategy_os/README.md`
- `tools/invasion_strategy_os/requirements.txt`
- `tools/invasion_strategy_os/sample_nodes.csv`
- `tools/invasion_strategy_os/sample_edges.csv`
- `sample_output/map.html`
- `sample_output/state.json`

## Key findings

1. The MVP can read CSV or Google Sheets CSV-export sources through a replaceable source layer.
2. The internal graph uses explicit Node and Edge structures matching the requested fields.
3. `networkx` analysis now covers connected components, articulation points, shortest path, degree centrality, and betweenness centrality.
4. CHOKE candidates are extracted from articulation points and scored by importance, graph degree, betweenness, major-node split, and major-node isolation.
5. `sample_output/state.json` currently reports three synthetic CHOKE candidates and one isolated synthetic node from the smoke-test fixture.
6. `sample_output/map.html` is generated with `pyvis`, owner-based node colors, importance-based size, edge display, click/hover node details, and protection-status border coloring.
7. After an initial black-screen test in the Codex in-app browser, HTML generation was changed to use local vis-network assets under `sample_output/lib/` instead of a giant inline script.
8. The sample CSV is synthetic smoke-test data only. It is not a real board state and should not be used tactically.
9. The Google Sheets live-test output currently contains `#534` area data from `拠点履歴_座標`: 221 nodes, 642 provisional distance edges, 1 connected component, and 0 CHOKE nodes under the current distance-edge model.

## Current risks

1. The live Google Sheet still needs a stable node/edge export tab or conversion layer.
2. CHOKE candidates are graph evidence, not automatic orders; game rules, protection windows, pact state, and attack eligibility must still be checked.
3. Diagonal adjacency and pact-assisted adjacency need explicit modeling rules before live operational use.
4. Browser opening of the local `file://` HTML was blocked by Codex browser policy, so verification used script execution, JSON inspection, and static HTML checks instead.
5. `拠点履歴_座標` does not expose explicit adjacency. The current live-test graph derives provisional same-area distance edges from coordinates, so CHOKE results must not be treated as confirmed game adjacency.

## Recommended next actions

1. Add a live node export tab to the operational Google Sheet with `id`, `name`, `type`, `owner`, `protect_until`, `x`, `y`, `importance`, and `adjacent`.
2. Add a live edge export tab only if adjacency is not stored in the node table.
3. Point `tools/invasion_strategy_os/config.example.json` or a copied local config at the live sheet id and gid.
4. Run `.\.venv\Scripts\python.exe tools\invasion_strategy_os\invasion_strategy_os.py --config tools\invasion_strategy_os\config.example.json`.
5. Review `sample_output/state.json` first, then use `sample_output/map.html` for commander sharing.
6. For the current live test, run `.\.venv\Scripts\python.exe tools\invasion_strategy_os\invasion_strategy_os.py --config tools\invasion_strategy_os\config.google_history_534.json`.

## Questions for ChatGPT

1. Should canonical node ids be grid ids, game coordinates, or combined ids?
2. Should diagonal adjacency be treated as normal, weighted, or scenario-dependent?
3. Should pact access be modeled as graph edges, temporary scenario edges, or a separate layer?
4. Which node types should count as major nodes for CHOKE scoring in Week 3?

## Notes

- Dependencies were installed into the existing local `.venv` for verification.
- The generated HTML is UTF-8 and uses local vis-network assets in `sample_output/lib/`, avoiding the inline-script black-screen issue seen in the in-app browser.
- The in-app browser successfully rendered the live `#534` Google Sheets output at `http://127.0.0.1:8000/sample_output/map.html`.
- The `tools/invasion_strategy_os/` directory was explicitly allowlisted in `.gitignore`; existing unrelated local `tools/` files remain ignored.
- Existing unrelated local changes were not touched.
