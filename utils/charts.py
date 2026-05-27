# -*- coding: utf-8 -*-
"""
Advanced Visualization Module for AOAA.
Provides 15+ chart types using Plotly + Matplotlib for powerful academic data visualization.
All charts are bilingual (zh/en) and gracefully handle missing data.
"""

import numpy as np
import io
from typing import Dict, Any, List, Optional, Tuple
from utils.i18n import get_lang

# ─── Color Palettes ───
AURORA_PALETTE = [
    "#00ff88", "#00ccff", "#ff6644", "#ffaa00", "#cc44ff",
    "#ff4488", "#44ffcc", "#8888ff", "#ffcc44", "#44ff88",
    "#ff8844", "#4488ff", "#ff44cc", "#88ff44", "#ff4444",
]
ATMOSPHERE_GRADIENT = [
    "#0a0a2e", "#1a1a4e", "#2a3a6e", "#3a5a8e", "#4a7aae",
    "#6a9ace", "#8abaee", "#aadaff", "#ccebff", "#eef8ff",
]
HEATMAP_COLORSCALE = "YlOrRd"
PHENOMENON_COLORS = {
    "aurora": "#00ff88", "noctilucent": "#6699ff", "nacreous": "#ff88cc",
    "asperitas": "#ff6644", "lenticular": "#aabbcc", "circumhorizontal": "#ff4444",
    "fallstreak": "#88ccee", "brocken": "#dddd88", "moonbow": "#9988cc",
}


def _get_plotly():
    """Lazy import plotly."""
    try:
        import plotly.graph_objects as go
        import plotly.express as px
        from plotly.subplots import make_subplots
        return go, px, make_subplots
    except ImportError:
        return None, None, None


