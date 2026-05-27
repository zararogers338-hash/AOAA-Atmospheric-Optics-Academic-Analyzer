# -*- coding: utf-8 -*-
"""Graph structure, centrality computation, and community detection for AOAA."""

from typing import Dict, Any, List
from utils.logger import log_info, log_error


def build_cooccurrence_graph(cooc_data: Dict[str, Any]) -> Any:
    """Build a NetworkX graph from co-occurrence data."""
    try:
        import networkx as nx
    except ImportError:
        log_error("networkx not available")
        return None

    G = nx.Graph()
    keywords = cooc_data.get("keywords", [])
    edges = cooc_data.get("edges", [])

    for kw in keywords:
        G.add_node(kw)
    for edge in edges:
        G.add_edge(edge["source"], edge["target"], weight=edge["weight"])

    log_info(f"Graph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G


def compute_centrality(G) -> Dict[str, Dict[str, float]]:
    """Compute various centrality measures."""
    if G is None or G.number_of_nodes() == 0:
        return {"degree": {}, "betweenness": {}, "closeness": {}, "eigenvector": {}}

    import networkx as nx

    result = {
        "degree": dict(nx.degree_centrality(G)),
        "betweenness": dict(nx.betweenness_centrality(G, weight="weight")),
        "closeness": dict(nx.closeness_centrality(G)),
    }

    try:
        result["eigenvector"] = dict(nx.eigenvector_centrality(G, max_iter=500, weight="weight"))
    except Exception:
        result["eigenvector"] = {}

    return result


def detect_communities(G) -> List[set]:
    """Detect communities using greedy modularity."""
    if G is None or G.number_of_nodes() < 3:
        return []

    import networkx as nx
    try:
        from networkx.algorithms.community import greedy_modularity_communities
        communities = list(greedy_modularity_communities(G, weight="weight"))
        log_info(f"Detected {len(communities)} communities")
        return communities
    except Exception as e:
        log_error("Community detection failed", e)
        return []


def classify_atmosphere(analysis_data: Dict[str, Any], centrality: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
    """Classify academic atmosphere zones: high pressure, low pressure, fronts, jet streams."""
    tfidf = analysis_data.get("tfidf", {})
    trend = analysis_data.get("year_trend", {})
    cooc = analysis_data.get("cooccurrence", {})

    global_top = tfidf.get("global_top", [])
    keywords = cooc.get("keywords", [])
    betweenness = centrality.get("betweenness", {})

    # High pressure: top stable keywords with high centrality
    high_pressure = []
    for kw, score in global_top[:10]:
        if betweenness.get(kw, 0) > 0.05:
            high_pressure.append({"keyword": kw, "tfidf": score, "betweenness": betweenness.get(kw, 0)})

    # Low pressure: emerging keywords (lower in global but higher growth if trend data available)
    low_pressure = []
    if len(global_top) > 10:
        for kw, score in global_top[10:25]:
            low_pressure.append({"keyword": kw, "tfidf": score})

    # Fronts: keywords with high betweenness bridging communities
    fronts = []
    sorted_between = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)
    for kw, bc in sorted_between[:5]:
        if bc > 0.1:
            fronts.append({"keyword": kw, "betweenness": bc})

    # Jet streams: high betweenness bridges
    jet_streams = []
    edges = cooc.get("edges", [])
    for edge in edges[:10]:
        src_bc = betweenness.get(edge["source"], 0)
        tgt_bc = betweenness.get(edge["target"], 0)
        if src_bc > 0.05 or tgt_bc > 0.05:
            jet_streams.append(edge)

    return {
        "high_pressure": high_pressure,
        "low_pressure": low_pressure,
        "fronts": fronts,
        "jet_streams": jet_streams
    }
