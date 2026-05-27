# AOAA - Atmospheric Optics Academic Analyzer

**AOAA / Academic Atmospheric Optics Analyzer** is an open-source Streamlit workbench that analyzes academic literature through the metaphor of atmospheric optics. It turns papers, reports, bibliographic records, and research texts into keyword statistics, co-occurrence networks, trend charts, 3D visualizations, and AI-assisted interpretations.

**AOAA / 学术大气光学分析器** 是一个开源的 Streamlit 工作台，它用“大气光学现象”的隐喻来分析学术文献。它可以把论文、报告、文献记录和研究文本转化为关键词统计、共现网络、趋势图表、3D 可视化和 AI 辅助解释。

> AOAA does **not** use biological, ecological, species, predator, extinction, or carbon-sink metaphors. Its conceptual language is intentionally restricted to atmospheric optics and meteorological / optical processes.
>
> AOAA **不使用** 生物学、生态学、物种、捕食者、灭绝或碳汇等隐喻。它的概念语言被刻意限制在大气光学、气象过程和光学过程之内。

---

## What is AOAA? / AOAA 是什么？

AOAA is a cross-disciplinary academic analysis tool. Instead of treating literature analysis as a plain table of titles and citations, it maps research patterns onto atmospheric optical phenomena:

AOAA 是一个跨学科的学术分析工具。它不是把文献分析仅仅做成标题和引用量表格，而是把研究模式映射到大气光学现象上：

| Phenomenon | Academic meaning | 中文含义 |
|---|---|---|
| Aurora | high-impact breakthrough methods | 极光：高影响力突破方法 |
| Noctilucent Clouds | far-horizon frontier methods | 夜光云：远期前沿方法 |
| Nacreous Clouds | rare precision methods | 珠母云：珍稀精密方法 |
| Asperitas | turbulent or controversial methods | Asperitas：剧烈扰动/争议方法 |
| Lenticular Clouds | stable symmetric methods | 透镜云：稳定对称方法 |
| Circumhorizontal Arc | ultra-pure precision methods | 火彩虹：高纯度精准方法 |
| Fallstreak Hole | human-triggered cascade methods | 陨落孔：人为触发连锁方法 |
| Brocken Spectre | observer-centric methods | 布罗肯幽灵：观测者中心方法 |
| Moonbow | low-light / weak-signal methods | 月虹：低亮度、弱信号方法 |

The result is a research observation cockpit: users can upload documents, compute statistical signals, explore keyword networks, compare atmospheric-metaphor categories, and optionally ask local or API-based AI models to explain the patterns.

它最终形成的是一个“研究观测舱”：用户可以上传文档、计算统计信号、探索关键词网络、比较不同大气隐喻类别，并可选择让本地或 API AI 模型解释这些结构。

---

## Core Features / 核心功能

- Multi-page Streamlit interface
- Chinese / English UI toggle
- 18+ file format parsing: TXT, MD, PDF, DOCX, CSV, XLSX, JSON, JSONL, HTML, XML, YAML, WOS, RIS, BibTeX and more
- TF-IDF keyword extraction
- Keyword co-occurrence analysis
- Research trend and citation-style statistics
- NetworkX-based graph analysis
- Atmospheric-zone classification: high pressure, low pressure, fronts, jet streams
- 9 atmospheric-optics analysis pages
- Overview dashboard with advanced visualization
- Plotly / matplotlib / word-cloud visualizations
- Optional AI interpretation
- Optional Ollama, llama.cpp / GGUF, and OpenAI-compatible backends
- Optional ensemble or hybrid backend mode
- Export to JSON, TXT, SVG, and ZIP
- Real-time system monitoring panel

---

## Hardware and System Observation / 硬件与系统观测

AOAA includes a lightweight system observation panel. It can show CPU usage, memory usage, GPU availability, GPU model, VRAM usage, GPU utilization, and GPU temperature when `nvidia-smi` is available.

AOAA 内置轻量级系统观测面板。在存在 `nvidia-smi` 的环境中，它可以显示 CPU 占用、内存占用、GPU 是否可用、GPU 型号、显存占用、GPU 利用率和 GPU 温度。

This is useful because users can immediately see whether the computer is actually working, whether GPU acceleration is being used, whether a task has fallen back to CPU, and whether the machine is under heavy load.

这个功能很重要，因为用户可以直接看到电脑到底有没有在干活、GPU 加速有没有真正跑起来、任务是不是掉回 CPU，以及机器是否正在处于高负载状态。

---

## Installation / 安装

Recommended Python version: **Python 3.10 or 3.11**.

推荐 Python 版本：**Python 3.10 或 3.11**。

```bash
git clone https://github.com/zararogers338-hash/AOAA-Atmospheric-Optics-Academic-Analyzer.git
cd AOAA-Atmospheric-Optics-Academic-Analyzer
python -m venv .venv
```

Windows:

```bat
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Linux / macOS:

```bash
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Windows users can also try:

```bat
run.bat
```

---

## Optional AI Backends / 可选 AI 后端

AOAA works without AI. Statistical analysis and visualizations remain available even when no model backend is configured.

AOAA 不依赖 AI 后端也能运行。即使没有配置模型，统计分析和可视化功能仍然可用。

Optional backends:

1. **llama-cpp-python / GGUF** for local model inference
2. **Ollama** for local model management and inference
3. **OpenAI-compatible API** for external or self-hosted API models
4. **Ensemble / Hybrid** mode for multi-backend interpretation

---

## Basic Workflow / 基本工作流

```text
Academic files / 学术文件
        ↓
Multi-format parser / 多格式解析
        ↓
TF-IDF + co-occurrence + trend analysis
关键词、共现和趋势分析
        ↓
Atmospheric-optics classification
大气光学现象分类
        ↓
Charts, networks, dashboards
图表、网络和仪表盘
        ↓
Optional AI interpretation / 可选 AI 解释
        ↓
JSON / TXT / SVG / ZIP export
结构化导出
```

---

## Project Status / 项目状态

This is an open-source preview release. Some modules are experimental and should be treated as research prototypes.

这是一个开源预览版本。部分模块仍具有实验性质，应当被视为研究原型。

AOAA is suitable for academic exploration, research-method analysis, literature review assistance, teaching demos, and interdisciplinary visualization experiments.

AOAA 适用于学术探索、研究方法分析、文献综述辅助、教学演示和跨学科可视化实验。

---

## Important Notice / 重要说明

AOAA is not an academic evaluation authority, not a citation ranking system, and not a final judgment tool.

AOAA 不是学术评价权威，不是引用排名系统，也不是最终裁决工具。

Its atmospheric-optics metaphors are designed to help users observe patterns, not to replace domain expertise, peer review, or careful scholarly interpretation.

它的大气光学隐喻是为了帮助用户观察模式，而不是取代领域专家判断、同行评议或严谨的学术解释。

---

## License / 许可证

MIT License.
