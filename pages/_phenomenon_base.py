# -*- coding: utf-8 -*-
"""Shared renderer for all 9 atmospheric phenomenon analyzer pages.
Always shows content — static explanation + stats even without data/AI.
Now includes 10+ advanced visualizations per page.
"""

import streamlit as st
import numpy as np
from typing import Dict, Any, List
from utils.i18n import t, get_lang
from utils.logger import log_info


PHENOMENA = {
    "aurora": {"metric": "high_impact", "color": "#00ff88", "emoji": "🌌"},
    "noctilucent": {"metric": "frontier", "color": "#6699ff", "emoji": "☁️"},
    "nacreous": {"metric": "precision", "color": "#ff88cc", "emoji": "🌈"},
    "asperitas": {"metric": "controversy", "color": "#ff6644", "emoji": "🌊"},
    "lenticular": {"metric": "stability", "color": "#aabbcc", "emoji": "🏔️"},
    "circumhorizontal": {"metric": "purity", "color": "#ff4444", "emoji": "🔥"},
    "fallstreak": {"metric": "cascade", "color": "#88ccee", "emoji": "🕳️"},
    "brocken": {"metric": "observer_dependent", "color": "#dddd88", "emoji": "👻"},
    "moonbow": {"metric": "low_signal", "color": "#9988cc", "emoji": "🌙"},
}


def _select_matching_keywords(analysis_data: Dict[str, Any], phenom_key: str, top_n: int = 10) -> List[Dict[str, Any]]:
    """Select keywords matching this phenomenon's characteristics."""
    tfidf = analysis_data.get("tfidf", {})
    global_top = tfidf.get("global_top", [])
    cooc = analysis_data.get("cooccurrence", {})
    edges = cooc.get("edges", [])
    cfg = PHENOMENA.get(phenom_key, {})
    metric = cfg.get("metric", "high_impact")

    if not global_top:
        return []

    scored = []
    for kw, score in global_top:
        edge_w = sum(e["weight"] for e in edges if e["source"] == kw or e["target"] == kw)
        if metric == "high_impact":
            final = score * 2 + edge_w * 0.1
        elif metric == "frontier":
            final = score * 0.5 + edge_w * 0.05
        elif metric == "precision":
            final = score * 3 if edge_w < 5 else score * 0.5
        elif metric == "controversy":
            final = edge_w * 0.3 + score * 0.5
        elif metric == "stability":
            final = score * 1.5 + edge_w * 0.2
        elif metric == "purity":
            final = score * 3 if edge_w < 3 else score * 0.3
        elif metric == "cascade":
            final = edge_w * 0.5 + score
        elif metric == "observer_dependent":
            # Use stable hash (hashlib) instead of Python hash() which varies per process
            import hashlib
            hash_val = int(hashlib.md5(kw.encode("utf-8")).hexdigest(), 16) % 1000 / 1000.0
            final = score * 1.0 + hash_val * 0.3
        elif metric == "low_signal":
            final = (1.0 / max(score, 0.001)) * 0.01
        else:
            final = score
        scored.append({"keyword": kw, "tfidf": round(score, 4),
                        "match_score": round(final, 4), "connections": edge_w})

    scored.sort(key=lambda x: x["match_score"], reverse=True)
    return scored[:top_n]


def _generate_stat_metaphor(phenom_key: str, matched_kws: List[Dict], lang: str) -> str:
    """Generate statistical (non-AI) metaphor explanation — always available."""
    desc = t(f"{phenom_key}_desc")
    if not matched_kws:
        return f"📖 {desc}\n\n⚠️ {t('phenom_stat_fallback')}"

    top3 = [kw["keyword"] for kw in matched_kws[:3]]
    top3_str = ", ".join(top3)
    if lang == "zh":
        return (
            f"📖 {desc}\n\n"
            f"📊 基于统计分析，与此现象最匹配的方法/关键词群：**{top3_str}**\n\n"
            f"- '{top3[0]}' TF-IDF = {matched_kws[0]['tfidf']:.4f}，共现连接 = {matched_kws[0]['connections']}\n"
            f"- 匹配得分 = {matched_kws[0]['match_score']:.4f}\n"
            f"- 共分析 {len(matched_kws)} 个候选关键词"
        )
    return (
        f"📖 {desc}\n\n"
        f"📊 Best-matching methods/keywords: **{top3_str}**\n\n"
        f"- '{top3[0]}' TF-IDF = {matched_kws[0]['tfidf']:.4f}, connections = {matched_kws[0]['connections']}\n"
        f"- Match score = {matched_kws[0]['match_score']:.4f}\n"
        f"- Analyzed {len(matched_kws)} candidate keywords"
    )


