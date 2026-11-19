"""Versioned prompt identifier.

Prompts are versioned and recorded in every report/experiment for reproducibility. The deterministic provider does not use prose
prompts, but it still reports this version so runs are comparable across providers.
"""

PROMPT_VERSION = "inv-prompt-v1"
