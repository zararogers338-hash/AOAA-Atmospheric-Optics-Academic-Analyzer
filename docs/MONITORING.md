# System Monitoring / 系统观测

AOAA includes a system observation panel implemented in `utils/system_monitor.py`.

AOAA 内置系统观测面板，由 `utils/system_monitor.py` 实现。

## What it observes / 它观测什么

- CPU usage via `psutil`
- RAM usage via `psutil`
- NVIDIA GPU availability via `nvidia-smi`
- GPU name
- VRAM used / total
- GPU utilization
- GPU temperature

## Why it matters / 为什么重要

When running local AI models, document parsing, visualization, or large NLP analysis, users need to know whether the machine is actually working. The panel helps users see whether GPU acceleration is active, whether the workload has fallen back to CPU, whether VRAM is nearly full, and whether the GPU temperature is rising.

在运行本地 AI 模型、文档解析、可视化或大型 NLP 分析时，用户需要知道电脑到底有没有在干活。观测面板可以帮助用户判断 GPU 加速是否真正启用、任务是否掉回 CPU、显存是否接近满载、GPU 温度是否升高。

This panel is informational. It does not replace hardware safety tools, manufacturer limits, or operating-system monitoring.

该面板仅用于信息观测，不能替代硬件安全工具、厂商限制或操作系统级监控。
