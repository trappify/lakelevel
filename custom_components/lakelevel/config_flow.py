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
    CONF_LAKE,
    CONF_RIVER,
    CONF_RETRIES,
    DEFAULT_FETCH_TIME,
    DEFAULT_RETRIES,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class LakeLevelConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Lake Level."""

    VERSION = 1

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
            data = {
                CONF_RIVER: self._selected_river,
                CONF_LAKE: user_input[CONF_LAKE],
                CONF_FETCH_TIME: user_input[CONF_FETCH_TIME],
                CONF_RETRIES: user_input[CONF_RETRIES],
            }
            return self.async_create_entry(title=f"{data[CONF_LAKE]} ({data[CONF_RIVER]})", data=data)

        try:
            lakes = await self.hass.async_add_executor_job(list_lakes, self._selected_river)
        except Exception as exc:  # pragma: no cover - network failure path
            _LOGGER.exception("Failed to load lakes", exc_info=exc)
            errors["base"] = "cannot_connect"
            lakes = []

        schema = (
            vol.Schema({})
            if errors
            else vol.Schema(
                {
                    vol.Required(CONF_LAKE): vol.In(lakes),
                    vol.Optional(CONF_FETCH_TIME, default=DEFAULT_FETCH_TIME): str,
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
