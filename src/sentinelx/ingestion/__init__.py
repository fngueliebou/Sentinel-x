"""Ingestion: load raw alerts from external representations into RawAlert."""

from sentinelx.ingestion.loader import load_raw_alert, load_raw_alert_from_dict

__all__ = ["load_raw_alert", "load_raw_alert_from_dict"]
