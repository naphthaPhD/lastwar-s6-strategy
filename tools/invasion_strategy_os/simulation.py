from __future__ import annotations

import argparse
import json
import re
import sys
from collections import deque
from datetime import datetime, time, timedelta
from pathlib import Path
from typing import Any


FISHERY_TYPE = "漁場"
CITY_TYPE = "都市"
DEFAULT_FRIENDLY_AFFILIATIONS = {"self", "ally"}
DEFAULT_INTERIOR_AFFILIATIONS = {"self", "ally", "unowned"}
DEFAULT_SELF_AFFILIATIONS = {"self"}
CENTRAL_AREA = "中央"


def build_invasion_simulation(state: dict[str, Any], config: dict[str, Any] | None = None) -> dict[str, Any]:
    config = config or {}
    nodes = {str(node.get("id")): node for node in state.get("nodes", []) if node.get("id")}
    adjacency, edge_lookup = build_adjacency(state.get("connections", []), nodes)
    generated_at = parse_datetime(state.get("generated_at"))
    max_items = int(config.get("max_items", 30))
    friendly_affiliations = {str(value) for value in config.get("friendly_affiliations", DEFAULT_FRIENDLY_AFFILIATIONS)}
    interior_affiliations = {str(value) for value in config.get("interior_affiliations", DEFAULT_INTERIOR_AFFILIATIONS)}
    self_affiliations = {str(value) for value in config.get("self_affiliations", DEFAULT_SELF_AFFILIATIONS)}
    depths = [int(value) for value in config.get("interior_depths", [1, 2, 3])]
    pacts = build_pact_context(state, nodes, generated_at)

    context = {
        "state": state,
        "nodes": nodes,
        "adjacency": adjacency,
        "edge_lookup": edge_lookup,
        "generated_at": generated_at,
        "config": config,
        "friendly_affiliations": friendly_affiliations,
        "interior_affiliations": interior_affiliations,
        "self_affiliations": self_affiliations,
        "pacts": pacts,
        "owner_power_by_key": build_owner_power_by_key(nodes),
        "articulation_points": set(str(node_id) for node_id in state.get("articulation_points", [])),
        "critical_node_ids": extract_node_ids(state.get("critical_nodes", [])),
        "degree_centrality": state.get("degree_centrality", {}) or {},
        "betweenness_centrality": state.get("betweenness_centrality", {}) or {},
        "coalition_sources": [
            node_id for node_id, node in nodes.items()
            if affiliation(node) in friendly_affiliations and is_capturable(node)
        ],
        "self_sources": [
            node_id for node_id, node in nodes.items()
            if affiliation(node) in self_affiliations and is_capturable(node)
        ],
        "enemy_sources": [
            node_id for node_id, node in nodes.items()
            if affiliation(node) == "enemy" and is_capturable(node)
        ],
    }
    context["coalition_reachable"] = reachable_from_sources(adjacency, context["coalition_sources"])
    context["self_reachable"] = reachable_from_sources(adjacency, context["self_sources"])

    legacy = build_legacy_edge_candidates(state, context, max_items)
    node_evaluations = top_items(
        [evaluate_node(node_id, context) for node_id in nodes if is_strategy_target(nodes[node_id])],
        len(nodes),
    )

    defense_priorities = top_items(
        [item for item in node_evaluations if item["classification"] in {"defend", "risk"}],
        max_items,
    )
    attack_priorities = top_items(
        [item for item in node_evaluations if item["classification"] == "attack"],
        max_items,
    )
    interdiction_priorities = top_items(
        [item for item in node_evaluations if item["classification"] == "interdict"],
        max_items,
    )
    risk_watchlist = top_items(
        sorted(node_evaluations, key=lambda item: (-float(item["invasion_score"]), -float(item["score"]))),
        max_items,
    )
    self_risk_watchlist = top_items(
        sorted(
            [item for item in node_evaluations if affiliation(item.get("target", {})) in self_affiliations],
            key=lambda item: (-float(item["invasion_score"]), -float(item["score"])),
        ),
        max_items,
    )
    abandonable_nodes = top_items(
        [item for item in node_evaluations if item["classification"] == "abandonable"],
        max_items,
    )
    coalition_lines = top_items(
        sorted(node_evaluations, key=lambda item: (-float(item["coalition_score"]), -float(item["score"]))),
        max_items,
    )
    protection_watchlist = top_items(
        sorted(
            [item for item in node_evaluations if item["protection_score"] >= 20],
            key=lambda item: (-float(item["protection_score"]), -float(item["score"])),
        ),
        max_items,
    )
    time_sensitive_nodes = top_items(
        sorted(
            [item for item in node_evaluations if item["time_score"] >= 20 or item["protection_score"] >= 20],
            key=lambda item: (-(float(item["time_score"]) + float(item["protection_score"])), -float(item["score"])),
        ),
        max_items,
    )

    result = {
        "engine": "strategic_rule_engine_v2",
        "assumptions": [
            "Input is the current state.json shape, not raw Google Sheets rows.",
            "Node-level strategy scoring is split into choke, isolation, coalition, alliance, invasion, protection, and time functions.",
            "Protection timing uses node.protection.hours_remaining when available.",
            "Battle windows and capture limits are configurable under config.simulation.",
            "Active pact records from state.pacts are used as one-hop enemy access projections.",
            "Trade posts, altars, and the ancestral temple are expected to be isolated before simulation.",
            "Destroyed cities are treated as unavailable connection sources.",
            "GPT is not used by this engine.",
        ],
        "strategic_read": [
            "Defense priorities favor nodes whose loss would fragment friendly reach or weaken coalition lines.",
            "Attack priorities favor reachable enemy or unowned targets with enemy adjacency, central value, and timing feasibility.",
            "Interdiction priorities favor enemy cities or choke nodes whose removal reduces reach.",
            "Risk watchlist flags nodes exposed to enemy adjacency, high enemy power, or near-term battle windows.",
            "Pact threat options flag enemy access that may be opened through active alliance agreements.",
        ],
        "node_evaluations": top_items(node_evaluations, max_items * 4),
        "defense_priorities": defense_priorities,
        "attack_priorities": attack_priorities,
        "interdiction_priorities": interdiction_priorities,
        "risk_watchlist": risk_watchlist,
        "self_risk_watchlist": self_risk_watchlist,
        "server_534_risk_watchlist": self_risk_watchlist,
        "server_534_pact_aware_risk_watchlist": self_risk_watchlist,
        "abandonable_nodes": abandonable_nodes,
        "coalition_lines": coalition_lines,
        "protection_watchlist": protection_watchlist,
        "time_sensitive_nodes": time_sensitive_nodes,
        "interior_depth_counts": collect_boundary_interior_counts(
            nodes,
            adjacency,
            friendly_affiliations,
            interior_affiliations,
            depths,
        ),
        "rule_config": normalized_rule_config(config),
        **legacy,
    }
    result["rule_score_samples"] = top_items(
        result["defense_priorities"] + result["attack_priorities"] + result["interdiction_priorities"] + result["risk_watchlist"],
        max_items,
    )
    return result