def _render_advanced_charts(phenom_key: str, matched: List[Dict], analysis: Dict[str, Any],
                            cfg: Dict[str, Any], lang: str):
    """Render the full suite of advanced visualizations."""
    from utils.charts import (
        rose_chart, scatter_rose_chart, candlestick_chart, radar_chart,
        bubble_chart, heatmap_chart, sunburst_chart, sankey_chart,
        line_statistics_chart, stacked_area_chart, treemap_chart,
        violin_chart, surface_3d_chart, parallel_coordinates_chart,
        funnel_chart, waterfall_chart, word_cloud_figure,
        render_plotly, render_matplotlib,
    )

    color = cfg.get("color", "#00ff88")
    phenom_name = t(phenom_key)
    atmo = st.session_state.get("atmosphere_data", {})

    # ─── Section: Key Visualizations ───
    st.divider()
    viz_title = "📊 " + t("phenom_advanced_viz")
    st.subheader(viz_title)

    tab_labels = [
        "🌹 " + ("玫瑰图" if lang == "zh" else "Rose"),
        "🌸 " + ("散点玫瑰" if lang == "zh" else "Scatter Rose"),
        "🕯️ " + ("蜡烛图" if lang == "zh" else "Candlestick"),
        "🕸️ " + ("雷达图" if lang == "zh" else "Radar"),
        "🫧 " + ("气泡图" if lang == "zh" else "Bubble"),
        "☁️ " + ("词云" if lang == "zh" else "Word Cloud"),
    ]
    tabs = st.tabs(tab_labels)

    with tabs[0]:
        kw_pairs = [(kw["keyword"], kw["match_score"]) for kw in matched]
        fig = rose_chart(kw_pairs, title=f"{phenom_name} - " +
                         ("南丁格尔玫瑰图" if lang == "zh" else "Nightingale Rose"), color=color)
        render_plotly(fig, key=f"rose_{phenom_key}")

    with tabs[1]:
        fig = scatter_rose_chart(matched, title=f"{phenom_name} - " +
                                 ("散点玫瑰图" if lang == "zh" else "Scatter Rose"))
        render_plotly(fig, key=f"srose_{phenom_key}")

    with tabs[2]:
        fig = candlestick_chart(matched, title=f"{phenom_name} - " +
                                ("学术K线图" if lang == "zh" else "Academic K-Chart"))
        render_plotly(fig, key=f"candle_{phenom_key}")

    with tabs[3]:
        fig = radar_chart(matched, title=f"{phenom_name} - " +
                          ("多维雷达" if lang == "zh" else "Multi-Dim Radar"), color=color)
        render_plotly(fig, key=f"radar_{phenom_key}")

    with tabs[4]:
        fig = bubble_chart(matched, title=f"{phenom_name} - " +
                           ("气泡分析" if lang == "zh" else "Bubble Analysis"))
        render_plotly(fig, key=f"bubble_{phenom_key}")

    with tabs[5]:
        global_top = analysis.get("tfidf", {}).get("global_top", [])
        fig = word_cloud_figure(global_top, title=f"{phenom_name} - " +
                                ("学术词云" if lang == "zh" else "Word Cloud"), color=color)
        render_matplotlib(fig, key=f"wc_{phenom_key}")

    # ─── Second row of charts ───
    st.divider()
    viz_title2 = "🔬 " + t("phenom_deep_charts")
    st.subheader(viz_title2)

    tab_labels2 = [
        "🔥 " + ("热力图" if lang == "zh" else "Heatmap"),
        "🌊 " + ("桑基图" if lang == "zh" else "Sankey"),
        "📈 " + ("折线统计" if lang == "zh" else "Line Stats"),
        "📊 " + ("堆积图" if lang == "zh" else "Stacked"),
        "🌍 " + ("地壳图" if lang == "zh" else "Treemap"),
        "📐 " + ("平行坐标" if lang == "zh" else "Parallel"),
        "🔻 " + ("漏斗图" if lang == "zh" else "Funnel"),
        "💧 " + ("瀑布图" if lang == "zh" else "Waterfall"),
    ]
    tabs2 = st.tabs(tab_labels2)

    with tabs2[0]:
        fig = heatmap_chart(analysis)
        render_plotly(fig, key=f"heat_{phenom_key}")

    with tabs2[1]:
        fig = sankey_chart(analysis)
        render_plotly(fig, key=f"sankey_{phenom_key}")

    with tabs2[2]:
        year_trend = analysis.get("year_trend", {})
        fig = line_statistics_chart(year_trend)
        render_plotly(fig, key=f"line_{phenom_key}")

    with tabs2[3]:
        fig = stacked_area_chart(analysis)
        render_plotly(fig, key=f"stacked_{phenom_key}")

    with tabs2[4]:
        fig = treemap_chart(analysis, atmosphere_data=atmo)
        render_plotly(fig, key=f"tree_{phenom_key}")

    with tabs2[5]:
        fig = parallel_coordinates_chart(matched)
        render_plotly(fig, key=f"para_{phenom_key}")

    with tabs2[6]:
        fig = funnel_chart(matched)
        render_plotly(fig, key=f"funnel_{phenom_key}")

    with tabs2[7]:
        fig = waterfall_chart(matched)
        render_plotly(fig, key=f"wf_{phenom_key}")

    # ─── 3D Charts (full width) ───
    st.divider()
    viz_title3 = "🏔️ " + t("phenom_3d_viz")
    st.subheader(viz_title3)

    col3d_1, col3d_2 = st.columns(2)
    with col3d_1:
        fig = surface_3d_chart(analysis)
        render_plotly(fig, key=f"surf3d_{phenom_key}")

    with col3d_2:
        fig = sunburst_chart(analysis, atmosphere_data=atmo)
        render_plotly(fig, key=f"sun_{phenom_key}")


