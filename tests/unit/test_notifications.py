import pytest
from email_validator import EmailNotValidError
from mock import patch
from uaa_bot import config, notifier
from fixtures.config import SMTP_CONFIG, user_email, username


def test_render_account_expired_template():
    template = "account_expired"
    notification = notifier.Notifier(user_email)
    rendered = notification.render_template(template, username=username)

    assert type(rendered) == str
    assert f"Hello," in rendered
    assert "Your account has been" in rendered
    assert "deactivated" in rendered


def test_render_account_expiration_10_days_template():
    template = "account_expires_in_10_days"
    notification = notifier.Notifier(user_email)
    rendered = notification.render_template(template, username=username)

    assert type(rendered) == str
    assert f"Hello," in rendered
    assert "Your account will be" in rendered
    assert "deactivated" in rendered
    assert "10 days" in rendered


def test_render_account_expiration_1_day_template():
    template = "account_expires_in_1_day"
    notification = notifier.Notifier(user_email)
    rendered = notification.render_template(template, username=username)

    assert type(rendered) == str
    assert f"Hello," in rendered
    assert "Your account will be" in rendered
    assert "deactivated" in rendered
    assert "1 day" in rendered


def test_uses_default_smtp_config_if_not_provided():
    notification = notifier.Notifier(user_email)

    assert type(notification.smtp_config) == dict
    for key, value in notification.smtp_config.items():
        assert value == config.smtp[key]


def test_uses_smtp_config_if_provided():
    notification = notifier.Notifier(user_email, smtp_config=SMTP_CONFIG)

    assert type(notification.smtp_config) == dict
    for key, value in notification.smtp_config.items():
        assert value == SMTP_CONFIG[key]


def test_raise_error_with_invalid_email():
    with pytest.raises(EmailNotValidError):
        invalid_email = "invalid email address"
        notification = notifier.Notifier(invalid_email)


def test_raise_error_with_invalid_template():
    with pytest.raises(Exception):
        invalid_template = "invalid template name"
        notification = notifier.Notifier(user_email)
        rendered = notification.render_template(invalid_template, username=username)


def test_get_email_subject_from_template_name():
    template = "account_expires_in_1_day"
    expected = "Your cloud.gov account expires in 1 day"
    notification = notifier.Notifier(user_email)
    subject = notification.get_email_subject(template)

    assert subject == expected


@patch("uaa_bot.notifier.smtplib")
def test_send_email_auth(smtp_connection):
    """IF SMTP_USER and SMTP_PASS are provided, smtp.login() is called"""
    template = "account_expired"
    notification = notifier.Notifier(user_email, smtp_config=SMTP_CONFIG)
    response = notification.send_email(template, username=username)

    assert response == True
    smtp_connection.SMTP.assert_called_with(
        SMTP_CONFIG["SMTP_HOST"], SMTP_CONFIG["SMTP_PORT"]
    )
    smtp_connection.SMTP().login.assert_called_with("user", SMTP_CONFIG["SMTP_PASS"])
