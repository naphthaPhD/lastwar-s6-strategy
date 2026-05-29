from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict, deque
from datetime import datetime, time
from pathlib import Path
from typing import Any


FISHERY_TYPE = "漁場"
CITY_TYPE = "都市"
DEFAULT_FRIENDLY_AFFILIATIONS = {"self", "ally"}
DEFAULT_INTERIOR_AFFILIATIONS = {"self", "ally", "unowned"}


def build_invasion_simulation(state: dict[str, Any], config: dict[str, Any] | None = None) -> dict[str, Any]:
    config = config or {}
    nodes = {str(node.get("id")): node for node in state.get("nodes", []) if node.get("id")}
    adjacency, edge_lookup = build_adjacency(state.get("connections", []), nodes)
    generated_at = parse_datetime(state.get("generated_at"))
    max_items = int(config.get("max_items", 30))
    friendly_affiliations = {str(value) for value in config.get("friendly_affiliations", DEFAULT_FRIENDLY_AFFILIATIONS)}
    interior_affiliations = {str(value) for value in config.get("interior_affiliations", DEFAULT_INTERIOR_AFFILIATIONS)}
    depths = [int(value) for value in config.get("interior_depths", [1, 2, 3])]

    context = {
        "nodes": nodes,
        "adjacency": adjacency,
        "edge_lookup": edge_lookup,
        "generated_at": generated_at,
        "config": config,
        "friendly_affiliations": friendly_affiliations,
    }

    friendly_pressure: list[dict[str, Any]] = []
    enemy_threats: list[dict[str, Any]] = []
    friendly_expansion: list[dict[str, Any]] = []
    enemy_expansion: list[dict[str, Any]] = []
    attack_score_options: list[dict[str, Any]] = []
    interdiction_score_options: list[dict[str, Any]] = []
    risk_avoidance_options: list[dict[str, Any]] = []

    for edge in state.get("connections", []):
        source_id, target_id = edge_endpoints(edge)
        if source_id not in nodes or target_id not in nodes:
            continue
        source = nodes[source_id]
        target = nodes[target_id]
        if source.get("destroyed") or target.get("destroyed"):
            continue

        source_affiliation = affiliation(source)
        target_affiliation = affiliation(target)

        if is_fishery(source) and is_fishery(target):
            if source_affiliation in friendly_affiliations and target_affiliation == "enemy":
                friendly_pressure.append(candidate_record(context, source_id, target_id, "friendly_to_enemy_boundary", "simple"))
                enemy_threats.append(candidate_record(context, target_id, source_id, "enemy_to_friendly_boundary", "risk"))
                attack_score_options.append(candidate_record(context, source_id, target_id, "attack_score", "attack"))
                risk_avoidance_options.append(candidate_record(context, source_id, target_id, "risk_avoidance", "risk"))
            elif target_affiliation in friendly_affiliations and source_affiliation == "enemy":
                friendly_pressure.append(candidate_record(context, target_id, source_id, "friendly_to_enemy_boundary", "simple"))
                enemy_threats.append(candidate_record(context, source_id, target_id, "enemy_to_friendly_boundary", "risk"))
                attack_score_options.append(candidate_record(context, target_id, source_id, "attack_score", "attack"))
                risk_avoidance_options.append(candidate_record(context, target_id, source_id, "risk_avoidance", "risk"))
            elif source_affiliation in friendly_affiliations and target_affiliation == "unowned":
                friendly_expansion.append(candidate_record(context, source_id, target_id, "friendly_to_unowned", "expansion"))
            elif target_affiliation in friendly_affiliations and source_affiliation == "unowned":
                friendly_expansion.append(candidate_record(context, target_id, source_id, "friendly_to_unowned", "expansion"))
            elif source_affiliation == "enemy" and target_affiliation == "unowned":
                enemy_expansion.append(candidate_record(context, source_id, target_id, "enemy_to_unowned", "expansion"))
            elif target_affiliation == "enemy" and source_affiliation == "unowned":
                enemy_expansion.append(candidate_record(context, target_id, source_id, "enemy_to_unowned", "expansion"))
        elif is_fishery(source) and source_affiliation in friendly_affiliations and is_city(target) and target_affiliation == "enemy":
            interdiction_score_options.append(candidate_record(context, source_id, target_id, "interdiction_score", "interdiction"))
        elif is_fishery(target) and target_affiliation in friendly_affiliations and is_city(source) and source_affiliation == "enemy":
            interdiction_score_options.append(candidate_record(context, target_id, source_id, "interdiction_score", "interdiction"))

    return {
        "engine": "strategic_rule_engine_v1",
        "assumptions": [
            "Input is the current state.json shape, not raw Google Sheets rows.",
            "Protection timing uses node.protection.hours_remaining when available.",
            "Battle windows and capture limits are configurable under config.simulation.",
            "Trade posts, altars, and the ancestral temple are expected to be isolated before simulation.",
            "Destroyed cities are treated as unavailable connection sources.",
            "GPT is not used by this engine.",
        ],
        "strategic_read": [
            "Attack score favors enemy boundary fisheries that extend toward enemy cities or central connection.",
            "Interdiction score favors enemy cities whose destruction reduces adjacency or local reach.",
            "Risk avoidance score flags boundaries where counterattack pressure or enemy power is high.",
        ],
        "friendly_pressure_options": top_items(friendly_pressure, max_items),
        "enemy_threat_options": top_items(enemy_threats, max_items),
        "friendly_expansion_options": top_items(friendly_expansion, max_items),
        "enemy_expansion_options": top_items(enemy_expansion, max_items),
        "attack_score_options": top_items(attack_score_options, max_items),
        "interdiction_score_options": top_items(interdiction_score_options, max_items),
        "risk_avoidance_options": top_items(risk_avoidance_options, max_items),
        "rule_score_samples": top_items(
            attack_score_options + interdiction_score_options + risk_avoidance_options,
            max_items,
        ),
        "interior_depth_counts": collect_boundary_interior_counts(
            nodes,
            adjacency,
            friendly_affiliations,
            interior_affiliations,
            depths,
        ),
        "rule_config": normalized_rule_config(config),
    }


