from posixpath import join as urljoin
import json
import time

import requests
from requests.auth import HTTPBasicAuth

from uaa_bot import config


class UAAError(RuntimeError):
    """
    This exception is raised when the UAA API returns a status code >= 400
    Attributes:
        response:   The full response object from requests that was returned
        error:  The body of the response json decoded
    Args:
        response: The full response object that is causing this exception to be raised
    """

    def __init__(self, response):
        self.response = response
        self.error = json.loads(response.text)

        message = self.error["error_description"]

        super(UAAError, self).__init__(message)


class UAAClient:
    """
    A minimal client for the UAA API
    Args:
        base_url: The URL to your UAA instance
        [uaa_config]: Optional UAA config if the default is not provided in env variables
    """

    def __init__(self, token: str = None, uaa_config: dict = config.uaa):
        self.token = token
        self.uaa_config = uaa_config

    @property
    def uaa_config(self):
        return self._uaa_config

    @uaa_config.setter
    def uaa_config(self, value):
        uaa_config = {}
        for k, v in config.uaa.items():
            uaa_config[k] = value.get(k, v)
        self._uaa_config = uaa_config

    @property
    def base_url(self):
        if not self.uaa_config["UAA_BASE_URL"]:
            return "None"
        return self.uaa_config["UAA_BASE_URL"]

    @property
    def client_id(self):
        if not self.uaa_config["UAA_CLIENT_ID"]:
            return None
        return self.uaa_config["UAA_CLIENT_ID"]

    @property
    def client_secret(self):
        if not self.uaa_config["UAA_CLIENT_SECRET"]:
            return None
        return self.uaa_config["UAA_CLIENT_SECRET"]

    def _get_past_epoch_in_ms(self, days_ago: int) -> int:
        """
        Return the epoch (milliseconds) integer based on the number of days ago
        Args:
            days_ago: Integer of the number of days ago back
        Returns:
            int: the epoch of the day n number of days ago.
        """
        current_epoch = int(time.time() * 1000)
        subtract_days = 60 * 60 * 24 * 1000 * days_ago
        return current_epoch - subtract_days

    def _request(
        self,
        resource,
        method,
        body=None,
        params=None,
        auth=None,
        headers=None,
        is_json=True,
    ):
        """
        Make a request to the UAA API.
        Args:
            resource: The API method you wish to call (example: '/Users')
            method: The method to use when making the request GET/POST/etc
            body (optional): An json encodeable object which will be included as the body
            of the request
            params (optional): Query string parameters that are included in the request
            auth (optional): A requests.auth.* instance
            headers (optional): A list of headers to include in the request
        Raises:
            UAAError: An error occured making the request
        Returns:
            dict:   The parsed json response
        """
        if headers is None:
            headers = {}

        endpoint = urljoin(self.base_url.rstrip("/"), resource.lstrip("/"))
        # convert HTTP method to requests' method (ie requests.post)
        requests_method = getattr(requests, method.lower())

        int_headers = {}

        if self.token and auth is None:
            int_headers["Authorization"] = "Bearer " + self.token

        for kk, vv in headers.items():
            int_headers[kk] = vv

        response = requests_method(
            endpoint,
            params=params,
            json=body,
            headers=int_headers,
            auth=auth,
        )

        # if we errored raise an exception
        if response.status_code >= 400:
            raise UAAError(response)

        if is_json:
            return json.loads(response.text)
        return response.text

    def _paginated_request(
        self,
        resource,
        method,
        prev_resources: list = [],
        body=None,
        params=None,
        auth=None,
        headers=None,
        is_json=True,
    ):
        if "startIndex" not in params:
            params["startIndex"] = 1

        response = self._request(
            resource,
            method,
            body=body,
            params=params,
            auth=auth,
            headers=headers,
            is_json=is_json,
        )

        resources = response.get("resources")
        start_index = response.get("startIndex")
        items_per_page = response.get("itemsPerPage")
        total_results = response.get("totalResults")

        resources.extend(prev_resources)

        if (start_index + items_per_page - 1) < total_results:
            params["startIndex"] = start_index + items_per_page

            return self._paginated_request(
                resource,
                method,
                prev_resources=resources,
                body=body,
                params=params,
                auth=auth,
                headers=headers,
                is_json=is_json,
            )
        else:
            return {
                "startIndex": start_index,
                "itemsPerPage": items_per_page,
                "resources": resources,
                "totalResults": total_results,
            }

    def authenticate(self) -> None:
        """
        Sets the client credentials token property
        Raises:UAAError: there was an error getting the token
        """
        response = self._request(
            "/oauth/token",
            "POST",
            params={"grant_type": "client_credentials", "response_type": "token"},
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
        )
        self.token = response.get("access_token", None)

    def list_expiring_users(
        self,
        days_ago: int = 90,
        days_range: int = 1,
        start_of_day: int = None,
        end_of_day: int = None,
        **kwargs,
    ) -> dict:
        """
        Gets a list of users based on last long in for the day n number of days ago
        Args:
            days_ago: int: The number of days ago
        Raises:UAAError: there was an error getting users
        Returns:
            dict: the list of users with last login
        """
        params = kwargs.get("params", {})

        if start_of_day is None:
            start_of_day = self._get_past_epoch_in_ms(days_ago + days_range)

        if end_of_day is None:
            end_of_day = self._get_past_epoch_in_ms(days_ago)

        # Param filters for UAA SCIM
        scim_origin = 'origin eq "cloud.gov"'
        scim_active = "active eq true"
        # Note - UAA API docs say "lastLogonTime" but the field attribute
        # is actually "last_logon_success_time" per https://github.com/cloudfoundry/uaa/issues/542
        scim_last_logon = (
            f"last_logon_success_time ge {start_of_day}"
            f" and "
            f"last_logon_success_time le {end_of_day}"
        )
        scim_filter = {
            "filter": f"{scim_origin} and {scim_active} and {scim_last_logon}"
        }
        params.update(scim_filter)

        response = self._paginated_request(
            "/Users",
            "GET",
            params=params,
        )

        return response

    def deactivate_user(self, user: dict) -> dict:
        """
        Deactivate a user
        Args:
            user: dict: The user object
        Returns:
            dict: Returns the response dict after updating user
        """
        user_guid = user.get("id")
        meta = user.get("meta", {})
        version = meta.get("version")
        user["active"] = False

        response = self._request(
            f"/Users/{user_guid}",
            "PUT",
            body=user,
            headers={"If-Match": f"{version}", "Content-Type": "application/json"},
        )

        return response
