"""Fetch and parse lake level data for Siljan."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Optional

import requests
from bs4 import BeautifulSoup

LAKE_LEVEL_URL = "https://login.vattenreglering.se/m/vattenstand.asp"
DEFAULT_TIMEOUT = 180
_DALALVEN_FORM_BODY = "Ralv=Dal%E4lven"
_FORM_HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}
_VALUE_CELL_INDEX = 8
_TIMESTAMP_CELL_INDEX = 9


class LakeLevelError(RuntimeError):
    """Raised when we cannot parse the Siljan measurement."""


@dataclass(frozen=True)
class LakeMeasurement:
    lake: str
    level_m: Decimal
    timestamp: str


def get_siljan_level(
    session: Optional[requests.Session] = None, timeout: float | None = None
) -> LakeMeasurement:
    """Retrieve the latest lake level for Siljan."""
    session = session or requests.Session()
    resolved_timeout = DEFAULT_TIMEOUT if timeout is None else timeout
    _prime_session(session, resolved_timeout)
    html = _fetch_dalalven_table(session, resolved_timeout)
    return parse_siljan_level(html)


def _prime_session(session: requests.Session, timeout: float) -> None:
    response = session.get(LAKE_LEVEL_URL, timeout=timeout)
    response.raise_for_status()
    response.encoding = "iso-8859-1"


def _fetch_dalalven_table(session: requests.Session, timeout: float) -> str:
    response = session.post(
        LAKE_LEVEL_URL,
        data=_DALALVEN_FORM_BODY,
        headers=_FORM_HEADERS,
        timeout=timeout,
    )
    response.raise_for_status()
    response.encoding = "iso-8859-1"
    return response.text


def parse_siljan_level(html: str) -> LakeMeasurement:
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", id="iseqchart")
    if table is None:
        raise LakeLevelError("Could not locate the Dalälven data table in the response")

    for row in table.find_all("tr"):
        first_cell = row.find("td")
        if first_cell is None:
            continue
        if first_cell.get_text(strip=True).lower() != "siljan":
            continue

        cells = row.find_all("td")
        if len(cells) <= max(_VALUE_CELL_INDEX, _TIMESTAMP_CELL_INDEX):
            raise LakeLevelError("Siljan row is missing expected columns")

        value_text = cells[_VALUE_CELL_INDEX].get_text(strip=True).replace("\xa0", " ")
        level = _parse_decimal(value_text)
        timestamp = cells[_TIMESTAMP_CELL_INDEX].get_text(" ", strip=True).replace("\xa0", " ")
        return LakeMeasurement(lake="Siljan", level_m=level, timestamp=timestamp)

    raise LakeLevelError("Siljan row not found in Dalälven table")


def _parse_decimal(value: str) -> Decimal:
    normalised = value.replace(" ", "").replace(",", ".")
    try:
        return Decimal(normalised)
    except InvalidOperation as exc:  # pragma: no cover - defensive path
        raise LakeLevelError(f"Could not parse numeric value '{value}'") from exc
