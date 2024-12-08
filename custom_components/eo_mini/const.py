"""Constants for EO."""
# Base component constants
NAME = "EO Mini"
DOMAIN = "eo_mini"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.0.2"
ATTRIBUTION = "Data provided by EO"
ISSUE_URL = "https://github.com/twhittock/eo_mini/issues"

# Platforms
SENSOR = "sensor"
SWITCH = "switch"
BINARY_SENSOR = "binary_sensor"
PLATFORMS = [SENSOR, BINARY_SENSOR, SWITCH]


# Configuration and options
CONF_ENABLED = "enabled"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_POLL_INTERVAL = "poll_interval"
DEFAULT_POLL_INTERVAL = 5  # minutes


STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
