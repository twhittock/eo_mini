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
    "Setup switch platform."
    coordinator: EODataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        [
            EOMiniLockSwitch(coordinator),
            EOMiniOffPeakSwitch(coordinator),
            EOMiniSolarSwitch(coordinator),
            EOMiniScheduledSwitch(coordinator),
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


class EOMiniOffPeakSwitch(EOMiniChargerEntity, SwitchEntity):
    "Switch entity to represent the enabled/disabled status of Off-Peak charging"
    coordinator: EODataUpdateCoordinator

    def __init__(self, *args):
        self.entity_description = SwitchEntityDescription(
            key="Off_Peak_Charging",
            name="Off Peak Charging",
            device_class=SwitchDeviceClass.SWITCH,
            icon="mdi:sort-clock-ascending-outline",
        )
        super().__init__(*args)

    @callback
    def _handle_coordinator_update(self) -> None:
        "Handle updated data from the coordinator."
        if self.coordinator.charge_options:
            _LOGGER.debug(
                "update: state: %r, api: %r",
                self._attr_is_on,
                bool(self.coordinator.charge_options["opMode"]),
            )
            self._attr_is_on = bool(self.coordinator.charge_options["opMode"])
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs):
        await self.coordinator.api.async_update_charge_options(
            "opMode", 1, self.coordinator.charge_options
        )

        # Get the state back from the API
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs):
        await self.coordinator.api.async_update_charge_options(
            "opMode", 0, self.coordinator.charge_options
        )

        # Get the state back from the API
        await self.coordinator.async_refresh()

    @property
    def unique_id(self):
        "Return a unique ID to use for this entity."
        return f"{DOMAIN}_charger_{self.coordinator.serial}_offpeak"


class EOMiniSolarSwitch(EOMiniChargerEntity, SwitchEntity):
    "Switch entity to represent the enabled/disabled status of Solar charging"
    coordinator: EODataUpdateCoordinator

    def __init__(self, *args):
        self.entity_description = SwitchEntityDescription(
            key="Solar_Charging",
            name="Solar Charging",
            device_class=SwitchDeviceClass.SWITCH,
            icon="mdi:solar-power",
        )
        super().__init__(*args)

    @callback
    def _handle_coordinator_update(self) -> None:
        "Handle updated data from the coordinator."
        if self.coordinator.charge_options:
            _LOGGER.debug(
                "update: state: %r, api: %r",
                self._attr_is_on,
                bool(self.coordinator.charge_options["solarMode"]),
            )
            self._attr_is_on = bool(self.coordinator.charge_options["solarMode"])
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs):
        await self.coordinator.api.async_update_charge_options(
            "solarMode", 1, self.coordinator.charge_options
        )

        # Get the state back from the API
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs):
        await self.coordinator.api.async_update_charge_options(
            "solarMode", 0, self.coordinator.charge_options
        )

        # Get the state back from the API
        await self.coordinator.async_refresh()

    @property
    def unique_id(self):
        "Return a unique ID to use for this entity."
        return f"{DOMAIN}_charger_{self.coordinator.serial}_solar"


class EOMiniScheduledSwitch(EOMiniChargerEntity, SwitchEntity):
    "Switch entity to represent the enabled/disabled status of Scheduled charging"
    coordinator: EODataUpdateCoordinator

    def __init__(self, *args):
        self.entity_description = SwitchEntityDescription(
            key="Scheduled_Charging",
            name="Scheduled Charging",
            device_class=SwitchDeviceClass.SWITCH,
            icon="mdi:calendar-clock",
        )
        super().__init__(*args)

    @callback
    def _handle_coordinator_update(self) -> None:
        "Handle updated data from the coordinator."
        if self.coordinator.charge_options:
            _LOGGER.debug(
                "update: state: %r, api: %r",
                self._attr_is_on,
                bool(self.coordinator.charge_options["timeMode"]),
            )
            self._attr_is_on = bool(self.coordinator.charge_options["timeMode"])
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs):
        await self.coordinator.api.async_update_charge_options(
            "timeMode", 1, self.coordinator.charge_options
        )

        # Get the state back from the API
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs):
        await self.coordinator.api.async_update_charge_options(
            "timeMode", 0, self.coordinator.charge_options
        )

        # Get the state back from the API
        await self.coordinator.async_refresh()

    @property
    def unique_id(self):
        "Return a unique ID to use for this entity."
        return f"{DOMAIN}_charger_{self.coordinator.serial}_scheduled"
