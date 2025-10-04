"""Helper to import lake level client for the Home Assistant integration."""

from __future__ import annotations

try:  # pragma: no cover - executed when package installed separately
    from lakelevel import (  # type: ignore[import]
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
except Exception:  # pragma: no cover - fallback to vendored copy
    from ._vendor import (  # noqa: F401
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
    "LakeLevelError",
    "LakeMeasurement",
    "get_lake_level",
    "get_siljan_level",
    "list_lakes",
    "list_rivers",
]
