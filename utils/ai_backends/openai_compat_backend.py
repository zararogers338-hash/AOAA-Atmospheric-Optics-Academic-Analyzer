# -*- coding: utf-8 -*-
"""OpenAI-compatible API backend with retry, streaming, and local server support."""

import time
import json as _json
import requests as _requests
from typing import Dict, Any, Optional, Generator
from utils.ai_backends.base import AIBackend
from utils.logger import log_info, log_warn, log_error


def _redact_key(key: str) -> str:
    """Return a redacted version of an API key for safe display."""
    if not key or len(key) < 8:
        return "***"
    return key[:4] + "..." + key[-4:]


def _safe_error(e: Exception, api_key: str = "") -> str:
    """Return an error message with the API key redacted."""
    msg = str(e)
    if api_key and api_key in msg:
        msg = msg.replace(api_key, _redact_key(api_key))
    return msg


class OpenAICompatBackend(AIBackend):
    def __init__(self):
        super().__init__()
        self.name = "openai_compat"
        self.base_url = ""
        self.api_key = ""
        self.temperature = 0.7
        self.timeout = 60
        self.max_retries = 4
        self.stream = False
        self.headers: Dict[str, str] = {}

    def load(self, base_url: str = "", api_key: str = "", model: str = "",
             temperature: float = 0.7, timeout: int = 60, stream: bool = False,
             extra_headers: Optional[Dict[str, str]] = None, **kwargs) -> bool:
        """Configure and verify the OpenAI-compatible backend.

        Supports local servers (e.g. http://127.0.0.1:8010/v1), remote APIs,
        and any OpenAI-compatible provider.
        """
        if not base_url or not model:
            log_error("OpenAI compat: base_url and model are required")
            self.is_loaded = False
            return False

        # Normalise base_url: strip trailing slash, ensure /v1 if missing and not already
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model_name = model
        self.temperature = temperature
        self.timeout = timeout
        self.stream = stream
        self.context_length = kwargs.get("context_length", 32768)
        self.quant_level = "N/A"

        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
        if extra_headers:
            self.headers.update(extra_headers)

        check = self.health_check()
        self.is_loaded = check["healthy"]
        if self.is_loaded:
            log_info(f"OpenAI compat connected: {_redact_key(api_key) if api_key else 'no-key'} @ {base_url}")
        else:
            log_warn(f"OpenAI compat health check failed: {check.get('message', 'unknown')}")
        return self.is_loaded

    def _make_request(self, messages: list, max_tokens: int = 1024,
                      temperature: Optional[float] = None) -> Optional[str]:
        """Make a non-streaming API request with exponential backoff."""
        if temperature is None:
            temperature = self.temperature

        payload = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False,
        }

        url = f"{self.base_url}/chat/completions"
        delay = 1.0

        for attempt in range(self.max_retries + 1):
            try:
                resp = _requests.post(url, json=payload, headers=self.headers,
                                      timeout=self.timeout)
                if resp.status_code >= 400:
                    err_text = resp.text[:300]
                    raise RuntimeError(f"HTTP {resp.status_code}: {err_text}")

                data = resp.json()
                choices = data.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "")
                return ""
            except _requests.exceptions.ConnectionError as e:
                log_warn(f"Connection refused at {self.base_url} (attempt {attempt+1})")
                if attempt < self.max_retries:
                    time.sleep(delay)
                    delay = min(delay * 2, 8)
                else:
                    log_error(f"All connection attempts failed for {self.base_url}")
                    return None
            except _requests.exceptions.Timeout:
                log_warn(f"Timeout at {self.base_url} (attempt {attempt+1})")
                if attempt < self.max_retries:
                    time.sleep(delay)
                    delay = min(delay * 2, 8)
                else:
                    log_error(f"All attempts timed out for {self.base_url}")
                    return None
            except Exception as e:
                if attempt < self.max_retries:
                    log_warn(f"OpenAI compat attempt {attempt+1} failed: {_safe_error(e, self.api_key)}, retrying in {delay}s")
                    time.sleep(delay)
                    delay = min(delay * 2, 8)
                else:
                    log_error(f"OpenAI compat all retries failed", e)
                    return None
        return None

    def generate(self, prompt: str, max_tokens: int = 1024,
                 temperature: float = 0.7) -> str:
        """Generate text from prompt (non-streaming)."""
        messages = [{"role": "user", "content": prompt}]
        result = self._make_request(messages, max_tokens, temperature)
        if result is not None:
            return result.strip()
        return "[OpenAI compat: generation failed — check connection and credentials]"

    def generate_stream(self, prompt: str, max_tokens: int = 1024,
                        temperature: float = 0.7) -> Generator[str, None, None]:
        """Generate text with streaming (yields chunks)."""
        if temperature is None:
            temperature = self.temperature

        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True,
        }

        url = f"{self.base_url}/chat/completions"
        try:
            resp = _requests.post(url, json=payload, headers=self.headers,
                                  timeout=self.timeout, stream=True)
            if resp.status_code >= 400:
                err_text = resp.text[:300]
                yield f"[Error: HTTP {resp.status_code} — {err_text}]"
                return

            for line in resp.iter_lines(decode_unicode=True):
                if not line or not line.startswith("data: "):
                    continue
                data_str = line[6:]
                if data_str.strip() == "[DONE]":
                    break
                try:
                    chunk = _json.loads(data_str)
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        yield content
                except Exception:
                    continue
        except _requests.exceptions.ConnectionError:
            yield "[Error: Could not connect to API server]"
        except Exception as e:
            yield f"[Error: {_safe_error(e, self.api_key)}]"

    def health_check(self) -> Dict[str, Any]:
        """Check backend health.

        Tries /models first, then falls back to a short chat completion test.
        """
        if not self.base_url:
            return {"healthy": False, "message": "No base_url configured"}

        # Strategy 1: /models endpoint
        try:
            resp = _requests.get(f"{self.base_url}/models", headers=self.headers, timeout=5)
            if resp.status_code == 200:
                return {"healthy": True, "message": f"API reachable at {self.base_url}"}
            # Some servers return 404 for /models but work fine for chat
            if resp.status_code == 404:
                log_info("OpenAI compat: /models returned 404, trying chat fallback")
        except _requests.exceptions.ConnectionError:
            log_info("OpenAI compat: /models connection refused, trying chat fallback")
        except Exception:
            pass

        # Strategy 2: Short chat completion test
        try:
            result = self._make_request(
                [{"role": "user", "content": "Hi"}],
                max_tokens=5, temperature=0.0
            )
            if result is not None:
                return {"healthy": True, "message": "OK (via chat completion)"}
        except Exception:
            pass

        return {"healthy": False, "message": f"Cannot reach {self.base_url} — check server is running"}