def build_adjacency(connections: list[dict[str, Any]], nodes: dict[str, dict[str, Any]]) -> tuple[dict[str, set[str]], dict[tuple[str, str], str]]:
    adjacency: dict[str, set[str]] = {node_id: set() for node_id in nodes}
    edge_lookup: dict[tuple[str, str], str] = {}
    for edge in connections:
        source_id, target_id = edge_endpoints(edge)
        if source_id not in nodes or target_id not in nodes:
            continue
        adjacency[source_id].add(target_id)
        adjacency[target_id].add(source_id)
        edge_id = str(edge.get("id") or f"{source_id}|{target_id}")
        edge_lookup[edge_key(source_id, target_id)] = edge_id
    return adjacency, edge_lookup


def edge_endpoints(edge: dict[str, Any]) -> tuple[str, str]:
    return str(edge.get("source") or edge.get("from") or ""), str(edge.get("target") or edge.get("to") or "")


def edge_key(source_id: str, target_id: str) -> tuple[str, str]:
    return tuple(sorted((source_id, target_id)))


def top_items(items: list[dict[str, Any]], max_items: int) -> list[dict[str, Any]]:
    return sorted(items, key=lambda item: (-float(item.get("score", 0)), item.get("target", {}).get("id", ""), item.get("source", {}).get("id", "")))[:max_items]


def candidate_record(context: dict[str, Any], source_id: str, target_id: str, label: str, score_model: str) -> dict[str, Any]:
    nodes = context["nodes"]
    source = node_summary(nodes[source_id])
    target = node_summary(nodes[target_id])
    breakdown = tactical_score_breakdown(context, source_id, target_id, score_model)
    return {
        "label": label,
        "node": target["name"],
        "node_id": target["id"],
        "edge": [source_id, target_id],
        "edge_id": context["edge_lookup"].get(edge_key(source_id, target_id)),
        "source": source,
        "target": target,
        "score": breakdown["score"],
        "reasons": breakdown["reasons"],
        "score_breakdown": breakdown,
    }