def _get_matplotlib():
    """Lazy import matplotlib."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial']
        matplotlib.rcParams['axes.unicode_minus'] = False
        return plt
    except ImportError:
        return None


def _label(zh: str, en: str) -> str:
    return zh if get_lang() == "zh" else en


def _hex_to_rgba(hex_color: str, alpha: float = 0.5) -> str:
    """Convert hex color (#RRGGBB) to rgba() string for Plotly compatibility."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


# ═══════════════════════════════════════════════════════════════════
# 1. NIGHTINGALE ROSE CHART (南丁格尔玫瑰图)
# ═══════════════════════════════════════════════════════════════════
def rose_chart(keywords: List[Tuple[str, float]], title: str = "",
               color: str = "#00ff88", max_items: int = 12):
    """Nightingale rose chart for keyword scores."""
    go, px, _ = _get_plotly()
    if go is None or not keywords:
        return None

    items = keywords[:max_items]
    names = [kw for kw, _ in items]
    values = [max(s, 0.001) for _, s in items]

    n = len(names)
    colors = [AURORA_PALETTE[i % len(AURORA_PALETTE)] for i in range(n)]

    fig = go.Figure()
    fig.add_trace(go.Barpolar(
        r=values,
        theta=names,
        marker_color=colors,
        marker_line_color="rgba(255,255,255,0.3)",
        marker_line_width=1,
        opacity=0.85,
        hovertemplate="%{theta}<br>Score: %{r:.4f}<extra></extra>"
    ))

    fig.update_layout(
        title=dict(text=title or _label("🌹 南丁格尔玫瑰图", "🌹 Nightingale Rose Chart"),
                   font=dict(size=16)),
        polar=dict(
            radialaxis=dict(visible=True, showticklabels=True, gridcolor="rgba(255,255,255,0.15)"),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
            bgcolor="rgba(10,10,46,0.8)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        height=500,
        margin=dict(t=60, b=40, l=40, r=40),
    )
    return fig


def _get_node_label_mode() -> bool:
    """Get the global node label toggle state from session state."""
    try:
        import streamlit as st
        return st.session_state.get("show_node_labels", True)
    except Exception:
        return True


def _filter_labels_by_priority(names: list, values: list, top_ratio: float = 0.5) -> list:
    """Return labels with only top-N important ones shown (others become '').
    Used when node labels are ON but we want to prioritize important nodes.
    Always keeps at least the top `top_ratio` fraction visible."""
    if not names or not values:
        return names
    n_show = max(1, int(len(names) * top_ratio))
    # Find indices of top values
    indexed = sorted(enumerate(values), key=lambda x: x[1], reverse=True)
    top_indices = set(i for i, _ in indexed[:n_show])
    return [name if i in top_indices else "" for i, name in enumerate(names)]


# ═══════════════════════════════════════════════════════════════════
# 2. SCATTER ROSE CHART (散点玫瑰图)
# ═══════════════════════════════════════════════════════════════════
def scatter_rose_chart(matched_kws: List[Dict], title: str = ""):
    """Polar scatter chart showing keyword distribution by match score & connections."""
    go, _, _ = _get_plotly()
    if go is None or not matched_kws:
        return None

    names = [kw["keyword"][:18] for kw in matched_kws]
    scores = [kw["match_score"] for kw in matched_kws]
    tfidfs = [kw["tfidf"] for kw in matched_kws]
    connections = [kw.get("connections", 1) for kw in matched_kws]

    n = len(names)
    angles = np.linspace(0, 360, n, endpoint=False).tolist()
    sizes = [max(8, min(40, c * 3 + 8)) for c in connections]
    colors = AURORA_PALETTE[:n]

    # Apply node label toggle: show labels based on priority or hide all
    show_labels = _get_node_label_mode()
    if show_labels:
        display_names = _filter_labels_by_priority(names, scores, top_ratio=0.6)
    else:
        display_names = [""] * n

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=angles,
        mode="markers+text",
        text=display_names,
        customdata=names,
        textposition="top center",
        textfont=dict(size=9, color="white"),
        marker=dict(
            size=sizes,
            color=tfidfs,
            colorscale="Viridis",
            showscale=True,
            colorbar=dict(title=dict(text="TF-IDF", font=dict(color="white")), tickfont=dict(color="white")),
            line=dict(width=1, color="white"),
            opacity=0.85,
        ),
        hovertemplate="%{customdata}<br>Score: %{r:.4f}<br>TF-IDF: %{marker.color:.4f}<extra></extra>"
    ))

    fig.update_layout(
        title=dict(text=title or _label("🌸 散点玫瑰图", "🌸 Scatter Rose Chart"),
                   font=dict(size=16)),
        polar=dict(
            radialaxis=dict(visible=True, gridcolor="rgba(255,255,255,0.15)"),
            angularaxis=dict(visible=False),
            bgcolor="rgba(10,10,46,0.8)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        height=500,
        margin=dict(t=60, b=40, l=40, r=40),
    )
    return fig


# ═══════════════════════════════════════════════════════════════════
# 3. LINE STATISTICS CHART (折线统计图)
# ═══════════════════════════════════════════════════════════════════
def line_statistics_chart(year_trend: Dict[str, Any], title: str = ""):
    """Enhanced line chart with trend line, confidence band, and dual Y axis."""
    go, _, make_subplots = _get_plotly()
    if go is None:
        return None

    years = year_trend.get("years", [])
    counts = year_trend.get("counts", [])
    avg_cit = year_trend.get("avg_citations", [])

    if not years or len(years) < 2:
        return None

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Publication count - area + line
    fig.add_trace(go.Scatter(
        x=years, y=counts, mode="lines+markers",
        name=_label("发文量", "Publications"),
        line=dict(color="#00ff88", width=3),
        marker=dict(size=8, color="#00ff88", line=dict(width=2, color="white")),
        fill="tozeroy", fillcolor="rgba(0,255,136,0.15)",
        hovertemplate="%{x}<br>" + _label("发文量", "Pubs") + ": %{y}<extra></extra>",
    ), secondary_y=False)

    # Moving average
    if len(counts) >= 3:
        window = min(3, len(counts))
        ma = np.convolve(counts, np.ones(window) / window, mode="valid")
        ma_years = years[window - 1:]
        fig.add_trace(go.Scatter(
            x=ma_years, y=ma.tolist(), mode="lines",
            name=_label(f"{window}年移动均线", f"{window}Y Moving Avg"),
            line=dict(color="#ffaa00", width=2, dash="dash"),
        ), secondary_y=False)

    # Confidence band
    if len(counts) >= 3:
        std = np.std(counts) * 0.5
        upper = [c + std for c in counts]
        lower = [max(0, c - std) for c in counts]
        fig.add_trace(go.Scatter(
            x=years + years[::-1],
            y=upper + lower[::-1],
            fill="toself", fillcolor="rgba(0,255,136,0.08)",
            line=dict(width=0), showlegend=False, hoverinfo="skip",
        ), secondary_y=False)

    # Average citations on secondary Y
    if avg_cit and any(c > 0 for c in avg_cit):
        fig.add_trace(go.Bar(
            x=years, y=avg_cit,
            name=_label("平均引用", "Avg Citations"),
            marker_color="rgba(255,102,68,0.6)",
            marker_line=dict(width=0),
            hovertemplate="%{x}<br>" + _label("引用", "Citations") + ": %{y:.1f}<extra></extra>",
        ), secondary_y=True)

    # Trend line (linear regression)
    if len(years) >= 3:
        z = np.polyfit(range(len(years)), counts, 1)
        trend_line = np.polyval(z, range(len(years)))
        fig.add_trace(go.Scatter(
            x=years, y=trend_line.tolist(), mode="lines",
            name=_label("趋势线", "Trend"),
            line=dict(color="#cc44ff", width=2, dash="dot"),
        ), secondary_y=False)

    fig.update_layout(
        title=dict(text=title or _label("📈 折线统计图", "📈 Line Statistics Chart"),
                   font=dict(size=16)),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(10,10,46,0.8)",
        font=dict(color="white"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.1)", title=_label("年份", "Year")),
        yaxis=dict(gridcolor="rgba(255,255,255,0.1)", title=_label("发文量", "Publications")),
        yaxis2=dict(gridcolor="rgba(255,255,255,0.05)", title=_label("引用数", "Citations")),
        legend=dict(bgcolor="rgba(0,0,0,0.5)", bordercolor="rgba(255,255,255,0.2)"),
        height=450,
        margin=dict(t=60, b=40),
        hovermode="x unified",
    )
    return fig


# ═══════════════════════════════════════════════════════════════════
# 4. CANDLESTICK CHART (蜡烛图 / K线图)
# ═══════════════════════════════════════════════════════════════════
def candlestick_chart(matched_kws: List[Dict], title: str = ""):
    """Candlestick-style chart treating keywords as 'academic stocks'.
    Open = TF-IDF base, High = match_score, Low = tfidf * 0.5, Close = connections-weighted."""
    go, _, _ = _get_plotly()
    if go is None or not matched_kws:
        return None

    names = [kw["keyword"][:15] for kw in matched_kws[:15]]
    opens = [kw["tfidf"] for kw in matched_kws[:15]]
    highs = [kw["match_score"] for kw in matched_kws[:15]]
    lows = [kw["tfidf"] * 0.3 for kw in matched_kws[:15]]
    closes = [kw["tfidf"] * (1 + kw.get("connections", 0) * 0.05)
              for kw in matched_kws[:15]]

    # Normalize so everything is on same scale
    all_vals = opens + highs + lows + closes
    max_v = max(all_vals) if all_vals else 1
    if max_v == 0:
        max_v = 1

    colors_inc = ["rgba(0,255,136,0.8)"] * len(names)
    colors_dec = ["rgba(255,68,68,0.8)"] * len(names)

    fig = go.Figure(data=[go.Candlestick(
        x=names,
        open=opens,
        high=highs,
        low=lows,
        close=closes,
        increasing=dict(line=dict(color="#00ff88"), fillcolor="rgba(0,255,136,0.4)"),
        decreasing=dict(line=dict(color="#ff4444"), fillcolor="rgba(255,68,68,0.4)"),
        hovertext=[f"{n}<br>TF-IDF: {o:.4f}<br>Score: {h:.4f}<br>Floor: {l:.4f}<br>Adjusted: {c:.4f}"
                   for n, o, h, l, c in zip(names, opens, highs, lows, closes)],
    )])

    fig.update_layout(
        title=dict(text=title or _label("🕯️ 学术K线图", "🕯️ Academic Candlestick Chart"),
                   font=dict(size=16)),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(10,10,46,0.8)",
        font=dict(color="white"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.1)", title=_label("关键词", "Keywords"),
                   rangeslider=dict(visible=False)),
        yaxis=dict(gridcolor="rgba(255,255,255,0.1)", title=_label("学术影响力", "Academic Impact")),
        height=450,
        margin=dict(t=60, b=80),
    )
    return fig


