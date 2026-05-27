from __future__ import annotations

import argparse
import csv
import hashlib
import inspect
import json
import re
import shutil
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote
from urllib.request import urlopen
from zoneinfo import ZoneInfo

import networkx as nx
from pyvis.network import Network


JST = ZoneInfo("Asia/Tokyo")

NODE_ALIASES = {
    "id": ["id", "node_id", "key", "キー", "ID", "拠点ID", "位置キー"],
    "name": ["name", "拠点名", "名称", "施設名", "座標"],
    "type": ["type", "種別", "施設種別"],
    "owner": ["owner", "所有連盟", "連盟", "alliance", "現在連盟"],
    "protect_until": ["protect_until", "保護終了時刻", "保護終了", "保護明け", "protect", "保護切れ"],
    "x": ["x", "X", "座標X", "game_x"],
    "y": ["y", "Y", "座標Y", "game_y"],
    "importance": ["importance", "重要度", "priority", "優先度"],
    "adjacent": ["adjacent", "隣接", "接続情報", "neighbors", "neighbours"],
    "area": ["area", "エリア", "server", "サーバ"],
}

EDGE_ALIASES = {
    "from": ["from", "source", "from_id", "起点"],
    "to": ["to", "target", "to_id", "終点"],
    "weight": ["weight", "重み"],
}


@dataclass(frozen=True)
class Node:
    id: str
    name: str
    type: str
    owner: str
    protect_until: str | None
    x: float
    y: float
    importance: float
    area: str = ""


@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    weight: float = 1.0


def read_config(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    with Path(path).open("r", encoding="utf-8") as fh:
        return json.load(fh)


def read_csv_rows(source: dict[str, Any], base_dir: Path) -> list[dict[str, str]]:
    source_type = source.get("type", "csv")
    if source_type == "csv":
        raw_path = Path(source["path"])
        path = raw_path if raw_path.is_absolute() else base_dir / raw_path
        text = path.read_text(encoding="utf-8-sig")
    elif source_type == "google_sheet_csv":
        url = google_sheet_csv_url(source)
        with urlopen(url, timeout=30) as response:
            text = response.read().decode("utf-8-sig")
    elif source_type == "url_csv":
        with urlopen(source["url"], timeout=30) as response:
            text = response.read().decode("utf-8-sig")
    else:
        raise ValueError(f"Unsupported source type: {source_type}")

    return list(csv.DictReader(text.splitlines()))


def google_sheet_csv_url(source: dict[str, Any]) -> str:
    spreadsheet_id = source["spreadsheet_id"]
    if source.get("gid") is not None:
        gid = source["gid"]
        return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid={gid}"
    if source.get("sheet_name"):
        sheet_name = quote(str(source["sheet_name"]))
        return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    raise ValueError("google_sheet_csv source needs either gid or sheet_name")


def pick(row: dict[str, str], aliases: dict[str, list[str]], field: str, default: str = "") -> str:
    for key in aliases[field]:
        if key in row and row[key] is not None:
            return str(row[key]).strip()
    return default


def parse_float(value: str, default: float = 0.0) -> float:
    if value == "":
        return default
    return float(str(value).replace(",", ""))


def parse_optional_time(value: str | None, tz: ZoneInfo) -> datetime | None:
    if not value:
        return None
    normalized = value.strip()
    if not normalized:
        return None
    normalized = normalized.replace("Z", "+00:00")
    for fmt in ("%Y/%m/%d %H:%M", "%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M:%S"):
        try:
            parsed = datetime.strptime(normalized, fmt)
            return parsed.replace(tzinfo=tz)
        except ValueError:
            pass
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=tz)
    return parsed.astimezone(tz)


def split_neighbors(value: str) -> list[str]:
    return [part for part in re.split(r"[;,\s]+", value.strip()) if part]


