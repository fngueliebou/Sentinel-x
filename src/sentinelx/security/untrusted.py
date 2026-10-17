"""Untrusted-data handling.

Logs, events and knowledge are UNTRUSTED (conception v0.2 §8). Two helpers:

- `detect_injection_patterns`: flags injection-like text so it can be recorded on
  the evidence. This is INFORMATIONAL ONLY — it never changes control flow and is
  not claimed to be a reliable defense (it must be *evaluated*, not trusted;
  EVALUATION.md §8). It is a heuristic for visibility, nothing more.
- `wrap_as_data`: renders untrusted text inside an explicit data fence so that,
  when it is later shown to an LLM, instruction/data separation is syntactically
  marked. The deterministic provider ignores content semantics entirely.
"""

from __future__ import annotations

import re

# Heuristic patterns commonly seen in prompt-injection attempts. Deliberately
# simple and transparent; extended and *measured* under EVALUATION.md §8.
_INJECTION_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("override_instructions", re.compile(r"ignore\s+(?:all\s+|previous\s+|prior\s+|the\s+)*instructions", re.I)),
    ("role_switch", re.compile(r"you are now|act as|new system prompt", re.I)),
    ("decision_steer", re.compile(r"mark\b.{0,40}?(benign|safe|false[ -]?positive)", re.I)),
    ("exfiltration", re.compile(r"(send|exfiltrate|leak).{0,20}(secret|password|token|key)", re.I)),
    ("tool_coercion", re.compile(r"(run|execute|delete|disable).{0,20}(command|rule|account)", re.I)),
)


def detect_injection_patterns(text: str) -> list[str]:
    """Return the names of injection-like patterns found in `text` (possibly empty)."""
    if not text:
        return []
    return [name for name, pattern in _INJECTION_PATTERNS if pattern.search(text)]


def wrap_as_data(text: str) -> str:
    """Fence untrusted text as data for display to an LLM.

    The fence makes instruction/data separation explicit. It is a marker, not a
    guarantee; robustness is evaluated separately.
    """
    return f"<<UNTRUSTED_DATA>>\n{text}\n<<END_UNTRUSTED_DATA>>"
