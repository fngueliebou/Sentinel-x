"""LLM provider abstraction.

Default provider is the offline `DeterministicProvider` (used by tests and local
runs, no secrets). A real `AnthropicProvider` exists behind the same interface but
is OPTIONAL and NOT exercised by the test suite (conception v0.2 §7, D4).
"""

from sentinelx.llm.base import AnalysisRequest, LLMProvider, ProviderOutput, ProviderUsage
from sentinelx.llm.factory import get_provider

__all__ = [
    "AnalysisRequest",
    "LLMProvider",
    "ProviderOutput",
    "ProviderUsage",
    "get_provider",
]
