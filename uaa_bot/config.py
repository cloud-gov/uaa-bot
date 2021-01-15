import os


def parse_config_env(default_dict):
    config_dict = {}

    for key, value in default_dict.items():
        config_dict[key] = os.environ.get(key, value)

    return config_dict


SMTP_KEYS = {
    "SMTP_HOST": "localhost",
    "SMTP_PORT": 25,
    "SMTP_FROM": "no-reply@example.com",
    "SMTP_USER": None,
    "SMTP_PASS": None,
    "SMTP_CERT": None,
}

UAA_KEYS = {
    "UAA_BASE_URL": "https://uaa.bosh-lite.com",
    "UAA_CLIENT_ID": None,
    "UAA_CLIENT_SECRET": None,
    "UAA_VERIFY_TLS": True,
}

smtp = parse_config_env(SMTP_KEYS)
uaa = parse_config_env(UAA_KEYS)