def load_nodes(rows: list[dict[str, str]], config: dict[str, Any]) -> tuple[dict[str, Node], list[Edge]]:
    nodes: dict[str, Node] = {}
    adjacency_edges: list[Edge] = []
    area_filter = set(config.get("areas", []))
    importance_by_type = {str(key): float(value) for key, value in config.get("importance_by_type", {}).items()}
    for row_number, row in enumerate(rows, start=2):
        node_id = pick(row, NODE_ALIASES, "id")
        if not node_id:
            raise ValueError(f"Node row {row_number} is missing id")
        area = pick(row, NODE_ALIASES, "area")
        if area_filter and area not in area_filter:
            continue
        node_type = pick(row, NODE_ALIASES, "type", "unknown") or "unknown"
        importance = parse_float(
            pick(row, NODE_ALIASES, "importance"),
            importance_by_type.get(node_type, 1.0),
        )
        node = Node(
            id=node_id,
            name=pick(row, NODE_ALIASES, "name", node_id) or node_id,
            type=node_type,
            owner=pick(row, NODE_ALIASES, "owner", "unknown") or "unknown",
            protect_until=pick(row, NODE_ALIASES, "protect_until") or None,
            x=parse_float(pick(row, NODE_ALIASES, "x")),
            y=parse_float(pick(row, NODE_ALIASES, "y")),
            importance=importance,
            area=area,
        )
        nodes[node.id] = node
        for neighbor_id in split_neighbors(pick(row, NODE_ALIASES, "adjacent")):
            adjacency_edges.append(Edge(node.id, neighbor_id, 1.0))
    return nodes, adjacency_edges


def load_edges(rows: list[dict[str, str]]) -> list[Edge]:
    edges: list[Edge] = []
    for row_number, row in enumerate(rows, start=2):
        source = pick(row, EDGE_ALIASES, "from")
        target = pick(row, EDGE_ALIASES, "to")
        if not source and not target:
            continue
        if not source or not target:
            raise ValueError(f"Edge row {row_number} needs both from and to")
        weight = parse_float(pick(row, EDGE_ALIASES, "weight"), 1.0)
        edges.append(Edge(source, target, weight))
    return edges


def derive_distance_edges(nodes: dict[str, Node], config: dict[str, Any]) -> list[Edge]:
    if config.get("type") != "distance":
        return []
    max_distance = float(config.get("max_distance", 80))
    same_area_only = bool(config.get("same_area_only", True))
    max_edges_per_node = int(config.get("max_edges_per_node", 6))
    candidates: list[tuple[float, str, str]] = []
    node_items = sorted(nodes.items())
    for index, (source_id, source) in enumerate(node_items):
        for target_id, target in node_items[index + 1 :]:
            if same_area_only and source.area != target.area:
                continue
            distance = ((source.x - target.x) ** 2 + (source.y - target.y) ** 2) ** 0.5
            if 0 < distance <= max_distance:
                candidates.append((distance, source_id, target_id))

    degree: dict[str, int] = {node_id: 0 for node_id in nodes}
    edges: list[Edge] = []
    for distance, source_id, target_id in sorted(candidates):
        if degree[source_id] >= max_edges_per_node or degree[target_id] >= max_edges_per_node:
            continue
        edges.append(Edge(source_id, target_id, round(distance, 3)))
        degree[source_id] += 1
        degree[target_id] += 1
    return edges


def build_graph(nodes: dict[str, Node], edges: list[Edge]) -> nx.Graph:
    graph = nx.Graph()
    for node in nodes.values():
        graph.add_node(node.id, **asdict(node))
    for edge in edges:
        if edge.source not in nodes or edge.target not in nodes:
            missing = [node_id for node_id in (edge.source, edge.target) if node_id not in nodes]
            raise ValueError(f"Edge references missing node(s): {', '.join(missing)}")
        graph.add_edge(edge.source, edge.target, weight=edge.weight)
    return graph


def is_major_node(graph: nx.Graph, node_id: str, config: dict[str, Any]) -> bool:
    node = graph.nodes[node_id]
    major_types = {str(value).lower() for value in config.get("major_types", ["city", "stronghold"])}
    major_importance = float(config.get("major_importance", 7))
    return str(node.get("type", "")).lower() in major_types or float(node.get("importance", 0)) >= major_importance


