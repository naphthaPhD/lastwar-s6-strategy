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

- Central area rows are excluded for now.
- `交易地` nodes are displayed but not connected by edges.
- Lowercase coordinate letters are normalized to `都市`.
- Uppercase coordinate letters are normalized to `漁場`.
- The full-map view uses smaller nodes and labels so city/fishery spacing is easier to read.
- Clicking a node opens a fixed information panel with management-table fields: position key, type, alliance, status, acquisition time, protection time, and memo.

## Tactical Use

1. Export or expose the current Google Sheets board state.
2. Run the script.
3. Open `sample_output/map.html`.
4. Review `critical_nodes` in `sample_output/state.json`.
5. Treat CHOKE output as a candidate list for human confirmation, not an automatic command.
