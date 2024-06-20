import pytest
from uaa_bot import client

from fixtures.config import (
    authenticated_response,
    base_url,
    sample_user_guid,
    UAA_CONFIG,
)


def test_authenticates_client_successfully_and_issues_token(uaa_authenticated):
    uaac = client.UAAClient(base_url, uaa_config=UAA_CONFIG)
    uaac.authenticate()

    assert uaac.token == authenticated_response.get("access_token")


def test_authenticates_client_unsuccessfully(uaa_unauthorized):
    with pytest.raises(client.UAAError):
        uaac = client.UAAClient(base_url, uaa_config=UAA_CONFIG)
        uaac.authenticate()


@pytest.mark.parametrize(
    "last_logon_config",
    [{"total_results": 100, "days_ago": 90}],
)
def test_client_list_expiring_users(uaa_list_expiring_users):
    uaac = client.UAAClient(base_url, uaa_config=UAA_CONFIG)
    uaac.authenticate()
    response = uaac.list_expiring_users(days_ago=90)

    assert uaac.token == authenticated_response.get("access_token")
    assert response["totalResults"] == 100
    assert len(response["resources"]) == 100


@pytest.mark.parametrize(
    "last_logon_config",
    [{"total_results": 100, "start_of_day": 10000, "end_of_day": 11000}],
)
def test_client_list_expiring_users_with_start_end_epoch(uaa_list_expiring_users):
    uaac = client.UAAClient(base_url, uaa_config=UAA_CONFIG)
    uaac.authenticate()
    response = uaac.list_expiring_users(start_of_day=10000, end_of_day=11000)

    assert uaac.token == authenticated_response.get("access_token")
    assert response["totalResults"] == 100
    assert len(response["resources"]) == 100


@pytest.mark.parametrize(
    "last_logon_config",
    [
        {
            "total_results": 200,
            "results_per_page": 100,
            "start_of_day": 10000,
            "end_of_day": 11000,
        }
    ],
)
def test_client_list_expiring_users_with_multiple_pages(uaa_list_users_multiple_pages):
    uaac = client.UAAClient(base_url, uaa_config=UAA_CONFIG)
    uaac.authenticate()
    response = uaac.list_expiring_users(start_of_day=10000, end_of_day=11000)

    assert uaac.token == authenticated_response.get("access_token")
    assert response["totalResults"] == 200
    assert len(response["resources"]) == 200


@pytest.mark.parametrize(
    "deactivate_user_guid",
    [sample_user_guid],
)
def test_client_deactivate_user(uaa_deactivate_user):
    deactivated_user = uaa_deactivate_user
    uaac = client.UAAClient(base_url, uaa_config=UAA_CONFIG)
    uaac.authenticate()
    response = uaac.deactivate_user(deactivated_user)
    user = response["resources"][0]

    assert uaac.token == authenticated_response.get("access_token")
    assert user["id"] == sample_user_guid
    assert response["totalResults"] == 1
    assert len(response["resources"]) == 1


@pytest.mark.parametrize(
    "last_logon_config",
    [
        {
            "total_results": 200,
            "results_per_page": 100,
            "start_of_day": 10000,
            "end_of_day": 11000,
        }
    ],
)
def test_client_list_users_last_logon(uaa_list_users_last_logon):
    uaac = client.UAAClient(base_url, uaa_config=UAA_CONFIG)
    uaac.authenticate()
    response = uaac.list_users_last_logon(start_of_day=10000, end_of_day=11000)

    assert uaac.token == authenticated_response.get("access_token")
    assert response["totalResults"] == 200
    assert len(response["resources"]) == 200