# ═══════════════════════════════════════════════════════════════════
# 5. WORD CLOUD (词云)
# ═══════════════════════════════════════════════════════════════════
def word_cloud_figure(keywords: List[Tuple[str, float]], title: str = "",
                      color: str = "#00ff88"):
    """Generate word cloud as matplotlib figure."""
    plt = _get_matplotlib()
    if plt is None or not keywords:
        return None

    try:
        from wordcloud import WordCloud
    except ImportError:
        # Fallback: create manual text-scatter word cloud with matplotlib
        return _manual_word_cloud(keywords, title, color)

    freq = {kw: max(score * 10000, 1) for kw, score in keywords[:60]}

    def color_func(word, font_size, position, orientation, **kwargs):
        idx = list(freq.keys()).index(word) if word in freq else 0
        c = AURORA_PALETTE[idx % len(AURORA_PALETTE)]
        # Convert hex to RGB
        r, g, b = int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)
        return f"rgb({r},{g},{b})"

    wc = WordCloud(
        width=800, height=400,
        background_color="#0a0a2e",
        max_words=60,
        color_func=color_func,
        prefer_horizontal=0.7,
        min_font_size=10,
        max_font_size=80,
    ).generate_from_frequencies(freq)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    ax.set_title(title or _label("☁️ 学术词云", "☁️ Academic Word Cloud"),
                 color="white", fontsize=14, pad=10)
    fig.patch.set_facecolor("#0a0a2e")
    plt.tight_layout()
    return fig


def _manual_word_cloud(keywords, title, color):
    """Fallback word cloud using matplotlib scatter text."""
    plt = _get_matplotlib()
    if plt is None:
        return None

    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor("#0a0a2e")
    ax.set_facecolor("#0a0a2e")

    np.random.seed(42)
    items = keywords[:30]
    max_score = max(s for _, s in items) if items else 1

    for i, (kw, score) in enumerate(items):
        x = np.random.uniform(0.05, 0.95)
        y = np.random.uniform(0.1, 0.9)
        size = 8 + (score / max_score) * 28
        c = AURORA_PALETTE[i % len(AURORA_PALETTE)]
        ax.text(x, y, kw, fontsize=size, color=c, alpha=0.85,
                ha="center", va="center", fontweight="bold",
                transform=ax.transAxes)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title(title or _label("☁️ 学术词云", "☁️ Academic Word Cloud"),
                 color="white", fontsize=14, pad=10)
    plt.tight_layout()
    return fig


