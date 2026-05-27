# -*- coding: utf-8 -*-
"""OpenAI-compatible API backend with retry and streaming support."""

import time
from typing import Dict, Any, Optional
from utils.ai_backends.base import AIBackend
from utils.logger import log_info, log_warn, log_error


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

    def load(self, base_url: str = "", api_key: str = "", model: str = "",
             temperature: float = 0.7, timeout: int = 60, stream: bool = False, **kwargs) -> bool:
        """Configure the OpenAI-compatible backend."""
        if not base_url or not model:
            log_error("OpenAI compat: base_url and model are required")
            self.is_loaded = False
            return False

        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model_name = model
        self.temperature = temperature
        self.timeout = timeout
        self.stream = stream
        self.context_length = 32768  # assumed
        self.quant_level = "N/A"

        check = self.health_check()
        self.is_loaded = check["healthy"]
        return self.is_loaded

    def _make_request(self, messages: list, max_tokens: int = 1024, temperature: float = None) -> Optional[str]:
        """Make API request with exponential backoff retry."""
        import requests

        if temperature is None:
            temperature = self.temperature

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        data = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False  # Always non-stream for reliability
        }

        url = f"{self.base_url}/chat/completions"
        delay = 1

        for attempt in range(self.max_retries + 1):
            try:
                resp = requests.post(url, json=data, headers=headers, timeout=self.timeout)
                resp.raise_for_status()
                result = resp.json()
                choices = result.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "")
                return ""
            except Exception as e:
                if attempt < self.max_retries:
                    log_warn(f"OpenAI compat attempt {attempt+1} failed: {e}, retrying in {delay}s")
                    time.sleep(delay)
                    delay = min(delay * 2, 8)
                else:
                    log_error(f"OpenAI compat all retries failed", e)
                    return None
        return None

    def generate(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.7) -> str:
        messages = [{"role": "user", "content": prompt}]
        result = self._make_request(messages, max_tokens, temperature)
        if result is not None:
            return result.strip()
        return "[OpenAI compat: generation failed]"

    def health_check(self) -> Dict[str, Any]:
        if not self.base_url:
            return {"healthy": False, "message": "No base_url configured"}
        try:
            import requests
            # Try models endpoint
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            resp = requests.get(f"{self.base_url}/models", headers=headers, timeout=5)
            if resp.status_code < 500:
                return {"healthy": True, "message": f"API reachable at {self.base_url}"}
        except Exception as e:
            pass

        # Try a simple generation
        try:
            result = self._make_request(
                [{"role": "user", "content": "Hi"}],
                max_tokens=5, temperature=0.1
            )
            if result:
                return {"healthy": True, "message": "OK"}
        except Exception:
            pass
        return {"healthy": False, "message": f"Cannot reach {self.base_url}"}
