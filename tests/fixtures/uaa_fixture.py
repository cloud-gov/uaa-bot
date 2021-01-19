import pytest
import time
from random import randint

from fixtures.config import authenticated_response, base_url


def get_epoch_days_ago(days_ago: int, current_time: float) -> int:
    return int(current_time) - (days_ago * 60 * 60 * 24 * 1000)


def create_uaa_user(
    idx=1, origin="cloud.gov", active="true", email="", last_logon_time=int
) -> dict:
    if not email:
        email = f"user-{idx}@example.com"

    if not last_logon_time:
        # Set in epoch milliseconds
        last_logon_time = int(time.time()) * 1000

    return {
        "id": "abcd-efg",
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
    total_results=10,
    days_ago=90,
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
def uaa_list_expiring_users(requests_mock, last_logon_config):
    days_ago = last_logon_config["days_ago"]
    current_time = time.time()
    last_logon_start = get_epoch_days_ago(days_ago, current_time)
    last_logon_end = get_epoch_days_ago(days_ago - 1, current_time)
    resources = create_uaa_users_last_logged_in(**last_logon_config)
    response = create_uaa_response(resources=resources)
    request_url = f"{base_url}/Users"
    requests_mock.get(request_url, json=response)
