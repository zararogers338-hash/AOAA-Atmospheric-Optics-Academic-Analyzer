# -*- coding: utf-8 -*-
"""Ollama backend with enhanced stability: auto-reconnect, retry, timeout handling."""

import time
import json
from typing import Dict, Any, List, Optional
from utils.ai_backends.base import AIBackend
from utils.logger import log_info, log_warn, log_error


class OllamaBackend(AIBackend):
    def __init__(self):
        super().__init__()
        self.name = "ollama"
        self.base_url = "http://localhost:11434"
        self.loaded_models: List[str] = []
        self.max_models = 3
        self._session = None
        self._max_retries = 3
        self._retry_delay = 2
        self._connect_timeout = 10
        self._read_timeout = 120

    def _get_session(self):
        """Get or create requests session for connection pooling."""
        import requests
        from requests.adapters import HTTPAdapter
        if self._session is None:
            self._session = requests.Session()
            adapter = HTTPAdapter(max_retries=0, pool_connections=5, pool_maxsize=5)
            self._session.mount("http://", adapter)
            self._session.mount("https://", adapter)
        return self._session

    def _request(self, endpoint: str, method: str = "GET", data: dict = None,
                 timeout: int = None) -> Optional[dict]:
        """Make HTTP request with retry and reconnection."""
        import requests
        if timeout is None:
            timeout = self._read_timeout
        url = f"{self.base_url}{endpoint}"
        session = self._get_session()
        last_err = None

        for attempt in range(self._max_retries + 1):
            try:
                if method == "GET":
                    resp = session.get(url, timeout=(self._connect_timeout, timeout))
                else:
                    resp = session.post(url, json=data,
                                        timeout=(self._connect_timeout, timeout))
                resp.raise_for_status()
                return resp.json()
            except requests.exceptions.ConnectionError as e:
                last_err = e
                log_warn(f"Ollama connection lost (attempt {attempt+1}/{self._max_retries+1})")
                self._session = None  # Reset session
                if attempt < self._max_retries:
                    time.sleep(self._retry_delay * (attempt + 1))
            except requests.exceptions.Timeout as e:
                last_err = e
                log_warn(f"Ollama timeout (attempt {attempt+1})")
                if attempt < self._max_retries:
                    time.sleep(self._retry_delay)
            except requests.exceptions.HTTPError as e:
                last_err = e
                log_error(f"Ollama HTTP error: {e}")
                if hasattr(e, 'response') and e.response is not None and e.response.status_code < 500:
                    break
                if attempt < self._max_retries:
                    time.sleep(self._retry_delay)
            except Exception as e:
                last_err = e
                log_error(f"Ollama error: {e}")
                if attempt < self._max_retries:
                    time.sleep(self._retry_delay)

        log_error(f"Ollama {endpoint} failed after all retries", last_err)
        return None

    def _stream_request(self, endpoint: str, data: dict, timeout: int = 300):
        """Stream request for pulling models."""
        import requests
        url = f"{self.base_url}{endpoint}"
        for attempt in range(self._max_retries + 1):
            try:
                resp = requests.post(url, json=data, stream=True,
                                      timeout=(self._connect_timeout, timeout))
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if line:
                        try:
                            yield json.loads(line)
                        except json.JSONDecodeError:
                            continue
                return
            except Exception as e:
                log_warn(f"Ollama stream attempt {attempt+1} failed: {e}")
                if attempt < self._max_retries:
                    time.sleep(self._retry_delay * (attempt + 1))

    def list_models(self) -> List[str]:
        result = self._request("/api/tags", timeout=15)
        if result and "models" in result:
            models = [m.get("name", m.get("model", "")) for m in result["models"]]
            return [m for m in models if m]
        return []

    def pull_model(self, model_name: str, progress_callback=None) -> bool:
        log_info(f"Pulling: {model_name}")
        for chunk in self._stream_request("/api/pull", {"name": model_name, "stream": True}, timeout=600):
            status = chunk.get("status", "")
            if progress_callback:
                total = chunk.get("total", 0)
                completed = chunk.get("completed", 0)
                pct = completed / total if total > 0 else 0
                progress_callback(pct, status)
            if "error" in chunk:
                log_error(f"Pull error: {chunk['error']}")
                return False
        return True

    def load(self, model_name: str = "", base_url: str = "", **kwargs) -> bool:
        if base_url:
            self.base_url = base_url.rstrip("/")
        if not model_name:
            models = self.list_models()
            if models:
                model_name = models[0]
            else:
                log_error("No Ollama models available")
                self.is_loaded = False
                return False

        self.model_name = model_name
        if model_name not in self.loaded_models:
            if len(self.loaded_models) >= self.max_models:
                self.loaded_models.pop(0)
            self.loaded_models.append(model_name)

        # Warmup request
        log_info(f"Warming up: {model_name}")
        warmup = {"model": model_name, "prompt": "Hi", "stream": False,
                   "options": {"num_predict": 1}}
        result = self._request("/api/generate", method="POST", data=warmup, timeout=120)
        if result and "response" in result:
            self.is_loaded = True
            self.context_length = 32768
            self.quant_level = "varies"
            log_info(f"Ready: {model_name}")
            return True

        check = self.health_check()
        self.is_loaded = check["healthy"]
        return self.is_loaded

    def generate(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.7) -> str:
        if not self.model_name:
            return "[Ollama: no model selected]"

        data = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": max_tokens, "temperature": temperature}
        }

        # Custom system prompt from session
        try:
            import streamlit as st
            modelfile = st.session_state.get("ollama_modelfile", "")
            if modelfile:
                for line in modelfile.split("\n"):
                    l = line.strip()
                    if l.upper().startswith("SYSTEM"):
                        data["system"] = l[6:].strip()
                        break
        except Exception:
            pass

        result = self._request("/api/generate", method="POST", data=data)
        if result and "response" in result:
            text = result["response"].strip()
            if "eval_count" in result and "eval_duration" in result:
                ed = result["eval_duration"]
                if ed > 0:
                    self.last_tokens_per_sec = round(result["eval_count"] / (ed / 1e9), 1)
            if "total_duration" in result:
                self.last_latency = round(result["total_duration"] / 1e9, 3)
            return text

        # Final retry with fresh session
        log_warn("Retrying with fresh session...")
        self._session = None
        result = self._request("/api/generate", method="POST", data=data)
        if result and "response" in result:
            return result["response"].strip()
        return "[Ollama: generation failed]"

    def generate_multi(self, prompt: str, models: List[str] = None,
                       max_tokens: int = 1024, temperature: float = 0.7) -> List[Dict[str, str]]:
        if models is None:
            models = self.loaded_models[:self.max_models]
        results = []
        for m in models:
            data = {"model": m, "prompt": prompt, "stream": False,
                    "options": {"num_predict": max_tokens, "temperature": temperature}}
            resp = self._request("/api/generate", method="POST", data=data)
            text = resp.get("response", "[failed]") if resp else "[failed]"
            results.append({"model": m, "text": text.strip()})
        return results

    def health_check(self) -> Dict[str, Any]:
        import requests
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=(5, 10))
            if resp.status_code == 200:
                data = resp.json()
                n = len(data.get("models", []))
                names = [m.get("name", "?") for m in data.get("models", [])][:5]
                return {"healthy": True, "message": f"OK: {n} models ({', '.join(names)})"}
            return {"healthy": False, "message": f"HTTP {resp.status_code}"}
        except requests.exceptions.ConnectionError:
            return {"healthy": False, "message": f"Cannot connect to {self.base_url}"}
        except requests.exceptions.Timeout:
            return {"healthy": False, "message": f"Timeout at {self.base_url}"}
        except Exception as e:
            return {"healthy": False, "message": str(e)}