def analyze_graph(
    graph: nx.Graph,
    config: dict[str, Any],
    shortest_from: str | None,
    shortest_to: str | None,
) -> dict[str, Any]:
    components = [sorted(component) for component in nx.connected_components(graph)]
    articulation_points = sorted(nx.articulation_points(graph))
    degree_centrality = nx.degree_centrality(graph)
    betweenness_centrality = nx.betweenness_centrality(graph, weight="weight", normalized=True)
    isolated_nodes = sorted(nx.isolates(graph))

    shortest_path: list[str] | None = None
    if shortest_from and shortest_to:
        if shortest_from not in graph or shortest_to not in graph:
            shortest_path = None
        else:
            try:
                shortest_path = nx.shortest_path(graph, shortest_from, shortest_to, weight="weight")
            except nx.NetworkXNoPath:
                shortest_path = None

    critical_nodes = extract_chokes(graph, articulation_points, betweenness_centrality, config)

    return {
        "connected_components": components,
        "articulation_points": articulation_points,
        "critical_nodes": critical_nodes,
        "isolated_nodes": isolated_nodes,
        "shortest_path": {
            "from": shortest_from,
            "to": shortest_to,
            "path": shortest_path,
        },
        "degree_centrality": round_mapping(degree_centrality),
        "betweenness_centrality": round_mapping(betweenness_centrality),
    }


