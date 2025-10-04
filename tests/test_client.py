from decimal import Decimal
from pathlib import Path

import pytest
import responses

from lakelevel import get_siljan_level
from lakelevel.siljan import LAKE_LEVEL_URL, LakeLevelError

FIXTURE = Path(__file__).parent / "fixtures" / "dalalven_siljan.html"


@pytest.fixture()
def dalalven_html() -> str:
    return FIXTURE.read_text(encoding="utf-8")


@responses.activate
def test_get_siljan_level_posts_iso_form_and_parses(dalalven_html: str) -> None:
    responses.add(responses.GET, LAKE_LEVEL_URL, body="ok", status=200)
    responses.add(responses.POST, LAKE_LEVEL_URL, body=dalalven_html, status=200)

    measurement = get_siljan_level(timeout=5)

    assert measurement.level_m == Decimal("161.65")
    assert measurement.timestamp == "12:55 okt 04"

    responses.assert_call_count(LAKE_LEVEL_URL, 2)
    post_request = responses.calls[1].request
    assert post_request.body == "Ralv=Dal%E4lven"
    assert post_request.headers["Content-Type"] == "application/x-www-form-urlencoded"


@responses.activate
def test_get_siljan_level_propagates_parse_error() -> None:
    responses.add(responses.GET, LAKE_LEVEL_URL, body="ok", status=200)
    responses.add(responses.POST, LAKE_LEVEL_URL, body="<html></html>", status=200)

    with pytest.raises(LakeLevelError):
        get_siljan_level(timeout=5)
