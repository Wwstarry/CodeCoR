"""
Unified LLM client supporting Anthropic Claude and OpenAI backends.
"""
from __future__ import annotations

import os
import time
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Thin wrapper around Anthropic / OpenAI APIs with:
    - Configurable backend ("anthropic" | "openai")
    - Shared retry logic (3 retries, exponential back-off)
    - Separate temperatures for generation vs. pruning calls
    """

    SUPPORTED_BACKENDS = {"anthropic", "openai"}

    def __init__(
        self,
        backend: str = "anthropic",
        model: str = "claude-haiku-4-5-20251001",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature_gen: float = 0.8,
        temperature_prune: float = 0.0,
        max_tokens: int = 2048,
        max_retries: int = 3,
    ):
        if backend not in self.SUPPORTED_BACKENDS:
            raise ValueError(f"backend must be one of {self.SUPPORTED_BACKENDS}")

        self.backend = backend
        self.model = model
        self.temperature_gen = temperature_gen
        self.temperature_prune = temperature_prune
        self.max_tokens = max_tokens
        self.max_retries = max_retries

        if backend == "anthropic":
            import anthropic  # type: ignore

            auth_token = api_key or os.environ.get("ANTHROPIC_AUTH_TOKEN") or os.environ.get("ANTHROPIC_API_KEY")
            _base_url = base_url or os.environ.get("ANTHROPIC_BASE_URL")
            self._client = anthropic.Anthropic(
                api_key=auth_token,
                base_url=_base_url,
            )

        elif backend == "openai":
            import openai  # type: ignore

            _api_key = api_key or os.environ.get("OPENAI_API_KEY")
            _base_url = base_url or os.environ.get("OPENAI_BASE_URL")
            self._client = openai.OpenAI(
                api_key=_api_key,
                base_url=_base_url,
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system: Optional[str] = None,
    ) -> str:
        """Single-turn chat completion, returns text string."""
        temp = temperature if temperature is not None else self.temperature_gen
        tok = max_tokens or self.max_tokens

        for attempt in range(self.max_retries):
            try:
                return self._call(messages, temp, tok, system)
            except Exception as exc:
                exc_str = str(exc)
                # Rate-limit (429): wait > 60s to guarantee the per-minute
                # window resets before retrying, avoiding wasted retry attempts.
                if "429" in exc_str or "rate" in exc_str.lower():
                    wait = 65 + attempt * 5  # 65s, 70s, 75s — always > 1min window
                else:
                    wait = 2 ** attempt  # 1s, 2s, 4s …
                logger.warning(
                    f"LLM call failed (attempt {attempt+1}/{self.max_retries}): {exc}. "
                    f"Retrying in {wait}s"
                )
                if attempt < self.max_retries - 1:
                    time.sleep(wait)
                else:
                    raise

    def chat_prune(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
    ) -> str:
        """Pruning call — always uses temperature=0.0 for determinism."""
        return self.chat(messages, temperature=self.temperature_prune, system=system)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _call(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        system: Optional[str],
    ) -> str:
        if self.backend == "anthropic":
            return self._call_anthropic(messages, temperature, max_tokens, system)
        return self._call_openai(messages, temperature, max_tokens, system)

    def _call_anthropic(self, messages, temperature, max_tokens, system):
        kwargs: Dict[str, Any] = dict(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=messages,
        )
        if system:
            kwargs["system"] = system
        response = self._client.messages.create(**kwargs)
        return response.content[0].text.strip()

    def _call_openai(self, messages, temperature, max_tokens, system):
        all_messages = []
        if system:
            all_messages.append({"role": "system", "content": system})
        all_messages.extend(messages)
        response = self._client.chat.completions.create(
            model=self.model,
            messages=all_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()
