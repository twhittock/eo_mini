"""Tests for eo_mini api."""
import pytest
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker
from custom_components.eo_mini.api import EOApiClient, EOApiError, EOAuthError
from homeassistant.core import HomeAssistant


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
        status=401,
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
        "https://eoappi.eocharging.com/api/user/",
        json={
            "title": "",
            "firstName": "Firstname",
            "lastName": "Surname",
            "userType": 0,
            "host": 0,
            "email": "user@example.com",
            "mobile": "",
            "foc": 0,
            "isDemo": 0,
            "tcVer": "1.1",
            "ppVer": "1.1",
            "pushUpdated": 1,
            "appSetup": 1,
            "homeHost": 12345,
            "AID": 0,
            "distanceUnits": 0,
            "address": "",
            "countryCode": "GBR",
            "chargeDefs": {
                "chargeStart": 0,
                "chargeEnd": 0,
                "chargeMin": 0,
                "solarMode": 0,
                "timeMode": 0,
            },
            "chargeOpts": {
                "cpid": 56789,
                "scheduleWDay": "TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT00",
                "scheduleWEnd": "TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT00",
                "tariffWDay": "00000000000000000000000000000000000000000000000000",
                "tariffWEnd": "00000000000000000000000000000000000000000000000000",
                "appSchedWDay": "TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT00",
                "appSchedWEnd": "TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT00",
                "solarMin": 6,
                "timeMode": 0,
                "solarMode": 0,
                "opMode": 0,
                "pricePeak": 0.0,
                "priceOffPeak": 0.0,
                "tnid": 0,
                "tariffZone": "N/A",
            },
            "currency": {"code": "GBP", "symbol": "£", "decimals": 2},
        },
    )

    user_data = await api.async_get_user()
    print(user_data)
    assert user_data["chargeOpts"]["cpid"] == 56789
