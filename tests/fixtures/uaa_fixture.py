import pytest
import time
from random import randint

from fixtures.config import authenticated_response, base_url


def get_epoch_days_ago(days_ago: int, current_time: float) -> int:
    return int(current_time) - (days_ago * 60 * 60 * 24 * 1000)


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
) -> list:
    users = []
    current_time = time.time()
    last_logon_start = get_epoch_days_ago(days_ago, current_time)
    last_logon_end = get_epoch_days_ago(days_ago - 1, current_time)

    for x in range(total_results):
        user = {}
        last_logon_time = randint(last_logon_start, last_logon_end)
        user = create_uaa_user(idx=x, last_logon_time=last_logon_time)
        users.append(user)

    return users


def create_uaa_response(resources=[], start_index=1, total_results=10) -> dict:
    if total_results < len(resources):
        total_results = len(resources)

    return {
        "resources": resources,
        "startIndex": start_index,
        "itemsPerPage": len(resources),
        "totalResults": total_results,
    }


@pytest.fixture
def uaa_authenticated(requests_mock):
    requests_mock.post(
        f"{base_url}/oauth/token?grant_type=client_credentials&response_type=token",
        json=authenticated_response,
    )


@pytest.fixture
def uaa_unauthorized(requests_mock):
    requests_mock.post(
        f"{base_url}/oauth/token?grant_type=client_credentials&response_type=token",
        json={"error_description": "Unauthorized"},
        status_code=401,
    )


@pytest.fixture
def uaa_deactivate_user(requests_mock, uaa_authenticated, deactivate_user_guid):
    user = create_uaa_user(user_guid=deactivate_user_guid, active="false")
    response = create_uaa_response(resources=[user], total_results=1)
    request_url = f"{base_url}/Users/{deactivate_user_guid}"
    requests_mock.put(request_url, json=response)


@pytest.fixture
def uaa_deactivate_multiple_users(requests_mock, uaa_authenticated, last_logon_config):
    days_ago = last_logon_config["days_ago"]
    resources = create_uaa_users_last_logged_in(**last_logon_config)
    response = create_uaa_response(resources=resources)
    users_request_url = f"{base_url}/Users"
    requests_mock.get(users_request_url, json=response)

    for user in response.get("resources"):
        user_guid = user.get("id")
        deactivate_request_url = f"{base_url}/Users/{user_guid}"
        requests_mock.put(deactivate_request_url, json=user)


@pytest.fixture
def uaa_list_expiring_users(requests_mock, uaa_authenticated, last_logon_config):
    days_ago = last_logon_config["days_ago"]
    resources = create_uaa_users_last_logged_in(**last_logon_config)
    response = create_uaa_response(resources=resources)
    request_url = f"{base_url}/Users"
    requests_mock.get(request_url, json=response)
