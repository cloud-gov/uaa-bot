UAA_CONFIG = {
    "UAA_BASE_URL": "https://uaa.example.com",
    "UAA_CLIENT_ID": "a_user",
    "UAA_CLIENT_SECRET": "a_password",
    "UAA_VERIFY_TLS": True,
}

base_url = UAA_CONFIG["UAA_BASE_URL"]
authenticated_response = {"access_token": "authenticated-token"}
