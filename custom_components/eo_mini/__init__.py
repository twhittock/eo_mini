"""
Custom integration to integrate EO Mini with Home Assistant.

For more details about this integration, please refer to
https://github.com/twhittock/eo_mini
"""
import asyncio
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config, HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import EOApiClient, EOAuthError

from .const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    DOMAIN,
    PLATFORMS,
    STARTUP_MESSAGE,
)

SCAN_INTERVAL = timedelta(minutes=1)

_LOGGER: logging.Logger = logging.getLogger(__package__)


def eo_model(hub_serial: str):
    "Get a model from the serial number"
    # if hub_serial.startswith("EO-"):
    #     return "EO Mini"
    if hub_serial.startswith("EMP-"):
        return "EO Mini Pro"
    if hub_serial.startswith("EM-"):
        return "EO Mini Pro 2"

    return "Unknown EO model"


# pylint: disable-next=unused-argument
async def async_setup(hass: HomeAssistant, config: Config):
    "Setting up this integration using YAML is not supported."
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    username = entry.data.get(CONF_USERNAME)
    password = entry.data.get(CONF_PASSWORD)

    session = async_get_clientsession(hass)
    client = EOApiClient(username, password, session)

    coordinator = EODataUpdateCoordinator(hass, client=client)
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await coordinator.async_config_entry_first_refresh()

    for platform in PLATFORMS:
        coordinator.platforms.append(platform)
        hass.async_add_job(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


class EODataUpdateCoordinator(DataUpdateCoordinator):
    "Class to manage fetching data from the API."

    api: EOApiClient

    def __init__(self, hass: HomeAssistant, client: EOApiClient) -> None:
        "Initialize."
        self.api = client
        self.platforms = []
        self.device = {}
        self.serial = ""
        self.model = ""
        self._user_data = None
        self._minis_list = None

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def _async_update_data(self):
        """Update data via library."""
        try:
            if not self._user_data:
                self._user_data = await self.api.async_get_user()

            self._minis_list = await self.api.async_get_list()
            assert len(self._minis_list) == 1
            self.device = self._minis_list[0]
            self.serial = self.device["hubSerial"]
            self.model = eo_model(self.serial)

            self.data = await self.api.async_get_session()

            self.async_update_listeners()
        except EOAuthError as exception:
            raise ConfigEntryAuthFailed from exception
        except Exception as exception:
            raise UpdateFailed() from exception


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in coordinator.platforms
            ]
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
