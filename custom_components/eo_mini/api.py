"EO API Client."
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


class EOApiClient:
    "EO Mini API"
    base_url = "https://eoappi.eocharging.com"

    def __init__(
        self, username: str, password: str, session: aiohttp.ClientSession
    ) -> None:
        """Sample API Client."""
        self._username = username
        self._password = password
        self._session = session

    async def async_get_user(self) -> dict:
        "Get the user information held by EO - including the changer we will be querying"
        return await self._async_api_wrapper("get", f"{self.base_url}/api/user/")

    async def _async_api_wrapper(
        self, method: str, url: str, _reissue=False, **kwargs
    ) -> dict:
        "Handle authorization and status checks"

        if aiohttp.hdrs.AUTHORIZATION not in self._session.headers:
            response = await self._session.post(
                f"{self.base_url}/Token",
                data=f"grant_type=password&username=${self._username}&password=${self._password}",
            )

            if response.status == 200:
                json = await response.json()
                token = json["access_token"]
                self._session.headers[aiohttp.hdrs.AUTHORIZATION] = f"Bearer {token}"
            elif response.status == 400:
                json = await response.json()
                raise EOAuthError(json["error_description"])
            else:
                raise EOApiError(response.status, await response.content.read())

        async with async_timeout.timeout(TIMEOUT):
            if method == "get":
                response = await self._session.get(url, **kwargs)

            elif method == "put":
                response = await self._session.put(url, **kwargs)

            elif method == "patch":
                response = await self._session.patch(url, **kwargs)

            elif method == "post":
                response = await self._session.post(url, **kwargs)

        if response.status == 200:
            return await response.json()
        elif response.status == 401:
            # Handle expired tokens
            if not _reissue:
                del self._session.headers[aiohttp.hdrs.AUTHORIZATION]
                return self._async_api_wrapper(method, url, _reissue=True, **kwargs)

        raise EOApiError(response.status, response.content.read())
