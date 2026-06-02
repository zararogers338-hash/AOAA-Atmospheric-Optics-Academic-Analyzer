# -*- coding: utf-8 -*-
"""AOAA - Atmospheric Optics Academic Analyzer
Main entry point / Home page.
"""

import streamlit as st
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.shared_ui import init_page, render_shared_sidebar
from utils.i18n import t, get_lang

# ── Initialize ──
init_page(title="AOAA - Home")
render_shared_sidebar()

lang = get_lang()
st.title(t("app_title"))

# ── Welcome section ──
if lang == "zh":
    st.markdown("## " + t("home_welcome_title"))
else:
    st.markdown("## " + t("home_welcome_title"))

st.markdown(t("app_title") + " — " +
            ("用大气光学隐喻理解学术文献中的方法模式" if lang == "zh"
             else "Understand methodological patterns in academic literature through atmospheric optics metaphors"))

# ── Quick Start ──
st.subheader(t("home_quick_start"))
steps = [
    t("home_step1"),
    t("home_step2"),
    t("home_step3"),
    t("home_step4"),
]
for i, s in enumerate(steps, 1):
    st.markdown(f"{i}. {s}")

# ── Phenomena table ──
st.subheader(t("home_phenomena_title"))
phenomena_data = [
    ("aurora", "🌌"),
    ("noctilucent", "☁️"),
    ("nacreous", "🌈"),
    ("asperitas", "🌊"),
    ("lenticular", "🏔️"),
    ("circumhorizontal", "🔥"),
    ("fallstreak", "🕳️"),
    ("brocken", "👻"),
    ("moonbow", "🌙"),
]
if lang == "zh":
    st.markdown("| 现象 | 学术隐喻 | 页面 |")
    st.markdown("|------|---------|------|")
    for key, emoji in phenomena_data:
        name = t(key)
        st.markdown(f"| {emoji} {name.split(' - ')[0] if ' - ' in name else name} | "
                    f"{name.split(' - ')[1] if ' - ' in name else name} | "
                    f"{name.split(' - ')[0] if ' - ' in name else name} 分析 |")
else:
    st.markdown("| Phenomenon | Academic Metaphor | Page |")
    st.markdown("|-----------|-------------------|------|")
    for key, emoji in phenomena_data:
        name = t(key)
        en_part = name.split(" - ")[1] if " - " in name else name
        en_first = name.split(" - ")[0] if " - " in name else name
        st.markdown(f"| {emoji} {en_first} | {en_part} | {en_first} |")

# ── AI Backend Support ──
st.subheader(t("home_ai_title"))
st.markdown(f"- {t('home_ai_llama')}")
st.markdown(f"- {t('home_ai_ollama')}")
st.markdown(f"- {t('home_ai_openai')}")
st.markdown(f"*{t('home_ai_note')}*")

# ── Custom Prompts ──
st.subheader(t("home_prompt_title"))
st.markdown(t("home_prompt_desc"))

# ── Data Status ──
if st.session_state.get("files_loaded"):
    st.divider()
    analysis = st.session_state.get("analysis_data", {})
    doc_n = analysis.get("doc_count", 0)
    kw_n = len(analysis.get("tfidf", {}).get("global_top", []))
    edge_n = len(analysis.get("cooccurrence", {}).get("edges", []))

    st.success(t("home_data_loaded", doc_n=doc_n, kw_n=kw_n, edge_n=edge_n))
    st.info(t("home_nav_hint"))