def build_legacy_edge_candidates(state: dict[str, Any], context: dict[str, Any], max_items: int) -> dict[str, Any]:
    nodes = context["nodes"]
    friendly_affiliations = context["friendly_affiliations"]
    self_affiliations = context["self_affiliations"]
    friendly_pressure: list[dict[str, Any]] = []
    enemy_threats: list[dict[str, Any]] = []
    self_enemy_threats: list[dict[str, Any]] = []
    friendly_expansion: list[dict[str, Any]] = []
    enemy_expansion: list[dict[str, Any]] = []
    attack_score_options: list[dict[str, Any]] = []
    server_534_attack_options: list[dict[str, Any]] = []
    interdiction_score_options: list[dict[str, Any]] = []
    risk_avoidance_options: list[dict[str, Any]] = []
    self_risk_avoidance_options: list[dict[str, Any]] = []
    pact_threat_options: list[dict[str, Any]] = []
    self_pact_threat_options: list[dict[str, Any]] = []

    city_destruction_active, city_destruction_window = battle_window_status(context["generated_at"], context["config"]) if context["generated_at"] else (False, None)

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
            if pact_projection_factor(context, source_id, target_id)["candidate"]:
                record = candidate_record(context, source_id, target_id, "enemy_pact_projection", "pact_threat")
                pact_threat_options.append(record)
                if target_affiliation in self_affiliations:
                    self_pact_threat_options.append(record)
            if pact_projection_factor(context, target_id, source_id)["candidate"]:
                record = candidate_record(context, target_id, source_id, "enemy_pact_projection", "pact_threat")
                pact_threat_options.append(record)
                if source_affiliation in self_affiliations:
                    self_pact_threat_options.append(record)
            if source_affiliation in friendly_affiliations and target_affiliation == "enemy":
                friendly_pressure.append(candidate_record(context, source_id, target_id, "friendly_to_enemy_boundary", "simple"))
                enemy_record = candidate_record(context, target_id, source_id, "enemy_to_friendly_boundary", "risk")
                enemy_threats.append(enemy_record)
                if source_affiliation in self_affiliations:
                    self_enemy_threats.append(enemy_record)
                attack_score_options.append(candidate_record(context, source_id, target_id, "attack_score", "attack"))
                risk_record = candidate_record(context, source_id, target_id, "risk_avoidance", "risk")
                risk_avoidance_options.append(risk_record)
                if source_affiliation in self_affiliations:
                    self_risk_avoidance_options.append(risk_record)
            elif target_affiliation in friendly_affiliations and source_affiliation == "enemy":
                friendly_pressure.append(candidate_record(context, target_id, source_id, "friendly_to_enemy_boundary", "simple"))
                enemy_record = candidate_record(context, source_id, target_id, "enemy_to_friendly_boundary", "risk")
                enemy_threats.append(enemy_record)
                if target_affiliation in self_affiliations:
                    self_enemy_threats.append(enemy_record)
                attack_score_options.append(candidate_record(context, target_id, source_id, "attack_score", "attack"))
                risk_record = candidate_record(context, target_id, source_id, "risk_avoidance", "risk")
                risk_avoidance_options.append(risk_record)
                if target_affiliation in self_affiliations:
                    self_risk_avoidance_options.append(risk_record)
            elif source_affiliation in friendly_affiliations and target_affiliation == "unowned":
                friendly_expansion.append(candidate_record(context, source_id, target_id, "friendly_to_unowned", "expansion"))
            elif target_affiliation in friendly_affiliations and source_affiliation == "unowned":
                friendly_expansion.append(candidate_record(context, target_id, source_id, "friendly_to_unowned", "expansion"))
            elif source_affiliation == "enemy" and target_affiliation == "unowned":
                enemy_expansion.append(candidate_record(context, source_id, target_id, "enemy_to_unowned", "expansion"))
            elif target_affiliation == "enemy" and source_affiliation == "unowned":
                enemy_expansion.append(candidate_record(context, target_id, source_id, "enemy_to_unowned", "expansion"))

            if source_affiliation in self_affiliations and target_affiliation in {"enemy", "unowned"}:
                server_534_attack_options.append(candidate_record(context, source_id, target_id, "server_534_attack", "attack" if target_affiliation == "enemy" else "expansion"))
            if target_affiliation in self_affiliations and source_affiliation in {"enemy", "unowned"}:
                server_534_attack_options.append(candidate_record(context, target_id, source_id, "server_534_attack", "attack" if source_affiliation == "enemy" else "expansion"))
        elif is_fishery(source) and source_affiliation in friendly_affiliations and is_city(target) and target_affiliation == "enemy":
            interdiction_score_options.append(candidate_record(context, source_id, target_id, "interdiction_score", "interdiction"))
            if source_affiliation in self_affiliations and city_destruction_active:
                server_534_attack_options.append(candidate_record(context, source_id, target_id, "server_534_city_destroy", "interdiction"))
        elif is_fishery(target) and target_affiliation in friendly_affiliations and is_city(source) and source_affiliation == "enemy":
            interdiction_score_options.append(candidate_record(context, target_id, source_id, "interdiction_score", "interdiction"))
            if target_affiliation in self_affiliations and city_destruction_active:
                server_534_attack_options.append(candidate_record(context, target_id, source_id, "server_534_city_destroy", "interdiction"))

    return {
        "friendly_pressure_options": top_items(friendly_pressure, max_items),
        "enemy_threat_options": top_items(enemy_threats, max_items),
        "self_enemy_threat_options": top_items(self_enemy_threats, max_items),
        "server_534_enemy_threat_options": top_items(self_enemy_threats, max_items),
        "friendly_expansion_options": top_items(friendly_expansion, max_items),
        "enemy_expansion_options": top_items(enemy_expansion, max_items),
        "attack_score_options": top_items(attack_score_options, max_items),
        "server_534_attack_options": top_items(server_534_attack_options, max_items),
        "server_534_city_destruction_active": city_destruction_active,
        "server_534_city_destruction_window": city_destruction_window,
        "interdiction_score_options": top_items(interdiction_score_options, max_items),
        "risk_avoidance_options": top_items(risk_avoidance_options, max_items),
        "self_risk_avoidance_options": top_items(self_risk_avoidance_options, max_items),
        "server_534_risk_avoidance_options": top_items(self_risk_avoidance_options, max_items),
        "pact_threat_options": top_items(pact_threat_options, max_items),
        "self_pact_threat_options": top_items(self_pact_threat_options, max_items),
        "server_534_pact_threat_options": top_items(self_pact_threat_options, max_items),
    }