# ═══════════════════════════════════════════════════════════════════
# 6. STACKED AREA CHART (层状堆积图)
# ═══════════════════════════════════════════════════════════════════
def stacked_area_chart(analysis_data: Dict[str, Any], title: str = ""):
    """Stacked area chart showing keyword category evolution across documents."""
    go, _, _ = _get_plotly()
    if go is None:
        return None

    per_doc = analysis_data.get("tfidf", {}).get("per_doc", [])
    global_top = analysis_data.get("tfidf", {}).get("global_top", [])

    if not per_doc or not global_top:
        return None

    top_kws = [kw for kw, _ in global_top[:8]]
    n_docs = len(per_doc)
    doc_labels = [f"Doc {i + 1}" for i in range(n_docs)]

    fig = go.Figure()
    for k, kw in enumerate(top_kws):
        values = []
        for doc_kws in per_doc:
            doc_dict = dict(doc_kws)
            values.append(doc_dict.get(kw, 0))

        fig.add_trace(go.Scatter(
            x=doc_labels, y=values,
            name=kw[:18],
            mode="lines",
            line=dict(width=0.5, color=AURORA_PALETTE[k % len(AURORA_PALETTE)]),
            stackgroup="one",
            fillcolor=_hex_to_rgba(AURORA_PALETTE[k % len(AURORA_PALETTE)], 0.4),
            hovertemplate=f"{kw[:18]}<br>" + "Doc %{{x}}<br>Score: %{{y:.4f}}<extra></extra>",
        ))

    fig.update_layout(
        title=dict(text=title or _label("📊 层状堆积图", "📊 Stacked Area Chart"),
                   font=dict(size=16)),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(10,10,46,0.8)",
        font=dict(color="white"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.1)", title=_label("文档", "Documents")),
        yaxis=dict(gridcolor="rgba(255,255,255,0.1)", title="TF-IDF"),
        legend=dict(bgcolor="rgba(0,0,0,0.5)", font=dict(size=10)),
        height=450, margin=dict(t=60, b=40),
        hovermode="x unified",
    )
    return fig


# ═══════════════════════════════════════════════════════════════════
# 7. TREEMAP (树状地壳图)
# ═══════════════════════════════════════════════════════════════════
def treemap_chart(analysis_data: Dict[str, Any], title: str = "",
                  atmosphere_data: Dict[str, Any] = None):
    """Treemap showing keyword hierarchy and their academic 'territory'."""
    go, px, _ = _get_plotly()
    if go is None:
        return None

    global_top = analysis_data.get("tfidf", {}).get("global_top", [])
    if not global_top:
        return None

    labels = [_label("学术大气层", "Academic Atmosphere")]
    parents = [""]
    values = [0]
    colors_list = ["rgba(10,10,46,0.8)"]

    # Group into pressure zones
    hp_kws = set()
    lp_kws = set()
    if atmosphere_data:
        hp_kws = {item["keyword"] for item in atmosphere_data.get("high_pressure", [])}
        lp_kws = {item["keyword"] for item in atmosphere_data.get("low_pressure", [])}

    # Add zone categories
    for zone, zone_label_zh, zone_label_en, zone_color in [
        ("high", "高压区", "High Pressure", "#2196F3"),
        ("low", "低压槽", "Low Pressure", "#FF9800"),
        ("neutral", "中性层", "Neutral", "#9E9E9E"),
    ]:
        labels.append(_label(zone_label_zh, zone_label_en))
        parents.append(_label("学术大气层", "Academic Atmosphere"))
        values.append(0)
        colors_list.append(zone_color)

    # Add keywords
    for kw, score in global_top[:25]:
        if kw in hp_kws:
            parent = _label("高压区", "High Pressure")
        elif kw in lp_kws:
            parent = _label("低压槽", "Low Pressure")
        else:
            parent = _label("中性层", "Neutral")

        labels.append(kw[:20])
        parents.append(parent)
        values.append(max(score * 10000, 1))
        idx = global_top.index((kw, score))
        colors_list.append(AURORA_PALETTE[idx % len(AURORA_PALETTE)])

    fig = go.Figure(go.Treemap(
        labels=labels,
        parents=parents,
        values=values,
        marker=dict(
            colors=colors_list,
            line=dict(width=2, color="rgba(255,255,255,0.3)"),
        ),
        textinfo="label+value",
        textfont=dict(size=12),
        hovertemplate="<b>%{label}</b><br>Score: %{value:.1f}<extra></extra>",
    ))

    fig.update_layout(
        title=dict(text=title or _label("🌍 学术地壳图", "🌍 Academic Treemap"),
                   font=dict(size=16)),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        height=500, margin=dict(t=60, b=20, l=20, r=20),
    )
    return fig


# ═══════════════════════════════════════════════════════════════════
# 8. RADAR CHART (雷达图)
# ═══════════════════════════════════════════════════════════════════
def radar_chart(matched_kws: List[Dict], title: str = "", color: str = "#00ff88"):
    """Multi-dimensional radar chart for keyword analysis."""
    go, _, _ = _get_plotly()
    if go is None or not matched_kws:
        return None

    items = matched_kws[:8]
    categories = [kw["keyword"][:15] for kw in items]

    # Normalize each dimension to 0-1
    tfidfs = [kw["tfidf"] for kw in items]
    scores = [kw["match_score"] for kw in items]
    conns = [kw.get("connections", 0) for kw in items]

    def normalize(arr):
        mx = max(arr) if arr and max(arr) > 0 else 1
        return [v / mx for v in arr]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=normalize(tfidfs) + [normalize(tfidfs)[0]],
        theta=categories + [categories[0]],
        fill="toself", fillcolor="rgba(0,255,136,0.15)",
        line=dict(color="#00ff88", width=2),
        name="TF-IDF",
    ))
    fig.add_trace(go.Scatterpolar(
        r=normalize(scores) + [normalize(scores)[0]],
        theta=categories + [categories[0]],
        fill="toself", fillcolor="rgba(255,170,0,0.15)",
        line=dict(color="#ffaa00", width=2),
        name=_label("匹配得分", "Match Score"),
    ))
    fig.add_trace(go.Scatterpolar(
        r=normalize(conns) + [normalize(conns)[0]],
        theta=categories + [categories[0]],
        fill="toself", fillcolor="rgba(204,68,255,0.15)",
        line=dict(color="#cc44ff", width=2),
        name=_label("共现连接", "Connections"),
    ))

    fig.update_layout(
        title=dict(text=title or _label("🕸️ 多维雷达图", "🕸️ Multi-Dim Radar Chart"),
                   font=dict(size=16)),
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1.1], gridcolor="rgba(255,255,255,0.15)"),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
            bgcolor="rgba(10,10,46,0.8)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        legend=dict(bgcolor="rgba(0,0,0,0.5)"),
        height=500, margin=dict(t=60, b=40),
    )
    return fig


