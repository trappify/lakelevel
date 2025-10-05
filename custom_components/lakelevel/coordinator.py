"""Update coordinator for Lake Level."""

from __future__ import annotations

from datetime import datetime, time
import logging
from typing import Any, Callable, List

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.event import async_track_utc_time_change
from homeassistant.util.dt import parse_time

from .lib import LakeLevelError, LakeMeasurement, get_lake_level

from .const import (
    CONF_FETCH_TIME,
    CONF_FETCH_TIMES,
    CONF_LAKE,
    CONF_RIVER,
    CONF_RETRIES,
    CONF_UPDATES_PER_DAY,
    DEFAULT_FETCH_TIME,
    DEFAULT_RETRIES,
    MAX_UPDATES_PER_DAY,
)

_LOGGER = logging.getLogger(__name__)


class LakeLevelCoordinator(DataUpdateCoordinator[LakeMeasurement | None]):
    """Coordinator that fetches lake data according to schedule."""

    def __init__(self, hass: HomeAssistant, config: dict[str, Any]) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="Lake Level",
        )
        self._river: str = config[CONF_RIVER]
        self._lake: str = config[CONF_LAKE]
        self._retries: int = config.get(CONF_RETRIES, DEFAULT_RETRIES)
        self._fetch_times: list[time] = self._parse_fetch_times(config)
        self._unsubs: List[Callable[[], None]] = []

    async def async_config_entry_first_refresh(self) -> None:
        await self._schedule_updates()
        await super().async_config_entry_first_refresh()

    async def _async_update_data(self) -> LakeMeasurement:
        retries = self._retries
        last_exception: Exception | None = None
        for attempt in range(retries):
            try:
                measurement = await self.hass.async_add_executor_job(
                    get_lake_level, self._river, self._lake
                )
            except LakeLevelError as err:
                last_exception = err
                _LOGGER.warning("Failed to fetch lake level (attempt %s/%s)", attempt + 1, retries)
                continue
            except Exception as err:  # pragma: no cover - unexpected
                last_exception = err
                _LOGGER.exception("Unexpected error fetching lake level", exc_info=err)
                continue
            else:
                return measurement

        raise last_exception or LakeLevelError("Unknown error")

    async def _schedule_updates(self) -> None:
        for unsub in self._unsubs:
            if unsub:
                unsub()
        self._unsubs = []

        unique_times = sorted(
            {time(hour=t.hour, minute=t.minute) for t in self._fetch_times},
            key=lambda t: (t.hour, t.minute),
        )

        @callback
        def _handle_time(_: datetime) -> None:
            self.async_set_updated_data(None)
            self.hass.async_create_task(self.async_request_refresh())

        for fetch_time in unique_times:
            unsub = async_track_utc_time_change(
                self.hass,
                _handle_time,
                hour=fetch_time.hour,
                minute=fetch_time.minute,
                second=0,
            )
            self._unsubs.append(unsub)

    async def async_update_options(self, options: dict[str, Any]) -> None:
        if CONF_RETRIES in options:
            self._retries = options[CONF_RETRIES]
        if CONF_FETCH_TIMES in options or CONF_FETCH_TIME in options:
            config = {CONF_FETCH_TIMES: options.get(CONF_FETCH_TIMES)}
            if CONF_FETCH_TIME in options:
                config[CONF_FETCH_TIME] = options[CONF_FETCH_TIME]
            if CONF_UPDATES_PER_DAY in options:
                config[CONF_UPDATES_PER_DAY] = options[CONF_UPDATES_PER_DAY]
            self._fetch_times = self._parse_fetch_times(config)
            await self._schedule_updates()

    def _parse_fetch_times(self, config: dict[str, Any]) -> list[time]:
        times = config.get(CONF_FETCH_TIMES)
        if not times:
            single = config.get(CONF_FETCH_TIME, DEFAULT_FETCH_TIME)
            times = [single]
        updates = config.get(CONF_UPDATES_PER_DAY, len(times))
        parsed: list[time] = []
        for index, value in enumerate(times):
            if index >= updates:
                break
            parsed_time = parse_time(value) or parse_time(DEFAULT_FETCH_TIME)
            parsed.append(parsed_time or time(6, 0))

        if not parsed:
            parsed.append(parse_time(DEFAULT_FETCH_TIME) or time(6, 0))
        return parsed[:MAX_UPDATES_PER_DAY]
