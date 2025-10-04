"""Vendored lake level client for Home Assistant integration."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup

LAKE_LEVEL_URL = "https://login.vattenreglering.se/m/vattenstand.asp"
DEFAULT_TIMEOUT = 180
DEFAULT_RIVER = "Dalälven"
DEFAULT_LAKE = "Siljan"
_FORM_HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}
_VALUE_CELL_INDEX = 8
_TIMESTAMP_CELL_INDEX = 9


class LakeLevelError(RuntimeError):
    """Raised when a measurement cannot be parsed."""


@dataclass(frozen=True)
class LakeMeasurement:
    river: str
    lake: str
    level_m: Decimal
    timestamp: str


def get_lake_level(
    river: str,
    lake: str,
    session: Optional[requests.Session] = None,
    timeout: float | None = None,
) -> LakeMeasurement:
    session = session or requests.Session()
    resolved_timeout = DEFAULT_TIMEOUT if timeout is None else timeout

    landing_html = _prime_session(session, resolved_timeout)
    river_options = _parse_river_options(landing_html)

    river_key = _normalise(river)
    if river_key not in river_options:
        raise LakeLevelError(f"River '{river}' not found on source page")

    table_html = _fetch_river_table(
        session, river_options[river_key], resolved_timeout
    )
    return parse_lake_level(table_html, river, lake)


def get_siljan_level(
    session: Optional[requests.Session] = None, timeout: float | None = None
) -> LakeMeasurement:
    return get_lake_level(
        DEFAULT_RIVER,
        DEFAULT_LAKE,
        session=session,
        timeout=timeout,
    )


def list_lakes(
    river: str,
    session: Optional[requests.Session] = None,
    timeout: float | None = None,
) -> List[str]:
    session = session or requests.Session()
    resolved_timeout = DEFAULT_TIMEOUT if timeout is None else timeout

    landing_html = _prime_session(session, resolved_timeout)
    river_options = _parse_river_options(landing_html)

    river_key = _normalise(river)
    if river_key not in river_options:
        raise LakeLevelError(f"River '{river}' not found on source page")

    table_html = _fetch_river_table(
        session, river_options[river_key], resolved_timeout
    )
    return _extract_lake_names(table_html)


def list_rivers(
    session: Optional[requests.Session] = None, timeout: float | None = None
) -> List[str]:
    session = session or requests.Session()
    resolved_timeout = DEFAULT_TIMEOUT if timeout is None else timeout

    landing_html = _prime_session(session, resolved_timeout)
    soup = BeautifulSoup(landing_html, "html.parser")
    select = soup.find("select", attrs={"name": "Ralv"})
    if select is None:
        raise LakeLevelError("Could not find river dropdown on landing page")

    rivers = [option.get_text(strip=True) for option in select.find_all("option") if option.get_text(strip=True)]
    if not rivers:
        raise LakeLevelError("No rivers discovered on landing page")
    return rivers


def parse_lake_level(html: str, river: str, lake_name: str) -> LakeMeasurement:
    target = _normalise(lake_name)
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", id="iseqchart")
    if table is None:
        raise LakeLevelError("Could not locate the lake data table in the response")

    for row in table.find_all("tr"):
        first_cell = row.find("td")
        if first_cell is None:
            continue
        cell_text = first_cell.get_text(strip=True)
        if _normalise(cell_text) != target:
            continue

        cells = row.find_all("td")
        if len(cells) <= max(_VALUE_CELL_INDEX, _TIMESTAMP_CELL_INDEX):
            raise LakeLevelError(
                f"Row for lake '{lake_name}' is missing expected columns"
            )

        value_text = cells[_VALUE_CELL_INDEX].get_text(strip=True).replace("\xa0", " ")
        level = _parse_decimal(value_text)
        timestamp = cells[_TIMESTAMP_CELL_INDEX].get_text(" ", strip=True).replace(
            "\xa0", " "
        )
        return LakeMeasurement(
            river=river,
            lake=cell_text,
            level_m=level,
            timestamp=timestamp,
        )

    raise LakeLevelError(f"Lake '{lake_name}' not found in river table")


def _prime_session(session: requests.Session, timeout: float) -> str:
    response = session.get(LAKE_LEVEL_URL, timeout=timeout)
    response.raise_for_status()
    response.encoding = "iso-8859-1"
    return response.text


def _fetch_river_table(
    session: requests.Session, river_value: str, timeout: float
) -> str:
    body = urlencode({"Ralv": river_value}, encoding="iso-8859-1")
    response = session.post(
        LAKE_LEVEL_URL, data=body, headers=_FORM_HEADERS, timeout=timeout
    )
    response.raise_for_status()
    response.encoding = "iso-8859-1"
    return response.text


def _parse_river_options(html: str) -> Dict[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    select = soup.find("select", attrs={"name": "Ralv"})
    if select is None:
        raise LakeLevelError("Could not find river dropdown on landing page")

    options: Dict[str, str] = {}
    for option in select.find_all("option"):
        value = option.get("value")
        label = option.get_text(strip=True)
        if not value or not label:
            continue
        options[_normalise(label)] = value

    if not options:
        raise LakeLevelError("No rivers discovered on landing page")

    return options


def _extract_lake_names(html: str) -> List[str]:
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", id="iseqchart")
    if table is None:
        raise LakeLevelError("Could not locate the lake data table in the response")

    names: List[str] = []
    for row in table.find_all("tr"):
        first_cell = row.find("td")
        if first_cell is None:
            continue
        name = first_cell.get_text(strip=True)
        if name:
            names.append(name)

    if not names:
        raise LakeLevelError("No lake rows found in river table")

    return names


def _parse_decimal(value: str) -> Decimal:
    normalised = value.replace(" ", "").replace(",", ".")
    try:
        return Decimal(normalised)
    except InvalidOperation as exc:  # pragma: no cover - defensive path
        raise LakeLevelError(f"Could not parse numeric value '{value}'") from exc


def _normalise(value: str) -> str:
    return " ".join(value.strip().lower().split())
