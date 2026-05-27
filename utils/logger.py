# -*- coding: utf-8 -*-
"""Unified in-memory logger for AOAA. Supports UI display and export."""

import traceback
from datetime import datetime

try:
    import streamlit as st  # type: ignore
except Exception:  # allows CLI tests before Streamlit is installed
    st = None

_FALLBACK_LOG_ENTRIES = []


def _get_log_store():
    if st is not None:
        try:
            if "log_entries" not in st.session_state:
                st.session_state.log_entries = []
            return st.session_state.log_entries
        except Exception:
            pass
    return _FALLBACK_LOG_ENTRIES


def log(level: str, msg: str, exc: Exception = None):
    """Add a log entry. level: INFO/WARN/ERROR."""
    ts = datetime.now().strftime("%H:%M:%S")
    entry = f"[{ts}][{level}] {msg}"
    if exc:
        tb = traceback.format_exception(type(exc), exc, exc.__traceback__)
        short_tb = "".join(tb[-3:]) if len(tb) > 3 else "".join(tb)
        entry += f"\n  Exception: {type(exc).__name__}: {exc}\n  {short_tb.strip()}"
    _get_log_store().append(entry)


def log_info(msg: str):
    log("INFO", msg)


def log_warn(msg: str):
    log("WARN", msg)


def log_error(msg: str, exc: Exception = None):
    log("ERROR", msg, exc)


def get_logs() -> str:
    return "\n".join(_get_log_store())


def get_log_list() -> list:
    return list(_get_log_store())


def clear_logs():
    store = _get_log_store()
    store.clear()


def export_logs() -> str:
    return get_logs()
