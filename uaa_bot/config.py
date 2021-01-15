import os

SMTP_KEYS = {
    "SMTP_HOST": "localhost",
    "SMTP_PORT": 25,
    "SMTP_FROM": "no-reply@example.com",
    "SMTP_USER": None,
    "SMTP_PASS": None,
    "SMTP_CERT": None,
}

smtp = {}

for ck, default in SMTP_KEYS.items():
    smtp[ck] = os.environ.get(ck, default)
