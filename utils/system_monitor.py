# -*- coding: utf-8 -*-
"""System monitoring: GPU (nvidia-smi), CPU, memory via psutil."""

import subprocess
import re
from typing import Dict, Any, List, Optional
from utils.logger import log_info, log_warn


def get_gpu_info() -> List[Dict[str, Any]]:
    """Parse nvidia-smi for GPU information."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=index,name,memory.used,memory.total,utilization.gpu,temperature.gpu",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return []

        gpus = []
        for line in result.stdout.strip().split("\n"):
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 6:
                gpus.append({
                    "index": int(parts[0]),
                    "name": parts[1],
                    "memory_used_mb": int(parts[2]),
                    "memory_total_mb": int(parts[3]),
                    "utilization_pct": int(parts[4]),
                    "temperature_c": int(parts[5])
                })
        return gpus
    except FileNotFoundError:
        return []
    except Exception as e:
        log_warn(f"nvidia-smi failed: {e}")
        return []


def get_system_info() -> Dict[str, Any]:
    """Get CPU and memory info via psutil."""
    info = {"cpu_percent": 0, "memory_used_mb": 0, "memory_total_mb": 0, "memory_percent": 0}
    try:
        import psutil
        info["cpu_percent"] = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        info["memory_used_mb"] = int(mem.used / 1024 / 1024)
        info["memory_total_mb"] = int(mem.total / 1024 / 1024)
        info["memory_percent"] = mem.percent
    except ImportError:
        log_warn("psutil not available")
    except Exception as e:
        log_warn(f"psutil failed: {e}")
    return info


def get_full_status() -> Dict[str, Any]:
    """Get combined GPU + system status."""
    gpus = get_gpu_info()
    sys_info = get_system_info()
    return {
        "gpus": gpus,
        "gpu_available": len(gpus) > 0,
        "gpu_count": len(gpus),
        "system": sys_info
    }


def format_status_text(status: Dict[str, Any], lang: str = "zh") -> str:
    """Format status for display."""
    lines = []
    sys_info = status.get("system", {})

    if lang == "zh":
        lines.append(f"CPU: {sys_info.get('cpu_percent', 0)}%")
        lines.append(f"内存: {sys_info.get('memory_used_mb', 0)}MB / {sys_info.get('memory_total_mb', 0)}MB ({sys_info.get('memory_percent', 0)}%)")
    else:
        lines.append(f"CPU: {sys_info.get('cpu_percent', 0)}%")
        lines.append(f"Memory: {sys_info.get('memory_used_mb', 0)}MB / {sys_info.get('memory_total_mb', 0)}MB ({sys_info.get('memory_percent', 0)}%)")

    gpus = status.get("gpus", [])
    if gpus:
        for gpu in gpus:
            if lang == "zh":
                lines.append(f"GPU {gpu['index']}: {gpu['name']} | 显存: {gpu['memory_used_mb']}MB / {gpu['memory_total_mb']}MB | 利用率: {gpu['utilization_pct']}% | 温度: {gpu['temperature_c']}°C")
            else:
                lines.append(f"GPU {gpu['index']}: {gpu['name']} | VRAM: {gpu['memory_used_mb']}MB / {gpu['memory_total_mb']}MB | Util: {gpu['utilization_pct']}% | Temp: {gpu['temperature_c']}°C")
    else:
        lines.append("GPU: N/A" if lang == "en" else "GPU: 无")

    return "\n".join(lines)
