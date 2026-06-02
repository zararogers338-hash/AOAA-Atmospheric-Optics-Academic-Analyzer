# -*- coding: utf-8 -*-
"""Tests for OpenAI-compatible backend with mocked requests."""

import pytest
import json
from unittest.mock import patch, MagicMock


@pytest.fixture
def backend():
    from utils.ai_backends.openai_compat_backend import OpenAICompatBackend
    return OpenAICompatBackend()


def test_load_requires_url_and_model(backend):
    ok = backend.load(base_url="", api_key="", model="")
    assert not ok
    assert not backend.is_loaded


def test_load_minimal(backend):
    with patch("utils.ai_backends.openai_compat_backend.OpenAICompatBackend.health_check",
               return_value={"healthy": True, "message": "OK"}):
        ok = backend.load(base_url="http://127.0.0.1:8010/v1", api_key="sk-test", model="test-model")
        assert ok
        assert backend.is_loaded
        assert backend.model_name == "test-model"
        assert backend.base_url == "http://127.0.0.1:8010/v1"


def test_load_strips_trailing_slash(backend):
    with patch("utils.ai_backends.openai_compat_backend.OpenAICompatBackend.health_check",
               return_value={"healthy": True, "message": "OK"}):
        ok = backend.load(base_url="http://127.0.0.1:8010/v1/", api_key="sk-test", model="m")
        assert ok
        assert backend.base_url == "http://127.0.0.1:8010/v1"


def test_health_check_no_url(backend):
    result = backend.health_check()
    assert not result["healthy"]
    assert "No base_url" in result["message"]


def test_health_check_models_success(backend):
    backend.base_url = "http://127.0.0.1:8010/v1"
    with patch("utils.ai_backends.openai_compat_backend._requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"data": []}
        result = backend.health_check()
        assert result["healthy"]


def test_health_check_models_404_fallback_to_chat(backend):
    backend.base_url = "http://127.0.0.1:8010/v1"
    with patch("utils.ai_backends.openai_compat_backend._requests.get") as mock_get:
        mock_get.return_value.status_code = 404
        with patch.object(backend, "_make_request", return_value="Hi"):
            result = backend.health_check()
            assert result["healthy"]
            assert "chat completion" in result["message"]


def test_health_check_connection_refused(backend):
    backend.base_url = "http://127.0.0.1:9999/v1"
    from utils.ai_backends.openai_compat_backend import _requests as req_mod
    with patch("utils.ai_backends.openai_compat_backend._requests.get",
               side_effect=req_mod.exceptions.ConnectionError()):
        with patch.object(backend, "_make_request",
                          side_effect=req_mod.exceptions.ConnectionError()):
            result = backend.health_check()
            assert not result["healthy"]


def test_make_request_success(backend):
    backend.base_url = "http://127.0.0.1:8010/v1"
    backend.model_name = "test-model"
    backend.api_key = "sk-test"

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"choices": [{"message": {"content": "Hello!"}}]}

    with patch("utils.ai_backends.openai_compat_backend._requests.post", return_value=mock_resp):
        result = backend._make_request([{"role": "user", "content": "Hi"}])
        assert result == "Hello!"


def test_make_request_http_error(backend):
    backend.base_url = "http://127.0.0.1:8010/v1"
    backend.model_name = "test-model"
    backend.api_key = "sk-test"
    backend.max_retries = 1

    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_resp.text = "Internal Server Error"

    with patch("utils.ai_backends.openai_compat_backend._requests.post", return_value=mock_resp):
        result = backend._make_request([{"role": "user", "content": "Hi"}])
        assert result is None


def test_generate_returns_result(backend):
    backend.base_url = "http://127.0.0.1:8010/v1"
    backend.model_name = "test-model"
    backend.api_key = "sk-test"

    with patch.object(backend, "_make_request", return_value="Hello world"):
        result = backend.generate("Hi")
        assert result == "Hello world"


def test_generate_returns_fallback_on_failure(backend):
    backend.base_url = "http://127.0.0.1:8010/v1"
    backend.model_name = "test-model"

    with patch.object(backend, "_make_request", return_value=None):
        result = backend.generate("Hi")
        assert "failed" in result


def test_redact_key():
    from utils.ai_backends.openai_compat_backend import _redact_key
    assert "..." in _redact_key("sk-abcdefghijklmnop")
    assert _redact_key("") == "***"
    assert _redact_key("ab") == "***"


def test_safe_error():
    from utils.ai_backends.openai_compat_backend import _safe_error
    e = RuntimeError("Auth failed: sk-1234abcd")
    msg = _safe_error(e, "sk-1234abcd")
    assert "sk-1234abcd" not in msg


def test_generate_stream(backend):
    backend.base_url = "http://127.0.0.1:8010/v1"
    backend.model_name = "test-model"
    backend.api_key = "sk-test"

    chunks = [
        b'data: {"choices":[{"delta":{"content":"Hello"}}]}\n\n',
        b'data: {"choices":[{"delta":{"content":" world"}}]}\n\n',
        b'data: [DONE]\n\n',
    ]

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.iter_lines.return_value = [c.decode() for c in chunks]

    with patch("utils.ai_backends.openai_compat_backend._requests.post", return_value=mock_resp):
        result = list(backend.generate_stream("Hi"))
        assert "Hello" in "".join(result)
        assert "world" in "".join(result)
