from decimal import Decimal
from pathlib import Path

import pytest
import responses

from lakelevel import (
    DEFAULT_LAKE,
    DEFAULT_RIVER,
    get_lake_level,
    get_siljan_level,
    list_lakes,
    list_rivers,
)
from lakelevel.siljan import LAKE_LEVEL_URL, LakeLevelError

FIXTURE_DIR = Path(__file__).parent / "fixtures"
LANDING_HTML = (FIXTURE_DIR / "landing.html").read_text(encoding="utf-8").encode(
    "iso-8859-1"
)
LAKE_HTML = (FIXTURE_DIR / "dalalven_sample.html").read_text(encoding="utf-8").encode(
    "iso-8859-1"
)


def _mock_responses_for_dalalven(
    resp: responses.RequestsMock, lake_html: bytes = LAKE_HTML
) -> None:
    resp.add(responses.GET, LAKE_LEVEL_URL, body=LANDING_HTML, status=200)
    resp.add(responses.POST, LAKE_LEVEL_URL, body=lake_html, status=200)


@responses.activate
def test_get_lake_level_posts_iso_form_and_parses() -> None:
    _mock_responses_for_dalalven(responses)

    measurement = get_lake_level(DEFAULT_RIVER, DEFAULT_LAKE, timeout=5)

    assert measurement.river == DEFAULT_RIVER
    assert measurement.level_m == Decimal("161.65")
    assert measurement.timestamp == "12:55 okt 04"

    responses.assert_call_count(LAKE_LEVEL_URL, 2)
    post_request = responses.calls[1].request
    assert post_request.body == "Ralv=Dal%E4lven"
    assert post_request.headers["Content-Type"] == "application/x-www-form-urlencoded"


@responses.activate
def test_get_lake_level_unknown_river() -> None:
    _mock_responses_for_dalalven(responses)

    with pytest.raises(LakeLevelError):
        get_lake_level("Nonexistent", DEFAULT_LAKE, timeout=5)


@responses.activate
def test_get_lake_level_unknown_lake() -> None:
    _mock_responses_for_dalalven(responses, b"<html></html>")

    with pytest.raises(LakeLevelError):
        get_lake_level(DEFAULT_RIVER, "Unknown", timeout=5)


@responses.activate
def test_get_siljan_level_alias() -> None:
    _mock_responses_for_dalalven(responses)

    measurement = get_siljan_level(timeout=5)
    assert measurement.lake == DEFAULT_LAKE


@responses.activate
def test_list_lakes_returns_names() -> None:
    _mock_responses_for_dalalven(responses)

    lakes = list_lakes(DEFAULT_RIVER, timeout=5)
    assert DEFAULT_LAKE in lakes


@responses.activate
def test_get_lake_level_propagates_parse_error() -> None:
    _mock_responses_for_dalalven(responses, b"<html></html>")

    with pytest.raises(LakeLevelError):
        get_lake_level(DEFAULT_RIVER, DEFAULT_LAKE, timeout=5)


@responses.activate
def test_list_rivers_returns_all_names() -> None:
    responses.add(responses.GET, LAKE_LEVEL_URL, body=LANDING_HTML, status=200)

    rivers = list_rivers(timeout=5)

    assert rivers[0] == "Umeälven"
    assert DEFAULT_RIVER in rivers