def evaluate_node(node_id: str, context: dict[str, Any]) -> dict[str, Any]:
    node = context["nodes"][node_id]
    scores = {
        "choke": choke_score(node_id, context),
        "isolation": isolation_score(node_id, context),
        "coalition": coalition_score(node_id, context),
        "alliance": alliance_score(node_id, context),
        "invasion": invasion_score(node_id, context),
        "protection": protection_score(node_id, context),
        "time": time_score(node_id, context),
    }
    defense_score = weighted_score(scores, {
        "choke": 0.16,
        "isolation": 0.24,
        "coalition": 0.20,
        "alliance": 0.12,
        "invasion": 0.10,
        "protection": 0.10,
        "time": 0.08,
    })
    attack_score = weighted_score(scores, {
        "invasion": 0.26,
        "choke": 0.16,
        "coalition": 0.16,
        "alliance": 0.16,
        "isolation": 0.08,
        "protection": 0.08,
        "time": 0.10,
    })
    interdiction_score_value = weighted_score(scores, {
        "isolation": 0.28,
        "choke": 0.20,
        "coalition": 0.16,
        "invasion": 0.14,
        "alliance": 0.06,
        "protection": 0.08,
        "time": 0.08,
    })
    classification, score = classify_node(node, defense_score, attack_score, interdiction_score_value, scores)
    reasons = merge_reasons(
        scores["choke"],
        scores["isolation"],
        scores["coalition"],
        scores["alliance"],
        scores["invasion"],
        scores["protection"],
        scores["time"],
        limit=8,
    )
    summary = node_summary(node)
    return {
        "node": summary["name"],
        "node_id": summary["id"],
        "target": summary,
        "score": round(score, 4),
        "classification": classification,
        "defense_score": round(defense_score, 4),
        "attack_score": round(attack_score, 4),
        "interdiction_score": round(interdiction_score_value, 4),
        "choke_score": scores["choke"]["score"],
        "isolation_score": scores["isolation"]["score"],
        "coalition_score": scores["coalition"]["score"],
        "alliance_score": scores["alliance"]["score"],
        "invasion_score": scores["invasion"]["score"],
        "protection_score": scores["protection"]["score"],
        "time_score": scores["time"]["score"],
        "reasons": reasons,
        "details": scores,
    }


def choke_score(node_id: str, context: dict[str, Any]) -> dict[str, Any]:
    nodes = context["nodes"]
    adjacency = context["adjacency"]
    node = nodes[node_id]
    degree = len(adjacency.get(node_id, set()))
    betweenness = float(context["betweenness_centrality"].get(node_id, 0) or 0)
    degree_centrality = float(context["degree_centrality"].get(node_id, 0) or 0)
    central = central_connection_factor(node_id, nodes, adjacency)
    raw = 0.0
    reasons: list[str] = []
    if node_id in context["articulation_points"]:
        raw += 35
        reasons.append("CHOKE候補")
    if node_id in context["critical_node_ids"]:
        raw += 20
        reasons.append("重要接続点")
    if betweenness >= 0.01:
        raw += min(25, betweenness * 300)
        reasons.append("主要通路")
    if central["score"] > 0:
        raw += min(25, central["score"])
        reasons.extend(central["reasons"])
    if 0 < degree <= 2:
        raw += 10
        reasons.append("経路限定")
    raw += min(10, float(node.get("importance") or 0))
    return score_result(raw, reasons, {
        "is_articulation_point": node_id in context["articulation_points"],
        "degree": degree,
        "degree_centrality": round(degree_centrality, 6),
        "betweenness": round(betweenness, 6),
        "central_neighbors": central.get("central_neighbors", []),
    })


def isolation_score(node_id: str, context: dict[str, Any]) -> dict[str, Any]:
    nodes = context["nodes"]
    adjacency = context["adjacency"]
    sources = [source for source in context["coalition_sources"] if source != node_id]
    before_set = set(context["coalition_reachable"])
    after_set = reachable_from_sources(adjacency, sources, removed_id=node_id)
    lost = before_set - after_set - {node_id}
    before = len(before_set)
    after = len(after_set)
    lost_count = len(lost)
    lost_ratio = lost_count / before if before else 0.0
    isolated_friendly = [lost_id for lost_id in lost if affiliation(nodes[lost_id]) in context["friendly_affiliations"]]
    isolated_major = [
        lost_id for lost_id in lost
        if float(nodes[lost_id].get("importance") or 0) >= 8 or is_city(nodes[lost_id])
    ]
    raw = min(45, lost_ratio * 90) + min(25, len(isolated_major) * 5) + min(20, len(isolated_friendly) * 0.8)
    central_lost = any(str(nodes[lost_id].get("area", "")) == CENTRAL_AREA for lost_id in lost)
    reasons: list[str] = []
    if lost_count:
        reasons.append(f"到達可能数 {before} → {after}")
    if lost_ratio >= 0.5:
        reasons.append("喪失時に大規模分断")
    elif lost_ratio >= 0.2:
        reasons.append("喪失時に分断リスク")
    if isolated_friendly:
        reasons.append(f"味方拠点 {len(isolated_friendly)} 件が孤立")
    if isolated_major:
        reasons.append(f"重要拠点 {len(isolated_major)} 件が孤立")
    if central_lost:
        raw += 15
        reasons.append("中央接続喪失")
    return score_result(raw, reasons, {
        "before_reachable": before,
        "after_reachable": after,
        "lost_reachable": lost_count,
        "lost_ratio": round(lost_ratio, 4),
        "isolated_friendly_nodes": len(isolated_friendly),
        "isolated_major_nodes": len(isolated_major),
        "central_lost": central_lost,
        "sample_lost_nodes": sorted(lost)[:12],
    })


