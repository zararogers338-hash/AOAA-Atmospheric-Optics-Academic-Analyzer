# -*- coding: utf-8 -*-
"""Shared UI components: session init, sidebar, model panel, analysis pipeline.
Every page MUST call init_page() and render_shared_sidebar() to work properly.
"""

import streamlit as st
import os
import yaml
from typing import Dict, Any

from utils.i18n import t, get_lang, set_lang, toggle_lang
from utils.logger import log_info, log_warn, log_error, get_logs, clear_logs
from utils.file_parser import parse_files
from utils.nlp import run_full_analysis
from utils.graph import build_cooccurrence_graph, compute_centrality, classify_atmosphere
from utils.system_monitor import get_full_status, format_status_text


def _load_config() -> dict:
    """Load config.yaml from project root."""
    paths = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.yaml"),
        os.path.join(os.getcwd(), "config.yaml"),
        "config.yaml",
    ]
    for p in paths:
        try:
            with open(p, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            continue
    return {}


def init_page(title: str = "AOAA", icon: str = "🌌"):
    """Initialize page config + session state. MUST be called first in every page."""
    try:
        st.set_page_config(page_title=title, page_icon=icon, layout="wide",
                           initial_sidebar_state="expanded")
    except st.errors.StreamlitAPIException:
        pass  # Already set

    defaults = {
        "lang": "zh",
        "config": _load_config(),
        "parsed_results": [],
        "analysis_data": {},
        "atmosphere_data": {},
        "sidebar_visible": True,
        "active_backend": None,
        "backend_type": "none",
        "ensemble_enabled": False,
        "hybrid_enabled": False,
        "log_entries": [],
        "files_loaded": False,
        "custom_prompt_template": "",
        "custom_system_prompt": "",
        "show_node_labels": True,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _get_or_create_backend(backend_type: str):
    """Get or create AI backend by type."""
    from utils.ai_backends.llama_cpp_backend import LlamaCppBackend
    from utils.ai_backends.ollama_backend import OllamaBackend
    from utils.ai_backends.openai_compat_backend import OpenAICompatBackend
    from utils.ai_backends.ensemble import EnsembleBackend

    key = f"_backend_{backend_type}"
    if key not in st.session_state:
        if backend_type == "llama_cpp":
            st.session_state[key] = LlamaCppBackend()
        elif backend_type == "ollama":
            st.session_state[key] = OllamaBackend()
        elif backend_type == "openai_compat":
            st.session_state[key] = OpenAICompatBackend()
        elif backend_type == "ensemble":
            st.session_state[key] = EnsembleBackend()
        else:
            return None
    return st.session_state[key]


def _run_analysis(uploaded_files):
    """Run the full analysis pipeline with progress + logs."""
    lang = get_lang()
    config = st.session_state.config
    config_analysis = config.get("analysis", {})

    log_info(f"Starting analysis pipeline with {len(uploaded_files)} files")
    progress_bar = st.progress(0, text=t("loading"))
    status_container = st.status(t("processing"), expanded=True)

    with status_container:
        # Phase 1: Parse files
        st.write(f"📄 {'解析文件...' if lang == 'zh' else 'Parsing files...'}")
        try:
            def update_parse_progress(pct):
                progress_bar.progress(pct * 0.4, text=f"Parsing: {int(pct*100)}%")

            results = parse_files(uploaded_files, progress_callback=update_parse_progress)
            success_count = sum(1 for r in results if r["success"])
            fail_count = len(results) - success_count
            st.write(f"✅ {success_count} {t('success')}, ⚠️ {fail_count} {t('failed')}")

            if fail_count > 0:
                for r in results:
                    if not r["success"]:
                        fname = r.get("metadata", {}).get("filename", "unknown")
                        st.write(f"  ⚠️ {fname}: {r.get('error', 'unknown error')}")

            st.session_state.parsed_results = results
        except Exception as e:
            log_error("File parsing failed", e)
            st.error(f"Parsing error: {e}")
            return

        progress_bar.progress(0.4, text="Analyzing...")

        # Phase 2: NLP Analysis
        st.write(f"🔬 {'运行 NLP 分析...' if lang == 'zh' else 'Running NLP analysis...'}")
        try:
            analysis = run_full_analysis(results, config_analysis)
            st.session_state.analysis_data = analysis
            kw_count = len(analysis.get('tfidf', {}).get('global_top', []))
            edge_count = len(analysis.get('cooccurrence', {}).get('edges', []))
            st.write(f"✅ TF-IDF: {kw_count} keywords, Co-occurrence: {edge_count} edges")
        except Exception as e:
            log_error("NLP analysis failed", e)
            st.error(f"Analysis error: {e}")
            st.session_state.analysis_data = {}

        progress_bar.progress(0.7, text="Building graph...")

        # Phase 3: Graph & Atmosphere
        st.write(f"🌐 {'构建图谱...' if lang == 'zh' else 'Building graph...'}")
        try:
            cooc_data = analysis.get("cooccurrence", {})
            G = build_cooccurrence_graph(cooc_data)
            if G and G.number_of_nodes() > 0:
                centrality = compute_centrality(G)
                atmo = classify_atmosphere(analysis, centrality)
                st.session_state.atmosphere_data = atmo
                st.session_state["centrality_data"] = centrality
                st.write(f"✅ Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
            else:
                st.session_state.atmosphere_data = {}
                st.write("⚠️ Graph: insufficient data")
        except Exception as e:
            log_error("Graph analysis failed", e)
            st.session_state.atmosphere_data = {}

        progress_bar.progress(1.0, text=t("done"))
        st.session_state.files_loaded = True
        st.write(f"🎉 {t('done')}!")
        log_info("Analysis pipeline complete")


def render_shared_sidebar():
    """Render the shared sidebar on every page: upload, navigation hint, model panel, logs."""
    lang = get_lang()

    with st.sidebar:
        st.title(t("sidebar_title"))

        # Language toggle
        if st.button(t("lang_switch"), key="lang_toggle_shared", use_container_width=True):
            toggle_lang()
            st.rerun()

        st.divider()

        # ─── File Upload ───
        st.subheader(t("upload_files"))
        uploaded = st.file_uploader(
            t("upload_files"),
            accept_multiple_files=True,
            type=["txt", "md", "pdf", "doc", "docx", "json", "jsonl", "csv", "tsv",
                  "xlsx", "xls", "html", "xml", "yaml", "yml", "ris", "bib"],
            key="file_uploader_shared",
            label_visibility="collapsed"
        )

        if uploaded:
            st.info(f"{len(uploaded)} {'files selected' if lang == 'en' else '个文件已选择'}")

        if st.button(f"🚀 {t('start_loading')}", key="start_loading_shared",
                      type="primary", disabled=not uploaded, use_container_width=True):
            if uploaded:
                _run_analysis(uploaded)

        # Data status
        if st.session_state.get("files_loaded"):
            ad = st.session_state.get("analysis_data", {})
            doc_n = ad.get("doc_count", 0)
            kw_n = len(ad.get("tfidf", {}).get("global_top", []))
            st.success(f"{'已加载' if lang=='zh' else 'Loaded'}: {doc_n} docs, {kw_n} keywords")

        st.divider()

        # ─── Node Label Toggle ───
        show_labels = st.toggle(
            t("node_label_toggle"),
            value=st.session_state.get("show_node_labels", True),
            key="node_label_toggle_shared",
            help=t("node_label_help"),
        )
        st.session_state.show_node_labels = show_labels

        st.divider()

        # ─── Model Control Panel ───
        _render_model_panel_sidebar()

        st.divider()

        # ─── Custom Prompt ───
        _render_custom_prompt_section()

        st.divider()

        # ─── Logs ───
        st.subheader(t("log_title"))
        if st.button(t("log_clear"), key="clear_log_shared"):
            clear_logs()
        log_text = get_logs()
        st.text_area(t("log_title"), value=log_text[-3000:] if log_text else "",
                      height=120, key="log_area_shared", label_visibility="collapsed")


def _render_custom_prompt_section():
    """Render custom prompt template section in sidebar."""
    lang = get_lang()
    label = "自定义提示词" if lang == "zh" else "Custom Prompts"
    st.subheader(f"✏️ {label}")

    # System prompt
    sys_label = "系统提示词 (System Prompt)" if lang == "zh" else "System Prompt"
    sys_help = ("自定义 AI 的角色设定和行为约束。留空则使用默认大气光学隐喻专家。"
                if lang == "zh" else
                "Customize AI role and behavior. Leave empty for default atmospheric optics metaphor expert.")
    sys_prompt = st.text_area(
        sys_label, value=st.session_state.get("custom_system_prompt", ""),
        height=80, key="custom_sys_prompt_input", help=sys_help,
        placeholder="例: 你是一个专注于大气光学过程的学术分析专家..." if lang == "zh" else "e.g.: You are an expert in atmospheric optics academic analysis..."
    )
    st.session_state.custom_system_prompt = sys_prompt

    # Analysis prompt template
    tpl_label = "分析提示词模板" if lang == "zh" else "Analysis Prompt Template"
    tpl_help = ("用于生成隐喻分析的模板。可用变量: {phenomenon}, {description}, {keywords}, {doc_count}。"
                if lang == "zh" else
                "Template for metaphor analysis. Variables: {phenomenon}, {description}, {keywords}, {doc_count}.")
    tpl_prompt = st.text_area(
        tpl_label, value=st.session_state.get("custom_prompt_template", ""),
        height=80, key="custom_tpl_prompt_input", help=tpl_help,
        placeholder=("请用大气光学隐喻分析 {phenomenon} 现象对应的学术方法: {keywords}"
                      if lang == "zh" else
                      "Analyze {phenomenon} phenomenon's academic methods using atmospheric optics metaphors: {keywords}")
    )
    st.session_state.custom_prompt_template = tpl_prompt

    # Prompt strength selector
    strength_label = "提示词强度" if lang == "zh" else "Prompt Strength"
    strength = st.select_slider(
        strength_label,
        options=["light", "standard", "strong", "maximum"],
        value=st.session_state.get("prompt_strength", "strong"),
        key="prompt_strength_slider",
        format_func=lambda x: {
            "light": "轻量" if lang == "zh" else "Light",
            "standard": "标准" if lang == "zh" else "Standard",
            "strong": "强劲" if lang == "zh" else "Strong",
            "maximum": "极限" if lang == "zh" else "Maximum"
        }.get(x, x)
    )
    st.session_state["prompt_strength"] = strength


def _render_model_panel_sidebar():
    """Render model control panel in sidebar."""
    from utils.ai_backends.ensemble import EnsembleBackend, HybridBackend
    lang = get_lang()
    st.subheader(t("model_panel"))

    # Backend selector
    backend_options = ["none", "llama_cpp", "ollama", "openai_compat"]
    backend_labels = {
        "none": t("no_backend"),
        "llama_cpp": "llama-cpp (GGUF)",
        "ollama": "Ollama",
        "openai_compat": "OpenAI API"
    }
    current_bt = st.session_state.get("backend_type", "none")

    selected_bt = st.selectbox(
        t("backend_type"),
        backend_options,
        index=backend_options.index(current_bt) if current_bt in backend_options else 0,
        format_func=lambda x: backend_labels.get(x, x),
        key="backend_selector_shared"
    )

    if selected_bt != current_bt:
        st.session_state.backend_type = selected_bt
        if selected_bt == "none":
            st.session_state.active_backend = None

    # Backend-specific config
    if selected_bt == "llama_cpp":
        model_path = st.text_input("GGUF Path", key="gguf_path_s")
        n_ctx = st.number_input("n_ctx", value=32768, min_value=2048, step=4096, key="gguf_nctx_s")
        n_gpu = st.number_input("n_gpu_layers (-1=all)", value=-1, min_value=-1, key="gguf_ngpu_s")
        if st.button("Load GGUF", key="load_gguf_s", use_container_width=True):
            backend = _get_or_create_backend("llama_cpp")
            with st.spinner("Loading..."):
                ok = backend.load(model_path=model_path, n_ctx=n_ctx, n_gpu_layers=n_gpu)
            if ok:
                st.session_state.active_backend = backend
                st.success("✅ GGUF loaded!")
            else:
                st.error("❌ Load failed")

    elif selected_bt == "ollama":
        base_url = st.text_input("Ollama URL", value="http://localhost:11434", key="ollama_url_s")
        if st.button("List Models", key="ollama_list_s", use_container_width=True):
            backend = _get_or_create_backend("ollama")
            backend.base_url = base_url
            with st.spinner("Connecting..."):
                models = backend.list_models()
            if models:
                st.session_state["ollama_models_list"] = models
                st.success(f"Found {len(models)} models")
            else:
                st.error("Cannot reach Ollama or no models")

        models_list = st.session_state.get("ollama_models_list", [])
        if models_list:
            sel_model = st.selectbox("Model", models_list, key="ollama_model_sel_s")
            if st.button("Load Model", key="ollama_load_s", use_container_width=True):
                backend = _get_or_create_backend("ollama")
                with st.spinner(f"Loading {sel_model}..."):
                    ok = backend.load(model_name=sel_model, base_url=base_url)
                if ok:
                    st.session_state.active_backend = backend
                    st.success(f"✅ {sel_model}")
                else:
                    st.error("❌ Load failed — check Ollama is running")

        pull_name = st.text_input("Pull Model", key="ollama_pull_name_s",
                                   placeholder="e.g. qwen2.5:7b")
        if st.button("Pull", key="ollama_pull_s") and pull_name:
            backend = _get_or_create_backend("ollama")
            backend.base_url = base_url
            prog = st.progress(0)
            def _upd(pct, status):
                prog.progress(min(pct, 1.0), text=status[:50])
            ok = backend.pull_model(pull_name, progress_callback=_upd)
            st.success(f"Pulled: {pull_name}") if ok else st.error("Pull failed")

        # Modelfile template
        mf_label = "Modelfile Prompt" if lang == "en" else "Modelfile 提示模板"
        mf = st.text_area(mf_label, height=60, key="ollama_modelfile_s",
                           placeholder="FROM model\nSYSTEM You are...")
        if mf:
            st.session_state["ollama_modelfile"] = mf

    elif selected_bt == "openai_compat":
        api_url = st.text_input("Base URL", key="oai_url_s",
                                 placeholder="https://api.openai.com/v1")
        api_key = st.text_input("API Key", type="password", key="oai_key_s")
        api_model = st.text_input("Model", key="oai_model_s", placeholder="gpt-4o-mini")
        temp = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1, key="oai_temp_s")
        if st.button("Connect", key="oai_connect_s", use_container_width=True):
            backend = _get_or_create_backend("openai_compat")
            with st.spinner("Connecting..."):
                ok = backend.load(base_url=api_url, api_key=api_key, model=api_model,
                                  temperature=temp)
            if ok:
                st.session_state.active_backend = backend
                st.success("✅ Connected!")
            else:
                st.error("❌ Connection failed")

    # ─── Status display ───
    active = st.session_state.get("active_backend")
    if active and getattr(active, "is_loaded", False):
        status = active.get_status()
        st.markdown(f"🟢 **{status['model']}**")
        st.caption(f"ctx={status['context_length']} | q={status['quant_level']} | "
                   f"{status['latency_sec']}s | ~{status['tokens_per_sec_approx']} tok/s")
    else:
        st.markdown("🔴 " + t("ai_not_enabled"))

    # System info
    try:
        sys_status = get_full_status()
        st.caption(format_status_text(sys_status, lang))
    except Exception:
        pass

    # Action buttons
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🏥", key="health_s", help=t("health_check"), use_container_width=True):
            if active and getattr(active, "is_loaded", False):
                result = active.health_check()
                st.success(result["message"]) if result["healthy"] else st.error(result["message"])
            else:
                st.info(t("ai_not_enabled"))
    with c2:
        if st.button("🔀", key="ensemble_s", help=t("ensemble_toggle"), use_container_width=True):
            st.session_state.ensemble_enabled = not st.session_state.get("ensemble_enabled", False)
            if st.session_state.ensemble_enabled:
                ens = _get_or_create_backend("ensemble")
                for bt in ["llama_cpp", "ollama", "openai_compat"]:
                    b = st.session_state.get(f"_backend_{bt}")
                    if b and getattr(b, "is_loaded", False):
                        ens.add_backend(b)
                ens.load(strategy="vote")
                st.session_state.active_backend = ens
                log_info("Ensemble ON")
            else:
                log_info("Ensemble OFF")
            st.rerun()

    if st.button(f"🔄 {t('hybrid_mode')}", key="hybrid_s", use_container_width=True):
        llama = st.session_state.get("_backend_llama_cpp")
        ollama = st.session_state.get("_backend_ollama")
        if llama and ollama:
            hybrid = HybridBackend(llama, ollama)
            hybrid.load()
            st.session_state.active_backend = hybrid
            st.success("Hybrid ON")
        else:
            st.warning("Need both llama_cpp + ollama")


def get_ai_prompt(phenom_key: str, matched_kws: list, lang: str,
                  extra_context: str = "") -> str:
    """Build AI prompt using custom templates or defaults, with strength scaling."""
    from utils.i18n import t as _t
    strength = st.session_state.get("prompt_strength", "strong")
    custom_sys = st.session_state.get("custom_system_prompt", "").strip()
    custom_tpl = st.session_state.get("custom_prompt_template", "").strip()

    phenom_name = _t(phenom_key)
    desc = _t(f"{phenom_key}_desc")
    kw_list = ", ".join([f"{kw['keyword']}(score={kw['tfidf']:.3f})" for kw in matched_kws[:8]])
    doc_count = st.session_state.get("analysis_data", {}).get("doc_count", 0)

    # If user has custom template, use it
    if custom_tpl:
        try:
            prompt = custom_tpl.format(
                phenomenon=phenom_name, description=desc,
                keywords=kw_list, doc_count=doc_count
            )
        except (KeyError, IndexError):
            prompt = custom_tpl  # Use as-is if format fails
    else:
        # Default prompt by strength
        prompt = _build_default_prompt(phenom_name, desc, kw_list, doc_count, lang, strength)

    # Prepend system prompt if custom
    if custom_sys:
        prompt = f"[System: {custom_sys}]\n\n{prompt}"

    if extra_context:
        prompt += f"\n\nAdditional context:\n{extra_context}"

    return prompt


def _build_default_prompt(phenom_name, desc, kw_list, doc_count, lang, strength):
    """Build default prompt at various strength levels."""
    if lang == "zh":
        base_role = "你是一个大气光学学术隐喻专家。"
        constraint = "严格禁止使用任何生物学、生态学、物种、捕食者、灭绝、碳汇等概念。只能使用大气/气象/光学过程的隐喻。"
        task = f"当前分析的大气光学现象：{phenom_name}\n描述：{desc}\n匹配到的学术关键词/方法（共{doc_count}篇文献）：{kw_list}"

        if strength == "light":
            return f"{base_role}\n{task}\n请用100字以内简述这些关键词与该现象的关联。"
        elif strength == "standard":
            return f"{base_role}\n{constraint}\n{task}\n请用200字以内，用该现象的物理过程隐喻解释这些方法的特征与趋势。"
        elif strength == "strong":
            return (
                f"{base_role}\n{constraint}\n\n{task}\n\n"
                f"请严格执行以下分析框架：\n"
                f"1. 【现象映射】将每个关键词映射到该大气光学现象的具体物理过程环节\n"
                f"2. 【能量分析】用光学能量/折射/散射/衍射/干涉概念描述方法间的相互作用\n"
                f"3. 【趋势预测】用气象演变（气团移动、锋面推进、云层消散/凝聚）预测发展方向\n"
                f"4. 【强度评估】用光学亮度/色散度/可见度评估每个方法的当前学术影响力\n"
                f"要求300字以内，必须包含至少3个具体的光学/气象术语。"
            )
        else:  # maximum
            return (
                f"{base_role}\n{constraint}\n\n"
                f"===== 极限分析任务 =====\n{task}\n\n"
                f"请按照以下严格框架进行深度分析（400字以内）：\n\n"
                f"【第一层：光学现象解构】\n"
                f"- 将 {phenom_name} 的物理形成机制逐步拆解\n"
                f"- 每个物理步骤对应一个学术方法或关键词\n\n"
                f"【第二层：能量光谱分析】\n"
                f"- 用光谱分布描述各方法在学术影响力频谱上的位置\n"
                f"- 哪些在紫外（前沿高能）？哪些在红外（成熟低能但稳定）？\n"
                f"- 识别光谱间隙（研究空白）和吸收线（被压制的方法）\n\n"
                f"【第三层：大气动力学预测】\n"
                f"- 用气压梯度力、科里奥利效应、对流-辐射平衡预测方法演变\n"
                f"- 指出哪些方法正在经历'相变'（如冰晶化→质变突破）\n"
                f"- 预测未来可能出现的'大气光学新现象'（学术新范式）\n\n"
                f"【第四层：观测者效应】\n"
                f"- 研究者自身视角如何影响这些方法的'可见度'\n"
                f"- 不同学科背景的观测者会看到不同的'光学现象'\n\n"
                f"要求：每段必须包含至少2个专业大气/光学术语。禁止任何生物/生态隐喻。"
            )
    else:
        base_role = "You are an atmospheric optics academic metaphor expert."
        constraint = ("STRICTLY FORBIDDEN: any biology, ecology, species, predator, extinction, "
                      "carbon sink concepts. Use ONLY atmospheric/meteorological/optical metaphors.")
        task = f"Phenomenon: {phenom_name}\nDescription: {desc}\nMatched keywords ({doc_count} documents): {kw_list}"

        if strength == "light":
            return f"{base_role}\n{task}\nBriefly relate these keywords to this phenomenon in under 100 words."
        elif strength == "standard":
            return f"{base_role}\n{constraint}\n{task}\nIn under 200 words, metaphorically explain using physical processes."
        elif strength == "strong":
            return (
                f"{base_role}\n{constraint}\n\n{task}\n\n"
                f"Execute this analysis framework:\n"
                f"1. [Phenomenon Mapping] Map each keyword to specific physical process stages\n"
                f"2. [Energy Analysis] Use refraction/scattering/diffraction/interference for interactions\n"
                f"3. [Trend Forecast] Use meteorological evolution to predict development\n"
                f"4. [Intensity Assessment] Use optical brightness/dispersion/visibility for impact\n"
                f"Under 300 words. Include at least 3 specific optical/meteorological terms."
            )
        else:  # maximum
            return (
                f"{base_role}\n{constraint}\n\n"
                f"===== MAXIMUM ANALYSIS =====\n{task}\n\n"
                f"Analyze in 4 layers (under 400 words):\n\n"
                f"[Layer 1: Optical Phenomenon Deconstruction]\n"
                f"- Decompose the physical formation mechanism of {phenom_name}\n"
                f"- Map each physical step to an academic method\n\n"
                f"[Layer 2: Spectral Analysis]\n"
                f"- Place methods on the academic impact frequency spectrum\n"
                f"- UV (frontier high-energy) vs IR (mature stable)\n"
                f"- Identify spectral gaps (research blanks) and absorption lines (suppressed methods)\n\n"
                f"[Layer 3: Atmospheric Dynamics Prediction]\n"
                f"- Use pressure gradients, Coriolis effect, convection-radiation balance\n"
                f"- Identify methods undergoing 'phase transitions'\n\n"
                f"[Layer 4: Observer Effect]\n"
                f"- How researcher perspective affects method 'visibility'\n\n"
                f"Every paragraph must contain 2+ professional atmospheric/optical terms."
            )
