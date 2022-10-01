"EOMiniChargerEntity to hold all charger information"
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.eo_mini import EODataUpdateCoordinator

from .const import DOMAIN


class EOMiniChargerEntity(CoordinatorEntity):
    "Base type for entities for the charger device"

    def __init__(self, coordinator: EODataUpdateCoordinator):
        super().__init__(coordinator)

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self._handle_coordinator_update()

    @property
    def device_unique_id(self):
        """Return a unique ID to use for this entity."""
        return f"{DOMAIN}_{self.coordinator.serial}"

    @property
    def device_name(self):
        "Return the name of the device"
        return f"{self.coordinator.model} - {self.coordinator.serial}"

    @property
    def name(self):
        "Return the name of the sensor."
        return f"{self.device_name} {self.entity_description.name}"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.device_unique_id)},
            "name": self.device_name,
            "serial": self.coordinator.serial,
            "model": self.coordinator.model,
            "manufacturer": "EO",
        }

    @property
    def extra_state_attributes(self):
        "Return the state attributes."
        return {
            "integration": DOMAIN,
        }
