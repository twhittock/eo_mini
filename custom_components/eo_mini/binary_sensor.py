"""Binary Sensor platform for EO Mini."""

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
    BinarySensorDeviceClass,
)
from homeassistant.core import callback

from custom_components.eo_mini import EODataUpdateCoordinator
from .const import DOMAIN
from .entity import EOMiniChargerEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup binary sensor platform."""
    coordinator: EODataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        [
            EOMiniChargerVehicleConnectedSensor(coordinator),
        ]
    )


class EOMiniChargerVehicleConnectedSensor(EOMiniChargerEntity, BinarySensorEntity):
    """EO Mini Charger vehicle connected binary sensor class."""

    coordinator: EODataUpdateCoordinator

    _attr_icon = "mdi:car-electric"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _previous_state = None

    def __init__(self, *args):
        self.entity_description = BinarySensorEntityDescription(
            key=BinarySensorDeviceClass.CONNECTIVITY,
            device_class=BinarySensorDeviceClass.CONNECTIVITY,
            name="Vehicle Connected",
        )
        self._attr_is_on = False
        super().__init__(*args)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_is_on = self.coordinator.live_session
        self.async_write_ha_state()

    @property
    def unique_id(self):
        """Return a unique ID for this entity."""
        return f"{DOMAIN}_charger_{self.coordinator.serial}_vehicle_connected"
