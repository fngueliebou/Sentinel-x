"""Security utilities: treat external content as untrusted data."""

from sentinelx.security.untrusted import detect_injection_patterns, wrap_as_data

__all__ = ["detect_injection_patterns", "wrap_as_data"]
