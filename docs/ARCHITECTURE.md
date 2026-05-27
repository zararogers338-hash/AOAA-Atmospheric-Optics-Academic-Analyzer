# Architecture / 架构

AOAA is a multi-page Streamlit application.

AOAA 是一个多页面 Streamlit 应用。

## Main layers / 主要层级

```text
app.py
  ↓
pages/*.py
  ↓
utils/shared_ui.py
  ↓
utils/file_parser.py → utils/nlp.py → utils/graph.py → utils/charts.py
  ↓
optional AI backends / 可选 AI 后端
```

## Important modules / 重要模块

- `app.py`: home page and entry point
- `pages/`: atmospheric phenomenon pages
- `utils/file_parser.py`: multi-format parser
- `utils/nlp.py`: TF-IDF, co-occurrence, trend analysis
- `utils/graph.py`: NetworkX graph analysis and atmosphere classification
- `utils/charts.py`: Plotly / matplotlib visualizations
- `utils/shared_ui.py`: common sidebar, upload workflow, model panel
- `utils/system_monitor.py`: CPU/RAM/GPU status observation
- `utils/ai_backends/`: Ollama, OpenAI-compatible, llama.cpp / GGUF, ensemble logic