# ═══════════════════════════════════════════════════════════════════
# 9. HEATMAP (热力图)
# ═══════════════════════════════════════════════════════════════════
def heatmap_chart(analysis_data: Dict[str, Any], title: str = ""):
    """Co-occurrence heatmap for keyword relationships."""
    go, _, _ = _get_plotly()
    if go is None:
        return None

    cooc = analysis_data.get("cooccurrence", {})
    keywords = cooc.get("keywords", [])[:20]
    edges = cooc.get("edges", [])

    if not keywords or not edges:
        return None

    n = len(keywords)
    matrix = np.zeros((n, n))
    kw_idx = {kw: i for i, kw in enumerate(keywords)}

    for e in edges:
        src, tgt = e["source"], e["target"]
        if src in kw_idx and tgt in kw_idx:
            i, j = kw_idx[src], kw_idx[tgt]
            matrix[i][j] = e["weight"]
            matrix[j][i] = e["weight"]

    short_names = [kw[:12] for kw in keywords]

    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        x=short_names,
        y=short_names,
        colorscale="YlOrRd",
        hovertemplate="%{y} ↔ %{x}<br>" + _label("权重", "Weight") + ": %{z}<extra></extra>",
        colorbar=dict(title=dict(text=_label("共现权重", "Co-occur Weight"), font=dict(color="white")),
                      tickfont=dict(color="white")),
    ))

    fig.update_layout(
        title=dict(text=title or _label("🔥 共现热力图", "🔥 Co-occurrence Heatmap"),
                   font=dict(size=16)),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(10,10,46,0.8)",
        font=dict(color="white"),
        xaxis=dict(tickangle=45, tickfont=dict(size=9), title=_label("关键词", "Keywords")),
        yaxis=dict(tickfont=dict(size=9), autorange="reversed", title=_label("关键词", "Keywords")),
        height=550, margin=dict(t=60, b=100, l=100),
    )
    return fig


# ═══════════════════════════════════════════════════════════════════
# 10. BUBBLE CHART (气泡图)
# ═══════════════════════════════════════════════════════════════════
def bubble_chart(matched_kws: List[Dict], title: str = ""):
    """Bubble chart: x=TF-IDF, y=match_score, size=connections."""
    go, _, _ = _get_plotly()
    if go is None or not matched_kws:
        return None

    names = [kw["keyword"][:18] for kw in matched_kws]
    tfidfs = [kw["tfidf"] for kw in matched_kws]
    scores = [kw["match_score"] for kw in matched_kws]
    conns = [kw.get("connections", 1) for kw in matched_kws]
    sizes = [max(10, min(60, c * 2 + 10)) for c in conns]
    colors = [AURORA_PALETTE[i % len(AURORA_PALETTE)] for i in range(len(names))]

    # Apply node label toggle: show labels based on priority (size/score) or hide all
    show_labels = _get_node_label_mode()
    if show_labels:
        display_names = _filter_labels_by_priority(names, scores, top_ratio=0.5)
    else:
        display_names = [""] * len(names)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=tfidfs, y=scores,
        mode="markers+text",
        text=display_names,
        customdata=names,
        textposition="top center",
        textfont=dict(size=8, color="white"),
        marker=dict(
            size=sizes,
            color=colors,
            line=dict(width=1, color="white"),
            opacity=0.75,
        ),
        hovertemplate="%{customdata}<br>TF-IDF: %{x:.4f}<br>Score: %{y:.4f}<extra></extra>",
    ))

    fig.update_layout(
        title=dict(text=title or _label("🫧 气泡分析图", "🫧 Bubble Analysis Chart"),
                   font=dict(size=16)),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(10,10,46,0.8)",
        font=dict(color="white"),
        xaxis=dict(title="TF-IDF", gridcolor="rgba(255,255,255,0.1)"),
        yaxis=dict(title=_label("匹配得分", "Match Score"), gridcolor="rgba(255,255,255,0.1)"),
        height=450, margin=dict(t=60, b=50),
    )
    return fig


