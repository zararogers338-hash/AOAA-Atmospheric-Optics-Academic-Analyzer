# -*- coding: utf-8 -*-
"""Internationalization module for AOAA. All UI text must go through t()."""

import streamlit as st

_DICT = {
    # Global
    "app_title": {"zh": "AOAA - 大气光学学术分析器", "en": "AOAA - Atmospheric Optics Academic Analyzer"},
    "sidebar_title": {"zh": "控制面板", "en": "Control Panel"},
    "lang_switch": {"zh": "Switch to English", "en": "切换到中文"},
    "sidebar_expand": {"zh": "展开侧边栏", "en": "Expand Sidebar"},
    "sidebar_collapse": {"zh": "收起侧边栏", "en": "Collapse Sidebar"},
    "start_loading": {"zh": "开始加载", "en": "Start Loading"},
    "loading": {"zh": "加载中...", "en": "Loading..."},
    "done": {"zh": "完成", "en": "Done"},
    "error": {"zh": "错误", "en": "Error"},
    "warning": {"zh": "警告", "en": "Warning"},
    "info": {"zh": "信息", "en": "Info"},
    "export": {"zh": "导出", "en": "Export"},
    "export_json": {"zh": "导出 JSON", "en": "Export JSON"},
    "export_txt": {"zh": "导出 TXT", "en": "Export TXT"},
    "export_svg": {"zh": "导出 SVG", "en": "Export SVG"},
    "export_zip": {"zh": "导出结果 ZIP", "en": "Export Results ZIP"},
    "no_data": {"zh": "暂无数据，请先上传文献并点击加载。", "en": "No data yet. Please upload files and click Start Loading."},
    "upload_files": {"zh": "上传文献文件", "en": "Upload Literature Files"},
    "processing": {"zh": "处理中", "en": "Processing"},
    "success": {"zh": "成功", "en": "Success"},
    "failed": {"zh": "失败", "en": "Failed"},
    "skipped": {"zh": "已跳过", "en": "Skipped"},
    "retry": {"zh": "重试", "en": "Retry"},
    "cancel": {"zh": "取消", "en": "Cancel"},
    "search": {"zh": "搜索 (标题/关键词/作者)", "en": "Search (title/keyword/author)"},
    "year_range": {"zh": "年份范围", "en": "Year Range"},
    "min_citations": {"zh": "最小引用数", "en": "Min Citations"},
    "max_docs": {"zh": "最大文献数", "en": "Max Documents"},
    "keyword_threshold": {"zh": "关键词阈值", "en": "Keyword Threshold"},

    # Model panel
    "model_panel": {"zh": "模型控制面板", "en": "Model Control Panel"},
    "backend_type": {"zh": "后端类型", "en": "Backend Type"},
    "model_name": {"zh": "模型名称", "en": "Model Name"},
    "context_length": {"zh": "上下文长度", "en": "Context Length"},
    "quant_level": {"zh": "量化级别", "en": "Quantization Level"},
    "vram_usage": {"zh": "显存/内存占用", "en": "VRAM/Memory Usage"},
    "inference_latency": {"zh": "推理延迟", "en": "Inference Latency"},
    "tokens_per_sec": {"zh": "tokens/s", "en": "tokens/s"},
    "switch_backend": {"zh": "切换后端", "en": "Switch Backend"},
    "health_check": {"zh": "健康检查", "en": "Health Check"},
    "load_backup": {"zh": "加载备用模型", "en": "Load Backup Model"},
    "ensemble_toggle": {"zh": "启用/关闭 Ensemble", "en": "Toggle Ensemble"},
    "hybrid_mode": {"zh": "混合推理模式", "en": "Hybrid Inference Mode"},
    "no_backend": {"zh": "无后端 (仅统计)", "en": "No Backend (Stats Only)"},
    "ai_not_enabled": {"zh": "AI 未启用 - 仅显示统计分析结果", "en": "AI Not Enabled - Showing statistical analysis only"},

    # Overview
    "overview": {"zh": "学术大气层状态总览", "en": "Academic Atmosphere Overview"},
    "high_pressure": {"zh": "高压区 (主流稳定)", "en": "High Pressure (Mainstream Stable)"},
    "low_pressure": {"zh": "低压槽 (新兴扰动)", "en": "Low Pressure Trough (Emerging Disturbance)"},
    "front": {"zh": "锋面 (方法冲突)", "en": "Front (Method Conflict)"},
    "jet_stream": {"zh": "急流 (传播通道)", "en": "Jet Stream (Propagation Channel)"},
    "keywords_chart": {"zh": "关键词分布", "en": "Keyword Distribution"},
    "trend_chart": {"zh": "年份趋势", "en": "Year Trend"},
    "cooccurrence": {"zh": "共现网络", "en": "Co-occurrence Network"},
    "citation_dist": {"zh": "引用分布", "en": "Citation Distribution"},

    # Phenomena
    "aurora": {"zh": "极光 - 高影响力突破方法", "en": "Aurora - High-Impact Breakthrough Methods"},
    "noctilucent": {"zh": "夜光云 - 远期前沿方法", "en": "Noctilucent Clouds - Far-Horizon Frontier Methods"},
    "nacreous": {"zh": "珠母云 - 珍稀精密方法", "en": "Nacreous Clouds - Rare Precision Methods"},
    "asperitas": {"zh": "Asperitas - 剧烈扰动争议方法", "en": "Asperitas - Turbulent Controversial Methods"},
    "lenticular": {"zh": "透镜云 - 稳固对称方法", "en": "Lenticular Clouds - Stable Symmetric Methods"},
    "circumhorizontal": {"zh": "火彩虹 - 纯度极高精准方法", "en": "Circumhorizontal Arc - Ultra-Pure Precision Methods"},
    "fallstreak": {"zh": "陨落孔 - 人为触发连锁方法", "en": "Fallstreak Hole - Human-Triggered Cascade Methods"},
    "brocken": {"zh": "布罗肯幽灵 - 观测者中心方法", "en": "Brocken Spectre - Observer-Centric Methods"},
    "moonbow": {"zh": "月虹 - 低亮幽灵方法", "en": "Moonbow - Low-Light Spectral Methods"},

    # Phenomenon descriptions
    "aurora_desc": {
        "zh": "如同太阳风粒子激发高层大气产生宏大流动光芒，这些方法在高影响力期刊层闪耀，需要持续的外部数据驱动（如太阳风般的资金与数据源）才能维持光辉。",
        "en": "Like solar wind particles exciting the upper atmosphere to produce grand flowing radiance, these methods shine in high-impact journal layers, requiring continuous external data drive (like solar wind-like funding and data sources) to maintain their brilliance."
    },
    "noctilucent_desc": {
        "zh": "如同中间层大气在暮光中短暂闪耀的电蓝银白丝状结构，这些前沿方法在学术边缘闪现，反射着即将落下的旧范式余晖，预示着新的研究黎明。",
        "en": "Like the electric-blue silvery filaments briefly shining in the mesosphere at twilight, these frontier methods flash at the academic edge, reflecting the afterglow of fading paradigms and heralding a new research dawn."
    },
    "nacreous_desc": {
        "zh": "如同极寒平流层中形成的珍珠般油膜彩虹光泽云层，这些方法极为罕见且精密，需要极端条件（高纯度数据、极精确校准）才能显现其多彩光谱。",
        "en": "Like the pearlescent oily-rainbow-sheen clouds forming in the ultra-cold stratosphere, these methods are extremely rare and precise, requiring extreme conditions (high-purity data, ultra-precise calibration) to reveal their colorful spectra."
    },
    "asperitas_desc": {
        "zh": "如同云底翻滚的海浪般起伏、下垂尖刺的剧烈扰动云层，这些方法在学术界引发激烈争论，其湍流般的不稳定性既带来创新也带来混乱。",
        "en": "Like the violently undulating, wave-like rolling and drooping spikes at cloud bases, these methods spark fierce academic debate, their turbulent instability bringing both innovation and chaos."
    },
    "lenticular_desc": {
        "zh": "如同山脉驻波形成的层层堆叠、金属光泽的透镜状云层，这些方法稳固、对称、可重复，像气流中的驻波一样在特定条件下始终保持形态。",
        "en": "Like the layered, metallic-sheen lenticular clouds formed by mountain standing waves, these methods are stable, symmetric, and repeatable, maintaining their form under specific conditions like standing waves in airflow."
    },
    "circumhorizontal_desc": {
        "zh": "如同冰晶精确折射产生的水平彩带，这些方法要求极高纯度的条件对齐（如太阳高度角>58°的精确几何），一旦满足便展现出无与伦比的光谱纯度。",
        "en": "Like the horizontal rainbow bands produced by precise ice crystal refraction, these methods demand ultra-high-purity condition alignment (like the precise geometry of solar altitude >58 degrees), revealing unmatched spectral purity once met."
    },
    "fallstreak_desc": {
        "zh": "如同飞机穿过过冷云层触发冰晶相变形成的几何洞，这些方法由人为干预触发连锁反应，一个初始扰动便在整个研究领域传播开来。",
        "en": "Like the geometric holes formed when aircraft trigger ice crystal phase transitions in supercooled cloud layers, these methods are triggered by human intervention causing chain reactions, a single initial perturbation spreading across the research field."
    },
    "brocken_desc": {
        "zh": "如同观测者自身投影在云雾上并被荣耀光环环绕的布罗肯幽灵，这些方法高度依赖观测者视角，研究者的位置和角度决定了所见'幽灵'的形态与光环大小。",
        "en": "Like the Brocken Spectre where the observer's own shadow is projected onto mist and surrounded by a glory halo, these methods are highly observer-dependent, the researcher's position and angle determining the shape and halo size of the 'spectre' seen."
    },
    "moonbow_desc": {
        "zh": "如同月光折射形成的淡彩虹弧，这些方法信号微弱、信噪比低，需要极暗的背景（低竞争领域）和长时间曝光（持久观测）才能被辨识。",
        "en": "Like the faint rainbow arc formed by moonlight refraction, these methods have weak signals and low signal-to-noise ratios, requiring extremely dark backgrounds (low-competition fields) and long exposures (persistent observation) to be discerned."
    },

    # AI analysis window
    "ai_analysis": {"zh": "AI 大气光学隐喻分析", "en": "AI Atmospheric Optics Metaphor Analysis"},
    "ai_generating": {"zh": "AI 正在生成隐喻分析...", "en": "AI generating metaphor analysis..."},

    # 3D
    "threejs_title": {"zh": "3D 大气光学可视化", "en": "3D Atmospheric Optics Visualization"},
    "threejs_fallback": {"zh": "3D 可视化已降级为 2D 图表展示", "en": "3D visualization degraded to 2D chart display"},

    # Logs
    "log_title": {"zh": "运行日志", "en": "Run Log"},
    "log_clear": {"zh": "清空日志", "en": "Clear Log"},

    # Node label toggle
    "node_label_toggle": {"zh": "显示节点名称", "en": "Show Node Labels"},
    "node_label_help": {"zh": "全局开关：显示/隐藏图表中的节点名称。开启后优先显示大节点和重要节点的名称，鼠标悬停始终可查看。",
                         "en": "Global toggle: show/hide node labels in charts. When enabled, prioritizes showing labels for large/important nodes. Hover always reveals labels."},

    # Home page
    "home_welcome_title": {"zh": "欢迎使用大气光学学术分析器", "en": "Welcome to AOAA"},
    "home_quick_start": {"zh": "快速开始", "en": "Quick Start"},
    "home_step1": {"zh": "上传文献 → 在左侧边栏上传 TXT/PDF/CSV/WOS 等格式的学术文献", "en": "Upload Files → Upload academic literature in TXT/PDF/CSV/WOS etc. in the sidebar"},
    "home_step2": {"zh": "点击加载 → 点击「开始加载」按钮，系统自动解析并分析", "en": "Start Loading → Click \"Start Loading\" for automatic parsing and analysis"},
    "home_step3": {"zh": "浏览页面 → 在左侧导航选择不同的大气现象分析页面", "en": "Browse Pages → Navigate to different atmospheric phenomenon pages"},
    "home_step4": {"zh": "AI 分析（可选）→ 配置模型后端获取 AI 隐喻解读", "en": "AI Analysis (optional) → Configure a model backend for AI metaphor interpretations"},
    "home_phenomena_title": {"zh": "9 大大气光学现象", "en": "9 Atmospheric Optical Phenomena"},
    "home_ai_title": {"zh": "AI 后端支持", "en": "AI Backend Support"},
    "home_ai_llama": {"zh": "llama-cpp-python — 本地 GGUF 模型，支持 GPU 加速", "en": "llama-cpp-python — Local GGUF models with GPU acceleration"},
    "home_ai_ollama": {"zh": "Ollama — 本地模型管理，支持拉取/加载/多模型 Ensemble", "en": "Ollama — Local model management with pull/load/ensemble"},
    "home_ai_openai": {"zh": "OpenAI 兼容 API — 任何兼容 API（含国产大模型）", "en": "OpenAI Compatible API — Any compatible API"},
    "home_ai_note": {"zh": "无模型时，统计分析与可视化仍完整可用。", "en": "Statistics and visualizations work fully without any AI model."},
    "home_prompt_title": {"zh": "自定义提示词", "en": "Custom Prompts"},
    "home_prompt_desc": {"zh": "在左侧「自定义提示词」区域可以设置系统提示词、分析模板和提示词强度。", "en": "In the sidebar \"Custom Prompts\" section you can set system prompts, analysis templates and prompt strength."},
    "home_data_loaded": {"zh": "数据已加载：{doc_n} 篇文献 | {kw_n} 个关键词 | {edge_n} 条共现关系", "en": "Data loaded: {doc_n} documents | {kw_n} keywords | {edge_n} co-occurrence edges"},
    "home_nav_hint": {"zh": "点击左侧导航栏选择分析页面", "en": "Use the sidebar navigation to explore analysis pages"},

    # Overview
    "overview_basic_charts": {"zh": "基础统计图表", "en": "Basic Statistical Charts"},
    "overview_advanced_center": {"zh": "高级可视化分析中心", "en": "Advanced Visualization Center"},
    "overview_polar_series": {"zh": "极坐标与玫瑰系列", "en": "Polar & Rose Series"},
    "overview_stat_series": {"zh": "统计分析系列", "en": "Statistical Analysis Series"},
    "overview_network_series": {"zh": "网络与流向系列", "en": "Network & Flow Series"},
    "overview_multidim_series": {"zh": "多维分析系列", "en": "Multi-Dimensional Series"},
    "overview_hierarchy_series": {"zh": "层级与领地系列", "en": "Hierarchy & Territory Series"},
    "overview_dist_series": {"zh": "分布与堆积系列", "en": "Distribution & Stacking Series"},
    "overview_compare_series": {"zh": "高级比较系列", "en": "Advanced Comparison Series"},
    "overview_3d_series": {"zh": "3D与词云系列", "en": "3D & Word Cloud Series"},
    "overview_generate_btn": {"zh": "生成全局大气层分析", "en": "Generate Global Atmosphere Analysis"},
    "overview_click_to_gen": {"zh": "点击按钮生成分析", "en": "Click button to generate"},
    "overview_upload_hint": {"zh": "请在左侧上传文献文件并点击'开始加载'", "en": "Upload files in the sidebar and click 'Start Loading'"},

    # Phenomenon base
    "phenom_advanced_viz": {"zh": "高级可视化分析", "en": "Advanced Visualization Suite"},
    "phenom_deep_charts": {"zh": "深度分析图表", "en": "Deep Analysis Charts"},
    "phenom_3d_viz": {"zh": "3D 可视化", "en": "3D Visualization"},
    "phenom_matched_keywords": {"zh": "匹配关键词", "en": "Matched Keywords"},
    "phenom_match_dist": {"zh": "匹配分布", "en": "Match Distribution"},
    "phenom_no_match": {"zh": "未找到匹配关键词", "en": "No matching keywords found"},
    "phenom_generate_btn": {"zh": "生成 AI 隐喻分析", "en": "Generate AI Metaphor Analysis"},
    "phenom_default_template": {"zh": "默认模板", "en": "Default Template"},
    "phenom_custom_template": {"zh": "自定义模板", "en": "Custom Template"},
    "phenom_stat_fallback": {"zh": "当前数据中未找到足够的关键词。请上传更多文献后重试。", "en": "Not enough keywords in current data. Upload more files and retry."},

    # Parser messages
    "parse_parsing_files": {"zh": "解析文件...", "en": "Parsing files..."},
    "parse_running_nlp": {"zh": "运行 NLP 分析...", "en": "Running NLP analysis..."},
    "parse_building_graph": {"zh": "构建图谱...", "en": "Building graph..."},
    "parse_files_selected": {"zh": "个文件已选择", "en": "files selected"},
    "parse_loaded_status": {"zh": "已加载", "en": "Loaded"},

    # Charts
    "chart_insufficient": {"zh": "数据不足，无法生成此图表", "en": "Insufficient data for this chart"},
    "chart_render_error": {"zh": "图表渲染错误", "en": "Chart render error"},

    # Exports
    "export_json": {"zh": "导出 JSON", "en": "Export JSON"},
    "export_txt": {"zh": "导出 TXT", "en": "Export TXT"},
    "export_report_title": {"zh": "AOAA - 大气光学学术分析报告", "en": "AOAA - Atmospheric Optics Academic Analysis Report"},

    # Prompt section
    "prompt_section_title": {"zh": "自定义提示词", "en": "Custom Prompts"},
    "prompt_system_label": {"zh": "系统提示词 (System Prompt)", "en": "System Prompt"},
    "prompt_system_help": {"zh": "自定义 AI 的角色设定和行为约束。留空则使用默认大气光学隐喻专家。", "en": "Customize AI role and behavior. Leave empty for default atmospheric optics metaphor expert."},
    "prompt_template_label": {"zh": "分析提示词模板", "en": "Analysis Prompt Template"},
    "prompt_template_help": {"zh": "用于生成隐喻分析的模板。可用变量: {phenomenon}, {description}, {keywords}, {doc_count}。", "en": "Template for metaphor analysis. Variables: {phenomenon}, {description}, {keywords}, {doc_count}."},
    "prompt_strength_label": {"zh": "提示词强度", "en": "Prompt Strength"},
    "prompt_strength_light": {"zh": "轻量", "en": "Light"},
    "prompt_strength_standard": {"zh": "标准", "en": "Standard"},
    "prompt_strength_strong": {"zh": "强劲", "en": "Strong"},
    "prompt_strength_maximum": {"zh": "极限", "en": "Maximum"},
    "prompt_sys_placeholder": {"zh": "例: 你是一个专注于大气光学过程的学术分析专家...", "en": "e.g.: You are an expert in atmospheric optics academic analysis..."},
    "prompt_tpl_placeholder": {"zh": "请用大气光学隐喻分析 {phenomenon} 现象对应的学术方法: {keywords}", "en": "Analyze {phenomenon} phenomenon's academic methods using atmospheric optics metaphors: {keywords}"},
}


def get_lang() -> str:
    """Get current language from session state."""
    if "lang" not in st.session_state:
        st.session_state.lang = "zh"
    return st.session_state.lang


def set_lang(lang: str):
    """Set language."""
    st.session_state.lang = lang


def toggle_lang():
    """Toggle between zh and en."""
    current = get_lang()
    set_lang("en" if current == "zh" else "zh")


def t(key: str, **kwargs) -> str:
    """Translate key to current language. Supports format kwargs."""
    lang = get_lang()
    entry = _DICT.get(key)
    if entry is None:
        return f"[{key}]"
    text = entry.get(lang, entry.get("en", f"[{key}]"))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text
