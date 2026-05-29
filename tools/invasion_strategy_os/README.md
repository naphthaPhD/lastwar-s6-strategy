# LastWar Invasion Strategy OS MVP

This is a prototype strategy-support tool for Season 6 map analysis. It is not a game bot and does not automate gameplay. It reads current board data from CSV or Google Sheets CSV export, builds a graph, extracts connection risks, and writes HTML plus JSON outputs for commander review.

## What It Does

- Reads nodes and edges from CSV files or Google Sheets export URLs.
- Builds a `networkx` graph.
- Calculates connected components, articulation points, shortest path, degree centrality, and betweenness centrality.
- Treats articulation points as CHOKE candidates.
- Flags stronger CHOKE candidates when removal splits major city/stronghold groups or leaves only a narrow route.
- Writes a zoomable `pyvis` HTML map.
- Writes machine-readable JSON for later GPT/API workflows.
- Uses JST by default for protection-timer calculations.
- Optionally reads alliance ranking power from a local Excel workbook and shows it in node details.
- Writes rule-engine invasion simulation candidates from the generated `state.json` shape.

## Input Schema

Node columns:

| Column | Meaning |
|---|---|
| `id` | Stable node id. Required. |
| `name` | Display name. |
| `type` | Facility type, such as `city`, `stronghold`, `fishery`, `sanctuary`. |
| `owner` | Owning alliance. |
| `protect_until` | Protection end time. ISO-8601 is preferred. JST is assumed if no timezone is included. |
| `x` | X coordinate. |
| `y` | Y coordinate. |
| `importance` | Numeric importance. Used for node size and CHOKE scoring. |
| `adjacent` | Optional semicolon/comma/space separated neighbor ids. |

Edge columns:

| Column | Meaning |
|---|---|
| `from` | Source node id. |
| `to` | Target node id. |
| `weight` | Optional edge weight. Defaults to `1`. |

Japanese column aliases such as `拠点名`, `種別`, `所有連盟`, `保護終了時刻`, `重要度`, and `隣接` are also accepted.

## Setup

```powershell
.\.venv\Scripts\python.exe -m pip install -r tools\invasion_strategy_os\requirements.txt
```

If `.venv` does not exist on a fresh machine, create it first with any available Python 3.11+ interpreter, then run the install command above.

The full-map config reads alliance strength from `s6powerrank_8server_power_2026-05-10_en.xlsx`, sheet `Alliance Power`, and writes a derived cache to `data/alliance_power_rankings_2026-05-10.json`. The cache is useful for review and reruns, but the Excel workbook remains the source for the ranking values.

## Run With Local CSV

```powershell
.\.venv\Scripts\python.exe tools\invasion_strategy_os\invasion_strategy_os.py --config tools\invasion_strategy_os\config.example.json
```

Outputs:

- `sample_output/map.html`
- `sample_output/state.json`

The included sample CSV is synthetic smoke-test data only. Do not treat it as a real LastWar board state.

## Run With Google Sheets CSV Export

Use `type: google_sheet_csv` and specify spreadsheet id plus gid. The target sheet must be readable by the current environment, or published/exportable as CSV.

```json
{
  "sources": {
    "nodes": {
      "type": "google_sheet_csv",
      "spreadsheet_id": "YOUR_SPREADSHEET_ID",
      "gid": "123456789"
    },
    "edges": {
      "type": "google_sheet_csv",
      "spreadsheet_id": "YOUR_SPREADSHEET_ID",
      "gid": "987654321"
    }
  }
}
```

If the map sheet stores adjacency in the node table, the edge source may be omitted.

## Run With The Current #534 Sheet

The live-test config reads `拠点履歴_座標` from spreadsheet `＃534`, filters it to the `#534` area, derives provisional same-area distance edges, and overwrites the usual output files.

```powershell
.\.venv\Scripts\python.exe tools\invasion_strategy_os\invasion_strategy_os.py --config tools\invasion_strategy_os\config.google_history_534.json
```

Outputs:

- `sample_output/map.html`
- `sample_output/state.json`

Important: the current sheet does not contain an explicit adjacency column. `config.google_history_534.json` therefore uses coordinate-distance edges as a trial graph. Use this for visualization and workflow testing, not as confirmed game-rule adjacency.

## Run With The Current Full Outer Map

`config.google_full_map.json` reads the live `管理表たたき` export, excludes the central area, applies the 3x3 outer-area layout from the Google Sheets full map, and derives provisional distance edges across area borders.

```powershell
.\.venv\Scripts\python.exe tools\invasion_strategy_os\invasion_strategy_os.py --config tools\invasion_strategy_os\config.google_full_map.json
```

Current rule assumptions:

