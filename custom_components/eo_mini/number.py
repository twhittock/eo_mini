from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.const import UnitOfElectricCurrent
from homeassistant.core import callback

from custom_components.eo_mini import EODataUpdateCoordinator

from .const import DOMAIN
from .entity import EOMiniChargerEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup number platform."""
    coordinator: EODataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        [
            EOMiniSolarMinCurrent(coordinator),
        ]
    )


class EOMiniSolarMinCurrent(EOMiniChargerEntity, NumberEntity):
    """Number entity to represent the solar minimum rate of charge."""

    coordinator: EODataUpdateCoordinator

    def __init__(self, *args):
        self.entity_description = NumberEntityDescription(
            key="Minimum_charge_current",
            name="Minimum charge current",
            native_step=1,
            native_min_value=6,
            native_max_value=32,
            native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
            device_class=NumberDeviceClass.CURRENT,
            icon="mdi:current-ac",
        )
        super().__init__(*args)
        self._attr_mode = NumberMode.BOX

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.coordinator.charge_options:
            self._attr_native_value = int(self.coordinator.charge_options["solarMin"])
        self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Set new minimum solar charge current value."""
        await self.coordinator.api.async_solar_min_charge_current(
            int(value), self.coordinator.charge_options
        )
        await self.coordinator.async_refresh()

    @property
    def unique_id(self):
        "Return a unique ID to use for this entity."
        return f"{DOMAIN}_charger_{self.coordinator.serial}_solar_min_charge"