def tactical_score_breakdown(context: dict[str, Any], source_id: str, target_id: str, model: str) -> dict[str, Any]:
    nodes = context["nodes"]
    adjacency = context["adjacency"]
    config = context["config"]
    generated_at = context["generated_at"]
    friendly_affiliations = context["friendly_affiliations"]

    source = nodes[source_id]
    target = nodes[target_id]
    source_power = power_value(source)
    target_power = power_value(target)
    target_importance = float(target.get("importance") or 0)
    power_ratio = ratio_or_none(source_power, target_power)
    enemy_power_ratio = ratio_or_none(target_power, source_power)
    protection = protection_factor(target)
    battle = battle_window_factor(generated_at, config)
    capture = capture_limit_factor(source, nodes, config)
    central = central_connection_factor(target_id, nodes, adjacency)
    enemy_adjacent = enemy_adjacency_factor(target_id, nodes, adjacency)
    counterattack = counterattack_risk_factor(source, target_id, nodes, adjacency)
    interdiction = interdiction_factor(target_id, nodes, adjacency, friendly_affiliations)

    if model == "attack":
        score = (
            target_importance * 1.3
            + protection["score"]
            + battle["score"]
            + capture["score"]
            + central["score"]
            + enemy_adjacent["score"] * 0.7
            + (power_ratio or source_power / 1_000_000_000) * 1.5
            - counterattack["score"] * 0.75
        )
    elif model == "interdiction":
        score = (
            target_importance * 2.0
            + protection["score"]
            + battle["score"]
            + interdiction["score"]
            + enemy_adjacent["score"] * 0.45
            + central["score"] * 0.55
            - counterattack["score"] * 0.35
        )
    elif model == "risk":
        score = (
            counterattack["score"] * 2.2
            + enemy_adjacent["score"] * 0.9
            + central["score"] * 0.4
            + max(0.0, (enemy_power_ratio or 0) - 1.0) * 5
            - protection["score"] * 0.25
        )
    elif model == "expansion":
        score = (
            target_importance
            + protection["score"]
            + battle["score"]
            + central["score"]
            + capture["score"]
            - counterattack["score"] * 0.4
        )
    else:
        score = target_importance + (power_ratio or source_power / 1_000_000_000)

    reasons = collect_reasons(
        protection,
        battle,
        capture,
        central,
        enemy_adjacent,
        counterattack,
        interdiction,
        model,
        source,
        target,
        friendly_affiliations,
    )
    return {
        "model": model,
        "score": round(max(0.0, score), 4),
        "reasons": reasons,
        "factors": {
            "protection": protection,
            "battle_window": battle,
            "capture_limit": capture,
            "enemy_adjacency": enemy_adjacent,
            "city_destruction_reach": interdiction,
            "central_connection": central,
            "counterattack_risk": counterattack,
            "source_power": int(source_power) if source_power else None,
            "target_power": int(target_power) if target_power else None,
            "source_to_target_power_ratio": round(power_ratio, 4) if power_ratio is not None else None,
            "target_to_source_power_ratio": round(enemy_power_ratio, 4) if enemy_power_ratio is not None else None,
        },
    }


def node_summary(node: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": node.get("id"),
        "area": node.get("area", ""),
        "name": node.get("name") or node.get("coord") or node.get("id"),
        "type": node.get("type") or node.get("nodeType", ""),
        "owner": node.get("display_owner") or node.get("owner", ""),
        "affiliation": affiliation(node),
        "importance": node.get("importance", 0),
        "alliance_power": node.get("alliance_power"),
    }


def collect_reasons(*factor_groups: Any) -> list[str]:
    reasons: list[str] = []
    for factor in factor_groups:
        if isinstance(factor, dict):
            reasons.extend(str(reason) for reason in factor.get("reasons", []))
    return list(dict.fromkeys(reason for reason in reasons if reason))


