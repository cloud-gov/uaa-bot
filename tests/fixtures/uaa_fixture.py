import pytest
from math import ceil
import time
from random import randint

from fixtures.config import authenticated_response, base_url


def get_epoch_days_ago(days_ago: int, current_time: float) -> int:
    return int(current_time) - (days_ago * 60 * 60 * 24 * 1000)


def build_url(path, start_of_day: int = None, end_of_day: int = None, **params):
    params_list = []

    if params:
        for k, v in params.items():
            params_list.append(f"{k}={v}")

    params_string = "&".join(params_list)

    if not start_of_day and not end_of_day:
        if params_string:
            return f"{base_url}{path}?{params_string}"
        else:
            return f"{base_url}{path}"

    filter_origin = 'origin eq "cloud.gov"'
    filter_active = "active eq true"
    filter_last_logon = (
        f"last_logon_success_time ge {start_of_day}"
        f" and "
        f"last_logon_success_time le {end_of_day}"
    )

    filter_params = f"{filter_origin} and {filter_active} and {filter_last_logon}"

    if params_string:
        return f"{base_url}{path}?filter={filter_params}&{params_string}"
    else:
        return f"{base_url}{path}?filter={filter_params}"

def build_url_no_filter(path, start_of_day: int = None, end_of_day: int = None, **params):
    params_list = []

    if params:
        for k, v in params.items():
            params_list.append(f"{k}={v}")

    params_string = "&".join(params_list)

    if not start_of_day and not end_of_day:
        if params_string:
            return f"{base_url}{path}?{params_string}"
        else:
            return f"{base_url}{path}"

    filter_last_logon = (
        f"last_logon_success_time ge {start_of_day}"
        f" and "
        f"last_logon_success_time le {end_of_day}"
    )

    filter_params = f"{filter_origin} and {filter_active} and {filter_last_logon}"

    if params_string:
        return f"{base_url}{path}?filter={filter_params}&{params_string}"
    else:
        return f"{base_url}{path}?filter={filter_params}"


def create_uaa_user(
    idx: int = 1,
    user_guid: str = "abcd-efg",
    origin: str = "cloud.gov",
    active: str = "true",
    email: str = "",
    last_logon_time: int = 0,
) -> dict:
    if not email:
        email = f"user-{idx}@example.com"

    if not last_logon_time:
        # Set in epoch milliseconds
        last_logon_time = int(time.time()) * 1000

    return {
        "id": user_guid,
        "externalId": email,
        "userName": email,
        "active": active,
        "verified": "true",
        "origin": origin,
        "zoneId": "uaa",
        "passwordLastModified": "2021-01-03T20:40:36.000Z",
        "lastLogonTime": last_logon_time,
    }


def create_uaa_users_last_logged_in(
    total_results: int = 10,
    days_ago: int = 90,
    start_of_day: int = None,
    end_of_day: int = None,
) -> list:
    users = []
    current_time = time.time()

    if start_of_day is None:
        start_of_day = get_epoch_days_ago(days_ago, current_time)

    if end_of_day is None:
        end_of_day = get_epoch_days_ago(days_ago - 1, current_time)

    for x in range(total_results):
        user = {}
        last_logon_time = randint(start_of_day, end_of_day)
        user = create_uaa_user(idx=x, last_logon_time=last_logon_time)
        users.append(user)

    return users


def create_uaa_response(
    resources: list = [],
    start_index: int = 1,
    total_results: int = 10,
    items_per_page: int = 0,
) -> dict:
    if total_results < len(resources):
        total_results = len(resources)

    if items_per_page < len(resources):
        items_per_page = len(resources)

    return {
        "resources": resources,
        "startIndex": start_index,
        "itemsPerPage": items_per_page,
        "totalResults": total_results,
    }


@pytest.fixture
def uaa_authenticated(requests_mock):
    requests_mock.post(
        build_url("/oauth/token?grant_type=client_credentials&response_type=token"),
        json=authenticated_response,
    )


@pytest.fixture
def uaa_unauthorized(requests_mock):
    requests_mock.post(
        build_url("/oauth/token?grant_type=client_credentials&response_type=token"),
        json={"error_description": "Unauthorized"},
        status_code=401,
    )


