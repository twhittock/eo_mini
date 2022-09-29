"""Adds config flow for Blueprint."""
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession
import voluptuous as vol
import logging

from .api import EOApiClient, EOAuthError
from .const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    DOMAIN,
    PLATFORMS,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)


class EOMiniFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    "Config flow for EO Mini."

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        "Initialize."
        self._errors = {}
        self._description_placeholders = {}

    async def async_step_user(self, user_input=None):
        "Handle a flow initialized by the user."
        self._errors = {}
        self._description_placeholders = {}

        # Uncomment the next 2 lines if only a single instance of the integration is allowed:
        # if self._async_current_entries():
        #     return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            try:
                session = async_create_clientsession(self.hass)
                client = EOApiClient(
                    user_input[CONF_USERNAME], user_input[CONF_PASSWORD], session
                )
                await client.async_get_user()

                return self.async_create_entry(
                    title=user_input[CONF_USERNAME], data=user_input
                )
            except EOAuthError:
                _LOGGER.warning("Invalid credentials during config flow")
                self._errors["base"] = "auth"
            except Exception as ex:  # pylint: disable=broad-except
                _LOGGER.warning("Unexpected error config flow: %s", str(ex))
                self._description_placeholders["credential_error"] = str(ex)
                self._errors["base"] = "credential_fail"

            return await self._show_config_form(user_input)

        user_input = {}
        # Provide defaults for form
        user_input[CONF_USERNAME] = ""
        user_input[CONF_PASSWORD] = ""

        return await self._show_config_form(user_input)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return EOMiniOptionsFlowHandler(config_entry)

    async def _show_config_form(self, user_input):  # pylint: disable=unused-argument
        """Show the configuration form to edit location data."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME, default=user_input[CONF_USERNAME]): str,
                    vol.Required(CONF_PASSWORD, default=user_input[CONF_PASSWORD]): str,
                }
            ),
            errors=self._errors,
            description_placeholders=self._description_placeholders,
        )


class EOMiniOptionsFlowHandler(config_entries.OptionsFlow):
    "EO Mini config flow options handler."

    def __init__(self, config_entry):
        "Initialize."
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None):  # pylint: disable=unused-argument
        "Manage the options."
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        "Handle a flow initialized by the user."
        if user_input is not None:
            self.options.update(user_input)
            return await self._update_options()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(x, default=self.options.get(x, True)): bool
                    for x in sorted(PLATFORMS)
                }
            ),
        )

    async def _update_options(self):
        """Update config entry options."""
        return self.async_create_entry(
            title=self.config_entry.data.get(CONF_USERNAME), data=self.options
        )