# ═══════════════════════════════════════════════════════════════════
# 11. SUNBURST CHART (旭日图)
# ═══════════════════════════════════════════════════════════════════
def sunburst_chart(analysis_data: Dict[str, Any], atmosphere_data: Dict[str, Any] = None,
                   title: str = ""):
    """Sunburst chart showing hierarchical keyword relationships."""
    go, _, _ = _get_plotly()
    if go is None:
        return None

    global_top = analysis_data.get("tfidf", {}).get("global_top", [])
    edges = analysis_data.get("cooccurrence", {}).get("edges", [])
    if not global_top:
        return None

    ids = ["ROOT"]
    labels = [_label("学术生态", "Academic Ecosystem")]
    parents = [""]
    values = [1]
    marker_colors = ["rgba(10,10,46,0.9)"]

    # Add top keywords as first ring
    for i, (kw, score) in enumerate(global_top[:15]):
        ids.append(kw)
        labels.append(kw[:15])
        parents.append("ROOT")
        values.append(max(score * 10000, 1))
        marker_colors.append(AURORA_PALETTE[i % len(AURORA_PALETTE)])

    # Add connected keywords as second ring
    top_kw_set = {kw for kw, _ in global_top[:15]}
    added = set()
    for e in edges[:50]:
        src, tgt, w = e["source"], e["target"], e["weight"]
        if src in top_kw_set and tgt not in top_kw_set:
            child_id = f"{src}_{tgt}"
            if child_id not in added:
                ids.append(child_id)
                labels.append(tgt[:12])
                parents.append(src)
                values.append(max(w * 10, 1))
                marker_colors.append("rgba(255,255,255,0.3)")
                added.add(child_id)
        elif tgt in top_kw_set and src not in top_kw_set:
            child_id = f"{tgt}_{src}"
            if child_id not in added:
                ids.append(child_id)
                labels.append(src[:12])
                parents.append(tgt)
                values.append(max(w * 10, 1))
                marker_colors.append("rgba(255,255,255,0.3)")
                added.add(child_id)

    fig = go.Figure(go.Sunburst(
        ids=ids, labels=labels, parents=parents, values=values,
        branchvalues="remainder",
        marker=dict(colors=marker_colors, line=dict(width=1, color="rgba(255,255,255,0.2)")),
        hovertemplate="<b>%{label}</b><br>Score: %{value:.1f}<extra></extra>",
        textfont=dict(size=10),
    ))

    fig.update_layout(
        title=dict(text=title or _label("🌞 旭日层级图", "🌞 Sunburst Hierarchy"),
                   font=dict(size=16)),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        height=550, margin=dict(t=60, b=20, l=20, r=20),
    )
    return fig


# ═══════════════════════════════════════════════════════════════════
# 12. SANKEY DIAGRAM (桑基图)
# ═══════════════════════════════════════════════════════════════════
def sankey_chart(analysis_data: Dict[str, Any], title: str = ""):
    """Sankey flow diagram showing keyword relationship flows."""
    go, _, _ = _get_plotly()
    if go is None:
        return None

    edges = analysis_data.get("cooccurrence", {}).get("edges", [])[:30]
    if not edges:
        return None

    # Collect unique nodes
    node_set = set()
    for e in edges:
        node_set.add(e["source"])
        node_set.add(e["target"])
    nodes = sorted(node_set)
    node_idx = {n: i for i, n in enumerate(nodes)}

    sources = [node_idx[e["source"]] for e in edges]
    targets = [node_idx[e["target"]] for e in edges]
    values = [e["weight"] for e in edges]

    node_colors = [AURORA_PALETTE[i % len(AURORA_PALETTE)] for i in range(len(nodes))]
    link_colors = [_hex_to_rgba(AURORA_PALETTE[s % len(AURORA_PALETTE)], 0.3) for s in sources]

    fig = go.Figure(go.Sankey(
        node=dict(
            pad=15, thickness=20,
            line=dict(color="white", width=0.5),
            label=[n[:15] for n in nodes],
            color=node_colors,
        ),
        link=dict(
            source=sources, target=targets, value=values,
            color=link_colors,
        ),
    ))

    fig.update_layout(
        title=dict(text=title or _label("🌊 知识流向桑基图", "🌊 Knowledge Flow Sankey"),
                   font=dict(size=16)),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white", size=10),
        height=500, margin=dict(t=60, b=20),
    )
    return fig


# ═══════════════════════════════════════════════════════════════════
# 13. VIOLIN PLOT (小提琴图)
# ═══════════════════════════════════════════════════════════════════
def violin_chart(analysis_data: Dict[str, Any], title: str = ""):
    """Violin plot showing TF-IDF score distribution across documents."""
    go, _, _ = _get_plotly()
    if go is None:
        return None

    per_doc = analysis_data.get("tfidf", {}).get("per_doc", [])
    if not per_doc:
        return None

    fig = go.Figure()

    # Collect all scores per document
    for i, doc_kws in enumerate(per_doc[:10]):
        if doc_kws:
            scores = [s for _, s in doc_kws if s > 0]
            if scores:
                fig.add_trace(go.Violin(
                    y=scores,
                    name=f"Doc {i + 1}",
                    box_visible=True,
                    meanline_visible=True,
                    fillcolor=_hex_to_rgba(AURORA_PALETTE[i % len(AURORA_PALETTE)], 0.4),
                    line_color=AURORA_PALETTE[i % len(AURORA_PALETTE)],
                    opacity=0.7,
                ))

    fig.update_layout(
        title=dict(text=title or _label("🎻 TF-IDF 分布小提琴图", "🎻 TF-IDF Distribution Violin"),
                   font=dict(size=16)),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(10,10,46,0.8)",
        font=dict(color="white"),
        yaxis=dict(title="TF-IDF Score", gridcolor="rgba(255,255,255,0.1)"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.1)", title=_label("文档", "Documents")),
        showlegend=False,
        height=450, margin=dict(t=60, b=40),
    )
    return fig


