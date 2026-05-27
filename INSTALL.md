# Installation / 安装说明

## Requirements / 环境要求

- Python 3.10 or 3.11 recommended
- Windows, Linux, or macOS
- Optional NVIDIA GPU for local GGUF acceleration
- Optional Ollama or OpenAI-compatible API for AI interpretation

## Install / 安装

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

Then open:

```text
http://localhost:8501
```

## Optional AI / 可选 AI

AOAA can run without any model. To enable AI interpretation, configure one of:

- Ollama
- llama-cpp-python with a GGUF model
- OpenAI-compatible API

Do not commit API keys or private model files to GitHub.