def coalition_score(node_id: str, context: dict[str, Any]) -> dict[str, Any]:
    nodes = context["nodes"]
    adjacency = context["adjacency"]
    node = nodes[node_id]
    neighbors = [nodes[neighbor_id] for neighbor_id in adjacency.get(node_id, set())]
    friendly_neighbors = [neighbor for neighbor in neighbors if affiliation(neighbor) in context["friendly_affiliations"]]
    enemy_neighbors = [neighbor for neighbor in neighbors if affiliation(neighbor) == "enemy"]
    connected_areas = sorted({str(neighbor.get("area", "")) for neighbor in friendly_neighbors if neighbor.get("area")})
    central = central_connection_factor(node_id, nodes, adjacency)
    raw = 0.0
    reasons: list[str] = []
    if affiliation(node) in context["friendly_affiliations"]:
        raw += 15
        reasons.append("味方グループ保有")
    if len(connected_areas) >= 2:
        raw += 25
        reasons.append("味方連盟間の接続維持")
    if central["score"] > 0:
        raw += min(25, central["score"])
        reasons.extend(central["reasons"])
    if enemy_neighbors:
        raw += min(15, len(enemy_neighbors) * 3)
        reasons.append("グループ防衛ライン")
    if context["nodes"][node_id].get("area") in connected_areas:
        raw += 5
    raw += min(15, len(friendly_neighbors) * 2)
    return score_result(raw, reasons, {
        "connected_friendly_areas": connected_areas,
        "friendly_neighbor_count": len(friendly_neighbors),
        "enemy_neighbor_count": len(enemy_neighbors),
        "central_connection": central["score"] > 0,
        "coalition_line": bool(enemy_neighbors and friendly_neighbors),
    })


def alliance_score(node_id: str, context: dict[str, Any]) -> dict[str, Any]:
    nodes = context["nodes"]
    adjacency = context["adjacency"]
    node = nodes[node_id]
    neighbors = [nodes[neighbor_id] for neighbor_id in adjacency.get(node_id, set())]
    self_neighbors = [neighbor for neighbor in neighbors if affiliation(neighbor) in context["self_affiliations"]]
    ally_neighbors = [neighbor for neighbor in neighbors if affiliation(neighbor) == "ally"]
    enemy_neighbors = [neighbor for neighbor in neighbors if affiliation(neighbor) == "enemy"]
    owned_by_self = affiliation(node) in context["self_affiliations"]
    raw = min(20, float(node.get("importance") or 0) * 2)
    reasons: list[str] = []
    if owned_by_self:
        raw += 25
        reasons.append("自連盟保有")
    if self_neighbors:
        raw += min(20, len(self_neighbors) * 4)
        reasons.append("自連盟隣接")
    if ally_neighbors:
        raw += min(10, len(ally_neighbors) * 2)
        reasons.append("味方隣接")
    if enemy_neighbors:
        raw += min(15, len(enemy_neighbors) * 3)
        reasons.append("自連盟境界リスク")
    if str(node.get("area", "")) == "#534":
        raw += 8
        reasons.append("#534エリア")
    return score_result(raw, reasons, {
        "owned_by_self": owned_by_self,
        "self_neighbor_count": len(self_neighbors),
        "ally_neighbor_count": len(ally_neighbors),
        "enemy_neighbor_count": len(enemy_neighbors),
    })


def invasion_score(node_id: str, context: dict[str, Any]) -> dict[str, Any]:
    nodes = context["nodes"]
    adjacency = context["adjacency"]
    node = nodes[node_id]
    neighbors = [nodes[neighbor_id] for neighbor_id in adjacency.get(node_id, set())]
    enemy_neighbors = [neighbor for neighbor in neighbors if affiliation(neighbor) == "enemy"]
    enemy_fisheries = [neighbor for neighbor in enemy_neighbors if is_fishery(neighbor)]
    enemy_cities = [neighbor for neighbor in enemy_neighbors if is_city(neighbor)]
    strong_enemy_neighbors = [
        str(neighbor.get("owner") or neighbor.get("display_owner") or neighbor.get("id"))
        for neighbor in enemy_neighbors
        if power_value(neighbor) >= float(context["config"].get("strong_enemy_power", 20_000_000_000))
    ]
    enemy_distance = nearest_distance(context["adjacency"], context["enemy_sources"], node_id, max_depth=8)
    raw = len(enemy_fisheries) * 10 + len(enemy_cities) * 12 + min(20, len(strong_enemy_neighbors) * 10)
    reasons: list[str] = []
    if enemy_neighbors:
        reasons.append("敵隣接")
    if strong_enemy_neighbors:
        reasons.append("高戦力敵連盟隣接")
    if enemy_distance is not None:
        raw += max(0, 20 - enemy_distance * 3)
        if enemy_distance <= 2:
            reasons.append(f"敵到達距離{enemy_distance}")
    if affiliation(node) == "unowned" and enemy_neighbors:
        raw += 10
        reasons.append("未取得地経由リスク")
    protection = protection_factor(node)
    if protection["status"] == "expired" or (is_number(protection.get("hours_remaining")) and float(protection["hours_remaining"]) <= 6):
        raw += 10
        reasons.extend(protection["reasons"][:1])
    pact_threat = pact_threat_factor(node_id, context)
    if pact_threat["candidate"]:
        raw += pact_threat["score"]
        reasons.extend(pact_threat["reasons"])
    return score_result(raw, reasons, {
        "enemy_neighbor_count": len(enemy_neighbors),
        "enemy_fishery_neighbors": len(enemy_fisheries),
        "enemy_city_neighbors": len(enemy_cities),
        "strong_enemy_neighbors": sorted(set(strong_enemy_neighbors)),
        "enemy_distance": enemy_distance,
        "pact_threat": pact_threat,
    })


def protection_score(node_id: str, context: dict[str, Any]) -> dict[str, Any]:
    node = context["nodes"][node_id]
    factor = protection_factor(node)
    hours = factor.get("hours_remaining")
    raw = 0.0
    reasons: list[str] = []
    status = str(factor.get("status") or "unknown")
    if status == "expired" or (is_number(hours) and float(hours) <= 0):
        raw += 35
        reasons.append("保護切れ")
    elif is_number(hours):
        hours_float = float(hours)
        if hours_float <= 6:
            raw += 25
            reasons.append("保護終了6h以内")
        elif hours_float <= 12:
            raw += 15
            reasons.append("保護終了12h以内")
        elif hours_float <= 24:
            raw += 8
            reasons.append("保護終了24h以内")
        else:
            raw -= 20
            reasons.append("保護中")
    else:
        reasons.append("保護不明")
    renewal = protection_renewal_probability(node)
    if renewal == "high":
        raw -= 15
        reasons.append("保護更新可能性高")
    elif renewal == "low":
        raw += 10
        reasons.append("保護更新可能性低")
    return score_result(raw, reasons, {
        "protect_until": factor.get("protect_until") or node.get("protect_until"),
        "hours_remaining": hours,
        "status": status,
        "renewal_probability": renewal,
    })


