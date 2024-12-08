"""Sensor platform for EO Mini."""

from datetime import datetime
from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
    SensorDeviceClass,
)

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
    BinarySensorDeviceClass,
)

from homeassistant.const import UnitOfTime, UnitOfEnergy, STATE_ON, STATE_OFF
from homeassistant.core import callback

from custom_components.eo_mini import EODataUpdateCoordinator

from .const import DOMAIN
from .entity import EOMiniChargerEntity


async def async_setup_entry(hass, entry, async_add_devices):
    "Setup sensor platform."
    coordinator: EODataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        [
            EOMiniChargerSessionEnergySensor(coordinator),
            EOMiniChargerSessionChargingTimeSensor(coordinator),
            EOMiniChargerVehicleConnectedSensor(coordinator),
        ]
    )


class EOMiniChargerSessionEnergySensor(EOMiniChargerEntity, SensorEntity):
    """EO Mini Charger session energy usage sensor class."""

    coordinator: EODataUpdateCoordinator

    _attr_icon = "mdi:ev-station"

    def __init__(self, *args):
        self.entity_description = SensorEntityDescription(
            key=SensorDeviceClass.ENERGY,
            native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL,
            name="Consumption",
        )
        super().__init__(*args)

    @callback
    def _handle_coordinator_update(self) -> None:
        "Handle updated data from the coordinator."
        if self.coordinator.data:
            if self.coordinator.data["ESKWH"] == 0:
                self._attr_last_reset = datetime.fromtimestamp(
                    self.coordinator.data["PiTime"]
                )
                self._attr_native_value = 0
            else:
                # No idea why ESKWH is stored in KWh/s...
                self._attr_native_value = self.coordinator.data["ESKWH"] / 3600
        self.async_write_ha_state()

    @property
    def unique_id(self):
        "Return a unique ID to use for this entity."
        return f"{DOMAIN}_charger_{self.coordinator.serial}_energy"


class EOMiniChargerSessionChargingTimeSensor(EOMiniChargerEntity, SensorEntity):
    """EO Mini Charger session charging time sensor class."""

    coordinator: EODataUpdateCoordinator

    _attr_icon = "mdi:ev-station"

    def __init__(self, *args):
        self.entity_description = SensorEntityDescription(
            key=SensorDeviceClass.DURATION,
            native_unit_of_measurement=UnitOfTime.SECONDS,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.TOTAL_INCREASING,
            name="Charging Time",
        )
        self._attr_native_value = 0
        super().__init__(*args)

    @callback
    def _handle_coordinator_update(self) -> None:
        "Handle updated data from the coordinator."

        if self.coordinator.data:
            if self.coordinator.data["ESKWH"] == 0:
                self._attr_native_value = 0
            else:
                self._attr_native_value = self.coordinator.data["ChargingTime"]
        self.async_write_ha_state()

    @property
    def unique_id(self):
        "Return a unique ID to use for this entity."
        return f"{DOMAIN}_charger_{self.coordinator.serial}_charging_time"


class EOMiniChargerVehicleConnectedSensor(EOMiniChargerEntity, BinarySensorEntity):
    """EO Mini Charger vehicle connected binary sensor class."""

    coordinator: EODataUpdateCoordinator

    _attr_icon = "mdi:car-electric"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

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
        # Check if vehicle is connected based on coordinator data
        if self.coordinator.data is None:
            self._attr_is_on = STATE_OFF
        else:
            self._attr_is_on = STATE_ON
        self.async_write_ha_state()

    @property
    def unique_id(self):
        """Return a unique ID for this entity."""
        return f"{DOMAIN}_charger_{self.coordinator.serial}_vehicle_connected"
