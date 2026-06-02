# -*- coding: utf-8 -*-
"""Shared test fixtures and mock setup for AOAA tests."""

import sys
import os
import types
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Mock streamlit before any imports ──
mock_st = types.ModuleType("streamlit")
mock_st.session_state = {
    "lang": "en",
    "log_entries": [],
    "config": {},
    "parsed_results": [],
    "analysis_data": {},
    "atmosphere_data": {},
    "sidebar_visible": True,
    "active_backend": None,
    "backend_type": "none",
    "ensemble_enabled": False,
    "hybrid_enabled": False,
    "files_loaded": False,
    "custom_prompt_template": "",
    "custom_system_prompt": "",
    "show_node_labels": True,
    "prompt_strength": "strong",
}
mock_st.errors = types.ModuleType("errors")
mock_st.errors.StreamlitAPIException = Exception
sys.modules["streamlit"] = mock_st


class FakeUploadedFile:
    """Simulates a Streamlit UploadedFile for parser tests."""
    def __init__(self, name, data):
        self.name = name
        self._data = data
    def read(self):
        return self._data
    def seek(self, n):
        pass


@pytest.fixture
def fake_file():
    """Factory fixture for FakeUploadedFile."""
    def _make(name, data):
        return FakeUploadedFile(name, data)
    return _make
