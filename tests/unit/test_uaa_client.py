import pytest
from uaa_bot import client

UAA_CONFIG = {
    "UAA_BASE_URL": "https://uaa.example.com",
    "UAA_CLIENT_ID": "a_user",
    "UAA_CLIENT_SECRET": "a_password",
    "UAA_VERIFY_TLS": True,
}

authenticated_response = {"access_token": "authenticated-token"}


def test_authenticates_client_successfully_and_issues_token(requests_mock):
    base_url = UAA_CONFIG["UAA_BASE_URL"]
    requests_mock.post(
        f"{base_url}/oauth/token?grant_type=client_credentials&response_type=token",
        json=authenticated_response,
    )
    uaac = client.UAAClient(base_url, uaa_config=UAA_CONFIG)
    uaac.authenticate()

    assert uaac.token == authenticated_response.get("access_token")


def test_authenticates_client_unsuccessfully(requests_mock):
    with pytest.raises(client.UAAError):
        base_url = UAA_CONFIG["UAA_BASE_URL"]
        requests_mock.post(
            f"{base_url}/oauth/token?grant_type=client_credentials&response_type=token",
            json={"error_description": "Unauthorized"},
            status_code=401,
        )
        uaac = client.UAAClient(base_url, uaa_config=UAA_CONFIG)
        uaac.authenticate()