- Central area rows are included and placed in the middle of the outer ring.
- Outer areas are placed clockwise from the upper-left: `#534`, `#509`, `#503`, `#480`, `#440`, `#511`, `#523`, `#476`.
- `交易地` nodes are displayed but not connected by edges.
- Lowercase coordinate letters are normalized to `都市`.
- Uppercase coordinate letters are normalized to `漁場`.
- Fishery nodes are displayed larger than city nodes in this view.
- The full-map view uses smaller nodes and labels so city/fishery spacing is easier to read.
- Fishery labels use smaller in-node text in alliance-label mode.
- The full-map view adds display-only gaps between area blocks while preserving graph coordinates for edge derivation. The current display gap is 90, so inter-area and outer-to-central edge spans are shorter while the rule graph remains unchanged.
- A fixed legend explains strategic colors, gray destroyed-city nodes, and red/yellow protection borders.
- Clicking a node opens a fixed information panel with management-table fields: position key, type, alliance, status, acquisition time, protection time, and memo.
- Clicking a node also shows alliance ranking power when the node owner matches an alliance tag in the local ranking workbook. Example fields are alliance power, overall rank, server rank, and alliance name.
- Central-area facility types are corrected from the Cpt Hedgehog Season 6 reference map pattern: outer central cells are fishery nodes, inner central cells are altar nodes, and the 2x2 center is represented as one large `祖霊神殿` node.
- Central fishery nodes are connected by orthogonal coordinate edges and displayed smaller than outer fisheries. Central altar nodes and `祖霊神殿` are displayed but isolated because altar ownership does not create adjacent movement.
- The HTML map has a label toggle: coordinate labels by default, or alliance-name labels at the same node-center position. In alliance-name mode, trade posts are always labeled `交易地`.
- Nodes can be temporarily moved with the mouse. The HTML map has a `位置リセット` button that returns moved nodes to the generated layout.
- Selecting a fishery highlights all edges connected to that fishery in cyan. `境界強調` highlights fishery edges where a friendly-side node (#534/#509/#440/#511 group) touches an enemy-side node in orange, and where an enemy-side node touches an unowned node in amber. `境界+内側`, `境界+内側+内側`, and `境界+内側+内側+内側` also highlight fishery edges from those friendly/enemy boundary friendly-side fisheries into friendly-side or unowned fisheries for 1, 2, or 3 interior steps in rose red. `敵侵攻予測`, `味方侵攻候補`, `遮断候補`, `危険回避`, `敵未取得拡張`, and `味方未取得拡張` highlight the top 30 candidate edges ranked by the relevant score model. `強調解除` clears edge highlighting.
- `戦力無視ルート` enables shortest-route selection on fishery routes only, ignoring enemy alliance power. `始点より低戦力通過` uses the same two-click route workflow but allows transit through enemy fisheries only when that enemy alliance has lower ranking power than the alliance owning the start node. Cities are not used as transit nodes. If the target is a city, the route is highlighted to the nearest fishery adjacent to that city. Route-mode node selection suppresses the normal yellow adjacent-edge selection highlight. `ルート解除` clears the route.
- `マップ最新化` can refresh the generated map from the latest `管理表たたき` sheet when `interactive_server.py` is running. It calls `/api/refresh`, regenerates `sample_output/map.html` and `sample_output/state.json`, then reloads the browser page.
- Node colors are strategic colors: #534-side owners are blue, #509/#440/#511-side owners are green, enemy-side owners are red, and unowned nodes are white. Owners with server-number prefixes such as `476B` are classified by that prefix even when they occupy another area.
- Edge rules are tactical and coordinate-based, not pure distance: fisheries connect to adjacent fisheries in 8 directions unless the diagonal crosses a city/trade-post cell, cities connect only to their four surrounding fisheries, destroyed cities are isolated, outer-area fisheries connect to nearby central fisheries with a small coordinate tolerance, city-city edges are blocked, trade posts remain isolated and are never treated as cities, and altar/temple nodes are isolated.
- Default edge display width is fixed at `1`, including outer-to-central edges; only interactive highlights use thicker lines.
- `sample_output/state.json` includes an `invasion_simulation` block generated by `tools/invasion_strategy_os/simulation.py`. The rule engine reads the same JSON shape that is written to disk and is intentionally separated from `invasion_strategy_os.py` so the scoring layer can be replaced without changing sheet ingestion or map rendering.
- The Phase 3 rule engine scores candidates with JSON reasons and factor breakdowns for protection expiry, battle windows, capture-limit pressure, enemy adjacency, city-destruction reach, central connection value, and counterattack risk. It also preserves the previous boundary/interior-depth counts used by the map highlight buttons.
- Simulation assumptions are conservative: trade posts, altars, and the ancestral temple do not create movement adjacency; destroyed cities are isolated; cities are not used as fishery-route transit; battle windows and capture limits are configurable; capture-limit usage is currently estimated from owned city/fishery nodes until a live cap counter is added.
- Example verification: `#534:a-2` is a trade post and has no edges; `#534:b-2` is a city and connects to `#534:B-1`, `#534:B-3`, `#534:C-1`, and `#534:C-3`.
- Central-boundary example: `#534:A-21` connects to `中央-1-1`.
- If a city row later contains `破壊`, `destroyed`, or `ruined` in owner/status/memo, the city node is shown in gray, labels as `破壊`, and receives no edges.

## Run The Interactive Local Map

Use this when you want a cpt-hedge-style workflow with search, node selection, sheet refresh, and local manual edits.

```powershell
.\.venv\Scripts\python.exe tools\invasion_strategy_os\interactive_server.py --port 8010
```

Then open:

```text
http://127.0.0.1:8010/
```

Interactive behavior:

- Reads `sample_output/state.json` in the browser.
- `マップを最新に` regenerates `sample_output/map.html` and `sample_output/state.json` from `config.google_full_map.json`.
- Node edits are saved locally to `data/invasion_strategy_overrides.json`.
- Manual edits override browser display after every refresh, so spreadsheet updates and local commander corrections can coexist.

The static generated map also has a `マップ最新化` button. For that button to work, keep the interactive server running on port `8010`; if the static map is opened through `http://127.0.0.1:8000/sample_output/map.html`, it will call the `8010` refresh API and reload itself after regeneration.

Current limitation: local edits do not write back to Google Sheets. Treat `data/invasion_strategy_overrides.json` as the safe editable layer until a Google Sheets write-back policy is decided.

## Tactical Use

1. Export or expose the current Google Sheets board state.
2. Run the script.
3. Open `sample_output/map.html`.
4. Review `critical_nodes` in `sample_output/state.json`.
5. Treat CHOKE output as a candidate list for human confirmation, not an automatic command.
