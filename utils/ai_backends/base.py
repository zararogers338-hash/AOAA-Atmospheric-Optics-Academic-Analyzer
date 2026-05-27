# -*- coding: utf-8 -*-
"""Base class for all AI backends."""

import time
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from utils.logger import log_info


class AIBackend(ABC):
    """Abstract base class for AI inference backends."""

    def __init__(self):
        self.name: str = "base"
        self.model_name: str = "unknown"
        self.context_length: int = 0
        self.quant_level: str = "unknown"
        self.last_latency: float = 0.0
        self.last_tokens_per_sec: float = 0.0
        self.is_loaded: bool = False

    @abstractmethod
    def load(self, **kwargs) -> bool:
        """Load the model. Returns True on success."""
        pass

    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.7) -> str:
        """Generate text from prompt."""
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Check backend health. Returns {"healthy": bool, "message": str}."""
        pass

    def timed_generate(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.7) -> str:
        """Generate with timing metrics."""
        start = time.time()
        result = self.generate(prompt, max_tokens, temperature)
        elapsed = time.time() - start
        self.last_latency = round(elapsed, 3)
        char_count = len(result)
        self.last_tokens_per_sec = round(char_count / max(elapsed, 0.001) * 0.75, 1)  # approx
        log_info(f"[{self.name}] Generated {char_count} chars in {elapsed:.2f}s (~{self.last_tokens_per_sec} tok/s approx)")
        return result

    def get_status(self) -> Dict[str, Any]:
        """Get current status for the control panel."""
        return {
            "backend": self.name,
            "model": self.model_name,
            "context_length": self.context_length,
            "quant_level": self.quant_level,
            "latency_sec": self.last_latency,
            "tokens_per_sec_approx": self.last_tokens_per_sec,
            "loaded": self.is_loaded,
        }