def protection_factor(node: dict[str, Any]) -> dict[str, Any]:
    protection = node.get("protection") or {}
    status = str(protection.get("status") or node.get("protectStatus") or "unknown")
    hours = protection.get("hours_remaining", node.get("hoursRemaining"))
    score = 0.0
    reasons: list[str] = []
    if status == "expired" or (is_number(hours) and float(hours) <= 0):
        score += 12.0
        reasons.append("保護切れ")
    elif is_number(hours):
        hours_float = float(hours)
        if hours_float <= 6:
            score += 9.0
            reasons.append("保護終了6h以内")
        elif hours_float <= 12:
            score += 6.0
            reasons.append("保護終了12h")
        elif hours_float <= 24:
            score += 2.0
            reasons.append("保護終了24h")
        else:
            score -= 4.0
            reasons.append("保護中")
    else:
        reasons.append("保護不明")
    return {"status": status, "hours_remaining": hours, "score": score, "reasons": reasons}


def battle_window_factor(now: datetime | None, config: dict[str, Any]) -> dict[str, Any]:
    windows = config.get("battle_windows") or [
        {"weekday": 2, "start": "00:00", "end": "23:59"},
        {"weekday": 5, "start": "00:00", "end": "23:59"},
    ]
    if now is None:
        return {"enabled": False, "score": 0.0, "reasons": ["戦闘時間不明"]}
    for window in windows:
        if int(window.get("weekday", -1)) != now.weekday():
            continue
        start = parse_time(str(window.get("start", "00:00")))
        end = parse_time(str(window.get("end", "23:59")))
        if start <= now.time() <= end:
            return {"enabled": True, "score": 6.0, "reasons": ["戦闘可能時間"]}
    return {"enabled": False, "score": -6.0, "reasons": ["戦闘時間外"]}


