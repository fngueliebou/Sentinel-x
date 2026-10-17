"""Load raw alerts from JSON. Validation is delegated to the RawAlert contract."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sentinelx.schemas import RawAlert


def load_raw_alert_from_dict(payload: dict[str, Any]) -> RawAlert:
    """Build a RawAlert from an in-memory dict (pydantic validates)."""
    return RawAlert.model_validate(payload)


def load_raw_alert(path: str | Path) -> RawAlert:
    """Load and validate a single raw alert from a JSON file.

    The file content is untrusted data; parsing it as JSON never executes anything.
    """
    text = Path(path).read_text(encoding="utf-8")
    payload = json.loads(text)
    return load_raw_alert_from_dict(payload)