@pytest.fixture
def uaa_deactivate_user(requests_mock, uaa_authenticated, deactivate_user_guid):
    user = create_uaa_user(user_guid=deactivate_user_guid, active="false")
    response = create_uaa_response(resources=[user], total_results=1)
    request_url = build_url(f"/Users/{deactivate_user_guid}")
    requests_mock.put(request_url, json=response)
    return user


@pytest.fixture
def uaa_deactivate_multiple_users(requests_mock, uaa_authenticated, last_logon_config):
    days_ago = last_logon_config["days_ago"]
    resources = create_uaa_users_last_logged_in(**last_logon_config)
    response = create_uaa_response(resources=resources)
    users_request_url = f"{base_url}/Users"
    requests_mock.get(users_request_url, json=response)

    for user in response.get("resources"):
        user_guid = user.get("id")
        deactivate_request_url = build_url(f"/Users/{user_guid}")
        requests_mock.put(deactivate_request_url, json=user)


@pytest.fixture
def uaa_deactivate_multiple_pages_of_users(
    requests_mock, uaa_authenticated, uaa_list_users_multiple_pages
):
    users = uaa_list_users_multiple_pages

    for user in users:
        user_guid = user.get("id")
        deactivate_request_url = build_url(f"/Users/{user_guid}")
        requests_mock.put(deactivate_request_url, json=user)


@pytest.fixture
def uaa_list_users_multiple_pages(
    requests_mock,
    uaa_authenticated,
    last_logon_config,
):
    total_users_resources = []
    start_of_day = last_logon_config.get("start_of_day", 10000)
    end_of_day = last_logon_config.get("end_of_day", 11000)
    results_per_page = last_logon_config.get("results_per_page", 100)
    total_results = last_logon_config.get("total_results", 150)
    pages = ceil(total_results / results_per_page)

    for idx in range(pages):
        start_index = (idx * results_per_page) + 1
        resources = create_uaa_users_last_logged_in(
            total_results=results_per_page,
            start_of_day=start_of_day,
            end_of_day=end_of_day,
        )
        total_users_resources.extend(resources)
        response = create_uaa_response(
            resources=resources, start_index=start_index, total_results=total_results
        )
        users_request_url = build_url(
            "/Users",
            start_of_day=start_of_day,
            end_of_day=end_of_day,
            startIndex=start_index,
        )
        requests_mock.get(users_request_url, json=response)

    return total_users_resources


@pytest.fixture
def uaa_list_expiring_users(requests_mock, uaa_authenticated, last_logon_config):
    start_of_day = last_logon_config.get("start_of_day", None)
    end_of_day = last_logon_config.get("end_of_day", None)
    resources = create_uaa_users_last_logged_in(**last_logon_config)
    response = create_uaa_response(resources=resources)

    if start_of_day and end_of_day:
        request_url = build_url(
            "/Users", start_of_day=start_of_day, end_of_day=end_of_day
        )
    else:
        request_url = build_url("/Users")

    requests_mock.get(request_url, json=response)


@pytest.fixture
def uaa_list_users_last_logon(requests_mock, uaa_authenticated, last_logon_config):
    total_users_resources = []
    start_of_day = last_logon_config.get("start_of_day", 10000)
    end_of_day = last_logon_config.get("end_of_day", 11000)
    results_per_page = last_logon_config.get("results_per_page", 100)
    total_results = last_logon_config.get("total_results", 150)
    pages = ceil(total_results / results_per_page)

    for idx in range(pages):
        start_index = (idx * results_per_page) + 1
        resources = create_uaa_users_last_logged_in(
            total_results=results_per_page,
            start_of_day=start_of_day,
            end_of_day=end_of_day,
        )
        total_users_resources.extend(resources)
        response = create_uaa_response(
            resources=resources, start_index=start_index, total_results=total_results
        )
        users_request_url = build_url_no_filter(
            "/Users",
            start_of_day=start_of_day,
            end_of_day=end_of_day,
            startIndex=start_index,
        )
        requests_mock.get(users_request_url, json=response)

    return total_users_resources