def render_phenomenon_page(phenom_key: str):
    """Render a complete phenomenon analyzer page. Always shows content."""
    lang = get_lang()
    cfg = PHENOMENA.get(phenom_key, {})
    emoji = cfg.get("emoji", "🌐")

    st.header(f"{emoji} {t(phenom_key)}")

    # ─── ALWAYS show description ───
    st.markdown(f"### {t(phenom_key + '_desc')}")
    st.divider()

    # ─── Check if data is loaded ───
    analysis = st.session_state.get("analysis_data", {})
    has_data = bool(analysis and analysis.get("tfidf", {}).get("global_top"))

    if not has_data:
        st.warning(t("no_data"))
        st.info(t(f"{phenom_key}_desc"))
        return

    # ─── Match keywords ───
    matched = _select_matching_keywords(analysis, phenom_key, top_n=15)

    # ─── Gauge Dashboard (top of page) ───
    try:
        from utils.charts import gauge_dashboard, render_plotly
        atmo = st.session_state.get("atmosphere_data", {})
        fig = gauge_dashboard(analysis, atmosphere_data=atmo)
        render_plotly(fig, key=f"gauge_{phenom_key}")
    except Exception:
        pass

    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("🎯 " + t("phenom_matched_keywords"))
        if matched:
            import pandas as pd
            df = pd.DataFrame(matched)
            df.columns = [
                t("search") if "Keyword" in t("search") else ("关键词" if lang == "zh" else "Keyword"),
                "TF-IDF",
                ("匹配得分" if lang == "zh" else "Match Score"),
                ("共现连接" if lang == "zh" else "Connections")
            ]
            st.dataframe(df, use_container_width=True, height=400)
        else:
            st.info(t("phenom_no_match"))

    with col2:
        st.subheader("📊 " + t("phenom_match_dist"))
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial']
            matplotlib.rcParams['axes.unicode_minus'] = False

            if matched:
                fig, ax = plt.subplots(figsize=(5, 5))
                top5 = matched[:7]
                names = [m["keyword"][:15] for m in top5]
                scores = [m["match_score"] for m in top5]
                colors = [cfg.get("color", "#4488ff")] * len(top5)
                ax.barh(names[::-1], scores[::-1], color=colors[::-1], alpha=0.85, edgecolor="white")
                ax.set_xlabel("Match Score")
                ax.set_title(t(phenom_key)[:30])
                for spine in ax.spines.values():
                    spine.set_visible(False)
                ax.tick_params(left=False)
                plt.tight_layout()
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.info("N/A")
        except Exception as e:
            st.warning(f"Chart error: {e}")

    # ─── Advanced Visualizations ───
    if matched:
        try:
            _render_advanced_charts(phenom_key, matched, analysis, cfg, lang)
        except Exception as e:
            st.warning(f"Advanced chart error: {e}")
            log_info(f"Chart error on {phenom_key}: {e}")

    # ─── AI / Statistical Analysis ───
    st.divider()
    ai_title = f"🤖 {t('ai_analysis')}"
    st.subheader(ai_title)

    stat_text = _generate_stat_metaphor(phenom_key, matched, lang)

    active = st.session_state.get("active_backend")
    ai_ok = active is not None and getattr(active, "is_loaded", False)

    if ai_ok:
        gen_label = "⚡ " + t("phenom_generate_btn")
        if st.button(gen_label, key=f"ai_gen_{phenom_key}", type="primary"):
            with st.spinner(t("ai_generating")):
                from utils.shared_ui import get_ai_prompt
                prompt = get_ai_prompt(phenom_key, matched, lang)
                try:
                    ai_text = active.timed_generate(prompt, max_tokens=800)
                    st.session_state[f"ai_result_{phenom_key}"] = ai_text
                    log_info(f"AI analysis generated for {phenom_key}")
                except Exception as e:
                    st.error(f"AI error: {e}")
                    log_info(f"AI failed for {phenom_key}: {e}")

        ai_cached = st.session_state.get(f"ai_result_{phenom_key}", "")
        if ai_cached:
            st.text_area(ai_title, value=ai_cached, height=350,
                          key=f"ai_disp_{phenom_key}")
        else:
            st.text_area(ai_title, value=stat_text, height=300,
                          key=f"stat_disp_{phenom_key}")

        strength = st.session_state.get("prompt_strength", "strong")
        strength_map = {"light": "🟢", "standard": "🟡", "strong": "🟠", "maximum": "🔴"}
        st.caption(f"Prompt: {strength_map.get(strength, '?')} {strength} | "
                   f"{t('phenom_custom_template') if st.session_state.get('custom_prompt_template') else t('phenom_default_template')}")
    else:
        st.info(t("ai_not_enabled"))
        st.text_area(ai_title, value=stat_text, height=300,
                      key=f"stat_disp_only_{phenom_key}")

    # ─── Export ───
    st.divider()
    from utils.exports import export_json
    export_data = {
        "phenomenon": phenom_key,
        "description": t(f"{phenom_key}_desc"),
        "matched_keywords": matched,
        "statistical_analysis": stat_text,
    }
    ec1, ec2 = st.columns(2)
    with ec1:
        st.download_button(
            t("export_json"), data=export_json(export_data),
            file_name=f"{phenom_key}_analysis.json", mime="application/json",
            key=f"ej_{phenom_key}"
        )
    with ec2:
        st.download_button(
            t("export_txt"), data=stat_text,
            file_name=f"{phenom_key}_report.txt", mime="text/plain",
            key=f"et_{phenom_key}"
        )