# ═══════════════════════════════════════════════════════════════════
# 14. 3D SURFACE (3D 曲面图)
# ═══════════════════════════════════════════════════════════════════
def surface_3d_chart(analysis_data: Dict[str, Any], title: str = ""):
    """3D surface plot of co-occurrence matrix."""
    go, _, _ = _get_plotly()
    if go is None:
        return None

    cooc = analysis_data.get("cooccurrence", {})
    keywords = cooc.get("keywords", [])[:15]
    edges = cooc.get("edges", [])

    if not keywords or not edges:
        return None

    n = len(keywords)
    matrix = np.zeros((n, n))
    kw_idx = {kw: i for i, kw in enumerate(keywords)}

    for e in edges:
        if e["source"] in kw_idx and e["target"] in kw_idx:
            i, j = kw_idx[e["source"]], kw_idx[e["target"]]
            matrix[i][j] = e["weight"]
            matrix[j][i] = e["weight"]

    # Apply Gaussian smoothing for nicer surface
    try:
        from scipy.ndimage import gaussian_filter
        matrix = gaussian_filter(matrix, sigma=0.8)
    except ImportError:
        pass

    short_names = [kw[:10] for kw in keywords]

    fig = go.Figure(data=[go.Surface(
        z=matrix, x=short_names, y=short_names,
        colorscale="Viridis",
        hovertemplate="%{y} × %{x}<br>" + _label("强度", "Intensity") + ": %{z:.1f}<extra></extra>",
        colorbar=dict(title=dict(text=_label("共现强度", "Co-occur"), font=dict(color="white")),
                      tickfont=dict(color="white")),
    )])

    fig.update_layout(
        title=dict(text=title or _label("🏔️ 3D 共现曲面", "🏔️ 3D Co-occurrence Surface"),
                   font=dict(size=16)),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        scene=dict(
            xaxis=dict(title=_label("关键词", "Keywords"), tickfont=dict(size=8), gridcolor="rgba(255,255,255,0.1)"),
            yaxis=dict(title=_label("关键词", "Keywords"), tickfont=dict(size=8), gridcolor="rgba(255,255,255,0.1)"),
            zaxis=dict(title=_label("共现强度", "Co-occurrence Intensity"), gridcolor="rgba(255,255,255,0.1)"),
            bgcolor="rgba(10,10,46,0.8)",
        ),
        height=550, margin=dict(t=60, b=20, l=20, r=20),
    )
    return fig


# ═══════════════════════════════════════════════════════════════════
# 15. GAUGE / DASHBOARD (仪表盘)
# ═══════════════════════════════════════════════════════════════════
def gauge_dashboard(analysis_data: Dict[str, Any], atmosphere_data: Dict[str, Any] = None,
                    title: str = ""):
    """Dashboard with gauge meters for key metrics."""
    go, _, make_subplots = _get_plotly()
    if go is None:
        return None

    doc_count = analysis_data.get("doc_count", 0)
    kw_count = len(analysis_data.get("tfidf", {}).get("global_top", []))
    edge_count = len(analysis_data.get("cooccurrence", {}).get("edges", []))
    hp_count = len((atmosphere_data or {}).get("high_pressure", []))

    fig = make_subplots(
        rows=1, cols=4,
        specs=[[{"type": "indicator"}] * 4],
        subplot_titles=[
            _label("文献数", "Documents"),
            _label("关键词", "Keywords"),
            _label("共现边", "Co-occur Edges"),
            _label("高压区", "High Pressure"),
        ]
    )

    metrics = [
        (doc_count, 100, "#00ff88"),
        (kw_count, 40, "#ffaa00"),
        (edge_count, 500, "#cc44ff"),
        (hp_count, 20, "#ff4488"),
    ]

    for i, (val, ref, color) in enumerate(metrics):
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=val,
            gauge=dict(
                axis=dict(range=[0, max(val * 1.5, ref)], tickcolor="white"),
                bar=dict(color=color),
                bgcolor="rgba(10,10,46,0.8)",
                bordercolor="rgba(255,255,255,0.3)",
                steps=[
                    dict(range=[0, ref * 0.5], color="rgba(255,255,255,0.05)"),
                    dict(range=[ref * 0.5, ref], color="rgba(255,255,255,0.1)"),
                ],
            ),
        ), row=1, col=i + 1)

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white", size=12),
        height=250, margin=dict(t=40, b=20, l=30, r=30),
    )
    return fig


