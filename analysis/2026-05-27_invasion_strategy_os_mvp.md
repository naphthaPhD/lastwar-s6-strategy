# LastWar invasion strategy OS MVP

## 1. Executive summary

Built a first MVP for a strategy-support graph system that reads board state data, generates a `networkx` graph, extracts CHOKE candidates, and writes `pyvis` HTML plus JSON output. This is a decision-support tool, not gameplay automation.

## 2. Context

Date: 2026-05-27

Purpose: provide a repeatable daily workflow for current-board visualization, connection analysis, collapse-risk review, CHOKE extraction, and isolated-node detection.

Input target: Google Sheets or CSV export. The MVP has a replaceable source layer so the live board sheet can be wired later by spreadsheet id and gid.

## 3. Key facts

- Added the MVP under `tools/invasion_strategy_os/`.
- Added CSV and Google Sheets CSV-export loading.
- Added `config.google_history_534.json` to read live `拠点履歴_座標` data from spreadsheet `＃534`.
- Added node and edge structures with `id`, `name`, `type`, `owner`, `protect_until`, `x`, `y`, `importance`, `from`, `to`, and `weight`.
- Added adjacency parsing from a node-table `adjacent` column.
- Added JST protection-timer handling.
- Added graph analysis for connected components, articulation points, shortest path, degree centrality, and betweenness centrality.
- Treats articulation points as CHOKE candidates.
- Adds stronger CHOKE reasons when major city/stronghold groups split, a major node is isolated, or route degree is narrow.
- Writes `sample_output/map.html` and `sample_output/state.json`.
- Generated HTML is UTF-8 and uses local vis-network assets under `sample_output/lib/`.
- The initial inline-script HTML produced a black screen in the Codex in-app browser; the local-asset output rendered correctly after reload.
- The first live `#534` output contains 221 nodes, 642 provisional distance edges, 1 connected component, and 0 CHOKE nodes under the current edge model.

## 4. Timeline

- Created `tools/invasion_strategy_os/invasion_strategy_os.py`.
- Created `tools/invasion_strategy_os/config.example.json`.
- Created sample CSV inputs for smoke testing only.
- Added `tools/invasion_strategy_os/README.md` and `requirements.txt`.
- Generated `sample_output/map.html` and `sample_output/state.json`.
- Updated `.gitignore` to allowlist only this durable tool directory under `tools/`.

## 5. Interpretation

This MVP should be used as a bridge between the current Google Sheets operational map and later GPT/API analysis. The immediate value is not tactical automation; it is a repeatable way to convert the current map into graph evidence that commanders can review.

The sample input is synthetic smoke-test data only. It is not a real LastWar board state and should not be used for operational decisions.

## 6. Risks

- The current live Google Sheet still needs a clean node/edge export or a mapping tab with stable ids.
- CHOKE output is graph-structural, so it must be checked against game rules, protection windows, alliance pact state, and actual attack eligibility.
- Google Sheets private/API access may require later credential or connector work; this MVP supports CSV export first because it is simpler to update daily.
- Browser verification over `file://` was blocked by the Codex browser safety policy, but the same output was verified through `http://127.0.0.1:8000/sample_output/map.html` in the in-app browser.
- The current live graph uses distance-derived same-area edges because `拠点履歴_座標` does not yet expose explicit adjacency. This is a workflow test, not confirmed game-rule adjacency.

## 7. Recommended actions

1. Add or export a live node table from the operational Google Sheet with stable ids and adjacency.
2. Add a live edge table only if adjacency is not already present in the node table.
3. Run the MVP after each meaningful map update and review `critical_nodes` in `sample_output/state.json`.
4. Compare CHOKE candidates against the commander map before issuing any R4/R5 order.
5. Later, add a small converter for the current Google Sheets map tab if the map body cannot be exported directly as nodes and edges.

## 8. Unknowns

- Exact live Google Sheets tab/range for the final node table.
- Whether the operational map should use grid ids, game coordinates, or both as the canonical node id.
- Whether diagonal adjacency should be represented as normal edges, lower-weight edges, or rule-dependent edges.
- Whether pact territory should be modeled as direct edges or as a scenario layer.

## 9. Files referenced

- `.gitignore`
- `tools/invasion_strategy_os/invasion_strategy_os.py`
- `tools/invasion_strategy_os/config.example.json`
- `tools/invasion_strategy_os/README.md`
- `tools/invasion_strategy_os/requirements.txt`
- `tools/invasion_strategy_os/sample_nodes.csv`
- `tools/invasion_strategy_os/sample_edges.csv`
- `sample_output/map.html`
- `sample_output/state.json`
