"""Lake Level Home Assistant integration."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    CONF_FETCH_TIME,
    CONF_FETCH_TIMES,
    CONF_RETRIES,
    CONF_UPDATES_PER_DAY,
    DEFAULT_FETCH_TIME,
    DEFAULT_RETRIES,
    DOMAIN,
)
from .coordinator import LakeLevelCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    config = dict(entry.data)
    config.update(entry.options)

    coordinator = LakeLevelCoordinator(hass, config)

    try:
        await coordinator.async_config_entry_first_refresh()
    except ConfigEntryNotReady:
        raise
    except Exception as exc:  # pragma: no cover - defensive path
        raise ConfigEntryNotReady(str(exc)) from exc

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "coordinator": coordinator,
    }

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if entry.version == 1:
        data = dict(entry.data)
        fetch_time = data.pop(CONF_FETCH_TIME, DEFAULT_FETCH_TIME)
        retries = data.get(CONF_RETRIES, DEFAULT_RETRIES)
        data[CONF_FETCH_TIMES] = [fetch_time]
        data[CONF_UPDATES_PER_DAY] = 1
        data[CONF_RETRIES] = retries
        entry.version = 2
        hass.config_entries.async_update_entry(entry, data=data, options={})
        _LOGGER.debug("Migrated Lake Level entry to version 2")
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
