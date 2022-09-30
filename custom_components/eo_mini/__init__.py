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
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import EOApiClient

from .const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    DOMAIN,
    PLATFORMS,
    STARTUP_MESSAGE,
)

SCAN_INTERVAL = timedelta(minutes=30)

_LOGGER: logging.Logger = logging.getLogger(__package__)


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
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    for platform in PLATFORMS:
        coordinator.platforms.append(platform)
        hass.async_add_job(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


class EODataUpdateCoordinator(DataUpdateCoordinator):
    "Class to manage fetching data from the API."

    def __init__(self, hass: HomeAssistant, client: EOApiClient) -> None:
        "Initialize."
        self.api = client
        self.platforms = []
        self._user_data = None
        self._minis_list = None

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def _async_update_data(self):
        """Update data via library."""
        try:
            if not self._user_data:
                self._user_data = await self.api.async_get_user()

            if not self._minis_list:
                self._minis_list = await self.api.async_get_list()

            self.async_update_listeners()

            # TODO: get charge history
        except Exception as exception:
            raise UpdateFailed() from exception

    @property
    def cpids(self):
        "List of charge point IDs in the account"
        # It feels like there should be multiple, but the only way
        # I can get at this is to get the cpid from the user account?!
        # No cpid info on the list of minis endpoint. Weird.
        # We'll act like there could be more just in case.
        yield self._user_data["chargeOpts"]["cpid"]

    def get_cp_data(self, cpid):
        "Get the charge point data for the given cpid"
        # Again this is a bit of a lie, but surely the cpid should
        # match up with something in the charge data.. but no.
        # Anyway, I can only see how 1 charger could be associated
        # with an account for now.
        assert len(self._minis_list) == 1
        assert cpid == self._user_data["chargeOpts"]["cpid"]
        return self._minis_list[0]


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
