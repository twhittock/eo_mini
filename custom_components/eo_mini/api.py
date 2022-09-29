"EO API Client."
from homeassistant.config_entries import ConfigEntry
import logging
import aiohttp
import async_timeout

TIMEOUT = 10

_LOGGER: logging.Logger = logging.getLogger(__package__)


class EOApiError(Exception):
    "Exception for when the EO API doesn't return an expected status code"

    def __init__(self, status, message):
        super().__init__(self)
        self.status = status
        self.message = message

    def __str__(self):
        return f"{self.status}: {self.message}"


class EOAuthError(Exception):
    "Exception for when the EO API can't validate the user credentials"

    def __init__(self, message):
        super().__init__(self)
        self.message = message

    def __str__(self):
        return self.message


def trace_callback(message):
    "Generate a callback with the given message, to help trace aiohttp requests"

    async def tracer(_session, _context, params):
        "Log the request lifecycle"
        _LOGGER.debug("%s with params: %s", message, params)

    return tracer


class EOApiClient:
    "EO Mini API"
    base_url = "https://eoappi.eocharging.com"

    def __init__(
        self, username: str, password: str, session: aiohttp.ClientSession
    ) -> None:
        "Initialise."

        trace = aiohttp.TraceConfig()
        trace.on_request_start.append(trace_callback("Request start"))
        trace.on_request_chunk_sent.append(trace_callback("Request sent chunk"))
        trace.on_request_end.append(trace_callback("Request end"))
        trace.on_request_exception.append(trace_callback("Request exception"))
        trace.on_request_headers_sent.append(trace_callback("Request sent headers"))
        trace.on_request_redirect.append(trace_callback("Request redirected"))
        trace.freeze()

        session.trace_configs.append(trace)

        self._session = session
        self._username = username
        self._password = password
        self._token = None

    async def async_get_user(self) -> dict:
        "Get the user information held by EO - including the changer we will be querying"
        return await self._async_api_wrapper("get", f"{self.base_url}/api/user/")

    async def _async_api_wrapper(
        self, method: str, url: str, _reissue=False, **kwargs
    ) -> dict:
        "Handle authorization and status checks"

        if not self._token:
            response = await self._session.post(
                f"{self.base_url}/Token",
                data=f"grant_type=password&username={self._username}&password={self._password}",
            )

            if response.status == 200:
                json = await response.json()
                self._token = json["access_token"]
            elif response.status == 400:
                json = await response.json()
                raise EOAuthError(json["error_description"])
            else:
                raise EOApiError(response.status, await response.content.read())

        headers = {
            aiohttp.hdrs.AUTHORIZATION: f"Bearer {self._token}",
        }

        async with async_timeout.timeout(TIMEOUT):
            if method == "get":
                response = await self._session.get(url, headers=headers, **kwargs)

            elif method == "put":
                response = await self._session.put(url, headers=headers, **kwargs)

            elif method == "patch":
                response = await self._session.patch(url, headers=headers, **kwargs)

            elif method == "post":
                response = await self._session.post(url, headers=headers, **kwargs)

        if response.status == 200:
            return await response.json()
        elif response.status == 400:
            # Handle expired/invalid tokens
            if not _reissue:
                self._token = None  # erase the invalid token.
                return self._async_api_wrapper(method, url, _reissue=True, **kwargs)

        raise EOApiError(response.status, response.content.read())
