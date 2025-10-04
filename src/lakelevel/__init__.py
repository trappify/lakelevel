"""Utilities for fetching lake levels."""

from .siljan import (
    DEFAULT_LAKE,
    DEFAULT_RIVER,
    DEFAULT_TIMEOUT,
    LakeLevelError,
    LakeMeasurement,
    get_lake_level,
    get_siljan_level,
    list_lakes,
    list_rivers,
)

__all__ = [
    "DEFAULT_LAKE",
    "DEFAULT_RIVER",
    "DEFAULT_TIMEOUT",
    "get_lake_level",
    "get_siljan_level",
    "list_lakes",
    "list_rivers",
    "LakeLevelError",
    "LakeMeasurement",
]
