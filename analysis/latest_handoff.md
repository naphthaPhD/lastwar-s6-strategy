# Handoff summary

## Date

2026-05-27

## Context

Built the first MVP of a LastWar invasion strategy OS for current-board visualization and connection analysis. The goal is strategic decision support: read map state from Google Sheets or CSV, generate a graph, extract CHOKE candidates, and output HTML plus JSON for review.

This does not automate gameplay. It is a repeatable analysis and visualization pipeline that can later be connected to the live Google Sheets operational map.

Previous tactical map work remains in Google Sheets; this update adds a local Python tool that can consume exported node/edge state once the sheet has stable export ranges.

## Updated files

- `.gitignore`
- `analysis/2026-05-27_invasion_strategy_os_mvp.md`
- `analysis/latest_handoff.md`
- `tools/invasion_strategy_os/invasion_strategy_os.py`
- `tools/invasion_strategy_os/config.example.json`
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
7. The sample CSV is synthetic smoke-test data only. It is not a real board state and should not be used tactically.

## Current risks

1. The live Google Sheet still needs a stable node/edge export tab or conversion layer.
2. CHOKE candidates are graph evidence, not automatic orders; game rules, protection windows, pact state, and attack eligibility must still be checked.
3. Diagonal adjacency and pact-assisted adjacency need explicit modeling rules before live operational use.
4. Browser opening of the local `file://` HTML was blocked by Codex browser policy, so verification used script execution, JSON inspection, and static HTML checks instead.

## Recommended next actions

1. Add a live node export tab to the operational Google Sheet with `id`, `name`, `type`, `owner`, `protect_until`, `x`, `y`, `importance`, and `adjacent`.
2. Add a live edge export tab only if adjacency is not stored in the node table.
3. Point `tools/invasion_strategy_os/config.example.json` or a copied local config at the live sheet id and gid.
4. Run `.\.venv\Scripts\python.exe tools\invasion_strategy_os\invasion_strategy_os.py --config tools\invasion_strategy_os\config.example.json`.
5. Review `sample_output/state.json` first, then use `sample_output/map.html` for commander sharing.

## Questions for ChatGPT

1. Should canonical node ids be grid ids, game coordinates, or combined ids?
2. Should diagonal adjacency be treated as normal, weighted, or scenario-dependent?
3. Should pact access be modeled as graph edges, temporary scenario edges, or a separate layer?
4. Which node types should count as major nodes for CHOKE scoring in Week 3?

## Notes

- Dependencies were installed into the existing local `.venv` for verification.
- The generated HTML is UTF-8 and has no external CDN dependency for vis-network.
- The `tools/invasion_strategy_os/` directory was explicitly allowlisted in `.gitignore`; existing unrelated local `tools/` files remain ignored.
- Existing unrelated local changes were not touched.
