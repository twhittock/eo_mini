"""Tests for eo_mini api."""
import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker
from custom_components.eo_mini.api import EOApiClient, EOAuthError
from tests import json_load_file


def add_successful_auth_request(aioclient_mock: AiohttpClientMocker):
    "Add the auth request we must issue to get the bearer token for API calls"
    aioclient_mock.post(
        "https://eoappi.eocharging.com/Token",
        json={
            "access_token": "test_token_data_123498712349862314987",
            "token_type": "bearer",
            "expires_in": 100000,
            "userName": "test@example.com",
            ".issued": "Thu, 29 Sep 2022 12:53:41 GMT",
            ".expires": "Sat, 29 Oct 2022 12:53:41 GMT",
        },
    )


async def test_auth_failure(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker):
    "Authorisation fails due to incorrect credentials"

    # To test the api submodule, we first create an instance of our API client
    api = EOApiClient("test", "test", async_get_clientsession(hass))

    aioclient_mock.post(
        "https://eoappi.eocharging.com/Token",
        status=400,
        json={
            "error": "invalid_grant",
            "error_description": "The user name or password is incorrect.",
        },
    )

    with pytest.raises(EOAuthError) as auth_error:
        await api.async_get_user()
    assert auth_error.value.message == "The user name or password is incorrect."


async def test_get_user_data_ok(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
):
    "Authorisation succeeds"

    # To test the api submodule, we first create an instance of our API client
    api = EOApiClient("test", "test", async_get_clientsession(hass))

    add_successful_auth_request(aioclient_mock)

    aioclient_mock.get(
        "https://eoappi.eocharging.com/api/user",
        json=json_load_file("user.json"),
    )

    user_data = await api.async_get_user()
    print(user_data)
    assert user_data["chargeOpts"]["cpid"] == 56789