def time_score(node_id: str, context: dict[str, Any]) -> dict[str, Any]:
    now = context.get("generated_at")
    if now is None:
        return score_result(0, ["現在時刻不明"], {"now": None})
    in_window, active_window = battle_window_status(now, context["config"])
    next_window = next_battle_window(now, context["config"])
    hours_to_next = ((next_window["starts_at"] - now).total_seconds() / 3600) if next_window else None
    raw = 0.0
    reasons: list[str] = []
    if in_window:
        raw += 30
        reasons.append("戦闘可能時間")
    elif hours_to_next is not None:
        if hours_to_next <= 6:
            raw += 20
            reasons.append("戦闘可能時間まで6h以内")
        elif hours_to_next <= 12:
            raw += 12
            reasons.append("戦闘可能時間まで12h以内")
        elif hours_to_next > 24:
            raw -= 15
            reasons.append("戦闘日から24h超")
    active_battle_day = battle_window_day(active_window)
    if active_battle_day == "saturday":
        raw += 15
        reasons.append("土曜戦闘日")
    elif active_battle_day == "wednesday":
        raw += 10
        reasons.append("水曜戦闘日")
    response_window = response_window_factor(context["nodes"][node_id], now, context["config"])
    raw += response_window["score"]
    reasons.extend(response_window["reasons"])
    return score_result(raw, reasons, {
        "now": now.isoformat(),
        "active_battle_window": active_window,
        "next_battle_window_starts_at": next_window["starts_at"].isoformat() if next_window else None,
        "hours_to_next_battle_window": round(hours_to_next, 2) if hours_to_next is not None else None,
        "battle_day": active_battle_day,
        "response_window_active": bool(response_window["active"]),
    })


def build_briefing_input(state: dict[str, Any], simulation: dict[str, Any] | None = None, config: dict[str, Any] | None = None) -> dict[str, Any]:
    simulation = simulation or state.get("invasion_simulation", {}) or {}
    config = config or {}
    limit = int(config.get("briefing_items", 10))
    return {
        "generated_at": state.get("generated_at"),
        "engine": simulation.get("engine"),
        "scenario": {
            "friendly_affiliations": simulation.get("rule_config", {}).get("friendly_affiliations", ["self", "ally"]),
            "battle_windows": simulation.get("rule_config", {}).get("battle_windows", []),
        },
        "top_defense": briefing_records(simulation.get("defense_priorities", []), limit),
        "top_attack": briefing_records(simulation.get("attack_priorities", []), limit),
        "top_server_534_attack": briefing_records(simulation.get("server_534_attack_options", []), limit),
        "top_interdiction": briefing_records(simulation.get("interdiction_priorities", []), limit),
        "top_pact_threats": briefing_records(simulation.get("pact_threat_options", []), limit),
        "top_self_pact_threats": briefing_records(simulation.get("self_pact_threat_options", []), limit),
        "top_server_534_pact_threats": briefing_records(simulation.get("server_534_pact_threat_options", []), limit),
        "top_server_534_pact_aware_risks": briefing_records(simulation.get("server_534_pact_aware_risk_watchlist", []), limit),
        "risk_watchlist": briefing_records(simulation.get("risk_watchlist", []), limit),
        "self_risk_watchlist": briefing_records(simulation.get("self_risk_watchlist", []), limit),
        "server_534_risk_watchlist": briefing_records(simulation.get("server_534_risk_watchlist", []), limit),
        "time_sensitive": briefing_records(simulation.get("time_sensitive_nodes", []), limit),
        "protection_watchlist": briefing_records(simulation.get("protection_watchlist", []), limit),
        "coalition_lines": briefing_records(simulation.get("coalition_lines", []), limit),
        "assumptions": simulation.get("assumptions", []),
        "missing_data": [
            "保護更新可能性が未登録の拠点は unknown として評価",
            "実稼働人数は未反映",
            "外交上の攻撃禁止対象は未反映",
            "占領上限は設定値または暫定推定を使用",
        ],
    }