def capture_limit_factor(source: dict[str, Any], nodes: dict[str, dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]:
    limit_config = config.get("capture_limit") or {}
    if limit_config.get("enabled", True) is False:
        return {"enabled": False, "score": 0.0, "reasons": []}
    limit = int(limit_config.get("default_limit", 6))
    owner = str(source.get("owner") or "")
    owner_limits = limit_config.get("owner_limits") or {}
    if owner in owner_limits:
        limit = int(owner_limits[owner])
    usage = count_owned_capturable_nodes(owner, nodes)
    remaining = limit - usage
    if remaining <= 0:
        return {"enabled": True, "limit": limit, "usage": usage, "remaining": remaining, "score": -8.0, "reasons": ["占領上限到達"]}
    if remaining <= 2:
        return {"enabled": True, "limit": limit, "usage": usage, "remaining": remaining, "score": -2.0, "reasons": ["占領枠残少"]}
    return {"enabled": True, "limit": limit, "usage": usage, "remaining": remaining, "score": 2.0, "reasons": ["占領枠あり"]}


def enemy_adjacency_factor(node_id: str, nodes: dict[str, dict[str, Any]], adjacency: dict[str, set[str]]) -> dict[str, Any]:
    enemy_neighbors = [
        neighbor_id for neighbor_id in adjacency.get(node_id, set())
        if affiliation(nodes[neighbor_id]) == "enemy"
    ]
    enemy_fisheries = [node_id for node_id in enemy_neighbors if is_fishery(nodes[node_id])]
    enemy_cities = [node_id for node_id in enemy_neighbors if is_city(nodes[node_id])]
    score = len(enemy_fisheries) * 2.0 + len(enemy_cities) * 3.0
    reasons = []
    if enemy_neighbors:
        reasons.append("敵隣接")
    if len(enemy_neighbors) >= 3:
        reasons.append("敵密集")
    return {
        "enemy_neighbors": sorted(enemy_neighbors),
        "enemy_fisheries": sorted(enemy_fisheries),
        "enemy_cities": sorted(enemy_cities),
        "score": score,
        "reasons": reasons,
    }


def interdiction_factor(
    node_id: str,
    nodes: dict[str, dict[str, Any]],
    adjacency: dict[str, set[str]],
    friendly_affiliations: set[str],
) -> dict[str, Any]:
    node = nodes[node_id]
    if not is_city(node):
        return {"candidate": False, "score": 0.0, "reasons": []}
    neighbors = adjacency.get(node_id, set())
    friendly_fisheries = sorted(neighbor_id for neighbor_id in neighbors if is_fishery(nodes[neighbor_id]) and affiliation(nodes[neighbor_id]) in friendly_affiliations)
    enemy_fisheries = sorted(neighbor_id for neighbor_id in neighbors if is_fishery(nodes[neighbor_id]) and affiliation(nodes[neighbor_id]) == "enemy")
    groups = neighbor_groups_without_node(node_id, neighbors, adjacency)
    score = len(friendly_fisheries) * 3.0 + len(enemy_fisheries) * 1.5 + max(0, groups - 1) * 4.0
    reasons = []
    if friendly_fisheries:
        reasons.append("都市破壊候補")
    if groups > 1:
        reasons.append("都市破壊で到達不能化")
    return {
        "candidate": bool(friendly_fisheries),
        "friendly_fishery_neighbors": friendly_fisheries,
        "enemy_fishery_neighbors": enemy_fisheries,
        "neighbor_groups_after_destroy": groups,
        "score": score,
        "reasons": reasons,
    }


def central_connection_factor(node_id: str, nodes: dict[str, dict[str, Any]], adjacency: dict[str, set[str]]) -> dict[str, Any]:
    node = nodes[node_id]
    central_neighbors = sorted(neighbor_id for neighbor_id in adjacency.get(node_id, set()) if str(nodes[neighbor_id].get("area", "")) == "中央")
    score = 0.0
    reasons: list[str] = []
    if str(node.get("area", "")) == "中央":
        score += 12.0
        reasons.append("中央接続")
    if central_neighbors:
        score += 8.0
        reasons.append("中央隣接")
    return {"central_neighbors": central_neighbors, "score": score, "reasons": reasons}


def counterattack_risk_factor(source: dict[str, Any], target_id: str, nodes: dict[str, dict[str, Any]], adjacency: dict[str, set[str]]) -> dict[str, Any]:
    source_power = power_value(source)
    enemy_neighbors = [nodes[neighbor_id] for neighbor_id in adjacency.get(target_id, set()) if affiliation(nodes[neighbor_id]) == "enemy"]
    enemy_power_values = [power_value(node) for node in enemy_neighbors if power_value(node)]
    max_enemy_power = max(enemy_power_values) if enemy_power_values else 0.0
    enemy_ratio = ratio_or_none(max_enemy_power, source_power) or 0.0
    score = len(enemy_neighbors) * 2.0 + max(0.0, enemy_ratio - 1.0) * 8.0
    reasons = []
    if enemy_neighbors:
        reasons.append("反撃リスク")
    if enemy_ratio > 1:
        reasons.append("高戦力敵隣接")
    return {
        "enemy_neighbor_count": len(enemy_neighbors),
        "max_enemy_neighbor_power": int(max_enemy_power) if max_enemy_power else None,
        "enemy_to_source_power_ratio": round(enemy_ratio, 4) if enemy_ratio else None,
        "score": score,
        "reasons": reasons,
    }


def collect_boundary_interior_counts(
    nodes: dict[str, dict[str, Any]],
    adjacency: dict[str, set[str]],
    friendly_affiliations: set[str],
    interior_affiliations: set[str],
    depths: list[int],
) -> dict[str, Any]:
    boundary_friendly_nodes: set[str] = set()
    boundary_edges: set[tuple[str, str]] = set()
    for source_id, neighbors in adjacency.items():
        source = nodes[source_id]
        if not is_fishery(source):
            continue
        for target_id in neighbors:
            target = nodes[target_id]
            if not is_fishery(target):
                continue
            source_affiliation = affiliation(source)
            target_affiliation = affiliation(target)
            if source_affiliation in friendly_affiliations and target_affiliation == "enemy":
                boundary_friendly_nodes.add(source_id)
                boundary_edges.add(edge_key(source_id, target_id))
            elif target_affiliation in friendly_affiliations and source_affiliation == "enemy":
                boundary_friendly_nodes.add(target_id)
                boundary_edges.add(edge_key(source_id, target_id))

    counts: dict[str, Any] = {"boundary_edges": len(boundary_edges), "boundary_friendly_nodes": len(boundary_friendly_nodes)}
    for depth in depths:
        visited = set(boundary_friendly_nodes)
        frontier = set(boundary_friendly_nodes)
        depth_edges: set[tuple[str, str]] = set()
        for _ in range(depth):
            next_frontier: set[str] = set()
            for node_id in frontier:
                for neighbor_id in adjacency.get(node_id, set()):
                    if neighbor_id in visited:
                        continue
                    neighbor = nodes[neighbor_id]
                    if not is_fishery(neighbor) or affiliation(neighbor) not in interior_affiliations:
                        continue
                    depth_edges.add(edge_key(node_id, neighbor_id))
                    visited.add(neighbor_id)
                    next_frontier.add(neighbor_id)
            frontier = next_frontier
        counts[f"depth_{depth}_edges"] = len(depth_edges)
        counts[f"depth_{depth}_nodes"] = max(0, len(visited) - len(boundary_friendly_nodes))
    return counts


def neighbor_groups_without_node(removed_id: str, neighbors: set[str], adjacency: dict[str, set[str]]) -> int:
    remaining = set(neighbors)
    groups = 0
    while remaining:
        groups += 1
        start = remaining.pop()
        queue = deque([start])
        while queue:
            node_id = queue.popleft()
            for neighbor_id in adjacency.get(node_id, set()):
                if neighbor_id == removed_id or neighbor_id not in remaining:
                    continue
                remaining.remove(neighbor_id)
                queue.append(neighbor_id)
    return groups


def count_owned_capturable_nodes(owner: str, nodes: dict[str, dict[str, Any]]) -> int:
    if not owner:
        return 0
    return sum(
        1
        for node in nodes.values()
        if str(node.get("owner") or "") == owner and (is_fishery(node) or is_city(node))
    )


def normalized_rule_config(config: dict[str, Any]) -> dict[str, Any]:
    return {
        "max_items": int(config.get("max_items", 30)),
        "battle_windows": config.get("battle_windows") or [
            {"weekday": 2, "start": "00:00", "end": "23:59"},
            {"weekday": 5, "start": "00:00", "end": "23:59"},
        ],
        "capture_limit": config.get("capture_limit") or {"enabled": True, "default_limit": 6, "usage_source": "owned_nodes"},
    }


def is_fishery(node: dict[str, Any]) -> bool:
    return str(node.get("type") or node.get("nodeType") or "") == FISHERY_TYPE


def is_city(node: dict[str, Any]) -> bool:
    return str(node.get("type") or node.get("nodeType") or "") == CITY_TYPE


def affiliation(node: dict[str, Any]) -> str:
    return str(node.get("affiliation") or "neutral")


def power_value(node: dict[str, Any]) -> float:
    power = node.get("alliance_power") or {}
    if isinstance(power, dict):
        return float(power.get("power") or 0)
    return 0.0


def ratio_or_none(numerator: float, denominator: float) -> float | None:
    if not numerator or not denominator:
        return None
    return numerator / denominator


def parse_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return None


def parse_time(value: str) -> time:
    hour_text, minute_text = value.split(":", 1)
    return time(int(hour_text), int(minute_text))


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Phase 3 strategy rule engine against state.json.")
    parser.add_argument("--state", default="sample_output/state.json", help="Input state.json path.")
    parser.add_argument("--config", help="Optional config JSON path. Uses its simulation block when present.")
    parser.add_argument("--output", help="Optional JSON output path. Writes to stdout when omitted.")
    return parser.parse_args()


def read_simulation_config(path_text: str | None) -> dict[str, Any]:
    if not path_text:
        return {}
    config = json.loads(Path(path_text).read_text(encoding="utf-8"))
    if isinstance(config, dict) and isinstance(config.get("simulation"), dict):
        return config["simulation"]
    if isinstance(config, dict):
        return config
    return {}


def main() -> int:
    args = parse_args()
    state = json.loads(Path(args.state).read_text(encoding="utf-8"))
    result = build_invasion_simulation(state, read_simulation_config(args.config))
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    else:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
