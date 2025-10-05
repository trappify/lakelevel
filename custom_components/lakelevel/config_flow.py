"""Config flow for the Lake Level integration."""

from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .lib import list_lakes, list_rivers

from .const import (
    CONF_FETCH_TIMES,
    CONF_LAKE,
    CONF_RIVER,
    CONF_RETRIES,
    CONF_UPDATES_PER_DAY,
    DEFAULT_RETRIES,
    DEFAULT_FETCH_TIME,
    DOMAIN,
    MAX_UPDATES_PER_DAY,
)

_LOGGER = logging.getLogger(__name__)

_TIME_KEY_TEMPLATE = "fetch_time_{}"
_DEFAULT_TIMES = ["06:00", "12:00", "18:00", "00:00"]


class LakeLevelConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Lake Level."""

    VERSION = 2

    def __init__(self) -> None:
        self._selected_river: str | None = None

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        hass: HomeAssistant = self.hass
        errors: dict[str, str] = {}

        if user_input is not None:
            self._selected_river = user_input[CONF_RIVER]
            return await self.async_step_lake()

        try:
            rivers = await hass.async_add_executor_job(list_rivers)
        except Exception as exc:  # pragma: no cover - network failure path
            _LOGGER.exception("Failed to load rivers", exc_info=exc)
            errors["base"] = "cannot_connect"
            rivers = []

        schema = vol.Schema({}) if errors else vol.Schema({vol.Required(CONF_RIVER): vol.In(rivers)})

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_lake(self, user_input: dict | None = None) -> FlowResult:
        if self._selected_river is None:
            return await self.async_step_user()

        errors: dict[str, str] = {}

        try:
            _LOGGER.debug("Loading lakes for river %s", self._selected_river)
            lakes = await self.hass.async_add_executor_job(list_lakes, self._selected_river)
        except Exception as exc:  # pragma: no cover - network failure path
            _LOGGER.exception("Failed to load lakes", exc_info=exc)
            errors["base"] = "cannot_connect"
            lakes = []

        defaults = self._default_times()
        current_input = user_input or {}
        current_times = [
            current_input.get(_TIME_KEY_TEMPLATE.format(index + 1), defaults[index])
            for index in range(MAX_UPDATES_PER_DAY)
        ]
        raw_updates = current_input.get(CONF_UPDATES_PER_DAY, 1)
        raw_retries = current_input.get(CONF_RETRIES, DEFAULT_RETRIES)

        try:
            current_updates = int(raw_updates)
        except (TypeError, ValueError):
            current_updates = 1
        current_updates = max(1, min(MAX_UPDATES_PER_DAY, current_updates))

        try:
            current_retries = int(raw_retries)
        except (TypeError, ValueError):
            current_retries = DEFAULT_RETRIES

        valid_times: list[str] = []
        if user_input is not None and "base" not in errors:
            for index in range(current_updates):
                key = _TIME_KEY_TEMPLATE.format(index + 1)
                value = current_times[index]
                if parse_time(value) is None:
                    errors[key] = "invalid_time"
                else:
                    valid_times.append(value)

            if not errors:
                data = {
                    CONF_RIVER: self._selected_river,
                    CONF_LAKE: user_input[CONF_LAKE],
                    CONF_FETCH_TIMES: valid_times,
                    CONF_UPDATES_PER_DAY: current_updates,
                    CONF_RETRIES: current_retries,
                }
                return self.async_create_entry(
                    title=f"{data[CONF_LAKE]} ({data[CONF_RIVER]})", data=data
                )

        schema = (
            vol.Schema({})
            if errors
            else vol.Schema(
                {
                    vol.Required(CONF_LAKE): vol.In(lakes),
                    vol.Required(
                        CONF_UPDATES_PER_DAY, default=current_updates
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=MAX_UPDATES_PER_DAY)),
                    vol.Optional(
                        _TIME_KEY_TEMPLATE.format(1), default=current_times[0]
                    ): str,
                    vol.Optional(
                        _TIME_KEY_TEMPLATE.format(2), default=current_times[1]
                    ): str,
                    vol.Optional(
                        _TIME_KEY_TEMPLATE.format(3), default=current_times[2]
                    ): str,
                    vol.Optional(
                        _TIME_KEY_TEMPLATE.format(4), default=current_times[3]
                    ): str,
                    vol.Optional(CONF_RETRIES, default=current_retries): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=10)
                    ),
                }
            )
        )

        return self.async_show_form(
            step_id="lake",
            data_schema=schema,
            errors=errors,
            description_placeholders={"river": self._selected_river},
        )

    def _default_times(self) -> list[str]:
        defaults = list(_DEFAULT_TIMES)
        defaults[0] = DEFAULT_FETCH_TIME
        return defaults


class LakeLevelOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        self._entry = entry

    async def async_step_init(self, user_input: dict | None = None) -> FlowResult:
        data = {**self._entry.data, **self._entry.options}
        errors: dict[str, str] = {}

        existing_times = data.get(CONF_FETCH_TIMES) or [data.get(CONF_FETCH_TIME, DEFAULT_FETCH_TIME)]
        existing_times = (existing_times + _DEFAULT_TIMES)[:MAX_UPDATES_PER_DAY]
        raw_existing_updates = data.get(CONF_UPDATES_PER_DAY, len(existing_times))

        current_input = user_input or {}
        current_times = [
            current_input.get(
                _TIME_KEY_TEMPLATE.format(index + 1), existing_times[index]
            )
            for index in range(MAX_UPDATES_PER_DAY)
        ]

        raw_updates = current_input.get(CONF_UPDATES_PER_DAY, raw_existing_updates)
        try:
            current_updates = int(raw_updates)
        except (TypeError, ValueError):
            current_updates = max(1, len(existing_times))
        current_updates = max(1, min(MAX_UPDATES_PER_DAY, current_updates))

        raw_retries = current_input.get(CONF_RETRIES, data.get(CONF_RETRIES, DEFAULT_RETRIES))
        try:
            current_retries = int(raw_retries)
        except (TypeError, ValueError):
            current_retries = DEFAULT_RETRIES

        valid_times: list[str] = []
        if user_input is not None:
            for index in range(current_updates):
                key = _TIME_KEY_TEMPLATE.format(index + 1)
                value = current_times[index]
                if parse_time(value) is None:
                    errors[key] = "invalid_time"
                else:
                    valid_times.append(value)

            if not errors:
                options = {
                    CONF_FETCH_TIMES: valid_times,
                    CONF_UPDATES_PER_DAY: current_updates,
                    CONF_RETRIES: current_retries,
                }
                return self.async_create_entry(title="", data=options)

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_UPDATES_PER_DAY, default=current_updates
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=MAX_UPDATES_PER_DAY)),
                vol.Optional(
                    _TIME_KEY_TEMPLATE.format(1), default=current_times[0]
                ): str,
                vol.Optional(
                    _TIME_KEY_TEMPLATE.format(2), default=current_times[1]
                ): str,
                vol.Optional(
                    _TIME_KEY_TEMPLATE.format(3), default=current_times[2]
                ): str,
                vol.Optional(
                    _TIME_KEY_TEMPLATE.format(4), default=current_times[3]
                ): str,
                vol.Optional(CONF_RETRIES, default=current_retries): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=10)
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)


async def async_get_options_flow(entry: config_entries.ConfigEntry) -> LakeLevelOptionsFlowHandler:
    return LakeLevelOptionsFlowHandler(entry)
