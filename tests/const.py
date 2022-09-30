"""Constants for EO Mini tests."""
from custom_components.eo_mini.const import CONF_PASSWORD, CONF_USERNAME

# Mock config data to be used across multiple tests
MOCK_CONFIG = {CONF_USERNAME: "test_username", CONF_PASSWORD: "test_password"}

EXAMPLE_USER = {
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
}

EXAMPLE_LIST_MINIS = [
    {
        "address": "0000ABCD",
        "isDisabled": 0,
        "ct1": 0.0,
        "ct2": 0.0,
        "ct3": 0.0,
        "advertisedRate": 0.0,
        "voltage": 0,
        "timezone": "Greenwich Standard Time",
        "chargerAddress": "0000ABCD",  # actually the same as address for me
        "hubAddress": "12345678",
        "chargerModel": 310,
        "hubModel": 202,
        "hubSerial": "EM-12345",
    }
]
