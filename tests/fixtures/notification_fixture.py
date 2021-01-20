import pytest

@pytest.fixture(scope="module")
def smtp_connection():
    from uaa_bot.notifier import smtplib