# ═══════════════════════════════════════════════════════════════════
# 16. PARALLEL COORDINATES (平行坐标图)
# ═══════════════════════════════════════════════════════════════════
def parallel_coordinates_chart(matched_kws: List[Dict], title: str = ""):
    """Parallel coordinates for multi-dimensional keyword comparison."""
    go, _, _ = _get_plotly()
    if go is None or not matched_kws:
        return None

    items = matched_kws[:15]
    tfidfs = [kw["tfidf"] for kw in items]
    scores = [kw["match_score"] for kw in items]
    conns = [float(kw.get("connections", 0)) for kw in items]

    fig = go.Figure(data=go.Parcoords(
        line=dict(
            color=scores,
            colorscale="Viridis",
            showscale=True,
            colorbar=dict(title=dict(text=_label("匹配分", "Score"), font=dict(color="white"))),
        ),
        dimensions=[
            dict(label="TF-IDF", values=tfidfs, range=[0, max(tfidfs) * 1.2] if tfidfs else [0, 1]),
            dict(label=_label("匹配分", "Match"), values=scores,
                 range=[0, max(scores) * 1.2] if scores else [0, 1]),
            dict(label=_label("连接", "Conns"), values=conns,
                 range=[0, max(conns) * 1.2] if conns else [0, 1]),
        ]
    ))

    fig.update_layout(
        title=dict(text=title or _label("📐 平行坐标图", "📐 Parallel Coordinates"),
                   font=dict(size=16)),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(10,10,46,0.8)",
        font=dict(color="white"),
        height=400, margin=dict(t=60, b=40, l=80, r=80),
    )
    return fig


# ═══════════════════════════════════════════════════════════════════
# 17. FUNNEL CHART (漏斗图)
# ═══════════════════════════════════════════════════════════════════
def funnel_chart(matched_kws: List[Dict], title: str = ""):
    """Funnel chart showing keyword ranking cascade."""
    go, _, _ = _get_plotly()
    if go is None or not matched_kws:
        return None

    items = matched_kws[:10]
    names = [kw["keyword"][:20] for kw in items]
    values = [kw["match_score"] for kw in items]
    colors = [AURORA_PALETTE[i % len(AURORA_PALETTE)] for i in range(len(items))]

    fig = go.Figure(go.Funnel(
        y=names, x=values,
        textinfo="value+percent initial",
        marker=dict(color=colors, line=dict(width=1, color="white")),
        connector=dict(line=dict(color="rgba(255,255,255,0.3)", width=1)),
        hovertemplate="%{y}<br>Score: %{x:.4f}<extra></extra>",
    ))

    fig.update_layout(
        title=dict(text=title or _label("🔻 学术漏斗图", "🔻 Academic Funnel Chart"),
                   font=dict(size=16)),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(10,10,46,0.8)",
        font=dict(color="white"),
        xaxis=dict(title=_label("匹配得分", "Match Score")),
        yaxis=dict(title=_label("关键词", "Keywords")),
        height=450, margin=dict(t=60, b=40),
    )
    return fig


# ═══════════════════════════════════════════════════════════════════
# 18. WATERFALL CHART (瀑布图)
# ═══════════════════════════════════════════════════════════════════
def waterfall_chart(matched_kws: List[Dict], title: str = ""):
    """Waterfall chart showing cumulative keyword contribution."""
    go, _, _ = _get_plotly()
    if go is None or not matched_kws:
        return None

    items = matched_kws[:12]
    names = [kw["keyword"][:15] for kw in items]
    values = [kw["match_score"] for kw in items]

    fig = go.Figure(go.Waterfall(
        x=names,
        y=values,
        measure=["relative"] * len(values),
        connector=dict(line=dict(color="rgba(255,255,255,0.3)")),
        increasing=dict(marker=dict(color="#00ff88")),
        decreasing=dict(marker=dict(color="#ff4444")),
        totals=dict(marker=dict(color="#ffaa00")),
        textposition="outside",
        text=[f"{v:.3f}" for v in values],
        textfont=dict(size=9, color="white"),
        hovertemplate="%{x}<br>Score: %{y:.4f}<extra></extra>",
    ))

    fig.update_layout(
        title=dict(text=title or _label("💧 贡献瀑布图", "💧 Contribution Waterfall"),
                   font=dict(size=16)),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(10,10,46,0.8)",
        font=dict(color="white"),
        xaxis=dict(tickangle=45, gridcolor="rgba(255,255,255,0.1)", title=_label("关键词", "Keywords")),
        yaxis=dict(gridcolor="rgba(255,255,255,0.1)", title=_label("匹配分", "Score")),
        height=450, margin=dict(t=60, b=100),
        showlegend=False,
    )
    return fig


# ═══════════════════════════════════════════════════════════════════
# HELPER: Render chart safely in Streamlit
# ═══════════════════════════════════════════════════════════════════
def render_plotly(fig, key: str = None):
    """Safely render a Plotly figure in Streamlit."""
    import streamlit as st
    if fig is None:
        st.caption(_label("⚠️ 数据不足，无法生成此图表", "⚠️ Insufficient data for this chart"))
        return
    try:
        st.plotly_chart(fig, use_container_width=True, key=key)
    except Exception as e:
        st.warning(f"Chart render error: {e}")


def render_matplotlib(fig, key: str = None):
    """Safely render a Matplotlib figure in Streamlit."""
    import streamlit as st
    if fig is None:
        st.caption(_label("⚠️ 数据不足，无法生成此图表", "⚠️ Insufficient data for this chart"))
        return
    try:
        st.pyplot(fig)
        import matplotlib.pyplot as plt
        plt.close(fig)
    except Exception as e:
        st.warning(f"Chart render error: {e}")
