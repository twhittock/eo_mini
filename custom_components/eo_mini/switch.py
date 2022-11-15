import asyncio
import logging

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.core import callback

from custom_components.eo_mini import EODataUpdateCoordinator

from .const import DOMAIN
from .entity import EOMiniChargerEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, entry, async_add_devices):
    "Setup sensor platform."
    coordinator: EODataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        [
            EOMiniLockSwitch(coordinator),
        ]
    )


class EOMiniLockSwitch(EOMiniChargerEntity, SwitchEntity):
    "Switch entity to represent the enabled/disabled (locked) status of the charger"
    coordinator: EODataUpdateCoordinator

    def __init__(self, *args):
        self.entity_description = SwitchEntityDescription(
            key="Lock",
            name="Lock",
            device_class=SwitchDeviceClass.SWITCH,
            icon="mdi:lock",
        )
        super().__init__(*args)

    @callback
    def _handle_coordinator_update(self) -> None:
        "Handle updated data from the coordinator."
        if self.coordinator.device:
            _LOGGER.debug(
                "update: state: %r, api: %r",
                self._attr_is_on,
                bool(self.coordinator.device["isDisabled"]),
            )
            self._attr_is_on = bool(self.coordinator.device["isDisabled"])
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs):
        await self.coordinator.api.async_post_disable(
            self.coordinator.device["address"]
        )

        # Get the state back from the API
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs):
        await self.coordinator.api.async_post_enable(self.coordinator.device["address"])

        # Get the state back from the API
        await self.coordinator.async_refresh()

    @property
    def unique_id(self):
        "Return a unique ID to use for this entity."
        return f"{DOMAIN}_charger_{self.coordinator.serial}_locked"
