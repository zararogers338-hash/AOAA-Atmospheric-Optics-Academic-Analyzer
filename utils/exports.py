# -*- coding: utf-8 -*-
"""Export module: JSON, TXT, SVG, ZIP results."""

import io
import json
import zipfile
from typing import Dict, Any, Optional
from utils.logger import log_info, get_logs
from utils.i18n import get_lang


def export_json(data: Dict[str, Any]) -> str:
    """Export analysis data as JSON string."""
    return json.dumps(data, ensure_ascii=False, indent=2, default=str)


def export_txt(data: Dict[str, Any]) -> str:
    """Export analysis data as human-readable TXT."""
    lang = get_lang()
    lines = []

    if lang == "zh":
        lines.append("=" * 60)
        lines.append("AOAA - 大气光学学术分析报告")
        lines.append("=" * 60)
    else:
        lines.append("=" * 60)
        lines.append("AOAA - Atmospheric Optics Academic Analysis Report")
        lines.append("=" * 60)

    # Document summary
    doc_count = data.get("doc_count", 0)
    valid = data.get("valid_text_count", 0)
    lines.append(f"\n{'文献总数' if lang == 'zh' else 'Total Documents'}: {doc_count}")
    lines.append(f"{'有效文本' if lang == 'zh' else 'Valid Text'}: {valid}")

    # TF-IDF top keywords
    tfidf = data.get("tfidf", {})
    global_top = tfidf.get("global_top", [])
    if global_top:
        lines.append(f"\n--- {'全局关键词 (TF-IDF)' if lang == 'zh' else 'Global Keywords (TF-IDF)'} ---")
        for kw, score in global_top[:20]:
            lines.append(f"  {kw}: {score:.4f}")

    # Year trend
    trend = data.get("year_trend", {})
    years = trend.get("years", [])
    counts = trend.get("counts", [])
    if years:
        lines.append(f"\n--- {'年份趋势' if lang == 'zh' else 'Year Trend'} ---")
        for y, c in zip(years, counts):
            lines.append(f"  {y}: {c}")

    # Citation stats
    cit = data.get("citation_stats", {})
    if cit.get("available"):
        lines.append(f"\n--- {'引用统计' if lang == 'zh' else 'Citation Stats'} ---")
        lines.append(f"  {'均值' if lang == 'zh' else 'Mean'}: {cit.get('mean', 0):.1f}")
        lines.append(f"  {'中位数' if lang == 'zh' else 'Median'}: {cit.get('median', 0):.1f}")
        lines.append(f"  {'最大' if lang == 'zh' else 'Max'}: {cit.get('max', 0)}")

    # Co-occurrence top edges
    cooc = data.get("cooccurrence", {})
    edges = cooc.get("edges", [])
    if edges:
        lines.append(f"\n--- {'共现关系 (Top 20)' if lang == 'zh' else 'Co-occurrence (Top 20)'} ---")
        for e in edges[:20]:
            lines.append(f"  {e['source']} <-> {e['target']}: {e['weight']}")

    return "\n".join(lines)


def export_svg_chart(fig) -> Optional[str]:
    """Export matplotlib figure as SVG string."""
    try:
        buf = io.StringIO()
        fig.savefig(buf, format="svg", bbox_inches="tight")
        buf.seek(0)
        return buf.getvalue()
    except Exception as e:
        log_info(f"SVG export failed: {e}")
        return None


def export_results_zip(data: Dict[str, Any], logs: str = None) -> bytes:
    """Export results as ZIP containing JSON + TXT + logs."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        # JSON data
        json_str = export_json(data)
        zf.writestr("analysis_results.json", json_str)

        # TXT report
        txt_str = export_txt(data)
        zf.writestr("analysis_report.txt", txt_str)

        # Logs
        if logs is None:
            logs = get_logs()
        zf.writestr("run_log.txt", logs)

    buf.seek(0)
    return buf.getvalue()
