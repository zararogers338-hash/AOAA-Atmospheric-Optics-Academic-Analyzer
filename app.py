# -*- coding: utf-8 -*-
"""AOAA - Atmospheric Optics Academic Analyzer
Main entry point / Home page.
"""

import streamlit as st
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.shared_ui import init_page, render_shared_sidebar
from utils.i18n import t, get_lang

# ── Initialize ──
init_page(title="AOAA - Home")
render_shared_sidebar()

# ── Home Content ──
lang = get_lang()

st.title(t("app_title"))

if lang == "zh":
    st.markdown("""
    ## 🌌 欢迎使用大气光学学术分析器

    本工具将学术文献分析与大气光学现象相结合，用纯粹的气象/光学过程隐喻来理解学术方法论的动态。

    ### 🚀 快速开始

    1. **上传文献** → 在左侧边栏上传 TXT/PDF/CSV/WOS 等格式的学术文献
    2. **点击加载** → 点击"开始加载"按钮，系统自动解析并分析
    3. **浏览页面** → 在左侧导航选择不同的大气现象分析页面
    4. **AI 分析**（可选）→ 配置模型后端获取 AI 隐喻解读

    ### 📖 9 大大气光学现象

    | 现象 | 学术隐喻 | 页面 |
    |------|---------|------|
    | 🌌 极光 Aurora | 高影响力突破方法 | 极光分析 |
    | ☁️ 夜光云 | 远期前沿方法 | 夜光云分析 |
    | 🌈 珠母云 | 珍稀精密方法 | 珠母云分析 |
    | 🌊 Asperitas | 剧烈扰动争议方法 | Asperitas 分析 |
    | 🏔️ 透镜云 | 稳固对称方法 | 透镜云分析 |
    | 🔥 火彩虹 | 纯度极高精准方法 | 火彩虹分析 |
    | 🕳️ 陨落孔 | 人为触发连锁方法 | 陨落孔分析 |
    | 👻 布罗肯幽灵 | 观测者中心方法 | 布罗肯分析 |
    | 🌙 月虹 | 低亮幽灵方法 | 月虹分析 |

    ### 🤖 AI 后端支持

    - **llama-cpp-python** — 本地 GGUF 模型，支持 GPU 加速
    - **Ollama** — 本地模型管理，支持拉取/加载/多模型 Ensemble
    - **OpenAI 兼容 API** — 任何兼容 API（含国产大模型）

    无模型时，统计分析与可视化仍完整可用。

    ### ✏️ 自定义提示词

    在左侧"自定义提示词"区域可以：
    - 设置系统提示词（角色设定）
    - 设置分析模板（变量: `{phenomenon}`, `{description}`, `{keywords}`, `{doc_count}`）
    - 调节提示词强度（轻量/标准/强劲/极限）
    """)
else:
    st.markdown("""
    ## 🌌 Welcome to AOAA

    This tool combines academic literature analysis with atmospheric optical phenomena, using pure meteorological/optical process metaphors to understand academic methodology dynamics.

    ### 🚀 Quick Start

    1. **Upload Files** → Upload academic literature (TXT/PDF/CSV/WOS/etc.) in the sidebar
    2. **Start Loading** → Click the "Start Loading" button for automatic parsing and analysis
    3. **Browse Pages** → Navigate to different atmospheric phenomenon pages
    4. **AI Analysis** (optional) → Configure a model backend for AI metaphor interpretations

    ### 📖 9 Atmospheric Optical Phenomena

    | Phenomenon | Academic Metaphor | Page |
    |-----------|-------------------|------|
    | 🌌 Aurora | High-impact breakthroughs | Aurora |
    | ☁️ Noctilucent | Far-horizon frontier | Noctilucent |
    | 🌈 Nacreous | Rare precision methods | Nacreous |
    | 🌊 Asperitas | Turbulent controversy | Asperitas |
    | 🏔️ Lenticular | Stable symmetric | Lenticular |
    | 🔥 Circumhorizontal | Ultra-pure precision | Circumhorizontal |
    | 🕳️ Fallstreak | Human-triggered cascade | Fallstreak |
    | 👻 Brocken Spectre | Observer-centric | Brocken |
    | 🌙 Moonbow | Low-light spectral | Moonbow |

    ### 🤖 AI Backend Support

    - **llama-cpp-python** — Local GGUF models with GPU acceleration
    - **Ollama** — Local model management with pull/load/ensemble
    - **OpenAI Compatible API** — Any compatible API

    Statistics and visualizations work fully without any AI model.

    ### ✏️ Custom Prompts

    In the sidebar "Custom Prompts" section:
    - Set a system prompt (role definition)
    - Set analysis template (variables: `{phenomenon}`, `{description}`, `{keywords}`, `{doc_count}`)
    - Adjust prompt strength (Light / Standard / Strong / Maximum)
    """)

# Show data status if loaded
if st.session_state.get("files_loaded"):
    st.divider()
    analysis = st.session_state.get("analysis_data", {})
    doc_n = analysis.get("doc_count", 0)
    kw_n = len(analysis.get("tfidf", {}).get("global_top", []))
    edge_n = len(analysis.get("cooccurrence", {}).get("edges", []))

    if lang == "zh":
        st.success(f"✅ 数据已加载：{doc_n} 篇文献 | {kw_n} 个关键词 | {edge_n} 条共现关系")
        st.info("👈 点击左侧导航栏选择分析页面")
    else:
        st.success(f"✅ Data loaded: {doc_n} documents | {kw_n} keywords | {edge_n} co-occurrence edges")
        st.info("👈 Use the sidebar navigation to explore analysis pages")
