"EOMiniChargerEntity to hold all charger information"
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.eo_mini import EODataUpdateCoordinator

from .const import DOMAIN


def eo_model(hub_serial: str):
    "Get a model from the serial number"
    # if hub_serial.startswith("EO-"):
    #     return "EO Mini"
    if hub_serial.startswith("EMP-"):
        return "EO Mini Pro"
    if hub_serial.startswith("EM-"):
        return "EO Mini Pro 2"

    return "Unknown EO model"


class EOMiniChargerEntity(CoordinatorEntity):
    "Base type for entities for the charger device"

    def __init__(self, coordinator: EODataUpdateCoordinator, cpid: int):
        super().__init__(coordinator)
        self.cpid = cpid
        self.serial = ""
        self.model = ""
        self._update_from_coordinator()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._update_from_coordinator()
        self.async_write_ha_state()

    def _update_from_coordinator(self) -> None:
        "Get the data from the coordinator into local fields"
        data = self.coordinator.get_cp_data(self.cpid)
        self.serial = data["hubSerial"]
        self.model = eo_model(self.serial)

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return f"{DOMAIN}_{self.serial}"

    @property
    def device_name(self):
        "Return the name of the device"
        return f"{self.model} - {self.serial}"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": self.device_name,
            "serial": self.serial,
            "model": self.model,
            "manufacturer": "EO",
        }

    @property
    def extra_state_attributes(self):
        "Return the state attributes."
        return {
            "cpid": str(self.cpid),
            "integration": DOMAIN,
        }
