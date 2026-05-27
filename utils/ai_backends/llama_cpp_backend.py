# -*- coding: utf-8 -*-
"""llama-cpp-python backend for GGUF models."""

import os
import re
from typing import Dict, Any, Optional
from utils.ai_backends.base import AIBackend
from utils.logger import log_info, log_warn, log_error


class LlamaCppBackend(AIBackend):
    def __init__(self):
        super().__init__()
        self.name = "llama_cpp"
        self.model = None
        self.n_ctx = 32768
        self.n_gpu_layers = -1

    def _detect_quant(self, path: str) -> str:
        """Detect quantization level from filename or metadata."""
        fname = os.path.basename(path).lower()
        patterns = ["q2_k", "q3_k_s", "q3_k_m", "q3_k_l", "q4_0", "q4_1",
                     "q4_k_s", "q4_k_m", "q5_0", "q5_1", "q5_k_s", "q5_k_m",
                     "q6_k", "q8_0", "f16", "f32"]
        for p in patterns:
            if p in fname:
                return p.upper()
        return "unknown"

    def load(self, model_path: str = "", n_ctx: int = 32768, n_gpu_layers: int = -1, **kwargs) -> bool:
        """Load a GGUF model."""
        try:
            from llama_cpp import Llama
        except ImportError:
            log_error("llama-cpp-python not installed. Install with: pip install llama-cpp-python")
            self.is_loaded = False
            return False

        if not model_path or not os.path.exists(model_path):
            log_error(f"Model path not found: {model_path}")
            self.is_loaded = False
            return False

        self.n_ctx = max(n_ctx, 32768)
        self.n_gpu_layers = n_gpu_layers

        # Try loading with GPU, fallback to CPU
        layers = n_gpu_layers
        while True:
            try:
                log_info(f"Loading GGUF: {model_path}, n_ctx={self.n_ctx}, n_gpu_layers={layers}")
                self.model = Llama(
                    model_path=model_path,
                    n_ctx=self.n_ctx,
                    n_gpu_layers=layers,
                    verbose=False
                )
                self.is_loaded = True
                self.model_name = os.path.basename(model_path)
                self.context_length = self.n_ctx
                self.quant_level = self._detect_quant(model_path)
                log_info(f"GGUF loaded: {self.model_name}, quant={self.quant_level}")
                return True
            except Exception as e:
                if layers > 0:
                    layers = max(0, layers // 2)
                    log_warn(f"GPU load failed ({e}), retrying with n_gpu_layers={layers}")
                elif layers == 0:
                    log_error("CPU load also failed", e)
                    self.is_loaded = False
                    return False
                else:  # layers == -1
                    layers = 35
                    log_warn(f"Full GPU failed ({e}), retrying with n_gpu_layers={layers}")

    def generate(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.7) -> str:
        if not self.is_loaded or self.model is None:
            return "[llama_cpp not loaded]"
        try:
            output = self.model(prompt, max_tokens=max_tokens, temperature=temperature, echo=False)
            text = output["choices"][0]["text"] if output.get("choices") else ""
            return text.strip()
        except Exception as e:
            log_error("llama_cpp generation failed", e)
            return f"[Generation error: {e}]"

    def health_check(self) -> Dict[str, Any]:
        if not self.is_loaded:
            return {"healthy": False, "message": "Model not loaded"}
        try:
            result = self.generate("Hello", max_tokens=5, temperature=0.1)
            return {"healthy": bool(result), "message": f"OK: got '{result[:30]}...'"}
        except Exception as e:
            return {"healthy": False, "message": str(e)}
