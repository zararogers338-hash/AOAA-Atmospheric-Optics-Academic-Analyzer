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
