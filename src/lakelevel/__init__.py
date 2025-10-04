"""Utilities for fetching lake levels."""

from .siljan import LakeLevelError, LakeMeasurement, get_siljan_level

__all__ = ["get_siljan_level", "LakeLevelError", "LakeMeasurement"]
