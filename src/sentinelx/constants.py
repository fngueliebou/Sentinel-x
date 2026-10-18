"""Shared, project-wide constants.

Single source of truth for values that would otherwise be duplicated across
modules (DRY - Don’t Repeat Yourself). Keeping them here prevents the classic bug where one copy is
changed and the others silently disagree.
"""

# Number of failed-authentication events that, on their own, warrant escalation
# as a likely brute-force attempt. Used by the deterministic triage baseline
# (triage/rules.py) and the deterministic LLM stub (llm/deterministic.py) so the
# two agree by construction.
BRUTE_FORCE_FAILED_AUTH_THRESHOLD = 5