import pytest
from mock import patch

from uaa_bot.bot import UAABot
from fixtures.config import (
    sample_user_guid,
    sample_user_guid,
    SMTP_CONFIG,
    UAA_CONFIG,
    user_email,
    username,
)


@pytest.mark.parametrize(
    "last_logon_config",
    [{"total_results": 100, "days_ago": 90}],
)
@patch("uaa_bot.notifier.smtplib")
def test_account_deactivation_and_notice(
    smtp_connection, uaa_deactivate_multiple_users
):
    bot = UAABot(smtp_config=SMTP_CONFIG, uaa_config=UAA_CONFIG)
    summary = bot.notify_and_deactivate()

    assert type(summary) == dict
    assert summary.get("title") == "Deactivation of accounts"
    assert summary.get("total_accounts") == 100
    assert len(summary.get("user_summary")) == 100


@pytest.mark.parametrize(
    "last_logon_config",
    [{"total_results": 100, "days_ago": 90}],
)
@patch("uaa_bot.notifier.smtplib")
def test_notification_1_day_out(smtp_connection, uaa_deactivate_multiple_users):
    bot = UAABot(smtp_config=SMTP_CONFIG, uaa_config=UAA_CONFIG)
    summary = bot.notify_deactivation_in_1_day()

    assert type(summary) == dict
    assert smtp_connection.SMTP._mock_call_count == 100
    assert summary.get("title") == "Account of deactivations in 1 day"
    assert summary.get("total_accounts") == 100
    assert len(summary.get("user_summary")) == 100


@pytest.mark.parametrize(
    "last_logon_config",
    [{"total_results": 100, "days_ago": 90}],
)
@patch("uaa_bot.notifier.smtplib")
def test_notification_10_days_out(smtp_connection, uaa_deactivate_multiple_users):
    bot = UAABot(smtp_config=SMTP_CONFIG, uaa_config=UAA_CONFIG)
    summary = bot.notify_deactivation_in_10_days()

    assert type(summary) == dict
    assert smtp_connection.SMTP._mock_call_count == 100
    assert summary.get("title") == "Account of deactivations in 10 days"
    assert summary.get("total_accounts") == 100
    assert len(summary.get("user_summary")) == 100
