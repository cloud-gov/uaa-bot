import pytest
from email_validator import EmailNotValidError
from mock import patch
from uaa_bot import config, notifier

email = "test@example.com"
username = "Test User"
test_smtp_config = {
    "SMTP_FROM": "bar@example.com",
    "SMTP_HOST": "remote-host",
    "SMTP_PORT": 9160,
    "SMTP_USER": "user",
    "SMTP_PASS": "pass",
    "SMTP_CERT": None,
}


def test_render_account_expired_template():
    template = "account_expired"
    notification = notifier.Notifier(email)
    rendered = notification.render_template(template, username=username)

    assert type(rendered) == str
    assert f"Hello {username}" in rendered
    assert "Your account has been" in rendered
    assert "deactivated" in rendered


def test_render_account_expiration_10_days_template():
    template = "account_expires_in_10_days"
    notification = notifier.Notifier(email)
    rendered = notification.render_template(template, username=username)

    assert type(rendered) == str
    assert f"Hello {username}" in rendered
    assert "Your account will be" in rendered
    assert "deactivated" in rendered
    assert "10 days" in rendered


def test_render_account_expiration_1_day_template():
    template = "account_expires_in_1_day"
    notification = notifier.Notifier(email)
    rendered = notification.render_template(template, username=username)

    assert type(rendered) == str
    assert f"Hello {username}" in rendered
    assert "Your account will be" in rendered
    assert "deactivated" in rendered
    assert "1 day" in rendered


def test_uses_default_smtp_config_if_not_provided():
    notification = notifier.Notifier(email)

    assert type(notification.smtp_config) == dict
    for key, value in notification.smtp_config.items():
        assert value == config.smtp[key]


def test_uses_smtp_config_if_provided():
    notification = notifier.Notifier(email, smtp_config=test_smtp_config)

    assert type(notification.smtp_config) == dict
    for key, value in notification.smtp_config.items():
        assert value == test_smtp_config[key]


def test_raise_error_with_invalid_email():
    with pytest.raises(EmailNotValidError):
        invalid_email = "invalid email address"
        notification = notifier.Notifier(invalid_email)


def test_raise_error_with_invalid_template():
    with pytest.raises(Exception):
        invalid_template = "invalid template name"
        notification = notifier.Notifier(email)
        rendered = notification.render_template(invalid_template, username=username)


def test_get_email_subject_from_template_name():
    template = "account_expires_in_1_day"
    expected = "Your cloud.gov account expires in 1 day"
    notification = notifier.Notifier(email)
    subject = notification.get_email_subject(template)

    assert subject == expected


@pytest.fixture(scope="module")
def smtp_connection():
    from uaa_bot.notifier import smtplib


@patch("uaa_bot.notifier.smtplib")
def test_send_email_auth(smtp_connection):
    """IF SMTP_USER and SMTP_PASS are provided, smtp.login() is called"""
    template = "account_expired"
    notification = notifier.Notifier(email, smtp_config=test_smtp_config)
    response = notification.send_email(template, username=username)

    assert response == True
    smtp_connection.SMTP.assert_called_with(
        test_smtp_config["SMTP_HOST"], test_smtp_config["SMTP_PORT"]
    )
    smtp_connection.SMTP().login.assert_called_with(
        "user", test_smtp_config["SMTP_PASS"]
    )
