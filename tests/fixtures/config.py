UAA_CONFIG = {
    "UAA_BASE_URL": "https://uaa.example.com",
    "UAA_CLIENT_ID": "a_user",
    "UAA_CLIENT_SECRET": "a_password",
}

authenticated_response = {"access_token": "authenticated-token"}
base_url = UAA_CONFIG["UAA_BASE_URL"]
sample_user_guid = "abcd-1234-efghi-jklmno-8765"

SMTP_CONFIG = {
    "SMTP_FROM": "bar@example.com",
    "SMTP_HOST": "remote-host",
    "SMTP_PORT": 9160,
    "SMTP_USER": "user",
    "SMTP_PASS": "pass",
    "SMTP_CERT": None,
}


user_email = "test@example.com"
username = "Test User"
