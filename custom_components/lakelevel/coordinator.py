"""Update coordinator for Lake Level."""

from __future__ import annotations

from datetime import datetime, time, timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.event import async_track_utc_time_change
from homeassistant.util.dt import as_utc, parse_time

from .lib import LakeLevelError, LakeMeasurement, get_lake_level

from .const import CONF_FETCH_TIME, CONF_LAKE, CONF_RIVER, CONF_RETRIES, DEFAULT_RETRIES

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
        self._fetch_time: time = parse_time(config.get(CONF_FETCH_TIME)) or time(6, 0)
        self._retries: int = config.get(CONF_RETRIES, DEFAULT_RETRIES)
        self._unsub = None

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
        if self._unsub is not None:
            self._unsub()

        @callback
        def _handle_time(_: datetime) -> None:
            self.async_set_updated_data(None)
            self.hass.async_create_task(self.async_request_refresh())

        self._unsub = async_track_utc_time_change(
            self.hass,
            _handle_time,
            hour=self._fetch_time.hour,
            minute=self._fetch_time.minute,
            second=0,
        )

    async def async_update_options(self, options: dict[str, Any]) -> None:
        if CONF_FETCH_TIME in options:
            self._fetch_time = parse_time(options[CONF_FETCH_TIME]) or self._fetch_time
            await self._schedule_updates()
        if CONF_RETRIES in options:
            self._retries = options[CONF_RETRIES]
