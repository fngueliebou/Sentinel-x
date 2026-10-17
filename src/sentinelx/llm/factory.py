"""Provider selection from settings."""

from __future__ import annotations

from sentinelx.config import Settings, load_settings
from sentinelx.llm.base import LLMProvider
from sentinelx.llm.deterministic import DeterministicProvider


def get_provider(settings: Settings | None = None) -> LLMProvider:
    settings = settings or load_settings()
    provider = settings.llm_provider.lower()

    if provider == "deterministic":
        return DeterministicProvider()

    if provider == "anthropic":
        # Imported lazily so the default path needs no optional dependency.
        from sentinelx.llm.anthropic_provider import AnthropicProvider

        return AnthropicProvider(
            api_key=settings.llm_api_key or "",
            model=settings.llm_model or "",
            temperature=settings.llm_temperature,
        )

    raise ValueError(f"Unknown LLM provider: {settings.llm_provider!r}")
