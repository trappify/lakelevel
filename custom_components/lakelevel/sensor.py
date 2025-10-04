"""Lake Level sensor platform."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_LAKE, CONF_RIVER, DOMAIN
from .coordinator import LakeLevelCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: LakeLevelCoordinator = data["coordinator"]
    async_add_entities([LakeLevelSensor(coordinator, entry.data)])


class LakeLevelSensor(CoordinatorEntity[LakeLevelCoordinator], SensorEntity):
    _attr_device_class = SensorDeviceClass.DISTANCE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "m"

    def __init__(self, coordinator: LakeLevelCoordinator, config: dict[str, Any]) -> None:
        super().__init__(coordinator)
        self._lake = config[CONF_LAKE]
        self._river = config[CONF_RIVER]
        self._attr_name = f"{self._lake} water level"
        self._attr_unique_id = f"lakelevel_{self._river}_{self._lake}".lower().replace(" ", "_")

    @property
    def native_value(self) -> Decimal | None:
        if not self.coordinator.last_update_success:
            return None
        data = self.coordinator.data
        return data.level_m if data else None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        data = self.coordinator.data
        if not data:
            return None
        return {
            "river": data.river,
            "timestamp": data.timestamp,
        }
