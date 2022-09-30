"""Sensor platform for EO Mini."""
from datetime import datetime
from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
    SensorDeviceClass,
)
from homeassistant.const import ENERGY_WATT_HOUR, DEVICE_CLASS_ENERGY

from custom_components.eo_mini import EODataUpdateCoordinator

from .const import DOMAIN
from .entity import EOMiniChargerEntity


async def async_setup_entry(hass, entry, async_add_devices):
    "Setup sensor platform."
    coordinator: EODataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        [EOMiniChargerEnergySensor(coordinator, cpid) for cpid in coordinator.cpids]
    )


class EOMiniChargerEnergySensor(EOMiniChargerEntity, SensorEntity):
    """EO Mini Sensor class."""

    _attr_icon = "mdi:ev-station"

    def __init__(self, *args):
        self.entity_description = SensorEntityDescription(
            key=SensorDeviceClass.ENERGY,
            native_unit_of_measurement=ENERGY_WATT_HOUR,
            device_class=DEVICE_CLASS_ENERGY,
            state_class=SensorStateClass.TOTAL,
            name="Consumption",
        )

        self._attr_last_reset = datetime.now()
        self._attr_native_value = 0

        super().__init__(*args)

    def _update_from_coordinator(self) -> None:
        super()._update_from_coordinator()

        c: EODataUpdateCoordinator = self.coordinator
        c.data

    @property
    def name(self):
        "Return the name of the sensor."
        return f"{self.model} - {self.serial} Consumption"

    @property
    def unique_id(self):
        "Return a unique ID to use for this entity."
        return f"{DOMAIN}_charger_{self.serial}_energy"