def extract_chokes(
    graph: nx.Graph,
    articulation_points: list[str],
    betweenness: dict[str, float],
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    major_nodes = {node_id for node_id in graph.nodes if is_major_node(graph, node_id, config)}
    route_limited_degree = int(config.get("route_limited_degree", 2))
    chokes: list[dict[str, Any]] = []

    for index, node_id in enumerate(articulation_points, start=1):
        reduced = graph.copy()
        reduced.remove_node(node_id)
        split_components = [sorted(component) for component in nx.connected_components(reduced)]
        major_components = [sorted(set(component) & major_nodes) for component in split_components]
        major_components = [component for component in major_components if component]

        reasons = ["removal_disconnects_graph"]
        if len(major_components) >= 2:
            reasons.append("major_groups_split")
        if any(len(component) == 1 for component in major_components):
            reasons.append("major_node_isolated")
        if graph.degree(node_id) <= route_limited_degree:
            reasons.append("limited_route_degree")

        node = graph.nodes[node_id]
        score = (
            float(node.get("importance", 0))
            + graph.degree(node_id)
            + (betweenness.get(node_id, 0.0) * 10)
            + (3 if "major_groups_split" in reasons else 0)
            + (2 if "major_node_isolated" in reasons else 0)
        )
        chokes.append(
            {
                "choke_id": f"CHOKE-{index:02d}",
                "node_id": node_id,
                "name": node.get("name", node_id),
                "owner": node.get("owner", "unknown"),
                "type": node.get("type", "unknown"),
                "importance": node.get("importance", 0),
                "degree": graph.degree(node_id),
                "betweenness": round(betweenness.get(node_id, 0.0), 4),
                "score": round(score, 3),
                "reasons": reasons,
                "affected_major_groups": major_components,
                "components_after_removal": split_components,
            }
        )

    chokes.sort(key=lambda item: (-item["score"], item["node_id"]))
    for index, choke in enumerate(chokes, start=1):
        choke["choke_id"] = f"CHOKE-{index:02d}"
    return chokes


def round_mapping(values: dict[str, float]) -> dict[str, float]:
    return {key: round(value, 4) for key, value in sorted(values.items())}


def owner_color(owner: str) -> str:
    palette = [
        "#2563eb",
        "#dc2626",
        "#16a34a",
        "#d97706",
        "#7c3aed",
        "#0891b2",
        "#be123c",
        "#4b5563",
    ]
    digest = hashlib.sha256(owner.encode("utf-8")).hexdigest()
    return palette[int(digest[:2], 16) % len(palette)]


def owner_color_map(owners: set[str]) -> dict[str, str]:
    palette = [
        "#2563eb",
        "#dc2626",
        "#16a34a",
        "#d97706",
        "#7c3aed",
        "#0891b2",
        "#be123c",
        "#4b5563",
        "#ca8a04",
        "#0f766e",
        "#9333ea",
        "#c2410c",
    ]
    colors: dict[str, str] = {}
    for index, owner in enumerate(sorted(owners)):
        colors[owner] = palette[index] if index < len(palette) else owner_color(owner)
    return colors


def protection_status(node: Node, now: datetime, warning_hours: float, tz: ZoneInfo) -> dict[str, Any]:
    protect_until = parse_optional_time(node.protect_until, tz)
    if protect_until is None:
        return {"status": "unknown", "hours_remaining": None, "protect_until": None}
    hours_remaining = (protect_until - now).total_seconds() / 3600
    if hours_remaining < 0:
        status = "expired"
    elif hours_remaining <= warning_hours:
        status = "soon"
    else:
        status = "protected"
    return {
        "status": status,
        "hours_remaining": round(hours_remaining, 2),
        "protect_until": protect_until.isoformat(),
    }


def write_html(
    graph: nx.Graph,
    analysis: dict[str, Any],
    output_path: Path,
    now: datetime,
    config: dict[str, Any],
    tz: ZoneInfo,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    critical_ids = {item["node_id"] for item in analysis["critical_nodes"]}
    warning_hours = float(config.get("protect_warning_hours", 6))
    colors_by_owner = owner_color_map({str(node_data.get("owner", "unknown")) for _, node_data in graph.nodes(data=True)})

    network = Network(height="820px", width="100%", bgcolor="#111827", font_color="#f9fafb", cdn_resources="local")
    network.toggle_physics(False)

    for node_id, node_data in graph.nodes(data=True):
        node = Node(**{field: node_data[field] for field in Node.__dataclass_fields__})
        protect = protection_status(node, now, warning_hours, tz)
        border = "#f9fafb"
        if protect["status"] == "expired":
            border = "#ef4444"
        elif protect["status"] == "soon":
            border = "#facc15"
        title = (
            f"<b>{node.name}</b><br>"
            f"id: {node.id}<br>"
            f"type: {node.type}<br>"
            f"owner: {node.owner}<br>"
            f"importance: {node.importance}<br>"
            f"protect: {protect['protect_until'] or 'unknown'}<br>"
            f"remaining hours: {protect['hours_remaining']}"
        )
        network.add_node(
            node.id,
            label=node.name,
            title=title,
            x=node.x,
            y=-node.y,
            physics=False,
            size=max(12, min(55, 12 + node.importance * 4)),
            color={"background": colors_by_owner.get(node.owner, owner_color(node.owner)), "border": border},
            borderWidth=6 if node_id in critical_ids else 2,
        )

    for source, target, edge_data in graph.edges(data=True):
        network.add_edge(source, target, value=edge_data.get("weight", 1.0), title=f"weight: {edge_data.get('weight', 1.0)}")

    network.set_options(
        """
        {
          "nodes": {
            "font": {"size": 18, "face": "arial", "color": "#f9fafb", "strokeWidth": 4, "strokeColor": "#111827"},
            "shape": "dot"
          },
          "edges": {
            "color": {"color": "#94a3b8", "highlight": "#facc15"},
            "smooth": false
          },
          "physics": {
            "enabled": false,
            "stabilization": false
          },
          "interaction": {
            "hover": true,
            "navigationButtons": true,
            "keyboard": true
          }
        }
        """
    )
    copy_local_vis_assets(output_path)
    html = network.generate_html(notebook=False)
    html = localize_vis_resources(strip_remote_bootstrap(html))
    html = clean_generated_html(html)
    output_path.write_text(html, encoding="utf-8")


def copy_local_vis_assets(output_path: Path) -> None:
    pyvis_root = Path(inspect.getfile(Network)).parent
    source = pyvis_root / "templates" / "lib"
    target = output_path.parent / "lib"
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    for asset_dir in ("bindings", "tom-select", "vis-9.1.2"):
        shutil.copytree(source / asset_dir, target / asset_dir)


def strip_remote_bootstrap(html: str) -> str:
    html = re.sub(
        r"\s*<link[^>]+bootstrap@5\.0\.0-beta3/dist/css/bootstrap\.min\.css[^>]+>\s*",
        "",
        html,
        flags=re.DOTALL,
    )
    html = re.sub(
        r"\s*<script[^>]+bootstrap@5\.0\.0-beta3/dist/js/bootstrap\.bundle\.min\.js[^>]*></script>\s*",
        "",
        html,
        flags=re.DOTALL,
    )
    return html


def localize_vis_resources(html: str) -> str:
    html = re.sub(
        r"<link[^>]+vis-network\.min\.css[^>]+>",
        '<link rel="stylesheet" href="lib/vis-9.1.2/vis-network.css" />',
        html,
    )
    html = re.sub(
        r"<script[^>]+vis-network\.min\.js[^>]*></script>",
        '<script src="lib/vis-9.1.2/vis-network.min.js"></script>',
        html,
    )
    return html


def clean_generated_html(html: str) -> str:
    return "\n".join(line.rstrip() for line in html.splitlines()) + "\n"


def write_json(
    graph: nx.Graph,
    edges: list[Edge],
    analysis: dict[str, Any],
    output_path: Path,
    now: datetime,
    config: dict[str, Any],
    tz: ZoneInfo,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    warning_hours = float(config.get("protect_warning_hours", 6))
    nodes = []
    for _, node_data in graph.nodes(data=True):
        node = Node(**{field: node_data[field] for field in Node.__dataclass_fields__})
        record = asdict(node)
        record["protection"] = protection_status(node, now, warning_hours, tz)
        nodes.append(record)
    payload = {
        "generated_at": now.isoformat(),
        "timezone": str(tz),
        "nodes": nodes,
        "connections": [asdict(edge) for edge in edges],
        **analysis,
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build LastWar invasion strategy graph outputs.")
    parser.add_argument("--config", help="JSON config path.")
    parser.add_argument("--nodes", help="Override node CSV path.")
    parser.add_argument("--edges", help="Override edge CSV path.")
    parser.add_argument("--html", help="Override HTML output path.")
    parser.add_argument("--json", dest="json_output", help="Override JSON output path.")
    parser.add_argument("--shortest-from", help="Shortest-path source node id.")
    parser.add_argument("--shortest-to", help="Shortest-path target node id.")
    parser.add_argument("--now", help="Override current time for repeatable tests. ISO-8601.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path.cwd()
    config = read_config(args.config)
    tz = ZoneInfo(config.get("timezone", "Asia/Tokyo"))

    sources = config.get("sources", {})
    if args.nodes:
        sources["nodes"] = {"type": "csv", "path": args.nodes}
    if args.edges:
        sources["edges"] = {"type": "csv", "path": args.edges}
    if "nodes" not in sources:
        raise ValueError("Node source is required")

    node_rows = read_csv_rows(sources["nodes"], repo_root)
    source_config = config.get("source_options", {})
    nodes, adjacency_edges = load_nodes(node_rows, source_config)
    explicit_edges = []
    if sources.get("edges"):
        explicit_edges = load_edges(read_csv_rows(sources["edges"], repo_root))
    derived_edges = derive_distance_edges(nodes, config.get("edge_derivation", {}))
    edges = dedupe_edges(adjacency_edges + explicit_edges + derived_edges)

    graph = build_graph(nodes, edges)
    shortest = config.get("shortest_path", {})
    shortest_from = args.shortest_from or shortest.get("from")
    shortest_to = args.shortest_to or shortest.get("to")
    analysis_config = config.get("analysis", {})
    analysis = analyze_graph(graph, analysis_config, shortest_from, shortest_to)

    now = parse_optional_time(args.now, tz) if args.now else datetime.now(tz)
    assert now is not None

    output_config = config.get("output", {})
    html_path = Path(args.html or output_config.get("html", "sample_output/map.html"))
    json_path = Path(args.json_output or output_config.get("json", "sample_output/state.json"))
    write_html(graph, analysis, repo_root / html_path, now, analysis_config, tz)
    write_json(graph, edges, analysis, repo_root / json_path, now, analysis_config, tz)
    print(f"Wrote {html_path}")
    print(f"Wrote {json_path}")
    print(f"Critical nodes: {len(analysis['critical_nodes'])}")
    return 0


def dedupe_edges(edges: list[Edge]) -> list[Edge]:
    seen: set[tuple[str, str]] = set()
    deduped: list[Edge] = []
    for edge in edges:
        key = tuple(sorted((edge.source, edge.target)))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(edge)
    return deduped


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
