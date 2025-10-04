from decimal import Decimal
from pathlib import Path

import pytest

from lakelevel.siljan import LakeLevelError, LakeMeasurement, parse_siljan_level

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_parse_siljan_level_returns_measurement() -> None:
    html = load_fixture("dalalven_siljan.html")
    measurement = parse_siljan_level(html)

    assert isinstance(measurement, LakeMeasurement)
    assert measurement.lake == "Siljan"
    assert measurement.level_m == Decimal("161.65")
    assert measurement.timestamp == "12:55 okt 04"


def test_parse_siljan_level_missing_row() -> None:
    html = "<table id=\"iseqchart\"></table>"
    with pytest.raises(LakeLevelError):
        parse_siljan_level(html)
