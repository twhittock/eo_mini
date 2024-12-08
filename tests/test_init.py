"Test integration_blueprint setup process."
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.config_entries import ConfigEntryState
import pytest
import aiohttp
from unittest.mock import patch
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.eo_mini import (
    EODataUpdateCoordinator,
    async_reload_entry,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.eo_mini.const import DOMAIN
from tests import json_load_file

from .const import MOCK_CONFIG


async def test_setup_unload_and_reload_entry(hass):
    """Test entry setup and unload."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = MockConfigEntry(
        domain=DOMAIN, data=MOCK_CONFIG, entry_id="test", state=ConfigEntryState.LOADED
    )

    with patch(
        "custom_components.eo_mini.EOApiClient.async_get_list",
        return_value=json_load_file("list.json"),
    ), patch(
        "custom_components.eo_mini.EOApiClient.async_get_user",
        return_value=json_load_file("user.json"),
    ), patch(
        "custom_components.eo_mini.EOApiClient.async_get_session",
        return_value=json_load_file("session_charging.json"),
    ), patch(
        "custom_components.eo_mini.EOApiClient.async_get_session_liveness",
        return_value=json_load_file("session_liveness.json"),
    ):
        # Set up the entry and assert that the values set during setup are where we expect
        # them to be. Because we have patched the BlueprintDataUpdateCoordinator.async_get_data
        # call, no code from custom_components/eo_mini/api.py actually runs.
        assert await async_setup_entry(hass, config_entry)
        assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]
        assert isinstance(
            hass.data[DOMAIN][config_entry.entry_id], EODataUpdateCoordinator
        )

        # Reload the entry and assert that the data from above is still there
        assert await async_reload_entry(hass, config_entry) is None
        assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]
        assert isinstance(
            hass.data[DOMAIN][config_entry.entry_id], EODataUpdateCoordinator
        )

        # Unload the entry and verify that the data has been removed
        assert await async_unload_entry(hass, config_entry)
        assert config_entry.entry_id not in hass.data[DOMAIN]


async def test_setup_entry_exception(hass):
    """Test ConfigEntryNotReady when API raises an exception during entry setup."""
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")

    # In this case we are testing the condition where async_setup_entry raises
    # ConfigEntryNotReady when the API raises an error during login
    with patch(
        "custom_components.eo_mini.EOApiClient.async_get_user",
        side_effect=aiohttp.ClientError,
    ), pytest.raises(ConfigEntryNotReady):
        assert await async_setup_entry(hass, config_entry)
