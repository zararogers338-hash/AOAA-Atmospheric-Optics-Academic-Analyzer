# -*- coding: utf-8 -*-
"""Ensemble inference: vote/consensus/weighted across multiple backends."""

from typing import Dict, Any, List, Optional
from utils.ai_backends.base import AIBackend
from utils.logger import log_info, log_warn, log_error


class EnsembleBackend(AIBackend):
    def __init__(self):
        super().__init__()
        self.name = "ensemble"
        self.backends: List[AIBackend] = []
        self.strategy = "vote"  # vote, concat, weighted
        self.fallback_chain: List[AIBackend] = []

    def add_backend(self, backend: AIBackend):
        self.backends.append(backend)

    def set_fallback_chain(self, chain: List[AIBackend]):
        self.fallback_chain = chain

    def load(self, **kwargs) -> bool:
        self.strategy = kwargs.get("strategy", "vote")
        self.is_loaded = any(b.is_loaded for b in self.backends)
        self.model_name = f"ensemble({len(self.backends)})"
        return self.is_loaded

    def generate(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.7) -> str:
        results = []
        for b in self.backends:
            if b.is_loaded:
                try:
                    text = b.timed_generate(prompt, max_tokens, temperature)
                    if text and not text.startswith("["):
                        results.append({"backend": b.name, "text": text})
                except Exception as e:
                    log_warn(f"Ensemble: {b.name} failed: {e}")

        if not results:
            # Try fallback chain
            for fb in self.fallback_chain:
                if fb.is_loaded:
                    try:
                        text = fb.timed_generate(prompt, max_tokens, temperature)
                        if text and not text.startswith("["):
                            return f"[Fallback: {fb.name}] {text}"
                    except Exception:
                        continue
            return "[Ensemble: all backends failed]"

        if self.strategy == "concat":
            parts = [f"--- {r['backend']} ---\n{r['text']}" for r in results]
            return "\n\n".join(parts)
        elif self.strategy == "vote" or self.strategy == "weighted":
            # Simple: pick longest / most detailed response
            best = max(results, key=lambda r: len(r["text"]))
            summary = f"[Consensus from {len(results)} models, selected: {best['backend']}]\n{best['text']}"
            return summary
        else:
            return results[0]["text"] if results else "[No results]"

    def health_check(self) -> Dict[str, Any]:
        statuses = []
        for b in self.backends:
            check = b.health_check()
            statuses.append(f"{b.name}: {'OK' if check['healthy'] else 'FAIL'}")
        healthy = any("OK" in s for s in statuses)
        return {"healthy": healthy, "message": "; ".join(statuses)}


class HybridBackend(AIBackend):
    """Primary + fallback backend: tries primary first, falls back on failure/timeout."""
    def __init__(self, primary: AIBackend, fallback: AIBackend):
        super().__init__()
        self.name = "hybrid"
        self.primary = primary
        self.fallback = fallback
        self.model_name = f"{primary.name}+{fallback.name}"

    def load(self, **kwargs) -> bool:
        self.is_loaded = self.primary.is_loaded or self.fallback.is_loaded
        return self.is_loaded

    def generate(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.7) -> str:
        if self.primary.is_loaded:
            try:
                result = self.primary.timed_generate(prompt, max_tokens, temperature)
                if result and not result.startswith("["):
                    return result
            except Exception as e:
                log_warn(f"Hybrid primary ({self.primary.name}) failed: {e}")

        if self.fallback.is_loaded:
            try:
                result = self.fallback.timed_generate(prompt, max_tokens, temperature)
                log_info(f"Hybrid: used fallback ({self.fallback.name})")
                return result
            except Exception as e:
                log_error(f"Hybrid fallback ({self.fallback.name}) also failed", e)

        return "[Hybrid: both primary and fallback failed]"

    def health_check(self) -> Dict[str, Any]:
        p = self.primary.health_check()
        f = self.fallback.health_check()
        return {
            "healthy": p["healthy"] or f["healthy"],
            "message": f"Primary({self.primary.name}): {p['message']}; Fallback({self.fallback.name}): {f['message']}"
        }
