"""Config flow for the Lake Level integration."""

from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .lib import list_lakes, list_rivers

from .const import (
    CONF_FETCH_TIME,
    CONF_FETCH_TIMES,
    CONF_LAKE,
    CONF_RIVER,
    CONF_RETRIES,
    CONF_UPDATES_PER_DAY,
    DEFAULT_FETCH_TIME,
    DEFAULT_RETRIES,
    DOMAIN,
    MAX_UPDATES_PER_DAY,
)

_LOGGER = logging.getLogger(__name__)

_TIME_KEY_TEMPLATE = "fetch_time_{}"
_TIME_VALIDATOR = vol.Match(r"^(?:[01]\d|2[0-3]):[0-5]\d$")
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

        if user_input is not None:
            updates = user_input[CONF_UPDATES_PER_DAY]
            times: list[str] = []
            for index in range(MAX_UPDATES_PER_DAY):
                key = _TIME_KEY_TEMPLATE.format(index + 1)
                value = user_input.get(key, DEFAULT_FETCH_TIME)
                if index < updates:
                    times.append(value)
            data = {
                CONF_RIVER: self._selected_river,
                CONF_LAKE: user_input[CONF_LAKE],
                CONF_FETCH_TIMES: times,
                CONF_UPDATES_PER_DAY: updates,
                CONF_RETRIES: user_input[CONF_RETRIES],
            }
            return self.async_create_entry(title=f"{data[CONF_LAKE]} ({data[CONF_RIVER]})", data=data)

        try:
            _LOGGER.debug("Loading lakes for river %s", self._selected_river)
            lakes = await self.hass.async_add_executor_job(list_lakes, self._selected_river)
        except Exception as exc:  # pragma: no cover - network failure path
            _LOGGER.exception("Failed to load lakes", exc_info=exc)
            errors["base"] = "cannot_connect"
            lakes = []

        defaults = self._default_times()
        schema = (
            vol.Schema({})
            if errors
            else vol.Schema(
                {
                    vol.Required(CONF_LAKE): vol.In(lakes),
                    vol.Required(
                        CONF_UPDATES_PER_DAY, default=1
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=MAX_UPDATES_PER_DAY)),
                    vol.Optional(_TIME_KEY_TEMPLATE.format(1), default=defaults[0]): _TIME_VALIDATOR,
                    vol.Optional(_TIME_KEY_TEMPLATE.format(2), default=defaults[1]): _TIME_VALIDATOR,
                    vol.Optional(_TIME_KEY_TEMPLATE.format(3), default=defaults[2]): _TIME_VALIDATOR,
                    vol.Optional(_TIME_KEY_TEMPLATE.format(4), default=defaults[3]): _TIME_VALIDATOR,
                    vol.Optional(CONF_RETRIES, default=DEFAULT_RETRIES): vol.All(
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
        retries = data.get(CONF_RETRIES, DEFAULT_RETRIES)
        times: list[str] = data.get(CONF_FETCH_TIMES) or [data.get(CONF_FETCH_TIME, DEFAULT_FETCH_TIME)]
        updates = data.get(CONF_UPDATES_PER_DAY, len(times))
        times = (times + _DEFAULT_TIMES)[:MAX_UPDATES_PER_DAY]

        if user_input is not None:
            updates = user_input[CONF_UPDATES_PER_DAY]
            times = []
            for index in range(MAX_UPDATES_PER_DAY):
                key = _TIME_KEY_TEMPLATE.format(index + 1)
                value = user_input.get(key, DEFAULT_FETCH_TIME)
                if index < updates:
                    times.append(value)

            options = {
                CONF_FETCH_TIMES: times,
                CONF_UPDATES_PER_DAY: updates,
                CONF_RETRIES: user_input[CONF_RETRIES],
            }
            return self.async_create_entry(title="", data=options)

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_UPDATES_PER_DAY, default=updates
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=MAX_UPDATES_PER_DAY)),
                vol.Optional(_TIME_KEY_TEMPLATE.format(1), default=times[0]): _TIME_VALIDATOR,
                vol.Optional(_TIME_KEY_TEMPLATE.format(2), default=times[1]): _TIME_VALIDATOR,
                vol.Optional(_TIME_KEY_TEMPLATE.format(3), default=times[2]): _TIME_VALIDATOR,
                vol.Optional(_TIME_KEY_TEMPLATE.format(4), default=times[3]): _TIME_VALIDATOR,
                vol.Optional(CONF_RETRIES, default=retries): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=10)
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)


async def async_get_options_flow(entry: config_entries.ConfigEntry) -> LakeLevelOptionsFlowHandler:
    return LakeLevelOptionsFlowHandler(entry)
