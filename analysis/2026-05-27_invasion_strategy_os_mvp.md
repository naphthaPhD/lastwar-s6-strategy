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
- Added `config.google_full_map.json` for the current full outer-map live test.
- Added node and edge structures with `id`, `name`, `type`, `owner`, `protect_until`, `x`, `y`, `importance`, `from`, `to`, and `weight`.
- Added JST protection-timer handling.
- Added graph analysis for connected components, articulation points, shortest path, degree centrality, and betweenness centrality.
- The full-map output now reads `管理表たたき`, includes the central area, and contains 2,168 nodes with 10,406 provisional distance edges.
- The outer area placement is clockwise from the upper-left: `#534`, `#509`, `#503`, `#480`, `#440`, `#511`, `#523`, `#476`.
- `交易地` nodes are displayed but intentionally left unconnected.
- Fishery nodes are now displayed larger than city nodes.
- The full-map view has a fixed click information panel using management-table fields, so alliance/status/protection data is easier to inspect.

## 4. Timeline

- Created `tools/invasion_strategy_os/invasion_strategy_os.py`.
- Created sample CSV inputs for smoke testing only.
- Added `tools/invasion_strategy_os/README.md` and `requirements.txt`.
- Generated `sample_output/map.html` and `sample_output/state.json`.
- Updated `.gitignore` to allowlist only this durable tool directory under `tools/`.
- Switched full-map input from `拠点履歴_座標` to `管理表たたき` for more direct ownership/type/status data.

## 5. Interpretation

This MVP should be used as a bridge between the current Google Sheets operational map and later GPT/API analysis. The immediate value is not tactical automation; it is a repeatable way to convert the current map into graph evidence that commanders can review.

The current full-map output is now useful for visual review across the outer 8 areas. The CHOKE result is still provisional because explicit game-rule adjacency is not yet modeled.

## 6. Risks

- `管理表たたき` does not expose explicit adjacency. The current live graph derives provisional distance edges from coordinates, so CHOKE results must not be treated as confirmed game adjacency.
- CHOKE candidates are graph evidence, not automatic orders; game rules, protection windows, alliance pact state, and actual attack eligibility must still be checked.
- Diagonal adjacency and pact-assisted adjacency need explicit modeling rules before live operational use.
- The 3x3 area offsets are derived from the Google Sheets full-map layout. If the sheet layout changes, `config.google_full_map.json` should be updated.

## 7. Recommended actions

1. Add or export a live adjacency table from the operational Google Sheet.
2. Run the MVP after each meaningful map update and review `critical_nodes` in `sample_output/state.json`.
3. Compare CHOKE candidates against the commander map before issuing any R4/R5 order.
4. Continue adjusting the full-map visual density as commander review reveals crowded areas.

## 8. Unknowns

- Whether diagonal adjacency should be represented as normal edges, lower-weight edges, or rule-dependent edges.
- Whether pact territory should be modeled as direct edges or as a scenario layer.
- Whether `交易地` should remain isolated in every scenario or only in the default tactical layer.

## 9. Files referenced

- `.gitignore`
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
