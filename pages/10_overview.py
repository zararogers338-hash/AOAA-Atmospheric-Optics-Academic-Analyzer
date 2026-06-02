# -*- coding: utf-8 -*-
"""Academic Atmosphere Overview Dashboard - Self-contained Streamlit page.
Now with 18+ advanced chart types for comprehensive data visualization.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import numpy as np
import json
from typing import Dict, Any

from utils.shared_ui import init_page, render_shared_sidebar, get_ai_prompt
from utils.i18n import t, get_lang
from utils.logger import log_info, get_logs
from utils.exports import export_json, export_txt, export_svg_chart, export_results_zip

# ── Initialize ──
init_page(title="Overview Dashboard")
render_shared_sidebar()

# ── Content ──
lang = get_lang()
st.header(f"🌍 {t('overview')}")

analysis = st.session_state.get("analysis_data", {})
atmo = st.session_state.get("atmosphere_data", {})
has_data = bool(analysis and analysis.get("tfidf", {}).get("global_top"))

if not has_data:
    st.warning(t("no_data"))
    st.info("👈 " + t("overview_upload_hint"))
    st.stop()

# ═══ Gauge Dashboard (top) ═══
try:
    from utils.charts import gauge_dashboard, render_plotly
    fig_gauge = gauge_dashboard(analysis, atmosphere_data=atmo)
    render_plotly(fig_gauge, key="overview_gauge")
except Exception as e:
    st.caption(f"Gauge: {e}")

# ═══ Atmosphere Dashboard ═══
st.subheader("🌡️ " + t("overview"))

c1, c2 = st.columns(2)
with c1:
    st.markdown(f"### 🔵 {t('high_pressure')}")
    hp = atmo.get("high_pressure", [])
    if hp:
        for item in hp[:5]:
            st.markdown(f"- **{item['keyword']}** (TF-IDF: {item['tfidf']:.4f}, BC: {item['betweenness']:.3f})")
    else:
        st.caption("N/A" if lang == "en" else "暂无数据")

    st.markdown(f"### ⚔️ {t('front')}")
    fronts = atmo.get("fronts", [])
    if fronts:
        for item in fronts[:5]:
            st.markdown(f"- **{item['keyword']}** (BC: {item['betweenness']:.3f})")
    else:
        st.caption("N/A")

with c2:
    st.markdown(f"### 🔴 {t('low_pressure')}")
    lp = atmo.get("low_pressure", [])
    if lp:
        for item in lp[:5]:
            st.markdown(f"- **{item['keyword']}** (TF-IDF: {item['tfidf']:.4f})")
    else:
        st.caption("N/A")

    st.markdown(f"### 💨 {t('jet_stream')}")
    jets = atmo.get("jet_streams", [])
    if jets:
        for item in jets[:5]:
            st.markdown(f"- **{item['source']}** ↔ **{item['target']}** (w: {item['weight']})")
    else:
        st.caption("N/A")

# ═══ Original Charts (Matplotlib) ═══
st.divider()
st.subheader("📊 " + t("overview_basic_charts"))

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial']
    matplotlib.rcParams['axes.unicode_minus'] = False

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Academic Atmospheric Pressure Map", fontsize=14, fontweight="bold")

    # 1. TF-IDF bar chart
    ax = axes[0][0]
    tfidf = analysis.get("tfidf", {})
    global_top = tfidf.get("global_top", [])[:15]
    if global_top:
        names = [kw for kw, _ in global_top]
        scores = [s for _, s in global_top]
        colors = ["#2196F3" if s > np.mean(scores) else "#FF9800" for s in scores]
        ax.barh(names[::-1], scores[::-1], color=colors[::-1], alpha=0.8)
        ax.set_title(t("keywords_chart"))
        ax.set_xlabel("TF-IDF Score")
    else:
        ax.text(0.5, 0.5, "No data", ha="center", va="center")

    # 2. Year trend
    ax = axes[0][1]
    trend = analysis.get("year_trend", {})
    years = trend.get("years", [])
    counts = trend.get("counts", [])
    if years:
        ax.fill_between(years, counts, alpha=0.3, color="#4CAF50")
        ax.plot(years, counts, "o-", color="#4CAF50", markersize=4)
        ax.set_title(t("trend_chart"))
        ax.set_xlabel("Year")
        ax.set_ylabel("Count")
    else:
        ax.text(0.5, 0.5, "No year data", ha="center", va="center")

    # 3. Co-occurrence network
    ax = axes[1][0]
    cooc = analysis.get("cooccurrence", {})
    edges = cooc.get("edges", [])[:30]
    keywords = cooc.get("keywords", [])[:20]
    if keywords:
        np.random.seed(42)
        pos = {kw: (np.random.uniform(-1, 1), np.random.uniform(-1, 1)) for kw in keywords}
        # Node label toggle
        show_labels_mpl = st.session_state.get("show_node_labels", True)
        # Compute importance for label priority
        kw_importance = {}
        for kw in keywords:
            kw_importance[kw] = sum(1 for e in edges if e["source"] == kw or e["target"] == kw)
        sorted_kws = sorted(kw_importance.items(), key=lambda x: x[1], reverse=True)
        top_label_set = set(kw for kw, _ in sorted_kws[:max(1, len(sorted_kws) // 2)])

        for kw, (x, y) in pos.items():
            ms = 6 + kw_importance.get(kw, 0) * 0.5
            ax.plot(x, y, "o", color="#E91E63", markersize=min(ms, 14), alpha=0.7)
            if show_labels_mpl and kw in top_label_set:
                ax.annotate(kw[:12], (x, y), fontsize=6, ha="center", va="bottom")
        for e in edges[:20]:
            if e["source"] in pos and e["target"] in pos:
                x1, y1 = pos[e["source"]]
                x2, y2 = pos[e["target"]]
                al = min(e["weight"] / 10.0, 0.8)
                ax.plot([x1, x2], [y1, y2], "-", color="#9E9E9E", alpha=al, linewidth=0.5)
        ax.set_title(t("cooccurrence"))
    else:
        ax.text(0.5, 0.5, "No data", ha="center", va="center")

    # 4. Citation distribution
    ax = axes[1][1]
    cit = analysis.get("citation_stats", {})
    if cit.get("available"):
        values = cit.get("values", [])
        if values:
            ax.hist(values, bins=min(30, len(set(values))), color="#FF5722", alpha=0.7, edgecolor="white")
            ax.set_title(t("citation_dist"))
    else:
        meta_kws = analysis.get("meta_keywords", {})
        if meta_kws:
            top_m = list(meta_kws.items())[:10]
            ax.barh([k for k, _ in top_m][::-1], [v for _, v in top_m][::-1], color="#FF5722", alpha=0.7)
            ax.set_title("Metadata Keywords")
        else:
            ax.text(0.5, 0.5, "No citation data", ha="center", va="center")

    plt.tight_layout()
    st.pyplot(fig)
    st.session_state["overview_fig"] = fig

except Exception as e:
    st.error(f"Chart rendering error: {e}")
    fig = None

# ═══════════════════════════════════════════════════════════════════
# ADVANCED VISUALIZATION SUITE
# ═══════════════════════════════════════════════════════════════════
st.divider()
st.subheader("🚀 " + t("overview_advanced_center"))

try:
    from utils.charts import (
        rose_chart, scatter_rose_chart, candlestick_chart, radar_chart,
        bubble_chart, heatmap_chart, sunburst_chart, sankey_chart,
        line_statistics_chart, stacked_area_chart, treemap_chart,
        violin_chart, surface_3d_chart, parallel_coordinates_chart,
        funnel_chart, waterfall_chart, word_cloud_figure,
        render_plotly, render_matplotlib,
    )

    # Build a "fake" matched list from global top for overview charts
    global_top_data = analysis.get("tfidf", {}).get("global_top", [])
    cooc_data = analysis.get("cooccurrence", {})
    edges_data = cooc_data.get("edges", [])

    overview_matched = []
    for kw, score in global_top_data[:15]:
        edge_w = sum(e["weight"] for e in edges_data if e["source"] == kw or e["target"] == kw)
        overview_matched.append({
            "keyword": kw,
            "tfidf": round(score, 4),
            "match_score": round(score * 2 + edge_w * 0.1, 4),
            "connections": edge_w,
        })

    # ─── Row 1: Polar & Rose Charts ───
    st.markdown("#### " + ("🌹 " + t("overview_polar_series")))
    r1c1, r1c2 = st.columns(2)

    with r1c1:
        kw_pairs = [(kw, s) for kw, s in global_top_data[:12]]
        fig = rose_chart(kw_pairs, title=("全局关键词玫瑰图" if lang == "zh" else "Global Keyword Rose"))
        render_plotly(fig, key="ov_rose")

    with r1c2:
        fig = scatter_rose_chart(overview_matched, title=("全局散点玫瑰" if lang == "zh" else "Global Scatter Rose"))
        render_plotly(fig, key="ov_srose")

    # ─── Row 2: Statistical Analysis ───
    st.markdown("#### 📈 " + t("overview_stat_series"))
    r2c1, r2c2 = st.columns(2)

    with r2c1:
        year_trend = analysis.get("year_trend", {})
        fig = line_statistics_chart(year_trend, title=("年度趋势折线图" if lang == "zh" else "Year Trend Line Stats"))
        render_plotly(fig, key="ov_line")

    with r2c2:
        fig = candlestick_chart(overview_matched, title=("学术K线图" if lang == "zh" else "Academic K-Chart"))
        render_plotly(fig, key="ov_candle")

    # ─── Row 3: Network & Flow ───
    st.markdown("#### 🌊 " + t("overview_network_series"))
    r3c1, r3c2 = st.columns(2)

    with r3c1:
        fig = heatmap_chart(analysis, title=("共现热力图" if lang == "zh" else "Co-occurrence Heatmap"))
        render_plotly(fig, key="ov_heat")

    with r3c2:
        fig = sankey_chart(analysis, title=("知识流向桑基图" if lang == "zh" else "Knowledge Flow Sankey"))
        render_plotly(fig, key="ov_sankey")

    # ─── Row 4: Multi-Dimensional ───
    st.markdown("#### 🕸️ " + t("overview_multidim_series"))
    r4c1, r4c2 = st.columns(2)

    with r4c1:
        fig = radar_chart(overview_matched, title=("全局多维雷达" if lang == "zh" else "Global Multi-Dim Radar"))
        render_plotly(fig, key="ov_radar")

    with r4c2:
        fig = bubble_chart(overview_matched, title=("全局气泡分析" if lang == "zh" else "Global Bubble Analysis"))
        render_plotly(fig, key="ov_bubble")

    # ─── Row 5: Hierarchy & Territory ───
    st.markdown("#### 🌍 " + t("overview_hierarchy_series"))
    r5c1, r5c2 = st.columns(2)

    with r5c1:
        fig = treemap_chart(analysis, atmosphere_data=atmo,
                           title=("学术地壳图" if lang == "zh" else "Academic Treemap"))
        render_plotly(fig, key="ov_tree")

    with r5c2:
        fig = sunburst_chart(analysis, atmosphere_data=atmo,
                            title=("旭日层级图" if lang == "zh" else "Sunburst Hierarchy"))
        render_plotly(fig, key="ov_sun")

    # ─── Row 6: Distribution Analysis ───
    st.markdown("#### 🎻 " + t("overview_dist_series"))
    r6c1, r6c2 = st.columns(2)

    with r6c1:
        fig = violin_chart(analysis, title=("TF-IDF小提琴图" if lang == "zh" else "TF-IDF Violin"))
        render_plotly(fig, key="ov_violin")

    with r6c2:
        fig = stacked_area_chart(analysis, title=("层状堆积图" if lang == "zh" else "Stacked Area"))
        render_plotly(fig, key="ov_stacked")

    # ─── Row 7: Advanced Comparison ───
    st.markdown("#### 📐 " + t("overview_compare_series"))
    r7c1, r7c2, r7c3 = st.columns(3)

    with r7c1:
        fig = parallel_coordinates_chart(overview_matched, title=("平行坐标图" if lang == "zh" else "Parallel Coords"))
        render_plotly(fig, key="ov_para")

    with r7c2:
        fig = funnel_chart(overview_matched, title=("学术漏斗图" if lang == "zh" else "Academic Funnel"))
        render_plotly(fig, key="ov_funnel")

    with r7c3:
        fig = waterfall_chart(overview_matched, title=("贡献瀑布图" if lang == "zh" else "Waterfall"))
        render_plotly(fig, key="ov_wf")

    # ─── Row 8: 3D + Word Cloud ───
    st.markdown("#### 🏔️ " + t("overview_3d_series"))
    r8c1, r8c2 = st.columns(2)

    with r8c1:
        fig = surface_3d_chart(analysis, title=("3D共现曲面" if lang == "zh" else "3D Co-occurrence Surface"))
        render_plotly(fig, key="ov_surf3d")

    with r8c2:
        fig = word_cloud_figure(global_top_data, title=("全局学术词云" if lang == "zh" else "Global Word Cloud"))
        render_matplotlib(fig, key="ov_wc")

except Exception as e:
    st.error(f"Advanced charts error: {e}")
    import traceback
    st.code(traceback.format_exc())

# ═══ 3D Visualization (Three.js) ═══
st.divider()
st.subheader(f"🌐 {t('threejs_title')}")

cooc = analysis.get("cooccurrence", {})
kws_3d = cooc.get("keywords", [])[:20]
edges_3d = cooc.get("edges", [])[:40]

if kws_3d:
    show_labels_3d = st.session_state.get("show_node_labels", True)
    # Compute node importance for label priority (based on co-occurrence connections)
    node_importance = {}
    for kw in kws_3d:
        conn = sum(1 for e in edges_3d if e["source"] == kw or e["target"] == kw)
        node_importance[kw] = conn
    max_imp = max(node_importance.values()) if node_importance else 1
    # Label priority: top 50% of nodes by importance get labels when toggle is ON
    sorted_by_imp = sorted(node_importance.items(), key=lambda x: x[1], reverse=True)
    top_n = max(1, len(sorted_by_imp) // 2)
    priority_set = {kw for kw, _ in sorted_by_imp[:top_n]}

    nodes_json = json.dumps([{
        "id": kw, "label": kw[:15],
        "importance": node_importance.get(kw, 0) / max(max_imp, 1),
        "showLabel": show_labels_3d and (kw in priority_set)
    } for kw in kws_3d])
    edges_json = json.dumps([{"source": e["source"], "target": e["target"], "weight": e["weight"]}
                              for e in edges_3d if e["source"] in kws_3d and e["target"] in kws_3d])

    threejs_html = f"""
    <div id="aoaa3d" style="width:100%;height:500px;background:#0a0a2e;border-radius:8px;position:relative;overflow:hidden;">
    <canvas id="c3d" style="width:100%;height:100%;"></canvas>
    <div id="tt3d" style="position:absolute;display:none;background:rgba(0,0,0,0.85);color:#0f0;padding:6px 12px;border-radius:6px;font-size:13px;pointer-events:none;border:1px solid #0f0;z-index:10;"></div>
    <div id="labels3d" style="position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;overflow:hidden;"></div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
    (function(){{
        const N={nodes_json}, E={edges_json};
        const showLabels={'true' if show_labels_3d else 'false'};
        const box=document.getElementById('aoaa3d'), cv=document.getElementById('c3d'), tt=document.getElementById('tt3d');
        const labelsDiv=document.getElementById('labels3d');
        const sc=new THREE.Scene(); sc.background=new THREE.Color(0x0a0a2e);
        const cam=new THREE.PerspectiveCamera(60,box.clientWidth/box.clientHeight,0.1,1000);
        cam.position.z=50;
        const ren=new THREE.WebGLRenderer({{canvas:cv,antialias:true}});
        ren.setSize(box.clientWidth,box.clientHeight);
        const bg=new THREE.BufferGeometry(), bn=600, bp=new Float32Array(bn*3);
        for(let i=0;i<bn*3;i++) bp[i]=(Math.random()-0.5)*100;
        bg.setAttribute('position',new THREE.BufferAttribute(bp,3));
        sc.add(new THREE.Points(bg,new THREE.PointsMaterial({{color:0x00ff88,size:0.3,transparent:true,opacity:0.4}})));
        const nm={{}}, meshes=[];
        // Create label elements for each node
        const labelEls=[];
        N.forEach((n,i)=>{{
            const phi=(i/N.length)*Math.PI*2, r=15+Math.random()*10;
            const nodeSize=0.5+n.importance*1.0;
            const geo=new THREE.SphereGeometry(nodeSize,16,16);
            const mat=new THREE.MeshBasicMaterial({{color:new THREE.Color().setHSL(i/N.length,0.8,0.6)}});
            const m=new THREE.Mesh(geo,mat);
            m.position.set(Math.cos(phi)*r,(Math.random()-0.5)*20,Math.sin(phi)*r);
            m.userData={{label:n.label,id:n.id,importance:n.importance}};
            sc.add(m); nm[n.id]=m.position; meshes.push(m);
            // Create HTML label for priority nodes
            if(showLabels && n.showLabel){{
                const el=document.createElement('div');
                el.style.cssText='position:absolute;color:rgba(255,255,255,0.85);font-size:'+(9+n.importance*4)+'px;white-space:nowrap;text-shadow:0 0 4px #000,0 0 8px #000;pointer-events:none;';
                el.textContent=n.label;
                labelsDiv.appendChild(el);
                labelEls.push({{el:el,mesh:m}});
            }}
        }});
        E.forEach(e=>{{
            if(nm[e.source]&&nm[e.target]){{
                const g=new THREE.BufferGeometry().setFromPoints([nm[e.source].clone(),nm[e.target].clone()]);
                sc.add(new THREE.Line(g,new THREE.LineBasicMaterial({{color:0x4488ff,transparent:true,opacity:Math.min(e.weight/10,0.6)}})));
            }}
        }});
        let mx=0,my=0,drag=false,rX=0,rY=0;
        box.onmousedown=()=>drag=true; box.onmouseup=()=>drag=false;
        box.onmousemove=(ev)=>{{if(drag){{rY+=ev.movementX*0.005;rX+=ev.movementY*0.005;}}mx=ev.offsetX;my=ev.offsetY;}};
        const rc=new THREE.Raycaster(), ms=new THREE.Vector2();
        function projectToScreen(pos){{
            const v=pos.clone().project(cam);
            return{{x:(v.x*0.5+0.5)*box.clientWidth, y:(-v.y*0.5+0.5)*box.clientHeight}};
        }}
        function anim(){{
            requestAnimationFrame(anim);
            sc.rotation.y=rY+performance.now()*0.0001; sc.rotation.x=rX;
            const t=performance.now()*0.001;
            for(let i=0;i<bn;i++) bp[i*3+1]+=Math.sin(t+i*0.1)*0.02;
            bg.attributes.position.needsUpdate=true;
            // Update label positions
            labelEls.forEach(item=>{{
                const sp=projectToScreen(item.mesh.position);
                item.el.style.left=(sp.x-20)+'px';
                item.el.style.top=(sp.y-18)+'px';
            }});
            // Hover tooltip (always works regardless of toggle)
            ms.x=(mx/box.clientWidth)*2-1; ms.y=-(my/box.clientHeight)*2+1;
            rc.setFromCamera(ms,cam);
            const h=rc.intersectObjects(meshes);
            if(h.length>0){{tt.style.display='block';tt.style.left=mx+'px';tt.style.top=(my-30)+'px';tt.textContent=h[0].object.userData.label;}}
            else{{tt.style.display='none';}}
            ren.render(sc,cam);
        }}
        anim();
        window.addEventListener('resize',()=>{{cam.aspect=box.clientWidth/box.clientHeight;cam.updateProjectionMatrix();ren.setSize(box.clientWidth,box.clientHeight);}});
    }})();
    </script>
    """
    try:
        import streamlit.components.v1 as components
        components.html(threejs_html, height=550, scrolling=False)
    except Exception as e:
        st.warning(f"3D fallback: {e}")
else:
    st.info(t("threejs_fallback"))

# ═══ Global AI Analysis ═══
st.divider()
st.subheader(f"🤖 {t('ai_analysis')}")

active = st.session_state.get("active_backend")
ai_ok = active is not None and getattr(active, "is_loaded", False)

if ai_ok:
    gen_label = "⚡ " + t("overview_generate_btn")
    if st.button(gen_label, key="global_ai_btn", type="primary"):
        top_kws = [kw for kw, _ in analysis.get("tfidf", {}).get("global_top", [])[:10]]
        kw_str = ", ".join(top_kws)
        strength = st.session_state.get("prompt_strength", "strong")
        custom_sys = st.session_state.get("custom_system_prompt", "").strip()

        if lang == "zh":
            prompt = (
                f"{'[System: ' + custom_sys + ']' if custom_sys else ''}\n"
                f"你是大气光学学术隐喻专家。严禁使用生物/生态隐喻。\n"
                f"当前学术文献核心关键词：{kw_str}\n"
                f"共 {analysis.get('doc_count', 0)} 篇文献。\n\n"
                f"请用大气光学现象的物理过程来隐喻描述这个学术领域的整体'大气层状态'：\n"
                f"1. 气压分布（哪些方法是高压区/稳定主流，哪些是低压槽/新兴扰动）\n"
                f"2. 锋面位置（哪些方法之间存在冲突/对立）\n"
                f"3. 急流方向（跨领域传播的主要通道）\n"
                f"4. 云层状态（各层大气的方法密度和活跃度）\n"
                f"{'400字以内，每段至少2个专业术语。' if strength in ['strong','maximum'] else '200字以内。'}"
            )
        else:
            prompt = (
                f"{'[System: ' + custom_sys + ']' if custom_sys else ''}\n"
                f"You are an atmospheric optics metaphor expert. NO biology/ecology.\n"
                f"Core keywords: {kw_str}\nDocuments: {analysis.get('doc_count', 0)}\n\n"
                f"Describe this field's 'atmospheric state' using optical/meteorological metaphors:\n"
                f"1. Pressure distribution (high/low pressure zones)\n"
                f"2. Front positions (method conflicts)\n"
                f"3. Jet stream directions (cross-field propagation)\n"
                f"4. Cloud layer status (method density per atmospheric layer)\n"
                f"{'Under 400 words, 2+ technical terms per paragraph.' if strength in ['strong','maximum'] else 'Under 200 words.'}"
            )

        with st.spinner(t("ai_generating")):
            try:
                result = active.timed_generate(prompt, max_tokens=1000)
                st.session_state["global_ai_result"] = result
            except Exception as e:
                st.error(f"AI error: {e}")

    if "global_ai_result" in st.session_state:
        st.text_area(t("ai_analysis"), value=st.session_state["global_ai_result"],
                      height=400, key="gai_area")
    else:
        st.info(t("ai_not_enabled") if not ai_ok else t("overview_click_to_gen"))
else:
    st.info(t("ai_not_enabled"))

# ═══ Exports ═══
st.divider()
st.subheader(f"📥 {t('export')}")
ec1, ec2, ec3, ec4 = st.columns(4)
with ec1:
    st.download_button(t("export_json"), data=export_json(analysis),
                        file_name="aoaa_analysis.json", mime="application/json")
with ec2:
    st.download_button(t("export_txt"), data=export_txt(analysis),
                        file_name="aoaa_report.txt", mime="text/plain")
with ec3:
    if fig is not None:
        svg = export_svg_chart(fig)
        if svg:
            st.download_button(t("export_svg"), data=svg,
                                file_name="aoaa_chart.svg", mime="image/svg+xml")
with ec4:
    zip_data = export_results_zip(analysis)
    st.download_button(t("export_zip"), data=zip_data,
                        file_name="aoaa_results.zip", mime="application/zip")