def briefing_records(items: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    records = []
    for item in items[:limit]:
        record = {
            "node": item.get("node"),
            "node_id": item.get("node_id"),
            "score": item.get("score"),
            "classification": item.get("classification"),
            "label": item.get("label"),
            "reasons": item.get("reasons", [])[:6],
            "scores": {
                "alliance": item.get("alliance_score"),
                "coalition": item.get("coalition_score"),
                "choke": item.get("choke_score"),
                "isolation": item.get("isolation_score"),
                "invasion": item.get("invasion_score"),
                "protection": item.get("protection_score"),
                "time": item.get("time_score"),
            },
        }
        if item.get("source"):
            record["source"] = item.get("source")
        if item.get("target"):
            record["target"] = item.get("target")
        records.append(record)
    return records


def weighted_score(scores: dict[str, dict[str, Any]], weights: dict[str, float]) -> float:
    return sum(float(scores[key]["score"]) * weight for key, weight in weights.items())


def classify_node(
    node: dict[str, Any],
    defense_score: float,
    attack_score: float,
    interdiction_score_value: float,
    scores: dict[str, dict[str, Any]],
) -> tuple[str, float]:
    node_affiliation = affiliation(node)
    if node_affiliation in DEFAULT_FRIENDLY_AFFILIATIONS:
        if defense_score < 18 and float(scores["invasion"]["score"]) < 15:
            return "abandonable", defense_score
        if float(scores["invasion"]["score"]) >= 45:
            return "risk", max(defense_score, float(scores["invasion"]["score"]))
        return "defend", defense_score
    alliance_details = scores["alliance"].get("details", {})
    friendly_neighbor_count = int(alliance_details.get("self_neighbor_count", 0) or 0) + int(alliance_details.get("ally_neighbor_count", 0) or 0)
    if is_city(node) and node_affiliation == "enemy" and friendly_neighbor_count > 0:
        return "interdict", interdiction_score_value
    if node_affiliation in {"enemy", "unowned"}:
        return "attack", attack_score
    return "optional", max(defense_score, attack_score, interdiction_score_value)


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
    return sorted(items, key=lambda item: (-float(item.get("score", 0)), str(item.get("node_id") or item.get("target", {}).get("id", ""))))[:max_items]


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
    pact_threat = pact_projection_factor(context, source_id, target_id)
    if model == "attack":
        score = target_importance * 1.3 + protection["score"] + battle["score"] + capture["score"] + central["score"] + enemy_adjacent["score"] * 0.7 + (power_ratio or source_power / 1_000_000_000) * 1.5 - counterattack["score"] * 0.75
    elif model == "interdiction":
        score = target_importance * 2.0 + protection["score"] + battle["score"] + interdiction["score"] + enemy_adjacent["score"] * 0.45 + central["score"] * 0.55 - counterattack["score"] * 0.35
    elif model == "risk":
        score = counterattack["score"] * 2.2 + enemy_adjacent["score"] * 0.9 + central["score"] * 0.4 + max(0.0, (enemy_power_ratio or 0) - 1.0) * 5 - protection["score"] * 0.25
    elif model == "pact_threat":
        score = target_importance * 1.15 + pact_threat["score"] * 2.0 + protection["score"] * 0.55 + battle["score"] + central["score"] * 0.65 + enemy_adjacent["score"] * 0.35 - counterattack["score"] * 0.2
    elif model == "expansion":
        score = target_importance + protection["score"] + battle["score"] + central["score"] + capture["score"] - counterattack["score"] * 0.4
    else:
        score = target_importance + (power_ratio or source_power / 1_000_000_000)
    reasons = collect_reasons(protection, battle, capture, central, enemy_adjacent, counterattack, interdiction, pact_threat)
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
            "pact_threat": pact_threat,
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


def merge_reasons(*results: dict[str, Any], limit: int = 8) -> list[str]:
    reasons: list[str] = []
    ranked = sorted(results, key=lambda item: float(item.get("score", 0)), reverse=True)
    for result in ranked:
        reasons.extend(str(reason) for reason in result.get("reasons", []))
    return list(dict.fromkeys(reason for reason in reasons if reason))[:limit]


def protection_factor(node: dict[str, Any]) -> dict[str, Any]:
    protection = node.get("protection") or {}
    status = str(protection.get("status") or node.get("protectStatus") or "unknown")
    hours = protection.get("hours_remaining", node.get("hoursRemaining"))
    protect_until = protection.get("protect_until") or node.get("protect_until") or node.get("protectUntil")
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
    return {"status": status, "protect_until": protect_until, "hours_remaining": hours, "score": score, "reasons": reasons}


def battle_window_factor(now: datetime | None, config: dict[str, Any]) -> dict[str, Any]:
    if now is None:
        return {"enabled": False, "score": 0.0, "reasons": ["戦闘時間不明"]}
    active, window = battle_window_status(now, config)
    if active:
        return {"enabled": True, "window": window, "score": 6.0, "reasons": ["戦闘可能時間"]}
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
    enemy_neighbors = [neighbor_id for neighbor_id in adjacency.get(node_id, set()) if affiliation(nodes[neighbor_id]) == "enemy"]
    enemy_fisheries = [node_id for node_id in enemy_neighbors if is_fishery(nodes[node_id])]
    enemy_cities = [node_id for node_id in enemy_neighbors if is_city(nodes[node_id])]
    score = len(enemy_fisheries) * 2.0 + len(enemy_cities) * 3.0
    reasons = []
    if enemy_neighbors:
        reasons.append("敵隣接")
    if len(enemy_neighbors) >= 3:
        reasons.append("敵密集")
    return {"enemy_neighbors": sorted(enemy_neighbors), "enemy_fisheries": sorted(enemy_fisheries), "enemy_cities": sorted(enemy_cities), "score": score, "reasons": reasons}


def build_pact_context(state: dict[str, Any], nodes: dict[str, dict[str, Any]], now: datetime | None) -> dict[str, Any]:
    pacts = state.get("pacts", {}) or {}
    records = [record for record in pacts.get("active", []) if isinstance(record, dict)]
    owner_names: dict[str, str] = {}
    for node in nodes.values():
        owner = node_owner(node)
        key = owner_key(owner)
        if key:
            owner_names.setdefault(key, owner)
    for record in records:
        for field in ("alliance_a", "alliance_b"):
            owner = str(record.get(field) or "").strip()
            key = owner_key(owner)
            if key:
                owner_names.setdefault(key, owner)

    partners_by_owner: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        a = str(record.get("alliance_a") or "").strip()
        b = str(record.get("alliance_b") or "").strip()
        a_key = owner_key(a)
        b_key = owner_key(b)
        if not a_key or not b_key:
            continue
        normalized_record = dict(record)
        normalized_record["alliance_a_key"] = a_key
        normalized_record["alliance_b_key"] = b_key
        partners_by_owner.setdefault(a_key, []).append({"partner_key": b_key, "partner": b, "record": normalized_record})
        partners_by_owner.setdefault(b_key, []).append({"partner_key": a_key, "partner": a, "record": normalized_record})

    enemy_owner_keys = sorted({
        owner_key(node_owner(node))
        for node in nodes.values()
        if affiliation(node) == "enemy" and owner_key(node_owner(node))
    })
    enemy_partner_links: dict[str, list[dict[str, Any]]] = {}
    for enemy_key in enemy_owner_keys:
        for partner in partners_by_owner.get(enemy_key, []):
            partner_key = str(partner.get("partner_key") or "")
            if not partner_key:
                continue
            enemy_partner_links.setdefault(partner_key, []).append({
                "enemy_owner_key": enemy_key,
                "enemy_owner": owner_names.get(enemy_key, enemy_key),
                "partner_owner_key": partner_key,
                "partner_owner": owner_names.get(partner_key, str(partner.get("partner") or partner_key)),
                "record": partner.get("record") or {},
            })

    return {
        "active": records,
        "active_count": int(pacts.get("active_count") or len(records)),
        "partners_by_owner": partners_by_owner,
        "enemy_owner_keys": enemy_owner_keys,
        "enemy_partner_links": enemy_partner_links,
        "source": pacts.get("source") or {},
        "generated_at": pacts.get("generated_at"),
        "now": now,
    }


def build_owner_power_by_key(nodes: dict[str, dict[str, Any]]) -> dict[str, float]:
    powers: dict[str, float] = {}
    for node in nodes.values():
        key = owner_key(node_owner(node))
        if not key:
            continue
        powers[key] = max(powers.get(key, 0.0), power_value(node))
    return powers


def pact_projection_factor(context: dict[str, Any], source_id: str, target_id: str) -> dict[str, Any]:
    config = context.get("config", {})
    if (config.get("pact_threat") or {}).get("enabled", True) is False:
        return {"candidate": False, "score": 0.0, "reasons": []}
    nodes = context["nodes"]
    source = nodes.get(source_id)
    target = nodes.get(target_id)
    if not source or not target or source.get("destroyed") or target.get("destroyed"):
        return {"candidate": False, "score": 0.0, "reasons": []}
    if not is_fishery(source) or not is_capturable(target):
        return {"candidate": False, "score": 0.0, "reasons": []}

    target_affiliation = affiliation(target)
    if target_affiliation == "enemy" or (target_affiliation not in context["friendly_affiliations"] and target_affiliation != "unowned"):
        return {"candidate": False, "score": 0.0, "reasons": []}

    source_key = owner_key(node_owner(source))
    if not source_key or affiliation(source) == "enemy":
        return {"candidate": False, "score": 0.0, "reasons": []}
    links = context["pacts"].get("enemy_partner_links", {}).get(source_key, [])
    if not links:
        return {"candidate": False, "score": 0.0, "reasons": []}

    unique_enemies = sorted({str(link.get("enemy_owner") or "") for link in links if link.get("enemy_owner")})
    enemy_power_values = [
        context["owner_power_by_key"].get(owner_key(str(link.get("enemy_owner") or "")), 0.0)
        for link in links
    ]
    max_enemy_power = max(enemy_power_values) if enemy_power_values else 0.0
    confidence_score = sum(pact_confidence_weight((link.get("record") or {}).get("confidence")) for link in links)
    safety = pact_safety_window_effect([link.get("record") or {} for link in links], context.get("generated_at"))

    score = min(28.0, len(unique_enemies) * 8.0 + confidence_score * 4.0)
    if target_affiliation in context["friendly_affiliations"]:
        score += 9.0
    elif target_affiliation == "unowned":
        score += 5.0
    if max_enemy_power >= float(config.get("strong_enemy_power", 20_000_000_000)):
        score += 8.0
    score += safety["score"]

    reasons = ["協定込み敵侵攻経路"]
    if unique_enemies:
        reasons.append("協定敵: " + ", ".join(unique_enemies[:3]))
    if target_affiliation in context["friendly_affiliations"]:
        reasons.append("味方側へ協定経由で隣接")
    if max_enemy_power >= float(config.get("strong_enemy_power", 20_000_000_000)):
        reasons.append("高戦力敵が協定先に存在")
    reasons.extend(safety["reasons"])

    return {
        "candidate": True,
        "score": round(max(0.0, score), 4),
        "reasons": list(dict.fromkeys(reasons)),
        "source_id": source_id,
        "target_id": target_id,
        "source_owner": node_owner(source),
        "target_owner": node_owner(target),
        "enemy_owners": unique_enemies,
        "max_enemy_power": int(max_enemy_power) if max_enemy_power else None,
        "pact_count": len(links),
        "pacts": [link.get("record") or {} for link in links],
        "safety_window": safety,
    }


def pact_threat_factor(node_id: str, context: dict[str, Any]) -> dict[str, Any]:
    adjacency = context["adjacency"]
    sources = []
    total_score = 0.0
    for source_id in sorted(adjacency.get(node_id, set())):
        projection = pact_projection_factor(context, source_id, node_id)
        if not projection["candidate"]:
            continue
        sources.append(projection)
        total_score += float(projection["score"])
    if not sources:
        return {"candidate": False, "score": 0.0, "reasons": []}
    enemy_owners = sorted({enemy for source in sources for enemy in source.get("enemy_owners", [])})
    reasons = ["協定込み敵侵攻リスク"]
    if enemy_owners:
        reasons.append("協定敵: " + ", ".join(enemy_owners[:4]))
    return {
        "candidate": True,
        "score": round(min(42.0, total_score), 4),
        "reasons": reasons,
        "source_count": len(sources),
        "enemy_owners": enemy_owners,
        "sources": sources[:8],
    }


def pact_confidence_weight(confidence: Any) -> float:
    value = str(confidence or "").lower()
    if value == "high":
        return 1.0
    if value == "medium":
        return 0.75
    if value == "low":
        return 0.45
    return 0.6


def pact_safety_window_effect(records: list[dict[str, Any]], now: datetime | None) -> dict[str, Any]:
    if now is None:
        return {"active": False, "score": 0.0, "reasons": []}
    for record in records:
        status = safety_window_status(str(record.get("safety_window") or ""), now)
        if status["active"]:
            return {"active": True, "score": -6.0, "reasons": ["協定安全期間中"], "window": status.get("window")}
    return {"active": False, "score": 0.0, "reasons": []}


def safety_window_status(text: str, now: datetime) -> dict[str, Any]:
    for match in re.finditer(r"(\d{1,2}):(\d{2})\s*[-~－〜]\s*(\d{1,2}):(\d{2})", text):
        start = time(int(match.group(1)), int(match.group(2)))
        end = time(int(match.group(3)), int(match.group(4)))
        current = now.time()
        active = start <= current <= end if start <= end else current >= start or current <= end
        if active:
            return {"active": True, "window": match.group(0)}
    return {"active": False}


def node_owner(node: dict[str, Any]) -> str:
    return str(node.get("owner") or node.get("display_owner") or "").strip()


def owner_key(owner: Any) -> str:
    return re.sub(r"\s+", "", str(owner or "").strip()).lower()


def interdiction_factor(node_id: str, nodes: dict[str, dict[str, Any]], adjacency: dict[str, set[str]], friendly_affiliations: set[str]) -> dict[str, Any]:
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
    return {"candidate": bool(friendly_fisheries), "friendly_fishery_neighbors": friendly_fisheries, "enemy_fishery_neighbors": enemy_fisheries, "neighbor_groups_after_destroy": groups, "score": score, "reasons": reasons}


def central_connection_factor(node_id: str, nodes: dict[str, dict[str, Any]], adjacency: dict[str, set[str]]) -> dict[str, Any]:
    node = nodes[node_id]
    central_neighbors = sorted(neighbor_id for neighbor_id in adjacency.get(node_id, set()) if str(nodes[neighbor_id].get("area", "")) == CENTRAL_AREA)
    score = 0.0
    reasons: list[str] = []
    if str(node.get("area", "")) == CENTRAL_AREA:
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
    return {"enemy_neighbor_count": len(enemy_neighbors), "max_enemy_neighbor_power": int(max_enemy_power) if max_enemy_power else None, "enemy_to_source_power_ratio": round(enemy_ratio, 4) if enemy_ratio else None, "score": score, "reasons": reasons}


def collect_boundary_interior_counts(nodes: dict[str, dict[str, Any]], adjacency: dict[str, set[str]], friendly_affiliations: set[str], interior_affiliations: set[str], depths: list[int]) -> dict[str, Any]:
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


def reachable_from_sources(adjacency: dict[str, set[str]], sources: list[str], removed_id: str | None = None) -> set[str]:
    starts = [source for source in sources if source != removed_id and source in adjacency]
    visited: set[str] = set()
    queue = deque(starts)
    while queue:
        node_id = queue.popleft()
        if node_id == removed_id or node_id in visited:
            continue
        visited.add(node_id)
        for neighbor_id in adjacency.get(node_id, set()):
            if neighbor_id != removed_id and neighbor_id not in visited:
                queue.append(neighbor_id)
    return visited


def nearest_distance(adjacency: dict[str, set[str]], sources: list[str], target_id: str, max_depth: int = 8) -> int | None:
    if target_id in sources:
        return 0
    visited = set(sources)
    queue = deque((source, 0) for source in sources if source in adjacency)
    while queue:
        node_id, depth = queue.popleft()
        if depth >= max_depth:
            continue
        for neighbor_id in adjacency.get(node_id, set()):
            if neighbor_id in visited:
                continue
            if neighbor_id == target_id:
                return depth + 1
            visited.add(neighbor_id)
            queue.append((neighbor_id, depth + 1))
    return None


def count_owned_capturable_nodes(owner: str, nodes: dict[str, dict[str, Any]]) -> int:
    if not owner:
        return 0
    return sum(1 for node in nodes.values() if str(node.get("owner") or "") == owner and is_capturable(node))


def normalized_rule_config(config: dict[str, Any]) -> dict[str, Any]:
    return {
        "max_items": int(config.get("max_items", 30)),
        "friendly_affiliations": list(config.get("friendly_affiliations", sorted(DEFAULT_FRIENDLY_AFFILIATIONS))),
        "interior_affiliations": list(config.get("interior_affiliations", sorted(DEFAULT_INTERIOR_AFFILIATIONS))),
        "battle_windows": config.get("battle_windows") or default_battle_windows(),
        "capture_limit": config.get("capture_limit") or {"enabled": True, "default_limit": 6, "usage_source": "owned_nodes"},
        "pact_threat": config.get("pact_threat") or {"enabled": True, "mode": "one_hop_enemy_partner_projection"},
    }


def score_result(raw_score: float, reasons: list[str], details: dict[str, Any]) -> dict[str, Any]:
    return {
        "score": round(clamp(raw_score), 4),
        "raw_score": round(raw_score, 4),
        "normalized": True,
        "reasons": list(dict.fromkeys(reason for reason in reasons if reason)),
        "details": details,
    }


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def is_strategy_target(node: dict[str, Any]) -> bool:
    return is_fishery(node) or is_city(node)


def is_capturable(node: dict[str, Any]) -> bool:
    return not node.get("destroyed") and (is_fishery(node) or is_city(node))


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


def extract_node_ids(items: Any) -> set[str]:
    ids: set[str] = set()
    if not isinstance(items, list):
        return ids
    for item in items:
        if isinstance(item, dict):
            value = item.get("id") or item.get("node_id") or item.get("node")
        else:
            value = item
        if value:
            ids.add(str(value))
    return ids


def protection_renewal_probability(node: dict[str, Any]) -> str:
    protection = node.get("protection") or {}
    value = protection.get("renewal_probability") or protection.get("renewalProbability") or node.get("renewal_probability")
    if value:
        return str(value).lower()
    memo = str(node.get("memo") or "")
    if "更新不可" in memo or "renewal low" in memo.lower():
        return "low"
    if "更新可能" in memo or "renewal high" in memo.lower():
        return "high"
    return "unknown"


def default_battle_windows() -> list[dict[str, Any]]:
    return [
        {"label": "wednesday_server_day", "weekday": 2, "start": "11:00", "end": "10:59"},
        {"label": "saturday_server_day", "weekday": 5, "start": "11:00", "end": "10:59"},
    ]


def battle_windows(config: dict[str, Any]) -> list[dict[str, Any]]:
    return config.get("battle_windows") or (config.get("battle_rules") or {}).get("weekly_windows") or default_battle_windows()


def battle_window_status(now: datetime, config: dict[str, Any]) -> tuple[bool, dict[str, Any] | None]:
    for window in battle_windows(config):
        weekday = int(window.get("weekday", -1))
        start = parse_time(str(window.get("start", "00:00")))
        end = parse_time(str(window.get("end", "23:59")))
        current = now.time()
        if start <= end and weekday == now.weekday() and start <= current <= end:
            return True, window
        if start > end:
            if weekday == now.weekday() and current >= start:
                return True, window
            if (weekday + 1) % 7 == now.weekday() and current <= end:
                return True, window
    return False, None


def battle_window_day(window: dict[str, Any] | None) -> str | None:
    if not window:
        return None
    label = str(window.get("label") or "").lower()
    if "saturday" in label:
        return "saturday"
    if "wednesday" in label:
        return "wednesday"
    weekday = int(window.get("weekday", -1))
    if weekday == 5:
        return "saturday"
    if weekday == 2:
        return "wednesday"
    return None


def next_battle_window(now: datetime, config: dict[str, Any]) -> dict[str, Any] | None:
    candidates: list[dict[str, Any]] = []
    for offset in range(0, 14):
        day = now + timedelta(days=offset)
        for window in battle_windows(config):
            if int(window.get("weekday", -1)) != day.weekday():
                continue
            starts_at = datetime.combine(day.date(), parse_time(str(window.get("start", "00:00"))), tzinfo=now.tzinfo)
            if starts_at >= now:
                candidates.append({"window": window, "starts_at": starts_at})
    return min(candidates, key=lambda item: item["starts_at"]) if candidates else None


def response_window_factor(node: dict[str, Any], now: datetime, config: dict[str, Any]) -> dict[str, Any]:
    hours = float((config.get("battle_rules") or {}).get("response_window_hours", config.get("response_window_hours", 24)))
    acquired_at = parse_loose_datetime(node.get("acquired_at"), now)
    if not acquired_at:
        return {"active": False, "score": 0.0, "reasons": []}
    elapsed = (now - acquired_at).total_seconds() / 3600
    if 0 <= elapsed <= hours:
        return {"active": True, "score": 20.0, "reasons": ["応戦期間中"]}
    return {"active": False, "score": 0.0, "reasons": []}


def parse_loose_datetime(value: Any, now: datetime) -> datetime | None:
    if not value:
        return None
    text = str(value).strip()
    for fmt in ("%Y/%m/%d %H:%M", "%Y/%m/%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M"):
        try:
            parsed = datetime.strptime(text, fmt)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=now.tzinfo)
            return parsed
        except ValueError:
            continue
    return parse_datetime(text)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Phase 3 strategy rule engine against state.json.")
    parser.add_argument("--state", default="sample_output/state.json", help="Input state.json path.")
    parser.add_argument("--config", help="Optional config JSON path. Uses its simulation block when present.")
    parser.add_argument("--output", help="Optional simulation JSON output path. Writes to stdout when omitted.")
    parser.add_argument("--briefing-output", default="sample_output/briefing_input.json", help="Compressed briefing JSON output path.")
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
    config = read_simulation_config(args.config)
    result = build_invasion_simulation(state, config)
    briefing = build_briefing_input(state, result, config)
    if args.briefing_output:
        Path(args.briefing_output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.briefing_output).write_text(json.dumps(briefing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
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
