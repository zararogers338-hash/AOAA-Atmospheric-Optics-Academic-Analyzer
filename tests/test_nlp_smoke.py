# -*- coding: utf-8 -*-
"""Smoke tests for NLP module."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock streamlit session_state for testing
import types
mock_st = types.ModuleType("streamlit")
mock_st.session_state = {"log_entries": [], "lang": "en"}
sys.modules["streamlit"] = mock_st


def test_tfidf():
    from utils.nlp import compute_tfidf
    texts = [
        "machine learning deep neural network training optimization",
        "natural language processing transformer attention mechanism",
        "computer vision convolutional neural network image recognition",
        "reinforcement learning policy gradient reward shaping"
    ]
    result = compute_tfidf(texts, top_k=5)
    assert len(result["global_top"]) > 0
    assert result["matrix"] is not None
    print(f"PASS: TF-IDF - {len(result['global_top'])} global keywords")


def test_cooccurrence():
    from utils.nlp import compute_cooccurrence
    texts = [
        "machine learning deep neural network",
        "deep learning neural network training",
        "machine learning model evaluation metrics",
    ]
    result = compute_cooccurrence(texts, top_k=10)
    assert len(result["keywords"]) > 0
    print(f"PASS: Co-occurrence - {len(result['keywords'])} keywords, {len(result['edges'])} edges")


def test_year_trend():
    from utils.nlp import compute_year_trend
    docs = [
        {"text": "Published in 2020 about AI", "metadata": {"year": "2020"}},
        {"text": "Published in 2021 about ML", "metadata": {"year": "2021"}},
        {"text": "Published in 2020 again", "metadata": {"year": "2020"}},
    ]
    result = compute_year_trend(docs)
    assert 2020 in result["years"]
    assert 2021 in result["years"]
    print(f"PASS: Year trend - {len(result['years'])} years")


def test_empty():
    from utils.nlp import compute_tfidf, compute_cooccurrence
    r1 = compute_tfidf([], top_k=5)
    r2 = compute_cooccurrence([], top_k=5)
    assert r1["global_top"] == []
    assert r2["keywords"] == []
    print("PASS: Empty input handled")


if __name__ == "__main__":
    test_tfidf()
    test_cooccurrence()
    test_year_trend()
    test_empty()
    print("\nAll NLP smoke tests passed!")
